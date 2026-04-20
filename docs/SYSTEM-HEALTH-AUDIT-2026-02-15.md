# System-Wide Health Audit Report

**Date:** 2026-02-15
**Auditor:** Claude (Opus 4.6)
**Method:** Playwright browser crawl (12 pages), API route handler filesystem audit, middleware analysis, backend endpoint probing

---

## Executive Summary

**8 of 12 dashboard pages have broken features.** The root cause is a systemic proxy layer gap: `api.ts` functions call endpoints that have no corresponding Next.js route handler, causing 404 HTML responses instead of JSON data. **12 route handlers are missing**, **3 existing handlers are unreachable** due to middleware misconfiguration, and **5 non-API bugs** affect interactive elements.

---

## Issue Classification

### Category 1: Missing Route Handlers (12 instances)

`api.ts` functions call endpoints, the middleware intercepts the path (via `handledByRoutes`), but no Next.js route handler file exists. Result: 404 HTML.

| # | Endpoint | Method | api.ts Function | Affected Page |
|---|----------|--------|-----------------|---------------|
| 1 | `/api/quarantine/{id}` | GET | `getQuarantinePreview()` | Quarantine |
| 2 | `/api/quarantine/bulk-process` | POST | `bulkProcessQuarantineItems()` | Quarantine |
| 3 | `/api/quarantine/bulk-delete` | POST | `bulkDeleteQuarantineItems()` | Quarantine |
| 4 | `/api/quarantine/{id}/undo-approve` | POST | `undoQuarantineApproval()` | Quarantine |
| 5 | `/api/actions` | GET | `getKineticActions()` | Actions |
| 6 | `/api/actions` | POST | `createKineticAction()` | Actions |
| 7 | `/api/actions/capabilities` | GET | `isKineticApiAvailable()` | Actions, HQ, Deal Detail |
| 8 | `/api/actions/{id}/approve` | POST | `approveKineticAction()` | Actions |
| 9 | `/api/actions/{id}/cancel` | POST | `cancelKineticAction()` | Actions |
| 10 | `/api/actions/{id}/retry` | POST | `retryKineticAction()` | Actions |
| 11 | `/api/actions/{id}/update` | POST | `updateKineticActionInputs()` | Actions |
| 12 | `/api/actions/metrics` | GET | `getActionMetrics()` | Actions |

**Additional method gap:** `actions/[id]/route.ts` exists but only exports `DELETE`. Needs `GET` for `getKineticAction()`.

### Category 2: Middleware Routing Gaps (3 instances)

Route handler files exist on disk but are never reached. The middleware's `handledByRoutes` array doesn't include their prefix, so requests are proxied to the backend at wrong paths instead of being handled by the Next.js route.

| # | Missing Prefix | Existing Handlers | Symptom |
|---|---------------|-------------------|---------|
| 1 | `/api/settings` | `settings/preferences/route.ts`, `settings/email/route.ts`, `settings/account/route.ts`, `settings/data/export/route.ts` | Settings page 404s → Save buttons permanently disabled |
| 2 | `/api/onboarding` | `onboarding/route.ts`, `onboarding/reset/route.ts` | Onboarding endpoints may be unreachable |
| 3 | `/api/user` | `user/profile/route.ts` | Profile endpoint may be unreachable |

### Category 3: Backend Endpoint Issues (6 instances)

The dashboard correctly proxies to the backend, but the backend returns errors. These are NOT route handler issues — they require backend-side fixes.

| # | Endpoint | Status | Affected Page | Notes |
|---|----------|--------|---------------|-------|
| 1 | `GET /api/deals/briefing?hours=18` | 500 | Dashboard | Backend internal error |
| 2 | `GET /api/deals/{id}/anomalies` | 500 | Dashboard (x8 deals) | Backend internal error |
| 3 | `GET /api/deals/{id}/case-file` | 404 | Deal Detail | Backend endpoint not implemented |
| 4 | `GET /api/deals/{id}/materials` | 404 | Deal Detail | Backend endpoint not implemented |
| 5 | `GET /api/deals/{id}/enrichment` | 404 | Deal Detail | Backend endpoint not implemented |
| 6 | `GET /api/deals/{id}/tasks` | 404 | Deal Detail | Backend endpoint not implemented |

