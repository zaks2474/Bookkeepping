# MISSION: UI-MASTERPLAN-M02
## Layout/Shell Foundation and Mobile Responsive Stabilization
## Date: 2026-02-11
## Classification: Frontend Foundation Remediation
## Prerequisite: UI-MASTERPLAN-M00 (Recon complete)
## Successor: UI-MASTERPLAN-M03 (API Contract Alignment), then Phase 2 page missions (M-04..M-10)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify artifact completeness in `/home/zaks/bookkeeping/missions/m00-artifacts/` and `/home/zaks/bookkeeping/missions/m02-artifacts/`

---

## Mission Objective
Deliver the shared responsive shell fix that M-00 evidence shows is gating all downstream page polish work. This mission targets cross-cutting layout defects F-01 through F-07 first, with emphasis on 375px and 768px behavior.

This is a foundation mission, not a page-by-page redesign. Apply changes at shared shell/layout/header/navigation layers so Phase 2 missions inherit consistent behavior by default.

Out of scope: page-local content redesign that does not originate in shared shell primitives.

---

## Context
Source evidence:
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/capture-index.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

Evidence highlights driving this mission:
- F-01, F-02: content truncation and header/action collisions across multiple pages at 375px.
- F-03: mobile sidebar behavior is not usable/clear enough in current shell state.
- F-04: global search truncation at 768px.
- F-05/F-06/F-07: shell polish inconsistencies (tab title convention, disabled bell semantics, floating "N" overlay visibility).

Current code shape confirms high shared leverage:
- Route layout duplication exists across dashboard surfaces under `/home/zaks/zakops-agent-api/apps/dashboard/src/app/*/layout.tsx`.
- Shared top bar logic is centralized in `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/header.tsx`.
- Sidebar behavior is centralized in `/home/zaks/zakops-agent-api/apps/dashboard/src/components/ui/sidebar.tsx` and `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/app-sidebar.tsx`.

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Shell | Shared app chrome: sidebar, top header, global controls, content container behavior |
| Scroll containment | Preventing nested containers from clipping/locking content unexpectedly at smaller breakpoints |
| Responsive triad | 375px / 768px / 1280px breakpoint verification set |
| Foundation fix | A fix at shared component/layout level that impacts multiple pages uniformly |

---

## Architectural Constraints
- **Shared-first remediation:** Fix in shared layout/header/sidebar components before touching page-local markup.
- **Surface 9 breakpoint discipline:** Every shell change is verified at 375/768/1280.
- **No feature creep:** Do not add new business features, endpoints, or page-specific workflows.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Console hygiene:** No new `console.error` for expected degradation paths.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are mandatory final gates.

---

## Anti-Pattern Examples

### WRONG: Page-by-page patching identical responsive issues
```text
Fix /dashboard header locally, then patch /deals separately, then /actions separately.
Result: repeated drift and inconsistent behavior.
```

### RIGHT: Shared shell remediation
```text
Fix shared header/sidebar/container primitives first.
Then verify every affected route inherits the same behavior.
```

### WRONG: Treating dev-overlay artifact as a product feature defect without context
```text
Hardcode CSS hacks in page components to hide all fixed overlays.
```

