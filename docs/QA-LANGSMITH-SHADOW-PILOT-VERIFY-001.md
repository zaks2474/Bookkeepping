> **POST-CONSOLIDATION NOTE (2026-02-16):** This document references `/home/zaks/zakops-backend/` paths.
> Backend is now at `/home/zaks/zakops-agent-api/apps/backend/` (MONOREPO-CONSOLIDATION-001).
> See `POST-CONSOLIDATION-PATH-MAPPING.md` for the full path translation table.

# QA MISSION: QA-LANGSMITH-SHADOW-PILOT-VERIFY-001
## Deep Code-Level Verification — Shadow-Mode Pilot Readiness
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: LANGSMITH-SHADOW-PILOT-READY-001 complete (6 phases, 11 AC, 7 evidence files)
## Auditor: Claude Code (Opus 4.6)

---

## 1. Mission Objective

This is an **independent, deep code-level verification** of LANGSMITH-SHADOW-PILOT-READY-001. The completion report claims 11 AC all PASS across 3 files modified, 3 core changes (source_type drift fix, server-side validation, startup warning gate), and 7 evidence files.

This QA will:

1. **Verify the drift elimination claim** — not just searching for `langsmith_production`, but sweeping ALL repos, ALL file types (Python, TypeScript, Markdown, JSON, SQL), and ALL naming variations for any surviving drift.
2. **Verify VALID_SOURCE_TYPES enforcement** — read the actual validation code path, confirm 400 rejection with error detail and valid_values list, and check edge cases (empty string, None, case sensitivity).
3. **Verify the startup warning gate** — read the lifespan function, confirm `app.state.api_key_configured` is set, and check the warning message content.
4. **Re-verify prior hardening claims** — the completion report references measurement (201/200), correlation chain, shadow isolation, flood protection, and deal truth from PostgreSQL. These overlap with LANGSMITH-INTAKE-HARDEN-001 but this mission independently re-checks them using the source evidence files.
5. **Cross-check evidence files against code** — verify E01-E07 line numbers and code snippets still match the actual source.

**What this is NOT**: This is not a build mission. No new code is written unless remediating a FAIL gate. Every PASS requires tee'd evidence.

### Source Artifacts

| Artifact | Path | Key Content |
|----------|------|-------------|
| Completion Report | `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md` | 11 AC, 6 phases, 3 files modified |
| Evidence E01 | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E01-source-type-drift.md` | Zero drift verification |
| Evidence E02 | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E02-intake-auth.md` | Fail-closed middleware + startup gate |
| Evidence E03 | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E03-dedup-measurement.md` | 201/200 response code distinction |
| Evidence E04 | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E04-correlation-id.md` | End-to-end correlation chain |
| Evidence E05 | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E05-shadow-isolation.md` | API filter + dashboard dropdown |
| Evidence E06 | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E06-flood-protection.md` | Rate limiter 120/min |
| Evidence E07 | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E07-deal-truth.md` | PostgreSQL-only deal reads |
| Injection Contract | `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` | Endpoint spec, auth, rate limits, source_type |
| Backend main.py | `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Quarantine POST/GET, VALID_SOURCE_TYPES, lifespan |
| API Key Middleware | `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` | INJECTION_PATHS, fail-closed |
| Security Module | `/home/zaks/zakops-backend/src/api/shared/security.py` | Rate limiters |
| Dashboard Quarantine | `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | Source type filter dropdown |
| Dashboard Route | `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts` | Param forwarding |
| Dashboard API | `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | getQuarantineQueue |
| Backend Client | `/home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py` | HTTP deal reads |
| Deal Tools | `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py` | Agent deal tools |

### Evidence Directory

```
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-shadow-pilot-verify-001
```

All evidence files are written to this directory via `| tee $EVIDENCE_DIR/<gate>.txt`.

---

## 2. Pre-Flight

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-shadow-pilot-verify-001
mkdir -p "$EVIDENCE_DIR"
```

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee "$EVIDENCE_DIR/PF-1-validate-local.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0. If not, stop — codebase is broken before QA starts.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee "$EVIDENCE_DIR/PF-2-tsc.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0, zero errors.

### PF-3: Backend Container Alive
```bash
curl -sf http://localhost:8091/health 2>&1 | tee "$EVIDENCE_DIR/PF-3-backend-health.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0, JSON healthy. If down, live gates become SKIP(services-down).

### PF-4: Source Artifacts Exist
```bash
for f in \
  "/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md" \
  "/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md" \
  "/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E01-source-type-drift.md" \
  "/home/zaks/bookkeeping/docs/_qa_evidence/langsmith_shadow_pilot_ready_001/E07-deal-truth.md"; do
  test -f "$f" && echo "EXISTS: $f" || echo "MISSING: $f"
done 2>&1 | tee "$EVIDENCE_DIR/PF-4-artifacts.txt"
```
**PASS if:** All 4 files exist.

### PF-5: Evidence Directory Ready
```bash
test -d "$EVIDENCE_DIR" && echo "EVIDENCE_DIR ready" | tee "$EVIDENCE_DIR/PF-5-dir-ready.txt"
ls -la "$EVIDENCE_DIR/" | tee -a "$EVIDENCE_DIR/PF-5-dir-ready.txt"
```
**PASS if:** Directory exists and is writable.

---

## 3. Verification Families

### VF-01 — AC-1: source_type Drift Eliminated — 6 checks

**Context:** Completion report claims `langsmith_production` was fixed to `langsmith_live` in 3 locations. E01 evidence shows zero hits in backend/src, backend/docs, dashboard/src, and program spec. This VF independently re-verifies AND expands the search scope to cover ALL repos and file types.

