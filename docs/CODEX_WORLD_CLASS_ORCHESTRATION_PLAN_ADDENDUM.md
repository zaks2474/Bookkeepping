# CODEX World-Class Orchestration Plan Addendum

This document builds on the previously approved **World-Class Orchestration Upgrade Plan** (`bookkeeping/docs/CODEX_WORLD_CLASS_ORCHESTRATION_UPGRADE_PLAN.md`) and has been hardened with concrete implementation details, file paths, acceptance criteria, and operational runbooks.

---

## Non-Negotiable Constraints

These MUST be preserved in all phases:

| Constraint | Enforcement |
|------------|-------------|
| **Local-first default** | vLLM + Qwen2.5-32B-Instruct-AWQ at `localhost:8000`. LangGraph triage hardblocks non-local URLs (SSRF protection). |
| **No auto-send email** | `COMMUNICATION.SEND_EMAIL` executor is NOT auto-executed by runner. Requires explicit human approval + separate invocation. |
| **No auto-delete email** | Gmail MCP delete operations require human confirmation. No batch delete without explicit user action. |
| **Approval gates** | All `requires_approval: true` actions start in `PENDING_APPROVAL` status. Transition to `READY` only via explicit `/approve` endpoint. |
| **Secrets out of git/logs** | `.env` files gitignored. Credentials via env vars only. Logs redact API keys via `[REDACTED]` filter. |
| **Idempotency** | All actions carry `idempotency_key`. Duplicate submissions return existing action. RFC `message_id` used for email dedup. |
| **Auditability** | Every action creates `AuditEvent` entries. Deal events persisted to `events.db`. Quarantine transitions logged. |

---

## Current State Snapshot (as of 2026-01)

### Core Components (EXIST)

| Component | Path | Status |
|-----------|------|--------|
| LangGraph Triage Runtime | `bookkeeping/scripts/email_triage_agent/langgraph_triage.py` | Implemented |
| Triage Logic | `bookkeeping/scripts/email_triage_agent/triage_logic.py` | Implemented |
| Agent Memories | `bookkeeping/configs/email_triage_agent/agent_config/memories/` | Configured |
| Quarantine Manager | `scripts/lifecycle_event_emitter.py` (class `QuarantineManager`) | Implemented |
| Quarantine REST API | `scripts/deal_lifecycle_api.py` | Implemented |
| Action Engine Models | `scripts/actions/engine/models.py` | Implemented |
| Action Store (SQLite) | `scripts/actions/engine/store.py` | Implemented |
| Action Runner (Kinetic v1.2) | `scripts/actions_runner.py` | Implemented |
| Executor Base + Registry | `scripts/actions/executors/base.py`, `registry.py` | Implemented |
| Capability Manifests (14) | `scripts/actions/capabilities/*.yaml` | Implemented |
| Deal Registry | `scripts/deal_registry.py` | Implemented |
| Deal Lifecycle Controller | `scripts/deal_lifecycle_controller.py` | Implemented |
| Temporal Worker | `scripts/temporal_worker/` | Implemented |
| n8n Webhook Integration | `scripts/integrations/n8n_webhook.py` | Implemented |
| Email Deduplicator | `scripts/lifecycle_event_emitter.py` (class `EmailDeduplicator`) | Implemented |
| Controller LLM | `Zaks-llm/src/agents/controller.py` | Implemented |
| vLLM Server | `Zaks-llm/docker-compose.yml` (service: vllm-qwen) | Operational |
| Gmail MCP | MCP tool via `@gongrzhe/server-gmail-autoauth-mcp` | Available |

### Data Stores

| Store | Path | Format |
|-------|------|--------|
| Action DB | `DataRoom/.deal-registry/ingest_state.db` | SQLite |
| Deal Registry | `DataRoom/.deal-registry/deal_registry.json` | JSON |
| Case Files | `DataRoom/.deal-registry/case_files/{deal_id}.json` | JSON |
| Quarantine Index | `DataRoom/.deal-registry/quarantine.json` | JSON |
| Email Dedup Ledger | `DataRoom/.deal-registry/dedupe/processed_emails.jsonl` | JSONL |
| Attachment Dedup | `DataRoom/.deal-registry/dedupe/processed_attachments.jsonl` | JSONL |
| Quarantine Files | `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/{message_id}/` | Directory |

### Makefile Targets (EXIST)

```bash
# bookkeeping/Makefile
make triage-run          # Run email triage once
make triage-test         # Run triage unit tests
make triage-status       # Check systemd timer status
make triage-logs         # Tail triage logs
make triage-eval         # Generate eval report
make temporal-up/down    # Start/stop Temporal stack
make temporal-worker     # Run Temporal worker
make temporal-status     # Show schedule status
make n8n-up/down/logs    # Manage n8n

# scripts/Makefile
make actions-runner      # Run action executor
make actions-status      # Show action queue
make actions-retry-stuck # Retry stuck actions
make api-status          # Check API health
```

