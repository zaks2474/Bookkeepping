# Completion Report: Dashboard Route Coverage Remediation

**Date:** 2026-02-15
**Scope:** System-wide dashboard API route coverage audit, structural remediation, and permanent enforcement
**Trigger:** Post-ET-VALIDATION-001 forensic audit revealed cascading 404 failures across 8 of 12 dashboard pages
**Classification:** Critical, Zero-Defect Deliverable

---

## 1. Root Cause Analysis

### Problem Statement
After executing the ET-VALIDATION-001 roadmap (Email Triage integration), the quarantine UI was broken — preview panels returned 404, bulk operations failed, action buttons were non-functional. Investigation revealed the issue was systemic, not quarantine-specific.

### Root Cause
The dashboard uses a **3-layer proxy architecture**:

```
Backend API (8091) → Next.js Route Handlers → api.ts functions → React Components
```

The middle layer (route handlers) had **zero validation coverage**. No contract surface, no CI gate, no smoke test verified that:
1. Every `api.ts` function calling `/api/X` has a matching `route.ts` file
2. Every route handler prefix is listed in `middleware.ts` `handledByRoutes`
3. Route handlers export the correct HTTP method

### Impact Assessment (Pre-Remediation)
- **8 of 12 dashboard pages** had broken features
- **12 missing route handler files** across quarantine and actions
- **3 middleware routing gaps** (settings, onboarding, user handlers existed but were unreachable)
- **4 code bugs** (chat fallback, CSS overlay, quarantine working state, dead code)
- **50+ console errors** per dashboard visit

---

## 2. Deliverables

### 2.1 System Health Audit Report
**File:** `/home/zaks/bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md`
**Content:** Comprehensive page-by-page audit of all 12 dashboard pages with categorized findings:
- Category 1: Missing route handlers (12 instances)
- Category 2: Middleware routing gaps (3 prefixes)
- Category 3: Backend missing endpoints (6 instances — out of scope, backend work)
- Category 4: Code bugs (5 instances)
- Category 5: Dead code (1 instance)

### 2.2 Surface 17: Dashboard Route Coverage Contract
**Validator:** `tools/infra/validate-surface17.sh`
**Makefile target:** `make validate-surface17`

Three automated checks:

| Check | What It Validates | Entry Count |
|-------|-------------------|-------------|
| CHECK 1: Route Handler Manifest | File exists + correct HTTP method export | 30 entries |
| CHECK 2: Middleware Routing | All handler prefixes in `handledByRoutes` | 13 prefixes |
| CHECK 3: Drift Detection | api.ts endpoints without matching handlers | Dynamic scan |

**Final state:** 43/43 PASS, 0 FAIL, 3 WARN (expected — proxy-only endpoints)

**Registration across all 4 sources (verified by four-way consistency check):**

| Source | Value | Status |
|--------|-------|--------|
| CLAUDE.md | 17 Total | PASS |
| MEMORY.md | All 17 surfaces | PASS |
| validate-contract-surfaces.sh | all 17 contract | PASS |
| INFRASTRUCTURE_MANIFEST.md | 17 Total | PASS |

### 2.3 Endpoint Liveness Probe
**Script:** `tools/infra/validate-endpoint-liveness.sh`
**Makefile target:** `make validate-endpoint-liveness`
**Coverage:** 15 GET endpoints across all dashboard API surface areas
**Pre-flight:** Checks dashboard (3003) + backend (8091) reachability; SKIPs all if either down

### 2.4 Smoke Test Suite
**Script:** `tools/infra/smoke-test.sh`
**Makefile target:** `make smoke-test`
**Coverage:** 9 dashboard pages with HTTP status + critical API endpoint checks per page

---

## 3. Route Handlers Created

### 3.1 New Files (10)

