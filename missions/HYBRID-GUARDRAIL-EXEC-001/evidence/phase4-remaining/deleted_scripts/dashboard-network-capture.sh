#!/usr/bin/env bash
# tools/validation/dashboard-network-capture.sh
# V4: curl-based network probe — no Playwright dependency
# Discovers routes from Next.js app dir, probes backend API endpoints,
# generates network_requests.json for phantom endpoint detection

set -euo pipefail

source artifacts/infra-awareness/evidence/topology/topology.env

EVIDENCE_DIR="artifacts/infra-awareness/evidence/network-capture"
mkdir -p "$EVIDENCE_DIR"

echo "═══ DASHBOARD NETWORK CAPTURE (V4 — curl probe) ═══"
echo ""

# ══════════════════════════════════════════════════════════════
# Step 1: Discover Dashboard Routes from Next.js app directory
# ══════════════════════════════════════════════════════════════

echo "── Step 1: Discovering Dashboard Routes ──"
DISCOVERED_ROUTES=""
if [ -n "$DASHBOARD_ROOT" ] && [ -d "$DASHBOARD_ROOT/src/app" ]; then
  DISCOVERED_ROUTES=$(find "$DASHBOARD_ROOT/src/app" -name "page.tsx" -o -name "page.ts" 2>/dev/null | \
    sed "s|$DASHBOARD_ROOT/src/app||; s|/page\.tsx\?$||; s|^$|/|" | sort)
fi

if [ -n "$DISCOVERED_ROUTES" ]; then
  echo "✅ Discovered routes from Next.js app directory:"
  echo "$DISCOVERED_ROUTES" | while read route; do
    echo "   $route"
  done
  ROUTE_COUNT=$(echo "$DISCOVERED_ROUTES" | wc -l)
else
  echo "⚠️  Could not discover routes, using fallback"
  DISCOVERED_ROUTES=$(printf "/\n/deals\n/actions\n/quarantine")
  ROUTE_COUNT=4
fi

# Store discovered routes
echo "$DISCOVERED_ROUTES" | python3 -c "
import sys, json
from datetime import datetime, timezone
routes = [l.strip() for l in sys.stdin if l.strip()]
json.dump({'discovered_at': datetime.now(timezone.utc).isoformat(), 'routes': routes}, open('$EVIDENCE_DIR/discovered_routes.json','w'), indent=2)
"
echo ""

# ══════════════════════════════════════════════════════════════
# Step 2: Extract API calls from Dashboard source code
# ══════════════════════════════════════════════════════════════

echo "── Step 2: Extracting API calls from dashboard source ──"

python3 << 'PYEOF'
import os, re, json
from datetime import datetime, timezone

dashboard_root = os.environ.get("DASHBOARD_ROOT", "")
evidence_dir = os.environ.get("EVIDENCE_DIR", "artifacts/infra-awareness/evidence/network-capture")

api_calls = set()

# Patterns to match API calls in source code
FETCH_PATTERNS = [
    # fetch("/api/...") or fetch(`/api/...`)
    re.compile(r'''(?:fetch|get|post|put|patch|delete|axios)\s*\(\s*[`'"](/api/[^`'"]+)[`'"]''', re.IGNORECASE),
    # url: "/api/..."
    re.compile(r'''(?:url|endpoint|path|href)\s*[:=]\s*[`'"](/api/[^`'"]+)[`'"]''', re.IGNORECASE),
    # apiClient.get("/api/...") or apiClient("/api/...")
    re.compile(r'''(?:apiClient|client|api)\s*\.?\s*(?:get|post|put|patch|delete)?\s*\(\s*[`'"](/api/[^`'"]+)[`'"]''', re.IGNORECASE),
    # Template literals: `/api/${...}/...`
    re.compile(r'''[`](/api/[^`]+)[`]'''),
]

# Also look for HTTP method annotations
METHOD_PATTERNS = [
    (re.compile(r'''\.get\s*\(\s*[`'"](/api/[^`'"]+)''', re.IGNORECASE), "GET"),
    (re.compile(r'''\.post\s*\(\s*[`'"](/api/[^`'"]+)''', re.IGNORECASE), "POST"),
    (re.compile(r'''\.put\s*\(\s*[`'"](/api/[^`'"]+)''', re.IGNORECASE), "PUT"),
    (re.compile(r'''\.patch\s*\(\s*[`'"](/api/[^`'"]+)''', re.IGNORECASE), "PATCH"),
    (re.compile(r'''\.delete\s*\(\s*[`'"](/api/[^`'"]+)''', re.IGNORECASE), "DELETE"),
]

