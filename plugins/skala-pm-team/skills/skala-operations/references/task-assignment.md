# Feature 3 — Task assignment (pembagian tugas)

Goal: turn a paragraph of remaining work ("sisa plafon, keramik, cat, kabinet") into a **ready-to-enter task table**: who, when, how far, and how "done" is judged.

## Rules that are never broken

- **One task, one person in charge (PIC)** [TSK-01]. Others may help; one name is accountable. A task with two PICs is owned by nobody.
- **A task must be verifiably done or not done** [TSK-04]. Without a completion criterion it stays "almost done" forever.
- **A task is linked to a RAB item** [TSK-07], so finished tasks feed progress automatically.

## Output columns

| Column | Required | Rule |
|---|---|---|
| ID | ✅ | `T-01`, `T-02`… for dependencies |
| Task | ✅ | Verb + object: "Pasang rangka plafon gypsum area ruang tamu", not "plafon" |
| Division | ✅ | See list below |
| PIC | ✅ | One name. Unknown → role (`mandor batu`) + `[perlu konfirmasi]` |
| Helpers | – | Names/roles |
| Start | ✅ | `dd/mm/yyyy` |
| Finish | ✅ | Realistic, not ideal |
| Duration | – | Working days |
| Depends on | – | e.g. `T-03` |
| RAB item | ✅ | Work item that absorbs the task |
| Done when | ✅ | Objective evidence: "Permukaan rata, gap < 2 mm, foto terkirim" |
| Status | ✅ | `Belum mulai` / `Jalan` / `Selesai` / `Tertahan` |
| Note | – | Material readiness, access, permits |

## Standard divisions

| Division | Scope |
|---|---|
| **Persiapan** | Mobilisation, initial cleaning, demolition, protection |
| **Struktur** | Foundation, sloof, columns, beams, casting |
| **Dinding & Partisi** | Brickwork, plaster, skim coat, gypsum partitions |
| **Plafon** | Hollow frame, gypsum board, profile trim |
| **Lantai & Dinding** | Screed, ceramic, granite, vinyl, stone |
| **Instalasi Listrik** | Lighting points, switches, sockets, panel |
| **Plumbing** | Clean water, waste water, sanitary |
| **Finishing** | Paint, wallpaper, coating, touch-up |
| **Furniture** | Cabinets, wardrobes, kitchen set, desks |
| **Subkon** | Glass, steel, powder coating, AC, lift |
| **Serah Terima** | Final cleaning, defect repair, BAST |

## Breakdown rules

1. **Size: 1–3 working days** [TSK-03]. "Renovasi dapur 3 minggu" is a project, not a task.
2. **One location or one kind of work per task.** Progress can differ per room.
3. **Separate different skills.** Ceiling frame (hollow) and gypsum board are two tasks.
4. **Explicit dependencies** [TSK-05]. Tiles cannot start before screed has cured.
5. **Material readiness.** A task without its material is `Tertahan` with the reason.

## Schedule rules (Indonesia) — run `scripts/check_schedule.py`

- National holidays and cuti bersama (SKB 2026–2027 data) [SCH-01/02].
- Sunday [SCH-03]; Saturday is normally a site working day.
- **Friday prayers 11:30–13:00 local time**: no meetings, site visits with the client, or calls [SCH-04].
- Meetings 08:00–17:00 local time [SCH-05]; always state WIB, WITA or WIT [SCH-07]. Makassar/Bali = WITA, Jayapura = WIT.

## Workload check

- Per person per day: at most 3 active tasks [TSK-06].
- Per person per week: 5–6 effective days, not 7.
- Key person holding 5 dependent tasks = bottleneck; tell the user.
- Four divisions in one small room on one day: re-sequence realistically.

Report these as notes, not refusals.

## Workflow

