# FINAL MASTER — TP-20260211-160514
## Mode: design
## Generated: 2026-02-11T16:20:19Z
## Sources: 3 Pass 1 reports + 3 Pass 2 cross-reviews

---

## MISSION

Produce a single master strategy for bringing the ZakOps dashboard to world-class quality. The platform has been built incrementally and now contains visual inconsistencies, unwired interactions, misaligned components, and unpolished flows. We are NOT adding features — we are fixing and perfecting everything that already exists. The strategy must leverage Playwright MCP (22 browser tools) as a first-class capability, be executable as mission prompts (v2.1), and fit within the existing 14-contract-surface infrastructure.

---

## EXECUTIVE SUMMARY

All three independent agents (Claude, Gemini, Codex) unanimously chose **Strategy C (Hybrid)** after investigating the codebase. The dashboard is a substantial Next.js 15 application (~26,600 lines, 120+ components, 12 pages, 31 API routes) with solid shadcn/ui primitives but inconsistent page-level composition. The real problems live at the page composition layer, not the primitive layer: duplicated shells, fragmented loading/empty/error states, untested responsive breakpoints, unwired interactions behind mock endpoints, and convention violations against declared contracts. The strategy executes as **13 missions across 4 phases**: reconnaissance baseline (Phase 0), cross-cutting foundation (Phase 1, 3 missions), page-by-page polish (Phase 2, 7 missions), and integration sweep (Phase 3, 2 missions). Playwright MCP is embedded in every phase — not just final QA — enabling Claude Code to *see* the UI during development for the first time.

---

## CONSOLIDATED FINDINGS

### F-1: Strategy C (Hybrid) Is the Correct Program Shape
**Sources:** Claude (P1-F1), Gemini (P1-F4 + Summary), Codex (P1-F1, P1-F8)
**Root Cause:** The dashboard has simultaneous **cross-cutting** problems (duplicated shells, convention violations, inconsistent states) and **page-local** problems (divergent composition, unwired interactions, varying complexity). Strategy A (Tab-by-Tab) would re-touch shared components differently per page, causing rework when inconsistencies are discovered late. Strategy B (Top-Down Blueprint) over-specifies abstractly while real integration paths still contain mock/placeholder endpoints — it confuses "incremental construction created inconsistencies" with "the architecture is wrong." The architecture is sound; the pages need polish.
**Fix Approach:** Execute a 4-phase hybrid: Phase 0 (evidence-based recon, no code changes) → Phase 1 (cross-cutting foundation fixes) → Phase 2 (page-by-page polish, the dominant effort) → Phase 3 (integration sweep + permanent regression suite). Phase weights rebalanced from original proposal: Phase 1 is narrower than expected (shadcn/ui primitives are already consistent at 44 files, ~3,400 lines), Phase 2 is the main event.
**Industry Standard:** Evidence-first modernization used in large UI remediation programs (Google Material Design migration, Shopify Polaris migration): baseline audit first, then shared primitives, then feature surfaces, then integrated regression hardening.
**System Fit:** Maps directly to ZakOps infrastructure: 14 contract surfaces, TriPass pipeline, mission prompt standard v2.1, Playwright MCP (22 browser tools). Phase 0 = 1 recon mission, Phase 1 = 3 build missions, Phase 2 = 7 build missions, Phase 3 = 2 QA missions.
**Enforcement:** Phase gates block progression: Phase 0 must produce complete findings catalog before Phase 1 starts. Phase 1 must pass `make validate-local` + `npx tsc --noEmit` before Phase 2 starts. Each Phase 2 mission must produce before/after evidence. Phase 3 produces permanent CI regression suite.

---

