# ZakOps — Master Implementation Roadmap (3‑Pass, Pass 1)

- **Model ID:** GPT 5.2
- **Version:** v1.0-pass1
- **Timestamp (UTC):** 2026-01-24T03:15:26Z
- **Authoritative inputs (read-only):**
  - `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
  - `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`
  - `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`
  - `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v2.md`

## Executive Summary

ZakOps is a **local-first Deal Lifecycle OS** whose “brain” is an **Agent API** that orchestrates deal workflows through **LangGraph** with **durable Postgres checkpoints**, executes actions via a **single tool-gateway choke point** with **strict schemas + permission tiers + idempotency**, and enforces **HITL approvals** for CRITICAL operations.

This roadmap starts from what is **already proven green** by the HITL spike, then sequences implementation work to avoid drift and rework:
1) **Preserve and regression-gate the HITL invariants** (kill-9 recovery, exactly-once under concurrency, schema correctness).
2) **Complete the Phase‑1 MVP surface** required by the Decision Lock (direct tools, Langfuse visibility, 24h soak).
3) **Harden security/observability/data handling** so the system is safe to run against real deal data.
4) Add **queue/worker**, **retrieval (RAG REST only)** + evals, and **hybrid routing (LiteLLM)** under measured gates.

## Baseline (Observed Reality)

### Baseline verdict

The HITL spike is **PASS** and is considered the current “known-good” baseline.

Source of truth:
- `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md` (Cycle `QA-CYCLE-3`, Verdict PASS)

### Baseline gates that already pass

Primary command:
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh` → exit `0`

Required artifacts confirmed present:
- `/home/zaks/zakops-agent-api/gate_artifacts/run.log` contains `ALL GATES PASSED - HITL Spike verified!`
- `/home/zaks/zakops-agent-api/gate_artifacts/checkpoint_kill9_test.log` contains `RESULT: PASSED`
- `/home/zaks/zakops-agent-api/gate_artifacts/concurrent_approves.log` shows N=20 with exactly one 200 and the rest 409
- `/home/zaks/zakops-agent-api/gate_artifacts/db_invariants.sql.out` shows `execution_count = 1`
- `/home/zaks/zakops-agent-api/gate_artifacts/tool_call_validation_test.log` PASS
- `/home/zaks/zakops-agent-api/gate_artifacts/auth_negative_tests.json` PASS
- `/home/zaks/zakops-agent-api/gate_artifacts/streaming_test.log` PASS
- `/home/zaks/zakops-agent-api/gate_artifacts/streaming_hitl_test.log` PASS (stream ends `awaiting_approval`)
- `/home/zaks/zakops-agent-api/gate_artifacts/dependency_licenses.json` PASS (copyleft scan gate as implemented)

### Baseline spec compliance confirmed by QA

- Canonical endpoints live:
  - `POST /agent/invoke`
  - `POST /agent/invoke/stream`
  - `GET /agent/threads/{thread_id}/state`
  - approvals list/get/approve/reject endpoints
- Status strings correct: `awaiting_approval`, `completed`.
- Auth enforcement behaviors correct when enabled:
  - missing/expired/wrong issuer/wrong audience/missing role → `401`
  - insufficient role → `403`
- Actor spoofing prevention when auth is enforced: actor bound to JWT `sub`.
- Local vLLM lane verified:
  - `curl http://localhost:8000/health` → `200`
  - model id returns `Qwen/Qwen2.5-32B-Instruct-AWQ`

### Baseline known issue (must be addressed before production exposure)

QA flags a **Major** risk:
- **Plaintext persistence risk remains** (checkpoint blobs + tool args/results). This must be gated and resolved before running against real confidential deal content.

## Hard Constraints (Decision Locks + High-Authority Rules)

> Authority order for conflicts: (1) Decision Lock, (2) QA observed reality, (3) Scaffold Plan, (4) Master Doc.

### Service boundaries / ports (locked)

- Agent API: `:8095`
- Deal API (existing): `:8090`
- vLLM: `:8000`
- RAG REST: `:8052`
- MCP server: `:9100`
- Langfuse: `:3001`
- Cloudflare routes to Agent API `:8095` (NOT Deal API `:8090`).

### Model serving (locked)

- Model: `Qwen2.5-32B-Instruct-AWQ`
- Inference: vLLM, OpenAI-compatible, `--tool-call-parser hermes`
- Context window: max 32,768
- Must prove tool-calling works on sample prompts.

### Orchestration + durability (locked)

- Orchestration: LangGraph
- Checkpointing: PostgresSaver
- HITL: `interrupt_before=["approval_gate"]`
- Must pass kill‑9 crash recovery.
- Max 10 iterations per workflow.

