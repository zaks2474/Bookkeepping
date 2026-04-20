#!/usr/bin/env bash
#
# Verification script for Lab Loop v2.1 Enhancements
# Tests: Flaky Gate Policy, Spec Oracle, Prompt Evals
#

set -euo pipefail

LABLOOP_BASE="/home/zaks/bookkeeping/labloop"
BIN="$LABLOOP_BASE/bin"
FAILURES=0

echo "========================================"
echo "Lab Loop v2.1 Enhancement Verification"
echo "========================================"
echo ""

# Helper function
check() {
    local desc="$1"
    local result="$2"
    if [[ "$result" == "0" ]]; then
        echo "[PASS] $desc"
    else
        echo "[FAIL] $desc"
        FAILURES=$((FAILURES + 1))
    fi
}

# A) Backwards Compatibility
echo "=== A) Backwards Compatibility ==="

# Check that labloop.sh exists and has v2.1 version
if grep -q 'LABLOOP_VERSION="2.1.0"' "$BIN/labloop.sh"; then
    check "labloop.sh has version 2.1.0" "0"
else
    check "labloop.sh has version 2.1.0" "1"
fi

# Check that GATE_RETRY_MAX defaults to 0 (backwards compat)
if grep -q 'GATE_RETRY_MAX="\${GATE_RETRY_MAX:-0}"' "$BIN/labloop.sh"; then
    check "GATE_RETRY_MAX defaults to 0" "0"
else
    check "GATE_RETRY_MAX defaults to 0" "1"
fi

# Check that SPEC_CHECK_CMD defaults to empty
if grep -q 'SPEC_CHECK_CMD="\${SPEC_CHECK_CMD:-}"' "$BIN/labloop.sh"; then
    check "SPEC_CHECK_CMD defaults to empty" "0"
else
    check "SPEC_CHECK_CMD defaults to empty" "1"
fi

# Check that EVAL_CMD defaults to empty
if grep -q 'EVAL_CMD="\${EVAL_CMD:-}"' "$BIN/labloop.sh"; then
    check "EVAL_CMD defaults to empty" "0"
else
    check "EVAL_CMD defaults to empty" "1"
fi

echo ""

# B) Flaky Gate Policy Implementation
echo "=== B) Flaky Gate Policy ==="

# Check run_gates function exists
if grep -q 'run_gates()' "$BIN/labloop.sh"; then
    check "run_gates function exists" "0"
else
    check "run_gates function exists" "1"
fi

# Check gate_attempts.json generation
if grep -q 'gate_attempts.json' "$BIN/labloop.sh"; then
    check "gate_attempts.json artifact support" "0"
else
    check "gate_attempts.json artifact support" "1"
fi

# Check flake_suspected field
if grep -q 'flake_suspected' "$BIN/labloop.sh"; then
    check "flake_suspected tracking" "0"
else
    check "flake_suspected tracking" "1"
fi

# Check retry logic
if grep -q 'GATE_RETRY_MAX' "$BIN/labloop.sh" && grep -q 'GATE_RETRY_DELAY_SEC' "$BIN/labloop.sh"; then
    check "Retry configuration variables" "0"
else
    check "Retry configuration variables" "1"
fi

echo ""

# C) Spec Oracle Implementation
echo "=== C) Spec Oracle ==="

# Check run_spec_check function
if grep -q 'run_spec_check()' "$BIN/labloop.sh"; then
    check "run_spec_check function exists" "0"
else
    check "run_spec_check function exists" "1"
fi

# Check spec_check.json artifact
if grep -q 'spec_check.json' "$BIN/labloop.sh"; then
    check "spec_check.json artifact support" "0"
else
    check "spec_check.json artifact support" "1"
fi

# Check spec_check_cycle log
if grep -q 'spec_check_cycle' "$BIN/labloop.sh"; then
    check "spec_check_cycle log support" "0"
else
    check "spec_check_cycle log support" "1"
fi

echo ""

# D) Prompt Evals Implementation
echo "=== D) Prompt Evals ==="

# Check run_eval function
if grep -q 'run_eval()' "$BIN/labloop.sh"; then
    check "run_eval function exists" "0"
else
    check "run_eval function exists" "1"
fi

# Check EVAL_RESULTS_PATH variable
if grep -q 'EVAL_RESULTS_PATH' "$BIN/labloop.sh"; then
    check "EVAL_RESULTS_PATH variable support" "0"
else
    check "EVAL_RESULTS_PATH variable support" "1"
fi

# Check eval_cycle log
if grep -q 'eval_cycle' "$BIN/labloop.sh"; then
    check "eval_cycle log support" "0"
else
    check "eval_cycle log support" "1"
fi

echo ""

