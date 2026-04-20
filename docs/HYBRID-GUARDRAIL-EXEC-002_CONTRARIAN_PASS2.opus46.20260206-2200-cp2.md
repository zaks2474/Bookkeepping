# HYBRID-GUARDRAIL-EXEC-002 — Contrarian Audit Pass 2

## AGENT IDENTITY

```
agent_name:    opus46
run_id:        20260206-2200-cp2
date_time:     2026-02-06T22:00:00Z
repo_revision: agent-api=b96b33c, backend=8546734, zaks-llm=56acbb9
pass:          2 of 3
target:        MISSION-HYBRID-GUARDRAIL-EXEC-002 (Full Stack Contract Coverage)
inputs:        PASS1 report + EXEC-001 artifacts + live codebase validation
```

---

## A) PATCH LIST (Surgical)

### PATCH-01: Agent API must have `export_openapi.py` (CI-safe spec generation)

- **Why:** KS-4 + D-3 — Agent API OpenAPI is behind `_enable_docs` feature flag (main.py:81). `curl localhost:8095/openapi.json` returns 404 in production mode. CI cannot depend on running services. RT-HARDEN-001 solved this exact problem for Backend via `scripts/export_openapi.py`.
- **Where:** Phase 2, Section 2.1 — REPLACE `curl` approach entirely
- **How:**
  ```python
  # Create: apps/agent-api/scripts/export_openapi.py
  #!/usr/bin/env python3
  """Generate OpenAPI spec from FastAPI app without starting server."""
  import json, sys
  sys.path.insert(0, ".")
  from app.main import app
  spec = app.openapi()
  print(json.dumps(spec, indent=2, sort_keys=True))
  ```
  ```makefile
  # Makefile target:
  update-agent-spec:
  	cd $(AGENT_API_ROOT) && uv run python scripts/export_openapi.py | jq -S . > \
  		$(MONOREPO_ROOT)/packages/contracts/openapi/agent-api.json
  ```
- **Proof:** `cd apps/agent-api && uv run python scripts/export_openapi.py | jq '.paths | keys | length'` → 18 (no network required)

---

### PATCH-02: Pin `datamodel-code-generator` version for deterministic output

- **Why:** KS-8 + D-2 — Different versions produce different field ordering, import style, annotation format. Unpinned `pip install` causes flaky drift detection.
- **Where:** Phase 1, Section 1.2 — ADD version constraint
- **How:**
  ```toml
  # In apps/agent-api/pyproject.toml [project.optional-dependencies]:
  codegen = ["datamodel-code-generator==0.26.3"]
  ```
  ```bash
  # CI step:
  uv sync --extra codegen
  # NOT: pip install datamodel-code-generator (unpinned)
  ```
- **Proof:** Run codegen twice → `diff backend_models_run1.py backend_models_run2.py` is empty. Pin version in lockfile via `uv.lock`.

---

### PATCH-03: Create behavioral migration map BEFORE refactoring deal_tools.py

- **Why:** KS-1 — 25 `.get(key, default)` fallbacks currently provide silent degradation. Replacing with typed attribute access changes error semantics from "return default" to "ValidationError/AttributeError". Every fallback is a behavioral regression risk.
- **Where:** Phase 1, INSERT new Section 1.3a between 1.3 (BackendClient) and 1.4 (Refactor)
- **How:**
  1. For each `.get()` call in deal_tools.py, query the backend OpenAPI schema:
     - Is the field REQUIRED in the schema? → safe to use typed access
     - Is the field OPTIONAL (nullable)? → generated model must have `Optional[T]` + caller must handle None
     - Does the field NOT EXIST in the schema? → response envelope differs from spec → STOP, investigate
  2. Create table: `| Line | .get() Call | Schema Field | Required? | Migration Strategy |`
  3. Commit map to evidence before touching any code
- **Proof:** `evidence/phase1-agent-backend-sdk/behavioral-migration-map.md` with all 25 entries classified. Zero "NOT EXIST" entries (if any exist, Phase 1 is blocked until spec is corrected).

