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

# Try standard OpenAPI endpoints; write directly to file to avoid shell variable size limits
OPENAPI_FOUND=false
for openapi_path in "/openapi.json" "/docs/openapi.json" "/api/openapi.json"; do
  HTTP_CODE=$(curl -sf -o "$EVIDENCE_DIR/backend_openapi.json" -w "%{http_code}" "$BACKEND_URL$openapi_path" 2>/dev/null || echo "000")
  if [ "$HTTP_CODE" = "200" ] && head -c 20 "$EVIDENCE_DIR/backend_openapi.json" 2>/dev/null | grep -q '"openapi"'; then
    OPENAPI_FOUND=true
    echo "✅ Found Backend OpenAPI at $openapi_path"
    break
  fi
done

if [ "$OPENAPI_FOUND" = false ]; then
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
# Try multiple OpenAPI paths for agent
AGENT_OPENAPI_FOUND=false
for agent_path in "/api/v1/openapi.json" "/openapi.json" "/api/openapi.json"; do
  curl -s -o "$EVIDENCE_DIR/agent_openapi.json" "$AGENT_URL$agent_path" 2>/dev/null || true
  if head -c 30 "$EVIDENCE_DIR/agent_openapi.json" 2>/dev/null | grep -q '"openapi"'; then
    AGENT_OPENAPI_FOUND=true
    echo "✅ Found Agent OpenAPI at $agent_path"
    break
  fi
done
if [ "$AGENT_OPENAPI_FOUND" = false ]; then
  echo '{"error": "NOT_FOUND"}' > "$EVIDENCE_DIR/agent_openapi.json"
fi

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
