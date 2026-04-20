# Acceptance Criteria - MathLib Phase 2

## Definition of Done

The task is complete when ALL of the following are true:

### Functional Requirements

#### New Feature: lcm()
- [ ] `lcm(4, 6)` returns `12`
- [ ] `lcm(3, 5)` returns `15`
- [ ] `lcm(12, 8)` returns `24`
- [ ] `lcm(-4, 6)` returns `12` (handles negatives)
- [ ] `lcm(4, -6)` returns `12`
- [ ] `lcm(-4, -6)` returns `12`
- [ ] `lcm(0, 5)` returns `0`
- [ ] `lcm(5, 0)` returns `0`
- [ ] `lcm(0, 0)` returns `0`
- [ ] `lcm` is importable from `mathlib.core`
- [ ] `lcm` is exported from `mathlib` package

### Quality Gates
- [ ] All pytest tests pass (36 total)
- [ ] No new test files created
- [ ] Only `mathlib/` files modified

## Gate Command
```bash
./verify.sh
```

Exit code 0 = PASS, non-zero = FAIL.

## Verification
Run the gate command. If it exits with code 0 and shows "36 passed", the task is complete.
