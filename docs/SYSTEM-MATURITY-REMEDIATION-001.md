# MISSION: SYSTEM-MATURITY-REMEDIATION-001
## Full-Stack Gap Remediation — Agent Intelligence, Document Architecture, Observability & UX Polish
## Date: 2026-02-20
## Classification: Platform Maturity Build (Full-Stack, XL)
## Prerequisite: CHAT-CONTROL-SURFACE-001 (Complete 2026-02-20), INTERVIEW-ROUND-2-SYSTEM-MATURITY (2026-02-20)
## Successor: QA-SMR-VERIFY-001 (paired QA)

---

## Mission Objective

Close **every gap** identified in the Second Round Interview — System Maturity & User-Facing Intelligence (`/home/zaks/bookkeeping/docs/INTERVIEW-ROUND-2-SYSTEM-MATURITY.md`). The interview scored the system across 8 dimensions and found gaps in agent memory (6/10), onboarding integration (5/10), document architecture (4/10), model switching (5/10), observability (5/10), and settings UX (6/10). This mission remediates all of them.

**What this mission delivers:**
1. **Settings provider UX** — Current model lists, real API key validation, text-only mode indicator
2. **User profile → agent integration** — Profile injected into system prompt (including `investment_focus`), agent tool for profile access, investment focus filtering
3. **Model switching hardening** — Server-side model persistence (SQL migration for `chat_threads`), graceful degradation UI, server-side content filtering for cloud providers, automatic vLLM failover
4. **Agent resilience** — Retry with backoff on BackendClient (pool-first-then-retry), connection pooling, resilience config enforcement, chain-of-thought logging, budget enforcement wiring, background task health monitoring
5. **Bug fixes (P0 from 3-Pass Escalation)** — Fix broken `_get_deal_brain_facts()` method call, fix missing `investment_focus` in profile API, fix HITL tool result format (success + error paths), fix empty specialist brain context
6. **Document upload & API** — Multipart upload endpoint, artifact listing, download, text extraction (pypdf + python-docx), synthetic URL scheme for RAG ingest
7. **Dashboard materials panel** — Wire `DealDocuments.tsx` into **actual** `/deals/[id]/page.tsx` (NOT dead `DealWorkspace.tsx`), upload/download/delete/share/export handlers
8. **Deal document RAG & agent tools** — Ingest deal PDFs into RAG with deal_id scoping, 5 new agent tools (documents + email threads + entity lookup)
9. **Cross-session memory** — Upgrade tiered memory with LLM-backed summarization, summary pruning, retention policy, cross-database cascade via HTTP
10. **Observability & Intelligence** — Cost/stats endpoints (with global monthly aggregate), wire Prometheus middleware, background task health monitor, proactive urgency alerts, conviction score endpoint, dashboard analytics components
11. **Onboarding intelligence** — Incremental profile building from deal interactions, profile update from chat
12. **Cross-cutting hardening** — SCOPE_TOOL_MAP updated for all new tools, tool count machine-verified against system prompt, per-endpoint Redocly validation
13. **Playwright E2E** — Comprehensive tests for all new features with functional keyword naming, integrated into per-phase gates

**What this mission does NOT do:** No email OAuth integration (L-effort, separate mission). No multi-user auth middleware (future architecture). No S3 migration tooling (no current need). No MCP bridge tool changes. No Deal Genome or Broker Intelligence dashboard (deferred to follow-on mission per Pass 3 recommendations).

**Source material:**
- `/home/zaks/bookkeeping/docs/INTERVIEW-ROUND-2-SYSTEM-MATURITY.md` — 491 lines, 8-dimension maturity scorecard
- `/home/zaks/bookkeeping/docs/CHAT-CONTROL-SURFACE-001-COMPLETION.md` — predecessor mission completion report
- `/home/zaks/bookkeeping/docs/3-PASS-ESCALATION-REPORT.md` — 3-pass escalation framework (gap excavation, system expansion, differentiation)
- `/home/zaks/bookkeeping/docs/PASS-3-DIFFERENTIATION-ANALYSIS.md` — world-class differentiation analysis

**Contract Surfaces Affected:** 1 (Backend OpenAPI), 2 (Agent OpenAPI), 8 (Agent Config), 9 (Design System), 10 (Dependency Health), 12 (Error Taxonomy), 13 (Test Coverage), 17 (Dashboard Routes)

---

## Glossary

| Term | Definition |
|------|-----------|
| Tiered memory | 3-layer agent memory: Working (last 6 msgs), Recall (session summaries + brain facts), Long-term (mem0/pgvector — currently disabled) |
| BackendClient | Singleton HTTP client in agent-api for all backend calls (`apps/agent-api/app/services/backend_client.py`) |
| HITL | Human-in-the-loop approval gate — 7 tools require operator confirmation before execution |
| DataRoom | Local filesystem at `/home/zaks/DataRoom/` with deal folder hierarchy for document storage |
| ArtifactStore | Pluggable storage abstraction (`apps/backend/src/core/storage/`) — local (default) or S3 (opt-in) |
| Recall memory | Active memory tier built from `session_summaries` + `deal_brain` facts via `build_recall_memory()` |
| Content filtering | Pre-transmission scrubbing of PII/sensitive data before messages are sent to cloud LLM providers |
| Synthetic URL | Manufactured URL scheme (`dataroom://{deal_id}/artifacts/{artifact_id}`) for documents without real URLs, required by RAG `POST /rag/add` endpoint's mandatory `url` field |
| TaskMonitor | Lightweight fire-and-forget task wrapper that collects `asyncio.Task` references, logs failures, and exposes Prometheus counters for background task health |
| Conviction score | Composite metric (0-100) aggregating brain facts, risk count, blind spots, ghost knowledge, stall probability, and document coverage for a deal |
| Cross-database cascade | HTTP-based cascade between `zakops` (backend) and `zakops_agent` (agent) databases, since they are separate PostgreSQL databases with no FK relationship |

---

## 3-Pass Escalation Findings (Integrated)

This plan incorporates all findings from the 3-Pass Escalation Framework (`/home/zaks/bookkeeping/docs/3-PASS-ESCALATION-REPORT.md`):
- **Pass 1 — Gap Excavation:** 3 P0-critical bugs, 8 P1 findings, 8 P2 findings, 7 concrete improvements
- **Pass 2 — System Expansion:** 8 untapped synergies, 7 structural enhancements, 6 durability proposals
- **Pass 3 — Differentiation:** 7 category-defining opportunities (conviction ledger, deal genome, temporal reasoning, broker intelligence — deferred to follow-on mission except urgency alerts and conviction endpoint)

**P0-critical bugs integrated:** A-1 (dead DealWorkspace → Phase 6 rewritten), A-2 (broken brain facts → Phase 4), A-3 (missing investment_focus → Phase 2)

---

## Architectural Constraints

- **BackendClient is the single HTTP client** for agent → backend calls. New methods follow existing pattern. No raw httpx.
- **`@tool` decorator pattern** — per LangChain convention in `deal_tools.py`. All new tools use `@tool` with Pydantic input schemas.
- **HITL_TOOLS frozenset** — approval gate. New mutation tools must be added here.
- **`Promise.allSettled` mandatory** — per DEAL-INTEGRITY-UNIFIED-001. `Promise.all` banned in dashboard data-fetching.
- **Surface 9 compliance** — per `.claude/rules/design-system.md` for all UI changes.
- **`transition_deal_state()` single choke point** — no direct deal state mutations.
- **Generated files never edited** — per V5PP deny rules. Use `make sync-*` pipeline.
- **Port 8090 FORBIDDEN** — decommissioned.
- **Contract surface discipline** — `make update-spec → make sync-types → npx tsc --noEmit` chain after backend API changes.
- **RAG REST first** — retrieval uses RAG REST API (`POST /rag/query`), not pgvector/mem0 directly (Decision Lock).
- **Existing `DealDocuments.tsx` is complete** — do NOT rebuild; wire the existing component to real data.
- **Existing `file-uploader.tsx` is ready** — reuse for document upload, do not create new upload component.
- **`resilience.py` config already defined** — enforce it, don't redefine it.

## Anti-Pattern Examples

### WRONG: Hardcoded model list that drifts
```typescript
const models = ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229'];
```

### RIGHT: Curated list with date comment and update instructions
```typescript
// Last verified: 2026-02-20. Update when new models release.
const ANTHROPIC_MODELS = [
  { id: 'claude-opus-4-6', label: 'Claude Opus 4.6 (Most capable)' },
  { id: 'claude-sonnet-4-6', label: 'Claude Sonnet 4.6 (Balanced)' },
  { id: 'claude-haiku-4-5-20251001', label: 'Claude Haiku 4.5 (Fast)' },
];
```

### WRONG: Sending full conversation to cloud without filtering
```typescript
const response = await openaiProvider.chat({ messages: body.messages });
```

### RIGHT: Filter sensitive data before cloud transmission
```typescript
const sanitized = filterSensitiveContent(body.messages);
const response = await openaiProvider.chat({ messages: sanitized });
```

### WRONG: New httpx client per BackendClient request
```python
async with httpx.AsyncClient(timeout=self.timeout) as client:
    response = await client.get(url)
```

### RIGHT: Shared connection pool with retry
```python
response = await self._pool.get(url, timeout=self._timeout_for(endpoint))
# Retry handled by tenacity decorator
```

### WRONG: Fire-and-forget background tasks with no error collection
```python
asyncio.create_task(summarize(thread_id))  # failure silently lost
```

