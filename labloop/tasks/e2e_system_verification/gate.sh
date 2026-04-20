#!/bin/bash
# E2E System Verification Gate Script
# Mission ID: E2E-VERIFY-001

# Don't use set -e - we want to collect all gate results

TASK_DIR="/home/zaks/bookkeeping/labloop/tasks/e2e_system_verification"
ARTIFACTS_DIR="$TASK_DIR/artifacts"
REPORT_FILE="$ARTIFACTS_DIR/gate_report_$(date +%Y%m%d_%H%M%S).json"

mkdir -p "$ARTIFACTS_DIR"

GATES_PASSED=0
GATES_FAILED=0
ISSUES=()

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║         E2E SYSTEM VERIFICATION GATE - E2E-VERIFY-001                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# GATE 0: PRE-FLIGHT
# ============================================================================
echo "=== GATE 0: PRE-FLIGHT ==="
GATE0_PASS=true

# Check services
for svc in "3003:Dashboard" "8091:Backend" "8095:Agent" "8052:RAG"; do
    PORT=$(echo "$svc" | cut -d: -f1)
    NAME=$(echo "$svc" | cut -d: -f2)

    if curl -s --max-time 3 -o /dev/null -w "%{http_code}" "http://localhost:$PORT" 2>/dev/null | grep -qE "^(200|307|301|302)$" || \
       curl -s --max-time 3 -o /dev/null -w "%{http_code}" "http://localhost:$PORT/health" 2>/dev/null | grep -qE "^(200|307|301|302)$"; then
        echo "  ✅ $NAME ($PORT): UP"
    else
        echo "  ❌ $NAME ($PORT): DOWN"
        GATE0_PASS=false
        ISSUES+=("$NAME service not responding on port $PORT")
    fi
done

# Check no ghost on 8090
if lsof -i :8090 >/dev/null 2>&1 || ss -tlnp 2>/dev/null | grep -q ":8090 "; then
    echo "  ❌ Port 8090: OCCUPIED (ghost service!)"
    GATE0_PASS=false
    ISSUES+=("Port 8090 is occupied - legacy service running")
else
    echo "  ✅ Port 8090: FREE"
fi

# Check no ghost files
if [ -f "/home/zaks/DataRoom/.deal-registry/deal_registry.json" ]; then
    echo "  ❌ Ghost file: deal_registry.json exists"
    GATE0_PASS=false
    ISSUES+=("Legacy deal_registry.json still exists")
else
    echo "  ✅ No ghost files"
fi

if [ "$GATE0_PASS" = true ]; then
    echo "✅ GATE 0 PASSED"
    ((GATES_PASSED++))
else
    echo "❌ GATE 0 FAILED"
    ((GATES_FAILED++))
fi
echo ""

# ============================================================================
# GATE 1: ENVIRONMENT CONFIGURATION
# ============================================================================
echo "=== GATE 1: ENVIRONMENT CONFIGURATION ==="
GATE1_PASS=true

DASHBOARD_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i dashboard | head -1)

if [ -z "$DASHBOARD_CONTAINER" ]; then
    echo "  ❌ Dashboard container not found"
    GATE1_PASS=false
    ISSUES+=("Dashboard container not running")
else
    DASH_API_URL=$(docker exec "$DASHBOARD_CONTAINER" printenv NEXT_PUBLIC_API_URL 2>/dev/null || echo "NOT_SET")
    DASH_AGENT_URL=$(docker exec "$DASHBOARD_CONTAINER" printenv NEXT_PUBLIC_AGENT_API_URL 2>/dev/null || echo "NOT_SET")

    if [ "$DASH_API_URL" = "http://localhost:8091" ]; then
        echo "  ✅ NEXT_PUBLIC_API_URL: $DASH_API_URL"
    else
        echo "  ❌ NEXT_PUBLIC_API_URL: $DASH_API_URL (expected http://localhost:8091)"
        GATE1_PASS=false
        ISSUES+=("Dashboard NEXT_PUBLIC_API_URL misconfigured: $DASH_API_URL")
    fi

    if [ "$DASH_AGENT_URL" = "http://localhost:8095" ]; then
        echo "  ✅ NEXT_PUBLIC_AGENT_API_URL: $DASH_AGENT_URL"
    else
        echo "  ❌ NEXT_PUBLIC_AGENT_API_URL: $DASH_AGENT_URL (expected http://localhost:8095)"
        GATE1_PASS=false
        ISSUES+=("Dashboard NEXT_PUBLIC_AGENT_API_URL misconfigured: $DASH_AGENT_URL")
    fi
fi

if [ "$GATE1_PASS" = true ]; then
    echo "✅ GATE 1 PASSED"
    ((GATES_PASSED++))
else
    echo "❌ GATE 1 FAILED"
    ((GATES_FAILED++))
fi
echo ""

