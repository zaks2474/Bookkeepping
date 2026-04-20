# QA VERIFICATION + REMEDIATION: AGENT-BRAIN-REMEDIATION-R4
## Schema Alignment Audit | Zero Trust | Zod Prevention | Cross-Layer Validation

**Codename:** `QA-AB-R4-VERIFY-001`
**Version:** V1
**Date:** 2026-02-05
**Target:** AGENT-BRAIN-REMEDIATION-R4 (Deal Tool Data Source Routing Fix)
**Executor:** Claude Code (Opus 4.5)
**Mode:** VERIFY + REMEDIATE — verify first, fix if broken, re-verify after fix
**Stance:** ZERO TRUST — Assume every Builder claim is fabricated until independently proven
**Authority:** VETO power — any critical failure = mission NOT COMPLETE
**Special Focus:** **SCHEMA ALIGNMENT** — The Zod cascade must NEVER happen again

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   HARD RULE: NO ENDING QA SESSION WHILE TESTS ARE RED                        ║
║                                                                               ║
║   ZERO-TRUST SCHEMA VALIDATION:                                              ║
║   - Backend API response schema → DOCUMENTED                                 ║
║   - Agent ToolResult data shape → MATCHES BACKEND                            ║
║   - Dashboard TypeScript types → MATCHES BACKEND                             ║
║   - Zod schemas (if any) → MATCHES ALL THREE                                 ║
║                                                                               ║
║   IF ANY SCHEMA MISMATCH EXISTS → MISSION FAILS                              ║
║   We will NOT repeat the Zod cascade incident.                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## THE ZOD PREVENTION MANDATE

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         WHY THIS QA IS DIFFERENT                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│ The Zod cascade happened because schemas drifted between layers:               │
│                                                                                 │
│   Backend returned: { stage: "inbound", ... }                                  │
│   Dashboard expected: { stage: "Inbound", ... }  ← CASE MISMATCH              │
│   Zod validation: FAILED → Crash                                               │
│                                                                                 │
│ This QA will:                                                                   │
│   1. Extract the EXACT schema from Backend API response                        │
│   2. Extract the EXACT schema from Agent ToolResult                            │
│   3. Extract the EXACT types from Dashboard TypeScript                         │
│   4. DIFF all three — ANY mismatch = FAIL                                      │
│   5. Run TypeScript compilation — ANY error = FAIL                             │
│   6. Test Zod parsing (if exists) — ANY error = FAIL                          │
│                                                                                 │
│ THE RULE: All three layers must agree on EVERY field name, type, and value.   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## SECTION 0: SETUP & VARIABLES

```bash
# ──── Project paths ────
AGENT_ROOT="/home/zaks/zakops-agent-api/apps/agent-api"
BACKEND_ROOT="/home/zaks/zakops-agent-api/apps/backend"  # Adjust if different
DASHBOARD_ROOT="/home/zaks/zakops-agent-api/apps/dashboard"
EVALS_ROOT="/home/zaks/zakops-agent-api/evals"
BOOKKEEPING="/home/zaks/bookkeeping"
OUTPUT_ROOT="$BOOKKEEPING/qa-verifications/QA-AB-R4-VERIFY-001"

# ──── Evidence structure ────
mkdir -p "$OUTPUT_ROOT/evidence"/{
  v0-baseline,
  schema-alignment,
  tool-implementation,
  system-prompt,
  routing-verification,
  golden-traces,
  dashboard-types,
  zod-validation,
  acceptance-test,
  regression,
  final-gate,
  discrepancies,
  remediation,
  red-team
}

# Red-team evidence subdirs
mkdir -p "$OUTPUT_ROOT/evidence/red-team"/{
  rt1-canary,
  rt2-backend-proof,
  rt3-db-sot,
  rt4-openapi,
  rt5-negative-path,
  rt6-tool-semantics,
  rt7-wrapper,
  rt8-skip-risk,
  rt9-golden-prompt,
  rt10-scope-rollback
}

# ──── Service endpoints ────
AGENT_API="http://localhost:8095"
BACKEND_API="http://localhost:8091"
SERVICE_TOKEN="<your_service_token>"

# ──── Verification timestamp ────
QA_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "QA-AB-R4-VERIFY-001 started at $QA_START" > "$OUTPUT_ROOT/evidence/qa_start.txt"
```

---

## SECTION 1: V0 — BASELINE & HEALTH

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  STEP V0 — BASELINE CAPTURE                                                  ║
║  Verify services are running before any schema extraction.                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**TASK V0.1:** Agent API health
```bash
curl -sf "$AGENT_API/health" | python3 -m json.tool \
  | tee "$OUTPUT_ROOT/evidence/v0-baseline/agent_health.json"
```
→ HTTP 200 required. If not → **HARD STOP**.

**TASK V0.2:** Backend API health
```bash
curl -sf "$BACKEND_API/health" | python3 -m json.tool \
  | tee "$OUTPUT_ROOT/evidence/v0-baseline/backend_health.json"
```
→ HTTP 200 required. If not → **HARD STOP**.

**TASK V0.3:** Backend /api/deals returns data
```bash
curl -sf "$BACKEND_API/api/deals" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Type: {type(data).__name__}')
print(f'Count: {len(data) if isinstance(data, list) else \"NOT A LIST\"}')
" | tee "$OUTPUT_ROOT/evidence/v0-baseline/deals_availability.txt"
```
→ Must return a list with deals. If empty or error → **HARD STOP**.

**TASK V0.4:** Capture R4 completion summary claims
```bash
cat /home/zaks/bookkeeping/evidence/agent-brain-r4-deal-tools/R4_COMPLETION_SUMMARY.md \
  | tee "$OUTPUT_ROOT/evidence/v0-baseline/builder_claims.md"
```

```
GATE V0: Both services healthy. Backend returns deals. Builder claims captured.
```

---

## SECTION 2: SCHEMA ALIGNMENT — THE CRITICAL SECTION

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  SCHEMA ALIGNMENT — THIS IS WHERE THE ZOD CASCADE WOULD HAVE BEEN CAUGHT    ║
║                                                                               ║
║  We will extract schemas from THREE sources and DIFF them:                   ║
║    1. Backend API actual response                                            ║
║    2. Agent ToolResult data structure                                        ║
║    3. Dashboard TypeScript type definitions                                  ║
║                                                                               ║
║  ANY MISMATCH = FAIL. No exceptions. No "it's close enough."                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### SA1 — Backend API Response Schema

**TASK SA1.1:** Extract EXACT field names and types from Backend /api/deals
```bash
curl -sf "$BACKEND_API/api/deals" | python3 -c "
import json, sys

data = json.load(sys.stdin)
if not isinstance(data, list) or len(data) == 0:
    print('ERROR: No deals returned')
    sys.exit(1)

# Extract schema from first deal
deal = data[0]
print('=== BACKEND API DEAL SCHEMA ===')
print('Field inventory (from first deal):')
print()

schema = {}
for key in sorted(deal.keys()):
    value = deal[key]
    value_type = type(value).__name__
    # For strings, capture actual value for enum detection
    if isinstance(value, str):
        schema[key] = {'type': 'string', 'example': value}
        print(f'  {key}: string = {repr(value)[:60]}')
    elif isinstance(value, bool):
        schema[key] = {'type': 'boolean', 'example': value}
        print(f'  {key}: boolean = {value}')
    elif isinstance(value, int):
        schema[key] = {'type': 'integer', 'example': value}
        print(f'  {key}: integer = {value}')
    elif isinstance(value, float):
        schema[key] = {'type': 'number', 'example': value}
        print(f'  {key}: number = {value}')
    elif isinstance(value, list):
        schema[key] = {'type': 'array', 'length': len(value)}
        print(f'  {key}: array[{len(value)}]')
    elif isinstance(value, dict):
        schema[key] = {'type': 'object', 'keys': list(value.keys())}
        print(f'  {key}: object {{ {list(value.keys())[:5]} }}')
    elif value is None:
        schema[key] = {'type': 'null', 'example': None}
        print(f'  {key}: null')
    else:
        schema[key] = {'type': value_type, 'example': str(value)[:50]}
        print(f'  {key}: {value_type} = {str(value)[:50]}')

# Save schema as JSON for comparison
with open('$OUTPUT_ROOT/evidence/schema-alignment/backend_schema.json', 'w') as f:
    json.dump(schema, f, indent=2, default=str)

print()
print(f'Total fields: {len(schema)}')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/schema-alignment/sa1_1_backend_fields.txt"
```

**TASK SA1.2:** Extract ALL stage values from Backend
```bash
curl -sf "$BACKEND_API/api/deals" | python3 -c "
import json, sys
from collections import Counter

data = json.load(sys.stdin)
stages = [d.get('stage', 'MISSING') for d in data]
print('=== BACKEND STAGE VALUES (EXACT) ===')
for stage, count in Counter(stages).most_common():
    print(f'  \"{stage}\" : {count} deals')
print()
print('Stage values are CASE SENSITIVE.')
print('Dashboard and agent MUST use these exact values.')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/schema-alignment/sa1_2_backend_stages.txt"
```

**TASK SA1.3:** Save raw Backend response for reference
```bash
curl -sf "$BACKEND_API/api/deals" | python3 -m json.tool \
  > "$OUTPUT_ROOT/evidence/schema-alignment/backend_raw_response.json"
```

### SA2 — Agent ToolResult Schema

**TASK SA2.1:** Extract list_deals implementation and return shape
```bash
# Get list_deals function source
python3 -c "
import re
with open('$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py') as f:
    content = f.read()

# Find list_deals function
match = re.search(r'((?:async )?def list_deals.*?)(?=\n(?:async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    print('=== list_deals IMPLEMENTATION ===')
    print(match.group(1))
else:
    print('ERROR: list_deals NOT FOUND')
" | tee "$OUTPUT_ROOT/evidence/schema-alignment/sa2_1_list_deals_impl.txt"
```

