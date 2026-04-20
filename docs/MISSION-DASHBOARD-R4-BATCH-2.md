# CLAUDE CODE MISSION: DASHBOARD ROUND 4 — BATCH 2: ACTIONS + QUARANTINE CLUSTER
## Mission ID: DASHBOARD-R4-BATCH-2
## Codename: "Triage Forge"
## Priority: P1
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Build everything, verify everything

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   EXECUTION DIRECTIVE                                                        ║
║                                                                              ║
║   This batch stabilizes Quarantine + Actions workflows:                       ║
║   approve/reject wiring, preview correctness, clear-completed actions,       ║
║   actions execute, capabilities 501, and the actions count UI bug.           ║
║                                                                              ║
║   Zero 405/501. Zero dead actions.                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## CONTEXT
- Depends on Batch 0 (auth + Playwright) and Batch 1 (routing + create + delete + bulk delete).
- If Batch 0/1 are not complete, fix blockers or log them and continue on non-blocked items.
- Primary source: /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md

---

## SECTION 0: PREFLIGHT VERIFICATION
Evidence directory:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-2/evidence/`

```bash
BASE_EVIDENCE=/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-2/evidence
mkdir -p "$BASE_EVIDENCE/preflight" "$BASE_EVIDENCE/rec-009" "$BASE_EVIDENCE/rec-010" \
  "$BASE_EVIDENCE/rec-011" "$BASE_EVIDENCE/rec-012" "$BASE_EVIDENCE/rec-019" "$BASE_EVIDENCE/dl-042" "$BASE_EVIDENCE/playwright"

# Service health
curl -s http://localhost:8091/health | tee "$BASE_EVIDENCE/preflight/01-backend-health.json"
curl -s http://localhost:8095/health | tee "$BASE_EVIDENCE/preflight/02-agent-health.json"

# Confirm Batch 0 auth key exists
rg -n "ZAKOPS_API_KEY" /home/zaks/zakops-agent-api/apps/dashboard/.env.local | tee "$BASE_EVIDENCE/preflight/03-api-key-present.txt"

# Confirm Batch 1 endpoints if already completed
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003/deals/new | tee "$BASE_EVIDENCE/preflight/04-deals-new-status.txt"
```

If preflight fails (health down), fix before proceeding.

---

## FIX 1 (P1): REC-009 — Wire Quarantine Approve/Reject to `/api/quarantine/{id}/process`
**Source text (verbatim):** “Wire approve/reject to `/api/quarantine/{id}/process` or implement execute endpoints”

### Step 1A: Confirm backend contract
Backend source of truth (FastAPI):
- File: `/home/zaks/zakops-backend/src/api/orchestration/main.py`
- Endpoint: `POST /api/quarantine/{item_id}/process`
- Payload schema: `QuarantineProcess` (fields: `action`, `processed_by`, `deal_id?`, `notes?`)

Verify in backend OpenAPI:
```bash
curl -s http://localhost:8091/openapi.json | jq '.paths["/api/quarantine/{item_id}/process"]' | tee "$BASE_EVIDENCE/rec-009/01-openapi-process.json"
```

### Step 1B: Update frontend approve/reject flows
Files:
- `apps/dashboard/src/lib/api.ts` — functions `approveQuarantineItem`, `rejectQuarantineItem`
- `apps/dashboard/src/app/quarantine/page.tsx` — `handleApprove`, `handleReject`

Required changes:
1. Replace action-based approval/reject (approveKineticAction/runKineticAction) with a direct POST to `/api/quarantine/{id}/process`.
2. Use **quarantine item ID** (prefer `item.id` or `item.quarantine_id`) rather than `action_id`.
3. For approval: use payload `{ action: "approve", processed_by: operatorName, deal_id?: <optional> }`.
4. For rejection: use payload `{ action: "reject", processed_by: operatorName, notes?: reason }`.
5. Handle response shape: `{status, item_id, deal_id, deal_created}`. If `deal_id` present, navigate to `/deals/{deal_id}`.

### Verification
```bash
# Pick a real quarantine ID
psql -U zakops -d zakops -c "SELECT id FROM zakops.quarantine_items WHERE status='pending' LIMIT 1;" | tee "$BASE_EVIDENCE/rec-009/02-sample-quarantine-id.txt"

# Replace <ITEM_ID>
export ITEM_ID=<ITEM_ID>

