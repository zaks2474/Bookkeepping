# MISSION: COL-V2-BUILD-001C
## Dashboard UI Components and Compliance Pipeline
## Date: 2026-02-13
## Classification: Feature Build + UI + Compliance
## Prerequisite: COL-V2-BUILD-001B
## Successor: QA-COL-BUILD-VERIFY-001

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash or context compaction, run:

```bash
# 1. Determine current phase
cat /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001C.md

# 2. Check validation state
cd /home/zaks/zakops-agent-api && make validate-local

# 3. Check for partial work
git -C /home/zaks/zakops-agent-api status

# 4. Verify 001A/001B deliverables still intact
cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "from app.services.reflexion import ReflexionService; from app.services.fatigue_sentinel import DecisionFatigueSentinel; print('001B deliverables OK')"
```

Resume from the checkpoint file. Do not re-execute completed phases.

---

## Mission Objective

**Build 12 deliverables across Dashboard UI components and the compliance pipeline.** This is the third and final sub-mission of COL-V2-BUILD-001, covering:

1. **Citation UI + Memory Panel + Momentum Colors** (Phase 1) — dashboard indicators for brain intelligence output
2. **Ambient UI** (Phase 2) — SmartPaste, CommandPalette, Ghost Knowledge toast
3. **Compliance Pipeline** (Phase 3) — retention policy, GDPR deletion, admin compliance endpoint
4. **Final Verification** (Phase 4) — full-stack audit covering all 3 sub-missions

**What this mission is NOT:**
- This is NOT a backend mission — backend endpoints for brain, momentum, anomaly already exist (built in 001A). Use them; do not create new ones.
- This is NOT an intelligence service mission — reflexion, fatigue sentinel, spaced repetition already exist (built in 001B). Do not rebuild.
- This is NOT a redesign — extend the dashboard with new components per Surface 9, do not restructure existing pages.

**Source material:**
- Actionable items register: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md`
- Design specification: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` (3,276 lines)
- Parent mission: `/home/zaks/bookkeeping/docs/MISSION-COL-V2-BUILD-001.md` (Phases 9-10 scope)
- Surface 9 design system: `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`

---

## Context

### What 001A Built (Phase 1-4 of parent mission)
- Backend DealBrainService with GET/POST/PUT endpoints in zakops-backend
- brain_history table with INSERT trigger
- Core wiring: graph.py post-turn enrichment (snapshot_writer, brain_extraction, drift_detection, citation_audit)
- Service completion: BackendClient migration, admin auth, configurable thresholds, proposal expiration
- Legal hold tables (legal_hold_locks, legal_hold_log) and create_monthly_partitions function

### What 001B Built (Phase 5-8 of parent mission)
- ReflexionService with CritiqueResult model, wired into graph.py
- Chain-of-Verification (claim verification)
- DecisionFatigueSentinel, StallPredictor, SpacedRepetition services
- Ghost knowledge SSE event type registered in sse_events.py
- PlanAndExecuteGraph with 4 specialists + synthesis in NodeRegistry
- MCP cost/decision ledger integration
- Morning briefing, anomaly detection, sentiment coach services

### What 001C Must Build
- 5 dashboard components: CitationIndicator, MemoryStatePanel, SmartPaste, CommandPalette, GhostKnowledgeToast
- Momentum color bands in deal detail view
- 2 compliance services: retention_policy.py, gdpr_service.py
- 1 admin endpoint: POST /admin/compliance/purge
- Final verification + completion report spanning all 3 sub-missions

### Backend Endpoints Available (from 001A + existing backend services)
- `GET /api/deals/{id}/brain` — brain state (facts, risks, decisions, ghost_knowledge, summary)
- `GET /api/deals/{id}/brain/momentum` — momentum score
- `POST /api/deals/{id}/brain/facts` — add facts
- `POST /api/deals/{id}/brain/ghost/confirm` — confirm ghost knowledge
- `POST /api/deals/{id}/brain/ghost/dismiss` — dismiss ghost knowledge

### R5-POLISH Coordination
Phase 0 must check for any in-progress dashboard layout changes from R5-POLISH. If layout changes are pending, coordinate new component placement to avoid merge conflicts.

---

## Glossary

