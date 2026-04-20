# MISSION: HYBRID GUARDRAIL PHASE 2 — FULL STACK CONTRACT COVERAGE
## Codename: `HYBRID-GUARDRAIL-EXEC-002`
## Version: V2-PATCHED | Date: 2026-02-06 | Patcher: PASS2 Contrarian Audit
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Extend compiler-enforced alignment to ALL contract surfaces
## Prerequisite: HYBRID-GUARDRAIL-EXEC-001 COMPLETE (Dashboard <-> Backend covered)

```
+==============================================================================+
|                                                                              |
|   DIRECTIVE: COMPLETE THE WALL                                               |
|                                                                              |
|   HYBRID-GUARDRAIL-EXEC-001 built compiler-enforced type alignment for      |
|   ONE contract surface: Dashboard <-> Backend.                               |
|                                                                              |
|   The system has 6 MORE contract surfaces with ZERO codegen coverage:       |
|                                                                              |
|   1. Agent API -> Backend API (HTTP calls with untyped response parsing)    |
|   2. Dashboard <- Agent API (SSE events with manual type definitions)       |
|   3. Agent API OpenAPI (18 endpoints with NO committed spec)     [CHANGED]  |
|   4. Backend -> RAG REST (plain dict requests, no validation)               |
|   5. MCP Server (12 tools with docstrings only, no formal contract)         |
|   6. Database Migrations (crawlrag has ZERO, zakops_agent has no tracking)  |
|                                                                              |
|   The agent brain -- the most fragile, highest-risk component -- is the     |
|   LEAST protected by compile-time gates.                                    |
|                                                                              |
|   This mission extends the Hybrid Guardrail pattern to ALL surfaces.        |
|   When complete, every inter-service contract will have:                    |
|   - An OpenAPI/JSON Schema specification                                    |
|   - Generated types (TypeScript and/or Python)                              |
|   - CI drift detection                                                      |
|   - Runtime validation                                                      |
|                                                                              |
+==============================================================================+
```

---

## CONTEXT

### What EXEC-001 Achieved (Foundation)

```
Backend (Pydantic) -> OpenAPI -> openapi-typescript -> api.ts bridge -> Dashboard
     ^                  ^              ^                  ^              ^
   83 paths         Committed      Generated          Single         13 consumers
   56 schemas       spec file      5,502 lines      source of        via bridge
                                                     truth
```

**Result:** Type changes in Backend -> automatic TypeScript updates -> compile-time errors if Dashboard breaks

### [ADDED] EXEC-001 Architectural Patterns (MUST REPLICATE)

| # | Pattern | How EXEC-001 Implements It | EXEC-002 Must Follow |
|---|---------|---------------------------|---------------------|
| P1 | Committed spec as truth | `packages/contracts/openapi/zakops-api.json` | Same directory for new specs |
| P2 | Codegen -> generated types | `openapi-typescript` -> `api-types.generated.ts` | Same tool for TS, `datamodel-codegen` for Python |
| P3 | Bridge file (single import) | `types/api.ts` re-exports from generated | One bridge per contract surface |
| P4 | CI drift detection | `git diff --exit-code` on generated files | Same pattern for all surfaces |
| P5 | `make sync-*` pipeline | `make sync-types` (committed spec -> codegen) | `make sync-agent-types`, `sync-backend-models`, `sync-rag-models` |
| P6 | ESLint import enforcement | `no-restricted-imports` blocks generated-file bypass | Add rule for EACH generated file |
| P7 | Debt ceiling (can only decrease) | Tracked in `docs/debt-ledger.md` with expiry | Same for all new ceilings |
| P8 | Negative controls | Sabotage -> detect -> revert | Prove EVERY new gate catches violations |
| P9 | Portable Makefile | `MONOREPO_ROOT=$(git rev-parse --show-toplevel)` | Zero hardcoded paths |
| P10 | Offline spec generation | `scripts/export_openapi.py` (Python import, no curl) | Same pattern for Agent API + RAG |

### What EXEC-002 Must Achieve (Complete Coverage)

```
+-----------------------------------------------------------------------------+
|                           FULL STACK COVERAGE                               |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +----------+         +-----------+         +----------+                    |
|  |Dashboard |<------->|Agent Brain|<------->| Backend  |                    |
|  | :3003    |  SSE    |   :8095   |  HTTP   |  :8091   |                    |
|  +----+-----+ PHASE 3 +-----+-----+ PHASE 1 +----+-----+                   |
|       |                     |                     |                         |
|       | DONE                |                     |                         |
|       | (EXEC-001)          |                     +---> RAG REST :8052      |
|       |                     |                     |    PHASE 4              |
|       |                     |                     |                         |
|       |                     +---> zakops_agent    +---> MCP Server :9100    |
|       |                     |    PHASE 5               PHASE 6             |
|       |                     |                     |                         |
|       +---------------------+---------------------+---> crawlrag DB        |
|                                                         PHASE 5            |
|                                                                             |
|  Legend:                                                                    |
|  ---> = Contract surface requiring codegen                                 |
|  DONE = Covered by EXEC-001                                                |
|                                                                             |
+-----------------------------------------------------------------------------+
```

### [ADDED] Dependency Graph (Execution Order)

```
Phase 0 (setup) -----> ALL phases depend on this

TRACK A (sequential): Phase 1 -> Phase 2 -> Phase 3
TRACK B (independent): Phase 4
TRACK C (independent): Phase 5
TRACK D (independent): Phase 6

Phase 7 (CI hardening) -----> depends on ALL above
```

Phases 4, 5, 6 are independent of each other and of Track A. They CAN be
parallelized but MUST all complete before Phase 7.

---

## [ADDED] CRITICAL RULES FROM CONTRARIAN AUDIT

```
CR-1: NO curl-based spec fetching in CI. Use export_openapi.py (Python import).
CR-2: NO unpinned codegen tools. Pin in pyproject.toml/package.json lockfiles.
CR-3: NO manual Pydantic models when the source service has OpenAPI. Codegen or block.
CR-4: NO || true in CI gates. Either lint properly or exclude with debt-ledger entry.
CR-5: NO hardcoded container names. Use docker compose service names.
CR-6: NO generated-file imports without ESLint enforcement.
CR-7: NO behavioral changes without a migration map (document .get() -> typed access).
CR-8: NO SSE type generation from OpenAPI. Use JSON Schema + json-schema-to-typescript.
CR-9: NO multiple server implementations for the same protocol. Canonicalize first.
CR-10: validate-all must work without running services (split local/live).
```

---

## AUDIT FINDINGS (Pre-Mission Research)

### Contract Surface 1: Agent API -> Backend HTTP Calls
**Location:** `apps/agent-api/app/core/langgraph/tools/deal_tools.py` (1,173 lines)
**Risk Level:** CRITICAL

| Pattern | Count | Lines |
|---------|-------|-------|
| `response.json()` (untyped) | 8 | 238, 323, 484, 568, 623, 791, 889, 1134 |
| `.get()` dict fallbacks | 25 | 239-240, 324-325, 488, 496, 571-572, 627, 635-639, 792, 803, 893, 899, 979-986, 1001, 1048, 1054, 1068, 1076 |
| Manual header construction | 1 | 53-62 (`_get_backend_headers()`) |
| Per-call `httpx.AsyncClient()` | 8 | One per endpoint call |

[CHANGED] **Updated from EXEC-002 V1:** Exact counts verified against live codebase.

### Contract Surface 2: Dashboard <- Agent API (SSE Events)
**Location:** `apps/dashboard/src/types/agent-activity.ts` (126 lines) + `execution-contracts.ts` (585 lines)
**Risk Level:** MEDIUM

