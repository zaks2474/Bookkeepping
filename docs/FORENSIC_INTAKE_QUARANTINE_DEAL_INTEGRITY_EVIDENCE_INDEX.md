# Evidence Pack Index — Forensic Intake/Quarantine/Deal Integrity Audit

## 1. Database & Schema
| Component | File Path | Lines | Description |
|---|---|---|---|
| Deal schema | `/home/zaks/zakops-backend/db/init/001_base_tables.sql` | 19-48 | Canonical deals table in `zakops` DB |
| Quarantine schema | `/home/zaks/zakops-backend/db/init/001_base_tables.sql` | 210-236 | Quarantine items table (missing correlation_id) |
| Email schema | `/home/zaks/zakops-backend/db/migrations/022_email_integration.sql` | 13-88 | Email accounts, threads, messages tables |
| Agent schema | `/home/zaks/zakops-agent-api/apps/agent-api/schema.sql` | 1-28 | Agent DB (user, session, thread only - no deals) |

## 2. Ingestion Pipeline (Broken)
| Component | File Path | Lines | Description |
|---|---|---|---|
| Missing Package | `/home/zaks/zakops-backend/src/workers/actions_runner.py` | 44-48 | Import of `email_ingestion` fails (package missing) |
| Quarantine Create | `/home/zaks/zakops-backend/src/api/orchestration/main.py` | 1483-1552 | Endpoint `POST /api/quarantine` exists but relies on manual calls |

## 3. Quarantine Operations
| Component | File Path | Lines | Description |
|---|---|---|---|
| List Quarantine | `/home/zaks/zakops-backend/src/api/orchestration/main.py` | 1374-1435 | `GET /api/quarantine` endpoint |
| Process/Approve | `/home/zaks/zakops-backend/src/api/orchestration/main.py` | 1591-1715 | `POST /api/quarantine/{id}/process` (atomic approval) |
| MCP Tools | `/home/zaks/zakops-backend/mcp_server/server.py` | 100-150 | MCP exposes `list_quarantine`, `approve_quarantine` |

## 4. Configuration & Env
| Component | File Path | Lines | Description |
|---|---|---|---|
| Backend DB URL | `/home/zaks/zakops-backend/.env` | 1 | `DATABASE_URL` for `zakops` DB |
| Agent DB URL | `/home/zaks/zakops-agent-api/apps/agent-api/.env.example` | 1 | `DATABASE_URL` for `zakops_agent` DB |