### Tool execution pattern (locked)

- Hybrid MCP + Direct tools.
- Direct tools required: `list_deals`, `get_deal`, `transition_deal`, `check_health`.
- Permissions: READ / WRITE / CRITICAL.
- Idempotency required for WRITE/CRITICAL tools.
- Idempotency pattern: **claim-first** (INSERT before execute) to guarantee exactly-once under concurrency.
- Pydantic validation on all tool calls.
- Tool calls logged to `audit_log`.

### Storage (locked)

- Postgres (+ pgvector extension).
- Required tables at system level include: `checkpoints`, `tool_executions`, `approvals`, `task_queue`, `audit_log`, `deal_embeddings`.
- `audit_log` must be immutable (no UPDATE/DELETE).
- Checkpoint TTL: 30 days.

**Conflict resolution note (retrieval ownership):**
- The Scaffold Plan states: retrieval is exclusively via RAG REST, and Agent API must not query pgvector directly. The Decision Lock requires pgvector + a single retrieval path. Resolution: **single retrieval path is RAG REST**, which fronts the pgvector-backed store; Agent never queries embeddings tables directly.

### Queue (locked)

- Queue: Postgres SKIP LOCKED.
- Retry: exponential backoff (30s × 2^attempt).
- Max attempts: 3.
- DLQ required.
- Performance targets:
  - Warning depth >50; critical >100.
  - P95 claim latency <100ms under load.
  - Migration trigger: Redis if P95 >500ms under 1000 concurrent tasks.

### Observability (locked)

- Langfuse (self-hosted) + OpenTelemetry.
- NEVER log raw prompts/responses (hash + length only).
- 100% trace coverage for workflows.
- Retention: 30 days.

**Conflict resolution note (Langfuse “external MVP”):**
- Scaffold Plan allows external Langfuse for MVP and self-hosted in Phase 2; Decision Lock requires self-hosted Langfuse on :3001. Resolution: **self-hosted Langfuse on :3001 is a required gate to declare MVP complete**; until then, system may degrade gracefully but cannot be marked “Phase 1 Done.”

### Security (locked)

- Auth: JWT (primary) + API key fallback (`X-API-Key`).
- JWT (HS256): required claims `sub`, `role`, `exp`, `iss`, `aud`.
- Issuer: `zakops-auth`, Audience: `zakops-agent`.
- RBAC roles: VIEWER / OPERATOR / APPROVER / ADMIN.
- Default deny.
- API keys stored as SHA256 hash.
- All auth attempts logged.

### Routing / hybrid cloud (locked, phased)

- LiteLLM gateway (deterministic).
- Cloud fallback chain: local-primary → cloud-claude.
- Cloud egress policy:
  - BLOCKED fields: `ssn`, `tax_id`, `bank_account`, `credit_card`.
  - Allowed conditions: context overflow, local model error, explicit user request, complexity threshold.
- Daily budget cap: $50.
- Target: ≥80% tasks handled locally.

## Phase Plan

Each phase ends with:
- Builder report: `/home/zaks/bookkeeping/docs/roadmap_3pass/current/<phase>/BUILDER_REPORT.md`
- QA report: `/home/zaks/bookkeeping/docs/roadmap_3pass/current/<phase>/QA_REPORT.md`
- Gate artifacts: `/home/zaks/zakops-agent-api/gate_artifacts/` (or a phase-specific subfolder)

### Phase 0 — Preserve Baseline + Prevent Regression

**Objective**
- Freeze the HITL spike as the non-negotiable baseline and prevent regressions.

**Scope IN**
- Ensure baseline gate command remains stable and reproducible.
- Document baseline artifacts and PASS markers.

**Scope OUT**
- No feature expansion.