### Components TO BE BUILT

| Component | Target Path | Phase | Status |
|-----------|-------------|-------|--------|
| Baseline Check Script | `/home/zaks/scripts/codex_baseline_check.py` | P0 | ✅ |
| Baseline Report | `bookkeeping/docs/CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md` | P0 | ✅ |
| Temporal Cutover Runbook | `bookkeeping/docs/RUNBOOK_TEMPORAL_CUTOVER.md` | P1 | ✅ |
| Triage Feedback Dataset | `DataRoom/.deal-registry/triage_feedback.jsonl` | P2 | ✅ |
| Triage Evaluation Script | `bookkeeping/scripts/email_triage_agent/eval_triage.py` | P2 | ✅ (baseline) |
| Gmail MCP Health Endpoint | `scripts/deal_lifecycle_api.py` (new route) | P3 | ⏳ |
| n8n Workflow Examples | `bookkeeping/docs/n8n_workflows/` | P4 | ✅ (starter set) |
| Deletion Research Doc | `bookkeeping/docs/RESEARCH_DELETION_CONTROLS.md` | P5 | ✅ |

---

## Target Behavior

### Email Triage Flow

```
Gmail Inbox
    │
    ▼
[Gmail MCP: search_emails] ──────────────────────────────────────────┐
    │                                                                 │
    ▼                                                                 │
[LangGraph Triage]                                                    │
    │  - Load agent memories                                          │
    │  - Call local vLLM (Qwen2.5-32B)                               │
    │  - Parse JSON response                                          │
    │  - Classify: deal_email | spam | personal | unknown            │
    │                                                                 │
    ├─── confidence >= 0.70 ──► [Auto-match to Deal]                 │
    │                              │                                  │
    │                              ▼                                  │
    │                           [Create Action: DEAL.APPEND_EMAIL]    │
    │                              │                                  │
    │                              ▼                                  │
    │                           [Executor: append materials]          │
    │                                                                 │
    └─── confidence < 0.70 ──► [Quarantine]                          │
                                   │                                  │
                                   ▼                                  │
                              [Create Action: EMAIL_TRIAGE.REVIEW_EMAIL]
                                   │  status = PENDING_APPROVAL       │
                                   │                                  │
                                   ▼                                  │
                              [Operator Reviews in UI]                │
                                   │                                  │
                    ┌──────────────┼──────────────┐                   │
                    │              │              │                   │
                    ▼              ▼              ▼                   │
               [Approve]      [Reject]      [Link to Existing]        │
                    │              │              │                   │
                    ▼              ▼              ▼                   │
            [Create Deal]   [Discard +    [Append to Deal]            │
                            Log Reason]                               │
                                                                      │
                    │                                                 │
                    └─────────────────────────────────────────────────┘
                                   (loop hourly via Temporal)
```

### Quarantine Decision Point

1. **Input**: Email with triage result showing `confidence < CONFIDENCE_THRESHOLD` (default: 0.70)
2. **Storage**:
   - Email body → `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/{message_id}/email_body.txt`
   - Attachments → `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/{message_id}/{filename}`
   - Metadata → `DataRoom/.deal-registry/quarantine.json`
3. **UI Display**: `/api/actions/quarantine` returns pending items with candidates and confidence
4. **Resolution Options**:
   - `link_to_deal` → Append materials to existing deal
   - `create_new_deal` → Create workspace in `DataRoom/00-PIPELINE/Inbound/{deal_id}/`
   - `discard` → Mark resolved, log reason, no deal created

### Deal Creation

1. **Trigger**: `EMAIL_TRIAGE.REVIEW_EMAIL` action approved with `resolution: create_new_deal`
2. **Steps**:
   - Generate `deal_id` (format: `DEAL-{YYYYMMDD}-{hash8}`)
   - Create directory structure in `DataRoom/00-PIPELINE/Inbound/{deal_id}/`
   - Copy email materials to `07-Correspondence/`
   - Create case file in `DataRoom/.deal-registry/case_files/{deal_id}.json`
   - Register in `deal_registry.json`
3. **Output**: Action `outputs.deal_id`, `outputs.workspace_path`

### Progressive Materials Ingestion

1. Each new email matching a deal triggers `DEAL.APPEND_EMAIL_MATERIALS`
2. Materials classified and placed in appropriate subdirectory (01-NDA through 09-Closing)
3. Deduplication via `EmailDeduplicator` prevents duplicate ingestion
4. Thread grouping via `thread_id` for conversation continuity

### Follow-on Email Threading

1. Replies detected via `In-Reply-To` / `References` headers
2. Thread ID extracted and matched to existing deal correspondence
3. New messages appended to same deal, maintaining conversation context
4. UI shows threaded view in deal correspondence section

---

## Architecture

