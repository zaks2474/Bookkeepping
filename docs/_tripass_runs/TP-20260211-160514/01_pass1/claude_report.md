# Pass 1 Report — CLAUDE
## Run: TP-20260211-160514 | Mode: design
## Generated: 2026-02-11T16:05:17Z

---

## EXECUTIVE SUMMARY

The ZakOps dashboard is a substantial Next.js 15 application (~26,600 lines across 120+ component files, 12 pages, 31 API routes) built incrementally over multiple remediation waves. The codebase has strong architectural foundations — Zod validation, graceful degradation, typed bridge files, 14 contract surfaces — but exhibits the classic symptoms of rapid incremental construction: visual pattern divergence across pages, inconsistent loading/empty/error states, untested responsive breakpoints, and shared components that have grown organically without a unified visual language. **Strategy C (Hybrid)** is the correct approach, refined with specific findings from this investigation. The key insight: the cross-cutting foundation layer is thinner than expected (most shared components are already consistent via shadcn/ui), so the real work is in page-level polish and interaction wiring — making Phase 2 (page-by-page) the dominant effort, not Phase 1 (cross-cutting).

---

## PRIMARY FINDINGS

### Finding 1: Strategy C (Hybrid) Is Correct, But Phase Weights Must Be Rebalanced

**Root Cause:** The mission proposes three strategies. After investigating the codebase, Strategy C is clearly superior, but its proposed phase weighting (heavy Phase 1 cross-cutting) doesn't match the actual codebase state. The shadcn/ui foundation (`components/ui/`, 44 files, ~3,400 lines) already provides consistent primitives. The real inconsistencies are at the page composition layer, not the primitive layer.

**Fix Approach:** Adopt Strategy C with these adjustments:
- **Phase 0 (Recon):** Keep as-is — Playwright screenshots at 375/768/1280px of all 12 pages. This is non-negotiable. Produces the evidence catalog.
- **Phase 1 (Cross-Cutting):** Narrow scope. Focus on: (a) loading/empty/error state consistency, (b) responsive layout framework, (c) sidebar/header/navigation polish, (d) global CSS token audit. NOT a redesign of primitives.
- **Phase 2 (Page-by-Page):** Expand scope. This is the main event. 6-8 missions covering the 12 pages grouped by complexity and shared concerns.
- **Phase 3 (Integration Sweep):** Keep but add Playwright regression suite as a permanent gate.

**Industry Standard:** Progressive enhancement methodology (audit → foundation → page polish → integration) is the standard for large-scale UI remediation. See Google's Material Design migration guides and Shopify's Polaris migration playbook.

**System Fit:** ZakOps already has 14 contract surfaces, TriPass pipeline, and mission prompt standard v2.1. This strategy maps directly: Phase 0 = recon mission, Phase 1 = 2-3 build missions, Phase 2 = 6-8 build missions, Phase 3 = 1-2 QA missions. Total: 10-13 missions.

**Enforcement:** Each phase gate enforced by Playwright screenshot comparison + `make validate-local` + `npx tsc --noEmit`. Phase 3 produces a permanent E2E regression suite that prevents future degradation.

---

### Finding 2: Page Complexity Distribution Demands Specific Mission Sizing

**Root Cause:** Pages vary enormously in complexity, from 5 lines (home redirect) to 1,772 lines (chat). Treating all pages equally in mission scoping will either waste sessions on simple pages or under-scope complex ones.

Evidence from investigation:
- **Tier 1 (Complex, 1000+ lines):** Chat (1,772), Deal Workspace (1,422), Actions (1,286) — these each need a dedicated mission
- **Tier 2 (Medium, 500-999 lines):** Quarantine (789), Deals List (695), Agent Activity (657) — can be paired (2 per mission)
- **Tier 3 (Simple, <500 lines):** Dashboard (425), Settings (178), HQ (119), Onboarding (34), New Deal (124), UI Test (289) — can be grouped (3-4 per mission)

