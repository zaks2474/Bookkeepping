# Deferral Rubric — M-12 Execute vs Defer Decision

## Date: 2026-02-12
## Mission: UI-MASTERPLAN-M12

## Decision Criteria

| # | Criterion | Threshold for Execute | Threshold for Defer |
|---|-----------|----------------------|---------------------|
| 1 | Time budget | Sufficient for 4-phase sweep | Insufficient for Phase 1+ |
| 2 | Complexity of gaps | Gaps are targeted and fixable | Gaps require architectural redesign |
| 3 | M-11 baseline confidence | M-11 complete with passing tests | M-11 incomplete or unstable |
| 4 | Risk of regression | Low — changes are additive (tests + small fixes) | High — accessibility fixes may break layouts |
| 5 | Value of coverage | Core routes lack basic a11y verification | Existing Radix foundation provides adequate baseline |

## Assessment

| # | Criterion | Assessment | Evidence |
|---|-----------|-----------|----------|
| 1 | Time budget | EXECUTE — session has capacity | M-10 and M-11 complete, no blockers |
| 2 | Complexity of gaps | EXECUTE — gaps are targeted | Skip-nav, landmarks, aria-live are additive; Radix handles focus traps |
| 3 | M-11 baseline confidence | EXECUTE — M-11 complete | phase3-gate3-scorecard exists, 25 E2E tests passing |
| 4 | Risk of regression | EXECUTE — low risk | Adding skip-nav/landmarks/attributes doesn't change visual layout |
| 5 | Value of coverage | EXECUTE — no a11y verification exists | Zero accessibility-focused E2E tests in suite |

## Decision

**EXECUTE NOW** — All 5 criteria favor execution.

### Rationale
1. The dashboard has a solid Radix/shadcn foundation but zero accessibility-specific test coverage.
2. Known gaps (skip-nav, landmarks, aria-live) are additive changes with near-zero regression risk.
3. Radix primitives handle focus trapping for Dialog/Sheet/AlertDialog — verification rather than implementation.
4. Time budget is available after M-10/M-11 completion.
5. Adding 3 accessibility E2E test files provides lasting verification value.

### Risk Mitigations
- Re-run key M-11 E2E tests after any remediation
- Keep remediations to discovered blockers only (no feature creep)
- Use deterministic focus assertions (no sleep-only gates)
