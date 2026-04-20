# Pass 1 Report — CLAUDE
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T16:45:00Z

---

## Investigator Metadata

| Key | Value |
|-----|-------|
| Agent | Claude Opus 4.6 |
| Git Revision | `fc5e39d8f7bfa0ffa1859c8d2b5d914d063dffec` |
| Branch | `fix/full-remediation-001` |
| Pass | 1 of 3 (Independent) |
| Mode | Forensic (read-only — no code changes) |
| Scope | Intake → Quarantine → Deals pipeline |

---

## Executive Summary

The ZakOps Intake → Quarantine → Deals pipeline is **structurally sound** at its core. The canonical source of truth is a single PostgreSQL database (`zakops` schema on port 5432), and all services (Dashboard, Agent API, MCP Server) access deal data exclusively through the Backend API on port 8091. The quarantine-to-deal promotion is atomic (single PostgreSQL transaction), deal stage transitions are protected by a stored-function FSM with ledger and outbox, and de-duplication exists on quarantine items by `message_id`.

However, this investigation uncovered **8 findings** ranging from a confirmed endpoint mismatch bug to architectural gaps in the intake pipeline. The most significant finding is that the MCP Server's quarantine approval/rejection tools call a nonexistent endpoint (`/review` instead of `/process`), meaning external MCP clients cannot process quarantine items. Additionally, the email-to-quarantine ingestion pipeline depends on an external `email_ingestion` module that is not present in any of the three repositories, creating an undocumented dependency and a gap in the automated intake flow.

---

## Finding F-001: MCP Server Quarantine Endpoint Mismatch (BUG)

**Severity**: HIGH | **Category**: Contract Violation

### Evidence

**MCP Server** (`/home/zaks/zakops-backend/mcp_server/server.py`):
- Line 311: `return await backend_post(f"/api/quarantine/{item_id}/review", data)` (approve)
- Line 341: `return await backend_post(f"/api/quarantine/{item_id}/review", data)` (reject)

**Backend API** (`/home/zaks/zakops-backend/src/api/orchestration/main.py`):
- Line 1591: `@app.post("/api/quarantine/{item_id}/process")` (the actual endpoint)

**OpenAPI Spec** (`/home/zaks/zakops-backend/shared/openapi/zakops-api.json`):
- Line 966: `"/api/quarantine/{item_id}/process"` (confirms `/process` is correct)

### Root Cause
The MCP server was coded against a draft endpoint name (`/review`) that was later renamed to `/process` during implementation. The MCP server was never updated.

### Fix Approach
Change two lines in `mcp_server/server.py` (311, 341): replace `/review` with `/process`.

### Industry Standard
API contract enforcement via OpenAPI spec validation in CI — all client endpoints must match the published spec.

### System Fit
The `make validate-full` pipeline does not currently validate MCP server endpoints against the OpenAPI spec. Adding this check would prevent recurrence.

### Enforcement
Add an integration test or CI step that verifies all MCP `backend_post()` / `backend_get()` URLs exist in the OpenAPI spec.

---

## Finding F-002: No Automated Email Ingestion Pipeline

**Severity**: HIGH | **Category**: Architecture Gap

### Evidence

**Email integration is OAuth-only, user-initiated**:
- `/home/zaks/zakops-backend/src/core/integrations/email/service.py`: All operations (`get_inbox`, `get_thread`, `search_emails`) require a user-initiated call with an authenticated account.
- `/home/zaks/zakops-backend/src/api/orchestration/routers/email.py`: No scheduled/polling endpoints. Only manual endpoints: `GET /api/integrations/email/inbox`, `POST /api/integrations/email/search`.

**No cron jobs, no workers, no webhooks found**:
- No IMAP polling daemon
- No Gmail push notification webhook handler
- No scheduled task runner for email fetching
- SharePoint sync is a manual script (`/home/zaks/Zaks-llm/scripts/sharepoint_sync.py`), not a daemon

