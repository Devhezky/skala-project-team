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

## Security audit at a glance

Audited on **3 November 2026** — the plugin (v2) and the Skala server module it talks to, not just the happy path. Method: two independent reviewers who did not write the code (one server, one agent/LLM), automated checks (bandit, secret-pattern scan, 18 agent tests, 13 server unit tests, 10 bridge self-checks) and a working proof-of-concept for every suspected issue. Frameworks: OWASP ASVS 4.0.3 L2, OWASP API Top 10 (2023), OWASP LLM Top 10 (2025), MITRE ATLAS, NIST CSF 2.0.

**46 findings: 36 fixed in code, 3 accepted with documented mitigation, 7 owner actions in the operating environment.** No remote code execution, authentication bypass, cross-tenant read, SQL injection or approval bypass was found.

- **Server guarantees.** Agent keys are hashed, compared in constant time, scoped `read,propose` and expire. There is no write endpoint for the agent. Approval is POST + CSRF, atomic, re-checked for the approver and executed once. Every endpoint re-checks the person's Skala permissions and project membership.
- **Plugin guarantees.** Credentials live outside the plugin folder (0700/0600, atomic writes). Message text is never read from a path, and outgoing messages are refused if they contain a configured secret. User text never goes inside a shell argument. The amount guard normalises `1,2 M`, `IDR 2 500 000`, `$300`, `sejuta` and zero-width characters.
- **Known limit.** WorkBuddy cannot sandbox the agent's Bash tool. A prompt-injected agent with full shell access can bypass the local guards; server-side read-by-role and human approval still hold. Practical rule: do not run sessions with *Allow full access* while processing outside documents or chat messages.
- **What this audit does not cover.** Changes made to the deployed server module after review, and runtime checks that need a live Skala tenant (`STAGING_TESTS.md` §1–10).

Every finding, its ID and its fix is in [`docs/SECURITY-AUDIT.md`](docs/SECURITY-AUDIT.md).

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
- [x] Choose a license and add `LICENSE` (MIT — free to use, modify and redistribute with attribution).
- [ ] Replace `author.email` in `plugin.json`.
- [ ] Replace the placeholder avatars of Sari, Dimas and Wulan with illustrations in the same style as Raka (512×512, ≤500 KB).
- [ ] Confirm `settings.json` format against the official Expert Team template (`trading-team.zip` on the Open Platform).
- [ ] Run `python3 tests/test_agent_guards.py` (expect 13 OK).
- [ ] Run behaviour tests B-01…B-24 and fill in `docs/TEST-PLAN.md` with screenshots.
- [ ] Skala server module v1.1 installed on the tenants you demo with, and `STAGING_TESTS.md` passed.
- [ ] `git status` shows no `config.json`, `.env`, `*.log` or `data/`.

## Bahasa Indonesia, singkat

Expert ini adalah tim empat agent (Raka, Sari, Dimas, Wulan) yang mengubah nota, kasbon, chat lapangan dan RAB menjadi data proyek yang sudah dicek. Setiap angka punya sumber, setiap draf diperiksa QA, dan **tidak ada yang disimpan ke Skala atau dikirim ke siapa pun sebelum kamu menyetujui detailnya**. Tanpa Skala pun tetap jalan, hasilnya berupa file Excel. Agent otomatis membalas dalam bahasa yang kamu pakai.

## License

MIT — free to use, copy, modify, merge, publish, distribute, sublicense and sell, as long as the copyright notice and this permission notice are kept. Provided **as is**, without warranty. See [`LICENSE`](LICENSE).

Artinya: expert ini gratis dipakai, termasuk untuk proyek komersial dan klien kamu. Kamu boleh mengubah dan membagikannya lagi, cukup cantumkan credit "Tim Skala Pro ID". Tidak ada jaminan — pakai dengan risiko sendiri. Logo, nama "Skala Pro", dan avatar karakter adalah merek/aset Tim Skala Pro ID dan tidak otomatis ikut lisensi ini.

