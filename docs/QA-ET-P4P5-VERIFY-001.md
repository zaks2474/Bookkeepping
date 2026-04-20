# MISSION: QA-ET-P4P5-VERIFY-001
## QA Verification: Deal Promotion & Auto-Routing
## Date: 2026-02-15
## Classification: QA Verification (read-only audit + evidence collection)
## Prerequisite: MISSION-ET-VALIDATION-001 (P4 + P5 executed)
## Successor: QA-ET-P4P5-REMEDIATE-001

## Mission Objective
Independent verification of Email Triage Phases 4 (Deal Promotion) and 5 (Auto-Routing).
Verify that quarantine items can be promoted to deals with full lifecycle artifacts, duplicate prevention works, undo capabilities function, and thread-aware auto-routing behaves correctly under all flag conditions.
This mission also re-verifies remediation of previous QA failures (VF-05.x, VF-06.x).

**Source Missions:**
- `MISSION-ET-VALIDATION-001` (Phases 4 & 5)

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/PF-1-validate-local.txt
```
**PASS if:** exit 0.

### PF-2: Checkpoint Verification
```bash
grep "P4 — Deal Promotion.*COMPLETE" /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/PF-2-checkpoint.txt
```
**PASS if:** P4 and P5 marked COMPLETE.

---

## Verification Families

## Verification Family 01 — Phase 4: Deal Promotion (G4 Gates)

### VF-01.1: Lifecycle Artifacts (G4-01, G4-02, G4-05)
*Verify one recent promotion produced all 5 artifacts.*
```bash
# Get a recently promoted deal ID
DEAL_ID=$(psql -d zakops -t -c "SELECT deal_id FROM zakops.deals WHERE identifiers->>'quarantine_item_id' IS NOT NULL ORDER BY created_at DESC LIMIT 1" | xargs)
echo "Checking artifacts for deal: $DEAL_ID" > /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.1-artifacts.txt

# 1. Deal record
psql -d zakops -c "SELECT deal_id, canonical_name, identifiers FROM zakops.deals WHERE deal_id = '$DEAL_ID'" >> /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.1-artifacts.txt

# 2. Transitions
psql -d zakops -c "SELECT * FROM zakops.deal_transitions WHERE deal_id = '$DEAL_ID'" >> /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.1-artifacts.txt

# 3. Events
psql -d zakops -c "SELECT * FROM zakops.deal_events WHERE deal_id = '$DEAL_ID'" >> /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.1-artifacts.txt

# 4. Outbox
psql -d zakops -c "SELECT * FROM zakops.outbox WHERE aggregate_id = '$DEAL_ID'" >> /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.1-artifacts.txt

