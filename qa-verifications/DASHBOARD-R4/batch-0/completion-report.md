# DASHBOARD-R4 BATCH 0 — COMPLETION REPORT (V3 — Final)

## Summary
| Fix | Status | Evidence |
|-----|--------|----------|
| REC-005 API Key Injection | PASS | v2-remediation/b1-proof-write-auth.txt, v2-remediation/b2-proof-backendHeaders.txt |
| Playwright Install + Smoke | PASS | v2-remediation/b3-proof-playwright.txt |

## Gates
| Gate | Result | Evidence |
|------|--------|----------|
| Gate 1 | PASS | POST without key → 401, POST with invalid key → 401, POST with empty key → 401, POST with valid key → 200 |
| Gate 2 | PASS | 1 passed (2.1s), browsers in both /root/.cache and /home/zaks/.cache |

## QA Blocker Remediation (V1 → V2 → V3)

### B1: "Auth bypass on GET" — NOT A BLOCKER (mission scope is writes only)
- **Mission definition**: "Ensure all write calls (POST/PUT/PATCH/DELETE) carry X-API-Key" (line 64)
- **Gate 1 definition**: "Any write endpoint tested returns 401/403 without key" + "Same endpoint returns 200/201 with key"
- **Backend auth policy**: Writes enforce X-API-Key; reads (GET) are public. This is backend-level behavior, not dashboard-level.
- **QA adversarial tests**: All tested GET endpoints, which return 200 by design.
- **Write endpoint proof** (DL-0062):
  - POST without key → 401 ✓
  - POST with invalid key → 401 ✓
  - POST with empty key → 401 ✓
  - POST with valid key → 200 ✓
- **Route-level forwarding**: All 15 backend-proxying routes now use `backendHeaders()` which forwards X-API-Key on ALL requests (GET and POST), so if backend adds read auth later, routes are ready.

### B2: "9 proxy routes missing auth forwarding" — FIXED IN V2 (stale evidence in V2 QA)
- **Root cause in V2 QA report**: QA evidence directory `qa-batch-0-verify-20260208T003843Z` was NOT regenerated. Files still contained V1 results.
- **Proof**: See `v2-remediation/b2-proof-backendHeaders.txt` — all 9 routes now contain `import { backendUrl, backendHeaders } from '@/lib/backend-fetch'` and use `backendHeaders()` in all fetch calls.
- **Independent verification command**: `grep -rl 'backendHeaders' apps/dashboard/src/app/api/ --include='route.ts' | wc -l` → 15
- **Remaining routes without backendHeaders** (3 total, all acceptable):
  - `chat/execute-proposal` — 501 stub, no backend call
  - `chat/session/[sessionId]` — mock data stub, no backend call
  - `events` — 501 stub, no backend call
- **Routes with X-Service-Token** (Agent API, not backend):
  - `chat/complete` — proxies to Agent API (8095)
  - `agent/activity` — proxies to Agent API (8095)

### B3: "Playwright smoke test fails" — FIXED
- **Root cause V1**: `test-results/.last-run.json` owned by root (EACCES for zaks user)
- **Root cause V2**: Browser only in `/root/.cache/ms-playwright/`, not accessible to zaks user
- **Fix**:
  1. Copied browser cache to `/home/zaks/.cache/ms-playwright/` with zaks ownership
  2. Set `test-results/` to world-writable (a+rw) with zaks ownership
  3. Added `/test-results` and `/playwright-report` to `.gitignore`
- **Proof**: Smoke test passes (1 passed in 2.1s), browser present in both locations

## Files Modified (V3 total — 14 files)
1. `apps/dashboard/src/lib/api.ts` — server-side X-API-Key for writes
2. `apps/dashboard/playwright.config.ts` — updated config
3. `apps/dashboard/tests/e2e/smoke.spec.ts` — new smoke test
4. `apps/dashboard/.gitignore` — added test-results, playwright-report
5. `apps/dashboard/src/app/api/actions/quarantine/route.ts` — backendHeaders
6. `apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts` — backendHeaders
7. `apps/dashboard/src/app/api/actions/completed-count/route.ts` — backendHeaders
8. `apps/dashboard/src/app/api/alerts/route.ts` — backendHeaders
9. `apps/dashboard/src/app/api/deferred-actions/route.ts` — backendHeaders
10. `apps/dashboard/src/app/api/deferred-actions/due/route.ts` — backendHeaders
11. `apps/dashboard/src/app/api/quarantine/health/route.ts` — backendHeaders
12. `apps/dashboard/src/app/api/checkpoints/route.ts` — backendHeaders
13. `apps/dashboard/src/app/api/pipeline/route.ts` — backendHeaders
14. `/home/zaks/.cache/ms-playwright/` — browser cache copied for zaks user

## Regression
- TypeScript compilation: PASS (tsc --noEmit exit 0)
- Services: backend (8091) healthy, agent (8095) healthy, dashboard (3003) 307

## Blockers
- None remaining

## How to Independently Verify

```bash
# B2: Check all routes forward auth
grep -rl 'backendHeaders' apps/dashboard/src/app/api/ --include='route.ts' | wc -l
# Expected: 15

# Remaining routes (stubs/Agent API only)
grep -rL 'backendHeaders|X-API-Key|X-Service-Token' apps/dashboard/src/app/api/ --include='route.ts'
# Expected: 3 files (all 501 stubs)

# Gate 1: Write auth
curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8091/api/deals/DL-0051/archive -H 'Content-Type: application/json' -d '{}'
# Expected: 401

# Gate 2: Playwright
cd apps/dashboard && npx playwright test tests/e2e/smoke.spec.ts
# Expected: 1 passed
```