---

### PATCH-04: Replace manual RAG models with codegen from RAG's own OpenAPI spec

- **Why:** KS-5 — EXEC-002 Phase 4 proposes hand-writing `rag_models.py` in the backend. This is the EXACT anti-pattern the Hybrid Guardrail exists to eliminate. RAG API is FastAPI with its own Pydantic models (`QueryRequest`, `AddContentRequest` at rag_rest_api.py:75-85). The correct pattern is: fetch RAG spec → commit → codegen → drift check.
- **Where:** Phase 4, REPLACE Sections 4.1-4.3 entirely
- **How:**
  1. Create `Zaks-llm/scripts/export_openapi.py`:
     ```python
     #!/usr/bin/env python3
     import json, sys
     sys.path.insert(0, "src")
     from api.rag_rest_api import app
     print(json.dumps(app.openapi(), indent=2, sort_keys=True))
     ```
  2. Commit spec: `packages/contracts/openapi/rag-api.json`
  3. Codegen: `datamodel-codegen --input rag-api.json --output src/schemas/rag_models.py`
  4. CI: `git diff --exit-code src/schemas/rag_models.py`
  5. Makefile: `sync-rag-models`, `update-rag-spec`, `check-rag-contract-drift`
- **Proof:** `diff <(cd Zaks-llm && python scripts/export_openapi.py | jq -S .) <(jq -S . packages/contracts/openapi/rag-api.json)` is empty.

---

### PATCH-05: Use JSON Schema contract for SSE event types (not OpenAPI)

- **Why:** KS-2 + D-4 + D-8 — OpenAPI has no standard for SSE event type enumeration. `openapi-typescript` generates response types, not event stream payloads. Phase 3's promise of "replace manual event types with generated" is technically impossible via OpenAPI alone. Must use an alternative contract format.
- **Where:** Phase 3, REPLACE Section 3.3 (SSE type generation)
- **How:**
  1. Agent API defines canonical event types as Python Enum:
     ```python
     # apps/agent-api/app/schemas/events.py
     class AgentEventType(str, Enum):
         RUN_STARTED = "agent.run_started"
         RUN_COMPLETED = "agent.run_completed"
         # ... all 21 types from agent-activity.ts
     ```
  2. Export to JSON Schema:
     ```python
     # scripts/export_event_schema.py
     from app.schemas.events import AgentEventType, AgentActivityEvent
     schema = AgentActivityEvent.model_json_schema()
     ```
  3. Commit: `packages/contracts/events/agent-events.schema.json`
  4. Codegen: `npx json-schema-to-typescript packages/contracts/events/agent-events.schema.json > apps/dashboard/src/lib/agent-event-types.generated.ts`
  5. CI: regenerate + `git diff --exit-code`
- **Proof:** Generated TS file contains `AgentEventType` union matching all 21 backend event strings. `tsc --noEmit` exits 0.

---

### PATCH-06: Resolve event type split-brain BEFORE Phase 3 codegen

- **Why:** KS-3 + D-14 — `agent-activity.ts` defines `agent.run_started` (dot-prefix). `execution-contracts.ts` defines `run_started` (no prefix). These are DIFFERENT string values for conceptually the same events. Without resolution, codegen produces a THIRD set of names.
- **Where:** Phase 3, INSERT new Section 3.0 (prerequisite)
- **How:**
  1. Determine canonical format from Agent API backend code (grep actual SSE event emission strings)
  2. Choose ONE file as the event type source:
     - **If dot-prefix is canonical** → `agent-activity.ts` types are correct, update `execution-contracts.ts`
     - **If no-prefix is canonical** → `execution-contracts.ts` types are correct, update `agent-activity.ts`
  3. Ensure unified types compile (`tsc --noEmit`)
  4. THEN proceed with codegen (which will replace the unified manual types)
