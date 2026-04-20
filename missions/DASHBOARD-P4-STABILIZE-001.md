# MISSION: DASHBOARD-P4-STABILIZE-001
## Dashboard Phase 4 Stabilization — Functional Completeness, Performance, and UX Closure
## Date: 2026-02-11
## Classification: Platform Stabilization
## Prerequisite: UI-MASTERPLAN Phase 3 complete (M-01 through M-12 closed, commit fc5e39d on fix/full-remediation-001)
## Successor: QA-P4S-VERIFY-001 (paired QA verification)

---

## Mission Objective

This mission remediates **15 confirmed findings** from an independent UI testing session conducted on 2026-02-11. The testing covered all major dashboard pages (Dashboard, Deals, Chat, Settings) at desktop resolution and identified critical functional gaps, performance bottlenecks, and UX regressions.

This is a **STABILIZATION mission**, not a feature-build mission. Every fix targets an existing component that is broken, incomplete, or degraded. No new pages, no new API endpoints, no new database tables.

**Source material:**
- Independent screenshot review: `/mnt/c/Users/mzsai/Downloads/Dash-sreenshots-1/` (13 screenshots)
- Code investigation results from 4 parallel exploration agents (Chat, Settings, Dashboard, Board+Performance)
- Prior deliverables: UI Masterplan M-01 through M-12 artifacts at `/home/zaks/bookkeeping/missions/`

**What this mission is NOT:**
- Not a mobile/responsive pass (that was Phases 2-3)
- Not adding new features or pages
- Not modifying backend Python code (all fixes are dashboard-side)
- Not touching generated files or contract surfaces

<!-- Adopted from Improvement Area IA-2 -->
## Crash Recovery Protocol

If resuming after a crash, run these commands to determine current state:
1. `git log --oneline -5` — check which phases were committed
2. `make validate-local` — verify codebase integrity
3. `ls /home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/` — check for partial evidence files

---

## Context

### 15 Confirmed Findings

| # | Finding | Page | Severity | Phase |
|---|---------|------|----------|-------|
| F-1 | Chat: `<button>` nested inside `<button>` causes hydration errors (2 console errors) | Chat | High | 1 |
| F-2 | Chat: Clicking history items creates duplicate entries (no dedup in archiving) | Chat | Critical | 1 |
| F-3 | Chat: History entries lack visual separation (no dividers, no cards) | Chat | Medium | 1 |
| F-4 | Performance: React Query global staleTime (5min) conflicts with per-hook staleTime (30s) | All | High | 2 |
| F-5 | Performance: Double proxy — next.config.ts rewrites AND middleware both proxy `/api/*` | All | Medium | 2 |
| F-6 | Performance: Timeout mismatch — middleware 30s vs backend-fetch 15s | All | Medium | 2 |
| F-7 | Dashboard: "Today / Next Up" items redirect to "Invalid Deal ID" error page | Dashboard | Critical | 3 |
| F-8 | Dashboard: Deal count inconsistency (8 vs 9) from client-side `.length` + race conditions | Dashboard | High | 3 |
| F-9 | Dashboard: All Deals container capped at `max-h-[500px]`, doesn't fill available space | Dashboard | Medium | 3 |
| F-10 | Dashboard: Pipeline shows "0 active deals, 0 stages" when API fails silently | Dashboard | High | 3 |
| F-11 | Dashboard: Alerts section not clickable (no onClick, no Link, no cursor) | Dashboard | Medium | 3 |
| F-12 | Deals: Board view cards not clickable (DealCard missing onClick handler) | Deals | High | 4 |
| F-13 | Deals: Board drag-and-drop wired but not functional (needs live verification) | Deals | Medium | 4 |
| F-14 | Settings: Page not scrollable, back arrow moves out of view | Settings | High | 5 |
| F-15 | Settings: Nav items lack visual container separation | Settings | Medium | 5 |

### Environment State

