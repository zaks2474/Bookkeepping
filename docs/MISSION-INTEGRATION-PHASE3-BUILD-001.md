# MISSION: INTEGRATION-PHASE3-BUILD-001
## Bi-directional Communication — Lease Reaper, Gmail Back-Labeling, Event Polling, Operator Messaging, ENH Remediation
## Date: 2026-02-17
## Classification: Feature Build (Integration Phase 3 — FINAL)
## Prerequisite: INTEGRATION-PHASE2-BUILD-001 (Complete), QA-UNIFIED-P1P2-VERIFY-001 (60/60 PASS)
## Successor: QA-IP3-VERIFY-001

---

## Mission Objective

Implement Phase 3 of the Integration Spec v1.0 — the **final phase** of the 3-phase build plan. This phase closes the bi-directional communication loop between ZakOps and the LangSmith Exec Agent.

**What this mission does:**
1. Implements a lease expiry reaper that reclaims stale delegated tasks (ENH-9 — production blocker)
2. Auto-creates `SYNC.BACKFILL_LABELS` delegated tasks on quarantine approval/rejection, enabling the agent to back-label Gmail (Item 15)
3. Expands event polling with `since_ts`, `event_type`, and deal-agnostic mode (Item 16)
4. Adds operator-to-agent mid-task messaging channel (Item 17)
5. Fixes dashboard delegation UX: empty dropdown (ENH-5), generic 503 toast (ENH-6)
6. Converts 9 manual `_ensure_dict` call sites to a decorator (ENH-10)

**What this mission is NOT:**
- No SSE/WebSocket push (deferred — polling is sufficient for current scale)
- No agent-side Gmail label logic (agent already has Gmail tools — it handles labeling itself)
- No SQLite action engine changes (store.py is out of scope)
- No modifications to the agent's internal processing logic

**Source material:**
- Integration Spec v1.0 §14 Items 15-17: `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md`
- QA-UNIFIED-P1P2-VERIFY-001 ENH findings: `/home/zaks/bookkeeping/qa-verifications/QA-UNIFIED-P1P2-VERIFY-001/QA-UNIFIED-P1P2-VERIFY-001-SCORECARD.md`
- Integration Roadmap: `/home/zaks/bookkeeping/docs/INTEGRATION-ROADMAP.md`

---

## Context

### Where We Are

Phases 1-2 gave the LangSmith agent:
- **Read access** (Phase 1): triage feedback, broker registry, classification audit, sender intelligence, manifest drift detection — 5 tools, all proven end-to-end
- **Write-with-lease access** (Phase 2): atomic claiming, lease-based task ownership, delegation framework — 5 new endpoints, 2 new MCP tools, 16 action types, dashboard Delegate button

**What's missing for full bi-directional communication:**
1. **No proactive push** — when an operator approves/rejects a quarantine item, the agent doesn't know unless it polls
2. **No efficient event polling** — `zakops_list_recent_events` requires `deal_id` (no deal-agnostic mode), no `since_ts` filter, no `event_type` filter
3. **No mid-task messaging** — operators can set initial notes at delegation time but can't communicate with the agent during task execution
4. **No crash recovery** — if the agent crashes mid-task, the lease expires but nothing reclaims the task (ENH-9)
5. **Dashboard UX gaps** — silent empty dropdown on type fetch failure (ENH-5), generic toast on 503 (ENH-6)

### LangSmith Agent Capabilities (confirmed in handshake 2026-02-17)

- **29 total tools**: 6 Gmail MCP + 23 ZakOps MCP
- **Gmail tools**: read, thread, label, draft, list_labels, create_label — agent can apply Gmail labels itself
- **Identity Contract**: `executor_id: "langsmith_exec_agent_prod"`, correlation_id, langsmith_run_id, langsmith_trace_url
- **Constraint awareness**: `delegate_actions=false` respected, supervised tier understood

