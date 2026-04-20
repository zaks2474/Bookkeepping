# MISSION: INTEGRATION-PHASE2-BUILD-001
## Delegation Framework — Lease-Based Task Claiming, Research Artifacts, Dashboard Delegate Button
## Date: 2026-02-17
## Classification: Feature Build (Integration)
## Prerequisite: INTEGRATION-PHASE1-BUILD-001 (Complete 2026-02-17, 9/9 AC PASS)
## Successor: QA-IP2-VERIFY-001 (Phase 2 QA) → INTEGRATION-PHASE3-BUILD-001 (Bi-directional Communication)

---

## Mission Objective

Build the **Delegation Framework** (Integration Spec v1.0 §14, Items 8-14) enabling the full delegation round-trip between ZakOps and the LangSmith Exec Agent. This is the second of three integration phases.

**What this mission does:**
- Adds lease-based claiming to the existing `delegated_tasks` table so the LangSmith agent can atomically claim work with race-condition protection
- Registers the 16 integration action types (from Integration Spec §5) with default lease durations
- Adds two new MCP bridge tools (`zakops_claim_action`, `zakops_renew_action_lease`) and expands two existing ones
- Adds a "Delegate to Agent" button on the Dashboard quarantine page
- Proves the write path end-to-end with golden tests T5, T9, T10

**What this mission is NOT:**
- NOT building Pipeline B (research execution) — that's the LangSmith agent's domain
- NOT implementing Gmail back-labeling or event polling — that's Phase 3
- NOT building the full research executor — only the delegation hand-off and result reporting
- NOT modifying the existing Kinetic Action Engine (SQLite store.py) — that's internal-only

**Source material:**
- `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` (1,075 lines, locked architectural agreement)
- `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md` (Phase 1 results, 9/9 AC)
- Integration Spec §5 (16 action types), §6 (payload schemas), §8 (Pipeline B), §14 (build plan Items 8-14)

---

## Context

### Current State of `delegated_tasks` Infrastructure

The `delegated_tasks` table (migration 035) already provides the delegation primitive:

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key (auto-generated) |
| deal_id | VARCHAR(50) | FK to deals (nullable, ON DELETE SET NULL) |
| task_type | VARCHAR(100) | Task category (currently 8 types, needs 16) |
| status | VARCHAR(30) | FSM: pending→queued→executing→completed/failed/dead_letter |
| assigned_to | VARCHAR(255) | Default 'langsmith_agent' |
| context | JSONB | Task input parameters |
| result | JSONB | Task output |
| max_attempts / attempt_count | INT | Retry logic |
| correlation_id | VARCHAR(100) | Cross-system tracing |

**What's MISSING for Phase 2:**
- `lease_owner_id`, `claimed_at`, `lease_expires_at`, `lease_heartbeat_at` — for atomic claiming
- `executor_id`, `langsmith_run_id`, `langsmith_trace_url` — for Identity Contract compliance (Spec §10)
- `research_id` — for linking research artifacts
- `artifacts` (JSONB) — for storing artifact metadata on completion

### Existing API Endpoints (all in `main.py`):

| Endpoint | Line | Status |
|----------|------|--------|
| `GET /api/deals/{id}/tasks` | 3377 | Works — lists tasks per deal |
| `POST /api/deals/{id}/tasks` | 3422 | Works — feature-flag gated (`delegate_actions=false`) |
| `POST /api/tasks/{id}/result` | 3493 | Works — basic result with retry/dead_letter |
| `POST /api/tasks/{id}/retry` | 3587 | Works — re-queues failed tasks |
| `POST /api/tasks/{id}/confirm` | 3622 | Works — operator confirms gated tasks |
| **`POST /api/tasks/{id}/claim`** | — | **MISSING — needs building** |
| **`POST /api/tasks/{id}/renew-lease`** | — | **MISSING — needs building** |
| **`GET /api/delegation/tasks`** | — | **MISSING — deal-agnostic task listing** |
| **`GET /api/delegation/types`** | — | **MISSING — action type registry** |