File evidence:
- `apps/dashboard/src/app/chat/page.tsx`: 1,772 lines — streaming SSE, provider selection, session management, evidence citations
- `apps/dashboard/src/app/deals/[id]/page.tsx`: 1,422 lines — 6-tab interface, transitions, notes, materials, case file, enrichment
- `apps/dashboard/src/app/actions/page.tsx`: 1,286 lines — real-time polling, bulk operations, metrics, schema-driven forms

**Fix Approach:** Mission inventory must respect this tiering:
- Tier 1 pages: 1 mission each (3 missions)
- Tier 2 pages: 2 missions (pair quarantine+deals-list, agent-activity solo or paired)
- Tier 3 pages: 1-2 missions (group dashboard+hq+onboarding, settings+new-deal)

**Industry Standard:** Agile story point estimation — complex pages get proportionally more effort allocation.

**System Fit:** Each mission must fit a single Claude Code session. Tier 1 pages at 1,200-1,800 lines with multiple sub-systems are at the limit of what a single session can audit + fix comprehensively. Splitting them further would lose context.

**Enforcement:** Mission prompt standard v2.1 requires scope declaration. Each mission states its page tier and expected line count to prevent scope creep.

---

### Finding 3: Loading/Empty/Error States Are the #1 Cross-Cutting Inconsistency

**Root Cause:** The component patterns rule (`.claude/rules/component-patterns.md`) mandates that "every data component must handle: loading, empty, error." Investigation reveals uneven implementation:

**Loading states:**
- 4 pages have explicit `loading.tsx` files: dashboard, quarantine, deals, hq
- 7 pages lack `loading.tsx`: chat, actions, agent-activity, settings, onboarding, deal-workspace, new-deal
- These pages use inline skeleton loaders of varying quality

**Error boundaries:**
- 11 error.tsx files exist (all 42 lines, identical template) — good coverage
- But they all use the same generic template. No page-specific error recovery guidance.

**Empty states:**
- No consistent `EmptyState` component found in shared components
- Each page handles "no data" differently — some show text, some show nothing

File evidence:
- `apps/dashboard/src/app/dashboard/loading.tsx` — exists
- `apps/dashboard/src/app/chat/` — no loading.tsx (inline skeletons in page.tsx)
- `apps/dashboard/src/app/actions/` — no loading.tsx (inline skeletons in page.tsx)
- `apps/dashboard/src/components/LoadingSkeleton.tsx`: 96 lines — generic skeleton, but not used universally
- All error.tsx files: identical 42-line template with Card + IconAlertTriangle + retry button

**Fix Approach:** Phase 1 should include:
1. Create a shared `EmptyState` component with variants (no-data, no-results, error-fallback)
2. Add `loading.tsx` to all pages that lack one, using consistent skeleton patterns
3. Enhance error.tsx templates with page-specific recovery guidance where appropriate
4. Audit inline skeleton usage across Tier 1 pages for consistency

**Industry Standard:** React Suspense boundaries with consistent fallback UIs. Vercel's Next.js docs recommend `loading.tsx` for every route segment.

**System Fit:** The `component-patterns.md` rule already mandates this. Implementation just needs to catch up. The `LoadingSkeleton.tsx` component (96 lines) exists but needs wider adoption.

**Enforcement:** Add a lint rule or E2E test that verifies every route directory contains `loading.tsx`. Add a Playwright test that navigates to each page with backend unavailable and verifies graceful empty states (extend `graceful-degradation.spec.ts`).

---

### Finding 4: Responsive Breakpoints Are Untested — Playwright MCP Is the Solution

**Root Cause:** The design system rule (`.claude/rules/design-system.md`, section C1) mandates testing at 375px, 768px, and 1280px. The E2E test suite has zero viewport-specific tests. No test resizes the browser. The Playwright MCP tools (`browser_resize`, `browser_take_screenshot`) exist but have never been used in any test file.

File evidence:
- `apps/dashboard/tests/e2e/` — 11 test files, zero use of `page.setViewportSize()`
- `.claude/rules/design-system.md` section A8: "Test at 375px, 768px, 1280px widths"
- `.claude/rules/design-system.md` section C1: "Mobile-first. Test at 375px, 768px, 1280px."
- No mobile-specific Tailwind classes verified in any test