**Contract Surfaces Affected:** 1 (Backend→Dashboard), 2 (Backend→Agent SDK), 15 (MCP Bridge), 17 (Dashboard Routes)

---

## Glossary

| Term | Definition |
|------|-----------|
| Back-labeling | After ZakOps approves/rejects a quarantine email, the Gmail message gets labels applied reflecting the decision |
| Lease reaper | Background task that reclaims expired leases on delegated tasks, making them re-claimable |
| Bridge server | MCP server at `apps/agent-api/mcp_bridge/server.py` — the LangSmith agent's gateway to ZakOps |
| Agent contract | `apps/agent-api/mcp_bridge/agent_contract.py` — tool manifest, risk levels, system prompt |
| OutboxProcessor pattern | Background polling loop: start/stop lifecycle, asyncio.create_task, graceful cancellation, configurable interval |
| Identity Contract | executor_id + langsmith_run_id must be present on all writes (Spec §10) |

---

## Key Design Decisions

**Item 15 (Gmail back-labeling):** Option (b) — auto-create `SYNC.BACKFILL_LABELS` delegated task when quarantine items are approved/rejected. The agent already has 6 Gmail tools (confirmed in handshake). We provide the data (message_id, thread_id, action); the agent claims the task and applies labels using its own Gmail MCP tools. This uses the existing delegation framework with zero new infrastructure.

**Item 16 (Event polling):** Expand existing endpoint + new deal-agnostic endpoint. `GET /api/deals/{id}/events` gets `since_ts` + `event_type` params. New `GET /api/events/history` is DB-backed (NOT the SSE in-memory buffer). Bridge tool `zakops_list_recent_events` gets optional `deal_id`, `since_ts`, `event_type`.

**Item 17 (Operator messaging):** New `messages` JSONB column on `delegated_tasks` + `POST /api/tasks/{id}/message` endpoint. Simple append-only array of `{ts, from, role, text}`. Dashboard gets message input on task detail. Agent reads messages when polling task state.

---

## Architectural Constraints

- **`delegate_actions` feature flag gates task creation** — auto-created SYNC.BACKFILL_LABELS tasks must respect this gate. Flag off = no tasks created, quarantine still works.
- **Identity Contract (Spec §10)** — executor_id + langsmith_run_id on all writes. System-created back-labeling tasks use `created_by='system'`.
- **OutboxProcessor pattern** — lease reaper must follow: `start()/stop()`, `asyncio.create_task()`, configurable poll interval, graceful cancellation on shutdown.
- **Back-labeling is best-effort** — task creation failure must NOT fail the quarantine operation. Log + swallow.
- **No unbounded queries** — `/api/events/history` requires at least `since_ts` or `deal_id`.
- **`Promise.allSettled` mandatory** for dashboard multi-fetch. `Promise.all` banned.
- **Surface 9 compliance** — `console.warn` for expected degradation, `console.error` for unexpected failures.
- **Generated file protection** — never edit `*.generated.ts` or `*_models.py`. Use sync pipeline.
- **Port 8090 FORBIDDEN** — never reference.

---

## Anti-Pattern Examples

### WRONG: Silent empty dropdown on fetch failure
```typescript
export async function getDelegationTypes() {
  try { ... } catch { return {}; }  // User sees empty dropdown, no error
}
```
### RIGHT: Surface error state to UI
```typescript
export async function getDelegationTypes() {
  try { ... }
  catch (err) {
    if (err instanceof ApiError && err.status === 503)
      throw new DelegationDisabledError('Delegation is disabled by administrator');
    console.warn('[API] Delegation types unavailable:', err);
    return {};
  }
}
```

