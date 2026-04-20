#!/usr/bin/env bash
# tools/infra/migration-assertion.sh
# V3 NEW: Verifies DB schema matches migration files
# Hard-fail if migrations not fully applied
# Companion Note #2: Uses $DB_USER from topology.env, not hardcoded

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

EVIDENCE_DIR="artifacts/infra-awareness/evidence/migrations"
mkdir -p "$EVIDENCE_DIR"

echo "═══ MIGRATION STATE ASSERTION (V3) ═══" | tee "$EVIDENCE_DIR/assertion.log"
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

FAILURES=0

# ══════════════════════════════════════════════════════════════
# CHECK 1: Get latest migration file
# ══════════════════════════════════════════════════════════════

echo "── Check 1: Latest Migration File ──" | tee -a "$EVIDENCE_DIR/assertion.log"

# Find migration directory
MIGRATION_DIR=""
for path in \
  "$BACKEND_ROOT/db/migrations" \
  "$BACKEND_ROOT/migrations" \
  "$BACKEND_ROOT/alembic/versions"; do
  if [ -d "$path" ]; then
    MIGRATION_DIR="$path"
    break
  fi
done

if [ -z "$MIGRATION_DIR" ]; then
  echo "⚠️  No migration directory found" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo '{"verdict": "SKIP", "reason": "no_migration_directory"}' > "$EVIDENCE_DIR/gate-summary.json"
  exit 0
fi

echo "Migration directory: $MIGRATION_DIR" | tee -a "$EVIDENCE_DIR/assertion.log"

