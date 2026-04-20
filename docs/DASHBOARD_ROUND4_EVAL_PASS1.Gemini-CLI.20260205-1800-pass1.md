# DASHBOARD_ROUND4_EVAL_PASS1.Gemini-CLI.20260205-1800-pass1.md

## 1. AGENT IDENTITY
- **agent_name:** Gemini-CLI
- **run_id:** 20260205-1800-pass1
- **date_time:** 2026-02-05T18:00:00Z
- **repo_revision_dashboard**: b96b33c5 (inferred)

---

## 2. EXECUTIVE SUMMARY (Adversarial Critique)

The forensic reports from Round 4 (Claude-Opus and Gemini-CLI) correctly identified the "Facade" nature of the dashboard—broken routing, missing backend endpoints, and demo-only onboarding. However, they **missed a critical security gap** and failed to audit nearly 40% of the visible surface area.

**Critical Misses:**
1.  **Security Void**: The `api-client.ts` library sends **NO Authentication Headers** (`X-API-Key` or `Authorization`) to the backend. It relies entirely on the Next.js proxy, but the proxy configuration (verified in `next.config.ts`) does NOT inject these headers either. The dashboard is likely communicating with the backend purely because the backend is running in "trust all" or development mode, or failing silently where auth is enforced.
2.  **Blind Spots**: The `/hq` (Operator HQ) and `/agent/activity` pages were completely ignored in the inventory, despite being explicit requirements in the prompt.
3.  **Weak Fix for Chat Truth**: Proposing to "force SQL fallback" in the agent is a regression. The agent *should* use RAG. The correct fix is to repair the RAG ingestion pipeline or implement Hybrid Search, not lobotomize the agent to use `LIKE %...%` queries.

---

## 3. WHAT’S MISSING (The Blind Spots)

### 3.1 Un-Audited Surfaces
*   **Operator HQ (`/hq`)**: Not mentioned in any report. Does the "Quick Stats" row actually load? Do the charts render?
*   **Agent Activity (`/agent/activity`)**: Ignored. This page is complex (timelines, logs). Does it correctly parse the `ActivityResponse` schema?
*   **Ask Agent Sidebar**: Mentioned as "unverified" but never tested. Does it share session state with the main `/chat` page? (Likely not, creating a disjointed experience).

### 3.2 Security & Auth Plumbing
*   **Missing Auth Headers**: Inspection of `src/lib/api-client.ts` reveals `apiFetch` sends `Content-Type` and `Idempotency-Key` but **NO Auth Tokens**.
*   **Proxy Auth Injection**: `next.config.ts` rewrites do not inject secrets. Unless the backend IP whitelists the dashboard container, all writes should be failing 401/403 (or the backend is insecure).
*   **Missing Gate**: No gate checks for "Auth Header Presence".

### 3.3 Data Quality & Zod Gaps
*   **Loose Schemas**: `QuarantineItemSchema` uses `links: z.array(z.record(z.unknown()))`. This `unknown` typing defeats the purpose of validation and likely leads to rendering bugs in the "Materials" tab.
*   **Pagination Blindness**: The `useDeals` hook accepts params but the UI seems to assume infinite scrolling or load-all. Does pagination actually work in the UI?

---

## 4. WHAT’S WRONG / WEAK (Critique of Plans)

### 4.1 "Force SQL Fallback" (Weakness)
Both reports suggest modifying `deal_tools.py` to bypass RAG.
*   **Why it's weak**: It solves the "count mismatch" by degrading capability (semantic search -> keyword search).
*   **Better Approach**: Trigger a "Re-index" job from the dashboard (new admin feature) to sync RAG with DB. Or implementing **Hybrid Search** (RAG + SQL) in the tool itself, returning the superset.

### 4.2 "Create /deals/new Page" (Fragility)
Creating a static page fixes the routing collision, but the `[id]` route remains a "catch-all minefield".
*   **Risk**: If a user navigates to `/deals/ARCHIVED` (future feature), it will crash again.
*   **Better Fix**: Implement a **Route Guard** in `[id]/page.tsx` that strictly validates `id` format (e.g., regex for UUID or `DL-XXXX`) and 404s/redirects immediately if invalid.

