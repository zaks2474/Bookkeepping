# DASHBOARD_ROUND4_EVAL_PASS2 — Execution Blueprint

---

## 1) AGENT IDENTITY

- **agent_name:** Claude-Opus
- **run_id:** 20260205-1750-exec
- **date_time:** 2026-02-05T17:50:00Z
- **repo_revision_dashboard:** b96b33c5
- **repo_revision_backend:** 2a68de17
- **repo_revision_agent_api:** b96b33c5
- **pass1_reference:** `DASHBOARD_ROUND4_EVAL_PASS1.Claude-Opus.20260205-1745-eval1.md`

---

## 2) EXECUTIVE ANSWERS

### Q1: What should be fixed FIRST to stabilize visible UX?
**Answer:** Three stop-the-bleeding fixes in order:
1. **Deal routing slug guard** — `/deals/new` and `/deals/GLOBAL` crash the UI
2. **Action bulk delete 405** — Users see "Method Not Allowed" on common operation
3. **Quarantine delete 404** — Delete button does nothing

### Q2: Exactly what endpoints/contracts must exist?

| Priority | Endpoint | Method | Request Body | Response | Notes |
|----------|----------|--------|--------------|----------|-------|
| P0 | `/api/deals` | POST | `{canonical_name, broker, ...}` | `{deal_id, ...}` | Deal creation |
| P0 | `/api/deals/bulk-archive` | POST | `{deal_ids[], operator, reason}` | `{archived[]}` | Bulk archive |
| P0 | `/api/quarantine/{id}/delete` | POST | `{deleted_by, reason?}` | `{hidden: true}` | Remove from queue |
| P0 | `/api/actions/clear-completed` | POST | `{operation, age}` | `{affected_count}` | Clear old actions |
| P1 | `/api/actions/{id}/execute` | POST | `{}` | `{action}` | Run approved action |
| P1 | `/api/actions/{id}/cancel` | POST | `{reason?}` | `{action}` | Cancel action |
| P1 | `/api/onboarding/complete` | POST | `{profile, preferences}` | `{success}` | Persist onboarding |
| P1 | `/api/integrations/email/connect` | POST | `{oauth_code}` | `{connected: true}` | Email OAuth |
| P2 | `/api/chat/health` | GET | - | `{status, model}` | Provider health check |
| P2 | `/api/user/profile` | GET | - | `{name, email, role}` | User identity |

### Q3: Exactly what UI routes must be protected?

| Route Pattern | Reserved Slugs | Protection Strategy |
|---------------|----------------|---------------------|
| `/deals/[id]` | `new`, `GLOBAL`, `global`, `edit`, `bulk` | Create `/deals/new/page.tsx` for precedence; add slug guard in `[id]` for others |
| `/actions/[id]` | `metrics`, `capabilities`, `bulk`, `clear-completed` | Create explicit routes for each OR add redirect guard |
| `/quarantine/[id]` | `bulk`, `stats` | Create explicit routes |

**Implementation:**
```typescript
// In /deals/[id]/page.tsx
const RESERVED = ['new', 'GLOBAL', 'global', 'edit', 'bulk'];
if (RESERVED.includes(params.id)) {
  if (params.id === 'new') redirect('/deals/new');
  if (params.id.toLowerCase() === 'global') return <GlobalDealsView />;
  notFound();
}
```

### Q4: Exactly what auth/header rules must be consistent?

| Rule | Current State | Required State | Implementation |
|------|---------------|----------------|----------------|
| X-API-Key | Added in `backendHeaders()` but NOT in client `apiFetch()` | All write operations must include key | Route all writes through Next.js API routes that add header |
| Operator Identity | localStorage `zakops_operator_name` | Validate against session/auth claims | Backend must reject unknown operators |
| Idempotency-Key | Added in `apiFetch()` for POST/PUT/PATCH | Backend must enforce de-dupe | Verify backend returns 409 on duplicate key |
| correlation_id | Not added | All requests must include `X-Correlation-ID` | Add to `apiFetch()` header block |

