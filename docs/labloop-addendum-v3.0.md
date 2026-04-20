# Lab Loop v3.0 Addendum

**Version:** 3.0.0 (Stabilization Release)
**Date:** 2026-01-24
**Supplement to:** LABLOOP_COMPLETE_GUIDE.md

---

## Overview

Lab Loop v3.0 adds stabilization features to prevent common failures, while maintaining full backwards compatibility with v2.x tasks:

**Stabilization Features (v3.0.0):**
1. **Project Profiles** - `.labloop.yaml` files for per-project settings
2. **Health Check Tool** - `labloop-doctor` for diagnostics and auto-fixing
3. **Auto-Commit Artifacts** - Prevents diff limit violations
4. **Enhanced Preflight** - Python syntax validation, venv detection
5. **Error Recovery** - Automatic recovery for diff_limit, stale_lock, builder_timeout

**Builder Fix (v2.1.4):**
6. **Builder Hang Fix** - Fixed dual-input confusion causing Claude CLI to hang

**Gemini QA Fallback (v2.1.2):**
7. **QA Agent Cascade** - Codex (primary) → Gemini (fallback) → fallback report
8. **Stdin Prompt Delivery** - Large prompts via stdin, not CLI arguments
9. **Condensed Prompts** - ~10KB prompt for Gemini (not full 48KB bundle)
10. **Auto early_exit Field** - Adds missing field to Gemini output

**Stability Fixes (v2.1.1):**
11. **JSON Extraction** - Handle markdown blocks anywhere in output
12. **Agent Timeouts** - 20 min (Builder), 15 min (QA) with fallbacks
13. **Fallback QA Reports** - Auto-generate when Codex fails
14. **Diff Limits** - 1000 lines total, 500 per file
15. **Required early_exit Field** - QA report schema update

**Optional Features (v2.1.0):**
16. **Flaky Gate Policy** - Retry handling for intermittent failures
17. **Spec Oracle** - Independent specification verification
18. **Prompt Evals** - Behavioral regression testing

All features are opt-in. Existing tasks continue to work unchanged.

---

## 1. Flaky Gate Policy

### Purpose
Automatically retry gate commands when transient failures occur (network timeouts, race conditions, external service flakiness).

### Configuration (in `config.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `GATE_RETRY_MAX` | `0` | Maximum retry attempts (0 = no retries) |
| `GATE_RETRY_DELAY_SEC` | `2` | Seconds between retries |
| `GATE_RETRY_ON_REGEX` | (empty) | Only retry if output matches regex |
| `GATE_RETRY_OFF_REGEX` | (empty) | Never retry if output matches regex |
| `GATE_RETRY_MODE` | `on_fail` | `on_fail` or `always` |
| `GATE_RETRY_TIMEOUT_SEC` | (unset) | Timeout per attempt |

### Example

```bash
# config.env - retry up to 3 times on network errors
GATE_RETRY_MAX=3
GATE_RETRY_DELAY_SEC=5
GATE_RETRY_ON_REGEX="(timeout|connection refused|ECONNRESET)"
```

### Evidence Capture

When retries occur, Lab Loop captures:

- `history/gate_attempt_1.log` - First attempt output
- `history/gate_attempt_2.log` - Second attempt output
- ... up to `gate_attempt_N.log`
- `artifacts/gate_attempts.json` - Summary:

```json
{
  "attempts": 2,
  "exit_codes": [1, 0],
  "flake_suspected": true,
  "final_exit_code": 0
}
```

### Flake Detection

If the gate fails on attempt 1 but passes on a subsequent attempt:
- `flake_suspected` is set to `true`
- QA report still shows PASS (final result counts)
- Evidence preserved for investigation

---

## 2. Spec Oracle

### Purpose
Run an independent specification check that must pass in addition to the gate. Useful when:
- Gate tests implementation but spec tests requirements
- External compliance checks are needed
- Separate validation logic shouldn't be in the gate