- Dashboard: Next.js bare (NOT Docker), port 3003
- Backend: FastAPI, port 8091 (Postgres container frequently restarts — `--no-deps` pattern)
- React Query: `@tanstack/react-query` with global provider in `providers.tsx`
- Board library: `@hello-pangea/dnd` (fork of react-beautiful-dnd)
- Chat history: localStorage-backed via `chat-history.ts` (96 lines, max 20 sessions)

### Prior Deliverables That Must Not Regress

- M-04 Chat responsive toolbar (DropdownMenu + Sheet mobile pattern)
- M-05 through M-10 page-by-page responsive fixes
- M-11 cross-page integration (26/26 journey steps)
- M-12 accessibility sweep (0 high-severity blockers)
- Shared state primitives: `error-boundary.tsx`, `page-loading.tsx`, `empty-state.tsx`
- All 29 E2E test files in `apps/dashboard/tests/e2e/`

---

## Glossary

| Term | Definition |
|------|-----------|
| Hydration error | React SSR/client mismatch — server-rendered HTML differs from client-side virtual DOM, causing console errors and broken interactivity |
| staleTime | React Query setting — how long cached data is considered "fresh" before triggering a background refetch |
| gcTime | React Query setting — how long unused/inactive cache entries are kept in memory before garbage collection |
| Double proxy | When an API request passes through both `next.config.ts` rewrites AND `middleware.ts` proxy, adding latency |
| archiveSession | Function in `chat-history.ts` that saves current chat session to localStorage history array |

---

## Architectural Constraints

- **`Promise.allSettled` mandatory** — `Promise.all` is banned in dashboard data-fetching. Every multi-fetch uses `Promise.allSettled` with typed empty fallbacks.
- **Server-side counts** — Deal counts must come from API response totals, not client-side `.length` on fetched arrays.
- **Middleware proxy pattern** — All `/api/*` requests proxy through middleware returning JSON 502 on backend failure, never HTML 500.
- **Surface 9 compliance** — `console.warn` for expected degradation (backend down, timeout), `console.error` only for genuinely unexpected failures.
- **`PIPELINE_STAGES` source of truth** — Stage definitions come from `execution-contracts.ts`, not hardcoded.
- **Port 8090 FORBIDDEN** — Legacy, decommissioned.
- **Contract surface discipline** — Generated files never edited. No `make sync-*` required for this mission (no API boundary changes).

---

## Anti-Pattern Examples

### WRONG: Nested interactive elements (F-1)
```html
<button onClick={selectSession}>          <!-- outer button -->
  <Button onClick={deleteSession}>        <!-- inner button — HYDRATION ERROR -->
    <TrashIcon />
  </Button>
</button>
```

### RIGHT: Container div with keyboard accessibility
```html
<div role="button" tabIndex={0} onClick={selectSession} onKeyDown={handleKeyDown}>
  <Button onClick={(e) => { e.stopPropagation(); deleteSession(); }}>
    <TrashIcon />
  </Button>
</div>
```

### WRONG: Client-side deal counting (F-8)
```tsx
<span>{filteredDeals.length} deals</span>  // counts only fetched page
```

### RIGHT: Server-side count with client fallback
```tsx
<span>{pipelineData?.total_active ?? serverDealCount} deals</span>  // server-computed
```

### WRONG: Silent null return on API failure (F-10)
```tsx
export async function getPipeline() {
  try { ... } catch { return null; }  // caller has no idea why it's null
}
```

