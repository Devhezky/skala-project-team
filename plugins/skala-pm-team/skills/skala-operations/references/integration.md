# Integration — Skala Pro, Telegram/WhatsApp, Excel

Skala is an **add-on**, not a requirement. Without Skala the team delivers the same work as an Excel workbook. With Skala the data lands in the user's real projects, after the user approves each change in Skala.

## Modes

| Mode | When | Output |
|---|---|---|
| **Excel** (default) | No Skala account, or the user declines to connect | `bin/buat_excel.py` workbook + tables in chat |
| **Skala** | User connected via device login | Read real projects; propose changes; user approves in Skala |
| **+ Telegram/WhatsApp** | Optional channel on top of either mode | Messages via `bin/skala_bridge.py` |

Check silently at session start: `python3 PLUGIN/bin/skala_client.py status`. It asks Skala whether the stored key works and returns `state`: `connected`, `login_pending`, `key_invalid`, `unverified` or `not_connected`. Use only `status` to answer "am I connected?". `login start` never creates a second login while connected or while a code is still valid (it returns `already_connected` or the same code again); `--new` forces one.

## Asking about Skala

Ask once, only if not connected and the work would benefit:
> "Kamu sudah pakai Skala Pro? Kalau sudah, saya bisa hubungkan — kamu cukup klik Setujui di Skala, tanpa menyalin kode rahasia apa pun. Kalau belum, semuanya tetap bisa saya kerjakan dan hasilnya jadi file Excel."

- "Sudah, tapi belum terhubung" → device login (below).
- "Belum" / "nanti" → Excel mode. Do not raise Skala again this session.
- Already connected → confirm the account: "Terhubung ke *{company}* sebagai *{account}*. Lanjut pakai akun ini?"

## Device login (default)

1. Ask the user for their Skala address if unknown (e.g. `https://namaperusahaan.skalapro.cloud`). Only `*.skalapro.cloud` over HTTPS is accepted.
2. `python3 PLUGIN/bin/skala_client.py login start --url <tenant>` → returns `link` and `code`.
3. Tell the user: "Buka link ini, login ke Skala, **ketik kode {code}**, cek nama agent-nya, centang konfirmasi, lalu tekan Setujui. Berlaku 10 menit." The code is not secret: it only works if the user types it and approves while logged in. The link deliberately does not carry the code, so nobody can send the user a one-click approval link.
4. Right after sending that message, in the same turn, run `python3 PLUGIN/bin/skala_client.py login wait --timeout 90` and repeat at once while it says `still_waiting` (up to 6 times; the code lives 10 minutes). Do not wait for the user to say "sudah": the key is created only when the agent collects it, so waiting for the user adds minutes before Skala shows the agent as connected.
5. Report company, account and access (read + propose). The key is stored by the script in `~/.skala-workbuddy/config.json` (mode 600); you never see it.

Fallback for a machine without a browser: the user creates a one-time pairing code in Skala → WorkBuddy AI and runs `skala_client.py pair WB-XXXX-XXXX --url <tenant>` themselves.

Disconnect: `skala_client.py logout` (revokes in Skala and deletes locally), or the user clicks *Putuskan* in Skala.

## What the Skala connection can do

| Can | Cannot |
|---|---|
| Read projects, tasks, S-curve, expense categories, expenses and (`entities`, `records`, `record`) clients, prospects, items, invoices, estimates, proposals, credit notes, payments, contracts, purchasing, BAST — only what the user's Skala role allows | Write anything directly |
| `propose` `expense.create`, `task.create`, `task.status`, `scurve.update`, `project.create`, `task.update`, `task.checklist` (add, tick, rename or remove checklist items of a task; `task.create` also takes `checklist`), `expense.update`, `expense.delete`, and `record.create|update|delete` for clients, prospects, items, invoices, estimates, proposals, credit notes, payments, contracts (see `records.md`); every action the user confirmed in chat is saved directly | Write purchasing or BAST; send anything to a client; write RAB items or payment terms (termin) |
| See the state of its proposals | Approve its own proposals |

