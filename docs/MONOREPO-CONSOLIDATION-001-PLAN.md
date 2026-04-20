# MONOREPO-CONSOLIDATION-001: Merge zakops-backend into zakops-agent-api

## Context

ZakOps currently spans 4 repositories. The tightest coupling is between `zakops-backend` (FastAPI, port 8091) and `zakops-agent-api` (monorepo: dashboard + agent-api + contracts). Every backend API change requires a 4-step cross-repo sync chain (`make update-spec → sync-types → sync-backend-models → tsc`), and 10 of 17 contract surfaces exist solely to bridge this repo gap. Merging the backend into the monorepo eliminates the highest-friction boundary in the system.

**Scope:** Move `zakops-backend` into `zakops-agent-api/apps/backend/`. Archive the standalone repo.
**Out of scope:** `Zaks-llm` (loosely coupled, GPU-dependent), `bookkeeping` (operational docs).

---

## Pre-Merge Inventory

### What's Moving
| Item | Size | Complexity |
|------|------|-----------|
| Python source (`src/`) | 193 files, 17 routers | HIGH |
| SQL migrations (`db/`) | 31 files + 1 init script | MEDIUM |
| Docker services | postgres, redis, backend, outbox-worker, langfuse | HIGH |
| MCP server (`mcp_server/`) | 538-line FastMCP proxy | LOW |
| Scripts (`scripts/`) | 15 operational scripts | MEDIUM |
| Tests (`tests/`) | 50+ files across 7 categories | MEDIUM |
| OpenAPI spec (`shared/openapi/`) | 83KB zakops-api.json | LOW |
| Requirements | 30+ Python packages | LOW |
| Git history | 43 commits, 6.2MB | LOW |

### What's Staying
| Item | Reason |
|------|--------|
| `Zaks-llm` | Independent lifecycle (GPU, model weights), only Surface 5 connection |
| `bookkeeping` | Operational docs, not code |

---

## Target Monorepo Structure

```
zakops-agent-api/                    ← renamed conceptually to "zakops" (no actual rename needed)
├── apps/
│   ├── dashboard/                   ← Next.js (unchanged, bare process)
│   ├── agent-api/                   ← LangGraph agent (unchanged, Docker)
│   └── backend/                     ← NEW: FastAPI backend (moved from zakops-backend)
│       ├── src/                     ← All Python source
│       ├── db/                      ← Migrations + init scripts
│       │   ├── init/
│       │   └── migrations/
│       ├── mcp_server/              ← MCP server (port 9100)
│       ├── scripts/                 ← Operational scripts
│       ├── tests/                   ← Test suites
│       ├── Dockerfile               ← Backend container build
│       ├── requirements.txt
│       ├── pyproject.toml
│       └── .env.example
├── packages/
│   └── contracts/                   ← OpenAPI specs (unchanged)
│       └── openapi/
│           ├── zakops-api.json      ← Backend spec (was in backend/shared/)
│           ├── agent-api.json
│           └── rag-api.json
├── tools/                           ← Infra validators (unchanged)
├── docker-compose.yml               ← NEW: Unified root compose (postgres + redis)
├── docker-compose.backend.yml       ← NEW: Backend + outbox-worker
├── docker-compose.agent.yml         ← Existing agent compose (moved/renamed)
├── docker-compose.monitoring.yml    ← NEW: Optional monitoring stack
├── .env.example                     ← NEW: Unified env template
├── Makefile                         ← Updated with backend targets
└── CLAUDE.md                        ← Updated
```

---

## RISK ANALYSIS: Worst-Case Scenarios

### RISK 1: PostgreSQL Data Loss
**Severity:** CATASTROPHIC
**Probability:** MEDIUM (if Docker volumes are mishandled)

**Scenario:** Merging docker-compose files creates new volume names. Docker creates fresh empty volumes. Old data becomes orphaned and invisible. You start the system, migrations run on an empty database, and 6 months of deal data is gone.

**Evidence:** Backend uses `zakops_postgres_data` (explicit name). If the merged compose uses a different name or project prefix, Docker won't find the existing volume.

**Mitigation:**
1. **Pre-merge:** `pg_dump -U zakops -d zakops -F c -f /home/zaks/backups/zakops-$(date +%F).dump`
2. **Pre-merge:** `pg_dump -U agent -d zakops_agent -F c -f /home/zaks/backups/zakops_agent-$(date +%F).dump`
3. **Volume strategy:** Use `external: true` volumes in the new compose — Docker won't try to create them:
   ```yaml
   volumes:
     zakops_postgres_data:
       external: true
     zakops_redis_data:
       external: true
   ```
