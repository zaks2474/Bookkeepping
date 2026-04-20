# MISSION: DASHBOARD-WORLDCLASS-REMEDIATION-001
## Critical Dashboard UX and Reliability Remediation from Post-Audit Operator Test Round
## Date: 2026-02-11
## Classification: Full-Stack Dashboard Remediation and UX Hardening
## Prerequisite: QA-S10-14-VERIFY-001, QA-FGH-VERIFY-001, and QA-CIH-VERIFY-001 are FULL PASS
## Successor: QA-DWR-VERIFY-001 (must report FULL PASS before this mission is considered closed)

---

## Preamble: Builder Operating Context

The builder auto-loads `/home/zaks/zakops-agent-api/CLAUDE.md`, memory, hooks, path-scoped rules, and deny rules. This mission does not restate baseline infra governance. It adds a targeted remediation execution plan for dashboard quality issues verified by operator testing and screenshot evidence.

This mission runs in a zero-trust execution model:
- Re-verify every finding before edits.
- Capture before/after evidence for each fix.
- Do not assume any stale audit claim is still true without local proof.

---

## 1. Mission Objective

Fix all dashboard issues reported in the latest operator validation round, using the report text and screenshot bundle as source of truth. The objective is to remove functional failures, restore deterministic flows, and raise UI quality to a world-class, consistent baseline.

This is a remediation mission, not a net-new feature build. The mission must preserve working behavior from prior passes while correcting layout, UX, and runtime regressions now visible in the live dashboard.

Scope includes dashboard frontend code, relevant Next.js proxy routes, and test coverage updates required to keep these regressions from returning.

Out of scope:
- Contract surface re-registration work (already closed by prior missions)
- Broad backend redesign unrelated to the reported issues
- New product features outside reported defects and UX gaps

---

## 2. Context

### 2.1 Source Material (authoritative inputs)

1. Audit baseline:
- `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md`

2. Screenshot source of truth (15 files):
- `/home/zaks/bookkeeping/docs/Dash-sreenshots-1/`

3. Operator testing findings (session-provided, mandatory coverage):
- Main dashboard layout height mismatch
- Ask Agent drawer UX quality gap
- Periodic "screen refreshed" popup quality concern
- Deals board view failure (`Failed to load deals`)
- Quarantine input persistence/ghost-character issue
- Chat tab missing history + poor agent selection UX
- Agent Activity tab identified as benchmark quality
- Onboarding step logic and prefill issues
- Setup/Data actions and scroll issues
- Settings navigation and design consistency issues

### 2.2 Screenshot Inventory (must all be reviewed in Phase 0)

1. `Screenshot 2026-02-10 213727.png`
2. `Screenshot 2026-02-10 213838.png`
3. `Screenshot 2026-02-10 214054.png`
4. `Screenshot 2026-02-10 214125.png`
5. `Screenshot 2026-02-10 214344.png`
6. `Screenshot 2026-02-10 214527.png`
7. `Screenshot 2026-02-10 215051.png`
8. `Screenshot 2026-02-10 215112.png`
9. `Screenshot 2026-02-10 215625.png`
10. `Screenshot 2026-02-10 215935.png`
11. `Screenshot 2026-02-10 220206.png`
12. `Screenshot 2026-02-10 220703.png`
13. `Screenshot 2026-02-10 220955.png`
14. `Screenshot 2026-02-10 221009.png`
15. `Screenshot 2026-02-10 221028.png`

### 2.3 Findings Registry (must be fully remediated)

