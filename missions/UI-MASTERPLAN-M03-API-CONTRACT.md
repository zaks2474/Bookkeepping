# MISSION: UI-MASTERPLAN-M03
## API Failure Contract Alignment and Convention Drift Closure
## Date: 2026-02-11
## Classification: Frontend/Proxy Contract Remediation
## Prerequisite: UI-MASTERPLAN-M02 (Shell foundation complete)
## Successor: UI-MASTERPLAN-M01 (state consistency) and Phase 2 page missions

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks/zakops-agent-api && git log --oneline -5`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Re-run baseline greps recorded in `/home/zaks/bookkeeping/missions/m03-artifacts/reports/baseline-contract-scan.md`

---

## Mission Objective
Align frontend and proxy route behavior with declared contract conventions before page-level polish missions proceed. This mission closes known drift around backend-unavailable status semantics, stage source-of-truth usage, and display-count conventions.

This is contract alignment, not feature expansion. Do not build new backend capabilities. Normalize existing behavior and strengthen validator enforcement.

Out of scope: deep page visual polish (handled in Phase 2 missions) and broad refactors unrelated to contract consistency.

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md`
- `/home/zaks/bookkeeping/missions/m00-artifacts/findings/console-error-catalog.md`

Evidence-backed scope includes:
- F-09/F-16 cross-mission contract implications from Deal Workspace and Settings error behavior.
- Non-502 degraded responses currently present in selected route handlers.
- Hardcoded stage array in `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/page.tsx`.
- Client-side display count patterns in dashboard/deals pages.
- Potential duplicate preferences fetch behavior observed in Settings (F-16), requiring explicit verification and fix if non-StrictMode duplication exists.

B7 clarification required by F-11: **B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.**

---

## Glossary

| Term | Definition |
|------|------------|
| Contract drift | Deviation between documented conventions and runtime implementation |
| Backend-unavailable semantics | Expected degraded response contract for unreachable dependencies (JSON 502) |
| Source-of-truth stage taxonomy | `PIPELINE_STAGES` exported from `execution-contracts.ts` |
| Display count convention | User-facing totals should come from server-computed fields, not local list length when total semantics are intended |

---

## Architectural Constraints
- **Proxy degradation contract:** Backend-unavailable conditions must return structured JSON with status 502.
- **Stage taxonomy contract:** Stage lists must use `PIPELINE_STAGES` from `/home/zaks/zakops-agent-api/apps/dashboard/src/types/execution-contracts.ts`.
- **Display count convention:** Where UI labels represent global totals, use server-computed values, not client `.length` derived subsets.
- **Promise resilience rule:** Multi-fetch page loads must use `Promise.allSettled` with typed fallbacks.
- **Change-boundary isolation:** Capture a clean M-02 boundary snapshot before any M-03 code edits (commit/tag preferred; evidence manifest fallback required if commit is blocked).
- **B7 clarification (mandatory):** B7 anti-convergence does not apply to this mission — we are standardizing existing patterns.
- **Validation and enforcement:** Update and run `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` plus `make validate-local`.

---

## Anti-Pattern Examples

### WRONG: Return 500 for backend-unavailable degradation
```text
catch (error) {
  return NextResponse.json({ error: 'backend_unavailable' }, { status: 500 });
}
```

### RIGHT: Return JSON 502 for backend-unavailable degradation
```text
catch (error) {
  return NextResponse.json({ error: 'backend_unavailable' }, { status: 502 });
}
```

### WRONG: Hardcoded stage array in UI form
```text
const STAGES = ['inbound', 'screening', 'qualified', ...];
```