**Fix Approach:**
- **Phase 0** must include Playwright screenshots at all 3 breakpoints for all 12 pages (36 screenshots minimum). This is the baseline catalog.
- **Phase 2** page missions must include viewport testing as a deliverable per page.
- **Phase 3** must produce a permanent responsive regression test that checks all pages at all breakpoints.

Playwright MCP integration strategy:
- `browser_navigate` + `browser_resize` + `browser_take_screenshot` = screenshot catalog
- `browser_snapshot` (accessibility tree) = semantic structure verification
- `browser_console_messages` = runtime error detection per breakpoint
- Save evidence to `/tmp/playwright-evidence/` as directed by design-system.md A8

**Industry Standard:** Visual regression testing (Chromatic, Percy, Playwright visual comparisons). Mobile-first responsive design requires explicit breakpoint testing.

**System Fit:** Playwright MCP is already declared as a first-class capability in the mission document. The 22 browser tools are available. This is the single biggest quality lever available.

**Enforcement:** Phase 3 produces a `responsive-regression.spec.ts` that runs `page.setViewportSize()` at 3 breakpoints per page and checks for overflow, layout collapse, and console errors.

---

### Finding 5: The API Client Layer Is Robust But Pages Bypass It Inconsistently

**Root Cause:** `apps/dashboard/src/lib/api.ts` (2,060 lines) is a comprehensive, well-structured API client with Zod validation, error normalization, correlation IDs, and idempotency keys. However, some pages and API route handlers use raw `fetch()` or `backendFetch()` directly instead of going through the centralized client.

File evidence:
- `apps/dashboard/src/lib/api.ts`: Centralized client, 2,060 lines, Zod-validated
- `apps/dashboard/src/lib/backend-fetch.ts`: Separate backend fetch utility (exists as modified file in git status)
- `apps/dashboard/src/lib/api-client.ts`: Yet another API client file (exists as modified in git status)
- `apps/dashboard/src/app/chat/page.tsx`: Uses `streamChatMessage` from api.ts but also has inline fetch logic for session restoration
- Multiple API route files under `src/app/api/` use `backendFetch()` directly

The existence of three separate fetch utilities (`api.ts`, `backend-fetch.ts`, `api-client.ts`) suggests layering that may not be fully rationalized.

**Fix Approach:** Phase 1 cross-cutting work should audit the three fetch layers:
1. `api.ts` — client-side API functions (primary)
2. `backend-fetch.ts` — server-side API route proxy functions
3. `api-client.ts` — unclear role, needs investigation

Ensure no page component calls `fetch()` directly. All data access must go through `api.ts` functions.

**Industry Standard:** Single data access layer pattern. One canonical way to call APIs prevents inconsistent error handling.

**System Fit:** The rule at `design-system.md` A6 already mandates "All /api/* through Next.js middleware proxy." The client layer just needs enforcement.

**Enforcement:** A grep-based CI check: `grep -r "fetch(" apps/dashboard/src/app/ --include="*.tsx" | grep -v "api.ts" | grep -v "import"` should return zero results outside of API route handlers.

---

### Finding 6: 11 Identical Error Boundaries Violate DRY — Shared Component Needed

**Root Cause:** Every route directory has an `error.tsx` file, and all 11 are identical 42-line copies of the same template. This is DRY violation that will drift over time as some get updated and others don't.

File evidence (all from `apps/dashboard/src/app/`):
- `error.tsx`, `actions/error.tsx`, `chat/error.tsx`, `agent/activity/error.tsx`, `settings/error.tsx`, `quarantine/error.tsx`, `hq/error.tsx`, `deals/error.tsx`, `deals/[id]/error.tsx`, `deals/new/error.tsx`, `onboarding/error.tsx`, `ui-test/error.tsx`
- All 42 lines, identical: Card + IconAlertTriangle + error.message + retry Button

**Fix Approach:** Create a shared `ErrorBoundaryUI` component in `components/` that accepts optional props for page-specific context (page name, suggested recovery action). Each `error.tsx` becomes a 5-line file importing the shared component.

**Industry Standard:** DRY principle. Shared error UI components. Next.js error boundary documentation recommends this pattern.