| ID | Finding | Required End State |
|---|---|---|
| F-01 | Dashboard layout imbalance: `All Deals` panel is visibly shorter than right-side stack (`Agent Activity`, `Execution Inbox`, `Quarantine`) | Desktop dashboard columns are visually aligned; no large dead zone under `All Deals`; responsive behavior remains correct on mobile |
| F-02 | Ask Agent drawer has weak UX and unclear input/composer experience | Drawer has clear message composition area, readable transcript hierarchy, and obvious send interaction |
| F-03 | Auto popup ("Dashboard refreshed / All data has been updated") appears during periodic refresh and feels noisy | Background refresh is silent/non-intrusive; success toast appears only for explicit user-triggered refresh |
| F-04 | Deals board view runtime failure: `Failed to load deals` with `currentDeals.forEach is not a function` | Board view loads consistently; data shape handling is resilient for wrapped/unwrapped API payloads |
| F-05 | Quarantine input state bug: persistent ghost character and sticky input behavior after refresh | Inputs are deterministic; no phantom character reappears unless deliberately entered and explicitly persisted |
| F-06 | Chat tab lacks world-class structure: no visible chat history rail; provider/agent selector UX is poor | Chat has session/history navigation and improved provider/agent control UX |
| F-07 | Agent Activity tab is strongest UI and should be benchmark | Shared UI language/tokens are aligned to Agent Activity quality level across dashboard/chat/drawer surfaces |
| F-08 | Onboarding logic issues: lands at wrong step, continue order breaks, stale prefilled values persist | Onboarding follows canonical sequence `Welcome -> Your Profile -> Connect Email -> Meet Your Agent -> Preferences -> All Set` with deterministic progression |
| F-09 | Setup/Data section issues: scroll/structure inconsistency and non-functional actions (notably export) | Settings/Setup sections are scroll-safe, aligned, and actions execute with clear success/failure behavior |
| F-10 | Settings page lacks clear return path and visual consistency with rest of app | Settings includes explicit navigation return affordance and consistent page-shell structure |

### 2.4 Current Code-Level Anchors (already observed)