- **Proof:** `grep -rn "EventType" apps/dashboard/src/types/ | sort` shows ONE definition point (not two). Dashboard builds clean.

---

### PATCH-07: Portable container discovery for migration assertions

- **Why:** KS-6 — EXEC-002 hardcodes `docker exec rag-db psql` and `docker exec zakops-agent-db psql`. RT-HARDEN-001 RT1 specifically eliminated hardcoded paths. Reintroducing them violates the portability contract.
- **Where:** Phase 5, Section 5.3 — REPLACE hardcoded container names
- **How:**
  ```bash
  # Use docker compose service names, not container names:
  check_crawlrag() {
    cd "$ZAKS_LLM_ROOT" && docker compose exec -T rag-db \
      psql -U postgres -d crawlrag -t -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
  }
  check_agent_db() {
    cd "$AGENT_API_ROOT" && docker compose exec -T db \
      psql -U postgres -d zakops_agent -t -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
  }
  ```
  Where `ZAKS_LLM_ROOT` and `AGENT_API_ROOT` are discovered via `discover-topology.sh` or `git rev-parse`.
- **Proof:** Script works from any directory. No hardcoded container names in `grep -r "docker exec [a-z]" tools/`.

---

### PATCH-08: Dump live crawlrag schema and diff BEFORE creating migration

- **Why:** KS-10 — `CREATE TABLE IF NOT EXISTS` is idempotent but `CREATE INDEX` may fail if indexes exist with different names. The proposed initial migration assumes the table DDL in code matches reality. If ad-hoc ALTERs have been run, migration is stale on day one.
- **Where:** Phase 5, Section 5.1 — INSERT prerequisite step
- **How:**
  ```bash
  # Step 0: Capture live schema
  docker compose -f $ZAKS_LLM_ROOT/docker-compose.yml exec -T rag-db \
    pg_dump -U postgres -d crawlrag --schema-only > \
    "$EVIDENCE_ROOT/evidence/phase5-database-migrations/crawlrag-live-schema.sql"

  # Step 1: Write proposed migration
  # Step 2: Diff live vs proposed
  diff crawlrag-live-schema.sql 001_initial_schema.sql > crawlrag-live-vs-proposed.diff
  # If diff is non-empty: adjust migration to match reality, NOT the other way around
  ```
- **Proof:** `evidence/phase5-database-migrations/crawlrag-live-vs-proposed.diff` exists and is reviewed. Migration matches live schema.

---

### PATCH-09: Canonicalize MCP server to ONE implementation

- **Why:** KS-7 + SF-15 — Three server files (`server.py`=12 tools, `server_http.py`=10, `server_sse.py`=10) means schemas added to one leave others unprotected. Changes to alternate servers bypass the contract.
- **Where:** Phase 6, INSERT new Section 6.0 (prerequisite)
- **How:**
  1. Determine which server is canonical:
     - `server.py` (537 lines, 12 tools, SSE) — largest tool set
     - `server_sse.py` (394 lines, 10 tools, v3.1.0) — latest version
     - `server_http.py` (419 lines, 10 tools, HTTP) — "CORRECT for LangSmith" comment
  2. Document decision in `mcp_server/README.md`
  3. Archive non-canonical to `mcp_server/archived/`
  4. Ensure all 12 tools exist in canonical server
  5. THEN add Pydantic schemas to the ONE canonical file
- **Proof:** `ls mcp_server/server*.py | wc -l` returns 1. `grep -c "@mcp.tool" mcp_server/server.py` returns 12.

---

### PATCH-10: Split `validate-all` into `validate-local` and `validate-live`

