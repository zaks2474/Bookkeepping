# MISSION: UI-MASTERPLAN-M10
## Settings + New Deal Polish - Responsive Configuration UX, Degraded-State Truthfulness, and Create-Flow Reliability
## Date: 2026-02-12
## Classification: Page-Level UX Hardening (Tier 3)
## Prerequisite: UI-MASTERPLAN-M09 complete
## Successor: Phase 3 integration sweep (M-11)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m10-artifacts/`

---

## Mission Objective
Close Settings + New Deal mission scope by resolving F-15 disposition and F-16 follow-through in Settings, while hardening `/deals/new` create-flow UX and interaction closure across breakpoints.

This mission is page-level UX hardening for `/settings` and `/deals/new`. It is not a backend settings-feature build and not a data-model redesign mission.

Out of scope: new provider/integration features, account-deletion workflow redesign, and broad settings architecture replacement.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

M-00 evidence driving this mission:
- F-15 (Sev-3): Settings uses a distinct layout pattern versus primary shell; requires explicit consistency decision/disposition.
- F-16 (Sev-2): Settings had 404 behavior and duplicate preferences fetch observation; M-03 classified core contract behavior and normalized APIs, but M-10 must validate final UX truthfulness and non-noisy behavior.

FINAL_MASTER scope expectation:
- M-10 includes Settings + New Deal in Tier 3, with standard Phase 2 requirements.

Current implementation center:
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useUserPreferences.ts`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/preferences/route.ts`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts`

Phase 2 per-mission requirements (FINAL_MASTER) apply:
- Interaction closure checklist
- Before/after screenshot triad at 375/768/1280
- Console audit
- Contract compliance preservation
- At least 2 new E2E tests in mission scope

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Layout disposition | Explicit determination of whether a divergent page pattern is intentional and acceptable |
| Degraded-state truthfulness | Unavailable backend features are communicated clearly without misleading success states |
| Create-flow reliability | `/deals/new` input, validation, submit, and redirect behavior works across breakpoints |
| Interaction closure | Every visible control classified as `real`, `degraded`, or `hidden` with rationale |

---

## Architectural Constraints
- **Primary scope lock:** Changes must remain focused on Settings and New Deal surfaces.
- **Truthful degraded UX:** Backend-unavailable or unavailable-feature states must be explicit and non-deceptive.
- **No backend scope creep:** Do not add new settings APIs or change business rules.
- **Preserve M-03 contracts:** Maintain JSON 502 semantics and prior API alignment outcomes.
- **Responsive integrity:** Settings sections/cards and New Deal form controls must remain readable/actionable at 375px.
- **No shell regression:** Do not destabilize M-02/M-09 shell and header foundations.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Divergent settings layout left undocumented
```text
Settings differs from shell but mission closes without explicit accept/fix rationale.
```

### RIGHT: Explicit layout disposition with evidence
```text
Mission records whether settings layout divergence is accepted, adjusted, or partially converged, with breakpoint proof.
```

### WRONG: 404/degraded states appear as broken UI
```text
Users see unclear failures or silent empties for unavailable settings integrations.
```

### RIGHT: Clear degraded disclosure
```text
Unavailable features render explicit status, explanation, and next-step guidance.
```

### WRONG: New Deal flow works only on desktop happy path
```text
Mobile users cannot reliably complete create/cancel/error flows.
```

### RIGHT: End-to-end reliable create flow
```text
At 375/768/1280, users can fill, submit, cancel, and recover from errors predictably.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Settings responsive polish regresses section navigation behavior | Medium | High | Verify desktop sidebar + mobile dropdown navigation at each gate |
| 2 | F-16 duplicate-fetch classification remains ambiguous | Medium | Medium | Capture dev vs production-mode network evidence and explicit disposition |
| 3 | Degraded-state messaging becomes inconsistent across sections | Medium | High | Use one disclosure pattern and verify in closure matrix |
| 4 | New Deal mobile fixes reduce desktop form clarity | Medium | Medium | Re-check form layout and CTA behavior at 1280 |
| 5 | Test coverage misses degraded-state and create-flow edge cases | Medium | Medium | Add E2E assertions for unavailable integrations and failed submit path |

---

## Phase 0 - Baseline and Boundary Snapshot
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Freeze pre-M10 state and define independent rollback boundary.

### Blast Radius
- **Services affected:** Settings and New Deal presentation/API-consumption surfaces
- **Pages affected:** `/settings`, `/deals/new`
- **Downstream consumers:** M-11 integration and Phase 2 completion gate

