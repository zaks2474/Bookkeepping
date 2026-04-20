# NC-2: CONTRACT DRIFT (Backend Types)
Date: 2026-02-08

## Pre-Sabotage State
api-types.generated.ts: clean (matches committed spec)

## Sabotage Applied
Appended "// NC-2 SABOTAGE" to apps/dashboard/src/lib/api-types.generated.ts

## Gate Result
Ran: `make sync-types`
- openapi-typescript regenerated the file from zakops-api.json spec
- `git diff --exit-code apps/dashboard/src/lib/api-types.generated.ts` returned EXIT_CODE=0
- Sabotage was completely obliterated by regeneration

**Gate DETECTED and FIXED the drift.**

## Revert
`git checkout` not needed (sync-types already cleaned it), but confirmed clean state.

## Post-Revert State
File matches committed spec. No diff.

**RESULT: PASS** (sync-types obliterates any manual edits to generated types)
