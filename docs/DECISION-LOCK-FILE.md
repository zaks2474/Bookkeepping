# ZakOps Agent — Decision Lock File

**Source:** ZakOps-Ultimate-Master-Document-v2.md (v2.1.0)
**Date:** 2026-01-22
**Status:** LOCKED FOR IMPLEMENTATION

---

## Quick Reference

| Category | Decision | Port/Version |
|----------|----------|--------------|
| Model | Qwen2.5-32B-Instruct-AWQ | — |
| Inference | vLLM | :8000 |
| Orchestration | LangGraph + PostgresSaver | — |
| Agent API | FastAPI | :8095 |
| Deal API | (existing) | :8090 |
| Vector DB | pgvector → Qdrant (Ph3) | :5432 |
| Embeddings | BGE-M3 (1024-dim) | — |
| Queue | Postgres SKIP LOCKED | :5432 |
| Tracing | Langfuse (self-hosted) | :3001 |
| Routing | LiteLLM (deterministic) | — |
| Tools | Hybrid MCP + Direct | :9100 |
| Auth | RBAC → ABAC (Ph3) | — |
| Secrets | Env vars → Vault (Ph3) | — |

---

## 1. Model Serving

| Attribute | Value |
|-----------|-------|
| **Choice** | Qwen2.5-32B-Instruct-AWQ |
| **Over** | Qwen3-32B, Llama-3.3-70B |
| **Engine** | vLLM with `--tool-call-parser hermes` |
| **Quantization** | AWQ |
| **Context** | 32,768 tokens max |
| **GPU Util** | 0.90 |

**Constraints:**
- Single RTX 5090 (32GB VRAM)
- Must support OpenAI-compatible API
- Must handle Hermes tool-calling format

**Definition of Done:**
- [ ] vLLM serves model at measurable tok/s
- [ ] `curl localhost:8000/health` returns 200
- [ ] Tool-calling works on 5 sample prompts

**Upgrade Trigger:** Qwen3-32B if ≥5% accuracy improvement on 50-prompt eval

---

## 2. Orchestration

| Attribute | Value |
|-----------|-------|
| **Choice** | LangGraph |
| **Over** | AutoGen, Temporal |
| **Checkpointing** | PostgresSaver |
| **HITL Pattern** | `interrupt_before=["approval_gate"]` |

**Constraints:**
- Must persist state across crashes
- Must support pause/resume for approvals
- Max 10 iterations per workflow

**Definition of Done:**
- [ ] Workflow completes simple query end-to-end
- [ ] State persists across process restart (kill -9 test)
- [ ] Approval gate pauses workflow correctly
- [ ] `POST /agent/approvals/{id}:approve` resumes workflow

---

## 3. Tool Pattern

| Attribute | Value |
|-----------|-------|
| **Choice** | Hybrid MCP + Direct |
| **Direct Tools** | list_deals, get_deal, transition_deal, check_health |
| **MCP Tools** | External APIs, future tools |
| **MCP Server** | :9100 (streamable-http) |

**Constraints:**
- 3-tier permissions: READ / WRITE / CRITICAL
- Idempotency required for all WRITE/CRITICAL tools
- Idempotency pattern: claim-first (INSERT before execute)
- Pydantic validation on all tool calls

**Definition of Done:**
- [ ] Tool validation rejects invalid params
- [ ] Idempotency key prevents duplicate execution
- [ ] CRITICAL tools require approval
- [ ] Tool calls logged to audit_log table

---

## 4. Storage

| Attribute | Value |
|-----------|-------|
| **Choice** | PostgreSQL (pgvector extension) |
| **Over** | Qdrant (Phase 1), Redis |
| **Port** | 5432 |

**Tables:**
- `checkpoints` — LangGraph state
- `tool_executions` — Idempotency + audit
- `approvals` — HITL decisions
- `task_queue` — Async tasks (SKIP LOCKED)
- `audit_log` — Immutable event log
- `deal_embeddings` — Vector storage (1024-dim)

**Constraints:**
- No DELETE on audit_log
- TTL on checkpoints: 30 days
- Dead letter queue for failed tasks

**Definition of Done:**
- [ ] All tables created with indexes
- [ ] Checkpoint write/read round-trips successfully
- [ ] Queue claims work under concurrent load
- [ ] pgvector similarity search returns results

**Migration Trigger:** Qdrant if >1M vectors OR P95 retrieval >250ms

---

## 5. Tracing / Observability

| Attribute | Value |
|-----------|-------|
| **Choice** | Langfuse (self-hosted) + OpenTelemetry |
| **Over** | LangSmith (cloud) |
| **Port** | 3001 |

**Constraints:**
- NEVER log raw prompts/responses (hash + length only)
- 100% trace coverage for all workflows
- Retention: 30 days default

**Definition of Done:**
- [ ] Langfuse UI accessible at :3001
- [ ] Complete trace visible for test workflow
- [ ] No raw content in trace spans
- [ ] Prometheus metrics exposed

---

