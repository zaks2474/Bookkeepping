# MISSION: TRIAGE-BRIDGE-ALIGN-001 — 10x Master Plan
## Full Alignment of MCP Bridge + Backend for LangSmith Email Triage Agent
## Date: 2026-02-23
## Classification: Feature Gap + Bug Fix + Reliability Hardening (Backend + Bridge, L)
## Prerequisite: CHAT-CONTROL-SURFACE-001, SYSTEM-MATURITY-REMEDIATION-001
## Successor: None (enables full hourly cron triage)

---

# 3-PASS ESCALATION ANALYSIS

---

## Pass 1 — Full-Stack Correctness & Contract Integrity

### Finding P1-F01: `actions` vs `delegated_tasks` — Two Disjoint Systems

**Problem:** The original plan proposes `POST /api/actions` to insert into `zakops.actions`. But the bridge tool `zakops_create_action` sends a payload with `requires_human_review` (line 1084) and expects a response shaped `{"action": {"action_id": ..., "status": ...}}` (lines 1099-1100). Meanwhile, the existing `actions` table has `requires_approval` (not `requires_human_review`), and the approval workflow uses `POST /api/actions/{id}/approve` which transitions `pending_approval → queued`. The `delegated_tasks` table is an entirely separate system with its own API (`/api/delegation/tasks`), its own status machine, and NO FK to `actions`.

**Root Cause:** The original plan assumed a simple INSERT, but the bridge expects a specific response shape and field mapping that doesn't match the existing table schema. The field name mismatch (`requires_human_review` in bridge vs `requires_approval` in DB) will cause silent data loss unless explicitly mapped.

**Fix:** The new `POST /api/actions` endpoint must:
1. Accept the bridge payload with `requires_human_review` and map it to `requires_approval`
2. Accept `source` and `created_by` fields, map them to `agent_type` and `actor` columns
3. Accept `inputs` and map to `agent_config` JSONB column
4. Return the response in the exact shape the bridge expects: `{"action": {"action_id": "...", "status": "..."}}`
5. Generate `action_id` using the `act-{uuid.hex[:12]}` pattern matching existing records

**Acceptance Criteria:** `zakops_create_action` via bridge returns `{"success": true, "action_id": "act-...", "status": "pending_approval"}` with the record verifiable in `zakops.actions`.

**Gate:** `psql -U zakops -d zakops -c "SELECT action_id, action_type, requires_approval, agent_type FROM zakops.actions ORDER BY created_at DESC LIMIT 1;"`

**Rollback:** `DELETE FROM zakops.actions WHERE agent_type = 'langsmith_bridge' AND created_at > '{deployment_time}';`

---

### Finding P1-F02: `deal_events` with `deal_id=NULL` — Orphan Event Problem

**Problem:** The original plan stores triage run reports in `deal_events` with `deal_id=NULL`. While the DB allows this (FK is nullable), it creates a semantic problem: `deal_events` is indexed by `deal_id` and the existing `ON DELETE CASCADE` means NULL-id events survive forever with no cleanup path. The `record_deal_event()` PL/pgSQL function signature takes `p_deal_id` as its first parameter — passing NULL works but is semantically misleading. More critically, queries like `SELECT * FROM zakops.deal_events WHERE deal_id = $1` will never find these orphaned events; they require `WHERE deal_id IS NULL AND event_type LIKE 'triage_run.%'`.

**Root Cause:** `deal_events` was designed for deal-scoped events, not system-level run reports. Using it for triage runs is a semantic mismatch that creates query complexity and cleanup problems.

**Fix:** Instead of raw `deal_events` insertion, create a thin wrapper:
1. Add a dedicated index: `CREATE INDEX idx_deal_events_triage_runs ON zakops.deal_events(event_type, created_at DESC) WHERE deal_id IS NULL` — this is a partial index that accelerates triage-run queries without affecting deal-scoped queries
2. Wrap the INSERT in a helper that enforces `event_type` naming convention (`triage_run.completed`, `triage_run.failed`)
3. The `GET /api/triage/runs` endpoint uses this partial index for efficient retrieval
4. Add a periodic cleanup note: triage run events older than 90 days can be purged without affecting deal data

**Acceptance Criteria:** `GET /api/triage/runs` returns results in < 100ms even with 10,000+ deal_events rows, because it uses the partial index.

**Gate:** `EXPLAIN ANALYZE SELECT * FROM zakops.deal_events WHERE deal_id IS NULL AND event_type LIKE 'triage_run.%' ORDER BY created_at DESC LIMIT 20;` — must show Index Scan on the partial index.

**Rollback:** Drop the partial index. Existing data is unaffected.

---

### Finding P1-F03: `zakops_approve_quarantine` — Wrong Endpoint, Missing Payload, Missing Parameters

**Problem:** The bridge calls `POST /api/actions/quarantine/{action_id}/approve` with NO body and expects HTTP 200. The actual backend endpoint is `POST /api/quarantine/{item_id}/process` which requires a JSON body with `action: "approve"` (validated by regex `^(approve|reject|escalate)$`), `processed_by` string, and optionally `deal_id`, `notes`, `corrections`, and `expected_version` for optimistic locking. The bridge tool accepts only `action_id: str` — no `deal_id`, no `reason`, no `notes`, no `corrections`.

**Root Cause:** The bridge tool was written against a spec that never existed. The backend never had `/api/actions/quarantine/{id}/approve`. There's a different endpoint (`POST /api/actions/{action_id}/approve`) for the HITL action approval workflow, which is a completely different concept.

**Fix:**
1. Change bridge endpoint to `POST {DEAL_API_URL}/api/quarantine/{item_id}/process`
2. Add parameters to the bridge tool: `deal_id: Optional[str] = None`, `notes: Optional[str] = None`, `corrections: Optional[dict] = None`
3. Rename parameter from `action_id` to `item_id` for clarity (this is a quarantine item UUID, not an action ID)
4. Send correct payload: `{"action": "approve", "processed_by": "langsmith_agent", "deal_id": deal_id, "notes": notes, "corrections": corrections}`
5. Accept both 200 and 201 (deal creation returns relevant data)
6. Parse the correct response shape: `{"status": "approved", "item_id": str, "deal_id": str, "deal_created": bool, "thread_linked": bool}`

**Acceptance Criteria:** Approving a pending quarantine item via bridge creates/links a deal and returns the deal_id.

**Gate:** Insert a test quarantine item, approve it via bridge, verify deal exists in `zakops.deals`.

**Rollback:** Revert bridge code changes. Quarantine items are unaffected (approval is idempotent — re-approving a non-pending item returns 409).

---

### Finding P1-F04: `zakops_report_task_result` — UUID Crash is in the BACKEND, Not the Bridge

**Problem:** The original plan says "Add UUID detection branch in the bridge." But the actual crash happens at **backend main.py line 3887**: `uuid.UUID(task_id)` raises `ValueError` before any query executes. The bridge at line 1425 passes `task_id` as a raw string in the URL path — no UUID parsing in the bridge whatsoever. The fix must address BOTH sides: (a) the bridge must route non-UUID task IDs to the new triage runs endpoint, AND (b) the backend must gracefully handle non-UUID strings in all `/api/tasks/{task_id}/*` endpoints (there are 9+ locations with this vulnerability: lines 3887, 3926, 3960, 4018, 4038, 4053, 4075, 4237, 4319, 4375, 4400).

**Root Cause:** Backend assumes all task IDs are UUIDs because `delegated_tasks.id` is UUID type. No input validation at the HTTP layer.

**Fix (two-part):**
1. **Bridge (primary):** Add UUID detection — non-UUID task IDs route to `POST /api/triage/runs`; UUID task IDs go to existing `POST /api/tasks/{task_id}/result`
2. **Backend (defense-in-depth):** Add a try/except around `uuid.UUID(task_id)` at the top of every `/api/tasks/{task_id}/*` endpoint, returning HTTP 400 "Invalid task ID format: must be UUID" instead of unhandled 500. This is a single reusable helper:
```
def parse_task_uuid(task_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(400, detail=f"Invalid task ID: {task_id} is not a UUID")
```

**Acceptance Criteria:** (a) Cron-style task IDs routed to triage runs. (b) Random strings sent directly to `/api/tasks/garbage/result` return 400, not 500.

**Gate:** `curl -X POST localhost:8091/api/tasks/not-a-uuid/result -H "Content-Type: application/json" -d '{"status":"completed"}' -w '\n%{http_code}'` — must return 400.