**TASK SA2.2:** Extract ToolResult schema definition
```bash
cat "$AGENT_ROOT/app/core/langgraph/tools/schemas.py" \
  | tee "$OUTPUT_ROOT/evidence/schema-alignment/sa2_2_toolresult_schema.txt"
```

**TASK SA2.3:** LIVE TEST — Call list_deals and capture actual response structure
```bash
THREAD_SCHEMA="qa-r4-schema-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"List all my deals\",\"thread_id\":\"$THREAD_SCHEMA\"}" \
  | python3 -c "
import json, sys

response = json.load(sys.stdin)
print('=== AGENT RESPONSE STRUCTURE ===')
print(json.dumps(response, indent=2, default=str)[:3000])

# Try to find the tool result data
# This depends on response format — adapt as needed
" 2>&1 | tee "$OUTPUT_ROOT/evidence/schema-alignment/sa2_3_agent_response.txt"
```

**TASK SA2.4:** Check if agent returns same field names as backend
```bash
# This is a CRITICAL check — field names MUST match
python3 -c "
import json

# Load backend schema
with open('$OUTPUT_ROOT/evidence/schema-alignment/backend_schema.json') as f:
    backend_schema = json.load(f)

backend_fields = set(backend_schema.keys())
print('=== BACKEND DEAL FIELDS ===')
print(sorted(backend_fields))
print()

# Check agent response for field usage
# We need to verify the agent returns deals with the SAME field names
with open('$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py') as f:
    tool_code = f.read()

# Look for field transformations or renaming
transformations = []
import re
# Check for any dict key manipulation in list_deals
if 'list_deals' in tool_code:
    # Find any explicit field renaming patterns
    renames = re.findall(r'[\"\'](\w+)[\"\']\s*:\s*[\w\.]+\[[\"\'](\w+)[\"\']', tool_code)
    for new_name, old_name in renames:
        if new_name != old_name:
            transformations.append(f'  {old_name} → {new_name}')

if transformations:
    print('=== FIELD TRANSFORMATIONS DETECTED ===')
    for t in transformations:
        print(t)
    print()
    print('WARNING: Field renaming may cause schema mismatch!')
else:
    print('=== NO FIELD TRANSFORMATIONS DETECTED ===')
    print('Agent appears to pass through backend fields as-is.')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/schema-alignment/sa2_4_field_comparison.txt"
```

### SA3 — Dashboard TypeScript Types

**TASK SA3.1:** Find Dashboard Deal type definitions
```bash
# Search for Deal interface/type definitions
grep -rn "interface.*Deal\|type.*Deal\|DealSchema\|DealResponse\|DealType" \
  "$DASHBOARD_ROOT/src/" 2>/dev/null \
  | tee "$OUTPUT_ROOT/evidence/dashboard-types/sa3_1_deal_types_grep.txt"

# Get full type definition files
find "$DASHBOARD_ROOT/src" -name "*.ts" -o -name "*.tsx" 2>/dev/null \
  | xargs grep -l "interface.*Deal\|type.*Deal" 2>/dev/null \
  | head -5 \
  | while read f; do
    echo "=== $f ===" >> "$OUTPUT_ROOT/evidence/dashboard-types/sa3_1_deal_type_files.txt"
    cat "$f" >> "$OUTPUT_ROOT/evidence/dashboard-types/sa3_1_deal_type_files.txt"
    echo "" >> "$OUTPUT_ROOT/evidence/dashboard-types/sa3_1_deal_type_files.txt"
  done
```

**TASK SA3.2:** Extract Dashboard stage enum/type
```bash
grep -rn "stage.*inbound\|stage.*screening\|DealStage\|DEAL_STAGES\|dealStages" \
  "$DASHBOARD_ROOT/src/" 2>/dev/null \
  | tee "$OUTPUT_ROOT/evidence/dashboard-types/sa3_2_stage_definitions.txt"

# Look for any stage enum
grep -rn "enum.*Stage\|Stage.*=\|stages.*\[" \
  "$DASHBOARD_ROOT/src/" 2>/dev/null \
  | tee -a "$OUTPUT_ROOT/evidence/dashboard-types/sa3_2_stage_definitions.txt"
```

**TASK SA3.3:** Find Zod schemas in Dashboard (if any)
```bash
# This is the ZOD CHECK
grep -rn "z\.object\|z\.string\|z\.enum\|zodSchema\|\.parse\|\.safeParse" \
  "$DASHBOARD_ROOT/src/" 2>/dev/null \
  | tee "$OUTPUT_ROOT/evidence/zod-validation/sa3_3_zod_schemas.txt"

# If Zod exists, get the full schema files
find "$DASHBOARD_ROOT/src" -name "*.ts" -o -name "*.tsx" 2>/dev/null \
  | xargs grep -l "z\.object\|zodSchema" 2>/dev/null \
  | head -10 \
  | while read f; do
    echo "=== ZOD FILE: $f ===" >> "$OUTPUT_ROOT/evidence/zod-validation/sa3_3_zod_files.txt"
    cat "$f" >> "$OUTPUT_ROOT/evidence/zod-validation/sa3_3_zod_files.txt"
    echo "" >> "$OUTPUT_ROOT/evidence/zod-validation/sa3_3_zod_files.txt"
  done

# Count Zod usage
ZOD_COUNT=$(grep -rn "z\." "$DASHBOARD_ROOT/src/" 2>/dev/null | wc -l)
echo "Zod usage count: $ZOD_COUNT" | tee "$OUTPUT_ROOT/evidence/zod-validation/zod_usage_count.txt"
```

### SA4 — THE SCHEMA DIFF (Critical)

**TASK SA4.1:** Compare Backend stages vs Dashboard stages
```bash
python3 -c "
import json, re

# Backend stages (from earlier capture)
backend_stages_file = '$OUTPUT_ROOT/evidence/schema-alignment/sa1_2_backend_stages.txt'
with open(backend_stages_file) as f:
    backend_stages_text = f.read()

# Extract stage values
import re
backend_stages = set(re.findall(r'\"([^\"]+)\"', backend_stages_text))

print('=== BACKEND STAGES ===')
print(sorted(backend_stages))

# Dashboard stages (from grep)
dashboard_stages_file = '$OUTPUT_ROOT/evidence/dashboard-types/sa3_2_stage_definitions.txt'
try:
    with open(dashboard_stages_file) as f:
        dashboard_text = f.read()
    # Try to extract stage values from dashboard
    # This is heuristic — adapt based on actual code patterns
    dashboard_stages = set(re.findall(r'[\"\\']([a-z_]+)[\"\\']', dashboard_text.lower()))
    
    print()
    print('=== DASHBOARD STAGE REFERENCES ===')
    print(sorted(dashboard_stages))
    
    print()
    print('=== COMPARISON ===')
    
    # Check for mismatches
    backend_lower = {s.lower() for s in backend_stages}
    common = backend_lower & dashboard_stages
    only_backend = backend_stages - {s for s in backend_stages if s.lower() in dashboard_stages}
    only_dashboard = dashboard_stages - backend_lower
    
    if only_backend:
        print(f'STAGES ONLY IN BACKEND: {only_backend}')
    if only_dashboard:
        print(f'STAGES ONLY IN DASHBOARD: {only_dashboard}')
    
    # CASE SENSITIVITY CHECK (THE ZOD KILLER)
    for bs in backend_stages:
        for ds in dashboard_stages:
            if bs.lower() == ds.lower() and bs != ds:
                print(f'⚠️  CASE MISMATCH: Backend \"{bs}\" vs Dashboard \"{ds}\"')
    
    if not only_backend and not only_dashboard:
        print('✓ Stage values appear aligned')
    
except FileNotFoundError:
    print('Dashboard stages file not found — manual verification required')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/schema-alignment/sa4_1_stage_comparison.txt"
```

**TASK SA4.2:** TypeScript compilation check
```bash
cd "$DASHBOARD_ROOT" && npx tsc --noEmit 2>&1 \
  | tee "$OUTPUT_ROOT/evidence/dashboard-types/sa4_2_tsc_check.txt"

TSC_EXIT=$?
if [ $TSC_EXIT -eq 0 ]; then
  echo "✓ TypeScript compilation: PASS" >> "$OUTPUT_ROOT/evidence/dashboard-types/sa4_2_tsc_check.txt"
else
  echo "✗ TypeScript compilation: FAIL (exit $TSC_EXIT)" >> "$OUTPUT_ROOT/evidence/dashboard-types/sa4_2_tsc_check.txt"
fi
```
→ **ANY TypeScript error = FAIL.** This is where Zod-style issues manifest.

**TASK SA4.3:** Zod parsing test (if Zod is used)
```bash
# If Zod schemas exist, test them with actual backend data
python3 -c "
import subprocess, json

# Check if Zod is used
with open('$OUTPUT_ROOT/evidence/zod-validation/zod_usage_count.txt') as f:
    count = int(f.read().split(':')[1].strip())

if count == 0:
    print('No Zod usage detected — skipping Zod validation')
else:
    print(f'Zod used {count} times — MANUAL ZOD VALIDATION REQUIRED')
    print()
    print('To test Zod parsing:')
    print('1. Find Zod schemas in dashboard-types/sa3_3_zod_files.txt')
    print('2. Run them against backend_raw_response.json')
    print('3. ANY parse failure = SCHEMA MISMATCH')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/zod-validation/sa4_3_zod_test.txt"
```

```
GATE SA: Backend schema documented. Agent returns matching field names.
  Dashboard types found. Stage values aligned (case-sensitive).
  TypeScript compiles. Zod schemas (if any) parse backend data.
  
  ANY MISMATCH = FAIL. Fix before proceeding.
```

---

