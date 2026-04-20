# MISSION: QUARANTINE-CHAT-REMEDIATE-001

**Subtitle:** Restore Quarantine Approve/Reject/Preview + Chat Fallback

## Date: 2026-02-15
## Classification: Remediation (bug fix)
## Prerequisite: Forensic audit complete (`/home/zaks/bookkeeping/docs/FORENSIC-QUARANTINE-CHAT-2026-02-15.md`)
## Successor: QA-QUARANTINE-CHAT-REMEDIATE-VERIFY-001 (paired QA)

**Affected Surfaces:** S1 (Backend -> Dashboard), S9 (Design System — Phase 3 only)
**Blast Radius:** Dashboard API routes + 1 line in chat route + quarantine page UX

---

## Mission Objective

### What

Restore the quarantine page approve/reject/escalate/preview workflows and the chat fallback display by fixing 5 confirmed root causes from the forensic audit dated 2026-02-15.

### What NOT

- Do NOT modify backend endpoints (all backend APIs work correctly — confirmed by direct curl testing)
- Do NOT modify the quarantine page component logic (buttons, modals, state management are correct — they just need working API routes behind them)
- Do NOT attempt to fix vLLM startup (operational issue, not code — separate runbook)
- Do NOT redesign the quarantine UX beyond the specific A1 polish items

### Source Material

- **Forensic report:** `/home/zaks/bookkeeping/docs/FORENSIC-QUARANTINE-CHAT-2026-02-15.md`
- **Screenshots:** `/mnt/c/Users/mzsai/Downloads/Dash-sreenshots-1/` (8 screenshots)
- **Existing route patterns:** `apps/dashboard/src/app/api/quarantine/[id]/process/route.ts` (reference for new routes)

---

## Context

The LangSmith Email Triage integration is live end-to-end: emails flow from LangSmith through the bridge to the backend, and quarantine items appear in the dashboard. However, the quarantine page is non-operational because three Next.js API route handlers were never created during the Phase 2 (Quarantine UX) build.

**Root causes (from forensic audit):**

| RC# | Root Cause | Impact |
|-----|-----------|--------|
| RC-1 | Missing `GET /api/quarantine/[id]/route.ts` | Preview 404 -> buttons disabled -> single approve/reject unreachable |
| RC-2 | Missing `POST /api/quarantine/bulk-process/route.ts` | Bulk approve/reject 404 |
| RC-3 | vLLM (port 8000) not running | Chat agent 500 (OPERATIONAL — not code fix) |
| RC-4 | Strategy 3 `done` event missing `final_text` | Chat fallback shows "No response received" |
| RC-5 | Missing `POST /api/quarantine/[id]/undo-approve/route.ts` | Undo-approve 404 |

**Middleware routing context:** The middleware at `middleware.ts:70` has `/api/quarantine/` in `handledByRoutes`, which means all requests starting with `/api/quarantine/` are passed to Next.js route handlers (NOT proxied to backend). But `GET /api/quarantine` (the list endpoint — no trailing slash) falls through to the backend proxy. This split is intentional — the existing `process` and `delete` route handlers add auth headers and error handling. The fix is to add the missing route handlers, not to change the middleware routing.

---

## Architectural Constraints

1. **Route handler pattern:** All new route handlers MUST follow the same proxy pattern as `apps/dashboard/src/app/api/quarantine/[id]/process/route.ts` — use `backendFetch()` from `@/lib/backend-fetch`, return JSON with `Content-Type: application/json`, catch errors and return 502 `backend_unavailable`.
2. **No direct backend URL construction:** Use `backendFetch()` which handles base URL, API key injection, timeout, and error handling.
3. **Middleware must not change:** The `handledByRoutes` list and prefix matching logic must remain as-is.
4. **Port 8090 is FORBIDDEN** — never reference.
5. **Generated files never edited** — `*.generated.ts`, `*_models.py` are deny-rule protected.
6. **WSL safety:** CRLF stripping (`sed -i 's/\r$//'`) on any `.sh` files, `chown zaks:zaks` on all created files.

---

## Anti-Pattern Examples

**WRONG — Changing middleware to proxy quarantine detail:**
```typescript
// DO NOT DO THIS — breaks process/delete handlers that need route-level logic
// middleware.ts
const handledByRoutes = [
  // Remove '/api/quarantine/' to let everything proxy
];
```

**RIGHT — Add missing route handler following existing pattern:**
```typescript
// apps/dashboard/src/app/api/quarantine/[id]/route.ts
import { backendFetch } from '@/lib/backend-fetch';
export async function GET(request, { params }) {
  const { id } = await params;
  const response = await backendFetch(`/api/quarantine/${id}`);
  // ... proxy pattern
}
```