#### VF-01.1: Zero `langsmith_production` in backend Python code
```bash
HITS=$(grep -rn "langsmith_production" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v __pycache__ | wc -l) || HITS=0
echo "BACKEND_SRC_HITS=$HITS" | tee "$EVIDENCE_DIR/VF-01-1.txt"
grep -rn "langsmith_production" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v __pycache__ | tee -a "$EVIDENCE_DIR/VF-01-1.txt"
```
**PASS if:** BACKEND_SRC_HITS is 0.

#### VF-01.2: Zero `langsmith_production` in backend docs
```bash
HITS=$(grep -rn "langsmith_production" /home/zaks/zakops-backend/docs/ 2>/dev/null | wc -l) || HITS=0
echo "BACKEND_DOCS_HITS=$HITS" | tee "$EVIDENCE_DIR/VF-01-2.txt"
grep -rn "langsmith_production" /home/zaks/zakops-backend/docs/ 2>/dev/null | tee -a "$EVIDENCE_DIR/VF-01-2.txt"
```
**PASS if:** BACKEND_DOCS_HITS is 0.

#### VF-01.3: Zero `langsmith_production` in dashboard source
```bash
HITS=$(grep -rn "langsmith_production" /home/zaks/zakops-agent-api/apps/dashboard/src/ 2>/dev/null | wc -l) || HITS=0
echo "DASHBOARD_HITS=$HITS" | tee "$EVIDENCE_DIR/VF-01-3.txt"
grep -rn "langsmith_production" /home/zaks/zakops-agent-api/apps/dashboard/src/ 2>/dev/null | tee -a "$EVIDENCE_DIR/VF-01-3.txt"
```
**PASS if:** DASHBOARD_HITS is 0.

#### VF-01.4: Zero `langsmith_production` in agent-api source (EXPANDED SCOPE)
```bash
HITS=$(grep -rn "langsmith_production" /home/zaks/zakops-agent-api/apps/agent-api/ 2>/dev/null | grep -v __pycache__ | grep -v node_modules | wc -l) || HITS=0
echo "AGENT_API_HITS=$HITS" | tee "$EVIDENCE_DIR/VF-01-4.txt"
grep -rn "langsmith_production" /home/zaks/zakops-agent-api/apps/agent-api/ 2>/dev/null | grep -v __pycache__ | grep -v node_modules | tee -a "$EVIDENCE_DIR/VF-01-4.txt"
```
**PASS if:** AGENT_API_HITS is 0. This checks the AGENT-API repo which was NOT in the original E01 scope.

#### VF-01.5: Zero `langsmith_production` in bookkeeping docs (EXPANDED SCOPE)
```bash
HITS=$(grep -rn "langsmith_production" /home/zaks/bookkeeping/docs/ 2>/dev/null | grep -v "_qa_evidence" | grep -v "COMPLETION" | wc -l) || HITS=0
echo "BOOKKEEPING_DOCS_HITS=$HITS" | tee "$EVIDENCE_DIR/VF-01-5.txt"
grep -rn "langsmith_production" /home/zaks/bookkeeping/docs/ 2>/dev/null | grep -v "_qa_evidence" | grep -v "COMPLETION" | tee -a "$EVIDENCE_DIR/VF-01-5.txt"
```
**PASS if:** BOOKKEEPING_DOCS_HITS is 0 (excluding QA evidence and completion reports which may reference the old name in historical context).

#### VF-01.6: `langsmith_live` canonical name present in all required locations
```bash
echo "=== Backend model comment ===" | tee "$EVIDENCE_DIR/VF-01-6.txt"
grep -n "langsmith_live" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -5 | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
echo "=== VALID_SOURCE_TYPES ===" | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
grep -n "VALID_SOURCE_TYPES" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
echo "=== Injection Contract ===" | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
grep -n "langsmith_live" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
echo "=== Dashboard dropdown ===" | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
grep -n "langsmith_live" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
LOCATIONS=$(grep -rln "langsmith_live" /home/zaks/zakops-backend/src/api/orchestration/main.py /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null | wc -l) || LOCATIONS=0
echo "LOCATIONS_WITH_CANONICAL=$LOCATIONS" | tee -a "$EVIDENCE_DIR/VF-01-6.txt"
```
**PASS if:** LOCATIONS_WITH_CANONICAL is 3 (main.py, INJECTION-CONTRACT.md, quarantine/page.tsx all contain `langsmith_live`).

**Gate VF-01:** All 6 checks pass. Drift is eliminated across ALL repos, not just the 3 original locations.

---

### VF-02 — AC-2/AC-3: VALID_SOURCE_TYPES Constant & Server-Side Validation — 5 checks

**Context:** Completion report claims `VALID_SOURCE_TYPES` constant with 5 values at main.py:277, and server-side validation at main.py:1534 that rejects unknown values with 400.

#### VF-02.1: VALID_SOURCE_TYPES constant defined with exactly 5 values
```bash
grep -n "VALID_SOURCE_TYPES" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-02-1.txt"
# Extract and count the values
python3 -c "
import re
with open('/home/zaks/zakops-backend/src/api/orchestration/main.py') as f:
    content = f.read()
m = re.search(r'VALID_SOURCE_TYPES\s*=\s*\{([^}]+)\}', content)
if m:
    values = [v.strip().strip('\"').strip(\"'\") for v in m.group(1).split(',')]
    print(f'VALUES_FOUND={len(values)}')
    for v in sorted(values):
        print(f'  - {v}')
    expected = {'email', 'email_sync', 'langsmith_shadow', 'langsmith_live', 'manual'}
    if set(values) == expected:
        print('EXACT_MATCH=YES')
    else:
        missing = expected - set(values)
        extra = set(values) - expected
        if missing: print(f'MISSING={missing}')
        if extra: print(f'EXTRA={extra}')
        print('EXACT_MATCH=NO')
else:
    print('VALID_SOURCE_TYPES NOT FOUND')
" 2>&1 | tee -a "$EVIDENCE_DIR/VF-02-1.txt"
```
**PASS if:** Exactly 5 values: `email`, `email_sync`, `langsmith_shadow`, `langsmith_live`, `manual`. EXACT_MATCH=YES.

