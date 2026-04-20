# MISSION: DASHBOARD-R5-POLISH-002
## R5 Corrective Remediation — Live UI Alignment for Chat History, Dashboard Layout, and Settings
## Date: 2026-02-12
## Classification: UI Corrective Remediation & Live Verification
## Prerequisite: DASHBOARD-R5-POLISH-001 (reported complete, invalidated by live UI evidence)
## Successor: QA-R5P-VERIFY-002 (optional independent QA) or direct closure if all AC pass with evidence

---

## Mission Objective

Remediate the R5 implementation-to-runtime mismatch identified by live user verification. This mission resolves three concrete discrepancies between claimed completion and observed UI behavior: invisible chat history actions, dashboard left-column dead space, and settings internal visual inconsistency.

This is a corrective remediation and verification mission, not a feature expansion mission. It must prioritize runtime truth (fresh compile + browser evidence) over static code claims.

**Source material:**
- `/home/zaks/bookkeeping/missions/DASHBOARD-R5-POLISH-001.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md`
- `/home/zaks/bookkeeping/docs/Dash-sreenshots-1/` (user live test evidence)

## Context

### Verified Mismatch Between Claim and Runtime

1. **Chat History 5 Actions not visible in live UI**
- Expected: 3-dot menu, badges, scope icons, message counts, relative time labels.
- Observed: plain history entries with none of the claimed enhancements visible.
- Root-cause hypothesis: stale `.next` output was served; runtime did not reflect latest source.

2. **Dashboard All Deals card not stretching**
- Expected: left column height visually balanced with right column stack.
- Observed: significant empty vertical gap below deals list.
- Root-cause hypothesis: `md:items-start` plus missing `flex-1` height propagation prevented stretch.

3. **Settings internal visual inconsistency**
- Expected: section internals feel uniform.
- Observed: AI Provider internals differ from other sections.
- Root-cause hypothesis: outer wrapper is consistent, internal subsection container styling diverges.

### Environment Reality at Failure Time

- `.next/BUILD_ID` was missing.
- `.next/cache` contained root-owned artifacts.
- Dev server was not running at verification time.
- User performed hard refreshes and still observed stale/incorrect output.

## Glossary

| Term | Definition |
|------|-----------|
| Runtime truth | What the browser renders after a fresh compile, not what source code implies |
| Flex propagation | Passing available height through parent and child containers with `flex-1` and `min-h-0` |
| Non-applicability note | Explicit artifact documenting why a conditional phase/task was intentionally not executed |
| Live verification | Browser-based evidence capture (Playwright screenshots + interaction checks) |

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after crash/interruption, run these commands first:

1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. `ls -la /home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/`

Then continue from the first incomplete phase gate.

## Context Checkpoint
<!-- Adopted from Improvement Area IA-1 -->

At the midpoint (after Phase 2), if context becomes constrained:

1. Write progress checkpoint: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/context-checkpoint.md`
2. Record completed gates and pending gates.
3. Continue in a fresh session from the saved checkpoint.

## Architectural Constraints

- **Runtime-first verification** — no acceptance based only on source inspection; browser evidence is mandatory.
- **Promise.allSettled discipline remains in force** — do not introduce `Promise.all` in dashboard data-fetching paths.
- **Server-side counts only** — do not reintroduce client `.length` display counts.
- **PIPELINE_STAGES source of truth** — no hardcoded stage lists while touching dashboard views.
- **Surface 9 compliance** — expected degradation uses `console.warn`; unexpected failures use `console.error`.
- **Contract surface discipline** — do not edit generated files directly.
- **Port 8090 forbidden** — never reference or use it.
- **Scope fence** — no backend/API/schema changes in this mission.

## Anti-Pattern Examples

### WRONG: Accepting code presence as proof of UI behavior
```
"ChatHistoryRail has the menu in source, so AC is done."
```

### RIGHT: Require fresh compile + live browser check
```
Reset .next -> start dev server -> verify in browser -> capture screenshots.
```

### WRONG: Grid forced to natural item heights
```
className='grid gap-4 md:grid-cols-3 md:items-start'
```

### RIGHT: Stretch + flex propagation
```
grid without items-start + left column min-h-0 + card/scrollarea flex-1.
```

### WRONG: Conditional tasks skipped without evidence
```
"Settings looked fine, skipped."  (no artifact)
```

### RIGHT: Explicit non-applicability record
```
Create non-applicability-notes.md with rationale + screenshots.
```

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Dev server still serves stale bundle after edits | HIGH | False pass/false fail results | Phase 0 hard reset of `.next`, compile readiness check, baseline screenshots |
| 2 | Dashboard stretch fix introduces collapsed or clipped deals content | MEDIUM | New layout regression | Phase 1 gate requires scroll behavior and empty/populated state checks |
| 3 | Chat action menu still perceived missing due hover-only opacity | MEDIUM | User still cannot discover actions | Phase 2 conditional visibility fallback + explicit before/after evidence |
| 4 | Settings consistency debate remains subjective without explicit criteria | MEDIUM | Endless rework loop | Phase 3 decision tree + standardized internal box pattern + non-app note option |
| 5 | Mission marked complete without validating local gates | LOW | Regressions leak | Phase 4 requires `npx tsc --noEmit` and `make validate-local` pass |

## Phase 0 — Environment Reset & Baseline
**Complexity:** S
**Estimated touch points:** 0 files modified

**Purpose:** Ensure runtime environment serves current code, then capture baseline evidence.

### Blast Radius
- **Services affected:** Dashboard dev runtime only (`localhost:3003`)
- **Pages affected:** `/dashboard`, `/chat`, `/settings`
- **Downstream consumers:** None

### Tasks
- P0-01: **Capture process and ownership baseline**
  - Commands:
    - `ps -ef | grep -E "next|3003" | grep -v grep`
    - `ls -la /home/zaks/zakops-agent-api/apps/dashboard/.next 2>/dev/null || true`
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p0-baseline-runtime.md`
  - **Checkpoint:** Confirm whether stale process/build artifacts exist.

- P0-02: **Stop stale Next.js processes and clean build artifacts**
  - Commands:
    - `pkill -f "next dev" || true`
    - `rm -rf /home/zaks/zakops-agent-api/apps/dashboard/.next`
  - Evidence: append command outputs to `p0-baseline-runtime.md`
  - **Checkpoint:** `.next` removed and no stale `next dev` process remains.

- P0-03: **Start fresh dashboard dev server and wait for readiness**
  - Command: `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run dev`
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p0-dev-server-ready.md`
  - **Checkpoint:** Server logs include successful compile/ready signal.

- P0-04: **Capture baseline UI snapshots after fresh compile**
  - Capture `/dashboard`, `/chat`, `/settings` screenshots.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/screenshots/p0-*`
  - **Checkpoint:** Baseline is now fresh-runtime, not stale-runtime.

### Decision Tree
- **IF** no stale process/artifacts exist in P0-01 -> continue with P0-03.
- **ELSE IF** stale process/artifacts exist -> complete P0-02 before any code edits.
- **ELSE** stop and resolve runtime environment before moving forward.

### Rollback Plan
1. Stop the restarted dev server.
2. Re-launch with prior local workflow if needed.
3. Verify: `cd /home/zaks/zakops-agent-api && make validate-local` passes.

### Gate P0
- Fresh compile readiness evidence captured.
- Baseline screenshots exist for all three target pages.
- Runtime reset artifacts recorded in `p0-baseline-runtime.md`.

## Phase 1 — Dashboard Layout Stretch Fix
**Complexity:** M
**Estimated touch points:** 1 file modified

**Purpose:** Remove dead vertical space and make All Deals card stretch with internal scroll.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/dashboard`
- **Downstream consumers:** None

### Tasks
- P1-01: **Update grid alignment strategy in dashboard page**
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - Remove `md:items-start` from the dashboard grid container.
  - **Checkpoint:** Grid uses stretch behavior at md+ breakpoints.

- P1-02: **Propagate flex constraints in left column**
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - Add `min-h-0` to left-column flex container (`md:col-span-2 ...`).
  - **Checkpoint:** Child card can consume constrained height.

- P1-03: **Enable All Deals card to stretch**
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - Add `flex-1` to the All Deals card class list while preserving `min-h-[300px]`.
  - **Checkpoint:** Card expands to fill remaining left-column height.

- P1-04: **Replace fixed-height scroll cap with flex fill**
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
  - Set `CardContent` to `flex-1 min-h-0 flex flex-col`.
  - Change deals `ScrollArea` from viewport-capped height to `flex-1`.
  - **Checkpoint:** List scroll is internal to card and uses available height.

- P1-05: **Capture responsive proof**
  - Screenshots at 375, 768, 1280 widths.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/screenshots/p1-dashboard-*`
  - **Checkpoint:** No large dead space under All Deals card.