# ============================================================================
# GATE 2: SERVICE CONNECTIVITY
# ============================================================================
echo "=== GATE 2: SERVICE CONNECTIVITY ==="
GATE2_PASS=true

# [A] Dashboard → Backend
BACKEND_RESP=$(curl -s --max-time 5 http://localhost:8091/api/deals 2>/dev/null)
if [ -n "$BACKEND_RESP" ] && echo "$BACKEND_RESP" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    echo "  ✅ [A] Dashboard → Backend (8091): OK"
else
    echo "  ❌ [A] Dashboard → Backend (8091): FAILED"
    GATE2_PASS=false
    ISSUES+=("Backend /api/deals not responding correctly")
fi

# [B] Dashboard → Agent
AGENT_HEALTH=$(curl -s --max-time 5 http://localhost:8095/health 2>/dev/null)
if echo "$AGENT_HEALTH" | grep -q "healthy"; then
    echo "  ✅ [B] Dashboard → Agent API (8095): OK"
else
    echo "  ❌ [B] Dashboard → Agent API (8095): FAILED"
    GATE2_PASS=false
    ISSUES+=("Agent API health check failed")
fi

# [C] Backend → PostgreSQL
if docker exec zakops-postgres-1 psql -U zakops -d zakops -c "SELECT 1" >/dev/null 2>&1; then
    echo "  ✅ [C] Backend → PostgreSQL (5432): OK"
else
    echo "  ❌ [C] Backend → PostgreSQL (5432): FAILED"
    GATE2_PASS=false
    ISSUES+=("PostgreSQL not accessible")
fi

# [G] RAG → rag-db
RAG_STATS=$(curl -s --max-time 5 http://localhost:8052/rag/stats 2>/dev/null)
if echo "$RAG_STATS" | grep -q "total_chunks"; then
    echo "  ✅ [G] RAG API → rag-db (5434): OK"
else
    echo "  ❌ [G] RAG API → rag-db (5434): FAILED"
    GATE2_PASS=false
    ISSUES+=("RAG API /rag/stats not responding")
fi

if [ "$GATE2_PASS" = true ]; then
    echo "✅ GATE 2 PASSED"
    ((GATES_PASSED++))
else
    echo "❌ GATE 2 FAILED"
    ((GATES_FAILED++))
fi
echo ""

# ============================================================================
# GATE 3: DATABASE SCHEMAS
# ============================================================================
echo "=== GATE 3: DATABASE SCHEMAS ==="
GATE3_PASS=true

# Check zakops.deals
if docker exec zakops-postgres-1 psql -U zakops -d zakops -c "SELECT 1 FROM zakops.deals LIMIT 1" >/dev/null 2>&1; then
    DEAL_COUNT=$(docker exec zakops-postgres-1 psql -U zakops -d zakops -t -c "SELECT COUNT(*) FROM zakops.deals" 2>/dev/null | tr -d ' ')
    echo "  ✅ zakops.deals: $DEAL_COUNT rows"
else
    echo "  ❌ zakops.deals: NOT QUERYABLE"
    GATE3_PASS=false
    ISSUES+=("zakops.deals table not queryable")
fi

# Check zakops.actions
if docker exec zakops-postgres-1 psql -U zakops -d zakops -c "SELECT 1 FROM zakops.actions LIMIT 1" >/dev/null 2>&1; then
    ACTION_COUNT=$(docker exec zakops-postgres-1 psql -U zakops -d zakops -t -c "SELECT COUNT(*) FROM zakops.actions" 2>/dev/null | tr -d ' ')
    echo "  ✅ zakops.actions: $ACTION_COUNT rows"
else
    echo "  ❌ zakops.actions: NOT QUERYABLE"
    GATE3_PASS=false
    ISSUES+=("zakops.actions table not queryable")
fi

# Check RAG table
if docker exec rag-db psql -U postgres -d crawlrag -c "SELECT 1 FROM crawledpage LIMIT 1" >/dev/null 2>&1; then
    RAG_COUNT=$(docker exec rag-db psql -U postgres -d crawlrag -t -c "SELECT COUNT(*) FROM crawledpage" 2>/dev/null | tr -d ' ')
    echo "  ✅ RAG crawledpage: $RAG_COUNT rows"
else
    echo "  ⚠️ RAG crawledpage: Empty or different schema (acceptable for virgin state)"
fi

if [ "$GATE3_PASS" = true ]; then
    echo "✅ GATE 3 PASSED"
    ((GATES_PASSED++))
else
    echo "❌ GATE 3 FAILED"
    ((GATES_FAILED++))
fi
echo ""

# ============================================================================
# GATE 4: END-TO-END FUNCTIONAL
# ============================================================================
echo "=== GATE 4: END-TO-END FUNCTIONAL ==="
GATE4_PASS=true

# Test Backend API
echo "  Testing Backend API..."
DEALS_RESP=$(curl -s --max-time 10 http://localhost:8091/api/deals 2>/dev/null)
if [ -n "$DEALS_RESP" ]; then
    echo "  ✅ Backend GET /api/deals: OK"
else
    echo "  ❌ Backend GET /api/deals: FAILED"
    GATE4_PASS=false
fi

# Test Agent API health
echo "  Testing Agent API..."
AGENT_RESP=$(curl -s --max-time 10 http://localhost:8095/health 2>/dev/null)
if echo "$AGENT_RESP" | grep -q "healthy"; then
    echo "  ✅ Agent /health: OK"
else
    echo "  ❌ Agent /health: FAILED"
    GATE4_PASS=false
fi

# Test RAG API
echo "  Testing RAG API..."
RAG_RESP=$(curl -s --max-time 10 http://localhost:8052/rag/stats 2>/dev/null)
if echo "$RAG_RESP" | grep -q "total_chunks"; then
    echo "  ✅ RAG /rag/stats: OK"
else
    echo "  ❌ RAG /rag/stats: FAILED"
    GATE4_PASS=false
fi

if [ "$GATE4_PASS" = true ]; then
    echo "✅ GATE 4 PASSED"
    ((GATES_PASSED++))
else
    echo "❌ GATE 4 FAILED"
    ((GATES_FAILED++))
fi
echo ""

# ============================================================================
# GATE 5: ISSUES CHECK
# ============================================================================
echo "=== GATE 5: ISSUES CHECK ==="

if [ ${#ISSUES[@]} -eq 0 ]; then
    echo "  ✅ No critical issues detected"
    echo "✅ GATE 5 PASSED"
    ((GATES_PASSED++))
else
    echo "  Issues detected (${#ISSUES[@]}):"
    for issue in "${ISSUES[@]}"; do
        echo "    - $issue"
    done
    echo "❌ GATE 5 FAILED"
    ((GATES_FAILED++))
fi
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════"
echo "                    FINAL GATE SUMMARY"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Gates Passed: $GATES_PASSED / 5"
echo "Gates Failed: $GATES_FAILED / 5"
echo ""

# Generate JSON report
cat > "$REPORT_FILE" << EOF
{
    "mission_id": "E2E-VERIFY-001",
    "timestamp": "$(date -Iseconds)",
    "gates_passed": $GATES_PASSED,
    "gates_failed": $GATES_FAILED,
    "gate_results": {
        "gate0_preflight": $([ "$GATE0_PASS" = true ] && echo "true" || echo "false"),
        "gate1_environment": $([ "$GATE1_PASS" = true ] && echo "true" || echo "false"),
        "gate2_connectivity": $([ "$GATE2_PASS" = true ] && echo "true" || echo "false"),
        "gate3_database": $([ "$GATE3_PASS" = true ] && echo "true" || echo "false"),
        "gate4_e2e": $([ "$GATE4_PASS" = true ] && echo "true" || echo "false")
    },
    "issues": $(printf '%s\n' "${ISSUES[@]}" | jq -R . | jq -s . 2>/dev/null || echo "[]"),
    "verdict": "$([ $GATES_FAILED -eq 0 ] && echo "PASS" || echo "FAIL")"
}
EOF

echo "Report saved: $REPORT_FILE"
echo ""

if [ $GATES_FAILED -eq 0 ]; then
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                       ║"
    echo "║   ██████╗  █████╗ ███████╗███████╗███████╗██████╗                    ║"
    echo "║   ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗                   ║"
    echo "║   ██████╔╝███████║███████╗███████╗█████╗  ██║  ██║                   ║"
    echo "║   ██╔═══╝ ██╔══██║╚════██║╚════██║██╔══╝  ██║  ██║                   ║"
    echo "║   ██║     ██║  ██║███████║███████║███████╗██████╔╝                   ║"
    echo "║   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═════╝                    ║"
    echo "║                                                                       ║"
    echo "║   ALL GATES PASSED - SYSTEM VERIFIED                                  ║"
    echo "║                                                                       ║"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                       ║"
    echo "║   ███████╗ █████╗ ██╗██╗     ███████╗██████╗                         ║"
    echo "║   ██╔════╝██╔══██╗██║██║     ██╔════╝██╔══██╗                        ║"
    echo "║   █████╗  ███████║██║██║     █████╗  ██║  ██║                        ║"
    echo "║   ██╔══╝  ██╔══██║██║██║     ██╔══╝  ██║  ██║                        ║"
    echo "║   ██║     ██║  ██║██║███████╗███████╗██████╔╝                        ║"
    echo "║   ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝                         ║"
    echo "║                                                                       ║"
    echo "║   SOME GATES FAILED - REVIEW ISSUES                                   ║"
    echo "║                                                                       ║"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    exit 1
fi
