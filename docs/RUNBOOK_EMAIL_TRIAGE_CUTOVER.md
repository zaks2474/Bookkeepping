# RUNBOOK — Email Triage Agent Cutover (Gmail → Labels/Quarantine/Actions)

Date: 2026-01-01

## Purpose

Safely cut over from legacy Email→DataRoom ingestion runners to the new **ZakOps Email Triage Agent** (hourly), without duplicate processing.

## Non-negotiables

- No automatic sending of email.
- No automatic deletion of emails.
- No LangSmith tracing for this agent (enable later, explicitly).
- Keep secrets out of git, logs, and cloud calls.
- Only one canonical email processor active after cutover.

## Components

- Runner (one cycle): `python3 -m email_triage_agent.run_once`
- Repo code: `/home/zaks/bookkeeping/scripts/email_triage_agent/`
- Exported Agent Builder config (source-controlled): `/home/zaks/bookkeeping/configs/email_triage_agent/agent_config/`
- Quarantine root: `/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/`
- Idempotency DB: `/home/zaks/DataRoom/.deal-registry/email_triage_state.db`
- Kinetic Actions API: `http://localhost:8090/api/actions`
- Systemd templates (not installed by default):
  - `/home/zaks/bookkeeping/configs/systemd/zakops-email-triage.service`
  - `/home/zaks/bookkeeping/configs/systemd/zakops-email-triage.timer`

## Phase 1 — Audit the current environment (no changes)

Run:

- `cd /home/zaks/bookkeeping && make audit-email-runners`

Confirm:
- Any legacy ingestion runners (cron/systemd) that touch Gmail/IMAP/email ingestion.
- Current schedule for `/etc/cron.d/dataroom-automation` (legacy Email→DataRoom).

## Phase 2 — Validate the triage agent manually (no scheduling yet)

1) Dry run (no writes):
- `cd /home/zaks/bookkeeping/scripts && sudo -u zaks python3 -m email_triage_agent.run_once --dry-run --max-per-run 5`

2) Real run (labels + quarantine + actions):
- `cd /home/zaks/bookkeeping && make triage-run`

3) Re-run to confirm idempotency:
- `cd /home/zaks/bookkeeping && make triage-run`

Expected:
- First run processes up to `MAX_PER_RUN` and applies `ZakOps/Processed` + other labels.
- Second run processes `0` (or only newly-arrived messages).
- Attachments (deal-signal only; safe types only) land under:
  - `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<message_id>/...`
- Deal-signal emails produce Kinetic Actions:
  - `EMAIL_TRIAGE.REVIEW_EMAIL` (custom, review record)
  - `COMMUNICATION.DRAFT_EMAIL` (draft-only capability; no send)

## Phase 3 — Install the systemd timer (still no cutover)

Install (system units):

- `sudo cp /home/zaks/bookkeeping/configs/systemd/zakops-email-triage.service /etc/systemd/system/`
- `sudo cp /home/zaks/bookkeeping/configs/systemd/zakops-email-triage.timer /etc/systemd/system/`
- `sudo systemctl daemon-reload`

Do **not** enable yet if legacy processors are still active.

## Phase 4 — Cutover (disable legacy, enable triage)

1) Disable legacy email ingestion schedule(s)
- Use the audit output to identify the active entries.
- Recommended: comment out or remove only the email ingestion line(s) in `/etc/cron.d/dataroom-automation`.
- Keep a timestamped backup copy under `bookkeeping/configs/cron/` before editing.

2) Enable triage timer
- `sudo systemctl enable --now zakops-email-triage.timer`

3) Verify only one processor is running
- `cd /home/zaks/bookkeeping && make audit-email-runners`
- `cd /home/zaks/bookkeeping && make triage-status`

4) Monitor logs
- `cd /home/zaks/bookkeeping && make triage-logs`

## Rollback

If duplicates/errors occur:

- `sudo systemctl disable --now zakops-email-triage.timer`
- Re-enable legacy cron entries from the backup under `bookkeeping/configs/cron/`
- Run: `cd /home/zaks/bookkeeping && make audit-email-runners` to confirm state

---

## Gmail MCP — Health + Re-auth

### Health checks (preferred)

```bash
# Gmail MCP readiness (stdio spawn + tools/list)
curl -sf http://localhost:8090/api/gmail/health | jq

# If the API is down, run the triage-side smoke test (read-only)
cd /home/zaks/bookkeeping/scripts
export GMAIL_MCP_CREDENTIALS_PATH="/home/zaks/.gmail-mcp/credentials.json"
python3 -m email_triage_agent.smoke_gmail_mcp --list-tools
python3 -m email_triage_agent.smoke_gmail_mcp --query "in:inbox newer_than:1d" --max-results 1
```

Expected:
- `/api/gmail/health` returns `ok: true`
- smoke test returns `hit_count >= 0` and a list of `message_ids`

If you see many lingering `npm exec @gongrzhe/server-gmail-autoauth-mcp` processes, they are usually stray interactive MCP servers. They are not required for ZakOps (ZakOps spawns MCP servers per call). You can clean them up with:

```bash
sudo pkill -f "npm exec @gongrzhe/server-gmail-autoauth-mcp" || true
```

Then re-run the health check.

### Re-auth procedure (if health is failing)

This uses the upstream Gmail MCP server’s built-in auth command:
`npx -y @gongrzhe/server-gmail-autoauth-mcp auth`

```bash
# 1) Confirm the OAuth client keys exist (do NOT print contents)
ls -la /home/zaks/.gmail-mcp/gcp-oauth.keys.json

# 2) Backup current credentials (safe rollback)
cp -a /home/zaks/.gmail-mcp/credentials.json "/home/zaks/.gmail-mcp/credentials.json.bak.$(date +%Y%m%d_%H%M%S)"

# 3) Run interactive auth as user zaks (opens browser; follow Google flow)
sudo -u zaks bash -lc 'cd ~ && npx -y @gongrzhe/server-gmail-autoauth-mcp auth'

# 4) Verify credentials exist
ls -la /home/zaks/.gmail-mcp/credentials.json

# 5) Re-check health
curl -sf http://localhost:8090/api/gmail/health | jq
```

Notes:
- Credentials live at `~/.gmail-mcp/credentials.json` (do not commit/copy into repo).
- If the browser does not auto-launch, the auth command prints a URL; open it manually and complete the flow.
