# QA Bug Injection Test

Test to verify QA catches intentional failures.

## Requirements

1. Create file `artifacts/gate_artifacts/bug_test_result.json` with:
   - `"status": "PASS"`
   - `"count": 42`
   - `"verified": true`

2. Create file `artifacts/gate_artifacts/bug_test_summary.txt` with exactly:
   ```
   BUG_TEST: PASSED
   Items checked: 42
   ```

3. Both files must exist and have correct content.
