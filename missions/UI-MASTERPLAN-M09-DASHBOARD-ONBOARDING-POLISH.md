# MISSION: UI-MASTERPLAN-M09
## Dashboard + Onboarding Polish - Mobile Priority Visibility, State Coherence, and Guided Setup Clarity
## Date: 2026-02-12
## Classification: Page-Level UX Hardening (Tier 3)
## Prerequisite: UI-MASTERPLAN-M08 complete
## Successor: UI-MASTERPLAN-M10 and Phase 3 integration sweep (M-11)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m09-artifacts/`

---

## Mission Objective
Close Dashboard + Onboarding findings F-19, F-20, F-17, and F-18 by ensuring priority content is visible at mobile breakpoints, count semantics are coherent during load transitions, and onboarding flow guidance remains clear on small screens.

This mission is page-level UX hardening for `/dashboard` and `/onboarding`. It is not a backend analytics mission and not an onboarding feature-expansion project.

Out of scope: new onboarding capability design, pipeline metric model changes, and cross-domain refactors unrelated to Dashboard/Onboarding interaction quality.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

M-00 evidence driving this mission:
- F-19 (Sev-2): Dashboard "Today & Next Up" cards clip at 375px with partial second-card visibility.
- F-20 (Sev-3): Dashboard pipeline count messaging appears inconsistent during load transitions.
- F-17 (Sev-3): Onboarding resume banner consumes excessive vertical space and disrupts step flow.
- F-18 (Sev-3): Onboarding step labels are hidden at 375px, reducing orientation clarity.

Current implementation center:
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/TodayNextUpStrip.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingBanner.tsx`

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
| Priority-strip visibility | Ability to view and navigate priority cards in "Today & Next Up" without clipped context |
| State coherence | Consistent user-facing count semantics across loading and settled states |
| Setup orientation | User’s ability to know onboarding step position and next action on mobile |
| Interaction closure | Every visible control classified as `real`, `degraded`, or `hidden` with rationale |

---

## Architectural Constraints
- **Primary scope lock:** Keep changes focused on Dashboard and Onboarding pages/components.
- **No contradictory count messaging:** Avoid transient UI text that implies conflicting totals without clear loading context.
- **Mobile-first visibility:** 375px layout must preserve priority-card readability and onboarding orientation.
- **No backend semantic drift:** Preserve existing API contracts, stage source conventions, and M-03 alignment.
- **No shell regression:** Do not alter shared shell foundations stabilized by M-02.
- **No toast noise regression:** Preserve established dashboard refresh-toast behavior expectations.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Priority strip with clipped actionable cards
```text
At 375px, second priority card is partially visible and actions are ambiguous.
```

### RIGHT: Explicit mobile priority-card affordance
```text
At 375px, priority cards remain readable with clear horizontal scroll affordance and full-card access.
```

### WRONG: Count text shows inconsistent semantics during load
```text
Pipeline shows "0 active deals" while nearby widgets imply non-zero items without loading context.
```

### RIGHT: Coherent loading and settled count behavior
```text
Count surfaces share aligned semantics and avoid misleading transitional values.
```

### WRONG: Mobile onboarding hides step labels entirely
```text
Only icons are visible on 375px with no readable step names.
```

### RIGHT: Mobile onboarding preserves orientation
```text
Step labels remain discoverable (inline, compact, or toggled) while keeping layout usable.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Dashboard mobile fix masks clipping but hurts desktop scanning | Medium | High | Re-verify 1280 layout at each gate |
| 2 | Count coherence fix introduces stale/incorrect totals | Medium | High | Tie messaging to explicit loading states and source fields |
| 3 | Onboarding resume-banner reduction removes key recovery context | Medium | Medium | Preserve resume semantics while compacting visual footprint |
| 4 | Step-label visibility fix causes crowded/overlapping stepper at 375 | Medium | Medium | Use compact label strategy and verify tap targets |
| 5 | New tests miss transitional-state regressions | Medium | Medium | Add assertions for loading-to-settled state behavior |

---

## Phase 0 - Baseline and Boundary Snapshot
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Capture pre-M09 state and isolate rollback boundary.

### Blast Radius
- **Services affected:** Dashboard and Onboarding presentation surfaces
- **Pages affected:** `/dashboard`, `/onboarding`
- **Downstream consumers:** M-10 sequencing and M-11 integration sweep

