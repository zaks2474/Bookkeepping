# TriPass — Pass 2: Cross-Review and Deduplication

## Agent Identity
**Agent**: GEMINI
**Run ID**: TP-20260211-160514
**Pipeline Mode**: design
**Timestamp**: 2026-02-11T16:15:01Z

---

## Mission (Original)

# TriPass Strategic Mission: Dashboard UI Masterplan

## Mission Type: Strategy / Design
## Date: 2026-02-11
## Requested By: ZakOps Principal

---

## 1. Mission Objective

Produce a **single master strategy** for bringing the ZakOps dashboard to world-class quality. The platform has been built incrementally and now contains visual inconsistencies, unwired interactions, misaligned components, and unpolished flows across multiple pages. We are NOT adding features — we are fixing and perfecting everything that already exists.

---

## 2. Context

### Platform State
- **Stack:** Next.js 15 + shadcn/ui + Tailwind CSS, backend FastAPI (port 8091), Agent API (port 8095)
- **Dashboard:** Located at `/home/zaks/zakops-agent-api/apps/dashboard`, runs on port 3003
- **Pages/Tabs:** Dashboard (pipeline overview), Deal Detail/Workspace, Quarantine, Chat, Agent Activity, Onboarding, Setup, Settings, and potentially others
- **Known issues:** Visual inconsistencies across pages, varying design patterns, components built at different times with different standards, some buttons/interactions not fully wired, responsive breakpoints untested
- **Infrastructure:** 14 contract surfaces, 7 hooks, 8 skills, Playwright MCP (22 browser tools for visual verification), TriPass pipeline, mission prompt standard v2.1

### Architectural Constraints (MANDATORY — do not violate)
- `Promise.allSettled` with typed empty fallbacks for multi-fetch (Promise.all is banned)
- `PIPELINE_STAGES` from `execution-contracts.ts` is the single source of truth for stages
- Server-side deal counts only — no client-side `.length` counting
- All `/api/*` through Next.js middleware proxy, JSON 502 on backend failure
- Import from bridge files (`@/types/api`, `@/types/agent-api`), never from generated files
- `caret-color: transparent` globally with input/textarea override to `auto`
- Design system rule at `.claude/rules/design-system.md` auto-loads for dashboard files

### New Capability: Playwright MCP
We now have 22 Playwright browser tools available as MCP tools within Claude Code:
- `browser_navigate`, `browser_take_screenshot`, `browser_snapshot`
- `browser_resize`, `browser_console_messages`, `browser_click`
- `browser_evaluate`, `browser_network_requests`, `browser_run_code`
- This means Claude Code can now SEE the UI, take screenshots, check console errors, and verify rendering at any breakpoint
- This is a game-changer for quality assurance and should be central to any strategy

---

## 3. The Strategic Question

We need to decide the optimal approach to systematically fix and polish the entire dashboard. Three candidate strategies have been identified:

### Strategy A: Tab-by-Tab (Bottom-Up)
- Pick one page at a time (Dashboard → Detail → Quarantine → Chat → etc.)
- For each page: audit every component, every interaction, every visual element
- Fix everything until that page is perfect, then move to the next
- **Pro:** Focused, delivers complete pages incrementally
- **Risk:** May fix shared components differently per page, causing rework. Cross-cutting issues discovered late.

### Strategy B: Top-Down Blueprint
- First, design a comprehensive UI blueprint: visual system, layout structure, interaction patterns, state management, component behavior rules
- Then restructure everything to match the blueprint
- **Pro:** Ensures consistency from the start
- **Risk:** Abstract, slow, may not account for real-world constraints discovered during implementation. Over-engineering risk.

