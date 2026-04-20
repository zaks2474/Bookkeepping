# MISSION: UI-MASTERPLAN-M07
## Quarantine + Deals List Polish - Mobile Decision Flow, Table Responsiveness, and URL-State Convergence
## Date: 2026-02-11
## Classification: Page-Level UX Hardening (Tier 2)
## Prerequisite: UI-MASTERPLAN-M04, UI-MASTERPLAN-M05, UI-MASTERPLAN-M06 complete
## Successor: UI-MASTERPLAN-M08 and Tier 3 missions (M-09, M-10)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m07-artifacts/`

---

## Mission Objective
Close Quarantine + Deals List findings F-13 and F-21 by making moderation and list-management workflows fully operable at 375/768/1280, while removing URL-state convention drift on Deals List.

This mission is page-level UX hardening for `/quarantine` and `/deals`. It is not a backend workflow redesign and not a full feature-expansion mission.

Out of scope: quarantine classifier logic changes, deal model/schema redesign, and cross-page architecture refactors unrelated to these two pages.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

M-00 evidence driving this mission:
- F-13 (Sev-2): Quarantine detail/review panel truncates at 768px and disappears at 375px; approve/reject workflow becomes inaccessible.
- F-21 (Sev-2): Deals table overflows horizontally at 375px with clipped columns and poor discoverability.

FINAL_MASTER convention drift to close in this mission:
- F-12 (FINAL_MASTER): deals URL state uses manual `URLSearchParams` despite global `nuqs` adapter availability; M-07 is the designated convergence point.

Current implementation center:
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/ui/table.tsx`

Phase 2 per-mission requirements (FINAL_MASTER) apply:
- Interaction closure checklist
- Before/after screenshot triad at 375/768/1280
- Console audit (no untriaged errors)
- Contract compliance preservation
- At least 2 new E2E tests in mission scope

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Decision workflow closure | Ability to select, preview, approve/reject, and clear quarantine items at every target breakpoint |
| Table responsiveness | Deals list remains readable and operable on small screens without hidden critical data |
| URL-state convergence | Filters/sort/pagination/view state managed with one consistent strategy (`nuqs`) |
| Interaction closure | Every visible control classified as `real`, `degraded`, or `hidden` with explicit rationale |

---

## Architectural Constraints
- **Primary scope lock:** Changes stay focused on `/quarantine`, `/deals`, and directly supporting components.
- **Decision controls must remain reachable:** Quarantine Approve/Reject/Operator/Reject reason cannot be clipped or hidden at 375px.
- **Deals list readability:** Key columns and row-level actions must be discoverable and usable on 375px.
- **URL-state convergence:** Replace manual `URLSearchParams` state manipulation in Deals List with `nuqs` hooks.
- **No backend scope creep:** Do not alter approval semantics, data contracts, or route business logic in this mission.
- **Contract preservation:** Do not reintroduce non-502 backend-unavailable patterns or client-count anti-patterns.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Quarantine detail actions inaccessible on mobile
```text
At 375px, queue is visible but Approve/Reject controls are not reachable from selected item context.
```

### RIGHT: Explicit responsive decision path
```text
At 375px and 768px, item selection always exposes operator + reject reason + Approve/Reject controls.
```

### WRONG: Manual URLSearchParams mutations for every state change
```text
Each filter/sort/page interaction builds URLSearchParams and router.push() manually.
```

### RIGHT: nuqs-driven URL state
```text
Deals filters/sort/view/page use nuqs hooks with typed serialization and predictable URL updates.
```

### WRONG: Deals columns clipped with no clear affordance
```text
Critical columns are partially hidden at 375px; users cannot reliably inspect stage/broker/priority/update.
```

### RIGHT: Responsive list strategy with clear affordances
```text
Small-screen behavior provides readable data density and clear row action reachability.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Quarantine controls become reachable but require non-obvious gestures | Medium | High | Interaction closure matrix must prove discoverability and action completion |
| 2 | Deals mobile fix sacrifices desktop scan efficiency | Medium | High | Re-verify 1280 layout at each phase gate |
| 3 | nuqs migration regresses back/forward behavior or query persistence | Medium | High | URL-state replay checks in Phase 2 plus targeted E2E assertions |
| 4 | View-mode/filter fixes work in table but regress board mode | Medium | Medium | Include board/table parity checks in Phase 2 and P3 tests |
| 5 | Tests pass only for happy path with seeded data shape | Medium | Medium | Use resilient selectors + deterministic preconditions in E2E cases |

---

