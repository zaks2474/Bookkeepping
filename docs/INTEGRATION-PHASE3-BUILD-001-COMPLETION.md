# Completion Report: INTEGRATION-PHASE3-BUILD-001
## Bi-directional Communication — Final Integration Phase
## Date: 2026-02-18
## Status: COMPLETE

---

## Mission Summary

Phase 3 of 3 in the ZakOps + LangSmith Agent integration. Closes the bi-directional communication loop between the ZakOps operator dashboard and the LangSmith Exec Agent.

## Acceptance Criteria Results

| AC | Description | Result |
|----|-------------|--------|
| AC-1 | LeaseReaper runs on start when delegate_actions=true, reclaims expired leases | PASS |
| AC-2 | Quarantine approve/reject auto-creates SYNC.BACKFILL_LABELS delegated task | PASS |
| AC-3 | GET /api/events/history returns deal-agnostic events with since_ts, event_type, deal_id params | PASS |
| AC-4 | POST /api/tasks/{id}/message appends message, rejects terminal tasks | PASS |
| AC-5 | Dashboard shows "Delegation is disabled" toast on 503 (ENH-5/ENH-6) | PASS |
| AC-6 | @ensure_dict_response decorator replaces 9 manual call sites (ENH-10) | PASS |
| AC-7 | All contract surfaces valid (make validate-local PASS) | PASS |
| AC-8 | Golden tests pass (T7-enhanced, T-reaper, T-backlabel, T-message) | PASS |

## Deliverables

### D1: Lease Expiry Reaper (ENH-9)
- `lease_reaper.py` — LeaseReaper class following OutboxProcessor pattern
- Reclaims tasks where `status='executing'` AND `lease_expires_at < NOW()`
- Resets to `queued`, clears lease fields, records deal events
- Starts conditionally on `delegate_actions` flag in lifespan
- Health endpoint reports `lease_reaper_active` status
- **Evidence:** 8 tasks reclaimed on first poll after startup

### D2: Gmail Back-Labeling (Item 15)
- `_maybe_create_backfill_task()` — best-effort task creation
- Hooked into `process_quarantine` (after commit) and `bulk_process_quarantine` (per-item)
- Checks `delegate_actions` flag (fail-closed)
- Failure does NOT propagate to quarantine operation (try/except + log)
- Agent contract updated with SYNC.BACKFILL_LABELS workflow documentation
- **Evidence:** Approve quarantine item → SYNC.BACKFILL_LABELS task created (1→2 in DB)

### D3: Event Polling Expansion (Item 16)
- `GET /api/deals/{id}/events` — expanded with `since_ts`, `event_type` params
- `GET /api/events/history` — new deal-agnostic, DB-backed endpoint
- Requires at least `since_ts` or `deal_id` (400 otherwise)
- `since_ts` properly parsed from ISO-8601 string to datetime for asyncpg
- MCP bridge `zakops_list_recent_events` — deal_id now optional, new params
- Dashboard route handler at `/api/events/history/route.ts` (fixes prefix clash with SSE stub)
- **Evidence:** Events returned with since_ts filter, 400 on missing params, 400 on invalid timestamp

### D4: Operator Messaging (Item 17)
- `POST /api/tasks/{id}/message` — append-only messages JSONB
- Migration 037: `messages JSONB DEFAULT '[]'` on `delegated_tasks`
- Feature-flag gated, rejects terminal tasks (completed/failed/dead_letter)
- Records deal events when task has deal_id
- MCP bridge `zakops_get_task_messages` tool added
- Agent contract tool definition added
- Dashboard: `sendTaskMessage()` API function, message panel UI
- **Evidence:** 2 messages sent (operator + system), count incremented, terminal rejection works

### D5: Dashboard Delegation UX (ENH-5, ENH-6)
- `DelegationDisabledError` — custom error class for 503 detection
- `getDelegationTypes()` — catches 503, throws DelegationDisabledError
- `createDelegatedTask()` — catches 503, throws DelegationDisabledError
- `openDelegateDialog` — shows "Delegation is disabled by administrator" toast
- `handleDelegate` — shows specific disabled toast on DelegationDisabledError