### Strategy C: Hybrid (Proposed by Claude)
- **Phase 0:** Reconnaissance sprint — Playwright screenshots of every page at 3 breakpoints, full catalog of all findings, categorized as cross-cutting vs page-specific. No code changes.
- **Phase 1:** Cross-cutting foundation — fix shared components, navigation, layout, typography, color, loading/error/empty states first. This prevents inconsistency.
- **Phase 2:** Page-by-page polish — now safe to go tab-by-tab because shared foundation is locked. Each page gets its own mission.
- **Phase 3:** Integration sweep — cross-page flows, full responsive regression, contract compliance across all 14 surfaces.
- **Pro:** Evidence-based, prevents fixing things twice, shared foundation cascades to all pages
- **Risk:** Phase 0 adds upfront time. Total estimated missions: 10-12.

---

## 4. What Each Agent Must Deliver

Each agent must produce a **strategy recommendation** covering:

1. **Chosen approach** (A, B, C, or your own D/E/F) with clear justification
2. **Phase breakdown** — what phases, what order, what each phase delivers
3. **Mission structure** — how many missions, what scope each, what type (recon/build/QA)
4. **Playwright integration** — how and when to use the 22 browser tools for maximum impact
5. **Risk mitigation** — what could go wrong and how each phase prevents it
6. **Regression prevention** — how to ensure fixing one thing doesn't break another
7. **Quality gates** — what criteria must each phase meet before proceeding to the next
8. **Continuous improvement** — how findings from each phase feed into the next
9. **Estimated shape** — rough number of missions, order, dependencies
10. **One thing the other strategies get wrong** — what critical flaw exists in the approaches you didn't choose

---

## 5. Evaluation Criteria

The master strategy will be judged on:
- **Minimizes wasted effort** — no fixing things twice, no over-engineering
- **Maximizes confidence** — evidence-based decisions, not assumptions
- **Ensures long-term stability** — regression prevention built into process
- **Aligns with existing infrastructure** — leverages 14 contracts, mission prompt standard, TriPass, Playwright MCP
- **Actionable** — the strategy should be immediately executable as mission prompts
- **Measurable** — clear definition of "done" for the entire initiative

---

## 6. Codebase Entry Points for Investigation

Agents should examine these to ground their strategy in reality:

- **Dashboard pages:** `apps/dashboard/src/app/` — all route directories
- **Components:** `apps/dashboard/src/components/` — shared and page-specific
- **Styles:** `apps/dashboard/src/styles/` — global CSS, theme tokens
- **Types:** `apps/dashboard/types/` — bridge types, execution contracts
- **E2E tests:** `apps/dashboard/tests/e2e/` — 9 existing test files
- **Design system rule:** `.claude/rules/design-system.md` — current UI standards
- **Frontend skill:** `/home/zaks/.claude/skills/frontend-design/SKILL.md`
- **Backend API spec:** `packages/contracts/openapi/zakops-api.json`

---

## 7. Constraints

- Do NOT produce code. This is a strategy-only mission.
- Do NOT propose adding new features. Only fix and polish what exists.
- Do NOT violate the architectural patterns listed in Section 2.
- The strategy must be executable using our existing mission prompt standard (v2.1).
- Each recommended mission must be scoped to fit a single Claude Code session.
- Playwright MCP integration must be a first-class citizen in the strategy, not an afterthought.

---

## 8. Deliverable Format

Your final output must be a structured strategy document with:
- Executive summary (3-5 sentences)
- Chosen approach with justification
- Phase-by-phase breakdown with clear deliverables
- Mission inventory (numbered list with scope and type)
- Quality gates per phase
- Risk register with mitigations
- How Playwright MCP is used in each phase
- Definition of "done" for the entire initiative

---

## Pass 1 Reports

You have access to all three Pass 1 reports:

### Report A (CLAUDE)
The sandbox prevents writing to the bookkeeping directory. The report is written at:

**`/home/zaks/zakops-agent-api/.tripass/TP-20260211-160514/01_pass1/claude_report.md`**

You'll need to copy it to the intended location:
```bash
cp /home/zaks/zakops-agent-api/.tripass/TP-20260211-160514/01_pass1/claude_report.md \
   /home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/01_pass1/claude_report.md
```

---

## Pass 1 Report Summary

