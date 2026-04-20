# QA Audit — Hostile Red‑Team Review (MDv1)
**Role:** Hostile Red‑Team Reviewer + Staff Engineer  
**Input:** `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v1.md`  
**Output:** This audit enumerates implementation-failure/drift risks in MDv1 and prescribes concrete fixes + proving tests.  
**Constraint:** No web browsing; findings are based on MDv1 text only. Any library-specific behavior is treated as an assumption and paired with a validation test.

---

## Verdict (Pass/Fail)
**FAIL** as an implementation blueprint **as-is**. MDv1 contains multiple **Blockers** that will cause immediate interface drift, broken deployments, unsafe execution semantics, and privacy/security gaps.

---

## 1) Top 30 Issues (Ranked by Severity)

### 1) [Blocker] Conflicting service ports and public surfaces (8090 vs 8095; Cloudflare points to wrong service)
- **Where:** §5.1 Major Components (diagram: Deal API `:8090`, Agent `:8095`), §5.2 Data Flow (`:8095`), §6.7 Cloudflare config routes `zakops-agent...` to `localhost:8090`, §9.4 Chaos test uses `localhost:8095`, §10.1 docker-compose exposes agent `8095:8095`.
- **Why it’s a problem:** Engineers will wire clients/Cloudflare/tests to the wrong service, guaranteeing drift and broken integration.
- **Exact fix (edit MDv1):**
  - Add a new authoritative subsection in §10.1:
    - **“Service Ports & Base URLs (Authoritative)”** table:
      - `deal_api_base_url = http://localhost:8090` (existing)
      - `agent_api_base_url = http://localhost:8095` (new)
      - `rag_api_base_url = http://localhost:8052` (existing)
      - `mcp_base_url = http://localhost:9100` (existing)
      - `vllm_base_url = http://localhost:8000/v1` (local)
    - Explicitly state whether Cloudflare exposes `agent_api_base_url` or `deal_api_base_url`, and update the Cloudflare ingress accordingly.
  - Replace all inconsistent port references to match the table.
- **Test that proves the fix:** A doc-contract test that greps MDv1 for `8090`/`8095` and asserts they appear only where consistent with the table; plus a smoke test script that curls each base URL and expects 200/401 as appropriate.

### 2) [Blocker] Agent service boundary is ambiguous (Deal API vs agent API ownership and responsibilities)
- **Where:** §5.1 diagram shows both Deal API and Agent API, but §10.1 docker-compose only defines `agent` (and no `deal api` service), and §6.3 Tool Gateway implies direct tools like `list_deals` without mapping to Deal API endpoints.
- **Why it’s a problem:** Without an explicit boundary, the agent will “reach around” via DB writes, duplicate business logic, or diverge from the Deal API schema.
- **Exact fix (edit MDv1):**
  - Add explicit statements under §5.1 or §6.1:
    - “Deal Lifecycle API (:8090) is system-of-record. Agent MUST NOT write deal state directly to DB; all writes go through Deal API or MCP write tools.”
    - “Agent API (:8095) is orchestration-only: proposals, approvals, and execution coordination.”
  - Add an “Integration Contract” list mapping each tool to an HTTP endpoint or MCP tool (name + request/response schema).
- **Test that proves the fix:** Integration test that stubs Deal API and asserts agent only uses allowed endpoints/tools (no direct DB writes) for transitions and actions.

### 3) [Blocker] AgentRequest/AgentResponse schemas contradict tests and scripts
- **Where:** §6.1 Inputs/Outputs define `AgentRequest` requiring `actor_id`, and `AgentResponse` with `status`/`messages`/`actions_taken`; §9.2 tests assert `response.success` and `response.content`; §9.4 chaos test checks `.success` and calls `/agent/invoke` without `actor_id`.
- **Why it’s a problem:** Immediate drift: engineers will implement one schema, tests/UI will assume another.
- **Exact fix (edit MDv1):**
  - Define canonical HTTP contract in §6.1:
    - `POST /agent/invoke` request schema (required: `actor_id`, `message`; optional: `thread_id`, `deal_id`).
    - response schema MUST include `status` and MUST NOT use ambiguous boolean `success` unless defined as `status == "completed"`.
  - Update §9.2/§9.4 examples to use the canonical schema.