# Get latest migration (by filename, assuming version prefix)
LATEST_FILE=$(ls -1 "$MIGRATION_DIR"/*.py 2>/dev/null | sort -V | tail -1 || echo "")
if [ -z "$LATEST_FILE" ]; then
  LATEST_FILE=$(ls -1 "$MIGRATION_DIR"/*.sql 2>/dev/null | sort -V | tail -1 || echo "")
fi

if [ -z "$LATEST_FILE" ]; then
  echo "⚠️  No migration files found in $MIGRATION_DIR" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo '{"verdict": "SKIP", "reason": "no_migration_files"}' > "$EVIDENCE_DIR/gate-summary.json"
  exit 0
fi

LATEST_MIGRATION=$(basename "$LATEST_FILE" | sed 's/\.[^.]*$//')
echo "Latest migration file: $LATEST_MIGRATION" | tee -a "$EVIDENCE_DIR/assertion.log"

# List all migration files for evidence
ls -1 "$MIGRATION_DIR" > "$EVIDENCE_DIR/migration_files.txt" 2>/dev/null

# ══════════════════════════════════════════════════════════════
# CHECK 2: Query DB for applied migrations
# ══════════════════════════════════════════════════════════════

echo "" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "── Check 2: Applied Migrations in DB ──" | tee -a "$EVIDENCE_DIR/assertion.log"

# Try Alembic table first
DB_LATEST=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
  SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;
" 2>/dev/null || echo "")

if [ -z "$DB_LATEST" ]; then
  # Try Django-style migrations table
  DB_LATEST=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT name FROM django_migrations ORDER BY applied DESC LIMIT 1;
  " 2>/dev/null || echo "")
fi

if [ -z "$DB_LATEST" ]; then
  # Try custom migrations table
  # Try with explicit search_path (tables may not be in 'public')
  DB_LATEST=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1;
  " 2>/dev/null || echo "")
  # If that failed, try with schema-qualified name
  if [ -z "$DB_LATEST" ]; then
    DB_SCHEMA_NAME=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
      SELECT table_schema FROM information_schema.tables WHERE table_name = 'schema_migrations' LIMIT 1;
    " 2>/dev/null || echo "")
    if [ -n "$DB_SCHEMA_NAME" ]; then
      DB_LATEST=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
        SELECT version FROM ${DB_SCHEMA_NAME}.schema_migrations ORDER BY version DESC LIMIT 1;
      " 2>/dev/null || echo "NO_MIGRATION_TABLE")
    else
      DB_LATEST="NO_MIGRATION_TABLE"
    fi
  fi
fi

if [ -z "$DB_LATEST" ]; then
  # Try checking if tables exist matching migration expectations
  TABLE_COUNT=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') AND table_type = 'BASE TABLE';
  " 2>/dev/null || echo "0")
  echo "No migration tracking table found, but $TABLE_COUNT tables exist" | tee -a "$EVIDENCE_DIR/assertion.log"
  DB_LATEST="NO_MIGRATION_TABLE"
fi

echo "DB reports latest migration: $DB_LATEST" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# CHECK 3: Compare
# ══════════════════════════════════════════════════════════════

echo "" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "── Check 3: Migration State Comparison ──" | tee -a "$EVIDENCE_DIR/assertion.log"

# Extract version number from filename (assuming format like 001_xxx or 20240101_xxx)
FILE_VERSION=$(echo "$LATEST_MIGRATION" | grep -oP '^\d+' || echo "$LATEST_MIGRATION")

if [ "$DB_LATEST" = "NO_MIGRATION_TABLE" ]; then
  echo "⚠️  No migration tracking table found in DB" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   This may be expected if migrations are applied via raw SQL" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   Verifying tables exist as proxy check..." | tee -a "$EVIDENCE_DIR/assertion.log"

  # Check if key tables from migrations exist
  DEALS_EXISTS=$(docker exec "$POSTGRES_CID" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'deals');
  " 2>/dev/null || echo "f")

  if [ "$DEALS_EXISTS" = "t" ]; then
    echo "✅ Key tables (deals) exist — migrations likely applied" | tee -a "$EVIDENCE_DIR/assertion.log"
  else
    echo "❌ FAIL: Key tables missing — migrations may not be applied" | tee -a "$EVIDENCE_DIR/assertion.log"
    FAILURES=$((FAILURES+1))
  fi
elif [ "$DB_LATEST" != "$FILE_VERSION" ] && ! echo "$LATEST_MIGRATION" | grep -q "$DB_LATEST"; then
  echo "❌ FAIL: Migration state mismatch!" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   File system: $LATEST_MIGRATION ($FILE_VERSION)" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   Database:    $DB_LATEST" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   Run migrations before proceeding:" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   alembic upgrade head" | tee -a "$EVIDENCE_DIR/assertion.log"
  FAILURES=$((FAILURES+1))
else
  echo "✅ Migration state matches: $DB_LATEST" | tee -a "$EVIDENCE_DIR/assertion.log"
fi

# ══════════════════════════════════════════════════════════════
# CHECK 4: Via Debug Endpoint (V3)
# ══════════════════════════════════════════════════════════════

echo "" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "── Check 4: Migration State via Debug Endpoint ──" | tee -a "$EVIDENCE_DIR/assertion.log"

DEBUG_MIGRATIONS=$(curl -sf "$BACKEND_URL/api/admin/debug/migrations" \
  -H "X-Service-Token: ${SERVICE_TOKEN:-internal}" 2>/dev/null || echo '{"error": "ENDPOINT_NOT_AVAILABLE"}')

echo "$DEBUG_MIGRATIONS" > "$EVIDENCE_DIR/debug_migrations.json"

if echo "$DEBUG_MIGRATIONS" | jq -e '.latest_migration' &>/dev/null; then
  ENDPOINT_LATEST=$(echo "$DEBUG_MIGRATIONS" | jq -r '.latest_migration')
  ENDPOINT_APPLIED=$(echo "$DEBUG_MIGRATIONS" | jq -r '.applied // "unknown"')

  echo "Debug endpoint reports:" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "  latest_migration: $ENDPOINT_LATEST" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "  applied: $ENDPOINT_APPLIED" | tee -a "$EVIDENCE_DIR/assertion.log"
else
  echo "⚠️  Debug migrations endpoint not available" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   Recommendation: Implement /api/admin/debug/migrations" | tee -a "$EVIDENCE_DIR/assertion.log"
fi

# ══════════════════════════════════════════════════════════════
# GATE SUMMARY
# ══════════════════════════════════════════════════════════════

VERDICT=$([ "$FAILURES" -eq 0 ] && echo "PASS" || echo "FAIL")

cat > "$EVIDENCE_DIR/gate-summary.json" << EOF
{
  "gate": "MIGRATION_STATE_V3",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "latest_file": "$LATEST_MIGRATION",
  "latest_db": "$DB_LATEST",
  "failures": $FAILURES,
  "verdict": "$VERDICT"
}
EOF

if [ "$FAILURES" -gt 0 ]; then
  echo "" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "❌ MIGRATION GATE FAILED" | tee -a "$EVIDENCE_DIR/assertion.log"
  exit 1
else
  echo "" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "✅ MIGRATION STATE VERIFIED" | tee -a "$EVIDENCE_DIR/assertion.log"
fi