### Configuration (in `config.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SPEC_CHECK_CMD` | (empty) | Command to run for spec verification |
| `SPEC_CHECK_REQUIRED` | `true` (if cmd set) | Fail cycle if spec check fails |
| `SPEC_CHECK_TIMEOUT_SEC` | (unset) | Timeout for spec check |

### Example

```bash
# config.env - require API spec validation
SPEC_CHECK_CMD="./scripts/validate-openapi-spec.sh"
SPEC_CHECK_REQUIRED=true
```

### Evidence Capture

- `history/spec_check_cycle_N.log` - Output for cycle N
- `artifacts/spec_check.json` - Summary:

```json
{
  "command": "./scripts/validate-openapi-spec.sh",
  "exit_code": 0,
  "passed": true
}
```

### Execution Order

1. Gate runs first
2. If gate passes AND `SPEC_CHECK_CMD` is set:
   - Spec check runs
   - If spec fails, cycle verdict = FAIL
3. Proceed to eval (if configured)

---

## 3. Prompt Evals (Behavioral Regression)

### Purpose
Run behavioral tests or prompt evaluations after gate and spec check pass. Useful for:
- LLM prompt regression testing
- Output quality verification
- Integration behavior validation

### Configuration (in `config.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `EVAL_CMD` | (empty) | Command to run evaluations |
| `EVAL_REQUIRED` | `true` (if cmd set) | Fail cycle if eval fails |
| `EVAL_TIMEOUT_SEC` | (unset) | Timeout for eval |
| `EVAL_RESULTS_PATH` | `artifacts/eval_results.json` | Path to results JSON |

### Example

```bash
# config.env - run prompt evaluations
EVAL_CMD="python eval/run_prompts.py --output artifacts/eval_results.json"
EVAL_REQUIRED=true
EVAL_RESULTS_PATH="artifacts/eval_results.json"
```

### Evidence Capture

- `history/eval_cycle_N.log` - Output for cycle N
- `artifacts/eval_results.json` - Must be valid JSON

### Results Format

The eval command must produce a JSON file. Recommended structure:

```json
{
  "passed": true,
  "tests": 10,
  "failures": 0,
  "results": [
    {"name": "test_greeting", "passed": true},
    {"name": "test_math", "passed": true}
  ]
}
```

### Execution Order

1. Gate must pass
2. Spec check must pass (if configured)
3. Then eval runs
4. If eval fails → cycle FAIL

---

## CLI Updates

### Status Command

```bash
$ labloop status my_task
========================================
Task: my_task
========================================
Status: NOT RUNNING

Gate Attempts:
  Attempts: 2
  Flake Suspected: true
  Final Exit Code: 0

Spec Check:
  Passed: true
  Exit Code: 0

Eval Results:
  Passed: true

History: 3 cycle(s)
```

### List Command

```bash
$ labloop list
========================================
Lab Loop Tasks (v2.1.0)
========================================

TASK_ID                   VERDICT  CYCLE  STATUS   FLAKE  SPEC  EVAL  SUMMARY
-------                   -------  -----  ------   -----  ----  ----  -------
auth_fix                  PASS     3      idle     no     OK    OK    All tests passing
api_migration             FAIL     5      RUN      YES    FAIL  -     Spec check failed
```

Column meanings:
- **FLAKE**: `YES` if flake suspected, `no` if not, `-` if not tracked
- **SPEC**: `OK` if passed, `FAIL` if failed, `-` if not configured
- **EVAL**: `OK` if passed, `FAIL` if failed, `-` if not configured

---

## QA Bundle Updates

The QA bundle now includes these additional artifacts when present:

```
qa_bundle/
├── gate_output.log        # Final gate output
├── gate_rc.txt            # Final exit code
├── gate_attempts.json     # Retry summary (if retries occurred)
├── spec_check.json        # Spec check result (if configured)
├── spec_check_cycle_N.log # Latest spec check output
├── eval_results.json      # Eval results (if configured)
├── eval_cycle_N.log       # Latest eval output
└── ...
```

---

## Escalation Packet Updates

When a task enters STUCK state, the escalation zip includes:

```
escalation_TASK_TIMESTAMP.zip
├── gate_attempt_1.log     # All retry attempts
├── gate_attempt_2.log
├── gate_attempts.json     # Retry summary
├── spec_check.json        # Spec check result
├── spec_check_cycle_N.log # Latest spec output
├── eval_results.json      # Eval results
├── eval_cycle_N.log       # Latest eval output
└── ...
```

---

## Backwards Compatibility

All v2.1 features are opt-in:

| Feature | Active When |
|---------|-------------|
| Flaky Gate Policy | `GATE_RETRY_MAX > 0` |
| Spec Oracle | `SPEC_CHECK_CMD` is set |
| Prompt Evals | `EVAL_CMD` is set |

Tasks with only `REPO_DIR` and `GATE_CMD` work exactly as before.

---

## Self-Test Tasks

Three test tasks are included for validation:

### 1. `_test_flake_policy`
Tests retry handling. Gate fails first attempt, passes second.
- Expected: PASS with `flake_suspected=true`

### 2. `_test_spec_oracle`
Tests spec check blocking. Gate passes but spec fails until fix.
- Expected: FAIL until builder creates marker file

### 3. `_test_prompt_eval`
Tests eval blocking. Gate passes but eval fails until fix.
- Expected: FAIL until builder creates results JSON

---

## Migration from v2.0

No migration required. All v2.0 tasks work without changes.

To adopt new features, add the relevant configuration to your `config.env`:

```bash
# Add flaky gate handling
GATE_RETRY_MAX=2

# Add spec check
SPEC_CHECK_CMD="./validate_spec.sh"

# Add prompt evals
EVAL_CMD="./run_evals.sh"
```

---

## 4. JSON Extraction (v2.1.1 Stability Fix)

### Problem
Claude Code sometimes wraps JSON output in markdown code blocks, and not always at the end of output.

### Solution
The controller now:
1. Detects ```` ```json ```` markers anywhere in the output
2. Extracts content between markers
3. Falls back to raw JSON extraction if no markers found

### Example Handled
```
Some explanation text here...

```json
{"status": "READY_FOR_QA", "changed_files": [...]}
```

More text after the JSON...
```

---

## 5. Agent Timeouts (v2.1.1 Stability Fix)

### Problem
Agents could hang indefinitely on complex tasks or API issues.

### Solution

| Agent | Timeout | On Timeout |
|-------|---------|------------|
| Builder (Claude Code) | 20 minutes | Kill process, log error |
| QA (Codex) | 15 minutes | Generate fallback report, continue |

### Implementation
```bash
# QA with timeout
if timeout 900 /root/.npm-global/bin/codex exec ... ; then
  # Success
else
  # Generate fallback report
fi
```

---

## 6. Fallback QA Reports (v2.1.1 Stability Fix)

### Problem
If Codex times out or produces empty/invalid output, the loop would crash or get stuck.

### Solution
When QA fails:
1. Create a valid fallback QA report
2. Set verdict to FAIL
3. Include error details in blockers
4. Continue the loop

### Fallback Report Structure
```json
{
  "verdict": "FAIL",
  "cycle": N,
  "early_exit": false,
  "summary": "QA agent timed out or failed to produce valid output",
  "blockers": [{
    "severity": "BLOCKER",
    "title": "QA agent failure",
    "details": "Codex failed to produce valid QA report. Exit code: X",
    "recommended_fix": "Check Codex logs and retry"
  }],
  "majors": [],
  "minors": [],
  "spec_compliance": {},
  "next_actions_for_builder": [{
    "priority": 1,
    "severity": "BLOCKER",
    "summary": "Investigate QA failure and retry"
  }],
  "evidence": []
}
```

---

## 7. Diff Limits (v2.1.1 Stability Fix)

### Problem
Large diffs could exhaust context windows, causing failures.

### Solution

| Limit | Old Value | New Value |
|-------|-----------|-----------|
| Max total diff lines | 500 | 1000 |
| Max lines per file | 300 | 500 |

### Implementation
Diffs are truncated with a warning if limits exceeded:
```
[TRUNCATED: Diff too large - showing first 500 lines of 847]
```

---

## 8. Required early_exit Field (v2.1.1 Stability Fix)

### Problem
QA reports missing `early_exit` field caused schema validation failures.

### Solution
The `early_exit` field is now:
1. Required in the QA report schema
2. Set to `false` in fallback reports
3. Set to `false` in dry-run reports

### Usage
Set `early_exit: true` only when QA cannot continue due to a fatal error (e.g., cannot read files, missing dependencies).

---

## E2E Validation Scenario

Before running Lab Loop on production tasks, validate with a deterministic test:

### MathLib Test Scenario

1. Create a simple math library with intentional bugs
2. Run Lab Loop to fix them
3. Expected: PASS in 1-2 cycles

```bash
# Create test scenario
mkdir -p /tmp/mathlib
cat > /tmp/mathlib/math_lib.py << 'EOF'
def divide(a, b):
    return a * b  # Bug: should be a / b

