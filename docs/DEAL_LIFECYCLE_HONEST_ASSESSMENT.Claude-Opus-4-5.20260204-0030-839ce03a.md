# ZakOps Deal Lifecycle: Forensic Assessment

## AGENT IDENTITY
- **agent_name:** Claude-Opus-4-5
- **agent_version:** claude-opus-4-5-20251101
- **run_id:** 20260204-0030-839ce03a
- **repo_revision:** a09538f04ed278c32ad6f2a037069b353bf5f797 (zakops-backend)
- **date_time:** 2026-02-04T00:30:00Z

---

## 1. Executive Summary

**What is a "Deal" in ZakOps today?**

A "Deal" is a tracked M&A acquisition opportunity with:
- A database record in `zakops.deals` (source of truth for stage/status)
- Optionally, a filesystem presence in `/home/zaks/DataRoom/00-PIPELINE/`
- A JSON entry in deal_registry.json (parallel tracking system, not synced)

**Critical Finding:** There are **THREE separate deal tracking systems** that do not automatically synchronize:
1. **PostgreSQL `zakops.deals`** — Backend API's source of truth (DL-XXXX IDs)
2. **JSON `deal_registry.json`** — Email ingestion's source of truth (DEAL-YYYY-### IDs)
3. **Filesystem DataRoom folders** — Document storage (folder names)

**Infrastructure Status:** The core deal CRUD and stage transition logic is **well-implemented and battle-tested**. The stage state machine enforces valid transitions at both code and database levels. HITL approval for agent-driven transitions works correctly.

**Integration Status:** The connective tissue between systems is **partial to broken**:
- Email → Quarantine → Deal path exists but cron is **NOT ACTIVE**
- Database → DataRoom folder sync is **NOT IMPLEMENTED**
- Dashboard shows backend deals but **NOT** DataRoom documents

---

## 2. Canonical Deal Data Model (As Implemented)

### 2.1 Primary Table: `zakops.deals`

**Location:** `/home/zaks/zakops-backend/db/init/001_base_tables.sql`

```sql
CREATE TABLE IF NOT EXISTS zakops.deals (
    deal_id VARCHAR(20) PRIMARY KEY,          -- "DL-0001" format
    canonical_name VARCHAR(255) NOT NULL,     -- Company name
    display_name VARCHAR(255),                -- Optional alias
    folder_path VARCHAR(1024),                -- DataRoom path (NOT enforced)
    stage VARCHAR(50) DEFAULT 'inbound',      -- State machine position
    status VARCHAR(50) DEFAULT 'active',      -- 'active' or 'stalled'
    identifiers JSONB DEFAULT '{}',           -- Listing IDs, broker refs
    company_info JSONB DEFAULT '{}',          -- Sector, location, etc.
    broker JSONB DEFAULT '{}',                -- Broker details
    metadata JSONB DEFAULT '{}',              -- Arbitrary data
    deleted BOOLEAN DEFAULT FALSE,            -- Soft delete flag
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
```

**ID Generation:**
```sql
CREATE SEQUENCE zakops.deal_id_seq START 1;
-- Returns "DL-0001", "DL-0002", etc.
```

### 2.2 Event History: `zakops.deal_events`

**Purpose:** Immutable audit trail of all deal changes

```sql
CREATE TABLE IF NOT EXISTS zakops.deal_events (
    id UUID PRIMARY KEY,
    deal_id VARCHAR(20) REFERENCES zakops.deals,
    event_type VARCHAR(100) NOT NULL,         -- 'stage_changed', 'created', etc.
    event_source VARCHAR(100),                -- 'workflow', 'api', 'agent'
    actor VARCHAR(255),                       -- Who made the change
    payload JSONB DEFAULT '{}',               -- Event details
    idempotency_key VARCHAR(64),              -- For duplicate detection (24h)
    created_at TIMESTAMPTZ NOT NULL
);
```

### 2.3 Stage Constraint

**Location:** `/home/zaks/zakops-backend/db/migrations/023_stage_check_constraint.sql`

