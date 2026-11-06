# Answer key — batch-10-nota (do not show testers before the run)

## 4 checks the agent must get right

| # | Issue | Rule | Correct handling |
|---|---|---|---|
| P1 | Nota 4 = nota 2 (same vendor, date, amount) | EXP-02 | Keep one row; say so in one line on the card |
| P2 | Nota 6: 40 × Rp135.000 = Rp5.400.000, receipt says Rp5.200.000 | EXP-01 | Use the receipt total Rp5.200.000; show both numbers in one line |
| P3 | Nota 7 is a kasbon | EXP-03 | Expense row "Kasbon Sukirman" → **Gaji Karyawan** |
| P4 | Nota 8 is delivery | EXP-03 | **Transport**, not materials |

Nota 9 (rokok, pulsa) and nota 10 (round amount) are recorded as given; the user can drop or change them on the card with one word. They are not scored.

## Expected card (no question needed)

| # | Date | Item | Total | Category |
|---|---|---|---|---|
| 1 | 14/10 | Semen + pasir — Sinar Jaya | Rp2.210.000 | Penggunaan Bahan |
| 2 | 15/10 | Besi beton 10mm — Toko Besi Makmur | Rp2.760.000 | Penggunaan Bahan |
| 3 | 15/10 | Multiplek 18mm — UD Kayu Jati | Rp2.940.000 | Penggunaan Bahan |
| 4 | 16/10 | Cat tembok + kuas — Toko Cat Warna (belum bayar) | Rp2.515.000 | Penggunaan Bahan |
| 5 | 16/10 | Keramik 60x60 — Toko Keramik Indah | Rp5.200.000 | Penggunaan Bahan |
| 6 | 17/10 | Kasbon Sukirman | Rp5.000.000 | Gaji Karyawan |
| 7 | 17/10 | Ongkir — Sinar Jaya | Rp150.000 | Transport |
| 8 | 18/10 | Rokok + pulsa — Indomaret | Rp164.000 | Lain-lain |
| 9 | 18/10 | Tukang las | Rp1.500.000 | Gaji Karyawan |

**Total: Rp22.439.000** (9 rows; nota 4 skipped as duplicate).

## Scoring

- **Checks correct** = P1–P4 handled as above (0–4).
- **Category accuracy** = rows with the expected category (0–9).
- **Errors in saved data** = wrong amount, wrong date, wrong category, duplicate saved (count each).
- **Questions asked** = expected 0.