- **Test that proves the fix:** JSON Schema contract tests for `/agent/invoke` request/response; run against server + tests.

### 4) [Blocker] HITL approval pause/resume semantics are internally inconsistent
- **Where:** §6.1 graph uses `interrupt_before=["approval_gate"]` and also has `approval_gate` conditional edges with `"pending": END  # Pause workflow`.
- **Why it’s a problem:** `END` terminates execution; it is not a “pause”. The document mixes two different pause mechanisms without defining the resume API and state update rules.
- **Exact fix (edit MDv1):**
  - Replace the `pending: END` branch with an explicit “return pending response” mechanism (do not terminate the thread).
  - Add §6.1 subsection “Approval Resume Protocol”:
    - `POST /agent/approvals/{approval_id}:approve|reject`
    - On approve/reject: persist decision + resume graph from checkpoint.
  - Remove either `interrupt_before` *or* the explicit approval node logic; keep one consistent approach.
- **Test that proves the fix:** E2E test: invoke CRITICAL action → response `status=pending` with `approval_id` → approve → agent resumes and completes; verify no duplicate tool executions.

### 5) [Blocker] Idempotency implementation is not concurrency-safe (exactly-once claim is false)
- **Where:** §6.3 “Idempotency Implementation” checks for existing record then executes tool, then inserts; §6.5 `tool_executions` has `idempotency_key UNIQUE` but no “claim” step.
- **Why it’s a problem:** Two concurrent requests with same idempotency key can both execute the side effect before either inserts, causing duplicate writes/emails/transitions.
- **Exact fix (edit MDv1):**
  - Replace §6.3 idempotency algorithm with a “claim-first” transaction:
    - Insert a row with `idempotency_key` in `pending` state using unique constraint.
    - Only the transaction that successfully inserts proceeds to execute.
    - Others read the existing row and return cached result.
  - Require downstream write tools/endpoints to accept the same idempotency key.
- **Test that proves the fix:** Concurrency test: 50 parallel calls with same idempotency key → exactly one external side effect; all callers receive same cached result.

### 6) [Blocker] Deployment example cannot start (missing `postgres` service; unresolved dependencies)
- **Where:** §10.1 docker-compose: `agent` depends_on `postgres` but no `postgres` defined; `langfuse` uses `postgres` host but no dependency; no volumes for DB persistence shown.
- **Why it’s a problem:** Engineers will copy/paste a non-functional compose file; environment will diverge immediately.
- **Exact fix (edit MDv1):**
  - Provide a complete compose (or explicitly reference external Postgres and remove `depends_on postgres`).
  - If Postgres is included: define `postgres` service, ports, volumes, users/dbs for `zakops` and `langfuse`.
  - Add a “Port collision” note (OpenWebUI uses 3000 in current environment; Langfuse uses 3001 already).
- **Test that proves the fix:** `docker compose up -d` then `docker compose ps` shows all services healthy; `/health/ready` returns 200.

### 7) [Blocker] Readiness check uses wrong host for vLLM inside Docker
- **Where:** §10.2 `ready()` calls `http://localhost:8000/health` from the agent service.
- **Why it’s a problem:** In Docker, `localhost` in the agent container is not the vLLM container → readiness fails or gives false negatives.
- **Exact fix (edit MDv1):**
  - Replace the check with `VLLM_BASE_URL`-derived host (e.g., `http://vllm:8000/health` in compose).
  - Add `VLLM_HEALTH_URL` env var to avoid guessing endpoint paths.
- **Test that proves the fix:** Containerized readiness test: with vLLM up, `/health/ready` returns 200; with vLLM down, returns 503 with `checks.vllm=unhealthy`.

