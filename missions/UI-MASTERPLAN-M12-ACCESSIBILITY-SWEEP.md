# MISSION: UI-MASTERPLAN-M12
## Accessibility Sweep - Keyboard Navigation, Focus Management, and Basic Screen-Reader/Contrast Coverage
## Date: 2026-02-12
## Classification: Phase 3 Accessibility QA (Deferrable)
## Prerequisite: UI-MASTERPLAN-M11 complete
## Successor: Post-Phase hardening backlog (if additional accessibility debt remains)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m12-artifacts/`

---

## Mission Objective
Execute the Phase 3 accessibility sweep for core dashboard routes: keyboard navigation, focus behavior, modal/drawer focus traps, and baseline contrast/screen-reader semantics checks. This mission provides accessible-usage confidence beyond visual polish.

This is a QA verification/remediation mission. It is not a full WCAG AA certification program.

Out of scope: comprehensive manual assistive-technology certification across all possible environments.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`
- `/home/zaks/bookkeeping/missions/m11-artifacts/reports/phase3-gate3-scorecard.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`

FINAL_MASTER guidance for M-12:
- M-12 is explicitly deferrable.
- Scope includes keyboard navigation sweep, focus traps, contrast checks, and basic screen-reader compatibility.
- If deferred, M-11 must contain basic accessibility checks and defer rationale.

Known priority surfaces for accessibility verification:
- Shell/navigation controls (sidebar, header, global controls)
- Major workflow pages (`/dashboard`, `/deals`, `/actions`, `/quarantine`, `/chat`)
- Complex forms and settings controls (`/settings`, `/deals/new`, `/onboarding`)
- Modal/drawer flows and dialog-like interactions

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Keyboard flow | Complete route interaction using Tab/Shift+Tab/Enter/Escape without mouse dependency |
| Focus trap | Modal/drawer behavior that keeps focus constrained until close |
| Contrast smoke check | Automated baseline check for obvious color-contrast violations |
| Deferral package | Evidence-backed record explaining why M-12 is deferred and what was still covered in M-11 |

---

## Architectural Constraints
- **Verification-first scope:** prioritize audits, checks, and targeted remediations over broad redesign.
- **Core-route coverage:** accessibility checks must include primary operational pages, not one-route samples.
- **No fake pass criteria:** accessibility pass/fail must rely on explicit evidence, not subjective claims.
- **Targeted remediation only:** fix accessibility blockers discovered during sweep without feature creep.
- **Deferral discipline:** if deferred, produce explicit deferral package and residual-risk list.
- **No regression of M-11 suites:** accessibility changes must preserve integration/regression outcomes.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Accessibility check limited to static page load
```text
Audit visits page but does not test keyboard path, focus order, or modal focus behavior.
```

### RIGHT: Interaction-driven accessibility audit
```text
Audit verifies tab order, keyboard activation, escape handling, and focus return behavior.
```

### WRONG: Contrast "pass" without evidence
```text
Report claims adequate contrast with no tool output or route-level references.
```

### RIGHT: Evidence-backed contrast smoke output
```text
Route-level findings include tool output, thresholds, and remediation/disposition notes.
```

### WRONG: Defer mission without risk statement
```text
M-12 marked deferred without explaining what was covered and what remains risky.
```

### RIGHT: Structured deferral package
```text
Deferral report includes coverage already done, remaining gaps, risk level, and next owner.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Keyboard checks pass on simple pages but fail on modal-heavy flows | Medium | High | Include explicit modal/drawer focus-trap test set |
| 2 | Contrast tool noise creates untriaged false positives | Medium | Medium | Classify findings by severity and actionable threshold |
| 3 | Accessibility remediations break established layout behavior | Medium | High | Re-run key M-11 integration suites after remediations |
| 4 | Mission deferred without concrete residual-risk record | Medium | Medium | Mandatory deferral package gate in Phase 3 decision path |
| 5 | Test suite becomes flaky due timing and focus races | Medium | Medium | Use deterministic focus assertions and avoid hard sleeps |

---

## Phase 0 - Baseline and Deferral Decision Setup
**Complexity:** S
**Estimated touch points:** 0-3 files

**Purpose:** Establish baseline accessibility posture and choose execute-now vs defer path with evidence.

### Blast Radius
- **Services affected:** Accessibility QA process and cross-route interaction checks
- **Pages affected:** Primary dashboard routes
- **Downstream consumers:** release quality posture and backlog prioritization

