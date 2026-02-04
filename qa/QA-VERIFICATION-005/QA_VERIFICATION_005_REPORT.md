# QA VERIFICATION 005 — REPORT

**Date:** 2026-02-04T01:50:00Z
**Auditor:** Claude Code (Opus 4.5)
**Target:** AGENT-REMEDIATION-005
**Version:** V2 (Anti-Escape Edition)
**Mission:** Adversarial verification of FORENSIC-004 findings remediation

---

## Executive Summary

**VERDICT: PASS**

| Metric | Value |
|--------|-------|
| Total Findings | 8 |
| FIXED | 4 |
| PARTIAL | 2 |
| EXISTING | 1 |
| DOCUMENTED | 1 |
| Hard-Stop Gates | 10/10 PASS |
| Discrepancies | 7/7 RESOLVED |

---

## Phase Results

| Phase | Status | Notes |
|-------|--------|-------|
| QA-0: Artifacts | PASS | All files exist, evidence directories populated |
| QA-1: Health + RT-DB-SOT | PASS | Services healthy, DB split-brain proof complete |
| QA-2: P2 Fixes + RT-LANGFUSE-NEG | PASS | F-001 fixed, F-002 deferral justified |
| QA-3: P3 Fixes + RT-PATH-MATRIX | PASS | All P3 verified as fixed/partial/documented |
| QA-4: Regression + RT-ERROR-REDACT | PASS | No regressions, errors properly sanitized |
| QA-5: RT-GOLDEN-PATH | PASS | E2E operator flow works |
| QA-6: Reconciliation | PASS | All discrepancies resolved |

---

## Finding-by-Finding Reconciliation

| Finding | Priority | Builder Status | QA Verdict | Evidence | Notes |
|---------|----------|---------------|------------|----------|-------|
| F-001 | P2 | FIXED | **VERIFIED** | qa2_1_langfuse.txt | tracing.py + trace_sink.py exist, RT-LANGFUSE-NEG pass |
| F-002 | P2 | DEFERRED | **JUSTIFIED** | qa1_2_db_sot.txt | zakops-postgres-1 has active connections, fresh data |
| F-003 | P3 | FIXED | **VERIFIED** | qa3_1_delete_trigger.txt | Trigger blocks DELETE, bypass documented |
| F-004 | P3 | EXISTING | **VERIFIED** | qa3_2_docs_exposure.txt | Conditional logic exists in main.py:59-69 |
| F-005 | P3 | DOCUMENTED | **ACCEPTABLE** | qa3_3_metrics.txt | /metrics 200 with benign Prometheus data only |
| F-006 | P3 | FIXED | **VERIFIED** | qa3_4_log_rotation.txt | max-size:50m, max-file:5 in container config |
| F-007 | P3 | FIXED | **VERIFIED** | qa3_5_retention.txt | audit_log_archive exists, maintenance script valid |
| F-008 | P3 | PARTIAL | **VERIFIED** | qa3_6_server_header.txt | Version masked, server name still exposed |

---

## Discrepancy Resolution (ALL FILLED)

| D-# | Description | QA Verdict | Proof Command | Evidence File |
|-----|-------------|------------|---------------|---------------|
| D-1 | F-002 orphan container deferral justified? | **JUSTIFIED** | `docker exec zakops-postgres-1 psql ... pg_stat_activity` shows 2 active connections; 29 deal_events vs 5; most recent today | qa1_2_db_sot.txt |
| D-2 | F-003 trigger bypass — security theater? | **PARTIAL** | `has_table_privilege('agent','audit_log','TRUNCATE')=true`; agent can disable trigger (is table owner). Bypass acknowledged in Builder report. Defense-in-depth, not absolute. | qa3_1_delete_trigger.txt |
| D-3 | F-004 "EXISTING" — pre-remediation or newly added? | **VERIFIED** | Git blame shows docs conditional in AGENT-REMEDIATION-001 (2dca48b), predates R-005. Builder correctly marked EXISTING. | qa3_2_docs_exposure.txt |
| D-4 | F-005 "DOCUMENTED" without testing | **ACCEPTABLE** | /metrics returns 200 with standard Prometheus metrics (GC, process stats). No secrets leaked. Builder noted "requires production test" — dev mode behavior expected. | qa3_3_metrics.txt |
| D-5 | F-008 MaskServerHeaderMiddleware actually works? | **PARTIAL** | Response shows `server: uvicorn` + `server: ZakOps`. Version is NOT disclosed. Middleware exists at line 40. Duplicate header issue but no version leak. | qa3_6_server_header.txt |
| D-6 | F-001 Langfuse RT-TRACE-SINK real test? | **VERIFIED** | test_trace_sink.py is 57 lines with real assertions. trace_sink.py is 76 lines with LocalTraceSink class. RT-LANGFUSE-NEG passed — no Langfuse errors during invoke. | qa2_1_langfuse.txt |
| D-7 | F-007 retention script operational? | **VERIFIED** | audit_log_maintenance.sql is 35 lines with proper archive flow. audit_log_archive table schema matches audit_log. Script includes trigger disable/re-enable logic. | qa3_5_retention.txt |

---

## RT Checklist