**System Fit:** The `ErrorBoundary.tsx` (77 lines) already exists in `components/` but is a React class component error boundary, not the Next.js `error.tsx` pattern. These are complementary: the class boundary catches render errors, the `error.tsx` catches route-level errors.

**Enforcement:** A file-size lint check: `error.tsx` files should be <15 lines (import + render shared component). Phase 1 deliverable.

---

### Finding 7: Design System Has Strong Rules But No Visual Enforcement Mechanism

**Root Cause:** The design system rule (`.claude/rules/design-system.md`) has 7 quality standards (B1-B7), 5 governance rules (C1-C5), and 7 architectural conventions (A1-A7). These are comprehensive. But the only enforcement is manual: the rule auto-loads when working on dashboard files, and TriPass triggers for 3+ component changes. There is no automated check that verifies visual consistency.

File evidence:
- `.claude/rules/design-system.md`: 500+ lines of rules
- `tools/infra/validate-surface9.sh`: Validates Surface 9 (design system) — but validates the contract metadata, not the visual output
- No visual regression tests exist
- No screenshot comparison baseline exists

**Fix Approach:** Phase 0 produces the screenshot baseline. Phase 3 produces the visual regression test suite. Between them:
- Phase 0: 36+ screenshots (12 pages x 3 breakpoints) saved as baseline
- Phase 2: Each page mission compares before/after screenshots
- Phase 3: Permanent Playwright test that takes screenshots and compares against Phase 0 baseline

The critical innovation: **Playwright MCP during development** (Claude Code can literally see the UI and decide if it looks right) + **Playwright E2E tests in CI** (automated regression prevention).

**Industry Standard:** Visual regression testing (Chromatic, Percy, BackstopJS). Baseline → change → comparison is the standard workflow.

**System Fit:** The 22 Playwright MCP tools are the game-changer. Claude Code can take a screenshot, evaluate it against design rules, and flag issues — all within a single session. This has never been available before in this codebase.

**Enforcement:** Phase 3 delivers a `visual-regression.spec.ts` that captures screenshots at standard breakpoints and stores them as git-tracked baselines. CI fails if screenshots differ beyond a threshold.

---

### Finding 8: Chat Page (1,772 Lines) Has the Most Complex State Management — Highest Risk

**Root Cause:** The chat page is the largest single file in the dashboard, handling:
- SSE streaming with retry logic
- Provider selection (Claude, GPT-4, etc.)
- Session management with archival
- Evidence citations and summaries
- Proposal generation and execution (5 proposal types)
- Chat history rail
- Deal context selection
- Timing analytics
- Error handling and warnings

This concentration of complexity in a single 1,772-line client component is the highest-risk area for visual inconsistency and interaction bugs.

File evidence:
- `apps/dashboard/src/app/chat/page.tsx`: 1,772 lines
- `apps/dashboard/src/components/chat/`: Only 3 files (268 lines total) — most logic is inlined in the page
- Components extracted: `MarkdownMessage.tsx` (41 lines), `ChatHistoryRail.tsx` (137 lines), `ProviderSelector.tsx` (90 lines)
- The page itself contains: provider state, session state, message state, streaming state, timing state, error state, citation state, proposal state, deal selection state

**Fix Approach:** The chat page mission (Phase 2, Tier 1) must:
1. Audit all interactive elements for correct wiring
2. Extract remaining inline components (message list, input area, evidence panel, proposal panel)
3. Test streaming at all 3 breakpoints
4. Verify provider selector, deal scope selector, and chat history rail
5. Check console for errors during streaming
6. Playwright: take screenshot mid-stream and post-stream

**Industry Standard:** Single Responsibility Principle. Chat UIs commonly decompose into: MessageList, MessageInput, MessageBubble, ToolCallDisplay, CitationPanel.

**System Fit:** The 3 existing chat components show the decomposition was started but not finished. The page file should be <500 lines with logic delegated to components and hooks.

**Enforcement:** File size lint: page.tsx files should be <600 lines. Logic in hooks, presentation in components.

---

### Finding 9: Existing E2E Test Suite Is Defense-Oriented, Not Quality-Oriented

