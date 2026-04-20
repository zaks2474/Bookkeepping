#!/usr/bin/env bash
#
# Gate Profile: Python Full (Parallel)
# =====================================
# Comprehensive Python verification with parallel checks
#
set -euo pipefail

echo "=== Gate: Python Full (Parallel) ==="

# Activate venv if present
if [[ -f "venv/bin/activate" ]]; then
  source venv/bin/activate
elif [[ -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
fi

# Run lint and type check in parallel (strict mode)
echo ">>> Running parallel checks (ruff + mypy)..."

RUFF_LOG=$(mktemp)
MYPY_LOG=$(mktemp)
RUFF_RC=0
MYPY_RC=0

# Background jobs for parallel execution
(
  if command -v ruff &>/dev/null; then
    ruff check . > "$RUFF_LOG" 2>&1
    echo $? > "${RUFF_LOG}.rc"
  else
    echo 0 > "${RUFF_LOG}.rc"
  fi
) &
RUFF_PID=$!

(
  if command -v mypy &>/dev/null && [[ -f "pyproject.toml" || -f "mypy.ini" ]]; then
    mypy . --ignore-missing-imports > "$MYPY_LOG" 2>&1
    echo $? > "${MYPY_LOG}.rc"
  else
    echo 0 > "${MYPY_LOG}.rc"
  fi
) &
MYPY_PID=$!

# Wait for parallel jobs
wait $RUFF_PID
wait $MYPY_PID

RUFF_RC=$(cat "${RUFF_LOG}.rc" 2>/dev/null || echo 0)
MYPY_RC=$(cat "${MYPY_LOG}.rc" 2>/dev/null || echo 0)

echo "--- Ruff output ---"
cat "$RUFF_LOG"
echo "--- Mypy output ---"
cat "$MYPY_LOG"

rm -f "$RUFF_LOG" "$MYPY_LOG" "${RUFF_LOG}.rc" "${MYPY_LOG}.rc"

if [[ $RUFF_RC -ne 0 ]]; then
  echo ">>> BLOCKER: Ruff check failed"
  exit 1
fi

if [[ $MYPY_RC -ne 0 ]]; then
  echo ">>> BLOCKER: Mypy check failed"
  exit 1
fi

# Full tests with coverage
echo ">>> Running pytest with coverage..."
pytest --cov=. --cov-report=term-missing --cov-fail-under=70 -v 2>&1 || exit 1

echo "=== Gate: Python Full PASSED ==="
