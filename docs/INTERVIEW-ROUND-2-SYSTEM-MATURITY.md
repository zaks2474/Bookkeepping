# Second Round Interview — System Maturity & User-Facing Intelligence

**Date:** 2026-02-20
**Interviewer:** Zak (Operator / System Owner)
**Respondent:** Claude Opus 4.6 (System Architect / Builder)
**Method:** Full codebase investigation across 4 repos, 5 parallel research agents, evidence-grounded

---

## Preamble

Every answer below is grounded in what is **currently implemented, wired, and verifiably functional** in the codebase today. No speculation. No future intentions presented as current state. Where something is partially implemented, I state exactly what works and what doesn't. Where something doesn't exist, I say so plainly.

---

# 1) Agent Capabilities at First Contact

## Does the ZakOps agent currently have persistent memory?

**YES — Tiered, with one layer intentionally disabled.**

The agent has a **3-tier memory architecture**:

| Tier | Name | Status | Storage | Details |
|------|------|--------|---------|---------|
| 1 | **Working Memory** | ACTIVE | In-process (LangGraph state) | Last 6 messages sent to LLM each turn (`chat_repository.py:417`, `max_messages=6`) |
| 2 | **Recall Memory** | ACTIVE | PostgreSQL (`session_summaries` table) | Rolling extractive summarization every 5 turns. Stores facts, decisions, open questions. Brain facts from `deal_brain` table. Rebuilt on each turn via `build_recall_memory()` in `summarizer.py` |
| 3 | **Long-Term Memory** | DISABLED (by design) | Would use pgvector via mem0 | Code exists in `graph.py:48,130-177` — `AsyncMemory` with pgvector backend. **Disabled** via `DISABLE_LONG_TERM_MEMORY=true` per "Decision Lock" compliance: retrieval must use RAG REST, not pgvector/mem0 directly |

**Bottom line:** The agent remembers within a session (Tier 1+2) but does NOT remember across sessions (Tier 3 disabled). Each new conversation starts fresh, with only deal-specific brain facts available if a deal is scoped.

## Does it have defined skills/modules beyond raw prompting?

**YES — Specialist routing system exists.**

**File:** `apps/agent-api/app/core/langgraph/node_registry.py`

Three specialist nodes are defined and active:
- **FinancialAnalystNode** (lines 67-104) — Financial analysis, metrics, valuation
- **RiskAssessorNode** (lines 107-137) — Risk identification, mitigation strategies
- **DealMemoryExpertNode** (lines 140-150+) — Historical facts, precedents

**Routing mechanism:** Dynamic classification in `graph.py:1210-1228`. Queries are classified at confidence threshold 0.6, and specialist output is injected into recall memory context. The LLM can then incorporate specialist insights into its response.

**Limitation:** Specialist routing is suggestive, not mandatory. The LLM sees specialist output in context but can ignore it.

## Does it have hooks, task management scaffolding, or lifecycle awareness?

**PARTIALLY.**

| Capability | Status | Evidence |
|-----------|--------|----------|
| Deal lifecycle awareness | **FULL** | System prompt defines 9 stages, valid transitions, and stage-aware action recommendations (`system.md:17-99`) |
| Tool routing rules | **FULL** | Explicit routing table in system prompt maps query types to tools (`system.md:79-99`) |
| HITL approval gates | **FULL** | 7 tools require human approval before execution. `interrupt()` in LangGraph pauses graph, stores checkpoint, waits for operator decision. 1-hour timeout (`graph.py:765-821`) |
| Injection guard | **FULL** | 4-layer defense: (1) 15 regex injection patterns at 3 severity levels, (2) tool scope + role control, (3) output validation with PII sanitization, (4) canary token verification |
| Task decomposition | **NOT IMPLEMENTED** | Agent uses sequential tool calls (max 10/turn). No plan-then-execute pattern. No explicit multi-step planning node in the graph |
| Long-horizon assistance | **PARTIAL** | Rolling summarization preserves context across turns within a session. No cross-session continuity beyond deal brain facts |
| Reasoning boundaries | **PARTIAL** | Tool budget limit (10 calls/turn), grounding rules in prompt ("always call tools for fresh data"), but no explicit chain-of-thought enforcement |

