# A3 Review — CHAT-CONTROL-SURFACE-001
## Agent: Codex CLI (gpt-5.3-codex) — Read-only sandbox, 239K tokens used

## 1. GAPS

1. `CRITICAL` Provider credential flow is not implementable as written.
Evidence: Plan requires reading keys from localStorage in server route (`CHAT-CONTROL-SURFACE-001.md:232`), but localStorage is client-only (`apps/dashboard/src/lib/settings/provider-settings.ts:79`), while routing happens in a Next server route (`apps/dashboard/src/app/api/chat/route.ts:100`).
Recommendation: Define a real credential transport contract now: either server-side encrypted provider profiles or client-sent ephemeral keys per request with strict redaction and no persistence in logs.

2. `CRITICAL` Delegation API contract is wrong in the plan and would fail at runtime.
Evidence: Planned endpoint `/api/deals/{deal_id}/delegate` (`CHAT-CONTROL-SURFACE-001.md:121`) does not exist. Existing endpoints are `POST /api/deals/{deal_id}/tasks` (`apps/backend/src/api/orchestration/main.py:3790`) and `POST /api/delegation/tasks` (`apps/backend/src/api/orchestration/main.py:4147`).
Recommendation: Replace P1/P3 contract with explicit endpoint mapping by task type and `deal_id` presence, then add integration tests for both paths.

3. `HIGH` Quarantine mutation payload is underspecified and partially wrong.
Evidence: Plan uses `operator_name` (`CHAT-CONTROL-SURFACE-001.md:120`) but backend expects `processed_by` (`apps/backend/src/api/orchestration/main.py:378`).
Recommendation: Lock the `process_quarantine` method signature to backend fields (`action`, `processed_by`, `reason`, `expected_version`, etc.) and add strict request/response models.

4. `HIGH` Race-condition mitigation is incomplete and could still allow write conflicts.
Evidence: Plan proposes GET status then POST (`CHAT-CONTROL-SURFACE-001.md:279`), but backend already supports versioned optimistic locking via `expected_version` (`apps/backend/src/api/orchestration/main.py:2757`).
Recommendation: Require `expected_version` in mutation tools and handle `409` with a deterministic user-facing retry path.

5. `HIGH` HITL enforcement can silently regress due naming drift.
Evidence: Objective names (`list_quarantine`, `approve_quarantine`) differ from phase tasks/AC (`approve_quarantine_item`, etc.) (`CHAT-CONTROL-SURFACE-001.md:17`, `:145`, `:350`), while HITL is exact string match (`apps/agent-api/app/schemas/agent.py:170`).
Recommendation: Finalize canonical tool names first, then add CI assertion that every mutating tool in registry is present in `HITL_TOOLS`.

6. `HIGH` Failure-path testing is missing for the riskiest edges.
Evidence: Gates rely mostly on manual checks, with no explicit tests for 503 feature-flag-off, 409 version conflicts, 422 validation, provider outage fallback, or allowlist rejects.
Recommendation: Add explicit unit/integration route tests for each error class before Phase 7.

7. `MEDIUM` SSE contract changes are not fully specified end-to-end.
Evidence: Plan adds `data_fetched_at`, but stream client typing currently centers on `token|evidence|done` with limited fields (`apps/dashboard/src/lib/api.ts:1871`).
Recommendation: Version the SSE `done` schema and update parser types/UI rendering in same phase to avoid silent field drops.

8. `MEDIUM` Rollback strategy is source-only, not operational.
Evidence: Rollbacks are "revert files" per phase, with no runtime flag rollback or deployment strategy.
Recommendation: Add rollback matrix with feature flags and canary cutover points for P2/P3/P5/P6.

9. `MEDIUM` MCP allowlist task lacks implementation details needed for safe enforcement.
Evidence: Plan asks for CIDR/IP allowlist, current MCP server has no such control and binds `0.0.0.0` (`apps/backend/mcp_server/server.py:526`).
Recommendation: Specify CIDR parsing, trusted proxy behavior, deny-mode defaults, and test vectors for container/K8s source IP patterns.

---

## 2. MISALIGNMENT

1. `HIGH` Scope contradiction: "No MCP bridge tool changes" vs planned MCP server modification.
Evidence: Constraint says no MCP changes (`:24`, `:370`), but P6-02 edits MCP server (`:270`).
Recommendation: Either split MCP security into a separate mission or update this mission's stated scope/guardrails.

2. `HIGH` Surface ownership contradiction.
Evidence: Surface 15 is marked "no changes, read-only reference" (`:26`) while P6 changes Surface 15 code.
Recommendation: Correct affected-surface matrix and gates before execution.

3. `CRITICAL` Delegation endpoint assumption conflicts with existing backend architecture.
Evidence: Planned `/api/deals/{deal_id}/delegate` (`:121`) vs actual task endpoints (`main.py:3790` and `main.py:4147`).
Recommendation: Rewrite delegation contract section with exact current endpoints and payloads.

