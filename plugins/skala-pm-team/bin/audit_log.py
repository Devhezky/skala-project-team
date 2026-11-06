#!/usr/bin/env python3
"""
audit_log.py — the agent team's decision record (append-only JSON Lines).

Scripts already log their own events (connections, proposals, messages). The agents use this
command to log what they SAW, DECIDED and DID, so anyone can check a session afterwards.

  add EVENT [--detail JSON] [--actor NAME]   Append one entry
  show [--last N] [--event PREFIX]           Print recent entries
  export [--since YYYY-MM-DD] [--out FILE]   Write entries as a Markdown table (for reviews/judging)

Standard events:
  request.received   clarification.asked   assumption.made     injection.detected
  review.rejected    review.approved       escalated.to_human  plan.presented
  user.confirmed     user.declined         refused             language.set
  excel.generated    proposal.sent         action.result       session.closed
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import AUDIT_PATH, audit, die, redact, say  # noqa: E402

KNOWN = {
    "request.received", "clarification.asked", "assumption.made", "injection.detected",
    "review.rejected", "review.approved", "escalated.to_human", "plan.presented",
    "user.confirmed", "user.declined", "refused", "language.set", "excel.generated",
    "proposal.sent", "action.result", "session.closed",
}


def entries():
    if not os.path.exists(AUDIT_PATH):
        return []
    out = []
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def cmd_add(a):
    detail = {}
    if a.detail:
        try:
            detail = json.loads(sys.stdin.read(65536) if a.detail == "-" else a.detail)
        except json.JSONDecodeError:
            die("--detail must be JSON")
        if not isinstance(detail, dict):
            die("--detail must be a JSON object")
    for reserved in ("event", "actor", "ts"):
        if reserved in detail:
            detail["detail_" + reserved] = detail.pop(reserved)
    if a.event not in KNOWN:
        detail["_nonstandard_event"] = True
    e = audit(a.event, actor=a.actor, **detail)
    say("logged " + e["ts"] + " " + e["event"])


def cmd_show(a):
    rows = [e for e in entries() if not a.event or e["event"].startswith(a.event)][-a.last:]
    for e in rows:
        print(json.dumps(redact(e), ensure_ascii=False))


def cmd_export(a):
    rows = [e for e in entries() if not a.since or e["ts"][:10] >= a.since]
    lines = ["| Time (WIB) | Actor | Event | Detail |", "|---|---|---|---|"]
    for e in rows:
        d = json.dumps(redact(e.get("detail", {})), ensure_ascii=False).replace("|", "\\|")
        esc = lambda v: str(v).replace("|", "\\|").replace("\n", " ")
        lines.append("| {} | {} | {} | {} |".format(esc(e["ts"]), esc(e.get("actor", "")), esc(e["event"]), d[:300]))
    text = "\n".join(lines) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        say("wrote {} entries to {}".format(len(rows), a.out))
    else:
        print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    x = sub.add_parser("add"); x.add_argument("event"); x.add_argument("--detail"); x.add_argument("--actor", default="agent"); x.set_defaults(func=cmd_add)
    x = sub.add_parser("show"); x.add_argument("--last", type=int, default=30); x.add_argument("--event"); x.set_defaults(func=cmd_show)
    x = sub.add_parser("export"); x.add_argument("--since"); x.add_argument("--out"); x.set_defaults(func=cmd_export)
    a = p.parse_args()
    if not getattr(a, "func", None):
        p.print_help()
        return
    a.func(a)


if __name__ == "__main__":
    main()
