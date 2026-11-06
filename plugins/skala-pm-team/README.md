# Skala Project Team

A WorkBuddy **Expert Team** for Indonesian interior and construction contractors. It turns receipts (nota), cash advances (kasbon), site chats and RAB files into checked, ready-to-use project data, and it never writes or sends anything until a person approves the exact details.

| Agent | Role |
|---|---|
| **Raka** — Project Operations Lead | Talks to you, detects your language, runs the workflow, shows the plan card, asks for your confirmation |
| **Sari** — Field Data Clerk | Extracts every value with its source; flags unclear data and instructions hidden in documents |
| **Dimas** — Cost & Schedule Analyst | Links to RAB, computes weights and S-curve, plans tasks around holidays and Friday prayers |
| **Wulan** — QA Reviewer | Checks every draft against 51 documented rules; rejects with rule IDs; escalates after 3 rounds |

## What it does

| You give | You get |
|---|---|
| Receipt photos, kasbon, chat notes | Expense rows with the category picked automatically (triplek → Penggunaan Bahan, kasbon → Gaji Karyawan) and one short confirmation |
| "Dinding 80%, keramik baru mulai" | Weighted total progress, S-curve deviation, status, client report |
| Remaining work + names + deadline | Tasks with one PIC each, dependencies, completion criteria, schedule checks |
| A new project + RAB | Master data, weights (100%), planned S-curve, team access, payment terms, QC checklist |

Works **with Skala Pro** (reads your projects; you approve each change inside Skala) or **without** it (Excel workbook with live formulas).

## How it stays accountable

- **Sources.** Every number points to the receipt line, chat message or Skala record it came from.
- **Permissions.** With Skala it sees only what your Skala role allows. Foremen's chats never receive prices or margins (blocked in code).
- **Approval.** You confirm a short card in chat. Once you say *ya*, the action is saved in Skala right away and you get the link; it also appears in Skala's decision history with your words. Only what the server holds back (above your admin's limit, similar to existing data, progress going down, or a type your admin switched off) still needs *Setujui* in Skala. Admins can switch types off or change the limit in Skala → WorkBuddy AI.
- **Limits.** Missing data is marked, not guessed. Instructions found inside documents are reported and ignored.
- **Record.** Every step is in `~/.skala-workbuddy/audit.jsonl`; every Skala call and decision is in Skala → WorkBuddy AI → Log aktivitas.

Full sheet: `docs/ACCOUNTABILITY.md` in the repository.

## Examples

- "Nota tgl 18, Toko Sinar Jaya, semen 20 sak @68rb, pasir 850rb, ongkir 150rb. Mandor Sukirman kasbon 5jt."
- "Minggu ke-3: persiapan selesai, pondasi 90%, dinding 20%, finishing belum. Rencana 40%."
- "Sisa plafon, keramik, cat, kabinet. Tukang: Sukirman, Adi, Rudi. Target 3 minggu dari 23 Oktober."
- "Saya belum punya Skala, bikin versi Excel-nya."
- "Hubungkan ke Skala."

## Requirements

- WorkBuddy with Expert Team support.
- Python 3.8+ (standard library). `openpyxl` only for Excel: `pip install openpyxl`.
- Optional: Skala Pro with module `skala_workbuddy` **v1.1 or later**; Telegram bot; WhatsApp Cloud API.

Setup: [`SETUP.md`](SETUP.md).

## Package contents

```
.codebuddy-plugin/plugin.json      Team manifest
settings.json                      Sets the lead agent
agents/                            Raka (lead), Sari, Dimas, Wulan
skills/skala-operations/
  SKILL.md                         Router
  references/                      confirmation-protocol, security, review-rules, expenses,
                                   progress-s-curve, task-assignment, new-project,
                                   output-format, integration, app-map, glossary
  scripts/                         kurva_s.py, check_schedule.py, id_holidays.json
bin/                               skala_client.py, skala_bridge.py, audit_log.py, buat_excel.py, _common.py
config/config.example.json         Template only (no secrets)
avatars/
```

No credentials are included. They are created on your machine in `~/.skala-workbuddy/` (folder 700, files 600).
