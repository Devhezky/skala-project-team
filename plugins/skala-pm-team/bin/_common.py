"""
Shared helpers for the Skala WorkBuddy scripts.

Security rules enforced here (not just in prompts):
  * Credentials live OUTSIDE the plugin folder, in ~/.skala-workbuddy/ (dir 0700, files 0600),
    so they can never be committed or zipped with the plugin.
  * Everything printed or logged passes through redact(); secrets never reach the model's context.
  * Only HTTPS hosts under skalapro.cloud, or a custom domain the user confirmed (public DNS only), are contacted.
  * Every significant event is appended to an audit log (JSON Lines).
"""

import contextlib
try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

WIB = timezone(timedelta(hours=7))

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_DIR = os.path.expanduser(os.environ.get("SKALA_WB_HOME", "~/.skala-workbuddy"))
CONFIG_PATH = os.path.join(HOME_DIR, "config.json")
STATE_PATH = os.path.join(HOME_DIR, "state.json")
DATA_DIR = os.path.join(HOME_DIR, "data")
AUDIT_PATH = os.path.join(HOME_DIR, "audit.jsonl")
LEGACY_CONFIG = os.path.join(PLUGIN_DIR, "config", "config.json")

ALLOWED_HOST_SUFFIX = ".skalapro.cloud"
ALLOWED_HOST_EXACT = "skalapro.cloud"
DEFAULT_BASE_URL = "https://app.skalapro.cloud"

USER_AGENT = "SkalaWorkBuddyAgent/2.0 (+https://skalapro.cloud)"

# --------------------------------------------------------------------------
# Redaction
# --------------------------------------------------------------------------

