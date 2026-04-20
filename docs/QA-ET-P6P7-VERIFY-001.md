# MISSION: QA-ET-P6P7-VERIFY-001
## QA Verification: Collaboration & Security Hardening
## Date: 2026-02-15
## Classification: QA Verification (read-only audit + evidence collection)
## Prerequisite: MISSION-ET-VALIDATION-001 (P6 + P7 executed)
## Successor: QA-ET-P6P7-REMEDIATE-001

## Mission Objective
Independent verification of Email Triage Phases 6 (Collaboration Contract) and 7 (Security & Hardening).
Verify that the delegated task system is fully operational with state machine enforcement, bridge tools work, dual-layer authentication is active, log redaction is effective, and key rotation procedures are executable.
This mission also re-verifies remediation of previous QA failures (VF-07.x, VF-08.3, ST-1).

**Source Missions:**
- `MISSION-ET-VALIDATION-001` (Phases 6 & 7)

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/PF-1-validate-local.txt
```
**PASS if:** exit 0.

### PF-2: Checkpoint Verification
```bash
grep -E "P6 — Collaboration.*COMPLETE|P7 — Security.*COMPLETE" /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/PF-2-checkpoint.txt
```
**PASS if:** P6 and P7 marked COMPLETE.

---

## Verification Families

## Verification Family 01 — Phase 6: Collaboration Contract (G6 Gates)

### VF-01.1: Delegated Schema (G6-01)
*Verify table structure and state machine constraint.*
```bash
psql -d zakops -c "\d zakops.delegated_tasks" | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-01.1-schema.txt
```
**PASS if:** Columns `status`, `task_type`, `payload` exist, and check constraint enforces 6 states.

### VF-01.2: Delegation API & Flags (G6-02, G6-03, G6-04, G6-05)
*Verify API logic exists and flags are checked.*
```bash
grep -E "delegate_actions|send_email_enabled|requires_confirmation" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-01.2-api-flags.txt
```
**PASS if:** Feature flags are checked in endpoint logic.

### VF-01.3: Bridge Tools (G6-09)
*Verify tool registration in bridge.*
```bash
grep -E "zakops_get_deal_status|zakops_list_recent_events|zakops_report_task_result" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-01.3-bridge-tools.txt
```
**PASS if:** Tools are registered and implemented.

### VF-01.4: Dashboard UI (G6-07, G6-08)
*Verify task management UI.*
```bash
grep -E "Tasks|Dead Letter|Retry|Confirm" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-01.4-dashboard.txt
```
**PASS if:** UI elements for task management are present.

**Gate VF-01:** Collaboration contract verified.

## Verification Family 02 — Phase 7: Security & Hardening (G7 Gates)

### VF-02.1: Dual-Layer Auth (G7-01, G7-02)
*Verify auth middleware checks both layers.*
```bash
grep -E "CF_ACCESS_REQUIRED|Cf-Access-Jwt-Assertion|Authorization" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-02.1-auth-logic.txt
```
**PASS if:** Logic checks for CF header (if required) AND Bearer token.

### VF-02.2: Key Rotation (G7-03)
*Verify dual-token logic and runbook existence.*
```bash
grep "ZAKOPS_BRIDGE_API_KEY_SECONDARY" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-02.2-rotation-code.txt
ls -l /home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-02.2-runbook.txt
```
**PASS if:** Secondary key check exists and runbook is present.

### VF-02.3: Log Redaction (G7-04)
*Verify redaction utility usage.*
```bash
grep "_redact_params" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-02.3-redaction.txt
```
**PASS if:** Redaction function is applied to logs.

### VF-02.4: Retention & Purge (G7-05)
*Verify purge endpoint and policy doc.*
```bash
grep "/api/admin/quarantine/purge" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-02.4-purge-endpoint.txt
ls -l /home/zaks/bookkeeping/docs/DATA-RETENTION-POLICY.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/VF-02.4-policy-doc.txt
```
**PASS if:** Endpoint defined and policy doc exists.

**Gate VF-02:** Security hardening verified.

---

## Cross-Consistency Checks

### XC-1: Sync Chain Verification
```bash
cd /home/zaks/zakops-agent-api && npx tsc --noEmit | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/XC-1-tsc.txt
```
**PASS if:** No errors.

### XC-2: Migration 035 Existence (VF-07.1 Remediation)
```bash
ls /home/zaks/zakops-backend/db/migrations/035_delegated_tasks.sql | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/XC-2-migration.txt
```
**PASS if:** File exists.

---

## Stress Tests

### ST-1: Auth Matrix
*Test auth rejection behavior (mocked requests).*
```bash
# This uses a script to curl local bridge with various header combos
# Assuming bridge is running on localhost:9100 or testable via unit test
# Fallback: static analysis of 401/403 responses
grep -E "401|403" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/ST-1-auth-responses.txt
```
**PASS if:** Code explicitly returns 401/403 for missing auth.

### ST-2: Kill Switch Latency (Remediates ST-1)
*Verify cache TTL config.*
```bash
grep "ttl=" /home/zaks/zakops-backend/src/core/feature_flags.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P6P7-VERIFY-001/evidence/ST-2-cache-ttl.txt
```
**PASS if:** TTL is 1 (or bypass=True).

---

## Remediation Protocol

1. **MISSING_FILE**: If VF-01.1 fails, check migrations.
2. **LOGIC_GAP**: If VF-02.1 fails, verify middleware chain.
3. **UI_MISSING**: If VF-01.4 fails, check dashboard build.
4. **TYPE_ERROR**: If XC-1 fails, re-run `make sync-types`.

---

## Enhancement Opportunities

### ENH-1: Log Volume Monitoring
Consider adding metrics for log volume to detect if redaction overhead is significant.

---

## Scorecard Template

QA-ET-P6P7-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]

Verification Gates:
  VF-01 (Phase 6 Collab):   __ / 4 checks PASS
  VF-02 (Phase 7 Security): __ / 4 checks PASS

Cross-Consistency:
  XC-1 (Types):     [ PASS / FAIL ]
  XC-2 (Migration): [ PASS / FAIL ]

Stress Tests:
  ST-1 (Auth):       [ PASS / FAIL ]
  ST-2 (KillSwitch): [ PASS / FAIL ]

Total: __ / 10 gates PASS

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]

---

## Guardrails
1. **No Code Changes.** Verification only.
2. **Evidence-based.** All PASS must have `tee` evidence.
3. **Path Safety.** Use canonical paths.

## Stop Condition
Stop when all gates pass, proving P6+P7 completion and remediation of previous QA failures.

---
*End of Mission Prompt — QA-ET-P6P7-VERIFY-001*