### RIGHT: Fallback with degradation signal
```tsx
export async function getPipeline() {
  try { ... } catch (err) {
    console.warn('Pipeline API unavailable — using deal-derived counts');
    return derivePipelineFromDeals(deals);  // compute from available data
  }
}
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Settings scroll fix breaks the existing responsive layout from M-10 | HIGH | Mobile settings unusable | Phase 5 gate requires responsive check at 375/768/1280px |
| 2 | React Query cache changes cause aggressive refetching, increasing backend load | MEDIUM | Performance regresses differently | Phase 2 gate: measure page load with DevTools before/after |
| 3 | Deal ID validation fix is too permissive, allowing SQL injection via crafted deal IDs | MEDIUM | Security vulnerability | Phase 3: validation must remain strict — accept alphanumeric but reject special chars |
| 4 | Chat history dedup fix loses legitimate distinct sessions that share the same first message | MEDIUM | Data loss | Phase 1: dedup by session ID, not by message content |
| 5 | Removing next.config.ts rewrites breaks a route that middleware doesn't handle | MEDIUM | API calls fail on specific endpoints | Phase 2: audit ALL `/api/*` routes before removing rewrite |

---

<!-- Adopted from Improvement Area IA-1 -->
## Context Checkpoint

This mission has 7 phases (0-6). If context becomes constrained after Phase 3, summarize progress, commit intermediate work, and continue in a fresh session using the Crash Recovery Protocol above.

---

## Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 files (read-only)

**Purpose:** Verify all 15 findings are still current and capture baseline validation state.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Run baseline validation** — `make validate-local` and `npx tsc --noEmit`
  - Evidence: capture output to `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/baseline-validation.txt`
  - **Checkpoint:** Both commands must pass before proceeding

- P0-02: **Verify all 15 findings** — Read each file from the findings table and confirm the problematic code is still present at the reported line numbers
  - Files to verify: `ChatHistoryRail.tsx:86,99`, `chat/page.tsx:826-847`, `settings/page.tsx:97,100-106`, `dashboard/page.tsx:288,396-427`, `DealBoard.tsx:41-96`, `providers.tsx:9-20`, `middleware.ts:29`, `backend-fetch.ts:9`, `next.config.ts:27-35`, `deals/[id]/page.tsx:84-90`
  - Evidence: produce `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/findings-verification.md` with CONFIRMED/CHANGED status for each finding

- P0-03: **Capture screenshot evidence baseline** — Note which console errors are present at baseline
  - Evidence: document in findings-verification.md

### Decision Tree
- **IF** a finding has been fixed since the investigation → Mark as RESOLVED, remove from scope, reduce AC count accordingly
- **ELSE IF** a finding has moved to different lines → Update line references, proceed with fix
- **ELSE** → Proceed as planned

### Rollback Plan
No rollback needed — this phase is read-only and produces only evidence files.

### Gate P0
- `make validate-local` passes at baseline
- All 15 findings verified as CONFIRMED or line-adjusted
- Evidence files created in `p4-stabilize-artifacts/reports/`

---

## Phase 1 — Chat Page Critical Fixes
**Complexity:** M
**Estimated touch points:** 2-3 files

**Purpose:** Eliminate hydration errors, fix history duplication, and improve history visual quality. (F-1, F-2, F-3)

### Blast Radius
- **Services affected:** Dashboard only
- **Pages affected:** `/chat`
- **Downstream consumers:** Chat E2E tests (`chat-responsive-toolbar.spec.ts`, `chat-interaction-closure.spec.ts`, `chat-shared.spec.ts`)

### Tasks
- P1-01: **Fix nested button hydration error** — Refactor `ChatHistoryRail.tsx` to eliminate `<button>` inside `<button>` at lines 86 and 99. The outer element should become a non-button interactive element (div with role="button" and keyboard handling), OR the inner delete button should use a different semantic approach. The key constraint: both click-to-select and click-to-delete must remain functional with proper event propagation (`stopPropagation` on delete).
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx`
  - **Checkpoint:** Open `/chat` in browser — "2 Issues" badge should disappear, 0 console errors

- P1-02: **Fix history duplication** — The `handleLoadFromHistory` function at `chat/page.tsx:826-847` must not re-archive the current session when selecting the same session. Guard against re-archiving by comparing session IDs before archiving. Additionally, the `archiveSession` function in `chat-history.ts` must deduplicate by session ID — if a session with the same ID already exists in history, update its metadata instead of appending a duplicate.
  - Files: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx`, `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/chat/chat-history.ts`
  - **Checkpoint:** Click the same history item 5 times — history count must not increase

- P1-03: **Add visual separation to history entries** — History items need clear visual boundaries (borders, card-like containers, or dividers between entries). Reference: ChatGPT and Claude interfaces use grouped entries with clear separation. Add subtle borders or card styling to each session item in the history rail.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx`
  - **Checkpoint:** History entries visually distinct at all breakpoints

### Rollback Plan
1. `git checkout -- apps/dashboard/src/components/chat/ChatHistoryRail.tsx apps/dashboard/src/app/chat/page.tsx apps/dashboard/src/lib/chat/chat-history.ts`
2. Verify: `make validate-local` passes after rollback

### Gate P1
- 0 hydration errors in browser console on `/chat` page
- Clicking same history item 5x produces no duplicates
- History entries have visible separation (borders/cards)
- `npx tsc --noEmit` passes
- Existing chat E2E tests still pass structurally (test file syntax valid)

---

## Phase 2 — Performance Stabilization
**Complexity:** M
**Estimated touch points:** 3-4 files

**Purpose:** Eliminate the systemic performance bottleneck causing 60+ second page loads. (F-4, F-5, F-6)

### Blast Radius
- **Services affected:** Dashboard (all pages — this is global config)
- **Pages affected:** Every dashboard page
- **Downstream consumers:** All API client hooks in `api-client.ts`

### Tasks
- P2-01: **Align React Query cache configuration** — The global `staleTime: 5 * 60 * 1000` (5 minutes) in `providers.tsx:12` conflicts with per-hook stale times (e.g., `useDeals` at 30s, `useHealth` at 5s). Reduce the global `staleTime` to a sensible default (e.g., 60 seconds) and reduce `gcTime` proportionally. Per-hook overrides remain authoritative.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx`
  - **Checkpoint:** React Query Devtools shows consistent stale/fresh status

- P2-02: **Remove redundant rewrite proxy** — The `next.config.ts` rewrites at lines 27-35 AND `middleware.ts` both proxy `/api/*` requests. This creates a double-proxy path for some requests. Audit ALL `/api/*` routes first to confirm middleware handles them all, then remove the `next.config.ts` rewrite. If any route is NOT handled by middleware, add it to middleware rather than keeping the rewrite.
  - Files: `/home/zaks/zakops-agent-api/apps/dashboard/next.config.ts`, `/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts`
  - **Checkpoint:** All `/api/*` calls work after rewrite removal (test `/api/deals`, `/api/pipeline`, `/api/chat`)

- P2-03: **Align timeout configuration** — Middleware uses `PROXY_TIMEOUT_MS = 30000` (line 29) while backend-fetch uses `DEFAULT_TIMEOUT_MS = 15000` (line 9). Unify to a single source of truth — both should read from the same env var with the same default. Recommended: 15 seconds for both (30s is too long for UI responsiveness).
  - Files: `/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts`, `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/backend-fetch.ts`
  - **Checkpoint:** Both files resolve to same timeout value

### Decision Tree
- **IF** removing next.config.ts rewrite breaks a specific API route → Add that route to middleware's explicit handler list instead of reverting the rewrite
- **ELSE IF** all routes work through middleware → Remove rewrite completely
- **ELSE** → Keep rewrite only for the specific broken routes, document why

### Rollback Plan
1. `git checkout -- apps/dashboard/next.config.ts apps/dashboard/src/middleware.ts apps/dashboard/src/lib/backend-fetch.ts apps/dashboard/src/components/layout/providers.tsx`
2. Verify: `make validate-local` passes

### Gate P2
- Global staleTime < 120 seconds
- Only ONE proxy path for `/api/*` requests (rewrite removed OR middleware removed — not both)
- Timeout values consistent between middleware and backend-fetch
- `make validate-local` passes
- Page load time subjectively improved (no 60+ second waits)

---

## Phase 3 — Dashboard Data & Layout Fixes
**Complexity:** L
**Estimated touch points:** 3-5 files

**Purpose:** Fix all dashboard-specific functional and display issues. (F-7, F-8, F-9, F-10, F-11)

### Blast Radius
- **Services affected:** Dashboard
- **Pages affected:** `/dashboard`, `/deals/[id]`
- **Downstream consumers:** Dashboard E2E tests, TodayNextUpStrip component

### Tasks
- P3-01: **Fix deal ID validation** — The regex at `deals/[id]/page.tsx:84-90` rejects alphanumeric deal IDs like `DL-IDEM2` because it only accepts digits after the `DL-` prefix. Expand the validation to accept alphanumeric characters in the deal ID suffix while maintaining UUID acceptance and rejecting special characters for security.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx`
  - **Checkpoint:** Navigate to `/deals/DL-IDEM2` — should show deal detail (or proper "not found" if deal doesn't exist in DB), NOT "Invalid Deal ID"

- P3-02: **Fix deal count display** — Replace client-side `filteredDeals.length` counting at `dashboard/page.tsx:275` with server-side count from `pipelineData?.total_active` or API response total. The display should show the server-provided count, falling back to array length only when the server count is unavailable.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - **Checkpoint:** Deal count stable across refreshes (no flickering between 8 and 9)

- P3-03: **Fix All Deals container height** — Remove or increase the `max-h-[500px]` constraint on the ScrollArea at `dashboard/page.tsx:288`. The container should grow to fill available viewport space. Use a calc-based max-height or remove the cap entirely and let the parent flex container control height.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - **Checkpoint:** All Deals section extends to fill available vertical space, scrollbar appears only when content exceeds visible area

- P3-04: **Fix Pipeline section** — When `getPipeline()` returns null (API failure), derive pipeline data from the `deals` array instead of showing "0 active deals, 0 stages". Count deals per stage using `PIPELINE_STAGES` from `execution-contracts.ts`. Display a degradation indicator (per Surface 9: `console.warn`, not `console.error`).
  - Files: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`, potentially `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts`
  - **Checkpoint:** Pipeline shows correct stage counts even when `/api/pipeline` endpoint is down

- P3-05: **Wire alerts with click handlers** — Alert items at `dashboard/page.tsx:395-427` need click behavior. For alerts with `deal_id`, navigate to `/deals/{deal_id}`. For alerts with type `stale_deals`, navigate to `/deals?sort=last_updated`. Add `cursor-pointer` and `hover:bg-accent` classes. If an alert has no actionable target, keep it as informational (no cursor change).
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - **Checkpoint:** Clicking "stale_deals" alert navigates to deals page

### Decision Tree
- **IF** `getPipeline()` returns valid data → Display as-is (current behavior is correct)
- **ELSE IF** `deals` array is available → Derive stage counts from deals using `PIPELINE_STAGES`
- **ELSE** → Show "Pipeline data unavailable" with retry button (not "0 stages")

### Rollback Plan
1. `git checkout -- apps/dashboard/src/app/dashboard/page.tsx apps/dashboard/src/app/deals/[id]/page.tsx apps/dashboard/src/lib/api.ts`
2. Verify: `make validate-local` passes

### Gate P3
- `/deals/DL-IDEM2` no longer shows "Invalid Deal ID" (shows deal or proper 404)
- Deal count stable across 5 consecutive auto-refreshes
- All Deals section fills available height (no premature cutoff)
- Pipeline shows non-zero counts when deals exist (even if pipeline API fails)
- At least one alert type is clickable with navigation
- `make validate-local` passes

---

## Phase 4 — Board View Interactivity
**Complexity:** S
**Estimated touch points:** 1-2 files

**Purpose:** Make board view deal cards clickable and verify drag-and-drop works. (F-12, F-13)

### Blast Radius
- **Services affected:** Dashboard
- **Pages affected:** `/deals?view=board`
- **Downstream consumers:** Board E2E tests (if any)

### Tasks
- P4-01: **Add onClick to DealCard** — The `DealCard` component at `DealBoard.tsx:41-96` has no navigation handler. Add `onClick` that navigates to `/deals/${deal.deal_id}` using `useRouter`. Ensure the click handler does NOT fire when dragging (check `snapshot.isDragging` from `@hello-pangea/dnd`).
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx`
  - **Checkpoint:** Click a board card → navigates to deal detail page

- P4-02: **Verify drag-and-drop** — The drag infrastructure (`DragDropContext`, `Droppable`, `Draggable`) is already wired. Test whether dragging actually works. If it doesn't, investigate whether the `onDragEnd` handler properly calls a backend API to update deal stage. If the backend endpoint doesn't exist, make the drag handler show a toast indicating the feature is not yet connected (degraded truthfully per Surface 9).
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx`
  - **Checkpoint:** Either drag works end-to-end, OR a truthful degradation message appears

### Decision Tree
- **IF** `onDragEnd` calls a backend API that exists and works → Drag-and-drop is functional, no changes needed
- **ELSE IF** `onDragEnd` calls a backend API that fails → Add error handling with toast notification
- **ELSE IF** `onDragEnd` only updates local state → Document as client-only behavior, add console.warn
- **ELSE** → Wire truthful degradation: "Stage changes via drag-and-drop coming soon"

### Rollback Plan
1. `git checkout -- apps/dashboard/src/components/deals/DealBoard.tsx`
2. Verify: `make validate-local` passes

### Gate P4
- Board cards are clickable — clicking navigates to deal detail
- Drag-and-drop either works or displays truthful degradation message
- Click does not fire during drag operations
- `npx tsc --noEmit` passes

---

## Phase 5 — Settings Page Remediation
**Complexity:** M
**Estimated touch points:** 2-3 files

**Purpose:** Fix scroll, back arrow, and visual container issues on Settings page. (F-14, F-15)

### Blast Radius
- **Services affected:** Dashboard
- **Pages affected:** `/settings`
- **Downstream consumers:** Settings E2E tests (`settings-mobile-layout-and-degraded-states.spec.ts`)

### Tasks
- P5-01: **Fix page scrolling** — The scroll container at `settings/page.tsx:97` has `overflow-y-auto` but the internal flex chain breaks the height constraint. Fix the height chain: ensure `min-h-0` propagates correctly through the flex containers at lines 97, 113, and 119. The page must scroll vertically when content exceeds viewport height.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
  - **Checkpoint:** Settings page scrolls when content exceeds viewport

- P5-02: **Fix back arrow** — The "Back to Dashboard" link at `settings/page.tsx:100-106` scrolls out of view when the user navigates into sub-sections. Make it sticky or move it outside the scrollable area. It must remain accessible at all scroll positions.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
  - **Checkpoint:** Back arrow visible and clickable after scrolling to any settings section

- P5-03: **Add visual containers to nav items** — The left sidebar navigation in `SettingsNav.tsx` has items with hover effects but no visual container boundaries. Add subtle card or border styling to each nav item to create clear visual separation, consistent with the Card-based section styling used in the main content area.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx`
  - **Checkpoint:** Nav items visually distinct with clear boundaries

### Rollback Plan
1. `git checkout -- apps/dashboard/src/app/settings/page.tsx apps/dashboard/src/components/settings/SettingsNav.tsx`
2. Verify: `make validate-local` passes

### Gate P5
- Settings page scrolls vertically
- Back arrow remains visible at all scroll positions
- Nav items have visual container separation
- Settings page renders correctly at 375px, 768px, and 1280px (no responsive regression from M-10)
- `make validate-local` passes

---

## Phase 6 — Tests & Final Validation
**Complexity:** M
**Estimated touch points:** 2-4 new test files

**Purpose:** Reinforce all fixes with E2E tests and run final validation sweep.

### Blast Radius
- **Services affected:** Dashboard (test files only)
- **Pages affected:** None (tests only)
- **Downstream consumers:** CI pipeline

### Tasks
- P6-01: **Create E2E test for chat history** — Playwright test covering: no hydration errors on load, no duplicate history entries on repeated click, visual separation present.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/chat-history-stability.spec.ts`
  - Test names must include functional keywords: "history", "duplicate", "hydration" (per IA-10)

- P6-02: **Create E2E test for board interactivity** — Playwright test covering: board cards clickable with navigation, drag handle visible.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/board-card-interactivity.spec.ts`
  - Test names must include: "board", "click", "navigate"

- P6-03: **Create E2E test for dashboard stability** — Playwright test covering: pipeline displays non-zero when deals exist, alerts have cursor-pointer, All Deals section extends vertically.
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/dashboard-data-stability.spec.ts`
  - Test names must include: "pipeline", "alerts", "deals"

- P6-04: **Run final validation sweep** — `make validate-local`, `npx tsc --noEmit`, verify 0 lint regressions
  - Evidence: `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/final-validation.txt`
  - **Checkpoint:** Both commands exit 0 with output captured to evidence file

- P6-05: **Produce completion summary** — Document all changes, AC status, and evidence paths
  - File: `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md`
  - **Checkpoint:** Summary contains a row for every AC (AC-1 through AC-9) with PASS/FAIL and evidence path

- P6-06: **Update bookkeeping** — Add entry to `/home/zaks/bookkeeping/CHANGES.md`
  - **Checkpoint:** CHANGES.md contains a dated entry referencing DASHBOARD-P4-STABILIZE-001

### Rollback Plan
1. `git checkout -- apps/dashboard/tests/e2e/chat-history-stability.spec.ts apps/dashboard/tests/e2e/board-card-interactivity.spec.ts apps/dashboard/tests/e2e/dashboard-data-stability.spec.ts`
2. Verify: `make validate-local` passes

### Gate P6
- 3 new E2E test files created with valid syntax (`npx tsc --noEmit` passes)
- `make validate-local` passes
- Completion summary produced with evidence paths for every AC
- CHANGES.md updated

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ├──────────────┬──────────────┐
    ▼              ▼              ▼
Phase 1        Phase 2        Phase 5
(Chat)         (Performance)  (Settings)
    │              │              │
    └──────┬───────┘              │
           ▼                      │
        Phase 3 ──────────────────┘
        (Dashboard)
           │
           ▼
        Phase 4
        (Board)
           │
           ▼
        Phase 6
        (Tests & Validation)
```

Phases 1, 2, and 5 can execute in parallel after Phase 0. Phase 3 depends on Phase 2 (cache/timeout fixes affect dashboard data loading). Phase 4 depends on Phase 3 (deal ID validation fix needed for board card navigation). Phase 6 runs last.

---

## Acceptance Criteria

### AC-1: Chat Hydration Errors Eliminated
0 console errors related to nested `<button>` elements on the `/chat` page. The "2 Issues" badge must not appear.

### AC-2: Chat History Deduplication
Clicking the same history item N times produces exactly 0 new duplicate entries. History entries have visible visual separation (borders, cards, or dividers).

### AC-3: Performance Measurably Improved
React Query global staleTime reduced from 5 minutes. Double proxy eliminated. Timeouts aligned. Page load time for `/dashboard` improved (no 60+ second waits).

### AC-4: Dashboard Data Accuracy
- "Today / Next Up" items navigate to valid deal pages (no "Invalid Deal ID" errors)
- Deal count stable across auto-refreshes
- Pipeline shows non-zero counts when deals exist
- All Deals section fills available viewport height

### AC-5: Dashboard Interactivity Complete
- Alerts with actionable data are clickable with navigation
- Board view cards navigate to deal detail on click
- Drag-and-drop either works or shows truthful degradation

### AC-6: Settings Page Fully Functional
- Page scrolls vertically
- Back arrow accessible at all scroll positions
- Nav items have visual container separation
- No responsive regressions at 375/768/1280px

### AC-7: Test Reinforcement
3 new E2E test files with functional keyword naming covering chat stability, board interactivity, and dashboard data accuracy.

### AC-8: Bookkeeping Complete
Completion summary with evidence paths for every AC. CHANGES.md updated. All changes committed.

### AC-9: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes. 0 new lint warnings. No responsive regressions from UI Masterplan Phases 2-3.

---

## Guardrails

1. **Scope fence:** Fix the 15 identified issues ONLY. Do not add new features, new pages, or new API endpoints.
2. **Generated files:** Do not modify `api-types.generated.ts` or `backend_models.py`. No `make sync-*` required.
3. **No backend changes:** All fixes are dashboard-side. Do not modify Python code in `zakops-backend` or `zakops-agent-api`.
4. **No migration changes:** Do not modify database migrations.
5. **Surface 9 compliance:** `console.warn` for degradation, `console.error` for unexpected. Per `.claude/rules/design-system.md`.
6. **WSL safety:** `sed -i 's/\r$//'` on any new .sh files. `sudo chown zaks:zaks` on files under `/home/zaks/`.
7. **Responsive preservation:** Every visual change must be verified at 375px, 768px, and 1280px to prevent regressing M-04 through M-10 work.
8. **Test naming:** E2E test descriptions must include functional keywords (per IA-10), not just finding IDs.
9. **Security:** Deal ID validation must remain strict — accept alphanumeric only, reject special characters, SQL injection patterns, and path traversal.
10. **Pre-task protocol:** Read CLAUDE.md, run `make infra-check` before starting.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify ALL 15 findings, or did I assume the investigation report is still accurate?"
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Are there any findings that were already fixed since the investigation?"

### After every code change:
- [ ] "Did I check this change at 375px, 768px, AND 1280px for responsive regressions?"
- [ ] "Am I using `console.warn` for expected degradation or `console.error` for unexpected?"
- [ ] "Does the deal ID validation remain secure (no special chars, no path traversal)?"

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks, or am I assuming they pass?"
- [ ] "Did I create new files? → CRLF stripped? Ownership fixed?"
- [ ] "Could this change affect other pages I haven't checked?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now, not 3 phases ago?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce a completion summary with evidence paths for every AC?"
- [ ] "Did I create ALL 3 test files listed in Phase 6?"
- [ ] "Do test names contain functional keywords (history, board, pipeline, alerts, deals)?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx` | 1 | Fix nested button, add visual separation |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx` | 1 | Fix history deduplication in handleLoadFromHistory |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/chat/chat-history.ts` | 1 | Add dedup logic to archiveSession |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/providers.tsx` | 2 | Reduce global staleTime and gcTime |
| `/home/zaks/zakops-agent-api/apps/dashboard/next.config.ts` | 2 | Remove redundant /api/* rewrite |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts` | 2 | Align timeout to 15s |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/backend-fetch.ts` | 2 | Align timeout source |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx` | 3 | Fix count, height, pipeline fallback, alerts |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | 3 | Fix deal ID validation regex |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx` | 4 | Add onClick to DealCard |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx` | 5 | Fix scroll, back arrow |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx` | 5 | Add visual containers |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/baseline-validation.txt` | 0 | Baseline validation evidence |
| `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/findings-verification.md` | 0 | Findings current-state verification |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/chat-history-stability.spec.ts` | 6 | Chat hydration + dedup tests |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/board-card-interactivity.spec.ts` | 6 | Board click + drag tests |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/dashboard-data-stability.spec.ts` | 6 | Pipeline + alerts + deals tests |
| `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/final-validation.txt` | 6 | Final validation evidence |
| `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md` | 6 | AC status + evidence paths |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/execution-contracts.ts` | PIPELINE_STAGES source of truth |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | API schemas (AlertSchema, PipelineStageSchema) |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts` | React Query hook staleTime overrides |
| `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` | Surface 9 design conventions |
| `/mnt/c/Users/mzsai/Downloads/Dash-sreenshots-1/` | Source screenshots for visual reference |

---

## Stop Condition

This mission is DONE when:
- All 9 acceptance criteria are met (AC-1 through AC-9)
- `make validate-local` passes
- All changes committed on branch `fix/full-remediation-001`
- Completion summary produced at `/home/zaks/bookkeeping/missions/p4-stabilize-artifacts/reports/completion-summary.md`
- CHANGES.md updated

Do NOT proceed to:
- QA verification (that is the successor mission QA-P4S-VERIFY-001)
- New feature development
- Backend modifications
- Mobile-specific testing beyond responsive regression checks

---

*End of Mission Prompt — DASHBOARD-P4-STABILIZE-001*
