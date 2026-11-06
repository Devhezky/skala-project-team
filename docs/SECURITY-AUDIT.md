# Security audit — Skala Project Team v2 + skala_workbuddy v1.1

**Date:** 2026-11-03 · **Scope:** WorkBuddy Expert Team plugin (`plugins/skala-pm-team`), Skala server module `skala_workbuddy`, the owner's workstation folders that hold the plugin and credentials.
**Method:** two independent reviewers (server; agent/LLM) who did not write the code, plus automated checks (bandit, secret-pattern scan, 18 agent tests, 13 server unit tests, 10 bridge self-checks) and proof-of-concept scripts for every suspected issue.

**Standards used.** There is no FBI application-security standard; this audit follows the frameworks auditors and agencies use:
OWASP ASVS 4.0.3 Level 2 · OWASP API Security Top 10 (2023) · OWASP Top 10 for LLM Applications (2025) · MITRE ATLAS · NIST CSF 2.0 (Identify/Protect/Detect/Respond) · CISA Secure by Design.

## Summary

| Severity | Found | Fixed in code | Open (owner action) | Accepted with mitigation |
|---|---|---|---|---|
| Critical | 1 | 0 | **1** (OPS-1) | 0 |
| High | 7 | 5 | **1** (OPS-2) | 1 (A-H3) |
| Medium | 12 | 11 | 1 (OPS-3) | 0 |
| Low / Info | 26 | 20 | 4 | 2 |

**No fatal flaw in the server design:** no remote code execution, authentication bypass, cross-tenant read, SQL injection or approval bypass was found. The weakest point is the **agent's workstation**: a successfully prompt-injected agent with unrestricted shell access can bypass every *local* guard. Server-side guarantees (nothing written without a person's approval in Skala, read limited by the person's role) still hold in that case.

## Open items for the owner (do these first)

| ID | Severity | Finding | Action |
|---|---|---|---|
| **OPS-1** | **Critical** | A live v1.0 Skala key is stored in plain text in `~/.workbuddy-ai/plugins/marketplaces/my-experts/plugins/skala-pro-operator/config/config.json`, and its prefix is in `publish/skala-expert-marketplace/PUBLISH.md`. The v1 expert is still installed and can be summoned. (Since the v1.1 upgrade that key is hashed server-side and limited to read + propose, but it can still read.) | In Skala → WorkBuddy AI, **revoke** the legacy key (`legacy…`). Remove `skala-pro-operator` from `my-experts/.codebuddy-plugin/marketplace.json`, then delete its `config/config.json`. Never share or zip the v1 folder. |
| **OPS-2** | High | WorkBuddy runs with **"Allow full access"**: the agent executes shell commands without asking. Combined with A-H3, injected content could read files or call the network from your Mac. | Switch WorkBuddy to ask before running commands (at least for sessions that process outside documents or chat messages). |
| **OPS-3** | Medium | The deployed server module differs from the reviewed source (redesigned views, a separate HTTP-500 fix). Unreviewed changes are not covered by this audit. | Put the deployed module under version control, apply `skala_workbuddy-1.1.0-to-1.1.1.patch`, and rerun `STAGING_TESTS.md` §1–10. |
| OPS-4 | Low | Module `README.md`, `STAGING_TESTS.md` and `tests/` may be web-reachable under `/modules/skala_workbuddy/`. | Deny `/modules/*/tests/` and `*.md` in the web server, or deploy the zip (tests excluded). |
| OPS-5 | Low | the multi-tenant layer trusts `X-Forwarded-Host` unconditionally, so URLs in responses reflect the requester's Host header (no cross-tenant impact found). | Configure trusted proxies (`proxy_ips`) and build URLs from the stored tenant domain. |

## Design change after the audit (v1.2, 2026-11-03)

Owner decision: small expenses are saved when the user says "ya" in chat, without the Skala approval page. This **removes the server-side human gate for that action type**, so A-H3 now also covers writes, bounded as below. Tracked as **A-M6**.

## Accepted risk