### Q5: Exactly what E2E tests must be added?

| Test ID | Test Name | Steps | Assertions | Stability Notes |
|---------|-----------|-------|------------|-----------------|
| E2E-001 | Deal creation route | Navigate `/deals/new` | Form renders, no console errors | Use static content check, not API mock |
| E2E-002 | Deal GLOBAL route | Navigate `/deals/GLOBAL` | Global view renders OR clean redirect | Define expected behavior first |
| E2E-003 | Bulk delete deals | Select 2 deals, click delete | Toast shows count, deals removed from list | Seed 3 test deals, delete 2 |
| E2E-004 | Quarantine delete | Click delete on queue item | Item removed, toast confirms | Seed 1 test quarantine item |
| E2E-005 | Quarantine approve | Fill operator, click approve | Item removed, deal appears | Verify deal creation endpoint works first |
| E2E-006 | Clear completed actions | Click Clear > Delete All | Toast shows count | Seed 5 completed actions |
| E2E-007 | Chat markdown | Send "Show **bold** text" | Response contains `<strong>bold</strong>` | Check rendered HTML |
| E2E-008 | Settings email tab | Navigate `/settings#email` | Email section visible | Requires Settings redesign first |
| E2E-009 | Onboarding complete | Complete all steps | Navigates to dashboard, state persists | Requires backend endpoint |
| E2E-010 | Error boundary | Navigate `/deals/crash-test` | Error UI renders, not white screen | Add intentional crash route for testing |

**Minimal Flake Strategy:**
- Use `data-testid` selectors, not CSS classes
- Wait for network idle before assertions
- Seed database with deterministic test data
- Use `test.describe.serial` for stateful flows
- Add 500ms delay before screenshot comparison

### Q6: Exactly what gates must be tightened?

| Gate | Check Type | CI Integration | Failure Action |
|------|------------|----------------|----------------|
| Contract Gate | Static | `npm run contract:check` | Block PR merge |
| No Dead UI Gate | Static + Runtime | Grep + Playwright click-all | Block PR merge |
| E2E Gate | Runtime | Playwright suite | Block deploy |
| Observability Gate | Runtime | Log correlation check | Block production |
| Security Gate | Static | `npm audit` + XSS scan | Block PR merge |

---

## 3) PHASED IMPLEMENTATION PLAN

### Phase P0 — Stop-the-Bleeding (3 atomic tasks)

**Objective:** Eliminate visible user-facing errors without backend changes.

| Task | Description | File(s) | Rollback | Acceptance Criteria | Proof Artifact |
|------|-------------|---------|----------|---------------------|----------------|
| P0-1 | Create `/deals/new/page.tsx` | New file | `git revert` | `/deals/new` renders create form | Playwright E2E-001 |
| P0-2 | Add slug guard in `/deals/[id]/page.tsx` | Edit existing | Conditional remove | `/deals/GLOBAL` shows global view or redirect | Playwright E2E-002 |
| P0-3 | Disable broken buttons until backend ready | Multiple files | Feature flag revert | No 405/404 errors in console | Manual audit log |

**Dependencies:** None (frontend-only)

**Evidence Commands:**
```bash
# After P0-1
curl -s -o /dev/null -w "%{http_code}" http://localhost:3003/deals/new
# Expected: 200

# After P0-2
curl -s http://localhost:3003/deals/GLOBAL | grep -q "Failed to load" && echo "FAIL" || echo "PASS"
```

---

### Phase P1 — Contract Stabilization (6 atomic tasks)

**Objective:** Fix all 404/405 errors by adding backend endpoints or fixing proxy.