## SECTION 2.5: RED-TEAM HARDENING GATES (GPT-RECOMMENDED)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  RED-TEAM HARDENING — These gates catch "false green" scenarios              ║
║                                                                               ║
║  A QA can "pass" while the system is wrong in subtle but dangerous ways.     ║
║  These gates are designed to catch those scenarios.                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### RT1 — Canary Dataset & Multi-Deal Validation (Anti-False-Green)

**Problem:** QA can pass if backend returns empty arrays or minimal fields.

**TASK RT1.1:** Create canary deals across different stages
```bash
# Create 3-5 canary deals for testing
CANARY_PREFIX="QA-CANARY-$(date +%s)"

# Create canary deals in different stages
for STAGE in inbound screening qualified archived; do
  curl -sf -X POST "$BACKEND_API/api/deals" \
    -H "Content-Type: application/json" \
    -d "{\"canonical_name\": \"${CANARY_PREFIX}-${STAGE}\", \"stage\": \"$STAGE\", \"status\": \"active\"}" \
    >> "$OUTPUT_ROOT/evidence/v0-baseline/rt1_1_canary_created.txt" 2>&1
  echo "" >> "$OUTPUT_ROOT/evidence/v0-baseline/rt1_1_canary_created.txt"
done

echo "CANARY_PREFIX=$CANARY_PREFIX" > "$OUTPUT_ROOT/evidence/v0-baseline/canary_prefix.txt"
```

**TASK RT1.2:** Validate schema across ENTIRE returned list (not just first)
```bash
curl -sf "$BACKEND_API/api/deals" | python3 -c "
import json, sys

data = json.load(sys.stdin)
if not isinstance(data, list):
    print('ERROR: Response is not a list')
    sys.exit(1)

print(f'Total deals returned: {len(data)}')

if len(data) == 0:
    print('ERROR: Empty response — cannot validate schema')
    sys.exit(1)

# Collect all field names across ALL deals
all_fields = set()
nullable_fields = set()
missing_fields = {}

for i, deal in enumerate(data):
    deal_fields = set(deal.keys())
    all_fields.update(deal_fields)

    # Track nullable fields (fields that are null in any deal)
    for field, value in deal.items():
        if value is None:
            nullable_fields.add(field)

    # Track missing fields per deal
    if i > 0:
        first_fields = set(data[0].keys())
        missing = first_fields - deal_fields
        if missing:
            missing_fields[i] = list(missing)

print(f'\\nTotal unique fields across all deals: {len(all_fields)}')
print(f'Fields: {sorted(all_fields)}')

print(f'\\nNullable fields (null in at least one deal): {sorted(nullable_fields)}')

if missing_fields:
    print(f'\\nWARNING: Inconsistent schema across deals:')
    for deal_idx, fields in list(missing_fields.items())[:5]:
        print(f'  Deal {deal_idx} missing: {fields}')
    print('  This may cause Zod validation failures!')
else:
    print('\\n✓ All deals have consistent schema')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/schema-alignment/rt1_2_full_list_validation.txt"
```

**TASK RT1.3:** Empty-state test (list_deals with no results)
```bash
# Test agent behavior when searching for non-existent deals
THREAD_EMPTY="qa-r4-empty-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Search for deals with ZZZNEVEREXISTS12345 in the name\",\"thread_id\":\"$THREAD_EMPTY\"}" \
  | python3 -c "
import json, sys
response = json.load(sys.stdin)
print(json.dumps(response, indent=2))

# Check if agent correctly reports 0 results (not inventing entries)
response_text = json.dumps(response).lower()
if 'no deals' in response_text or '0 deal' in response_text or 'no results' in response_text or 'found 0' in response_text:
    print('\\n✓ Agent correctly reports no deals found')
else:
    print('\\n⚠️ WARNING: Agent may be inventing deals or not handling empty results correctly')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/tool-implementation/rt1_3_empty_state.txt"
```

**TASK RT1.4:** Cleanup canary deals
```bash
# Read canary prefix
CANARY_PREFIX=$(cat "$OUTPUT_ROOT/evidence/v0-baseline/canary_prefix.txt" | grep CANARY_PREFIX | cut -d= -f2)

# Get canary deal IDs and delete them
curl -sf "$BACKEND_API/api/deals" | python3 -c "
import json, sys
prefix = '$CANARY_PREFIX'
data = json.load(sys.stdin)
canaries = [d for d in data if d.get('canonical_name', '').startswith(prefix)]
print(f'Found {len(canaries)} canary deals to clean up')
for c in canaries:
    print(f'  {c.get(\"deal_id\")}: {c.get(\"canonical_name\")}')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/v0-baseline/rt1_4_canary_cleanup.txt"

# Note: Actual deletion would require DELETE endpoint - document for manual cleanup if needed
```

### RT2 — Real Backend Proof (Anti-Mock/Stub)

**Problem:** Tests can pass using mocks/stubs instead of real backend calls.

**TASK RT2.1:** Enable structured tool logging (verify real HTTP calls)
```bash
# Check if structured logging exists in tool implementation
grep -n "logger\|logging\|log\.\|print.*url\|print.*status" \
  "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | tee "$OUTPUT_ROOT/evidence/routing-verification/rt2_1_tool_logging.txt"

# Check for DEAL_API_URL resolution
grep -n "DEAL_API_URL\|backend.*url\|api.*url" \
  "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | tee -a "$OUTPUT_ROOT/evidence/routing-verification/rt2_1_tool_logging.txt"
```

**TASK RT2.2:** Capture cross-service correlation (agent → backend)
```bash
# Make a test call with unique correlation ID
TRACE_ID="QA-R4-TRACE-$(date +%s)"
THREAD_TRACE="qa-r4-trace-$(date +%s)"

# Clear logs first
docker logs zakops-agent-api --since 1s 2>&1 > /dev/null
docker logs zakops-backend-backend-1 --since 1s 2>&1 > /dev/null

# Make the call
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "X-Correlation-ID: $TRACE_ID" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"List all my deals\",\"thread_id\":\"$THREAD_TRACE\"}" > /dev/null

sleep 2

# Capture agent logs
echo "=== AGENT LOGS ===" > "$OUTPUT_ROOT/evidence/routing-verification/rt2_2_correlation.txt"
docker logs zakops-agent-api 2>&1 | tail -30 \
  | grep -E "list_deals|/api/deals|$TRACE_ID|correlation|deal" \
  >> "$OUTPUT_ROOT/evidence/routing-verification/rt2_2_correlation.txt"

# Capture backend logs
echo -e "\n=== BACKEND LOGS ===" >> "$OUTPUT_ROOT/evidence/routing-verification/rt2_2_correlation.txt"
docker logs zakops-backend-backend-1 2>&1 | tail -30 \
  | grep -E "/api/deals|$TRACE_ID|correlation|GET" \
  >> "$OUTPUT_ROOT/evidence/routing-verification/rt2_2_correlation.txt"

echo -e "\nTrace ID: $TRACE_ID" >> "$OUTPUT_ROOT/evidence/routing-verification/rt2_2_correlation.txt"
```
→ Both services must show correlated log entries proving real HTTP call.

**TASK RT2.3:** Verify response is NOT from cache/stub
```bash
# Check for any mock/stub/cache indicators in tool code
grep -n "mock\|stub\|cache\|fake\|hardcoded\|dummy" \
  "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | tee "$OUTPUT_ROOT/evidence/routing-verification/rt2_3_no_mocks.txt"

MOCK_COUNT=$(wc -l < "$OUTPUT_ROOT/evidence/routing-verification/rt2_3_no_mocks.txt")
echo "Mock/stub/cache references: $MOCK_COUNT" >> "$OUTPUT_ROOT/evidence/routing-verification/rt2_3_no_mocks.txt"
```
→ Should be 0 in production tool code.

### RT3 — DB Source-of-Truth Assertion (Anti-Split-Brain)

**Problem:** Everything works, but on the wrong database.

**TASK RT3.1:** Verify ALL services point to same database
```bash
echo "=== DATABASE SOURCE OF TRUTH CHECK ===" > "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"

# Backend database
echo -e "\n--- BACKEND DATABASE ---" >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"
docker exec zakops-backend-backend-1 env 2>/dev/null | grep -E "DATABASE|POSTGRES|DB_" \
  | sed 's/password=[^&]*/password=REDACTED/gi' \
  >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"

# Query actual database
echo -e "\n--- DATABASE IDENTITY ---" >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"
docker exec zakops-postgres-1 psql -U dealengine -d zakops -c "
SELECT current_database(), inet_server_addr(), version();
" 2>/dev/null >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"

# Count deals in actual database
echo -e "\n--- DEAL COUNT IN ACTUAL DB ---" >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"
docker exec zakops-postgres-1 psql -U dealengine -d zakops -c "
SELECT COUNT(*) as deal_count FROM deals;
" 2>/dev/null >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"

# Compare with API response
echo -e "\n--- DEAL COUNT FROM API ---" >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"
curl -sf "$BACKEND_API/api/deals" | python3 -c "import json,sys; print(f'API returns: {len(json.load(sys.stdin))} deals')" \
  >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_1_db_sot.txt"
```
→ Database count MUST match API count. If not = **SPLIT-BRAIN DETECTED**.

**TASK RT3.2:** Check for other postgres containers (orphan detection)
```bash
echo "=== POSTGRES CONTAINER INVENTORY ===" > "$OUTPUT_ROOT/evidence/v0-baseline/rt3_2_postgres_containers.txt"
docker ps -a --filter "name=postgres" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" \
  >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_2_postgres_containers.txt"

POSTGRES_COUNT=$(docker ps --filter "name=postgres" --format "{{.Names}}" | wc -l)
echo -e "\nRunning postgres containers: $POSTGRES_COUNT" >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_2_postgres_containers.txt"

if [ "$POSTGRES_COUNT" -gt 1 ]; then
  echo "⚠️ WARNING: Multiple postgres containers detected — split-brain risk!" \
    >> "$OUTPUT_ROOT/evidence/v0-baseline/rt3_2_postgres_containers.txt"
fi
```

