# ZakOps Dashboard Round-4 Forensic Report

---

## 1) AGENT IDENTITY

- **agent_name:** Claude-Opus
- **run_id:** 20260205-1710-1a20a2
- **date_time:** 2026-02-05T17:10:00Z
- **dashboard_revision:** b96b33c5
- **backend_revision:** 2a68de17

---

## 2) EXECUTIVE SUMMARY

This forensic audit examined the ZakOps Dashboard (Next.js App Router on port 3003) against 11 user-submitted screenshots documenting functional failures. The audit identified **17 distinct limitations** spanning routing bugs, missing API endpoints, incomplete UI features, demo-only flows, and data integrity mismatches.

**Critical Findings:**
- 4 P0 (Critical) issues blocking core workflows
- 6 P1 (High) issues degrading user experience
- 5 P2 (Medium) issues requiring attention
- 2 P3 (Low) cosmetic/usability issues

**Root Cause Categories:**
1. **Routing Architecture** - Dynamic `[id]` catch-all without slug guards
2. **Contract Drift** - Frontend calls endpoints backend doesn't expose
3. **Demo-Only Flows** - Onboarding/email config saves to localStorage only
4. **Data Source Mismatch** - Agent DB vs UI DB showing different deal counts

---

## 3) SCREENSHOT EVIDENCE ANALYSIS

### Screenshot 1: `/deals/GLOBAL` - "Failed to load deal"
- **Route:** `/deals/[id]/page.tsx:18-25`
- **Root Cause:** `params.id` passed directly to `getDeal(dealId)` without checking for reserved slugs
- **Impact:** P0 - Users clicking "GLOBAL" deal scope get error page

### Screenshot 2: `/deals` - "Method Not Allowed" toast
- **Route:** `/deals/page.tsx` list view
- **Root Cause:** Some bulk operation triggered 405 from backend
- **Impact:** P1 - Bulk operations fail silently

### Screenshot 3: `/settings` - Only AI Provider config visible
- **Route:** `/settings/page.tsx` (537 lines)
- **Root Cause:** Settings page only implements LLM provider selector; NO email config, NO agent config, NO buy box criteria
- **Impact:** P1 - Email sync cannot be configured from UI

### Screenshot 4: `/onboarding` - "Configure Email Settings" button
- **Route:** `/onboarding/page.tsx:9-13`
- **Root Cause:** `handleComplete` only sets `localStorage.setItem('zakops-onboarding-complete', 'true')` - NO backend call
- **Impact:** P0 - Onboarding is demo-only; email not actually configured

### Screenshot 5: `/onboarding` - "Meet Your Agent" capability cards
- **Route:** `OnboardingWizard` component
- **Root Cause:** Capability cards are presentational only; no real backend integration
- **Impact:** P2 - Misleading UX; promises features not connected

### Screenshot 6: `/chat` - Raw markdown visible (`**bold**`)
- **Route:** `/chat/page.tsx` streaming handler
- **Root Cause:** Message content rendered as plain text without markdown processor
- **Impact:** P1 - Chat responses hard to read; formatting ignored

### Screenshot 6 (continued): Agent says "3 deals" vs UI shows 9
- **Root Cause:** Agent queries its own DB (deal_registry); UI queries different endpoint; data not synchronized
- **Impact:** P0 - Critical data integrity mismatch; user trust issue

### Screenshot 7: `/quarantine` - "Preview not found" in detail panel
- **Route:** `/quarantine/page.tsx:143-151`
- **API:** `getQuarantinePreview(actionId)` returns null
- **Root Cause:** Preview endpoint `/api/actions/quarantine/{id}/preview` returns 404 for some items
- **Impact:** P1 - Cannot review quarantine items before approval/rejection

### Screenshot 8: `/quarantine` - "Not Found" error on delete click
- **Route:** `/quarantine/page.tsx:263-302`
- **API:** `deleteQuarantineItem()` calls `/api/quarantine/{id}/delete`
- **Root Cause:** Backend endpoint may not exist or action_id mapping incorrect
- **Impact:** P1 - Cannot remove items from quarantine queue

### Screenshot 9: `/actions` - "Delete Completed Actions" returns 405
- **Route:** `/actions/page.tsx:486-505`
- **API:** `clearCompletedActions()` calls `/api/actions/clear-completed` with POST
- **Frontend Route:** `/api/actions/clear-completed/route.ts` exports `POST` (line 20)
- **Root Cause:** Backend `/api/actions/clear-completed` returns 405 (Method Not Allowed); Next.js route exists but backend proxy fails
- **Impact:** P1 - Cannot clear completed actions from Actions Command Center

