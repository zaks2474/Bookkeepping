# Acceptance Criteria - MathLib Phase 1

## Definition of Done

The task is complete when ALL of the following are true:

### Functional Requirements

#### Bug Fix: divide()
- [ ] `divide(5, 2)` returns `2.5` (float, not int)
- [ ] `divide(10, 4)` returns `2.5`
- [ ] `divide(-3, 2)` returns `-1.5`
- [ ] `divide(7, 2)` returns `3.5`
- [ ] `divide(5, 0)` raises `ZeroDivisionError`

#### New Feature: gcd()
- [ ] `gcd(12, 8)` returns `4`
- [ ] `gcd(17, 13)` returns `1`
- [ ] `gcd(100, 25)` returns `25`
- [ ] `gcd(-12, 8)` returns `4` (handles negatives)
- [ ] `gcd(12, -8)` returns `4`
- [ ] `gcd(-12, -8)` returns `4`
- [ ] `gcd(0, 5)` returns `5`
- [ ] `gcd(5, 0)` returns `5`
- [ ] `gcd(0, 0)` returns `0`
- [ ] `gcd` is importable from `mathlib.core`
- [ ] `gcd` is exported from `mathlib` package

### Quality Gates
- [ ] All pytest tests pass (27 total)
- [ ] No new test files created
- [ ] Only `mathlib/` files modified

## Gate Command
```bash
./verify.sh
```

Exit code 0 = PASS, non-zero = FAIL.

## Verification
Run the gate command. If it exits with code 0 and shows "27 passed", the task is complete.
