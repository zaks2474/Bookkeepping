# MISSION: HYBRID GUARDRAIL PHASE 2 — FULL STACK CONTRACT COVERAGE
## Codename: `HYBRID-GUARDRAIL-EXEC-002`
## Version: VFINAL | Date: 2026-02-06
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Extend compiler-enforced alignment to ALL contract surfaces
## Prerequisite: HYBRID-GUARDRAIL-EXEC-001 COMPLETE + RT-HARDEN-001-V2 COMPLETE

```
AGENT IDENTITY (Pass 3 — Final Synthesis)
agent_name:    opus46
run_id:        20260206-2330-cp3
date_time:     2026-02-06T23:30:00Z
pass:          3 of 3 (FINAL)
inputs:        EXEC-002 V1, PASS1 report (10 kill shots, 15 missing pieces),
               PASS2 report (18 patches, hardened gates, alignment checklist),
               fresh codebase verification (2 exploration agents, 34 files inspected)
verdict:       EXECUTE — Plan is now hardened and implementation-ready
```

---

## DIRECTIVE

```
HYBRID-GUARDRAIL-EXEC-001 built compiler-enforced type alignment for
ONE contract surface: Dashboard <-> Backend.

The system has 6 MORE contract surfaces with ZERO codegen coverage:

1. Agent API -> Backend API (25 untyped .get() fallbacks, 8 response.json() calls)
2. Dashboard <- Agent API (21+15 manual event types, split-brain naming)
3. Agent API OpenAPI (18 endpoints, spec gated behind _enable_docs flag)
4. Backend -> RAG REST (plain dict requests, RAG already has Pydantic models)
5. MCP Server (3 server files, 32 total @mcp.tool decorators, no schemas)
6. Database Migrations (crawlrag: ZERO, zakops_agent: no tracking table)

This mission extends the Hybrid Guardrail pattern to ALL surfaces.
When complete, every inter-service contract will have:
- A committed specification (OpenAPI or JSON Schema)
- Generated types (TypeScript and/or Python)
- CI drift detection
- Negative controls proving gates catch sabotage
```

---

## HARD RULES (NON-NEGOTIABLE)

```
HR-1:  EVERY INTER-SERVICE CALL MUST BE TYPED. No raw .json() -> dict patterns.
HR-2:  EVERY SERVICE MUST HAVE A COMMITTED SPEC. No undocumented endpoints.
HR-3:  EVERY DATABASE MUST HAVE MIGRATION TRACKING. No hardcoded schemas.
HR-4:  EVERY CODEGEN MUST BE IN CI. Drift = build failure.
HR-5:  NEGATIVE CONTROLS MUST PROVE GATES WORK. Sabotage -> detection -> revert.
HR-6:  NO || true IN CI GATES. Either lint properly or exclude with debt-ledger entry.
HR-7:  NO HARDCODED PATHS. Use git rev-parse, docker compose service names.
HR-8:  NO MANUAL MODELS WHEN SOURCE HAS OPENAPI. Codegen or block.
HR-9:  NO CURL-BASED SPEC FETCH IN CI. Use export_openapi.py (Python import).
HR-10: ALL CODEGEN TOOLS PINNED. Version in lockfile, deterministic output verified.
HR-11: NO BEHAVIORAL CHANGES WITHOUT MIGRATION MAP. Document .get() -> typed access.
HR-12: NO MULTIPLE SERVER IMPLEMENTATIONS. Canonicalize before adding schemas.
HR-13: STOP IF PREREQUISITE FAILS. Document blocker. Do not work around it silently.
```

---

## EXEC-001 PATTERNS (MUST REPLICATE EXACTLY)

These patterns were established and verified in EXEC-001 + RT-HARDEN-001-V2. EXEC-002
MUST follow the same conventions. Deviation requires explicit justification.

| # | Pattern | EXEC-001 Implementation | EXEC-002 Convention |
|---|---------|------------------------|---------------------|
| P1 | Committed spec as truth | `packages/contracts/openapi/zakops-api.json` | Same dir: `agent-api.json`, `rag-api.json` |
| P2 | Codegen -> generated types | `openapi-typescript@7.10.1` -> `api-types.generated.ts` | Same for TS; `datamodel-code-generator==0.26.3` for Python |
| P3 | Bridge file (single import) | `types/api.ts` re-exports from generated | `types/agent-api.ts` (same pattern) |
| P4 | CI drift detection | `git diff --exit-code` after regen | Same pattern for ALL generated files |
| P5 | `make sync-*` pipeline | `make sync-types` (committed spec -> codegen) | `sync-agent-types`, `sync-backend-models`, `sync-rag-models` |
| P6 | ESLint import enforcement | `no-restricted-imports` on `api-types.generated*` | Add pattern for `agent-api-types.generated*` |
| P7 | Debt ceiling (can only decrease) | Tracked in `docs/debt-ledger.md` with expiry dates | Same for all new ceilings |
| P8 | Negative controls | Sabotage -> detect -> revert | Prove EVERY new gate catches violations |
| P9 | Portable Makefile | `MONOREPO_ROOT ?= $(shell git rev-parse --show-toplevel)` | Same; zero hardcoded absolute paths |
| P10 | Offline spec generation | `zakops-backend/scripts/export_openapi.py` | Same pattern for Agent API + RAG |

---

## VERIFIED CODEBASE STATE (Pre-Mission Baseline)

Verified 2026-02-06 by 4 exploration agents + direct inspection.

### Existing Infrastructure (EXEC-001)
| Artifact | Location | State |
|----------|----------|-------|
| Makefile | `zakops-agent-api/Makefile` | `MONOREPO_ROOT=$(git rev-parse --show-toplevel)`, targets: sync-types, update-spec, validate-all, check-contract-drift, check-redocly-debt |
| Generated types | `apps/dashboard/src/lib/api-types.generated.ts` | 5,502 lines, openapi-typescript@7.10.1 |
| Bridge file | `apps/dashboard/src/types/api.ts` | Imports from `../lib/api-types.generated`, re-exports via `components['schemas']` |
| ESLint | `apps/dashboard/.eslintrc.json` | `no-restricted-imports: ["error", patterns: [api-types.generated*, zod]]` |
| CI type-sync | `.github/workflows/ci.yml` (lines 157-220) | codegen -> drift check -> tsc -> legacy import check -> manual debt ceiling -> Zod ceiling |
| Backend spec export | `zakops-backend/scripts/export_openapi.py` | Python import of FastAPI app, `json.dumps(spec, sort_keys=True)` |
| Committed spec | `packages/contracts/openapi/zakops-api.json` | 83 paths, 56 schemas |
| Debt ledger | `docs/debt-ledger.md` | Manual type debt=0, Redocly ignores<=57, mypy baseline=83 |
| spec-freshness-bot | `.github/workflows/spec-freshness-bot.yml` | **PLACEHOLDER ONLY** (echo statements, no real checks) |

### Gap State (What EXEC-002 Fixes)
| Surface | Current State | Key Files |
|---------|--------------|-----------|
| Agent->Backend HTTP | 25 `.get()`, 8 `response.json()`, no typed client | `apps/agent-api/app/core/langgraph/tools/deal_tools.py` (1,173 lines) |
| Dashboard<-Agent SSE | 21 event types in `agent-activity.ts` (dot-prefix), 15 in `execution-contracts.ts` (no prefix) — SPLIT-BRAIN | Two files, incompatible naming |
| Agent API OpenAPI | 18 endpoints (14/18 with response_model), spec gated behind `_enable_docs` flag | `apps/agent-api/app/main.py:80-81` |
| Backend->RAG REST | Raw `requests.post(json={...})`, no Pydantic models in backend | `zakops-backend/src/actions/executors/rag_reindex_deal.py`, RAG has its own Pydantic models |
| MCP Server | 3 implementations (server.py=12 tools, server_http.py=10, server_sse.py=10), no Pydantic schemas | `zakops-backend/mcp_server/server*.py` |
| DB Migrations | crawlrag: ZERO migrations dir; zakops_agent: 2 files, NO schema_migrations table | crawlrag DDL inline in rag_rest_api.py |
| Agent API deps | No `datamodel-code-generator` in pyproject.toml | Needs codegen optional dep |
| Backend schemas dir | `zakops-backend/src/schemas/` DOES NOT EXIST | Needs creation for Phase 4 |
| Runtime topology | V3, does NOT include crawlrag | Needs update |
| Agent docker-compose | TWO compose files: `apps/agent-api/docker-compose.yml` (service: `db`) and `deployments/docker/docker-compose.yml` (service: `postgres`) | Use app-level compose (service `db`) |
| RAG docker-compose | External network `rag-backend` from crawl4ai-rag; DB service `rag-db` | `/home/zaks/Zaks-llm/docker-compose.yml` |