### Tasks
- P0-00: Capture M-09 boundary snapshot before M-10 edits.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m10-artifacts/reports/m09-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-10 rollback remains isolated.
- P0-01: Capture before screenshots + console logs at 375/768/1280 for `/settings` and `/deals/new`.
  - Evidence: `/home/zaks/bookkeeping/missions/m10-artifacts/before/`
  - Checkpoint: captures include section navigation, major cards, and create-form controls.
- P0-02: Build baseline interaction closure matrix.
  - Evidence: `/home/zaks/bookkeeping/missions/m10-artifacts/reports/interaction-closure.md`
  - Checkpoint: all visible controls across both pages are inventoried.
- P0-03: Capture settings fetch-behavior baseline (dev and production-mode classification).
  - Evidence: `/home/zaks/bookkeeping/missions/m10-artifacts/reports/settings-fetch-behavior.md`
  - Checkpoint: duplicate-fetch behavior is classified with concrete evidence.

### Decision Tree
- IF F-16 duplicate fetch appears only in dev StrictMode -> classify as non-app defect and preserve stable code path.
- ELSE -> implement dedupe fix and verify reduced request count.

### Rollback Plan
1. Keep baseline artifacts immutable.
2. Re-capture only if environment/data materially changes.

### Gate P0
- M-09 boundary snapshot exists.
- Before-state triad + console baseline exists for both pages.
- Interaction closure and fetch-behavior baseline reports are complete.

---

## Phase 1 - Settings Responsive Integrity and Layout Disposition
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Resolve F-15 by enforcing clear, evidence-backed settings layout behavior and responsive usability.

### Blast Radius
- **Services affected:** Settings page layout, section nav, section-card responsiveness
- **Pages affected:** `/settings`
- **Downstream consumers:** operator configuration workflows and consistency standards

### Tasks
- P1-01: Fix 375px/768px settings layout clipping and card overflow issues.
  - Primary paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/`
  - Checkpoint: content remains readable/actionable without clipped panels.
- P1-02: Validate desktop sidebar + mobile dropdown section navigation.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx`
  - Checkpoint: section jumps remain predictable and accessible.
- P1-03: Explicitly disposition F-15 (accept divergence, partial convergence, or full convergence) with rationale.
  - Evidence: `/home/zaks/bookkeeping/missions/m10-artifacts/reports/f15-layout-disposition.md`
  - Checkpoint: decision is documented and evidence-backed.

### Rollback Plan
1. Revert responsive layout changes that break navigation or section usability.
2. Re-apply with section-by-section adjustments and viewport assertions.

### Gate P1
- F-15 is resolved or explicitly dispositioned with evidence.
- Settings sections are readable and operable at 375/768/1280.
- Section navigation behavior is stable.

---

## Phase 2 - Settings Degraded-State Truthfulness + New Deal Create-Flow Closure
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Close F-16 follow-through and harden `/deals/new` interaction reliability.

### Blast Radius
- **Services affected:** Settings data hooks/API routes + New Deal form experience
- **Pages affected:** `/settings`, `/deals/new`
- **Downstream consumers:** configuration trust and deal-creation reliability

### Tasks
- P2-01: Verify and normalize degraded-state messaging for unavailable integrations/preferences paths.
  - Primary paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useUserPreferences.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/`
  - Checkpoint: unavailable states are explicit, non-misleading, and consistent.
- P2-02: Validate F-16 duplicate-fetch classification and apply dedupe only if production-reproducible.
  - Primary paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/preferences/route.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts`
  - Checkpoint: final classification and remediation (if needed) are evidenced.
- P2-03: Harden New Deal form for mobile/desktop interaction closure.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/page.tsx`
  - Checkpoint: create/cancel/validation/error/retry flows are usable at all target breakpoints.
- P2-04: Update interaction closure matrix with final dispositions for both pages.
  - Evidence: `/home/zaks/bookkeeping/missions/m10-artifacts/reports/interaction-closure.md`
  - Checkpoint: 100% visible-control coverage with `real/degraded/hidden` status.

### Decision Tree
- IF settings endpoint degradation is expected/unavailable-feature case -> render explicit unavailable state with guidance.
- ELSE IF degradation indicates unexpected backend failure -> preserve error path and classify for remediation.

### Rollback Plan
1. Revert dedupe or disclosure changes that obscure true system state.
2. Keep validated layout fixes while iterating behavior-specific adjustments.

### Gate P2
- F-16 is resolved, explicitly dispositioned, or confirmed non-app with evidence.
- New Deal create-flow closure verified at 375/768/1280.
- Interaction closure matrix complete and accurate.

---

## Phase 3 - Test Reinforcement, Validation, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Lock M-10 behavior with deterministic tests and complete evidence package.

### Blast Radius
- **Services affected:** Dashboard E2E + validation pipeline
- **Pages affected:** `/settings`, `/deals/new`
- **Downstream consumers:** M-11 integration and final Phase 2 gate

### Tasks
- P3-01: Add at least 2 mission-scoped E2E tests.
  - Candidate location: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/`
  - Suggested files:
    - `settings-mobile-layout-and-degraded-states.spec.ts`
    - `new-deal-responsive-create-flow.spec.ts`
  - Checkpoint: tests verify settings responsive truthfulness and create-flow reliability.
