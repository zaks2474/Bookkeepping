# QA Validation Plan: Lab Loop Optimizations

**Objective:** Verify that the "Contrarian Optimizations" (Token Economy, Metrics, Smart Stuck) are functioning correctly and safely.

## 1. Validation Gates

### Gate 1: Syntax & Safety Check
**Command:** `bash -n /home/zaks/bookkeeping/labloop/bin/labloop.sh`
**Criteria:** Exit code 0 (No syntax errors).

### Gate 2: Dry-Run Mechanics
**Command:** `labloop run labloop_selftest --dry-run`
**Criteria:**
- Script runs to completion (Exit code 0).
- `metrics_summary.json` (or constituent txt files) are NOT created (dry-run shouldn't produce real timing metrics, or should produce mock ones). *Correction based on patch: Dry run bypasses real execution so metrics might be 0 or missing, which is fine.*
- **Crucial:** Dry run must NOT trigger "STUCK" logic even if run multiple times.

### Gate 3: Live Cycle Metrics Verification
**Command:** Create a dummy task `test_metrics` and run 1 cycle.
`labloop new test_metrics --repo /tmp --gate "true"`
`labloop run test_metrics --max-cycles 1`
**Criteria:**
- Check for existence of:
    - `tasks/test_metrics/_builder_duration.txt`
    - `tasks/test_metrics/_gate_duration.txt`
    - `tasks/test_metrics/_qa_duration.txt`
- Values should be integers > 0.

### Gate 4: Condensed Prompt Verification
**Command:** Inspect `tasks/test_metrics/_bundle.txt` (after a run > cycle 1).
**Criteria:**
- If `BUNDLE_MODE=condensed` (default), the file should **NOT** contain the full text of `mission.md` if it's large. It should show the truncated version. *Note: Use a multi-line mission to test this.*

### Gate 5: Smart Stuck Logic
**Test:**
1. Manually create a `QA_REPORT.json` in a task dir.
2. Run `labloop.sh` logic (or a test harness sourcing it) calling `check_stuck`.
3. Ensure it returns 1 (Not Stuck).
4. Repeat 2 more times (total 3).
5. Ensure it returns 0 (Stuck) only on the Nth attempt (default 3).

## 2. Regression Testing
- Run existing `e2e_mathlib_phase1` task (if environment allows) to ensure logic didn't break core functionality.

## 3. Success Artifacts
After validation, the following must exist:
- `/home/zaks/bookkeeping/labloop/bin/labloop.sh` (Patched & Executable)
- Validation logs showing successful metric capture.