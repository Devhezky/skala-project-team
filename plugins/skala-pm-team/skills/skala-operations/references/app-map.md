# Skala Pro — app map

## What it is

A web ERP for **interior and construction contractors**. Not a CRM, not heavy 3D rendering: the focus is project operations and stopping margin leaks.

- Site: `skalapro.cloud` · App: `app.skalapro.cloud` or `<company>.skalapro.cloud`
- Login: email + password, or "Login with SKALA" (SSO)
- Multi-tenant: one installation hosts several companies/workspaces
- Trial: 7 days

## Module families

| Family | Modules |
|---|---|
| **Planning** | Price database, estimates, RAB, Material Optimizer |
| **Execution** | Project tasks, progress, schedule, S-curve |
| **Administration** | Invoices, payments, expenses |
| **Collaboration** | Client portal, gallery, comments, 360° panorama |
| **Quality** | QC checklists, findings |
| **WorkBuddy AI** | Agent connections, proposals waiting for approval, activity log |

## Signature features

1. **Material Optimizer** — cut lists for sheet materials (HPL, plywood): cutting pattern, sheet count, waste. Feeds RAB and BOQ.
2. **AI Copilot** — receipt photo → amount, date, vendor → admin verifies. Extraction still needs human review.
3. **360° panorama** — room documentation with navigation points and floor plan.

## Data flow

```
RAB / BOQ ──(split into work items, each with a weight %)──▶ Schedule
   │                                                        │
   │                                                        ▼
   │                                              Planned S-curve ◀──┐
   │                                                        │        │ compared
   │                                         Site progress ─▶ Actual S-curve
   │                                                        ▼
   │                                              Progress report (client portal)
   ▼
Actual expenses ──▶ Cost control (plan vs actual)   ← must link to the same RAB items
```

Consequences:
- RAB items without weights → progress % is a guess.
- Expenses without RAB links → cost control cannot say which work is leaking.
- Schedule not split by period → no planned S-curve.

So if the user asks for a progress update and RAB has no weights, build the weights first.

## Users

| Role | Uses Skala for |
|---|---|
| **Business owner / operations lead** | Main buyer: dashboard, margin, cost control |
| **Admin** | Expenses, invoices, AI Copilot verification |
| **Estimator** | RAB, BOQ, Material Optimizer |
| **Site PIC / foreman** | Progress, photos, QC checklist (no cost data) |
| **Client** | Portal: progress, photos, documents |

Owners usually are not operators: they know the project but will not type receipts. That is the gap this team fills.

## Problems Skala solves

1. Scattered data: receipts, photos and reports in different places.
2. Late cost control: plan vs actual compared only when the project is far along.
3. Repeated calculation: material estimates eat the interior team's time.
4. Repeated client updates: PICs explain progress again and again.

## Limits

- The agent sees only what the connected account's role allows, and can only propose.
- Menu labels change between versions; describe menus by function and ask the user to confirm.
- Some modules (Material Optimizer, panorama, invoices) have undocumented details. If asked something very specific, say so and help at the workflow level.
