# PASS 3 — Hostile Red‑Team Audit of PASS2 Scaffold Master Plan
**Role:** Hostile Red‑Team Reviewer + Staff Engineer + OSS Risk Analyst  
**Input:** `/home/zaks/bookkeeping/docs/PASS2_MASTER_SELECTION.md`  
**Output:** `/home/zaks/bookkeeping/docs/PASS3_HOSTILE_AUDIT.md`  
**Scope:** Break the plan by identifying contradictions, missing proof, security/reliability gaps, and “paper architecture.”  
**Evidence rule:** No web browsing. Findings are grounded in PASS2 text plus local repo structure checks where available; anything not proven is labeled **unverified** and converted into a required test.

---

## 1) Severity‑Ranked Issues (Top 25)

### 1) [Blocker] `/agent/invoke` contract is inconsistent with approved MDv2 (request/response fields drift)
- **Where:** §4 Phase 1 (endpoint list), §5 demo request body uses `"input"` and omits `actor_id`, §5 expected response uses `pending_action`.
- **Why it fails:** This guarantees interface drift between Agent API, UI clients, and tests; it also breaks RBAC/audit requirements because caller identity is not included or derivable.
- **Exact fix (rewrite PASS2 text):**
  - Replace the demo payload and endpoint contract with the MDv2 canonical schemas (minimum):
    - Request: `{"thread_id"?: "...", "message": "...", "actor_id": "...", "deal_id"?: "...", "context"?: {...}}`
    - Response: `{"thread_id": "...", "status": "completed|awaiting_approval|error", "content"?: "...", "pending_approval"?: {...}, "actions_taken": [...], "error"?: "..." }`
  - Rename `pending_action` → `pending_approval` (or explicitly map the two and standardize).
- **Test that proves the fix:**
  - JSON Schema contract tests for `POST /agent/invoke` and approval endpoints; fail build if any field differs from MDv2 schema.
  - E2E: invoke → get `awaiting_approval` → approve → completes; verify `actor_id` recorded in DB.

### 2) [Blocker] `.env.zakops` uses `localhost` for service URLs; this will break in Docker
- **Where:** §4 Phase 0 `.env.zakops` (`VLLM_BASE_URL=http://localhost:8000/v1`, `DEAL_API_URL=http://localhost:8090`, `MCP_SERVER_URL=http://localhost:9100`, `LANGFUSE_HOST=http://localhost:3001`).
- **Why it fails:** Inside the `agent-api` container, `localhost` refers to itself, not other containers or the host. This causes immediate runtime failure unless `network_mode: host` is used (not specified).
- **Exact fix (add a required subsection + edits):**
  - Add **“Networking Modes (Authoritative)”** with two supported configurations:
    - **All‑in‑compose:** use service DNS names: `VLLM_BASE_URL=http://vllm:8000/v1`, `DEAL_API_URL=http://deal-api:8090`, `MCP_SERVER_URL=http://mcp:9100`, `LANGFUSE_HOST=http://langfuse:3000|3001` (actual internal port), etc.
    - **Host‑services:** use `host.docker.internal` (or `network_mode: host`) and document OS requirements.
  - Update `.env.zakops` examples accordingly (no `localhost` unless `network_mode: host`).
- **Test that proves the fix:**
  - `docker compose up -d` for the chosen mode; containerized smoke test curls `VLLM_BASE_URL`, `DEAL_API_URL`, `MCP_SERVER_URL` from inside `agent-api` container.

### 3) [Blocker] File/service names in the fork plan do not match the chosen scaffold (guaranteed rework)
- **Where:** §4 Phase 0 says “Rename service `api` → `agent-api`”; §4 Phase 1/Appendix B says delete `app/core/langgraph/tools.py`; §5 says restart `agent-api`; §5/§6 refer to `app/core/observability.py`.
- **Why it fails:** Implementers will not find the referenced service/file paths. This is an execution failure and a sign the plan is not grounded in the actual scaffold structure.
- **Exact fix (rewrite PASS2 with a “verified paths” map):**
  - Add **“Scaffold Reality Check (Verified Paths)”** and require running:
    - `docker compose config` to list service names
    - `find app -maxdepth 4 -type f` to confirm file paths
  - Update all file names and service names to match the scaffold’s actual structure before starting work.
