#!/usr/bin/env bash
# Flaky gate test: fails first time, passes second time
# Uses a counter file to track attempts

set -euo pipefail

TASK_DIR="/home/zaks/bookkeeping/labloop/tasks/_test_flake_policy"
COUNTER_FILE="$TASK_DIR/.attempt_counter"

# Read current attempt count
if [[ -f "$COUNTER_FILE" ]]; then
    count=$(cat "$COUNTER_FILE")
else
    count=0
fi

# Increment counter
count=$((count + 1))
echo "$count" > "$COUNTER_FILE"

echo "Flaky gate test - Attempt #$count"

if [[ $count -eq 1 ]]; then
    echo "ERROR: Simulated flaky failure (first attempt)"
    echo "This is intentional to test retry handling."
    exit 1
else
    echo "SUCCESS: Gate passed on retry (attempt #$count)"
    echo "Flake policy test completed successfully."
    exit 0
fi