- **Why:** KS-9 — With 6+ contract surfaces, `validate-all` requires ALL services healthy simultaneously. Probability of success drops with each added dependency. CI must not depend on live services.
- **Where:** Phase 7, REPLACE Section 7.1
- **How:**
  ```makefile
  validate-local: sync-types sync-agent-types lint-dashboard  ## Gates that need NO running services
  	cd $(DASHBOARD_ROOT) && npx tsc --noEmit
  	@$(MAKE) check-redocly-debt
  	@echo "All local validations passed"

  validate-live: validate-local  ## Gates that need running services
  	@$(MAKE) check-contract-drift        # backend spec
  	@$(MAKE) check-agent-contract-drift   # agent spec
  	@$(MAKE) check-rag-contract-drift     # rag spec
  	@$(MAKE) check-migrations             # all 3 DBs
  	@echo "All live validations passed"

  validate-all: validate-live  ## Everything (backwards compat)
  ```
  CI uses `validate-local` only. Developer runs `validate-live` when services are up.
- **Proof:** `make validate-local` exits 0 with zero running services. CI workflow calls `validate-local`.

---

### PATCH-11: Remove `|| true` from ALL CI gates

- **Why:** D-12 — Phase 7.1 includes `npx @redocly/cli lint ... || true` for RAG spec. This is a silent-pass gate. RT-HARDEN-001 Hard Rule #3: "CI GATES MUST BLOCK. No `|| true`."
- **Where:** Phase 7, Section 7.1 — line `npx @redocly/cli lint packages/contracts/openapi/rag-api.json || true`
- **How:** Either:
  - (A) Lint RAG spec properly with `.redocly.yaml` ignore file (add debt-ledger entry)
  - (B) Exclude RAG spec from Redocly lint entirely (with justification: "RAG is external service, spec is auto-generated")
  - NEVER `|| true`
- **Proof:** `grep -c "|| true" .github/workflows/ci.yml` returns 0.

---

### PATCH-12: Add ESLint enforcement for agent-api bridge pattern

- **Why:** EXEC-001 P6 pattern — ESLint `no-restricted-imports` blocks direct imports from generated files. Phase 3 creates `agent-api-types.generated.ts` but does NOT add ESLint enforcement. Without it, consumers can bypass the bridge.
- **Where:** Phase 3, INSERT new Section 3.3a
- **How:**
  ```json
  // Add to .eslintrc.json no-restricted-imports patterns:
  {
    "group": ["**/agent-api-types.generated*"],
    "message": "Import from '@/types/agent-api' instead of the generated file directly."
  }
  ```
- **Proof:** Add test import of `agent-api-types.generated` to a random file → `npm run lint` exits 1. Remove → exits 0.

---

### PATCH-13: Add `make sync-agent-types` Makefile target (EXEC-001 parity)

- **Why:** EXEC-001 uses `make sync-types` for Dashboard←Backend. Phase 3 needs the equivalent for Dashboard←Agent. The naming convention must match.
- **Where:** Phase 3, Section 3.4 — ADD Makefile target
- **How:**
  ```makefile
  sync-agent-types: ## Regenerate TypeScript types from committed Agent API spec
  	cd $(DASHBOARD_ROOT) && npx openapi-typescript \
  		../../packages/contracts/openapi/agent-api.json \
  		-o src/lib/agent-api-types.generated.ts
  ```
- **Proof:** `make sync-agent-types` exits 0. `git diff --exit-code apps/dashboard/src/lib/agent-api-types.generated.ts` is clean.

---

### PATCH-14: Fix Phase 2 endpoint count and add missing response_models

- **Why:** PASS1 found 18 endpoints (not 16) with 14/18 having response_model. The 4 missing ones produce incomplete spec.
- **Where:** Phase 2, Section 2.1
- **How:**
  1. Add `response_model` to the 4 missing endpoints:
     - `/invoke/stream` — streaming, use `Response(media_type="text/event-stream")` in spec description
     - `/chat/stream` — same
     - `DELETE /messages` — add response model
     - `DELETE /session/{id}` — add response model
  2. Update endpoint count in mission doc: 16 → 18
- **Proof:** `jq '.paths | to_entries | length' packages/contracts/openapi/agent-api.json` returns path count. All non-streaming endpoints have response schemas.

---

### PATCH-15: Extend spec-freshness-bot to cover Agent API

