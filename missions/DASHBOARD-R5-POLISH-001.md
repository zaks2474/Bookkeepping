# MISSION: DASHBOARD-R5-POLISH-001
## Dashboard Round 5 — Layout Balance, Chat History Actions, Settings Refinement
## Date: 2026-02-12
## Classification: Platform Polish & Feature Build
## Prerequisite: DASHBOARD-P4-STABILIZE-001 (complete), P4-STABILIZE Post-QA Remediation (complete)
## Successor: QA-R5P-VERIFY-001

---

## Mission Objective

Apply four targeted refinements identified during user UI testing (Round 5) to bring the dashboard to world-class standard. This mission covers:

1. **Layout balance** — All Deals card on the Dashboard must match right-column height (no dead vertical space)
2. **Chat history actions** — Five actions per chat history entry (Delete, Rename, Pin/Unpin, Duplicate, Archive)
3. **Settings visual consistency** — Sidebar nav items must share uniform styling
4. **Settings performance** — Investigate and resolve slow load compared to other tabs

This is a POLISH and FEATURE BUILD mission — all critical bugs are resolved. The focus is interaction completeness, layout symmetry, and UX consistency.

**Source material:**
- User Round 5 findings (verbal, 2026-02-12)
- Prior mission completion: `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md`
- Post-QA remediation: `/home/zaks/bookkeeping/CHANGES.md` (entry: 2026-02-12 — P4-STABILIZE Post-QA Remediation)

---

## Context

### Current State
- Dashboard is stable: 14/14 contract surfaces PASS, TypeScript compiles clean
- All P4-STABILIZE findings remediated + post-QA fixes applied
- User confirmed: chat dedup fixed, alerts clickable, settings scrollable, performance improved
- Remaining: layout imbalance, missing chat actions, settings visual/perf gaps

### Chat History Architecture (Current)
- **Storage:** Pure localStorage — `zakops-chat-history` (metadata), `zakops-chat-archive-{id}` (data blobs)
- **Operations today:** `getSessionHistory()`, `archiveSession()`, `loadArchivedSession()`, `deleteArchivedSession()`
- **UI:** `ChatHistoryRail.tsx` — ScrollArea with clickable session items, hover-visible trash icon (delete only)
- **Backend:** Placeholder only (`GET /api/chat/session/{id}` returns empty — no backend persistence for history)
- **Limit:** MAX_HISTORY = 20 sessions
- **Data model:** `ChatSessionSummary { id, preview, messageCount, scopeType, dealId?, dealName?, createdAt, lastActive }`

### Settings Architecture (Current)
- Settings page at `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
- NOT inside ShellLayout — standalone page with `h-dvh` container
- SettingsNav at `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx`
- Desktop: sticky sidebar with `rounded-lg border border-border/60 bg-card p-2`
- Mobile: Select dropdown
- 6 sections: AI Provider, Email, Agent, Notifications, Data & Privacy, Appearance
- Preferences fetched via `useUserPreferences()` hook → `GET /api/settings/preferences`

---

## Glossary

| Term | Definition |
|------|-----------|
| ChatHistoryRail | Sidebar component showing archived chat sessions in `/components/chat/ChatHistoryRail.tsx` |
| ChatSessionSummary | Metadata record for one archived chat session (id, preview, timestamps, scope) |
| ShellLayout | Wrapper providing sidebar + header for main pages. Settings does NOT use this |
| Surface 9 | Component Design System — `.claude/rules/design-system.md`. Governs dashboard UI conventions |

---

## Architectural Constraints

- **Promise.allSettled mandatory** — `Promise.all` is banned in dashboard data-fetching. All multi-fetch must use `Promise.allSettled` with typed empty fallbacks.
- **Server-side counts only** — no client-side `.length` counting for display values. Use `pipelineData?.total_active` or `stageCounts[stage]`.
- **PIPELINE_STAGES source of truth** — from `execution-contracts.ts`. No hardcoded stage lists.
- **Surface 9 compliance** — `console.warn` for expected degradation, `console.error` for unexpected errors only.
- **Contract surface discipline** — generated files never edited directly; use bridge files.
- **localStorage is the only persistence layer for chat history** — no backend API exists yet. All chat history operations are client-side only.
- **No new dependencies** — implement features using existing UI primitives (shadcn/ui components, tabler icons).

---

## Anti-Pattern Examples

### WRONG: Hardcoded grid row heights
```
<div className='grid grid-rows-[400px_400px] md:grid-cols-3'>
```
// Rigid heights break on different content sizes

### RIGHT: Flex stretch with min-height
```
<div className='grid gap-4 md:grid-cols-3'>
  <div className='md:col-span-2 flex flex-col gap-4'>
    <Card>...</Card>
    <Card className='flex-1 flex flex-col min-h-[300px]'>  <!-- stretches to fill -->
