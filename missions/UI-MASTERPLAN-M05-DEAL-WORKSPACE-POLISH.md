# MISSION: UI-MASTERPLAN-M05
## Deal Workspace Polish - Mobile Readability, Tab Truthfulness, and Workflow Clarity
## Date: 2026-02-11
## Classification: Page-Level UX Hardening (Tier 1)
## Prerequisite: UI-MASTERPLAN-M01, UI-MASTERPLAN-M02, UI-MASTERPLAN-M03, UI-MASTERPLAN-M04 complete
## Successor: UI-MASTERPLAN-M06 and Tier 2 missions (M-07, M-08)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Verify evidence continuity in `/home/zaks/bookkeeping/missions/m05-artifacts/`

---

## Mission Objective
Close Deal Workspace findings F-08, F-09, and F-10 by making `/deals/[id]` readable and actionable across breakpoints, while preserving truthful degraded semantics for unavailable materials/case-file data.

This mission focuses on the Deal Workspace experience, not a full domain-model rewrite. Fixes should improve mobile readability, reduce redundant UI signals, and ensure tabs/actions accurately reflect backend availability.

Out of scope: broad refactoring unrelated to workspace usability and interaction closure.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/RECON-REPORT.md`
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`

M-00 evidence driving this mission:
- F-08 (Sev-2): Deal Information/Broker/Financials values overflow or disappear at 375px.
- F-09 (Sev-2): Deal Workspace materials/case-file/enrichment dependencies reported as unavailable in recon environment; UX needs explicit degraded behavior.
- F-10 (Sev-3): Redundant archived signaling in workspace header.

Current workspace implementation center:
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx`
- Supporting shared components under `/home/zaks/zakops-agent-api/apps/dashboard/src/components/`

Phase 2 per-mission requirements (FINAL_MASTER) apply:
- Interaction closure checklist
- Before/after screenshot triad
- Console error audit
- Contract compliance preservation
- At least 2 new E2E tests for page scope

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Workspace readability | Ability to read labels and values without clipping/overflow at 375/768/1280 |
| Tab truthfulness | Tab states and counts reflect actual data availability, including degraded cases |
| Degraded disclosure | Explicit messaging when endpoint/data is unavailable, instead of silent empty or misleading success |
| Interaction closure | Every visible control has validated behavior: real, degraded, or intentionally hidden |

---

## Architectural Constraints
- **Primary scope lock:** Main edits focus on `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` and directly supporting components.
- **Mobile-first readability:** 375px rendering must preserve label/value visibility and action affordances.
- **No silent degradation:** Materials/Case File/Enrichment unavailable states must be explicit and non-deceptive.
- **No dead controls:** Any visible action/tab must either work, degrade clearly, or be hidden with rationale.
- **Contract preservation:** Do not reintroduce status 500 degradation paths or client-count anti-patterns.
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation discipline:** `make validate-local` and `npx tsc --noEmit` are required final gates.

---

## Anti-Pattern Examples

### WRONG: Keep data labels visible while values clip off-screen on mobile
```text
User sees "Stage / Status / Created" labels but value column is off-canvas at 375px.
```

### RIGHT: Responsive value layout with preserved readability
```text
At 375px, values remain visible via stack/reflow/overflow-safe layout.
```

### WRONG: Show tabs as fully functional when dependent data endpoints are unavailable
```text
Materials/Case File tabs appear normal but display confusing empty content with no explanation.
```

### RIGHT: Explicit degraded tab states
```text
Tabs and panels show clear unavailable/degraded messaging with actionable next step.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Mobile readability fixes regress desktop workspace density | Medium | High | Before/after triad plus desktop checks at every gate |
| 2 | Degraded tabs are cosmetically changed but still misleading | Medium | High | Interaction closure matrix includes degraded-truth criteria per tab |
| 3 | Badge cleanup removes needed state information | Medium | Medium | Keep one authoritative archived indicator and verify state clarity |
| 4 | Workspace-specific fixes leak into unrelated pages | Low | Medium | Scope guardrails limit changes to workspace-specific paths |
| 5 | E2E tests are flaky due to environment-dependent deal IDs | Medium | Medium | Use robust selectors and seed-or-discover strategy for test deal |

---

## Phase 0 - Baseline and Boundary Snapshot
**Complexity:** S
**Estimated touch points:** 0-2 files

**Purpose:** Freeze pre-M05 state and capture baseline evidence for workspace findings.

### Blast Radius
- **Services affected:** Deal Workspace only
- **Pages affected:** `/deals/[id]`
- **Downstream consumers:** M-11 integration/regression

