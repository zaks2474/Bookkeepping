# MISSION: UI-MASTERPLAN-M06
## Actions Command Center Polish - Mobile Access and Detail Workflow Clarity
## Date: 2026-02-11
## Classification: Page-Level UX Hardening (Tier 1)
## Prerequisite: UI-MASTERPLAN-M01, UI-MASTERPLAN-M02, UI-MASTERPLAN-M03, UI-MASTERPLAN-M04 complete
## Successor: UI-MASTERPLAN-M07 and UI-MASTERPLAN-M08 (Tier 2 mission wave)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m06-artifacts/`

---

## Mission Objective
Close Actions findings F-11 and F-12 by ensuring `/actions` preserves creation and review workflows across breakpoints, with clear detail-panel behavior and reachable primary actions on mobile.

This mission polishes the Actions Command Center interaction model. It is not a backend feature mission and should not change risk/approval semantics beyond UX clarity and accessibility.

Out of scope: broad action-orchestration redesign or capability model changes.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

M-00 evidence driving this mission:
- F-12 (Sev-2): "New Action" control inaccessible/cut off at 375px.
- F-11 (Sev-3): desktop empty detail panel wastes space when nothing selected.
- Cross-cutting shell issues from M-02 are already addressed; this mission handles page-specific Actions behavior.

Current page center:
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/page.tsx`

Phase 2 per-mission requirements (FINAL_MASTER) apply:
- Interaction closure checklist
- Before/after screenshot triad
- Console audit
- Contract compliance preservation
- At least 2 new E2E tests for actions scope

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Command center ergonomics | Whether primary operations (create, filter, inspect, approve/run) remain efficient across breakpoints |
| Detail workflow | Pattern for inspecting an action’s full details and taking next steps |
| Mobile action reachability | Ability to trigger key operations at 375px without clipped/hidden controls |
| Interaction closure | Per-control validation: real endpoint, explicit degradation, or intentional hide |

---

## Architectural Constraints
- **Primary scope lock:** `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/page.tsx` and directly related action UI components.
- **Primary action access:** "New Action" and key filters/tabs must be reachable at 375px.
- **Detail flow clarity:** Empty detail state should be informative without wasting core workspace on desktop.
- **Mobile detail handling:** Selected action detail behavior at small viewports must be explicit and non-obstructive.
- **No backend scope creep:** Do not modify risk-tier semantics or action engine behavior beyond UI polish.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Primary action hidden at mobile breakpoint
```text
New Action exists on desktop but clips/disappears at 375px with no alternate entry path.
```

### RIGHT: Guaranteed primary action reachability
```text
New Action remains visible or moves into explicit overflow action menu with identical behavior.
```

### WRONG: Large static empty detail pane on desktop
```text
Main workspace dedicates large panel to "Select an action" without adaptive layout response.
```

### RIGHT: Adaptive detail empty-state strategy
```text
Detail panel preserves context while minimizing wasted space and keeping list productivity high.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Mobile fixes break desktop list-detail workflow | Medium | High | Validate list/detail behavior at 1280 after each responsive change |
| 2 | New Action becomes reachable but hidden behind non-obvious interaction | Medium | High | Interaction closure matrix requires explicit discoverability proof |
| 3 | Detail panel adjustments regress selected-action editing actions | Medium | Medium | Replay approve/run/retry/update flows in each gate |
| 4 | Additional filters introduce layout clipping at 768 | Medium | Medium | Triad screenshots and viewport-specific checks |
| 5 | Tests pass superficially without validating real control availability | Medium | Medium | Use explicit selectors/visibility/assertions, not generic page-load checks |

---

## Phase 0 - Baseline and Boundary Snapshot
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Establish pre-M06 baseline and isolate rollback boundary.

### Blast Radius
- **Services affected:** Actions page only
- **Pages affected:** `/actions`
- **Downstream consumers:** M-11 integration and actions regression behavior