- P3-02: Run validation stack and archive transcript.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m10-artifacts/reports/validation.txt`
- P3-03: Publish closure and completion reports.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m10-artifacts/reports/findings-closure.md`
    - `/home/zaks/bookkeeping/missions/m10-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert flaky/new tests and stabilize selectors/assertions.
2. Revert only regressions while retaining validated fixes.

### Gate P3
- 2+ new M-10-focused E2E tests exist and pass.
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: F-15 disposition complete
Settings layout divergence is resolved or explicitly dispositioned with evidence.

### AC-2: F-16 follow-through complete
Settings fetch/degraded behavior is resolved, explicitly dispositioned, or documented as non-app with evidence.

### AC-3: Settings responsive integrity
Settings sections and controls are readable and operable at 375/768/1280.

### AC-4: New Deal interaction closure
`/deals/new` create/cancel/validation/error flows are reliable at target breakpoints.

### AC-5: Test reinforcement
At least 2 new M-10-focused E2E tests are added and passing.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Before/after triad, closure reports, and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not implement new settings backend features in this mission.
2. Do not redesign unrelated pages or global shell structures.
3. Keep changes scoped to Settings and New Deal UX hardening.
4. Preserve M-03 contract semantics and degraded-response conventions.
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m10-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic E2E assertions; avoid sleep-only gates.
8. Do not proceed into M-11 implementation from this mission.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Full settings architecture rewrite is **not applicable** in M-10.
- If duplicate preferences fetch is dev StrictMode-only, it is **not applicable** as a production defect (must be documented with evidence).

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture triad baseline for `/settings` and `/deals/new` at 375/768/1280?
- [ ] Did I map all visible controls in the interaction matrix?
- [ ] Did I classify settings fetch behavior in both dev and production modes?

### After each code change
- [ ] Did this change improve responsive integrity or degraded-state truthfulness?
- [ ] Did I preserve desktop behavior while fixing mobile?
- [ ] Did I avoid backend feature scope creep?

### Before marking COMPLETE
- [ ] Is F-15 explicitly resolved/dispositioned with evidence?
- [ ] Is F-16 resolved/dispositioned/non-app documented with evidence?
- [ ] Are settings cards/controls readable and operable at 375px?
- [ ] Is New Deal create-flow reliable at 375/768/1280?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I add at least 2 M-10-focused E2E tests?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx` | Phase 1 | Responsive layout and section framing |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx` | Phase 1 | Sidebar/dropdown navigation behavior and responsiveness |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/` | Phase 1-2 | Section-card responsiveness and degraded-state clarity |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useUserPreferences.ts` | Phase 2 | Fetch behavior and section-save UX coherence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/preferences/route.ts` | Phase 2 | F-16 behavior follow-through if required |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts` | Phase 2 | Unavailable/degraded semantics verification |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/page.tsx` | Phase 2 | Responsive create-flow hardening |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m10-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m10-artifacts/before/` | Phase 0 | Before screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m10-artifacts/after/` | Phase 2 | After screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/m09-boundary-snapshot.md` | Phase 0 | Pre-M10 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/interaction-closure.md` | Phase 0-2 | Control closure matrix |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/settings-fetch-behavior.md` | Phase 0-2 | F-16 classification and evidence |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/f15-layout-disposition.md` | Phase 1 | Explicit layout decision record |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/findings-closure.md` | Phase 3 | F-15/F-16 + New Deal closure summary |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion summary |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/settings-mobile-layout-and-degraded-states.spec.ts` | Phase 3 | New E2E test |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/new-deal-responsive-create-flow.spec.ts` | Phase 3 | New E2E test |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-15/F-16 baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Control inventory baseline |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/settings-fetch-behavior.md` | Prior F-16 classification context |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/findings-closure.md` | Adjacent mission context |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 2 requirements and mission map |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation passes, artifacts are complete, and bookkeeping is updated. Do not proceed into M-11 implementation from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M10*