| # | File | Method | Backend Proxy Path | Timeout |
|---|------|--------|-------------------|---------|
| 1 | `api/quarantine/[id]/route.ts` | GET | `/api/quarantine/${id}` | default |
| 2 | `api/quarantine/bulk-process/route.ts` | POST | `/api/quarantine/bulk-process` | 60s |
| 3 | `api/quarantine/bulk-delete/route.ts` | POST | `/api/quarantine/bulk-delete` | 60s |
| 4 | `api/quarantine/[id]/undo-approve/route.ts` | POST | `/api/quarantine/${id}/undo-approve` | 30s |
| 5 | `api/actions/capabilities/route.ts` | GET | `/api/actions/capabilities` | default |
| 6 | `api/actions/[id]/approve/route.ts` | POST | `/api/actions/${actionId}/approve` | 30s |
| 7 | `api/actions/[id]/cancel/route.ts` | POST | `/api/actions/${actionId}/cancel` | 30s |
| 8 | `api/actions/[id]/retry/route.ts` | POST | `/api/actions/${actionId}/retry` | 30s |
| 9 | `api/actions/[id]/update/route.ts` | POST | `/api/actions/${actionId}/update` | 30s |
| 10 | `api/actions/metrics/route.ts` | GET | `/api/actions/metrics` | default |

All route handlers follow the established pattern:
- Import `backendFetch` from `@/lib/backend-fetch`
- Proxy request body and return response text with original status code
- Catch block returns JSON `{ error: 'backend_unavailable', message: '...' }` with status 502
- Dynamic route params use `{ params }: { params: Promise<{ id: string }> }` (Next.js 15 async params)

### 3.2 Method Addition (1)

| File | Change |
|------|--------|
| `api/actions/[id]/route.ts` | Added `GET` export (previously only exported DELETE) |

### 3.3 Middleware Routing Fix (1 file, 3 prefixes)

| File | Change |
|------|--------|
| `middleware.ts` | Added `/api/settings/`, `/api/onboarding`, `/api/user` to `handledByRoutes` array |

**Before:** Settings, onboarding, and user route handler files existed on disk but were unreachable — middleware proxied requests to backend instead of invoking the handlers.
**After:** All three prefix groups correctly route to their Next.js handlers.

---

## 4. Bug Fixes

### 4.1 Chat Fallback `final_text` (HIGH severity)

| Aspect | Detail |
|--------|--------|
| File | `app/api/chat/route.ts` line 247 |
| Symptom | Chat shows "No response received" when agent unavailable |
| Root Cause | Strategy 3 (fallback) done event was missing `final_text` field. Client (`chat/page.tsx:575`) uses `final_text` from done event as primary content source. |
| Fix | Added `final_text: helpfulResponse` to the done event JSON |

### 4.2 Activity CSS Overlay (HIGH severity)

| Aspect | Detail |
|--------|--------|
| File | `app/agent/activity/page.tsx` line 416 |
| Symptom | Activity items not clickable in certain areas |
| Root Cause | `#runs-section` had permanent `p-2 -m-2` CSS classes creating an invisible padding overlay that intercepted pointer events |
| Fix | Moved `p-2 -m-2` from permanent to conditional — only applied during highlight state (`highlightedStat === 'runs'`) |

### 4.3 Quarantine `working` State (LOW severity)

| Aspect | Detail |
|--------|--------|
| File | `app/quarantine/page.tsx` line 135 → 168 |
| Symptom | Operator name input and action buttons never disabled during operations |
| Root Cause | `const [working, setWorking] = useState(false)` — `setWorking` was never called anywhere. The state was permanently `false`. |
| Fix | Replaced with derived value: `const working = approving \|\| rejecting \|\| escalating \|\| bulkProcessing \|\| deleting` placed after all individual state declarations |

### 4.4 Dead Code Removal

| Aspect | Detail |
|--------|--------|
| File | `app/api/actions/quarantine/[actionId]/preview/route.ts` |
| Issue | Queried the actions table instead of quarantine table. Nothing in the codebase consumed this endpoint. |
| Action | Deleted file and empty parent directories |