- **Test that proves the fix:**
  - A “plan conformance” script that asserts every referenced path in PASS2 exists in the fork (grep PASS2 for backticked paths → `test -e` each).

### 4) [Blocker] Langfuse self‑host deployment is treated as a single service (“paper architecture”)
- **Where:** §3.2 “Langfuse :3001 Add to compose”; §4 Phase 0 “Add `langfuse` service on :3001”.
- **Why it fails:** The plan does not specify a runnable self‑hosted Langfuse stack (dependencies, storage). “Add a langfuse service” is not implementable as written.
- **Exact fix (add concrete deploy artifact + acceptance):**
  - Add a dedicated `docker-compose.langfuse.yml` (or explicit “Langfuse is already running externally; do not deploy in this compose”).
  - Add a health check endpoint expectation for Langfuse (and required env vars).
- **Test that proves the fix:**
  - Bring-up test: `docker compose -f docker-compose.langfuse.yml up -d` then verify UI reachable and the agent can create a trace (HTTP 2xx from Langfuse API).

### 5) [Blocker] Postgres ownership/port plan will likely collide with existing Postgres and/or Deal API DB
- **Where:** §3.1 “Single Database :5432”; §4 Phase 0 “Ensure Postgres image pgvector/pg16”; §3.2 says Postgres is “existing + new tables”.
- **Why it fails:** In a real ZakOps workstation, Postgres is already running for Deal API. Binding another container to `5432:5432` will fail; also “single database” across services is a coupling risk unless explicitly designed.
- **Exact fix (add DB topology decision + port rules):**
  - Add **“DB Topology (Authoritative)”**:
    - Option A: Agent uses a **separate database** on the same Postgres instance (recommended); no host port exposure required for internal compose.
    - Option B: Agent uses a separate Postgres instance on a different host port (e.g., 5433) and Deal API remains on 5432.
  - Update compose to avoid binding 5432 if already used (use internal network only).
- **Test that proves the fix:**
  - `docker compose up -d` succeeds on a host where Postgres is already bound to 5432; agent can connect to its DB and Deal API remains functional.

### 6) [Blocker] HITL “graft” instructions lack a complete, executable approval state model
- **Where:** §4 Phase 1/2/3 (approval endpoints + approval_gate node); §5 demo expects `approval_id` and resume after restart.
- **Why it fails:** The plan doesn’t define the invariant linking `approval_id` ↔ `thread_id` ↔ checkpoint state ↔ proposed tool execution ↔ idempotency key. Without this, resumes will be unreliable or unsafe (double-execution).
- **Exact fix (add an “Approval Invariants” subsection):**
  - Define approval state machine and invariants:
    - Every CRITICAL tool proposal creates an `approvals` row with `approval_id`, `thread_id`, `tool_name`, `tool_args_hash`, `idempotency_key`, `requested_by`, `status`.
    - Resume endpoint loads approval row, writes decision into graph state, and resumes from checkpoint **without re-proposing**.
  - Explicitly specify where the “pending approval” lives in LangGraph state.
- **Test that proves the fix:**
  - E2E test: invoke → pending approval → restart agent → approve → verify exactly one tool execution (idempotency enforced).

### 7) [Blocker] JWT requirements are asserted as “already implemented,” but the plan lacks a verification standard for Decision Lock claims
- **Where:** §4 Phase 4 “Verify existing JWT middleware … required claims `sub, role, exp, iss, aud`”; §2.2 Gate SEC=4; §6.1 “JWT Auth grep” check.
- **Why it fails:** Grep is not verification. If the scaffold doesn’t validate `iss/aud/exp` or doesn’t carry `role`, you will ship a broken RBAC boundary or silently accept invalid tokens.
- **Exact fix (tighten to a real gate):**
  - Replace “Verify existing JWT middleware” with “Implement/modify JWT verification to enforce required claims + issuer/audience + expiry.”
  - Add explicit negative test cases in §6.2: expired token, wrong issuer, wrong audience, missing role.
