# ZakOps Agent — Master Implementation Roadmap

**Model ID:** Claude OPUS 4.5
**Version:** 1.0.0
**Timestamp (UTC):** 2026-01-24T04:30:00Z
**Status:** EXECUTION-READY
**Priority Resolution Order:** DECISION-LOCK > QA_REPORT > Scaffold-Plan > MDv2

---

## 1. Executive Summary

The HITL spike completed on 2026-01-23 with **VERDICT: PASS** across all 14 gates. The foundational patterns (interrupt/resume, crash recovery, idempotency, auth) are proven. This roadmap transitions from validated spike to production-grade Deal Lifecycle Agent.

**Next Milestone:** Phase 1 — Wire Agent API to real Deal API (:8090), deploy Langfuse at :3001, resolve plaintext persistence risk.

**Definition of Done (System-Wide):**
- Agent processes deals end-to-end with HITL approval gates
- Tool accuracy ≥95% on 50-prompt eval
- 72h continuous health with zero unrecovered crashes
- Langfuse traces visible for 100% of workflows
- No raw content in logs/traces/DB (hash+length only)

---

## 2. Baseline (Proven by HITL Spike)

**Source:** [QA_REPORT.md §2-4]

### Gates Passed (2026-01-23)

| Gate | Status | Evidence Artifact |
|------|--------|-------------------|
| T0: Health | ✅ PASS | `gate_artifacts/health.json` |
| T1: HITL Invoke | ✅ PASS | `gate_artifacts/invoke_hitl.json` → `awaiting_approval` |
| T2: DB Invariants | ✅ PASS | `gate_artifacts/db_invariants.sql.out` |
| T3: Approve | ✅ PASS | `gate_artifacts/approve.json` → HTTP 200 |
| T4: Idempotency | ✅ PASS | `gate_artifacts/approve_again.json` → HTTP 409 |
| T5: Concurrency N=20 | ✅ PASS | `gate_artifacts/concurrent_approves.log` → 1×200, 19×409 |
| T6: Kill-9 Recovery | ✅ PASS | `gate_artifacts/checkpoint_kill9_test.log` |
| T8: Tool Validation | ✅ PASS | `gate_artifacts/tool_call_validation_test.log` |
| T9: License | ✅ PASS | `gate_artifacts/dependency_licenses.json` → no copyleft |
| T10: Audit Log | ✅ PASS | `gate_artifacts/db_invariants.sql.out` |
| T11: Mock Safety | ✅ PASS | `gate_artifacts/mock_safety_test.log` |
| T12: Streaming | ✅ PASS | `gate_artifacts/streaming_test.log` |
| T13: HITL Scope | ✅ PASS | `gate_artifacts/hitl_scope_test.log` |
| T14: Auth Negative 7/7 | ✅ PASS | `gate_artifacts/auth_negative_tests.json` |

### Infrastructure Verified

| Service | Port | Status |
|---------|------|--------|
| Agent API | :8095 | ✅ Healthy |
| Deal API | :8090 | ✅ Healthy |
| vLLM (Qwen2.5-32B-AWQ) | :8000 | ✅ Serving |
| RAG REST | :8052 | ✅ Running |
| PostgreSQL | :5432 | ✅ Running |

### Open Issue (P0)

**QA-M1: Plaintext persistence risk** — Checkpoint blobs contain raw tool args/results. Must add PII canary gate before production.
[Source: QA_REPORT.md §5]

---

## 3. Hard Constraints (from DECISION-LOCK-FILE.md)

**Authority:** These constraints are NON-NEGOTIABLE. Any deviation requires explicit lock-file amendment.

### 3.1 Service Ports (LOCKED)

| Service | Port | Notes |
|---------|------|-------|
| vLLM | 8000 | `--tool-call-parser hermes` |
| RAG REST | 8052 | Exclusive retrieval path |
| Deal API | 8090 | KEEP-AS-IS |
| Agent API | 8095 | Cloudflare routes here |
| MCP Server | 9100 | streamable-http |
| Langfuse | 3001 | Self-hosted |
| PostgreSQL | 5432 | pgvector extension |

### 3.2 Technology Stack (LOCKED)

| Component | Choice | Constraint |
|-----------|--------|------------|
| Model | Qwen2.5-32B-Instruct-AWQ | Upgrade only if ≥5% accuracy gain |
| Inference | vLLM | GPU util 0.90, 32K context |
| Orchestration | LangGraph + PostgresSaver | `interrupt_before=["approval_gate"]`, max 10 iter |
| Vector DB | pgvector → Qdrant (Ph3) | Migrate if >1M vectors OR P95 >250ms |
| Queue | Postgres SKIP LOCKED | Migrate to Redis if P95 claim >500ms |
| Tracing | Langfuse self-hosted | NEVER log raw content |
| Auth | RBAC → ABAC (Ph3) | JWT: sub, role, exp, iss=zakops-auth, aud=zakops-agent |
| Secrets | Env vars → Vault (Ph3) | Never commit to repo |

