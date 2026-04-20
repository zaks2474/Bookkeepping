Hook registry initialized with 0 hook entries
Attempt 1 failed with status 503. Retrying with backoff... ApiError: {"error":{"code":503,"message":"This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.","status":"UNAVAILABLE"}}
    at throwErrorIfNotOK (file:///root/.npm-global/lib/node_modules/@google/gemini-cli/node_modules/@google/genai/dist/node/index.mjs:11716:30)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async file:///root/.npm-global/lib/node_modules/@google/gemini-cli/node_moI will verify the existence of `packages/contracts/mcp/tool-schemas.json` and check for any existing tests in `apps/agent-api/tests/` using the `list_directory` tool.
I will examine the contents of the `apps/agent-api/tests` directory to verify the existence of unit tests for the tools.
I will verify if `test_cost_tracking.py` contains any tool tests and, given the sparse testing, I'll document the low test coverage as a significant finding.
I have completed the analysis and identified critical gaps in testing, misalignments in the deal count query logic and contract surface numbering, and opportunities for world-class improvements in observability and UX. I am now ready to draft the comprehensive A3 review as requested.

## A3 REVIEW: CHAT-CONTROL-SURFACE-001

### 1. GAPS

1.  **[CRITICAL] Missing Unit Tests for New Tools & Client Methods**
    *   **Finding:** The plan includes "Verify" steps (manual/e2e) but strictly lacks unit tests for `quarantine_tools.py`, `delegation_tools.py`, and the new `BackendClient` methods. Given the high-stakes nature of "Quarantine Approval" and "Research Delegation", code-level verification is mandatory.
    *   **Recommendation:** Add a Phase 1.5 and Phase 3.5 to write `pytest` suites.
        *   `apps/agent-api/tests/test_backend_clHere is the A3 review of the mission plan **CHAT-CONTROL-SURFACE-001**.

## 1. GAPS

*   **[CRITICAL] Data Flow Violation (LocalStorage to Server):**
    *   **Finding:** Phase 5 task P5-04 states: *"Read API keys from provider settings (localStorage)"* inside `provider-service.ts`. The chat route (`apps/dashboard/src/app/api/chat/route.ts`) runs on the server. Server-side code **cannot** access the browser's `localStorage`.
    *   **Recommendation:** The client-side chat component (`page.tsx` or `useChat` hook) must read the configuration from `localStorage` and pass it in the request body (e.g., inside a `config` object) to the API route. The API route should then initialize the provider with these passed credentials.

*   **[HIGH] Test Coverage Zero:**
    *   **Finding:** The plan adds 6 new critical tools (Quarantine/Delegation) and new BackendClient methods but includes **zero** unit tests. `make validate-local` runs existing suites but does not verify the logic of new tools.
    *   **Recommendation:** Add a **Phase 2.5 and 3.5**: Create `tests/unit/test_quarantine_tools.py` and `tests/unit/test_delegation_tools.py` using `pytest` to mock `BackendClient` responses and verify tool outputs match the Pydantic schemas.

*   **[HIGH] Cloud Provider Context Blindness:**
    *   **Finding:** Phase 4 updates the *Local Agent's* system prompt (`apps/agent-api/.../system.md`). However, Phase 5 (Cloud Providers) runs in the Next.js Dashboard. If the Dashboard constructs calls to OpenAI/Anthropic, it needs to inject a system prompt. If it sends no system prompt, the cloud models will have no context of "ZakOps", the user, or the mission.
    *   **Recommendation:** Expose the system prompt template via an endpoint or shared package, or duplicate a lightweight version in the Dashboard to send to Cloud providers so they maintain persona consistency.

## 2. MISALIGNMENT

*   **[HIGH] "Universal Control Surface" vs. "Text-Only" Cloud:**
    *   **Finding:** The Mission Objective claims to transform chat into a "Universal Control Surface." However, Phase 5 explicitly states Cloud providers are *"text-only, no ZakOps tools"*. If a user switches to OpenAI to "act on the full deal lifecycle" (as promised in the objective), the system will fail to execute any tools. This breaks the primary mission promise.
    *   **Recommendation:** Either re-scope the mission to clarify that "Control Surface" features are Local-only, OR implement OpenAI Function Calling in the Dashboard provider to bridge calls back to the Agent API (significantly larger scope). For this mission, **explicit UI warnings** are required when switching to a provider that does not support tools.

*   **[MEDIUM] HITL UI Implementation details:**
    *   **Finding:** Phase 2 relies on adding tools to `HITL_TOOLS`. The plan assumes the frontend `ProposalCard` component automatically handles *any* tool in that list. If the UI has hardcoded checks for `transition_deal` vs `create_deal`, the new tools might render generically or break.
    *   **Recommendation:** In Phase 0, verify `apps/dashboard/src/components/chat/ProposalCard.tsx` (or similar) to ensure it renders a generic approval UI for unknown tools in the HITL list.

## 3. WORLD CLASS

*   **[HIGH] Streaming UX for Cloud:**
    *   **Finding:** The plan mentions "Text-only" for cloud but doesn't explicitly mandate **Streaming**. Waiting 5-10 seconds for a full OpenAI/Anthropic response (while the Local Agent streams via SSE) is a jarring UX degradation.
    *   **Recommendation:** Ensure `OpenAIProvider` and `AnthropicProvider` implement streaming responses (`stream: true`) and pipe chunks to the frontend using the `ai` SDK's `StreamingTextResponse` or the existing SSE format to match the Local Agent's fluidity.

*   **[MEDIUM] Token/Cost Visibility:**
    *   **Finding:** Switching to paid providers (OpenAI/Anthropic) introduces cost. The user has no visibility into this.
    *   **Recommendation:** In the response metadata (where latency is added in P6-10), also attempt to estimate or display token usage if provided by the upstream API, reinforcing the "Professional Operator" feel.

## 4. FULL-STACK IMPLEMENTATION

*   **Completeness:**
    *   **Agent:** Strong. Pydantic schemas and `BackendClient` pattern usage is correct.
    *   **Dashboard:** Weak on data flow (LocalStorage issue) and System Prompt injection.
    *   **Infrastructure:** Good (Docker, Environment).
    *   **Security:** Good (IP Allowlist, BackendClient usage).

*   **Summary Recommendation:**
    The plan is solid on the Python/Agent side but has critical architectural flaws on the Next.js/Dashboard side regarding **Data Flow (Secrets)** and **Context (System Prompts)**. Fix the API Key propagation strategy and add Unit Tests to make this a safe execution.
 The Provider architecture (P5) is clean. **Gap:** The `Custom` provider needs to validate the endpoint URL format to prevent SSRF or malformed requests.
4.  **Infra Layer**: `MCP_ALLOWED_IPS` is good. **Gap:** Ensure this env var is actually injected into the `agent-api` or `backend` container (wherever `mcp_server.py` runs) in `docker-compose.yml`. The plan doesn't mention updating `docker-compose.yml`.

### FINAL RECOMMENDATION
**Proceed with caution.** The plan is architecturally sound but risky due to low test coverage and potential regression of the "Deal Count" safety feature.
**Must Fix:** Add unit tests (Gap 1), fix "Deal Count" routing (Gap 3), and verify `FastMCP` middleware feasibility (Gap 4) before execution.
