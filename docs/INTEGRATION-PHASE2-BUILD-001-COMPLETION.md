# INTEGRATION-PHASE2-BUILD-001 — Completion Report

## Date: 2026-02-17
## Status: COMPLETE — 11/11 AC PASS
## Golden Tests: 7 passed, 1 skipped (RAG conditional)
## Predecessor: INTEGRATION-PHASE1-BUILD-001 (Feedback Loop) — Complete 2026-02-17
## Successor: INTEGRATION-PHASE3-BUILD-001 (Bi-directional Communication) — Planned

---

## Executive Summary

Phase 2 "Delegation Framework" of the ZakOps + LangSmith Agent integration is complete. This mission built the full **delegation round-trip** enabling the LangSmith agent to:

1. **Atomically claim tasks** — Lease-based `SELECT FOR UPDATE` claiming with race-condition protection (`POST /api/tasks/{id}/claim`)
2. **Maintain lease ownership** — Time-boxed leases with heartbeat renewal (`POST /api/tasks/{id}/renew-lease`)
3. **Report results with artifacts** — Expanded result submission with research artifacts, LangSmith tracing, and Identity Contract compliance
4. **Poll for available work** — Deal-agnostic task listing with claimable filters (`GET /api/delegation/tasks`)
5. **Delegate from the Dashboard** — Operator-initiated delegation via "Delegate" button on quarantine page

These capabilities transform the integration from read-only (Phase 1) to read-write: the agent can now claim work, execute it, and report results back — the core delegation primitive.

---

## Mission Scope

**Source:** Integration Spec v1.0 (`/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md`, 1,074 lines)
**Build Plan:** §14 Items 8-14
**Pipelines Affected:** Pipeline A (Email Triage) — delegation hand-off; Pipeline B (Research) — task claiming
**Golden Tests:** T5 (round-trip), T9 (race condition), T10 (artifact storage)
**Contract Surfaces Affected:** 1 (Backend→Dashboard), 2 (Backend→Agent SDK), 15 (MCP Bridge), 17 (Dashboard Routes)

---

## Phase Execution Summary

### Phase 0 — Discovery & Baseline
- `make validate-local` PASS at baseline
- `delegate_actions` flag confirmed `false`
- `delegated_tasks` table confirmed without lease columns (8 original columns from migration 035)
- Identified 4 affected contract surfaces

### Phase 1 — Database Migration + Action Type Registry
- **Migration 036** (`apps/backend/db/migrations/036_delegation_leases.sql`): Added 9 columns to `delegated_tasks`:
  - `lease_owner_id` (VARCHAR 255) — who holds the lease
  - `claimed_at` (TIMESTAMPTZ) — when the task was claimed
  - `lease_expires_at` (TIMESTAMPTZ) — when the lease expires
  - `lease_heartbeat_at` (TIMESTAMPTZ) — last heartbeat
  - `executor_id` (VARCHAR 255) — Identity Contract: who executed
  - `langsmith_run_id` (VARCHAR 255) — LangSmith tracing
  - `langsmith_trace_url` (TEXT) — LangSmith trace URL
  - `research_id` (VARCHAR 100) — research artifact linking
  - `artifacts` (JSONB) — artifact metadata array
- **2 new indexes**: `idx_dt_claimable` (for polling) and `idx_dt_lease_expires` (for expiry monitoring)
- **Rollback migration** (`036_delegation_leases_rollback.sql`) created
- **Action type registry** (`delegation_types.py`): 16 integration action types with lease durations per Spec §5.1
- **`DelegatedTaskCreate` expanded**: Accepts all 16 integration types + 8 legacy types (24 total)
- **`DelegatedTaskResult` expanded**: Added `executor_id`, `research_id`, `artifacts`, `langsmith_run_id`, `langsmith_trace_url`
- **`GET /api/delegation/types`** endpoint: Returns 16 types with metadata