```sql
ALTER TABLE zakops.deals ADD CONSTRAINT chk_deals_stage
    CHECK (stage IN ('inbound','screening','qualified','loi',
                     'diligence','closing','portfolio','junk','archived'));
```

**Effect:** Database rejects any INSERT/UPDATE with non-canonical stage values.

### 2.4 Related Tables

| Table | Purpose | Foreign Key |
|-------|---------|-------------|
| `zakops.deal_aliases` | Alternative identifiers | deal_id → deals |
| `zakops.deal_events` | Event history | deal_id → deals |
| `zakops.actions` | Workflow tasks | deal_id → deals |
| `zakops.quarantine_items` | Email quarantine | deal_id → deals (nullable) |
| `zakops.email_threads` | Email tracking | deal_id → deals (nullable) |
| `zakops.artifacts` | Document storage | deal_id → deals (nullable) |

### 2.5 Source of Truth

| System | Owns | Trusts |
|--------|------|--------|
| Backend API (8091) | `zakops.deals` | Self |
| Agent API (8095) | `zakops_agent.approvals` | Backend for deals |
| Email Ingestion | `ingest_state.db`, `deal_registry.json` | Self (NO sync) |
| Dashboard | Nothing | Backend for all |

**CRITICAL:** Email ingestion writes to `deal_registry.json` and SQLite. It does NOT call `POST /api/deals`. Deals created by email ingestion **do not exist** in the backend database.

---

## 3. Deal State Machine (As Implemented)

### 3.1 Stages

**Location:** `/home/zaks/zakops-backend/src/core/deals/workflow.py`

```python
class DealStage(str, Enum):
    INBOUND = "inbound"       # New opportunity, not yet reviewed
    SCREENING = "screening"   # Initial evaluation
    QUALIFIED = "qualified"   # Passed screening, active pursuit
    LOI = "loi"               # Letter of Intent phase
    DILIGENCE = "diligence"   # Due diligence in progress
    CLOSING = "closing"       # Final paperwork
    PORTFOLIO = "portfolio"   # Acquired (terminal success)
    JUNK = "junk"             # Rejected (can restore)
    ARCHIVED = "archived"     # Final terminal state
```

### 3.2 Allowed Transitions

```python
STAGE_TRANSITIONS = {
    INBOUND:    [SCREENING, JUNK, ARCHIVED],
    SCREENING:  [QUALIFIED, JUNK, ARCHIVED],
    QUALIFIED:  [LOI, JUNK, ARCHIVED],
    LOI:        [DILIGENCE, QUALIFIED, JUNK, ARCHIVED],  # Can regress
    DILIGENCE:  [CLOSING, LOI, JUNK, ARCHIVED],          # Can regress
    CLOSING:    [PORTFOLIO, DILIGENCE, JUNK, ARCHIVED],  # Can regress
    PORTFOLIO:  [ARCHIVED],                              # Terminal
    JUNK:       [INBOUND, ARCHIVED],                     # Can resurrect
    ARCHIVED:   [],                                       # Final
}
```

### 3.3 ASCII State Diagram

```
                    ┌──────────────────────────────────────────────┐
                    │                                              │
                    ▼                                              │
┌─────────┐   ┌───────────┐   ┌───────────┐   ┌─────┐   ┌───────────┐   ┌─────────┐   ┌───────────┐
│ INBOUND │──▶│ SCREENING │──▶│ QUALIFIED │──▶│ LOI │──▶│ DILIGENCE │──▶│ CLOSING │──▶│ PORTFOLIO │
└────┬────┘   └─────┬─────┘   └─────┬─────┘   └──┬──┘   └─────┬─────┘   └────┬────┘   └─────┬─────┘
     │              │               │            │            │              │              │
     │              │               │            ▲            ▲              ▲              │
     │              │               │            │            │              │              │
     │              │               │            └────────────┴──────────────┘              │
     │              │               │         (regression allowed at LOI+)                  │
     │              │               │                                                       │
     ▼              ▼               ▼                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         JUNK                                               │
│                                    (can resurrect to INBOUND)                              │
└─────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                              │
                                              ▼
                                        ┌──────────┐
                                        │ ARCHIVED │ (terminal, no exits)
                                        └──────────┘
```

