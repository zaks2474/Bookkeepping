# V6PP Setup Guide — ZakOps Claude Code Infrastructure
## Generated: 2026-02-09 | Version: 6.0

---

## What Changed Since V5PP-DMS

- **Surface 9 added** — Component Design System → Dashboard, with manifest, path-scoped rule, and validation script
- **TriPass pipeline hardened** — 5 QA enhancements: trap handler (ENH-3), T-3 SKIP on generate-only (ENH-1), T-6 idempotency (ENH-2), WSL file ownership (ENH-9), MEMORY.md gates line (ENH-8)
- **Phantom plugin references removed** — All references to the non-existent skill plugin path replaced with `.claude/rules/design-system.md`
- **Contract surfaces now 9** — Previously 8; Surface 9 governs frontend conventions and design quality
- **Path-scoped rules now 5** — Added `design-system.md` triggering on dashboard component paths
- **Deal Integrity patterns codified** — 7 mandatory architectural conventions documented in Surface 9 manifest
- **Config-Stabilize findings remediated** — 14 configuration issues resolved across hooks, memory, and settings

---

## Part 1: Repository & Environment Orientation

### Project Roots

| Repository | Path | Stack | Purpose |
|-----------|------|-------|---------|
| Monorepo | `/home/zaks/zakops-agent-api` | Next.js + LangGraph + contracts | Agent API, Dashboard, contracts, tools |
| Backend | `/home/zaks/zakops-backend` | FastAPI + Docker | Backend API, DB migrations, MCP server |
| RAG/LLM | `/home/zaks/Zaks-llm` | vLLM + RAG service | RAG REST, vLLM inference, vector DB |
| Bookkeeping | `/home/zaks/bookkeeping` | Docs + scripts | Change log, snapshots, QA, TriPass runs |

### Service Map

| Service | Port | Container | Health Check | Notes |
|---------|------|-----------|-------------|-------|
| Dashboard | 3003 | bare process (NOT Docker) | `GET /` | Next.js dev server; Docker conflicts on network_mode: host |
| Backend API | 8091 | `zakops-backend-1` | `GET /health` | FastAPI; postgres container enters restart loops — use `--no-deps` |
| Agent API | 8095 | `agent-api` | `GET /health` | LangGraph + Qwen 2.5 via vLLM |
| PostgreSQL | 5432 | `zakops-backend-postgres-1` | `pg_isready` | **Port 5432 ONLY** — port 5435 does not exist |
| RAG REST | 8052 | `rag-service` | `GET /health` | Needs restart if pool=null at boot |
| MCP Server | 9100 | native process | — | `/home/zaks/zakops-backend/mcp_server/` |
| OpenWebUI | 3000 | `open-webui` | `GET /` | Chat UI |
| vLLM | 8000 | `vllm` | — | Qwen2.5-32B-Instruct-AWQ, GPU |
| **Port 8090** | — | — | — | **DECOMMISSIONED — never use** |

### Databases

| Database | Schema | User | Service | Migrations |
|----------|--------|------|---------|-----------|
| zakops | zakops (NOT public) | zakops (NOT dealengine) | Backend | Alembic (`zakops-backend/db/migrations/`) |
| zakops_agent | public | agent | Agent API | SQL (`apps/agent-api/migrations/`) |
| crawlrag | public | (env) | RAG | SQL (`Zaks-llm/db/migrations/`) |

### Key Monorepo Directory Tree

```
zakops-agent-api/
├── apps/
│   ├── dashboard/src/          # Next.js dashboard
│   │   ├── app/                # Pages (App Router)
│   │   ├── components/         # React components
│   │   ├── lib/                # API client, generated types
│   │   ├── types/              # Bridge files, contracts, manifests
│   │   └── styles/             # CSS
│   └── agent-api/              # LangGraph agent
│       ├── app/core/langgraph/ # Nodes, edges, tools
│       └── app/schemas/        # Generated Python models
├── packages/contracts/         # OpenAPI specs, schemas
│   ├── openapi/                # zakops-api.json, agent-api.json, rag-api.json
│   ├── mcp/                    # tool-schemas.json
│   └── sse/                    # agent-events.schema.json
├── tools/
│   ├── infra/                  # Validation scripts
│   └── tripass/                # TriPass orchestrator
├── .claude/
│   ├── rules/                  # Path-scoped rules (5 files)
│   └── commands/               # Slash commands (13 files)
└── Makefile                    # ~112 targets
```

---

## Part 2: Claude Brain Architecture

### Configuration Loading Order

1. **User-level settings** — `~/.claude/settings.json` (permissions, hooks, MCP servers)
2. **Project-level settings** — `.claude/settings.json` (if exists; not used in ZakOps)
3. **Agent definitions** — `~/.claude/agents/*.md` (3 agents)
4. **Path-scoped rules** — `.claude/rules/*.md` (5 rules, injected when file paths match)
5. **CLAUDE.md files** — Root-level `/home/zaks/CLAUDE.md` (64 lines) → Monorepo `/home/zaks/zakops-agent-api/CLAUDE.md` (143 lines, ceiling: 150)
6. **Persistent memory** — Two copies: `/root/.claude/projects/-home-zaks/memory/MEMORY.md` and `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md` (loaded based on cwd)

### The CLAUDE.md Split

| File | Lines | Purpose |
|------|-------|---------|
| `/home/zaks/CLAUDE.md` | 64 | Operational reference: service map, key paths, golden commands, secrets policy |
| `/home/zaks/zakops-agent-api/CLAUDE.md` | 143 | Full system guide: contract surfaces, pre/post-task protocol, agent delegation, safety rules, rollback procedures. **Ceiling: 150 lines** — Surface 9 detail goes in the rule file, not here |

### Path-Scoped Rules (`.claude/rules/`)

