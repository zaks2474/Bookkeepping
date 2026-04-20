# LAYER 1: INFRASTRUCTURE TRUTH — COMPLETION REPORT

## Timestamp
2026-02-08T22:22:00Z

## Status
COMPLETE

## Gate Results

| Gate | Result | Evidence Location |
|------|--------|-------------------|
| L1-1 | PASS | Only `zakops-backend-postgres-1` on port 5432 running for deal data (+ 2 separate legitimate DBs: agent-db, rag-db) | post-state/docker-ps.txt |
| L1-2 | PASS | `zakops-postgres` container stopped, removed. Volumes `docker_postgres_data` and `docker_postgres-data` destroyed. Zero containers matching 5435. | post-state/docker-ps.txt |
| L1-3 | PASS | `infra/docker/docker-compose.postgres.yml` and `infra/docker/docker-compose.yml` replaced with deprecation notices. `Zaks-llm/docker-compose.deal-engine.yml` and `src/deal_origination/docker-compose.deal-engine.yml` also decommissioned. |
| L1-4 | PASS | Zero 5435 references in application code across all 3 repos. Remaining matches are only in venv/node_modules (third-party packages). |
| L1-5 | PASS | `zakops-backend/docker-compose.yml` defines ONE postgres service. Rogue compose files decommissioned. |
| L1-6 | PASS | Agent API DSN: `postgresql://agent:agent_secure_pass_123@db:5432/zakops_agent` — connects to separate agent DB, no 5435 reference. |
| L1-7 | PASS | RAG service DSN: `postgresql://postgres:crawl4aipass@rag-db:5432/crawlrag` — connects to separate RAG DB, no 5435 reference. |
| L1-8 | PASS | `GET /health` returns `database: {dbname: "zakops", user: "zakops", host: "172.23.0.3", port: 5432}` | post-state/health-endpoint.json |
| L1-9 | PASS | Backend logs show `DSN gate check: db=zakops, user=zakops` → `DSN gate PASSED`. Code raises `RuntimeError` if `current_database() != 'zakops'`. |
| L1-10 | PASS | Canonical DSN documented in `/home/zaks/bookkeeping/docs/CANONICAL-DATABASE.md` |

## Items Completed

1. **Fixed `.env`**: `DATABASE_URL` changed from `dealengine:changeme@localhost:5435` to `zakops:zakops_dev@localhost:5432`
2. **Fixed `adapter.py`**: Default fallback DSN updated to canonical
3. **Fixed `main.py`**: Default fallback DSN updated to canonical
4. **Fixed 8 migration/utility scripts**: All `5435/dealengine` references → `5432/zakops`
5. **Fixed `agent_invocation.py`**: DSN updated
6. **Fixed `zakops-api.service`**: Systemd service file DSN updated
7. **Fixed `Zaks-llm/src/deal_origination/config.py`**: DSN updated
8. **Killed rogue container**: `zakops-postgres` stopped and removed
9. **Destroyed rogue volumes**: `docker_postgres_data` and `docker_postgres-data` removed
10. **Removed stopped legacy container**: `zakops-postgres-1` (exited)
11. **Decommissioned 4 compose files**: Replaced with deprecation notices
12. **Added startup DSN gate**: `lifespan()` verifies `current_database() == 'zakops'` before accepting traffic
13. **Added DB identity to health endpoint**: `GET /health` now includes `database` object
14. **Created canonical DSN documentation**: `/home/zaks/bookkeeping/docs/CANONICAL-DATABASE.md`
15. **Rebuilt and restarted backend**: Confirmed healthy with new DSN

## Items Deferred
None.

## Issues Discovered During Execution

1. **Backend `.env` was pointing to rogue DB all along**: `DATABASE_URL=postgresql://dealengine:changeme@localhost:5435/zakops`. However, the Docker Compose file overrides this with the correct DSN (`postgres:5432`) for containerized execution. So the running backend was actually connected to the canonical DB — but any bare-process execution would hit the rogue.
2. **`adapter.py` and `main.py` both had hardcoded 5435 fallback DSNs**: These would be used if `DATABASE_URL` env var was unset.
3. **11 total files contained 5435 references**: All fixed.

## Dependencies Verified
Layer 1 has no dependencies (foundation layer).

## Second-Pass Confirmation

Re-verified all gates:
- `docker ps -a | grep 5435` → empty (PASS)
- `docker volume ls | grep docker_postgres` → empty (PASS)
- `curl localhost:8091/health | jq .database` → `{dbname: "zakops", user: "zakops", port: 5432}` (PASS)
- Backend logs show DSN gate passed (PASS)
- `grep -r 5435 zakops-backend/ --include="*.py" --include="*.env"` → only venv matches (PASS)