### RIGHT: Classify and handle by environment intent
```text
If overlay is dev-only, ensure production behavior is clean and document the non-app condition.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Shared shell changes regress desktop while fixing mobile | Medium | High | Gate each phase with triad screenshot checks and no-regression comparison |
| 2 | Team patches page-level overflow instead of shell root cause | High | High | Guardrail: shared-first edits; page-local edits only with explicit evidence link |
| 3 | Sidebar mobile behavior remains ambiguous after refactor | Medium | High | Phase 2 requires explicit mobile navigation acceptance criteria |
| 4 | Tab-title/notification polish changes are inconsistent | Medium | Medium | Add deterministic checklist in Gate P2 and AC coverage |
| 5 | Mission drifts into API or data-contract work | Medium | Medium | Scope fence excludes API contract fixes (handled by M-03) |

---

## Phase 0 - Baseline and Scope Lock
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Confirm findings and freeze exact shared-shell scope before edits.

### Blast Radius
- **Services affected:** Dashboard frontend shell only
- **Pages affected:** Dashboard, Deals, Deal Workspace, Actions, Chat, Quarantine, Agent Activity, HQ, Onboarding
- **Downstream consumers:** M-04..M-10 inherit shell behavior

### Tasks
- P0-01: Validate target findings F-01..F-07 against M-00 artifacts and current UI.
  - Evidence: `/home/zaks/bookkeeping/missions/m02-artifacts/baseline-findings-check.md`
  - Checkpoint: Each finding mapped to shared component or explicit non-shared justification.
- P0-02: Create mission artifact workspace.
  - Evidence: `/home/zaks/bookkeeping/missions/m02-artifacts/`
  - Checkpoint: directories for `before/`, `after/`, and `reports/` exist.

### Decision Tree
- IF a finding is no longer reproducible -> document as resolved-by-drift with evidence, keep mission scope unchanged unless 3+ findings are invalid.
- ELSE -> proceed with shell-first implementation.

### Rollback Plan
1. Revert only shell/layout files touched in this phase.
2. Re-capture baseline artifacts and restart Phase 0.

### Gate P0
- Baseline map exists and covers F-01..F-07.
- Artifact workspace exists.

---

## Phase 1 - Shell Consolidation and Header Contract
**Complexity:** L
**Estimated touch points:** 8-14 files

**Purpose:** Remove duplicated shell layout behavior and establish one responsive header contract.

### Blast Radius
- **Services affected:** Dashboard app shell
- **Pages affected:** All sidebar-layout routes
- **Downstream consumers:** All page missions rely on this header/shell baseline

### Tasks
- P1-01: Consolidate duplicated route layout wrappers into a shared shell layout group.
  - Evidence paths include:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/layout.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/layout.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/layout.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/layout.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/layout.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/hq/layout.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/layout.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/layout.tsx`
  - Checkpoint: All shell routes use a unified layout contract with no duplicated wrapper drift.
- P1-02: Introduce/standardize a shared page-header primitive for title/description/action composition.
  - Evidence: shared component under `/home/zaks/zakops-agent-api/apps/dashboard/src/components/` and adoption across target pages.
  - Checkpoint: 375px header stack behavior avoids collisions for title, subtitle, and actions.
- P1-03: Lock tab-title naming convention (`{Page} | ZakOps`) for shell-routed pages.
  - Evidence: metadata declarations in relevant layout/page modules.
  - Checkpoint: no mixed title patterns among shell pages.

### Decision Tree
- IF settings intentionally uses alternate layout -> preserve it and record as explicit non-applicability under this mission.
- ELSE -> converge route layout onto shared shell.

### Rollback Plan
1. Revert shared shell/layout commits.
2. Restore per-route layout files.
3. Verify app renders and `npx tsc --noEmit` passes.

### Gate P1
- Shell layout duplication removed or justified with explicit exceptions.
- Header primitive applied to target pages.
- `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` passes.

---

## Phase 2 - Mobile Navigation and Responsive Behavior Hardening
**Complexity:** L
**Estimated touch points:** 6-12 files

**Purpose:** Resolve 375px/768px shell interaction issues and overflow/truncation defects.

### Blast Radius
- **Services affected:** Sidebar/header/global-search shell surfaces
- **Pages affected:** All shell-routed pages
- **Downstream consumers:** Phase 2 pages inherit mobile navigation behavior

### Tasks
- P2-01: Ensure mobile sidebar behavior is explicit and usable (drawer/hamburger strategy), not icon-strip ambiguity.
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/ui/sidebar.tsx` and `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/header.tsx`
  - Checkpoint: at 375px user can open labeled navigation without clipping content area.
- P2-02: Resolve header action collisions at 375px by stacking/reflow rules.
  - Evidence: shared header/page-header primitives and affected page header containers.
  - Checkpoint: no clipped primary action buttons in Dashboard, Actions, Chat, Quarantine, Agent Activity.
- P2-03: Resolve global-search truncation behavior at 768px.
  - Evidence: global-search trigger behavior in header.
  - Checkpoint: search control is either fully readable, iconized intentionally, or moved without truncation artifact.
- P2-04: Handle shell polish findings F-06/F-07.
  - Notification control must be actionable or intentionally explanatory (tooltip/degraded label).
  - Floating dev overlay behavior must be documented and non-disruptive for production snapshots.

### Decision Tree
- IF a control is intentionally unavailable -> show explicit degraded state text/tooltip.
- ELSE IF control is actionable -> keep enabled and responsive.
- ELSE -> hide until integration exists (no silent dead UI).

### Rollback Plan
1. Revert header/sidebar responsive changes.
2. Keep Phase 1 layout convergence intact.
3. Re-run triad verification before continuing.

### Gate P2
- Screenshot triad exists for key routes in `/home/zaks/bookkeeping/missions/m02-artifacts/after/`.
- No header action clipping at 375px in shell pages.
- Mobile navigation has clear interaction path.

---

## Phase 3 - Verification, Evidence, and Handoff
**Complexity:** M
**Estimated touch points:** 2-5 files

**Purpose:** Prove shell foundation is stable and unblock M-03 and Phase 2 missions.

### Blast Radius
- **Services affected:** Validation pipeline + artifact outputs
- **Pages affected:** Shared shell routes
- **Downstream consumers:** M-03 and M-04..M-10

### Tasks
- P3-01: Run validation stack and capture outputs.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m02-artifacts/reports/validation.txt`
- P3-02: Archive before/after screenshot index with findings closure mapping.
  - Evidence: `/home/zaks/bookkeeping/missions/m02-artifacts/reports/findings-closure.md`
  - Checkpoint: F-01..F-07 each marked `closed`, `partial`, or `deferred` with reason.
