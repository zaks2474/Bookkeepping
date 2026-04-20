AGENT IDENTITY
- agent_name: Codex
- run_id: 20260204-1903-1b4aee
- date_time: 2026-02-04T19:03:47Z
- repo_revision: 559a5d1f5c6d22adfd90fd767191dcd421f8732a

Executive Summary
- Verdict: NOT production-grade. Biggest risk: HITL enforcement is inconsistent with tool reality (create_deal is not HITL-gated in code but is declared HITL in prompt), enabling destructive actions without approval.
- Agent grounding is weak: system prompt is generic, no enforced “query before answer,” tools return unstructured strings, and search_deals provides no provenance.
- Observability is incomplete: no correlation ID propagation into agent logs or tool calls; decision chain reconstruction is not guaranteed.
- Long-term memory is disabled by default and not deal-scoped; RAG is tool-only and lacks freshness/provenance enforcement.
- Provider abstraction exists in config but routing policy is unused; mem0 uses OpenAI models even when vLLM is primary.
- QA baseline file `QA_VERIFICATION_006_REPORT.md` not found. NEEDS VERIFICATION: locate in `/home/zaks/bookkeeping/qa/` or regenerate.

Agent Architecture Inventory

1.1 Graph Definition and Topology
- Graph file: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
- Nodes:
  - chat: LLM call and tool routing
  - tool_call: executes non-HITL tools
  - approval_gate: HITL interrupt/resume
  - execute_approved_tools: executes approved tools
- Edges and routing predicates:
  - chat -> tool_call (if response_message.tool_calls and no HITL tools)
  - chat -> approval_gate (if tool_calls and requires_approval(tool_name) true)
  - chat -> END (no tool calls)
  - tool_call -> chat
  - approval_gate -> execute_approved_tools (approved)
  - approval_gate -> END (rejected)
  - execute_approved_tools -> chat
- Text-based topology:
  START -> chat
     chat -> END
     chat -> tool_call -> chat
     chat -> approval_gate -> execute_approved_tools -> chat
     chat -> approval_gate -> END
- Supervisor/router pattern: Single-agent graph; no supervisor.
- Checkpointing: LangGraph AsyncPostgresSaver with checkpoint tables (`checkpoints`, `checkpoint_blobs`, `checkpoint_writes`) using `settings.DATABASE_URL` in `create_graph`.

1.2 Tool Registry and Contracts
- Tool registry: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/__init__.py`
- Tools listed and contracts (LLM-visible via @tool docstrings):

1) duckduckgo_search
- Description: web search tool (DuckDuckGo).
- Input schema: from langchain_community DuckDuckGoSearchResults (query string). (NEEDS VERIFICATION: schema from library)
- Output schema: list of search results as string/JSON.
- Side effects: external web request.
- Idempotency: safe for retries.
- Error handling: handle_tool_error=True (tool returns error string).

2) search_deals
- File: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py`
- Input schema: SearchDealsInput(query:str, limit:int). No extra forbid.
- Output: string (response.text) or error string.
- Side effects: RAG REST call at `RAG_REST_URL`.
- Idempotency: safe.
- Error handling: ConnectError raises in prod; returns mock in dev.

3) get_deal
- Input schema: GetDealInput(deal_id). No extra forbid.
- Output: string (JSON on 200, plain error string on 404/other) — not a stable JSON schema.
- Side effects: backend GET /api/deals/{id}.
- Idempotency: safe.
- Error handling: ConnectError raises in prod; returns mock in dev.
- Evidence: `deal_tools.py:308-352` (see line numbers in report evidence).

4) transition_deal (HITL)
- Input schema: TransitionDealInput(deal_id, from_stage, to_stage, reason). extra=forbid.
- Output: JSON string with ok/error and backend_status.
- Side effects: backend POST /api/deals/{id}/transition and follow-up GET verification.
- Idempotency: uses tool_idempotency_key, but thread_id hardcoded as "agent" in tool payload.
- Error handling: returns JSON error string; fail-closed on connect error in prod.