### WRONG: Back-labeling failure crashes quarantine
```python
await _maybe_create_backfill_task(conn, item, action, pool)  # If this throws, quarantine fails
```
### RIGHT: Best-effort with swallow
```python
try:
    await _maybe_create_backfill_task(conn, item, action, pool)
except Exception:
    logger.warning("Back-labeling task creation failed, quarantine continues")
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Lease reaper starts before db_pool is ready | MEDIUM | Backend crash loop | P1: start reaper AFTER db_pool + flags in lifespan, same as OutboxProcessor placement |
| 2 | Back-labeling task created but delegate_actions not checked | HIGH | Tasks created when feature disabled | P2: explicit flag check in helper, fail-closed |
| 3 | Event history returns unbounded results without filters | MEDIUM | Memory pressure, slow queries | P3: require at least since_ts or deal_id, enforce limit |
| 4 | `_ensure_dict` decorator breaks FastMCP introspection | LOW | Agent can't call tools | P5: use functools.wraps, test all 9 tools after conversion |
| 5 | Dashboard messaging UI conflicts with quarantine page state | MEDIUM | Broken UX | P4: messaging is additive to existing dialog, test both flows |

---

## Phases

### Dependency Graph

```
Phase 0 (Discovery)
    │
    v
Phase 1 (Lease Reaper) --------+
    │                           │ (parallel-safe)
    v                           v
Phase 2 (Back-Labeling)    Phase 3 (Event Polling)
    │                           │
    +-------+-------------------+
            │
            v
    Phase 4 (Messaging + Dashboard UX)
            │
            v
    Phase 5 (ENH-10 Decorator + Manifest)
            │
            v
    Phase 6 (Contract Sync + Golden Tests + Bookkeeping)
