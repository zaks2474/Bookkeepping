# MISSION: CHAT-CONTROL-SURFACE-001
## Chat as Universal Control Surface — Full-Stack Agent Capability Expansion
## Date: 2026-02-19
## Classification: Platform Capability Build (Full-Stack)
## Prerequisite: DEAL-UX-PIPELINE-001 v2 (Complete), SYSTEM-CAPABILITY-ASSESSMENT-2026-02-19
## Successor: None (self-contained)

---

## Mission Objective

Transform the ZakOps chat interface from a deal-management-only assistant into a universal control surface where an operator can manage quarantine, trigger research delegation, switch LLM providers mid-session, and act on the full deal lifecycle — all from natural language conversation.

The SYSTEM-CAPABILITY-ASSESSMENT-2026-02-19 identified 5 primary gaps and 10 additional risk areas. This mission closes all of them in a single coordinated execution.

**What this mission delivers:**
1. **Quarantine tools in the local agent** (Q3) — `list_quarantine_items`, `approve_quarantine_item`, `reject_quarantine_item`, `escalate_quarantine_item` added to the LangGraph agent tool registry, callable from chat with HITL approval gates
2. **Research delegation from chat** (Q2) — `delegate_research` tool that creates a backend delegation task, claimable by the LangSmith execution agent
3. **Email trigger from chat** (Q1) — `trigger_email_scan` tool that creates an `EMAIL_TRIAGE.PROCESS_INBOX` delegation task
4. **Multi-provider routing** (Q4) — Chat route routes to the selected provider (local/OpenAI/Anthropic/custom); settings page already exists with ProviderSection UI
5. **Model-agnostic system prompt** (Q5) — System prompt parameterized to accept any model identity; Qwen-specific hardcoding removed
6. **Operational hardening** (Q6.1-Q6.10) — Operator identity consistency, conversation persistence, race condition guards, error recovery in chat, MCP bridge IP allowlist

**What this mission does NOT do:** No DB migrations. No new backend API endpoints (uses existing delegation + quarantine endpoints). No agent graph restructure (adds tools only). No MCP bridge tool definition changes (but adds IP allowlist security to MCP server).

**Contract Surfaces Affected:** 8 (Agent Config — new tools + HITL expansion), 9 (Design System — settings page polish, provider UI warnings), 15 (MCP Bridge — IP allowlist security hardening)

---

## Architectural Constraints

- **BackendClient is the single HTTP client** — per HYBRID-GUARDRAIL-EXEC-002. New tools use `get_backend_client()`, never raw httpx
- **HITL_TOOLS frozenset is the approval gate** — per `apps/agent-api/app/schemas/agent.py` line 170. New quarantine tools must be added here
- **`@tool` decorator pattern** — per LangChain convention in `deal_tools.py`. All new tools use `@tool` with Pydantic input schemas
- **`delegate_actions` feature flag** — delegation tasks require this flag to be ON in the backend
- **Promise.allSettled pattern** — per DEAL-INTEGRITY-UNIFIED-001 for any new dashboard fetches
- **Surface 9 compliance** — per `.claude/rules/design-system.md` for any UI changes
- **System prompt is template-formatted** — `{agent_name}`, `{current_date_and_time}`, `{long_term_memory}` are injected by `load_system_prompt()` in `app/core/prompts/__init__.py`

## Anti-Pattern Examples

### WRONG: Raw httpx call in agent tool
```python
async with httpx.AsyncClient() as client:
    resp = await client.get(f"http://host.docker.internal:8091/api/quarantine")
```

### RIGHT: BackendClient with correlation_id
```python
client = _get_client()
result = await client.raw_request("GET", "/api/quarantine")
```

### WRONG: Hardcoded model identity in system prompt
```
You are powered by Qwen 2.5 (32B-Instruct-AWQ), a large language model created by Alibaba Cloud.
```

