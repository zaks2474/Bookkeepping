# ZakOps — Ultimate Master Implementation Roadmap (Lab Loop)

- **Version:** v1.0 (combine)
- **Timestamp (UTC):** 2026-01-24T03:58:51Z
- **Audience:** Builder (implementation) + QA (verification) + Infra (runtime)
- **Execution model:** Lab Loop cycles (Builder → QA → repeat) with hard, reproducible gates

---

## 1) Title + Version + Timestamp (UTC)

**Title:** ZakOps Ultimate Master Implementation Roadmap (Lab Loop) — combine.v1  
**Version:** v1.0  
**Timestamp (UTC):** 2026-01-24T03:58:51Z

---

## 2) Executive Summary (what we are building next + why this sequencing)

### What we are building

We are building the **ZakOps Agent API** (FastAPI on **:8095**) as the local-first “brain” that orchestrates deal lifecycle workflows with:
- **LangGraph + PostgresSaver** for durable workflow state and crash recovery.
- A **single tool gateway choke point** enforcing **READ/WRITE/CRITICAL** tiers, strict schemas, idempotency, timeouts, retries, and audit logging.
- **HITL approvals** for CRITICAL actions using the LangGraph interrupt/resume pattern.
- **Strong observability** (Langfuse + OpenTelemetry) with a **no-raw-content** policy.

This integrates with existing services:
- Deal API **:8090** (existing)
- vLLM **:8000** (local model serving)
- RAG REST **:8052** (retrieval frontend)
- MCP server **:9100** (optional tools)
- Cloudflare tunnel routes **only to Agent API :8095**

### Why this sequencing

We sequence work to prevent “false green” and protect confidentiality:
1) **Preserve the HITL spike invariants** as non-negotiable regression gates.
2) **Convert known risks into hard gates** (especially plaintext-at-rest and no-raw-content).
3) **Prove real-service integration** (Deal API + vLLM) with mocks disabled.
4) Only then scale into **queue/worker**, **retrieval evals**, and **hybrid routing** with measurable success thresholds.

---

## 3) Baseline & Proven Invariants (from HITL spike; gates that must never regress)

### Baseline status

The HITL spike is **PASS** and is the current baseline.

**Baseline gate command:**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

### Proven invariants (non-negotiable)

These MUST remain green in every phase. If any fails: **stop and fix before proceeding**.

1) **HITL scope is limited** (spike contract): only `transition_deal` triggers approval interruption.
   - Evidence: `gate_artifacts/hitl_scope_test.log`

2) **Approval persisted before interrupt response**.
   - Evidence: `gate_artifacts/invoke_hitl.json` + `gate_artifacts/db_invariants.sql.out`

3) **Crash recovery (kill -9) preserves resumability**.
   - Evidence: `gate_artifacts/checkpoint_kill9_test.log` contains `RESULT: PASSED`

4) **Concurrency is safe: exactly-once execution** for the approved CRITICAL tool.
   - Evidence: `gate_artifacts/concurrent_approves.log` (1×200, rest 409)
   - Evidence: `gate_artifacts/db_invariants.sql.out` shows `execution_count = 1`

5) **Strict tool arguments** (extra args rejected).
   - Evidence: `gate_artifacts/tool_call_validation_test.log`

6) **Auth negative semantics when enforcement enabled**:
   - Missing/expired/wrong `iss`/wrong `aud`/missing `role` → **401**
   - Insufficient role → **403**
   - Evidence: `gate_artifacts/auth_negative_tests.json`

7) **Streaming endpoint works and matches contract**.
   - Evidence: `gate_artifacts/streaming_test.log`
   - Evidence: `gate_artifacts/streaming_hitl_test.log`

8) **Local vLLM lane is live** (no cloud key requirement).
   - Evidence: vLLM health check is 200; model id `Qwen/Qwen2.5-32B-Instruct-AWQ` is served.

9) **License gate pack exists** (dependency license report; copyleft scan gate is enforced by the test pack as implemented).
   - Evidence: `gate_artifacts/dependency_licenses.json`

