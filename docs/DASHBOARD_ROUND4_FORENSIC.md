# DASHBOARD_ROUND4_FORENSIC — Run Index

This file tracks all Round-4 Dashboard Forensic & Product Hardening passes for the ZakOps Dashboard.

---

## Run Index

### PASS 1: 20260205-1710-1a20a2

**Agent**: Claude-Opus
**Run ID**: 20260205-1710-1a20a2
**Timestamp**: 2026-02-05T17:10:00Z
**Dashboard Revision**: b96b33c5
**Backend Revision**: 2a68de17

**Files**:
- Forensic Report: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_FORENSIC.Claude-Opus.20260205-1710-1a20a2.md`
- Forensic JSON: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_FORENSIC.Claude-Opus.20260205-1710-1a20a2.json`
- Remediation Plan: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_PLAN.Claude-Opus.20260205-1710-1a20a2.md`
- Remediation JSON: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_PLAN.Claude-Opus.20260205-1710-1a20a2.json`

**Summary Statistics**:
- Screenshots Analyzed: 11
- Total Limitations Identified: 17
- P0 (Critical): 4
- P1 (High): 6
- P2 (Medium): 5
- P3 (Low): 2

**Key P0 Issues**:
1. DL-001: Deal routing bug (`/deals/GLOBAL`, `/deals/new` treated as deal IDs)
2. DL-002: Data integrity mismatch (agent reports 3 deals vs UI 9 deals)
3. DL-003: Onboarding demo-only (localStorage, no backend)
4. DL-004: Missing email configuration UI

**Hard Gates Defined**:
- Gate A: Contract Verification (OpenAPI vs frontend)
- Gate B: No Dead UI (E2E covers every button)
- Gate C: E2E Coverage (CI green)
- Gate D: Observability (correlation_id end-to-end)

**Remediation Phases**:
- Phase 0: Critical Path Unblock (P0)
- Phase 1: API Contract Alignment (P1)
- Phase 2: UX Hardening & Technical Debt (P2)
- Phase 3: Polish & Observability (P3)

**Evidence Location**: `/mnt/c/Users/mzsai/Downloads/Dashboard Screenshots/`

---

*Index maintained by ROUND4-FORENSIC missions*
### Run Index Entry — Codex — 20260205-1723-r4d1
**Agent**: Codex
**Run ID**: 20260205-1723-r4d1
**Dashboard Revision**: b96b33c5
**Backend Revision**: 2a68de17

**Files**:
- Forensic Report: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_FORENSIC.Codex.20260205-1723-r4d1.md`
- Forensic JSON: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_FORENSIC.Codex.20260205-1723-r4d1.json`
- Remediation Plan: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_PLAN.Codex.20260205-1723-r4d1.md`
- Remediation JSON: `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_PLAN.Codex.20260205-1723-r4d1.json`

**Top 10 Limitations Found**:
1) Reserved slugs in `/deals/[id]` cause `/deals/new` and `/deals/GLOBAL` to 404.
2) Bulk archive used in UI but backend lacks `/api/deals/bulk-archive`.
3) UI write calls via `apiFetch` omit X-API-Key.
4) Quarantine approve/reject wired to actions endpoints, not `/api/quarantine/{id}/process`.
5) Quarantine preview uses `/api/actions/{id}` causing “Preview not found”.
6) Quarantine delete uses `/api/quarantine/{id}/delete` which is not implemented.
7) Actions “clear completed” endpoint missing; 405 Method Not Allowed.
8) Actions capabilities endpoint conflict (501 in orchestration vs router).
9) Onboarding email + agent demo are mock/localStorage only.
10) Chat rendering plain text; no markdown, deal count mismatch via RAG.

**Top 10 Recommended Fixes**:
1) Add `/deals/new` route or guard slugs in `/deals/[id]`.
2) Implement `/api/deals/bulk-archive` or change UI to single-item loop.
3) Route all writes through Next API routes or inject API key in `apiFetch`.
4) Wire quarantine approve/reject to `/api/quarantine/{id}/process` (or implement execute endpoints).
5) Fix quarantine preview to `/api/quarantine/{id}` and add preview endpoint if missing.
6) Implement `/api/quarantine/{id}/delete` or remove delete UI with explanation.
7) Implement actions clear-completed + bulk endpoints (or hide buttons).
8) Resolve actions capabilities conflict and ensure consistent handler.
9) Replace onboarding mocks with real email OAuth + persisted profile.
10) Add markdown rendering in chat + align agent deal count with DB.

**Top 5 Redesign Recommendations (Settings + Onboarding)**:
1) Settings: multi-section layout with Email Integration, Agent Config, Notifications, Data & Privacy.
2) Settings: connected accounts table with health checks + last sync timestamps.
3) Onboarding: real profile capture persisted to backend (no localStorage).
4) Onboarding: “Meet Your Agent” runs a real workflow (create test deal + approve).
5) Onboarding: progress saved server-side with resume + validation checkpoints.

---

## Run Index Entry: 20260205-1055-gemini

- **Agent:** Gemini-CLI
- **Run ID:** 20260205-1055-gemini
- **Date:** 2026-02-05
- **Files:**
  - [Forensic Report](./DASHBOARD_ROUND4_FORENSIC.Gemini-CLI.20260205-1055-gemini.md)
  - [Remediation Plan](./DASHBOARD_ROUND4_PLAN.Gemini-CLI.20260205-1055-gemini.md)

### Top 10 Limitations Found
1. **P0** `/deals/new` and `/deals/GLOBAL` broken (captured by `[id]` route).
2. **P0** Bulk Delete Actions returns 405 (Proxy mismatch: `/api/actions` vs `/api/kinetic/actions`).
3. **P0** Quarantine Delete returns 404 (Missing proxy + backend endpoint).
4. **P0** Chat Deal Count Mismatch (Agent uses stale RAG vs UI uses fresh DB).
5. **P1** Settings page missing Email Configuration.
6. **P1** Onboarding is client-side demo-ware.
7. **P1** Chat displays raw markdown.
8. **P2** Missing backend endpoints for Action archiving/clearing.
9. **P2** Dashboard "Ask Agent" sidebar actions unverified.
10. **P2** Inconsistent styling in Settings vs rest of app.

### Top 10 Recommended Fixes
1. **Create** `src/app/deals/new/page.tsx` for deal creation.
2. **Update** Action Proxy routes to target `/api/kinetic/actions`.
3. **Implement** `DELETE /api/triage/quarantine/{id}` in backend + proxy.
4. **Force** SQL search fallback in Agent `search_deals` tool.
5. **Add** `react-markdown` to Chat component.
6. **Implement** Email Settings tab in Settings page.
7. **Wire** Onboarding to backend persistence.
8. **Guard** `/deals/[id]` against "GLOBAL" slug.
9. **Implement** missing Action management endpoints in backend.
10. **Align** frontend API client paths with validated backend contracts.

### Top 5 Redesign Recommendations
1. **Modal-First Creation**: Use global Command-K for creating deals instead of pages.
2. **Unified Search**: Merge RAG and SQL search results at API level.
3. **Draft Deals**: Use temporary IDs for new deals (`/deals/draft-123`).
4. **Operations API**: Unified `POST /api/ops` for all bulk actions.
5. **Context Injection**: Inject current UI view context (visible deal IDs) into Agent prompt.
