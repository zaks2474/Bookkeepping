# AGENT_BRAIN_ROUND3_FORENSIC.Gemini.20260204-1050-gemini.md

## 1) AGENT IDENTITY
- **agent_name**: Gemini-CLI
- **run_id**: 20260204-1050-gemini
- **date_time**: 2026-02-04T10:50:00Z
- **repo_revision**: unknown (git not active)

## 2) EXECUTIVE SUMMARY
**Verdict: PRODUCTION-READY CORE (Tier 2), BUT INTELLIGENCE-LIMITED (Tier 1)**

The ZakOps Agent "Body" (execution/safety) is surprisingly robust. It passes the "Tier 2" bar for forensic quality:
- **Safety**: `transition_deal` is HITL-gated, stage-validating, and verifies its own outcome ("No-Illusions Gate").
- **Idempotency**: Implements a restart-safe, SHA-256 deterministic key pattern.
- **Audit**: Every action is logged to `audit_log` and `tool_executions`.

However, the "Brain" (intelligence/reasoning) is currently at **Tier 1 (Minimum Viable)**:
- **Amnesic**: `DISABLE_LONG_TERM_MEMORY=true` is the default. The agent has NO memory of past deals unless it actively searches.
- **RAG-Dependent**: It relies entirely on `search_deals` (port 8052). If that service is down, the agent is blind.
- **Context-Poor**: The system prompt is generic. It doesn't load "Deal Context" automatically. The agent has to "ask" for everything.

**Single Biggest Risk:** **Blindness.** The agent operates without a "Deal Context Object." It doesn't know the current deal's state until it calls `get_deal`. This leads to chatty, inefficient, and error-prone interactions.

---

## 3) AGENT ARCHITECTURE INVENTORY

### 3.1) Graph Definition and Topology
- **File**: `app/core/langgraph/graph.py`
- **Topology**:
  - `START` -> `chat` (LLM Decision)
  - `chat` -> `tool_call` (Automatic execution for read-only tools)
  - `chat` -> `approval_gate` (Interrupt for HITL tools)
  - `chat` -> `END` (Response generation)
  - `approval_gate` -> `execute_approved_tools` (Resume after approval) -> `chat`
  - `approval_gate` -> `END` (Resume after rejection)
- **Checkpointing**: Uses `AsyncPostgresSaver` with `psycopg_pool`. State is durable in Postgres.

### 3.2) Tool Registry and Contracts
- **Registry**: `app/core/langgraph/tools/deal_tools.py`
- **Tools**:
  1.  `transition_deal`: **CRITICAL**. HITL. Validates `to_stage` enum. Fetches actual `from_stage`. Verifies DB update.
  2.  `create_deal`: HITL. Validates `stage` enum.
  3.  `add_note`: Read-write.
  4.  `get_deal`: Read-only.
  5.  `search_deals`: Read-only. Calls RAG service (port 8052).
  6.  `duckduckgo_search`: External search.
- **Schemas**: All tools use Pydantic models with `extra="forbid"`. Strong typing.

### 3.3) System Prompt
- **File**: `app/core/prompts/system.md`
- **Content**: Generic Qwen 2.5 identity. Hardcoded tool list (risk of drift). Explicit stage name rules (GOOD).
- **Missing**: No dynamic deal context injection. No "current user" context beyond simple string.

### 3.4) Memory Architecture
- **Short-term**: LangGraph state (`messages` list).
- **Long-term**: `mem0` + pgvector is implemented but **DISABLED BY DEFAULT** (`DISABLE_LONG_TERM_MEMORY=true`).
- **Isolation**: Minimal. `user_id` is passed to memory methods, but RAG search scope needs verification.

### 3.5) RAG and Retrieval
- **Pipeline**: REST call to `http://host.docker.internal:8052/rag/query`.
- **Fragility**: No fallback. If the RAG service is down (common in dev), the agent cannot find deals.

