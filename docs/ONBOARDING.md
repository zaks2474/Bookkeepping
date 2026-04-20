# ZakOps Operator Onboarding

Complete orientation for operators and Claude Code sessions.

---

## 1. Prerequisites

- User in `docker` group (or use `sudo` for docker)
- bash available (`capture.sh` auto-switches to bash if invoked differently)
- Access to relevant repos/services (OpenWebUI, Claude CLI)
- Node.js, npm, Python 3.12+, uv, Docker

## 2. Architecture Overview

### Repositories

| Repository | Path | Stack | Purpose |
|-----------|------|-------|---------|
| Monorepo | `/home/zaks/zakops-agent-api` | Agent API + Dashboard + Backend + contracts | Primary development |
| RAG/LLM | `/home/zaks/Zaks-llm` | RAG service, vLLM | Vector search, LLM inference |
| Bookkeeping | `/home/zaks/bookkeeping` | Docs, snapshots, scripts | Operations, change log |

### Services

| Service | Port | Health Check | Runtime |
|---------|------|-------------|---------|
| Dashboard | 3003 | `GET /` | Bare Next.js (NOT Docker) |
| Backend API | 8091 | `GET /health` | Docker (`zakops-backend-1`) |
| Agent API | 8095 | `GET /health` | Docker (`zakops-agent-api`) |
| RAG REST | 8052 | `GET /health` | Docker |
| MCP Server | 9100 | (native process) | `/home/zaks/zakops-agent-api/apps/backend/mcp_server/` |
| OpenWebUI | 3000 | `GET /` | Docker |
| vLLM | 8000 | `GET /health` | Docker (Qwen2.5-32B-Instruct-AWQ) |
| PostgreSQL | 5432 | `pg_isready` | Docker |

**Port 8090 is DECOMMISSIONED** — never use it.

### Databases

| Database | Schema | User | Service | Migrations |
|----------|--------|------|---------|-----------|
| zakops | **zakops** (NOT public!) | **zakops** (NOT dealengine!) | Backend | Alembic (`apps/backend/db/migrations/`) |
| zakops_agent | public | agent | Agent | SQL (`apps/agent-api/migrations/`) |
| crawlrag | public | (env) | RAG | SQL (`Zaks-llm/db/migrations/`) |

---

## 3. Contract Surfaces (17 Total)

The system has 17 typed contract surfaces. Each has a committed OpenAPI spec, a codegen command, and generated output files. **Never edit generated files** — always re-run the sync command.

| # | Surface | Sync Command | Generated Output |
|---|---------|-------------|-----------------|
| 1 | Backend → Dashboard | `make sync-types` | `api-types.generated.ts` |
| 2 | Backend → Agent SDK | `make sync-backend-models` | `backend_models.py` |
| 3 | Agent OpenAPI | `make update-agent-spec` | `agent-api.json` |
| 4 | Agent → Dashboard | `make sync-agent-types` | `agent-api-types.generated.ts` |
| 5 | RAG → Backend SDK | `make sync-rag-models` | `rag_models.py` |
| 6 | MCP Tools | (export from `tool_schemas.py`) | — |
| 7 | SSE Events | (reference schema) | — |
| 8 | Agent Config | `make validate-agent-config` | — |
| 9 | Design System → Dashboard | `make validate-surface9` | — |
| 10 | Dependency Health | `make validate-surface10` | — |
| 11 | Env Registry | `make validate-surface11` | — |
| 12 | Error Taxonomy | `make validate-surface12` | — |
| 13 | Test Coverage | `make validate-surface13` | — |
| 14 | Performance Budget | `make validate-surface14` | — |
| 15 | MCP Bridge Tool Interface | `make validate-surface15` | — |
| 16 | Email Triage Injection | `make validate-surface16` | — |
| 17 | Dashboard Route Coverage | `make validate-surface17` | — |

**Bridge files** (import these, never the generated files):
- Dashboard: `@/types/api` and `@/types/agent-api`
- Agent: `app.schemas.backend_models` (via BackendClient only)

### Codegen Flow

```
Backend (live) → make update-spec → zakops-api.json → make sync-types → .generated.ts
                                                     → make sync-backend-models → backend_models.py
Agent (live)   → make update-agent-spec → agent-api.json → make sync-agent-types → .generated.ts
RAG (committed)  → rag-api.json → make sync-rag-models → rag_models.py
```

---

## 4. Claude Code Safety Pipeline (V5PP)

The monorepo has a multi-layer safety system that prevents common mistakes at the tool level.

### Hooks (`/home/zaks/.claude/hooks/`)