- Deals board crash locus:
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx`
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts`
- Dashboard refresh toast locus:
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
- Ask Agent drawer locus:
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/agent/AgentDrawer.tsx`
- Chat UX locus:
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx`
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ProviderSelector.tsx`
- Quarantine input state locus:
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
- Onboarding sequence locus:
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx`
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useOnboardingState.ts`
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/onboarding/onboarding-api.ts`
- Settings/Setup and export locus:
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/DataSection.tsx`
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/settings/preferences-api.ts`
  - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/data/export/route.ts`

---

## Crash Recovery Protocol <!-- Adopted from Improvement Area IA-2 -->

If session is interrupted:

```bash
cd /home/zaks/zakops-agent-api && git status --short
cd /home/zaks/zakops-agent-api && make validate-local
cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check
cd /home/zaks/bookkeeping && ls -1 /home/zaks/bookkeeping/docs/Dash-sreenshots-1
```

If validation fails during recovery, classify pre-existing vs mission-induced breakage before proceeding.

---

## Continuation Protocol <!-- Adopted from Improvement Area IA-7 -->

At every stop point update:
- `/home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-WORLDCLASS-REMEDIATION-001.md`

Checkpoint minimum content:
1. Completed phases/tasks
2. Open tasks by ID
3. Current validation status
4. Known blockers or decisions
5. Exact next command

---

## Context Checkpoint <!-- Adopted from Improvement Area IA-1 -->

If context pressure rises:
1. Write status snapshot to checkpoint file above.
2. Commit logically complete work.
3. Resume with Crash Recovery Protocol.

---

## 2b. Glossary

| Term | Definition |
|---|---|
| World-class baseline | UI/UX quality bar set by current `Agent Activity` page clarity and structure |
| Drawer | Right-side `Ask Agent` slide-over component |
| Ghost character bug | Input state that reappears after user deletion/refresh due stale persistence/control wiring |
| Deterministic onboarding | Step order and transitions always follow canonical sequence without hidden jumps |
| Manual refresh vs auto refresh | User button-triggered refresh vs timed background polling |

---

## 3. Architectural Constraints

- **Fix all listed findings, no scope drift**
  - Meaning: Every F-01 to F-10 item must be explicitly remediated and evidenced.
  - Why: The operator asked for complete closure with no dropped issues.

- **Zero-trust evidence discipline**
  - Meaning: Capture before/after proof for each finding; do not mark fixed without reproducible verification.
  - Why: Prevent false closure.

- **Preserve existing governance patterns**
  - Meaning: Keep `Promise.allSettled` degradation behavior where applicable and maintain `console.warn` for expected degradation.
  - Why: Surface 9 and prior hardening missions established this standard.

- **No generated-file edits**
  - Meaning: Do not directly edit generated types/contracts.
  - Why: Contract sync pipeline ownership.

- **No migration/schema edits**
  - Meaning: No DB migration changes in this mission.
  - Why: Out of scope and high blast radius.

- **No mock-data fallback masking real failures**
  - Meaning: Do not hide runtime errors by silently substituting fake business data.
  - Why: Must fix root cause, not cosmetic symptom.

- **Responsive behavior must not regress**
  - Meaning: Every layout fix must be verified on desktop and mobile breakpoints.
  - Why: Dashboard is multi-viewport.

- **Shared state consistency**
  - Meaning: Ask Agent drawer and Chat page must use consistent session/thread behavior.
  - Why: Prevent fragmented assistant context.

- **Accessibility baseline**
  - Meaning: Interactive controls remain keyboard-accessible with visible focus and readable contrast.
  - Why: UX quality and compliance.

- **WSL hygiene**
  - Meaning: LF line endings and correct ownership for any new scripts/docs.
  - Why: Avoid delayed execution failures.

---

## 3b. Anti-Pattern Examples

### WRONG: Assuming deals payload is always array
```ts
const currentDeals = deals || [];
currentDeals.forEach((deal) => {
  grouped[deal.stage].push(deal);
});
```

### RIGHT: Normalize payload shape before iteration
```ts
const currentDeals = Array.isArray(deals) ? deals : (deals?.deals ?? []);
for (const deal of currentDeals) {
  if (grouped[deal.stage]) grouped[deal.stage].push(deal);
}
```

### WRONG: Showing success toast for timed background refresh
```ts
setInterval(() => fetchData(false), 60000); // emits success toast every cycle
```

### RIGHT: Distinguish refresh source and toast only manual action
```ts
fetchData({ source: 'auto' });   // silent
fetchData({ source: 'manual' }); // toast.success
```

### WRONG: Forcing resumed onboarding step without explicit user choice
```ts
if (currentStep > 0) {
  setCurrentStep(currentStep); // always resumes mid-flow
}
```

### RIGHT: Explicit resume vs start-fresh path
```ts
// default to Welcome unless user chooses Resume
setCurrentStep(0);
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | UI looks improved but board/settings runtime errors still occur under real payloads | HIGH | HIGH | Phase 1 requires payload-shape hardening + regression tests |
| 2 | Onboarding still jumps due persisted backend step state | HIGH | HIGH | Phase 2 enforces explicit start/resume model + reset path |
| 3 | Dashboard toast noise returns after future refactor | MEDIUM | MEDIUM | Phase 6 test asserts manual-only success toast |
| 4 | Settings scroll/nav fix regresses responsive layout | MEDIUM | MEDIUM | Phase 5 includes desktop/mobile verification gate |
| 5 | Chat drawer and full chat diverge again | MEDIUM | HIGH | Phase 4 shared-session gate + e2e shared-state test |

---

## 4. Phases

## Phase 0 - Discovery and Baseline Evidence
**Complexity:** M  
**Estimated touch points:** 2 files created (baseline docs), 0 product code changes

**Purpose:** Reconfirm all findings and capture reproducible baseline before edits.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** Dashboard, Deals, Quarantine, Chat, Onboarding, Settings (verification only)
- **Downstream consumers:** None

### Tasks
- P0-01: **Build screenshot index and issue mapping**
  - Create `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md`.
  - Map all 15 screenshots to F-01..F-10.
  - **Checkpoint:** Every screenshot is linked to at least one finding.

- P0-02: **Capture baseline reproduction report**
  - Create `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-BASELINE.md`.
  - Record reproducibility for each finding (`reproduced`, `partial`, `not_reproduced`).
  - **Checkpoint:** Baseline includes exact repro steps for each reproduced issue.

