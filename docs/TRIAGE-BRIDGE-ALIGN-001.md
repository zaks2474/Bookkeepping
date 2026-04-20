# MISSION: TRIAGE-BRIDGE-ALIGN-001
## Full Alignment of MCP Bridge + Backend for LangSmith Email Triage Agent
## Date: 2026-02-23
## Classification: Feature Gap + Bug Fix (Backend + Bridge, L)
## Prerequisite: CHAT-CONTROL-SURFACE-001, SYSTEM-MATURITY-REMEDIATION-001
## Successor: None (enables full hourly cron triage)

---

## Context

The LangSmith email triage agent runs hourly. It can read/classify/label Gmail and inject deal signals into quarantine. But 100% of the agent's designed capabilities are NOT available because:

1. **3 backend endpoints are missing** (POST /api/actions, POST /api/triage/runs, correct quarantine approve path)
2. **1 feature flag is disabled** (`delegate_actions=false` blocks all delegation tools)
3. **1 service is down** (RAG database connection broken → rag_query_local and rag_reindex_deal fail)
4. **2 bridge tools have wrong endpoint paths** (approve_quarantine, report_task_result for cron IDs)

This mission fixes ALL gaps so the agent operates at 100% of designed capability.

---

## Complete Tool Audit (24 tools)

| # | Tool | Backend Endpoint | Status | Fix Phase |
|---|------|-----------------|--------|-----------|
| 1 | zakops_list_deals | GET /api/deals | ✅ Working | — |
| 2 | zakops_get_deal | GET /api/deals/{id} | ✅ Working | — |
| 3 | zakops_update_deal_profile | Filesystem | ✅ Working | — |
| 4 | zakops_write_deal_artifact | Filesystem | ✅ Working | — |
| 5 | zakops_list_deal_artifacts | Filesystem | ✅ Working | — |
| 6 | zakops_list_quarantine | GET /api/quarantine | ✅ Working | — |
| 7 | **zakops_create_action** | POST /api/actions | ❌ 405 (endpoint missing) | P1 |
| 8 | zakops_get_action | GET /api/actions/{id} | ✅ Working | — |
| 9 | zakops_list_actions | GET /api/actions | ✅ Working | — |
| 10 | **zakops_approve_quarantine** | POST /api/actions/quarantine/{id}/approve | ❌ Wrong path | P3 |
| 11 | zakops_get_deal_status | GET /api/deals/{id} | ✅ Working | — |
| 12 | zakops_list_recent_events | GET /api/deals/{id}/events | ✅ Working | — |
| 13 | **zakops_report_task_result** | POST /api/tasks/{id}/result | ❌ 500 for cron IDs | P3 |
| 14 | zakops_claim_action | POST /api/tasks/{id}/claim | ⚠️ 503 (flag off) | P2 |
| 15 | zakops_renew_action_lease | POST /api/tasks/{id}/renew-lease | ⚠️ 503 (flag off) | P2 |
| 16 | zakops_get_task_messages | GET /api/delegation/tasks | ✅ Working | — |
| 17 | zakops_inject_quarantine | POST /api/quarantine | ✅ Working | — |
| 18 | **rag_query_local** | POST RAG:8052/rag/query | ❌ 503 (DB down) | P4 |
| 19 | **rag_reindex_deal** | POST RAG:8052/rag/index | ❌ 503 (DB down) | P4 |
| 20 | zakops_get_triage_feedback | GET /api/quarantine/feedback | ✅ Working | — |
| 21 | zakops_list_brokers | GET /api/quarantine/brokers | ✅ Working | — |
| 22 | zakops_get_classification_audit | GET /api/quarantine/audit | ✅ Working | — |
| 23 | zakops_get_sender_intelligence | GET /api/quarantine/sender-intelligence | ✅ Working | — |
| 24 | zakops_get_manifest | Self-contained | ✅ Working | — |

**Current: 15/24 working (62%). Target: 24/24 (100%).**

---

## Phases

### Phase 0 — Baseline Verification
**Complexity:** S

- `make validate-local` PASS
- Backend healthy (8091)
- Bridge healthy (9100)
- Confirm current tool failure states match audit

**Gate:** Baseline clean

---

### Phase 1 — Backend: Add Missing Endpoints
**Complexity:** M | **Files:** `apps/backend/src/api/orchestration/main.py`

**Blast Radius:** Backend API only. No dashboard/agent changes.

#### P1-01: Add `POST /api/triage/runs` — Store Cron Run Reports

