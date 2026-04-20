AGENT IDENTITY
- agent_name: Codex
- run_id: 20260204-2004-4b2f4e
- date_time: 2026-02-04T20:04:19Z
- repo_revision: 559a5d1f5c6d22adfd90fd767191dcd421f8732a

Decision Set (Must Decide Now)
- HITL policy: Enforce HITL for all destructive write tools (create_deal, transition_deal, add_note if required); centrally enforced in requires_approval with tests.
- Grounding policy: For any deal-specific answer, require successful get_deal/search_deals; refuse with explicit error if unavailable.
- ToolResult schema: Adopt unified ToolResult with success/data/error/metadata; no plain string errors; robust parsing for malformed tool calls.
- Idempotency + retry: All write tools include idempotency_key; backend enforces de-dupe; retry semantics documented.
- Auth model: actor_id must be verified against auth claims; no caller-supplied impersonation; tenant scoping required.
- Memory strategy: Enable long-term memory with deal-scoped retrieval and privacy controls (Forget tool).
- RAG strategy: RAG results require provenance + freshness; add SQL/DB fallback; explicit outage behavior.
- Observability: correlation_id propagation; Langfuse/OTel tracing; prompt version tracking; response logging with redaction.
- Evals: Expand golden traces to >=30 + adversarial suite; CI gate blocks regressions.

Phased Implementation Plan
Phase 0 — Safety & Auth Hard Stop
- Objective: Eliminate P0 unsafe behavior (HITL gaps, grounding, auth impersonation).
- Atomic tasks:
  - Add create_deal (and any write tools requiring approval, e.g., add_note if policy requires) to HITL_TOOLS and enforce centrally in requires_approval.
  - Enforce grounding policy in system prompt and add graph guard: deal-specific answers require get_deal/search_deals success.
  - Validate actor_id against auth claims for service-token requests; enforce tenant scoping and audit mismatches.
  - Add HITL bypass tests and grounding tests to eval harness.
- Dependencies: None
- Risks: Over-blocking legitimate flows; false HITL prompts.
- Rollback: Feature-flag HITL enforcement and grounding guard; disable write tools temporarily.
- Gates + acceptance criteria:
  - Gate B (HITL enforcement tests) must pass
  - Gate C (Grounding tests) must pass
  - Gate E (Auth impersonation tests) must pass
- Evidence required:
  - Golden trace showing create_deal returns pending_approval
  - Grounding test showing get_deal called before response
  - Adversarial auth test returns 403 on fake actor_id

Phase 1 — Tool Contract Reliability & Loop Control
- Objective: Make tool calls safe, structured, idempotent, and bounded.
- Atomic tasks:
  - Introduce ToolResult schema (success/data/error/metadata) and wrap all tool outputs; remove plain-string errors.
  - Add try/except around tool execution in _tool_call; return ToolResult error on exceptions.
  - Add idempotency_key to create_deal/add_note payloads and backend enforcement; document retry semantics.
  - Implement tool call budget (per turn and per conversation) and token budget guard.
  - Harden tool call parsing for malformed JSON; re-ask or fail with controlled error.
  - Fix dev mocks to use valid stage enums.
- Dependencies: Phase 0 completed
- Risks: Breaking changes in tool response handling; existing clients expect strings.
- Rollback: Feature-flag ToolResult output and provide backward-compatible wrapper.
- Gates + acceptance criteria:
  - Gate A (Tool unit tests + ToolResult schema)
  - Gate D (Idempotency/retry tests)
- Evidence required:
  - Unit tests show ToolResult success=false on errors
  - DB queries prove idempotency on double-call
  - Loop test halts at max tool calls

Phase 2 — Observability & Prompt Governance
- Objective: Make decisions traceable and prompts auditable; improve debugability.
- Atomic tasks:
  - Propagate correlation_id end-to-end (UI -> agent -> backend); bind to logs and tool headers.
  - Configure Langfuse/OTel tracing with startup health checks; ensure prompt_version logged per request.
  - Implement prompt versioning (header + hash) and dynamic tool list injection to prevent drift.
  - Add response logging with redaction and retention policy.
  - Create decision ledger for all tool actions with reasoning metadata.