- P0-03: **Capture baseline validation**
  - Run and record:
    - `cd /home/zaks/zakops-agent-api && make validate-local`
    - `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check`
    - `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test`
  - **Checkpoint:** Baseline failures are tagged pre-existing vs mission-induced.

### Decision Tree
- **IF** any source finding is not reproducible:
  - Document as `not_reproduced` with evidence and still include regression guard.
- **ELSE**
  - Proceed with full remediation sequence.

### Rollback Plan
1. No product-code rollback needed (discovery only).
2. Keep baseline artifacts as immutable evidence.

### Gate P0
- Baseline report exists with all F-01..F-10 statuses.
- Screenshot index exists and covers all 15 files.
- Baseline validation output captured.

---

## Phase 1 - Functional Breakers First (Board + Export)
**Complexity:** L  
**Estimated touch points:** 5-8 files

**Purpose:** Remove hard runtime failures and broken actions that block core usability.

### Blast Radius
- **Services affected:** Dashboard frontend + Next.js proxy routes (+ backend endpoint compatibility)
- **Pages affected:** `/deals`, `/settings`
- **Downstream consumers:** Deal board users, data export users

### Tasks
- P1-01: **Fix board-view data-shape crash**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts`
  - Ensure deals payload normalization handles both array and wrapped response shapes.
  - **Checkpoint:** `currentDeals.forEach is not a function` cannot be reproduced.

- P1-02: **Add board payload regression test**
  - Create/update:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/deals-board-shape.test.ts`
  - **Checkpoint:** Test fails pre-fix and passes post-fix.

- P1-03: **Fix Export All Data 404 path/contract mismatch**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/settings/preferences-api.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/data/export/route.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/DataSection.tsx`
  - Ensure export route points to a valid backend contract (or explicit degraded behavior with clear user message if backend endpoint unavailable).
  - **Checkpoint:** Export action no longer triggers runtime overlay error in settings flow.

- P1-04: **Harden export error handling**
  - Ensure recoverable 4xx/5xx responses are surfaced as user-safe messages, not raw runtime overlays.
  - **Checkpoint:** Failed export path is graceful and actionable.

### Decision Tree
- **IF** backend provides export endpoint:
  - Return downloadable payload path.
- **ELSE IF** backend endpoint absent:
  - Return explicit degraded response and UI copy; do not crash.
- **ELSE**
  - Document as backend contract gap with follow-up ticket reference.

### Rollback Plan
1. Revert Phase 1 commits only.
2. Re-run:
   - `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check`
   - `cd /home/zaks/zakops-agent-api && make validate-local`

### Gate P1
- Board view loads without runtime error.
- Settings export action is functional or gracefully degraded without overlay crash.
- New board-shape regression test passes.
- `make validate-local` passes.

---

## Phase 2 - Onboarding and Input State Determinism
**Complexity:** L  
**Estimated touch points:** 6-9 files

**Purpose:** Remove step-order jumps and input persistence artifacts.

### Blast Radius
- **Services affected:** Dashboard onboarding flow + quarantine UI
- **Pages affected:** `/onboarding`, `/quarantine`
- **Downstream consumers:** New-user onboarding and operator review workflow

### Tasks
- P2-01: **Enforce canonical onboarding sequence**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useOnboardingState.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/onboarding/onboarding-api.ts`
  - Required sequence:
    - `Welcome -> Your Profile -> Connect Email -> Meet Your Agent -> Preferences -> All Set`
  - **Checkpoint:** `Continue` always advances exactly one step in order.

- P2-02: **Fix onboarding entry behavior**
  - Ensure default onboarding landing is `Welcome` unless user explicitly resumes.
  - Ensure `Start Fresh` performs real reset (backend + local/session state).
  - **Checkpoint:** Opening `/onboarding` does not force step 4 without explicit resume intent.

- P2-03: **Remove stale prefilled artifacts**
  - Clean stale or unintended persistent values in onboarding fields.
  - **Checkpoint:** No sticky stale entries after refresh unless intentionally persisted.