**Strategy Recommendation: Strategy C (Hybrid) — Refined**

10 primary findings, organized around a 12-mission, 4-phase execution plan:

| Phase | Missions | Focus |
|-------|----------|-------|
| **0: Recon** | 1 | Playwright screenshots of all 12 pages at 3 breakpoints (36 screenshots), findings catalog |
| **1: Cross-Cutting** | 2-3 | Loading/empty/error state consistency, layout/nav/CSS audit, optional API client rationalization |
| **2: Page Polish** | 7 | Tier 1 (Chat, Deal Workspace, Actions) get solo missions; Tier 2-3 pages grouped |
| **3: Integration** | 2 | Cross-page flows, visual regression suite, accessibility {{PASS1_REPORT_A}} performance |

**Key insight:** The shadcn/ui foundation is already solid — the real problems live at the page composition layer. Phase 1 is narrower than originally proposed; Phase 2 is the dominant effort.

**Critical lever:** Playwright MCP (22 browser tools) is the game-changer — Claude Code can now *see* the UI during development, not just edit code blind. Every phase uses it as a first-class tool.

### Report B (GEMINI)
I will start by creating the directory for the report as requested in the instructions.
I will list the files in `apps/dashboard/src/components` and `apps/dashboard/src/app` to understand the structure and potential inconsistencies.
I will list the contents of `apps/dashboard/src/components/ui` and search for `Promise.all` in the codebase to identify architectural violations.
I will read the content of the `page.tsx` files for `dashboard`, `deals`, and `quarantine` to compare their implementation patterns and identify inconsistencies.
I will list the contents of the `apps/dashboard/tests/e2e` directory to understand the existing test coverage and identify gaps for the new Playwright MCP tools.
I will read the contents of `apps/dashboard/src/app/layout.tsx` and `apps/dashboard/src/lib/api.ts` to understand the global layout structure and API integration patterns.
I will list the contents of the `apps/dashboard/src/lib` directory to verify if there are accessible API-related files or definitions.
I will read the `.gitignore` file in `apps/dashboard` to verify if `src/lib/api.ts` is explicitly ignored and to understand the project's ignore rules.
I will write the "Pass 1" report to `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/01_pass1/gemini_report.md` detailing the findings on inconsistent page shells, divergent data fetching, fragmented UI states, and the lack of a visual regression baseline, ultimately recommending Strategy C.
I will list the contents of the `docs` directory to check for a `_tripass_runs` subdirectory and determine the appropriate location to save the report within the allowed workspace.
I will create the directory `docs/_tripass_runs/TP-20260211-160514/01_pass1/` within the repository and save the report there, as I cannot write outside the allowed workspace.
I have completed the "Pass 1" investigation for the TriPass mission.

I analyzed the dashboard codebase, specifically the `Dashboard`, `Deals`, and `Quarantine` pages, along with shared components and configuration.

**Key Findings:**
1.  **Inconsistent Page Shells:** Each page reimplements headers and layout logic, leading to visual drift.
2.  **Divergent Data Fetching:** `Dashboard` correctly uses `Promise.allSettled`, while others use single awaits, risking partial failure handling.
3.  **Fragmented UI States:** Loading skeletons and empty states are ad-hoc and inconsistent across pages.
4.  **No Visual Baseline:** Existing tests are functional; there is no protection against visual regression during a UI polish.

**Recommendation:**
I strongly recommend **Strategy C (Hybrid)**. We must start with **Phase 0** to establish a visual baseline using the new Playwright MCP tools (`browser_snapshot`) before any code changes. This enables safe refactoring of shared components in **Phase 1**, followed by page-specific polish in **Phase 2**.

The report has been saved to:
`docs/_tripass_runs/TP-20260211-160514/01_pass1/gemini_report.md`
(Note: Saved within the project `docs` directory as the requested `/home/zaks/bookkeeping` path was outside the allowed workspace).

