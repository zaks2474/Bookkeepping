AGENT IDENTITY
- agent_name: Codex
- run_id: 20260204-1958-c47151
- date_time: 2026-02-04T19:58:24Z
- repo_revision: 559a5d1f5c6d22adfd90fd767191dcd421f8732a

Top 30 Failure Modes Still Possible
1) Destructive create_deal executes without HITL approval
- Detection: Approvals table has no pending approval while audit_log shows create_deal side effects; golden trace expecting pending_approval fails
- Mitigation: Add create_deal to HITL_TOOLS and enforce requires_approval
- Rollback: Disable create_deal tool or feature-flag write tools to require manual approval
- Source: ZK-BRAIN-ISSUE-0001
2) Agent answers deal facts without grounding (hallucinates/stale data)
- Detection: LLM response contains deal stage/amount without preceding get_deal/search_deals tool call; golden trace grounding tests fail
- Mitigation: Enforce grounding policy in prompt and graph (must call get_deal before deal answers)
- Rollback: Force read-only mode: block deal-specific answers unless tool call succeeded
- Source: ZK-BRAIN-ISSUE-0002
3) No tracing in production due to missing Langfuse config
- Detection: Langfuse dashboard has no traces; startup logs show missing LANGFUSE keys
- Mitigation: Configure LANGFUSE_PUBLIC_KEY/SECRET and add startup health check
- Rollback: Enable local trace sink or OpenTelemetry exporter until Langfuse is configured
- Source: ZK-BRAIN-ISSUE-0003
4) Actor impersonation via service-token requests
- Detection: Audit log shows actor_id not matching authenticated service token claims; adversarial test passes with fake actor_id
- Mitigation: Validate actor_id against auth claims; enforce tenant scoping
- Rollback: Disable service-token endpoints or restrict to internal service identity only
- Source: ZK-BRAIN-ISSUE-0004
5) Agent is amnesic because long-term memory disabled
- Detection: Memory store empty; DISABLE_LONG_TERM_MEMORY=true; agent fails to recall prior info in evals
- Mitigation: Enable mem0/pgvector and verify retention settings
- Rollback: Use deal context loader as minimal persistent memory (DB-backed)
- Source: ZK-BRAIN-ISSUE-0005
6) No deal-scoped memory; agent forgets deal-specific history
- Detection: Deal follow-up questions require re-specifying deal context; evals show missing recall
- Mitigation: Implement deal-scoped memory and DealContext loader
- Rollback: Force explicit get_deal + recent_notes tool calls per turn
- Source: ZK-BRAIN-ISSUE-0006
7) Prompt lacks M&A intelligence; bad stage reasoning
- Detection: Agent suggests invalid transitions or omits M&A terms in scenario tests
- Mitigation: Rewrite system prompt with M&A taxonomy, allowed transitions, and examples
- Rollback: Add validation guardrails in transition tool; block invalid transitions
- Source: ZK-BRAIN-ISSUE-0007
8) Tool call loop with no budget leads to runaway execution
- Detection: Repeated tool calls in logs; request exceeds timeout; high tool_call_count
- Mitigation: Add tool call budget per turn and per conversation; hard-stop with error
- Rollback: Throttle tool calls and enforce max tokens
- Source: ZK-BRAIN-ISSUE-0008
9) Prompt changes are untraceable (no versioning)
- Detection: Cannot identify which prompt version produced a response in logs
- Mitigation: Add prompt version header and hash; log per request
- Rollback: Pin prompt to last known good version; block deployment without version
- Source: ZK-BRAIN-ISSUE-0009
10) Evals are not gating deployments (CI missing)
- Detection: CI pipeline allows merge despite golden trace failures
- Mitigation: Add CI gate with golden_trace_runner and fail on regressions
- Rollback: Manual release freeze until evals pass
- Source: ZK-BRAIN-ISSUE-0010
11) No correlation_id propagation (debugging impossible)
- Detection: Logs cannot be tied across UI -> agent -> backend; missing X-Correlation-ID
- Mitigation: Add middleware to ingest/propagate correlation_id and inject into tool calls
- Rollback: Use request_id as temporary correlation until full propagation
- Source: ZK-BRAIN-ISSUE-0011
12) Non-idempotent write tools cause duplicate creates/notes
- Detection: Duplicate deals/notes with same payload in DB; retries correlate with duplicates
- Mitigation: Add idempotency_key for create_deal/add_note and backend enforcement
- Rollback: Disable retries for write tools; manual dedupe job
- Source: ZK-BRAIN-ISSUE-0012
13) Tool output schema mismatch (plain strings on errors)
- Detection: Tool outputs are not JSON; LLM misparses errors and proceeds
- Mitigation: Standardize ToolResult schema with success/data/error
- Rollback: Force error outputs to be JSON-wrapped before passing to LLM
- Source: ZK-BRAIN-ISSUE-0013
14) mem0 hard-depends on OpenAI even when local-vLLM required
- Detection: OpenAI API calls during local-only deployments; missing API key failures
- Mitigation: Make mem0 provider configurable and support local embeddings
- Rollback: Disable mem0 and rely on DB-backed DealContext
- Source: ZK-BRAIN-ISSUE-0014
15) Tool exceptions crash the agent (no try/except)
- Detection: Unhandled exception stack traces from _tool_call; 500 responses
- Mitigation: Wrap tool calls with try/except; return ToolResult error
- Rollback: Feature-flag error-resilient mode to bypass tool calls
- Source: ZK-BRAIN-ISSUE-0015
16) RAG results stale or unverifiable (no provenance/freshness)
- Detection: RAG responses lack source metadata or timestamps; user reports stale data
- Mitigation: Require provenance metadata and freshness checks on RAG results
- Rollback: Fallback to DB queries or require manual confirmation
- Source: ZK-BRAIN-ISSUE-0016
17) No decision ledger for non-HITL actions
- Detection: Cannot reconstruct why a tool was called; audit_log lacks reasoning
- Mitigation: Add decision_ledger table logging tool decisions and outcomes
- Rollback: Increase verbose logging for tool selection reasoning
- Source: ZK-BRAIN-ISSUE-0017
18) Prompt/tool list drift (hardcoded tool list)
- Detection: System prompt lists tools that differ from registry; tool errors in logs
- Mitigation: Generate tool list dynamically from registry; prompt template uses runtime tool names
- Rollback: Add CI check to diff prompt tool list against registry
- Source: ZK-BRAIN-ISSUE-0018
19) No response logging (cannot audit output quality)
- Detection: No stored responses for post-incident review; logs only inputs
- Mitigation: Add response logging with redaction and retention policy
- Rollback: Enable temporary debug logging for selected sessions
- Source: ZK-BRAIN-ISSUE-0019
20) Eval coverage too small (10 traces) misses regressions
- Detection: New defects appear despite passing evals; eval set <30 cases
- Mitigation: Expand golden traces and add adversarial suite
- Rollback: Manual QA hold on releases until suite expanded
- Source: ZK-BRAIN-ISSUE-0020
21) Stage transition rules missing in prompt
- Detection: Agent suggests invalid transitions in scenario tests
- Mitigation: Add stage transition matrix to prompt and enforce in tools
- Rollback: Hard-block invalid transitions at tool level
- Source: ZK-BRAIN-ISSUE-0021
22) Dev mocks use invalid stage names causing test drift
- Detection: Local tests show stage values not in enum; mismatch with prod
- Mitigation: Fix mock data to use valid stage enums
- Rollback: Disable mocks and require integration tests
- Source: ZK-BRAIN-ISSUE-0022
23) No deal health scoring; agent cannot triage pipeline risk
- Detection: Agent responses lack health indicators; no health score computed
- Mitigation: Implement deal health scoring and expose in DealContext
- Rollback: Manual scoring in UI until agent scoring exists
- Source: ZK-BRAIN-ISSUE-0023
24) No next-step recommendations; weak deal guidance
- Detection: Agent replies are generic; no stage-aware next steps
- Mitigation: Add stage-aware action suggestions in prompt/DealContext
- Rollback: Link to static playbooks as interim guidance
- Source: ZK-BRAIN-ISSUE-0024
25) LLM reasoning not captured; audit trails incomplete
- Detection: No stored reasoning metadata; cannot explain tool choice
- Mitigation: Capture reasoning metadata in decision ledger (tools_considered, rationale)
- Rollback: Capture minimal rationale fields in audit_log
- Source: ZK-BRAIN-ISSUE-0025
26) RAG outage or errors appear as empty results (false negatives)
- Detection: RAG service down but agent says 'no deals found'; error logs in search_deals
- Mitigation: Circuit breaker + explicit error surfaced to LLM; fallback to DB search
- Rollback: Disable search_deals tool and use direct DB lookup
- Source: Codex report FM-6 / Gemini contrarian risk #5
27) Multiple HITL tool calls in one response drop all but first
- Detection: LLM emits multiple HITL tool calls; only first executed; others ignored
- Mitigation: Queue all HITL tool calls or enforce single-tool-call policy
- Rollback: Reject multi-tool-call responses and request single action
- Source: Codex report FM-21
28) Stale approvals never expire (zombie approvals)
- Detection: Approvals remain pending/claimed beyond TTL; no expiry job runs
- Mitigation: Add background expiry job and enforce TTL on resume
- Rollback: Manual cleanup script; disable long-lived approvals
- Source: Codex report FM-7
29) Prompt injection causes policy bypass
- Detection: Adversarial prompt tests override tool usage or HITL rules
- Mitigation: Add prompt injection guardrails and evaluate with adversarial suite
- Rollback: Disable high-risk tools for untrusted inputs
- Source: Claude-Opus report contrarian risk #5 / Gemini contrarian risk #3
30) Malformed tool call JSON from model breaks parsing
- Detection: LLM outputs invalid tool call JSON; tool parser errors in logs
- Mitigation: Add robust tool call parser with repair or re-ask pattern
- Rollback: Fallback to non-tool response with explicit error
- Source: Claude-Opus report contrarian risk #10