### F-2: Page Complexity Tiering Demands Specific Mission Sizing
**Sources:** Claude (P1-F2), Codex (P1-F2 — mission plan), Gemini (implicit via P2 endorsement)
**Root Cause:** Pages vary enormously in complexity — from 5 lines (home redirect) to 1,772 lines (chat). Treating all pages equally in mission scoping wastes sessions on simple pages or under-scopes complex ones. Evidence:
- **Tier 1 (1000+ lines):** `apps/dashboard/src/app/chat/page.tsx` (1,772), `apps/dashboard/src/app/deals/[id]/page.tsx` (1,422), `apps/dashboard/src/app/actions/page.tsx` (1,286) — each needs a dedicated mission
- **Tier 2 (500-999 lines):** `apps/dashboard/src/app/quarantine/page.tsx` (789), `apps/dashboard/src/app/deals/page.tsx` (695), `apps/dashboard/src/app/hq/page.tsx` (657) — can be paired
- **Tier 3 (<500 lines):** `apps/dashboard/src/app/dashboard/page.tsx` (425), `apps/dashboard/src/app/settings/page.tsx` (178), `apps/dashboard/src/app/onboarding/page.tsx` (34), New Deal (124) — can be grouped
**Fix Approach:** Tier 1 pages get 1 mission each (3 missions). Tier 2 pages get 2 missions (pair quarantine+deals-list, agent-activity+HQ or solo). Tier 3 pages get 1-2 missions (group dashboard+onboarding, settings+new-deal).
**Industry Standard:** Agile story point estimation — complex surfaces get proportionally more effort allocation. Session-scoped vertical slices with dependency gates.
**System Fit:** Each mission must fit a single Claude Code session. Tier 1 pages at 1,200-1,800 lines are at the session limit. Mission prompt standard v2.1 requires scope declaration.
**Enforcement:** Each mission prompt states its page tier and expected line count. Mission is blocked from expanding into adjacent pages.

---

### F-3: Loading/Empty/Error States Are the #1 Cross-Cutting Inconsistency
**Sources:** Claude (P1-F3), Gemini (P1-F3), Codex (P1-F4)
**Root Cause:** The component-patterns rule mandates "every data component must handle: loading, empty, error." Implementation is uneven:
- **Loading states:** 4 pages have `loading.tsx` (dashboard, quarantine, deals, hq). 7 pages lack it (chat, actions, agent-activity, settings, onboarding, deal-workspace, new-deal). Pages without it use inline skeletons of varying quality. `apps/dashboard/src/components/LoadingSkeleton.tsx` (96 lines) exists but isn't universally adopted.
- **Error boundaries:** 13 `error.tsx` files exist (corrected count — Claude reported 11, actual is 13), all 42-line identical copies of Card + IconAlertTriangle + error.message + retry Button. DRY violation.
- **Empty states:** No shared `EmptyState` component in shared components. Each page handles "no data" differently.
**Fix Approach:** Phase 1 Mission 1 (M-01):
1. Create shared `EmptyState` component with variants (no-data, no-results, error-fallback)
2. Add `loading.tsx` to all 7 pages missing one, using consistent skeleton patterns
3. Refactor 13 identical `error.tsx` files to use shared `ErrorBoundaryUI` component (each becomes ~5 lines)
4. Audit inline skeleton usage across Tier 1 pages for consistency
**Industry Standard:** React Suspense boundaries with consistent fallback UIs. Vercel's Next.js docs recommend `loading.tsx` for every route segment.
**System Fit:** `component-patterns.md` already mandates this. `LoadingSkeleton.tsx` (96 lines) exists but needs wider adoption. Implementation catching up to rules.
**Enforcement:** E2E test that navigates each page with backend unavailable and verifies graceful empty states (extend `graceful-degradation.spec.ts`). `error.tsx` files should be <15 lines after refactor.

---

### F-4: Inconsistent Page Shell / Header Implementation
**Sources:** Gemini (P1-F1), Codex (P1-F4), Claude (P1-F10)
**Root Cause:** Each page manually implements its own header structure (title, description, action buttons) with varying styles:
- `apps/dashboard/src/app/dashboard/page.tsx:117-135` — manual header
- `apps/dashboard/src/app/deals/page.tsx:238-259` — different manual header
- `apps/dashboard/src/app/quarantine/page.tsx:210-218` — yet another pattern
All 8 route `layout.tsx` files are nearly identical (SidebarProvider → AppSidebar + SidebarInset → Header + children). An unused `apps/dashboard/src/components/layout/page-container.tsx:20` exists with zero call sites. Body is globally locked with `overflow-hidden` (`apps/dashboard/src/app/layout.tsx:53`) but pages handle scroll differently (`dashboard/page.tsx:148`, `deals/page.tsx:306`, `quarantine/page.tsx:302`, `settings/page.tsx:97`).
**Fix Approach:** Phase 1 Mission 2 (M-02):
1. Extract a shared `<PageHeader />` component accepting `title`, `description`, `children` (actions)
2. Consolidate duplicated route layouts into fewer shared layout groups
3. Delete unused `page-container.tsx`
4. Standardize scroll containment strategy across pages
**Industry Standard:** "Layout Composition" / "Shell" pattern. Dashboard layouts need: sidebar nav, header with breadcrumbs + global actions, main content area with proper scroll containment.
**System Fit:** The existing UI stack (shadcn + Tailwind + shared sidebar/header) is already componentized. Convergence cost is low. `global-search.tsx` (534 lines, Cmd+K) and `user-nav.tsx` (232 lines) exist and need integration verification.
**Enforcement:** Lint rule or code review check rejecting manual `<h1>` tags in page roots, requiring `<PageHeader>` instead. Phase 0 screenshots reveal header/sidebar state at each breakpoint.

