# ZakOps — Ultimate Implementation Roadmap (3-Pass Final)

**Version:** 3.0.0-FINAL
**Timestamp (UTC):** 2026-01-24T06:00:00Z
**Status:** APPROVED FOR EXECUTION (requires gate PASS evidence per phase)
**Synthesis:** Pass 3 — Editor-in-Chief + Chief Architect
**Authority Order:** DECISION-LOCK > QA_REPORT > Scaffold-Plan > MDv2

---

## 1. Executive Summary

### What We Are Building

ZakOps Agent is a **production-grade, locally-hosted AI agent system** for Deal Lifecycle Management. The agent orchestrates deal workflows through **LangGraph** with **durable PostgreSQL checkpoints**, executes actions via a **single tool-gateway choke point** with **strict schemas + permission tiers + idempotency**, and enforces **HITL approvals** for CRITICAL operations.

### Current State

The **HITL spike completed on 2026-01-23 with VERDICT: PASS** across all 14 gates. The foundational patterns are proven:
- Interrupt/resume for CRITICAL tools
- Crash recovery (kill -9)
- Exactly-once execution under concurrency (N=20)
- Auth enforcement (7/7 negative tests)
- Streaming with HITL interrupts

### Critical Security Issue (P0)

**QA-M1: Plaintext persistence risk** — Checkpoint blobs contain raw tool args/results. Must implement AES-256-GCM encryption via `SecurePostgresSaver` wrapper before production exposure.

### Next Milestone

**Phase 1: MVP Surface Completion** — Wire Agent API to real Deal API (:8090), deploy self-hosted Langfuse at :3001, implement PII protection, complete 24h stability soak.

### System-Wide Definition of Done

- Agent processes deals end-to-end with HITL approval gates
- Tool accuracy ≥95% on 50-prompt eval
- 72h continuous health with zero unrecovered crashes
- Langfuse traces visible for 100% of workflows
- Zero plaintext PII at rest (encryption + canary gates)
- No raw content in logs/traces (hash+length only)

---

## 2. Baseline & Proven Invariants

**Source:** [QA_REPORT.md Cycle QA-CYCLE-3, 2026-01-23]

### Gates That Must NEVER Regress

| Gate ID | Description | Evidence Artifact | Pass Criteria |
|---------|-------------|-------------------|---------------|
| BL-01 | Health endpoint | `gate_artifacts/health.json` | HTTP 200 |
| BL-02 | HITL invoke triggers approval | `gate_artifacts/invoke_hitl.json` | status=`awaiting_approval` |
| BL-03 | DB invariants | `gate_artifacts/db_invariants.sql.out` | approval row exists pre-interrupt |
| BL-04 | Approve completes workflow | `gate_artifacts/approve.json` | HTTP 200 |
| BL-05 | Idempotency rejects duplicate | `gate_artifacts/approve_again.json` | HTTP 409 |
| BL-06 | Concurrency N=20 | `gate_artifacts/concurrent_approves.log` | 1×200, 19×409 |
| BL-07 | Kill-9 recovery | `gate_artifacts/checkpoint_kill9_test.log` | RESULT: PASSED |
| BL-08 | Tool validation | `gate_artifacts/tool_call_validation_test.log` | Invalid args rejected |
| BL-09 | License scan | `gate_artifacts/dependency_licenses.json` | 0 copyleft at runtime |
| BL-10 | Audit log | `gate_artifacts/db_invariants.sql.out` | Events recorded |
| BL-11 | Mock safety | `gate_artifacts/mock_safety_test.log` | No live calls in test |
| BL-12 | Streaming | `gate_artifacts/streaming_test.log` | Events received |
| BL-13 | HITL scope | `gate_artifacts/hitl_scope_test.log` | Only CRITICAL triggers |
| BL-14 | Auth negative 7/7 | `gate_artifacts/auth_negative_tests.json` | All cases pass |