- **Why:** D-11 — RT-HARDEN-001 created `spec-freshness-bot.yml` but it only checks Backend spec. Agent API spec has no automated freshness check.
- **Where:** Phase 7, INSERT step in spec-freshness-bot.yml
- **How:**
  ```yaml
  - name: Check Agent API spec freshness
    run: |
      cd apps/agent-api && uv run python scripts/export_openapi.py | jq -S . > /tmp/live-agent.json
      jq -S . ../../packages/contracts/openapi/agent-api.json > /tmp/committed-agent.json
      diff /tmp/live-agent.json /tmp/committed-agent.json || echo "::warning::Agent API spec may be stale"
  ```
- **Proof:** Workflow includes both backend AND agent-api freshness checks.

---

### PATCH-16: Clarify `api.ts` vs `agent-api.ts` bridge scope

- **Why:** D-15 — `api.ts` already exports `AgentRunApiResponse` (from backend schema `AgentRunResponse`). The new `agent-api.ts` bridge is for types from the Agent API's OWN OpenAPI spec. These are different contracts (backend vs agent-api) but the naming overlap creates confusion.
- **Where:** Phase 3, Section 3.2 — ADD clarifying documentation
- **How:**
  1. `types/api.ts` = bridge for **Backend API** types (from `zakops-api.json`)
  2. `types/agent-api.ts` = bridge for **Agent API** types (from `agent-api.json`)
  3. `AgentRunApiResponse` in `api.ts` is the BACKEND's view of an agent run (returned by backend endpoint)
  4. `AgentInvokeResponse` in `agent-api.ts` is the AGENT API's response to an invocation
  5. Add header comments to both files documenting which spec they bridge
  6. Move agent-origin types OUT of `api.ts` if any exist (currently only `AgentRunApiResponse` which IS a backend schema — stays in `api.ts`)
- **Proof:** Each bridge file's header comment names its source spec. No type appears in both bridges.

---

### PATCH-17: Add migration runner for agent-api and crawlrag

- **Why:** D-10 — EXEC-002 creates migration FILES but no migration RUNNER. Backend has a runner (schema_migrations tracking). Agent-api and crawlrag have no mechanism to apply migrations.
- **Where:** Phase 5, INSERT new Section 5.2a
- **How:**
  ```bash
  # Create: apps/agent-api/scripts/run_migrations.sh
  #!/usr/bin/env bash
  set -euo pipefail
  MIGRATIONS_DIR="$(dirname "$0")/../migrations"
  DB_URL="${DATABASE_URL:?DATABASE_URL not set}"

  for f in $(ls "$MIGRATIONS_DIR"/*.sql | sort -V); do
    VERSION=$(basename "$f" .sql)
    APPLIED=$(psql "$DB_URL" -t -c "SELECT 1 FROM schema_migrations WHERE version='$VERSION'" 2>/dev/null || echo "")
    if [ -z "$APPLIED" ]; then
      echo "Applying $VERSION..."
      psql "$DB_URL" -f "$f"
    fi
  done
  ```
  Same pattern for crawlrag.
- **Proof:** `run_migrations.sh` is idempotent — running twice produces same DB state.

---

### PATCH-18: Phase ordering — make Phase 5 independent, not blocking

- **Why:** Phase 5 (database migrations) has no dependency on Phases 1-4 and can be executed in parallel. Phase 3 depends on Phase 2 (Agent API spec). Phases 4 and 6 are independent.
- **Where:** Phase structure diagram
- **How:** Reorder execution graph:
  ```
  Phase 0 (setup) → [all phases depend on this]

  PARALLEL TRACK A: Phase 1 → Phase 2 → Phase 3
  PARALLEL TRACK B: Phase 4
  PARALLEL TRACK C: Phase 5
  PARALLEL TRACK D: Phase 6

  Phase 7 (CI hardening) → [depends on all above]
  ```
- **Proof:** Updated phase diagram shows dependency arrows. No circular dependencies.

---

