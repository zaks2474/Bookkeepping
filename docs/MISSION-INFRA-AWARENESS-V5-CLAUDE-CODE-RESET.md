# CLAUDE CODE MISSION: INFRASTRUCTURE AWARENESS V5 — FULL RESET

## Mission ID: INFRA-AWARENESS-V5
## Codename: "Total Recall"
## Priority: P0 — Claude Code Cannot Be Effective Without This
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Rewrite everything, verify everything

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   DIRECTIVE: RESET CLAUDE CODE'S BRAIN                                       ║
║                                                                              ║
║   Infrastructure Awareness V4 was completed on 2026-02-06.                   ║
║   Then EXEC-001, EXEC-002, and QA-HG-VERIFY-002 happened.                  ║
║   These missions added 6 new contract surfaces, 5 new Makefile targets,     ║
║   2 new bridge files, typed Python SDKs, 2 new OpenAPI specs, SSE event     ║
║   schemas, and completely rewrote deal_tools.py.                            ║
║                                                                              ║
║   The current CLAUDE.md knows NONE of this.                                  ║
║   The infrastructure manifest generator covers 1/7 contract surfaces.        ║
║   The cross-layer validation checks 1/7 codegen pipelines.                  ║
║   The dependency graph is incomplete.                                        ║
║                                                                              ║
║   END STATE: When a developer asks Claude Code to make ANY change,          ║
║   Claude Code automatically:                                                 ║
║     1. Knows the full system topology (all 7 contract surfaces)             ║
║     2. Understands which layers the change affects                           ║
║     3. Makes the change                                                      ║
║     4. Runs the correct sync/codegen targets to realign affected layers     ║
║     5. Validates that all layers are still aligned                           ║
║     6. Reports what it changed and what it re-aligned                       ║
║                                                                              ║
║   This is NOT a new system. V4 infrastructure exists and works.             ║
║   This mission UPDATES it to cover everything that was added since V4.      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## CONTEXT: WHAT CHANGED SINCE V4

### V4 Knew About (1 contract surface):
- Backend OpenAPI → Dashboard TypeScript types (sync-types)
- contracts/ directory with stages.json, statuses.json
- Infrastructure manifest generator
- Cross-layer validation scripts
- CLAUDE.md with pre/post task hooks
- Git pre-commit hook
- .claude/commands/infra-check.md

### What Was Added After V4 (6 new contract surfaces + massive infrastructure):

| # | Contract Surface | Spec Location | Codegen Target | Output |
|---|-----------------|---------------|----------------|--------|
| 1 | Backend → Dashboard | packages/contracts/openapi/zakops-api.json | `make sync-types` | apps/dashboard/src/lib/api-types.generated.ts |
| 2 | Agent → Backend SDK | packages/contracts/openapi/zakops-api.json | `make sync-backend-models` | apps/agent-api/app/schemas/backend_models.py |
| 3 | Agent OpenAPI spec | packages/contracts/openapi/agent-api.json | `make update-agent-spec` | (exports from live Agent API) |
| 4 | Dashboard ← Agent | packages/contracts/openapi/agent-api.json | `make sync-agent-types` | apps/dashboard/src/lib/agent-api-types.generated.ts |
| 5 | Backend → RAG SDK | packages/contracts/openapi/rag-api.json | `make sync-rag-models` | zakops-backend/src/schemas/rag_models.py |
| 6 | MCP Tool Schemas | packages/contracts/mcp/tool-schemas.json | (exported from Pydantic) | zakops-backend/mcp_server/tool_schemas.py |
| 7 | SSE Event Schema | packages/contracts/sse/agent-events.schema.json | (reference schema) | Dashboard SSE event parsing |

#### New Makefile Targets
```
sync-backend-models    # Backend spec → Agent API Python models
sync-agent-types       # Agent spec → Dashboard TypeScript types
sync-rag-models        # RAG spec → Backend Python models
sync-all-types         # ALL codegen operations (composite)
update-agent-spec      # Export live Agent API → committed spec
validate-local         # Offline validation (CI-safe, no running services)
validate-live          # Online validation (requires running services)
```

#### New Bridge Files (ESLint-enforced import patterns)
- `apps/dashboard/src/types/api.ts` — Bridge for Backend types (MUST import from here, NOT api-types.generated.ts)
- `apps/dashboard/src/types/agent-api.ts` — Bridge for Agent types (MUST import from here, NOT agent-api-types.generated.ts)

#### New Typed Python SDKs
- `apps/agent-api/app/schemas/backend_models.py` — Pydantic models matching Backend API responses
- `apps/agent-api/app/services/backend_client.py` — Typed HTTP client (Agent → Backend)
- `zakops-backend/src/schemas/rag_models.py` — Pydantic models matching RAG API responses
- `zakops-backend/src/services/rag_client.py` — Typed HTTP client (Backend → RAG)

#### deal_tools.py Rewrite (QA-HG-VERIFY-002 R-1)
- ALL 39 `.get()` patterns eliminated → 0
- ALL 8 `response.json()` patterns eliminated → 0
- 22 BackendClient references added
- deal_tools.py now uses typed SDK instead of raw HTTP

#### New Tracking Files
- `debt-ledger.md` — Technical debt tracking with EXEC-001 and EXEC-002 sections
- `.github/workflows/spec-freshness-bot.yml` — Automated spec drift detection
- `packages/contracts/sse/agent-events.schema.json` — 5 SSE event type definitions
- `packages/contracts/runtime.topology.json` — Service/DB mapping (v3.1)

#### Database Migration Tracking (all 3 databases)
- zakops (backend): Alembic migrations
- zakops_agent (agent): SQL migrations in apps/agent-api/migrations/
- crawlrag (RAG): SQL migrations in Zaks-llm/db/migrations/
- `tools/infra/migration-assertion.sh` — Checks all 3 databases

