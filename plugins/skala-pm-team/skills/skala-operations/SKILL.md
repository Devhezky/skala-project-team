---
name: skala-operations
description: Operating manual for the Skala project-operations team — expense entry from receipts and kasbon, weighted progress and S-curve (Kurva-S), task assignment for foremen and workers, new-project setup with RAB weights, the confirmation protocol, the QA rulebook, security rules, Skala Pro connection (read + propose only) and the Excel fallback.
---

# Skala operations manual

Skala Pro (`skalapro.cloud`) is an ERP for Indonesian interior and construction contractors. This skill is shared by Raka (lead), Sari (intake), Dimas (analysis) and Wulan (QA).

## Read only what the task needs

Do not read files for greetings, connecting, status or simple questions. For data work, open the one file for that task type, once per session. Never read the scripts' source code; use `--help`.

| Need | File |
|---|---|
| When and how to ask for confirmation; the plan card; audit events | `references/confirmation-protocol.md` |
| Untrusted content, secrets, permissions, roles | `references/security.md` |
| QA rule catalogue with IDs | `references/review-rules.md` |
| Expenses, receipts, kasbon reconciliation | `references/expenses.md` |
| Progress %, weights, S-curve, deviation | `references/progress-s-curve.md` |
| Task breakdown, PIC, dependencies, workload | `references/task-assignment.md` |
| New project: RAB, weights, schedule, team, termin, QC | `references/new-project.md` |
| Tables, number/date formats, tone | `references/output-format.md` |
| Skala login, proposals, Telegram/WhatsApp, Excel | `references/integration.md` |
| Skala modules, data flow, user roles | `references/app-map.md` |
| Indonesian ↔ English terms | `references/glossary.md` |

## Locating the scripts

Scripts sit in this plugin. `PLUGIN` is two folders above this skill's folder (`.../skala-pm-team`).
If you do not know the path: `ls -d ~/.workbuddy-ai/plugins/marketplaces/*/plugins/skala-pm-team 2>/dev/null | head -1` (resolve once per session).

| Script | Purpose |
|---|---|
| `PLUGIN/bin/skala_client.py` | Skala login, read data, **propose** changes (no write command exists) |
| `PLUGIN/bin/skala_bridge.py` | Telegram/WhatsApp mailbox with allowlist, roles and owner approval |
| `PLUGIN/bin/audit_log.py` | Record what the team saw, decided and did |
| `PLUGIN/bin/buat_excel.py` | Excel workbook equivalent to Skala (requires `openpyxl`) |
| `scripts/kurva_s.py` | Weights, weighted progress, deviation, status |
| `scripts/check_schedule.py` | Holidays (SKB 2026–2027), Sunday, Friday prayers, office hours, WIB/WITA/WIT |

## Principles

1. **RAB is the backbone.** Every expense and task links to a RAB item, or is explicitly marked `[tanpa item RAB]`.
2. **Prepare, never pretend.** Nothing is in Skala until the user said yes (expenses) or approved it in Skala (everything else), and the state is `executed`. Never say "tersimpan" otherwise.
3. **Show the calculation.** Weights, totals and deviations must be traceable to a formula and a source.
4. **Mark assumptions.** `[asumsi]` / `[assumption]`, `[perlu konfirmasi]` / `[needs confirmation]`, `[kosong]` / `[empty]`.
5. **Ask once, in one block,** and only what blocks a correct result.
6. **Menu names vary by version.** Describe menus by function and ask the user to confirm the label they see.
7. **Physical progress is not opname.** State once per report that percentages come from the site team, not a joint measurement.
8. **Reply in the user's language.** Keep Indonesian field terms.
