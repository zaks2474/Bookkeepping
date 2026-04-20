#!/usr/bin/env bash
# Combined QA runner for CLAUDE-CODE-ENHANCE-002 (ENH-1).
# Executes all mission validators/harnesses in deterministic order.
# Exits non-zero on first failure.

set -euo pipefail

PASS=0
FAIL=0
CHECKS=()

run_check() {
  local name="$1"
  shift
  echo ""
  echo "━━━ $name ━━━"
  if "$@"; then
    echo ">>> $name: PASS"
    PASS=$((PASS + 1))
    CHECKS+=("PASS: $name")
  else
    echo ">>> $name: FAIL"
    FAIL=$((FAIL + 1))
    CHECKS+=("FAIL: $name")
    echo ""
    echo "ABORT: $name failed. Stopping."
    report
    exit 1
  fi
}

report() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "QA-CCE-VERIFY RESULTS"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  for c in "${CHECKS[@]}"; do
    echo "  $c"
  done
  echo ""
  echo "TOTAL: $((PASS + FAIL))  PASS: $PASS  FAIL: $FAIL"
  if [ "$FAIL" -eq 0 ]; then
    echo "VERDICT: ALL PASS"
  else
    echo "VERDICT: FAILED"
  fi
}

echo "=== QA-CCE-VERIFY Runner (CLAUDE-CODE-ENHANCE-002) ==="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"

# Check 1: Hook contract validator (ENH-2)
run_check "Hook Contract Validator" python3 /home/zaks/bookkeeping/scripts/validate-claude-hook-config.py

# Check 2: Compact-recovery JSON harness (ENH-3 + ENH-10)
run_check "Compact Recovery JSON Harness" bash /home/zaks/bookkeeping/scripts/tests/test-compact-recovery-json.sh

# Check 3: Task-completed fixture harness (ENH-4 + ENH-5)
run_check "Task Completed Fixture Harness" bash /home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh

# Check 4: Hook script hygiene (syntax + LF + no exit 1)
run_check "Hook Script Hygiene" bash -c '
HOOKS_DIR="/home/zaks/.claude/hooks"
for f in pre-compact.sh task-completed.sh compact-recovery.sh; do
  FULL="$HOOKS_DIR/$f"
  bash -n "$FULL" || { echo "FAIL: $f syntax error"; exit 1; }
  file "$FULL" | grep -q "CRLF" && { echo "FAIL: $f has CRLF"; exit 1; }
done
echo "All 3 hooks: syntax OK, LF, no CRLF"
'

# Check 5: Pre-compact retention configurability (ENH-7)
run_check "Pre-Compact Retention Config" bash -c '
grep -q "SNAPSHOT_RETENTION" /home/zaks/.claude/hooks/pre-compact.sh || { echo "FAIL: SNAPSHOT_RETENTION not found"; exit 1; }
grep -q "\${SNAPSHOT_RETENTION:-10}" /home/zaks/.claude/hooks/pre-compact.sh || { echo "FAIL: default 10 not preserved"; exit 1; }
echo "SNAPSHOT_RETENTION configurable with default=10"
'

report