- P3-03: Record mission summary and bookkeeping update.
  - Evidence: `/home/zaks/bookkeeping/CHANGES.md` entry + `/home/zaks/bookkeeping/missions/m02-artifacts/reports/completion-summary.md`

### Rollback Plan
1. If validation fails, revert last responsive change set and re-run P2 gate.
2. If regression is detected, restore previous shell commit and re-scope with evidence.

### Gate P3
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence bundle includes triad screenshots and findings closure report.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: Cross-cutting shell findings addressed
F-01 through F-07 are resolved or explicitly dispositioned with evidence and rationale.

### AC-2: Responsive shell baseline achieved
Shared shell behavior is clean at 375/768/1280 for all shell-routed pages with no clipped primary actions.

### AC-3: Mobile navigation is unambiguous
At 375px, users can access labeled navigation via a clear interaction path.

### AC-4: Header and search behavior standardized
Header composition and global-search behavior no longer produce truncation/collision artifacts.

### AC-5: Validation and type safety pass
`make validate-local` and `npx tsc --noEmit` both pass after remediation.

### AC-6: Evidence and bookkeeping complete
Before/after artifacts, findings closure report, and `/home/zaks/bookkeeping/CHANGES.md` update are present.

---

## Guardrails
1. Do not introduce new page features or business logic in this mission.
2. Do not modify generated files under any codegen output paths.
3. Keep fixes at shared shell/layout level whenever possible.
4. Preserve Surface 9 conventions for responsive behavior and console classification.
5. Do not move API contract work into this mission; reserve for M-03.
6. Maintain absolute-path evidence outputs under `/home/zaks/bookkeeping/missions/m02-artifacts/`.
7. B7 anti-convergence does not apply to this mission — standardization is required.
8. If uncertain between local patch and shared fix, prefer shared fix and document exception if impossible.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: this mission has 4 phases and is intentionally scoped below the 500-line/5-phase threshold.
- IA-7 Multi-Session Continuity is **not applicable** unless execution expands to XL scope; current expected scope is L.
- Settings page layout parity is **partially non-applicable** in M-02 where divergence is intentional and handled in M-10.

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I map each F-01..F-07 finding to a shared component or explicit exception?
- [ ] Did I establish baseline artifacts before changing shell code?

### After each code change
- [ ] Is this fix shared-shell-first rather than page-local patching?
- [ ] Does the change improve 375px behavior without regressing 1280px?
- [ ] Did I avoid introducing API-contract scope creep?

### Before marking COMPLETE
- [ ] Do before/after artifacts prove closure for all seven findings?
- [ ] Does `make validate-local` pass now?
- [ ] Does `npx tsc --noEmit` pass now?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/header.tsx` | Phase 1-2 | Responsive header contract and control behavior |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/layout/app-sidebar.tsx` | Phase 1-2 | Sidebar rendering behavior adjustments |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/ui/sidebar.tsx` | Phase 2 | Mobile/drawer/collapse behavior hardening |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/actions/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/hq/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/onboarding/layout.tsx` | Phase 1 | Layout convergence |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m02-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m02-artifacts/before/` | Phase 0 | Pre-change screenshots and notes |
| `/home/zaks/bookkeeping/missions/m02-artifacts/after/` | Phase 2 | Post-change screenshots and notes |
| `/home/zaks/bookkeeping/missions/m02-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m02-artifacts/reports/findings-closure.md` | Phase 3 | F-01..F-07 closure matrix |
| `/home/zaks/bookkeeping/missions/m02-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion report |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md` | Priority and findings baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-01..F-07 details |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Original strategy and mission inventory |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Mission structure standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt skeleton/checklist |

---

## Stop Condition
Stop when AC-1 through AC-6 are all satisfied, `make validate-local` and `npx tsc --noEmit` pass, evidence artifacts are complete, and bookkeeping is updated. Do not proceed into API contract remediation or page-specific polish in this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M02*
