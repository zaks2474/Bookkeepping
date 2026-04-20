# AGENT_BRAIN_ROUND3_EVAL — PASS 1 Report

---

## AGENT IDENTITY

- **agent_name:** Claude-Opus
- **run_id:** 20260204-2045-p1r3
- **date_time:** 2026-02-04T20:45:00Z
- **repo_revision:** 3173c36f714f13524f3d81375483484887a6ac99

---

## A) DEDUPED "ALL KNOWN BRAIN ISSUES" REGISTER (NO DROP)

**Summary Statistics:**
| Severity | Count |
|----------|-------|
| P0 | 4 |
| P1 | 9 |
| P2 | 8 |
| P3 | 4 |
| **Total** | **25** |

---

### P0 — PRODUCTION BLOCKERS

---

#### ZK-BRAIN-ISSUE-0001: create_deal not in HITL_TOOLS despite being destructive

| Field | Value |
|-------|-------|
| **Title** | create_deal not in HITL_TOOLS despite being destructive |
| **Description** | The `create_deal` tool is a write operation that creates deals in the database, but it is NOT included in the `HITL_TOOLS` frozenset. This means the agent can create deals without human approval, despite the docstring claiming HITL is required. The HITL_TOOLS only contains `transition_deal`. |
| **Category** | HITL |
| **Severity** | P0 |
| **Evidence References** | - `schemas/agent.py:167-172` (HITL_TOOLS frozenset)<br>- `deal_tools.py:405-552` (create_deal implementation)<br>- Claude-Opus report G-001<br>- Codex report P0-1 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Add `create_deal` to `HITL_TOOLS` frozenset in `schemas/agent.py`<br>2. Also consider adding `add_note` if it should require approval |
| **Verification Proof** | ```python\n# Test: Call agent with "create a new deal for Acme Corp"\n# Expected: Agent returns pending_approval response\n# Current: Agent creates deal immediately without approval\n``` |
| **Verification Status** | PROVEN — Code inspection confirms HITL_TOOLS = {"transition_deal"} only |

---

#### ZK-BRAIN-ISSUE-0002: No grounding enforcement — agent can hallucinate deal details

| Field | Value |
|-------|-------|
| **Title** | No grounding enforcement — agent can hallucinate deal details |
| **Description** | The system prompt does NOT require the agent to call `get_deal` or `search_deals` before answering deal questions. The agent can fabricate deal information based on conversation context alone without fetching current state from Postgres. This is the single biggest risk identified across all reports. |
| **Category** | Grounding |
| **Severity** | P0 |
| **Evidence References** | - `core/prompts/system.md` (lacks grounding rule)<br>- Claude-Opus report G-002 and FM-001<br>- Codex report P1-3 (LLM answers without grounding)<br>- Gemini report P1-1 (Blind Agent) |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee), Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Add grounding enforcement to system prompt: "ALWAYS call get_deal before answering questions about a specific deal"<br>2. Consider adding validation in graph.py to enforce tool calls before deal responses<br>3. Implement DealContext injection (Gemini recommendation) |
| **Verification Proof** | Golden trace test: User asks "What stage is deal DL-0048 in?" → Agent must call get_deal before responding |
| **Verification Status** | PROVEN — Prompt inspection confirms no grounding rule |

---

#### ZK-BRAIN-ISSUE-0003: Langfuse tracing not configured in production

| Field | Value |
|-------|-------|
| **Title** | Langfuse tracing not configured in production |
| **Description** | The Langfuse tracing integration code exists in `app/core/tracing.py`, but the required API keys (`LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`) are empty in production. The code fails silently (no-op) when keys are missing, resulting in no LLM traces being collected. |
| **Category** | Observability |
| **Severity** | P0 |
| **Evidence References** | - `.env` (keys empty)<br>- `app/core/tracing.py` (graceful no-op)<br>- Claude-Opus report G-003 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01) |
| **Recommended Remediation** | 1. Configure Langfuse API keys in production `.env`<br>2. Add startup health check that warns if keys missing<br>3. Verify traces appear in Langfuse dashboard |
| **Verification Proof** | ```bash\ngrep LANGFUSE /home/zaks/zakops-agent-api/.env\n# Expected: Both keys set\n``` |
| **Verification Status** | PROVEN — Config inspection confirms empty keys |