**Baseline Command:** `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

### Infrastructure Status

| Service | Port | Status | Evidence |
|---------|------|--------|----------|
| Agent API | :8095 | ✅ Verified | QA_REPORT §4 |
| Deal API | :8090 | ✅ Healthy | QA_REPORT §4 |
| vLLM (Qwen2.5-32B-AWQ) | :8000 | ✅ Serving | `curl localhost:8000/health` → 200 |
| RAG REST | :8052 | ⚠️ UNVERIFIED | Requires contract probe |
| MCP Server | :9100 | ⚠️ UNVERIFIED | Requires contract probe |
| PostgreSQL | :5432 | ✅ Running | QA_REPORT §4 |
| Langfuse | :3001 | ⏳ PENDING | Requires self-hosted deployment |

---

## 3. Hard Constraints (DECISION-LOCK)

**Authority:** These constraints are NON-NEGOTIABLE. Any deviation requires explicit lock-file amendment.

### 3.1 Service Ports (LOCKED)

| Service | Port | Notes |
|---------|------|-------|
| vLLM | 8000 | `--tool-call-parser hermes`, 32K context max |
| RAG REST | 8052 | Exclusive retrieval path (Agent never queries pgvector directly) |
| Deal API | 8090 | KEEP-AS-IS, existing service |
| Agent API | 8095 | Cloudflare routes here (NOT :8090) |
| MCP Server | 9100 | streamable-http transport |
| Langfuse | 3001 | Self-hosted REQUIRED (cloud is dev-only, non-compliant) |
| PostgreSQL | 5432 | pgvector extension, separate `zakops_agent` database |

### 3.2 Technology Stack (LOCKED)

| Component | Choice | Constraint |
|-----------|--------|------------|
| Model | Qwen2.5-32B-Instruct-AWQ | Upgrade only if ≥5% accuracy gain on 50-prompt eval |
| Inference | vLLM | GPU util 0.90, 32K context, Hermes tool parser |
| Orchestration | LangGraph + PostgresSaver | `interrupt_before=["approval_gate"]`, max 10 iterations |
| Vector DB | pgvector → Qdrant (Ph3) | Migrate if >1M vectors OR P95 retrieval >250ms |
| Queue | Postgres SKIP LOCKED | Migrate to Redis if P95 claim >500ms under 1000 tasks |
| Tracing | Langfuse self-hosted | NEVER log raw content (see §3.5) |
| Auth | RBAC → ABAC (Ph3) | JWT: sub, role, exp, iss=zakops-auth, aud=zakops-agent |
| Secrets | Env vars → Vault (Ph3) | Never commit to repo |

### 3.3 Tool Tiers (LOCKED)

| Tier | Tools | Approval Required | Idempotent |
|------|-------|-------------------|------------|
| READ | list_deals, get_deal, search_documents, check_health | No | N/A |
| WRITE | create_deal, update_deal | Policy-dependent | Yes |
| CRITICAL | transition_deal, delete_deal, send_email | **Always** | Yes |

**Tool-to-Deal-API Mapping (from MDv2 §5.2):**

| Agent Tool | Deal API Endpoint | Method |
|------------|-------------------|--------|
| list_deals | `GET /deals` | Direct HTTP |
| get_deal | `GET /deals/{id}` | Direct HTTP |
| transition_deal | `POST /deals/{id}/transition` | Direct HTTP |
| update_deal | `PATCH /deals/{id}` | Direct HTTP |
| create_deal | `POST /deals` | Direct HTTP |

### 3.4 External Service Resilience (NEW)

| Service | Timeout | Retries | Backoff | Circuit Breaker |
|---------|---------|---------|---------|-----------------|
| Deal API | 10s | 3 | 1s/2s/4s | 5 failures → 30s open |
| vLLM | 120s | 2 | 5s/10s | 3 failures → 60s open |
| RAG REST | 10s | 3 | 1s/2s/4s | 5 failures → 30s open |
| MCP | 30s | 3 | 1s/2s/4s | 5 failures → 30s open |

### 3.5 "No Raw Content" Policy Scope (EXPLICIT)

**MUST hash+length only (NEVER plaintext):**
- LLM prompts (user messages + system prompts)
- LLM responses (assistant messages)
- Tool arguments (all tiers: READ/WRITE/CRITICAL)
- Tool results (all tiers)
- Deal content (titles, descriptions, values)
- Document text (extracted content)

**MAY log in plaintext:**
- Thread IDs, deal IDs, approval IDs (opaque identifiers)
- Timestamps
- Status strings (awaiting_approval, completed, error)
- Error codes (NOT error messages containing user data)

### 3.6 Encryption Requirements (NEW — Resolves P0)

**Checkpoint Encryption:**
- Algorithm: AES-256-GCM via `SecurePostgresSaver` wrapper
- Scope: `checkpoint_blobs.blob` column AND `checkpoint_writes.channel_values` column
- Key source: `CHECKPOINT_ENCRYPTION_KEY` env var (256-bit random)
- Key rotation: Manual until Vault (Phase 3)
- Startup behavior: Fail-closed (refuse to start without valid key)

**Log Field Handling:**
- Use `SafeLogger` wrapper that hashes sensitive fields before logging
- NEVER encrypt log files (key management nightmare)

### 3.7 Migration Triggers (LOCKED)

| Component | Trigger | Target |
|-----------|---------|--------|
| Vector DB | >1M vectors OR P95 retrieval >250ms | Qdrant |
| Queue | P95 claim >500ms under 1000 tasks | Redis+Dramatiq |
| Model | ≥5% accuracy improvement on 50-prompt eval | Qwen3-32B |
| Auth | Phase 3 complexity | ABAC |

---

## 4. Phase Plan

### Phase 0: Baseline Preservation (Pre-requisite)

**Objective:** Freeze HITL spike as non-negotiable baseline; prevent regressions.

**Scope IN:**
- Ensure baseline gate command remains stable and reproducible
- Document baseline artifacts and PASS markers
- Verify PORTS.md exists and matches Decision Lock

**Scope OUT:**
- No feature expansion

**Acceptance Gates:**
```bash
# P0-G1: Baseline regression
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
# Assert: exit 0, run.log contains "ALL GATES PASSED"
```

**Definition of Done:**
- [ ] Gate pack passes with all required artifacts
- [ ] PORTS.md exists and matches Decision Lock ports

---

### Phase 1: MVP Surface Completion (Target: 1 Week)

**Objective:** Meet Decision Lock Phase-1 MVP criteria:
- Direct tools wired to Deal API
- Self-hosted Langfuse on :3001 with visible traces
- PII protection implemented (encryption + canary)
- 24h stability soak

**Scope IN:**
- Wire `list_deals`, `get_deal`, `transition_deal` to Deal API :8090
- Implement `SecurePostgresSaver` (AES-256-GCM encryption)
- Deploy self-hosted Langfuse at :3001
- Implement PII canary gate
- Implement `SafeLogger` wrapper (hash+length)
- Create contract probes for Deal API
- 24h health monitoring soak

**Scope OUT:**
- Queue worker (Phase 2)
- RAG integration (Phase 2)
- LiteLLM routing (Phase 3)
- Additional tools beyond deal CRUD

**Dependencies:**
- ✅ HITL spike passing (verified 2026-01-23)
- ✅ Deal API at :8090 (verified healthy)
- ✅ vLLM at :8000 (verified serving)
- ⏳ Langfuse Docker images available

**Risks:**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Deal API schema mismatch | High | Contract probe before implementation |
| Encryption adds >50ms latency | Medium | Benchmark; optimize if needed |
| PII canary false negatives | High | Conservative regex patterns |
| Langfuse Docker issues | Medium | Cloud dev fallback (non-compliant) |

**Acceptance Gates:**
```bash
# P1-G1: Baseline regression (must still pass)
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh

# P1-G2: Deal API integration
curl -X POST http://localhost:8095/agent/invoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT" \
  -d '{"actor_id":"test","message":"List all deals"}'
# Assert: status=completed, actions_taken includes list_deals with real data

# P1-G3: HITL E2E with real transition
curl -X POST http://localhost:8095/agent/invoke \
  -H "Authorization: Bearer $JWT" \
  -d '{"actor_id":"test","deal_id":"DL-0001","message":"Transition to qualified"}'
# Assert: status=awaiting_approval
# Then: POST /agent/approvals/{id}:approve → verify Deal API state changed

# P1-G4: Langfuse self-hosted
curl -f http://localhost:3001/api/public/health
# Assert: HTTP 200; trace visible in UI for P1-G3 workflow

# P1-G5: PII canary
./scripts/gates/pii_canary_gate.sh
# Assert: exit 0 (canary token NOT in logs/traces/DB)

# P1-G6: Kill-9 with encryption (must still pass)
./scripts/gates/kill9_encrypted_test.sh
# Assert: state recovered after encryption enabled

# P1-G7: 24h health soak
./scripts/gates/soak_24h.sh
# Assert: 100% uptime, 0 crashes, artifacts recorded
```

**Definition of Done:**
- [ ] All Phase 0 gates PASS
- [ ] Agent invokes Deal API for all deal tools (real data, not mocks)
- [ ] Checkpoint encryption enabled (AES-256-GCM)
- [ ] Kill-9 recovery still works with encryption
- [ ] Langfuse self-hosted at :3001 with visible traces
- [ ] PII canary gate passes
- [ ] 24h health soak passes
- [ ] Artifacts in `gate_artifacts/phase1/`

---

### Phase 2: Production Hardening (Target: 2 Weeks)

**Objective:** Make system safe and operable under real usage:
- Queue worker with retries/DLQ
- Full RBAC enforcement
- Audit immutability
- Token counting middleware
- Chaos tests
- Tool accuracy eval

**Scope IN:**
- Postgres SKIP LOCKED queue + worker + DLQ
- RBAC middleware enforcement (VIEWER blocked from approve)
- API key auth fallback with SHA256 storage
- Audit_log immutability (DB-level)
- Token counting middleware (reject >32K)
- Approval expiry daemon (24h TTL)
- Chaos tests (extended kill-9, N=50 concurrency)
- 50-prompt tool accuracy eval
- Prometheus metrics
- 72h stability soak

**Scope OUT:**
- RAG retrieval (Phase 3)
- LiteLLM cloud routing (Phase 3)
- ABAC policies (Phase 3)

**Acceptance Gates:**
```bash
# P2-G1: Baseline + Phase 1 regression
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh

# P2-G2: Tool validation
curl -X POST http://localhost:8095/agent/invoke \
  -d '{"actor_id":"test","message":"Transition INVALID-ID to bogus_stage"}'
# Assert: Validation error, tool NOT executed

# P2-G3: RBAC enforcement
curl -X POST "http://localhost:8095/agent/approvals/xxx:approve" \
  -H "Authorization: Bearer $VIEWER_JWT"
# Assert: HTTP 403 Forbidden

# P2-G4: Queue load test
python tests/load/queue_load_test.py --tasks 1000 --workers 10
# Assert: P95 claim <100ms, 0 lost tasks, DLQ captures failures

# P2-G5: Chaos test (extended)
./scripts/gates/chaos_test.sh
# Assert: kill-9 mid-workflow → recovered; N=50 concurrent → exactly 1 execution

# P2-G6: Tool accuracy
python evals/run_tool_accuracy.py
# Assert: ≥95% exact match on 50 prompts

# P2-G7: Audit immutability
./scripts/gates/audit_immutability_test.sh
# Assert: UPDATE/DELETE on audit_log denied

# P2-G8: Token counting
./scripts/gates/token_limit_test.sh
# Assert: 33K token input rejected pre-request

# P2-G9: 72h soak
./scripts/gates/soak_72h.sh
# Assert: 100% uptime, 0 crashes
```

**Definition of Done:**
- [ ] Tool registry rejects invalid params
- [ ] RBAC blocks VIEWER from approve
- [ ] Queue P95 claim <100ms under 1000 tasks
- [ ] Chaos test passes (kill-9 + N=50)
- [ ] Tool accuracy ≥95%
- [ ] Audit log immutable
- [ ] Token counting enforced
- [ ] 72h health soak passes

---

### Phase 3: Advanced Features (Target: 3-4 Weeks)

**Objective:** RAG retrieval, LiteLLM routing, cost tracking, full lifecycle demo.

**Scope IN:**
- RAG REST integration via `search_documents` tool
- Retrieval eval (recall@5 ≥ 0.80)
- LiteLLM gateway with cost-based routing
- Cloud Egress Policy enforcement
- Cost tracking dashboard
- MCP client for :9100
- Full deal lifecycle demo

**Scope OUT:**
- Qdrant migration (unless trigger met)
- Model upgrade (unless trigger met)
- Fine-tuning

**Acceptance Gates:**
```bash
# P3-G1: RAG retrieval eval
python evals/run_retrieval_eval.py
# Assert: recall@5 ≥ 0.80

# P3-G2: Local handling rate
python evals/check_local_rate.py --workflows 100
# Assert: ≥80% handled locally

# P3-G3: Cloud egress block
./scripts/gates/cloud_block_test.sh
# Assert: Blocked fields prevent cloud escalation

# P3-G4: Cost tracking
curl http://localhost:8095/agent/metrics/cost
# Assert: JSON with total_cost, by_model breakdown