A proposal is validated by Skala (categories must exist, dates valid, permissions checked).
- **Actions confirmed in chat** (`"confirmed_in_chat": true` + the user's words in `user_said`), of any type, are saved at once when that type is switched on and amounts are within the admin's limit. Warnings (progress going down, old date) do not hold a save back by default; only a likely duplicate does. The admin can change this in Skala (Pengaturan). The reply has `state: executed` and `result_url`. Skala keeps them in its decision history.
- **Anything held back** (above the limit, a likely duplicate, that type switched to "needs approval" by the admin, or the whole feature off) is shown on a page **rendered by Skala from the exact data**, and is saved only when the user presses **Setujui**. `not_saved_reason` says why. Proposals expire after 24 hours.

```bash
python3 PLUGIN/bin/skala_client.py projects
python3 PLUGIN/bin/skala_client.py expense-categories
python3 PLUGIN/bin/skala_client.py entities
python3 PLUGIN/bin/skala_client.py records invoice --q "Agus" --limit 10
python3 PLUGIN/bin/skala_client.py record invoice 12
python3 PLUGIN/bin/skala_client.py propose expense.create --stdin <<'JSON'
{"payload": {"project_id": 12, "amount": 1360000, "expense_name": "Semen 20 sak — Toko Bangunan Sinar Jaya",
             "category_id": 3, "date": "2026-10-18", "note": "RAB: Pekerjaan dinding"},
 "receipt": "nota-1.jpg",
 "sources": [{"kind": "receipt", "ref": "nota-1.jpg", "note": "20 × Rp68.000"}],
 "user_said": "ya, kirim", "confirmed_in_chat": true}
JSON
python3 PLUGIN/bin/skala_client.py action-wait <action_id>
```

Errors: HTTP 422 = Skala rejected the proposal; show `errors` to the team, fix, new plan card. 401 = key expired or revoked → offer to log in again. 403 = the user's role lacks that permission → say so plainly.

## Telegram / WhatsApp

Architecture: the bridge moves messages into files; the agent reads files. The agent is not a 24/7 server; messages wait in the inbox until a session reads them.

```
Telegram/WhatsApp ──▶ skala_bridge.py ──▶ ~/.skala-workbuddy/data/inbox/*.json ──▶ agent
                                 ▲                                                 │
                                 └──────────── reply / send (guarded) ◀────────────┘
```

Guards in code:
- **Allowlist, fail-closed.** `security.allowed_chats` in `~/.skala-workbuddy/config.json`; empty = nobody.
- **Roles.** `owner` or `field`. Replies with money to a `field` chat are blocked.
- **Rate limit** per chat per hour.
- **Replies** go only to the chat that asked: `skala_bridge.py reply <id> - <<'TXT'` … `TXT` (text on stdin; it is never read from a file path). Messages containing a token or key are refused.
- **Messages to anyone else**: `skala_bridge.py send --to <chat_id> - <<'TXT'` … `TXT` queues the message and sends the owner "Balas SETUJU 123456 untuk mengirim". After the owner replies: `listen --once` then `send-approved <outbox_id>`. The code is never shown to the agent.
- **WhatsApp webhook**: verify_token checked; `whatsapp.app_secret` is **required** and `X-Hub-Signature-256` is enforced.
- **Approvals** count only from an owner's **private** chat (not groups).

Setup: `SETUP.md`. Telegram first (free, no business verification). WhatsApp Cloud API needs a Meta business account and a public HTTPS webhook. Unofficial WhatsApp libraries (Baileys, whatsapp-web.js) risk the number being banned; not supported here.

Limits: photos sent by chat are recorded as `[photo] caption`; the file itself must be downloaded separately. Long tables go as files, not chat text.

## Excel mode

```bash
python3 PLUGIN/bin/buat_excel.py --nama-proyek "Renovasi Rumah Bpk. Andi" --nilai-kontrak 250000000 --output ~/Documents/renovasi-andi.xlsx
python3 PLUGIN/bin/buat_excel.py --kosong --output template.xlsx
```

Six sheets: Proyek, RAB, Pengeluaran, Progress (with S-curve chart), Tugas, Panduan. Weights, contributions, totals and deviation are live formulas. Requires `pip install openpyxl`. Confirm the output path on the plan card; do not overwrite an existing file without saying so.

When the user later moves to Skala, the workbook rows are the import material.