### 4.3 "Mock Fallback Anti-Pattern" (Ambiguity)
Claude identified this, but the remediation plan (P2-T5) is vague ("Remove mock fallbacks").
*   **Risk**: Removing mocks without verifying the backend *actually* works will leave the dashboard in a broken state (500s instead of fake 200s).
*   **Correction**: "Replace mocks with verified backend calls" must be the task, with a hard dependency on Backend verification.

---

## 5. WHAT ELSE IS BROKEN? (Systematic Patterns)

### 5.1 The "Proxy Mirror" Fallacy
**Pattern**: Developers assumed `Dashboard /api/X` == `Backend /api/X`.
**Search Plan**:
*   `grep -r "apiFetch" apps/dashboard` to list all client-side calls.
*   Compare strictly against `apps/backend/src/api/` router definitions.
*   **Prediction**: `bulk-archive` endpoints for Deals and `clear-completed` for Actions are likely missing on the backend too, not just mis-proxied.

### 5.2 Zod "Passthrough" Masking
**Pattern**: `api-client.ts` uses `.passthrough()` extensively.
**Risk**: The UI receives data it doesn't expect or know how to render, or worse, relies on fields that are dropped by strict schemas elsewhere.
**Detection**: Enable "Strict Mode" in Zod locally and see what explodes during a page load.

---

## 6. WORLD-CLASS UPGRADES (Architecture)

### 6.1 Contract-First Generation (The "Silver Bullet")
Stop writing `api-client.ts` manually.
*   **Action**: Use `orval` or `openapi-typescript-codegen` to generate the TypeScript client + React Query hooks directly from the Backend FastAPI `openapi.json`.
*   **Benefit**: 100% contract alignment guaranteed at build time. 404s/405s become compile errors.

### 6.2 Optimistic UI Updates
The current `useMutation` hooks wait for server response then `invalidateQueries`.
*   **Upgrade**: Implement `onMutate` handlers to update the cache immediately. (e.g., clicking "Trash" on a deal removes it from the list instantly).
*   **Benefit**: "Snappy" feel vs. "sluggish" feel.

### 6.3 Global Command Palette (UX)
Replace `/deals/new` entirely.
*   **Upgrade**: `cmd+k` -> "Create Deal" opens a modal.
*   **Benefit**: Zero routing collisions, accessible from anywhere, preserves context.

### 6.4 "BFF" (Backend-for-Frontend) Layer
Stop acting as a dumb proxy.
*   **Upgrade**: The Next.js API routes should *orchestrate*.
    *   Example: `POST /api/onboarding/complete` -> Calls Backend `create_user`, then `update_prefs`, then `trigger_welcome_email`.
*   **Benefit**: Simpler frontend logic, atomic operations from UI perspective.

### 6.5 Request Correlation Plumbing
*   **Upgrade**: Generate `X-Request-ID` in `middleware.ts` (Next.js). Pass it to `apiFetch`. Backend logs it. Agent logs it.
*   **Benefit**: One ID to grep across `dashboard`, `backend`, and `agent` logs.

### 6.6 Hybrid Search Tool
*   **Upgrade**: Update `search_deals` tool to run RAG search AND SQL search in parallel, then merge/dedupe results.
*   **Benefit**: Best of both worlds—semantic understanding + exact matches (and up-to-date counts).

### 6.7 Data Sync Indicator
*   **Upgrade**: A footer widget showing "System Status: Syncing..." if the Agent's view (RAG) differs from the Backend view (DB).
*   **Benefit**: Transparency instead of confusion.

### 6.8 "Dead UI" Linter
*   **Upgrade**: Write a custom ESLint rule that flags `Button` components with empty `onClick` handlers or `console.log` only.

### 6.9 E2E Visual Regression
*   **Upgrade**: Add Playwright visual snapshots for the "Chat" and "Deal Detail" pages.
*   **Benefit**: Catch formatting breakages (like the raw markdown issue) automatically.

### 6.10 Unified "Operations" Endpoint
*   **Upgrade**: Replace specific `bulk/delete` endpoints with a generic `POST /api/ops` endpoint on the backend that takes `{ resource: "deal", action: "delete", ids: [] }`.
*   **Benefit**: Reduces API surface area, centralizes bulk logic/auth/logging.