### RT4 — OpenAPI Contract Validation (Anti-Schema-Drift)

**Problem:** Zod patches are symptoms; root fix is contract alignment.

**TASK RT4.1:** Fetch and validate against OpenAPI spec
```bash
# Get OpenAPI spec
curl -sf "$BACKEND_API/openapi.json" > "$OUTPUT_ROOT/evidence/schema-alignment/rt4_1_openapi.json" 2>/dev/null \
  || curl -sf "$BACKEND_API/docs/openapi.json" > "$OUTPUT_ROOT/evidence/schema-alignment/rt4_1_openapi.json" 2>/dev/null \
  || echo "OpenAPI spec not available at /openapi.json or /docs/openapi.json" > "$OUTPUT_ROOT/evidence/schema-alignment/rt4_1_openapi.json"

# Check if we got a valid spec
if [ -f "$OUTPUT_ROOT/evidence/schema-alignment/rt4_1_openapi.json" ]; then
  python3 -c "
import json
with open('$OUTPUT_ROOT/evidence/schema-alignment/rt4_1_openapi.json') as f:
    try:
        spec = json.load(f)
        if 'openapi' in spec or 'swagger' in spec:
            print('✓ Valid OpenAPI spec found')
            print(f'  Version: {spec.get(\"openapi\", spec.get(\"swagger\", \"unknown\"))}')
            print(f'  Paths: {len(spec.get(\"paths\", {}))}')
            # Extract /api/deals schema if present
            if '/api/deals' in spec.get('paths', {}):
                print('  /api/deals endpoint: FOUND')
            else:
                print('  /api/deals endpoint: NOT FOUND')
        else:
            print('⚠️ File is not a valid OpenAPI spec')
    except:
        print('⚠️ Could not parse OpenAPI spec')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/schema-alignment/rt4_1_openapi_validation.txt"
fi
```

**TASK RT4.2:** Compare runtime response to OpenAPI schema
```bash
# This requires openapi-spec-validator or similar tool
# Document the manual verification requirement
echo "=== OpenAPI Runtime Validation ===" > "$OUTPUT_ROOT/evidence/schema-alignment/rt4_2_runtime_validation.txt"
echo "Manual verification required:" >> "$OUTPUT_ROOT/evidence/schema-alignment/rt4_2_runtime_validation.txt"
echo "1. Compare backend_raw_response.json against OpenAPI Deal schema" >> "$OUTPUT_ROOT/evidence/schema-alignment/rt4_2_runtime_validation.txt"
echo "2. Verify all required fields are present" >> "$OUTPUT_ROOT/evidence/schema-alignment/rt4_2_runtime_validation.txt"
echo "3. Verify field types match spec" >> "$OUTPUT_ROOT/evidence/schema-alignment/rt4_2_runtime_validation.txt"
```

### RT5 — Negative Path Verification (Chaos/Attacker Cases)

**Problem:** QA is oriented toward happy path; need to test failure modes.

**TASK RT5.1:** Backend down — tool must return structured error
```bash
echo "=== BACKEND DOWN TEST ===" > "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "This test requires temporarily stopping the backend." >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "Manual test procedure:" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "1. docker stop zakops-backend-backend-1" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "2. Invoke agent with 'list all deals'" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "3. Verify agent returns structured error (not hallucinated data)" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "4. docker start zakops-backend-backend-1" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "Expected: ToolResult with success=false and error message" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
echo "NOT Expected: Agent inventing deal data" >> "$OUTPUT_ROOT/evidence/regression/rt5_1_backend_down.txt"
```

**TASK RT5.2:** Auth failure (401/403) handling
```bash
# Test with invalid/missing service token
THREAD_NOAUTH="qa-r4-noauth-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: INVALID_TOKEN_12345" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"List all my deals\",\"thread_id\":\"$THREAD_NOAUTH\"}" \
  -w "\nHTTP: %{http_code}" \
  | tee "$OUTPUT_ROOT/evidence/regression/rt5_2_auth_failure.txt"

echo -e "\n\n=== EXPECTED BEHAVIOR ===" >> "$OUTPUT_ROOT/evidence/regression/rt5_2_auth_failure.txt"
echo "Should return 401/403 or structured auth error" >> "$OUTPUT_ROOT/evidence/regression/rt5_2_auth_failure.txt"
echo "Should NOT expose internal errors or stack traces" >> "$OUTPUT_ROOT/evidence/regression/rt5_2_auth_failure.txt"
```

**TASK RT5.3:** Large dataset handling (pagination)
```bash
# Check if tools handle pagination/limits
grep -n "limit\|offset\|page\|pagination\|max_" \
  "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/rt5_3_pagination.txt"

echo -e "\n=== PAGINATION CHECK ===" >> "$OUTPUT_ROOT/evidence/tool-implementation/rt5_3_pagination.txt"
echo "Verify list_deals has reasonable limit to prevent 10k deals to model" >> "$OUTPUT_ROOT/evidence/tool-implementation/rt5_3_pagination.txt"
```

### RT6 — Tool Semantics Guardrails (Prevent Wrong Tool Selection)

**Problem:** Model keeps using search_deals for "how many deals" questions.

**TASK RT6.1:** Verify tool descriptions enforce correct selection
```bash
# Check tool descriptions in deal_tools.py
python3 -c "
import re
with open('$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py') as f:
    content = f.read()

# Extract docstrings for list_deals and search_deals
for tool in ['list_deals', 'search_deals']:
    match = re.search(rf'(?:async )?def {tool}.*?\"\"\"(.*?)\"\"\"', content, re.DOTALL)
    if match:
        print(f'=== {tool} DOCSTRING ===')
        print(match.group(1).strip()[:500])
        print()
" 2>&1 | tee "$OUTPUT_ROOT/evidence/system-prompt/rt6_1_tool_descriptions.txt"
```

**TASK RT6.2:** Verify prompt explicitly guides tool selection
```bash
# Check for explicit routing guidance in prompt
grep -B 2 -A 5 "list_deals\|search_deals\|count\|pipeline\|summary" \
  "$AGENT_ROOT/app/core/prompts/system.md" \
  | head -50 \
  | tee "$OUTPUT_ROOT/evidence/system-prompt/rt6_2_tool_guidance.txt"

# Check for explicit "use X for Y" patterns
grep -E "use.*list_deals|use.*search_deals|for counting|for searching" \
  "$AGENT_ROOT/app/core/prompts/system.md" \
  | tee -a "$OUTPUT_ROOT/evidence/system-prompt/rt6_2_tool_guidance.txt"
```
→ Must have explicit guidance: "Counts/pipeline/summary → list_deals" and "Exact lookup → search_deals"

**TASK RT6.3:** Prompt test for correct tool selection
```bash
# Test 1: Count question should use list_deals
THREAD_SEL1="qa-r4-sel1-$(date +%s)"
echo "=== TEST: Count question ===" > "$OUTPUT_ROOT/evidence/system-prompt/rt6_3_selection_tests.txt"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"How many deals are in my pipeline?\",\"thread_id\":\"$THREAD_SEL1\"}" \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
text = json.dumps(r)
if 'list_deals' in text:
    print('✓ CORRECT: Used list_deals for count question')
elif 'search_deals' in text:
    print('⚠️ WRONG: Used search_deals for count question')
else:
    print('? Could not determine which tool was used')
" >> "$OUTPUT_ROOT/evidence/system-prompt/rt6_3_selection_tests.txt"

# Test 2: Search question should use search_deals
THREAD_SEL2="qa-r4-sel2-$(date +%s)"
echo -e "\n=== TEST: Search question ===" >> "$OUTPUT_ROOT/evidence/system-prompt/rt6_3_selection_tests.txt"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Find the deal named Healthcare Solutions Inc\",\"thread_id\":\"$THREAD_SEL2\"}" \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
text = json.dumps(r)
if 'search_deals' in text:
    print('✓ CORRECT: Used search_deals for search question')
elif 'list_deals' in text:
    print('⚠️ WRONG: Used list_deals for search question')
else:
    print('? Could not determine which tool was used')
" >> "$OUTPUT_ROOT/evidence/system-prompt/rt6_3_selection_tests.txt"
```

### RT7 — Response Wrapper Consistency (No Double-Wrapping)

**Problem:** Backend uses envelope; if tools wrap again, cascades occur.

**TASK RT7.1:** Verify ToolResult schema is canonical
```bash
# Check ToolResult structure
cat "$AGENT_ROOT/app/core/langgraph/tools/schemas.py" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/rt7_1_toolresult_schema.txt"

# Check for double-wrapping patterns
grep -n "ToolResult\|success.*data\|data.*success" \
  "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/rt7_1_wrapping_check.txt"
```

**TASK RT7.2:** Verify tool output is exactly expected shape
```bash
# Check a live tool response shape
THREAD_SHAPE="qa-r4-shape-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"List all my deals\",\"thread_id\":\"$THREAD_SHAPE\"}" \
  | python3 -c "
import json, sys

response = json.load(sys.stdin)

# Check for double-wrapping indicators
response_str = json.dumps(response)

# Look for nested success/data patterns
nested_success = response_str.count('\"success\"')
nested_data = response_str.count('\"data\"')

print(f'Occurrences of \"success\": {nested_success}')
print(f'Occurrences of \"data\": {nested_data}')

if nested_success > 1 or nested_data > 2:
    print('⚠️ WARNING: Possible double-wrapping detected')
else:
    print('✓ No obvious double-wrapping')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/tool-implementation/rt7_2_shape_check.txt"
```