### 3.6) HITL Wiring
- **Mechanism**: `interrupt({"type": "approval_required", ...})`.
- **Storage**: `approvals` table in Postgres.
- **State Machine**: `pending` -> `claimed` -> `approved`/`rejected`/`expired`.
- **Safety**: Atomic claims (`UPDATE ... WHERE status='pending'`). Stale claim reclamation (5 min timeout).

### 3.7) Model Config
- **Provider**: `llm_service` supports OpenAI format.
- **Default**: `Qwen/Qwen2.5-32B-Instruct-AWQ` via vLLM (local) or `gpt-4o-mini` (cloud).
- **Auth**: `OPENAI_API_KEY` env var.

### 3.8) Telemetry
- **Tracing**: `Langfuse` integration (conditional).
- **Logs**: Structured JSON logging via `structlog`.
- **Metrics**: Prometheus metrics for LLM duration.

---

## 4) END-TO-END AGENT RUNTIME FLOW

1.  **Request**: `POST /agent/invoke` with `message` and `thread_id`.
2.  **Auth**: `require_service_token` validates Dashboard-to-Agent trust.
3.  **Graph Start**: `LangGraphAgent.invoke_with_hitl` initializes graph with Postgres checkpointer.
4.  **Chat Node**: Loads `system.md`. Calls LLM.
5.  **Decision**:
    *   *Case A (Read Tool)*: LLM chooses `get_deal`. `tool_call` node executes it. Result feeds back to `chat`.
    *   *Case B (HITL Tool)*: LLM chooses `transition_deal`.
        1.  Graph detects `requires_approval`.
        2.  Creates `Approval` record in DB.
        3.  Returns `pending_approval` JSON to API.
        4.  Graph suspends at `approval_gate`.
6.  **Approval**: User clicks "Approve". Dashboard calls `POST /agent/approvals/{id}:approve`.
7.  **Resume**:
    1.  API updates `Approval` status.
    2.  Calls `agent.resume_after_approval`.
    3.  Graph resumes at `execute_approved_tools`.
    4.  Tool executes (with idempotency check).
    5.  Result feeds back to `chat`.
8.  **Response**: Agent generates final text response.

---

## 5) GAP LIST (BROKEN, MISALIGNED, OR FRAGILE)

| Severity | Issue | Evidence | Impact |
|:---:|---|---|---|
| **P1** | **Blind Agent (No Deal Context)** | `system.md` lacks dynamic context. Agent doesn't know active deal. | User must explicitly state deal ID/Context every turn. High friction. |
| **P1** | **Long-Term Memory Disabled** | `config.py:DISABLE_LONG_TERM_MEMORY=true`. | Agent forgets user preferences and past deal details instantly. |
| **P2** | **RAG Fragility** | `search_deals` calls port 8052 without fallback. | If RAG container dies, agent cannot find deals. System looks broken. |
| **P2** | **Prompt Drift** | `system.md` hardcodes tool list. `deal_tools.py` defines them. | If a tool is added/removed, prompt lies to the LLM. Hallucination risk. |
| **P2** | **No Decision Ledger** | `audit_log` is a flat event stream. No "Reasoning" captured. | Cannot debug *why* agent chose a specific action. |
| **P3** | **Evaluations Unverified** | `evals/` folder exists but usage is undocumented/unverified. | Unknown quality baseline. Regression risk on prompt changes. |

---

## 6) CONTRARIAN VIEW — FAILURE SCENARIOS

### 3.1) Environment Drift
*   **Scenario**: `VLLM_BASE_URL` is set in Dev but missing in Prod.
    *   *Result*: Agent defaults to `gpt-4o-mini` (cloud) silently, leaking data if not expected.
*   **Scenario**: `DEAL_API_URL` points to `localhost` instead of `host.docker.internal` in container.
    *   *Result*: Connection refused. Tools fail.

### 3.3) Tool Misuse
*   **Scenario**: LLM calls `transition_deal` with `to_stage="negotiation"`.
    *   *Mitigation*: **CAUGHT**. `deal_tools.py` validates against enum. Returns structured error.
