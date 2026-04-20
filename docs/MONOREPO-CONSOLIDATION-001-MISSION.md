# MISSION: MONOREPO-CONSOLIDATION-001
## Merge zakops-backend into zakops-agent-api Monorepo
## Date: 2026-02-15
## Classification: Infrastructure Consolidation
## Prerequisite: AGENT-CONFIG-AUTOSYNC-001 (complete — provides sync automation used in P7)
## Successor: None (standalone — enables future atomic commits across backend+dashboard)

---

## Mission Objective

Merge the `zakops-backend` repository into the `zakops-agent-api` monorepo at `apps/backend/`, creating a unified codebase for all ZakOps services except the loosely-coupled RAG/LLM stack.

This is a MOVE mission, not a rewrite. The backend code, Docker configuration, migrations, and scripts move into the monorepo with minimal modification. The primary changes are path references, Docker orchestration unification, and documentation updates.

**What this is NOT:**
- NOT a refactor of backend code (no Python changes except path fixes in scripts)
- NOT a feature addition (no new endpoints, no new functionality)
- NOT a migration of Zaks-llm (stays external — GPU-dependent, loosely coupled via Surface 5)
- NOT a Docker architecture redesign (same services, same ports, unified orchestration)

**Source material:**
- Design plan: `/home/zaks/bookkeeping/docs/MONOREPO-CONSOLIDATION-001-PLAN.md`
- Pre-execution advisory review: 8 amendments incorporated (see Context section)

**What this eliminates:**
- Cross-repo sync friction (`../zakops-backend/` fragile paths → in-tree `apps/backend/`)
- Dual docker-compose port conflicts (2 fighting stacks → 1 unified compose)
- Split commits for API changes (backend + types can now be atomic)

**What this does NOT eliminate:**
- `make update-spec` (still curl-based, backend must be running)
- `make sync-types` / `sync-backend-models` (codegen still needed)
- 17 contract surfaces (type safety is orthogonal to repo layout)
- Surface 5 RAG → Backend (Zaks-llm is still external)

---

## Context

### Current State (verified 2026-02-15)

**Backend repo (`/home/zaks/zakops-backend/`):**
- Branch: `fix/full-remediation-001` (NOT `main`)
- 49 modified files + 37 untracked files — substantial uncommitted work
- Last commit on branch: `444dff6 feat(exec-002): MCP contract formalization + RAG typed client`
- Contains: 193 Python source files, 35+ migrations, 50+ tests, Docker compose, MCP server

**Docker state:**
- 2 separate compose stacks running simultaneously (backend + agent)
- 4 Docker volumes: `zakops_postgres_data`, `zakops_redis_data`, `agent-api_agent-postgres-data`, `docker_redis-data`
- Langfuse defined but not running (Prisma migration collision, exit code 1)
- 3 PostgreSQL instances: backend (5432), agent-db (internal only), rag-db (5434)

**Path references:**
- 223 references to `zakops-backend` across monorepo, hooks, skills, commands, and Codex configs
- Categories: filesystem paths, Docker container names, documentation tables, rule glob patterns

### Decision Points (Locked)

| # | Decision | Locked Value | Rationale |
|---|----------|-------------|-----------|
| D1 | Git history | `--squash` | Clean monorepo history; original repo archived for blame |
| D2 | Langfuse | Drop entirely | Broken since day one; future Langfuse = separate infrastructure |
| D3 | Agent DB port | 5433 (host) → 5432 (container) | Avoids conflict; agent-api uses Docker DNS internally |
| D4 | Timing | Execute now | ~10 min service downtime acceptable |

### Advisor Amendments (8 items, all incorporated)

| # | Amendment | How Incorporated |
|---|-----------|-----------------|
| A1 | Bootstrap guard for external volumes | `bootstrap-docker` Makefile target + keep `external: true` |
| A2 | Pin COMPOSE_PROJECT_NAME=zakops | Root `.env.example` + compose file |
| A3 | Host-side curl for P6 verification | Host `curl` primary + in-container Python for network check |
| A4 | Verify backend repo state before subtree | Hard gate at P2 start |
| A5 | Verify agent-api DATABASE_URL after port change | Verification in P6 |
| A6 | Backup gate with pg_restore --list + 500KB threshold | Strengthened P0 gate |
| A7 | Verify .gitignore covers apps/backend/.env | Check in P2, fix if needed |
| A8 | Visual migration file ordering check | Verification in P1 |

---

## Glossary

| Term | Definition |
|------|-----------|
| Subtree merge | `git subtree add` — merges another repo into a subdirectory, optionally preserving or squashing history |
| `external: true` | Docker Compose volume declaration that references an existing volume instead of creating a new one; fails if volume doesn't exist (intentional safety) |
| `COMPOSE_PROJECT_NAME` | Docker env var that controls container name prefix; if unset, derived from directory name |
| Bootstrap guard | A pre-start script or Makefile target that creates required infrastructure (volumes, networks) before `docker compose up` |

---

## Architectural Constraints

