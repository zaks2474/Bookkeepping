# CLAUDE CODE MISSION: DASHBOARD ROUND 4 — BATCH 0: AUTH + PREFLIGHT + PLAYWRIGHT
## Mission ID: DASHBOARD-R4-BATCH-0
## Codename: "Keystone"
## Priority: P0
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Build everything, verify everything

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   EXECUTION DIRECTIVE                                                        ║
║                                                                              ║
║   This batch is the foundation for all Round-4 dashboard work.               ║
║   It has three non-negotiable outcomes:                                      ║
║                                                                              ║
║   1) All write requests carry X-API-Key (REC-005)                             ║
║   2) Preflight health checks are captured                                     ║
║   3) Playwright is installed + smoke test passes                              ║
║                                                                              ║
║   If any of these fail, every subsequent batch will produce false passes.    ║
║   Do not proceed unless all gates pass.                                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## CONTEXT
- This is Batch 0. No prior batches exist.
- All subsequent batches depend on working write-auth and Playwright.
- Primary source: /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md

---

## SECTION 0: PREFLIGHT VERIFICATION
Run these commands and write outputs to:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-0/evidence/service-health/`

```bash
# Create evidence directories
BASE_EVIDENCE=/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-0/evidence
mkdir -p "$BASE_EVIDENCE/service-health" "$BASE_EVIDENCE/auth-injection" "$BASE_EVIDENCE/playwright-install"

# Repo root
cd /home/zaks/zakops-agent-api
pwd | tee "$BASE_EVIDENCE/service-health/00-repo-root.txt"

# Services
curl -s http://localhost:8091/health | tee "$BASE_EVIDENCE/service-health/01-backend-health.json"
curl -s http://localhost:8095/health | tee "$BASE_EVIDENCE/service-health/02-agent-health.json"

# Dashboard up (basic)
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003 | tee "$BASE_EVIDENCE/service-health/03-dashboard-status.txt"