**Rollback:** Revert bridge routing changes; backend validation is purely additive and can stay.

---

### Finding P1-F05: `delegate_actions` Flag — Enabling Has Uneven Coverage

**Problem:** The original plan says "enable `delegate_actions` to unblock `zakops_claim_action` and `zakops_renew_action_lease`." But the audit reveals that `delegate_actions=false` only gates 4 locations: `POST /api/deals/{deal_id}/tasks` (3813), `POST /api/delegation/tasks` (4168), `POST /api/tasks/{task_id}/message` (4369), and `_maybe_create_backfill_task` (3628). The `/api/tasks/{task_id}/claim`, `/renew-lease`, `/result`, `/retry`, and `/confirm` endpoints are NOT gated. So enabling the flag primarily unblocks task CREATION, not task operations. The bridge tools `zakops_claim_action` and `zakops_renew_action_lease` will work IF there are tasks to claim — but no tasks will exist unless something creates them.

**Root Cause:** The flag gates task creation, not task operations. The claim/renew tools fail with "task not found" when no tasks exist, not with 503.

**Fix:** The plan must clarify:
1. Enabling `delegate_actions` unblocks: delegation task creation (bridge and backend), backfill task creation, task message posting
2. The bridge tools `zakops_claim_action` and `zakops_renew_action_lease` will return "task not found" (404) rather than 503 after enabling — they need EXISTING delegated tasks to operate on
3. For the triage agent, these tools become useful ONLY after: (a) `delegate_actions=true`, AND (b) something creates delegated tasks (either via `POST /api/delegation/tasks` or the quarantine processing pipeline)
4. Verify no unintended side effects: enabling the flag also starts the LeaseReaper background task, which reaps expired leases every 30 seconds

**Acceptance Criteria:** After enabling, `POST /api/delegation/tasks` returns 201 (not 503). LeaseReaper is running. No unexpected background activity.

**Gate:** `psql -U zakops -d zakops -c "SELECT name, enabled FROM zakops.feature_flags WHERE name='delegate_actions';"` AND `docker logs zakops-backend-1 --tail 20 2>&1 | grep -i 'lease.*reaper'`

**Rollback:** `UPDATE zakops.feature_flags SET enabled=false WHERE name='delegate_actions';` — takes effect within 1s TTL.

---

### Finding P1-F06: Route Ordering Constraint for New Endpoints

**Problem:** The original plan mentions the route ordering rule but doesn't verify that existing routes won't shadow the new ones. The backend already has `GET /api/actions/{action_id}` (parameterized) — if `POST /api/actions` is added AFTER it in the code, FastAPI's route matching could still work (different HTTP method), but the plan doesn't verify whether `POST /api/actions/create` style routes would be needed, or whether the existing `GET /api/actions/quarantine` (line 1298) could interfere with the new GET route patterns.

**Root Cause:** FastAPI matches routes top-to-bottom for the same method. POST and GET are separate, but compound paths need checking.

**Fix:** New routes must be inserted at specific locations:
- `POST /api/actions` → BEFORE `GET /api/actions/{action_id}` (same pattern as the plan states, but verify placement line number)
- `POST /api/triage/runs` → NEW route group, no conflict
- `GET /api/triage/runs` → NEW route group, no conflict
- No new `{id}` parameterized routes needed

**Acceptance Criteria:** All routes respond correctly — no shadowing verified by `curl -sf http://localhost:8091/openapi.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(p) for p in sorted(d['paths'].keys()) if '/actions' in p or '/triage' in p]"`.

**Gate:** OpenAPI spec includes all new routes.

**Rollback:** Remove route definitions.

---

### Revised Invariants

**Triage Run Reporting:**
- Every triage run MUST have a unique `run_id` (enforced by idempotency — see Pass 2)
- Triage runs are stored in `deal_events` with `deal_id=NULL`, `event_type IN ('triage_run.completed', 'triage_run.failed')`, `event_source='langsmith_bridge'`
- The partial index `idx_deal_events_triage_runs` ensures efficient retrieval
- Bridge routes non-UUID task IDs to `POST /api/triage/runs`; UUID task IDs to existing delegation endpoint

**Action Creation:**
- `POST /api/actions` creates a record in `zakops.actions` (NOT `delegated_tasks`)
- Bridge field `requires_human_review` maps to DB column `requires_approval`
- Bridge field `source` maps to `agent_type`; `created_by` maps to `actor` in the event record
- Status starts at `pending_approval` (if requires_approval=true) or `queued` (if false)
- Actions are proposals — they do NOT auto-execute. Execution requires explicit `POST /api/actions/{id}/execute`

**Quarantine Approval Routing:**
- Bridge calls `POST /api/quarantine/{item_id}/process` with `action: "approve"`
- Only items with `status IN ('pending', 'escalated')` can be approved (backend enforces)
- Optimistic locking via `expected_version` prevents double-approval (409 on conflict)
- Approval auto-creates a deal if `deal_id` is not provided

**Delegation Task Lifecycle:**
- Task creation gated by `delegate_actions` flag (503 when disabled)
- Task operations (claim, renew, result, retry, confirm) are NOT flag-gated
- Task status machine: `pending → queued → executing → completed|failed|dead_letter`
- Lease holder verification on result submission (403 if mismatch)

---

## Pass 2 — Reliability Engineering, Failure Modes, and Security

### A) Failure Mode Review

| # | Scenario | Current Behavior | Required Behavior | Fix |
|---|----------|-----------------|-------------------|-----|
| FM-1 | Bridge up, backend down | Each tool returns `{"error": "Deal API error: ConnectError"}` | Same, but health endpoint reflects degraded. LangSmith sees errors and can skip ZakOps tools | Already handled — verify health check shows `deal_api: unhealthy` |
| FM-2 | Backend up, DB degraded | Backend returns 500 on all DB queries | Bridge returns `{"error": "HTTP 500"}` with no detail | **Fix:** Backend should return structured error; bridge should include response body in error |
| FM-3 | RAG down | `rag_query_local` returns `{"error": "RAG API unreachable"}` | Triage should STILL RUN — RAG is enrichment only, not critical path | **Fix:** Document that RAG tools are optional enrichment; triage pipeline must not require them |
| FM-4 | Duplicate `run_id` submitted | No dedup — creates duplicate events | Idempotent — second POST returns the existing event_id | **Fix:** See P2-F01 below |
| FM-5 | API keys missing/invalid | Bridge sends empty `X-API-Key` header → backend returns 401 | Bridge should fail-fast at startup if `ZAKOPS_API_KEY` is empty | **Fix:** See P2-F03 below |
| FM-6 | Overlapping cron runs | Two cron runs with different `run_id`s process same emails | Acceptable — Gmail labels prevent double-classification | Document as expected behavior |
| FM-7 | Partial results reported | Agent sends `run_id` with `emails_processed=5` then crashes; next run reports `emails_processed=8` for same emails | Original event persists; new run creates new event | Acceptable — events are append-only log |

### B) Idempotency & Deduplication

### Finding P2-F01: Triage Run Report Idempotency

**Problem:** If the LangSmith agent retries `zakops_report_task_result` (which routes to `POST /api/triage/runs`), a duplicate event is created in `deal_events`. The backend IdempotencyMiddleware is active but only triggers when the client sends an `Idempotency-Key` header — the bridge does NOT send this header.

**Root Cause:** The bridge creates a new `httpx.Client` per request with no idempotency header.

**Fix:**
1. The `POST /api/triage/runs` endpoint implements application-level dedup: `SELECT id FROM zakops.deal_events WHERE event_type LIKE 'triage_run.%' AND payload->>'run_id' = $1` — if found, return the existing event_id with HTTP 200 (not 201)
2. This is simpler and more reliable than the middleware approach because the dedup key (`run_id`) is domain-specific

**Acceptance Criteria:** Posting the same `run_id` twice returns the same `event_id` both times. Second call is HTTP 200, not 201.

**Gate:** `curl -X POST ... -d '{"run_id":"dedup_test"}' && curl -X POST ... -d '{"run_id":"dedup_test"}'` — both return same event_id.

**Rollback:** Remove the SELECT check; endpoint reverts to always-INSERT.

---

### Finding P2-F02: Action Creation Deduplication

**Problem:** If the LangSmith agent retries `zakops_create_action`, duplicate actions are created. There's no natural dedup key — `action_type + title + deal_id` is not guaranteed unique.

