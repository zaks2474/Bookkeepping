# DASHBOARD_ROUND4_PLAN.Gemini-CLI.20260205-1055-gemini.md

## 1. AGENT IDENTITY
- **agent_name**: Gemini-CLI
- **run_id**: 20260205-1055-gemini
- **date_time**: 2026-02-05T10:55:00Z

## 2. EXECUTIVE SUMMARY
**Goal**: Stabilize the Dashboard Facade and Ground the Agent.
We will execute a 4-phase plan to fix critical routing collisions, align API proxies with the actual backend contract, and force the agent to use the canonical database as its source of truth.

---

## 3. PHASE 1: CRITICAL ROUTING & PROXIES (P0)

**Objective**: Ensure basic navigation and actions work without 404/405 errors.

### 3.1 Fix Deal Creation Routing
- **Task**: Create `src/app/deals/new/page.tsx`.
- **Implementation**: Move deal creation form logic from any modal/component into this page.
- **Verification**: `curl -I http://localhost:3003/deals/new` returns 200.

### 3.2 Align Actions Bulk Delete Proxy
- **Task**: Modify `src/app/api/actions/bulk/delete/route.ts`.
- **Change**: Update `fetch` URL to `${BACKEND_URL}/api/kinetic/actions/bulk/delete`.
- **Backend Check**: Verify backend endpoint exists. If not, implement `POST /api/kinetic/actions/bulk/delete`.

### 3.3 Quarantine Proxy Handlers
- **Task**: Create `src/app/api/quarantine/[id]/delete/route.ts`.
- **Implementation**: Proxy DELETE requests to `${BACKEND_URL}/api/triage/quarantine/{id}`.
- **Task**: Create `src/app/api/quarantine/[id]/approve/route.ts`.
- **Implementation**: Proxy POST requests to `${BACKEND_URL}/api/triage/quarantine/{id}/approve`.

---

## 4. PHASE 2: CHAT TRUTH & UX (P0/P1)

**Objective**: Ensure Agent sees the same data as the User.

### 4.1 Force Agent SQL Fallback
- **Task**: Modify `apps/agent-api/app/core/langgraph/tools/deal_tools.py`.
- **Logic**: In `search_deals` function, bypass RAG call and directly invoke `_search_deals_fallback` (SQL search) to guarantee data consistency with the Dashboard.

### 4.2 Fix Markdown Rendering
- **Task**: Update Dashboard Chat Component.
- **Implementation**: Import `react-markdown` and wrap agent responses.

---

## 5. PHASE 3: PRODUCT HARDENING (P1)

**Objective**: Replace "Demo-Ware" with functional features.

### 5.1 Email Settings UI
- **Task**: Update `src/app/settings/page.tsx`.
- **Add**: "Email Integration" section.
- **Fields**: IMAP Host, SMTP Host, Username, Password (masked).
- **Action**: "Test Connection" button calling `POST /api/settings/email/test`.

### 5.2 Onboarding Persistence
- **Task**: Update `src/app/onboarding/page.tsx`.
- **Logic**: Replace `localStorage` calls with `await apiFetch('/api/user/onboarding', { method: 'POST', body: ... })`.

---

## 6. GATES

### Gate A: Contract Gate
- Automated script to verify `GET /api/deals` returns same count as Agent `search_deals`.

### Gate B: E2E Gate
- Playwright test: Navigate to `/deals/new` -> Verify "Create Deal" header exists.

### Gate C: Observability Gate
- Verify `X-Correlation-ID` header presence in `src/lib/api-client.ts` headers.

---

## 7. BETTER IDEAS (APPENDIX)

**Idea 1: Global "Quick Action" Fab**
Instead of `/deals/new` page, implement a floating action button (FAB) available on all pages that opens a `CreateDealModal`. This avoids routing complexity entirely.

**Idea 2: Unified "Sync" Status**
Add a "Data Sync" indicator in the Dashboard footer. If RAG index count != DB count, show "Indexing..." or "Sync Error". This makes the "Split-Brain" transparent to the user.