### Decision Tree
- **IF** gap persists after P1-04 -> inspect nearest parent containers for missing `min-h-0` and correct only within `/dashboard/page.tsx`.
- **ELSE** proceed to Phase 2.

### Rollback Plan
1. Revert `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`.
2. Re-run dashboard screenshot capture.
3. Verify: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` passes.

### Gate P1
- Dashboard screenshots show left column visually balanced with right column.
- Deals list scrolls within the All Deals card.
- No clipping of empty or populated states.

## Phase 2 — Chat History Runtime Verification and Conditional Visibility Fix
**Complexity:** M
**Estimated touch points:** 0-1 files modified

**Purpose:** Confirm the 5-action history UI is truly rendered; apply targeted visibility fix only if still required.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/chat`
- **Downstream consumers:** Chat history UX only

### Tasks
- P2-01: **Verify enhanced history UI on fresh runtime**
  - Open `/chat`, toggle History rail, inspect entries.
  - Required visible elements: badges, scope icons, message counts, time labels.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/screenshots/p2-chat-history-open.png`
  - **Checkpoint:** Enhanced metadata visible on at least one entry.

- P2-02: **Verify 3-dot action affordance and 5 actions**
  - Hover a history item and confirm 3-dot control appears.
  - Open menu and verify all 5 actions are present.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/screenshots/p2-chat-menu-hover.png`
  - **Checkpoint:** Menu is discoverable and complete.

- P2-03: **Apply conditional visibility fallback only if needed**
  - File: `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx`
  - If menu remains effectively invisible, change trigger button from `opacity-0` to `opacity-50` while retaining hover transition.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p2-visibility-fix.md`
  - **Checkpoint:** 3-dot affordance visible without hover and fully visible on hover.

- P2-04: **Record non-applicability if fallback not needed**
  - Create explicit note if P2-03 is skipped.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/non-applicability-notes.md`

### Decision Tree
- **IF** P2-01 and P2-02 pass on fresh runtime -> skip P2-03 and record non-applicability.
- **ELSE IF** only trigger visibility fails -> apply P2-03 then re-verify.
- **ELSE** return to Phase 0 runtime reset and repeat verification before broadening scope.

### Rollback Plan
1. Revert `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx` if P2-03 was applied.
2. Re-open chat and re-check hover behavior.
3. Verify: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` passes.

### Gate P2
- Chat history entries visibly include enhanced metadata.
- 3-dot action trigger is discoverable and menu shows 5 actions.
- Conditional edit either applied with proof or skipped with explicit non-app note.

## Phase 3 — Settings Internal Consistency (Conditional)
**Complexity:** M
**Estimated touch points:** 0-6 files modified

**Purpose:** Normalize internal subsection visual pattern only if inconsistency remains after fresh-runtime verification.

### Blast Radius
- **Services affected:** Dashboard frontend only
- **Pages affected:** `/settings`
- **Downstream consumers:** None

### Tasks
- P3-01: **Audit internal subsection container patterns**
  - Files:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/ProviderSection.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/EmailSection.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/AgentSection.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/NotificationsSection.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/DataSection.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/AppearanceSection.tsx`
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p3-settings-audit.md`
  - **Checkpoint:** Differences are explicitly listed.

- P3-02: **Define one internal subsection box pattern**
  - Target pattern example: `rounded-lg border border-border/60 bg-muted/30 p-4`.
  - Apply only to mismatched internal subsection containers.
  - Evidence: append updated matrix in `p3-settings-audit.md`.
  - **Checkpoint:** Pattern consistency achieved across audited sections.

- P3-03: **Capture settings proof screenshots**
  - Capture at 375 and 1280 widths.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/screenshots/p3-settings-*`
  - **Checkpoint:** Internal containers present uniform treatment.

- P3-04: **If normalization not required, record explicit non-applicability**
  - Write rationale + screenshot references.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/non-applicability-notes.md`

### Decision Tree
- **IF** inconsistency remains and user wants alignment -> execute P3-02 and P3-03.
- **ELSE IF** inconsistency is acceptable and user does not request redesign -> skip edits and execute P3-04.
- **ELSE** escalate with side-by-side screenshot comparison before any additional design changes.

### Rollback Plan
1. Revert only modified settings section component files.
2. Re-open `/settings` and confirm pre-change rendering.
3. Verify: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` passes.