- Dependencies: Phase 1 completed
- Risks: PII exposure in logs; increased storage costs.
- Rollback: Enable redaction-only logging mode; reduce retention window.
- Gates + acceptance criteria:
  - Gate F (Observability proof) must pass
  - Prompt version logged and tool list matches registry
- Evidence required:
  - Trace sample shows correlation_id across services
  - Langfuse/OTel spans present for agent_turn/tool_execution
  - Decision ledger row per tool call with rationale

Phase 3 — Memory, RAG & Provider Hardening
- Objective: Enable reliable memory and deal-centric retrieval with provenance and fallback.
- Atomic tasks:
  - Enable long-term memory (mem0/pgvector) and add privacy controls (Forget tool).
  - Implement deal-scoped memory and DealContext loader.
  - Make mem0 provider configurable; support local embeddings to avoid OpenAI hard dependency.
  - Add RAG provenance + freshness metadata; implement SQL/DB fallback and circuit breaker when RAG is down.
- Dependencies: Phase 2 completed
- Risks: Memory contamination across tenants; stale RAG results.
- Rollback: Disable long-term memory; force explicit get_deal + recent_notes on each turn.
- Gates + acceptance criteria:
  - RAG outage test must return explicit error + fallback
  - Memory retrieval tests confirm deal_id scoping
- Evidence required:
  - Memory store shows deal-scoped entries
  - RAG results include provenance and timestamps

Phase 4 — Deal Intelligence & Evals/CI
- Objective: Make the agent deal-smart and prevent regressions.
- Atomic tasks:
  - Add stage transition matrix to prompt and enforce in tools; include stage-aware next-step recommendations.
  - Implement deal health scoring and surface in DealContext.
  - Expand golden traces to >=30 and add adversarial suite (prompt injection, malformed tool calls, outages).
  - Add CI gates to block deployment on eval regressions.
- Dependencies: Phase 3 completed
- Risks: Eval suite flakiness; insufficient test coverage.
- Rollback: Manual QA hold; rollback prompt to last known good version.
- Gates + acceptance criteria:
  - Gate G (Eval regression gate) must pass
  - Stage rule tests must pass
- Evidence required:
  - CI logs show golden_trace_runner + adversarial suite
  - Scenario tests show valid transitions and next-step recommendations

