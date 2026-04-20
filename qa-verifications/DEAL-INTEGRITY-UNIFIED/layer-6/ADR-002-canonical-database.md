# ADR-002: Canonical Database — Single Source of Truth

| Field       | Value                          |
|-------------|--------------------------------|
| Status      | **Accepted**                   |
| Date        | 2026-02-08                     |
| Mission     | DEAL-INTEGRITY-UNIFIED         |
| Layer       | 6 — Governance                 |
| Deciders    | Zak (owner), Claude (advisor)  |

## Context

During the DEAL-INTEGRITY-UNIFIED mission, investigation revealed that ZakOps
was running **two** PostgreSQL containers simultaneously:

| Container                    | Port | Database | Deal Count |
|------------------------------|------|----------|------------|
| `zakops-backend-postgres-1`  | 5432 | `zakops` | 49         |
| Rogue container              | 5435 | `zakops` | 51         |

The backend `.env` file pointed to the **rogue** database on port 5435, meaning
all API reads/writes were hitting a divergent data store. The dashboard (via the
API) displayed 51 deals from the rogue DB, while the canonical DB on 5432 had
only 49. This split-brain condition caused:

- **Data divergence**: 2 deals existed only in the rogue DB.
- **Silent corruption risk**: Migrations applied to one DB but not the other.
- **Debugging confusion**: Queries against `psql` on 5432 returned different
  results than the running application.

## Decision

**Single canonical database: `zakops` on `zakops-backend-postgres-1`, port 5432.**

All other PostgreSQL containers and compose files that spawn secondary databases
are destroyed and decommissioned.

### Canonical DSN

```
# From host
postgresql://zakops:zakops_dev@localhost:5432/zakops

# From Docker network (service-to-service)
postgresql://zakops:zakops_dev@postgres:5432/zakops
```

### Protection Mechanisms

1. **Startup DSN Verification Gate** (`main.py`):
   At application boot, before accepting requests, the backend executes:
   ```sql
   SELECT current_database();
   ```
   If the result is not `'zakops'`, the process exits with a fatal error.
   This prevents silent reconnection to a wrong database.

2. **Health Endpoint DB Identity**:
   The `/health` endpoint includes `db_name` in its response payload, reporting
   the connected database name. Monitoring and smoke tests can assert this value.

3. **Compose File Lockdown**:
   The single `docker-compose.yml` in `zakops-backend/` defines exactly one
   `postgres` service on port 5432. No other compose files may define a
   PostgreSQL service.

## Consequences

### Positive
- **Single source of truth** — no data divergence possible.
- **Simpler operations** — one DB to back up, migrate, and monitor.
- **Auditable** — startup gate and health endpoint provide continuous
  verification.

### Negative / Constraints
- **No local Postgres for testing** — all integration tests must target the
  canonical container. Use transactions + rollback or a dedicated test schema.
- **All services must use the canonical container** — any new service that needs
  PostgreSQL must connect to `zakops-backend-postgres-1:5432/zakops` (or use a
  separate named database within the same container if isolation is required).
- **Port 5435 is permanently blacklisted** — no service may bind to or connect
  to port 5435.

## Compliance

Any PR that modifies `DATABASE_URL`, `POSTGRES_*` environment variables, or
Docker Compose `ports:` mappings for PostgreSQL **must** reference this ADR and
receive explicit approval.