### 3.4 Transition Triggers

| Trigger | Mechanism | Reference |
|---------|-----------|-----------|
| Dashboard UI | `POST /api/deals/{id}/transition` via `transitionDeal()` | `apps/dashboard/src/lib/api.ts` |
| Agent Tool | `transition_deal` tool → same endpoint | `deal_tools.py:81` |
| Direct API | HTTP POST with idempotency_key | `routers/workflow.py` |

### 3.5 Idempotency Implementation

**Location:** `/home/zaks/zakops-backend/src/core/deals/workflow.py:120-155`

```python
# Check idempotency first (before any locks)
if idempotency_key:
    existing = await db.fetchrow("""
        SELECT payload, actor, created_at
        FROM zakops.deal_events
        WHERE deal_id = $1
          AND idempotency_key = $2
          AND event_type = 'stage_changed'
          AND created_at > NOW() - INTERVAL '24 hours'
        ORDER BY created_at DESC LIMIT 1
    """, deal_id, idempotency_key)

    if existing:
        return StageTransition(..., idempotent_hit=True)
```

**Behavior:** 24-hour window for idempotent replays. Same key returns cached result.

---

## 4. End-to-End "Deal Story" (The Narrative)

### 4.1 SCENARIO A: Manual Deal Creation (WORKS)

**Step 1:** User calls `POST /api/deals`

```bash
curl -X POST http://localhost:8091/api/deals \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"canonical_name": "Acme Corp", "stage": "inbound"}'
```

**Code Path:**
1. `main.py` → `create_deal()` endpoint
2. Validates stage against `ValidStage` Literal type
3. Generates `deal_id` via `zakops.next_deal_id()`
4. `INSERT INTO zakops.deals`
5. Returns deal object

**References:**
- Endpoint: `/home/zaks/zakops-backend/src/api/orchestration/main.py`
- ID Generator: `/home/zaks/zakops-backend/db/init/001_base_tables.sql:next_deal_id()`

**VERIFIED:** Working as of 2026-02-04

---

**Step 2:** Deal appears in Dashboard

```
Dashboard → GET /api/deals → PostgreSQL zakops.deals
```

**VERIFIED:** Working

---

**Step 3:** User transitions deal via Dashboard

1. User clicks stage button in Deal Workspace
2. Dialog captures: target stage, reason, approved_by
3. Dashboard calls `transitionDeal(dealId, newStage, reason, approvedBy)`
4. Which calls `POST /api/deals/{id}/transition`
5. `DealWorkflowEngine.transition_stage()` validates and executes
6. `deal_events` records `stage_changed` event

**Code Path:**
- Dashboard: `apps/dashboard/src/app/deals/[id]/page.tsx:transitionDeal`
- API Router: `routers/workflow.py`
- Engine: `core/deals/workflow.py:transition_stage()`

**VERIFIED:** Working

---

### 4.2 SCENARIO B: Agent-Driven Transition (WORKS with HITL)

**Step 1:** User asks agent to move deal

```
User: "Move deal DL-0005 to diligence"
```

**Step 2:** Agent invokes `transition_deal` tool

```python
transition_deal(
    deal_id="DL-0005",
    from_stage="loi",        # Advisory, will be verified
    to_stage="diligence",
    reason="Ready for due diligence"
)
```

**Code Path:**
1. Tool validates `to_stage` against `VALID_STAGES` frozenset
2. Fetches current deal state from backend (ground truth)
3. If `from_stage` mismatches actual, logs warning but continues
4. Tool marked as HITL-required → LangGraph interrupt

**Reference:** `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:80-120`

---

**Step 3:** HITL Approval Required

1. LangGraph interrupts at `approval_gate` node
2. Agent API returns `status: "awaiting_approval"` with `pending_approval` object
3. Dashboard shows approval card in queue
4. Operator clicks Approve

**Code Path:**
- Graph: `app/core/langgraph/graph.py` (interrupt_before=["approval_gate"])
- API: `app/api/v1/agent.py` (POST /approvals/{id}:approve)
- DB: `zakops_agent.approvals` table