#### VF-02.2: Validation code rejects unknown source_type with 400
```bash
grep -n -A15 "source_type not in VALID_SOURCE_TYPES\|if.*source_type.*not.*VALID" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -25 | tee "$EVIDENCE_DIR/VF-02-2.txt"
```
**PASS if:** Code block returns `JSONResponse(status_code=400, ...)` when `source_type not in VALID_SOURCE_TYPES`. The response must include error detail explaining what went wrong.

#### VF-02.3: 400 response includes valid_values list
```bash
grep -n "valid_values\|valid.*values\|VALID_SOURCE_TYPES" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-02-3.txt"
```
**PASS if:** The 400 error response body includes a `valid_values` field listing the accepted values. This helps callers self-correct without consulting documentation.

#### VF-02.4: Validation occurs BEFORE database operations
```bash
# Read the quarantine POST handler and check order: validation must come before INSERT
python3 -c "
with open('/home/zaks/zakops-backend/src/api/orchestration/main.py') as f:
    lines = f.readlines()
validation_line = None
insert_line = None
for i, line in enumerate(lines, 1):
    if 'not in VALID_SOURCE_TYPES' in line and validation_line is None:
        validation_line = i
    if 'INSERT INTO' in line and 'quarantine' in line.lower() and insert_line is None:
        insert_line = i
print(f'VALIDATION_LINE={validation_line}')
print(f'INSERT_LINE={insert_line}')
if validation_line and insert_line:
    if validation_line < insert_line:
        print('ORDER=CORRECT (validation before INSERT)')
    else:
        print('ORDER=WRONG (INSERT before validation!)')
else:
    print('ORDER=UNABLE_TO_DETERMINE')
" 2>&1 | tee "$EVIDENCE_DIR/VF-02-4.txt"
```
**PASS if:** ORDER=CORRECT — validation rejects bad source_type BEFORE any database write.

#### VF-02.5: source_type resolution order matches contract (body > header > default)
```bash
grep -n -B3 -A10 "source_type.*=.*item\.\|source_type.*header\|X-Source-Type\|or.*\"email\"" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -20 | tee "$EVIDENCE_DIR/VF-02-5.txt"
```
**PASS if:** Code resolves source_type as: `item.source_type or request.headers.get("X-Source-Type") or "email"` — body first, header second, default third.

**Gate VF-02:** All 5 checks pass. VALID_SOURCE_TYPES enforcement is complete and correctly ordered.

---

### VF-03 — AC-4: Intake Auth Startup Gate — 4 checks

**Context:** Completion report claims a LAYER 2 startup gate at main.py:428-436 that warns when ZAKOPS_API_KEY is unset and sets `app.state.api_key_configured`.

#### VF-03.1: Startup gate exists in lifespan function
```bash
grep -n -B5 -A20 "ZAKOPS_API_KEY\|api_key_configured\|LAYER 2" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -40 | tee "$EVIDENCE_DIR/VF-03-1.txt"
```
**PASS if:** Code within the lifespan context manager reads `ZAKOPS_API_KEY` from environment and sets `app.state.api_key_configured`.

#### VF-03.2: Warning message printed when key is absent
```bash
grep -n "STARTUP WARNING\|ZAKOPS_API_KEY is not set\|injection paths.*503\|fail-closed" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-03-2.txt"
```
**PASS if:** Warning message includes: (a) "ZAKOPS_API_KEY is not set", (b) reference to 503/fail-closed behavior, (c) mentions injection paths.

#### VF-03.3: Success message printed when key IS set
```bash
grep -n "API key gate PASSED\|key.*configured\|api.*key.*set" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-03-3.txt"
```
**PASS if:** Code has a positive confirmation message when the key is configured (not just a warning for the negative case).

#### VF-03.4: Startup gate is inside the lifespan (not in module-level code)
```bash
# Verify the gate is inside the async lifespan context manager
python3 -c "
import re
with open('/home/zaks/zakops-backend/src/api/orchestration/main.py') as f:
    content = f.read()
    lines = content.split('\n')

lifespan_start = None
lifespan_end = None
gate_line = None
for i, line in enumerate(lines, 1):
    if 'async def lifespan' in line or 'def lifespan' in line:
        lifespan_start = i
    if lifespan_start and 'yield' in line and i > lifespan_start:
        lifespan_end = i
        break
    if 'api_key_configured' in line and gate_line is None:
        gate_line = i

print(f'LIFESPAN_START={lifespan_start}')
print(f'LIFESPAN_YIELD={lifespan_end}')
print(f'GATE_LINE={gate_line}')
if lifespan_start and lifespan_end and gate_line:
    if lifespan_start < gate_line < lifespan_end:
        print('PLACEMENT=CORRECT (inside lifespan, before yield)')
    elif gate_line > lifespan_end:
        print('PLACEMENT=WRONG (after yield — runs at shutdown, not startup)')
    else:
        print('PLACEMENT=UNCERTAIN')
else:
    print('PLACEMENT=UNABLE_TO_DETERMINE')
" 2>&1 | tee "$EVIDENCE_DIR/VF-03-4.txt"
```
**PASS if:** PLACEMENT=CORRECT — gate runs at startup (before yield), not at shutdown.

**Gate VF-03:** All 4 checks pass. Startup gate is correctly placed and provides early warning.

---

### VF-04 — AC-5: Created vs Deduped Measurable (201/200) — 4 checks

**Context:** Completion report references E03 evidence showing 201 for new items, 200 for dedup hits, including race-condition handling with ON CONFLICT DO NOTHING.

#### VF-04.1: Dedup SELECT before INSERT
```bash
grep -n "existing.*fetchrow\|message_id.*exists\|SELECT.*quarantine_items.*WHERE.*message_id" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-04-1.txt"
```
**PASS if:** A SELECT query checks for existing `message_id` before INSERT.