**WRONG — Hardcoding backend URL in route handler:**
```typescript
const response = await fetch(`http://localhost:8091/api/quarantine/${id}`);
```

**RIGHT — Using backendFetch:**
```typescript
const response = await backendFetch(`/api/quarantine/${id}`);
```

---

## Pre-Mortem

| # | Failure Scenario | Mitigation |
|---|-----------------|------------|
| PM-1 | New route handler created but Next.js doesn't pick it up (stale build cache) | Restart dashboard dev server after creating route files; verify with `curl` |
| PM-2 | `backendFetch` not imported correctly (wrong path alias) | Copy import exactly from existing `process/route.ts` |
| PM-3 | Route parameter name mismatch (`id` vs `itemId` vs `actionId`) | Use `id` to match existing `[id]` directory structure; the backend expects UUID at `/api/quarantine/{item_id}` |
| PM-4 | Chat `final_text` fix breaks Strategy 1 or 2 done events | Only modify Strategy 3 block (lines 247-253); Strategy 1 and 2 already have `final_text` |
| PM-5 | Forensic test artifact (DL-0115 deal + approved quarantine item) breaks verify gates | Clean up in Phase 1 pre-flight: undo-approve via backend curl, verify item restored to pending |

---

## Phase 0: Pre-Flight & Cleanup

**Complexity:** S (read-only checks + 1 cleanup curl)
**Blast Radius:** None (read-only + backend API call)

### Tasks

| # | Task | Detail |
|---|------|--------|
| P0-01 | Verify services running | `curl -sf http://localhost:8091/health`, `curl -sf http://localhost:3003 -o /dev/null -w "%{http_code}"` |
| P0-02 | Read forensic report | `/home/zaks/bookkeeping/docs/FORENSIC-QUARANTINE-CHAT-2026-02-15.md` |
| P0-03 | Read existing route handler (reference pattern) | `apps/dashboard/src/app/api/quarantine/[id]/process/route.ts` |
| P0-04 | Read `backendFetch` utility | `apps/dashboard/src/lib/backend-fetch.ts` |
| P0-05 | Identify contract surfaces | S1 (Backend -> Dashboard API routes), S9 (Phase 3 UI polish) |
| P0-06 | Clean up forensic test artifact | `curl -s -X POST http://localhost:8091/api/quarantine/8de45567-f402-487c-b293-acd277b66e50/undo-approve -H "Content-Type: application/json" -H "X-API-Key: $ZAKOPS_API_KEY" -d '{"admin_user":"cleanup","reason":"Reverting forensic test"}'` — IF item is in approved status |
| P0-07 | Baseline validation | `make validate-local` |

### Gate P0
```
P0-01: Backend health returns 200
P0-02: Dashboard returns 200 or 307
P0-03: backendFetch utility file exists and exports backendFetch function
P0-04: Existing process/route.ts uses backendFetch (pattern confirmed)
P0-05: make validate-local PASS
P0-06: Quarantine item 8de45567 is in 'pending' status (cleaned up or was never changed)
```

---

## Phase 1: Restore Quarantine API Routes

**Complexity:** S (3 new files, ~15 lines each, identical pattern)
**Blast Radius:** Dashboard API layer only — no backend changes, no page component changes

### Tasks

| # | Task | File | RC |
|---|------|------|----|
| P1-01 | Create GET detail route handler | `apps/dashboard/src/app/api/quarantine/[id]/route.ts` | RC-1 |
| P1-02 | Create POST bulk-process route handler | `apps/dashboard/src/app/api/quarantine/bulk-process/route.ts` | RC-2 |
| P1-03 | Create POST undo-approve route handler | `apps/dashboard/src/app/api/quarantine/[id]/undo-approve/route.ts` | RC-5 |
| P1-04 | Restart dashboard dev server | Kill and restart `npm run dev` in `apps/dashboard` |
| P1-05 | Verify GET detail | `curl -sf http://localhost:3003/api/quarantine/{pending_item_id}` returns JSON with quarantine item fields |
| P1-06 | Verify POST bulk-process | `curl -s -X POST http://localhost:3003/api/quarantine/bulk-process -H "Content-Type: application/json" -d '{"item_ids":["non-existent"],"action":"approve","processed_by":"test"}' -w "\n%{http_code}"` returns JSON (not 404 HTML) |
| P1-07 | Verify POST undo-approve | `curl -s -X POST http://localhost:3003/api/quarantine/00000000-0000-0000-0000-000000000000/undo-approve -H "Content-Type: application/json" -d '{"admin_user":"test","reason":"test"}' -w "\n%{http_code}"` returns JSON 404 (not HTML 404) |
| P1-08 | Browser verify: preview loads | Open `localhost:3003/quarantine`, click item, verify preview panel shows data (not "Preview not found") |
| P1-09 | Browser verify: buttons enabled | With preview loaded, verify Escalate/Reject/Approve buttons are NOT disabled |
| P1-10 | Browser verify: single approve | Enter operator name, click item, click Approve, confirm in modal — verify deal created toast + redirect |
| P1-11 | Browser verify: single reject | Select pending item, click Reject, enter reason, confirm — verify status changes |
| P1-12 | Browser verify: bulk approve | Select multiple items via checkboxes, click Approve in bulk bar, confirm — verify deals created |
| P1-13 | Fix CRLF + ownership | `sed -i 's/\r$//' <new files>` + `sudo chown zaks:zaks <new files>` |

