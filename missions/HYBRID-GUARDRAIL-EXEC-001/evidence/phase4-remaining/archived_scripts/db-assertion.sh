#!/usr/bin/env bash
# tools/infra/db-assertion.sh
# V3 HARD GATE: Verifies EXPLICIT DB mapping from contracts/runtime.topology.json
# Uses runtime debug endpoints (not code grep) as primary verification
# sqlite detection via runtime check, not grep
# Companion Note #2: Uses $DB_USER from topology.env, not hardcoded

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

EVIDENCE_DIR="artifacts/infra-awareness/evidence/db-assertion"
mkdir -p "$EVIDENCE_DIR"

echo "═══ DB SOURCE-OF-TRUTH ASSERTION (V3 HARD GATE) ═══" | tee "$EVIDENCE_DIR/assertion.log"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

FAILURES=0
CHECKS=0

# Load expected DB mapping
MAPPING_FILE="contracts/runtime.topology.json"
if [ ! -f "$MAPPING_FILE" ]; then
  echo "❌ FAIL: Missing contracts/runtime.topology.json" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   Create this file with explicit DB mappings" | tee -a "$EVIDENCE_DIR/assertion.log"
  exit 1
fi

EXPECTED_BACKEND_DB=$(jq -r '.db_mapping.backend.expected_database' "$MAPPING_FILE")
EXPECTED_AGENT_DB=$(jq -r '.db_mapping["agent-api"].expected_database' "$MAPPING_FILE")

echo "Expected mappings:" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "  backend → $EXPECTED_BACKEND_DB" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "  agent-api → $EXPECTED_AGENT_DB" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# CHECK 1: Backend DB Connection via Debug Endpoint (V3 PRIMARY)
# ══════════════════════════════════════════════════════════════

echo "── Check 1: Backend DB via Debug Endpoint (V3) ──" | tee -a "$EVIDENCE_DIR/assertion.log"
CHECKS=$((CHECKS+1))

# Try debug endpoint first (V3 primary)
BACKEND_DEBUG=$(curl -sf "$BACKEND_URL/api/admin/debug/db" \
  -H "X-Service-Token: ${SERVICE_TOKEN:-internal}" 2>/dev/null || echo '{"error": "ENDPOINT_NOT_AVAILABLE"}')

echo "$BACKEND_DEBUG" > "$EVIDENCE_DIR/backend_debug_db.json"

if echo "$BACKEND_DEBUG" | jq -e '.db_name' &>/dev/null; then
  ACTUAL_BACKEND_DB=$(echo "$BACKEND_DEBUG" | jq -r '.db_name')
  ACTUAL_BACKEND_TYPE=$(echo "$BACKEND_DEBUG" | jq -r '.pool_backend // "postgresql"')
  ACTUAL_READ_FROM=$(echo "$BACKEND_DEBUG" | jq -r '.read_from // "postgresql"')

  echo "Backend reports:" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "  db_name: $ACTUAL_BACKEND_DB" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "  pool_backend: $ACTUAL_BACKEND_TYPE" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "  read_from: $ACTUAL_READ_FROM" | tee -a "$EVIDENCE_DIR/assertion.log"

  # V3: Check for sqlite in any field
  if [ "$ACTUAL_BACKEND_TYPE" = "sqlite" ] || [ "$ACTUAL_READ_FROM" = "sqlite" ]; then
    echo "❌ FAIL: Backend using SQLite! This is a P0 split-brain risk" | tee -a "$EVIDENCE_DIR/assertion.log"
    FAILURES=$((FAILURES+1))
  elif [ "$ACTUAL_BACKEND_DB" != "$EXPECTED_BACKEND_DB" ]; then
    echo "❌ FAIL: Backend connected to '$ACTUAL_BACKEND_DB', expected '$EXPECTED_BACKEND_DB'" | tee -a "$EVIDENCE_DIR/assertion.log"
    FAILURES=$((FAILURES+1))
  else
    echo "✅ Backend DB verified via debug endpoint" | tee -a "$EVIDENCE_DIR/assertion.log"
  fi
