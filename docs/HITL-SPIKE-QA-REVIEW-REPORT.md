# ZakOps HITL Spike — QA/Review Report

> Scope: **transition_deal HITL spike only** (interrupt/resume, approval persistence, claim-first idempotency, kill -9 recovery, concurrent approvals).  
> Repo under test: `/home/zaks/zakops-agent-api`  
> Gate runner: `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh`  
>
> Note: `/mnt/data/ZakOps-Scaffold-Master-Plan-v2.md` and `/mnt/data/DECISION-LOCK-FILE.md` are **not readable** in this environment; validation below is against the constraints in your prompt + current implementation.

---

## Section 1: Spike DoD checklist (copy/paste)

**How to run the full gate pack**
- [ ] Run `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
  - Pass: exit code `0` and script prints `ALL GATES PASSED - HITL Spike verified!`
  - Fail: exit code `1` and script prints `GATE VERIFICATION FAILED`

**Gate Artifacts Pack (required before Phase 1)**
- [ ] `gate_artifacts/checkpoint_kill9_test.log` exists and contains `RESULT: PASSED`
- [ ] `gate_artifacts/auth_negative_tests.json` exists, `.status=="completed"`, and **all tests** `.passed==true`
- [ ] `gate_artifacts/tool_call_validation_test.log` exists and JSON `.status=="PASSED"`
- [ ] `gate_artifacts/streaming_test.log` exists and contains `STATUS=PASSED`
- [ ] `gate_artifacts/dependency_licenses.json` exists and `.package_count > 0`
- [ ] `gate_artifacts/copyleft_findings.json` is **missing** or **empty** (denylist scan: GPL/AGPL/LGPL)
- [ ] `gate_artifacts/health.json`, `invoke_hitl.json`, `approve.json`, `approve_again.json`, `db_invariants.sql.out`, `concurrent_approves.log`, `mock_safety_test.log`, `hitl_scope_test.log`, `build.log`, `run.log` exist (see `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh` header)

**HITL scope correctness**
- [ ] Only `transition_deal` requires approval
  - Verify: `gate_artifacts/hitl_scope_test.log` JSON `.status=="PASSED"`
  - Verify source: `/home/zaks/zakops-agent-api/app/schemas/agent.py` `HITL_TOOLS == {"transition_deal"}`

**Interrupt/resume semantics**
- [ ] Graph interrupts at approval gate
  - Verify source: `/home/zaks/zakops-agent-api/app/core/langgraph/graph.py` compiled with `interrupt_before=["approval_gate"]`
- [ ] Approval is resumable via API
  - Verify: `POST /api/v1/agent/approvals/{id}:approve` returns `{"status":"approved", ...}` (see `gate_artifacts/approve.json`)

**Approval row persisted BEFORE interrupt response**
- [ ] Invoke returns `pending_approval` AND the referenced approval row exists in DB
  - Verify: `gate_artifacts/invoke_hitl.json` has `.status=="pending_approval"` and `.pending_approval.tool_name=="transition_deal"`
  - Verify: `gate_artifacts/db_invariants.sql.out` shows `SELECT ... FROM approvals WHERE id='<approval_id>'` returns 1 row with `status='pending'`

**Claim-first idempotency + concurrency**
- [ ] Approvals claim is atomic (exactly one winner)
  - Verify: `gate_artifacts/concurrent_approves.log` shows exactly one `200` and contains `RESULT: PASSED`
- [ ] Tool executions are unique by `idempotency_key`
  - Verify: `gate_artifacts/db_invariants.sql.out` has **0 rows** for `GROUP BY idempotency_key HAVING COUNT(*) > 1`
- [ ] Exactly one tool execution for the concurrent approval
  - Verify: `gate_artifacts/db_invariants.sql.out` contains `SELECT COUNT(*) ... WHERE approval_id='<conc_approval_id>'` → expected `1`

**Kill -9 recovery**
- [ ] After `SIGKILL` of `zakops-agent-api`, the pending approval can be fetched and approved
  - Verify: `gate_artifacts/checkpoint_kill9_test.log` contains recovered approval JSON + `RESULT: PASSED`
  - Optional DB proof: `checkpoints` row count increases (see DB assertions below)

**Tool arg strictness**
- [ ] Extra args to `transition_deal` are rejected (`extra="forbid"`)
  - Verify: `gate_artifacts/tool_call_validation_test.log` JSON `.status=="PASSED"` and includes `extra_args_rejected.passed==true`
  - Verify source: `/home/zaks/zakops-agent-api/app/core/langgraph/tools/deal_tools.py` `TransitionDealInput.model_config = ConfigDict(extra="forbid")`

**JWT auth negative tests (approve/reject only)**
- [ ] With `AGENT_JWT_ENFORCE=true`, approve requires JWT and enforces iss/aud/role
  - Verify: `gate_artifacts/auth_negative_tests.json` includes:
    - `no_token` → `401`
    - `expired_token` → `401`
    - `wrong_issuer` → `401`
    - `wrong_audience` → `401`
    - `missing_role` → `403`

**Decision-lock retrieval compliance (no direct pgvector/mem0 from Agent API)**
- [ ] Long-term memory is disabled for the spike
  - Verify source: `/home/zaks/zakops-agent-api/app/core/langgraph/graph.py` `DISABLE_LONG_TERM_MEMORY` defaults to `"true"`
  - Verify quickly: `docker exec zakops-agent-api python -c "from app.core.langgraph.graph import DISABLE_LONG_TERM_MEMORY; print(DISABLE_LONG_TERM_MEMORY)"` → `True`

---

## Section 2: Test matrix table

| Test | Name | Endpoint / Entrypoint | Preconditions | Steps | Assertions (pass criteria) | Expected artifact/log |
|---:|---|---|---|---|---|---|
| T0 | Build + start | `docker compose build agent-api` + `docker compose up -d db agent-api` | Docker running | Run script | Containers start; `/health` reachable | `gate_artifacts/build.log`, `gate_artifacts/run.log` |
| T0 | Health check | `GET http://localhost:8095/health` | Agent API running | `curl /health` | JSON `.status=="healthy" OR "degraded"` | `gate_artifacts/health.json` |
| T1 | HITL invoke | `POST /api/v1/agent/invoke` | LLM configured; tool binding enabled | Send “Transition deal …” message | Response `.status=="pending_approval"` and `.pending_approval.tool_name=="transition_deal"` | `gate_artifacts/invoke_hitl.json` |
| T2 | DB invariants (persisted pre-interrupt) | DB (`zakops_agent`) | DB reachable (host `localhost:5433`) | Query approvals + checkpoint tables | Approval row exists for `approval_id`; checkpoint tables exist | `gate_artifacts/db_invariants.sql.out` |
| T3 | Approve happy path | `POST /api/v1/agent/approvals/{id}:approve` | Pending approval exists | Approve as `approver-1` | HTTP `200` and JSON `.status=="approved"` | `gate_artifacts/approve.json` (+ audit rows appended to `db_invariants.sql.out`) |
| T4 | Double-approve rejection | same as T3 | Approval already resolved | Approve again | HTTP `409` (or `400`) | `gate_artifacts/approve_again.json` |
| T6 | Kill -9 recovery | `docker kill -s KILL zakops-agent-api` + restart | Pending approval exists | Create approval → kill container → restart → `GET /approvals/{id}` → approve | `GET` returns approval; log contains `RESULT: PASSED` | `gate_artifacts/checkpoint_kill9_test.log` |
| T5 | Concurrent approvals (exactly one winner) | 20x `POST /approvals/{id}:approve` in parallel | Fresh pending approval exists | Fire 20 parallel approves | Exactly one `200`; others `409`/`400`; DB execution count for approval is `1` | `gate_artifacts/concurrent_approves.log` + `db_invariants.sql.out` |
| T8 | Tool arg validation | `docker exec zakops-agent-api python -c ...` | Container running | Construct `TransitionDealInput` with valid/missing/extra fields | JSON `.status=="PASSED"` and extra args rejected | `gate_artifacts/tool_call_validation_test.log` |
| T9 | Dependency license report | `docker exec ... python -c importlib.metadata` | Container running | Generate JSON report | `.package_count > 0` | `gate_artifacts/dependency_licenses.json` |
| T9b | Copyleft denylist scan | `jq` on `dependency_licenses.json` | License report exists | Scan for `agpl|gpl|lgpl` strings | **No** `gate_artifacts/copyleft_findings.json` or file empty | `gate_artifacts/copyleft_findings.json` (only if found) |
| T10 | Audit log verification | DB queries | Approvals exercised | Query `audit_log` counts + recent events | Audit rows exist (at least claim + exec start/complete + approve) | Appends to `gate_artifacts/db_invariants.sql.out` |
| T11 | Mock safety | `docker exec ... python -c os.getenv(...)` | Container running | Read `APP_ENV`, `ALLOW_TOOL_MOCKS` | In production: mocks must be disabled; otherwise warn | `gate_artifacts/mock_safety_test.log` |
| T12 | Streaming test | `POST /api/v1/auth/register` → `/auth/session` → `POST /api/v1/chatbot/chat/stream` | Auth endpoints + session DB working | Register throwaway user; stream request | Streaming output contains `"done":true`; log contains `STATUS=PASSED` | `gate_artifacts/streaming_test.log` |
| T13 | HITL scope test | `docker exec ... python -c from app.schemas.agent import HITL_TOOLS` | Container running | Assert set membership + exact set | JSON `.status=="PASSED"` | `gate_artifacts/hitl_scope_test.log` |
| T14 | Auth negative tests | restart agent with `AGENT_JWT_ENFORCE=true` | Able to create pending approval | Generate tokens → approve with each token | 401/403 codes match expected; JSON `.status=="completed"` | `gate_artifacts/auth_negative_tests.json` |