| Term | Definition |
|------|-----------|
| Surface 9 | Component Design System — `.claude/rules/design-system.md`. Governs ALL dashboard UI conventions |
| Citation Strength | Score from citation_audit.py: >= 0.5 strong (green), 0.3-0.5 weak (amber), < 0.3 orphan (red) |
| Ghost Knowledge | Facts the user references that don't exist in the Deal Brain. Detected during brain extraction. |
| Reflexion Critique | Self-critique output stored as `critique_result` on turn snapshots. "Refined" badge indicates it was applied. |
| Legal Hold | Thread-level lock preventing deletion. Threads with `legal_hold=true` MUST NOT be deleted by GDPR purge. |
| Retention Tier | Time-based deletion policy: 30d (default), 90d (deal-scoped), 365d (legal hold), forever (compliance) |

---

## Architectural Constraints

Per standing constraints in CLAUDE.md and contract surface discipline. Mission-specific additions:

- **Surface 9 mandatory for ALL new dashboard components** — every component in Phases 1-2 must follow `.claude/rules/design-system.md`. Reference the rule set by name; the builder loads it automatically for dashboard file paths.
- **Promise.allSettled mandatory** — all multi-fetch patterns in new dashboard components must use `Promise.allSettled` with typed empty fallbacks. `Promise.all` is banned.
- **Server-side counts only** — MemoryStatePanel tier counts must come from API responses or server-side computation, never client-side `.length` counting.
- **Backend is read-only** — this mission does NOT modify `/home/zaks/zakops-backend/`. All backend endpoints needed already exist. Use them via BackendClient or dashboard API routes.
- **Admin endpoints require role check** — the compliance purge endpoint must verify admin role before allowing execution.
- **GDPR purge respects legal holds** — threads with `legal_hold=true` in legal_hold_locks MUST NOT be deleted. This is a hard safety requirement.
- **Fire-and-forget for enrichment** — any new async operations added to graph.py or services must not block user responses.
- **console.warn for degradation, console.error for unexpected** — new dashboard components must follow the standing logging classification rules.

---

## Anti-Pattern Examples

### WRONG: Promise.all for multi-fetch in dashboard component
```typescript
const [brain, momentum, memory] = await Promise.all([
  fetchBrain(dealId), fetchMomentum(dealId), fetchMemory(threadId)
]);
// If fetchMomentum fails, brain and memory data are lost — entire component crashes
```

### RIGHT: Promise.allSettled with typed fallbacks
```typescript
const [brainResult, momentumResult, memoryResult] = await Promise.allSettled([
  fetchBrain(dealId), fetchMomentum(dealId), fetchMemory(threadId)
]);
const brain = brainResult.status === 'fulfilled' ? brainResult.value : { facts: [], risks: [] };
const momentum = momentumResult.status === 'fulfilled' ? momentumResult.value : { score: 0 };
const memory = memoryResult.status === 'fulfilled' ? memoryResult.value : { tiers: [] };
// Component renders with available data even if one fetch fails
```

### WRONG: console.error for backend-down in dashboard
```typescript
} catch (err) {
  console.error("Failed to fetch momentum score", err);  // backend is just down — expected
  return { score: 0 };
}
```

### RIGHT: console.warn for degradation
```typescript
} catch (err) {
  if (err instanceof TypeError || (err as any).code === 'ECONNREFUSED') {
    console.warn("Momentum score unavailable — backend may be down");
    return { score: 0 };
  }
  console.error("Unexpected error fetching momentum score", err);
  throw err;
}
```

### WRONG: Client-side counting for memory tiers
```typescript
<span>Working: {messages.length}</span>  // counts only fetched page, not accurate
```

### RIGHT: Server-side count from API
```typescript
<span>Working: {memoryState.working_count}</span>  // server-computed count
```

### WRONG: GDPR purge deleting legal-held threads
```python
async def gdpr_purge(user_id: str, db):
    threads = await db.fetch_all("SELECT id FROM threads WHERE user_id = $1", user_id)
    for t in threads:
        await db.execute("DELETE FROM messages WHERE thread_id = $1", t.id)  # deletes everything including legal holds!
```

