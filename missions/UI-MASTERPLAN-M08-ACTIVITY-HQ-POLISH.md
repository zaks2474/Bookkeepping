# MISSION: UI-MASTERPLAN-M08
## Agent Activity + Operator HQ Polish - Mobile Density, Stage Legibility, and Command Clarity
## Date: 2026-02-11
## Classification: Page-Level UX Hardening (Tier 2)
## Prerequisite: UI-MASTERPLAN-M07 complete
## Successor: UI-MASTERPLAN-M09, UI-MASTERPLAN-M10, and Phase 3 integration sweep (M-11)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m08-artifacts/`

---

## Mission Objective
Close Agent Activity + Operator HQ findings F-23 and F-14 by improving mobile information density and preserving stage/stat legibility at 375/768/1280.

This mission hardens command-center usability for `/agent/activity` and `/hq` without changing backend pipeline semantics.

Out of scope: new analytics features, pipeline business-rule changes, and full accessibility audit scope (handled in Phase 3 follow-up).

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

M-00 evidence driving this mission:
- F-23 (Sev-3): Agent Activity stat cards stack vertically at 375px, pushing core activity content below the fold.
- F-14 (Sev-2): Operator HQ stage labels/stats truncate at 375px, reducing readability and scan quality.

Current implementation center:
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/hq/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/OperatorHQ.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/QuickStats.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/PipelineOverview.tsx`

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
| Mobile density | Amount of actionable information visible above the fold at 375px |
| Stage legibility | Ability to read full pipeline stage/status labels without destructive truncation |
| Command clarity | Primary controls/tabs/stats are discoverable and understandable across breakpoints |
| Interaction closure | Every visible control classified as `real`, `degraded`, or `hidden` with explicit rationale |

---

## Architectural Constraints
- **Primary scope lock:** Keep changes focused to Agent Activity and Operator HQ pages/components.
- **No destructive truncation:** Stage/stat labels at 375px must remain interpretable.
- **Mobile-first density:** Agent Activity stat section should avoid one-card-per-row full-height stacking at 375px.
- **Workflow preservation:** HQ tabs (Pipeline/Approvals/Activity) and Agent Activity tabs/search/refresh must remain fully operable.
- **No backend semantics drift:** Preserve pipeline counts/status sources and M-03 contract alignment.
- **No shell regression:** Do not undo shared shell/header baselines from M-02.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Agent Activity stats consume full mobile vertical space
```text
At 375px, four stat cards stack 1x4 and push tabs + event list below the fold.
```

### RIGHT: Compact mobile stat layout
```text
At 375px, stats present in compact 2x2 (or equivalent) while preserving click targets.
```

### WRONG: Operator HQ pipeline/stats truncate labels to unreadable fragments
```text
Stage badges display cut labels (Int, Sc, Qu, Dil, Clo, Port) without explicit full context.
```

### RIGHT: Legible stage presentation
```text
Pipeline stages remain readable (full labels or explicit, intentional abbreviations with clear context).
```

### WRONG: Responsive fix hides essential controls
```text
Making cards smaller removes reachability of refresh, tabs, or detail interactions.
```

### RIGHT: Responsive fix preserves command center workflows
```text
Density improvements maintain full control reachability and interaction closure.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Mobile density improvements reduce tap targets below usable size | Medium | High | Verify minimum control hit areas during triad checks |
| 2 | HQ stage legibility fix regresses desktop visual hierarchy | Medium | High | Re-check 1280 layout at each phase gate |
| 3 | QuickStats/Pipeline layout changes break tab flow context | Medium | Medium | Run full HQ interaction closure replay per phase |
| 4 | Agent Activity compact grid introduces clipping in long labels | Medium | Medium | Validate text wrapping/truncation strategy with screenshot evidence |
| 5 | Test coverage misses actual readability regressions | Medium | Medium | Add viewport-specific assertions for label visibility and control reachability |

---

## Phase 0 - Baseline and Boundary Snapshot
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Freeze pre-M08 state and ensure rollback isolation.

### Blast Radius
- **Services affected:** Agent Activity + Operator HQ presentation layers
- **Pages affected:** `/agent/activity`, `/hq`
- **Downstream consumers:** M-09/M-10 sequencing and M-11 integration gate

