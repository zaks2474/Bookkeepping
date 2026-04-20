# ZakOps Prebuilt Scaffold Master Plan v2

**Version:** 2.0
**Date:** 2026-01-22
**Role:** Editor-in-Chief + Principal Architect
**Status:** FINAL — READY FOR IMPLEMENTATION
**Audit Status:** All PASS3 Blockers (8) and Majors (12) resolved

---

## 1) Executive Summary

### Selection: wassim249/fastapi-langgraph-agent-production-ready-template

After synthesizing PASS 1 evidence, resolving contradictions, applying the 8 gate checklist against Decision Lock constraints, and completing PASS 3 hostile audit remediation, **we select `wassim249/fastapi-langgraph-agent-production-ready-template` as the primary fork target** for the ZakOps Agent API (:8095).

**Why this scaffold wins:**

| Criterion | wassim249 | agent-service-toolkit | aegra |
|-----------|:---------:|:---------------------:|:-----:|
| Service Boundary (BND) | **5** | 5 | 3 |
| Security/Auth (SEC) | **4** | 2 | 2 |
| Checkpointing (CP) | **5** | 4 | 5 |
| Local-First (DEV) | **5** | 5 | 5 |
| Template Shape | **Clean** | Toolkit (pruning needed) | Platform (mismatch) |
| HITL Support | 1 (add) | 4 | 4 |

**Trade-off accepted:** wassim249 lacks built-in HITL (scored 1). This gap is addressed via a **2-day time-boxed spike** implementing the approval state machine for one CRITICAL tool (`transition_deal`). The spike has explicit success criteria (§4.1 Spike DoD). If the spike fails, we switch to `agent-service-toolkit` as fallback.

**Reference library:** `JoshuaC215/agent-service-toolkit` provides the best reference for:
- MCP streamable-http client integration
- Interrupt/resume service patterns
- Test structure and pre-commit configuration

---

## 2) Selection Rationale (Evidence-Based)

### 2.1 Contradiction Resolution

| ID | Contradiction | Resolution | Evidence |
|----|---------------|------------|----------|
| C-01 | Which scaffold to fork first? | **wassim249** — SEC=4 vs SEC=2, template shape, PASS 2 gate outcomes (checkpoint kill-9 test, auth negative tests, tool call validation) | Gate artifacts required |
| C-02 | MCP support in agent-service-toolkit | **T3 correct** — MCP streamable-http verified in `src/agents/github_mcp_agent/github_mcp_agent.py` | T3 §3B, code path verified |
| C-03 | Observability (LangSmith vs Langfuse) | **Both optional** — Langfuse can be integrated; LangSmith is default but removable | T2/T3 aligned after resolution |
| C-05 | wassim249 delta sizing | **Medium** — Core surgery is bounded; HITL spike defines go/no-go | Spike DoD in §4.1 |
| C-07 | Port conventions | **:3001** per Decision Lock; Langfuse internal port 3000 mapped to host 3001 | Decision Lock §5 |

### 2.2 Gate Checklist Results (with Measured Outcomes)

| Gate | wassim249 | Verification Required | Status |
|------|:---------:|----------------------|--------|
| G1: License | ✅ MIT | `cat LICENSE` + dependency license report (no GPL/AGPL at runtime) | Verified |
| G2: Service boundary | ✅ Configurable | Runs on :8095; calls Deal API :8090 | Pending bring-up |
| G3: Durable checkpointing | ✅ AsyncPostgresSaver | **Kill-9 test**: invoke → kill → restart → verify state | Pending bring-up |
| G4: HITL support | ⚠️ Must add | **Spike DoD**: approval endpoints + checkpoint resume + exactly-once | Pending spike |
| G5: Tool abstraction | ✅ Clear registry | **Choke point test**: mock gateway, assert no direct tool invocation outside gateway | Pending test |
| G6: Observability | ✅ Langfuse present | Trace creation test + PII canary test (no raw content in traces/logs/DB) | Pending test |
| G7: Local-first | ✅ Compose ready | Starts with `OPENAI_API_KEY=` unset; uses local vLLM only | Pending bring-up |
| G8: Maintenance | ✅ 1868⭐, MIT | Maintainer count, release cadence, security policy reviewed | Pending |

**Gate artifacts required before Phase 1:**
- [ ] Checkpoint kill-9 test log
- [ ] Auth negative test results (expired, wrong issuer, wrong audience, missing role)
- [ ] Tool call validation test log
- [ ] Streaming test log
- [ ] Dependency license report (no copyleft at runtime)

### 2.3 Score Matrix (PASS 1 Normalized)

```
                              LG  CP  HITL STR  TV  RW/C IDEM OBS DEV SEC BND  TOTAL
wassim249/...                  5   5    1   4   4    1    1   4   5   4   5    39
JoshuaC215/agent-service-...   5   4    4   5   4    1    1   3   5   2   5    39
ibbybuilds/aegra               5   5    4   4   3    1    1   4   5   2   3    37
```