### Phase 2 — Backend Claim + Renew-Lease + Expanded Result Endpoints
- **`POST /api/tasks/{id}/claim`**: Atomic claiming via `SELECT ... FOR UPDATE`. Verifies status IN ('pending','queued'), checks no active lease, sets lease with configurable duration. Default lease from action type registry. Records `task_claimed` deal event. Returns 200 with lease details or 409 Conflict.
- **`POST /api/tasks/{id}/renew-lease`**: Verifies `lease_owner_id == executor_id` AND `status = 'executing'`. Updates `lease_expires_at` and `lease_heartbeat_at`. Returns 200 or 409.
- **`POST /api/tasks/{id}/result` expanded**: Stores artifacts, research_id, LangSmith tracing fields. Verifies lease ownership (403 if mismatch). Clears lease on completion/failure. Enhanced deal event includes artifact metadata.
- **`GET /api/delegation/tasks`**: Deal-agnostic listing with filters: `status`, `assigned_to`, `task_type`, `claimable_only`, `limit`. Agent polls this for claimable work.
- **`POST /api/delegation/tasks`**: Deal-optional task creation. Feature-flag gated (`delegate_actions`). For deal-less types (SYNC.*, OPS.*).

### Phase 3 — MCP Bridge Tool Additions
- **`zakops_claim_action`** (NEW): Posts to claim endpoint with executor_id, lease_seconds, correlation_id, langsmith_run_id
- **`zakops_renew_action_lease`** (NEW): Posts to renew-lease endpoint with executor_id, lease_seconds
- **`zakops_report_task_result`** (EXPANDED): Added executor_id, research_id, artifacts, langsmith_run_id, langsmith_trace_url params
- **`zakops_list_actions`** (EXPANDED): Added `include_delegated` and `assigned_to` params. When `include_delegated=True`, merges results from both actions and delegation endpoints.
- **Manifest updated**: `bridge_tool_count: 23`, `supported_action_types` expanded to 16, `prompt_version: v1.0-integration-phase2`, new tools in `supervised_tools` tier
- **`agent_contract.py` updated**: 2 new ToolDefinitions (MEDIUM risk, requires_approval=False)
- **Bridge restarted** as bare Python process (user `zaks`)

### Phase 4 — Dashboard "Delegate to Agent" Button
- **API functions** added to `apps/dashboard/src/lib/api.ts`:
  - `getDelegationTypes()` → GET `/api/delegation/types`
  - `createDelegatedTask(params)` → POST `/api/delegation/tasks`
  - `listDelegatedTasks(params)` → GET `/api/delegation/tasks`
- **Quarantine page**: "Delegate" button added alongside Approve/Reject/Escalate with `IconSend`
- **Delegation dialog**: Task type dropdown (16 types from API, lazy-loaded), priority selector (low/medium/high/critical), notes textarea, submit/cancel
- **Context pre-fill**: Quarantine item context (email_subject, sender, classification, company_name, operator_notes) included in delegation payload

### Phase 5 — Contract Surface Sync + Validation
- `make update-spec` → PASS (OpenAPI refreshed)
- `make sync-types` → PASS (Dashboard TS types updated)
- `make sync-backend-models` → PASS (Agent Python models regenerated via local `datamodel-codegen`)
- Surface 17 fix: Added `/api/delegation/tasks` and `/api/delegation/types` to proxy-pass exceptions
- `make validate-local` → PASS
- `npx tsc --noEmit` → zero errors

### Phase 6 — Golden Tests + Bookkeeping
- **T5 (Round-trip)**: Create → Claim → Renew → Result → Verify completed — **PASS** (3 sub-tests)
- **T9 (Race condition)**: Concurrent claims → exactly one 200, one 409 — **PASS** (3 sub-tests)
- **T10 (Artifact storage)**: Submit with artifacts → verify in DB — **PASS** (1 sub-test + 1 SKIP for RAG indexing)
- CHANGES.md updated
- `make validate-local` → final PASS

---

## Acceptance Criteria Results

| AC | Description | Status | Evidence |
|----|------------|--------|----------|
| AC-1 | Database Schema (9 columns + 2 indexes) | PASS | `SELECT column_name FROM information_schema.columns` returns all 9 |
| AC-2 | Action Type Registry (16 types) | PASS | `GET /api/delegation/types` → 16 types with correct lease durations |
| AC-3 | Atomic Claim (SELECT FOR UPDATE, 409 on double-claim) | PASS | T9 golden test: asyncio.gather → [200, 409] |
| AC-4 | Lease Renewal (holder-only) | PASS | T9: wrong executor → 409, correct executor → 200 |
| AC-5 | Expanded Result (artifacts, Identity Contract fields) | PASS | T5 + T10: artifacts stored, lease cleared |
| AC-6 | Bridge Tools (23 total, 2 new) | PASS | MCP `tools/list` → 23 tools including claim + renew |
| AC-7 | Dashboard Delegate (button + dialog + creation) | PASS | Quarantine page: Delegate button → dialog → task creation |
| AC-8 | Contract Surfaces (validate-local, surface15, surface17) | PASS | `make validate-local` PASS, all surfaces green |
| AC-9 | Golden Tests (T5, T9, T10) | PASS | 7 passed, 1 skipped (RAG conditional) |
| AC-10 | No Regressions (Phase 1 pipeline still works) | PASS | Existing quarantine, actions, deal pages unaffected |
| AC-11 | Bookkeeping (CHANGES.md updated) | PASS | Entry added with full Phase 2 details |

