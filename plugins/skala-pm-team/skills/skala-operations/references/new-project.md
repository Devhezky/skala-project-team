# Feature 4 — New project setup (bikin proyek baru)

Goal: from "there's a new project" to a **complete setup package**: master data, RAB items with weights, schedule, planned S-curve, team and access, payment terms (termin) and QC checklist, ready to enter in one session.

## Why setup decides everything

A sloppily opened project stays broken: spending cannot be analysed because RAB was not split, progress cannot be computed because weights are missing, client reports are late because there is no baseline. **Ten extra minutes at the start save hours mid-project.** Say this if the user wants to rush.

> **What goes into Skala from here:** the project itself (`project.create`: name, client, dates, contract value, team) and afterwards tasks with weights (`task.create`) and S-curve rows. **What does not:** RAB items, payment terms (termin) and the QC checklist; they stay in the setup package or the Excel workbook for the user to enter. Say that in one line, never name the module or a version.
>
> **Quick lane:** "buat proyek baru <nama>, anggota <orang>" needs only the client and the start date from the user. Look up the client (`skala_client.py customers --q …`) and members (`staff --q …`), show the "Proyek baru" card (`confirmation-protocol.md`), and on "ya" propose `project.create`. Offer the rest of this setup (RAB, schedule, termin) **after** the project exists, as one optional sentence, not as four questions up front.

## Step 1 — Master data (ask in one block; mark what may be empty)

| Data | Required | Note |
|---|---|---|
| Project name | ✅ | Pattern `[Type] [Location/Client] — [Year]`, e.g. "Renovasi Rumah Bpk. Andi — 2026" |
| Type | ✅ | Interior / Konstruksi / Fit-out / Renovasi |
| Client | ✅ | Person or company |
| Address | ✅ | At least city + area (more detail for 360° panorama) |
| Contract value | ✅ | Final; **state explicitly whether VAT is included** (PRJ-01) |
| Start date | ✅ | Mobilisation date, not signing date |
| End date | ✅ | Per contract; note delay penalties |
| Payment terms | ✅ | Table below |
| RAB / BOQ | ✅ | Excel, PDF or typed. The main fuel |
| Team | – | Foreman, workers, admin, PIC |
| Client portal contact | – | Email for portal access |
| Retention | – | Usually 5%, held until BAST |

No RAB yet: do not stop. Draft an item framework from the project type and ask the user for values; note that weights must be updated when the final RAB arrives.

## Step 2 — Split RAB into work items

- 8–15 items for small projects (< Rp500 jt), 15–30 for medium. More than 40 is usually too detailed for weekly control (PRJ-04).
- Items at the **same level**: do not mix "Pekerjaan pondasi" with "Beli engsel".
- Each item has a value and **weight = value ÷ total × 100**.
- Weights total **exactly 100,0%** (PRG-01).

Typical interior structure:

| Group | Example items |
|---|---|
| Persiapan | Mobilisation, demolition, protection |
| Sipil | Walls, plaster, skim coat, screed |
| Plafon | Frame, gypsum, trim |
| Lantai & dinding | Ceramic, granite, vinyl, stone |
| Instalasi | Electrical, plumbing, AC |
| Finishing | Paint, wallpaper, coating |
| Furniture | Cabinets, wardrobe, kitchen set |
| Lain-lain | Final cleaning, defect repair |

## Step 3 — Schedule and planned S-curve

1. Duration per item (weeks). 2. Order and overlaps. 3. Distribute weights per week. 4. Accumulate. 5. Verify the curve ends at 100,0% (PRJ-02) and looks flat–steep–flat. Use `scripts/kurva_s.py`; check dates with `scripts/check_schedule.py` (Idulfitri and cuti bersama can remove a whole week).

Realistic distributions:

| Item type | Weekly pattern |
|---|---|
| Preparation (2 wk) | 60% / 40% |
| Structure (3 wk) | 25% / 40% / 35% |
| Walls (4 wk) | 20% / 30% / 30% / 20% |
| Finishing (3 wk) | 20% / 40% / 40% |
| Cleaning & BAST (1 wk) | 100% |

Never spread everything evenly: a straight-line S-curve always misleads.

## Step 4 — Team and access

| Role | Suggested access |
|---|---|
| Owner | Full, incl. cost & margin |
| Admin | Expenses, invoices, AI Copilot verification |
| Estimator | RAB, BOQ, Material Optimizer |
| Site PIC / foreman | Progress, photos, QC checklist — **no cost data** (PRJ-05) |
| Client | Portal: progress, photos, documents — **no internal cost** |

Foremen do not need vendor prices; over-broad access leaks margins that can be used against you in negotiation. The same rule is enforced in chats: `field` role chats never receive amounts.

## Step 5 — Payment terms (termin)

| Term | Trigger | Typical share |
|---|---|---|
| Down payment | Contract signed | 20–30% |
| Term 1 | Progress 30% | 20–25% |
| Term 2 | Progress 60% | 20–25% |
| Term 3 | Progress 90% | 20–25% |
| Retention / final | BAST, after maintenance period | 5–10% |

Total 100% (PRJ-03). Record the signed contract; **never change the contract scheme**.

## Step 6 — QC checklist (at least for finishing; that is where BAST disputes happen)

- Paint even, no streaks or drips
- Tile grout consistent, no hollow tiles
- Cabinet doors aligned, hinges silent
- All sockets work, positions match drawings
- No leftover material or debris in the handover area

## Step 7 — Lock the baseline

After RAB, weights, schedule and planned S-curve are saved: **make it the baseline**. From then on every scope change is a variation order, not a silent RAB edit. A baseline that moves with reality always looks "on track".

## Final output (in order, not one giant table)

1. Project summary (6–8 rows). 2. RAB items + weights (total 100,0%). 3. Schedule + planned S-curve (weekly, cumulative). 4. Team & access. 5. Payment terms. 6. Initial QC checklist. 7. Entry order in Skala (5–7 functional steps). Or: the Excel workbook via `bin/buat_excel.py`.

## Example summary

| Field | Value |
|---|---|
| Name | Renovasi Rumah Bpk. Andi — 2026 |
| Type | Interior renovation |
| Client | Bpk. Andi Wijaya |
| Location | Jl. Melati No. 12, Bandung |
| Contract | Rp250.000.000 (incl. VAT 11%) |
| Duration | 23/10/2026 – 20/12/2026 (9 weeks) |
| Terms | DP 30% · T1 25% (progress 40%) · T2 25% (progress 75%) · Retention 20% (BAST) |
| Team | Foreman Sukirman · Carpenter Adi · Painter Rudi · Admin: owner |

## Common mistakes

1. RAB in 3 rows ("material, labour, other"). 2. Weights ≠ 100%. 3. Straight-line S-curve. 4. Baseline edited mid-project. 5. Foreman given cost access. 6. Terms not recorded. 7. End date set to the ideal date.