### RIGHT: Parameterized model identity
```
You are powered by {model_identity}, running on the ZakOps infrastructure.
```

### WRONG: Provider TODO in chat route (current state)
```typescript
// TODO: Route to different providers based on selectedProvider when implemented
```

### RIGHT: Provider switch with factory pattern
```typescript
const provider = await getProviderForType(selectedProvider);
const response = await provider.chat({ messages, session_id });
```

## Pre-Mortem

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Quarantine approve tool called without HITL gate → auto-approves spam into pipeline | HIGH if HITL_TOOLS not updated | CRITICAL | Add all 4 quarantine tools to HITL_TOOLS frozenset; verify in Gate P2 |
| 2 | Provider routing sends to OpenAI but no API key configured → silent failure | MEDIUM | MEDIUM | Provider factory validates key presence; fallback to local with warning |
| 3 | Research delegation creates task but `delegate_actions` flag is OFF → 503 surfaced to user | MEDIUM | LOW | Tool catches 503 and returns human-readable "Delegation is disabled" message |
| 4 | System prompt loses `{model_identity}` variable → renders literal text | LOW | MEDIUM | `load_system_prompt()` .format() handles it — add `model_identity` to kwargs with fallback |
| 5 | BackendClient doesn't have quarantine methods → tools use raw_request → type safety lost | CERTAIN | LOW | Add typed `list_quarantine()`, `process_quarantine()` methods to BackendClient |

---

## Phase 0 — Discovery & Baseline
**Complexity:** S | **Estimated touch points:** 0 (read-only)

**Purpose:** Verify baseline state and confirm all findings from the capability assessment are still current.

### Tasks
- P0-01: **Verify agent tool count** — `apps/agent-api/app/core/langgraph/tools/__init__.py` has exactly 8 tools
- P0-02: **Verify HITL_TOOLS** — `apps/agent-api/app/schemas/agent.py` line 170 contains only `transition_deal` and `create_deal`
- P0-03: **Verify chat route TODO** — `apps/dashboard/src/app/api/chat/route.ts` line 104 still has the TODO comment
- P0-04: **Verify system prompt Qwen reference** — `apps/agent-api/app/core/prompts/system.md` line 10 hardcodes Qwen
- P0-05: **Verify `delegate_actions` flag** — `SELECT value FROM zakops.feature_flags WHERE key='delegate_actions'`
- P0-06: **Run `make validate-local`** — capture baseline
- P0-07: **Identify affected surfaces** — Surface 8 (Agent Config): new tools change agent capability. Surface 9 (Design System): settings page.

### Gate P0
- All 6 findings confirmed still current
- `make validate-local` PASS
- Surface list: 8, 9

---

## Phase 1 — Backend: Quarantine Methods on BackendClient
**Complexity:** S | **Estimated touch points:** 1

**Purpose:** Add typed methods for quarantine and delegation operations to the agent's BackendClient.

### Blast Radius
- **Services affected:** Agent API only (client-side HTTP wrapper)
- **Pages affected:** None
- **Downstream consumers:** New quarantine/delegation tools in Phases 2-3

### Tasks
- P1-01: **Add `list_quarantine()` method** to `apps/agent-api/app/services/backend_client.py` — `GET /api/quarantine?status=pending`, returns `List[Dict[str, Any]]`
- P1-02: **Add `process_quarantine()` method** — `POST /api/quarantine/{item_id}/process` with `QuarantineProcess` fields: `action`, `processed_by` (NOT operator_name), `reason`, `expected_version` (for optimistic locking, handles 409 Conflict). Returns `Dict[str, Any]`
- P1-03: **Add `create_delegation_task()` method** — Two endpoints based on context:
  - Deal-scoped: `POST /api/deals/{deal_id}/tasks` (uses `DelegatedTaskCreate` model — requires deal_id in path)
  - Global: `POST /api/delegation/tasks` (uses `DelegationTaskCreate` model — deal_id optional in body)
  - Both gated by `delegate_actions` feature flag (returns 503 when OFF)
  - Fields: `task_type`, `title`, `description`, `context`, `priority`. Returns `Dict[str, Any]`