[CHANGED] **Split-Brain Alert (from PASS1):**
- `agent-activity.ts` defines `AgentEventType` with **21 dot-prefixed** strings: `agent.run_started`, etc.
- `execution-contracts.ts` defines `AgentRunEventType`+`AgentToolEventType`+`AgentStreamEventType` with **15 non-prefixed** strings: `run_started`, etc.
- These are DIFFERENT values for conceptually similar events. MUST be resolved before codegen.
- `mapEventType()` does NOT exist (PASS1 KS — EXEC-002 V1 referenced non-existent function).

### Contract Surface 3: Agent API OpenAPI Spec
**Location:** `apps/agent-api/app/main.py` (227 lines)
**Risk Level:** CRITICAL

[CHANGED] **Updated facts (from PASS1):**
- OpenAPI IS auto-generated by FastAPI but **gated behind `_enable_docs`** (line 81)
- `_enable_docs = ENVIRONMENT == "development" OR ENABLE_API_DOCS == "true"`
- **Actual endpoint count: 18** (not 16): agent.py=8, chatbot.py=4, auth.py=6
- **14/18 have response_model** (missing: /invoke/stream, /chat/stream, DELETE /messages, DELETE /session/{id})
- Duplicate routing: `/v1/agent/*` AND `/agent/*` (line 162) — spec shows both

### Contract Surface 4: Backend -> RAG REST
**Location:** `src/actions/executors/rag_reindex_deal.py` (313 lines)
**Risk Level:** MEDIUM

[CHANGED] **Critical update:** RAG API (`Zaks-llm/src/api/rag_rest_api.py`) is **already FastAPI with Pydantic models**:
- `QueryRequest(BaseModel)`: query, source, match_count
- `AddContentRequest(BaseModel)`: url, content, metadata, chunk_size
- 6 endpoints, automatic OpenAPI generation

**Correct approach:** Fetch RAG's OWN OpenAPI spec -> codegen -> drift check.
**WRONG approach (V1):** Hand-write duplicate Pydantic models in backend.

### Contract Surface 5: Database Migrations
**Risk Level:** CRITICAL for crawlrag, MEDIUM for zakops_agent

[CHANGED] **Updated facts:**
- Backend (`zakops`): **24 migration files** (not 12 — numbering skips), latest `024_correlation_id.sql`
- Agent (`zakops_agent`): 2 files, NO `schema_migrations` table
- RAG (`crawlrag`): ZERO migrations, inline DDL in `rag_rest_api.py` (line 89-97)
- [ADDED] **crawlrag DB is external** — managed by `crawl4ai-rag` repo, accessed via `rag-backend` Docker network

### Contract Surface 6: MCP Server
**Location:** `mcp_server/server.py` (537 lines)
**Risk Level:** LOW

[CHANGED] **Critical update:** THREE MCP server implementations exist:
| File | Lines | Tools | Transport | Notes |
|------|-------|-------|-----------|-------|
| `server.py` | 537 | 12 | SSE (deprecated comment) | Primary |
| `server_http.py` | 419 | 10 | HTTP streamable | "CORRECT for LangSmith" |
| `server_sse.py` | 394 | 10 | SSE (uvicorn) | Latest v3.1.0 |

Must canonicalize to ONE before adding schemas.

---

## PHASE STRUCTURE

[CHANGED] Updated with dependency graph and prerequisites.

```
+-----------------------------------------------------------------------------+
|  PHASE 0: SETUP & BASELINE                                                 |
|  - Verify EXEC-001 infrastructure still works                              |
|  - Create evidence directories                                             |
|  - Baseline all current contract surfaces                                  |
+------|----------------------------------------------------------------------+
       v
+-----------------------------------------------------------------------------+
|  TRACK A (Sequential — each depends on previous)                            |
+-----------------------------------------------------------------------------+
|  PHASE 1: AGENT -> BACKEND SDK (P0 -- Highest Risk)                        |
|  [CHANGED] + Behavioral migration map before refactoring                   |
|  [CHANGED] + Pinned datamodel-code-generator version                       |
|  - Generate Python client from Backend OpenAPI spec                        |
|  - Replace raw httpx calls in deal_tools.py with typed SDK                 |
|  - Add response validation to all agent tools                              |
|  - Wire into agent-api CI                                                  |
+------|----------------------------------------------------------------------+
       v
|  PHASE 2: AGENT API OPENAPI SPEC (P0 -- Foundation for Phase 3)           |
|  [CHANGED] + export_openapi.py (no curl, no running service)              |
|  [CHANGED] + Fix 4 missing response_models                                |
|  [CHANGED] + Endpoint count corrected to 18                               |
|  - Export spec via Python import -> commit to contracts                    |
|  - Add spec validation to CI                                               |
+------|----------------------------------------------------------------------+
       v
|  PHASE 3: DASHBOARD <- AGENT CODEGEN (P1 -- Depends on Phase 2)           |
|  [ADDED] + Resolve event type split-brain FIRST                           |
|  [ADDED] + JSON Schema contract for SSE events                            |
|  [ADDED] + ESLint enforcement for agent bridge                            |
|  [ADDED] + make sync-agent-types target                                   |
|  - Generate TypeScript types from Agent OpenAPI                            |
|  - Create agent-api.ts bridge file                                         |
|  - Add drift detection to CI                                               |
+-----------------------------------------------------------------------------+

+-----------------------------------------------------------------------------+
|  TRACK B (Independent — can run parallel with A, C, D)                     |
+-----------------------------------------------------------------------------+
|  PHASE 4: BACKEND -> RAG CONTRACT (P1 -- Medium Risk)                      |
|  [CHANGED] + Codegen from RAG's own OpenAPI (not manual models)           |
|  [CHANGED] + RAG export_openapi.py (same pattern as backend)              |
|  - Commit RAG spec to contracts directory                                  |
|  - Generate Pydantic models from RAG spec                                  |
|  - Add drift check                                                         |
+-----------------------------------------------------------------------------+

+-----------------------------------------------------------------------------+
|  TRACK C (Independent)                                                      |
+-----------------------------------------------------------------------------+
|  PHASE 5: DATABASE MIGRATION GOVERNANCE (P1 -- Critical for crawlrag)      |
|  [ADDED] + Dump live schema and diff before creating migration            |
|  [CHANGED] + Portable container discovery (no hardcoded names)            |
|  [ADDED] + Migration runner scripts                                       |
|  - Create migration infrastructure for crawlrag                            |
|  - Add version tracking to zakops_agent                                    |
|  - Update assertion scripts to cover all 3 databases                       |
+-----------------------------------------------------------------------------+

+-----------------------------------------------------------------------------+
|  TRACK D (Independent)                                                      |
+-----------------------------------------------------------------------------+
|  PHASE 6: MCP CONTRACT FORMALIZATION (P2 -- Lower Risk)                    |
|  [ADDED] + Canonicalize to ONE server implementation first                |
|  - Generate JSON Schema for MCP tools                                      |
|  - Add tool input/output validation                                        |
|  - Document in contracts directory                                         |
+-----------------------------------------------------------------------------+

+-----------------------------------------------------------------------------+
|  PHASE 7: CI INTEGRATION & HARDENING (depends on ALL above)               |
|  [CHANGED] + Split validate-all into validate-local / validate-live       |
|  [CHANGED] + Remove all || true gates                                     |
|  [ADDED] + 6 negative controls (sabotage tests)                          |
|  [ADDED] + Extend spec-freshness-bot for agent-api                       |
|  - Wire all new gates into CI workflows                                    |
|  - Update documentation                                                    |
|  - Final verification                                                      |
+-----------------------------------------------------------------------------+
```