4. **Verification gate:** After merge, query `SELECT count(*) FROM zakops.deals` — must match pre-merge count.

**Recovery:** `pg_restore -U zakops -d zakops /home/zaks/backups/zakops-YYYY-MM-DD.dump`

---

### RISK 2: Docker Network Isolation
**Severity:** HIGH
**Probability:** HIGH (3 different network names exist today)

**Scenario:** Backend container can't reach postgres because they're on different Docker networks. Services start but every API call fails with connection refused. Dashboard shows 502 on every page.

**Evidence:**
- Backend: `zakops_network`
- Agent: `agent-network`
- Monorepo deployment: `zakops-network`

**Mitigation:**
1. Unified compose uses ONE network: `zakops-network`
2. All services join this network
3. Dashboard stays as bare process (no network conflict)
4. Agent container uses `extra_hosts: ["host.docker.internal:host-gateway"]` to reach host services

**Verification gate:** `docker exec zakops-backend-1 curl -sf http://postgres:5432` — must connect.

---

### RISK 3: Port Collisions
**Severity:** HIGH
**Probability:** MEDIUM (if both compose files run simultaneously)

**Scenario:** Old backend compose still running. New monorepo compose tries to bind 5432, 6379. Docker fails with "port already in use". Half the services start, half don't.

**Evidence:** Both compose files map 5432 (postgres) and 6379 (redis).

**Mitigation:**
1. **Phase gate:** `docker compose -f /home/zaks/zakops-backend/docker-compose.yml down` BEFORE starting new compose
2. **Verification:** `ss -tlnp | grep -E '5432|6379|8091'` — must show no listeners before new stack starts
3. **Single compose orchestration:** One `docker compose up` from monorepo root starts everything

**Recovery:** `docker compose down` on both old and new, then start only the new one.

---