5) create_deal (declared HITL in docstring, NOT enforced in code)
- Input schema: CreateDealInput (extra=forbid).
- Output: JSON string with ok/deal_id/error.
- Side effects: backend POST /api/deals.
- Idempotency: no idempotency key passed; not safe on retries.
- Error handling: returns JSON error string; fail-closed on connect error.
- Evidence: `deal_tools.py:405-552` (no idempotency key, no HITL enforcement).

6) add_note
- Input schema: AddNoteInput (no extra forbid).
- Output: JSON string with ok/event_id/error.
- Side effects: backend POST /api/deals/{id}/notes.
- Idempotency: none.
- Error handling: JSON error string.

Tool schema tightness: mixed. transition_deal/create_deal use extra=forbid; get_deal/search_deals/add_note do not — LLM can pass unexpected args.

Tool description accuracy: create_deal docstring says HITL required, but HITL list does not include create_deal (mismatch).

1.3 System Prompt and Instruction Architecture
- Prompt file: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/system.md`
- Loader: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/__init__.py` (simple .format, no versioning).
- Prompt content: generic assistant instructions, tool list, stage names; minimal M&A domain guidance.
- Prompt versioning: none; no per-run prompt hash stored.
- Instruction drift risk: low structural complexity, but content does not encode critical rules (grounding, HITL enforcement, deal context, provenance).

1.4 Memory Architecture
- Short-term: LangGraph state with trimming via `prepare_messages` (MAX_TOKENS). (file: `app/utils/graph.py`)
- Long-term: mem0 AsyncMemory with pgvector and OpenAI models (graph.py:103-120). Disabled by default via `DISABLE_LONG_TERM_MEMORY=true` (graph.py:75-77).
- Deal-scoped memory: not implemented. Memory scoped by `actor_id` only when enabled.
- Memory isolation: actor_id is caller-provided and not verified for tenant isolation.

1.5 RAG and Knowledge Retrieval
- RAG usage: only via tool `search_deals` (RAG REST at 8052). No automatic retrieval.
- Vector store: external RAG service; not in agent.
- Freshness/provenance: none in agent. Tool returns raw RAG response without source citations.
- Chunk strategy: not visible in agent; external service.

1.6 HITL Wiring
- HITL triggers: `requires_approval` in `/app/schemas/agent.py` uses HITL_TOOLS={"transition_deal"} only.
- Approval persistence: `approvals` table and `audit_log` in `/app/models/approval.py`.
- Approval flow: /agent/invoke -> LangGraph interrupt -> approval record -> /approvals/{id}:approve -> resume_after_approval.
- Expiry: lazy expiry on list and approve (no background job). `_reclaim_stale_approvals` uses claimed_at TTL.
- Audit trail: `AuditLog` records; but non-HITL tool executions are not recorded.
- Bypass prevention: service token auth; actor_id trusted from request body; no tenant validation.

1.7 Model and Provider Configuration
- Config: `/app/core/config.py` (DEFAULT_LLM_MODEL, VLLM_BASE_URL, OPENAI_API_KEY).
- Provider: ChatOpenAI with base_url (vLLM) or OpenAI; default model Qwen2.5-32B if VLLM_BASE_URL set.
- Provider abstraction layer: partial (LLMRegistry); routing policy exists but not used (`app/core/routing.py`).
- Parameters: temperature, max_tokens, top_p, etc.
- Streaming: `/api/v1/chatbot/chat/stream` uses LangGraph astream.

1.8 Telemetry and Observability
- Logs: structlog with sanitization (`app/core/logging.py`).
- Metrics: Prometheus counters and LLM latency histograms (`app/core/metrics.py`).
- Tracing: Langfuse optional (`app/core/tracing.py`); LocalTraceSink for tests.
- Correlation IDs: no explicit propagation or binding in agent middleware; LoggingContext only binds session_id from JWT (no X-Correlation-ID).
- Decision chain reconstruction: limited; HITL audit logs exist; non-HITL tool executions not recorded.

End-to-End Agent Runtime Flow
1) HTTP request -> /agent/invoke with X-Service-Token (service auth) and actor_id in body.
2) LangGraphAgent.invoke_with_hitl builds config and calls graph. System prompt injected.
3) LLM returns response; if tool_calls:
   - If tool requires approval -> pending_tool_calls -> approval_gate -> interrupt -> approval record created.
   - Else tool_call node executes tool directly.
