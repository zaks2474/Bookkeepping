# V-P5.5: Sync-Types Determinism

**Verification ID**: QA-HG-VERIFY-001-V2 / V-P5.5
**Date**: 2026-02-06T08:27Z
**Verdict**: FAIL (sync-types uses LIVE backend, not committed spec)

## Analysis

### How sync-types Works

From `/home/zaks/Makefile` (lines 15-24):

```makefile
sync-types: ## Fetch OpenAPI spec, run codegen, format, typecheck
    @echo "=== Fetching OpenAPI spec ==="
    @curl -sf $(BACKEND_API)/openapi.json -o $(DASHBOARD_ROOT)/openapi.json
    @echo "=== Running codegen ==="
    @cd $(DASHBOARD_ROOT) && npx openapi-typescript openapi.json -o src/lib/api-types.generated.ts
    @echo "=== Formatting ==="
    @cd $(DASHBOARD_ROOT) && npx prettier --write src/lib/api-types.generated.ts 2>/dev/null || true
    @echo "=== Type check ==="
    @cd $(DASHBOARD_ROOT) && npx tsc --noEmit
    @echo "sync-types complete"
```

**Step 1**: `curl -sf $(BACKEND_API)/openapi.json` fetches spec from LIVE backend at `http://localhost:8091/openapi.json`
**Step 2**: Writes fetched spec to `$(DASHBOARD_ROOT)/openapi.json` (overwriting any committed version)
**Step 3**: Runs `openapi-typescript` codegen against the freshly fetched spec
**Step 4**: Runs `prettier` to format the generated TypeScript
**Step 5**: Runs `tsc --noEmit` to type-check

### Committed OpenAPI Specs Found

Two OpenAPI JSON files exist in the repository:

1. **`/home/zaks/zakops-agent-api/apps/dashboard/openapi.json`**
   - This is the OUTPUT of `make sync-types` (gets overwritten each run)
   - Contains the full OpenAPI 3.1.0 spec for ZakOps API v1.0.0
   - Exported timestamp: `2026-01-19T21:06:07.998922`
   - Very large file (single-line JSON, 25907+ tokens)

2. **`/home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json`**
   - This is the PROTECTED contract spec (per CLAUDE.md)
   - OpenAPI 3.1.0, ZakOps API v1.0.0
   - Separate from the dashboard copy

### Determinism Issue

The `sync-types` target is **non-deterministic** in CI-like contexts because:

1. It depends on the **live backend** being running and accessible at `$(BACKEND_API)/openapi.json`
2. The output changes whenever the backend's OpenAPI spec changes
3. If the backend is down, `curl -sf` will fail silently (`-f` flag = fail silently on HTTP errors)
4. Different environments may have different backend states, producing different types

### What Would Be Deterministic

A deterministic approach would use the committed spec at `packages/contracts/openapi/zakops-api.json`:
```makefile
# Hypothetical deterministic version (NOT what exists):
@cp packages/contracts/openapi/zakops-api.json $(DASHBOARD_ROOT)/openapi.json
```

### validate-all Also Uses Live Backend

The `validate-all` Makefile target (line 69) includes `sync-types` as a dependency:
```makefile
validate-all: infra-check sync-types validate-rag-routing scan-evidence-secrets validate-enforcement
```

This means `make validate-all` also fetches from the live backend.

## Conclusion

`sync-types` is NOT deterministic. It fetches the OpenAPI spec from the live backend (`http://localhost:8091/openapi.json`) at runtime rather than using the committed contract spec at `packages/contracts/openapi/zakops-api.json`. This means:

- CI cannot run `sync-types` without a live backend
- Two developers with different backend states get different generated types
- There is no mechanism to detect drift between the committed contract and the live backend's spec during type generation