### RT8 — Skip Risk Mitigation (Skipped Tests = Unknown State)

**Problem:** Tests skip and we don't actually know if things work.

**TASK RT8.1:** Verify critical tests are not skippable
```bash
echo "=== SKIP RISK CHECK ===" > "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"

# Check for skip decorators in test files
find "$AGENT_ROOT" -name "test_*.py" -o -name "*_test.py" 2>/dev/null \
  | xargs grep -l "skip\|Skip\|@pytest.mark.skip" 2>/dev/null \
  | tee -a "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"

SKIP_COUNT=$(find "$AGENT_ROOT" -name "test_*.py" -o -name "*_test.py" 2>/dev/null \
  | xargs grep -c "@pytest.mark.skip\|pytest.skip\|unittest.skip" 2>/dev/null \
  | awk -F: '{sum+=$2} END {print sum}')

echo -e "\nTotal skip decorators found: ${SKIP_COUNT:-0}" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
```

**TASK RT8.2:** Final QA summary must include skip count
```bash
echo "=== QA SUMMARY REQUIREMENTS ===" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
echo "The final report MUST include:" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
echo "  - Total tests run" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
echo "  - Tests passed" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
echo "  - Tests failed" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
echo "  - Tests SKIPPED" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
echo "  - Threshold: 0 skipped for core R4 suites" >> "$OUTPUT_ROOT/evidence/final-gate/rt8_1_skip_check.txt"
```

### RT9 — Golden Prompt E2E Verification

**Problem:** Need measurable "one question that must work".

**TASK RT9.1:** Define and execute golden prompt
```bash
GOLDEN_THREAD="qa-r4-golden-$(date +%s)"

# THE GOLDEN PROMPT
GOLDEN_PROMPT="How many deals do I have in my pipeline? Break it down by stage."

# EXPECTED: Tool call logs + tool JSON output + correct count
echo "=== GOLDEN PROMPT TEST ===" > "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"
echo "Prompt: $GOLDEN_PROMPT" >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"
echo "Thread: $GOLDEN_THREAD" >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"
echo "" >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"

# Execute golden prompt
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"$GOLDEN_PROMPT\",\"thread_id\":\"$GOLDEN_THREAD\"}" \
  | python3 -m json.tool \
  >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"

# Get expected answer from backend
echo -e "\n=== EXPECTED ANSWER (from backend) ===" >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"
curl -sf "$BACKEND_API/api/deals" | python3 -c "
import json, sys
from collections import Counter
data = json.load(sys.stdin)
print(f'Total: {len(data)}')
stages = Counter(d.get('stage') for d in data)
for stage, count in stages.most_common():
    print(f'  {stage}: {count}')
" >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"

echo -e "\n=== VERIFICATION ===" >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"
echo "Agent response MUST contain same total and stage breakdown as backend" >> "$OUTPUT_ROOT/evidence/acceptance-test/rt9_1_golden_prompt.txt"
```

### RT10 — Implementation Discipline (Scope Control)

**Problem:** Changes sprawl into unrelated files, creating regressions.

**TASK RT10.1:** Document allowed edit scope
```bash
echo "=== R4 ALLOWED EDIT SCOPE ===" > "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "Only these files should be modified for R4:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "TOOLS:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - app/core/langgraph/tools/deal_tools.py" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - app/core/langgraph/tools/schemas.py" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - app/core/langgraph/tools/__init__.py" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "PROMPTS:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - app/core/prompts/system.md" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "TESTS:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - evals/golden_traces/GT-032.json" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - evals/golden_traces/GT-033.json" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - evals/golden_traces/GT-034.json" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "CI:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "  - scripts/validate_prompt_tools.py" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
echo "Any other file changes require explicit justification." >> "$OUTPUT_ROOT/evidence/final-gate/rt10_1_scope.txt"
```

**TASK RT10.2:** Document rollback plan
```bash
echo "=== R4 ROLLBACK PLAN ===" > "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "If R4 causes regressions:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "1. Revert deal_tools.py to pre-R4 version:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "   git checkout HEAD~1 -- app/core/langgraph/tools/deal_tools.py" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "2. Revert system.md to previous version:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "   git checkout HEAD~1 -- app/core/prompts/system.md" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "3. Restart agent container:" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "   docker compose restart agent-api" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
echo "4. Verify regression is fixed with golden prompt test" >> "$OUTPUT_ROOT/evidence/final-gate/rt10_2_rollback.txt"
```

```
GATE RT (RED-TEAM HARDENING):
  RT1: Canary dataset tested, full list validated, empty state handled
  RT2: Real backend calls proven with correlation IDs
  RT3: DB source-of-truth verified, no split-brain
  RT4: OpenAPI contract captured (manual validation if tooling unavailable)
  RT5: Negative paths documented (backend down, auth fail, large dataset)
  RT6: Tool selection semantics verified with prompt tests
  RT7: Response wrapper consistency checked (no double-wrapping)
  RT8: Skip count documented, 0 skipped for core R4 suites
  RT9: Golden prompt executed with matching evidence
  RT10: Edit scope documented, rollback plan exists
```

---

## SECTION 3: TOOL IMPLEMENTATION VERIFICATION

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  TOOL IMPLEMENTATION — Verify Builder's claims about tool changes            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### TI1 — list_deals Tool

**TASK TI1.1:** Verify list_deals exists and is exported
```bash
# Check function exists
grep -n "def list_deals\|async def list_deals" \
  "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/ti1_1_list_deals_exists.txt"

# Check it's exported
grep -n "list_deals" "$AGENT_ROOT/app/core/langgraph/tools/__init__.py" \
  | tee -a "$OUTPUT_ROOT/evidence/tool-implementation/ti1_1_list_deals_exists.txt"
```
→ Must exist in deal_tools.py AND be exported in __init__.py.

**TASK TI1.2:** Verify list_deals queries BACKEND API (not RAG)
```bash
# Critical: list_deals must call backend, NOT RAG
grep -A 50 "def list_deals\|async def list_deals" \
  "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | grep -E "DEAL_API_URL|/api/deals|backend|rag|RAG_REST" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/ti1_2_routing_check.txt"

# Count RAG references in list_deals
python3 -c "
import re
with open('$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py') as f:
    content = f.read()

# Extract list_deals function
match = re.search(r'((?:async )?def list_deals.*?)(?=\n(?:async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    func = match.group(1)
    rag_refs = len(re.findall(r'rag|RAG', func, re.IGNORECASE))
    backend_refs = len(re.findall(r'DEAL_API|/api/deals|backend', func, re.IGNORECASE))
    print(f'RAG references in list_deals: {rag_refs}')
    print(f'Backend references in list_deals: {backend_refs}')
    if rag_refs > 0:
        print('⚠️  WARNING: list_deals references RAG — should be backend only!')
    if backend_refs == 0:
        print('⚠️  WARNING: list_deals has no backend references!')
" 2>&1 | tee -a "$OUTPUT_ROOT/evidence/tool-implementation/ti1_2_routing_check.txt"
```
→ Must have ZERO RAG references and >0 backend references.

**TASK TI1.3:** Verify list_deals returns ToolResult
```bash
grep -A 50 "def list_deals" "$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py" \
  | grep -E "ToolResult|return.*\{|success.*:|data.*:|error.*:" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/ti1_3_toolresult.txt"
```
→ Must return ToolResult with success, data, error, metadata.

**TASK TI1.4:** LIVE TEST — list_deals actually works
```bash
THREAD_LIST="qa-r4-list-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"How many deals do I have? Give me a count.\",\"thread_id\":\"$THREAD_LIST\"}" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/ti1_4_live_test.txt"
```
→ Agent must respond with deal count that matches backend.

### TI2 — search_deals Fix

**TASK TI2.1:** Verify search_deals NO LONGER queries RAG for deals
```bash
# Extract search_deals function
python3 -c "
import re
with open('$AGENT_ROOT/app/core/langgraph/tools/deal_tools.py') as f:
    content = f.read()

match = re.search(r'((?:async )?def search_deals.*?)(?=\n(?:async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    func = match.group(1)
    print('=== search_deals IMPLEMENTATION ===')
    print(func[:2000])
    print()
    
    # Check routing
    rag_refs = len(re.findall(r'RAG_REST|rag.*query|/rag/', func, re.IGNORECASE))
    backend_refs = len(re.findall(r'DEAL_API|/api/deals', func, re.IGNORECASE))
    
    print(f'RAG query references: {rag_refs}')
    print(f'Backend API references: {backend_refs}')
    
    if rag_refs > 0 and 'knowledge' not in func.lower():
        print('⚠️  search_deals still queries RAG for deals — FIX INCOMPLETE')
    else:
        print('✓ search_deals appears to use backend for deal queries')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/tool-implementation/ti2_1_search_deals_routing.txt"
```

**TASK TI2.2:** LIVE TEST — search_deals returns real deals
```bash
THREAD_SEARCH="qa-r4-search-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Search for deals in inbound stage\",\"thread_id\":\"$THREAD_SEARCH\"}" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/ti2_2_search_live.txt"
```

### TI3 — ToolResult.from_legacy() Fix

**TASK TI3.1:** Verify the from_legacy fix exists
```bash
grep -n "from_legacy\|_legacy\|legacy" \
  "$AGENT_ROOT/app/core/langgraph/tools/schemas.py" \
  | tee "$OUTPUT_ROOT/evidence/tool-implementation/ti3_1_from_legacy.txt"

# Get the full from_legacy method if it exists
grep -A 20 "def from_legacy\|def _from_legacy" \
  "$AGENT_ROOT/app/core/langgraph/tools/schemas.py" \
  >> "$OUTPUT_ROOT/evidence/tool-implementation/ti3_1_from_legacy.txt"
```

```
GATE TI: list_deals exists, exported, uses backend. search_deals fixed.
  ToolResult wrapper present. Live tests return real deal data.
```