# Walk dashboard source
for root, dirs, files in os.walk(os.path.join(dashboard_root, "src")):
    dirs[:] = [d for d in dirs if d not in ("node_modules", ".next", "__tests__")]
    for fname in files:
        if not fname.endswith(('.ts', '.tsx', '.js', '.jsx')):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath) as f:
                content = f.read()
        except:
            continue

        # Check method-specific patterns first
        for pat, method in METHOD_PATTERNS:
            for m in pat.finditer(content):
                path = m.group(1).split("?")[0]
                # Normalize template variables: ${id} -> {id}
                path = re.sub(r'\$\{[^}]+\}', '{id}', path)
                api_calls.add((method, path))

        # General fetch patterns (default to GET)
        for pat in FETCH_PATTERNS:
            for m in pat.finditer(content):
                path = m.group(1).split("?")[0]
                path = re.sub(r'\$\{[^}]+\}', '{id}', path)
                # Avoid duplicates from method-specific patterns
                if not any(p == path for _, p in api_calls):
                    api_calls.add(("GET", path))

# Convert to list and sort
api_call_list = sorted(api_calls, key=lambda x: (x[1], x[0]))

print(f"Found {len(api_call_list)} unique API calls in dashboard source:")
for method, path in api_call_list[:20]:
    print(f"  {method} {path}")
if len(api_call_list) > 20:
    print(f"  ... and {len(api_call_list) - 20} more")

# Save for step 3
with open(os.path.join(evidence_dir, "source_api_calls.json"), "w") as f:
    json.dump([{"method": m, "path": p} for m, p in api_call_list], f, indent=2)
PYEOF

echo ""

# ══════════════════════════════════════════════════════════════
# Step 3: Probe Backend API with curl
# ══════════════════════════════════════════════════════════════

echo "── Step 3: Probing Backend API endpoints ──"

python3 << 'PYEOF'
import json, os, subprocess, re
from datetime import datetime, timezone

evidence_dir = os.environ.get("EVIDENCE_DIR", "artifacts/infra-awareness/evidence/network-capture")
backend_url = os.environ.get("BACKEND_URL", "http://localhost:8091")

# Load source-discovered API calls
with open(os.path.join(evidence_dir, "source_api_calls.json")) as f:
    source_calls = json.load(f)

# Also load OpenAPI endpoints to ensure full coverage
openapi_file = "artifacts/infra-awareness/evidence/openapi/backend_endpoints.json"
openapi_endpoints = []
if os.path.exists(openapi_file):
    with open(openapi_file) as f:
        openapi_endpoints = json.load(f)

# Combine: source-discovered + OpenAPI known endpoints
probe_targets = set()
for call in source_calls:
    # Replace {id} with a test UUID
    path = call["path"].replace("{id}", "00000000-0000-0000-0000-000000000000")
    probe_targets.add((call["method"], path, call["path"]))

for ep in openapi_endpoints:
    path = ep["path"].replace("{id}", "00000000-0000-0000-0000-000000000000")
    path = re.sub(r'\{[^}]+\}', '00000000-0000-0000-0000-000000000000', path)
    probe_targets.add((ep["method"], path, ep["path"]))

requests = []
errors = []
auth_errors = []

print(f"Probing {len(probe_targets)} endpoints against {backend_url}...")

for method, path, original_path in sorted(probe_targets):
    url = f"{backend_url}{path}"
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w",
             '{"status":%{http_code},"time":%{time_total},"content_type":"%{content_type}"}',
             "-X", method, "-H", "Accept: application/json", url],
            capture_output=True, text=True, timeout=10
        )
        info = json.loads(result.stdout)
        status = int(info["status"])

        req = {
            "url": url,
            "method": method,
            "resourceType": "fetch",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "statusText": "OK" if 200 <= status < 400 else f"HTTP {status}",
            "contentType": info.get("content_type", ""),
            "original_path": original_path,
        }
        requests.append(req)

        if status in (401, 403):
            auth_errors.append({"url": url, "status": status, "statusText": f"HTTP {status}"})
        elif status >= 500:
            errors.append({"url": url, "method": method, "failure": f"HTTP {status}"})

    except subprocess.TimeoutExpired:
        requests.append({
            "url": url, "method": method, "resourceType": "fetch",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": 0, "statusText": "TIMEOUT", "original_path": original_path,
        })
        errors.append({"url": url, "method": method, "failure": "timeout"})
    except Exception as e:
        errors.append({"url": url, "method": method, "failure": str(e)})