---

#### ZK-BRAIN-ISSUE-0004: Actor identity unverified for service-token requests (impersonation risk)

| Field | Value |
|-------|-------|
| **Title** | Actor identity unverified for service-token requests (impersonation risk) |
| **Description** | The `/agent/*` endpoints accept `actor_id` from the request body when using service token authentication. This value is trusted without verification against actual auth claims. An attacker could impersonate any user by passing their `actor_id`, compromising audit trails and authorization. |
| **Category** | Auth/Security |
| **Severity** | P0 |
| **Evidence References** | - `api/v1/agent.py` (trusts actor_id from body)<br>- Codex report P0-2 |
| **Source Attribution** | Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Validate `actor_id` against authenticated service token claims<br>2. Reject requests where actor_id doesn't match auth claims<br>3. Add tenant scoping validation |
| **Verification Proof** | Adversarial test: Call /agent/invoke with service-token but fake actor_id → should return 403 |
| **Verification Status** | PROVEN — Code inspection confirms trusted actor_id |

---

### P1 — MAJOR RISK

---

#### ZK-BRAIN-ISSUE-0005: Long-term memory disabled by default

| Field | Value |
|-------|-------|
| **Title** | Long-term memory disabled by default |
| **Description** | The agent's long-term memory (mem0 with pgvector) is disabled by default via `DISABLE_LONG_TERM_MEMORY=true`. The agent is "amnesic" — it cannot remember user preferences or past deal conversations between sessions. |
| **Category** | Memory/RAG |
| **Severity** | P1 |
| **Evidence References** | - `graph.py:75-77` (env var check)<br>- `config.py:DISABLE_LONG_TERM_MEMORY=true`<br>- Claude-Opus G-009<br>- Codex P2-6<br>- Gemini P1-2 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee), Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Verify mem0/pgvector configuration is correct<br>2. Set `DISABLE_LONG_TERM_MEMORY=false` in production<br>3. Add "Forget" tool for privacy compliance (Gemini suggestion) |
| **Verification Proof** | Check env: `printenv DISABLE_LONG_TERM_MEMORY` → should be `false` when enabled |
| **Verification Status** | PROVEN — Config confirms default true |

---

#### ZK-BRAIN-ISSUE-0006: No deal-scoped memory

| Field | Value |
|-------|-------|
| **Title** | No deal-scoped memory |
| **Description** | Even when long-term memory is enabled, there is no mechanism to recall prior conversations about a specific deal. Memory is scoped only by `user_id` via mem0, not by `deal_id`. The agent cannot remember "what did we discuss about this deal last week?" |
| **Category** | Memory/RAG |
| **Severity** | P1 |
| **Evidence References** | - `graph.py:103-126` (_long_term_memory implementation)<br>- Claude-Opus G-010<br>- Codex P2-6 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Design deal-scoped memory architecture<br>2. Implement DealContext loader that fetches deal history<br>3. Add deal_id to memory retrieval queries |
| **Verification Proof** | Feature not implemented — requires design + implementation |
| **Verification Status** | PROVEN — Feature does not exist |

---

#### ZK-BRAIN-ISSUE-0007: System prompt lacks M&A domain intelligence

| Field | Value |
|-------|-------|
| **Title** | System prompt lacks M&A domain intelligence |
| **Description** | The system prompt is generic with minimal M&A domain context. It lists stage names but provides no explanation of what each stage means, allowed transitions, M&A terminology (LOI, due diligence, earnouts), or deal-specific reasoning guidance. |
| **Category** | Prompt/Versioning |
| **Severity** | P1 |
| **Evidence References** | - `core/prompts/system.md`<br>- Claude-Opus G-004<br>- Codex P3-11<br>- Gemini implicit (static prompt) |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee), Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Rewrite system prompt with M&A domain context<br>2. Add stage transition rules matrix<br>3. Add deal-centric reasoning instructions<br>4. Explain M&A terminology (LOI, CIM, diligence, etc.) |
| **Verification Proof** | Scenario test: Agent should refuse invalid stage transitions and explain why |
| **Verification Status** | PROVEN — Prompt inspection confirms minimal domain content |

---