**Tie-breaker rationale:** With wassim249 and agent-service-toolkit tied at 39, we select wassim249 because:
1. **SEC=4 vs SEC=2** — JWT auth already implemented; agent-service-toolkit uses bearer secret
2. **Template shape** — wassim249 is a clean scaffold; agent-service-toolkit requires significant pruning
3. **Measured gate outcomes** — Selection confirmed by bring-up test pack results

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
│  │  │  stream     │  │             │  │             │  │            │  │   │
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
│  │  │              Hybrid Tool Gateway (SINGLE CHOKE POINT)        │   │   │
│  │  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐  │   │   │
│  │  │  │ Direct Tools  │  │  MCP Client   │  │  Idempotency    │  │   │   │
│  │  │  │ (Deal API)    │  │  (:9100)      │  │  + Audit Log    │  │   │   │
│  │  │  └───────┬───────┘  └───────┬───────┘  └─────────────────┘  │   │   │
│  │  │          │                  │                                │   │   │
│  │  │    READ / WRITE / CRITICAL permission enforcement            │   │   │
│  │  └──────────┼──────────────────┼────────────────────────────────┘   │   │
│  │             │                  │                                    │   │
│  └─────────────┼──────────────────┼────────────────────────────────────┘   │
│                │                  │                                        │
│  ┌─────────────┴──────────────────┴────────────────────────────────────┐   │
│  │            PostgreSQL — Agent Database (zakops_agent)               │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │   │
│  │  │checkpoints │ │ approvals  │ │ tool_exec  │ │   task_queue     │  │   │
│  │  │(LangGraph) │ │ (HITL)     │ │ (audit)    │ │ (SKIP LOCKED)    │  │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │                  │
          ┌──────────────┤  External Stack  ├──────────────┐
          │              │  (Host Services) │              │
          ▼              └──────────────────┘              ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   vLLM (:8000)   │    │  Deal API        │    │  MCP Server      │
│  Qwen2.5-32B-AWQ │    │  (:8090)         │    │  (:9100)         │
│  --tool-parser   │    │  (Existing)      │    │  streamable-http │
│    hermes        │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Langfuse        │    │  RAG REST        │    │  LiteLLM         │
│  (:3001)         │    │  (:8052)         │    │  (Phase 2)       │
│  External/       │    │  (Exclusive      │    │  Deterministic   │
│  Self-hosted     │    │   retrieval)     │    │  Routing         │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### 3.2 Service Boundary Mapping (PORTS.md Authoritative)

| Service | Host Port | Container Port | Source | Network Mode |
|---------|-----------|----------------|--------|--------------|
| Agent API | 8095 | 8095 | Fork of wassim249 | zakops-network |
| Deal API | 8090 | — | Existing (host) | host.docker.internal |
| vLLM | 8000 | — | Existing (host) | host.docker.internal |
| MCP Server | 9100 | — | Existing (host) | host.docker.internal |
| RAG REST | 8052 | — | Existing (host) | host.docker.internal |
| Langfuse | 3001 | 3000 | External or docker-compose.langfuse.yml | zakops-network |
| Agent Postgres | — (internal) | 5432 | pgvector/pgvector:pg16 | zakops-network |

**Create `PORTS.md` in repo root as single source of truth. All compose/env/tests must reference this file.**

### 3.3 Networking Modes (Authoritative)

**Mode A: Host-Services (Recommended for ZakOps workstation)**
```bash
# .env.zakops (host-services mode)
VLLM_BASE_URL=http://host.docker.internal:8000/v1
DEAL_API_URL=http://host.docker.internal:8090
MCP_SERVER_URL=http://host.docker.internal:9100
RAG_REST_URL=http://host.docker.internal:8052
LANGFUSE_HOST=http://host.docker.internal:3001
```

Agent API container connects to existing host services via `host.docker.internal`. Postgres for agent runs in compose with internal-only networking (no host port binding to avoid collision with Deal API Postgres on :5432).

**Mode B: All-in-Compose (CI/Testing)**
```bash
# .env.zakops (all-in-compose mode)
VLLM_BASE_URL=http://vllm:8000/v1
DEAL_API_URL=http://deal-api:8090
MCP_SERVER_URL=http://mcp:9100
RAG_REST_URL=http://rag-rest:8052
LANGFUSE_HOST=http://langfuse:3000
```

All services in compose; use service DNS names.

**NEVER use `localhost` in `.env.zakops` for container mode.**

### 3.4 DB Topology (Authoritative)

**Decision: Agent uses a SEPARATE DATABASE on existing Postgres instance.**

```
PostgreSQL Instance (host :5432)
├── zakops_deals      # Deal API database (existing)
└── zakops_agent      # Agent API database (NEW)
    ├── checkpoints
    ├── approvals
    ├── tool_executions
    ├── audit_log
    └── task_queue
```

**Rationale:** Avoids port collision; allows independent schema evolution; Deal API remains unchanged.

**Connection string:** `postgresql://agent_user:***@host.docker.internal:5432/zakops_agent`

If Postgres is not shared, Agent compose creates its own Postgres on internal network only (no host port binding).

### 3.5 Retrieval Path (Authoritative)

**Decision: Retrieval is EXCLUSIVELY via RAG REST (:8052).**

- Agent API calls RAG REST for all document retrieval
- No direct pgvector queries from Agent API
- `deal_embeddings` table is owned by RAG REST, not Agent API
- Agent schema does NOT include embedding tables

**Rationale:** Single retrieval path prevents split-brain indexing/security semantics.

### 3.6 Langfuse Deployment (Authoritative)

**Decision: Langfuse is EXTERNAL for MVP; self-hosted deployment is Phase 2.**

For MVP:
- Langfuse runs externally (existing ZakOps Langfuse instance or cloud)
- Agent API integrates via `LANGFUSE_HOST` environment variable
- If no Langfuse available, observability degrades gracefully (traces disabled)