### Tasks
- P0-00: Capture M-04 boundary snapshot before workspace edits.
  - Preferred: commit/tag boundary.
  - Fallback: `/home/zaks/bookkeeping/missions/m05-artifacts/reports/m04-boundary-snapshot.md` with changed-file manifest and `git diff --stat`.
  - Checkpoint: M-05 can roll back independently.
- P0-01: Capture before screenshots and console output at 375/768/1280 using a real deal ID.
  - Evidence: `/home/zaks/bookkeeping/missions/m05-artifacts/before/`
  - Checkpoint: triad complete with route/deal ID recorded.
- P0-02: Build baseline interaction closure matrix for workspace controls and tabs.
  - Evidence: `/home/zaks/bookkeeping/missions/m05-artifacts/reports/interaction-closure.md`
  - Checkpoint: all visible controls and tabs have baseline status.

### Decision Tree
- IF recon-specific 404s no longer reproduce -> still verify degraded semantics with simulated unavailable responses or documented non-app condition.
- ELSE -> implement explicit degraded tab/panel behavior.

### Rollback Plan
1. Preserve baseline artifacts as read-only.
2. Re-capture only if test deal or environment materially changes.

### Gate P0
- M-04 boundary snapshot exists.
- Before-state triad + console capture exists.
- Baseline interaction closure matrix is complete.

---

## Phase 1 - Mobile Readability and Header Signal Cleanup
**Complexity:** L
**Estimated touch points:** 3-9 files

**Purpose:** Fix F-08 and F-10 by making information panels readable on mobile and removing redundant archived cues.

### Blast Radius
- **Services affected:** Deal Workspace presentation layer
- **Pages affected:** `/deals/[id]`
- **Downstream consumers:** none beyond workspace UX

### Tasks
- P1-01: Fix 375px value visibility in Deal Information/Broker/Financials cards.
  - Primary path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx`
  - Checkpoint: label/value pairs are fully visible at 375px.
- P1-02: Normalize archived state signaling to one clear indicator.
  - Checkpoint: no redundant archived badges with duplicated meaning.
- P1-03: Verify card/grid behavior at 768px and 1280px remains stable.
  - Checkpoint: no new clipping, overflow, or misalignment introduced.

### Rollback Plan
1. Revert panel layout changes if readability improves mobile but breaks desktop.
2. Re-run triad capture and adjust with smaller scoped CSS/layout changes.

### Gate P1
- F-08 resolved at 375px for key information cards.
- F-10 redundant status signaling removed.
- Desktop/tablet layout remains stable.

---

## Phase 2 - Tab/Workflow Truthfulness and Degraded UX
**Complexity:** L
**Estimated touch points:** 4-12 files

**Purpose:** Close F-09 by making Materials/Case File/related flows explicit, truthful, and actionable under unavailable data conditions.

### Blast Radius
- **Services affected:** Workspace tabs and related data-display logic
- **Pages affected:** `/deals/[id]`
- **Downstream consumers:** no-dead-ui and graceful degradation quality gates

### Tasks
- P2-01: Enforce explicit degraded messaging for unavailable tab data (Materials/Case File/Enrichment-related surfaces).
  - Checkpoint: users see clear status and next-step messaging, not ambiguous empty states.
- P2-02: Ensure tab badges/counts reflect actual available data and do not imply successful retrieval when unavailable.
  - Checkpoint: tab labels and counts are truthful.
- P2-03: Validate View All Actions and related workspace links remain usable at all breakpoints.
  - Checkpoint: workflow controls remain reachable and functional.
- P2-04: Update interaction closure matrix with final control dispositions.
  - Evidence: `/home/zaks/bookkeeping/missions/m05-artifacts/reports/interaction-closure.md`
  - Checkpoint: 100% control coverage with `real/degraded/hidden` status.

### Decision Tree
- IF dependent endpoint is unavailable -> render explicit degraded UI with consistent severity messaging.
- ELSE -> render full data flow with no fallback banner.

### Rollback Plan
1. Revert tab-state logic changes if truthfulness regresses.
2. Keep readability fixes from Phase 1 intact while iterating tab behavior.

### Gate P2
- F-09 behavior is explicitly handled and user-understandable.
- Final interaction closure matrix complete.
- Console error audit contains no untriaged errors for workspace interactions.

---

## Phase 3 - Test Reinforcement, Validation, and Handoff
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Lock M-05 fixes with deterministic tests and complete evidence package.

### Blast Radius
- **Services affected:** Dashboard E2E + validation pipeline
- **Pages affected:** `/deals/[id]`
- **Downstream consumers:** M-11 integration sweep

### Tasks
- P3-01: Add at least 2 workspace-focused E2E tests.
  - Candidate location: `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/`
  - Suggested files:
    - `deal-workspace-mobile-readability.spec.ts`
    - `deal-workspace-tab-truthfulness.spec.ts`
  - Checkpoint: tests verify mobile readability and degraded tab truthfulness.
- P3-02: Run validation stack and archive output.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - Evidence: `/home/zaks/bookkeeping/missions/m05-artifacts/reports/validation.txt`
- P3-03: Publish completion and findings closure summaries.
  - Evidence:
    - `/home/zaks/bookkeeping/missions/m05-artifacts/reports/findings-closure.md`
    - `/home/zaks/bookkeeping/missions/m05-artifacts/reports/completion-summary.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert flaky test additions and stabilize selectors/assertions.