## Phase 0 - Baseline and Boundary Snapshot
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Capture pre-M07 behavior and define rollback boundary.

### Blast Radius
- **Services affected:** Quarantine and Deals UI layers
- **Pages affected:** `/quarantine`, `/deals`
- **Downstream consumers:** M-11 integration sweep and regression bundle

### Tasks
- P0-00: Capture M-06 boundary snapshot before M-07 edits.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m07-artifacts/reports/m06-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-07 rollback can be performed independently.
- P0-01: Capture before screenshots + console logs at 375/768/1280 for `/quarantine` and `/deals` (table and board).
  - Evidence: `/home/zaks/bookkeeping/missions/m07-artifacts/before/`
  - Checkpoint: route + mode + viewport metadata recorded for every screenshot.
- P0-02: Build baseline interaction closure matrix for both pages.
  - Evidence: `/home/zaks/bookkeeping/missions/m07-artifacts/reports/interaction-closure.md`
  - Checkpoint: all visible controls mapped with baseline status.
- P0-03: Baseline URL-state inventory for Deals List manual param handling.
  - Evidence: `/home/zaks/bookkeeping/missions/m07-artifacts/reports/url-state-baseline.md`
  - Checkpoint: every manual `URLSearchParams` touchpoint is enumerated.

### Decision Tree
- IF F-13/F-21 no longer reproduce exactly -> capture closure-by-foundation evidence and still execute interaction-closure + URL-state convergence tasks.
- ELSE -> implement explicit responsive corrections and verify with new triad.

### Rollback Plan
1. Keep baseline artifacts immutable.
2. Re-capture baseline only if environment/data materially changes.

### Gate P0
- M-06 boundary snapshot exists.
- Before-state triad + console baseline exists for both pages.
- Baseline interaction closure + URL-state reports are complete.

---

## Phase 1 - Quarantine Decision Workflow Responsiveness
**Complexity:** L
**Estimated touch points:** 3-10 files

**Purpose:** Close F-13 by guaranteeing moderation workflow completion across mobile/tablet/desktop.

### Blast Radius
- **Services affected:** Quarantine queue/detail interaction layer
- **Pages affected:** `/quarantine`
- **Downstream consumers:** Approval/rejection operational reliability

### Tasks
- P1-01: Ensure selected-item review content and decision controls remain reachable at 375px and 768px.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
  - Checkpoint: Approve/Reject + operator + reject reason controls are visible and usable.
- P1-02: Fix panel layout so queue and detail behavior are explicit at small viewports.
  - Checkpoint: users can reliably select, inspect, clear, retry preview, and complete decisions.
- P1-03: Verify empty/loading/error states remain clear after responsive changes.
  - Checkpoint: no hidden moderation paths under degraded preview conditions.

### Rollback Plan
1. Revert responsive panel changes that reduce workflow clarity.
2. Reintroduce smaller scoped layout adjustments with breakpoint-specific assertions.

### Gate P1
- F-13 resolved with evidence at 375/768.
- Quarantine decision workflow closure validated end-to-end.
- No new console regressions for review actions.

---

## Phase 2 - Deals List Responsiveness and nuqs Convergence
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Close F-21 and FINAL_MASTER F-12 by improving mobile list behavior and standardizing URL state management.

### Blast Radius
- **Services affected:** Deals table/filters/view-mode state behavior
- **Pages affected:** `/deals`
- **Downstream consumers:** deep-linking, navigation predictability, M-11 regression suite

### Tasks
- P2-01: Fix 375px table/list readability and row action discoverability.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx`
  - Checkpoint: critical deal fields are readable with explicit mobile affordances.
- P2-02: Maintain board/table parity for filters/search/selection behavior after responsive updates.
  - Checkpoint: no regression in board mode or list navigation.
- P2-03: Replace manual `URLSearchParams` updates with `nuqs` hooks for filter/sort/view/page state.
  - Checkpoint: URL persistence works with back/forward navigation and reload.
- P2-04: Finalize interaction closure matrix for both pages.
  - Evidence: `/home/zaks/bookkeeping/missions/m07-artifacts/reports/interaction-closure.md`
  - Checkpoint: 100% visible-control coverage with `real/degraded/hidden` status.

### Decision Tree
- IF direct nuqs migration conflicts with existing state semantics -> use typed adapter wrappers and document exact mapping.
- ELSE -> use direct nuqs hooks for each URL-backed control.

### Rollback Plan
1. Revert nuqs migration if URL-state behavior regresses.
2. Keep validated responsive UI fixes while restoring state handling incrementally.

### Gate P2
- F-21 resolved at 375px with evidence.
- Deals URL-state convergence completed with nuqs (FINAL_MASTER F-12 closure).
- Interaction closure matrix updated and complete.

---

## Phase 3 - Test Reinforcement, Validation, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Lock M-07 changes with deterministic tests and complete artifact bundle.

### Blast Radius
- **Services affected:** Dashboard E2E and validation pipeline
- **Pages affected:** `/quarantine`, `/deals`
- **Downstream consumers:** M-11 integration and future regression checks

### Tasks
- P3-01: Add at least 2 mission-scoped E2E tests.
  - Candidate location: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/`
  - Suggested files:
    - `quarantine-mobile-decision-flow.spec.ts`
    - `deals-mobile-responsiveness-and-url-state.spec.ts`
  - Checkpoint: tests verify moderation closure + deals mobile + nuqs behavior.