---

## SECTION 0: DISCOVERY — VERIFY CURRENT STATE

**Before changing anything, discover what actually exists right now.**

```bash
# ════════════════════════════════════════════════════
# STEP 0.1: Find all project roots
# ════════════════════════════════════════════════════

echo "=== PROJECT ROOTS ==="
# These are the known repository roots. VERIFY they exist.
MONOREPO_ROOT="/home/zaks/zakops-agent-api"
BACKEND_ROOT="/home/zaks/zakops-backend"
DASHBOARD_ROOT="$MONOREPO_ROOT/apps/dashboard"
AGENT_API_ROOT="$MONOREPO_ROOT/apps/agent-api"
RAG_ROOT="/home/zaks/Zaks-llm"
MCP_ROOT="$BACKEND_ROOT/mcp_server"

for dir in "$MONOREPO_ROOT" "$BACKEND_ROOT" "$DASHBOARD_ROOT" "$AGENT_API_ROOT" "$RAG_ROOT" "$MCP_ROOT"; do
  if [ -d "$dir" ]; then
    echo "✅ $dir"
  else
    echo "❌ $dir NOT FOUND — investigate"
  fi
done

# ════════════════════════════════════════════════════
# STEP 0.2: Find current CLAUDE.md
# ════════════════════════════════════════════════════

echo ""
echo "=== CURRENT CLAUDE.md ==="
for loc in "$MONOREPO_ROOT/.claude/CLAUDE.md" "$MONOREPO_ROOT/CLAUDE.md"; do
  if [ -f "$loc" ]; then
    echo "Found: $loc"
    echo "--- Content (first 50 lines) ---"
    head -50 "$loc"
    echo "--- Size ---"
    wc -l "$loc"
  fi
done

# ════════════════════════════════════════════════════
# STEP 0.3: Find current Makefile and list ALL targets
# ════════════════════════════════════════════════════

echo ""
echo "=== MAKEFILE TARGETS ==="
grep "^[a-z].*:" "$MONOREPO_ROOT/Makefile" 2>/dev/null | sort

# ════════════════════════════════════════════════════
# STEP 0.4: Find all committed specs
# ════════════════════════════════════════════════════

echo ""
echo "=== COMMITTED SPECS ==="
find "$MONOREPO_ROOT/packages/contracts" -name "*.json" -type f 2>/dev/null | sort

# ════════════════════════════════════════════════════
# STEP 0.5: Find all generated type files
# ════════════════════════════════════════════════════

echo ""
echo "=== GENERATED TYPE FILES ==="
find "$DASHBOARD_ROOT/src" -name "*.generated.ts" -type f 2>/dev/null
find "$AGENT_API_ROOT" -name "backend_models.py" -type f 2>/dev/null
find "$BACKEND_ROOT" -name "rag_models.py" -type f 2>/dev/null

# ════════════════════════════════════════════════════
# STEP 0.6: Find all bridge files
# ════════════════════════════════════════════════════

echo ""
echo "=== BRIDGE FILES ==="
for bridge in "$DASHBOARD_ROOT/src/types/api.ts" "$DASHBOARD_ROOT/src/types/agent-api.ts"; do
  if [ -f "$bridge" ]; then
    echo "✅ $bridge"
    # Count manual types
    MANUAL=$(grep -c "MANUAL_TYPE_DEBT\|Manual:" "$bridge" 2>/dev/null || echo 0)
    echo "   Manual type debt: $MANUAL"
  else
    echo "❌ $bridge NOT FOUND"
  fi
done

# ════════════════════════════════════════════════════
# STEP 0.7: Find all validation/infra scripts
# ════════════════════════════════════════════════════

echo ""
echo "=== VALIDATION SCRIPTS ==="
find "$MONOREPO_ROOT/tools" -name "*.sh" -type f 2>/dev/null | sort

# ════════════════════════════════════════════════════
# STEP 0.8: Find existing .claude/commands/
# ════════════════════════════════════════════════════

echo ""
echo "=== CLAUDE COMMANDS ==="
find "$MONOREPO_ROOT/.claude" -type f 2>/dev/null | sort

# ════════════════════════════════════════════════════
# STEP 0.9: Find existing hooks
# ════════════════════════════════════════════════════

echo ""
echo "=== GIT HOOKS ==="
ls -la "$MONOREPO_ROOT/.git/hooks/pre-commit" 2>/dev/null
ls -la "$MONOREPO_ROOT/tools/hooks/" 2>/dev/null

# ════════════════════════════════════════════════════
# STEP 0.10: Service health
# ════════════════════════════════════════════════════

echo ""
echo "=== SERVICE HEALTH ==="
for svc in "Backend:8091:/health" "Agent:8095:/health" "Dashboard:3003:/"; do
  name=$(echo $svc | cut -d: -f1)
  port=$(echo $svc | cut -d: -f2)
  path=$(echo $svc | cut -d: -f3)
  STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:$port$path" 2>/dev/null || echo "DOWN")
  echo "$name (port $port): $STATUS"
done
```

**IMPORTANT: Capture the output of ALL discovery steps. The rest of this mission adapts based on what actually exists.**

---

## FIX 1 (P0): REWRITE CLAUDE.md — THE COMPLETE SYSTEM MAP

**This is the most important deliverable.** CLAUDE.md is what Claude Code reads at the start of every session. If it's incomplete, Claude Code is flying blind.

### What CLAUDE.md Must Contain

The new CLAUDE.md replaces the V4 version entirely. It must contain these sections:

```markdown
# ZakOps — Claude Code System Guide

## Quick Reference

### Project Roots
| Repository | Path | Purpose |
|-----------|------|---------|
| Monorepo (agent-api + dashboard) | /home/zaks/zakops-agent-api | Agent API, Dashboard, contracts, tools |
| Backend | /home/zaks/zakops-backend | FastAPI backend, MCP server |
| RAG/LLM | /home/zaks/Zaks-llm | RAG service, vector DB, LLM integration |

### Services
| Service | Port | Tech | Health Check |
|---------|------|------|-------------|
| Dashboard | 3003 | Next.js 15 | GET / |
| Backend API | 8091 | FastAPI | GET /health |
| Agent API | 8095 | FastAPI + LangGraph | GET /health |
| RAG API | 8052 | FastAPI | GET /health |
| MCP Server | 9100 | Custom Protocol | (native process) |
| PostgreSQL (backend) | 5435 | PostgreSQL | zakops database |
| PostgreSQL (agent) | 5432 | pgvector | zakops_agent database |
| vLLM | 8000 | vLLM | GET /health |

### Databases
| Database | Schema | User | Service | Migrations |
|----------|--------|------|---------|-----------|
| zakops | zakops | zakops | Backend API | Alembic (zakops-backend/db/migrations/) |
| zakops_agent | public | agent | Agent API | SQL (apps/agent-api/migrations/) |
| crawlrag | public | (from DATABASE_URL) | RAG API | SQL (Zaks-llm/db/migrations/) |

---

## The 7 Contract Surfaces (Hybrid Guardrail)

These are the compiler-enforced alignment pipelines. When you change a schema
in any service, the corresponding codegen pipeline must be run to keep all
layers aligned.

### Surface 1: Backend → Dashboard (TypeScript)
- **Spec:** packages/contracts/openapi/zakops-api.json
- **Command:** `make sync-types`
- **Output:** apps/dashboard/src/lib/api-types.generated.ts
- **Bridge:** apps/dashboard/src/types/api.ts
- **Rule:** Dashboard components MUST import from @/types/api, NEVER from api-types.generated.ts directly
- **ESLint:** no-restricted-imports blocks direct generated file imports

### Surface 2: Backend → Agent SDK (Python)
- **Spec:** packages/contracts/openapi/zakops-api.json
- **Command:** `make sync-backend-models`
- **Output:** apps/agent-api/app/schemas/backend_models.py
- **Consumer:** apps/agent-api/app/services/backend_client.py
- **Rule:** Agent tools MUST use BackendClient, NEVER raw HTTP requests
- **Verification:** `grep -c '.get(' apps/agent-api/app/core/langgraph/tools/deal_tools.py` → MUST be 0

### Surface 3: Agent API OpenAPI Spec
- **Spec:** packages/contracts/openapi/agent-api.json
- **Command:** `make update-agent-spec` (exports from live Agent API)
- **Prerequisite:** Agent API must be running on port 8095
- **Note:** This is an EXPORT, not a codegen. It captures the current Agent API schema.

### Surface 4: Agent → Dashboard (TypeScript)
- **Spec:** packages/contracts/openapi/agent-api.json
- **Command:** `make sync-agent-types`
- **Output:** apps/dashboard/src/lib/agent-api-types.generated.ts
- **Bridge:** apps/dashboard/src/types/agent-api.ts
- **Rule:** Dashboard components MUST import from @/types/agent-api, NEVER from agent-api-types.generated.ts directly

### Surface 5: RAG → Backend SDK (Python)
- **Spec:** packages/contracts/openapi/rag-api.json
- **Command:** `make sync-rag-models`
- **Output:** zakops-backend/src/schemas/rag_models.py
- **Consumer:** zakops-backend/src/services/rag_client.py

### Surface 6: MCP Tool Schemas
- **Spec:** packages/contracts/mcp/tool-schemas.json
- **Source:** zakops-backend/mcp_server/tool_schemas.py (Pydantic classes)
- **Rule:** MCP tools defined in tool_schemas.py, exported to JSON schema

### Surface 7: SSE Event Schema
- **Spec:** packages/contracts/sse/agent-events.schema.json
- **Defines:** 5 SSE event types (agent_thinking, tool_call, tool_result, agent_response, agent_error)
- **Consumer:** Dashboard SSE event parsing

---

## Dependency Graph — What to Sync After Changes

### If you change a Backend API endpoint or response schema:
1. `make update-spec` — refresh committed Backend OpenAPI spec
2. `make sync-types` — regenerate Dashboard TypeScript types
3. `make sync-backend-models` — regenerate Agent SDK Python models
4. `npx tsc --noEmit` — verify Dashboard compiles
5. Run any affected tests

### If you change an Agent API endpoint or response schema:
1. `make update-agent-spec` — refresh committed Agent OpenAPI spec (Agent API must be running)
2. `make sync-agent-types` — regenerate Dashboard TypeScript types for Agent
3. `npx tsc --noEmit` — verify Dashboard compiles

### If you change a RAG API endpoint or response schema:
1. Export the new RAG spec (or update packages/contracts/openapi/rag-api.json manually)
2. `make sync-rag-models` — regenerate Backend Python models
3. Verify BackendClient still works with RAG

### If you change MCP tool definitions:
1. Update tool_schemas.py in zakops-backend/mcp_server/
2. Export to packages/contracts/mcp/tool-schemas.json
3. Verify MCP server starts correctly

### If you change SSE event types:
1. Update packages/contracts/sse/agent-events.schema.json
2. Update Dashboard SSE event parsing to match
3. Update Agent API SSE emission to match

### If you change a database schema:
1. Create migration in the appropriate migrations directory
2. Run migration: `docker compose exec <service> python -m alembic upgrade head` (or SQL runner)
3. Run `make infra-migration-assert` to verify migration state
4. If the change affects API response shapes, follow the appropriate codegen pipeline above

### If you change stage or status values:
1. Update contracts/stages.json or contracts/statuses.json FIRST (single source of truth)
2. Update Backend Python enum/validator
3. Update Dashboard Zod schema
4. Update Agent tool parameters
5. Run `make infra-contracts` to verify alignment

### Quick reference — composite commands:
- `make sync-all-types` — runs ALL codegen operations
- `make validate-local` — offline validation (CI-safe, no running services needed)
- `make validate-live` — online validation (requires all services running)
- `make validate-all` — FULL system validation (infra + schema + routing + enforcement)
- `make infra-check` — infrastructure health (DB assertion + migration + manifest age)

---

## Pre-Task Protocol (MANDATORY)

Before starting any task that modifies code:

1. Read this file (you're doing it now)
2. Run: `make infra-snapshot` — generates fresh INFRASTRUCTURE_MANIFEST.md
3. Run: `make infra-check` — verifies DB + migrations + manifest freshness
4. Identify which contract surfaces your change will affect (see Dependency Graph)

## Post-Task Protocol (MANDATORY)

After completing any code change:

1. Run the appropriate `make sync-*` targets for affected surfaces
2. Run: `npx tsc --noEmit` (in apps/dashboard) — verify TypeScript compiles
3. Run: `make validate-local` — offline validation
4. If services are running: `make validate-live` — online validation
5. Verify no regressions in unrelated surfaces

## Non-Negotiable Rules

1. **NEVER hand-write types that should be generated.** If a type exists in an OpenAPI spec, use codegen.
2. **NEVER import generated files directly.** Always go through bridge files (@/types/api, @/types/agent-api).
3. **NEVER use raw HTTP in Agent tools.** Always use BackendClient with typed responses.
4. **NEVER modify generated files.** They will be overwritten by the next sync.
5. **NEVER add to manual type debt.** The ceiling can only go DOWN, never UP.
6. **ALWAYS update the spec BEFORE regenerating types.** Stale spec = stale types.
7. **ALWAYS run migration-assertion after DB changes.** File system must match DB state.
8. **Committed specs MUST match live backends.** Any drift is a bug.

---

## Tracking & Debt

- **debt-ledger.md** — Technical debt tracking (check before starting work)
- **spec-freshness-bot** — .github/workflows/spec-freshness-bot.yml (automated drift detection)
- **Manual type debt ceiling** — tracked in CI, cannot increase
- **Redocly ignore ceiling** — tracked in CI, cannot increase
- **Mypy baseline** — stored in tools/type_baselines/mypy_baseline.txt
```