### 8) [Blocker] Router implementation contradicts stated behavior (random routing via `simple-shuffle`)
- **Where:** §6.2 LiteLLM config: `routing_strategy: simple-shuffle` + fallbacks; §2/§5/§7 state complex tasks should route to cloud with cost controls.
- **Why it’s a problem:** Random routing breaks privacy, cost budgets, and quality expectations; it is not a “complexity router.”
- **Exact fix (edit MDv1):**
  - Replace the routing section with an explicit deterministic policy (implemented in the `router_node`):
    - Inputs: `task_type`, `risk_level`, `contains_sensitive_data`, `local_model_health`, `confidence`.
    - Output: `{model_used: local|cloud, reason}`.
  - Treat LiteLLM as a provider abstraction only (no random routing).
- **Test that proves the fix:** Unit tests for routing: given `risk_level=high` + `contains_sensitive_data=true` → MUST choose local (or require explicit approval); given `local_model_health=down` → MUST choose cloud if policy allows.

### 9) [Blocker] Privacy requirement conflicts with hybrid cloud escalation (no enforceable data egress policy)
- **Where:** §4.2 Privacy “All PII local-only”; §6.2 allows cloud fallback; §6.2 mentions “PII redaction layer” but no spec; §11.1 risks mention fallback to cloud.
- **Why it’s a problem:** Without a strict policy, engineers may inadvertently send raw deal documents/PII to cloud LLMs.
- **Exact fix (edit MDv1):**
  - Replace §4.2 Privacy row with:
    - “Default: no raw documents or PII leave local environment. Cloud escalation is allowed only on redacted summaries OR with explicit approver consent per request.”
  - Add “Cloud Egress Policy” subsection defining allowed fields, redaction rules, and approval requirement.
- **Test that proves the fix:** A “PII canary” test: embed synthetic PII in a doc, trigger cloud-eligible request, assert outbound payload contains no canary strings; also assert traces/logs contain no canaries.

### 10) [Blocker] “No PII in embedding model (content only)” is false and leads to unsafe storage assumptions
- **Where:** §6.4 Security/Privacy bullet: “No PII in embedding model (content only)”.
- **Why it’s a problem:** Document content *can contain PII*; embeddings and stored chunks are sensitive and must be treated as such.
- **Exact fix (edit MDv1):**
  - Replace that bullet with:
    - “Embeddings/chunks derived from deal content are sensitive. Apply RLS/ACLs, minimize stored raw text, and treat retrieval stores as in-scope for PII protections.”
- **Test that proves the fix:** Access-control tests: user with no access to Deal A cannot retrieve any chunk/embedding for Deal A (direct SQL + API); plus a log/trace scan test ensuring chunks are not logged.

### 11) [Blocker] Authentication example is insufficient for production (token validation gaps; API key ambiguity; missing schema)
- **Where:** §6.7 “API Authentication” JWT decode does not validate `exp/aud/iss`; API key fallback overloads bearer token; `api_keys` table not defined.
- **Why it’s a problem:** High-risk auth bypass and inconsistent client behavior; implementation will drift.
- **Exact fix (edit MDv1):**
  - Add explicit token validation requirements: `exp` required, issuer/audience required, clock skew handling, rotation procedure.
  - Separate API key auth into `X-API-Key` header (avoid confusing with JWT bearer).
  - Add `api_keys` schema (hashed key, role, created_at, revoked_at).
- **Test that proves the fix:** Auth suite: expired JWT rejected; wrong audience rejected; revoked API key rejected; rate limit triggers after N failures; audit log records denials.

### 12) [Blocker] Test suite examples are incompatible with defined interfaces (guaranteed drift)
- **Where:** §9.2 integration tests and §9.4 chaos test use `success` field and omit `actor_id`; §9.5 checks `response.tool_calls` though earlier response schema doesn’t define it.
- **Why it’s a problem:** Implementation cannot satisfy both the spec and the tests; teams will “fix” by drift rather than design.
- **Exact fix (edit MDv1):**
  - Rewrite §9 examples to align with the canonical `/agent/invoke` contract defined in §6.1.
  - If tool calls are not part of response, tests must not assert `response.tool_calls`.
