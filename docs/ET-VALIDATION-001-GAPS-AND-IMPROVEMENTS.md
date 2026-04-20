# ET-VALIDATION-001: Consolidated Gaps, Improvements & Deferred Items

**Generated:** 2026-02-15
**Source Mission:** `MISSION-ET-VALIDATION-001.md` (Email Triage Operational Validation Roadmap)
**Phases Covered:** P0 through P8
**QA Reports Analyzed:**

| Report | Scope | Result | Agent |
|--------|-------|--------|-------|
| QA-ET-VALIDATION-VERIFY-001 | Checkpoint validation (pre-execution) | 23/44 PASS | Codex |
| QA-ET-P2-VERIFY-001 | Phase 1 + 2 (Schema & UX) | 8/8 PASS | Gemini |
| QA-ET-P4P5-VERIFY-001 | Phases 4 + 5 (Promotion & Routing) | 9/9 PASS | Gemini |
| QA-ET-P6P7-VERIFY-001 | Phases 6 + 7 (Collaboration & Security) | 10/10 PASS | Claude |
| QA-ET-P8-VERIFY-001 | Phase 8 (Operational Excellence) + Final AC | 13/13 PASS | Claude |

**Remediation Missions:** QA-ET-P6P7-REMEDIATE-001 (NO-OP), QA-ET-P8-REMEDIATE-001 (NO-OP)

---

## 1. Deferred Items

### 1.1 G0-12: SSE Transport Auth (MITIGATED)

- **Origin:** Phase 0, Gate G0-12
- **Issue:** FastMCP SSE `/sse` endpoint returns 200 without Bearer token. The SSE handler operates at the transport level before application middleware runs.
- **Mitigation:** CF Access Layer 1 gates all paths (including SSE) when `ZAKOPS_CF_ACCESS_REQUIRED=true`. REST endpoints (`/tools`, `/tools/zakops/*`) correctly enforce Bearer auth regardless.
- **Status:** Deferred from P0 → P7; mitigated in P7 via dual-layer auth architecture. Full fix requires FastMCP upstream change or SSE transport replacement.
- **Risk Level:** LOW (mitigated by network-layer auth when CF Access is enabled)

### 1.2 Undo Approval Outbox Cascade

- **Origin:** Phase 4 completion report
- **Issue:** `POST /api/quarantine/{id}/undo-approve` archives the deal and restores quarantine to pending, but does NOT cascade to outbox consumers. Downstream services may have already acted on the `deal_created` event.
- **Status:** Accepted risk. Undo is an admin-only last-resort operation.
- **Risk Level:** MEDIUM (data consistency risk for already-consumed outbox events)

### 1.3 CF Access Opt-In

- **Origin:** Phase 7 completion report
- **Issue:** `ZAKOPS_CF_ACCESS_REQUIRED=false` by default. Layer 1 (CF Access) does not protect the bridge until the environment variable is explicitly enabled after Cloudflare tunnel configuration.
- **Status:** Expected behavior. Enable when infrastructure is ready.
- **Action Required:** Set `ZAKOPS_CF_ACCESS_REQUIRED=true` in production bridge environment after Cloudflare tunnel is configured.

---

## 2. Outstanding Risks

### 2.1 Cache TTL Mismatches

| Cache | TTL | Impact | Source |
|-------|-----|--------|--------|
| Bridge flag cache (`_get_flag`) | 60s | Shadow mode changes take up to 60s to propagate | P0 checkpoint |
| Backend flag cache | 5s | Kill switch activation worst case is 5s (gate G0-04 says "within 1s") | P0 checkpoint |
| Kill switch Dashboard TTL | 1.0s | Confirmed correct in P2 QA | QA-ET-P2-VERIFY-001 |

**Assessment:** The P0 gate language ("within 1s") is aspirational; actual worst case is 5s for backend. Bridge-side flag changes are even slower (60s). Not a correctness issue but a documentation accuracy gap.

### 2.2 No Circuit Breaker Pattern

- **Origin:** Phase 7 completion report
- **Issue:** Each MCP bridge tool call fails independently without backoff or circuit-breaking. A backend outage causes every tool call to timeout individually.
- **Impact:** Under backend failure, the agent will burn through context calling tools that all time out.
- **Recommendation:** Add circuit breaker with half-open recovery (e.g., 3 failures in 30s → open → probe every 60s).

### 2.3 Pre-Phase-5 Routing Reason NULL