#### ZK-BRAIN-ISSUE-0008: No tool call budget enforcement (infinite loop risk)

| Field | Value |
|-------|-------|
| **Title** | No tool call budget enforcement (infinite loop risk) |
| **Description** | There is no limit on how many tool calls the agent can make in a single turn. If the LLM gets stuck in a tool-calling loop, it will continue indefinitely, consuming resources and potentially causing timeouts or crashes. |
| **Category** | Tool Reliability |
| **Severity** | P1 |
| **Evidence References** | - `graph.py` (no max tool calls)<br>- Claude-Opus G-005 and FM-004<br>- Codex FM-13<br>- Gemini FM-4 (Tool Loop) |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee), Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Add `tool_call_count` to GraphState<br>2. Increment on each tool call<br>3. Hard limit at 10 calls per turn<br>4. Return error message when limit reached |
| **Verification Proof** | Unit test: Force agent into loop scenario → should stop at 10 calls |
| **Verification Status** | PROVEN — No budget counter in GraphState |

---

#### ZK-BRAIN-ISSUE-0009: No prompt versioning

| Field | Value |
|-------|-------|
| **Title** | No prompt versioning |
| **Description** | The system prompt has no version tracking mechanism. Cannot trace which prompt version was used for a given agent run. Changes to the prompt cannot be audited or rolled back, and regressions are undetectable. |
| **Category** | Prompt/Versioning |
| **Severity** | P1 |
| **Evidence References** | - `prompts/__init__.py` (simple .format, no version)<br>- Claude-Opus G-006<br>- Codex P3-11 (partial) |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Add version field to prompt file (e.g., `# version: 1.0.0`)<br>2. Log prompt version with each request<br>3. Hash prompt content for drift detection |
| **Verification Proof** | Check traces: prompt_version field should be logged |
| **Verification Status** | PROVEN — No version mechanism exists |

---

#### ZK-BRAIN-ISSUE-0010: Evals have no CI gate (only 10 golden traces)

| Field | Value |
|-------|-------|
| **Title** | Evals have no CI gate (only 10 golden traces) |
| **Description** | The golden trace eval system exists but has only 10 traces and no CI integration. Deployments are not blocked on eval failure. This creates high risk that prompt changes or code changes cause regressions that go undetected. |
| **Category** | Evals |
| **Severity** | P1 |
| **Evidence References** | - `evals/golden_traces/` (only 10 traces)<br>- `evals/golden_trace_runner.py`<br>- Claude-Opus G-007<br>- Gemini P3-6 (Evaluations Unverified) |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Add CI gate: `CI=true python3 evals/golden_trace_runner.py`<br>2. Block deployment on eval failure<br>3. Expand to 30+ golden traces |
| **Verification Proof** | CI pipeline should fail if any eval fails |
| **Verification Status** | PROVEN — No CI gate configured |

---

#### ZK-BRAIN-ISSUE-0011: No correlation_id propagation across systems

| Field | Value |
|-------|-------|
| **Title** | No correlation_id propagation across systems |
| **Description** | There is no end-to-end correlation ID propagation from UI → agent → backend. LoggingContextMiddleware only binds `session_id` from JWT, not `X-Correlation-ID`. Cannot trace a user action through all system layers during incident investigation. |
| **Category** | Observability |
| **Severity** | P1 |
| **Evidence References** | - `core/middleware.py` (no X-Correlation-ID)<br>- Claude-Opus G-008<br>- Codex P1-5 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Add correlation_id middleware<br>2. Extract from X-Correlation-ID header or generate UUID<br>3. Forward to backend in tool calls<br>4. Include in all log events |
| **Verification Proof** | Trace test: Single request should show same correlation_id in agent logs, backend logs, and deal_events |
| **Verification Status** | PROVEN — Middleware inspection confirms missing |

---

#### ZK-BRAIN-ISSUE-0012: Non-idempotent write tools (create_deal, add_note)