# Approve (should return 200 with deal_id or deal_created)
curl -i -X POST http://localhost:8091/api/quarantine/$ITEM_ID/process \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action":"approve","processed_by":"qa"}' | tee "$BASE_EVIDENCE/rec-009/03-approve.txt"
```

```
GATE 1:
- Approve returns 200
- Response includes status + item_id (deal_id optional)
- UI removes item from list and navigates to deal if returned
```

---

## FIX 2 (P1): REC-010 — Fix Quarantine Preview ID / Endpoint
**Source text (verbatim):** “Fix preview to use correct quarantine item ID endpoint”

### Step 2A: Audit current preview call
File: `apps/dashboard/src/lib/api.ts` → `getQuarantinePreview` currently uses `/api/actions/quarantine/{actionId}/preview`.

### Step 2B: Align preview to backend reality
Backend OpenAPI does **not** define `/api/actions/quarantine/{id}/preview`. You must align preview to a real endpoint. Options:
- **Preferred:** Use `GET /api/quarantine/{item_id}` and adapt preview UI to the available fields.
- **Alternate:** Implement new backend `GET /api/quarantine/{item_id}/preview` if preview requires message body and raw content.

If you add a new endpoint, update backend OpenAPI and ensure response matches `QuarantinePreviewSchema` (or update schema to match backend).

### Step 2C: Update frontend preview logic
- Use quarantine `id` / `quarantine_id`, not `action_id`.
- Update `QuarantinePreviewSchema` if necessary to match actual response.
- Ensure `loadPreview` in `apps/dashboard/src/app/quarantine/page.tsx` uses the same ID field.

### Verification
```bash
export ITEM_ID=<ITEM_ID>

