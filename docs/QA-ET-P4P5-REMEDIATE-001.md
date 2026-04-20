# MISSION: QA-ET-P4P5-REMEDIATE-001
## QA Remediation: Deal Promotion & Auto-Routing
## Date: 2026-02-15
## Classification: Execution Mission (Remediation)
## Prerequisite: QA-ET-P4P5-VERIFY-001 (Execution)
## Successor: MISSION-ET-P6-EXECUTE-001

## Mission Objective
Fix all failures identified in `QA-ET-P4P5-VERIFY-001`.
This mission focuses on remediating gaps in Deal Promotion (P4) and Auto-Routing (P5) logic, specifically targeting any failures in artifact generation, duplicate prevention, undo logic, or routing behavior.

**Source Material:**
- `QA-ET-P4P5-VERIFY-001` (QA Report - INPUT)

---

## Context
This mission is conditionally executed ONLY if `QA-ET-P4P5-VERIFY-001` reports failures. It enforces the "fix-before-proceeding" discipline.

**Potential Failures to Fix (based on previous QA):**
1.  **Missing Artifacts:** If P4 did not generate all 5 lifecycle records.
2.  **Duplicate Deals:** If P4 allowed duplicate deals for the same thread.
3.  **Routing Gaps:** If P5 auto-routing logic is bypassed or incorrect.
4.  **UI Sync:** If dashboard types do not match backend.

---

## Architectural Constraints
- **Scope Fence:** Only fix what failed in the QA report. Do not refactor unrelated code.
- **Sync Chain:** If backend code changes, run: `make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`.
- **Surface 9:** Maintain design system compliance.

---

## Phases

### Phase 0 — Analysis | Complexity: S
- P0-01: Read QA scorecard.
- P0-02: Identify specific failures.
- Gate P0: Remediation plan clear.

### Phase 1 — Backend Remediation (if needed) | Complexity: M
- P1-01: Fix promotion logic (P4).
- P1-02: Fix routing logic (P5).
- P1-03: Fix undo logic.
- Gate P1: Unit tests pass.

### Phase 2 — Dashboard Remediation (if needed) | Complexity: M
- P2-01: Fix deal source indicator.
- P2-02: Fix conflict resolution UI.
- P2-03: Fix thread management UI.
- Gate P2: UI renders correctly.

### Phase 3 — Verification | Complexity: S
- P3-01: Re-run all failed QA gates.
- P3-02: Run sync chain.
- P3-03: Run `make validate-local`.
- Gate P3: All regressions fixed.

---

## Acceptance Criteria
### AC-1: QA Gates Pass
All gates that failed in `QA-ET-P4P5-VERIFY-001` now pass.

### AC-2: Sync Chain Verified
`make sync-types` and `npx tsc` pass if API changed.

---

## Files Reference

### Files to Modify (Potential)
| File | Reason |
|------|--------|
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Promotion/Routing logic fixes |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | UI fixes |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | Type fixes |

---

## Guardrails
1. **Targeted Fixes Only.** No refactoring.
2. **Mandatory Sync.** Run sync chain if API touched.

## Stop Condition
Stop when all gates in `QA-ET-P4P5-VERIFY-001` pass.

---
*End of Mission Prompt — QA-ET-P4P5-REMEDIATE-001*
