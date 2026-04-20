# MISSION: POST-MERGE-STABILIZE-001
## Full-Stack Post-Migration Stabilization & Verification
## Date: 2026-02-15
## Classification: Infrastructure Stabilization
## Prerequisite: MONOREPO-CONSOLIDATION-001 (must be complete — backend is at apps/backend/)
## Successor: None (standalone — closes the migration lifecycle)

---

## Mission Objective

After MONOREPO-CONSOLIDATION-001 moves `zakops-backend` into `apps/backend/`, this mission performs comprehensive full-stack stabilization: verifying every service works, sweeping every configuration for stale references, cleaning up GitHub, validating all automation pipelines, updating all documentation, fixing pre-existing bugs discovered during migration planning, and running browser-level smoke tests.

This is a STABILIZE mission — verify, sweep, fix, document. No new features, no architecture changes.

**What this mission covers that MONOREPO-CONSOLIDATION-001 does NOT:**
- GitHub-level actions (archive old repo, CI workflows, push consolidated repo)
- `settings.json` project scope update (line 131 references old backend path)
- `runtime.topology.json` in packages/contracts (4 stale references)
- `migrate_chat_data.py` hardcoded path to old backend
- `codex-boot.sh` rag_models.py lookup path
- Bookkeeping docs (SERVICE-CATALOG, RUNBOOKS, ONBOARDING)
- Zaks-llm CLAUDE.md and docker-compose comments
- Lab Loop example paths in `labloop-new.sh`
- `health.sh` bug (checks decommissioned port 8090, doesn't check actual backend 8091)
- Dashboard README.md and historical `.claude/reports/`
- GitHub Actions workflows in both repos
- Backend CLAUDE.md disposition (now at `apps/backend/CLAUDE.md`)
- Full browser-level verification of every dashboard page

**What this is NOT:**
- NOT a re-migration (backend is already moved)
- NOT a feature build
- NOT a Zaks-llm consolidation (that remains external)

**Source material:**
- Post-execution checklist: provided during MONOREPO-CONSOLIDATION-001 planning session
- Path reference scans: 223+ references identified across all repos and configs
- GitHub discovery: `zaks2474/zakops-backend` (HTTPS), `zaks2474/zakops` (SSH monorepo)

---

## Context

### What MONOREPO-CONSOLIDATION-001 Already Handled
- Git subtree merge of backend into `apps/backend/`
- Unified docker-compose.yml with external volumes
- Makefile path updates + new backend targets
- Hook path updates (compact-recovery, pre-compact, task-completed, session-start)
- Skill and command path updates
- Agent config updates (Codex AGENTS.md, .agents/AGENTS.md, GEMINI.md)
- CLAUDE.md updates (monorepo, root, MEMORY.md)
- Sync chain verification
- Old repo archived to `zakops-backend-ARCHIVED-*`

### What This Mission Must Still Address (discovered during planning)

| # | Item | Location | Why Consolidation Missed It |
|---|------|----------|-----------------------------|
| 1 | `settings.json` line 131 | `/home/zaks/.claude/settings.json` | Not in the Makefile/tools/hooks sweep — it's a Claude Code config file |
| 2 | `runtime.topology.json` (4 refs) | `packages/contracts/runtime.topology.json` | JSON config, not in the `.sh`/`.ts`/`.py` grep patterns |
| 3 | `migrate_chat_data.py` hardcoded path | `apps/agent-api/scripts/migrate_chat_data.py` | Agent-api internal script, not a sync chain file |
| 4 | `codex-boot.sh` (2 refs) | `/home/zaks/scripts/codex-boot.sh` | External scripts dir, not in monorepo |
| 5 | SERVICE-CATALOG.md (3 refs) | `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md` | Bookkeeping repo, not in monorepo sweep |
| 6 | RUNBOOKS.md (1 ref) | `/home/zaks/bookkeeping/docs/RUNBOOKS.md` | Bookkeeping repo |
| 7 | ONBOARDING.md (5 refs) | `/home/zaks/bookkeeping/docs/ONBOARDING.md` | Bookkeeping repo |
| 8 | Zaks-llm CLAUDE.md + composes (5 refs) | `/home/zaks/Zaks-llm/` | External repo |
| 9 | Lab Loop `labloop-new.sh` examples (3 refs) | `/home/zaks/bookkeeping/labloop/bin/labloop-new.sh` | Lab Loop infra, not in monorepo |
| 10 | Dashboard README.md (3 refs) | `apps/dashboard/README.md` | Documentation, not code |
| 11 | `health.sh` doesn't check 8091 | `/home/zaks/bookkeeping/scripts/health.sh` | Pre-existing bug, not caused by migration |
| 12 | GitHub: archive old repo | `github.com/zaks2474/zakops-backend` | GitHub-level action, not filesystem |
| 13 | GitHub: CI workflows | `.github/workflows/` in both repos | Not checked during consolidation |
| 14 | Backend CLAUDE.md disposition | `apps/backend/CLAUDE.md` | Moved with subtree, needs evaluation |
| 15 | Dashboard `.claude/reports/` (20+ refs) | `apps/dashboard/.claude/reports/*.md` | Historical reports — decide: update or leave |
| 16 | Deal integrity test (1 ref) | `apps/dashboard/src/__tests__/deal-integrity.test.ts` line 114 | References `zakops-backend-postgres-1` container name |

### Locked Decisions from Advisor Review
- `COMPOSE_PROJECT_NAME=zakops` pinned (container names: `zakops-backend-1`, `zakops-postgres-1`, etc.)
- Langfuse dropped entirely
- Agent-db on host port 5433
- `external: true` for all data volumes with `bootstrap-docker` Makefile target

---

## Glossary

| Term | Definition |
|------|-----------|
| Stale reference | Any path, container name, or command that points to `zakops-backend` as a standalone repo |
| Historical reference | A reference in a completed mission report, audit, or QA artifact — these document what WAS true and should NOT be updated |
| Runtime reference | A reference in code, config, hook, or script that is actively used during system operation — these MUST be updated |
| Archiving (GitHub) | Setting a repo to read-only mode — prevents pushes, disables issues/PRs, preserves history |

---

## Architectural Constraints

Per standing rules plus migration-specific:
- **Container names changed** — with `COMPOSE_PROJECT_NAME=zakops`, containers are now `zakops-backend-1` (was `zakops-backend-backend-1`), `zakops-postgres-1` (was `zakops-backend-postgres-1`), `zakops-redis-1` (was `zakops-backend-redis-1`), `zakops-outbox-worker-1` (was `zakops-backend-outbox-worker-1`)
- **Historical docs are read-only** — audit reports, QA reports, forensic reports, completed mission artifacts contain historical references that must NOT be updated (they document what was true at the time)
- **Port 8091 stays the same** — all `localhost:8091` references remain valid
- **Port 8090 is FORBIDDEN** — and `health.sh` incorrectly checks it (will be fixed)
- **Zaks-llm changes are documentation-only** — no runtime code changes in the RAG repo

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Historical references in bookkeeping reports get wrongly updated, corrupting audit trail | MEDIUM | Audit trail integrity lost | Guardrail #3 explicitly forbids updating historical artifacts; grep exclusions filter them out |
| 2 | `settings.json` edit breaks Claude Code permissions | MEDIUM | Claude Code sessions fail to start | P1 edits only line 131 (project scope path); backup settings.json before edit |
| 3 | GitHub archive locks out future hot-fixes to old backend | LOW | Can't push emergency fixes | Archive is reversible via GitHub settings; plus the full code is in the monorepo now |
| 4 | Container name changes in test assertions cause false test failures | HIGH | Tests break on new container names | P1 updates `deal-integrity.test.ts` container name reference |
| 5 | `health.sh` fix introduces false positives/negatives | LOW | Health checks become unreliable | Replace decommissioned port checks with actual service checks; verify manually |

---

<!-- Adopted from Improvement Area IA-2 -->
## Crash Recovery

If resuming after a crash:

1. `grep -c 'zakops-backend' /home/zaks/.claude/settings.json` — if 0, P1 settings.json done
2. `grep -c 'zakops-backend' /home/zaks/zakops-agent-api/packages/contracts/runtime.topology.json` — if 0, P1 topology done
3. `gh repo view zaks2474/zakops-backend --json isArchived 2>/dev/null | grep true` — if true, P2 GitHub done
4. `grep -c 'zakops-backend' /home/zaks/bookkeeping/docs/SERVICE-CATALOG.md` — if 0, P3 docs done
5. `grep -c '8091' /home/zaks/bookkeeping/scripts/health.sh` — if >0, P4 health.sh fixed

---

## Contract Surfaces Affected

No contract surfaces are modified — this mission only updates references and documentation. However, the following validators must pass post-stabilization:

| Surface | Gate |
|---------|------|
| All 17 | `make validate-local` |
| S10-S13 | `make validate-surface10` through `make validate-surface13` (paths were updated in consolidation) |
| S17 | `make validate-surface17` (dashboard route coverage) |

---

## Phase 0 — Service & Data Verification
**Complexity:** M
**Estimated touch points:** 0 (read-only verification, 6 checkpoint categories)

**Purpose:** Verify all services are healthy, data survived the migration, Docker infrastructure is correct, and the sync chain works. This is the "did the migration actually work?" gate.

### Blast Radius
- **Services affected:** None (verification only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks

- P0-01: **Service health checks** — Verify each service responds:
  | Service | Command | Expected |
  |---------|---------|----------|
  | Backend | `curl -sf http://localhost:8091/health/ready` | 200 |
  | Agent API | `curl -sf http://localhost:8095/health` | 200 |
  | Dashboard | `curl -sf http://localhost:3003` | HTML |
  | PostgreSQL | `psql -U zakops -h localhost -d zakops -c "SELECT 1"` | 1 row |
  | Agent DB | `docker exec zakops-agent-db psql -U agent -d zakops_agent -c "SELECT 1"` | 1 row |
  | Redis | `redis-cli ping` | PONG |
  | RAG | `curl -sf http://localhost:8052/health` | 200 |
  - **Checkpoint:** All 7 services respond correctly

- P0-02: **Data integrity** — Verify deal data survived:
  - `curl -sf http://localhost:8091/api/deals?limit=5 | jq length` — returns 5
  - `curl -sf http://localhost:8091/api/pipeline/summary` — returns stage counts
  - `psql -U zakops -h localhost -d zakops -t -A -c "SELECT count(*) FROM zakops.deals"` — non-zero, matches pre-merge count
  - **Checkpoint:** Deal count matches pre-merge, pipeline summary has data

- P0-03: **Docker infrastructure** — Verify unified compose:
  - `docker ps --format '{{.Names}} {{.Status}}'` — all containers healthy
  - `docker compose -f /home/zaks/zakops-agent-api/docker-compose.yml ps` — all services listed
  - `docker volume inspect zakops_postgres_data` — exists
  - **COMPOSE_PROJECT_NAME verification (CRITICAL):** `docker inspect zakops-backend-1 --format '{{.Name}}' 2>/dev/null && echo "OK" || echo "FAIL: Container name wrong — check COMPOSE_PROJECT_NAME"` — if this fails, the entire container naming scheme in this mission is wrong. STOP and fix.
  - `ss -tlnp | grep -E '5432|5433|6379|8091|8095'` — each port bound once (5433 = agent-db)
  - **Agent-db on 5433:** `psql -U agent -h localhost -p 5433 -d zakops_agent -c "SELECT 1"` — confirms agent-db is reachable on the locked port
  - No old-stack containers: `docker ps | grep 'zakops-backend-backend'` — empty
  - **Checkpoint:** Single unified stack running, COMPOSE_PROJECT_NAME=zakops confirmed, agent-db on 5433, no orphan containers

- P0-04: **Backend .env existence** — Verify the backend env file was copied during consolidation:
  - `test -f /home/zaks/zakops-agent-api/apps/backend/.env && echo "OK" || echo "MISSING: backend .env"`
  - **IF MISSING:** The consolidation plan required copying `/home/zaks/zakops-backend/.env` to `apps/backend/.env`. Docker services may appear healthy from baked-in env vars, but `cd apps/backend && bash scripts/dev.sh` (Phase 4) will fail without this file. Copy from the ARCHIVED backup if needed.
  - **Checkpoint:** `apps/backend/.env` exists

- P0-05: **Sync chain** — Verify codegen still works:
  - `cd /home/zaks/zakops-agent-api && make sync-all-types` — exit 0
  - `cd apps/dashboard && npx tsc --noEmit` — 0 errors
  - **Checkpoint:** Full sync chain passes

- P0-06: **Validation pipeline** — Run offline validation:
  - `make validate-local` — PASS
  - `make infra-check` — PASS
  - **Checkpoint:** Both pass

### Gate P0
- All 7 services healthy
- Deal data intact
- COMPOSE_PROJECT_NAME=zakops confirmed (container naming correct)
- Agent-db reachable on port 5433
- `apps/backend/.env` exists
- Unified compose running (no orphans)
- Sync chain passes
- `make validate-local` passes

**IF ANY P0 CHECK FAILS:** Stop. The migration has a problem that must be fixed before stabilization continues. Go back to MONOREPO-CONSOLIDATION-001 rollback procedures.

---

## Phase 1 — Configuration Sweep (Runtime References)
**Complexity:** M
**Estimated touch points:** 8 files + crontab + git remotes

**Purpose:** Update all runtime configurations that still reference the old `zakops-backend` path or old container names.

### Blast Radius
- **Services affected:** Claude Code sessions (settings.json change)
- **Pages affected:** None
- **Downstream consumers:** Codex boot script, contract topology, agent migration script

### Tasks

- P1-01: **Update `settings.json`** — `/home/zaks/.claude/settings.json` line 131 references `/home/zaks/zakops-backend`. This is likely a project scope path. Change it to `/home/zaks/zakops-agent-api/apps/backend` (or remove if redundant since the monorepo root already covers it).
  - **Backup first:** `cp /home/zaks/.claude/settings.json /home/zaks/.claude/settings.json.bak`
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/.claude/settings.json` returns 0
  - **Verify Claude Code still works:** Start a new session, confirm boot diagnostics pass

- P1-02: **Update `runtime.topology.json`** — `/home/zaks/zakops-agent-api/packages/contracts/runtime.topology.json` has 4 references:
  - `"service": "zakops-backend"` → update to reflect unified compose
  - `"migrations_dir": "zakops-backend/db/migrations"` → `"apps/backend/db/migrations"`
  - `"container": "zakops-backend-postgres-1"` → `"zakops-postgres-1"` (unified compose name)
  - `"container": "zakops-backend-1"` → `"zakops-backend-1"` (this may already be correct with COMPOSE_PROJECT_NAME=zakops)
  - **Checkpoint:** `grep -c 'zakops-backend' packages/contracts/runtime.topology.json` returns 0

- P1-03: **Update `migrate_chat_data.py`** — `/home/zaks/zakops-agent-api/apps/agent-api/scripts/migrate_chat_data.py` has a hardcoded path at line 190: `"/home/zaks/zakops-backend/data/chat_persistence.db"`. But this may not be the only reference — **scan the FULL FILE** for any `zakops-backend` reference, including `sys.path.append()`, imports, or other hardcoded paths.
  - `grep -n 'zakops-backend' apps/agent-api/scripts/migrate_chat_data.py` — find ALL references, not just line 190
  - **Decision tree:**
    - **IF** the `data/` directory exists at `apps/backend/data/` → update data path(s)
    - **IF** `sys.path.append` or imports reference old backend → update those too
    - **IF** it doesn't exist and the script is a one-time migration that already ran → add a comment noting the old path and that migration is complete
  - **Checkpoint:** `grep -c 'zakops-backend' apps/agent-api/scripts/migrate_chat_data.py` returns 0

- P1-04: **Update `codex-boot.sh`** — `/home/zaks/scripts/codex-boot.sh` lines 163+169 look for `rag_models.py` in `/home/zaks/zakops-backend`. Update to `/home/zaks/zakops-agent-api/apps/backend`.
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/scripts/codex-boot.sh` returns 0
  - WSL safety: `sed -i 's/\r$//' /home/zaks/scripts/codex-boot.sh && sudo chown zaks:zaks /home/zaks/scripts/codex-boot.sh`

- P1-05: **Update deal-integrity test** — `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/deal-integrity.test.ts` line 114 references `zakops-backend-postgres-1`. Update to `zakops-postgres-1` (the new container name under unified compose).
  - **Checkpoint:** `grep -c 'zakops-backend-postgres-1' apps/dashboard/src/__tests__/deal-integrity.test.ts` returns 0

- P1-06: **Check cron jobs for stale references** — Filesystem grep won't catch crontab entries:
  - `crontab -l 2>/dev/null | grep -i 'zakops-backend'`
  - `sudo crontab -l 2>/dev/null | grep -i 'zakops-backend'`
  - **Decision tree:**
    - **IF** matches found → update the crontab entries to use new paths
    - **IF** no matches → record "no cron references" in completion report
  - **Checkpoint:** Zero crontab references to old backend path

- P1-07: **Check git remotes for stale references** — Subtree merge may have left a remote:
  - `cd /home/zaks/zakops-agent-api && git remote -v | grep zakops-backend`
  - **Decision tree:**
    - **IF** a remote exists → `git remote remove <name>` (it points to the archived repo)
    - **IF** no match → no action needed
  - **Checkpoint:** No git remotes referencing the old backend repo

- P1-08: **Update backend CLAUDE.md** — `apps/backend/CLAUDE.md` (moved from zakops-backend) references itself as a standalone repo. Either:
  - **Option A:** Update it to reflect that it's now part of the monorepo (change paths, golden commands, container names)
  - **Option B:** Add a header noting it's archived reference material, and the monorepo CLAUDE.md is authoritative
  - **Decision tree:** Option B is simpler and safer — add a 2-line header: `> **NOTE:** This file was migrated from the standalone zakops-backend repo. The authoritative guide is the monorepo root CLAUDE.md.`

### Rollback Plan
1. `cp /home/zaks/.claude/settings.json.bak /home/zaks/.claude/settings.json`
2. `git checkout -- packages/contracts/runtime.topology.json apps/agent-api/scripts/migrate_chat_data.py apps/dashboard/src/__tests__/deal-integrity.test.ts`

### Gate P1
- `grep -c 'zakops-backend' /home/zaks/.claude/settings.json` → 0
- `grep -c 'zakops-backend' packages/contracts/runtime.topology.json` → 0
- `grep -c 'zakops-backend' apps/agent-api/scripts/migrate_chat_data.py` → 0
- `grep -c 'zakops-backend' /home/zaks/scripts/codex-boot.sh` → 0
- `grep -c 'zakops-backend-postgres-1' apps/dashboard/src/__tests__/deal-integrity.test.ts` → 0
- Zero crontab references to old backend path
- No git remotes referencing old backend repo
- `apps/backend/CLAUDE.md` has deprecation header

---

## Phase 2 — GitHub & CI Cleanup
**Complexity:** M
**Estimated touch points:** 2 GitHub repos + CI configs

**Purpose:** Archive the old GitHub repo, verify/update CI workflows, push the consolidated monorepo.

### Blast Radius
- **Services affected:** None (GitHub-level only)
- **Pages affected:** None
- **Downstream consumers:** CI pipelines, GitHub integrations

### Tasks

- P2-01: **Inspect CI workflows** — Read both (NOTE: the old backend repo was archived/renamed by MONOREPO-CONSOLIDATION-001):
  - **Backend CI — try paths in order (the old repo is renamed):**
    1. `ls /home/zaks/zakops-agent-api/apps/backend/.github/workflows/*.yml 2>/dev/null` — subtree may have included it
    2. `ls /home/zaks/zakops-backend-ARCHIVED-*/.github/workflows/*.yml 2>/dev/null` — archived path (date suffix varies)
    3. `gh api repos/zaks2474/zakops-backend/contents/.github/workflows 2>/dev/null` — read from GitHub (works even after archive)
  - Use whichever path exists. Read the workflows to understand what backend CI does.
  - `cat /home/zaks/zakops-agent-api/.github/workflows/*.yml` — what does the monorepo CI do?
  - **Decision tree:**
    - **IF** backend CI has useful workflows (tests, linting) → port them to monorepo CI, scoped to `apps/backend/`
    - **IF** backend CI is stale or duplicative → don't port, document in completion report
    - **IF** monorepo CI references the old backend repo → update those references
  - **Checkpoint:** CI workflow analysis documented

- P2-02: **Check for open issues/PRs** — `gh repo view zaks2474/zakops-backend --json openIssues,pullRequests 2>/dev/null || echo "Check manually"`
  - **Decision tree:**
    - **IF** open issues exist → transfer them to the monorepo or close with a note pointing to the new location
    - **IF** open PRs exist → close them with a note that the code has moved to `zakops/apps/backend/`

- P2-03: **Push consolidated monorepo** — Ensure all migration commits are pushed:
  - `cd /home/zaks/zakops-agent-api && git push origin main`
  - **Checkpoint:** `git status` shows "Your branch is up to date with 'origin/main'"

- P2-04: **Archive old backend repo on GitHub** — `gh repo archive zaks2474/zakops-backend --yes`
  - This makes the repo read-only: no pushes, no issues, no PRs
  - History is fully preserved and browsable
  - **Checkpoint:** `gh repo view zaks2474/zakops-backend --json isArchived` returns `true`

- P2-05: **Update monorepo repo description** — `gh repo edit zaks2474/zakops --description "ZakOps platform — Dashboard + Agent API + Backend + Contracts"` (if the current description doesn't mention backend)

- P2-06: **Check CODEOWNERS** — `/home/zaks/zakops-agent-api/.github/CODEOWNERS` may need updating if it has ownership rules that should cover `apps/backend/`

### Rollback Plan
1. `gh repo unarchive zaks2474/zakops-backend` — reverses the archive
2. Git push can be reverted with a force push (but this is destructive — only if necessary)

### Gate P2
- All migration commits pushed to GitHub
- Old repo archived
- No open issues/PRs left dangling
- CI workflows evaluated and updated if needed
- CODEOWNERS reviewed

---

## Phase 3 — Documentation Sweep
**Complexity:** L
**Estimated touch points:** 10-15 files across 3 repos

**Purpose:** Update all documentation that references the old backend location. Distinguish between runtime docs (update) and historical docs (leave alone).

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** New developer onboarding, operational runbooks, session orientation

### Tasks

- P3-01: **Update SERVICE-CATALOG.md** — `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md` (3 refs):
  - Path: `/home/zaks/zakops-backend` → `/home/zaks/zakops-agent-api/apps/backend`
  - Start/stop: `cd /home/zaks/zakops-backend && docker compose ...` → `cd /home/zaks/zakops-agent-api && docker compose ...`
  - Compose project name update
  - **Checkpoint:** `grep -c 'zakops-backend' SERVICE-CATALOG.md` returns 0

- P3-02: **Update RUNBOOKS.md** — `/home/zaks/bookkeeping/docs/RUNBOOKS.md` (1 ref):
  - Backend restart command path update
  - **Checkpoint:** `grep -c 'zakops-backend' RUNBOOKS.md` returns 0

- P3-03: **Update ONBOARDING.md** — `/home/zaks/bookkeeping/docs/ONBOARDING.md` (5 refs):
  - Repo table: remove standalone backend row, update monorepo description to include backend
  - Service map: update container names
  - Database section: update migrations path
  - Rules table: update backend-api.md path reference
  - **Checkpoint:** `grep -c 'zakops-backend' ONBOARDING.md` returns 0

- P3-04: **Update Zaks-llm CLAUDE.md** — `/home/zaks/Zaks-llm/CLAUDE.md` (2 refs):
  - Line 4: "active application code lives in `zakops-backend`" → "lives in `zakops-agent-api/apps/backend`"
  - Line 45: reference to `zakops-backend` on port 8091 → update path
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/Zaks-llm/CLAUDE.md` returns 0

- P3-05: **Update Zaks-llm docker-compose comments** — 2 files have comments referencing `zakops-backend-postgres-1`:
  - `/home/zaks/Zaks-llm/src/deal_origination/docker-compose.deal-engine.yml` line 4
  - `/home/zaks/Zaks-llm/docker-compose.deal-engine.yml` line 4
  - `/home/zaks/Zaks-llm/src/api/server.py` line 633 (comment only)
  - These are comments, not runtime — update for accuracy
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/Zaks-llm/*.yml /home/zaks/Zaks-llm/src/api/server.py /home/zaks/Zaks-llm/CLAUDE.md` returns 0

- P3-06: **Update Lab Loop example paths** — `/home/zaks/bookkeeping/labloop/bin/labloop-new.sh` lines 68-69, 107:
  - Example paths show `--repo /home/zaks/zakops-backend` → update to `--repo /home/zaks/zakops-agent-api`
  - Interactive prompt default → update
  - **Note:** Historical task missions in `labloop/tasks/` are artifacts — do NOT update them
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/bookkeeping/labloop/bin/labloop-new.sh` returns 0

- P3-07: **Update Dashboard README.md** — `/home/zaks/zakops-agent-api/apps/dashboard/README.md` (3 refs):
  - Architecture diagram reference
  - Related repos table
  - Prerequisites section
  - **Checkpoint:** `grep -c 'zakops-backend' apps/dashboard/README.md` returns 0

- P3-08: **Mark historical reports as-is** — The following contain references but are historical artifacts that must NOT be modified:
  - `apps/dashboard/.claude/reports/*.md` (20+ refs) — historical mission reports
  - `bookkeeping/qa-results/`, `bookkeeping/qa/`, `bookkeeping/reports/`, `bookkeeping/audits/` — QA and forensic artifacts
  - `bookkeeping/missions/` — completed mission prompts and evidence
  - `bookkeeping/labloop/tasks/*/` — completed Lab Loop task artifacts
  - **Action:** No changes. Document this decision in the completion report.

### Decision Tree
- **IF** a file is in `bookkeeping/docs/` (operational documentation) → UPDATE it
- **IF** a file is in `bookkeeping/qa*/`, `bookkeeping/audits/`, `bookkeeping/missions/`, `bookkeeping/reports/` → LEAVE it (historical)
- **IF** a file is in `bookkeeping/labloop/bin/` (tooling) → UPDATE it
- **IF** a file is in `bookkeeping/labloop/tasks/` (task artifacts) → LEAVE it (historical)

### Rollback Plan
1. `git checkout -- docs/SERVICE-CATALOG.md docs/RUNBOOKS.md docs/ONBOARDING.md` in bookkeeping
2. `git checkout -- CLAUDE.md` in Zaks-llm
3. `git checkout -- apps/dashboard/README.md` in monorepo

### Gate P3
- 0 stale references in operational docs (SERVICE-CATALOG, RUNBOOKS, ONBOARDING)
- 0 stale references in Zaks-llm CLAUDE.md
- 0 stale references in Lab Loop tooling scripts
- 0 stale references in Dashboard README
- Historical artifacts confirmed untouched

---

## Phase 4 — Developer Workflow & Health Script Fix
**Complexity:** M
**Estimated touch points:** 3-5 files

**Purpose:** Ensure all developer-facing workflows (make targets, deploy skills, health checks) work correctly with the new layout. Fix the pre-existing `health.sh` bug.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** Developer workflow, monitoring

### Tasks

- P4-01: **Fix `health.sh` bug** — `/home/zaks/bookkeeping/scripts/health.sh` checks:
  - Port 8090 (`"Claude API (8090)"`) — **DECOMMISSIONED** — remove this check
  - Port 8080 (`"ZakOps API (8080)"`) — **doesn't exist** — remove this check
  - **Missing:** Port 8091 (Backend API) — add this check
  - **Missing:** Port 8095 (Agent API) — add this check
  - **Missing:** Port 3003 (Dashboard) — add this check
  - Updated checks array should include:
    - Backend API (8091): `curl -fsS --max-time 3 http://localhost:8091/health/ready`
    - Agent API (8095): `curl -fsS --max-time 3 http://localhost:8095/health`
    - Dashboard (3003): `curl -fsS --max-time 3 http://localhost:3003`
    - OpenWebUI (3000), vLLM (8000), RAG (8052), MCP Bridge (9100) — keep these
    - Docker daemon — keep
  - WSL safety: `sed -i 's/\r$//' health.sh && sudo chown zaks:zaks health.sh`
  - **Checkpoint:** `bash /home/zaks/bookkeeping/scripts/health.sh` — Backend API shows OK, no 8090/8080 checks

- P4-02: **Verify Makefile targets work** — Test each new target added during consolidation:
  - `make bootstrap-docker` — creates volumes (idempotent)
  - `make backend-dev` (if added) — starts backend
  - `make backend-test` (if added) — runs tests
  - `make backend-build` (if added) — builds Docker image
  - `make sync-all-types` — includes sync-agent-configs
  - **Checkpoint:** All targets execute without error

- P4-03: **Verify deploy-backend skill** — The deploy-backend skill/command at `/home/zaks/.claude/commands/deploy-backend.md` should now reference the unified compose from the monorepo root, not the old `cd /home/zaks/zakops-backend` path.
  - **Decision tree:**
    - **IF** already updated in consolidation → verify
    - **IF** still references old path → update
  - **Checkpoint:** `grep -c 'zakops-backend' /home/zaks/.claude/commands/deploy-backend.md` returns 0

- P4-04: **Verify tail-logs command** — `/home/zaks/.claude/commands/tail.md` references `zakops-backend-backend-1` container name. Should now reference `zakops-backend-1`.
  - **Decision tree:**
    - **IF** already updated → verify
    - **IF** still references old name → update
  - **Checkpoint:** Container name references are correct for unified compose

- P4-05: **Run backend tests from new location** — `cd /home/zaks/zakops-agent-api/apps/backend && bash scripts/test.sh`
  - **Decision tree:**
    - **IF** tests pass → record result
    - **IF** tests fail due to path issues → fix SCRIPT_DIR in test.sh
    - **IF** tests fail due to container name changes → update test fixtures
  - **Checkpoint:** Tests pass (or failures are documented with root cause)

### Rollback Plan
1. `git checkout -- scripts/health.sh` in bookkeeping
2. Other changes are command/skill configs — restore from backup

### Gate P4
- `health.sh` checks 8091 and 8095, does NOT check 8090 or 8080
- All Makefile targets work
- Deploy skill references correct paths
- Backend tests pass from new location

---

## Phase 5 — Browser Verification
**Complexity:** M
**Estimated touch points:** 0 (verification only)

**Purpose:** Verify every dashboard page renders correctly with real data. Curl success does NOT equal UI works.

### Blast Radius
- **Services affected:** None
- **Pages affected:** All (read-only verification)

### Tasks

- P5-01: **Dashboard must be running** — `curl -sf http://localhost:3003` returns HTML. If not running: `cd /home/zaks/zakops-agent-api/apps/dashboard && npm run dev`

- P5-02: **Browser page verification** — Open each page and verify it loads with data:

  | Page | URL | What to Verify |
  |------|-----|----------------|
  | Pipeline/Home | `http://localhost:3003` | Pipeline stages render, deal counts match server-side numbers |
  | Deal detail | Click any deal from pipeline | Detail page loads, transitions visible, events listed |
  | Quarantine | `/quarantine` | Table renders, approve/reject buttons visible |
  | Email triage | `/email-triage` | Triage queue loads, items visible |
  | Settings | `/settings` | All sections render without errors |
  | Agent activity | `/agent-activity` | Activity feed renders (or graceful "no activity" message) |
  | Onboarding | `/onboarding` | Page loads (if applicable) |

  - **Checkpoint:** All pages load with data, no 502 errors, no blank screens, no console errors

- P5-03: **Check browser console** — Open DevTools on each page and verify:
  - No `Failed to fetch` errors
  - No `500` or `502` responses in Network tab
  - No React hydration errors
  - `console.error` only for genuinely unexpected failures (per Surface 9)

### Gate P5
- All dashboard pages render correctly
- No 502 errors
- No browser console errors (expected degradation uses console.warn, not console.error)

---

## Phase 6 — Full Regression & Bookkeeping
**Complexity:** M
**Estimated touch points:** 2 files (CHANGES.md, completion report)

**Purpose:** Run comprehensive validation suite, record all changes, create completion report.

### Blast Radius
- **Services affected:** None

### Tasks

- P6-01: **Full offline validation** — `make validate-local` — PASS
- P6-02: **TypeScript compilation** — `cd apps/dashboard && npx tsc --noEmit` — 0 errors
- P6-03: **Contract surface validation** — `make validate-contract-surfaces` — 17/17
- P6-04: **Surface count consistency** — `bash tools/infra/validate-surface-count-consistency.sh` — 4-way consistent
- P6-05: **Governance surfaces** — `make validate-surface10 && make validate-surface11 && make validate-surface12 && make validate-surface13` — all PASS
- P6-06: **Live validation** — `make validate-live` — PASS
- P6-07: **Endpoint liveness** — `bash tools/infra/validate-endpoint-liveness.sh` — all endpoints respond JSON
- P6-08: **Hook syntax verification** — `bash -n` on all hooks in `/home/zaks/.claude/hooks/`
- P6-09: **Boot diagnostics** — `bash /home/zaks/.claude/hooks/session-start.sh` — all 7 CHECKs PASS

- P6-10: **Zero stale references final sweep** — Run the comprehensive grep:
  ```
  grep -rn '/home/zaks/zakops-backend' \
    /home/zaks/zakops-agent-api/ \
    /home/zaks/.claude/ \
    /home/zaks/.codex/ \
    /home/zaks/CLAUDE.md \
    /home/zaks/bookkeeping/docs/ \
    /home/zaks/bookkeeping/scripts/ \
    /home/zaks/bookkeeping/labloop/bin/ \
    /home/zaks/scripts/ \
    /home/zaks/Zaks-llm/ \
    --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=.git \
    --exclude-dir=models --exclude-dir=embeddings --exclude-dir=.cache \
    --include='*.sh' --include='*.ts' --include='*.tsx' \
    --include='*.py' --include='*.md' --include='Makefile' \
    --include='*.json' --include='*.yml' --include='*.yaml' \
    2>/dev/null \
    | grep -v node_modules | grep -v .next | grep -v .git \
    | grep -v ARCHIVED | grep -v PLAN | grep -v COMPLETION \
    | grep -v CHANGES | grep -v '.claude/reports/' \
    | grep -v 'bookkeeping/qa' | grep -v 'bookkeeping/audits' \
    | grep -v 'bookkeeping/missions' | grep -v 'bookkeeping/reports' \
    | grep -v 'labloop/tasks/'
  ```
  **Expected:** 0 lines

- P6-10b: **Targeted .claude/ safety check** — The main sweep excludes `.claude/reports/` to protect historical artifacts. This secondary check verifies no active Claude Code configs were masked by that exclusion:
  ```
  grep -rn 'zakops-backend' /home/zaks/.claude/ \
    --include='*.md' --include='*.json' --include='*.sh' \
    | grep -v reports/ | grep -v settings.json.bak
  ```
  **Expected:** 0 lines (any match = active config still referencing old backend)

- P6-10c: **Crontab final check** — Verify cron was cleaned in P1-06:
  ```
  (crontab -l 2>/dev/null; sudo crontab -l 2>/dev/null) | grep -i 'zakops-backend'
  ```
  **Expected:** 0 lines

- P6-11: **Record in CHANGES.md** — Full entry in `/home/zaks/bookkeeping/CHANGES.md`
- P6-12: **Create completion report** — `/home/zaks/bookkeeping/docs/POST-MERGE-STABILIZE-001-COMPLETION.md`
- P6-13: **Update MEMORY.md completed missions** — Add both MONOREPO-CONSOLIDATION-001 and POST-MERGE-STABILIZE-001 to the completed missions list

### Gate P6
- `make validate-local` PASS
- `npx tsc --noEmit` 0 errors
- 17/17 contract surfaces pass
- All hooks pass syntax check
- Boot diagnostics: 7/7 PASS
- Zero stale references in runtime paths (main sweep)
- Zero stale references in `.claude/` active configs (targeted check)
- Zero stale references in crontab (final check)
- CHANGES.md updated
- Completion report created
- MEMORY.md updated

---

## Dependency Graph

```
Phase 0 (Service & Data Verification)
    │
    │  ← STOP if any P0 check fails
    │
    ├──────────────────────┐
    ▼                      ▼
Phase 1 (Config Sweep)   Phase 2 (GitHub Cleanup)
    │                      │
    └──────────┬───────────┘
               ▼
       Phase 3 (Documentation Sweep)
               │
               ▼
       Phase 4 (Developer Workflow + health.sh)
               │
               ▼
       Phase 5 (Browser Verification)
               │
               ▼
       Phase 6 (Full Regression & Bookkeeping)
```

Phases 1 and 2 can run in parallel (no dependencies). All other phases are sequential.

---

## Acceptance Criteria

### AC-1: All Services Healthy
All 7 services respond correctly (Backend 8091, Agent 8095, Dashboard 3003, PostgreSQL, Agent DB, Redis, RAG).

### AC-2: Data Intact
Deal count matches pre-merge. Pipeline summary returns valid stage data.

### AC-3: Zero Runtime Stale References
The comprehensive grep sweep returns 0 matches (excluding historical artifacts).

### AC-4: GitHub Cleaned Up
Old `zakops-backend` repo archived on GitHub. All migration commits pushed to `zakops`. No dangling issues/PRs.

### AC-5: Documentation Updated
SERVICE-CATALOG, RUNBOOKS, ONBOARDING, Zaks-llm CLAUDE.md, Dashboard README, Lab Loop examples all updated. Historical artifacts preserved untouched.

### AC-6: Health Script Fixed
`health.sh` checks ports 8091 and 8095. Does NOT check decommissioned 8090 or nonexistent 8080.

### AC-7: Configuration Swept
`settings.json`, `runtime.topology.json`, `codex-boot.sh`, `migrate_chat_data.py`, `deal-integrity.test.ts` all updated.

### AC-8: CI Evaluated
GitHub Actions workflows in both repos reviewed. Backend CI ported to monorepo if useful.

### AC-9: Browser Verified
All dashboard pages render correctly with real data. No 502 errors. No console errors.

### AC-10: Developer Workflow Works
All Makefile targets work. Deploy skill references correct paths. Backend tests pass from new location.

### AC-11: Full Validation Passes
`make validate-local`, `npx tsc --noEmit`, `make validate-contract-surfaces`, boot diagnostics — all PASS.

### AC-12: Bookkeeping
CHANGES.md updated. Completion report created. MEMORY.md completed missions updated.

---

## Guardrails

1. **Scope fence:** This is a STABILIZE mission. Do not add new features, refactor code, or change architecture.
2. **Historical artifacts are sacred:** Do NOT modify files in `bookkeeping/qa*/`, `bookkeeping/audits/`, `bookkeeping/missions/`, `bookkeeping/reports/`, `bookkeeping/labloop/tasks/`, or `apps/dashboard/.claude/reports/`. These document what was true at the time.
3. **Generated file protection:** Per standing deny rules — do not edit `*.generated.ts` or `*_models.py`.
4. **settings.json backup:** Create a backup before editing `settings.json`. If Claude Code breaks, restore immediately.
5. **WSL safety:** CRLF strip and ownership fix on any modified .sh files.
6. **Port 8090 FORBIDDEN** — remove from health checks, never add back.
7. **GitHub archive is reversible** — `gh repo unarchive` restores full functionality if needed.
8. **Browser verification is mandatory** — `curl` success is not sufficient proof that the UI works.
9. **Zaks-llm changes are documentation-only** — do not modify runtime Python code or Docker configs in Zaks-llm.
10. **No force pushes** — push normally. If conflicts arise, resolve them.

---

## Executor Self-Check Prompts

### After Phase 0 (Verification):
- [ ] "Did ALL 7 services respond? Not just 3 or 4?"
- [ ] "Did I compare the deal count to the pre-merge number, or just check it's non-zero?"

### After Phase 1 (Config Sweep):
- [ ] "Did I back up settings.json before editing?"
- [ ] "Did I verify Claude Code still works after the settings.json change?"
- [ ] "Did I handle the container name changes (zakops-backend-backend-1 → zakops-backend-1)?"

### After Phase 3 (Docs):
- [ ] "Did I update ONLY operational docs? Did I leave all historical artifacts untouched?"
- [ ] "Did I update Zaks-llm CLAUDE.md? It's in a different repo."

### After Phase 4 (Workflow):
- [ ] "Did I actually fix health.sh to check 8091 and 8095?"
- [ ] "Did I remove the 8090 and 8080 checks?"

### Before marking COMPLETE:
- [ ] "Does `make validate-local` pass RIGHT NOW?"
- [ ] "Did I run the comprehensive stale-reference grep?"
- [ ] "Did I open the dashboard in a BROWSER, not just curl it?"
- [ ] "Did I update CHANGES.md and create the completion report?"
- [ ] "Did I update MEMORY.md completed missions list?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/.claude/settings.json` | P1 | Remove/update old backend project scope path |
| `/home/zaks/zakops-agent-api/packages/contracts/runtime.topology.json` | P1 | Update 4 backend references |
| `/home/zaks/zakops-agent-api/apps/agent-api/scripts/migrate_chat_data.py` | P1 | Update hardcoded backend path |
| `/home/zaks/scripts/codex-boot.sh` | P1 | Update rag_models.py lookup path |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/__tests__/deal-integrity.test.ts` | P1 | Update container name |
| `/home/zaks/zakops-agent-api/apps/backend/CLAUDE.md` | P1 | Add deprecation header |
| `/home/zaks/zakops-agent-api/.github/workflows/*.yml` | P2 | Update if backend CI ported |
| `/home/zaks/zakops-agent-api/.github/CODEOWNERS` | P2 | Add apps/backend/ ownership |
| `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md` | P3 | Update backend section |
| `/home/zaks/bookkeeping/docs/RUNBOOKS.md` | P3 | Update backend restart command |
| `/home/zaks/bookkeeping/docs/ONBOARDING.md` | P3 | Update repo table, service map, DB section |
| `/home/zaks/Zaks-llm/CLAUDE.md` | P3 | Update backend reference |
| `/home/zaks/Zaks-llm/docker-compose.deal-engine.yml` | P3 | Update comment |
| `/home/zaks/Zaks-llm/src/deal_origination/docker-compose.deal-engine.yml` | P3 | Update comment |
| `/home/zaks/Zaks-llm/src/api/server.py` | P3 | Update comment |
| `/home/zaks/bookkeeping/labloop/bin/labloop-new.sh` | P3 | Update example paths |
| `/home/zaks/zakops-agent-api/apps/dashboard/README.md` | P3 | Update architecture references |
| `/home/zaks/bookkeeping/scripts/health.sh` | P4 | Fix: add 8091/8095/3003, remove 8090/8080 |
| `/home/zaks/bookkeeping/CHANGES.md` | P6 | Mission closure entry |
| `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | P6 | Add completed missions |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/POST-MERGE-STABILIZE-001-COMPLETION.md` | P6 | Completion report |
| `/home/zaks/.claude/settings.json.bak` | P1 | Backup before settings edit |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/MONOREPO-CONSOLIDATION-001-COMPLETION.md` | Confirms consolidation is complete |
| `/home/zaks/zakops-agent-api/docker-compose.yml` | Unified compose (reference for container names) |
| `bookkeeping/qa*/`, `bookkeeping/audits/`, `bookkeeping/missions/` | Historical artifacts — read to understand, do NOT modify |

---

## Stop Condition

Mission is DONE when:
- All 12 AC pass
- All 7 services healthy
- Deal data intact
- Zero stale runtime references
- GitHub old repo archived, monorepo pushed
- All operational docs updated, historical docs untouched
- Health script fixed
- All dashboard pages verified in browser
- `make validate-local` passes
- Boot diagnostics 7/7 PASS
- CHANGES.md and completion report written
- MEMORY.md updated

Do NOT proceed to:
- Backend code refactoring
- Zaks-llm consolidation
- New feature development

The migration lifecycle is complete after this mission.

---
*End of Mission Prompt — POST-MERGE-STABILIZE-001*