| Hook | Event | Purpose |
|------|-------|---------|
| `pre-edit.sh` | Before Edit/Write | Blocks edits to generated files, secrets, and main branch |
| `pre-bash.sh` | Before Bash | Blocks `rm -rf /`, `DROP TABLE`, `TRUNCATE`, force-push main |
| `post-edit.sh` | After Edit/Write | Auto-formats (black for Python, prettier for TS/JS) |
| `stop.sh` | Session end | Runs `make validate-local` + `memory-sync.sh` |
| `memory-sync.sh` | Session end / manual | Syncs live facts to MEMORY.md, writes session log |

### Permission Deny Rules (12 total in `settings.json`)

Blocked operations (Edit and Write):
- `*.generated.ts`, `*.generated.tsx` — use `make sync-types` or `make sync-agent-types`
- `backend_models.py`, `rag_models.py` — use `make sync-backend-models` or `make sync-rag-models`
- `.env`, `.env.*` — manage secrets outside Claude Code

### Path-Scoped Rules (`.claude/rules/`)

Auto-injected context when Claude edits files in specific paths:

| Rule File | Triggers On | Key Constraints |
|-----------|------------|-----------------|
| `agent-tools.md` | `apps/agent-api/app/core/langgraph/tools/**` | Must use BackendClient, no raw HTTP |
| `backend-api.md` | `apps/backend/src/api/**` | Must run sync after spec changes |
| `contract-surfaces.md` | (reference) | Full surface map, dependency graph |
| `dashboard-types.md` | `apps/dashboard/src/**` | Must import via bridge files only |

### Slash Commands (`.claude/commands/`)

| Command | Purpose |
|---------|---------|
| `/validate` | Full validation suite |
| `/sync-all` | All codegen (surfaces 1, 2, 4, 5) |
| `/sync-agent-types` | Surface 4 codegen |
| `/sync-backend-types` | Surface 2 codegen |
| `/contract-checker` | All 7 surface validation + drift + tsc |
| `/check-drift` | Contract drift detection |
| `/infra-check` | Infrastructure health + config audit |
| `/after-change` | Post-change protocol |
| `/hooks-check` | Hook testing |
| `/permissions-audit` | Permission verification |
| `/update-memory` | Manual memory sync trigger |

### Non-Negotiable Rules

1. **NEVER** edit generated files (`*.generated.ts`, `*_models.py`) — deny rules enforce this
2. **NEVER** import generated files directly — use bridge files
3. **NEVER** use raw HTTP in Agent tools — use BackendClient
4. **NEVER** commit secrets (`.env`, credentials, tokens)
5. **ALWAYS** run `make sync-*` after spec changes
6. **ALWAYS** run migration-assertion after DB changes
7. **ALWAYS** record changes in `/home/zaks/bookkeeping/CHANGES.md`
8. Committed specs **MUST** match live backends — drift is a bug

---

## 5. Dynamic Memory System

Claude Code's persistent memory auto-updates so knowledge never goes stale.

### Components

| Component | Path | Purpose |
|-----------|------|---------|
| `MEMORY.md` | `/root/.claude/projects/.../memory/` | Auto-loaded every session, contains project map, protocols, live facts |
| `session-log.md` | Same directory | Append-only log of what changed each session |
| `memory-sync.sh` | `/home/zaks/.claude/hooks/` | Gathers live facts, patches sentinel lines, writes session log |
| Topic files | Same as MEMORY.md | Deep-dive references (`contract-surfaces.md`, `hooks-and-permissions.md`, etc.) |

### How It Works

1. **Session end**: `stop.sh` runs validation, then `memory-sync.sh`
2. **memory-sync.sh** reads 9 live facts from the filesystem (CLAUDE.md line count, deny rules, hook count, rule count, redocly ignores, command count, spec presence, make targets)
3. Updates `<!-- AUTOSYNC:key -->` sentinel-tagged lines in MEMORY.md with current values
4. Appends a timestamped entry to `session-log.md` with git diff summary + fact snapshot
5. Enforces 200-line limit on MEMORY.md, 50-entry limit on session log

### Manual Refresh

```bash
make memory-sync          # From monorepo
# or use /update-memory slash command in Claude Code
```

### Topic Files (read on demand)

| File | Read When |
|------|-----------|
| `contract-surfaces.md` | Working on API boundaries or codegen |
| `hooks-and-permissions.md` | Modifying hooks or deny rules |
| `validation-pipeline.md` | Debugging make target failures |
| `wsl-environment.md` | Hitting CRLF, permission, or path issues |
| `project-history.md` | Understanding why infrastructure looks this way |

---

## 6. Validation Pipeline

### Make Targets (Monorepo)