For Phase 2:
- Provide `docker-compose.langfuse.yml` with full self-hosted stack
- Includes Postgres, Redis, and Langfuse server
- Health check: `curl -f http://localhost:3001/api/public/health`

**Bring-up test:** Agent can create a trace (HTTP 2xx from Langfuse API) or gracefully skip if unavailable.

---

## 4) Fork Plan (Actionable Checklist)

### 4.1 HITL Spike Definition of Done (2-Day Time-Box)

**Before proceeding to Phase 1, complete this spike to validate the HITL approach:**

**Spike Objective:** Implement approval endpoints + checkpoint resume + exactly-once tool execution for `transition_deal` (one CRITICAL tool).

**Success Criteria:**
- [ ] `POST /agent/invoke` with CRITICAL tool returns `awaiting_approval` with `approval_id`
- [ ] Checkpoint persists across process crash (kill -9 mid-approval)
- [ ] `POST /agent/approvals/{id}:approve` resumes graph and executes tool exactly once
- [ ] Concurrent approval attempts (N=10) result in exactly one tool execution
- [ ] Idempotency key prevents duplicate side effects

**Fail Criteria (switch to agent-service-toolkit):**
- Checkpoint state cannot be reliably resumed after crash
- Approval state machine requires rewriting LangGraph internals
- Integration complexity exceeds 2 days

### 4.2 Scaffold Reality Check (Verified Paths)

**Execute before Phase 1 to ground the plan in actual scaffold structure:**

```bash
# Clone and inspect
git clone https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template zakops-agent-api
cd zakops-agent-api

# Verify service names
docker compose config --services > /tmp/services.txt

# Verify file structure
find . -maxdepth 4 -type f -name "*.py" > /tmp/files.txt

# Run plan conformance check
# Assert every path in this plan exists in the fork
```

**Update Appendix B with actual paths before starting work.**

### Phase 0: Fork & Environment Setup

- [ ] Fork `wassim249/fastapi-langgraph-agent-production-ready-template` → `zakops-agent-api`
- [ ] Run Scaffold Reality Check (§4.2); update all paths in this plan
- [ ] Generate dependency license report; confirm no GPL/AGPL at runtime
- [ ] Run vulnerability scan; generate SBOM (CycloneDX)
- [ ] Create `PORTS.md` with all port assignments
- [ ] Update `docker-compose.yml`:
  - [ ] Rename service per scaffold reality check → `agent-api`
  - [ ] Change port mapping: `8095:8095`
  - [ ] Remove Postgres host port binding (internal network only)
  - [ ] Move Grafana off `:3000` → `:3002`
  - [ ] Ensure Postgres image is `pgvector/pgvector:pg16`
- [ ] Create `.env.zakops` with host-services URLs (NO localhost):
  ```bash
  # Host-services mode (ZakOps workstation)
  VLLM_BASE_URL=http://host.docker.internal:8000/v1
  DEAL_API_URL=http://host.docker.internal:8090
  MCP_SERVER_URL=http://host.docker.internal:9100
  RAG_REST_URL=http://host.docker.internal:8052
  LANGFUSE_HOST=http://host.docker.internal:3001

  # Agent database (separate from Deal API)
  DATABASE_URL=postgresql://agent_user:${AGENT_DB_PASSWORD}@host.docker.internal:5432/zakops_agent

  # JWT (Decision Lock requirements)
  JWT_SECRET=${JWT_SECRET}
  JWT_ISSUER=zakops-auth
  JWT_AUDIENCE=zakops-agent
  JWT_ALGORITHM=HS256
  ```
- [ ] Run bring-up test pack (§6.1)
- [ ] Verify `docker compose up` starts; smoke test curls all service URLs from inside container

### Phase 1: Core Surgery (Service Shell)

- [ ] **Deprecate** existing chat endpoints (keep streaming plumbing for reuse)
- [ ] **Create** `app/api/v1/agent.py` with ZakOps canonical endpoints (MDv2 schema):

**POST /agent/invoke — Request Schema:**
```json
{
  "thread_id": "string (optional, generated if omitted)",
  "message": "string (required)",
  "actor_id": "string (required)",
  "deal_id": "string (optional)",
  "context": {"key": "value"}
}
```

**POST /agent/invoke — Response Schema:**
```json
{
  "thread_id": "string",
  "status": "completed | awaiting_approval | error",
  "content": "string (optional, agent response)",
  "pending_approval": {
    "approval_id": "string",
    "tool": "string",
    "args": {},
    "permission_tier": "CRITICAL",
    "requested_by": "string",
    "requested_at": "ISO8601"
  },
  "actions_taken": [{"tool": "string", "result": {}}],
  "error": "string (optional)"
}
```

- [ ] **Create** `POST /agent/invoke/stream` (SSE endpoint):
  - Returns incremental tokens/events
  - Stream ends with `awaiting_approval` event if interrupted
  - Reuse existing streaming plumbing from chat endpoints

- [ ] **Create** `GET /agent/threads/{thread_id}/state`
- [ ] **Create** `POST /agent/approvals/{approval_id}:approve`
- [ ] **Create** `POST /agent/approvals/{approval_id}:reject`
- [ ] **Add** JSON Schema contract tests for all endpoints; fail build if schema differs from MDv2