### Tasks
- P0-00: Capture M-11 boundary snapshot before M-12 work.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m12-artifacts/reports/m11-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-12 work can be isolated/reverted independently.
- P0-01: Build route accessibility coverage matrix (keyboard/focus/contrast semantics).
  - Evidence: `/home/zaks/bookkeeping/missions/m12-artifacts/reports/accessibility-coverage-matrix.md`
  - Checkpoint: routes and check types are explicit and complete.
- P0-02: Record execute-vs-defer decision rubric.
  - Evidence: `/home/zaks/bookkeeping/missions/m12-artifacts/reports/deferral-rubric.md`
  - Checkpoint: deferral criteria and risk thresholds are documented.

### Decision Tree
- IF time/risk budget supports full sweep -> execute Phases 1-3 fully.
- ELSE -> run minimum accessibility checks from M-11 coverage, publish deferral package, and stop at documented defer gate.

### Rollback Plan
1. Preserve baseline matrices and rubric regardless of decision.
2. Revisit decision only with updated capacity/risk inputs.

### Gate P0
- M-11 boundary snapshot exists.
- Coverage matrix and deferral rubric are complete.
- Execute/defer decision path is explicitly selected.

---

## Phase 1 - Keyboard and Focus Verification Sweep
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Validate keyboard operability and focus behavior across critical routes and interactions.

### Blast Radius
- **Services affected:** Cross-route keyboard/focus interaction quality
- **Pages affected:** `/dashboard`, `/deals`, `/deals/new`, `/actions`, `/quarantine`, `/chat`, `/settings`, `/onboarding`, `/hq`, `/agent/activity`
- **Downstream consumers:** usability for keyboard-only and assistive-tech users

### Tasks
- P1-01: Add keyboard navigation sweep suite.
  - Create: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/accessibility-keyboard-sweep.spec.ts`
  - Checkpoint: tab order and activation paths are validated on critical controls.
- P1-02: Add focus-trap and focus-return suite for modal/drawer/dialog flows.
  - Create: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/accessibility-focus-management.spec.ts`
  - Checkpoint: focus is trapped/released correctly for each target flow.
- P1-03: Log route-by-route pass/fail with remediation notes.
  - Evidence: `/home/zaks/bookkeeping/missions/m12-artifacts/reports/keyboard-focus-results.md`
  - Checkpoint: blockers are classified by severity.

### Rollback Plan
1. Revert flaky focus assertions and rework with deterministic focus checks.
2. Keep stable checks and isolate unstable interaction paths.

### Gate P1
- Keyboard and focus suites exist and run.
- Blockers are identified with severity and route references.
- No unclassified critical accessibility failures remain.

---

## Phase 2 - Contrast/Semantics Smoke Checks and Targeted Remediation
**Complexity:** M
**Estimated touch points:** 3-10 files

**Purpose:** Run baseline contrast and semantics checks and remediate high-impact accessibility blockers.

### Blast Radius
- **Services affected:** UI semantics and contrast-related readability
- **Pages affected:** Core operational routes and high-interaction components
- **Downstream consumers:** accessibility baseline confidence before long-term certification work

### Tasks
- P2-01: Add contrast/semantics smoke suite.
  - Create: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/accessibility-contrast-semantics-smoke.spec.ts`
  - Checkpoint: findings are captured with route and component context.
- P2-02: Apply targeted remediations for P0/P1-discovered high-severity blockers.
  - Checkpoint: remediations are limited to discovered blockers; no feature creep.
- P2-03: Re-run accessibility checks post-remediation.
  - Evidence: `/home/zaks/bookkeeping/missions/m12-artifacts/reports/accessibility-remediation-results.md`
  - Checkpoint: blockers are closed or explicitly deferred with rationale.

### Decision Tree
- IF blocker is high-severity and low-risk to fix -> remediate now.
- ELSE IF blocker requires architectural redesign -> defer with explicit risk + owner + follow-up ticket.

### Rollback Plan
1. Revert remediations that regress core flows.
2. Preserve non-regressing accessibility improvements while reworking problematic fixes.

### Gate P2
- Contrast/semantics smoke checks are completed and evidenced.
- High-severity accessibility blockers are remediated or formally deferred with rationale.
- M-11 regression suites still pass after remediations.

---

## Phase 3 - Validation, Deferral Package (if needed), and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Finalize accessibility sweep outcome (complete or deferred) with explicit evidence and risk statement.

### Blast Radius
- **Services affected:** Validation pipeline, accessibility QA posture, mission bookkeeping
- **Pages affected:** All audited routes
- **Downstream consumers:** release readiness and accessibility backlog planning

### Tasks
- P3-01: Run validation stack.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m12-artifacts/reports/validation.txt`
- P3-02: Publish accessibility scorecard.
  - Evidence: `/home/zaks/bookkeeping/missions/m12-artifacts/reports/accessibility-scorecard.md`
