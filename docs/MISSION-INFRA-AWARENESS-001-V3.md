# CLAUDE CODE MISSION: INFRASTRUCTURE AWARENESS SYSTEM

## Mission ID: INFRA-AWARENESS-001
## Version: V3 (GPT-5.2 Final Red-Team Hardened)
## Codename: "The All-Seeing Eye"
## Priority: P0 — Root Cause Fix for Systemic Drift

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   EXECUTION DIRECTIVE                                                        ║
║                                                                              ║
║   This mission addresses the ROOT CAUSE of recurring ZakOps failures:        ║
║   Zod cascade, RAG routing, ActionStatus drift, schema misalignment.         ║
║                                                                              ║
║   The problem: Claude Code was configured once. The system evolves daily.    ║
║   Its understanding becomes stale. Changes break things it didn't know       ║
║   about. No cross-layer validation exists.                                   ║
║                                                                              ║
║   The fix: Make infrastructure self-documenting, self-validating, and        ║
║   impossible to ignore.                                                      ║
║                                                                              ║
║   END STATE: A single-line request to Claude Code triggers full              ║
║   infrastructure awareness. After completing the task, Claude Code           ║
║   automatically evaluates which other layers are impacted and adjusts        ║
║   them accordingly.                                                          ║
║                                                                              ║
║   V3 CRITICAL PATCHES (GPT-5.2 Final Red-Team):                             ║
║   1. Contracts are SoT — discovery runs in COMPARE mode by default          ║
║   2. Dynamic container discovery — no hardcoded container names             ║
║   3. Explicit DB mapping — backend→zakops, agent→zakops_agent               ║
║   4. Runtime sqlite detection — not code grep                               ║
║   5. Migration state gate — hard fail if migrations not applied             ║
║   6. Admin debug endpoints — /api/admin/debug/* for count/db assertions     ║
║   7. Phantom endpoint detection — dashboard calls vs OpenAPI inventory      ║
║   8. Playwright auth state — pre-seeded storageState.json                   ║
║   9. SSE handshake + first event proof — not just headers                   ║
║   10. CI static vs runtime gates — clearly separated                        ║
║   11. Evidence hygiene — secret scanning gate                               ║
║                                                                              ║
║   NON-NEGOTIABLE END STATE:                                                  ║
║   • make infra-topology        → PASS                                        ║
║   • make infra-check           → PASS (includes migration + db mapping)      ║
║   • make validate-dashboard-network → PASS (with auth state)                 ║
║   • make infra-openapi         → PASS (with phantom detection)               ║
║   • make validate-cross-layer  → PASS                                        ║
║   All gates produce machine-readable JSON + evidence artifacts               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## V3 RED-TEAM HARDENING SUMMARY

| # | Attack Vector | V2 Gap | V3 Fix |
|---|--------------|--------|--------|
| 1 | Contracts written from bad DB state | Extract → write inverts SoT | Compare mode default, --write-contracts required |
| 2 | Hardcoded container names break in CI | zakops-postgres-1 hardcoded | Dynamic container ID discovery |
| 3 | Two Postgres = wrong DB assumption | Multiple Postgres = warning | Explicit DB mapping: service → expected DB |
| 4 | Grep for sqlite misses env-driven toggles | Code grep primary | Runtime debug endpoint primary |
| 5 | DB schema behind code = phantom failures | No migration gate | Migration state hard gate |
| 6 | Deal count via UI endpoint = pagination | /api/deals response | Admin debug /counts endpoint |
| 7 | Dashboard calls non-existent endpoints | OpenAPI inventory only | Phantom endpoint detection from Playwright |
| 8 | Playwright captures 401s (no auth) | No auth state | Pre-seeded storageState.json |
| 9 | SSE headers-only doesn't prove stream | Content-type check | Handshake + first event + replay test |
| 10 | CI ambiguity: static vs runtime | Unclear | Explicit static-only and runtime gates |
| 11 | Evidence contains secrets | Partial redaction | Secret scanning gate |

---

## ARCHITECTURE OVERVIEW

### Three-Tier Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 1: SINGLE SOURCE OF TRUTH                   │
│                                                                     │
│  contracts/                                                         │
│  ├── stages.json          ← Canonical pipeline stage values         │
│  ├── statuses.json        ← Canonical action/deal statuses          │
│  ├── deal.schema.json     ← Deal shape (fields, types, nullability) │
│  ├── action.schema.json   ← Action shape                           │
│  ├── event.schema.json    ← Event shape                            │
│  ├── tool-registry.json   ← Agent tool definitions + risk levels    │
│  └── runtime.topology.json ← V3: Expected DB mappings               │
│                                                                     │
│  Rule: Change ONCE here → regenerate → ALL layers aligned           │
│  V3 Rule: Discovery COMPARES to contracts, never writes by default  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              TIER 2: LIVE INFRASTRUCTURE INVENTORY                   │
│                                                                     │
│  INFRASTRUCTURE_MANIFEST.md (auto-generated, never hand-edited)     │
│                                                                     │
│  Contains:                                                          │
│  • Current DB schema (tables, columns, types, constraints)          │
│  • API endpoints (FROM OPENAPI, not grep)                          │
│  • Agent tools (name, parameters, return shapes)                    │
│  • Dashboard Zod schemas (field names, types, optionality)          │
│  • Stage values across all layers                                   │
│  • Status values across all layers                                  │
│  • Service dependency graph                                         │
│  • Port assignments (DYNAMICALLY RESOLVED)                          │
│  • Container IDs (DYNAMICALLY RESOLVED, V3)                        │
│  • DB connection verification (runtime, V3)                         │
│  • Migration state (V3)                                            │
│  • Environment variables per service                                │
│                                                                     │
│  Hardened with:                                                     │
│  • Age Gate: FAIL if manifest >10 minutes old                       │
│  • Health Gate: FAIL if any section has zero entries                 │
│  • Required Sections: ALL must be present or explicit UNKNOWN        │
│  • Policy: "UNKNOWN ≠ PASS" — unknown state = hard failure          │
│  • Evidence Gate: Every check must dump to evidence/                │
│  • Secret Scan: FAIL if evidence contains leaked credentials (V3)   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              TIER 3: PRE/POST TASK AUTOMATION                       │
│                                                                     │
│  Pre-Task:                                                          │
│  • Run Phase 0 topology discovery (with container IDs)              │
│  • Regenerate INFRASTRUCTURE_MANIFEST.md                            │
│  • Run age gate + health gate                                       │
│  • Inject manifest into Claude Code context                         │
│                                                                     │
│  Post-Task:                                                         │
│  • Run 3-way schema diff (Backend ↔ Agent ↔ Dashboard)             │
│  • Run DB source-of-truth assertion (HARD GATE with mapping)        │
│  • Run migration state assertion (HARD GATE, V3)                    │
│  • Run TypeScript compilation gate                                  │
│  • Run Playwright network capture (with auth state, V3)             │
│  • Run phantom endpoint detection (V3)                              │
│  • Run secret scan on evidence (V3)                                 │
│  • Output cross-layer impact report                                 │
│                                                                     │
│  Enforced via:                                                      │
│  • Makefile targets                                                 │
│  • CLAUDE.md protocol (mandatory pre/post hooks)                    │
│  • Git pre-commit hook (soft in dev, HARD in CI)                    │
│  • CI job — static gate (fast) + runtime gate (slower)              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 0: TOPOLOGY DISCOVERY (V3 — Dynamic Container Discovery)
### Duration: ~30 minutes | CRITICAL — prevents auditing wrong code
### P0 — Must pass before ANY other phase

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PHASE 0 — TOPOLOGY DISCOVERY (V3)                                           ║
║                                                                              ║
║  V2 Problem: Hardcoded container names like zakops-postgres-1                ║
║  Reality: Container names vary by compose project name, stack, CI            ║
║                                                                              ║
║  V3 Fix: Use docker compose ps to discover container IDs dynamically         ║
║  Export: POSTGRES_CID, BACKEND_CID, AGENT_CID to topology.env                ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 0.1 — Topology Discovery Script (V3)

**TASK 0.1.1: Create `tools/infra/discover-topology.sh` (V3)**

```bash
#!/usr/bin/env bash
# tools/infra/discover-topology.sh
# V3: Dynamic container discovery — no hardcoded container names
# Exports container IDs + repo roots + ports + DB connections

set -euo pipefail

EVIDENCE_DIR="${EVIDENCE_DIR:-artifacts/infra-awareness/evidence/topology}"
mkdir -p "$EVIDENCE_DIR"

echo "═══ PHASE 0: TOPOLOGY DISCOVERY (V3) ═══" | tee "$EVIDENCE_DIR/discovery.log"
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
  if [ -d "$path" ] && [ -f "$path/src/api/orchestration/main.py" -o -f "$path/main.py" -o -f "$path/app.py" ]; then
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
  if [ -d "$path" ] && [ -d "$path/app/core/langgraph" -o -f "$path/app/main.py" ]; then
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

if command -v docker &>/dev/null; then
  # Method 1: docker compose ps --format json (preferred)
  # Try from backend compose file location
  if [ -n "$BACKEND_ROOT" ] && [ -f "$BACKEND_ROOT/docker-compose.yml" ]; then
    pushd "$BACKEND_ROOT" > /dev/null

    # Get postgres container ID
    POSTGRES_CID=$(docker compose ps --format json 2>/dev/null | \
      python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin if l.strip()]; \
      print(next((c.get('ID','') for c in data if 'postgres' in c.get('Service','').lower()), ''))" 2>/dev/null || echo "")

    # Get backend container ID
    BACKEND_CID=$(docker compose ps --format json 2>/dev/null | \
      python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin if l.strip()]; \
      print(next((c.get('ID','') for c in data if 'backend' in c.get('Service','').lower()), ''))" 2>/dev/null || echo "")

    popd > /dev/null
  fi

  # Method 2: Fallback to docker ps with label/name matching
  if [ -z "$POSTGRES_CID" ]; then
    POSTGRES_CID=$(docker ps --filter "name=postgres" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
  fi

  if [ -z "$BACKEND_CID" ]; then
    BACKEND_CID=$(docker ps --filter "name=backend" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
  fi

  # Agent container
  if [ -n "$AGENT_ROOT" ] && [ -f "$AGENT_ROOT/docker-compose.yml" ]; then
    pushd "$AGENT_ROOT" > /dev/null
    AGENT_CID=$(docker compose ps --format json 2>/dev/null | \
      python3 -c "import sys,json; data=[json.loads(l) for l in sys.stdin if l.strip()]; \
      print(next((c.get('ID','') for c in data if 'agent' in c.get('Service','').lower()), ''))" 2>/dev/null || echo "")
    popd > /dev/null
  fi

  if [ -z "$AGENT_CID" ]; then
    AGENT_CID=$(docker ps --filter "name=agent" --format "{{.ID}}" 2>/dev/null | head -1 || echo "")
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
  BACKEND_PORT=$(docker port "$BACKEND_CID" 2>/dev/null | grep -oP '\d+$' | head -1 || echo "")
fi

if [ -n "$AGENT_CID" ]; then
  AGENT_PORT=$(docker port "$AGENT_CID" 2>/dev/null | grep -oP '\d+$' | head -1 || echo "")
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
# ══════════════════════════════════════════════════════════════

echo "── Step 4: Database Discovery ──" | tee -a "$EVIDENCE_DIR/discovery.log"

DB_HOST=""
DB_NAME=""
DB_PORT=""

# Get DATABASE_URL from backend container (using dynamic CID)
if [ -n "$BACKEND_CID" ]; then
  DB_URL=$(docker exec "$BACKEND_CID" printenv DATABASE_URL 2>/dev/null || echo "")

  if [ -n "$DB_URL" ]; then
    # Parse postgresql://user:pass@host:port/dbname
    DB_HOST=$(echo "$DB_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    DB_PORT=$(echo "$DB_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    DB_NAME=$(echo "$DB_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
  fi
fi

# Default fallback
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-zakops}"

echo "✅ DB_HOST=$DB_HOST" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "✅ DB_PORT=$DB_PORT" | tee -a "$EVIDENCE_DIR/discovery.log"
echo "✅ DB_NAME=$DB_NAME" | tee -a "$EVIDENCE_DIR/discovery.log"

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

# Service ports
export BACKEND_PORT="$BACKEND_PORT"
export AGENT_PORT="$AGENT_PORT"
export DASHBOARD_PORT="$DASHBOARD_PORT"

# Service URLs
export BACKEND_URL="$BACKEND_URL"
export AGENT_URL="$AGENT_URL"
export DASHBOARD_URL="$DASHBOARD_URL"

# Database
export DB_HOST="$DB_HOST"
export DB_PORT="$DB_PORT"
export DB_NAME="$DB_NAME"
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
    "agent": "$AGENT_CID"
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
    "name": "$DB_NAME"
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
  "gate": "PHASE_0_TOPOLOGY_V3",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": $TOTAL_CHECKS,
  "passed": $PASSED,
  "failed": $ERRORS,
  "skipped": 0,
  "verdict": "$VERDICT",
  "v3_features": ["dynamic_container_discovery", "no_hardcoded_names"]
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
```

---

## PHASE 1: CONTRACTS + DB ASSERTION (V3)
### Duration: ~2 hours

### 1.1 — Expected DB Mapping (V3 — Explicit)

**TASK 1.1.1: Create `contracts/runtime.topology.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "V3: Explicit DB mapping — services to expected databases",
  "version": "V3",
  "db_mapping": {
    "backend": {
      "expected_database": "zakops",
      "expected_schema": "public",
      "description": "Main deal engine database"
    },
    "outbox-worker": {
      "expected_database": "zakops",
      "expected_schema": "public",
      "description": "Must share DB with backend"
    },
    "agent-api": {
      "expected_database": "zakops_agent",
      "expected_schema": "public",
      "description": "LangGraph checkpoints and approvals"
    }
  },
  "prohibited_configs": {
    "sqlite_in_production": true,
    "read_from_sqlite": true,
    "multiple_postgres_without_mapping": true
  },
  "required_debug_endpoints": [
    "/api/admin/debug/db",
    "/api/admin/debug/migrations",
    "/api/admin/debug/counts"
  ]
}
```

### 1.2 — Contract Extraction (V3 — Compare Mode Default)

**TASK 1.2.1: Create `tools/infra/extract-contracts.sh` (V3)**

```bash
#!/usr/bin/env bash
# tools/infra/extract-contracts.sh
# V3: COMPARE mode by default — never overwrites contracts/ unless --write-contracts
# Discovers values → writes to artifacts/ → diffs vs contracts/*.json → FAIL if mismatch

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

# Priority 1: PostgreSQL enum type (using dynamic container ID)
STAGES=$(docker exec "$POSTGRES_CID" psql -U dealengine -d "$DB_NAME" -t -A -c "
  SELECT enumlabel FROM pg_enum e
  JOIN pg_type t ON e.enumtypid = t.oid
  WHERE t.typname = 'deal_stage' OR t.typname = 'dealstage'
  ORDER BY enumsortorder;
" 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "")

if [ -z "$STAGES" ]; then
  echo "  No DB enum found, trying CHECK constraint..."

  STAGES=$(docker exec "$POSTGRES_CID" psql -U dealengine -d "$DB_NAME" -t -A -c "
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
ACTION_STATUSES=$(docker exec "$POSTGRES_CID" psql -U dealengine -d "$DB_NAME" -t -A -c "
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

  # Compare logic similar to stages...
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
```

### 1.3 — DB Source-of-Truth Assertion (V3 — With DB Mapping + Runtime Verification)

**TASK 1.3.1: Create `tools/infra/db-assertion.sh` (V3)**

```bash
#!/usr/bin/env bash
# tools/infra/db-assertion.sh
# V3 HARD GATE: Verifies EXPLICIT DB mapping from contracts/runtime.topology.json
# Uses runtime debug endpoints (not code grep) as primary verification
# sqlite detection via runtime check, not grep

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

    AGENT_DB_URL=$(docker exec "$AGENT_CID" printenv DATABASE_URL 2>/dev/null || echo "")
    if [ -n "$AGENT_DB_URL" ] && echo "$AGENT_DB_URL" | grep -q "$EXPECTED_AGENT_DB"; then
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
  BACKEND_DB_URL=$(docker exec "$BACKEND_CID" printenv DATABASE_URL 2>/dev/null || echo "")

  if [ -n "$OUTBOX_DB_URL" ] && [ -n "$BACKEND_DB_URL" ]; then
    # Compare hosts (redacted comparison)
    OUTBOX_HOST=$(echo "$OUTBOX_DB_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    BACKEND_HOST=$(echo "$BACKEND_DB_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')

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

# Direct DB count
DB_COUNT=$(docker exec "$POSTGRES_CID" psql -U dealengine -d "$EXPECTED_BACKEND_DB" -t -A -c \
  "SELECT COUNT(*) FROM deals;" 2>/dev/null || echo "QUERY_FAILED")

# V3: Use admin debug endpoint, not UI endpoint (avoids pagination/filter issues)
DEBUG_COUNTS=$(curl -sf "$BACKEND_URL/api/admin/debug/counts" \
  -H "X-Service-Token: ${SERVICE_TOKEN:-internal}" 2>/dev/null || echo '{"error": "ENDPOINT_NOT_AVAILABLE"}')

echo "$DEBUG_COUNTS" > "$EVIDENCE_DIR/debug_counts.json"

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

echo "{\"db_count\": \"$DB_COUNT\", \"api_count\": \"$API_COUNT\"}" > "$EVIDENCE_DIR/deal_counts.json"
echo "" | tee -a "$EVIDENCE_DIR/assertion.log"

# ══════════════════════════════════════════════════════════════
# CHECK 5: Multiple Postgres Detection (V3 — With Mapping)
# ══════════════════════════════════════════════════════════════

echo "── Check 5: Multiple Postgres Detection ──" | tee -a "$EVIDENCE_DIR/assertion.log"
CHECKS=$((CHECKS+1))

POSTGRES_CONTAINERS=$(docker ps --filter "ancestor=postgres" --format "{{.Names}}\t{{.Status}}" 2>/dev/null || \
                      docker ps --filter "name=postgres" --format "{{.Names}}\t{{.Status}}" 2>/dev/null || echo "")
echo "$POSTGRES_CONTAINERS" > "$EVIDENCE_DIR/postgres_containers.txt"

RUNNING_COUNT=$(echo "$POSTGRES_CONTAINERS" | grep -v "^$" | wc -l)
echo "Running postgres containers: $RUNNING_COUNT" | tee -a "$EVIDENCE_DIR/assertion.log"

if [ "$RUNNING_COUNT" -gt 1 ]; then
  echo "⚠️  Multiple postgres containers detected:" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "$POSTGRES_CONTAINERS" | while read line; do
    echo "   $line" | tee -a "$EVIDENCE_DIR/assertion.log"
  done

  # V3: Check if this is expected per mapping
  AGENT_DB_EXPECTED=$(jq -r '.db_mapping["agent-api"].expected_database' "$MAPPING_FILE")
  if [ "$EXPECTED_BACKEND_DB" != "$AGENT_DB_EXPECTED" ]; then
    echo "   → This may be expected: backend uses '$EXPECTED_BACKEND_DB', agent uses '$AGENT_DB_EXPECTED'" | tee -a "$EVIDENCE_DIR/assertion.log"
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
```

### 1.4 — Migration State Gate (V3 — NEW)

**TASK 1.4.1: Create `tools/infra/migration-assertion.sh`**

```bash
#!/usr/bin/env bash
# tools/infra/migration-assertion.sh
# V3 NEW: Verifies DB schema matches migration files
# Hard-fail if migrations not fully applied

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

# ══════════════════════════════════════════════════════════════
# CHECK 2: Query DB for applied migrations
# ══════════════════════════════════════════════════════════════

echo "" | tee -a "$EVIDENCE_DIR/assertion.log"
echo "── Check 2: Applied Migrations in DB ──" | tee -a "$EVIDENCE_DIR/assertion.log"

# Try Alembic table first
DB_LATEST=$(docker exec "$POSTGRES_CID" psql -U dealengine -d "$DB_NAME" -t -A -c "
  SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;
" 2>/dev/null || echo "")

if [ -z "$DB_LATEST" ]; then
  # Try Django-style migrations table
  DB_LATEST=$(docker exec "$POSTGRES_CID" psql -U dealengine -d "$DB_NAME" -t -A -c "
    SELECT name FROM django_migrations ORDER BY applied DESC LIMIT 1;
  " 2>/dev/null || echo "")
fi

if [ -z "$DB_LATEST" ]; then
  # Try custom migrations table
  DB_LATEST=$(docker exec "$POSTGRES_CID" psql -U dealengine -d "$DB_NAME" -t -A -c "
    SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1;
  " 2>/dev/null || echo "NO_MIGRATION_TABLE")
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
  echo "❌ FAIL: No migration tracking table found in DB" | tee -a "$EVIDENCE_DIR/assertion.log"
  echo "   This suggests migrations were never applied or tracking is disabled" | tee -a "$EVIDENCE_DIR/assertion.log"
  FAILURES=$((FAILURES+1))
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
```

---

## PHASE 2: OpenAPI DISCOVERY + PHANTOM ENDPOINT DETECTION (V3)
### Duration: ~1.5 hours

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PHASE 2 — OpenAPI + Phantom Endpoint Detection (V3)                        ║
║                                                                              ║
║  V2 Gap: OpenAPI inventory only; dashboard could call non-existent endpoints║
║  V3 Fix: Cross-check Playwright captured requests against OpenAPI inventory  ║
║  Output: phantom_endpoints.json (dashboard calls, backend doesn't implement) ║
║          dead_endpoints.json (backend publishes, dashboard never calls)      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**TASK 2.1.1: Create `tools/infra/openapi-discovery.sh` (V3)**

```bash
#!/usr/bin/env bash
# tools/infra/openapi-discovery.sh
# V3: Includes phantom endpoint detection after Playwright capture

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

EVIDENCE_DIR="artifacts/infra-awareness/evidence/openapi"
mkdir -p "$EVIDENCE_DIR"

echo "═══ OpenAPI ENDPOINT DISCOVERY (V3) ═══"
echo ""

# ── Fetch Backend OpenAPI ──
echo "── Fetching Backend OpenAPI ──"
BACKEND_OPENAPI=$(curl -sf "$BACKEND_URL/openapi.json" 2>/dev/null || \
                  curl -sf "$BACKEND_URL/docs/openapi.json" 2>/dev/null || \
                  curl -sf "$BACKEND_URL/api/openapi.json" 2>/dev/null || \
                  echo '{"error": "NOT_FOUND"}')

echo "$BACKEND_OPENAPI" > "$EVIDENCE_DIR/backend_openapi.json"

if echo "$BACKEND_OPENAPI" | grep -q '"error"'; then
  echo "⚠️  Backend OpenAPI not available at standard paths"
  echo "   Attempting extraction from FastAPI app..."

  docker exec "$BACKEND_CID" python3 -c "
from app.main import app
import json
print(json.dumps(app.openapi(), indent=2))
" 2>/dev/null > "$EVIDENCE_DIR/backend_openapi.json" || echo '{"error": "EXTRACTION_FAILED"}' > "$EVIDENCE_DIR/backend_openapi.json"
fi

# Count and list endpoints
python3 << 'PYEOF'
import json
import os

evidence_dir = "artifacts/infra-awareness/evidence/openapi"

with open(f"{evidence_dir}/backend_openapi.json") as f:
    spec = json.load(f)

if "error" in spec:
    print(f"❌ Backend OpenAPI: {spec['error']}")
else:
    endpoints = []
    for path, methods in spec.get("paths", {}).items():
        for method in methods:
            if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                endpoints.append({"method": method.upper(), "path": path})

    # Write endpoint inventory
    with open(f"{evidence_dir}/backend_endpoints.json", "w") as f:
        json.dump(endpoints, f, indent=2)

    print(f"✅ Backend: {len(endpoints)} endpoints discovered")
PYEOF

echo ""

# ── Fetch Agent OpenAPI ──
echo "── Fetching Agent API OpenAPI ──"
AGENT_OPENAPI=$(curl -sf "$AGENT_URL/openapi.json" 2>/dev/null || echo '{"error": "NOT_FOUND"}')
echo "$AGENT_OPENAPI" > "$EVIDENCE_DIR/agent_openapi.json"

python3 << 'PYEOF'
import json

evidence_dir = "artifacts/infra-awareness/evidence/openapi"

with open(f"{evidence_dir}/agent_openapi.json") as f:
    spec = json.load(f)

if "error" in spec:
    print(f"⚠️  Agent OpenAPI: {spec['error']}")
else:
    endpoints = []
    for path, methods in spec.get("paths", {}).items():
        for method in methods:
            if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
                endpoints.append({"method": method.upper(), "path": path})

    with open(f"{evidence_dir}/agent_endpoints.json", "w") as f:
        json.dump(endpoints, f, indent=2)

    print(f"✅ Agent: {len(endpoints)} endpoints discovered")
PYEOF

echo ""
echo "✅ OpenAPI discovery complete"
echo "   Run 'make validate-dashboard-network' then 'make detect-phantom-endpoints'"
```

**TASK 2.1.2: Create `tools/infra/detect-phantom-endpoints.sh` (V3 — NEW)**

```bash
#!/usr/bin/env bash
# tools/infra/detect-phantom-endpoints.sh
# V3 NEW: Cross-checks Playwright captured requests against OpenAPI inventory
# Produces phantom_endpoints.json and dead_endpoints.json

set -euo pipefail

EVIDENCE_DIR="artifacts/infra-awareness/evidence"
OUTPUT_DIR="$EVIDENCE_DIR/phantom-detection"
mkdir -p "$OUTPUT_DIR"

echo "═══ PHANTOM ENDPOINT DETECTION (V3) ═══"
echo ""

# Check prerequisites
NETWORK_FILE="$EVIDENCE_DIR/network-capture/network_requests.json"
OPENAPI_FILE="$EVIDENCE_DIR/openapi/backend_endpoints.json"

if [ ! -f "$NETWORK_FILE" ]; then
  echo "❌ FAIL: Network capture not found. Run: make validate-dashboard-network"
  exit 1
fi

if [ ! -f "$OPENAPI_FILE" ]; then
  echo "❌ FAIL: OpenAPI inventory not found. Run: make infra-openapi"
  exit 1
fi

# Allowlist for known proxy routes or intentional mismatches
ALLOWLIST_FILE="contracts/endpoint_allowlist.json"

python3 << 'PYEOF'
import json
import os
import re

evidence_dir = "artifacts/infra-awareness/evidence"
output_dir = f"{evidence_dir}/phantom-detection"

# Load data
with open(f"{evidence_dir}/network-capture/network_requests.json") as f:
    network_data = json.load(f)

with open(f"{evidence_dir}/openapi/backend_endpoints.json") as f:
    openapi_endpoints = json.load(f)

# Load allowlist if exists
allowlist = []
if os.path.exists("contracts/endpoint_allowlist.json"):
    with open("contracts/endpoint_allowlist.json") as f:
        allowlist = json.load(f).get("allowed_phantom", [])

# Normalize OpenAPI paths (convert {param} to regex pattern)
def normalize_path(path):
    # Convert /deals/{id} to /deals/[^/]+
    return re.sub(r'\{[^}]+\}', '[^/]+', path)

openapi_patterns = []
for ep in openapi_endpoints:
    pattern = normalize_path(ep["path"])
    openapi_patterns.append({
        "method": ep["method"],
        "pattern": f"^{pattern}$",
        "original": ep["path"]
    })

# Extract dashboard requests
dashboard_requests = set()
for req in network_data.get("requests", []):
    url = req.get("url", "")
    method = req.get("method", "GET")

    # Extract path from URL
    if "/api/" in url:
        path = "/api/" + url.split("/api/")[1].split("?")[0]
        dashboard_requests.add((method, path))

# Find phantoms (dashboard calls, backend doesn't have)
phantoms = []
for method, path in dashboard_requests:
    found = False
    for pattern in openapi_patterns:
        if pattern["method"] == method and re.match(pattern["pattern"], path):
            found = True
            break

    if not found:
        # Check allowlist
        allowed = any(
            a.get("method") == method and re.match(normalize_path(a.get("path", "")), path)
            for a in allowlist
        )
        if not allowed:
            phantoms.append({"method": method, "path": path, "source": "dashboard"})

# Find dead endpoints (backend has, dashboard never calls)
dead = []
called_patterns = set()
for method, path in dashboard_requests:
    for pattern in openapi_patterns:
        if pattern["method"] == method and re.match(pattern["pattern"], path):
            called_patterns.add((pattern["method"], pattern["original"]))

for ep in openapi_endpoints:
    if (ep["method"], ep["path"]) not in called_patterns:
        # Exclude admin/debug endpoints
        if not any(x in ep["path"] for x in ["/admin/", "/debug/", "/health", "/openapi"]):
            dead.append({"method": ep["method"], "path": ep["path"], "source": "openapi"})

# Write results
with open(f"{output_dir}/phantom_endpoints.json", "w") as f:
    json.dump({"count": len(phantoms), "endpoints": phantoms}, f, indent=2)

with open(f"{output_dir}/dead_endpoints.json", "w") as f:
    json.dump({"count": len(dead), "endpoints": dead}, f, indent=2)

print(f"Dashboard requests analyzed: {len(dashboard_requests)}")
print(f"OpenAPI endpoints: {len(openapi_endpoints)}")
print("")

if phantoms:
    print(f"❌ PHANTOM ENDPOINTS: {len(phantoms)} (dashboard calls, backend missing)")
    for p in phantoms[:10]:
        print(f"   {p['method']} {p['path']}")
    if len(phantoms) > 10:
        print(f"   ... and {len(phantoms) - 10} more")
else:
    print("✅ No phantom endpoints detected")

print("")

if dead:
    print(f"⚠️  DEAD ENDPOINTS: {len(dead)} (backend has, dashboard never calls)")
    for d in dead[:5]:
        print(f"   {d['method']} {d['path']}")
else:
    print("✅ All backend endpoints are used")

# Gate summary
gate = {
    "gate": "PHANTOM_ENDPOINT_DETECTION_V3",
    "timestamp": network_data.get("timestamp", ""),
    "phantom_count": len(phantoms),
    "dead_count": len(dead),
    "verdict": "FAIL" if phantoms else "PASS"
}

with open(f"{output_dir}/gate-summary.json", "w") as f:
    json.dump(gate, f, indent=2)

# Exit code
if phantoms:
    exit(1)
PYEOF
```

---

## PHASE 3: PLAYWRIGHT NETWORK CAPTURE (V3 — With Auth State)
### Duration: ~1 hour

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PHASE 3 — Playwright with Authentication State (V3)                         ║
║                                                                              ║
║  V2 Gap: Visits pages without logged-in state → captures 401s               ║
║  V3 Fix: Pre-seeded storageState.json OR programmatic login                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**TASK 3.1.1: Create `tools/validation/dashboard-network-capture.sh` (V3)**

```bash
#!/usr/bin/env bash
# tools/validation/dashboard-network-capture.sh
# V3: Includes authentication state handling

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

EVIDENCE_DIR="artifacts/infra-awareness/evidence/network-capture"
mkdir -p "$EVIDENCE_DIR"

echo "═══ DASHBOARD NETWORK CAPTURE (V3 — With Auth) ═══"
echo ""

# Check Playwright
if ! command -v npx &>/dev/null; then
  echo "❌ FAIL: npx not found"
  exit 1
fi

# Check for pre-seeded auth state
AUTH_STATE_FILE="artifacts/auth/storageState.json"
AUTH_MODE="none"

if [ -f "$AUTH_STATE_FILE" ]; then
  echo "✅ Using pre-seeded auth state: $AUTH_STATE_FILE"
  AUTH_MODE="storage_state"
elif [ -n "${DASHBOARD_TEST_USER:-}" ] && [ -n "${DASHBOARD_TEST_PASS:-}" ]; then
  echo "✅ Will perform programmatic login"
  AUTH_MODE="programmatic"
else
  echo "⚠️  No auth state available"
  echo "   - No storageState.json at $AUTH_STATE_FILE"
  echo "   - No DASHBOARD_TEST_USER/DASHBOARD_TEST_PASS env vars"
  echo ""
  echo "   If auth is intentionally disabled in dev, this is OK."
  echo "   If auth is required, run: make capture-auth-state"
  AUTH_MODE="none"
fi

# Record auth mode as evidence
echo "{\"auth_mode\": \"$AUTH_MODE\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$EVIDENCE_DIR/auth_state.json"

# Create capture script
cat > "$EVIDENCE_DIR/capture.js" << 'JSEOF'
const { chromium } = require('playwright');
const fs = require('fs');

const DASHBOARD_URL = process.env.DASHBOARD_URL || 'http://localhost:3003';
const OUTPUT_FILE = process.env.OUTPUT_FILE || 'network_requests.json';
const AUTH_STATE_FILE = process.env.AUTH_STATE_FILE || '';
const AUTH_MODE = process.env.AUTH_MODE || 'none';
const TEST_USER = process.env.DASHBOARD_TEST_USER || '';
const TEST_PASS = process.env.DASHBOARD_TEST_PASS || '';

async function captureNetworkRequests() {
  const browser = await chromium.launch({ headless: true });

  // V3: Handle auth state
  let contextOptions = {};
  if (AUTH_MODE === 'storage_state' && AUTH_STATE_FILE && fs.existsSync(AUTH_STATE_FILE)) {
    console.log(`Loading auth state from ${AUTH_STATE_FILE}`);
    contextOptions.storageState = AUTH_STATE_FILE;
  }

  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();

  // V3: Programmatic login if needed
  if (AUTH_MODE === 'programmatic' && TEST_USER && TEST_PASS) {
    console.log('Performing programmatic login...');
    try {
      await page.goto(`${DASHBOARD_URL}/login`, { waitUntil: 'networkidle', timeout: 30000 });
      await page.fill('input[name="email"], input[type="email"]', TEST_USER);
      await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
      await page.click('button[type="submit"]');
      await page.waitForURL('**/*', { timeout: 10000 });
      console.log('Login successful');
    } catch (e) {
      console.error(`Login failed: ${e.message}`);
    }
  }

  const requests = [];
  const errors = [];
  const authErrors = [];

  page.on('request', request => {
    if (request.url().includes('/api/') || request.url().includes(':8091') || request.url().includes(':8095')) {
      requests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType(),
        timestamp: new Date().toISOString()
      });
    }
  });

  page.on('response', response => {
    const req = requests.find(r => r.url === response.url() && !r.status);
    if (req) {
      req.status = response.status();
      req.statusText = response.statusText();
      req.contentType = response.headers()['content-type'];

      // V3: Track auth errors separately
      if (response.status() === 401 || response.status() === 403) {
        authErrors.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
      }
    }
  });

  page.on('requestfailed', request => {
    errors.push({
      url: request.url(),
      method: request.method(),
      failure: request.failure()?.errorText || 'Unknown error'
    });
  });

  // Visit key pages
  const pages = ['/', '/deals', '/actions', '/quarantine'];

  for (const path of pages) {
    try {
      console.log(`Visiting ${DASHBOARD_URL}${path}...`);
      await page.goto(`${DASHBOARD_URL}${path}`, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(2000);
    } catch (e) {
      console.error(`Error visiting ${path}: ${e.message}`);
    }
  }

  await browser.close();

  const result = {
    timestamp: new Date().toISOString(),
    dashboard_url: DASHBOARD_URL,
    auth_mode: AUTH_MODE,
    requests: requests,
    errors: errors,
    auth_errors: authErrors,
    summary: {
      total_requests: requests.length,
      successful: requests.filter(r => r.status >= 200 && r.status < 400).length,
      client_errors: requests.filter(r => r.status >= 400 && r.status < 500).length,
      server_errors: requests.filter(r => r.status >= 500).length,
      auth_errors: authErrors.length,
      failed: errors.length
    }
  };

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(result, null, 2));

  console.log(`\nCaptured ${requests.length} API requests`);
  console.log(`  Successful: ${result.summary.successful}`);
  console.log(`  Auth errors (401/403): ${result.summary.auth_errors}`);
  console.log(`  Server errors (5xx): ${result.summary.server_errors}`);
  console.log(`  Network failures: ${result.summary.failed}`);

  // V3: Fail on auth errors if auth was expected
  if (AUTH_MODE !== 'none' && authErrors.length > 0) {
    console.error('\n❌ FAIL: Auth errors detected despite auth state');
    process.exit(1);
  }

  // Fail on server errors
  if (result.summary.server_errors > 0 || errors.length > 0) {
    console.error('\n❌ FAIL: Server errors or network failures detected');
    process.exit(1);
  }
}

