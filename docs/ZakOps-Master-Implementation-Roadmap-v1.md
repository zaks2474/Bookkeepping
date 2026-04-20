# ZakOps — Master Implementation Roadmap (Lab Loop)

## 1) Title + Version + Timestamp

- **Title:** ZakOps Master Implementation Roadmap (Lab Loop)
- **Version:** v1.0
- **Timestamp:** 2026-01-23T20:18:55-06:00
- **Primary execution workflow:** Lab Loop (Builder=Claude Code, QA=Codex)
- **Primary target repo (current):** `/home/zaks/zakops-agent-api` (Agent API)

---

## 2) Executive Summary (what we’re building next, why this order, what “done” means)

### What we’re building next

We are building the **ZakOps Agent API (:8095)** as a production-grade, local-first “deal lifecycle brain” that:
- Orchestrates workflows via **LangGraph + PostgresSaver** (durable checkpoints, crash recovery).
- Executes tools via a **single choke point** with strict schemas, permission tiers, and idempotency for WRITE/CRITICAL operations.
- Implements **HITL** approvals for CRITICAL tools using `interrupt_before=["approval_gate"]`.
- Provides **secure, auditable** operations (RBAC, audit_log, redaction, tracing) from day 1.

Justification:
- [Doc: ZakOps-Ultimate-Master-Document-v2.md | Section: 2. Executive Summary]
- [Doc: DECISION-LOCK-FILE.md | Section: Quick Reference]

### Why this order (risk-driven sequencing)

1) **Lock in safety invariants first (already proven)**, then expand capabilities without regressions.  
   - [Doc: QA_REPORT.md | Section: 2) Verdict: PASS]
2) **Eliminate “false green” integrations** by enforcing no-mocks and proving real-service E2E against the existing Deal API and vLLM before adding more tools.  
   - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]
3) **Treat plaintext-at-rest exposure as P0** (explicitly flagged by QA) and close it before processing real confidential deal content at scale.  
   - [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]
4) **Only then** add queue/worker, retrieval, MCP, and hybrid routing based on measured triggers and acceptance thresholds.  
   - [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]
   - [Doc: DECISION-LOCK-FILE.md | Section: 9. Embeddings / Retrieval]
   - [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]

### What “done” means (for Phase 1–2 MVP)

We consider the MVP milestone “done” only when:
- Gate Pack passes and produces a complete artifact pack (every run is reproducible).  
  - [Doc: QA_REPORT.md | Section: 3) Gate Pack Results Summary]
- “First Working Demo” succeeds against real services with mocks disabled: approve `transition_deal` → Deal API reflects stage transition.  
  - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]
- Decision Lock security/observability requirements are enforced:
  - RBAC enforced; auth failures logged
  - No raw prompts/responses in logs/traces
  - Plaintext-at-rest risk explicitly mitigated (encrypt/scrub) with a failing canary gate if violated  
  - [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]
  - [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]
  - [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

---

## 3) Current Baseline (what is already proven/green, with evidence references to QA_REPORT + gate artifacts)

### Baseline status: HITL spike is PASS (spec-compliant)

Proven by QA (Cycle `QA-CYCLE-3`):
- HITL interrupt/resume for `transition_deal` only
- Approval persisted before interrupt response
- kill `-9` recovery works
- Concurrency: exactly-once execution under N=20 approvals
- Tool args strictness (extra forbidden)
- Auth enforcement negative tests pass
- SSE streaming endpoint works and can end in `awaiting_approval`
- Local vLLM lane verified (no `OPENAI_API_KEY` requirement)

Evidence:
- [Doc: QA_REPORT.md | Section: 2) Verdict: PASS]
- [Doc: QA_REPORT.md | Section: 3) Gate Pack Results Summary]
- [Doc: QA_REPORT.md | Section: 4) Spec Compliance Audit (explicit yes/no)]

### Baseline artifacts (must remain reproducible)

Artifact pack location (current repo):
- `/home/zaks/zakops-agent-api/gate_artifacts/`

Minimum required artifacts for “green” status (per QA report):
- `run.log` (contains `ALL GATES PASSED - HITL Spike verified!`)
- `invoke_hitl.json`, `approve.json`
- `checkpoint_kill9_test.log`
- `concurrent_approves.log`
- `db_invariants.sql.out`
- `tool_call_validation_test.log`
- `auth_negative_tests.json`
- `streaming_test.log`, `streaming_hitl_test.log`

Evidence:
- [Doc: QA_REPORT.md | Section: 3) Gate Pack Results Summary]

### Explicit known risk (P0)

QA flagged a major risk:
- **Plaintext persistence risk remains (checkpoint blobs + tool args/results)**.

This constrains what we can safely do next:
- We must not progress to “real confidential deal content at scale” until we implement and gate data-at-rest controls.

Evidence:
- [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

---

## 4) Decision Locks & Constraints (explicit bullets extracted from DECISION-LOCK-FILE)

### 4.1 Model & inference (locked)

- Primary model: `Qwen2.5-32B-Instruct-AWQ`.
- Inference engine: vLLM on `:8000`, OpenAI-compatible.
- Tool calling must work with Hermes tool-calling format (`--tool-call-parser hermes`).
- Context window: 32,768 tokens max.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 1. Model Serving]

