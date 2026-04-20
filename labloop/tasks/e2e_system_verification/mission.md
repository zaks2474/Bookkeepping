# MISSION: End-to-End System Verification & Integration QA
## Post-Decommission Validation with Rigorous Gates

**Mission ID:** E2E-VERIFY-001
**Date:** 2026-01-26
**Priority:** CRITICAL
**Prerequisite:** LEGACY-DECOM-001 COMPLETE

---

## Mission Objective

Perform exhaustive end-to-end verification of the clean ZakOps architecture to:

1. **Verify all service interconnections** are correctly configured
2. **Test data flow** through the entire system (Dashboard → Agent API → Backend → Database)
3. **Validate RAG integration** with the LangGraph agent
4. **Identify and FIX** any issues discovered
5. **Achieve production-ready state** with documented evidence

---

## Architecture Under Test

```
Dashboard (3003)
    │
    ├── NEXT_PUBLIC_API_URL ──────► Backend (8091) ──► PostgreSQL (5432)
    │
    └── NEXT_PUBLIC_AGENT_API_URL ─► Agent API (8095) ──► RAG (8052) ──► rag-db (5434)
```

## Connections to Verify

| Connection | Source | Target | Port | Env Variable |
|------------|--------|--------|------|--------------|
| [A] | Dashboard | Backend | 8091 | NEXT_PUBLIC_API_URL |
| [B] | Dashboard | Agent API | 8095 | NEXT_PUBLIC_AGENT_API_URL |
| [C] | Backend | PostgreSQL | 5432 | DATABASE_URL |
| [D/E] | Agent API | Backend | 8091 | BACKEND_URL |
| [F] | Agent API | Agent DB | internal | DATABASE_URL |
| [G] | RAG API | rag-db | 5434 | POSTGRES_URL |

## Gate Requirements

All 6 gates must PASS:
- Gate 0: Pre-flight (all services up, no ghosts on port 8090)
- Gate 1: Environment configuration correct
- Gate 2: All service connections working
- Gate 3: Database schemas valid and queryable
- Gate 4: End-to-end functional tests pass
- Gate 5: No issues remaining or all auto-fixed

## Deliverables

1. Verification report at `/home/zaks/bookkeeping/docs/E2E_VERIFICATION_REPORT_*.md`
2. All gates passing
3. Any identified issues fixed