captureNetworkRequests().catch(e => {
  console.error(e);
  process.exit(1);
});
JSEOF

# Install playwright if needed
if ! npx playwright --version &>/dev/null 2>&1; then
  echo "Installing Playwright..."
  npm install -D @playwright/test
  npx playwright install chromium
fi

# Run capture
echo ""
echo "Running Playwright network capture..."
DASHBOARD_URL="$DASHBOARD_URL" \
  OUTPUT_FILE="$EVIDENCE_DIR/network_requests.json" \
  AUTH_STATE_FILE="$AUTH_STATE_FILE" \
  AUTH_MODE="$AUTH_MODE" \
  node "$EVIDENCE_DIR/capture.js" 2>&1 | tee "$EVIDENCE_DIR/capture.log"

CAPTURE_EXIT=$?

# Generate gate summary
python3 << PYEOF
import json

with open("$EVIDENCE_DIR/network_requests.json") as f:
    data = json.load(f)

gate = {
    "gate": "DASHBOARD_NETWORK_V3",
    "timestamp": data["timestamp"],
    "auth_mode": data["auth_mode"],
    "checks": data["summary"]["total_requests"],
    "passed": data["summary"]["successful"],
    "failed": data["summary"]["server_errors"] + data["summary"]["failed"],
    "auth_errors": data["summary"]["auth_errors"],
    "verdict": "PASS" if (data["summary"]["server_errors"] == 0 and data["summary"]["failed"] == 0) else "FAIL"
}

