#!/usr/bin/env bash
# tools/infra/extract-contracts.sh
# V3: COMPARE mode by default — never overwrites contracts/ unless --write-contracts
# Discovers values → writes to artifacts/ → diffs vs contracts/*.json → FAIL if mismatch
# Companion Note #2: Uses $DB_USER from topology.env, not hardcoded

set -euo pipefail

WRITE_MODE=false
if [ "${1:-}" = "--write-contracts" ]; then
  WRITE_MODE=true
  echo "⚠️  WRITE MODE: Will update contracts/ with discovered values"
fi

# Source topology
TOPOLOGY_FILE="artifacts/infra-awareness/evidence/topology/topology.env"
if [ ! -f "$TOPOLOGY_FILE" ]; then
  echo "❌ FAIL: Run Phase 0 first: make infra-topology"
  exit 1
fi
source "$TOPOLOGY_FILE"

EVIDENCE_DIR="artifacts/infra-awareness/evidence/contracts"
DISCOVERED_DIR="$EVIDENCE_DIR/discovered"
CONTRACTS_DIR="contracts"
mkdir -p "$EVIDENCE_DIR" "$DISCOVERED_DIR"

echo "═══ CONTRACT EXTRACTION (V3 — Compare Mode) ═══"
echo "Mode: $([ "$WRITE_MODE" = true ] && echo 'WRITE' || echo 'COMPARE')"
echo ""

MISMATCHES=0

# ══════════════════════════════════════════════════════════════
# STAGE VALUES — Priority: DB enum > Backend constant > Dashboard Zod
# ══════════════════════════════════════════════════════════════

echo "── Extracting Stage Values ──"

STAGES=""

# Priority 1: PostgreSQL enum type (using dynamic container ID + DB_USER)
STAGES=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
  SELECT enumlabel FROM pg_enum e
  JOIN pg_type t ON e.enumtypid = t.oid
  WHERE t.typname = 'deal_stage' OR t.typname = 'dealstage'
  ORDER BY enumsortorder;
" 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "")

if [ -z "$STAGES" ]; then
  echo "  No DB enum found, trying CHECK constraint..."

  STAGES=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT pg_get_constraintdef(c.oid)
    FROM pg_constraint c
    JOIN pg_class t ON c.conrelid = t.oid
    WHERE t.relname = 'deals' AND c.conname LIKE '%stage%';
  " 2>/dev/null | grep -oP "'[^']+'" | tr -d "'" | tr '\n' ',' | sed 's/,$//' || echo "")
fi

if [ -z "$STAGES" ] && [ -n "$BACKEND_ROOT" ]; then
  echo "  No DB constraint found, trying backend Python enum..."
  STAGES=$(grep -rh "ValidStage\|DealStage\|STAGES" "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
    | grep -oP '"[a-z_]+"' | tr -d '"' | sort -u | tr '\n' ',' | sed 's/,$//' || echo "")
fi

if [ -n "$STAGES" ]; then
  echo "✅ Discovered stages: $STAGES"

  # Write discovered to artifacts
  STAGES_JSON=$(echo "$STAGES" | tr ',' '\n' | jq -R . | jq -s .)
  cat > "$DISCOVERED_DIR/stages.json" << EOF
{
  "discovered_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "stages": $STAGES_JSON
}
EOF

  # Compare with contracts/
  if [ -f "$CONTRACTS_DIR/stages.json" ]; then
    EXISTING=$(jq -c '.stages | sort' "$CONTRACTS_DIR/stages.json" 2>/dev/null || echo '[]')
    DISCOVERED=$(echo "$STAGES_JSON" | jq -c 'sort')

    if [ "$EXISTING" != "$DISCOVERED" ]; then
      echo "❌ MISMATCH: stages.json"
      echo "   Contract: $EXISTING"
      echo "   Discovered: $DISCOVERED"
      MISMATCHES=$((MISMATCHES+1))

      if [ "$WRITE_MODE" = true ]; then
        echo "   → Updating contracts/stages.json"
        cat > "$CONTRACTS_DIR/stages.json" << EOF
{
  "\$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "ZakOps canonical pipeline stages",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "stages": $STAGES_JSON
}
EOF
      fi
    else
      echo "✅ stages.json matches contract"
    fi
  else
    echo "⚠️  No existing contracts/stages.json"
    MISMATCHES=$((MISMATCHES+1))

    if [ "$WRITE_MODE" = true ]; then
      echo "   → Creating contracts/stages.json"
      mkdir -p "$CONTRACTS_DIR"
      cat > "$CONTRACTS_DIR/stages.json" << EOF
{
  "\$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "ZakOps canonical pipeline stages",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "stages": $STAGES_JSON
}
EOF
    fi
  fi
