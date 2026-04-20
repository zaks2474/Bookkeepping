# NC-3: HARDCODED STAGE INJECTION
Date: 2026-02-08

## Pre-Sabotage State
No qa-nc3-stage-test.tsx file exists.

## Sabotage Applied
Created /apps/dashboard/src/components/qa-nc3-stage-test.tsx with hardcoded:
```tsx
const PIPELINE_STAGES = ['prospecting', 'qualification', 'proposal'];
export default function NC3Test() { return <div>{PIPELINE_STAGES.join(',')}</div>; }
```

## Gate Result
Ran: `npx tsc --noEmit`
- EXIT_CODE=0 (TypeScript compilation passed)
- TSC does NOT catch naming convention violations or hardcoded stage arrays
- The file is valid TypeScript, so tsc has no type error to report

**Gate DID NOT DETECT the sabotage.** This is expected behavior — TSC is a type checker,
not a naming/convention linter. Detection would require a custom ESLint rule or grep-based gate.

## Revert
`rm -f .../qa-nc3-stage-test.tsx` — confirmed file removed.

## Post-Revert State
File does not exist. `npx tsc --noEmit` passes (EXIT_CODE=0).

**RESULT: EXPECTED-FAIL** (TSC cannot detect hardcoded stage arrays; needs ESLint rule)
