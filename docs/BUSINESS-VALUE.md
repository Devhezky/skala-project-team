# Measuring business value

Every number in the submission must come from this procedure or from Skala data. Report the sample size; do not extrapolate beyond it.

## A. Pilot timing test (≈ 1 hour)

Materials: `tests/business-value/batch-10-nota.md`, `answer-key.md`, `timing-sheet.csv`.

1. **Manual run (M1, ideally also M2 by a second person).** The tester enters the 10 nota into Skala (or the Excel template) the way they normally would. Start the stopwatch when they first see the batch, stop when the last row is saved. Do not help or hint.
2. **Agent run (A1, A2).** A tester who has **not** just done the manual run (or the same person a day later) pastes the batch into WorkBuddy. Stop when the last item is approved (Skala) or the workbook is generated (Excel). Time spent answering the agent's questions counts.
3. **Score both** with `answer-key.md`: checks correct (0–4), category accuracy (0–9), errors in saved data, number of questions asked.
4. Screenshot the agent's plan card and questions; they double as test-result evidence (B-03 … B-06).
5. Fill `timing-sheet.csv`.

Fairness: same batch, same project, same destination (Skala or Excel), no copy-paste from the answer key. If the same person does both runs, do the agent run first or wait a day, and say so in the report.

## B. Baseline from your own Skala data (aggregates only, no personal data)

Run on a tenant database with permission (replace `tbl` with the tenant prefix).

```sql
-- Expenses entered per month and per active project (last 6 months)
SELECT DATE_FORMAT(dateadded, '%Y-%m') AS month,
       COUNT(*)                         AS expenses,
       COUNT(DISTINCT project_id)       AS projects,
       ROUND(COUNT(*) / COUNT(DISTINCT project_id), 1) AS expenses_per_project
FROM tblexpenses
WHERE dateadded >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY month ORDER BY month;

-- Possible duplicates already in the data (same project, date, amount)
SELECT COUNT(*) AS duplicate_groups, SUM(c - 1) AS extra_rows, SUM((c - 1) * amount) AS amount_at_risk
FROM (SELECT project_id, date, amount, COUNT(*) AS c FROM tblexpenses
      WHERE dateadded >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
      GROUP BY project_id, date, amount HAVING c > 1) d;

-- Expenses without a note or description (cannot be audited)
SELECT ROUND(100 * SUM(COALESCE(NULLIF(TRIM(note), ''), NULLIF(TRIM(expense_name), '')) IS NULL) / COUNT(*), 1) AS pct_without_detail
FROM tblexpenses WHERE dateadded >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH);
```

If `dateadded` does not exist in your Skala version, use `date`. Duplicate groups are *candidates*; check a sample by hand before quoting them.

## C. Turning results into business value

```
minutes saved per receipt = (manual minutes − agent minutes) ÷ 10
hours saved per month     = minutes saved per receipt × expenses per month ÷ 60
errors prevented / batch  = manual errors in saved data − agent errors in saved data
```

Example sentence (fill in, keep the n):
> In a pilot with **n = [x]** testers on a 10-receipt batch with 4 planted checks, manual entry took **[a] min** and caught **[b]/4** issues; the agent workflow took **[c] min** including approval and caught **[d]/4**. At **[e]** expenses per month (Skala data, last 6 months), that is about **[f] hours saved per month** per company. Skala data also shows **[g]** duplicate-candidate expenses worth **Rp[h]** in 6 months, the error class the quick check catches before saving.

If the agent is slower but catches more errors, report that honestly; error prevention is the stronger claim for accountability.