### RIGHT: TaskMonitor wraps background tasks with Prometheus counters
```python
task_monitor.spawn("summarize", summarize(thread_id))
# Failures logged, counted, and exposed via /metrics
```

### WRONG: Calling nonexistent BackendClient method (P0 bug A-2)
```python
response = await client.get(f"/api/deals/{deal_id}/brain")  # .get() doesn't exist
```

### RIGHT: Use existing BackendClient._request() pattern
```python
response = await self._request("GET", f"/api/deals/{deal_id}/brain")
```

### WRONG: System prompt tool count as free text
```markdown
You have 14 tools available.
```

### RIGHT: Machine-verified count injected at build time
```python
tool_count = len(tools)  # derived from registry
system_prompt = template.format(tool_count=tool_count)
```

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Profile injection adds latency to every chat turn (extra HTTP round-trip) | HIGH | MEDIUM | Cache profile in memory/session for 5 min; don't fetch on every turn |
| 2 | Content filtering strips too aggressively — removes legitimate deal discussion from cloud messages | MEDIUM | HIGH | Filter only structured PII (SSN, EIN, CC, phone); leave business context intact |
| 3 | Document upload breaks `make validate-local` via new Redocly ignores (already at 57 ceiling) | HIGH | HIGH | New endpoints must pass Redocly without adding ignores; fix any lint issues |
| 4 | RAG ingest of deal PDFs overwhelms vector DB with large CIMs (100+ pages) | MEDIUM | MEDIUM | Chunk size limit (1000 tokens), max 500 chunks per document, async ingest |
| 5 | Resilience config wiring breaks existing tool calls that worked without retry | MEDIUM | HIGH | Gate P4 verifies all 14 existing tools still work; retry only on 503/429/timeout |
| 6 | XL mission exceeds context window mid-execution | HIGH | MEDIUM | Per IA-1: context checkpoint at Phase 6 midpoint; per IA-7: checkpoint file |
| 7 | Brain facts fix (`_get_deal_brain_facts`) changes recall memory shape, breaking downstream consumers | MEDIUM | HIGH | Keep return type identical; only fix the HTTP call method; verify recall memory output unchanged |
| 8 | SCOPE_TOOL_MAP update misses a tool, causing scope violations at runtime | MEDIUM | MEDIUM | Machine-verify: `len(SCOPE_TOOL_MAP.values_flat()) == len(tools)` assertion in test |
| 9 | TaskMonitor wrapping changes `asyncio.create_task` timing, causing subtle ordering bugs | LOW | HIGH | TaskMonitor delegates to `asyncio.create_task` internally; wrapper only adds logging/counting |
| 10 | Synthetic URL scheme (`dataroom://`) confuses RAG retrieval when used as source reference | MEDIUM | MEDIUM | RAG ingest stores `dataroom://` as source_url; retrieval filters by deal_id, not URL |

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash, run:
1. `git log --oneline -10` — determine last committed phase
2. `make validate-local` — verify codebase state
3. `ls /home/zaks/bookkeeping/mission-checkpoints/SYSTEM-MATURITY-REMEDIATION-001.md` — read progress checkpoint
4. Resume from the next uncommitted phase

## Context Checkpoint
<!-- Adopted from Improvement Area IA-1 -->

At Phase 6 completion: summarize progress, commit intermediate work, write checkpoint to `/home/zaks/bookkeeping/mission-checkpoints/SYSTEM-MATURITY-REMEDIATION-001.md`. If context is constrained, continue in a fresh session from that checkpoint.

## Multi-Session Continuity
<!-- Adopted from Improvement Area IA-7 -->

This is an XL mission. At the end of each session, write a structured checkpoint:
```
/home/zaks/bookkeeping/mission-checkpoints/SYSTEM-MATURITY-REMEDIATION-001.md
```
Contents: phases completed, phases remaining, current validation state, open decisions.

---

## Phase 0 — Discovery & Baseline
**Complexity:** S | **Estimated touch points:** 0 (read-only)

**Purpose:** Verify baseline state, confirm all interview findings are current, identify affected contract surfaces.

### Tasks
- P0-01: **Run `make validate-local`** — capture baseline. Must PASS.
- P0-02: **Verify outdated model lists** — `grep -n 'gpt-3.5\|claude-3-opus\|claude-3-sonnet\|claude-3-haiku' /home/zaks/zakops-agent-api/apps/dashboard/src/lib/settings/provider-settings.ts`
- P0-03: **Verify profile not injected** — confirm no `/api/user/profile` fetch in `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/route.ts`
- P0-04: **Verify DISABLE_LONG_TERM_MEMORY** — confirm `true` in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`
- P0-05: **Verify no document upload endpoint** — `grep -rn 'upload\|multipart' /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
- P0-06: **Verify DealDocuments not wired** — confirm `onUpload` not passed in `DealWorkspace.tsx`
- P0-07: **Verify resilience.py not imported** — `grep -rn 'resilience' /home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py`
- P0-08: **Verify no cost query endpoint** — `grep -rn 'cost\|stats\|metrics' /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/agent.py`
- P0-09: **Identify contract surfaces** — Surfaces 1, 2, 8, 9, 10, 12, 13, 17 affected
- P0-10: **Capture agent tool count** — must be 14 tools, 7 HITL
- P0-11: **Verify broken `_get_deal_brain_facts()`** — In `summarizer.py` ~line 332, confirm it calls `client.get()` which doesn't exist on BackendClient (P0 bug A-2)
- P0-12: **Verify `investment_focus` missing from profile API** — In `preferences.py` ~line 21, confirm `UserProfileResponse` lacks `investment_focus` field despite DB column existing (P0 bug A-3)
- P0-13: **Verify SCOPE_TOOL_MAP gaps** — In `tool_scoping.py`, confirm quarantine tools (`list_quarantine_items`, `add_quarantine_item`, `resolve_quarantine_item`, `bulk_resolve_quarantine`) and delegation tools (`delegate_research`, `delegate_outreach`) are missing from scope maps
- P0-14: **Verify specialist brain empty** — In `graph.py` specialist dispatch, confirm `brain: {}` is passed instead of actual deal brain facts
- P0-15: **Verify HITL success format mismatch** — In `graph.py` `_execute_approved_tools()`, confirm approved tool returns raw string instead of `ToolResult` format matching `_tool_call()` output
- P0-16: **Verify budget enforcement gap** — In `cost_repository.py`, confirm `check_budget()` method exists but is never called before LLM invocations
- P0-17: **Verify fire-and-forget task blindness** — Confirm 5+ `asyncio.create_task()` calls in `graph.py` with no error collection

### Gate P0
- All findings confirmed current (including 3 P0 bugs, SCOPE_TOOL_MAP gaps, specialist brain, budget, task blindness)
- `make validate-local` PASS
- Surface list documented: 1, 2, 8, 9, 10, 12, 13, 17

---

## Phase 1 — Settings Provider UX (Quick Wins)
**Complexity:** S | **Estimated touch points:** 2

**Purpose:** Fix outdated model lists, descriptions, and defaults. Add text-only mode indicator. This is the highest-visibility, lowest-effort fix.

### Blast Radius
- **Services affected:** Dashboard only
- **Pages affected:** Settings page, Chat page (text-only indicator)
- **Downstream consumers:** Provider routing in chat route

### Tasks
- P1-01: **Update Anthropic model list** in `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/settings/provider-settings.ts` lines 212-217:
  - Replace with: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`
  - Add label/description for each model
  - Update default from `claude-3-5-sonnet-20241022` to `claude-sonnet-4-6` (line 64)
- P1-02: **Update OpenAI model list** same file lines 206-210:
  - Replace with: `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `gpt-4o`, `gpt-4o-mini`, `o3`, `o4-mini`
  - Update default from `gpt-4o` to `gpt-4.1` (line 58)
- P1-03: **Update card descriptions** in `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/ProviderSection.tsx` lines 158-159:
  - OpenAI: "GPT-4.1, o3, GPT-4o"
  - Anthropic: "Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5"
- P1-04: **Add text-only mode indicator** — In the Architecture Note section (ProviderSection.tsx ~line 391), add clear note: "Cloud providers (OpenAI, Anthropic, Custom) operate in text-only mode — ZakOps tools (deal transitions, quarantine, delegation) are not available. Switch to Local for full tool access."
- P1-05: **Add "last verified" comment** to model lists for maintainability

### Gate P1
- `npx tsc --noEmit` passes
- Settings page renders with updated model names
- No references to `gpt-3.5`, `claude-3-opus`, `claude-3-sonnet`, or `claude-3-haiku` remain

---

## Phase 2 — User Profile → Agent Integration
**Complexity:** M | **Estimated touch points:** 5

**Purpose:** Connect the user profile (already collected and stored) to the agent, so it knows the operator's name, company, role, investment focus, and timezone.

### Blast Radius
- **Services affected:** Dashboard (chat route), Agent API (system prompt, new tool)
- **Pages affected:** Chat page (agent responses now personalized)
- **Downstream consumers:** All agent conversations

### Tasks
- P2-01: **Add `{user_profile}` section to system prompt** in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/system.md`:
  - Add new section before `{long_term_memory}`:
    ```
    # Operator Profile
    {user_profile}
    ```
  - Include guidance: "Use this profile to personalize responses, filter deal relevance by investment focus, and address the operator by name."
- P2-02: **Pass `user_profile` kwarg in `load_system_prompt()`** — in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/__init__.py`, add `user_profile` parameter with empty string default
- P2-03: **Fetch profile in chat route** — in `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/route.ts`, add `GET ${BACKEND_URL}/api/user/profile` call with 5-second cache (use module-level cache with TTL). Pass profile as `options.user_profile` to agent provider.
- P2-04: **Thread profile through to agent** — in `invoke_with_hitl()` in `graph.py`, read `user_profile` from options/metadata, format it as structured text, pass to `load_system_prompt(user_profile=formatted)`.
  - **Checkpoint:** After P2-04, agent should respond with operator's name when asked "Who am I?"