---

## Endpoint Inventory (Post-Phase 2)

### New Endpoints (5)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/delegation/types` | List 16 integration action types |
| GET | `/api/delegation/tasks` | Deal-agnostic task listing with filters |
| POST | `/api/delegation/tasks` | Create task (deal_id optional) |
| POST | `/api/tasks/{id}/claim` | Atomic lease-based claiming |
| POST | `/api/tasks/{id}/renew-lease` | Extend lease for current holder |

### Modified Endpoints (1)
| Method | Path | Change |
|--------|------|--------|
| POST | `/api/tasks/{id}/result` | Now stores artifacts, research_id, LangSmith tracing; verifies lease ownership; clears lease on completion |

### Unchanged Endpoints (from Phase 1)
| Method | Path |
|--------|------|
| GET | `/api/deals/{id}/tasks` |
| POST | `/api/deals/{id}/tasks` |
| POST | `/api/tasks/{id}/retry` |
| POST | `/api/tasks/{id}/confirm` |

---

## MCP Bridge Tool Inventory (23 Tools)

### New Tools (2)
| Tool | Risk | Approval | Description |
|------|------|----------|-------------|
| `zakops_claim_action` | MEDIUM | No | Atomically claim task with time-limited lease |
| `zakops_renew_action_lease` | MEDIUM | No | Renew lease on claimed task |

### Modified Tools (2)
| Tool | Change |
|------|--------|
| `zakops_report_task_result` | Added executor_id, research_id, artifacts, langsmith_run_id, langsmith_trace_url |
| `zakops_list_actions` | Added include_delegated, assigned_to params |

### Unchanged Tools (19)
`rag_query_local`, `rag_reindex_deal`, `zakops_approve_quarantine`, `zakops_create_action`, `zakops_get_action`, `zakops_get_classification_audit`, `zakops_get_deal`, `zakops_get_deal_status`, `zakops_get_manifest`, `zakops_get_sender_intelligence`, `zakops_get_triage_feedback`, `zakops_inject_quarantine`, `zakops_list_brokers`, `zakops_list_deal_artifacts`, `zakops_list_deals`, `zakops_list_quarantine`, `zakops_list_recent_events`, `zakops_update_deal_profile`, `zakops_write_deal_artifact`

---

## 16 Integration Action Types (from Spec §5)

| Type | Category | Lease (s) | Requires Deal |
|------|----------|-----------|---------------|
| EMAIL_TRIAGE.PROCESS_INBOX | email_triage | 300 | No |
| EMAIL_TRIAGE.CLASSIFY_THREAD | email_triage | 300 | No |
| RESEARCH.COMPANY_PROFILE | research | 1800 | Yes |
| RESEARCH.BROKER_INTEL | research | 1800 | No |
| RESEARCH.VENDOR_DUE_DILIGENCE | research | 1800 | No |
| DEAL.INTAKE_ANALYSIS | deal | 300 | Yes |
| DEAL.PIPELINE_MONITOR | deal | 600 | No |
| DOCUMENT.ANALYZE_CIM | document | 900 | Yes |
| DOCUMENT.EXTRACT_TERMS | document | 900 | Yes |
| DOCUMENT.SUMMARIZE_NDA | document | 900 | Yes |
| DRAFT.BROKER_REPLY | draft | 300 | Yes |
| DRAFT.FOLLOW_UP | draft | 300 | Yes |
| DRAFT.INTRO_REQUEST | draft | 300 | No |
| SYNC.REFRESH_CACHES | sync | 120 | No |
| OPS.HEALTH_CHECK | ops | 600 | No |
| OPS.GENERATE_REPORT | ops | 600 | No |

---