**Root Cause:** Actions have no idempotency mechanism.

**Fix:**
1. Accept an optional `idempotency_key` field in the `ActionCreate` payload
2. If provided, check `SELECT action_id FROM zakops.actions WHERE correlation_id = $1` (reuse the existing `correlation_id` UUID column for this purpose)
3. If found, return existing action with HTTP 200
4. If not provided, generate a new action (current behavior) — backward compatible
5. Bridge should generate and send `idempotency_key = f"{action_type}:{title}:{deal_id or 'none'}:{run_id}"` to prevent cross-retry duplicates

**Acceptance Criteria:** Posting with the same `idempotency_key` twice returns the same `action_id`.

**Gate:** Two identical POST requests with same idempotency key → same action_id returned.

**Rollback:** Remove the SELECT check; ignore `idempotency_key` if present.

---

### Finding P2-F03: Bridge Startup Validation — Missing API Key Fail-Fast

**Problem:** If `ZAKOPS_API_KEY` is empty/missing, the bridge starts successfully but ALL write operations fail with HTTP 401. This was the actual failure mode encountered in this session — it took multiple cron runs to diagnose.

**Root Cause:** The bridge reads `BACKEND_API_KEY = os.getenv("ZAKOPS_API_KEY", "")` with an empty string default. No validation at startup.

**Fix:**
1. Add startup validation in the bridge server initialization:
```python
if not BACKEND_API_KEY:
    logger.critical("ZAKOPS_API_KEY is not set — all backend writes will fail")
    # Don't crash — allow read-only operation — but log prominently
```
2. Include API key presence in the health check response: `"backend_auth": "configured"` vs `"backend_auth": "MISSING — writes will fail"`
3. This makes the failure visible immediately via `/health` instead of requiring a failed cron run

**Acceptance Criteria:** Health endpoint shows `backend_auth` status. Missing key produces a CRITICAL log at startup.

**Gate:** `curl -sf http://127.0.0.1:9100/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['checks'].get('backend_auth', 'NOT_PRESENT'))"` — must show "configured".

**Rollback:** Remove the startup check. Health check reverts to current fields.

---

### Finding P2-F04: Bridge Error Responses Lack Backend Detail

**Problem:** When the backend returns an error, the bridge typically returns only `{"error": "Failed to create action: HTTP 405"}` — discarding the response body which contains the actual error message. This makes debugging from LangSmith traces extremely difficult.

**Root Cause:** Bridge error handling pattern: `return {"error": f"Failed to ...: HTTP {resp.status_code}"}` without reading `resp.text` or `resp.json()`.

**Fix:** For all tool error paths, include a truncated response body:
```python
if resp.status_code not in (200, 201):
    detail = ""
    try:
        detail = resp.json().get("detail", resp.text[:200])
    except Exception:
        detail = resp.text[:200]
    return {"error": f"HTTP {resp.status_code}: {detail}"}
```

**Acceptance Criteria:** Error responses include the backend's error detail string.

**Gate:** Trigger a known error (e.g., create action with invalid deal_id) → error response includes "Deal not found" text.

**Rollback:** Revert to simple HTTP status code errors.

---

### Finding P2-F05: No Correlation ID Propagation on Most Tools

**Problem:** Only 2 of 24 tools propagate correlation IDs to the backend (inject_quarantine via header, claim_action via body). All others use local-only correlation IDs for bridge logging. End-to-end tracing from LangSmith → bridge → backend is broken for 22 tools.

**Root Cause:** Correlation ID handling was added ad-hoc to individual tools, never standardized.

