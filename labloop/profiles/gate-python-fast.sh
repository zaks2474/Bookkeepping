#!/usr/bin/env bash
#
# Gate Profile: Python Fast (Parallel)
# =====================================
# Quick Python verification with parallel lint + type check
#
set -euo pipefail

echo "=== Gate: Python Fast (Parallel) ==="

# Activate venv if present
if [[ -f "venv/bin/activate" ]]; then
  source venv/bin/activate
elif [[ -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
fi

# Run lint and type check in parallel
echo ">>> Running parallel checks (ruff + mypy)..."
FAIL=0

# Background jobs for parallel execution
(
  if command -v ruff &>/dev/null; then
    ruff check . --fix 2>&1 | sed 's/^/[ruff] /'
  fi
) &
RUFF_PID=$!

(
  if command -v mypy &>/dev/null && [[ -f "pyproject.toml" || -f "mypy.ini" ]]; then
    mypy . --ignore-missing-imports 2>&1 | sed 's/^/[mypy] /'
  fi
) &
MYPY_PID=$!

# Wait for parallel jobs
wait $RUFF_PID || FAIL=1
wait $MYPY_PID || FAIL=1

if [[ $FAIL -ne 0 ]]; then
  echo ">>> Parallel checks had warnings (non-blocking)"
fi

# Fast tests (sequential, fail fast)
echo ">>> Running pytest (fast mode)..."
pytest -x -q --tb=short 2>&1 || exit 1

echo "=== Gate: Python Fast PASSED ==="