| File | Trigger Paths | Key Constraints |
|------|--------------|----------------|
| `agent-tools.md` | `apps/agent-api/app/core/langgraph/tools/**` | 3-file update rule (deal_tools.py + system.md + tool-schemas.json) |
| `backend-api.md` | `zakops-backend/**` | Schema conventions, migration rules, OWASP |
| `contract-surfaces.md` | `packages/contracts/**`, `*generated*`, `*_models.py` | All 9 surfaces, sync commands, dependency graph |
| `dashboard-types.md` | `apps/dashboard/src/types/**`, `apps/dashboard/src/lib/**` | Import discipline, bridge file rules |
| `design-system.md` | `apps/dashboard/src/components/**`, `apps/dashboard/src/app/**`, `apps/dashboard/src/styles/**` | Surface 9: architectural conventions (Category A) + design quality standards (Category B) |

### Slash Commands (`.claude/commands/`)

| Command | Purpose |
|---------|---------|
| `/after-change` | Post-change alignment (sync-types + lint + tsc) |
| `/check-drift` | Verify committed specs match live backends |
| `/contract-checker` | Validate all contract surfaces |
| `/hooks-check` | Verify hook configuration |
| `/infra-check` | Infrastructure health check |
| `/permissions-audit` | Show effective permissions |
| `/scaffold-feature` | Generate vertical slice for new feature |
| `/sync-agent-types` | Regenerate Agent → Dashboard types |
| `/sync-all` | Run all codegen pipelines |
| `/sync-backend-types` | Regenerate Backend → Dashboard types |
| `/tripass` | Run TriPass multi-agent pipeline |
| `/update-memory` | Refresh MEMORY.md from live filesystem |
| `/validate` | Run all validation checks |

**Total: 13 commands**

### Hooks (`~/.claude/hooks/`)

| Script | Event | Timeout | Behavior |
|--------|-------|---------|----------|
| `pre-edit.sh` | PreToolUse (Edit, Write) | 10s | Blocks edits to: secrets (.env, .pem, .key), generated files (*.generated.ts, *_models.py), files on main/master. Exit 2 = block |
| `pre-bash.sh` | PreToolUse (Bash) | 10s | Blocks: `rm -rf /`, `DROP TABLE`, `TRUNCATE`, force-push main. Exit 2 = block |
| `post-edit.sh` | PostToolUse (Edit, Write) | 30s | Auto-format: Python (black), TS/JS (prettier), JSON validation. Async, best-effort |
| `stop.sh` | Stop | 60s | Fast-tier validation (Gates A, B, E) + TriPass lock check + memory-sync. Exit 2 = block session end |
| `memory-sync.sh` | Called by stop.sh | — | Syncs MEMORY.md sentinel tags with live filesystem facts. Non-fatal |

**Total: 5 hooks**

#### Hook Behavior Details

**pre-edit.sh** enforces three categories of protection:
1. **Secrets protection** — Blocks any Edit/Write to files matching `.env`, `.env.*`, `.pem`, `.key`, `*_token*`
2. **Generated file protection** — Blocks edits to `*generated.ts` and `*_models.py` (must use codegen instead)
3. **Branch protection** — Blocks edits when on main/master branch (prevents accidental direct commits)

**pre-bash.sh** blocks destructive patterns:
1. `rm -rf /` or `rm -rf /*` — Prevents root filesystem deletion
2. `DROP TABLE`, `TRUNCATE`, `DROP DATABASE` — Prevents destructive database operations
3. `git push --force` or `git push -f` to main/master — Prevents force-push to protected branches

**post-edit.sh** auto-formats asynchronously after writes:
1. Python files — Runs `black` formatter
2. TypeScript/JavaScript files — Runs `prettier`
3. JSON files — Validates syntax
4. All formatting is best-effort; failures are silenced

**stop.sh** performs end-of-session validation:
1. Runs fast-tier validation (TypeScript compile + Redocly debt check)
2. Runs contract surface validation
3. Checks for raw httpx client usage in deal_tools.py (must use BackendClient)
4. Checks for active TriPass lock files (warns if orphaned)
5. Invokes memory-sync.sh to update MEMORY.md sentinel tags

**memory-sync.sh** gathers live facts and updates MEMORY.md:
1. Reads CLAUDE.md line counts
2. Counts deny rules from settings.json
3. Counts hooks, rules, and commands
4. Checks Redocly ignore ceiling
5. Gathers TriPass run count and latest run ID
6. Checks OpenAPI spec presence
7. Updates all `<!-- AUTOSYNC:key -->` sentinel lines in MEMORY.md
8. Appends timestamped entry to session-log.md (capped at 50 entries)

### Settings (`~/.claude/settings.json`)

**Deny Rules (12):**
- Edit/Write to `*api-types.generated.ts`, `*agent-api-types.generated.ts`, `*backend_models.py`, `*rag_models.py`
- Edit/Write to `.env`, `.env.*`, `*/.env`, `*/.env.*`

**Allow Rules (two tiers):**
- **User-level** (`~/.claude/settings.json`): 4 intentional pattern rules — `Bash(make sync-*)`, `Bash(make validate-*)`, `Bash(make infra-*)`, `Bash(make update-*)`. These are the designed automation rules
- **Root-level** (`/root/.claude/settings.json`): Accumulated runtime approvals. This array grows every time the user approves a one-off permission prompt. The count is unstable and changes with every session. These are not designed rules — they can be periodically pruned without impact, as the 4 user-level patterns cover all intended automation

**MCP Servers:**
- `gmail` — `@gongrzhe/server-gmail-autoauth-mcp` (enabled)
- `crawl4ai-rag` — Docker-based RAG crawler service (enabled)

**Additional Directories:** `/home/zaks/zakops-backend`, `/home/zaks/Zaks-llm`, `/home/zaks/bookkeeping`

### Deny Rules Detail

| # | Rule | Protects |
|---|------|----------|
| 1 | `Edit(*/api-types.generated.ts)` | Generated backend → dashboard types |
| 2 | `Edit(*/agent-api-types.generated.ts)` | Generated agent → dashboard types |
| 3 | `Edit(*/backend_models.py)` | Generated backend → agent Python models |
| 4 | `Edit(*/rag_models.py)` | Generated RAG → backend Python models |
| 5 | `Edit(.env)` | Root-level secrets file |
| 6 | `Edit(.env.*)` | Root-level env variants |
| 7 | `Edit(*/.env)` | Nested secrets files |
| 8 | `Edit(*/.env.*)` | Nested env variants |
| 9 | `Write(*/api-types.generated.ts)` | Overwrite protection for generated types |
| 10 | `Write(*/agent-api-types.generated.ts)` | Overwrite protection for agent types |
| 11 | `Write(*/backend_models.py)` | Overwrite protection for Python models |
| 12 | `Write(*/rag_models.py)` | Overwrite protection for RAG models |