### Implementation Instructions

1. **Read the current CLAUDE.md** to understand what V4 wrote
2. **REPLACE IT ENTIRELY** with the comprehensive version above
3. **Adapt paths and details** based on what Step 0 discovery found
4. **The content above is a template** — fill in actual values from discovery
5. **If any section references something that doesn't exist yet, note it as a gap to fix in subsequent steps**

```
GATE 1: CLAUDE.md rewritten with all 7 contract surfaces documented.
        Dependency graph covers all change scenarios.
        Pre/post task protocols reference correct make targets.
        Non-negotiable rules are comprehensive.
        File is >200 lines (the V4 version was too brief).
```

---

## FIX 2 (P0): UPDATE .claude/commands/ WITH ALL OPERATIONS

**V4 created `infra-check.md`. We now need commands for every common operation.**

### Commands to Create/Update

```
.claude/commands/
├── infra-check.md          ← V4 (update to include all 7 surfaces)
├── sync-all.md             ← NEW: run all codegen pipelines
├── sync-backend-types.md   ← NEW: Backend → Dashboard + Agent SDK
├── sync-agent-types.md     ← NEW: Agent → Dashboard
├── sync-rag-types.md       ← NEW: RAG → Backend SDK
├── validate.md             ← NEW: full validation suite
├── check-drift.md          ← NEW: check all specs vs live backends
└── after-change.md         ← NEW: post-change checklist (the key one)
```

### The Most Important Command: after-change.md

```markdown
# After-Change Validation

Run this after ANY code change to ensure all layers are aligned.

## Steps:
1. Identify affected contract surfaces
2. Run appropriate sync targets
3. Validate

## Commands:
```bash
# If you changed Backend API:
make update-spec && make sync-types && make sync-backend-models

# If you changed Agent API:
make update-agent-spec && make sync-agent-types

# If you changed RAG API:
make sync-rag-models

# Full sync (if unsure what changed):
make sync-all-types

# Validate:
make validate-local
npx tsc --noEmit --project apps/dashboard/tsconfig.json

# If services are running:
make validate-live
```
```

### Create each command file:

Each `.claude/commands/*.md` file should contain:
1. A brief description of what it does
2. The exact commands to run
3. What to check in the output
4. What to do if it fails

```
GATE 2: At least 7 command files in .claude/commands/
        after-change.md exists and covers all 7 contract surfaces
        Each command file has actionable content (not just a title)
```

---

## FIX 3 (P0): UPDATE INFRASTRUCTURE MANIFEST GENERATOR

**The V4 `tools/infra/generate-manifest.sh` only covers the V4 infrastructure. It needs to also cover all Hybrid Guardrail additions.**

### What to Add to the Manifest

The manifest generator must now include these additional sections:

```bash
# ════════════════════════════════════════════════════
# NEW SECTION: Contract Surfaces Status
# ════════════════════════════════════════════════════

echo "## Contract Surfaces (Hybrid Guardrail)" >> $OUTPUT
echo "" >> $OUTPUT

# For each committed spec, report:
# - File exists: Y/N
# - Last modified date
# - Schema count
# - Endpoint count (for OpenAPI specs)

for spec in \
  "packages/contracts/openapi/zakops-api.json:Backend API" \
  "packages/contracts/openapi/agent-api.json:Agent API" \
  "packages/contracts/openapi/rag-api.json:RAG API" \
  "packages/contracts/mcp/tool-schemas.json:MCP Tools" \
  "packages/contracts/sse/agent-events.schema.json:SSE Events"; do

  file=$(echo $spec | cut -d: -f1)
  name=$(echo $spec | cut -d: -f2)

  if [ -f "$file" ]; then
    modified=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
    size=$(wc -c < "$file")
    echo "- $name: ✅ ($size bytes, modified $(date -d @$modified +%Y-%m-%d 2>/dev/null || date -r $modified +%Y-%m-%d))" >> $OUTPUT
  else
    echo "- $name: ❌ NOT FOUND" >> $OUTPUT
  fi
done
echo "" >> $OUTPUT

# ════════════════════════════════════════════════════
# NEW SECTION: Generated Type Files
# ════════════════════════════════════════════════════

echo "## Generated Type Files" >> $OUTPUT
echo "" >> $OUTPUT

for gen in \
  "apps/dashboard/src/lib/api-types.generated.ts:Dashboard Backend Types" \
  "apps/dashboard/src/lib/agent-api-types.generated.ts:Dashboard Agent Types" \
  "apps/agent-api/app/schemas/backend_models.py:Agent Backend SDK" \
  "zakops-backend/src/schemas/rag_models.py:Backend RAG SDK"; do

  file=$(echo $gen | cut -d: -f1)
  name=$(echo $gen | cut -d: -f2)

  if [ -f "$file" ]; then
    lines=$(wc -l < "$file")
    echo "- $name: ✅ ($lines lines)" >> $OUTPUT
  else
    echo "- $name: ❌ NOT FOUND" >> $OUTPUT
  fi
done
echo "" >> $OUTPUT

# ════════════════════════════════════════════════════
# NEW SECTION: Bridge File Status
# ════════════════════════════════════════════════════

echo "## Bridge Files (Manual Type Debt)" >> $OUTPUT
echo "" >> $OUTPUT

for bridge in \
  "apps/dashboard/src/types/api.ts:Backend Bridge" \
  "apps/dashboard/src/types/agent-api.ts:Agent Bridge"; do

  file=$(echo $bridge | cut -d: -f1)
  name=$(echo $bridge | cut -d: -f2)

  if [ -f "$file" ]; then
    debt=$(grep -c "MANUAL_TYPE_DEBT\|Manual:" "$file" 2>/dev/null || echo 0)
    echo "- $name: ✅ (manual debt: $debt)" >> $OUTPUT
  else
    echo "- $name: ❌ NOT FOUND" >> $OUTPUT
  fi
done
echo "" >> $OUTPUT

# ════════════════════════════════════════════════════
# NEW SECTION: Typed SDK Status
# ════════════════════════════════════════════════════

echo "## Typed SDKs" >> $OUTPUT
echo "" >> $OUTPUT

# BackendClient usage in deal_tools.py
DEAL_TOOLS="apps/agent-api/app/core/langgraph/tools/deal_tools.py"
if [ -f "$DEAL_TOOLS" ]; then
  GET_COUNT=$(grep -c '\.get(' "$DEAL_TOOLS" 2>/dev/null || echo 0)
  JSON_COUNT=$(grep -c 'response\.json()' "$DEAL_TOOLS" 2>/dev/null || echo 0)
  CLIENT_COUNT=$(grep -c 'BackendClient\|backend_client' "$DEAL_TOOLS" 2>/dev/null || echo 0)
  echo "- deal_tools.py: .get()=$GET_COUNT, response.json()=$JSON_COUNT, BackendClient=$CLIENT_COUNT" >> $OUTPUT
  if [ "$GET_COUNT" -gt 0 ] || [ "$JSON_COUNT" -gt 0 ]; then
    echo "  ⚠️  WARNING: Untyped patterns detected — should be 0" >> $OUTPUT
  fi
fi
echo "" >> $OUTPUT

# ════════════════════════════════════════════════════
# NEW SECTION: Make Sync Targets Available
# ════════════════════════════════════════════════════

echo "## Available Sync Targets" >> $OUTPUT
echo "" >> $OUTPUT
for target in sync-types sync-backend-models sync-agent-types sync-rag-models sync-all-types update-spec update-agent-spec validate-local validate-live; do
  if grep -q "^$target:" Makefile 2>/dev/null; then
    echo "- make $target: ✅" >> $OUTPUT
  else
    echo "- make $target: ❌ NOT FOUND" >> $OUTPUT
  fi
done
echo "" >> $OUTPUT
```

### Implementation