### Report C (CODEX)
I could not write to `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/01_pass1/codex_report.md` because this session is running in a read-only sandbox (`Permission denied` on write attempts).  
Here is the complete report content:

```markdown
# Pass 1 Report — CODEX
## Run: TP-20260211-160514 | Mode: design
## Generated: 2026-02-11T16:05:18Z

## EXECUTIVE SUMMARY
The recommended strategy is **C (Hybrid)** with a strict sequence: reconnaissance baseline, cross-cutting foundation, page-by-page polish, and integration sweep. The codebase currently shows both shared-system drift (duplicated shells, convention violations, inconsistent API failure contracts) and page-specific UX defects, so pure tab-by-tab (A) and pure blueprint-first (B) each fail in different ways. Playwright must lead Phase 0 and remain embedded in every subsequent phase because current E2E coverage is largely non-visual and desktop-only. The initiative should run as **11 missions** with hard quality gates between phases, and a final definition of done tied to contract compliance, responsive parity, and zero-regression evidence.

## PRIMARY FINDINGS

### Finding 1: Strategy C Is The Correct Choice; A and B Each Miss A Critical Failure Mode
**Root Cause:** The repo has simultaneous **cross-cutting** and **page-local** problems. Cross-cutting: the app shell is duplicated in many layouts (`apps/dashboard/src/app/dashboard/layout.tsx:1`, `apps/dashboard/src/app/deals/layout.tsx:1`, `apps/dashboard/src/app/quarantine/layout.tsx:1`, `apps/dashboard/src/app/chat/layout.tsx:1`, `apps/dashboard/src/app/actions/layout.tsx:1`, `apps/dashboard/src/app/hq/layout.tsx:1`, `apps/dashboard/src/app/onboarding/layout.tsx:1`, `apps/dashboard/src/app/agent/activity/layout.tsx:1`). Page-local: interaction and rendering behavior diverges per route (for example, different scroll strategies under `overflow-hidden` body: `apps/dashboard/src/app/layout.tsx:53`, `apps/dashboard/src/app/dashboard/page.tsx:148`, `apps/dashboard/src/app/deals/page.tsx:306`, `apps/dashboard/src/app/quarantine/page.tsx:302`, `apps/dashboard/src/app/settings/page.tsx:97`).
**Fix Approach:** Choose **Hybrid C** with four phases: Phase 0 recon (no code changes), Phase 1 shared foundations, Phase 2 route missions, Phase 3 integration/regression sweep.
**Industry Standard:** This matches evidence-first modernization used in large UI remediation programs: baseline audit first, then shared primitives, then feature surfaces, then integrated regression hardening.
**System Fit:** This directly matches ZakOps constraints and drift profile: strong design-system conventions exist (`apps/dashboard/src/types/design-system-manifest.ts:22`, `apps/dashboard/src/types/design-system-manifest.ts:67`, `apps/dashboard/src/types/design-system-manifest.ts:84`) but are not uniformly applied yet.
**Enforcement:** Require a phase gate that blocks any page-polish mission until recon inventory and foundation checklist are complete and signed off.

### Finding 2: Mission Plan Should Be 11 Sessions With Explicit Dependencies
**Root Cause:** Scope breadth is large (9 primary nav surfaces in `apps/dashboard/src/config/nav-config.ts:6`) and currently heterogeneous in implementation style and API behavior (`apps/dashboard/src/app/api` route surface shows mixed degradation strategies and placeholders, e.g., `apps/dashboard/src/app/api/chat/execute-proposal/route.ts:16`, `apps/dashboard/src/app/api/chat/session/[sessionId]/route.ts:17`, `apps/dashboard/src/app/api/actions/[id]/archive/route.ts:38`).
**Fix Approach:** Use this mission inventory:
1. `M0` Recon Baseline (recon): Playwright capture matrix + issue catalog by route/component/state.
2. `M1` Shared Shell Consolidation (build): replace duplicated route layouts with one shell group.
3. `M2` Shared State/Status/Token Foundation (build): normalize status badges, spacing, typography, color token usage.
4. `M3` API Failure Contract Alignment (build): standardize backend-unavailable responses and UI degradation behavior.
5. `M4` Dashboard + HQ Polish (build).
6. `M5` Deals List + Deals New Polish (build).
7. `M6` Deal Workspace/Detail Polish (build).
8. `M7` Quarantine + Actions Polish (build).
9. `M8` Chat + Agent Activity Polish (build).
10. `M9` Onboarding + Settings Polish (build).
11. `M10` Integration Sweep + Responsive/Flow Regression (QA).
Dependencies: `M0 -> M1/M2/M3 -> M4..M9 -> M10`.
**Industry Standard:** Session-scoped vertical slices with dependency gates are standard for multi-page UX remediation to minimize rework.
**System Fit:** This mapping aligns with existing route boundaries and reusable UI primitives while keeping each mission within one Claude Code session.
**Enforcement:** Track every mission in a single backlog sheet with fields: route, component, issue class, severity, fix status, verification artifact link.

### Finding 3: Playwright Must Be Embedded In Every Phase, Not Only Final QA
**Root Cause:** Current automated coverage is weak for visual/responsive regressions: Playwright is configured only for desktop Chromium (`apps/dashboard/playwright.config.ts:15`), and tests are mostly visibility + timeout based (`apps/dashboard/tests/e2e/chat-shared.spec.ts:7`, `apps/dashboard/tests/e2e/dashboard-worldclass-remediation.spec.ts:55`, `apps/dashboard/tests/e2e/no-dead-ui.spec.ts:122`). The design rule already expects 375/768/1280 verification (`.claude/rules/design-system.md:145`) and Playwright MCP workflow (`.claude/rules/design-system.md:82`).
**Fix Approach:**
- Phase 0: For each route, collect `browser_navigate`, `browser_resize` (375/768/1280), `browser_take_screenshot`, `browser_console_messages`, `browser_network_requests`, and `browser_snapshot` artifacts.
- Phase 1/2: Every PR-sized mission must include before/after screenshots for touched routes + at least one critical interaction replay.
- Phase 3: Full flow matrix across cross-route journeys (dashboard -> deals -> detail -> actions -> quarantine -> settings -> chat).
**Industry Standard:** Visual regression plus runtime console/network capture is the current best practice for UI stabilization.
**System Fit:** The project explicitly calls out Playwright MCP as available and central to quality; this approach uses that capability as intended.
**Enforcement:** A mission is blocked from completion unless its artifact bundle includes screenshots at 3 breakpoints and console/network logs with zero untriaged errors.

### Finding 4: Foundation Phase Must Resolve Shell/Scaffold Drift Before Any Route-Level Polish
**Root Cause:** Core scaffolding is fragmented: duplicated shell layouts across routes (multiple files above), an unused shared container (`apps/dashboard/src/components/layout/page-container.tsx:20` with no call sites), and divergent route scroll/container patterns while body is globally locked (`apps/dashboard/src/app/layout.tsx:53`).
**Fix Approach:** In Phase 1, implement one canonical app-shell layout group, one canonical page scaffold pattern, and one canonical loading/error template family; migrate all routes to it before page-specific aesthetic passes.
**Industry Standard:** Consolidate layout primitives first to reduce defect multiplication and avoid repeated fixes.
**System Fit:** The existing UI stack (shadcn + Tailwind + shared sidebar/header) is already componentized, so convergence cost is low and payoff is high.
**Enforcement:** Add lint/rule checks that reject new duplicated route shell layouts and require scaffold usage for top-level routes.

### Finding 5: Contract Compliance Drift Is Real and Must Be Treated As A First-Class Workstream
**Root Cause:** Current code deviates from declared conventions. Examples:
- Hardcoded stage array despite canonical stage source rule (`apps/dashboard/src/types/design-system-manifest.ts:76`, `apps/dashboard/src/app/deals/new/page.tsx:20`).
- Client-side `.length` display counting despite server-count convention (`apps/dashboard/src/types/design-system-manifest.ts:67`, `apps/dashboard/src/app/dashboard/page.tsx:209`, `apps/dashboard/src/app/deals/page.tsx:220`).
- Backend failure status inconsistency (500 in dedicated API routes) despite JSON 502 convention (`apps/dashboard/src/types/design-system-manifest.ts:84`, `apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts:49`, `apps/dashboard/src/app/api/chat/complete/route.ts:59`, `apps/dashboard/src/app/api/chat/execute-proposal/route.ts:34`).
**Fix Approach:** Add a dedicated contract-compliance subphase (within `M3`) to normalize stage sources, server-count usage, and failure status semantics before polish missions continue.
**Industry Standard:** Treat architecture contract drift as a blocking quality defect, not a cleanup backlog.
**System Fit:** ZakOps already has explicit convention manifests/rules; this phase operationalizes them.
**Enforcement:** Extend `tools/infra/validate-surface9.sh` beyond current checks (`tools/infra/validate-surface9.sh:14`) to include banned client display counts and non-502 backend-unavailable responses.

### Finding 6: Interaction Wiring Is Inconsistent (Placeholders + Mock Success Paths)
**Root Cause:** Several endpoints intentionally return placeholders or mock success, which hides real integration state:
- Proposal execution not implemented: `apps/dashboard/src/app/api/chat/execute-proposal/route.ts:16`.
- Chat session persistence placeholder: `apps/dashboard/src/app/api/chat/session/[sessionId]/route.ts:17`.
- Mock archival fallback when backend absent: `apps/dashboard/src/app/api/actions/[id]/archive/route.ts:54`.
- Mock bulk archive fallback: `apps/dashboard/src/app/api/actions/bulk/archive/route.ts:68`.
- Mock completed-count fallback values: `apps/dashboard/src/app/api/actions/completed-count/route.ts:53`.
**Fix Approach:** Add explicit “interaction closure” checklist per page mission: every visible control must map to one of: real endpoint, intentionally degraded endpoint with explicit UI state, or removed/hidden until integrated.
**Industry Standard:** UX hardening requires truthful interaction semantics; silent mock success is acceptable only in dedicated test/sandbox surfaces.
**System Fit:** ZakOps explicitly targets “no dead UI” and already has E2E intent for this (`apps/dashboard/tests/e2e/no-dead-ui.spec.ts:1`).
**Enforcement:** Introduce an interaction-matrix test that fails if production routes return mock success signatures on critical actions.

### Finding 7: Regression Gates Need Hardening; Current Tests Contain Weak Pass Conditions
**Root Cause:** Existing regression safeguards are insufficient: one assertion is tautological (`apps/dashboard/tests/e2e/quarantine-actions.spec.ts:56`), many tests depend on static sleeps (`apps/dashboard/tests/e2e/dashboard-worldclass-remediation.spec.ts:55`, `apps/dashboard/tests/e2e/no-dead-ui.spec.ts:122`), and validator coverage is narrow (`tools/infra/validate-surface9.sh:14` through `tools/infra/validate-surface9.sh:57`).
**Fix Approach:** Define mandatory quality gates by phase:
- Phase 0 gate: complete issue catalog with severity + owner + artifact links.
- Phase 1 gate: shell/scaffold/token convergence + contract validator pass.
- Phase 2 gate (per route): interaction checklist pass + no console errors + responsive screenshot triad.
- Phase 3 gate: full flow regression pass + contract surface checks + no open Sev-1/Sev-2 UI defects.
Program-level Definition of Done: all nav routes pass 375/768/1280 checks, no unwired primary actions, architecture conventions pass automated checks, and cross-route flows are artifact-verified.
**Industry Standard:** Deterministic gates (artifact + assertion based) are required for stable UI remediation at scale.
**System Fit:** This complements existing TriPass and validation scripts without introducing new infrastructure.
**Enforcement:** Add CI jobs that fail on missing artifact bundles, weak assertions, or validator regressions.

### Finding 8: Critical Flaws In The Rejected Strategies
**Root Cause:**
- Strategy A flaw: It would repeatedly re-touch shared shell/state patterns because those are currently duplicated and inconsistent across routes (`apps/dashboard/src/app/dashboard/layout.tsx:1` and peers).
- Strategy B flaw: It can over-specify abstractly while real integration paths still contain placeholders/mocks (`apps/dashboard/src/app/api/chat/execute-proposal/route.ts:16`, `apps/dashboard/src/app/api/chat/session/[sessionId]/route.ts:17`, `apps/dashboard/src/app/api/actions/bulk/archive/route.ts:53`).
**Fix Approach:** Keep Strategy C and enforce “evidence before implementation” with phase gates.
**Industry Standard:** Hybrid audit + foundation + vertical remediation is the proven compromise between local optimization and abstract overdesign.
**System Fit:** ZakOps has enough existing structure to standardize quickly, but enough drift that empirical recon is mandatory.
**Enforcement:** Reject mission prompts that skip recon artifacts or attempt page polish before foundation gates pass.

## ADJACENT OBSERVATIONS
- `apps/dashboard/src/hooks/use-breadcrumbs.tsx:14` and `apps/dashboard/src/hooks/use-breadcrumbs.tsx:18` still include legacy route mappings (`/dashboard/employee`, `/dashboard/product`) that are not part of current route inventory.
- `apps/dashboard/src/app/ui-test/page.tsx:225` includes `alert(...)` and mock data flows; useful for sandboxing, but should remain isolated from production QA metrics.
- `apps/dashboard/src/components/diligence/useDiligence.ts:123` contains TODO placeholders for API replacement, which indicates another partially integrated surface outside this mission’s immediate tab list.

## SUMMARY
- Total primary findings: 8
- Total adjacent observations: 3
- Confidence level: HIGH
- Key recommendation: Execute Strategy C as an 11-mission program with Playwright-first recon, foundation-first standardization, and hard phase gates tied to contract compliance and responsive visual evidence.
```