- P2-05: **Create `get_operator_profile` agent tool** — New tool in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py` (or new file). Calls `BackendClient` to `GET /api/user/profile`. Returns formatted profile. NOT HITL-gated (read-only).
- P2-06: **Add `update_operator_profile` agent tool** — Calls `PATCH /api/onboarding` with profile field updates. HITL-gated (mutation). Allows agent to update profile from conversation ("I now focus on healthcare").
- P2-07: **Register new tools** in `__init__.py`, add `update_operator_profile` to `HITL_TOOLS`
- P2-08: **Add `BackendClient.get_user_profile()` and `BackendClient.update_user_profile()` methods**
- P2-09: **Fix `investment_focus` missing from profile API (P0 bug A-3)** — In `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/routers/preferences.py`:
  - Add `investment_focus: Optional[str] = None` to `UserProfileResponse` model
  - Update SQL query in `get_user_profile()` to include `os.profile_investment_focus` from `onboarding_state` table
  - This field is stored in `onboarding_state.profile_investment_focus` but never returned by the API
- P2-10: **Update SCOPE_TOOL_MAP for new profile tools** — In `tool_scoping.py`, add `get_operator_profile` and `update_operator_profile` to appropriate scope entries. Also add the 6 missing existing tools: `list_quarantine_items`, `add_quarantine_item`, `resolve_quarantine_item`, `bulk_resolve_quarantine`, `delegate_research`, `delegate_outreach`

### Decision Tree
- **IF** backend `/api/user/profile` returns 404 or empty → pass empty profile, agent operates without personalization
- **IF** onboarding not completed → profile fields are null → agent says "I don't have your profile yet. Would you like to set it up?"

### Rollback Plan
1. Revert `system.md`, `__init__.py`, `route.ts`, `graph.py`
2. Remove new tools from `__init__.py` and `HITL_TOOLS`
3. `make validate-local` passes

### Gate P2
- Agent responds to "Who am I?" with operator's name from profile
- Agent responds to "What's my investment focus?" with correct sector (requires P2-09 fix)
- `get_operator_profile` tool works in chat
- `update_operator_profile` requires HITL approval
- `investment_focus` field present in `GET /api/user/profile` response
- SCOPE_TOOL_MAP includes all 16 tools (14 original + 2 new) plus 6 previously missing quarantine/delegation tools
- `npx tsc --noEmit` passes
- Playwright: `npx playwright test chat-profile-integration` passes (P11-02 written early, run here)
- Tool count: 16 (was 14), HITL_TOOLS: 8 (was 7)

---

## Phase 3 — Model Switching & Cloud Safety
**Complexity:** M | **Estimated touch points:** 5

**Purpose:** Harden model switching: persist choice server-side, add graceful degradation UI, filter sensitive content before cloud transmission, implement automatic vLLM failover.

### Blast Radius
- **Services affected:** Dashboard (chat route, chat UI)
- **Pages affected:** Chat page
- **Downstream consumers:** All chat interactions with cloud providers

### Tasks
- P3-01: **Add SQL migration for provider/model persistence** — Add migration to `zakops_agent` database: `ALTER TABLE chat_threads ADD COLUMN provider VARCHAR(50) DEFAULT 'local', ADD COLUMN model VARCHAR(100) DEFAULT NULL;`. In chat route, when provider is selected, store `{ thread_id, provider, model }` via `PATCH /api/v1/threads/{id}`. On thread restore, read stored provider.
- P3-02: **Add server-side content filtering** — Instead of duplicating PII patterns in TypeScript, reuse existing patterns from `apps/agent-api/app/core/security/output_validation.py`. Create `/home/zaks/zakops-agent-api/apps/agent-api/app/core/security/content_filter.py`:
  - Import PII regex patterns from `output_validation.py` (SSN, EIN, CC, phone, email)
  - Add `filter_for_cloud(messages: list[dict]) -> list[dict]` that strips PII and replaces with `[REDACTED]`
  - Add `POST /api/v1/agent/filter` endpoint for dashboard to call before cloud transmission
  - Log filter actions (redaction count) without logging the sensitive data
  - Also add thin TypeScript wrapper in `apps/dashboard/src/lib/agent/content-filter.ts` that calls the server-side endpoint
- P3-03: **Disable proposal cards in cloud mode** — In chat UI, when active provider is not `local`, hide or disable "Approve"/"Reject" buttons on proposal cards. Show "Switch to Local provider for tool actions" tooltip.
- P3-04: **Add text-only mode banner** — When cloud provider is active, show a persistent subtle banner in chat: "Text-only mode — switch to Local for full ZakOps tools"
- P3-05: **Implement automatic vLLM failover** — In chat route, if local agent call fails (connection refused, timeout) AND a cloud provider is configured with valid API key, automatically route to that cloud provider with a warning message prepended: "Local agent unavailable — responding via [Provider]. Tool actions are temporarily disabled."

### Decision Tree
- **IF** local agent fails AND openai key exists → fallback to OpenAI
- **ELSE IF** local agent fails AND anthropic key exists → fallback to Anthropic
- **ELSE IF** local agent fails AND custom endpoint exists → fallback to Custom
- **ELSE** → return error: "Agent unavailable. Please try again or configure a cloud provider in Settings."

### Rollback Plan
1. Revert chat route, chat page, remove content-filter.ts
2. `npx tsc --noEmit` passes

### Gate P3
- `npx tsc --noEmit` passes
- SQL migration applied: `chat_threads` table has `provider` and `model` columns
- Server-side content filter strips SSN/EIN/CC from test message (reuses `output_validation.py` patterns)
- Proposal cards disabled when cloud provider active
- Text-only banner appears when cloud provider selected
- Fallback to cloud works when local is unavailable (manual test: stop agent-api, send chat message)
- Playwright: `npx playwright test chat-profile-integration` passes (text-only banner, proposal card disable)

---

## Phase 4 — Agent Resilience, Bug Fixes & Tool Reliability
**Complexity:** L | **Estimated touch points:** 8

**Purpose:** Fix 3 P0 bugs from 3-Pass Escalation. Wire resilience config, add retry with backoff, connection pooling, chain-of-thought logging, TaskMonitor for background tasks, budget enforcement, specialist brain context, and concurrent approval safety.

### Blast Radius
- **Services affected:** Agent API (BackendClient, graph, summarizer, tool scoping, metrics)
- **Pages affected:** None directly (backend resilience)
- **Downstream consumers:** All agent tool calls, all background tasks, all deal-scoped conversations

### Tasks
- P4-01: **Wire resilience config into BackendClient (pool-first-then-retry)** — In `/home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py`:
  - Import `RESILIENCE_CONFIG` from `resilience.py`
  - **CRITICAL ORDER:** First create shared `httpx.AsyncClient` connection pool (persistent across requests), THEN add retry decorator on top. Current code creates new client per request AND `with_correlation_id()` clones entire client — both must be fixed.
  - Add `tenacity` retry decorator: retry on `httpx.ConnectError`, `httpx.TimeoutException`, HTTP 503, HTTP 429. Max 3 retries, exponential backoff (1s, 2s, 4s). No retry on 4xx (client errors).
  - Use per-endpoint timeout from resilience config instead of single 30s scalar
- P4-02: **Fix `_get_deal_brain_facts()` broken method call (P0 bug A-2)** — In `/home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py` ~line 332:
  - Current code calls `client.get(f"/api/deals/{deal_id}/brain")` but BackendClient has no `.get()` method
  - The `except AttributeError` silently catches this, so deal brain facts NEVER load into recall memory
  - Fix: use `BackendClient._request("GET", ...)` or add a dedicated `get_deal_brain(deal_id)` method
  - After fix, verify `build_recall_memory()` includes brain facts in output
- P4-03: **Fix HITL tool result format (P0 adjacent)** — In `graph.py` `_execute_approved_tools()` (~line 922):
  - Change raw string error to `ToolResult.error_result()` pattern matching `_tool_call()` output
  - Also fix success path: ensure approved tool results use same `ToolResult` format as direct tool calls
- P4-04: **Fix specialist brain context (P1)** — In `graph.py` specialist dispatch:
  - Currently passes `brain: {}` (empty dict) to specialist agents instead of actual deal brain facts
  - Fix: pass `brain_facts` from recall memory (already available in the parent graph state) to specialist context
- P4-05: **Wire budget enforcement** — In `graph.py`, before LLM invocation:
  - Call `cost_repository.check_budget()` (method already exists but is never called)
  - If budget exceeded, return early with message: "Budget limit reached. Please contact administrator."
  - Add `MONTHLY_BUDGET_USD` env var (default: 100.0)
- P4-06: **Add TaskMonitor for background tasks** — Create `/home/zaks/zakops-agent-api/apps/agent-api/app/core/task_monitor.py`:
  - Wraps `asyncio.create_task()` with error logging, Prometheus counter (`agent_background_tasks_total{status=success|error}`), and task reference tracking
  - Replace all 5+ bare `asyncio.create_task()` calls in `graph.py` with `task_monitor.spawn(name, coro)`
  - Add `GET /api/v1/agent/tasks/health` endpoint returning active/completed/failed counts
- P4-07: **Add chain-of-thought logging** — In `decision_ledger` write (graph.py lines 715-738), add `reasoning` field capturing the LLM's chain-of-thought text for tool selection. Add column to `decision_ledger` table if not present.
- P4-08: **Add optimistic locking to deal transitions** — In `transition_deal` tool, add `expected_version` parameter (matching the quarantine pattern from CHAT-CONTROL-SURFACE-001). Prevents concurrent approve race condition.
- P4-09: **Add summary pruning** — In `summarizer.py`, add `prune_old_summaries(thread_id, keep_latest=5)` that deletes summaries older than the 5 most recent versions. Call after each new summary write.
- P4-10: **Add task decomposition via system prompt** — In `system.md`, add a "Complex Query Decomposition" section:
  - Instruct the agent: "For multi-step queries, first outline the steps needed, then execute each step sequentially using tools."
  - Add structured format: "PLAN: 1. [step] 2. [step] → EXECUTE: [tool calls]"
  - This is a prompt-based approach (not a graph restructure) that enables multi-step reasoning within the existing graph topology.
- P4-11: **Add stage-aware tool recommendations** — In `tool_scoping.py`, add `get_stage_recommendations(stage)` that returns which tools are most relevant per deal stage. Inject into system prompt context when a deal is scoped. Doesn't block tools (no breaking changes) but strongly guides the agent.
  - `inbound/screening`: `search_deals`, `get_deal`, `delegate_research`, `list_quarantine_items`
  - `qualified/loi`: `get_deal_health`, `add_note`, `list_deal_documents`, `analyze_document`
  - `diligence/closing`: `search_deal_documents`, `analyze_document`, `transition_deal`
- P4-12: **Add concurrent request queueing** — Semaphore-based concurrency limiter for `invoke_with_hitl()`. Max concurrent invocations: `MAX_CONCURRENT_AGENT_INVOCATIONS` env var (default: 3). Queue beyond limit with 30s timeout. Prevents GPU contention on vLLM.
- P4-13: **Machine-verify tool count in system prompt** — Replace hardcoded "14 tools" text in `system.md` with `{tool_count}` placeholder. Inject actual count from tool registry in `load_system_prompt()`. Add assertion in tool registration: `assert len(tools) == len(SCOPE_TOOL_MAP.all_tools())`.

### Rollback Plan
1. Revert `backend_client.py`, `graph.py`, `summarizer.py`, `tool_scoping.py`, `system.md`, `task_monitor.py`
2. `make validate-local` passes
3. Verify all 16 tools still work (14 original + 2 from P2)

### Gate P4
- `_get_deal_brain_facts()` returns actual brain facts (not empty due to AttributeError)
- Recall memory includes brain facts when deal is scoped
- HITL approved tool results match `ToolResult` format
- Specialist agents receive non-empty `brain` context for deal-scoped requests
- Budget check runs before each LLM invocation
- TaskMonitor wraps all background tasks; `GET /api/v1/agent/tasks/health` returns counts
- BackendClient uses shared connection pool with retry (pool-first-then-retry order)
- Retry works on transient 503 (test with backend temporarily stopped)
- All 16 tools still function correctly
- Decision ledger records tool selection reasoning
- Summary pruning keeps only 5 most recent per thread
- System prompt includes task decomposition instructions and machine-verified tool count
- Stage-aware tool recommendations appear in deal-scoped conversations
- Concurrent request limiter active (configurable via env)
- Agent API health: `curl localhost:8095/health` returns healthy

---

## Phase 5 — Document Upload Backend API
**Complexity:** M | **Estimated touch points:** 3

**Purpose:** Add multipart file upload, listing, download, and delete endpoints for deal artifacts. Text extraction for PDFs.

### Blast Radius
- **Services affected:** Backend API
- **Pages affected:** None yet (wired in P6)
- **Downstream consumers:** Dashboard (P6), Agent tools (P7), RAG ingest (P7)

### Tasks
- P5-01: **Add `POST /api/deals/{deal_id}/artifacts`** — Multipart upload endpoint in backend main.py. Accepts file + metadata (category, description). Uses `get_artifact_store().put()` to store. Writes row to `zakops.artifacts` table. Returns artifact metadata with ID.
  - Categories: `nda`, `cim`, `financials`, `operations`, `legal`, `analysis`, `correspondence`, `loi`, `closing`, `other`
  - Max file size: 50MB (configurable via env)
  - Supported types: PDF, DOCX, XLSX, CSV, TXT, MD, images
- P5-02: **Add `GET /api/deals/{deal_id}/artifacts`** — List artifacts for a deal. Query `zakops.artifacts WHERE deal_id=$1`. Return array with metadata.
- P5-03: **Add `GET /api/deals/{deal_id}/artifacts/{artifact_id}`** — Download/stream single artifact via `get_artifact_store().get_stream()`.
- P5-04: **Add `DELETE /api/deals/{deal_id}/artifacts/{artifact_id}`** — Delete from store + DB. Soft-delete pattern (set `deleted_at`, don't remove file immediately).
- P5-05: **Add text extraction** — For PDF uploads, use `pypdf` (already a common Python PDF library; add to requirements if not present) to extract text. Store in `artifacts.extracted_text`. For DOCX, use `python-docx`. For other text-based files, read directly.
- P5-06: **Add RAG ingest on upload with synthetic URL scheme** — After text extraction, POST extracted text to `POST http://localhost:8052/rag/add` with `deal_id` scoping. Use synthetic URL: `dataroom://{deal_id}/artifacts/{artifact_id}` (RAG's `url` field is mandatory). Chunk into 1000-token segments. Max 500 chunks per document. Async ingest via TaskMonitor (P4-06).
- P5-07: **Add access logging** — Log each artifact access (upload, download, delete) to a new `artifact_access_log` table: `artifact_id`, `action` (upload/download/delete), `actor`, `timestamp`, `ip_address`.
- P5-08: **Add document versioning** — Add `version_number` (default 1) and `previous_artifact_id` (nullable FK to self) columns to `zakops.artifacts` table via new migration. On upload of a file with the same `(deal_id, filename, category)` as an existing artifact: increment version, link via `previous_artifact_id`. The list endpoint returns only the latest version by default, with `?include_versions=true` param to show history.
- P5-09: **Verify dependencies** — Ensure `pypdf` and `python-docx` are in backend `requirements.txt`. If not present, add them. Do NOT add new Redocly ignores — new endpoints must pass Redocly lint clean (ceiling at 57).
- P5-10: **Run `make update-spec && make sync-all-types`** — Sync new endpoints to generated types. Run per-endpoint Redocly validation: `npx @redocly/cli lint packages/contracts/openapi/zakops-api.json` must pass without new ignores.