---

## Section 3: Curl cookbook

**Base URLs**
- Agent API: `http://localhost:8095`
- Agent v1 prefix: `http://localhost:8095/api/v1`

### Health
```bash
curl -s http://localhost:8095/health | jq .
```

### Invoke HITL (expects `pending_approval`)
```bash
curl -s -X POST http://localhost:8095/api/v1/agent/invoke \
  -H 'Content-Type: application/json' \
  -d '{
    "actor_id":"qa",
    "message":"Transition deal DEAL-001 from qualification to proposal because budget approved",
    "metadata":{"test":"hitl"}
  }' | jq .
```

Extract approval id:
```bash
APPROVAL_ID="$(curl -s -X POST http://localhost:8095/api/v1/agent/invoke \
  -H 'Content-Type: application/json' \
  -d '{"actor_id":"qa","message":"Transition deal DEAL-001 from lead to qualification"}' \
 | jq -r '.pending_approval.approval_id')"
echo "$APPROVAL_ID"
```

### List/get approvals
```bash
curl -s http://localhost:8095/api/v1/agent/approvals | jq .
curl -s http://localhost:8095/api/v1/agent/approvals/$APPROVAL_ID | jq .
```

### Approve / reject (no JWT enforcement)
```bash
curl -s -X POST http://localhost:8095/api/v1/agent/approvals/$APPROVAL_ID:approve \
  -H 'Content-Type: application/json' \
  -d '{"actor_id":"approver-1","reason":"approved"}' | jq .

curl -s -X POST http://localhost:8095/api/v1/agent/approvals/$APPROVAL_ID:reject \
  -H 'Content-Type: application/json' \
  -d '{"actor_id":"approver-1","reason":"rejecting for test"}' | jq .
```