**External `email_ingestion` module referenced but absent**:
- `main.py:1491`: Comment states "email_ingestion pipeline calls this to insert emails into quarantine"
- `actions_runner.py:45`: `from email_ingestion.run_ledger import generate_run_id, run_context`
- `chat_orchestrator.py:45`: `from email_ingestion.chat_persistence import ChatSessionStore`
- `email_triage_review_email.py:267`: `from email_ingestion.enrichment.name_resolver import NameResolver`
- `deal_backfill_sender_history.py:15`: `from email_ingestion.enrichment.link_extractor import LinkExtractor`

This module is NOT present in `zakops-backend`, `zakops-agent-api`, or `Zaks-llm`. It appears to be an external Python module installed on the system path but not tracked in any of the three repositories.

### Root Cause
The `email_ingestion` module is an external dependency predating the current multi-repo architecture. The Phase 22 email integration (Gmail OAuth) provides manual email operations but does not replace the automated ingestion pipeline. There is currently no way for emails to automatically flow into quarantine.

### Fix Approach
Either: (A) Document and track the `email_ingestion` module as a formal dependency, or (B) Build a replacement ingestion pipeline using the Gmail OAuth integration (e.g., a background worker that polls `GET /inbox` and calls `POST /api/quarantine` for new messages).

### Industry Standard
Email ingestion should be a managed background process with:
- Configurable polling interval or push notifications (Gmail Pub/Sub)
- Dead-letter queue for failed ingestion
- Deduplication by message_id (already exists in quarantine creation)
- Observability (success/failure counts, latency metrics)

### System Fit
The quarantine `POST /api/quarantine` endpoint with deduplication (lines 1509-1529 of main.py) is ready to receive automated ingestion — the gap is purely in the producer side.

### Enforcement
Add a health check or metric for "time since last quarantine item created" to detect ingestion pipeline failures.

---

## Finding F-003: Legacy SQLite Dual-Write Infrastructure Still Present

**Severity**: MEDIUM | **Category**: Technical Debt

### Evidence

**`.env.example`** (lines 37-45):
```
SQLITE_PATH=/home/zaks/DataRoom/.deal-registry/ingest_state.db
ZAKOPS_STATE_DB=/home/zaks/DataRoom/.deal-registry/ingest_state.db
DUAL_WRITE_ENABLED=false
```

**Database adapter** (`/home/zaks/zakops-backend/src/core/database/adapter.py`):
- Line 56: Reads `ZAKOPS_STATE_DB` env var, defaults to SQLite path
- Line 63: `self.dual_write = os.getenv("DUAL_WRITE_ENABLED", "false").lower() == "true"`
- Lines 121-138: Conditionally connects to both PostgreSQL and SQLite if dual-write enabled
- Lines 187, 214, 235: Dual-write logic in read/write operations

**Action engine store** (`/home/zaks/zakops-backend/src/actions/engine/store.py`):
- Line 27: `return Path(os.getenv("ZAKOPS_STATE_DB", "/home/zaks/DataRoom/.deal-registry/ingest_state.db"))`

**Memory store** (`/home/zaks/zakops-backend/src/actions/memory/store.py`):
- Line 15: Same SQLite path default

### Root Cause
The system migrated from SQLite to PostgreSQL but left the dual-write adapter and SQLite path references. `DUAL_WRITE_ENABLED=false` means this code is inactive, but it adds complexity and confusion.

### Fix Approach
Remove the dual-write adapter code path and SQLite references from the database adapter, action store, and memory store. The actions engine should use PostgreSQL directly.

### Industry Standard
Dead code removal. A toggled-off feature flag that references filesystem paths outside the application directory is a maintenance risk.

### System Fit
The DSN startup gate (main.py:395-419) already ensures the backend connects to the canonical `zakops` PostgreSQL database. The SQLite path is vestigial.

### Enforcement
Add a lint rule or startup warning if `DUAL_WRITE_ENABLED` is set to `true`.

---

## Finding F-004: OAuth State Stored In-Memory (Not Production-Safe)

**Severity**: MEDIUM | **Category**: Security / Scalability

### Evidence

**Email router** (`/home/zaks/zakops-backend/src/api/orchestration/routers/email.py`, lines 31-54):
- `OAuthStateStore` class uses a Python `dict` for CSRF state tokens
- 5-minute expiry per state entry
- Comment at line 52 acknowledges this is not suitable for multi-instance