## B) HARDENED GATES (EXEC-001 Parity + Extensions)

### Per-Phase MUST-PASS Gates

#### Phase 0: Setup & Baseline
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G0.1 | EXEC-001 infrastructure works | `make sync-types && cd apps/dashboard && npx tsc --noEmit` | 0 |
| G0.2 | Evidence directories created | `ls -d $EVIDENCE_ROOT/evidence/phase{0..7}-*` | 0 |
| G0.3 | Baseline files captured | `wc -c $EVIDENCE_ROOT/evidence/phase0-baseline/*.{py,ts}` | >0 per file |

#### Phase 1: Agent → Backend SDK
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G1.1 | Codegen determinism | Run `datamodel-codegen` twice, diff | empty diff |
| G1.2 | backend_models.py exists | `python -c "from app.schemas.backend_models import DealResponse"` | 0 |
| G1.3 | Behavioral map complete | `wc -l evidence/phase1*/behavioral-migration-map.md` | ≥25 entries |
| G1.4 | BackendClient methods | `grep -c "async def" app/services/backend_client.py` | ≥5 |
| G1.5 | deal_tools.py refactored | `grep -c "response\.json()" app/core/langgraph/tools/deal_tools.py` | 0 |
| G1.6 | CI drift check | `git diff --exit-code app/schemas/backend_models.py` after regen | 0 |
| G1.7 | Agent tools functional | Run golden traces (if available) or smoke test | 0 |

#### Phase 2: Agent API OpenAPI Spec
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G2.1 | export script works offline | `cd apps/agent-api && uv run python scripts/export_openapi.py \| jq .` | valid JSON |
| G2.2 | Spec committed | `test -f packages/contracts/openapi/agent-api.json` | 0 |
| G2.3 | Endpoint count | `jq '.paths \| keys \| length' agent-api.json` | ≥18 |
| G2.4 | Redocly lint | `npx @redocly/cli lint packages/contracts/openapi/agent-api.json` | 0 (or documented ignores) |
| G2.5 | Makefile targets | `make update-agent-spec && make check-agent-contract-drift` | 0 |

#### Phase 3: Dashboard ← Agent Codegen
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G3.1 | Event type split-brain resolved | One canonical definition of agent event types | 1 file |
| G3.2 | agent-api-types.generated.ts exists | `wc -l apps/dashboard/src/lib/agent-api-types.generated.ts` | >100 |
| G3.3 | agent-api.ts bridge exists | `test -f apps/dashboard/src/types/agent-api.ts` | 0 |
| G3.4 | ESLint blocks direct imports | Add test import → `npm run lint` | 1 (fails) |
| G3.5 | SSE event types codegen'd | `test -f packages/contracts/events/agent-events.schema.json` | 0 |
| G3.6 | Dashboard builds | `npm run type-check && npm run build` | 0 |
| G3.7 | CI drift check | `git diff --exit-code agent-api-types.generated.ts` after regen | 0 |

#### Phase 4: Backend → RAG Contract
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G4.1 | RAG export script works | `cd Zaks-llm && python scripts/export_openapi.py \| jq .` | valid JSON |
| G4.2 | RAG spec committed | `test -f packages/contracts/openapi/rag-api.json` | 0 |
| G4.3 | rag_models.py codegen'd | `python -c "from src.schemas.rag_models import AddContentRequest"` | 0 |
| G4.4 | rag_reindex_deal.py uses typed models | `grep -c "RAGAddRequest" src/actions/executors/rag_reindex_deal.py` | ≥1 |
| G4.5 | Drift check | `git diff --exit-code src/schemas/rag_models.py` after regen | 0 |