Per standing rules in CLAUDE.md and MEMORY.md, plus mission-specific:

- **Port 8091 does not change** — all `localhost:8091` references remain valid after the merge
- **Port 8090 is FORBIDDEN** — per standing rule, never use or reference
- **Separate .env files per service** — `apps/backend/.env` and `apps/agent-api/.env` remain independent; root `.env` only has shared infra vars (per Risk 5 mitigation)
- **Dashboard stays bare** — NOT in Docker compose (per standing rule: Docker conflicts on network_mode: host)
- **No Langfuse** — dropped entirely from the unified compose (Decision D2)
- **external: true for data volumes** — Docker must reference existing volumes, not create new empty ones (per Risk 1 mitigation)
- **Migration files immutable** — do NOT rename, reorder, or modify migration SQL files during the move
- **Contract surface discipline** — per standing rules; this mission does not modify contract surfaces, only updates paths that reference them

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | `git subtree add` from `main` misses 86 uncommitted changes on `fix/full-remediation-001` | CERTAIN if not addressed | All recent backend work lost | Phase 1 commits and merges to main before subtree add |
| 2 | Docker volume names change due to COMPOSE_PROJECT_NAME mismatch, creating empty volumes | HIGH | Data loss — 6 months of deals | Amendment A2: pin `COMPOSE_PROJECT_NAME=zakops` + `external: true` volumes |
| 3 | 223 path references not fully updated, causing silent failures in validators/hooks | HIGH | `make validate-local` fails, hooks break | Phase 4+5 systematic grep-and-replace with zero-match verification gate |
| 4 | Backend .env with credentials committed to monorepo git | MEDIUM | Security incident | Amendment A7: verify `**/.env` in root .gitignore |
| 5 | Old backend compose accidentally started alongside new unified compose, port collision | MEDIUM | Services fail to bind, partial stack | Phase 6 explicit `docker compose down` on old stack + port verification |

---

<!-- Adopted from Improvement Area IA-1 -->
## Context Checkpoint (IA-1)

This mission has 11 phases. If context becomes constrained at any point, summarize progress to the checkpoint file at `/home/zaks/bookkeeping/mission-checkpoints/MONOREPO-CONSOLIDATION-001.md` with: phases completed, phases remaining, current validation state, any open decisions. Resume from the checkpoint in the next session.

<!-- Adopted from Improvement Area IA-2 -->
## Crash Recovery

If resuming after a crash, run these commands to determine current state:

1. `ls /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>/dev/null && echo "P2 DONE" || echo "P2 NOT DONE"` — subtree merge status
2. `ls /home/zaks/zakops-agent-api/docker-compose.yml 2>/dev/null && echo "P3 DONE" || echo "P3 NOT DONE"` — root compose exists
3. `grep -c 'apps/backend' /home/zaks/zakops-agent-api/Makefile 2>/dev/null` — if >0, P4 started
4. `docker ps --format '{{.Names}}' | grep -c 'zakops-' 2>/dev/null` — if services running from monorepo root, P6 done
5. `ls /home/zaks/zakops-backend-ARCHIVED-* 2>/dev/null && echo "P9 DONE" || echo "P9 NOT DONE"` — archive status

---

## Contract Surfaces Affected

This mission affects path references in surfaces but does not modify the surfaces themselves:

| Surface | Impact | Gate |
|---------|--------|------|
| S5 (RAG → Backend SDK) | Output path changes from `../zakops-backend/` to `apps/backend/` | `make sync-rag-models` |
| S6 (MCP Tool Schemas) | Source path reference changes | `make validate-local` |
| S10 (Dependency Health) | Backend path in validator | `make validate-surface10` |
| S11 (Env Registry) | Backend .env.example path | `make validate-surface11` |
| S12 (Error Taxonomy) | Backend source path | `make validate-surface12` |
| S13 (Test Coverage) | Backend test path | `make validate-surface13` |

---

## Phase 0 — Backup Everything
**Complexity:** S
**Estimated touch points:** 0 (creates backup files only)

**Purpose:** Create recoverable backups of all data and code before any destructive operations.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks

- P0-01: **Create backup directory** — `mkdir -p /home/zaks/backups`
- P0-02: **Dump zakops database** — `pg_dump -U zakops -h localhost -d zakops -F c -f /home/zaks/backups/zakops-pre-merge.dump`
  - **Checkpoint:** File exists and >500KB: `ls -lh /home/zaks/backups/zakops-pre-merge.dump`
  - **Checkpoint:** Archive is structurally valid: `pg_restore --list /home/zaks/backups/zakops-pre-merge.dump | head -5` (must show table-of-contents entries)
- P0-03: **Dump zakops_agent database** — `pg_dump -U agent -h localhost -d zakops_agent -F c -f /home/zaks/backups/zakops_agent-pre-merge.dump`
  - **Checkpoint:** File exists and >100KB
  - **Checkpoint:** `pg_restore --list /home/zaks/backups/zakops_agent-pre-merge.dump | head -5`