### D6: @ensure_dict_response Decorator (ENH-10)
- Decorator using `functools.wraps` for FastMCP introspection compatibility
- Applied to all 9 MCP tool functions
- Replaced 9 manual `_ensure_dict(resp.json())` calls with plain `resp.json()`
- Manifest prompt_version updated to `v1.0-integration-phase3`

## Golden Test Results

| Test | Cases | Result | Key Evidence |
|------|-------|--------|-------------|
| T7-enhanced | 4 | PASS | since_ts returns events, deal_id works, 400 no params, 400 bad timestamp |
| T-reaper | 1 | PASS | 8 tasks reclaimed on first poll, status→queued, lease fields nulled |
| T-backlabel | 1 | PASS | BACKFILL_LABELS task count 1→2, correct title/created_by/status |
| T-message | 5 | PASS | Operator msg sent, system msg sent, count=2, 400 terminal, 404 missing |

## Contract Surface Validation

| Surface | Status |
|---------|--------|
| 1 — Backend → Dashboard | PASS (make sync-types + tsc) |
| 2 — Backend → Agent SDK | PASS (datamodel-codegen regenerated) |
| 15 — MCP Bridge Tool Interface | PASS (24 tools, manifest updated) |
| 17 — Dashboard Route Coverage | PASS (events/history route handler added) |
| make validate-local | PASS |

## Bugs Found and Fixed During Execution

1. **since_ts asyncpg DataError** — Passed raw string to asyncpg instead of datetime. Fixed with `datetime.fromisoformat()` parsing + 400 on invalid format.
2. **NameError: logger not defined** — `_maybe_create_backfill_task` used `logger` but main.py uses `print()`. Fixed to use `print()`.
3. **events/history route blocked by SSE stub** — `/api/events` route.ts catches all sub-paths via middleware prefix match. Fixed by creating dedicated `/api/events/history/route.ts` proxy handler.

## Files Created (5)

| File | Purpose |
|------|---------|
| `apps/backend/src/core/delegation/__init__.py` | Package init |
| `apps/backend/src/core/delegation/lease_reaper.py` | LeaseReaper background worker |
| `apps/backend/db/migrations/037_task_messages.sql` | Messages column migration |
| `apps/backend/db/migrations/037_task_messages_rollback.sql` | Migration rollback |
| `apps/dashboard/src/app/api/events/history/route.ts` | Event history proxy route |

## Files Modified (6)

| File | Changes |
|------|---------|
| `apps/backend/src/api/orchestration/main.py` | Lifespan reaper, backfill hook, events expansion, history endpoint, message endpoint, since_ts fix |
| `apps/backend/src/api/shared/routers/health.py` | lease_reaper_active health component |
| `apps/agent-api/mcp_bridge/server.py` | Decorator (9 sites), events expansion, task_messages tool, manifest update |
| `apps/agent-api/mcp_bridge/agent_contract.py` | Events/messages tool defs, BACKFILL_LABELS system prompt |
| `apps/dashboard/src/lib/api.ts` | DelegationDisabledError, 503 handling, sendTaskMessage |
| `apps/dashboard/src/app/quarantine/page.tsx` | Delegate error handling, message panel UI |

## Integration Phase Status

| Phase | Mission | Status | QA |
|-------|---------|--------|-----|
| Phase 1 | INTEGRATION-PHASE1-BUILD-001 | Complete | 60/60 PASS |
| Phase 2 | INTEGRATION-PHASE2-BUILD-001 | Complete | 60/60 PASS |
| Phase 3 | INTEGRATION-PHASE3-BUILD-001 | **Complete** | Pending QA-IP3-VERIFY-001 |

## Successor Mission

QA-IP3-VERIFY-001 — Independent verification of all Phase 3 deliverables.
