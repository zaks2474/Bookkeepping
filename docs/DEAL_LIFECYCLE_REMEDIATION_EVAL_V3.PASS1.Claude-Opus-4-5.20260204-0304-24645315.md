# DEAL_LIFECYCLE_REMEDIATION_EVAL_V3 — PASS 1: Coverage & Gaps Analysis

## AGENT IDENTITY
- **agent_name:** Claude-Opus-4-5
- **run_id:** 20260204-0304-24645315
- **date_time:** 2026-02-04T03:04:00Z
- **repo_revision:** 07db465760f88f892b56b8eb18e1746b64f7ddf0
- **pass_type:** PASS 1 (Evaluation)

---

## 1. Executive Summary

### Evaluation Scope
This PASS 1 evaluation analyzes **3 V3 remediation plans** against the **22 issues** documented in the V2 Consolidated Issues Register.

### Plans Evaluated
| Plan | Agent | Run ID | Repo Revision | Phases | Decision Sets |
|------|-------|--------|---------------|--------|---------------|
| 1 | Claude-Opus-4-5 | 20260204-0212-b214408d | a09538f04ed | 7 (0-6) | 7 |
| 2 | Gemini-CLI | 20260204-0221-gemini | unknown | 6 (0-5) | 4 |
| 3 | Codex | 20260204-021313-1158 | a09538f04ed | 7 (0-6) | 7 |

### Key Findings

| Metric | Claude | Gemini | Codex |
|--------|--------|--------|-------|
| Issues Fully Covered | 22/22 | 21/22 | 22/22 |
| Issues Missing | 0 | 1 (ZK-ISSUE-0021 in Backlog) | 0 |
| Decision Sets Complete | 7/7 | 4/7 | 7/7 |
| Phases Aligned | Yes | Mostly | Yes |
| Verification Defined | All | Most | All |

### Overall Assessment
- **Best Structural Coverage:** Claude V3 and Codex V3 (tie)
- **Most Complete Decision Framework:** Claude V3 and Codex V3 (tie)
- **Gap Identified:** Gemini V3 defers ZK-ISSUE-0021 (scheduling/reminders) to "Backlog" without explicit remediation
- **Consensus Decisions:** All 3 plans agree on core decisions (Postgres as SoT, 9-stage model, API-first agent contract)

---

## 2. Coverage Matrix

### A. Full Issue-to-Plan Mapping

| Issue ID | Severity | Title | Claude Phase | Gemini Phase | Codex Phase | Consensus |
|----------|----------|-------|--------------|--------------|-------------|-----------|
| ZK-ISSUE-0001 | P0 | Split-brain persistence | Phase 1 | Phase 1 | Phase 1 | YES |
| ZK-ISSUE-0002 | P0 | Email ingestion disabled | Phase 4 | Phase 0 | Phase 4 | PARTIAL (timing) |
| ZK-ISSUE-0003 | P1 | Quarantine approval no deal | Phase 2 | Phase 2 | Phase 3 | YES |
| ZK-ISSUE-0004 | P1 | No DataRoom folders | Phase 2 | Phase 2 | Phase 4 | YES |
| ZK-ISSUE-0005 | P1 | Dashboard no auth | Phase 5 | Phase 3 | Phase 0 | PARTIAL (timing) |
| ZK-ISSUE-0006 | P1 | Wrong quarantine endpoint | Phase 0 | Phase 2 | Phase 2 | YES |
| ZK-ISSUE-0007 | P1 | Stage taxonomy conflicts | Phase 0 | Phase 3 | Phase 3 | YES |
| ZK-ISSUE-0008 | P1 | Actions split Postgres/SQLite | Phase 1 | Phase 1 | Phase 1 | YES |
| ZK-ISSUE-0009 | P2 | Agent no create_deal | Phase 3 | Phase 4 | Phase 2 | YES |
| ZK-ISSUE-0010 | P2 | RAG unverified | Phase 0 | Phase 0 | Phase 4 | PARTIAL (depth) |
| ZK-ISSUE-0011 | P2 | No event correlation | Phase 3 | Phase 4 | Phase 0 | PARTIAL (timing) |
| ZK-ISSUE-0012 | P2 | Notes endpoint mismatch | Phase 0 | Phase 2 | Phase 2 | YES |
| ZK-ISSUE-0013 | P2 | Capabilities/metrics 501 | Phase 2 | Phase 4 | Phase 4 | YES |
| ZK-ISSUE-0014 | P2 | sys.path hack | Phase 1 | Phase 1 | Phase 1 | YES |
| ZK-ISSUE-0015 | P3 | Approval expiry lazy | Phase 3 | Phase 4 | Phase 5 | YES |
| ZK-ISSUE-0016 | P2 | No duplicate detection | Phase 3 | Phase 3 | Phase 3 | YES |
| ZK-ISSUE-0017 | P3 | No retention policy | Phase 5 | Phase 5 | Phase 5 | YES |
| ZK-ISSUE-0018 | P2 | Zod schema mismatch | Phase 2 | Phase 3 | Phase 2 | YES |
| ZK-ISSUE-0019 | P2 | Executors unwired | Phase 4 | Phase 4 | Phase 4 | YES |
| ZK-ISSUE-0020 | P2 | SSE not implemented | Phase 4 | Phase 5 | Phase 5 | YES |
| ZK-ISSUE-0021 | P2 | No scheduling/reminders | Phase 4 | **BACKLOG** | Phase 4 | **MISS** |
| ZK-ISSUE-0022 | P3 | Archive/restore missing | Phase 2 | Phase 2 | Phase 3 | YES |