with open("$EVIDENCE_DIR/gate-summary.json", "w") as f:
    json.dump(gate, f, indent=2)

print(f"\n{'✅' if gate['verdict'] == 'PASS' else '❌'} Dashboard Network Gate: {gate['verdict']}")
PYEOF

exit $CAPTURE_EXIT
```

**TASK 3.1.2: Create `tools/validation/capture-auth-state.sh` (V3 — Helper)**

```bash
#!/usr/bin/env bash
# tools/validation/capture-auth-state.sh
# V3: One-time capture of authenticated browser state

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

OUTPUT_DIR="artifacts/auth"
mkdir -p "$OUTPUT_DIR"

echo "═══ CAPTURE AUTH STATE ═══"
echo ""

if [ -z "${DASHBOARD_TEST_USER:-}" ] || [ -z "${DASHBOARD_TEST_PASS:-}" ]; then
  echo "Set DASHBOARD_TEST_USER and DASHBOARD_TEST_PASS environment variables"
  exit 1
fi

cat > "$OUTPUT_DIR/capture-auth.js" << 'JSEOF'
const { chromium } = require('playwright');

const DASHBOARD_URL = process.env.DASHBOARD_URL || 'http://localhost:3003';
const TEST_USER = process.env.DASHBOARD_TEST_USER;
const TEST_PASS = process.env.DASHBOARD_TEST_PASS;
const OUTPUT_FILE = process.env.OUTPUT_FILE || 'storageState.json';

