# Email Triage Agent — GO LIVE REPORT

Date: 2026-01-01

Source-of-truth runbook: `bookkeeping/docs/RUNBOOK_EMAIL_TRIAGE_CUTOVER.md`

## Summary

- **Enabled (live):** `zakops-email-triage.timer` (hourly, systemd)
- **Disabled:** legacy Email→DataRoom ingestion cron (`/home/zaks/scripts/email_ingestion && make ingest`)
- **Safety:** draft-only actions; no auto-send; no delete; no LangSmith tracing enabled
- **Idempotency:** state stored in `/home/zaks/DataRoom/.deal-registry/email_triage_state.db` (unique `message_id`)

## Phase 1 — Preflight Verification (NO scheduling changes)

### 1) Audit email runners (pre-cutover)

Command:
```bash
cd /home/zaks/bookkeeping && make audit-email-runners
```

Findings (legacy email ingestion runner):
- **File:** `/etc/cron.d/dataroom-automation`
- **Schedule:** `5 6-21 * * *` and `5 22,2 * * *`
- **Command:** `cd /home/zaks/scripts/email_ingestion && make ingest >> /home/zaks/logs/email_sync.log 2>&1`

### 2) Dry-run triage (no side effects)

Command:
```bash
cd /home/zaks/bookkeeping/scripts && sudo -u zaks python3 -m email_triage_agent.run_once --dry-run --max-per-run 5
```

Output:
```text
email_triage_run completed processed=5 skipped=0 failed=0 query='in:inbox -label:ZakOps/Processed newer_than:30d'
```

### 3) Real triage twice (idempotency)

Commands:
```bash
cd /home/zaks/bookkeeping && make triage-run
cd /home/zaks/bookkeeping && make triage-run
```

Outputs:
```text
email_triage_run completed processed=50 skipped=0 failed=0 query='in:inbox -label:ZakOps/Processed newer_than:30d'
email_triage_run completed processed=50 skipped=0 failed=0 query='in:inbox -label:ZakOps/Processed newer_than:30d'
```

Idempotency evidence (no message processed twice):
```bash
python3 - <<'PY'
import sqlite3
p='/home/zaks/DataRoom/.deal-registry/email_triage_state.db'
con=sqlite3.connect(p)
cur=con.cursor()
print("rows", cur.execute("select count(*) from email_triage_messages").fetchone()[0])
print("max_attempts", cur.execute("select max(attempts) from email_triage_messages").fetchone()[0])
PY
```

Observed:
```text
rows 101
max_attempts 1
```

### 4) Evidence collection

Label applied (example query):
```bash
cd /home/zaks/bookkeeping/scripts && sudo -u zaks python3 - <<'PY'
import asyncio
from email_triage_agent.mcp_stdio import McpStdioSession
from email_triage_agent.gmail_mcp import gmail_mcp_command
async def main():
  async with McpStdioSession(command=gmail_mcp_command()) as s:
    res = await s.call(name="search_emails", arguments={"query":"label:ZakOps/Processed newer_than:30d","maxResults":5})
    c = res.get("content")
    print((c[0].get("text") if isinstance(c, list) and c and isinstance(c[0], dict) else "").strip())
asyncio.run(main())
PY
```

Example output (shows `label:ZakOps/Processed` results):
```text
ID: 19b7a701c13a8319
Subject: Employee owned company
From: Dealmaker Wealth Society <no-reply@notification.circle.so>
Date: Thu, 01 Jan 2026 16:42:06 +0000
```

Quarantine folder created:
```bash
ls -la /home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/19b761e947e70c80
```

Output:
```text
Invoice-IR1O0NCZ-0026.pdf
Receipt-2848-2025-9805.pdf
```

Kinetic Action created (required command):
```bash
curl -s http://localhost:8090/api/actions?limit=10 | jq '.'
```

Example output (truncated):
```text
{
  "count": 10,
  "actions": [
    {
      "action_type": "EMAIL_TRIAGE.REVIEW_EMAIL",
      "created_by": "email_triage_agent",
      "status": "PENDING_APPROVAL",
      ...
    }
  ]
}
```

Safety check (no triage-created send actions):
```bash
curl -s 'http://localhost:8090/api/actions?limit=200' | jq '[.actions[] | select(.created_by=="email_triage_agent" and .action_type=="COMMUNICATION.SEND_EMAIL")] | length'
```

Output:
```text
0
```

## Phase 2 — Systemd Install (STILL NO CUTOVER)

Installed templates:
- `bookkeeping/configs/systemd/zakops-email-triage.service` → `/etc/systemd/system/zakops-email-triage.service`
- `bookkeeping/configs/systemd/zakops-email-triage.timer` → `/etc/systemd/system/zakops-email-triage.timer`

Commands:
```bash
sudo cp /home/zaks/bookkeeping/configs/systemd/zakops-email-triage.service /etc/systemd/system/
sudo cp /home/zaks/bookkeeping/configs/systemd/zakops-email-triage.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl status zakops-email-triage.timer zakops-email-triage.service --no-pager
```

Observed (pre-enable):
- Timer **loaded** and **disabled**

## Phase 3 — CUTOVER (MAKE LIVE)

### 1) Disable legacy ingestion (backup + minimal edit)

Backup created:
- `bookkeeping/configs/cron/dataroom-automation.pre-triage-cutover.20260101-104912.cron`

Change:
- Commented out only these email ingestion lines in `/etc/cron.d/dataroom-automation`:
  - `cd /home/zaks/scripts/email_ingestion && make ingest`

### 2) Enable triage timer

Command:
```bash
sudo systemctl enable --now zakops-email-triage.timer
```

### 3) Confirm exclusivity + logs

Commands:
```bash
cd /home/zaks/bookkeeping && make audit-email-runners
cd /home/zaks/bookkeeping && make triage-status
cd /home/zaks/bookkeeping && make triage-logs
```

Manual one-shot run under systemd (sanity):
```bash
sudo systemctl start zakops-email-triage.service
journalctl -u zakops-email-triage.service -n 20 --no-pager
```

Observed:
```text
email_triage_run completed processed=50 skipped=0 failed=0 query='in:inbox -label:ZakOps/Processed newer_than:30d'
```

## Phase 4 — Frontend Alignment Sanity

API proof (actions list contains triage-created actions with `action_type` field):
```bash
curl -s 'http://localhost:8090/api/actions?action_type=EMAIL_TRIAGE.REVIEW_EMAIL&limit=5' | jq '.actions[0] | {action_id, action_type, status, created_by}'
```

## Rollback (confirmed)

1) Disable timer:
```bash
sudo systemctl disable --now zakops-email-triage.timer
```

2) Restore legacy cron file from backup and re-enable the `email_ingestion && make ingest` lines:
- Restore from `bookkeeping/configs/cron/dataroom-automation.pre-triage-cutover.20260101-104912.cron` to `/etc/cron.d/dataroom-automation`

3) Verify:
```bash
cd /home/zaks/bookkeeping && make audit-email-runners
```

