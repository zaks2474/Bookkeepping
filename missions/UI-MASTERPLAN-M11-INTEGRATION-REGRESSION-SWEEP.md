# MISSION: UI-MASTERPLAN-M11
## Cross-Page Integration Flows + Responsive/Visual Regression Suite
## Date: 2026-02-12
## Classification: Phase 3 Integration QA and Regression Hardening
## Prerequisite: UI-MASTERPLAN-M04 through UI-MASTERPLAN-M10 complete
## Successor: UI-MASTERPLAN-M12 (Accessibility Sweep, deferrable)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m11-artifacts/`

---

## Mission Objective
Execute the Phase 3 integration sweep by verifying cross-page user journeys and adding permanent regression coverage for responsive and visual behavior. This mission is the system-level proof that Phase 1 and Phase 2 closures hold together under realistic navigation and workflow sequences.

This is a QA/integration mission: verify, remediate, and enforce. It is not a feature-delivery mission.

Out of scope: new product features, broad visual redesign, and backend capability expansion.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m04-artifacts/reports/findings-closure.md`
- `/home/zaks/bookkeeping/missions/m05-artifacts/reports/findings-closure.md`
- `/home/zaks/bookkeeping/missions/m06-artifacts/reports/findings-closure.md`
- `/home/zaks/bookkeeping/missions/m07-artifacts/reports/findings-closure.md`
- `/home/zaks/bookkeeping/missions/m08-artifacts/reports/findings-closure.md`
- `/home/zaks/bookkeeping/missions/m09-artifacts/reports/findings-closure.md`
- `/home/zaks/bookkeeping/missions/m10-artifacts/reports/findings-closure.md`

FINAL_MASTER Phase 3 scope anchors:
- M-11 verifies cross-route flows after all page polish missions.
- Permanent `responsive-regression.spec.ts` and `visual-regression.spec.ts` are required outputs.
- Gate requires no open Sev-1/Sev-2 UI defects and stable validation checks.

Core integration journey expectations:
- Journey A: create deal -> navigate workspace -> add/inspect actions -> quarantine decision path -> verify state continuity.
- Journey B: chat proposal flow -> execute proposal -> verify reflected effects on page surfaces.
- Journey C: settings/onboarding/user preference changes persist and reflect coherently across route changes.

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Flow matrix | Enumerated cross-route journeys with explicit pass/fail criteria |
| Responsive regression suite | Breakpoint-specific assertions at 375/768/1280 for all key routes |
| Visual baseline | Screenshot evidence set used for future drift detection |
| Closure replay | Re-running previously fixed interaction paths to catch regressions |

---

## Architectural Constraints
- **Integration-first scope:** Prioritize cross-page behavior and regression enforcement over local polish tweaks.
- **No brittle gating:** Avoid sleep-only assertions; use stable selectors and deterministic checks.
- **Breakpoint discipline:** 375/768/1280 must be explicitly covered in responsive regression tests.
- **No hidden regressions:** Any Sev-1/Sev-2 reappearance is blocking and must be remediated.
- **Contract alignment preservation:** Keep M-03 conventions intact (status semantics, count semantics, stage taxonomy usage).
- **Evidence completeness:** Every journey and regression suite run must map to archived evidence.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Add a "regression" test that only checks page load
```text
Test visits route and checks body visible; no assertions for workflow integrity.
```

### RIGHT: Assert end-to-end state transitions
```text
Test verifies user action triggers expected route/state changes and preserves previous mission guarantees.
```

### WRONG: Responsive test without viewport changes
```text
Single desktop viewport run labeled as responsive coverage.
```

### RIGHT: Explicit viewport triad coverage
```text
Regression suite sets viewport to 375/768/1280 and validates key controls/content each time.
```

### WRONG: Visual evidence not archived with route/viewport metadata
```text
Screenshots exist but cannot be traced to journey step, route, and breakpoint.
```

### RIGHT: Traceable visual baseline bundle
```text
Each screenshot path includes journey, route, viewport, and before/after context.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Flow tests pass in isolation but fail in sequence due state coupling | Medium | High | Add sequential flow matrix run and reset strategy per journey |
| 2 | Visual baseline is captured but unusable for future diffing | Medium | Medium | Standardize naming and route/viewport metadata in evidence manifest |
| 3 | Responsive suite misses pages with prior Sev-2 history | Medium | High | Require coverage map tied to M-00 findings and M-04..M-10 closures |
| 4 | False confidence from flaky assertions | Medium | High | Enforce deterministic selectors and explicit retry strategy |
| 5 | Integration mission introduces feature-scope creep | Low | Medium | Guardrails prohibit new features and keep changes regression-focused |

---

## Phase 0 - Baseline and Scope Lock
**Complexity:** S
**Estimated touch points:** 0-3 files

**Purpose:** Capture post-Phase-2 baseline and lock integration verification scope.