---

**Step 4:** Execution After Approval

1. Dashboard calls `POST /agent/approvals/{id}:approve`
2. Agent API atomically claims approval (`WHERE status='pending'`)
3. Resumes LangGraph with `Command(resume={approved: True})`
4. Tool executes `POST /api/deals/{id}/transition` to backend
5. No-Illusions Gate: Re-fetches deal to verify stage changed

**Reference:** `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:191-221`

**VERIFIED:** Working (F-003 remediation complete)

---

### 4.3 SCENARIO C: Email → Quarantine → Deal (PARTIALLY IMPLEMENTED)

**Step 1:** Email arrives in Gmail

- Email ingestion pipeline polls Gmail IMAP
- Filters by broker domains and acquisition keywords
- **STATUS:** Code exists at `/home/zaks/scripts/email_ingestion/stages/stage_1_fetch.py`

---

**Step 2:** Email normalized and matched

- Deduplication via body_hash + message_id
- Multi-tier matching against `deal_registry.json`
- Confidence scores: 0.95 (registry match), 0.85 (alias), 0.80 (keyword)
- **STATUS:** Code exists at `/home/zaks/scripts/email_ingestion/stages/stage_3_match.py`

---

**Step 3:** New email → Quarantine

**PROBLEM:** Two different quarantine systems exist:

| System | Storage | API |
|--------|---------|-----|
| Email Ingestion | `/home/zaks/DataRoom/.deal-registry/ingest_state.db` | None (local) |
| Backend | `zakops.quarantine_items` table | `POST /api/quarantine` |

**Bridge Attempt:** `ingestion_gateway.py` was intended to POST to backend.
**STATUS:** **NOT WORKING** — cron job not active, bridge not tested.

**Reference:**
- Ingestion: `/home/zaks/scripts/email_ingestion/stages/stage_4_persist.py`
- Backend: `/home/zaks/zakops-backend/src/api/orchestration/main.py` (quarantine endpoints)

---

**Step 4:** Quarantine item approval

**Dashboard Flow (exists):**
1. Dashboard fetches `GET /api/quarantine` (pending items)
2. User sees email preview, extracted fields
3. User clicks Approve
4. Dashboard calls `POST /api/quarantine/{id}/process`

**PROBLEM:** Processing a quarantine item does NOT create a deal automatically.

```python
# POST /api/quarantine/{item_id}/process
# Just updates status to 'approved' or 'rejected'
# deal_id must be provided separately
```

**STATUS:** **NEEDS VERIFICATION** — quarantine→deal automation incomplete

---

### 4.4 SCENARIO D: Deal from Email Executor (EXISTS BUT DISCONNECTED)

**CreateDealFromEmailExecutor exists:**

```python
# /home/zaks/zakops-backend/src/actions/executors/deal_create_from_email.py
class CreateDealFromEmailExecutor(ActionExecutor):
    def execute(self, payload, ctx):
        # Creates DataRoom folder structure:
        # 01-NDA/, 02-CIM/, 03-Financials/, ..., 07-Correspondence/
        # Copies quarantine artifacts
        # Updates deal_registry.json
        # Writes deal_profile.json
```

**PROBLEM:** This executor is NOT wired to quarantine approval flow.
- It's registered as capability `deal.create_from_email`
- But no automatic trigger from `POST /api/quarantine/{id}/process`

**STATUS:** **NOT IMPLEMENTED** — executor exists but not connected

---

## 5. Scenarios & Edge Cases

### 5.1 New Deal Enters Quarantine (Happy Path)

**Expected:** Email → Quarantine → Review → Approve → Deal created
**Actual:** Email ingestion not running; manual quarantine creation only

**Evidence:**
- Query: `SELECT COUNT(*) FROM zakops.quarantine_items` returns 0
- Cron: No active cron job for email ingestion

**Status:** **NOT WORKING**

---

### 5.2 Duplicate Deal Detection

**Expected:** Prevent duplicate deals for same company
**Actual:** No automatic deduplication in backend