- **Test that proves the fix:**
  - Auth test suite: 401 on invalid tokens; 200 on valid tokens; role gates enforced (e.g., VIEWER cannot approve).

### 8) [Blocker] DB schema uses `gen_random_uuid()` without enabling the required extension
- **Where:** §4 Phase 6 schema for `approvals` table (`DEFAULT gen_random_uuid()`).
- **Why it fails:** In Postgres, `gen_random_uuid()` requires `pgcrypto` extension; migrations will fail on a clean DB.
- **Exact fix (add migration prelude):**
  - Add: `CREATE EXTENSION IF NOT EXISTS pgcrypto;` before using `gen_random_uuid()` (or use `uuid_generate_v4()` with `uuid-ossp`).
- **Test that proves the fix:**
  - Run migrations on a fresh Postgres container with no extensions pre-installed; verify tables create successfully.

---

### 9) [Major] Selection method relies on “2:1 LLM consensus” instead of measured capability fit
- **Where:** §2.1 C‑01 resolution and tie-breaker rationale.
- **Why it fails:** Majority vote among LLM outputs is not evidence; it can lock you into a higher-delta fork and increase rework risk.
- **Exact fix:** Replace “2:1 consensus” language with objective PASS 2 gate outcomes (measured tests) and explicitly list pass/fail results with links to logs/artifacts.
- **Test:** Require PASS 2 gate artifacts: checkpoint kill‑9 test logs, JWT negative tests, container networking test logs.

### 10) [Major] Gate checklist marks “Tool abstraction ✅ Clear registry” but no proof that it supports permissions/idempotency insertion points
- **Where:** §2.2 Gate G5 for wassim249.
- **Why it fails:** A “tool list” is not a policy-enforced tool gateway. Without a single choke point, permissions and idempotency will be scattered and drift.
- **Exact fix:** Add a checklist item: “Identify the single tool execution choke point and enforce permissions + idempotency there (unit-tested).”
- **Test:** Static test: mock tool gateway and assert **no direct tool invocation** occurs outside gateway module.

### 11) [Major] LiteLLM routing is in the architecture diagram but missing from the fork plan deliverables
- **Where:** §3 diagram includes LiteLLM; §4 Phase 0 does not add LiteLLM service/config.
- **Why it fails:** Decision Lock requires deterministic routing; without a deployed gateway or implemented router node policy, you risk ad hoc cloud calls or no fallback behavior.
- **Exact fix:** Add Phase 0/1 tasks: deploy LiteLLM (or explicitly implement routing in code and treat LiteLLM as Phase 2). Mark one as authoritative.
- **Test:** Routing tests: given policy inputs (context overflow / local down), correct model/provider selected deterministically.

### 12) [Major] Retrieval is split-brain (RAG REST + `deal_embeddings` table) and violates “single retrieval path”
- **Where:** §3.1 DB lists `deal_embeddings`; §3.2 includes RAG REST `:8052`; §4 Phase 3 adds `rag_tools.py`.
- **Why it fails:** Two retrieval surfaces create inconsistent indexing/security semantics and will cause drift.
- **Exact fix:** Add an explicit decision: “Retrieval is exclusively via RAG REST (:8052) OR exclusively via pgvector direct queries.” Remove the other from MVP plan.
- **Test:** Integration test disables the non-chosen retrieval service/path and verifies system still functions.

### 13) [Major] Streaming requirements are not preserved after deleting chat endpoints
- **Where:** §4 Phase 1 deletes `chatbot.py`; new `/agent/*` endpoints do not include a streaming mode; §6 tests don’t cover streaming.
- **Why it fails:** If the UI expects streaming, you will regress UX and may break existing frontends.
- **Exact fix:** Add a streaming endpoint (e.g., `POST /agent/invoke/stream` SSE) or define response streaming semantics for `/agent/invoke`.
- **Test:** E2E: stream endpoint returns incremental tokens/events and handles interrupt transitions (stream ends with `awaiting_approval`).

