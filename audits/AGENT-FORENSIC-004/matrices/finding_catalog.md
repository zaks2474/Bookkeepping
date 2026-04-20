# Finding Catalog

**Mission:** AGENT-FORENSIC-004  
**Date:** 2026-02-03  
**Total Findings:** 5 (0 P0, 2 P2, 3 P3)

## P2 Findings (Medium Priority)

### F-001: Langfuse Tracing Not Configured

| Field | Value |
|-------|-------|
| ID | F-001 |
| Severity | P2 |
| Category | RT-3PLANE (Observability) |
| Status | OPEN |
| Evidence | evidence/rt-additions/6_A_3_traces_plane.txt |

**Description:** Langfuse environment variables are empty. The traces plane of three-plane observability is non-functional.

**Impact:** Cannot trace requests across services via distributed tracing. Debugging production issues requires manual log correlation.

**Recommendation:** 
1. Obtain Langfuse credentials and configure in `.env`
2. OR implement OpenTelemetry as alternative

---

### F-002: Orphan Postgres Container

| Field | Value |
|-------|-------|
| ID | F-002 |
| Severity | P2 |
| Category | RT-DBSOT (Database) |
| Status | OPEN |
| Evidence | evidence/rt-additions/6_E_3_containers.txt |

**Description:** Container `zakops-postgres-1` exists alongside `zakops-backend-postgres-1` and `zakops-agent-db`. This may cause confusion about which DB is authoritative.

**Impact:** Developers may accidentally connect to wrong DB during debugging.

**Recommendation:**
1. Remove stale container: `docker rm zakops-postgres-1`
2. Document correct container names

---

## P3 Findings (Low Priority)

### F-003: No DELETE Triggers on audit_log

| Field | Value |
|-------|-------|
| ID | F-003 |
| Severity | P3 |
| Category | RT-TAMPER (Log Integrity) |
| Status | OPEN |
| Evidence | evidence/rt-additions/6_C_tamper.txt |

**Description:** audit_log table has no triggers to prevent DELETE operations. Defense-in-depth gap.

**Impact:** Privileged users could delete audit records without triggering alerts.

**Recommendation:** Add trigger or policy to log/block DELETE operations on audit_log.

---

### F-004: OpenAPI Docs Exposed in Development

| Field | Value |
|-------|-------|
| ID | F-004 |
| Severity | P3 |
| Category | RT-DIAG (Diagnostic Endpoints) |
| Status | OPEN |
| Evidence | evidence/rt-additions/6_D_diag.txt |

**Description:** /docs and /redoc endpoints return HTTP 200 in development environment.

**Impact:** API documentation exposed, revealing internal endpoints.

**Recommendation:** Disable in production via FastAPI `docs_url=None, redoc_url=None` in prod config.

---

### F-005: /metrics Endpoint Exposed Without Auth

| Field | Value |
|-------|-------|
| ID | F-005 |
| Severity | P3 |
| Category | RT-DIAG (Diagnostic Endpoints) |
| Status | OPEN |
| Evidence | evidence/rt-additions/6_D_diag.txt |

**Description:** /metrics endpoint returns Prometheus metrics without authentication.

**Impact:** Internal system metrics (memory, CPU, db_connections) visible to anyone.

**Recommendation:** 
1. Require auth for /metrics in production
2. OR bind to internal network only

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| P0 (Critical) | 0 | - |
| P1 (High) | 0 | - |
| P2 (Medium) | 2 | OPEN |
| P3 (Low) | 3 | OPEN |
| **Total** | **5** | **All OPEN** |

**Blocking Issues:** None (no P0/P1)  
**Recommended for Next Remediation:** AGENT-REMEDIATION-005
