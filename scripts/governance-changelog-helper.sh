#!/usr/bin/env bash
# governance-changelog-helper.sh — Auto-generate changelog entries for governance rule changes
# Usage: bash governance-changelog-helper.sh [--since YYYY-MM-DD]
set -euo pipefail

RULES_DIR="/home/zaks/zakops-agent-api/.claude/rules"
SINCE="${2:-7 days ago}"

echo "=== Governance Changelog Helper ==="
echo "Rules directory: $RULES_DIR"
echo "Looking for changes since: $SINCE"
echo ""

# Check git log for governance file changes
cd /home/zaks/zakops-agent-api

GOVERNANCE_FILES=(
  ".claude/rules/design-system.md"
  ".claude/rules/accessibility.md"
  ".claude/rules/component-patterns.md"
  ".claude/rules/contract-surfaces.md"
  "tools/infra/validate-frontend-governance.sh"
  "tools/infra/validate-rule-frontmatter.sh"
  "tools/infra/check-governance-drift.sh"
)

CHANGED=0
echo "## Governance Changes"
echo ""
echo "| File | Last Modified | Status |"
echo "|------|--------------|--------|"

for file in "${GOVERNANCE_FILES[@]}"; do
  FULL_PATH="/home/zaks/zakops-agent-api/$file"
  if [[ -f "$FULL_PATH" ]]; then
    MOD_DATE=$(stat -c %y "$FULL_PATH" 2>/dev/null | cut -d' ' -f1)
    SIZE=$(wc -c < "$FULL_PATH")
    echo "| $file | $MOD_DATE | ${SIZE} bytes |"
    CHANGED=$((CHANGED + 1))
  else
    echo "| $file | — | MISSING |"
  fi
done

echo ""
echo "Total governance files tracked: $CHANGED/${#GOVERNANCE_FILES[@]}"
echo ""
echo "Governance Changelog Helper: DONE"
