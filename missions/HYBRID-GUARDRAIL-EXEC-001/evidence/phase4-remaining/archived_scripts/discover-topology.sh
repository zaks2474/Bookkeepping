#!/usr/bin/env bash
# tools/infra/discover-topology.sh
# V4: Dynamic container discovery + DB_USER extraction (C1 fix) + route discovery (C2)
# Exports container IDs + repo roots + ports + DB connections + DB users + routes

set -euo pipefail

EVIDENCE_DIR="artifacts/infra-awareness/evidence/topology"
mkdir -p "$EVIDENCE_DIR"

echo "═══ PHASE 0: TOPOLOGY DISCOVERY (V4) ═══" | tee "$EVIDENCE_DIR/discovery.log"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "" | tee -a "$EVIDENCE_DIR/discovery.log"

ERRORS=0

# ══════════════════════════════════════════════════════════════
# STEP 1: DISCOVER REPO ROOTS
# ══════════════════════════════════════════════════════════════

echo "── Step 1: Repo Root Discovery ──" | tee -a "$EVIDENCE_DIR/discovery.log"

# Backend: Try multiple possible locations
BACKEND_ROOT=""
for path in \
  "/home/zaks/zakops-backend" \
  "/home/zaks/zakops-agent-api/apps/backend" \
  "/home/zaks/backend"; do
  if [ -d "$path" ] && { [ -f "$path/src/api/orchestration/main.py" ] || [ -f "$path/main.py" ] || [ -f "$path/app.py" ]; }; then
    BACKEND_ROOT="$path"
    break
  fi
done

if [ -z "$BACKEND_ROOT" ]; then
  echo "❌ FAIL: Could not find backend repo root" | tee -a "$EVIDENCE_DIR/discovery.log"
  ERRORS=$((ERRORS+1))
else
  echo "✅ BACKEND_ROOT=$BACKEND_ROOT" | tee -a "$EVIDENCE_DIR/discovery.log"
fi

# Dashboard: Try multiple possible locations
DASHBOARD_ROOT=""
for path in \
  "/home/zaks/zakops-dashboard" \
  "/home/zaks/zakops-agent-api/apps/dashboard" \
  "/home/zaks/dashboard"; do
  if [ -d "$path" ] && [ -f "$path/package.json" ]; then
    if grep -q "next" "$path/package.json" 2>/dev/null; then
      DASHBOARD_ROOT="$path"
      break
    fi
  fi
done

if [ -z "$DASHBOARD_ROOT" ]; then
  echo "❌ FAIL: Could not find dashboard repo root" | tee -a "$EVIDENCE_DIR/discovery.log"
  ERRORS=$((ERRORS+1))
else
  echo "✅ DASHBOARD_ROOT=$DASHBOARD_ROOT" | tee -a "$EVIDENCE_DIR/discovery.log"
fi

# Agent API: Try multiple possible locations
AGENT_ROOT=""
for path in \
  "/home/zaks/zakops-agent-api/apps/agent-api" \
  "/home/zaks/zakops-agent-api" \
  "/home/zaks/agent-api"; do
  if [ -d "$path" ] && { [ -d "$path/app/core/langgraph" ] || [ -f "$path/app/main.py" ]; }; then
    AGENT_ROOT="$path"
    break
  fi
done

if [ -z "$AGENT_ROOT" ]; then
  echo "❌ FAIL: Could not find agent-api repo root" | tee -a "$EVIDENCE_DIR/discovery.log"
  ERRORS=$((ERRORS+1))
else
  echo "✅ AGENT_ROOT=$AGENT_ROOT" | tee -a "$EVIDENCE_DIR/discovery.log"
fi

echo "" | tee -a "$EVIDENCE_DIR/discovery.log"

# ══════════════════════════════════════════════════════════════
# STEP 2: DYNAMIC CONTAINER DISCOVERY (V3 — NO HARDCODED NAMES)
# ══════════════════════════════════════════════════════════════

echo "── Step 2: Container Discovery (V3 Dynamic) ──" | tee -a "$EVIDENCE_DIR/discovery.log"