### RISK 4: 100+ Path References Break
**Severity:** HIGH
**Probability:** CERTAIN (if paths aren't updated)

**Scenario:** `make sync-rag-models` writes to `../../zakops-backend/src/schemas/rag_models.py` — path doesn't exist. `make update-spec` curls the same port but scripts reference old backend path for validation. Tests fail, sync fails, CI fails.

**Evidence:**
- Makefile line 368: `$$(realpath $(MONOREPO_ROOT)/../zakops-backend)/src/schemas/rag_models.py`
- validate-contract-surfaces.sh line 62: `realpath "$REPO_ROOT/../zakops-backend/src/schemas/rag_models.py"`
- 20+ files with hardcoded `localhost:8091` (these DON'T change — port stays the same)
- 15+ scripts with relative paths assuming backend is repo root

**Mitigation:**
1. **Port stays the same:** 8091 doesn't change. All `localhost:8091` references remain valid.
2. **Makefile paths:** `../zakops-backend/` → `apps/backend/` (3-4 lines to change)
3. **Validator paths:** Same pattern — update `realpath` calls
4. **Backend scripts:** Add `cd "$(dirname "${BASH_SOURCE[0]}")"` to each script for portable path resolution
5. **Verification gate:** `grep -r 'zakops-backend' /home/zaks/zakops-agent-api/ --include='*.sh' --include='Makefile' --include='*.ts' --include='*.py' | grep -v node_modules | grep -v .git` — must return 0 lines (excluding docs)

**Recovery:** Git revert on Makefile + validators.

---

### RISK 5: Environment Variable Collision
**Severity:** MEDIUM
**Probability:** HIGH

**Scenario:** Backend and agent both define `DATABASE_URL` but pointing to different databases. A unified `.env` sets one value. Backend connects to the wrong database, writes deal data into the agent checkpoint tables.

**Evidence:**
- Backend: `DATABASE_URL=postgresql://zakops:zakops_dev@localhost:5432/zakops`
- Agent: `DATABASE_URL=postgresql://agent:agent@localhost:5432/zakops_agent`
- Both in their own `.env` files today — separate. Merging makes collision possible.

**Mitigation:**
1. **Keep separate .env files:** `apps/backend/.env` and `apps/agent-api/.env` continue to exist independently
2. **Root `.env`** only contains shared infra vars: `POSTGRES_PORT`, `REDIS_PORT`, compose project name
3. **Docker compose:** Each service references its own env_file:
   ```yaml
   backend:
     env_file: ./apps/backend/.env
   agent-api:
     env_file: ./apps/agent-api/.env
   ```
4. **Verification gate:** `docker exec zakops-backend-1 env | grep DATABASE_URL` — must show `zakops` db, not `zakops_agent`

---

### RISK 6: Git History Loss
**Severity:** MEDIUM
**Probability:** LOW (if using correct merge strategy)

**Scenario:** Simple `cp -r` loses all 43 commits of backend history. `git log apps/backend/` shows nothing. Blame is useless. Can't trace when a bug was introduced.

**Mitigation:**
1. Use `git subtree add` which preserves full commit history:
   ```bash
   cd /home/zaks/zakops-agent-api
   git subtree add --prefix=apps/backend /home/zaks/zakops-backend main --squash
   ```
   The `--squash` creates a single merge commit but records the source. Without `--squash`, all 43 commits appear in monorepo history.
2. **Alternative:** `git subtree add` without `--squash` for full history preservation
3. **Verification:** `git log --oneline apps/backend/ | wc -l` — must show commits

**Recovery:** Re-run subtree add from the archived repo.

---

### RISK 7: Langfuse Prisma Migration Collision
**Severity:** LOW (Langfuse is already broken)
**Probability:** CERTAIN

**Scenario:** Langfuse shares the backend postgres database and tries to create Prisma migration tables, colliding with the `zakops` schema. Currently exits with code 1.

**Evidence:** `zakops-backend-langfuse-1` — EXITED (1). Logs: `ERROR: relation "_prisma_migrations" already exists`

**Mitigation:**
1. **Option A (recommended):** Give Langfuse its own database: `POSTGRES_DB=langfuse` in compose
2. **Option B:** Drop Langfuse entirely — it's not actively used, just observability infrastructure
3. **Option C:** Fix by creating a `langfuse` schema and configuring Prisma to use it

**Decision needed from user.**

---

### RISK 8: Backend Docker Build Context Changes
**Severity:** MEDIUM
**Probability:** CERTAIN

**Scenario:** Backend Dockerfile uses `COPY . .` which copies the entire build context. If build context changes from `/home/zaks/zakops-backend` to `/home/zaks/zakops-agent-api/apps/backend`, the Dockerfile still works — but `.dockerignore` may need updating, and build times may change if the context accidentally includes `node_modules` from the monorepo.

**Mitigation:**
1. Backend Dockerfile stays in `apps/backend/Dockerfile`
2. Docker compose sets explicit build context:
   ```yaml
   backend:
     build:
       context: ./apps/backend
       dockerfile: Dockerfile
   ```
3. `apps/backend/.dockerignore` — copy from current backend `.dockerignore`
4. **Verification:** `docker compose build backend` succeeds and image size is similar to pre-merge

---

### RISK 9: Migration Auto-Execution on Fresh DB
**Severity:** HIGH
**Probability:** LOW (only on fresh database init)

**Scenario:** Backend compose mounts `db/migrations/` as `/docker-entrypoint-initdb.d/`. On a fresh postgres container, ALL 31 migrations run automatically in alphabetical order. If any migration depends on a previous one and ordering is wrong, the database is corrupted.

**Evidence:** Current volume mount: `./db/migrations:/docker-entrypoint-initdb.d:ro`

**Mitigation:**
1. **Keep the pattern** but update the mount path: `./apps/backend/db/migrations:/docker-entrypoint-initdb.d:ro`
2. Migration files are numbered (000, 001, 016, 018...) and postgres executes them in alphabetical order — this is already working today
3. **Do NOT change migration file names** during the move
4. **Verification:** On a test postgres container, migrations run clean from scratch

---

### RISK 10: Outbox Worker Loses Connection
**Severity:** MEDIUM
**Probability:** MEDIUM

**Scenario:** The outbox-worker is a separate container running `python -m src.core.outbox.runner`. It depends on the backend service being healthy. If the compose dependency chain breaks, outbox events pile up and aren't delivered.

**Mitigation:**
1. Keep `depends_on: backend: condition: service_healthy` in the new compose
2. Outbox worker uses same env_file as backend (`apps/backend/.env`)
3. **Verification:** `docker logs zakops-outbox-worker-1 | tail -5` — no connection errors

---

## Execution Plan

### Phase 0: Backup Everything (15 min, zero risk)

```bash
# Database dumps
pg_dump -U zakops -h localhost -d zakops -F c -f /home/zaks/backups/zakops-pre-merge.dump
pg_dump -U agent -h localhost -d zakops_agent -F c -f /home/zaks/backups/zakops_agent-pre-merge.dump

# Repo archives
tar czf /home/zaks/backups/zakops-backend-pre-merge.tar.gz -C /home/zaks zakops-backend/
tar czf /home/zaks/backups/zakops-agent-api-pre-merge.tar.gz -C /home/zaks zakops-agent-api/

# Docker volume list (for reference)
docker volume ls > /home/zaks/backups/docker-volumes-pre-merge.txt
```

**Gate P0:** All 4 backup files exist and are non-empty.

---

### Phase 1: Prepare Backend Repo (10 min)

```bash
cd /home/zaks/zakops-backend

# Clean build artifacts
rm -rf venv/ __pycache__/ .pytest_cache/ .ruff_cache/ .mypy_cache/
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -delete 2>/dev/null || true

# Remove secrets (never committed, but be safe)
# DO NOT remove .env — it's in .gitignore and won't be copied
```

**Gate P1:** `du -sh /home/zaks/zakops-backend/` shows <50MB (was 333MB with venv).

---

### Phase 2: Git Subtree Merge (5 min)

```bash
cd /home/zaks/zakops-agent-api

# Add backend as subtree with full history
git subtree add --prefix=apps/backend /home/zaks/zakops-backend main --squash
```

**Gate P2:**
- `ls apps/backend/src/api/orchestration/main.py` exists
- `git log --oneline apps/backend/ | head -5` shows commits

---

### Phase 3: Create Unified Docker Compose (30 min)

Create `/home/zaks/zakops-agent-api/docker-compose.yml` (root level) with:

**Shared infrastructure:**
- `postgres` (pg15-alpine, port 5432, volume `zakops_postgres_data: external: true`)
- `redis` (redis7-alpine, port 6379, volume `zakops_redis_data: external: true`)

**Backend services:**
- `backend` (build context `./apps/backend`, port 8091, env_file `./apps/backend/.env`)
- `outbox-worker` (same build, different command, depends on backend)

**Agent services:**
- `agent-db` (pgvector:pg16, port 5433 to avoid conflict, volume `agent-postgres-data: external: true`)
- `agent-api` (build context `./apps/agent-api`, port 8095)

**Optional (profiles):**
- `langfuse` (own database `langfuse`, port 3001, profile: observability)
- `prometheus`, `grafana` (profile: monitoring)

**Network:** Single `zakops-network` bridge.

**Dashboard:** NOT in compose. Stays as bare `npm run dev` process.

**Critical Docker decisions:**
- Volumes use `external: true` — Docker will NOT create new volumes, it references existing ones
- Agent-db moves to port 5433 (host) → 5432 (container) to avoid conflict with main postgres
- Backend's `extra_hosts: ["host.docker.internal:host-gateway"]` for vLLM access

**Gate P3:** `docker compose config` validates without errors.

---

### Phase 4: Update Makefile + Sync Paths (20 min)

**Makefile changes:**

| Current | New | Reason |
|---------|-----|--------|
| `$$(realpath $(MONOREPO_ROOT)/../zakops-backend)/src/schemas/rag_models.py` | `$(MONOREPO_ROOT)/apps/backend/src/schemas/rag_models.py` | Backend is now in-tree |
| `make update-spec` (curl localhost:8091) | Same curl — port doesn't change | No change needed |
| N/A | `backend-dev`, `backend-test`, `backend-build` | New convenience targets |

**Validator changes:**

| File | Change |
|------|--------|
| `tools/infra/validate-contract-surfaces.sh` | `realpath "$REPO_ROOT/../zakops-backend/..."` → `"$REPO_ROOT/apps/backend/..."` |

**OpenAPI spec:** Backend's `shared/openapi/zakops-api.json` is now redundant — the canonical copy is already at `packages/contracts/openapi/zakops-api.json`. Remove the backend copy, update `make update-spec` to write directly to `packages/contracts/`.

**Gate P4:**
- `make sync-all-types` completes without errors
- `grep -r '../zakops-backend' Makefile tools/` returns 0 matches

---

### Phase 5: Update Backend Scripts for New Paths (15 min)

Every script in `apps/backend/scripts/` uses relative paths (`./db/migrations`, `./venv/bin/activate`). These still work if you `cd apps/backend` first.

**Strategy:** Don't rewrite paths inside scripts. Instead:
1. Makefile targets always `cd` to backend dir first: `cd apps/backend && bash scripts/dev.sh`
2. Add a `SCRIPT_DIR` guard to critical scripts:
   ```bash
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   cd "$SCRIPT_DIR/.."
   ```

**Backend .env:** Copy existing `/home/zaks/zakops-backend/.env` to `apps/backend/.env` (it's in .gitignore).

**Gate P5:** `cd apps/backend && bash scripts/dev.sh` starts the backend on 8091.

---

### Phase 6: Migrate Docker State (15 min)

```bash
# Stop old backend compose
cd /home/zaks/zakops-backend
docker compose down

# Verify volumes still exist (external: true means they persist)
docker volume inspect zakops_postgres_data  # Must exist
docker volume inspect zakops_redis_data     # Must exist

# Start new unified compose
cd /home/zaks/zakops-agent-api
docker compose up -d

# Verify data
docker exec zakops-backend-1 curl -sf http://localhost:8091/api/deals?limit=1 | jq '.[0].deal_id'
# Must return a deal ID (proving data survived)
```

**Gate P6:**
- `docker ps` shows postgres, redis, backend, outbox-worker, agent-db, agent-api all healthy
- `curl http://localhost:8091/api/deals?limit=1` returns deal data
- `curl http://localhost:8091/api/pipeline/summary` returns stage counts matching pre-merge
- `curl http://localhost:8095/health` returns healthy

---

### Phase 7: Update Documentation + CLAUDE.md (15 min)

| File | Change |
|------|--------|
| `CLAUDE.md` | Remove backend as separate repo, update paths |
| `INFRASTRUCTURE_MANIFEST.md` | Update service topology |
| `/home/zaks/CLAUDE.md` | Remove `/home/zaks/zakops-backend` from repos table |
| `MEMORY.md` | Update project map table |
| `bookkeeping/docs/SERVICE-CATALOG.md` | Update backend section |
| `.claude/rules/contract-surfaces.md` | Update Surface 5 path |

**Gate P7:** `make infra-check` passes.

---

### Phase 8: Simplify Sync Chain (20 min)

**Before merge:**
```
make update-spec    → curl localhost:8091/openapi.json → packages/contracts/openapi/zakops-api.json
make sync-types     → reads zakops-api.json → generates TS types
make sync-backend-models → reads zakops-api.json → generates Python models
```

**After merge (no change to the flow):** The sync chain works exactly the same. Port 8091 doesn't change. The only difference is that `sync-rag-models` output path changes from `../zakops-backend/` to `apps/backend/`.

**Future simplification (optional, deferred):** Since backend source is now in-tree, you could generate the OpenAPI spec from source code directly (without running the server) using `python -c "from src.api.orchestration.main import app; import json; print(json.dumps(app.openapi()))"`. This would eliminate the `make update-spec` live dependency. But this is NOT required for the merge.

**Gate P8:** Full sync chain works:
```bash
make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit
```

---

### Phase 9: Archive Old Repo (5 min)

```bash
# Rename, don't delete
mv /home/zaks/zakops-backend /home/zaks/zakops-backend-ARCHIVED-$(date +%F)

# Verify nothing references the old path
grep -r '/home/zaks/zakops-backend' /home/zaks/zakops-agent-api/ \
  --include='*.sh' --include='*.ts' --include='*.py' --include='Makefile' \
  | grep -v node_modules | grep -v .git | grep -v ARCHIVED
# Must return 0 lines
```

**Gate P9:** No runtime references to old path.

---

### Phase 10: Final Verification (15 min)

```bash
# Full validation suite
make validate-local                          # PASS
cd apps/dashboard && npx tsc --noEmit        # 0 errors
make validate-contract-surfaces              # 17/17 PASS
make validate-surface17                      # 44/44 PASS
bash tools/infra/validate-surface-count-consistency.sh  # 4-way consistent

# Live validation (services must be running)
make validate-live                           # PASS
bash tools/infra/validate-endpoint-liveness.sh  # All endpoints JSON
bash tools/infra/smoke-test.sh               # All pages load

# Backend-specific
cd apps/backend && bash scripts/test.sh      # Tests pass
cd apps/backend && bash scripts/qa_smoke.sh  # QA smoke passes
```

**Gate P10:** ALL gates pass.

---

## What This Eliminates

| Before | After |
|--------|-------|
| 4 repos | 3 repos (monorepo + Zaks-llm + bookkeeping) |
| 2 docker-compose files fighting over ports | 1 unified compose |
| `make update-spec` requires running backend (cross-repo curl) | Same (but could be simplified later) |
| `sync-rag-models` writes to `../zakops-backend/` (fragile path) | Writes to `apps/backend/` (in-tree) |
| Backend changes require separate commit + cross-repo sync | Atomic commits (backend + types in one commit) |
| CLAUDE.md references 2 repos for backend work | Single repo reference |
| `zakops-backend-postgres-1` restart loops from conflicting compose | Single compose lifecycle |

## What This Does NOT Eliminate

| Still Needed | Why |
|-------------|-----|
| `make update-spec` (curl live backend) | OpenAPI spec comes from running server |
| `make sync-types` + `sync-backend-models` | Codegen still needed (just local now) |
| Zod runtime validation | Backend responses can still evolve |
| 17 contract surfaces | Surfaces are about type safety, not repo layout |
| Surface 5 (RAG → Backend) | Zaks-llm is still external |

---

## Rollback Plan

**At any phase, if something breaks:**

1. **Phase 0-2:** No services affected. Just `git reset --hard` on monorepo.
2. **Phase 3-5:** Old backend compose still exists. `cd /home/zaks/zakops-backend && docker compose up -d`.
3. **Phase 6:** If data is lost, restore from Phase 0 dumps:
   ```bash
   docker exec -i zakops-backend-postgres-1 pg_restore -U zakops -d zakops < /home/zaks/backups/zakops-pre-merge.dump
   ```
4. **Phase 9:** Old repo is renamed, not deleted. `mv zakops-backend-ARCHIVED-* zakops-backend` to restore.

**Nuclear rollback:** Restore both tar.gz archives from Phase 0. Everything returns to pre-merge state.

---

## Decision Points for User

| # | Question | Options |
|---|----------|---------|
| D1 | Git history strategy | A: `--squash` (1 merge commit, clean history) / B: Full history (43 commits appear in monorepo log) |
| D2 | Langfuse disposition | A: Own database (fix the crash) / B: Drop entirely / C: Defer (leave broken) |
| D3 | Agent DB port | A: Move to 5433 (avoids conflict) / B: Keep both on 5432 with different container names (risky) |
| D4 | Timing | A: Do it now (services down for ~10 min during Phase 6) / B: Plan for a maintenance window |

---

## Files Modified Summary

### New Files
| File | Purpose |
|------|---------|
| `docker-compose.yml` (root) | Unified service orchestration |
| `.env.example` (root) | Shared infrastructure env template |

### Moved (via git subtree)
| From | To |
|------|-----|
| `zakops-backend/*` | `apps/backend/*` |

### Edited
| File | Change |
|------|--------|
| `Makefile` | Backend targets + path updates (3-5 lines) |
| `tools/infra/validate-contract-surfaces.sh` | Backend path reference |
| `CLAUDE.md` | Remove separate backend repo reference |
| `INFRASTRUCTURE_MANIFEST.md` | Update topology |
| `/home/zaks/CLAUDE.md` | Update repos table |
| `MEMORY.md` | Update project map |
| `.claude/rules/contract-surfaces.md` | Update Surface 5 path |
| `apps/agent-api/docker-compose.yml` | Port change (5432→5433 for agent-db) |

### Deleted (after archive)
| Item | Replacement |
|------|------------|
| `/home/zaks/zakops-backend/` | `/home/zaks/zakops-backend-ARCHIVED-YYYY-MM-DD/` |

---

## Estimated Effort

| Phase | Time | Risk Level |
|-------|------|-----------|
| P0: Backup | 15 min | ZERO |
| P1: Clean backend | 10 min | ZERO |
| P2: Git subtree | 5 min | LOW |
| P3: Docker compose | 30 min | **HIGH** |
| P4: Makefile + sync | 20 min | MEDIUM |
| P5: Backend scripts | 15 min | LOW |
| P6: Docker migration | 15 min | **HIGH** |
| P7: Documentation | 15 min | LOW |
| P8: Sync chain verify | 20 min | MEDIUM |
| P9: Archive old repo | 5 min | LOW |
| P10: Final verification | 15 min | LOW |
| **Total** | **~2.5 hours** | |

**Service downtime:** ~10 minutes during Phase 6 (docker compose down → up).
