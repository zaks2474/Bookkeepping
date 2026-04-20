# HYBRID-GUARDRAIL-EXEC-001 Implementation Report

**Date**: 2026-02-06
**Executor**: Opus 4.6
**Status**: COMPLETE — All 8 phases PASS
**Mission**: Replace reactive bash schema-diffing with compiler-enforced codegen (Hybrid Guardrail)

---

## Executive Summary

Replaced 3,369 lines of V4 bash validation scripts with a 967-line V5 infrastructure plus `openapi-typescript` codegen. The dashboard now gets its API types directly from the backend OpenAPI spec via `make sync-types`, eliminating an entire class of schema drift bugs at compile time. A feature scaffolder generates complete vertical slices (7 files) from YAML specs.

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Setup & path discovery | PASS |
| 1 | POC — openapi-typescript handles Pydantic v2 | PASS |
| 2 | Codegen pipeline (`make sync-types`) | PASS |
| 3 | Schema migration (hybrid types/api.ts) | PASS |
| 4 | V4 slim — 3,369 → 967 lines (71% reduction) | PASS |
| 5 | CI gate + correlation ID + CLAUDE.md V5 | PASS |
| 6 | Golden payloads + RAG routing re-verify | PASS |
| 7 | Documentation cutover | PASS |
| 8 | Feature scaffolder + 2 pilot features | PASS |

---

## Phase 0: Setup & Path Discovery

Identified all relevant file paths, confirmed backend serves OpenAPI at `/openapi.json`, dashboard at `zakops-agent-api/apps/dashboard`, and existing V4 scripts in `tools/infra/`.

---

## Phase 1: POC — GO/NO-GO Gate

**Question**: Can `openapi-typescript` handle Pydantic v2's `anyOf`-with-null pattern?

**Result**: YES — PROCEED.
- openapi-typescript v7.10.1 correctly emits `| null` unions
- 127 `| null` unions generated from 90 nullable Pydantic fields
- 85.2% endpoint coverage (75/88 backend endpoints)
- OpenAPI 3.1.0 spec with Pydantic v2's native JSON Schema output

---

## Phase 2: Codegen Pipeline

**Created**: `make sync-types` target

Pipeline: `curl OpenAPI spec` → `openapi-typescript` codegen → `prettier` format → `tsc --noEmit`

- Execution time: ~100ms
- Output: `src/lib/api-types.generated.ts` (auto-generated, do not edit)
- Also created `tools/infra/generate-preflight.sh` for Claude context bundling

**Files created**:
- `Makefile` target: `sync-types`
- `tools/infra/generate-preflight.sh`

---

## Phase 3: Schema Migration

**Approach**: Hybrid bridge pattern — generated base types + manual refinements.

Rewrote `types/api.ts` to:
1. Import generated types from `api-types.generated.ts`
2. Derive 11 dashboard types from generated base types
3. Keep manual string literal unions and nested object interfaces where codegen output was too broad

**Key discovery**: `src/lib/api-schemas.ts` (500 lines of hand-written Zod schemas) had **zero imports** anywhere in the codebase — pure dead code. Deleted entirely.

**Files modified**: `types/api.ts`
**Files deleted**: `src/lib/api-schemas.ts` (500 lines)

---

## Phase 4: V4 Slim

Target: reduce V4 infrastructure scripts from 3,369 lines to <1,000.

### Scripts deleted (1,317 lines)
| Script | Lines | Reason |
|--------|-------|--------|
| `schema-diff.sh` | 650 | Replaced by `tsc --noEmit` |
| `detect-phantom-endpoints.sh` | 204 | Codegen covers endpoint existence |
| `dashboard-network-capture.sh` | 302 | Was curl-based probe, not needed |
| `sse-validation.sh` | 161 | SSE not implemented, informational only |

### Scripts archived (396 lines)
| Script | Lines | Reason |
|--------|-------|--------|
| `extract-contracts.sh` | 222 | Codegen replaces schema diffing |
| `openapi-discovery.sh` | 109 | `sync-types` fetches OpenAPI directly |
| `capture-auth-state.sh` | 65 | One-time utility, not recurring |