### B. Coverage Summary by Severity

| Severity | Total | Claude Covered | Gemini Covered | Codex Covered |
|----------|-------|----------------|----------------|---------------|
| P0 | 2 | 2 | 2 | 2 |
| P1 | 6 | 6 | 6 | 6 |
| P2 | 11 | 11 | 10 | 11 |
| P3 | 3 | 3 | 3 | 3 |
| **TOTAL** | **22** | **22** | **21** | **22** |

### C. Phase Distribution Analysis

| Phase | Claude Issues | Gemini Issues | Codex Issues |
|-------|---------------|---------------|--------------|
| Phase 0 | 4 | 3 | 3 |
| Phase 1 | 3 | 3 | 3 |
| Phase 2 | 5 | 4 | 4 |
| Phase 3 | 4 | 2 | 4 |
| Phase 4 | 4 | 6 | 5 |
| Phase 5 | 2 | 3 | 3 |
| Phase 6 | - | - | - |
| Backlog | 0 | 1 | 0 |

---

## 3. No-Drop Findings

### A. Missing Issues

| Finding ID | Issue ID | Plan | Description | Risk |
|------------|----------|------|-------------|------|
| NDF-001 | ZK-ISSUE-0021 | Gemini | Scheduling/reminders marked as "Backlog" instead of active phase | MEDIUM — Feature gap may persist indefinitely |

**Recommendation:** Promote ZK-ISSUE-0021 from Backlog to Phase 4 or Phase 5 to ensure explicit remediation timeline.

### B. Duplicated Coverage (Redundant Tasks)

| Finding ID | Issue ID | Plans | Description | Risk |
|------------|----------|-------|-------------|------|
| NDF-002 | ZK-ISSUE-0001 | All 3 | Split-brain addressed in Phase 1 by all plans — GOOD | LOW (beneficial redundancy) |
| NDF-003 | ZK-ISSUE-0014 | All 3 | sys.path hack removal covered by all — GOOD | LOW (beneficial redundancy) |

**Assessment:** No harmful duplications found. All three plans address the same core issues, which provides validation rather than waste.

### C. Conflicts Between Plans

| Finding ID | Conflict Area | Claude | Gemini | Codex | Resolution Recommendation |
|------------|---------------|--------|--------|-------|---------------------------|
| NDF-004 | Auth timing | Phase 5 | Phase 3 | Phase 0 | Codex approach (Phase 0) is aggressive but riskier; Claude/Gemini approach safer |
| NDF-005 | Email ingestion timing | Phase 4 | Phase 0 (dry-run) | Phase 4 | Gemini's dry-run in Phase 0 is good for early validation |
| NDF-006 | Correlation ID timing | Phase 3 | Phase 4 | Phase 0 | Codex approach (Phase 0) enables earlier traceability |