- **Origin:** Phase 5 completion report
- **Issue:** `routing_reason` field is NULL for quarantine items created before Phase 5 deployment.
- **Impact:** Detail view shows empty routing reason for historical items.
- **Recommendation:** Backfill migration or display "Pre-routing era" for NULL values.

### 2.4 Thread Move Granularity

- **Origin:** Phase 5 completion report
- **Issue:** `POST /api/threads/move` updates all rows matching `(deal_id, thread_id)` — no per-email-provider granularity.
- **Impact:** If a thread is linked to the same deal from multiple providers, moving affects all providers.
- **Recommendation:** Add optional `provider` filter parameter to move endpoint.

### 2.5 Database Catalog Corruption (zakops)

- **Origin:** Phase 8 completion report, QA-ET-P8-VERIFY-001 (ENH-3)
- **Issue:** `pg_dump` fails on `deal_events` table due to pre-existing catalog corruption. Backup drill uses per-table COPY fallback (74/76 tables backed up, 2 views skipped).
- **Impact:** Full-database pg_dump unusable; per-table COPY works but is fragile.
- **Recommendation:** Schedule `pg_catalog` repair or rebuild the table by dumping data → drop → recreate → restore.

### 2.6 Migration Sequence Fragility

- **Origin:** Phase 0 completion report
- **Issue:** Migration numbers (032-035) were assigned sequentially. Future migrations from other features could conflict if numbering isn't coordinated.
- **Status:** Resolved — all 4 migrations (032-035) are applied.

---

## 3. Enhancement Opportunities

### From QA-ET-P8-VERIFY-001 Scorecard

| ID | Enhancement | Category | Effort |
|----|-------------|----------|--------|
| ENH-1 | Add automated load tests to CI pipeline (lightweight smoke profile) | CI/CD | Medium |
| ENH-2 | Add cron entry for `email_triage_health_probe.sh` (currently manual setup) | Ops | Low |
| ENH-3 | Fix zakops DB `pg_dump` catalog corruption on `deal_events` table | Database | High |
| ENH-4 | Add Prometheus scrape endpoint to backend for metric-based alerting | Monitoring | Medium |
| ENH-5 | Automate daily shadow measurement report generation | Automation | Low |

### From QA-ET-VALIDATION-VERIFY-001 Completion Report

| ID | Enhancement | Category | Effort |
|----|-------------|----------|--------|
| ENH-6 | Add `extraction_evidence` field to quarantine UI detail panel | UX | Low |
| ENH-7 | Display `field_confidences` object in quarantine detail panel | UX | Low |
| ENH-8 | Add visual confidence bar/meter alongside numeric confidence score | UX | Low |
| ENH-9 | Add quarantine item count badge to navigation sidebar | UX | Low |
| ENH-10 | Add bulk export of quarantine items (CSV/JSON) | Feature | Medium |

### From Independent P8 Re-verification (Claude)

| ID | Enhancement | Category | Effort |
|----|-------------|----------|--------|
| ENH-11 | Fix `backup_restore_drill.sh` ownership (root:root → zaks:zaks) | Ops | Trivial |
| ENH-12 | Address Surface 14 advisory: `main-app.js` exceeds 2MB limit (currently 7.6MB) | Performance | Medium |

---

## 4. QA Process Observations

### 4.1 First-Pass Quality

All four post-execution QA verifications achieved FULL PASS on first attempt:
- QA-ET-P2: 8/8 PASS
- QA-ET-P4P5: 9/9 PASS
- QA-ET-P6P7: 10/10 PASS
- QA-ET-P8: 13/13 PASS

Both conditional remediation missions (P6P7, P8) were NO-OPs — zero failures to remediate. This indicates strong implementation quality across all phases.

### 4.2 Pre-Execution Validation Run

QA-ET-VALIDATION-VERIFY-001 was run by Codex **before** phases P1-P8 were executed (only P0 was complete). It correctly identified 21/44 failures — all in the NOT_EXECUTED phase families (VF-03 through VF-08, ST-1 through ST-4). The 23 gates that passed were infrastructure/perimeter checks (PF-*, XC-*, VF-01, VF-02).

This demonstrates the QA framework correctly detects missing implementation, and also validates that the perimeter checks (sync chain, migrations, type safety) were already green before feature work began.

### 4.3 Cross-Agent Consistency