### Tasks
- P0-00: Capture M-04 boundary snapshot before actions edits.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m06-artifacts/reports/m04-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-06 rollback is independent.
- P0-01: Capture before triad screenshots and console logs at 375/768/1280.
  - Evidence: `/home/zaks/bookkeeping/missions/m06-artifacts/before/`
  - Checkpoint: baseline captures include toolbar, filters, tabs, detail panel state.
- P0-02: Build baseline interaction closure matrix for all visible actions controls.
  - Evidence: `/home/zaks/bookkeeping/missions/m06-artifacts/reports/interaction-closure.md`
  - Checkpoint: every control has baseline state classification.

### Decision Tree
- IF F-12 no longer reproduces due prior shell work -> still verify reachability and document closure-by-foundation with evidence.
- ELSE -> implement explicit mobile accessibility fix for primary action controls.

### Rollback Plan
1. Preserve baseline artifacts as immutable evidence.
2. Re-capture only if environment state changes materially.

### Gate P0
- M-04 boundary snapshot exists.
- Before-state triad + console baseline exists.
- Baseline interaction closure matrix is complete.

---

## Phase 1 - Primary Action Reachability and Toolbar Layout
**Complexity:** L
**Estimated touch points:** 3-10 files

**Purpose:** Close F-12 by making key toolbar and creation controls accessible at smaller breakpoints.

### Blast Radius
- **Services affected:** Actions header, toolbar, and filter section
- **Pages affected:** `/actions`
- **Downstream consumers:** mobile operational usability

### Tasks
- P1-01: Ensure "New Action" is reachable at 375px and 768px.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/page.tsx`
  - Checkpoint: no clipping; clear tap target and visible label.
- P1-02: Validate filter and tab controls remain usable without horizontal clipping.
  - Checkpoint: search, type filters, tabs, clear/refresh actions are reachable and readable.
- P1-03: Preserve desktop ergonomics while introducing responsive adaptations.
  - Checkpoint: 1280px layout remains clean and efficient.

### Rollback Plan
1. Revert toolbar/controls layout changes that regress desktop behavior.
2. Re-apply using smaller, test-backed responsive adjustments.

### Gate P1
- F-12 resolved with evidence at 375/768.
- No clipped primary controls in toolbar/filter strip.

---

## Phase 2 - Detail Panel Workflow and Interaction Closure
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Close F-11 and complete interaction closure for command-center list/detail workflows.

### Blast Radius
- **Services affected:** Detail panel, selected-action flow, mobile detail drawer behavior
- **Pages affected:** `/actions`
- **Downstream consumers:** action review/approval workflows

### Tasks
- P2-01: Refine empty detail-panel state so desktop workspace remains productive when no action is selected.
  - Checkpoint: empty state is informative with reduced wasted-space impact.
- P2-02: Verify selected-action detail workflows across desktop/mobile patterns (desktop panel + mobile bottom sheet).
  - Checkpoint: selecting, inspecting, closing, and executing action tasks works at all breakpoints.
- P2-03: Validate clear/refresh/bulk operations remain discoverable and intact after layout updates.
  - Checkpoint: no workflow regressions for command-center operations.
- P2-04: Finalize interaction closure matrix with `real/degraded/hidden` status and evidence.
  - Evidence: `/home/zaks/bookkeeping/missions/m06-artifacts/reports/interaction-closure.md`
  - Checkpoint: 100% visible control coverage.

### Decision Tree
- IF desktop empty-state optimization conflicts with detail readability -> prioritize selected-action detail clarity and add compact empty variant.
- ELSE -> keep simplified empty state for space efficiency.

### Rollback Plan
1. Revert detail-panel behavior changes that break selected-action flows.
2. Keep proven responsive toolbar fixes from Phase 1.

### Gate P2
- F-11 behavior resolved or explicitly dispositioned with evidence.
- Interaction closure matrix complete and accurate.
- Console logs show zero untriaged errors during interaction replay.

---

## Phase 3 - Test Reinforcement, Validation, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Make M-06 stable and enforceable with deterministic tests plus final verification evidence.

### Blast Radius
- **Services affected:** Dashboard E2E and validation pipeline
- **Pages affected:** `/actions`
- **Downstream consumers:** M-11 integration sweep

### Tasks
- P3-01: Add at least 2 actions-focused E2E tests.
  - Candidate location: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/`
  - Suggested files:
    - `actions-mobile-primary-controls.spec.ts`
    - `actions-detail-workflow.spec.ts`
  - Checkpoint: tests cover primary control reachability and detail workflow behavior.