Patch Set (Plan Edits)
- P0-HITL-001: Add create_deal (and any other write tools like add_note if required) to HITL_TOOLS and enforce in requires_approval logic
  - Where: Phase 0: Safety/HITL Enforcement section (HITL gating subsection)
  - Verification: Golden trace: create_deal request returns pending_approval; audit_log shows approval required
  - Sources: ZK-BRAIN-ISSUE-0001
- P0-AUTH-001: Validate actor_id against authenticated service token/JWT claims; enforce tenant scoping; log mismatches
  - Where: Phase 0: Auth & Security section
  - Verification: Adversarial test: fake actor_id returns 403; audit log records auth mismatch
  - Sources: ZK-BRAIN-ISSUE-0004
- P0-GROUND-001: Add grounding enforcement: system prompt rule + graph guard that requires get_deal/search_deals before deal-specific answers
  - Where: Phase 0: Grounding & Data Truth section
  - Verification: Grounding gate test: asking deal stage must trigger get_deal tool call before response
  - Sources: ZK-BRAIN-ISSUE-0002
- P1-TOOL-001: Standardize ToolResult schema (success/data/error/metadata); remove plain-string error returns; add try/except wrapper
  - Where: Phase 1: Tool Contract Reliability section
  - Verification: Unit tests confirm errors return ToolResult.success=false; no raw exceptions bubble
  - Sources: ZK-BRAIN-ISSUE-0013, ZK-BRAIN-ISSUE-0015
