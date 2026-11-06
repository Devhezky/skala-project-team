# Feature 2 — Progress update (S-curve / Kurva-S and percentages)

Goal: turn site reports ("walls 80%, tiles just started") into the **correct total progress**, the position against the **S-curve**, schedule deviation, and a client-ready narrative.

## Three concepts to keep apart

| Term | Meaning | Example |
|---|---|---|
| **Item progress** | How complete one work item is | "Walls 80% done" |
| **Item weight (bobot)** | Item value ÷ total RAB | Walls Rp40 jt of Rp100 jt → 40% |
| **Total progress** | Σ (weight × item progress) | e.g. 62,4% |

Total progress is **not** the average of item percentages (PRG-02). Small and large items are not equal.

## Formulas

```
item weight (%)   = (item value ÷ total RAB) × 100
total progress    = Σ (item weight × item progress)
earned value      = total progress × contract value
deviation         = actual cumulative − planned cumulative (same period)
```

| Work item | Value | Weight |
|---|---|---|
| Preparation | Rp10.000.000 | 10,0% |
| Foundation | Rp30.000.000 | 30,0% |
| Walls | Rp40.000.000 | 40,0% |
| Finishing | Rp20.000.000 | 20,0% |
| **Total** | **Rp100.000.000** | **100,0%** |

## Building the planned S-curve

The S-shape follows the rhythm of work: slow at the start (preparation, mobilisation), fast in the middle (structure, walls), slow at the end (finishing, cleaning, handover/BAST).

1. Choose the period. Indonesian standard: **weekly**. Very short projects (< 1 month) daily; long projects (> 6 months) may be bi-weekly, but weekly is safer for control.
2. Distribute each item's weight over its weeks according to the schedule. A 4-week item with 40% weight: 10/10/10/10 (linear) or 5/15/15/5 (realistic).
3. Sum all items per period → **period weight**.
4. Accumulate → **cumulative %**. These are the S-curve points.
5. The curve must end at exactly 100% (PRJ-02). Below 100% = missing weight; above = double counting.

## Reading deviation

| Deviation | Status | Action |
|---|---|---|
| ≥ +2% | **Ahead** | Faster than plan. Watch that spending is not also running ahead |
| −2% to +2% | **On track** | No intervention |
| −2% to −5% | **Attention** | Check the items causing it, prepare extra labour |
| −5% to −10% | **Late** | Concrete recovery plan: extra shift, more workers, re-sequence |
| < −10% | **Critical** | Escalate to the owner; is the end date still realistic? |

These are guidelines. Projects with heavy delay penalties should use tighter thresholds.

## Workflow

1. **Make sure weights exist.** If the user has none, build them from RAB values first. Without them every later number is meaningless; say so calmly.
2. **Collect item progress.** "Untuk tiap item, kasih persentase kasarnya saja, nanti saya hitung." Never ask the user to compute weights.
3. **Compute total progress** with `scripts/kurva_s.py`. Show the table, not just the result, so the user sees which items drag.
4. **Compare with plan** for the same period (PRG-03). No planned curve → help build it from the schedule, or, without a schedule, say plainly that deviation cannot be computed yet and report actual progress only.
5. **Causes and actions.** For each item more than 5% behind its own plan, give a likely cause (late material, too few workers, weather, design change) and a proposed action, labelled as a proposal.
6. **Client report.** 4–6 lines + a short table. No internal jargon, **never margins or vendor prices**.
7. **For Skala:** `scurve.update` with `realisasi` = **cumulative** % for the period (PRG-04), `rencana` if known, `periode_label` (e.g. "Minggu 3"), `periode_type`, `urutan`. If the new value is lower than the current project progress, show the warning (PRG-05). Skala moves headline project progress only for the latest period.

## Script

```bash
python3 scripts/kurva_s.py --demo
python3 scripts/kurva_s.py data.json
```

```json
{
  "project": "Renovasi Rumah Bpk. Andi",
  "contract_value": 250000000,
  "items": [
    {"name": "Pekerjaan persiapan", "value": 25000000, "progress": 100},
    {"name": "Pekerjaan pondasi",   "value": 75000000, "progress": 90},
    {"name": "Pekerjaan dinding",   "value": 100000000, "progress": 20},
    {"name": "Pekerjaan finishing", "value": 50000000, "progress": 0}
  ],
  "planned_cumulative": 40.0
}
```

Without `planned_cumulative` the script reports actual progress only and notes that deviation cannot be computed.

## Worked example

**User:** "Minggu ke-3. Persiapan selesai, pondasi 90%, dinding baru jalan 20%, finishing belum."

```
preparation = 10% × 100% = 10,0%
foundation  = 30% ×  90% = 27,0%
walls       = 40% ×  20% =  8,0%
finishing   = 20% ×   0% =  0,0%
───────────────────────────────
total progress           = 45,0%
```

Planned cumulative week 3 = 40,0% → deviation **+5,0% (Ahead)**.

Note: ahead overall, but the foundation is still 10% below its own target; the gain comes from finished preparation. Overall deviation alone is not enough; always check items.

## Common mistakes

1. Averaging percentages instead of weighting: (100+90+20+0)/4 = 52,5% is **wrong**; the correct value is 45,0%.
2. Weights not summing to 100% after items were added.
3. Progress without evidence (photo/checklist). Remind gently.
4. 100% before inspection: suggest 95% until QC passes; that 5% holds back the payment term (PRG-06).
5. Comparing with the wrong period.
6. Contract value used as total RAB when RAB excludes VAT/overhead; use the same basis.

## Client report template

```
LAPORAN PROGRESS — [Project]
Periode: Minggu ke-[n] ([date] – [date])
Progress fisik: [x,x]% (rencana [y,y]% · deviasi [±z,z]%)

Pekerjaan periode ini:
- [item] — [what was done]

Pekerjaan periode berikutnya:
- [item] — [target]

Catatan: [issues / decisions needed from the client]
Dokumentasi: [n] foto lapangan di galeri proyek.

Persentase ini berdasarkan laporan pelaksana lapangan, bukan hasil opname bersama.
```

The closing line is mandatory (PRG-07); it protects the user in disputes.
