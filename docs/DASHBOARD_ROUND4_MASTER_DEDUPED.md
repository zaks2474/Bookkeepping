# DASHBOARD_ROUND4_MASTER_DEDUPED — Run Index

This file tracks the consolidated master plans for Round 4.

---

## Run Index Entry: 20260205-1900-master

- **Agent:** Codex
- **Run ID:** 20260205-1900-master
- **Date:** 2026-02-05
- **Files:**
  - [Master Deduped Report](./DASHBOARD_ROUND4_MASTER_DEDUPED.Codex.20260205-1900-master.md)
  - [Master JSON](./DASHBOARD_ROUND4_MASTER_DEDUPED.Codex.20260205-1900-master.json)

### Counts
- **Issues (Deduped):** 13
- **Recommendations (Deduped):** 11
- **Redesign Specs:** 2 (Settings, Onboarding)

### Top 15 Priorities (Deduped)
1. **P0** Security: Inject Auth Headers in `api-client.ts` (R4-001)
2. **P0** Routing: Fix `/deals/new` collision (R4-002)
3. **P0** Data Integrity: Force Agent SQL Fallback (R4-003)
4. **P0** Proxy: Align Actions Bulk Delete to `kinetic/actions` (R4-005)
5. **P0** Quarantine: Fix Delete Action (Backend + Proxy) (R4-006)
6. **P0** Onboarding: Wire to Backend Persistence (R4-004)
7. **P1** Settings: Build Email Configuration UI (R4-007)
8. **P1** Chat: Add Markdown Rendering (R4-008)
9. **P1** Quarantine: Fix Preview 404s (R4-009)
10. **P2** Actions: Implement `clear-completed` (R4-010)
11. **P2** Dashboard: Verify Sidebar Actions (R4-011)
12. **P2** Settings: Add Agent/Notif Config (R4-012)
13. **P3** UI: Fix CSS Truncation (R4-013)
14. **Gate**: Contract Verification Script
15. **Gate**: "No Dead UI" E2E Spider

---
### Run Index Entry — Codex — 20260205-1845-p3r4
**Agent**: Codex
**Run ID**: 20260205-1845-p3r4
**Files**:
- `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_MASTER_DEDUPED.Codex.20260205-1845-p3r4.md`
- `/home/zaks/bookkeeping/docs/DASHBOARD_ROUND4_MASTER_DEDUPED.Codex.20260205-1845-p3r4.json`

**Counts**:
- issues total before dedupe: 99
- issues total after dedupe: 50
- recommendations total before dedupe: 72
- recommendations total after dedupe: 19
- ideas total before dedupe: 72
- ideas total after dedupe: 35

**Top 15 Priorities (deduped)**:
1) R4-001 Deal routing slugs captured by /deals/[id]
2) R4-003 Deals bulk archive/delete 405
3) R4-035 Client writes lack X-API-Key
4) R4-017 Quarantine approve/reject wired to actions endpoints
5) R4-019 Quarantine delete missing
6) R4-010 Actions clear-completed/bulk delete 405
7) R4-023 Agent deal count mismatch (RAG vs DB)
8) R4-027 Settings missing email configuration
9) R4-031 Onboarding demo-only (localStorage)
10) R4-029 Settings test connection uses GET /api/chat
11) R4-018 Quarantine preview ID mismatch
12) R4-022 Chat renders raw markdown
13) R4-036 Next API route handlers override rewrites
14) R4-037 Mock fallbacks mask failures
15) R4-028 Settings missing agent config/buy box/notifications

---