- P1-IDEMP-001: Add idempotency_key to create_deal/add_note payloads; enforce in backend
  - Where: Phase 1: Idempotency & Retry Safety section
  - Verification: Idempotency tests: double-call yields same record id; no duplicates
  - Sources: ZK-BRAIN-ISSUE-0012
- P1-BUDGET-001: Implement tool call budget and context/token budget in GraphState; stop after N calls
  - Where: Phase 1: Loop/Budget Control section
  - Verification: Loop test halts at max tool calls and returns controlled error
  - Sources: ZK-BRAIN-ISSUE-0008
- P1-OBS-001: Add correlation_id middleware and propagate to backend headers; configure Langfuse/OTel
  - Where: Phase 1: Observability & Tracing section
  - Verification: Log query shows same correlation_id across UI->agent->backend; traces visible in Langfuse
  - Sources: ZK-BRAIN-ISSUE-0011, ZK-BRAIN-ISSUE-0003
- P1-PROMPT-001: Add prompt versioning + hash; generate tool list dynamically to avoid drift
  - Where: Phase 1: Prompt Governance section
  - Verification: Prompt version logged per request; CI check ensures registry/tool list match
  - Sources: ZK-BRAIN-ISSUE-0009, ZK-BRAIN-ISSUE-0018
- P2-MEM-001: Enable long-term memory; implement deal-scoped memory + DealContext object
  - Where: Phase 2: Memory & Deal Intelligence section
  - Verification: Deal follow-up queries use stored context; memory retrieval scoped by deal_id
  - Sources: ZK-BRAIN-ISSUE-0005, ZK-BRAIN-ISSUE-0006
- P2-RAG-001: Add RAG provenance/freshness metadata and fallback path when RAG down
  - Where: Phase 2: RAG Reliability section
  - Verification: RAG-down test returns explicit error and uses DB fallback; responses include provenance
  - Sources: ZK-BRAIN-ISSUE-0016
