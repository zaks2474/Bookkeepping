# NC-7: AGENT TYPE DRIFT
Date: 2026-02-08

## Pre-Sabotage State
agent-api-types.generated.ts: clean (matches committed agent-api.json spec)

## Sabotage Applied
Appended "// NC-7 SABOTAGE" to apps/dashboard/src/lib/agent-api-types.generated.ts

## Gate Result
Ran: `make sync-agent-types`
- openapi-typescript regenerated the file from agent-api.json spec in 50.1ms
- `git diff --exit-code apps/dashboard/src/lib/agent-api-types.generated.ts` returned EXIT_CODE=0
- Sabotage was completely obliterated by regeneration

**Gate DETECTED and FIXED the drift.**

## Revert
sync-agent-types already cleaned the file. Confirmed clean state.

## Post-Revert State
File matches committed spec. No diff.

**RESULT: PASS** (sync-agent-types obliterates any manual edits to generated agent types)