### Rollback Plan
1. Revert `backend_client.py` changes
2. Verify: agent starts without errors

### Gate P1
- BackendClient has `list_quarantine`, `process_quarantine`, `create_delegation_task` methods
- No import errors on agent-api startup

---

## Phase 2 — Agent: Quarantine Tools (Q3)
**Complexity:** M | **Estimated touch points:** 3

**Purpose:** Add 4 quarantine tools to the LangGraph agent, all mutation tools with HITL approval gates.

### Blast Radius
- **Services affected:** Agent API (new tools)
- **Pages affected:** Chat page (new tool responses appear in conversation)
- **Downstream consumers:** Chat UI proposal rendering

### Tasks
- P2-01: **Create `quarantine_tools.py`** in `apps/agent-api/app/core/langgraph/tools/` — 4 tools:
  - `list_quarantine_items` — calls `client.list_quarantine()`, returns formatted summary. LOW risk, no approval.
  - `approve_quarantine_item` — calls `client.process_quarantine(item_id, action="approve")`. CRITICAL, HITL required.
  - `reject_quarantine_item` — calls `client.process_quarantine(item_id, action="reject", reason=...)`. HIGH, HITL required.
  - `escalate_quarantine_item` — calls `client.process_quarantine(item_id, action="escalate")`. HIGH, HITL required.
  - Follow `@tool` + Pydantic input schema pattern from `deal_tools.py`; use `_get_client()` for BackendClient
- P2-02: **Register tools in `__init__.py`** — import from `quarantine_tools.py`, add all 4 to the `tools` list (now 12)
- P2-03: **Add to HITL_TOOLS** — in `apps/agent-api/app/schemas/agent.py`, add `approve_quarantine_item`, `reject_quarantine_item`, `escalate_quarantine_item` to `HITL_TOOLS` (now 5)

### Rollback Plan
1. Remove `quarantine_tools.py`, revert `__init__.py` and `agent.py`

### Gate P2
- Agent API starts without import errors
- `tools` list has 12 entries (was 8)
- `HITL_TOOLS` has 5 entries (was 2)
- `curl localhost:8095/health` returns healthy

---

## Phase 3 — Agent: Delegation Tools (Q1 + Q2)
**Complexity:** M | **Estimated touch points:** 2

**Purpose:** Add research delegation and email trigger tools to the local agent.

### Blast Radius
- **Services affected:** Agent API (new tools)
- **Pages affected:** Chat page
- **Downstream consumers:** Backend delegation system, LangSmith agent (claims tasks)

### Tasks
- P3-01: **Create `delegation_tools.py`** in `apps/agent-api/app/core/langgraph/tools/` — 2 tools:
  - `delegate_research` — Creates a delegation task (`RESEARCH.COMPANY_PROFILE`, `RESEARCH.BROKER_PROFILE`, or `RESEARCH.MARKET_SCAN`). Params: `deal_id` (optional for broker/market), `research_type`, `query`, `context`. Calls `client.create_delegation_task()`. HIGH risk, HITL required. Handles 503 (delegation disabled) with user-friendly message.
  - `trigger_email_scan` — Creates `EMAIL_TRIAGE.PROCESS_INBOX` delegation task. No deal_id required. MEDIUM risk, HITL required. Handles 503 gracefully.
- P3-02: **Register tools in `__init__.py`** — add both (now 14 total)
- P3-03: **Add to HITL_TOOLS** — add both (now 7 total)

### Rollback Plan
1. Remove `delegation_tools.py`, revert `__init__.py` and `agent.py`

### Gate P3
- Agent API starts without errors; `tools` list has 14; `HITL_TOOLS` has 7
- `delegate_research` tool schema validates `research_type` against known types