NO-DROP Coverage Matrix
- Each issue maps to phase, task, verification, and Definition of Done (DoD)
ZK-BRAIN-ISSUE-0001: create_deal not in HITL_TOOLS despite being destructive
- Phase: Phase 0
- Task: HITL enforcement
- Verification: Golden trace pending_approval
- DoD: HITL tool requires approval
ZK-BRAIN-ISSUE-0002: No grounding enforcement — agent can hallucinate deal details
- Phase: Phase 0
- Task: Grounding guard + prompt policy
- Verification: Grounding test requires get_deal
- DoD: No deal answers without tool call
ZK-BRAIN-ISSUE-0003: Langfuse tracing not configured in production
- Phase: Phase 2
- Task: Langfuse/OTel config + health check
- Verification: Trace appears in Langfuse
- DoD: Traces for >=95% of requests
ZK-BRAIN-ISSUE-0004: Actor identity unverified for service-token requests (impersonation risk)
- Phase: Phase 0
- Task: actor_id verification
- Verification: Adversarial test 403
- DoD: Auth mismatch blocked + audited
ZK-BRAIN-ISSUE-0005: Long-term memory disabled by default
- Phase: Phase 3
- Task: Enable long-term memory
- Verification: env shows DISABLE_LONG_TERM_MEMORY=false
- DoD: Memory writes/reads succeed
ZK-BRAIN-ISSUE-0006: No deal-scoped memory
- Phase: Phase 3
- Task: Deal-scoped memory + DealContext
- Verification: Deal follow-up test uses memory
- DoD: Deal_id scoped retrieval
ZK-BRAIN-ISSUE-0007: System prompt lacks M&A domain intelligence
- Phase: Phase 4
- Task: M&A prompt + stage guidance
- Verification: Scenario tests with M&A terms
- DoD: Prompt includes M&A taxonomy
ZK-BRAIN-ISSUE-0008: No tool call budget enforcement (infinite loop risk)
- Phase: Phase 1
- Task: Tool call budget
- Verification: Loop test halts at limit
- DoD: Max tool calls enforced
ZK-BRAIN-ISSUE-0009: No prompt versioning
- Phase: Phase 2
- Task: Prompt versioning
- Verification: Prompt hash logged
- DoD: Prompt version present in logs
ZK-BRAIN-ISSUE-0010: Evals have no CI gate (only 10 golden traces)
- Phase: Phase 4
- Task: CI gate for evals
- Verification: CI fails on eval regression
- DoD: Golden traces in CI
ZK-BRAIN-ISSUE-0011: No correlation_id propagation across systems
- Phase: Phase 2
- Task: Correlation_id propagation
- Verification: Log sample shows shared correlation_id
- DoD: End-to-end traceability
ZK-BRAIN-ISSUE-0012: Non-idempotent write tools (create_deal, add_note)
- Phase: Phase 1
- Task: Idempotency keys for writes
- Verification: DB shows no duplicates
- DoD: Idempotent retry safe
ZK-BRAIN-ISSUE-0013: Tool output schemas inconsistent
- Phase: Phase 1
- Task: ToolResult schema
- Verification: Unit tests show ToolResult
- DoD: No plain-string errors
ZK-BRAIN-ISSUE-0014: mem0 uses OpenAI provider even in local-vLLM deployments
- Phase: Phase 3
- Task: Configurable mem0 provider
- Verification: Local-only deployment works without OpenAI
- DoD: Provider switch via config
ZK-BRAIN-ISSUE-0015: Tool error handling inconsistent; _tool_call lacks try/except
- Phase: Phase 1
- Task: Tool try/except
- Verification: Tool error returns ToolResult
- DoD: No uncaught exceptions
ZK-BRAIN-ISSUE-0016: RAG retrieval lacks provenance and freshness
- Phase: Phase 3
- Task: RAG provenance/freshness + fallback
- Verification: RAG outage test passes
- DoD: RAG results include sources/timestamps
ZK-BRAIN-ISSUE-0017: No decision ledger for non-HITL tool decisions
- Phase: Phase 2
- Task: Decision ledger
- Verification: Decision ledger row exists
- DoD: All tool actions logged
ZK-BRAIN-ISSUE-0018: Prompt drift (tool list hardcoded, not dynamic)
- Phase: Phase 2
- Task: Dynamic tool list in prompt
- Verification: CI check passes
- DoD: Prompt tool list matches registry
ZK-BRAIN-ISSUE-0019: No response logging
- Phase: Phase 2
- Task: Response logging with redaction
- Verification: Sample response log exists
- DoD: Retention/redaction policy enforced
ZK-BRAIN-ISSUE-0020: Only 10 golden traces (insufficient eval coverage)
- Phase: Phase 4
- Task: Expand golden traces to >=30
- Verification: Trace count >=30
- DoD: Eval coverage report
ZK-BRAIN-ISSUE-0021: No stage transition rules in prompt
- Phase: Phase 4
- Task: Stage transition rules in prompt + tools
- Verification: Invalid transition blocked
- DoD: Stage matrix present
ZK-BRAIN-ISSUE-0022: Dev mock uses invalid stage name
- Phase: Phase 1
- Task: Fix dev mocks
- Verification: Tests show valid stages
- DoD: No invalid stage in mocks
ZK-BRAIN-ISSUE-0023: No deal health scoring
- Phase: Phase 4
- Task: Deal health scoring
- Verification: Health score appears in DealContext
- DoD: Score computed for active deals
ZK-BRAIN-ISSUE-0024: No next-step recommendations
- Phase: Phase 4
- Task: Next-step recommendations
- Verification: Scenario tests include next steps
- DoD: Recommendations present per stage
ZK-BRAIN-ISSUE-0025: No LLM reasoning capture
- Phase: Phase 2
- Task: Reasoning capture in decision ledger
- Verification: Decision ledger includes rationale
- DoD: Reasoning fields populated

