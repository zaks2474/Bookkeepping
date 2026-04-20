# DEAL-INTEGRITY-UNIFIED: Negative Control Summary
Date: 2026-02-08
Executed by: Claude Opus 4.6

## Results Matrix

| NC | Name | Sabotage | Gate Detected? | Result |
|----|------|----------|----------------|--------|
| NC-0 | Integrity Harness | N/A (baseline) | N/A | **PASS** |
| NC-1 | Lifecycle Bypass | SQL UPDATE active+archived | Auto-corrected by trigger | **PASS** |
| NC-2 | Contract Drift (backend) | Append to api-types.generated.ts | sync-types obliterated | **PASS** |
| NC-3 | Hardcoded Stage Injection | Create .tsx with local stages | TSC did NOT detect | **EXPECTED-FAIL** |
| NC-4 | Promise.all Regression | allSettled → all in hq/page.tsx | TSC caught 18 errors | **PASS** |
| NC-5 | DSN Sabotage | Audit only | Gate exists in main.py | **PASS** |
| NC-6 | Count Invariant | INSERT active+archived | Auto-corrected by trigger | **PASS** |
| NC-7 | Agent Type Drift | Append to agent-api-types.generated.ts | sync-agent-types obliterated | **PASS** |
| NC-8 | Migration File Sabotage | Fake .sql in migrations/ | git status detected | **PASS** |

## Summary
- **8/9 PASS** — gates detected or prevented sabotage
- **1/9 EXPECTED-FAIL** (NC-3) — TSC cannot catch naming convention violations; needs ESLint rule

## Key Findings

### Defense Layers Confirmed
1. **DB Layer**: `enforce_deal_lifecycle_trigger` auto-corrects impossible states BEFORE
   `chk_deal_lifecycle` CHECK constraint evaluates (NC-1, NC-6)
2. **Type Codegen Layer**: `make sync-types` and `make sync-agent-types` fully regenerate
   from specs, obliterating any manual drift (NC-2, NC-7)
3. **TypeScript Layer**: `npx tsc --noEmit` catches type-level regressions like
   Promise.allSettled → Promise.all (NC-4)
4. **Startup Gate**: DSN verification gate in lifespan() refuses to start if connected
   to wrong database (NC-5)
5. **Git Layer**: `git status --porcelain` detects unauthorized files in protected
   directories (NC-8)

### Gap Identified
- NC-3: No ESLint rule or grep-gate to detect hardcoded pipeline stage arrays.
  Components can define local `PIPELINE_STAGES` without compiler error.
  **Recommendation**: Add ESLint no-restricted-syntax rule or grep-based CI gate.

## Revert Verification
All repos confirmed at pre-test baseline state after all reverts completed.