### 4.2 Orchestration (locked)

- Orchestration: LangGraph.
- Durable checkpointing: PostgresSaver.
- HITL pattern: `interrupt_before=["approval_gate"]`.
- Must persist across crashes; kill `-9` recovery is a hard DoD gate.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 2. Orchestration]

### 4.3 Tools and execution safety (locked)

- Pattern: Hybrid MCP + Direct.
- Direct tools required: `list_deals`, `get_deal`, `transition_deal`, `check_health`.
- Permission tiers: READ / WRITE / CRITICAL.
- Idempotency required for WRITE/CRITICAL tools using claim-first pattern.
- Pydantic validation for all tool calls.
- Tool calls must be logged to `audit_log`.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]

### 4.4 Storage, queue, retrieval (locked)

- DB: PostgreSQL (+ pgvector extension).
- Required tables include: `checkpoints`, `tool_executions`, `approvals`, `task_queue`, `audit_log`, `deal_embeddings`.
- Checkpoint TTL: 30 days.
- `audit_log` must be immutable (no DELETE/UPDATE).
- Queue: Postgres SKIP LOCKED; retries with exponential backoff; max attempts=3; DLQ required.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 4. Storage]
- [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]

### 4.5 Observability (locked)

- Tracing/observability: Langfuse (self-hosted) + OpenTelemetry.
- **Never log raw prompts/responses** (hash + length only).
- Retention: 30 days.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]

### 4.6 Security / RBAC (locked)

- Auth: JWT (primary) + API key (fallback).
- RBAC Phase 1 → ABAC Phase 3.
- JWT: HS256; required claims: `sub`, `role`, `exp`, `iss`, `aud`.
- Issuer: `zakops-auth`; Audience: `zakops-agent`.
- Default-deny policy.
- API keys stored as SHA256 hash.
- All auth attempts logged.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]

### 4.7 Routing / hybrid cloud (locked, but phased)

- LiteLLM gateway (deterministic).
- Cloud egress policy with blocked fields; daily budget $50; ≥80% tasks local.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]

### 4.8 Service boundaries (locked)

- Agent API: :8095
- Deal API: :8090 (existing)
- vLLM: :8000 (existing)
- MCP: :9100
- RAG REST: :8052
- Langfuse: :3001

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 10. Service Boundaries]

---

## 5) Implementation Strategy (how we move from current state to production-grade system)

### 5.1 Guiding principles

1) **Local-first, deterministic execution**  
   - Prefer local vLLM and local services; any cloud escalation is policy-gated and measurable.  
   - [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]
2) **Reliability invariants are regression gates**  
   - kill `-9` recovery and concurrency exactly-once tests run in every phase.  
   - [Doc: DECISION-LOCK-FILE.md | Section: 2. Orchestration]
   - [Doc: QA_REPORT.md | Section: 3) Gate Pack Results Summary]
3) **One tool execution choke point**  
   - All tool calls go through a single gateway that enforces schema validation, permissions, idempotency, timeouts/retries, and audit logging.  
   - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Phase 3: Tool Gateway Implementation]
4) **Security is default-deny**  
   - RBAC is enforced on every endpoint and every tool call; actor identity must bind to authenticated subject when auth is enabled.  
   - [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]
5) **No raw content policy is enforced with tests**  
   - We do not “trust” developer discipline; we enforce it with canary tests and failing gates.  
   - [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]
   - [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

### 5.2 What we will NOT do yet (deferred items)

To avoid scope drift and keep Lab Loop execution deterministic:
- **No ABAC** until Phase 6+ (RBAC only in Phase 1–5).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]
- **No Qdrant** until migration triggers are met.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 4. Storage]
- **No Redis queue** until migration triggers are met.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]
- **No model upgrade (Qwen3)** until the locked eval delta threshold is proven.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 1. Model Serving]
- **No cloud dependency** in Phase 1–2 (hybrid routing is Phase 5).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]

---

## 6) Phase Plan (Phases 1–N)

### Lab Loop execution contract (applies to every phase)

Each phase is executed as one or more Builder+QA cycles:
- **Builder output:** `/home/zaks/bookkeeping/docs/<phase_dir>/BUILDER_REPORT.md`
- **QA output:** `/home/zaks/bookkeeping/docs/<phase_dir>/QA_REPORT.md`
- Each cycle must end with a PASS/FAIL verdict and artifact pointers.

Evidence (pattern already used successfully):
- [Doc: QA_REPORT.md | Section: 1) Cycle ID + timestamp]

---

### Phase 1 — Real-Service E2E + “No Mocks” Enforcement (P0)

**Objectives**
- Convert the spike from “green in isolation” to “green against real services”:
  - Real Deal API reachable and used
  - Real vLLM reachable and used
  - Mocks forbidden for acceptance
- Create a deterministic “First Working Demo” gate that can be run repeatedly in Lab Loop.

Justification:
- [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]
- [Doc: QA_REPORT.md | Section: 6) Stop/Go guidance]

**Scope (IN)**
- Add a **Real-Service Gate** to the test pack:
  - Assert `ALLOW_TOOL_MOCKS=false`
  - From inside the Agent container, verify reachability of:
    - vLLM `:8000`
    - Deal API `:8090`
    - (optional) RAG REST `:8052`
    - (optional) MCP `:9100`
  - Execute `transition_deal` HITL flow against a verified deal (or a synthetic deal created for test) and confirm Deal API state changed.