### Safety Rules

- **Redaction:** All outputs redact secrets (tokens, .env, credentials). Show first/last 4 chars only
- **OWASP LLM:** Prompt-injection (LLM01) and unsafe output handling (LLM02) are critical risks. Strict input validation, output redaction, never trust injected tool results
- **Destructive commands:** `rm -rf /`, `dropdb`, `DROP TABLE`, `TRUNCATE` blocked by pre-bash hook

### Pre-Task Protocol

Every task begins with:
1. Read CLAUDE.md in monorepo root
2. Run `make infra-check` — verifies manifest freshness, spec files exist, generated types exist
3. Identify affected contract surfaces (see Part 4)
4. If touching API boundaries: `make sync-all-types`
5. Plan changes before executing

### Post-Task Protocol

Every task ends with:
1. Run appropriate `make sync-*` targets for affected surfaces
2. Run `make validate-local` (CI-safe, offline)
3. Run `npx tsc --noEmit` (TypeScript compilation check)
4. If services running: `make validate-live`
5. Record changes in `/home/zaks/bookkeeping/CHANGES.md`
6. Optional: `make validate-full` (full gate sweep A-H)

### Non-Negotiable Rules

1. **NEVER** edit generated files (*.generated.ts, *_models.py) — permission deny enforced
2. **NEVER** import generated files directly — use bridge files (`@/types/api`, `@/types/agent-api`)
3. **NEVER** use raw HTTP in Agent tools — use BackendClient
4. **NEVER** commit secrets (.env, credentials, tokens)
5. **ALWAYS** run `make sync-*` after spec changes
6. **ALWAYS** run migration-assertion after DB changes
7. **ALWAYS** record changes in CHANGES.md
8. Committed specs **MUST** match live backends — drift is a bug

### Autonomy Ladder

| Level | Mode | When |
|-------|------|------|
| Plan | `--permission-mode plan` | Architecture/design tasks |
| Execute-Safe | Default | Normal development |
| Execute-Full | `dangerouslySkipPermissions` | Trusted automation |
| Emergency | Manual rollback | See Part 8: Rollback Procedures |

---

## Part 3: Agent Topology

### The 4-Agent Architecture

| Agent | Model | Purpose | Permissions |
|-------|-------|---------|------------|
| **main-builder** | Opus 4.6 | Primary development agent; orchestrates all work | Full Read/Write/Bash (subject to hooks) |
| **Architecture Reviewer** | Opus | Analyzes proposed changes for risks, edge cases, cross-surface impact | Read-only (Grep, Glob, Read) |
| **Contract Guardian** | Sonnet | Validates all contract surfaces, runs gates, reports drift | Read-only + validation commands |
| **Test Engineer** | Sonnet | Writes tests, validates golden payloads | Write to test directories only |

### Agent Definition Files

Located at `~/.claude/agents/`. Each file has YAML frontmatter specifying name, description, model, and tool permissions.

### Delegation Protocol

- **After any code change:** Contract Guardian runs automatically via stop hook (Fast Tier)
- **Before high-impact changes** (Pydantic models, middleware, DB migrations, LangGraph nodes/edges/state, error response schemas, or >=2 surfaces): Run Architecture Reviewer
- **After new feature/endpoint:** Run Test Engineer to generate tests
- **For CLI tools:** Use `gemini`/`codex` directly (optional, no delegation)

### External Models

| CLI | Path | Use Case |
|-----|------|----------|
| Gemini CLI | `/root/.npm-global/bin/gemini` | TriPass Pass 1/2 agent, general investigation |
| Codex CLI | `/root/.npm-global/bin/codex` | TriPass Pass 1/2 agent, code analysis |
| Claude CLI | System PATH | TriPass orchestrator, primary development |

### Agents vs Skills vs Commands

- **Agents** — Custom definitions in `~/.claude/agents/` with YAML frontmatter, model selection, and tool permissions. Invoked via `/agent-name` or Task tool with `subagent_type`
- **Skills** — Built-in capabilities (e.g., `/commit`, `/review-pr`). No plugin system in Claude Code
- **Commands** — Project-scoped prompt templates in `.claude/commands/`. Invoked via `/<command-name>`

There is **no `frontend-design` plugin** available to Claude Code. Frontend design standards are embedded in `.claude/rules/design-system.md` as part of Surface 9.

---

## Part 4: The 9 Contract Surfaces

### The Hybrid Guardrail Pattern

```
Source System → OpenAPI Spec → Codegen → Generated File → Bridge File → Consumer
                (committed)      (make)    (DO NOT EDIT)    (hand-written)
```

### Surface 1: Backend → Dashboard (TypeScript)

| Attribute | Value |
|-----------|-------|
| Spec | `packages/contracts/openapi/zakops-api.json` (183KB) |
| Command | `make sync-types` |
| Generated | `apps/dashboard/src/lib/api-types.generated.ts` (5,786 lines) |
| Bridge | `apps/dashboard/src/types/api.ts` (376 lines) |
| Rule | Import from `@/types/api`, NEVER from `api-types.generated.ts` |

### Surface 2: Backend → Agent SDK (Python)

| Attribute | Value |
|-----------|-------|
| Spec | `packages/contracts/openapi/zakops-api.json` |
| Command | `make sync-backend-models` |
| Generated | `apps/agent-api/app/schemas/backend_models.py` (609 lines) |
| Consumer | `apps/agent-api/app/services/backend_client.py` |

### Surface 3: Agent API OpenAPI Spec

| Attribute | Value |
|-----------|-------|
| Spec | `packages/contracts/openapi/agent-api.json` (72KB) |
| Command | `make update-agent-spec` (requires running Agent API) |

### Surface 4: Agent → Dashboard (TypeScript)

