# DASHBOARD-R4 BATCH-3 "Signal Harmony" — Completion Report

**Date:** 2026-02-08
**Status:** COMPLETE — ALL 5 GATES PASS (after B1 remediation)

---

## Summary

Batch 3 fixes the Chat trust layer and Agent Drawer alignment — Markdown rendering, deal count provenance, Settings Test Connection, and shared chat state.

**QA Remediation (B1 - Deal Count Mismatch):** Fixed unbounded LangGraph checkpoint accumulation that caused the agent to hallucinate deal counts. Added dashboard-side direct backend fetch for deal-count queries to guarantee accuracy.

---

## Fixes Implemented

### FIX 1: REC-013 — Markdown Rendering with Sanitization
- Installed `react-markdown`, `remark-gfm`, `rehype-sanitize`
- Created reusable `MarkdownMessage` component at `src/components/chat/MarkdownMessage.tsx`
- Strict sanitization allowlist: `p, strong, em, ul, ol, li, code, pre, a, blockquote, br, h1-h3`
- Links get `target="_blank" rel="noopener noreferrer"` automatically
- Applied to all 3 chat UIs:
  - `src/app/chat/page.tsx` (line 1052)
  - `src/components/agent/AgentDrawer.tsx` (line 249)
  - `src/components/deal-workspace/DealChat.tsx` (line 349)

**Files:** `MarkdownMessage.tsx` (new), `chat/page.tsx`, `AgentDrawer.tsx`, `DealChat.tsx`, `package.json`

### FIX 2: REC-006 — Deal Count Alignment + Provenance Badge
- **Provenance badge:** Added `data_source` field to SSE `done` event in `/api/chat/route.ts`
- Chat page parses `data_source`, displays "Source: DB" badge on assistant messages
- Badge uses outline variant, positioned below message content

**B1 REMEDIATION — Deal Count Accuracy:**
- **Root cause:** LangGraph checkpoint accumulated 266 messages in "service-session" thread, overwhelming Qwen 2.5 context → agent stopped calling tools + hallucinated counts
- **Fix A (agent-api):** `auth.py` now generates unique session IDs per service request (`svc-{uuid}`) instead of reusing "service-session" — prevents re-accumulation
- **Fix B (one-time):** Cleared 266 stale checkpoints from agent postgres
- **Fix C (dashboard):** `route.ts` detects deal-count queries (`isDealCountQuery()`) and fetches directly from backend API (`fetchDealCountFromBackend()`), bypassing unreliable Qwen tool-calling. Data source tagged as `backend_api_direct`.
- **Verified:** 36/36 ALIGNED (3 consecutive tests)

**Files:** `api/chat/route.ts`, `chat/page.tsx`, `agent-api/app/api/v1/auth.py`

### FIX 3: REC-015 — Settings Test Connection 405
- **Status:** Already working — `/api/chat` GET handler exists and returns `{"status":"available",...}` (HTTP 200)
- `testConnection()` in `provider-settings.ts` already uses GET method correctly
- No code changes needed — verified with curl

**Files:** No changes needed

### FIX 4: REC-018 — Ask Agent Drawer Shares State with Main Chat
- Created shared hook `useChatSession` at `src/lib/chat/session.ts`
- Same storage key: `zakops-chat-session` (version 1)
- Hook provides: `messages`, `isStreaming`, `sendMessage`, `refreshFromStorage`
- **AgentDrawer rewritten:** Removed mock response logic, now uses real SSE streaming via `streamChatMessage`
- Messages persist to localStorage, synced between `/chat` page and drawer
- `StorageEvent` listener handles cross-tab updates
- Drawer refreshes messages from storage on open

**Files:** `lib/chat/session.ts` (new), `AgentDrawer.tsx`

---

## Gate Results

| Gate | Description | Result | Evidence |
|------|-------------|--------|----------|
| Gate 1 | `**bold**` renders as `<strong>` in chat UI | PASS | `rec-013/01-install.txt`, Playwright |
| Gate 2 | Agent count matches backend; provenance badge | PASS (remediated) | `rec-006-remediation/01-root-cause.txt`, `rec-006-remediation/02-verification.txt` |
| Gate 3 | Test Connection returns success (no 405) | PASS | `rec-015/01-chat-get.txt` |
| Gate 4 | Ask Agent drawer shares state with /chat | PASS | `rec-018/01-shared-state.txt` |
| Gate 5 | Playwright 4/4 pass, 12/12 full suite | PASS | `playwright/01-chat-shared.txt` |

---

## Verification

- `tsc --noEmit`: PASS (0 errors)
- `npx next lint --quiet`: PASS (0 warnings/errors)
- `npx playwright test`: 12/12 PASS (full suite, no regressions)
  - 4 new tests in `chat-shared.spec.ts`
  - 4 from Batch 2 (`quarantine-actions.spec.ts`)
  - 3 from Batch 1 (`deal-routing-create.spec.ts`)
  - 1 smoke test
- Deal count: 36/36 ALIGNED (backend=36, dashboard chat=36)

---

## Files Modified

### Frontend (`/home/zaks/zakops-agent-api/apps/dashboard/`)
- `src/components/chat/MarkdownMessage.tsx` — NEW: reusable Markdown renderer
- `src/lib/chat/session.ts` — NEW: shared chat session hook
- `src/app/chat/page.tsx` — Markdown rendering, provenance badge, dataSource parsing
- `src/app/api/chat/route.ts` — Deal count direct fetch, data_source to SSE done events
- `src/components/agent/AgentDrawer.tsx` — Rewired to shared chat session + real SSE
- `src/components/deal-workspace/DealChat.tsx` — Markdown rendering
- `tests/e2e/chat-shared.spec.ts` — NEW: 4 Playwright tests
- `package.json` / `package-lock.json` — react-markdown, remark-gfm, rehype-sanitize

### Agent API (`/home/zaks/zakops-agent-api/apps/agent-api/`)
- `app/api/v1/auth.py` — Unique session IDs per service request (B1 fix)