**Assessment:**
- **NDF-004:** Auth timing conflict is significant. Recommendation: Use Claude's Phase 5 approach (after core functionality) to avoid disrupting development.
- **NDF-005:** Gemini's dry-run approach in Phase 0 is valuable for early validation even if full ingestion is Phase 4.
- **NDF-006:** Codex's early correlation ID implementation (Phase 0) is preferred for debugging throughout development.

### D. Risky Assumptions

| Finding ID | Plan | Assumption | Risk | Mitigation |
|------------|------|------------|------|------------|
| NDF-007 | All | RAG service will be stable | HIGH — RAG noted as "pool=null at boot" | Add health check gating in Phase 0 |
| NDF-008 | All | JSON→Postgres migration will be lossless | MEDIUM — Schema differences exist | Require dry-run with validation before production migration |
| NDF-009 | Gemini | Email ingestion cron can run dry-run in Phase 0 | LOW — May conflict with disabled state | Verify cron job can be enabled in dry-run mode |
| NDF-010 | All | Dashboard Zod schemas are the only source of silent failures | MEDIUM — Other sources may exist | Comprehensive API contract testing needed |

### E. Underspecified Areas

| Finding ID | Area | Plans Affected | Issue | Recommendation |
|------------|------|----------------|-------|----------------|
| NDF-011 | Rollback procedures | All | Rollback described but no specific scripts/procedures | Add explicit rollback scripts to each phase |
| NDF-012 | Data migration validation | All | Migration mentioned but validation criteria vague | Define row-count, field-mapping, and integrity checks |
| NDF-013 | SSE implementation | Claude, Codex | SSE mentioned but no protocol/payload spec | Define SSE event types and payload schemas |
| NDF-014 | Scheduling framework | Claude, Codex | "Add scheduling" without specifying approach | Clarify: cron, celery, or built-in scheduler |

---

## 4. Plan Quality Scorecard

### Scoring Dimensions (0-5 scale)
- **5:** Excellent — Comprehensive, detailed, no gaps
- **4:** Good — Mostly complete, minor gaps
- **3:** Adequate — Covers basics, some gaps
- **2:** Weak — Significant gaps or vagueness
- **1:** Poor — Major gaps, unclear
- **0:** Missing — Not addressed

### A. Claude-Opus-4-5 Plan Scorecard

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **Issue Coverage** | 5 | All 22 issues explicitly mapped to phases with task IDs |
| **Decision Clarity** | 5 | 7 decision sets with options, pros/cons, migration approaches, verification proofs |
| **Phase Sequencing** | 5 | Clear dependencies stated; logical progression from P0 blockers to P6 decommission |
| **Verification Rigor** | 5 | Every phase has gate checks, acceptance criteria, and evidence requirements |
| **Risk Management** | 4 | Risks and rollbacks stated but no explicit scripts |
| **Actionability** | 4 | Tasks are atomic but effort estimates ("S/M/L") are relative, not time-bound |
| **TOTAL** | **28/30** | |

### B. Gemini-CLI Plan Scorecard

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **Issue Coverage** | 4 | 21/22 issues covered; ZK-ISSUE-0021 deferred to backlog |
| **Decision Clarity** | 4 | 4 decision sets (D1-D4) are clear but fewer than others |
| **Phase Sequencing** | 4 | 6 phases with dependencies but less explicit about inter-phase gates |
| **Verification Rigor** | 4 | Coverage matrix has verification column; E2E proof commands included |
| **Risk Management** | 3 | Mentions risks but less detailed mitigation |
| **Actionability** | 4 | Task list is clear; atomic and prioritized |
| **TOTAL** | **23/30** | |

### C. Codex Plan Scorecard

| Dimension | Score | Evidence |
|-----------|-------|----------|
| **Issue Coverage** | 5 | All 22 issues explicitly mapped with verification steps |
| **Decision Clarity** | 5 | 7 decision sets with options, pros/cons, recommendations, verification proofs |
| **Phase Sequencing** | 5 | 7 phases with explicit dependencies and gates |
| **Verification Rigor** | 5 | Every issue has verification step and definition of done in coverage matrix |
| **Risk Management** | 4 | Risks and rollbacks mentioned; CI guard rails specified |
| **Actionability** | 5 | Prioritized backlog with effort, owner, dependencies, and expected outcomes |
| **TOTAL** | **29/30** | |

### D. Comparative Summary