---

### F-5: Playwright MCP Must Be Central to Every Phase
**Sources:** Claude (P1-F4, P1-F7), Gemini (P1-F4), Codex (P1-F3, P1-F7)
**Root Cause:** Current E2E tests are functional only — zero visual regression tests, zero responsive breakpoint tests, zero viewport-specific assertions. The design system rule mandates 375/768/1280px testing (`.claude/rules/design-system.md` sections A8, C1) but no test file uses `page.setViewportSize()`. Playwright config is desktop Chromium only (`playwright.config.ts:14-18`). The 22 Playwright MCP browser tools are available but have never been used in any test.
**Fix Approach:** Playwright integration strategy by phase:
- **Phase 0:** For each of 12 routes, collect `browser_navigate` + `browser_resize` (375/768/1280) + `browser_take_screenshot` + `browser_console_messages` + `browser_snapshot` artifacts. Minimum 36 screenshots.
- **Phase 1/2:** Every mission includes before/after screenshots for touched routes at 3 breakpoints + console error check + at least one critical interaction replay.
- **Phase 3:** Full flow matrix across cross-route journeys. Permanent `responsive-regression.spec.ts` and `visual-regression.spec.ts` added to CI.
**Industry Standard:** Visual regression testing (Chromatic, Percy, BackstopJS). Baseline → change → comparison is standard workflow. Runtime console/network capture is current best practice for UI stabilization.
**System Fit:** The project explicitly declares Playwright MCP as central. 22 browser tools available. This is the single biggest quality lever. Claude Code can now *see* the UI during development, not just edit code blind.
**Enforcement:** A mission is blocked from completion unless its artifact bundle includes screenshots at 3 breakpoints and console/network logs with zero untriaged errors.

---

### F-6: Divergent Data Fetching Patterns (Promise.allSettled Compliance)
**Sources:** Gemini (P1-F2), Claude (P1-F5), Codex (P1-F5)
**Root Cause:** Architectural constraint mandates `Promise.allSettled` with typed empty fallbacks for multi-fetch, but compliance is uneven:
- Dashboard correctly uses `Promise.allSettled` — `apps/dashboard/src/app/dashboard/page.tsx:64`
- Actions page also uses `Promise.allSettled` — `apps/dashboard/src/app/actions/page.tsx:185`
- HQ page also uses `Promise.allSettled` — `apps/dashboard/src/app/hq/page.tsx:29`
- Deals page uses single `await` (fragile) — `apps/dashboard/src/app/deals/page.tsx:103`
- Quarantine page uses single `await` — `apps/dashboard/src/app/quarantine/page.tsx:58`
Three separate fetch utilities exist adding confusion: `api.ts` (2,060 lines, centralized), `backend-fetch.ts` (server-side proxy), `api-client.ts` (unclear role).
**Fix Approach:** Phase 1 Mission 3 (M-03): Standardize all multi-fetch page loads on `Promise.allSettled`. Audit the three fetch layers to clarify roles. Ensure no page component calls `fetch()` directly — all data access through `api.ts` functions.
**Industry Standard:** Single data access layer pattern. Resilient parallel execution with fallbacks.
**System Fit:** Explicitly required by architectural constraints. Dashboard is the model implementation. Normalization is mandatory, not optional.
**Enforcement:** ESLint rule banning `Promise.all` (already exists/requested). CI grep check: `fetch(` in page components should return zero results outside API route handlers.

---

### F-7: Contract/Convention Compliance Drift
**Sources:** Codex (P1-F5), Claude (P1-F7), Gemini (P2 endorsement)
**Root Cause:** Design system conventions are declared in `apps/dashboard/src/types/design-system-manifest.ts` but not uniformly enforced. Specific verified violations:
- **Hardcoded stages:** `apps/dashboard/src/app/deals/new/page.tsx:20` — should use `PIPELINE_STAGES` from `execution-contracts.ts` (line 76 of manifest)
- **Client-side `.length` counting:** `apps/dashboard/src/app/dashboard/page.tsx:209`, `apps/dashboard/src/app/deals/page.tsx:220` (possibly :636) — banned by manifest (line 67), must use server-side counts
- **Non-502 backend failure status:** `apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts:49`, `apps/dashboard/src/app/api/chat/complete/route.ts:59`, `apps/dashboard/src/app/api/chat/execute-proposal/route.ts:34` — return 500 instead of JSON 502 (manifest line 84)
**Fix Approach:** Included in Phase 1 Mission 3 (M-03) as contract alignment work: normalize stage sources, server-count usage, and failure status semantics before Phase 2 page polish.
**Industry Standard:** Architecture contract drift treated as blocking quality defect, not cleanup backlog.
**System Fit:** ZakOps has explicit convention manifests and `validate-surface9.sh` (lines 14-57). This phase operationalizes them.
**Enforcement:** Extend `tools/infra/validate-surface9.sh` to include banned client display counts and non-502 backend-unavailable responses. Add to `make validate-local`.

