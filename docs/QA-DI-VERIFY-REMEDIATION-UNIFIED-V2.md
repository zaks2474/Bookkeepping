# QA VERIFICATION + REMEDIATION — DEAL-INTEGRITY-UNIFIED-001
## Codename: `QA-DI-VERIFY-UNIFIED-V2`
## Version: V2 (Residual Defects — Platform-Level Fixes) | Date: 2026-02-09
## Executor: Claude Code (Opus 4.6)
## Authority: FULL EXECUTION — Fix everything, defer nothing
## Predecessor: QA-DI-VERIFY-UNIFIED V1 (109/113 PASS, 2 PARTIAL, 2 DEFERRED)
## Input: ZakOps_Manual_Testing_Findings_V-L4.8.docx (operator manual testing)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   V2 DIRECTIVE: FINISH THE JOB                                               ║
║                                                                              ║
║   V1 achieved 109/113 PASS. Four items remain unresolved.                   ║
║   Manual operator testing found 4 additional defects.                        ║
║   This V2 addresses ONLY what is broken. Nothing else.                       ║
║                                                                              ║
║   SCOPE: 7 platform-level fixes. No retesting of passing gates.             ║
║   DEFERRALS: ZERO. Every item is fixed or the mission fails.                ║
║   APPROACH: Platform-level fixes, not page-specific patches.                ║
║                                                                              ║
║   ITEMS FROM V1:                                                             ║
║     • V-L2.4b  PARTIAL — FSM bypass paths (PATCH endpoint + retention)      ║
║     • V-L2.15  PARTIAL — Transition function not sole choke point           ║
║     • NC-3     EXPECTED-FAIL — No ESLint rule for hardcoded stage arrays    ║
║     (V-L4.8 and V-L4.10 CLEARED by manual testing — excluded from V2)      ║
║                                                                              ║
║   ITEMS FROM MANUAL TESTING:                                                 ║
║     • MT-001  Deal count discrepancy: /hq=31, /deals=30                     ║
║     • MT-002  Phantom text cursor on deals table                            ║
║     • MT-003  Intermittent Zod errors after backend shutdown                ║
║     • MT-004  Duplicate deal entries in deals table                          ║
║                                                                              ║
║   EVERY ITEM TRACES TO THE ORIGINAL SIX-LAYER MISSION.                      ║
║   EVERY FIX IS STRUCTURAL, NOT A BAND-AID.                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## VERDICT RULES

```
PASS or FAIL. Nothing else. Zero deferrals.
Every fix must:
  1. Be implemented (code changed)
  2. Be verified (gate passes with evidence)
  3. Not regress anything (make validate-local still passes)
  4. Be structural (platform-level, not page-specific patch)
```

---

## EVIDENCE STRUCTURE

```
/home/zaks/bookkeeping/qa-verifications/QA-DI-VERIFY-UNIFIED-V2/
├── evidence/
│   ├── FIX-1-fsm-bypass/
│   ├── FIX-2-count-parity/
│   ├── FIX-3-api-error-interception/
│   ├── FIX-4-phantom-cursor/
│   ├── FIX-5-duplicate-deals/
│   ├── FIX-6-eslint-stage-rule/
│   ├── regression/
│   └── FINAL/
└── completion-report.md
```

---

## PRE-FLIGHT: CONFIRM V1 PASSING GATES STILL HOLD

Before touching anything, confirm the platform is still healthy:

```bash
MONOREPO=$(git -C /home/zaks/zakops-agent-api rev-parse --show-toplevel)
BACKEND_ROOT="/home/zaks/zakops-backend"
DASHBOARD_ROOT="$MONOREPO/apps/dashboard"
QA_ROOT="/home/zaks/bookkeeping/qa-verifications/QA-DI-VERIFY-UNIFIED-V2"
mkdir -p "$QA_ROOT/evidence"/{FIX-1-fsm-bypass,FIX-2-count-parity,FIX-3-api-error-interception,FIX-4-phantom-cursor,FIX-5-duplicate-deals,FIX-6-eslint-stage-rule,regression,FINAL}

cd "$MONOREPO"
make validate-local 2>&1 | tee "$QA_ROOT/evidence/regression/validate-local-pre.log"
echo "Exit: $?" >> "$QA_ROOT/evidence/regression/validate-local-pre.log"
# STOP IF exit != 0
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 1: CLOSE ALL FSM BYPASS PATHS
# Layer: 2 (Data Model Integrity)
# V1 Gates: V-L2.4b (PARTIAL), V-L2.15 (PARTIAL)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem

Three code paths modify deal lifecycle fields (`status`, `stage`, `deleted`) without going through the centralized `transition_deal_state()` FSM function. The DB trigger (`enforce_deal_lifecycle`) auto-corrects impossible states, but this is defense-in-depth — the application layer MUST enforce the FSM too.

### Bypass Path A: PATCH /api/deals/{deal_id}
**File:** `/home/zaks/zakops-backend/src/api/orchestration/main.py` lines 655-714
**Problem:** Accepts `stage` and `status` in the `DealUpdate` model. Builds a raw `UPDATE zakops.deals SET {fields}` query. A client can send `{"stage": "archived", "status": "active"}` and the trigger will auto-correct, but the FSM is never consulted, no audit trail entry is created, and no deal_events record is written.

### Bypass Path B: Retention Cleanup
**File:** `/home/zaks/zakops-backend/src/core/retention/cleanup.py` lines 341-348
**Problem:** Raw `UPDATE zakops.deals SET deleted = TRUE, updated_at = NOW() WHERE stage = 'junk' AND ...`. Bypasses FSM — no audit trail, no deal_events, no transition validation.

### Bypass Path C: In-Memory Deal Registry
**File:** `/home/zaks/zakops-backend/src/core/deal_registry.py` lines 1029-1037, 1123-1141
**Problem:** `archive_deal()` and `mark_deal_deleted()` modify Python objects directly. This is a legacy non-database registry (JSON file based). Not connected to production API paths but creates a parallel truth.

## Fix

### Fix 1A: Strip lifecycle fields from PATCH endpoint

The `PATCH /api/deals/{deal_id}` endpoint must NOT accept `status`, `stage`, or `deleted` as updatable fields. These fields are ONLY modifiable through the FSM endpoints:
- `POST /api/deals/{deal_id}/archive` (archive)
- `POST /api/deals/{deal_id}/restore` (restore)
- `POST /api/deals/{deal_id}/transition` (stage change)

**Implementation:**
1. In `main.py`, modify the PATCH handler to explicitly exclude `status`, `stage`, and `deleted` from the `updates` dict before building the SQL query
2. If a client sends these fields, they are silently ignored (not an error — the PATCH still updates other fields like `canonical_name`, `broker`, etc.)
3. Add a comment documenting WHY these fields are excluded: "Lifecycle fields must go through transition_deal_state() FSM — see ADR-001"

**Alternative (stricter):** Return HTTP 422 if the client sends `status`, `stage`, or `deleted` in the PATCH body. This makes the contract explicit. Choose based on how the frontend currently uses PATCH.

### Fix 1B: Route retention cleanup through FSM

The retention cleanup job at `cleanup.py:341-348` must call `transition_deal_state()` instead of raw UPDATE.

**Implementation:**
1. Replace the bulk `UPDATE ... WHERE stage = 'junk'` with a loop that calls `SELECT * FROM zakops.transition_deal_state(deal_id, 'deleted', 'retention_cleanup', 'Retention policy: junk deals older than N days')` for each qualifying deal
2. This ensures: audit_trail JSONB updated, deal_events row created, FSM validation applied
3. **Performance note:** If there are many junk deals, batch the calls. The FSM function uses `SELECT ... FOR UPDATE` row locking, so each call is safe under concurrency.

### Fix 1C: Deprecate in-memory DealRegistry lifecycle methods

The `deal_registry.py` `archive_deal()` and `mark_deal_deleted()` methods must either:
- **Option A (preferred):** Be refactored to call the database FSM via an injected DB connection
- **Option B:** Be marked as deprecated with a runtime warning: `warnings.warn("Use transition_deal_state() for lifecycle changes", DeprecationWarning)` and stripped of the ability to modify `status`, `stage`, or `deleted`

If DealRegistry is truly unused in production paths, Option B is acceptable. But confirm first by searching for callers.

## Verification

```bash
FIX1_DIR="$QA_ROOT/evidence/FIX-1-fsm-bypass"

# Gate F1.1: PATCH endpoint does NOT accept status/stage/deleted
curl -sf -X PATCH "http://localhost:8091/api/deals/DL-0001" \
  -H "Content-Type: application/json" \
  -d '{"stage": "archived", "status": "active"}' 2>/dev/null \
  | python3 -m json.tool \
  | tee "$FIX1_DIR/patch_lifecycle_blocked.txt"
# Verify: stage and status are UNCHANGED in the response (still original values)
# OR: HTTP 422 returned

# Gate F1.1b: PATCH still works for non-lifecycle fields
curl -sf -X PATCH "http://localhost:8091/api/deals/DL-0001" \
  -H "Content-Type: application/json" \
  -d '{"priority": "high"}' 2>/dev/null \
  | python3 -m json.tool \
  | tee "$FIX1_DIR/patch_non_lifecycle_works.txt"
# Verify: priority updated successfully

# Gate F1.2: Retention cleanup uses FSM
grep -n "transition_deal_state" "$BACKEND_ROOT/src/core/retention/cleanup.py" 2>/dev/null \
  | tee "$FIX1_DIR/retention_uses_fsm.txt"
# Must find at least 1 reference
grep -n "UPDATE.*deals.*SET.*deleted" "$BACKEND_ROOT/src/core/retention/cleanup.py" 2>/dev/null \
  | tee "$FIX1_DIR/retention_no_raw_update.txt"
# Must be EMPTY (raw UPDATE removed)

# Gate F1.3: ZERO raw UPDATEs for lifecycle fields outside FSM
grep -rn "UPDATE.*deals.*SET.*status\|UPDATE.*deals.*SET.*stage\|UPDATE.*deals.*SET.*deleted" \
  "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  | grep -v "transition_deal_state\|migration\|alembic\|test\|025_deal_lifecycle" \
  | tee "$FIX1_DIR/raw_update_audit.txt"
echo "Bypass paths remaining: $(wc -l < "$FIX1_DIR/raw_update_audit.txt")"
# Must be 0

# Gate F1.4: DealRegistry lifecycle methods deprecated or refactored
grep -n "def archive_deal\|def mark_deal_deleted\|def restore_deal" \
  "$BACKEND_ROOT/src/core/deal_registry.py" 2>/dev/null \
  | tee "$FIX1_DIR/registry_lifecycle_methods.txt"
