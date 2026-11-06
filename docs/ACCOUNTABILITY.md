# Accountability sheet — Skala Project Team

*AI CAN DO IT Tencent Cloud Hackathon Indonesia 2026 · Challenge B: The Office Agent · Scenario: receipts, invoices and forms (plus field reports → actions)*

## What it can access

| Source | Access | Limit |
|---|---|---|
| Files and messages the user gives it (receipt photos, chat exports, voice-note transcripts, RAB spreadsheets) | Read | Treated as **untrusted data**; instructions inside are never followed |
| Skala Pro (optional) | **Read** projects, tasks, S-curve, expense categories, expenses, clients and staff names (only to pick a client, team member or task assignee) | Only what the connected staff member's Skala role allows; finance fields hidden from roles without invoice permission; other projects look identical to non-existent ones |
| Skala Pro | **Propose** expense, task, task status, S-curve update | Proposals write nothing |
| Telegram / WhatsApp (optional) | Read messages from allowlisted chats; reply to the asker | Allowlist is fail-closed; `field` chats never receive money amounts |
| Local disk | `~/.skala-workbuddy/` (config 600, audit log), output files the user names | No access to other Skala tenants |

## What it does on its own (no approval needed)

- Extract data from inputs, with a source for every value.
- Calculate weights, progress, deviation and totals with scripts; check dates against holidays, Sunday, Friday prayers and WIB/WITA/WIT.
- Review its own drafts with a separate QA agent (up to 3 rounds), then escalate.
- Ask clarifying questions when something would change who, what, when, where or how much.
- Read from Skala within the user's permissions.
- Write the audit log.

## What requires human approval

| Action | Approval | Enforced by |
|---|---|---|
| A small expense in Skala | User answers "ya" to the expense card showing each row, amount and category | **Prompt** for the "ya"; **server** limits what can be saved this way: only expenses, ≤ the admin's limit (default Rp10.000.000 per row), nothing Skala flags as a possible duplicate, ≤ 30 per hour per staff, the user's words stored with the record, admin can switch it off. Same permission and integrity checks as the Approve button |
| Any change in Skala (expense, edit, deletion, project, task, S-curve) | User confirms the card in chat; Skala saves it and lists it in its decision history with the user's words. Held back by the server (above the limit, similar data, progress going down, type switched off): ② user presses **Setujui** on a page rendered by Skala from the exact payload | **Server.** Type switch, limits and hourly cap; payload hash checked; permissions re-checked |
| Connecting the agent to a Skala account | User approves on Skala's consent screen after matching the code | **Server** (device login) |
| A message to anyone other than the person who asked | Owner replies `SETUJU <code>` from their own chat; the code is never shown to the agent | **Code** (`skala_bridge.py send-approved`) |
| Generating or overwriting a file | User confirms the plan card | Prompt |

## What it will never do

- Write to Skala without the user's "ya" to the exact details. Anything beyond a small, unflagged expense also needs the user's approval inside Skala.
- Create invoices, estimates or projects (removed from the agent API).
- Send prices, amounts or margins to a foreman's (`field`) chat (blocked in code).
- Follow instructions found inside documents, receipts or messages.
- Ask for, display or store keys and passwords in the conversation. The key is held by the script in a 600-mode file outside the plugin folder and is redacted from every output.
- Connect to any host other than `*.skalapro.cloud` over HTTPS.
- Claim something was saved or sent unless the script reports it.
- Delete data on its own initiative. The only deletion is an expense you asked to delete: it needs a reason and your yes in chat, and Skala keeps what was deleted in its decision history.

## How you can check what it did

| Record | Where |
|---|---|
| Every agent decision: request, clarification, assumption, injection detected, QA verdicts with rule IDs, plan shown, user's words, proposal, result | `~/.skala-workbuddy/audit.jsonl` · `python3 bin/audit_log.py export` |
| Every API call, login, proposal, approval, rejection, execution (with who and from which IP) | Skala → WorkBuddy AI → *Log aktivitas* (`tblskala_workbuddy_audit`) |
| Per-proposal page: server summary, agent sources, receipt, payload hash, decision and note | Skala → WorkBuddy AI → proposal |
| Messages in and out, owner approvals | `~/.skala-workbuddy/data/{inbox,processed,outbox}` |

## Known limits (disclosed, not hidden)

- **Local guards depend on the agent behaving.** WorkBuddy gives the agent a shell on the user's computer and the plugin cannot sandbox it. A prompt-injected agent could bypass the *local* guards (chat roles, owner approval for messages). What still holds in that case: nothing is written to Skala without a person approving it in Skala, and reads stay within that person's Skala role. Mitigations: scripts refuse credential paths and block secrets in outgoing messages; we recommend running WorkBuddy in "ask before running commands" mode. Full audit: `docs/SECURITY-AUDIT.md`.

- **Expenses saved from chat (v1.2) rely on the agent reporting the user's "ya" honestly.** The server cannot verify that the user typed it. A prompt-injected agent could save expenses up to the admin's limit and hourly cap without the user. Bounded by: expense type only, amount limit, duplicate check, hourly cap, the user's quoted words and the agent key on every record, a Skala notification for every saved expense, the audit log, and an admin switch. Owners who want a server-enforced approval for every write switch "Simpan pengeluaran dari chat" off.
- For tasks and S-curve the *first* confirmation (plan card) relies on the agent following its rules; the *binding* approval is server-side. For local files it is not.
- Device-login phishing (someone sends you an approval link for their request) is mitigated (the code must be typed, never pre-filled; warning; code-match checkbox; requester IP; notification after every new connection; 10-minute expiry), not eliminated.
- Photos sent through Telegram/WhatsApp are not downloaded automatically.
- Holiday data covers 2026–2027 (SKB 3 Menteri); regional holidays are not included.