2. Revert only failing behavioral changes while retaining validated fixes.

### Gate P3
- 2+ new workspace-focused E2E tests exist and pass.
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- Evidence and bookkeeping are complete.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: F-08 resolved
Deal Workspace value readability at 375px is fixed with no hidden key data fields.

### AC-2: F-09 closed or explicitly dispositioned
Unavailable data surfaces in Materials/Case File/related flows are handled with explicit degraded semantics and user guidance.

### AC-3: F-10 resolved
Archived state signaling is clear and non-redundant.

### AC-4: Interaction closure complete
All visible Deal Workspace controls/tabs have `real/degraded/hidden` status with evidence.

### AC-5: Test reinforcement
At least 2 new Deal Workspace E2E tests are added and passing.

### AC-6: Validation and type safety
`make validate-local` and `npx tsc --noEmit` pass.

### AC-7: Evidence and bookkeeping
Before/after triad, closure reports, and `/home/zaks/bookkeeping/CHANGES.md` update are complete.

---

## Guardrails
1. Do not turn M-05 into a full deal domain refactor.
2. Keep fixes confined to workspace UX, tabs, and truthful degraded messaging.
3. Do not add backend features in this mission.
4. Preserve contract-aligned status semantics (no 500 degradation regressions).
5. Keep all evidence under `/home/zaks/bookkeeping/missions/m05-artifacts/`.
6. B7 anti-convergence does not apply to this mission — standardization is required.
7. Use deterministic selectors and avoid sleep-only test assertions.
8. Do not alter unrelated page-level shell behavior already stabilized by M-02.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: mission is 4 phases and expected below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** unless scope expands to XL.
- Broad component extraction for `deals/[id]` is **not applicable** unless directly required to close F-08/F-09/F-10.
- nuqs migration is **not applicable** in M-05 (applies to M-07 scope).

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture triad baseline screenshots for a real deal ID?
- [ ] Did I inventory all visible workspace controls/tabs in the interaction matrix?

### After each code change
- [ ] Did this change directly improve workspace readability/truthfulness?
- [ ] Are degraded states explicit and non-misleading?
- [ ] Did I preserve desktop/tablet layout while fixing mobile?

### Before marking COMPLETE
- [ ] Are key deal values readable at 375px?
- [ ] Are Materials/Case File unavailable states explicit when needed?
- [ ] Do `make validate-local` and `npx tsc --noEmit` pass now?
- [ ] Did I add at least 2 workspace-focused E2E tests?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | Phase 1-2 | Mobile readability, tab truthfulness, degraded messaging |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/loading.tsx` | Phase 1 | Optional loading readability alignment |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/deal-routing-create.spec.ts` | Phase 3 | Extend existing deal-flow assertions if applicable |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m05-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m05-artifacts/before/` | Phase 0 | Before screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m05-artifacts/after/` | Phase 2 | After screenshots/console captures |
| `/home/zaks/bookkeeping/missions/m05-artifacts/reports/m04-boundary-snapshot.md` | Phase 0 | Pre-M05 boundary snapshot |
| `/home/zaks/bookkeeping/missions/m05-artifacts/reports/interaction-closure.md` | Phase 0-2 | Control closure matrix |
| `/home/zaks/bookkeeping/missions/m05-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m05-artifacts/reports/findings-closure.md` | Phase 3 | F-08/F-09/F-10 closure summary |
| `/home/zaks/bookkeeping/missions/m05-artifacts/reports/completion-summary.md` | Phase 3 | Mission completion summary |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/deal-workspace-mobile-readability.spec.ts` | Phase 3 | New E2E test |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/deal-workspace-tab-truthfulness.spec.ts` | Phase 3 | New E2E test |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | F-08/F-09/F-10 baseline |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/interaction-wiring-inventory.md` | Workspace control inventory baseline |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md` | Prior contract alignment status |
| `/home/zaks/bookkeeping/missions/m04-artifacts/reports/findings-closure.md` | Adjacent Tier 1 chat mission context |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Phase 2 requirements |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation passes, artifacts are complete, and bookkeeping is updated. Do not proceed into M-06/M-07 implementation from this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M05*