### Root Cause
The OAuth flow was implemented for single-instance development. In a multi-instance deployment, the OAuth callback could hit a different instance than the one that generated the state token, causing authentication failures.

### Fix Approach
Move OAuth state to Redis (already in the stack on port 6379) or the PostgreSQL database.

### Industry Standard
OAuth state must be stored in a shared, persistent store in any deployment with more than one application instance. OWASP recommends CSRF state tokens be bound to the user's session and stored server-side.

### System Fit
Redis is already available in the ZakOps infrastructure (port 6379). This is a straightforward migration.

### Enforcement
Add a startup check: if `DEPLOYMENT_MODE != "development"`, require Redis-backed OAuth state.

---

## Finding F-005: Quarantine Approval Does Not Use FSM `transition_deal_state()`

**Severity**: MEDIUM | **Category**: Consistency

### Evidence

**Normal deal transitions** use the FSM stored function:
- `workflow.py:105-325`: `DealWorkflowEngine.transition_stage()` calls `transition_deal_state()` PL/pgSQL function
- `025_deal_lifecycle_fsm.sql:67-161`: `transition_deal_state()` provides row-level locking, idempotency, ledger recording, and outbox publishing

**Quarantine approval creates deals directly**:
- `main.py:1623-1680`: `process_quarantine()` does a raw `INSERT INTO zakops.deals` followed by `record_deal_event()`, bypassing:
  - The `transition_deal_state()` function
  - The `deal_transitions` ledger table
  - The outbox pattern for side-effects
  - The `enforce_deal_lifecycle` trigger (though this fires on INSERT, so the trigger does apply)

### Root Cause
The quarantine approval was implemented before the FSM infrastructure (migration 025). The initial deal creation from quarantine uses raw SQL rather than routing through the workflow engine.

### Fix Approach
After inserting the deal, call `transition_deal_state(deal_id, 'inbound', 'quarantine_approval', processed_by)` to record the initial state in the transitions ledger and trigger the outbox. Alternatively, refactor to use `DealWorkflowEngine` for the initial stage assignment.

### Industry Standard
All state changes should flow through a single choke point (the FSM) to ensure consistent auditing, side-effects, and invariant enforcement.

### System Fit
The `enforce_deal_lifecycle` trigger does fire on INSERT, so the basic constraint is met. But the ledger and outbox are bypassed, meaning:
- No entry in `deal_transitions` for the initial `inbound` stage
- No outbox event for downstream consumers (folder creation, RAG indexing, notifications)

### Enforcement
Add an assertion: every deal_id in `zakops.deals` must have at least one entry in `zakops.deal_transitions`. Run as a periodic integrity check.

---

## Finding F-006: Dashboard Email Settings Proxy May Target Nonexistent Endpoint

**Severity**: LOW | **Category**: Dead Code / Integration Gap

### Evidence

**Dashboard route** (`apps/dashboard/src/app/api/settings/email/route.ts`):
- Line 12: `const response = await backendFetch('/api/user/email-config', { timeoutMs: 3000 });`

**Backend API** (`main.py`): No endpoint `/api/user/email-config` exists. The email endpoints are under `/api/integrations/email/`.

**Dashboard behavior**: The route returns 404 with `"Email integration not available"` for any non-200 response, so this fails silently.

### Root Cause
The dashboard email settings UI was scaffolded against a planned endpoint that was never implemented, or was implemented under a different path.

### Fix Approach
Either: (A) Remove the dead settings route, or (B) Implement `/api/user/email-config` in the backend, or (C) Update the dashboard to use `/api/integrations/email/accounts`.

### Industry Standard
Dead proxy routes should be removed or clearly marked as feature-flagged.

### System Fit
Low impact — the route gracefully degrades to 404, and the settings page handles this by showing "Email integration not available."

### Enforcement
OpenAPI spec validation: all dashboard proxy routes should target endpoints that exist in the spec.

---

## Finding F-007: Correlation ID Not Propagated End-to-End

**Severity**: LOW | **Category**: Observability

### Evidence

**Dashboard middleware** (`apps/dashboard/src/middleware.ts`):
- Generates `X-Correlation-ID` header for proxied requests to backend
- BUT only for routes that go through the middleware proxy path (non-handled routes)