**Evidence:**
- `POST /api/deals` has no duplicate check on `canonical_name`
- Email ingestion has dedup via body_hash, but doesn't sync to backend

**Status:** **NOT IMPLEMENTED** in backend

---

### 5.3 Approval Flow (HITL): Approve/Reject/Timeout

**Approve Flow:**
1. Atomic claim: `UPDATE approvals SET status='claimed' WHERE status='pending' AND id=$1`
2. Execute tool
3. Mark approved

**Reject Flow:**
1. Atomic update: `UPDATE approvals SET status='rejected' WHERE status='pending' AND id=$1`
2. Resume graph with rejection
3. Agent acknowledges rejection

**Timeout (expiry):**
- `expires_at` field set on approval creation (default: 1 hour)
- **PROBLEM:** No background job to expire stale approvals
- Lazy expiry: checked only when approval is accessed

**Evidence:** `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/agent.py`

**Status:** Approve/Reject **WORKING**; Timeout **LAZY EXPIRY ONLY**

---

### 5.4 Manual User Edits from Dashboard

**Stage Transitions:** Working via `transitionDeal()`
**Deal Metadata:** `PUT /api/deals/{id}` exists
**Notes:** `POST /api/deals/{id}/notes` exists (via `addDealNote`)

**Evidence:** Dashboard imports `transitionDeal`, `addDealNote` from `@/lib/api`

**Status:** **WORKING**

---

### 5.5 Agent-Driven Updates (Tool Calls)

**Available Tools:**
| Tool | HITL Required | Status |
|------|---------------|--------|
| `get_deal` | No | WORKING |
| `search_deals` | No | NEEDS VERIFICATION (RAG dependency) |
| `transition_deal` | Yes | WORKING |

**NOT Available:**
- `create_deal` (agent cannot create deals)
- `update_deal` (agent cannot update metadata)
- `delete_deal` (agent cannot delete)

**Evidence:** `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py`

**Status:** Limited but intentional (HITL for state changes)

---

### 5.6 Missing Auth Token / Permission Denied

**Backend Authentication:**
- `X-API-Key` header required
- `APIKeyMiddleware` validates against env var

**Agent→Backend:**
- `ZAKOPS_API_KEY` env var used in headers
- On missing key: 401 Unauthorized

**Dashboard→Backend:**
- Next.js rewrites proxy to backend
- No auth (trusts internal network)

**Evidence:**
- `/home/zaks/zakops-backend/src/api/shared/middleware/auth.py`
- `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:37-42`

**Status:** **WORKING** (but dashboard has no auth)

---

### 5.7 Split-Brain DB Risk (Agent DB vs Backend DB)

**Two Separate Databases:**
1. `zakops` (backend) — deals, events, actions
2. `zakops_agent` (agent) — approvals, tool_executions, audit_log

**Risk:** Agent's approval state can diverge from backend's deal state if:
- Agent marks approval as executed
- Backend rejects transition (validation failure)
- Agent records success; backend has old state

**Mitigation (implemented):**
- No-Illusions Gate: Agent re-fetches deal after transition to verify
- Returns `phantom_success: true` if verification fails

**Evidence:** `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:206-221`

**Status:** **MITIGATED** (F-003 remediation)

---

### 5.8 "Deal Exists in DB but Not Visible in UI"

**Possible Causes:**
1. `deleted = true` (soft deleted)
2. `status != 'active'` (filtered by some views)
3. Dashboard Zod schema mismatch (safeParse fails silently)

**Verification:**
```sql
SELECT deal_id, deleted, status FROM zakops.deals WHERE deal_id = 'DL-XXXX';
```

**Evidence:** Dashboard uses `.safeParse()` which returns empty on schema mismatch

**Status:** **POSSIBLE** — investigate with DB query

---

### 5.9 "UI Shows Deal but Agent Cannot List It"

**Possible Causes:**
1. Agent API cannot reach backend (HTTP connection failure)
2. `DEAL_API_URL` misconfigured (wrong port)
3. API key missing/invalid