---

### F-8: Interaction Wiring Inconsistency — Placeholders and Mock Success Paths
**Sources:** Codex (P1-F6), Claude P2 endorsement (U-3), Gemini P2 endorsement (U-4)
**Root Cause:** Several production API endpoints intentionally return placeholders or mock success, hiding real integration state and violating "no dead UI":
- `apps/dashboard/src/app/api/chat/execute-proposal/route.ts:14-25` — returns 501 "not yet integrated"
- `apps/dashboard/src/app/api/chat/session/[sessionId]/route.ts:15-22` — returns placeholder with "not yet implemented" comment
- `apps/dashboard/src/app/api/actions/[id]/archive/route.ts:38,54` — mock archival fallback on 404 and backend unavailable
- `apps/dashboard/src/app/api/actions/bulk/archive/route.ts:53,68` — mock bulk archive fallback
- `apps/dashboard/src/app/api/actions/completed-count/route.ts:52-60` — mock completed-count with hardcoded values
**Fix Approach:** Every Phase 2 page mission MUST include an **interaction closure checklist**: every visible control maps to one of:
(a) Real endpoint — fully wired
(b) Explicitly degraded endpoint — UI shows "not available" state
(c) Hidden/removed — control not rendered until backend integration exists
Silent mock success on primary actions is unacceptable.
**Industry Standard:** UX hardening requires truthful interaction semantics. Silent mock success is acceptable only in dedicated test/sandbox surfaces.
**System Fit:** ZakOps explicitly targets "no dead UI" and has E2E intent for this (`apps/dashboard/tests/e2e/no-dead-ui.spec.ts:1`).
**Enforcement:** Interaction-matrix test that fails if production routes return mock success signatures on critical actions.

---

### F-9: Chat Page Is the Highest-Risk Surface
**Sources:** Claude (P1-F8), Gemini P2 endorsement (U-1), Codex P2 endorsement (U-1)
**Root Cause:** The chat page (`apps/dashboard/src/app/chat/page.tsx`, 1,772 lines) is the largest single file in the dashboard, handling 9+ distinct concerns inlined in one component:
- SSE streaming with retry logic
- Provider selection (Claude, GPT-4, etc.)
- Session management with archival
- Evidence citations and summaries
- Proposal generation and execution (5 proposal types)
- Chat history rail
- Deal context selection
- Timing analytics
- Error handling and warnings
Only 3 components extracted to `components/chat/` (268 lines total): `MarkdownMessage.tsx` (41), `ChatHistoryRail.tsx` (137), `ProviderSelector.tsx` (90). The page itself contains provider state, session state, message state, streaming state, timing state, error state, citation state, proposal state, and deal selection state.
**Fix Approach:** Chat page mission (M-04, Phase 2, Tier 1) must:
1. Audit all interactive elements for correct wiring
2. Test streaming UI at all 3 breakpoints
3. Verify provider selector, deal scope selector, chat history rail
4. Check console for errors during streaming
5. Playwright: screenshot mid-stream and post-stream
6. Component extraction allowed ONLY where it's a natural byproduct of fixing visual/interaction issues (not purely for code organization — see DRIFT-2)
**Industry Standard:** Chat UIs commonly decompose into MessageList, MessageInput, MessageBubble, ToolCallDisplay, CitationPanel. SRP.
**System Fit:** The 3 existing chat components show decomposition was started but not finished. This is the highest-risk mission and may need a prep commit.
**Enforcement:** Before/after screenshots at 3 breakpoints + console error check + interaction closure checklist. Mission is Tier 1 — full dedicated session.

---