---

## SECTION 4: SYSTEM PROMPT VERIFICATION

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  SYSTEM PROMPT — Verify tool documentation and routing guidance              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**TASK SP1.1:** Verify prompt version is v1.4.0-r4
```bash
grep "PROMPT_VERSION" "$AGENT_ROOT/app/core/prompts/system.md" \
  | tee "$OUTPUT_ROOT/evidence/system-prompt/sp1_1_version.txt"
```
→ Must show v1.4.0-r4.

**TASK SP1.2:** Verify list_deals is documented in prompt
```bash
grep -n "list_deals" "$AGENT_ROOT/app/core/prompts/system.md" \
  | tee "$OUTPUT_ROOT/evidence/system-prompt/sp1_2_list_deals_doc.txt"

grep -B 2 -A 10 "list_deals" "$AGENT_ROOT/app/core/prompts/system.md" \
  >> "$OUTPUT_ROOT/evidence/system-prompt/sp1_2_list_deals_doc.txt"
```
→ list_deals must be documented with usage guidance.

**TASK SP1.3:** Verify TOOL ROUTING section exists
```bash
grep -n "TOOL ROUTING\|Tool Routing\|tool routing" \
  "$AGENT_ROOT/app/core/prompts/system.md" \
  | tee "$OUTPUT_ROOT/evidence/system-prompt/sp1_3_routing_section.txt"

grep -A 20 "TOOL ROUTING\|Tool Routing" "$AGENT_ROOT/app/core/prompts/system.md" \
  >> "$OUTPUT_ROOT/evidence/system-prompt/sp1_3_routing_section.txt"
```
→ Must have explicit routing guidance for when to use list_deals vs search_deals.

**TASK SP1.4:** Verify tool count in system prompt
```bash
# Run CI validation
cd "$AGENT_ROOT" && python3 scripts/validate_prompt_tools.py --ci 2>&1 \
  | tee "$OUTPUT_ROOT/evidence/system-prompt/sp1_4_tool_count.txt"
```
→ Should show 8 tools aligned (was 7 in R3).

**TASK SP1.5:** Full system prompt capture for audit
```bash
cat "$AGENT_ROOT/app/core/prompts/system.md" \
  > "$OUTPUT_ROOT/evidence/system-prompt/system_md_full.txt"
```

```
GATE SP: Version v1.4.0-r4. list_deals documented. TOOL ROUTING section exists.
  8 tools validated. Full prompt captured.
```

---

## SECTION 5: ROUTING VERIFICATION (Prove RAG is NOT used for deals)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ROUTING PROOF — Verify agent actually routes deal queries to backend        ║
║  This is the ROOT CAUSE verification.                                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**TASK RV1.1:** Check agent logs for routing evidence
```bash
# Clear recent logs and make a test call
THREAD_ROUTE="qa-r4-route-$(date +%s)"

echo "=== BEFORE TEST ===" > "$OUTPUT_ROOT/evidence/routing-verification/rv1_1_logs.txt"
date >> "$OUTPUT_ROOT/evidence/routing-verification/rv1_1_logs.txt"

# Make the call
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"How many deals do I have in my pipeline?\",\"thread_id\":\"$THREAD_ROUTE\"}" \
  > /dev/null

# Capture logs
echo -e "\n=== AGENT LOGS ===" >> "$OUTPUT_ROOT/evidence/routing-verification/rv1_1_logs.txt"
docker logs zakops-agent-api 2>&1 | tail -50 \
  | grep -E "list_deals|search_deals|/api/deals|rag|RAG|backend|DEAL_API" \
  >> "$OUTPUT_ROOT/evidence/routing-verification/rv1_1_logs.txt"
```

**TASK RV1.2:** Verify NO RAG calls for deal count questions
```bash
# Check agent logs for RAG calls
docker logs zakops-agent-api 2>&1 | tail -100 \
  | grep -i "rag.*query\|/rag/\|RAG_REST" \
  | tee "$OUTPUT_ROOT/evidence/routing-verification/rv1_2_rag_calls.txt"

RAG_CALLS=$(wc -l < "$OUTPUT_ROOT/evidence/routing-verification/rv1_2_rag_calls.txt")
echo "RAG calls found in recent logs: $RAG_CALLS" \
  >> "$OUTPUT_ROOT/evidence/routing-verification/rv1_2_rag_calls.txt"
```
→ Should be 0 for deal-related queries. If RAG is still being called for deals = **FIX INCOMPLETE**.

**TASK RV1.3:** Verify backend /api/deals WAS called
```bash
# Check backend logs for deal API calls
docker logs zakops-backend-backend-1 2>&1 | tail -50 \
  | grep -E "/api/deals|GET.*deals" \
  | tee "$OUTPUT_ROOT/evidence/routing-verification/rv1_3_backend_calls.txt"

BACKEND_CALLS=$(wc -l < "$OUTPUT_ROOT/evidence/routing-verification/rv1_3_backend_calls.txt")
echo "Backend /api/deals calls found: $BACKEND_CALLS" \
  >> "$OUTPUT_ROOT/evidence/routing-verification/rv1_3_backend_calls.txt"
```
→ Should be >0 showing the agent actually called the backend.

```
GATE RV: Agent logs show list_deals used. NO RAG calls for deal queries.
  Backend /api/deals WAS called. Routing fix confirmed.
```

---

## SECTION 6: GOLDEN TRACE VERIFICATION

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  GOLDEN TRACES — Verify new traces exist and suite passes                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**TASK GT1.1:** Verify GT-032, GT-033, GT-034 exist
```bash
for GT in GT-032 GT-033 GT-034; do
  FILE="$EVALS_ROOT/golden_traces/${GT}.json"
  if [ -f "$FILE" ]; then
    echo "EXISTS: $GT ($(wc -l < "$FILE") lines)"
    python3 -c "import json; json.load(open('$FILE')); print('  Valid JSON: YES')" 2>&1 || echo "  Valid JSON: NO"
  else
    echo "MISSING: $GT"
  fi
done | tee "$OUTPUT_ROOT/evidence/golden-traces/gt1_1_new_traces.txt"
```

**TASK GT1.2:** Verify new traces test list_deals
```bash
for GT in GT-032 GT-033 GT-034; do
  FILE="$EVALS_ROOT/golden_traces/${GT}.json"
  if [ -f "$FILE" ]; then
    echo "=== $GT ===" 
    grep -i "list_deals\|how many deals\|pipeline" "$FILE" | head -5
  fi
done | tee "$OUTPUT_ROOT/evidence/golden-traces/gt1_2_trace_content.txt"
```

**TASK GT1.3:** Run full golden trace suite
```bash
cd "$EVALS_ROOT" && python3 golden_trace_runner.py 2>&1 \
  | tee "$OUTPUT_ROOT/evidence/golden-traces/gt1_3_suite_results.txt"

# Extract pass rate
grep -E "pass|fail|accuracy|total" "$OUTPUT_ROOT/evidence/golden-traces/gt1_3_suite_results.txt" \
  | tail -10 >> "$OUTPUT_ROOT/evidence/golden-traces/gt1_3_suite_results.txt"
```
→ All traces must pass. Accuracy ≥95%.

**TASK GT1.4:** Count total traces
```bash
TRACE_COUNT=$(ls "$EVALS_ROOT/golden_traces/"GT-*.json 2>/dev/null | wc -l)
echo "Total golden traces: $TRACE_COUNT" \
  | tee "$OUTPUT_ROOT/evidence/golden-traces/gt1_4_trace_count.txt"
```
→ Should be ≥34 (31 from R3 + 3 new).

```
GATE GT: GT-032/033/034 exist and valid. Suite passes ≥95%. ≥34 total traces.
```

---

## SECTION 7: THE ACCEPTANCE TEST

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ACCEPTANCE TEST — THE ONE TEST THAT MATTERS                                 ║
║                                                                               ║
║  Dashboard deal count MUST equal Agent deal count.                           ║
║  If they disagree, the mission is NOT COMPLETE.                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**TASK AT1.1:** Get Backend deal count (source of truth)
```bash
curl -sf "$BACKEND_API/api/deals" | python3 -c "
import json, sys
from collections import Counter

data = json.load(sys.stdin)
print('=== BACKEND (Source of Truth) ===')
print(f'Total deals: {len(data)}')

stages = Counter(d.get('stage', 'MISSING') for d in data)
print('By stage:')
for stage, count in stages.most_common():
    print(f'  {stage}: {count}')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/acceptance-test/at1_1_backend_count.txt"
```

**TASK AT1.2:** Get Agent deal count
```bash
THREAD_ACCEPT="qa-r4-accept-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"How many deals do I have in my pipeline? Give me the exact count and break it down by stage.\",\"thread_id\":\"$THREAD_ACCEPT\"}" \
  | python3 -m json.tool \
  | tee "$OUTPUT_ROOT/evidence/acceptance-test/at1_2_agent_response.txt"
```

**TASK AT1.3:** COMPARE — Must match exactly
```bash
echo "=== ACCEPTANCE TEST COMPARISON ===" \
  | tee "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"

echo -e "\nBackend says:" >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"
cat "$OUTPUT_ROOT/evidence/acceptance-test/at1_1_backend_count.txt" \
  >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"

echo -e "\n\nAgent says:" >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"
# Extract agent's answer (adapt parsing based on response format)
cat "$OUTPUT_ROOT/evidence/acceptance-test/at1_2_agent_response.txt" \
  >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"

echo -e "\n\n=== MANUAL VERIFICATION REQUIRED ===" \
  >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"
echo "Compare the numbers above. They MUST match exactly." \
  >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"
echo "If backend says 10 (8 inbound, 1 screening, 1 archived)," \
  >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"
echo "agent must say 10 (8 inbound, 1 screening, 1 archived)." \
  >> "$OUTPUT_ROOT/evidence/acceptance-test/at1_3_comparison.txt"
```