### Approve with JWT enforcement (Bearer token)
Generate a token inside the container:
```bash
TOKEN="$(docker exec zakops-agent-api python -c \
  "from app.core.security.agent_auth import create_agent_token; print(create_agent_token('approver-1'))")"
```

Approve (when `AGENT_JWT_ENFORCE=true` in the running agent container):
```bash
curl -s -X POST http://localhost:8095/api/v1/agent/approvals/$APPROVAL_ID:approve \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"actor_id":"approver-1","reason":"approved with jwt"}' | jq .
```

### Auth negative tests (manual spot checks)
```bash
# No token → expect 401
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  http://localhost:8095/api/v1/agent/approvals/$APPROVAL_ID:approve \
  -H 'Content-Type: application/json' -d '{"actor_id":"no-token"}'

# Generate “expired/wrong_iss/wrong_aud/no_role” tokens
docker exec zakops-agent-api python -c \
  "from app.core.security.agent_auth import generate_test_tokens; import json; print(json.dumps(generate_test_tokens(), indent=2))"
```

### Streaming (SSE) smoke test
Register:
```bash
USER_JSON="$(curl -s -X POST http://localhost:8095/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"qa-stream@example.com","password":"Str0ng!Passw0rd"}')"
USER_TOKEN="$(echo "$USER_JSON" | jq -r '.token.access_token // .access_token')"
```