else
  echo "❌ FAIL: Could not extract stage values from ANY source"
  MISMATCHES=$((MISMATCHES+1))
fi

echo ""

# ══════════════════════════════════════════════════════════════
# STATUS VALUES — Same pattern
# ══════════════════════════════════════════════════════════════

echo "── Extracting Status Values ──"

# Extract ActionStatus enum
ACTION_STATUSES=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
  SELECT enumlabel FROM pg_enum e
  JOIN pg_type t ON e.enumtypid = t.oid
  WHERE t.typname = 'action_status' OR t.typname = 'actionstatus'
  ORDER BY enumsortorder;
" 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "")

if [ -n "$ACTION_STATUSES" ]; then
  echo "✅ Discovered action statuses: $ACTION_STATUSES"

  STATUSES_JSON=$(echo "$ACTION_STATUSES" | tr ',' '\n' | jq -R . | jq -s .)
  cat > "$DISCOVERED_DIR/statuses.json" << EOF
{
  "discovered_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "action_statuses": $STATUSES_JSON
}
EOF

  # Compare with contracts/
  if [ -f "$CONTRACTS_DIR/statuses.json" ]; then
    EXISTING=$(jq -c '.action_statuses | sort' "$CONTRACTS_DIR/statuses.json" 2>/dev/null || echo '[]')
    DISCOVERED=$(echo "$STATUSES_JSON" | jq -c 'sort')

    if [ "$EXISTING" != "$DISCOVERED" ]; then
      echo "❌ MISMATCH: statuses.json"
      echo "   Contract: $EXISTING"
      echo "   Discovered: $DISCOVERED"
      MISMATCHES=$((MISMATCHES+1))

      if [ "$WRITE_MODE" = true ]; then
        echo "   → Updating contracts/statuses.json"
        cat > "$CONTRACTS_DIR/statuses.json" << EOF
{
  "\$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "ZakOps canonical action statuses",
  "updated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "action_statuses": $STATUSES_JSON
}
EOF
      fi
    else
      echo "✅ statuses.json matches contract"
    fi
  else
    echo "⚠️  No existing contracts/statuses.json"
    MISMATCHES=$((MISMATCHES+1))

    if [ "$WRITE_MODE" = true ]; then
      echo "   → Creating contracts/statuses.json"
      cat > "$CONTRACTS_DIR/statuses.json" << EOF
{
  "\$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "ZakOps canonical action statuses",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "action_statuses": $STATUSES_JSON
}
EOF
    fi
  fi
else
  echo "⚠️  Could not extract action status values"
fi

echo ""

# ══════════════════════════════════════════════════════════════
# GATE SUMMARY
# ══════════════════════════════════════════════════════════════

cat > "$EVIDENCE_DIR/gate-summary.json" << EOF
{
  "gate": "CONTRACT_EXTRACTION_V3",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "mode": "$([ "$WRITE_MODE" = true ] && echo 'WRITE' || echo 'COMPARE')",
  "mismatches": $MISMATCHES,
  "verdict": "$([ $MISMATCHES -eq 0 ] && echo 'PASS' || echo 'FAIL')"
}
EOF

if [ $MISMATCHES -gt 0 ] && [ "$WRITE_MODE" = false ]; then
  echo ""
  echo "❌ CONTRACT EXTRACTION FAILED: $MISMATCHES mismatches"
  echo "   Run with --write-contracts to update contracts/"
  exit 1
else
  echo ""
  echo "✅ Contract extraction complete"
fi