#### VF-04.2: Three-tier response code logic (200/201/200-race)
```bash
grep -n "response\.status_code\s*=\s*20[01]" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-04-2.txt"
CODE_LINES=$(grep -c "response\.status_code\s*=\s*20[01]" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>/dev/null) || CODE_LINES=0
echo "STATUS_CODE_ASSIGNMENTS=$CODE_LINES" | tee -a "$EVIDENCE_DIR/VF-04-2.txt"
```
**PASS if:** STATUS_CODE_ASSIGNMENTS >= 3 (200 for dedup SELECT, 201 for INSERT success, 200 for ON CONFLICT race loser).

#### VF-04.3: ON CONFLICT DO NOTHING for race-condition safety
```bash
grep -n "ON CONFLICT\|DO NOTHING\|race.*condition\|TOCTOU" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-04-3.txt"
```
**PASS if:** INSERT statement includes `ON CONFLICT (message_id) DO NOTHING`.

#### VF-04.4: Race-condition fallback returns 200 (not 201)
```bash
grep -n -B5 -A10 "row is None\|row == None\|not row" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -B5 -A10 "quarantine\|status_code" | head -30 | tee "$EVIDENCE_DIR/VF-04-4.txt"
```
**PASS if:** When INSERT returns None (ON CONFLICT triggered), the handler fetches the existing record and returns 200, not 201.

**Gate VF-04:** All 4 checks pass. Three-tier dedup with correct status codes for every path.

---

### VF-05 — AC-6: Correlation ID End-to-End — 4 checks

**Context:** E04 evidence documents a 4-link chain: header capture → quarantine INSERT → deal identifiers → outbox event.

#### VF-05.1: X-Correlation-ID header captured (case-insensitive)
```bash
grep -n "X-Correlation-ID\|x-correlation-id" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -5 | tee "$EVIDENCE_DIR/VF-05-1.txt"
```
**PASS if:** Both `X-Correlation-ID` and `x-correlation-id` are checked (case-insensitive header handling).

#### VF-05.2: correlation_id in quarantine_items INSERT
```bash
grep -n -A30 "INSERT INTO.*quarantine_items" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep "correlation_id" | head -5 | tee "$EVIDENCE_DIR/VF-05-2.txt"
```
**PASS if:** `correlation_id` appears in both the column list and VALUES of the quarantine INSERT.

#### VF-05.3: correlation_id forwarded to deal identifiers JSON
```bash
grep -n -B3 -A15 "identifiers\|quarantine_item_id" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep "correlation_id" | head -5 | tee "$EVIDENCE_DIR/VF-05-3.txt"
```
**PASS if:** When a quarantine item is approved and a deal is created, `correlation_id` from the quarantine record is included in the deal's `identifiers` JSONB.

#### VF-05.4: Outbox INSERT uses original correlation_id with UUID fallback
```bash
grep -n "outbox_correlation\|correlation.*uuid\|uuid\.uuid4" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-05-4.txt"
```
**PASS if:** `outbox_correlation = item.get('correlation_id') or str(uuid.uuid4())` — original value preferred, fresh UUID as fallback for legacy items.

**Gate VF-05:** All 4 checks pass. Correlation chain is end-to-end with UUID fallback.

---

### VF-06 — AC-7: Shadow-Mode Isolation — 5 checks

**Context:** E05 evidence documents 4-layer isolation: backend SQL filter, dashboard dropdown, route handler forwarding, API client parameter.

#### VF-06.1: Backend GET /api/quarantine accepts source_type query param
```bash
grep -n "source_type.*Query\|Query.*source_type" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -5 | tee "$EVIDENCE_DIR/VF-06-1.txt"
```
**PASS if:** `source_type: str | None = Query(None, ...)` in the GET handler signature.

#### VF-06.2: SQL WHERE uses parameterized source_type filter
```bash
grep -n -A5 "if source_type" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "source_type\|conditions\|param_idx\|\$" | head -10 | tee "$EVIDENCE_DIR/VF-06-2.txt"
```
**PASS if:** `conditions.append(f"q.source_type = ${param_idx}")` with `params.append(source_type)` — parameterized SQL, not string interpolation.

#### VF-06.3: Dashboard dropdown has langsmith_shadow option
```bash
grep -n "langsmith_shadow" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | tee "$EVIDENCE_DIR/VF-06-3.txt"
```
**PASS if:** `<option value='langsmith_shadow'>` exists in the dropdown.

#### VF-06.4: Route handler forwards source_type to backend
```bash
grep -n "source_type\|sourceType" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts 2>&1 | tee "$EVIDENCE_DIR/VF-06-4.txt"
```
**PASS if:** `source_type` is extracted from searchParams and forwarded to the backend URL.

#### VF-06.5: API client serializes source_type into query string
```bash
grep -n -A3 "source_type" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | grep -i "searchParams\|set\|source_type" | head -5 | tee "$EVIDENCE_DIR/VF-06-5.txt"
```
**PASS if:** `searchParams.set('source_type', params.source_type)` in `getQuarantineQueue()`.

**Gate VF-06:** All 5 checks pass. Shadow-mode items can be isolated at every layer.

---

### VF-07 — AC-8: Flood Protection Active — 4 checks

**Context:** E06 evidence documents injection_rate_limiter at 120/min, invoked before any DB work.

#### VF-07.1: injection_rate_limiter at 120 requests/minute
```bash
grep -n "injection_rate_limiter" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee "$EVIDENCE_DIR/VF-07-1.txt"
```
**PASS if:** `injection_rate_limiter = RateLimiter(requests_per_minute=120)` exists.