| Attribute | Value |
|-----------|-------|
| Spec | `packages/contracts/openapi/agent-api.json` |
| Command | `make sync-agent-types` |
| Generated | `apps/dashboard/src/lib/agent-api-types.generated.ts` (2,229 lines) |
| Bridge | `apps/dashboard/src/types/agent-api.ts` (91 lines) |

### Surface 5: RAG → Backend SDK (Python)

| Attribute | Value |
|-----------|-------|
| Spec | `packages/contracts/openapi/rag-api.json` (6.9KB) |
| Command | `make sync-rag-models` |
| Generated | `zakops-backend/src/schemas/rag_models.py` (32 lines) |

### Surface 6: MCP Tool Schemas

| Attribute | Value |
|-----------|-------|
| Spec | `packages/contracts/mcp/tool-schemas.json` (8.4KB) |
| Source | `zakops-backend/mcp_server/tool_schemas.py` |

### Surface 7: SSE Event Schema

| Attribute | Value |
|-----------|-------|
| Spec | `packages/contracts/openapi/agent-events.schema.json` (3.9KB) |
| Events | agent_thinking, tool_call, tool_result, agent_response, agent_error |

### Surface 8: Agent Configuration

| Attribute | Value |
|-----------|-------|
| Boundary | `deal_tools.py` ↔ `system.md` ↔ `tool-schemas.json` |
| Validation | `make validate-agent-config` (Gate C) |
| Rule | When adding/modifying an agent tool, update ALL THREE files. Checklist in `.claude/rules/agent-tools.md` |

### Surface 9: Component Design System → Dashboard

| Attribute | Value |
|-----------|-------|
| Boundary | Design system conventions ↔ Dashboard implementation |
| Manifest | `apps/dashboard/src/types/design-system-manifest.ts` (102 lines) |
| Rule | `.claude/rules/design-system.md` (auto-loaded for dashboard component/app/styles paths) |
| Validation | `bash tools/infra/validate-surface9.sh` |
| Governs | CSS architecture, data-fetching patterns, error handling, import discipline, stage definitions, design quality standards |
| Scope | Dashboard frontend only — does NOT govern Surfaces 1–8 |

**Category A — ZakOps Architectural Conventions (7 rules):**
1. Data fetching: `Promise.allSettled` mandatory, `Promise.all` banned for page-level fetching
2. Error handling: `console.warn` for degradation, `console.error` for unexpected only
3. CSS architecture: `@layer base` globals, `caret-color: transparent` with input override
4. Data aggregation: Server-side counts only, no client-side `.length`
5. Stage definitions: `PIPELINE_STAGES` from `execution-contracts.ts` only
6. API communication: Middleware proxy for `/api/*`, JSON 502 on failure
7. Import discipline: Bridge files only, never direct generated imports

**Category B — Frontend Design Quality Standards:**
- Design thinking: intentional aesthetic direction, not generic defaults
- Typography: distinctive fonts appropriate to context, avoid Inter/Roboto/Arial without justification
- Color: cohesive palettes via CSS variables, avoid purple-gradient-on-white cliche
- Motion: purposeful animations, CSS-only where possible, orchestrated page loads
- Spatial composition: intentional layouts, consider asymmetry and grid-breaking
- Backgrounds: atmosphere over flat colors, depth through shadow and layering
- Anti-patterns: cookie-cutter layouts, decoration without purpose, convergence

### Codegen Flow

```
Backend → zakops-api.json → api-types.generated.ts → api.ts (bridge)
                           → backend_models.py → backend_client.py → deal_tools.py

Agent API → agent-api.json → agent-api-types.generated.ts → agent-api.ts (bridge)

RAG API → rag-api.json → rag_models.py → rag_client.py

Design System → design-system-manifest.ts ← design-system.md (rule) ← validate-surface9.sh
```

### Quick Sync Commands

| Changed | Run |
|---------|-----|
| Backend API | `make update-spec && make sync-types && make sync-backend-models` |
| Agent API | `make update-agent-spec && make sync-agent-types` |
| RAG API | `make sync-rag-models` |
| Any/unsure | `make sync-all-types` |

### Validation Pipeline

The validation system has 4 tiers, each building on the previous:

**Tier 1: Fast (`make validate-fast`)** — Used by stop hook
- TypeScript compilation (`npx tsc --noEmit`)
- Redocly ignore ceiling check (max 57 ignores)

**Tier 2: Local (`make validate-local`)** — CI-safe, offline
- All type syncs (sync-types, sync-agent-types)
- Dashboard lint
- Contract surface validation (Surfaces 1-8)
- Agent config validation (Surface 8)
- SSE schema validation (Surface 7)
- TypeScript compilation
- Redocly debt check

**Tier 3: Full (`make validate-full`)** — All gates A-H
- Everything in validate-fast
- Contract surface validation
- Agent config validation
- SSE schema validation
- Database migration validation (all 3 databases)
- Raw httpx client check in deal_tools.py
- External CLI availability check (Gemini, Codex)

**Tier 4: Live (`make validate-live`)** — Requires running services
- Everything in validate-local
- Contract drift check (live backend vs committed spec)
- Migration assertion (DB state vs migration history)

**Gate Reference:**

| Gate | Command | What It Validates |
|------|---------|------------------|
| A | `npx tsc --noEmit` | TypeScript compilation |
| B | `validate-contract-surfaces.sh` | All contract surfaces |
| C | `validate-agent-config` | Agent tool/prompt/schema alignment |
| D | `validate-sse-schema` | SSE event schema |
| E | Raw httpx check | BackendClient usage enforcement |
| F | `validate-migrations` | Database migration integrity |
| G | `check-contract-drift` | Live spec matches committed spec |
| H | `check-redocly-debt` | Lint ignore ceiling |

**Surface 9 Gate:**
- `bash tools/infra/validate-surface9.sh` — Import discipline, stage definitions, Promise.allSettled usage, manifest/rule existence

---

## Part 5: Dynamic Memory System

### Architecture

