# Mission: Lab Loop v2 Enhancements — Flake Policy + Spec Oracle + Prompt Evals

## Goal
Enhance Lab Loop with three capabilities while remaining backwards-compatible:

(4) Flaky Gate Policy:
- Add optional retry handling for flaky gate failures (and optionally flaky passes).
- Capture and preserve evidence for every attempt (first failure, retries, final outcome).
- Mark runs as "flake suspected" when a retry leads to PASS.

(5) Spec Oracle Stage:
- Add an optional SPEC_CHECK_CMD that runs independently from GATE_CMD.
- SPEC_CHECK_CMD must be run every cycle (when configured) and must be included in the QA bundle.
- PASS is not allowed if SPEC_CHECK_CMD fails.

(7) Prompt-Evals (Behavior Regression Harness):
- Add optional EVAL_CMD (or equivalent) to run behavioral tests / prompt evals.
- EVAL_CMD runs after GATE_CMD passes and after SPEC_CHECK_CMD passes (if configured).
- EVAL_CMD must produce a machine-readable artifact (JSON) and exit nonzero on failure.

## Hard Constraints (Non-negotiable)
1) DO NOT edit or update the guide version.
   - Specifically: DO NOT modify /home/zaks/bookkeeping/docs/labloop-guide.md if it is designated v2.
   - If docs are needed, write a new addendum file:
     /home/zaks/bookkeeping/docs/labloop-addendum-v2.x.md
     and/or release notes:
     /home/zaks/bookkeeping/docs/labloop-release-notes-v2.x.md
2) Backwards compatibility:
   - Existing tasks that only define REPO_DIR + GATE_CMD must continue to run unchanged.
   - New capabilities must be opt-in via task config.
3) Keep QA schema stable:
   - You may extend schemas with OPTIONAL fields only.
   - Do not introduce new required properties that break existing tasks.
4) Safety:
   - QA remains read-only.
   - Builder may modify only within the repo and task workspace.

## Implementation Scope
Repo: /home/zaks/bookkeeping/labloop

### A) Flaky Gate Policy (Enhancement 4)
Add support for these OPTIONAL task config variables (in tasks/<task>/config.env):
- GATE_RETRY_MAX (default 0)
- GATE_RETRY_DELAY_SEC (default 2)
- GATE_RETRY_ON_REGEX (default empty)
- GATE_RETRY_OFF_REGEX (default empty)
- GATE_RETRY_TIMEOUT_SEC (default unset / none)
- GATE_RETRY_MODE = "on_fail" | "always" (default "on_fail")

Behavior:
- Run GATE_CMD normally.
- If it fails and GATE_RETRY_MAX > 0:
  - Retry up to GATE_RETRY_MAX times
  - Sleep GATE_RETRY_DELAY_SEC between attempts
  - Only retry if:
    - (GATE_RETRY_ON_REGEX is empty OR output matches it) AND
    - (GATE_RETRY_OFF_REGEX is empty OR output does NOT match it)
- Evidence capture:
  - Write attempt logs under TASK_DIR/history/ as:
    gate_attempt_1.log, gate_attempt_2.log, ... gate_attempt_N.log
  - Write a short summary file:
    TASK_DIR/artifacts/gate_attempts.json
    containing: attempts, exit_codes, flake_suspected boolean, final_exit_code
- If final attempt passes after earlier failure → set flake_suspected=true.

### B) Spec Oracle (Enhancement 5)
Add support for OPTIONAL task config variable:
- SPEC_CHECK_CMD (default empty)
- SPEC_CHECK_TIMEOUT_SEC (default unset / none)
- SPEC_CHECK_REQUIRED = true|false (default true if SPEC_CHECK_CMD is set)

Behavior:
- If SPEC_CHECK_CMD is set:
  - Run SPEC_CHECK_CMD each cycle.
  - Capture output to:
    TASK_DIR/history/spec_check_cycle_<n>.log
  - Capture a summary artifact:
    TASK_DIR/artifacts/spec_check.json with fields:
    { "command": "...", "exit_code": <int>, "passed": <bool> }
- If SPEC_CHECK_REQUIRED is true:
  - Any nonzero exit code is a hard FAIL for the cycle, even if gate passes.

### C) Prompt Evals / Behavioral Tests (Enhancement 7)
Add support for OPTIONAL task config variables:
- EVAL_CMD (default empty)
- EVAL_TIMEOUT_SEC (default unset / none)
- EVAL_REQUIRED = true|false (default true if EVAL_CMD is set)
- EVAL_RESULTS_PATH (default: TASK_DIR/artifacts/eval_results.json)

Behavior:
- If EVAL_CMD is set and GATE_CMD (and SPEC_CHECK_CMD if required) passed:
  - Run EVAL_CMD
  - Capture output to TASK_DIR/history/eval_cycle_<n>.log
  - Require EVAL_RESULTS_PATH to exist and contain valid JSON when EVAL_REQUIRED=true
  - If EVAL_CMD exits nonzero → cycle FAIL

### D) QA bundle changes
Ensure the QA prompt bundle includes:
- gate_attempts.json (if present)
- spec_check.json + spec_check log (if present)
- eval_results.json + eval log (if present)
- final gate_output.log and final gate_rc

### E) Self-tests (must add)
Add new internal tasks under tasks/ that validate all three enhancements:

1) Flake policy test
- A verify script that fails first time, passes second time.
- Configure task with:
  GATE_RETRY_MAX=2
  GATE_RETRY_MODE=on_fail
- Expected: final PASS, flake_suspected=true, all attempt logs present.

2) Spec Oracle test
- Gate always passes.
- Spec check fails unless a file exists.
- Expected: FAIL until Builder creates file, then PASS.
- Ensures SPEC_CHECK_CMD is a real hard gate.

3) Prompt eval test
- Gate passes.
- Eval fails unless a file exists or unless output matches expected JSON.
- Expected: FAIL → Builder fixes → PASS.
- Ensures eval artifacts are produced.

### F) CLI / Status output
Update labloop status/list outputs to show (if available):
- flake_suspected
- spec_check passed/failed
- eval passed/failed

### G) Escalation packet
Ensure escalation zip includes:
- gate_attempts.json + all gate_attempt_*.log
- spec_check.json + last spec log
- eval_results.json + last eval log

## Builder Deliverables
- Code changes implementing A–G
- New tests/tasks added and passing
- Addendum or release notes ONLY (no guide v2 edits), if necessary.

## QA Deliverables
- QA schema remains valid and used
- QA report explicitly checks: flake policy evidence, spec oracle gating, eval gating
- PASS only if all required parts pass.
