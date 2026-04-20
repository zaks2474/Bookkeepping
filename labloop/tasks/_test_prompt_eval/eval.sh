#!/usr/bin/env bash
# Eval check: fails unless eval_results.json exists with valid content
# Builder must create the file to pass

set -euo pipefail

TASK_DIR="/home/zaks/bookkeeping/labloop/tasks/_test_prompt_eval"
RESULTS_FILE="$TASK_DIR/artifacts/eval_results.json"

echo "Prompt Eval Check"
echo "================="

if [[ -f "$RESULTS_FILE" ]]; then
    # Validate JSON
    if python3 -c "import json; json.load(open('$RESULTS_FILE'))" 2>/dev/null; then
        # Check for passed field
        if grep -q '"passed"[[:space:]]*:[[:space:]]*true' "$RESULTS_FILE"; then
            echo "SUCCESS: Eval results valid and passed=true"
            cat "$RESULTS_FILE"
            exit 0
        else
            echo "ERROR: Eval results exist but passed is not true"
            cat "$RESULTS_FILE"
            exit 1
        fi
    else
        echo "ERROR: Invalid JSON in $RESULTS_FILE"
        exit 1
    fi
else
    echo "ERROR: Eval results file not found: $RESULTS_FILE"
    echo "Builder must create this file with valid JSON."
    echo ""
    echo "Expected format:"
    echo '{ "passed": true, "tests": 5, "failures": 0 }'
    exit 1
fi