### Tasks
- P0-00: Capture M-08 boundary snapshot before M-09 edits.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m09-artifacts/reports/m08-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-09 rollback can be performed independently.
- P0-01: Capture before screenshots + console logs at 375/768/1280 for Dashboard and Onboarding.
  - Evidence: `/home/zaks/bookkeeping/missions/m09-artifacts/before/`
  - Checkpoint: captures include Today & Next Up, pipeline card text, onboarding stepper, and resume banner.
- P0-02: Build baseline interaction closure matrix.
  - Evidence: `/home/zaks/bookkeeping/missions/m09-artifacts/reports/interaction-closure.md`
  - Checkpoint: all visible controls across both pages are inventoried.
- P0-03: Record baseline count-semantics matrix for Dashboard surfaces.
  - Evidence: `/home/zaks/bookkeeping/missions/m09-artifacts/reports/dashboard-count-semantics.md`
  - Checkpoint: each count label is mapped to source and loading behavior.

### Decision Tree
- IF F-19/F-20/F-17/F-18 are partially improved by prior mission work -> capture closure-by-foundation evidence and still complete explicit interaction closure and coherence checks.
- ELSE -> implement targeted responsive and state-coherence corrections.

### Rollback Plan
1. Keep baseline artifacts immutable.
2. Re-capture baseline only if data/environment state materially changes.

### Gate P0
- M-08 boundary snapshot exists.
- Before-state triad + console baseline exists.
- Interaction closure + count-semantics baseline reports are complete.

---

## Phase 1 - Dashboard Priority Visibility and Count Coherence
**Complexity:** L
**Estimated touch points:** 3-10 files

**Purpose:** Close F-19 and F-20 by improving mobile card visibility and count-message consistency.

### Blast Radius
- **Services affected:** Dashboard header/widgets/pipeline/priority strip
- **Pages affected:** `/dashboard`
- **Downstream consumers:** operational scanning reliability and confidence in displayed metrics

### Tasks
- P1-01: Fix 375px Today & Next Up card clipping and ensure clear navigation affordance.
  - Primary paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/TodayNextUpStrip.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - Checkpoint: cards are fully readable and actionable at 375px.
- P1-02: Align pipeline and related count messaging semantics across loading and settled states.
  - Checkpoint: no contradictory or misleading count text during data transitions.
- P1-03: Verify stage filter, approvals toggle, and refresh flow remain stable.
  - Checkpoint: control reachability and behavior preserved at 375/768/1280.

### Rollback Plan
1. Revert dashboard layout/state-message changes that regress readability or behavior.
2. Re-apply with narrower, breakpoint-specific adjustments and explicit loading-state handling.

### Gate P1
- F-19 resolved with 375px evidence.
- F-20 resolved or explicitly dispositioned with coherent count semantics evidence.
- Dashboard controls remain fully reachable and stable.

---

## Phase 2 - Onboarding Orientation and Resume-Flow Refinement
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Close F-17 and F-18 by improving mobile setup orientation and reducing resume-banner visual overhead.

### Blast Radius
- **Services affected:** Onboarding stepper/banner/navigation and related step components
- **Pages affected:** `/onboarding`
- **Downstream consumers:** first-run completion rate and guided setup clarity

### Tasks
- P2-01: Reduce resume-banner vertical footprint while preserving resume/start-fresh affordances.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx`
  - Checkpoint: banner remains informative without crowding core content.
- P2-02: Improve 375px stepper label discoverability.
  - Primary paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/page.tsx`
  - Checkpoint: users can identify current and upcoming steps on mobile.
- P2-03: Validate navigation controls (`Back`, `Next`, `Skip`, `Resume`, `Start Fresh`) across breakpoints.
  - Checkpoint: full interaction closure for onboarding flow.
- P2-04: Update interaction closure matrix with final dispositions.
  - Evidence: `/home/zaks/bookkeeping/missions/m09-artifacts/reports/interaction-closure.md`
  - Checkpoint: 100% visible-control coverage with `real/degraded/hidden` status.

### Decision Tree
- IF full labels cannot fit cleanly at 375px -> use compact label strategy with explicit current-step context.
- ELSE -> keep direct label visibility for all accessible steps.

### Rollback Plan
1. Revert stepper/banner changes that reduce onboarding clarity.
2. Keep validated dashboard fixes while iterating onboarding layout.

### Gate P2
- F-17 resolved with evidence.
- F-18 resolved with 375px evidence.
- Onboarding interaction closure matrix complete and accurate.