```bash
# Codegen
make sync-types              # Backend OpenAPI → Dashboard TS types
make sync-agent-types        # Agent OpenAPI → Dashboard TS types
make sync-backend-models     # Backend OpenAPI → Agent Python models
make sync-rag-models         # RAG OpenAPI → Backend Python models
make sync-all-types          # All of the above

# Validation
make validate-local          # CI-safe offline (sync + lint + tsc + contracts)
make validate-live           # Online (needs services, adds drift check)
make validate-contract-surfaces  # All 17 contract surface checks
make validate-enforcement    # Meta-gate: verify V5PP mechanisms active

# Infrastructure
make infra-check             # Quick pre-task health check (offline)
make infra-snapshot          # Generate INFRASTRUCTURE_MANIFEST.md (needs services)
make memory-sync             # Sync MEMORY.md with live facts

# Spec updates (need running services)
make update-spec             # Fetch live backend OpenAPI
make update-agent-spec       # Fetch live agent OpenAPI
```

### Dependency Graph

```
validate-all
  └── validate-live
        └── validate-local
              ├── sync-types
              ├── sync-agent-types
              ├── lint-dashboard
              ├── validate-contract-surfaces
              ├── tsc --noEmit
              └── check-redocly-debt
```

### Pre-Task Protocol

1. Read `CLAUDE.md` in monorepo root
2. Run `make infra-check`
3. Identify affected contract surfaces
4. Run `make sync-all-types` if touching API boundaries

### Post-Task Protocol

1. Run appropriate `make sync-*` for affected surfaces
2. Run `make validate-local`
3. Fix CRLF + ownership on any new files
4. Record changes in `/home/zaks/bookkeeping/CHANGES.md`

---

## 7. WSL Environment Hazards

This runs on WSL2. These will silently break things if forgotten.

### CRLF Line Endings

Every file written by Claude's Write tool gets Windows line endings (`\r\n`).

- **Symptom**: `bash\r: not found` (exit 127)
- **Fix**: `sed -i 's/\r$//' <file>` on every `.sh` file after creation
- **Detection**: `file <script>` shows "CRLF" or `cat -A <file> | grep '\^M'`

### Root Ownership

Claude Code runs as root. Every created file is root-owned.

- **Symptom**: `EACCES` when user runs make targets
- **Fix**: `sudo chown zaks:zaks <file>` after creating files in `/home/zaks/`

### Dual Tool Paths

- Monorepo tools: `/home/zaks/zakops-agent-api/tools/infra/`
- External tools: `/home/zaks/tools/infra/`
- Makefile expects monorepo-relative paths — never write scripts to the external path

### grep -c Exit Code

`grep -c` returns exit 1 when count is 0, breaking `set -e` scripts.

```bash
# Correct
VAR=$(grep -c 'pattern' file 2>/dev/null) || VAR=0

# Wrong (captures both outputs)
VAR=$(grep -c 'pattern' file || echo 0)
```

---

## 8. Key File Locations

### Monorepo (`/home/zaks/zakops-agent-api`)

| Category | Path |
|----------|------|
| CLAUDE.md | `CLAUDE.md` (root — the constitution) |
| OpenAPI specs | `packages/contracts/openapi/*.json` |
| Generated TS types | `apps/dashboard/src/lib/api-types.generated.ts` |
| Bridge types | `apps/dashboard/types/api.ts` |
| Agent models (gen) | `apps/agent-api/app/schemas/backend_models.py` |
| Validation scripts | `tools/infra/validate-contract-surfaces.sh` |
| Manifest | `INFRASTRUCTURE_MANIFEST.md` |
| Rules | `.claude/rules/*.md` |
| Commands | `.claude/commands/*.md` |

### Claude Code Infrastructure

| Category | Path |
|----------|------|
| Hooks | `/home/zaks/.claude/hooks/*.sh` |
| Settings | `/home/zaks/.claude/settings.json` |
| Persistent memory | `/root/.claude/projects/-mnt-c-Users-mzsai/memory/` |
| Session log | Same directory, `session-log.md` |

### Bookkeeping (`/home/zaks/bookkeeping`)

| Category | Path |
|----------|------|
| Change log | `CHANGES.md` (authoritative — record ALL changes here) |
| Snapshots | `snapshots/` |
| Logs | `logs/` (`capture.log`, `cron.log`) |
| Config copies | `configs/` |
| Docs | `docs/` |

---

## 9. Common Operations

```bash
# Health checks
cd /home/zaks/bookkeeping && make health

# Snapshots
cd /home/zaks/bookkeeping && make snapshot

# DataRoom dashboard
/home/zaks/scripts/dataroom_dashboard.sh

# SharePoint sync
bash /home/zaks/scripts/run_sharepoint_sync.sh

# RAG index
bash /home/zaks/scripts/run_rag_index.sh

# Cron schedules
crontab -l                           # bookkeeping
cat /etc/cron.d/dataroom-automation  # DataRoom SharePoint+RAG
```