### RIGHT: GDPR purge respecting legal holds
```python
async def gdpr_purge(user_id: str, db):
    threads = await db.fetch_all(
        "SELECT t.id, lh.hold_type FROM threads t LEFT JOIN legal_hold_locks lh ON t.id = lh.thread_id WHERE t.user_id = $1",
        user_id
    )
    for t in threads:
        if t.hold_type is not None:
            await _log_skipped(t.id, "legal_hold_active", db)
            continue
        await db.execute("DELETE FROM messages WHERE thread_id = $1", t.id)
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | SmartPaste entity extraction produces false positives — every capitalized word flagged as entity | HIGH | Useless UX, user ignores feature | Phase 2 task specifies pattern tuning: require 2+ character names, filter common words, test with real text |
| 2 | CommandPalette Cmd+K conflicts with browser address bar or other shortcuts | MEDIUM | Palette doesn't open on some browsers | Phase 2 task specifies `preventDefault` handling; test in Chrome/Firefox |
| 3 | Citation indicators break chat message layout with long messages or multiple citations | MEDIUM | UI regression in chat view | Phase 1 gate: test with varying message lengths; overflow handling in CSS |
| 4 | GDPR purge accidentally deletes legal-held threads | HIGH | Compliance violation, data loss | Phase 3 has explicit legal_hold check as a hard gate; anti-pattern shown above |
| 5 | New dashboard components conflict with pending R5-POLISH layout changes | MEDIUM | Merge conflicts, broken layout | Phase 0 discovery audits for in-progress R5-POLISH work and coordinates placement |

---

## Phase 0 -- Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify 001A and 001B completion, establish clean validation baseline, and audit the dashboard component structure to identify correct locations for new components.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Run baseline validation** -- `cd /home/zaks/zakops-agent-api && make validate-local`
  - **Checkpoint:** Must exit 0. If not, fix before proceeding.
- P0-02: **Verify 001A deliverables** -- confirm key 001A outputs exist:
  - `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_locks"` (legal hold tables)
  - `python -c "from app.core.langgraph.graph import build_graph; print('graph OK')"` (core wiring)
  - **Decision Tree:**
    - **IF** legal_hold_locks table exists AND graph imports cleanly -> proceed
    - **ELSE** -> STOP. 001A is incomplete. Do not proceed with 001C.
- P0-03: **Verify 001B deliverables** -- confirm key 001B outputs exist:
  - `python -c "from app.services.reflexion import ReflexionService; print('reflexion OK')"` (reflexion)
  - `python -c "from app.services.fatigue_sentinel import DecisionFatigueSentinel; print('fatigue OK')"` (cognitive intelligence)
  - `python -c "from app.schemas.sse_events import *; print('SSE OK')"` (ghost knowledge SSE event)
  - **Decision Tree:**
    - **IF** all imports succeed -> proceed
    - **ELSE** -> STOP. 001B is incomplete. Do not proceed with 001C.
- P0-04: **Audit dashboard component structure** -- discover correct locations for new components:
  - Identify the chat message component (for citation indicators)
  - Identify the chat sidebar area (for MemoryStatePanel)
  - Identify the chat input component (for SmartPaste)
  - Identify the deal detail/pipeline view (for momentum colors)
  - Identify the global layout component (for CommandPalette)
  - Record file paths in the checkpoint file.
- P0-05: **Check for R5-POLISH in-progress work** -- scan for pending dashboard layout changes:
  - `git -C /home/zaks/zakops-agent-api stash list`
  - `git -C /home/zaks/zakops-agent-api branch --list '*polish*' '*r5*'`
  - **Decision Tree:**
    - **IF** R5-POLISH branches or stashes found -> note layout context, coordinate placement
    - **ELSE** -> proceed normally
- P0-06: **Read spec sections** for this mission's scope:
  - S8.2 (Citation UI), S5.4 (Memory Panel), S17.4 (SmartPaste), S17.6 (CommandPalette)
  - S20 (Momentum UI), S7.3-S7.6 (GDPR/Retention), S14.7 (Ghost Knowledge)
  - Source: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md`
- P0-07: **Read Surface 9 design system rules** -- `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
- P0-08: **Write checkpoint** -- per Continuity Protocol

### Gate P0
- `make validate-local` passes
- 001A legal hold tables exist
- 001B reflexion + fatigue sentinel + SSE events import cleanly
- Dashboard component locations identified and recorded in checkpoint
- No unresolved R5-POLISH conflicts