### Decision Tree
- IF `backendFetch` is not available in the route handler context -> use the same import path as `process/route.ts`
- IF dashboard doesn't pick up new routes after file creation -> restart dev server (P1-04)
- IF backend returns unexpected format -> check the backend endpoint directly via `curl http://localhost:8091/api/quarantine/{id}`

### Rollback
```bash
# Delete the 3 new files (returns to pre-mission state)
rm apps/dashboard/src/app/api/quarantine/[id]/route.ts
rm -rf apps/dashboard/src/app/api/quarantine/bulk-process/
rm -rf apps/dashboard/src/app/api/quarantine/[id]/undo-approve/
# Restart dashboard
```

### Gate P1
```
P1-01: GET /api/quarantine/{id} returns JSON 200 (not 404 HTML)
P1-02: POST /api/quarantine/bulk-process returns JSON (not 404 HTML)
P1-03: POST /api/quarantine/{id}/undo-approve returns JSON (not 404 HTML)
P1-04: Browser: preview panel shows quarantine item data
P1-05: Browser: Escalate/Reject/Approve buttons are clickable (not disabled)
P1-06: Browser: single approve creates deal (toast confirmation + redirect)
P1-07: Browser: single reject changes status (toast confirmation)
P1-08: Browser: bulk approve via checkbox bar works
P1-09: All 3 new files owned by zaks:zaks, no CRLF
P1-10: make validate-local PASS
```

---

## Phase 2: Fix Chat Fallback Display

**Complexity:** XS (1 line change)
**Blast Radius:** Chat route handler only — Strategy 3 fallback path

### Tasks

| # | Task | File |
|---|------|------|
| P2-01 | Add `final_text: helpfulResponse` to Strategy 3 done event | `apps/dashboard/src/app/api/chat/route.ts` line ~247 |
| P2-02 | Verify: send chat message with vLLM down | Open chat, send message, verify fallback response text appears (not "No response received") |
| P2-03 | Verify: warning banner still shows | Confirm "AI agent service is currently unavailable" banner still appears |
| P2-04 | Verify: Strategy 1 unaffected | If vLLM is up, verify normal chat still works (skip if vLLM not available) |

### Rollback
```bash
# Revert the single line change in route.ts
# The done event goes back to not having final_text
```

### Gate P2
```
P2-01: Strategy 3 done event JSON includes final_text field
P2-02: Chat with agent down shows helpful response text (not "No response received")
P2-03: Warning banner "AI agent service is currently unavailable" still displays
P2-04: make validate-local PASS
```

---

## Phase 3: UX Polish

**Complexity:** S (minor edits to quarantine page)
**Blast Radius:** Quarantine page component only
**Surface 9 compliance:** Read `/frontend-design` skill; check `.claude/rules/design-system.md`

### Tasks

| # | Task | File |
|---|------|------|
| P3-01 | Read `/frontend-design` skill and `.claude/rules/design-system.md` | Reference only |
| P3-02 | Improve operator name input: add descriptive placeholder, tooltip or help text | `apps/dashboard/src/app/quarantine/page.tsx` (~line 113 area) |
| P3-03 | Fix `working` state: set `true` during approve/reject/escalate async operations (not just delete) | `page.tsx` — wrap `setApproving`/`setRejecting` etc. or use `working` state in those handlers |
| P3-04 | Remove dead preview route | Delete `apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts` (dead code — queries wrong table) |
| P3-05 | Browser verify: operator name has clear placeholder/help | Visual check |
| P3-06 | Browser verify: buttons show loading state during operations | Click approve, verify buttons disable during async call |

### Rollback
```bash
# Revert page.tsx changes
git checkout apps/dashboard/src/app/quarantine/page.tsx
# Restore dead preview route if needed
```

### Gate P3
```
P3-01: Operator name input has descriptive placeholder text
P3-02: Approve/reject/escalate operations disable buttons while in progress
P3-03: Dead preview route file deleted
P3-04: make validate-local PASS
P3-05: npx tsc --noEmit PASS (in apps/dashboard)
```

---

## Dependency Graph