### Decision Tree
- **IF** file is PDF → extract text with pypdf → ingest to RAG
- **ELSE IF** file is DOCX → extract text with python-docx → ingest to RAG
- **ELSE IF** file is text-based (TXT, MD, CSV) → read directly → ingest to RAG
- **ELSE** (images, XLSX, binary) → store artifact, skip text extraction/RAG ingest

### Rollback Plan
1. Revert `main.py`, remove new migration file
2. `make validate-local` passes

### Gate P5
- `curl -X POST localhost:8091/api/deals/DL-TEST/artifacts -F 'file=@test.pdf'` returns 200 with artifact ID
- `curl localhost:8091/api/deals/DL-TEST/artifacts` returns list including uploaded file
- `curl localhost:8091/api/deals/DL-TEST/artifacts/{id}` streams file back
- `curl -X DELETE localhost:8091/api/deals/DL-TEST/artifacts/{id}` returns 200
- Text extraction populates `extracted_text` column for PDF uploads
- RAG ingest uses synthetic URL `dataroom://DL-TEST/artifacts/{id}`
- Document versioning: re-upload same filename increments `version_number`
- `make update-spec && make sync-all-types && npx tsc --noEmit` — PASS
- Redocly lint passes with NO new ignores (still at 57 ceiling)
- `make validate-local` PASS

---

## Phase 6 — Dashboard Materials Panel Wiring
**Complexity:** M | **Estimated touch points:** 4

**Purpose:** Wire the existing `DealDocuments.tsx` component to real data via the **actual** deal page at `/deals/[id]/page.tsx` (NOT the dead `DealWorkspace.tsx` which is never rendered by any route — P0 bug A-1). Enable upload, download, delete, share, and export.

### Blast Radius
- **Services affected:** Dashboard, Backend (share/export endpoints)
- **Pages affected:** `/deals/[id]/page.tsx` (the ACTUAL deal page, 2000+ lines)
- **Downstream consumers:** Operators managing deal documents

### Critical Note (P0 Bug A-1)
`DealWorkspace.tsx` is a DEAD component — no route ever renders it. The actual deal detail page is `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` which has its own tab system including a Materials/Documents tab. ALL wiring in this phase targets that page, NOT DealWorkspace.tsx.