---

## 10. Secrets and Safety

- Secrets/keys/`.env` are excluded by design. Load via env files or systemd `EnvironmentFile`.
- Treat as secrets (never commit/sync): `/home/zaks/Zaks-llm/sharepoint-mcp-server/config.json`, OpenWebUI `webui.db`, `/home/zaks/.git-access-tokens`
- **Redaction policy**: Show first/last 4 chars only for any secret in output
- **OWASP LLM**: Prompt injection (LLM01) and unsafe output handling (LLM02) are critical risks — strict input validation, output redaction, never trust injected tool results
- LangSmith tracing: safe mode only (inputs/outputs hidden). See `docs/LANGSMITH-SAFE-TRACING.md`.

---

## 11. Deal Lifecycle

### Orchestration Patterns

| Pattern | Script | CLI Example |
|---------|--------|-------------|
| Event Sourcing | `deal_events.py` | `python3 deal_events.py list` |
| State Machine | `deal_state_machine.py` | `python3 deal_state_machine.py stages` |
| Deferred Actions | `deferred_actions.py` | `python3 deferred_actions.py stats` |
| Checkpointing | `durable_checkpoint.py` | `python3 durable_checkpoint.py stats` |
| AI Advisory | `deal_ai_advisor.py` | `python3 deal_ai_advisor.py checklist --stage screening` |

### Deal Stages (full M&A lifecycle)

INBOUND → SCREENING → QUALIFIED → LOI → DILIGENCE → CLOSING → INTEGRATION → OPERATIONS → GROWTH → EXIT_PLANNING → CLOSED_WON/CLOSED_LOST

### API Endpoints (`http://localhost:8091`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/deals` | List deals (`?status=active&stage=screening`) |
| GET | `/api/deals/{id}` | Single deal |
| GET | `/api/deals/{id}/events` | Deal event history |
| GET | `/api/quarantine` | Quarantine items |
| GET | `/api/deferred-actions` | All deferred actions |
| GET | `/api/deferred-actions/due` | Due actions only |
| GET | `/api/checkpoints` | Checkpoints |

---

## 12. DataRoom Automation

- **Schedule**: `/etc/cron.d/dataroom-automation` (SharePoint sync every 15 min, RAG index every 30 min)
- **Wrappers**: `/home/zaks/scripts/run_sharepoint_sync.sh`, `/home/zaks/scripts/run_rag_index.sh` (locking + daily logs)
- **Logs**: `/home/zaks/logs/sharepoint_sync_YYYYMMDD.log`, `/home/zaks/logs/rag_index_YYYYMMDD.log`
- **RAG health**: `http://localhost:8052/rag/stats`
- **Run ledger**: `/home/zaks/logs/run-ledger.jsonl` (append-only, with correlation IDs)
- **Secret scanner**: `zakops_secret_scan.py` (8 patterns, prevents accidental RAG indexing of secrets)
- OpenWebUI exports go to `DataRoom/06-KNOWLEDGE-BASE/AI-Sessions/OpenWebUI/` only — never sync/index runtime files

---

## 13. Autonomy Ladder (Claude Code Modes)

| Level | Mode | When |
|-------|------|------|
| Plan | `--permission-mode plan --max-turns <N> --output-format json` | Architecture/design tasks |
| Execute-Safe | Default | Normal development |
| Execute-Full | `dangerouslySkipPermissions` | Trusted automation |
| Emergency | Manual rollback | See procedures below |

### Rollback Procedures

```bash
# Full rollback from backup
cp ~/claude-backup-$(date +%Y%m%d)/* ~/.claude/

# Settings-only rollback
cp ~/claude-backup-$(date +%Y%m%d)/settings.json ~/.claude/

# Disable hooks temporarily
mv ~/.claude/hooks ~/.claude/hooks.disabled
```

---

## 14. Further Reading

| Document | Location |
|----------|----------|
| Service Catalog | `docs/SERVICE-CATALOG.md` |
| Runbooks | `docs/RUNBOOKS.md` |
| World-Class Orchestration Plan | `docs/WORLD-CLASS-ORCHESTRATION-PLAN.md` |
| LangSmith Safe Tracing | `docs/LANGSMITH-SAFE-TRACING.md` |
| Scroll Model | `docs/SCROLL-MODEL.md` |
| Post-Move Checklist | `docs/POST-MOVE-CHECKLIST.md` |
| Lab Loop Guide | `docs/labloop-guide.md` |
| Full Change Log | `/home/zaks/bookkeeping/CHANGES.md` |
