# ZakOps System Capability Assessment
## Operator-Perspective End-to-End Evaluation
**Date:** 2026-02-19
**Classification:** Strategic Assessment — Source-of-Truth Grounded
**Methodology:** Every answer verified against live code, configs, and working flows

---

## Q1: Email Injection from ZakOps Chat

**Can a user trigger email injection/ingestion from the ZakOps chat interface?**

### Status: NOT SUPPORTED

The ZakOps chat agent has **8 tools** — none of them involve email:

| Tool | Purpose |
|------|---------|
| `duckduckgo_search_tool` | Web search |
| `transition_deal` | Move deal between stages |
| `get_deal` | Retrieve deal details |
| `list_deals` | List pipeline deals |
| `search_deals` | Search deals by name |
| `create_deal` | Create new deal |
| `add_note` | Add notes to deal |
| `get_deal_health` | Calculate deal health score |

**Source:** `apps/agent-api/app/core/langgraph/tools/__init__.py` (lines 25-34)

There is no tool for:
- Fetching emails from Gmail/IMAP
- Injecting emails into quarantine
- Triggering the email triage pipeline
- Sending emails
- Accessing any email-related backend endpoint

**What happens if a user says "check my account for new emails":**
The agent has no tool to do this. It would either respond with a text explanation that it can't do that, or attempt an irrelevant tool call (e.g., web search).

**Where email injection actually lives:**
- The LangSmith agent (external) calls `zakops_inject_quarantine` via MCP bridge (port 9100)
- Backend has `/api/integrations/email/` endpoints (OAuth-based, admin-only)
- Email triage is a separate pipeline — not chat-accessible

**Gap to close:** A `check_email` or `trigger_email_scan` tool would need to be added to the local agent's toolset, wired to either the Gmail integration or the LangSmith agent's email triage capability.

---

## Q2: Research Delegation from ZakOps Chat to LangSmith

**Can a user trigger a research request from ZakOps chat that is delegated to the LangSmith execution agent?**

### Status: NOT SUPPORTED

The architecture is **inverted from what you'd expect**:

```
WHAT EXISTS:
  LangSmith Agent → calls ZakOps tools via MCP bridge → reads/writes ZakOps data

WHAT DOES NOT EXIST:
  ZakOps Chat → delegates research to LangSmith Agent
```

**Evidence:**

1. **No delegation tool in the agent:** The 8 tools listed above have no "delegate to external agent" or "request research" capability.

2. **No outbound call to LangSmith:** The agent-api codebase contains zero HTTP calls to any LangSmith execution endpoint from within the chat flow.

3. **System prompt is silent:** `apps/agent-api/app/core/prompts/system.md` (146 lines) — no mention of delegating to external services or LangSmith.

4. **Chat route confirms it:** `apps/dashboard/src/app/api/chat/route.ts` line 104:
   ```typescript
   // TODO: Route to different providers based on selectedProvider when implemented
   ```

**What research the agent CAN do today:**
- `duckduckgo_search_tool` — basic web search via DuckDuckGo (local execution, no delegation)
- That's it. No Tavily, no Serper, no deep research, no company profile lookups.

**What the delegation system supports (but not from chat):**
The backend has a task delegation system with research task types:

| Task Type | Description |
|-----------|-------------|
| `RESEARCH.COMPANY_PROFILE` | Deep company research |
| `RESEARCH.BROKER_PROFILE` | Broker/advisory firm research |
| `RESEARCH.MARKET_SCAN` | Acquisition criteria matching |
| `RESEARCH.VENDOR_DUE_DILIGENCE` | Dataroom vendor evaluation |

**Source:** `apps/backend/src/api/orchestration/delegation_types.py`

These are **pull-based tasks** — external agents poll and claim them. There is no mechanism for a user chat message to create one of these tasks.

