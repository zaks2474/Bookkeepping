# MISSION: QA-ET-P8-REMEDIATE-001
## QA Remediation: Operational Excellence & Final Acceptance
## Date: 2026-02-15
## Classification: Execution Mission (Remediation)
## Prerequisite: QA-ET-P8-VERIFY-001 (Execution)
## Successor: MISSION-COMPLETE (Roadmap Delivered)

## Mission Objective
Fix all failures identified in `QA-ET-P8-VERIFY-001`.
This mission is the final remediation step for the Email Triage Validation Roadmap. It must resolve any gaps in Operational Excellence (P8) or the Mission-Wide Acceptance Criteria (AC-1 through AC-16).

**Source Material:**
- `QA-ET-P8-VERIFY-001` (QA Report - INPUT)

---

## Context
This mission is conditionally executed ONLY if `QA-ET-P8-VERIFY-001` reports failures. It enforces the "fix-before-finish" discipline.

**Potential Failures to Fix:**
1.  **Missing Ops Artifacts:** If SLOs, alerts, or scripts are missing.
2.  **AC Failures:** If any of the 16 acceptance criteria (AC-1..AC-16) failed verification.
3.  **Migration Drift:** If 034/035 are still missing (unlikely, but critical).
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

## Phase 1 - Operational Remediation (if needed)
**Complexity:** S
**Estimated touch points:** 1-3 files

**Purpose:** Fix missing P8 artifacts.

### Blast Radius
- **Services affected:** None (docs/scripts)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P1-01: Create/fix SLO docs.
- P1-02: Create/fix load/backup scripts.

### Gate P1
- Files exist and are valid.

## Phase 2 - Acceptance Remediation (if needed)
**Complexity:** M
**Estimated touch points:** 2-6 files

**Purpose:** Fix any functional gaps in AC-1 through AC-16.

### Blast Radius
- **Services affected:** Backend/Dashboard
- **Pages affected:** Quarantine/Deals
- **Downstream consumers:** N/A

### Tasks
- P2-01: Fix backend logic gaps (AC-1..10, 13).
- P2-02: Fix UI rendering gaps (AC-11, 12, 14).

### Gate P2
- Feature logic verified.

## Phase 3 - Final Verification
**Complexity:** S
**Estimated touch points:** 0 files (verification only)

**Purpose:** Verify mission completion.

### Blast Radius
- **Services affected:** All
- **Pages affected:** All
- **Downstream consumers:** N/A

### Tasks
- P3-01: Re-run all failed QA gates.
- P3-02: Run sync chain (FINAL).
- P3-03: Run `make validate-local` (FINAL).

### Gate P3
- All gates PASS.

---

## Acceptance Criteria
### AC-1: QA Gates Pass
All gates that failed in `QA-ET-P8-VERIFY-001` now pass.

### AC-2: Mission Complete
Full validation roadmap (P0-P8) is verifiable.

---

## Files Reference

### Files to Modify (Potential)
| File | Reason |
|------|--------|
| `/home/zaks/bookkeeping/docs/EMAIL-TRIAGE-SLO.md` | Doc fix |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Logic fix |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | UI fix |

---

## Guardrails
1. **Targeted Fixes Only.** No refactoring.
2. **Mandatory Sync.** Run sync chain if API touched.

## Stop Condition
Stop when all gates in `QA-ET-P8-VERIFY-001` pass.

---
*End of Mission Prompt — QA-ET-P8-REMEDIATE-001*
