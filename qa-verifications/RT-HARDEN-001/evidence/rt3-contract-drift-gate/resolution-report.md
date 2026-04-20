# RT3 Contract Drift Gate — Resolution Report

**Date**: 2026-02-06
**Task**: RT-HARDEN-001 / FIX 3 (RT3)

## Actions Taken

### 1. Created export_openapi.py (deterministic version)
- **File**: `/home/zaks/zakops-backend/scripts/export_openapi.py`
- Replaced existing feature-rich version with deterministic `sort_keys=True` output
- Script can generate spec from FastAPI app without starting server

### 2. Created spec-freshness-bot workflow
- **File**: `/home/zaks/zakops-agent-api/.github/workflows/spec-freshness-bot.yml`
- Runs daily at 06:00 UTC (cron: '0 6 * * *')
- Also supports manual trigger (workflow_dispatch)

### 3. Drift Check Results

#### Pre-resolution
- **Status**: DRIFT DETECTED
- **Diff size**: 4765 lines
- **Nature**: New schemas (ActionSearchResponse, ActionSearchResult, etc.), new/modified endpoints, updated response models
- **Evidence**: `spec-drift-diff.txt`

#### Resolution
- Ran `make update-spec` -- pulled live spec from backend (port 8091)
- Ran `make sync-types` -- regenerated TypeScript types (openapi-typescript 7.10.1, 92.1ms)
- Ran `make check-contract-drift` -- PASS (committed spec matches live backend)
- Ran `npx tsc --noEmit` -- PASS (no compilation errors)

#### Post-resolution
- **Status**: NO DRIFT
- Committed spec now matches live backend
- TypeScript types regenerated and compile cleanly

## Files Modified
1. `/home/zaks/zakops-backend/scripts/export_openapi.py` (overwritten)
2. `/home/zaks/zakops-agent-api/.github/workflows/spec-freshness-bot.yml` (created)
3. `/home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json` (updated from live)
4. `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-types.generated.ts` (regenerated)

## Evidence Files in This Directory
- `live-spec-canonical.json` — canonical form of live spec (pre-resolution snapshot)
- `committed-spec-canonical.json` — canonical form of committed spec (pre-resolution snapshot)
- `spec-drift-diff.txt` — full diff showing 4765 lines of drift
- `drift-check-report.md` — initial drift detection report
- `resolution-report.md` — this file