**Dashboard API routes** (e.g., `quarantine/[id]/process/route.ts`):
- Uses `backendFetch()` which adds auth headers but correlation ID propagation depends on `backendFetch` implementation

**Agent API** (`apps/agent-api/app/services/backend_client.py`):
- Line 89-90: Sends `X-Correlation-ID` header if `_correlation_id` is set on the client instance
- Context variable `_correlation_id_ctx` propagates within agent tool calls

**Backend API** (`main.py`):
- Line 681: Generates correlation_id from deal_id for deal creation events, but does not extract/propagate incoming `X-Correlation-ID` from request headers

### Root Cause
Correlation ID generation and propagation was implemented piecemeal across services rather than as a unified middleware concern.

### Fix Approach
Add a backend middleware that:
1. Extracts `X-Correlation-ID` from incoming request headers
2. Falls back to generating a new UUID if not present
3. Attaches to all log entries and database events
4. Returns in response headers

### Industry Standard
OpenTelemetry or W3C Trace Context standard for distributed tracing. Every log line should include the correlation/trace ID.

### System Fit
The infrastructure is partially in place (middleware generates IDs, agent propagates them). The gap is in the backend not consuming the incoming header.

### Enforcement
Add structured logging middleware to backend that rejects requests without correlation IDs in production mode, or auto-generates and logs them.

---

## Finding F-008: Deals Table Default Stage Mismatch

**Severity**: LOW | **Category**: Schema Inconsistency

### Evidence

**Database DDL** (`db/init/001_base_tables.sql`, line 36):
```sql
stage VARCHAR(50) DEFAULT 'lead',
```

**DealStage enum** (`src/core/deals/workflow.py`, line 41):
```python
class DealStage(str, Enum):
    INBOUND = "inbound"
    # ... no "lead" stage
```

**Quarantine approval** (`main.py`, line 1660):
```python
'inbound',  # INITIAL STAGE — overrides the DDL default
```

**Deal creation endpoint** (`main.py`, line 655):
```python
# Uses deal.stage from input, defaults to 'inbound' in DealCreate model
```

### Root Cause
The DDL default of `'lead'` predates the current M&A stage taxonomy which uses `'inbound'`. All code paths explicitly set the stage, so the DDL default never fires, but it's inconsistent.

### Fix Approach
Alter the DDL default: `ALTER TABLE zakops.deals ALTER COLUMN stage SET DEFAULT 'inbound';`

### Industry Standard
DDL defaults should match the application's canonical enum values.

### System Fit
Low risk — all code paths set stage explicitly. But a future code path that omits the stage would create a deal with an invalid stage value.

### Enforcement
Add a CHECK constraint: `CHECK (stage IN ('inbound', 'screening', 'qualified', 'loi', 'diligence', 'closing', 'portfolio', 'junk', 'archived'))`.

---

## Forensic Questions Checklist

### Source of Truth (R1)

| # | Question | Answer | Evidence |
|---|----------|--------|----------|
| R1-1 | Which database is the canonical source of truth for deals? | `zakops` (PostgreSQL, port 5432, schema `zakops`) | `main.py:85-88`: `DATABASE_URL = "postgresql://zakops:zakops_dev@localhost:5432/zakops"` |
| R1-2 | Does the DSN startup gate enforce canonical DB? | Yes | `main.py:395-419`: Checks `CANONICAL_DB_NAME = "zakops"` on startup, aborts if mismatch |
| R1-3 | Do any services write directly to `zakops` DB bypassing the API? | No. Agent API uses BackendClient HTTP. Dashboard proxies through middleware. MCP server uses HTTP. | `backend_client.py:73`, `middleware.ts`, `mcp_server/server.py` |
| R1-4 | Is there a split-brain risk? | Low. The only risk is the `email_ingestion` external module and the Deal Origination module in Zaks-llm, which reference direct DB connections. | `deal_backfill_sender_history.py:15`, `Zaks-llm/src/deal_origination/` |

### Intake Pipeline (R2)

