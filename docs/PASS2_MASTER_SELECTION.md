# ZakOps Prebuilt Scaffold Master Plan (PASS 2)

**Version:** 1.0
**Date:** 2026-01-22
**Role:** Editor-in-Chief + Principal Architect
**Status:** FINAL SELECTION — READY FOR IMPLEMENTATION

---

## 1) Executive Summary

### Selection: wassim249/fastapi-langgraph-agent-production-ready-template

After synthesizing PASS 1 evidence from three independent research inputs (T1, T2, T3), resolving 7 contradictions, and applying the 8 gate checklist against Decision Lock constraints, **we select `wassim249/fastapi-langgraph-agent-production-ready-template` as the primary fork target** for the ZakOps Agent API (:8095).

**Why this scaffold wins:**

| Criterion | wassim249 | agent-service-toolkit | aegra |
|-----------|:---------:|:---------------------:|:-----:|
| Service Boundary (BND) | **5** | 5 | 3 |
| Security/Auth (SEC) | **4** | 2 | 2 |
| Checkpointing (CP) | **5** | 4 | 5 |
| Local-First (DEV) | **5** | 5 | 5 |
| Template Shape | **Clean** | Toolkit (pruning needed) | Platform (mismatch) |
| HITL Support | 1 (add) | 4 | 4 |

**Trade-off accepted:** wassim249 lacks built-in HITL (scored 1), but this is a **known, bounded gap** that we address by grafting interrupt/resume patterns from the `esurovtsev/langgraph-hitl-fastapi-demo` reference implementation. The alternative candidates (agent-service-toolkit, aegra) require more invasive adaptation to match ZakOps' service boundary and auth requirements.

**Reference library:** `JoshuaC215/agent-service-toolkit` provides the best reference for:
- MCP streamable-http client integration
- Interrupt/resume service patterns
- Test structure and pre-commit configuration

---

## 2) Selection Rationale (Evidence-Based)

### 2.1 Contradiction Resolution

| ID | Contradiction | Resolution | Evidence |
|----|---------------|------------|----------|
| C-01 | Which scaffold to fork first? (T1/T3: wassim249, T2: agent-service-toolkit) | **wassim249** — T1+T3 consensus (2:1), and agent-service-toolkit's strength (HITL) doesn't offset its auth/pruning burden | T1 §1, T3 §1, PASS1 scores |
| C-02 | MCP support in agent-service-toolkit (T2: missing, T3: present) | **T3 correct** — MCP streamable-http verified in `src/agents/github_mcp_agent/github_mcp_agent.py` | T3 §3B, code path verified |
| C-03 | Observability in agent-service-toolkit (LangSmith vs Langfuse) | **Both optional** — Langfuse can be integrated; LangSmith is default but removable | T2/T3 aligned after resolution |
| C-05 | wassim249 delta sizing (Medium vs Large) | **Medium** — Core surgery is bounded: LLM swap, tool registry, approval endpoints. HITL graft is isolated. | T1 §4, T3 §3A |
| C-07 | Port conventions (Langfuse :3000 vs :3001) | **Use :3001** per Decision Lock; configure all scaffolds to avoid :3000 (OpenWebUI conflict) | Decision Lock §5 |

### 2.2 Gate Checklist Results

| Gate | wassim249 | agent-service-toolkit | aegra |
|------|:---------:|:---------------------:|:-----:|
| G1: License (MIT/Apache-2.0) | ✅ MIT | ✅ MIT | ✅ Apache-2.0 |
| G2: Service boundary (:8095 / :8090) | ✅ Configurable | ✅ Configurable | ⚠️ Platform-shaped |
| G3: Durable checkpointing | ✅ AsyncPostgresSaver verified | ✅ AsyncPostgresSaver verified | ✅ AsyncPostgresSaver verified |
| G4: HITL support | ⚠️ Must add | ✅ interrupt/resume present | ✅ interrupt_before present |
| G5: Tool abstraction | ✅ Clear registry | ✅ Clear registry | ⚠️ Platform abstraction |
| G6: Observability compliance | ✅ Langfuse present | ⚠️ LangSmith default | ✅ Langfuse present |
| G7: Local-first | ✅ Compose ready | ✅ Compose ready | ✅ Compose ready |
| G8: Maintenance risk | ✅ 1868⭐, MIT, 70 commits | ✅ 4033⭐, MIT, 188 commits | ✅ 532⭐, Apache-2.0, active |