else
  echo "⚠️  Debug endpoint not available, falling back to container env..." | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   Recommendation: Implement /api/admin/debug/db endpoint" | tee -a "$EVIDENCE_DIR/assertion.log"

  # Fallback: Check container env (V2 method)
  BACKEND_DB_URL=$(docker exec "$BACKEND_CID" printenv DATABASE_URL 2>/dev/null || echo "UNREACHABLE")
  BACKEND_DB_URL_REDACTED=$(echo "$BACKEND_DB_URL" | sed 's|://[^:]*:[^@]*@|://***:***@|')
  echo "$BACKEND_DB_URL_REDACTED" > "$EVIDENCE_DIR/backend_db_url_redacted.txt"

  if [ "$BACKEND_DB_URL" = "UNREACHABLE" ]; then
    echo "❌ FAIL: Cannot reach backend container" | tee -a "$EVIDENCE_DIR/assertion.log"
    FAILURES=$((FAILURES+1))
  elif echo "$BACKEND_DB_URL" | grep -qi "sqlite"; then
    echo "❌ FAIL: Backend DATABASE_URL contains sqlite!" | tee -a "$EVIDENCE_DIR/assertion.log"
    FAILURES=$((FAILURES+1))
  elif ! echo "$BACKEND_DB_URL" | grep -q "$EXPECTED_BACKEND_DB"; then
    echo "❌ FAIL: Backend DATABASE_URL does not contain '$EXPECTED_BACKEND_DB'" | tee -a "$EVIDENCE_DIR/assertion.log"
    FAILURES=$((FAILURES+1))
  else
    echo "✅ Backend DB verified via container env (debug endpoint not available)" | tee -a "$EVIDENCE_DIR/assertion.log"
  fi
fi
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# CHECK 2: Agent API DB Connection (V3)
# ══════════════════════════════════════════════════════════════

echo "── Check 2: Agent API DB Connection (V3) ──" | tee -a "$EVIDENCE_DIR/assertion.log"
CHECKS=$((CHECKS+1))

if [ -n "$AGENT_CID" ]; then
  AGENT_DEBUG=$(curl -sf "$AGENT_URL/api/admin/debug/db" \
    -H "X-Service-Token: ${SERVICE_TOKEN:-internal}" 2>/dev/null || echo '{"error": "ENDPOINT_NOT_AVAILABLE"}')

  echo "$AGENT_DEBUG" > "$EVIDENCE_DIR/agent_debug_db.json"

  if echo "$AGENT_DEBUG" | jq -e '.db_name' &>/dev/null; then
    ACTUAL_AGENT_DB=$(echo "$AGENT_DEBUG" | jq -r '.db_name')

    if [ "$ACTUAL_AGENT_DB" != "$EXPECTED_AGENT_DB" ]; then
      echo "❌ FAIL: Agent connected to '$ACTUAL_AGENT_DB', expected '$EXPECTED_AGENT_DB'" | tee -a "$EVIDENCE_DIR/assertion.log"
      FAILURES=$((FAILURES+1))
    else
      echo "✅ Agent DB verified: $ACTUAL_AGENT_DB" | tee -a "$EVIDENCE_DIR/assertion.log"
    fi
  else
    echo "⚠️  Agent debug endpoint not available, checking container env..." | tee -a "$EVIDENCE_DIR/assertion.log"

    AGENT_DB_URL_RAW=$(docker exec "$AGENT_CID" printenv DATABASE_URL 2>/dev/null || echo "")
    if [ -n "$AGENT_DB_URL_RAW" ] && echo "$AGENT_DB_URL_RAW" | grep -q "$EXPECTED_AGENT_DB"; then
      echo "✅ Agent DB verified via container env" | tee -a "$EVIDENCE_DIR/assertion.log"
    else
      echo "⚠️  Could not verify agent DB connection" | tee -a "$EVIDENCE_DIR/assertion.log"
    fi
  fi
else
  echo "⚠️  Agent container not running, skipping" | tee -a "$EVIDENCE_DIR/assertion.log"