- P3-02: Run validation stack and archive output.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m06-artifacts/reports/validation.txt`
- P3-03: Publish completion and findings closure summary.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m06-artifacts/reports/findings-closure.md`
    - `/home/zaks/bookkeeping/missions/m06-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert flaky/new tests and stabilize assertions.
2. Revert only behavioral changes causing regression while keeping validated fixes.

### Gate P3
- 2+ new actions-focused E2E tests exist and pass.
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: F-12 resolved
"New Action" and other primary actions are reachable and readable at 375px and 768px.

### AC-2: F-11 resolved or dispositioned
Empty detail-panel behavior is improved and does not degrade command-center productivity.

### AC-3: Interaction closure complete
All visible Actions controls are mapped to `real/degraded/hidden` with evidence.

### AC-4: Workflow replay stability
Key actions flows (select, inspect, run/approve/retry, clear/refresh) function across breakpoints.

### AC-5: Test reinforcement
At least 2 new Actions-focused E2E tests are added and passing.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Before/after triad, closure reports, and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not change backend action semantics in this mission.
2. Do not redesign unrelated pages or shared shell foundations.
3. Keep fixes focused on Actions usability and interaction closure.
4. Preserve contract-compliant response/error behavior.
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m06-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic E2E assertions; avoid sleep-only gates.
8. Do not regress selected-action detail workflows while optimizing empty states.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: 4-phase mission below expected 500-line threshold.
- IA-7 Multi-Session Continuity is **not applicable** unless mission scope expands to XL.
- Deep action capability/risk-model refactor is **not applicable** in M-06.
- nuqs migration is **not applicable** in M-06 (targeted to M-07 deals-list scope).

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture actions triad baseline with visible toolbar/filter/detail states?
- [ ] Is every visible control represented in the interaction matrix?

### After each code change
- [ ] Did this change improve primary control reachability or detail workflow clarity?
- [ ] Are mobile and desktop behaviors both still coherent?
- [ ] Did I avoid backend/semantics scope creep?

### Before marking COMPLETE
- [ ] Is New Action definitely reachable at 375px?
- [ ] Is empty detail state improved without harming selected-action flow?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I add at least 2 actions-focused E2E tests?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/page.tsx` | Phase 1-2 | Primary control accessibility + detail workflow polish |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/loading.tsx` | Phase 1 | Optional loading alignment for responsive consistency |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/quarantine-actions.spec.ts` | Phase 3 | Extend existing actions coverage if applicable |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m06-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m06-artifacts/before/` | Phase 0 | Before screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m06-artifacts/after/` | Phase 2 | After screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m06-artifacts/reports/m04-boundary-snapshot.md` | Phase 0 | Pre-M06 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m06-artifacts/reports/interaction-closure.md` | Phase 0-2 | Control closure matrix |
| `/home/zaks/bookkeeping/missions/m06-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m06-artifacts/reports/findings-closure.md` | Phase 3 | F-11/F-12 closure summary |
| `/home/zaks/bookkeeping/missions/m06-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion summary |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/actions-mobile-primary-controls.spec.ts` | Phase 3 | New E2E test |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/actions-detail-workflow.spec.ts` | Phase 3 | New E2E test |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-11/F-12 baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Actions control inventory baseline |
| `/home/zaks/bookkeeping/missions/m02-artifacts/reports/findings-closure.md` | Shared shell baseline already stabilized |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md` | Contract baseline status |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/findings-closure.md` | Adjacent Tier 1 chat mission context |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 2 requirements |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation passes, artifacts are complete, and bookkeeping is updated. Do not proceed into M-07/M-08 implementation from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M06*