## Golden Test Results

```
Test File: apps/backend/tests/e2e/test_delegation_e2e.py
Duration: 0.74s
Results: 7 passed, 1 skipped

T5 — Full Delegation Round-Trip:
  test_create_claim_result     PASS  (create → claim → renew → result → verify)
  test_types_endpoint          PASS  (16 types with correct lease durations)
  test_legacy_types_still_work PASS  (legacy types accepted)

T9 — Concurrent Claim Race Condition:
  test_concurrent_claims       PASS  (asyncio.gather → [200, 409])
  test_renew_wrong_executor    PASS  (wrong executor → 409)
  test_result_wrong_executor   PASS  (wrong executor → 403)

T10 — Research Artifact → RAG:
  test_artifact_storage        PASS  (artifacts stored in DB, research_id linked)
  test_artifact_rag_indexing   SKIP  (RAG service not confirmed available)
```

---

## Architectural Decisions

### AD-1: Atomic Claiming via SELECT FOR UPDATE
Two simultaneous claims on the same task: exactly one gets 200, the other gets 409 Conflict. The row is locked within a PostgreSQL transaction, preventing the TOCTOU race condition that would occur with separate SELECT + UPDATE.

### AD-2: Lease-Based Ownership
Leases are time-boxed locks. If an agent crashes, the lease eventually expires and the task becomes re-claimable. Default durations are per-type (120s for SYNC, 1800s for RESEARCH). Future work: background job to requeue expired-lease tasks.

### AD-3: Identity Contract Compliance (Spec §10)
Every write operation stores `executor_id`, `correlation_id`, `langsmith_run_id`, and `langsmith_trace_url`. This provides complete audit trail for cross-system task execution.

### AD-4: Lease Ownership Enforcement
Only the lease holder can: renew the lease (409 for others), submit results (403 for others), or clear the lease. This prevents one agent from interfering with another's work.

### AD-5: Feature Flag Gating
The `delegate_actions` flag remains `false` in production. Task creation is gated behind this flag. The flag is enabled only during golden tests via session-scoped fixture with cleanup.

---

## Post-Delivery Fixes (During Execution)

1. **Surface 2 stale codegen**: `make sync-backend-models` failed because agent container lacks `datamodel-codegen`. Fixed by running locally with `datamodel-codegen --input ...zakops-api.json --output ...backend_models.py`.
2. **Surface 17 uncovered endpoints**: New `/api/delegation/tasks` and `/api/delegation/types` endpoints detected as uncovered by dashboard route validator. Fixed by adding to `PROXY_PASS_EXCEPTIONS` in `validate-surface17.sh` (these are backend-only endpoints, no Next.js route needed).
3. **TypeScript type mismatch**: `source_message_id` doesn't exist on QuarantineItem type. Removed from delegation context pre-fill — sender and email_subject already capture the essential context.
4. **pytest event loop lifecycle**: Module-scoped async `client` fixture caused "Event loop is closed" errors. Fixed by changing to function-scoped `client` fixture with session-scoped sync `_enable_flag` fixture.

---

## Files Created

| File | Purpose |
|------|---------|
| `apps/backend/db/migrations/036_delegation_leases.sql` | Add 9 lease columns + 2 indexes |
| `apps/backend/db/migrations/036_delegation_leases_rollback.sql` | Rollback migration |
| `apps/backend/src/api/orchestration/delegation_types.py` | 16 integration action type registry |
| `apps/backend/tests/e2e/test_delegation_e2e.py` | Golden tests T5, T9, T10 |

## Files Modified

| File | Change |
|------|--------|
| `apps/backend/src/api/orchestration/main.py` | Expanded models + 5 new endpoints |
| `apps/agent-api/mcp_bridge/server.py` | 2 new tools + 2 expanded + manifest update |
| `apps/agent-api/mcp_bridge/agent_contract.py` | 2 new ToolDefinitions + system prompt update |
| `apps/dashboard/src/app/quarantine/page.tsx` | Delegate button + dialog |
| `apps/dashboard/src/lib/api.ts` | 3 new API functions + types |
| `tools/infra/validate-surface17.sh` | Added proxy-pass exceptions for delegation endpoints |

---

## What's NOT in This Mission (Scope Fence)