| # | Question | Answer | Evidence |
|---|----------|--------|----------|
| R2-1 | How do emails enter the system? | Via external `email_ingestion` module calling `POST /api/quarantine`. No automated polling exists in the current codebase. | `main.py:1491` comment, `email_ingestion` imports in 5 files |
| R2-2 | Is there a Gmail webhook or push notification handler? | No. Only OAuth-based manual operations. | `routers/email.py`: Only `GET /inbox`, `POST /search`, `GET /threads/{id}` |
| R2-3 | Is there deduplication on quarantine ingestion? | Yes, by `message_id`. | `main.py:1509-1529`: `SELECT id FROM quarantine_items WHERE message_id = $1` before insert |
| R2-4 | What happens if the external email_ingestion module is unavailable? | No emails enter quarantine. No health check or monitoring for this. | Absence of any polling or worker daemon |

### Quarantine Layer (R3)

| # | Question | Answer | Evidence |
|---|----------|--------|----------|
| R3-1 | What are the quarantine item statuses? | `pending`, `approved`, `rejected`, `deleted` (soft) | `QuarantineResponse` model, `main.py:252` |
| R3-2 | Is the approve/reject action validated? | Yes, via Pydantic regex: `pattern="^(approve|reject)$"` | `QuarantineProcess` model, `main.py:271` |
| R3-3 | Can a non-pending item be re-processed? | No. The endpoint checks `if item['status'] != 'pending'` and returns 400. | `main.py:1606-1610` (inferred from transaction logic) |
| R3-4 | Is the quarantine table schema in sync with the API model? | Partial mismatch. DB uses `raw_content` JSONB for `classification`, `urgency`, `company_name`, `broker_name`. API model presents these as top-level fields. | `001_base_tables.sql` vs `QuarantineResponse` model |

### Approval/Promotion Flow (R3a)

| # | Question | Answer | Evidence |
|---|----------|--------|----------|
| R3a-1 | Is quarantine → deal promotion atomic? | Yes. Single `async with conn.transaction()` block. | `main.py:1602-1715` |
| R3a-2 | What fields map from quarantine to deal? | subject→canonical_name, sender→broker.email, broker_name→broker.name, message_id→identifiers | `main.py:1623-1680` (see F-005 for detailed mapping) |
| R3a-3 | Does it use the FSM for initial stage? | No. Raw INSERT with `stage='inbound'`. Bypasses `transition_deal_state()` and `deal_transitions` ledger. | Finding F-005 |
| R3a-4 | Is a deal_created event recorded? | Yes, via `record_deal_event()`. | `main.py:1675` |

### Deal Lifecycle (R4)

| # | Question | Answer | Evidence |
|---|----------|--------|----------|
| R4-1 | Are stage transitions enforced by the FSM? | Yes, via `transition_deal_state()` stored function with row-level locking. | `025_deal_lifecycle_fsm.sql:67-161` |
| R4-2 | Does the agent duplicate the transition matrix? | Yes. `VALID_TRANSITIONS` in `deal_tools.py` mirrors `STAGE_TRANSITIONS` in `workflow.py`. | `deal_tools.py:83-95`, `workflow.py:54-64` |
| R4-3 | Is there a no-illusions gate on agent transitions? | Yes. Agent re-fetches deal after transition to verify stage change. | `deal_tools.py` F-003 RT-1 annotation |
| R4-4 | Can the agent see newly promoted deals immediately? | Yes. No indexing delay — direct DB query via backend API. | Agent `list_deals()` → backend `GET /api/deals` → `zakops.deals` table |
| R4-5 | Is there an outbox for side-effects? | Yes, but only for transitions through `DealWorkflowEngine`. | `workflow.py:248-275`, `outbox/writer.py` |

### Observability (R5)

| # | Question | Answer | Evidence |
|---|----------|--------|----------|
| R5-1 | Is there a deal_events audit trail? | Yes. `zakops.deal_events` table with event_type, source, actor, payload. | `001_base_tables.sql:107-122` |
| R5-2 | Is there a transitions ledger? | Yes. `zakops.deal_transitions` table (migration 025). | `025_deal_lifecycle_fsm.sql` |
| R5-3 | Is correlation ID propagated end-to-end? | Partially. Dashboard generates it, agent sends it, but backend doesn't extract/use incoming header. | Finding F-007 |

---

## Gap & Misalignment Table