| ID | Finding | Why accepted | Mitigation |
|---|---|---|---|
| **A-M6** | Chat-confirmed expenses (v1.2): the server trusts the agent's `confirmed_in_chat` + `user_said`. A prompt-injected agent could save expenses without the user. | Pilot feedback: a second approval page per receipt made the tool slower than manual entry. | Server-enforced: `expense.create` only; amount ≤ admin limit (default Rp10.000.000); any server warning (duplicate, very old date) → approval page; ≤ 30 per hour per staff; same permission and payload checks as Approve; user's words stored in `decision_note`; Skala notification per saved expense; audit `action.approved_in_chat`; admin switch in WorkBuddy AI → Pengaturan. Roadmap: undo within 60 s. |
| **A-H3** | The plugin cannot restrict the agent's Bash tool. A compromised agent can read `~/.skala-workbuddy/config.json`, forge inbox files, or call Telegram directly, bypassing the bridge's role guard and owner approval. (Proven by the reviewer.) | WorkBuddy does not offer per-plugin sandboxing; true isolation needs a separate OS user or service for the bridge. | Server enforces read-by-role and human approval for every write; secrets blocked in outgoing messages; credential paths refused by scripts; prompts forbid reading them; OPS-2. Roadmap: run the bridge as a separate macOS user/launchd service and store tokens in Keychain with an access-control list. |
| A-L | Bandit B310 on `urllib.urlopen` in the bridge. | URLs are fixed `https://api.telegram.org` / `graph.facebook.com` constants. | — |

## Findings fixed in this audit

### Agent / LLM (OWASP LLM Top 10, ATLAS, ASVS)

| ID | Sev | Finding | Fix |
|---|---|---|---|
| H1 | High | `reply`/`send` read any existing file path given as message text and sent it unredacted (PoC sent `config.json` with the Skala key and bot token). LLM02, AML.T0057 | Text is literal or stdin only, never read from a path; every outgoing message is refused if it contains a configured secret or a secret pattern. |
| H2 | High | Documented commands put receipt/chat text inside shell arguments (`--payload '<json>'`, `reply "<text>"`), so a vendor name with `'` or `$(…)` could run code. ASVS V5.3.8, LLM05 | `propose --stdin`, `reply … -`, `audit_log --detail -` with quoted heredocs; prompts and references updated. |
| M1 | Med | `--confirm-domain` was not tied to `--url` and was saved before login succeeded (any domain could be trusted silently). | Must equal the URL host; saved only after the person approves the login in Skala. |
| M2 | Med | `--payload-file` / `--receipt` accepted any path (could upload `~/.ssh/id_rsa` or the config). | Credential folders, dotfiles and system paths refused; receipt must be real JPEG/PNG/WEBP/PDF by magic bytes; payload fields allow-listed per action type. |
| M3 | Med | Money guard for field chats bypassable (`1,2 M`, `IDR 2500000`, `2 500 000`, `$300`, `sejuta`, zero-width chars). | NFKC normalisation, currency tokens and number words, long digit runs; quantities with units (mm, sak, m) still allowed. Tested: 18 bypasses blocked, 0 false positives on 8 site messages. |
| M4 | Med | `redact()` missed private keys, upper-case keys and exact config values. | PEM blocks, case-insensitive patterns, exact secret values from config masked everywhere. |
| M5 | Med | WhatsApp signature check was optional. | `ingest` refuses to run without `app_secret`; body ≤ 1 MB. |
| L1 | Low | Redirects not re-validated against the URL policy. | Redirect target must pass the same host + policy check. |
| L2 | Low | An owner *group* chat let any member approve outgoing messages. | Approvals only from an owner's private chat. |
| L3 | Low | Custom domain could resolve to a private IP (DNS tricks). | Domain must resolve, and only to public IPs. |
| L4 | Low | Unbounded reads/polling. | Response ≤ 8 MB, `action-wait` ≤ 300 s, stdin limits. |
| L5 | Low | Excel formula injection (`=HYPERLINK(...)` in project name). | User text written as string cells. |
| L6 | Low | Action ids and `approve_url` host not validated. | Id format checked; links to another host dropped. |
| L7 | Low | Audit export: reserved keys crashed `audit()`, unescaped actor in Markdown. | Reserved keys renamed; fields escaped. |
| — | Low | 6-digit outbox approval code hashed with plain SHA-256 (brute-forced offline in < 1 s). | Salted scrypt (n=2¹⁴). |