## 6. Queue System

| Attribute | Value |
|-----------|-------|
| **Choice** | PostgreSQL SKIP LOCKED |
| **Over** | Redis + Dramatiq |
| **Retry** | Exponential backoff (30s × 2^attempt) |
| **Max Attempts** | 3 |

**Constraints:**
- Dead letter after max attempts
- Queue depth warning: >50
- Queue depth critical: >100

**Definition of Done:**
- [ ] Worker claims tasks correctly
- [ ] Failed tasks retry with backoff
- [ ] Dead letter queue captures persistent failures
- [ ] P95 claim latency <100ms under load

**Migration Trigger:** Redis if P95 >500ms under 1000 concurrent tasks

---

## 7. Security / RBAC

| Attribute | Value |
|-----------|-------|
| **Choice** | RBAC (Phase 1) → ABAC (Phase 3) |
| **Over** | ABAC from start |
| **Auth** | JWT (primary) + API key (X-API-Key header) |

**Roles:**
- VIEWER: read
- OPERATOR: read, write
- APPROVER: read, write, approve
- ADMIN: read, write, approve, admin

**JWT Requirements:**
- Algorithm: HS256
- Required claims: sub, role, exp, iss, aud
- Issuer: `zakops-auth`
- Audience: `zakops-agent`

**Constraints:**
- Default-deny policy
- API keys stored as SHA256 hash
- Secrets via env vars (→ Vault Phase 3)

**Definition of Done:**
- [ ] JWT validation rejects expired/invalid tokens
- [ ] API key auth works as fallback
- [ ] Permission check blocks unauthorized actions
- [ ] All auth attempts logged

---

## 8. LLM Routing

| Attribute | Value |
|-----------|-------|
| **Choice** | LiteLLM gateway (deterministic) |
| **Over** | Random shuffle |
| **Strategy** | cost-based-routing |
| **Fallback Chain** | local-primary → cloud-claude |

**Cloud Egress Policy:**
- BLOCKED fields: ssn, tax_id, bank_account, credit_card
- ALLOWED conditions: context_overflow, local_model_error, explicit_user_request, complexity_threshold

**Constraints:**
- Daily budget: $50 max
- ≥80% tasks handled locally
- PII redaction before cloud send

**Definition of Done:**
- [ ] Local model handles simple queries
- [ ] Cloud fallback triggers on context overflow
- [ ] Blocked fields prevent cloud escalation
- [ ] Cost tracking dashboard shows spend

---

## 9. Embeddings / Retrieval

| Attribute | Value |
|-----------|-------|
| **Choice** | BGE-M3 |
| **Over** | text-embedding-3-small (cloud) |
| **Dimension** | 1024 |
| **Reranker** | BGE-reranker-large (optional) |

**Constraints:**
- Single retrieval path (no split-brain)
- Deal-scoped queries by default
- Reranker enabled only if MRR ≥10% uplift

**Definition of Done:**
- [ ] Embeddings stored in pgvector
- [ ] Similarity search returns relevant chunks
- [ ] recall@5 ≥ 0.8 on eval set
- [ ] Reranker latency <100ms additional

---

## 10. Service Boundaries

| Service | Port | Responsibilities |
|---------|------|------------------|
| **Deal API** | 8090 | CRUD, transitions (existing) |
| **Agent API** | 8095 | Orchestration, approvals, tools |
| **vLLM** | 8000 | Inference |
| **MCP** | 9100 | External tool server |
| **RAG REST** | 8052 | Retrieval frontend |
| **Langfuse** | 3001 | Trace UI |
| **Cloudflare** | — | Routes to :8095 (NOT :8090) |

---

## Checklist Summary

### Phase 1 (MVP)
- [ ] vLLM serves Qwen2.5-32B
- [ ] LangGraph workflow E2E
- [ ] State persists across restart
- [ ] Tool calls validated + logged
- [ ] Langfuse trace visible
- [ ] Health checks pass 24h

### Phase 2 (Hardening)
- [ ] Tool accuracy ≥95%
- [ ] HITL approval workflow works
- [ ] Queue load tested
- [ ] Health checks pass 72h
- [ ] Crash recovery verified (chaos test)

### Phase 3 (Advanced)
- [ ] Retrieval recall@5 ≥80%
- [ ] ≥80% tasks local
- [ ] Cost dashboard operational
- [ ] ABAC policies enforced

---

## Migration Triggers

| Component | Current | Migrate To | Trigger |
|-----------|---------|------------|---------|
| Vector DB | pgvector | Qdrant | >1M vectors OR P95 >250ms |
| Queue | Postgres | Redis+Dramatiq | P95 claim >500ms |
| Model | Qwen2.5-32B | Qwen3-32B | ≥5% accuracy improvement |
| Reranker | Disabled | Enabled | MRR ≥10% uplift |
| Auth | RBAC | ABAC | Phase 3 complexity |
| Secrets | Env vars | Vault | Phase 3 |

---

*Lock file extracted from Master Document v2.1.0*