| # | Gap | Severity | Layer | Impact |
|---|-----|----------|-------|--------|
| G-1 | MCP server calls `/review` instead of `/process` | HIGH | MCP → Backend | MCP quarantine approve/reject is broken |
| G-2 | No automated email ingestion pipeline in codebase | HIGH | Intake | Quarantine items can only be created manually or by external module |
| G-3 | External `email_ingestion` module not tracked in repos | HIGH | Intake | Undocumented dependency, no CI/CD coverage |
| G-4 | Quarantine approval bypasses FSM choke point | MEDIUM | Quarantine → Deal | No ledger entry, no outbox event for initial stage |
| G-5 | OAuth state in-memory (not multi-instance safe) | MEDIUM | Email Auth | OAuth flow fails in multi-instance deployment |
| G-6 | DDL default stage `'lead'` doesn't exist in enum | LOW | Schema | Inconsistency — no functional impact currently |
| G-7 | Dashboard `/api/user/email-config` targets nonexistent endpoint | LOW | Dashboard → Backend | Silent 404, no functional impact |
| G-8 | Correlation ID not consumed by backend | LOW | Observability | Cross-service tracing incomplete |
| G-9 | `DUAL_WRITE_ENABLED` / SQLite adapter still in codebase | MEDIUM | Tech Debt | Confusion, unnecessary code paths |
| G-10 | Outlook email provider entirely stubbed | LOW | Email | No Microsoft email support |
| G-11 | Email outreach Gmail MCP integration stubbed | LOW | Origination | Deal origination email outreach non-functional |
| G-12 | No CHECK constraint on deals.stage column | LOW | Schema | Arbitrary stage values possible via raw SQL |

---

## Contrarian Sweep: Top 10 Failure Patterns

| # | Failure Pattern | Could It Happen Here? | Evidence / Mitigation |
|---|----------------|----------------------|----------------------|
| 1 | **Split-brain: two services write to the same table** | LOW. All services go through Backend API at 8091. The `email_ingestion` module and `Zaks-llm/deal_origination` are potential exceptions. | DSN startup gate enforces canonical DB. Agent uses BackendClient HTTP. |
| 2 | **Phantom deal: quarantine approved but deal creation fails** | NO. Single transaction (`async with conn.transaction()`). If deal INSERT fails, quarantine status rollback is automatic. | `main.py:1602` — atomic transaction boundary |
| 3 | **Orphaned quarantine: approved item with no linked deal** | NO. Deal creation and quarantine status update are in the same transaction. | Same atomic block. |
| 4 | **Stage regression: deal moves backward unexpectedly** | LOW. FSM `STAGE_TRANSITIONS` matrix only allows specific transitions. Backward moves (LOI→QUALIFIED) are explicitly in the matrix. | `workflow.py:57`: `DealStage.LOI: [DealStage.DILIGENCE, DealStage.QUALIFIED, ...]` — intentional |
| 5 | **Duplicate deals from same email** | LOW. Quarantine dedup by `message_id`. But if `message_id` is null (manual creation), duplicates are possible. | `main.py:1509-1529`: `WHERE message_id = $1` check |
| 6 | **Agent creates deal without HITL approval** | LOW. `create_deal` tool has HITL annotation. But enforcement depends on LangGraph HITL node being properly wired. | `deal_tools.py`: HITL annotation present, LangGraph interrupt mechanism |
| 7 | **MCP approves quarantine item (broken endpoint)** | YES. MCP calls `/review` which returns 404 or 405. MCP quarantine approval is non-functional. | Finding F-001 — confirmed bug |
| 8 | **Deal transition without outbox event (missed side-effects)** | YES. Quarantine-promoted deals bypass the outbox. Also, outbox is gated by `is_outbox_enabled()`. | Finding F-005, `workflow.py:249` |
| 9 | **OAuth token leak via logs** | LOW. Token values are stored encrypted (Fernet). But log statements could inadvertently log token values if not redacted. | `email/service.py` uses Fernet encryption. CLAUDE.md mandates redaction. |
| 10 | **Quarantine item processed after expiry** | N/A. No TTL on quarantine items. Items sit in `pending` indefinitely. Could be a feature gap. | No expiry mechanism found |

---

## Remediation Recommendations (Prioritized)