Pydantic model `TriageRunReport`:
```python
class TriageRunReport(BaseModel):
    run_id: str                          # cron_2026-02-22T23:58:31-0600 or any string
    status: str = "completed"            # completed | failed
    correlation_id: str | None = None
    emails_processed: int = 0
    classifications: dict = {}           # {"NEWSLETTER": 2, "DEAL_SIGNAL": 1}
    injections: dict = {}                # {"attempted": 3, "succeeded": 2, "failed": 1}
    labels_applied: int = 0
    errors: list[str] = []
    duration_ms: int | None = None
    langsmith_run_id: str | None = None
    langsmith_trace_url: str | None = None
    agent_config: dict | None = None
    summary: str | None = None
```

Endpoint behavior:
- API key auth (X-API-Key required, same pattern as quarantine POST)
- Store in `deal_events` table: `event_type='triage_run.completed'` or `'triage_run.failed'`, `event_source='langsmith_bridge'`, `payload=full report JSONB`, `deal_id=NULL`, `actor='langsmith_agent'`
- Return: `{"event_id": str, "run_id": str, "status": "stored"}`
- Route placement: BEFORE any `{id}` routes in the triage section

#### P1-02: Add `GET /api/triage/runs` — List Recent Runs

- Query `deal_events WHERE event_type LIKE 'triage_run.%' ORDER BY created_at DESC`
- Pagination: `limit` (default 20), `offset` (default 0)
- Return: `[{event_id, run_id, status, emails_processed, created_at, ...}]`

#### P1-03: Add `POST /api/actions` — Create Action Proposals

Pydantic model `ActionCreate`:
```python
class ActionCreate(BaseModel):
    action_type: str                     # REQUEST_DOCS, DRAFT_REPLY, INGEST_MATERIALS, FOLLOW_UP, CREATE_DEAL_REVIEW, OPS.ERROR_RECOVERY
    title: str
    description: str | None = None
    deal_id: str | None = None
    inputs: dict = {}
    source: str = "langsmith_bridge"
    created_by: str = "langsmith_agent"
    requires_approval: bool = True
```

Endpoint behavior:
- API key auth (X-API-Key required)
- Generate `action_id = f"act-{uuid.uuid4().hex[:12]}"`
- If `deal_id` provided, validate it exists (HTTP 404 if not)
- Insert into `zakops.actions` table:
  - `action_id`, `deal_id`, `action_type`, `title`, `description`
  - `status='pending_approval'` if requires_approval else `'queued'`
  - `agent_type=source`, `agent_config=json(inputs)`
  - `requires_approval=requires_approval`
- If `deal_id` provided, record deal_event: `event_type='action_created'`
- Return: `{"action_id": str, "status": str, "requires_approval": bool}` with HTTP 201

**Route ordering:** `POST /api/actions` MUST come BEFORE `GET /api/actions/{action_id}` per backend CLAUDE.md rule.

**Patterns to reuse:**
- API key auth: same pattern as `create_quarantine_item()` (main.py:2225)
- deal_events insert: `record_deal_event()` PL/pgSQL function (001_base_tables.sql:125)
- Action ID format: `f"act-{uuid.uuid4().hex[:12]}"` matching existing action_id patterns
- Deal validation: same as `create_delegation_task()` (main.py:4172)

**Gate P1:**
```bash
cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend
sleep 5
# Test triage run report
curl -sf -X POST http://localhost:8091/api/triage/runs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $KEY" \
  -d '{"run_id":"test_run","emails_processed":2,"classifications":{"NEWSLETTER":2}}' | python3 -m json.tool
# Test list triage runs
curl -sf http://localhost:8091/api/triage/runs | python3 -m json.tool
# Test create action
curl -sf -X POST http://localhost:8091/api/actions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $KEY" \
  -d '{"action_type":"FOLLOW_UP","title":"Test action"}' | python3 -m json.tool
# All three return valid JSON with no 4xx/5xx
```

---

### Phase 2 — Enable Feature Flags
**Complexity:** S | **Files:** None (database only)

**Blast Radius:** Enables delegation tools system-wide. No code changes.

#### P2-01: Enable `delegate_actions` flag

```sql
psql -U zakops -d zakops -c "UPDATE zakops.feature_flags SET enabled=true WHERE name='delegate_actions';"
```

This unblocks:
- `zakops_claim_action` (POST /api/tasks/{id}/claim)
- `zakops_renew_action_lease` (POST /api/tasks/{id}/renew-lease)
- Delegation task creation (POST /api/deals/{id}/tasks)

#### P2-02: Verify shadow_mode status

