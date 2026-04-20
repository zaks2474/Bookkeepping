# NC-4: PROMISE.ALL REGRESSION
Date: 2026-02-08

## Pre-Sabotage State
hq/page.tsx contains 2 occurrences of `Promise.allSettled`
Backup created at /tmp/qa-nc4-backup.tsx

## Sabotage Applied
`sed -i 's/Promise\.allSettled/Promise.all/g'` on hq/page.tsx
Changed allSettled → all (2 replacements)

## Gate Result
Ran: `npx tsc --noEmit`
- EXIT_CODE=2 (TypeScript compilation FAILED)
- 18 type errors detected in hq/page.tsx:
  - `.status` property does not exist on resolved types (allSettled returns PromiseSettledResult[] with .status/.value/.reason; Promise.all returns T[])
  - `.value` property does not exist
  - `.reason` property does not exist
  - Object possibly null comparisons

**Gate DETECTED the regression.** TypeScript's type system catches the allSettled→all
switch because the return type changes from PromiseSettledResult<T>[] to T[].

## Revert
Restored from backup: `cp /tmp/qa-nc4-backup.tsx .../hq/page.tsx`
Verified: `grep -c allSettled` returns 2

## Post-Revert State
`npx tsc --noEmit` passes (EXIT_CODE=0)

**RESULT: PASS** (TypeScript catches Promise.all/allSettled type mismatch)