```
MEMORY.md (persistent, auto-loaded) ← memory-sync.sh (sentinel tag updater)
    ↕                                    ↕
session-log.md (timestamped entries)   topic files (on-demand reference)
    ↕
/update-memory command (manual trigger)
```

### Authoritative MEMORY.md Path

Two MEMORY.md copies exist, loaded depending on the working directory at session start:
- `/root/.claude/projects/-home-zaks/memory/MEMORY.md` — loaded when cwd is `/home/zaks/`
- `/root/.claude/projects/-mnt-c-Users-mzsai/memory/MEMORY.md` — loaded when cwd is `/mnt/c/Users/mzsai/`

Both copies must be kept in sync. The `memory-sync.sh` hook updates the active copy at session end. When editing MEMORY.md manually, update BOTH copies to prevent drift.

### Sentinel Tag Format

Pattern: `<!-- AUTOSYNC:key --> value text`

The entire line after the sentinel is replaced by `memory-sync.sh` at session end.

| Key | What It Tracks |
|-----|---------------|
| `deny_rules` | Count of deny rules in settings.json |
| `hook_count` | Count of hook scripts in ~/.claude/hooks/ |
| `rule_count` | Count of path-scoped rules in .claude/rules/ |
| `claude_md_lines` | Line count of monorepo CLAUDE.md |
| `redocly_ignores` | Count of Redocly lint ignores (ceiling: 57) |

### Facts Gathered by memory-sync.sh

- CLAUDE.md line counts (both files)
- Deny rule count from settings.json
- Hook count from `~/.claude/hooks/`
- Rule count from `.claude/rules/`
- Redocly ignore count
- TriPass run count and latest run ID
- Backend/Agent OpenAPI spec presence
- Git status (changed files, staged files count)

### Session Log

`session-log.md` receives timestamped entries at session end. Trimmed to 50 most recent entries to prevent unbounded growth.

### Mission Recording Format

```markdown
- MISSION-ID: STATUS (YYYY-MM-DD) — brief description
```

### Completed Missions Registry

| Mission | Status | Date | Summary |
|---------|--------|------|---------|
| RT-HARDEN-001 V2 | 19/19 PASS | 2026-02-06 | Runtime hardening |
| HYBRID-GUARDRAIL-EXEC-001 | Complete | 2026-02-06 | Hybrid guardrail framework |
| QA-HG-VERIFY-001-V2 | FULL PASS | 2026-02-06 | Guardrail QA verification |
| DEAL-INTEGRITY-UNIFIED-001 | Complete | 2026-02-09 | 6 layers, 13 resolved issues |
| CONFIG-STABILIZE-001 | Complete | 2026-02-09 | 14 findings remediated |
| TRIPASS-INTEGRATE-002 | Complete | 2026-02-09 | Multi-agent pipeline, 9 AC PASS |
| QA-TP-VERIFY-001 | FULL PASS | 2026-02-09 | 75/75 gates |
| QA-TP-V2-001 | FULL PASS | 2026-02-09 | 67/67 gates, 142 combined points |
| V6-GUIDE-REGEN-001 | Complete | 2026-02-09 | Surface 9, TriPass QA, V6PP guide |

---

## Part 6: Deal Integrity Architecture Patterns

Permanent system constraints established by DEAL-INTEGRITY-UNIFIED-001. These are **mandatory** — all future dashboard work must comply.

### State Machine

`transition_deal_state()` is the **single choke point** for all deal state changes. No direct state mutations anywhere in the codebase. Valid transitions defined in `DEAL_TRANSITIONS` in `execution-contracts.ts`.

### Data Fetching

`Promise.allSettled` with typed empty fallbacks is **mandatory** for multi-fetch operations. `Promise.all` is **banned** in dashboard page-level data fetching.

```typescript
const [dealsResult, countsResult] = await Promise.allSettled([fetchDeals(), fetchCounts()]);
const deals = dealsResult.status === 'fulfilled' ? dealsResult.value : [];
```

### Middleware Proxy

Next.js middleware proxies all `/api/*` requests. Backend errors return **JSON 502**, never HTML 500.

### Stage Definitions

`PIPELINE_STAGES` in `execution-contracts.ts` is the **single source of truth** for stage definitions. No hardcoded stage arrays anywhere.

### Data Aggregation

Server-side deal counts only. No client-side `.length` calculations for display counts.

### CSS

`caret-color: transparent` at `@layer base` level with input/textarea override to `auto`.

### Error Handling

`console.warn` for expected degradation paths (backend unavailable, partial data). `console.error` reserved for unexpected failures only. React error boundaries wrap major page sections.

### ADRs

| ADR | Title | Location |
|-----|-------|----------|
| ADR-001 | Lifecycle FSM | Layer 6 deliverables |
| ADR-002 | Canonical Database | Layer 6 deliverables |
| ADR-003 | Stage Configuration Authority | Layer 6 deliverables |

---

## Part 7: TriPass Pipeline

### Purpose

TriPass is a multi-agent investigation pipeline that runs Claude Code, Gemini CLI, and Codex CLI as independent investigators, then consolidates their findings with structured cross-review and append-only evidence discipline.

### Pipeline Architecture

**4 passes:**

| Pass | Name | Description |
|------|------|-------------|
| 1 | Independent Investigation | 3 agents investigate the mission independently in parallel |
| 2 | Cross-Review & Deduplication | All Pass 1 reports shared; each agent reviews the others' findings |
| 3 | Consolidation | Single agent produces FINAL_MASTER.md from all inputs |
| 4 | Meta-QA (optional) | Verification of the consolidated output; skippable via `--skip-pass4` |

**3 modes:** `forensic` (root cause analysis), `design` (architecture/UI proposals), `implement` (code change plans)

**2 execution modes:** `autonomous` (agents execute via CLI) and `generate-only` (prompts saved as PROMPT.md, no execution)

### File System Contract

```
_tripass_runs/TP-YYYYMMDD-HHMMSS/
├── 00_context/          # Mission copy, CLI discovery report
├── 01_pass1/            # 3 independent investigation reports
├── 02_pass2/            # 3 cross-review reports
├── 03_pass3/            # Consolidated FINAL_MASTER.md
├── 04_metaqa/           # Meta-QA verification (optional)
├── EVIDENCE/            # gates.md, append_only_log.txt
├── WORKSPACE.md         # Append-only workspace
├── MASTER_LOG.md        # Append-only pipeline log
└── FINAL_MASTER.md      # Consolidated deliverable
```