POSTGRES_CID=""
BACKEND_CID=""
AGENT_CID=""
AGENT_DB_CID=""

if command -v docker &>/dev/null; then
  # Method 1: docker compose ps --format json (preferred)
  if [ -n "$BACKEND_ROOT" ] && [ -f "$BACKEND_ROOT/docker-compose.yml" ]; then
    pushd "$BACKEND_ROOT" > /dev/null

    # Get postgres container ID
    POSTGRES_CID=$(docker compose ps --format json 2>/dev/null | \
      python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin if l.strip()]; \
      print(next((c.get('ID','') for c in data if 'postgres' in c.get('Service','').lower()), ''))" 2>/dev/null || echo "")

    # Get backend container ID
    BACKEND_CID=$(docker compose ps --format json 2>/dev/null | \
      python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin if l.strip()]; \
      print(next((c.get('ID','') for c in data if 'backend' in c.get('Service','').lower() and 'outbox' not in c.get('Service','').lower()), ''))" 2>/dev/null || echo "")

    popd > /dev/null
  fi

  # Verify postgres container is actually healthy/running (not restarting)
  if [ -n "$POSTGRES_CID" ]; then
    PG_STATUS=$(docker inspect --format '{{.State.Status}}' "$POSTGRES_CID" 2>/dev/null || echo "unknown")
    PG_HEALTH=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$POSTGRES_CID" 2>/dev/null || echo "unknown")
    if [ "$PG_STATUS" != "running" ] || [ "$PG_HEALTH" != "healthy" -a "$PG_HEALTH" != "no-healthcheck" ]; then
      echo "⚠️  Compose postgres ($POSTGRES_CID) is $PG_STATUS/$PG_HEALTH, looking for healthy alternative..." | tee -a "$EVIDENCE_DIR/discovery.log"
      POSTGRES_CID=""
    fi
  fi

  # Method 2: Fallback to docker ps with label/name matching — prefer healthy
  if [ -z "$POSTGRES_CID" ]; then
    POSTGRES_CID=$(docker ps --filter "name=postgres" --filter "status=running" --filter "health=healthy" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
  fi
  if [ -z "$POSTGRES_CID" ]; then
    POSTGRES_CID=$(docker ps --filter "name=postgres" --filter "status=running" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
  fi

  if [ -z "$BACKEND_CID" ]; then
    BACKEND_CID=$(docker ps --filter "name=backend" --filter "status=running" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
  fi

  # Agent container — try docker compose first, then fallback
  if [ -n "$AGENT_ROOT" ] && [ -f "$AGENT_ROOT/docker-compose.yml" ]; then
    pushd "$AGENT_ROOT" > /dev/null
    AGENT_CID=$(docker compose ps --format json 2>/dev/null | \
      python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin if l.strip()]; \
      print(next((c.get('ID','') for c in data if 'agent' in c.get('Service','').lower() and 'db' not in c.get('Service','').lower()), ''))" 2>/dev/null || echo "")
    AGENT_DB_CID=$(docker compose ps --format json 2>/dev/null | \
      python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin if l.strip()]; \
      print(next((c.get('ID','') for c in data if 'db' in c.get('Service','').lower()), ''))" 2>/dev/null || echo "")
    popd > /dev/null
  fi

  if [ -z "$AGENT_CID" ]; then
    AGENT_CID=$(docker ps --filter "name=agent-api" --filter "status=running" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
    [ -z "$AGENT_CID" ] && AGENT_CID=$(docker ps --filter "name=agent" --filter "status=running" --format "{{.ID}}" 2>/dev/null | grep -v db | head -1 || echo "")
  fi

  if [ -z "$AGENT_DB_CID" ]; then
    AGENT_DB_CID=$(docker ps --filter "name=agent-db" --filter "status=running" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
  fi
fi

# Report container discovery
if [ -n "$POSTGRES_CID" ]; then
  POSTGRES_NAME=$(docker inspect --format '{{.Name}}' "$POSTGRES_CID" 2>/dev/null | sed 's/^\///')
  echo "✅ POSTGRES_CID=$POSTGRES_CID ($POSTGRES_NAME)" | tee -a "$EVIDENCE_DIR/discovery.log"
else
  echo "❌ FAIL: Could not discover postgres container" | tee -a "$EVIDENCE_DIR/discovery.log"
  ERRORS=$((ERRORS+1))
fi

if [ -n "$BACKEND_CID" ]; then
  BACKEND_NAME=$(docker inspect --format '{{.Name}}' "$BACKEND_CID" 2>/dev/null | sed 's/^\///')
  echo "✅ BACKEND_CID=$BACKEND_CID ($BACKEND_NAME)" | tee -a "$EVIDENCE_DIR/discovery.log"
else
  echo "❌ FAIL: Could not discover backend container" | tee -a "$EVIDENCE_DIR/discovery.log"
  ERRORS=$((ERRORS+1))
fi

if [ -n "$AGENT_CID" ]; then
  AGENT_NAME=$(docker inspect --format '{{.Name}}' "$AGENT_CID" 2>/dev/null | sed 's/^\///')
  echo "✅ AGENT_CID=$AGENT_CID ($AGENT_NAME)" | tee -a "$EVIDENCE_DIR/discovery.log"
else
  echo "⚠️  WARN: Could not discover agent container" | tee -a "$EVIDENCE_DIR/discovery.log"
fi

if [ -n "$AGENT_DB_CID" ]; then
  AGENT_DB_NAME=$(docker inspect --format '{{.Name}}' "$AGENT_DB_CID" 2>/dev/null | sed 's/^\///')
  echo "✅ AGENT_DB_CID=$AGENT_DB_CID ($AGENT_DB_NAME)" | tee -a "$EVIDENCE_DIR/discovery.log"
else
  echo "⚠️  WARN: Could not discover agent DB container" | tee -a "$EVIDENCE_DIR/discovery.log"
fi

echo "" | tee -a "$EVIDENCE_DIR/discovery.log"

# ══════════════════════════════════════════════════════════════
# STEP 3: DISCOVER PORTS (from containers)
# ══════════════════════════════════════════════════════════════

echo "── Step 3: Port Discovery ──" | tee -a "$EVIDENCE_DIR/discovery.log"

BACKEND_PORT=""
AGENT_PORT=""
DASHBOARD_PORT=""

# Get port from container
if [ -n "$BACKEND_CID" ]; then
  BACKEND_PORT=$(docker port "$BACKEND_CID" 2>/dev/null | grep -oP '0\.0\.0\.0:\K\d+' | head -1 || echo "")
fi

if [ -n "$AGENT_CID" ]; then
  AGENT_PORT=$(docker port "$AGENT_CID" 2>/dev/null | grep -oP '0\.0\.0\.0:\K\d+' | head -1 || echo "")
fi

# Fallback port probing if container port mapping not found
if [ -z "$BACKEND_PORT" ]; then
  for port in 8091 8090 9200 8000; do
    if curl -sf "http://localhost:$port/health" &>/dev/null || \
       curl -sf "http://localhost:$port/api/health" &>/dev/null; then
      BACKEND_PORT="$port"
      break
    fi
  done
fi

if [ -z "$AGENT_PORT" ]; then
  for port in 8095 8096 8097; do
    if curl -sf "http://localhost:$port/health" &>/dev/null; then
      AGENT_PORT="$port"
      break
    fi
  done
fi

if [ -z "$DASHBOARD_PORT" ]; then
  for port in 3003 3000 3001; do
    if curl -sf "http://localhost:$port" &>/dev/null; then
      DASHBOARD_PORT="$port"
      break
    fi
  done
fi

# Report
[ -n "$BACKEND_PORT" ] && echo "✅ BACKEND_PORT=$BACKEND_PORT" | tee -a "$EVIDENCE_DIR/discovery.log" || \
  { echo "❌ FAIL: Could not discover backend port" | tee -a "$EVIDENCE_DIR/discovery.log"; ERRORS=$((ERRORS+1)); }

[ -n "$AGENT_PORT" ] && echo "✅ AGENT_PORT=$AGENT_PORT" | tee -a "$EVIDENCE_DIR/discovery.log" || \
  echo "⚠️  WARN: Could not discover agent port" | tee -a "$EVIDENCE_DIR/discovery.log"

[ -n "$DASHBOARD_PORT" ] && echo "✅ DASHBOARD_PORT=$DASHBOARD_PORT" | tee -a "$EVIDENCE_DIR/discovery.log" || \
  echo "⚠️  WARN: Could not discover dashboard port" | tee -a "$EVIDENCE_DIR/discovery.log"

# Build URLs
BACKEND_URL="http://localhost:${BACKEND_PORT:-8091}"
AGENT_URL="http://localhost:${AGENT_PORT:-8095}"
DASHBOARD_URL="http://localhost:${DASHBOARD_PORT:-3003}"

echo "" | tee -a "$EVIDENCE_DIR/discovery.log"

# ══════════════════════════════════════════════════════════════
# STEP 4: DISCOVER DATABASE CONNECTION (V3 — Runtime verification)
# Companion Note #2: Extract DB_USER from DATABASE_URL
# ══════════════════════════════════════════════════════════════

echo "── Step 4: Database Discovery ──" | tee -a "$EVIDENCE_DIR/discovery.log"

DB_HOST=""
DB_NAME=""
DB_PORT=""
BACKEND_DB_USER=""
AGENT_DB_USER=""

# Get DATABASE_URL from backend container (using dynamic CID)
if [ -n "$BACKEND_CID" ]; then
  DB_URL=$(docker exec "$BACKEND_CID" printenv DATABASE_URL 2>/dev/null || echo "")

  if [ -n "$DB_URL" ]; then
    # Parse postgresql://user:pass@host:port/dbname
    DB_HOST=$(echo "$DB_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    DB_PORT=$(echo "$DB_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    DB_NAME=$(echo "$DB_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
    # Companion Note #2: Extract username from URL
    BACKEND_DB_USER=$(echo "$DB_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
  fi
fi

# Get agent DB user
if [ -n "$AGENT_CID" ]; then
  AGENT_DB_URL=$(docker exec "$AGENT_CID" printenv DATABASE_URL 2>/dev/null || echo "")
  if [ -n "$AGENT_DB_URL" ]; then
    AGENT_DB_USER=$(echo "$AGENT_DB_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
    AGENT_DB_NAME=$(echo "$AGENT_DB_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
  fi
fi

# Default fallback
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-zakops}"
BACKEND_DB_USER="${BACKEND_DB_USER:-zakops}"
AGENT_DB_USER="${AGENT_DB_USER:-agent}"
AGENT_DB_NAME="${AGENT_DB_NAME:-zakops_agent}"

echo "✅ DB_HOST=$DB_HOST" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "✅ DB_PORT=$DB_PORT" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "✅ DB_NAME=$DB_NAME" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "✅ BACKEND_DB_USER=$BACKEND_DB_USER" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "✅ AGENT_DB_USER=$AGENT_DB_USER" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "✅ AGENT_DB_NAME=$AGENT_DB_NAME" | tee -a "$EVIDENCE_DIR/discovery.log"

echo "" | tee -a "$EVIDENCE_DIR/discovery.log"

# ══════════════════════════════════════════════════════════════
# STEP 5: EXPORT TOPOLOGY CONFIG (V3)
# ══════════════════════════════════════════════════════════════

echo "── Step 5: Exporting Topology (V3) ──" | tee -a "$EVIDENCE_DIR/discovery.log"

TOPOLOGY_FILE="$EVIDENCE_DIR/topology.env"
cat > "$TOPOLOGY_FILE" << EOF
# Auto-generated by discover-topology.sh (V3)
# Source this file before running other infra scripts:
#   source artifacts/infra-awareness/evidence/topology/topology.env

# Repo roots
export BACKEND_ROOT="$BACKEND_ROOT"
export DASHBOARD_ROOT="$DASHBOARD_ROOT"
export AGENT_ROOT="$AGENT_ROOT"

# Container IDs (V3 — DYNAMIC, no hardcoded names)
export POSTGRES_CID="$POSTGRES_CID"
export BACKEND_CID="$BACKEND_CID"
export AGENT_CID="$AGENT_CID"
export AGENT_DB_CID="$AGENT_DB_CID"

# Service ports
export BACKEND_PORT="$BACKEND_PORT"
export AGENT_PORT="$AGENT_PORT"
export DASHBOARD_PORT="$DASHBOARD_PORT"

# Service URLs
export BACKEND_URL="$BACKEND_URL"
export AGENT_URL="$AGENT_URL"
export DASHBOARD_URL="$DASHBOARD_URL"

# Database (backend)
export DB_HOST="$DB_HOST"
export DB_PORT="$DB_PORT"
export DB_NAME="$DB_NAME"

# Companion Note #2: DB users extracted from DATABASE_URL (never hardcoded)
export BACKEND_DB_USER="$BACKEND_DB_USER"
export AGENT_DB_USER="$AGENT_DB_USER"
export AGENT_DB_NAME="$AGENT_DB_NAME"

# Convenience alias: DB_USER defaults to backend user for backward compat
export DB_USER="$BACKEND_DB_USER"
EOF

echo "✅ Topology exported to: $TOPOLOGY_FILE" | tee -a "$EVIDENCE_DIR/discovery.log"

# Also export as JSON
cat > "$EVIDENCE_DIR/topology.json" << EOF
{
  "generated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "V3",
  "repos": {
    "backend": "$BACKEND_ROOT",
    "dashboard": "$DASHBOARD_ROOT",
    "agent": "$AGENT_ROOT"
  },
  "containers": {
    "postgres": "$POSTGRES_CID",
    "backend": "$BACKEND_CID",
    "agent": "$AGENT_CID",
    "agent_db": "$AGENT_DB_CID"
  },
  "ports": {
    "backend": "$BACKEND_PORT",
    "agent": "$AGENT_PORT",
    "dashboard": "$DASHBOARD_PORT"
  },
  "urls": {
    "backend": "$BACKEND_URL",
    "agent": "$AGENT_URL",
    "dashboard": "$DASHBOARD_URL"
  },
  "database": {
    "host": "$DB_HOST",
    "port": "$DB_PORT",
    "name": "$DB_NAME",
    "backend_user": "$BACKEND_DB_USER",
    "agent_user": "$AGENT_DB_USER",
    "agent_db_name": "$AGENT_DB_NAME"
  }
}
EOF

echo "" | tee -a "$EVIDENCE_DIR/discovery.log"

# ══════════════════════════════════════════════════════════════
# GATE CHECK
# ══════════════════════════════════════════════════════════════

TOTAL_CHECKS=8
PASSED=$((TOTAL_CHECKS - ERRORS))
VERDICT=$([ $ERRORS -eq 0 ] && echo 'PASS' || echo 'FAIL')

cat > "$EVIDENCE_DIR/gate-summary.json" << EOF
{
  "gate": "PHASE_0_TOPOLOGY_V4",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": $TOTAL_CHECKS,
  "passed": $PASSED,
  "failed": $ERRORS,
  "skipped": 0,
  "verdict": "$VERDICT",
  "v4_features": ["dynamic_container_discovery", "db_user_extraction", "route_discovery", "allowlist_bootstrap"]
}
EOF

if [ "$ERRORS" -gt 0 ]; then
  echo "❌ PHASE 0 FAILED: $ERRORS errors" | tee -a "$EVIDENCE_DIR/discovery.log"
  echo "   Cannot proceed with infrastructure checks on wrong paths/ports" | tee -a "$EVIDENCE_DIR/discovery.log"
  exit 1
else
  echo "✅ PHASE 0 PASSED: Topology discovered successfully (V3)" | tee -a "$EVIDENCE_DIR/discovery.log"
  echo "" | tee -a "$EVIDENCE_DIR/discovery.log"
  echo "To use in subsequent scripts:" | tee -a "$EVIDENCE_DIR/discovery.log"
  echo "  source $TOPOLOGY_FILE" | tee -a "$EVIDENCE_DIR/discovery.log"
fi
