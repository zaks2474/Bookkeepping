# Test Task: Spec Oracle

## Purpose
Validate Lab Loop v2.1 SPEC_CHECK_CMD functionality.

## Expected Behavior
1. Gate always passes
2. Spec check fails until marker file is created
3. Builder must create `.spec_marker` file
4. After file creation: cycle PASS

## Builder Action Required
Create file `tasks/_test_spec_oracle/.spec_marker` with content:
```json
{ "status": "compliant" }
```

## Validation Criteria
- Gate passes but cycle FAILs when spec check fails
- `artifacts/spec_check.json` shows passed=false initially
- After Builder fix: passed=true
- `history/spec_check_cycle_*.log` captures output