### Tasks
- P0-00: Capture M-07 boundary snapshot before M-08 edits.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m08-artifacts/reports/m07-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-08 rollback remains independent.
- P0-01: Capture before screenshots + console logs at 375/768/1280 for `/agent/activity` and `/hq`.
  - Evidence: `/home/zaks/bookkeeping/missions/m08-artifacts/before/`
  - Checkpoint: captures include stat sections, tabs, and primary command controls.
- P0-02: Build baseline interaction closure matrix for both pages.
  - Evidence: `/home/zaks/bookkeeping/missions/m08-artifacts/reports/interaction-closure.md`
  - Checkpoint: all visible controls have baseline status.

### Decision Tree
- IF F-14/F-23 are partially improved by prior shell/page work -> keep baseline evidence and still execute explicit legibility/density closure tasks.
- ELSE -> implement targeted responsive and layout fixes as primary closure path.

### Rollback Plan
1. Preserve baseline artifacts as immutable references.
2. Re-capture baseline only if environment state materially changes.

### Gate P0
- M-07 boundary snapshot exists.
- Before-state triad + console baseline exists for both pages.
- Baseline interaction closure matrix is complete.

---

## Phase 1 - Agent Activity Density and Mobile Usability
**Complexity:** L
**Estimated touch points:** 3-9 files

**Purpose:** Close F-23 by improving above-the-fold density while preserving activity workflows.

### Blast Radius
- **Services affected:** Agent Activity header/stats/tabs/list layout
- **Pages affected:** `/agent/activity`
- **Downstream consumers:** command-center workflow speed and usability

### Tasks
- P1-01: Refactor stats section for compact, readable 375px behavior.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/page.tsx`
  - Checkpoint: stats no longer force a full vertical stack that hides primary content.
- P1-02: Validate search, tabs, status badge, and refresh controls remain reachable across breakpoints.
  - Checkpoint: no clipping or inaccessible controls at 375/768.
- P1-03: Verify selected run/event navigation and highlight flow remain stable.
  - Checkpoint: no regression in run selection, highlight, or scrolling behavior.

### Rollback Plan
1. Revert density/layout changes that reduce interaction quality.
2. Re-apply with smaller responsive adjustments and explicit viewport assertions.

### Gate P1
- F-23 resolved with evidence at 375px.
- Agent Activity control reachability verified at 375/768/1280.
- No new console regressions.

---

## Phase 2 - Operator HQ Legibility and Workflow Closure
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Close F-14 by making stage/stat labels readable and preserving HQ command clarity.

### Blast Radius
- **Services affected:** HQ header, quick-stats row, pipeline overview, tab surfaces
- **Pages affected:** `/hq`
- **Downstream consumers:** operations overview and stage triage workflows

### Tasks
- P2-01: Improve QuickStats responsive layout to avoid truncation/compression at 375px.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/QuickStats.tsx`
  - Checkpoint: labels/values remain readable and tap targets remain usable.
- P2-02: Refactor pipeline stage-card presentation for mobile legibility.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/PipelineOverview.tsx`
  - Checkpoint: stage labels are readable and not destructively clipped.
- P2-03: Validate header + tabs + approvals/activity sections preserve workflow clarity.
  - Primary paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/OperatorHQ.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/hq/page.tsx`
  - Checkpoint: pipeline/approvals/activity flows remain accessible at all target breakpoints.
- P2-04: Finalize interaction closure matrix for `/agent/activity` and `/hq`.
  - Evidence: `/home/zaks/bookkeeping/missions/m08-artifacts/reports/interaction-closure.md`
  - Checkpoint: 100% visible-control coverage with `real/degraded/hidden` status.

### Decision Tree
- IF full labels cannot fit without harming usability -> apply intentional, explicit abbreviation strategy with clear contextual cues.
- ELSE -> keep full stage labels visible across breakpoints.

### Rollback Plan
1. Revert HQ layout changes that regress desktop hierarchy or tab behavior.
2. Keep validated Agent Activity improvements while iterating HQ legibility.

### Gate P2
- F-14 resolved with 375px evidence.
- HQ command controls remain reachable and clear.
- Interaction closure matrix complete and accurate.

---

## Phase 3 - Test Reinforcement, Validation, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Stabilize M-08 changes with tests and final evidence pack.

