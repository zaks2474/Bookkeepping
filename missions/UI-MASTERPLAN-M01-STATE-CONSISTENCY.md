# MISSION: UI-MASTERPLAN-M01
## Loading/Empty/Error State Consistency (Slim, Low-Urgency Foundation)
## Date: 2026-02-11
## Classification: UI Consistency and Code-Quality Standardization
## Prerequisite: UI-MASTERPLAN-M03 (API contract alignment complete)
## Successor: Phase 2 page missions (M-04..M-10) and integration missions (M-11/M-12)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Re-run state-file inventory and compare with `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-inventory.md`

---

## Mission Objective
Standardize loading, empty, and error-state implementation patterns across dashboard routes with minimal behavioral risk. This mission is intentionally slimmed: M-00 produced no direct visual severity findings for state handling, so the work is consistency-focused rather than urgent defect remediation.

This mission is not a UX redesign. Preserve existing user-facing behavior while reducing duplication and making state handling easier to maintain.

Out of scope: page-specific visual polish and unrelated refactors.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`

Evidence context:
- M-00 reported **0 direct findings** requiring immediate loading/empty/error UX fixes.
- FINAL_MASTER still identifies consistency debt: repeated `error.tsx` patterns and missing `loading.tsx` coverage.
- Current inventory in `/home/zaks/zakops-agent-api/apps/dashboard/src/app/` includes many `error.tsx` files and limited route-level `loading.tsx` files.

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| State primitives | Shared UI components for loading, empty, and error render states |
| Thin error wrapper | Route `error.tsx` file that delegates rendering to shared primitive with route-specific copy |
| Coverage gap | Route lacking explicit `loading.tsx` where async page load behavior exists |

---

## Architectural Constraints
- **Behavior preservation:** Refactor toward shared primitives without changing intended UX flow.
- **Shared primitives first:** Create reusable state components before route rewiring.
- **Route-level wrappers allowed:** Keep route-local files as thin adapters where Next.js conventions require route files.
- **No feature scope creep:** Do not combine with page-level polish tasks.
- **Validation required:** `make validate-local` and `npx tsc --noEmit` must pass.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.

---

## Anti-Pattern Examples

### WRONG: Ad-hoc inline state markup in each page
```text
Each page defines custom spinner/error/empty markup independently.
```

### RIGHT: Shared primitives with thin route wrappers
```text
Create shared state components once, then keep route files minimal and explicit.
```

### WRONG: Skip loading coverage because route "usually loads fast"
```text
No loading.tsx added for async route; inconsistent transition behavior remains.
```

### RIGHT: Add deterministic route-level loading boundaries
```text
Provide explicit loading.tsx where route-level async behavior exists.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Refactor changes copy/visual behavior unexpectedly | Medium | Medium | Require thin wrapper pattern with preserved route-specific messaging |
| 2 | Missing loading coverage list is inaccurate | Medium | Medium | Phase 0 inventory gate must produce explicit route matrix |
| 3 | Mission over-expands into visual redesign | Medium | Medium | Guardrails enforce consistency-only scope |
| 4 | Shared primitives become too rigid for route nuances | Low | Medium | Allow controlled route-specific props/overrides in wrappers |

---

## Phase 0 - State Inventory and Scope Confirmation
**Complexity:** S
**Estimated touch points:** 1-2 files

**Purpose:** Build exact inventory of state files and lock slim mission scope.

### Blast Radius
- **Services affected:** Dashboard route-level state boundaries
- **Pages affected:** Routes with `error.tsx`/`loading.tsx`
- **Downstream consumers:** Phase 2 pages inherit normalized state primitives

### Tasks
- P0-01: Inventory all route `error.tsx` and `loading.tsx` files, including gaps.
  - Evidence: `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-inventory.md`
  - Checkpoint: explicit table of existing files and missing targets.
- P0-02: Confirm no critical user-facing state defects from M-00 require urgent redesign.
  - Evidence: `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-priority-rationale.md`
  - Checkpoint: slim-scope rationale recorded.

### Decision Tree
- IF new Sev-2/Sev-1 state defect appears during inventory -> stop and reclassify scope with user approval.
- ELSE -> proceed with slim standardization.

### Rollback Plan
1. Keep baseline inventories immutable.
2. Re-run inventory if route structure changes.

### Gate P0
- State inventory and slim-scope rationale exist.

---

## Phase 1 - Shared State Primitive Creation
**Complexity:** M
**Estimated touch points:** 3-6 files

**Purpose:** Establish shared components for loading, empty, and error states.

### Blast Radius
- **Services affected:** Shared UI component layer
- **Pages affected:** Any route using the new state primitives
- **Downstream consumers:** Future route implementations and page missions