```
// Card grows to match sibling column height via grid auto-rows

### WRONG: Inline action handlers without confirmation
```
<button onClick={() => deleteSession(id)}>Delete</button>
// Accidental click permanently deletes — no undo
```

### RIGHT: Confirmation dialog before destructive action
```
<AlertDialog>
  <AlertDialogTrigger>Delete</AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogTitle>Delete this chat?</AlertDialogTitle>
    <AlertDialogAction onClick={() => deleteSession(id)}>Confirm</AlertDialogAction>
  </AlertDialogContent>
</AlertDialog>
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | All Deals card `flex-1` fix causes the card to collapse to 0 height when deals list is empty | MEDIUM | Broken empty state | Phase 1 must verify empty state renders `min-h-[300px]` fallback |
| 2 | Chat Pin/Archive operations corrupt localStorage causing all history to disappear | MEDIUM | Data loss | Phase 2 must wrap all localStorage writes in try/catch with fallback |
| 3 | Settings performance fix changes `staleTime` globally, breaking React Query cache behavior on other pages | LOW | Side-effect regression | Phase 4 must only change settings-specific query options, not globals |
| 4 | Chat history actions (rename, pin) add fields to `ChatSessionSummary` that break existing stored data | HIGH | History rail crashes on load | Phase 2 must handle migration: missing fields default to safe values |
| 5 | CRLF in new .sh or .ts files breaks CI or runtime | LOW | Build failure | WSL safety: `sed -i 's/\r$//'` on any new shell scripts |

---

## Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify codebase is stable before making changes.

### Tasks
- P0-01: **Run baseline validation** — `make validate-local` must PASS (14/14 surfaces)
- P0-02: **Run TypeScript compilation** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P0-03: **Capture current dashboard screenshot** — Playwright screenshot of `/dashboard` at 1280x720 showing deals card and right column
- P0-04: **Capture current settings screenshot** — Playwright screenshot of `/settings` at 1280x720 showing sidebar nav
- P0-05: **Inventory chat history entries** — Read `ChatHistoryRail.tsx` and `chat-history.ts` to confirm current operations and data model

### Gate P0
- `make validate-local` exits 0
- `npx tsc --noEmit` exits 0
- Baseline screenshots captured
- Evidence: `reports/baseline-validation.txt`

---

## Phase 1 — Dashboard Layout Balance (All Deals Height)
**Complexity:** S
**Estimated touch points:** 1 file

**Purpose:** Make the All Deals card extend to match the full height of the right-hand column stack.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/dashboard`
- **Downstream consumers:** None — layout-only change

### Tasks
- P1-01: **Restore `flex-1` on the All Deals Card** in `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - The Card wrapping the deals list must have `flex-1 flex flex-col` so it stretches to fill the left column height
  - Add `min-h-[300px]` to prevent collapse when deals list is empty
  - The left column `<div>` must have `flex flex-col` (already has it) to allow flex-1 to work
  - Evidence: inspect the Card element's className
  - **Checkpoint:** After this task, verify the Card stretches to at least the height of the right column in a 1280x720 viewport