- P2-04: **Fix quarantine ghost-input behavior**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
  - Remove phantom character reappearance and sticky first-character behavior.
  - **Checkpoint:** Edit/delete/refresh cycle preserves exactly the expected value state.

- P2-05: **Add onboarding/input regression tests**
  - Create/update:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/onboarding-sequence.test.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/quarantine-input-state.test.tsx`
  - **Checkpoint:** Tests capture the previously failing behavior.

### Decision Tree
- **IF** resume state is required for returning users:
  - Make resume explicit via user choice and keep `Welcome` default for new/manual-start flow.
- **ELSE**
  - Reset onboarding route entry to step 0 consistently.

### Rollback Plan
1. Revert onboarding/input changes.
2. Re-run onboarding and quarantine smoke tests.

### Gate P2
- Onboarding no longer jumps incorrectly.
- Quarantine input ghost-character issue no longer reproduces.
- New onboarding/input tests pass.
- `make validate-local` passes.

---

## Phase 3 - Dashboard Layout Symmetry and Refresh UX
**Complexity:** M  
**Estimated touch points:** 3-6 files

**Purpose:** Eliminate visual imbalance and intrusive refresh notifications.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/dashboard`
- **Downstream consumers:** Operator dashboard daily workflow

### Tasks
- P3-01: **Align main dashboard column heights**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/ExecutionInbox.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AgentActivityWidget.tsx`
  - Match `All Deals` panel visual vertical rhythm to right-column stack on desktop.
  - **Checkpoint:** No obvious dead zone under `All Deals` in target viewport.

- P3-02: **Refactor refresh feedback model**
  - Separate manual refresh feedback from timed background refresh.
  - Keep manual success toast; remove periodic auto-refresh toast spam.
  - **Checkpoint:** No repeating "Dashboard refreshed" popup during passive use.

- P3-03: **Preserve responsive behavior**
  - Verify layout on desktop and mobile widths.
  - **Checkpoint:** No overflow clipping or broken stacking.

### Decision Tree
- **IF** exact pixel symmetry harms smaller viewports:
  - Use responsive height strategy with breakpoint-specific behavior.
- **ELSE**
  - Keep unified height model.

### Rollback Plan
1. Revert layout/toast commits.
2. Restore baseline dashboard rendering.

### Gate P3
- F-01 and F-03 are visually and behaviorally resolved.
- Desktop and mobile checks pass.
- `make validate-local` passes.

---

## Phase 4 - Ask Agent and Chat UX Hardening
**Complexity:** XL  
**Estimated touch points:** 5-10 files

**Purpose:** Make assistant surfaces coherent, navigable, and benchmark-grade.

### Blast Radius
- **Services affected:** Dashboard chat/drawer flows
- **Pages affected:** `/dashboard`, `/chat`
- **Downstream consumers:** Agent interactions and proposal workflows

### Tasks
- P4-01: **Redesign Ask Agent drawer clarity**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/agent/AgentDrawer.tsx`
  - Improve visual hierarchy, message readability, and input/composer discoverability.
  - **Checkpoint:** Empty state and active state both have clear primary action.

- P4-02: **Add chat history rail/session recall**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx`
  - Add visible conversation history/session switching UI.
  - **Checkpoint:** User can reopen a prior chat without losing context.

- P4-03: **Redesign provider/agent selector UX**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ProviderSelector.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx`
  - Replace weak controls with clear, modern selector presentation.
  - **Checkpoint:** Provider and scope controls are visually readable and logically grouped.

- P4-04: **Ensure drawer and chat state consistency**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/agent/AgentDrawer.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx`
  - Keep shared session behavior across both entry points.
  - **Checkpoint:** Message posted in one surface appears in the other for same session.

- P4-05: **Apply Agent Activity as style benchmark**
  - Reference:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/page.tsx`
  - Reuse visual rhythm/tokens where appropriate across chat and drawer.
  - **Checkpoint:** No obvious style break between benchmark and remediated surfaces.