### F-10: Existing E2E Tests Need Stronger Assertions
**Sources:** Claude (P1-F9), Codex (P1-F7), Gemini P2 endorsement
**Root Cause:** The 11 E2E test files (~1,100 lines) are defense-oriented ("doesn't crash") not quality-oriented ("looks correct", "interactions work"). Specific weaknesses:
- Tautological assertion: `apps/dashboard/tests/e2e/quarantine-actions.spec.ts:56` — `expect(btnCount).toBeGreaterThanOrEqual(0)` (always true)
- Static sleeps: `apps/dashboard/tests/e2e/dashboard-worldclass-remediation.spec.ts:55`, `apps/dashboard/tests/e2e/no-dead-ui.spec.ts:122` — fragile timing
- Narrow validator scope: `tools/infra/validate-surface9.sh:14-57` — checks contract metadata, not visual output
**Fix Approach:** Define mandatory quality gates by phase:
- **Phase 0 gate:** Complete issue catalog with severity + owner + artifact links
- **Phase 1 gate:** Shell/scaffold/token convergence + contract validator pass + `make validate-local` + `npx tsc --noEmit`
- **Phase 2 gate (per route):** Interaction closure checklist pass + no console errors + responsive screenshot triad + before/after evidence
- **Phase 3 gate:** Full flow regression pass + contract surface checks + no open Sev-1/Sev-2 UI defects + permanent visual regression suite
Phase 3 produces three new test categories: visual regression tests, interaction flow tests, and basic accessibility tests.
**Industry Standard:** Deterministic gates (artifact + assertion based) required for stable UI remediation at scale. Testing pyramid: unit → integration → E2E (both defensive and quality).
**System Fit:** Complements existing TriPass and validation scripts without new infrastructure. Existing `phase-coverage.spec.ts` and `dashboard-worldclass-remediation.spec.ts` show the team uses E2E for quality verification — just needs expansion.
**Enforcement:** Each Phase 2 mission must produce at least 2 new E2E tests. Phase 3 consolidates into permanent suite. CI jobs fail on missing artifact bundles or validator regressions.

---

### F-11: Design System Rule B7 Anti-Convergence Tension
**Sources:** Claude (P1-AO-5), Claude P2 endorsement (U-8)
**Root Cause:** `.claude/rules/design-system.md` rule B7 states "NEVER converge on common choices across generations." This is in direct tension with a consistency/polish mission that explicitly wants convergence across pages.
**Fix Approach:** Clarify in all mission prompts: B7 applies to **new feature design** (future innovation), NOT to polish/consistency work (current initiative). Standardizing shared components, error states, and loading patterns is the goal of this initiative and does not violate B7's intent.
**Industry Standard:** Design system rules should distinguish between creative divergence (new features) and systematic consistency (existing surfaces).
**System Fit:** Without this clarification, builder agents may hesitate to standardize. This is a meta-finding that enables all other findings.
**Enforcement:** Every mission prompt includes: "B7 anti-convergence does not apply to this mission — we are standardizing existing patterns."

---

### F-12: nuqs vs Manual URLSearchParams Inconsistency
**Sources:** Gemini (P1-AO-2), Gemini P2 endorsement (U-2), Codex P2 endorsement
**Root Cause:** `nuqs` (modern URL state management) is globally available — `apps/dashboard/src/app/layout.tsx:9` imports `NuqsAdapter`, wrapping the app at line 60. However, `apps/dashboard/src/app/deals/page.tsx:129-140` uses manual `URLSearchParams` with `router.push()` instead of nuqs hooks.
**Fix Approach:** Flag during the Deals List page mission (M-07, Phase 2). Low-effort fix if nuqs is already globally available — replace manual `URLSearchParams` manipulation with nuqs hooks for consistency.
**Industry Standard:** Single state management strategy for URL params. Mixing approaches creates maintenance burden.
**System Fit:** nuqs is already the chosen solution (globally wired). This is a missed adoption, not an architectural decision.
**Enforcement:** Phase 2 Deals mission checklist includes: "Replace manual URLSearchParams with nuqs hooks."

---

## DISCARDED ITEMS

### DISC-1: "11 Identical Error Boundaries" Count (from Claude, P1-F6)
**Reason for exclusion:** The finding itself (DRY violation in error.tsx files, shared component needed) is valid and included as part of F-3. However, Claude's specific count of "11" is inaccurate — actual count is **13** error.tsx files. Corrected count used in F-3. The finding is merged, not dropped.

### DISC-2: API Client Bypass in Page Components (from Claude, P1-F5 partial; Codex P2-U-2)
**Reason for exclusion:** Claude claimed pages bypass `api.ts` with direct `fetch()` calls. Codex P2 verification found this UNVERIFIED — multiple API routes intentionally use `backendFetch` (expected for server-side routes), and direct `fetch(` in page components was not confirmed. The broader fetch-layer concern (3 utilities) is included in F-6 and DRIFT-1, but the specific "pages bypass api.ts" claim lacks evidence.