---

## Phase 3 - Test Reinforcement, Validation, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Lock M-09 behavior with deterministic tests and complete evidence package.

### Blast Radius
- **Services affected:** Dashboard E2E + validation pipeline
- **Pages affected:** `/dashboard`, `/onboarding`
- **Downstream consumers:** M-11 integration and regression suite consolidation

### Tasks
- P3-01: Add at least 2 mission-scoped E2E tests.
  - Candidate location: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/`
  - Suggested files:
    - `dashboard-mobile-priority-and-count-coherence.spec.ts`
    - `onboarding-mobile-orientation-and-resume.spec.ts`
  - Checkpoint: tests verify F-19/F-20 and F-17/F-18 closure behavior.
- P3-02: Run validation stack and archive transcript.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m09-artifacts/reports/validation.txt`
- P3-03: Publish closure and completion reports.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m09-artifacts/reports/findings-closure.md`
    - `/home/zaks/bookkeeping/missions/m09-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert flaky/new tests and stabilize selectors/assertions.
2. Revert only regressions while retaining validated fixes.

### Gate P3
- 2+ new M-09-focused E2E tests exist and pass.
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: F-19 resolved
Dashboard "Today & Next Up" cards are fully visible and actionable at 375px.

### AC-2: F-20 resolved or dispositioned
Dashboard count messaging is coherent across loading and settled states with evidence.

### AC-3: F-17 resolved
Onboarding resume banner no longer consumes excessive vertical space while preserving resume context.

### AC-4: F-18 resolved
Onboarding step labels/orientation are clear at 375px.

### AC-5: Test reinforcement
At least 2 new M-09-focused E2E tests are added and passing.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Before/after triad, closure reports, and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not alter backend dashboard/onboarding business logic in this mission.
2. Do not change shared shell architecture outside M-09 scope.
3. Keep changes focused on Dashboard and Onboarding readability/coherence.
4. Preserve M-03 contract-aligned behavior and stage/count source conventions.
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m09-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic E2E assertions; avoid sleep-only gates.
8. Do not proceed into M-10/M-11 implementation from this mission.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Full onboarding feature redesign is **not applicable** in M-09.
- Visual-regression framework expansion is **not applicable** in M-09 (belongs to Phase 3 integration).

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture triad baseline for Dashboard and Onboarding at 375/768/1280?
- [ ] Did I map all visible controls in interaction closure?
- [ ] Did I document count-semantics sources before edits?

### After each code change
- [ ] Did this change directly improve visibility/coherence/orientation?
- [ ] Did I preserve desktop/tablet usability while fixing mobile?
- [ ] Did I avoid backend/feature scope creep?

### Before marking COMPLETE
- [ ] Are Today & Next Up cards fully usable at 375px?
- [ ] Are dashboard count semantics coherent during loading and settled states?
- [ ] Is onboarding orientation clear at 375px with readable step context?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I add at least 2 M-09-focused E2E tests?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx` | Phase 1 | Count coherence and dashboard interaction behavior |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/TodayNextUpStrip.tsx` | Phase 1 | Mobile priority-card visibility and affordances |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/page.tsx` | Phase 2 | Onboarding page-level responsive framing |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx` | Phase 2 | Resume banner and stepper orientation improvements |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingBanner.tsx` | Phase 2 | Optional orientation consistency alignment |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m09-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m09-artifacts/before/` | Phase 0 | Before screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m09-artifacts/after/` | Phase 2 | After screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/m08-boundary-snapshot.md` | Phase 0 | Pre-M09 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/interaction-closure.md` | Phase 0-2 | Control closure matrix |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/dashboard-count-semantics.md` | Phase 0-1 | Count source and transition mapping |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/findings-closure.md` | Phase 3 | F-17/F-18/F-19/F-20 closure summary |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion summary |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/dashboard-mobile-priority-and-count-coherence.spec.ts` | Phase 3 | New E2E test |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/onboarding-mobile-orientation-and-resume.spec.ts` | Phase 3 | New E2E test |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-17/F-18/F-19/F-20 baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Control inventory baseline |
| `/home/zaks/bookkeeping/missions/m08-artifacts/reports/findings-closure.md` | Adjacent mission context |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md` | Contract baseline guardrail |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 2 requirements and mission map |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation passes, artifacts are complete, and bookkeeping is updated. Do not proceed into M-10/M-11 implementation from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M09*