```
GATE AT (CRITICAL): Backend count == Agent count. EXACT match required.
  THIS GATE DETERMINES IF THE MISSION SUCCEEDED.
```

---

## SECTION 8: REGRESSION SUITE

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  REGRESSION — Ensure R4 changes didn't break existing functionality          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**TASK REG.1:** Agent health
```bash
curl -sf "$AGENT_API/health" -w "\nHTTP: %{http_code}" \
  | tee "$OUTPUT_ROOT/evidence/regression/reg1_health.txt"
```

**TASK REG.2:** get_deal still works
```bash
THREAD_GET="qa-r4-reg-get-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Show me details for deal DL-0001\",\"thread_id\":\"$THREAD_GET\"}" \
  -w "\nHTTP: %{http_code}" \
  | tee "$OUTPUT_ROOT/evidence/regression/reg2_get_deal.txt"
```

**TASK REG.3:** search_deals still works
```bash
THREAD_SRCH="qa-r4-reg-search-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Find deals with healthcare in the name\",\"thread_id\":\"$THREAD_SRCH\"}" \
  -w "\nHTTP: %{http_code}" \
  | tee "$OUTPUT_ROOT/evidence/regression/reg3_search_deals.txt"
```

**TASK REG.4:** HITL still triggers for create_deal
```bash
THREAD_HITL="qa-r4-reg-hitl-$(date +%s)"
curl -s -X POST "$AGENT_API/agent/invoke" \
  -H "X-Service-Token: $SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Create a new deal for QA Test Company\",\"thread_id\":\"$THREAD_HITL\"}" \
  | tee "$OUTPUT_ROOT/evidence/regression/reg4_hitl.txt"
```
→ Must trigger HITL, not auto-execute.

**TASK REG.5:** All imports work
```bash
cd "$AGENT_ROOT" && python3 -c "
from app.core.langgraph.tools.deal_tools import (
    list_deals, search_deals, get_deal, transition_deal, 
    add_note, create_deal, get_deal_health
)
from app.core.langgraph.tools.schemas import ToolResult
print('ALL IMPORTS OK')
" 2>&1 | tee "$OUTPUT_ROOT/evidence/regression/reg5_imports.txt"
```

**TASK REG.6:** Dashboard TypeScript still compiles
```bash
cd "$DASHBOARD_ROOT" && npx tsc --noEmit 2>&1 \
  | tee "$OUTPUT_ROOT/evidence/regression/reg6_tsc.txt"
echo "Exit code: $?" >> "$OUTPUT_ROOT/evidence/regression/reg6_tsc.txt"
```
→ **CRITICAL for Zod prevention.** Must exit 0.

```
GATE REG: Health OK. Existing tools work. HITL triggers. Imports succeed.
  TypeScript compiles (CRITICAL).
```

---

## SECTION 9: COVERAGE MATRIX

**The auditor MUST fill in every cell. NO BLANKS.**

```
┌──────────┬───────────────────────────────────────────┬────────┬──────────────┬───────────────┐
│ Section  │ Verification                              │ Status │ Evidence     │ Notes         │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ V0       │ Agent API healthy                         │        │              │               │
│ V0       │ Backend API healthy                       │        │              │               │
│ V0       │ Backend /api/deals returns data           │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ SA1      │ Backend schema documented (all fields)    │        │              │               │
│ SA1      │ Backend stage values extracted            │        │              │               │
│ SA2      │ list_deals implementation captured        │        │              │               │
│ SA2      │ ToolResult schema documented              │        │              │               │
│ SA2      │ Agent returns matching field names        │        │              │               │
│ SA3      │ Dashboard Deal types found                │        │              │               │
│ SA3      │ Dashboard stage values documented         │        │              │               │
│ SA3      │ Zod schemas identified (if any)           │        │              │               │
│ SA4      │ Stage values match (case-sensitive)       │        │              │               │
│ SA4      │ TypeScript compiles (tsc --noEmit)        │        │              │               │
│ SA4      │ Zod parsing works (if applicable)         │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ TI1      │ list_deals exists in deal_tools.py        │        │              │               │
│ TI1      │ list_deals exported in __init__.py        │        │              │               │
│ TI1      │ list_deals uses backend (0 RAG refs)      │        │              │               │
│ TI1      │ list_deals returns ToolResult             │        │              │               │
│ TI1      │ list_deals LIVE TEST passes               │        │              │               │
│ TI2      │ search_deals no longer uses RAG for deals │        │              │               │
│ TI2      │ search_deals LIVE TEST passes             │        │              │               │
│ TI3      │ ToolResult.from_legacy() fix verified     │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ SP       │ Prompt version v1.4.0-r4                  │        │              │               │
│ SP       │ list_deals documented in prompt           │        │              │               │
│ SP       │ TOOL ROUTING section exists               │        │              │               │
│ SP       │ CI validates 8 tools                      │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ RV       │ Agent logs show list_deals called         │        │              │               │
│ RV       │ NO RAG calls for deal queries             │        │              │               │
│ RV       │ Backend /api/deals WAS called             │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ GT       │ GT-032 exists and valid JSON              │        │              │               │
│ GT       │ GT-033 exists and valid JSON              │        │              │               │
│ GT       │ GT-034 exists and valid JSON              │        │              │               │
│ GT       │ Golden trace suite passes ≥95%            │        │              │               │
│ GT       │ Total traces ≥34                          │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ AT       │ Backend deal count extracted              │        │              │               │
│ AT       │ Agent deal count extracted                │        │              │               │
│ AT       │ COUNTS MATCH EXACTLY                      │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ REG      │ Agent health 200                          │        │              │               │
│ REG      │ get_deal works                            │        │              │               │
│ REG      │ search_deals works                        │        │              │               │
│ REG      │ HITL triggers for create_deal             │        │              │               │
│ REG      │ All imports succeed                       │        │              │               │
│ REG      │ TypeScript compiles (exit 0)              │        │              │               │
├──────────┼───────────────────────────────────────────┼────────┼──────────────┼───────────────┤
│ RT1      │ Canary deals created across stages        │        │              │               │
│ RT1      │ Full list schema validated (all deals)    │        │              │               │
│ RT1      │ Empty-state test passes (no hallucination)│        │              │               │
│ RT2      │ Tool logging shows real HTTP calls        │        │              │               │
│ RT2      │ Correlation IDs match agent→backend       │        │              │               │
│ RT2      │ No mock/stub/cache in tool code           │        │              │               │
│ RT3      │ All services point to same database       │        │              │               │
│ RT3      │ DB count matches API count (no split-brain)│        │              │               │
│ RT4      │ OpenAPI spec captured                     │        │              │               │
│ RT5      │ Backend-down behavior documented          │        │              │               │
│ RT5      │ Auth failure returns proper error         │        │              │               │
│ RT5      │ Pagination/limit exists for large datasets│        │              │               │
│ RT6      │ Tool descriptions enforce correct selection│        │              │               │
│ RT6      │ Prompt has explicit routing guidance      │        │              │               │
│ RT6      │ Tool selection tests pass (count→list)    │        │              │               │
│ RT7      │ ToolResult schema is canonical            │        │              │               │
│ RT7      │ No double-wrapping in responses           │        │              │               │
│ RT8      │ Skip count documented                     │        │              │               │
│ RT8      │ 0 skipped tests for core R4 suites        │        │              │               │
│ RT9      │ Golden prompt executed                    │        │              │               │
│ RT9      │ Golden prompt result matches backend      │        │              │               │
│ RT10     │ Edit scope documented                     │        │              │               │
│ RT10     │ Rollback plan exists                      │        │              │               │
└──────────┴───────────────────────────────────────────┴────────┴──────────────┴───────────────┘

TOTAL CELLS: 65
ALL MUST BE FILLED. NO BLANKS.
```

---

## SECTION 10: DISCREPANCIES TO INVESTIGATE

Pre-identified suspicious claims that require deeper verification:

| ID | Suspicion | Verification Method |
|----|-----------|---------------------|
| D-1 | **list_deals "queries backend"** — does it actually make HTTP call to DEAL_API_URL, or does it still touch RAG anywhere in the code path? | Trace full code path from list_deals to HTTP call |
| D-2 | **search_deals "fixed"** — is RAG completely removed from deal searches, or is there still a code path that queries RAG? | Read full search_deals implementation |
| D-3 | **ToolResult.from_legacy() fix** — what was broken? Did it treat valid data as errors? Is the fix complete? | Read the before/after of from_legacy |
| D-4 | **Stage values case-sensitivity** — do backend stages ("inbound") match dashboard expectations exactly? Any capitalization differences? | Compare backend response to dashboard types |
| D-5 | **CI validation "8 tools"** — did validate_prompt_tools.py actually update to expect 8? Is it hardcoded or dynamic? | Read the CI script source |
| D-6 | **Dashboard TypeScript compiles** — did the builder actually run tsc --noEmit, or did they assume it works? | Run tsc ourselves and capture output |
| D-7 | **Zod schemas** — are there ANY Zod schemas in the dashboard that parse deal data? Would they pass with current backend response? | Search for Zod usage and test |
| D-8 | **Agent response format** — when agent calls list_deals, does it return the same field names the dashboard uses? Any renaming? | Compare live agent response to dashboard expectations |
| D-9 | **Golden trace accuracy** — do GT-032/033/034 actually test list_deals scenarios, or are they generic? | Read trace content |
| D-10 | **TOOL ROUTING section** — does it explicitly say "use list_deals for counting" or is it vague? | Read exact prompt text |
| D-11 | **Empty-state hallucination** — when no deals match, does agent invent data or correctly report "0 found"? | Execute empty-state test RT1.3 |
| D-12 | **Split-brain risk** — are there multiple postgres containers? Does API query the right one? | Check postgres inventory RT3.2 |
| D-13 | **Real HTTP vs mock** — does tool code contain any mock/stub/cache patterns? | Grep tool code for mocks RT2.3 |
| D-14 | **Correlation tracking** — can we trace agent→backend calls via correlation ID? | Execute RT2.2 correlation test |
| D-15 | **Backend-down behavior** — what does agent return when backend is unreachable? | Document expected behavior RT5.1 |
| D-16 | **Auth error handling** — does agent leak stack traces on 401/403? | Test with invalid token RT5.2 |
| D-17 | **Large dataset safety** — does list_deals have a limit to prevent 10k deals to model? | Check pagination RT5.3 |
| D-18 | **Tool selection correctness** — does "how many" use list_deals and "find X" use search_deals? | Execute RT6.3 prompt tests |
| D-19 | **Double-wrapping** — does ToolResult wrap backend envelope creating nested structure? | Check RT7.1 and RT7.2 |
| D-20 | **Test skip risk** — are any core R4 tests marked as skip? | Count skip decorators RT8.1 |