### Blast Radius
- **Services affected:** Dashboard-wide UI flows and E2E infrastructure
- **Pages affected:** All Phase 2 routes
- **Downstream consumers:** M-12 accessibility sweep and CI regression gates

### Tasks
- P0-00: Capture M-10 boundary snapshot before Phase 3 edits.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m11-artifacts/reports/m10-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-11 rollback remains isolated.
- P0-01: Build cross-page flow matrix with explicit pass/fail criteria.
  - Evidence: `/home/zaks/bookkeeping/missions/m11-artifacts/reports/flow-matrix.md`
  - Checkpoint: all high-value journeys are enumerated and mapped to routes.
- P0-02: Capture baseline regression index (existing tests + current gaps).
  - Evidence: `/home/zaks/bookkeeping/missions/m11-artifacts/reports/regression-gap-index.md`
  - Checkpoint: required permanent suites are explicitly scoped.

### Decision Tree
- IF any Phase 2 closure artifact is missing -> block Phase 3 execution and restore required evidence before proceeding.
- ELSE -> continue with integration replay and suite hardening.

### Rollback Plan
1. Preserve baseline reports and manifests as immutable references.
2. Rebuild flow matrix if route contracts changed materially since baseline.

### Gate P0
- M-10 boundary snapshot exists.
- Flow matrix and regression-gap index are complete.
- Phase 2 closure artifacts are present and accessible.

---

## Phase 1 - Cross-Page Journey Replay and Remediation
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Replay full integration journeys and remediate regressions discovered under cross-route sequencing.

### Blast Radius
- **Services affected:** Workflow integration across dashboard pages and route transitions
- **Pages affected:** `/dashboard`, `/deals`, `/deals/[id]`, `/actions`, `/quarantine`, `/chat`, `/settings`, `/onboarding`, `/hq`, `/agent/activity`, `/deals/new`
- **Downstream consumers:** regression suite correctness and release confidence

### Tasks
- P1-01: Replay Journey A/B/C from flow matrix and log outcomes.
  - Evidence: `/home/zaks/bookkeeping/missions/m11-artifacts/reports/flow-replay-results.md`
  - Checkpoint: each step marked pass/fail with route-level evidence.
- P1-02: Remediate blocking regressions discovered during replay (Sev-1/Sev-2 blockers first).
  - Checkpoint: blocking regressions are fixed or explicitly dispositioned with rationale.
- P1-03: Re-run replay after fixes to confirm closure.
  - Checkpoint: no open Sev-1/Sev-2 UI regressions remain.

### Rollback Plan
1. Revert any fix that introduces broader instability.
2. Keep non-regressing remediations and isolate failing deltas for targeted retry.

### Gate P1
- Cross-page journey replay is complete and evidenced.
- No open Sev-1/Sev-2 UI regressions remain.
- Console audits for replay runs have no untriaged critical errors.

---

## Phase 2 - Permanent Responsive and Visual Regression Suites
**Complexity:** L
**Estimated touch points:** 4-10 files

**Purpose:** Add durable, CI-friendly regression suites to prevent recurrence of Phase 0/2 issues.

### Blast Radius
- **Services affected:** E2E suite, snapshot artifacts, CI quality gates
- **Pages affected:** All primary dashboard routes
- **Downstream consumers:** M-12 accessibility sweep and future release pipelines

### Tasks
- P2-01: Add permanent responsive regression suite.
  - Create: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/responsive-regression.spec.ts`
  - Checkpoint: suite covers 375/768/1280 across key routes and critical controls.
- P2-02: Add permanent visual regression suite.
  - Create: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/visual-regression.spec.ts`
  - Checkpoint: deterministic snapshot naming and stable capture strategy.
- P2-03: Add cross-page integration flow suite.
  - Create: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/cross-page-integration-flows.spec.ts`
  - Checkpoint: covers Journey A/B/C with deterministic assertions.
- P2-04: Archive screenshot baseline bundle and manifest.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m11-artifacts/after/`
    - `/home/zaks/bookkeeping/missions/m11-artifacts/reports/visual-baseline-manifest.md`
  - Checkpoint: baseline is route/viewport/journey traceable.

### Decision Tree
- IF snapshot flakiness exceeds threshold -> tighten selectors/wait strategy and reduce nondeterministic regions before locking baseline.
- ELSE -> lock baseline and proceed to validation.

### Rollback Plan
1. Revert flaky suite additions that do not meet deterministic criteria.
2. Restore prior stable tests and reintroduce hardened versions incrementally.

### Gate P2
- `responsive-regression.spec.ts` exists and passes.
- `visual-regression.spec.ts` exists and passes.
- `cross-page-integration-flows.spec.ts` exists and passes.
- Visual baseline manifest is complete.

---

## Phase 3 - Validation, CI Alignment, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Finalize Phase 3 Gate 3 readiness and publish integration completion evidence.

### Blast Radius
- **Services affected:** Validation pipeline, E2E execution discipline, mission bookkeeping
- **Pages affected:** All validated surfaces
- **Downstream consumers:** M-12 and ongoing CI regression enforcement