**Verification:**
```bash
# From agent-api container
curl -H "X-API-Key: $ZAKOPS_API_KEY" http://host.docker.internal:8091/api/deals
```

**Evidence:** `DEAL_API_URL = os.getenv("DEAL_API_URL", "http://host.docker.internal:8091")`

**Status:** **POSSIBLE** — verify connectivity

---

### 5.10 Partial Failure: Downstream Service Down

**If Backend (8091) is down:**
- Dashboard: Empty results, error toasts
- Agent: `httpx.ConnectError` → returns error JSON
- Email Ingestion: Writes to local SQLite anyway

**If RAG (8052) is down:**
- `search_deals` tool returns error
- Deal transitions unaffected

**If Agent API (8095) is down:**
- Dashboard: Chat fails
- Approvals: Cannot be processed
- Backend: Unaffected

**Evidence:** Circuit breaker in `/home/zaks/zakops-backend/src/core/agent/deal_api_client.py`

**Status:** **DEGRADED GRACEFULLY** (partial)

---

### 5.11 Retry/Idempotency Behavior

**Backend Transitions:**
- 24-hour idempotency window via `idempotency_key` in `deal_events`
- Same key → returns cached result, no state change

**Agent Tool Calls:**
- `tool_idempotency_key()` generates consistent key from args
- Prevents duplicate transitions on retry

**Evidence:**
- `/home/zaks/zakops-backend/src/core/deals/workflow.py:119-155`
- `/home/zaks/zakops-agent-api/apps/agent-api/app/core/idempotency.py`

**Status:** **WORKING**

---

### 5.12 Deletion/Archive Behavior

**Soft Delete:**
- `deleted = true` column
- Filtered from most queries
- No hard delete endpoint

**Archive Stage:**
- `stage = 'archived'` is terminal
- No transitions out allowed
- Folder remains in DataRoom

**Retention Policy:**
- **NOT IMPLEMENTED** — no automatic cleanup

**Evidence:**
- Schema: `deleted BOOLEAN DEFAULT FALSE`
- Workflow: `ARCHIVED: []` (empty transitions)

**Status:** **PARTIAL** (soft delete works, no retention)

---

## 6. Brutally Honest Gap Analysis

### GAP-001: Email Ingestion Not Running

**Title:** Email ingestion pipeline is disabled in production

**Evidence:**
- No active cron job in `/etc/cron.d/`
- `SELECT COUNT(*) FROM zakops.quarantine_items` returns 0
- Prior assessment confirms: "cron job to run the pipeline is NOT ACTIVE"

**Impact:**
- No automatic deal discovery
- All deals must be created manually
- Email-based M&A intelligence unavailable

**Severity:** P0 (Critical)

**Remediation:**
1. Enable cron job: `5 6-21 * * * zaks cd /home/zaks/scripts/email_ingestion && make ingest`
2. Verify IMAP credentials in `/home/zaks/.config/email_sync.env`
3. Test with `--dry-run` first
4. Monitor `/home/zaks/logs/email_sync.log`

---

### GAP-002: Quarantine-to-Deal Automation Missing

**Title:** Approving quarantine item does not create deal

**Evidence:**
- `POST /api/quarantine/{id}/process` only updates status
- `CreateDealFromEmailExecutor` exists but not triggered
- Dashboard quarantine approval does not call deal creation

**Impact:**
- Two-step manual process: approve quarantine → separately create deal
- High friction for operators
- Quarantine items orphaned without deals

**Severity:** P1 (High)

**Remediation:**
1. Wire `POST /api/quarantine/{id}/process` with `action=approve` to trigger `deal.create_from_email` action
2. Or: Add "Create Deal" button to quarantine approval dialog
3. Test end-to-end flow

---

### GAP-003: Three Disconnected Deal Registries

**Title:** Database, JSON registry, and DataRoom are not synchronized

**Evidence:**
- Backend uses `zakops.deals` with DL-XXXX IDs
- Email ingestion uses `deal_registry.json` with DEAL-YYYY-### IDs
- DataRoom folders have arbitrary names
- No sync mechanism between them