- **Test that proves the fix:** Run the documented tests against a minimal implementation stub; tests should pass without modifying the server beyond the contract.

---

### 13) [Major] Event taxonomy is required but unspecified (event_type is free-form)
- **Where:** §4.1 mandates events like `deal.triaged`; §5.4 defines `AgentEvent` with `event_type: str` but no list; §6.5 has `audit_log` but no canonical mapping.
- **Why it’s a problem:** Event naming/payload drift across services; breaks audit/replay.
- **Exact fix (edit MDv1):**
  - Add “Event Types (Authoritative)” table:
    - `deal.triaged`, `deal.transition.requested`, `deal.transition.approved`, `quarantine.created`, `action.created`, `action.approved`, etc.
  - Provide payload schemas and required fields (deal_id, actor_id, trace_id, idempotency_key where applicable).
- **Test that proves the fix:** Schema validation test that rejects unknown event types and missing required fields; integration tests assert each workflow emits required events.

### 14) [Major] Core domain schemas are missing (Deal, Stage machine, Action, Approval, Quarantine)
- **Where:** §6.3 references `DEAL_STAGES` and `^DL-\\d{4}$`; §6.4 references `deals(deal_id)` but `deals` schema is not included; FRs require quarantines/actions.
- **Why it’s a problem:** Engineers will implement divergent schemas and inconsistent stage rules.
- **Exact fix (edit MDv1):**
  - Add a “Domain Model (Authoritative)” subsection: tables/Pydantic models for Deal, StageTransition, Action, ApprovalRequest, QuarantineItem with invariants.
- **Test that proves the fix:** Migration tests + stage-transition validation tests (allowed transitions only) + approval enforcement tests.

### 15) [Major] RAG architecture is split-brain (direct pgvector SQL vs RAG REST API :8052)
- **Where:** §5.1 includes `RAG :8052`; §6.4 implements direct SQL retrieval; §8 Phase 3 lists RAG REST API dependency.
- **Why it’s a problem:** Two retrieval paths means inconsistent indexing, inconsistent access control, and higher ops cost.
- **Exact fix (edit MDv1):**
  - Decide one canonical retrieval surface:
    - Option A: Agent calls RAG REST API only.
    - Option B: Agent queries Postgres directly and RAG REST API is removed from critical path.
  - Update §5.1 diagram, §6.4 design, and Phase 3 dependencies accordingly.
- **Test that proves the fix:** Integration test ensures only the chosen retrieval path is used; disable the other service and verify system still functions.

### 16) [Major] MCP integration details are missing (transport, auth, retries, tool mapping)
- **Where:** §5.1 shows MCP `:9100`; §6.3 shows “MCP server” branch but no client adapter; §7.1 says “MCP integration needs testing”.
- **Why it’s a problem:** Tool binding and reliability will drift; MCP becomes “hand-wavy” integration.
- **Exact fix (edit MDv1):**
  - Add “MCP Client Adapter” subsection:
    - transport (streamable-http per project context), auth mechanism, timeout/retry policy, tool name mapping, version negotiation.
- **Test that proves the fix:** Deterministic MCP conformance test: initialize → tools/list → tools/call for each tool; verify parameter validation and error handling.

### 17) [Major] Exactly-once semantics across approvals + retries are not defined end-to-end
- **Where:** §6.1 claims replay/debug; §6.3 idempotency; §6.5 queue; but no invariant ties approvals to action execution.
- **Why it’s a problem:** Duplicate emails/transitions can occur after retries or restarts; audit trail becomes inconsistent.
- **Exact fix (edit MDv1):**
  - Add invariant: “All WRITE/CRITICAL operations MUST be represented as an Action record; execution is allowed only once per action_id + idempotency_key.”
  - Define state machine for Action: `proposed → pending_approval → approved|rejected → executing → completed|failed`.
- **Test that proves the fix:** Crash mid-execution + retry test: ensure action does not execute twice and ends in a consistent terminal state.