- P1-02: **Ensure ScrollArea fills the Card** — The `ScrollArea` inside the Card must use `flex-1` height (not a fixed `max-h`) so it expands with the Card
  - Change the `CardContent` to `flex-1 min-h-0 flex flex-col`
  - Change the `ScrollArea` to `flex-1` (remove the `max-h-[60vh]` cap — the Card's grid-constrained height is the natural limit)
  - Evidence: ScrollArea should fill the entire Card content area

- P1-03: **Verify empty state** — When no deals exist, the empty state (IconBox + "No deals found") must still render properly within the `min-h-[300px]` constraint
  - Evidence: Playwright screenshot of dashboard with no deals filter applied should show balanced layout

### Rollback Plan
1. Revert changes to `dashboard/page.tsx`
2. Verify: `make validate-local` passes

### Gate P1
- Dashboard screenshot at 1280x720 shows: left column (Pipeline + All Deals) matches right column height — no large empty gap
- All Deals card is internally scrollable when content exceeds visible area
- Empty state renders cleanly
- `npx tsc --noEmit` passes

---

## Phase 2 — Chat History Actions (5 Actions)
**Complexity:** L
**Estimated touch points:** 3 files

**Purpose:** Add Delete (with confirmation), Rename, Pin/Unpin, Duplicate, and Archive actions to each chat history entry.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/chat`
- **Downstream consumers:** Chat page (`handleLoadFromHistory`), localStorage chat data

### Tasks

#### Data Model Extension
- P2-01: **Extend ChatSessionSummary** in `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/chat/chat-history.ts`
  - Add optional fields: `title?: string` (for rename), `pinned?: boolean` (for pin), `archived?: boolean` (for soft archive)
  - These fields MUST be optional to preserve backward compatibility with existing localStorage data
  - Evidence: type definition includes new fields
  - **Checkpoint:** Existing `getSessionHistory()` still returns valid data after model change (missing fields default to `undefined`/`false`)

#### Storage Operations
- P2-02: **Add new operations** to `chat-history.ts`:
  - `renameSession(sessionId: string, newTitle: string): void` — updates the `title` field in history
  - `togglePinSession(sessionId: string): void` — toggles `pinned` boolean
  - `duplicateSession(sessionId: string): string` — clones both summary and data blob, returns new ID
  - `archiveSessionEntry(sessionId: string): void` — sets `archived: true` (soft delete — data preserved)
  - `getSessionHistory()` must now filter out `archived: true` entries by default
  - Add `getArchivedSessions(): ChatSessionSummary[]` to retrieve archived entries
  - Evidence: all functions exported and callable
  - **Checkpoint:** Write to localStorage and read back — all operations round-trip correctly

#### Sort Order
- P2-03: **Update sort order in getSessionHistory** — Pinned sessions sort first (by `lastActive` descending), then unpinned (by `lastActive` descending)
  - Evidence: pinned session always appears at top of returned array

#### UI — Three-Dot Action Menu
- P2-04: **Add action menu to ChatHistoryRail** in `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx`
  - Each session item gets a three-dot (`IconDots`) button that appears on hover (alongside the existing delete icon — replace the standalone delete icon with the menu)
  - Menu uses `DropdownMenu` from shadcn/ui with 5 items:
    1. **Rename** (IconPencil) — opens inline edit (Input field replaces preview text, Enter to save, Escape to cancel)
    2. **Pin / Unpin** (IconPin / IconPinOff) — toggles immediately, re-sorts list
    3. **Duplicate** (IconCopy) — creates copy, shows at top of list
    4. **Archive** (IconArchive) — hides from list with brief toast confirmation
    5. **Delete** (IconTrash, text-destructive) — shows AlertDialog confirmation before removing
  - Pinned sessions show a pin icon indicator next to the timestamp
  - Sessions with custom `title` show the title instead of the `preview` text
  - Evidence: all 5 menu items visible on hover
  - **Checkpoint:** Each action updates localStorage and UI immediately

#### Confirmation Dialog
- P2-05: **Add delete confirmation using AlertDialog** from shadcn/ui
  - Dialog shows: "Delete this chat?" with session preview text
  - Two buttons: "Cancel" (closes dialog) and "Delete" (executes deletion)
  - After deletion, toast notification confirms removal
  - Evidence: clicking Delete shows dialog, confirming removes entry
  - **Checkpoint:** Verify no React hydration errors in console after all interactions

#### Inline Rename
- P2-06: **Implement inline rename editing**
  - When "Rename" is selected, the preview text becomes an Input field
  - Pre-filled with current `title || preview`
  - Enter saves, Escape cancels
  - Input has `autoFocus` and `onBlur` cancels if no Enter was pressed
  - Evidence: rename persists after page refresh (stored in localStorage)

### Decision Tree
- **IF** AlertDialog component is not yet available in the project → install it via shadcn CLI (`npx shadcn@latest add alert-dialog`)
- **IF** existing delete icon button is referenced in E2E tests → update test selectors to use the new menu approach

### Rollback Plan
1. Revert changes to `chat-history.ts`, `ChatHistoryRail.tsx`
2. Existing localStorage data remains valid (new fields are optional)
3. Verify: `make validate-local` passes

### Gate P2
- All 5 actions work: Delete (with confirmation), Rename (inline), Pin (sorts to top), Duplicate (new entry), Archive (hides)
- No React hydration warnings in console
- No chat duplication regression (clicking same history item repeatedly creates no duplicates)
- Pinned sessions appear first in the list
- Renamed sessions show custom title
- Archived sessions are hidden from the default list
- `npx tsc --noEmit` passes

---

## Phase 3 — Settings Visual Consistency
**Complexity:** S
**Estimated touch points:** 1 file

**Purpose:** Make all sidebar navigation items share uniform card container styling.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/settings`
- **Downstream consumers:** None — CSS-only change

### Tasks
- P3-01: **Verify current SettingsNav structure** in `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx`
  - The desktop nav already has `rounded-lg border border-border/60 bg-card p-2` on the container `<div>` wrapping all items (line 60)
  - All items are inside this single container — there should be no visual inconsistency
  - If the user sees AI Provider styled differently, it may be because it has the `isActive` state (bg-primary/10 + border-l-[3px]) while others don't
  - Evidence: screenshot showing all items have identical base styling

- P3-02: **Refine active vs. inactive contrast** if needed
  - Ensure inactive items have a subtle hover state (`hover:bg-accent/50`) that's visibly distinct from the background
  - Active item indicator (left border + background) should be visible but not dominating
  - Ensure the container padding and item padding are consistent
  - Evidence: screenshot comparison showing hover states

### Rollback Plan
1. Revert SettingsNav.tsx
2. Verify: `make validate-local` passes

### Gate P3
- Desktop screenshot: all 6 nav items have consistent visual treatment inside one unified card
- Active item has clear but balanced highlight
- Hover state is visible on all inactive items
- `npx tsc --noEmit` passes

---

## Phase 4 — Settings Performance Investigation
**Complexity:** M
**Estimated touch points:** 2–4 files

**Purpose:** Identify and resolve slow load of Settings page compared to other tabs.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/settings`
- **Downstream consumers:** React Query cache behavior (scoped to settings queries only)

### Tasks
- P4-01: **Profile the Settings page load** — Add temporary `console.time`/`console.timeEnd` markers in the `useUserPreferences` hook and the `ProviderSection` component to identify the bottleneck
  - Measure: API call duration, component render time, initial loading state duration
  - Evidence: console output showing timing breakdown

- P4-02: **Check React Query configuration** for settings-specific queries
  - The global `staleTime` is 30s with `refetchOnMount: true` — this means every navigation to Settings triggers a re-fetch
  - If preferences rarely change, consider increasing `staleTime` for preferences query specifically (e.g., 5 minutes)
  - Evidence: network tab showing reduced API calls on re-navigation

- P4-03: **Check for blocking fetches** — If `useUserPreferences` is the only data source and it returns quickly, the issue may be in the ProviderSection (which reads from localStorage) or component mount cascade
  - Decision tree:
    - **IF** API call is slow (>500ms) → investigate backend `/api/settings/preferences` route
    - **IF** API returns 404 (common — backend may not implement this) → ensure fallback defaults load instantly without waiting for the network timeout
    - **IF** component render is slow → check for unnecessary re-renders in section components
  - Evidence: identify the specific bottleneck with timing data

- P4-04: **Apply fix based on findings** — Implement the appropriate optimization:
  - Fast API call with long staleTime: reduce unnecessary refetches
  - 404 fallback: return defaults immediately, skip network call
  - Component optimization: memoize heavy sections
  - Evidence: before/after load time comparison

- P4-05: **Remove temporary timing markers** — Clean up any `console.time` calls added in P4-01

### Rollback Plan
1. Revert changes to hook and component files
2. Verify: `make validate-local` passes

### Gate P4
- Settings page loads perceptibly faster (or at parity with Dashboard)
- No React Query cache behavior changes on other pages
- `npx tsc --noEmit` passes

---

## Phase 5 — Final Verification & Bookkeeping
**Complexity:** S
**Estimated touch points:** 1 file

**Purpose:** Run full validation, capture evidence, update change log.

### Tasks
- P5-01: **Run `make validate-local`** — must pass 14/14 surfaces
- P5-02: **Run `npx tsc --noEmit`** — must compile clean
- P5-03: **Browser verification** — Playwright screenshots of:
  - Dashboard at 1280x720 showing balanced column heights
  - Chat page with history rail showing action menu
  - Settings page at 1280x720 showing consistent nav
- P5-04: **Update CHANGES.md** at `/home/zaks/bookkeeping/CHANGES.md`
- P5-05: **Write completion summary** to `/home/zaks/bookkeeping/missions/r5-polish-artifacts/reports/completion-summary.md`

### Gate P5
- `make validate-local` exits 0
- All screenshots captured
- CHANGES.md updated
- Completion summary written

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ├──────────────┬──────────────┐
    ▼              ▼              ▼
Phase 1        Phase 2        Phase 3 ──► Phase 4
(Layout)    (Chat Actions)  (Settings     (Settings
                             Visual)       Perf)
    │              │              │              │
    └──────────────┴──────┬───────┴──────────────┘
                          ▼
                   Phase 5 (Final Verification)
```

Phases 1, 2, and 3 can execute in parallel. Phase 4 depends on Phase 3 (same file area). Phase 5 depends on all prior phases.

---

## Acceptance Criteria

### AC-1: Dashboard Layout Balance
The All Deals card extends vertically to match the right-hand column stack (Quarantine + Alerts). No large empty space in the center-left of the dashboard at 1280x720 viewport.

### AC-2: Chat Delete with Confirmation
Each chat history entry can be deleted. A confirmation dialog appears before deletion. Deletion persists in localStorage.

### AC-3: Chat Rename
Each chat history entry can be renamed via inline edit. Custom title is displayed instead of preview text. Rename persists across page refreshes.

### AC-4: Chat Pin/Unpin
Pinned chats sort to the top of the history rail. A visual indicator (icon) marks pinned entries. Toggle is immediate.

### AC-5: Chat Duplicate
Duplicating a chat creates a new entry with copied metadata and message data. The new entry appears at the top of the list.

### AC-6: Chat Archive
Archiving a chat hides it from the default history list. Data is preserved (soft delete). Archived chats do not appear in the active history view.

### AC-7: Settings Visual Consistency
All 6 sidebar navigation items share identical base styling within one unified card container. Active/inactive states are visually distinct and consistent.

### AC-8: Settings Performance
Settings page load time is comparable to Dashboard or other tabs. No unnecessary re-fetches on navigation.

### AC-9: No Regressions
`make validate-local` passes (14/14 surfaces). TypeScript compiles clean. No new React hydration warnings. Chat duplication fix still works. All prior P4-STABILIZE fixes remain intact.

### AC-10: Bookkeeping
CHANGES.md updated with all modifications. Completion summary produced with evidence paths for every AC.

---

## Guardrails

1. **Scope fence** — This mission covers layout, chat history actions, settings visual/perf. Do NOT add new API endpoints, modify backend code, or change database schemas.
2. **Generated file protection** — Do not modify `*.generated.ts` or `*_models.py`. Use bridge files per contract surface discipline.
3. **localStorage backward compatibility** — New fields added to `ChatSessionSummary` MUST be optional. Existing stored data must load without errors.
4. **No global React Query changes** — Settings performance optimizations must be scoped to settings-specific queries. Do not change the global `QueryClient` defaults.
5. **Surface 9 compliance** — Per `.claude/rules/design-system.md`
6. **WSL safety** — Strip CRLF from any new `.sh` files. Fix ownership for files under `/home/zaks/`.
7. **shadcn/ui components only** — Use existing primitives (DropdownMenu, AlertDialog, Input, Badge, etc.). No new UI libraries.
8. **Port 8090 FORBIDDEN** — Never reference.
9. **Pre-task protocol** — Run `make validate-local` before starting work.
10. **Chat duplication guard** — The `loadedHistoryIdRef` / `messageCountAtLoadRef` pattern from the post-QA fix must NOT be regressed by Phase 2 changes.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I capture baseline screenshots for before/after comparison?"
- [ ] "Did I verify the ChatSessionSummary data model matches what's in the code?"

### After every code change:
- [ ] "Did I check that existing localStorage data still loads without errors?"
- [ ] "Is the UI change visible in both mobile and desktop viewports?"
- [ ] "Did I test the empty state (no deals, no history) alongside the populated state?"

### Before marking Phase 2 COMPLETE:
- [ ] "Do all 5 actions work: Delete, Rename, Pin, Duplicate, Archive?"
- [ ] "Did I test: click same history item 5 times — no duplicates?"
- [ ] "Are there any React hydration warnings in the console?"
- [ ] "Does renamed/pinned/archived state persist after page refresh?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now, not 3 phases ago?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce a completion summary with evidence paths for every AC?"
- [ ] "Did I remove any temporary `console.time` debug markers from Phase 4?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx` | 1 | Restore flex-1 on deals card, adjust ScrollArea height |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/chat/chat-history.ts` | 2 | Extend data model, add 5 new operations |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx` | 2 | Three-dot menu, inline rename, pin indicator, confirmation dialog |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx` | 3 | Refine hover/active states if needed |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useUserPreferences.ts` | 4 | Optimize query staleTime/fallback |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/r5-polish-artifacts/reports/baseline-validation.txt` | 0 | Baseline validation evidence |
| `/home/zaks/bookkeeping/missions/r5-polish-artifacts/reports/completion-summary.md` | 5 | Final completion report |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx` | Chat page integration with history (loadedHistoryIdRef pattern) |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/types/execution-contracts.ts` | Stage config source of truth |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx` | Global React Query config (do not change) |
| `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` | Surface 9 rules |

---

## Stop Condition

This mission is DONE when:
- All 10 acceptance criteria are met
- `make validate-local` passes (14/14 surfaces)
- TypeScript compiles clean
- All changes committed
- Completion summary written to `/home/zaks/bookkeeping/missions/r5-polish-artifacts/reports/completion-summary.md`
- CHANGES.md updated

Do NOT proceed to:
- Backend API changes for chat history persistence
- New page routes or navigation restructuring
- Database schema modifications
- Agent API changes

---

*End of Mission Prompt — DASHBOARD-R5-POLISH-001*