4) Tool results returned as ToolMessage -> LLM -> final response.
5) For approval: /approvals/{id}:approve claims approval, resumes graph with Command(resume=...). Tool executes, audit logs written.
6) Response returned to caller.

Tool Contract Map (summary)
- Tool -> backend endpoint -> side effects -> idempotency -> error handling
- transition_deal -> POST /api/deals/{id}/transition; side effect: stage update; idempotency: yes (tool_idempotency_key, but thread_id hardcoded); error: JSON string
- create_deal -> POST /api/deals; side effect: create; idempotency: none; error: JSON string
- add_note -> POST /api/deals/{id}/notes; side effect: event; idempotency: none; error: JSON string
- get_deal -> GET /api/deals/{id}; side effect: read; idempotency: safe; error: plain string (not JSON)
- search_deals -> POST /rag/query; side effect: read; idempotency: safe; error: plain string
- duckduckgo_search -> external web; side effect: external network; idempotency: safe; error: handled by tool

Grounding and Data Truth Analysis
- Truth source: backend Postgres via /api/deals endpoints.
- Agent access: only via tools; no enforced grounding in prompt or code (LLM can answer without tools).
- search_deals tool provides RAG results without provenance or freshness checks.
- Memory: long-term memory disabled by default; no deal-scoped memory in agent.

HITL and Audit Trail Analysis
- State machine (observed): pending -> claimed -> approved/rejected/expired.
- State machine diagram (observed):
  pending -> claimed -> approved -> executed
  pending -> claimed -> rejected
  pending -> expired (lazy expiry via list/approve)
- Approvals stored in `approvals` table; audit events in `audit_log`.
- Gaps:
  - create_deal and add_note are not in HITL_TOOLS set (despite prompt). Evidence: `schemas/agent.py:167-172`.
  - No background expiry job; expiry is lazy (list/approve).
  - Actor identity is trusted from request body for service token flows.

Observability and Debuggability Analysis
- No correlation ID propagation; no end-to-end trace across UI -> agent -> backend.
- Logs sanitize content but do not log tool arguments or outcomes in structured way for non-HITL tools.
- Langfuse tracing optional; if disabled, no LLM trace data.