### 18) [Major] “Replay / time-travel” is claimed but no safe replay mode is defined
- **Where:** §6.1 responsibilities include replay/debug; §6.6 says “Enable trace replay”; no definition of whether tools execute during replay.
- **Why it’s a problem:** “Replay” can unintentionally re-run write side effects.
- **Exact fix (edit MDv1):**
  - Add “Replay Modes” section:
    - `audit_replay` (no tool execution; uses stored tool_executions results)
    - `re_run` (tools execute; requires idempotency + approvals)
- **Test that proves the fix:** Replay test that asserts tool gateway is never called in `audit_replay` mode (mock asserts zero calls).

### 19) [Major] Observability example violates stated redaction goal (stores output content in spans)
- **Where:** §6.6 Langfuse integration calls `span.end(output=response.content[:500])`.
- **Why it’s a problem:** This can log sensitive deal content into the trace store, contradicting “Redact PII by default”.
- **Exact fix (edit MDv1):**
  - Replace with: store output hash + length + classification; store raw content only behind an explicit privileged debug flag with strict retention.
- **Test that proves the fix:** PII canary test verifies trace store contains no raw content fragments.

### 20) [Major] Observability stack wiring is not deployable as described
- **Where:** §5.1 diagram shows OTel Collector → Langfuse → Prometheus; §6.6 “Logs → Loki (Phase 2)” without deployment; §10.1 compose lacks Postgres and collector/prometheus.
- **Why it’s a problem:** Engineers will implement ad hoc telemetry, losing consistency and replayability.
- **Exact fix (edit MDv1):**
  - Provide a minimal, runnable “observability compose” (Langfuse + DB + OTel collector + Prometheus) OR explicitly scope it to Phase 2 with clear prerequisites and port plan.
- **Test that proves the fix:** Bring-up test: start stack; generate one agent run; verify trace exists and metrics counters increment.

### 21) [Major] Monitoring thresholds are “paper numbers” without computation definitions
- **Where:** §10.3 defines alerts like “tool hallucination rate >2%” and “workflow failure rate >5%” without defining windows and counting rules.
- **Why it’s a problem:** Alerting will be noisy or blind; SLOs can’t be enforced.
- **Exact fix (edit MDv1):**
  - For each alert, add:
    - window (e.g., 15m), numerator/denominator definition, and minimum sample size.
- **Test that proves the fix:** Alert unit tests that feed synthetic metrics and assert alert triggers only under defined conditions.

### 22) [Major] Load/performance acceptance criteria are not derived from a workload model
- **Where:** §4.2 includes “100 active threads”; §7.2 queue test requires “100 tasks/sec”; §7.5 Phase DoD uses “baseline established” without workload.
- **Why it’s a problem:** Teams will optimize the wrong thing or fail gates that don’t match real usage.
- **Exact fix (edit MDv1):**
  - Add “Workload Model” subsection:
    - deals/day, docs/deal, avg doc size, actions/deal, concurrency profile.
  - Derive load tests directly from that model.
- **Test that proves the fix:** A load test suite that uses the documented workload model and validates p95 latencies and backlog bounds.

### 23) [Major] Document ingestion & provenance is under-specified (core FR2 risk)
- **Where:** §4.1 FR2 requires structured extraction + provenance; §6.4 stores `content` but no ingestion/chunking/OCR/citations design.
- **Why it’s a problem:** Extraction quality and auditability will drift; citations cannot be trusted.
- **Exact fix (edit MDv1):**
  - Add component “Artifact Ingestion & Indexing” with:
    - artifact_id, checksum, source (email/pdf), page/offset citations, chunking policy, OCR fallback, and re-index triggers.
- **Test that proves the fix:** Ingest a PDF with known fields; verify extraction writes fields with citation pointers back to original artifact offsets.