---

## DEPENDENCY GRAPH

```
Phase 0 (setup) -----> ALL phases depend on this

TRACK A (sequential):  Phase 1 -> Phase 2 -> Phase 3
TRACK B (independent): Phase 4
TRACK C (independent): Phase 5
TRACK D (independent): Phase 6

Phase 7 (CI hardening) -----> depends on ALL above
```

Phases 4, 5, 6 are independent of each other and of Track A. They CAN be
parallelized but MUST all complete before Phase 7. Each phase has explicit
"STOP IF FAILS" markers — do not proceed past a failed gate.

---

## PHASE 0: SETUP & BASELINE

### 0.1 Verify EXEC-001 Infrastructure

```bash
MONOREPO=$(git -C /home/zaks/zakops-agent-api rev-parse --show-toplevel)
cd "$MONOREPO"
make sync-types
cd apps/dashboard && npx tsc --noEmit
cd "$MONOREPO" && make validate-all
```

**STOP IF FAILS.** Fix EXEC-001 infrastructure before proceeding.

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

# Agent tool implementation
cp "$MONOREPO/apps/agent-api/app/core/langgraph/tools/deal_tools.py" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/deal_tools_before.py"

# Dashboard agent types (BOTH files — split-brain baseline)
cp "$MONOREPO/apps/dashboard/src/types/agent-activity.ts" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/agent-activity_before.ts"
cp "$MONOREPO/apps/dashboard/src/types/execution-contracts.ts" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/execution-contracts_before.ts"

# RAG client
cp "$BACKEND_ROOT/src/actions/executors/rag_reindex_deal.py" \
   "$EVIDENCE_ROOT/evidence/phase0-baseline/rag_reindex_deal_before.py"

# MCP server state (ALL 3 files)
for f in "$BACKEND_ROOT"/mcp_server/server*.py; do
  cp "$f" "$EVIDENCE_ROOT/evidence/phase0-baseline/$(basename "$f")_before"
done

# Count untyped patterns
grep -c '\.get(' "$MONOREPO/apps/agent-api/app/core/langgraph/tools/deal_tools.py" \
  > "$EVIDENCE_ROOT/evidence/phase0-baseline/untyped_get_count.txt"
grep -c 'response\.json()' "$MONOREPO/apps/agent-api/app/core/langgraph/tools/deal_tools.py" \
  > "$EVIDENCE_ROOT/evidence/phase0-baseline/untyped_json_count.txt"
