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