### Component Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATION LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Temporal Server (docker)         │  Schedules + Workflow Execution         │
│  temporal_worker/worker.py        │  Polls task queue, runs workflows       │
│  temporal_worker/schedules.py     │  Hourly: EmailTriageOnce, Controller    │
│  temporal_worker/workflows.py     │  Workflow definitions                   │
│  temporal_worker/activities.py    │  Actual work (triage, controller)       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TRIAGE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  langgraph_triage.py              │  StateGraph: prepare→call_llm→parse     │
│  triage_logic.py                  │  Classification + confidence scoring    │
│  agent_config/memories/           │  Agent behavior + domain knowledge      │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ACTION ENGINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  actions/engine/models.py         │  ActionPayload, ActionStatus, etc.      │
│  actions/engine/store.py          │  SQLite persistence, state transitions  │
│  actions_runner.py                │  Kinetic Engine: lease, execute, retry  │
│  actions/executors/*.py           │  Domain-specific executors (14 total)   │
│  actions/capabilities/*.yaml      │  Capability manifests                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  deal_registry.py                 │  Deal CRUD, email-to-deal matching      │
│  lifecycle_event_emitter.py       │  QuarantineManager, EmailDeduplicator   │
│  deal_events.py                   │  Event sourcing, audit trail            │
│  DataRoom/.deal-registry/         │  SQLite + JSON persistence              │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  deal_lifecycle_api.py            │  FastAPI: /api/deals, /api/quarantine   │
│                                   │  /api/actions, health endpoints         │
│  Port: 8090 (systemd: zakops-api-8090)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL INTEGRATIONS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  Gmail MCP                        │  Email fetch, labels, drafts (NO send)  │
│  n8n Webhook                      │  Event emission for workflows           │
│  vLLM (localhost:8000)            │  Local LLM inference                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Event Flow (Temporal-Orchestrated)

```
[Temporal Schedule: zakops-email-triage-hourly (hourly)]
         │
         ▼
[EmailTriageOnceWorkflow]
         │
         ├──► Activity: fetch_new_emails() ──► Gmail MCP search
         │
         ├──► Activity: triage_email(msg) ──► LangGraph ──► LlmTriageResult
         │              │
         │              ├── high confidence ──► create DEAL.APPEND action
         │              └── low confidence  ──► create EMAIL_TRIAGE.REVIEW action
         │
         └──► Activity: persist_results() ──► ActionStore.create_action()

[Temporal Schedule: controller_schedule (hourly)]
         │
         ▼
[DealLifecycleControllerOnceWorkflow]
         │
         ├──► Activity: scan_active_deals()
         │
         └──► Activity: evaluate_next_actions() ──► Controller LLM
                        │
                        └──► enqueue follow-on actions

[ActionRunner (continuous)]
         │
         ├──► acquire_runner_lease()
         │
         ├──► get_next_due_action()
         │
         ├──► claim_action_lock()
         │
         ├──► executor.execute()
         │              │
         │              └──► outputs, artifacts, audit events
         │
         └──► mark_completed() / mark_retry()
```

---

## Data Contracts

### LlmTriageResult (from langgraph_triage.py)

```json
{
  "classification": "deal_email | spam | personal | unknown",
  "confidence": 0.85,
  "deal_match": {
    "deal_id": "DEAL-20250101-abc12345",
    "company_name": "Acme Corp",
    "match_reason": "subject_keyword | sender_domain | broker_match"
  },
  "extracted_fields": {
    "company_name": "Acme Corp",
    "broker_name": "John Smith",
    "broker_email": "john@broker.com",
    "deal_type": "acquisition | divestiture | financing",
    "keywords": ["manufacturing", "midwest", "5M EBITDA"]
  },
  "suggested_action": "append_to_deal | quarantine | discard",
  "reasoning": "string explaining classification"
}
```

### QuarantineItem (from lifecycle_event_emitter.py)

```json
{
  "quarantine_id": "QRN-20250109T120000-abc12345",
  "email_subject": "RE: Potential Acquisition Target",
  "email_from": "broker@example.com",
  "email_date": "2025-01-09T12:00:00Z",
  "message_id": "<abc123@mail.example.com>",
  "thread_id": "thread_abc123",
  "reason": "low_confidence_match | ambiguous_sender | missing_context",
  "candidates": [
    {
      "deal_id": "DEAL-20250101-abc12345",
      "company_name": "Acme Corp",
      "score": 0.65
    }
  ],
  "confidence": 0.65,
  "attachments": [
    {"filename": "CIM.pdf", "size_bytes": 1048576, "path": "..."}
  ],
  "manifest_path": "DataRoom/00-PIPELINE/_INBOX_QUARANTINE/{message_id}/",
  "created_at": "2025-01-09T12:00:00Z",
  "status": "pending | resolved",
  "resolved_at": null,
  "resolution": null
}
```

### ActionPayload (from actions/engine/models.py)

```json
{
  "action_id": "ACT-20250109T120000-abc12345",
  "deal_id": "DEAL-20250101-abc12345",
  "capability_id": "email_triage.review_email.v1",
  "type": "EMAIL_TRIAGE.REVIEW_EMAIL",
  "status": "PENDING_APPROVAL | READY | PROCESSING | COMPLETED | FAILED | CANCELLED",
  "risk_level": "low | medium | high",
  "requires_human_review": true,
  "idempotency_key": "triage-{message_id}",
  "inputs": {
    "message_id": "<abc123@mail.example.com>",
    "quarantine_dir": "DataRoom/00-PIPELINE/_INBOX_QUARANTINE/{message_id}/"
  },
  "outputs": {
    "deal_id": "DEAL-20250101-abc12345",
    "workspace_path": "DataRoom/00-PIPELINE/Inbound/DEAL-20250101-abc12345/",
    "next_actions": []
  },
  "error": null,
  "retry_count": 0,
  "max_retries": 3,
  "created_at": "2025-01-09T12:00:00Z",
  "updated_at": "2025-01-09T12:00:00Z",
  "audit_trail": [
    {"event": "created", "timestamp": "...", "actor": "system"},
    {"event": "approved", "timestamp": "...", "actor": "user@example.com"}
  ]
}
```

### Null Handling Rules

| Field | Null Allowed | Default | UI Handling |
|-------|--------------|---------|-------------|
| `deal_match.deal_id` | Yes | `null` | Show "No match found" |
| `candidates` | No | `[]` | Show "No candidates" |
| `attachments` | No | `[]` | Hide attachment section |
| `confidence` | No | Required | - |
| `resolution` | Yes (pending) | `null` | Show pending status |
| `outputs` | Yes (not completed) | `null` | Show "In progress" |
| `error` | Yes | `null` | Hide error section if null |

---

## Idempotency & Deduplication Rules

### Email Deduplication

1. **Primary Key**: RFC `Message-ID` header
2. **Fallback**: SHA256 hash of `(from, to, subject, date, body[:1000])`
3. **Store**: `DataRoom/.deal-registry/dedupe/processed_emails.jsonl`
4. **Behavior**:
   - If `message_id` exists in ledger → skip processing, return existing result
   - Log skip event with `reason: duplicate_message_id`

### Action Idempotency

1. **Key Generation**: `{action_type}-{primary_input_hash}`
   - For `EMAIL_TRIAGE.REVIEW_EMAIL`: `triage-{message_id}`
   - For `DEAL.APPEND_EMAIL_MATERIALS`: `append-{deal_id}-{message_id}`
2. **Store**: `ingest_state.db` table `actions`, column `idempotency_key` (UNIQUE)
3. **Behavior**:
   - On duplicate key → return existing action_id, do not create new
   - Log with `reason: idempotent_duplicate`

### Reprocessing Rules

| Scenario | Behavior |
|----------|----------|
| Action COMPLETED | No reprocess. Return existing result. |
| Action FAILED (retries exhausted) | Allow manual requeue via API. New action_id. |
| Action CANCELLED | Allow resubmit. New action_id, new idempotency_key suffix. |
| Quarantine RESOLVED | No reprocess. Log attempt. |
| Email re-received (same message_id) | Skip. Dedup catches at ingestion. |

### Thread Handling

1. **Thread ID**: Gmail thread_id used for grouping
2. **New message in existing thread**:
   - Check thread_id → deal_id mapping in registry
   - If mapped → append to same deal (no quarantine)
   - If unmapped → triage as new email

---

## Observability & Debugging

### Log Locations

| Component | Log Path | How to View |
|-----------|----------|-------------|
| Triage Agent | Temporal worker logs | `tail -f /home/zaks/logs/temporal_worker/worker_stdout.log` |
| Action Runner | systemd journal | `journalctl -u kinetic-actions-runner -f` |
| API Server | systemd journal | `journalctl -u zakops-api-8090 -f` |
| Temporal Worker | (recommended: systemd) | `tail -f /home/zaks/logs/temporal_worker/worker_stdout.log` |
| vLLM Server | docker logs | `docker logs vllm-qwen -f` |
| n8n | docker logs | `docker logs n8n -f` |
| Application logs | `Zaks-llm/logs/` | `tail -f Zaks-llm/logs/*.log` |

### Structured Logging Fields

All logs should include (TO BE IMPLEMENTED in P0):

```json
{
  "timestamp": "2025-01-09T12:00:00Z",
  "level": "INFO | WARN | ERROR",
  "component": "triage | runner | api | temporal",
  "correlation_id": "req-abc12345",
  "action_id": "ACT-...",
  "deal_id": "DEAL-...",
  "message_id": "<abc@example.com>",
  "message": "Human readable message",
  "extra": {}
}
```

### Correlation IDs

1. **Request ID**: Generated at API entry, passed through all layers
2. **Action ID**: Links all events for a single action execution
3. **Message ID**: Links all processing for a single email

### Key Metrics (TO BE IMPLEMENTED)

| Metric | Description | Source |
|--------|-------------|--------|
| `triage_emails_processed_total` | Counter of emails triaged | Triage activity |
| `triage_confidence_histogram` | Distribution of confidence scores | Triage activity |
| `quarantine_items_pending` | Gauge of pending quarantine items | QuarantineManager |
| `actions_by_status` | Gauge per status | ActionStore.action_metrics() |
| `action_duration_seconds` | Histogram of execution time | Runner |
| `runner_lease_healthy` | Boolean gauge | Runner |
| `gmail_mcp_healthy` | Boolean gauge | Health endpoint |

### Health Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `GET /api/version` | Overall API health/config | JSON with `server_pid`, `server_start_time`, `config` |
| `GET /api/quarantine/health` | Quarantine subsystem | `{"pending_count": N, "oldest_age_hours": M}` |
| `GET /api/actions/runner-status` | Runner lease + queue status | JSON with `lease_ok`, `queue_counts`, `stuck_processing` |
| `GET /api/temporal/status` (TO BUILD) | Temporal connectivity | `{"connected": true, "schedules_active": 2}` |
| `GET /api/gmail/health` (TO BUILD) | Gmail MCP readiness | JSON from `scripts/tools/mcp_health.check_gmail_mcp_health()` |

### Common Failure Signatures

| Symptom | Likely Cause | Debug Steps |
|---------|--------------|-------------|
| No emails processed | Gmail MCP auth expired | `curl -sf http://localhost:8090/api/gmail/health` (once implemented), re-auth if needed |
| All emails quarantined | vLLM down or slow | Check `docker ps`, `curl localhost:8000/health` |
| Actions stuck PROCESSING | Runner crashed mid-execution | Check `make actions-status`, run `make actions-retry-stuck` |
| Confidence always 0.0 | Agent memories not loaded | Check `bookkeeping/configs/email_triage_agent/` mtime |
| Duplicate deals created | Dedup ledger corrupted | Check `processed_emails.jsonl` integrity |

### Debug Commands

```bash
# Check overall system status
make -C bookkeeping health

# Check action queue
make -C scripts actions-status

# List stuck actions
sqlite3 DataRoom/.deal-registry/ingest_state.db \
  "SELECT action_id, type, status, updated_at FROM actions WHERE status='PROCESSING' AND updated_at < datetime('now', '-5 minutes')"

# Check quarantine backlog
curl -s http://localhost:8090/api/actions/quarantine | jq '.count'

# Verify vLLM is responding
curl -s http://localhost:8000/v1/models | jq '.data[0].id'

# Test Gmail MCP connectivity
# (via Claude Code or MCP client)

# Check Temporal schedules
temporal schedule list --namespace default

# Force triage run
make -C bookkeeping triage-run
```

---

## Operational Runbook

### Daily Operations

```bash
# Morning check (run as cron or manually)
make -C bookkeeping health
make -C scripts actions-status
curl -s http://localhost:8090/api/quarantine/health | jq

# If quarantine backlog > 20, alert operator
```

### Restart Services

```bash
# Restart API
sudo systemctl restart zakops-api-8090

# Restart Temporal worker
sudo systemctl restart zakops-temporal-worker

# Restart vLLM (careful: model reload takes ~2 min)
cd Zaks-llm && docker compose restart vllm-qwen

# Full stack restart (nuclear option)
cd Zaks-llm && docker compose down && docker compose up -d
sudo systemctl restart zakops-api-8090 zakops-temporal-worker
```

### Verify Health

```bash
# API health
curl -s http://localhost:8090/api/version | jq -e '.server_pid'

# vLLM health
curl -s http://localhost:8000/health

# Temporal health
temporal operator cluster health

# Action runner lease
sqlite3 DataRoom/.deal-registry/ingest_state.db \
  "SELECT * FROM action_runner_leases ORDER BY acquired_at DESC LIMIT 1"
```

### Run E2E Smoke Test

```bash
# Triage E2E (TO BE CREATED as scripts/e2e_smoke_test.py)
python scripts/e2e_smoke_test.py --component triage
python scripts/e2e_smoke_test.py --component actions
python scripts/e2e_smoke_test.py --component full

# Manual smoke test
# 1. Send test email to monitored inbox
# 2. Wait for triage cycle (or run `make triage-run`)
# 3. Check quarantine: curl http://localhost:8090/api/actions/quarantine
# 4. Approve item via UI or API
# 5. Verify deal created in DataRoom/00-PIPELINE/Inbound/
```

### Recover from Failures

```bash
# Stuck actions (processing > 5 min)
make -C scripts actions-retry-stuck

# Corrupted quarantine.json
cp DataRoom/.deal-registry/quarantine.json DataRoom/.deal-registry/quarantine.json.bak
python -c "import json; q=json.load(open('DataRoom/.deal-registry/quarantine.json')); print(len(q.get('items',[])))"
# If fails, restore from backup or reinitialize

# Lost runner lease (another process holding)
# Check what's holding it:
sqlite3 DataRoom/.deal-registry/ingest_state.db "SELECT * FROM action_runner_leases"
# Force release (if stale):
sqlite3 DataRoom/.deal-registry/ingest_state.db "DELETE FROM action_runner_leases WHERE lease_id='...'"

# Temporal schedule not firing
temporal schedule describe --schedule-id zakops-email-triage-hourly
temporal schedule trigger --schedule-id zakops-email-triage-hourly  # Force run
```

---

## Rollout & Rollback Plan

### Feature Flags

| Flag | Env Var | Values | Default |
|------|---------|--------|---------|
| Triage Backend | `EMAIL_TRIAGE_LLM_BACKEND` | `llm_triage`, `langgraph` | `llm_triage` |
| Triage Mode | `EMAIL_TRIAGE_LLM_MODE` | `off`, `assist`, `full` | `assist` |
| n8n Webhooks | `N8N_WEBHOOKS_ENABLED` | `true`, `false` | `false` |
| Auto-approve Low Risk | `AUTO_APPROVE_LOW_RISK` | `true`, `false` | `false` |

### Staged Rollout

**Phase 0-1: Shadow Mode**
```bash
EMAIL_TRIAGE_LLM_BACKEND=llm_triage
EMAIL_TRIAGE_LLM_MODE=assist
# Temporal is controlled operationally (pause/unpause schedules + enable/disable systemd timers)
```

**Phase 2: Temporal Cutover**
```bash
# 1. Pause systemd timers
sudo systemctl stop zakops-email-triage.timer
sudo systemctl stop zakops-deal-lifecycle-controller.timer

# 2. Enable Temporal
make -C bookkeeping temporal-schedules-enable

# 3. Monitor for 24h
# If issues, rollback (see below)
```

**Phase 3: Full LangGraph**
```bash
EMAIL_TRIAGE_LLM_BACKEND=langgraph
EMAIL_TRIAGE_LLM_MODE=full
# Monitor false positive rate via triage_feedback.jsonl
```

### Rollback Procedures

**Rollback Temporal → systemd**
```bash
# 1. Pause Temporal schedules
make -C bookkeeping temporal-schedules-disable

# 2. Re-enable systemd timers
sudo systemctl start zakops-email-triage.timer
sudo systemctl start zakops-deal-lifecycle-controller.timer

# (No env toggle; Temporal is operationally paused/unpaused)
```

**Rollback LangGraph full → assist**
```bash
EMAIL_TRIAGE_LLM_BACKEND=llm_triage
EMAIL_TRIAGE_LLM_MODE=assist
# Restart the Temporal worker so child subprocesses inherit the env.
```

**Emergency: Disable All Automation**
```bash
# Stop all triage/controller
sudo systemctl stop zakops-email-triage.timer zakops-deal-lifecycle-controller.timer
make -C bookkeeping temporal-schedules-disable

# Actions still in queue won't auto-process
# Manual processing only via API
```

---

## Revised Implementation Phases

### Phase 0: Verification + Baseline (P0)

**Objective**: Establish baseline, verify existing functionality, structured logging.

**Tasks**:
- [x] Create `/home/zaks/scripts/codex_baseline_check.py` (service status, port checks, DB integrity)
- [x] Run baseline and generate `bookkeeping/docs/CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md`
- [ ] Add structured logging with correlation IDs to triage + runner
- [x] Update `CHANGES.md` with this addendum

**Acceptance Criteria**:
```bash
# Baseline script runs without error
python3 /home/zaks/scripts/codex_baseline_check.py
# Output: CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md exists and shows all services UP

# Triage tests pass
make -C bookkeeping triage-test
# Exit code: 0

# API health check
curl -sf http://localhost:8090/api/version | jq -e '.server_pid'
# Output: (number)

# vLLM responds
curl -sf http://localhost:8000/v1/models | jq -e '.data[0].id'
# Output: "Qwen/Qwen2.5-32B-Instruct-AWQ"
```

**Verification Commands**:
```bash
make -C bookkeeping health
make -C bookkeeping triage-test
python3 /home/zaks/scripts/codex_baseline_check.py --output bookkeeping/docs/CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md
```

---

### Phase 1: Temporal Orchestration (P1)

**Objective**: Replace systemd timers with Temporal for reliable scheduling and observability.

**Tasks**:
- [x] Verify Temporal server running (`make temporal-up`)
- [x] Configure `temporal_worker/config.py` with env vars
- [x] Test workflows locally: `EmailTriageOnceWorkflow`, `DealLifecycleControllerOnceWorkflow`
- [x] Create `RUNBOOK_TEMPORAL_CUTOVER.md`
- [x] Cutover: pause systemd, enable Temporal schedules
- [x] Monitor 24h, document any issues

**Acceptance Criteria**:
```bash
# Temporal schedules exist and are unpaused
make -C bookkeeping temporal-status

# No conflicting cron/timer sources remain
make -C bookkeeping orchestration-audit

# systemd timers disabled
systemctl is-active zakops-email-triage.timer
# Output: inactive
systemctl is-active zakops-deal-lifecycle-controller.timer
# Output: inactive
```

**Verification Commands**:
```bash
make -C bookkeeping orchestration-deps
make -C bookkeeping temporal-up
make -C bookkeeping temporal-run-once
make -C bookkeeping temporal-schedules
sudo systemctl disable --now zakops-email-triage.timer zakops-deal-lifecycle-controller.timer
make -C bookkeeping temporal-schedules-enable
make -C bookkeeping orchestration-audit
make -C bookkeeping temporal-status
```

---

### Phase 2: LangGraph Agentic Triage (P2)

**Objective**: Full LangGraph triage with feedback loop and evaluation.

**Tasks**:
- [ ] Set `EMAIL_TRIAGE_LLM_BACKEND=langgraph` and `EMAIL_TRIAGE_LLM_MODE=full`
- [x] Implement `triage_summary.json` output alongside existing flow
- [x] Create `triage_feedback.jsonl` for operator corrections
- [x] Ensure `DataRoom/.deal-registry/triage_outputs/` exists and is populated (audit trail)
- [x] Extend `bookkeeping/scripts/email_triage_agent/eval_triage.py` to compute precision/recall/F1 from `triage_feedback.jsonl`
- [ ] Run evaluation weekly, adjust agent memories if FP > 10%

**Acceptance Criteria**:
```bash
# Triage produces structured output
find DataRoom/00-PIPELINE/_INBOX_QUARANTINE -maxdepth 2 -name triage_summary.json | head
# Output: at least 1 path

# Feedback file exists and is appendable
echo '{"test": true}' >> DataRoom/.deal-registry/triage_feedback.jsonl
tail -1 DataRoom/.deal-registry/triage_feedback.jsonl | jq -e '.test'
# Output: true

# Eval script runs
make -C bookkeeping triage-eval
# Output: bookkeeping/docs/EMAIL_TRIAGE_EVAL_REPORT.md

# False positive rate < 15% (target)
cat bookkeeping/docs/EMAIL_TRIAGE_EVAL_REPORT.md | rg -n "false_positive_rate"
# Output: value < 0.15
```

**Verification Commands**:
```bash
make -C bookkeeping triage-eval
cd /home/zaks/bookkeeping/scripts && python3 -m email_triage_agent.eval_triage
```

---

### Phase 3: Gmail MCP + Health (P3)

**Objective**: Unified Gmail MCP across all components with health monitoring.

**Tasks**:
- [x] Standardize Gmail MCP command in all manifests/configs
- [x] Add `/api/gmail/health` endpoint to `deal_lifecycle_api.py`
- [x] Add Gmail MCP smoke test to baseline script
- [x] Document auth refresh procedure in runbook

**Acceptance Criteria**:
```bash
# Gmail health endpoint exists and responds
curl -sf http://localhost:8090/api/gmail/health | jq -e '.ok'
# Output: true

# Smoke test passes
python3 /home/zaks/scripts/codex_baseline_check.py --component gmail
# Exit code: 0
```

**Verification Commands**:
```bash
curl http://localhost:8090/api/gmail/health
make -C bookkeeping preflight  # Should include Gmail check
```

---

### Phase 4: n8n Peripheral Workflows (P4)

**Objective**: Optional n8n integration for advanced workflow automation.

**Tasks**:
- [x] Add n8n compose stack (optional; `make -C bookkeeping n8n-up`)
- [x] Create example workflows in `bookkeeping/docs/n8n_workflows/`
- [x] Document webhook URLs and event payloads (`bookkeeping/docs/N8N_WEBHOOKS.md`)
- [x] Add `N8N_WEBHOOKS_ENABLED` flag (default false)

**Acceptance Criteria**:
```bash
# n8n container running (when enabled)
docker ps | grep n8n
# Output: n8n container UP

# Webhook endpoint responds
curl -sf http://localhost:5678/webhook/test
# Output: 200 OK

# Example workflows importable
ls bookkeeping/docs/n8n_workflows/*.json
# At least 2 files
```

**Verification Commands**:
```bash
make -C bookkeeping n8n-up
make -C bookkeeping n8n-logs
```

---

### Phase 5: Deletion Controls (P5)

**Objective**: Safe deletion semantics for deals and quarantine items.

**Tasks**:
- [x] Write `RESEARCH_DELETION_CONTROLS.md` analyzing data dependencies
- [x] Decide: soft delete vs hard delete
- [x] Implement soft delete with `deleted_at` timestamp
- [x] Add `/api/deals/{deal_id}/archive`, `/api/deals/{deal_id}/restore`, and `/api/deals/bulk-archive`
- [x] Add `/api/quarantine/{quarantine_id}/delete` and `/api/quarantine/bulk-delete`
- [x] NO batch delete without explicit multi-select confirmation (bulk endpoint requires an explicit list)

**Acceptance Criteria**:
```bash
# Research doc exists
cat bookkeeping/docs/RESEARCH_DELETION_CONTROLS.md | head -20
# Contains "Recommendation:" section

# Archive endpoint exists
curl -sf -X POST http://localhost:8090/api/deals/TEST-DEAL/archive
# Output: {"archived": true, "deleted_at": "..."}

# Archived deals hidden from default list
curl -sf http://localhost:8090/api/deals | jq '.deals[] | select(.deleted_at != null)'
# Output: empty

# Can restore archived
curl -sf -X POST http://localhost:8090/api/deals/TEST-DEAL/restore
# Output: {"restored": true}
```

**Verification Commands**:
```bash
# Manual test only - no automated deletion tests to avoid accidents
```

---

### Phase 6: Observability + Recovery (P6)

**Objective**: Production-grade observability and self-healing.

**Tasks**:
- [x] Add Prometheus metrics endpoint `/metrics`
- [x] Create Grafana dashboard JSON (`bookkeeping/docs/grafana/zakops_dealos_overview.json`)
- [x] Implement watchdog for actions stuck in `PROCESSING` (runner TTL + failure audit)
- [x] Add alerting rules (`bookkeeping/docs/ALERTING_RULES.md`)
- [x] Document `PlanSpec` contract (`bookkeeping/docs/PLANSPEC_CONTRACT.md`)

**Acceptance Criteria**:
```bash
# Metrics endpoint exists
curl -sf http://localhost:8090/metrics | grep actions_by_status
# Output: Prometheus metrics

# Auto-unstick works
# (simulate stuck action, wait >10 min, verify it becomes FAILED with code=processing_timeout; then requeue via /api/actions/{id}/requeue)

# Alert rules documented
cat bookkeeping/docs/ALERTING_RULES.md | grep "quarantine_backlog"
# Contains alert definition
```

**Verification Commands**:
```bash
curl http://localhost:8090/metrics
make -C scripts actions-status
```

---

## Defaults / Decisions (no operator input required)

1. **Temporal namespace**: use `default` (simple local lab).
2. **Retention policy**: target 90 days for completed actions (implement as a safe, operator-triggered prune job in P6).
3. **Quarantine timeout**: no auto-escalation; show age + optional n8n reminder only.
4. **Multi-tenant**: single-operator assumption for v1 (no new auth system in this phase).
5. **Backup strategy**: rely on existing DataRoom backups + ensure `ingest_state.db` (WAL) is included; add explicit runbook steps in P6.
6. **Gmail quota**: keep conservative batch sizes + backoff; add observability counters in P6.
7. **Attachment size limit**: keep conservative extraction caps (skip huge files with an operator note) to prevent stalls.
8. **LLM fallback**: if vLLM is down, degrade to deterministic + quarantine (no cloud fallback).

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **LLM drift** | False classifications increase over time | Medium | Weekly eval script, retrain on feedback |
| **False positives** | Good deals discarded | Medium | Default to quarantine (safe), operator review |
| **False negatives** | Spam/irrelevant creates deals | Low | Post-triage validation, easy archive |
| **Rate limits** | Gmail API quota exceeded | Low | Batch fetching, exponential backoff |
| **Missing attachments** | CIM/financials not captured | Medium | Retry logic, manual upload fallback |
| **Auth-required links** | Can't fetch linked documents | High | Flag for operator, n8n workflow option |
| **Stale permissions** | Gmail MCP auth expires | Medium | Health check, re-auth runbook |
| **Runner crash** | Actions stuck indefinitely | Low | Lease timeout, auto-unstick |
| **Data loss** | SQLite corruption | Low | Daily backup, WAL mode |
| **Secret leak** | API keys in logs | Medium | Log redaction filter, secret scanning |
| **vLLM OOM** | Model crashes on large context | Medium | Context truncation, memory limits |
| **Temporal unavailable** | No scheduled runs | Medium | Fallback to manual `make triage-run` |

---

## Appendix: Quick Reference Commands

```bash
# System status
make -C bookkeeping health
make -C scripts actions-status

# Triage
make -C bookkeeping triage-run      # Manual run
make -C bookkeeping triage-test     # Unit tests
make -C bookkeeping triage-logs     # Tail logs

# Temporal
make -C bookkeeping temporal-up     # Start server
make -C bookkeeping temporal-status # Check schedules
temporal schedule trigger --schedule-id zakops-email-triage-hourly  # Force run

# Actions
make -C scripts actions-runner      # Start runner
make -C scripts actions-retry-stuck # Retry stuck

# API
curl http://localhost:8090/api/version
curl http://localhost:8090/api/actions/quarantine
curl http://localhost:8090/api/actions?status=PENDING_APPROVAL

# Debug
docker logs vllm-qwen --tail 100
journalctl -u zakops-api-8090 -f
sqlite3 DataRoom/.deal-registry/ingest_state.db ".schema"
```

---

*Last updated: 2026-01-10*
*Document version: 2.0 (comprehensive revision)*