```

### GATE P0

| Check | Command | Expected |
|-------|---------|----------|
| EXEC-001 gates pass | `make validate-all` | exit 0 |
| Evidence dirs exist | `ls -d $EVIDENCE_ROOT/evidence/phase{0..7}-*` | 9 dirs |
| Baseline files captured | `ls $EVIDENCE_ROOT/evidence/phase0-baseline/*.py $EVIDENCE_ROOT/evidence/phase0-baseline/*.ts` | >= 6 files |
| Untyped .get() count recorded | `cat $EVIDENCE_ROOT/evidence/phase0-baseline/untyped_get_count.txt` | 25 (baseline) |

---

## PHASE 1: AGENT -> BACKEND SDK (P0 — Highest Risk)

### 1.1 Install and Pin Python Client Generator

```bash
cd "$MONOREPO/apps/agent-api"

# Add to pyproject.toml under [project.optional-dependencies]:
# codegen = ["datamodel-code-generator==0.26.3"]
# Then:
uv sync --extra codegen
```

**Verify determinism** — run codegen twice, diff must be empty:

```bash
CODEGEN_OPTS="--input ../../packages/contracts/openapi/zakops-api.json \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated --field-constraints --use-double-quotes \
  --target-python-version 3.12"

uv run datamodel-codegen $CODEGEN_OPTS --output /tmp/backend_models_run1.py
uv run datamodel-codegen $CODEGEN_OPTS --output /tmp/backend_models_run2.py
diff /tmp/backend_models_run1.py /tmp/backend_models_run2.py
# MUST be empty. STOP IF NOT — investigate version-specific non-determinism.
```

Save evidence:
```bash
cp /tmp/backend_models_run1.py "$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/codegen_determinism_run1.py"
cp /tmp/backend_models_run2.py "$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/codegen_determinism_run2.py"
echo "DETERMINISTIC" > "$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/codegen_determinism_verdict.txt"
```

### 1.2 Generate Backend Response Models

```bash
cd "$MONOREPO/apps/agent-api"
uv run datamodel-codegen \
  --input ../../packages/contracts/openapi/zakops-api.json \
  --output app/schemas/backend_models.py \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated --field-constraints --use-double-quotes \
  --target-python-version 3.12

# Verify generation — must import cleanly
uv run python -c "from app.schemas.backend_models import *; print('OK')"
```

**STOP IF FAILS.** If codegen fails, the Backend OpenAPI spec has issues that must be resolved first.

### 1.3 Create Behavioral Migration Map (PREREQUISITE FOR REFACTORING)

**BEFORE touching deal_tools.py**, document every `.get()` fallback:

```bash
cd "$MONOREPO/apps/agent-api"
grep -n '\.get(' app/core/langgraph/tools/deal_tools.py \
  > "$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/get_patterns_raw.txt"
```

Create `$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/behavioral-migration-map.md`:

```markdown
# Behavioral Migration Map: deal_tools.py .get() -> Typed Access

For each .get() call, check the generated backend_models.py:

| Line | .get() Call | Generated Model Field | Required? | Migration Strategy |
|------|-------------|----------------------|-----------|-------------------|
| NNN | `data.get("field", "default")` | Model.field: type | YES/OPTIONAL/NOT_IN_SCHEMA | typed/handle_none/STOP |
```

**Rules:**
- **REQUIRED in schema** -> typed access is safe (`.field` replaces `.get("field", "default")`)
- **OPTIONAL/nullable** -> generated model has `Optional[T]`, caller MUST handle `None` explicitly
- **NOT IN SCHEMA** -> **STOP.** Response shape differs from spec. Fix spec or create envelope adapter.

**STOP IF any "NOT IN SCHEMA" entries remain.** Fix Backend spec to match actual responses first.

### 1.4 Create Typed Backend Client

Create: `apps/agent-api/app/services/backend_client.py`

```python
"""
Typed Backend API Client

Generated models from Backend OpenAPI spec ensure type safety.
All responses validated against Pydantic models before returning.

Source spec: packages/contracts/openapi/zakops-api.json
Generated models: app/schemas/backend_models.py
"""

from typing import Optional
import httpx
from pydantic import ValidationError

from app.schemas.backend_models import (
    # Import models identified in behavioral migration map
)
from app.core.config import settings

class BackendClientError(Exception):
    """Raised when backend returns unexpected response shape."""
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

    async def get_deal(self, deal_id: str, correlation_id: str = None):
        """Fetch a deal by ID with validated response.
        See behavioral-migration-map.md for field handling."""
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
    # Reference behavioral-migration-map.md for field handling decisions
```

### 1.5 Refactor Agent Tools to Use Typed Client

Follow the behavioral migration map from 1.3:

```python
# BEFORE (untyped):
deal_data = response.json()
actual_from_stage = deal_data.get("stage", "unknown")

# AFTER (typed, per migration map):
from app.services.backend_client import BackendClient, BackendClientError
_backend = BackendClient()

deal = await _backend.get_deal(deal_id, correlation_id)
actual_from_stage = deal.stage  # REQUIRED per migration map -> safe
```

### 1.6 Add Codegen to CI + Makefile

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
codegen = ["datamodel-code-generator==0.26.3"]
```

Add to Makefile:
```makefile
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

Add to `ci.yml` agent-api job:
```yaml
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

### GATE P1

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| G1.1 | Codegen deterministic | `diff run1.py run2.py` | empty | Non-empty |
| G1.2 | Models importable | `python -c "from app.schemas.backend_models import DealResponse"` | exit 0 | ImportError |
| G1.3 | Migration map complete | `wc -l behavioral-migration-map.md` | >= 25 entries | Any NOT_IN_SCHEMA |
| G1.4 | BackendClient exists | `grep -c "async def" app/services/backend_client.py` | >= 5 | 0 |
| G1.5 | Zero response.json() | `grep -c "response\.json()" deal_tools.py` | 0 | > 0 |
| G1.6 | Zero .get() fallbacks | `grep -c "\.get(" deal_tools.py` | 0 | > 0 |
| G1.7 | CI drift check | `make sync-backend-models && git diff --exit-code app/schemas/backend_models.py` | exit 0 | exit 1 |
| G1.8 | Agent tools functional | Smoke test agent invoke endpoint | 200 | Non-200 |

**Evidence:** `$EVIDENCE_ROOT/evidence/phase1-agent-backend-sdk/`

---

## PHASE 2: AGENT API OPENAPI SPEC (P0 — Foundation for Phase 3)

### 2.1 Create Offline Spec Export Script

**Do NOT use `curl localhost:8095`. Use Python import (same pattern as Backend's
`zakops-backend/scripts/export_openapi.py`).**

The Agent API gates its OpenAPI endpoint behind `_enable_docs` (main.py:80-81).
`curl` returns 404 in production mode. Python import bypasses this entirely.

```python
# Create: apps/agent-api/scripts/export_openapi.py
#!/usr/bin/env python3
"""Generate OpenAPI spec from FastAPI app without starting server.

Same pattern as zakops-backend/scripts/export_openapi.py.
Works in CI without running the Agent API service.
"""
import json
import sys
import os

# Add the agent-api root to path
agent_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, agent_root)

from app.main import app

spec = app.openapi()
print(json.dumps(spec, indent=2, sort_keys=True))
```

Test without network:
```bash
cd "$MONOREPO/apps/agent-api"
uv run python scripts/export_openapi.py | jq '.paths | keys | length'
# Expected: >= 18
```

**STOP IF FAILS.** If the script can't import `app.main` without running services,
investigate import-time side effects (database connections, etc.) and guard them
behind `if __name__ == "__main__"` or lifespan checks.

### 2.2 Fix Missing response_models

Before exporting spec, ensure all non-streaming endpoints have `response_model`:

| Endpoint | Current | Fix |
|----------|---------|-----|
| `POST /invoke/stream` | Streaming SSE | Document as `text/event-stream` in description |
| `POST /chat/stream` | Streaming SSE | Document as `text/event-stream` in description |
| `DELETE /messages` | No response_model | Add appropriate response model |
| `DELETE /session/{id}` | No response_model | Add appropriate response model |

### 2.3 Commit Spec and Validate

```bash
cd "$MONOREPO/apps/agent-api"
uv run python scripts/export_openapi.py | jq -S . > \
  ../../packages/contracts/openapi/agent-api.json

# Validate with Redocly
cd "$MONOREPO"
npx @redocly/cli lint packages/contracts/openapi/agent-api.json
# If errors: fix endpoint definitions OR add .redocly.lint-ignore.yaml entries
# with debt-ledger documentation. NEVER || true.
```

### 2.4 Create Makefile Targets

```makefile
update-agent-spec: ## Fetch Agent API spec via Python import (no running service needed)
	cd $(AGENT_API_ROOT) && uv run python scripts/export_openapi.py | jq -S . > \
		$(MONOREPO_ROOT)/packages/contracts/openapi/agent-api.json

check-agent-contract-drift: ## Verify committed agent spec matches code
	cd $(AGENT_API_ROOT) && uv run python scripts/export_openapi.py | jq -S . > /tmp/live-agent.json
	jq -S . $(MONOREPO_ROOT)/packages/contracts/openapi/agent-api.json > /tmp/committed-agent.json
	diff /tmp/live-agent.json /tmp/committed-agent.json && \
		echo "Agent API spec matches code" || \
		{ echo "Agent API spec drift detected — run 'make update-agent-spec'"; exit 1; }
```

### GATE P2

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| G2.1 | Offline export works | `cd apps/agent-api && uv run python scripts/export_openapi.py \| jq .` | valid JSON | error |
| G2.2 | Spec committed | `test -f packages/contracts/openapi/agent-api.json` | exit 0 | exit 1 |
| G2.3 | Endpoint count | `jq '.paths \| keys \| length' agent-api.json` | >= 18 | < 18 |
| G2.4 | Redocly lint | `npx @redocly/cli lint agent-api.json` | exit 0 (or documented ignores) | unknown errors |
| G2.5 | Makefile targets | `make update-agent-spec && make check-agent-contract-drift` | both exit 0 | either fails |
| G2.6 | Canonical JSON | `jq -S . agent-api.json \| diff agent-api.json -` | empty diff | non-empty |

**Evidence:** `$EVIDENCE_ROOT/evidence/phase2-agent-openapi/`

---

## PHASE 3: DASHBOARD <- AGENT CODEGEN (P1 — Depends on Phase 2)

### 3.0 Resolve Event Type Split-Brain (PREREQUISITE)

**MUST complete before any codegen. Two files define incompatible event types:**
- `agent-activity.ts`: 21 types with dot-prefix (`agent.run_started`)
- `execution-contracts.ts`: 15 types without prefix (`run_started`)

```bash
# Step 1: Identify canonical format from Agent API backend code
cd "$MONOREPO/apps/agent-api"
grep -rn "event_type\|EventType\|event\.type" app/ --include="*.py" \
  > "$EVIDENCE_ROOT/evidence/phase3-dashboard-agent-codegen/backend-event-formats.txt"

# Step 2: Determine which naming convention the backend actually emits
# Step 3: Choose ONE canonical definition:
#   - If backend emits "agent.run_started" -> agent-activity.ts is correct
#   - If backend emits "run_started"       -> execution-contracts.ts is correct
# Step 4: Update the non-canonical file to re-export from the canonical source
# Step 5: Verify dashboard builds clean
cd "$MONOREPO/apps/dashboard" && npx tsc --noEmit
```

**STOP IF dashboard doesn't build after unification.** Fix type errors before proceeding.

### 3.1 Create SSE Event Type Contract (JSON Schema)

OpenAPI has no standard for SSE event type enumeration. `openapi-typescript`
generates response types, not event stream payloads. Use JSON Schema instead.

```python
# Create: apps/agent-api/app/schemas/events.py
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AgentEventType(str, Enum):
    """Canonical event types emitted via SSE. Dashboard consumes these.
    Source of truth for all SSE event type strings."""
    RUN_STARTED = "agent.run_started"       # or "run_started" — per 3.0 decision
    RUN_COMPLETED = "agent.run_completed"
    RUN_FAILED = "agent.run_failed"
    TOOL_CALLED = "agent.tool_called"
    TOOL_COMPLETED = "agent.tool_completed"
    TOOL_FAILED = "agent.tool_failed"
    # ... all canonical types from the 3.0 resolution

class AgentActivityEvent(BaseModel):
    """SSE event payload schema. Committed as JSON Schema for TS codegen."""
    id: str
    type: AgentEventType
    label: str
    timestamp: datetime
    deal_id: Optional[str] = None
    deal_name: Optional[str] = None
    metadata: Dict[str, Any] = {}
```

```python
# Create: apps/agent-api/scripts/export_event_schema.py
#!/usr/bin/env python3
"""Export SSE event schemas as JSON Schema for TypeScript codegen."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.schemas.events import AgentActivityEvent, AgentEventType
schema = AgentActivityEvent.model_json_schema()
print(json.dumps(schema, indent=2, sort_keys=True))
```

```bash
# Generate JSON Schema
cd "$MONOREPO/apps/agent-api"
mkdir -p ../../packages/contracts/events
uv run python scripts/export_event_schema.py | jq -S . > \
  ../../packages/contracts/events/agent-events.schema.json

# Generate TypeScript from JSON Schema
cd "$MONOREPO/apps/dashboard"
npx json-schema-to-typescript ../../packages/contracts/events/agent-events.schema.json \
  -o src/lib/agent-event-types.generated.ts
```

### 3.2 Generate TypeScript Types from Agent API OpenAPI

```bash
cd "$MONOREPO/apps/dashboard"
npx openapi-typescript ../../packages/contracts/openapi/agent-api.json \
  -o src/lib/agent-api-types.generated.ts
```

### 3.3 Create Agent API Bridge File

```typescript
// Create: apps/dashboard/src/types/agent-api.ts

/**
 * Agent API Type Bridge
 *
 * Single source of truth for Agent API types in the dashboard.
 *
 * SOURCE SPEC: packages/contracts/openapi/agent-api.json
 * GENERATED FROM: src/lib/agent-api-types.generated.ts
 *
 * NOTE: This bridges the AGENT API (port 8095).
 * For BACKEND API (port 8091) types, use types/api.ts.
 */

