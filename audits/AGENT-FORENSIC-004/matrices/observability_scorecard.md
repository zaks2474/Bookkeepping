# Observability Scorecard

**Mission:** AGENT-FORENSIC-004  
**Date:** 2026-02-03  

## RT-3PLANE: Three-Plane Observability

| Plane | Status | Score |
|-------|--------|-------|
| Logs (Structured) | ✅ Configured | 3/3 |
| Traces (Langfuse) | ❌ Not Configured | 0/3 |
| Audit Spine (DB) | ✅ Configured | 3/3 |
| **Total** | **2/3 Planes** | **6/9** |

## RT-LOGSAFE: Sensitive Data Protection

| Check | Status | Score |
|-------|--------|-------|
| Secret Scan (deny-list) | ✅ PASS | 3/3 |
| PII Redaction | ✅ PASS | 3/3 |
| Stack Trace Redaction | ✅ PASS | 3/3 |
| **Total** | **PASS** | **9/9** |

## RT-TAMPER: Log Integrity

| Check | Status | Score |
|-------|--------|-------|
| Log Storage (json-file) | ✅ Configured | 2/3 |
| Audit Protection (triggers) | ⚠️ No triggers | 1/3 |
| Timestamp Integrity (NOW()) | ✅ Server-side | 3/3 |
| **Total** | **PASS w/finding** | **6/9** |

## RT-DIAG: Diagnostic Endpoints

| Check | Status | Score |
|-------|--------|-------|
| /health minimal | ✅ PASS | 3/3 |
| Debug endpoints blocked | ✅ 404 | 3/3 |
| /docs, /redoc exposed | ⚠️ 200 (P3) | 1/3 |
| /metrics exposed | ⚠️ 200 (P3) | 1/3 |
| **Total** | **PASS w/findings** | **8/12** |

## RT-DBSOT: Database Source-of-Truth

| Check | Status | Score |
|-------|--------|-------|
| Agent DB identity | ✅ zakops_agent | 3/3 |
| Backend DB identity | ✅ zakops | 3/3 |
| Fingerprint tables | ✅ Separate | 3/3 |
| Container inventory | ⚠️ Orphan found | 2/3 |
| **Total** | **PASS w/finding** | **11/12** |

## Overall Observability Score

| Category | Score | Max | Percentage |
|----------|-------|-----|------------|
| RT-3PLANE | 6 | 9 | 67% |
| RT-LOGSAFE | 9 | 9 | 100% |
| RT-TAMPER | 6 | 9 | 67% |
| RT-DIAG | 8 | 12 | 67% |
| RT-DBSOT | 11 | 12 | 92% |
| **TOTAL** | **40** | **51** | **78%** |

## Findings Summary

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| F-001 | P2 | RT-3PLANE | Langfuse not configured (traces plane missing) |
| F-002 | P2 | RT-DBSOT | Orphan container zakops-postgres-1 |
| F-003 | P3 | RT-TAMPER | No DELETE triggers on audit_log |
| F-004 | P3 | RT-DIAG | /docs, /redoc exposed in development |
| F-005 | P3 | RT-DIAG | /metrics exposed without auth |

**OVERALL STATUS:** PASS with P2/P3 findings