#### Phase 5: Database Migration Governance
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G5.1 | Live schema dumped | `test -f evidence/phase5*/crawlrag-live-schema.sql` | 0 |
| G5.2 | crawlrag migration exists | `test -f Zaks-llm/db/migrations/001_initial_schema.sql` | 0 |
| G5.3 | Migration matches live | `diff` of live dump vs migration shows only tracking table delta | reviewed |
| G5.4 | zakops_agent tracking added | SQL for schema_migrations table exists | 0 |
| G5.5 | Migration runner exists | `test -x apps/agent-api/scripts/run_migrations.sh` | 0 |
| G5.6 | Assertion checks all 3 DBs | `bash migration-assertion.sh` | 0 |
| G5.7 | No hardcoded container names | `grep -c "docker exec [a-z]" tools/infra/migration-assertion.sh` | 0 |

#### Phase 6: MCP Contract
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G6.1 | One canonical server file | `ls mcp_server/server*.py \| grep -v archived \| wc -l` | 1 |
| G6.2 | Pydantic schemas exist | `grep -c "class.*BaseModel" mcp_server/tool_schemas.py` | ≥12 |
| G6.3 | MCP tools validate input | `grep -c "model_validate\|ValidationError" mcp_server/server.py` | ≥1 |
| G6.4 | Contract committed | `test -f packages/contracts/mcp/tool-schemas.json` | 0 |

#### Phase 7: CI Hardening
| Gate | Check | Command | Exit |
|------|-------|---------|------|
| G7.1 | No `\|\| true` in CI | `grep -c '\|\| true' .github/workflows/ci.yml` | 0 |
| G7.2 | validate-local works offline | `make validate-local` (no services) | 0 |
| G7.3 | All negative controls pass | NC-1 through NC-6 all detected | 6/6 |
| G7.4 | spec-freshness-bot covers agent | `grep -c "agent" .github/workflows/spec-freshness-bot.yml` | ≥1 |
| G7.5 | Debt ledger updated | All new ceilings documented | reviewed |

### Sabotage Tests (Negative Controls)

| # | Test | Sabotage | Expected Detection | Remediation |
|---|------|----------|-------------------|-------------|
| NC-1 | Agent→Backend model drift | `echo "SABOTAGE" >> app/schemas/backend_models.py` | `make sync-backend-models` regenerates, `git diff --exit-code` fails | Regen removes sabotage |
| NC-2 | Dashboard←Agent type drift | `echo "// SABOTAGE" >> src/lib/agent-api-types.generated.ts` | `make sync-agent-types` regenerates, `git diff --exit-code` fails | Regen removes sabotage |
| NC-3 | Direct generated-file import | Add `import { X } from '@/lib/agent-api-types.generated'` to test file | `npm run lint` exits 1 (ESLint `no-restricted-imports`) | Remove import |
| NC-4 | SSE event type drift | Add unknown event to JSON Schema → regen TS | Dashboard build catches: unhandled event type in switch | Fix schema or add handler |
| NC-5 | Migration version drift | `DELETE FROM schema_migrations WHERE version = '002_decision_ledger'` in agent DB | `bash migration-assertion.sh` detects drift, exits 1 | Re-apply migration |
| NC-6 | RAG model drift | Manually edit `rag_models.py` → `make check-rag-contract-drift` | Drift detected, exit 1 | Regen from spec |

---

## C) NON-NEGOTIABLE ALIGNMENT CHECKLIST (EXEC-001 Compatibility)

Before declaring EXEC-002 "done", the builder MUST satisfy ALL of the following:

### Spec Locations & Conventions
- [ ] Backend spec at `packages/contracts/openapi/zakops-api.json` (UNCHANGED from EXEC-001)
- [ ] Agent API spec at `packages/contracts/openapi/agent-api.json` (NEW, same directory convention)
- [ ] RAG API spec at `packages/contracts/openapi/rag-api.json` (NEW, same directory convention)
- [ ] MCP tool schema at `packages/contracts/mcp/tool-schemas.json` (NEW, contracts subdir)
- [ ] SSE event schema at `packages/contracts/events/agent-events.schema.json` (NEW, contracts subdir)
- [ ] All specs use `jq -S` canonical JSON formatting (deterministic diffs)