### 3.3 Tool Tiers (LOCKED)

| Tier | Tools | Approval Required |
|------|-------|-------------------|
| READ | list_deals, get_deal, search_documents, check_health | No |
| WRITE | create_deal, update_deal | Policy-dependent |
| CRITICAL | transition_deal, delete_deal, send_email | **Always** |

### 3.4 Migration Triggers (LOCKED)

| Component | Trigger | Target |
|-----------|---------|--------|
| Vector DB | >1M vectors OR P95 >250ms | Qdrant |
| Queue | P95 claim >500ms under 1000 tasks | Redis+Dramatiq |
| Model | ≥5% accuracy improvement on 50-prompt eval | Qwen3-32B |
| Auth | Phase 3 complexity | ABAC |

---

## 4. Phase Plan

### Phase 1: Production Integration (1 Week)

**Objective:** Wire spike to real services; resolve P0 security issue; establish stability baseline.

#### Scope IN
- Wire `transition_deal`, `list_deals`, `get_deal` to Deal API :8090
- Deploy Langfuse at :3001 (self-hosted or cloud fallback)
- Implement PII canary gate for checkpoint tables
- 24h continuous health monitoring
- Integration test suite

#### Scope OUT
- RAG integration (Phase 2)
- Queue worker (Phase 2)
- LiteLLM routing (Phase 2)
- Additional tools beyond deal CRUD

#### Dependencies
- ✅ HITL spike passing (verified 2026-01-23)
- ✅ Deal API at :8090 (verified healthy)
- ✅ vLLM at :8000 (verified serving)
- ⏳ Langfuse Docker availability

#### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Deal API schema mismatch | High | Read OpenAPI spec first; create contract tests |
| PII detection false negatives | High | Conservative regex; manual audit backup |
| Langfuse Docker issues | Medium | Fall back to cloud; graceful degradation |

#### Acceptance Gates

```bash
# P1-G1: Deal API Integration
curl -X POST http://localhost:8095/agent/invoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT" \
  -d '{"actor_id":"test","message":"List all deals"}'
# Assert: status=completed, actions_taken includes list_deals with real data

# P1-G2: HITL E2E with Real Transition
curl -X POST http://localhost:8095/agent/invoke \
  -d '{"actor_id":"test","deal_id":"DL-0001","message":"Transition to qualified"}'
# Assert: status=awaiting_approval
# Then: POST /agent/approvals/{id}:approve → verify Deal API state changed

# P1-G3: Langfuse Trace
curl -f http://localhost:3001/api/public/health
# Assert: HTTP 200; trace visible in UI for above workflow

# P1-G4: PII Canary
./scripts/pii_canary_gate.sh
# Assert: exit 0 (no SSN/CC/email patterns in checkpoint tables)

# P1-G5: 24h Health
./scripts/health_monitor.sh --duration 24h --interval 300
# Assert: 100% uptime, 0 crashes
```

#### Definition of Done
- [ ] Agent invokes Deal API for all deal tools
- [ ] Langfuse trace visible for complete workflow
- [ ] PII canary gate passes
- [ ] 24h health monitor shows 100% uptime
- [ ] All artifacts in `gate_artifacts/phase1/`

---

### Phase 2: Production Hardening (2 Weeks)

**Objective:** Complete tool validation, RBAC enforcement, queue processing, chaos testing.

#### Scope IN
- Full tool registry with Pydantic validation
- RBAC middleware enforcement
- Queue worker (Postgres SKIP LOCKED)
- Dead letter queue
- Chaos tests (kill -9, concurrent load)
- 50-prompt tool accuracy eval
- Prometheus metrics

#### Scope OUT
- RAG retrieval (Phase 3)
- LiteLLM cloud routing (Phase 3)
- ABAC policies (Phase 3)

#### Acceptance Gates