| Field | Value |
|-------|-------|
| **Title** | Non-idempotent write tools (create_deal, add_note) |
| **Description** | The `create_deal` and `add_note` tools do not pass idempotency keys. If the LLM retries these tools or the request is replayed, duplicate deals or notes will be created. Only `transition_deal` has proper idempotency via SHA-256 key. |
| **Category** | Tool Reliability |
| **Severity** | P1 |
| **Evidence References** | - `deal_tools.py:487-589` (no idempotency key)<br>- Codex P1-3 |
| **Source Attribution** | Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Add idempotency_key parameter to create_deal payload<br>2. Add idempotency_key parameter to add_note payload<br>3. Backend should dedupe on key<br>4. Use deterministic key (SHA-256 of args) |
| **Verification Proof** | Unit test: Call create_deal twice with same args → should not create duplicate |
| **Verification Status** | PROVEN — Code inspection confirms no idempotency key |

---

#### ZK-BRAIN-ISSUE-0013: Tool output schemas inconsistent

| Field | Value |
|-------|-------|
| **Title** | Tool output schemas inconsistent |
| **Description** | Tools return inconsistent output formats. `transition_deal` and `create_deal` return structured JSON with `{ok, error}`, but `get_deal` and `search_deals` return plain error strings on failure. This inconsistency can confuse the LLM and lead to misinterpretation of errors. |
| **Category** | Schema |
| **Severity** | P1 |
| **Evidence References** | - `deal_tools.py:325-330` (get_deal plain string)<br>- Codex P1-4 |
| **Source Attribution** | Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Define ToolResult schema: `{success: bool, data?: any, error?: string}`<br>2. Wrap all tool outputs in ToolResult<br>3. Consistent error handling across all tools |
| **Verification Proof** | All tools should return JSON with consistent schema |
| **Verification Status** | PROVEN — Code shows mixed return formats |

---

### P2 — QUALITY GAP

---

#### ZK-BRAIN-ISSUE-0014: mem0 uses OpenAI provider even in local-vLLM deployments

| Field | Value |
|-------|-------|
| **Title** | mem0 uses OpenAI provider even in local-vLLM deployments |
| **Description** | The mem0 memory system is hardcoded to use OpenAI provider for embeddings (`text-embedding-3-small`). Even when the primary LLM is local vLLM (Qwen), memory operations still call OpenAI, creating a hidden cloud dependency and potential data leak. |
| **Category** | Provider Config |
| **Severity** | P2 |
| **Evidence References** | - `graph.py:119-123` (mem0 config uses provider "openai")<br>- Codex P2-7 |
| **Source Attribution** | Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Make mem0 provider configurable via env<br>2. Support local embeddings (e.g., sentence-transformers)<br>3. Or: Make OpenAI optional/fallback only |
| **Verification Proof** | Run with no OPENAI_API_KEY → memory should still work (if local provider configured) |
| **Verification Status** | PROVEN — Code shows hardcoded openai provider |

---

#### ZK-BRAIN-ISSUE-0015: Tool error handling inconsistent; _tool_call lacks try/except

| Field | Value |
|-------|-------|
| **Title** | Tool error handling inconsistent; _tool_call lacks try/except |
| **Description** | The `_tool_call` function in graph.py directly invokes tools without try/except wrapping. If a tool raises an unexpected exception, it bubbles up and can crash the entire agent invocation instead of returning an error response. |
| **Category** | Tool Reliability |
| **Severity** | P2 |
| **Evidence References** | - `graph.py:144-165` (_tool_call implementation)<br>- Codex P2-8 |
| **Source Attribution** | Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Add try/except wrapper in _tool_call<br>2. Return error response on exception<br>3. Log exception with correlation_id |
| **Verification Proof** | Adversarial test: Force tool exception → should return error response, not crash |
| **Verification Status** | PROVEN — Code shows no try/except |

---

#### ZK-BRAIN-ISSUE-0016: RAG retrieval lacks provenance and freshness

| Field | Value |
|-------|-------|
| **Title** | RAG retrieval lacks provenance and freshness |
| **Description** | The `search_deals` tool returns raw RAG results without source citations or freshness timestamps. Agent cannot verify when documents were last indexed or provide proper attribution. If RAG index is stale, agent may use outdated information. Additionally, there is no SQL fallback if RAG service is down. |
| **Category** | Memory/RAG |
| **Severity** | P2 |
| **Evidence References** | - `deal_tools.py:355-399` (search_deals)<br>- Claude-Opus G-014<br>- Codex P2-9<br>- Gemini P2-3 (RAG Fragility) |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Codex (20260204-1903-1b4aee), Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Add `last_indexed_at` to RAG results<br>2. Add citation formatting to agent responses<br>3. Implement RAG circuit breaker with SQL fallback (Gemini suggestion) |
| **Verification Proof** | RAG results should include timestamps and source URLs |
| **Verification Status** | PROVEN — RAG returns raw results only |

