# Test Task: Flaky Gate Policy

## Purpose
Validate Lab Loop v2.1 flaky gate retry handling.

## Expected Behavior
1. First gate attempt fails (simulated flaky failure)
2. Retry triggers automatically (GATE_RETRY_MAX=2)
3. Second attempt passes
4. Result: PASS with flake_suspected=true

## Validation Criteria
- `history/gate_attempt_1.log` exists with failure message
- `history/gate_attempt_2.log` exists with success message
- `artifacts/gate_attempts.json` contains:
  - attempts >= 2
  - flake_suspected == true
  - final_exit_code == 0