---

## 5. Infrastructure Fixes

### 5.1 Boot Diagnostics 4-Session HALT Resolved

| Source | Before | After |
|--------|--------|-------|
| `validate-contract-surfaces.sh` line 3 | "all 16 contract surfaces" | "all 17 contract surfaces" |
| `INFRASTRUCTURE_MANIFEST.md` line 1019 | "16 Total" | "17 Total" |

**Root cause:** Boot CHECK 2 four-way consistency check used case-sensitive regex `'all \K\d+(?= contract)'` which matched the lowercase "all" in the validator comment (stale at 16). CLAUDE.md and MEMORY.md were already at 17.

### 5.2 Surface 17 Validator Manifest Corrections

The validator was initially created with phantom entries that didn't match the actual codebase:

| Manifest Entry (Wrong) | Actual Codebase | Fix |
|------------------------|-----------------|-----|
| `agent/runs/route.ts` (GET) | `agent/activity/route.ts` (GET) | Updated path |
| `agent/state/route.ts` (GET) | Does not exist (not in api.ts) | Removed |
| `agent/invoke/route.ts` (POST) | Does not exist (not in api.ts) | Removed |
| `deferred-actions/[id]/execute/route.ts` (POST) | Does not exist (not in api.ts) | Removed |
| `settings/preferences` PUT | Actually exports PATCH | Fixed method |
| `settings/email` PUT | Actually exports POST | Fixed method |
| `onboarding/status/route.ts` | Actually at `onboarding/route.ts` | Fixed path |
| (missing) | `deferred-actions/due/route.ts` (GET) | Added |

---

## 6. Verification Results

### 6.1 Automated Gates

| Gate | Command | Result |
|------|---------|--------|
| Surface 17 | `make validate-surface17` | **43/43 PASS**, 0 FAIL, 3 WARN |
| Four-way consistency | `bash tools/infra/validate-surface-count-consistency.sh` | **PASS** (17 everywhere) |
| validate-local | `make validate-local` | **PASS** |
| TypeScript | `npx tsc --noEmit` | **0 errors** |
| Boot diagnostics | Session hook | **ALL CLEAR** (6/6 PASS, 0 WARN, 0 FAIL) |

### 6.2 Surface 17 WARN Analysis (3 expected, not actionable)

| WARN | Explanation |
|------|-------------|
| `/api/actions` | List endpoint — proxied by middleware directly to backend, no handler needed |
| `/api/quarantine` | List endpoint — same as above |
| `/api/agent/api/v1/chatbot/sentiment/{param}` | Routed via chatbot proxy path in middleware (lines 84-88) |

### 6.3 File Ownership

All files under `apps/dashboard/src/app/api/` owned by `zaks:zaks` — verified.

---

## 7. Files Modified/Created Summary

### Created (13 files)
```
apps/dashboard/src/app/api/quarantine/[id]/route.ts
apps/dashboard/src/app/api/quarantine/bulk-process/route.ts
apps/dashboard/src/app/api/quarantine/bulk-delete/route.ts
apps/dashboard/src/app/api/quarantine/[id]/undo-approve/route.ts
apps/dashboard/src/app/api/actions/capabilities/route.ts
apps/dashboard/src/app/api/actions/[id]/approve/route.ts
apps/dashboard/src/app/api/actions/[id]/cancel/route.ts
apps/dashboard/src/app/api/actions/[id]/retry/route.ts
apps/dashboard/src/app/api/actions/[id]/update/route.ts
apps/dashboard/src/app/api/actions/metrics/route.ts
tools/infra/validate-surface17.sh
tools/infra/validate-endpoint-liveness.sh
bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md
```

