# MISSION: QA-ET-P6P7-REMEDIATE-001
## QA Remediation: Collaboration & Security
## Date: 2026-02-15
## Classification: Execution Mission (Remediation)
## Prerequisite: QA-ET-P6P7-VERIFY-001 (Execution)
## Successor: MISSION-ET-P8-EXECUTE-001 (Operational Excellence)

## Mission Objective
Fix all failures identified in `QA-ET-P6P7-VERIFY-001`.
This mission focuses on remediating gaps in Collaboration (P6) and Security (P7) logic, specifically targeting any failures in delegation state machine, auth layers, log redaction, or key rotation.

**Source Material:**
- `QA-ET-P6P7-VERIFY-001` (QA Report - INPUT)

---

## Context
This mission is conditionally executed ONLY if `QA-ET-P6P7-VERIFY-001` reports failures. It enforces the "fix-before-proceeding" discipline.

**Current Status:**
`QA-ET-P6P7-VERIFY-001` scorecard is pending. Remediation will commence upon confirmation of failures.

**Potential Failures to Fix (based on previous QA):**
1.  **Missing Migration:** If 035 is still absent.
2.  **Auth Gaps:** If Layer 1/2 checks are incomplete.
3.  **Logging Leaks:** If redaction is not applied to all sensitive paths.
4.  **UI Sync:** If dashboard types do not match backend.

---

## Architectural Constraints
- **Scope Fence:** Only fix what failed in the QA report. Do not refactor unrelated code.
- **Sync Chain:** If backend code changes, run: `make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`.
- **Surface 9:** Maintain design system compliance.

---

## Phase 0 - Analysis
**Complexity:** S
**Estimated touch points:** 0 files (read-only)

**Purpose:** Identify specific failures from QA report.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: Read QA scorecard.
- P0-02: Identify specific failures.

### Gate P0
- Remediation plan clear.

## Phase 1 - Backend Remediation (if needed)
**Complexity:** M
**Estimated touch points:** 2-4 files

**Purpose:** Fix backend logic gaps.

### Blast Radius
- **Services affected:** Backend API
- **Pages affected:** N/A
- **Downstream consumers:** N/A

### Tasks
- P1-01: Fix delegation logic (P6).
- P1-02: Fix auth middleware (P7).
- P1-03: Fix purge logic.

### Gate P1
- Unit tests pass.

## Phase 2 - Dashboard Remediation (if needed)
**Complexity:** M
**Estimated touch points:** 2-4 files

**Purpose:** Fix UI gaps.

### Blast Radius
- **Services affected:** Dashboard
- **Pages affected:** Deal Detail, Task List
- **Downstream consumers:** N/A

### Tasks
- P2-01: Fix task list UI.
- P2-02: Fix retry/confirm actions.

### Gate P2
- UI renders correctly.

## Phase 3 - Verification
**Complexity:** S
**Estimated touch points:** 0 files (verification only)

**Purpose:** Verify fixes.

### Blast Radius
- **Services affected:** All
- **Pages affected:** All
- **Downstream consumers:** N/A

### Tasks
- P3-01: Re-run all failed QA gates.
- P3-02: Run sync chain.
- P3-03: Run `make validate-local`.

### Gate P3
- All regressions fixed.

---

## Acceptance Criteria
### AC-1: QA Gates Pass
All gates that failed in `QA-ET-P6P7-VERIFY-001` now pass.

### AC-2: Sync Chain Verified
`make sync-types` and `npx tsc` pass if API changed.

---

## Files Reference

### Files to Modify (Potential)
| File | Reason |
|------|--------|
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Delegation logic fixes |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` | Auth/Redaction fixes |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | Type fixes |

---

## Guardrails
1. **Targeted Fixes Only.** No refactoring.
2. **Mandatory Sync.** Run sync chain if API touched.

## Stop Condition
Stop when all gates in `QA-ET-P6P7-VERIFY-001` pass.

---
*End of Mission Prompt — QA-ET-P6P7-REMEDIATE-001*