## Gap Analysis: Basic LLM Wrapper vs. Structured M&A Co-Pilot

| Capability | Frontier Standard (Claude Code, etc.) | ZakOps Current | Gap |
|-----------|---------------------------------------|----------------|-----|
| **Structured memory layers** | Working + Recall + Long-term | Working + Recall (Long-term disabled) | **Moderate** — code exists, needs re-enabling with RAG integration |
| **Reasoning boundaries** | Explicit planning, tool routing, step-by-step | Tool routing via prompt, no explicit planner | **Significant** — no plan-then-execute graph node |
| **Tool routing logic** | Dynamic, confidence-scored | Rule-based in prompt + specialist routing | **Minor** — functional, not dynamic |
| **Safety and execution guards** | Multi-layer, injection defense, output validation | 4-layer defense, HITL, injection guard, canary tokens | **None** — this is world-class |
| **Task decomposition** | Break complex queries into sub-tasks | Sequential tool calls only | **Significant** — no decomposition capability |
| **Long-horizon assistance** | Cross-session memory, user modeling | Session-only recall, no user modeling | **Significant** — no cross-session continuity |

**Honest verdict:** ZakOps is **well beyond a basic LLM wrapper** — it has specialist routing, 4-layer security, HITL gates, tiered memory, deal lifecycle awareness, and 14 purpose-built tools. But it falls short of a **true co-pilot** in two critical areas: (1) no task decomposition for complex multi-step queries, and (2) no cross-session memory or user profile integration.

---

# 2) Onboarding System — Is It Fully Wired and Operational?

## Do we currently have a fully wired onboarding system?

**YES for data collection. NO for agent integration.**

### What EXISTS and works today:

**6-step onboarding wizard** at `/onboarding`:
1. **Welcome** — Introduction
2. **Your Profile** — Structured data collection (name, company, role, investment focus, timezone)
3. **Connect Email** — Gmail/Outlook provider selection + email entry
4. **Meet Your Agent** — Agent introduction + enablement
5. **Preferences** — Notification settings, quiet hours, approval mode
6. **All Set!** — Completion

**Backend persistence:**
- `zakops.onboarding_state` table (Migration 027) — profile fields + step tracking
- `zakops.user_preferences` table (Migration 026) — agent config, notifications, timezone
- REST APIs: `GET/PATCH /api/onboarding`, `GET /api/user/profile`, `GET/PATCH /api/user/preferences`