### Decision Tree
- **IF** history rail density harms mobile:
  - Use collapsible drawer or tabbed compact history on small screens.
- **ELSE**
  - Keep persistent rail on desktop.

### Rollback Plan
1. Revert chat/drawer UX commits only.
2. Re-run chat shared-state tests.

### Gate P4
- F-02 and F-06 resolved with visible UX improvements.
- Shared state behavior remains intact.
- `make validate-local` passes.

---

## Phase 5 - Settings and Setup Cohesion
**Complexity:** M  
**Estimated touch points:** 3-6 files

**Purpose:** Fix settings structural consistency, scroll behavior, and return navigation clarity.

### Blast Radius
- **Services affected:** Dashboard settings page
- **Pages affected:** `/settings`
- **Downstream consumers:** User preference workflows

### Tasks
- P5-01: **Fix settings scroll/container behavior**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
  - Ensure page scroll behavior is deterministic inside app shell (`body` is overflow-hidden globally).
  - **Checkpoint:** Full settings content is reachable by scroll in normal viewport.

- P5-02: **Add explicit return navigation**
  - Target:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx`
  - Provide clear, visible route back to prior context/dashboard.
  - **Checkpoint:** Operator can navigate away from settings without relying on browser back.

- P5-03: **Validate setup actions**
  - Ensure retention save, export, and destructive actions provide consistent feedback states.
  - **Checkpoint:** No silent/no-op click paths.

### Decision Tree
- **IF** shared page shell component can be reused safely:
  - Migrate settings to that shell.
- **ELSE**
  - Implement equivalent scroll/navigation structure directly.

### Rollback Plan
1. Revert settings-only commits.
2. Re-run settings smoke.

### Gate P5
- F-09 and F-10 resolved.
- Settings UX is consistent with rest of app.
- `make validate-local` passes.

---

## Phase 6 - Regression Harness and Verification
**Complexity:** L  
**Estimated touch points:** 6-10 files

**Purpose:** Lock fixes with automated verification and produce evidence for QA.

### Blast Radius
- **Services affected:** Test harnesses and CI-visible checks
- **Pages affected:** Dashboard, Deals, Quarantine, Chat, Onboarding, Settings
- **Downstream consumers:** QA mission and future remediation passes

### Tasks
- P6-01: **Add/extend unit and integration tests**
  - Create/update:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/deals-board-shape.test.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/dashboard-refresh-toast.test.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/onboarding-sequence.test.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/quarantine-input-state.test.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/settings-export-route.test.ts`
  - **Checkpoint:** Every F-01..F-10 cluster has at least one automated guard.

- P6-02: **Add focused e2e coverage**
  - Create/update:
    - `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/dashboard-worldclass-remediation.spec.ts`
  - Include scenarios for board view load, onboarding sequence, chat history rail, settings export behavior.
  - **Checkpoint:** E2E script exercises top user paths from findings list.

- P6-03: **Run validation suite and capture evidence**
  - Run:
    - `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run type-check`
    - `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test`
    - `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test:e2e`
    - `cd /home/zaks/zakops-agent-api && make validate-local`
  - Store outputs in:
    - `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md`
  - **Checkpoint:** All required commands recorded with pass/fail status.

### Rollback Plan
1. Revert failing test additions if they are invalid.
2. Keep only stable tests aligned to accepted behavior.

### Gate P6
- Required test and validation commands pass.
- Evidence file exists with command outputs.

---

## Phase 7 - Bookkeeping and Handoff
**Complexity:** S  
**Estimated touch points:** 2-3 files

**Purpose:** Produce auditable closure artifacts for QA and stakeholders.

### Blast Radius
- **Services affected:** None (documentation only)
- **Pages affected:** None
- **Downstream consumers:** QA verifier, auditor, operator handoff

### Tasks
- P7-01: **Create completion report**
  - Create:
    - `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md`
  - Include:
    - F-01..F-10 reconciliation (`Before`, `After`, `Evidence Path`, `Status`)
    - test/validation summary
    - open follow-ups (if any)