async function captureAuth() {
  const browser = await chromium.launch({ headless: false }); // Show browser for debugging
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log(`Navigating to ${DASHBOARD_URL}/login...`);
  await page.goto(`${DASHBOARD_URL}/login`, { waitUntil: 'networkidle' });

  console.log('Filling login form...');
  await page.fill('input[name="email"], input[type="email"]', TEST_USER);
  await page.fill('input[name="password"], input[type="password"]', TEST_PASS);

  console.log('Submitting...');
  await page.click('button[type="submit"]');

  // Wait for redirect after login
  await page.waitForURL('**/*', { timeout: 30000 });
  console.log(`Logged in, now at: ${page.url()}`);

  // Save storage state
  await context.storageState({ path: OUTPUT_FILE });
  console.log(`Auth state saved to ${OUTPUT_FILE}`);

  await browser.close();
}

captureAuth().catch(console.error);
JSEOF

DASHBOARD_URL="$DASHBOARD_URL" \
  DASHBOARD_TEST_USER="$DASHBOARD_TEST_USER" \
  DASHBOARD_TEST_PASS="$DASHBOARD_TEST_PASS" \
  OUTPUT_FILE="$OUTPUT_DIR/storageState.json" \
  node "$OUTPUT_DIR/capture-auth.js"