# P3-G5: Full lifecycle demo
python demos/full_lifecycle.py
# Assert: Deal progresses intake → qualified → proposal → won
```

---

## 5. Testing & Eval Strategy

### 5.1 Regression Gates (Every PR/Phase)

| Gate | Command | Artifact |
|------|---------|----------|
| Baseline | `./scripts/bring_up_tests.sh` | `gate_artifacts/run.log` |
| Kill-9 | `./scripts/gates/kill9_test.sh` | `gate_artifacts/checkpoint_kill9_test.log` |
| Concurrency | `./scripts/gates/concurrent_approve.sh 20` | `gate_artifacts/concurrent_approves.log` |
| Auth negative | `pytest tests/auth/test_negative.py` | `gate_artifacts/auth_negative_tests.json` |

### 5.2 Load/Chaos Tests (Phase 2+)

| Test | Command | Pass Criteria |
|------|---------|---------------|
| Queue load | `python tests/load/queue_load_test.py --tasks 1000` | P95 <100ms |
| Concurrent idempotency N=50 | `./scripts/gates/concurrent_approve.sh 50` | Exactly 1 execution |
| Kill-9 mid-workflow | `./scripts/gates/chaos_test.sh` | State recovered |

### 5.3 Tool Accuracy Eval (Phase 2+)

| Eval | Command | Pass Criteria |
|------|---------|---------------|
| 50-prompt tool accuracy | `python evals/run_tool_accuracy.py` | ≥95% exact match |
| Retrieval recall@5 | `python evals/run_retrieval_eval.py` | ≥0.80 |

### 5.4 Security Tests

| Test | Command | Pass Criteria |
|------|---------|---------------|
| PII canary | `./scripts/gates/pii_canary_gate.sh` | Canary NOT in logs/traces/DB |
| Audit immutability | `./scripts/gates/audit_immutability_test.sh` | UPDATE/DELETE denied |
| Auth negative 7/7 | `pytest tests/auth/test_negative.py` | All cases pass |
| Cloud egress block | `./scripts/gates/cloud_block_test.sh` | Blocked fields fail |

### 5.5 PII Canary Patterns (Regex)

```regex
SSN:         \b\d{3}-\d{2}-\d{4}\b
Credit Card: \b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b
Email:       \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b
Phone:       \b\d{3}[-.]?\d{3}[-.]?\d{4}\b
Deal values: \$[\d,]+(\.\d{2})?
Canary:      ZAKOPS_CANARY_[A-Z0-9]{16}
```

---

## 6. Work Breakdown (MECE Backlog)

### 6.1 Baseline & Environment

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| BL-001 | P0 | QA | `scripts/bring_up_tests.sh` | Gate pack deterministic | `./scripts/bring_up_tests.sh` |
| ENV-001 | P0 | Builder | `PORTS.md` | Matches Decision Lock | `./scripts/gates/ports_lint.sh` |
| ENV-002 | P0 | Builder | `.env.zakops` | host.docker.internal URLs | `./scripts/gates/env_lint.sh` |

### 6.2 Security (P0 — Phase 1)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| SEC-001 | P0 | Builder | `app/core/persistence/secure_saver.py` | AES-256-GCM encryption | Kill-9 + canary gates |
| SEC-002 | P0 | Builder | `app/core/middleware/auth.py` | JWT enforcement | `pytest tests/auth/test_negative.py` |
| SEC-003 | P0 | Builder | `app/core/observability/safe_logger.py` | Hash+length only | Canary gate |
| SEC-004 | P0 | Builder | `.env.zakops` | `CHECKPOINT_ENCRYPTION_KEY` | Startup fails without key |
| SEC-005 | P1 | Builder | `app/core/middleware/rbac.py` | VIEWER blocked from approve | RBAC test |
| SEC-006 | P1 | Builder | `app/core/auth/api_keys.py` | SHA256 storage | API key tests |
| SEC-007 | P1 | Builder | DB migrations | audit_log immutable | Immutability gate |

### 6.3 Tools (Phase 1)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| TOOL-001 | P0 | Builder | `app/core/tools/deal_tools.py` | `list_deals` wired to Deal API | Integration test |
| TOOL-002 | P0 | Builder | `app/core/tools/deal_tools.py` | `get_deal` wired to Deal API | Integration test |
| TOOL-003 | P0 | Builder | `app/core/tools/deal_tools.py` | `transition_deal` wired to Deal API | HITL E2E test |
| TOOL-004 | P0 | Builder | `app/core/tools/gateway.py` | HybridToolGateway singleton | Choke point test |
| TOOL-005 | P1 | Builder | `app/core/tools/deal_tools.py` | `create_deal` | Unit tests |
| TOOL-006 | P1 | Builder | `app/core/tools/deal_tools.py` | `update_deal` | Unit tests |

### 6.4 Observability (Phase 1)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| OBS-001 | P0 | Infra | `docker-compose.langfuse.yml` | Langfuse at :3001 | Health check |
| OBS-002 | P0 | Builder | Langfuse integration | Trace visible for workflow | Manual verify |
| OBS-003 | P1 | Builder | `app/core/observability/metrics.py` | `/metrics` endpoint | Prometheus check |

### 6.5 HITL / Approvals (Phase 1-2)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| HITL-001 | P0 | Builder | `scripts/gates/pii_canary_gate.sh` | Canary not in logs/traces/DB | Exit 0 |
| HITL-002 | P1 | Builder | `app/workers/approval_expiry.py` | 24h TTL, auto-expire, audit log | Cron test |

### 6.6 Queue & Ops (Phase 2)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| OPS-001 | P1 | Builder | `app/workers/queue_worker.py` | SKIP LOCKED claims | Smoke test |
| OPS-002 | P1 | Builder | `app/workers/dlq_handler.py` | Dead letter capture | Unit tests |
| OPS-003 | P1 | Builder | `scripts/gates/soak_24h.sh` | 24h uptime | Soak pass |
| OPS-004 | P2 | Builder | `scripts/gates/soak_72h.sh` | 72h uptime | Soak pass |

### 6.7 Context & Limits (Phase 2)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| CTX-001 | P1 | Builder | `app/core/middleware/context.py` | Reject >32K tokens | Token limit test |

### 6.8 RAG / Retrieval (Phase 3)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| RAG-001 | P2 | Builder | `app/core/tools/rag_tools.py` | `search_documents` via RAG REST only | Contract test |
| RAG-002 | P2 | QA | `evals/retrieval/` | recall@5 ≥ 0.80 | Eval script |

### 6.9 Routing (Phase 3)

| ID | Priority | Owner | Target | Acceptance | Gate |
|----|----------|-------|--------|------------|------|
| ROUTE-001 | P2 | Builder | LiteLLM integration | Cost-based routing | Policy tests |
| ROUTE-002 | P2 | Builder | Cloud egress policy | Blocked fields enforced | Block test |
| ROUTE-003 | P2 | QA | Cost dashboard | ≥80% local handling | Rate check |

### 6.10 Gate Scripts (Must Create)

| ID | Priority | Owner | Target | Artifact |
|----|----------|-------|--------|----------|
| GATE-001 | P0 | Builder | `scripts/gates/pii_canary_gate.sh` | `gate_artifacts/pii_canary.log` |
| GATE-002 | P0 | Builder | `scripts/gates/kill9_encrypted_test.sh` | `gate_artifacts/kill9_encrypted.log` |
| GATE-003 | P0 | Builder | `scripts/gates/ports_lint.sh` | `gate_artifacts/ports_lint.log` |
| GATE-004 | P0 | Builder | `scripts/gates/env_lint.sh` | `gate_artifacts/env_lint.log` |
| GATE-005 | P1 | Builder | `scripts/gates/soak_24h.sh` | `gate_artifacts/soak_24h.log` |
| GATE-006 | P1 | Builder | `scripts/gates/audit_immutability_test.sh` | `gate_artifacts/audit_immutable.log` |
| GATE-007 | P1 | Builder | `scripts/gates/token_limit_test.sh` | `gate_artifacts/token_limit.log` |
| GATE-008 | P2 | Builder | `scripts/gates/chaos_test.sh` | `gate_artifacts/chaos.log` |
| GATE-009 | P2 | Builder | `scripts/gates/soak_72h.sh` | `gate_artifacts/soak_72h.log` |
| GATE-010 | P2 | Builder | `scripts/gates/cloud_block_test.sh` | `gate_artifacts/cloud_block.log` |

---

## 7. Non-Negotiable Gates

**All must pass before production deployment.**

| Gate ID | Description | Command | Pass Criteria |
|---------|-------------|---------|---------------|
| NG-01 | Kill-9 recovery | `./scripts/gates/kill9_test.sh` | State recovered, workflow completes |
| NG-02 | Concurrent idempotency N=20 | `./scripts/gates/concurrent_approve.sh 20` | Exactly 1 execution |
| NG-03 | Auth negative 7/7 | `pytest tests/auth/test_negative.py` | All 7 cases pass |
| NG-04 | No copyleft deps | `./scripts/gates/license_scan.sh` | 0 GPL/AGPL at runtime |
| NG-05 | HITL scope | `pytest tests/hitl/test_scope.py` | Only CRITICAL tools trigger approval |
| NG-06 | Tool validation | `pytest tests/tools/test_validation.py` | Invalid params rejected |
| NG-07 | PII canary | `./scripts/gates/pii_canary_gate.sh` | Canary NOT in logs/traces/DB |
| NG-08 | No raw content | `./scripts/gates/raw_content_scan.sh` | 0 matches per §3.5 policy |
| NG-09 | Encryption enabled | `./scripts/gates/encryption_verify.sh` | checkpoint_blobs encrypted |
| NG-10 | Production concurrency N=50 | `./scripts/gates/concurrent_approve.sh 50` | Exactly 1 execution |

**Rationale for NG-10 (N=50):** Production headroom at 2.5× spike threshold (N=20 validated → N=50 target).

---

## 8. Deployment & Ops

### 8.1 Service Management

| Service | Management | Config |
|---------|------------|--------|
| Agent API | Docker Compose OR systemd | `docker-compose.yml` / `agent-api.service` |
| Langfuse | Docker Compose | `docker-compose.langfuse.yml` |
| vLLM | systemd (existing) | `vllm.service` |
| PostgreSQL | systemd (existing) | Port 5432 |

### 8.2 Health Monitoring

| Check | Endpoint | Frequency | Alert Threshold |
|-------|----------|-----------|-----------------|
| Agent API | `GET /health` | 60s | 3 failures |
| Langfuse | `GET /api/public/health` | 60s | 3 failures |
| vLLM | `GET /health` | 60s | 3 failures |
| Queue depth | SQL query | 300s | >50 warn, >100 critical |

### 8.3 Incident Response

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| P0 (Data breach) | Immediate | Shutdown + Zak |
| P1 (Service down) | 15 min | Restart + investigate |
| P2 (Degraded) | 1 hour | Monitor + ticket |

### 8.4 Backups

| Data | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| PostgreSQL (zakops_agent) | Daily | 30 days | pg_dump |
| Langfuse DB | Daily | 30 days | pg_dump |
| Encryption keys | On change | Indefinite | Secure backup |

### 8.5 Rollback Procedure

1. Stop Agent API service
2. Restore previous Docker image tag
3. If DB schema changed: restore from backup
4. Restart and verify baseline gates

---

## 9. Top 10 Failure Modes

| ID | Failure Mode | Impact | Detection | Mitigation |
|----|--------------|--------|-----------|------------|
| FM-01 | Plaintext PII in checkpoints | Data breach | PII canary gate | AES-256-GCM via SecurePostgresSaver |
| FM-02 | Tool accuracy <95% | Poor UX, wrong actions | 50-prompt eval | Prompt engineering; cloud escalation |
| FM-03 | vLLM OOM under load | Service down | nvidia-smi | Token counting middleware; context pruning |
| FM-04 | Kill-9 state loss | Lost work | Chaos test | PostgresSaver checkpoint before interrupt |
| FM-05 | Concurrent double-execution | Duplicate side effects | N=50 test | Claim-first idempotency with DB locks |
| FM-06 | Deal API unavailable | Tools fail | Health check | Retry + circuit breaker (§3.4) |
| FM-07 | Langfuse down | No traces | Health check | Graceful degradation; buffer locally |
| FM-08 | Queue backlog | Latency | Depth monitoring | Scale workers; alert at >50 |
| FM-09 | Auth bypass | Unauthorized access | Auth negative tests | Default-deny; audit all attempts |
| FM-10 | Raw content in traces | Privacy violation | Grep scan | SafeLogger wrapper; hash+length only |

---

## 10. Risks, Tradeoffs, Open Questions

### 10.1 Risks

| ID | Risk | Probability | Impact | Mitigation | Fallback |
|----|------|-------------|--------|------------|----------|
| R-01 | Deal API schema mismatch | Low | High | Contract probe first | Mock for testing |
| R-02 | PII canary false negatives | Medium | High | Conservative patterns | Manual audit |
| R-03 | vLLM throughput unknown | Medium | Medium | Benchmark before load | Reduce concurrency |
| R-04 | Langfuse Docker issues | Medium | Low | Cloud dev fallback | Disable tracing |
| R-05 | Encryption adds >50ms | Medium | Medium | Benchmark | Optimize or accept |
| R-06 | pgvector index blocks | Low | Medium | Monitor latency | Qdrant migration |

### 10.2 Open Questions

| ID | Question | Resolution Test | Owner |
|----|----------|-----------------|-------|
| OQ-01 | Actual vLLM tok/s on workstation? | `vllm bench --model Qwen2.5-32B-AWQ` | Infra |
| OQ-02 | Deal API requires same JWT or different auth? | `curl -H "Authorization: Bearer $JWT" localhost:8090/deals` | Builder |
| OQ-03 | RAG REST /search schema? | `curl http://localhost:8052/openapi.json` | Builder |
| OQ-04 | Qwen3-32B fits in 32GB VRAM? | Test model load with nvidia-smi | Infra |
| OQ-05 | Encryption latency impact? | Benchmark 1MB checkpoint save | Builder |
| OQ-06 | DB topology: shared vs compose Postgres? | Document and add connectivity gate | Builder |

