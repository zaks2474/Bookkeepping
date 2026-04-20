# DASHBOARD_ROUND4_EVAL_MASTER — Run Index

This file tracks the evaluation passes for the Dashboard Round 4 audit.

---

## Run Index

### PASS 1: Gemini-CLI (20260205-1800-pass1)

**Agent**: Gemini-CLI
**Run ID**: 20260205-1800-pass1
**Timestamp**: 2026-02-05T18:00:00Z
**Report Path**: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_EVAL_PASS1.Gemini-CLI.20260205-1800-pass1.md`

**Top 10 "Missing" Items:**
1. **Security**: No Auth Headers in `api-client.ts`.
2. **Surface**: `/hq` (Operator HQ) page ignored.
3. **Surface**: `/agent/activity` page ignored.
4. **Surface**: Ask Agent Sidebar unverified.
5. **Surface**: Mobile/Responsive behavior check.
6. **Backend**: explicit verification of backend endpoints (vs assumed missing).
7. **Config**: `next.config.ts` rewrite auth injection check.
8. **Schema**: Zod schema weak typing (`unknown` records).
9. **UX**: Pagination functionality verification.
10. **Gate**: "Auth Header Presence" gate.

**Top 10 "Weaknesses" (Critique):**
1. **Force SQL Fallback**: Band-aid solution; prefer Hybrid Search or Re-index.
2. **Static `/deals/new`**: Vulnerable to future routing collisions; needs Route Guard.
3. **Mock Fallback Removal**: Vague plan; needs "Replace with Verified Backend".
4. **Data Integrity**: Root cause analysis stopped at "RAG vs SQL"; didn't propose sync mechanism.
5. **Onboarding**: "Wire to backend" is vague; backend endpoint might not exist.
6. **Bulk Delete**: Assumed backend 405 means "wrong method" only; could be missing endpoint.
7. **Chat UX**: Markdown fix is cosmetic; doesn't address structured data rendering.
8. **Settings**: Email config plan assumes backend readiness.
9. **Quarantine**: Delete fix assumes backend supports hard delete (might be soft).
10. **Evidence**: Screen 10 (Dashboard) dismissed as "working" without checking interaction.

**Top 10 Upgrade Ideas:**
1. **Generated Client**: `orval`/`kubb` from OpenAPI (Contract-First).
2. **Optimistic UI**: `onMutate` cache updates for snappy feel.
3. **Command Palette**: `cmd+k` instead of navigation pages.
4. **BFF Layer**: Next.js API routes as orchestrators, not proxies.
5. **Correlation ID**: `X-Request-ID` from middleware to DB.
6. **Hybrid Search**: Agent tool combines RAG + SQL results.
7. **Sync Indicator**: UI widget showing RAG freshness status.
8. **Dead UI Linter**: ESLint rule for empty handlers.
9. **Visual Regression**: Playwright snapshots for layout breaks.
10. **Unified Ops API**: Generic `POST /api/ops` for bulk actions.

---

### PASS 2: Codex (20260205-1830-pass2)

**Agent**: Codex
**Run ID**: 20260205-1830-pass2
**Timestamp**: 2026-02-05T18:30:00Z
**Report Path**: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_EVAL_PASS2.Codex.20260205-1830-pass2.md`

**Top 10 Execution Risks:**
1. **Auth Lockout**: Injecting auth headers might reveal broken backend auth config.
2. **Backend Sync**: Frontend fixes depend on backend endpoints that might need simultaneous deploy.
3. **Route Precedence**: `/deals/new` static page must strictly precede `[id]` in filesystem build.
4. **Data Loss**: Quarantine "delete" might need soft-delete confirmation UI.
5. **Regression**: Removing mock fallbacks could break demos if backend is unstable.
6. **Performance**: Hybrid search (SQL+RAG) might be slow without optimization.
7. **Migration**: Persisting onboarding might require DB schema updates for user prefs.
8. **Test Flake**: E2E tests for async agent operations (chat response) are historically flaky.
9. **Secrets**: Storing OAuth tokens requires encryption key management.
10. **Mobile**: Layouts for new Settings/Onboarding pages might break on mobile.

**Top 10 High-Leverage Tests/Gates:**
1. **Gate A**: `verify-contracts.ts` (Static analysis of frontend calls vs OpenAPI).
2. **Gate B**: E2E "Click-All" spider for Dead UI detection.
3. **Test**: `curl` check for 401/403 when Auth header missing (Security regression).
4. **Test**: Deal Creation flow (New -> Submit -> Detail).
5. **Test**: Agent Deal Count accuracy check (DB vs Chat).
6. **Test**: Quarantine action lifecycle (List -> Approve -> Deal Created).
7. **Test**: Markdown rendering snapshot.
8. **Test**: Settings persistence (Save -> Reload -> Verify).
9. **Gate**: `grep` check for `console.log("TODO")` in handlers.
10. **Log Check**: Correlation ID presence in backend logs for dashboard actions.