**Root Cause:** The 11 E2E test files (1,100 lines) focus on defensive concerns: graceful degradation, no-dead-UI, backend-up checks, regression tests for specific findings. They verify "doesn't crash" and "doesn't show errors." They do NOT verify "looks correct" or "interactions work as expected."

File evidence:
- `graceful-degradation.spec.ts` (202 lines): Verifies no crashes when backend is down
- `no-dead-ui.spec.ts` (146 lines): Clicks all buttons, checks for 404s
- `backend-up.spec.ts` (73 lines): Verifies pages render with zero console.error
- `dashboard-worldclass-remediation.spec.ts` (187 lines): Specific finding regressions
- `phase-coverage.spec.ts` (183 lines): Verifies features from R4 mission

Missing:
- No visual snapshot tests
- No responsive breakpoint tests
- No interaction flow tests (e.g., "create a deal, navigate to it, add a note")
- No accessibility tests (keyboard navigation, screen reader)
- No performance tests (load time, time to interactive)

**Fix Approach:** Phase 3 must produce three new test categories:
1. **Visual regression tests** — screenshot comparison at 3 breakpoints per page
2. **Interaction flow tests** — end-to-end user journeys (create deal → detail → action → quarantine)
3. **Accessibility tests** — keyboard navigation sweep, focus trapping in modals, color contrast

**Industry Standard:** Testing pyramid: unit (fast, many) → integration (medium) → E2E (slow, focused). Current E2E tests are "defensive E2E" — need "quality E2E" to complement.

**System Fit:** The existing `phase-coverage.spec.ts` and `dashboard-worldclass-remediation.spec.ts` show the team already uses E2E for quality verification. Just needs systematic expansion.

**Enforcement:** Each Phase 2 page mission must produce at least 2 new E2E tests for that page. Phase 3 consolidates into a permanent regression suite.

---

### Finding 10: Sidebar/Navigation Is Consistent But Header Is Minimal

**Root Cause:** All page layouts use the same pattern: `SidebarProvider` → `AppSidebar` + `Header`. The sidebar (`app-sidebar.tsx`, 129 lines) is well-structured with nav links and org switcher. But the header (`header.tsx`, 31 lines) is minimal — likely just a breadcrumb or page title.

File evidence:
- `apps/dashboard/src/components/layout/app-sidebar.tsx`: 129 lines
- `apps/dashboard/src/components/layout/header.tsx`: 31 lines
- `apps/dashboard/src/components/ui/sidebar.tsx`: 728 lines (the primitive)
- All layout.tsx files follow identical pattern: SidebarProvider + AppSidebar + Header

The layout skeleton is consistent, which is good news for Phase 1 — there's no major structural rework needed. But the header at 31 lines may be too sparse (no global search, no notifications, no user menu in header).

**Fix Approach:** Phase 1 should:
1. Verify the sidebar renders correctly at all breakpoints (it collapses to mobile sheet)
2. Evaluate whether the header needs enhancement (global search is in `global-search.tsx` at 534 lines — is it accessible from the header?)
3. Ensure consistent page title/breadcrumb display across all pages
4. Test sidebar collapse/expand interaction

**Industry Standard:** Dashboard layouts need: sidebar nav, header with breadcrumbs + global actions (search, notifications, user menu), main content area with proper scroll containment.

**System Fit:** The `global-search.tsx` (534 lines, Cmd+K command palette) exists but its integration with the header needs verification. The `user-nav.tsx` (232 lines) exists for user menu.

**Enforcement:** Phase 0 Playwright screenshots will reveal header/sidebar state at each breakpoint. Phase 1 fixes any issues found.

---

## STRATEGY RECOMMENDATION

### Chosen Approach: Strategy C (Hybrid) — Refined

**Justification:** Strategy A (Tab-by-Tab) risks fixing shared components differently per page and discovering cross-cutting issues late. Strategy B (Top-Down Blueprint) is over-engineered — the shadcn/ui foundation is already solid, so a full blueprint redesign is unnecessary. Strategy C combines evidence-based reconnaissance (Phase 0) with cross-cutting foundation fixes (Phase 1) and page-by-page polish (Phase 2), preventing both premature optimization and inconsistency.

