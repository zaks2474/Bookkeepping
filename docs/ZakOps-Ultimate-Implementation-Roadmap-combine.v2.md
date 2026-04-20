# ZakOps — Ultimate Implementation Roadmap (combine.v2)

- **Version:** v2.0
- **Timestamp (UTC):** 2026-01-24T05:07:26Z
- **Readiness statement:** Executable only when **phase gates PASS** and required **artifacts exist** (objective evidence; no “approved/execution-ready” claims).

## Authority & conflict resolution

If any sources conflict, resolve in this order:
1) `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md` (hard constraints)
2) `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md` (observed reality + proven gates + known risks)
3) `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md` (implementation mechanics, service topology, contracts)
4) `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v2.md` (broader architecture; subordinate to locks/QA)
5) Pass 1 syntheses (`S_*.md`) and Pass 2 critiques (`R_*.md`) as supporting material only

When Document A vs Document B disagree, choose using this ranking:
(1) correctness/feasibility (2) completeness (3) safety/reliability/security (4) clarity (5) performance/scale (6) future-proofing.
All such choices are recorded in **Appendix → Decision Log** with acceptance checks.

## One canonical gate entrypoint (global)

Single source of truth for gates (no scattered scripts in the roadmap):

```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

- Any “sub-gate” referenced in this roadmap MUST be implemented as a step inside `./scripts/bring_up_tests.sh`.
- Every sub-gate MUST emit deterministic artifacts under `/home/zaks/zakops-agent-api/gate_artifacts/` and must fail the run with a non-zero exit code when a phase requires it to PASS.

## Canonical terminology (global)

- **Canonical Agent API prefix:** `/agent/*`
  - Versioned aliases may exist (`/api/v1/agent/*`) but are not canonical and must not be used for acceptance unless explicitly permitted by the contract probe.
- **Canonical approval status string:** `awaiting_approval`
  - Other status strings are non-compliant unless explicitly added to the contract snapshot.
- **Canonical completion status string:** `completed`
- **Canonical failure status string:** `error`

## Canonical artifact root (global)

- **Artifact directory:** `/home/zaks/zakops-agent-api/gate_artifacts/`
- Every phase must define an explicit artifact set (filenames + PASS markers) that `bring_up_tests.sh` produces.

---

# Executive Summary

ZakOps is a **local-first Deal Lifecycle OS** whose “brain” is the **Agent API**. We will execute a phased program using Lab Loop (Builder+QA+Infra) with hard gates.

What we build and prove, in order:
1) Preserve and lock the **HITL spike invariants** as non-regressable gates.
2) Lock **contracts** (API base paths, status strings, tool names, artifact naming) to prevent drift.
3) Close **Stop‑Ship security risks** (plaintext at rest / raw content leakage) with **enforceable gates** and fail-closed behavior for production exposure.
4) Prove **real-service E2E** with mocks disabled (Deal API + vLLM).
5) Add intelligence (RAG REST only) and measurable evals (tool accuracy / retrieval recall).
6) Add optional integrations (MCP) and controlled hybrid routing (LiteLLM) with egress/budget enforcement.
7) Harden reliability (queue/DLQ, chaos, audit immutability), formal QA/red-team, and then production ops/runbooks.

---

# Baseline & Proven Invariants (HITL spike)

Baseline is “green” only when the gate pack passes:

```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

## Baseline invariants (must never regress)

These are proven by `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md` and the current gate pack implementation (`scripts/bring_up_tests.sh`).

| Gate ID | Description | Evidence artifact | PASS marker / check |
|---|---|---|---|
| BL-01 | Health endpoint | `gate_artifacts/health.json` | HTTP 200 recorded |
| BL-02 | HITL invoke triggers approval | `gate_artifacts/invoke_hitl.json` | `status == "awaiting_approval"` |
| BL-03 | Approval persisted pre-interrupt | `gate_artifacts/db_invariants.sql.out` | approval row exists pre-interrupt |
| BL-04 | Approve completes workflow | `gate_artifacts/approve.json` | HTTP 200 and `status == "completed"` |
| BL-05 | Idempotency rejects duplicate | `gate_artifacts/approve_again.json` | HTTP 409 (no double exec) |
| BL-06 | Concurrency N=20 | `gate_artifacts/concurrent_approves.log` | 1×200, rest 409; `RESULT: PASSED` present |
| BL-07 | Kill -9 recovery | `gate_artifacts/checkpoint_kill9_test.log` | contains `RESULT: PASSED` |
| BL-08 | Tool validation | `gate_artifacts/tool_call_validation_test.log` | JSON `status == "PASSED"` |
| BL-09 | Dependency license report | `gate_artifacts/dependency_licenses.json` | file exists; copyleft findings empty/absent |
| BL-10 | Audit log evidence present | `gate_artifacts/db_invariants.sql.out` | audit events exist |
| BL-11 | Mock safety sanity | `gate_artifacts/mock_safety_test.log` | PASS marker present |
| BL-12 | Streaming (basic + HITL) | `gate_artifacts/streaming_test.log` + `gate_artifacts/streaming_hitl_test.log` | basic contains `STATUS=PASSED`; HITL contains `awaiting_approval` |
| BL-13 | HITL scope is constrained | `gate_artifacts/hitl_scope_test.log` | JSON `status == "PASSED"` |
| BL-14 | Auth negative suite (enforced) | `gate_artifacts/auth_negative_tests.json` | all tests passed; correct 401/403 semantics |

## Baseline Stop‑Ship risk

QA flags a Major risk (Stop‑Ship for production exposure):
- **Plaintext at rest risk remains** (checkpoint blobs and persisted tool args/results may contain raw content).
This roadmap makes that risk a P0 gate in Phase 1 (not prose).

---

# Hard Constraints (non-negotiable)

## Service boundaries / ports (locked)

From `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`:

- Agent API: **:8095**
- Deal API (existing): **:8090**
- vLLM: **:8000**
- RAG REST: **:8052**
- MCP server: **:9100**
- Langfuse (self-hosted): **:3001**
- Cloudflare tunnel routes to **Agent API :8095** (NOT Deal API :8090)

## Model serving (locked)

- Model: `Qwen2.5-32B-Instruct-AWQ`
- Inference: vLLM, OpenAI-compatible, `--tool-call-parser hermes`
- Context window: max 32,768 tokens
- Upgrade trigger: Qwen3-32B only if ≥5% accuracy improvement on 50-prompt eval

## Orchestration (locked)

- Orchestration: LangGraph
- Checkpointing: PostgresSaver
- HITL pattern: `interrupt_before=["approval_gate"]`
- Crash recovery: kill -9 gate required
- Max iterations: 10 per workflow

## Tool execution safety (locked)

- Pattern: Hybrid MCP + Direct tools
- Required direct tools: `list_deals`, `get_deal`, `transition_deal`, `check_health`
- Permission tiers: READ / WRITE / CRITICAL
- Idempotency for WRITE/CRITICAL: claim-first insert-before-execute
- Pydantic validation on all tool calls
- Tool calls logged to audit_log

## Storage + queue + retrieval (locked)

- Storage: Postgres + pgvector
- Queue: Postgres SKIP LOCKED; backoff 30s × 2^attempt; max attempts=3; DLQ required
- Queue targets: queue depth warn >50; critical >100; P95 claim latency <100ms under load
- Retrieval:
  - Embeddings: BGE-M3 (1024)
  - Quality DoD: recall@5 ≥ 0.8
  - Single retrieval path (no split-brain)

### Retrieval rule (Agent API specific; must not drift)

From `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`:
- Agent API retrieval is **exclusively via RAG REST :8052**.
- Agent API must not query pgvector directly.

## Observability (locked)

- Langfuse self-hosted + OpenTelemetry
- Never log raw prompts/responses (hash + length only)
- Retention: 30 days

## Security / RBAC (locked)

- Auth: JWT primary + API key fallback (`X-API-Key`)
- JWT HS256 required claims: `sub`, `role`, `exp`, `iss`, `aud`
- Issuer: `zakops-auth`; Audience: `zakops-agent`
- Roles: VIEWER / OPERATOR / APPROVER / ADMIN
- Default deny
- API keys stored as SHA256 hash
- All auth attempts logged

## LLM routing / cloud egress (locked)

From `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`:
- Routing: LiteLLM gateway (deterministic)
- Fallback chain: `local-primary → cloud-claude`
- Cloud egress policy:
  - BLOCKED fields: `ssn`, `tax_id`, `bank_account`, `credit_card`
  - ALLOWED conditions only: `context_overflow`, `local_model_error`, `explicit_user_request`, `complexity_threshold`
- Constraints:
  - Daily budget: `$50` max
  - ≥80% tasks handled locally
  - PII redaction before any cloud send

## Container networking constraint (authoritative)

From `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`:
- In container mode, **never use `localhost`** to reach host services.
- Use `host.docker.internal` for host-services mode (Deal API, vLLM, MCP, RAG REST, Langfuse).

---

# Unified Phase Plan (0–8)

This roadmap uses the unified phase index requested. A mapping to Decision Lock “Phase 1/2/3” checklists is included in Appendix → Decision Log.

## Phase 0 — Foundations & Alignment (Baseline preservation + contract locking)

### Entry criteria
- Access to `/home/zaks/zakops-agent-api`
- Able to run the baseline gate pack once: `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh` (exit 0)

### Required prior artifacts (baseline snapshot; by filename)
- `gate_artifacts/health.json`
- `gate_artifacts/invoke_hitl.json`
- `gate_artifacts/approve.json`
- `gate_artifacts/approve_again.json`
- `gate_artifacts/db_invariants.sql.out`
- `gate_artifacts/checkpoint_kill9_test.log`
- `gate_artifacts/concurrent_approves.log`
- `gate_artifacts/tool_call_validation_test.log`
- `gate_artifacts/dependency_licenses.json`
- `gate_artifacts/mock_safety_test.log`
- `gate_artifacts/streaming_test.log`
- `gate_artifacts/streaming_hitl_test.log`
- `gate_artifacts/hitl_scope_test.log`
- `gate_artifacts/auth_negative_tests.json`
- `gate_artifacts/run.log`

### Objective
- Freeze the HITL spike as non-regressable baseline.
- Lock contracts early to prevent drift in endpoints, status strings, tool names, and artifact naming.

### Scope IN
- Baseline pack remains green (BL-01..BL-14).
- Create/lock a **Contract Lock Pack** (written artifacts, generated by `bring_up_tests.sh`):
  - Canonical Agent API base path and endpoints
  - Canonical status strings (`awaiting_approval`, `completed`, `error`)
  - Tool names and permission tiers (READ/WRITE/CRITICAL)
  - Artifact directory and required filenames
- Lock the **local-first vLLM lane** as an explicit, deterministic sub-gate:
  - vLLM health endpoint returns 200
  - served model id matches Decision Lock (Qwen2.5-32B-Instruct-AWQ)
- Add `PORTS.md` as authoritative (if missing) and implement lints:
  - `PORTS.md` presence + expected port values
  - Env “no localhost in container mode” lint
- Standardize artifact bundling:
  - `bring_up_tests.sh` must produce a phase bundle zip containing gate artifacts plus the active Builder/QA reports paths (if provided as env vars).
- Add a **gate registry + dependency lint** (machine-readable) so future phases cannot reference “paper artifacts”:
  - Registry enumerates gates, artifacts, PASS markers, and phase ownership for the artifacts implemented so far.
  - Lint fails if the registry references missing artifacts or missing PASS markers.

### Scope OUT
- No new features beyond contract/lint/bundling.

### Deliverables
- Repo docs:
  - `/home/zaks/zakops-agent-api/PORTS.md` (authoritative ports)
  - `/home/zaks/zakops-agent-api/docs/contracts/CONTRACTS.md` (human-readable contract summary)
- Gate artifacts (must be produced by `bring_up_tests.sh`):
  - `gate_artifacts/contract_snapshot.json` (Agent API endpoints + statuses + schema keys)
  - `gate_artifacts/vllm_lane_verify.json` (vLLM health + model id contract)
  - `gate_artifacts/ports_md_lint.log` (PASS marker)
  - `gate_artifacts/env_no_localhost_lint.log` (PASS marker)
  - `gate_artifacts/artifact_bundle.zip` (or timestamped bundle; naming locked in contracts)
  - `gate_artifacts/gate_registry.json` (machine-readable gate+artifact registry for implemented gates)
  - `gate_artifacts/gate_registry_lint.log` (PASS marker)

### Dependencies
- None beyond baseline.

### Risks & mitigations
- Risk: API/status naming drift causes silent client breakage.
  - Mitigation: contract snapshot gate fails on drift; schema snapshots are versioned.
- Risk: “paper gates” reintroduced.
  - Mitigation: contract explicitly bans scattered commands; only bring_up_tests.sh is the gate runner.

### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- Baseline BL-01..BL-14 still PASS.
- New Phase 0 artifacts exist and contain PASS markers:
  - `contract_snapshot.json` present and validates canonical `/agent/*` endpoints and `awaiting_approval` status string.
  - `vllm_lane_verify.json` present and `status == "PASSED"` with expected model id.
  - `ports_md_lint.log` contains `PORTS_MD_LINT: PASSED`
  - `env_no_localhost_lint.log` contains `ENV_NO_LOCALHOST: PASSED`
  - artifact bundle exists and includes the baseline artifacts.
  - `gate_registry.json` present and includes Phase 0 + baseline entries.
  - `gate_registry_lint.log` contains `GATE_REGISTRY_LINT: PASSED`

### Rollback plan (Phase 0 changes)
- Revert contract snapshot expectations to match Decision Lock + QA report only (no project-specific drift).

---

## Phase 1 — Core Infrastructure & Architecture (MVP wiring + observability + stop-ship closure)

### Entry criteria
- Phase 0 PASS (baseline + contracts locked).

### Required prior artifacts (Phase 0 outputs; by filename)
- `gate_artifacts/contract_snapshot.json`
- `gate_artifacts/vllm_lane_verify.json`
- `gate_artifacts/ports_md_lint.log`
- `gate_artifacts/env_no_localhost_lint.log`
- `gate_artifacts/artifact_bundle.zip` (or timestamped equivalent per contracts)
- `gate_artifacts/gate_registry.json`
- `gate_artifacts/gate_registry_lint.log`

### Objective
- Close Stop‑Ship security risks with enforceable gates:
  - plaintext at rest
  - raw content leakage
- Deploy observability that meets Decision Lock (self-hosted Langfuse :3001) and prove trace coverage.

### Scope IN
1) **At-rest protection** (checkpoint + workflow persistence) with rollback:

   - Implement `SecurePostgresSaver` (AES-256-GCM) or equivalent wrapper that encrypts checkpoint payloads.

   - Encryption scope MUST include both:

     - `checkpoint_blobs` (payload blobs)

     - `checkpoint_writes` (channel values)

   - Key management v1:

     - `CHECKPOINT_ENCRYPTION_KEY` env var

     - no default value

     - format validation (32 bytes / 256-bit)

     - **fail start** in production exposure mode if key missing/invalid

2) **Crypto migration plan**:

   - Backfill/re-encrypt existing plaintext rows.

   - Include rollback strategy (restore DB backup; disable encryption wrapper only if data loss risk is controlled).

3) **No-raw-content enforcement** as gates (not prose):

   - Deterministic canary injection.

   - Deterministic scans across:

     - docker logs

     - Langfuse trace exports

     - DB sample rows from relevant tables

   - Explicit exclusions list (IDs allowed; raw user/doc text forbidden).

   - Fail-closed behavior for production exposure.

4) **Langfuse self-hosted** spec + verification:

   - Provide compose or infra method to run Langfuse at :3001.

   - Gate must verify:

     - `GET http://localhost:3001/api/public/health` returns 2xx

     - At least one trace is created for a defined workflow

     - No raw content appears in the trace export

5) **Resilience contract** for external services (tool gateway):

   - Define and implement timeouts/retries/backoff/circuit breakers for Deal API, RAG REST, MCP.

   - Record config snapshot as an artifact.


### Scope OUT
- Real-service E2E deal transition validation (Phase 2).
- RAG integration and evals (Phase 3).
- MCP expansion + routing policies (Phase 4).
- Queue/DLQ (Phase 5).

### Deliverables
- Code (agent repo):

  - Encryption wrapper + key validation + backfill tooling

  - Raw-content redaction boundary (logs/traces) + scanners

  - Langfuse self-host deployment artifacts (compose/instructions)

  - External service resilience configuration

- Docs:

  - `/home/zaks/zakops-agent-api/docs/security/AT_REST_PROTECTION.md`

  - `/home/zaks/zakops-agent-api/docs/observability/LANGFUSE_SELF_HOST.md`

  - `/home/zaks/zakops-agent-api/docs/runbooks/KEY_ROTATION.md` (manual until Vault)


### Dependencies
- Infra support to run Langfuse self-hosted on :3001.

- DB backup capability before applying crypto/backfill migrations.


### Risks & mitigations
- Risk: encryption breaks PostgresSaver semantics (crash recovery / resume fails).

  - Mitigation: run BL-07 kill‑9 gate and BL-06 concurrency gate after enabling encryption; Phase 1 FAIL if regression.

- Risk: “redaction reduces debuggability”.

  - Mitigation: log structured metadata (IDs, hashes, lengths) + allow explicit local-only secure debug mode guarded by env var and blocked in production exposure mode.


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD (objective, testable)
- Baseline BL-01..BL-14 PASS.

- New Phase 1 artifacts exist and PASS:

  - `gate_artifacts/encryption_verify.log` contains `ENCRYPTION_VERIFY: PASSED`

  - `gate_artifacts/kill9_encrypted.log` contains `KILL9_ENCRYPTED: PASSED`

  - `gate_artifacts/pii_canary_report.json` contains `PII_CANARY: PASSED`

  - `gate_artifacts/raw_content_scan.log` contains `RAW_CONTENT_SCAN: PASSED`

  - `gate_artifacts/secrets_hygiene_lint.log` contains `SECRETS_HYGIENE: PASSED`

  - `gate_artifacts/langfuse_selfhost_gate.log` contains `LANGFUSE_SELFHOST: PASSED`

  - `gate_artifacts/resilience_config_snapshot.json` exists

- Production exposure fail-closed behavior validated:

  - If `PRODUCTION_EXPOSURE=true` and `CHECKPOINT_ENCRYPTION_KEY` missing/invalid → agent refuses to start and writes `gate_artifacts/prod_exposure_fail_closed.log` containing `PROD_EXPOSURE_FAIL_CLOSED: PASSED`.


### Rollback plan (Phase 1 crypto changes)
- Precondition: DB backup taken and recorded.

- Rollback path:

  - Stop agent

  - Restore DB backup

  - Revert encryption wrapper changes

  - Re-run baseline gate pack


---

## Phase 2 — MVP Build (real-service E2E + UI/API contract proof + disable mocks)

### Entry criteria
- Phase 1 PASS (security/observability/at-rest controls proven).

- Deal API reachable.

- vLLM reachable.

### Required prior artifacts (Phase 1 outputs; by filename)
- `gate_artifacts/encryption_verify.log`
- `gate_artifacts/kill9_encrypted.log`
- `gate_artifacts/pii_canary_report.json`
- `gate_artifacts/raw_content_scan.log`
- `gate_artifacts/langfuse_selfhost_gate.log`
- `gate_artifacts/resilience_config_snapshot.json`


### Objective
- Prove the MVP works end-to-end against real services with mocks disabled.

- Prove UI can consume streaming + approvals without drifting contracts.


### Scope IN
1) **Contract probes (stop guessing routes)**

   - Implement a contract probe gate that resolves:

     - Deal API base path (`/deals` vs `/api/v1/deals`) and minimal schema

     - Agent API canonical prefix (`/agent/*`) and schema/status strings

   - Gate writes JSON artifacts and also writes a generated `repro_commands.sh` with placeholders.

2) **Disable mocks for MVP acceptance**

   - Enforce `ALLOW_TOOL_MOCKS=false` (or equivalent) and fail if any mock path is exercised.

   - Gate emits `mocks_disabled_check.log`.

3) **Direct tools wired to Deal API** (MVP-critical)

   - `list_deals`, `get_deal`, `transition_deal`, `check_health` executed via tool gateway.

4) **E2E HITL lifecycle path**

   - invoke → `awaiting_approval` → approve → `completed` → Deal API state changed

   - Must record exactly-once semantics in `tool_executions`.

5) **Frontend integration (ZakOps Next.js)**

   - UI uses canonical `/agent/*` endpoints.

   - UI supports:

     - invoke

     - stream

     - list approvals

     - approve/reject

   - Add an automated smoke flow (Playwright or equivalent) OR, if not possible, a minimal scripted check that captures HTTP traces as artifacts.

6) **Cloudflare routing constraint**

   - Cloudflare tunnel routes only to :8095. Add a config lint gate to ensure it does not expose :8090.


### Scope OUT
- RAG integration (Phase 3).

- MCP expansion (Phase 4).

- Queue/DLQ (Phase 5).

### Deliverables
- Gate artifacts (Phase 2 outputs):
  - `gate_artifacts/agent_api_contract.json`
  - `gate_artifacts/deal_api_contract.json`
  - `gate_artifacts/repro_commands.sh`
  - `gate_artifacts/mocks_disabled_check.log`
  - `gate_artifacts/deal_api_e2e_transition.json`
  - `gate_artifacts/ui_smoke_test.log` (or `gate_artifacts/ui_smoke_trace.json`)
  - `gate_artifacts/cloudflare_route_lint.log`
- Code/Docs (minimal, production-leaning):
  - Deal API adapter + tool gateway uses real HTTP (no mocks for Phase 2 acceptance)
  - UI integration notes under contracts (canonical `/agent/*` endpoints; auth expectations)
  - Cloudflare routing constraint documented + linted


### Dependencies
- Deal API auth semantics may differ; must be discovered by contract probe.


### Risks & mitigations
- Risk: auth mismatch between Agent API and Deal API.

  - Mitigation: Deal API auth probe + explicit adapter design documented.

- Risk: UI builds against unstable contract.

  - Mitigation: Phase 0 contract lock pack + Phase 2 contract probe gate; UI tests fail on drift.


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- Phase 1 artifacts remain PASS.

- New Phase 2 artifacts exist and PASS:

  - `gate_artifacts/agent_api_contract.json`

  - `gate_artifacts/deal_api_contract.json`

  - `gate_artifacts/repro_commands.sh`

  - `gate_artifacts/mocks_disabled_check.log` contains `MOCKS_DISABLED: PASSED`

  - `gate_artifacts/deal_api_e2e_transition.json` contains `E2E_TRANSITION: PASSED`

  - `gate_artifacts/ui_smoke_test.log` contains `UI_SMOKE: PASSED` (or `ui_smoke_trace.json`)

  - `gate_artifacts/cloudflare_route_lint.log` contains `CLOUDFLARE_ROUTE_LINT: PASSED`
- E2E requires real Deal API state verification (captured in `deal_api_e2e_transition.json`).


### Rollback plan
- If tool wiring breaks production invariants, revert wiring changes and re-run baseline gates.


---

## Phase 3 — Intelligence / Agent Capabilities (RAG integration + eval harness + tool accuracy)

### Entry criteria
- Phase 2 PASS (real-service MVP stable; mocks disabled).

- RAG REST reachable.

### Required prior artifacts (Phase 2 outputs; by filename)
- `gate_artifacts/agent_api_contract.json`
- `gate_artifacts/deal_api_contract.json`
- `gate_artifacts/repro_commands.sh`
- `gate_artifacts/mocks_disabled_check.log`
- `gate_artifacts/deal_api_e2e_transition.json`
- `gate_artifacts/ui_smoke_test.log` (or `gate_artifacts/ui_smoke_trace.json`)
- `gate_artifacts/cloudflare_route_lint.log`


### Objective
- Add retrieval and “agent intelligence” under measurable evals.


### Scope IN
1) **RAG REST contract probe + lock**

   - Discover and lock RAG REST endpoints/schema via probe (including OpenAPI if available).

   - Write `rag_rest_contract.json` and update contract lock pack.

2) **RAG integration rule**

   - All retrieval via RAG REST only.

   - Add a static scan gate to fail if Agent queries pgvector directly.

3) **Eval dataset management**

   - Define dataset storage path and versioning:

     - `evals/datasets/<name>/<version>/...`

   - Add `eval_dataset_manifest.json` describing provenance, size, allowed data (no secrets).

4) **Tool accuracy eval (≥95% on 50 prompts)**

   - Define “tool accuracy” precisely:

     - correct tool selection

     - schema-valid args

     - expected side effect (when applicable)

     - idempotency behavior (no duplicate exec)

   - Output `tool_accuracy_eval.json` with per-tool breakdown and error taxonomy.

5) **Retrieval eval (recall@5 ≥ 0.80)**

   - Output `retrieval_eval_results.json` including dataset version and latency stats.

6) **Reranker rubric**

   - Adopt reranker only if MRR uplift ≥10% AND within latency budget; record decision.


### Scope OUT
- Hybrid routing (Phase 4).

- Queue/DLQ (Phase 5).

### Deliverables
- Gate artifacts (Phase 3 outputs):
  - `gate_artifacts/rag_rest_contract.json`
  - `gate_artifacts/eval_dataset_manifest.json`
  - `gate_artifacts/tool_accuracy_eval.json`
  - `gate_artifacts/retrieval_eval_results.json`
  - `gate_artifacts/no_split_brain_retrieval_scan.log`
- Code/Docs:
  - RAG REST client integration (Agent API retrieves only via :8052)
  - Eval harness with versioned datasets (append-only trend added in Phase 6)
  - Retrieval policy documentation (no split-brain)


### Dependencies
- Stable eval datasets and ability to run eval harness locally.


### Risks & mitigations
- Risk: evals not representative.

  - Mitigation: define coverage requirements; expand dataset via controlled change process; keep historical trend artifacts.


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- New Phase 3 artifacts exist and PASS:

  - `gate_artifacts/rag_rest_contract.json`

  - `gate_artifacts/eval_dataset_manifest.json`

  - `gate_artifacts/tool_accuracy_eval.json` meets ≥95% threshold

  - `gate_artifacts/retrieval_eval_results.json` meets recall@5 ≥0.80

  - `gate_artifacts/no_split_brain_retrieval_scan.log` contains `NO_SPLIT_BRAIN: PASSED`

### Rollback plan
- If retrieval/evals break baseline invariants or safety gates:
  - Disable retrieval path (local-only) and revert to last known-good contract snapshot
  - Re-run baseline gate pack and Phase 2 E2E gate


---

## Phase 4 — Tooling + Integrations (MCP optional, routing policies, cost controls)

### Entry criteria
- Phase 3 PASS for routing/cost work.

- Phase 2 PASS is sufficient for MCP-only work.

### Required prior artifacts (Phase 3 outputs; by filename)
- `gate_artifacts/rag_rest_contract.json`
- `gate_artifacts/eval_dataset_manifest.json`
- `gate_artifacts/tool_accuracy_eval.json`
- `gate_artifacts/retrieval_eval_results.json`
- `gate_artifacts/no_split_brain_retrieval_scan.log`


### Objective
- Add optional integrations safely without compromising core reliability.


### Scope IN
1) **MCP client (optional; never core-critical)**

   - Implement MCP client contract:

     - initialize

     - tools/list

     - tools/call

   - Error normalization and tool namespace mapping rules.

   - Conformance test emits `mcp_conformance.json`.

2) **Hybrid routing policies (LiteLLM) + cost controls**

   - Enforce blocked-field policy for cloud egress.

   - Enforce explicit allow conditions.

   - Implement daily budget cap $50 and cost accounting per day and per thread.

   - Emit `routing_policy_tests.json`, `cost_report.json`, `policy_config_snapshot.json`.

3) **Local-handling rate measurement**

   - Measure ≥80% tasks handled locally on a defined workflow set.

   - Emit `local_percent_report.json`.


### Scope OUT
- Queue/DLQ + chaos/soak (Phase 5).

### Deliverables
- Gate artifacts (Phase 4 outputs; conditional where noted):
  - `gate_artifacts/mcp_conformance.json` (if MCP enabled)
  - `gate_artifacts/routing_policy_tests.json`
  - `gate_artifacts/policy_config_snapshot.json`
  - `gate_artifacts/cost_report.json`
  - `gate_artifacts/local_percent_report.json`
- Code/Docs:
  - MCP client adapter with error normalization + namespace mapping rules (optional)
  - LiteLLM routing policy implementation (blocked fields + allow conditions + deterministic routing)
  - Cost accounting schema (per thread + per day) and budget enforcement

### Dependencies
- If MCP enabled: MCP server reachable at :9100 with initialize/tools/list/tools/call.
- If cloud routing enabled: cloud credentials supplied via secrets (never committed) + explicit `PRODUCTION_EXPOSURE` policy enforcement.


### Risks & mitigations
- Risk: accidental cloud exfiltration.

  - Mitigation: default deny; blocked-field tests; canary tokens; fail closed.


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- MCP conformance PASS (if MCP enabled): `gate_artifacts/mcp_conformance.json`.

- Routing policies PASS: `gate_artifacts/routing_policy_tests.json`.

- Budget enforcement PASS: `gate_artifacts/cost_report.json`.

- Local handling rate ≥80% recorded: `gate_artifacts/local_percent_report.json`.

### Rollback plan
- If routing/MCP introduces risk or instability:
  - Disable MCP adapter and/or cloud routing (default to local-only)
  - Re-run baseline gates and Phase 2 E2E gates before re-enabling


---

## Phase 5 — Hardening, Security, Reliability (queue/DLQ, chaos, audit immutability, key mgmt)

### Entry criteria
- Phase 2 PASS minimum.

- Prefer Phase 3 PASS for richer workloads.

### Required prior artifacts (Phase 2 outputs; by filename)
- `gate_artifacts/agent_api_contract.json`
- `gate_artifacts/deal_api_contract.json`
- `gate_artifacts/mocks_disabled_check.log`
- `gate_artifacts/deal_api_e2e_transition.json`

### Optional prior artifacts (if Phase 4 work is enabled; by filename)
- `gate_artifacts/mcp_conformance.json` (if MCP is enabled)
- `gate_artifacts/routing_policy_tests.json` (if cloud routing is enabled)
- `gate_artifacts/cost_report.json` (if cloud routing is enabled)
- `gate_artifacts/policy_config_snapshot.json` (if cloud routing is enabled)
- `gate_artifacts/local_percent_report.json` (if cloud routing is enabled)


### Objective
- Make reliability claims provable: durable background execution, chaos resilience, audit immutability, secrets hygiene.


### Scope IN
1) **Queue + DLQ (Postgres SKIP LOCKED)**

   - Implement schema + worker loop + retry policy per Decision Lock.

   - Load test under defined profile; record P95 claim latency.

2) **Chaos hardening**

   - kill -9 mid-workflow and resume.

   - concurrency headroom test (N=50) is additive evidence; baseline N=20 remains mandatory.

3) **Audit immutability**

   - Enforce at DB level: UPDATE/DELETE denied.

   - Gate proves immutability.

4) **Secrets hygiene / unsafe defaults**

   - No default JWT secret accepted in production exposure mode.

   - No enabling mocks in production exposure mode.

   - Gate fails closed if defaults detected.

5) **Rate limiting + request size limits (Agent API)**

   - Required before external exposure (Cloudflare).

### Deliverables
- Gate artifacts (Phase 5 outputs):
  - `gate_artifacts/queue_worker_smoke.log`
  - `gate_artifacts/queue_load_test.json`
  - `gate_artifacts/chaos_kill9.log`
  - `gate_artifacts/concurrency_n50.log` (additive)
  - `gate_artifacts/audit_immutability_test.log`
  - `gate_artifacts/secrets_hygiene_lint.log`
  - `gate_artifacts/rate_limit_test.log`
- Code/Docs:
  - Postgres SKIP LOCKED queue schema + worker loop + DLQ
  - Retry/backoff policy + idempotency integration for side-effecting tasks
  - Audit immutability DB constraints + runbook for audit review
  - Rate limiting + request size limits (documented, configurable)

### Risks & mitigations
- Risk: retries or worker concurrency create duplicate side effects.
  - Mitigation: idempotency keys for all WRITE/CRITICAL operations; DLQ after max attempts; chaos+load gates must prove “exactly once”.
- Risk: rate limiting causes false negatives for legitimate clients.
  - Mitigation: conservative defaults; explicit allowlist; always measure and record `429` rates in artifacts.
- Risk: audit immutability blocks necessary operational workflows.
  - Mitigation: design audit_log as append-only with compensating events; never UPDATE/DELETE; provide operator tooling to interpret.


### Dependencies
- DB migrations require backup + rollback plan.


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- Queue artifacts PASS:

  - `gate_artifacts/queue_worker_smoke.log` contains `QUEUE_WORKER_SMOKE: PASSED`

  - `gate_artifacts/queue_load_test.json` records P95 claim latency <100ms under defined load

- Chaos artifacts PASS:

  - `gate_artifacts/chaos_kill9.log` contains `CHAOS_KILL9: PASSED`

  - `gate_artifacts/concurrency_n50.log` contains `CONCURRENCY_N50: PASSED` (additive)

- Audit immutability PASS:

  - `gate_artifacts/audit_immutability_test.log` contains `AUDIT_IMMUTABILITY: PASSED`

- Secrets hygiene PASS:

  - `gate_artifacts/secrets_hygiene_lint.log` contains `SECRETS_HYGIENE: PASSED`

- Rate limiting PASS:

  - `gate_artifacts/rate_limit_test.log` contains `RATE_LIMIT: PASSED`


### Rollback plan (schema changes)

- Pre-migration DB backup.

- Migration scripts must support rollback or restore procedure.


---

## Phase 6 — Evaluation, Red‑Team, QA (formal evals, adversarial, regression CI)

### Entry criteria
- Phase 3 PASS minimum.

- Prefer Phase 5 PASS for reliability/security posture.

### Required prior artifacts (Phase 3 outputs; by filename)
- `gate_artifacts/tool_accuracy_eval.json`
- `gate_artifacts/retrieval_eval_results.json`
- `gate_artifacts/eval_dataset_manifest.json`

### Optional prior artifacts (if Phase 5 is complete; by filename)
- `gate_artifacts/queue_load_test.json`
- `gate_artifacts/audit_immutability_test.log`
- `gate_artifacts/secrets_hygiene_lint.log`
- `gate_artifacts/rate_limit_test.log`


### Objective
- Formalize QA and red-team so correctness and safety do not regress.


### Scope IN
1) **CI gate runner**

   - Run `./scripts/bring_up_tests.sh` in CI mode.

   - Retain artifacts and publish summary.

2) **Adversarial suites**

   - Prompt injection attempts

   - Tool-arg manipulation

   - Role escalation attempts

   - Data exfil attempts (cloud routing)

3) **Regression tracking**

   - Store eval trends (tool accuracy + retrieval metrics + latency).

### Scope OUT
- No new runtime features; only verification, CI automation, and adversarial testing harnesses.

### Deliverables
- Gate artifacts (Phase 6 outputs):
  - `gate_artifacts/ci_gate_run.log`
  - `gate_artifacts/redteam_report.json`
  - `gate_artifacts/eval_trend.csv`
- Code/Docs:
  - CI workflow that runs `bring_up_tests.sh` in CI mode and uploads artifacts
  - Red-team suite (prompt injection, tool arg manipulation, role escalation, exfil attempts) with deterministic reports
  - Eval methodology doc (how prompts/datasets are versioned; how failures are triaged)

### Dependencies
- CI runner with Docker (or equivalent) capable of running the agent stack and `bring_up_tests.sh`.
- Artifact retention policy defined (minimum retention >= 30 days) for CI evidence bundles.

### Risks & mitigations
- Risk: CI flakiness creates false negatives or “retry until green” behavior.
  - Mitigation: deterministic seeding; separate “infra flaky” vs “spec failure” categories; treat repeated flake as Stop‑Ship until fixed.
- Risk: red-team suite becomes non-representative.
  - Mitigation: require versioned red-team cases + quarterly refresh; keep historical trend artifacts.

### Rollback plan
- If CI/red-team automation blocks progress due to infra issues:
  - Fix infra (preferred) rather than bypassing gates.
  - Temporary bypass requires explicit Security+QA sign-off and must be recorded as a tracked exception with an expiry.


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- CI artifacts exist:

  - `gate_artifacts/ci_gate_run.log` contains `CI_GATES: PASSED`

- Red-team suite PASS:

  - `gate_artifacts/redteam_report.json` contains `REDTEAM: PASSED`

- Eval trend artifacts updated:

  - `gate_artifacts/eval_trend.csv` (or JSON) updated with new run.


---

## Phase 7 — Deployment, Monitoring, Operations (backups, rollbacks, runbooks, incident response)

### Entry criteria
- Phase 5 PASS minimum.

- Prefer Phase 6 PASS.

### Required prior artifacts (Phase 5 outputs; by filename)
- `gate_artifacts/queue_load_test.json`
- `gate_artifacts/chaos_kill9.log`
- `gate_artifacts/audit_immutability_test.log`
- `gate_artifacts/secrets_hygiene_lint.log`
- `gate_artifacts/rate_limit_test.log`

### Optional prior artifacts (if Phase 6 is complete; by filename)
- `gate_artifacts/ci_gate_run.log`
- `gate_artifacts/redteam_report.json`
- `gate_artifacts/eval_trend.csv`


### Objective
- Make production exposure safe and operable with runbooks, backups, monitoring, and release gates.


### Scope IN
- Runbooks:

  - startup/shutdown

  - key rotation

  - backup/restore

  - stuck approval triage

  - suspected double execution triage

- Monitoring spec:

  - required metrics

  - alert thresholds

  - dashboards

- Backup/restore drill (must be executed and logged).

- Release readiness Go/No-Go checklist defined and enforced.

### Scope OUT
- No scaling/optimization work (Phase 8).
- No new agent capabilities; focus is operability and safe exposure.

### Deliverables
- Gate artifacts (Phase 7 outputs):
  - `gate_artifacts/runbook_lint.log`
  - `gate_artifacts/backup_restore_drill.log`
  - `gate_artifacts/monitoring_smoke.log`
  - `gate_artifacts/release_readiness_check.json`
- Docs/Runbooks (authoritative, versioned):
  - startup/shutdown
  - key rotation
  - backup/restore
  - stuck approval triage
  - suspected double execution triage
- Monitoring:
  - dashboards + alert thresholds documented and exported (format TBD; must be reproducible)

### Dependencies
- Infra access to monitoring stack and the host where services run.
- Ability to perform and log a DB backup + restore drill (non-destructive environment).

### Risks & mitigations
- Risk: runbooks diverge from reality.
  - Mitigation: runbook lint gate + quarterly restore drill + incident postmortem updates.
- Risk: backup/restore drill is treated as optional.
  - Mitigation: Stop‑Ship if `backup_restore_drill.log` is missing or fails.

### Rollback plan
- If operability gates fail or external exposure introduces risk:
  - Disable external exposure (Cloudflare routing off) and return to lab-only mode
  - Restore last known-good deployment configuration and re-run the gate pack


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- `gate_artifacts/backup_restore_drill.log` contains `BACKUP_RESTORE: PASSED`

- `gate_artifacts/runbook_lint.log` contains `RUNBOOK_LINT: PASSED`

- `gate_artifacts/monitoring_smoke.log` contains `MONITORING_SMOKE: PASSED`

- `gate_artifacts/release_readiness_check.json` contains `RELEASE_READY: PASSED`


---

## Phase 8 — Scaling, Optimization, Continuous Improvement (perf, throughput, migration triggers, continuous gates)

### Entry criteria
- Phase 7 PASS.

### Required prior artifacts (Phase 7 outputs; by filename)
- `gate_artifacts/backup_restore_drill.log`
- `gate_artifacts/runbook_lint.log`
- `gate_artifacts/monitoring_smoke.log`
- `gate_artifacts/release_readiness_check.json`


### Objective
- Optimize only after safety/correctness is stable; measure everything; enforce migration triggers.


### Scope IN
- Benchmark suite (record hardware signature):

  - vLLM tok/s baseline

  - Agent API latency P50/P95

  - tool call latency P95

  - retrieval latency P95

  - queue throughput

- Migration trigger monitoring:

  - pgvector → Qdrant triggers

  - Postgres queue → Redis triggers

  - model upgrade trigger

- Continuous cadence:

  - weekly eval refresh

  - monthly red-team rerun

  - quarterly restore drill

### Scope OUT
- No safety-reducing optimizations (never trade confidentiality/auditability for speed).
- No cross-service scaling beyond what is measurable on the single-host profile unless explicitly approved.

### Deliverables
- Gate artifacts (Phase 8 outputs):
  - `gate_artifacts/benchmarks.json`
  - `gate_artifacts/migration_trigger_status.json`
  - `gate_artifacts/ci_cadence_schedule.md`
- Docs:
  - Performance budgets (latency, throughput) and measurement methodology
  - Migration trigger definitions (what metrics/thresholds are used and where they are computed)

### Dependencies
- Stable monitoring/metrics from Phase 7 (otherwise benchmarks cannot be trusted).
- Ability to run benchmark workloads without impacting production data (use test fixtures only).

### Risks & mitigations
- Risk: benchmarks are noisy and lead to incorrect decisions.
  - Mitigation: record hardware signature; fixed seeds; run N>=5 trials and report variance; store artifacts for trend.
- Risk: optimization breaks non-negotiable invariants.
  - Mitigation: baseline gates run first and must stay green; optimizations never bypass gates.

### Rollback plan
- If optimization/scale work regresses any baseline invariant:
  - Revert to last known-good config/code (tagged “green”)
  - Re-run baseline + Phase 2 E2E gates to confirm recovery


### Acceptance gate (single command)
```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

### Exit criteria / DoD
- `gate_artifacts/benchmarks.json` contains `BENCHMARKS: PASSED`

- `gate_artifacts/migration_trigger_status.json` present and correctly computed

- `gate_artifacts/ci_cadence_schedule.md` present


---

# Work Breakdown (MECE backlog)

All tasks must be Lab Loop compatible. Every task lists:
- Owner role (Builder/QA/Infra/Security)
- Repo/path
- Acceptance criteria
- Gate cmd (always canonical)
- Artifacts emitted

## Backlog table

| task_id | Phase | Owner | Repo/Path | Acceptance criteria (objective) | Gate cmd | Artifacts emitted (deterministic) |
|---|---:|---|---|---|---|---|
| P0-CONTRACT-001 | 0 | QA | `scripts/bring_up_tests.sh` | Contract probe implemented; contract snapshot validates `/agent/*` + status strings | `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh` | `contract_snapshot.json`, `agent_api_contract.json` |
| P0-PORTS-001 | 0 | Builder | `PORTS.md` + `scripts/bring_up_tests.sh` | PORTS.md exists; lint passes; ports match Decision Lock | (canonical) | `ports_md_lint.log` |
| P0-ENV-001 | 0 | Builder | env files + `scripts/bring_up_tests.sh` | No `localhost` in container-mode env; uses `host.docker.internal` | (canonical) | `env_no_localhost_lint.log` |
| P0-BUNDLE-001 | 0 | QA | `scripts/bring_up_tests.sh` | Artifact bundle zip created per run | (canonical) | `artifact_bundle.zip` |
| P0-VLLM-001 | 0 | Infra | vLLM service on :8000 | vLLM `/health` returns 200 and `/v1/models` includes Qwen2.5 AWQ; gate artifact emitted | (canonical) | `vllm_lane_verify.json` |
| P0-REGISTRY-001 | 0 | Builder | `scripts/bring_up_tests.sh` | gate registry written and linted; fails if artifacts/PASS markers missing | (canonical) | `gate_registry.json`, `gate_registry_lint.log` |
| P1-ENC-001 | 1 | Builder | saver wrapper + DB | AES-256-GCM at-rest protection implemented (blobs + writes) | (canonical) | `encryption_verify.log`, `kill9_encrypted.log` |
| P1-KEY-001 | 1 | Security | config | No default key; production exposure fails closed | (canonical) | `secrets_hygiene_lint.log`, `prod_exposure_fail_closed.log` |
| P1-RAW-001 | 1 | Security | logging/tracing | Raw content scanners pass; canary absent | (canonical) | `pii_canary_report.json`, `raw_content_scan.log` |
| P1-LANGFUSE-001 | 1 | Infra | Langfuse stack | Self-hosted :3001 healthy and traces visible | (canonical) | `langfuse_selfhost_gate.log` |
| P1-RESILIENCE-001 | 1 | Builder | resilience config | timeouts/retries/backoff/circuit breakers defined and snapshot emitted | (canonical) | `resilience_config_snapshot.json` |
| P2-DEAL-PROBE-001 | 2 | QA | contract probe | Deal API base path + schema locked | (canonical) | `deal_api_contract.json`, `repro_commands.sh` |
| P2-MOCKS-001 | 2 | QA | tool gateway | Mocks disabled and verified | (canonical) | `mocks_disabled_check.log` |
| P2-E2E-001 | 2 | QA | e2e test | HITL transition changes Deal API state; exactly-once proven | (canonical) | `deal_api_e2e_transition.json` |
| P2-CLOUDFLARE-001 | 2 | Security | Cloudflare config lint | Cloudflare tunnel routes only to :8095 (not :8090); lint PASS | (canonical) | `cloudflare_route_lint.log` |
| P2-UI-001 | 2 | Builder | Next.js repo (TBD) | UI smoke flow passes against canonical endpoints | (canonical) | `ui_smoke_test.log` |
| P3-RAG-PROBE-001 | 3 | QA | RAG probe | RAG REST contract locked | (canonical) | `rag_rest_contract.json` |
| P3-EVAL-001 | 3 | QA | eval harness | tool accuracy ≥95% on 50 prompts | (canonical) | `tool_accuracy_eval.json`, `eval_dataset_manifest.json` |
| P3-EVAL-002 | 3 | QA | eval harness | recall@5 ≥0.80 | (canonical) | `retrieval_eval_results.json` |
| P3-NO-SPLITBRAIN-001 | 3 | Security | static scan gate | Agent API has no direct pgvector retrieval; scan PASS | (canonical) | `no_split_brain_retrieval_scan.log` |
| P4-MCP-001 | 4 | Builder | MCP client | MCP conformance PASS; errors normalized | (canonical) | `mcp_conformance.json` |
| P4-ROUTE-001 | 4 | Security | routing policy | blocked-field + allow-conditions enforced | (canonical) | `routing_policy_tests.json`, `policy_config_snapshot.json` |
| P4-COST-001 | 4 | QA | cost accounting | daily budget enforced; report emitted | (canonical) | `cost_report.json`, `local_percent_report.json` |
| P5-QUEUE-001 | 5 | Builder | queue worker | SKIP LOCKED worker + DLQ works | (canonical) | `queue_worker_smoke.log`, `queue_load_test.json` |
| P5-AUDIT-001 | 5 | Security | DB migrations | audit_log immutability enforced and tested | (canonical) | `audit_immutability_test.log` |
| P5-CHAOS-001 | 5 | QA | chaos gates | chaos kill-9 + concurrency N=50 headroom PASS (additive) | (canonical) | `chaos_kill9.log`, `concurrency_n50.log` |
| P5-SECRETS-001 | 5 | Security | config lint | default/unsafe secrets rejected in production exposure mode | (canonical) | `secrets_hygiene_lint.log` |
| P5-RATE-001 | 5 | Builder | Agent API middleware | rate limiting + request size limits enforced and tested | (canonical) | `rate_limit_test.log` |
| P6-REDTEAM-001 | 6 | Security | red-team suite | adversarial suite PASS; artifacts stored | (canonical) | `redteam_report.json` |
| P6-CI-001 | 6 | Infra | CI config | CI runs gate pack and retains artifacts | (canonical) | `ci_gate_run.log` |
| P6-EVALTREND-001 | 6 | QA | eval harness | eval trend artifact updated every run (append-only) | (canonical) | `eval_trend.csv` |
| P7-OPS-001 | 7 | Infra | runbooks | runbooks complete and linted | (canonical) | `runbook_lint.log` |
| P7-BACKUP-001 | 7 | Infra | backups | restore drill PASS | (canonical) | `backup_restore_drill.log` |
| P7-MONITORING-001 | 7 | Infra | monitoring | monitoring smoke checks PASS | (canonical) | `monitoring_smoke.log` |
| P7-RELEASE-001 | 7 | QA | release readiness gate | release readiness check computed from required artifacts | (canonical) | `release_readiness_check.json` |
| P8-BENCH-001 | 8 | QA | benchmarks | baseline benchmarks recorded | (canonical) | `benchmarks.json`, `migration_trigger_status.json` |
| P8-CADENCE-001 | 8 | QA | docs | cadence schedule written and referenced by CI | (canonical) | `ci_cadence_schedule.md` |

---

# Testing & Eval Strategy (global)

## Regression

- Run baseline gate pack (`bring_up_tests.sh`) for every phase and in CI.

- Any drift in contracts (endpoints/status strings/tool names/artifacts) must fail immediately.


## Reliability/chaos

- kill -9 recovery is a permanent gate.

- concurrency N=20 remains mandatory baseline; N=50 is additive headroom evidence.


## Security

- Auth negative suite must remain stable (401 vs 403 semantics).

- No-raw-content and at-rest protection must be enforced as gates, not manual checks.


## Quality evals

- Tool accuracy ≥95% on 50 prompts (Phase 3).

- Retrieval recall@5 ≥0.80 (Phase 3).

# Top 10 failure modes (Stop‑Ship) + mitigations

Each item below must have (a) a gate in `bring_up_tests.sh`, (b) a deterministic artifact, and (c) a rollback action.

1) **Contract drift (endpoints/status/schema keys)**
   - Detection: `contract_snapshot.json` + `agent_api_contract.json`
   - Mitigation: Phase 0 contract lock pack; fail CI on drift
   - Rollback: revert to last green contract snapshot; rerun baseline gates

2) **Approval not persisted before interrupt**
   - Detection: `invoke_hitl.json` + `db_invariants.sql.out` show approval row exists pre-interrupt
   - Mitigation: “create approval row → commit → interrupt” invariant; reject any refactor that changes ordering
   - Rollback: revert graph/tool-gateway changes; rerun BL-02/BL-03

3) **Double execution under concurrency**
   - Detection: `concurrent_approves.log` (1×200, rest 409) + `db_invariants.sql.out` (`execution_count = 1`)
   - Mitigation: claim-first idempotency (INSERT before execute); unique constraint on idempotency key
   - Rollback: disable the tool execution path until fixed; restore from DB backup if side effects occurred

4) **Crash mid-workflow leaves a stuck claim**
   - Detection: `checkpoint_kill9_test.log` and Phase 1 `kill9_encrypted.log`
   - Mitigation: stale-claim reclaim logic + checkpointing; time-bound claims
   - Rollback: operator runbook “reclaim stale claims”; restart worker/agent

5) **Plaintext at rest / raw content leakage**
   - Detection: `pii_canary_report.json` + `raw_content_scan.log` + `langfuse_selfhost_gate.log`
   - Mitigation: at-rest encryption + redaction boundary; fail closed on `PRODUCTION_EXPOSURE=true` without keys (`prod_exposure_fail_closed.log`)
   - Rollback: restore pre-migration DB backup; rotate keys if exposure suspected

6) **Actor spoofing / approval privilege escalation**
   - Detection: `auth_negative_tests.json` + `db_invariants.sql.out` shows actor bound to JWT `sub`
   - Mitigation: bind effective actor_id to verified auth subject when enforcement enabled; default deny
   - Rollback: disable approval endpoints from external exposure; rotate JWT secret; audit log review

7) **Cloud egress policy violation (PII exfiltration)**
   - Detection: `routing_policy_tests.json` + `policy_config_snapshot.json`
   - Mitigation: default deny cloud routing; blocked-field enforcement; canary tokens
   - Rollback: disable cloud fallback; force local-only until policy revalidated

8) **Mocks accidentally used in acceptance runs**
   - Detection: `mocks_disabled_check.log` + `mock_safety_test.log`
   - Mitigation: fail start if mocks enabled in `APP_ENV=production` / `PRODUCTION_EXPOSURE=true`
   - Rollback: rerun Phase 2 E2E with mocks disabled; invalidate any “green” run that used mocks

9) **Queue retries cause duplicate side effects**
   - Detection: `queue_load_test.json` + audit/tool execution logs show idempotent outcomes
   - Mitigation: idempotency keys on all write/critical executions; DLQ after max attempts
   - Rollback: pause workers; drain DLQ with operator approval; restore DB backup if needed

10) **Backup/restore procedures fail when needed**
    - Detection: `backup_restore_drill.log`
    - Mitigation: scheduled restore drills; versioned runbooks (`runbook_lint.log`)
    - Rollback: none at incident time—prevention is the only safe strategy; treat failed drills as Stop‑Ship


---

# Release Readiness Gate (Go/No-Go)

No production exposure (including Cloudflare external exposure or real confidential deal data) is allowed unless:

1) Phase 2 PASS (MVP E2E real-service, mocks disabled)

2) Phase 1 PASS (at-rest protection + no-raw-content gates + Langfuse self-hosted)

3) Phase 5 PASS (queue + audit immutability + secrets hygiene + rate limiting)

4) Phase 6 PASS (CI gates + red-team)

5) Phase 7 PASS (runbooks + backup/restore drill)



Required evidence bundle:

- Baseline artifacts (BL-01..BL-14)

- `encryption_verify.log`, `prod_exposure_fail_closed.log`
- `raw_content_scan.log`, `pii_canary_report.json`, `secrets_hygiene_lint.log`

- `deal_api_e2e_transition.json`, `mocks_disabled_check.log`, `cloudflare_route_lint.log`
- `ui_smoke_test.log` (or `ui_smoke_trace.json`)

- `queue_load_test.json`, `chaos_kill9.log`, `audit_immutability_test.log`, `rate_limit_test.log`

- `redteam_report.json`, `ci_gate_run.log`, `eval_trend.csv`

- `runbook_lint.log`, `backup_restore_drill.log`, `monitoring_smoke.log`, `release_readiness_check.json`



Sign-off roles:

- Builder (implementation readiness)

- QA (gate evidence)

- Security (privacy/egress/audit)

- Infra (ops/runbooks/backup)


---

# Appendix

## Evidence Index (major claims → source)

- Baseline invariants and artifacts: `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`

- Locked constraints (ports, model, orchestration, queue, security, routing, retrieval): `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`

- Host-services mode and “no localhost” rule; retrieval via RAG REST only; PORTS.md authoritative: `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`

- Tool-to-Deal-API mapping (expected target; still contract-probed for base path): `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v2.md` (Agent tool mapping table)

- Pass 2 stop-ship findings used to eliminate “paper gates” and enforce key management + checkpoint_writes scope: `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass2/R_*.md`


## Decision Log (A vs B and other conflicts)

1) **Gate runner**: single entrypoint `bring_up_tests.sh` (B + Pass2 critiques) over multiple scattered scripts (A).

   - Acceptance: all required gates run through one command and emit deterministic artifacts.

2) **Status string**: `awaiting_approval` (QA reality) over any `pending_approval` variant.

   - Acceptance: contract snapshot asserts status string; drift fails.

3) **Agent API prefix**: `/agent/*` canonical (QA reality) with `/api/v1/agent/*` as alias only.

   - Acceptance: contract snapshot asserts `/agent/*` endpoints exist.

4) **Langfuse**: self-hosted :3001 required for completion (Decision Lock) over “cloud fallback as compliant” (older drafts).

   - Acceptance: langfuse selfhost gate PASS required.

5) **Retrieval**: RAG REST only for Agent API (Scaffold Plan) over any implication of direct pgvector access.

   - Acceptance: static scan gate for direct DB retrieval + runtime contract.

6) **Concurrency thresholds**: keep N=20 as mandatory baseline (QA reality); allow N=50 as additive headroom evidence (not a replacement).

   - Acceptance: both artifacts present when Phase 5 is complete.


## Gate Artifact Index (filename → produced by → PASS marker)



Baseline artifacts (already produced today by bring_up_tests.sh):

- `health.json` → health gate → HTTP 200 recorded

- `invoke_hitl.json` → HITL invoke gate → `status == "awaiting_approval"`

- `approve.json` → approve gate → `status == "completed"`

- `approve_again.json` → idempotency gate → HTTP 409

- `db_invariants.sql.out` → DB invariant gate → contains invariants

- `checkpoint_kill9_test.log` → kill -9 gate → contains `RESULT: PASSED`

- `concurrent_approves.log` → concurrency gate → contains `RESULT: PASSED`

- `tool_call_validation_test.log` → schema gate → JSON `status == "PASSED"`

- `dependency_licenses.json` → license gate → file exists; violations flagged

- `mock_safety_test.log` → mock safety gate → contains PASS marker

- `streaming_test.log` → streaming gate → contains `STATUS=PASSED`

- `streaming_hitl_test.log` → streaming (HITL) gate → contains `awaiting_approval`

- `hitl_scope_test.log` → scope gate → JSON `status == "PASSED"`

- `auth_negative_tests.json` → auth gate → all tests passed

- `run.log` → final summary → contains `ALL GATES PASSED - HITL Spike verified!`



Planned additions (must be implemented inside bring_up_tests.sh; phase-gated):

- `contract_snapshot.json` → contract lock pack → `CONTRACT_SNAPSHOT: PASSED`

- `agent_api_contract.json` → agent API probe → schema/status checks

- `vllm_lane_verify.json` → vLLM lane verify → JSON `status == "PASSED"` and expected model id

- `ports_md_lint.log` → ports lint → `PORTS_MD_LINT: PASSED`

- `env_no_localhost_lint.log` → env lint → `ENV_NO_LOCALHOST: PASSED`

- `artifact_bundle.zip` → bundler → `BUNDLE: CREATED`

- `gate_registry.json` → gate+artifact registry (implemented gates only)

- `gate_registry_lint.log` → gate registry lint → `GATE_REGISTRY_LINT: PASSED`

- `encryption_verify.log` → encryption verify → `ENCRYPTION_VERIFY: PASSED`

- `kill9_encrypted.log` → encrypted kill-9 → `KILL9_ENCRYPTED: PASSED`

- `pii_canary_report.json` → canary → `PII_CANARY: PASSED`

- `raw_content_scan.log` → raw scan → `RAW_CONTENT_SCAN: PASSED`

- `langfuse_selfhost_gate.log` → langfuse gate → `LANGFUSE_SELFHOST: PASSED`

- `resilience_config_snapshot.json` → resilience snapshot

- `prod_exposure_fail_closed.log` → production exposure fail-closed → `PROD_EXPOSURE_FAIL_CLOSED: PASSED`

- `deal_api_contract.json` → deal API contract

- `repro_commands.sh` → generated repro

- `mocks_disabled_check.log` → mocks enforcement → `MOCKS_DISABLED: PASSED`

- `deal_api_e2e_transition.json` → E2E proof → `E2E_TRANSITION: PASSED`

- `ui_smoke_test.log` → UI smoke → `UI_SMOKE: PASSED`

- `cloudflare_route_lint.log` → Cloudflare lint → `CLOUDFLARE_ROUTE_LINT: PASSED`

- `rag_rest_contract.json` → RAG contract

- `eval_dataset_manifest.json` → dataset manifest

- `tool_accuracy_eval.json` → tool eval

- `retrieval_eval_results.json` → retrieval eval

- `no_split_brain_retrieval_scan.log` → scan → `NO_SPLIT_BRAIN: PASSED`

- `mcp_conformance.json` → MCP conformance

- `routing_policy_tests.json` → routing tests

- `policy_config_snapshot.json` → policy snapshot

- `cost_report.json` → cost report

- `local_percent_report.json` → local% report

- `queue_worker_smoke.log` → queue smoke

- `queue_load_test.json` → queue load

- `chaos_kill9.log` → chaos kill-9 → `CHAOS_KILL9: PASSED`

- `concurrency_n50.log` → concurrency headroom → `CONCURRENCY_N50: PASSED`

- `audit_immutability_test.log` → audit immutability

- `secrets_hygiene_lint.log` → secrets lint

- `rate_limit_test.log` → rate limit

- `ci_gate_run.log` → CI summary

- `redteam_report.json` → red-team report

- `eval_trend.csv` → eval trend (append-only)

- `backup_restore_drill.log` → drill

- `runbook_lint.log` → runbooks lint → `RUNBOOK_LINT: PASSED`

- `monitoring_smoke.log` → monitoring

- `release_readiness_check.json` → Go/No-Go summary

- `benchmarks.json` → benchmarks

- `migration_trigger_status.json` → triggers

- `ci_cadence_schedule.md` → cadence schedule (CI + ops)



## Quality Audit



Grades (A–F):

- Completeness: A-

- Correctness (locks + QA reality): A-

- Novelty/edge-of-tech: B (intentionally conservative; safety-first)

- Engineering feasibility: A-

- Clarity: A-



Top 10 remaining weaknesses (and fixes):

1) Next.js repo path is not pinned → locate repo and replace “TBD” with exact path; add UI gate.

2) Deal API base path uncertainty → contract probe must lock it; update tool gateway accordingly.

3) At-rest protection details may require iteration → treat kill‑9 + concurrency as absolute regressions; fail fast.

4) Trace export scanning may be brittle → standardize Langfuse export endpoint and scope.

5) Rate limiting design needs concrete choice → implement in Agent API middleware; add gate.

6) CI environment parity vs host-services mode → define CI all-in-compose mode and gate.

7) Eval datasets risk containing sensitive data → enforce dataset policy lint.

8) Migration trigger computation needs canonical counters → define where counts/latency come from.

9) Budget/cost tracking depends on provider metadata → standardize cost accounting schema.

10) Runbooks may drift from reality → runbook lint gate + periodic drills.