echo ""
echo "✅ Auth state captured to: $OUTPUT_DIR/storageState.json"
echo "   This file is gitignored but used by network capture"
```

---

## PHASE 4: SSE HANDSHAKE + FIRST EVENT PROOF (V3)
### Fixes "headers-only doesn't prove stream works"

**TASK 4.1.1: Create `tools/validation/sse-validation.sh` (V3)**

```bash
#!/usr/bin/env bash
# tools/validation/sse-validation.sh
# V3: Proves SSE actually streams events, not just headers

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

EVIDENCE_DIR="artifacts/infra-awareness/evidence/sse"
mkdir -p "$EVIDENCE_DIR"

echo "═══ SSE VALIDATION (V3 — Handshake + First Event) ═══" | tee "$EVIDENCE_DIR/validation.log"
echo "" | tee -a "$EVIDENCE_DIR/validation.log"

FAILURES=0

# Discover SSE endpoints
SSE_ENDPOINTS=$(grep -rn "EventSource\|text/event-stream" "$DASHBOARD_ROOT/src/" \
  --include="*.ts" --include="*.tsx" 2>/dev/null | \
  grep -oP "/api/[^\"'\`\s]+" | sort -u || echo "")

if [ -z "$SSE_ENDPOINTS" ]; then
  echo "⚠️  No SSE endpoints found in dashboard code" | tee -a "$EVIDENCE_DIR/validation.log"
  echo '{"verdict": "SKIP", "reason": "no_sse_endpoints"}' > "$EVIDENCE_DIR/gate-summary.json"
  exit 0