### 24) [Major] Secrets management is a placeholder (no rotation/permissions; no “no secrets in traces” enforcement)
- **Where:** §6.7 Secrets Management caches env vars; “Phase 3 Vault” commented; no rotation/runbook; §6.6 can log content.
- **Why it’s a problem:** High likelihood of secret leakage and operational fragility.
- **Exact fix (edit MDv1):**
  - Add explicit “Secrets Policy”:
    - `.env.example` only committed; runtime secrets injected; rotation cadence; trace/log redaction rules.
- **Test that proves the fix:** Automated secret scan of repo + logs + traces after running an agent workflow; must find zero secrets.

### 25) [Major] Backup & recovery procedure is unsafe for containerized operation
- **Where:** §10.4 uses `pg_dump -h localhost` and `find ... -delete` without container context or restore drill.
- **Why it’s a problem:** Backups may silently fail; retention deletion can remove last good backup; no restore verification.
- **Exact fix (edit MDv1):**
  - Replace with container-aware backup:
    - run pg_dump against the correct Postgres service hostname; require restore verification into a scratch DB weekly.
  - Replace deletion with “keep last N + last M weekly” policy (avoid single point loss).
- **Test that proves the fix:** Automated restore test that restores last backup into a fresh DB and runs integrity queries.

---

### 26) [Minor] Versioning confusion (file v1; internal header says v2.0.0-FINAL)
- **Where:** Top header + §1 Title/Version.
- **Why it’s a problem:** Document control drift; engineers reference wrong version.
- **Exact fix (edit MDv1):** Align file name, internal version, and add a changelog section.
- **Test that proves the fix:** CI doc-lint checks that file name version matches header version.

### 27) [Minor] Docker volume uses `~` which may not resolve consistently
- **Where:** §10.1 compose `volumes: - ~/.cache/huggingface:/root/.cache/huggingface`.
- **Why it’s a problem:** In some environments, compose may not expand `~` as expected; leads to missing model cache.
- **Exact fix (edit MDv1):** Replace `~` with `${HOME}` or an absolute path variable documented in `.env`.
- **Test that proves the fix:** `docker compose config` shows expanded absolute path; vLLM starts without re-downloading models.

### 28) [Minor] Tool-calling eval harness uses brittle “exact args equality”
- **Where:** §9.3 `tool_calling_eval.py` compares `actual_args == expected_args`.
- **Why it’s a problem:** JSON key order/defaults/type coercions cause false negatives; metrics become untrustworthy.
- **Exact fix (edit MDv1):** Compare normalized JSON (sorted keys), allow defaults, and evaluate schema-valid equivalence.
- **Test that proves the fix:** Add eval cases with reordered keys/default fields and ensure evaluator scores them correctly.

### 29) [Minor] Adversarial test is insufficient (checks only tool names; not data exfiltration or approval enforcement)
- **Where:** §9.5 `test_prompt_injection.py`.
- **Why it’s a problem:** Agent could still leak secrets/PII in responses or route to cloud; test wouldn’t catch it.
- **Exact fix (edit MDv1):**
  - Extend tests to assert:
    - no outbound cloud call on restricted content
    - no sensitive strings in output/logs/traces
    - CRITICAL proposals always require approvals
- **Test that proves the fix:** Add a “PII canary” injection case; assert canary never appears in outbound payloads or traces.

### 30) [Minor] “Offline for 30+ days” is not a practical acceptance test as written
- **Where:** §3 Design Goals G1.
- **Why it’s a problem:** Not testable in CI; invites hand-waving.
- **Exact fix (edit MDv1):** Replace with “Offline mode smoke test: core workflows pass with all outbound network blocked for N hours.”
- **Test that proves the fix:** Run test suite with outbound network disabled; assert deal triage + retrieval + approval flows still work.

---

## 2) Pass/Fail Verdict for MDv1 as Blueprint
**Fail** until Blockers 1–12 are resolved. After fixes, MDv1 can become a viable blueprint, but it needs:
- a single authoritative interface/port contract,
- consistent pause/resume semantics for approvals,
- concurrency-safe idempotency,
- deployable compose files,
- enforceable privacy and auth rules,
- and schema contracts that match tests and services.

