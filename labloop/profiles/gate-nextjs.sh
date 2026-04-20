#!/usr/bin/env bash
#
# Gate Profile: Next.js (Parallel)
# =================================
# Next.js verification with parallel TypeScript + ESLint
#
set -euo pipefail

echo "=== Gate: Next.js (Parallel) ==="

# Check for package manager
if [[ -f "pnpm-lock.yaml" ]]; then
  PKG="pnpm"
elif [[ -f "yarn.lock" ]]; then
  PKG="yarn"
elif [[ -f "bun.lockb" ]]; then
  PKG="bun"
else
  PKG="npm"
fi

echo ">>> Using package manager: $PKG"

# Install deps if needed
if [[ ! -d "node_modules" ]]; then
  echo ">>> Installing dependencies..."
  $PKG install
fi

# Run TypeScript and ESLint in parallel
echo ">>> Running parallel checks (tsc + eslint)..."

TSC_LOG=$(mktemp)
LINT_LOG=$(mktemp)

# Background jobs for parallel execution
(
  if [[ -f "tsconfig.json" ]]; then
    $PKG exec tsc --noEmit > "$TSC_LOG" 2>&1
    echo $? > "${TSC_LOG}.rc"
  else
    echo 0 > "${TSC_LOG}.rc"
  fi
) &
TSC_PID=$!

(
  $PKG run lint > "$LINT_LOG" 2>&1
  echo $? > "${LINT_LOG}.rc"
) &
LINT_PID=$!

# Wait for parallel jobs
wait $TSC_PID
wait $LINT_PID

TSC_RC=$(cat "${TSC_LOG}.rc" 2>/dev/null || echo 0)
LINT_RC=$(cat "${LINT_LOG}.rc" 2>/dev/null || echo 0)

echo "--- TypeScript output ---"
cat "$TSC_LOG"
echo "--- ESLint output ---"
cat "$LINT_LOG"

rm -f "$TSC_LOG" "$LINT_LOG" "${TSC_LOG}.rc" "${LINT_LOG}.rc"

if [[ $TSC_RC -ne 0 ]]; then
  echo ">>> BLOCKER: TypeScript check failed"
  exit 1
fi

if [[ $LINT_RC -ne 0 ]]; then
  echo ">>> BLOCKER: ESLint check failed"
  exit 1
fi

# Build (sequential - depends on type check passing)
echo ">>> Building Next.js app..."
$PKG run build 2>&1 || exit 1

# Tests (if configured)
if grep -q '"test"' package.json 2>/dev/null; then
  echo ">>> Running tests..."
  $PKG test 2>&1 || exit 1
fi

echo "=== Gate: Next.js PASSED ==="