- P7-02: **Update mission checkpoint**
  - Update:
    - `/home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-WORLDCLASS-REMEDIATION-001.md`
  - Mark mission ready for QA successor.

### Gate P7
- Completion report exists and is complete.
- Checkpoint reflects final state and next mission.

---

## 4b. Dependency Graph

```text
Phase 0 (Discovery + Baseline)
    |
    v
Phase 1 (Functional Breakers)
    |
    v
Phase 2 (Onboarding + Input Determinism)
    |
    +--------------------+
    |                    |
    v                    v
Phase 3 (Dashboard UX)   Phase 4 (Chat/Drawer UX)
    |                    |
    +---------+----------+
              |
              v
Phase 5 (Settings/Setup Cohesion)
              |
              v
Phase 6 (Regression Harness + Validation)
              |
              v
Phase 7 (Bookkeeping + Handoff)
              |
              v
QA-DWR-VERIFY-001
```

---

## 5. Acceptance Criteria

### AC-1: Deals Board Reliability
`/deals?view=board` loads with no `currentDeals.forEach` runtime error and no "Failed to load deals" blocker.

### AC-2: Export Action Integrity
Settings `Export All Data` no longer fails with raw runtime overlay and follows a deterministic success/degraded path.

### AC-3: Onboarding Step Order Integrity
Onboarding transitions strictly follow `Welcome -> Your Profile -> Connect Email -> Meet Your Agent -> Preferences -> All Set`.

### AC-4: Onboarding Entry Consistency
Onboarding route defaults to Welcome unless explicit resume action is selected.

### AC-5: Quarantine Input Determinism
No ghost character or sticky single-character artifact appears after delete/refresh cycles.

### AC-6: Dashboard Layout Symmetry
Dashboard main layout no longer has obvious left/right vertical imbalance in target desktop viewport.

### AC-7: Refresh Notification Quality
Background refresh does not produce repetitive success toasts; manual refresh still provides explicit feedback.

### AC-8: Ask Agent Drawer Quality
Drawer includes clear composer/input area, readable messages, and coherent interaction flow.

### AC-9: Chat Information Architecture
Chat page includes usable session/history navigation and improved provider/agent selection UX.

### AC-10: Settings Navigation and Structure
Settings page is scroll-safe and includes clear return navigation path to the app workflow.

### AC-11: No Regressions
`make validate-local`, dashboard type-check, unit tests, and e2e suite pass after remediation.

### AC-12: Bookkeeping Complete
Completion and validation evidence artifacts are produced under `/home/zaks/bookkeeping/docs/` and checkpoint is updated.

---

## 6. Guardrails

1. Do not skip any finding from F-01 through F-10.
2. Do not modify generated files, migration files, or unrelated infrastructure contracts.
3. Do not hide runtime issues by injecting mock business data.
4. Preserve existing surface/governance guardrail behavior unless explicitly required by this mission.
5. Keep console severity semantics: expected degradation uses warn-level paths.
6. Keep responsive behavior and keyboard accessibility intact.
7. Do not introduce destructive workflow changes in onboarding without explicit reset paths.
8. All fixes must have before/after evidence.
9. Keep repository scope limited to dashboard + directly related proxy route files.
10. Record all residual gaps as explicit follow-ups; do not silently defer.

---

## 7. Executor Self-Check Prompts

### After Phase 0
- [ ] Did I map all 15 screenshots to findings?
- [ ] Did I verify each finding in the running app, not just by reading code?
- [ ] Did I record baseline validation output?

### After Phase 1
- [ ] Does board view handle both array and wrapped data payloads?
- [ ] Did export behavior stop failing with runtime overlay?
- [ ] Did I add at least one automated guard for functional breaker regressions?

### After Phase 2
- [ ] Can onboarding only advance one step at a time in canonical order?
- [ ] Does "Start Fresh" actually reset state, not just hide a banner?
- [ ] Are quarantine/input ghost-value bugs reproducibly gone?