import type { components } from '@/lib/agent-api-types.generated';

// GENERATED TYPE ALIASES (from Agent API OpenAPI spec)
export type AgentInvokeRequest = components['schemas']['AgentInvokeRequest'];
export type AgentInvokeResponse = components['schemas']['AgentInvokeResponse'];
export type PendingApproval = components['schemas']['PendingApproval'];
export type ApprovalListResponse = components['schemas']['ApprovalListResponse'];
// ... add all Agent API schemas

// SSE EVENT TYPES (from JSON Schema contract)
export type { AgentEventType, AgentActivityEvent } from '@/lib/agent-event-types.generated';
```

### 3.4 Add ESLint Enforcement

Add to `.eslintrc.json` `no-restricted-imports` patterns array:

```json
{
  "group": ["**/agent-api-types.generated*"],
  "message": "Import from '@/types/agent-api' instead of the generated file directly."
},
{
  "group": ["**/agent-event-types.generated*"],
  "message": "Import from '@/types/agent-api' instead of the generated file directly."
}
```

Add override for bridge file:
```json
{
  "files": ["src/types/agent-api.ts"],
  "rules": {
    "no-restricted-imports": "off"
  }
}
```

### 3.5 Refactor Dashboard to Use Generated Types

Update `agent-activity.ts` to re-export from the bridge (or remove manual types
that are now generated). Update `execution-contracts.ts` similarly per 3.0 resolution.

### 3.6 Add Sync Target and CI

Makefile:
```makefile
sync-agent-types: ## Regenerate TypeScript types from committed Agent API spec
	cd $(DASHBOARD_ROOT) && npx openapi-typescript \
		../../packages/contracts/openapi/agent-api.json \
		-o src/lib/agent-api-types.generated.ts
```

CI (`ci.yml` type-sync job, add after existing codegen):
```yaml
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

      - name: Agent legacy import check
        run: |
          VIOLATIONS=$(grep -r "agent-api-types\.generated" src/ --include='*.ts' --include='*.tsx' -l \
            | grep -v "src/types/agent-api.ts" \
            | grep -v "src/lib/agent-api-types.generated.ts" || true)
          if [ -n "$VIOLATIONS" ]; then
            echo "::error::Direct imports from agent-api-types.generated found:"
            echo "$VIOLATIONS"
            exit 1
          fi
```

### GATE P3

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| G3.1 | Split-brain resolved | `grep -rn "EventType" apps/dashboard/src/types/ \| sort` | ONE canonical def | Two incompatible defs |
| G3.2 | Generated TS exists | `wc -l apps/dashboard/src/lib/agent-api-types.generated.ts` | > 100 lines | 0 |
| G3.3 | Event schema committed | `test -f packages/contracts/events/agent-events.schema.json` | exit 0 | exit 1 |
| G3.4 | Bridge file exists | `test -f apps/dashboard/src/types/agent-api.ts` | exit 0 | exit 1 |
| G3.5 | ESLint blocks direct imports | Add test import -> `npm run lint` | exit 1 | exit 0 |
| G3.6 | Dashboard builds | `cd apps/dashboard && npx tsc --noEmit` | exit 0 | exit 1 |
| G3.7 | CI drift check | `make sync-agent-types && git diff --exit-code` | exit 0 | exit 1 |

**Evidence:** `$EVIDENCE_ROOT/evidence/phase3-dashboard-agent-codegen/`

---

## PHASE 4: BACKEND -> RAG CONTRACT (P1 — Medium Risk)

**CRITICAL: RAG API (`Zaks-llm/src/api/rag_rest_api.py`) is already FastAPI with
Pydantic models (`QueryRequest`, `AddContentRequest`). Do NOT hand-write duplicate
models. Codegen from RAG's own OpenAPI spec.**

### 4.1 Create RAG Spec Export Script

```python
# Create: Zaks-llm/scripts/export_openapi.py
#!/usr/bin/env python3
"""Generate OpenAPI spec from RAG REST API without starting server."""
import json
import sys
import os

rag_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(rag_root, "src"))

from api.rag_rest_api import app

spec = app.openapi()
print(json.dumps(spec, indent=2, sort_keys=True))
```

Test:
```bash
cd "$ZAKS_LLM_ROOT"
python scripts/export_openapi.py | jq '.paths | keys | length'
# Expected: >= 4 (query, add, sources, stats)
```

**NOTE:** RAG's FastAPI app uses `asyncpg.create_pool` in its lifespan. The
`export_openapi.py` script calls `app.openapi()` which does NOT trigger lifespan.
If it fails due to import-time DB connection, guard the pool creation.

### 4.2 Commit RAG Spec and Generate Backend Models

```bash
# Create backend schemas directory (DOES NOT EXIST YET)
mkdir -p "$BACKEND_ROOT/src/schemas"

# Commit RAG spec to contracts
cd "$ZAKS_LLM_ROOT"
python scripts/export_openapi.py | jq -S . > \
  "$MONOREPO/packages/contracts/openapi/rag-api.json"

# Generate backend models from RAG spec
cd "$BACKEND_ROOT"
pip install datamodel-code-generator==0.26.3  # Pin same version as agent-api
datamodel-codegen \
  --input "$MONOREPO/packages/contracts/openapi/rag-api.json" \
  --output src/schemas/rag_models.py \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated --field-constraints --use-double-quotes \
  --target-python-version 3.12

# Verify
python -c "from src.schemas.rag_models import AddContentRequest; print('OK')"
```

### 4.3 Refactor RAG Reindex to Use Generated Models

```python
# Update: src/actions/executors/rag_reindex_deal.py

# BEFORE: raw dict
resp = requests.post(_rag_api_url(), json={...}, timeout=30)

# AFTER: generated model from RAG's own spec
from src.schemas.rag_models import AddContentRequest
request = AddContentRequest(
    url=f"https://dataroom.local/DataRoom/{file_path}",
    content=file_content,
    metadata={"source": "deal", "deal_id": deal_id, "path": file_path},
    chunk_size=5000,
)
resp = requests.post(_rag_api_url(), json=request.model_dump(), timeout=30)
```

### 4.4 Makefile Targets

```makefile
ZAKS_LLM_ROOT ?= /home/zaks/Zaks-llm
BACKEND_ROOT ?= /home/zaks/zakops-backend

update-rag-spec: ## Fetch RAG API spec via Python import
	cd $(ZAKS_LLM_ROOT) && python scripts/export_openapi.py | jq -S . > \
		$(MONOREPO_ROOT)/packages/contracts/openapi/rag-api.json

sync-rag-models: ## Generate Pydantic models from RAG OpenAPI
	cd $(BACKEND_ROOT) && datamodel-codegen \
		--input $(MONOREPO_ROOT)/packages/contracts/openapi/rag-api.json \
		--output src/schemas/rag_models.py \
		--input-file-type openapi \
		--output-model-type pydantic_v2.BaseModel \
		--use-annotated --field-constraints --use-double-quotes \
		--target-python-version 3.12