**Fix:**
1. For the 3 new/modified endpoints only (scope fence — don't refactor all 24 tools in this mission):
   - `POST /api/triage/runs` — include `X-Correlation-ID` header with the bridge-generated correlation ID
   - `POST /api/actions` — include `X-Correlation-ID` header
   - `POST /api/quarantine/{id}/process` — include `X-Correlation-ID` header
2. Store correlation_id in the `deal_events.payload` for triage runs
3. Store correlation_id in `actions.correlation_id` column (already exists as UUID type)

**Acceptance Criteria:** New endpoints log correlation IDs end-to-end. Triage run events contain correlation_id in payload.

**Gate:** Bridge log entry and backend deal_event for same operation share the same correlation_id.

**Rollback:** Remove header propagation; bridge still generates local correlation IDs.

---

### Finding P2-F06: Rate Limiting Gap on New Write Endpoints

**Problem:** Only `POST /api/quarantine` has rate limiting (120/min). The new `POST /api/actions` and `POST /api/triage/runs` have no rate limiting. A misbehaving agent could create thousands of actions per minute.

**Root Cause:** Rate limiting was added specifically to quarantine injection and never generalized.

**Fix:**
1. Apply `injection_rate_limiter` (120/min) to `POST /api/triage/runs` — same rate as quarantine injection
2. Apply `general_rate_limiter` (60/min) to `POST /api/actions` — lower because action creation should be deliberate
3. Both use `client_ip` as the rate limit key (same pattern as quarantine)

**Acceptance Criteria:** Exceeding rate limit returns HTTP 429 with `Retry-After: 60`.

**Gate:** Fire 61 rapid requests to `POST /api/actions` → 61st returns 429.

**Rollback:** Remove rate limit calls from the endpoints.

---

### C) Security and Auditability

### Finding P2-F07: Audit Trail for Triage Runs and Actions

**Problem:** The original plan stores triage runs in `deal_events` but doesn't specify how to trace back to the LangSmith trace. Actions created by the agent have `agent_type` and `agent_config` but no direct trace URL.

**Fix:**
1. Triage run `payload` JSONB includes: `run_id`, `langsmith_run_id`, `langsmith_trace_url`, `agent_identity: "langsmith_agent"`, `bridge_correlation_id`
2. Action creation includes `langsmith_trace_url` in `agent_config` JSONB if provided by bridge
3. All audit fields are queryable via JSONB operators

### Finding P2-F08: Email Content Exposure in Logs

**Problem:** The bridge logs tool calls to `agent_bridge.jsonl`. If the agent passes email subjects or body previews as part of action `inputs` or triage run `result`, these are logged in plaintext.

**Fix:**
1. The `log_tool_call` function should redact known sensitive fields: `body_preview`, `raw_content`, `email_body`
2. Bridge logs should NEVER include full email content — only metadata (sender, subject truncated to 50 chars, message_id)
3. Add to bridge logging: `if "body" in kwargs.get("inputs", {}): kwargs["inputs"]["body"] = "[REDACTED]"`

**Acceptance Criteria:** `grep -i "body_preview\|raw_content\|email_body" /home/zaks/DataRoom/.deal-registry/logs/agent_bridge.jsonl` returns zero matches after deployment.

---

### Observability Requirements

| Requirement | Implementation | Location |
|------------|----------------|----------|
| Structured logs | Already implemented via JSONLogHandler | Bridge `agent_bridge.jsonl` |
| Correlation IDs | Generate per-request in bridge, propagate to backend via `X-Correlation-ID` header | Bridge → Backend |
| Trace links | Store `langsmith_run_id` and `langsmith_trace_url` in triage run payload and action agent_config | Backend DB |
| Success/failure counters | Add to health endpoint: `{"stats": {"triage_runs_24h": N, "actions_created_24h": N, "errors_24h": N}}` | Backend `/api/triage/runs` GET response metadata |
| Latency metrics | Bridge logs already include timestamp; add `duration_ms` to tool call log entries | Bridge logging |

---

## Pass 3 — Operational Excellence + Scalability + World-Class Upgrades

### Finding P3-F01: End-to-End Health Command

**Problem:** Currently, checking system health requires 4+ separate curl commands. There's no single command that validates all dependencies and prints actionable diagnostics.

**Fix:** Add a `make triage-health` target that:
```bash
#!/bin/bash
echo "=== TRIAGE PIPELINE HEALTH ==="
echo ""

# 1. Backend
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:8091/health)
echo "Backend (8091): ${STATUS:-UNREACHABLE}"

# 2. Bridge
BRIDGE=$(curl -sf http://127.0.0.1:9100/health 2>/dev/null)
echo "Bridge (9100): $(echo $BRIDGE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'])" 2>/dev/null || echo 'UNREACHABLE')"

# 3. RAG
RAG=$(curl -sf http://localhost:8052/rag/stats 2>/dev/null)
echo "RAG (8052): $(echo $RAG | python3 -c "import sys,json; d=json.load(sys.stdin); print('healthy' if d.get('database_connected') else 'DEGRADED')" 2>/dev/null || echo 'UNREACHABLE')"

# 4. Feature flags
echo ""
echo "=== FEATURE FLAGS ==="
psql -U zakops -d zakops -t -c "SELECT name || ': ' || enabled FROM zakops.feature_flags ORDER BY name;" 2>/dev/null || echo "DB UNREACHABLE"

# 5. Recent triage runs
echo ""
echo "=== LAST 5 TRIAGE RUNS ==="
psql -U zakops -d zakops -t -c "SELECT payload->>'run_id' AS run_id, payload->>'status' AS status, payload->>'emails_processed' AS emails, created_at FROM zakops.deal_events WHERE deal_id IS NULL AND event_type LIKE 'triage_run.%' ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "No runs found"

# 6. Tool count
TOOLS=$(echo $BRIDGE | python3 -c "import sys,json; print(json.load(sys.stdin).get('tools_count', 'N/A'))" 2>/dev/null)
echo ""
echo "Bridge tools: $TOOLS"
echo "=== END ==="
```

**Acceptance Criteria:** `make triage-health` prints actionable status for all 4 services + flags + recent runs in < 5 seconds.

---

### Finding P3-F02: 24-Tool Smoke Test Harness

**Problem:** No automated way to verify all 24 tools work. The current verification is manual curl commands.

**Fix:** Create `/home/zaks/zakops-agent-api/tools/ops/smoke-test-bridge.sh`:
- For each of the 24 tools, sends a minimal valid request via the bridge MCP endpoint
- Read-only tools: verify HTTP 200 with valid JSON
- Write tools: verify with deterministic fixtures, then clean up
- Output: `PASS/FAIL` per tool, total count, elapsed time
- Gate-compatible: exits 0 if all pass, exits 1 if any fail

**Acceptance Criteria:** `bash tools/ops/smoke-test-bridge.sh` returns 24/24 PASS.

---

### Finding P3-F03: RAG Self-Healing

**Problem:** RAG service has NO Docker healthcheck. If rag-db crashes at boot, rag-rest-api gets a null pool and never retries. Manual restart is required.

**Fix:**
1. Add Docker healthcheck to `rag-db` in docker-compose.yml:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```
2. Add Docker healthcheck to `rag-rest-api`:
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -sf http://localhost:8080/rag/stats || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
```
3. Add `depends_on: rag-db: condition: service_healthy` to rag-rest-api
4. This ensures rag-rest-api only starts after rag-db is accepting connections

**Acceptance Criteria:** After `docker compose restart rag-db`, rag-rest-api auto-recovers without manual intervention.

---

### Finding P3-F04: Progressive Rollout Strategy

**Problem:** The original plan enables `delegate_actions` system-wide in one step. This is a blast-radius concern — it enables ALL delegation features simultaneously.

**Fix:** Define a staged rollout:
1. **Stage 1 (current):** `shadow_mode=true`, `delegate_actions=false` — triage runs, classifications, label-only. Zero delegation.
2. **Stage 2 (this mission):** `delegate_actions=true`, `shadow_mode=true` — delegation tools available, but quarantine items still marked `langsmith_shadow`. Operator can see and verify before trusting.
3. **Stage 3 (future):** `shadow_mode=false` — full autonomous operation. Quarantine items are real. Requires operator sign-off.
4. Document this progression in runbooks so the next operator knows the sequence.

**Acceptance Criteria:** After this mission, system is at Stage 2. Operator knows Stage 3 requirements.

---

### Finding P3-F05: Triage Run Dashboard Visibility

**Problem:** Triage runs stored in `deal_events` are invisible to operators unless they run SQL queries. There's no dashboard view or API response optimized for operators.

**Fix:** The `GET /api/triage/runs` response shape should be operator-friendly:
```json
{
  "runs": [
    {
      "event_id": "uuid",
      "run_id": "cron_2026-02-23T00:00:00-0600",
      "status": "completed",
      "emails_processed": 10,
      "classifications": {"DEAL_SIGNAL": 2, "NEWSLETTER": 5, "OPERATIONAL": 3},
      "injections": {"attempted": 2, "succeeded": 2, "failed": 0},
      "errors": [],
      "duration_ms": 45000,
      "langsmith_trace_url": "https://...",
      "created_at": "2026-02-23T06:00:05Z"
    }
  ],
  "total": 47,
  "stats": {
    "runs_24h": 24,
    "success_rate": 0.96,
    "avg_emails_per_run": 8.2,
    "total_injections_24h": 12
  }
}
```

**Acceptance Criteria:** `GET /api/triage/runs` returns runs with stats summary. Response is structured for future dashboard consumption.

---

### Production Readiness Checklist

| Category | Requirement | Status After Mission |
|----------|-------------|---------------------|
| **Rollback** | Every phase has exact rollback commands | Included in each phase |
| **Runbooks** | Triage pipeline restart procedure documented | Add to RUNBOOKS.md |
| **Alerting** | Health endpoint reflects all dependencies | Bridge `/health` updated |
| **Log redaction** | No email content in bridge logs | Enforced in `log_tool_call` |
| **Rate limiting** | Write endpoints capped | 120/min (triage), 60/min (actions) |
| **Idempotency** | Duplicate run reports handled | `run_id` dedup on triage runs |
| **Input validation** | Non-UUID task IDs return 400, not 500 | Backend helper function |
| **Auth verification** | Missing API key visible in health check | Bridge startup validation |
| **Partial failure** | RAG down doesn't block triage | Documented as optional enrichment |
| **Monitoring** | Recent run history queryable | `GET /api/triage/runs` with stats |
| **Feature flag safety** | Progressive rollout documented | Stage 1 → 2 → 3 defined |
| **Cleanup** | Orphaned events have purge path | 90-day retention note |

---

# 10x MASTER PLAN (Consolidated)

---

## Mission Objective

Bring ALL 24 MCP bridge tools from 62% (15/24) to 100% (24/24) working by: adding 3 missing backend endpoints, fixing 2 bridge tool routing errors, enabling 1 feature flag, restarting 1 degraded service, and hardening reliability with idempotency, input validation, correlation ID propagation, rate limiting, startup validation, and operator visibility. This mission also establishes the triage run reporting infrastructure that enables observability into the hourly cron cycle.

**What this is NOT:** This is NOT a dashboard build (no new UI pages). This is NOT a schema migration (no new tables — reuses `deal_events` and `actions`). This is NOT a refactor of the 22 other tools (scope-fenced to the 9 broken tools + 3 new endpoints).

---

## Glossary

| Term | Definition |
|------|-----------|
| Bridge | MCP server at port 9100 (`apps/agent-api/mcp_bridge/server.py`) — proxies LangSmith agent calls to backend |
| Triage run | A single hourly cron execution of the LangSmith email triage agent |
| Quarantine item | An email classified by the triage agent, awaiting human approval before becoming a deal |
| Delegation task | A `zakops.delegated_tasks` record — agent-to-agent work assignment with lease management |
| Action | A `zakops.actions` record — a human-visible proposal for a state change, requiring approval |
| Shadow mode | `shadow_mode=true` — triage outputs tagged `langsmith_shadow`, visible but not treated as production |

---

## Architectural Constraints

- **Route ordering:** Static routes BEFORE parameterized `{id}` routes in `main.py`
- **API key auth on writes:** All new POST endpoints use `X-API-Key` header via existing `APIKeyMiddleware`
- **Contract surface discipline:** After backend API changes: `make update-spec → make sync-types → npx tsc --noEmit`
- **No new tables/migrations:** Reuse `deal_events` (triage runs) and `actions` (action proposals)
- **Port 8090 FORBIDDEN**
- **Generated files NEVER edited directly**
- **Bridge backward-compatible:** UUID task IDs MUST still route to existing delegation endpoint

---

## Anti-Pattern Examples

### WRONG: Bridge swallows backend error detail
```python
if resp.status_code != 200:
    return {"error": f"Failed to create action: HTTP {resp.status_code}"}
    # Agent sees "HTTP 405" with no context
```

### RIGHT: Include backend error detail
```python
if resp.status_code not in (200, 201):
    detail = ""
    try:
        detail = resp.json().get("detail", resp.text[:200])
    except Exception:
        detail = resp.text[:200]
    return {"error": f"HTTP {resp.status_code}: {detail}"}
    # Agent sees "HTTP 405: Method Not Allowed" — actionable
```

### WRONG: Assume task_id is always UUID
```python
task = await conn.fetchrow("SELECT * FROM ... WHERE id = $1", uuid.UUID(task_id))
# Crashes with ValueError on "cron_2026-02-22T23:58:31"
```

### RIGHT: Validate and return 400
```python
try:
    task_uuid = uuid.UUID(task_id)
except ValueError:
    raise HTTPException(400, detail=f"Invalid task ID: {task_id} is not a UUID")
task = await conn.fetchrow("SELECT * FROM ... WHERE id = $1", task_uuid)
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | New `POST /api/actions` returns response shape the bridge doesn't expect → `action_id` is None | HIGH | Agent sees success but action_id is null | P1 gate verifies exact response shape via bridge round-trip |
| 2 | Enabling `delegate_actions` starts LeaseReaper which interferes with existing tasks | MEDIUM | Unexpected task status changes | P3 gate checks for unexpected task status changes after flag enable |
| 3 | RAG restart fails because rag-db has corrupt data from prior crash | MEDIUM | 2 tools remain broken | P5 decision tree: if restart fails, check logs, attempt fresh init |
| 4 | Bridge .env file gets CRLF line endings → service fails to read env vars | MEDIUM | All tools broken | WSL safety checklist after any .env write |
| 5 | Partial index migration fails silently on existing large deal_events table | LOW | Triage run queries are slow | P1 gate runs EXPLAIN ANALYZE to verify index usage |

---

## Dependency Graph

```
Phase 0 (Baseline)
    │
    ▼
Phase 1 (Backend Endpoints)
    │
    ├──────────────────────┐
    ▼                      ▼
Phase 2 (Feature Flags)   Phase 3 (Bridge Fixes)
    │                      │
    └──────┬───────────────┘
           ▼
    Phase 4 (Backend Hardening)
           │
           ▼
    Phase 5 (RAG Recovery)
           │
           ▼
    Phase 6 (Full Validation + Bookkeeping)
```

Phases 2 and 3 can execute in parallel after Phase 1 completes.

---

## Phase 0 — Discovery & Baseline Verification
**Complexity:** S | **Estimated touch points:** 0

**Purpose:** Verify current state matches the audit before changing anything.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks

- P0-01: **Verify backend health** — `curl -sf http://localhost:8091/health`
  - **Checkpoint:** HTTP 200

- P0-02: **Verify bridge health** — `curl -sf http://127.0.0.1:9100/health | python3 -m json.tool`
  - **Checkpoint:** Shows 24 tools, status "degraded" (expected due to RAG)

- P0-03: **Verify tool failure states match audit** — Confirm:
  - `zakops_create_action` → 405 (POST /api/actions missing)
  - `zakops_approve_quarantine` → 404 or error (wrong path)
  - `zakops_report_task_result` with cron ID → 500 (UUID crash)
  - `delegate_actions` flag → false
  - RAG stats → unreachable or 503

- P0-04: **Run `make validate-local`** — Must PASS before any changes

- P0-05: **Identify affected contract surfaces:**
  - Surface 3 (Agent OpenAPI) — if bridge tool signatures change
  - Surface 15 (MCP Bridge Tool Interface) — bridge routing changes
  - Surface 16 (Email Triage Injection) — triage run reporting

### Gate P0
- Backend healthy (8091)
- Bridge shows 24 tools
- `make validate-local` PASS
- All failure states confirmed

### Rollback Plan
No changes to roll back.

---

## Phase 1 — Backend: Add Missing Endpoints + Partial Index
**Complexity:** M | **Estimated touch points:** 1 file + 1 migration

**Purpose:** Add `POST /api/triage/runs`, `GET /api/triage/runs`, `POST /api/actions`, and the partial index for efficient triage run queries.

### Blast Radius
- **Services affected:** Backend (8091)
- **Pages affected:** None
- **Downstream consumers:** Bridge (via HTTP), LangSmith agent (indirectly)

### Tasks

- P1-01: **Add partial index for triage run queries**
  - File: `/home/zaks/zakops-agent-api/apps/backend/db/migrations/` — new migration file
  - SQL: `CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_deal_events_triage_runs ON zakops.deal_events(created_at DESC) WHERE deal_id IS NULL AND event_type LIKE 'triage_run.%';`
  - Apply via: `psql -U zakops -d zakops -f <migration_file>`
  - **Checkpoint:** `\di idx_deal_events_triage_runs` shows the index

- P1-02: **Add Pydantic models**
  - File: `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
  - Add `TriageRunReport` model with fields: `run_id`, `status`, `correlation_id`, `emails_processed`, `classifications`, `injections`, `labels_applied`, `errors`, `duration_ms`, `langsmith_run_id`, `langsmith_trace_url`, `agent_config`, `summary`
  - Add `ActionCreate` model with fields: `action_type`, `title`, `description`, `deal_id`, `inputs`, `source`, `created_by`, `requires_human_review` (mapped to DB `requires_approval`)

- P1-03: **Add `POST /api/triage/runs`** — Store cron run reports
  - Route placement: New `/api/triage/` group, no conflict with existing routes
  - Behavior: API key auth, application-level dedup on `run_id` (SELECT before INSERT), rate limit 120/min
  - Store in `deal_events`: `deal_id=NULL`, `event_type='triage_run.{status}'`, `event_source='langsmith_bridge'`, `actor='langsmith_agent'`, `payload=full report JSONB including run_id`
  - Return: `{"event_id": str, "run_id": str, "status": "stored"}` with HTTP 201 (new) or HTTP 200 (dedup)
  - **Checkpoint:** Verify with curl

- P1-04: **Add `GET /api/triage/runs`** — List recent runs with operator-friendly stats
  - Query: `SELECT * FROM zakops.deal_events WHERE deal_id IS NULL AND event_type LIKE 'triage_run.%' ORDER BY created_at DESC LIMIT $1 OFFSET $2`
  - Add 24h stats summary: runs count, success rate, avg emails per run, total injections
  - Pagination: `limit` (default 20), `offset` (default 0)

- P1-05: **Add `POST /api/actions`** — Create action proposals
  - Route placement: BEFORE `GET /api/actions/{action_id}` in main.py
  - Behavior: API key auth, rate limit 60/min, generate `action_id = f"act-{uuid.uuid4().hex[:12]}"`
  - Field mapping: `requires_human_review` → `requires_approval`, `source` → `agent_type`, `inputs` → `agent_config`
  - If `deal_id` provided, validate it exists (404 if not)
  - Insert into `zakops.actions`
  - If `deal_id` provided, record deal_event: `event_type='action_created'`
  - Support optional `idempotency_key` → stored as `correlation_id` UUID (if parseable) or hashed
  - Response shape: `{"action": {"action_id": str, "status": str, "requires_approval": bool}}`
  - Return HTTP 201 (new) or HTTP 200 (dedup via idempotency_key)
  - **Checkpoint:** Verify response shape matches bridge expectations at lines 1099-1100

### Decision Tree
- **IF** `deal_id` is provided AND deal does not exist → return 404 `{"detail": "Deal {deal_id} not found"}`
- **ELSE IF** `deal_id` is provided AND deal exists → create action + deal_event
- **ELSE** (no deal_id) → create action without deal_event

### Rollback Plan
1. Remove the 3 route definitions from main.py
2. Drop the partial index: `DROP INDEX IF EXISTS zakops.idx_deal_events_triage_runs;`
3. Any events/actions created remain in DB (harmless)
4. Rebuild backend: `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend`
5. Verify: `make validate-local`

### Gate P1
```bash
# Rebuild and restart backend
cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend
sleep 5

# Test triage run report (new)
curl -sf -X POST http://localhost:8091/api/triage/runs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"run_id":"gate_p1_test","emails_processed":2,"classifications":{"NEWSLETTER":2}}' | python3 -m json.tool
# Must return event_id

# Test dedup (same run_id)
curl -sf -X POST http://localhost:8091/api/triage/runs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"run_id":"gate_p1_test","emails_processed":2}' | python3 -m json.tool
# Must return same event_id

# Test list triage runs
curl -sf http://localhost:8091/api/triage/runs | python3 -m json.tool
# Must return runs array with stats

# Test create action
curl -sf -X POST http://localhost:8091/api/actions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"action_type":"FOLLOW_UP","title":"Test action"}' -w '\n%{http_code}'
# Must return 201 with {"action": {"action_id": "act-...", "status": "pending_approval"}}

# Verify index exists
psql -U zakops -d zakops -c "\di idx_deal_events_triage_runs"

# make validate-local still passes
cd /home/zaks/zakops-agent-api && make validate-local
```

---

## Phase 2 — Enable Feature Flags
**Complexity:** S | **Estimated touch points:** 0 (database only)

**Purpose:** Enable `delegate_actions` to unblock delegation task creation tools. This is Stage 2 of the progressive rollout (shadow mode remains on).

### Blast Radius
- **Services affected:** Backend (behavior change via flag read), Agent API (can now create tasks)
- **Pages affected:** None immediately
- **Downstream consumers:** Any code calling `POST /api/delegation/tasks` — previously blocked with 503, now succeeds

### Tasks

- P2-01: **Enable `delegate_actions` flag**
  - `psql -U zakops -d zakops -c "UPDATE zakops.feature_flags SET enabled=true, updated_by='TRIAGE-BRIDGE-ALIGN-001' WHERE name='delegate_actions';"`
  - **Checkpoint:** Flag enabled, LeaseReaper starts within 1 second

- P2-02: **Verify no unintended side effects**
  - Check LeaseReaper started: `docker logs zakops-backend-1 --tail 50 2>&1 | grep -i lease`
  - Check no tasks are reaped unexpectedly: `psql -U zakops -d zakops -c "SELECT COUNT(*) FROM zakops.delegated_tasks WHERE status = 'dead_letter';"`
  - Verify `shadow_mode=true` (unchanged): `psql -U zakops -d zakops -c "SELECT name, enabled FROM zakops.feature_flags ORDER BY name;"`

### Rollback Plan
1. `psql -U zakops -d zakops -c "UPDATE zakops.feature_flags SET enabled=false WHERE name='delegate_actions';"`
2. LeaseReaper stops within 30 seconds (next poll cycle)
3. No data changes to revert

### Gate P2
```bash
psql -U zakops -d zakops -c "SELECT name, enabled, updated_by FROM zakops.feature_flags ORDER BY name;"
# delegate_actions = true, updated_by = 'TRIAGE-BRIDGE-ALIGN-001'
# shadow_mode = true (unchanged)
# email_triage_writes_enabled = true (unchanged)

# Verify delegation endpoint no longer returns 503
curl -sf http://localhost:8091/api/delegation/types | python3 -m json.tool
# Returns 200 with 16 integration action types
```

---

## Phase 3 — Bridge: Fix Tool Routing + Hardening
**Complexity:** M | **Estimated touch points:** 1 file

**Purpose:** Fix `zakops_report_task_result` routing for cron IDs, fix `zakops_approve_quarantine` to call correct endpoint, add startup validation and improved error reporting.

### Blast Radius
- **Services affected:** Bridge (9100)
- **Pages affected:** None
- **Downstream consumers:** LangSmith agent (tool behavior changes)

### Tasks

- P3-01: **Add UUID detection + triage run routing to `zakops_report_task_result`**
  - File: `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py`
  - At the top of the function (after status validation, before the try block):
    ```python
    import re
    UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

    if not UUID_RE.match(task_id):
        # Non-UUID → cron run report, route to triage runs endpoint
        triage_payload = {
            "run_id": task_id,
            "status": status,
            "summary": feedback,
            "errors": [error] if error else [],
            "langsmith_run_id": langsmith_run_id,
            "langsmith_trace_url": langsmith_trace_url,
            **(result or {}),
        }
        correlation = str(uuid.uuid4())[:8]
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"{DEAL_API_URL}/api/triage/runs",
                    json=triage_payload,
                    headers={"X-API-Key": BACKEND_API_KEY, "X-Correlation-ID": correlation},
                )
                if resp.status_code not in (200, 201):
                    detail = resp.text[:200] if resp.text else ""
                    return {"error": f"Failed to store triage run: HTTP {resp.status_code}: {detail}"}
                data = resp.json()
            return {"success": True, "run_id": task_id, "event_id": data.get("event_id"), "message": "Triage run report stored"}
        except httpx.HTTPError as e:
            return {"error": f"Triage run storage error: {str(e)}"}
    # else: existing UUID path continues unchanged
    ```
  - **Checkpoint:** Verify the existing UUID path is untouched

- P3-02: **Fix `zakops_approve_quarantine`**
  - Change endpoint: `f"{DEAL_API_URL}/api/actions/quarantine/{action_id}/approve"` → `f"{DEAL_API_URL}/api/quarantine/{item_id}/process"`
  - Add parameters: `deal_id: Optional[str] = None`, `notes: Optional[str] = None`
  - Add payload: `{"action": "approve", "processed_by": "langsmith_agent", "deal_id": deal_id, "notes": notes or "Approved via LangSmith triage agent"}`
  - Accept 200 or 201 (not just 200)
  - Include correlation ID header
  - Parse response: `{"status": "approved", "item_id": ..., "deal_id": ..., "deal_created": bool}`
  - **Checkpoint:** Verify docstring and parameter names are updated

- P3-03: **Add startup validation for BACKEND_API_KEY**
  - After `BACKEND_API_KEY = os.getenv("ZAKOPS_API_KEY", "")` (line 53), add:
    ```python
    if not BACKEND_API_KEY:
        logging.critical("ZAKOPS_API_KEY is not set — all backend write operations will return 401")
    ```
  - In health endpoint, add `"backend_auth": "configured" if BACKEND_API_KEY else "MISSING"` to checks dict

- P3-04: **Improve error detail in tool responses** for `zakops_create_action` and `zakops_report_task_result`
  - When `resp.status_code not in (200, 201)`, include `resp.text[:200]` in error message

- P3-05: **Add correlation ID propagation** to `zakops_create_action` and the new triage run routing
  - Generate `correlation_id = str(uuid.uuid4())[:8]`
  - Include as `X-Correlation-ID` header in the HTTP request

- P3-06: **Restart bridge**
  - `sudo systemctl restart zakops-agent-bridge`

### Decision Tree
- **IF** `systemctl restart` fails → check `.env` for CRLF: `file /home/zaks/scripts/agent_bridge/.env`
- **ELSE IF** bridge starts but health shows 0 tools → check Python import errors: `journalctl -u zakops-agent-bridge --tail 50`
- **ELSE** → proceed to gate

### Rollback Plan
1. `git checkout -- apps/agent-api/mcp_bridge/server.py`
2. `sudo systemctl restart zakops-agent-bridge`
3. Verify: `curl -sf http://127.0.0.1:9100/health | python3 -m json.tool`