### Category 4: Code Bugs (5 instances)

| # | Issue | Page | Root Cause | Severity |
|---|-------|------|-----------|----------|
| 1 | Activity items not clickable | Agent Activity | `#runs-section` has permanent `p-2 -m-2` CSS causing overlap, intercepting pointer events | HIGH |
| 2 | Chat "No response received" fallback | Chat | Strategy 3 done event missing `final_text` field (line 247 of chat/route.ts) | HIGH |
| 3 | Pipeline shows "0 deals" in all stages | Operator HQ | Data mapping issue despite 8 real deals | MEDIUM |
| 4 | "No transitions available (terminal stage)" | Deal Detail | Incorrect terminal stage check for "inbound" deals | LOW |
| 5 | Quarantine operator name ambiguous | Quarantine | No placeholder/help text, `working` state never set | LOW |

### Category 5: Dead Code (1 instance)

| File | Issue |
|------|-------|
| `app/api/actions/quarantine/[actionId]/preview/route.ts` | Queries actions table instead of quarantine table — dead code |

---

## Page-by-Page Status

| Page | URL | Status | Issues |
|------|-----|--------|--------|
| Dashboard | `/dashboard` | PARTIAL | 2 backend 500s (briefing, anomalies) |
| Deals List | `/deals` | OK | Minor: slow initial "0 Deals" flash |
| Deal Detail | `/deals/{id}` | PARTIAL | 4 backend 404s (case-file, materials, enrichment, tasks), capabilities 405, terminal stage bug |
| New Deal | `/deals/new` | OK | Fully functional |
| Actions | `/actions` | BROKEN | 8 missing route handlers, capabilities 405 |
| Quarantine | `/quarantine` | BROKEN | 4 missing route handlers → preview 404, buttons disabled |
| Chat | `/chat` | PARTIAL | Strategy 3 fallback bug (final_text missing) |
| Agent Activity | `/agent/activity` | BROKEN | CSS overlay blocks all clicks |
| Operator HQ | `/hq` | PARTIAL | Pipeline data mapping wrong, capabilities 405 |
| Settings | `/settings` | BROKEN | Route handlers unreachable (middleware gap) |
| Onboarding | `/onboarding` | OK | Functional |

**Summary: 4 OK, 3 PARTIAL, 4 BROKEN**

---

## Remediation Scope

### In-Scope (Dashboard Layer — this deliverable)

1. Create 12 missing route handlers (Category 1)
2. Add GET method to existing `actions/[id]/route.ts`
3. Add `/api/settings`, `/api/onboarding`, `/api/user` to middleware `handledByRoutes` (Category 2)
4. Fix chat Strategy 3 `final_text` (Category 4, #2)
5. Fix activity CSS overlay (Category 4, #1)
6. Fix quarantine UX polish (Category 4, #5)
7. Delete dead preview route (Category 5)
8. Build Surface 17 validator (permanent prevention)
9. Build endpoint liveness probe (permanent prevention)
10. Build Playwright smoke suite (permanent prevention)

### Out-of-Scope (Backend — separate mission required)

1. `GET /api/deals/briefing` → 500 (backend error)
2. `GET /api/deals/{id}/anomalies` → 500 (backend error)
3. `GET /api/deals/{id}/case-file` → 404 (not implemented)
4. `GET /api/deals/{id}/materials` → 404 (not implemented)
5. `GET /api/deals/{id}/enrichment` → 404 (not implemented)
6. `GET /api/deals/{id}/tasks` → 404 (not implemented)
7. Pipeline data mapping in Operator HQ (may be backend data issue)
8. Terminal stage check in Deal Detail (may be backend state issue)

---

## Validation Infrastructure to Build

| Component | Purpose | Enforcement Point |
|-----------|---------|-------------------|
| Surface 17: Route Coverage | Checks api.ts → route handler mapping | `make validate-local` (every session) |
| Endpoint Liveness Probe | Curls every endpoint through dashboard | `make validate-live` (mission completion) |
| Playwright Smoke Suite | Crawls every page for 4xx/5xx + broken UI | `make smoke-test` (mission completion) |