---

## Phase 1 -- Citation UI + Memory Panel + Momentum Colors
**Complexity:** L
**Estimated touch points:** 4-6 new/modified dashboard files

**Purpose:** Build the three dashboard UI components that visualize brain intelligence output: citation strength indicators on chat messages, a memory tier panel in the sidebar, and momentum color bands in deal detail.

### Blast Radius
- **Services affected:** Dashboard (port 3003)
- **Pages affected:** Chat interface (citation indicators, memory panel), Deal detail view (momentum colors)
- **Downstream consumers:** End users viewing chat messages and deal details

### Tasks
- P1-01: **Build CitationIndicator component** per S8.2:
  - Render citation strength as colored underlines on chat messages
  - Green (score >= 0.5) = strong citation, Amber (0.3-0.5) = weak citation, Red (< 0.3 or no source) = orphan
  - Target: Dashboard chat message component area (path discovered in P0-04)
  - Per Surface 9 design system rules
  - **Checkpoint:** Component renders without TypeScript errors: `npx tsc --noEmit`
- P1-02: **Add "Refined" badge** per S8.2:
  - On messages where `critique_result` is present (from reflexion processing), render a "Refined" badge
  - Badge indicates the message went through reflexion critique and was improved
  - Target: Same chat message component as P1-01
  - Per Surface 9
- P1-03: **Build MemoryStatePanel component** per S5.4:
  - Sidebar panel in chat view showing memory tiers:
    - Working: last 6 messages (real-time count)
    - Recall: brain facts + session summaries (count from API)
    - Archival: expired summaries (count only, from API)
  - Tier counts must be server-side, not client-side `.length`
  - Target: Dashboard chat sidebar area (path discovered in P0-04)
  - Per Surface 9
  - **Checkpoint:** Panel renders with tier labels and counts
- P1-04: **Add Momentum UI color bands** per S20:
  - In deal detail/pipeline view, render momentum score with color coding:
    - Green (70+), Amber (40-69), Red (0-39)
  - Fetch momentum score from backend `GET /api/deals/{id}/brain/momentum` endpoint
  - Target: Dashboard deal detail component (path discovered in P0-04)
  - Per Surface 9
  - **Checkpoint:** Color band renders for a deal with available momentum data

### Decision Tree
- **IF** chat message component uses a render function pattern -> add citation underlines as a sub-component
- **ELSE IF** chat message component is a single template -> wrap citation text in styled spans
- **IF** deal detail view has no existing momentum section -> create a new section per Surface 9
- **ELSE IF** momentum section exists without colors -> add color bands only