### Gate P3
```bash
# Verify bridge health
curl -sf http://127.0.0.1:9100/health | python3 -m json.tool
# Must show backend_auth: "configured", 24 tools

# Test report_task_result with cron-style ID (via bridge)
curl -sf -X POST http://127.0.0.1:9100/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"zakops_report_task_result","arguments":{"task_id":"cron_gate_p3_test","status":"completed","result":{"emails_processed":0}}}}'
# Must return success with event_id

# Test report_task_result with UUID still works
# (requires an existing delegated task — skip if none exist, verified in Phase 6)

# Verify approve_quarantine endpoint path changed (inspect logs or code)
grep -n "api/quarantine.*process" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
# Must match at least 1 line
```

---

## Phase 4 — Backend: Input Validation Hardening
**Complexity:** S | **Estimated touch points:** 1 file

**Purpose:** Add `parse_task_uuid()` helper to all `/api/tasks/{task_id}/*` endpoints, converting unhandled 500 → 400.

### Blast Radius
- **Services affected:** Backend (8091)
- **Pages affected:** None
- **Downstream consumers:** Bridge (improved error messages), any API consumer

### Tasks

- P4-01: **Add `parse_task_uuid()` helper function**
  - File: `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
  - Location: Near other helper functions
  ```python
  def parse_task_uuid(task_id: str) -> uuid.UUID:
      try:
          return uuid.UUID(task_id)
      except ValueError:
          raise HTTPException(status_code=400, detail=f"Invalid task ID format: '{task_id}' is not a valid UUID")
  ```

- P4-02: **Replace `uuid.UUID(task_id)` with `parse_task_uuid(task_id)`** at all 9+ locations:
  - Line 3887 (submit_task_result)
  - Line 3926 (within submit_task_result completed branch)
  - Line 3960 (within submit_task_result failed branch)
  - Line 4018 (claim_task)
  - Line 4038 (within claim_task)
  - Line 4053 (within claim_task)
  - Line 4075 (within claim_task)
  - Line 4237 (renew_task_lease)
  - Line 4319 (retry_task)
  - Line 4375 (send_task_message)
  - Line 4400 (within send_task_message)
  - Additional locations from grep for `uuid.UUID(task_id)`
  - **Checkpoint:** `grep -n "uuid\.UUID(task_id)" main.py` returns 0 matches

- P4-03: **Rebuild and restart backend**

### Rollback Plan
1. `git checkout -- apps/backend/src/api/orchestration/main.py`
2. Rebuild backend
3. Old behavior (500 on invalid UUID) returns

### Gate P4
```bash
# Rebuild backend
cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend
sleep 5