The refinement: Phase 1 is narrower than originally proposed (the primitive layer is already good), and Phase 2 is the dominant effort (page-level composition is where the problems live).

### Phase Breakdown

#### Phase 0: Reconnaissance Sprint (1 mission, type: recon)
**Deliverables:**
- Playwright screenshots of all 12 pages at 375px, 768px, 1280px (36 screenshots)
- Console error catalog per page per breakpoint
- Accessibility tree snapshots per page
- Findings catalog: cross-cutting issues vs page-specific issues
- Priority ranking of all findings

**Playwright MCP usage:** This phase is 100% Playwright. `browser_navigate` to each page, `browser_resize` to each breakpoint, `browser_take_screenshot`, `browser_console_messages`, `browser_snapshot`.

**Quality gate:** All 36 screenshots captured. All findings categorized. Cross-cutting issues identified.

#### Phase 1: Cross-Cutting Foundation (2-3 missions, type: build)

**Mission 1.1: Loading/Empty/Error State Consistency**
- Create shared `EmptyState` component with variants
- Add `loading.tsx` to all pages missing one (7 pages)
- Refactor 11 identical `error.tsx` to use shared component
- Audit and standardize inline skeleton patterns

**Mission 1.2: Layout, Navigation & Global CSS**
- Verify sidebar at all breakpoints (collapse/expand/mobile sheet)
- Verify header integration (global search, user nav, breadcrumbs)
- Audit CSS custom properties for completeness (hover states, focus states)
- Verify `caret-color: transparent` override works correctly everywhere
- Test dark mode toggle at all breakpoints

**Mission 1.3 (optional): API Client Rationalization**
- Audit `api.ts` vs `backend-fetch.ts` vs `api-client.ts` — clarify roles
- Ensure no page component calls `fetch()` directly
- Only if Phase 0 reveals fetch-layer issues

**Playwright MCP usage:** After each fix, take screenshot to verify. Test at all breakpoints. Check console for new errors.

**Quality gate:** `npx tsc --noEmit` passes. `make validate-local` passes. All pages load without console.error at all breakpoints. Shared components render correctly.

#### Phase 2: Page-by-Page Polish (6-8 missions, type: build)

Missions organized by page tier:

**Mission 2.1: Chat Page (Tier 1)**
- Audit all interactive elements
- Extract remaining inline components
- Test streaming UI at all breakpoints
- Verify provider selector, deal scope, chat history rail
- Playwright mid-stream screenshot

**Mission 2.2: Deal Workspace (Tier 1)**
- Audit all 6 tabs (Summary, Events, Case File, Enrichment, Materials, Actions)
- Test tab switching and data loading
- Verify stage transition workflow
- Verify note-taking interaction
- Test at all breakpoints

**Mission 2.3: Actions Command Center (Tier 1)**
- Audit polling mechanism
- Test bulk operations with confirmation
- Verify metrics display
- Test schema-driven form generation
- Verify status-based tab filtering

**Mission 2.4: Quarantine + Deals List (Tier 2)**
- Quarantine: approval/rejection workflow, preview expansion, bulk operations
- Deals: table vs kanban toggle, sorting, pagination, URL-persisted filters
- Test both pages at all breakpoints

**Mission 2.5: Agent Activity (Tier 2)**
- Audit event filtering tabs
- Test search filtering
- Verify event detail display
- Test agent status indicator

**Mission 2.6: Dashboard + Operator HQ (Tier 3)**
- Dashboard: pipeline funnel, approval queue, execution inbox, auto-refresh
- HQ: aggregated stats, component delegation
- Verify data consistency between dashboard and HQ

**Mission 2.7: Settings + Onboarding (Tier 3)**
- Settings: all 6 sections, section navigation, persistence targets
- Onboarding: wizard step sequence, skip/continue/complete flows
- New Deal: form validation, redirect behavior

**Mission 2.8 (optional): UI Test Page Cleanup**
- Only if Phase 0 reveals issues with the dev testing page

**Playwright MCP usage:** Every page mission starts with "before" screenshots and ends with "after" screenshots at all breakpoints. Console checked before and after. Accessibility tree diffed.

**Quality gate per mission:** Page-specific screenshots match design intent. Zero console.error. All interactive elements wired and functional. `npx tsc --noEmit` passes.