**Recommended Phase Order:**
1. **Phase 0**: Security (Auth Headers) & Routing (`/deals/new`).
2. **Phase 1**: Contract Stabilization (Quarantine/Actions Proxies).
3. **Phase 2**: Product Hardening (Email Settings, Onboarding Persistence).
4. **Phase 3**: Polish & Observability.

---### Run Index Entry — Codex — 20260205-1842-p2r4
**Agent**: Codex
**Run ID**: 20260205-1842-p2r4
**File**: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_EVAL_PASS2.Codex.20260205-1842-p2r4.md`

**Top 10 Execution Risks**:
1) UI writes fail in prod due to missing X‑API‑Key injection.
2) Next API `route.ts` overrides rewrites and drops DELETE/PATCH methods → 405.
3) Quarantine canonical path mismatch (`/api/quarantine` vs `/api/triage/quarantine`).
4) Bulk endpoints not implemented but UI wired → 404/405.
5) Actions backend lacks execute/cancel/retry endpoints used by UI.
6) Settings/Onboarding persist to localStorage only; changes lost on reload.
7) Chat deal count mismatch persists (RAG vs DB).
8) Preview uses action_id but quarantine items use different IDs.
9) Test Connection uses GET `/api/chat` which only supports POST.
10) No correlation ID propagation → debugging impossible.

**Top 10 High‑Leverage Tests/Gates**:
1) Contract Gate: UI route map vs backend route list (CI fail on mismatch).
2) Method Matrix Gate: verify UI methods match Next API route exports.
3) Playwright: `/deals/new` + `/deals/GLOBAL` routing.
4) Playwright: bulk delete/clear completed actions works.
5) Playwright: quarantine approve/reject/preview works.
6) Auth Gate: writes 401 without API key, 200 with key.
7) No Dead UI Gate: static scan + runtime click‑through.
8) SSE Gate: chat streams tokens + reconnects.
9) Count Match Gate: agent search count == `/api/deals` count.
10) Observability Gate: correlation_id appears in UI + backend logs.

**Recommended Phase Order**:
1) P0 — stop‑the‑bleeding (routing + method mismatches + quarantine wiring)
2) P1 — contract stabilization (route diff + bulk endpoints + action ops)
3) P2 — onboarding + settings real wiring
4) P3 — polish + observability

---

### PASS 3: Claude-Opus (20260205-1855-p3) — MASTER CONSOLIDATION

**Agent**: Claude-Opus
**Run ID**: 20260205-1855-p3
**Timestamp**: 2026-02-05T18:55:00Z
**Report Path**: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_MASTER_DEDUPED.Claude-Opus.20260205-1855-p3.md`

**Consolidation Statistics:**
| Category | Raw Count | Deduped Count | Dedup Rate |
|----------|-----------|---------------|------------|
| Limitations | 73 | 38 | 48% |
| Recommendations | 89 | 42 | 53% |
| Upgrade Ideas | 47 | 25 | 47% |

**Source Reports Merged:**
- FORENSIC: Claude-Opus, Codex, Gemini-CLI
- PASS 1: Claude-Opus, Gemini-CLI, Codex
- PASS 2: Claude-Opus, Codex

**Deliverables:**
- A) Master Deduped Limitations Registry (38 unique items, P0-P3 prioritized)
- B) Master Deduped Recommendations Catalog (42 unique items)
- C) Settings Redesign Spec (6 sections: Provider, Email, Agent, Notifications, Data, Appearance)
- D) Onboarding Redesign Spec (4 steps with backend persistence, live agent demo)

**Top 7 P0 Limitations (Deduped):**
1. `DL-001`: Deal routing crash (`/deals/new`, `/deals/GLOBAL`)
2. `DL-002`: Missing `POST /api/deals` endpoint
3. `DL-003`: Quarantine delete 404
4. `DL-004`: Actions bulk delete 405
5. `DL-005`: Client writes missing X-API-Key
6. `DL-006`: Chat deal count mismatch (RAG vs DB)
7. `DL-007`: Onboarding demo-only (localStorage)

**6 Hard Gates Defined:**
- Gate A: Contract (OpenAPI vs Frontend)
- Gate B: No Dead UI (ESLint + Playwright)
- Gate C: E2E Suite
- Gate D: Observability (correlation_id)
- Gate E: Security (auth headers)
- Gate F: Method Matrix (UI methods vs route exports)

---