**Dependencies**
- None.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`

**Definition of Done**
- Gate Pack passes and produces all required artifacts listed in Baseline.

### Phase 1 — MVP Surface Completion (Direct Tools + Ports + Self-Hosted Langfuse + 24h Soak)

**Objective**
- Meet Decision Lock Phase‑1 MVP criteria beyond the HITL spike by proving:
  - required Direct tools exist and are exercised,
  - ports and env are authoritative (PORTS.md + no localhost rule),
  - Langfuse self-hosted on :3001 is reachable and shows a trace,
  - health checks are stable for 24h.

**Scope IN**
- Ensure Direct tools required by Decision Lock are implemented and exercised:
  - `list_deals`, `get_deal`, `check_health` (and keep `transition_deal` CRITICAL+HITL)
- Create `PORTS.md` as authoritative and enforce it in compose/env/tests.
- Provision/verify self-hosted Langfuse at `:3001` and add a gate verifying a trace is created.
- Add a 24h soak harness (health checks + lightweight invoke) with explicit PASS markers.

**Scope OUT**
- Queue/worker implementation (Phase 2).
- Retrieval eval harness (Phase 3).
- LiteLLM hybrid routing (Phase 4).

**Dependencies**
- vLLM available at :8000.
- Deal API available at :8090.

**Risks + mitigations**
- Risk: tool contracts for Deal API are unknown → integration churn.
  - Mitigation: add contract-probe gates that record evidence before implementing tool clients.

**Acceptance gates (commands)**
- Regression gate: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
- MVP proof gates (to be implemented if not already):
  - `cd /home/zaks/zakops-agent-api && ./scripts/mvp_direct_tools_smoke.sh`
  - `cd /home/zaks/zakops-agent-api && ./scripts/langfuse_selfhost_gate.sh`
  - `cd /home/zaks/zakops-agent-api && ./scripts/soak_24h.sh`

**Definition of Done (objective)**
- All Phase 0 gates PASS.
- `PORTS.md` exists and drift causes gate failure.
- `list_deals`, `get_deal`, `check_health` run successfully (HTTP 200) with strict schema validation.
- `curl -f http://localhost:3001/api/public/health` returns 2xx and a trace is visible for a test workflow.
- 24h soak completes with no crashes and PASS markers recorded.

### Phase 2 — Production Hardening (Queue + Audit Immutability + API Key Fallback + No-Raw-Content Canaries)

**Objective**
- Make the system safe and operable under real usage by implementing:
  - Postgres SKIP LOCKED queue + worker + DLQ,
  - audit immutability,
  - API key fallback,
  - no-raw-content enforcement gates across logs/traces/DB.

**Scope IN**
- Implement `task_queue` + DLQ schema and worker with retries/backoff.
- Implement API key auth fallback with SHA256 storage and tests.
- Enforce audit_log immutability (DB-level) and test UPDATE/DELETE denial.
- Add PII canary gates scanning:
  - docker logs
  - Langfuse traces
  - DB tables: checkpoints/checkpoint_blobs/approvals/tool_executions/audit_log

**Scope OUT**
- ABAC (Phase 5).
- Hybrid routing (Phase 4).

**Dependencies**
- Phase 1 complete.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
- Queue gates (to be implemented):
  - `cd /home/zaks/zakops-agent-api && ./scripts/queue_worker_smoke.sh`
  - `cd /home/zaks/zakops-agent-api && ./scripts/queue_load_test.sh`
- Security/compliance gates (to be implemented):
  - `cd /home/zaks/zakops-agent-api && ./scripts/auth_api_key_tests.sh`
  - `cd /home/zaks/zakops-agent-api && ./scripts/audit_immutability_test.sh`
  - `cd /home/zaks/zakops-agent-api && ./scripts/pii_canary_gate.sh`
- Soak gate: `cd /home/zaks/zakops-agent-api && ./scripts/soak_72h.sh`

**Definition of Done (objective)**
- Queue worker passes smoke + load tests; retries/backoff + DLQ proven.
- API key fallback works and plaintext keys never appear in DB.
- audit_log UPDATE/DELETE attempts fail.
- Canary token is not present in logs/traces/DB.
- 72h soak passes.

### Phase 3 — Retrieval Integration (RAG REST Only) + Evals

**Objective**
- Implement retrieval strictly via RAG REST and prove retrieval quality with recall@5.

**Scope IN**
- Implement `search_documents` (READ) tool using RAG REST (`:8052`) only.
- Add retrieval contract probe + schema validation.
- Create a minimal eval harness to measure recall@5 ≥ 0.8.

**Scope OUT**
- Qdrant migration unless trigger met.
- Reranker unless MRR uplift threshold met.

**Dependencies**
- Phase 2 complete.
- RAG REST available.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/retrieval_contract_test.sh`
- `cd /home/zaks/zakops-agent-api && ./evals/retrieval_eval.py`

**Definition of Done (objective)**
- Retrieval contract test passes.
- recall@5 ≥ 0.8 on a defined eval set.

### Phase 4 — Hybrid Routing (LiteLLM) + Egress/Budget Controls

**Objective**
- Add deterministic routing and cloud fallback without leaking sensitive data.

**Scope IN**
- Add LiteLLM routing.
- Enforce blocked-field policy; require explicit allow conditions.
- Add budget enforcement and reporting.

**Dependencies**
- Phase 3 complete.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/routing_policy_tests.sh`
- `cd /home/zaks/zakops-agent-api && ./scripts/cost_budget_gate.sh`