### Tasks
- P6-01: **Add API client functions** — In `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (or new `deal-artifacts.ts` file), add:
  - `fetchDealArtifacts(dealId)` → `GET /api/deals/{id}/artifacts`
  - `uploadDealArtifact(dealId, file, metadata)` → `POST /api/deals/{id}/artifacts` (multipart)
  - `downloadDealArtifact(dealId, artifactId)` → `GET /api/deals/{id}/artifacts/{id}`
  - `deleteDealArtifact(dealId, artifactId)` → `DELETE /api/deals/{id}/artifacts/{id}`
  - `shareDealArtifact(dealId, artifactId)` → `POST /api/deals/{id}/artifacts/{id}/share`
  - `exportDealArtifacts(dealId)` → `POST /api/deals/{id}/artifacts/export`
- P6-02: **Wire documents into `/deals/[id]/page.tsx`** — In the actual deal page:
  - Add `fetchDealArtifacts(dealId)` to the existing `Promise.allSettled` data-fetching block (mandatory pattern per DEAL-INTEGRITY-UNIFIED-001)
  - Pass fetched artifacts to the Documents/Materials tab content
  - Import and render `DealDocuments.tsx` in the Documents tab with real data props
- P6-03: **Wire upload handler** — Pass `onUpload` to `DealDocuments` that calls `uploadDealArtifact()` and refreshes the data. Show toast on success/failure. Reuse existing `file-uploader.tsx` component.
- P6-04: **Wire download handler** — Pass `onDownload` that opens artifact download URL in new tab or triggers browser download.
- P6-05: **Wire delete handler** — Pass `onDelete` that calls `deleteDealArtifact()` with confirmation dialog. HITL-like pattern: "Delete {filename}? This cannot be undone."
- P6-06: **Map backend artifact type to DealDocument type** — Ensure the API response shape maps to the existing `DealDocument` interface in `DealDocuments.tsx`. Import from generated types where possible.
- P6-07: **Add document sharing via secure links** — Add `POST /api/deals/{deal_id}/artifacts/{artifact_id}/share` backend endpoint that generates a time-limited (24h default) presigned URL. For local storage: generate a signed token URL served by the backend. Display "Copy Link" button on each document in `DealDocuments.tsx`.
- P6-08: **Add document export bundle** — Add `POST /api/deals/{deal_id}/artifacts/export` backend endpoint that creates a ZIP archive of all (or selected) deal artifacts. Returns a download URL. Add "Export All" button to `DealDocuments.tsx` toolbar.
- P6-09: **Run `make update-spec && make sync-all-types`** — Sync share/export endpoints

**Context Checkpoint:** At Phase 6 completion, write progress checkpoint to `/home/zaks/bookkeeping/mission-checkpoints/SYSTEM-MATURITY-REMEDIATION-001.md` per IA-1/IA-7. Summarize: phases completed, remaining, validation state, open decisions. If context is constrained, continue in fresh session from that checkpoint.

### Rollback Plan
1. Revert API client, `/deals/[id]/page.tsx` changes, DealDocuments wiring
2. `npx tsc --noEmit` passes

### Gate P6
- Deal page (`/deals/{id}`) Documents tab shows uploaded files (verify in BROWSER, not just curl)
- Upload via drag-and-drop works with progress indicator
- Download streams file to browser
- Delete removes file with confirmation
- Share generates time-limited URL, "Copy Link" button works
- Export bundles all artifacts into ZIP download
- Empty state shows "No documents yet" message
- `npx tsc --noEmit` passes
- Playwright: `npx playwright test deal-materials-upload` passes
- Context checkpoint file written

---

## Phase 7 — Deal Document RAG, Email Intelligence & Agent Tools
**Complexity:** L | **Estimated touch points:** 6

**Purpose:** Enable the agent to search/analyze deal documents via RAG, access email thread context linked to deals, and perform cross-deal entity lookups. This phase closes the "email threads linked to deals but invisible to agent" gap from Pass 2.

### Blast Radius
- **Services affected:** Agent API (new tools, BackendClient methods, RAG client)
- **Pages affected:** Chat page (agent can now reference deal documents and email threads)
- **Downstream consumers:** All deal-scoped conversations

### Tasks
- P7-01: **Add BackendClient methods for artifacts** — In `backend_client.py`:
  - `list_deal_artifacts(deal_id)` → `GET /api/deals/{deal_id}/artifacts`
  - `get_artifact_text(deal_id, artifact_id)` → `GET /api/deals/{deal_id}/artifacts/{artifact_id}` (text content from `extracted_text`)
  - `get_deal_email_threads(deal_id)` → `GET /api/email-triage/threads?deal_id={deal_id}` (email threads linked to deal)
  - `search_entities(query)` → `GET /api/deals?search={query}` (cross-deal entity lookup by broker name, company, etc.)
- P7-02: **Add RAG client to agent** — Create `/home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_client.py`:
  - `query_deal_documents(deal_id, query, match_count=5)` → `POST http://localhost:8052/rag/query` with `deal_id` filter
  - Reuse existing RAG URL from config/env
- P7-03: **Create `list_deal_documents` tool** — Lists artifacts for a deal. Calls `BackendClient.list_deal_artifacts()`. Returns formatted list with filename, category, upload date, size. NOT HITL-gated.
- P7-04: **Create `search_deal_documents` tool** — Semantic search over deal document content. Calls `rag_client.query_deal_documents()`. Returns relevant chunks with source filenames. NOT HITL-gated.
- P7-05: **Create `analyze_document` tool** — Fetches artifact text, sends to LLM with analysis prompt (summarize, extract key terms, identify risks). Parameters: `deal_id`, `artifact_id`, `analysis_type` (summary|risks|financials|key_terms). NOT HITL-gated (read-only analysis).
- P7-06: **Create `get_deal_email_threads` tool** — Returns email threads linked to a deal from the email triage system. Shows subject, sender, date, triage status, confidence. Enables agent to say "There are 3 email threads about this deal, the latest from broker@firm.com." NOT HITL-gated (read-only).
- P7-07: **Create `lookup_entity` tool** — Cross-deal entity search. Given a broker name, company, or keyword, returns deals associated with that entity. Enables agent to answer "What other deals involve John Smith?" NOT HITL-gated (read-only).
- P7-08: **Register 5 new tools** in `__init__.py`. Update `SCOPE_TOOL_MAP` in `tool_scoping.py`. Update tool count placeholder in `system.md`.
- P7-09: **Rebuild agent-api container** — `COMPOSE_PROJECT_NAME=zakops docker compose build agent-api && docker compose up -d agent-api --no-deps`

### Rollback Plan
1. Remove new tool files, revert `__init__.py`, remove `rag_client.py`
2. Rebuild agent-api container

### Gate P7
- Agent API healthy with 21 tools (14 original + 2 profile + 5 document/email/entity), 8 HITL
- "List documents for deal DL-0001" → agent calls `list_deal_documents`
- "Search deal documents for revenue" → agent calls `search_deal_documents`, returns relevant chunks
- "Show email threads for this deal" → agent calls `get_deal_email_threads`
- "What other deals involve [broker name]?" → agent calls `lookup_entity`
- `SCOPE_TOOL_MAP` includes all 21 tools
- `curl localhost:8095/health` returns healthy

---

## Phase 8 — Cross-Session Memory & Data Lifecycle
**Complexity:** M | **Estimated touch points:** 3

**Purpose:** Upgrade tiered memory: LLM-backed summarization, summary pruning, thread cascade on deal deletion, retention policy.

### Blast Radius
- **Services affected:** Agent API (summarizer), Backend (cascade)
- **Pages affected:** None directly
- **Downstream consumers:** All agent conversations (improved recall quality)

### Tasks
- P8-01: **Upgrade extractive summarizer with optional LLM path** — In `summarizer.py`, add `abstractive_summarize()` that uses the local vLLM (Qwen 2.5) to generate a concise summary. Keep extractive as fallback. Switch based on `USE_LLM_SUMMARIZATION` env var (default: `true` for quality, `false` for speed).
  - Extractive: current deterministic path (no LLM, keyword-based)
  - Abstractive: send last N unsummarized messages to local LLM with "Summarize this conversation, extracting key facts, decisions, and open questions" prompt
- P8-02: **Add retention policy** — In `summarizer.py`, add `enforce_retention(thread_id, max_age_days=90)`:
  - Archive turn snapshots older than 90 days (move to `turn_snapshots_archive` table or mark as archived)
  - Prune cost_ledger entries older than 365 days
  - This runs as fire-and-forget after each summary write
- P8-03: **Add deal deletion → thread cascade via HTTP** — `zakops` (backend) and `zakops_agent` (agent) are separate PostgreSQL databases with no FK relationship. No triggers, no shared connection. Cascade must use HTTP:
  - In backend's deal archive/delete flow, POST to `http://localhost:8095/api/v1/threads/archive` with `{ deal_id }` body
  - Agent-api receives this and marks associated `chat_threads` as `archived` (set `archived_at` timestamp)
  - Do NOT hard-delete (legal hold may apply)
  - Fire-and-forget via TaskMonitor; log failures but don't block deal deletion
- P8-04: **Fix stale `LONG_TERM_MEMORY_MODEL` config** — In agent config, change `"gpt-5-nano"` to `"gpt-4o-mini"` (or reference local model). This doesn't re-enable mem0, but fixes the config so it won't crash if someone flips the flag later.
- P8-05: **Add memory backfill utility** — Create `/home/zaks/zakops-agent-api/apps/agent-api/app/services/memory_backfill.py`:
  - Script that reads existing `chat_messages` for threads that have no `session_summaries` entry
  - Runs extractive (or abstractive if enabled) summarization on historical messages
  - Creates `session_summaries` entries for those threads
  - Callable as `python -m app.services.memory_backfill --dry-run` for preview, without flag for execution
  - This provides cross-session context for existing conversations that pre-date the summarizer