### Lock File Management

The orchestrator creates `/tmp/tripass.lock` to prevent concurrent runs. **Trap handler** (ENH-3) ensures the lock is cleaned up on any exit — normal, error, signal, or interrupt:

```bash
trap 'release_lock' EXIT ERR INT TERM
```

### Gates T-1 through T-6

| Gate | Name | Checks |
|------|------|--------|
| T-1 | Append-Only Integrity | WORKSPACE.md + MASTER_LOG.md size/hash consistency via append_only_log.txt |
| T-2 | Output Completeness | 3 reports in 01_pass1, 3 reviews in 02_pass2, FINAL_MASTER.md non-empty |
| T-3 | Structural Validity | Agent identity headers, required fields in FINAL_MASTER.md. **Returns SKIP on generate-only stub** (ENH-1) |
| T-4 | Drift Detection | Counts drift/out-of-scope references vs findings. Fails if drift > 30% |
| T-5 | No-Drop Verification | Checks METAQA.md for overall PASS verdict. SKIP if Pass 4 not run |
| T-6 | Memory Sync | Updates TRIPASS_LATEST_RUN.md pointer and CHANGES.md. **Idempotent** — skips if run ID already recorded (ENH-2) |

### File Ownership (WSL)

At pipeline completion, all created files under `/home/zaks/` are re-owned to `zaks:zaks` (ENH-9). This prevents permission errors when the operator runs make targets from the terminal.

### Make Targets

| Target | Usage |
|--------|-------|
| `make tripass-init` | Initialize templates + CLI discovery |
| `make tripass-run MISSION=<file> MODE=forensic` | Execute a pipeline run |
| `make tripass-status RUN_ID=<id>` | Show run status |
| `make tripass-gates RUN_ID=<id>` | Re-run gates for a completed run |

### Integration Points

- **Memory:** MEMORY.md records TriPass capability, gate names, run path, SOP reference
- **Hooks:** `stop.sh` checks for active TriPass lock files; `memory-sync.sh` gathers run count and latest run ID
- **Bookkeeping:** All runs under `/home/zaks/bookkeeping/docs/_tripass_runs/`, entries in CHANGES.md

### Design-Mode Runs

Frontend design standards come from `.claude/rules/design-system.md` (Surface 9), not from any external plugin. The rule is automatically loaded when Claude Code works on dashboard component files. If the rule file is missing, the orchestrator logs a warning.

### Template System

Templates are parameterized Markdown files rendered with `render_template()`. Located at `/home/zaks/bookkeeping/docs/_tripass_templates/`:

| Template | Lines | Used In | Key Parameters |
|----------|-------|---------|---------------|
| `pass1.md` | 80 | Pass 1 (investigation) | MISSION_DESCRIPTION, RUN_ID, MODE, AGENT_NAME, REPO_ROOTS, CONSTRAINTS |
| `pass2.md` | 102 | Pass 2 (cross-review) | MISSION_DESCRIPTION, RUN_ID, MODE, AGENT_NAME, OUTPUT_FILE |
| `pass3.md` | 100 | Pass 3 (consolidation) | MISSION_DESCRIPTION, RUN_ID, MODE, OUTPUT_FILE |
| `pass4_metaqa.md` | 102 | Pass 4 (meta-QA) | MISSION_DESCRIPTION, RUN_ID, MODE, OUTPUT_FILE |

Pass 1 templates enforce the 5-field structure per finding:
1. **Root Cause** — Why the issue exists
2. **Fix Approach** — How to resolve it
3. **Industry Standard** — What best practices say
4. **System Fit** — How the fix integrates with ZakOps
5. **Enforcement** — How to prevent recurrence

### CLI Agent Invocation

Each agent is invoked via `timeout` with configurable limits:

```bash
GEMINI_TIMEOUT=900   # 15 minutes
CODEX_TIMEOUT=900    # 15 minutes
CLAUDE_TIMEOUT=900   # 15 minutes
```

Output is captured by shell redirect — agents have no direct filesystem write access.

### Append-Only Evidence

Every write to WORKSPACE.md and MASTER_LOG.md is recorded in `EVIDENCE/append_only_log.txt` with SHA256 hash, file size, and timestamp. Gate T-1 verifies no size decrease or hash inconsistency.

### Reference

Full operational procedures: `/home/zaks/bookkeeping/docs/TRIPASS_SOP.md` (206 lines)

### Essential Make Targets

The Makefile contains ~112 targets. Below are the most commonly used:

**Sync Commands:**

| Target | Purpose |
|--------|---------|
| `make sync-types` | Backend OpenAPI → Dashboard TypeScript types |
| `make sync-agent-types` | Agent OpenAPI → Dashboard TypeScript types |
| `make sync-backend-models` | Backend OpenAPI → Agent Python models |
| `make sync-rag-models` | RAG OpenAPI → Backend Python models |
| `make sync-all-types` | Run all 4 sync commands |

**Validation Commands:**

| Target | Purpose | Requires Services? |
|--------|---------|-------------------|
| `make validate-fast` | TypeScript + Redocly (stop hook tier) | No |
| `make validate-local` | Full offline validation (CI-safe) | No |
| `make validate-full` | All gates A-H | No |
| `make validate-live` | Online validation (drift check + migrations) | Yes |

**Infrastructure Commands:**

| Target | Purpose |
|--------|---------|
| `make infra-check` | Quick pre-task health check |
| `make infra-snapshot` | Generate INFRASTRUCTURE_MANIFEST.md |
| `make memory-sync` | Force MEMORY.md refresh |
| `make doctor` | Health check for all development tools |

**Spec Management:**

| Target | Purpose |
|--------|---------|
| `make update-spec` | Fetch live backend OpenAPI spec |
| `make update-agent-spec` | Fetch live agent OpenAPI spec |
| `make check-contract-drift` | Verify committed spec matches live |

