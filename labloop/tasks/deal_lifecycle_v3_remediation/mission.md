# Mission: DEAL LIFECYCLE V3 FULL REMEDIATION (All Phases)

## Objective

Implement the **complete DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL** covering all 22 issues across 7 phases (69 tasks total), eliminating the split-brain architecture and establishing PostgreSQL as the single source of truth.

**Source Plan:** `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.md`

## Critical Context

The ZakOps system has a **split-brain architecture** that must be eliminated:
- PostgreSQL `zakops.deals` is used by Dashboard/API (DL-XXXX IDs)
- JSON `deal_registry.json` is used by email ingestion/executors (DEAL-YYYY-### IDs)
- These never sync, causing data inconsistency

**22 issues documented:** 2 P0, 6 P1, 11 P2, 3 P3

## Locked Decisions (DO NOT DEVIATE)

1. **D-FINAL-01:** PostgreSQL `zakops.deals` is the SOLE source of truth
2. **D-FINAL-02:** Keep 9-stage canonical model (inbound, screening, qualified, loi, diligence, closing, portfolio, junk, archived)
3. **D-FINAL-03:** Agent calls backend HTTP APIs ONLY (no direct DB)
4. **D-FINAL-04:** Email ingestion POSTs to `/api/quarantine`
5. **D-FINAL-05:** Central RAG service with deal_id keying
6. **D-FINAL-06:** Mirror HITL approvals to backend with correlation_id
7. **D-FINAL-07:** API key for services; user JWT in Phase 5; correlation_id in Phase 0

---

## PHASE 0: Stop the Bleeding

**Issues:** ZK-ISSUE-0006, 0007, 0010, 0011, 0012, 0018

| Task | Description | File |
|------|-------------|------|
| T0.1 | Fix Dashboard quarantine endpoint `/resolve` → `/process` | `apps/dashboard/src/lib/api.ts` |
| T0.2 | Fix Dashboard notes endpoint path | `apps/dashboard/src/lib/api.ts` |
| T0.3 | Add `/api/deals/{id}/notes` endpoint | `zakops-backend/src/api/orchestration/main.py` |
| T0.4 | DELETE deal_state_machine.py | `/home/zaks/scripts/deal_state_machine.py` |
| T0.5 | Update DB default stage `lead` → `inbound` | `db/migrations/` |
| T0.6 | Add correlation_id generation in Dashboard | `apps/dashboard/src/middleware.ts` |
| T0.7 | Add correlation_id reading in backend | `zakops-backend/src/api/orchestration/main.py` |
| T0.8 | Add correlation_id column to deal_events | `db/migrations/` |
| T0.9 | Verify RAG health, document | `SERVICE-CATALOG.md` |
| T0.10 | Add health check aggregator | `zakops-backend/src/api/orchestration/routers/health.py` |
| T0.11 | Fix Zod schemas with `.passthrough()` | `apps/dashboard/src/lib/schemas.ts` |
| T0.12 | Add schema validation logging | `apps/dashboard/src/lib/api.ts` |

---

## PHASE 1: Data Truth Unification

**Issues:** ZK-ISSUE-0001 (P0), 0008, 0014

| Task | Description | File |
|------|-------------|------|
| T1.1 | Create id_map table for legacy ID mapping | `db/migrations/xxx_id_map.sql` |
| T1.2 | Create migration script JSON→Postgres | `scripts/migrations/migrate_json_to_postgres.py` |
| T1.3 | Run migration dry-run with validation | N/A |
| T1.4 | Refactor CreateDealFromEmailExecutor to use backend API | `zakops-backend/src/actions/executors/deal_create_from_email.py` |
| T1.5 | Remove sys.path hack from executor | Same file |
| T1.6 | Migrate action engine SQLite→Postgres | `zakops-backend/src/actions/engine/store.py` |
| T1.7 | Make deal_registry.json read-only | Filesystem |
| T1.8 | Add CI guard blocking legacy writes | `.github/workflows/ci.yml` |
| T1.9 | Run production migration | N/A |

---

## PHASE 2: Contract Alignment

**Issues:** ZK-ISSUE-0003 (P1), 0004, 0013, 0022

| Task | Description | File |
|------|-------------|------|
| T2.1 | Wire quarantine approval → deal creation (atomic) | `zakops-backend/src/api/orchestration/main.py` |
| T2.2 | Add folder scaffolding hook to POST /api/deals | New service |
| T2.3 | Add idempotency guard on quarantine approval | Same |
| T2.4 | Implement /api/actions/capabilities | `zakops-backend/src/api/orchestration/routers/actions.py` |
| T2.5 | Implement /api/actions/metrics | Same |
| T2.6 | Add /api/deals/{id}/archive endpoint | `zakops-backend/src/api/orchestration/main.py` |
| T2.7 | Add /api/deals/{id}/restore endpoint | Same |
| T2.8 | Sync OpenAPI spec | `openapi.yaml` |
| T2.9 | Generate API client from OpenAPI | `apps/dashboard/src/lib/generated/` |

---

## PHASE 3: Deal Lifecycle Correctness

**Issues:** ZK-ISSUE-0009, 0015, 0016

| Task | Description | File |
|------|-------------|------|
| T3.1 | Add create_deal agent tool with HITL | `apps/agent-api/app/core/langgraph/tools/deal_tools.py` |
| T3.2 | Add add_note agent tool | Same |
| T3.3 | Pass X-Correlation-ID in all tool calls | Same + HTTP client |
| T3.4 | Add duplicate detection to POST /api/deals | `zakops-backend/src/api/orchestration/main.py` |
| T3.5 | Add background job for approval expiry | `apps/agent-api/app/jobs/expire_approvals.py` |
| T3.6 | Add optimistic locking on approval | `apps/agent-api/app/services/approval.py` |
| T3.7 | Mirror approvals to backend approval_audit | `db/migrations/xxx_approval_audit.sql` |

---

## PHASE 4: Deal Knowledge System

**Issues:** ZK-ISSUE-0002 (P0), 0019, 0020, 0021

| Task | Description | File |
|------|-------------|------|
| T4.1 | Refactor email ingestion Stage 4 → POST /api/quarantine | `scripts/email_ingestion/stage_4_persist.py` |
| T4.2 | Add idempotency key table | `db/migrations/xxx_ingestion_idempotency.sql` |
| T4.3 | Add attachment scanning | Ingestion service |
| T4.4 | Test email ingestion dry-run | N/A |
| T4.5 | Enable email ingestion cron | `/etc/cron.d/dataroom-automation` |
| T4.6 | Wire deal_append_email_materials executor | `zakops-backend/src/actions/executors/deal_append_email_materials.py` |
| T4.7 | Wire deal_enrich_materials executor | `zakops-backend/src/actions/executors/deal_enrich_materials.py` |
| T4.8 | Wire rag_reindex_deal executor | `zakops-backend/src/actions/executors/rag_reindex_deal.py` |
| T4.9 | Add last_indexed_at + content_hash columns | Migration |
| T4.10 | Add deal indexing hook on create/update | Deal service |
| T4.11 | Add RAG reindex retry queue | `zakops-backend/src/services/queue.py` |
| T4.12 | Implement SSE endpoint | `routers/events.py` |
| T4.13 | Add deal age tracking field | Migration |
| T4.14 | Add basic scheduled reminders | Scheduler service |

---

## PHASE 5: Hardening

**Issues:** ZK-ISSUE-0005 (P1), 0017

| Task | Description | File |
|------|-------------|------|
| T5.1 | Add user authentication to Dashboard | `apps/dashboard/src/` |
| T5.2 | Add auth middleware | `middleware.ts` |
| T5.3 | Pass user ID in backend requests | API client |
| T5.4 | Add user attribution to deal_events | Event service |
| T5.5 | Define retention policy document | `/home/zaks/bookkeeping/docs/RETENTION_POLICY.md` |
| T5.6 | Implement retention cleanup job | Scheduler |
| T5.7 | Add request tracing | Middleware |
| T5.8 | Add performance monitoring | Metrics service |
| T5.9 | Add error alerting | Alert rules |
| T5.10 | Add token rotation runbook | Documentation |

---

## PHASE 6: Legacy Decommission

**Issues:** Final verification of all 22 issues

| Task | Description | File |
|------|-------------|------|
| T6.1 | DELETE deal_registry.json | `/home/zaks/DataRoom/.deal-registry/deal_registry.json` |
| T6.2 | DELETE deal_registry.py | `/home/zaks/scripts/deal_registry.py` |
| T6.3 | DELETE deal_state_machine.py | `/home/zaks/scripts/deal_state_machine.py` |
| T6.4 | DELETE deal_lifecycle/ directory | `zakops-backend/src/api/deal_lifecycle/` |
| T6.5 | Remove SQLite state DB path from code | Config cleanup |
| T6.6 | Verify no legacy references | ripgrep scan |
| T6.7 | Update SERVICE-CATALOG.md | Documentation |
| T6.8 | Run full regression test suite | CI/CD |
| T6.9 | Final 22-issue checklist verification | This document |
| T6.10 | Record in CHANGES.md | `/home/zaks/bookkeeping/CHANGES.md` |

---

## Execution Order

**CRITICAL: Phases must be executed IN ORDER due to dependencies.**

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
```

## Key Repositories

| Repo | Path |
|------|------|
| Backend | `/home/zaks/zakops-backend/` |
| Agent API | `/home/zaks/zakops-agent-api/apps/agent-api/` |
| Dashboard | `/home/zaks/zakops-agent-api/apps/dashboard/` |
| Scripts | `/home/zaks/scripts/` |

## References

- **Full Plan:** `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.md`
- **Issues Register:** `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT_V2.md`

## Safety Constraints

- Max 25 files per cycle
- Max 1500 lines per cycle
- NO dual-write period
- All agent tools must include X-Correlation-ID
- HITL required for create_deal and transition_deal
- DataRoom folders are derived, NOT sources of truth
