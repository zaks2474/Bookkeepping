# Mission: MathLib Phase 2 - Implement LCM Function

## Objective
Implement the lcm() (Least Common Multiple) function to make all tests pass.

## Background
Phase 1 is complete. The divide() bug is fixed and gcd() is implemented. Now add lcm().

## Current State
- Phase 1 tests pass (27 tests)
- New lcm() tests are failing (9 tests)
- `lcm()` function is missing

## Required Changes

### 1. Implement lcm() function in `mathlib/core.py`
**Requirement:** Implement Least Common Multiple using the formula: `lcm(a, b) = abs(a * b) // gcd(a, b)`

Rules:
- Must handle negative inputs (use absolute values)
- `lcm(0, x)` returns `0` (by convention)
- `lcm(x, 0)` returns `0`
- Use the existing `gcd()` function

Implementation pattern:
```python
def lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)
```

### 2. Export lcm from `mathlib/__init__.py`
Add `lcm` to the imports and `__all__` list.

## Constraints
- Only modify files in `mathlib/` directory
- Do NOT modify test files
- Keep implementations simple and readable

## Gate Command
```bash
./verify.sh
```

## Success Criteria
All 36 tests must pass (27 existing + 9 new lcm tests).