def gcd(a, b):
    pass  # Not implemented
EOF

cat > /tmp/mathlib/test_math.py << 'EOF'
from math_lib import divide, gcd

def test_divide():
    assert divide(10, 2) == 5

def test_gcd():
    assert gcd(12, 8) == 4
EOF

# Create Lab Loop task
labloop new mathlib_test --repo /tmp/mathlib --gate "pytest"

# Write mission
echo "Fix divide() bug and implement gcd() function" > \
  /home/zaks/bookkeeping/labloop/tasks/mathlib_test/mission.md

# Run
labloop run mathlib_test
```

Expected: PASS within 1-2 cycles if Lab Loop is working correctly.

---

## 9. Gemini QA Fallback (v2.1.2)

### Purpose
When Codex is unavailable (rate limits, outages, errors), Lab Loop automatically falls back to Gemini for QA evaluation.

### QA Agent Cascade

```
Codex (primary) → Gemini (fallback) → Fallback Report (last resort)
```

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_CLI_PATH` | `$(which gemini)` | Path to Gemini CLI |
| `GEMINI_TIMEOUT` | `600` | Timeout in seconds (10 min) |
| `GEMINI_API_KEY` | (required) | Google API key |

### How It Works

1. **Codex fails** (timeout, rate limit, invalid output)
2. **Gemini receives condensed prompt** (~10KB instead of 48KB):
   - Gate exit code and last 100 lines of output
   - First 100 lines of Builder report
   - First 80 lines of acceptance criteria
   - JSON schema template
3. **Prompt delivered via stdin** (not CLI argument - fixes shell limit issues)
4. **JSON extracted** from Gemini output with multiple fallback methods
5. **`early_exit` field added** if missing from Gemini output

### Troubleshooting

**"Primary QA agent (codex) failed, trying fallback (gemini)..."**

This is normal behavior. If Gemini also fails:

1. Check `loop.log` for "Gemini prompt size" - should be ~10KB
2. Check "Gemini raw output" for response content
3. Verify `GEMINI_API_KEY` is set
4. Verify Gemini CLI is installed: `which gemini`

**Gemini timing out**

v2.1.2 fixed a bug where the full 142KB prompt was passed as a CLI argument, causing hangs.

**Old (broken):**
```bash
gemini --yolo "$(cat prompt.txt)"  # 142KB arg!
```

**New (fixed):**
```bash
cat prompt.txt | gemini --yolo      # stdin delivery
```

### Evidence Capture

When Gemini runs, these are logged:
- Prompt size in bytes
- Raw output (first 500 chars)
- Extracted JSON
- Any parsing errors

---

## Version History

- **v2.1.2** (2026-01-24): Gemini QA fallback (stdin delivery, condensed prompts, auto early_exit)
- **v2.1.1** (2026-01-24): Stability fixes (JSON extraction, timeouts, fallback reports, diff limits, early_exit)
- **v2.1.0** (2026-01-23): Flaky Gate Policy, Spec Oracle, Prompt Evals
- **v2.0.0** (2026-01-23): Initial v2 release with safety guardrails, 2-tier gates