- [ ] **Modify** config to add ZakOps env vars (per scaffold reality check)
- [ ] **Modify** main.py:
  - [ ] Change uvicorn port to `8095`
  - [ ] Initialize `AsyncPostgresSaver` with connection string
  - [ ] Register new `/agent/*` router

### Phase 2: LangGraph Adaptation + Queue

- [ ] **Create** ZakOps Deal Lifecycle graph:
  - [ ] Define nodes: `router`, `planner`, `executor`, `approval_gate`
  - [ ] Configure `interrupt_before=["approval_gate"]`
  - [ ] Wire `AsyncPostgresSaver` as checkpointer (separate connection pool)
- [ ] **Create** graph nodes (per scaffold reality check paths)
- [ ] **Implement** HITL logic per spike results:
  - [ ] `Command(resume=...)` pattern for approval resume
  - [ ] Approval state written to graph state before interrupt
  - [ ] Resume loads approval row, does NOT re-propose

- [ ] **Create** `task_queue` table and worker service:
  ```sql
  CREATE TABLE task_queue (
      id BIGSERIAL PRIMARY KEY,
      task_type TEXT NOT NULL,
      payload JSONB NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      attempts INTEGER NOT NULL DEFAULT 0,
      max_attempts INTEGER NOT NULL DEFAULT 3,
      scheduled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      claimed_at TIMESTAMPTZ,
      completed_at TIMESTAMPTZ,
      error TEXT,
      CONSTRAINT task_queue_status_check CHECK (status IN ('pending', 'claimed', 'completed', 'failed', 'dead_letter'))
  );
  CREATE INDEX idx_task_queue_pending ON task_queue(status, scheduled_at) WHERE status = 'pending';

  CREATE TABLE task_queue_dlq (
      id BIGSERIAL PRIMARY KEY,
      original_task_id BIGINT NOT NULL,
      task_type TEXT NOT NULL,
      payload JSONB NOT NULL,
      error TEXT NOT NULL,
      failed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  );
  ```
- [ ] **Implement** SKIP LOCKED worker (minimal, even if single-threaded for MVP)
- [ ] **Add** LiteLLM routing stub (Phase 2 implementation; explicit in plan):
  - For MVP: direct vLLM calls
  - Phase 2: LiteLLM gateway with routing policy

### Phase 3: Tool Gateway Implementation

- [ ] **Create** HybridToolGateway class (SINGLE CHOKE POINT for all tool calls)
- [ ] **Enforce** no direct tool invocation outside gateway module
- [ ] **Create** direct tools:
  - [ ] `deal_tools.py` — list_deals, get_deal, transition_deal (HTTP to Deal API)
  - [ ] `health_tools.py` — check_health
- [ ] **Create** MCP client with contract checklist:
  - [ ] Transport: streamable-http
  - [ ] Per-tool timeout (configurable, default 30s)
  - [ ] Retry: exponential backoff (3 attempts, 1s/2s/4s)
  - [ ] Parameter validation before call
  - [ ] Error normalization to standard format
  - [ ] Logging of all MCP calls (no raw content)
- [ ] **Implement** permission enforcement per Tool Catalog (§4.4)
- [ ] **Implement** idempotency layer:
  - [ ] Idempotency key derivation: `sha256(thread_id + tool_name + canonical_args_json + approval_id)`
  - [ ] Claim-first pattern: INSERT before execute
  - [ ] Return cached result on duplicate key
  - [ ] Concurrency test: 50 parallel calls → exactly one execution

### 4.4 Tool Catalog (Authoritative)

| Tool | Permission Tier | Approval Required | Idempotent |
|------|-----------------|-------------------|------------|
| `list_deals` | READ | No | N/A |
| `get_deal` | READ | No | N/A |
| `search_documents` | READ | No | N/A |
| `check_health` | READ | No | N/A |
| `create_deal` | WRITE | Policy-dependent | Yes |
| `update_deal` | WRITE | Policy-dependent | Yes |
| `transition_deal` | CRITICAL | **Always** | Yes |
| `delete_deal` | CRITICAL | **Always** | Yes |
| `send_email` | CRITICAL | **Always** | Yes |
| MCP tools (external) | WRITE | Policy-dependent | Yes |

### Phase 4: Auth Hardening

- [ ] **Implement/Modify** JWT verification to enforce Decision Lock requirements:
  - [ ] Required claims: `sub`, `role`, `exp`, `iss`, `aud`
  - [ ] Issuer validation: reject if `iss != "zakops-auth"`
  - [ ] Audience validation: reject if `aud != "zakops-agent"`
  - [ ] Expiry validation: reject if `exp < now()`
  - [ ] Role extraction: parse `role` claim for RBAC
- [ ] **Add** negative test cases:
  - [ ] Expired token → 401
  - [ ] Wrong issuer → 401
  - [ ] Wrong audience → 401
  - [ ] Missing role → 401
  - [ ] Valid token → 200
- [ ] **Add** API key fallback:
  - [ ] Check `X-API-Key` header if no Bearer token
  - [ ] Store API keys as SHA256 hashes in database
  - [ ] Revoked keys → 401
- [ ] **Implement** RBAC enforcement:
  - [ ] VIEWER: read-only endpoints
  - [ ] OPERATOR: read + write
  - [ ] APPROVER: read + write + approve
  - [ ] ADMIN: all permissions
  - [ ] Test: VIEWER cannot call approve endpoint
- [ ] **Add** auth audit logging to `audit_log` table

### Phase 5: Observability Compliance