# 5. Quarantine status
Q_ID=$(psql -d zakops -t -c "SELECT identifiers->>'quarantine_item_id' FROM zakops.deals WHERE deal_id = '$DEAL_ID'" | xargs)
psql -d zakops -c "SELECT id, status, deal_id FROM zakops.quarantine_items WHERE id = '$Q_ID'" >> /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.1-artifacts.txt
```
**PASS if:** All 5 query blocks return data for the same deal.

### VF-01.2: Duplicate Prevention (G4-03, G4-06)
*Verify source_thread_id maps to existing deal.*
```bash
psql -d zakops -c "SELECT * FROM zakops.email_threads LIMIT 5" | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.2-threads.txt
```
**PASS if:** Rows exist linking `thread_id` to `deal_id`.

### VF-01.3: Undo Approval Logic (G4-07)
*Verify undo endpoint code exists (read-only verification).*
```bash
grep -r "undo-approve" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.3-undo-code.txt
```
**PASS if:** Endpoint definition found.

### VF-01.4: Deal Source Indicator (G4-08)
*Verify UI badge logic exists.*
```bash
grep -r "From Email Triage" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-01.4-source-indicator.txt
```
**PASS if:** Badge text found in UI code.

**Gate VF-01:** Deal promotion pipeline verified.

## Verification Family 02 — Phase 5: Auto-Routing (G5 Gates)

### VF-02.1: Auto-Routing Logic (G5-01..G5-04)
*Verify backend routing logic.*
```bash
grep -E "auto_route.*feature_flags" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-02.1-routing-logic.txt
```
**PASS if:** Feature flag check found in ingestion path.

### VF-02.2: Routing Reason (G5-05)
*Verify DB stores routing reason.*
```bash
psql -d zakops -c "SELECT id, status, raw_content->>'routing_reason' as reason FROM zakops.quarantine_items WHERE raw_content->>'routing_reason' IS NOT NULL LIMIT 5" | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-02.2-routing-reason.txt
```
**PASS if:** Rows returned with reasons (e.g., `auto_route_off`, `no_thread_match`).

### VF-02.3: Conflict Resolution UI (G5-06)
*Verify conflict banner in UI.*
```bash
grep "routing_conflict" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-02.3-conflict-ui.txt
```
**PASS if:** Handling for `routing_conflict` found.

### VF-02.4: Thread Management (G5-07)
*Verify thread management endpoints.*
```bash
grep "/api/deals/{deal_id}/threads" /home/zaks/zakops-backend/src/api/orchestration/main.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/VF-02.4-thread-endpoints.txt
```
**PASS if:** GET/POST/DELETE endpoints found.

**Gate VF-02:** Auto-routing verified.

---

## Cross-Consistency Checks

### XC-1: Sync Chain Verification
```bash
cd /home/zaks/zakops-agent-api && npx tsc --noEmit | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/XC-1-tsc.txt
```
**PASS if:** No errors.

### XC-2: API Contract
```bash
grep "routing_reason" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/XC-2-api-contract.txt
```
**PASS if:** Frontend type definition matches backend.

---

## Stress Tests

### ST-1: Concurrent Approve Race
*Simulate concurrent approval of same item to test optimistic locking.*
```bash
# This requires a dedicated script. We check if the script exists first.
ls /home/zaks/zakops-backend/tests/stress/test_quarantine_locking.py | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/ST-1-script-check.txt
# If exists, run it (read-only mode if possible, or dry-run)
# Note: Actual stress test modifies DB, so we verify the locking mechanism code instead for read-only QA.
grep "version" /home/zaks/zakops-backend/src/api/orchestration/main.py | grep "409" | tee /home/zaks/bookkeeping/qa-verifications/QA-ET-P4P5-VERIFY-001/evidence/ST-1-locking-code.txt
```
**PASS if:** 409 Conflict logic found for version mismatch.

---

## Remediation Protocol

1. **MISSING_ARTIFACT**: If VF-01.1 fails, trace backend logs for insertion errors.
2. **LOGIC_GAP**: If VF-02.1 fails, verify feature flag implementation.
3. **UI_MISSING**: If VF-02.3 fails, check dashboard build.
4. **TYPE_ERROR**: If XC-1 fails, re-run `make sync-types`.

---

## Enhancement Opportunities

### ENH-1: Metric Observability
Add counters for routing decisions (routed vs quarantined).

---

## Scorecard Template

QA-ET-P4P5-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]

Verification Gates:
  VF-01 (Phase 4 Promotion): __ / 4 checks PASS
  VF-02 (Phase 5 Routing):   __ / 4 checks PASS

Cross-Consistency:
  XC-1 (Types): [ PASS / FAIL ]
  XC-2 (API):   [ PASS / FAIL ]

Stress Tests:
  ST-1 (Locking): [ PASS / FAIL ]

Total: __ / 9 gates PASS

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]

---

## Guardrails
1. **No Code Changes.** Verification only.
2. **Evidence-based.** All PASS must have `tee` evidence.
3. **Path Safety.** Use canonical paths.

## Stop Condition
Stop when all gates pass, proving P4+P5 completion and remediation of previous QA failures.

---
*End of Mission Prompt — QA-ET-P4P5-VERIFY-001*
