# MISSION: QA-ET-P8-VERIFY-001
## QA Verification: Operational Excellence & Final Acceptance
## Date: 2026-02-15
## Classification: QA Verification (read-only audit + evidence collection)
## Prerequisite: MISSION-ET-VALIDATION-001 (P8 executed)
## Successor: QA-ET-P8-REMEDIATE-001

## Mission Objective
Independent verification of Email Triage Phase 8 (Operational Excellence) and the Final Mission-Wide Acceptance Gate.
Verify that production readiness artifacts (SLOs, alerts, load tests, backup drills, shadow measurement) are complete and operational.
Perform a full audit of all 16 Acceptance Criteria (AC-1 through AC-16) to certify the entire ET-VALIDATION-001 mission for completion.
Re-verify remediation of migration drift (ST-4).

**Source Missions:**
- `MISSION-ET-VALIDATION-001` (Phase 8)

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/PF-1-validate-local.txt
```
**PASS if:** exit 0.

### PF-2: Checkpoint Verification
```bash
grep "P8 — Operational Excellence.*COMPLETE" /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/PF-2-checkpoint.txt
```
**PASS if:** P8 marked COMPLETE.

---

## Verification Families

## Verification Family 01 — Phase 8: Operational Excellence (G8 Gates)

### VF-01.1: SLOs & Alerting (G8-01, G8-02)
*Verify documentation and health probe script exist.*
```bash
ls -l /home/zaks/bookkeeping/docs/EMAIL-TRIAGE-SLO.md /home/zaks/bookkeeping/docs/EMAIL-TRIAGE-ALERTING.md /home/zaks/bookkeeping/scripts/email_triage_health_probe.sh | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-01.1-ops-docs.txt
```
**PASS if:** All 3 files exist.

### VF-01.2: Load Test (G8-03)
*Verify load test script exists.*
```bash
ls -l /home/zaks/zakops-backend/tests/load/test_email_triage_load.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-01.2-load-test.txt
```
**PASS if:** File exists.

### VF-01.3: Backup Drill (G8-04)
*Verify backup drill script exists.*
```bash
ls -l /home/zaks/bookkeeping/scripts/backup_restore_drill.sh | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-01.3-backup-drill.txt
```
**PASS if:** File exists.

### VF-01.4: Shadow Measurement (G8-05, G8-06)
*Verify measurement script and production safety flags.*
```bash
ls -l /home/zaks/bookkeeping/scripts/shadow_measurement.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-01.4-shadow-script.txt
# Check flags in migration or seed data logic (read-only)
grep -E "shadow_mode.*true|auto_route.*false|delegate_actions.*false|send_email_enabled.*false" /home/zaks/zakops-backend/db/migrations/032_feature_flags.sql | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-01.4-flags.txt
```
**PASS if:** Script exists and default flag values match safe production state.

## Verification Family 02 — Mission Acceptance (AC-1 through AC-16)

### VF-02.1: Ingestion & Schema (AC-1, AC-2, AC-9, AC-14)
*Verify subject rendering, snippet population, schema validation, and source types.*
```bash
# Check code for COALESCE subject logic
grep "COALESCE(email_subject, subject)" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.1-subject.txt
# Check code for snippet truncation
grep "email_body_snippet" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.1-snippet.txt
# Check code for extra='forbid'
grep "extra='forbid'" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.1-schema.txt
```
**PASS if:** Logic present for all checks.

### VF-02.2: Lifecycle & Promotion (AC-3, AC-5, AC-10, AC-13)
*Verify artifacts, locking, dedup, and correlation.*
```bash
# Check transaction wrapper for artifacts
grep "async with.*transaction" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.2-transaction.txt
# Check optimistic locking (409)
grep "HTTPException.*409" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.2-locking.txt
# Check correlation ID propagation
grep "correlation_id" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.2-correlation.txt
```
**PASS if:** Patterns confirmed in codebase.

### VF-02.3: UX & Safety (AC-4, AC-6, AC-7, AC-8, AC-11, AC-12)
*Verify reject reason, kill switch, auth, and UI fields.*
```bash
# Reject reason
grep "reject_reason" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.3-reject.txt
# Kill switch
grep "email_triage_writes_enabled" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.3-killswitch.txt
# Auth
grep "BearerAuthMiddleware" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.3-auth.txt
# UI Fields
grep -E "triage_summary|extraction_evidence|field_confidences" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.3-ui-fields.txt
```
**PASS if:** All safety and UI elements found.

### VF-02.4: Regression & Bookkeeping (AC-15, AC-16)
*Verify CHANGELOG and surfaces.*
```bash
grep "Phase 8 Complete" /home/zaks/bookkeeping/CHANGES.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.4-changelog.txt
cd /home/zaks/zakops-agent-api && make validate-surface13 && make validate-surface14 | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/VF-02.4-surfaces.txt
```
**PASS if:** Changelog updated and validation passes.

---

## Cross-Consistency Checks

### XC-1: Sync Chain Final Verification
```bash
cd /home/zaks/zakops-agent-api && make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/XC-1-final-sync.txt
```
**PASS if:** All commands exit 0.

### XC-2: Migration Continuity (Remediates ST-4)
```bash
ls -1 /home/zaks/zakops-backend/db/migrations/ | grep -E "033|034|035" | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/XC-2-migrations.txt
```
**PASS if:** 033, 034, and 035 exist.

---

## Stress Tests

### ST-1: Load Test Profile Integrity
*Read-only check of load test assertions.*
```bash
grep "assert.*p95" /home/zaks/zakops-backend/tests/load/test_email_triage_load.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P8-VERIFY-001/evidence/ST-1-load-assertions.txt
```
**PASS if:** SLO assertions (p95 latency) found in script.

---

## Remediation Protocol

1. **MISSING_ARTIFACT**: If ops docs missing, create them.
2. **LOGIC_GAP**: If AC checks fail, trace back to Phase 1-7 implementation.
3. **TYPE_ERROR**: If XC-1 fails, investigate type drift.

---

## Enhancement Opportunities

### ENH-1: Automated Load Tests in CI
Add load test to CI pipeline (Gate H) if lightweight enough.

---

## Scorecard Template

QA-ET-P8-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]

Verification Gates:
  VF-01 (Phase 8 Ops):      __ / 4 checks PASS
  VF-02 (Acceptance AC):    __ / 4 checks PASS

Cross-Consistency:
  XC-1 (Sync):       [ PASS / FAIL ]
  XC-2 (Migrations): [ PASS / FAIL ]

Stress Tests:
  ST-1 (Load Assert): [ PASS / FAIL ]

Total: __ / 9 gates PASS

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]

---

## Guardrails
1. **No Code Changes.** Verification only.
2. **Evidence-based.** All PASS must have `tee` evidence.
3. **Path Safety.** Use canonical paths.

## Stop Condition
Stop when all G8 gates and AC-1..16 are verified PASS.

---
*End of Mission Prompt — QA-ET-P8-VERIFY-001*