---

## PHASE 0: SETUP & BASELINE

### 0.1 Verify EXEC-001 Infrastructure

```bash
# Verify existing Hybrid Guardrail still works
cd $(git -C /home/zaks/zakops-agent-api rev-parse --show-toplevel)
make sync-types
cd apps/dashboard && npx tsc --noEmit
make validate-all  # if services are running; validate-local otherwise

# All must exit 0. If not, fix before proceeding.
```

### 0.2 Create Evidence Structure

```bash
EVIDENCE_ROOT="/home/zaks/bookkeeping/qa-verifications/HYBRID-GUARDRAIL-EXEC-002"
mkdir -p "$EVIDENCE_ROOT/evidence"/{
  phase0-baseline,
  phase1-agent-backend-sdk,
  phase2-agent-openapi,
  phase3-dashboard-agent-codegen,
  phase4-backend-rag-contract,
  phase5-database-migrations,
  phase6-mcp-contract,
  phase7-ci-hardening,
  verification
}
```

### 0.3 Baseline Current State

```bash
MONOREPO=$(git -C /home/zaks/zakops-agent-api rev-parse --show-toplevel)
BACKEND_ROOT="/home/zaks/zakops-backend"
ZAKS_LLM_ROOT="/home/zaks/Zaks-llm"

# Capture current agent tool implementation
cp "$MONOREPO/apps/agent-api/app/core/langgraph/tools/deal_tools.py" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/deal_tools_before.py"

# Capture current dashboard agent types
cp "$MONOREPO/apps/dashboard/src/types/agent-activity.ts" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/agent-activity_before.ts"
cp "$MONOREPO/apps/dashboard/src/types/execution-contracts.ts" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/execution-contracts_before.ts"

# Capture current RAG client
cp "$BACKEND_ROOT/src/actions/executors/rag_reindex_deal.py" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/rag_reindex_deal_before.py"

# Capture MCP server state (all 3 files)
cp "$BACKEND_ROOT/mcp_server/server.py" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/mcp_server_before.py"
ls -la "$BACKEND_ROOT/mcp_server/server"*.py \
   > "$EVIDENCE_ROOT/evidence/phase0-baseline/mcp_server_files.txt"

# Count current untyped patterns
grep -c "\.get(" "$MONOREPO/apps/agent-api/app/core/langgraph/tools/deal_tools.py" \
  | tee "$EVIDENCE_ROOT/evidence/phase0-baseline/untyped_get_count.txt"
grep -c "response\.json()" "$MONOREPO/apps/agent-api/app/core/langgraph/tools/deal_tools.py" \
  | tee "$EVIDENCE_ROOT/evidence/phase0-baseline/untyped_json_count.txt"
```

```
GATE P0: EXEC-001 infrastructure verified working.
         Evidence directories created.
         Baseline files captured (including execution-contracts.ts + MCP server list).
```

---

## PHASE 1: AGENT -> BACKEND SDK (P0 -- Highest Risk)

### 1.1 Install and Pin Python Client Generator

[CHANGED] Pin version in project dependencies.

```bash
cd $MONOREPO/apps/agent-api

# Add to pyproject.toml optional dependencies:
# [project.optional-dependencies]
# codegen = ["datamodel-code-generator==0.26.3"]

uv sync --extra codegen

# Verify determinism: run twice, diff output
uv run datamodel-codegen \
  --input ../../packages/contracts/openapi/zakops-api.json \
  --output /tmp/backend_models_run1.py \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated --field-constraints --use-double-quotes \
  --target-python-version 3.12

uv run datamodel-codegen \
  --input ../../packages/contracts/openapi/zakops-api.json \
  --output /tmp/backend_models_run2.py \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated --field-constraints --use-double-quotes \
  --target-python-version 3.12

diff /tmp/backend_models_run1.py /tmp/backend_models_run2.py
# MUST be empty. If not, investigate version-specific non-determinism.
```

### 1.2 Generate Backend Response Models

```bash
uv run datamodel-codegen \
  --input ../../packages/contracts/openapi/zakops-api.json \
  --output app/schemas/backend_models.py \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated --field-constraints --use-double-quotes \
  --target-python-version 3.12

# Verify generation
uv run python -c "from app.schemas.backend_models import DealResponse; print('OK')"
```

### [ADDED] 1.3a Create Behavioral Migration Map

**BEFORE refactoring deal_tools.py**, document every `.get()` fallback:

```bash
# Extract all .get() patterns with context
grep -n "\.get(" app/core/langgraph/tools/deal_tools.py \
  > "$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/get_patterns_raw.txt"
```

Create `$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/behavioral-migration-map.md`:

```markdown
# Behavioral Migration Map: deal_tools.py .get() -> Typed Access

| Line | .get() Call | Schema Field | Required in Schema? | Migration Strategy |
|------|-------------|--------------|--------------------|--------------------|
| 239 | `deal_data.get("stage", "unknown")` | DealResponse.stage | YES (required) | Safe: use `deal.stage` |
| 240 | `deal_data.get("status", "unknown")` | DealResponse.status | YES (required) | Safe: use `deal.status` |
| 488 | `deals.get("results", [])` | DealListResponse envelope | CHECK | May differ from schema — verify |
| ... | ... | ... | ... | ... |
```

**Rules:**
- **REQUIRED in schema** -> typed access is safe (`.stage` instead of `.get("stage", "unknown")`)
- **OPTIONAL/nullable in schema** -> generated model has `Optional[T]`, caller MUST handle `None`
- **NOT IN SCHEMA** -> STOP. Response envelope differs from spec. Fix spec or adjust client.

```
GATE 1.3a: behavioral-migration-map.md has entries for ALL 25 .get() calls.
           Zero "NOT IN SCHEMA" entries remaining (if any, fix spec first).
```

### 1.3 Create Typed Backend Client

```python
# Create: apps/agent-api/app/services/backend_client.py

"""
Typed Backend API Client

Generated models from Backend OpenAPI spec ensure compile-time type safety.
All responses are validated against Pydantic models before returning.
"""

from typing import Optional
import httpx
from pydantic import ValidationError

from app.schemas.backend_models import (
    DealResponse,
    TransitionRequest,
    TransitionResponse,
)
from app.core.config import settings

class BackendClientError(Exception):
    """Raised when backend returns unexpected response."""
    pass

class BackendClient:
    """Type-safe client for Backend API."""

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.DEAL_API_URL
        self.api_key = api_key or getattr(settings, 'ZAKOPS_API_KEY', '')

    def _headers(self, correlation_id: Optional[str] = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        return headers

    async def get_deal(self, deal_id: str, correlation_id: str = None) -> DealResponse:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/deals/{deal_id}",
                headers=self._headers(correlation_id),
            )
            response.raise_for_status()
            try:
                return DealResponse.model_validate(response.json())
            except ValidationError as e:
                raise BackendClientError(f"Invalid DealResponse: {e}")

    # Add methods for each endpoint called by deal_tools.py
    # Reference behavioral-migration-map.md for field handling
```

### 1.4 Refactor Agent Tools to Use Typed Client

Follow the behavioral migration map from 1.3a:

```python
# Update: apps/agent-api/app/core/langgraph/tools/deal_tools.py

# BEFORE (untyped):
deal_data = response.json()
actual_from_stage = deal_data.get("stage", "unknown")

# AFTER (typed, per migration map):
from app.services.backend_client import BackendClient, BackendClientError
_backend = BackendClient()

deal = await _backend.get_deal(deal_id, correlation_id)
actual_from_stage = deal.stage  # Required field per schema -> safe
```

