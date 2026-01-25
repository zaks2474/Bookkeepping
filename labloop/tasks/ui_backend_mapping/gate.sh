#!/bin/bash
# UI-Backend Mapping Gate Script
# Validates that all required deliverables exist and are properly structured

set -e

DOCS_DIR="/home/zaks/bookkeeping/docs/ui-backend-mapping"
ARTIFACTS_DIR="$DOCS_DIR/gate_artifacts"

echo "=== UI-Backend Mapping Gate ==="
echo "Docs directory: $DOCS_DIR"
echo ""

# Track failures
FAILURES=0

# Helper function
check_file() {
    local file="$1"
    local desc="$2"
    if [[ -f "$file" ]]; then
        echo "✓ $desc"
        return 0
    else
        echo "✗ $desc - MISSING: $file"
        return 1
    fi
}

check_section() {
    local file="$1"
    local section="$2"
    if grep -qi "$section" "$file" 2>/dev/null; then
        echo "  ✓ Section '$section' found"
        return 0
    else
        echo "  ✗ Section '$section' NOT found"
        return 1
    fi
}

# 1. Check documentation files exist
echo "--- Documentation Files ---"

if ! check_file "$DOCS_DIR/UI_INVENTORY.md" "UI Inventory"; then
    ((FAILURES++))
else
    # Check required sections
    check_section "$DOCS_DIR/UI_INVENTORY.md" "Routes" || ((FAILURES++))
    check_section "$DOCS_DIR/UI_INVENTORY.md" "Components" || ((FAILURES++))
    check_section "$DOCS_DIR/UI_INVENTORY.md" "Actions" || ((FAILURES++))
fi

if ! check_file "$DOCS_DIR/UI_BACKEND_MAPPING.md" "Backend Mapping (MD)"; then
    ((FAILURES++))
fi

if ! check_file "$DOCS_DIR/UI_BACKEND_MAPPING.json" "Backend Mapping (JSON)"; then
    ((FAILURES++))
else
    # Validate JSON
    echo "  Validating JSON..."
    if python3 -c "import json; data=json.load(open('$DOCS_DIR/UI_BACKEND_MAPPING.json')); assert 'version' in data; assert 'mappings' in data" 2>/dev/null; then
        echo "  ✓ JSON is valid with required fields"
    else
        echo "  ✗ JSON validation failed (missing version or mappings)"
        ((FAILURES++))
    fi
fi

if ! check_file "$DOCS_DIR/GAPS_AND_FIX_PLAN.md" "Gaps and Fix Plan"; then
    ((FAILURES++))
else
    check_section "$DOCS_DIR/GAPS_AND_FIX_PLAN.md" "Gap Classification\|Priority" || ((FAILURES++))
fi

if ! check_file "$DOCS_DIR/QA_HANDOFF.md" "QA Handoff"; then
    ((FAILURES++))
else
    check_section "$DOCS_DIR/QA_HANDOFF.md" "Validation\|Prerequisites\|Run" || ((FAILURES++))
fi

if ! check_file "$DOCS_DIR/BUILDER_REPORT.md" "Builder Report"; then
    ((FAILURES++))
else
    check_section "$DOCS_DIR/BUILDER_REPORT.md" "Summary\|Changed Files" || ((FAILURES++))
fi

echo ""
echo "--- Artifacts Directory ---"

# Create artifacts dir if needed
mkdir -p "$ARTIFACTS_DIR"

echo ""
echo "--- Backend Service Probes ---"

# Run contract probes with correct endpoints
PROBE_RESULTS="$ARTIFACTS_DIR/contract_probe_results.json"
echo '{"probes": [' > "$PROBE_RESULTS"

# Deal API (8090) - uses /health
DEAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8090/health 2>/dev/null || echo "000")
echo "{\"service\": \"deal_api\", \"port\": 8090, \"endpoint\": \"/health\", \"status\": \"$DEAL_STATUS\"}," >> "$PROBE_RESULTS"
if [[ "$DEAL_STATUS" == "200" ]]; then
    echo "✓ Deal API (8090): UP"
else
    echo "✗ Deal API (8090): DOWN (status: $DEAL_STATUS)"
    ((FAILURES++))
fi

# RAG API (8052) - uses /rag/stats
RAG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8052/rag/stats 2>/dev/null || echo "000")
echo "{\"service\": \"rag_api\", \"port\": 8052, \"endpoint\": \"/rag/stats\", \"status\": \"$RAG_STATUS\"}," >> "$PROBE_RESULTS"
if [[ "$RAG_STATUS" == "200" ]]; then
    echo "✓ RAG API (8052): UP"
else
    echo "✗ RAG API (8052): DOWN (status: $RAG_STATUS)"
    ((FAILURES++))
fi

# MCP Server (9100) - uses POST /mcp with JSON-RPC
MCP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:9100/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"ping","id":1}' 2>/dev/null || echo "000")
# MCP returns 200 even for method errors, so check if port responds
if [[ "$MCP_STATUS" == "000" ]]; then
    MCP_STATUS="DOWN"
fi
echo "{\"service\": \"mcp_server\", \"port\": 9100, \"endpoint\": \"/mcp\", \"status\": \"$MCP_STATUS\"}," >> "$PROBE_RESULTS"
if [[ "$MCP_STATUS" == "200" ]]; then
    echo "✓ MCP Server (9100): UP"
else
    echo "⚠ MCP Server (9100): status $MCP_STATUS (non-critical)"
fi

# Orchestration API (9200) - uses /health
ORCH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9200/health 2>/dev/null || echo "000")
echo "{\"service\": \"orchestration_api\", \"port\": 9200, \"endpoint\": \"/health\", \"status\": \"$ORCH_STATUS\"}" >> "$PROBE_RESULTS"
if [[ "$ORCH_STATUS" == "200" ]]; then
    echo "✓ Orchestration API (9200): UP"
else
    echo "⚠ Orchestration API (9200): status $ORCH_STATUS (non-critical)"
fi

echo '],"timestamp":"'$(date -Iseconds)'"}' >> "$PROBE_RESULTS"

echo ""
echo "--- Contract Probe Results ---"
if [[ -f "$PROBE_RESULTS" ]]; then
    echo "✓ Contract probe results saved"
    if python3 -c "import json; json.load(open('$PROBE_RESULTS'))" 2>/dev/null; then
        echo "  ✓ Valid JSON"
    else
        echo "  ✗ Invalid JSON"
        ((FAILURES++))
    fi
else
    echo "✗ Contract probe results missing"
    ((FAILURES++))
fi

echo ""
echo "=== Gate Summary ==="

if [[ $FAILURES -eq 0 ]]; then
    echo "✓ All checks passed"
    exit 0
else
    echo "✗ $FAILURES check(s) failed"
    exit 1
fi