**Definition of Done (objective)**
- Blocked fields prevent cloud escalation.
- Budget cap enforced.
- ≥80% tasks handled locally on a measured test set.

### Phase 5 — ABAC + Advanced Policy

**Objective**
- Implement ABAC for complex approvals and governance.

**Acceptance gates (commands)**
- `cd /home/zaks/zakops-agent-api && ./scripts/abac_policy_tests.sh`

**Definition of Done (objective)**
- ABAC policy tests pass and approval decisions are policy-justified and audited.

## Backlog (MECE)

> Columns: task_id | priority | owner | target | acceptance criteria | gate_cmd

### A) Baseline / Regression

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| BL-001 | P0 | QA | `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh` | Gate pack remains deterministic; produces required artifacts every run | `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh` |
| BL-002 | P0 | QA | `/home/zaks/zakops-agent-api/gate_artifacts/` | Artifact presence + PASS markers validated (run.log + specific logs) | `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh` |

### B) Ports / Env / Networking

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| ENV-001 | P0 | Builder | `/home/zaks/zakops-agent-api/PORTS.md` | `PORTS.md` exists; ports match Decision Lock; drift fails gates | `cd /home/zaks/zakops-agent-api && ./scripts/ports_lint.sh` |
| ENV-002 | P0 | Builder | `.env.zakops` (repo path per scaffold reality) | Host-services URLs use `host.docker.internal`; no `localhost` references | `cd /home/zaks/zakops-agent-api && ./scripts/env_lint.sh` |

### C) Tools (Direct)

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| TOOL-001 | P0 | Builder | `app/core/langgraph/tools/*` | Implement/confirm `list_deals` with strict schema; audited | `cd /home/zaks/zakops-agent-api && ./scripts/mvp_direct_tools_smoke.sh` |
| TOOL-002 | P0 | Builder | `app/core/langgraph/tools/*` | Implement/confirm `get_deal` with strict schema; audited | `cd /home/zaks/zakops-agent-api && ./scripts/mvp_direct_tools_smoke.sh` |
| TOOL-003 | P0 | Builder | `app/core/langgraph/tools/*` | Implement/confirm `check_health` with strict schema; audited | `cd /home/zaks/zakops-agent-api && ./scripts/mvp_direct_tools_smoke.sh` |

### D) Observability (Langfuse/OTel) + No-Raw-Content

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| OBS-001 | P0 | Infra | Langfuse stack | `curl -f http://localhost:3001/api/public/health` 2xx; trace visible | `cd /home/zaks/zakops-agent-api && ./scripts/langfuse_selfhost_gate.sh` |
| OBS-002 | P0 | Builder | logging/tracing layer | Raw prompts/responses never logged; hashing enforced | `cd /home/zaks/zakops-agent-api && ./scripts/pii_canary_gate.sh` |

### E) Security (API key fallback)

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| SEC-001 | P0 | Builder | auth middleware + DB | API key stored as SHA256; valid key works; revoked fails; audited | `cd /home/zaks/zakops-agent-api && ./scripts/auth_api_key_tests.sh` |

### F) Audit immutability

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| AUD-001 | P0 | Builder | DB migrations | UPDATE/DELETE on audit_log denied at DB level | `cd /home/zaks/zakops-agent-api && ./scripts/audit_immutability_test.sh` |

### G) Queue / Worker

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| Q-001 | P1 | Builder | DB migrations + worker | SKIP LOCKED claim works; retries/backoff; DLQ used after max attempts | `cd /home/zaks/zakops-agent-api && ./scripts/queue_worker_smoke.sh` |
| Q-002 | P1 | QA | load harness | P95 claim latency <100ms under defined load; artifacts recorded | `cd /home/zaks/zakops-agent-api && ./scripts/queue_load_test.sh` |

### H) Retrieval

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| RAG-001 | P1 | Builder | retrieval tool | `search_documents` uses RAG REST only; contract probe passes | `cd /home/zaks/zakops-agent-api && ./scripts/retrieval_contract_test.sh` |
| RAG-002 | P1 | QA | eval harness | recall@5 ≥ 0.8 on eval set; results stored | `cd /home/zaks/zakops-agent-api && ./evals/retrieval_eval.py` |

### I) Routing

| task_id | priority | owner | target | acceptance criteria | gate_cmd |
|---|---|---|---|---|---|
| ROUTE-001 | P2 | Builder | routing layer | blocked fields prevent cloud escalation; policy test suite passes | `cd /home/zaks/zakops-agent-api && ./scripts/routing_policy_tests.sh` |
| ROUTE-002 | P2 | QA | budget reporting | daily budget enforced; cost dashboard artifact produced | `cd /home/zaks/zakops-agent-api && ./scripts/cost_budget_gate.sh` |