- Implement missing locked direct tools (if missing): `list_deals` and `check_health` with strict schemas.
- Create `PORTS.md` and require scripts/docs to reference it.

Justification:
- [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]
- [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.2 Service Boundary Mapping (PORTS.md Authoritative)]

**Scope (OUT)**
- API key auth fallback (Phase 2).
- Queue and workers (Phase 3).
- Retrieval eval harness (Phase 4).
- LiteLLM routing (Phase 5).

**Deliverables**
- Code:
  - Updated `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh` with Real-Service Gate outputs
  - Direct tools: `list_deals`, `check_health` (strict schemas, no extra args)
  - `PORTS.md`
- Docs:
  - `/home/zaks/bookkeeping/docs/phase1_real_service/BUILDER_REPORT.md`
  - `/home/zaks/bookkeeping/docs/phase1_real_service/QA_REPORT.md`
- Gates/artifacts:
  - `gate_artifacts/real_service_probe.json`
  - `gate_artifacts/real_transition_verification.json`

**Dependencies**
- Existing services must be running and reachable at their locked ports:
  - Deal API :8090
  - vLLM :8000
  - RAG REST :8052 (optional in Phase 1, but probe it)
  - MCP :9100 (optional in Phase 1, but probe it)

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 10. Service Boundaries]

**Risks + mitigations**
- Risk: Deal API endpoint contract is unknown/changed → tests hang or silently degrade to mocks.  
  - Mitigation: add short-timeout probes and fail fast with captured evidence; do not guess endpoints.  
  - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]
- Risk: “real deal data” exposure while plaintext-at-rest risk is unresolved.  
  - Mitigation: use synthetic deals/test data only; block any production exposure until Phase 2 controls pass.  
  - [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

**Acceptance tests / gates (explicit commands and artifacts)**
- Primary gate:
  - Command: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
  - Pass criteria:
    - exit code 0
    - includes new artifacts `real_service_probe.json` and `real_transition_verification.json`
- Evidence to attach in QA report:
  - `gate_artifacts/run.log` (PASS marker)
  - `gate_artifacts/real_service_probe.json`
  - `gate_artifacts/real_transition_verification.json`

**Definition of Done (objective)**
- A QA cycle report shows PASS with real-service verification and mocks disabled.
- `PORTS.md` exists and ports in compose/tests match it.
- Direct tools required by Decision Lock exist and are validated.

**Estimated effort (assumptions explicit)**
- 2–5 Builder-days + 1–3 QA-days.
- Assumption: Deal API exposes a testable transition endpoint and a test deal can be created safely (verify via probes).  
  - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]

---

### Phase 2 — Security & Compliance Closure (P0/P1)

**Objectives**
- Close the P0 plaintext-at-rest risk and make security controls production-grade for day-to-day use:
  - API key fallback
  - RBAC enforcement proof
  - Audit immutability proof
  - Canary gates for no-raw-content across logs/traces/DB

Justification:
- [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]
- [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]
- [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

**Scope (IN)**
- Implement API key auth fallback (`X-API-Key`) with SHA256 hashed storage.
- Enforce RBAC role matrix end-to-end (VIEWER/OPERATOR/APPROVER/ADMIN).
- Enforce `audit_log` immutability (DB permission/trigger) and prove via tests.
- Implement DB-at-rest mitigation for sensitive state:
  - Encrypt or scrub checkpoint blobs and persisted tool args/results, OR fail closed in `APP_ENV=production` until encryption is implemented.
- Add a canary test that fails if plaintext canary appears in:
  - docker logs
  - Langfuse spans (if enabled)
  - DB tables (`checkpoints`, `checkpoint_blobs`, `approvals`, `tool_executions`, `audit_log`)

Justification:
- [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Phase 5: Observability Compliance]
- [Doc: DECISION-LOCK-FILE.md | Section: 4. Storage]

**Scope (OUT)**
- Queue and workers (Phase 3).
- Retrieval eval harness (Phase 4).
- LiteLLM routing (Phase 5).

**Deliverables**
- Code:
  - API key table + middleware + tests
  - RBAC tests (including approval endpoints permissioning)
  - audit immutability enforcement + tests
  - DB canary scan + logs/traces canary scans + gates
- Docs:
  - `/home/zaks/bookkeeping/docs/phase2_security/BUILDER_REPORT.md`
  - `/home/zaks/bookkeeping/docs/phase2_security/QA_REPORT.md`
- Gates/artifacts:
  - `gate_artifacts/rbac_tests.json`
  - `gate_artifacts/api_key_tests.json`
  - `gate_artifacts/audit_immutability_test.log`
  - `gate_artifacts/pii_canary_report.json`

**Dependencies**
- Phase 1 PASS.
- Decision on encryption/scrubbing approach for checkpoints/tool args/results.
  - If unknown, implement the “fail closed in production” fallback first.

**Risks + mitigations**
- Risk: encrypting checkpoint blobs breaks resume semantics.  
  - Mitigation: run kill `-9` recovery gate as regression; if it fails, revert encryption implementation and use fail-closed fallback while redesigning serialization.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 2. Orchestration]