- P2-DEC-001: Create decision ledger for non-HITL actions; capture reasoning metadata
  - Where: Phase 2: Decision Ledger & Audit section
  - Verification: Every tool call inserts ledger row with trace_id and rationale
  - Sources: ZK-BRAIN-ISSUE-0017, ZK-BRAIN-ISSUE-0025, ZK-BRAIN-ISSUE-0019
- P2-EVAL-001: Expand golden traces to >=30; add CI gate + adversarial suite (prompt injection, malformed tool calls, outages)
  - Where: Phase 2: Evals & Regression section
  - Verification: CI fails on any golden trace regression; adversarial suite executed
  - Sources: ZK-BRAIN-ISSUE-0010, ZK-BRAIN-ISSUE-0020
- P2-STAGE-001: Add stage transition rules and stage-aware recommendations to prompt + DealContext
  - Where: Phase 2: Stage Intelligence section
  - Verification: Scenario tests show valid transitions only; next-step recommendations present
  - Sources: ZK-BRAIN-ISSUE-0021, ZK-BRAIN-ISSUE-0024
- P2-INTEL-001: Add deal health scoring and surface in responses
  - Where: Phase 2: Deal Intelligence section
  - Verification: Health score computed for deals and included in DealContext
  - Sources: ZK-BRAIN-ISSUE-0023
- P2-PROVIDER-001: Make mem0 provider configurable; support local embeddings; remove hard OpenAI dependency
  - Where: Phase 2: Provider Abstraction section
  - Verification: Local-only deployment passes without OpenAI key; golden traces succeed
  - Sources: ZK-BRAIN-ISSUE-0014
- P3-MOCK-001: Fix invalid dev mocks (stage enums) to align with production taxonomy
  - Where: Phase 3: Test/Dev Parity section
  - Verification: Dev mocks use valid stage enums; unit tests pass
  - Sources: ZK-BRAIN-ISSUE-0022

Tough Gates Blueprint
- Gate A: Tool unit tests + ToolResult schema
  - All tools return ToolResult with success/data/error
  - Schema validation tests for each tool input
  - Error handling returns success=false (no raw exceptions)
  - Evidence: Unit test logs + sample ToolResult payloads
  - Sources: ZK-BRAIN-ISSUE-0013, ZK-BRAIN-ISSUE-0015
- Gate B: HITL enforcement tests
  - create_deal and transition_deal require approval
  - Bypass attempts fail and are audited
  - Evidence: Golden trace for create_deal returns pending_approval; audit_log shows approval required
  - Sources: ZK-BRAIN-ISSUE-0001
- Gate C: Grounding tests
  - Deal fact questions must call get_deal/search_deals
  - No answer if tool call fails
  - Evidence: Scenario tests show tool call before answer; responses blocked on tool failure
  - Sources: ZK-BRAIN-ISSUE-0002
- Gate D: Idempotency/retry tests
  - create_deal/add_note double-call yields no duplicates
  - Backend enforces idempotency key
  - Evidence: DB queries show single record after double-call
  - Sources: ZK-BRAIN-ISSUE-0012
- Gate E: Auth impersonation tests
  - actor_id must match auth claims
  - Cross-tenant access returns 403
  - Evidence: Adversarial test logs; audit entry for mismatch
  - Sources: ZK-BRAIN-ISSUE-0004
- Gate F: Observability proof
  - correlation_id present in UI, agent, backend logs
  - Langfuse/OTel traces visible for agent_turn + tool_execution
  - Evidence: Trace sample with shared correlation_id across services
  - Sources: ZK-BRAIN-ISSUE-0011, ZK-BRAIN-ISSUE-0003
- Gate G: Eval regression gate in CI
  - golden_trace_runner in CI
  - >=30 golden traces
  - adversarial suite for prompt injection, malformed tool calls, outages
  - Evidence: CI logs show eval run; failures block merge
  - Sources: ZK-BRAIN-ISSUE-0010, ZK-BRAIN-ISSUE-0020

Ship Criteria
- All P0/P1 issues closed with verified evidence
- Gates A-G pass in CI and staging
- Grounding compliance >= 99% on golden traces
- HITL compliance 100% for destructive tools
- Idempotency tests show 0 duplicates across retries
- Correlation ID present end-to-end in logs and traces
- Langfuse/OTel traces available for 95%+ of requests
- Adversarial suite passes (prompt injection, RAG outage, malformed tool calls)

Notes
- QA baseline file QA_VERIFICATION_006_REPORT.md not found. NEEDS VERIFICATION: check /home/zaks/bookkeeping/qa/ or regenerate.