# Test: non-UUID returns 400, not 500
curl -s -X POST http://localhost:8091/api/tasks/not-a-uuid/result \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"status":"completed","result":{}}' -w '\n%{http_code}'
# Must show 400, not 500

# Test: valid UUID format still works (404 if no task exists — that's correct)
curl -s -X POST http://localhost:8091/api/tasks/00000000-0000-0000-0000-000000000000/result \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"status":"completed","result":{}}' -w '\n%{http_code}'
# Must show 404, not 500

# Verify no UUID.UUID(task_id) patterns remain
grep -rn "uuid\.UUID(task_id)" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | wc -l
# Must be 0

# make validate-local still passes
cd /home/zaks/zakops-agent-api && make validate-local
```

---

## Phase 5 — RAG Service Recovery
**Complexity:** S | **Estimated touch points:** 1 file (docker-compose)

**Purpose:** Restart RAG stack and add Docker healthchecks for self-healing.

### Blast Radius
- **Services affected:** RAG (8052), rag-db
- **Pages affected:** None
- **Downstream consumers:** Bridge (rag_query_local, rag_reindex_deal)

### Tasks

- P5-01: **Add Docker healthchecks to RAG services**
  - File: `/home/zaks/Zaks-llm/docker-compose.yml`
  - Add to `rag-db`:
    ```yaml
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    ```
  - Add `depends_on: rag-db: condition: service_healthy` to `rag-rest-api`

- P5-02: **Restart RAG stack**
  ```bash
  cd /home/zaks/Zaks-llm
  docker compose down rag-db rag-rest-api
  docker compose up -d rag-db
  sleep 15  # Wait for postgres init + healthcheck
  docker compose up -d rag-rest-api
  sleep 5
  ```

- P5-03: **Verify RAG health**
  - `curl -sf http://localhost:8052/rag/stats | python3 -m json.tool`
  - Must show `database_connected: true`

