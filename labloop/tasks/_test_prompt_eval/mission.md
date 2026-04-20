# Test Task: Prompt Eval

## Purpose
Validate Lab Loop v2.1 EVAL_CMD functionality.

## Expected Behavior
1. Gate always passes
2. Eval fails until results file is created with valid JSON
3. Builder must create `artifacts/eval_results.json`
4. After file creation: cycle PASS

## Builder Action Required
Create file `tasks/_test_prompt_eval/artifacts/eval_results.json` with content:
```json
{ "passed": true, "tests": 5, "failures": 0 }
```

## Validation Criteria
- Gate passes but cycle FAILs when eval fails
- Eval results file must exist and contain valid JSON
- File must have `passed: true` for success
- `history/eval_cycle_*.log` captures output