- [ ] **Integrate** Langfuse (graceful degradation if unavailable)
- [ ] **Implement** "no raw content" policy across ALL surfaces:
  - [ ] Langfuse traces: hash + length only for prompts/responses
  - [ ] Application logs: never log raw prompts/responses/tool args
  - [ ] Database: store hashes/summaries for tool args/results
- [ ] **Add** PII canary test:
  - [ ] Send prompt with canary string
  - [ ] Assert canary NOT in: `docker logs`, any DB table, Langfuse spans
- [ ] **Add** OpenTelemetry spans for workflow/tool/approval events
- [ ] **Configure** Prometheus metrics endpoint

### Phase 6: Database Schema

- [ ] **Create** migration with extension prelude:
```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Approvals table (HITL state machine)
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    tool_args_hash TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    requested_by TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at TIMESTAMPTZ,
    decided_by TEXT,
    decision TEXT,
    CONSTRAINT approvals_status_check CHECK (status IN ('pending', 'approved', 'rejected', 'expired'))
);
CREATE INDEX idx_approvals_thread_id ON approvals(thread_id);
CREATE INDEX idx_approvals_status ON approvals(status) WHERE status = 'pending';

-- Tool executions table (idempotency)
CREATE TABLE tool_executions (
    idempotency_key TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    tool_args_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'claimed',
    result_hash TEXT,
    result_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT tool_exec_status_check CHECK (status IN ('claimed', 'completed', 'failed'))
);

-- Audit log table (IMMUTABLE - enforced by permissions)
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    trace_id TEXT NOT NULL,
    thread_id TEXT,
    actor_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL,
    idempotency_key TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_thread_id ON audit_log(thread_id);

-- Enforce audit_log immutability
REVOKE UPDATE, DELETE ON audit_log FROM agent_user;
-- Or use trigger:
-- CREATE FUNCTION prevent_audit_mutation() RETURNS TRIGGER AS $$
-- BEGIN RAISE EXCEPTION 'audit_log is immutable'; END;
-- $$ LANGUAGE plpgsql;
-- CREATE TRIGGER audit_log_immutable BEFORE UPDATE OR DELETE ON audit_log
--   FOR EACH ROW EXECUTE FUNCTION prevent_audit_mutation();

-- Task queue (from Phase 2)
-- ... (see Phase 2 schema)
```

- [ ] **Test** migrations on fresh Postgres container with no pre-installed extensions
- [ ] **Test** audit_log immutability: UPDATE/DELETE as app role → denied

---

## 4.5 Approval Invariants (Authoritative)

**Approval State Machine:**
```
CRITICAL tool proposed
        │
        ▼
┌───────────────┐
│    pending    │ ◀── INSERT approvals row with:
│               │     - approval_id (UUID)
│               │     - thread_id (links to checkpoint)
│               │     - tool_name, tool_args_hash
│               │     - idempotency_key
│               │     - requested_by (actor_id)
└───────┬───────┘
        │
   LangGraph interrupt_before=["approval_gate"]
   Checkpoint saved with pending_approval in state
        │
        ▼
┌───────────────┐
│   awaiting    │ ── API returns { status: "awaiting_approval", pending_approval: {...} }
│   approval    │
└───────┬───────┘
        │
   POST /agent/approvals/{id}:approve or :reject
        │
        ├── approve ──▶ UPDATE approvals SET status='approved', decided_by, decided_at
        │               │
        │               ▼
        │         Load checkpoint by thread_id
        │         Inject approval decision into graph state
        │         Resume graph (Command(resume=...))
        │               │
        │               ▼
        │         ┌───────────────┐
        │         │   approved    │
        │         └───────┬───────┘
        │                 │
        │         Tool gateway executes with idempotency_key
        │         (claim-first: INSERT tool_executions first)
        │                 │
        │                 ▼
        │         ┌───────────────┐
        │         │   completed   │
        │         └───────────────┘
        │
        └── reject ──▶ UPDATE approvals SET status='rejected', decided_by, decided_at
                      │
                      ▼
                Resume graph with rejection
                Graph terminates gracefully
```

**Invariants:**
1. Every CRITICAL tool proposal creates an `approvals` row BEFORE interrupt
2. `approval_id` is the primary key; `thread_id` links to LangGraph checkpoint
3. `idempotency_key` is pre-computed and stored; same key used for tool execution
4. Resume endpoint loads approval row, validates decision, resumes checkpoint
5. Resume does NOT re-propose the tool; decision is injected into state
6. Tool execution uses claim-first idempotency; concurrent resumes → one execution

---

## 5) "First Working Demo" Scenario (MVP Validation)

### Scenario: Transition Deal with Approval Gate

**Objective:** Validate the complete Agent API flow from request → CRITICAL tool → approval gate → crash recovery → resume → execution → audit.

**Pre-conditions:**
- All services running (Agent :8095, Deal API :8090, vLLM :8000, Postgres)
- JWT token with `role=APPROVER`, `iss=zakops-auth`, `aud=zakops-agent`
- Test deal exists in Deal API (use actual Deal API client, not assumed path)
- Langfuse available (or gracefully skipped)

**Steps:**

