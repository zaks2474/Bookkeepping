# QA-HG-VERIFY-002 Verification Report
Date: 2026-02-06
Executor: QA Verification Agent (Claude Opus 4.6)

## Summary
- **Total Checks**: 29
- **PASS**: 18
- **FAIL**: 5
- **CONDITIONAL PASS**: 3
- **WARN**: 2
- **CANNOT_VERIFY**: 1

---

## Phase 1: Agent -> Backend SDK

| Check | Description | Result | Value | Verdict |
|-------|-------------|--------|-------|---------|
| V-P1.1 | datamodel-code-generator==0.26.3 in pyproject.toml | `codegen = ["datamodel-code-generator==0.26.3"]` | Exact match | **PASS** |
| V-P1.2 | backend_models.py > 100 lines | 594 lines | 594 > 100 | **PASS** |
| V-P1.3 | `from app.schemas.backend_models import *` prints OK | `OK` | Import succeeds | **PASS** |
| V-P1.4 | Codegen idempotency (run twice, diff) | Timestamp-only diff (line 3) | Expected behavior | **CONDITIONAL PASS** |
| V-P1.5 | `make sync-backend-models && git diff --exit-code` | exit 0 | No drift | **PASS** |
| V-P1.6 | async def count >= 5 in backend_client.py | 5 | 5 >= 5 | **PASS** |
| V-P1.7 | backend_models imports in backend_client.py | `from app.schemas.backend_models import (` | Present | **PASS** |
| V-P1.8 | Behavioral migration map exists in builder evidence | 96-line map at HYBRID-GUARDRAIL-EXEC-002/evidence/phase1-agent-backend-sdk/behavioral-migration-map.md | Found | **PASS** |
| V-P1.9 | response.json() count in deal_tools.py == 0 | **8** | 8 occurrences at lines 238,323,484,568,623,791,889,1134 | **CRITICAL FAIL** |
| V-P1.10 | .get( count in deal_tools.py == 0 | **39** | 39 occurrences (includes HTTP .get(), ContextVar .get(), and dict .get()) | **CRITICAL FAIL** |
| V-P1.11 | BackendClient usage in deal_tools.py > 0 | **0** | No BackendClient usage found | **FAIL** |

### Phase 1 Analysis
The codegen pipeline (V-P1.1 through V-P1.8) is solid. However, the behavioral migration from raw HTTP calls to typed BackendClient has NOT been executed in `deal_tools.py`. The file still uses raw `httpx` calls with `response.json()` and manual dict `.get()` access. The migration map (V-P1.8) was created but the actual migration was not applied.

---

## Phase 2: Agent API OpenAPI Spec

| Check | Description | Result | Value | Verdict |
|-------|-------------|--------|-------|---------|
| V-P2.1 | export_openapi.py exists | EXISTS | File present | **PASS** |
| V-P2.2 | No network calls in export_openapi.py | 0 | No curl/requests/urllib | **PASS** |
| V-P2.3 | export_openapi.py outputs >= 18 paths | Script fails: db error (local) / missing dotenv (container) | Cannot run | **FAIL** |
| V-P2.5 | agent-api.json paths count | 28 | Committed spec has 28 paths | **PASS** |
| V-P2.6 | agent-api.json schemas count | 22 | 22 schemas | **PASS** |
| V-P2.7 | Canonical JSON (jq -S sorted == original) | 0 diff lines | Already canonical | **PASS** |
| V-P2.8 | Makefile has update-agent-spec/check-agent-contract-drift | 2 | Both targets present | **PASS** |

### Phase 2 Analysis
The committed spec (agent-api.json) is well-formed with 28 paths and 22 schemas in canonical JSON. However, the export_openapi.py script cannot run outside Docker (db dependency) and fails inside the container (missing dotenv module). The spec may have been generated once and committed, but the regeneration pipeline is broken.

---

## Phase 3: Dashboard <- Agent Codegen

| Check | Description | Result | Value | Verdict |
|-------|-------------|--------|-------|---------|
| V-P3.1 | Split-brain: agent-activity.ts AND execution-contracts.ts exist | Both exist (125 + 584 lines) | Legacy files persist | **WARN** |
| V-P3.2 | agent-api-types.generated.ts line count | 2229 lines | Substantial generated file | **PASS** |
| V-P3.3 | agent-events.schema.json exists | MISSING | File not found | **WARN** |
| V-P3.4 | agent-api.ts bridge file exists | EXISTS | Present | **PASS** |
| V-P3.5 | No direct imports of generated file | NO_DIRECT_IMPORTS | All imports go through bridge | **PASS** |
| V-P3.6 | ESLint rule blocks direct imports | Rule present with EXEC-002 message | Enforced | **PASS** |

### Phase 3 Analysis
The codegen pipeline is healthy: 2229-line generated types, a bridge file (agent-api.ts), ESLint enforcement preventing direct imports. Two concerns: (1) Legacy files (agent-activity.ts, execution-contracts.ts) still exist alongside the generated types - potential split-brain; (2) agent-events.schema.json is missing from packages/contracts/events/.

---

## Phase 4: Backend -> RAG Contract

| Check | Description | Result | Value | Verdict |
|-------|-------------|--------|-------|---------|
| V-P4.1 | Zaks-llm export_openapi.py exists | EXISTS | File present | **PASS** |
| V-P4.2 | rag-api.json paths count | 6 | 6 paths | **PASS** |
| V-P4.3 | rag_models.py line count | 32 lines | Small but present | **CONDITIONAL PASS** |
| V-P4.5 | RAGClient/rag_models usage in rag_reindex_deal.py | **0** | No typed client usage | **FAIL** |
| V-P4.7 | sync-rag-models in Makefile | 3 | Makefile target present | **PASS** |

### Phase 4 Analysis
The RAG contract infrastructure exists (spec, codegen target, models file), but the behavioral migration has not been applied to rag_reindex_deal.py. The executor still uses raw HTTP calls rather than the typed RAGClient.

---

## Critical Findings Summary

### CRITICAL FAILS (Blockers)
1. **V-P1.9**: `deal_tools.py` has 8 `response.json()` calls (should be 0) -- raw JSON parsing instead of typed models
2. **V-P1.10**: `deal_tools.py` has 39 `.get()` calls -- manual dict access instead of typed attribute access
3. **V-P1.11**: `deal_tools.py` has 0 BackendClient references -- migration to typed SDK not applied

### FAILS (Non-Critical)
4. **V-P2.3**: `export_openapi.py` cannot execute (broken pipeline)
5. **V-P4.5**: `rag_reindex_deal.py` has 0 typed RAGClient usage (migration not applied)

### WARNINGS
6. **V-P3.1**: Legacy type files coexist with generated types (split-brain risk)
7. **V-P3.3**: `agent-events.schema.json` missing

### Interpretation
The Hybrid Guardrail infrastructure (codegen pipelines, Makefile targets, specs, ESLint rules, bridge files) is in place and solid. However, the **behavioral migrations** -- converting actual tool code from raw HTTP + dict parsing to typed SDK clients -- have NOT been executed in the two key files:
- `apps/agent-api/app/core/langgraph/tools/deal_tools.py` (Phase 1)
- `src/actions/executors/rag_reindex_deal.py` (Phase 4)

The migration map for deal_tools.py exists (V-P1.8) but was never applied.