### 1.5 Add Codegen to Agent API CI + Makefile

```yaml
# Add to ci.yml agent-api job:
      - name: Install codegen dependencies
        run: uv sync --extra codegen

      - name: Backend model drift check
        run: |
          uv run datamodel-codegen \
            --input ../../packages/contracts/openapi/zakops-api.json \
            --output app/schemas/backend_models.py \
            --input-file-type openapi \
            --output-model-type pydantic_v2.BaseModel \
            --use-annotated --field-constraints --use-double-quotes \
            --target-python-version 3.12
          if ! git diff --exit-code app/schemas/backend_models.py; then
            echo "::error::Backend models out of sync. Run 'make sync-backend-models'"
            exit 1
          fi
```

```makefile
# Add to Makefile:
AGENT_API_ROOT ?= $(MONOREPO_ROOT)/apps/agent-api

sync-backend-models: ## Generate Pydantic models from Backend OpenAPI
	cd $(AGENT_API_ROOT) && uv run datamodel-codegen \
		--input $(OPENAPI_SPEC) \
		--output app/schemas/backend_models.py \
		--input-file-type openapi \
		--output-model-type pydantic_v2.BaseModel \
		--use-annotated --field-constraints --use-double-quotes \
		--target-python-version 3.12
```

```
GATE P1: backend_models.py generated from Backend OpenAPI (pinned codegen version).
         Behavioral migration map complete (25/25 entries).
         BackendClient class with typed methods exists.
         deal_tools.py refactored — zero response.json() calls, zero .get() fallbacks.
         CI includes model generation + drift check.
         Codegen is deterministic (two runs produce identical output).
```

---

## PHASE 2: AGENT API OPENAPI SPEC (P0 -- Foundation for Phase 3)

### [CHANGED] 2.1 Create Offline Spec Export Script

**Do NOT use `curl localhost:8095`. Use Python import (same pattern as backend).**

```python
# Create: apps/agent-api/scripts/export_openapi.py
#!/usr/bin/env python3
"""Generate OpenAPI spec from FastAPI app without starting server.

Same pattern as backend's scripts/export_openapi.py.
Works in CI without running the Agent API service.
"""
import json
import sys

sys.path.insert(0, ".")
from app.main import app

spec = app.openapi()
print(json.dumps(spec, indent=2, sort_keys=True))
```

```bash
# Test: must work without network
cd $MONOREPO/apps/agent-api
uv run python scripts/export_openapi.py | jq '.paths | keys | length'
# Expected: 18 (or more)
```

### [CHANGED] 2.1a Fix Missing response_models

Before exporting spec, ensure all endpoints have proper response models:

```python
# Check for missing response_model:
# - /invoke/stream -> streaming, document as text/event-stream
# - /chat/stream -> streaming, document as text/event-stream
# - DELETE /messages -> add response_model
# - DELETE /session/{id} -> add response_model
```

### 2.2 Commit Spec and Validate

```bash
# Generate and commit
cd $MONOREPO/apps/agent-api
uv run python scripts/export_openapi.py | jq -S . > \
  ../../packages/contracts/openapi/agent-api.json

# Validate with Redocly
npx @redocly/cli lint packages/contracts/openapi/agent-api.json
# If errors: fix endpoint definitions, add .redocly.lint-ignore.yaml entries with
# debt-ledger documentation. NEVER use || true.
```

### 2.3 Create Makefile Targets

```makefile
update-agent-spec: ## Fetch Agent API spec via Python import (no running service)
	cd $(AGENT_API_ROOT) && uv run python scripts/export_openapi.py | jq -S . > \
		$(MONOREPO_ROOT)/packages/contracts/openapi/agent-api.json

check-agent-contract-drift: ## Verify committed agent spec matches code
	cd $(AGENT_API_ROOT) && uv run python scripts/export_openapi.py | jq -S . > /tmp/live-agent.json
	jq -S . $(MONOREPO_ROOT)/packages/contracts/openapi/agent-api.json > /tmp/committed-agent.json
	diff /tmp/live-agent.json /tmp/committed-agent.json && \
		echo "Agent API spec matches code" || \
		{ echo "Agent API spec drift detected"; exit 1; }
```

```
GATE P2: export_openapi.py works without network (Python import, no curl).
         Spec committed to packages/contracts/openapi/agent-api.json.
         Spec contains all 18 endpoints. [CHANGED: 16 -> 18]
         Redocly lint passes (or has documented ignores in debt-ledger.md).
         update-agent-spec and check-agent-contract-drift targets exist.
```

---

## PHASE 3: DASHBOARD <- AGENT CODEGEN (P1 -- Depends on Phase 2)

### [ADDED] 3.0 Resolve Event Type Split-Brain (PREREQUISITE)

**MUST complete before any codegen.**

```bash
# Identify canonical event type format from Agent API backend:
cd $MONOREPO/apps/agent-api
grep -rn "event_type\|EventType\|event\.type" app/ --include="*.py" \
  | tee "$EVIDENCE_ROOT/evidence/phase3-dashboard-agent-codegen/backend-event-formats.txt"

# Compare with dashboard definitions:
grep "agent\.\|run_\|tool_\|stream_" apps/dashboard/src/types/agent-activity.ts \
  > "$EVIDENCE_ROOT/evidence/phase3-dashboard-agent-codegen/frontend-event-formats.txt"
grep "run_\|tool_\|stream_" apps/dashboard/src/types/execution-contracts.ts \
  >> "$EVIDENCE_ROOT/evidence/phase3-dashboard-agent-codegen/frontend-event-formats.txt"
```

**Decision tree:**
1. If backend emits dot-prefixed events (`agent.run_started`): `agent-activity.ts` is correct
2. If backend emits non-prefixed events (`run_started`): `execution-contracts.ts` is correct
3. Unify into ONE canonical definition
4. Update the other file to re-export from the canonical source
5. Verify: `tsc --noEmit` exits 0

```
GATE 3.0: One canonical event type definition (not two).
          Dashboard builds clean after unification.
```

### 3.1 Generate TypeScript Types from Agent API

```bash
cd $MONOREPO/apps/dashboard
npx openapi-typescript ../../packages/contracts/openapi/agent-api.json \
  -o src/lib/agent-api-types.generated.ts
```

### 3.2 Create Agent API Bridge File

```typescript
// Create: apps/dashboard/src/types/agent-api.ts

/**
 * Agent API Type Bridge
 *
 * Single source of truth for Agent API types in the dashboard.
 * All agent-related types from the Agent API service flow through this file.
 *
 * SOURCE SPEC: packages/contracts/openapi/agent-api.json
 * GENERATED FROM: src/lib/agent-api-types.generated.ts
 *
 * NOTE: This file bridges the AGENT API (port 8095).
 * For BACKEND API (port 8091) types, use types/api.ts.
 */

import type { components } from '@/lib/agent-api-types.generated';

// =============================================================================
// GENERATED TYPE ALIASES
// =============================================================================

export type AgentInvokeRequest = components['schemas']['AgentInvokeRequest'];
export type AgentInvokeResponse = components['schemas']['AgentInvokeResponse'];
export type PendingApproval = components['schemas']['PendingApproval'];
// ... add all Agent API schemas
```

### [ADDED] 3.2a SSE Event Type Contract (JSON Schema)

**OpenAPI cannot describe SSE event type enumerations. Use JSON Schema instead.**