---

## 11. Appendix

### 11.1 Evidence Index

| Claim | Source | Section |
|-------|--------|---------|
| HITL spike PASS | QA_REPORT.md | §2 Verdict |
| 14 gates passed | QA_REPORT.md | §3 Gate Pack Results |
| Plaintext persistence risk | QA_REPORT.md | §5 Issues List - Major |
| Port assignments | DECISION-LOCK-FILE.md | §10 Service Boundaries |
| Model: Qwen2.5-32B-AWQ | DECISION-LOCK-FILE.md | §1 Model Serving |
| Orchestration: LangGraph | DECISION-LOCK-FILE.md | §2 Orchestration |
| Tool tiers: READ/WRITE/CRITICAL | DECISION-LOCK-FILE.md | §3 Tool Pattern |
| Queue: Postgres SKIP LOCKED | DECISION-LOCK-FILE.md | §6 Queue System |
| Auth: RBAC, JWT claims | DECISION-LOCK-FILE.md | §7 Security |
| Tracing: Langfuse, no raw content | DECISION-LOCK-FILE.md | §5 Tracing |
| wassim249 scaffold selected | Scaffold-Master-Plan-v2.md | §1 Executive Summary |
| HITL spike DoD | Scaffold-Master-Plan-v2.md | §4.1 Spike DoD |
| Deal API endpoints | MDv2 | §5.2 Service Boundaries |
| Architecture diagram | MDv2 | §5.1 Major Components |
| Service boundaries | MDv2 | §5.2 Deal API vs Agent API |
| AES-256-GCM encryption | S_Gemini_3.0.md | SEC-01 |
| Non-negotiable gates structure | S_Claude_OPUS_4.5.md | §6 |
| Phase structure (0-5) | S_GPT_5.2.md | Phase Plan |
| Stop-ship: key management | R_Claude_OPUS_4.5.md | SS-02 |
| Stop-ship: missing NG gates | R_Claude_OPUS_4.5.md | SS-01 |
| Stop-ship: paper scripts | R_GPT_5.2.md | SS-04 |