- Risk: canary false positives due to existing old data.  
  - Mitigation: canary gate uses a unique per-run token; scan only for that token; clear test artifacts deterministically.  
  - (General engineering knowledge; implement as test design, not a system claim.)

**Acceptance tests / gates**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh` must pass with new artifacts.
- New gates must be treated as hard gates (non-zero exit on failure).

**Definition of Done**
- API key auth works; RBAC enforced; audit immutability proven.
- Canary gate passes (no raw content in logs/traces/DB for the canary token).
- No regression in HITL durability (kill `-9`, concurrency exactly-once).

**Estimated effort (assumptions explicit)**
- 4–10 Builder-days + 3–6 QA-days.
- Assumption: we can implement at-rest protection without rewriting LangGraph internals; if not, we default to “fail closed in production” and schedule design work.  
  - [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

---

### Phase 3 — Postgres Queue + Worker (SKIP LOCKED) (P1)

**Objectives**
- Implement durable background execution (task_queue + worker + DLQ) with retries/backoff and measurable claim latency.

Justification:
- [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]
- [Doc: ZakOps-Ultimate-Master-Document-v2.md | Section: 8. Implementation Roadmap]

**Scope (IN)**
- Implement `task_queue` and DLQ schema (as specified in the scaffold plan).
- Implement worker that claims tasks using SKIP LOCKED.
- Implement retries/backoff and DLQ after max attempts.
- Add load tests to measure:
  - P95 claim latency target <100ms under lab load (explicit, measured).

Justification:
- [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]
- [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Phase 2: LangGraph Adaptation + Queue]

**Scope (OUT)**
- Redis migration unless triggers exceeded.

**Deliverables**
- Code:
  - DB migration(s) for queue and DLQ
  - Worker service and scripts
  - Queue metrics (depth thresholds)
- Docs:
  - `/home/zaks/bookkeeping/docs/phase3_queue/BUILDER_REPORT.md`
  - `/home/zaks/bookkeeping/docs/phase3_queue/QA_REPORT.md`
- Gates/artifacts:
  - `gate_artifacts/queue_worker_smoke.log`
  - `gate_artifacts/queue_load_test.json`

**Dependencies**
- Phase 2 PASS (security + data-at-rest controls are stable).

**Risks + mitigations**
- Risk: claim latency >100ms under load.  
  - Mitigation: record evidence; if sustained and meets migration trigger criteria, plan Redis migration (do not silently accept).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]

**Acceptance tests / gates**
- Worker functional smoke test produces PASS artifact.
- Load test produces measured claim latency; PASS only if threshold met or a formal migration decision is logged.

**Definition of Done**
- Queue processes tasks with retries/backoff and DLQ; concurrency safe; performance evidence captured.

**Estimated effort (assumptions explicit)**
- 3–8 Builder-days + 2–5 QA-days.
- Assumption: single-host lab; multi-host scaling deferred.  
  - [Doc: ZakOps-Ultimate-Master-Document-v2.md | Section: 10. Deployment & Operations]

---

### Phase 4 — Retrieval via RAG REST + Eval Harness (P1)

**Objectives**
- Integrate retrieval strictly through the RAG REST service (single retrieval path) and establish retrieval quality benchmarks.

Conflict identification (must resolve):
- Scaffold Master Plan states: **retrieval is exclusively via RAG REST; no direct pgvector queries from Agent API**.  
  - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.5 Retrieval Path (Authoritative)]
- Decision Lock states: **pgvector is the Phase 1 vector DB**, with embeddings BGE-M3.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 4. Storage]

Resolution stance (this roadmap):
- Agent API will **not** query pgvector directly; pgvector remains the underlying vector store owned by the retrieval subsystem (e.g., RAG REST). This satisfies both documents without introducing split-brain retrieval.
- If RAG REST is unavailable, Agent retrieval must fail closed (no “silent fallback” to direct DB queries).

**Scope (IN)**
- Implement `search_documents` (READ tier) tool calling RAG REST (`:8052`) with strict schema validation.
- Add a contract probe gate for RAG REST (health + a known query).
- Build an eval harness for retrieval quality and record:
  - recall@5 target ≥0.8 (locked).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 9. Embeddings / Retrieval]

**Scope (OUT)**
- Reranker enablement unless MRR uplift threshold is met.
- Qdrant migration unless triggers exceeded.

**Deliverables**
- Code:
  - `search_documents` tool + schemas
  - `retrieval_contract_test.sh`
  - `evals/retrieval_eval.py` skeleton + dataset format
- Docs:
  - `/home/zaks/bookkeeping/docs/phase4_retrieval/BUILDER_REPORT.md`
  - `/home/zaks/bookkeeping/docs/phase4_retrieval/QA_REPORT.md`
- Gates/artifacts:
  - `gate_artifacts/retrieval_contract.json`
  - `gate_artifacts/retrieval_eval_results.json`

**Dependencies**
- Phase 3 PASS.
- Verified RAG REST contract (endpoints unknown → must be probed and recorded; do not guess).

**Risks + mitigations**
- Risk: RAG REST contract mismatch.  
  - Mitigation: contract probe gate fails fast; update tool only after capturing evidence.  
  - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.5 Retrieval Path (Authoritative)]

**Acceptance tests / gates**
- Contract gate passes (RAG REST reachable and returns expected schema).
- Retrieval eval produces measured metrics; acceptance if recall@5 ≥ 0.8 on a defined dataset.

**Definition of Done**
- Agent can retrieve via RAG REST and quality is measured and recorded (not assumed).

**Estimated effort (assumptions explicit)**
- 4–12 Builder-days + 3–8 QA-days.
- Assumption: we can assemble a minimal labeled retrieval dataset (even 25–50 queries) from synthetic or sanitized documents before using sensitive data.  
  - [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

---

### Phase 5 — MCP Integration + Tool Catalog Expansion (P2)

**Objectives**
- Add MCP tools safely with conformance tests and reliability patterns, while keeping MCP optional.

Justification:
- [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]
- [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Appendix C: MCP Client Contract Checklist]

**Scope (IN)**
- Implement MCP client with:
  - streamable-http transport
  - timeouts, retries, circuit breaker
  - schema validation before call
  - audit logging (no raw content)
- Conformance test: initialize → tools/list → tools/call (measured pass rate).

**Scope (OUT)**
- Make MCP a hard dependency for core workflow (forbid; keep direct tool fallback for core paths).

**Deliverables**
- Code: MCP client + conformance test script
- Docs: phase reports
- Artifacts: `gate_artifacts/mcp_conformance.json`

**Dependencies**
- Phase 4 PASS.

**Risks + mitigations**
- Risk: MCP instability breaks core workflows.  
  - Mitigation: keep MCP optional; direct tools remain primary for Deal API critical path.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]

**Acceptance tests / gates**
- MCP conformance test achieves a documented pass rate and failure modes are enumerated.

**Definition of Done**
- MCP integration exists and is safe-by-default without becoming a single point of failure.

**Estimated effort (assumptions explicit)**
- 3–8 Builder-days + 2–5 QA-days.
- Assumption: MCP server tools are stable and accessible at :9100.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]

---

### Phase 6 — Hybrid Routing (LiteLLM) + Egress Policy + Cost Controls (P2)

**Objectives**
- Implement deterministic local-first routing with explicit cloud fallback and enforce egress and budget constraints.

Justification:
- [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]

**Scope (IN)**
- LiteLLM gateway integration.
- Egress policy enforcement (blocked fields).
- Cost tracking and daily budget cap enforcement.
- Test harness validating fallback triggers and blocked content behavior.

**Scope (OUT)**
- Any routing that is non-deterministic or untestable.

**Deliverables**
- Code: routing policy + tests + metrics
- Docs: phase reports
- Artifacts: `gate_artifacts/routing_policy_tests.json`, `gate_artifacts/cost_report.json`

**Dependencies**
- Phase 5 PASS.
- Secure cloud credentials (no secrets committed).

**Risks + mitigations**
- Risk: cloud exfiltration of sensitive data.  
  - Mitigation: fail closed on blocked fields; add adversarial tests; require explicit allow conditions.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]

**Acceptance tests / gates**
- Blocked fields prevent cloud escalation.
- Budget cap enforcement test passes.
- ≥80% tasks local measured on a test set (target locked; measurement required).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]

**Definition of Done**
- Hybrid routing is demonstrably safe and measurable under lab tests.

**Estimated effort (assumptions explicit)**
- 5–15 Builder-days + 4–10 QA-days.
- Assumption: clear cloud provider selection and stable API connectivity; otherwise defer.  
  - [Doc: ZakOps-Ultimate-Master-Document-v2.md | Section: 8. Implementation Roadmap]

---

## 7) Task Backlog (MECE)

> Each task includes: priority, owner role, target path, acceptance criteria, labloop task_id + gate command.

### Agent API

- **P0 | Builder | Target:** `/home/zaks/zakops-agent-api/PORTS.md`  
  - Task: Create `PORTS.md` and make it authoritative; update scripts/docs to reference it.  
  - Acceptance: `PORTS.md` exists; gate script asserts ports match config; drift causes gate failure.  
  - Labloop: `LL-AGENT-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`  
  - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.2 Service Boundary Mapping (PORTS.md Authoritative)]

- **P0 | QA | Target:** `/home/zaks/zakops-agent-api/gate_artifacts/`  
  - Task: Add a spec-check artifact proving canonical endpoints exist (`/agent/*`) and schema/status match.  
  - Acceptance: artifact contains curl results and JSON schema checks; fails on any mismatch.  
  - Labloop: `LL-AGENT-002`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`  
  - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Phase 1: Core Surgery (Service Shell)]

### LangGraph

- **P0 | Builder | Target:** `/home/zaks/zakops-agent-api/app/core/langgraph/graph.py`  
  - Task: Ensure HITL interrupt pattern remains `interrupt_before=["approval_gate"]` and is regression-tested.  
  - Acceptance: HITL scope test proves only `transition_deal` triggers interrupt; kill `-9` gate remains green.  
  - Labloop: `LL-LG-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`  
  - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 2. Orchestration]

### Tools

- **P0 | Builder | Target:** `/home/zaks/zakops-agent-api` (test script + tool modules)  
  - Task: Add Real-Service Gate (no mocks + container reachability probes + verified deal transition).  
  - Acceptance: new artifacts exist; any unreachable service or missing transition fails hard (non-zero exit).  
  - Labloop: `LL-TOOLS-001`  
  - Gate: `ALLOW_TOOL_MOCKS=false cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`  
  - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]

- **P0 | Builder | Target:** `TBD` (Deal API tool module)  
  - Task: Implement missing direct tools from Decision Lock: `list_deals`, `check_health` with strict schemas.  
  - Acceptance: schema validation rejects extra args; tool calls succeed against real services; tool calls are audited.  
  - Labloop: `LL-TOOLS-002`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`  
  - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]

- **P1 | Builder | Target:** `TBD` (MCP client module + script)  
  - Task: Implement MCP client and conformance test (initialize → tools/list → tools/call).  
  - Acceptance: conformance test produces measurable pass rate and normalized error report.  
  - Labloop: `LL-MCP-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/mcp_conformance_test.sh`  
  - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Appendix C: MCP Client Contract Checklist]

### HITL

- **P0 | QA | Target:** `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh`  
  - Task: Ensure concurrency exactly-once remains a regression gate (N>=20) and DB invariant is asserted.  
  - Acceptance: `concurrent_approves.log` shows 1×200, rest 409; DB invariant `execution_count=1`.  
  - Labloop: `LL-HITL-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`  
  - Evidence: [Doc: QA_REPORT.md | Section: 3) Gate Pack Results Summary]

### Security

- **P0 | Builder | Target:** `TBD` (auth middleware + DB)  
  - Task: Add API key fallback auth with hashed storage and tests.  
  - Acceptance: valid key → 200; revoked/expired → 401; key never stored plaintext.  
  - Labloop: `LL-SEC-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/auth_api_key_tests.sh`  
  - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]

- **P0 | QA | Target:** `TBD` (RBAC test harness)  
  - Task: RBAC matrix tests (VIEWER/OPERATOR/APPROVER/ADMIN) including approval endpoints.  
  - Acceptance: VIEWER blocked from approve; APPROVER allowed; attempts logged.  
  - Labloop: `LL-SEC-002`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/rbac_tests.sh`  
  - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]

### Observability

- **P0 | Builder | Target:** `TBD` (logging/tracing/db)  
  - Task: Implement “no raw content” across logs/traces/DB and add canary gates.  
  - Acceptance: canary token absent from docker logs, Langfuse spans, and DB tables; gate fails if found.  
  - Labloop: `LL-OBS-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/pii_canary_gate.sh`  
  - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]

### RAG/Memory

- **P1 | Builder | Target:** `TBD` (RAG REST tool module + script)  
  - Task: Implement `search_documents` tool (RAG REST only) + contract probe + eval harness skeleton.  
  - Acceptance: retrieval works via RAG REST; recall@5 measured; no direct DB vector queries in agent.  
  - Labloop: `LL-RAG-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/retrieval_contract_test.sh`  
  - Eval: `cd /home/zaks/zakops-agent-api && ./evals/retrieval_eval.py`  
  - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.5 Retrieval Path (Authoritative)]

### UI integration

- **P1 | Builder | Target:** `TBD` (Next.js repo path)  
  - Task: UI for approvals + streaming consumption (SSE).  
  - Acceptance: can view pending approvals, approve/reject, observe stream events; no secret leakage in UI logs.  
  - Labloop: `LL-UI-001`  
  - Gate: manual smoke checklist + captured network logs (until e2e tests exist)  
  - Evidence: [Doc: ZakOps-Ultimate-Master-Document-v2.md | Section: 8. Implementation Roadmap]

### Ops/Deploy

- **P1 | Builder | Target:** `/home/zaks/zakops-agent-api`  
  - Task: SBOM + dependency license report + vulnerability scan artifact generation (no secrets).  
  - Acceptance: artifacts exist; copyleft at runtime is flagged; issues triaged.  
  - Labloop: `LL-OPS-001`  
  - Gate: `cd /home/zaks/zakops-agent-api && ./scripts/sbom_and_scan.sh`  
  - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Phase 0: Fork & Environment Setup]

---

## 8) Verification & Evaluation Strategy

### Automated tests (unit/integration/e2e)

- Unit tests (fast):
  - Tool schema strictness (reject extra args)
  - Idempotency key determinism
  - RBAC role enforcement
- Integration tests:
  - `/agent/invoke` → `awaiting_approval` → `:approve` → `completed`
  - Audit trail completeness checks
- E2E tests (lab):
  - “First Working Demo” scenario (real stage transition verified)

Evidence:
- [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 6) Verification Plan (Repo & Capability Verification)]

### Reliability/chaos tests

- kill `-9` recovery test (every phase, regression gate).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 2. Orchestration]
- Concurrency exactly-once test (N>=20 approvals; every phase).  
  - [Doc: QA_REPORT.md | Section: 3) Gate Pack Results Summary]
- Retry/idempotency tests for WRITE/CRITICAL tools (Phase 2+).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]

### Model/tool-call quality evals

- Phase 1 acceptance: tool-calling works on 5 sample prompts (measured; do not assume).  
  - [Doc: DECISION-LOCK-FILE.md | Section: 1. Model Serving]
- Phase 2 target: tool accuracy ≥95% on an eval set (to build and measure).  
  - [Doc: ZakOps-Ultimate-Master-Document-v2.md | Section: 8. Implementation Roadmap]

### Performance targets (latency, TPS, soak)

Locked targets / triggers (must be measured):
- Queue claim latency P95 <100ms under load; migrate to Redis if P95 >500ms under 1000 tasks.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]
- Retrieval: recall@5 ≥0.8; migrate to Qdrant if >1M vectors OR P95 >250ms.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 4. Storage]
  - [Doc: DECISION-LOCK-FILE.md | Section: 9. Embeddings / Retrieval]
- Soak: health checks pass 24h then 72h (Phase 2+).  
  - [Doc: DECISION-LOCK-FILE.md | Section: Checklist Summary]

---

## 9) Security & Compliance Plan

### Auth / RBAC policy

- JWT: HS256, required claims, strict iss/aud checks.
- RBAC: VIEWER/OPERATOR/APPROVER/ADMIN; default deny.
- Approval endpoints restricted to APPROVER+.
- API key fallback via `X-API-Key` with SHA256 storage.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 7. Security / RBAC]

### Secrets handling

- Phase 1–2: environment variables; never commit secrets.
- Phase 3+: migrate to Vault (locked direction).

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: Quick Reference]

### Logging/tracing redaction

- Never log raw prompts/responses (hash + length only).
- Enforce via canary tests; do not rely on discipline.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]

### Data-at-rest policy (P0)

Constraint:
- QA has flagged plaintext persistence exposure as a major risk.  
  - [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

Roadmap requirement:
- Implement encryption/scrubbing (checkpoints/tool args/results) OR block production mode until implemented.
- Add DB canary scan gate as a hard requirement.

Justification:
- [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: Phase 5: Observability Compliance]

---

## 10) Observability Plan

### Logs
- Structured logs with redaction and correlation IDs (thread_id/approval_id/idempotency_key).
- No raw prompts/responses in logs.

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]

### Metrics
- Prometheus metrics exposed (locked).
- Minimum metrics:
  - approvals pending/approved/rejected
  - tool executions success/failure
  - auth failures/denies
  - queue depth + DLQ depth (Phase 3)

Evidence:
- [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]
- [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]

### Traces

Conflict identification:
- Decision Lock: Langfuse self-hosted on :3001.  
  - [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]
- Scaffold Master Plan: Langfuse external for MVP; self-hosted Phase 2.  
  - [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.6 Langfuse Deployment (Authoritative)]

Resolution strategy (this roadmap):
- Phase 1: tracing must **not block** execution; it may degrade gracefully if Langfuse unavailable.
- Phase 2: enforce self-hosted Langfuse compatibility and add a gate verifying Langfuse UI at :3001 and traces visible.
- Regardless: “no raw content” applies in all phases.

### Replay/debug workflow
- Primary replay artifacts:
  - approval_id, thread_id, idempotency_key
  - audit_log rows linked to approval/tool execution
  - checkpoint state (encrypted/scrubbed post-Phase 2)
- All lab runs archive `gate_artifacts/` and QA report paths.

### Incident response basics (lab)
- Stop CRITICAL tools quickly (policy toggle / disable list) to prevent unsafe side effects.
- Preserve artifacts: gate_artifacts + DB invariants output + minimal redacted logs.

---

## 11) Risks, Tradeoffs, Open Questions

### P0 (must resolve before production exposure)

1) **Plaintext at rest (checkpoints/tool args/results)**  
   - Impact: High (confidential deal leakage)  
   - Likelihood: Medium (already observed risk)  
   - Detection: DB canary gate + manual audits  
   - Mitigation: encrypt/scrub; fail closed in production until implemented  
   - Fallback: block production mode entirely; keep synthetic-only lab until resolved  
   - Evidence: [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]

2) **False-green due to mocks**  
   - Impact: High (integration drift)  
   - Likelihood: Medium  
   - Detection: Real-Service Gate with `ALLOW_TOOL_MOCKS=false`  
   - Mitigation: fail closed when upstream unreachable  
   - Fallback: block Phase 2 start until Phase 1 real-service PASS  
   - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]

### P1 (must resolve for reliable operations)

3) **Queue correctness under concurrency**  
   - Impact: Medium (lost work / duplicates)  
   - Likelihood: Medium  
   - Detection: load tests and DLQ verification  
   - Mitigation: SKIP LOCKED + idempotent handlers + DLQ  
   - Fallback: migrate to Redis when trigger exceeded (per lock)  
   - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]

4) **RAG REST contract mismatch / retrieval split-brain**  
   - Impact: Medium  
   - Likelihood: Medium  
   - Detection: contract probe gates; code scan prohibiting direct DB retrieval  
   - Mitigation: single retrieval path (RAG REST only)  
   - Fallback: if RAG REST unavailable, retrieval fails closed (no DB fallback)  
   - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.5 Retrieval Path (Authoritative)]

### P2 (advanced, must be gated)

5) **Cloud egress leakage**  
   - Impact: High  
   - Likelihood: Low→Medium  
   - Detection: blocked-field tests + adversarial evals  
   - Mitigation: fail closed on blocked fields; strict allow rules  
   - Fallback: disable cloud routing until compliance gates pass  
   - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]

### Open questions (unknown facts; do not guess)

1) **Deal API contract**: exact endpoints and request/response schemas for list/get/transition.  
   - Verification plan: Real-Service Gate probes with short timeouts, records evidence, and only then updates tool URLs.  
   - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]

2) **RAG REST contract**: health, search endpoints, response schema.  
   - Verification plan: `retrieval_contract_test.sh` captures responses; QA verifies.  
   - Evidence: [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 3.5 Retrieval Path (Authoritative)]

3) **Langfuse availability**: do we have self-hosted Langfuse at :3001 today?  
   - Verification plan: add explicit `curl` probe + trace creation test; if missing, Phase 2 must include self-hosted deployment.  
   - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 5. Tracing / Observability]

4) **Encryption approach for checkpoints**: what preserves resume semantics?  
   - Verification plan: prototype encryption at serialization boundary; rerun kill `-9` gate; accept only if recovery remains 100%.  
   - Evidence: [Doc: DECISION-LOCK-FILE.md | Section: 2. Orchestration]

---

## 12) Appendix

### A) Extracted evidence index (where major claims are grounded)

- HITL spike is PASS; core invariants proven → [Doc: QA_REPORT.md | Section: 2) Verdict: PASS]
- Required artifact pack exists → [Doc: QA_REPORT.md | Section: 3) Gate Pack Results Summary]
- Plaintext persistence is a known risk → [Doc: QA_REPORT.md | Section: 5) Issues List (ranked)]
- “First Working Demo” scenario is the required E2E validation → [Doc: ZakOps-Scaffold-Master-Plan-v2.md | Section: 5) "First Working Demo" Scenario (MVP Validation)]
- Ports and service boundaries are locked → [Doc: DECISION-LOCK-FILE.md | Section: 10. Service Boundaries]
- Tool pattern, idempotency, schema validation are locked → [Doc: DECISION-LOCK-FILE.md | Section: 3. Tool Pattern]
- Queue requirements and thresholds are locked → [Doc: DECISION-LOCK-FILE.md | Section: 6. Queue System]
- Retrieval thresholds are locked → [Doc: DECISION-LOCK-FILE.md | Section: 9. Embeddings / Retrieval]
- Hybrid routing constraints are locked → [Doc: DECISION-LOCK-FILE.md | Section: 8. LLM Routing]
- Overall sequencing aligns with master doc phases → [Doc: ZakOps-Ultimate-Master-Document-v2.md | Section: 8. Implementation Roadmap]

### B) Proposed labloop tasks list (table)

| task_id | repo | gate_cmd | spec_check_cmd | eval_cmd |
|--------:|------|----------|----------------|----------|
| LL-AGENT-001 | `/home/zaks/zakops-agent-api` | `./scripts/bring_up_tests.sh` | `curl -sS http://localhost:8095/agent/invoke -o /dev/null` | — |
| LL-AGENT-002 | `/home/zaks/zakops-agent-api` | `./scripts/bring_up_tests.sh` | `curl -sS http://localhost:8095/agent/threads/<id>/state -o /dev/null` | — |
| LL-TOOLS-001 | `/home/zaks/zakops-agent-api` | `ALLOW_TOOL_MOCKS=false ./scripts/bring_up_tests.sh` | — | — |
| LL-TOOLS-002 | `/home/zaks/zakops-agent-api` | `./scripts/bring_up_tests.sh` | — | — |
| LL-HITL-001 | `/home/zaks/zakops-agent-api` | `./scripts/bring_up_tests.sh` | — | — |
| LL-SEC-001 | `/home/zaks/zakops-agent-api` | `./scripts/auth_api_key_tests.sh` | — | — |
| LL-SEC-002 | `/home/zaks/zakops-agent-api` | `./scripts/rbac_tests.sh` | — | — |
| LL-OBS-001 | `/home/zaks/zakops-agent-api` | `./scripts/pii_canary_gate.sh` | — | — |
| LL-QUEUE-001 | `/home/zaks/zakops-agent-api` | `./scripts/queue_worker_smoke.sh` | — | — |
| LL-QUEUE-002 | `/home/zaks/zakops-agent-api` | `./scripts/queue_load_test.sh` | — | — |
| LL-RAG-001 | `/home/zaks/zakops-agent-api` | `./scripts/retrieval_contract_test.sh` | — | `./evals/retrieval_eval.py` |
| LL-MCP-001 | `/home/zaks/zakops-agent-api` | `./scripts/mcp_conformance_test.sh` | — | — |

### C) Assumptions list (explicit)

1) **Deal API contract discoverability:** The Deal API exposes stable endpoints that can be probed with short timeouts. If not, Phase 1 must begin with contract discovery and the roadmap timeline expands.  
2) **RAG REST contract discoverability:** RAG REST provides a query endpoint and health endpoint; if not, Phase 4 must begin with service contract definition.  
3) **Checkpoint encryption feasibility:** We can implement encryption/scrubbing without breaking LangGraph recovery; if not, we will fail closed in production and schedule a dedicated design iteration.  
4) **Langfuse availability:** Self-hosted Langfuse may not be running today; Phase 2 will provision it if missing.  
5) **Dataset availability:** Retrieval eval dataset may not exist; Phase 4 must create a minimal sanitized dataset before claiming recall@5 thresholds.  