### Bridge Pattern (One Source-of-Truth File Per Contract Surface)
- [ ] `types/api.ts` = bridge for Backend API types (UNCHANGED)
- [ ] `types/agent-api.ts` = bridge for Agent API types (NEW, same pattern)
- [ ] Each bridge imports ONLY from its generated file
- [ ] Each bridge is the ONLY file importing from its generated file
- [ ] ESLint `no-restricted-imports` enforces BOTH bridge files

### CI Enforcement Model
- [ ] `type-sync` job validates ALL codegen drift (backend + agent + RAG)
- [ ] No `|| true` in any CI gate
- [ ] No `continue-on-error: true` on any blocking step
- [ ] All new ceilings/baselines tracked in `docs/debt-ledger.md`
- [ ] `spec-freshness-bot.yml` covers ALL committed specs
- [ ] Negative controls prove all new gates catch violations

### `make sync-*` Discipline
- [ ] `make sync-types` — Dashboard←Backend types (EXISTING)
- [ ] `make sync-agent-types` — Dashboard←Agent API types (NEW)
- [ ] `make sync-backend-models` — Agent API←Backend models (NEW, Python)
- [ ] `make sync-rag-models` — Backend←RAG models (NEW, Python)
- [ ] `make sync-all` — runs ALL sync targets (NEW)
- [ ] `make update-spec` — fetch Backend spec (EXISTING)
- [ ] `make update-agent-spec` — fetch Agent API spec (NEW)
- [ ] `make update-rag-spec` — fetch RAG spec (NEW)
- [ ] `make validate-local` — all offline gates (NEW)
- [ ] `make validate-live` — all online gates (NEW)
- [ ] `make validate-all` — everything (EXISTING, updated)

### Portability (RT-HARDEN-001 Parity)
- [ ] ALL Makefile paths use `$(MONOREPO_ROOT)` or `$(shell git rev-parse ...)` — ZERO hardcoded absolute paths
- [ ] ALL spec export scripts use Python import (not `curl localhost`) — works in CI without running services
- [ ] ALL version-dependent tools pinned in lockfiles (datamodel-code-generator, openapi-typescript)
- [ ] ALL migration assertions use `docker compose exec` (service names), NOT `docker exec` (container names)

### Debt Governance
- [ ] Every new ceiling has: current count, justification, owner, target reduction date
- [ ] `docs/debt-ledger.md` updated with sections for: Agent API Redocly ignores, RAG spec issues, MCP schema gaps
- [ ] Manual types remaining: tracked with `MANUAL_TYPE_DEBT` comments + ceiling in CI

---

## D) PATCHED MISSION PROMPT DRAFT (V2)

**See companion file:** `MISSION-HYBRID-GUARDRAIL-EXEC-002_PATCHED_V2.opus46.20260206-2200-cp2.md`

Key changes in the patched version:
1. **[CHANGED] Phase 1:** Added behavioral migration map prerequisite, pinned codegen version
2. **[CHANGED] Phase 2:** Replaced `curl` with `export_openapi.py`, fixed endpoint count 16→18
3. **[CHANGED] Phase 3:** Added split-brain resolution prerequisite, SSE event JSON Schema contract, ESLint enforcement, `make sync-agent-types`
4. **[CHANGED] Phase 4:** Replaced manual RAG models with codegen from RAG spec
5. **[CHANGED] Phase 5:** Added live schema dump, portable container discovery, migration runner
6. **[CHANGED] Phase 6:** Added MCP server canonicalization prerequisite
7. **[CHANGED] Phase 7:** Split validate-all into local/live, removed `|| true`, added agent spec-freshness, added 6 negative controls
8. **[ADDED] Dependency graph:** Parallel execution tracks for independent phases
9. **[ADDED] Non-negotiable checklist:** EXEC-001 alignment verification

---

*Generated: 2026-02-06T22:00:00Z*
*Pass 2 of 3 — Contrarian Audit Pipeline*
*Next: Pass 3 (synthesis + final recommendations)*