### Current `DelegatedTaskCreate` validator (line 3354):
Only allows 8 types: `send_email, draft_email, research_company, research_broker, analyze_document, schedule_meeting, follow_up, custom`. **Needs expanding to 16 integration types.**

### MCP Bridge Status (21 tools):
- `zakops_create_action` (server.py:1029) — Posts to backend but targets wrong endpoint pattern
- `zakops_report_task_result` (server.py:1281) — Posts to `/api/tasks/{id}/result`, works
- `zakops_list_actions` — Lists via `/api/actions`, doesn't include delegation tasks
- **Need 2 new tools:** `zakops_claim_action`, `zakops_renew_action_lease`

---

## Glossary

| Term | Definition |
|------|-----------|
| Delegation round-trip | Operator creates task → agent claims → agent executes → agent reports result |
| Lease | Time-boxed lock on a task. Agent must renew before expiry or task becomes re-claimable |
| `delegated_tasks` | PostgreSQL table in `zakops` schema for cross-agent task coordination |
| Integration action types | 16 task categories from Spec §5 (EMAIL_TRIAGE.*, RESEARCH.*, DOCUMENT.*, etc.) |
| Identity Contract | Spec §10 — every write must include executor_id, correlation_id, LangSmith tracing |
| Golden tests | T5 (round-trip), T9 (race condition), T10 (artifact→RAG) from Spec §13 |
| Pipeline B | Spec §8.2 — Research execution pipeline (agent-side, NOT built here) |

---

## Architectural Constraints

- **`delegated_tasks` is the coordination backbone** — per Spec §15 Decision #3. Do NOT merge with the `actions` table or SQLite store. These are separate systems.
- **Atomic lease claiming** — `SELECT ... FOR UPDATE` with status+lease check. Two simultaneous claims → exactly one wins, other gets 409.
- **Identity Contract compliance** — every task write operation stores `executor_id`, `correlation_id`, `langsmith_run_id`, `langsmith_trace_url` (per Spec §10).
- **Feature flag gating** — `delegate_actions` flag (currently `false`) gates task creation. Migration does NOT enable it.
- Per standing constraints: `transition_deal_state()` choke point, `Promise.allSettled` for dashboard data fetching, Surface 9 compliance, port 8090 FORBIDDEN, generated files never edited.

---

## Anti-Pattern Examples

### WRONG: Non-atomic claim (race condition)
```python
task = await conn.fetchrow("SELECT * FROM delegated_tasks WHERE id = $1", task_id)
if task["status"] == "queued":  # Another agent could claim between SELECT and UPDATE
    await conn.execute("UPDATE delegated_tasks SET status = 'executing' WHERE id = $1", task_id)
```

### RIGHT: Atomic claim with SELECT FOR UPDATE
```python
async with conn.transaction():
    task = await conn.fetchrow(
        "SELECT * FROM zakops.delegated_tasks WHERE id = $1 FOR UPDATE", task_id
    )
    if task["status"] not in ("pending", "queued"):
        raise HTTPException(409, "Task already claimed")
    if task["lease_expires_at"] and task["lease_expires_at"] > datetime.now(timezone.utc):
        raise HTTPException(409, "Active lease exists")
    await conn.execute(
        "UPDATE zakops.delegated_tasks SET status='executing', lease_owner_id=$2, claimed_at=NOW(), lease_expires_at=NOW() + interval '$3 seconds' WHERE id=$1",
        task_id, executor_id, lease_seconds
    )
```

### WRONG: Clearing lease on any result submission
```python
# Clears lease even if the submitter isn't the lease holder
await conn.execute("UPDATE delegated_tasks SET lease_owner_id=NULL WHERE id=$1", task_id)
```