```

---

### Phase 0 — Discovery & Baseline
**Complexity:** S | **Blast Radius:** None (read-only)

| Task | Description | Gate |
|------|-------------|------|
| P0-01 | `make validate-local` — capture baseline | Exit 0 |
| P0-02 | Validate affected surfaces: `make validate-surface1 && make validate-surface15 && make validate-surface17` | All PASS |
| P0-03 | Verify `SYNC.BACKFILL_LABELS` in delegation_types.py | Present (120s lease, category=sync) |
| P0-04 | Verify lease index `idx_dt_lease_expires` exists in live DB | Present |
| P0-05 | Verify `_ensure_dict` call site count = 9 | Confirmed |
| P0-06 | Read `OutboxProcessor` pattern at `apps/backend/src/core/outbox/processor.py` | Pattern understood |

**Gate P0:** Baseline green, all findings current.

---

### Phase 1 — Lease Expiry Reaper (ENH-9)
**Complexity:** M | **Blast Radius:** Backend (8091), delegated task lifecycle

| Task | Description |
|------|-------------|
| P1-01 | Create `LeaseReaper` class at `apps/backend/src/core/delegation/lease_reaper.py` following `OutboxProcessor` pattern (start/stop/poll loop, asyncio.create_task, configurable interval=30s). SQL: `UPDATE zakops.delegated_tasks SET status='queued', lease_owner_id=NULL, lease_expires_at=NULL, lease_heartbeat_at=NULL WHERE status='executing' AND lease_expires_at < NOW() RETURNING id, task_type, lease_owner_id`. Log each reclaim. Record deal event if task has deal_id. |
| P1-02 | Wire into lifespan at `main.py` — start AFTER db_pool + feature flags, stop BEFORE pool close. Conditional on `delegate_actions` flag (skip if off). |
| P1-03 | Add `lease_reaper_active: bool` to `/health` response. |

**Decision Tree:**
- `delegate_actions` OFF at startup → skip reaper, log "LeaseReaper skipped (delegate_actions disabled)"
- DB error during poll → log error, sleep, retry (same as OutboxProcessor)
- No expired leases → sleep interval, retry

**Rollback:** Remove from lifespan, delete lease_reaper.py.
**Gate P1:** Backend starts with reaper log. Manually expire a lease → reaper reclaims within 30s. `make validate-local` PASS.

---

### Phase 2 — Gmail Back-Labeling Push (Item 15)
**Complexity:** M | **Blast Radius:** Backend (quarantine processing path)

| Task | Description |
|------|-------------|
| P2-01 | Create `_maybe_create_backfill_task(conn, item_data, action, pool)` helper in main.py. Checks `delegate_actions` flag (fail-closed). Creates `SYNC.BACKFILL_LABELS` task with context: `{quarantine_item_id, message_id, source_thread_id, email_subject, sender, action, deal_id}`. Uses `created_by='system'`, `assigned_to='langsmith_agent'`, `priority='low'`. |
| P2-02 | Hook into `process_quarantine()` — call helper AFTER transaction commit for both approve and reject paths. Failure must NOT fail the quarantine operation (try/except with log + swallow). |
| P2-03 | Hook into `bulk_process_quarantine()` — same helper, once per item processed. |
| P2-04 | Update agent contract system prompt to document `SYNC.BACKFILL_LABELS` as auto-created task type. Include note: "Claim the task, read context for message_id and action, apply corresponding Gmail label (ZakOps/Approved or ZakOps/Rejected), report result." |

**Decision Tree:**
- `delegate_actions` OFF → log warning, skip, quarantine proceeds normally
- INSERT fails → log error, continue (best-effort)

**Rollback:** Remove helper calls, delete helper function.
**Gate P2:** Approve quarantine → `SYNC.BACKFILL_LABELS` task appears. Reject → same. Flag OFF → no task, quarantine still works. `make validate-local` PASS.

---

### Phase 3 — Event Polling Expansion (Item 16)
**Complexity:** M | **Blast Radius:** Backend + MCP Bridge

| Task | Description |
|------|-------------|
| P3-01 | Expand `GET /api/deals/{id}/events` with `since_ts: str | None` and `event_type: str | None` query params. Follow quarantine param-building pattern. |
| P3-02 | Create `GET /api/events/history` — deal-agnostic, DB-backed (NOT SSE buffer). Params: `since_ts`, `event_type`, `deal_id` (optional), `limit`. Requires at least `since_ts` or `deal_id`. |
| P3-03 | Expand MCP bridge `zakops_list_recent_events` — make `deal_id` optional, add `since_ts`, `event_type`. When no `deal_id`, hit `/api/events/history`. When `deal_id` provided, hit existing endpoint with new params. |
| P3-04 | Update agent contract ToolDefinition — `deal_id` optional, new params documented. |

**Decision Tree:**
- `deal_id` is None AND `since_ts` is None → reject with 400 "At least deal_id or since_ts required"
- `since_ts` malformed → 422 validation error

**Rollback:** Revert param additions, remove new endpoint.
**Gate P3:** Deal-specific + deal-agnostic queries work with all filter combos. MCP tool returns data. `make validate-local` PASS.

---

### Phase 4 — Operator-to-Agent Messaging + Dashboard UX (Item 17, ENH-5, ENH-6)
**Complexity:** L | **Blast Radius:** Backend + Dashboard + MCP Bridge

#### Item 17: Operator-to-Agent Messaging

| Task | Description |
|------|-------------|
| P4-01 | Migration 037: `ALTER TABLE zakops.delegated_tasks ADD COLUMN IF NOT EXISTS messages JSONB DEFAULT '[]'` + rollback. |
| P4-02 | `POST /api/tasks/{id}/message` — appends `{ts, from, role, text}` to messages JSONB array. Feature-flag gated. Only for non-terminal tasks (pending/queued/executing). Records deal event if deal_id present. |
| P4-03 | Verify `messages` appears in `GET /api/delegation/tasks` response (auto from `dt.*`). |
| P4-04 | Add `zakops_get_task_messages` MCP tool (or expose messages in existing task detail). Update agent contract as LOW risk, no approval needed. |

#### ENH-5 + ENH-6: Dashboard UX Fixes

| Task | Description |
|------|-------------|
| P4-05 | **ENH-5:** Fix `getDelegationTypes()` in api.ts — detect 503, surface "Delegation disabled" to caller instead of silent `{}`. |
| P4-06 | **ENH-6:** Fix `handleDelegate()` in quarantine/page.tsx — detect 503 specifically, show "Delegation is disabled by administrator" toast. Other errors show actual error message. |
| P4-07 | Add message input + history display to task detail area in dashboard. |

**Decision Tree:**
- Task in terminal status (completed/failed/dead_letter) → reject message with 400
- `delegate_actions` OFF → reject with 503

**Rollback:** Revert dashboard changes, remove endpoint. Migration 037 is additive.
**Gate P4:** POST message → appears in task. "Delegation disabled" on 503 (not empty dropdown). `make validate-local` + `npx tsc --noEmit` PASS.

---

### Phase 5 — `_ensure_dict` Decorator (ENH-10) + Manifest Update
**Complexity:** S | **Blast Radius:** MCP Bridge

| Task | Description |
|------|-------------|
| P5-01 | Create `@ensure_dict_response` decorator in bridge server.py. Uses `functools.wraps`. All bridge tools are sync `def` — no async handling needed. |
| P5-02 | Apply decorator to all 9 tool functions. Replace `return _ensure_dict(resp.json())` with `return resp.json()`. Keep `_ensure_dict` available for edge cases. |
| P5-03 | Update manifest: `bridge_tool_count`, `prompt_version` to `v1.0-integration-phase3`, add any new tools to tier lists. |

**Gate P5:** All 9 sites use decorator. Bridge returns healthy. MCP `tools/list` returns correct count. `make validate-local` PASS.

---

### Phase 6 — Contract Sync + Golden Tests + Bookkeeping
**Complexity:** M | **Blast Radius:** Validation only

| Task | Description |
|------|-------------|
| P6-01 | `make update-spec` → `make sync-types` → `make sync-backend-models` → `make sync-all-types` |
| P6-02 | `npx tsc --noEmit` in dashboard |
| P6-03 | `make validate-local` + `make validate-surface1 && make validate-surface15 && make validate-surface17` |
| P6-04 | Surface 17 proxy-pass exceptions for new endpoints (`/api/events/history`, `/api/tasks/{id}/message`) |
| P6-05 | Golden tests: T7-enhanced (event polling with since_ts), T-reaper (lease expiry reclaim), T-backlabel (quarantine approve → task created), T-message (operator message round-trip) |
| P6-06 | Browser verify: quarantine page delegation dialog, messaging, disabled state |
| P6-07 | Update CHANGES.md, write completion report |

**Gate P6:** All validation passes. Golden tests pass. Browser verified. Bookkeeping complete.

---

## Acceptance Criteria

| AC | Description | Phase |
|----|-------------|-------|
| AC-1 | Lease reaper reclaims expired leases within 30s, follows OutboxProcessor lifecycle | P1 |
| AC-2 | Quarantine approve/reject auto-creates `SYNC.BACKFILL_LABELS` task with message_id + thread_id + action | P2 |
| AC-3 | `zakops_list_recent_events` accepts optional deal_id, since_ts, event_type. `GET /api/events/history` is DB-backed + deal-agnostic | P3 |
| AC-4 | `POST /api/tasks/{id}/message` stores messages. Dashboard shows message input. Agent reads messages via task detail | P4 |
| AC-5 | Dashboard shows "Delegation disabled" on 503, not empty dropdown + generic toast | P4 |
| AC-6 | 9 manual `_ensure_dict` sites replaced with `@ensure_dict_response` decorator | P5 |
| AC-7 | `make validate-local` + `npx tsc --noEmit` + all affected surfaces PASS | P6 |
| AC-8 | CHANGES.md + completion report committed | P6 |

---

## Guardrails

1. **Scope fence:** No SSE push, no agent-side Gmail logic, no SQLite action engine changes
2. **Back-labeling is best-effort:** Task creation failure must NOT fail quarantine operations (log + swallow)
3. **Feature flag respect:** All new delegation paths check `delegate_actions`
4. **No unbounded queries:** `/api/events/history` requires at least `since_ts` or `deal_id`
5. **Generated file protection:** Use sync pipeline, never edit `*.generated.ts` or `*_models.py`
6. **Surface 9 compliance:** `console.warn` for expected degradation, `console.error` for unexpected
7. **WSL safety:** CRLF fix on `.sh` files, ownership fix on `/home/zaks/` files
8. **Governance surfaces:** `make validate-surface{1,15,17}` after respective changes (per IA-15)

---

## Executor Self-Check Prompts

### After Phase 0:
- "Did `make validate-local` pass at baseline?"
- "Did I verify all 4 affected contract surfaces?"
- "Are the findings (9 _ensure_dict sites, no reaper) still current?"

### After every code change:
- "Did I check the `delegate_actions` feature flag in new code paths?"
- "Is this a degradation path or an unexpected failure?" (for console.warn/error)

### Before marking COMPLETE:
- "Does `make validate-local` pass?"
- "Did I run `npx tsc --noEmit`?"
- "Did I create ALL files in the Files to Create table?"
- "Did I verify the quarantine page in a browser?"
- "Did I update CHANGES.md?"

---

## Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `apps/backend/src/core/delegation/lease_reaper.py` | P1 | LeaseReaper background task |
| `apps/backend/src/core/delegation/__init__.py` | P1 | Package init |
| `apps/backend/db/migrations/037_task_messages.sql` | P4 | Add messages JSONB column |
| `apps/backend/db/migrations/037_task_messages_rollback.sql` | P4 | Rollback |

## Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `apps/backend/src/api/orchestration/main.py` | P1-P4 | Lifespan reaper, back-labeling helper, events expansion, message endpoint |
| `apps/agent-api/mcp_bridge/server.py` | P3, P5 | Expand events tool, apply decorator, manifest update |
| `apps/agent-api/mcp_bridge/agent_contract.py` | P2-P4 | Update tool defs, system prompt, messaging tool |
| `apps/dashboard/src/lib/api.ts` | P4 | Fix getDelegationTypes + createDelegatedTask error handling |
| `apps/dashboard/src/app/quarantine/page.tsx` | P4 | Fix toasts, add messaging UI |
| `tools/infra/validate-surface17.sh` | P6 | Proxy-pass exceptions for new endpoints |

## Files to Read (pattern sources — do NOT modify)

| File | Purpose |
|------|---------|
| `apps/backend/src/core/outbox/processor.py` | LeaseReaper lifecycle pattern |
| `apps/backend/src/api/orchestration/delegation_types.py` | SYNC.BACKFILL_LABELS type registry |
| `apps/backend/db/migrations/035_delegated_tasks.sql` | Original table schema |
| `apps/backend/db/migrations/036_delegation_leases.sql` | Lease columns + indexes |

---

## Stop Condition

DONE when all 8 AC met, all validation passes, browser verified, bookkeeping committed.

Do NOT proceed to:
- QA-IP3-VERIFY-001 (that is the successor QA mission)
- Agent-side Gmail label application logic (out of scope — agent handles this)
- SSE push implementation (deferred — polling sufficient at current scale)

---

## Crash Recovery Protocol

If resuming after crash or context compaction:
1. `git log --oneline -10` — check which phases have been committed
2. `make validate-local` — check current state
3. Check migration applied: `docker exec zakops-postgres-1 psql -U zakops -d zakops -c "SELECT column_name FROM information_schema.columns WHERE table_schema='zakops' AND table_name='delegated_tasks' AND column_name='messages'"`
4. Check reaper present: `grep -c 'LeaseReaper' apps/backend/src/api/orchestration/main.py`
5. Check back-labeling hook: `grep -c '_maybe_create_backfill_task' apps/backend/src/api/orchestration/main.py`

---

*End of Mission Prompt — INTEGRATION-PHASE3-BUILD-001*
