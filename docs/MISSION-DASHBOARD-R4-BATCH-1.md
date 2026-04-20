# CLAUDE CODE MISSION: DASHBOARD ROUND 4 — BATCH 1: ROUTING + MISSING ENDPOINTS
## Mission ID: DASHBOARD-R4-BATCH-1
## Codename: "Route Marshal"
## Priority: P0
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Build everything, verify everything

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   EXECUTION DIRECTIVE                                                        ║
║                                                                              ║
║   This batch fixes fatal routing and missing endpoint gaps:                  ║
║   - /deals/new and /deals/GLOBAL slug guard                                  ║
║   - Create Deal endpoint wiring                                              ║
║   - Quarantine delete endpoint                                                ║
║   - Actions bulk delete backend                                               ║
║                                                                              ║
║   If these fail, the dashboard cannot create, delete, or navigate deals.     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## CONTEXT
- Depends on Batch 0 (auth + Playwright) being complete.
- Uses evidence structure defined in the batch plan.
- Primary source: /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md

---

## SECTION 0: PREFLIGHT VERIFICATION
Evidence directory:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-1/evidence/`

```bash
BASE_EVIDENCE=/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-1/evidence
mkdir -p "$BASE_EVIDENCE/preflight" "$BASE_EVIDENCE/rec-001" "$BASE_EVIDENCE/rec-002" "$BASE_EVIDENCE/rec-003" "$BASE_EVIDENCE/rec-004" "$BASE_EVIDENCE/playwright"

# Health checks
curl -s http://localhost:8091/health | tee "$BASE_EVIDENCE/preflight/01-backend-health.json"
curl -s http://localhost:8095/health | tee "$BASE_EVIDENCE/preflight/02-agent-health.json"

# Confirm Batch 0 auth key exists
rg -n "ZAKOPS_API_KEY" /home/zaks/zakops-agent-api/apps/dashboard/.env.local | tee "$BASE_EVIDENCE/preflight/03-api-key-present.txt"

# Confirm dashboard is up
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003 | tee "$BASE_EVIDENCE/preflight/04-dashboard-status.txt"
```

If preflight fails (health down), fix before proceeding.

---

## FIX 1 (P0): REC-001 — Deal Routing Slug Guard + /deals/new
**Source text (verbatim):** “Create `/deals/new/page.tsx` AND add slug guard in `[id]` for GLOBAL, edit, bulk”

### Step 1A: Add /deals/new page
Create file: `apps/dashboard/src/app/deals/new/page.tsx`
- Build a simple form with at least `canonical_name` and optional `display_name`, `stage`, `status`.
- On submit, call a new `createDeal` API function (see Step 1B).
- On success, navigate to `/deals/{deal_id}`.

### Step 1B: Add createDeal API function
File: `apps/dashboard/src/lib/api.ts`
- Add `createDeal` that POSTs to `/api/deals` with required fields.
- Ensure response is parsed as `Deal` or `DealDetail` (depending on existing schema).

### Step 1C: Add slug guard to /deals/[id]
File: `apps/dashboard/src/app/deals/[id]/page.tsx`
- Guard reserved slugs: `new`, `GLOBAL`, `edit`, `bulk` (case-insensitive).
- If slug is reserved, render a clean 404 page or redirect to `/deals`.
- Validate IDs: allow `DL-` pattern or UUID. If invalid, render 404.

### Verification
```bash
# /deals/new should render create form (not crash)
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003/deals/new | tee "$BASE_EVIDENCE/rec-001/01-deals-new-status.txt"

# /deals/GLOBAL should not crash or fetch /api/deals/GLOBAL
curl -s http://localhost:3003/deals/GLOBAL | tee "$BASE_EVIDENCE/rec-001/02-deals-global.html"
```

```
GATE 1:
- /deals/new returns 200 and shows create form
- /deals/GLOBAL does not show “Failed to load deal” and does not call /api/deals/GLOBAL
```

---

## FIX 2 (P0): REC-002 — POST /api/deals (Create Deal)
**Source text (verbatim):** “Implement `POST /api/deals` with schema `{canonical_name, broker, ...}`”

### Step 2A: Confirm backend endpoint exists
Backend: `/home/zaks/zakops-backend/src/api/orchestration/main.py`
- Endpoint already exists: `@app.post("/api/deals")`.
- If missing, implement per backend `DealCreate` model.

### Step 2B: Ensure request goes through proxy with auth
- /api/deals has no Next route; it should pass through middleware with X-API-Key.
- Ensure middleware handles POST correctly (Batch 0).

### Verification
```bash
curl -i -X POST http://localhost:8091/api/deals \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"canonical_name":"Test Deal R4","stage":"inbound","status":"active"}' | tee "$BASE_EVIDENCE/rec-002/01-create-deal.txt"
```

```
GATE 2:
- POST /api/deals returns 201 with deal_id
- UI create form successfully creates a deal and navigates to detail page
```

---

## FIX 3 (P0): REC-003 — Quarantine Delete Endpoint + Proxy
**Source text (verbatim):** “Implement `POST /api/quarantine/{id}/delete` in backend + Next proxy”

### Step 3A: Implement backend endpoint
Backend repo: `/home/zaks/zakops-backend/src/api/orchestration/main.py`
- Add `POST /api/quarantine/{item_id}/delete`
- Soft delete preferred: set `hidden_from_quarantine = 1`, set `quarantine_hidden_at`, `quarantine_hidden_by`.
- Return `{status:"deleted", item_id}`.

### Step 3B: Add Next route
Create: `apps/dashboard/src/app/api/quarantine/[id]/delete/route.ts`
- Proxy POST to backend `/api/quarantine/{id}/delete` with backendHeaders().

### Verification
```bash
# Find a quarantine item
psql -U zakops -d zakops -c "SELECT id FROM zakops.quarantine_items LIMIT 1;" | tee "$BASE_EVIDENCE/rec-003/01-quarantine-id.txt"