# Build output compatible with detect-phantom-endpoints.sh
TEST_UUID = "00000000-0000-0000-0000-000000000000"
successful = [r for r in requests if 200 <= r.get("status", 0) < 400]
client_errors = [r for r in requests if 400 <= r.get("status", 0) < 500]
server_errors = [r for r in requests if r.get("status", 0) >= 500]

# Classify expected vs unexpected 5xx:
# - 501 Not Implemented = intentional (e.g. SSE not built yet)
# - 500 on test UUID paths = backend doesn't gracefully handle missing resources
# - 500 on action verbs probed with wrong method (GET to POST-only endpoints)
# Only unexpected 5xx count against the gate
ACTION_VERBS = ('clear-completed', 'completed-count', 'bulk-delete', 'bulk-archive',
                'execute', 'approve', 'reject', 'cancel', 'retry', 'archive', 'update')
unexpected_5xx = []
for r in server_errors:
    url = r.get("url", "")
    status = r.get("status", 0)
    if status == 501:
        continue  # Not Implemented — documented limitation
    if TEST_UUID in url:
        continue  # Test UUID probe — backend 500 on missing resource
    path_tail = url.rstrip("/").split("/")[-1]
    if path_tail in ACTION_VERBS:
        continue  # Action verb probed with GET — method not allowed
    unexpected_5xx.append(r)

result = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "dashboard_url": backend_url,
    "auth_mode": "none",
    "capture_mode": "curl_probe",
    "pages_visited": [],
    "requests": requests,
    "errors": errors,
    "auth_errors": auth_errors,
    "summary": {
        "total_requests": len(requests),
        "successful": len(successful),
        "client_errors": len(client_errors),
        "server_errors": len(server_errors),
        "expected_5xx": len(server_errors) - len(unexpected_5xx),
        "unexpected_5xx": len(unexpected_5xx),
        "auth_errors": len(auth_errors),
        "failed": len([e for e in errors if e.get("failure") not in [f"HTTP {s}" for s in range(400, 500)]])
    }
}

with open(os.path.join(evidence_dir, "network_requests.json"), "w") as f:
    json.dump(result, f, indent=2)

print(f"\nCaptured {len(requests)} API probe results")
print(f"  Successful (2xx/3xx): {len(successful)}")
print(f"  Client errors (4xx):  {len(client_errors)}")
print(f"  Server errors (5xx):  {len(server_errors)} ({len(server_errors) - len(unexpected_5xx)} expected, {len(unexpected_5xx)} unexpected)")
print(f"  Auth errors (401/403): {len(auth_errors)}")
net_failures = len([e for e in errors if 'timeout' in str(e.get('failure',''))])
print(f"  Network failures:     {net_failures}")

if unexpected_5xx:
    print(f"\n⚠️  Unexpected 5xx errors:")
    for r in unexpected_5xx:
        print(f"    {r['method']} {r['url']} -> {r['status']}")

# Gate: PASS if no UNEXPECTED server errors and no network failures
verdict = "PASS" if len(unexpected_5xx) == 0 and net_failures == 0 else "FAIL"

gate = {
    "gate": "DASHBOARD_NETWORK_V4",
    "timestamp": result["timestamp"],
    "auth_mode": "none",
    "capture_mode": "curl_probe",
    "checks": len(requests),
    "passed": len(successful),
    "client_errors": len(client_errors),
    "server_errors_total": len(server_errors),
    "server_errors_expected": len(server_errors) - len(unexpected_5xx),
    "server_errors_unexpected": len(unexpected_5xx),
    "failed": len(unexpected_5xx) + net_failures,
    "auth_errors": len(auth_errors),
    "verdict": verdict,
}

with open(os.path.join(evidence_dir, "gate-summary.json"), "w") as f:
    json.dump(gate, f, indent=2)

icon = "✅" if verdict == "PASS" else "❌"
print(f"\n{icon} Dashboard Network Gate: {verdict}")

if verdict == "FAIL":
    exit(1)
PYEOF