### DISC-3: `api.ts` Ignored by Standard Listing Tools (from Gemini, P1-AO-1)
**Reason for exclusion:** Codex P2 verified this as INVALID. File exists and is not git-ignored (`git check-ignore` reports not ignored). Likely a tooling artifact during Gemini's investigation.

### DISC-4: Dual `use-callback-ref` Implementations (from Claude, P1-AO-1)
**Reason for exclusion:** Housekeeping item with zero visual impact. Out of scope for a UI polish strategy. Both `use-callback-ref.ts` and `use-callback-ref.tsx` exist but this is codebase cleanup, not UI quality.

---

## DRIFT LOG

Out-of-scope items flagged by cross-reviews. Not actionable in this mission unless Phase 0 findings change the assessment.

### DRIFT-1: API Client Layer Rationalization
**Flagged by:** Claude (P1-F5, optional M-03), Claude P2 (DRIFT-1)
**Why out of scope:** Rationalizing 3 fetch utility layers (`api.ts`, `backend-fetch.ts`, `api-client.ts`) into a single canonical layer is architecture refactoring, not visual polish. The UI works fine either way.
**Severity if ignored:** LOW for visual quality, MEDIUM for long-term maintainability.
**Action:** Defer unless Phase 0 reveals user-visible issues caused by fetch layer inconsistency.

### DRIFT-2: Chat Page Component Extraction
**Flagged by:** Claude (P1-AO-3, P1-F8), Claude P2 (DRIFT-2)
**Why out of scope:** Extracting inline components from a 1,772-line file is refactoring, not visual polish. The mission states "fix and polish what exists."
**Severity if ignored:** MEDIUM — polish mission harder without extraction, but forced extraction risks bugs.
**Action:** Allow extraction ONLY where it's a natural byproduct of fixing visual/interaction issues. Do NOT extract purely for code organization.

### DRIFT-3: Lint Rules and CI Enforcement Infrastructure
**Flagged by:** All agents proposed new lint rules/CI jobs. Claude P2 (DRIFT-3).
**Why out of scope:** Infrastructure improvements, not UI polish. Adding ESLint rules, file-size checks, CI jobs.
**Severity if ignored:** LOW for current quality, HIGH for regression prevention.
**Action:** Phase 3 is the right place for new enforcement (regression prevention is explicitly in scope). Phase 1/2 should NOT add new lint rules — that's scope creep.

### DRIFT-4: Full Accessibility/WCAG AA Audit
**Flagged by:** Claude (P1-F9, M-11), Claude P2 (DRIFT-4)
**Why out of scope:** Full WCAG AA audit (keyboard nav, screen reader, color contrast) is a distinct discipline from visual polish. The mission targets "visual inconsistencies, unwired interactions, misaligned components" — not accessibility compliance.
**Severity if ignored:** MEDIUM — accessibility defects are real quality issues but not the primary target.
**Action:** Include basic accessibility checks (keyboard nav, focus traps) in Phase 3 integration sweep. Full WCAG AA audit should be a separate follow-up initiative. M-12 is deferrable.

### DRIFT-5: Diligence Hook TODO Replacement
**Flagged by:** Codex (P1-AO), Codex P2 (DRIFT-3), Gemini P2 (DRIFT-3)
**Why out of scope:** `apps/dashboard/src/components/diligence/useDiligence.ts:123` contains `// TODO: Replace with actual API call`. This is feature-integration work outside dashboard tab polish.
**Severity if ignored:** MEDIUM if linked to active pages, LOW otherwise.
**Action:** Catalog in Phase 0. Address only if it causes visible UI issues.

### DRIFT-6: Chat File-Size Lint Mandate
**Flagged by:** Codex P2 (DRIFT-4)
**Why out of scope:** Structural refactor target (<600 lines) is maintainability work, not visual/interaction polish.
**Severity if ignored:** MEDIUM.
**Action:** Defer to separate refactoring initiative.

---

## MISSION INVENTORY

### Phase 0: Reconnaissance (No Code Changes)

| # | Mission | Type | Scope |
|---|---------|------|-------|
| M-00 | Reconnaissance Sprint | recon | All 12 pages at 3 breakpoints |

