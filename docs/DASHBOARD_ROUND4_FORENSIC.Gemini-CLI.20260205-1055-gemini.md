# DASHBOARD_ROUND4_FORENSIC.Gemini-CLI.20260205-1055-gemini.md

## 1. AGENT IDENTITY
- **agent_name**: Gemini-CLI
- **run_id**: 20260205-1055-gemini
- **date_time**: 2026-02-05T10:55:00Z
- **repo_revision_dashboard**: unknown
- **repo_revision_backend**: unknown
- **repo_revision_agent_api**: unknown

## 2. EXECUTIVE SUMMARY
**Verdict: CRITICAL ROUTING & CONTRACT FAILURES (P0)**

The ZakOps Dashboard is functionally broken for deal creation and bulk operations due to two systemic failures: **Catch-All Routing Priority** and **Proxy Path Misalignment**.

1.  **Routing Blockade**: The dynamic route `src/app/deals/[id]/page.tsx` aggressively captures *all* sub-paths, rendering `/deals/new` (Creation) and `/deals/GLOBAL` (Scope) inaccessible.
2.  **Proxy Hallucination**: The Next.js API layer assumes a 1:1 mapping with the backend (`/api/actions` -> `/api/actions`). The actual backend contract is `/api/kinetic/actions`. This causes 404s/405s for all Action-related bulk operations.
3.  **Missing Surfaces**: Quarantine management is effectively read-only due to missing proxy handlers for `DELETE`. Onboarding is client-side "demo-ware" that does not persist configuration.

**Root Cause**: The frontend was built against an assumed API surface area that does not match the actual FastAPI backend implementation.

---

## 3. EVIDENCE REVIEW

| # | Screenshot Evidence | Observed Route | Root Cause |
|---|---------------------|----------------|------------|
| 1 | "Deal not found" | `/deals/GLOBAL` | `[id]` route captures "GLOBAL". Backend returns 404 for deal ID "GLOBAL". |
| 11| "Failed to load deal" | `/deals/new` | `[id]` route captures "new". Backend returns 404 for deal ID "new". |
| 2 | "Method Not Allowed" | `/deals` (Bulk Delete) | UI sends DELETE (or POST) to a proxy that forwards to a non-existent backend path or uses wrong method. |
| 7 | Quarantine Delete Fail | `/quarantine` | UI calls `deleteQuarantineItem` -> `POST /api/quarantine/{id}/delete`. No proxy handler exists. Fallback rewrite targets `/api/triage/quarantine/{id}/delete` (Missing on Backend). |
| 6 | Agent Deal Count (3 vs 9) | `/chat` | Agent tool `search_deals` calls RAG (Port 8052). UI calls Backend SQL (Port 8091). RAG index is stale. |

---

## 4. DASHBOARD SURFACE INVENTORY

### Pages & Status
- **`/dashboard`**: **PARTIAL**. Sidebar actions unverified.
- **`/deals`**: **OK** (List view).
- **`/deals/[id]`**: **BROKEN** for special slugs ("new", "GLOBAL").
- **`/actions`**: **BROKEN** (Bulk delete fails).
- **`/quarantine`**: **BROKEN** (Actions fail).
- **`/chat`**: **POOR** (Raw markdown, split-brain data).
- **`/settings`**: **INCOMPLETE** (No email config).
- **`/onboarding`**: **FAKE** (Client-side only).

### Proxy Layer (`src/app/api/`)
- `actions/bulk/delete/route.ts`: **MISCONFIGURED**. Targets `/api/actions/bulk/delete`. Should be `/api/kinetic/actions/bulk/delete`.
- `quarantine/*`: **MISSING**. No explicit handlers for delete/approve. Relies on `next.config.ts` rewrites which are insufficient for complex path mapping.

---

## 5. LIMITATIONS REGISTRY (DEDUPED)