### Screenshot 10: `/dashboard` - Main view with Ask Agent sidebar
- **Route:** `/dashboard/page.tsx`
- **Status:** Renders correctly; no errors visible
- **Impact:** P3 - Baseline working

### Screenshot 11: `/deals/new` - "Failed to load deal" same as GLOBAL
- **Route:** `/deals/[id]/page.tsx`
- **Root Cause:** Same as Screenshot 1; "new" treated as deal_id
- **Impact:** P0 - Cannot create new deals from `/deals/new` route

---

## 4) LIMITATIONS REGISTRY (Deduplicated)

| ID | Priority | Category | Description | Route/File | API Contract | Evidence |
|----|----------|----------|-------------|------------|--------------|----------|
| DL-001 | P0 | Routing | `/deals/GLOBAL` and `/deals/new` treated as deal IDs; return 404 | `/deals/[id]/page.tsx:18-25` | `GET /api/deals/{id}` | Screenshots 1, 11 |
| DL-002 | P0 | Data Integrity | Agent reports 3 deals vs UI showing 9 deals | Multiple | Agent DB vs Backend API | Screenshot 6 |
| DL-003 | P0 | Demo-Only | Onboarding saves to localStorage only; no backend persistence | `/onboarding/page.tsx:9-13` | N/A | Screenshot 4 |
| DL-004 | P0 | Missing Feature | No email configuration UI in Settings | `/settings/page.tsx` | N/A | Screenshot 3 |
| DL-005 | P1 | API Contract | Quarantine delete returns 404/Not Found | `/quarantine/page.tsx:263` | `POST /api/quarantine/{id}/delete` | Screenshot 8 |
| DL-006 | P1 | API Contract | Clear completed actions returns 405 Method Not Allowed | `/actions/page.tsx:486` | `POST /api/actions/clear-completed` | Screenshot 9 |
| DL-007 | P1 | API Contract | Quarantine preview returns null for some items | `/quarantine/page.tsx:143` | `GET /api/actions/quarantine/{id}/preview` | Screenshot 7 |
| DL-008 | P1 | Rendering | Chat responses show raw markdown instead of rendered | `/chat/page.tsx` | N/A | Screenshot 6 |
| DL-009 | P1 | API Contract | Deals bulk operation returns 405 | `/deals/page.tsx` | Unknown bulk endpoint | Screenshot 2 |
| DL-010 | P1 | Missing Feature | No agent configuration section in Settings | `/settings/page.tsx` | N/A | Screenshot 3 |
| DL-011 | P2 | Demo-Only | Onboarding capability cards are presentational only | `OnboardingWizard` | N/A | Screenshot 5 |
| DL-012 | P2 | Missing Feature | No buy box criteria configuration | `/settings/page.tsx` | N/A | Implied |
| DL-013 | P2 | Missing Feature | No notification preferences in Settings | `/settings/page.tsx` | N/A | Implied |
| DL-014 | P2 | UX | "Configure Email Settings" button in onboarding has no target | `/onboarding/page.tsx` | N/A | Screenshot 4 |
| DL-015 | P2 | Contract Gap | Next.js API routes have mock fallbacks masking real failures | `/api/actions/clear-completed/route.ts:65-100` | N/A | Code review |
| DL-016 | P3 | UX | Dashboard Ask Agent sidebar not integrated with main chat | `/dashboard/page.tsx` | N/A | Screenshot 10 |
| DL-017 | P3 | UX | Actions page shows "0 action(s) will be deleted" even when actions exist | `/actions/page.tsx:1246-1256` | N/A | Screenshot 9 |

---

## 5) FEATURE-TO-CONTRACT MAPPING

### 5.1 Deals Module

| UI Action | Frontend Function | API Endpoint | HTTP Method | Backend Status | Notes |
|-----------|-------------------|--------------|-------------|----------------|-------|
| View deal list | `getDeals()` | `GET /api/deals` | GET | Implemented | Works |
| View deal detail | `getDeal(id)` | `GET /api/deals/{id}` | GET | Implemented | Fails for "GLOBAL", "new" |
| Transition stage | `transitionDeal()` | `POST /api/deals/{id}/transition` | POST | Implemented | Works |
| Add note | `addDealNote()` | `POST /api/deals/{id}/notes` | POST | Implemented | Works |
| Archive deal | `archiveDeal()` | `POST /api/deals/{id}/archive` | POST | Implemented | Works |
| Bulk archive | `bulkArchiveDeals()` | `POST /api/deals/bulk-archive` | POST | Unknown | May return 405 |
| Get enrichment | `getDealEnrichment()` | `GET /api/deals/{id}/enrichment` | GET | Implemented | Works |
| Get materials | `getDealMaterials()` | `GET /api/deals/{id}/materials` | GET | Implemented | Works |