---

## Phase 4 — Agent: Model-Agnostic System Prompt (Q5)
**Complexity:** S | **Estimated touch points:** 2

**Purpose:** Remove Qwen-specific hardcoding; parameterize model identity.

### Blast Radius
- **Services affected:** Agent API (prompt template)
- **Pages affected:** None
- **Downstream consumers:** LLM responses

### Tasks
- P4-01: **Parameterize system prompt** in `apps/agent-api/app/core/prompts/system.md`:
  - Line 10: `{model_identity}` replaces hardcoded Qwen text
  - Line 67: Model identity truthfulness instruction parameterized
  - Tool count updated to 14; add quarantine + delegation tools to Available Tools section
  - Add TOOL ROUTING entries for quarantine/delegation queries
- P4-02: **Pass `model_identity` in `load_system_prompt()`** — in `apps/agent-api/app/core/prompts/__init__.py`, add `model_identity=getattr(settings, 'MODEL_IDENTITY', settings.DEFAULT_LLM_MODEL)` to `.format()` kwargs

### Rollback Plan
1. Revert `system.md` and `__init__.py`

### Gate P4
- Agent starts without prompt format errors
- System prompt contains no hardcoded "Qwen" references
- Chat → "What model are you?" → responds with configured model name

---

## Phase 5 — Dashboard: Multi-Provider Chat Routing (Q4)
**Complexity:** M | **Estimated touch points:** 4

**Purpose:** Implement provider routing in chat route; create OpenAI/Anthropic/Custom provider implementations.

### Blast Radius
- **Services affected:** Dashboard (chat route, provider service)
- **Pages affected:** Chat page, Settings page
- **Downstream consumers:** All chat interactions