### Priority 1: Fix MCP Endpoint Mismatch (F-001)
- **Effort**: Trivial (2 lines changed)
- **Risk**: Zero — aligns MCP with correct backend endpoint
- **Files**: `mcp_server/server.py` lines 311, 341
- **Validation**: Run MCP quarantine approval test against live backend

### Priority 2: Document or Replace `email_ingestion` Module (F-002)
- **Effort**: Medium (documentation) or High (replacement)
- **Risk**: Low — no breaking change, additive
- **Options**:
  - A: Track `email_ingestion` as a git submodule or pip dependency
  - B: Build a polling worker using Gmail OAuth `GET /inbox` → `POST /api/quarantine`
- **Validation**: Verify automated quarantine item creation from email

### Priority 3: Route Quarantine Approval Through FSM (F-005)
- **Effort**: Low (add `transition_deal_state()` call after INSERT)
- **Risk**: Low — additive change
- **Validation**: Verify `deal_transitions` has entry for quarantine-promoted deals

### Priority 4: Move OAuth State to Redis (F-004)
- **Effort**: Low (Redis is already in stack)
- **Risk**: Low — behavior change only for edge case
- **Validation**: Test OAuth flow with multiple backend instances

### Priority 5: Clean Up Legacy SQLite Dual-Write (F-003)
- **Effort**: Medium (code removal, testing)
- **Risk**: Medium — actions engine store still defaults to SQLite path
- **Validation**: Verify actions engine works with PostgreSQL-only mode

### Priority 6: Fix DDL Default Stage (F-008)
- **Effort**: Trivial (one ALTER TABLE)
- **Risk**: Zero — no running code uses the default
- **Validation**: Schema introspection confirms `'inbound'` default

---

## Minimum Proof Steps (Pipeline Validation)

To validate the full Intake → Quarantine → Deals pipeline is working:

```bash
# 1. Create a quarantine item
curl -s -X POST http://localhost:8091/api/quarantine \
  -H "Content-Type: application/json" \
  -d '{"message_id":"test-msg-001","email_subject":"Test Deal","sender":"broker@test.com","classification":"inbound_email","urgency":"normal","confidence":0.8,"company_name":"TestCo","broker_name":"Test Broker"}' | jq .

# 2. List pending quarantine items (verify item appears)
curl -s "http://localhost:8091/api/quarantine?status=pending" | jq '.items | length'

# 3. Approve the quarantine item (should auto-create deal)
ITEM_ID=$(curl -s "http://localhost:8091/api/quarantine?status=pending" | jq -r '.items[0].id')
curl -s -X POST "http://localhost:8091/api/quarantine/${ITEM_ID}/process" \
  -H "Content-Type: application/json" \
  -d '{"action":"approve","processed_by":"test_operator"}' | jq .

# 4. Verify deal was created
DEAL_ID=$(curl -s "http://localhost:8091/api/quarantine/${ITEM_ID}" | jq -r '.deal_id')
curl -s "http://localhost:8091/api/deals/${DEAL_ID}" | jq '{deal_id, canonical_name, stage, status}'

# 5. Verify deal event was recorded
curl -s "http://localhost:8091/api/deals/${DEAL_ID}/events" | jq '.[0] | {event_type, event_source, actor}'

# 6. Verify deal is visible via agent API
curl -s http://localhost:8095/api/deals -H "X-Service-Token: $DASHBOARD_SERVICE_TOKEN" | jq ".deals[] | select(.deal_id == \"${DEAL_ID}\")"

# 7. Verify MCP endpoint mismatch (this SHOULD fail — confirms F-001)
# MCP calls /review, not /process — expect 404 or 405
curl -s -X POST "http://localhost:8091/api/quarantine/${ITEM_ID}/review" \
  -H "Content-Type: application/json" \
  -d '{"action":"approve","processed_by":"mcp_test"}' | jq .
# Expected: 404 or Method Not Allowed — confirms the bug
```

---

## Evidence Index