```python
# Agent API side: define event types as Python Enum + Pydantic model
# Create: apps/agent-api/app/schemas/events.py

from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AgentEventType(str, Enum):
    """Canonical event types emitted via SSE. Dashboard consumes these."""
    RUN_STARTED = "agent.run_started"
    RUN_COMPLETED = "agent.run_completed"
    RUN_FAILED = "agent.run_failed"
    TOOL_CALLED = "agent.tool_called"
    TOOL_COMPLETED = "agent.tool_completed"
    TOOL_FAILED = "agent.tool_failed"
    # ... all 21 types from agent-activity.ts

class AgentActivityEvent(BaseModel):
    """SSE event payload schema."""
    id: str
    type: AgentEventType
    label: str
    timestamp: datetime
    deal_id: Optional[str] = None
    deal_name: Optional[str] = None
    metadata: Dict[str, Any] = {}

# Export script: apps/agent-api/scripts/export_event_schema.py
```

```bash
# Generate JSON Schema from Pydantic
cd $MONOREPO/apps/agent-api
uv run python scripts/export_event_schema.py | jq -S . > \
  ../../packages/contracts/events/agent-events.schema.json

# Generate TypeScript from JSON Schema
cd $MONOREPO/apps/dashboard
npx json-schema-to-typescript ../../packages/contracts/events/agent-events.schema.json \
  -o src/lib/agent-event-types.generated.ts
```

### [ADDED] 3.3a Add ESLint Enforcement for Agent Bridge

```json
// Add to .eslintrc.json no-restricted-imports patterns:
{
  "group": ["**/agent-api-types.generated*"],
  "message": "Import from '@/types/agent-api' instead of the generated file directly."
},
{
  "group": ["**/agent-event-types.generated*"],
  "message": "Import from '@/types/agent-api' instead of the generated file directly."
}
```

### 3.3 Refactor Dashboard to Use Generated Types

```typescript
// Update agent-activity.ts to import from bridge (or generated event types)
// BEFORE: manual string literals
// AFTER: re-export from agent-api.ts bridge
```

### 3.4 Add Agent Type Sync to CI + Makefile

[ADDED] Makefile target:

```makefile
sync-agent-types: ## Regenerate TypeScript types from committed Agent API spec
	cd $(DASHBOARD_ROOT) && npx openapi-typescript \
		../../packages/contracts/openapi/agent-api.json \
		-o src/lib/agent-api-types.generated.ts
```

```yaml
# Add to ci.yml type-sync job:
      - name: Agent API codegen
        run: |
          npx openapi-typescript ../../packages/contracts/openapi/agent-api.json \
            -o src/lib/agent-api-types.generated.ts

      - name: Agent type drift check
        run: |
          if ! git diff --exit-code src/lib/agent-api-types.generated.ts; then
            echo "::error::Agent types out of sync. Run 'make sync-agent-types'"
            exit 1
          fi
```

```
GATE P3: Event type split-brain resolved (one canonical source). [ADDED]
         agent-api-types.generated.ts exists with Agent API schemas.
         agent-events.schema.json committed for SSE event contract. [ADDED]
         agent-api.ts bridge file created with spec-source header comment. [CHANGED]
         ESLint blocks direct imports from generated files. [ADDED]
         make sync-agent-types target works. [ADDED]
         Dashboard builds and type-checks.
         CI includes agent type drift check.
```

---

## PHASE 4: BACKEND -> RAG CONTRACT (P1 -- Medium Risk)

[CHANGED] **Entire approach changed: codegen from RAG's own OpenAPI, not manual models.**

### [CHANGED] 4.1 Create RAG Spec Export Script

```python
# Create: Zaks-llm/scripts/export_openapi.py
#!/usr/bin/env python3
"""Generate OpenAPI spec from RAG REST API without starting server."""
import json
import sys

sys.path.insert(0, "src")
from api.rag_rest_api import app

spec = app.openapi()
print(json.dumps(spec, indent=2, sort_keys=True))
```

```bash
# Test: must work without network (except database connection may be needed)
cd $ZAKS_LLM_ROOT
python scripts/export_openapi.py | jq '.paths | keys | length'
# Expected: 6
```

### [CHANGED] 4.2 Commit RAG Spec and Generate Backend Models

```bash
# Commit spec
cd $ZAKS_LLM_ROOT
python scripts/export_openapi.py | jq -S . > \
  $MONOREPO/packages/contracts/openapi/rag-api.json

# Generate backend models from RAG spec
cd $BACKEND_ROOT
uv run datamodel-codegen \
  --input $MONOREPO/packages/contracts/openapi/rag-api.json \
  --output src/schemas/rag_models.py \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated --field-constraints --use-double-quotes \
  --target-python-version 3.12

# Verify
uv run python -c "from src.schemas.rag_models import AddContentRequest; print('OK')"
```

### [CHANGED] 4.3 Refactor RAG Reindex to Use Generated Models

```python
# Update: src/actions/executors/rag_reindex_deal.py

# BEFORE: raw dict
resp = requests.post(_rag_api_url(), json={...})

# AFTER: generated model (from RAG's own spec)
from src.schemas.rag_models import AddContentRequest
request = AddContentRequest(url=url, content=content, metadata=metadata, chunk_size=5000)
resp = requests.post(_rag_api_url(), json=request.model_dump(), timeout=30)
```

### [CHANGED] 4.4 Makefile Targets

```makefile
update-rag-spec: ## Fetch RAG API spec via Python import
	cd $(ZAKS_LLM_ROOT) && python scripts/export_openapi.py | jq -S . > \
		$(MONOREPO_ROOT)/packages/contracts/openapi/rag-api.json

sync-rag-models: ## Generate Pydantic models from RAG OpenAPI
	cd $(BACKEND_ROOT) && uv run datamodel-codegen \
		--input $(MONOREPO_ROOT)/packages/contracts/openapi/rag-api.json \
		--output src/schemas/rag_models.py \
		--input-file-type openapi \
		--output-model-type pydantic_v2.BaseModel

check-rag-contract-drift: ## Verify committed RAG spec matches code
	cd $(ZAKS_LLM_ROOT) && python scripts/export_openapi.py | jq -S . > /tmp/live-rag.json
	jq -S . $(MONOREPO_ROOT)/packages/contracts/openapi/rag-api.json > /tmp/committed-rag.json
	diff /tmp/live-rag.json /tmp/committed-rag.json
```

```
GATE P4: RAG spec committed from RAG's own OpenAPI (not hand-written). [CHANGED]
         rag_models.py codegen'd from RAG spec (not manual Pydantic). [CHANGED]
         rag_reindex_deal.py uses generated models.
         Drift check works (spec matches live RAG code).
         Makefile targets: update-rag-spec, sync-rag-models, check-rag-contract-drift.
```

---

## PHASE 5: DATABASE MIGRATION GOVERNANCE (P1 -- Critical for crawlrag)

### [ADDED] 5.0 Dump Live Schemas (PREREQUISITE)

```bash
# Capture live crawlrag schema BEFORE creating any migrations
cd $ZAKS_LLM_ROOT
docker compose exec -T rag-db pg_dump -U postgres -d crawlrag --schema-only \
  > "$EVIDENCE_ROOT/evidence/phase5-database-migrations/crawlrag-live-schema.sql"

# Capture live zakops_agent schema
cd $MONOREPO/apps/agent-api
docker compose exec -T db pg_dump -U postgres -d zakops_agent --schema-only \
  > "$EVIDENCE_ROOT/evidence/phase5-database-migrations/zakops_agent-live-schema.sql"
```

### 5.1 Create crawlrag Migration Infrastructure

```bash
mkdir -p $ZAKS_LLM_ROOT/db/migrations
```

Create `001_initial_schema.sql` — but base it on the LIVE dump, not assumptions:

```bash
# Diff live schema against proposed migration
diff "$EVIDENCE_ROOT/evidence/phase5-database-migrations/crawlrag-live-schema.sql" \
     "$ZAKS_LLM_ROOT/db/migrations/001_initial_schema.sql" \
  > "$EVIDENCE_ROOT/evidence/phase5-database-migrations/crawlrag-live-vs-proposed.diff"

# Review: migration MUST match live schema (with schema_migrations addition only)
```

### 5.2 Add Version Tracking to zakops_agent

```sql
-- Create: apps/agent-api/migrations/003_add_migration_tracking.sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO schema_migrations (version) VALUES
    ('001_approvals'),
    ('002_decision_ledger'),
    ('003_add_migration_tracking')
ON CONFLICT (version) DO NOTHING;
```

### [ADDED] 5.2a Create Migration Runner Scripts

```bash
# Create: apps/agent-api/scripts/run_migrations.sh
#!/usr/bin/env bash
set -euo pipefail
MIGRATIONS_DIR="$(dirname "$0")/../migrations"
DB_URL="${DATABASE_URL:?DATABASE_URL not set}"

for f in $(ls "$MIGRATIONS_DIR"/*.sql | sort -V); do
  VERSION=$(basename "$f" .sql)
  APPLIED=$(psql "$DB_URL" -t -c \
    "SELECT 1 FROM schema_migrations WHERE version='$VERSION'" 2>/dev/null | tr -d ' ' || echo "")
  if [ -z "$APPLIED" ]; then
    echo "Applying $VERSION..."
    psql "$DB_URL" -f "$f"
  else
    echo "Skipping $VERSION (already applied)"
  fi
done
echo "All migrations applied."
```

Same pattern for `Zaks-llm/scripts/run_migrations.sh`.

### [CHANGED] 5.3 Update Assertion Scripts (Portable)

**NO hardcoded container names. Use `docker compose exec` with service names.**

```bash
# Use docker compose service names + project directories:
check_crawlrag_migrations() {
    echo "=== Checking crawlrag migrations ==="
    CRAWLRAG_MIGRATIONS="$ZAKS_LLM_ROOT/db/migrations"
    if [ ! -d "$CRAWLRAG_MIGRATIONS" ]; then
        echo "crawlrag migrations directory not found"
        return 1
    fi

    LATEST_FILE=$(ls -1 "$CRAWLRAG_MIGRATIONS"/*.sql 2>/dev/null | sort -V | tail -1)
    LATEST_VERSION=$(basename "$LATEST_FILE" .sql)

    # Use docker compose (service name), not docker exec (container name)
    APPLIED=$(cd "$ZAKS_LLM_ROOT" && docker compose exec -T rag-db \
        psql -U postgres -d crawlrag -t -c \
        "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1" 2>/dev/null | tr -d ' ')

    if [ "$LATEST_VERSION" = "$APPLIED" ]; then
        echo "crawlrag: $APPLIED (up to date)"
    else
        echo "crawlrag: file=$LATEST_VERSION, db=$APPLIED (DRIFT)"
        return 1
    fi
}
```

### 5.4 Update runtime.topology.json

[CHANGED] Use discovered paths, document external service:

```json
{
  "db_mapping": {
    "backend": {
      "expected_database": "zakops",
      "migrations_dir": "zakops-backend/db/migrations",
      "relative_to": "home_dir"
    },
    "agent-api": {
      "expected_database": "zakops_agent",
      "migrations_dir": "zakops-agent-api/apps/agent-api/migrations",
      "relative_to": "home_dir"
    },
    "rag-api": {
      "expected_database": "crawlrag",
      "migrations_dir": "Zaks-llm/db/migrations",
      "relative_to": "home_dir",
      "note": "External service in Zaks-llm repo, rag-backend Docker network"
    }
  }
}
```

```
GATE P5: Live schemas dumped and diffed against proposed migrations. [ADDED]
         crawlrag has migration infrastructure (001_initial_schema.sql).
         zakops_agent has version tracking (schema_migrations table).
         Migration runner scripts exist and are idempotent. [ADDED]
         migration-assertion.sh checks all 3 databases.
         NO hardcoded container names (uses docker compose service names). [CHANGED]
         runtime.topology.json includes all 3 databases.
```

---

## PHASE 6: MCP CONTRACT FORMALIZATION (P2 -- Lower Risk)

### [ADDED] 6.0 Canonicalize MCP Server (PREREQUISITE)

```bash
# Step 1: Identify canonical server
cd $BACKEND_ROOT/mcp_server
ls -la server*.py | tee "$EVIDENCE_ROOT/evidence/phase6-mcp-contract/server-files.txt"

# Step 2: Compare tool lists
grep "@mcp.tool" server.py | sort > /tmp/tools_main.txt
grep "@mcp.tool" server_http.py | sort > /tmp/tools_http.txt 2>/dev/null || true
grep "@mcp.tool" server_sse.py | sort > /tmp/tools_sse.txt 2>/dev/null || true

diff /tmp/tools_main.txt /tmp/tools_http.txt || true
diff /tmp/tools_main.txt /tmp/tools_sse.txt || true
```

**Decision:** Choose ONE canonical server. Archive others to `mcp_server/archived/`.
Document rationale in `mcp_server/README.md`.

```
GATE 6.0: One canonical server file. Others archived.
          Canonical has all 12 tools.
```

### 6.1 Generate JSON Schema for MCP Tools

Create `mcp_server/tool_schemas.py` with Pydantic models for all 12 tools.

### 6.2 Add Validation to Canonical MCP Server

Validate tool inputs against Pydantic schemas.

### 6.3 Document MCP Contract

```bash
# Export schemas
cd $BACKEND_ROOT
python -c "
from mcp_server.tool_schemas import export_tool_schemas
import json
print(json.dumps(export_tool_schemas(), indent=2, sort_keys=True))
" > $MONOREPO/packages/contracts/mcp/tool-schemas.json
```

```
GATE P6: One canonical server (others archived). [ADDED]
         tool_schemas.py with Pydantic models for all 12 MCP tools.
         MCP server validates inputs against schemas.
         tool-schemas.json committed to contracts directory.
```

---

## PHASE 7: CI INTEGRATION & HARDENING

### [CHANGED] 7.1 Update CI Workflow

```yaml
# Add to ci.yml:

  # Unified contract validation (runs on dashboard, agent-api, or contracts changes)
  contract-validation:
    needs: [changes]
    if: >
      needs.changes.outputs.contracts == 'true' ||
      needs.changes.outputs.agent-api == 'true' ||
      needs.changes.outputs.dashboard == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate all OpenAPI specs
        run: |
          npx @redocly/cli lint packages/contracts/openapi/zakops-api.json
          npx @redocly/cli lint packages/contracts/openapi/agent-api.json
          # RAG spec: lint OR exclude with debt-ledger entry. NEVER || true.

      - name: Codegen drift check (all surfaces)
        run: |
          # Dashboard <- Backend (existing)
          npx openapi-typescript packages/contracts/openapi/zakops-api.json \
            -o apps/dashboard/src/lib/api-types.generated.ts
          git diff --exit-code apps/dashboard/src/lib/api-types.generated.ts

          # Dashboard <- Agent API (new)
          npx openapi-typescript packages/contracts/openapi/agent-api.json \
            -o apps/dashboard/src/lib/agent-api-types.generated.ts
          git diff --exit-code apps/dashboard/src/lib/agent-api-types.generated.ts

          # Agent <- Backend (Python, new)
          cd apps/agent-api && uv sync --extra codegen
          uv run datamodel-codegen --input ../../packages/contracts/openapi/zakops-api.json \
            --output app/schemas/backend_models.py \
            --input-file-type openapi --output-model-type pydantic_v2.BaseModel \
            --use-annotated --field-constraints --use-double-quotes \
            --target-python-version 3.12
          git diff --exit-code app/schemas/backend_models.py
```