**Impact:**
- Deals created via email don't appear in backend
- Backend deals don't have DataRoom folders
- Document search disconnected from deal records

**Severity:** P1 (High)

**Remediation:**
1. Migrate to single source of truth (backend database)
2. Deprecate `deal_registry.json`
3. Create folders on deal creation via backend hook
4. Or: Build sync job that reconciles registries

---

### GAP-004: Agent Cannot Create Deals

**Title:** Agent has no `create_deal` tool

**Evidence:**
- Only tools: `get_deal`, `search_deals`, `transition_deal`
- `create_deal` not registered
- Intentional limitation for safety

**Impact:**
- Agent cannot automate deal discovery
- All deals require human creation
- Limits autonomous operation

**Severity:** P2 (Medium)

**Remediation:**
1. Add `create_deal` tool with HITL approval requirement
2. Or: Keep as manual-only (policy decision)

---

### GAP-005: RAG Search Integration Unverified

**Title:** `search_deals` tool depends on RAG service at 8052

**Evidence:**
- Tool calls `POST http://host.docker.internal:8052/rag/query`
- RAG service status unknown
- "pool=null at boot" note in service catalog

**Impact:**
- Deal search may fail silently
- Agent cannot find deals by content

**Severity:** P2 (Medium)

**Remediation:**
1. Verify RAG service running: `curl http://localhost:8052/health`
2. Index existing deals into RAG
3. Add health check to agent startup

---

### GAP-006: No Event Correlation

**Title:** Backend events and agent audit logs are separate

**Evidence:**
- `zakops.deal_events` captures backend changes
- `zakops_agent.audit_log` captures agent actions
- No shared `correlation_id` linking them

**Impact:**
- Cannot trace agent action → backend change
- Debugging requires cross-DB queries
- Compliance audit difficult

**Severity:** P2 (Medium)

**Remediation:**
1. Pass `trace_id` from agent through to backend
2. Store `correlation_id` in both systems
3. Build unified audit view

---

### GAP-007: Dashboard Has No Authentication

**Title:** Dashboard proxies to backend without auth

**Evidence:**
- Next.js rewrites forward requests directly
- No user session management
- Trusts internal network

**Impact:**
- Anyone on network can access all deals
- No user attribution for changes
- Security risk

**Severity:** P1 (High)

**Remediation:**
1. Add authentication middleware to dashboard
2. Pass user ID in requests to backend
3. Implement RBAC

---

### GAP-008: No Approval Expiry Background Job

**Title:** Stale approvals expire lazily only

**Evidence:**
- `expires_at` field exists on approvals
- No background job to expire them
- Only checked when approval is accessed

**Impact:**
- Stale approvals accumulate in queue
- User confusion about old requests
- Memory/performance concern at scale

**Severity:** P3 (Low)

**Remediation:**
1. Add background job to expire old approvals
2. Run every 5 minutes
3. Emit `APPROVAL_EXPIRED` audit event

---

## 7. Comparison to Prior Assessment

### 7.1 New Findings vs Prior Report

| Finding | Prior Report | This Assessment |
|---------|--------------|-----------------|
| F-003 HITL Verification | Not detailed | **NEW:** Full code trace of No-Illusions Gate implementation |
| Two-DB split-brain risk | Mentioned | **DETAILED:** Mitigation via re-fetch verification confirmed |
| Idempotency 24h window | Not specified | **NEW:** Exact implementation in workflow.py:120-155 |
| Dashboard auth gap | Not mentioned | **NEW:** No authentication on dashboard |
| Agent tool limitations | Partial | **DETAILED:** Exact tools available with HITL requirements |

### 7.2 Disagreements/Conflicts vs Prior Report

| Item | Prior Report Says | This Assessment Says | Resolution |
|------|-------------------|---------------------|------------|
| Stage validation | "CHECK constraint prevents invalid stages" | **CONFIRMED** | Verified in migration 023 |
| Quarantine automation | "NOT automatic deal creation" | **CONFIRMED** | Code inspection confirms |
| Email ingestion status | "NOT ACTIVE" | **CONFIRMED** | No cron job found |