Create session:
```bash
SESSION_JSON="$(curl -s -X POST http://localhost:8095/api/v1/auth/session \
  -H "Authorization: Bearer $USER_TOKEN")"
SESSION_TOKEN="$(echo "$SESSION_JSON" | jq -r '.token.access_token // .access_token // empty')"
[ -z "$SESSION_TOKEN" ] && SESSION_TOKEN="$USER_TOKEN"
```

Stream:
```bash
curl -N -X POST http://localhost:8095/api/v1/chatbot/chat/stream \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -d '{"messages":[{"role":"user","content":"stream test"}]}'
# Pass: SSE includes a final event with {"done":true}
```

---

## Section 4: DB assertions (SQL)

Connection (default compose):
```bash
export PGPASSWORD='agent_secure_pass_123'
psql -h localhost -p 5433 -U agent -d zakops_agent
```

### 1) Exactly one execution per idempotency key
```sql
SELECT idempotency_key, COUNT(*) AS cnt
FROM tool_executions
GROUP BY idempotency_key
HAVING COUNT(*) > 1;
-- Expected: 0 rows
```

### 2) Approval lifecycle correctness for a specific approval
```sql
-- replace :approval_id
SELECT id, tool_name, status, idempotency_key, claimed_at, resolved_at, resolved_by, expires_at, created_at
FROM approvals
WHERE id = :'approval_id';
-- Expected:
-- - tool_name = 'transition_deal'
-- - status in ('pending','claimed','approved','rejected','expired')
-- - idempotency_key is non-null and stable
```

### 3) Concurrency: exactly one execution row for a specific approval
```sql
SELECT COUNT(*) AS execution_count
FROM tool_executions
WHERE approval_id = :'approval_id';
-- Expected: 1 (after a successful approve)
```

### 4) Audit trail exists and is ordered
```sql
SELECT event_type, actor_id, created_at
FROM audit_log
WHERE approval_id = :'approval_id'
ORDER BY created_at ASC;
-- Expected (minimum): approval_claimed → tool_execution_started → tool_execution_completed → approval_approved
-- (Reject path: approval_rejected; reclaim path: stale_claim_reclaimed)
```

### 5) Checkpoint tables exist and contain data
```sql
SELECT
  to_regclass('public.checkpoints') AS checkpoints,
  to_regclass('public.checkpoint_writes') AS checkpoint_writes,
  to_regclass('public.checkpoint_blobs') AS checkpoint_blobs;
-- Expected: all non-null regclass values

SELECT COUNT(*) AS checkpoint_count FROM checkpoints;
-- Expected: >= 1 after running HITL invoke
```

Optional: discover schema without guessing:
```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('checkpoints','checkpoint_writes','checkpoint_blobs')
ORDER BY table_name, ordinal_position;
```

### 6) Retrieval compliance flag (spike)
```bash
docker exec zakops-agent-api python -c "from app.core.langgraph.graph import DISABLE_LONG_TERM_MEMORY; print(DISABLE_LONG_TERM_MEMORY)"
# Expected: True
```