`shadow_mode=true` means quarantine items are tagged with `source_type='langsmith_shadow'`. This is correct for the current stage — keeps triage outputs visible but marked as shadow. Leave as-is.

**Gate P2:**
```bash
psql -U zakops -d zakops -c "SELECT name, enabled FROM zakops.feature_flags;"
# delegate_actions = true
# email_triage_writes_enabled = true
# shadow_mode = true
```

---

### Phase 3 — Bridge: Fix Tool Routing
**Complexity:** M | **Files:** `apps/agent-api/mcp_bridge/server.py`

**Blast Radius:** Bridge only. Backend unchanged.

#### P3-01: Fix `zakops_report_task_result` (line ~1423)

Add UUID detection branch:
```python
import re
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

# Inside zakops_report_task_result, before the try block:
if not UUID_PATTERN.match(task_id):
    # Cron run — route to triage runs endpoint
    triage_payload = {
        "run_id": task_id,
        "status": status,
        "correlation_id": None,
        "summary": feedback,
        "errors": [error] if error else [],
        "langsmith_run_id": langsmith_run_id,
        "langsmith_trace_url": langsmith_trace_url,
        **(result or {}),
    }
    resp = client.post(f"{DEAL_API_URL}/api/triage/runs", json=triage_payload, headers={"X-API-Key": BACKEND_API_KEY})
    if resp.status_code not in (200, 201):
        return {"error": f"Failed to store triage run: HTTP {resp.status_code}"}
    data = resp.json()
    return {"success": True, "run_id": task_id, "event_id": data.get("event_id"), "message": "Triage run report stored"}
# else: existing UUID path continues unchanged
```

#### P3-02: Fix `zakops_approve_quarantine` (line ~1219)

Change the endpoint URL from:
```python
f"{DEAL_API_URL}/api/actions/quarantine/{action_id}/approve"
```
to:
```python
f"{DEAL_API_URL}/api/quarantine/{action_id}/process"
```

Change the payload from whatever it sends now to:
```python
{
    "action": "approve",
    "deal_id": deal_id,           # optional — auto-creates deal if omitted
    "processed_by": "langsmith_agent",
    "notes": reason or "Approved via LangSmith triage agent",
}
```

Update the response parsing to match the backend's response format:
```python
# Backend returns: {"status": "approved", "item_id": ..., "deal_id": ..., "deal_created": bool}
```

#### P3-03: Restart bridge

```bash
sudo systemctl restart zakops-agent-bridge
```

**Gate P3:**
```bash
# Test report_task_result with cron-style ID
curl -sf -X POST https://zakops-bridge.zaksops.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"zakops_report_task_result","arguments":{"task_id":"cron_test_123","status":"completed","result":{"emails_processed":2}}}}'
# Should not return 500

# Verify bridge health
curl -sf https://zakops-bridge.zaksops.com/health | python3 -m json.tool
```

---

### Phase 4 — Fix RAG Service
**Complexity:** S | **Files:** None (Docker restart)

**Blast Radius:** RAG service only. Affects rag_query_local and rag_reindex_deal.

#### P4-01: Restart RAG stack

```bash
cd /home/zaks/Zaks-llm
docker compose restart rag-db
sleep 10  # Let postgres init
docker compose restart rag-rest-api
sleep 5
```

Per CLAUDE.md note: "RAG REST (:8052) — Needs restart if pool=null at boot"

#### P4-02: Verify RAG health

```bash
curl -sf http://localhost:8052/rag/stats | python3 -m json.tool
# Should return 200 with database_connected: true
```

If RAG-db still fails, check:
- `docker logs rag-db --tail 20` for init errors
- Database credentials in Zaks-llm docker-compose.yml

**Gate P4:**
```bash
curl -sf http://localhost:8052/rag/stats  # 200 OK
curl -sf http://localhost:9100/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['checks']['rag_api'])"
# Should print: "healthy" (not "degraded")
```

---

### Phase 5 — Full Validation + Bookkeeping
**Complexity:** S

#### P5-01: Verify all 24 tools

Run a quick health check on every tool category:
```bash
# Backend reads (should all return 200)
curl -sf http://localhost:8091/api/deals | head -c 100
curl -sf http://localhost:8091/api/actions | head -c 100
curl -sf http://localhost:8091/api/quarantine | head -c 100
curl -sf http://localhost:8091/api/quarantine/brokers | head -c 100

# New endpoints
curl -sf -X POST http://localhost:8091/api/triage/runs -H "Content-Type: application/json" -H "X-API-Key: $KEY" -d '{"run_id":"verify","emails_processed":0}'
curl -sf -X POST http://localhost:8091/api/actions -H "Content-Type: application/json" -H "X-API-Key: $KEY" -d '{"action_type":"FOLLOW_UP","title":"Verify"}'

# RAG
curl -sf http://localhost:8052/rag/stats

# Bridge health
curl -sf https://zakops-bridge.zaksops.com/health
```