```bash
# P2-G1: Tool Validation
curl -X POST http://localhost:8095/agent/invoke \
  -d '{"actor_id":"test","message":"Transition INVALID-ID to bogus_stage"}'
# Assert: Validation error returned, tool NOT executed

# P2-G2: RBAC Enforcement
curl -X POST "http://localhost:8095/agent/approvals/xxx:approve" \
  -H "Authorization: Bearer $VIEWER_JWT"
# Assert: 403 Forbidden

# P2-G3: Queue Load Test
python tests/load/queue_load_test.py --tasks 1000 --workers 10
# Assert: P95 claim <100ms, 0 lost tasks

# P2-G4: Chaos Test
./tests/chaos/run_chaos.sh
# Assert: kill -9 mid-workflow → state recovered → workflow completes

# P2-G5: Tool Accuracy
python evals/run_tool_accuracy.py
# Assert: ≥95% exact match on 50 prompts
```

#### Definition of Done
- [ ] Tool registry rejects invalid params
- [ ] RBAC blocks VIEWER from approve
- [ ] Queue P95 claim <100ms under 1000 tasks
- [ ] Chaos test passes
- [ ] Tool accuracy ≥95%
- [ ] 72h health monitor passes

---

### Phase 3: Advanced Features (3-4 Weeks)

**Objective:** RAG retrieval, LiteLLM routing, cost tracking, full lifecycle demo.

#### Scope IN
- RAG REST integration via `query_rag` tool
- LiteLLM gateway with cost-based routing
- Cloud Egress Policy enforcement
- Cost tracking dashboard
- MCP client for :9100
- Full deal lifecycle demo

#### Acceptance Gates

```bash
# P3-G1: RAG Retrieval
python evals/run_retrieval_eval.py
# Assert: recall@5 ≥ 0.80

# P3-G2: Local Handling
# After 100 test workflows:
# Assert: ≥80% handled locally (no cloud escalation)

# P3-G3: Cost Tracking
curl http://localhost:8095/agent/metrics/cost
# Assert: JSON with total_cost, by_model breakdown

# P3-G4: Full Lifecycle Demo
python demos/full_lifecycle.py
# Assert: Deal progresses intake → qualified → proposal → won
```

---

## 5. Task Backlog (MECE)

### 5.1 Agent API

| ID | Task | Owner | Path | Acceptance | Gate |
|----|------|-------|------|------------|------|
| API-001 | Wire transition_deal to Deal API | Builder | `app/core/langgraph/tools/deal_tools.py` | HTTP POST succeeds | `pytest tests/integration/test_transition_deal.py` |
| API-002 | Wire list_deals to Deal API | Builder | `app/core/langgraph/tools/deal_tools.py` | Returns real data | `pytest tests/integration/test_list_deals.py` |
| API-003 | Wire get_deal to Deal API | Builder | `app/core/langgraph/tools/deal_tools.py` | Returns single deal | `pytest tests/integration/test_get_deal.py` |
| API-004 | Add create_deal tool | Builder | `app/core/langgraph/tools/deal_tools.py` | WRITE permission | Unit tests |
| API-005 | Add update_deal tool | Builder | `app/core/langgraph/tools/deal_tools.py` | WRITE permission | Unit tests |

### 5.2 Security

| ID | Task | Owner | Path | Acceptance | Gate |
|----|------|-------|------|------------|------|
| SEC-001 | Enable JWT enforcement | Builder | `app/core/middleware/auth.py` | AGENT_JWT_ENFORCE=true works | `pytest tests/auth/test_negative.py` |
| SEC-002 | RBAC middleware | Builder | `app/core/middleware/rbac.py` | VIEWER blocked from /approve | Role test suite |
| SEC-003 | API key management | Builder | `app/core/auth/api_keys.py` | Create/revoke works | Unit tests |

### 5.3 Observability

| ID | Task | Owner | Path | Acceptance | Gate |
|----|------|-------|------|------------|------|
| OBS-001 | Langfuse self-hosted | Builder | `docker-compose.langfuse.yml` | UI at :3001 | `curl -f localhost:3001/api/public/health` |
| OBS-002 | No-raw-content wrapper | Builder | `app/core/observability/safe_logger.py` | Hash+length only | Grep logs |
| OBS-003 | Prometheus metrics | Builder | `app/core/observability/metrics.py` | /metrics valid | curl check |

### 5.4 HITL / Approvals

| ID | Task | Owner | Path | Acceptance | Gate |
|----|------|-------|------|------------|------|
| HITL-001 | PII canary gate | Builder | `scripts/pii_canary_gate.sh` | No SSN/CC/email in DB | Exit 0 |
| HITL-002 | Approval expiry (24h) | Builder | `app/core/approvals/expiry.py` | Expired auto-rejected | Cron test |

### 5.5 Queue / Ops

