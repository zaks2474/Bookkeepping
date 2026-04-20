#!/usr/bin/env bash
# Spec check: fails unless a marker file exists
# Builder must create the file to pass

set -euo pipefail

TASK_DIR="/home/zaks/bookkeeping/labloop/tasks/_test_spec_oracle"
MARKER_FILE="$TASK_DIR/.spec_marker"

echo "Spec Oracle Check"
echo "================="

if [[ -f "$MARKER_FILE" ]]; then
    echo "SUCCESS: Marker file exists - spec check passed"
    cat "$MARKER_FILE"
    exit 0
else
    echo "ERROR: Marker file not found: $MARKER_FILE"
    echo "Builder must create this file to satisfy spec check."
    echo ""
    echo "Expected content: { \"status\": \"compliant\" }"
    exit 1
fi