### Tasks
- P3-01: Run full validation stack and regression suite subset.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test tests/e2e/responsive-regression.spec.ts tests/e2e/visual-regression.spec.ts tests/e2e/cross-page-integration-flows.spec.ts`
  - Evidence: `/home/zaks/bookkeeping/missions/m11-artifacts/reports/validation.txt`
- P3-02: Publish integration closure report and scorecard.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m11-artifacts/reports/integration-closure.md`
    - `/home/zaks/bookkeeping/missions/m11-artifacts/reports/phase3-gate3-scorecard.md`
- P3-03: Update bookkeeping.
  - `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert failing regression-suite deltas if they destabilize validation.
2. Keep replay-proven fixes and isolate test-only instability for follow-up.

### Gate P3
- Validation and TypeScript checks pass.
- New permanent suites execute successfully.
- Phase 3 Gate 3 scorecard is complete and evidence-backed.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: Cross-page flow matrix complete
High-value integration journeys are documented and replayed with pass/fail evidence.

### AC-2: Blocking regressions closed
No open Sev-1/Sev-2 UI regressions remain after replay/remediation.

### AC-3: Permanent responsive suite added
`responsive-regression.spec.ts` exists, runs, and covers 375/768/1280 behavior.

### AC-4: Permanent visual suite added
`visual-regression.spec.ts` exists, runs, and archives traceable baseline evidence.

### AC-5: Integration flow suite added
`cross-page-integration-flows.spec.ts` exists and validates Journey A/B/C.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Phase 3 scorecard, closure reports, and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not implement new product features in this mission.
2. Keep changes integration/regression-focused; avoid local visual redesigns unless fixing discovered regressions.
3. Do not weaken assertions to make flaky tests "pass".
4. Preserve M-03 contract conventions and Phase 2 closures.
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m11-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic selectors and reproducible snapshot conventions.
8. Do not proceed into unrelated refactors from this mission.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Full WCAG AA certification audit is **not applicable** in M-11 (reserved for M-12/deferred workstream).
- Backend feature hardening is **not applicable** in M-11 except regression fixes required by replay failures.

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I verify all Phase 2 closure artifacts exist before replay?
- [ ] Is the flow matrix specific enough to be testable end-to-end?

### After each code/test change
- [ ] Did this change improve integration confidence instead of masking failures?
- [ ] Are assertions deterministic and breakpoint-aware?
- [ ] Did I avoid feature-scope creep?

### Before marking COMPLETE
- [ ] Are all high-value journeys replayed and evidenced?
- [ ] Do responsive/visual/integration suites exist and run?
- [ ] Are there zero open Sev-1/Sev-2 UI regressions?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/phase-coverage.spec.ts` | Phase 2 | Optional consolidation alignment with permanent suites |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/no-dead-ui.spec.ts` | Phase 2 | Optional stabilization for integration coverage |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/graceful-degradation.spec.ts` | Phase 2-3 | Optional alignment with Phase 3 coverage contracts |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m11-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m11-artifacts/before/` | Phase 0 | Baseline snapshots and logs |
| `/home/zaks/bookkeeping/missions/m11-artifacts/after/` | Phase 2 | Final visual baseline bundle |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/m10-boundary-snapshot.md` | Phase 0 | Pre-M11 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/flow-matrix.md` | Phase 0 | Cross-page journey definitions |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/regression-gap-index.md` | Phase 0 | Baseline suite coverage map |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/flow-replay-results.md` | Phase 1 | Replay outcomes + regressions |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/visual-baseline-manifest.md` | Phase 2 | Snapshot traceability manifest |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/integration-closure.md` | Phase 3 | Final closure report |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/phase3-gate3-scorecard.md` | Phase 3 | Gate 3 scorecard |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/responsive-regression.spec.ts` | Phase 2 | Permanent responsive suite |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/visual-regression.spec.ts` | Phase 2 | Permanent visual suite |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/cross-page-integration-flows.spec.ts` | Phase 2 | Journey integration suite |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 3 contract and mission scope |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | Original finding baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Control inventory baseline |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/findings-closure.md` | Chat mission closure reference |
| `/home/zaks/bookkeeping/missions/m05-artifacts/reports/findings-closure.md` | Deal workspace closure reference |
| `/home/zaks/bookkeeping/missions/m06-artifacts/reports/findings-closure.md` | Actions closure reference |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/findings-closure.md` | Quarantine/deals closure reference |
| `/home/zaks/bookkeeping/missions/m08-artifacts/reports/findings-closure.md` | Activity/HQ closure reference |
| `/home/zaks/bookkeeping/missions/m09-artifacts/reports/findings-closure.md` | Dashboard/onboarding closure reference |
| `/home/zaks/bookkeeping/missions/m10-artifacts/reports/findings-closure.md` | Settings/new-deal closure reference |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation passes, regression suites are stable, and bookkeeping is updated. Do not proceed into M-12 execution from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M11*