---

#### ZK-BRAIN-ISSUE-0017: No decision ledger for non-HITL tool decisions

| Field | Value |
|-------|-------|
| **Title** | No decision ledger for non-HITL tool decisions |
| **Description** | The audit_log table captures HITL approval events, but non-HITL tool executions (get_deal, search_deals) are not recorded. Cannot reconstruct "why did the agent choose to call search_deals instead of get_deal?" or audit non-HITL actions. |
| **Category** | Observability |
| **Severity** | P2 |
| **Evidence References** | - `models/approval.py` (only HITL events)<br>- Gemini P2-5 (No Decision Ledger)<br>- Codex FM-15 |
| **Source Attribution** | Gemini-CLI (20260204-1050-gemini), Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Create `decisions` table with reasoning capture<br>2. Log all tool decisions (not just HITL)<br>3. Include LLM reasoning if available |
| **Verification Proof** | Every tool call should have a decision_ledger row |
| **Verification Status** | PROVEN — Only HITL events logged |

---

#### ZK-BRAIN-ISSUE-0018: Prompt drift (tool list hardcoded, not dynamic)

| Field | Value |
|-------|-------|
| **Title** | Prompt drift (tool list hardcoded, not dynamic) |
| **Description** | The system prompt hardcodes the tool list. If a tool is added or removed in `deal_tools.py`, the prompt becomes stale and misleads the LLM about available capabilities. This is a source of hallucination risk. |
| **Category** | Prompt/Versioning |
| **Severity** | P2 |
| **Evidence References** | - `core/prompts/system.md` (hardcoded tool list)<br>- Gemini P2-4 |
| **Source Attribution** | Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Auto-generate tool section from tool registry<br>2. Or: Build prompt dynamically from registered tools<br>3. Add CI check that prompt matches registry |
| **Verification Proof** | Add a tool → prompt should automatically include it |
| **Verification Status** | PROVEN — Prompt has static tool list |

---

#### ZK-BRAIN-ISSUE-0019: No response logging

| Field | Value |
|-------|-------|
| **Title** | No response logging |
| **Description** | Agent responses are not persisted or logged. Cannot reconstruct what the agent said in a specific conversation. This is a gap for debugging, compliance, and incident investigation. |
| **Category** | Observability |
| **Severity** | P2 |
| **Evidence References** | - `agent.py` (no response logging)<br>- Claude-Opus G-012 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01) |
| **Recommended Remediation** | 1. Log sanitized response to audit trail<br>2. Include response_preview (first 200 chars)<br>3. Full response should be retrievable |
| **Verification Proof** | Check audit_log after conversation → should have response entries |
| **Verification Status** | PROVEN — Responses not logged |

---

#### ZK-BRAIN-ISSUE-0020: Only 10 golden traces (insufficient eval coverage)

| Field | Value |
|-------|-------|
| **Title** | Only 10 golden traces (insufficient eval coverage) |
| **Description** | The eval suite has only 10 golden traces. This is insufficient coverage for a production agent. Key scenarios like HITL approval, rejection, error handling, and adversarial inputs are likely not covered. |
| **Category** | Evals |
| **Severity** | P2 |
| **Evidence References** | - `evals/golden_traces/` directory<br>- Claude-Opus G-011 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01) |
| **Recommended Remediation** | 1. Add 20+ more golden traces<br>2. Cover: all deal stages, HITL approve/reject, error cases, prompt injection attempts<br>3. Target: 30+ traces minimum |
| **Verification Proof** | `ls evals/golden_traces/*.json | wc -l` → should be >= 30 |
| **Verification Status** | PROVEN — Only 10 traces exist |

---

#### ZK-BRAIN-ISSUE-0021: No stage transition rules in prompt

