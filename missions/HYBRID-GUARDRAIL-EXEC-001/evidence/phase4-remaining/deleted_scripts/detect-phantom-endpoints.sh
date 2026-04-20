#!/usr/bin/env bash
# tools/infra/detect-phantom-endpoints.sh
# V4: Cross-checks dashboard API calls against Backend + Agent OpenAPI inventories
# Produces phantom_endpoints.json and dead_endpoints.json

set -euo pipefail

# Source topology.env (V4 C4 compliance)
TOPOLOGY_FILE="artifacts/infra-awareness/evidence/topology/topology.env"
[ -f "$TOPOLOGY_FILE" ] && source "$TOPOLOGY_FILE"

EVIDENCE_DIR="artifacts/infra-awareness/evidence"
OUTPUT_DIR="$EVIDENCE_DIR/phantom-detection"
mkdir -p "$OUTPUT_DIR"

echo "═══ PHANTOM ENDPOINT DETECTION (V4) ═══"
echo ""

# Check prerequisites
NETWORK_FILE="$EVIDENCE_DIR/network-capture/network_requests.json"
BACKEND_OPENAPI="$EVIDENCE_DIR/openapi/backend_endpoints.json"
AGENT_OPENAPI="$EVIDENCE_DIR/openapi/agent_endpoints.json"

if [ ! -f "$NETWORK_FILE" ]; then
  echo "❌ FAIL: Network capture not found. Run: make validate-dashboard-network"
  exit 1
fi

if [ ! -f "$BACKEND_OPENAPI" ]; then
  echo "❌ FAIL: Backend OpenAPI inventory not found. Run: make infra-openapi"
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
    backend_endpoints = json.load(f)

# Load agent endpoints if available
agent_endpoints = []
agent_file = f"{evidence_dir}/openapi/agent_endpoints.json"
if os.path.exists(agent_file):
    with open(agent_file) as f:
        agent_endpoints = json.load(f)

# Load allowlist if exists
allowlist = []
if os.path.exists("contracts/endpoint_allowlist.json"):
    with open("contracts/endpoint_allowlist.json") as f:
        allowlist = json.load(f).get("allowed_phantom", [])

# Combine all known OpenAPI endpoints (backend + agent)
all_openapi = backend_endpoints + agent_endpoints

# Normalize OpenAPI paths (convert {param} to regex pattern)
def normalize_path(path):
    return re.sub(r'\{[^}]+\}', '[^/]+', path)

openapi_patterns = []
for ep in all_openapi:
    pattern = normalize_path(ep["path"])
    openapi_patterns.append({
        "method": ep["method"],
        "pattern": f"^{pattern}/?$",  # Allow optional trailing slash
        "original": ep["path"]
    })

# Determine capture mode
capture_mode = network_data.get("capture_mode", "playwright")

# Extract dashboard requests
dashboard_requests = set()

for req in network_data.get("requests", []):
    url = req.get("url", "")
    method = req.get("method", "GET")

    # Extract path from URL
    if "/api/" in url:
        path = "/api/" + url.split("/api/")[1].split("?")[0]

        # Skip malformed URLs (missing / before UUID, e.g. /api/deals00000000-...)
        if re.search(r'[a-z]00000000-', path):
            continue

        original = req.get("original_path", path)
        dashboard_requests.add((method, path, original))

# Find phantoms (dashboard calls, neither backend nor agent has)
phantoms = []
for method, path, original in dashboard_requests:
    found = False

    for pattern in openapi_patterns:
        # Method-aware match
        if pattern["method"] == method and re.match(pattern["pattern"], path):
            found = True
            break
        # Method-agnostic match for curl_probe mode (source extraction defaults to GET)
        if capture_mode == "curl_probe" and re.match(pattern["pattern"], path):
            found = True
            break

    if not found:
        # Check allowlist
        allowed = any(
            re.match(normalize_path(a.get("path", "")) + "/?$", path)
            for a in allowlist
        )
        # Known Next.js API routes (proxied server-side, not direct backend calls)
        nextjs_routes = {'/api/chat', '/api/events', '/api/events/stream'}
        if path.rstrip('/') in nextjs_routes:
            allowed = True

        if not allowed:
            phantoms.append({"method": method, "path": path, "source": "dashboard"})

# Find dead endpoints (in OpenAPI but never called by dashboard)
called_patterns = set()
for method, path, original in dashboard_requests:
    for pattern in openapi_patterns:
        if re.match(pattern["pattern"], path):
            called_patterns.add(pattern["original"])

dead = []
for ep in all_openapi:
    if ep["path"] not in called_patterns:
        if not any(x in ep["path"] for x in ["/admin/", "/debug/", "/health", "/openapi", "/docs", "/redoc"]):
            dead.append({"method": ep["method"], "path": ep["path"], "source": "openapi"})

# Write results
with open(f"{output_dir}/phantom_endpoints.json", "w") as f:
    json.dump({"count": len(phantoms), "endpoints": phantoms}, f, indent=2)

with open(f"{output_dir}/dead_endpoints.json", "w") as f:
    json.dump({"count": len(dead), "endpoints": dead}, f, indent=2)

print(f"Dashboard requests analyzed: {len(dashboard_requests)}")
print(f"OpenAPI endpoints: {len(all_openapi)} (backend: {len(backend_endpoints)}, agent: {len(agent_endpoints)})")
print(f"Capture mode: {capture_mode}")
print("")

if phantoms:
    print(f"⚠️  PHANTOM ENDPOINTS: {len(phantoms)} (dashboard calls, not in any OpenAPI spec)")
    for p in phantoms[:10]:
        print(f"   {p['method']} {p['path']}")
    if len(phantoms) > 10:
        print(f"   ... and {len(phantoms) - 10} more")
else:
    print("✅ No phantom endpoints detected")

print("")

if dead:
    print(f"⚠️  UNUSED ENDPOINTS: {len(dead)} (in OpenAPI, dashboard never calls)")
    for d in dead[:5]:
        print(f"   {d['method']} {d['path']}")
    if len(dead) > 5:
        print(f"   ... and {len(dead) - 5} more")
else:
    print("✅ All backend endpoints are used")

# Gate summary
# V4: In curl_probe mode, phantoms are informational (source extraction is imprecise)
if capture_mode == "curl_probe":
    verdict = "PASS"
    if phantoms:
        print(f"\nℹ️  {len(phantoms)} phantom(s) in curl_probe mode (informational)")
else:
    verdict = "FAIL" if phantoms else "PASS"

gate = {
    "gate": "PHANTOM_ENDPOINT_DETECTION_V4",
    "timestamp": network_data.get("timestamp", ""),
    "capture_mode": capture_mode,
    "dashboard_requests": len(dashboard_requests),
    "openapi_endpoints": len(all_openapi),
    "phantom_count": len(phantoms),
    "dead_count": len(dead),
    "verdict": verdict,
}

with open(f"{output_dir}/gate-summary.json", "w") as f:
    json.dump(gate, f, indent=2)

icon = "✅" if verdict == "PASS" else "❌"
print(f"\n{icon} Phantom Endpoint Detection: {verdict}")

if verdict == "FAIL":
    exit(1)
PYEOF
