# Forensic Audit Report: Quarantine UI + Chat Page

**Date:** 2026-02-15
**Auditor:** Claude (Opus 4.6)
**Method:** Code analysis, API endpoint testing, Playwright browser automation, backend logs, DB queries

---

## Executive Summary

**5 of 6 reported issues CONFIRMED.** The root cause chain is short: **3 missing Next.js API route handlers** break the entire quarantine workflow, and **vLLM being down** breaks chat. A secondary chat bug means even the fallback response doesn't display.

---

## 1) Reproduction Confirmation

| Issue | Confirmed? | Method |
|-------|-----------|--------|
| A1: Operator name input unclear | **Confirmed** | Code + Playwright snapshot |
| A2: Detail buttons permanently disabled | **Confirmed** | Playwright: `button "Escalate" [disabled]` |
| A3: Approve flow fails (single + bulk) | **Confirmed** | Curl: bulk-process -> 404 HTML; single via UI unreachable |
| A4: Reject flow fails | **Confirmed** | Same root cause as A3 |
| A5: Preview shows "Preview not found" | **Confirmed** | Playwright network: `GET /api/quarantine/{id}` -> 404 |
| B1: Chat "No response received" | **Confirmed** | Playwright + agent API logs + vLLM health check |

---

## 2) Evidence

### A5 -- Preview Not Found (ROOT CAUSE of A2, A3, A4)

**Network trace (Playwright):**
```
[GET] /api/quarantine?limit=200&offset=0&sort_by=received_at&sort_order=desc => 200 OK  <- list works
[GET] /api/quarantine/96e27a54-b01f-4d44-bd90-7e2edc8579c6 => 404 Not Found  <- detail broken
```

**Console error:**
```
Failed to load resource: the server responded with a status of 404 (Not Found)
  @ http://localhost:3003/api/quarantine/96e27a54-b01f-4d44-bd90-7e2edc8579c6
```

**Code path:**
- `api.ts:914` -- `getQuarantinePreview()` calls `GET /api/quarantine/${itemId}`
- `middleware.ts:70` -- `/api/quarantine/` is in `handledByRoutes` -> passes to Next.js
- **No route handler exists** at `apps/dashboard/src/app/api/quarantine/[id]/route.ts`

**Existing route handlers:**
```
apps/dashboard/src/app/api/quarantine/[id]/process/route.ts  <- POST only
apps/dashboard/src/app/api/quarantine/[id]/delete/route.ts   <- POST only
apps/dashboard/src/app/api/quarantine/health/route.ts        <- GET health
```

**Missing route handlers:**
```
apps/dashboard/src/app/api/quarantine/[id]/route.ts          <- GET detail (MISSING)
apps/dashboard/src/app/api/quarantine/bulk-process/route.ts  <- POST bulk (MISSING)
apps/dashboard/src/app/api/quarantine/[id]/undo-approve/route.ts <- POST undo (MISSING)
```

**Why the list works but detail doesn't:**
The middleware prefix match for `/api/quarantine/` (with trailing slash) catches `/api/quarantine/{id}` but NOT `/api/quarantine` (no trailing slash). So `GET /api/quarantine` (list) falls through to the middleware's backend proxy and works. But `GET /api/quarantine/{id}` matches the prefix and is routed to Next.js, which has no GET handler -> 404.

### A2 -- Buttons Disabled

**Code:** `page.tsx:801-809`
```typescript
<Button ... disabled={!preview || working}>Escalate</Button>
<Button ... disabled={!preview || working}>Reject</Button>
<Button ... disabled={!preview || working}>Approve</Button>
```

Since `preview` is always `null` (A5 fails), `!preview` is always `true` -> buttons permanently disabled.

### A3 / A4 -- Approve/Reject Fails

**Two broken paths:**

1. **Single item (detail buttons):** Unreachable because buttons are disabled (A2 <- A5).
2. **Bulk action (checkbox + bottom bar):** Calls `POST /api/quarantine/bulk-process` -> 404 HTML page (no route handler).

**Backend is fine** -- direct curl through dashboard proxy works:
```
POST http://localhost:3003/api/quarantine/{id}/process -> 200
  {"status":"approved","item_id":"...","deal_id":"DL-0115","deal_created":true}
```

The "massive debug/error panel" visible in screenshots is the browser DevTools console (open during testing), not an app-rendered panel.

### A1 -- Operator Name Input

**Location:** `page.tsx:113` -- `textbox "Operator name"` (ref=e113)

This is **not a search bar**. It stores the operator's name/initials for the `processed_by` field in approve/reject/escalate API calls. Persisted to `localStorage('zakops_operator_name')`.

**Issues:**
- Label says "Operator name" which is ambiguous (search? identity?)
- No inline help text explaining its purpose
- Validation only fires on action attempt (toast: "Enter your name/initials first")
- No min/max length, no character validation

### B1 -- Chat Broken

**Two independent issues stacked:**

**Primary: vLLM is down**
```bash
$ curl -sf http://localhost:8000/health
# NO RESPONSE -- vLLM not running
```

Agent API logs:
```
openai.APIConnectionError: Connection error.
llm_call_failed_all_models  error="'WARNING'"
chat_request_failed  error='1 validation error for ChatResponse messages
  Input should be a valid list [type=list_type, input_value=None]'
```

Chain: vLLM down -> Agent API can't call LLM -> graph returns None -> Pydantic validation error -> 500 -> Dashboard Strategy 1 fails.

**Secondary: Strategy 3 fallback bug**