- P0-04: **Archive both repos** — `tar czf` each to `/home/zaks/backups/`
- P0-05: **Record Docker volume state** — `docker volume ls > /home/zaks/backups/docker-volumes-pre-merge.txt`
- P0-06: **Record pre-merge deal count** — `psql -U zakops -h localhost -d zakops -t -A -c "SELECT count(*) FROM zakops.deals"` — save this number for P6 verification

### Gate P0
- 4 backup files exist: 2 pg_dumps (>500KB and >100KB respectively), 2 tar.gz archives
- `pg_restore --list` succeeds on both dumps
- Docker volumes file is non-empty
- Pre-merge deal count recorded

---

## Phase 1 — Prepare Backend Repo
**Complexity:** M
**Estimated touch points:** 1 repo (zakops-backend)

**Purpose:** Commit all uncommitted work, merge to main, clean build artifacts, verify migration ordering.

### Blast Radius
- **Services affected:** None (backend continues running during this phase)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks

- P1-01: **Commit all work in zakops-backend** — The backend has 49 modified + 37 untracked files on `fix/full-remediation-001`. Stage all changes, commit with a descriptive message like "chore: pre-merge consolidation commit — all WIP from fix/full-remediation-001"
  - **Checkpoint:** `git status --short` returns empty (clean working tree)
- P1-02: **Merge branch to main** — `git checkout main && git merge fix/full-remediation-001`
  - **Decision tree:**
    - **IF** merge conflicts → resolve them (these are all YOUR changes, so prefer the branch version)
    - **IF** `main` has diverged significantly → use `git merge --no-ff` to preserve branch history
  - **Checkpoint:** `git branch --show-current` returns `main`, `git log --oneline -1` shows the merge commit
- P1-03: **Clean build artifacts** — Remove `venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `*.pyc`
  - **Checkpoint:** `du -sh /home/zaks/zakops-backend/` shows <50MB
- P1-04: **Verify migration file ordering (Amendment A8)** — `ls -1 /home/zaks/zakops-backend/db/migrations/*.sql | sort` — visually confirm numbered order is correct and no migration depends on a later-numbered one
  - **Checkpoint:** Files list in ascending numeric order (000, 001, 016, 018, 022-035)

### Rollback Plan
1. `git checkout fix/full-remediation-001` to return to original branch
2. Backend services are unaffected (still running from the old path)

### Gate P1
- Backend repo is on `main` with clean working tree
- All recent work committed (86 files)
- Build artifacts removed (<50MB)
- Migration files verified in correct order

---

## Phase 2 — Git Subtree Merge
**Complexity:** S
**Estimated touch points:** 1 (monorepo git operation)

**Purpose:** Import backend codebase into monorepo as `apps/backend/` using git subtree.

### Blast Radius
- **Services affected:** None (git operation only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks

- P2-01: **Verify backend repo state (Amendment A4)** — Hard gate before subtree add:
  ```
  cd /home/zaks/zakops-backend && git status --porcelain
  ```
  Must return empty. If not empty, STOP — go back to P1.
  - **Checkpoint:** Exit code 0 AND empty output
- P2-02: **Verify monorepo state** — `cd /home/zaks/zakops-agent-api && git status --short` — note any existing uncommitted changes (commit them separately first if needed)
- P2-03: **Run subtree add** — `cd /home/zaks/zakops-agent-api && git subtree add --prefix=apps/backend /home/zaks/zakops-backend main --squash`
  - **Checkpoint:** `ls /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` exists
- P2-04: **Verify .gitignore coverage (Amendment A7)** — Check that the monorepo root `.gitignore` covers `apps/backend/.env`. The root gitignore already has `.env` and `.env.*` patterns. Verify: `grep -n '\.env' /home/zaks/zakops-agent-api/.gitignore`
  - **Decision tree:**
    - **IF** `.env` is already covered by root patterns → no action needed
    - **IF** not covered → add `**/.env` to root `.gitignore`

### Rollback Plan
1. `cd /home/zaks/zakops-agent-api && git reset --hard HEAD~1` (removes the subtree merge commit)

### Gate P2
- `apps/backend/` directory exists with full backend source
- `git log --oneline apps/backend/ | head -3` shows the squash merge commit
- Root `.gitignore` covers `apps/backend/.env`

---

## Phase 3 — Create Unified Docker Compose
**Complexity:** L
**Estimated touch points:** 3 new files

**Purpose:** Create a single root-level docker-compose.yml that orchestrates all services (postgres, redis, backend, outbox-worker, agent-db, agent-api).

### Blast Radius
- **Services affected:** All Docker services (but not started yet — just creating the file)
- **Pages affected:** None
- **Downstream consumers:** All make targets and scripts that reference docker compose

### Tasks

- P3-01: **Create root docker-compose.yml** at `/home/zaks/zakops-agent-api/docker-compose.yml` with:
  - **Shared infra:** postgres (pg15-alpine, port 5432), redis (redis7-alpine, port 6379)
  - **Backend services:** backend (build: `./apps/backend`, port 8091, env_file: `./apps/backend/.env`), outbox-worker (same build, depends_on backend)
  - **Agent services:** agent-db (pgvector:pg16, port 5433:5432, container_name: zakops-agent-db), agent-api (build: `./apps/agent-api`, port 8095:8000, container_name: zakops-agent-api)
  - **Volumes:** `zakops_postgres_data: external: true`, `zakops_redis_data: external: true`, `agent-postgres-data: external: true`
  - **Network:** single `zakops-network` bridge
  - **NO Langfuse** (Decision D2)
  - **Optional profiles:** monitoring (prometheus, grafana, cadvisor)
  - **Checkpoint:** `docker compose -f /home/zaks/zakops-agent-api/docker-compose.yml config` validates without errors

- P3-02: **Create root .env.example** at `/home/zaks/zakops-agent-api/.env.example` with:
  - `COMPOSE_PROJECT_NAME=zakops` (Amendment A2)
  - Shared infra vars only: `POSTGRES_PORT`, `REDIS_PORT`
  - Comments explaining per-service env files
  - **Checkpoint:** File exists and contains `COMPOSE_PROJECT_NAME=zakops`

- P3-03: **Create bootstrap-docker target (Amendment A1)** — Add to Makefile:
  ```
  bootstrap-docker:  ## Create required Docker volumes (first-time setup only)
  	docker volume create zakops_postgres_data 2>/dev/null || true
  	docker volume create zakops_redis_data 2>/dev/null || true
  	docker volume create agent-api_agent-postgres-data 2>/dev/null || true
  ```
  - **Checkpoint:** `make bootstrap-docker` runs without error

### Decision Tree
- **IF** existing agent compose uses volume name `agent-api_agent-postgres-data` → use that exact name in unified compose (volume names must match)
- **IF** the agent compose uses a different volume name prefix → check `docker volume ls` and use the actual existing name

### Rollback Plan
1. `rm /home/zaks/zakops-agent-api/docker-compose.yml /home/zaks/zakops-agent-api/.env.example`
2. Old compose files still exist and are functional

### Gate P3
- `docker compose config` validates without errors
- `COMPOSE_PROJECT_NAME=zakops` present in `.env.example`
- `bootstrap-docker` target exists in Makefile
- All volumes declared as `external: true`
- No Langfuse service defined

---

## Phase 4 — Update Makefile + Sync Paths
**Complexity:** M
**Estimated touch points:** 8-10 files

**Purpose:** Update all path references from `../zakops-backend/` to `apps/backend/` in Makefile and validator scripts.

### Blast Radius
- **Services affected:** None (path updates only)
- **Pages affected:** None
- **Downstream consumers:** All `make sync-*` targets, all `validate-surface*` scripts

### Tasks

- P4-01: **Update Makefile** — Change `$$(realpath $(MONOREPO_ROOT)/../zakops-backend)` to `$(MONOREPO_ROOT)/apps/backend` in all relevant targets. Add new convenience targets: `backend-dev`, `backend-test`, `backend-build`, `backend-logs`.
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/zakops-agent-api/Makefile` returns 0

