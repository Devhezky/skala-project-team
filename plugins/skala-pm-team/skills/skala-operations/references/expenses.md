# Feature 1 — Expense entry (pencatatan pengeluaran)

Goal: turn receipts (nota), kasbon and purchase notes into expense rows for Skala (or Excel) **fast**, with the right category, and one short confirmation. Keep it light: the user wants to log spending, not be audited.

## Principle

- **No receipt is fine.** Cash, transfers and kasbon often have no nota. Never ask for one, never warn about a missing one.

- **Decide, don't ask.** Pick the category, the date and the description yourself; show them on the card. The user corrects with one word if needed.
- **Ask only when the amount or the project is unknown.** Everything else is an assumption shown on the card.
- **One card, one question.** No progress messages, no rule IDs, no "what will not happen" lists for plain expense entry.

## Category: choose it automatically

In Skala, fetch the tenant's categories once (`skala_client.py expense-categories`) and pick the one whose **meaning** best fits the item. Names differ per tenant (e.g. "Penggunaan Bahan" vs "Material"); match by meaning, not by exact word. Always use the `category_id` from that list.

| What was bought / paid | Category meaning | Typical tenant names |
|---|---|---|
| Triplek/multiplek, HPL, semen, pasir, bata, besi, cat, keramik, paku, lem, engsel, kabel, pipa, aksesoris | Materials used | **Penggunaan Bahan**, Material, Bahan |
| **Kasbon** to a worker/foreman, upah harian, borongan tukang, lembur, uang makan tukang, gaji | Wages | **Gaji Karyawan**, Upah, Tenaga Kerja |
| Sewa scaffolding, molen, genset, mobil/pickup, laser cutting | Equipment rental | Sewa Alat |
| Ongkir, bensin, tol, parkir | Transport | Transport |
| Electrical, plumbing, glass, powder coating done by a third party | Subcontractor | Subkon |
| Anything else (permits, cleaning, refreshments, admin) | Other | Lain-lain |

Examples: "beli triplek 10 lembar" → **Penggunaan Bahan**. "Kasbon Benzema 2jt" → **Gaji Karyawan**.

- Ask about the category only if **nothing** in the tenant's list fits. Then offer the 2–3 closest names in one line.
- Excel mode (no Skala): use the six names above in bold/first column: Penggunaan Bahan, Gaji Karyawan, Sewa Alat, Transport, Subkon, Lain-lain.

## Kasbon

A kasbon is recorded as an expense in the wages category (Gaji Karyawan or the tenant's equivalent), payment `Kasbon`, with the person's name in the description: `Kasbon Benzema`.

## Row fields

| Field | Rule |
|---|---|
| Date | Receipt date. "kemarin"/"tgl 18" → resolve it and show the date. No date at all → the message date. |
| Description | `<item> — <vendor>` or `Kasbon <name>` |
| Amount | Receipt total. Multi-item receipt: one row per item only if the items fall in **different** categories; otherwise one row with the receipt total. |
| Category | As above |
| Payment / status | From the text if stated; otherwise leave empty (do not ask) |
| Note | Optional: receipt number, qty × unit price |
| Source | Which photo or chat line (kept in the proposal, not shown on the card) |

## Quick checks (QA, rule IDs in `review-rules.md`)

1. **Arithmetic** [EXP-01]. If qty × price ≠ the receipt total, use the receipt total and show both numbers in one line.
2. **Same receipt twice** [EXP-02]. Same vendor + date + amount in one batch → keep one, say so in one line.
3. **Category from the tenant's list** [EXP-03].
4. **Date sanity** [EXP-04]. A date in the future is shown as a warning.

Nothing else is checked for plain expense entry.

## Workflow (fast lane)

1. Sari extracts the rows and suggests the category per row from the tenant's list.
2. Wulan runs the quick check once (no rejection loop).
3. Raka shows the expense card as a table (`confirmation-protocol.md` → "Expense card").
4. On "ya": one `expense.create` per row with `"confirmed_in_chat": true` and the user's words in `user_said`:
   `{"project_id", "amount", "expense_name", "category_id", "date": "YYYY-MM-DD", "note"}` and, **whenever the user sent a nota (photo or PDF) for that row, `"receipt": "<file path of that attachment>"` at the top level of the propose JSON, next to `payload`** (never inside it). Do not skip it: the nota is the evidence kept on the expense in Skala. One file per expense; a nota split over several rows is attached to each row. JPG/PNG/WEBP/PDF, max 5 MB. If you have no file path for the image, tell the user in one line instead of saving silently without it. A receipt cannot be added later to an existing expense from chat; attach it when creating.
   The reply shows `receipt_attached`: say "📎 nota terlampir" per row, or say plainly that it was not attached.
   Skala saves it immediately and returns `expense_url`. Reply: "✅ 3 pengeluaran tersimpan" + one link per row.
   A row that comes back `pending` (above the admin's limit, similar to an existing expense, or that kind of action switched off) needs Setujui in Skala: one line with the reason and the link.

## Example

**User:** "nota tgl 18 Toko Sinar Jaya, triplek 10 lembar @125rb, ongkir 100rb, transfer. terus kasbon Benzema 2jt."

**Card:**

**3 pengeluaran · Renovasi Rumah Bpk. Andi**

| No | Tanggal | Keterangan | Jumlah | Kategori |
|:-:|:-:|---|--:|---|
| 1 | 18/10 | Triplek 10 lbr — Sinar Jaya | Rp1.250.000 | Penggunaan Bahan |
| 2 | 18/10 | Ongkir — Sinar Jaya | Rp100.000 | Transport |
| 3 | 03/11 | Kasbon Benzema | Rp2.000.000 | Gaji Karyawan |
| | | **Total** | **Rp3.350.000** | |

**Simpan ke Skala?** (ya / ubah no. …)

**After "ya":**

**✅ 3 pengeluaran tersimpan di Skala**

| No | Keterangan | Jumlah | Link |
|:-:|---|--:|---|
| 1 | Triplek — Sinar Jaya | Rp1.250.000 | [Buka](https://…/admin/expenses/list_expenses/101) |
| 2 | Ongkir — Sinar Jaya | Rp100.000 | [Buka](https://…/admin/expenses/list_expenses/102) |
| 3 | Kasbon Benzema | Rp2.000.000 | [Buka](https://…/admin/expenses/list_expenses/103) |

Card rules:
- Always a Markdown table with exactly these columns: No · Tanggal · Keterangan · Jumlah · Kategori, plus a bold **Total** row. English: No · Date · Description · Amount · Category.
- Notes: only when something can change the result (possible duplicate, receipt total ≠ qty × price, date outside the project period). At most 2 short lines under the table, starting with "Catatan:". Never mention missing receipts, missing quantities, RAB links, or that two rows are *not* duplicates.
- Last line: **Simpan ke Skala?** (ya / ubah no. …). Excel mode: **Buat file Excel-nya?** (ya / ubah no. …).
- After saving: the result table No · Keterangan · Jumlah · Link (one "Buka" link per row). Rows not saved show the reason in the Link column and the approve link.

Ask before the card only if the project is unclear (user has several active projects and nothing points to one) or an amount is missing.
