# CLAUDE CODE MISSION: DASHBOARD ROUND 4 — BATCH 3: CHAT + AGENT ALIGNMENT
## Mission ID: DASHBOARD-R4-BATCH-3
## Codename: "Signal Harmony"
## Priority: P0 (contains REC-006)
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Build everything, verify everything

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   EXECUTION DIRECTIVE                                                        ║
║                                                                              ║
║   This batch fixes the CHAT trust layer and the Ask Agent sidebar:            ║
║   - Markdown rendering (no raw **bold**)                                      ║
║   - Deal count mismatch between agent and UI                                 ║
║   - Settings “Test Connection” 405                                           ║
║   - Ask Agent drawer must share state with main chat                          ║
║                                                                              ║
║   Goal: One source of truth, one chat pipeline, one consistent UX.            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## CONTEXT
- Depends on Batch 0 (auth + Playwright) and Batch 1/2 for API stability.
- Primary source: /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md
- This batch touches dashboard UI, Next API route /api/chat, and agent tool behavior.

---

## SECTION 0: PREFLIGHT VERIFICATION
Evidence directory:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-3/evidence/`

```bash
BASE_EVIDENCE=/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-3/evidence
mkdir -p "$BASE_EVIDENCE/preflight" "$BASE_EVIDENCE/rec-006" "$BASE_EVIDENCE/rec-013" \
  "$BASE_EVIDENCE/rec-015" "$BASE_EVIDENCE/rec-018" "$BASE_EVIDENCE/playwright"

# Service health
curl -s http://localhost:8091/health | tee "$BASE_EVIDENCE/preflight/01-backend-health.json"
curl -s http://localhost:8095/health | tee "$BASE_EVIDENCE/preflight/02-agent-health.json"

# Chat API health (dashboard proxy)
curl -i http://localhost:3003/api/chat | tee "$BASE_EVIDENCE/preflight/03-chat-get.txt"