#### Phase 3: Integration Sweep (1-2 missions, type: QA)

**Mission 3.1: Cross-Page Flows & Visual Regression**
- End-to-end user journeys: create deal → navigate → add action → quarantine → approve
- Chat → proposal → execute → verify result in deal workspace
- Visual regression test suite (permanent): screenshot at 3 breakpoints per page
- Responsive regression test suite (permanent)

**Mission 3.2: Accessibility & Performance**
- Keyboard navigation sweep across all pages
- Focus trapping in modals/dialogs
- Color contrast verification
- Screen reader compatibility (accessibility tree check)
- Performance budget check (load time, bundle size)

**Playwright MCP usage:** Both missions are Playwright-heavy. Visual regression captures the final baseline. Cross-page flows use `browser_navigate` + `browser_click` + `browser_take_screenshot` + `browser_console_messages`.

**Quality gate:** All cross-page flows complete without error. Visual regression baseline established. Zero accessibility violations. Performance within budget.

---

### Mission Inventory

| # | Mission | Type | Phase | Tier | Est. Pages |
|---|---------|------|-------|------|-----------|
| M-00 | Reconnaissance Sprint | recon | 0 | — | All 12 |
| M-01 | Loading/Empty/Error States | build | 1 | cross-cutting | All |
| M-02 | Layout, Navigation & Global CSS | build | 1 | cross-cutting | All |
| M-03 | Chat Page Polish | build | 2 | Tier 1 | Chat |
| M-04 | Deal Workspace Polish | build | 2 | Tier 1 | Deal [id] |
| M-05 | Actions Command Center Polish | build | 2 | Tier 1 | Actions |
| M-06 | Quarantine + Deals List | build | 2 | Tier 2 | Quarantine, Deals |
| M-07 | Agent Activity Polish | build | 2 | Tier 2 | Agent Activity |
| M-08 | Dashboard + Operator HQ | build | 2 | Tier 3 | Dashboard, HQ |
| M-09 | Settings + Onboarding | build | 2 | Tier 3 | Settings, Onboarding, New Deal |
| M-10 | Cross-Page Flows & Visual Regression | QA | 3 | — | All |
| M-11 | Accessibility & Performance | QA | 3 | — | All |

**Total: 12 missions** (1 recon, 2 cross-cutting build, 7 page build, 2 QA)

---

### Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Phase 0 reveals more cross-cutting issues than expected | Medium | High | Mission 1.3 is held in reserve; Phase 1 can expand to 3-4 missions |
| Chat page too complex for single session | Medium | Medium | Pre-extract components in a prep commit before the main polish mission |
| Playwright MCP unavailable during sessions | Low | High | Degrade to manual curl + visual inspection; capture evidence via `make validate-live` |
| Fixing one page breaks another via shared CSS | Medium | High | Phase 1 locks down shared styles first; Phase 2 runs `make validate-local` after every page mission |
| Dark mode inconsistencies compound across pages | Medium | Medium | Phase 0 captures dark mode screenshots; Phase 1 audits CSS variables for dark mode gaps |
| Backend unavailable during QA testing | Low | Medium | `graceful-degradation.spec.ts` already covers this; Phase 3 extends it |
| Scope creep — "fix and polish" becomes "add features" | Medium | High | Mission prompts explicitly state: NO new features, only fix and polish existing |

---

### Regression Prevention

1. **Screenshot baselines** from Phase 0 serve as the visual contract — any Phase 2 change must not degrade other pages' screenshots
2. **`make validate-local`** runs after every mission — catches type errors, contract drift, import violations
3. **`npx tsc --noEmit`** catches TypeScript regressions immediately
4. **Existing E2E tests** (`graceful-degradation.spec.ts`, `no-dead-ui.spec.ts`, `backend-up.spec.ts`) run as regression gates during Phase 2
5. **New E2E tests** produced per Phase 2 mission become permanent regression gates
6. **Phase 3 visual regression suite** becomes the ultimate gate — CI fails if screenshots drift

---

### Continuous Improvement