- P8-06: **Add unified agent knowledge endpoint** — `GET /api/v1/agent/knowledge/{thread_id}`:
  - Returns a single JSON view combining: current LangGraph checkpoint state, latest session summary (facts, decisions, open questions), deal brain facts (if deal-scoped), user profile, tool call history from decision ledger
  - This is the "single source of truth for what the agent knows right now" (interview Q7)
  - Read-only, for debugging and operator visibility

### Rollback Plan
1. Revert `summarizer.py`, backend cascade changes
2. Agent-api restart

### Gate P8
- New summary after 5 turns is abstractive (LLM-generated) when `USE_LLM_SUMMARIZATION=true`
- Summary pruning keeps only 5 most recent per thread (from P4-09) + retention enforced
- Deal archive triggers HTTP cascade to agent-api, marking threads as archived
- `LONG_TERM_MEMORY_MODEL` is a valid model ID
- Memory backfill: `python -m app.services.memory_backfill --dry-run` lists un-summarized threads
- `GET /api/v1/agent/knowledge/{thread_id}` returns combined state (checkpoint + summary + brain + profile + decisions)
- Agent API healthy

---

## Phase 9 — Observability & Monitoring
**Complexity:** M | **Estimated touch points:** 5

**Purpose:** Expose cost/metrics data via API, wire Prometheus middleware, add dashboard analytics components.

### Blast Radius
- **Services affected:** Agent API (new endpoints), Dashboard (new page)
- **Pages affected:** New analytics/observability page
- **Downstream consumers:** Operator visibility into agent behavior

### Tasks
- P9-01: **Wire Prometheus middleware** — In agent-api startup, add middleware that increments `http_requests_total` and records `http_request_duration_seconds` for every request. The metrics are already defined in `metrics.py`; they just need middleware wiring. Add agent-specific dimensions: `agent_tool_calls_total{tool_name}`, `agent_background_tasks_total{status}` (from TaskMonitor P4-06).
- P9-02: **Add cost/stats endpoint with global monthly aggregate** — `GET /api/v1/agent/stats`:
  - `today_cost_usd`, `month_cost_usd`, `total_cost_usd`, `total_threads`, `total_messages`
  - `top_tools` (by usage count), `avg_latency_ms`
  - `background_tasks` (active/completed/failed from TaskMonitor)
  - Queries `cost_ledger` and `decision_ledger`
  - Global monthly aggregate: `SUM(cost_usd) WHERE created_at >= date_trunc('month', now())`
- P9-03: **Add decision log endpoint** — `GET /api/v1/agent/decisions?thread_id=X`:
  - Returns decision_ledger entries for a thread: tool_name, tool_args, success, reasoning, timestamp
  - Paginated, most recent first
- P9-04: **Add turn replay endpoint** — `GET /api/v1/agent/turns/{thread_id}/{turn_number}`:
  - Returns full turn snapshot: system_prompt, messages, model, temperature, completion, tokens
  - For debugging tool selection and agent behavior
- P9-05: **Add proactive urgency alerts endpoint** — `GET /api/v1/agent/alerts`:
  - Combines stall_predictor + anomaly_detector + momentum_calculator signals (if available in brain)
  - Returns deals with urgency indicators: stalled deals (no activity > N days), momentum drops, approaching deadlines
  - If stall/anomaly/momentum modules don't exist yet, build from brain facts: deals with `stall_probability > 0.5` or no transitions in 14 days
- P9-06: **Add conviction score endpoint** — `GET /api/v1/agent/conviction/{deal_id}`:
  - Composite metric (0-100) aggregating: brain facts count, risk count, blind spots, ghost knowledge indicators, stall probability, document coverage (artifacts count vs expected for stage)
  - Returns breakdown: `{ score, components: { brain_facts, risks, blind_spots, documents, stall_risk } }`
- P9-07: **Add dashboard observability page** — Create `/home/zaks/zakops-agent-api/apps/dashboard/src/app/analytics/page.tsx`:
  - Cards: Today's Cost, Monthly Cost, Total Conversations, Avg Latency, Background Task Health
  - Table: Recent tool executions from decision log
  - Section: Urgency alerts (deals needing attention)
  - Per Surface 9 design system compliance
- P9-08: **Add nav link** — Add "Analytics" to dashboard sidebar navigation

### Rollback Plan
1. Remove new endpoints, dashboard page, nav link
2. `npx tsc --noEmit` passes

### Gate P9
- `curl localhost:8095/api/v1/agent/stats` returns cost/metrics JSON with monthly aggregate
- `curl localhost:8095/api/v1/agent/decisions?thread_id=X` returns decision log with reasoning field
- `curl localhost:8095/api/v1/agent/alerts` returns urgency alerts
- `curl localhost:8095/api/v1/agent/conviction/{deal_id}` returns conviction score breakdown
- Analytics page renders with cost cards, tool execution table, and urgency section
- Prometheus `/metrics` endpoint includes agent-specific dimensions
- `npx tsc --noEmit` passes
- Playwright: `npx playwright test analytics-observability` passes

---

## Phase 10 — Onboarding Intelligence
**Complexity:** M | **Estimated touch points:** 3

**Purpose:** Enable incremental profile enrichment from deal interactions and chat conversations.

### Blast Radius
- **Services affected:** Agent API (profile enrichment), Backend (profile update)
- **Pages affected:** None directly
- **Downstream consumers:** Agent personalization quality

### Tasks
- P10-01: **Add profile enrichment service** — Create `/home/zaks/zakops-agent-api/apps/agent-api/app/services/profile_enricher.py`:
  - After each conversation turn, analyze tool calls for sector signals (deal names, industries mentioned, stages worked)
  - Track: `sectors_engaged` (count per sector), `stages_active` (which pipeline stages the operator works in most)
  - Store as JSONB in `user_preferences.metadata` field (add if not present) or a new `profile_insights` table
  - Run as fire-and-forget (like summarizer)