### RIGHT: Verify lease ownership before clearing
```python
if task["lease_owner_id"] and task["lease_owner_id"] != body.executor_id:
    raise HTTPException(403, "Only the lease holder can submit results")
await conn.execute("UPDATE delegated_tasks SET lease_owner_id=NULL, lease_expires_at=NULL WHERE id=$1", task_id)
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Claim endpoint not truly atomic — race condition in production | HIGH | Double execution of same task | T9 golden test explicitly tests concurrent claims; `FOR UPDATE` row lock mandatory |
| 2 | `DelegatedTaskCreate` validator rejects new integration types | MEDIUM | Bridge can't create tasks | Phase 1 explicitly expands validator; gate verifies all 16 types accepted |
| 3 | Bridge `zakops_create_action` still targets wrong endpoint after changes | MEDIUM | Tasks created in wrong table | Explicitly retarget to `/api/deals/{id}/tasks` or `/api/delegation/tasks` |
| 4 | Dashboard delegate dialog doesn't show task types (API type mismatch) | MEDIUM | UX broken | `make sync-types` gate after backend changes, browser verification mandatory |
| 5 | Lease expiry orphans tasks (agent crashes, no cleanup) | LOW | Tasks stuck in 'executing' forever | Document: future background job to expire stale leases (out of scope for this mission) |

---

## Phase 0 — Discovery & Baseline

**Complexity:** S | **Touch points:** 0 files

### Tasks
- P0-01: **Run `make validate-local`** — capture baseline
  - **Checkpoint:** Must pass before any changes
- P0-02: **Verify `delegate_actions` flag** — `SELECT name, enabled FROM zakops.feature_flags WHERE name = 'delegate_actions'` → should be `false`
- P0-03: **Verify `delegated_tasks` schema** — confirm current columns match expectations (no lease columns yet)
- P0-04: **Identify affected contract surfaces:**
  - Surface 1 (Backend → Dashboard) — new API types from expanded endpoints
  - Surface 15 (MCP Bridge Tool Interface) — 2 new tools
  - Surface 16 (Email Triage Injection) — no regression check

### Gate P0
- `make validate-local` passes at baseline
- `delegated_tasks` table confirmed without lease columns
- `delegate_actions` flag confirmed `false`

---

## Phase 1 — Database Migration + Action Type Registry

**Complexity:** M | **Touch points:** 3 new files, 1 modified

### Blast Radius
- **Services affected:** Backend (schema change)
- **Pages affected:** None (additive columns)
- **Downstream consumers:** Bridge tools (after Phase 3), Dashboard (after Phase 4)

### Tasks
- P1-01: **Create migration** `apps/backend/db/migrations/036_delegation_leases.sql`
  - Add 9 columns: `lease_owner_id`, `claimed_at`, `lease_expires_at`, `lease_heartbeat_at`, `executor_id`, `langsmith_run_id`, `langsmith_trace_url`, `research_id`, `artifacts`
  - Add index `idx_dt_claimable` on (assigned_to, status, lease_expires_at) WHERE status IN ('pending','queued')
  - Add index `idx_dt_lease_expires` on (lease_expires_at) WHERE status = 'executing'
  - **Checkpoint:** Run migration, verify columns exist

- P1-02: **Create rollback** `apps/backend/db/migrations/036_delegation_leases_rollback.sql`

- P1-03: **Create action type registry** `apps/backend/src/api/orchestration/delegation_types.py`
  - `INTEGRATION_ACTION_TYPES` dict with 16 types from Spec §5
  - Each entry: `{lease_seconds, category, requires_deal, description}`
  - Helper functions: `get_default_lease(task_type)`, `is_valid_integration_type(task_type)`
  - Lease durations per Spec §5.1: EMAIL_TRIAGE=300, RESEARCH=1800, DEAL.INTAKE=300, DEAL.MONITOR=600, DOCUMENT=900, DRAFT=300, SYNC=120, OPS=600

- P1-04: **Expand `DelegatedTaskCreate.validate_task_type()`** in `main.py` line 3353
  - Accept all 16 integration types PLUS existing 8 legacy types
  - Import from `delegation_types.py`

- P1-05: **Expand `DelegatedTaskResult` model** in `main.py` line 3363
  - Add optional fields: `research_id: str | None`, `artifacts: list[dict] | None`, `langsmith_run_id: str | None`, `langsmith_trace_url: str | None`, `executor_id: str | None`

- P1-06: **Add `GET /api/delegation/types` endpoint** in `main.py`
  - Returns the 16 integration action types with lease defaults and metadata

### Decision Tree
- **IF** migration fails due to existing column: Use `ADD COLUMN IF NOT EXISTS` (safe)
- **IF** existing `task_type` CHECK constraint blocks new types: Drop constraint if exists, rely on Pydantic validation
  - Note: Current table has no CHECK on `task_type` (only on `status` and `priority`)

### Rollback
1. Run `036_delegation_leases_rollback.sql`
2. Revert `main.py` model changes
3. `make validate-local`

### Gate P1
- All 9 new columns exist: `SELECT column_name FROM information_schema.columns WHERE table_schema='zakops' AND table_name='delegated_tasks' AND column_name IN ('lease_owner_id','claimed_at','lease_expires_at','lease_heartbeat_at','executor_id','langsmith_run_id','langsmith_trace_url','research_id','artifacts')`
- `GET /api/delegation/types` returns 16 types
- Existing task creation still works with legacy types

---

## Phase 2 — Backend Claim + Renew-Lease + Expanded Result Endpoints

**Complexity:** L | **Touch points:** 1 file (main.py)

### Blast Radius
- **Services affected:** Backend API
- **Pages affected:** None yet (dashboard integration in Phase 4)
- **Downstream consumers:** MCP bridge (Phase 3), LangSmith agent

### Tasks
- P2-01: **Add `POST /api/tasks/{task_id}/claim` endpoint**
  - Request model: `ClaimTaskRequest(executor_id: str, lease_seconds: int | None, correlation_id: str | None, langsmith_run_id: str | None)`
  - Atomic: `SELECT ... FOR UPDATE` → verify status IN ('pending','queued') → verify no active lease → UPDATE
  - Sets: `status='executing', lease_owner_id, claimed_at=NOW(), lease_expires_at=NOW()+interval, started_at=COALESCE(started_at, NOW()), executor_id, langsmith_run_id`
  - Default lease: lookup from `INTEGRATION_ACTION_TYPES[task_type].lease_seconds`
  - Records deal event `task_claimed` (if deal_id present)
  - Returns 200 `{task_id, status, lease_expires_at, lease_seconds_remaining}` or 409 Conflict
  - **Checkpoint:** curl test with two sequential claims, second gets 409

- P2-02: **Add `POST /api/tasks/{task_id}/renew-lease` endpoint**
  - Request model: `RenewLeaseRequest(executor_id: str, lease_seconds: int | None)`
  - Verify: `lease_owner_id == executor_id` AND `status = 'executing'`
  - Update: `lease_expires_at = NOW() + interval, lease_heartbeat_at = NOW()`
  - Returns 200 `{task_id, new_lease_expires_at, lease_seconds_remaining}` or 409
  - **Checkpoint:** curl test renew after claim

- P2-03: **Expand `submit_task_result` (line 3493)**
  - Store new fields from expanded `DelegatedTaskResult`: `executor_id`, `langsmith_run_id`, `langsmith_trace_url`, `research_id`, `artifacts`
  - Verify lease ownership if `lease_owner_id` is set (403 if mismatch)
  - Clear lease on completion: `SET lease_owner_id=NULL, lease_expires_at=NULL, lease_heartbeat_at=NULL`
  - Enhanced deal event includes artifact metadata
  - **Checkpoint:** curl test result submission with artifacts

- P2-04: **Add `GET /api/delegation/tasks` endpoint** (deal-agnostic listing)
  - Query params: `status`, `assigned_to`, `task_type`, `claimable_only: bool` (filters to pending/queued with no active lease), `limit`
  - Returns `{tasks: [...], count: N}`
  - Agent uses this to poll for claimable work
  - **Checkpoint:** curl test listing with filters

- P2-05: **Add `POST /api/delegation/tasks` endpoint** (deal-optional creation)
  - Like `POST /api/deals/{id}/tasks` but `deal_id` is optional in the body
  - Feature-flag gated (`delegate_actions`)
  - For deal-less types: SYNC.*, OPS.*
  - **Checkpoint:** curl create task without deal_id

### Rollback
1. Revert main.py endpoint additions (preserve model expansions from Phase 1)
2. `make validate-local`

### Gate P2
- `POST /api/tasks/{id}/claim` returns 200 with lease; second claim returns 409
- `POST /api/tasks/{id}/renew-lease` extends `lease_expires_at`
- `POST /api/tasks/{id}/result` with artifacts stores them and clears lease
- `GET /api/delegation/tasks?claimable_only=true` returns only unclaimed tasks
- `POST /api/delegation/tasks` creates task without deal_id

---

## Phase 3 — MCP Bridge Tool Additions

**Complexity:** M | **Touch points:** 2 files

### Blast Radius
- **Services affected:** MCP Bridge (port 9100)
- **Pages affected:** None
- **Downstream consumers:** LangSmith agent, integration manifest

### Tasks
- P3-01: **Add `zakops_claim_action` tool** in `server.py`
  - Params: `task_id: str, executor_id: str, lease_seconds: int | None, correlation_id: str | None, langsmith_run_id: str | None`
  - Posts to `POST {DEAL_API_URL}/api/tasks/{task_id}/claim`
  - Returns: `{task_id, status, lease_expires_at, lease_seconds_remaining}` or `{error: "..."}`
  - Risk level: MEDIUM (state change)
  - **Checkpoint:** Verify tool appears in `tools/list`

- P3-02: **Add `zakops_renew_action_lease` tool** in `server.py`
  - Params: `task_id: str, executor_id: str, lease_seconds: int | None`
  - Posts to `POST {DEAL_API_URL}/api/tasks/{task_id}/renew-lease`
  - Risk level: MEDIUM
  - **Checkpoint:** Verify tool callable via MCP

- P3-03: **Expand `zakops_list_actions` tool**
  - Add `assigned_to: Optional[str]` parameter
  - Add `include_delegated: bool = False` parameter — when True, also queries `/api/delegation/tasks`
  - **Checkpoint:** MCP call with assigned_to filter returns filtered results

- P3-04: **Expand `zakops_report_task_result` tool**
  - Add params: `research_id, artifacts: list[dict], langsmith_run_id, langsmith_trace_url, executor_id`
  - Include in POST payload to `/api/tasks/{id}/result`
  - **Checkpoint:** MCP call with artifacts parameter succeeds

- P3-05: **Fix `zakops_create_action` tool** — verify it targets `/api/deals/{deal_id}/tasks` or `/api/delegation/tasks` correctly
  - Currently creates via unknown endpoint — retarget to work with delegation system
  - **Checkpoint:** MCP create action → task appears in `GET /api/delegation/tasks`

- P3-06: **Update `zakops_get_manifest` tool**
  - Add `zakops_claim_action` and `zakops_renew_action_lease` to `supervised_tools` list
  - Update `supported_action_types` to include all 16 integration types
  - **Checkpoint:** Manifest shows correct tool count and action types

- P3-07: **Update `agent_contract.py`**
  - Add `zakops_claim_action` ToolDefinition (MEDIUM risk, requires_approval=False)
  - Add `zakops_renew_action_lease` ToolDefinition (MEDIUM risk, requires_approval=False)
  - Update system prompt delegation section with new tools
  - **Checkpoint:** Contract validates

- P3-08: **Restart MCP bridge** — kill old process, start new one, verify tool count
  - Remember: Bridge runs as bare Python (NOT Docker), user `zaks`

### Rollback
1. Revert server.py and agent_contract.py
2. Restart bridge with old code
3. Verify 21 tools restored

### Gate P3
- MCP `tools/list` shows 23 tools (21 existing + claim + renew_lease)
- `zakops_claim_action` callable via JSON-RPC → returns 200 or 409
- `zakops_get_manifest` → `bridge_tool_count: 23`, `supervised_tools` includes new tools
- `make validate-surface15` passes

---

## Phase 4 — Dashboard "Delegate to Agent" Button

**Complexity:** M | **Touch points:** 3 files

### Blast Radius
- **Services affected:** Dashboard (Next.js)
- **Pages affected:** Quarantine page, Deal detail page
- **Downstream consumers:** Operator UX

### Tasks
- P4-01: **Add API functions** in `apps/dashboard/src/lib/api.ts`
  - `createDelegatedTask(params: {deal_id?, task_type, title, description?, context?, priority?, assigned_to?})` → POST `/api/delegation/tasks`
  - `listDelegatedTasks(filters: {status?, assigned_to?, task_type?, limit?})` → GET `/api/delegation/tasks`
  - `getDelegationTypes()` → GET `/api/delegation/types`
  - Use existing error handling patterns (normalizeError, Promise.allSettled wrapper)

- P4-02: **Add "Delegate" button to quarantine page** in `apps/dashboard/src/app/quarantine/page.tsx`
  - Location: alongside Approve/Reject/Escalate buttons (line ~800-812)
  - Button: "Delegate" with Send icon, secondary variant
  - Opens delegation dialog on click

- P4-03: **Build delegation dialog** (inline in quarantine page or extracted component)
  - Form fields: task_type (dropdown from delegation types API), priority (low/medium/high/critical), notes (optional textarea)
  - Pre-fills: context from quarantine item (email_subject, sender, classification, company_name)
  - On submit: calls `createDelegatedTask()` with quarantine item context
  - Success: toast notification, optionally marks quarantine item as delegated
  - Error: toast with error details

- P4-04: **Add delegation option in deal detail page** `apps/dashboard/src/app/deals/[id]/page.tsx`
  - In tasks/actions tab: "Delegate to Agent" button
  - Same dialog pattern but pre-fills deal_id

- P4-05: **Run type sync chain**
  ```
  make update-spec → make sync-types → npx tsc --noEmit
  ```
  - **Checkpoint:** TypeScript compiles with new API types

### Rollback
1. Revert quarantine page and api.ts changes
2. `npx tsc --noEmit` still passes

### Gate P4
- Browser: Quarantine page → select item → "Delegate" button visible
- Dialog opens with task type dropdown (16 types)
- Submit creates task → toast confirmation
- `make validate-local` passes

---

## Dependency Graph

```
Phase 0 (Discovery)
    │
    ▼