1. Get scope (remaining work or RAB), start date, target date, available people and their skills.
2. Break into tasks with standard divisions; IDs in execution order.
3. Assign PIC by skill. If the user only says "ada 4 tukang", ask their skills once; otherwise use generic roles and flag.
4. Sequence and dependencies; compute dates from durations and dependencies.
5. Workload and critical path.
6. Table + summary: number of tasks, date range, busiest PIC, 2–3 schedule risks.

For Skala, each task is a `task.create` proposal: `project_id`, `name`, `startdate`, `duedate`, `assignee_ids` (Skala staff the user names, ids from `skala_client.py staff --q <name>`; the person is then really assigned and notified in Skala), `pic_name` (for workers who are not Skala staff, e.g. tukang; plain text), `description` (done-when, dependencies, RAB item), `priority`, `weight` if known (the card then shows the project's weight total; keep it at 100%), and `checklist` for the sub-items (a list of `{"description", "finished"}`: they land in Skala's Checklist Items, not in the description). To change items later: `tasks PROJECT_ID` returns each task's `checklist` (ids) and `weight`; propose `task.checklist` with `add` / `update` (`id`, `description`, `finished`) / `remove`. Who is staff and who is not: look the name up with `staff --q`; a match → `assignee_ids`, no match → `pic_name`. If two staff match, list them and ask. Changing assignees of an existing task is `task.update` with the full new list of `assignee_ids`. Status changes are `task.status` proposals (1 Not started · 4 In progress · 5 Complete).

## Example

**User:** "Proyek renovasi rumah, sisa: plafon, keramik, cat, kabinet. Tukang: Sukirman (mandor/batu), Adi (kayu), Rudi (cat), 2 helper. Target selesai 3 minggu dari 23 Oktober."

| ID | Task | Division | PIC | Start | Finish | Dep. | RAB item | Done when | Status |
|---|---|---|---|---|---|---|---|---|---|
| T-01 | Pasang rangka hollow plafon ruang tamu & dapur | Plafon | Adi | 23/10/2026 | 25/10/2026 | — | Plafon gypsum | Rangka level, jarak 60 cm, tidak bergetar | Belum mulai |
| T-02 | Pasang papan gypsum + compound | Plafon | Adi | 26/10/2026 | 28/10/2026 | T-01 | Plafon gypsum | Sambungan rapat, tidak ada retak rambut | Belum mulai |
| T-03 | Screed lantai area servis | Lantai & Dinding | Sukirman | 23/10/2026 | 25/10/2026 | — | Lantai keramik | Rata, miring ke floor drain | Belum mulai |
| T-04 | Pasang keramik lantai 60×60 | Lantai & Dinding | Sukirman | 27/10/2026 | 31/10/2026 | T-03 | Lantai keramik | Nat konsisten, kopong < 5% | Belum mulai |
| T-05 | Plamir + cat dasar dinding | Finishing | Rudi | 26/10/2026 | 29/10/2026 | T-02 | Pengecatan | Halus, tidak belang | Belum mulai |
| T-06 | Pasang kabinet bawah dapur | Furniture | Adi | 01/11/2026 | 04/11/2026 | T-04 | Kitchen set | Pintu sejajar, engsel halus | Belum mulai |

Summary: 6 tasks · 23/10 – 04/11/2026 · busiest PIC: Adi (3 sequential tasks) · critical paths T-01 → T-02 → T-05 and T-03 → T-04 → T-06.
Risks: (1) primer depends on gypsum; a gypsum delay delays painting. (2) Adi holds ceiling and cabinets; if cabinets are built in the workshop, avoid clashing with ceiling dates.
Schedule check (`check_schedule.py`): 25/10/2026 (T-01, T-03) and 01/11/2026 (T-06 start) are Sundays (SCH-03) — confirm the crew works those days or shift the tasks.

## Common mistakes

1. Two PICs per task. 2. Tasks too big ("finishing"). 3. No completion criterion. 4. Dependencies ignored. 5. Workload not checked. 6. Tasks not linked to RAB.