**Gap to close:** Two options:
1. **Push model:** Add a `delegate_research` tool to the local agent that creates a delegation task in the backend, which the LangSmith agent then claims and executes
2. **Direct model:** Add a tool that makes an HTTP call to the LangSmith agent's endpoint with a research prompt, waits for the result, and returns it to the user

Neither exists today.

---

## Q3: Acting on Quarantine Items from Chat

**Can a user approve, reject, escalate, or delegate quarantine items from the chat interface?**

### Status: PARTIALLY SUPPORTED — with critical caveats

**What the LOCAL agent (port 8095) can do: NO quarantine tools.**

The local LangGraph agent has 8 tools — none of them touch quarantine. A user cannot say "approve the TechCorp email" in ZakOps chat and have the local agent execute it.

**What the MCP bridge (port 9100) exposes to EXTERNAL agents:**

| Tool | Available |
|------|-----------|
| `list_quarantine` | Yes |
| `approve_quarantine` | Yes |
| `reject_quarantine` | Yes |
| `escalate_quarantine` | **No** (backend supports it, but no MCP tool defined) |
| `delegate_quarantine` | **No** |

**Source:** `apps/backend/mcp_server/tool_schemas.py`

**The disconnect:** MCP bridge tools are accessible to the LangSmith agent (external), NOT to the local chat agent. These are two separate tool registries:
- Local agent tools: `apps/agent-api/app/core/langgraph/tools/__init__.py` (8 tools)
- MCP bridge tools: `apps/backend/mcp_server/server.py` (12 tools)
- They do NOT share a tool registry

**Deal lifecycle transitions from chat: YES (partial).**

The local agent DOES have `transition_deal` — so a user can say "move DL-0133 to screening" and the agent can execute it (with HITL approval via the proposal system). But:
- The user cannot approve a quarantine item to CREATE a deal via chat
- Once a deal exists, the user CAN transition it via chat
- The "quarantine → approve → deal creation → stage transition" flow is broken at step 1

**Proposal system:**
The chat UI does have an approve/reject proposal mechanism (lines 650-760 of `chat/page.tsx`). When the agent proposes an action, the user sees approve/reject buttons. This works for the tools the agent HAS (create_deal, transition_deal, add_note). It would work for quarantine tools IF they were added to the local agent.

**Gap to close:** Add `list_quarantine`, `approve_quarantine`, `reject_quarantine`, and `escalate_quarantine` to the local agent's tool registry. The backend endpoints already exist (`POST /api/quarantine/{id}/process`). This is a wiring task, not a feature build.

---

## Q4: Multi-Model Continuity (LangCraft-Style Mid-Thread Switching)

**Can a user start a conversation with one model and switch providers mid-thread?**

### Status: NOT SUPPORTED

**What exists:**

1. **Provider Selector UI:** `apps/dashboard/src/components/chat/ProviderSelector.tsx` — displays a badge showing the active provider with a connection status indicator. Supports 4 providers:
   - `local` — Local vLLM (Qwen)
   - `openai` — OpenAI
   - `anthropic` — Anthropic Claude
   - `custom` — Custom endpoint

2. **Provider Settings:** `apps/dashboard/src/lib/settings/provider-settings.ts` — localStorage-based settings with fields for each provider (endpoint, apiKey, model, enabled). Default is `local`.

3. **Settings Page:** The provider selector links to `/settings` — but **this page does not exist** (no `apps/dashboard/src/app/settings/` directory). Users cannot actually change the active provider.

**What does NOT work:**

1. **Provider routing is a TODO:** `apps/dashboard/src/app/api/chat/route.ts` line 100-104:
   ```typescript
   const selectedProvider = body.options?.provider || 'local';
   console.log(`[Chat] Provider: ${selectedProvider}, Message: ...`);
   // TODO: Route to different providers based on selectedProvider when implemented
   ```
   The provider value is extracted and logged, but **every request goes to the same local agent** regardless of the selected provider.