- P10-02: **Add profile insights to agent context** — When building user profile for system prompt (P2 integration), append `profile_insights` data: "Based on your activity: You frequently work with SaaS deals in screening/qualified stages."
- P10-03: **Add onboarding interview tool** — New agent tool `interview_user` that asks structured questions to fill missing profile fields. Triggers when profile has null fields and conversation is in global scope. NOT HITL-gated (it's asking questions, not taking actions). Responses are stored via `update_operator_profile` (P2-06).
- P10-04: **Register new tool** in `__init__.py`. Update `SCOPE_TOOL_MAP`. Now 22 tools total (14 original + 2 profile + 5 document/email/entity + 1 interview).

### Rollback Plan
1. Remove `profile_enricher.py`, revert `__init__.py`
2. Agent-api restart

### Gate P10
- After several deal-scoped conversations, profile insights include sector data
- Agent can answer "What sectors do I work with most?" from enriched profile
- `interview_user` tool triggers for users with incomplete profiles
- 22 tools total, 8 HITL
- `SCOPE_TOOL_MAP` includes all 22 tools (machine-verified assertion from P4-13)

---

## Phase 11 — Playwright E2E & Final Validation
**Complexity:** M | **Estimated touch points:** 5+

**Purpose:** Comprehensive Playwright E2E tests for all new features. Tests are written early (during their respective phases) and run here as the final gate. Final validation across all surfaces.
<!-- Adopted from Improvement Area IA-10: Test naming with functional keywords -->

### Blast Radius
- **Services affected:** None (tests only)
- **Pages affected:** Tests verify all affected pages
- **Downstream consumers:** QA verification

### Per-Phase Playwright Integration
Tests are WRITTEN in this phase but REFERENCED in earlier phase gates. Each phase gate includes a Playwright run for its specific test file. Phase 11 runs the FULL suite as the final gate.

### Tasks
- P11-01: **Settings provider model tests** — New test file `tests/e2e/settings-provider-models.spec.ts`:
  - Test: "settings page shows current Anthropic models" — verify `Claude Opus 4.6` appears
  - Test: "settings page shows current OpenAI models" — verify `GPT-4.1` appears
  - Test: "settings text-only mode note visible" — verify architecture note mentions text-only
  - Test: "settings page has no stale model references" — grep for gpt-3.5, claude-3-opus etc
  - Functional keywords: `settings`, `provider`, `model`, `anthropic`, `openai`
- P11-02: **Chat profile & cloud mode tests** — New test file `tests/e2e/chat-profile-integration.spec.ts`:
  - Test: "chat shows operator context" — verify agent can access profile
  - Test: "chat text-only banner with cloud provider" — verify banner appears when non-local selected
  - Test: "chat proposal cards disabled in cloud mode" — verify approve/reject buttons hidden
  - Test: "chat content filter redacts PII" — verify SSN/EIN patterns filtered
  - Functional keywords: `chat`, `profile`, `operator`, `banner`, `cloud`, `filter`
- P11-03: **Deal materials tests** — New test file `tests/e2e/deal-materials-upload.spec.ts`:
  - Test: "deal page documents tab renders" — verify Documents tab in `/deals/[id]` page (NOT DealWorkspace)
  - Test: "deal documents shows uploaded files" — verify file list renders
  - Test: "deal documents upload button exists" — verify upload UI present
  - Test: "deal documents share link button exists" — verify share UI
  - Test: "deal documents export all button exists" — verify export UI
  - Functional keywords: `deal`, `documents`, `materials`, `upload`, `share`, `export`
- P11-04: **Analytics page tests** — New test file `tests/e2e/analytics-observability.spec.ts`:
  - Test: "analytics page renders cost cards" — verify today/monthly/total cost display
  - Test: "analytics page shows tool executions" — verify decision log table
  - Test: "analytics page shows urgency alerts section" — verify alerts section
  - Test: "analytics nav link visible in sidebar" — verify navigation
  - Functional keywords: `analytics`, `cost`, `observability`, `tools`, `alerts`
- P11-05: **Run full Playwright suite** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test`
- P11-06: **Rebuild agent-api** — Final rebuild with all changes:
  `COMPOSE_PROJECT_NAME=zakops docker compose build agent-api && docker compose up -d agent-api --no-deps`
- P11-07: **Run `make validate-local`** — Full validation
- P11-08: **Run `npx tsc --noEmit`** — TypeScript clean
- P11-09: **Verify all tool counts** — 22 tools, 8 HITL. Machine-verify: `len(tools) == len(SCOPE_TOOL_MAP.all_tools())` assertion passes.
- P11-10: **Final `make update-spec && make sync-all-types`** — Ensure all specs are current
- P11-11: **Update `/home/zaks/bookkeeping/CHANGES.md`**
- P11-12: **Write completion report** per Section 9b template in MISSION-PROMPT-STANDARD.md v2.4

### Gate P11
- All new Playwright tests pass (settings, chat, deal materials, analytics — 4 test files)
- Full Playwright suite: no new failures (pre-existing failures documented)
- `make validate-local` PASS
- `npx tsc --noEmit` PASS
- Agent API healthy with 22 tools, 8 HITL
- SCOPE_TOOL_MAP covers all 22 tools (machine-verified)
- Redocly lint at ≤57 ignores (no increase)
- CHANGES.md updated
- Completion report written with evidence for every AC

---

## Dependency Graph

```
Phase 0 (Discovery — 17 checks)
    │
    ├──→ Phase 1 (Settings UX) ─────────────────────────────────────┐
    │                                                                │
    ├──→ Phase 2 (Profile + investment_focus fix) ──→ P10 (Onboard) │
    │         │                                                      │
    │         ├──→ Phase 3 (Model Switching + Content Filter)        │
    │         │                                                      │
    ├──→ Phase 4 (Bug Fixes + Resilience + TaskMonitor) ────────────│
    │         │                                                      │
    │         └──→ Phase 9 (Observability — needs TaskMonitor)       │
    │                                                                │
    ├──→ Phase 5 (Document API) ──→ Phase 6 (Materials Panel)       │
    │         │                         │                            │
    │         └──→ Phase 7 (RAG + Email + Entity Tools)              │
    │                                                                │
    ├──→ Phase 8 (Memory + HTTP Cascade) ───────────────────────────│
    │                                                                │
    └─── All phases ──→ Phase 11 (Playwright E2E + Validation) ◄────┘

Dependencies:
  - P1: after P0 (no other deps)
  - P2: after P0 (no other deps)
  - P3: after P2 (profile integration for cloud context)
  - P4: after P0 (no other deps — fixes P0 bugs)
  - P5: after P0 (no other deps)
  - P6: after P5 (backend API must exist) + after P4 (TaskMonitor for async ingest)
  - P7: after P5 (artifacts) + after P4 (BackendClient pool/retry)
  - P8: after P4 (summary pruning, TaskMonitor for cascade)
  - P9: after P4 (TaskMonitor, Prometheus counters)
  - P10: after P2 (profile tools for enrichment)
  - P11: after ALL prior phases

Tool count progression:
  P0: 14 tools, 7 HITL (baseline)
  P2: 16 tools, 8 HITL (+get_operator_profile, +update_operator_profile)
  P7: 21 tools, 8 HITL (+list_deal_documents, +search_deal_documents, +analyze_document, +get_deal_email_threads, +lookup_entity)
  P10: 22 tools, 8 HITL (+interview_user)

Recommended sequential order: P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10 → P11
```

---

## Git Commit Discipline
<!-- Per Cross-Cutting Standard #15 -->

- **Branch:** `feat/system-maturity-remediation-001`
- **Per-phase commits:** `SYSTEM-MATURITY-REMEDIATION-001 P{N}: {description}`
- **Mid-phase checkpoints:** Commit at P5-08 (after spec sync) and P6 completion (context checkpoint)
- **Final commit:** `SYSTEM-MATURITY-REMEDIATION-001: Complete — full-stack gap remediation`

---

## Acceptance Criteria

| AC | Description | Phase |
|----|-------------|-------|
| AC-1 | Settings page shows current model names (Claude Opus 4.6, GPT-4.1) with no stale references | P1 |
| AC-2 | Agent knows operator's name, company, role, investment focus from profile | P2 |
| AC-3 | `get_operator_profile` and `update_operator_profile` tools registered and functional | P2 |
| AC-4 | `investment_focus` field present in `GET /api/user/profile` response (P0 bug A-3 fixed) | P2 |
| AC-5 | SCOPE_TOOL_MAP includes all tools including 6 previously missing quarantine/delegation tools | P2 |
| AC-6 | Server-side content filtering strips PII before cloud transmission (reuses `output_validation.py` patterns) | P3 |
| AC-7 | SQL migration adds `provider`/`model` columns to `chat_threads`; provider persisted per thread | P3 |
| AC-8 | Proposal cards disabled when cloud provider is active; text-only banner visible | P3 |
| AC-9 | Automatic vLLM failover to cloud provider works | P3 |
| AC-10 | `_get_deal_brain_facts()` returns actual brain facts (P0 bug A-2 fixed); recall memory includes them | P4 |
| AC-11 | HITL tool results use `ToolResult` format matching `_tool_call()` output (success + error paths) | P4 |
| AC-12 | Specialist agents receive non-empty `brain` context for deal-scoped requests | P4 |
| AC-13 | Budget enforcement calls `check_budget()` before LLM invocations | P4 |
| AC-14 | TaskMonitor wraps all background tasks; `GET /api/v1/agent/tasks/health` returns counts | P4 |
| AC-15 | BackendClient uses connection pooling with retry/backoff (pool-first-then-retry order) | P4 |
| AC-16 | Decision ledger records chain-of-thought reasoning for tool selections | P4 |
| AC-17 | System prompt includes task decomposition instructions and machine-verified tool count | P4 |
| AC-18 | Stage-aware tool recommendations appear in deal-scoped conversations | P4 |
| AC-19 | Concurrent request limiter active with configurable max invocations | P4 |
| AC-20 | `POST /api/deals/{id}/artifacts` accepts multipart upload with text extraction and RAG ingest via synthetic URL | P5 |
| AC-21 | Document versioning tracks `version_number` and `previous_artifact_id` on re-upload | P5 |
| AC-22 | Deal page (`/deals/{id}`) Documents tab shows uploaded files with upload/download/delete/share/export (NOT dead DealWorkspace) | P6 |
| AC-23 | Agent has `list_deal_documents`, `search_deal_documents`, `analyze_document`, `get_deal_email_threads`, `lookup_entity` tools | P7 |
| AC-24 | LLM-backed summarization active; session summaries pruned to 5 most recent | P8 |
| AC-25 | Deal deletion triggers HTTP cascade to agent-api, archiving associated threads | P8 |
| AC-26 | Memory backfill utility creates summaries for existing un-summarized threads | P8 |
| AC-27 | Unified agent knowledge endpoint returns combined state for a thread | P8 |
| AC-28 | `GET /api/v1/agent/stats` returns cost/metrics with global monthly aggregate; analytics page renders | P9 |
| AC-29 | Proactive urgency alerts endpoint identifies stalled/at-risk deals | P9 |
| AC-30 | Conviction score endpoint returns composite metric with component breakdown | P9 |
| AC-31 | Profile enrichment tracks sector engagement from deal interactions | P10 |
| AC-32 | All new Playwright E2E tests pass with functional keyword naming (4 test files) | P11 |
| AC-33 | `make validate-local` + `npx tsc --noEmit` PASS (no regressions) | P11 |
| AC-34 | 22 tools, 8 HITL, SCOPE_TOOL_MAP machine-verified against tool registry | P11 |
| AC-35 | CHANGES.md updated, completion report written with evidence for every AC | P11 |

---

## Guardrails

1. **No email OAuth** — out of scope. Email setup remains basic form entry.
2. **No multi-user auth middleware** — out of scope. Single-operator design preserved.
3. **No S3 migration** — out of scope. Local storage remains default.
4. **No agent graph restructure** — add tools and config only, no graph topology changes.
5. **No MCP bridge tool changes** — agent accesses backend directly via BackendClient.
6. **Generated files never edited** — per V5PP deny rules. Use `make sync-*` pipeline.
7. **Surface 9 compliance** — per `.claude/rules/design-system.md` for all UI changes.
8. **WSL safety** — CRLF fix on new .sh files, ownership fix on /home/zaks/ files.
9. **Redocly ignore ceiling** — do NOT add new ignores (at 57 limit). New endpoints must pass lint.
10. **RAG REST first** — all document retrieval goes through RAG REST API, not direct pgvector.
11. **Contract surface gates** — `make validate-surface{N}` for affected surfaces in phase gates.
12. **Test naming convention** — per IA-10, Playwright test descriptions include functional keywords (settings, provider, model, chat, profile, deal, documents, analytics).

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify ALL interview findings are still current?"
- [ ] "Does `make validate-local` pass at baseline?"
- [ ] "Did I list all 8 affected contract surfaces?"

### After every code change:
- [ ] "Did I run `make sync-all-types` if I changed an API boundary?"
- [ ] "Am I using `Promise.allSettled` for any new multi-fetch in dashboard?"
- [ ] "Am I reusing existing components (DealDocuments.tsx, file-uploader.tsx) instead of creating new ones?"

### After Phase 6 (Context Checkpoint):
- [ ] "Did I write the progress checkpoint file?"
- [ ] "If context is constrained, can I continue in a fresh session?"

### After Phase 4 (Bug Fixes):
- [ ] "Does `_get_deal_brain_facts()` actually return brain facts now (not silently fail)?"
- [ ] "Do specialist agents receive non-empty `brain` context?"
- [ ] "Does `check_budget()` run before each LLM invocation?"
- [ ] "Are ALL background tasks wrapped in TaskMonitor?"
- [ ] "Does HITL approved tool results match `ToolResult` format?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Do all Playwright test names contain functional keywords?"
- [ ] "Did I create ALL 15 files listed in the Files to Create table?"
- [ ] "Is the completion report written with evidence for every AC (35 total)?"
- [ ] "Are there 22 tools and 8 HITL gates in the agent?"
- [ ] "Does SCOPE_TOOL_MAP machine-verify against the tool registry?"
- [ ] "Does document versioning work on re-upload of same filename?"
- [ ] "Does the unified knowledge endpoint return combined state?"
- [ ] "Does the task decomposition prompt guide multi-step reasoning?"
- [ ] "Is the content filter server-side (reusing output_validation.py patterns)?"
- [ ] "Does the deal page (NOT DealWorkspace) show the Documents tab?"
- [ ] "Does HTTP cascade archive threads when deals are deleted?"
- [ ] "Does the conviction score endpoint return component breakdown?"
- [ ] "Do urgency alerts identify stalled deals?"
- [ ] "Are Redocly ignores still at ≤57 (no increase)?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `apps/dashboard/src/lib/settings/provider-settings.ts` | P1 | Update model lists, defaults |
| `apps/dashboard/src/components/settings/ProviderSection.tsx` | P1 | Update descriptions, add text-only note |
| `apps/agent-api/app/core/prompts/system.md` | P2, P4, P7 | Add `{user_profile}`, `{tool_count}`, task decomposition, tool routing |
| `apps/agent-api/app/core/prompts/__init__.py` | P2, P4 | Add `user_profile` kwarg, inject tool count |
| `apps/dashboard/src/app/api/chat/route.ts` | P2, P3 | Fetch profile, content filter call, failover, provider persistence |
| `apps/agent-api/app/core/langgraph/graph.py` | P2, P4 | Profile threading, brain facts fix, HITL format fix, specialist brain, budget check, TaskMonitor, CoT logging |
| `apps/agent-api/app/core/langgraph/tools/__init__.py` | P2, P7, P10 | Register new tools (8 total new) |
| `apps/agent-api/app/schemas/agent.py` | P2 | Expand HITL_TOOLS |
| `apps/agent-api/app/services/backend_client.py` | P2, P4, P7 | Profile methods, connection pool (pool-first-then-retry), retry, artifact/email/entity methods |
| `apps/backend/src/api/orchestration/main.py` | P5, P6 | New artifact endpoints, share/export endpoints |
| `apps/backend/src/api/orchestration/routers/preferences.py` | P2 | Fix `investment_focus` missing from `UserProfileResponse` + SQL query |
| `apps/dashboard/src/app/deals/[id]/page.tsx` | P6 | Wire DealDocuments with real data (ACTUAL deal page, NOT DealWorkspace) |
| `apps/dashboard/src/components/deal-workspace/DealDocuments.tsx` | P6 | Add share link and export buttons |
| `apps/agent-api/app/services/summarizer.py` | P4, P8 | Fix `_get_deal_brain_facts()` (P0 bug A-2), pruning, LLM summarization |
| `apps/agent-api/app/core/metrics.py` | P9 | Wire middleware, add agent-specific dimensions |
| `apps/agent-api/app/api/v1/agent.py` | P8, P9 | New stats/decisions/turns/alerts/conviction/knowledge/tasks-health endpoints |
| `apps/agent-api/app/core/config.py` | P8 | Fix LONG_TERM_MEMORY_MODEL |
| `apps/dashboard/src/app/chat/page.tsx` | P3 | Text-only banner, proposal card disable |
| `apps/agent-api/app/core/security/tool_scoping.py` | P2, P4, P7, P10 | Add missing tools to SCOPE_TOOL_MAP, stage-aware recommendations |
| `apps/agent-api/app/services/cost_repository.py` | P4 | Wire `check_budget()` call |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `apps/agent-api/app/core/langgraph/tools/profile_tools.py` | P2 | `get_operator_profile`, `update_operator_profile` tools |
| `apps/agent-api/app/core/security/content_filter.py` | P3 | Server-side PII filtering reusing `output_validation.py` patterns |
| `apps/dashboard/src/lib/agent/content-filter.ts` | P3 | Thin TypeScript wrapper calling server-side filter endpoint |
| `apps/agent-api/app/core/task_monitor.py` | P4 | Background task wrapper with Prometheus counters and error logging |
| `apps/agent-api/app/core/langgraph/tools/document_tools.py` | P7 | `list_deal_documents`, `search_deal_documents`, `analyze_document`, `get_deal_email_threads`, `lookup_entity` tools |
| `apps/agent-api/app/services/rag_client.py` | P7 | RAG REST client for deal document queries |
| `apps/dashboard/src/lib/deal-artifacts.ts` | P6 | API client functions for artifact CRUD, share, export |
| `apps/agent-api/app/services/memory_backfill.py` | P8 | Backfill summaries for existing un-summarized threads |
| `apps/agent-api/app/services/profile_enricher.py` | P10 | Incremental profile enrichment from deal interactions |
| `apps/dashboard/src/app/analytics/page.tsx` | P9 | Analytics/observability dashboard page with cost, alerts, conviction |
| `apps/dashboard/tests/e2e/settings-provider-models.spec.ts` | P11 | Settings provider model tests |
| `apps/dashboard/tests/e2e/chat-profile-integration.spec.ts` | P11 | Chat profile & cloud mode tests |
| `apps/dashboard/tests/e2e/deal-materials-upload.spec.ts` | P11 | Deal materials upload/share/export tests |
| `apps/dashboard/tests/e2e/analytics-observability.spec.ts` | P11 | Analytics page & alerts tests |
| `/home/zaks/bookkeeping/mission-checkpoints/SYSTEM-MATURITY-REMEDIATION-001.md` | P6 | Multi-session checkpoint |

### Files to Read (sources of truth — do NOT modify unless noted)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/INTERVIEW-ROUND-2-SYSTEM-MATURITY.md` | Source material — all gaps |
| `/home/zaks/bookkeeping/docs/3-PASS-ESCALATION-REPORT.md` | 3-pass escalation findings — P0 bugs, synergies, differentiation |
| `/home/zaks/bookkeeping/docs/PASS-3-DIFFERENTIATION-ANALYSIS.md` | World-class differentiation analysis |
| `apps/agent-api/app/core/langgraph/tools/deal_tools.py` | Tool pattern reference |
| `apps/agent-api/app/core/langgraph/tools/quarantine_tools.py` | Tool pattern reference (P2 precedent) |
| `apps/agent-api/app/core/resilience.py` | Resilience config to enforce |
| `apps/backend/src/core/storage/` | Storage abstraction reference |
| `apps/dashboard/src/components/deal-workspace/DealDocuments.tsx` | Existing component to wire (do not rebuild) |
| `apps/dashboard/src/components/file-uploader.tsx` | Existing upload component to reuse |
| `apps/dashboard/src/app/deals/[id]/page.tsx` | ACTUAL deal page (2000+ lines) — P6 target |
| `apps/backend/src/api/orchestration/routers/onboarding.py` | Profile endpoint reference |
| `apps/backend/src/api/orchestration/routers/preferences.py` | Preferences endpoint reference (MODIFY for investment_focus fix) |
| `apps/agent-api/app/core/security/output_validation.py` | Existing PII patterns to reuse in server-side content filter |
| `apps/agent-api/app/services/cost_repository.py` | Budget enforcement — `check_budget()` method to wire |
| `apps/agent-api/app/services/summarizer.py` | Broken `_get_deal_brain_facts()` — P0 bug A-2 |
| `/home/zaks/Zaks-llm/src/api/rag_rest_api.py` | RAG API reference for deal-scoped queries |

---

## Completion Report Template

To be filled after execution per Section 9b template in MISSION-PROMPT-STANDARD.md v2.4.

---

## Stop Condition

DONE when all 35 AC are met, all validations pass, all 4 Playwright test files pass, and browser confirms: settings show current models, agent knows operator profile with investment_focus, cloud providers have server-side content filtering with text-only UI, document upload+download+share+export works in deal page (NOT DealWorkspace), agent can search/analyze deal documents via RAG + access email threads + lookup entities, brain facts load correctly into recall memory, specialist agents receive full brain context, budget enforcement is wired, TaskMonitor wraps all background tasks, observability page renders cost/metrics/alerts/conviction, profile enrichment tracks sector engagement, task decomposition instructions guide multi-step queries, stage-aware tool recommendations appear, document versioning tracks re-uploads, memory backfill covers historical threads, unified knowledge endpoint works, HTTP cascade archives threads on deal deletion, and SCOPE_TOOL_MAP machine-verifies all 22 tools.

Do NOT proceed to: email OAuth integration, multi-user auth middleware, S3 migration tooling, MCP bridge modifications, Deal Genome dashboard, or Broker Intelligence dashboard.

---

*End of Mission Prompt — SYSTEM-MATURITY-REMEDIATION-001*