**Deliverables:** 36+ screenshots (12 pages x 3 breakpoints x light mode, optionally dark), console error catalog per page per breakpoint, accessibility tree snapshots, findings catalog (cross-cutting vs page-specific), priority ranking, interaction wiring inventory.
**Playwright usage:** 100% — `browser_navigate`, `browser_resize` (375/768/1280), `browser_take_screenshot`, `browser_console_messages`, `browser_snapshot`.

### Phase 1: Cross-Cutting Foundation (3 Build Missions)

| # | Mission | Type | Source |
|---|---------|------|--------|
| M-01 | Loading/Empty/Error State Consistency | build | Claude F3, Gemini F3, Codex F4 |
| M-02 | Layout/Shell Consolidation + Navigation | build | Gemini F1, Codex F4, Claude F10 |
| M-03 | API Failure Contract Alignment | build | Codex F5, Claude F7 |

**M-01 scope:** Shared `EmptyState` component, `loading.tsx` for 7 missing pages, refactor 13 `error.tsx` to shared component, standardize inline skeletons.
**M-02 scope:** Shared `<PageHeader />` component, consolidate duplicated route layouts, delete unused `page-container.tsx`, standardize scroll containment, verify sidebar at all breakpoints, verify header integration.
**M-03 scope:** Standardize `Promise.allSettled` for multi-fetch, fix hardcoded stages (use `PIPELINE_STAGES`), fix client-side `.length` counts, fix non-502 backend failure responses. Extend `validate-surface9.sh`.
**Playwright usage:** After each fix, screenshot to verify. Test at all breakpoints. Console error check.

### Phase 2: Page-by-Page Polish (7 Build Missions)

| # | Mission | Type | Tier | Pages |
|---|---------|------|------|-------|
| M-04 | Chat Page Polish | build | Tier 1 | Chat |
| M-05 | Deal Workspace Polish | build | Tier 1 | Deal [id] |
| M-06 | Actions Command Center Polish | build | Tier 1 | Actions |
| M-07 | Quarantine + Deals List | build | Tier 2 | Quarantine, Deals |
| M-08 | Agent Activity + Operator HQ | build | Tier 2 | Agent Activity, HQ |
| M-09 | Dashboard + Onboarding | build | Tier 3 | Dashboard, Onboarding |
| M-10 | Settings + New Deal | build | Tier 3 | Settings, New Deal |

**Every Phase 2 mission MUST include:**
1. Interaction closure checklist — every visible control mapped to real/degraded/hidden
2. Before/after screenshots at 3 breakpoints
3. Console error check (zero errors required)
4. Contract compliance check — no client-side `.length`, proper stage source, 502 not 500
5. At least 2 new E2E tests for covered pages
6. nuqs adoption where manual URLSearchParams exist (M-07 specifically)

**Playwright usage:** Start with "before" screenshots, end with "after" at all breakpoints. Console checked before and after. Accessibility tree diffed.

### Phase 3: Integration Sweep (2 QA Missions)

| # | Mission | Type | Scope |
|---|---------|------|-------|
| M-11 | Cross-Page Flows + Visual Regression Suite | QA | All pages |
| M-12 | Accessibility Sweep (deferrable) | QA | All pages |

**M-11 scope:** End-to-end user journeys (create deal → navigate → add action → quarantine → approve; chat → proposal → execute → verify in workspace). Permanent `visual-regression.spec.ts` and `responsive-regression.spec.ts`. Full flow matrix across cross-route journeys.
**M-12 scope (deferrable):** Keyboard navigation sweep, focus trapping in modals, color contrast verification, basic screen reader compatibility. Include basic checks in M-11 if M-12 is deferred.
**Playwright usage:** Both missions are Playwright-heavy. M-11 captures the final visual baseline for CI.

### Mission Dependency Graph

```
M-00 (Phase 0)
  └── M-01, M-02, M-03 (Phase 1, parallel-safe)
        └── M-04 through M-10 (Phase 2, parallel-safe within tier)
              └── M-11 (Phase 3)
                    └── M-12 (Phase 3, deferrable)
```

**Total: 13 missions** (1 recon, 3 cross-cutting build, 7 page build, 2 QA)

---

## ACCEPTANCE GATES

### Gate 0: Phase 0 Complete (Recon)
**Command:** Verify artifact directory contains 36+ screenshots + findings catalog
**Pass criteria:**
- All 12 pages captured at 375/768/1280px
- Console error catalog complete
- Findings categorized as cross-cutting vs page-specific
- Priority ranking assigned to all findings
- Interaction wiring inventory for all pages

