# Canonical Database Configuration

## Single Source of Truth

**There is exactly ONE PostgreSQL database for deal data in the ZakOps platform.**

| Property | Value |
|----------|-------|
| **Container** | `zakops-backend-postgres-1` |
| **Image** | `postgres:15-alpine` |
| **Host Port** | `5432` |
| **Database** | `zakops` |
| **Schema** | `zakops` |
| **User** | `zakops` |
| **Password** | `zakops_dev` |
| **DSN** | `postgresql://zakops:zakops_dev@localhost:5432/zakops` |
| **Docker-internal DSN** | `postgresql://zakops:zakops_dev@postgres:5432/zakops` |
| **Volume** | `zakops_postgres_data` |
| **Defined in** | `/home/zaks/zakops-backend/docker-compose.yml` |

## Other Databases (Separate Instances)

| Database | Container | Port | Purpose |
|----------|-----------|------|---------|
| `zakops_agent` | `zakops-agent-db` | Docker-internal only | LangGraph checkpoints, agent state |
| `crawlrag` | `rag-db` | `5434` | RAG vector store (web content, NOT deal data) |

## Protection Mechanisms

1. **Startup DSN Gate**: Backend refuses to start if `current_database()` is not `zakops`
2. **Health Endpoint**: `GET /health` reports `database.dbname`, `database.user`, `database.port`
3. **Decommissioned compose files**: `infra/docker/docker-compose*.yml` contain only deprecation notices
4. **Port 5435 is FORBIDDEN**: No service may bind to or reference port 5435

## History

- **Before 2026-02-08**: A rogue `zakops-postgres` container on port 5435 (user: `dealengine`) existed alongside the canonical DB on port 5432. This caused split-brain data divergence (49 vs 51 deals, different stage distributions).
- **2026-02-08**: DEAL-INTEGRITY-UNIFIED Layer 1 destroyed the rogue container and all its volumes. All DSN references fixed to canonical.

See ADR-002 for the full rationale.