### Gate P3
- Either:
  - Settings internal styling normalized with before/after evidence, or
  - Non-applicability documented with screenshot-backed rationale.
- No unintended changes to section order/content behavior.

## Phase 4 — Mandatory Live Verification, Validation, and Bookkeeping
**Complexity:** S
**Estimated touch points:** 2 files modified + artifacts

**Purpose:** Close the mission using reproducible validation and evidence.

### Blast Radius
- **Services affected:** Dashboard frontend validation pipeline
- **Pages affected:** `/dashboard`, `/chat`, `/settings`
- **Downstream consumers:** Mission records, future QA pass

### Tasks
- P4-01: **Run compile and repo validation gates**
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p4-validation.txt`
  - **Checkpoint:** both commands exit 0.

- P4-02: **Capture final screenshot set**
  - Dashboard: prove All Deals stretch and internal scroll.
  - Chat: prove history metadata + 3-dot actions.
  - Settings: prove internal consistency outcome.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/screenshots/final-*`

- P4-03: **Compare final screenshots against user originals**
  - Compare to `/home/zaks/bookkeeping/docs/Dash-sreenshots-1/`.
  - Evidence: `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p4-comparison.md`
  - **Checkpoint:** each of the three reported issues explicitly marked resolved/conditional.

- P4-04: **Update mission records and change log**
  - Update `/home/zaks/bookkeeping/CHANGES.md`.
  - Write `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/completion-summary.md`.

### Decision Tree
- **IF** validation fails -> stop, fix failure, and re-run P4-01 before completion.
- **ELSE IF** screenshot evidence is incomplete -> do not close mission; capture missing evidence.
- **ELSE** close mission.

### Rollback Plan
1. Revert code edits introduced in Phases 1-3 if closure criteria cannot be met.
2. Re-run baseline checks from Phase 0.
3. Verify: `cd /home/zaks/zakops-agent-api && make validate-local` passes.

### Gate P4
- `npx tsc --noEmit` passes.
- `make validate-local` passes.
- Final screenshot set exists and comparison report completed.
- `CHANGES.md` and completion summary updated.

## Dependency Graph

```
Phase 0 (Environment Reset & Baseline)
    │
    ▼
Phase 1 (Dashboard Layout Stretch Fix)
    │
    ▼
Phase 2 (Chat Runtime Verification + Conditional Fix)
    │
    ▼
Phase 3 (Settings Internal Consistency — Conditional)
    │
    ▼
Phase 4 (Live Verification + Validation + Bookkeeping)
```

Phases execute sequentially. Phase 3 may complete as either code remediation or documented non-applicability.

## Acceptance Criteria

### AC-1: Fresh Runtime Baseline Established
Stale Next.js artifacts are cleared, dev server recompiles successfully, and baseline screenshots are captured from the fresh runtime.

### AC-2: Dashboard Dead Space Eliminated
At 1280 width, the All Deals card stretches to consume available left-column height with no large vertical dead zone.

### AC-3: Dashboard Card Scroll Behavior Correct
Deals list scrolls inside the All Deals card without clipping or collapsing empty/populated states.

### AC-4: Chat Enhanced History Metadata Visible
Chat history entries visibly show badges, scope icons, message counts, and relative time labels after fresh runtime build.

### AC-5: Chat 3-Dot Actions Discoverable
3-dot action menu is discoverable and displays all 5 actions; conditional opacity fallback is applied only when required and evidenced.

### AC-6: Settings Consistency Outcome Explicit
Settings internal consistency is either normalized across section internals or explicitly documented as non-applicable with evidence and rationale.

### AC-7: No Regressions
`cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` and `cd /home/zaks/zakops-agent-api && make validate-local` both pass.

### AC-8: Evidence and Bookkeeping Complete
Screenshots, comparison report, completion summary, and `/home/zaks/bookkeeping/CHANGES.md` updates are present.

## Guardrails