### 14) [Major] “transition_deal” permission tier is inconsistent (WRITE vs CRITICAL) and not justified
- **Where:** §3 tool tiers; §5 demo marks `transition_deal` as CRITICAL.
- **Why it fails:** Over-gating slows operations; under-gating is a compliance risk. The plan must define tier mapping per tool.
- **Exact fix:** Add a “Tool Catalog (Authoritative)” table mapping each ZakOps tool to READ/WRITE/CRITICAL and approval requirements.
- **Test:** Policy tests: each tool call enforces its tier; CRITICAL always triggers approval.

### 15) [Major] Idempotency verification is insufficient (no concurrency test; no idempotency-key derivation spec)
- **Where:** §4 Phase 3 idempotency; §6.2 T‑06; §7 R‑01/R‑06.
- **Why it fails:** Without concurrency tests and a deterministic idempotency key scheme, duplicate side effects remain likely under retries/restarts.
- **Exact fix:** Add:
  - idempotency key derivation rule (e.g., `sha256(thread_id + tool_name + canonical_args_json + approval_id)`).
  - concurrency test requirement (N parallel requests).
- **Test:** 50 parallel calls with same idempotency key → exactly one tool execution row transitions to completed; others return cached result.

### 16) [Major] Audit log table is called “immutable” but no immutability controls are defined
- **Where:** §4 Phase 6 “Audit log table (immutable)”; §4 Phase 4 “auth audit logging”.
- **Why it fails:** “Immutable” is not enforced by schema; accidental deletes/updates are possible.
- **Exact fix:** Add:
  - DB permission model (revoke UPDATE/DELETE from app role), or triggers to prevent mutation.
  - Required fields: `trace_id`, `thread_id`, `actor_id`, `idempotency_key`.
- **Test:** DB test attempts UPDATE/DELETE on audit_log as app role → denied; insert-only works.

### 17) [Major] MCP client integration is under‑specified (timeouts/retries/auth/tool mapping/versioning)
- **Where:** §4 Phase 3 “Create mcp_client.py … reference agent-service-toolkit”.
- **Why it fails:** MCP reliability problems are one of the original causes of platform failure; a vague adapter reintroduces the same risk.
- **Exact fix:** Add an “MCP Client Contract” checklist:
  - transport = streamable-http
  - per-tool timeout
  - retry/backoff rules
  - parameter validation before call
  - error normalization
- **Test:** MCP conformance suite against :9100: initialize → tools/list → tools/call for each tool; assert 99%+ success under retry-able failures.

### 18) [Major] “Langfuse no raw content” covers only tracing, not logs or DB persistence
- **Where:** §4 Phase 5 “Wrap Langfuse callbacks”; acceptance only checks Langfuse.
- **Why it fails:** PII can leak via structured logs, exceptions, or stored tool args/results (JSONB).
- **Exact fix:** Add:
  - Logging redaction policy: never log raw prompts/responses/tool args by default.
  - DB redaction policy: store hashes/summaries for tool args/results unless explicitly allowed.
- **Test:** PII canary string appears nowhere in logs (`docker logs`), DB tables, or traces by default.

### 19) [Major] Postgres schema plan lacks queue tables / SKIP LOCKED worker plan (Decision Lock gap)
- **Where:** §3 DB diagram includes checkpoints/approvals/tool_exec/embeddings but no `task_queue`; §4 has no worker service plan.
- **Why it fails:** Long-running workflows will block request threads; crash recovery for background work is incomplete.
- **Exact fix:** Add Phase 2 deliverables:
  - `task_queue` + DLQ tables
  - worker process/service (even if minimal) using SKIP LOCKED
- **Test:** Submit background task, crash agent, restart worker, verify completion without loss.