### Modified (11 files)
```
apps/dashboard/src/app/api/actions/[id]/route.ts          — added GET export
apps/dashboard/src/middleware.ts                           — 3 new handledByRoutes prefixes
apps/dashboard/src/app/api/chat/route.ts                  — final_text in fallback done event
apps/dashboard/src/app/agent/activity/page.tsx             — conditional CSS p-2 -m-2
apps/dashboard/src/app/quarantine/page.tsx                 — derived working state
tools/infra/validate-contract-surfaces.sh                  — "all 17", S17 check block
tools/infra/validate-surface-count-consistency.sh          — EXPECTED=17, regex update
CLAUDE.md                                                  — 17 Total, S17 row
.claude/rules/contract-surfaces.md                         — S17 definition
INFRASTRUCTURE_MANIFEST.md                                 — 17 Total, S17 line
Makefile                                                   — validate-surface17, validate-endpoint-liveness, smoke-test targets
```

### Deleted (1 file)
```
apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts  — dead code
```

---

## 8. QA Verification Checklist

For the QA verifier, these are the recommended verification gates:

### Structural (offline, no services needed)
- [ ] `make validate-local` — PASS
- [ ] `npx tsc --noEmit` (in apps/dashboard) — 0 errors
- [ ] `make validate-surface17` — 43/43 PASS, 0 FAIL
- [ ] `bash tools/infra/validate-surface-count-consistency.sh` — PASS (17 everywhere)
- [ ] `make validate-contract-surfaces` — all 17 surfaces pass

### Route Handler Spot Checks (file existence + pattern compliance)
- [ ] Each of the 10 new route files imports `backendFetch` from `@/lib/backend-fetch`
- [ ] Each has try/catch with 502 JSON error response
- [ ] `actions/[id]/route.ts` exports both GET and DELETE
- [ ] `middleware.ts` handledByRoutes contains `/api/settings/`, `/api/onboarding`, `/api/user`
- [ ] Dead file `actions/quarantine/[actionId]/preview/route.ts` does not exist

### Bug Fix Verification
- [ ] `chat/route.ts` Strategy 3 done event contains `final_text: helpfulResponse`
- [ ] `agent/activity/page.tsx` `#runs-section` div has NO permanent `p-2 -m-2` (only conditional)
- [ ] `quarantine/page.tsx` has `const working = approving || rejecting || escalating || bulkProcessing || deleting` (not useState)
- [ ] `quarantine/page.tsx` does NOT contain `setWorking`

### Runtime (requires dashboard + backend running)
- [ ] `make validate-endpoint-liveness` — all covered endpoints return JSON (not HTML 404)
- [ ] `make smoke-test` — all pages accessible
- [ ] Quarantine page: click item → preview panel loads (not 404)
- [ ] Quarantine page: approve/reject/escalate buttons disable during operation
- [ ] Actions page: capabilities dropdown loads (not empty)
- [ ] Activity page: items are clickable in the runs section area
- [ ] Chat page: when agent unavailable, fallback response text appears (not "No response received")

### Infrastructure
- [ ] All new files owned by `zaks:zaks` (not root)
- [ ] Boot diagnostics: ALL CLEAR (6/6 PASS)
- [ ] CHANGES.md updated with full remediation entry

---

## 9. Scope Exclusions (Documented, Not Skipped)

The following items were identified in the audit but explicitly excluded from this remediation scope:

| Item | Reason |
|------|--------|
| Category 3: 6 backend-missing endpoints (deals enrichment, deals tasks, etc.) | Requires backend development — separate mission |
| Category 4 #3: Pipeline shows "0 deals" in all stages | Data mapping issue in pipeline page — requires investigation of stage data structure |
| Category 4 #4: "No transitions available (terminal stage)" | Deal detail transition logic — requires backend FSM analysis |

These are documented in the health audit report for future remediation.

---

**Report prepared by:** Claude Opus 4.6
**Verification gate count:** 22 checkable items
**Confidence level:** HIGH — all automated gates pass, all file operations verified