### Scripts slimmed (kept core, removed verbose logging)
| Script | Before | After |
|--------|--------|-------|
| `discover-topology.sh` | 426 | 107 |
| `db-assertion.sh` | 283 | 57 |
| `migration-assertion.sh` | 200 | 56 |

### Makefile cleanup
- Removed 8 dead targets: `validate-schema-diff`, `validate-cross-layer`, `detect-phantom-endpoints`, `validate-dashboard-network`, `validate-sse`, `infra-contracts`, `infra-contracts-write`, `infra-openapi`
- Updated `validate-all` composite target for V5
- Version label: "V5 — Hybrid Guardrail"

**Result**: 3,369 → 967 lines (71% reduction)

---

## Phase 5: CI Integration + Protocol Update

### P5.1: CI Workflow
Created `.github/workflows/type-sync.yml` with 4 gates:
1. **Codegen drift**: regenerate types, `git diff --exit-code` (fails if types stale)
2. **tsc compilation**: `npx tsc --noEmit`
3. **Legacy import check**: `grep -r "api-schemas"` must find zero hits
4. **Zod ceiling**: manual `z.object` count must stay ≤ 46

### P5.2: Zod Ceiling
Counted 46 manual `z.object` occurrences — set as CI ceiling. Any new Zod schema must be justified or codegen-derived.

### P5.3: Correlation ID
TraceMiddleware already existed but only echoed correlation IDs when provided. Fixed to auto-generate `uuid4()` when absent. Every request now returns `X-Correlation-ID` in response headers.

**Files modified**: `zakops-backend/src/api/shared/middleware/trace.py` (2-line change)

### P5.4: CLAUDE.md V5
Replaced 38-line V4 Infrastructure Awareness Protocol with 8-line V5 version:
- Pre-task: `make sync-types` + read `PREFLIGHT.md`
- Post-task: `make sync-types && tsc --noEmit`
- Cross-layer changes: change Pydantic model → `make sync-types` → fix compile errors → done

---

## Phase 6: Hardening + Golden Payloads

### P6.1: Golden Payloads
Captured real API responses for regression testing:
| Entity | File | Size |
|--------|------|------|
| Deals | `golden/deals.json` | 9,398 bytes |
| Actions | `golden/actions.json` | 3,243 bytes |
| Events | `golden/events.json` | 23 bytes |
| Quarantine | `golden/quarantine.json` | 1,339 bytes |

### P6.2: RAG Routing Re-verification
DB ground truth (25 deals) matches Backend API (25 deals). PASS.

### P6.3: Secret Scan
Evidence directory clean — no leaked credentials. PASS.

### P6.4: Migration Completion
- Legacy imports of `api-schemas`: 0
- Migrated types in `types/api.ts`: 11

---

## Phase 7: Documentation Cutover

Updated 3 operational documents:
- **SERVICE-CATALOG.md**: Added Backend, Dashboard, Infrastructure Validation sections
- **RUNBOOKS.md**: Added "Sync Dashboard Types", "Troubleshoot Codegen Pipeline", "Run Full Infrastructure Validation" runbooks
- **CHANGES.md**: Full mission record

Final `make validate-all`: EXIT 0.

---

## Phase 8: Feature Scaffolder

### Scaffolder CLI
- Location: `tools/scaffolder/new-feature.py`
- Usage: `make new-feature NAME=feature_name` or `make new-feature-spec SPEC=features/spec.yaml`
- Accepts YAML feature sheets for contract-first development

### Generated Files per Feature (7 files)

| Layer | File | Description |
|-------|------|-------------|
| Backend | `routers/models/{feature}.py` | Pydantic request/response models |
| Backend | `routers/{feature}.py` | FastAPI router with TODO placeholder |
| Backend | `tests/integration/test_{feature}.py` | Integration test skeleton |
| Dashboard | `src/lib/{feature}-api.ts` | API function (native `fetch`) |
| Dashboard | `src/hooks/use{Pascal}.ts` | React Query hook (method-aware) |
| Dashboard | `tests/{feature}.spec.ts` | Playwright E2E test skeleton |
| Contract | `features/{feature}.yaml` | Feature sheet |

### Action Registry
Created `src/lib/action-registry.ts` mapping 30+ UI actions to API endpoints. Enables dead-UI detection and endpoint validation.

