# DASHBOARD_ROUND4_EVAL_PASS1 — Adversarial Augmentation Report

---

## 1) AGENT IDENTITY

- **agent_name:** Claude-Opus
- **run_id:** 20260205-1745-eval1
- **date_time:** 2026-02-05T17:45:00Z
- **repo_revision_dashboard:** b96b33c5
- **repo_revision_backend:** 2a68de17
- **repo_revision_agent_api:** b96b33c5
- **reports_reviewed:** Claude-Opus, Codex, Gemini-CLI

---

## 2) EXECUTIVE SUMMARY

This adversarial pass identifies **23 missing items**, **18 weaknesses**, and proposes **15 world-class upgrades**. The existing reports converge on similar issues but diverge on root cause analysis and remediation strategy. Critical blind spots include: auth model inconsistency, pagination/filtering gaps, keyboard accessibility, loading state handling, and error boundary coverage.

---

## A) WHAT'S MISSING — Blind Spots Across All Three Reports

### A-1. Missing UI Actions Not Inventoried

| ID | Missing Item | Evidence Gap |
|----|--------------|--------------|
| M-01 | **Pagination controls** on `/deals`, `/actions`, `/quarantine` lists not tested | No report mentions limit/offset behavior or infinite scroll testing |
| M-02 | **Filter persistence** across navigation (URL params vs state) | Filters may reset on back navigation |
| M-03 | **Keyboard accessibility** (Tab order, Enter/Escape handlers) | No a11y testing mentioned in any report |
| M-04 | **Loading states** for slow API responses (skeleton vs spinner) | Only Codex mentions Skeleton but no consistency check |
| M-05 | **Error boundary** behavior when component crashes | No report tests React error boundaries |
| M-06 | **Offline/network failure** handling | No offline mode or retry-on-reconnect testing |
| M-07 | **Session expiration** behavior (what happens when API key expires mid-session?) | Auth model discussion lacks session lifecycle |
| M-08 | **Concurrent user** editing conflicts (optimistic updates vs server state) | No discussion of race conditions |
| M-09 | **File upload** behavior in quarantine/materials (if any) | Materials tab has downloads but upload not mapped |
| M-10 | **Print/export** functionality for deal data | No export feature testing |

### A-2. Missing Endpoints Not Mapped

| ID | Endpoint | Used By | Verification Needed |
|----|----------|---------|---------------------|
| M-11 | `GET /api/health` or `/api/version` | Dashboard startup check | NEEDS VERIFICATION: Does backend expose health endpoint? |
| M-12 | `POST /api/onboarding/complete` | Onboarding persistence | All reports say missing; none propose schema |
| M-13 | `GET /api/user/profile` or `/me` | User identity display | Who is the logged-in user? How is identity displayed? |
| M-14 | `POST /api/deals` (create) | Deal creation form | If `/deals/new` is fixed, what endpoint creates deals? |
| M-15 | `PATCH /api/deals/{id}` (edit fields) | Deal detail editing | Can users edit deal metadata beyond notes? |
| M-16 | `GET /api/audit-log` | Action history | No audit trail UI discovered |
| M-17 | `POST /api/integrations/email/test` | Email settings test | Gemini mentions but no verification |
| M-18 | `DELETE /api/actions/{id}` (hard delete) | Action permanent removal | Claude-Opus marks "Unknown"; Codex says "missing" |

### A-3. Missing Contract Checks

| ID | Contract Gap |
|----|--------------|
| M-19 | **Method + Path + Body validation**: No OpenAPI schema verification automation proposed |
| M-20 | **Response schema validation**: Frontend Zod schemas never compared to backend Pydantic models |
| M-21 | **Error response format**: Is error format consistent? `{error: string}` vs `{detail: string}` vs `{message: string}`? |
| M-22 | **Rate limiting behavior**: What happens if user clicks button 10x fast? |
| M-23 | **Idempotency keys**: Claude-Opus mentions apiFetch adds them, but backend idempotency enforcement not verified |

### A-4. Missing E2E Tests Specified

| ID | Test Gap |
|----|----------|
| M-24 | No test for `/deals/GLOBAL` post-fix (what should GLOBAL actually render?) |
| M-25 | No test for quarantine **bulk** delete (only single delete mentioned) |
| M-26 | No test for chat **citation links** (do they navigate correctly?) |
| M-27 | No test for deal **stage transition** with invalid transition (rejection case) |
| M-28 | No test for **concurrent approval** (two users approve same quarantine item) |

### A-5. Missing Auth Wiring Clarity

| ID | Auth Gap |
|----|----------|
| M-29 | **Who is the "operator"?** All approve/reject calls send `operatorName` from localStorage. Is this validated server-side? |
| M-30 | **Tenant isolation**: Multi-tenant scoping never mentioned. Can user A see user B's deals? |
| M-31 | **API key rotation**: If key changes, does frontend gracefully re-auth or hard fail? |