**Development:**

| Target | Purpose |
|--------|---------|
| `make dev` | Start all services |
| `make dev-dashboard` | Start dashboard dev server |
| `make dev-agent-api` | Start agent API dev server |
| `make test` | Run all tests |

---

## Part 8: Rollback Procedures

### Full Configuration Rollback

```bash
cp ~/claude-backup-$(date +%Y%m%d)/* ~/.claude/
```

### Settings-Only Rollback

```bash
cp ~/claude-backup-$(date +%Y%m%d)/settings.json ~/.claude/
```

### Hook Disable/Re-Enable

```bash
# Disable all hooks
mv ~/.claude/hooks ~/.claude/hooks.disabled

# Re-enable
mv ~/.claude/hooks.disabled ~/.claude/hooks
```

### Emergency: Disable All Claude Code Config

```bash
# Disable hooks
mv ~/.claude/hooks ~/.claude/hooks.disabled

# Disable rules
mv /home/zaks/zakops-agent-api/.claude/rules /home/zaks/zakops-agent-api/.claude/rules.disabled

# Reset permissions (settings.json)
cp ~/claude-backup-$(date +%Y%m%d)/settings.json ~/.claude/settings.json
```

### TriPass Run Cleanup

```bash
# Abandon a stuck run (remove lock)
rm -f /tmp/tripass.lock

# View run status
make tripass-status RUN_ID=<id>

# Re-run gates on a completed run
make tripass-gates RUN_ID=<id>
```

---

## Part 9: WSL Environment Hazards

### CRLF Line Endings

Every file written via Claude Code's Write tool gets Windows line endings (CRLF). **Always run `sed -i 's/\r$//'` after writing any `.sh` file.** Symptom: `bash\r: not found` (exit 127).

### Root Ownership

Claude Code runs as root. Every file created is owned by `root:root`. **Run `chown zaks:zaks <file>` after creating files in `/home/zaks/`**. Symptom: EACCES when user runs make targets.

The TriPass pipeline handles this automatically via ENH-9 (`chown -R zaks:zaks` at pipeline end).

### Dual Path Formats

- Linux paths: `/home/zaks/...`
- Windows paths via WSL: `/mnt/c/Users/mzsai/...`
- The `/mnt/c/` prefix accesses Windows filesystem. Do not use for scripts or configs.

### Docker Socket Permissions

Docker socket at `/var/run/docker.sock` may require root access. Claude Code (running as root) has access; the `zaks` user may not without `sudo`.

### Dual Tool Paths

Monorepo tools at `/home/zaks/zakops-agent-api/tools/infra/` vs external tools at `/home/zaks/tools/infra/`. Makefile expects monorepo-relative paths. Never write scripts to the external path when Makefile references them.

### `grep -c` Exit Code

Returns exit 1 when count is 0. Use `VAR=$(grep -c ... 2>/dev/null) || VAR=0` — not `$(grep -c ... || echo 0)`.

---

## Appendix A: Complete File Inventory

### Configuration Files

