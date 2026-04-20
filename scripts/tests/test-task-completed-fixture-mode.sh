#!/usr/bin/env bash
# Test harness for task-completed.sh fixture mode (ENH-4 + ENH-5).
#
# Creates controlled fixtures to verify:
# 1. Clean file → all gates PASS (exit 0)
# 2. CRLF-injected file → gate 1 FAIL (exit 2)
# 3. Root-owned file → gate 2 FAIL (exit 2)
# 4. Machine-readable GATE_RESULT markers present in all cases
#
# Exit 0 = all checks pass, Exit 1 = failure.

set -euo pipefail

SCRIPT="/home/zaks/.claude/hooks/task-completed.sh"
TMPDIR=$(mktemp -d /tmp/test-tc-fixture-XXXX)
trap 'rm -rf "$TMPDIR"' EXIT

echo "=== test-task-completed-fixture-mode ==="

# --- Fixture 1: Clean file (should PASS all gates) ---
CLEAN_FILE="$TMPDIR/clean.sh"
printf '#!/usr/bin/env bash\necho hello\n' > "$CLEAN_FILE"
chmod 755 "$CLEAN_FILE"
chown zaks:zaks "$CLEAN_FILE" 2>/dev/null || true

RC=0
OUTPUT=$(TASK_COMPLETED_TARGETS="$CLEAN_FILE" bash "$SCRIPT" 2>&1) || RC=$?

echo "$OUTPUT" | grep -q "GATE_RESULT:overall:PASS" || { echo "FAIL: Clean fixture did not produce overall:PASS"; echo "$OUTPUT"; exit 1; }
[ "$RC" -eq 0 ] || { echo "FAIL: Clean fixture exit code=$RC, expected 0"; exit 1; }
echo "STEP 1: Clean fixture → PASS (exit 0)"

# Verify all 4 GATE_RESULT markers present
for marker in "crlf" "ownership" "typescript" "overall"; do
  echo "$OUTPUT" | grep -q "GATE_RESULT:${marker}:" || { echo "FAIL: Missing GATE_RESULT:${marker} marker"; exit 1; }
done
echo "STEP 2: All 4 GATE_RESULT markers present"

# --- Fixture 2: CRLF file (should FAIL gate 1) ---
CRLF_FILE="$TMPDIR/crlf.sh"
printf '#!/usr/bin/env bash\r\necho hello\r\n' > "$CRLF_FILE"
chmod 755 "$CRLF_FILE"
chown zaks:zaks "$CRLF_FILE" 2>/dev/null || true

RC=0
OUTPUT=$(TASK_COMPLETED_TARGETS="$CRLF_FILE" bash "$SCRIPT" 2>&1) || RC=$?

echo "$OUTPUT" | grep -q "GATE_RESULT:crlf:FAIL" || { echo "FAIL: CRLF fixture did not produce crlf:FAIL"; echo "$OUTPUT"; exit 1; }
echo "$OUTPUT" | grep -q "GATE_RESULT:overall:FAIL" || { echo "FAIL: CRLF fixture did not produce overall:FAIL"; echo "$OUTPUT"; exit 1; }
[ "$RC" -eq 2 ] || { echo "FAIL: CRLF fixture exit code=$RC, expected 2"; exit 1; }
echo "STEP 3: CRLF fixture → crlf:FAIL, overall:FAIL (exit 2)"

# --- Fixture 3: Root-owned file (should FAIL gate 2) ---
ROOT_FILE="$TMPDIR/root-owned.sh"
printf '#!/usr/bin/env bash\necho hello\n' > "$ROOT_FILE"
chmod 755 "$ROOT_FILE"
# File is already root-owned since we run as root

RC=0
OUTPUT=$(TASK_COMPLETED_TARGETS="$ROOT_FILE" bash "$SCRIPT" 2>&1) || RC=$?

echo "$OUTPUT" | grep -q "GATE_RESULT:ownership:FAIL" || { echo "FAIL: Root fixture did not produce ownership:FAIL"; echo "$OUTPUT"; exit 1; }
echo "$OUTPUT" | grep -q "GATE_RESULT:overall:FAIL" || { echo "FAIL: Root fixture did not produce overall:FAIL"; echo "$OUTPUT"; exit 1; }
[ "$RC" -eq 2 ] || { echo "FAIL: Root fixture exit code=$RC, expected 2"; exit 1; }
echo "STEP 4: Root-owned fixture → ownership:FAIL, overall:FAIL (exit 2)"

# --- Fixture 4: Non-existent file (should PASS — no targets to scan) ---
RC=0
OUTPUT=$(TASK_COMPLETED_TARGETS="/tmp/nonexistent-file-xyz.sh" bash "$SCRIPT" 2>&1) || RC=$?

echo "$OUTPUT" | grep -q "GATE_RESULT:overall:PASS" || { echo "FAIL: Nonexistent fixture did not produce overall:PASS"; echo "$OUTPUT"; exit 1; }
[ "$RC" -eq 0 ] || { echo "FAIL: Nonexistent fixture exit code=$RC, expected 0"; exit 1; }
echo "STEP 5: Nonexistent target → graceful PASS (exit 0)"

echo "=== ALL CHECKS PASS ==="