### A-6. Missing Observability Correlation Strategy

| ID | Observability Gap |
|----|-------------------|
| M-32 | **Frontend-to-backend correlation_id** injection not verified in any `apiFetch` call |
| M-33 | **Error tracking integration** (Sentry, LogRocket) not mentioned |
| M-34 | **Performance monitoring** (Web Vitals, API latency histograms) not proposed |

### A-7. Missing Settings Redesign Requirements

| ID | Settings Gap |
|----|--------------|
| M-35 | **Data retention** settings (how long to keep completed actions?) |
| M-36 | **Theme/appearance** settings (dark mode toggle location) |
| M-37 | **Timezone** settings (event timestamps in user's timezone?) |
| M-38 | **Default filters** settings (remember last deal stage filter?) |

### A-8. Missing Onboarding Workflow Wiring

| ID | Onboarding Gap |
|----|----------------|
| M-39 | **Resume onboarding**: If user leaves mid-flow, how is progress restored? |
| M-40 | **Skip validation**: Can user skip all steps and still use the app? What's blocked? |
| M-41 | **Re-onboard trigger**: How does user re-enter onboarding to change email settings? |

---

## B) WHAT'S WRONG / WEAK — Critique of Recommendations

### B-1. Weak Recommendations

| ID | Report | Weakness | Verification Needed |
|----|--------|----------|---------------------|
| W-01 | Claude-Opus | "Fix deal routing slug guard" assumes `RESERVED_SLUGS` is sufficient | What about `edit`, `settings`, `archive`? Need comprehensive slug list from product spec |
| W-02 | Claude-Opus | "Add react-markdown" without specifying sanitization | XSS risk if `rehype-raw` is enabled. NEEDS VERIFICATION: What rehype plugins are safe? |
| W-03 | Codex | "Route all writes through Next API routes" | This doubles latency. Better: server-side session with signed cookies |
| W-04 | Codex | L-03 "Client writes lack X-API-Key" | But Codex also says backend requires it. How do existing writes work at all? Contradiction needs resolution |
| W-05 | Gemini | "Force Agent SQL fallback" | This defeats RAG purpose. Better: fix RAG index freshness, add provenance badge |
| W-06 | Gemini | "Update proxy target to `/api/kinetic/actions`" | NEEDS VERIFICATION: Is `/api/kinetic/actions` the actual backend path? Check FastAPI routes |
| W-07 | All | No rollback strategy for Phase 0 fixes | If slug guard breaks deep links, how to revert? |
| W-08 | All | "Implement endpoint X" assumes backend team availability | No stub/mock strategy for frontend-only progress |

### B-2. Fragile Assumptions

| ID | Assumption | Risk |
|----|------------|------|
| W-09 | "Backend returns 405 for missing routes" | FastAPI may return 404 for some path patterns. Need to test both |
| W-10 | "localStorage operator name is sufficient" | No identity verification. User can impersonate any operator name |
| W-11 | "Mock fallbacks only trigger on 404" | If backend returns 500, mock doesn't trigger. Error handling incomplete |
| W-12 | "Email OAuth will work" | Google OAuth requires verified domain. Dev environment may fail |
| W-13 | "Playwright E2E will be stable" | No mention of test isolation, database seeding, or deterministic IDs |

### B-3. Ambiguous Claims Requiring Clarification

| ID | Claim | Clarification Steps |
|----|-------|---------------------|
| W-14 | "Data integrity mismatch (3 vs 9 deals)" | Run: `curl /api/deals | jq length` AND `curl /agent-api/tools/search_deals | jq length` simultaneously. Document exact counts and filters |
| W-15 | "Quarantine preview returns null for some items" | Which items? Run: `for id in $(curl /api/actions/quarantine | jq -r '.[].id'); do curl /api/actions/quarantine/$id/preview; done` |
| W-16 | "Backend lacks /api/actions/clear-completed" | Verify: `grep -r "clear-completed" zakops-backend/src/` to confirm absence |
| W-17 | "Agent queries deal_registry SQLite directly" | Verify: Is deal_registry a separate SQLite file or same DB? Check `deal_tools.py` imports |
| W-18 | "Capability conflict 501 vs router" | Verify: `curl -i /api/actions/capabilities` and check response code and body |

---

## C) WHAT ELSE IS BROKEN — Pattern Expansion

### C-1. 405 Method Not Allowed Pattern

**Where else?**
```bash
# Systematic search for POST calls to paths that may not have handlers
rg -n "apiFetch\(.*, \{.*method: 'POST'" apps/dashboard/src/lib/api.ts | \
  awk -F"'" '{print $2}' | sort -u > frontend_post_paths.txt

# Compare against backend routes
python -c "from zakops_backend.src.api.orchestration.main import app; print([r.path for r in app.routes if 'POST' in r.methods])" > backend_post_paths.txt

diff frontend_post_paths.txt backend_post_paths.txt
```

**Potential Additional 405s:**
- `POST /api/chat/session/{id}/clear` (clear chat history)
- `POST /api/deals/{id}/refresh-enrichment` (trigger re-enrichment)
- `POST /api/alerts/dismiss` (dismiss alert)

**Prevention Gate:**
```yaml
# CI check: contract-mismatch.yml
- name: Contract Mismatch Check
  run: |
    npm run extract-api-calls > frontend.txt
    python scripts/extract-backend-routes.py > backend.txt
    diff frontend.txt backend.txt || exit 1
```

### C-2. Catch-All Route Collision Pattern

**Where else?**
```bash
# Find all [param] routes
find apps/dashboard/src/app -name '[*]/page.tsx' -type f

# Check if sibling routes exist for common patterns
# Example: /actions/[id] - does /actions/new exist?
```

**Potential Additional Collisions:**
- `/actions/[id]` captures `/actions/metrics`, `/actions/capabilities`
- `/quarantine/[id]` captures `/quarantine/bulk`, `/quarantine/stats`

**Prevention Gate:**
```typescript
// route-guard.test.ts
const RESERVED_SLUGS = ['new', 'edit', 'bulk', 'metrics', 'capabilities', 'stats', 'GLOBAL'];
// Test that each reserved slug either has explicit route or returns 404 intentionally
```

### C-3. Mock Fallback Masking Pattern

**Detection Strategy:**
```bash
# Find all mock fallbacks in API routes
rg -A 5 "if.*backendResponse.status === 404" apps/dashboard/src/app/api/

# These files have hidden failures:
# - /api/actions/clear-completed/route.ts
# - /api/actions/bulk/delete/route.ts
# - /api/actions/bulk/archive/route.ts
```

**Prevention Gate:**
```typescript
// In production builds, fail instead of mocking
if (process.env.NODE_ENV === 'production' && backendResponse.status >= 400) {
  throw new Error(`Backend error ${backendResponse.status}: ${endpoint}`);
}
```

---

## D) WORLD-CLASS UPGRADES — Architecture Improvements

### D-01. Contract-First API Gating
**What:** Generate TypeScript client from backend OpenAPI spec. CI fails if frontend calls endpoint not in spec.
**How:** Use `openapi-typescript` + `openapi-fetch`. Backend generates `openapi.json` on build.
**Benefit:** Zero method/path mismatches at compile time.

### D-02. Playwright "Click Every Button" Test
**What:** Automated discovery of all `<button>`, `<a>`, `onClick` elements. Test clicks each and asserts no console errors or 4xx/5xx responses.
**How:** Custom Playwright utility that traverses DOM and clicks all interactive elements.
**Benefit:** No Dead UI guarantee.

### D-03. Request Correlation ID Middleware
**What:** Every `apiFetch` call adds `X-Correlation-ID: uuid`. Backend logs include this ID. Frontend error tracking includes this ID.
**How:** Middleware wrapper around fetch. Sentry/LogRocket breadcrumb injection.
**Benefit:** End-to-end traceability for every user action.

### D-04. Unified Operations API
**What:** Single `POST /api/ops` endpoint that accepts operation type and parameters. Frontend doesn't need to know about 20 different bulk endpoints.
**How:** Backend orchestration layer dispatches to appropriate handlers.
**Benefit:** Single contract to maintain; easier versioning.

### D-05. UX State Sync Protocol
**What:** Frontend subscribes to backend events (SSE/WebSocket) for deal changes. When another user modifies deal, UI updates automatically.
**How:** Event bus pattern with optimistic updates and server reconciliation.
**Benefit:** No stale data; no need to refresh.

### D-06. Capability-Based UI Rendering
**What:** Backend returns user capabilities (can_delete_deal, can_approve_quarantine). Frontend hides/disables buttons user can't use.
**How:** `/api/capabilities/me` returns permission set. UI components check before rendering.
**Benefit:** No "click then fail" experiences.

### D-07. Schema-Driven Forms
**What:** Settings, onboarding, and deal creation forms generated from JSON Schema. Backend returns schema; frontend renders.
**How:** `react-jsonschema-form` or similar. Backend Pydantic models generate schema.
**Benefit:** Forms always match backend validation; no manual sync.

### D-08. Typed Error Protocol
**What:** All API errors follow standard format: `{code: string, message: string, details?: object, correlation_id: string}`.
**How:** Backend error handler middleware. Frontend error boundary parses and displays.
**Benefit:** Consistent error UX; actionable error messages.

### D-09. Feature Flag Integration
**What:** Demo-only features (onboarding email mock) are behind flags. Production build removes them entirely.
**How:** `@vercel/flags` or LaunchDarkly. Build-time tree shaking for disabled features.
**Benefit:** No demo code in production; safe to ship partial features.

### D-10. Automated Screenshot Regression
**What:** Playwright captures screenshots of every page. CI compares against baseline.
**How:** Percy, Chromatic, or custom diff. Threshold for acceptable pixel difference.
**Benefit:** Catch unintended visual changes.

### D-11. API Versioning Strategy
**What:** Backend supports `/api/v1/`, `/api/v2/`. Frontend specifies version in base URL.
**How:** FastAPI path prefix. Frontend config for API version.
**Benefit:** Breaking changes don't break existing clients.

### D-12. Graceful Degradation Patterns
**What:** If non-critical feature fails (enrichment, materials), UI shows placeholder instead of error.
**How:** Error boundaries with fallback UI per section.
**Benefit:** Core workflow continues even when auxiliary services fail.

### D-13. Optimistic Update Protocol
**What:** UI immediately reflects user action (archive deal) before server confirms. Rollback if server fails.
**How:** React Query mutation with `onMutate` optimistic update and `onError` rollback.
**Benefit:** Snappy UX; no waiting for server round-trip.

### D-14. Health Dashboard
**What:** `/health` page showing status of all integrations (backend, agent, RAG, email).
**How:** Aggregate health checks into single dashboard view.
**Benefit:** Operators can diagnose issues before users report them.

### D-15. Audit Trail UI
**What:** Every action (approve, reject, transition, note) logged with actor, timestamp, correlation_id. UI shows activity feed per deal.
**How:** Backend event sourcing. Frontend activity timeline component.
**Benefit:** Compliance; debugging; accountability.

---

## E) SYSTEMATIC SEARCH PLANS

### E-1. Find All 405/404 Prone Endpoints
```bash
#!/bin/bash
# Run from monorepo root

# Extract all API calls from frontend
rg -o "apiFetch\(['\"]([^'\"]+)['\"]" apps/dashboard/src/ | \
  sed "s/.*apiFetch(['\"]//;s/['\"].*//" | sort -u > /tmp/frontend_endpoints.txt

# Extract all routes from backend (requires FastAPI introspection)
python3 << 'EOF'
import sys
sys.path.insert(0, 'zakops-backend/src')
from api.orchestration.main import app
for route in app.routes:
    if hasattr(route, 'methods'):
        for method in route.methods:
            print(f"{method} {route.path}")
EOF
> /tmp/backend_routes.txt

# Diff
echo "=== Frontend calls not in backend ==="
comm -23 /tmp/frontend_endpoints.txt /tmp/backend_routes.txt
```

### E-2. Find All Reserved Slug Collisions
```bash
# Find all dynamic routes
find apps/dashboard/src/app -type d -name '\[*\]' | while read dir; do
  parent=$(dirname "$dir")
  slug=$(basename "$dir" | tr -d '[]')
  echo "=== $dir ==="
  echo "Siblings that should exist:"
  ls -1 "$parent" 2>/dev/null | grep -v '\[' || echo "  (none)"
done
```

### E-3. Find All Mock Fallbacks
```bash
rg -l "Mock|mock|fallback|development" apps/dashboard/src/app/api/
```

---

## F) SUMMARY TABLES

### Top 10 Missing Items
1. M-01: Pagination controls not tested
2. M-14: `POST /api/deals` create endpoint not verified
3. M-19: No OpenAPI schema validation automation
4. M-29: Operator identity not verified server-side
5. M-32: correlation_id injection not verified
6. M-39: Onboarding resume not specified
7. M-24: No test for `/deals/GLOBAL` expected behavior
8. M-21: Error response format inconsistent
9. M-30: Tenant isolation not discussed
10. M-17: Email test endpoint not verified

### Top 10 Weaknesses
1. W-04: Codex contradiction about X-API-Key
2. W-05: Gemini "force SQL fallback" defeats RAG
3. W-10: localStorage operator name not secure
4. W-11: Mock fallbacks don't trigger on 500
5. W-13: Playwright stability not addressed
6. W-06: `/api/kinetic/actions` path not verified
7. W-07: No rollback strategy for Phase 0
8. W-14: Data mismatch claim not reproduced
9. W-02: Markdown XSS risk not addressed
10. W-09: 405 vs 404 assumption fragile

### Top 10 Upgrade Ideas
1. D-01: Contract-first API gating
2. D-02: Click-every-button test
3. D-03: Request correlation ID middleware
4. D-06: Capability-based UI rendering
5. D-08: Typed error protocol
6. D-09: Feature flag integration
7. D-13: Optimistic update protocol
8. D-14: Health dashboard
9. D-15: Audit trail UI
10. D-07: Schema-driven forms

---

*Adversarial Evaluation PASS 1 Complete: 2026-02-05T17:45:00Z*
*Auditor: Claude-Opus*