grep -n "DeprecationWarning\|transition_deal_state" \
  "$BACKEND_ROOT/src/core/deal_registry.py" 2>/dev/null \
  | tee "$FIX1_DIR/registry_deprecation.txt"
# Must show deprecation warnings OR FSM calls

# Gate F1.5: Backend restarts and passes health check
docker restart zakops-backend-backend-1 2>/dev/null
sleep 5
curl -sf "http://localhost:8091/health" 2>/dev/null | python3 -m json.tool \
  | tee "$FIX1_DIR/health_post_fix.txt"
```

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| F1.1 | PATCH rejects lifecycle fields | stage/status unchanged or 422 | |
| F1.1b | PATCH still works for other fields | priority updated | |
| F1.2 | Retention uses FSM | transition_deal_state found in cleanup.py | |
| F1.3 | ZERO raw lifecycle UPDATEs | 0 bypass paths | |
| F1.4 | Registry methods deprecated/refactored | warnings or FSM calls | |
| F1.5 | Backend healthy after changes | 200 OK | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 2: ELIMINATE DEAL COUNT DISCREPANCY
# Layer: 3 (Application Parity)
# Manual Testing: MT-001 (Medium)
# Original Issue: DI-ISSUE-002 remnant
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem

Operator HQ (`/hq`) displays 31 active deals. Deals page (`/deals`) displays 30 deals. The operator confirmed this is reproducible and persists across refreshes. Sometimes `/deals` shows 31, sometimes 30 — suggesting a race condition or off-by-one boundary.

### Root Cause Analysis

The two pages use **completely different data paths:**

**Path A (`/hq`):**
1. `/hq/page.tsx` calls `getPipeline()`
2. `getPipeline()` hits Next.js wrapper `/api/pipeline/route.ts`
3. The wrapper fetches BOTH `/api/pipeline/summary` (backend view) AND `/api/deals` (backend rows)
4. `total_active` is computed by **summing the `count` values from `v_pipeline_summary` view** (database aggregation)
5. Result: 31

**Path B (`/deals`):**
1. `/deals/page.tsx` calls `getDeals({status: 'active'})`
2. `getDeals()` hits backend `GET /api/deals?status=active` directly
3. Backend query: `SELECT ... FROM zakops.deals WHERE deleted = FALSE AND status = 'active' LIMIT 50 OFFSET 0`
4. Frontend displays `sortedDeals.length` (array length of returned rows)
5. Result: 30

**The discrepancy sources:**
1. **View vs rows mismatch:** `v_pipeline_summary` and `GET /api/deals` use the same WHERE clause (`deleted = FALSE AND status = 'active'`), but a row could be created/modified between the two separate API calls
2. **LIMIT 50:** The `/api/deals` endpoint has `LIMIT 50 OFFSET 0` pagination. If there are 31 active deals, it returns all 31 (under the limit). But if a deal is in a race condition (being archived while being counted), the view sum and row count can differ.
3. **Frontend counts from `sortedDeals.length`:** This is client-side array length, NOT a server-provided total

## Fix

This is a **platform-level parity fix**, not a page-specific patch. Three changes:

### Fix 2A: Add `total_count` to GET /api/deals response

The backend `GET /api/deals` endpoint must return a `total_count` field alongside the deal array. This count comes from the SAME query (same WHERE clause, same transaction) — not a separate API call.

**Implementation in `main.py`:**
1. Add a COUNT query in the same transaction as the deals listing query
2. Return response as `{"deals": [...], "total_count": N}` instead of a bare array
3. Update the `response_model` to reflect the new shape
4. Run `make update-spec && make sync-all-types` after the change

### Fix 2B: /deals page uses server-provided total_count

The `/deals/page.tsx` must display `total_count` from the API response, NOT `sortedDeals.length`.

**Implementation:**
1. Update `getDeals()` in `api.ts` to extract `total_count` from the response
2. Update `/deals/page.tsx` to display the server-provided count in the header
3. `sortedDeals.length` is still used for rendering the table rows, but the HEADER count must come from the server

### Fix 2C: /hq and /deals must use the SAME count source

After Fix 2A, both pages can use the server-provided `total_count`. The `/api/pipeline/route.ts` wrapper should use the `total_count` from the deals response rather than independently summing from the view.

**Implementation:**
1. In `/api/pipeline/route.ts`, use `total_count` from the `/api/deals` response as the authoritative total
2. The view-based stage breakdown is still useful for per-stage counts, but the TOTAL comes from the deals endpoint
3. This guarantees that `/hq` and `/deals` display the same total — they use the same number from the same source

### Fix 2D: Investigate the actual discrepancy in the database

Before implementing the fix, run a diagnostic to understand WHY the counts differ right now:

```bash
# What does the view say?
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT stage, count FROM zakops.v_pipeline_summary;"

# What does the actual table say?
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT COUNT(*) FROM zakops.deals WHERE deleted = FALSE AND status = 'active';"

# Are they different? Find the ghost deal:
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT deal_id, canonical_name, stage, status, deleted, updated_at
   FROM zakops.deals WHERE deleted = FALSE AND status = 'active'
   ORDER BY updated_at DESC;"
```

If the view count and actual count are the same (both 31), then the discrepancy is in the frontend. If they differ, there's a data issue to fix.

## Verification

```bash
FIX2_DIR="$QA_ROOT/evidence/FIX-2-count-parity"