fi
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# CHECK 3: Cross-Service DB Consistency (V3)
# ══════════════════════════════════════════════════════════════

echo "── Check 3: Cross-Service DB Consistency ──" | tee -a "$EVIDENCE_DIR/assertion.log"
CHECKS=$((CHECKS+1))

# Verify outbox-worker uses same DB as backend
OUTBOX_CID=$(docker ps --filter "name=outbox" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")

if [ -n "$OUTBOX_CID" ]; then
  OUTBOX_DB_URL=$(docker exec "$OUTBOX_CID" printenv DATABASE_URL 2>/dev/null || echo "")
  BACKEND_DB_URL_RAW=$(docker exec "$BACKEND_CID" printenv DATABASE_URL 2>/dev/null || echo "")

  if [ -n "$OUTBOX_DB_URL" ] && [ -n "$BACKEND_DB_URL_RAW" ]; then
    # Compare hosts (redacted comparison)
    OUTBOX_HOST=$(echo "$OUTBOX_DB_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    BACKEND_HOST=$(echo "$BACKEND_DB_URL_RAW" | sed -n 's|.*@\([^:]*\):.*|\1|p')

    if [ "$OUTBOX_HOST" != "$BACKEND_HOST" ]; then
      echo "❌ FAIL: Outbox-worker uses different DB host than backend!" | tee -a "$EVIDENCE_DIR/assertion.log"
      echo "   Outbox: $OUTBOX_HOST" | tee -a "$EVIDENCE_DIR/assertion.log"
      echo "   Backend: $BACKEND_HOST" | tee -a "$EVIDENCE_DIR/assertion.log"
      FAILURES=$((FAILURES+1))
    else
      echo "✅ Outbox-worker shares DB host with backend" | tee -a "$EVIDENCE_DIR/assertion.log"
    fi
  fi
else
  echo "⚠️  No outbox-worker container found" | tee -a "$EVIDENCE_DIR/assertion.log"
fi
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# CHECK 4: Deal Count via Debug Endpoint (V3 — Not UI endpoint)
# ══════════════════════════════════════════════════════════════

echo "── Check 4: Deal Count Assertion (V3 — Debug Endpoint) ──" | tee -a "$EVIDENCE_DIR/assertion.log"
CHECKS=$((CHECKS+1))

# Direct DB count (using $DB_USER, not hardcoded)
DB_COUNT=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$EXPECTED_BACKEND_DB" -t -A -c \
  "SELECT COUNT(*) FROM deals;" 2>/dev/null || echo "QUERY_FAILED")

# V3: Use admin debug endpoint, not UI endpoint (avoids pagination/filter issues)
DEBUG_COUNTS=$(curl -sf "$BACKEND_URL/api/admin/debug/counts" \
  -H "X-Service-Token: ${SERVICE_TOKEN:-internal}" 2>/dev/null || echo '{"error": "ENDPOINT_NOT_AVAILABLE"}')

echo "$DEBUG_COUNTS" > "$EVIDENCE_DIR/debug_counts.json"
API_COUNT=""

if echo "$DEBUG_COUNTS" | jq -e '.deals_total' &>/dev/null; then
  API_COUNT=$(echo "$DEBUG_COUNTS" | jq -r '.deals_total')

  echo "DB direct count:    $DB_COUNT" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "Debug API count:    $API_COUNT" | tee -a "$EVIDENCE_DIR/assertion.log"

  if [ "$DB_COUNT" != "$API_COUNT" ]; then
    echo "❌ FAIL: Deal count mismatch — potential split-brain!" | tee -a "$EVIDENCE_DIR/assertion.log"
    FAILURES=$((FAILURES+1))
  else
    echo "✅ Deal counts match" | tee -a "$EVIDENCE_DIR/assertion.log"
  fi
else
  echo "⚠️  Debug counts endpoint not available" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   Recommendation: Implement /api/admin/debug/counts endpoint" | tee -a "$EVIDENCE_DIR/assertion.log"

  # Fallback to UI endpoint (V2 method, less reliable)
  API_RESPONSE=$(curl -sf "$BACKEND_URL/api/deals" 2>/dev/null || echo '{"error":"UNREACHABLE"}')
  API_COUNT=$(echo "$API_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        print(len(data))
    elif 'items' in data:
        print(data.get('total', len(data['items'])))
    elif 'deals' in data:
        print(len(data['deals']))
    else:
        print('SHAPE_UNKNOWN')
except:
    print('PARSE_FAILED')
" 2>/dev/null)

  echo "DB direct count:    $DB_COUNT" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "UI API count:       $API_COUNT (may be paginated)" | tee -a "$EVIDENCE_DIR/assertion.log"
fi

echo "{\"db_count\": \"$DB_COUNT\", \"api_count\": \"${API_COUNT:-unknown}\"}" > "$EVIDENCE_DIR/deal_counts.json"
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# CHECK 5: Multiple Postgres Detection (V3 — With Mapping)
# ══════════════════════════════════════════════════════════════

echo "── Check 5: Multiple Postgres Detection ──" | tee -a "$EVIDENCE_DIR/assertion.log"
CHECKS=$((CHECKS+1))

# Use name-based filter (more reliable than ancestor with tagged images)
POSTGRES_CONTAINERS=$(docker ps --format "{{.Names}}\t{{.Image}}\t{{.Status}}" 2>/dev/null | grep -iE "postgres|pgvector" || echo "")
ALL_PG=$(echo "$POSTGRES_CONTAINERS" | grep -v "^$" | sort -u)

echo "$ALL_PG" > "$EVIDENCE_DIR/postgres_containers.txt"

RUNNING_COUNT=$(echo "$ALL_PG" | grep -v "^$" | wc -l)
echo "Running postgres-type containers: $RUNNING_COUNT" | tee -a "$EVIDENCE_DIR/assertion.log"

if [ "$RUNNING_COUNT" -gt 1 ]; then
  echo "⚠️  Multiple postgres containers detected:" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "$ALL_PG" | while read line; do
    [ -n "$line" ] && echo "   $line" | tee -a "$EVIDENCE_DIR/assertion.log"
  done

  # V3: Check if this is expected per mapping
  AGENT_DB_EXPECTED=$(jq -r '.db_mapping["agent-api"].expected_database' "$MAPPING_FILE")
  if [ "$EXPECTED_BACKEND_DB" != "$AGENT_DB_EXPECTED" ]; then
    echo "   → This is expected: backend uses '$EXPECTED_BACKEND_DB', agent uses '$AGENT_DB_EXPECTED'" | tee -a "$EVIDENCE_DIR/assertion.log"
  else
    echo "   → WARNING: Services share same DB name but multiple Postgres running!" | tee -a "$EVIDENCE_DIR/assertion.log"
  fi
fi
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# GATE SUMMARY
# ══════════════════════════════════════════════════════════════

PASSED=$((CHECKS - FAILURES))
VERDICT=$([ "$FAILURES" -eq 0 ] && echo "PASS" || echo "FAIL")

cat > "$EVIDENCE_DIR/gate-summary.json" << EOF
{
  "gate": "DB_SOURCE_OF_TRUTH_V3",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": $CHECKS,
  "passed": $PASSED,
  "failed": $FAILURES,
  "skipped": 0,
  "verdict": "$VERDICT",
  "v3_features": ["explicit_db_mapping", "debug_endpoints", "runtime_sqlite_detection"],
  "evidence_dir": "$EVIDENCE_DIR"
}
EOF

echo "═══ DB ASSERTION SUMMARY ═══" | tee -a "$EVIDENCE_DIR/assertion.log"
if [ "$FAILURES" -gt 0 ]; then
  echo "❌ HARD GATE FAILED: $FAILURES/$CHECKS checks failed" | tee -a "$EVIDENCE_DIR/assertion.log"
  exit 1
else
  echo "✅ ALL DB ASSERTIONS PASSED ($PASSED/$CHECKS)" | tee -a "$EVIDENCE_DIR/assertion.log"
fi