# Environment keys (do NOT print secret value)
rg -n "ZAKOPS_API_KEY" /home/zaks/zakops-agent-api/apps/dashboard/.env.local | tee "$BASE_EVIDENCE/service-health/04-env-check.txt"
```

If any of the above fails (non-200 health, missing env), fix before continuing.

---

## FIX 1 (P0): REC-005 — API Key Injection for Writes
Goal: Ensure all write calls (POST/PUT/PATCH/DELETE) carry X-API-Key to backend, whether routed via middleware, Next API routes, or server-side apiFetch.

### Step 1A: Audit apiFetch and add server-side X-API-Key
File: `apps/dashboard/src/lib/api.ts`

- `apiFetch` currently adds Idempotency-Key but does not add X-API-Key.
- Add X-API-Key **only on server side** to avoid leaking secrets to the browser.
- Use `process.env.ZAKOPS_API_KEY` when `typeof window === 'undefined'`.

Expected logic (example):
```ts
const method = options.method?.toUpperCase() || 'GET';
const isWrite = ['POST','PUT','PATCH','DELETE'].includes(method);
if (isWrite && typeof window === 'undefined' && process.env.ZAKOPS_API_KEY) {
  (headers as Record<string,string>)['X-API-Key'] = process.env.ZAKOPS_API_KEY;
}
```

### Step 1B: Audit Next API routes for write methods
Directory: `apps/dashboard/src/app/api/**`

- For any route handlers that perform write operations, ensure they call `backendHeaders()` from `apps/dashboard/src/lib/backend-fetch.ts`.
- If any write handler does NOT use backendHeaders(), update it.
- DO NOT bypass middleware for write operations unless the route explicitly sets X-API-Key.

Command to inventory handlers:
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src/app/api -name "route.ts" | while read f; do
  echo "=== $f ==="
  rg -n "export async function (POST|PUT|PATCH|DELETE)" "$f"
  rg -n "backendHeaders" "$f" || echo "WARNING: backendHeaders not used"
done | tee "$BASE_EVIDENCE/auth-injection/01-route-audit.txt"
```

### Step 1C: Verify middleware behavior (write proxy)
File: `apps/dashboard/src/middleware.ts`
- Confirm write methods are proxied with X-API-Key for rewrite-handled routes.
- Ensure `handledByRoutes` list aligns with actual route handlers.

Capture current middleware snapshot:
```bash
sed -n '1,220p' /home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts | tee "$BASE_EVIDENCE/auth-injection/02-middleware-snapshot.txt"
```

### Verification
You must prove 401 without key and 200/201 with key against a **real write endpoint**.
Use OpenAPI + DB to choose a valid endpoint and ID.

```bash
# Find a POST endpoint from backend OpenAPI
curl -s http://localhost:8091/openapi.json | jq '.paths | keys[]' | tee "$BASE_EVIDENCE/auth-injection/03-openapi-paths.txt"

# Use DB to find a valid deal/action id (adjust as needed)
# Example: fetch a deal id
psql -U zakops -d zakops -c "SELECT deal_id FROM zakops.deals LIMIT 1;" | tee "$BASE_EVIDENCE/auth-injection/04-sample-id.txt"

# Replace <DEAL_ID> with a real ID from the DB output
export DEAL_ID=<DEAL_ID>

# Without key (expect 401/403)
curl -i -X POST http://localhost:8091/api/deals/$DEAL_ID/archive \
  -H "Content-Type: application/json" \
  -d '{"operator":"test"}' | tee "$BASE_EVIDENCE/auth-injection/05-no-key.txt"

# With key (expect 200/201)
curl -i -X POST http://localhost:8091/api/deals/$DEAL_ID/archive \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operator":"test"}' | tee "$BASE_EVIDENCE/auth-injection/06-with-key.txt"
```

```
GATE 1:
- Any write endpoint tested returns 401/403 without key
- Same endpoint returns 200/201 with key
- Route handler audit shows backendHeaders() for all write routes
```

---

## FIX 2 (P0): Playwright Installation + Smoke Test
Goal: Install Playwright and ensure a basic UI smoke test passes.

### Step 2A: Install Playwright
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard
npm install -D @playwright/test | tee "$BASE_EVIDENCE/playwright-install/01-install.txt"

npx playwright install --with-deps chromium | tee "$BASE_EVIDENCE/playwright-install/02-browser-install.txt"
```

### Step 2B: Create playwright.config.ts
Path: `apps/dashboard/playwright.config.ts`
- baseURL: http://localhost:3003
- retries: 1
- workers: 1

### Step 2C: Create smoke test
Path: `apps/dashboard/tests/e2e/smoke.spec.ts`
Test must:
- open `/`
- verify main page renders (e.g., header text exists)

Example:
```ts
import { test, expect } from '@playwright/test';

test('smoke: dashboard loads', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('body')).toBeVisible();
});
```

### Verification
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard
npx playwright test --list | tee "$BASE_EVIDENCE/playwright-install/03-list.txt"

npx playwright test tests/e2e/smoke.spec.ts | tee "$BASE_EVIDENCE/playwright-install/04-smoke.txt"
```

```
GATE 2:
- Playwright installed and `npx playwright test --list` succeeds
- Smoke test passes
```

---

## VERIFICATION SEQUENCE
Run after all fixes:
```bash
# Gate 1
cat "$BASE_EVIDENCE/auth-injection/05-no-key.txt"
cat "$BASE_EVIDENCE/auth-injection/06-with-key.txt"

# Gate 2
cat "$BASE_EVIDENCE/playwright-install/04-smoke.txt"
```

---

## AUTONOMY RULES
- If a dependency is missing, create it.
- If a route handler is missing X-API-Key, fix it.
- If a write endpoint does not exist, document as BLOCKER and proceed with Playwright install.
- Do not stop unless blocked by missing infrastructure or permissions.

---

## OUTPUT FORMAT
Save a completion report at:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-0/completion-report.md`

Template:
```
# DASHBOARD-R4 BATCH 0 — COMPLETION REPORT

## Summary
| Fix | Status | Evidence |
|-----|--------|----------|
| REC-005 API Key Injection | PASS/FAIL | path(s) |
| Playwright Install + Smoke | PASS/FAIL | path(s) |

## Gates
| Gate | Result | Evidence |
|------|--------|----------|
| Gate 1 | PASS/FAIL | auth-injection/05-no-key.txt, 06-with-key.txt |
| Gate 2 | PASS/FAIL | playwright-install/04-smoke.txt |

## Blockers (if any)
- ...

## Notes
- ...
```

---

## HARD RULES
- Do not remove or weaken auth enforcement.
- Do not expose secret API keys to client-side bundles.
- No gate == no completion.