| ID | Severity | Limitation | Fix |
|----|----------|------------|-----|
| **L-01** | **P0** | **Deal Creation Blocked**: `/deals/new` treats "new" as an ID. | Create `src/app/deals/new/page.tsx` (Precedence fix). |
| **L-02** | **P0** | **Actions Bulk Delete Fails**: 405 Method Not Allowed. | Fix proxy target URL to `/api/kinetic/actions`. |
| **L-03** | **P0** | **Quarantine Dead Ends**: Delete/Approve actions fail. | Implement `route.ts` proxies mapping to correct backend paths. |
| **L-04** | **P0** | **Chat Data Split-Brain**: Agent sees stale RAG data. | Force Agent to use SQL search fallback (`_search_deals_fallback`). |
| **L-05** | **P1** | **Settings Missing Email**: No way to configure ingestion. | Add Email Settings Tab + Backend Endpoint. |
| **L-06** | **P1** | **Onboarding is Fake**: State lost on refresh. | Wire "Complete" to `POST /api/users/onboarding`. |
| **L-07** | **P2** | **Chat Rendering**: Raw markdown displayed. | Add `react-markdown` component. |

---

## 6. FEATURE → CONTRACT MAPPING

### Feature: Bulk Delete Actions
- **UI Component**: `ActionCommandCenter`
- **Current Call**: `POST /api/actions/bulk/delete`
- **Current Proxy**: `fetch(${BACKEND_URL}/api/actions/bulk/delete)` -> **404/405**
- **Required Contract**: `POST ${BACKEND_URL}/api/kinetic/actions/bulk/delete`

### Feature: Quarantine Delete
- **UI Component**: `QuarantineList`
- **Current Call**: `POST /api/quarantine/{id}/delete`
- **Current Proxy**: *None* (Rewrite attempts `/api/triage/quarantine/{id}/delete`)
- **Required Contract**: `DELETE ${BACKEND_URL}/api/triage/quarantine/{id}`

### Feature: Chat Search
- **UI Component**: `ChatInterface`
- **Current Call**: `search_deals` Tool -> `POST :8052/rag/query`
- **Required Contract**: `GET :8091/api/deals?q={query}` (SQL Fallback)

---

## 7. DEEP DIVE: DEALS ROUTING
The Next.js App Router prioritizes static routes over dynamic ones *only if they exist*.
- **Current**: `src/app/deals/[id]/page.tsx` exists. `src/app/deals/new/page.tsx` does **not** exist.
- **Result**: `[id]` captures "new".
- **Fix**: Creating `src/app/deals/new/page.tsx` immediately solves this by taking precedence.

---

## 8. DEEP DIVE: CHAT TRUTH
The Agent uses `search_deals` which hits the RAG service. The RAG service index is not updating in real-time (3 deals indexed vs 9 in DB).
- **Immediate Fix**: Modify `search_deals` in `deal_tools.py` to default to `_search_deals_fallback` (Direct Backend SQL search) until RAG freshness is solved. This aligns the Agent's "eyes" with the User's "eyes".

---

## 9. VERIFICATION COMMANDS

```bash
# 1. Verify Deal Creation Route (Should return 200)
curl -I http://localhost:3003/deals/new

# 2. Verify Actions Bulk Delete Proxy (Should proxy to kinetic)
# Note: Fails if backend endpoint missing, but should not be 405 from Next.js
curl -X POST http://localhost:3003/api/actions/bulk/delete -d '{"action_ids":["1"]}'

# 3. Verify Backend Quarantine Delete Support
curl -X DELETE http://localhost:8091/api/triage/quarantine/test-id
```

---

## 10. APPENDIX: BETTER IDEAS

**Idea 1: Route-Guarded Dynamic Pages**
Inside `[id]/page.tsx`, explicitly check `if (params.id === 'new') return notFound();`. This prevents accidental rendering of the detail view for reserved slugs if the static page creation is delayed.

**Idea 2: "BFF" (Backend for Frontend) Pattern**
Instead of 1:1 proxies, the Next.js API layer should be a true BFF. `POST /api/quarantine/actions/bulk` on Next.js could orchestrate multiple calls to the backend (e.g., delete item + log event + update stats) rather than just proxying a single failing call.