export QID=<ITEM_ID>

curl -i -X POST http://localhost:8091/api/quarantine/$QID/delete \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" | tee "$BASE_EVIDENCE/rec-003/02-delete.txt"
```

```
GATE 3:
- POST /api/quarantine/{id}/delete returns 200
- Quarantine item no longer appears in /api/quarantine list
```

---

## FIX 4 (P0): REC-004 — Actions Bulk Delete
**Source text (verbatim):** “Update bulk delete proxy to correct backend path `/api/kinetic/actions/bulk/delete` OR implement endpoint”

### Step 4A: Implement backend endpoint
Backend repo: `/home/zaks/zakops-backend/src/api/orchestration/main.py`
- Add `POST /api/actions/bulk/delete` accepting `{action_ids: []}`.
- Return `{success, deleted_count, deleted_ids}`.
- Update OpenAPI.

### Step 4B: Align Next route
Next route exists: `apps/dashboard/src/app/api/actions/bulk/delete/route.ts`.
- Ensure it targets `/api/actions/bulk/delete` (not /api/kinetic/*).

### Verification
```bash
# Get sample action ids
psql -U zakops -d zakops -c "SELECT action_id FROM zakops.actions LIMIT 2;" | tee "$BASE_EVIDENCE/rec-004/01-action-ids.txt"

export ACTION_IDS='["<ACTION_ID_1>","<ACTION_ID_2>"]'

curl -i -X POST http://localhost:8091/api/actions/bulk/delete \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action_ids":'$ACTION_IDS'}' | tee "$BASE_EVIDENCE/rec-004/02-bulk-delete.txt"
```

```
GATE 4:
- Bulk delete returns 200
- deleted_count matches input length
```

---

## PLAYWRIGHT VERIFICATION (REQUIRED)
Create a Playwright test for routing guard + deal create.
Path: `apps/dashboard/tests/e2e/deal-routing-create.spec.ts`

Test steps:
1. Navigate to `/deals/new`, fill form, submit.
2. Verify redirect to `/deals/{deal_id}`.
3. Navigate to `/deals/GLOBAL` and ensure no crash (404 or redirect).

Run:
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard
npx playwright test tests/e2e/deal-routing-create.spec.ts | tee "$BASE_EVIDENCE/playwright/01-deal-routing-create.txt"
```

```
GATE 5:
- Playwright test passes
```

---

## VERIFICATION SEQUENCE
```bash
# Gate 1
cat "$BASE_EVIDENCE/rec-001/01-deals-new-status.txt"
cat "$BASE_EVIDENCE/rec-001/02-deals-global.html"
# Gate 2
cat "$BASE_EVIDENCE/rec-002/01-create-deal.txt"
# Gate 3
cat "$BASE_EVIDENCE/rec-003/02-delete.txt"
# Gate 4
cat "$BASE_EVIDENCE/rec-004/02-bulk-delete.txt"
# Gate 5
cat "$BASE_EVIDENCE/playwright/01-deal-routing-create.txt"
```

---

## AUTONOMY RULES
- If a backend endpoint is missing, implement it.
- If OpenAPI lacks a path, update and regenerate.
- If something fails, document BLOCKER and continue with other fixes.

---

## OUTPUT FORMAT
Save completion report:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-1/completion-report.md`

Template:
```
# DASHBOARD-R4 BATCH 1 — COMPLETION REPORT

## Summary
| Fix | Status | Evidence |
|-----|--------|----------|
| REC-001 Routing + /deals/new | PASS/FAIL | path(s) |
| REC-002 Create deal | PASS/FAIL | path(s) |
| REC-003 Quarantine delete | PASS/FAIL | path(s) |
| REC-004 Actions bulk delete | PASS/FAIL | path(s) |
| Playwright test | PASS/FAIL | path(s) |

## Gates
| Gate | Result | Evidence |
|------|--------|----------|
| Gate 1 | PASS/FAIL | rec-001/01-deals-new-status.txt |
| Gate 2 | PASS/FAIL | rec-002/01-create-deal.txt |
| Gate 3 | PASS/FAIL | rec-003/02-delete.txt |
| Gate 4 | PASS/FAIL | rec-004/02-bulk-delete.txt |
| Gate 5 | PASS/FAIL | playwright/01-deal-routing-create.txt |

## Blockers
- ...

## Notes
- ...
```

---

## HARD RULES
- No mock fallbacks for endpoints in this batch unless explicitly documented.
- All new backend endpoints must appear in OpenAPI.
- All write endpoints must require X-API-Key.