- P4-02: **Update validator scripts** in `tools/infra/`:
  - `validate-contract-surfaces.sh` — update `BACKEND_RAG` path
  - `validate-surface10.sh` — update `BACKEND` path
  - `validate-surface11.sh` — update `BACKEND_ENV` path
  - `validate-surface12.sh` — update `BACKEND` path
  - `validate-surface13.sh` — update `BACKEND` path
  - `migration-assertion.sh` — update `BACKEND_ROOT` path
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/zakops-agent-api/tools/infra/*.sh` returns 0

- P4-03: **Update operational scripts** in `tools/ops/`:
  - `reset_state.sh` — update backend compose reference
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/zakops-agent-api/tools/ops/*.sh` returns 0

- P4-04: **Update validation scripts** in `tools/validation/`:
  - `phase8_double_verify.sh` — update container name references
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/zakops-agent-api/tools/validation/*.sh` returns 0

- P4-05: **Remove redundant OpenAPI spec** — Backend's `apps/backend/shared/openapi/zakops-api.json` is now redundant (canonical copy is at `packages/contracts/openapi/zakops-api.json`). Remove it to avoid drift.
  - **Checkpoint:** `ls apps/backend/shared/openapi/zakops-api.json 2>/dev/null` returns not found

### Rollback Plan
1. `git checkout -- Makefile tools/`

### Gate P4
- `make sync-all-types` completes without errors
- `grep -r '../zakops-backend' /home/zaks/zakops-agent-api/Makefile /home/zaks/zakops-agent-api/tools/` returns 0 matches
- `make validate-surface10 && make validate-surface11 && make validate-surface12 && make validate-surface13` all pass

---

## Phase 5 — Update Backend Scripts + .env
**Complexity:** S
**Estimated touch points:** 2-3 files

**Purpose:** Ensure backend scripts work from their new location and copy the .env file.

### Blast Radius
- **Services affected:** None (scripts not executed yet)
- **Pages affected:** None
- **Downstream consumers:** Makefile targets that call backend scripts

### Tasks

- P5-01: **Copy backend .env** — `cp /home/zaks/zakops-backend/.env /home/zaks/zakops-agent-api/apps/backend/.env` (it's in .gitignore, won't be committed)
  - **Checkpoint:** File exists at `apps/backend/.env`

- P5-02: **Verify scripts work from new location** — Test a non-destructive script: `cd /home/zaks/zakops-agent-api/apps/backend && bash scripts/export_openapi.py --help 2>/dev/null || echo "Need SCRIPT_DIR guard"`
  - **Decision tree:**
    - **IF** scripts work with `cd apps/backend` prefix → no changes needed
    - **IF** scripts fail → add `SCRIPT_DIR` guard to failing scripts

- P5-03: **Copy .dockerignore** — If `apps/backend/.dockerignore` doesn't exist, copy from original: `cp /home/zaks/zakops-backend/.dockerignore /home/zaks/zakops-agent-api/apps/backend/.dockerignore 2>/dev/null || true`

### Rollback Plan
1. `rm apps/backend/.env` (it's not committed)

### Gate P5
- `apps/backend/.env` exists (not committed)
- `apps/backend/.dockerignore` exists

---

## Phase 6 — Migrate Docker State
**Complexity:** L
**Estimated touch points:** Docker infrastructure (compose down/up)

**Purpose:** Stop the old dual-stack compose and start the unified compose. This is the service downtime window (~10 min).

### Blast Radius
- **Services affected:** ALL — postgres, redis, backend, outbox-worker, agent-db, agent-api
- **Pages affected:** ALL — dashboard will show 502 during downtime
- **Downstream consumers:** Everything

### Tasks

- P6-01: **Stop old backend compose** — `cd /home/zaks/zakops-backend && docker compose down`
  - **Checkpoint:** `docker ps | grep zakops-backend` returns nothing

- P6-02: **Stop old agent compose** — `cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose down`
  - **Checkpoint:** `docker ps | grep zakops-agent` returns nothing

- P6-03: **Verify no port conflicts** — `ss -tlnp | grep -E '5432|6379|8091|8095'` — must show no listeners

- P6-04: **Verify volumes exist** — `docker volume inspect zakops_postgres_data && docker volume inspect zakops_redis_data && docker volume inspect agent-api_agent-postgres-data` — all must succeed

- P6-05: **Create root .env from .env.example** — Copy `.env.example` to `.env`, set `COMPOSE_PROJECT_NAME=zakops`

- P6-06: **Start unified compose** — `cd /home/zaks/zakops-agent-api && docker compose up -d`
  - **Checkpoint:** `docker ps` shows all services starting

- P6-07: **Wait for health** — Wait up to 60s for all healthchecks to pass

- P6-08: **Verify data survived (Amendment A3)** — Host-side curl:
  - `curl -sf http://localhost:8091/api/deals?limit=1 | jq '.[0].deal_id'` — must return a deal ID
  - `curl -sf http://localhost:8091/api/pipeline/summary` — stage counts must match pre-merge
  - Compare deal count with P0-06 recorded value

- P6-09: **Verify Docker internal networking (Amendment A3)** — In-container Python TCP check:
  - `docker exec zakops-backend-1 python -c "import socket; socket.create_connection(('postgres', 5432), timeout=3); print('OK')"` — backend→postgres
  - `docker exec zakops-agent-api python -c "import socket; socket.create_connection(('db', 5432), timeout=3); print('OK')"` — agent→agent-db

- P6-10: **Verify agent-api DATABASE_URL (Amendment A5)** — `docker exec zakops-agent-api env | grep -E 'POSTGRES_HOST|POSTGRES_PORT|DATABASE_URL'` — must reference `db:5432` (Docker DNS), not `localhost:5432`

- P6-11: **Verify environment isolation (Risk 5)** — `docker exec zakops-backend-1 env | grep DATABASE_URL` — must show `zakops` db, not `zakops_agent`

### Rollback Plan
1. `cd /home/zaks/zakops-agent-api && docker compose down`
2. `cd /home/zaks/zakops-backend && docker compose up -d` (old stack still exists)
3. `cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose up -d` (old agent stack)
4. If data lost: `pg_restore -U zakops -d zakops /home/zaks/backups/zakops-pre-merge.dump`

### Gate P6
- `docker ps` shows all services healthy
- `curl localhost:8091/health/ready` returns 200
- `curl localhost:8095/health` returns 200
- Deal count matches pre-merge
- Internal Docker networking verified
- Environment isolation verified

---

## Phase 7 — Update Documentation
**Complexity:** M
**Estimated touch points:** 12-15 files

**Purpose:** Update all documentation, CLAUDE.md files, MEMORY.md, hooks, skills, and agent configs to reference the new backend location.

### Blast Radius
- **Services affected:** None (documentation only)
- **Pages affected:** None
- **Downstream consumers:** All Claude Code sessions, Codex sessions, Gemini sessions

### Tasks

- P7-01: **Update monorepo CLAUDE.md** — Remove separate backend repo reference, update paths, update database migrations path
- P7-02: **Update `/home/zaks/CLAUDE.md`** — Remove `zakops-backend` from repos table, update golden commands to `cd apps/backend && ...`
- P7-03: **Update `MEMORY.md`** — Update project map table (3 repos, not 4), update key file locations
- P7-04: **Update `.claude/rules/contract-surfaces.md`** — Update all `zakops-backend/` path references to `apps/backend/`
- P7-05: **Update `.claude/rules/backend-api.md`** — Update path globs from `zakops-backend/src/` to `apps/backend/src/`
- P7-06: **Update hooks** — `compact-recovery.sh`, `pre-compact.sh`, `task-completed.sh`, `session-start.sh` — update backend path references
- P7-07: **Update skills** — `security-and-data`, `debugging-playbook`, `project-context`, `add-endpoint` — update backend references
- P7-08: **Update commands** — `investigate.md`, `tail.md`, `run-gates.md`, `deploy-backend.md` — update paths
- P7-09: **Update `.claude/CLAUDE.md`** — Update backend reference
- P7-10: **Update Codex configs** — `/home/zaks/.codex/AGENTS.md` and all Codex skills with backend references
- P7-11: **Update monorepo `.agents/AGENTS.md`** — Update backend paths
- P7-12: **Update `GEMINI.md`** — Update any backend path references
- P7-13: **Update `INFRASTRUCTURE_MANIFEST.md`** — Update service topology
- P7-14: **Update `bookkeeping/docs/SERVICE-CATALOG.md`** — Update backend section

### Decision Tree
- **IF** a file references `docker logs zakops-backend-backend-1` → update to `docker logs zakops-backend-1` (container name changes with unified compose)
- **IF** a file references `cd /home/zaks/zakops-backend && docker compose ...` → update to `cd /home/zaks/zakops-agent-api && docker compose ...`

### Rollback Plan
1. Git revert on documentation files
2. Restore hooks from backup

### Gate P7
- `grep -rn 'zakops-backend' /home/zaks/.claude/ /home/zaks/.codex/ /home/zaks/zakops-agent-api/CLAUDE.md /home/zaks/zakops-agent-api/.claude/ /home/zaks/zakops-agent-api/.agents/ /home/zaks/zakops-agent-api/GEMINI.md /home/zaks/CLAUDE.md 2>/dev/null | grep -v ARCHIVED | grep -v PLAN | grep -v node_modules | grep -v .git | wc -l` — must be 0 (excluding archived references and plan docs)
- `make infra-check` passes

---

## Phase 8 — Verify Sync Chain
**Complexity:** M
**Estimated touch points:** 0 (verification only)

**Purpose:** Verify the full codegen sync chain works end-to-end from the new layout.

### Blast Radius
- **Services affected:** None (read/codegen only)
- **Pages affected:** None

### Tasks

- P8-01: **Run full sync chain** — `make update-spec && make sync-types && make sync-backend-models && make sync-rag-models`
  - **Checkpoint:** All 4 commands succeed (exit 0)
- P8-02: **TypeScript compilation** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - **Checkpoint:** 0 errors
- P8-03: **Agent types sync** — `make sync-agent-types`
  - **Checkpoint:** Exit 0
- P8-04: **Full sync-all-types** — `make sync-all-types`
  - **Checkpoint:** Exit 0 (includes sync-agent-configs from AGENT-CONFIG-AUTOSYNC-001)

### Gate P8
- Full sync chain: `make update-spec && make sync-all-types && npx tsc --noEmit` — all pass

---

## Phase 9 — Archive Old Repo
**Complexity:** S
**Estimated touch points:** 1 (filesystem rename)

**Purpose:** Rename the old backend repo to prevent accidental use.

### Blast Radius
- **Services affected:** None (old compose already stopped in P6)
- **Pages affected:** None

### Tasks

- P9-01: **Archive old repo** — `mv /home/zaks/zakops-backend /home/zaks/zakops-backend-ARCHIVED-$(date +%F)`
- P9-02: **Verify no remaining runtime references** — `grep -rn '/home/zaks/zakops-backend' /home/zaks/zakops-agent-api/ /home/zaks/.claude/ /home/zaks/.codex/ /home/zaks/CLAUDE.md --include='*.sh' --include='*.ts' --include='*.py' --include='*.md' --include='Makefile' --include='*.json' 2>/dev/null | grep -v node_modules | grep -v .git | grep -v ARCHIVED | grep -v PLAN | grep -v COMPLETION | grep -v CHANGES`
  - Must return 0 lines

### Rollback Plan
1. `mv /home/zaks/zakops-backend-ARCHIVED-* /home/zaks/zakops-backend`

### Gate P9
- Old repo renamed
- Zero runtime references to old path (excluding docs/history)

---

## Phase 10 — Final Verification
**Complexity:** M
**Estimated touch points:** 1 (CHANGES.md)

**Purpose:** Run comprehensive validation suite and record all changes.

### Blast Radius
- **Services affected:** None (verification only)

### Tasks

- P10-01: **Offline validation** — `make validate-local`
- P10-02: **TypeScript check** — `cd apps/dashboard && npx tsc --noEmit`
- P10-03: **Contract surface validation** — `make validate-contract-surfaces`
- P10-04: **Surface count consistency** — `bash tools/infra/validate-surface-count-consistency.sh`
- P10-05: **Live validation** — `make validate-live`
- P10-06: **Endpoint liveness** — `bash tools/infra/validate-endpoint-liveness.sh`
- P10-07: **Backend tests** — `cd apps/backend && bash scripts/test.sh`
- P10-08: **Dashboard smoke** — verify `curl -sf http://localhost:3003` loads (if dashboard is running)
- P10-09: **Record in CHANGES.md** — Full entry in `/home/zaks/bookkeeping/CHANGES.md`
- P10-10: **Create completion report** — `/home/zaks/bookkeeping/docs/MONOREPO-CONSOLIDATION-001-COMPLETION.md`

### Gate P10
- `make validate-local` PASS
- `npx tsc --noEmit` 0 errors
- All live services healthy
- CHANGES.md updated
- Completion report created

---

## Dependency Graph

```
Phase 0 (Backup)
    │
    ▼
Phase 1 (Prepare Backend — commit + merge + clean)
    │
    ▼
Phase 2 (Git Subtree Merge)
    │
    ▼
Phase 3 (Create Unified Docker Compose)
    │
    ├──────────────────┐
    ▼                  ▼
Phase 4 (Makefile)   Phase 5 (Scripts + .env)
    │                  │
    └────────┬─────────┘
             ▼
     Phase 6 (Migrate Docker State) ← SERVICE DOWNTIME
             │
             ▼
     Phase 7 (Documentation — 223 references)
             │
             ▼
     Phase 8 (Verify Sync Chain)
             │
             ▼
     Phase 9 (Archive Old Repo)
             │
             ▼
     Phase 10 (Final Verification)
```

Phases 4 and 5 can run in parallel (no dependencies between them). All other phases are sequential.

---

## Acceptance Criteria

### AC-1: Backend Source In Monorepo
`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` exists and contains the FastAPI app.

### AC-2: Unified Docker Compose
A single `docker-compose.yml` at monorepo root starts all services (postgres, redis, backend, outbox-worker, agent-db, agent-api) with `external: true` volumes and `COMPOSE_PROJECT_NAME=zakops`.

### AC-3: All Services Healthy
`docker ps` shows all services running and healthy from the unified compose.

### AC-4: Data Preserved
Deal count matches pre-merge snapshot. `curl localhost:8091/api/deals?limit=1` returns valid data.

### AC-5: Sync Chain Works
`make update-spec && make sync-all-types && npx tsc --noEmit` succeeds end-to-end.

### AC-6: Zero Stale References
`grep -r 'zakops-backend' <all relevant paths>` returns 0 matches (excluding archived repo, plan docs, and CHANGES.md history).

### AC-7: Langfuse Removed
No Langfuse service in docker-compose.yml. No Langfuse-related required env vars.

### AC-8: Bootstrap Guard Exists
`make bootstrap-docker` creates required Docker volumes for first-time setup.

### AC-9: Old Repo Archived
`/home/zaks/zakops-backend` renamed to `/home/zaks/zakops-backend-ARCHIVED-YYYY-MM-DD/`.

### AC-10: No Regressions
`make validate-local` passes. TypeScript compiles. No test breakage.

### AC-11: Bookkeeping
CHANGES.md updated. Completion report created.

---

## Guardrails

1. **Scope fence:** Do not refactor backend Python code. Move it as-is. The only code changes are path fixes in scripts.
2. **Generated file protection:** Per standing deny rules — do not edit `*.generated.ts` or `*_models.py`.
3. **Migration immutability:** Do NOT rename, reorder, or modify any SQL migration file. Move them exactly as they are.
4. **No Langfuse:** Do not include Langfuse in the unified compose (Decision D2 locked).
5. **Separate .env files:** Do NOT create a unified `.env` that merges backend and agent vars. Keep `apps/backend/.env` and `apps/agent-api/.env` independent.
6. **Volume safety:** All data volumes must use `external: true`. Never let Docker create new volumes that shadow existing ones.
7. **WSL safety:** CRLF strip and ownership fix on any new .sh files.
8. **Port 8090 FORBIDDEN** — per standing rule.
9. **Governance surfaces:** Validate S10-S13 after path updates (`make validate-surface10` through `make validate-surface13`).
10. **No feature creep:** Do not implement the "offline OpenAPI generation" optimization mentioned in the plan. That's a future enhancement.

---

## Executor Self-Check Prompts

### After Phase 0 (Backup):
- [ ] "Are both pg_dump files >500KB? Did `pg_restore --list` succeed on both?"
- [ ] "Did I record the pre-merge deal count for Phase 6 comparison?"

### After Phase 1 (Prepare Backend):
- [ ] "Did I commit ALL 86 uncommitted changes, not just the modified ones?"
- [ ] "Is the backend repo now on `main` with a clean working tree?"

### After Phase 2 (Subtree):
- [ ] "Does `.gitignore` cover `apps/backend/.env`?"
- [ ] "Was the subtree added from `main` (with all the recently committed work)?"

### After Phase 3 (Docker Compose):
- [ ] "Did I set `COMPOSE_PROJECT_NAME=zakops` in `.env.example`?"
- [ ] "Are ALL volumes `external: true`?"
- [ ] "Is there NO Langfuse service?"
- [ ] "Did `docker compose config` validate?"

### After Phase 6 (Docker Migration):
- [ ] "Does the deal count match the pre-merge number?"
- [ ] "Did I verify both backend→postgres AND agent→agent-db internal networking?"
- [ ] "Did I verify environment isolation (backend gets `zakops` db, not `zakops_agent`)?"

### Before marking COMPLETE:
- [ ] "Does `make validate-local` pass RIGHT NOW?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I create the completion report?"
- [ ] "Is the reference count for 'zakops-backend' actually 0 in all relevant locations?"

---

## File Paths Reference

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/docker-compose.yml` | P3 | Unified service orchestration |
| `/home/zaks/zakops-agent-api/.env.example` | P3 | Shared infra env template with COMPOSE_PROJECT_NAME |
| `/home/zaks/bookkeeping/docs/MONOREPO-CONSOLIDATION-001-COMPLETION.md` | P10 | Completion report |
| `/home/zaks/bookkeeping/mission-checkpoints/MONOREPO-CONSOLIDATION-001.md` | If needed | Context checkpoint (IA-1) |

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/Makefile` | P3, P4 | bootstrap-docker target, backend path updates, convenience targets |
| `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` | P4 | Backend path |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh` | P4 | Backend path |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh` | P4 | Backend path |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh` | P4 | Backend path |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh` | P4 | Backend path |
| `/home/zaks/zakops-agent-api/tools/infra/migration-assertion.sh` | P4 | Backend path |
| `/home/zaks/zakops-agent-api/tools/ops/reset_state.sh` | P4 | Backend compose path |
| `/home/zaks/zakops-agent-api/tools/validation/phase8_double_verify.sh` | P4 | Container name |
| `/home/zaks/zakops-agent-api/CLAUDE.md` | P7 | Remove separate backend repo |
| `/home/zaks/CLAUDE.md` | P7 | Update repos, golden commands |
| `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | P7 | Update project map |
| `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` | P7 | Backend paths (13 refs) |
| `/home/zaks/zakops-agent-api/.claude/rules/backend-api.md` | P7 | Path globs |
| `/home/zaks/.claude/hooks/compact-recovery.sh` | P7 | Backend path |
| `/home/zaks/.claude/hooks/pre-compact.sh` | P7 | Backend path |
| `/home/zaks/.claude/hooks/task-completed.sh` | P7 | Backend path |
| `/home/zaks/.claude/hooks/session-start.sh` | P7 | Backend path |
| `/home/zaks/.claude/CLAUDE.md` | P7 | Backend reference |
| `/home/zaks/.claude/skills/*/SKILL.md` | P7 | Backend references (4 skills) |
| `/home/zaks/.claude/commands/*.md` | P7 | Backend references (4 commands) |
| `/home/zaks/.codex/AGENTS.md` | P7 | Backend paths (24 refs) |
| `/home/zaks/.codex/skills/*/SKILL.md` | P7 | Backend references |
| `/home/zaks/zakops-agent-api/.agents/AGENTS.md` | P7 | Backend paths |
| `/home/zaks/zakops-agent-api/GEMINI.md` | P7 | Backend paths |
| `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md` | P7 | Service topology |
| `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md` | P7 | Backend section |
| `/home/zaks/bookkeeping/CHANGES.md` | P10 | Mission closure entry |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/MONOREPO-CONSOLIDATION-001-PLAN.md` | Design plan with risk analysis |
| `/home/zaks/zakops-backend/docker-compose.yml` | Source compose for unified version |
| `/home/zaks/zakops-agent-api/apps/agent-api/docker-compose.yml` | Agent compose (reference for volume names, networking) |

---

## Stop Condition

Mission is DONE when:
- All 11 AC pass
- `make validate-local` passes
- All services running and healthy from unified compose
- Deal count matches pre-merge snapshot
- Zero stale `zakops-backend` references in runtime paths
- Old repo archived (renamed, not deleted)
- CHANGES.md and completion report written

Do NOT proceed to:
- Offline OpenAPI generation optimization (future enhancement)
- Backend code refactoring
- Zaks-llm consolidation

---
*End of Mission Prompt — MONOREPO-CONSOLIDATION-001*