| Field | Value |
|-------|-------|
| **Title** | No stage transition rules in prompt |
| **Description** | The system prompt lists valid stage names but does not explain which transitions are allowed. The agent may suggest invalid transitions (e.g., inbound → closing). The transition rules exist in `workflow.py` but are not communicated to the LLM. |
| **Category** | Prompt/Versioning |
| **Severity** | P2 |
| **Evidence References** | - `core/prompts/system.md`<br>- `workflow.py:STAGE_TRANSITIONS`<br>- Claude-Opus G-013 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01) |
| **Recommended Remediation** | 1. Add transition matrix to system prompt<br>2. Or: Inject allowed transitions dynamically based on current deal stage<br>3. Explain stage meanings |
| **Verification Proof** | Agent should refuse invalid transition and explain why |
| **Verification Status** | PROVEN — Prompt lacks transition rules |

---

### P3 — IMPROVEMENT

---

#### ZK-BRAIN-ISSUE-0022: Dev mock uses invalid stage name

| Field | Value |
|-------|-------|
| **Title** | Dev mock uses invalid stage name |
| **Description** | The `get_deal` dev mock returns stage "qualification" which is not in the valid stage list. This causes dev/test behavior to diverge from production and can mask real issues. |
| **Category** | Evals |
| **Severity** | P3 |
| **Evidence References** | - `deal_tools.py:335-339`<br>- Codex P3-10 |
| **Source Attribution** | Codex (20260204-1903-1b4aee) |
| **Recommended Remediation** | 1. Fix mock to use valid stage (e.g., "screening")<br>2. Validate mock data against schema |
| **Verification Proof** | Mock should return valid stage from VALID_STAGES |
| **Verification Status** | PROVEN — Code shows "qualification" |

---

#### ZK-BRAIN-ISSUE-0023: No deal health scoring

| Field | Value |
|-------|-------|
| **Title** | No deal health scoring |
| **Description** | The agent has no mechanism to assess deal health or readiness. Cannot answer "Is this deal ready to close?" or "What's blocking this deal?" without explicit tool calls and manual reasoning. |
| **Category** | Evals |
| **Severity** | P3 |
| **Evidence References** | - Feature not implemented<br>- Claude-Opus G-015<br>- Gemini FM-6 (Intelligence Gaps) |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01), Gemini-CLI (20260204-1050-gemini) |
| **Recommended Remediation** | 1. Implement deal health scoring system<br>2. Check for missing documents, stale stages<br>3. Expose via tool or automatic context |
| **Verification Proof** | Feature not implemented — requires design |
| **Verification Status** | NEEDS IMPLEMENTATION |

---

#### ZK-BRAIN-ISSUE-0024: No next-step recommendations

| Field | Value |
|-------|-------|
| **Title** | No next-step recommendations |
| **Description** | The agent cannot provide stage-aware next-step suggestions. If a deal is in "loi" stage, it should suggest diligence activities, but there is no such guidance built in. |
| **Category** | Evals |
| **Severity** | P3 |
| **Evidence References** | - Feature not implemented<br>- Claude-Opus G-016 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01) |
| **Recommended Remediation** | 1. Add stage-aware action templates to prompt<br>2. Or: Implement next-step tool<br>3. Leverage DealContext if implemented |
| **Verification Proof** | Feature not implemented — requires design |
| **Verification Status** | NEEDS IMPLEMENTATION |

---

#### ZK-BRAIN-ISSUE-0025: No LLM reasoning capture

| Field | Value |
|-------|-------|
| **Title** | No LLM reasoning capture |
| **Description** | The agent does not log or store the LLM's reasoning chain. Only final tool calls are captured. Cannot reconstruct "why did the agent choose action A over B?" for debugging or compliance. |
| **Category** | Observability |
| **Severity** | P3 |
| **Evidence References** | - Not logged<br>- Claude-Opus G-017 |
| **Source Attribution** | Claude-Opus (20260204-1300-r3f01) |
| **Recommended Remediation** | 1. Enable chain-of-thought logging<br>2. Store reasoning in decision_ledger<br>3. Consider optional verbose mode |
| **Verification Proof** | Check logs: should include LLM reasoning text |
| **Verification Status** | NEEDS IMPLEMENTATION |

---

## B) COVERAGE MATRIX (Issue → Remediation)

