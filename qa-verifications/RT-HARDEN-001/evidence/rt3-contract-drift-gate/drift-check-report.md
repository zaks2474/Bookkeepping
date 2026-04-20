# RT3 Contract Drift Gate — Check Report

**Date**: 2026-02-06
**Task**: RT-HARDEN-001 / FIX 3 (RT3)
**Check**: Spec drift between committed OpenAPI contract and live backend

## Sources
- **Committed spec**: `/home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json`
- **Live spec**: `http://localhost:8091/openapi.json`

## Result: DRIFT DETECTED

The canonical diff between the committed spec and the live backend spec is **4765 lines**.

The live backend has diverged significantly from the committed contract. This includes:
- New schemas (ActionSearchResponse, ActionSearchResult, etc.)
- New/modified endpoints
- Updated response models

## Resolution
Running `make update-spec && make sync-types` in the monorepo to pull the live spec
and regenerate TypeScript types.

## Evidence Files
- `live-spec-canonical.json` — canonical (jq -S) form of live spec
- `committed-spec-canonical.json` — canonical (jq -S) form of committed spec
- `spec-drift-diff.txt` — full diff (4765 lines)
- `drift-check-report.md` — this file