---

## Instructions

You are reviewing all three independent investigation reports. Your job is to:

1. **Identify duplicates** — findings that multiple agents reported (high confidence items)
2. **Identify conflicts** — findings where agents disagree on root cause or fix approach
3. **Identify unique findings** — items only one agent found (potential blind spot coverage)
4. **Verify evidence** — check that cited file:line references are accurate
5. **Flag drift** — note any findings that fall outside the declared mission scope

### Output Format

Write your cross-review to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/02_pass2/gemini_review.md`

Begin with exactly this header:

```
# Pass 2 Cross-Review — GEMINI
## Run: TP-20260211-160514 | Mode: design
## Generated: 2026-02-11T16:15:01Z
```

Then organize as:

```
## DUPLICATES (High Confidence)
Items found by 2+ agents. Merge into a single entry with attribution.

### D-1: [Merged Title]
**Reported by:** Agent A (Finding X), Agent B (Finding Y)
**Consensus root cause:** ...
**Consensus fix:** ...
**Evidence verified:** YES/NO

(repeat)

## CONFLICTS
Items where agents disagree. State both positions with evidence.

### C-1: [Conflict Title]
**Agent A position:** ...
**Agent B position:** ...
**Evidence comparison:** ...
**Recommended resolution:** ...

(repeat)

## UNIQUE FINDINGS
Items found by only one agent. Verify if the finding is valid.

### U-1: [Title] (from Agent X)
**Verification:** CONFIRMED / UNVERIFIED / INVALID
**Evidence check:** ...
**Should include in final:** YES / NO (with reason)

(repeat)

## DRIFT FLAGS
Findings that fall outside declared scope.

### DRIFT-1: [Title] (from Agent X)
**Why out of scope:** ...
**Severity if ignored:** ...

## SUMMARY
- Duplicates: N
- Conflicts: N
- Unique valid findings: N
- Drift items: N
- Overall assessment: ...
```