### 7.3 Confirmed Items (Both Agree)

1. ✅ Core deal CRUD works
2. ✅ Stage transitions validated at code and DB level
3. ✅ HITL approval flow operational
4. ✅ Email ingestion pipeline exists but disabled
5. ✅ Quarantine → Deal is multi-step manual
6. ✅ Three disconnected data stores (DB, JSON, DataRoom)
7. ✅ Dashboard shows partial picture
8. ✅ No scheduling/reminders implemented

---

## 8. Verification Plan

### 8.1 Stage Transition Verification

```bash
# Create test deal
curl -X POST http://localhost:8091/api/deals \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"canonical_name": "Test Deal", "stage": "inbound"}' | jq

# Capture deal_id from response, then transition
DEAL_ID="DL-XXXX"
curl -X POST "http://localhost:8091/api/deals/${DEAL_ID}/transition" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"new_stage": "screening", "reason": "Test transition"}' | jq

# Verify in database
psql -h localhost -p 5432 -U dealengine zakops -c \
  "SELECT deal_id, stage, updated_at FROM zakops.deals WHERE deal_id = '${DEAL_ID}';"

# Verify event recorded
psql -h localhost -p 5432 -U dealengine zakops -c \
  "SELECT event_type, payload FROM zakops.deal_events WHERE deal_id = '${DEAL_ID}' ORDER BY created_at DESC LIMIT 1;"
```

### 8.2 HITL Approval Verification

```bash
# Invoke agent with transition request
curl -X POST http://localhost:8095/agent/invoke \
  -H "Content-Type: application/json" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -d '{"actor_id": "test-user", "message": "Move deal DL-0001 to screening"}' | jq

# Check for pending approval
psql -h localhost -p 5432 -U agent zakops_agent -c \
  "SELECT id, tool_name, status FROM approvals WHERE status = 'pending' ORDER BY created_at DESC LIMIT 1;"

# Approve it
APPROVAL_ID="..."
curl -X POST "http://localhost:8095/agent/approvals/${APPROVAL_ID}:approve" \
  -H "Content-Type: application/json" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -d '{"actor_id": "test-approver"}' | jq
```

### 8.3 Quarantine Flow Verification

```bash
# Check quarantine items
curl http://localhost:8091/api/quarantine | jq

# Create test quarantine item
curl -X POST http://localhost:8091/api/quarantine \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"sender": "broker@example.com", "subject": "New Deal: Acme Corp", "message_id": "test-123"}' | jq

# Process it
ITEM_ID="..."
curl -X POST "http://localhost:8091/api/quarantine/${ITEM_ID}/process" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"status": "approved"}' | jq

# Check if deal was created (expected: NO automatic creation)
curl http://localhost:8091/api/deals | jq '.[] | select(.canonical_name == "Acme Corp")'
```

### 8.4 Email Ingestion Verification

```bash
# Check if cron job exists
cat /etc/cron.d/dataroom-automation 2>/dev/null || echo "No cron file"

# Manual dry-run
cd /home/zaks/scripts/email_ingestion && python -m email_ingestion.cli --dry-run --days 1

# Check SQLite for processed emails
sqlite3 /home/zaks/DataRoom/.deal-registry/ingest_state.db "SELECT COUNT(*) FROM processed_emails;"
```

### 8.5 Dashboard Deal Visibility

```bash
# Verify dashboard is running
curl -s http://localhost:3003/api/deals | jq 'length'

# Compare with backend
curl -s http://localhost:8091/api/deals | jq 'length'

# If counts differ, check Zod schema in dashboard
grep -r "dealSchema" /home/zaks/zakops-agent-api/apps/dashboard/src/
```

---

## Self-Audit Checklist

- [x] Every stage/state mentioned exists in code (or is marked NOT IMPLEMENTED)
- [x] Every scenario includes evidence refs or is marked NEEDS VERIFICATION
- [x] Gap list is actionable and prioritized
- [x] Comparison to prior assessment completed
- [x] Verification commands provided for each major claim

---

*Assessment generated from actual code inspection on 2026-02-04. No documentation assumptions.*