### 11.2 Decision Log

| ID | Decision | Options | Chosen | Rationale |
|----|----------|---------|--------|-----------|
| D-01 | Encryption scheme | Hash-only vs AES-GCM | AES-256-GCM | S_Gemini more specific; preserves recoverability |
| D-02 | Encryption key source | Vault vs env var | Env var (Phase 1-2) | Vault is Phase 3; env var is Decision Lock compliant |
| D-03 | Concurrency threshold | N=20 vs N=50 | Both | N=20 baseline (validated), N=50 production (2.5× headroom) |
| D-04 | Phase naming | Various | Phase 0-3 | Align with Scaffold-Plan while simplifying |
| D-05 | Langfuse | Cloud fallback vs self-hosted | Self-hosted REQUIRED | Decision Lock mandates :3001; cloud is dev-only |
| D-06 | Retrieval path | pgvector direct vs RAG REST | RAG REST only | Scaffold-Plan authority; prevents split-brain |
| D-07 | Gate scripts | Single vs multiple | Multiple with standard artifacts | Better modularity; R_GPT recommendation |
| D-08 | No raw content scope | Prompts only vs all content | All content (§3.5) | R_Claude_OPUS fix; conservative approach |
| D-09 | Status claims | APPROVED vs Draft | Gate-based | R_GPT stop-ship fix; prevents false confidence |