4. `CRITICAL` Provider routing plan conflicts with Next.js runtime boundaries.
Evidence: Route is server-side (`route.ts:100`), provider settings are localStorage client-side (`provider-settings.ts:79`).
Recommendation: Redesign P5 around a server-resolvable provider config model.

5. `HIGH` Optimistic locking design contradicts backend-native version lock contract.
Evidence: Plan pre-checks status only (`:279`), backend lock is `expected_version` (`main.py:2757`).
Recommendation: Align to versioned POST contract, not status polling.

6. `MEDIUM` Prompt update strategy conflicts with anti-drift utilities already in code.
Evidence: Plan hardcodes "tool count updated to 14" (`:204`), while prompt package already has registry-driven tooling helpers (`__init__.py:96`).
Recommendation: Use dynamic tool section injection or automated prompt validation gate as the source of truth.

7. `MEDIUM` Non-local context requirement conflicts with current chat request shape.
Evidence: Plan says send full history for non-local (`:238`), but current client sends only `query/scope/session_id` (`api.ts:1914`) and route defaults to a single message (`route.ts:94`).
Recommendation: Add explicit history retrieval/compaction design to P5 before implementation.

8. `LOW` Tool naming is inconsistent across objective, tasks, and acceptance criteria.
Evidence: `list_quarantine` vs `list_quarantine_items` split across sections (`:17`, `:145`, `:350`).
Recommendation: Normalize names now to prevent schema/test/prompt drift.

---

## 3. WORLD CLASS

1. `MEDIUM` Missing end-to-end observability contract for the new control surface.
Recommendation: Require structured events with `correlation_id`, `session_id`, `provider`, `tool_name`, `proposal_id`, `task_id`, and fallback reason at each hop (agent, route, backend, MCP).

2. `MEDIUM` No explicit SLOs or error-budget targets for launch.
Recommendation: Define SLOs for chat success, p95 latency, provider fallback rate, proposal execution success, and quarantine action conflict rate.

3. `MEDIUM` No progressive delivery plan for high-risk phases.
Recommendation: Add feature flags for each major capability (quarantine tools, delegation tools, provider routing, MCP allowlist) with staged rollout and kill-switches.

4. `LOW` UX transparency for provider capabilities is under-specified.
Recommendation: In chat UI, display capability badges (tool-enabled vs text-only), active model/provider, and explicit warning before switching to cloud providers.

5. `LOW` Performance/cost governance is not planned for multi-provider context replay.
Recommendation: Add context window policy (truncate/summarize) and token-budget guardrails per provider.

6. `MEDIUM` Developer-experience quality gates are not elevated enough.
Recommendation: Add contract tests that assert alignment among tool registry, HITL set, prompt references, provider enum, and SSE payload schema.

---

## 4. FULL-STACK IMPLEMENTATION

1. `HIGH` Agent layer is not fully closed.
Evidence: Plan adds new tool files and HITL entries but does not define shared correlation-id propagation strategy beyond existing `deal_tools` implementation (`graph.py:77`).
Recommendation: Introduce shared tool runtime utility for `_get_client` + correlation context and add unit tests for each new tool schema/error path/HITL status.

2. `HIGH` API layer contract is incomplete.
Evidence: Planned "typed" methods still return loose dict/list types (`:119`), and delegation endpoint mapping is wrong.
Recommendation: Add typed request/response models for quarantine/delegation methods and lock exact endpoints in tests.

3. `HIGH` Dashboard layer is incomplete for provider routing.
Evidence: Current route still TODO-routed (`route.ts:104`) and provider service is env-based singleton with cloud providers unimplemented (`provider-service.ts:46`).
Recommendation: Implement per-request provider selection API and secure credential resolution before adding provider classes.

4. `MEDIUM` Infrastructure layer changes are under-specified.
Evidence: New env/runtime needs implied (e.g., `MCP_ALLOWED_IPS`, model identity) but no compose/env/runbook updates are listed.
Recommendation: Add explicit infra tasks for `.env`, docker compose, secret injection, and network policy updates.

5. `CRITICAL` Testing layer is not complete for a full-stack mission of this scope.
Evidence: Validation mostly uses `tsc`, `make validate-local`, and manual browser checks.
Recommendation: Add minimum matrix: agent unit tests, backend API integration tests, dashboard route tests, and e2e flows covering success + failure + rollback for each major capability.

6. `MEDIUM` Operational readiness layer is partial.
Recommendation: Add production runbooks for provider outage, delegation-flag off behavior, quarantine conflict handling, and MCP unauthorized-source incidents, with clear on-call diagnostics.

---

### Priority Fix Order Before Execution
1. Resolve provider credential architecture and per-request routing contract.
2. Correct delegation endpoint contracts and typed BackendClient methods.
3. Align quarantine mutation contract with `processed_by` + `expected_version`.
4. Reconcile scope contradictions (MCP "no changes" vs P6-02 change).
5. Add automated test gates for HITL, provider fallback, SSE schema, and allowlist security.