### 20) [Major] Pre‑fork verification uses grep and one health curl; does not detect “demo‑ware” quality gaps
- **Where:** §6.1 Pre‑Fork Verification.
- **Why it fails:** Grep checks do not validate runtime behavior (checkpoint durability, auth correctness, tool calling, streaming).
- **Exact fix:** Replace §6.1 with a small “bring-up test pack” that executes:
  - checkpoint kill‑9
  - auth negative tests
  - one tool call validation test
  - one streaming test
- **Test:** CI pipeline that runs the bring‑up tests in Docker.

### 21) [Minor] Demo references Deal API paths and deal IDs without grounding in actual Deal API contract
- **Where:** §5 Step 4 uses `curl http://localhost:8090/api/deals/DEAL-001`.
- **Why it fails:** If the real Deal API path differs, engineers will waste time debugging the wrong thing.
- **Exact fix:** Replace with “Call Deal API per its OpenAPI / existing client,” or cite the canonical endpoint from ZakOps API contract docs.
- **Test:** Integration test that uses the real Deal API client and validates stage transition.

### 22) [Minor] Restart test is weaker than required crash test (restart ≠ kill -9)
- **Where:** §5 Step 2 uses `docker compose restart agent-api` but acceptance says “kill -9”.
- **Why it fails:** Restart is graceful; it won’t expose checkpoint corruption or in-flight execution hazards.
- **Exact fix:** Add explicit crash test steps: `docker kill -s KILL <container>` during tool execution.
- **Test:** Kill‑9 during CRITICAL execution → on restart, system resumes safely without double-execution.

### 23) [Minor] Port documentation is implied but not made authoritative
- **Where:** §7 risk R‑05 mentions `PORTS.md` but not created or enforced.
- **Why it fails:** Port drift causes repeated integration failures (already seen historically).
- **Exact fix:** Add a required artifact: `PORTS.md` as a single source of truth; update compose/env/tests to reference it.
- **Test:** A linter script verifies all referenced ports match `PORTS.md`.

### 24) [Minor] “Bounded gap” claim for HITL graft is not backed by a time-boxed spike definition
- **Where:** §1 trade-off accepted; §7 R‑01 says time-box 3 days but no explicit success criteria.
- **Why it fails:** Without a spike DoD, you can burn time and still not know when to switch scaffolds.
- **Exact fix:** Add a 1–2 day spike DoD: implement approval endpoints + checkpoint resume + exactly-once tool execution for one CRITICAL tool.
- **Test:** Spike passes the MVP scenario with a crash mid-approval and concurrency idempotency.

### 25) [Minor] “Delete chatbot.py” is unnecessarily destructive; increases churn
- **Where:** §4 Phase 1 deletes `app/api/v1/chatbot.py`.
- **Why it fails:** This discards working streaming/plumbing that could be repurposed, increasing scope and regression risk.
- **Exact fix:** Replace “Delete” with “Deprecate / keep temporarily; reuse streaming plumbing for `/agent/invoke/stream`.”
- **Test:** Regression test ensures existing health and basic chat paths (if retained) do not break while new endpoints are introduced.

---

## 2) OSS Due Diligence Gaps
PASS2 includes a high-level gate list, but it misses several hard due‑diligence checks needed for production OSS adoption.

### 2.1 License Risk (dependencies + assets)
- **Gap:** PASS2 checks only top-level repo LICENSE (MIT/Apache‑2.0). It does not validate transitive dependency licenses or embedded assets.
- **Exact check required:**
  - Generate a dependency license report for Python dependencies (runtime + dev) and confirm compatibility with ZakOps distribution model.
  - Scan repo for vendored files/assets with separate licenses.
- **Fail-fast rule:** Reject if any copyleft licenses (GPL/AGPL) are required at runtime unless explicitly approved.

### 2.2 Maintenance / Bus Factor Risk
- **Gap:** Star/commit counts are not sufficient; PASS2 does not check maintainer count, release cadence, or issue triage health.
- **Exact check required:**
  - Identify number of active maintainers (distinct committers in last 90 days) and whether releases/tags exist.
  - Review open issue backlog trend (growing/flat) and presence of security policy/process.