Builder Mission Sequence (Execution-Ready Prompts)
Builder Mission 1 — Safety/HITL/Auth/Grounding
- REPO: /home/zaks/zakops-agent-api
- GATE: Gate B + Gate C + Gate E
- Scope boundaries: HITL enforcement, actor_id verification, grounding policy + guard
- Acceptance criteria:
  - create_deal returns pending_approval
  - fake actor_id returns 403
  - deal fact question triggers get_deal before answer
- Evidence required:
  - Golden trace output
  - Audit log with approval_required
  - Adversarial auth test output
- Blocker policy: If HITL or auth cannot be enforced safely, disable write tools and document action item.
- Next mission rule: Proceed to Mission 2 when all P0 gates pass.

Builder Mission 2 — ToolResult + Idempotency + Loop Control
- REPO: /home/zaks/zakops-agent-api
- GATE: Gate A + Gate D
- Scope boundaries: ToolResult schema, try/except, idempotency keys, tool call budget, mock fixes
- Acceptance criteria:
  - All tools return ToolResult
  - Idempotency tests show no duplicates
  - Loop test stops at max tool calls
- Evidence required:
  - Unit test logs
  - DB queries showing no duplicates
  - Loop test output
- Blocker policy: If ToolResult breaks clients, add backward-compatible wrapper and document.
- Next mission rule: Proceed to Mission 3 after Gate A/D pass.

Builder Mission 3 — Observability + Prompt Governance
- REPO: /home/zaks/zakops-agent-api
- GATE: Gate F
- Scope boundaries: correlation_id propagation, Langfuse/OTel, prompt versioning, dynamic tool list, response logging, decision ledger
- Acceptance criteria:
  - Trace shows correlation_id across services
  - Prompt version logged per request
  - Decision ledger row per tool call
- Evidence required:
  - Trace screenshots or log snippets
  - Decision ledger DB query
- Blocker policy: If tracing config unavailable, enable local trace sink and log correlation_id for all requests.
- Next mission rule: Proceed to Mission 4 after Gate F passes.

Builder Mission 4 — Memory/RAG/Provider Hardening
- REPO: /home/zaks/zakops-agent-api
- GATE: Memory + RAG outage tests
- Scope boundaries: Enable long-term memory, deal-scoped memory, RAG provenance/freshness + fallback, mem0 provider config
- Acceptance criteria:
  - Deal follow-up uses memory
  - RAG outage falls back to DB and returns explicit error
  - Local-only deployment works without OpenAI
- Evidence required:
  - Memory retrieval logs
  - RAG outage test output
- Blocker policy: If memory causes tenant leakage risk, keep it disabled and rely on DealContext.
- Next mission rule: Proceed to Mission 5 when memory and RAG tests pass.

Builder Mission 5 — Deal Intelligence + Eval Gates
- REPO: /home/zaks/zakops-agent-api
- GATE: Gate G
- Scope boundaries: Stage rules, next-step recommendations, deal health scoring, expand golden traces, add adversarial suite, CI gates
- Acceptance criteria:
  - Invalid transitions blocked
  - Next-step recommendations present
  - CI blocks on eval regression
- Evidence required:
  - Scenario test outputs
  - CI logs with golden_trace_runner
- Blocker policy: If eval suite flakey, quarantine failing traces and document action items.
- Next mission rule: Ship criteria review after Gate G passes.

Final QA Plan for Agent Brain
- Functional QA:
  - HITL approval flows (create_deal, transition_deal)
  - Grounding tests for deal facts
  - Idempotency tests for create_deal/add_note
  - Deal-scoped memory retrieval
  - Stage transition validation
- Adversarial QA:
  - Prompt injection attempts
  - Auth impersonation attempts
  - Malformed tool call JSON
  - RAG outage + fallback
  - Tool loop stress test
- Proof artifacts:
  - Golden trace report
  - CI logs showing eval gates
  - DB queries for idempotency and decision ledger
  - Trace logs with correlation_id
- SHIP IT definition:
  - All P0/P1 issues closed with verification
  - Gates A-G pass in CI and staging
  - Grounding compliance >=99%
  - HITL compliance 100% for destructive tools
  - Idempotency tests show 0 duplicates
  - Traces available for >=95% of requests

Notes
- QA baseline file QA_VERIFICATION_006_REPORT.md not found. NEEDS VERIFICATION: check /home/zaks/bookkeeping/qa/ or regenerate.