| Dimension | Claude | Gemini | Codex | Best |
|-----------|--------|--------|-------|------|
| Issue Coverage | 5 | 4 | 5 | Claude/Codex |
| Decision Clarity | 5 | 4 | 5 | Claude/Codex |
| Phase Sequencing | 5 | 4 | 5 | Claude/Codex |
| Verification Rigor | 5 | 4 | 5 | Claude/Codex |
| Risk Management | 4 | 3 | 4 | Claude/Codex |
| Actionability | 4 | 4 | 5 | Codex |
| **TOTAL** | **28** | **23** | **29** | **Codex** |

---

## 5. Decision Set Consensus Analysis

### A. Core Decisions (All Plans Agree)

| Decision Area | Consensus | Evidence |
|---------------|-----------|----------|
| Source of Truth | PostgreSQL `zakops.deals` | All 3 recommend Option A |
| Stage Taxonomy | Keep 9-stage canonical model | All 3 keep existing workflow.py stages |
| Agent Contract | API-first (no direct DB writes) | All 3 specify HTTP-only tool calls |
| Email Ingestion Target | POST to `/api/quarantine` | All 3 route ingestion through backend API |
| HITL Approach | Approval required for mutations | All 3 specify HITL for create_deal |

### B. Decisions Where Plans Diverge

| Decision Area | Claude | Gemini | Codex | Recommendation |
|---------------|--------|--------|-------|----------------|
| Auth timing | Phase 5 | Phase 3 | Phase 0 | Phase 5 (Claude) — avoid disrupting early dev |
| Correlation ID timing | Phase 3 | Phase 4 | Phase 0 | Phase 0 (Codex) — enable early tracing |
| Approval storage | Agent DB | Agent DB | Backend DB mirror | Backend mirror (Codex) — unified audit |
| RAG architecture depth | Moderate | Light | Detailed | Codex approach preferred |

### C. Missing Decisions (Not Covered by Any Plan)

| Gap | Description | Recommendation |
|-----|-------------|----------------|
| Backup strategy | No plan addresses database backup procedures | Add to Phase 5 hardening |
| Incident response | No plan addresses rollback testing or incident procedures | Add runbook to Phase 6 |
| Performance testing | No plan includes load testing | Add to Phase 5 QA |

---

## 6. Recommended Unified Action Items

Based on this PASS 1 evaluation, the following actions are recommended before PASS 2 synthesis:

### High Priority (Block PASS 2)

| # | Action | Rationale |
|---|--------|-----------|
| 1 | Promote ZK-ISSUE-0021 from Backlog to active phase | Gemini leaves scheduling gap |
| 2 | Align auth timing decision | Current conflict: Phase 0 vs Phase 3 vs Phase 5 |
| 3 | Align correlation ID timing decision | Current conflict: Phase 0 vs Phase 3 vs Phase 4 |

### Medium Priority (Include in PASS 2)

| # | Action | Rationale |
|---|--------|-----------|
| 4 | Add explicit rollback scripts to each phase | All plans mention rollback but lack scripts |
| 5 | Define data migration validation criteria | Vague across all plans |
| 6 | Specify SSE event types and payloads | Underspecified in all plans |
| 7 | Clarify scheduling framework (cron/celery/other) | Underspecified in all plans |

### Low Priority (Nice to Have)

| # | Action | Rationale |
|---|--------|-----------|
| 8 | Add backup strategy to Phase 5 | Not covered by any plan |
| 9 | Add incident response procedures to Phase 6 | Not covered by any plan |
| 10 | Add performance/load testing to Phase 5 | Not covered by any plan |

---

## 7. Appendix: Source Plan References

### Plans Evaluated

| # | Agent | Run ID | Path |
|---|-------|--------|------|
| 1 | Claude-Opus-4-5 | 20260204-0212-b214408d | `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Claude-Opus-4-5.20260204-0212-b214408d.md` |
| 2 | Gemini-CLI | 20260204-0221-gemini | `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Gemini-CLI.20260204-0221-gemini.md` |
| 3 | Codex | 20260204-021313-1158 | `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Codex.20260204-021313-1158.md` |

### Issues Register

| Source | Path |
|--------|------|
| V2 Issues Register | `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT_V2.md` |

---

*PASS 1 Evaluation completed by Claude-Opus-4-5 on 2026-02-04. Ready for PASS 2 synthesis.*
