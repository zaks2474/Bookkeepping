# DEAL-INTEGRITY-001 — PIPELINE WORKSPACE (APPEND-ONLY)

## PASS 1 — Run Index Entry
- **Run ID:** 20260208T160103Z
- **Agent:** Claude Code (Opus 4.6)
- **Pass:** 1 (INVESTIGATE → REPORT → STOP)
- **Report:** `DEAL-INTEGRITY-001.PASS1.CloudCode.20260208T160103Z.md`
- **Evidence dir:** `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-001/evidence/00-forensics/`
- **Status:** COMPLETE
- **Summary:** All 6 issues root-caused. Fundamental defect: 3 conflated archive mechanisms (status/stage/deleted) with no lifecycle state machine. Archive endpoint only sets stage='archived', leaves status='active' and deleted=false. Every downstream surface inherits the confusion differently.
- **Issues confirmed:**
  1. Count disagreement: API returns 37 non-deleted (incl. 6 archived-stage), surfaces count different subsets
  2. Pipeline sum mismatch: /hq PIPELINE_STAGES excludes 'archived'/'junk', header=37 but cards sum=31
  3. Archived in active: archive endpoint only sets stage, not status or deleted
  4. Zod error: Promise.all without per-function error boundaries; quarantine/agent endpoints intermittently fail
  5. UI creation: works correctly, "propagation" issue is perception caused by count mismatches
  6. Active filter no-op: status column is always 'active', filter returns everything
- **Bonus findings:** audit_trail column referenced but missing from schema; /api/actions/kinetic returns 500
- **Recommended fix order:** Issue 3 → 1 → 2 → 6 → 4 → 5
---
## PASS 1 RUN — Codex — 20260208-1015-c1xh
- report_path: /home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001.PASS1.Codex.20260208-1015-c1xh.md
- top_findings: split-brain DB (backend uses postgres:5432, ops queries 5435); /api/deals returns 37 while DB shows 51; archived deals have status=active; pipeline totals exclude archived stage; /api/agent/activity returns [] vs schema expects object
- confirmed_root_causes: backend DB != ops DB; archive sets stage only (status remains active); HQ pipeline excludes archived stage while total includes it; /api/agent/activity schema mismatch
- highest_leverage_fix_theme: enforce single canonical DB + unify “active” semantics (status/stage/deleted) across API/UI/pipeline.
- needs_operator_decisions: choose canonical DB DSN; decide whether archived is stage or status; decide whether active filter excludes archived or shows it as separate stage.
---

---
## PASS 1 RUN — CloudCode — 20260208-0500-pass1
- report_path: /home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001.PASS1.CloudCode.20260208-0500-pass1.md
- top_findings:
  - Split-Brain DBs: Port 5432 (Real) vs Port 5435 (Rogue).
  - Status/Stage Conflation: Archived deals are status='active'.
  - Pipeline Sum Mismatch: Archived deals counted in header but hidden in columns.
  - Zod Error: Archived deals leaking into active view cause schema mismatch.
  - Creation Propagation: UI writes to one DB, Agent reads from another.
- confirmed_root_causes:
  - Multiple Postgres containers.
  - Archive logic updates stage only.
  - API default filter matches archived deals.
- highest_leverage_fix_theme: Infrastructure Unification & Data Model Cleanup.
- needs_operator_decisions:
  - Confirm 'Archive' behavior vs 'Soft Delete' behavior.
---
## PASS 2 RUN — Codex — 20260208-1025-q1zg
- report_path: /home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001.PASS2.Codex.20260208-1025-q1zg.md
- deduped_issue_count: 7
- top_systemic_root_causes: split-brain DB/DSN mismatch; lifecycle semantics conflation (status/stage/deleted)
- biggest_conflicts_to_resolve: DB counts 49 vs 51 vs 37; exact HQ “1 Issue” badge trigger; backend DB accessibility at postgres:5432
---

---
## PASS 2 RUN — CloudCode — 20260208-1700-pass2
- report_path: /home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001.PASS2.CloudCode.20260208-1700-pass2.md
- deduped_issue_count: 6
- top_systemic_root_causes:
  - Lifecycle State Fragmentation (status/stage/deleted mismatch).
  - Infrastructure Split-Brain (DB-5432 vs DB-5435).
- biggest_conflicts_to_resolve:
  - Agent Activity Schema (Array vs Object) - Codex's finding is likely correct.

---
## PASS 2 RUN — CloudCode — 20260208T162638Z
- report_path: /home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001.PASS2.CloudCode.20260208T162638Z.md
- deduped_issue_count: 9
- top_systemic_root_causes:
  - **A: Incoherent Deal Lifecycle State Machine** — 3 state signals (status/stage/deleted) with no enforced coupling. Archive endpoint updates only stage, leaving status='active'. Cascades into 5 observable symptoms (DI-ISSUE-001→004, 007).
  - **B: Split-Brain Database Infrastructure** — Two Postgres containers (5432 vs 5435) with divergent data (49 vs 51 deals). Cross-service data invisibility (DI-ISSUE-006, 007).
- biggest_conflicts_to_resolve:
  - **Split-brain existence**: CC3 did not investigate; Codex+CC1 both confirm. Resolution: verify with `docker ps | grep postgres`.
  - **Zod error root cause**: 3 theories (Promise.all fragility / agent activity schema mismatch / archived deal field gaps). All may coexist. Resolution: test each endpoint response shape + run HQ with DevTools.
  - **Propagation root cause**: CC3 says perception issue; Codex+CC1 say split-brain. Both partially correct. Resolution: create test deal, verify across both DBs.
  - **Archived count 6 vs 4**: Explained by split-brain (different DBs queried). Canonical = 6 (from DB 5432).
---