# Deal counts (backend vs dashboard proxy)
BACKEND_COUNT=$(curl -s http://localhost:8091/api/deals | jq 'if type=="array" then length else (.deals|length) end')
DASH_COUNT=$(curl -s http://localhost:3003/api/deals | jq 'if type=="array" then length else (.deals|length) end')
printf "backend=%s\ndashboard=%s\n" "$BACKEND_COUNT" "$DASH_COUNT" | tee "$BASE_EVIDENCE/preflight/04-deal-counts.txt"
```

If health or /api/chat fails, fix before proceeding.

---

## FIX 1 (P1): REC-013 — Add Markdown Rendering w/ Sanitization
**Source text (verbatim):** “Add `react-markdown` with `rehype-sanitize` (strict allowlist) to chat”

### Step 1A: Install dependencies
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard
npm install react-markdown remark-gfm rehype-sanitize | tee "$BASE_EVIDENCE/rec-013/01-install.txt"
```

### Step 1B: Implement Markdown renderer in chat message bubbles
Target files:
- `apps/dashboard/src/app/chat/page.tsx` (MessageBubble)
- `apps/dashboard/src/components/agent/AgentDrawer.tsx` (Ask Agent drawer)
- (Optional) `apps/dashboard/src/components/deal-workspace/DealChat.tsx` if still used

Required changes:
1. Replace raw `<div className='whitespace-pre-wrap text-sm'>{message.content}</div>` with a Markdown renderer.
2. Use `react-markdown` + `remark-gfm` + `rehype-sanitize` with a **strict allowlist**:
   - allowed tags: `p`, `strong`, `em`, `ul`, `ol`, `li`, `code`, `pre`, `a`, `blockquote`
   - allow `a` with `href`, `target`, `rel` only
3. Ensure `target="_blank"` + `rel="noopener noreferrer"` on links.
4. Preserve `whitespace-pre-wrap` behavior with Markdown where needed.

Example implementation note:
- Create a reusable `MarkdownMessage` component in `apps/dashboard/src/components/chat/MarkdownMessage.tsx` and use it in all chat UIs.

### Verification
Manual proof:
```bash
# Inspect rendered output in DOM via Playwright (see Playwright step below)
```

```
GATE 1:
- User message with "**bold**" renders as <strong>bold</strong> in chat UI
- No raw markdown characters visible for standard Markdown syntax
```

---

## FIX 2 (P0): REC-006 — Deal Count Alignment (Hybrid Search or Reindex)
**Source text (verbatim):** “Implement Hybrid Search (RAG + SQL) in agent OR trigger RAG reindex on deal changes”

### Step 2A: Prove actual data source used by agent
Files to inspect:
- `apps/agent-api/app/core/langgraph/tools/deal_tools.py` (list_deals/search_deals)
- `apps/agent-api/app/core/prompts/system.md` (tool routing)

Commands:
```bash
rg -n "list_deals|search_deals" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py | tee "$BASE_EVIDENCE/rec-006/01-tools.txt"
rg -n "How many deals|list_deals" /home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/system.md | tee "$BASE_EVIDENCE/rec-006/02-prompt.txt"
```

### Step 2B: Fix mismatch by aligning tool behavior and defaults
Common mismatch causes:
- Agent tool defaults to `status="active"` while UI shows all deals
- Agent answers from memory without calling list_deals
- RAG index stale or incomplete

You must choose **one** of the following **and document your choice**:

**Option A (Preferred): Backend-first count**
1. Ensure agent uses `list_deals` for count queries (update `system.md` if needed).
2. Change `list_deals` default `status` to match UI (e.g., `status=None` or `status="all"`).
3. In chat UI, show provenance badge “Source: DB” for responses that include list_deals metadata.

**Option B: Hybrid Search**
1. Use backend list_deals for authoritative count.
2. Use RAG for semantic ranking ONLY (do not use RAG for counts).
3. Add `metadata.source="backend_api"` in agent response and surface it in UI.

**Option C: RAG Reindex on Deal Changes**
1. If the agent still uses RAG for deal lookup, trigger reindex on deal create/transition.
2. Ensure reindex is idempotent and logged.
3. Add “Source: RAG (fresh)” badge in chat UI when RAG was used.

### Step 2C: Add provenance indicator in chat UI
- In `apps/dashboard/src/app/chat/page.tsx`, add a small badge or footnote in assistant messages:
  - “Source: DB” when count comes from list_deals (backend_api)
  - “Source: RAG” when RAG was used
- If metadata is not currently exposed, add a field in `done` SSE payload in `/api/chat`.

### Verification
```bash
# Backend count
BACKEND_COUNT=$(curl -s http://localhost:8091/api/deals | jq 'if type=="array" then length else (.deals|length) end')

# Ask agent for count (capture SSE)
curl -s -N http://localhost:3003/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"How many deals do I have?"}' | tee "$BASE_EVIDENCE/rec-006/03-chat-sse.txt"

# Manually confirm agent response count matches BACKEND_COUNT
printf "backend=%s\n" "$BACKEND_COUNT" | tee "$BASE_EVIDENCE/rec-006/04-backend-count.txt"
```

```
GATE 2:
- Agent response count matches backend count (no more mismatch)
- Provenance badge rendered (“Source: DB” or “Source: RAG”)
```

---

## FIX 3 (P1): REC-015 — Settings Test Connection 405
**Source text (verbatim):** “Change Test Connection to POST or add GET handler to `/api/chat`”

### Step 3A: Verify /api/chat GET/POST
Files:
- `apps/dashboard/src/app/api/chat/route.ts`
- `apps/dashboard/src/lib/settings/provider-settings.ts`

Commands:
```bash
curl -i http://localhost:3003/api/chat | tee "$BASE_EVIDENCE/rec-015/01-chat-get.txt"
```

### Step 3B: Fix method mismatch
If GET is returning 405 or 4xx:
- Option 1: Update `testConnection()` to use POST with minimal payload.
- Option 2: Ensure GET handler exists in `/api/chat/route.ts` and is not shadowed.

Required outcome:
- “Test Connection” in Settings returns a success or structured failure (not 405).

### Verification
```bash
# UI test (manual or Playwright)
# Click “Test Connection” for Local provider and capture toast output
```

```
GATE 3:
- Test Connection button returns success or known error (no 405/Method Not Allowed)
- /api/chat GET returns JSON with status field
```

---

## FIX 4 (P1): REC-018 + UP-25 — Ask Agent Drawer Shares State with Main Chat
**Source text (verbatim):** “Verify Ask Agent sidebar shares state with main chat; fix if not”

### Step 4A: Replace mock drawer chat with real shared chat client
File: `apps/dashboard/src/components/agent/AgentDrawer.tsx`
- Current behavior: mock response + local state only.

Required change:
1. Extract chat state and streaming logic into a shared hook (e.g., `useChatSession`) in `apps/dashboard/src/lib/chat/session.ts`.
2. Use the same storage key as Chat page (`zakops-chat-session`).
3. Use the same streaming function (`streamChatMessage` from `lib/api.ts`) or create a shared SSE parser.
4. The drawer must **read and write** the same message list as `/chat` page.

### Step 4B: Optional — unify DealWorkspace chat
If `DealWorkspace` still uses simulated chat (`apps/dashboard/src/components/deal-workspace/DealWorkspace.tsx`), migrate it to the same shared chat session so all chat surfaces are consistent.

### Verification
Manual:
1. Open `/chat`, send a message.
2. Open Ask Agent drawer (Dashboard sidebar button).
3. Confirm the drawer shows the same message history.
4. Send a message from drawer; confirm it appears in `/chat`.

```
GATE 4:
- Ask Agent drawer shows same chat session as /chat (messages sync both directions)
- Drawer uses real SSE chat pipeline (no mock text)
```

---

## PLAYWRIGHT VERIFICATION (REQUIRED)
Create a Playwright test to verify markdown rendering + shared Ask Agent state.
Path: `apps/dashboard/tests/e2e/chat-shared.spec.ts`

Test requirements:
1. Navigate to `/chat`, send message `**bold**` and assert `<strong>` rendered.
2. Open Ask Agent drawer from `/dashboard` and verify the same message exists.
3. Send a new message in drawer and verify it appears on `/chat`.

Run:
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard
npx playwright test tests/e2e/chat-shared.spec.ts | tee "$BASE_EVIDENCE/playwright/01-chat-shared.txt"
```

```
GATE 5:
- Playwright test passes
```

---

## VERIFICATION SEQUENCE
After all fixes:
```bash
# Gate 1
cat "$BASE_EVIDENCE/rec-013/01-install.txt"
# Gate 2
cat "$BASE_EVIDENCE/rec-006/03-chat-sse.txt"
cat "$BASE_EVIDENCE/rec-006/04-backend-count.txt"
# Gate 3
cat "$BASE_EVIDENCE/rec-015/01-chat-get.txt"
# Gate 4
# (Manual verification notes + screenshots)
# Gate 5
cat "$BASE_EVIDENCE/playwright/01-chat-shared.txt"
```

---

## AUTONOMY RULES
- If a fix is already implemented, prove it with evidence and move on.
- If the agent doesn’t call list_deals for count queries, update tool routing rules.
- If a required backend/agent endpoint is missing, implement it or log BLOCKER.
- Do not stop unless infrastructure prevents all fixes.

---

## OUTPUT FORMAT
Save completion report:
`/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-3/completion-report.md`

Template:
```
# DASHBOARD-R4 BATCH 3 — COMPLETION REPORT

## Summary
| Fix | Status | Evidence |
|-----|--------|----------|
| REC-013 Chat markdown | PASS/FAIL | path(s) |
| REC-006 Deal count alignment | PASS/FAIL | path(s) |
| REC-015 Test Connection | PASS/FAIL | path(s) |
| REC-018 Ask Agent shared state | PASS/FAIL | path(s) |
| Playwright test | PASS/FAIL | path(s) |

## Gates
| Gate | Result | Evidence |
|------|--------|----------|
| Gate 1 | PASS/FAIL | rec-013/01-install.txt + UI proof |
| Gate 2 | PASS/FAIL | rec-006/03-chat-sse.txt + 04-backend-count.txt |
| Gate 3 | PASS/FAIL | rec-015/01-chat-get.txt |
| Gate 4 | PASS/FAIL | manual notes + screenshots |
| Gate 5 | PASS/FAIL | playwright/01-chat-shared.txt |

## Blockers
- ...

## Notes
- ...
```

---

## HARD RULES
- No mock responses in Ask Agent drawer after this batch.
- Any new agent metadata added must be reflected in OpenAPI if applicable.
- All chat-related changes must use a shared SSE parser or shared chat hook (UP-25).
- Evidence is mandatory for every gate.