---

## Section 5: Security/config pitfalls (top 10)

1) **Actor spoofing on approve/reject**
- Risk: `actor_id` is taken from request body even when JWT is enforced; caller can claim actions “as someone else”.
- Check: review `/home/zaks/zakops-agent-api/app/api/v1/agent.py` approve/reject handlers.
- Fix: bind `actor_id` to JWT `sub` (snippet in Section 6).

2) **JWT enforcement defaults OFF**
- Risk: `AGENT_JWT_ENFORCE=false` allows unauthenticated approve/reject, which is unsafe if exposed via Cloudflare.
- Check: ensure production env sets `AGENT_JWT_ENFORCE=true` and strong `JWT_SECRET_KEY`.

3) **JWT secret default in compose**
- Risk: `docker-compose.yml` provides a fallback secret (`supersecret...`) if env missing.
- Check: verify production deploy never uses defaults; require secret injection.

4) **Decision-lock retrieval rule drift**
- Risk: mem0/pgvector config exists in `/home/zaks/zakops-agent-api/app/core/langgraph/graph.py`; if `DISABLE_LONG_TERM_MEMORY=false`, agent will query pgvector directly.
- Check: ensure `DISABLE_LONG_TERM_MEMORY` remains true for spike and until RAG REST-only path is implemented end-to-end.

5) **DB topology mismatch vs “existing Postgres instance”**
- Current: compose runs its own Postgres container on host port `5433`.
- Risk: diverges from “separate DB `zakops_agent` on existing Postgres instance”; can hide prod issues (roles, backups, HA, constraints).
- Check: document whether this is dev-only; ensure prod points to your existing Postgres and uses a dedicated DB/schema.

6) **Local-first / vLLM inference mismatch**
- Current: `/home/zaks/zakops-agent-api/app/services/llm.py` uses `ChatOpenAI` with `OPENAI_API_KEY`; `.env.development` sets `DEFAULT_LLM_MODEL=gpt-4o-mini`.
- Risk: violates “local-first + vLLM :8000” constraint; tests may pass using cloud but fail on local model tool-calling behavior.
- Check: add a dedicated local-model CI lane once vLLM is wired.

7) **Langfuse self-hosting mismatch**
- Current: `.env.development` points to `LANGFUSE_HOST=https://cloud.langfuse.com`.
- Risk: violates “Langfuse self-hosted :3001”; can break offline operation.
- Check: ensure local Langfuse config exists and port `3001` is reserved (compose already moved Grafana to `3002`).

8) **Mocks can hide real integration failures**
- Current: `transition_deal` returns `[MOCK]...` on connection error when `APP_ENV=development` and `ALLOW_TOOL_MOCKS=true`.
- Risk: approval path may “succeed” without actually hitting Deal API.
- Check: set `ALLOW_TOOL_MOCKS=false` for gate runs if you want integration assurance; keep mock gate log reviewed.

9) **Copyleft scan is best-effort**
- Current: denylist scans license metadata strings; some packages have `Unknown`/missing classifiers.
- Risk: false negatives; runtime copyleft sneaks in.
- Check: augment later with SBOM + license allowlist (but keep this spike gate as a minimum bar).

10) **Retry behavior may be blocked by unique idempotency key (edge case)**
- Risk: if an approval execution fails after inserting a `tool_executions` row, re-approving can hit a unique-constraint conflict unless the code reuses/updates the existing row.
- Check: simulate tool failure (e.g., Deal API unreachable with `ALLOW_TOOL_MOCKS=false`) and retry approve; ensure it doesn’t 500.
- Fix: reuse existing `tool_executions` row when `success=false` (snippet in Section 6).

---

## Section 6: Patch snippets (bash + SQL + schemas)