| Task | Description | File(s) | Dependencies | Acceptance Criteria | Proof Artifact |
|------|-------------|---------|--------------|---------------------|----------------|
| P1-1 | Add `POST /api/deals` endpoint | Backend FastAPI | Schema design | `curl -X POST /api/deals` returns 201 | curl output |
| P1-2 | Add `POST /api/deals/bulk-archive` endpoint | Backend FastAPI | P1-1 | `curl -X POST /api/deals/bulk-archive` returns 200 | curl output |
| P1-3 | Add `POST /api/quarantine/{id}/delete` endpoint | Backend FastAPI | Schema | `curl -X POST /api/quarantine/test/delete` returns 200 | curl output |
| P1-4 | Add `POST /api/actions/clear-completed` endpoint | Backend FastAPI | Schema | `curl -X POST /api/actions/clear-completed` returns 200 | curl output |
| P1-5 | Fix X-API-Key injection | Frontend API routes | None | All writes succeed with auth | E2E tests pass |
| P1-6 | Remove mock fallbacks in production | Frontend API routes | P1-1 to P1-4 | No `[Mock]` in logs | Log grep |

**Rollback Strategy:**
- If endpoint breaks existing clients: add `/v2/` prefix, keep `/v1/`
- If X-API-Key change breaks: revert and add session auth instead

**Evidence Commands:**
```bash
# P1-3 verification
curl -i -X POST http://localhost:8091/api/quarantine/test-id/delete \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deleted_by":"qa"}'
# Expected: HTTP 200
```

---

### Phase P2 — Onboarding + Settings Real Wiring (5 atomic tasks)

**Objective:** Replace demo-only UX with real backend integration.

| Task | Description | File(s) | Dependencies | Acceptance Criteria | Proof Artifact |
|------|-------------|---------|--------------|---------------------|----------------|
| P2-1 | Add `POST /api/onboarding/complete` endpoint | Backend | Schema design | Endpoint returns 200 | curl output |
| P2-2 | Wire onboarding to backend | Frontend | P2-1 | Refresh preserves onboarding state | E2E-009 |
| P2-3 | Build email settings section | Frontend `/settings` | Backend email API | Tab renders, OAuth flow works | Screenshot |
| P2-4 | Build agent config section | Frontend `/settings` | Backend user prefs | Settings persist | Screenshot |
| P2-5 | Add chat markdown renderer | Frontend `/chat` | None | `**bold**` renders as bold | E2E-007 |

**Rollback Strategy:**
- If OAuth blocked: add "Coming Soon" placeholder
- If backend unavailable: keep localStorage with warning banner

---

### Phase P3 — Polish + Observability (4 atomic tasks)

**Objective:** Add traceability and prevent regressions.

| Task | Description | File(s) | Dependencies | Acceptance Criteria | Proof Artifact |
|------|-------------|---------|--------------|---------------------|----------------|
| P3-1 | Add correlation_id to all requests | Frontend `api.ts` | None | All logs have correlation_id | Log sample |
| P3-2 | Add frontend error tracking | Sentry/LogRocket | None | JS errors captured | Sentry dashboard |
| P3-3 | Add Contract Gate to CI | GitHub Actions | OpenAPI spec | PR blocked on mismatch | CI failure screenshot |
| P3-4 | Add No Dead UI check to CI | GitHub Actions | Playwright | PR blocked on dead UI | CI failure screenshot |

---

## 4) "NO DEAD UI" DETECTION STRATEGY

### 4.1 Static Checks (CI Pre-commit)

```bash
# Check for TODO onClick handlers
rg -l "onClick.*TODO" apps/dashboard/src/
rg -l "onClick.*\(\)" apps/dashboard/src/  # empty handlers

# Check for fetch routes not in contract
npm run contract:extract-ui
diff ui-routes.txt backend-routes.txt

# Check for disabled buttons without tooltip explanation
rg -l 'disabled.*{true}' apps/dashboard/src/ | \
  xargs -I {} sh -c 'rg -L "title=" {} && echo "Missing disabled explanation: {}"'
```