### Blast Radius
- **Services affected:** Dashboard E2E and validation pipeline
- **Pages affected:** `/agent/activity`, `/hq`
- **Downstream consumers:** M-11 integration and long-term regression coverage

### Tasks
- P3-01: Add at least 2 mission-scoped E2E tests.
  - Candidate location: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/`
  - Suggested files:
    - `agent-activity-mobile-density.spec.ts`
    - `hq-pipeline-legibility-and-controls.spec.ts`
  - Checkpoint: tests verify density/legibility plus control reachability.
- P3-02: Run validation stack and archive transcript.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m08-artifacts/reports/validation.txt`
- P3-03: Publish closure and completion reports.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m08-artifacts/reports/findings-closure.md`
    - `/home/zaks/bookkeeping/missions/m08-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert flaky/new tests and stabilize selectors/assertions.
2. Revert only behavior causing regressions while keeping validated fixes.

### Gate P3
- 2+ new M-08 E2E tests exist and pass.
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: F-23 resolved
Agent Activity mobile stat section is compact/readable and no longer blocks core activity content at 375px.

### AC-2: F-14 resolved
Operator HQ stage/stat labels are readable at 375px without destructive truncation.

### AC-3: Interaction closure complete
All visible controls across `/agent/activity` and `/hq` are mapped to `real/degraded/hidden` with evidence.

### AC-4: Workflow replay stability
Tabs, search, refresh, and detail flows remain functional across 375/768/1280.

### AC-5: Test reinforcement
At least 2 new M-08-focused E2E tests are added and passing.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Before/after triad, closure reports, and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not alter backend pipeline/action semantics in this mission.
2. Do not redesign unrelated pages or shell structures outside M-08 scope.
3. Keep fixes focused on Agent Activity and HQ readability/usability.
4. Preserve M-03 contract conventions and server-source stage/count patterns.
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m08-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic E2E assertions; avoid sleep-only gates.
8. Do not proceed into M-09/M-10/M-11 implementation from this mission.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Full accessibility/WCAG audit is **not applicable** in M-08 (reserved for Phase 3 accessibility sweep).
- New analytics feature expansion is **not applicable** in M-08.

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture triad baseline screenshots for both pages at 375/768/1280?
- [ ] Did I inventory all visible controls in the interaction matrix?

### After each code change
- [ ] Did this change improve mobile density or stage legibility directly?
- [ ] Did I preserve desktop and tablet clarity while fixing mobile?
- [ ] Did I avoid backend/feature scope creep?

### Before marking COMPLETE
- [ ] Are Agent Activity stats compact and readable at 375px?
- [ ] Are HQ stage/stat labels readable at 375px?
- [ ] Do tabs/search/refresh/detail workflows still work at all breakpoints?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I add at least 2 M-08-focused E2E tests?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/page.tsx` | Phase 1 | Mobile density + control reachability improvements |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/hq/page.tsx` | Phase 2 | HQ data presentation flow adjustments if needed |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/QuickStats.tsx` | Phase 2 | Responsive stats readability and hit-target quality |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/PipelineOverview.tsx` | Phase 2 | Stage-card legibility at 375px |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/operator-hq/OperatorHQ.tsx` | Phase 2 | Header/tab/section layout integrity |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m08-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m08-artifacts/before/` | Phase 0 | Before screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m08-artifacts/after/` | Phase 2 | After screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m08-artifacts/reports/m07-boundary-snapshot.md` | Phase 0 | Pre-M08 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m08-artifacts/reports/interaction-closure.md` | Phase 0-2 | Control closure matrix |
| `/home/zaks/bookkeeping/missions/m08-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m08-artifacts/reports/findings-closure.md` | Phase 3 | F-14/F-23 closure summary |
| `/home/zaks/bookkeeping/missions/m08-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion summary |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/agent-activity-mobile-density.spec.ts` | Phase 3 | New E2E test |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/hq-pipeline-legibility-and-controls.spec.ts` | Phase 3 | New E2E test |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-14/F-23 baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Control inventory baseline |
| `/home/zaks/bookkeeping/missions/m07-artifacts/reports/findings-closure.md` | Adjacent Tier 2 mission context |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md` | Contract baseline guardrail |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 2 requirements and mission map |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation passes, artifacts are complete, and bookkeeping is updated. Do not proceed into M-09/M-10/M-11 implementation from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M08*