### Decision Tree
- **IF** rag-db healthcheck fails → `docker logs rag-db --tail 30` — check for data corruption or disk space
- **ELSE IF** rag-rest-api starts but returns 503 → restart it again (pool=null race condition)
- **ELSE IF** both services healthy but bridge still shows RAG degraded → restart bridge to clear health cache

### Rollback Plan
1. `git checkout -- /home/zaks/Zaks-llm/docker-compose.yml` (remove healthchecks)
2. `cd /home/zaks/Zaks-llm && docker compose up -d rag-db rag-rest-api`
3. RAG was already degraded — rollback returns to pre-mission state

### Gate P5
```bash
# RAG health
curl -sf http://localhost:8052/rag/stats | python3 -m json.tool
# Must show database_connected: true

# Bridge reflects RAG healthy
curl -sf http://127.0.0.1:9100/health | python3 -c "import sys,json; d=json.load(sys.stdin); print('rag_api:', d['checks']['rag_api'])"
# Must print: rag_api: healthy
```

---

## Phase 6 — Full Validation + Bookkeeping
**Complexity:** S | **Estimated touch points:** 2 files

**Purpose:** Verify all 24 tools, run validation, update CHANGES.md.

### Tasks

- P6-01: **Verify all 24 tools** — Run quick health checks on every tool category:
  ```bash
  # Backend reads (should all return 200)
  curl -sf http://localhost:8091/api/deals -o /dev/null -w "deals: %{http_code}\n"
  curl -sf http://localhost:8091/api/actions -o /dev/null -w "actions: %{http_code}\n"
  curl -sf http://localhost:8091/api/quarantine -o /dev/null -w "quarantine: %{http_code}\n"
  curl -sf http://localhost:8091/api/quarantine/brokers -o /dev/null -w "brokers: %{http_code}\n"
  curl -sf http://localhost:8091/api/quarantine/feedback -o /dev/null -w "feedback: %{http_code}\n"
  curl -sf http://localhost:8091/api/quarantine/audit -o /dev/null -w "audit: %{http_code}\n"
  curl -sf http://localhost:8091/api/quarantine/sender-intelligence -o /dev/null -w "sender-intel: %{http_code}\n"
  curl -sf http://localhost:8091/api/delegation/tasks -o /dev/null -w "delegation: %{http_code}\n"
  curl -sf http://localhost:8091/api/delegation/types -o /dev/null -w "del-types: %{http_code}\n"

  # New endpoints (POST with auth)
  curl -sf -X POST http://localhost:8091/api/triage/runs -H "Content-Type: application/json" -H "X-API-Key: $ZAKOPS_API_KEY" -d '{"run_id":"p6_verify","emails_processed":0}' -o /dev/null -w "triage-runs-post: %{http_code}\n"
  curl -sf http://localhost:8091/api/triage/runs -o /dev/null -w "triage-runs-get: %{http_code}\n"
  curl -sf -X POST http://localhost:8091/api/actions -H "Content-Type: application/json" -H "X-API-Key: $ZAKOPS_API_KEY" -d '{"action_type":"FOLLOW_UP","title":"P6 verify"}' -o /dev/null -w "actions-post: %{http_code}\n"

  # RAG
  curl -sf http://localhost:8052/rag/stats -o /dev/null -w "rag-stats: %{http_code}\n"

  # Bridge health
  curl -sf http://127.0.0.1:9100/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"bridge: {d['status']}, tools: {d.get('tools_count', 'N/A')}\")"
  ```

- P6-02: **Run `make validate-local`** — Must PASS

- P6-03: **Run contract surface gates:**
  ```bash
  make validate-surface15  # MCP Bridge
  make validate-surface16  # Email Triage
  ```

- P6-04: **Update OpenAPI spec** (backend API changed):
  ```bash
  make update-spec && make sync-types && npx tsc --noEmit
  ```

- P6-05: **Update CHANGES.md** with full mission summary

- P6-06: **Commit per-phase**:
  - P1 commit: `TRIAGE-BRIDGE-ALIGN-001 P1: Add triage runs and action creation endpoints`
  - P2 commit: `TRIAGE-BRIDGE-ALIGN-001 P2: Enable delegate_actions feature flag`
  - P3 commit: `TRIAGE-BRIDGE-ALIGN-001 P3: Fix bridge tool routing and add startup validation`
  - P4 commit: `TRIAGE-BRIDGE-ALIGN-001 P4: Add UUID input validation to all task endpoints`
  - P5 commit: `TRIAGE-BRIDGE-ALIGN-001 P5: Add RAG healthchecks and restart`
  - Final commit: `TRIAGE-BRIDGE-ALIGN-001: Complete — 24/24 tools working, 62% → 100%`

### Gate P6
- All 24 tools return 200 or valid response
- `make validate-local` PASS
- `make validate-surface15` PASS
- `make validate-surface16` PASS
- TypeScript compiles: `npx tsc --noEmit` PASS
- CHANGES.md updated
- Bridge health: "healthy" (not "degraded")

---

## Acceptance Criteria