_REDACTIONS = [
    (re.compile(r"(?s)-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?(-----END [A-Z0-9 ]*PRIVATE KEY-----|$)"), "***private-key***"),
    (re.compile(r"(?i)wbk_([a-z2-9]{8})_[a-f0-9]{48}"), r"wbk_\1_***"),         # Skala v1.1 agent key
    (re.compile(r"(?i)wb_live_[a-f0-9]{8,}"), "wb_live_***"),                  # Skala v1.0 key
    (re.compile(r"bot\d{5,}:[A-Za-z0-9_-]{20,}"), "bot***"),                    # Telegram token inside a URL
    (re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{30,}\b"), "***telegram-token***"),     # bare Telegram token
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{12,}"), r"\1***"),
    (re.compile(r"\bEA[A-Za-z0-9]{40,}\b"), "***meta-token***"),               # Meta / WhatsApp access token
    (re.compile(r"\b[a-f0-9]{64}\b"), "***64hex***"),                          # device codes, hashes
    (re.compile(r"\bWB-[2-9A-HJ-NP-Z]{4}-[2-9A-HJ-NP-Z]{4}\b"), "WB-****-****"),  # pairing codes
]


def secret_values():
    """Exact secret strings from the user's config (tokens, keys, app secrets), for masking and blocking."""
    found = []

    def walk(o, key=""):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and len(o) >= 8 and _is_secret_key(key):
            found.append(o)
    walk(read_json(CONFIG_PATH))
    return sorted(set(found), key=len, reverse=True)


def contains_secret(text):
    """True if text holds any configured secret value or any known secret pattern."""
    if not isinstance(text, str):
        return False
    squashed = re.sub(r"\s+", "", text)
    for v in secret_values():
        if v in text or v in squashed:
            return True
    return redact(text) != text


def redact(value):
    """Return value with every known secret pattern and every configured secret value masked."""
    if isinstance(value, str):
        out = value
        for v in secret_values():
            out = out.replace(v, "***")
        for pattern, repl in _REDACTIONS:
            out = pattern.sub(repl, out)
        return out
    if isinstance(value, dict):
        return {k: ("***" if _is_secret_key(k) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def _is_secret_key(key):
    k = str(key).lower()
    return any(s in k for s in ("token", "secret", "api_key", "apikey", "password", "device_code", "app_secret"))


_FORBIDDEN_DIRS = ("~/.ssh", "~/.aws", "~/.gnupg", "~/.config", "~/.kube", "~/.docker", "~/.netrc",
                   "~/Library/Keychains", "~/Library/Application Support", "~/.workbuddy", "~/.workbuddy-ai")


def safe_input_path(path, allowed_ext=None):
    """Resolve a user-supplied input path and refuse credential stores, dotfiles and system folders.
    Returns the real path or raises ValueError."""
    real = os.path.realpath(os.path.expanduser(path))
    if not os.path.isfile(real):
        raise ValueError("file not found: " + path)
    blocked = [os.path.realpath(os.path.expanduser(d)) for d in _FORBIDDEN_DIRS] + [os.path.realpath(HOME_DIR)]
    for b in blocked:
        if real == b or real.startswith(b + os.sep):
            raise ValueError("refusing to read from a private or credential folder: " + path)
    parts = real.split(os.sep)
    if any(p.startswith(".") and p not in (".", "..") for p in parts) or real.startswith(("/etc", "/private/etc", "/var", "/System")):
        raise ValueError("refusing to read hidden or system files: " + path)
    if allowed_ext and not real.lower().endswith(tuple(allowed_ext)):
        raise ValueError("unsupported file type: " + path)
    return real


def say(*parts):
    """print() that can never leak a secret."""
    print(redact(" ".join(str(p) for p in parts)))


def die(message, code=1):
    say("ERROR: " + str(message))
    sys.exit(code)


# --------------------------------------------------------------------------
# Files with safe permissions
# --------------------------------------------------------------------------

def ensure_home():
    os.makedirs(HOME_DIR, mode=0o700, exist_ok=True)
    os.makedirs(DATA_DIR, mode=0o700, exist_ok=True)
    for d in (HOME_DIR, DATA_DIR):
        try:
            os.chmod(d, 0o700)
        except OSError:
            pass


def write_private_json(path, data):
    """Write in place, file mode 0600 from the first byte. Never creates, renames or deletes another
    file, so the host does not show a "file deletion" confirmation to the user. The JSON is built in
    memory first and written with a single write under a file lock; readers retry once (read_json)."""
    ensure_home()
    payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        os.fchmod(fd, 0o600)
        if fcntl:
            fcntl.flock(fd, fcntl.LOCK_EX)
        os.ftruncate(fd, 0)
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)


def read_json(path, default=None):
    empty = {} if default is None else default
    if not os.path.exists(path):
        return empty
    for attempt in (0, 1):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            if attempt == 0:
                time.sleep(0.05)  # a writer may be between truncate and write
    return empty


@contextlib.contextmanager
def locked():
    """Exclusive lock across processes (two WorkBuddy chats share ~/.skala-workbuddy), so a
    read-modify-write of config.json / state.json cannot be overwritten by another chat."""
    ensure_home()
    fd = os.open(os.path.join(HOME_DIR, ".lock"), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        if fcntl:
            fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            if fcntl:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def load_config():
    cfg = read_json(CONFIG_PATH)
    if not cfg and os.path.exists(LEGACY_CONFIG):
        say("WARNING: found an old config inside the plugin folder (" + LEGACY_CONFIG + ").")
        say("         Credentials must not live there. Run:  python3 bin/skala_client.py migrate-config")
    if os.path.exists(CONFIG_PATH):
        mode = os.stat(CONFIG_PATH).st_mode & 0o777
        if mode & 0o077:
            os.chmod(CONFIG_PATH, 0o600)
    return cfg


def save_config(cfg):
    write_private_json(CONFIG_PATH, cfg)


def load_state():
    return read_json(STATE_PATH)


def save_state(state):
    write_private_json(STATE_PATH, state)


# --------------------------------------------------------------------------
# Audit log (append-only JSON Lines)
# --------------------------------------------------------------------------

def now_iso():
    return datetime.now(WIB).isoformat(timespec="seconds")


def audit(event, actor="script", **detail):
    ensure_home()
    entry = {"ts": now_iso(), "actor": actor, "event": event, "detail": redact(detail)}
    line = json.dumps(entry, ensure_ascii=False)
    fd = os.open(AUDIT_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return entry


# --------------------------------------------------------------------------
# Skala URL allowlist
# --------------------------------------------------------------------------

import ipaddress
import socket


def _require_public_dns(host):
    """A custom domain must resolve, and only to public IPs (blocks DNS tricks pointing at localhost/LAN)."""
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        raise ValueError("domain '" + host + "' does not resolve")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("domain '" + host + "' resolves to a private address; refused")


def trusted_custom_hosts():
    """Custom tenant domains the user explicitly confirmed (stored in ~/.skala-workbuddy/config.json)."""
    return [h.lower() for h in read_json(CONFIG_PATH).get("security", {}).get("trusted_skala_hosts", [])]


def check_skala_url(url, confirm_host=None):
    """Return a normalised base URL or raise ValueError.
    Allowed: HTTPS on *.skalapro.cloud, or on a custom domain the user confirmed
    (already trusted, or confirm_host equals the host). Never IP addresses or private hosts."""
    if not url:
        raise ValueError("Skala URL is empty")
    url = url.strip().rstrip("/")
    if "://" not in url:
        url = "https://" + url  # users type "namaperusahaan.skalapro.cloud"
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    local_test = os.environ.get("SKALA_WB_ALLOW_LOCALHOST") == "1" and host in ("127.0.0.1", "localhost")
    if parts.username or parts.password:
        raise ValueError("URL must not contain a username or password")
    if local_test:
        if parts.scheme not in ("http", "https"):
            raise ValueError("unsupported scheme")
    else:
        if parts.scheme != "https":
            raise ValueError("Skala URL must use https://")
        official = host == ALLOWED_HOST_EXACT or host.endswith(ALLOWED_HOST_SUFFIX)
        if not official:
            try:
                ipaddress.ip_address(host)
                raise ValueError("IP addresses are not accepted; use the tenant's domain name")
            except ValueError as e:
                if "IP addresses" in str(e):
                    raise
            if "." not in host or host.endswith((".local", ".localhost", ".internal", ".lan")):
                raise ValueError("'" + host + "' is not a public domain")
            if host not in trusted_custom_hosts() and (confirm_host or "").strip().lower() != host:
                raise ValueError("CUSTOM_DOMAIN_NEEDS_CONFIRMATION:" + host)
            _require_public_dns(host)
        if parts.port not in (None, 443):
            raise ValueError("Non-standard port refused")
    netloc = host + (":" + str(parts.port) if parts.port else "")
    return parts.scheme + "://" + netloc