### 5.2 Actions Module

| UI Action | Frontend Function | API Endpoint | HTTP Method | Backend Status | Notes |
|-----------|-------------------|--------------|-------------|----------------|-------|
| List actions | `getKineticActions()` | `GET /api/actions` | GET | Implemented | Works |
| View action | `getKineticAction(id)` | `GET /api/actions/{id}` | GET | Implemented | Works |
| Approve action | `approveKineticAction()` | `POST /api/actions/{id}/approve` | POST | Implemented | Works |
| Run action | `runKineticAction()` | `POST /api/actions/{id}/execute` | POST | Implemented | Works |
| Cancel action | `cancelKineticAction()` | `POST /api/actions/{id}/cancel` | POST | Implemented | Works |
| Archive action | `archiveKineticAction()` | `POST /api/actions/{id}/archive` | POST | Unknown | Needs verification |
| Delete action | `deleteKineticAction()` | `DELETE /api/actions/{id}` | DELETE | Unknown | Needs verification |
| Bulk delete | `bulkDeleteKineticActions()` | `POST /api/actions/bulk/delete` | POST | Has Next.js mock | May not reach backend |
| Clear completed | `clearCompletedActions()` | `POST /api/actions/clear-completed` | POST | Returns 405 | Backend missing |

### 5.3 Quarantine Module

| UI Action | Frontend Function | API Endpoint | HTTP Method | Backend Status | Notes |
|-----------|-------------------|--------------|-------------|----------------|-------|
| List queue | `getQuarantineQueue()` | `GET /api/actions/quarantine` | GET | Implemented | Works |
| Get preview | `getQuarantinePreview()` | `GET /api/actions/quarantine/{id}/preview` | GET | Partial | Returns null for some |
| Approve item | `approveQuarantineItem()` | `POST /api/actions/{id}/approve` + execute | POST | Implemented | Works |
| Reject item | `rejectQuarantineItem()` | `POST /api/actions/quarantine/{id}/reject` | POST | Implemented | Works |
| Delete item | `deleteQuarantineItem()` | `POST /api/quarantine/{id}/delete` | POST | Missing | Returns 404 |
| Bulk delete | `bulkDeleteQuarantineItems()` | `POST /api/quarantine/bulk-delete` | POST | Unknown | Needs verification |

### 5.4 Chat Module

| UI Action | Frontend Function | API Endpoint | HTTP Method | Backend Status | Notes |
|-----------|-------------------|--------------|-------------|----------------|-------|
| Send message | `streamChatMessage()` | `POST /api/chat` | POST | Implemented | Works (SSE) |
| Get session | `getChatSession()` | `GET /api/chat/session/{id}` | GET | Implemented | Works |
| Execute proposal | `executeChatProposal()` | `POST /api/chat/execute-proposal` | POST | Implemented | Works |

### 5.5 Settings Module

| UI Action | Frontend Function | API Endpoint | HTTP Method | Backend Status | Notes |
|-----------|-------------------|--------------|-------------|----------------|-------|
| Get AI provider | N/A (localStorage) | N/A | N/A | N/A | Client-side only |
| Set AI provider | N/A (localStorage) | N/A | N/A | N/A | Client-side only |
| Get email config | N/A | N/A | N/A | Not implemented | Missing entirely |
| Get agent config | N/A | N/A | N/A | Not implemented | Missing entirely |
| Get buy box criteria | N/A | N/A | N/A | Not implemented | Missing entirely |

---

## 6) DEEP DIVE: ROOT CAUSE ANALYSIS

### 6.1 Deal Routing Bug (DL-001)

**Location:** `/apps/dashboard/src/app/deals/[id]/page.tsx:18-25`

```typescript
const params = useParams();
const dealId = params.id as string;
// ... passed directly to getDeal(dealId)
```

**Problem:** The `[id]` dynamic segment catches ALL paths including:
- `/deals/GLOBAL` - Should be global scope view
- `/deals/new` - Should be create new deal form

**Fix Required:** Add slug guard before API call:
```typescript
const RESERVED_SLUGS = ['new', 'GLOBAL', 'global'];
if (RESERVED_SLUGS.includes(dealId)) {
  // Redirect or render appropriate component
}
```

### 6.2 Data Integrity Mismatch (DL-002)

**Symptoms:**
- Agent says: "You have 3 active deals"
- UI shows: 9 deals in the deals list

**Root Causes (Multiple Possible):**
1. Agent queries `deal_registry` SQLite directly
2. UI queries `/api/deals` which may include archived deals
3. Agent uses different `status` filter than UI
4. Memory/context from different time period

