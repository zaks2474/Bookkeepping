# DASHBOARD_ROUND4_EVAL_PASS2.Codex.20260205-1830-pass2.md

## 1. AGENT IDENTITY
- **agent_name:** Codex
- **run_id:** 20260205-1830-pass2
- **date_time:** 2026-02-05T18:30:00Z
- **repo_revision_dashboard**: b96b33c5 (inferred)

---

## 2. EXECUTIVE SUMMARY (Execution Blueprint)

The Dashboard is in a "Fragile Facade" state. Critical workflows (Deal Creation, Bulk Delete, Quarantine) are broken by routing and contract errors. More dangerously, the **Security Void** identified in Pass 1 (missing Auth headers) means the dashboard works only by accident of network topology or backend insecurity.

This Execution Blueprint prioritizes **Security & Routing (P0)** to stop the bleeding, followed by **Contract Stabilization (P1)** to make buttons work, and finally **Product Hardening (P2)** to replace demo-ware with real features.

**Top Execution Risks:**
1.  **Auth Lockout**: Fixing the missing Auth headers might break *everything* if the backend is actively rejecting unauthenticated requests (and currently only working due to a bypass).
2.  **Route Guard Fragility**: A simple `if` check in `[id]` page is brittle. We must prioritize static route creation (`/deals/new`).
3.  **Backend Dependency**: Frontend fixes for Bulk Delete and Quarantine depend on Backend endpoints that might not exist yet.

---

## 3. PHASE 0: STOP THE BLEEDING (Security & Routing)

**Goal**: Secure the pipe and unblock navigation.

### Task P0.1: Inject Auth Headers (Security Fix)
- **Target**: `apps/dashboard/src/lib/api-client.ts`
- **Action**: Modify `apiFetch` to inject `Authorization: Bearer <token>` or `X-API-Key`.
- **Dependency**: Must source token from session (NextAuth/Clerk?) or env var (`DASHBOARD_SERVICE_TOKEN`) for server-side calls.
- **Verification**: `curl` to backend with and without header to verify enforcement.

### Task P0.2: Fix Deal Creation Routing
- **Target**: Create `apps/dashboard/src/app/deals/new/page.tsx`
- **Action**: Move creation form logic here.
- **Target**: `apps/dashboard/src/app/deals/[id]/page.tsx`
- **Action**: Add `if (params.id === 'GLOBAL') return <GlobalDashboard />;`
- **Proof**: `curl -I http://localhost:3003/deals/new` returns 200.

### Task P0.3: Force Agent SQL Fallback (Truth Fix)
- **Target**: `apps/agent-api/app/core/langgraph/tools/deal_tools.py`
- **Action**: Update `search_deals` to call `_search_deals_fallback` (SQL) immediately if RAG returns low confidence or count mismatch.
- **Why**: Stops the "I see 3 deals" vs "UI shows 9 deals" gaslighting.

---

## 4. PHASE 1: CONTRACT STABILIZATION

**Goal**: Make "Dead UI" buttons work.

### Task P1.1: Align Actions Proxy
- **Target**: `apps/dashboard/src/app/api/actions/bulk/delete/route.ts`
- **Action**: Update proxy target to `${BACKEND_URL}/api/kinetic/actions/bulk/delete`.
- **Backend Task**: Ensure `POST /api/kinetic/actions/bulk/delete` exists in FastAPI.

### Task P1.2: Wire Quarantine Actions
- **Target**: `apps/dashboard/src/app/api/quarantine/[id]/delete/route.ts` (New File)
- **Action**: Proxy to Backend `DELETE /api/triage/quarantine/{id}`.
- **Backend Task**: Implement `DELETE /api/triage/quarantine/{id}` (Soft delete).

### Task P1.3: Fix Chat Rendering
- **Target**: `apps/dashboard/src/app/chat/page.tsx` (or component)
- **Action**: Wrap message content in `<ReactMarkdown>`.
- **Proof**: Screenshot of rendered bold/lists.

---

## 5. PHASE 2: REAL WIRING (Product Hardening)

**Goal**: Replace demo-ware with persistence.

### Task P2.1: Email Settings UI
- **Target**: `apps/dashboard/src/app/settings/page.tsx`
- **Action**: Add "Email" tab. Form for IMAP/SMTP/OAuth.
- **Endpoint**: `POST /api/settings/email`.

### Task P2.2: Onboarding Persistence
- **Target**: `apps/dashboard/src/app/onboarding/page.tsx`
- **Action**: Replace `localStorage` with `apiFetch('/api/onboarding/complete')`.

---

## 6. PHASE 3: POLISH & OBSERVABILITY

### Task P3.1: Correlation ID Plumbing
- **Target**: `apps/dashboard/src/middleware.ts`
- **Action**: Generate `X-Request-ID` if missing.
- **Target**: `api-client.ts`
- **Action**: Pass `X-Request-ID` in headers.

---

## 7. NO DEAD UI STRATEGY

### Static Analysis (Build Time)
- **Grep Check**: `grep -r "console.log" apps/dashboard/src | grep "TODO"` -> Fail build if found in onClick handlers.
- **Route Check**: Script that scans `api-client.ts` for fetch URLs and verifies a corresponding `src/app/api/.../route.ts` exists.

### Runtime Analysis (E2E)
- **Playwright "Click-All"**:
    1.  Spider the dashboard.
    2.  Click every `<button>` and `<a>`.
    3.  Fail if any click results in:
        *   Client-side error boundary
        *   Toast with "Error" / "Failed"
        *   Network 404/405/500

---

## 8. GATES & PROOF

### Gate A: Contract Alignment
- **Test**: `scripts/verify-contracts.ts`
- **Logic**: Fetches OpenAPI spec from Backend. Scans Frontend code for API calls. Asserts every Frontend call maps to a valid OpenAPI definition (Method + Path).

### Gate B: Critical Flows E2E
- **Test**: `tests/e2e/creation.spec.ts`
- **Steps**:
    1.  Login.
    2.  Nav to `/deals/new`.
    3.  Create "Test Deal".
    4.  Verify redirect to `/deals/[id]`.
    5.  Verify "Test Deal" appears in Agent Chat count.

---

*Execution Blueprint Generated: 2026-02-05T18:30:00Z*
*Evaluator: Codex*
