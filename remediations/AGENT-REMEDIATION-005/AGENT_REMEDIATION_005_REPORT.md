# AGENT-REMEDIATION-005 — Final Report

**Codename:** AGENT-REMEDIATION-005
**Date:** 2026-02-03
**Executor:** Claude Opus 4.5
**Mode:** Evidence-first remediation
**Status:** COMPLETE (with caveats)

---

## Executive Summary

This mission addressed 8 findings from AGENT-FORENSIC-004 (2 P2, 6 P3). All findings have been addressed through fixes, documentation, or justified deferral.

### Results

| Category | Count |
|----------|-------|
| FIXED | 4 (F-001, F-003, F-006, F-007) |
| PARTIAL | 1 (F-008 - version masked) |
| EXISTING | 1 (F-004 - already implemented) |
| DOCUMENTED | 1 (F-005 - production mode) |
| DEFERRED | 1 (F-002 - data safety) |

---

## Finding Remediation Details

### F-001: Langfuse Tracing Not Configured (P2) - FIXED

**Root Cause:** Langfuse SDK imported unconditionally, crashed without keys.

**Fix:**
1. Created `app/core/tracing.py` with conditional initialization
2. Created `app/core/trace_sink.py` for local testing (RT-TRACE-SINK)
3. Updated imports to use lazy initialization
4. Added graceful skip message when keys not configured
5. Added env var placeholders to `.env`

**Evidence:**
- App starts cleanly without Langfuse keys
- Startup log shows: "Langfuse tracing not configured"
- RT-TRACE-SINK test passes (proof-of-wiring)
- Activation guide created

**Activation:** Uncomment and fill `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` in `.env`, restart.

### F-002: Orphan Container zakops-postgres-1 (P2) - DEFERRED

**Investigation Finding:** Container is NOT orphan - it contains the ACTIVE production data.

**Evidence:**
- `zakops-postgres-1`: 29 deal_events, most recent 2026-02-03 21:00 (TODAY)
- `zakops-backend-postgres-1`: 5 deal_events, most recent 2026-02-02 15:25 (yesterday)

**Decision:** DEFERRED - removing this container would cause DATA LOSS.

**Recommendation:** Investigate which service is writing to this container, then plan proper data migration.

### F-003: No DELETE Trigger on audit_log (P3) - FIXED

**Fix:** Created `trg_prevent_audit_log_delete` trigger that blocks DELETE operations.

**Verification:**
```sql
DELETE FROM audit_log WHERE id = '...'
-- ERROR: DELETE on audit_log is prohibited — append-only table (chain-of-custody)
```

**Bypass Note:** Agent user can bypass via TRUNCATE or DROP TRIGGER (table owner). Full hardening requires privilege changes.

### F-004: /docs, /redoc Exposed (P3) - EXISTING

**Status:** Already implemented in codebase.

**Evidence:** `main.py:59-69` - docs disabled when `ENVIRONMENT != development`

### F-005: /metrics Exposed Without Auth (P3) - DOCUMENTED

**Status:** Requires production environment test. In dev mode, /metrics returns 200 (expected).

**Recommendation:** Test with `ENVIRONMENT=production` to verify endpoint protection.

### F-006: Docker Log Rotation Not Configured (P3) - FIXED

**Fix:** Added logging configuration to docker-compose.yml:
```yaml
logging:
  driver: json-file
  options:
    max-size: "50m"
    max-file: "5"
```

**Evidence:** Container inspect shows log rotation config applied.

### F-007: No audit_log Retention Policy (P3) - FIXED

**Fix:**
1. Created `audit_log_archive` table for archival
2. Created `scripts/audit_log_maintenance.sql` maintenance script
3. Documented retention policy (90 days)

**Procedure:** Monthly manual run of maintenance script by admin.

### F-008: Server Version Disclosure (P3) - PARTIAL

**Status:** Version number not disclosed. Server header shows "uvicorn" (no version).

**Evidence:** `server: uvicorn` (not `server: uvicorn/0.x.x`)

**Full Fix:** Requires Docker image rebuild with `--no-server-header` flag.

---

## Files Changed

### New Files
- `app/core/tracing.py` - Conditional Langfuse integration
- `app/core/trace_sink.py` - Local trace sink for testing
- `scripts/test_trace_sink.py` - RT-TRACE-SINK verification
- `scripts/audit_log_maintenance.sql` - Retention maintenance script

### Modified Files
- `app/main.py` - Conditional Langfuse import, server header middleware
- `app/core/langgraph/graph.py` - Use get_callbacks() for tracing
- `app/core/middleware/__init__.py` - Added MaskServerHeaderMiddleware
- `docker-compose.yml` - Added log rotation config, scripts volume mount
- `.env` - Added Langfuse placeholders

### Database Changes
- Created trigger `trg_prevent_audit_log_delete` on `audit_log`
- Created table `audit_log_archive`

---

## Regression Status

| Check | Status |
|-------|--------|
| Agent API Health | PASS |
| Backend API Health | PASS |
| Dashboard Health | PASS (307 redirect) |
| DB Source of Truth | PASS (Agent ≠ Backend) |
| Langfuse Graceful Skip | PASS |
| Log Rotation Config | PASS |
| DELETE Trigger | PASS |
| INSERT Still Works | PASS |

---

## Recommendations

1. **F-002 Investigation:** Determine which service writes to `zakops-postgres-1`, plan data migration
2. **F-008 Full Fix:** Rebuild Docker image with `--no-server-header` uvicorn flag
3. **F-005 Production Test:** Verify /metrics protection with `ENVIRONMENT=production`
4. **Bypass Hardening:** Restrict agent user privileges (REVOKE TRUNCATE, transfer table ownership)

---

## Output Artifacts

1. `AGENT_REMEDIATION_005_REPORT.md` - This file
2. `matrices/finding_to_fix_matrix.md` - Finding status matrix
3. `evidence/before/` - BEFORE state evidence
4. `evidence/after/` - AFTER state evidence
5. `evidence/regression/` - Regression test evidence

---

*End of AGENT-REMEDIATION-005 Report*
*Executor: Claude Opus 4.5*
*Generated: 2026-02-03*
