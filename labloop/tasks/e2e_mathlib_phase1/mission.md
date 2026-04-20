# Mission: MathLib Phase 1 - Fix Bugs and Implement GCD

## Objective
Fix the divide() function bug and implement the gcd() function to make all tests pass.

## Background
MathLib is a simple math library with intentional bugs for E2E testing of the Lab Loop automation system.

## Current State
- Tests are FAILING (14 failed, 13 passed)
- `divide()` uses floor division (`//`) instead of true division (`/`)
- `gcd()` function is missing

## Required Changes

### 1. Fix divide() function in `mathlib/core.py`
**Problem:** Uses floor division `a // b` instead of true division `a / b`
**Fix:** Change line `return a // b` to `return a / b`

Expected behavior after fix:
- `divide(5, 2)` returns `2.5` (not `2`)
- `divide(-3, 2)` returns `-1.5` (not `-2`)
- `divide(7, 2)` returns `3.5` (not `3`)

### 2. Implement gcd() function in `mathlib/core.py`
**Requirement:** Implement Greatest Common Divisor using Euclid's algorithm

Rules:
- Must handle negative inputs (use absolute values)
- `gcd(0, 0)` must return `0` (explicit decision)
- `gcd(a, 0)` returns `abs(a)`
- `gcd(0, b)` returns `abs(b)`

Implementation pattern:
```python
def gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a
```

### 3. Export gcd from `mathlib/__init__.py`
Add `gcd` to the imports and `__all__` list.

## Constraints
- Only modify files in `mathlib/` directory
- Do NOT modify test files
- Keep implementations simple and readable

## Gate Command
```bash
./verify.sh
```

## Success Criteria
All 27 tests must pass (currently 13 pass, 14 fail).