### Tasks
- P5-01: **Create OpenAI provider** — `apps/dashboard/src/lib/agent/providers/openai.ts`. Implements `AgentProvider`. Uses OpenAI chat completions API. Maps responses to `AgentResponse` format.
- P5-02: **Create Anthropic provider** — `apps/dashboard/src/lib/agent/providers/anthropic.ts`. Uses Anthropic Messages API. Maps to `AgentResponse`.
- P5-03: **Create Custom provider** — `apps/dashboard/src/lib/agent/providers/custom.ts`. OpenAI-compatible format to user-configured endpoint.
- P5-04: **Update provider-service.ts** — Replace `console.warn` fallbacks with actual provider creation. NOTE: Provider settings live in localStorage (client-side only). The client must send provider config (including API keys) in the request body to the server-side chat route. The route MUST NOT attempt to read localStorage directly (server has no access).
- P5-05: **Implement routing in chat route** — `apps/dashboard/src/app/api/chat/route.ts`:
  - Replace TODO at line 104 with provider routing based on `selectedProvider`
  - Read provider config from `body.providerConfig` (sent by client from localStorage)
  - `local` → existing agent API path (unchanged, full tool access)
  - `openai`/`anthropic`/`custom` → direct LLM call with streaming (`stream: true`), text-only — no ZakOps tools (MVP). Display "text-only" warning badge in chat UI when non-local provider active.
  - Validate API key presence; fallback to local with warning if missing
  - SSRF guard: validate custom provider endpoint URL format (must be https:// or http://localhost)
- P5-06: **Conversation context for non-local** — Client must send message history in request body (current client sends only `query/scope/session_id`). Add `messages` array to request. Include lightweight ZakOps system prompt for cloud providers so they maintain persona context.
- P5-07: **Update chat page to send provider config** — In `chat/page.tsx`, read provider settings from localStorage and include `providerConfig` object in POST body to `/api/chat`. Include full message history from session state for non-local providers.

### Decision Tree
- **IF** `local` → agent API at 8095, full tool access
- **ELSE IF** `openai` AND apiKey → OpenAI chat completions
- **ELSE IF** `anthropic` AND apiKey → Anthropic Messages API
- **ELSE IF** `custom` AND endpoint → custom endpoint
- **ELSE** → fallback to local with warning

### Rollback Plan
1. Revert chat/route.ts, provider-service.ts, remove new provider files

### Gate P5
- `npx tsc --noEmit` passes
- Chat with `local` works (unchanged)
- Chat with `openai` (if key configured) returns text response
- Fallback to local works when provider unavailable
- Settings ProviderSection loads and saves

---

## Phase 6 — Operational Hardening (Q6 Gaps)
**Complexity:** M | **Estimated touch points:** 5

**Purpose:** Close the 10 additional risk areas from the assessment.

### Tasks

**Q6.1 — Conversation Persistence:**
- P6-01: **Persist session_id to localStorage** — in `chat/page.tsx`, verify `loadSession()` uses localStorage (not sessionStorage). Fix if needed.

**Q6.5 — MCP Bridge Security:**
- P6-02: **Add IP allowlist** — in `apps/backend/mcp_server/server.py`, add middleware checking `request.client.host` against `MCP_ALLOWED_IPS` env var (default: `127.0.0.1,172.0.0.0/8`). Log/reject unauthorized IPs when bearer auth is disabled.

**Q6.7 — Error Recovery in Chat:**
- P6-03: **Retry button for failed proposals** — in chat UI, when proposal execution fails, show "Retry" button.

**Q6.9 — Operator Identity Consistency:**
- P6-04: **Standardize `processed_by`** — Quarantine tools read from `OPERATOR_NAME` env var (default: "Zak") and pass as the `processed_by` field (matching backend `QuarantineProcess` model). Pass consistently to all `process_quarantine()` calls.

**Q6.10 — Concurrent Quarantine Actions:**
- P6-05: **Optimistic lock via `expected_version`** — All quarantine mutation tools (`approve`, `reject`, `escalate`) must include `expected_version` from the item's current state in the POST payload. Backend returns 409 Conflict on version mismatch. Tool catches 409 and returns "Item was modified by another operator — please refresh and retry" message to user. Do NOT use GET-then-POST pattern (race-prone).

**Q6.2 — vLLM Down Fallback:**
- P6-06: **Cloud fallback** — In chat route, if local agent fails AND cloud provider configured, retry with cloud. Provides warm standby.

**Q6.3 — Proposal Audit Trail:**
- P6-07: **Log proposal executions** — In `execute-proposal/route.ts`, add structured log: `{ proposal_id, action, approved_by, session_id, timestamp }`.

**Q6.4 — Tool Permission Display:**
- P6-08: **Enhance proposal cards** — Verify each proposal shows tool name, parameters, risk badge. Enhance where needed.

**Q6.8 — Data Freshness:**
- P6-09: **Add data_fetched_at to responses** — In chat route, include timestamp in done event metadata.

**Q6.6 — Latency Display:**
- P6-10: **Surface latency in chat UI** — Display `latency_ms` from response (e.g., "Responded in 2.3s").

### Rollback Plan
1. Revert individual changes per-file

### Gate P6
- `npx tsc --noEmit` passes
- Session persists across page reload
- Failed proposals show retry button
- Proposal execution logged with provenance

---

## Phase 7 — Unit Tests (A3 Remediation)
**Complexity:** M | **Estimated touch points:** 3

**Purpose:** Add automated test coverage for all new tools and BackendClient methods. (A3 finding: zero test coverage was flagged CRITICAL by all 3 reviewers.)

### Tasks
- P7-01: **Create `tests/test_quarantine_tools.py`** — in `apps/agent-api/tests/`:
  - Mock `BackendClient` responses for `list_quarantine`, `process_quarantine`
  - Test each tool's Pydantic input schema validation
  - Test HITL gate enforcement: verify all 3 mutation tools are in `HITL_TOOLS`
  - Test error paths: 409 Conflict (version mismatch), 404 (item not found), 503 (backend down)
  - Test `processed_by` field passed correctly
- P7-02: **Create `tests/test_delegation_tools.py`** — in `apps/agent-api/tests/`:
  - Mock `BackendClient` for both delegation endpoints
  - Test `delegate_research` with/without `deal_id` (routes to correct endpoint)
  - Test `trigger_email_scan` creates correct task type
  - Test 503 handling (delegation disabled) returns user-friendly message
  - Test HITL gate enforcement for both tools
- P7-03: **Create `tests/test_backend_client_new_methods.py`** — in `apps/agent-api/tests/`:
  - Test `list_quarantine()` → correct GET URL + params
  - Test `process_quarantine()` → correct POST URL + `processed_by`/`expected_version` payload
  - Test `create_delegation_task()` → routes to correct endpoint based on `deal_id`

### Gate P7
- `pytest apps/agent-api/tests/test_quarantine_tools.py` PASS
- `pytest apps/agent-api/tests/test_delegation_tools.py` PASS
- `pytest apps/agent-api/tests/test_backend_client_new_methods.py` PASS

---

## Phase 8 — Rebuild + Validate + Playwright E2E
**Complexity:** M | **Estimated touch points:** 0

### Tasks
- P8-01: **Rebuild agent-api** — `COMPOSE_PROJECT_NAME=zakops docker compose build agent-api && docker compose up -d agent-api --no-deps`
- P8-02: **`npx tsc --noEmit`** in `apps/dashboard`
- P8-03: **`make validate-local`**
- P8-04: **`make sync-agent-types`** — regenerate dashboard types for new agent tools

**Playwright E2E Tests** (browser automation):
- P8-05: **Playwright: Chat page loads** — navigate to /chat, verify page renders, input field exists
- P8-06: **Playwright: Settings provider section** — navigate to /settings, verify ProviderSection renders, can select providers, save works
- P8-07: **Playwright: Chat send message** — send "Hello" in chat, verify response appears (SSE stream completes)
- P8-08: **Playwright: Session persistence** — send message, reload page, verify session_id persists in localStorage
- P8-09: **Playwright: Provider switching** — switch to non-local provider, verify "text-only" badge appears, switch back to local
- P8-10: **Playwright: Proposal card rendering** — if quarantine items exist, trigger "Show quarantine items" and verify tool response renders

**Manual Verification** (cannot be fully automated):
- P8-11: **Verify quarantine HITL flow** — "Approve the TechCorp email" → proposal card → approve → deal created
- P8-12: **Verify delegation flow** — "Research CompanyX" → proposal card → approve → task created
- P8-13: **Verify email trigger** — "Check for new emails" → proposal card → approve → task created
- P8-14: **Verify model identity** — "What model are you?" → responds with configured model name
- P8-15: **Update `/home/zaks/bookkeeping/CHANGES.md`**

### Gate P8
- All unit tests PASS (from P7)
- All Playwright E2E tests PASS
- `make validate-local` PASS; `npx tsc --noEmit` PASS
- Agent has 14 tools, 7 HITL-gated
- Browser confirms all 5 primary gaps + 10 hardening items closed

---

## Dependency Graph

```
P0 (Discovery)
 ↓
P1 (BackendClient methods) → P2 (Quarantine tools) → P4 (System prompt)
                           → P3 (Delegation tools) ↗
                                                      ↓
P5 (Provider routing) ─────────────────────────────→ P6 (Operational hardening)
                                                      ↓
                                                    P7 (Unit tests)
                                                      ↓
                                                    P8 (Rebuild + Playwright E2E + Validate)

P5 depends on P2-P4 completion (chat route used for testing tools).
Recommended order: P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8
```

---

## Acceptance Criteria

| AC | Description | Phase |
|----|-------------|-------|
| AC-1 | Agent has `list_quarantine_items`, `approve_quarantine_item`, `reject_quarantine_item`, `escalate_quarantine_item` tools | P2 |
| AC-2 | All quarantine mutation tools require HITL approval (in HITL_TOOLS frozenset) | P2 |
| AC-3 | Agent has `delegate_research` tool creating backend delegation tasks via correct endpoints (`/api/deals/{id}/tasks` or `/api/delegation/tasks`) | P3 |
| AC-4 | Agent has `trigger_email_scan` tool creating EMAIL_TRIAGE tasks | P3 |
| AC-5 | System prompt model-agnostic — no hardcoded Qwen references | P4 |
| AC-6 | Chat route routes to selected provider (local/openai/anthropic/custom) with client-sent provider config (not server-read localStorage) | P5 |
| AC-7 | Provider fallback to local with warning when unavailable; "text-only" badge for cloud providers | P5 |
| AC-8 | Chat session persists across tab close via localStorage | P6 |
| AC-9 | Quarantine mutations use `expected_version` for optimistic locking (handles 409 Conflict) | P6 |
| AC-10 | MCP bridge has IP allowlist when bearer auth disabled | P6 |
| AC-11 | Unit tests pass for quarantine tools, delegation tools, and BackendClient new methods | P7 |
| AC-12 | Playwright E2E tests pass for chat page, settings, session persistence, provider switching | P8 |
| AC-13 | `npx tsc --noEmit` + `make validate-local` PASS | P8 |
| AC-14 | CHANGES.md updated | P8 |

---

## Guardrails

1. **No DB migrations** — all changes are agent tools, dashboard routes, and system prompt
2. **No new backend API endpoints** — uses existing quarantine and delegation endpoints
3. **No generated file edits** — per V5PP deny rules
4. **No MCP bridge tool definition changes** — local agent calls backend directly via BackendClient. IP allowlist (P6-02) is a security hardening change to the MCP server transport layer, not a tool change.
5. **All quarantine mutations HITL-gated** — no auto-execute path
6. **Non-local providers are text-only MVP** — no ZakOps tool access for cloud providers
7. **Surface 9 compliance** — per `.claude/rules/design-system.md`
8. **WSL safety** — CRLF fix on new .sh files, ownership fix on /home/zaks/ files
9. **Delegation requires feature flag** — tools handle `delegate_actions=off` gracefully
10. **BackendClient pattern mandatory** — no raw httpx in tools

## Executor Self-Check Prompts

1. **After Phase 2:** Does the agent have 12 tools? Does `HITL_TOOLS` have 5 entries?
2. **After Phase 3:** Does the agent have 14 tools? Does `HITL_TOOLS` have 7 entries?
3. **After Phase 4:** Does the system prompt contain `{model_identity}`?
4. **After Phase 5:** Does switching provider actually change the chat backend? Is provider config sent from client (not read from localStorage on server)?
5. **After Phase 6:** Does session persist? Do quarantine mutations use `expected_version`? Do failed proposals show retry?
6. **After Phase 7:** Do all unit tests pass? Are error paths (409, 503, 404) tested?
7. **After Phase 8:** Do all Playwright E2E tests pass? Does `make validate-local` PASS?

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `apps/agent-api/app/services/backend_client.py` | P1 | Add quarantine + delegation methods |
| `apps/agent-api/app/core/langgraph/tools/__init__.py` | P2, P3 | Register new tools |
| `apps/agent-api/app/schemas/agent.py` | P2, P3 | Expand HITL_TOOLS frozenset |
| `apps/agent-api/app/core/prompts/system.md` | P4 | Parameterize model identity, add tool docs |
| `apps/agent-api/app/core/prompts/__init__.py` | P4 | Pass model_identity kwarg |
| `apps/dashboard/src/lib/agent/provider-service.ts` | P5 | Wire providers |
| `apps/dashboard/src/app/api/chat/route.ts` | P5, P6 | Provider routing, fallback, timestamps |
| `apps/dashboard/src/app/chat/page.tsx` | P6 | Session persistence, retry, latency |
| `apps/dashboard/src/app/api/chat/execute-proposal/route.ts` | P6 | Audit logging |
| `apps/backend/mcp_server/server.py` | P6 | IP allowlist |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `apps/agent-api/app/core/langgraph/tools/quarantine_tools.py` | P2 | 4 quarantine tools |
| `apps/agent-api/app/core/langgraph/tools/delegation_tools.py` | P3 | 2 delegation tools |
| `apps/dashboard/src/lib/agent/providers/openai.ts` | P5 | OpenAI provider |
| `apps/dashboard/src/lib/agent/providers/anthropic.ts` | P5 | Anthropic provider |
| `apps/dashboard/src/lib/agent/providers/custom.ts` | P5 | Custom provider |

### Files Read-Only (reference)
| File | Purpose |
|------|---------|
| `apps/agent-api/app/core/langgraph/tools/deal_tools.py` | Tool pattern reference |
| `apps/agent-api/app/core/langgraph/graph.py` | Graph tool binding |
| `apps/backend/mcp_server/server.py` | MCP quarantine tools (reference) |
| `apps/backend/src/api/orchestration/delegation_types.py` | Task type registry |
| `apps/dashboard/src/lib/agent/providers/local.ts` | Provider pattern reference |
| `apps/dashboard/src/components/settings/ProviderSection.tsx` | Settings UI (already exists) |

---

## Stop Condition

DONE when all 14 AC met, all unit tests + Playwright E2E tests pass, all validations pass, and browser confirms: quarantine actions work from chat with HITL gates, research delegation creates backend tasks via correct endpoints, email trigger creates inbox scan tasks, provider switching routes to correct backend with client-sent credentials, system prompt is model-agnostic, and all 10 operational hardening items are addressed.

Do NOT proceed to: MCP bridge tool changes, agent graph restructure, new backend endpoints, database migrations, or tool access for cloud providers.

---

## A3 Remediation Log

Findings incorporated from 3-agent review (Claude, Gemini, Codex) on 2026-02-19:

| # | Severity | Finding | Fix Applied |
|---|----------|---------|-------------|
| 1 | CRITICAL | Delegation endpoint `/api/deals/{id}/delegate` does not exist | Fixed P1-03: uses `/api/deals/{id}/tasks` + `/api/delegation/tasks` |
| 2 | CRITICAL | Provider credentials in localStorage not accessible from server route | Fixed P5-04/P5-07: client sends providerConfig in request body |
| 3 | HIGH | `operator_name` field doesn't exist; backend uses `processed_by` | Fixed P1-02, P6-04 |
| 4 | HIGH | GET-then-POST race condition; backend has `expected_version` locking | Fixed P6-05: uses `expected_version` + handles 409 |
| 5 | HIGH | Tool naming drift (`list_quarantine` vs `list_quarantine_items`) | Fixed: canonical names throughout plan |
| 6 | HIGH | MCP scope contradiction ("no changes" vs P6-02 edit) | Fixed: guardrail 4 + surface 15 updated |
| 7 | CRITICAL | Zero test coverage for 6 new tools | Added P7 (unit tests) + P8 (Playwright E2E) |
| 8 | HIGH | Cloud providers have no system prompt context | Fixed P5-06: lightweight ZakOps system prompt for cloud |
| 9 | HIGH | "Universal Control Surface" vs text-only cloud contradiction | Fixed P5-05: text-only badge warning in UI |
| 10 | MEDIUM | Non-local context: client sends only query, not history | Fixed P5-06/P5-07: client sends messages array |
| 11 | MEDIUM | SSRF risk on custom provider endpoint | Fixed P5-05: URL format validation |
| 12 | HIGH | Dependency graph: P5 should depend on P2-P4 | Fixed dependency graph |

---

## Completion Report

To be filled after execution per Section 9b template.