### Baseline known issue (must be addressed before production exposure)

- **Plaintext-at-rest risk remains** (checkpoint blobs + tool args/results). This is a **Stop‑Ship** risk for processing real confidential deal content.

---

## 4) Hard Constraints (ports, model, DB/queue, observability, security, retrieval rules)

> Conflict resolution priority (no exceptions):
> 1) `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
> 2) `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`
> 3) Best-supported elements across Pass 1 syntheses + Pass 2 critiques

### Service boundaries / ports (locked)

- **Agent API:** :8095
- **Deal API:** :8090 (KEEP-AS-IS)
- **vLLM:** :8000
- **RAG REST:** :8052
- **MCP:** :9100
- **Langfuse (self-hosted):** :3001
- **Cloudflare tunnel:** routes to :8095 only

### Model serving (locked)

- **Model:** Qwen2.5-32B-Instruct-AWQ
- **Inference:** vLLM, OpenAI-compatible; must support Hermes tool-calling parser (`--tool-call-parser hermes`)
- **Context:** max 32,768
- **Upgrade trigger:** Qwen3-32B only if ≥5% accuracy improvement on 50-prompt eval

### Orchestration (locked)

- **LangGraph** with **PostgresSaver** checkpointing
- **HITL:** `interrupt_before=["approval_gate"]`
- **Crash recovery:** kill -9 recovery is mandatory
- **Max iterations:** 10 per workflow

### Tool execution safety (locked)

- Pattern: **Hybrid MCP + Direct**
- Direct tools required (Decision Lock):
  - `list_deals`, `get_deal`, `transition_deal`, `check_health`
- Permission tiers: **READ / WRITE / CRITICAL**
- Idempotency required for WRITE/CRITICAL; **claim-first INSERT before execute**
- Pydantic validation on all tool calls
- Tool calls logged to **audit_log**

### Storage + queue + retrieval (locked)

- Storage: PostgreSQL (+ pgvector)
- Queue: Postgres `SKIP LOCKED` with retries/backoff; DLQ required; max attempts=3
- Queue performance DoD: P95 claim latency <100ms under load
- Retrieval:
  - Single retrieval path
  - Embeddings: BGE-M3 (1024)
  - Quality DoD: recall@5 ≥ 0.8

**Retrieval rule (authoritative for Agent API):**
- Agent API uses **RAG REST only** for retrieval; Agent must not query pgvector/embedding tables directly.

### Observability (locked)

- Langfuse (self-hosted) + OpenTelemetry
- **Never log raw prompts/responses** (hash + length only)
- Retention: 30 days

### Security / RBAC (locked)

- Auth: JWT (primary) + API key fallback (`X-API-Key`)
- JWT HS256 required claims: `sub`, `role`, `exp`, `iss`, `aud`
- Issuer: `zakops-auth`; Audience: `zakops-agent`
- Roles: VIEWER / OPERATOR / APPROVER / ADMIN
- Default deny
- API keys stored as SHA256 hash
- All auth attempts logged

### “No raw content” policy (explicit scope)

This roadmap makes “no raw content” concrete to avoid ambiguity:

**MUST be hash+length only (never plaintext in logs/traces):**
- LLM prompts (system + user)
- LLM responses
- Tool args (all tiers)
- Tool results (all tiers)
- Document text

**MAY be plaintext:**
- Opaque identifiers (thread_id, approval_id, deal_id)
- Timestamps, HTTP status codes
- Status strings (`awaiting_approval`, `completed`, `error`)

**DB at-rest:**
- Until at-rest mitigation is implemented and proven, treat DB persistence of raw deal/document content as a **Stop‑Ship** for production exposure.

---

## 5) Phase Plan (Phase 1..N)

### Lab Loop contract (applies to every phase)

Every phase is executed as one or more cycles:
- Builder writes: `/home/zaks/bookkeeping/docs/<phase_dir>/BUILDER_REPORT.md`
- QA writes: `/home/zaks/bookkeeping/docs/<phase_dir>/QA_REPORT.md`
- Gates write artifacts under: `/home/zaks/zakops-agent-api/gate_artifacts/`

**Rule:** No “paper gates.” If a gate is listed, the phase must include the work to implement it and emit deterministic artifacts.

---

### Phase 1 — MVP Completion (Real-Service Proof + Langfuse Self-Hosted + Stop‑Ship Closure)

**Objective**
- Convert the spike into a compliant MVP per Decision Lock Phase‑1 checklist.
- Eliminate false-green by proving real-service integration with mocks disabled.
- Convert plaintext-at-rest risk into a hard gate and a production fail-closed posture.

**Scope IN**
- Preserve all HITL spike invariants.
- Add required Direct tools (if missing): `list_deals`, `get_deal`, `check_health`.
- Implement **contract probes** (from inside container) and record artifacts:
  - Deal API contract probe (endpoint discovery + minimal response schema)
  - vLLM health probe
  - MCP probe (optional)
  - RAG REST probe (availability only; full retrieval integration is Phase 3)
- Enforce **mocks disabled** for MVP gate (`ALLOW_TOOL_MOCKS=false`).
- Bring up **self-hosted Langfuse at :3001** and prove a trace exists for a workflow.
- Implement **PII canary gate** (see Stop‑Ship SS‑03) that scans:
  - docker logs
  - Langfuse traces (if enabled)
  - DB tables containing checkpoint/tool state
- 24h soak (Decision Lock Phase‑1 checklist) with deterministic artifacts.

**Scope OUT**
- Queue/worker (Phase 2).
- Retrieval integration/evals (Phase 3).
- LiteLLM routing (Phase 4).
- ABAC (Phase 5).

**Dependencies**
- Deal API reachable at :8090.
- vLLM reachable at :8000.
- Infrastructure support to deploy Langfuse self-hosted stack on :3001.

**Primary risks**
- Deal API endpoint prefix mismatch (e.g., `/deals` vs `/api/v1/deals`).
  - Mitigation: contract probe tries both and records canonical base path.
- PII canary implementation “theatre” (scan misses binary blobs).
  - Mitigation: enforce scrubbing/encryption at the serialization boundary; canary scan becomes a secondary guardrail.

**Acceptance gates (commands)**

All Phase‑1 gates are executed via a single top-level command to prevent drift:
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

Phase‑1 is PASS only if `bring_up_tests.sh` produces these additional artifacts (beyond baseline):
- `gate_artifacts/ports_md_lint.log` (PASS marker: `PORTS_MD_LINT: PASSED`)
- `gate_artifacts/env_no_localhost_lint.log` (PASS marker: `ENV_NO_LOCALHOST: PASSED`)
- `gate_artifacts/deal_api_contract.json`
- `gate_artifacts/vllm_contract.json`
- `gate_artifacts/langfuse_selfhost_gate.log` (PASS marker: `LANGFUSE_SELFHOST: PASSED`)
- `gate_artifacts/pii_canary_report.json` (PASS marker: `PII_CANARY: PASSED`)
- `gate_artifacts/soak_24h.log` (PASS marker: `SOAK_24H: PASSED`)

**Definition of Done (objective)**
- All baseline invariants remain PASS.
- Decision Lock Phase‑1 checklist items are met:
  - vLLM serves model and health passes
  - LangGraph workflow is E2E
  - kill‑9 recovery PASS
  - tool calls validated + logged
  - Langfuse trace visible via self-hosted :3001
  - 24h soak PASS
- Mocks are disabled and Deal API is proven to receive real calls.
- PII canary gate passes (or production mode fails closed until it can pass).

---

### Phase 2 — Hardening (Queue + Audit Immutability + API Keys + Durable At‑Rest Controls)

**Objective**
- Meet Decision Lock Phase‑2 checklist and remove remaining safety gaps:
  - Postgres queue + DLQ
  - audit_log immutability
  - API key fallback
  - durability under chaos (kill -9 mid-workflow) and 72h soak
  - tool accuracy measurement (≥95%)
  - harden plaintext-at-rest handling beyond detection

**Scope IN**
- Implement Postgres `task_queue` worker with:
  - SKIP LOCKED claims
  - exponential backoff per Decision Lock
  - DLQ after max attempts
  - load test proving P95 claim latency <100ms under defined load
- Implement API key fallback (`X-API-Key`) with SHA256 storage and tests.
- Enforce **audit_log immutability at DB-level** and prove via a gate that UPDATE/DELETE fail.
- Implement **at-rest protection** for checkpoint-related persistence without breaking recovery:
  - Scope MUST include: `checkpoint_blobs` and `checkpoint_writes` (QA observed tables).
  - Key management (Phase 2): env-var bootstrap with **no default**; refuse to start in production mode if key missing.
  - Acceptance: kill‑9 and concurrency gates must still PASS.
- Implement external-service resilience in tool gateway:
  - timeouts + retries + circuit breaker for Deal API and MCP.
- 72h soak with deterministic artifact.

**Scope OUT**
- Retrieval evals (Phase 3).
- LiteLLM hybrid routing (Phase 4).
- ABAC (Phase 5).

**Dependencies**
- Phase 1 PASS.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

Phase‑2 is PASS only if `bring_up_tests.sh` produces these additional artifacts:
- `gate_artifacts/api_key_tests.json` (PASS marker: `API_KEY_TESTS: PASSED`)
- `gate_artifacts/audit_immutability_test.log` (PASS marker: `AUDIT_IMMUTABILITY: PASSED`)
- `gate_artifacts/queue_worker_smoke.log` (PASS marker: `QUEUE_WORKER_SMOKE: PASSED`)
- `gate_artifacts/queue_load_test.json` (must include measured P95 claim latency)
- `gate_artifacts/tool_accuracy_eval.json` (must show ≥95% success on defined set)
- `gate_artifacts/soak_72h.log` (PASS marker: `SOAK_72H: PASSED`)

**Definition of Done (objective)**
- Decision Lock Phase‑2 checklist satisfied.
- Queue meets latency and DLQ requirements.
- audit_log immutability enforced.
- API key fallback works.
- At-rest controls implemented and proven without breaking crash recovery.

---

### Phase 3 — Advanced (Retrieval Evals + MCP Expansion + ABAC Readiness)

**Objective**
- Meet Decision Lock Phase‑3 checklist items related to retrieval quality and advanced governance.

**Scope IN**
- Implement retrieval tool(s) using **RAG REST only** and never querying pgvector directly.
- Build retrieval eval harness and meet **recall@5 ≥ 0.8**.
- Implement optional reranker only if MRR uplift ≥10% and latency budget allows.
- Expand MCP integration (conformance tests; keep MCP optional for core Deal API path).
- Prepare for ABAC (policy scaffolding, but ABAC enforcement is Phase 5).

**Dependencies**
- Phase 2 PASS.
- RAG REST reachable.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

Phase‑3 is PASS only if artifacts include:
- `gate_artifacts/rag_rest_contract.json` (probe + schema)
- `gate_artifacts/retrieval_eval_results.json` (recall@5)
- `gate_artifacts/mcp_conformance.json` (initialize/tools/list/tools/call pass rate)

**Definition of Done (objective)**
- recall@5 ≥ 0.8 on the eval set.
- No split-brain retrieval path.
- MCP integration is safe-by-default and optional.

---

### Phase 4 — Hybrid Routing + Cost Controls (LiteLLM)

**Objective**
- Implement deterministic routing and safe cloud fallback without data leakage.

**Scope IN**
- Add LiteLLM deterministic routing.
- Enforce blocked-field policy and require explicit allow conditions.
- Enforce daily budget cap $50 and cost reporting.
- Measure ≥80% tasks handled locally on a defined workflow set.

**Dependencies**
- Phase 3 PASS.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

Phase‑4 is PASS only if artifacts include:
- `gate_artifacts/routing_policy_tests.json` (blocked-field checks)
- `gate_artifacts/cost_report.json` (budget enforcement)
- `gate_artifacts/local_percent_report.json` (≥80% local)

**Definition of Done (objective)**
- Cloud escalation is policy-safe, measurable, and budget-controlled.

---

### Phase 5 — ABAC (Policy Enforcement)

**Objective**
- Enforce ABAC policies for complex approvals and governance.

**Dependencies**
- Phase 4 PASS.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

Phase‑5 is PASS only if artifacts include:
- `gate_artifacts/abac_policy_tests.json`

**Definition of Done (objective)**
- ABAC policies are enforced, audited, and regression-tested.

---

## 6) Work Breakdown (MECE backlog table)

> All tasks must specify artifacts; no “paper work.”

| task_id | Owner | Repo/Path | Acceptance Criteria | Gate Cmd | Artifacts Emitted |
|---|---|---|---|---|---|
| GATE-001 | Builder | `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh` | Gate pack remains the single source of truth; every subgate writes deterministic artifacts and non-zero exit on failure | `./scripts/bring_up_tests.sh` | `gate_artifacts/run.log` + subgate artifacts |
| ENV-001 | Builder | `/home/zaks/zakops-agent-api/PORTS.md` | PORTS.md exists; all port references validated; no drift | `./scripts/bring_up_tests.sh` | `gate_artifacts/ports_md_lint.log` |
| ENV-002 | Builder | `/home/zaks/zakops-agent-api/.env.zakops` (or equivalent) | Host-services mode uses `host.docker.internal`; no `localhost` | `./scripts/bring_up_tests.sh` | `gate_artifacts/env_no_localhost_lint.log` |
| PROBE-001 | QA | `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh` | Deal API contract probe records canonical base path and minimal schema | `./scripts/bring_up_tests.sh` | `gate_artifacts/deal_api_contract.json` |
| TOOL-001 | Builder | `/home/zaks/zakops-agent-api/app/**/deal_tools.py` | `list_deals` implemented with strict schema, audited | `./scripts/bring_up_tests.sh` | `gate_artifacts/direct_tools_smoke.json` |
| TOOL-002 | Builder | `/home/zaks/zakops-agent-api/app/**/deal_tools.py` | `get_deal` implemented with strict schema, audited | `./scripts/bring_up_tests.sh` | `gate_artifacts/direct_tools_smoke.json` |
| TOOL-003 | Builder | `/home/zaks/zakops-agent-api/app/**/health_tools.py` | `check_health` implemented with strict schema, audited | `./scripts/bring_up_tests.sh` | `gate_artifacts/direct_tools_smoke.json` |
| OBS-001 | Infra | Langfuse stack | Self-hosted Langfuse accessible at :3001 and receives a trace | `./scripts/bring_up_tests.sh` | `gate_artifacts/langfuse_selfhost_gate.log` |
| SEC-001 | Builder | `/home/zaks/zakops-agent-api/app/core/security/*` | JWT enforcement remains correct; actor binding to JWT sub | `./scripts/bring_up_tests.sh` | `gate_artifacts/auth_negative_tests.json` |
| SEC-002 | Builder | `/home/zaks/zakops-agent-api/app/core/security/*` | API key fallback works; keys hashed only; audited | `./scripts/bring_up_tests.sh` | `gate_artifacts/api_key_tests.json` |
| AUD-001 | Builder | DB migrations | audit_log UPDATE/DELETE fail at DB-level | `./scripts/bring_up_tests.sh` | `gate_artifacts/audit_immutability_test.log` |
| PII-001 | QA | `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh` | Canary token absent from logs/traces/DB; fails closed in prod mode | `./scripts/bring_up_tests.sh` | `gate_artifacts/pii_canary_report.json` |
| DUR-001 | QA | `/home/zaks/zakops-agent-api` | kill -9 recovery remains PASS after at-rest mitigation changes | `./scripts/bring_up_tests.sh` | `gate_artifacts/checkpoint_kill9_test.log` |
| QUEUE-001 | Builder | Worker + DB migrations | SKIP LOCKED worker processes tasks; retries/backoff; DLQ | `./scripts/bring_up_tests.sh` | `gate_artifacts/queue_worker_smoke.log` |
| QUEUE-002 | QA | Load harness | P95 claim latency <100ms under defined load; JSON report | `./scripts/bring_up_tests.sh` | `gate_artifacts/queue_load_test.json` |
| EVAL-001 | QA | Eval harness | Tool accuracy ≥95% on defined prompt set | `./scripts/bring_up_tests.sh` | `gate_artifacts/tool_accuracy_eval.json` |
| RAG-001 | Builder | RAG tool module | Retrieval only via RAG REST; contract probe recorded | `./scripts/bring_up_tests.sh` | `gate_artifacts/rag_rest_contract.json` |
| RAG-002 | QA | Retrieval eval | recall@5 ≥ 0.8 | `./scripts/bring_up_tests.sh` | `gate_artifacts/retrieval_eval_results.json` |
| MCP-001 | Builder | MCP client | MCP conformance tests pass; errors normalized | `./scripts/bring_up_tests.sh` | `gate_artifacts/mcp_conformance.json` |
| ROUTE-001 | Builder | LiteLLM policy | Blocked fields prevent cloud routing; budget enforced | `./scripts/bring_up_tests.sh` | `gate_artifacts/routing_policy_tests.json`, `gate_artifacts/cost_report.json` |
| ABAC-001 | Builder | Policy engine | ABAC policies enforced and audited | `./scripts/bring_up_tests.sh` | `gate_artifacts/abac_policy_tests.json` |

---

## 7) Testing & Eval Strategy

### Regression gates

- The canonical regression command remains:
  - `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
- Regression gates must include all HITL spike invariants (Section 3).

### Load + chaos

- Chaos: kill -9 mid-workflow; verify resume and correct end state.
- Concurrency: N=20 approvals remains the validated baseline; increasing N requires justification and must not replace the baseline.
- Queue load: 1000 tasks with defined worker count; record P95 claim latency; validate DLQ behavior.

### Tool accuracy eval

- Eval set: 50 prompts (Decision Lock upgrade trigger uses 50; use same size).
- Metric: tool selection + argument correctness (exact match or schema-valid match); threshold ≥95% for Phase 2.

### Retrieval eval

- Eval set: a labeled query set (minimum size to be defined; must be stable and versioned).
- Metric: recall@5; threshold ≥0.8.

### Security tests

- Auth negatives (already in baseline): expired/wrong iss/wrong aud/missing role → 401; insufficient role → 403.
- API key tests: valid → 200; revoked/unknown → 401; ensure hash-only storage.
- audit immutability: UPDATE/DELETE denied.
- No-raw-content: canary token absent from logs/traces/DB.

---

## 8) Deployment & Ops

### Runtime expectations

- Primary runtime for lab: docker compose.
- Host-services mode must use `host.docker.internal` inside container (no `localhost` in container env).

### Monitoring

- Minimum:
  - service health probes (Agent API /health, vLLM /health, Deal API health if exposed)
  - gate pack artifacts archived per run
  - Langfuse trace coverage for workflows

### Incident response (lab)

- If a CRITICAL tool misbehaves:
  - disable CRITICAL tool execution via a config switch (must be implemented as a policy gate)
  - preserve artifacts (`gate_artifacts/`, Builder report, QA report)

### Backups and rollbacks

- DB backups:
  - nightly `pg_dump` for the Agent DB (and retrieval DB if owned locally)
  - restore procedure documented and tested once per phase boundary

---

## 9) Risks, Tradeoffs, Open Questions

### Key risks

- **Plaintext at rest**: highest risk; must be gated before production.
- **False-green due to mocks**: must prove real-service integration.
- **Langfuse availability**: self-hosted requirement must be met to declare Phase 1 done.
- **Deal API contract drift**: must be discovered/probed; do not hardcode assumptions.

### Tradeoffs

- Encrypting checkpoints can break crash recovery if done incorrectly.
  - Tradeoff: prefer “fail closed in production” until proven.

### Open questions (must be resolved via gates)

- What is the canonical Deal API base path and schema (`/deals` vs `/api/v1/deals`)?
- What is the exact RAG REST contract (health + query schema)?
- What at-rest mitigation preserves PostgresSaver resume semantics?

---

## 10) Appendix

### A) Evidence Index

**Authoritative sources**
- Decision locks (ports, model, orchestration, tool pattern, storage/queue, security, routing, retrieval):
  - `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
- Baseline invariants and known risk:
  - `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`
- Implementation mechanics (PORTS.md, host-services mode, retrieval via RAG REST, tool gateway patterns):
  - `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`
- Supplemental sequencing + acceptance thresholds:
  - `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v2.md`

**Pass 1 syntheses used (input, not authority)**
- `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_Gemini_3.0.md`
- `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_Claude_OPUS_4.5.md`
- `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_GPT_5.2.md`

**Pass 2 critiques used (input, not authority)**
- `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass2/R_Gemini_3.0.md`
- `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass2/R_Claude_OPUS_4.5.md`
- `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass2/R_GPT_5.2.md`

### B) Decision Log (what we chose and why)

1) **Langfuse requirement**
   - Choice: self-hosted Langfuse at :3001 is required to declare Phase 1 done.
   - Why: Decision Lock requires it; cloud fallback is allowed only as temporary dev mode and is explicitly non-compliant.

2) **Gates implementation approach**
   - Choice: one canonical gate pack entrypoint: `./scripts/bring_up_tests.sh`.
   - Why: avoids paper gates and drift; aligns with QA reality (existing gate pack).

3) **Retrieval path**
   - Choice: Agent API retrieval uses RAG REST only; Agent must not query pgvector directly.
   - Why: Scaffold Plan makes this authoritative; Decision Lock requires single retrieval path and pgvector; treat pgvector as backing store owned by retrieval subsystem.

4) **Deal API endpoint uncertainty**
   - Choice: treat Deal API base path as an open question resolved by contract probe gates.
   - Why: master doc uses `/deals` but scaffold plan examples use `/api/v1/deals`; Decision Lock is silent; we must not guess.

5) **Concurrency threshold**
   - Choice: keep N=20 concurrency approval test as the validated baseline gate; increasing N is optional but cannot replace baseline without justification.
   - Why: QA reality proves N=20; raising thresholds without evidence is paper-hardening.

### C) What we removed or replaced

- Removed “APPROVED / EXECUTION‑READY” language from Pass‑1 drafts (replaced with gate-based status).
- Replaced ad-hoc gate script references with a single canonical gate pack entrypoint.
- Replaced vague “encrypt/hash” statements with explicit no-raw-content scope and concrete gate artifacts.

---

## 11) Quality Audit

### Grades (A–F)

- **Completeness:** B+
- **Correctness (against locks + QA reality):** A-
- **Novelty / edge-of-tech:** B (intentionally conservative; avoids risky rewrites)
- **Engineering feasibility:** A-
- **Clarity / actionability:** A-

### Top 10 remaining weaknesses + how to fix

1) **Deal API contract is not pinned** → implement contract probe and lock it as an artifact.
2) **At-rest mitigation design not proven** → prototype + re-run kill‑9 and concurrency gates.
3) **Langfuse self-hosted stack not specified here** → add infra repo or compose file and gate it.
4) **Tool accuracy eval harness not defined** → implement eval runner producing JSON artifacts.
5) **Retrieval eval dataset not defined** → create minimal labeled dataset and version it.
6) **Queue load test definition needs a fixed workload profile** → define tasks, concurrency, hardware baseline.
7) **Policy for disabling CRITICAL tools (“kill switch”) not implemented** → add config + gate.
8) **Audit immutability mechanism unspecified (trigger vs permissions)** → pick one and add gate.
9) **MCP conformance expectations need measurable thresholds** → define pass rate and error taxonomy.
10) **Phase boundaries need explicit artifact bundles** → define per-phase artifact lists and enforce in gate pack.