### Rollback Plan
1. `git checkout -- apps/dashboard/src/` (revert all dashboard changes)
2. Verify: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` passes after rollback

### Gate P1
- Dashboard compiles: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- CitationIndicator component file exists and exports correctly
- MemoryStatePanel component file exists and exports correctly
- Momentum color logic renders green/amber/red based on score thresholds
- `make validate-local` passes

---

<!-- Adopted from Improvement Area IA-1: Context checkpoint at midpoint -->

## CONTEXT CHECKPOINT -- Between Phase 2 and Phase 3

Phase 2 completes the dashboard UI work. Phase 3 switches context entirely to compliance pipeline (Python, agent-api services). If context is constrained after Phase 2, summarize progress, commit intermediate work, update the checkpoint file, and continue in a fresh session.

---

## Phase 2 -- Ambient UI
**Complexity:** L
**Estimated touch points:** 4-6 new/modified dashboard files + 1 agent-api file

**Purpose:** Build the ambient intelligence UI features: SmartPaste for entity extraction from pasted text, CommandPalette for keyboard-driven navigation, and Ghost Knowledge toast for SSE-driven notifications.

### Blast Radius
- **Services affected:** Dashboard (port 3003)
- **Pages affected:** Chat interface (SmartPaste, Ghost Knowledge toast), All pages (CommandPalette)
- **Downstream consumers:** End users, backend brain/facts endpoint (SmartPaste writes), backend ghost confirm/dismiss endpoints

### Tasks
- P2-01: **Build SmartPaste component** per S17.4:
  - When user pastes text into chat input, extract entities: numbers (currency, quantities), proper nouns (multi-word capitalized), dates
  - Show "Add to Deal Brain" button for each extracted entity
  - On click, POST extracted entity to backend brain/facts endpoint
  - Target: Dashboard chat input component area (path discovered in P0-04)
  - Per Surface 9
  - **Checkpoint:** Pasting text with a proper noun and a date shows extraction UI
- P2-02: **Build CommandPalette component** per S17.6:
  - Cmd+K (Mac) / Ctrl+K (Win) opens a search/command palette overlay
  - Context-aware command sets:
    - In deal view: transition stage, add note, export deal, view brain
    - In global view: navigate to deals, search deals, open settings
  - Target: Dashboard global layout (path discovered in P0-04)
  - Per Surface 9
  - **Checkpoint:** Pressing Cmd+K opens the palette; typing filters commands
- P2-03: **Add Ghost Knowledge UI toast** per S14.7:
  - Listen for `ghost_knowledge_flags` SSE event on the existing event stream
  - When event arrives, show a toast notification: "Brain detected unknown reference: {fact}"
  - Two action buttons: "Confirm" and "Dismiss"
  - Confirm calls `POST /api/deals/{id}/brain/ghost/confirm` (via dashboard API route)
  - Dismiss calls `POST /api/deals/{id}/brain/ghost/dismiss` (via dashboard API route)
  - Target: Dashboard chat interface or global notification area
  - Per Surface 9
  - **Checkpoint:** Toast component renders with mock data; Confirm/Dismiss buttons call correct endpoints
- P2-04: **Write checkpoint**

### Decision Tree
- **IF** dashboard already has a toast/notification system -> integrate Ghost Knowledge into it
- **ELSE** -> build a minimal toast component per Surface 9, then use it for Ghost Knowledge
- **IF** dashboard has an existing keyboard shortcut handler -> register Cmd+K there
- **ELSE** -> add a global keydown listener with `preventDefault` to avoid browser shortcut conflicts

### Rollback Plan
1. `git checkout -- apps/dashboard/src/` (revert all dashboard changes from this phase)
2. Verify: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` passes after rollback

### Gate P2
- Dashboard compiles: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- CommandPalette component file exists and exports correctly
- SmartPaste component file exists and exports correctly
- GhostKnowledgeToast component file exists and exports correctly
- `make validate-local` passes

---

## Phase 3 -- Compliance Pipeline
**Complexity:** L
**Estimated touch points:** 3 new files in agent-api + 1 modified file

**Purpose:** Build the compliance infrastructure: retention policy engine for time-based data management, GDPR deletion service respecting legal holds, and an admin-only compliance purge endpoint.

### Blast Radius
- **Services affected:** agent-api (port 8095)
- **Pages affected:** None (admin-only, no UI)
- **Downstream consumers:** Legal hold system (from 001A), admin panel, compliance auditors

### Tasks
- P3-01: **Build RetentionPolicy engine** per S7.4:
  - Configurable retention tiers:
    - 30 days (default) — general threads
    - 90 days (deal-scoped) — threads associated with a deal
    - 365 days (legal hold) — threads with active legal holds
    - forever (compliance) — threads flagged for permanent retention
  - Applied per thread based on `scope_type` and `legal_hold` status
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/retention_policy.py` (new file)
  - **Checkpoint:** `python -c "from app.services.retention_policy import RetentionPolicy; print('OK')"`
- P3-02: **Build GDPR deletion service** per S7.3:
  - `gdpr_purge(user_id)` function that:
    - Fetches all threads owned by user_id
    - For each thread, checks legal_hold_locks table
    - Threads with active legal holds: SKIP and log to legal_hold_log with action='gdpr_skip'
    - Threads without holds: DELETE messages, snapshots, summaries, then the thread itself
    - Log every deletion to legal_hold_log with action='gdpr_delete'
    - Return an audit report: { deleted_count, skipped_count, skipped_thread_ids }
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py` (new file)
  - **Checkpoint:** `python -c "from app.services.gdpr_service import gdpr_purge; print('OK')"`