check-rag-contract-drift: ## Verify committed RAG spec matches code
	cd $(ZAKS_LLM_ROOT) && python scripts/export_openapi.py | jq -S . > /tmp/live-rag.json
	jq -S . $(MONOREPO_ROOT)/packages/contracts/openapi/rag-api.json > /tmp/committed-rag.json
	diff /tmp/live-rag.json /tmp/committed-rag.json && \
		echo "RAG spec matches code" || \
		{ echo "RAG spec drift detected — run 'make update-rag-spec'"; exit 1; }
```

### GATE P4

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| G4.1 | RAG export works | `cd Zaks-llm && python scripts/export_openapi.py \| jq .` | valid JSON | error |
| G4.2 | RAG spec committed | `test -f packages/contracts/openapi/rag-api.json` | exit 0 | exit 1 |
| G4.3 | Models codegen'd | `python -c "from src.schemas.rag_models import AddContentRequest"` | exit 0 | ImportError |
| G4.4 | Reindex uses models | `grep -c "RAGAddRequest\|AddContentRequest" rag_reindex_deal.py` | >= 1 | 0 |
| G4.5 | Drift check | `make sync-rag-models && git diff --exit-code src/schemas/rag_models.py` | exit 0 | exit 1 |

**Evidence:** `$EVIDENCE_ROOT/evidence/phase4-backend-rag-contract/`

---

## PHASE 5: DATABASE MIGRATION GOVERNANCE (P1 — Critical for crawlrag)

### 5.0 Dump Live Schemas (PREREQUISITE)

**Capture actual schema BEFORE creating any migrations.**

```bash
# crawlrag — uses external rag-db from Zaks-llm compose
cd "$ZAKS_LLM_ROOT"
docker compose exec -T rag-db pg_dump -U postgres -d crawlrag --schema-only \
  > "$EVIDENCE_ROOT/evidence/phase5-database-migrations/crawlrag-live-schema.sql"

# zakops_agent — uses db service from agent-api compose
cd "$MONOREPO/apps/agent-api"
docker compose exec -T db pg_dump -U agent -d zakops_agent --schema-only \
  > "$EVIDENCE_ROOT/evidence/phase5-database-migrations/zakops_agent-live-schema.sql"
```

**STOP IF either dump fails.** The service must be running for schema dump. Document
as blocker and move to a parallel track.

### 5.1 Create crawlrag Migration Infrastructure

```bash
mkdir -p "$ZAKS_LLM_ROOT/db/migrations"
```

**Base initial migration on the LIVE dump, not assumptions:**

1. Review the live schema dump from 5.0
2. Write `001_initial_schema.sql` that matches the live schema exactly
3. Add `schema_migrations` tracking table
4. Diff to verify:

```bash
# After writing 001_initial_schema.sql:
diff "$EVIDENCE_ROOT/evidence/phase5-database-migrations/crawlrag-live-schema.sql" \
     "$ZAKS_LLM_ROOT/db/migrations/001_initial_schema.sql" \
  > "$EVIDENCE_ROOT/evidence/phase5-database-migrations/crawlrag-live-vs-proposed.diff"
# Only difference should be the schema_migrations table addition
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

### 5.3 Create Migration Runner Scripts

```bash
# Create: apps/agent-api/scripts/run_migrations.sh
#!/usr/bin/env bash
set -euo pipefail
MIGRATIONS_DIR="$(cd "$(dirname "$0")/../migrations" && pwd)"
DB_URL="${DATABASE_URL:?DATABASE_URL not set}"

# Ensure schema_migrations table exists
psql "$DB_URL" -c "CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);" 2>/dev/null || true

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

Mark both executable: `chmod +x scripts/run_migrations.sh`

### 5.4 Update Migration Assertion Script

The current `migration-assertion.sh` (57 lines) only checks the backend via
`$POSTGRES_CID` from topology.env. It must be extended to check all 3 databases.

**Use `docker compose exec` with service names (portable), NOT `docker exec`
with container names (hardcoded).**

```bash
# Add functions for agent-api and crawlrag checks:

check_agent_migrations() {
    echo "=== Checking zakops_agent migrations ==="
    AGENT_MIGRATIONS="$MONOREPO/apps/agent-api/migrations"
    [ ! -d "$AGENT_MIGRATIONS" ] && echo "SKIP: no agent migrations dir" && return 0

    LATEST_FILE=$(ls -1 "$AGENT_MIGRATIONS"/*.sql 2>/dev/null | sort -V | tail -1)
    [ -z "$LATEST_FILE" ] && echo "SKIP: no migration files" && return 0
    LATEST_VERSION=$(basename "$LATEST_FILE" .sql)

    # Use docker compose service name (db), not container name
    APPLIED=$(cd "$MONOREPO/apps/agent-api" && docker compose exec -T db \
        psql -U agent -d zakops_agent -t -c \
        "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1" \
        2>/dev/null | tr -d ' ')

    [ "$LATEST_VERSION" = "$APPLIED" ] && echo "zakops_agent: OK ($APPLIED)" && return 0
    echo "FAIL: zakops_agent file=$LATEST_VERSION db=${APPLIED:-none}" && return 1
}

check_crawlrag_migrations() {
    echo "=== Checking crawlrag migrations ==="
    CRAWLRAG_MIGRATIONS="$ZAKS_LLM_ROOT/db/migrations"
    [ ! -d "$CRAWLRAG_MIGRATIONS" ] && echo "SKIP: no crawlrag migrations dir" && return 0

    LATEST_FILE=$(ls -1 "$CRAWLRAG_MIGRATIONS"/*.sql 2>/dev/null | sort -V | tail -1)
    [ -z "$LATEST_FILE" ] && echo "SKIP: no migration files" && return 0
    LATEST_VERSION=$(basename "$LATEST_FILE" .sql)

    APPLIED=$(cd "$ZAKS_LLM_ROOT" && docker compose exec -T rag-db \
        psql -U postgres -d crawlrag -t -c \
        "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1" \
        2>/dev/null | tr -d ' ')

    [ "$LATEST_VERSION" = "$APPLIED" ] && echo "crawlrag: OK ($APPLIED)" && return 0
    echo "FAIL: crawlrag file=$LATEST_VERSION db=${APPLIED:-none}" && return 1
}
```

### 5.5 Update runtime.topology.json

Add crawlrag to the V3 topology:

```json
{
  "rag-api": {
    "expected_database": "crawlrag",
    "expected_schema": "public",
    "migrations_dir": "Zaks-llm/db/migrations",
    "description": "pgvector embeddings for RAG, external rag-backend network"
  }
}
```

### GATE P5

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| G5.1 | Live schemas dumped | `test -s evidence/phase5*/crawlrag-live-schema.sql` | non-empty | empty/missing |
| G5.2 | crawlrag migration exists | `test -f Zaks-llm/db/migrations/001_initial_schema.sql` | exit 0 | exit 1 |
| G5.3 | Migration matches live | `diff` reviewed, only schema_migrations delta | reviewed | structural mismatch |
| G5.4 | Agent tracking added | `test -f apps/agent-api/migrations/003_add_migration_tracking.sql` | exit 0 | exit 1 |
| G5.5 | Runner scripts executable | `test -x apps/agent-api/scripts/run_migrations.sh` | exit 0 | exit 1 |
| G5.6 | No hardcoded container names | `grep -c "docker exec [a-z]" tools/infra/migration-assertion.sh` | 0 new | > 0 new |
| G5.7 | Topology includes crawlrag | `jq '.db_mapping["rag-api"]' contracts/runtime.topology.json` | non-null | null |

**Evidence:** `$EVIDENCE_ROOT/evidence/phase5-database-migrations/`

---

## PHASE 6: MCP CONTRACT FORMALIZATION (P2 — Lower Risk)

### 6.0 Canonicalize MCP Server (PREREQUISITE)

Three implementations exist:
| File | Tools | Transport | Notes |
|------|-------|-----------|-------|
| `server.py` | 12 | SSE | Primary, most tools |
| `server_http.py` | 10 | HTTP streamable | "CORRECT for LangSmith" |
| `server_sse.py` | 10 | SSE/uvicorn | Latest v3.1.0 |

**Decision process:**
1. Identify which server is actually used in production (check docker-compose, Makefile, docs)
2. Ensure canonical server has ALL 12 tools
3. Archive non-canonical to `mcp_server/archived/`
4. Document decision in `mcp_server/README.md`

```bash
cd "$BACKEND_ROOT/mcp_server"
mkdir -p archived

# After deciding canonical server (likely server.py — most tools):
mv server_http.py archived/
mv server_sse.py archived/
echo "# MCP Server\n\nCanonical: server.py (12 tools, SSE transport)\nArchived: server_http.py, server_sse.py (see archived/)" > README.md
```

**STOP IF you cannot determine which server is canonical.** Ask for clarification.

### 6.1 Create Pydantic Schemas for MCP Tools

```python
# Create: mcp_server/tool_schemas.py
"""
MCP Tool Input Schemas — Pydantic models for all 12 tools.
Used for input validation and JSON Schema export.
"""
from pydantic import BaseModel, Field
from typing import Optional

class ListDealsInput(BaseModel):
    stage: Optional[str] = Field(None, description="Filter by deal stage")
    limit: int = Field(50, ge=1, le=100)

class GetDealInput(BaseModel):
    deal_id: str = Field(..., description="Deal ID to fetch")

class TransitionDealInput(BaseModel):
    deal_id: str = Field(...)
    new_stage: str = Field(...)
    reason: Optional[str] = None

# ... models for all 12 tools

def export_tool_schemas() -> dict:
    """Export all tool schemas as JSON Schema dict."""
    return {
        "list_deals": ListDealsInput.model_json_schema(),
        "get_deal": GetDealInput.model_json_schema(),
        "transition_deal": TransitionDealInput.model_json_schema(),
        # ... all 12
    }
```

### 6.2 Add Validation to Canonical Server

```python
# Update canonical server.py:
from tool_schemas import ListDealsInput, GetDealInput, TransitionDealInput
from pydantic import ValidationError

@mcp.tool()
async def list_deals(stage: str = None, limit: int = 50):
    """List deals with optional filters."""
    validated = ListDealsInput(stage=stage, limit=limit)  # Validates on construction
    # ... rest of implementation uses validated.stage, validated.limit
```

### 6.3 Commit Contract

```bash
mkdir -p "$MONOREPO/packages/contracts/mcp"
cd "$BACKEND_ROOT"
python -c "
from mcp_server.tool_schemas import export_tool_schemas
import json
print(json.dumps(export_tool_schemas(), indent=2, sort_keys=True))
" > "$MONOREPO/packages/contracts/mcp/tool-schemas.json"
```

### GATE P6

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| G6.1 | One canonical server | `ls mcp_server/server*.py \| grep -v archived \| wc -l` | 1 | > 1 |
| G6.2 | All 12 tools in canonical | `grep -c "@mcp.tool" mcp_server/server.py` | 12 | < 12 |
| G6.3 | Schemas exist | `grep -c "class.*BaseModel" mcp_server/tool_schemas.py` | >= 12 | < 12 |
| G6.4 | Server validates | `grep -c "ValidationError\|model_validate" mcp_server/server.py` | >= 1 | 0 |
| G6.5 | Contract committed | `test -f packages/contracts/mcp/tool-schemas.json` | exit 0 | exit 1 |

**Evidence:** `$EVIDENCE_ROOT/evidence/phase6-mcp-contract/`

---

## PHASE 7: CI INTEGRATION & HARDENING

### 7.1 Update CI Workflow

Add to `ci.yml`:

```yaml
  contract-validation:
    needs: [changes]
    if: >
      needs.changes.outputs.contracts == 'true' ||
      needs.changes.outputs.agent-api == 'true' ||
      needs.changes.outputs.dashboard == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Validate OpenAPI specs
        run: |
          npx @redocly/cli lint packages/contracts/openapi/zakops-api.json
          npx @redocly/cli lint packages/contracts/openapi/agent-api.json
          # RAG spec: lint with documented ignores. NEVER || true.

      - name: All codegen drift checks
        run: |
          # Dashboard <- Backend (existing)
          npx openapi-typescript packages/contracts/openapi/zakops-api.json \
            -o apps/dashboard/src/lib/api-types.generated.ts
          git diff --exit-code apps/dashboard/src/lib/api-types.generated.ts

          # Dashboard <- Agent API (new)
          npx openapi-typescript packages/contracts/openapi/agent-api.json \
            -o apps/dashboard/src/lib/agent-api-types.generated.ts
          git diff --exit-code apps/dashboard/src/lib/agent-api-types.generated.ts

          # Agent API <- Backend (Python, new)
          cd apps/agent-api && uv sync --extra codegen
          uv run datamodel-codegen \
            --input ../../packages/contracts/openapi/zakops-api.json \
            --output app/schemas/backend_models.py \
            --input-file-type openapi \
            --output-model-type pydantic_v2.BaseModel \
            --use-annotated --field-constraints --use-double-quotes \
            --target-python-version 3.12
          git diff --exit-code app/schemas/backend_models.py
```

### 7.2 Split validate-all into local/live

```makefile
validate-local: sync-types sync-agent-types lint-dashboard ## Offline gates (CI-safe)
	cd $(DASHBOARD_ROOT) && npx tsc --noEmit
	@$(MAKE) check-redocly-debt
	@echo "All local validations passed"

validate-live: validate-local ## Online gates (needs running services)
	@$(MAKE) check-contract-drift
	@$(MAKE) check-agent-contract-drift
	@echo "All live validations passed"

validate-all: validate-live ## Full suite (backwards compatible)

sync-all: sync-types sync-agent-types sync-backend-models ## Regenerate all types
```

CI uses `validate-local` only. Developers run `validate-live` when services are up.

### 7.3 Implement spec-freshness-bot (Currently PLACEHOLDER)

The existing `spec-freshness-bot.yml` is placeholder-only (echo statements).
Replace with real implementation:

```yaml
name: Spec Freshness Bot

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  check-spec-freshness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Check Backend spec freshness
        run: |
          cd zakops-backend
          pip install -e .
          python scripts/export_openapi.py | jq -S . > /tmp/live-backend.json
          jq -S . ../packages/contracts/openapi/zakops-api.json > /tmp/committed-backend.json
          if ! diff /tmp/live-backend.json /tmp/committed-backend.json; then
            echo "::warning::Backend spec may be stale. Run 'make update-spec'."
          fi

      - name: Check Agent API spec freshness
        run: |
          cd apps/agent-api
          uv sync
          uv run python scripts/export_openapi.py | jq -S . > /tmp/live-agent.json
          jq -S . ../../packages/contracts/openapi/agent-api.json > /tmp/committed-agent.json
          if ! diff /tmp/live-agent.json /tmp/committed-agent.json; then
            echo "::warning::Agent API spec may be stale. Run 'make update-agent-spec'."
          fi
```

### 7.4 Negative Controls (6 sabotage tests)

| # | Test | Sabotage | Expected Detection | Remediation |
|---|------|----------|-------------------|-------------|
| NC-1 | Backend model drift | `echo "SABOTAGE" >> backend_models.py` | `make sync-backend-models` regenerates; `git diff --exit-code` fails | Regen removes sabotage |
| NC-2 | Agent type drift | `echo "// SABOTAGE" >> agent-api-types.generated.ts` | `make sync-agent-types` regenerates; `git diff --exit-code` fails | Regen removes sabotage |
| NC-3 | Direct import bypass | Add `import { X } from '@/lib/agent-api-types.generated'` to test file | `npm run lint` exits 1 (ESLint) | Remove import |
| NC-4 | SSE event type unknown | Add unknown event to JSON Schema, regen TS | Dashboard build catches unhandled type | Fix schema or add handler |
| NC-5 | Migration version drift | `DELETE FROM schema_migrations WHERE version = '002_decision_ledger'` | `migration-assertion.sh` detects, exits 1 | Re-apply migration |
| NC-6 | RAG model drift | `echo "SABOTAGE" >> rag_models.py` | `make sync-rag-models` regenerates; `git diff --exit-code` fails | Regen removes sabotage |

Execute each sabotage test, capture evidence, revert.

### 7.5 Update Documentation

- Update `docs/debt-ledger.md` with new ceilings:
  - Agent API Redocly ignores (count + expiry)
  - RAG spec Redocly ignores (if any)
  - MCP server consolidation decision
  - SSE event manual types remaining (if any)
- Update `SERVICE-CATALOG.md` with new contract surfaces
- Update `RUNBOOKS.md` with new `make sync-*` commands
- Update `CHANGES.md` with EXEC-002 mission completion

### GATE P7

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| G7.1 | No `\|\| true` | `grep -c '\|\| true' .github/workflows/ci.yml` | 0 | > 0 |
| G7.2 | validate-local offline | `make validate-local` (no services) | exit 0 | exit 1 |
| G7.3 | Negative controls | NC-1 through NC-6 | 6/6 PASS | any FAIL |
| G7.4 | spec-freshness-bot real | `grep -c "export_openapi" .github/workflows/spec-freshness-bot.yml` | >= 2 | 0 |
| G7.5 | Debt ledger updated | `grep -c "EXEC-002" docs/debt-ledger.md` | >= 1 | 0 |

**Evidence:** `$EVIDENCE_ROOT/evidence/phase7-ci-hardening/`

---

## NO-DRIFT ALIGNMENT CONTRACT

### Source-of-Truth Locations

| Contract Surface | Spec File | Generated File | Bridge File (if TS) |
|-----------------|-----------|----------------|---------------------|
| Dashboard <-> Backend | `packages/contracts/openapi/zakops-api.json` | `apps/dashboard/src/lib/api-types.generated.ts` | `apps/dashboard/src/types/api.ts` |
| Dashboard <- Agent API | `packages/contracts/openapi/agent-api.json` | `apps/dashboard/src/lib/agent-api-types.generated.ts` | `apps/dashboard/src/types/agent-api.ts` |
| Dashboard <- Agent SSE | `packages/contracts/events/agent-events.schema.json` | `apps/dashboard/src/lib/agent-event-types.generated.ts` | (re-exported via agent-api.ts) |
| Agent API -> Backend | `packages/contracts/openapi/zakops-api.json` | `apps/agent-api/app/schemas/backend_models.py` | (Python: BackendClient) |
| Backend -> RAG | `packages/contracts/openapi/rag-api.json` | `zakops-backend/src/schemas/rag_models.py` | (Python: direct import) |
| MCP Server | `packages/contracts/mcp/tool-schemas.json` | (source: tool_schemas.py) | N/A |

### CI Checks That Enforce Them

| Gate | What It Checks | Failure Mode |
|------|----------------|-------------|
| type-sync: Backend codegen | `openapi-typescript` regen + `git diff --exit-code` | Drift = exit 1 |
| type-sync: Agent codegen | `openapi-typescript` regen + `git diff --exit-code` | Drift = exit 1 |
| type-sync: Python codegen | `datamodel-codegen` regen + `git diff --exit-code` | Drift = exit 1 |
| type-sync: Legacy import | `grep` for direct generated-file imports | Bypass = exit 1 |
| type-sync: ESLint | `no-restricted-imports` for all generated files | Bypass = lint error |
| contract-validation: Redocly | `@redocly/cli lint` all specs | Invalid spec = exit 1 |
| type-sync: tsc | `npx tsc --noEmit` | Type error = exit 1 |

### Required Make Targets (Final List)

| Target | Function | New/Existing |
|--------|----------|--------------|
| `sync-types` | Dashboard <- Backend TS types | EXISTING |
| `sync-agent-types` | Dashboard <- Agent API TS types | NEW |
| `sync-backend-models` | Agent API <- Backend Python models | NEW |
| `sync-rag-models` | Backend <- RAG Python models | NEW |
| `sync-all` | All sync targets | NEW |
| `update-spec` | Fetch Backend spec | EXISTING |
| `update-agent-spec` | Fetch Agent API spec | NEW |
| `update-rag-spec` | Fetch RAG spec | NEW |
| `validate-local` | Offline gates (CI-safe) | NEW |
| `validate-live` | Online gates (needs services) | NEW |
| `validate-all` | Full suite | EXISTING (updated) |
| `check-contract-drift` | Backend spec drift | EXISTING |
| `check-agent-contract-drift` | Agent API spec drift | NEW |
| `check-rag-contract-drift` | RAG spec drift | NEW |
| `check-redocly-debt` | Redocly ignore ceiling | EXISTING |

### Bridge File Convention

- Each bridge file imports ONLY from its generated file
- Each bridge file is the ONLY file importing from its generated file
- Bridge file header MUST name its source spec
- ESLint `no-restricted-imports` enforces ALL bridge files

---

## WHAT COULD STILL GO WRONG (RESIDUAL RISKS)

### R-1: RAG `export_openapi.py` import-time side effects (MEDIUM)

RAG's FastAPI app uses `asyncpg.create_pool` in its lifespan. While `app.openapi()`
should not trigger lifespan, some apps connect to DB at import time for alembic or
config validation. If the export script fails without a running database, you need
to mock the DB connection or guard the pool creation behind `if __name__ == "__main__"`.

**Detection:** `cd Zaks-llm && python scripts/export_openapi.py` fails with connection error.
**Mitigation:** Add `try/except` around pool creation, or use `unittest.mock.patch`.

### R-2: `datamodel-code-generator` field ordering sensitivity (LOW)

Even with pinned version, if the OpenAPI spec changes field ordering (e.g., after
`jq -S .` re-sort), the generated Python models may have different field order.
This is cosmetic but triggers false drift detection.

**Detection:** `make sync-backend-models && git diff` shows only field reordering.
**Mitigation:** Always normalize spec with `jq -S .` before committing.

### R-3: Agent API import chain pulls in LangGraph at spec-export time (MEDIUM)

`apps/agent-api/app/main.py` may import LangGraph components that require
running infrastructure (Redis, Postgres). If `export_openapi.py` triggers
these imports, it will fail in CI.

**Detection:** `uv run python scripts/export_openapi.py` fails with connection error.
**Mitigation:** Lazy-import LangGraph tools, or create a minimal FastAPI app for spec export only.

### R-4: Two docker-compose files for agent-api (LOW)

Agent API has `apps/agent-api/docker-compose.yml` (service: `db`, user: `agent`)
and `deployments/docker/docker-compose.yml` (service: `postgres`, user: `zakops`).
Migration assertions must target the correct one.

**Detection:** `docker compose exec -T db psql` fails because wrong compose file.
**Mitigation:** Always `cd apps/agent-api` before running compose commands.

### R-5: crawlrag `rag-db` is external to Zaks-llm compose (LOW)

The `rag-db` service is defined in an external compose file (`/root/mcp-servers/crawl4ai-rag/`),
not in `Zaks-llm/docker-compose.yml`. The `docker compose exec -T rag-db` command
may fail if the external network isn't up.

**Detection:** `cd Zaks-llm && docker compose exec -T rag-db psql` fails.
**Mitigation:** Check if `rag-db` is accessible via `docker exec` as fallback,
or document that `crawl4ai-rag` compose must be running.

### R-6: SSE event types not exhaustively enumerable (MEDIUM)

If the Agent API backend emits event types dynamically (e.g., plugin-generated),
the Python Enum approach in Phase 3 cannot capture them. The JSON Schema contract
becomes incomplete.

**Detection:** Dashboard receives events not in the generated type union.
**Mitigation:** Add `UNKNOWN = "unknown"` catch-all to the Enum, with
MANUAL_TYPE_DEBT tracking.

### R-7: `execution-contracts.ts` has type guards that may break on rename (MEDIUM)

The 585-line file includes runtime type guard functions. If event types are renamed
in the split-brain resolution (Phase 3.0), these guards break silently at runtime
(they just return false instead of true).

**Detection:** `tsc --noEmit` passes but runtime type narrowing stops working.
**Mitigation:** Add unit tests for type guards as part of Phase 3.0 resolution.

---

## VERIFICATION SEQUENCE

```
Execute in this order. Do NOT skip steps. STOP IF any gate fails.

1. PHASE 0 — Setup & baseline
   |- Verify EXEC-001 works (STOP IF FAILS)
   |- Create evidence dirs
   |- Capture baselines (including execution-contracts.ts + MCP file list)

2. PHASE 1 — Agent -> Backend SDK (CRITICAL)
   |- Pin datamodel-code-generator==0.26.3 + verify determinism
   |- Generate backend_models.py
   |- Create behavioral migration map (STOP IF NOT_IN_SCHEMA entries)
   |- Create BackendClient
   |- Refactor deal_tools.py
   |- Verify: zero .get() fallbacks, zero response.json(), codegen deterministic

3. PHASE 2 — Agent API OpenAPI Spec (CRITICAL)
   |- Create export_openapi.py (Python import, no curl)
   |- Fix 4 missing response_models
   |- Export spec, commit, validate with Redocly
   |- Verify: >= 18 endpoints, canonical JSON

4. PHASE 3 — Dashboard <- Agent Codegen
   |- Resolve event type split-brain (STOP IF dashboard breaks)
   |- Create SSE event JSON Schema contract
   |- Generate agent-api-types.generated.ts
   |- Create bridge file + ESLint enforcement
   |- Verify: tsc --noEmit exits 0, ESLint blocks direct imports

5. PHASE 4 — Backend -> RAG Contract (parallel with Track A)
   |- Create RAG export_openapi.py (Python import)
   |- Codegen rag_models.py from RAG spec (NOT manual)
   |- Refactor rag_reindex_deal.py
   |- Verify: drift check passes

6. PHASE 5 — Database Migration Governance (parallel)
   |- Dump live schemas FIRST
   |- Diff live vs proposed migrations
   |- Create migration runners
   |- Use portable container discovery (docker compose exec)
   |- Verify: assertion checks all 3 databases

7. PHASE 6 — MCP Contract Formalization (parallel)
   |- Canonicalize to ONE server (archive others)
   |- Create Pydantic schemas for all 12 tools
   |- Add validation + commit contract
   |- Verify: one server file, 12 schemas

8. PHASE 7 — CI Integration & Hardening (depends on ALL above)
   |- Wire all gates (NO || true)
   |- Split validate-all into local/live
   |- Implement spec-freshness-bot (currently placeholder)
   |- Run 6 negative controls (sabotage tests)
   |- Update debt-ledger + documentation
   |- Verify: validate-local exits 0, all NCs pass

9. FINAL VERIFICATION
   |- All phase gates pass
   |- No-Drift Alignment Contract satisfied
   |- Evidence directories populated (no empty files)
   |- Zero untyped contract surfaces remaining
```

---

## SUCCESS CRITERIA

```
BEFORE EXEC-002                           AFTER EXEC-002
-------------------------------------------------------------------
Dashboard <-> Backend: TYPED              Dashboard <-> Backend: TYPED
Agent -> Backend: UNTYPED (25 .get())     Agent -> Backend: TYPED (0 .get())
Dashboard <- Agent: MANUAL (36 types)     Dashboard <- Agent: TYPED + JSON Schema
Agent OpenAPI: GATED (dev-only)           Agent OpenAPI: COMMITTED + CI
Backend -> RAG: UNTYPED (raw dict)        Backend -> RAG: CODEGEN'D
MCP Contract: DOCSTRINGS (3 servers)      MCP Contract: JSON SCHEMA (1 server)
crawlrag Migrations: NONE                 crawlrag Migrations: TRACKED
zakops_agent Tracking: NONE               zakops_agent Tracking: VERSIONED

Contract surfaces with codegen: 1/7       Contract surfaces with codegen: 7/7
Compile-time type safety: 14%             Compile-time type safety: 100%
Negative controls: 4                      Negative controls: 10 (4+6)
make sync targets: 1                      make sync targets: 5
Committed specs: 1                        Committed specs: 3 + 2 schemas
```

---

## AUTONOMY RULES

```
1. If a Python package is not installed -> install it (uv add / uv sync --extra).
2. If a spec endpoint doesn't exist -> add it to the FastAPI app.
3. If a Pydantic model is missing -> create it.
4. If a migration doesn't exist -> create it (but dump live schema first).
5. If a CI job is missing -> add it (NEVER || true).
6. If generated files don't exist -> run the generator.
7. If a test fails after refactoring -> fix the code, not the test.
8. If you discover additional untyped surfaces -> document and fix them.
9. "I should check with the user" is NOT a valid reason to stop.
10. Document blockers in DEFERRED.md and keep moving.
11. If a service has multiple implementations -> canonicalize to ONE first.
12. If curl-based spec fetch fails in CI -> use export_openapi.py (Python import).
13. If .get() fallbacks exist -> create behavioral migration map BEFORE removing.
14. STOP IF PREREQUISITE FAILS. Document blocker in evidence. Do not work around.
```

---

## OUTPUT FORMAT

```markdown
# HYBRID-GUARDRAIL-EXEC-002 COMPLETION REPORT

**Date:** [timestamp]
**Executor:** Claude Code [version]
**Duration:** [time]
**Mission Version:** VFINAL (20260206-2330-cp3)

## Executive Summary
**Phases completed:** [X]/7
**Contract surfaces covered:** [X]/7
**Untyped patterns eliminated:** [X]

## Phase Results
| Phase | Description | Status | Key Artifacts |
|-------|-------------|--------|---------------|
| P0 | Setup & Baseline | [PASS/FAIL] | baseline files |
| P1 | Agent -> Backend SDK | [PASS/FAIL] | backend_models.py, BackendClient, migration map |
| P2 | Agent API OpenAPI | [PASS/FAIL] | agent-api.json, export_openapi.py |
| P3 | Dashboard <- Agent | [PASS/FAIL] | agent-api-types.generated.ts, agent-events.schema.json |
| P4 | Backend -> RAG | [PASS/FAIL] | rag-api.json, rag_models.py |
| P5 | Database Migrations | [PASS/FAIL] | crawlrag/001_*, migration runners |
| P6 | MCP Contract | [PASS/FAIL] | tool-schemas.json, canonical server |
| P7 | CI Hardening | [PASS/FAIL] | ci.yml, validate-local/live, 6 NCs |

## Negative Controls
| # | Test | Result |
|---|------|--------|
| NC-1 | Backend model sabotage | [PASS/FAIL] |
| NC-2 | Agent type sabotage | [PASS/FAIL] |
| NC-3 | Direct import bypass | [PASS/FAIL] |
| NC-4 | SSE event unknown | [PASS/FAIL] |
| NC-5 | Migration drift | [PASS/FAIL] |
| NC-6 | RAG model sabotage | [PASS/FAIL] |

## No-Drift Alignment Contract
- [ ] All spec locations verified
- [ ] All CI gates verified
- [ ] All Makefile targets verified
- [ ] All bridge files verified
- [ ] All ESLint rules verified

## Metrics
| Metric | Before | After |
|--------|--------|-------|
| Untyped .get() in deal_tools.py | 25 | 0 |
| response.json() in deal_tools.py | 8 | 0 |
| Manual event types | 36 | [N] |
| Databases with migration tracking | 1 | 3 |
| Committed OpenAPI specs | 1 | 3 |
| Committed JSON Schemas | 0 | 2 |
| CI contract gates | 1 | 6+ |
| MCP server implementations | 3 | 1 |

## Files Created
[list with paths]

## Files Modified
[list with paths]

## Residual Risks
[from Section C, with detection + mitigation]

## Deferred Items (if any)
[list with reasons + blockers]

## Final Verification
- make validate-local: [exit code]
- make validate-live: [exit code]
- npm run type-check: [exit code]
- npm run lint: [exit code]
- migration-assertion.sh: [exit code]
- Negative controls: [X/6 pass]
- Evidence files: [count] (0 empty)
```

---

*Version: VFINAL*
*Synthesized by: PASS 3 Contrarian Audit (opus46, 20260206-2330-cp3)*
*Inputs: EXEC-002 V1, PASS1 (10 kill shots, 15 missing pieces), PASS2 (18 patches, hardened gates), fresh codebase verification*
*Prerequisite: HYBRID-GUARDRAIL-EXEC-001 COMPLETE + RT-HARDEN-001-V2 COMPLETE*
*Target: Full stack compiler-enforced contract alignment*
*Phases: 7 (P1-P7) + setup (P0) + verification*
*Contract surfaces: 7 (up from 1)*
*Negative controls: 10 total (4 existing + 6 new)*
*Stance: Complete the wall. No exceptions. No silent passes. STOP IF prerequisite fails.*