| ID | Task | Owner | Path | Acceptance | Gate |
|----|------|-------|------|------------|------|
| OPS-001 | 24h health monitor | Builder | `scripts/health_monitor.sh` | Continuous run | 24h uptime |
| OPS-002 | Queue worker | Builder | `app/workers/queue_worker.py` | SKIP LOCKED claims | Load test |
| OPS-003 | Dead letter handler | Builder | `app/workers/dlq_handler.py` | Failed tasks captured | Unit tests |

### 5.6 RAG / Memory

| ID | Task | Owner | Path | Acceptance | Gate |
|----|------|-------|------|------------|------|
| RAG-001 | query_rag tool | Builder | `app/core/tools/rag_tools.py` | Calls RAG REST :8052 | Integration test |
| RAG-002 | Retrieval eval | QA | `evals/retrieval/` | recall@5 ≥ 0.80 | Eval script |

---

## 6. Non-Negotiable Gates

These gates are derived from HITL spike invariants and Decision Lock. **All must pass before production.**

| Gate ID | Description | Command | Pass Criteria |
|---------|-------------|---------|---------------|
| NG-01 | Kill-9 recovery | `./tests/chaos/kill9_test.sh` | State recovered, workflow completes |
| NG-02 | Concurrent idempotency N=50 | `./tests/chaos/concurrent_approve.sh 50` | Exactly 1 execution |
| NG-03 | Auth negative 7/7 | `pytest tests/auth/test_negative.py` | All 7 cases pass |
| NG-04 | No copyleft deps | `./scripts/license_scan.sh` | 0 GPL/AGPL at runtime |
| NG-05 | HITL scope | `pytest tests/hitl/test_scope.py` | Only CRITICAL tools trigger approval |
| NG-06 | Tool validation | `pytest tests/tools/test_validation.py` | Invalid params rejected |
| NG-07 | PII canary | `./scripts/pii_canary_gate.sh` | Exit 0 |
| NG-08 | No raw content | `./scripts/raw_content_scan.sh` | 0 matches in logs/traces/DB |

---

## 7. Top 10 Failure Modes

| ID | Failure Mode | Impact | Detection | Mitigation |
|----|--------------|--------|-----------|------------|
| FM-01 | Plaintext PII in checkpoints | Data breach | PII canary gate | Hash/encrypt tool args before storage |
| FM-02 | Tool accuracy <95% | Poor UX, wrong actions | 50-prompt eval | Prompt engineering; cloud escalation |
| FM-03 | vLLM OOM under load | Service down | nvidia-smi monitoring | Reduce batch/context; graceful error |
| FM-04 | Kill-9 state loss | Lost work | Chaos test | PostgresSaver checkpoint before interrupt |
| FM-05 | Concurrent double-execution | Duplicate side effects | N=50 concurrency test | Claim-first idempotency with DB locks |
| FM-06 | Deal API unavailable | Tools fail | Health check | Retry with backoff; circuit breaker |
| FM-07 | Langfuse down | No traces | Health check | Graceful degradation; buffer locally |
| FM-08 | Queue backlog | Latency | Depth monitoring (>50 warn) | Scale workers; alert operator |
| FM-09 | Auth bypass | Unauthorized access | Auth negative tests | Default-deny; audit all attempts |
| FM-10 | Raw content in traces | Privacy violation | Grep scan | safe_logger wrapper; hash+length only |

---

## 8. Risks and Open Questions

### Risks

| ID | Risk | Probability | Impact | Mitigation | Fallback |
|----|------|-------------|--------|------------|----------|
| R-01 | Deal API schema mismatch | Low | High | Contract tests | Mock fallback for testing |
| R-02 | PII canary false negatives | Medium | High | Conservative patterns | Manual audit |
| R-03 | vLLM throughput unknown | Medium | Medium | Benchmark before load | Reduce concurrency |
| R-04 | Langfuse Docker issues | Medium | Low | Cloud fallback | Disable tracing |

### Open Questions

| ID | Question | Resolution Test |
|----|----------|-----------------|
| OQ-01 | Actual vLLM tok/s on workstation? | `vllm bench --model Qwen2.5-32B-AWQ` |
| OQ-02 | Deal API requires same JWT? | Check Deal API auth config |
| OQ-03 | RAG REST /search schema? | `curl http://localhost:8052/openapi.json` |
| OQ-04 | Qwen3-32B fits in 32GB VRAM? | Test model load with nvidia-smi |

---

## 9. Appendix: Evidence Index

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
| Architecture diagram | MDv2 | §5.1 Major Components |
| Service boundaries | MDv2 | §5.2 Deal API vs Agent API |
| Workload model | MDv2 | §4.3 Workload Model |

---

**Document End**
*Generated: 2026-01-24T04:30:00Z*
*Model: Claude OPUS 4.5*
