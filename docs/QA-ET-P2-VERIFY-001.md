# MISSION: QA-ET-P2-VERIFY-001
## QA Verification: Email Triage Phase 2 (Schema + UX)
## Date: 2026-02-15
## Classification: QA Verification & Remediation
## Prerequisite: ET-P2-EXECUTE-001 (Execution)
## Successor: MISSION-ET-P4-EXECUTE-001

## Mission Objective
Independent verification of **Mission ET-P2-EXECUTE-001**.
Verify that the canonical schema expansion (P1), quarantine UX overhaul (P2), and agent config specs (P3) are correctly implemented and operational.
This mission specifically targets the remediation of failures from `QA-ET-VALIDATION-VERIFY-001`.

**Source Missions:**
- `ET-P2-EXECUTE-001`

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/PF-1-validate-local.txt
```
**PASS if:** exit 0.

### PF-2: Migration Check
```bash
ls /home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2.sql /home/zaks/zakops-backend/db/migrations/034_quarantine_escalate.sql | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/PF-2-migrations.txt
```
**PASS if:** Both files exist.

---

## Verification Families

## Verification Family 01 — Phase 1: Canonical Schema & Bridge (G1 Gates)

### VF-01.1: DB Schema Columns (G1-01, G1-02)
```bash
psql -d zakops -c "\d zakops.quarantine_items" | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-01.1-schema.txt
```
**PASS if:** Output contains `email_body_snippet`, `triage_summary`, `confidence`, `received_at`, `sender_name`, `version`.

### VF-01.2: Bridge Tool Contract (G1-03)
```bash
grep -E "email_body_snippet|triage_summary|confidence" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-01.2-bridge-code.txt
```
**PASS if:** New fields are present in the tool definition/validation logic.

### VF-01.3: Golden Payload Injection (G1-09)
*Executes the golden payload test script created in P1.*
```bash
python3 /home/zaks/zakops-agent-api/apps/agent-api/scripts/test_golden_injection.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-01.3-golden-test.txt
```
**PASS if:** Script exits 0 and reports success.

**Gate VF-01:** Schema and Bridge contract verified.

## Verification Family 02 — Phase 2: Quarantine UX (G2 Gates)

### VF-02.1: UI Field Presence (Remediates VF-03.1)
```bash
grep -rE "sender_name|confidence|triage_summary" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-02.1-ui-fields.txt
```
**PASS if:** Matches found in page components.

### VF-02.2: Optimistic Locking Logic (Remediates VF-03.2)
```bash
grep "ETag" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-02.2-optimistic-locking-fe.txt
grep "version" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-02.2-optimistic-locking-be.txt
```
**PASS if:** Frontend sends version/ETag, Backend checks it.

### VF-02.3: Kill Switch TTL (Remediates VF-01.2)
```bash
grep -E "ttl=1|bypass_cache=True" /home/zaks/zakops-backend/src/core/feature_flags.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-02.3-kill-switch-ttl.txt
```
**PASS if:** Cache TTL is <= 1s or bypass is implemented for writes.

### VF-02.4: Surface 9 Logging (Remediates VF-03.4)
```bash
grep "console.warn" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-02.4-s9-logging.txt
```
**PASS if:** Found handling API errors/degradation.

**Gate VF-02:** UX Operationalization verified.

## Verification Family 03 — Phase 3: Agent Config (G3 Gates)

### VF-03.1: Spec Artifacts (Remediates VF-04.1)
```bash
ls -l /home/zaks/bookkeeping/docs/LANGSMITH_AGENT_CONFIG_SPEC.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/VF-03.1-spec-file.txt
```
**PASS if:** File exists.

**Gate VF-03:** Config specs verified.

---

## Cross-Consistency Checks

### XC-1: Sync Chain Verification
```bash
cd /home/zaks/zakops-agent-api && npx tsc --noEmit | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/XC-1-tsc.txt
```
**PASS if:** No errors (proving `make sync-types` was run and consumed correctly).

### XC-2: Checkpoint Consistency
```bash
cat /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/XC-2-checkpoint.txt
```
**PASS if:** Checkpoint reflects P1/P2/P3 completion.

---

## Stress Tests

### ST-1: Optimistic Locking Concurrency (Remediates ST-2)
*Runs a script attempting concurrent updates to the same quarantine item.*
```bash
python3 /home/zaks/zakops-backend/tests/stress/test_quarantine_locking.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P2-VERIFY-001/evidence/ST-1-locking.txt
```
**PASS if:** One succeeds, one fails with 409 Conflict.

---

## Remediation Protocol

1. **SCHEMA_MISMATCH**: If VF-01.1 fails, re-run Migration 033.
2. **UI_MISSING**: If VF-02.1 fails, re-run P2 UI tasks.
3. **LOCKING_FAIL**: If ST-1 fails, fix backend version check logic.
4. **TYPE_ERROR**: If XC-1 fails, re-run `make sync-types`.

---

## Enhancement Opportunities

### ENH-1: Batch Operations
Add bulk approve/reject with per-item validation and partial success reporting.

---

## Scorecard Template

QA-ET-P2-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]

Verification Gates:
  VF-01 (Phase 1 Schema): __ / 3 checks PASS
  VF-02 (Phase 2 UX):     __ / 4 checks PASS
  VF-03 (Phase 3 Spec):   __ / 1 checks PASS

Cross-Consistency:
  XC-1 (Types): [ PASS / FAIL ]
  XC-2 (Docs):  [ PASS / FAIL ]

Stress Tests:
  ST-1 (Locking): [ PASS / FAIL ]

Total: __ / 8 gates PASS

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]

---

## Guardrails
1. **No Code Changes.** Verification only.
2. **Evidence-based.** All PASS must have `tee` evidence.
3. **Path Safety.** Use canonical bridge paths.

## Stop Condition
Stop when all gates pass, proving P1+P2+P3 completion and remediation of previous QA failures.

---
*End of Mission Prompt — QA-ET-P2-VERIFY-001*
