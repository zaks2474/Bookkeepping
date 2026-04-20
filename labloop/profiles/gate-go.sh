#!/usr/bin/env bash
#
# Gate Profile: Go
# ================
# Go verification: vet + staticcheck + test
#
# Usage in config.env:
#   GATE_CMD="source $BASE/profiles/gate-go.sh"
#
set -euo pipefail

echo "=== Gate: Go ==="

# Vet
echo ">>> Running go vet..."
go vet ./... || exit 1

# Staticcheck (if available)
if command -v staticcheck &>/dev/null; then
  echo ">>> Running staticcheck..."
  staticcheck ./... || exit 1
fi

# Build
echo ">>> Building..."
go build ./... || exit 1

# Tests
echo ">>> Running tests..."
go test -v -race ./... 2>&1 || exit 1

echo "=== Gate: Go PASSED ==="