#### VF-07.2: Rate limiter called in quarantine POST handler
```bash
grep -n "check_rate_limit.*injection\|injection_rate_limiter" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -5 | tee "$EVIDENCE_DIR/VF-07-2.txt"
```
**PASS if:** `check_rate_limit(f"quarantine:{client_ip}", limiter=injection_rate_limiter)` exists.

#### VF-07.3: Rate limit check is BEFORE source_type validation and DB operations
```bash
python3 -c "
with open('/home/zaks/zakops-backend/src/api/orchestration/main.py') as f:
    lines = f.readlines()
rate_line = None
validation_line = None
insert_line = None
for i, line in enumerate(lines, 1):
    if 'check_rate_limit' in line and 'quarantine' in line and rate_line is None:
        rate_line = i
    if 'not in VALID_SOURCE_TYPES' in line and validation_line is None:
        validation_line = i
    if 'INSERT INTO' in line and 'quarantine' in line.lower() and insert_line is None:
        insert_line = i
print(f'RATE_LIMIT_LINE={rate_line}')
print(f'VALIDATION_LINE={validation_line}')
print(f'INSERT_LINE={insert_line}')
if rate_line and validation_line and insert_line:
    if rate_line < validation_line < insert_line:
        print('ORDER=CORRECT (rate_limit → validation → INSERT)')
    else:
        print('ORDER=WRONG')
else:
    print('ORDER=UNABLE_TO_DETERMINE')
" 2>&1 | tee "$EVIDENCE_DIR/VF-07-3.txt"
```
**PASS if:** ORDER=CORRECT — rate limit is the first check, then validation, then INSERT.

#### VF-07.4: 429 response includes Retry-After header
```bash
grep -n "429\|Retry-After\|Too many" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee "$EVIDENCE_DIR/VF-07-4.txt"
```
**PASS if:** HTTPException with status_code=429 includes `Retry-After: 60` header.

**Gate VF-07:** All 4 checks pass. Flood protection is correctly ordered and complete.

---

### VF-08 — AC-9: Deal Truth from PostgreSQL — 4 checks

**Context:** E07 evidence documents that ALL deal reads in agent-api go through BackendClient → HTTP → PostgreSQL. Zero filesystem deal-state reads.

#### VF-08.1: BackendClient.get_deal() uses httpx to call backend API
```bash
grep -n -A10 "async def get_deal" /home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py 2>&1 | head -15 | tee "$EVIDENCE_DIR/VF-08-1.txt"
```
**PASS if:** Method uses `httpx.AsyncClient` to call `GET /api/deals/{deal_id}`.

#### VF-08.2: deal_tools.py uses BackendClient for ALL deal reads
```bash
grep -n "client\.get_deal\|client\.list_deals\|client\.create_deal\|client\.transition_deal" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py 2>&1 | tee "$EVIDENCE_DIR/VF-08-2.txt"
CLIENT_CALLS=$(grep -c "client\.\(get_deal\|list_deals\|create_deal\|transition_deal\)" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py 2>/dev/null) || CLIENT_CALLS=0
echo "BACKEND_CLIENT_CALLS=$CLIENT_CALLS" | tee -a "$EVIDENCE_DIR/VF-08-2.txt"
```
**PASS if:** BACKEND_CLIENT_CALLS >= 5 — all deal operations route through BackendClient.

#### VF-08.3: Zero filesystem deal-state reads in agent-api
```bash
HITS=$(grep -rn "deal_registry\|\.deal-registry\|deal_registry\.json\|DealRegistry" /home/zaks/zakops-agent-api/apps/agent-api/app/ 2>/dev/null | grep -v __pycache__ | grep -v node_modules | wc -l) || HITS=0
echo "FILESYSTEM_DEAL_READS=$HITS" | tee "$EVIDENCE_DIR/VF-08-3.txt"
grep -rn "deal_registry\|\.deal-registry\|deal_registry\.json\|DealRegistry" /home/zaks/zakops-agent-api/apps/agent-api/app/ 2>/dev/null | grep -v __pycache__ | grep -v node_modules | tee -a "$EVIDENCE_DIR/VF-08-3.txt"
```
**PASS if:** FILESYSTEM_DEAL_READS is 0 — no direct filesystem deal state access in agent-api.

#### VF-08.4: No raw httpx.get/post in deal_tools.py (must use BackendClient)
```bash
RAW_HTTPX=$(grep -c "httpx\.\|AsyncClient\|aiohttp" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py 2>/dev/null) || RAW_HTTPX=0
echo "RAW_HTTPX_IN_DEAL_TOOLS=$RAW_HTTPX" | tee "$EVIDENCE_DIR/VF-08-4.txt"
```
**PASS if:** RAW_HTTPX_IN_DEAL_TOOLS is 0 — all HTTP goes through BackendClient, not raw httpx calls.

**Gate VF-08:** All 4 checks pass. Deal truth flows exclusively through BackendClient → Backend → PostgreSQL.

---

### VF-09 — AC-10: No Regressions — 3 checks

**Context:** Completion report claims `make validate-local` and `npx tsc --noEmit` both pass.

#### VF-09.1: `make validate-local` passes
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tail -5 | tee "$EVIDENCE_DIR/VF-09-1.txt"
echo "EXIT:$?" | tee -a "$EVIDENCE_DIR/VF-09-1.txt"
```
**PASS if:** Exit 0, "All local validations passed".

#### VF-09.2: `npx tsc --noEmit` passes
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee "$EVIDENCE_DIR/VF-09-2.txt"
echo "EXIT:$?" | tee -a "$EVIDENCE_DIR/VF-09-2.txt"
```
**PASS if:** Exit 0, zero errors.

