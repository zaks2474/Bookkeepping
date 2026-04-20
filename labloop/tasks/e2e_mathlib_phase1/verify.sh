#!/bin/bash
# Gate verification script for e2e_mathlib_phase1
# Runs pytest and captures artifacts

set -e

TASK_DIR="/home/zaks/bookkeeping/labloop/tasks/e2e_mathlib_phase1"
ARTIFACTS_DIR="$TASK_DIR/artifacts"
mkdir -p "$ARTIFACTS_DIR"

# Run pytest and capture output
echo "Running pytest..."
.venv/bin/pytest -v --tb=short 2>&1 | tee "$ARTIFACTS_DIR/pytest_output.txt"
EXIT_CODE=${PIPESTATUS[0]}

# Generate summary JSON
TIMESTAMP=$(date -Iseconds)
PASSED=$(grep -c "PASSED" "$ARTIFACTS_DIR/pytest_output.txt" || echo 0)
FAILED=$(grep -c "FAILED" "$ARTIFACTS_DIR/pytest_output.txt" || echo 0)

cat > "$ARTIFACTS_DIR/pytest_summary.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "exit_code": $EXIT_CODE,
  "passed": $PASSED,
  "failed": $FAILED,
  "total": $((PASSED + FAILED))
}
EOF

echo ""
echo "=== Gate Summary ==="
echo "Exit code: $EXIT_CODE"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Artifacts written to: $ARTIFACTS_DIR"

exit $EXIT_CODE