#### P5-02: `make validate-local` PASS

#### P5-03: Update CHANGES.md

#### P5-04: Relay final status to LangSmith agent

**Gate P5:** All 24 tools verified, `make validate-local` PASS, CHANGES.md updated.

---

## Acceptance Criteria

| AC | Description |
|----|-------------|
| AC-1 | `POST /api/triage/runs` stores cron run report, returns event_id |
| AC-2 | `GET /api/triage/runs` lists recent runs with pagination |
| AC-3 | `POST /api/actions` creates action in `zakops.actions` table, returns 201 |
| AC-4 | `zakops_report_task_result` with cron-style ID → success (routed to triage runs) |
| AC-5 | `zakops_report_task_result` with UUID → unchanged behavior (delegated tasks) |
| AC-6 | `zakops_create_action` via bridge → success (no 405) |
| AC-7 | `zakops_approve_quarantine` via bridge → calls correct /api/quarantine/{id}/process |
| AC-8 | `delegate_actions` flag enabled — zakops_claim_action and zakops_renew_action_lease return non-503 |
| AC-9 | RAG service healthy — rag_query_local and rag_reindex_deal return non-503 |
| AC-10 | Bridge health shows all checks "healthy" (not "degraded") |
| AC-11 | `make validate-local` PASS, no regressions |
| AC-12 | CHANGES.md updated |

---

## Guardrails

1. **No new database tables or migrations** — reuse `deal_events` (triage runs) and `actions` (action proposals)
2. **No changes to existing endpoint behavior** — only additions and bridge routing fixes
3. **API key auth on all new write endpoints** (same pattern as quarantine injection)
4. **Route ordering rule** — static POST routes before parameterized GET `{id}` routes
5. **Bridge backward-compatible** — UUID task_ids still route to existing delegation endpoint
6. **Feature flag change is database-only** — no code changes, takes effect within 1s TTL
7. **RAG fix is restart-only** — no code changes to RAG service
8. **Port 8090 FORBIDDEN**

---

## Files Reference

| File | Action | Phase |
|------|--------|-------|
| `apps/backend/src/api/orchestration/main.py` | MODIFY — add POST/GET /api/triage/runs, POST /api/actions | P1 |
| `apps/agent-api/mcp_bridge/server.py` | MODIFY — fix report_task_result routing, fix approve_quarantine path | P3 |

**Patterns to reuse (read-only):**
| Pattern | Source |
|---------|--------|
| API key auth + rate limit | `create_quarantine_item()` at main.py:2225 |
| deal_events insert | `record_deal_event()` PL/pgSQL at 001_base_tables.sql:125 |
| Deal validation | `create_delegation_task()` at main.py:4172 |
| Action table schema | `001_base_tables.sql:64` |

---

## Verification (End-to-End)

After all phases complete:
```bash
# 1. Triage run report (was: 500)
curl -X POST localhost:8091/api/triage/runs -H "Content-Type: application/json" \
  -H "X-API-Key: $KEY" -d '{"run_id":"cron_verify","emails_processed":2,"classifications":{"NEWSLETTER":2}}'
# → 200 with event_id ✓

# 2. Create action (was: 405)
curl -X POST localhost:8091/api/actions -H "Content-Type: application/json" \
  -H "X-API-Key: $KEY" -d '{"action_type":"FOLLOW_UP","title":"Follow up on broker call"}'
# → 201 with action_id ✓

# 3. Delegation tools (was: 503)
psql -U zakops -d zakops -c "SELECT enabled FROM zakops.feature_flags WHERE name='delegate_actions';"
# → true ✓

# 4. RAG (was: 503)
curl -sf http://localhost:8052/rag/stats
# → 200 with database_connected: true ✓

# 5. Bridge health (was: degraded)
curl -sf https://zakops-bridge.zaksops.com/health | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])"
# → "healthy" ✓

# 6. Trigger LangSmith cron run → agent reports success on all tools
# 7. make validate-local → PASS ✓
```

---

## Stop Condition

DONE when all 12 AC pass, all 24 MCP tools verified working, bridge health is "healthy" (not "degraded"), and CHANGES.md is updated. The next LangSmith cron trigger should complete with zero tool failures.