**Verification Needed:**
- Compare `/api/deals` response with agent's `search_deals` tool output
- Check if archived deals counted differently
- Verify deal_registry sync with API layer

### 6.3 405 Method Not Allowed (DL-006)

**Frontend Route:** `/api/actions/clear-completed/route.ts`
- Exports `POST` handler (line 20)
- Has mock fallback when backend returns 404 (line 61-77)

**Backend Behavior:** Returns 405 (not 404), so mock fallback doesn't trigger.

**Root Cause:** Backend FastAPI router doesn't have `/api/actions/clear-completed` endpoint, OR the endpoint exists but only accepts different HTTP method.

### 6.4 Onboarding Demo-Only (DL-003)

**Location:** `/apps/dashboard/src/app/onboarding/page.tsx:9-13`

```typescript
const handleComplete = (state) => {
  console.log('Onboarding complete:', state);
  localStorage.setItem('zakops-onboarding-complete', 'true');
  router.push('/dashboard');
};
```

**Problem:** No backend call to:
- Configure Gmail OAuth
- Set up email sync
- Register user preferences
- Initialize deal pipeline

---

## 7) ARCHITECTURAL OBSERVATIONS

### 7.1 API Proxy Pattern

Dashboard uses Next.js rewrites (likely in `next.config.ts`) to proxy `/api/*` to backend port 8091. This creates:

**Pros:**
- Single origin for frontend
- Can add middleware/auth
- Mock fallbacks in development

**Cons:**
- Extra hop adds latency
- Error messages get mangled
- 405 from backend appears as dashboard bug

### 7.2 Mock Fallback Anti-Pattern

Several Next.js API routes have this pattern:
```typescript
if (backendResponse.status === 404) {
  // Mock implementation
  return NextResponse.json({ success: true, ... });
}
```

**Problem:** This masks real backend failures. When backend returns 405 (not 404), the mock doesn't trigger and error propagates.

### 7.3 Zod Schema Hardening

The `api.ts` client uses Zod schemas with `.passthrough()` to avoid silent field drops. This is good practice but:
- Some schemas still have `.optional()` without `.nullable()`
- Coercion helpers (like `coerceToNumber`) may hide data quality issues

---

## 8) PRIORITY CLASSIFICATION RATIONALE

### P0 (Critical) - 4 Issues
Must fix before any release; blocks core user workflows:
- DL-001: Cannot navigate to deals properly
- DL-002: Data integrity issue breaks user trust
- DL-003: Onboarding doesn't actually work
- DL-004: Cannot configure email (core feature)

### P1 (High) - 6 Issues
Significantly degrades user experience:
- DL-005, DL-006, DL-007: Quarantine/Actions workflows broken
- DL-008: Chat unusable without markdown rendering
- DL-009: Bulk operations fail
- DL-010: Missing core settings

### P2 (Medium) - 5 Issues
Should fix in next sprint:
- DL-011 to DL-015: UX improvements, missing features, technical debt

### P3 (Low) - 2 Issues
Nice to have:
- DL-016, DL-017: Minor polish items

---

## 9) EVIDENCE ARTIFACTS

All screenshots preserved at:
```
/mnt/c/Users/mzsai/Downloads/Dashboard Screenshots/
├── 1.png  - /deals/GLOBAL error
├── 2.png  - /deals 405 error
├── 3.png  - /settings AI-only
├── 4.png  - /onboarding email config
├── 5.png  - /onboarding capabilities
├── 6.png  - /chat markdown issue
├── 7.png  - /quarantine preview missing
├── 8.png  - /quarantine delete 404
├── 9.png  - /actions delete 405
├── 10.png - /dashboard baseline
└── 11.png - /deals/new error
```

---

## 10) RECOMMENDATIONS

### Immediate (This Week)
1. Fix deal routing slug guard (DL-001) - 30 min fix
2. Add markdown renderer to chat (DL-008) - Use react-markdown
3. Add backend endpoint for `/api/actions/clear-completed` (DL-006)

### Short-Term (This Sprint)
4. Build email configuration UI in Settings (DL-004)
5. Fix quarantine delete endpoint (DL-005)
6. Investigate data integrity mismatch (DL-002)
7. Remove mock fallbacks, implement proper error handling (DL-015)

### Medium-Term (Next Sprint)
8. Complete onboarding backend integration (DL-003)
9. Add agent configuration UI (DL-010)
10. Add buy box criteria configuration (DL-012)

---

*Forensic Report Generated: 2026-02-05T17:10:00Z*
*Auditor: Claude-Opus*