### 6A) Bash: make kill-9 + concurrency hard gates (drop-in snippet)
Insert into `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh` inside the “HARD GATE CHECKS” block:
```bash
# Gate 6: Kill-9 recovery must be PASSED
if [ -f "$OUT/checkpoint_kill9_test.log" ] && grep -q "RESULT: PASSED" "$OUT/checkpoint_kill9_test.log"; then
  log_info "Kill-9 recovery gate PASSED"
else
  log_error "Kill-9 recovery gate FAILED"
  GATE_FAILED=1
fi

# Gate 7: Concurrent approvals must have exactly 1 winner
if [ -f "$OUT/concurrent_approves.log" ] && grep -q "RESULT: PASSED" "$OUT/concurrent_approves.log"; then
  log_info "Concurrency gate PASSED"
else
  log_error "Concurrency gate FAILED"
  GATE_FAILED=1
fi
```

### 6B) SQL: minimal schema (approvals + tool_executions + audit_log)
(Already implemented in `/home/zaks/zakops-agent-api/migrations/001_approvals.sql`; this is the minimal core.)
```sql
CREATE TABLE approvals (
  id TEXT PRIMARY KEY,
  thread_id TEXT NOT NULL,
  checkpoint_id TEXT,
  tool_name TEXT NOT NULL,
  tool_args TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  idempotency_key TEXT NOT NULL UNIQUE,
  claimed_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  resolved_by TEXT,
  rejection_reason TEXT,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tool_executions (
  id TEXT PRIMARY KEY,
  approval_id TEXT REFERENCES approvals(id) ON DELETE SET NULL,
  idempotency_key TEXT NOT NULL UNIQUE,
  tool_name TEXT NOT NULL,
  tool_args TEXT NOT NULL,
  result TEXT,
  success BOOLEAN NOT NULL DEFAULT FALSE,
  error_message TEXT,
  executed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_log (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  actor_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  thread_id TEXT,
  approval_id TEXT,
  tool_execution_id TEXT,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

### 6C) Pydantic: spike response + approval decision payloads
Drop-in models (aligns with `/home/zaks/zakops-agent-api/app/schemas/agent.py`):
```python
from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

class PendingApproval(BaseModel):
    approval_id: str
    tool_name: Literal["transition_deal"]
    tool_args: Dict[str, Any]
    description: str
    expires_at: Optional[datetime] = None

class AgentInvokeResponse(BaseModel):
    thread_id: str
    status: Literal["completed", "pending_approval", "error"]
    response: Optional[str] = None
    pending_approval: Optional[PendingApproval] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ApprovalDecisionRequest(BaseModel):
    actor_id: str
    reason: Optional[str] = None
```

### 6D) Python: prevent retry from failing on unique `tool_executions.idempotency_key`
Patch target: `/home/zaks/zakops-agent-api/app/api/v1/agent.py` (approve path).
```python
# Replace the "existing success==True" query with a full fetch:
existing = db.exec(
    select(ToolExecution).where(ToolExecution.idempotency_key == idempotency_key)
).first()

if existing and existing.success:
    # idempotent fast-path (already executed)
    ...

if existing and not existing.success:
    # reuse the same row for retry (avoid unique violation)
    execution = existing
    execution.error_message = None
    execution.result = None
    execution.executed_at = datetime.now(UTC)
    db.add(execution)
    db.commit()
    execution_id = execution.id
else:
    # create new row on first attempt
    execution = ToolExecution(
        id=str(uuid.uuid4()),
        approval_id=approval_id,
        idempotency_key=idempotency_key,
        tool_name=tool_name,
        tool_args=tool_args_json,
        success=False,
        executed_at=datetime.now(UTC),
    )
    db.add(execution)
    db.commit()
    execution_id = execution.id
```

### 6E) Python: bind `actor_id` to JWT `sub` when enforced (prevents spoofing)
Patch target: `/home/zaks/zakops-agent-api/app/api/v1/agent.py` approve/reject handlers.
```python
# After Depends(require_approve_role):
effective_actor_id = action_request.actor_id
if user is not None:  # JWT enforced path
    effective_actor_id = user.subject  # bind actor to token subject
# Use effective_actor_id for audit + resolved_by + tool execution attribution
```