| Issue ID | Claude-Opus | Codex | Gemini | Recommended Fix | Where | How to Verify |
|----------|-------------|-------|--------|-----------------|-------|---------------|
| ZK-BRAIN-ISSUE-0001 | G-001 | P0-1 | — | Add create_deal to HITL_TOOLS | `schemas/agent.py` | create_deal returns pending_approval |
| ZK-BRAIN-ISSUE-0002 | G-002 | P1-3 | P1-1 | Add grounding rule to prompt | `system.md` | Golden trace requires get_deal |
| ZK-BRAIN-ISSUE-0003 | G-003 | — | — | Configure Langfuse keys | `.env` | Traces appear in dashboard |
| ZK-BRAIN-ISSUE-0004 | — | P0-2 | — | Validate actor_id | `agent.py` | Impersonation returns 403 |
| ZK-BRAIN-ISSUE-0005 | G-009 | P2-6 | P1-2 | Enable long-term memory | `.env` | Memory persists across sessions |
| ZK-BRAIN-ISSUE-0006 | G-010 | P2-6 | — | Build deal-scoped memory | `graph.py` | Agent recalls deal history |
| ZK-BRAIN-ISSUE-0007 | G-004 | P3-11 | implicit | Rewrite prompt with M&A context | `system.md` | Scenario tests pass |
| ZK-BRAIN-ISSUE-0008 | G-005 | FM-13 | FM-4 | Add tool call budget | `graph.py` | Loop stops at 10 calls |
| ZK-BRAIN-ISSUE-0009 | G-006 | P3-11 | — | Add prompt versioning | `prompts/__init__.py` | Version logged |
| ZK-BRAIN-ISSUE-0010 | G-007 | — | P3-6 | Add CI gate | CI pipeline | Deployment blocks on failure |
| ZK-BRAIN-ISSUE-0011 | G-008 | P1-5 | — | Add correlation_id middleware | `middleware.py` | ID in all logs |
| ZK-BRAIN-ISSUE-0012 | — | P1-3 | — | Add idempotency keys | `deal_tools.py` | No duplicates on retry |
| ZK-BRAIN-ISSUE-0013 | — | P1-4 | — | Implement ToolResult schema | `deal_tools.py` | Consistent JSON returns |
| ZK-BRAIN-ISSUE-0014 | — | P2-7 | — | Configurable mem0 provider | `graph.py` | Works without OpenAI key |
| ZK-BRAIN-ISSUE-0015 | — | P2-8 | — | Add try/except to _tool_call | `graph.py` | Error response on exception |
| ZK-BRAIN-ISSUE-0016 | G-014 | P2-9 | P2-3 | Add provenance + SQL fallback | `deal_tools.py` | Citations + circuit breaker |
| ZK-BRAIN-ISSUE-0017 | — | FM-15 | P2-5 | Create decisions table | new table | All tool calls logged |
| ZK-BRAIN-ISSUE-0018 | G-006 | — | P2-4 | Auto-generate tool list | `system.md` | Prompt matches registry |
| ZK-BRAIN-ISSUE-0019 | G-012 | — | — | Log sanitized responses | `agent.py` | Responses in audit |
| ZK-BRAIN-ISSUE-0020 | G-011 | — | — | Add 20+ golden traces | `evals/` | 30+ traces exist |
| ZK-BRAIN-ISSUE-0021 | G-013 | — | — | Add transition matrix | `system.md` | Agent refuses invalid transitions |
| ZK-BRAIN-ISSUE-0022 | — | P3-10 | — | Fix mock stage value | `deal_tools.py` | Mock uses valid stage |
| ZK-BRAIN-ISSUE-0023 | G-015 | — | FM-6 | Implement health scoring | new feature | Agent assesses deal readiness |
| ZK-BRAIN-ISSUE-0024 | G-016 | — | — | Add next-step suggestions | new feature | Stage-aware recommendations |
| ZK-BRAIN-ISSUE-0025 | G-017 | — | — | Log LLM reasoning | `graph.py` | Reasoning in decision_ledger |

---

## C) CONFLICTS & DIVERGENCES

### Conflict 1: HITL Coverage Scope