#### VF-09.3: No new ESLint errors in modified files
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx eslint src/app/quarantine/page.tsx --no-error-on-unmatched-pattern 2>&1 | tee "$EVIDENCE_DIR/VF-09-3.txt"
echo "EXIT:$?" | tee -a "$EVIDENCE_DIR/VF-09-3.txt"
```
**PASS if:** Exit 0 or only pre-existing warnings (no new errors introduced by the mission).

**Gate VF-09:** All 3 checks pass. No regressions.

---

### VF-10 — AC-11: Bookkeeping — 2 checks

**Context:** Completion report claims CHANGES.md was updated.

#### VF-10.1: CHANGES.md contains entry for this mission
```bash
grep -n "LANGSMITH-SHADOW-PILOT\|shadow.*pilot\|source_type.*drift\|VALID_SOURCE_TYPES\|startup.*warning.*gate" /home/zaks/bookkeeping/CHANGES.md 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-10-1.txt"
HITS=$(grep -c "LANGSMITH-SHADOW-PILOT\|shadow.*pilot" /home/zaks/bookkeeping/CHANGES.md 2>/dev/null) || HITS=0
echo "CHANGES_ENTRIES=$HITS" | tee -a "$EVIDENCE_DIR/VF-10-1.txt"
```
**PASS if:** CHANGES_ENTRIES >= 1.

#### VF-10.2: Completion report exists and lists 11 AC
```bash
test -f "/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md" && echo "EXISTS" || echo "MISSING"
AC_COUNT=$(grep -c "| AC-" /home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md 2>/dev/null) || AC_COUNT=0
echo "AC_COUNT=$AC_COUNT" | tee "$EVIDENCE_DIR/VF-10-2.txt"
grep "Status:.*COMPLETE\|11/11" /home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-READY-001.COMPLETION.md 2>&1 | tee -a "$EVIDENCE_DIR/VF-10-2.txt"
```
**PASS if:** File exists, AC_COUNT is 11, status is COMPLETE.

**Gate VF-10:** Both checks pass. Bookkeeping is complete.

---

### VF-11 — INJECTION-CONTRACT.md Updated — 3 checks

**Context:** Completion report claims the contract was updated with 400 response code for unknown source_type and the langsmith_production → langsmith_live fix.

#### VF-11.1: 400 response code documented
```bash
grep -n "400\|Bad Request\|unrecognized.*source_type\|VALID_SOURCE_TYPES" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-11-1.txt"
```
**PASS if:** 400 response is documented with description mentioning source_type validation.

#### VF-11.2: All 5 source types listed correctly
```bash
grep -n "email_sync\|langsmith_shadow\|langsmith_live\|manual\|email" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-11-2.txt"
# Verify no langsmith_production in contract
LP_HITS=$(grep -c "langsmith_production" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>/dev/null) || LP_HITS=0
echo "LANGSMITH_PRODUCTION_IN_CONTRACT=$LP_HITS" | tee -a "$EVIDENCE_DIR/VF-11-2.txt"
```
**PASS if:** All 5 canonical values present AND LANGSMITH_PRODUCTION_IN_CONTRACT is 0.

#### VF-11.3: Canonical Truth section preserved
```bash
grep -n "Canonical Truth\|canonical.*truth\|PostgreSQL" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee "$EVIDENCE_DIR/VF-11-3.txt"
```
**PASS if:** "Canonical Truth" section exists (this section was accidentally deleted during a prior QA run and restored).

**Gate VF-11:** All 3 checks pass. Contract documentation is accurate and complete.

---

## 4. Cross-Consistency Checks

### XC-1: VALID_SOURCE_TYPES Matches Contract Source Types
```bash
echo "=== Code constant ===" | tee "$EVIDENCE_DIR/XC-1.txt"
grep "VALID_SOURCE_TYPES" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -1 | tee -a "$EVIDENCE_DIR/XC-1.txt"
echo "=== Contract source types ===" | tee -a "$EVIDENCE_DIR/XC-1.txt"
grep "email_sync\|langsmith_shadow\|langsmith_live\|manual" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/XC-1.txt"
```
**PASS if:** Every value in `VALID_SOURCE_TYPES` appears in the contract, and the contract does not list values absent from the constant.

### XC-2: Dashboard Dropdown Options Match VALID_SOURCE_TYPES
```bash
echo "=== Code constant ===" | tee "$EVIDENCE_DIR/XC-2.txt"
grep "VALID_SOURCE_TYPES" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -1 | tee -a "$EVIDENCE_DIR/XC-2.txt"
echo "=== Dashboard dropdown ===" | tee -a "$EVIDENCE_DIR/XC-2.txt"
grep "option.*value=" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | tee -a "$EVIDENCE_DIR/XC-2.txt"
```
**PASS if:** Dashboard dropdown values are a subset of VALID_SOURCE_TYPES (dashboard may omit `email` since it's the legacy default). No dropdown option should be a value that VALID_SOURCE_TYPES would reject.

### XC-3: Contract Response Codes Match Code (Updated for 400)
```bash
echo "=== Contract codes ===" | tee "$EVIDENCE_DIR/XC-3.txt"
grep -E "^\| \*\*[0-9]{3}" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | tee -a "$EVIDENCE_DIR/XC-3.txt"
echo "=== Code: 400 for bad source_type ===" | tee -a "$EVIDENCE_DIR/XC-3.txt"
grep -n "status_code.*400\|JSONResponse.*400" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -5 | tee -a "$EVIDENCE_DIR/XC-3.txt"
echo "=== Code: 503 fail-closed ===" | tee -a "$EVIDENCE_DIR/XC-3.txt"
grep -n "503" /home/zaks/zakops-backend/src/api/shared/middleware/apikey.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-3.txt"
echo "=== Code: 429 rate limit ===" | tee -a "$EVIDENCE_DIR/XC-3.txt"
grep -n "429" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-3.txt"
```
**PASS if:** All documented response codes (200, 201, 400, 401, 429, 503) have matching code paths.

### XC-4: E01 Line Numbers Still Accurate
```bash
echo "=== E01 claims main.py:272 has langsmith_live ===" | tee "$EVIDENCE_DIR/XC-4.txt"
sed -n '270,280p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-4.txt"
echo "=== E01 claims main.py:277 has VALID_SOURCE_TYPES ===" | tee -a "$EVIDENCE_DIR/XC-4.txt"
sed -n '275,280p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-4.txt"
echo "=== E01 claims page.tsx:327 has langsmith_live option ===" | tee -a "$EVIDENCE_DIR/XC-4.txt"
sed -n '325,330p' /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | tee -a "$EVIDENCE_DIR/XC-4.txt"
```
**PASS if:** Line numbers in E01 evidence match the actual source code. If lines have shifted (due to other changes), classify as INFO (not FAIL).

### XC-5: E02 Startup Gate Line Numbers Still Accurate
```bash
echo "=== E02 claims startup gate at lines 428-439 ===" | tee "$EVIDENCE_DIR/XC-5.txt"
sed -n '425,445p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-5.txt"
```
**PASS if:** Lines 428-439 contain the LAYER 2 ZAKOPS_API_KEY startup check. If shifted, classify as INFO.

---

## 5. Stress Tests

### ST-1: Empty String source_type Handling
```bash
# Check: what happens if source_type is empty string (not None)?
grep -n -A20 "source_type.*=.*item\.\|X-Source-Type" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -25 | tee "$EVIDENCE_DIR/ST-1.txt"
echo "=== Does 'or' chain handle empty string? ===" | tee -a "$EVIDENCE_DIR/ST-1.txt"
python3 -c "
# Simulate the resolution logic
source_type = '' or None or 'email'
print(f'empty string result: {source_type}')
# Empty string is falsy in Python, so 'or' chain works correctly
print('VERDICT: PASS — empty string falls through to default')
" 2>&1 | tee -a "$EVIDENCE_DIR/ST-1.txt"
```
**PASS if:** Empty string source_type falls through to default `"email"` via the `or` chain.

### ST-2: VALID_SOURCE_TYPES Is a Set (Not a List)
```bash
grep "VALID_SOURCE_TYPES\s*=" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/ST-2.txt"
python3 -c "
line = open('/home/zaks/zakops-backend/src/api/orchestration/main.py').read()
if 'VALID_SOURCE_TYPES = {' in line and 'VALID_SOURCE_TYPES = [' not in line:
    print('TYPE=set (O(1) lookup)')
    print('VERDICT: PASS')