When Strategy 1 fails, the chat route falls to Strategy 3 (helpful fallback). Strategy 3's SSE done event (`route.ts:247`) is **missing `final_text`**:

```typescript
// Strategy 1 done event (line 145-154) -- HAS final_text:
{ final_text: assistantContent, warnings: [], ... }

// Strategy 3 done event (line 247-253) -- MISSING final_text:
{ warnings: ['AI agent service is currently unavailable...'], ... }
//  ^ no final_text field!
```

The frontend relies on `final_text` from the done event. When missing, "No response received" is displayed.

**Auth is NOT the issue** -- Dashboard token matches Agent API container's DASHBOARD_SERVICE_TOKEN.

---

## 3) Root Cause Hypotheses (Ranked)

| # | Root Cause | Impact | Confidence |
|---|-----------|--------|-----------|
| **RC-1** | Missing `GET /api/quarantine/[id]/route.ts` | Preview broken -> buttons disabled -> single approve/reject unreachable | **Certain** (404 confirmed) |
| **RC-2** | Missing `POST /api/quarantine/bulk-process/route.ts` | Bulk approve/reject broken | **Certain** (404 confirmed) |
| **RC-3** | vLLM (port 8000) not running | Chat agent can't generate responses | **Certain** (no health response) |
| **RC-4** | Strategy 3 done event missing `final_text` | Even fallback shows "No response received" | **Certain** (code confirmed) |
| **RC-5** | Missing `POST /api/quarantine/[id]/undo-approve/route.ts` | Undo not functional from UI | **Certain** (404 confirmed) |

---

## 4) Remediation Plan Proposal

### Phase 1: Critical -- Restore Quarantine Operations (3 route handlers)

**Fix RC-1: Create `GET /api/quarantine/[id]/route.ts`** (~15 lines)
- Proxy GET to backend `GET /api/quarantine/{item_id}`
- Same pattern as existing `process/route.ts` but for GET
- This alone fixes: A5 (preview), A2 (buttons), and single-item A3/A4

**Fix RC-2: Create `POST /api/quarantine/bulk-process/route.ts`** (~15 lines)
- Proxy POST to backend `POST /api/quarantine/bulk-process`
- This fixes: bulk A3 (approve) and bulk A4 (reject)

**Fix RC-5: Create `POST /api/quarantine/[id]/undo-approve/route.ts`** (~15 lines)
- Proxy POST to backend `POST /api/quarantine/{item_id}/undo-approve`
- Not user-reported but discovered during audit; needed for P4 undo flow

### Phase 2: Critical -- Restore Chat

**Fix RC-3: Start vLLM**
- `cd /home/zaks/Zaks-llm && docker compose up -d vllm` (or equivalent)
- Verify: `curl http://localhost:8000/health`

**Fix RC-4: Add `final_text` to Strategy 3 done event** (1 line)
- File: `apps/dashboard/src/app/api/chat/route.ts:247`
- Add `final_text: helpfulResponse` to the Strategy 3 done event JSON

### Phase 3: Polish -- UX Clarity

**Fix A1: Operator name field clarity**
- Add placeholder text: "Your initials (e.g., JYH)" or inline label
- Low priority -- functional, just unclear

**Additional polish found during audit:**
- `working` state (page.tsx:135) declared but never set during approve/reject/escalate
- Preview route at `/api/actions/quarantine/[actionId]/preview/route.ts` is dead code

### Execution Order

```
Phase 1 (30 min) --- 3 route handler files --- fixes A2, A3, A4, A5
Phase 2a (15 min) -- start vLLM -------------- fixes B1 primary
Phase 2b (5 min) --- 1 line fix --------------- fixes B1 secondary
Phase 3 (30 min) --- UX polish --------------- fixes A1 + working state
```

---

## 5) Files Audited

| File | Lines | Key Finding |
|------|-------|------------|
| `apps/dashboard/src/app/quarantine/page.tsx` | 1320 | Buttons disabled by `!preview`, `working` never set |
| `apps/dashboard/src/lib/api.ts` | 2663 | `getQuarantinePreview()` calls missing route |
| `apps/dashboard/src/app/api/quarantine/[id]/process/route.ts` | 38 | POST works, no GET |
| `apps/dashboard/src/app/api/quarantine/[id]/delete/route.ts` | 36 | POST works |
| `apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts` | 51 | Dead code (wrong table) |
| `apps/dashboard/src/middleware.ts` | 148 | `/api/quarantine/` routing causes split |
| `apps/dashboard/src/app/api/chat/route.ts` | 390 | Strategy 3 missing `final_text` |
| `apps/dashboard/src/lib/agent/providers/local.ts` | 251 | Auth token flow correct |
| `apps/dashboard/src/app/chat/page.tsx` | 1876 | Relies on `final_text` from done event |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | ~2900 | All backend endpoints work correctly |

## 6) DB State Check

Quarantine items present and correct in `zakops.quarantine_items`:
- 15 pending items (mix of `langsmith_shadow`, `email_inbox` source types)
- Schema V2 fields populated (sender_name, confidence, triage_summary, etc.)
- Version field = 1 on all pending items (no concurrent edits)
- Backend endpoints return correct data (list, detail, process all tested)

**One test artifact to clean up:** DL-0115 was created during forensic approve test, then undo-approve attempted but the dashboard route was missing. The quarantine item `8de45567` may now be in `approved` status with deal DL-0115 linked. Remediation mission should verify and clean up if needed.