### RIGHT: Import canonical stage taxonomy
```text
Use PIPELINE_STAGES from execution-contracts.ts.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | Status-code normalization misses some degraded routes | Medium | High | Baseline and post-change grep sweep for backend_unavailable/500 patterns |
| 2 | Count convention updates unintentionally alter user-facing semantics | Medium | Medium | Restrict to labels that imply total/global counts; verify against API payload fields |
| 3 | Settings duplicate fetch diagnosis misattributes StrictMode behavior | High | Medium | Verify in production-mode run and network trace before applying fixes |
| 4 | Validator script updates create false positives | Medium | Medium | Add narrow, path-scoped checks and validate against existing codebase |
| 5 | Mission drifts into unrelated refactoring | Medium | Medium | Keep touch points limited to explicitly listed contract paths |

---

## Phase 0 - Contract Baseline Scan
**Complexity:** S
**Estimated touch points:** 1-3 files

**Purpose:** Freeze current contract-drift inventory and define exact remediation list.

### Blast Radius
- **Services affected:** Dashboard proxy routes and selected page contracts
- **Pages affected:** Dashboard, Deals, New Deal, Settings, Deal Workspace, Chat
- **Downstream consumers:** Phase 2 page missions depend on this baseline

### Tasks
- P0-00: Isolate and snapshot completed M-02 shell changes before starting M-03 edits.
  - Preferred: create a dedicated commit or tag marking the M-02 boundary.
  - Fallback (if commit/tag is blocked by branch policy): record exact changed-file manifest and `git diff --stat` in `/home/zaks/bookkeeping/missions/m03-artifacts/reports/m02-boundary-snapshot.md`.
  - Checkpoint: M-03 can be rolled back independently without losing M-02 shell foundation work.
- P0-01: Run grep inventory for non-502 degradation responses and hardcoded stage arrays.
  - Evidence: `/home/zaks/bookkeeping/missions/m03-artifacts/reports/baseline-contract-scan.md`
  - Checkpoint: list includes every current violation path and line reference.
- P0-02: Confirm Settings duplicate fetch behavior in both dev and production run modes.
  - Evidence: `/home/zaks/bookkeeping/missions/m03-artifacts/reports/settings-fetch-behavior.md`
  - Checkpoint: classify as `StrictMode expected` or `true duplicate request`.

### Decision Tree
- IF duplicate request only appears in dev StrictMode -> document as non-applicable defect and avoid unnecessary code churn.
- ELSE -> implement dedupe fix and verify request count reduction.

### Rollback Plan
1. Keep baseline evidence immutable.
2. Re-run scans if branch drift occurs before Phase 1 edits.

### Gate P0
- M-02 boundary snapshot exists (commit/tag or fallback manifest).
- Baseline scan report exists with violation list.
- Settings fetch behavior classification is documented.

---

## Phase 1 - Route Status and Error Contract Normalization
**Complexity:** M
**Estimated touch points:** 3-8 files

**Purpose:** Enforce JSON 502 semantics for backend-unavailable degradations.

### Blast Radius
- **Services affected:** Next.js API route handlers
- **Pages affected:** Chat, Quarantine preview, any UI consuming degraded route responses
- **Downstream consumers:** Error handling consistency and test assertions

### Tasks
- P1-01: Normalize degraded status codes from 500 to 502 where failure mode is backend unavailable.
  - Priority paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/complete/route.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/execute-proposal/route.ts`
  - Checkpoint: route catch blocks and backend-unavailable responses emit JSON 502 consistently.
- P1-02: Verify existing settings proxy routes retain normalized semantics.
  - Reference:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/preferences/route.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts`
  - Checkpoint: no regression from existing 502 behavior.

### Decision Tree
- IF route failure path represents client validation/auth issue -> keep domain-appropriate status (not forced 502).
- ELSE IF route failure path is backend availability -> must return JSON 502.

### Rollback Plan
1. Revert route-level status changes.
2. Re-run route contract tests and baseline scans.

### Gate P1
- Target routes return JSON 502 for backend-unavailable paths.
- No unintended status regressions for other error classes.

---

## Phase 2 - Convention Alignment (Stages, Counts, Promise Patterns)
**Complexity:** M
**Estimated touch points:** 4-10 files

**Purpose:** Close declared convention drift in stage source, display counts, and resilient fetch patterns.

### Blast Radius
- **Services affected:** Dashboard and deals UI contracts
- **Pages affected:** Dashboard, Deals, New Deal
- **Downstream consumers:** Surface 9 validator + user-visible data semantics

### Tasks
- P2-01: Replace hardcoded stage list in new deal flow with canonical stage source.
  - Path: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/page.tsx`
  - Checkpoint: no local hardcoded stage array remains.
- P2-02: Align user-facing total count labels with server-computed totals where required.
  - Priority paths:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx`
  - Checkpoint: labels representing global totals no longer derive from local subset `.length`.
- P2-03: Verify Promise resiliency compliance on multi-fetch page loads.
  - Checkpoint: all multi-fetch page-level loads use `Promise.allSettled`.
  - Non-app condition: pages with single upstream call may keep single await and must be documented in report.
- P2-04: Apply Settings duplicate fetch fix only if true duplication is confirmed outside StrictMode behavior.
  - Paths may include hooks/components under:
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/useUserPreferences.ts`
    - `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/settings/preferences-api.ts`
  - Checkpoint: redundant network calls reduced without breaking persistence.

### Rollback Plan
1. Revert count and stage-source edits if data semantics drift.
2. Revert optional dedupe changes if they break settings save flow.

### Gate P2
- Hardcoded stage array eliminated from New Deal page.
- Target count labels use intended server totals.
- Multi-fetch pages satisfy `Promise.allSettled` contract.

---

## Phase 3 - Validator Enforcement and Final Verification
**Complexity:** M
**Estimated touch points:** 2-6 files

**Purpose:** Prevent recurrence by extending validator checks and proving clean validation.

### Blast Radius
- **Services affected:** Infra validation scripts and CI gate behavior
- **Pages affected:** None directly (enforcement layer)
- **Downstream consumers:** All future frontend missions

### Tasks
- P3-01: Extend `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` with checks for:
  - Backend-unavailable 500 status regressions in dashboard API routes.
  - Hardcoded stage arrays outside approved source files.
  - Client-side total-count anti-patterns in user-facing labels where applicable.
- P3-02: Run full validation sequence and archive outputs.
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - `bash /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh`
  - Evidence: `/home/zaks/bookkeeping/missions/m03-artifacts/reports/validation.txt`