else:
    print('TYPE=list or tuple (O(n) lookup)')
    print('VERDICT: INFO — works but suboptimal')
" 2>&1 | tee -a "$EVIDENCE_DIR/ST-2.txt"
```
**PASS if:** `VALID_SOURCE_TYPES` is a set `{...}` not a list `[...]`. Sets provide O(1) membership testing.

### ST-3: source_type Validation Is Case-Sensitive
```bash
echo "=== Case sensitivity check ===" | tee "$EVIDENCE_DIR/ST-3.txt"
grep -n "lower()\|upper()\|casefold()\|case.*insensitive" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "source_type" | tee -a "$EVIDENCE_DIR/ST-3.txt"
echo "=== Verdict ===" | tee -a "$EVIDENCE_DIR/ST-3.txt"
CASE_NORMALIZE=$(grep -c "source_type.*lower()\|source_type.*casefold()" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>/dev/null) || CASE_NORMALIZE=0
echo "CASE_NORMALIZATION_CALLS=$CASE_NORMALIZE" | tee -a "$EVIDENCE_DIR/ST-3.txt"
if [ "$CASE_NORMALIZE" -eq 0 ]; then
  echo "VERDICT: INFO — source_type is case-sensitive. 'Langsmith_Shadow' would be rejected. This is acceptable behavior (callers should use exact values) but worth documenting."
else
  echo "VERDICT: PASS — source_type is normalized before validation."