1. **Read the current `tools/infra/generate-manifest.sh`**
2. **Add the sections above** AFTER the existing sections (don't remove V4 content)
3. **Test:** Run `make infra-snapshot` and verify the manifest includes all new sections
4. **Verify:** The manifest should now be significantly larger than the V4 version

```
GATE 3: make infra-snapshot generates manifest with contract surfaces section.
        Manifest includes generated type files section.
        Manifest includes bridge file debt status.
        Manifest includes SDK status with deal_tools.py metrics.
        Manifest includes make target availability check.
        Manifest is >250 lines (V4 was ~214).
```

---

## FIX 4 (P1): UPDATE CROSS-LAYER VALIDATION

**The V4 `validate-cross-layer` and `validate-all` targets need to cover the new surfaces.**

### New Validation Checks to Add

```bash
# ════════════════════════════════════════════════════
# CHECK: All generated files are newer than their source specs
# ════════════════════════════════════════════════════

echo "=== GENERATED FILE FRESHNESS ==="

check_freshness() {
  local spec="$1"
  local generated="$2"
  local name="$3"

  if [ -f "$spec" ] && [ -f "$generated" ]; then
    SPEC_TIME=$(stat -c %Y "$spec" 2>/dev/null || stat -f %m "$spec")
    GEN_TIME=$(stat -c %Y "$generated" 2>/dev/null || stat -f %m "$generated")
    if [ "$GEN_TIME" -ge "$SPEC_TIME" ]; then
      echo "✅ $name: generated file is current"
    else
      echo "❌ $name: STALE — generated file is older than spec"
      echo "   Run the appropriate make sync-* target"
      FAILURES=$((FAILURES+1))
    fi
  elif [ ! -f "$spec" ]; then
    echo "⚠️  $name: spec not found ($spec)"
  elif [ ! -f "$generated" ]; then
    echo "❌ $name: generated file not found ($generated)"
    FAILURES=$((FAILURES+1))
  fi
}

check_freshness "packages/contracts/openapi/zakops-api.json" \
                "apps/dashboard/src/lib/api-types.generated.ts" \
                "Backend → Dashboard types"

check_freshness "packages/contracts/openapi/zakops-api.json" \
                "apps/agent-api/app/schemas/backend_models.py" \
                "Backend → Agent SDK"

check_freshness "packages/contracts/openapi/agent-api.json" \
                "apps/dashboard/src/lib/agent-api-types.generated.ts" \
                "Agent → Dashboard types"

check_freshness "packages/contracts/openapi/rag-api.json" \
                "zakops-backend/src/schemas/rag_models.py" \
                "RAG → Backend SDK"

# ════════════════════════════════════════════════════
# CHECK: TypeScript compilation
# ════════════════════════════════════════════════════

echo ""
echo "=== TYPESCRIPT COMPILATION ==="
cd apps/dashboard
if npx tsc --noEmit 2>&1; then
  echo "✅ TypeScript compiles"
else
  echo "❌ TypeScript compilation FAILED"
  FAILURES=$((FAILURES+1))
fi
cd "$OLDPWD"

# ════════════════════════════════════════════════════
# CHECK: Bridge file import enforcement
# ════════════════════════════════════════════════════

echo ""
echo "=== BRIDGE IMPORT ENFORCEMENT ==="

# Check for direct generated file imports (the anti-pattern)
DIRECT_IMPORTS=$(grep -rn "api-types\.generated\|agent-api-types\.generated" \
  apps/dashboard/src/components/ apps/dashboard/src/hooks/ apps/dashboard/src/app/ \
  --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l)

if [ "$DIRECT_IMPORTS" -eq 0 ]; then
  echo "✅ No direct generated file imports"
else
  echo "❌ $DIRECT_IMPORTS direct imports of generated files found (must use bridge)"
  FAILURES=$((FAILURES+1))
fi

# ════════════════════════════════════════════════════
# CHECK: deal_tools.py typed SDK usage
# ════════════════════════════════════════════════════

echo ""
echo "=== TYPED SDK ENFORCEMENT ==="

DEAL_TOOLS="apps/agent-api/app/core/langgraph/tools/deal_tools.py"
if [ -f "$DEAL_TOOLS" ]; then
  GET_COUNT=$(grep -c '\.get(' "$DEAL_TOOLS" 2>/dev/null || echo 0)
  JSON_COUNT=$(grep -c 'response\.json()' "$DEAL_TOOLS" 2>/dev/null || echo 0)

  if [ "$GET_COUNT" -gt 0 ] || [ "$JSON_COUNT" -gt 0 ]; then
    echo "❌ deal_tools.py still has untyped patterns (.get()=$GET_COUNT, response.json()=$JSON_COUNT)"
    FAILURES=$((FAILURES+1))
  else
    echo "✅ deal_tools.py uses typed SDK (0 untyped patterns)"
  fi
fi
```

### Implementation

1. **Read the current validation scripts** in tools/infra/ and tools/validation/
2. **Add the checks above** to the appropriate scripts (or create a new `validate-contract-surfaces.sh`)
3. **Wire into the Makefile** — either add to `validate-local` or create a new target `validate-contracts`
4. **Ensure `validate-all` includes** the new checks

```
GATE 4: Validation covers all 7 contract surfaces.
        Generated file freshness check catches stale types.
        Bridge import enforcement catches direct generated imports.
        deal_tools.py typed SDK check catches regression.
        make validate-local includes all new checks.
```

---

## FIX 5 (P1): UPDATE DEPENDENCY GRAPH IN MANIFEST

**The V4 manifest had a basic dependency graph. It needs to be comprehensive.**

### Replace the V4 Dependency Graph Section

```bash
# In generate-manifest.sh, replace the dependency graph with:

echo "## Dependency Graph (Impact Matrix)" >> $OUTPUT
echo "" >> $OUTPUT
cat << 'DEPGRAPH' >> $OUTPUT
### Change Impact Reference

| If You Change... | Run These Targets | Then Verify |
|-----------------|-------------------|-------------|
| Backend API endpoint/schema | `make update-spec && make sync-types && make sync-backend-models` | `npx tsc --noEmit`, Agent tools still work |
| Agent API endpoint/schema | `make update-agent-spec && make sync-agent-types` | `npx tsc --noEmit` |
| RAG API endpoint/schema | `make sync-rag-models` | Backend RAG calls still work |
| Dashboard component types | (nothing — types come FROM bridge) | `npx tsc --noEmit` |
| MCP tool definition | Update tool_schemas.py, export JSON | MCP server starts, tools listed |
| SSE event type | Update agent-events.schema.json | Dashboard SSE parsing, Agent emission |
| Database schema | Create migration, run it, `make infra-migration-assert` | API response shapes still match |
| Stage/status values | Update contracts/ FIRST, then all consumers | `make infra-contracts` |
| deal_tools.py | Use BackendClient methods ONLY | `grep -c '.get(' deal_tools.py` → 0 |

### Service → Database Mapping (DO NOT MIX UP)
| Service | Database | Schema | User |
|---------|----------|--------|------|
| Backend API (8091) | zakops | zakops | zakops |
| Agent API (8095) | zakops_agent | public | agent |
| RAG API (8052) | crawlrag | public | (from DATABASE_URL) |

### Codegen Flow Diagram
```
Backend (FastAPI) ──[openapi.json]──→ zakops-api.json ──→ api-types.generated.ts ──→ api.ts (bridge)
                                          │
                                          └──→ backend_models.py ──→ backend_client.py ──→ deal_tools.py

Agent API (FastAPI) ──[openapi.json]──→ agent-api.json ──→ agent-api-types.generated.ts ──→ agent-api.ts (bridge)

RAG API (FastAPI) ──[openapi.json]──→ rag-api.json ──→ rag_models.py ──→ rag_client.py

MCP Server ──[tool_schemas.py]──→ tool-schemas.json
SSE Events ──[agent-events.schema.json]──→ Dashboard parsing
```
DEPGRAPH
```

```
GATE 5: Dependency graph covers all 7 contract surfaces.
        Impact matrix shows exact make targets for each change type.
        Service → Database mapping is explicit.
        Codegen flow diagram is included.
```

---

## FIX 6 (P1): UPDATE PRE-COMMIT HOOK

**The V4 pre-commit hook only checks V4 infrastructure. It needs to catch Hybrid Guardrail violations too.**

### Add to Pre-Commit Hook

```bash
# Add these checks to tools/hooks/pre-commit:

# ════════════════════════════════════════════════════
# CHECK: No direct generated file imports in staged files
# ════════════════════════════════════════════════════

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx)$')

if [ -n "$STAGED_FILES" ]; then
  VIOLATIONS=$(echo "$STAGED_FILES" | xargs grep -l "api-types\.generated\|agent-api-types\.generated" 2>/dev/null | grep -v "src/types/" || true)
  if [ -n "$VIOLATIONS" ]; then
    echo "❌ PRE-COMMIT: Direct generated file imports detected:"
    echo "$VIOLATIONS"
    echo "Use @/types/api or @/types/agent-api instead."
    # In soft mode, warn. In hard mode, block.
    if [ "$ZAKOPS_HOOK_MODE" = "hard" ]; then
      exit 1
    fi
  fi
fi

# ════════════════════════════════════════════════════
# CHECK: If a spec changed, generated files should also be staged
# ════════════════════════════════════════════════════

STAGED=$(git diff --cached --name-only)

# If zakops-api.json changed, api-types.generated.ts should also be staged
if echo "$STAGED" | grep -q "zakops-api.json"; then
  if ! echo "$STAGED" | grep -q "api-types.generated.ts"; then
    echo "⚠️  PRE-COMMIT: zakops-api.json changed but api-types.generated.ts not staged"
    echo "   Did you forget to run: make sync-types?"
  fi
  if ! echo "$STAGED" | grep -q "backend_models.py"; then
    echo "⚠️  PRE-COMMIT: zakops-api.json changed but backend_models.py not staged"
    echo "   Did you forget to run: make sync-backend-models?"
  fi
fi

if echo "$STAGED" | grep -q "agent-api.json"; then
  if ! echo "$STAGED" | grep -q "agent-api-types.generated.ts"; then
    echo "⚠️  PRE-COMMIT: agent-api.json changed but agent-api-types.generated.ts not staged"
    echo "   Did you forget to run: make sync-agent-types?"
  fi
fi
```

```
GATE 6: Pre-commit hook catches direct generated file imports.
        Pre-commit hook warns if spec changed without regenerating types.
        Hook works in both soft (dev) and hard (CI) modes.
```

---

## FIX 7 (P2): VERIFY AND FIX MAKEFILE PORTABILITY

**QA-HG-VERIFY-002 fixed the hardcoded /home/zaks path. Verify it's still clean.**

```bash
# Check for ANY remaining hardcoded paths in Makefile
grep -n "/home/zaks" Makefile 2>/dev/null
# → Must find ZERO matches

# Verify the Makefile uses portable path discovery
head -20 Makefile
# → Should use $(shell git rev-parse --show-toplevel) or $$(realpath ...)

# If any hardcoded paths remain, fix them
```

```
GATE 7: Zero hardcoded absolute paths in Makefile.
        All paths use $(MONOREPO_ROOT) or equivalent portable discovery.
```

---

## FIX 8 (P2): ENSURE spec-freshness-bot IS COMPREHENSIVE

**The spec-freshness-bot workflow should check ALL specs, not just the backend.**

```bash
# Read current spec-freshness-bot.yml
cat .github/workflows/spec-freshness-bot.yml

# Verify it checks:
# 1. Backend OpenAPI spec (zakops-api.json) vs live backend
# 2. Agent API spec (agent-api.json) vs live Agent API
# 3. SSE event schema (agent-events.schema.json) exists and is valid JSON
# 4. MCP tool schemas (tool-schemas.json) exists and is valid JSON
#
# If any checks are missing, add them.
```

```
GATE 8: spec-freshness-bot checks all 4 spec files.
        Bot workflow is valid YAML.
```

---

## FIX 9 (P2): UPDATE validate-enforcement.sh

**The V4 enforcement validator checks V4 mechanisms. Add Hybrid Guardrail checks.**

### Add These Checks to validate-enforcement.sh

```bash
# CHECK: CLAUDE.md references all 7 contract surfaces
SURFACES=$(grep -c "Surface [1-7]\|Contract Surface" .claude/CLAUDE.md 2>/dev/null || echo 0)
if [ "$SURFACES" -ge 7 ]; then
  echo "✅ CLAUDE.md documents all contract surfaces"
else
  echo "❌ CLAUDE.md only documents $SURFACES contract surfaces (need 7)"
  FAILURES=$((FAILURES+1))
fi

# CHECK: after-change.md command exists
if [ -f ".claude/commands/after-change.md" ]; then
  echo "✅ after-change.md command exists"
else
  echo "❌ after-change.md command missing"
  FAILURES=$((FAILURES+1))
fi

# CHECK: All sync Makefile targets exist
for target in sync-types sync-backend-models sync-agent-types sync-rag-models sync-all-types; do
  if grep -q "^$target:" Makefile 2>/dev/null; then
    echo "✅ make $target exists"
  else
    echo "❌ make $target MISSING"
    FAILURES=$((FAILURES+1))
  fi
done
```

```
GATE 9: validate-enforcement checks CLAUDE.md has all 7 surfaces.
        validate-enforcement checks after-change.md exists.
        validate-enforcement checks all sync targets exist.
```

---

## VERIFICATION SEQUENCE

```
Execute in this order:

1. Section 0: Discovery — understand current state
2. Fix 1: Rewrite CLAUDE.md — the complete system map
3. Fix 2: Create/update .claude/commands/ — all operations
4. Fix 3: Update manifest generator — cover all surfaces
5. Fix 4: Update validation — cover all surfaces
6. Fix 5: Update dependency graph — comprehensive
7. Fix 6: Update pre-commit hook — catch HG violations
8. Fix 7: Verify Makefile portability
9. Fix 8: Verify spec-freshness-bot coverage
10. Fix 9: Update enforcement validator

FINAL VERIFICATION:
  make infra-snapshot          → exit 0, manifest >250 lines
  make infra-check             → exit 0
  make validate-enforcement    → exit 0 (with new checks)
  make validate-local          → exit 0 (with contract surface checks)
  cat .claude/CLAUDE.md        → contains all 7 surfaces
  ls .claude/commands/         → ≥7 command files
  grep "/home/zaks" Makefile   → 0 matches
```

---

## AUTONOMY RULES

```
1. If something doesn't exist → create it.
2. If a script is incomplete → complete it.
3. If a path is wrong → fix it based on discovery.
4. If a Makefile target is missing → add it.
5. If the current CLAUDE.md is too short → rewrite it completely.
6. ADAPT to what discovery finds. Paths in this prompt are EXPECTED paths.
   If the actual filesystem differs, use the actual paths.
7. Don't remove V4 infrastructure — ADD to it.
8. If a check fails during verification → fix it before moving on.
9. Document any gaps you find that aren't covered by this mission.
10. The goal is: next time Claude Code starts a session, it reads CLAUDE.md
    and knows EVERYTHING about the system. Test this by reading it yourself
    and asking: "Would I know what to do after any change?"
```

---

## OUTPUT FORMAT

```markdown
# INFRA-AWARENESS-V5 COMPLETION REPORT

**Date:** [timestamp]
**Executor:** Claude Code [version]

## Results
| # | Fix | Status | Key Change |
|---|-----|--------|------------|
| 0 | Discovery | DONE | [summary of what was found] |
| 1 | CLAUDE.md rewrite | [PASS/FAIL] | [line count, sections] |
| 2 | .claude/commands/ | [PASS/FAIL] | [N command files created] |
| 3 | Manifest generator | [PASS/FAIL] | [new sections added] |
| 4 | Cross-layer validation | [PASS/FAIL] | [new checks added] |
| 5 | Dependency graph | [PASS/FAIL] | [comprehensive Y/N] |
| 6 | Pre-commit hook | [PASS/FAIL] | [new checks added] |
| 7 | Makefile portability | [PASS/FAIL] | [hardcoded paths: N] |
| 8 | spec-freshness-bot | [PASS/FAIL] | [specs covered: N] |
| 9 | validate-enforcement | [PASS/FAIL] | [new checks: N] |

## Final Verification
- make infra-snapshot: [exit code]
- make infra-check: [exit code]
- make validate-enforcement: [exit code]
- make validate-local: [exit code]
- CLAUDE.md line count: [N]
- Command files: [N]
- Hardcoded paths: [N]

## Before/After
| Metric | V4 (Before) | V5 (After) |
|--------|-------------|------------|
| CLAUDE.md line count | ~50 | [N] |
| Contract surfaces documented | 0 | 7 |
| .claude/commands/ files | 1 | [N] |
| Manifest sections | ~8 | [N] |
| Validation checks | ~5 | [N] |
| Pre-commit checks | ~2 | [N] |
| Enforcement checks | 7 | [N] |
```

---

## HARD RULES

```
1. CLAUDE.md IS THE SINGLE MOST IMPORTANT FILE IN THIS MISSION.
   If Claude Code reads it and still doesn't know what to do after a
   Backend API change, the mission has failed.

2. EVERYTHING ADAPTS TO DISCOVERY. Don't blindly copy paths from this prompt.
   Run Step 0, see what exists, then adapt.

3. DON'T REMOVE V4 INFRASTRUCTURE. Add to it. V4's manifest generator,
   validation scripts, hooks, and enforcement are the foundation.

4. ALL 7 CONTRACT SURFACES MUST BE DOCUMENTED. Not 6. Not "most of them." ALL 7.

5. THE DEPENDENCY GRAPH MUST BE ACTIONABLE. Not "check if things are aligned."
   Specific make targets for specific change scenarios.

6. COMMANDS MUST BE COPY-PASTEABLE. No "run the appropriate target."
   Specific commands for specific situations.

7. VALIDATE YOUR OWN WORK. After rewriting CLAUDE.md, read it as if you're
   a fresh Claude Code instance. Would you know what to do? If not, fix it.
```

---

*Generated: 2026-02-07*
*Purpose: Reset Claude Code's infrastructure awareness to cover ALL current systems*
*Foundation: INFRA-AWARENESS V4 (retained and extended)*
*New Coverage: 7 Hybrid Guardrail contract surfaces + all EXEC-001/002/QA additions*
*Target: Claude Code reads CLAUDE.md → knows everything → changes anything → auto-realigns*