**Gate summary:** wassim249 passes 7/8 gates outright; the G4 (HITL) gap is resolvable with bounded effort.

### 2.3 Score Matrix (PASS 1 Normalized)

```
                              LG  CP  HITL STR  TV  RW/C IDEM OBS DEV SEC BND  TOTAL
wassim249/...                  5   5    1   4   4    1    1   4   5   4   5    39
JoshuaC215/agent-service-...   5   4    4   5   4    1    1   3   5   2   5    39
ibbybuilds/aegra               5   5    4   4   3    1    1   4   5   2   3    37
```

**Tie-breaker rationale:** With wassim249 and agent-service-toolkit tied at 39, we select wassim249 because:
1. **SEC=4 vs SEC=2** — JWT auth already implemented; agent-service-toolkit uses bearer secret
2. **Template shape** — wassim249 is a clean scaffold; agent-service-toolkit is a "toolkit" requiring significant pruning
3. **Consensus** — 2 of 3 research inputs (T1, T3) recommend wassim249 as primary

---

## 3) Target Architecture Using the Chosen Scaffold

### 3.1 ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ZAKOPS AGENT ARCHITECTURE                           │
│                      (Based on wassim249 Fork)                              │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐          ┌──────────────────┐
    │   Next.js UI     │◀────────▶│  Cloudflare      │
    │   (Existing)     │   SSE    │  (Routes→:8095)  │
    └──────────────────┘          └────────┬─────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENT API (:8095)                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Service                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │ /agent/     │  │ /agent/     │  │ JWT + RBAC  │  │ Health     │  │   │