- P3-03: **Build compliance deletion API endpoint** per S7.5:
  - `POST /admin/compliance/purge` — admin-only endpoint
  - Accepts: `{ user_id: string }`
  - Validates: admin role (per standing admin auth pattern from 001A)
  - Executes: `gdpr_purge(user_id)` from gdpr_service.py
  - Returns: audit report from GDPR service
  - Non-admin requests receive 403
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py` (add to existing router)
  - **Checkpoint:** Import chatbot module: `python -c "from app.api.v1.chatbot import router; print('OK')"`
- P3-04: **Write checkpoint**

### Decision Tree
- **IF** legal_hold_locks table does not exist (001A incomplete) -> STOP. Do not build GDPR service without the hold infrastructure.
- **ELSE** -> proceed with full implementation
- **IF** chatbot.py already has admin auth pattern (from 001A admin endpoint work) -> reuse the same pattern
- **ELSE** -> implement role check per the anti-pattern example above

### Rollback Plan
1. Remove new files: `rm apps/agent-api/app/services/retention_policy.py apps/agent-api/app/services/gdpr_service.py`
2. Revert chatbot.py: `git checkout -- apps/agent-api/app/api/v1/chatbot.py`
3. Restart agent-api: `cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose restart agent-api`

### Gate P3
- RetentionPolicy imports: `python -c "from app.services.retention_policy import RetentionPolicy; print('OK')"`
- GDPR service imports: `python -c "from app.services.gdpr_service import gdpr_purge; print('OK')"`
- Compliance endpoint rejects non-admin: verify 403 response for unauthenticated/non-admin request
- Legal hold respect: GDPR service code contains explicit legal_hold check (grep for `legal_hold` in gdpr_service.py)
- `make validate-local` passes

---

## Phase 4 -- Final Verification & Full-Stack Self-Audit
**Complexity:** M
**Estimated touch points:** 0 (verification only) + 2-3 bookkeeping files

**Purpose:** Run comprehensive validation, cross-check all 3 sub-mission acceptance criteria, produce completion report, and update bookkeeping. This is the FINAL phase of the entire COL-V2-BUILD-001 effort.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** QA successor mission (QA-COL-BUILD-VERIFY-001)

### Tasks
- P4-01: **Run full validation** -- `cd /home/zaks/zakops-agent-api && make validate-local`
- P4-02: **Run TypeScript compilation** -- `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P4-03: **Import check all new services** from this mission:
  - `python -c "from app.services.retention_policy import RetentionPolicy; print('OK')"`
  - `python -c "from app.services.gdpr_service import gdpr_purge; print('OK')"`
- P4-04: **Cross-check 001A acceptance criteria** -- verify key 001A deliverables still intact:
  - Backend brain endpoints respond (if backend running)
  - Legal hold tables exist
  - graph.py post-turn enrichment wired
- P4-05: **Cross-check 001B acceptance criteria** -- verify key 001B deliverables still intact:
  - ReflexionService imports
  - NodeRegistry has 4+ specialists
  - PlanAndExecuteGraph imports
  - Ghost knowledge SSE event type exists
- P4-06: **Cross-check 001C dashboard components** -- verify all 5 components exist and the dashboard compiles
- P4-07: **Final item count reconciliation** -- compare built items against `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` to produce final coverage metrics
- P4-08: **Update CHANGES.md** -- record all changes from this mission in `/home/zaks/bookkeeping/CHANGES.md`
- P4-09: **Produce completion report** -- write `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001C-COMPLETION.md` with:
  - Phase-by-phase results for 001C
  - Summary of all 3 sub-missions (001A + 001B + 001C)
  - Files created and modified across all 3 sub-missions
  - Total items completed vs. deferred vs. out-of-scope
  - Validation results with evidence
  - Evidence paths for every AC
- P4-10: **Fix CRLF and ownership** -- `sed -i 's/\r$//'` on any new .sh files, `chown zaks:zaks` on new files under /home/zaks/
- P4-11: **Write final checkpoint**

### Gate P4
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All new services import without error
- 001A + 001B deliverables verified intact
- CHANGES.md updated
- Completion report written covering all 3 sub-missions

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    |
    v
Phase 1 (Citation UI + Memory Panel + Momentum Colors)
    |
    v
Phase 2 (Ambient UI: SmartPaste + CommandPalette + Ghost Toast)
    |
    v
    *** CONTEXT CHECKPOINT ***
    |
    v
Phase 3 (Compliance Pipeline)
    |
    v