| AC | Description | Phase |
|----|-------------|-------|
| AC-1 | `POST /api/triage/runs` stores cron run report, returns event_id. Duplicate run_id returns existing event_id (idempotent) | P1 |
| AC-2 | `GET /api/triage/runs` lists recent runs with pagination and 24h stats summary | P1 |
| AC-3 | `POST /api/actions` creates action in `zakops.actions` table. Response shape matches bridge expectations: `{"action": {"action_id": "act-...", "status": "..."}}`. Returns 201 | P1 |
| AC-4 | `zakops_report_task_result` with cron-style task_id → routed to triage runs, returns success | P3 |
| AC-5 | `zakops_report_task_result` with UUID task_id → unchanged behavior (delegated task result) | P3 |
| AC-6 | `zakops_create_action` via bridge → success (no 405). Response includes action_id | P1+P3 |
| AC-7 | `zakops_approve_quarantine` via bridge calls correct `POST /api/quarantine/{id}/process` with `action: "approve"` payload | P3 |
| AC-8 | `delegate_actions` flag enabled. `POST /api/delegation/tasks` returns non-503. LeaseReaper running | P2 |
| AC-9 | RAG service healthy. `curl http://localhost:8052/rag/stats` returns 200 with `database_connected: true` | P5 |
| AC-10 | Bridge health shows ALL checks "healthy" (not "degraded"). Shows `backend_auth: configured` | P3+P5 |
| AC-11 | Non-UUID task IDs to `/api/tasks/{id}/result` return HTTP 400 (not 500) | P4 |
| AC-12 | `make validate-local` PASS. TypeScript compiles. Surface 15/16 gates PASS. No regressions | P6 |
| AC-13 | Correlation IDs propagated on new endpoints (triage runs, action creation, quarantine approval) | P3 |
| AC-14 | Rate limiting active: 120/min on triage runs, 60/min on action creation | P1 |
| AC-15 | CHANGES.md updated. All changes committed with per-phase commit messages | P6 |

---

## Guardrails

1. **Scope fence:** Do NOT refactor existing working tools. Only fix the 9 broken tools + 3 new endpoints. Do NOT build dashboard pages.
2. **No new database tables or migrations** (exception: partial index on existing `deal_events` table). Reuse `deal_events` (triage runs) and `actions` (proposals).
3. **No changes to existing endpoint behavior** — only additions and routing fixes. All existing UUID-based paths must work identically.
4. **API key auth on all new write endpoints** (same middleware as quarantine injection).
5. **Route ordering rule** — static POST routes BEFORE parameterized GET `{id}` routes per backend CLAUDE.md.
6. **Bridge backward-compatible** — UUID task_ids MUST still route to existing delegation endpoint.
7. **Feature flag change is database-only** — no code changes, takes effect within 1s TTL.
8. **RAG is optional enrichment** — triage pipeline must function with RAG down.
9. **Port 8090 FORBIDDEN.**
10. **Generated files NEVER edited directly** — after backend changes, run `make update-spec → make sync-types`.
11. **WSL safety** — `sed -i 's/\r$//'` on any new/modified .sh files, `chown zaks:zaks` on files under `/home/zaks/`.
12. **Progressive rollout** — after this mission: `delegate_actions=true`, `shadow_mode=true` (Stage 2). Do NOT disable shadow_mode.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I confirm ALL 9 failure states match the audit?"
- [ ] "Did I identify all affected contract surfaces (3, 15, 16)?"

### After every code change:
- [ ] "Does the response shape match what the bridge client expects?" (Check bridge lines 1097-1103 for actions, lines 1433-1438 for task results)
- [ ] "Did I add the `X-API-Key` header to new write endpoints?"
- [ ] "Did I add rate limiting to new write endpoints?"
- [ ] "Did I include correlation ID propagation?"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks?"
- [ ] "Did I fix CRLF on any new files? (`sed -i 's/\r$//'`)"
- [ ] "Did I fix ownership? (`chown zaks:zaks`)"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass RIGHT NOW?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I run `make update-spec → make sync-types → npx tsc --noEmit`?"
- [ ] "Do all 24 tools return success or valid response?"
- [ ] "Does bridge health show 'healthy' (not 'degraded')?"

---

## Files Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` | P1, P4 | Add POST/GET /api/triage/runs, POST /api/actions, parse_task_uuid() helper |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` | P3 | Fix report_task_result routing, fix approve_quarantine path, startup validation, error detail |
| `/home/zaks/Zaks-llm/docker-compose.yml` | P5 | Add healthchecks to rag-db and rag-rest-api |
| `/home/zaks/bookkeeping/CHANGES.md` | P6 | Record all changes |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/apps/backend/db/migrations/XXX_triage_run_index.sql` | P1 | Partial index for triage run queries |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/apps/backend/db/init/001_base_tables.sql` | Actions and deal_events table schema |
| `/home/zaks/zakops-agent-api/apps/backend/db/migrations/032_feature_flags.sql` | Feature flag definitions |
| `/home/zaks/zakops-agent-api/apps/backend/db/migrations/035_delegated_tasks.sql` | Delegated tasks schema |
| `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/delegation_types.py` | Valid task types and lease durations |
| `/home/zaks/zakops-agent-api/apps/backend/src/api/shared/middleware/apikey.py` | API key auth pattern |
| `/home/zaks/zakops-agent-api/apps/backend/src/api/shared/middleware/idempotency.py` | Idempotency middleware pattern |
| `/home/zaks/zakops-agent-api/apps/backend/src/api/shared/security.py` | Rate limiter pattern |

---

## Crash Recovery Protocol

If resuming after a crash:
1. `git log --oneline -10` — check which phases are committed
2. `make validate-local` — check current state
3. `curl -sf http://127.0.0.1:9100/health | python3 -m json.tool` — check bridge state
4. `psql -U zakops -d zakops -c "SELECT name, enabled FROM zakops.feature_flags;"` — check flag state
5. Resume from the last uncommitted phase

---

## Completion Report Template

```
## Completion Report — TRIAGE-BRIDGE-ALIGN-001

**Date:** 2026-02-23
**Executor:** Claude Code (opus)
**Status:** COMPLETE / PARTIAL

### Phases Completed
| Phase | Name | Gate | Status |
|-------|------|------|--------|
| P0 | Discovery & Baseline | Gate P0 | PASS |
| P1 | Backend Endpoints | Gate P1 | PASS |
| P2 | Feature Flags | Gate P2 | PASS |
| P3 | Bridge Fixes | Gate P3 | PASS |
| P4 | Backend Hardening | Gate P4 | PASS |
| P5 | RAG Recovery | Gate P5 | PASS |
| P6 | Full Validation | Gate P6 | PASS |

### Acceptance Criteria
| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-1 | Triage run storage + dedup | PASS | curl output |
| ... | ... | ... | ... |

### Validation Results
- `make validate-local`: PASS
- TypeScript compilation: PASS
- Surface 15: PASS
- Surface 16: PASS

### Files Modified
...

### Files Created
...
```

---

## Stop Condition

DONE when:
- All 15 AC pass
- All 24 MCP tools verified working (bridge health: "healthy")
- `make validate-local` PASS
- `make validate-surface15` and `make validate-surface16` PASS
- `npx tsc --noEmit` PASS
- CHANGES.md updated
- All changes committed with per-phase messages
- Completion report produced

Do NOT proceed to: shadow_mode disablement (Stage 3), dashboard triage run page, refactoring of the other 22 tools, or any additional feature flags.

---

# STOP-THE-LINE ISSUES

Issues that MUST be resolved before coding:

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 1 | **`deal_events.deal_id` FK allows NULL but `ON DELETE CASCADE` won't clean up orphans** — triage run events with `deal_id=NULL` persist forever | LOW | Acceptable for now. Add 90-day retention note in RUNBOOKS.md. Not a blocker. |
| 2 | **Bridge field `requires_human_review` vs DB column `requires_approval`** — name mismatch must be explicitly mapped in the new endpoint | HIGH | Map in P1-05. The Pydantic model must accept `requires_human_review` and store as `requires_approval`. |
| 3 | **Bridge expects `{"action": {"action_id": ..., "status": ...}}` response shape** — endpoint MUST return this exact nesting, not a flat dict | HIGH | Verified from bridge code lines 1099-1100. Endpoint response must wrap in `"action"` key. |
| 4 | **`approve_quarantine` parameter rename: `action_id` → `item_id`** — changing tool parameter names may break LangSmith agent prompts | MEDIUM | Keep parameter name as `action_id` in the MCP tool signature for backward compatibility. Only change the internal variable name and endpoint URL. |
| 5 | **Partial index creation on large `deal_events` table** — `CREATE INDEX CONCURRENTLY` is non-blocking but requires outside a transaction | MEDIUM | Use `CONCURRENTLY` and run as standalone psql command, not inside a migration transaction. |
| 6 | **RAG `rag-db` is on an external Docker network** (`crawl4ai-rag_backend`) — healthcheck and depends_on only work within the same compose file | MEDIUM | If rag-db is in a different compose stack, the healthcheck approach may need adjustment. Verify with `docker compose -f /home/zaks/Zaks-llm/docker-compose.yml config` that rag-db is defined in the same file. If external, use a startup script instead. |

---

*End of Mission Prompt — TRIAGE-BRIDGE-ALIGN-001 (10x Master Plan)*