- Phase 0 findings feed directly into Phase 1 scope (what cross-cutting issues exist?)
- Phase 1 completion unblocks Phase 2 (shared foundation is locked)
- Each Phase 2 mission produces: fixed code + new E2E tests + updated screenshots
- Phase 2 findings that affect other pages are logged and addressed in later missions or Phase 3
- Phase 3 consolidates all Phase 2 tests into a permanent regression suite
- Final deliverable: the screenshot baseline + test suite serve as the quality contract for all future dashboard work

---

### What the Other Strategies Get Wrong

**Strategy A (Tab-by-Tab) gets shared components wrong.** By diving into pages immediately without a cross-cutting audit, Strategy A would fix the same shared component (e.g., LoadingSkeleton, error boundary) differently on different pages. Page 1 might get a fancy empty state, Page 2 gets a plain text "No data", Page 3 gets nothing. Then when you notice the inconsistency, you have to go back and normalize — fixing things twice. Phase 0 + Phase 1 prevent this entirely.

**Strategy B (Top-Down Blueprint) gets the effort distribution wrong.** The shadcn/ui primitives are already consistent. The CSS variable system is already semantic. The design system rule is already comprehensive. What's missing is not a blueprint — it's execution. Spending 3-4 missions on an abstract blueprint before writing any code is wasted effort in a codebase where the foundations already exist. Strategy B confuses "incremental construction created inconsistencies" with "the architecture is wrong." The architecture is fine; the pages just need polish.

---

### Definition of "Done" for the Entire Initiative

The dashboard UI masterplan is complete when ALL of the following are true:

1. **Visual parity:** Every page looks intentional and consistent at 375px, 768px, and 1280px in both light and dark mode
2. **Zero console.error:** No page produces console.error messages under normal operation (with or without backend)
3. **All interactions wired:** Every button, link, form, and interactive element does something meaningful or is removed
4. **Consistent states:** Every data component handles loading, empty, and error states using shared components
5. **E2E coverage:** Every page has at least 2 E2E tests covering its primary interaction flows
6. **Visual regression baseline:** A permanent Playwright screenshot suite exists in CI
7. **Responsive verification:** All pages pass layout checks at 3 breakpoints
8. **Accessibility pass:** Keyboard navigation works across all pages; no focus traps; color contrast meets WCAG AA
9. **Type safety:** `npx tsc --noEmit` passes with zero errors
10. **Contract compliance:** `make validate-local` passes with zero errors

---

## ADJACENT OBSERVATIONS

### AO-1: Dual Callback Ref Implementations
Two files exist with the same purpose: `use-callback-ref.ts` and `use-callback-ref.tsx` in `hooks/`. One should be deleted. Not in scope (no visual impact) but noted for housekeeping.

### AO-2: api-client.ts vs api.ts vs backend-fetch.ts
Three separate fetch abstraction layers exist. The relationship between them should be documented even if not rationalized in this initiative. If Phase 0 reveals no issues, defer to a separate technical debt mission.

### AO-3: Chat Page Size (1,772 lines)
The chat page is dangerously close to the "too complex for a single file" threshold. Component extraction would improve maintainability but is a refactoring concern, not a visual polish concern. If the chat mission (M-03) can naturally extract components while polishing, do it. If not, defer to a separate refactoring mission.

### AO-4: UI Test Page
`apps/dashboard/src/app/ui-test/page.tsx` (289 lines) is a development tool, not a production page. It should not be included in the visual regression baseline. Consider adding a `robots.txt` exclusion or a "dev only" flag.

### AO-5: Design System Rule B7 Anti-Convergence
The rule explicitly states "NEVER converge on common choices across generations." This is aspirational for future feature development but is in tension with the current mission (which is about consistency). Clarify: B7 applies to new feature design, not to polish/consistency work.

---

## SUMMARY

- Total primary findings: 10
- Total adjacent observations: 5
- Confidence level: HIGH
- Key recommendation: Execute Strategy C (Hybrid) with 12 missions across 4 phases, placing Playwright MCP at the center of every phase. The cross-cutting foundation (Phase 1) is narrower than expected — the real value is in evidence-based page-by-page polish (Phase 2) backed by a permanent visual regression suite (Phase 3).