Phase 4 (Final Verification & Self-Audit)
```

Phases execute sequentially: 0 -> 1 -> 2 -> checkpoint -> 3 -> 4.

---

## Acceptance Criteria

### AC-1: Citation UI Shows Strength Indicators
Citation strength renders as colored underlines on chat messages: green (score >= 0.5), amber (0.3-0.5), red (orphan/no source). Component exists and TypeScript compiles.

### AC-2: Refined Badge on Reflexion Messages
Messages with `critique_result` present display a "Refined" badge, indicating the message went through reflexion critique.

### AC-3: MemoryStatePanel Shows Tier Counts
Sidebar panel displays Working (last 6 messages), Recall (brain facts + summaries), and Archival (expired summaries) tier counts. Counts are server-side, not client-side `.length`.

### AC-4: Momentum Score Renders with Color Bands
Deal detail view shows momentum score with green (70+), amber (40-69), red (0-39) color coding, fetched from the backend momentum endpoint.

### AC-5: SmartPaste Extracts Entities
Pasting text into chat input extracts entities (numbers, proper nouns, dates) and offers "Add to Deal Brain" action for each.

### AC-6: CommandPalette Opens on Cmd+K
Cmd+K (Mac) / Ctrl+K (Win) opens a context-aware command palette with deal-specific or global commands depending on current view.

### AC-7: Ghost Knowledge Toast with Actions
When `ghost_knowledge_flags` SSE event arrives, a toast notification appears with the flagged fact and "Confirm" / "Dismiss" action buttons that call the correct backend endpoints.

### AC-8: RetentionPolicy Service Applies Tier-Based Retention
RetentionPolicy service exists with configurable tiers (30d, 90d, 365d, forever) applied per thread based on scope_type and legal_hold status.

### AC-9: GDPR Purge Respects Legal Holds
`gdpr_purge(user_id)` deletes user threads, messages, snapshots, and summaries while explicitly skipping threads with active legal holds. Every deletion and skip is logged to legal_hold_log.

### AC-10: Compliance Purge Endpoint Works with Admin Auth
`POST /admin/compliance/purge` accepts user_id, validates admin role (returns 403 for non-admin), runs GDPR purge, and returns an audit report.

### AC-11: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes. No test breakage. All existing services still function. 001A and 001B deliverables verified intact.

### AC-12: Bookkeeping Complete
CHANGES.md updated. Completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001C-COMPLETION.md` covering all 3 sub-missions. Checkpoint file updated.

---

## Guardrails

1. **Scope: Dashboard UI + compliance pipeline only** -- do not build new intelligence services, backend endpoints, or database migrations. Those were done in 001A/001B.
2. **Surface 9 mandatory** -- ALL dashboard components must follow `.claude/rules/design-system.md`. Per Surface 9 design system rules.
3. **Promise.allSettled mandatory** -- `Promise.all` is banned in dashboard data-fetching code.
4. **Generated files never edited** -- do not modify `*.generated.ts` or `*_models.py`. Use bridge files.
5. **Backend repo read-only** -- do not modify any files in `/home/zaks/zakops-backend/`. Use existing endpoints only.
6. **GDPR purge MUST respect legal holds** -- threads with `legal_hold=true` in legal_hold_locks MUST NOT be deleted. This is non-negotiable.
7. **Contract surface discipline** -- run `make sync-all-types` if any API boundary changes.
8. **WSL safety** -- strip CRLF from .sh files (`sed -i 's/\r$//'`), fix ownership on files under /home/zaks/ (`chown zaks:zaks`).
9. **Port 8090 is FORBIDDEN** -- never use or reference.
10. **Server-side counts only** -- no client-side `.length` counting for display values in MemoryStatePanel or any other component.
<!-- Adopted from Improvement Area IA-15 -->
11. **Governance surfaces** -- if touching error handling -> `make validate-surface12`; if adding tests -> `make validate-surface13`.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify BOTH 001A AND 001B deliverables exist before proceeding?"
- [ ] "Did I identify the correct dashboard component locations for all 5 new components?"
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I check for R5-POLISH in-progress work that might conflict?"