## Gates (Non‑Negotiable)

These gates MUST remain green across all phases. If any fails, stop and fix before proceeding.

1) **HITL scope gate**: only `transition_deal` is HITL in the spike.
   - Evidence artifact: `gate_artifacts/hitl_scope_test.log`
2) **Approval persisted pre-interrupt**.
   - Evidence artifact: `gate_artifacts/invoke_hitl.json` + `gate_artifacts/db_invariants.sql.out`
3) **Crash recovery (kill‑9)**.
   - Evidence artifact: `gate_artifacts/checkpoint_kill9_test.log`
4) **Concurrency exactly-once**.
   - Evidence artifacts: `gate_artifacts/concurrent_approves.log` and `gate_artifacts/db_invariants.sql.out` (`execution_count = 1`)
5) **Strict tool args**.
   - Evidence artifact: `gate_artifacts/tool_call_validation_test.log`
6) **Auth negative suite (when enforced)**.
   - Evidence artifact: `gate_artifacts/auth_negative_tests.json`
7) **Streaming contract**.
   - Evidence artifacts: `gate_artifacts/streaming_test.log` and `gate_artifacts/streaming_hitl_test.log`
8) **Local vLLM lane**.
   - Command: `curl -f http://localhost:8000/health`
9) **No copyleft at runtime** (license report gate).
   - Evidence artifact: `gate_artifacts/dependency_licenses.json`
10) **No raw content policy** (must become a hard gate before production exposure).
   - Gate to implement: `./scripts/pii_canary_gate.sh`

## Risks (Top 10 Failure Modes + Mitigations)

1) **Idempotency key non-determinism** → duplicate side effects.
   - Mitigation: canonical JSON + sha256; claim-first insert; concurrency test (N>=20).
2) **Approval not persisted before interrupt** → unrecoverable approvals after crash.
   - Mitigation: DB write before interrupt; invariant query gate.
3) **Kill‑9 recovery breaks due to serialization changes**.
   - Mitigation: kill‑9 gate on every PR/phase.
4) **Actor spoofing when auth enforced**.
   - Mitigation: bind actor_id to JWT sub when enforced; audit verification.
5) **Plaintext confidential content stored at rest**.
   - Mitigation: PII canary gates; store hashes/summaries; define production fail-closed mode.
6) **Langfuse not self-hosted / unavailable** causing missing traceability.
   - Mitigation: provision self-hosted :3001; gate health + trace creation.
7) **Tool gateway bypass** → missing audit/idempotency/permission enforcement.
   - Mitigation: code-structure rule + static grep/lint gate; central gateway module.
8) **Queue duplicate claims / lost tasks**.
   - Mitigation: SKIP LOCKED + idempotent handlers; DLQ; load tests.
9) **Hybrid routing leaks blocked fields to cloud**.
   - Mitigation: blocked-field enforcement with tests; fail closed.
10) **Port/env drift** causes hidden integration breakage.
   - Mitigation: PORTS.md + env lint; fail fast.

## Open Questions

> If unresolved, treat as blockers for the relevant phase DoD.

- **OQ-01:** Which Deal API endpoints and schemas are canonical for `list_deals`, `get_deal`, `transition_deal`?
  - Test: run a contract probe that records HTTP paths, status codes, and minimal response schema; store artifact under gate_artifacts.
- **OQ-02:** What is the exact RAG REST contract (health + query endpoints + schema)?
  - Test: implement `retrieval_contract_test.sh` to probe and store artifact.
- **OQ-03:** Where will `zakops_agent` DB live in the workstation environment: shared host Postgres :5432 or internal compose Postgres?
  - Test: document chosen mode and prove with `psql` connectivity checks from inside container.
- **OQ-04:** What is the acceptable data-at-rest representation for checkpoints/tool args/results that preserves crash recovery?
  - Test: prototype scrub/encrypt strategy and re-run kill‑9 + concurrency gates; accept only if 100% recovery.

## Appendix — Evidence Index

- Decision locks: `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
  - Model serving, orchestration, tool pattern, storage, observability, queue, security, routing, retrieval, service boundaries.
- Baseline proof and artifacts: `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`
  - Gate Pack Results Summary; Spec Compliance Audit; Issues List.
- Implementation and verification mechanics: `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`
  - Service boundary mapping (PORTS.md); host-services mode env; retrieval path via RAG REST; verification plan tests.
- Longer-horizon sequencing and acceptance thresholds: `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v2.md`
  - Implementation roadmap; acceptance thresholds; deployment & operations context.