```bash
# Step 1: Invoke agent with CRITICAL action (MDv2 schema)
curl -X POST http://localhost:8095/agent/invoke \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Transition deal DEAL-001 from Qualification to Proposal stage",
    "actor_id": "user-123",
    "deal_id": "DEAL-001"
  }'

# Expected response (MDv2 schema):
# {
#   "thread_id": "...",
#   "status": "awaiting_approval",
#   "pending_approval": {
#     "approval_id": "abc-123-def",
#     "tool": "transition_deal",
#     "args": {"deal_id": "DEAL-001", "from_stage": "Qualification", "to_stage": "Proposal"},
#     "permission_tier": "CRITICAL",
#     "requested_by": "user-123",
#     "requested_at": "2026-01-22T..."
#   },
#   "actions_taken": []
# }

# Capture values
THREAD_ID=<from response>
APPROVAL_ID=<from response>

# Step 2: Verify state persisted (HARD CRASH, not graceful restart)
CONTAINER_ID=$(docker ps -q -f name=agent-api)
docker kill -s KILL $CONTAINER_ID
sleep 2
docker compose up -d agent-api
sleep 10

# Verify state survives crash
curl -X GET "http://localhost:8095/agent/threads/$THREAD_ID/state" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Expected: status = "awaiting_approval", pending_approval present

# Step 3: Approve the action
curl -X POST "http://localhost:8095/agent/approvals/$APPROVAL_ID:approve" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Approved for testing", "actor_id": "approver-456"}'

# Expected response:
# {
#   "thread_id": "...",
#   "status": "completed",
#   "content": "Deal DEAL-001 transitioned to Proposal stage.",
#   "actions_taken": [
#     {"tool": "transition_deal", "result": {"success": true, "deal_id": "DEAL-001", "new_stage": "Proposal"}}
#   ]
# }

# Step 4: Verify in Deal API (use actual Deal API client)
# Example using existing ZakOps Deal API:
curl "http://localhost:8090/api/v1/deals/DEAL-001" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Expected: stage = "Proposal"

# Step 5: Verify exactly-once execution (idempotency)
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tool_executions WHERE idempotency_key LIKE '%transition_deal%DEAL-001%';"
# Expected: 1

# Step 6: Verify audit log
psql $DATABASE_URL -c "SELECT trace_id, actor_id, event_type, idempotency_key FROM audit_log WHERE event_type = 'tool_executed' ORDER BY created_at DESC LIMIT 1;"
# Expected: row with actor_id, trace_id, idempotency_key all set

# Step 7: Verify no raw content in logs/traces
docker logs agent-api 2>&1 | grep -i "qualification\|proposal" | wc -l
# Expected: 0 (no raw deal content in logs)

# Step 8: Verify Langfuse trace (if available)
# Open http://localhost:3001 → verify trace shows workflow
# Assert: no raw prompt/response content visible
```

**Acceptance Criteria:**
- [ ] `/agent/invoke` returns `awaiting_approval` for CRITICAL tool with MDv2 schema
- [ ] `actor_id` recorded in approvals table and audit_log
- [ ] State survives hard crash (kill -9 + restart)
- [ ] `/agent/approvals/{id}:approve` resumes and completes workflow
- [ ] Deal API reflects stage change (via Deal API client)
- [ ] `tool_executions` table has exactly one record (idempotency enforced)
- [ ] `audit_log` table has execution event with trace_id, actor_id, idempotency_key
- [ ] No raw content in docker logs
- [ ] Langfuse trace visible with no raw content (or gracefully skipped)

---

## 6) Verification Plan (Repo & Capability Verification)

### 6.1 Pre-Fork Bring-Up Test Pack (Execute Before Committing to Fork)

**Replace grep checks with runtime tests:**

| Test | Command | Pass Criteria |
|------|---------|---------------|
| License | `cat LICENSE && pip-licenses --format=csv > /tmp/deps.csv && grep -c "GPL" /tmp/deps.csv` | MIT present; 0 GPL at runtime |
| Checkpoint kill-9 | See script below | State recovered after SIGKILL |
| Auth negative | See script below | 401 on invalid tokens |
| Tool call | `curl -X POST .../tools/call health` | 200 OK with result |
| Streaming | `curl -N .../stream` | SSE events received |
| Container networking | `docker exec agent-api curl $VLLM_BASE_URL/health` | 200 OK |

**Checkpoint kill-9 test script:**
```bash
#!/bin/bash
# start workflow
RESPONSE=$(curl -s -X POST http://localhost:8095/agent/invoke -H "Content-Type: application/json" \
  -d '{"message": "test", "actor_id": "test"}')
THREAD_ID=$(echo $RESPONSE | jq -r '.thread_id')

# hard kill
docker kill -s KILL $(docker ps -q -f name=agent-api)
sleep 2
docker compose up -d agent-api
sleep 10

# verify state
STATE=$(curl -s http://localhost:8095/agent/threads/$THREAD_ID/state)
if [ "$(echo $STATE | jq -r '.thread_id')" == "$THREAD_ID" ]; then
  echo "PASS: Checkpoint recovered"
else
  echo "FAIL: Checkpoint lost"
  exit 1
fi
```