**Each discrepancy MUST have a RESOLVED/CONFIRMED/REMEDIATED status in the final report.**

---

## SECTION 11: REMEDIATION PROTOCOL

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  IF ANY VERIFICATION FAILS — ESPECIALLY SCHEMA ALIGNMENT:                    ║
║                                                                               ║
║  1. DOCUMENT the failure (before state, evidence)                            ║
║  2. FIX the issue — ensure ALL THREE LAYERS agree on schema                  ║
║  3. DOCUMENT the fix (after state, evidence)                                 ║
║  4. RE-VERIFY with the same test                                             ║
║  5. RUN tsc --noEmit AGAIN after any fix                                     ║
║                                                                               ║
║  For SCHEMA MISMATCHES specifically:                                         ║
║  - Identify which layer is wrong (backend, agent, or dashboard)              ║
║  - The backend response is SOURCE OF TRUTH                                   ║
║  - Agent and dashboard must adapt to backend, not vice versa                 ║
║  - After fixing, verify ALL THREE LAYERS again                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## SECTION 12: OUTPUT FORMAT

```markdown
# QA VERIFICATION + REMEDIATION — QA-AB-R4-VERIFY-001 REPORT

**Date:** [timestamp]
**Auditor:** Claude Code (Opus 4.5)
**Target:** AGENT-BRAIN-REMEDIATION-R4 (Deal Tool Data Source Routing)
**Mode:** Verify-Fix-Reverify
**Special Focus:** Schema Alignment / Zod Prevention

## Executive Summary
**VERDICT:** [PASS / PARTIAL / FAIL]
**Tasks Verified:** [X]/42
**Tasks Remediated:** [X]
**Schema Alignment:** [PASS/FAIL]
**TypeScript Compilation:** [PASS/FAIL]
**Acceptance Test (counts match):** [PASS/FAIL]

## Schema Alignment Results
| Layer | Schema Documented | Stages Match | Fields Match |
|-------|-------------------|--------------|--------------|
| Backend API | [Y/N] | — | — |
| Agent ToolResult | [Y/N] | [Y/N] | [Y/N] |
| Dashboard Types | [Y/N] | [Y/N] | [Y/N] |

## Acceptance Test Results
| Source | Total | Inbound | Screening | Archived | Other |
|--------|-------|---------|-----------|----------|-------|
| Backend API | [?] | [?] | [?] | [?] | [?] |
| Agent Response | [?] | [?] | [?] | [?] | [?] |
| **MATCH** | [Y/N] | [Y/N] | [Y/N] | [Y/N] | [Y/N] |

## Gate Results
| Gate | Section | Status | Critical? |
|------|---------|--------|-----------|
| V0 | Baseline | [FILL] | No |
| SA | Schema Alignment | [FILL] | **YES** |
| RT | Red-Team Hardening | [FILL] | **YES** |
| TI | Tool Implementation | [FILL] | Yes |
| SP | System Prompt | [FILL] | Yes |
| RV | Routing Verification | [FILL] | Yes |
| GT | Golden Traces | [FILL] | Yes |
| AT | Acceptance Test | [FILL] | **YES** |
| REG | Regression | [FILL] | **YES** |

## Red-Team Hardening Results
| RT Gate | Description | Status | Evidence |
|---------|-------------|--------|----------|
| RT1 | Canary/Empty-State | [FILL] | rt1_*.txt |
| RT2 | Real Backend Proof | [FILL] | rt2_*.txt |
| RT3 | DB Source-of-Truth | [FILL] | rt3_*.txt |
| RT4 | OpenAPI Contract | [FILL] | rt4_*.txt |
| RT5 | Negative Path Tests | [FILL] | rt5_*.txt |
| RT6 | Tool Semantics | [FILL] | rt6_*.txt |
| RT7 | Response Wrapper | [FILL] | rt7_*.txt |
| RT8 | Skip Risk | [FILL] | rt8_*.txt |
| RT9 | Golden Prompt E2E | [FILL] | rt9_*.txt |
| RT10 | Scope/Rollback | [FILL] | rt10_*.txt |

## Discrepancy Investigation Results
[D-1 through D-10 with resolutions]

## Coverage Matrix
[Full 42-cell matrix — NO BLANKS]

## Remediation Log
[If any fixes were needed]

## Evidence Directory
[List of all evidence files]
```

---

## COMPLETION CRITERIA

The mission PASSES when:
- ALL 65 coverage matrix cells are PASS or REMEDIATED+PASS
- ALL 20 discrepancies are investigated and resolved
- **Schema Alignment**: Backend, Agent, Dashboard all agree on field names and types
- **TypeScript compiles**: `tsc --noEmit` exits 0
- **Acceptance Test**: Backend deal count == Agent deal count (EXACT)
- Golden trace suite passes ≥95%
- ZERO empty evidence files
- All regression tests pass
- **Red-Team Gates (RT1-RT10)**: All pass or documented exceptions
- **DB Source-of-Truth**: Verified single database, no split-brain
- **No Hallucination**: Empty-state test passes (agent doesn't invent data)
- **Tool Selection**: Prompt tests confirm correct tool routing
- **Skip Count**: 0 skipped for core R4 suites

The mission FAILS when:
- ANY schema mismatch between layers (THE ZOD RULE)
- TypeScript compilation fails
- Acceptance test numbers don't match
- ANY critical gate fails AND cannot be remediated
- Split-brain detected (multiple databases with different data)
- Agent hallucinates data when backend returns empty
- Wrong tool used for count/search questions
- Skipped tests hide failures

---

## SERVICES REFERENCE

| Service | Port | Container |
|---------|------|-----------|
| Agent API | 8095 | zakops-agent-api |
| Backend API | 8091 | zakops-backend-backend-1 |
| Dashboard | 3003 | (dev server or container) |

**Evidence Root:** `/home/zaks/bookkeeping/qa-verifications/QA-AB-R4-VERIFY-001/`

---

## SEQUENCING

1. V0 Baseline — verify services running
2. **SA Schema Alignment (CRITICAL)** — extract and compare all three layers
3. **RT Red-Team Hardening (CRITICAL)** — execute RT1-RT10 gates
4. TI Tool Implementation — verify code changes
5. SP System Prompt — verify documentation
6. RV Routing Verification — prove RAG not called for deals
7. GT Golden Traces — verify test coverage
8. **AT Acceptance Test (CRITICAL)** — counts must match
9. REG Regression — nothing else broke
10. Fill coverage matrix — ALL 65 CELLS
11. Investigate discrepancies — ALL 20 RESOLVED
12. Write final report

**Use `/compact` after SA, after RT, and after AT.**

### RT Gate Sequencing (within Section 2.5)
```
RT1 (Canary) → RT2 (Backend Proof) → RT3 (DB SOT) → RT4 (OpenAPI)
    ↓
RT5 (Negative Path) → RT6 (Tool Semantics) → RT7 (Wrapper) → RT8 (Skip)
    ↓
RT9 (Golden Prompt) → RT10 (Scope/Rollback)
```

---

*Generated: 2026-02-05*
*Generator: Claude Opus 4.5*
*Patched: 2026-02-05 (GPT Red-Team Hardening)*
*Target: AGENT-BRAIN-REMEDIATION-R4 Completion*
*Special Focus: Schema Alignment — THE ZOD CASCADE MUST NEVER HAPPEN AGAIN*
*Red-Team Focus: False-Green Prevention, Split-Brain Detection, Hallucination Prevention*
*Verification Cells: 65 (42 original + 23 red-team)*
*Discrepancies: 20 (10 original + 10 red-team)*
*Critical Gates: Schema Alignment, Red-Team Hardening, TypeScript Compilation, Acceptance Test*

---

## APPENDIX: RED-TEAM HARDENING SUMMARY

| # | Risk | Gate | Detection |
|---|------|------|-----------|
| 1 | False green (empty/minimal response) | RT1 | Canary dataset + full list validation |
| 2 | Mock/stub instead of real backend | RT2 | Correlation ID tracing |
| 3 | Split-brain (wrong database) | RT3 | DB SOT assertion |
| 4 | Schema drift (Zod vs OpenAPI) | RT4 | OpenAPI contract validation |
| 5 | Backend down hallucination | RT5 | Negative path tests |
| 6 | Wrong tool selection | RT6 | Prompt tests for semantics |
| 7 | Double-wrapped responses | RT7 | Response shape inspection |
| 8 | Hidden failures (skipped tests) | RT8 | Skip count enforcement |
| 9 | E2E UX broken | RT9 | Golden prompt verification |
| 10 | Scope creep / no rollback | RT10 | Edit scope + rollback plan |

**If ANY finding is discovered during QA, report it and have the builder fix the issue before marking PASS.**
