# Localize LangSmith Agent Builder — Gmail Triage Agent (Plan)

Date: 2026-01-01

## Goal

Bring the LangSmith Agent Builder Gmail triage agent into the lab as a **local, scheduled, source-controlled** workflow that:
- polls Gmail hourly,
- labels emails immediately,
- quarantines attachments to `DataRoom/00-PIPELINE/_INBOX_QUARANTINE`,
- emits **approval-gated** Kinetic Actions (no auto-sending email),
- and ultimately replaces legacy Email→DataRoom ingestion runners (no duplication).

## Non‑negotiables (Safety)

- **Do not enable LangSmith tracing** right now (no remote run logging).
- **Never send email automatically.** Drafts only; “send” must only occur via approval-gated action execution.
- No deleting emails automatically.
- No secrets in repo, logs, traces, or cloud calls.
- After cutover, only one canonical email processor should be active.

## Current lab reality (inventory snapshot)

- Existing Email→DataRoom ingestion is cron-driven via `/etc/cron.d/dataroom-automation`:
  - `cd /home/zaks/scripts/email_ingestion && make ingest`
- Gmail MCP currently available locally as a Node MCP server:
  - `/root/mcp-servers/Gmail-MCP-Server/dist/index.js`
  - Tool list includes `search_emails`, `read_email`, label and attachment tools.
- Deal Lifecycle API (action engine / dashboard backend): `http://localhost:8090`

## Plan (phased)

### Phase A — Export Agent Builder configuration locally (source-of-truth)

1) Pull/export verbatim from LangSmith Agent Builder into:
   - `/home/zaks/scripts/email_triage_agent/agent_config/`
2) Mirror the expected structure:
   - `memories/agent.md`
   - `memories/tools.json`
   - `memories/brokers.md`
   - `memories/deals.md`
   - `memories/vendor_patterns.md`
   - `memories/subagents/**/agent.md`
   - `memories/subagents/**/tools.json`
3) Implement exporter script that authenticates via LangSmith API key **from local secret storage** (never committed).

Deliverable: agent config tree committed to repo (no secrets).

### Phase B — Tool-name mapping audit + alias layer

1) Parse `memories/tools.json` (+ subagent tool files) and enumerate “builder tool names”.
2) Compare to the actual Gmail MCP tool surface and implement a runtime alias layer:
   - builder tool name → MCP tool name
   - input param mapping (incl. defaults and type conversions)
3) Document mapping in:
   - `bookkeeping/docs/EMAIL_TRIAGE_TOOL_MAPPING.md`

Deliverable: mapping doc + executable alias adapter module.

### Phase C — Local runtime service (hourly polling; one-shot runner)

Implement a one-cycle runner (`python3 -m email_triage_agent.run_once`) that:

1) Queries Gmail for unprocessed messages:
   - default search: `in:inbox -label:ZakOps/Processed newer_than:30d`
   - cap per run: `MAX_PER_RUN=50` (newest first)
2) Enforces idempotency via SQLite state:
   - `/home/zaks/DataRoom/.deal-registry/email_triage_state.db`
   - `message_id` unique + hashes for body/attachments + processing metadata
3) For each message:
   - read content + thread info
   - classify + extract entities/links (LLM-assisted; local-first)
   - apply labels immediately:
     - `ZakOps/Processed` always
     - `ZakOps/Deal`, `ZakOps/Urgent`, `ZakOps/Needs-Review`, `ZakOps/Needs-Reply`,
       `ZakOps/Needs-Docs`, `ZakOps/Quarantine` as triggered
4) Attachment quarantine:
   - if safe: download into `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<message_id>/...`
   - if unsafe/unknown: do not download; label `ZakOps/Quarantine`; emit review action
5) Emit approval-gated actions through the Deal Lifecycle API (8090):
   - `REQUEST_DOCS`, `DRAFT_REPLY`, `INGEST_MATERIALS`, `FOLLOW_UP`, `CREATE_DEAL_REVIEW`
   - actions must be visible in the dashboard and require approval to execute “send”

Deliverable: a repeatable run that creates labels/quarantine/actions without duplicates.

### Phase D — Integrations (feature-flagged)

Add env flags (default `false`):
- `ENABLE_SLACK`
- `ENABLE_LINEAR`
- `ENABLE_SHEETS`
- `ENABLE_CALENDAR`

If disabled or not configured:
- log “integration disabled” and continue core triage (never fail the run).

Deliverable: integrations do not block core triage.

### Phase E — Deployment (systemd + Make targets)

Create:
- `zakops-email-triage.service` (runs one cycle and exits)
- `zakops-email-triage.timer` (hourly)

Add Make targets (bookkeeping Makefile):
- `make triage-run`
- `make triage-status`
- `make triage-logs`
- `make audit-email-runners`

Deliverable: operator can run/status/logs from a single entrypoint.

### Phase F — Decommission legacy email ingestion/sync (after validation)

1) Implement `make audit-email-runners` to report:
   - user+root crontabs
   - `/etc/cron.d/*` email jobs
   - systemd units/timers containing “email/ingest/gmail”
   - running processes matching known scripts
2) Write runbook for safe cutover + rollback:
   - `bookkeeping/docs/RUNBOOK_EMAIL_TRIAGE_CUTOVER.md`
3) Cutover steps:
   - disable legacy email ingestion cron (`email_ingestion make ingest`)
   - enable triage timer
   - verify no duplicates

Deliverable: one canonical processor active after cutover.

## Acceptance / Verification Checklist

- One run labels new messages with `ZakOps/Processed`.
- Re-run produces **no duplicates** (idempotent).
- Attachments land in quarantine directory (safe types only).
- Deal-related emails create Kinetic Actions visible in dashboard.
- No email is sent automatically (only draft/actions requiring approval).
- After cutover: legacy ingestion runners are disabled and triage timer is the only active pipeline.