### [CHANGED] 7.1a Split validate-all

```makefile
# Offline gates (CI-safe, no running services):
validate-local: sync-types sync-agent-types lint-dashboard
	cd $(DASHBOARD_ROOT) && npx tsc --noEmit
	@$(MAKE) check-redocly-debt

# Online gates (need services):
validate-live: validate-local
	@$(MAKE) check-contract-drift
	@$(MAKE) check-agent-contract-drift
	@echo "Live validations passed"

# Full suite (backwards compatible):
validate-all: validate-live

# Sync everything:
sync-all: sync-types sync-agent-types sync-backend-models
```

### [ADDED] 7.1b Extend spec-freshness-bot

```yaml
# Add to spec-freshness-bot.yml:
      - name: Check Agent API spec freshness
        run: |
          cd apps/agent-api && uv run python scripts/export_openapi.py | jq -S . > /tmp/live-agent.json
          jq -S . ../../packages/contracts/openapi/agent-api.json > /tmp/committed-agent.json
          if ! diff /tmp/live-agent.json /tmp/committed-agent.json; then
            echo "::warning::Agent API spec may be stale. Run 'make update-agent-spec'."
          fi
```

### [CHANGED] 7.2 Negative Controls (6 sabotage tests)

```bash
# NC-1: Backend model drift (Agent <- Backend)
echo "SABOTAGE" >> apps/agent-api/app/schemas/backend_models.py
make sync-backend-models
git diff --exit-code apps/agent-api/app/schemas/backend_models.py || echo "NC-1 PASS: Codegen removes sabotage"
git checkout apps/agent-api/app/schemas/backend_models.py

# NC-2: Agent type drift (Dashboard <- Agent)
echo "// SABOTAGE" >> apps/dashboard/src/lib/agent-api-types.generated.ts
make sync-agent-types
git diff --exit-code apps/dashboard/src/lib/agent-api-types.generated.ts || echo "NC-2 PASS: Codegen removes sabotage"
git checkout apps/dashboard/src/lib/agent-api-types.generated.ts

# NC-3: Direct generated-file import
echo "import type { components } from '@/lib/agent-api-types.generated';" > /tmp/test_import.ts
# Add to a random component temporarily -> npm run lint should exit 1

# NC-4: SSE event type unknown
# Add unknown event to schema -> regen TS -> tsc should catch unhandled type

# NC-5: Migration drift
cd $MONOREPO/apps/agent-api
docker compose exec -T db psql -U postgres -d zakops_agent -c \
  "DELETE FROM schema_migrations WHERE version = '002_decision_ledger'"
bash /home/zaks/tools/infra/migration-assertion.sh || echo "NC-5 PASS: Drift detected"
# Restore:
docker compose exec -T db psql -U postgres -d zakops_agent -c \
  "INSERT INTO schema_migrations (version) VALUES ('002_decision_ledger')"

# NC-6: RAG model drift
echo "SABOTAGE" >> $BACKEND_ROOT/src/schemas/rag_models.py
make sync-rag-models
git diff --exit-code $BACKEND_ROOT/src/schemas/rag_models.py || echo "NC-6 PASS: Codegen removes sabotage"
git checkout $BACKEND_ROOT/src/schemas/rag_models.py
```

### 7.3 Update Documentation

- Update `docs/debt-ledger.md` with new ceilings (Agent API Redocly ignores, etc.)
- Update SERVICE-CATALOG.md with new contract surfaces
- Update RUNBOOKS.md with new sync commands
- Update CHANGES.md with mission completion
- [ADDED] Update `docs/debt-ledger.md` with MCP server consolidation decision

```
GATE P7: No || true in any CI gate. [CHANGED]
         validate-local works without running services. [ADDED]
         validate-live includes all contract drift checks.
         6 negative controls all PASS (sabotage detected + reverted). [CHANGED: was 3]
         spec-freshness-bot covers backend + agent-api. [ADDED]
         Documentation updated.
```

---

## [ADDED] NON-NEGOTIABLE ALIGNMENT CHECKLIST (EXEC-001 Compatibility)

Before declaring EXEC-002 complete, verify ALL of these:

### Spec Locations
- [ ] `packages/contracts/openapi/zakops-api.json` — Backend (UNCHANGED)
- [ ] `packages/contracts/openapi/agent-api.json` — Agent API (NEW)
- [ ] `packages/contracts/openapi/rag-api.json` — RAG API (NEW)
- [ ] `packages/contracts/mcp/tool-schemas.json` — MCP tools (NEW)
- [ ] `packages/contracts/events/agent-events.schema.json` — SSE events (NEW)
- [ ] All specs formatted with `jq -S` (canonical JSON)

### Bridge Files
- [ ] `types/api.ts` — Backend bridge (UNCHANGED, header comment names source spec)
- [ ] `types/agent-api.ts` — Agent API bridge (NEW, header comment names source spec)
- [ ] ESLint blocks both `api-types.generated` AND `agent-api-types.generated` direct imports

### CI Gates
- [ ] Zero `|| true` in `.github/workflows/ci.yml`
- [ ] Zero `continue-on-error: true` on blocking steps
- [ ] All ceilings in `docs/debt-ledger.md`
- [ ] `spec-freshness-bot.yml` covers ALL committed specs

### Makefile Targets
- [ ] `sync-types` (existing), `sync-agent-types` (new), `sync-backend-models` (new), `sync-rag-models` (new)
- [ ] `update-spec` (existing), `update-agent-spec` (new), `update-rag-spec` (new)
- [ ] `validate-local` (new, offline), `validate-live` (new, online), `validate-all` (updated)
- [ ] `sync-all` (new, runs all sync targets)

### Portability
- [ ] Zero hardcoded absolute paths in Makefile
- [ ] All spec exports use Python import (not `curl localhost`)
- [ ] All codegen tools pinned in lockfiles
- [ ] All migration assertions use `docker compose exec` (not `docker exec`)

---

## VERIFICATION SEQUENCE

```
Execute in this order. Do NOT skip steps.

1. PHASE 0 -- Setup & baseline
   +- Verify EXEC-001 works
   +- Create evidence dirs
   +- Capture baselines (including execution-contracts.ts + MCP file list)

2. PHASE 1 -- Agent -> Backend SDK (CRITICAL)
   +- Pin datamodel-code-generator version [ADDED]
   +- Generate backend_models.py
   +- Create behavioral migration map [ADDED]
   +- Create BackendClient
   +- Refactor deal_tools.py
   +- Verify: zero .get() fallbacks, codegen deterministic

3. PHASE 2 -- Agent API OpenAPI Spec (CRITICAL)
   +- Create export_openapi.py (no curl) [CHANGED]
   +- Fix 4 missing response_models [ADDED]
   +- Export spec, commit to contracts, validate with Redocly
   +- Verify: 18 endpoints documented

4. PHASE 3 -- Dashboard <- Agent Codegen
   +- Resolve event type split-brain [ADDED]
   +- Generate agent-api-types.generated.ts
   +- Create SSE event JSON Schema contract [ADDED]
   +- Create bridge, add ESLint enforcement [ADDED]
   +- Verify: npm run type-check exits 0

5. PHASE 4 -- Backend -> RAG Contract
   +- Create RAG export_openapi.py [CHANGED]
   +- Codegen rag_models.py from RAG spec [CHANGED]
   +- Refactor rag_reindex_deal.py
   +- Verify: RAG indexing still works

6. PHASE 5 -- Database Migration Governance
   +- Dump live schemas first [ADDED]
   +- Diff live vs proposed migrations [ADDED]
   +- Create migration runners [ADDED]
   +- Use portable container discovery [CHANGED]
   +- Verify: migration-assertion.sh passes for all 3 databases

7. PHASE 6 -- MCP Contract Formalization
   +- Canonicalize to ONE server [ADDED]
   +- Create tool_schemas.py, add validation, document
   +- Verify: MCP tools work with validation

8. PHASE 7 -- CI Integration & Hardening
   +- Wire all gates (NO || true) [CHANGED]
   +- Split validate-all into local/live [ADDED]
   +- Run 6 negative controls [CHANGED: was 3]
   +- Extend spec-freshness-bot [ADDED]
   +- Verify non-negotiable alignment checklist [ADDED]

9. FINAL VERIFICATION
   +- All phase gates pass
   +- Non-negotiable checklist 100% [ADDED]
   +- Evidence directories populated
   +- Zero untyped contract surfaces remaining
```