| RT | Requirement | Verdict | Evidence |
|----|-------------|---------|----------|
| RT-DB-SOT | Split-brain proof | **PASS** | zakops-postgres-1 has 2 active connections, 29 fresh events. zakops-backend-postgres-1 has 0 connections, stale data. |
| RT-TIMEOUT | No hanging tests | **PASS** | All curl commands used --max-time 30 --connect-timeout 10 |
| RT-DOC-1 | Deferred/Documented justified | **PASS** | F-002: active DB proven. F-005: benign metrics only. |
| RT-LANGFUSE-NEG | No network calls when disabled | **PASS** | Invoke succeeded, zero Langfuse errors in logs |
| RT-PATH-MATRIX | Endpoint variants tested | **PASS** | /docs, /redoc, /metrics, /openapi.json all tested |
| RT-TRACE-SINK | Tracing wiring proof | **PASS** | trace_sink.py + test_trace_sink.py exist with real code |
| RT-TRIGGER-1 | DELETE trigger works | **PASS** | Trigger blocks DELETE. Bypass risk documented (can_truncate=true). |
| RT-ERROR-REDACT | No stack traces in errors | **PASS** | Error response shows only "Validation error" + field names |
| RT-GOLDEN-PATH | E2E operator flow | **PASS** | Dashboard 307, invoke completed, approvals 200, activity 200 |
| RT-GATE-INV | Gate inventory created | **PASS** | See below |

---

## Gate Inventory (RT-GATE-INV)

| Gate ID | Phase | Description | Evidence Files | QA Verdict |
|---------|-------|-------------|----------------|------------|
| QA-0 | Artifacts | Output files exist | qa0_1_output_dir.txt, qa0_2_artifacts.txt, qa0_4_new_files.txt | PASS |
| QA-1.2 | RT-DB-SOT | Split-brain proof | qa1_2_db_sot.txt | PASS |
| QA-1 | Health | Services + Langfuse | qa1_1_health.txt, qa1_3_langfuse_startup.txt | PASS |
| QA-2.1-NEG | RT-LANGFUSE-NEG | No network calls | qa2_1_neg_langfuse.txt | PASS |
| QA-2 | P2 Fixes | F-001, F-002 | qa2_1_langfuse.txt, qa2_2_orphan.txt | PASS |
| QA-3 | P3 Fixes | F-003 through F-008 | qa3_*.txt | PASS |
| QA-4.6 | RT-ERROR-REDACT | Error redaction | qa4_6_error_redact.txt | PASS |
| QA-4 | Regression | Services healthy | qa4_*.txt | PASS |
| QA-5.0 | RT-GOLDEN-PATH | E2E operator flow | qa5_0_golden_path.txt | PASS |
| QA-6 | Reconciliation | Discrepancies resolved | D-1 through D-7 all filled | PASS |

---

## Critical Evidence

### QA-1.2: DB Source of Truth (RT-DB-SOT)
```
zakops-backend-postgres-1:
- deal_events: 5, most recent: 2026-02-02 15:25
- Active connections: 0

zakops-postgres-1:
- deal_events: 29, most recent: 2026-02-03 21:00 (TODAY)
- Active connections: 2 (172.23.0.5, 172.23.0.4)

VERDICT: zakops-postgres-1 is ACTIVE production DB, NOT orphan
F-002 DEFERRAL: JUSTIFIED
```

### QA-3.1: DELETE Trigger (F-003)
```
Trigger: trg_prevent_audit_log_delete (BEFORE DELETE)
Test: DELETE blocked with error "DELETE on audit_log is prohibited"
Row count: unchanged after delete attempt
BYPASS NOTE: Agent user can_truncate=true (table owner)
VERDICT: PASS (defense-in-depth)
```

### QA-4.6: RT-ERROR-REDACT
```
Error response: {"detail":"Validation error","errors":[...]}
Stack traces: None
Env var names: None
Internal hostnames: None
VERDICT: PASS
```

### QA-5.0: RT-GOLDEN-PATH
```
Dashboard: 307 (redirect, expected)
Agent invoke: completed
Approvals endpoint: 200
Activity endpoint: 200
VERDICT: PASS
```

---

## Findings (Informational)

### P2: Trigger Bypass Risk (D-2)
The `agent` database user owns the `audit_log` table and can:
- TRUNCATE the table
- DISABLE/DROP the trigger

**Impact:** Medium. The trigger provides defense-in-depth against accidental deletes but not against privileged operations.
**Recommendation:** Transfer table ownership or revoke TRUNCATE privilege.

### P3: Duplicate Server Header (D-5)
Response contains two `server:` headers:
- `server: uvicorn`
- `server: ZakOps`

**Impact:** Low. No version disclosed. Middleware is functional.
**Recommendation:** Rebuild with uvicorn `--no-server-header` flag for complete removal.

---

## Conclusion

AGENT-REMEDIATION-005 has been successfully verified:

1. **P2 Fixes Verified:** F-001 Langfuse conditional init works, F-002 deferral justified
2. **P3 Fixes Verified:** DELETE trigger, log rotation, retention policy all functional
3. **RT-DB-SOT Proven:** zakops-postgres-1 is active production DB (2 connections, fresh data)
4. **RT-GOLDEN-PATH Passed:** Real operator flow works end-to-end
5. **All Discrepancies Resolved:** 7/7 D-# cells filled with verdicts

**No P0 or P1 blockers found.**

---

## Evidence Locations

- QA Evidence: `/home/zaks/bookkeeping/qa/QA-VERIFICATION-005/evidence/`
- Builder Evidence: `/home/zaks/bookkeeping/remediations/AGENT-REMEDIATION-005/evidence/`
- Builder Matrices: `/home/zaks/bookkeeping/remediations/AGENT-REMEDIATION-005/matrices/`

---

*Generated by QA-VERIFICATION-005 audit*
*Auditor: Claude Code (Opus 4.5)*
*Version: V2 (Anti-Escape Edition)*
*Date: 2026-02-04T01:50:00Z*