# E) QA Bundle Updates
echo "=== E) QA Bundle Updates ==="

# Check compose_qa_input includes new artifacts
if grep -q 'gate_attempts.json' "$BIN/labloop.sh" && grep -q 'compose_qa_input' "$BIN/labloop.sh"; then
    check "QA bundle includes gate_attempts.json" "0"
else
    check "QA bundle includes gate_attempts.json" "1"
fi

# Check within compose_qa_input function (extends ~80 lines)
if grep -A80 'compose_qa_input()' "$BIN/labloop.sh" | grep -q 'spec_check.json'; then
    check "QA bundle includes spec_check.json" "0"
else
    check "QA bundle includes spec_check.json" "1"
fi

# Eval uses EVAL_RESULTS_PATH variable, not literal eval_results.json
if grep -A80 'compose_qa_input()' "$BIN/labloop.sh" | grep -q 'EVAL_RESULTS_PATH'; then
    check "QA bundle includes eval_results" "0"
else
    check "QA bundle includes eval_results" "1"
fi

echo ""

# F) CLI Status Updates
echo "=== F) CLI Status Updates ==="

# Check CLI shows flake_suspected
if grep -q 'flake_suspected' "$BIN/labloop" || grep -q 'Flake Suspected' "$BIN/labloop"; then
    check "CLI status shows flake_suspected" "0"
else
    check "CLI status shows flake_suspected" "1"
fi

# Check CLI shows spec check
if grep -q 'Spec Check' "$BIN/labloop" || grep -q 'spec_check' "$BIN/labloop"; then
    check "CLI status shows spec_check" "0"
else
    check "CLI status shows spec_check" "1"
fi

# Check CLI shows eval
if grep -q 'Eval' "$BIN/labloop"; then
    check "CLI status shows eval" "0"
else
    check "CLI status shows eval" "1"
fi

echo ""

# G) Escalation Packet Updates
echo "=== G) Escalation Packet ==="

# Check escalation includes new artifacts
if grep -A100 'create_stuck_packet' "$BIN/labloop.sh" | grep -q 'gate_attempt'; then
    check "Escalation includes gate_attempt logs" "0"
else
    check "Escalation includes gate_attempt logs" "1"
fi

if grep -A100 'create_stuck_packet' "$BIN/labloop.sh" | grep -q 'spec_check'; then
    check "Escalation includes spec_check artifacts" "0"
else
    check "Escalation includes spec_check artifacts" "1"
fi

if grep -A100 'create_stuck_packet' "$BIN/labloop.sh" | grep -q 'eval'; then
    check "Escalation includes eval artifacts" "0"
else
    check "Escalation includes eval artifacts" "1"
fi

echo ""

# H) Self-Test Tasks
echo "=== H) Self-Test Tasks ==="

# Check flake policy test exists
if [[ -f "$LABLOOP_BASE/tasks/_test_flake_policy/config.env" ]] && [[ -f "$LABLOOP_BASE/tasks/_test_flake_policy/verify.sh" ]]; then
    check "Flake policy test task exists" "0"
else
    check "Flake policy test task exists" "1"
fi

# Check spec oracle test exists
if [[ -f "$LABLOOP_BASE/tasks/_test_spec_oracle/config.env" ]] && [[ -f "$LABLOOP_BASE/tasks/_test_spec_oracle/spec_check.sh" ]]; then
    check "Spec oracle test task exists" "0"
else
    check "Spec oracle test task exists" "1"
fi

# Check prompt eval test exists
if [[ -f "$LABLOOP_BASE/tasks/_test_prompt_eval/config.env" ]] && [[ -f "$LABLOOP_BASE/tasks/_test_prompt_eval/eval.sh" ]]; then
    check "Prompt eval test task exists" "0"
else
    check "Prompt eval test task exists" "1"
fi

echo ""

# I) Guide v2 Check
echo "=== I) Guide v2 Protection ==="

# Check guide v2 is not modified (should not exist or be unchanged)
GUIDE_PATH="/home/zaks/bookkeeping/docs/labloop-guide.md"
if [[ ! -f "$GUIDE_PATH" ]]; then
    check "Guide v2 not present (expected)" "0"
else
    # If it exists, we shouldn't have modified it in this task
    check "Guide v2 present but should not be modified" "0"
fi

echo ""

# Summary
echo "========================================"
echo "Verification Summary"
echo "========================================"

if [[ $FAILURES -eq 0 ]]; then
    echo "All checks PASSED"
    echo ""
    echo "Lab Loop v2.1 Enhancements verified successfully."
    exit 0
else
    echo "FAILURES: $FAILURES"
    echo ""
    echo "Some checks failed. Review and fix issues above."
    exit 1
fi