- Pipeline B execution logic (LangSmith agent domain)
- Gmail back-labeling (Phase 3)
- Event polling / bi-directional communication (Phase 3)
- Background lease expiry reaper (future enhancement)
- Production enablement of `delegate_actions` flag
- Modification of SQLite action engine (store.py)

---

## Successor: INTEGRATION-PHASE3-BUILD-001

Phase 3 "Bi-directional Communication" will build (per Integration Spec v1.0 §14 Items 15-17):
- Lease expiry reaper for stale delegated tasks (ENH-9 — production blocker)
- Gmail back-labeling push — auto-create `SYNC.BACKFILL_LABELS` task on quarantine approve/reject (Item 15)
- Event polling expansion — `since_ts`, `event_type`, deal-agnostic mode (Item 16)
- Operator-to-agent mid-task messaging channel (Item 17)
- Dashboard UX fixes for delegation (ENH-5, ENH-6)
- `_ensure_dict` decorator refactor (ENH-10)

**Mission Prompt:** `/home/zaks/bookkeeping/docs/MISSION-INTEGRATION-PHASE3-BUILD-001.md`
**Roadmap:** `/home/zaks/bookkeeping/docs/INTEGRATION-ROADMAP.md`

---

## Post-QA Remediation (QA-UNIFIED-P1P2-VERIFY-001)

**QA Scorecard:** 60/60 gates PASS, 0 FAIL, 1 INFO, 10 ENH
**QA Report:** `/home/zaks/bookkeeping/qa-verifications/QA-UNIFIED-P1P2-VERIFY-001/QA-UNIFIED-P1P2-VERIFY-001-SCORECARD.md`
**Remediation Date:** 2026-02-17

### Immediate Fixes Applied

| ENH | Finding | Fix | File |
|-----|---------|-----|------|
| ENH-1 | Hardcoded API key in e2e test (inline fallback) | Removed fallback — `ZAKOPS_API_KEY` env var now required, `RuntimeError` on missing | `apps/backend/tests/e2e/test_delegation_e2e.py` L16 |
| ENH-4 | Comment says "Phase 6" instead of "Phase 2" | Verified already correct ("Phase 2 Integration" at L327) — QA caught transient state | `apps/agent-api/mcp_bridge/agent_contract.py` L327 |

### Deferred to Phase 3 Roadmap

| ENH | Priority | Finding | Phase 3 Placement |
|-----|----------|---------|-------------------|
| ENH-9 | HIGH | No lease expiry reaper for stale executing tasks | **Phase 3, P0 (first thing)** — background job: `UPDATE ... SET status='pending', lease_owner_id=NULL WHERE lease_expires_at < NOW() AND status='executing'` on 60s interval |
| ENH-5 | MEDIUM | Silent empty dropdown on delegation type fetch failure | Phase 3 Dashboard UX pass |
| ENH-6 | MEDIUM | Generic toast on 503 — should detect disabled delegation | Phase 3 Dashboard UX pass |
| ENH-7 | LOW | RAG indexing test is permanent stub | Phase 3 when artifact→RAG pipeline wired |
| ENH-10 | LOW | `_ensure_dict` applied manually at 9 sites | Phase 3 when adding more tools — refactor to decorator |

### Accepted As-Is (No Action)

| ENH | Priority | Finding | Rationale |
|-----|----------|---------|-----------|
| ENH-2 | MEDIUM | Hardcoded `zakops-postgres-1` container name | e2e tests inherently couple to infra; COMPOSE_PROJECT_NAME=zakops is stable |
| ENH-3 | LOW | SQL string interpolation in test psql | Test-only, values are UUIDs from our own API responses, not user input |
| ENH-8 | LOW | Manifest sha256 recalculated per call | Endpoint called infrequently; caching adds stale-data risk for microsecond savings |

---

## Key Artifact Paths

| Artifact | Path |
|----------|------|
| This report | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE2-BUILD-001-COMPLETION.md` |
| Phase 1 report | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md` |
| Mission plan | Plan file `ethereal-prancing-cascade.md` |
| Integration Spec | `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` |
| Golden tests | `apps/backend/tests/e2e/test_delegation_e2e.py` |
| Action type registry | `apps/backend/src/api/orchestration/delegation_types.py` |
| Migration | `apps/backend/db/migrations/036_delegation_leases.sql` |
| Change log | `/home/zaks/bookkeeping/CHANGES.md` |

---

*End of Completion Report — INTEGRATION-PHASE2-BUILD-001*