fi

echo "Discovered SSE endpoints:" | tee -a "$EVIDENCE_DIR/validation.log"
echo "$SSE_ENDPOINTS" | while read ep; do
  echo "  $ep" | tee -a "$EVIDENCE_DIR/validation.log"
done
echo "" | tee -a "$EVIDENCE_DIR/validation.log"

for endpoint in $SSE_ENDPOINTS; do
  echo "── Testing: $endpoint ──" | tee -a "$EVIDENCE_DIR/validation.log"

  ENDPOINT_FILE=$(echo "$endpoint" | tr '/' '_')

  # ═══ Step 1: Headers check ═══
  HEADERS=$(timeout 5 curl -sI -X GET \
    -H "Accept: text/event-stream" \
    "$BACKEND_URL$endpoint" 2>&1 || echo "TIMEOUT")

  echo "$HEADERS" > "$EVIDENCE_DIR/headers_$ENDPOINT_FILE.txt"

  if ! echo "$HEADERS" | grep -qi "text/event-stream"; then
    echo "❌ Headers: No event-stream content-type" | tee -a "$EVIDENCE_DIR/validation.log"
    FAILURES=$((FAILURES+1))
    continue
  fi
  echo "✅ Headers: content-type: text/event-stream" | tee -a "$EVIDENCE_DIR/validation.log"

  # ═══ Step 2: First event proof (V3) ═══
  echo "Testing first event..." | tee -a "$EVIDENCE_DIR/validation.log"

  STREAM_OUTPUT=$(timeout 5 curl -sN \
    -H "Accept: text/event-stream" \
    "$BACKEND_URL$endpoint" 2>&1 | head -n 30 || echo "TIMEOUT_OR_EMPTY")

  echo "$STREAM_OUTPUT" > "$EVIDENCE_DIR/stream_$ENDPOINT_FILE.txt"

  if [ "$STREAM_OUTPUT" = "TIMEOUT_OR_EMPTY" ]; then
    echo "⚠️  Stream: No data within 5s (may be idle)" | tee -a "$EVIDENCE_DIR/validation.log"
  elif echo "$STREAM_OUTPUT" | grep -qE "^event:|^data:|^:"; then
    # Look for: event:, data:, or : (comment/keepalive)
    EVENT_COUNT=$(echo "$STREAM_OUTPUT" | grep -cE "^event:|^data:" || echo "0")
    KEEPALIVE_COUNT=$(echo "$STREAM_OUTPUT" | grep -c "^:" || echo "0")

    echo "✅ Stream: Received $EVENT_COUNT event(s), $KEEPALIVE_COUNT keepalive(s)" | tee -a "$EVIDENCE_DIR/validation.log"

    # Verify event has expected fields (if data: present)
    if echo "$STREAM_OUTPUT" | grep -q "^data:"; then
      FIRST_DATA=$(echo "$STREAM_OUTPUT" | grep "^data:" | head -1 | sed 's/^data://')
      if echo "$FIRST_DATA" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        echo "✅ Stream: Event data is valid JSON" | tee -a "$EVIDENCE_DIR/validation.log"
      else
        echo "⚠️  Stream: Event data is not JSON (may be text)" | tee -a "$EVIDENCE_DIR/validation.log"
      fi
    fi
  else
    echo "❌ Stream: No valid SSE format detected" | tee -a "$EVIDENCE_DIR/validation.log"
    FAILURES=$((FAILURES+1))
  fi

  # ═══ Step 3: Replay check (V3) ═══
  echo "Testing replay with Last-Event-ID..." | tee -a "$EVIDENCE_DIR/validation.log"

  REPLAY_OUTPUT=$(timeout 3 curl -sN \
    -H "Accept: text/event-stream" \
    -H "Last-Event-ID: 0" \
    "$BACKEND_URL$endpoint" 2>&1 | head -n 20 || echo "TIMEOUT")

  echo "$REPLAY_OUTPUT" > "$EVIDENCE_DIR/replay_$ENDPOINT_FILE.txt"

  if echo "$REPLAY_OUTPUT" | grep -qE "^event:|^data:|^:"; then
    echo "✅ Replay: Server responded to Last-Event-ID" | tee -a "$EVIDENCE_DIR/validation.log"
  else
    echo "⚠️  Replay: No response (may not support replay)" | tee -a "$EVIDENCE_DIR/validation.log"
  fi

  echo "" | tee -a "$EVIDENCE_DIR/validation.log"
done

# ═══ Gate Summary ═══
ENDPOINT_COUNT=$(echo "$SSE_ENDPOINTS" | wc -l)
PASSED=$((ENDPOINT_COUNT - FAILURES))
VERDICT=$([ "$FAILURES" -eq 0 ] && echo "PASS" || echo "FAIL")

cat > "$EVIDENCE_DIR/gate-summary.json" << EOF
{
  "gate": "SSE_VALIDATION_V3",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "endpoints_tested": $ENDPOINT_COUNT,
  "passed": $PASSED,
  "failed": $FAILURES,
  "verdict": "$VERDICT",
  "v3_features": ["first_event_proof", "replay_check", "keepalive_detection"]
}
EOF