# If using GET /api/quarantine/{id}
curl -s http://localhost:8091/api/quarantine/$ITEM_ID | tee "$BASE_EVIDENCE/rec-010/01-preview-response.json"
```

```
GATE 2:
- Preview endpoint returns 200 for real item
- UI preview panel shows subject/sender/received date (no “Preview not found”)
```

---

## FIX 3 (P1): REC-011 — Implement POST /api/actions/clear-completed
**Source text (verbatim):** “Implement `POST /api/actions/clear-completed` in backend”

### Step 3A: Add backend endpoint
Backend repo: `/home/zaks/zakops-backend/src/api/`
- Implement `POST /api/actions/clear-completed` with body `{operation: 'archive'|'delete', age: 'all'|'7d'|'30d'}`.
- Return `{success, affected_count, operation, age}`.
- Add to OpenAPI.

### Step 3B: Ensure Next route proxies correctly
Next route exists: `apps/dashboard/src/app/api/actions/clear-completed/route.ts` (already proxies). Ensure it does NOT fall back to mock when backend exists.

### Verification
```bash
curl -i -X POST http://localhost:8091/api/actions/clear-completed \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operation":"delete","age":"all"}' | tee "$BASE_EVIDENCE/rec-011/01-clear-completed.txt"
```

```
GATE 3:
- clear-completed returns 200
- affected_count is an integer
```

---

## FIX 4 (P1): REC-012 — Resolve /api/actions/capabilities 501
**Source text (verbatim):** “Resolve 501 conflict; ensure single canonical handler”

### Step 4A: Verify backend router
Backend router file exists:
`/home/zaks/zakops-backend/src/api/orchestration/routers/actions.py`
Ensure `app.include_router(actions_router)` is active and no legacy stub returns 501.

### Step 4B: Ensure dashboard calls correct path
Front-end uses `/api/actions/capabilities`.
Confirm backend supports `/api/actions/capabilities` (not `/api/kinetic/actions/*`).

### Verification
```bash
curl -i http://localhost:8091/api/actions/capabilities | tee "$BASE_EVIDENCE/rec-012/01-capabilities.txt"
```

```
GATE 4:
- /api/actions/capabilities returns 200
- JSON has `capabilities` array
```

---

## FIX 5 (P1): REC-019 — Implement POST /api/actions/{id}/execute
**Source text (verbatim):** “Implement `POST /api/actions/{id}/execute` for approved actions”

### Step 5A: Implement backend endpoint
Backend: add `POST /api/actions/{action_id}/execute`
- Should enqueue or execute the action (match existing actions runner behavior).
- Return `{status, action_id}` or existing action object.

### Step 5B: Add Next proxy route
Create Next route: `apps/dashboard/src/app/api/actions/[id]/execute/route.ts`
- Proxy POST to backend `/api/actions/{id}/execute` with backendHeaders().

### Verification
```bash
export ACTION_ID=<ACTION_ID>

curl -i -X POST http://localhost:8091/api/actions/$ACTION_ID/execute \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" | tee "$BASE_EVIDENCE/rec-019/01-execute.txt"
```

```
GATE 5:
- execute returns 200
- action status transitions to running/completed (verify via GET /api/actions/{id})
```

---

## FIX 6 (P3): DL-042 — Actions count display bug
**Source text (verbatim):** “Actions "Clear" dialog shows "0 action(s) will be deleted" even when actions exist”

### Step 6A: Identify root cause
File: `apps/dashboard/src/app/actions/page.tsx`
- The count uses `actions.filter(... completed_at ...)`.
- In API schema, `ActionSchema` does **not** include `completed_at`, so the field is missing in parsed data.

### Step 6B: Fix schema + count logic
- Add `completed_at` to `ActionSchema` in `apps/dashboard/src/lib/api.ts`.
- Ensure actions fetched include `completed_at` (verify backend response, update mapping if needed).
- Update count logic if backend uses a different field (e.g., `updated_at`).

### Verification
```bash
curl -s http://localhost:8091/api/actions | jq '.[0] | {action_id, status, completed_at}' | tee "$BASE_EVIDENCE/dl-042/01-actions-sample.json"
```

```
GATE 6:
- Clear dialog count matches the number of completed actions in API response
```

---

## PLAYWRIGHT VERIFICATION (REQUIRED)
Add a minimal Playwright test to validate quarantine approve/reject + clear completed actions.
Path: `apps/dashboard/tests/e2e/quarantine-actions.spec.ts`

Test steps:
1. Navigate to `/quarantine` and select first item (if any).
2. Click Approve or Reject and ensure UI updates (toast + item removed).
3. Navigate to `/actions`, open clear-completed dialog, ensure count > 0 when completed actions exist.

Run:
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard
npx playwright test tests/e2e/quarantine-actions.spec.ts | tee "$BASE_EVIDENCE/playwright/01-quarantine-actions.txt"
```

```
GATE 7:
- Playwright test passes
```

---

## VERIFICATION SEQUENCE
After all fixes:
```bash
# Gate 1
cat "$BASE_EVIDENCE/rec-009/03-approve.txt"
# Gate 2
cat "$BASE_EVIDENCE/rec-010/01-preview-response.json"
# Gate 3
cat "$BASE_EVIDENCE/rec-011/01-clear-completed.txt"
# Gate 4
cat "$BASE_EVIDENCE/rec-012/01-capabilities.txt"
# Gate 5
cat "$BASE_EVIDENCE/rec-019/01-execute.txt"
# Gate 6
cat "$BASE_EVIDENCE/dl-042/01-actions-sample.json"
# Gate 7
cat "$BASE_EVIDENCE/playwright/01-quarantine-actions.txt"
```

---

## AUTONOMY RULES
- If backend endpoints are missing, implement them.
- If OpenAPI lacks paths, update and regenerate.
- If a fix is too large, document as BLOCKER and continue with other fixes.
- Do not stop unless missing infrastructure prevents all fixes.

---

## OUTPUT FORMAT
Save completion report:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-2/completion-report.md`

Template:
```
# DASHBOARD-R4 BATCH 2 — COMPLETION REPORT

## Summary
| Fix | Status | Evidence |
|-----|--------|----------|
| REC-009 Quarantine approve/reject | PASS/FAIL | path(s) |
| REC-010 Quarantine preview | PASS/FAIL | path(s) |
| REC-011 Clear completed actions | PASS/FAIL | path(s) |
| REC-012 Capabilities 501 | PASS/FAIL | path(s) |
| REC-019 Actions execute | PASS/FAIL | path(s) |
| DL-042 Actions count bug | PASS/FAIL | path(s) |
| Playwright test | PASS/FAIL | path(s) |

## Gates
| Gate | Result | Evidence |
|------|--------|----------|
| Gate 1 | PASS/FAIL | rec-009/03-approve.txt |
| Gate 2 | PASS/FAIL | rec-010/01-preview-response.json |
| Gate 3 | PASS/FAIL | rec-011/01-clear-completed.txt |
| Gate 4 | PASS/FAIL | rec-012/01-capabilities.txt |
| Gate 5 | PASS/FAIL | rec-019/01-execute.txt |
| Gate 6 | PASS/FAIL | dl-042/01-actions-sample.json |
| Gate 7 | PASS/FAIL | playwright/01-quarantine-actions.txt |

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