- P3-03: If deferred, publish deferral package with residual-risk statement.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m12-artifacts/reports/deferral-package.md`
    - `/home/zaks/bookkeeping/missions/m12-artifacts/reports/residual-risk-register.md`
- P3-04: Update bookkeeping.
  - `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert unstable accessibility test additions that break deterministic execution.
2. Keep stable improvements and document remaining work in deferral package if needed.

### Gate P3
- Validation and TypeScript checks pass.
- Accessibility scorecard is complete.
- If deferred: deferral package and residual-risk register are complete and explicit.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: Coverage matrix complete
Accessibility coverage matrix exists for all targeted routes and check categories.

### AC-2: Keyboard/focus verification complete
Keyboard and focus management checks execute with route-level evidence.

### AC-3: Contrast/semantics smoke complete
Baseline contrast and semantics checks are run and findings classified.

### AC-4: High-severity blocker disposition complete
High-severity accessibility blockers are fixed or explicitly deferred with rationale.

### AC-5: Accessibility suites reinforced
At least 2 new accessibility-focused E2E test files are added and runnable.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Accessibility scorecard, deferral package (if needed), and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not treat this mission as full WCAG certification.
2. Keep remediations targeted to discovered accessibility blockers.
3. Do not weaken existing M-11 integration regression coverage.
4. Avoid feature-scope creep while remediating accessibility issues.
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m12-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic accessibility assertions; avoid sleep-only gates.
8. If deferred, publish explicit residual risk and next-owner details.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Full assistive-technology matrix certification is **not applicable** in M-12 baseline sweep.
- If M-12 is formally deferred, only deferral-package completion remains applicable for this phase.

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I explicitly choose execute-now vs defer path with rubric evidence?
- [ ] Is route coverage complete for keyboard/focus/contrast checks?

### After each code/test change
- [ ] Did this change improve measurable accessibility behavior?
- [ ] Did I keep integration regressions from M-11 intact?
- [ ] Did I avoid feature-scope creep?

### Before marking COMPLETE
- [ ] Are keyboard and focus tests actually passing on target routes?
- [ ] Are contrast/semantics findings classified and dispositioned?
- [ ] If deferred, is the residual-risk package complete and actionable?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/graceful-degradation.spec.ts` | Phase 1-2 | Optional alignment with accessibility checks where applicable |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/responsive-regression.spec.ts` | Phase 2 | Optional a11y assertion hooks integration |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m12-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/m11-boundary-snapshot.md` | Phase 0 | Pre-M12 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/accessibility-coverage-matrix.md` | Phase 0 | Route/check coverage map |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/deferral-rubric.md` | Phase 0 | Execute/defer decision framework |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/keyboard-focus-results.md` | Phase 1 | Keyboard/focus outcomes |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/accessibility-remediation-results.md` | Phase 2 | Remediation and recheck outcomes |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/accessibility-scorecard.md` | Phase 3 | Final accessibility scorecard |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/deferral-package.md` | Phase 3 | Deferral package (if deferred) |
| `/home/zaks/bookkeeping/missions/m12-artifacts/reports/residual-risk-register.md` | Phase 3 | Residual risk statement (if deferred) |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/accessibility-keyboard-sweep.spec.ts` | Phase 1 | Keyboard navigation suite |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/accessibility-focus-management.spec.ts` | Phase 1 | Focus trap/return suite |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/accessibility-contrast-semantics-smoke.spec.ts` | Phase 2 | Contrast/semantics smoke suite |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | M-12 scope and deferrable policy |
| `/home/zaks/bookkeeping/missions/m11-artifacts/reports/phase3-gate3-scorecard.md` | Post-M11 baseline context |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | Global finding baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Control inventory baseline |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied for either (a) full sweep execution or (b) explicit deferral package completion with residual-risk documentation, and validation/bookkeeping are complete.

---
*End of Mission Prompt - UI-MASTERPLAN-M12*
