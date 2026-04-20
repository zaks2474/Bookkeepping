# V-L1.4: Docker-Compose Files -- No Secondary Postgres
**VERDICT: PASS (with caveats)**

## Evidence
All compose files were scanned across MONOREPO, BACKEND_ROOT, ZAKS_LLM_ROOT.

### Secondary Postgres definitions found (non-production):
- `deployments/bluegreen/compose.green.yml` / `compose.blue.yml` -- blue/green deployment templates (not active)
- `deployments/docker/compose.restore.yml` -- restore utility on port 15432 (not active)
- `deployments/demo/compose.demo.yml` -- demo environment (not active)
- `apps/agent-api/docker-compose.yml` -- agent-api has its own `db` service for `zakops_agent` DB (separate, expected)
- `docker-compose.temporal.yml` in Zaks-llm -- Temporal workflow DB (separate purpose)

### Decommissioned files (properly documented):
- `zakops-backend/infra/docker/docker-compose.postgres.yml` -- Contains comment: "This file previously defined a secondary PostgreSQL container on port 5435... Canonical database: zakops-backend-postgres-1 on port 5432"
- `zakops-backend/infra/docker/docker-compose.yml` -- Same decommission notice
- `Zaks-llm/docker-compose.deal-engine.yml` -- "The deal-engine-db container on port 5435 has been permanently destroyed"

### Active production Postgres:
Only `zakops-backend/docker-compose.yml` defines the canonical Postgres service on port 5432.

No active secondary Postgres service competing with the canonical database.