│  │  │  invoke     │  │ approvals/* │  │ Middleware  │  │ /health    │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └─────────────┘  └────────────┘  │   │
│  │         │                │                                          │   │
│  │         ▼                ▼                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                 LangGraph State Machine                      │   │   │
│  │  │  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐   │   │   │
│  │  │  │ Router  │─▶│ Planner  │─▶│ Executor │─▶│ Approval    │   │   │   │
│  │  │  │  Node   │  │   Node   │  │   Node   │  │  Gate Node  │   │   │   │
│  │  │  └─────────┘  └──────────┘  └────┬─────┘  └──────┬──────┘   │   │   │
│  │  │                                  │               │          │   │   │
│  │  │               interrupt_before=["approval_gate"] │          │   │   │
│  │  └──────────────────────────────────┼───────────────┼──────────┘   │   │
│  │                                     │               │              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │              Hybrid Tool Gateway (ZakOps)                    │   │   │
│  │  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐  │   │   │
│  │  │  │ Direct Tools  │  │  MCP Client   │  │  Idempotency    │  │   │   │
│  │  │  │ (Deal, RAG)   │  │  (:9100)      │  │  + Audit Log    │  │   │   │
│  │  │  └───────┬───────┘  └───────┬───────┘  └─────────────────┘  │   │   │
│  │  │          │                  │                                │   │   │
│  │  │    READ / WRITE / CRITICAL permission enforcement            │   │   │
│  │  └──────────┼──────────────────┼────────────────────────────────┘   │   │
│  │             │                  │                                    │   │
│  └─────────────┼──────────────────┼────────────────────────────────────┘   │
│                │                  │                                        │
│  ┌─────────────┴──────────────────┴────────────────────────────────────┐   │
│  │            PostgreSQL (:5432) — Single Database                      │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │   │
│  │  │checkpoints │ │ approvals  │ │ tool_exec  │ │ deal_embeddings  │  │   │
│  │  │(LangGraph) │ │ (HITL)     │ │ (audit)    │ │ (pgvector 1024d) │  │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │                  │
          ┌──────────────┤  External Stack  ├──────────────┐
          │              │                  │              │
          ▼              └──────────────────┘              ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   vLLM (:8000)   │    │  Deal API        │    │  MCP Server      │
│  Qwen2.5-32B-AWQ │    │  (:8090)         │    │  (:9100)         │
│  --tool-parser   │    │  (Existing)      │    │  streamable-http │
│    hermes        │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
          ▲                                               ▲
          │              ┌──────────────────┐              │
          └──────────────│    LiteLLM       │──────────────┘
                         │  (routing)       │
                         │  cost-based      │
                         │  local→cloud     │
                         └──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│  Langfuse        │    │  RAG REST        │
│  (:3001)         │    │  (:8052)         │
│  Self-hosted     │    │  Retrieval       │
│  No raw content  │    │                  │
└──────────────────┘    └──────────────────┘
```

### 3.2 Service Boundary Mapping

| Service | Port | Source |
|---------|------|--------|
| Agent API | :8095 | **Fork of wassim249 → zakops-agent-api** |
| Deal API | :8090 | Existing (unchanged) |
| vLLM | :8000 | Existing (unchanged) |
| MCP Server | :9100 | Existing (unchanged) |
| RAG REST | :8052 | Existing (unchanged) |
| Langfuse | :3001 | Add to compose |
| PostgreSQL | :5432 | Existing + new tables |

---

## 4) Fork Plan (Actionable Checklist)

### Phase 0: Fork & Environment Setup

- [ ] Fork `wassim249/fastapi-langgraph-agent-production-ready-template` → `zakops-agent-api`
- [ ] Update `docker-compose.yml`:
  - [ ] Rename service `api` → `agent-api`
  - [ ] Change port mapping: `8095:8095` (was 8000:8000)
  - [ ] Add `vllm` service (if not using host network vLLM)
  - [ ] Add `langfuse` service on `:3001`
  - [ ] Move Grafana off `:3000` → `:3002` to avoid OpenWebUI conflict
  - [ ] Ensure Postgres image is `pgvector/pgvector:pg16`
- [ ] Create `.env.zakops` with:
  ```
  VLLM_BASE_URL=http://localhost:8000/v1
  DEAL_API_URL=http://localhost:8090
  MCP_SERVER_URL=http://localhost:9100
  RAG_REST_URL=http://localhost:8052
  LANGFUSE_HOST=http://localhost:3001
  JWT_SECRET=<generate>
  JWT_ISSUER=zakops-auth
  JWT_AUDIENCE=zakops-agent
  ```
- [ ] Verify `docker compose up` starts without port conflicts

### Phase 1: Core Surgery (Service Shell)

- [ ] **Delete** `app/api/v1/chatbot.py` (too simple, chat-centric)
- [ ] **Delete** `app/core/langgraph/tools.py` (example tools)
- [ ] **Create** `app/api/v1/agent.py` with ZakOps canonical endpoints:
  - [ ] `POST /agent/invoke` — Start workflow
  - [ ] `GET /agent/threads/{thread_id}/state` — Check status
  - [ ] `POST /agent/approvals/{approval_id}:approve` — Approve
  - [ ] `POST /agent/approvals/{approval_id}:reject` — Reject
- [ ] **Modify** `app/core/config.py`:
  - [ ] Add `VLLM_BASE_URL`, `DEAL_API_URL`, `MCP_SERVER_URL`, `RAG_REST_URL`
  - [ ] Add `JWT_ISSUER`, `JWT_AUDIENCE` (per Decision Lock)
- [ ] **Modify** `app/main.py`:
  - [ ] Change uvicorn port to `8095`
  - [ ] Initialize `AsyncPostgresSaver` with connection string
  - [ ] Register new `/agent/*` router

### Phase 2: LangGraph Adaptation

- [ ] **Replace** `app/core/langgraph/graph.py` with ZakOps Deal Lifecycle graph:
  - [ ] Define nodes: `router`, `planner`, `executor`, `approval_gate`
  - [ ] Configure `interrupt_before=["approval_gate"]`
  - [ ] Wire `AsyncPostgresSaver` as checkpointer
- [ ] **Create** `app/core/langgraph/nodes/`:
  - [ ] `router.py` — Intent classification
  - [ ] `planner.py` — Action planning
  - [ ] `executor.py` — Tool execution
  - [ ] `approval_gate.py` — Approval pause point
- [ ] **Graft HITL logic** from `esurovtsev/langgraph-hitl-fastapi-demo`:
  - [ ] Copy `Command(resume=...)` pattern into resume endpoint
  - [ ] Test interrupt → state persistence → resume flow

### Phase 3: Tool Gateway Implementation

- [ ] **Create** `app/core/tools/gateway.py` — HybridToolGateway class
- [ ] **Create** `app/core/tools/direct/`:
  - [ ] `deal_tools.py` — list_deals, get_deal, transition_deal (HTTP to :8090)
  - [ ] `rag_tools.py` — search_documents (HTTP to :8052)
  - [ ] `health_tools.py` — check_health
- [ ] **Create** `app/core/tools/mcp_client.py`:
  - [ ] MCP streamable-http client pointing to `:9100`
  - [ ] Reference `agent-service-toolkit/src/agents/github_mcp_agent/` for implementation
- [ ] **Implement** permission enforcement:
  - [ ] `READ` tools: execute immediately
  - [ ] `WRITE` tools: policy-dependent (configurable approval)
  - [ ] `CRITICAL` tools: always require approval
- [ ] **Implement** idempotency layer:
  - [ ] Create `tool_executions` table (idempotency_key, status, result)
  - [ ] Claim-first pattern: INSERT before execute
  - [ ] Return cached result on duplicate key

### Phase 4: Auth Hardening

- [ ] **Verify** existing JWT middleware in `app/core/middleware.py`:
  - [ ] Required claims: `sub`, `role`, `exp`, `iss`, `aud`
  - [ ] Issuer validation: `zakops-auth`
  - [ ] Audience validation: `zakops-agent`
- [ ] **Add** API key fallback:
  - [ ] Check `X-API-Key` header if no Bearer token
  - [ ] Store API keys as SHA256 hashes in database
- [ ] **Implement** RBAC enforcement:
  - [ ] VIEWER: read-only endpoints
  - [ ] OPERATOR: read + write
  - [ ] APPROVER: read + write + approve
  - [ ] ADMIN: all permissions
- [ ] **Add** auth audit logging to `audit_log` table

### Phase 5: Observability Compliance

- [ ] **Verify** Langfuse integration in `app/core/observability.py`
- [ ] **Implement** "no raw content" policy:
  - [ ] Wrap Langfuse callbacks to send only hash + length
  - [ ] Test with PII canary prompt → verify no raw content in traces
- [ ] **Add** OpenTelemetry spans for:
  - [ ] Workflow start/end
  - [ ] Tool invocations
  - [ ] Approval gates
- [ ] **Configure** Prometheus metrics endpoint

### Phase 6: Database Schema

- [ ] **Create** migration for new tables:
  ```sql
  -- Approvals table
  CREATE TABLE approvals (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      thread_id TEXT NOT NULL,
      tool_name TEXT NOT NULL,
      tool_args JSONB NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      decided_at TIMESTAMPTZ,
      decided_by TEXT,
      decision TEXT,
      CONSTRAINT approvals_status_check CHECK (status IN ('pending', 'approved', 'rejected', 'expired'))
  );

  -- Tool executions table (idempotency)
  CREATE TABLE tool_executions (
      idempotency_key TEXT PRIMARY KEY,
      tool_name TEXT NOT NULL,
      tool_args JSONB NOT NULL,
      status TEXT NOT NULL DEFAULT 'claimed',
      result JSONB,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      completed_at TIMESTAMPTZ,
      CONSTRAINT tool_exec_status_check CHECK (status IN ('claimed', 'completed', 'failed'))
  );

  -- Audit log table (immutable)
  CREATE TABLE audit_log (
      id BIGSERIAL PRIMARY KEY,
      event_type TEXT NOT NULL,
      event_data JSONB NOT NULL,
      actor TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  );
  CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
  CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
  ```

---

## 5) "First Working Demo" Scenario (MVP Validation)

### Scenario: Transition Deal with Approval Gate

**Objective:** Validate the complete Agent API flow from request → CRITICAL tool → approval gate → resume → execution → audit.

**Pre-conditions:**
- All services running (Agent :8095, Deal :8090, vLLM :8000, Postgres :5432, Langfuse :3001)
- JWT token with `role=APPROVER` available
- Test deal exists in Deal API

**Steps:**

```bash
# Step 1: Invoke agent with CRITICAL action
THREAD_ID=$(uuidgen)
curl -X POST http://localhost:8095/agent/invoke \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "'$THREAD_ID'",
    "input": "Transition deal DEAL-001 from Qualification to Proposal stage"
  }'

# Expected response:
# {
#   "status": "awaiting_approval",
#   "approval_id": "abc-123-def",
#   "thread_id": "<thread_id>",
#   "pending_action": {
#     "tool": "transition_deal",
#     "args": {"deal_id": "DEAL-001", "from_stage": "Qualification", "to_stage": "Proposal"},
#     "permission_tier": "CRITICAL"
#   }
# }

# Step 2: Verify state persisted (simulate crash recovery)
docker compose restart agent-api
sleep 5

curl -X GET http://localhost:8095/agent/threads/$THREAD_ID/state \
  -H "Authorization: Bearer $JWT_TOKEN"

# Expected: status still "awaiting_approval"

# Step 3: Approve the action
curl -X POST "http://localhost:8095/agent/approvals/abc-123-def:approve" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Approved for testing"}'

# Expected response:
# {
#   "status": "completed",
#   "thread_id": "<thread_id>",
#   "result": {
#     "tool": "transition_deal",
#     "success": true,
#     "deal_id": "DEAL-001",
#     "new_stage": "Proposal"
#   }
# }

# Step 4: Verify in Deal API
curl http://localhost:8090/api/deals/DEAL-001 \
  -H "Authorization: Bearer $JWT_TOKEN"

# Expected: stage = "Proposal"

# Step 5: Verify audit log
psql $DATABASE_URL -c "SELECT * FROM audit_log WHERE event_type = 'tool_executed' ORDER BY created_at DESC LIMIT 1;"

# Expected: row with tool_name='transition_deal', idempotency_key set

# Step 6: Verify Langfuse trace
# Open http://localhost:3001 → verify trace shows workflow without raw prompt/response content
```

**Acceptance Criteria:**
- [ ] `/agent/invoke` returns `awaiting_approval` for CRITICAL tool
- [ ] State survives process restart (kill -9 + restart)
- [ ] `/agent/approvals/{id}:approve` resumes and completes workflow
- [ ] Deal API reflects stage change
- [ ] `tool_executions` table has idempotency record
- [ ] `audit_log` table has execution event
- [ ] Langfuse trace visible with no raw content

---

## 6) Verification Plan (Repo & Capability Verification)

### 6.1 Pre-Fork Verification (Execute Before Committing to Fork)

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| License | `cat LICENSE` | MIT license text present |
| LangGraph | `grep -r "from langgraph" app/` | Import statements found |
| AsyncPostgresSaver | `grep -r "AsyncPostgresSaver\|PostgresSaver" app/` | Usage in graph compilation |
| JWT Auth | `grep -r "jwt\|JWT" app/core/` | JWT validation code present |
| Langfuse | `grep -r "langfuse" app/` | Langfuse callback/handler present |
| Compose | `docker compose config` | Valid compose file, services defined |
| Startup | `docker compose up -d && sleep 30 && curl localhost:8000/health` | 200 OK |

### 6.2 Post-Fork Integration Tests

| Test | Description | Pass Criteria |
|------|-------------|---------------|
| T-01 | Invoke simple query | `/agent/invoke` returns response within 30s |
| T-02 | Checkpoint persistence | Kill process mid-workflow, restart, verify state recovered |
| T-03 | HITL interrupt | CRITICAL tool triggers `awaiting_approval` status |
| T-04 | HITL resume | Approval endpoint resumes and completes workflow |
| T-05 | Tool validation | Invalid tool args rejected with 400 error |
| T-06 | Idempotency | Duplicate idempotency key returns cached result |
| T-07 | Auth enforcement | Request without token returns 401 |
| T-08 | RBAC enforcement | VIEWER role blocked from approve endpoint |
| T-09 | Langfuse trace | Trace visible in Langfuse UI |
| T-10 | No raw content | PII canary string not in Langfuse spans |

### 6.3 Blind Spot Verification (from PASS 1)

| ID | Blind Spot | Verification Method | Status |
|----|------------|---------------------|--------|
| B-01 | Durable checkpointing E2E | T-02 (kill -9 test) | Pending |
| B-02 | HITL semantics match MDv2 | T-03, T-04 (approval endpoints) | Pending |
| B-03 | Tool contract strictness | T-05 (invalid args test) | Pending |
| B-04 | READ/WRITE/CRITICAL tiers | Manual review + T-03 | Pending |
| B-05 | Idempotency claim-first | T-06 + concurrent load test | Pending |
| B-06 | Langfuse no raw content | T-10 (PII canary) | Pending |
| B-07 | Local-first (no cloud keys) | Startup with `OPENAI_API_KEY=` unset | Pending |
| B-08 | Port compatibility | Compose up with all ZakOps services | Pending |
| B-09 | MCP transport alignment | MCP conformance test against :9100 | Pending |

---

## 7) Risk & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **R-01**: HITL graft complexity exceeds estimate | Schedule slip | Medium | Time-box to 3 days; fall back to agent-service-toolkit if blocked |
| **R-02**: vLLM Hermes tool parsing failures | Tool calls malformed | Medium | Validate with 10-prompt test suite before integration; have prompt engineering fallback |
| **R-03**: AsyncPostgresSaver pool conflicts with app pool | Connection starvation | Low | Use separate connection pool for checkpointer; monitor connections |
| **R-04**: Langfuse "no raw content" requires deep refactor | Observability gap | Low | Accept hash+length only in Phase 1; defer full redaction to Phase 2 |
| **R-05**: Port collision during development | Dev friction | Low | Document all ports in PORTS.md; use `.env` for all port configs |
| **R-06**: MCP streamable-http client not working | Tool integration blocked | Medium | Reference agent-service-toolkit implementation; fallback to direct HTTP if MCP fails |
| **R-07**: Scope creep from "toolkit" features | Schedule slip | Medium | Delete all non-ZakOps code in Phase 0; enforce PR review for additions |

**Contingency:** If wassim249 fork encounters blocking issues in Phase 1-2, switch to agent-service-toolkit fork with auth/pruning overhead accepted.

---

## 8) Decision Log

| ID | Decision | Options Considered | Rationale | Date |
|----|----------|-------------------|-----------|------|
| D-01 | **Primary fork: wassim249** | wassim249, agent-service-toolkit, aegra | Best SEC (4) + BND (5) + template shape; HITL gap is bounded | 2026-01-22 |
| D-02 | **Reference: agent-service-toolkit** | N/A | Best MCP + interrupt/resume reference | 2026-01-22 |
| D-03 | **HITL pattern: graft from esurovtsev** | Implement from scratch, adopt aegra patterns | Smallest code delta; well-documented demo | 2026-01-22 |
| D-04 | **Reject aegra as primary** | aegra | Platform-shaped API (BND=3) requires more adaptation than HITL graft | 2026-01-22 |
| D-05 | **Langfuse on :3001** | :3000, :3001 | Avoid OpenWebUI (:3000) conflict per Decision Lock | 2026-01-22 |
| D-06 | **JWT auth retained from scaffold** | Implement fresh, adopt scaffold | wassim249 JWT is close to Decision Lock spec; minimal changes | 2026-01-22 |
| D-07 | **Tool gateway: hybrid (direct + MCP)** | MCP-only, direct-only | Decision Lock mandates hybrid; direct for Deal/RAG, MCP for extensibility | 2026-01-22 |
| D-08 | **Idempotency: claim-first pattern** | Check-then-execute, claim-first | Decision Lock specifies claim-first; prevents duplicate side effects | 2026-01-22 |

---

## Appendix A: Repository URLs

| Repository | URL | Usage |
|------------|-----|-------|
| **Primary Fork Target** | https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template | Fork to zakops-agent-api |
| Reference: MCP + Interrupt | https://github.com/JoshuaC215/agent-service-toolkit | Copy MCP client, interrupt patterns |
| Reference: HITL Demo | https://github.com/esurovtsev/langgraph-hitl-fastapi-demo | Copy Command(resume=...) pattern |
| Reference: Platform Patterns | https://github.com/ibbybuilds/aegra | Streaming/replay patterns if needed |

---

## Appendix B: File-Level Surgery Map (wassim249 Fork)

### Files to DELETE

```
app/api/v1/chatbot.py          # Replace with agent.py
app/core/langgraph/tools.py    # Replace with tool gateway
```

### Files to CREATE

```
app/api/v1/agent.py                    # ZakOps canonical endpoints
app/core/langgraph/nodes/router.py     # Intent classification
app/core/langgraph/nodes/planner.py    # Action planning
app/core/langgraph/nodes/executor.py   # Tool execution
app/core/langgraph/nodes/approval_gate.py  # HITL pause point
app/core/tools/gateway.py              # HybridToolGateway
app/core/tools/direct/deal_tools.py    # Deal API tools
app/core/tools/direct/rag_tools.py     # RAG tools
app/core/tools/direct/health_tools.py  # Health check tool
app/core/tools/mcp_client.py           # MCP streamable-http client
app/db/models/approvals.py             # Approvals model
app/db/models/tool_executions.py       # Idempotency model
app/db/models/audit_log.py             # Audit log model
migrations/versions/001_zakops_tables.py  # Schema migration
```

### Files to MODIFY

```
app/main.py                    # Port, router, checkpointer init
app/core/config.py             # ZakOps env vars
app/core/langgraph/graph.py    # New graph definition
app/core/middleware.py         # Add API key fallback, RBAC
app/core/observability.py      # No raw content wrapper
docker-compose.yml             # Ports, services, Langfuse
.env.example                   # ZakOps variables
```

---

**Document Status:** FINAL — Ready for implementation
**Next Action:** Execute Phase 0 (Fork & Environment Setup)