### Tasks
- P1-01: Create shared state primitives under a dedicated components path.
  - Suggested target: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/states/`
  - Components: loading, empty, and error primitives.
  - Checkpoint: primitives support route-specific title/message/action overrides.
- P1-02: Add lightweight docs for state primitive usage.
  - Evidence: `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-primitives-usage.md`
  - Checkpoint: route wrapper usage pattern documented.

### Rollback Plan
1. Revert shared primitives if API/props are unstable.
2. Keep existing route files untouched until primitives are stable.

### Gate P1
- Shared state primitive components exist and compile.
- Usage guidance exists.

---

## Phase 2 - Route Coverage and Thin Wrapper Refactor
**Complexity:** L
**Estimated touch points:** 8-18 files

**Purpose:** Add missing loading boundaries and reduce duplicated error files to thin wrappers.

### Blast Radius
- **Services affected:** Route-level state rendering
- **Pages affected:** actions, chat, agent/activity, settings, onboarding, deals/new, deals/[id], plus existing state routes
- **Downstream consumers:** QA verification and future consistency checks

### Tasks
- P2-01: Add missing `loading.tsx` files for target async routes identified in Phase 0.
  - Checkpoint: coverage matrix shows required routes now have loading boundaries.
- P2-02: Refactor route `error.tsx` files into thin wrappers over shared primitive.
  - Checkpoint: route files remain explicit but no longer duplicate full UI markup.
- P2-03: Keep route-specific wording where necessary while preserving shared structure.
  - Checkpoint: no regression in route context messaging.

### Decision Tree
- IF a route needs materially distinct error behavior -> keep custom wrapper but document exception.
- ELSE -> use shared primitive pattern.

### Rollback Plan
1. Revert wrapper refactor for any route with behavior regression.
2. Retain shared primitives and continue route-by-route.

### Gate P2
- Missing loading coverage is closed for scoped routes.
- Target error files are thin wrappers or explicitly justified exceptions.

---

## Phase 3 - Verification and Bookkeeping
**Complexity:** M
**Estimated touch points:** 2-4 files

**Purpose:** Confirm no regressions and close mission evidence.

### Blast Radius
- **Services affected:** Validation pipeline
- **Pages affected:** Any route with updated state files
- **Downstream consumers:** Phase 2 mission execution confidence

### Tasks
- P3-01: Run validation stack and archive outputs.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m01-artifacts/reports/validation.txt`
- P3-02: Capture representative before/after state screenshots for sampled routes.
  - Evidence: `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-samples.md`
- P3-03: Write completion summary and update bookkeeping.
  - Evidence: `/home/zaks/bookkeeping/missions/m01-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert problematic route wrappers.
2. Re-run validation before re-attempting.

### Gate P3
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: State inventory and priority rationale documented
Phase 0 artifacts clearly show existing coverage and why this mission is slim/low urgency.

### AC-2: Shared state primitives implemented
Reusable loading/empty/error components are available for route wrappers.

### AC-3: Missing loading coverage addressed
Scoped routes identified in inventory now have explicit `loading.tsx` boundaries or documented exception.

### AC-4: Error duplication reduced
Target route `error.tsx` files are standardized as thin wrappers over shared primitive or explicitly justified exceptions.

### AC-5: Validation and type safety pass
`make validate-local` and `npx tsc --noEmit` pass.

### AC-6: Evidence and bookkeeping complete
M-01 artifacts and `/home/zaks/bookkeeping/CHANGES.md` entry are present.

---

## Guardrails
1. Do not expand this mission into page redesign work.
2. Preserve existing route behavior and context-specific messaging.
3. Keep route wrappers explicit for Next.js conventions.
4. Do not edit generated files.
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m01-artifacts/`.
6. Run validation before finalizing.
7. B7 anti-convergence does not apply to this mission — standardization is required.
8. If scope expands beyond slim baseline, stop and re-baseline before continuing.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: 4 phases, non-XL scope, expected document size below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** for current mission size.
- M-00 found no high-severity visual state defects; this mission is primarily consistency/code-quality, not urgent UX recovery.
- Schedule flexibility note: this mission may be deferred to the start of Phase 2 if critical-path execution needs to prioritize M-02 and M-03 outcomes first.

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I produce a concrete inventory rather than assuming missing files?
- [ ] Did I confirm this remains low-urgency consistency work?

### After each code change
- [ ] Is this a shared-state standardization change, not a redesign?
- [ ] Does route-specific context remain clear?

### Before marking COMPLETE
- [ ] Does `make validate-local` pass now?
- [ ] Does `npx tsc --noEmit` pass now?
- [ ] Did I capture representative state samples?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/hq/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/error.tsx` | Phase 2 | Thin wrapper over shared error primitive |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/error.tsx` | Phase 2 | Root-level alignment to shared primitive |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/states/` | Phase 1 | Shared state primitive directory |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/loading.tsx` | Phase 2 | Route loading boundary |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/loading.tsx` | Phase 2 | Route loading boundary |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/loading.tsx` | Phase 2 | Route loading boundary |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/loading.tsx` | Phase 2 | Route loading boundary |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/loading.tsx` | Phase 2 | Route loading boundary |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/loading.tsx` | Phase 2 | Route loading boundary |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/loading.tsx` | Phase 2 | Route loading boundary |
| `/home/zaks/bookkeeping/missions/m01-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-inventory.md` | Phase 0 | Current coverage matrix |
| `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-priority-rationale.md` | Phase 0 | Slim-scope justification |
| `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-primitives-usage.md` | Phase 1 | Usage guidance |
| `/home/zaks/bookkeeping/missions/m01-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m01-artifacts/reports/state-samples.md` | Phase 3 | Sample state screenshots/notes |
| `/home/zaks/bookkeeping/missions/m01-artifacts/reports/completion-summary.md` | Phase 3 | Completion summary |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md` | Confirms no urgent visual state defects |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Original M-01 consistency scope |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Structural checklist |

---

## Stop Condition
Stop when AC-1 through AC-6 are met, validation passes, and evidence/bookkeeping are complete. Do not continue into page-level visual polish from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M01*
