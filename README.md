# Skala Expert Marketplace

WorkBuddy marketplace containing **Skala Project Team** (`skala-pm-team`): an accountable four-agent team for Indonesian interior and construction contractors.

> Messy site receipts become approved project records.

| | |
|---|---|
| Expert | [`plugins/skala-pm-team`](plugins/skala-pm-team/README.md) |
| Setup | [`plugins/skala-pm-team/SETUP.md`](plugins/skala-pm-team/SETUP.md) |
| Accountability sheet | [`docs/ACCOUNTABILITY.md`](docs/ACCOUNTABILITY.md) |
| Architecture & trust boundaries | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Security model | [`docs/SECURITY.md`](docs/SECURITY.md) · audit: [`docs/SECURITY-AUDIT.md`](docs/SECURITY-AUDIT.md) |
| Tests & results | [`docs/TEST-PLAN.md`](docs/TEST-PLAN.md) · `python3 tests/test_agent_guards.py` |
| Hackathon submission pack | [`docs/SUBMISSION.md`](docs/SUBMISSION.md) |

## Install

**From this repository (marketplace source):**

```bash
/plugin marketplace add https://github.com/<owner>/skala-expert-marketplace
/plugin install skala-pm-team
```

Then open **Experts → Expert Teams** in WorkBuddy.

**Test locally before publishing:**

```bash
/plugin marketplace add "/path/to/skala-expert-marketplace"
python3 tests/test_agent_guards.py
```

**Official WorkBuddy Expert Market:** zip `plugins/skala-pm-team/` and upload it in the WorkBuddy Open Platform (open.workbuddy.cn → 发布管理 → 专家). Checklist below.

## Pre-publication checklist

- [ ] Rotate any Skala key or Telegram token that was ever stored in an old plugin folder or shared zip.
- [ ] Choose a license and add `LICENSE`.
- [ ] Replace `author.email` in `plugin.json`.
- [ ] Replace the placeholder avatars of Sari, Dimas and Wulan with illustrations in the same style as Raka (512×512, ≤500 KB).
- [ ] Confirm `settings.json` format against the official Expert Team template (`trading-team.zip` on the Open Platform).
- [ ] Run `python3 tests/test_agent_guards.py` (expect 13 OK).
- [ ] Run behaviour tests B-01…B-24 and fill in `docs/TEST-PLAN.md` with screenshots.
- [ ] Skala server module v1.1 installed on the tenants you demo with, and `STAGING_TESTS.md` passed.
- [ ] `git status` shows no `config.json`, `.env`, `*.log` or `data/`.

## Bahasa Indonesia, singkat

Expert ini adalah tim empat agent (Raka, Sari, Dimas, Wulan) yang mengubah nota, kasbon, chat lapangan dan RAB menjadi data proyek yang sudah dicek. Setiap angka punya sumber, setiap draf diperiksa QA, dan **tidak ada yang disimpan ke Skala atau dikirim ke siapa pun sebelum kamu menyetujui detailnya**. Tanpa Skala pun tetap jalan, hasilnya berupa file Excel. Agent otomatis membalas dalam bahasa yang kamu pakai.