| Evidence ID | File | Lines | Description |
|-------------|------|-------|-------------|
| E-001 | `zakops-backend/src/api/orchestration/main.py` | 85-88 | DATABASE_URL canonical DSN |
| E-002 | `zakops-backend/src/api/orchestration/main.py` | 395-419 | DSN startup gate |
| E-003 | `zakops-backend/src/api/orchestration/main.py` | 1509-1529 | Quarantine deduplication by message_id |
| E-004 | `zakops-backend/src/api/orchestration/main.py` | 1591-1716 | Quarantine approval atomic transaction |
| E-005 | `zakops-backend/src/api/orchestration/main.py` | 1623-1680 | Deal creation from quarantine (raw INSERT) |
| E-006 | `zakops-backend/mcp_server/server.py` | 311 | MCP approve calls `/review` (wrong) |
| E-007 | `zakops-backend/mcp_server/server.py` | 341 | MCP reject calls `/review` (wrong) |
| E-008 | `zakops-backend/shared/openapi/zakops-api.json` | 966 | OpenAPI confirms `/process` is correct |
| E-009 | `zakops-backend/src/core/deals/workflow.py` | 40-50 | DealStage enum (no `lead` stage) |
| E-010 | `zakops-backend/src/core/deals/workflow.py` | 54-64 | STAGE_TRANSITIONS matrix |
| E-011 | `zakops-backend/src/core/deals/workflow.py` | 248-275 | Outbox writes on stage transitions |
| E-012 | `zakops-backend/db/init/001_base_tables.sql` | 29-51 | Deals table DDL (default stage = 'lead') |
| E-013 | `zakops-backend/db/init/001_base_tables.sql` | 125-142 | record_deal_event() function |
| E-014 | `zakops-backend/db/migrations/025_deal_lifecycle_fsm.sql` | 67-161 | transition_deal_state() function |
| E-015 | `zakops-backend/db/migrations/025_deal_lifecycle_fsm.sql` | 186-213 | enforce_deal_lifecycle trigger |
| E-016 | `zakops-backend/src/api/orchestration/routers/email.py` | 31-54 | In-memory OAuthStateStore |
| E-017 | `zakops-backend/.env.example` | 37-45 | SQLite/dual-write config |
| E-018 | `zakops-backend/src/core/database/adapter.py` | 56-63, 121-138 | Dual-write adapter logic |
| E-019 | `zakops-agent-api/apps/agent-api/app/services/backend_client.py` | 73 | Agent API DEAL_API_URL default |
| E-020 | `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py` | 83-95 | Agent VALID_TRANSITIONS (duplicated) |
| E-021 | `zakops-agent-api/apps/dashboard/src/middleware.ts` | all | Dashboard proxy middleware |
| E-022 | `zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts` | 12 | Proxy to `/api/user/email-config` |
| E-023 | `zakops-backend/src/workers/actions_runner.py` | 45 | Import from external email_ingestion |
| E-024 | `zakops-backend/src/core/chat_orchestrator.py` | 45 | Import from external email_ingestion |
| E-025 | `zakops-backend/src/actions/executors/email_triage_review_email.py` | 267 | Import from external email_ingestion |
| E-026 | `zakops-backend/src/actions/executors/deal_backfill_sender_history.py` | 15 | Import from external email_ingestion |
| E-027 | `zakops-agent-api/apps/dashboard/src/app/api/quarantine/[id]/process/route.ts` | 21 | Dashboard proxies to correct `/process` endpoint |
| E-028 | `zakops-backend/src/api/orchestration/main.py` | 681 | Correlation ID generation from deal_id |

---

## Conclusion

The core deal pipeline (PostgreSQL → Backend API → consumers) is architecturally sound with proper atomicity, deduplication, and FSM enforcement. The three highest-priority issues are:

1. **MCP endpoint bug (F-001)**: Trivial fix, breaks external tooling
2. **Missing automated ingestion (F-002)**: The biggest functional gap — no way for emails to flow into quarantine automatically without the undocumented `email_ingestion` module
3. **FSM bypass on quarantine promotion (F-005)**: Deals created from quarantine miss the transitions ledger and outbox

All findings have clear fix approaches and none require architectural changes. The system's defense-in-depth (DSN gate, atomic transactions, FSM triggers, typed clients) is well-designed — the gaps are at the seams between subsystems rather than in the core logic.

---

*End of Pass 1 Report — CLAUDE*
*TriPass Run: TP-20260213-163446*
