#!/usr/bin/env bash
# Test harness for compact-recovery.sh JSON output (ENH-3 + ENH-10).
#
# Validates:
# - Output is valid JSON
# - Required keys present: hookSpecificOutput, hookEventName, additionalContext
# - Quality assertions present and all_pass=true
# - Context is non-empty and contains key path markers
#
# Exit 0 = all checks pass, Exit 1 = failure.

set -euo pipefail

SCRIPT="/home/zaks/.claude/hooks/compact-recovery.sh"
TMPOUT=$(mktemp /tmp/test-cr-json-XXXX.json)
trap 'rm -f "$TMPOUT"' EXIT

echo "=== test-compact-recovery-json ==="

# Run compact-recovery
bash "$SCRIPT" > "$TMPOUT" 2>&1
echo "STEP 1: Script executed (exit 0)"

# Validate JSON structure and quality assertions
python3 << PYEOF
import json, sys

with open("$TMPOUT", "r") as f:
    raw = f.read()

# Parse JSON
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON: {e}")
    sys.exit(1)
print("STEP 2: Valid JSON")

# Required top-level key
hso = data.get("hookSpecificOutput")
if not hso:
    print("FAIL: Missing hookSpecificOutput")
    sys.exit(1)
print("STEP 3: hookSpecificOutput present")

# Required fields
if hso.get("hookEventName") != "SessionStart":
    print(f"FAIL: hookEventName={hso.get('hookEventName')}, expected SessionStart")
    sys.exit(1)
print("STEP 4: hookEventName=SessionStart")

ctx = hso.get("additionalContext", "")
if not ctx.strip():
    print("FAIL: additionalContext is empty")
    sys.exit(1)
print(f"STEP 5: additionalContext non-empty (len={len(ctx)})")

# Key path markers
required_paths = [
    "/home/zaks/zakops-agent-api",
    "/home/zaks/zakops-backend",
    "/home/zaks/bookkeeping",
]
for p in required_paths:
    if p not in ctx:
        print(f"FAIL: Missing key path marker: {p}")
        sys.exit(1)
print("STEP 6: All key path markers present")

# Changes marker
if "Recent Changes" not in ctx:
    print("FAIL: Missing 'Recent Changes' marker in context")
    sys.exit(1)
print("STEP 7: Recent Changes marker present")

# Quality assertions (ENH-10)
qa = hso.get("qualityAssertions")
if not qa:
    print("FAIL: Missing qualityAssertions")
    sys.exit(1)
print("STEP 8: qualityAssertions present")

if not qa.get("all_pass"):
    print(f"FAIL: qualityAssertions.all_pass={qa.get('all_pass')}")
    sys.exit(1)
print("STEP 9: qualityAssertions.all_pass=true")

print("=== ALL CHECKS PASS ===")
PYEOF