```
Phase 0 (pre-flight)
    |
    v
Phase 1 (quarantine routes) ---> Phase 3 (UX polish)
    |
    v
Phase 2 (chat fallback)

Phase 1 and Phase 2 are independent — can run in any order.
Phase 3 depends on Phase 1 (needs working preview to test loading states).
```

---

## Acceptance Criteria

| AC# | Criterion | Gate(s) |
|-----|-----------|---------|
| AC-1 | Quarantine preview loads when clicking any item (no "Preview not found") | P1-04 |
| AC-2 | Per-item Escalate/Reject/Approve buttons are enabled when preview is loaded | P1-05 |
| AC-3 | Single-item approve creates a deal and redirects to deal page | P1-06 |
| AC-4 | Single-item reject changes item status with reason | P1-07 |
| AC-5 | Bulk approve via checkbox selection bar works | P1-08 |
| AC-6 | Bulk reject via checkbox selection bar works | P1-08 (extend test) |
| AC-7 | Undo-approve route returns JSON (not HTML 404) | P1-03 |
| AC-8 | Chat fallback shows helpful text when agent is down (not "No response received") | P2-02 |
| AC-9 | Chat warning banner still displays when agent is down | P2-03 |
| AC-10 | Operator name input has clear purpose indication | P3-01 |
| AC-11 | Action buttons show loading state during async operations | P3-02 |
| AC-12 | No regression: `make validate-local` PASS | P1-10, P2-04, P3-04 |
| AC-13 | No regression: `npx tsc --noEmit` PASS in dashboard | P3-05 |
| AC-14 | All changes recorded in `/home/zaks/bookkeeping/CHANGES.md` | Post-task |

---

## Guardrails

1. **MUST NOT** modify any backend code (`/home/zaks/zakops-backend/`)
2. **MUST NOT** modify the middleware routing logic (`middleware.ts` `handledByRoutes` list)
3. **MUST NOT** modify generated files (`*.generated.ts`, `*_models.py`)
4. **MUST NOT** change the quarantine page component's approve/reject/escalate logic (only UX polish in Phase 3)
5. **MUST NOT** reference port 8090
6. **MUST** use `backendFetch()` in all new route handlers (not raw `fetch` with hardcoded URLs)
7. **MUST** follow the exact proxy pattern from `process/route.ts` for error handling (catch -> 502)
8. **MUST** run `make validate-local` after each phase
9. **MUST** fix CRLF and ownership on all new files
10. **MUST** record all changes in `/home/zaks/bookkeeping/CHANGES.md`

---

## Executor Self-Check Prompts

After Phase 1:
- "Can I click a quarantine item and see its preview data?" (YES required)
- "Can I approve a single item from the detail view?" (YES required)
- "Does `curl /api/quarantine/bulk-process` return JSON, not HTML?" (YES required)

After Phase 2:
- "When the agent is down, does chat show helpful text instead of 'No response received'?" (YES required)

After Phase 3:
- "Is it obvious what the operator name field is for without prior knowledge?" (YES required)

---

## File Paths Reference

### Files to Create

| File | Purpose |
|------|---------|
| `apps/dashboard/src/app/api/quarantine/[id]/route.ts` | GET detail proxy (RC-1) |
| `apps/dashboard/src/app/api/quarantine/bulk-process/route.ts` | POST bulk-process proxy (RC-2) |
| `apps/dashboard/src/app/api/quarantine/[id]/undo-approve/route.ts` | POST undo-approve proxy (RC-5) |

### Files to Modify

| File | Change |
|------|--------|
| `apps/dashboard/src/app/api/chat/route.ts` | Add `final_text` to Strategy 3 done event (~line 247) |
| `apps/dashboard/src/app/quarantine/page.tsx` | Operator name placeholder + working state fix |

### Files to Delete

| File | Reason |
|------|--------|
| `apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts` | Dead code — queries actions table instead of quarantine table |

### Files to Read (Reference Only)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/FORENSIC-QUARANTINE-CHAT-2026-02-15.md` | Forensic audit with full evidence |
| `apps/dashboard/src/app/api/quarantine/[id]/process/route.ts` | Reference pattern for new routes |
| `apps/dashboard/src/lib/backend-fetch.ts` | backendFetch utility |
| `apps/dashboard/src/lib/api.ts` | Frontend API functions (lines 912-1005) |
| `apps/dashboard/src/middleware.ts` | Middleware routing context |

---

## Stop Condition

Mission is DONE when:
1. All 14 acceptance criteria PASS
2. `make validate-local` PASS
3. `npx tsc --noEmit` PASS in `apps/dashboard`
4. All changes recorded in CHANGES.md
5. Quarantine approve/reject/escalate is operational from the UI (browser-verified)
6. Chat shows fallback text when agent is down (browser-verified)