- P3-03: Produce closure matrix and bookkeeping entry.
  - Evidence: `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md`
  - Bookkeeping: `/home/zaks/bookkeeping/CHANGES.md`

### Rollback Plan
1. Revert validator additions if they generate false positives.
2. Keep route and page fixes; patch validator patterns and rerun.

### Gate P3
- `make validate-local` passes.
- `npx tsc --noEmit` passes.
- `validate-surface9.sh` passes with new checks.

---

## Dependency Graph
Phases execute sequentially: Phase 0 -> Phase 1 -> Phase 2 -> Phase 3.

---

## Acceptance Criteria

### AC-1: Backend-unavailable responses standardized
Target degraded route handlers return JSON 502 instead of 500 for backend-unavailable conditions.

### AC-2: Stage source-of-truth compliance
New Deal stage options originate from `PIPELINE_STAGES`, with no local hardcoded stage list.

### AC-3: Count convention alignment complete
User-facing total labels in targeted surfaces no longer rely on local subset `.length` when total semantics are intended.

### AC-4: Promise resilience compliance verified
All multi-fetch page-level loads conform to `Promise.allSettled` policy or are explicitly documented as non-applicable due to single fetch.

### AC-5: Settings duplicate fetch dispositioned
F-16 duplicate fetch is either fixed (if true duplication) or documented as StrictMode non-issue with evidence.

### AC-6: Validator and baseline checks pass
`make validate-local`, `npx tsc --noEmit`, and `validate-surface9.sh` pass with updated enforcement.

### AC-7: Evidence and bookkeeping complete
M-03 artifacts and `/home/zaks/bookkeeping/CHANGES.md` entry are present.

---

## Guardrails
1. Do not create new product features; this mission is contract alignment only.
2. Do not modify generated contract/codegen outputs directly.
3. Preserve existing success-path response contracts while normalizing degraded paths.
4. Use explicit evidence for any non-applicable determination.
5. Keep fixes scoped to listed paths unless new drift evidence requires expansion.
6. Run validation stack before marking phase complete.
7. B7 anti-convergence does not apply to this mission — standardization is required.
8. Do not treat dev StrictMode-only duplicate fetches as production defects without proof.

---

## Non-Applicability Notes
- IA-1 Context Checkpoint is **not applicable**: scope is 4 phases and expected document size below 500 lines.
- IA-7 Multi-Session Continuity is **not applicable** at current M scope.
- Promise-allSettled conversion is **not applicable** to pages with single data fetch, but these cases must be documented.
- Settings duplicate fetch remediation is **not applicable** if duplication occurs only in React StrictMode development semantics.

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I distinguish backend-unavailable errors from validation/auth errors before changing statuses?
- [ ] Did I classify the Settings duplicate request with dev vs production evidence?

### After each code change
- [ ] Did I preserve route success-path behavior while fixing degraded semantics?
- [ ] Did I avoid introducing feature-level behavior changes?
- [ ] Are stage/count convention fixes aligned with declared source-of-truth rules?

### Before marking COMPLETE
- [ ] Does `make validate-local` pass now?
- [ ] Does `npx tsc --noEmit` pass now?
- [ ] Does `validate-surface9.sh` pass now?
- [ ] Did I update `/home/zaks/bookkeeping/CHANGES.md` and archive evidence?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts` | Phase 1 | 500 -> 502 backend-unavailable alignment |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/complete/route.ts` | Phase 1 | 500 -> 502 backend-unavailable alignment |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/execute-proposal/route.ts` | Phase 1 | 500 -> 502 backend-unavailable alignment |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/new/page.tsx` | Phase 2 | Replace hardcoded stage list with PIPELINE_STAGES |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx` | Phase 2 | Total count convention alignment |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx` | Phase 2 | Total count convention alignment |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` | Phase 3 | Add drift checks and enforce new contract patterns |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 3 | Mission bookkeeping entry |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/missions/m03-artifacts/` | Phase 0 | Artifact root |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/baseline-contract-scan.md` | Phase 0 | Baseline drift inventory |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/settings-fetch-behavior.md` | Phase 0-2 | Duplicate fetch analysis |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/validation.txt` | Phase 3 | Validation transcript |
| `/home/zaks/bookkeeping/missions/m03-artifacts/reports/contract-closure.md` | Phase 3 | Closure matrix |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/findings-catalog.md` | Findings baseline (F-09/F-16 context) |
| `/home/zaks/bookkeeping/missions/m00-artifacts/findings/console-error-catalog.md` | Runtime error evidence |
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260211-160514/FINAL_MASTER.md` | Contract scope and mission sequence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/types/design-system-manifest.ts` | Declared conventions |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/types/execution-contracts.ts` | Stage source-of-truth |

---

## Stop Condition
Stop when AC-1 through AC-7 are satisfied, validation commands pass, and evidence plus bookkeeping are complete. Do not proceed into state-component refactoring or page-specific visual polish in this mission.

---
*End of Mission Prompt - UI-MASTERPLAN-M03*
