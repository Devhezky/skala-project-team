# Security model

## Threats and controls

| Threat | Control | Where |
|---|---|---|
| Agent writes wrong or unwanted data | Actions the user confirmed in chat are saved directly (v1.4), bounded by the staff member's Skala permissions, a per-type admin switch, the expense amount limit, warnings (duplicate, old date, same project name, progress going down), an hourly cap and the master switch; each is audited, notified and listed in the decision history with the user's words. The server cannot verify the typed "ya": a document that tricks the agent into claiming one is the residual risk, which is why admins can switch types off (deletion in particular). Held-back items need a logged-in person's approval on a server-rendered page. Payload hash and permissions re-checked on every write | Server (chat "ya": prompt) |
| Agent misdescribes what it will do | The approval page is rendered by Skala from the stored payload, not from agent text | Server |
| Prompt injection via receipts, chats, files | Content wrapped as untrusted; lead, intake and QA rules (SEC-01); writes need human approval anyway | Prompt + server |
| Key leaks through chat or logs | Device login (no secret typed); key stored by the script only, never printed; `redact()` on every output and log line | Code |
| Key committed to git / shipped in a zip | Credentials live in `~/.skala-workbuddy/` outside the plugin folder; `.gitignore` also covers `**/config/config.json` | Code + repo |
| Stolen key | Scopes read + propose only; 90-day lifetime; 30-day idle expiry; revoke / revoke all; hashed at rest; no key in URLs; per-key rate limit | Server |
| Data beyond the user's role | Skala `staff_can` + project membership on every endpoint; finance hidden without invoice permission; "not found" for invisible projects | Server |
| Foreman sees prices | `field` chat role; bridge blocks money in replies | Code |
| Unknown person uses the Telegram bot | Allowlist, empty = nobody; per-chat rate limit | Code |
| Message sent to the wrong person | Only replies to the asker are direct; anything else needs the owner's `SETUJU <code>` from their own chat; the agent never sees the code | Code |
| Forged WhatsApp webhook | `verify_token` on subscribe; `X-Hub-Signature-256` when `app_secret` is set | Code |
| Connecting to a fake Skala | Only `https://*.skalapro.cloud`; returned tenant URL re-checked | Code |
| Malicious receipt upload | Type from bytes (JPEG/PNG/WEBP/PDF), ≤5 MB, server-generated filename, stored only after approval | Server |
| Brute force of pairing / device codes | Rate limits per IP and global; 15 / 10-minute expiry; single use with atomic claim | Server |

## Issues found in v1 and fixed in v2 / v1.1

| v1 issue | Fix |
|---|---|
| `.gitignore` rule `config/config.json` did not match `plugins/…/config/config.json` (verified with `git check-ignore`) | Credentials moved out of the plugin; `.gitignore` uses `**/` patterns |
| Publishing notes contained the first characters of a live Skala key | Notes removed from the repo; **rotate that key** |
| Telegram bot token printed inside error messages (token is in the URL path) | URLs redacted in every error |
| `config.json` written world-readable | Written atomically with mode 600 in a 700 folder |
| First 10–12 characters of the API key printed | Never printed |
| `pair --url` accepted any host | `*.skalapro.cloud` over HTTPS only |
| Whitelist empty = everyone allowed; `wajib_whitelist` and rate limit documented but not implemented | Fail-closed allowlist and working rate limit |
| `send` could message any chat id directly | Owner approval required, verified in code |
| Approval was a `--ya` flag the agent passed itself | No write command; approval happens in Skala |
| Server: client-chosen receipt filename (path traversal → RCE), no authorization, direct writes incl. invoices, plaintext keys, key in URL, pairing race | See the server module README |

## Reporting

Security issues: **[fill in contact]**. Please do not open public issues for vulnerabilities.