### Gate 1: Phase 1 Complete (Foundation)
**Command:** `make validate-local && cd apps/dashboard && npx tsc --noEmit`
**Pass criteria:**
- Shared `EmptyState`, `PageLoading`, `PageError` components exist and are used
- All 12 pages have `loading.tsx`
- All 13 `error.tsx` files refactored to <15 lines each
- Shared `<PageHeader />` component used by all pages
- `Promise.allSettled` used for all multi-fetch page loads
- Zero client-side `.length` for display counts
- All backend failure responses return JSON 502 (not 500)
- `PIPELINE_STAGES` used as stage source (no hardcoded arrays)
- `validate-surface9.sh` extended and passing
- Screenshots at 3 breakpoints show consistent loading/error/empty states

### Gate 2: Phase 2 Complete (Per Mission)
**Command:** `npx tsc --noEmit && make validate-local` + Playwright evidence review
**Pass criteria (per mission):**
- Interaction closure checklist: 100% of visible controls mapped
- Before/after screenshots at 375/768/1280px archived
- Zero `console.error` at all breakpoints
- Contract compliance verified (no banned patterns)
- At least 2 new E2E tests added and passing
- No regression in existing E2E tests

### Gate 3: Phase 3 Complete (Integration)
**Command:** `npx playwright test && make validate-local && make validate-full`
**Pass criteria:**
- All cross-page flows complete without error
- `visual-regression.spec.ts` exists and passes in CI
- `responsive-regression.spec.ts` exists and passes in CI
- Zero open Sev-1/Sev-2 UI defects
- Interaction closure matrix complete for all pages
- Basic keyboard navigation works across all pages
- `make validate-full` passes (all 14 surfaces)

### Definition of Done (Entire Initiative)
The dashboard UI masterplan is complete when ALL of the following are true:
1. **Visual parity:** Every page looks intentional and consistent at 375px, 768px, and 1280px in both light and dark mode
2. **Zero console.error:** No page produces console.error messages under normal operation (with or without backend)
3. **All interactions wired:** Every button, link, form, and interactive element does something meaningful or is explicitly degraded — no silent mock success
4. **Consistent states:** Every data component handles loading, empty, and error states using shared components
5. **Convention compliance:** All data fetching uses `Promise.allSettled`, server-side counts, canonical stage source, JSON 502 for backend failure
6. **E2E coverage:** Every page has at least 2 E2E tests covering primary interaction flows
7. **Visual regression baseline:** Permanent Playwright screenshot suite exists in CI
8. **Responsive verification:** All pages pass layout checks at 3 breakpoints
9. **Type safety:** `npx tsc --noEmit` passes with zero errors
10. **Contract compliance:** `make validate-local` passes with zero errors
11. **Interaction closure matrix:** Complete and archived for all pages

---

## RISK REGISTER

| # | Risk | Probability | Impact | Mitigation |
|---|------|------------|--------|-----------|
| R-1 | Phase 0 reveals more cross-cutting issues than expected | Medium | High | Phase 1 can expand; M-03 scope is adjustable |
| R-2 | Chat page too complex for single session | Medium | Medium | Allow prep commit to extract components before polish mission |
| R-3 | Playwright MCP unavailable during sessions | Low | High | Degrade to manual curl + visual inspection; `make validate-live` |
| R-4 | Fixing one page breaks another via shared CSS | Medium | High | Phase 1 locks shared styles first; `make validate-local` after every mission |
| R-5 | Dark mode inconsistencies compound | Medium | Medium | Phase 0 captures dark mode screenshots; Phase 1 audits CSS variables |
| R-6 | Backend unavailable during QA | Low | Medium | `graceful-degradation.spec.ts` covers this; Phase 3 extends it |
| R-7 | Scope creep — "fix" becomes "add features" | Medium | High | Mission prompts explicitly state: NO new features, only fix and polish |
| R-8 | B7 anti-convergence rule confuses builder agents | Medium | Medium | Every mission prompt clarifies: B7 does not apply to this initiative (F-11) |
| R-9 | Mock endpoints mask broken flows until late | Medium | High | Interaction closure checklist mandatory per mission (F-8) |

---

## STATISTICS

- Total Pass 1 findings across all agents: 22 (Claude: 10 + 5 AO, Gemini: 4 + 2 AO, Codex: 8 + 3 AO)
- Deduplicated primary findings: 12
- Discarded (with reason): 4
- Drift items: 6
- Adjacent observations merged into findings: 6 (legacy breadcrumbs, diligence TODO, nuqs, UI test page, B7 tension, callback ref)
- Drop rate: 0% (all 22 Pass 1 findings + 10 adjacent observations accounted for as either primary finding, merged item, discarded item with reason, or drift log entry)