### 4.2 Runtime Checks (Playwright)

```typescript
// click-all-buttons.spec.ts
test('every button is functional', async ({ page }) => {
  const routes = ['/dashboard', '/deals', '/actions', '/quarantine', '/settings'];

  for (const route of routes) {
    await page.goto(route);
    await page.waitForLoadState('networkidle');

    const buttons = await page.locator('button:not([disabled])').all();
    for (const button of buttons) {
      await button.click();

      // Check no error toast appeared
      await expect(page.locator('[data-testid="error-toast"]')).not.toBeVisible();

      // Check no console errors
      page.on('console', msg => {
        if (msg.type() === 'error') throw new Error(`Console error: ${msg.text()}`);
      });
    }
  }
});
```

### 4.3 Contract Checks (OpenAPI vs Frontend)

```typescript
// contract.check.ts
import { paths } from './generated/api-types';  // From openapi-typescript
import { UI_API_CALLS } from './api';  // Manually maintained list

for (const call of UI_API_CALLS) {
  if (!paths[call.path]?.[call.method]) {
    throw new Error(`UI calls ${call.method} ${call.path} but backend does not expose it`);
  }
}
```

---

## 5) EXECUTION RISK REGISTER

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Backend team unavailable | P1 delayed | Medium | Frontend stubs return explicit "Not Implemented" error |
| OAuth blocked by Google | P2-3 delayed | Medium | Manual credential entry fallback |
| E2E tests flaky | Gate C unreliable | High | Test isolation + deterministic seeds + 3x retry |
| Slug guard breaks deep links | P0-2 regresses | Low | Preserve query params on redirect |
| Mock removal breaks dev | P1-6 blocks development | Medium | Keep mocks behind `NEXT_PUBLIC_MOCK_MODE=true` |
| Contract gate too strict | False positives | Medium | Allow `/internal/*` routes without check |
| Correlation ID overhead | Performance | Low | UUID generation is O(1), header is small |
| Error tracking quota | Cost | Medium | Sample at 10% in production |
| Markdown XSS | Security | Medium | Use `rehype-sanitize` with strict allowlist |
| Concurrent deploys | State mismatch | Low | Use database migrations with locks |

---

## 6) RECOMMENDED PHASE ORDER

```
P0 (Stop-the-Bleeding)      [Frontend Only - Immediate]
  ↓
P1-5, P1-6 (Frontend Auth)  [Frontend Only - 1 day]
  ↓
P1-1, P1-2, P1-3, P1-4      [Backend Required - Parallel]
  ↓
P2-5 (Chat Markdown)        [Frontend Only - Quick Win]
  ↓
P2-1, P2-2 (Onboarding)     [Backend + Frontend]
  ↓
P2-3, P2-4 (Settings)       [Backend + Frontend]
  ↓
P3 (Observability)          [CI Integration - Final]
```

---

## 7) HIGH-LEVERAGE TESTS/GATES

| Rank | Test/Gate | Catches | Effort |
|------|-----------|---------|--------|
| 1 | Contract Gate (OpenAPI diff) | All 404/405 errors | Medium |
| 2 | E2E-001 (Deal new route) | P0 routing crash | Low |
| 3 | E2E-006 (Clear completed) | P1 bulk operation failure | Low |
| 4 | Click-all-buttons test | Any dead UI | Medium |
| 5 | E2E-007 (Chat markdown) | Rendering bugs | Low |
| 6 | Correlation ID log check | Traceability gaps | Low |
| 7 | Mock code grep | Production demo code | Low |
| 8 | Disabled button audit | UX dead ends | Low |
| 9 | E2E-009 (Onboarding) | Demo-only detection | Medium |
| 10 | Error boundary test | Crash recovery | Medium |

---

*Execution Blueprint PASS 2 Complete: 2026-02-05T17:50:00Z*
*Architect: Claude-Opus*