Phase 1 (DB Migration + Type Registry)
    │
    ├──────────────────────────┐
    ▼                          ▼
Phase 2 (Backend Endpoints)    Phase 4a (Dashboard API functions)
    │                          │ (needs type sync from P2)
    ▼                          │
Phase 3 (Bridge Tools)         │
    │                          │
    ├──────────────────────────┘
    ▼
Phase 4b-d (Dashboard UI)
    │
    ▼
Phase 5 (Contract Sync + Validation)
    │
    ▼
Phase 6 (Golden Tests)
```

---

## Phase 5 — Contract Surface Sync + Validation

**Complexity:** S | **Touch points:** 0 new files

### Tasks
- P5-01: **Run sync chain**
  ```bash
  make update-spec            # Refresh backend OpenAPI (needs backend running)
  make sync-types             # Backend → Dashboard TS types
  make sync-all-types         # All pipelines
  npx tsc --noEmit            # TypeScript compilation
  ```
- P5-02: **Run surface validators**
  ```bash
  make validate-surface15     # MCP Bridge Tool Interface
  make validate-surface16     # Email Triage Injection (no regression)
  make validate-local         # Full offline validation
  ```
- P5-03: **Verify no regression on Phase 1 pipeline** — quarantine item `69223113-4528-43fb-97a6-5c67d597bb7f` still accessible, MCP tools still return dicts

### Gate P5
- `make validate-local` passes
- `make validate-surface15` and `validate-surface16` both PASS
- `npx tsc --noEmit` zero errors
- Phase 1 quarantine item still accessible

---

## Phase 6 — Golden Tests + Bookkeeping

**Complexity:** M | **Touch points:** 1 new file

### Tasks
- P6-01: **Create test file** `apps/backend/tests/test_delegation_e2e.py`

- P6-02: **T5 — Full Delegation Round-Trip**
  1. Enable `delegate_actions` flag
  2. Create `RESEARCH.COMPANY_PROFILE` task via `POST /api/delegation/tasks` with deal_id
  3. Verify task in `GET /api/delegation/tasks?status=pending`
  4. Claim via `POST /api/tasks/{id}/claim` with executor_id
  5. Verify status=executing, lease set, claimed_at set
  6. Report result via `POST /api/tasks/{id}/result` with artifacts + research_id
  7. Verify status=completed, lease cleared, deal event recorded

- P6-03: **T9 — Concurrent Claim Race**
  1. Create one queued task
  2. Two concurrent `POST /api/tasks/{id}/claim` with different executor_ids (asyncio.gather)
  3. Exactly one gets 200, other gets 409
  4. DB shows single lease_owner_id on the row

- P6-04: **T10 — Research Artifact → RAG (if services up)**
  - **IF** RAG service running: Write artifact to deal folder → reindex → query → verify
  - **ELSE:** Mark as SKIP with note "RAG not running — test manually when available"

- P6-05: **Update CHANGES.md** in `/home/zaks/bookkeeping/CHANGES.md`

- P6-06: **Final `make validate-local`** — the definitive pass

### Gate P6
- T5 PASS (round-trip proven)
- T9 PASS (race condition safe)
- T10 PASS or SKIP (RAG-dependent)
- CHANGES.md updated
- `make validate-local` passes

---

## Acceptance Criteria

### AC-1: Database Schema
`delegated_tasks` has 9 new columns (lease_owner_id, claimed_at, lease_expires_at, lease_heartbeat_at, executor_id, langsmith_run_id, langsmith_trace_url, research_id, artifacts) and 2 new indexes.

### AC-2: Action Type Registry
`GET /api/delegation/types` returns 16 integration action types with correct lease durations per Spec §5.1. `DelegatedTaskCreate` accepts all 16 types.

### AC-3: Atomic Claim
`POST /api/tasks/{id}/claim` atomically claims with `SELECT FOR UPDATE`. Second claim returns 409 Conflict. Lease set correctly.

### AC-4: Lease Renewal
`POST /api/tasks/{id}/renew-lease` extends lease for current holder only. Non-holder gets 409.

### AC-5: Expanded Result
`POST /api/tasks/{id}/result` stores artifacts, research_id, LangSmith tracing fields. Clears lease on completion.

### AC-6: Bridge Tools
`zakops_claim_action` and `zakops_renew_action_lease` callable via MCP bridge. Bridge tool count = 23. Manifest updated.

### AC-7: Dashboard Delegate
Quarantine page has "Delegate to Agent" button. Dialog shows 16 task types. Submission creates delegated task.

### AC-8: Contract Surfaces
`make validate-local`, `make validate-surface15`, `make validate-surface16` all PASS. TypeScript compiles.

### AC-9: Golden Tests
T5 (delegation round-trip) PASS. T9 (concurrent claim race) PASS. T10 (artifact→RAG) PASS or documented SKIP.

### AC-10: No Regressions
Phase 1 Pipeline A still works. Existing quarantine, actions, and deal pages unaffected.

### AC-11: Bookkeeping
CHANGES.md updated with all Phase 2 changes.

---

## Guardrails

1. **Scope fence:** Do NOT implement Pipeline B execution logic, Gmail back-labeling, or event polling — those are Phase 3 / LangSmith domain
2. **Generated files:** Do NOT edit `*.generated.ts` or `*_models.py` — per contract surface discipline
3. **Migration safety:** Do NOT modify existing migration files (033-035). Only create new 036
4. **Feature flag:** Do NOT enable `delegate_actions` flag in migration — leave as `false`, enable only in test/golden-test context
5. **Existing action engine:** Do NOT modify SQLite store.py or executors — those are internal-only
6. **WSL safety:** `sed -i 's/\r$//'` on new .sh files; `sudo chown zaks:zaks` on files under `/home/zaks/`
7. **Surface 9 compliance:** Dashboard changes follow design system rules
8. **Identity Contract:** All new write endpoints store executor_id + correlation_id per Spec §10
9. **Port 8090 FORBIDDEN** — per standing rules
10. **Bridge restart:** MCP bridge is bare Python process (NOT Docker) — kill pid, restart with env vars as user `zaks`

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I verify the `delegated_tasks` table doesn't already have lease columns?"
- [ ] "Did I confirm `delegate_actions` flag is `false`?"

### After Phase 1 (Migration + Registry):
- [ ] "Did the migration run successfully? Are all 9 columns present?"
- [ ] "Does `GET /api/delegation/types` return exactly 16 types?"
- [ ] "Can I still create tasks with legacy types (send_email, custom)?"

### After Phase 2 (Endpoints):
- [ ] "Does a second claim correctly return 409?"
- [ ] "Does result submission clear the lease?"
- [ ] "Does `GET /api/delegation/tasks?claimable_only=true` exclude claimed tasks?"

### After Phase 3 (Bridge):
- [ ] "Did I restart the bridge as bare Python process (not Docker restart)?"
- [ ] "Does `tools/list` show 23 tools?"
- [ ] "Does the manifest include new tools in supervised tier?"

### Before marking COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I run `make update-spec → make sync-types → npx tsc --noEmit`?"
- [ ] "Are all golden tests passing?"

---

## File Paths Reference

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `apps/backend/db/migrations/036_delegation_leases.sql` | P1 | Add lease columns to delegated_tasks |
| `apps/backend/db/migrations/036_delegation_leases_rollback.sql` | P1 | Rollback migration |
| `apps/backend/src/api/orchestration/delegation_types.py` | P1 | 16 integration action types registry |
| `apps/backend/tests/test_delegation_e2e.py` | P6 | Golden tests T5, T9, T10 |

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `apps/backend/src/api/orchestration/main.py` | P1-P2 | Expand models, add 5 new endpoints (claim, renew, delegation tasks CRUD, types) |
| `apps/agent-api/mcp_bridge/server.py` | P3 | Add 2 new tools, expand 3 existing, update manifest |
| `apps/agent-api/mcp_bridge/agent_contract.py` | P3 | Add 2 ToolDefinitions, update system prompt |
| `apps/dashboard/src/app/quarantine/page.tsx` | P4 | Add Delegate button + dialog |
| `apps/dashboard/src/lib/api.ts` | P4 | Add delegation API functions |
| `apps/dashboard/src/app/deals/[id]/page.tsx` | P4 | Add Delegate option in tasks tab |

### Files to Read (do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` | Authoritative spec for action types, payloads, pipelines |
| `apps/backend/db/migrations/035_delegated_tasks.sql` | Reference for existing table schema |
| `apps/backend/src/actions/engine/store.py` | Reference for claim_action_lock pattern (SQLite) |
| `apps/agent-api/mcp_bridge/agent_contract.py` | Existing tool manifest pattern |

---

## Stop Condition

This mission is DONE when:
- All 11 AC pass
- `make validate-local` passes
- `make validate-surface15` and `validate-surface16` pass
- Golden tests T5, T9, (T10) pass
- CHANGES.md updated
- All changes committed

Do NOT proceed to: Phase 3 (Bi-directional Communication), Pipeline B execution, Gmail back-labeling, or production deployment of `delegate_actions=true`.

---

<!-- Adopted from Improvement Area IA-2 (Crash Recovery) -->
## Crash Recovery

If resuming after a crash:
1. `git log --oneline -5` — check what's already committed
2. `make validate-local` — see if codebase is in a good state
3. Check `delegated_tasks` columns — determine if Phase 1 migration ran
4. Check backend endpoints — curl `/api/delegation/types` to see if Phase 1 is complete
5. Check bridge tool count — curl manifest to see if Phase 3 is complete

---

*End of Mission Prompt — INTEGRATION-PHASE2-BUILD-001*