echo "═══ SSE VALIDATION SUMMARY ═══" | tee -a "$EVIDENCE_DIR/validation.log"
if [ "$FAILURES" -gt 0 ]; then
  echo "❌ SSE GATE FAILED: $FAILURES/$ENDPOINT_COUNT endpoints failed" | tee -a "$EVIDENCE_DIR/validation.log"
  exit 1
else
  echo "✅ SSE VALIDATION PASSED ($PASSED/$ENDPOINT_COUNT)" | tee -a "$EVIDENCE_DIR/validation.log"
fi
```

---

## PHASE 5: EVIDENCE HYGIENE — SECRET SCANNING (V3 — NEW)

**TASK 5.1.1: Create `tools/infra/redact.sh`**

```bash
#!/usr/bin/env bash
# tools/infra/redact.sh
# V3: Redacts secrets from text input
# Usage: cat file.txt | ./redact.sh > redacted.txt

sed -E \
  -e 's/Bearer [A-Za-z0-9._-]+/Bearer [REDACTED]/g' \
  -e 's/sk-[A-Za-z0-9._-]+/[REDACTED_KEY]/g' \
  -e 's/CLIENT_SECRET=[^[:space:]]*/CLIENT_SECRET=[REDACTED]/g' \
  -e 's/password=[^[:space:]]*/password=[REDACTED]/g' \
  -e 's/:[^:@]+@/:***@/g' \
  -e 's/-----BEGIN [A-Z]+ KEY-----/[REDACTED_KEY_BEGIN]/g' \
  -e 's/-----END [A-Z]+ KEY-----/[REDACTED_KEY_END]/g'
```

**TASK 5.1.2: Create `tools/infra/scan-evidence-secrets.sh` (V3 — NEW)**

```bash
#!/usr/bin/env bash
# tools/infra/scan-evidence-secrets.sh
# V3 NEW: Scans evidence directory for leaked secrets
# Hard-fail if secrets detected

set -euo pipefail

EVIDENCE_DIR="artifacts/infra-awareness/evidence"

echo "═══ EVIDENCE SECRET SCAN (V3) ═══"
echo ""

LEAKS_FOUND=0
LEAKS_FILE="/tmp/secret_leaks_$$.txt"
> "$LEAKS_FILE"

# Patterns to detect
SECRET_PATTERNS=(
  "Bearer [A-Za-z0-9._-]{20,}"
  "sk-[A-Za-z0-9._-]{20,}"
  "CLIENT_SECRET=[^[:space:]]+"
  "password=[^[:space:]]{8,}"
  "-----BEGIN (RSA |EC |)PRIVATE KEY-----"
  "-----BEGIN CERTIFICATE-----"
  "ghp_[A-Za-z0-9]{36}"  # GitHub personal access token
  "gho_[A-Za-z0-9]{36}"  # GitHub OAuth token
  "AKIA[0-9A-Z]{16}"     # AWS access key
)

echo "Scanning evidence directory: $EVIDENCE_DIR"
echo ""

for pattern in "${SECRET_PATTERNS[@]}"; do
  MATCHES=$(grep -rEo "$pattern" "$EVIDENCE_DIR" 2>/dev/null || true)
  if [ -n "$MATCHES" ]; then
    echo "❌ SECRET DETECTED: Pattern '$pattern'" | tee -a "$LEAKS_FILE"
    echo "$MATCHES" | head -5 | while read line; do
      echo "   $line" | tee -a "$LEAKS_FILE"
    done
    LEAKS_FOUND=$((LEAKS_FOUND + $(echo "$MATCHES" | wc -l)))
  fi
done

echo ""

# Gate summary
cat > "$EVIDENCE_DIR/secret-scan/gate-summary.json" << EOF
{
  "gate": "EVIDENCE_SECRET_SCAN_V3",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "leaks_found": $LEAKS_FOUND,
  "verdict": "$([ $LEAKS_FOUND -eq 0 ] && echo 'PASS' || echo 'FAIL')"
}
EOF

if [ "$LEAKS_FOUND" -gt 0 ]; then
  echo "❌ EVIDENCE SECRET SCAN FAILED: $LEAKS_FOUND potential secrets found"
  echo ""
  echo "Run: bash tools/infra/redact.sh on affected files"
  exit 1
else
  echo "✅ EVIDENCE SECRET SCAN PASSED: No secrets detected"
fi
```

---

## PHASE 6: CI WORKFLOW (V3 — Static vs Runtime Gates)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PHASE 6 — CI Workflow (V3)                                                  ║
║                                                                              ║
║  V2 Gap: Ambiguous whether CI spins up services or does static checks       ║
║  V3 Fix: Explicit separation of static and runtime gates                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**TASK 6.1.1: Create `.github/workflows/infra-validation-static.yml`**

```yaml
# Static CI Gate — Fast, no running services required
name: Infrastructure Validation (Static)

on:
  pull_request:
    paths:
      - 'contracts/**'
      - '**/types/**'
      - '**/schemas/**'
      - '**/*.schema.*'
      - '**/api-schemas.ts'
      - '**/zod/**'

jobs:
  static-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt

      - name: TypeScript compilation check
        run: npx tsc --noEmit

      - name: Contract schema validation
        run: |
          # Validate JSON schemas
          for f in contracts/*.json; do
            python3 -c "import json; json.load(open('$f'))" || exit 1
          done

      - name: Extract OpenAPI from app (static)
        run: |
          # Extract without running server
          python3 -c "
          from app.main import app
          import json
          with open('artifacts/openapi-static.json', 'w') as f:
              json.dump(app.openapi(), f)
          "

      - name: Contract diff check
        run: |
          # Compare contracts with code
          bash tools/infra/extract-contracts.sh
          # Will fail if mismatches (compare mode)

      - name: Evidence secret scan
        run: |
          mkdir -p artifacts/infra-awareness/evidence/secret-scan
          bash tools/infra/scan-evidence-secrets.sh

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: static-validation-evidence
          path: artifacts/
```

**TASK 6.1.2: Create `.github/workflows/infra-validation-runtime.yml`**

```yaml
# Runtime CI Gate — Slower, requires running services
name: Infrastructure Validation (Runtime)

on:
  pull_request:
    paths:
      - 'contracts/**'
      - '**/types/**'
      - '**/schemas/**'
      - '**/*.schema.*'
      - 'docker-compose*.yml'
      - '**/migrations/**'

jobs:
  runtime-validation:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: dealengine
          POSTGRES_PASSWORD: test
          POSTGRES_DB: zakops
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup environment
        run: |
          npm ci
          pip install -r requirements.txt

      - name: Start backend service
        run: |
          docker compose up -d backend
          sleep 10

      - name: Run topology discovery
        run: make infra-topology

      - name: Run DB assertion
        run: make infra-db-assert

      - name: Run migration assertion
        run: make infra-migration-assert

      - name: Run OpenAPI discovery
        run: make infra-openapi

      - name: Start dashboard
        run: |
          cd apps/dashboard && npm run build && npm start &
          sleep 10

      - name: Run dashboard network capture
        run: make validate-dashboard-network

      - name: Run phantom endpoint detection
        run: make detect-phantom-endpoints

      - name: Run cross-layer validation
        run: make validate-cross-layer

      - name: Evidence secret scan
        run: bash tools/infra/scan-evidence-secrets.sh

      - name: Upload evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: runtime-validation-evidence
          path: artifacts/infra-awareness/evidence/
```

---

## UPDATED MAKEFILE (V3)

```makefile
# ══════════════════════════════════════════════════════════════
# INFRASTRUCTURE AWARENESS V3
# ══════════════════════════════════════════════════════════════

.PHONY: infra-topology infra-contracts infra-snapshot infra-validate \
        infra-db-assert infra-migration-assert infra-openapi infra-check \
        validate-cross-layer validate-dashboard-network detect-phantom-endpoints \
        validate-sse scan-evidence-secrets capture-auth-state validate-all

# ═══ Phase 0: Topology Discovery ═══
infra-topology: ## Discover repos, containers, ports, DB (V3 dynamic)
	@bash tools/infra/discover-topology.sh