| Agent | Position |
|-------|----------|
| **Claude-Opus** | create_deal should be added to HITL_TOOLS |
| **Codex** | create_deal AND add_note should be HITL (both are destructive writes) |
| **Gemini** | HITL architecture is "robust" (did not flag create_deal gap) |

**Resolution Required:** Decide which tools require HITL:
- Minimum: create_deal
- Conservative: create_deal, add_note
- Evidence needed: Risk assessment of add_note without approval

---

### Conflict 2: Long-term Memory Approach

| Agent | Position |
|-------|----------|
| **Claude-Opus** | Enable mem0 with deal-scoped retrieval (XL effort) |
| **Codex** | Remove OpenAI dependency in mem0; use routing policy |
| **Gemini** | Enable pgvector + add "Forget" tool for privacy |

**Resolution Required:** Decide memory architecture:
- Option A: mem0 with OpenAI (current, simpler)
- Option B: mem0 with local embeddings (no cloud)
- Option C: Custom deal-scoped memory (most control)
- Evidence needed: Privacy requirements, local-only constraints

---

### Conflict 3: RAG Failure Handling

| Agent | Position |
|-------|----------|
| **Gemini** | Implement RAG Circuit Breaker with SQL fallback |
| **Codex** | RAG ConnectError raises in prod (fail-closed is correct) |

**Resolution Required:** Graceful degradation vs fail-closed:
- Option A: SQL fallback (Gemini) — better UX
- Option B: Fail-closed (Codex) — safer, explicit failure
- Evidence needed: Business impact of RAG downtime

---

### Conflict 4: Tool Reliability Scoring

| Agent | Score |
|-------|-------|
| **Claude-Opus** | 7/10 (idempotency + validation exists) |
| **Codex** | 5/10 (inconsistent schemas, no try/except) |
| **Gemini** | 9/10 (HITL + idempotency rock solid) |

**Resolution Required:** Reconcile divergent assessments:
- Gemini focused on transition_deal (which is solid)
- Codex focused on create_deal/add_note (which lack idempotency)
- Claude-Opus in middle
- Evidence needed: Test all tools systematically

---

## D) WHAT'S STILL NOT PROVEN

| Item | Claimed By | Assertion | Verification Method |
|------|------------|-----------|---------------------|
| 1 | All | RAG service is running | `curl http://localhost:8052/health` |
| 2 | Gemini | Idempotency is "cryptographic and restart-safe" | Test: Kill agent mid-execution, resume, verify no duplicates |
| 3 | Claude-Opus | Stale approvals accumulate | Query: `SELECT COUNT(*) FROM approvals WHERE expires_at < NOW()` |
| 4 | Codex | Actor impersonation is exploitable | Adversarial test: Call with fake actor_id |
| 5 | All | Dashboard actually fails on Zod mismatch | Test: Add field to backend response, verify dashboard behavior |
| 6 | Codex | mem0 calls OpenAI in local-only mode | Test: Set no OPENAI_API_KEY, enable memory, verify failure |
| 7 | Gemini | Atomic claim prevents race conditions | Concurrent approval test |
| 8 | All | 10 golden traces pass currently | Run: `CI=true python3 evals/golden_trace_runner.py` |

---

## E) SOURCE REPORTS USED

| # | Agent | Run ID | Report Path |
|---|-------|--------|-------------|
| 1 | Claude-Opus-4.5 | 20260204-1300-r3f01 | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_FORENSIC.Claude-Opus.20260204-1300-r3f01.md` |
| 2 | Codex | 20260204-1903-1b4aee | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_FORENSIC.Codex.20260204-1903-1b4aee.md` |
| 3 | Gemini-CLI | 20260204-1050-gemini | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_FORENSIC.Gemini.20260204-1050-gemini.md` |

---

## F) SUMMARY STATISTICS

| Metric | Value |
|--------|-------|
| Total Findings Extracted | 52 (across all reports) |
| Deduplicated Issues | 25 |
| P0 Issues | 4 |
| P1 Issues | 9 |
| P2 Issues | 8 |
| P3 Issues | 4 |
| Conflicts Identified | 4 |
| Unproven Items | 8 |

---

*Report Generated: 2026-02-04T20:45:00Z*
*Operator: Claude-Opus (PASS 1 Round-3 Eval)*
