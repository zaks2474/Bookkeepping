---

## Run Index Entry
- **Agent:** Claude-Opus-4-5
- **Run ID:** 20260204-0212-b214408d
- **Report Path:** /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Claude-Opus-4-5.20260204-0212-b214408d.md
- **Top 10 Priorities:**
  1. Eliminate split-brain persistence (Phase 1 — Postgres as sole source)
  2. Enable email ingestion pipeline (Phase 4 — POST to /api/quarantine)
  3. Wire quarantine approval to deal creation (Phase 2)
  4. Add folder scaffolding to deal creation (Phase 2)
  5. Fix Dashboard endpoint mismatches (Phase 0 — quarantine, notes)
  6. Unify stage taxonomy (Phase 0 — delete deal_state_machine.py)
  7. Add agent create_deal tool with HITL (Phase 3)
  8. Add correlation IDs across systems (Phase 3)
  9. Add Dashboard user authentication (Phase 5)
  10. Decommission legacy JSON/scripts (Phase 6)
- **Decision Set:**
  - **D2.1 Source of Truth:** Postgres `zakops.deals` as sole source (Option A)
  - **D2.2 Stage Taxonomy:** Keep 9-stage canonical model (Option A)
  - **D2.3 Agent Contract:** Agent calls backend HTTP APIs only (Option A)
  - **D2.4 Email Ingestion:** Refactor to POST to `/api/quarantine` (Option A)
  - **D2.5 RAG:** Dedicated crawlrag database with deal update hooks
  - **D2.6 HITL Audit:** Add correlation_id to connect agent and backend events
  - **D2.7 Auth:** Keep API key infrastructure, add user auth in Phase 5

---

## Run Index Entry
- **Agent:** Gemini-CLI
- **Run ID:** 20260204-0221-gemini
- **Report Path:** /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Gemini-CLI.20260204-0221-gemini.md
- **Top 10 Priorities:**
  1. Enable Email Ingestion Cron (Dry Run)
  2. Migrate Deal Registry JSON -> Postgres
  3. Rewrite Deal Creation Executor to use DB
  4. Fix Quarantine Approval -> Deal Creation link
  5. Add Folder Scaffolding to Deal Creation
  6. Add Dashboard Authentication
  7. Fix Dashboard/API Endpoint Mismatches
  8. Unify Stage Taxonomies
  9. Add Agent 'Create Deal' Tool
  10. Decommission Legacy JSON/Scripts
- **Decision Set:**
  - **DB:** Single Source of Truth = PostgreSQL.
  - **Ingestion:** Script calls API; API writes DB.
  - **Auth:** Service Keys + User Sessions.
  - **Model:** API-First; no direct file manipulation by Agents.
# DEAL_LIFECYCLE_REMEDIATION_PLAN_V3 - Run Index

## Run Index Entry — Codex 20260204-021313-1158
- agent_name: Codex
- run_id: 20260204-021313-1158
- plan_path: /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Codex.20260204-021313-1158.md
- top_10_priorities:
  - Unify deal source-of-truth in Postgres (ZK-ISSUE-0001, ZK-ISSUE-0008, ZK-ISSUE-0014)
  - Secure dashboard authentication and user attribution (ZK-ISSUE-0005)
  - Wire quarantine approval to create a deal (ZK-ISSUE-0003)
  - Re-enable email ingestion on canonical path (ZK-ISSUE-0002)
  - Align stage taxonomy and DB defaults (ZK-ISSUE-0007)
  - Fix UI endpoint mismatches (/process, /note) (ZK-ISSUE-0006, ZK-ISSUE-0012)
  - Create DataRoom folders on deal creation (ZK-ISSUE-0004)
  - Add correlation_id across services (ZK-ISSUE-0011)
  - Wire action executors + capabilities/metrics (ZK-ISSUE-0019, ZK-ISSUE-0013)
  - Verify RAG indexing and search_deals reliability (ZK-ISSUE-0010)
- decision_set_recommendations:
  - DB model: single canonical Postgres; all other stores derived/indexed only
  - Email ingestion: cron bridge -> event-driven pipeline; write to Postgres + attachments to DataRoom
  - Auth: OIDC/JWT for users + service tokens for internal services; full user attribution
  - Deal knowledge model: canonical deal record with emails/notes/docs; RAG indexed by deal_id

---

## PASS 3 FINAL — Synthesized Plan

### Run Index Entry — PASS 3 FINAL
- **Agent:** Claude-Opus-4-5
- **Run ID:** 20260204-0345-PASS3-FINAL
- **Pass Type:** PASS 3 (FINAL SYNTHESIS)
- **Report Path:** /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.md
- **JSON Path:** /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.json

### Source Plans Synthesized:
| Source | Agent | Run ID | Score |
|--------|-------|--------|-------|
| V3 Plan | Claude-Opus-4-5 | 20260204-0212-b214408d | 28/30 |
| V3 Plan | Gemini-CLI | 20260204-0221-gemini | 23/30 |
| V3 Plan | Codex | 20260204-021313-1158 | 29/30 |
| PASS 1 | Claude-Opus-4-5 | 20260204-0304-24645315 | Coverage Analysis |
| PASS 2 | Codex | 20260204-0310-5abffd | Red-Team Patches |

### Final Decision Set (Locked):
1. **D-FINAL-01:** Postgres `zakops.deals` as SOLE source of truth
2. **D-FINAL-02:** Keep 9-stage canonical model from workflow.py
3. **D-FINAL-03:** Agent calls backend HTTP APIs ONLY
4. **D-FINAL-04:** Email ingestion POSTs to `/api/quarantine`
5. **D-FINAL-05:** Central RAG service with deal_id keying + consistency contract
6. **D-FINAL-06:** Mirror approvals to backend with correlation_id
7. **D-FINAL-07:** API key for services; user JWT in Phase 5; correlation_id in Phase 0

### Final Metrics:
- **Total Issues Covered:** 22/22 (100%)
- **Total Tasks:** 68 atomic tasks
- **Total Phases:** 7 (Phase 0-6)
- **RT Gates:** 6 red-team verification gates
- **QA Passes:** 2 (functional + adversarial)
- **Estimated Duration:** 40-58 developer-days

### Top 10 Priorities (Final):
1. Eliminate split-brain persistence (Phase 1 — RT-DB-SOT gate)
2. Enable email ingestion pipeline (Phase 4 — with safety spec)
3. Wire quarantine approval to atomic deal creation (Phase 2)
4. Add folder scaffolding + DataRoom path storage (Phase 2)
5. Add correlation_id tracing across all services (Phase 0)
6. Fix all endpoint mismatches (Phase 0 — quarantine, notes)
7. Unify stage taxonomy (Phase 0 — delete legacy, fix DB default)
8. Add agent create_deal tool with HITL (Phase 3)
9. Add Dashboard user authentication (Phase 5)
10. Decommission legacy and prove clean (Phase 6)

---