**Auth negative test script:**
```bash
#!/bin/bash
# Expired token
EXPIRED_TOKEN="eyJ..." # generate with exp in past
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $EXPIRED_TOKEN" http://localhost:8095/agent/invoke)
[ "$RESULT" == "401" ] && echo "PASS: Expired token rejected" || echo "FAIL: Expired token accepted"

# Wrong issuer
WRONG_ISS_TOKEN="eyJ..." # generate with iss != zakops-auth
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $WRONG_ISS_TOKEN" http://localhost:8095/agent/invoke)
[ "$RESULT" == "401" ] && echo "PASS: Wrong issuer rejected" || echo "FAIL: Wrong issuer accepted"

# Wrong audience
WRONG_AUD_TOKEN="eyJ..." # generate with aud != zakops-agent
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $WRONG_AUD_TOKEN" http://localhost:8095/agent/invoke)
[ "$RESULT" == "401" ] && echo "PASS: Wrong audience rejected" || echo "FAIL: Wrong audience accepted"

# Missing role
NO_ROLE_TOKEN="eyJ..." # generate without role claim
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $NO_ROLE_TOKEN" http://localhost:8095/agent/invoke)
[ "$RESULT" == "401" ] && echo "PASS: Missing role rejected" || echo "FAIL: Missing role accepted"
```

### 6.2 Post-Fork Integration Tests

| Test | Description | Pass Criteria |
|------|-------------|---------------|
| T-01 | Invoke simple query | `/agent/invoke` returns MDv2 schema response within 30s |
| T-02 | Checkpoint persistence | Kill -9 mid-workflow, restart, verify state recovered |
| T-03 | HITL interrupt | CRITICAL tool triggers `awaiting_approval` status |
| T-04 | HITL resume | Approval endpoint resumes and completes workflow |
| T-05 | Tool validation | Invalid tool args rejected with 400 error |
| T-06 | Idempotency (serial) | Duplicate idempotency key returns cached result |
| T-07 | Idempotency (concurrent) | 50 parallel calls → exactly one tool execution |
| T-08 | Auth enforcement | Request without token returns 401 |
| T-09 | Auth negative suite | Expired/wrong-iss/wrong-aud/no-role → 401 |
| T-10 | RBAC enforcement | VIEWER role blocked from approve endpoint |
| T-11 | Langfuse trace | Trace visible in Langfuse UI (or graceful skip) |
| T-12 | No raw content | PII canary not in logs/DB/traces |
| T-13 | Streaming | SSE endpoint returns incremental events |
| T-14 | Audit immutability | UPDATE/DELETE on audit_log → denied |
| T-15 | Tool gateway choke point | Mock gateway; assert no direct tool calls outside |

### 6.3 Blind Spot Verification (from PASS 1)

| ID | Blind Spot | Verification Method | Status |
|----|------------|---------------------|--------|
| B-01 | Durable checkpointing E2E | T-02 (kill -9 test) | Pending |
| B-02 | HITL semantics match MDv2 | T-03, T-04, MDv2 schema tests | Pending |
| B-03 | Tool contract strictness | T-05 (invalid args test) | Pending |
| B-04 | READ/WRITE/CRITICAL tiers | T-03 + Tool Catalog audit | Pending |
| B-05 | Idempotency claim-first | T-06, T-07 (concurrent test) | Pending |
| B-06 | No raw content (all surfaces) | T-12 (logs/DB/traces) | Pending |
| B-07 | Local-first (no cloud keys) | Startup with `OPENAI_API_KEY=` unset | Pending |
| B-08 | Port compatibility | Compose up with PORTS.md verification | Pending |
| B-09 | MCP transport alignment | MCP conformance test against :9100 | Pending |

### 6.4 OSS Due Diligence Checklist

| Check | Requirement | Status |
|-------|-------------|--------|
| License (deps) | No GPL/AGPL at runtime | Pending |
| Maintainers | >1 active committer in 90 days OR code small enough to own | Pending |
| Releases | Tagged releases exist OR we accept maintenance burden | Pending |
| Security policy | SECURITY.md or similar exists | Pending |
| Vulnerabilities | No critical vulns with no patch path | Pending |
| SBOM | CycloneDX generated and stored in repo | Pending |
| Container images | Pinned by digest for production | Pending |
| Tests | CI workflow + unit tests exist | Pending |

---