---

## SUCCESS CRITERIA

```
+-----------------------------------------------------------------------------+
|  BEFORE EXEC-002                           AFTER EXEC-002                   |
+-----------------------------------------------------------------------------+
|                                                                             |
|  Dashboard <-> Backend: TYPED              Dashboard <-> Backend: TYPED     |
|  Agent -> Backend: UNTYPED                 Agent -> Backend: TYPED          |
|  Dashboard <- Agent: MANUAL                Dashboard <- Agent: TYPED        |
|  Agent OpenAPI: NONE                       Agent OpenAPI: COMPLETE          |
|  Backend -> RAG: UNTYPED                   Backend -> RAG: TYPED            |
|  MCP Contract: DOCSTRINGS                  MCP Contract: JSON SCHEMA        |
|  crawlrag Migrations: NONE                 crawlrag Migrations: TRACKED     |
|  zakops_agent Tracking: NONE               zakops_agent Tracking: VERSIONED |
|                                                                             |
|  Contract surfaces with codegen: 1/7       Contract surfaces with codegen: 7/7
|  Compile-time type safety: 14%             Compile-time type safety: 100%  |
|  SSE event types: MANUAL                   SSE event types: JSON SCHEMA    |
|  Negative controls: 4                      Negative controls: 10 (4+6)     |
|  make sync targets: 1                      make sync targets: 5            |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## AUTONOMY RULES

```
1. If a Python package is not installed -> install it (uv add / uv sync --extra).
2. If a spec endpoint doesn't exist -> add it to the FastAPI app.
3. If a Pydantic model is missing -> create it.
4. If a migration doesn't exist -> create it (but dump live schema first).
5. If a CI job is missing -> add it (but NEVER || true).
6. If generated files don't exist -> run the generator.
7. If a test fails after refactoring -> fix the code, not the test.
8. If you discover additional untyped surfaces -> document and fix them.
9. "I should check with the user" is NOT a valid reason to stop.
10. Document blockers in DEFERRED.md and keep moving.
11. [ADDED] If a service has multiple implementations -> canonicalize to ONE first.
12. [ADDED] If curl-based spec fetch fails in CI -> use export_openapi.py (Python import).
13. [ADDED] If .get() fallbacks exist -> create behavioral migration map BEFORE removing.
```

---

## HARD RULES

```
1. EVERY INTER-SERVICE CALL MUST BE TYPED. No raw .json() -> dict patterns.
2. EVERY SERVICE MUST HAVE AN OPENAPI SPEC (or JSON Schema for non-REST). No undocumented endpoints.
3. EVERY DATABASE MUST HAVE MIGRATION TRACKING. No hardcoded schemas.
4. EVERY CODEGEN MUST BE IN CI. Drift = build failure.
5. NEGATIVE CONTROLS MUST PROVE GATES WORK. Sabotage -> detection -> revert.
6. THE AGENT BRAIN IS NO LONGER EXEMPT. It gets the same treatment as everything else.
7. MANUAL TYPES ARE DEBT. Track them, reduce them, eliminate them.
8. WHEN THIS MISSION COMPLETES, COMPILE-TIME TYPE SAFETY = 100%.
9. [ADDED] NO || true IN CI GATES. Either lint properly or exclude with justification.
10. [ADDED] NO HARDCODED PATHS. Use git rev-parse, docker compose service names.
11. [ADDED] NO MANUAL MODELS WHEN SOURCE HAS OPENAPI. Codegen or block.
12. [ADDED] NO CURL-BASED SPEC FETCH IN CI. Use export_openapi.py (Python import).
13. [ADDED] ALL CODEGEN TOOLS PINNED. Version in lockfile, deterministic output.
```

---

## [ADDED] CHANGE LOG (V1 -> V2)

| Section | Change | Reason (PASS1 Kill Shot / Missing Piece) |
|---------|--------|------------------------------------------|
| Overview | Endpoint count 16 -> 18 | PASS1 actual count verification |
| Phase structure | Added dependency graph with parallel tracks | Phases 4,5,6 are independent |
| Critical Rules | Added CR-1 through CR-10 | Contrarian audit constraints |
| Phase 0 | Added execution-contracts.ts + MCP file list to baseline | KS-3, KS-7 |
| Phase 1 | Pinned datamodel-code-generator version | KS-8 |
| Phase 1 | Added behavioral migration map (1.3a) | KS-1 |
| Phase 2 | Replaced curl with export_openapi.py | KS-4, D-3 |
| Phase 2 | Added fix for 4 missing response_models | PASS1 audit |
| Phase 3 | Added event type split-brain resolution (3.0) | KS-3, D-14 |
| Phase 3 | Added JSON Schema for SSE events (3.2a) | KS-2, D-4, D-8 |
| Phase 3 | Added ESLint enforcement (3.3a) | EXEC-001 P6 parity |
| Phase 3 | Added make sync-agent-types target | EXEC-001 P5 parity |
| Phase 3 | Added bridge scope clarification | D-15 |
| Phase 4 | Replaced manual models with codegen from RAG spec | KS-5 |
| Phase 4 | Added RAG export_openapi.py | D-5 |
| Phase 5 | Added live schema dump prerequisite | KS-10 |
| Phase 5 | Replaced hardcoded container names | KS-6 |
| Phase 5 | Added migration runner scripts | D-10 |
| Phase 6 | Added MCP server canonicalization | KS-7 |
| Phase 7 | Split validate-all into local/live | KS-9 |
| Phase 7 | Removed all || true | D-12 |
| Phase 7 | Extended spec-freshness-bot | D-11 |
| Phase 7 | Added 6 negative controls (was 3) | EXEC-001 P8 parity |
| New section | Non-negotiable alignment checklist | EXEC-001 compatibility |

---

*Version: V2-PATCHED*
*Patched by: PASS2 Contrarian Audit (opus46, 20260206-2200-cp2)*
*Original: MISSION-HYBRID-GUARDRAIL-EXEC-002 V1 (2026-02-06)*
*Inputs: PASS1 Kill Shots (KS-1 through KS-10) + Missing Pieces (D-1 through D-15)*
*Prerequisite: HYBRID-GUARDRAIL-EXEC-001 COMPLETE*
*Target: Full stack compiler-enforced contract alignment*
*Phases: 7 (P1-P7) + setup (P0) + verification*
*Contract surfaces: 7 (up from 1)*
*Negative controls: 10 (4 existing + 6 new)*
*Stance: Complete the wall. No exceptions. No silent passes.*
