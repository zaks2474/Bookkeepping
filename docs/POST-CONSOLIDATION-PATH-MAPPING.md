# Post-Consolidation Path Mapping

**Date:** 2026-02-16
**Triggered by:** MONOREPO-CONSOLIDATION-001 (zakops-backend merged into zakops-agent-api monorepo)
**RCA:** `POST-MERGE-INCIDENT-RCA-2026-02-16.md`

---

## Path Translation Table

| Old Path (Pre-Consolidation) | New Path (Post-Consolidation) |
|------------------------------|-------------------------------|
| `/home/zaks/zakops-backend/` | `/home/zaks/zakops-agent-api/apps/backend/` |
| `/home/zaks/zakops-backend/src/` | `/home/zaks/zakops-agent-api/apps/backend/src/` |
| `/home/zaks/zakops-backend/db/` | `/home/zaks/zakops-agent-api/apps/backend/db/` |
| `/home/zaks/zakops-backend/mcp_server/` | `/home/zaks/zakops-agent-api/apps/backend/mcp_server/` |
| `/home/zaks/zakops-backend/scripts/` | `/home/zaks/zakops-agent-api/apps/backend/scripts/` |
| `/home/zaks/zakops-backend/tests/` | `/home/zaks/zakops-agent-api/apps/backend/tests/` |
| `/home/zaks/zakops-backend/shared/openapi/` | `/home/zaks/zakops-agent-api/packages/contracts/openapi/` |
| `/home/zaks/zakops-backend/.env` | `/home/zaks/zakops-agent-api/apps/backend/.env` |
| `/home/zaks/zakops-backend/docker-compose.yml` | `/home/zaks/zakops-agent-api/docker-compose.yml` (unified) |

## Container Name Changes

| Old Container | New Container |
|---------------|---------------|
| `zakops-backend-postgres-1` | `zakops-postgres-1` |
| `zakops-backend-backend-1` | `zakops-backend-1` |

## Docker Compose Changes

| Old Command | New Command |
|-------------|-------------|
| `cd /home/zaks/zakops-backend && docker compose up -d backend` | `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose up -d backend` |
| `cd /home/zaks/zakops-backend && docker compose build backend` | `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend` |
| `docker exec zakops-backend-postgres-1 psql ...` | `docker exec zakops-postgres-1 psql ...` |

## Port Changes

| Service | Old Port | New Port | Notes |
|---------|----------|----------|-------|
| Claude Code API | 8090 | N/A | **DECOMMISSIONED** — replaced by Agent API at 8095 |
| Dashboard | 3000 | 3003 | Active Next.js dashboard |
| Backend API | 8091 | 8091 | Unchanged |
| Agent API | 8095 | 8095 | Unchanged |

## Repository Status

| Repository | Path | Status |
|-----------|------|--------|
| `zakops-agent-api` | `/home/zaks/zakops-agent-api/` | **ACTIVE** — monorepo (dashboard, agent-api, backend, contracts) |
| `zakops-backend` | `/home/zaks/zakops-backend/` | **ARCHIVED** — merged into monorepo at `apps/backend/` |
| `zakops-dashboard` | `/home/zaks/zakops-dashboard/` | **LEGACY** — stale, do not use |

## Documents with Consolidation Headers

The following historical documents have been annotated with a `POST-CONSOLIDATION NOTE` header:

1. `QA-DI-VERIFY-REMEDIATION-UNIFIED.md` (20+ old path references)
2. `QA-MASTER-PROGRAM-VERIFY-001A.md` (50+ old path references)
3. `QA-LANGSMITH-INTAKE-HARDEN-VERIFY-001.md` (71 old path references)
4. `QA-LANGSMITH-SHADOW-PILOT-VERIFY-001.md` (57 old path references)
5. `QA-COL-DEEP-VERIFY-001C.md` (63 old path references)
6. `QA-ET-VALIDATION-VERIFY-001.md` (25 old path references)

An additional ~300 historical documents in `/home/zaks/bookkeeping/docs/` contain old path references.
These are preserved as historical records — the paths in verification commands reflect the state
at the time those missions were executed. Use this mapping table to translate when re-running commands.

## Active Operational Docs Updated

These documents were directly updated with correct monorepo paths:

1. `/home/zaks/zakops-agent-api/CLAUDE.md` — container name fix
2. `/home/zaks/zakops-agent-api/apps/backend/docs/qa-runbook.md` — commands, ports
3. `/home/zaks/bookkeeping/docs/TRIPASS_SOP.md` — repos flag
4. `/home/zaks/bookkeeping/docs/ONBOARDING.md` — contract surfaces 7 to 17
5. `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md` — decommissioned service, paths
6. `/home/zaks/bookkeeping/docs/RUNBOOKS.md` — decommissioned sections, ports, chat operations
7. `/home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md` — backend paths, compose commands
8. `/home/zaks/bookkeeping/docs/EMAIL-TRIAGE-ALERTING.md` — backend restart command
9. `/home/zaks/bookkeeping/docs/EMAIL-INGESTION-UPGRADE-PLAN.md` — chat backend note