| File | Path | Editable | Update Mechanism |
|------|------|----------|-----------------|
| settings.json | `~/.claude/settings.json` | Yes (carefully) | Manual edit |
| CLAUDE.md (root) | `/home/zaks/CLAUDE.md` | Yes | Manual edit |
| CLAUDE.md (monorepo) | `/home/zaks/zakops-agent-api/CLAUDE.md` | Yes (ceiling: 150 lines) | Manual edit |
| MEMORY.md | `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | Yes + auto-sync | memory-sync.sh + manual |

### Hook Scripts

| Script | Path | Event |
|--------|------|-------|
| pre-edit.sh | `~/.claude/hooks/pre-edit.sh` | PreToolUse (Edit, Write) |
| pre-bash.sh | `~/.claude/hooks/pre-bash.sh` | PreToolUse (Bash) |
| post-edit.sh | `~/.claude/hooks/post-edit.sh` | PostToolUse (Edit, Write) |
| stop.sh | `~/.claude/hooks/stop.sh` | Stop |
| memory-sync.sh | `~/.claude/hooks/memory-sync.sh` | Called by stop.sh |

### Path-Scoped Rules

| File | Path | Trigger |
|------|------|---------|
| agent-tools.md | `.claude/rules/agent-tools.md` | Agent tool files |
| backend-api.md | `.claude/rules/backend-api.md` | Backend files |
| contract-surfaces.md | `.claude/rules/contract-surfaces.md` | Contracts, generated files |
| dashboard-types.md | `.claude/rules/dashboard-types.md` | Dashboard types, lib |
| design-system.md | `.claude/rules/design-system.md` | Dashboard components, app, styles |

### Agent Definitions

| Agent | Path | Model |
|-------|------|-------|
| Architecture Reviewer | `~/.claude/agents/arch-reviewer.md` | Opus |
| Contract Guardian | `~/.claude/agents/contract-guardian.md` | Sonnet |
| Test Engineer | `~/.claude/agents/test-engineer.md` | Sonnet |

---

## Appendix B: OpenAPI Specs, Generated Files & Bridge Files

### Spec Files

| Spec | Path | Size |
|------|------|------|
| Backend API | `packages/contracts/openapi/zakops-api.json` | 183KB |
| Agent API | `packages/contracts/openapi/agent-api.json` | 72KB |
| RAG API | `packages/contracts/openapi/rag-api.json` | 6.9KB |
| Agent Events | `packages/contracts/openapi/agent-events.schema.json` | 3.9KB |
| MCP Tools | `packages/contracts/mcp/tool-schemas.json` | 8.4KB |
| Runtime Topology | `packages/contracts/runtime.topology.json` | 2.8KB |

### Generated Files (DO NOT EDIT)

| File | Lines | Sync Command |
|------|-------|-------------|
| `apps/dashboard/src/lib/api-types.generated.ts` | 5,786 | `make sync-types` |
| `apps/dashboard/src/lib/agent-api-types.generated.ts` | 2,229 | `make sync-agent-types` |
| `apps/agent-api/app/schemas/backend_models.py` | 609 | `make sync-backend-models` |
| `zakops-backend/src/schemas/rag_models.py` | 32 | `make sync-rag-models` |

### Bridge Files (Hand-Written)

| File | Lines | Purpose |
|------|-------|---------|
| `apps/dashboard/src/types/api.ts` | 376 | Business logic abstractions, union types |
| `apps/dashboard/src/types/agent-api.ts` | 91 | Agent event types, payload extensions |
| `apps/dashboard/src/types/execution-contracts.ts` | 645 | Deal FSM, pipeline stages, transitions |
| `apps/dashboard/src/types/design-system-manifest.ts` | 102 | Surface 9 convention declarations |

---

## Appendix C: Glossary

| Term | Definition |
|------|-----------|
| **Append-only discipline** | Evidence files (WORKSPACE.md, MASTER_LOG.md) can only be appended to, never overwritten. Verified by Gate T-1 |
| **Bridge file** | Hand-written TypeScript/Python file that re-exports from generated types with additional business logic. The only valid import source for consumers |
| **Contract surface** | A formalized boundary between systems, enforced by spec files, codegen, and validation gates |
| **Deal Integrity patterns** | 7 mandatory architectural conventions from DEAL-INTEGRITY-UNIFIED-001 (see Part 6) |
| **Generate-only mode** | TriPass execution mode where prompts are saved as PROMPT.md but no CLI agents execute |
| **Hybrid Guardrail** | The pattern: OpenAPI spec → codegen → generated file → bridge file → consumer |
| **PIPELINE_STAGES** | Single source of truth for deal pipeline stage definitions, in `execution-contracts.ts` |
| **Sentinel tag** | `<!-- AUTOSYNC:key -->` pattern in MEMORY.md, auto-updated by memory-sync.sh |
| **Surface 9** | Component Design System → Dashboard; governs frontend conventions and design quality |
| **Trap handler** | Bash `trap` command ensuring lock file cleanup on EXIT, ERR, INT, TERM signals |
| **TriPass** | Three-Pass Pipeline — multi-agent orchestrator running Claude/Gemini/Codex as investigators |
| **V5PP** | Version 5 of the Protection Pipeline (predecessor to V6PP) |
| **V6PP** | Version 6 of the Protection Pipeline — this document captures its full state |
| **ADR** | Architecture Decision Record; documents a significant design choice with context and consequences |
| **BackendClient** | The only permitted HTTP client for Agent API → Backend API communication |
| **Category A** | Project-specific architectural conventions in Surface 9 (7 rules from Deal Integrity) |
| **Category B** | General frontend design quality standards in Surface 9 (7 areas of guidance) |
| **Codegen** | Automatic generation of TypeScript types or Python models from OpenAPI specs |
| **Config-Stabilize** | Mission that remediated 14 configuration findings across hooks, memory, and settings |
| **Deal Integrity** | Mission that established 7 mandatory frontend patterns and 3 ADRs |
| **Fast Tier** | Stop hook validation tier: tsc + Redocly + contract surfaces + httpx check |
| **Gate** | An automated check that must pass for a deliverable to be considered valid |
| **Idempotent** | An operation that produces the same result whether executed once or multiple times |
| **Lock file** | `/tmp/tripass.lock` — prevents concurrent TriPass runs |
| **Mission** | A structured task with acceptance criteria, gates, and deliverables |
| **Redocly ceiling** | Maximum allowed lint ignores (57); any new ignore breaks validation |

---

## Appendix D: Agent Definition Files

### Architecture Reviewer (`~/.claude/agents/arch-reviewer.md`)

```yaml
name: Architecture Reviewer
description: Read-only architecture and security reviewer
model: opus
tools: Read, Grep, Glob
```

Analyzes proposed changes for risks, missed edge cases, and cross-surface impact. Invoked before high-impact changes.

### Contract Guardian (`~/.claude/agents/contract-guardian.md`)

```yaml
name: Contract Guardian
description: Read-only validator for all 9 contract surfaces
model: sonnet
tools: Read, Grep, Glob, Bash(make:*), Bash(npx:*), ...
```

Runs gates, reports drift, cannot modify source code. Runs automatically via stop hook.

### Test Engineer (`~/.claude/agents/test-engineer.md`)

```yaml
name: Test Engineer
description: Writes tests and validates golden payloads
model: sonnet
tools: Read, Grep, Glob, Write, Bash(npx:*), Bash(pytest:*), ...
```

Can only write to test directories. Cannot modify production code.

---

## Appendix E: Completed Missions Registry

| Mission ID | Date | Status | Summary |
|-----------|------|--------|---------|
| RT-HARDEN-001 V2 | 2026-02-06 | 19/19 PASS | Runtime hardening across all services |
| HYBRID-GUARDRAIL-EXEC-001 | 2026-02-06 | Complete | Established hybrid guardrail framework |
| QA-HG-VERIFY-001-V2 | 2026-02-06 | FULL PASS | Guardrail QA verification after remediation |
| DEAL-INTEGRITY-UNIFIED-001 | 2026-02-09 | Complete | 6 layers, 13 resolved issues, 3 ADRs |
| CONFIG-STABILIZE-001 | 2026-02-09 | Complete | 14 findings remediated across config |
| TRIPASS-INTEGRATE-002 | 2026-02-09 | Complete | Multi-agent pipeline orchestrator, 9 AC all PASS |
| QA-TP-VERIFY-001 | 2026-02-09 | FULL PASS | 75/75 gates, 0 remediations |
| QA-TP-V2-001 | 2026-02-09 | FULL PASS | 67/67 gates, mission spec compliance audit |
| V6-GUIDE-REGEN-001 | 2026-02-09 | Complete | Surface 9, TriPass QA hardening, V6PP guide |

---

## Document Information

| Field | Value |
|-------|-------|
| **Version** | V6PP 6.0 |
| **Date** | 2026-02-09 |
| **Supersedes** | V5PP-DMS (2026-02-07) |
| **Generated by** | Claude Opus 4.6 from live system state |
| **Key changes** | Surface 9 added, TriPass QA hardened, phantom plugin removed, 9 contract surfaces documented |
| **Validation** | All facts verified against live filesystem at generation time |
