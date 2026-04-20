# Finding-to-Fix Matrix — AGENT-REMEDIATION-004

## Summary

| Severity | Total | Fixed | Documented | Deferred |
|----------|-------|-------|------------|----------|
| P1 | 4 | 4 | 0 | 0 |
| P2 | 4 | 3 | 1 | 0 |
| P3 | 4 | 1 | 2 | 1 |
| Claude-Identified | 6 | 0 | 6 | 0 |
| **TOTAL** | **18** | **8** | **9** | **1** |

---

## P1 Findings

| Finding ID | Severity | Description | Fix Task | Status | Notes |
|------------|----------|-------------|----------|--------|-------|
| F003-P1-001 | P1 | Agent Activity Returns Hardcoded Empty State | R1.A | ✅ FIXED | Wired to audit_log with pagination |
| F003-P1-002 | P1 | JSON.parse Without Validation in Chat Page | R1.B | ✅ FIXED | RT-STORE-1 compliant utility |
| F003-P2-003-ELEVATED | P1 | Extra Postgres Containers (Split-Brain Risk) | R2.C | ✅ FIXED | Removed stale container |
| F003-CL-001 | P1 | Decision/Execution Consistency Gap | R1.C | ✅ FIXED | RT-SEM-1 Option A documented |

## P2 Findings

| Finding ID | Severity | Description | Fix Task | Status | Notes |
|------------|----------|-------------|----------|--------|-------|
| F003-P2-001 | P2 | No Dedicated Expiry Background Worker | R2.A | ✅ FIXED | Lazy expiry with HTTP 410 |
| F003-P2-002 | P2 | Approval Approved Despite Backend Failure | R1.C + R2.B | ✅ FIXED | Option A semantics (by design) |
| F003-CL-002 | P2 | No Dashboard Error State for Failed Approvals | R2.B | 📝 DOCUMENTED | API returns error state, UI deferred |
| F003-CL-003 | P2 | Activity Endpoint Not Connected to audit_log | R1.A | ✅ FIXED | Now queries real audit_log |

## P3 Findings

| Finding ID | Severity | Description | Fix Task | Status | Notes |
|------------|----------|-------------|----------|--------|-------|
| F003-P3-001 | P3 | V1 Endpoint Different Payload Shape | R3.B | 📝 DOCUMENTED | Intentional, backward compat |
| F003-P3-002 | P3 | No Zod Schemas for Approval Types | R3.A | ✅ FIXED | Created approval schemas |
| F003-P3-003 | P3 | Deal Chat Uses Query Param | R3.C | 📝 DOCUMENTED | Working as intended |
| F003-P3-004 | P3 | WebSocket Not Implemented | R3.D | ⏸️ DEFERRED | Ticket created, polling acceptable |

## Sweep-Discovered Findings (RT-SWEEP-1)

| Finding ID | Severity | Description | Fix Task | Status | Notes |
|------------|----------|-------------|----------|--------|-------|
| F003-CL-004 | P3 | /api/chat/execute-proposal is placeholder | N/A | 📝 DOCUMENTED | Placeholder for future feature |
| F003-CL-005 | P3 | /api/chat/session/[sessionId] is placeholder | N/A | 📝 DOCUMENTED | Placeholder for future feature |
| F003-CL-006 | P3 | /api/events returns 501 (SSE not implemented) | N/A | 📝 DOCUMENTED | Global SSE not needed |
| F003-CL-007 | P3 | Multiple action routes use mock fallback | N/A | 📝 DOCUMENTED | Graceful degradation pattern |

---

## Evidence Files

### Before Evidence (Phase R0)
- `evidence/before/r0_2_activity_before.txt` — Hardcoded empty activity
- `evidence/before/r0_3_jsonparse_before.txt` — Unsafe JSON.parse
- `evidence/before/r0_4_approval_error_handling_before.txt` — Error handling review
- `evidence/before/r0_5_expiry_worker_before.txt` — No expiry worker, 5 stale approvals
- `evidence/before/r0_6_db_sot.txt` — DB source of truth verification
- `evidence/before/r0_7_endpoint_sweep.txt` — Endpoint realism sweep

### After Evidence (Phases R1-R3)
- `evidence/after/r1_a4_activity_after.txt` — Real audit_log data
- `evidence/after/r1_b3_jsonparse_after.txt` — RT-STORE-1 compliant
- `evidence/after/r1_c_semantics_decision.md` — Option A documentation
- `evidence/after/r2_a4_expiry_after.txt` — Lazy expiry working
- `evidence/after/r3_a_zod_schemas.txt` — Zod schemas created
- `evidence/after/r3_d2_websocket_ticket.md` — WebSocket enhancement ticket

### Regression Evidence
- `evidence/regression/r1_reg*.txt` — Phase R1 regression
- `evidence/regression/r2_reg*.txt` — Phase R2 regression
- `evidence/regression/r3_reg*.txt` — Final regression

---

*Last Updated: 2026-02-03T21:40 UTC*