### After every dashboard component (Phases 1-2):
- [ ] "Does this component follow Surface 9 design system rules?"
- [ ] "Am I using Promise.allSettled, not Promise.all, for data fetching?"
- [ ] "Am I using server-side counts, not `.length`, for display values?"
- [ ] "Am I using console.warn for degradation, not console.error?"
- [ ] "Does `npx tsc --noEmit` still pass?"
<!-- Adopted from Improvement Area IA-10 -->
- [ ] "If I wrote tests, do test names contain functional keywords (citation, memory, momentum, paste, palette, ghost) for QA grep?"

### After compliance pipeline (Phase 3):
- [ ] "Does the GDPR service explicitly check legal_hold_locks before deleting?"
- [ ] "Does the GDPR service log every deletion AND every skip to legal_hold_log?"
- [ ] "Does the compliance endpoint reject non-admin requests with 403?"
- [ ] "Can I grep 'legal_hold' in gdpr_service.py and find the guard clause?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now, not 2 phases ago?"
- [ ] "Does `npx tsc --noEmit` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce the completion report covering ALL 3 sub-missions?"
- [ ] "Did I verify 001A and 001B deliverables are still intact (not regressed)?"
- [ ] "Did I create ALL files listed in the 'Files to Create' table?"
- [ ] "Did I reconcile the final item count against COL-V2-ACTIONABLE-ITEMS.md?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py` | P3 | Add POST /admin/compliance/purge endpoint |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/` (chat message component, discovered in P0) | P1 | Citation indicators + Refined badge |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/` (chat sidebar, discovered in P0) | P1 | MemoryStatePanel |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/` (deal detail view, discovered in P0) | P1 | Momentum color bands |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/` (chat input, discovered in P0) | P2 | SmartPaste |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/` (global layout, discovered in P0) | P2 | CommandPalette |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| CitationIndicator component (exact path per Surface 9, discovered in P0) | P1 | Citation strength underlines + Refined badge |
| MemoryStatePanel component (exact path per Surface 9, discovered in P0) | P1 | Memory tier sidebar panel |
| SmartPaste component (exact path per Surface 9, discovered in P0) | P2 | Entity extraction from pasted text |
| CommandPalette component (exact path per Surface 9, discovered in P0) | P2 | Cmd+K command palette overlay |
| GhostKnowledgeToast component (exact path per Surface 9, discovered in P0) | P2 | SSE-driven ghost knowledge notification |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/retention_policy.py` | P3 | RetentionPolicy engine with tier-based retention |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py` | P3 | GDPR deletion service respecting legal holds |
| `/home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001C.md` | P0+ | Multi-session checkpoint |
| `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001C-COMPLETION.md` | P4 | Completion report covering all 3 sub-missions |

### Files to Read (sources of truth -- do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` | Design specification (3,276 lines) — S5.4, S7.3-S7.6, S8.2, S14.7, S17.4, S17.6, S20 |
| `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` | Actionable items register — final reconciliation target |
| `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` | Surface 9 design system rules — mandatory for all dashboard components |
| `/home/zaks/zakops-backend/src/api/orchestration/routers/brain.py` | Endpoint contracts for ghost confirm/dismiss, momentum, brain facts |

---

## Stop Condition

This mission is DONE when:
- All 12 acceptance criteria (AC-1 through AC-12) are met
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All changes recorded in CHANGES.md
- Completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001C-COMPLETION.md`
- Checkpoint file updated to reflect completion
- 001A + 001B deliverables verified intact (no regressions from 001C work)

This is the **FINAL sub-mission** of COL-V2-BUILD-001. After completion, the successor QA mission (QA-COL-BUILD-VERIFY-001) verifies all 3 sub-missions together.

**Do NOT proceed to:**
- Running the QA successor mission (QA-COL-BUILD-VERIFY-001) -- that is a separate session
- Deploying to production -- this is development work only
- Modifying the COL-DESIGN-SPEC-V2.md -- the spec is a read-only source of truth
- Modifying backend repo (`/home/zaks/zakops-backend/`) -- backend is read-only for this mission

---

## Lab Loop Configuration

For automated execution via Lab Loop:

```
TASK_ID=COL-V2-BUILD-001C
REPO_DIR=/home/zaks/zakops-agent-api
GATE_CMD="make validate-local && cd apps/dashboard && npx tsc --noEmit"
```

---

*End of Mission Prompt -- COL-V2-BUILD-001C*