### Pilot Features
1. `quarantine_delete` — DELETE `/api/quarantine/bulk`
2. `deals_bulk_delete` — DELETE `/api/deals/bulk`

Both compile cleanly: `tsc --noEmit` EXIT 0.

### Scaffolder Bugs Fixed
- Changed from private `apiFetch` to native `fetch` with `credentials: 'include'`
- Inline response types instead of importing from `types/api.ts`
- Method-aware hook function naming (e.g., `deleteQuarantineDelete` not `getQuarantineDelete`)

---

## Files Inventory

### Created
| File | Purpose |
|------|---------|
| `tools/scaffolder/new-feature.py` | Feature scaffolder CLI |
| `src/lib/action-registry.ts` | UI action → endpoint mapping |
| `src/lib/api-types.generated.ts` | Auto-generated OpenAPI types |
| `.github/workflows/type-sync.yml` | CI codegen drift gate |
| `tools/infra/generate-preflight.sh` | Claude context bundle |
| `golden/*.json` | 4 golden payload files |
| `features/*.yaml` | 3 feature sheet specs |
| 14 pilot scaffolded files | Backend + Dashboard for 2 features |

### Modified
| File | Change |
|------|--------|
| `Makefile` | V4 → V5, removed 8 targets, added scaffolder targets |
| `types/api.ts` | Hybrid bridge pattern (imports from generated) |
| `trace.py` | Auto-generate X-Correlation-ID |
| `validate-enforcement.sh` | Updated for V5 targets |
| `discover-topology.sh` | 426 → 107 lines |
| `db-assertion.sh` | 283 → 57 lines |
| `migration-assertion.sh` | 200 → 56 lines |
| `.claude/CLAUDE.md` | 38 → 8 line protocol |
| `SERVICE-CATALOG.md` | Added 3 sections |
| `RUNBOOKS.md` | Added 3 runbooks |

### Deleted / Archived
| File | Lines | Disposition |
|------|-------|-------------|
| `api-schemas.ts` | 500 | Deleted (dead code) |
| `schema-diff.sh` | 650 | Deleted |
| `detect-phantom-endpoints.sh` | 204 | Deleted |
| `dashboard-network-capture.sh` | 302 | Deleted |
| `sse-validation.sh` | 161 | Deleted |
| `extract-contracts.sh` | 222 | Archived |
| `openapi-discovery.sh` | 109 | Archived |
| `capture-auth-state.sh` | 65 | Archived |

**Total removed**: 2,213 lines of bash + 500 lines of dead TypeScript

---

## Key Metrics

| Metric | Before (V4) | After (V5) | Change |
|--------|-------------|------------|--------|
| Infra script lines | 3,369 | 967 | -71% |
| Schema validation approach | Bash diffing | Compiler (`tsc`) | Eliminated class of bugs |
| Type sync time | N/A | ~100ms | New capability |
| Zod schemas (manual) | 500 lines | 46 occurrences (ceiling) | Codegen replaces new schemas |
| Makefile targets | 20+ | 14 | Removed 8 dead targets |
| CLAUDE.md protocol | 38 lines | 8 lines | -79% |
| CI gates | 0 | 4 | Drift, tsc, legacy, Zod ceiling |
| Feature scaffold time | Manual | `make new-feature` | 7 files auto-generated |

---

## Verification

```
$ make validate-all
Topology discovered
DB assertions passed
Migration state verified: 024
MANIFEST AGE GATE PASSED
✅ sync-types complete
RAG ROUTING PROOF PASSED
✅ EVIDENCE SECRET SCAN PASSED
ENFORCEMENT GATE AUDIT PASSED: All mechanisms active (7/7)

══════════════════════════════════════════════════════════════
  FULL SYSTEM VALIDATION COMPLETE (V5 — Hybrid Guardrail)
══════════════════════════════════════════════════════════════
```

---

## Evidence

- Phase 8 gate: `artifacts/infra-awareness/evidence/phase8-scaffolder/phase8_gate.md`
- Golden payloads: `zakops-agent-api/apps/dashboard/golden/`
- Feature specs: `features/quarantine_bulk_delete.yaml`, `features/deals_bulk_delete.yaml`
- CI workflow: `.github/workflows/type-sync.yml`
- Change log: `bookkeeping/CHANGES.md`