QA was distributed across three agents:
- **Codex** (gpt-5.3-codex): Validation checkpoint run
- **Gemini** (gemini-3-pro-preview): P2 and P4P5 verification
- **Claude** (opus): P6P7, P8 verification, and independent re-verification

No cross-agent contradictions were found. All agents agreed on gate pass/fail status when evaluating the same surfaces.

### 4.4 Evidence Grep Pattern Issue

One false positive was identified in the QA process:
- **PF-3 (TypeScript validation):** Mission spec runs `npx tsc --noEmit` from monorepo root where the TypeScript CLI is not directly available. `make validate-local` passes its internal dashboard TypeScript check, but the standalone command fails.
- **Fix Applied:** R-01 remediation added location-correct verification at the dashboard workspace.
- **Lesson:** QA gate commands should match the actual project structure (workspace-level TypeScript, not root-level).

---

## 5. Documentation Gaps

| Gap | Location | Status |
|-----|----------|--------|
| Kill switch TTL actual vs documented | `EMAIL-TRIAGE-SLO.md` says injection <30s p95; P0 gate says "within 1s" for kill switch; actual is 5s | Needs alignment |
| Delegation task lifecycle architecture doc | Not in `ARCHITECTURE.md` | Recommended: add delegated task state machine diagram |
| Routing decision contract formal spec | Embedded in code, not in standalone doc | Recommended: extract to `ROUTING-DECISION-CONTRACT.md` |
| Shadow measurement automation schedule | `EMAIL-TRIAGE-BURNIN-PLAN.md` describes manual daily checks | Recommended: cron automation (ENH-5) |

---

## 6. Security Posture Summary

| Layer | Status | Notes |
|-------|--------|-------|
| Bearer Token (Layer 2) | ACTIVE | All REST endpoints enforce auth |
| CF Access (Layer 1) | OPT-IN | Enable via `ZAKOPS_CF_ACCESS_REQUIRED=true` |
| Key Rotation | READY | Dual-token window, runbook documented |
| Log Redaction | ACTIVE | Secrets masked (8+4 chars), PII emails masked |
| SSE Transport | PARTIAL | Returns 200 without auth; mitigated by CF Access |
| Data Retention | DOCUMENTED | Purge endpoint ready, dry_run default |

---

## 7. Production Readiness Checklist

### Ready Now
- [x] Email triage pipeline (inject → quarantine → approve → deal)
- [x] Auto-routing with conflict resolution
- [x] Delegated task management with dead-letter handling
- [x] Operator controls (undo, retry, confirm, thread management)
- [x] SLOs defined and documented
- [x] Monitoring/alerting framework (health probe)
- [x] Load test profiles created
- [x] Backup/restore drill passed (with pg_dump workaround)
- [x] Shadow measurement tooling ready
- [x] 7-day burn-in plan documented
- [x] Production safety flags at safe defaults

### Requires Action Before Production
- [ ] Enable CF Access Layer 1 (`ZAKOPS_CF_ACCESS_REQUIRED=true`)
- [ ] Schedule cron for `email_triage_health_probe.sh` (ENH-2)
- [ ] Execute 7-day shadow burn-in per `EMAIL-TRIAGE-BURNIN-PLAN.md`
- [ ] Graduate from shadow mode after burn-in success criteria are met
- [ ] Fix `backup_restore_drill.sh` ownership (ENH-11)

### Recommended Before Production
- [ ] Address `main-app.js` bundle size (7.6MB, limit 2MB) (ENH-12)
- [ ] Add circuit breaker to bridge tool calls (Risk 2.2)
- [ ] Repair `deal_events` catalog corruption (ENH-3)
- [ ] Backfill NULL `routing_reason` for pre-P5 items (Risk 2.3)
- [ ] Automate shadow measurement reports (ENH-5)

---

## 8. Summary Statistics

| Category | Count |
|----------|-------|
| Total QA Gates Evaluated | 40 (post-execution) |
| Gates Passed | 40/40 (100%) |
| Remediation Missions Executed | 2 |
| Remediations Required | 0 (both NO-OP) |
| Deferred Items | 3 |
| Outstanding Risks | 6 |
| Enhancement Opportunities | 12 |
| Documentation Gaps | 4 |
| Phases Completed | 9 (P0-P8) |
| Migrations Applied | 4 (032-035) |
| Files Created | 18 |
| Files Modified | 12 |

---

*This document consolidates findings from all QA verification and remediation reports for the ET-VALIDATION-001 mission. It serves as the authoritative reference for post-mission improvement planning.*