# Gate F2.1: GET /api/deals returns total_count field
curl -sf "http://localhost:8091/api/deals?status=active" 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'total_count: {d.get(\"total_count\", \"MISSING\")}'); print(f'deals_length: {len(d.get(\"deals\", d if isinstance(d, list) else []))}')" \
  | tee "$FIX2_DIR/api_deals_total_count.txt"
# Must show total_count field (not MISSING)

# Gate F2.2: /api/pipeline total matches /api/deals total
PIPELINE_TOTAL=$(curl -sf "http://localhost:3003/api/pipeline" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_active', 'MISSING'))")
DEALS_TOTAL=$(curl -sf "http://localhost:8091/api/deals?status=active" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_count', len(d) if isinstance(d, list) else 'MISSING'))")
echo "Pipeline total: $PIPELINE_TOTAL" | tee "$FIX2_DIR/count_parity.txt"
echo "Deals total: $DEALS_TOTAL" >> "$FIX2_DIR/count_parity.txt"
echo "Match: $([ "$PIPELINE_TOTAL" = "$DEALS_TOTAL" ] && echo YES || echo NO)" >> "$FIX2_DIR/count_parity.txt"
# Must match

# Gate F2.3: /deals page shows server-provided count (not array.length)
grep -n "total_count\|totalCount\|server.*count" "$DASHBOARD_ROOT/src/app/deals/page.tsx" 2>/dev/null \
  | tee "$FIX2_DIR/deals_page_server_count.txt"
# Must show total_count usage in header
grep -n "sortedDeals\.length" "$DASHBOARD_ROOT/src/app/deals/page.tsx" 2>/dev/null \
  | tee "$FIX2_DIR/deals_page_array_length.txt"
# This should NOT be used for the header count (may still exist for table rendering — that's OK)

# Gate F2.4: Contract sync after API shape change
cd "$MONOREPO"
make sync-all-types 2>&1 | tee "$FIX2_DIR/sync_all_types.log"
echo "Exit: $?" >> "$FIX2_DIR/sync_all_types.log"
# Must exit 0

# Gate F2.5: make validate-local passes
make validate-local 2>&1 | tee "$FIX2_DIR/validate_local.log"
echo "Exit: $?" >> "$FIX2_DIR/validate_local.log"
# Must exit 0
```

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| F2.1 | API returns total_count | field present | |
| F2.2 | /hq total == /deals total | counts match | |
| F2.3 | /deals uses server count | total_count in header code | |
| F2.4 | Contract sync passes | exit 0 | |
| F2.5 | validate-local passes | exit 0 | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 3: PLATFORM-LEVEL API ERROR INTERCEPTION
# Layer: 4 (Defensive Architecture)
# Manual Testing: MT-003 (Medium)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem

When the backend is stopped, intermittent Zod validation errors appear in the browser console. The errors are inconsistent — sometimes they appear on refresh, sometimes they don't. This confuses debugging and indicates that error responses are reaching Zod schemas instead of being intercepted.

### Root Cause Analysis

The dashboard has two layers that should prevent this:

1. **`apiFetch()` in `api.ts`** (lines 397-404) — checks `response.ok` before calling `response.json()`. If the backend returns an HTTP error, it throws `ApiError` before Zod is reached. This works for HTTP errors.

2. **`Promise.allSettled`** on `/hq` and `/dashboard` — catches rejected promises and checks `status === 'fulfilled'`. This works when `apiFetch()` throws.

**But the gap is:**
- When the backend returns **valid JSON with an error shape** (e.g., `{"error": "service_unavailable"}` or `{"detail": "Internal Server Error"}`), `response.ok` may be false BUT `response.json()` succeeds
- The `ApiError` is thrown, caught by `Promise.allSettled`, and the Zod schema never sees it — **this path works**
- **The actual problem:** When the backend is **partially available** (e.g., recovering, returning incomplete responses, or returning valid JSON missing required fields), `response.ok` is TRUE, `response.json()` succeeds, but the data doesn't match the Zod schema
- The existing `.safeParse()` usage handles this gracefully (logs a debug message and falls back to partial data), but the **console output looks like errors** to the operator

Additionally, an **existing `error-normalizer.ts`** exists but is NOT wired into the fetch pipeline.

### The intermittent nature explained:
- Backend recovering: sometimes returns full data (no Zod error), sometimes partial (Zod logs validation notes)
- Caching: browser may serve stale valid response on some refreshes
- Race condition: multi-endpoint fetch where some succeed and some fail

## Fix

This is a **platform-level fix** applied to the shared API client, not individual pages.

### Fix 3A: Harden apiFetch() with response shape validation

Before returning `response.json()`, validate that the response is actually a success payload (not an error payload):

**Implementation in `api.ts` `apiFetch()`:**
1. After `response.json()`, check if the parsed data matches a known error shape: `{"error": ...}` or `{"detail": ...}` or `{"message": "...error..."}`
2. If it matches an error shape, throw `ApiError` with the error details — this prevents error payloads from reaching Zod schemas
3. Wire in the existing `error-normalizer.ts` for this check — it already handles 3 backend error shapes

### Fix 3B: Suppress Zod debug noise during degradation

The current `.safeParse()` usage logs `console.debug('[API] Deal schema validation notes:', ...)`. During backend degradation, these messages flood the console and look like errors.

**Implementation:**
1. In each API function that uses `.safeParse()`, check if the response data looks like an error payload BEFORE calling `.safeParse()`
2. If the data is `null`, `undefined`, an empty object, or has an `error`/`detail` key at the top level, skip Zod validation entirely and return the typed fallback immediately
3. This eliminates the "intermittent Zod errors" — they never fire because error payloads are caught before validation

### Fix 3C: Sequential fetch pages need the same protection

The `/deals/[id]` and `/actions` pages use sequential `await` (not `Promise.allSettled`). Each API function already has try/catch, but the pattern must be consistent:

**Implementation:**
1. Audit every API function in `api.ts` that calls `.safeParse()`
2. Ensure each follows the pattern:
   ```
   const data = await apiFetch(endpoint)
   if (!data || typeof data !== 'object' || 'error' in data || 'detail' in data) {
     return fallback  // Skip Zod, return typed empty/default
   }
   const parsed = Schema.safeParse(data)
   ```
3. This is a one-time audit, not an ongoing obligation — the pattern is established in the shared function

## Verification

```bash
FIX3_DIR="$QA_ROOT/evidence/FIX-3-api-error-interception"

# Gate F3.1: error-normalizer.ts is wired into apiFetch()
grep -n "error-normalizer\|normalizeError\|isErrorResponse\|error.*shape" \
  "$DASHBOARD_ROOT/src/lib/api.ts" 2>/dev/null \
  | tee "$FIX3_DIR/error_normalizer_wired.txt"
# Must find references

# Gate F3.2: apiFetch() checks for error payloads before returning
grep -A10 "response\.json()" "$DASHBOARD_ROOT/src/lib/api.ts" 2>/dev/null \
  | tee "$FIX3_DIR/response_shape_check.txt"
# Must show error shape check after json() parse

# Gate F3.3: Every .safeParse() call has a pre-validation guard
SAFEPPARSE_COUNT=$(grep -c "\.safeParse(" "$DASHBOARD_ROOT/src/lib/api.ts" 2>/dev/null || echo 0)
GUARD_COUNT=$(grep -c "error.*in.*data\|isErrorResponse\|typeof data" "$DASHBOARD_ROOT/src/lib/api.ts" 2>/dev/null || echo 0)
echo "safeParse calls: $SAFEPPARSE_COUNT" | tee "$FIX3_DIR/safepparse_guards.txt"
echo "Pre-validation guards: $GUARD_COUNT" >> "$FIX3_DIR/safepparse_guards.txt"
# Guard count should be >= safeParse count

# Gate F3.4: Backend down → zero Zod console errors
# Stop backend, hit each page, verify no Zod messages in console
echo "Manual verification required:" | tee "$FIX3_DIR/backend_down_zod.txt"
echo "1. docker stop zakops-backend-backend-1" >> "$FIX3_DIR/backend_down_zod.txt"
echo "2. Open browser console, navigate to /hq, /dashboard, /deals, /actions" >> "$FIX3_DIR/backend_down_zod.txt"
echo "3. Verify: zero Zod-related messages in console" >> "$FIX3_DIR/backend_down_zod.txt"
echo "4. docker start zakops-backend-backend-1" >> "$FIX3_DIR/backend_down_zod.txt"

# Gate F3.5: Pages still work correctly when backend is UP
# (Regression check — error interception must not break normal operation)
curl -sf "http://localhost:3003/hq" > /dev/null 2>&1 && echo "PASS: /hq loads" || echo "FAIL: /hq broken"
curl -sf "http://localhost:3003/dashboard" > /dev/null 2>&1 && echo "PASS: /dashboard loads" || echo "FAIL: /dashboard broken"
curl -sf "http://localhost:3003/deals" > /dev/null 2>&1 && echo "PASS: /deals loads" || echo "FAIL: /deals broken"
```

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| F3.1 | error-normalizer wired in | references found | |
| F3.2 | apiFetch checks error shape | guard after json() | |
| F3.3 | Every safeParse has pre-guard | guard count >= safeParse count | |
| F3.4 | Backend down → zero Zod console msgs | manual verification | |
| F3.5 | Normal operation unaffected | all pages load | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 4: ELIMINATE PHANTOM TEXT CURSOR
# Layer: 4 (Defensive Architecture — UX)
# Manual Testing: MT-002 (Low)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem

A blinking text cursor (caret) appears at random locations on the Deals page table, particularly near deal entries. The cursor does not accept input. This was documented with screenshots in the manual testing report.

### Root Cause Analysis

Investigation found no `contentEditable` attributes or stray `tabIndex` in the codebase. The deals table uses `@hello-pangea/dnd` for drag-and-drop. The most likely causes:

1. **CSS `user-select` inheritance:** Table cells may inherit `user-select: text` from a parent, causing the browser to show a text cursor when the cell is focused/clicked
2. **Drag handle focus leak:** The Kanban drag handles may capture focus and display a caret via the browser's default focus ring behavior
3. **Hidden input/textarea for clipboard or search:** Some table implementations use an off-screen input for keyboard shortcuts — if its positioning is off, the caret appears visually

## Fix

### Fix 4A: Audit and fix CSS focus states on deals table

**Implementation:**
1. Search the deals table component and its parent components for focus-related CSS
2. Add `user-select: none` to non-input table cells and row elements
3. Add `caret-color: transparent` to the table container as a safety net — this hides any stray carets without breaking actual input fields (inputs override this with their own caret-color)
4. Ensure drag handles have `outline: none` on `:focus` (or use a visible focus ring that doesn't include a caret)

### Fix 4B: Check for hidden input elements

**Implementation:**
1. Search the deals page and DealBoard component for hidden `<input>`, `<textarea>`, or elements with `contentEditable`
2. If found, ensure they are properly positioned off-screen or have `caret-color: transparent`

## Verification

```bash
FIX4_DIR="$QA_ROOT/evidence/FIX-4-phantom-cursor"

# Gate F4.1: No contentEditable on non-input elements in deals components
grep -rn "contentEditable" "$DASHBOARD_ROOT/src/" --include="*.tsx" --include="*.ts" 2>/dev/null \
  | grep -v "node_modules" \
  | tee "$FIX4_DIR/content_editable_audit.txt"

# Gate F4.2: user-select: none applied to table elements
grep -rn "user-select\|userSelect\|caret-color\|caretColor" \
  "$DASHBOARD_ROOT/src/app/deals/" "$DASHBOARD_ROOT/src/components/DealBoard*" \
  --include="*.tsx" --include="*.ts" --include="*.css" 2>/dev/null \
  | tee "$FIX4_DIR/focus_css_audit.txt"

# Gate F4.3: Manual verification — no phantom cursor
echo "Manual verification required:" | tee "$FIX4_DIR/phantom_cursor_check.txt"
echo "1. Navigate to /deals" >> "$FIX4_DIR/phantom_cursor_check.txt"
echo "2. Click on deal rows and table cells" >> "$FIX4_DIR/phantom_cursor_check.txt"
echo "3. Verify: no blinking text cursor appears outside of input fields" >> "$FIX4_DIR/phantom_cursor_check.txt"
```

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| F4.1 | No stray contentEditable | 0 matches in deals components | |
| F4.2 | user-select/caret-color applied | CSS rules found | |
| F4.3 | No phantom cursor (manual) | operator confirms | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 5: RESOLVE DUPLICATE DEAL ENTRIES
# Layer: 2 (Data Model Integrity) + Layer 3 (Application Parity)
# Manual Testing: MT-004 (Low)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem

The deals table shows duplicate entries: `DUP-FINAL-1770192031` appears twice with consecutive IDs (DL-0060 and DL-0059), both in the `screening` stage. Other test-prefixed entries exist: `SPLITBRAIN-CANARY`, `E2E-LIFECYCLE`, etc.

### Investigation Required

First, determine if this is test data or an actual duplication bug:

```bash
# Are these test artifacts from the QA process?
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT deal_id, canonical_name, stage, status, deleted, created_at
   FROM zakops.deals
   WHERE canonical_name LIKE 'DUP%' OR canonical_name LIKE 'SPLITBRAIN%' OR canonical_name LIKE 'E2E%'
   ORDER BY canonical_name, created_at;"
```

## Fix

### If test data: Fix 5A — Clean up test artifacts

**Implementation:**
1. Delete all test/canary deals that were created during the QA process
2. Document which deals were removed and why
3. Add a unique constraint or deduplication check if the creation pipeline lacks one

### If real duplication bug: Fix 5B — Fix the creation pipeline

**Implementation:**
1. Trace the deal creation path to find where duplicates can be introduced
2. Add a UNIQUE constraint on `canonical_name` (or a composite key) to prevent future duplicates at the DB level
3. Deduplicate existing entries (keep the newer one, delete the older, or merge)

## Verification

```bash
FIX5_DIR="$QA_ROOT/evidence/FIX-5-duplicate-deals"

# Gate F5.1: No duplicate canonical_names in active deals
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT canonical_name, COUNT(*) as cnt
   FROM zakops.deals WHERE deleted = FALSE
   GROUP BY canonical_name HAVING COUNT(*) > 1;" 2>/dev/null \
  | tee "$FIX5_DIR/duplicate_check.txt"
# Must return 0 rows

# Gate F5.2: Test artifacts cleaned (if applicable)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT COUNT(*) FROM zakops.deals
   WHERE canonical_name LIKE 'DUP%' OR canonical_name LIKE 'SPLITBRAIN%' OR canonical_name LIKE 'E2E%';" 2>/dev/null \
  | tee "$FIX5_DIR/test_artifacts.txt"
# Should be 0 (cleaned) or documented as intentional test data

# Gate F5.3: Deal count is consistent after cleanup
TOTAL=$(docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -t -c \
  "SELECT COUNT(*) FROM zakops.deals WHERE deleted = FALSE AND status = 'active';")
echo "Active deals after cleanup: $TOTAL" | tee "$FIX5_DIR/post_cleanup_count.txt"
```

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| F5.1 | Zero duplicate canonical_names | 0 rows returned | |
| F5.2 | Test artifacts resolved | 0 or documented | |
| F5.3 | Count consistent | matches across surfaces | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 6: ADD ESLINT RULE FOR HARDCODED STAGE ARRAYS
# Layer: 5 (Verification & Observability)
# V1 Gate: NC-3 (EXPECTED-FAIL)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem

NC-3 proved that TypeScript cannot detect a local `const PIPELINE_STAGES = [...]` array — it's valid TypeScript. Without a lint rule, a developer can reintroduce hardcoded stage lists and the CI pipeline won't catch it. The canonical stage config in `execution-contracts.ts` becomes meaningless if nothing enforces its use.

## Fix

### Fix 6A: Custom ESLint rule or restricted-syntax pattern

ESLint has a built-in `no-restricted-syntax` rule that can match AST patterns. Use it to flag variable declarations that look like hardcoded stage arrays.

**Implementation:**
1. In the dashboard's `.eslintrc.json`, add a `no-restricted-syntax` rule that matches:
   - Variable declarations named `PIPELINE_STAGES`, `STAGE_ORDER`, `STAGES`, `STAGE_COLORS`, or any `*_STAGES` / `*_STAGE_*` pattern
   - That are NOT imports from the canonical config module
2. The rule message should say: "Hardcoded stage arrays are not allowed. Import from '@/types/execution-contracts' instead."
3. Alternatively, use `eslint-plugin-import` restricted paths to require that any module importing stage-related symbols must import from the canonical config

### Fix 6B: Re-run NC-3 negative control

After the ESLint rule is in place, re-run the NC-3 sabotage test:
1. Create a temp file with `const PIPELINE_STAGES = ['prospecting', 'qualification']`
2. Run ESLint on it
3. ESLint must exit 1 (rule violation detected)
4. Delete the temp file

## Verification

```bash
FIX6_DIR="$QA_ROOT/evidence/FIX-6-eslint-stage-rule"

# Gate F6.1: ESLint rule exists in config
grep -A10 "restricted-syntax\|PIPELINE_STAGES\|STAGE_ORDER\|hardcoded.*stage" \
  "$DASHBOARD_ROOT/.eslintrc.json" "$DASHBOARD_ROOT/eslint.config.*" 2>/dev/null \
  | tee "$FIX6_DIR/eslint_rule.txt"
# Must find the restriction rule

# Gate F6.2: NC-3 RE-RUN — ESLint catches hardcoded stages
TEMP_FILE="$DASHBOARD_ROOT/src/components/qa-nc3-retest.tsx"
cat > "$TEMP_FILE" << 'EOF'
const PIPELINE_STAGES = ['prospecting', 'qualification', 'proposal'];
export default function NC3() { return <div>{PIPELINE_STAGES.join(',')}</div>; }
EOF
cd "$DASHBOARD_ROOT" && npx eslint "$TEMP_FILE" 2>&1 \
  | tee "$FIX6_DIR/nc3_rerun.txt"
NC3_EXIT=$?
rm -f "$TEMP_FILE"
echo "NC-3 re-run: eslint exit=$NC3_EXIT (expect 1 = caught)" >> "$FIX6_DIR/nc3_rerun.txt"
# Must exit 1

# Gate F6.3: Existing canonical imports still pass lint
cd "$DASHBOARD_ROOT" && npx eslint src/app/hq/page.tsx 2>&1 | tail -5 \
  | tee "$FIX6_DIR/canonical_still_passes.txt"
# Must pass (canonical imports are allowed)
```

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| F6.1 | ESLint restriction rule exists | rule in config | |
| F6.2 | NC-3 re-run: ESLint catches sabotage | exit 1 | |
| F6.3 | Canonical imports still pass lint | exit 0 | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FIX 7: CONTRACT SYNC AFTER ALL FIXES
# Layer: Cross-cutting (Constraint Q6)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Problem

Fix 2 changes the `/api/deals` response shape (adds `total_count`). This requires a full contract sync to regenerate TypeScript types and Python models.

## Fix

```bash
cd "$MONOREPO"
make update-spec        # Fetch live backend OpenAPI (requires backend running)
make sync-all-types     # Regenerate all generated files
make validate-local     # Full offline validation
```

## Verification

```bash
FIX7_DIR="$QA_ROOT/evidence/regression"

cd "$MONOREPO"
make update-spec 2>&1 | tee "$FIX7_DIR/update_spec.log"
echo "Exit: $?" >> "$FIX7_DIR/update_spec.log"

make sync-all-types 2>&1 | tee "$FIX7_DIR/sync_all_types.log"
echo "Exit: $?" >> "$FIX7_DIR/sync_all_types.log"

make validate-local 2>&1 | tee "$FIX7_DIR/validate_local_final.log"
echo "Exit: $?" >> "$FIX7_DIR/validate_local_final.log"

cd "$DASHBOARD_ROOT" && npx tsc --noEmit 2>&1 | tee "$FIX7_DIR/tsc_final.log"
echo "Exit: $?" >> "$FIX7_DIR/tsc_final.log"
```

| # | Gate | Expected | Verdict |
|---|------|----------|---------|
| F7.1 | make update-spec | exit 0 | |
| F7.2 | make sync-all-types | exit 0 | |
| F7.3 | make validate-local | exit 0 | |
| F7.4 | tsc --noEmit | exit 0 | |

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUTION ORDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
PRE-FLIGHT  ━━  Verify V1 gates still hold (make validate-local)
     ↓
FIX 1  ━━━━━━  Close FSM bypass paths (backend code changes)
     ↓
FIX 5  ━━━━━━  Resolve duplicate deals (DB investigation + cleanup)
     ↓
FIX 2  ━━━━━━  Add total_count, unify count source (backend + frontend)
     ↓
FIX 7  ━━━━━━  Contract sync (make update-spec + sync-all-types)
     ↓
FIX 3  ━━━━━━  API error interception (frontend, api.ts)
     ↓                              ┐
FIX 4  ━━━━━━  Phantom cursor fix   ├ Can run in parallel
FIX 6  ━━━━━━  ESLint stage rule    ┘
     ↓
FINAL  ━━━━━━  make validate-local + full gate verification
```

**Dependencies:**
- Fix 1 is independent (backend only)
- Fix 5 must run before Fix 2 (duplicate cleanup affects counts)
- Fix 2 changes API shape → Fix 7 (contract sync) must follow
- Fix 3, 4, 6 are independent frontend changes
- Final validation requires ALL fixes complete

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FINAL VERIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```bash
FINAL_DIR="$QA_ROOT/evidence/FINAL"

echo "=== V2 FINAL VERIFICATION ===" | tee "$FINAL_DIR/final_report.txt"

# 1. All V2 gates pass
echo "--- Gate Summary ---" >> "$FINAL_DIR/final_report.txt"
echo "FIX 1 (FSM bypass):     F1.1-F1.5  [PASS/FAIL]" >> "$FINAL_DIR/final_report.txt"
echo "FIX 2 (Count parity):   F2.1-F2.5  [PASS/FAIL]" >> "$FINAL_DIR/final_report.txt"
echo "FIX 3 (Error intercept): F3.1-F3.5  [PASS/FAIL]" >> "$FINAL_DIR/final_report.txt"
echo "FIX 4 (Phantom cursor):  F4.1-F4.3  [PASS/FAIL]" >> "$FINAL_DIR/final_report.txt"
echo "FIX 5 (Duplicates):      F5.1-F5.3  [PASS/FAIL]" >> "$FINAL_DIR/final_report.txt"
echo "FIX 6 (ESLint rule):     F6.1-F6.3  [PASS/FAIL]" >> "$FINAL_DIR/final_report.txt"
echo "FIX 7 (Contract sync):   F7.1-F7.4  [PASS/FAIL]" >> "$FINAL_DIR/final_report.txt"

# 2. V1 gates still hold (no regression)
cd "$MONOREPO"
make validate-local 2>&1 | tee "$FINAL_DIR/validate_local_final.log"
echo "Exit: $?" >> "$FINAL_DIR/validate_local_final.log"

# 3. Parity test (from V1) — re-run with both surfaces
PIPELINE_TOTAL=$(curl -sf "http://localhost:3003/api/pipeline" 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_active', 'ERR'))" 2>/dev/null)
DEALS_TOTAL=$(curl -sf "http://localhost:8091/api/deals?status=active" 2>/dev/null \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_count', len(d) if isinstance(d, list) else 'ERR'))" 2>/dev/null)
echo "Parity: Pipeline=$PIPELINE_TOTAL, Deals=$DEALS_TOTAL, Match=$([ "$PIPELINE_TOTAL" = "$DEALS_TOTAL" ] && echo YES || echo NO)" \
  | tee -a "$FINAL_DIR/final_report.txt"

# 4. Zero Zod errors under normal operation (manual confirmation)
echo "" >> "$FINAL_DIR/final_report.txt"
echo "Manual Zod check: [PASS/FAIL — operator confirms zero console errors on /hq, /dashboard, /deals, /actions]" >> "$FINAL_DIR/final_report.txt"

# 5. Backend down resilience (manual confirmation)
echo "Manual resilience: [PASS/FAIL — operator confirms graceful degradation, zero Zod errors on backend stop]" >> "$FINAL_DIR/final_report.txt"

# 6. V1 → V2 scorecard
echo "" >> "$FINAL_DIR/final_report.txt"
echo "=== V1 → V2 SCORECARD ===" >> "$FINAL_DIR/final_report.txt"
echo "V1: 109/113 PASS, 2 PARTIAL, 2 DEFERRED, 1 EXPECTED-FAIL" >> "$FINAL_DIR/final_report.txt"
echo "V2: [N]/28 gates PASS across 7 fixes" >> "$FINAL_DIR/final_report.txt"
echo "Combined: 113/113 + MT findings resolved" >> "$FINAL_DIR/final_report.txt"
echo "" >> "$FINAL_DIR/final_report.txt"
echo "VERDICT: [PASS / FAIL]" >> "$FINAL_DIR/final_report.txt"
echo "DEFERRALS: 0" >> "$FINAL_DIR/final_report.txt"
```

| Category | V1 Result | V2 Target |
|----------|-----------|-----------|
| V-L2.4b (FSM bypass) | PARTIAL | PASS (Fix 1) |
| V-L2.15 (single choke point) | PARTIAL | PASS (Fix 1) |
| V-L4.8 (Zod errors) | DEFERRED → CLEARED | PASS (confirmed by manual testing) |
| V-L4.10 (Resilience) | DEFERRED → CLEARED | PASS (confirmed by manual testing) |
| NC-3 (ESLint stage rule) | EXPECTED-FAIL | PASS (Fix 6) |
| MT-001 (Count discrepancy) | NEW | PASS (Fix 2) |
| MT-002 (Phantom cursor) | NEW | PASS (Fix 4) |
| MT-003 (Zod on backend down) | NEW | PASS (Fix 3) |
| MT-004 (Duplicate deals) | NEW | PASS (Fix 5) |

---

## PIPELINE MASTER LOG ENTRY

Upon V2 completion, append to `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_PIPELINE_MASTER_LOG.md`:

```
[TIMESTAMP] | QA-DI-VERIFY-UNIFIED-V2 COMPLETE | Agent=[agent] | RunID=[id] | STATUS=[PASS/FAIL] | 7 fixes | 28 gates | 0 deferrals | V1 PARTIAL→PASS: 2, V1 DEFERRED→CLEARED: 2, V1 NC-3→PASS: 1, MT findings: 4 resolved | Report=$QA_ROOT/evidence/FINAL/final_report.txt
```

---

**END OF QA-DI-VERIFY-REMEDIATION-UNIFIED V2**

**One sentence:** V1 proved the platform is 96.5% correct. V2 closes the remaining 3.5% and the manual testing findings — permanently, structurally, with zero deferrals.