fi | tee -a "$EVIDENCE_DIR/ST-3.txt"
```
**INFO or PASS:** Document whether validation is case-sensitive. Both are acceptable as long as behavior is consistent.

### ST-4: No Promise.all in Dashboard Quarantine (Surface 9)
```bash
PA_COUNT=$(grep -c "Promise\.all[^S]" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null) || PA_COUNT=0
echo "PROMISE_ALL_COUNT=$PA_COUNT" | tee "$EVIDENCE_DIR/ST-4.txt"
echo "VERDICT: $([ $PA_COUNT -eq 0 ] && echo 'PASS' || echo 'FAIL')" | tee -a "$EVIDENCE_DIR/ST-4.txt"
```
**PASS if:** PA_COUNT is 0.

### ST-5: No console.error in Dashboard Quarantine (Surface 9)
```bash
CE_COUNT=$(grep -c "console\.error" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null) || CE_COUNT=0
echo "CONSOLE_ERROR_COUNT=$CE_COUNT" | tee "$EVIDENCE_DIR/ST-5.txt"
echo "VERDICT: $([ $CE_COUNT -eq 0 ] && echo 'PASS' || echo 'FAIL')" | tee -a "$EVIDENCE_DIR/ST-5.txt"
```
**PASS if:** CE_COUNT is 0.

### ST-6: 'use client' Directive Present (Surface 9)
```bash
FIRST_LINE=$(head -1 /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null)
echo "FIRST_LINE=$FIRST_LINE" | tee "$EVIDENCE_DIR/ST-6.txt"
echo "VERDICT: $(echo "$FIRST_LINE" | grep -q "use client" && echo 'PASS' || echo 'FAIL')" | tee -a "$EVIDENCE_DIR/ST-6.txt"
```
**PASS if:** First line is `'use client'`.

---

## 6. Remediation Protocol

When a gate returns FAIL:

1. **Read the evidence file** — understand the exact failure
2. **Classify the failure:**
   - `MISSING_FIX` — Claimed fix was not applied
   - `REGRESSION` — A prior fix was reverted or broken
   - `RESIDUAL_ARTIFACT` — Stale code from before the mission that should have been cleaned
   - `DRIFT` — source_type naming drift survives in a location not checked by the mission
   - `WIRING_GAP` — Feature exists but is not connected to the right code path
   - `FALSE_POSITIVE` — Gate logic is wrong, code is correct
   - `SCOPE_GAP` — Issue exists outside the mission's declared scope
3. **Apply minimal fix** following existing patterns
4. **Re-run the specific gate** — capture new evidence
5. **Re-run `make validate-local`** — ensure no regression
6. **Record in completion report** with before/after evidence paths

---

## 7. Enhancement Opportunities

### ENH-1: Database Migration for Existing `langsmith_production` Rows
The completion report's follow-up item #1: any quarantine_items rows stored with `langsmith_production` before the drift fix remain unchanged. A future `UPDATE ... SET source_type = 'langsmith_live' WHERE source_type = 'langsmith_production'` migration would clean these.

### ENH-2: source_type Validation in Dashboard (Client-Side)
Currently validation is server-side only. Adding client-side validation in the dashboard (before the API call) would provide faster feedback and reduce 400 responses.

### ENH-3: Pydantic Enum for source_type
Replace the string comparison with a Pydantic `Literal` or `Enum` type on the `QuarantineCreate` model. This would move validation from manual code to model validation.

### ENH-4: Integration Test for 400 Rejection of Unknown source_type
Add a test that sends `source_type=unknown_value` and asserts a 400 response with the `valid_values` list.

### ENH-5: Structured Logging for source_type Validation Failures
Log rejected source_type values with caller IP for detecting misconfigured integrations.

### ENH-6: Health Endpoint Should Report api_key_configured State
Since `app.state.api_key_configured` is set at startup, the `/health` endpoint could expose this (without revealing the key) so monitoring can detect misconfigured deployments.

### ENH-7: Rate Limiter Observability Endpoint
Add a `/api/admin/rate-limits` endpoint showing current rate limiter state per key (remaining requests, window reset time).

---

## 8. Scorecard Template

```
QA-LANGSMITH-SHADOW-PILOT-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: Claude Code (Opus 4.6)

Pre-Flight:
  PF-1 (validate-local):          [ PASS / FAIL ]
  PF-2 (TypeScript):              [ PASS / FAIL ]
  PF-3 (Backend health):          [ PASS / FAIL / SKIP ]
  PF-4 (Source artifacts):        [ PASS / FAIL ]
  PF-5 (Evidence dir):            [ PASS / FAIL ]

Verification Families:
  VF-01 (Drift eliminated):       __ / 6  checks PASS
  VF-02 (VALID_SOURCE_TYPES):     __ / 5  checks PASS
  VF-03 (Startup gate):           __ / 4  checks PASS
  VF-04 (201/200 measurement):    __ / 4  checks PASS
  VF-05 (Correlation chain):      __ / 4  checks PASS
  VF-06 (Shadow isolation):       __ / 5  checks PASS
  VF-07 (Flood protection):       __ / 4  checks PASS
  VF-08 (Deal truth):             __ / 4  checks PASS
  VF-09 (No regressions):         __ / 3  checks PASS
  VF-10 (Bookkeeping):            __ / 2  checks PASS
  VF-11 (Contract updated):       __ / 3  checks PASS

Cross-Consistency:
  XC-1 (Constant vs contract):    [ PASS / FAIL ]
  XC-2 (Constant vs dropdown):    [ PASS / FAIL ]
  XC-3 (Response codes):          [ PASS / FAIL ]
  XC-4 (E01 line numbers):        [ PASS / FAIL / INFO ]
  XC-5 (E02 line numbers):        [ PASS / FAIL / INFO ]

Stress Tests:
  ST-1 (Empty string handling):   [ PASS / FAIL ]
  ST-2 (Set vs list):             [ PASS / FAIL ]
  ST-3 (Case sensitivity):        [ PASS / INFO ]
  ST-4 (Promise.all ban):         [ PASS / FAIL ]
  ST-5 (console.error ban):       [ PASS / FAIL ]
  ST-6 ('use client'):            [ PASS / FAIL ]

Summary:
  Total gates:          __ / 75
  PASS:                 __
  FAIL:                 __
  INFO:                 __
  SKIP:                 __

  Remediations Applied: __
  Enhancement Opportunities: 7 (ENH-1 through ENH-7)

  Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **QA only** — Do not build new features. If a gate reveals a gap, classify and fix minimally.
2. **Remediate, don't redesign** — Fixes must follow existing patterns.
3. **Evidence-based** — Every PASS needs tee'd output in `$EVIDENCE_DIR`.
4. **Services-down accommodation** — If PF-3 fails, live gates become SKIP(services-down).
5. **Surface 9 compliance** — Dashboard checks include `'use client'`, `console.warn`, `Promise.allSettled`.
6. **Generated files are read-only** — Do not modify `api-types.generated.ts` or `backend_models.py`.
7. **WSL safety** — Strip CRLF and fix ownership on any new files.
8. **Record all changes** in `/home/zaks/bookkeeping/CHANGES.md`.
9. **Preserve prior fixes** — Remediation must not revert LANGSMITH-INTAKE-HARDEN-001 or LANGSMITH-SHADOW-PILOT-READY-001 changes.

---

## 10. Stop Condition

Stop when:
- All 75 verification gates pass, are justified (SKIP/INFO), or are remediated (FAIL → fix → re-gate → PASS)
- All remediations are applied and re-verified
- `make validate-local` passes as final check
- The scorecard is complete with evidence paths for every gate
- All changes recorded in CHANGES.md

Do NOT proceed to: LangSmith shadow-mode pilot execution, database migration for existing rows, or Pydantic enum refactoring. Those are out of scope.

---

*End of QA Mission Prompt — QA-LANGSMITH-SHADOW-PILOT-VERIFY-001*