### After Phase 3 and Phase 4
- [ ] Is dashboard refresh feedback user-intent aware (manual vs auto)?
- [ ] Is Ask Agent composer obvious and usable?
- [ ] Can I see and recall prior chat sessions?

### Before Mission Complete
- [ ] Did I run all required validation commands now (not earlier)?
- [ ] Did I update completion and checkpoint artifacts?
- [ ] Are all AC-1..AC-12 clearly evidenced?

---

## 8. File Paths Reference

### Files to Modify

| File | Phase | Change |
|---|---|---|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deals/DealBoard.tsx` | 1 | Fix board payload handling and runtime robustness |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts` | 1 | Normalize deals data shape for board consumer |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/settings/preferences-api.ts` | 1 | Align export client behavior and error handling |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/data/export/route.ts` | 1 | Align proxy route contract for export |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/DataSection.tsx` | 1,5 | Harden export UX states and setup action feedback |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/OnboardingWizard.tsx` | 2 | Fix step entry/progression and stale state behavior |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useOnboardingState.ts` | 2 | Make onboarding state transitions deterministic |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/onboarding/onboarding-api.ts` | 2 | Correct reset/migration/resume semantics |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | 2 | Remove ghost-character/sticky input behavior |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx` | 3 | Fix panel symmetry and manual-vs-auto refresh feedback |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/ExecutionInbox.tsx` | 3 | Height/scroll behavior alignment with dashboard layout |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AgentActivityWidget.tsx` | 3,4 | Layout alignment and benchmark token consistency |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/agent/AgentDrawer.tsx` | 4 | Drawer UX redesign and composer clarity |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx` | 4 | Add history rail and improve chat IA |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ProviderSelector.tsx` | 4 | Improve provider selector UX clarity |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/settings/page.tsx` | 5 | Fix scroll shell, layout consistency, and return navigation |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsNav.tsx` | 5 | Add/clarify settings navigation behavior |

### Files to Create

| File | Phase | Purpose |
|---|---|---|
| `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-SCREENSHOT-INDEX.md` | 0 | Screenshot-to-finding mapping |
| `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-BASELINE.md` | 0 | Baseline reproduction and validation report |
| `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-VALIDATION.md` | 6 | Validation command evidence |
| `/home/zaks/bookkeeping/docs/DASHBOARD-WORLDCLASS-REMEDIATION-001-COMPLETION.md` | 7 | Final completion and reconciliation report |
| `/home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-WORLDCLASS-REMEDIATION-001.md` | 7 | Continuation + final checkpoint state |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/deals-board-shape.test.ts` | 1,6 | Board payload regression guard |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/dashboard-refresh-toast.test.tsx` | 3,6 | Manual-vs-auto refresh feedback guard |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/onboarding-sequence.test.tsx` | 2,6 | Step order regression guard |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/quarantine-input-state.test.tsx` | 2,6 | Input ghost-state regression guard |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/settings-export-route.test.ts` | 1,6 | Export route/UX guard |
| `/home/zaks/zakops-agent-api/apps/dashboard/tests/e2e/dashboard-worldclass-remediation.spec.ts` | 6 | End-to-end path coverage for this mission |

### Files to Read (sources of truth - do NOT modify)

| File | Purpose |
|---|---|
| `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md` | Audit context baseline |
| `/home/zaks/bookkeeping/docs/Dash-sreenshots-1/` | Screenshot evidence source |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Prompt standard compliance |
| `/home/zaks/zakops-agent-api/CLAUDE.md` | Active architecture and guardrail context |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/agent/activity/page.tsx` | Benchmark UI reference surface |

---

## 9. Stop Condition

Stop when all AC-1 through AC-12 are met, every finding F-01 through F-10 is closed with evidence, required validations pass, and completion/checkpoint artifacts are written.

Do not proceed to unrelated feature work, infra surface expansion, or backend redesign in this mission. Any additional improvements discovered during execution must be documented as follow-up opportunities, not silently included.

---
*End of Mission Prompt - DASHBOARD-WORLDCLASS-REMEDIATION-001*