- P3-02: Run validation stack and archive transcript.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m07-artifacts/reports/validation.txt`
- P3-03: Publish closure and completion reports.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m07-artifacts/reports/findings-closure.md`
    - `/home/zaks/bookkeeping/missions/m07-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert flaky test additions and stabilize selectors/assertions.
2. Revert only behavior causing regressions while retaining validated fixes.

### Gate P3
- 2+ new M-07 E2E tests exist and pass.
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: F-13 resolved
Quarantine review and decision controls are reachable and usable at 375px and 768px.

### AC-2: F-21 resolved
Deals list no longer clips critical data at 375px; row actions remain reachable.

### AC-3: URL-state convergence completed
Deals List URL state is nuqs-based and preserves filter/sort/view/page behavior.

### AC-4: Interaction closure complete
All visible controls across `/quarantine` and `/deals` are mapped to `real/degraded/hidden` with evidence.

### AC-5: Test reinforcement
At least 2 new M-07-focused E2E tests are added and passing.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Before/after triad, closure reports, and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not change quarantine backend workflow semantics in this mission.
2. Do not introduce unrelated global layout changes already stabilized by M-02.
3. Keep edits scoped to `/quarantine` and `/deals` UX and URL-state behavior.
4. Preserve M-03 contract conventions (no non-502 degradation regressions).
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m07-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic E2E assertions; avoid sleep-only pass conditions.
8. Do not proceed into M-08/M-09 implementation from this mission.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Full quarantine classifier/business-rule redesign is **not applicable** in M-07.
- New visual-regression framework work is **not applicable** in M-07 (belongs to Phase 3 integration missions).

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture triad baseline for both `/quarantine` and `/deals` modes?
- [ ] Did I inventory all visible controls in the interaction matrix?
- [ ] Did I record all manual `URLSearchParams` touchpoints?

### After each code change
- [ ] Did this change improve mobile workflow closure or list readability?
- [ ] Did I preserve desktop/tablet ergonomics?
- [ ] Did I avoid backend/contract scope creep?

### Before marking COMPLETE
- [ ] Are Quarantine Approve/Reject workflows definitely reachable at 375px?
- [ ] Is Deals List readable and actionable at 375px?
- [ ] Is Deals URL state now nuqs-based and replayable by navigation?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I add at least 2 M-07-focused E2E tests?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | Phase 1 | Mobile decision-flow and detail-panel responsiveness |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx` | Phase 2 | Mobile list/table behavior + nuqs URL-state convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx` | Phase 2 | Optional board-mode parity adjustments |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/ui/table.tsx` | Phase 2 | Optional table container behavior improvements |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m07-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m07-artifacts/before/` | Phase 0 | Before screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m07-artifacts/after/` | Phase 2 | After screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/m06-boundary-snapshot.md` | Phase 0 | Pre-M07 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/interaction-closure.md` | Phase 0-2 | Control closure matrix |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/url-state-baseline.md` | Phase 0 | Manual URL-state inventory |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/findings-closure.md` | Phase 3 | F-13/F-21/FINAL_MASTER F-12 closure summary |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion summary |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/quarantine-mobile-decision-flow.spec.ts` | Phase 3 | New E2E test |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/deals-mobile-responsiveness-and-url-state.spec.ts` | Phase 3 | New E2E test |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-13/F-21 baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Control inventory baseline |
| `/home/zaks/bookkeeping/missions/m06-artifacts/reports/findings-closure.md` | Adjacent Tier 1 completion context |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md` | Contract baseline guardrail |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 2 requirements + nuqs convention closure |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation passes, artifacts are complete, and bookkeeping is updated. Do not proceed into M-08/M-09 implementation from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M07*