2. **Agent API ignores provider:** `apps/agent-api/app/schemas/chat.py` — `ChatRequest` has only `messages: List[Message]`. No `provider` field. No `model` field. The agent always uses whatever model is configured at startup.

3. **No mid-thread switching:** Even if provider routing were implemented, the conversation history lives in the LangGraph agent's checkpoint store. Switching providers mid-thread would mean the new provider has no access to the conversation context (different checkpoint backends, different message formats).

4. **No settings page:** Users cannot configure API keys, endpoints, or active providers through the UI.

**What the agent backend supports (but isn't exposed):**

The agent-api has an `LLMRegistry` (`apps/agent-api/app/services/llm.py`) that:
- Registers multiple models at startup based on env vars
- Supports `ChatOpenAI` (for vLLM and OpenAI) with fallback chain
- Has `LLMService.call(model_name=...)` for per-request model selection
- But this is NOT wired to the chat API — no way for a user to specify a model

**Summary:**
- The **scaffolding** for multi-provider exists (UI component, settings schema, provider type)
- The **implementation** does not exist (no routing, no settings page, no model passthrough)
- **Mid-thread switching** (the LangCraft-style capability) has zero implementation

**Gap to close:**
1. Create `/settings` page with provider configuration UI
2. Implement provider routing in `/api/chat/route.ts` (the TODO)
3. For mid-thread continuity: need a conversation history serialization layer that works across providers (not trivial — LangGraph checkpoints are provider-specific)

---

## Q5: Model-Agnostic Agent Behavior

**Is the ZakOps agent model-agnostic in practice?**

### Status: NOT MODEL-AGNOSTIC — Structurally tied to Qwen/OpenAI-compatible APIs

**Hardcoded dependencies on current model:**

| Dependency | Location | What Breaks |
|-----------|----------|-------------|
| System prompt names Qwen | `app/core/prompts/system.md` line 10: *"You are powered by Qwen 2.5 (32B-Instruct-AWQ)"* | Factually false with any other model |
| vLLM Hermes tool parser | `docker-compose.yml`: `--tool-call-parser hermes` | Tool calling format changes with different providers |
| OpenAI API format assumed | All LLM calls use `ChatOpenAI` from LangChain | Claude, Gemini use different client classes |
| Response parsing handles GPT-5 blocks | `app/utils/graph.py` lines 29-72 | Claude/Gemini have different response structures |
| JSON mode via OpenAI format | `app/services/llm.py` lines 442-498: `response_format={"type": "json_object"}` | Claude uses different structured output API |
| Deal count query override | `apps/dashboard/src/app/api/chat/route.ts` lines 118-121: *"Qwen 2.5 is unreliable"* | Hardcoded workaround for Qwen-specific behavior |

**What IS abstracted:**
- `LLMRegistry` pattern allows registering multiple models
- `LLMService` wraps calls with retry and fallback
- LangChain's `bind_tools()` handles OpenAI→other format conversion (partially)
- Token counting falls back to approximate counter for unknown models
- Temperature/sampling params are env-configurable

**What would break if you switched to Claude:**
1. System prompt identity claim (cosmetic but misleading)
2. `ChatOpenAI` instantiation → need `ChatAnthropic`
3. Tool calling format (Hermes → Claude XML)
4. JSON mode API differences
5. Response parsing for structured output
6. Deal count workaround (may not be needed — Claude may handle it correctly)

**What would break if you switched to GPT-4o:**
1. System prompt identity claim
2. Likely works otherwise — GPT uses OpenAI API format
3. Hermes parser → would need OpenAI native tool parser
4. Deal count workaround (may not be needed)

**What would break if you switched to Gemini:**
1. Everything from Claude list, plus
2. Need `ChatVertexAI` or `ChatGoogleGenerativeAI`
3. Different auth model (service account vs API key)

**Verdict:** The agent is **OpenAI-API-compatible-model-semi-agnostic** — it can work with any model served behind an OpenAI-compatible API (vLLM, OpenRouter, Together AI). It is NOT provider-agnostic across Claude/Gemini/other native APIs without code changes.

---

## Q6: Additional Questions You Should Be Asking

### 6.1 — Conversation Persistence and Context Recovery

**Question:** When a user closes the browser and returns, does the chat conversation persist? If they switch between deal-scoped and global chat, is context preserved?

**Why this matters:** Operator workflows span hours/days. If chat state is ephemeral, the user loses all context on refresh. LangGraph checkpoints store conversation state, but the dashboard uses `sessionStorage` for session IDs — these are lost on tab close.

### 6.2 — Tool Execution Reliability Under Load

**Question:** What happens when the local vLLM (Qwen 2.5) is slow or unresponsive? Does the chat degrade gracefully, or does the user see timeouts?

**Why this matters:** The `/api/chat/route.ts` has a 3-strategy fallback (Agent Provider → Backend agent → Helpful response), but Strategy 3 returns static text — not tool-backed answers. If vLLM is down, the user gets a "service starting up" message for all queries. There is no warm standby to a cloud model.

### 6.3 — Proposal Execution Audit Trail

**Question:** When a user approves a proposal in chat (e.g., "transition deal to screening"), is that action recorded with full provenance (who approved, when, from which session)?

**Why this matters:** For M&A compliance, every deal state change needs an audit trail. If proposals are executed without tracing back to the chat session and operator, there's a governance gap.

### 6.4 — Tool Permission Boundaries

**Question:** What prevents the agent from calling `transition_deal` with a stage the user didn't intend? Does the HITL approval surface enough context for the user to catch mistakes?

**Why this matters:** The agent picks tool parameters based on LLM inference. If it infers the wrong deal ID or wrong target stage, the user only sees what the proposal surface shows. If the proposal display is minimal, the user may approve a wrong action.

### 6.5 — MCP Bridge Security: Who Can Call It?

**Question:** The MCP bridge on port 9100 has `ZAKOPS_BRIDGE_BEARER_REQUIRED=false` (disabled for LangSmith compatibility). Who else on the network can call these tools?

**Why this matters:** With bearer auth disabled, any service that can reach port 9100 can approve quarantine items, create deals, and transition deal stages. The bridge log shows external IPs (34.59.244.194) hitting it. There are no IP allowlists.

### 6.6 — End-to-End Latency Budget

**Question:** What is the actual wall-clock time from "user sends message" to "agent responds with tool result" for a typical deal query?

**Why this matters:** Local Qwen 2.5-32B on a single GPU has inference latency. If a "list my deals" query takes 8+ seconds, the operator experience degrades. Compare this to a cloud Claude/GPT call at ~2 seconds.

### 6.7 — Error Recovery in Chat

**Question:** If a tool call fails mid-conversation (e.g., backend returns 500 on `transition_deal`), what does the user see? Can they retry?

**Why this matters:** Today, tool failures likely surface as either an opaque error message or a hallucinated "I've completed that" response from the LLM. There's no retry mechanism or error-specific UI in the chat.

### 6.8 — Data Freshness in Chat vs Dashboard

**Question:** When the agent calls `list_deals` and returns results, are those results guaranteed to be consistent with what the dashboard shows at the same moment?

**Why this matters:** The chat agent calls the backend API directly, while the dashboard uses its own fetch cycle. If a deal was just transitioned via the dashboard, the agent might return stale data from its last tool call. There's no cache invalidation protocol between chat and dashboard.

### 6.9 — Operator Identity Across Surfaces

**Question:** Is the operator identity (who is acting) consistent across chat, dashboard UI, and MCP bridge? When a deal is approved from quarantine in the UI vs from chat, does the same operator name appear?

**Why this matters:** `operator_name` is a freeform text field in quarantine processing. The dashboard uses a localStorage value. The chat agent may use a different identifier. The MCP bridge uses `executor_id`. If these diverge, the audit trail breaks.

### 6.10 — What Happens When Both Surfaces Act Simultaneously?

**Question:** If an operator approves a quarantine item via the dashboard UI while the LangSmith agent simultaneously tries to approve the same item via MCP bridge — what happens?

**Why this matters:** The process endpoint (`POST /api/quarantine/{id}/process`) checks `status` before processing, but there's no optimistic locking on the quarantine item itself. Two concurrent approvals could race.

---

## Summary Matrix

| # | Capability | Status | Gap Severity |
|---|-----------|--------|-------------|
| Q1 | Email injection from chat | **Not Supported** | HIGH — core workflow gap |
| Q2 | Research delegation to LangSmith | **Not Supported** | HIGH — segregation of duties broken |
| Q3 | Quarantine actions from chat | **Partially Supported** | MEDIUM — tools exist at MCP level but not in local agent |
| Q4 | Multi-model mid-thread switching | **Not Supported** | HIGH — scaffolding exists, implementation missing |
| Q5 | Model-agnostic agent | **Partially Supported** | MEDIUM — works with OpenAI-compatible APIs only |

### Priority Gaps (Recommended Closure Order)

1. **Q3 — Quarantine tools in local agent** (MEDIUM effort, HIGH impact) — The backend endpoints and MCP tools already exist. Wire `list_quarantine`, `approve_quarantine`, `reject_quarantine` into the local agent's tool registry. Enables chat as a control surface for the most critical operator workflow.

2. **Q1 — Email trigger from chat** (MEDIUM effort, HIGH impact) — Add a tool that triggers the LangSmith agent's email scan or creates a delegation task. Requires defining the contract between local agent and LangSmith agent for email operations.

3. **Q2 — Research delegation** (HIGH effort, HIGH impact) — Requires building the push-model delegation: local agent creates a research task → LangSmith claims it → result flows back to chat. The delegation infrastructure exists but the initiation path from chat doesn't.

4. **Q4 — Multi-model routing** (HIGH effort, STRATEGIC impact) — Implement provider routing in `/api/chat/route.ts`, create settings page, solve conversation context portability across providers. The hardest part is mid-thread switching with context preservation.

5. **Q5 — Model agnosticism** (MEDIUM effort, STRATEGIC impact) — Abstract the system prompt identity, add provider-specific LLM client factories, normalize tool calling format across providers. Can be done incrementally alongside Q4.

---

## Appendix: Source File Index

| File | Lines | Relevance |
|------|-------|-----------|
| `apps/agent-api/app/core/langgraph/tools/__init__.py` | 25-34 | Agent tool registry (8 tools) |
| `apps/agent-api/app/core/prompts/system.md` | 1-146 | Agent system prompt (Qwen-specific) |
| `apps/agent-api/app/schemas/chat.py` | 56-67 | ChatRequest schema (no provider field) |
| `apps/agent-api/app/services/llm.py` | 76-219 | LLMRegistry + model initialization |
| `apps/backend/mcp_server/server.py` | — | MCP bridge tools (12 tools) |
| `apps/backend/mcp_server/tool_schemas.py` | — | MCP tool input schemas |
| `apps/backend/src/api/orchestration/delegation_types.py` | — | Research task type definitions |
| `apps/dashboard/src/app/api/chat/route.ts` | 79-279 | Chat route handler (provider TODO) |
| `apps/dashboard/src/app/chat/page.tsx` | 242-489 | Chat UI (provider state, proposal flow) |
| `apps/dashboard/src/components/chat/ProviderSelector.tsx` | 1-91 | Provider selector component |
| `apps/dashboard/src/lib/settings/provider-settings.ts` | 1-135 | Provider settings (localStorage) |
| `apps/agent-api/mcp_bridge/agent_contract.py` | 1-928 | LangSmith agent operating contract |
| `Zaks-llm/docker-compose.yml` | 10-18 | vLLM model configuration |