Security and Provider Abstraction Analysis
- Auth: /agent/* uses service token; actor_id not verified; potential tenant leakage.
- JWT auth for /chatbot; session tokens are thread-based, not user-scoped.
- Provider abstraction: partial; routing policy defined but not used; mem0 uses OpenAI even when local vLLM is primary.

Deal-Centric Intelligence Assessment
- System prompt is generic; no M&A-specific reasoning guidance beyond stage list.
- No DealContext object or stage-aware suggestions; no document completeness checks; no M&A domain terms guidance.
- Agent does not compute deal health/score or provide structured deal insights.

What Is Broken / Misaligned / Fragile (Evidence-Based)

P0
1) HITL not enforced for create_deal (prompt says HITL, code does not)
- Evidence: HITL_TOOLS only contains transition_deal (`schemas/agent.py:167-172`), create_deal defined as tool with HITL docstring but no enforcement (`deal_tools.py:405-552`).
- Impact: Agent can create deals without approval.

2) Actor identity unverified for service-token requests
- Evidence: /agent endpoints trust actor_id from request body with service token (`api/v1/agent.py`, comments “trust actor_id”).
- Impact: User can impersonate another actor_id; audit and authorization compromised.

P1
3) Non-idempotent write tools (create_deal, add_note)
- Evidence: create_deal/add_note do not pass idempotency key; no retry guards (`deal_tools.py:487-589`).
- Impact: duplicate creates/notes on retries or LLM re-calls.

4) Tool output schemas inconsistent/unsafe
- Evidence: get_deal returns plain strings on error (not JSON) (`deal_tools.py:325-330`).
- Impact: LLM may misinterpret tool results; no structured error handling.

5) Correlation IDs not propagated
- Evidence: LoggingContextMiddleware binds only session_id from JWT; no X-Correlation-ID handling (`core/middleware.py`).
- Impact: cannot trace user action end-to-end.

P2
6) Long-term memory disabled by default; no deal-scoped memory
- Evidence: DISABLE_LONG_TERM_MEMORY defaults true (`graph.py:75-77`).
- Impact: agent lacks persistent deal context.

7) mem0 uses OpenAI models even in local-vLLM deployments
- Evidence: mem0 config in graph uses provider "openai" for LLM/embedder (`graph.py:119-123`).
- Impact: provider-agnostic requirement violated; hidden cloud dependency.

8) Tool error handling inconsistent; _tool_call lacks try/except
- Evidence: _tool_call directly invokes tool; exceptions bubble (`graph.py:144-165`).
- Impact: tool failure can crash agent invocation.

9) RAG retrieval lacks provenance and freshness
- Evidence: search_deals returns raw response text; no citation, no freshness checks (`deal_tools.py:355-399`).
- Impact: hallucination risk and stale info used in decisions.

P3
10) dev mocks return invalid stage names
- Evidence: get_deal mock uses stage "qualification" (invalid) (`deal_tools.py:335-339`).
- Impact: tests/dev behavior diverges from production stage taxonomy.

11) Prompt lacks M&A domain context and grounding requirements
- Evidence: system prompt is generic; no structured domain reasoning rules (`core/prompts/system.md`).
- Impact: weak deal-centric intelligence.

Failure Modes and Contrarian Risks (Top 25)
Each includes likelihood/impact and evidence path.

1) create_deal executed without HITL
- Likelihood: High; Impact: High
- Evidence: HITL_TOOLS only transition_deal (`schemas/agent.py:167-172`).

2) Duplicate deals/notes from retries
- Likelihood: Medium; Impact: High
- Evidence: create_deal/add_note no idempotency key (`deal_tools.py:487-589`).

3) LLM answers without grounding
- Likelihood: High; Impact: Medium
- Evidence: prompt lacks forced tool usage (`system.md`).

4) Tool errors crash run
- Likelihood: Medium; Impact: High
- Evidence: _tool_call no try/except (`graph.py:144-165`).

5) Actor impersonation via service token
- Likelihood: Medium; Impact: High
- Evidence: actor_id trusted in /agent endpoints (`api/v1/agent.py`).

6) RAG outage causes agent failure
- Likelihood: Medium; Impact: Medium
- Evidence: search_deals ConnectError raises in prod (`deal_tools.py:383-399`).

7) Stale approvals persist (no background expiry)
- Likelihood: Medium; Impact: Medium
- Evidence: expiry only on list/approve (`api/v1/agent.py`).

8) Approval replay attempts succeed
- Likelihood: Low; Impact: Medium
- Evidence: idempotency handled for approved tool execution, but actor_id trust remains.

9) Tool schema mismatch leads to bad calls
- Likelihood: Medium; Impact: Medium
- Evidence: GetDealInput/SearchDealsInput lacks extra forbid; invalid args possible.

10) Stage mismatch due to invalid mock data
- Likelihood: Medium (dev/test); Impact: Low
- Evidence: get_deal mock stage “qualification” (`deal_tools.py:335-339`).

11) Provider fallback not policy-driven
- Likelihood: Medium; Impact: Medium
- Evidence: routing policy unused (`core/routing.py`).

12) Mem0 uses OpenAI even when local-only required
- Likelihood: Medium; Impact: Medium
- Evidence: mem0 config uses provider openai (`graph.py:119-123`).

13) No tool call budget -> infinite loops
- Likelihood: Low; Impact: High
- Evidence: no max tool calls in graph.

14) Missing deal-scoped memory causes context loss
- Likelihood: High; Impact: Medium
- Evidence: no deal memory object; long-term memory disabled.

15) No decision ledger for non-HITL decisions
- Likelihood: High; Impact: Medium
- Evidence: only HITL audit log exists.

16) Web search tool introduces unverified external info
- Likelihood: Medium; Impact: Medium
- Evidence: duckduckgo_search tool available.

17) Error strings not structured -> LLM misreads
- Likelihood: Medium; Impact: Medium
- Evidence: get_deal/search_deals return plain strings.

18) Correlation IDs absent in logs
- Likelihood: High; Impact: Medium
- Evidence: no correlation binding in middleware.

19) M&A domain reasoning missing
- Likelihood: High; Impact: Medium
- Evidence: prompt generic.

20) Approval concurrency (two approvals same tool) not resolved
- Likelihood: Low; Impact: Medium
- Evidence: only first pending tool call used in approval record.

21) Multiple HITL tool calls in one response drop others
- Likelihood: Low; Impact: Medium
- Evidence: invoke_with_hitl uses first_call only.

22) Tool execution results not sanitized
- Likelihood: Low; Impact: Medium
- Evidence: sanitize_llm_output on AI responses only.

23) Database URL mismatch or misconfig
- Likelihood: Medium; Impact: High
- Evidence: .env.example lacks DATABASE_URL; config requires it.

24) Streaming errors not correlated
- Likelihood: Medium; Impact: Low
- Evidence: stream errors log without trace ID.

25) Prompt drift not versioned
- Likelihood: Medium; Impact: Medium
- Evidence: system prompt file with no versioning.

Gap List (Prioritized)
P0
- Enforce HITL for create_deal (and any destructive tool). (S; evidence `schemas/agent.py:167-172`, `deal_tools.py:405-552`)
- Enforce actor_id authorization for service-token invocations (tenant scoping). (M; evidence `api/v1/agent.py`)
P1
- Idempotency keys for create_deal/add_note and tool retry safety. (M; evidence `deal_tools.py:487-589`)
- Structured tool output schema (ToolResult) and tool error handling in _tool_call. (M; evidence `graph.py:144-165`, `deal_tools.py`)
- Correlation ID propagation across UI -> agent -> backend. (M; evidence `core/middleware.py`, `deal_tools.py`)
P2
- Deal-scoped memory and DealContext object. (M; evidence `graph.py:75-120`, `utils/graph.py`)
- RAG provenance + freshness checks. (L; evidence `deal_tools.py:355-399`)
- Provider abstraction: use routing policy; remove OpenAI dependency in mem0 or make optional. (M; evidence `core/routing.py`, `graph.py:119-123`)
P3
- Prompt versioning and domain enrichment. (S; evidence `core/prompts/system.md`)
- Remove invalid dev mocks. (S; evidence `deal_tools.py:335-339`)

Round-3 Implementation Plan (Phased)
Phase A (P0, 3-5 days)
- Add create_deal to HITL_TOOLS and enforce in requires_approval (S, `schemas/agent.py`).
- Validate actor_id against authenticated service token / JWT claims; reject mismatches (M, `api/v1/agent.py`).
- Add idempotency_key to create_deal/add_note payloads and backend support (M, `deal_tools.py`).

Phase B (P1, 1-2 weeks)
- Implement ToolResult schema and wrap all tool outputs with success/data/error/metadata (M, tool modules + graph parsing).
- Add try/except in _tool_call to prevent tool exceptions crashing runs (S, `graph.py`).
- Add correlation_id middleware; bind to logs and forward to backend headers (M, `core/middleware.py`, `deal_tools.py`).

Phase C (P2, 1-2 weeks)
- Implement DealContext loader: get_deal + notes + approvals summary; inject before response (M).
- Add deal memory store (deal_id scoped) and RAG provenance; freshness policy (L).
- Use routing policy for provider selection; remove OpenAI-only mem0 dependency or make optional (M).

Phase D (P2, 1-2 weeks)
- Decision ledger: append-only table logging tool decisions (L).
- Evals: extend golden traces to cover HITL, idempotency, grounding, and M&A logic (M).

Dependency Graph (must-hold)
- A1 HITL enforcement -> A2 idempotency -> B1 ToolResult -> C1 DealContext -> D1 decision ledger
- A2 idempotency -> B2 correlation ID propagation -> D1 decision ledger (needs trace IDs)
- B1 ToolResult -> B3 tool error handling -> C1 DealContext (stable tool outputs)

Verification and Evals Plan
- Unit tool tests: tool input/output schema, idempotency, error handling. (NEEDS VERIFICATION: test runner wiring)
- Golden traces (existing): expand with create_deal HITL and non-HITL tool constraints.
- CI command (existing): `CI=true python3 apps/agent-api/evals/golden_trace_runner.py` (from `evals/golden_trace_runner.py`).
- Local integration command: `python3 apps/agent-api/evals/golden_trace_runner.py` (requires agent running at localhost:8095).
- Scenario tests: 20+ with expected tool sequence; require 95% tool accuracy and 100% HITL compliance.
- Adversarial tests: prompt injection, auth bypass, repeated tool calls, RAG down.
- Logging checks: correlation_id present in agent logs + backend deal_events; p95 latency target <= 3s for tool-free responses.

Decision Ledger and Observability Blueprint
- Add decision_ledger table with fields: decision_id, timestamp, trace_id, thread_id, user_id, deal_id, tool_name, tool_args_hash, tool_result, hitl_required, approval_id, outcome.
- Emit OpenTelemetry spans: agent_turn, llm_call, tool_execution, hitl_checkpoint, rag_retrieval.

Scorecard (Current -> Target -> Delta Plan -> Proof Plan)
1) Grounding and truthfulness
- Current: 4/10; Target: 9/10
- Delta plan: Mandatory get_deal/search_deals before answering deal questions; ToolResult schema enforced.
- Proof plan: Golden traces require tool calls for deal queries; 0 hallucination findings in adversarial tests.

2) Tool reliability
- Current: 5/10; Target: 9/10
- Delta plan: Idempotency keys for all write tools; tool budget; structured error handling.
- Proof plan: Unit tests show double-call is safe; tool error returns success=false with error.

3) Prompt/system instruction quality
- Current: 3/10; Target: 8/10
- Delta plan: M&A domain prompt, HITL rules, grounding policy, prompt versioning hash.
- Proof plan: Prompt version logged in traces; scenario tests show stage-aware suggestions.

4) Memory/RAG correctness
- Current: 2/10; Target: 8/10
- Delta plan: Deal-scoped memory + provenance + freshness checks.
- Proof plan: RAG results include citations + timestamps; stale results flagged in responses.

5) HITL correctness
- Current: 5/10; Target: 9/10
- Delta plan: HITL coverage for create_deal/add_note; expiry job; approval replay protection.
- Proof plan: Golden traces show HITL triggers 100%; approval audit log entries for every HITL decision.

6) Observability/tracing
- Current: 4/10; Target: 9/10
- Delta plan: Correlation IDs propagated; decision ledger; OpenTelemetry spans.
- Proof plan: Trace shows UI -> agent -> backend; decision ledger row for each tool action.

7) Security/permissions
- Current: 4/10; Target: 9/10
- Delta plan: actor_id verification; tenant scoping; deny cross-tenant access.
- Proof plan: Adversarial tests for impersonation fail with 403; audit log records actor_id from auth claims.

8) Provider abstraction
- Current: 5/10; Target: 8/10
- Delta plan: Use routing policy; remove hard OpenAI dependency for mem0 or make optional; fallback chain.
- Proof plan: Config-only provider swap passes golden traces; no OpenAI key required in local-only mode.

9) Stage-aware reasoning
- Current: 3/10; Target: 8/10
- Delta plan: DealContext object + stage-aware action templates and allowed transitions.
- Proof plan: Scenario tests verify correct stage-aware suggestions; invalid transitions are refused.

10) Evals and regression gates
- Current: 6/10; Target: 9/10
- Delta plan: Expand golden traces; add CI gates for tool selection accuracy and HITL compliance.
- Proof plan: CI blocks on <95% tool accuracy or any HITL miss.

NOT FOUND / NEEDS VERIFICATION
- QA verification baseline file: `/home/zaks/bookkeeping/docs/QA_VERIFICATION_006_REPORT.md` not found. Search recommended in `/home/zaks/bookkeeping/qa/`.
- Prior Round-3 forensic artifacts: AGENT_BRAIN_ROUND3_FORENSIC.md, AGENT_FORENSIC_001_REPORT.md, ZAKOPS_AGENT_API_FORENSIC_PLAN.md not found.