- **Fail-fast rule:** If single-maintainer + high open issues + no releases, treat as high-risk unless the code is small enough to own internally.

### 2.3 Dependency Security / Supply Chain Risk
- **Gap:** No vulnerability scanning is required; lockfile integrity and update strategy are not addressed.
- **Exact check required:**
  - Run vulnerability scan on pinned dependencies (Python + docker images).
  - Produce SBOM (CycloneDX or equivalent) and store it in repo.
  - Ensure container images are pinned by digest for production.
- **Fail-fast rule:** Reject if critical vulns exist with no patch path, or if dependencies are unpinned for production.

### 2.4 “Demo‑ware” Risk (production readiness)
- **Gap:** PASS2 does not require evidence of tests, CI, migration strategy, or operational runbooks.
- **Exact check required:**
  - Confirm presence of: CI workflow, unit tests, integration tests, reproducible local dev setup, and a clear migration story.
  - If missing, require a “hardening sprint” plan before shipping.
- **Fail-fast rule:** If no tests exist, require adding contract + E2E tests before any feature work.

---

## 3) Implementation Feasibility Audit (Is the fork plan actually minimal?)

### Finding: The plan implicitly builds multiple major subsystems “from scratch”
These are not “small grafts”; they are core product subsystems that dominate schedule risk:
- Approval state machine + resume semantics (HITL)
- Tool permission enforcement + idempotency gateway
- JWT/RBAC hardening to Decision Lock spec (iss/aud/exp/role)
- Observability “no raw content” across traces/logs/DB
- Potentially: migrations framework (if scaffold lacks it)

### Why this matters
PASS2 frames the HITL gap as “bounded,” but the checklist requires implementing a durable, crash-safe, exactly-once approval execution pipeline. That is a substantial subsystem.

### Smaller alternative steps (still compliant; not a rebuild)
1) **Do not delete working streaming plumbing.** Reuse existing SSE/stream patterns for `/agent/invoke/stream` before refactoring.
2) **Implement HITL for exactly one CRITICAL tool first** (transition_deal) with strict DoD; defer multi-tool workflows until that passes.
3) **Treat Langfuse deployment as external for MVP** (if self-host stack is not already present). Keep the code-level integration and enable self-hosted deployment in Phase 2 with a dedicated compose.
4) **Avoid adding Alembic unless already present.** For MVP, use SQLModel `create_all` (dev-only) for new tables; add Alembic migrations after the approval/idempotency pipeline is proven.
5) **If HITL or auth hardening blocks:** switch fork target to `agent-service-toolkit` (already the reference) rather than continuing to graft large subsystems into a template that wasn’t designed for them. This is not a rebuild; it’s choosing a closer base.

---

## 4) “Go/No‑Go” Verdict

### Verdict: **NO‑GO** as written.
You should not start implementation with PASS2 unchanged because several items will fail immediately (contract drift, Docker networking URLs, incorrect file/service references, and an incomplete HITL state model).

### Minimum changes required to reach **GO**
1) Align `/agent/invoke` + approval endpoints **exactly** to MDv2 schemas; update all examples/tests.
2) Add an authoritative **Networking Modes** section and remove `localhost` service URLs for container mode.
3) Fix all scaffold-specific file/service names by running a “verified paths” sweep before Phase 1.
4) Define the approval invariants and resume mechanism end-to-end (approval_id ↔ checkpoint ↔ idempotency).
5) Add `pgcrypto` (or equivalent) extension enablement to migrations.
6) Decide and document DB topology to avoid Postgres port collisions and cross-service coupling.
7) Specify how Langfuse is deployed (external vs full self-hosted stack) and add a bring-up test.

Once these are corrected, you can begin with a time-boxed HITL + idempotency MVP spike and re-evaluate whether wassim249 remains the lowest-delta fork.