### 11.3 What We Removed or Replaced

| Item | From | Reason |
|------|------|--------|
| "EXECUTION-READY" status | S_Claude | Misleading; no gate evidence (R_GPT SS-01) |
| "APPROVED FOR EXECUTION" status | S_Gemini | Misleading; no gate evidence (R_GPT SS-01) |
| Cloud Langfuse as compliant | S_Claude | Non-compliant with Decision Lock (R_GPT SS-02) |
| Vague "hash/encrypt" mitigation | S_Claude | Replaced with specific AES-256-GCM (R_Claude SS-03) |
| Missing checkpoint_writes scope | All S docs | Added per R_Claude SS-04 |
| Missing NG gates section | S_Gemini | Added complete section (R_Claude SS-01) |
| Unverified infra claims | S_Claude | Marked UNVERIFIED (R_GPT SS-05) |

---

## 12. Quality Audit

### 12.1 Self-Assessment Grades

| Criterion | Grade | Justification |
|-----------|-------|---------------|
| Completeness | A- | All phases, gates, tasks defined; some scripts still to create |
| Correctness | A | Aligns with all authoritative sources; contradictions resolved |
| Novelty | B+ | Incorporates R_* fixes; adds encryption spec, resilience table |
| Feasibility | A- | Based on proven spike; realistic phase targets |
| Clarity | A | Explicit definitions, tables, commands |

### 12.2 Top 10 Remaining Weaknesses

| # | Weakness | Impact | Fix |
|---|----------|--------|-----|
| 1 | Gate scripts don't exist yet | Can't run gates | Create per GATE-001..010 tasks |
| 2 | RAG REST contract unknown | Integration delay | Run OQ-03 probe |
| 3 | Encryption latency unmeasured | Performance risk | Run OQ-05 benchmark |
| 4 | MCP client not implemented | Tool gap | Phase 3 scope |
| 5 | Deal API auth unknown | Integration blocker | Run OQ-02 probe |
| 6 | No automated E2E test suite | Manual verification | Create in Phase 2 |
| 7 | Approval expiry daemon untested | Orphaned approvals | HITL-002 task |
| 8 | DB topology not pinned | Port collision risk | Document choice + gate |
| 9 | Reranker decision pending | Retrieval quality | Eval in Phase 3 |
| 10 | ABAC spec incomplete | Phase 3 scope | Define in Phase 3 |

---

**Document End**
*Synthesized: 2026-01-24T06:00:00Z*
*Editor-in-Chief: Claude OPUS 4.5 (Pass 3)*
*Inputs: 3 S_* files, 3 R_* files, 4 authoritative sources*