*   **Scenario**: LLM calls `create_deal` twice.
    *   *Mitigation*: **CAUGHT**. `tool_idempotency_key` ensures second call returns cached result (if approved).

### 3.4) HITL Bypass
*   **Scenario**: User tries to `POST /approvals/{id}:approve` for a rejected approval.
    *   *Mitigation*: **CAUGHT**. Atomic SQL update `WHERE status='pending'` prevents zombie resurrection.

### 3.6) Intelligence Gaps
*   **Scenario**: User asks "Is this deal ready to close?"
    *   *Result*: **FAILURE**. Agent has no "readiness checklist" or context. It will likely hallucinate or say "I don't know."
*   **Scenario**: User asks "What happened with this deal last week?"
    *   *Result*: **FAILURE**. Agent has no access to event history unless it calls `get_deal` (which returns current state, not history).

---

## 7) WORLD-CLASS AGENT ARCHITECTURE PLAN

### 4.1) The "Deal Context Object" (The Brain Upgrade)
**Current**: System Prompt is static.
**Proposed**: Inject a `DealContext` block into the system prompt when a deal is active.
```python
# In graph.py _chat node:
if state.active_deal_id:
    context = await get_deal_context(state.active_deal_id)
    system_prompt += f"
# Active Deal Context
{context.to_markdown()}"
```
**Impact**: Agent immediately knows stage, missing docs, and next steps without tool calls.

### 4.2) Decision Ledger Implementation
**Current**: `audit_log` (actor, event, payload).
**Proposed**: `decisions` table.
```sql
CREATE TABLE decisions (
    id UUID PRIMARY KEY,
    trace_id UUID,
    trigger TEXT,         -- "user_message"
    reasoning TEXT,       -- "User asked to close. Documents missing. Suggesting checklist."
    tools_selected JSONB, -- ["get_deal_checklist"]
    outcome TEXT          -- "success"
);
```
**Impact**: "Explainable AI" for M&A compliance.

### 4.3) RAG Circuit Breaker
**Current**: Hard failure on connection error.
**Proposed**:
```python
try:
    results = await rag_client.query(...)
except ConnectError:
    # Fallback: SQL LIKE search on canonical_name
    results = await db.search_deals_sql(query)
    logger.warn("rag_down_fallback_active")
```
**Impact**: Graceful degradation. The system remains usable even if the vector DB is flaky.

---

## 8) ROUND-3 IMPLEMENTATION PLAN

### Phase R3-1: Intelligence Injection (P1)
1.  Implement `DealContext` fetcher service.
2.  Update `LangGraphAgent` to detect `active_deal_id` from conversation state.
3.  Inject dynamic context into `system.md` at runtime.

### Phase R3-2: Memory Activation (P1)
1.  Verify `mem0` / pgvector configuration.
2.  Set `DISABLE_LONG_TERM_MEMORY=false`.
3.  Add "Forget" tool for privacy compliance.

### Phase R3-3: Robustness Hardening (P2)
1.  Implement RAG Circuit Breaker (fallback to SQL).
2.  Add `DecisionLedger` recording to `_chat` node.
3.  Automate `system.md` tool list generation from `tools` registry (fix drift).

---

## 9) SCORECARD

| Category | Score | Target | Proof Plan |
|---|:---:|:---:|---|
| **Tool Reliability** | **9/10** | 9 | HITL + Idempotency + Validation are rock solid. |
| **Safety / HITL** | **9/10** | 9 | Atomic locking, expiration, audit trails exist. |
| **Grounding** | **8/10** | 9 | Tools verify "No-Illusions". |
| **Intelligence** | **3/10** | 9 | **CRITICAL GAP**. No context injection. Amnesic. |
| **Observability** | **6/10** | 9 | Good logs, but no decision tracing or spans. |
| **Prompt Quality** | **4/10** | 9 | Static, generic, prone to drift. |

**Final Recommendation**: The "Body" is ready. Build the "Brain" (Context + Memory) immediately.