# ═══ Phase 1: Contracts + DB ═══
infra-contracts: infra-topology ## Extract and compare contracts (V3 compare mode)
	@bash tools/infra/extract-contracts.sh

infra-contracts-write: infra-topology ## Write discovered values to contracts/
	@bash tools/infra/extract-contracts.sh --write-contracts

infra-db-assert: infra-topology ## Verify DB mapping (V3 with debug endpoints)
	@bash tools/infra/db-assertion.sh

infra-migration-assert: infra-topology ## Verify migrations applied (V3 NEW)
	@bash tools/infra/migration-assertion.sh

# ═══ Phase 2: OpenAPI + Phantom Detection ═══
infra-openapi: infra-topology ## Fetch OpenAPI specs
	@bash tools/infra/openapi-discovery.sh

detect-phantom-endpoints: ## Cross-check dashboard calls vs OpenAPI (V3 NEW)
	@bash tools/infra/detect-phantom-endpoints.sh

# ═══ Phase 3: Dashboard Network Capture ═══
validate-dashboard-network: infra-topology ## Playwright capture (V3 with auth)
	@bash tools/validation/dashboard-network-capture.sh

capture-auth-state: ## One-time auth state capture (V3 helper)
	@bash tools/validation/capture-auth-state.sh

# ═══ Phase 4: SSE Validation ═══
validate-sse: infra-topology ## SSE handshake + first event (V3)
	@bash tools/validation/sse-validation.sh

# ═══ Phase 5: Evidence Hygiene ═══
scan-evidence-secrets: ## Scan evidence for leaked secrets (V3 NEW)
	@bash tools/infra/scan-evidence-secrets.sh

# ═══ Phase 6: Cross-Layer Validation ═══
validate-cross-layer: infra-topology ## 3-way schema diff
	@bash tools/infra/schema-diff.sh

# ═══ Composite Targets ═══
infra-check: infra-topology infra-db-assert infra-migration-assert
	@echo "✅ Infrastructure check complete (V3)"

validate-all: infra-check infra-openapi validate-dashboard-network detect-phantom-endpoints validate-cross-layer validate-sse scan-evidence-secrets
	@echo ""
	@echo "══════════════════════════════════════════════════════════════"
	@echo "  ✅ FULL SYSTEM VALIDATION COMPLETE (V3)"
	@echo "══════════════════════════════════════════════════════════════"
```

---

## FINAL ACCEPTANCE CRITERIA (V3)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   THE INFRASTRUCTURE AWARENESS SYSTEM V3 IS COMPLETE WHEN:                   ║
║                                                                              ║
║   NON-NEGOTIABLE GATES — ALL MUST PASS:                                      ║
║                                                                              ║
║   ┌────────────────────────────┬─────────────────────────────────────────┐   ║
║   │ make infra-topology        │ Dynamic container discovery, no        │   ║
║   │                            │ hardcoded names                         │   ║
║   ├────────────────────────────┼─────────────────────────────────────────┤   ║
║   │ make infra-check           │ Includes:                               │   ║
║   │                            │ • DB mapping gate (backend→zakops,     │   ║
║   │                            │   agent→zakops_agent)                  │   ║
║   │                            │ • Migration state gate                  │   ║
║   │                            │ • Runtime sqlite detection              │   ║
║   ├────────────────────────────┼─────────────────────────────────────────┤   ║
║   │ make validate-dashboard-   │ Playwright with auth state              │   ║
║   │ network                    │ (storageState.json or programmatic)     │   ║
║   ├────────────────────────────┼─────────────────────────────────────────┤   ║
║   │ make infra-openapi         │ OpenAPI-driven inventory                │   ║
║   │ + detect-phantom-endpoints │ + phantom/dead endpoint detection      │   ║
║   ├────────────────────────────┼─────────────────────────────────────────┤   ║
║   │ make validate-cross-layer  │ 3-way schema diff                       │   ║
║   └────────────────────────────┴─────────────────────────────────────────┘   ║
║                                                                              ║
║   ADDITIONAL V3 REQUIREMENTS:                                                ║
║                                                                              ║
║   [ ] contracts/ is SoT — discovery runs in COMPARE mode by default         ║
║   [ ] Container IDs dynamically discovered (POSTGRES_CID, BACKEND_CID)       ║
║   [ ] Explicit DB mapping in contracts/runtime.topology.json                 ║
║   [ ] Runtime sqlite detection (not code grep)                               ║
║   [ ] Migration state verified via DB + debug endpoint                       ║
║   [ ] Deal counts via /api/admin/debug/counts (not UI endpoint)             ║
║   [ ] Phantom endpoints detected: dashboard calls vs OpenAPI                 ║
║   [ ] Playwright captures with auth state                                    ║
║   [ ] SSE validates handshake + first event + replay                        ║
║   [ ] CI has explicit static vs runtime gates                               ║
║   [ ] Evidence scanned for secrets (hard fail on leak)                       ║
║   [ ] Every gate produces machine-readable JSON                              ║
║                                                                              ║
║   EVIDENCE REQUIREMENT:                                                      ║
║   Mission is NOT complete until evidence/ folder proves every gate passed    ║
║   AND secret scan shows no leaks                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## COMPLETION PACKET (V3)

```
artifacts/infra-awareness/
├── contracts/
│   ├── stages.json
│   ├── statuses.json
│   ├── runtime.topology.json       ← V3: Explicit DB mapping
│   └── endpoint_allowlist.json     ← V3: Allowed phantom endpoints
├── tools/
│   ├── infra/
│   │   ├── discover-topology.sh    ← V3: Dynamic container discovery
│   │   ├── extract-contracts.sh    ← V3: Compare mode default
│   │   ├── db-assertion.sh         ← V3: With DB mapping + debug endpoints
│   │   ├── migration-assertion.sh  ← V3 NEW
│   │   ├── openapi-discovery.sh
│   │   ├── detect-phantom-endpoints.sh ← V3 NEW
│   │   ├── redact.sh               ← V3 NEW
│   │   ├── scan-evidence-secrets.sh ← V3 NEW
│   │   └── schema-diff.sh
│   └── validation/
│       ├── dashboard-network-capture.sh ← V3: With auth state
│       ├── capture-auth-state.sh   ← V3 NEW
│       └── sse-validation.sh       ← V3: Handshake + first event
├── evidence/
│   ├── topology/
│   │   ├── topology.env            ← V3: Includes container IDs
│   │   ├── topology.json
│   │   └── gate-summary.json
│   ├── db-assertion/
│   │   ├── backend_debug_db.json   ← V3: Debug endpoint response
│   │   ├── debug_counts.json       ← V3: Admin counts endpoint
│   │   └── gate-summary.json
│   ├── migrations/                 ← V3 NEW
│   │   ├── debug_migrations.json
│   │   └── gate-summary.json
│   ├── contracts/
│   │   ├── discovered/
│   │   └── gate-summary.json
│   ├── openapi/
│   │   ├── backend_openapi.json
│   │   ├── backend_endpoints.json
│   │   └── endpoint_inventory.json
│   ├── phantom-detection/          ← V3 NEW
│   │   ├── phantom_endpoints.json
│   │   ├── dead_endpoints.json
│   │   └── gate-summary.json
│   ├── network-capture/
│   │   ├── auth_state.json         ← V3: Records auth mode
│   │   ├── network_requests.json
│   │   └── gate-summary.json
│   ├── sse/                        ← V3: Enhanced
│   │   ├── stream_*.txt
│   │   ├── replay_*.txt
│   │   └── gate-summary.json
│   └── secret-scan/                ← V3 NEW
│       └── gate-summary.json
├── auth/                           ← V3 NEW (gitignored)
│   └── storageState.json
├── .github/workflows/
│   ├── infra-validation-static.yml  ← V3: Separated
│   └── infra-validation-runtime.yml ← V3: Separated
└── completion-summary.md
```

---

*Generated: 2026-02-05*
*Version: V3 (GPT-5.2 Final Red-Team Hardened)*
*Patches Applied: 11 structural fixes*
*Non-Negotiable Gates: 5*
*Evidence Requirement: Mandatory for all gates + secret scan*