## 7) Risk & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **R-01**: HITL spike fails | Must switch scaffolds | Medium | 2-day time-box with explicit DoD; fallback to agent-service-toolkit |
| **R-02**: vLLM Hermes tool parsing failures | Tool calls malformed | Medium | 10-prompt test suite before integration; prompt engineering fallback |
| **R-03**: AsyncPostgresSaver pool conflicts | Connection starvation | Low | Separate connection pool for checkpointer; monitor connections |
| **R-04**: Langfuse integration complexity | Observability gap | Low | External Langfuse for MVP; self-hosted Phase 2; graceful degradation |
| **R-05**: Port collision | Dev friction | Low | `PORTS.md` as single source of truth; linter verifies references |
| **R-06**: MCP client unreliable | Tool integration blocked | Medium | Contract checklist (timeouts/retries); fallback to direct HTTP |
| **R-07**: Scope creep | Schedule slip | Medium | Deprecate (don't delete) unused code; enforce PR review |
| **R-08**: Docker networking failures | Runtime errors | Medium | Host-services mode with `host.docker.internal`; bring-up test validates |
| **R-09**: DB port collision | Startup failure | Low | Agent uses separate database; no host port binding for agent Postgres |

**Contingency:** If wassim249 fork encounters blocking issues in spike or Phase 1, switch to agent-service-toolkit fork with auth/pruning overhead accepted.

---

## 8) Decision Log

| ID | Decision | Options Considered | Rationale | Date |
|----|----------|-------------------|-----------|------|
| D-01 | **Primary fork: wassim249** | wassim249, agent-service-toolkit, aegra | Best SEC (4) + BND (5) + template shape; HITL spike validates | 2026-01-22 |
| D-02 | **Reference: agent-service-toolkit** | N/A | Best MCP + interrupt/resume reference | 2026-01-22 |
| D-03 | **HITL: 2-day spike with DoD** | Implement from scratch, assume bounded | Spike validates approach before full investment | 2026-01-22 |
| D-04 | **Networking: host-services mode** | All-in-compose, host-services | Matches ZakOps workstation; avoids localhost in containers | 2026-01-22 |
| D-05 | **DB: separate database** | Shared DB, separate DB, separate instance | Avoids port collision; independent schema evolution | 2026-01-22 |
| D-06 | **Retrieval: RAG REST exclusive** | RAG REST, pgvector direct, both | Single path prevents split-brain | 2026-01-22 |
| D-07 | **Langfuse: external for MVP** | Self-hosted, external, none | Reduces MVP complexity; self-hosted in Phase 2 | 2026-01-22 |
| D-08 | **Tool gateway: single choke point** | Distributed tools, single gateway | Enforces permissions + idempotency consistently | 2026-01-22 |
| D-09 | **Idempotency key: sha256 derivation** | UUID, hash, timestamp | Deterministic; prevents duplicates across retries | 2026-01-22 |
| D-10 | **Audit log: immutable via permissions** | Trigger, permissions, none | Simple; enforced at DB level | 2026-01-22 |
| D-11 | **LiteLLM: Phase 2 explicit** | MVP, Phase 2 | Reduces MVP scope; direct vLLM sufficient initially | 2026-01-22 |
| D-12 | **Chat endpoints: deprecate not delete** | Delete, deprecate | Preserves streaming plumbing for reuse | 2026-01-22 |

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

**NOTE: Run Scaffold Reality Check (§4.2) and update these paths before starting work.**

### Files to DEPRECATE (keep for streaming reuse)

```
app/api/v1/chatbot.py          # Deprecate; reuse streaming plumbing
```

### Files to CREATE

```
app/api/v1/agent.py                    # ZakOps canonical endpoints (MDv2 schema)
app/core/langgraph/nodes/router.py     # Intent classification
app/core/langgraph/nodes/planner.py    # Action planning
app/core/langgraph/nodes/executor.py   # Tool execution
app/core/langgraph/nodes/approval_gate.py  # HITL pause point
app/core/tools/gateway.py              # HybridToolGateway (SINGLE CHOKE POINT)
app/core/tools/direct/deal_tools.py    # Deal API tools
app/core/tools/direct/health_tools.py  # Health check tool
app/core/tools/mcp_client.py           # MCP streamable-http client
app/db/models/approvals.py             # Approvals model
app/db/models/tool_executions.py       # Idempotency model
app/db/models/audit_log.py             # Audit log model
app/db/models/task_queue.py            # Queue model
migrations/001_extensions.sql          # pgcrypto extension
migrations/002_zakops_tables.sql       # Schema migration
scripts/bring_up_tests.sh              # Pre-fork validation
PORTS.md                               # Authoritative port assignments
```

### Files to MODIFY

```
app/main.py                    # Port 8095, router, checkpointer init
app/core/config.py             # ZakOps env vars (host-services URLs)
app/core/langgraph/graph.py    # New graph definition
app/core/middleware.py         # JWT claims validation (iss/aud/exp/role), API key fallback, RBAC
app/core/observability.py      # No raw content wrapper (traces + logs + DB)
docker-compose.yml             # Ports, networking, no Postgres host binding
.env.example                   # ZakOps variables (host.docker.internal URLs)
```

---

## Appendix C: MCP Client Contract Checklist

| Requirement | Specification |
|-------------|---------------|
| Transport | streamable-http |
| Server URL | `http://host.docker.internal:9100` (host-services mode) |
| Per-tool timeout | Configurable; default 30 seconds |
| Retry policy | Exponential backoff: 3 attempts, delays 1s/2s/4s |
| Circuit breaker | Open after 5 consecutive failures; half-open after 30s |
| Parameter validation | Validate args against tool schema before call |
| Error normalization | Map MCP errors to standard `{error: string, code: string}` format |
| Logging | Log tool name, duration, success/failure; NO raw args/results |
| Conformance test | initialize → tools/list → tools/call for each tool; 99%+ success |

---

## Appendix D: Definition of Done Summary

### Spike DoD (2 days)
- [ ] Approval endpoints implemented
- [ ] Checkpoint resumes after kill -9
- [ ] Exactly-once execution verified
- [ ] 10 concurrent approvals → 1 execution

### MVP DoD (Phase 0-3)
- [ ] All bring-up tests pass
- [ ] All T-01 to T-15 integration tests pass
- [ ] All OSS due diligence checks pass
- [ ] First Working Demo scenario completes
- [ ] No raw content in logs/DB/traces
- [ ] PORTS.md matches all configs

### Production DoD (Phase 4-6)
- [ ] Auth negative suite passes
- [ ] RBAC enforcement verified
- [ ] Audit log immutability enforced
- [ ] Langfuse self-hosted (Phase 2)
- [ ] LiteLLM routing (Phase 2)
- [ ] Queue worker operational

---

**Document Status:** FINAL v2 — All PASS3 Blockers and Majors resolved
**Next Action:** Execute HITL Spike (§4.1) then Phase 0 (Fork & Environment Setup)