**Features that work:**
- Resumable progress (shows "Resume" banner if user returns mid-setup)
- Monotonic step advancement (can't go backward)
- Backend persistence via UPSERT
- Profile reset preserves profile fields

### Profile Schema (as collected today):

| Field | Collected At | Stored In | Used By Agent? |
|-------|-------------|-----------|----------------|
| Name | Step 2 | `onboarding_state.profile_name` | **NO** |
| Company | Step 2 | `onboarding_state.profile_company` | **NO** |
| Role | Step 2 | `onboarding_state.profile_role` | **NO** |
| Investment Focus | Step 2 | `onboarding_state.profile_investment_focus` | **NO** |
| Timezone | Step 5 | `user_preferences.timezone` | **NO** |
| Email Address | Step 3 | `user_preferences.email_config` (JSONB) | **NO** |
| Agent Enabled | Step 4 | `user_preferences.agent_enabled` | Yes (conditional) |
| Approval Mode | Step 5 | `user_preferences.auto_approve_level` | **NO** |

### The Critical Gap: Profile is NEVER passed to the agent

The system prompt has a placeholder:
```markdown
# What you know about the user
{long_term_memory}
```

But `{long_term_memory}` is populated from **mem0 memory store** (which is disabled), NOT from the user profile. The agent does not know the operator's name, company, role, investment focus, or timezone.

**Your HVAC scenario:** If a user's profile says "Investment Focus: Manufacturing" and they say "Search for deals," the agent would NOT recognize their preference. It would treat the query generically. The profile data exists in the database but is never read by the agent.

### What must be built for world-class onboarding:

| # | Gap | What to Build | Complexity |
|---|-----|---------------|------------|
| 1 | **Profile injection into agent context** | Chat route fetches `/api/user/profile` before each agent call, injects into system prompt or `long_term_memory` | S |
| 2 | **Agent tool for profile access** | `get_operator_profile` tool so agent can self-retrieve context | S |
| 3 | **Incremental profile building** | Backend job that analyzes deal interactions (sectors viewed, stages worked, brokers contacted) and enriches profile | M |
| 4 | **Investment focus integration** | Agent uses investment_focus to filter deal recommendations and contextualize search queries | S |
| 5 | **Profile update from chat** | Agent can update profile fields via conversation ("I now focus on healthcare") | M |
| 6 | **Email OAuth integration** | Replace basic email entry with real Gmail/Outlook OAuth flow | L |
| 7 | **Onboarding interview mode** | Agent actively interviews new users in chat, collecting structured profile data incrementally | M |

**Architecture status:** Scaffolding complete (DB tables, API endpoints, UI wizard). Integration incomplete (agent doesn't use the data).

---

# 3) Deal Documents & Raw Data Architecture

## Where are deal documents stored?

**Local filesystem with a storage abstraction layer.**

### Physical Storage

**Location:** `/home/zaks/DataRoom/`

```
DataRoom/
├── 00-PIPELINE/
│   └── _INBOX_QUARANTINE/          ← Email triage staging
│       └── {message_id}/
│           ├── email.json
│           ├── email_body.txt
│           ├── triage_summary.json
│           └── triage_summary.md
├── 01-ACTIVE-DEALS/
│   └── {DealName}-{Year}/
│       ├── 01-NDA/
│       ├── 02-CIM/
│       ├── 03-Financials/
│       ├── 04-Operations/
│       ├── 05-Legal/
│       ├── 06-Analysis/
│       ├── 07-Correspondence/      ← Email bundles with attachments
│       ├── 08-LOI-Offer/
│       └── 09-Closing/
```

### Storage Abstraction Layer

**Location:** `apps/backend/src/core/storage/`

| Backend | Status | Details |
|---------|--------|---------|
| **Local (DEFAULT)** | ACTIVE | Reads/writes to `/home/zaks/DataRoom`. Supports `put()`, `get()`, `delete()`, `exists()`, `list()`, `get_metadata()` |
| **S3 (OPT-IN)** | IMPLEMENTED, NOT ENABLED | Full S3-compatible backend with presigned URLs. Requires `ARTIFACT_STORAGE_BACKEND=s3` + AWS credentials |
| **Factory** | ACTIVE | Smart backend selection via env var. Singleton pattern. Cloud requires explicit `ALLOW_CLOUD_DEFAULT=true` |

### Database Tracking

**`zakops.artifacts` table** (Migration 001):
- Tracks all stored files: `filename`, `file_path`, `file_type`, `file_size`, `mime_type`, `sha256`
- Storage abstraction fields: `storage_backend`, `storage_uri`, `storage_key`
- Extracted text field for future RAG: `extracted_text TEXT`
- Linked to deals via `deal_id` FK

**`zakops.email_attachments` table** (Migration 022):
- Links email attachments to artifacts
- Fields: `filename`, `mime_type`, `size_bytes`, `artifact_id` (FK to artifacts)

## When email triage injects deal candidates with links — what happens?

**Fully automated pipeline:**

1. **Email arrives** → quarantine item created with `attachments` JSONB array
2. **Operator approves** → `DEAL.APPEND_EMAIL_MATERIALS` action fires:
   - Creates correspondence bundle in `07-Correspondence/{timestamp}_{message_id}/`
   - Copies attachments from quarantine to bundle's `attachments/` subdirectory
   - Generates `manifest.json`, `links.json`, `email.md`
3. **Enrichment** → `DEAL.ENRICH_MATERIALS` action:
   - Extracts links from attachment metadata
   - Classifies links (NDA, CIM, data room, portal vs. tracking vs. social)
   - Auth-required links queued to `.deal-registry/link_intake_queue.json`
4. **Materials API** → `GET /api/deals/{deal_id}/materials` returns email metadata + links + attachments

## Does the agent have access to stored documents?

**NO — This is a critical gap.**

| Capability | Status |
|-----------|--------|
| Agent reads deal PDFs | **NOT IMPLEMENTED** — `analyze_document` and `list_documents` tools are declared as stubs but not implemented |
| Agent searches deal documents | **NOT IMPLEMENTED** — RAG service only indexes external web pages, not deal materials |
| Agent reads email attachments | **NOT IMPLEMENTED** — no tool to access DataRoom files |
| Deal-scoped RAG | **PARTIAL** — `deal_id` parameter exists in RAG query endpoint but is not enforced; queries return global results |

## What about access control, versioning, and sharing?

| Feature | Status |
|---------|--------|
| Document-level permissions | **NOT IMPLEMENTED** — falls back to deal-level access |
| Version tracking | **NOT IMPLEMENTED** — no revision history on artifacts |
| Sharing/export | **NOT IMPLEMENTED** — no sharing UI or export API |
| Audit trail | **PARTIAL** — `correlation_id` for request tracing, but no "who accessed what document" log |
| Dashboard materials UI | **NOT IMPLEMENTED** — no "Deal Materials" view component in dashboard |

### What must be built:

| # | Gap | What to Build | Complexity |
|---|-----|---------------|------------|
| 1 | **Document upload endpoint** | `POST /api/deals/{id}/upload` → artifact store | M |
| 2 | **Dashboard materials panel** | React component to list/view/download deal docs per category | M |
| 3 | **Deal document RAG indexing** | Auto-extract text from PDFs in DataRoom, index with `deal_id` namespace in vector DB | L |
| 4 | **Agent document tools** | Implement `analyze_document`, `list_documents`, `search_deal_documents` | M |
| 5 | **Document versioning** | `version_number` + `previous_artifact_id` in artifacts table | S |
| 6 | **Access logging** | `document_access_log` table for audit trail | S |
| 7 | **Sharing/export** | Generate secure links, export bundles | M |

**Architecture status:** Storage infrastructure is solid (pluggable backends, artifact tracking, email pipeline). Feature layer is incomplete (no upload, no UI, no agent access, no RAG indexing of deal docs).

---

# 4) Chat Persistence, Long-Horizon Continuity & Model Switching

## Are chats tied permanently to specific deals?

**YES.**

- `chat_threads` table has `deal_id` column and `scope_type` (global/deal/document)
- URL pattern: `/chat?deal_id=DL-0001` creates a deal-scoped thread
- `thread_ownership` table enforces access control per user + deal
- Brain facts from `deal_brain` table are loaded for deal-scoped threads
- Specialist routing activates deal-specific analysis nodes

## Are they stored durably?

**YES — Dual durability.**

| Layer | Storage | Survives |
|-------|---------|----------|
| **Server-side** | PostgreSQL `chat_messages` (immutable, ACID) | Server restart, DB restart, crashes |
| **Client-side** | localStorage (`zakops-chat-session`) | Page refresh, tab close |
| **LangGraph checkpoints** | PostgreSQL `checkpoints` table | Server restart, enables graph resumption |
| **Summaries** | PostgreSQL `session_summaries` (versioned) | Everything |

**Session restoration flow** (`page.tsx:271-340`):
1. Check URL for `?deal_id=X`
2. Try backend first: `getChatSession(storedSessionId)` — restores from PostgreSQL
3. Fallback to localStorage if backend unavailable
4. Both are written on each turn

## Is there a guarantee no conversation history is lost?

**YES for stored messages. Partial for in-flight.**

- **Stored messages:** Immutable INSERT into `chat_messages` with `(thread_id, turn_number)` UNIQUE constraint. ACID transactions. No message is ever deleted unless explicitly requested (and even then, `legal_hold` can block deletion).
- **In-flight:** If the server crashes mid-response, the partial response is lost. User must retry. The checkpoint system means the graph state is recoverable, but the incomplete message is not.

## Context window management and long conversations?

**Implemented via tiered memory.**

- **Working memory:** Last 6 messages sent to LLM (`max_messages=6`)
- **Recall memory:** Rolling summaries every 5 turns (extractive, no LLM, deterministic)
- **Full history:** ALL messages stored in DB (never truncated), but only recent + summarized context sent to model
- **Token tracking:** Cost ledger records `input_tokens`, `output_tokens` per turn
- **Turn snapshots:** Complete pre-trim and post-trim messages stored for replay/audit

**What happens when chats become very large?** The LLM only sees the last 6 messages + recall memory (summaries + brain facts). Storage grows linearly but context window stays bounded. No practical limit on conversation length.

## Is model switching supported mid-thread?

**PARTIALLY — history survives, but tool access breaks.**

### What works:
- Thread ID persists across model switches (client-generated UUID)
- Full message history available to any model (stored in PostgreSQL)
- Evidence context rebuilt via RAG on each turn

### What breaks:
- **Tool access:** Only the local provider (Qwen via LangGraph) has access to ZakOps tools. Switching to OpenAI/Anthropic/Custom = text-only mode. The agent loses ability to execute proposals (transition deals, approve quarantine, etc.)
- **Proposals:** Proposal cards may still appear in the UI from previous turns, but clicking "Approve" would fail if the current provider is cloud-based
- **Model choice not persisted:** Provider selection is stored in client localStorage only. Server restart or new tab reverts to default (local)

### Can a user start with GPT and continue with Claude?

**Yes, the history carries over.** Both models see the same conversation. But neither cloud model can execute ZakOps tools — they're text-only advisors. Only the local LangGraph agent has full tool access.

**Recommendation:** Lock model choice per thread, or implement a clear "text-only mode" indicator when using cloud providers, disabling proposal UI elements.

---

# 4.5) Settings Provider Section — Outdated Model Lists

## Current State (as seen in screenshots)

The provider cards in `/settings` show **outdated model names**:

| Provider | Currently Shows | Should Show |
|----------|---------------|-------------|
| **OpenAI** | "GPT-4o, GPT-4 Turbo, GPT-3.5" | "GPT-5.2, GPT-4o, GPT-4o mini" |
| **Anthropic** | "Claude 3.5 Sonnet, Claude 3 Opus" | "Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5" |

The model **dropdown lists** are also outdated:

**OpenAI dropdown** (currently):
```
gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
```

**Anthropic dropdown** (currently):
```
claude-3-5-sonnet-20241022, claude-3-opus-20240229,
claude-3-sonnet-20240229, claude-3-haiku-20240307
```

## Where the outdated values live

| File | Lines | What |
|------|-------|------|
| `apps/dashboard/src/components/settings/ProviderSection.tsx` | 158 | OpenAI card description: `'GPT-4o, GPT-4 Turbo, GPT-3.5'` |
| `apps/dashboard/src/components/settings/ProviderSection.tsx` | 159 | Anthropic card description: `'Claude 3.5 Sonnet, Claude 3 Opus'` |
| `apps/dashboard/src/lib/settings/provider-settings.ts` | 206-210 | OpenAI model dropdown list |
| `apps/dashboard/src/lib/settings/provider-settings.ts` | 212-217 | Anthropic model dropdown list |
| `apps/dashboard/src/lib/settings/provider-settings.ts` | 58 | OpenAI default model: `'gpt-4o'` |
| `apps/dashboard/src/lib/settings/provider-settings.ts` | 64 | Anthropic default model: `'claude-3-5-sonnet-20241022'` |

**Note:** The chat route fallbacks are already correct (`route.ts:122` uses `claude-sonnet-4-20250514`), and the provider files (`anthropic.ts:63`) use current models. It's only the settings UI and dropdown lists that are stale.

## Desired State (per LangSmith reference)

The LangSmith Agent Builder shows the correct pattern:
1. Enter API key
2. Models appear in dropdown (current, searchable)
3. Models are accurate: Sonnet 4.6, Sonnet 4.5, Opus 4.6, Opus 4.5, Haiku 4.5, GPT-5.2, Gemini 3.1 Pro
4. "+ Add custom model" option

**What needs to change:**
1. Update card descriptions to show current flagship models
2. Update dropdown lists to current model IDs
3. Update default model selections
4. Consider: dynamic model fetching via API key validation (list models endpoint) instead of hardcoded lists

---

# 5) Builder-Side Questions You Should Be Asking

Here are 20 high-impact questions that expose structural blind spots:

### Agent Architecture Maturity

**Q1: What happens when the agent hallucinates a tool call that doesn't exist?**
Currently: The LangGraph tool executor returns an error message. But there's no retry logic or fallback tool suggestion. The agent may repeat the same invalid call up to the tool budget limit (10).

**Q2: Can the agent explain WHY it chose a particular tool?**
Currently: The `decision_ledger` table records tool name and args, but not the reasoning. There's no chain-of-thought logging. Debugging tool selection requires reading turn snapshots.

**Q3: What happens if two operators approve the same HITL proposal simultaneously?**
Currently: The `approvals` table has status tracking, but there's no explicit distributed lock. Two concurrent approvals could both succeed. The optimistic locking on quarantine (expected_version) helps for quarantine tools, but not for deal transitions.

### Memory Durability

**Q4: If mem0 long-term memory is re-enabled, what's the migration path for existing conversations?**
Currently: All existing conversations have no long-term memory entries. Re-enabling mem0 would start fresh — no backfill mechanism exists to index historical conversations into the vector store.

**Q5: Are session summaries ever pruned?**
Currently: No. Session summaries accumulate indefinitely. For a deal with 12+ months of conversations, the summaries table could grow very large. There's no TTL or archival strategy.

### State Synchronization

**Q6: What happens if the backend database and agent database disagree about a deal's state?**
Currently: The agent queries deals via BackendClient (HTTP). If backend says deal is in "screening" but agent's last checkpoint cached "inbound," the agent uses fresh data on the next tool call. But within a single turn, stale data is possible.

**Q7: Is there a single source of truth for "what the agent knows right now"?**
Currently: No. Agent state is split across: (1) LangGraph checkpoint, (2) chat_messages table, (3) session_summaries, (4) deal_brain table, (5) system prompt template. There's no unified "agent knowledge" view.

### Tool Routing Reliability

**Q8: What happens when a tool call times out?**
Currently: The BackendClient has a configurable timeout (`httpx.AsyncClient(timeout=self.timeout)`). On timeout, an exception is raised and the agent sees an error message. But there's no retry with backoff, and no circuit breaker pattern.

**Q9: Can tools be dynamically enabled/disabled per deal stage?**
Currently: No. All 14 tools are always available. The system prompt suggests which tools to use per stage, but doesn't enforce it. A user could ask the agent to "create a deal" while already in a deal context, and the tool would be available.

### Document Access Control

**Q10: If we enable S3 storage, do existing DataRoom files get migrated?**
Currently: No migration tool exists. The storage factory would need to be pointed at S3, but existing local files wouldn't move. Dual-read (check S3, fallback to local) isn't implemented.

**Q11: What prevents a user from accessing another deal's documents via the API?**
Currently: Deal-level access is assumed (single-operator system today). There's no per-document ACL. When multi-user is added, the `artifacts` table has `deal_id` but no `user_id` or permission model.

### Multi-User & Concurrency

**Q12: What happens when the system goes multi-user?**
Currently: Single-operator design. `user_id` defaults to `"default"` in most tables. Thread ownership exists but isn't enforced at the API gateway level. Adding real multi-user requires: auth middleware, user_id propagation, thread isolation enforcement, profile per-user.

**Q13: Can two users chat with the agent simultaneously about different deals?**
Currently: The LangGraph agent processes one invocation at a time per thread. Different threads can run concurrently. But resource contention (vLLM GPU, BackendClient connections) isn't managed — no queue or priority system.

### Data Privacy

**Q14: What happens to conversation data when a deal is deleted?**
Currently: `chat_threads` has `legal_hold` flag that prevents deletion. `soft_delete_thread()` marks as deleted but preserves data. `hard_delete_thread()` cascades with redaction of PII in audit logs. But there's no automatic cascade from deal deletion to thread cleanup.

**Q15: Is sensitive deal data (financials, valuations) ever sent to cloud providers?**
Currently: When using OpenAI/Anthropic, the full conversation history is sent to the cloud API — including any deal-specific information from previous turns. The Architecture Note in settings mentions "Sensitive data (SSN, tax IDs, bank accounts) is blocked from cloud providers" but there's no actual content filtering implemented on the chat route.

### Observability

**Q16: Can you tell me the p95 latency of the agent's response time?**
Currently: `latency_ms` is tracked in the response metadata, and `cost_ledger` records per-turn data. But there's no aggregation dashboard, no Grafana, no alerting. You'd need to query the database directly.

**Q17: Is there a way to replay a specific conversation turn for debugging?**
Currently: YES — `turn_snapshots` table stores complete input/output per turn (system prompt, model, temperature, raw completion, tokens). This is excellent for debugging but has no UI — requires direct DB queries.

### Audit Trails

**Q18: Is there a complete audit trail of every action the agent has ever taken?**
Currently: Partial. `decision_ledger` records tool selections. `audit_log` records HITL approvals. `chat_messages` stores all conversations. But there's no unified "agent activity log" that combines all three into a single queryable timeline.

### Long-Term Scalability

**Q19: What's the data growth rate and when do we hit storage limits?**
Currently: Not monitored. `chat_messages`, `turn_snapshots`, and `cost_ledger` are partitioned by month (good), but there's no retention policy, no archival to cold storage, and no growth projections. For a 12-24 month deal lifecycle, this could become significant.

**Q20: What happens if vLLM goes down for an extended period?**
Currently: The chat route falls back through 3 strategies: (1) try agent provider, (2) try backend agent invoke, (3) return helpful static response. If a cloud provider is configured, it's used as Strategy 1 when local fails. But there's no automatic failover — the user must manually switch providers in settings, or the code falls through to static responses.

---

# Summary: Where We Stand vs. Where We Need to Be

## Maturity Scorecard

| Dimension | Current Score | Target (World-Class) | Gap |
|-----------|:------------:|:-------------------:|:---:|
| **Agent Memory** | 6/10 | 10/10 | Cross-session memory disabled, no user profile integration |
| **Onboarding System** | 5/10 | 10/10 | Data collected but never used by agent |
| **Document Architecture** | 4/10 | 10/10 | Storage exists, no agent access, no upload, no UI, no RAG indexing |
| **Chat Persistence** | 9/10 | 10/10 | Excellent dual durability, minor gap on model choice persistence |
| **Model Switching** | 5/10 | 10/10 | History survives, tool access breaks, no graceful degradation |
| **Safety & Guards** | 9/10 | 10/10 | World-class 4-layer defense, minor gap on concurrent approvals |
| **Observability** | 5/10 | 10/10 | Data collected (snapshots, cost), no dashboards or alerting |
| **Settings/Provider UX** | 6/10 | 10/10 | Functional but outdated model lists, no dynamic model fetching |

## The Path to World-Class

The foundation is strong. The gaps are feature-layer, not architectural. The hardest infrastructure work (storage abstraction, tiered memory, HITL gates, security layers, chat persistence) is done. What's missing is the **integration layer** — connecting the pieces that already exist:

1. **Connect user profile to agent** (S effort) — biggest UX impact per line of code
2. **Enable deal document RAG** (L effort) — makes the agent truly useful for M&A research
3. **Fix model lists** (S effort) — credibility issue, easy fix
4. **Re-enable long-term memory** (M effort) — cross-session continuity
5. **Build document upload + UI** (M effort) — operators need self-service
6. **Add observability dashboards** (M effort) — operational maturity
7. **Implement graceful model switching** (S effort) — UX polish

The desired destination — a model-agnostic, memory-aware, document-intelligent, long-horizon M&A co-pilot — is achievable. The architecture supports it. The execution is the remaining work.

---

*End of Second Round Interview — System Maturity & User-Facing Intelligence*
