# Setup

Every step is optional. After step 0 the team already works (Excel mode).

`PLUGIN` below is the installed folder, e.g. `~/.workbuddy-ai/plugins/marketplaces/<marketplace>/plugins/skala-pm-team`.

## 0. Check the scripts (1 minute)

```bash
cd "$PLUGIN"
python3 bin/skala_bridge.py selftest      # expect: 10 of 10 checks passed
python3 bin/skala_client.py status        # expect: "mode": "excel_only"
python3 skills/skala-operations/scripts/check_schedule.py --demo
pip install openpyxl                      # only for Excel output
```

Your private folder is `~/.skala-workbuddy/` (created automatically, permissions 700/600). Nothing secret is ever stored inside the plugin folder.

## 1. Connect Skala Pro (optional, 2 minutes)

Requires the Skala module `skala_workbuddy` v1.1+ on your tenant, and a Skala account allowed to connect agents (admin, or role permission *WorkBuddy AI → connect*).

In WorkBuddy, just say **"hubungkan ke Skala"**. Or in a terminal:

```bash
python3 bin/skala_client.py login start --url https://<company>.skalapro.cloud
#  → prints a link and a code like KQ7M-3XPA
#  Open the link, sign in, TYPE the code, check the agent name, tick the box, press Setujui.
python3 bin/skala_client.py login wait
```

You never copy a password or key. The agent can then **read** what your role allows and **propose** changes; you approve each one in Skala → WorkBuddy AI.

Fallback (machine without a browser): in Skala → WorkBuddy AI → *Buat kode pairing*, then `python3 bin/skala_client.py pair WB-XXXX-XXXX --url https://<company>.skalapro.cloud`.

Disconnect: `python3 bin/skala_client.py logout`, or *Putuskan* in Skala.

Upgrading from v1: run `python3 bin/skala_client.py migrate-config`, delete the old `config/config.json` it points to, revoke the old key in Skala and log in again.

## 2. Telegram (optional, ~10 minutes)

```bash
python3 bin/skala_bridge.py init          # creates ~/.skala-workbuddy/config.json
```

1. In Telegram, chat **@BotFather** → `/newbot` → copy the token into `telegram.bot_token` in `~/.skala-workbuddy/config.json`. Keep it secret; if it ever leaks, `/revoke` in BotFather.
2. Send any message to your bot, then run `python3 bin/skala_bridge.py listen --once`. The output shows `Rejected (not in allowed_chats): <id>`; that number is your chat id.
3. Add yourself as owner, and foremen as field:
   ```json
   "security": {
     "allowed_chats": [
       {"id": "123456789", "name": "Budi (owner)", "role": "owner"},
       {"id": "987654321", "name": "Mandor Sukirman", "role": "field"}
     ],
     "max_messages_per_hour": 30
   }
   ```
   `owner` gets full answers and approves outgoing messages. `field` never receives amounts or margins. An empty list accepts nobody.
4. Run `python3 bin/skala_bridge.py listen` and keep it running.

### Keep the bridge running on macOS (launchd)

Create `~/Library/LaunchAgents/cloud.skalapro.bridge.plist` (replace `PLUGIN_PATH`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>cloud.skalapro.bridge</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string><string>PLUGIN_PATH/bin/skala_bridge.py</string><string>listen</string>
  </array>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/Users/YOU/.skala-workbuddy/bridge.log</string>
  <key>StandardErrorPath</key><string>/Users/YOU/.skala-workbuddy/bridge.err</string>
</dict></plist>
```

```bash
launchctl load ~/Library/LaunchAgents/cloud.skalapro.bridge.plist
```

Logs go to your private folder, not `/tmp`. Tokens are redacted from all output.

## 3. WhatsApp Cloud API (optional, advanced)

Needs a Meta business account, a verified number and a public HTTPS webhook. Fill `whatsapp.phone_number_id`, `access_token` (permanent), `verify_token` (random string you choose) and `app_secret` (enables signature checks), set `"channel": "whatsapp"`.

Your webhook receiver forwards each request body to the bridge, with the signature header:

```bash
python3 bin/skala_bridge.py ingest --signature "$X_HUB_SIGNATURE_256" < body.json
```

Unofficial WhatsApp libraries (scan-QR) risk your number being banned and are not supported.

## 4. Excel without Skala

```bash
python3 bin/buat_excel.py --nama-proyek "Renovasi Rumah Bpk. Andi" --nilai-kontrak 250000000 --output ~/Documents/renovasi-andi.xlsx
python3 bin/buat_excel.py --kosong --output ~/Documents/template.xlsx
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Not connected to Skala` | `login start` → approve → `login wait` |
| `Refusing to connect to '…'` | Use your `https://<company>.skalapro.cloud` address |
| HTTP 410 from Skala | Your server module is v1.0; upgrade to v1.1 |
| HTTP 401 expired / revoked | Log in again |
| HTTP 403 role | Ask your Skala admin for the permission named in the message |
| `Rejected (not in allowed_chats)` | Add the chat id to `security.allowed_chats` |
| `blocked: this is a FIELD chat` | Working as intended; remove amounts |
| `No owner approval found yet` | The owner must reply `SETUJU <code>`; then `listen --once` and `send-approved` |
| Excel error | `pip install openpyxl` |