1. **Scope fence** — Do not add new backend endpoints, schema changes, or agent workflows.
2. **Generated file protection** — Do not edit generated files (`*.generated.ts`, generated schema outputs).
3. **Runtime truth required** — Do not mark any AC complete without browser evidence.
4. **Conditional edits require explicit decision logs** — every skipped conditional task must have a non-app note.
5. **No cross-page redesign** — only address the three reported issue families.
6. **Surface 9 conventions stay intact** — avoid stylistic drift outside target components.
7. **Port 8090 forbidden** — do not reference or use it.
8. **WSL hygiene** — ensure file ownership remains `zaks:zaks` for new artifacts under `/home/zaks/`.
9. **Validation discipline** — Phase 4 closure requires both TypeScript and local validation gates.
10. **No silent substitutions** — if a planned check cannot run, document why in non-applicability notes.

## Non-Applicability Notes

Record non-applicability in `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/non-applicability-notes.md` when applicable.

| Item | When N/A Is Allowed | Required Evidence |
|------|---------------------|------------------|
| P2-03 chat opacity fallback | 3-dot menu is already discoverable after fresh runtime verification | Hover and non-hover screenshots + written note |
| P3-02 settings normalization edits | User confirms current internal variation is acceptable after refreshed verification | Side-by-side settings screenshots + written note |
| Any live comparison sub-step | Source screenshot not accessible in runtime | Note path limitation and provide closest local evidence |

## Executor Self-Check Prompts

### After Phase 0
- [ ] "Did I prove the runtime is fresh, or did I assume it?"
- [ ] "Do I have baseline screenshots for dashboard, chat, and settings?"
- [ ] "Is there any remaining root-owned artifact in dashboard runtime output?"

### After Every Code Change
- [ ] "Did I verify this change in the browser, not just in code diff?"
- [ ] "Did I avoid touching generated files or backend scope?"
- [ ] "If this was conditional, did I document the decision path?"

### Before Mission Completion
- [ ] "Do all ACs have explicit evidence paths?"
- [ ] "Did `npx tsc --noEmit` and `make validate-local` pass in this final state?"
- [ ] "Did I update `/home/zaks/bookkeeping/CHANGES.md` and completion-summary.md?"
- [ ] "Did I record non-applicable conditional steps explicitly?"

## File Paths Reference

### Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx` | 1 | Grid/flex stretch + scroll propagation fixes |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/ChatHistoryRail.tsx` | 2 (conditional) | 3-dot trigger visibility fallback if required |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/ProviderSection.tsx` | 3 (conditional) | Internal subsection box normalization |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/EmailSection.tsx` | 3 (conditional) | Internal subsection box normalization |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/AgentSection.tsx` | 3 (conditional) | Internal subsection box normalization |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/NotificationsSection.tsx` | 3 (conditional) | Internal subsection box normalization |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/DataSection.tsx` | 3 (conditional) | Internal subsection box normalization |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/AppearanceSection.tsx` | 3 (conditional) | Internal subsection box normalization |
| `/home/zaks/bookkeeping/CHANGES.md` | 4 | Record mission execution and evidence links |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p0-baseline-runtime.md` | 0 | Runtime reset/process baseline evidence |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p0-dev-server-ready.md` | 0 | Fresh compile readiness evidence |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p2-visibility-fix.md` | 2 (conditional) | Chat visibility fallback decision and proof |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p3-settings-audit.md` | 3 (conditional) | Settings internal consistency audit matrix |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/non-applicability-notes.md` | 2/3/4 (conditional) | Explicit N/A documentation |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p4-validation.txt` | 4 | Compile + validate-local output |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/p4-comparison.md` | 4 | Original-vs-final screenshot comparison |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/context-checkpoint.md` | 2 (conditional) | Mid-mission continuation checkpoint |
| `/home/zaks/bookkeeping/missions/r5-polish-corrective-artifacts/reports/completion-summary.md` | 4 | Final AC closure report |

### Files to Read (sources of truth — do NOT modify)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/DASHBOARD-R5-POLISH-001.md` | Prior mission scope and claims |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Structural and quality standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist and validator reminders |
| `/home/zaks/bookkeeping/docs/Dash-sreenshots-1/` | User live screenshot baseline |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx` | Chat page integration context |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/settings/SettingsSectionCard.tsx` | Shared settings section wrapper pattern |

## Stop Condition

Mission is complete only when AC-1 through AC-8 all pass with artifact-backed evidence, both validation commands pass in the final state, and bookkeeping is updated.

Do not proceed to new R6 enhancements, backend persistence redesign, or unrelated UI refactors from this mission. Any remaining work becomes a separate mission.

---
*End of Mission Prompt — DASHBOARD-R5-POLISH-002*