### Server (OWASP API Top 10, ASVS)

| ID | Sev | Finding | Fix (v1.1.1) |
|---|---|---|---|
| S-H1 | High | Unauthenticated 8 MB nested JSON consumed ~460 MB RAM per request (DoS). API4 | Body caps (16 KB default; 7 MB only for proposals), JSON depth 8, nesting cap, `device_token` rate limit. |
| S-M1 | Med | Agent activity logged as **visible to customers** (amounts in the client portal) and unescaped. API3 | Logged internal-only and escaped. |
| S-M2 | Med | Key-in-URL branch: unthrottled, unauthenticated audit inserts; no audit retention. API4 | Throttled first; audited only for real keys; 180-day retention and stale-row purge. |
| S-M3 | Med | Approval page could be framed (clickjacking from a sibling tenant). ASVS V14.4.7 | `X-Frame-Options: DENY`, `frame-ancestors 'none'`. |
| S-M4 | Med | Unbounded keys per staff and pending receipt storage. API4 | 5 active keys per staff (oldest revoked); 50 MB pending receipts per staff. |
| S-M5 | Med | Device-login consent showed an attacker-chosen agent name as if trusted. API6 | Labelled as untrusted; the typed code is the trust anchor; notification on every new key. |
| S-L1…L8 | Low | Task visibility edge cases; expired blob retention; IPv6 rate-limit bypass; stale-authority execution; web-reachable test file; PDF inline on admin origin; `activate_decide` not rate-limited; orphan receipt on rollback. | All fixed — see server `README.md` "v1.1.1". |
| S-I2 | Info | Integrity HMAC did not bind proposal identity. | HMAC over type, payload, receipt, proposal id, staff, key, MIME; tenant-specific key. |

## Verified controls (passed)

- **Server:** keys hashed (SHA-256), compared in constant time, scoped `read,propose`, 90-day/30-day-idle expiry, revocation; no write endpoint for agents; approval is POST + CSRF, atomic, re-validated for the approver, executed once; Skala permissions and project membership on every endpoint; invisible projects indistinguishable from non-existent; receipt type from bytes, server-generated names; all view output escaped; bound SQL; CSRF exclusion limited to `skala_workbuddy/api`; tenant tables isolated by prefix.
- **Agent:** credentials outside the plugin folder (0700/0600, atomic writes); key never printed; HTTPS only, certificate verified; tenant URL pinned to the approved host; fail-closed chat allowlist, roles, per-chat rate limit; no `eval`/`exec`/`pickle`/`shell=True`; standard library + openpyxl only; no secrets in prompts; errors stop the agent instead of probing.

## Residual risks and roadmap

1. Isolate the bridge and its tokens from the agent (separate macOS user or launchd service, Keychain ACL) — closes A-H3.
2. Official WorkBuddy Connector with OAuth 2.1 + PKCE — WorkBuddy holds tokens; nothing in the agent's reach.
3. Step-up re-authentication for admins approving a new agent connection.
4. Server-side verification that a custom domain belongs to a registered tenant (the multi-tenant layer custom-domain table).
5. Move server writes onto Skala models; monthly dependency and permission review; incident runbook (revoke-all, rotate APP_ENC_KEY, audit export).

## Runtime checks still required (cannot be proven without a running Skala)

See `STAGING_TESTS.md` §1–10 in the server package, in particular: CSRF on approve, XSS rendering in project activity and notifications, client-portal visibility of activity, web reachability of `/modules/skala_workbuddy/tests` and `*.md`, `proxy_ips`, `db_debug` off, body-size limits in nginx/PHP, session cookie SameSite on tenant and custom domains.
