# CODEX INSTRUCTION: Generate Dashboard Round 4 Mission Prompts (Batch-by-Batch)

## What This Document Is

You (Codex) are being tasked with generating **mission prompts** for Claude Code to execute. You will generate **one batch at a time**, following a 10-batch execution plan. Each batch is a self-contained mission prompt file that Claude Code will receive, execute, and complete before you generate the next one.

**You are NOT executing these missions.** You are writing the mission prompts that Claude Code will follow.

---

## Your Source Material

You have access to the following files in the repository. **Read them before generating any batch.**

### Primary Source (THE WORK TO BE DONE)
- **`/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md`** — The full 1,300-line dashboard audit document containing all findings (REC-001 through REC-042), upgrade items (UP-01 through UP-25), design specs (Settings Redesign, Onboarding Redesign), E2E test definitions (E2E-001 through E2E-009), and page audits. **This is the work backlog.** Every item in the batches below comes from this document.

### Format References (HOW TO STRUCTURE THE PROMPTS)
- **`/home/zaks/bookkeeping/docs/MISSION-INFRA-AWARENESS-001-V3.md`** — The structural template. Match its hardening format: header block with mission ID/codename/priority/executor/authority, ASCII directive box, context section, discovery section (Section 0), numbered fix sections with bash verification commands, gate checks after each fix, verification sequence, autonomy rules, output format template, and hard rules.
- **`/home/zaks/zakops-agent-api/.claude/missions/MISSION-AGENT-ARCH-001.md`** — Another reference for the same format pattern.

### System Context (WHAT THE CODEBASE LOOKS LIKE)
- **`/home/zaks/zakops-agent-api/CLAUDE.md`** (or `ONBOARDING.md`) — Current system guide with all 7 contract surfaces, service ports, database mappings, and codegen pipeline documentation.
- **`/home/zaks/zakops-agent-api/Makefile`** — All available make targets including sync-types, validate-local, etc.
- **`/home/zaks/zakops-agent-api/apps/dashboard/`** — The Next.js dashboard codebase being modified.
- **`/home/zaks/zakops-backend/`** — The FastAPI backend where new endpoints are added.
- **`/home/zaks/zakops-agent-api/apps/agent-api/`** — The Agent API service.
- **`/home/zaks/zakops-agent-api/packages/contracts/`** — All OpenAPI specs and contract schemas.

### Project History (LESSONS LEARNED)
- **`/home/zaks/bookkeeping/docs/handoff-summary.md`** — Full context on what happened before: Hybrid Guardrail, Red-Team Review, V5PP-MQ1, adversarial verification that found 8 blockers the builder missed.

---

## The Mission Prompt Format

Every batch mission prompt you generate MUST follow this exact structure. Do not deviate.

```
# CLAUDE CODE MISSION: DASHBOARD ROUND 4 — BATCH [N]: [BATCH TITLE]
## Mission ID: DASHBOARD-R4-BATCH-[N]
## Codename: "[creative codename]"
## Priority: [P0/P1/P2]
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Build everything, verify everything

[ASCII directive box explaining what this batch does and why]

---

## CONTEXT
[What was completed in previous batches. What this batch depends on.
 What the current system state should be.]

---

## SECTION 0: PREFLIGHT VERIFICATION
[Bash commands to verify prerequisites from previous batches are working.
 Service health checks. File existence checks. If a prerequisite fails,
 the builder must fix it before proceeding.]

---

## FIX 1 (P[x]): [REC-NNN] [TITLE]
[Detailed instructions for the first item in this batch]

### Step 1A: [substep]
[Exact file paths, code changes, bash commands]

### Step 1B: [substep]
[More details]

### Verification
[Exact curl commands, grep checks, or browser verification steps]

```
GATE 1: [Specific pass/fail criteria with exact commands]
```

---

## FIX 2 (P[x]): [REC-NNN] [TITLE]
[Same pattern for each item]

---

## VERIFICATION SEQUENCE
[Ordered list of all verifications to run after all fixes in this batch]

---

## AUTONOMY RULES
[Standard rules: if something is broken → fix it; if something is missing → create it;
 adapt to what you find; don't stop unless genuinely blocked]

---

## OUTPUT FORMAT
[Completion report template with table of fix results, evidence locations,
 final verification exit codes]

---

## HARD RULES
[Batch-specific non-negotiable rules]
```

---

## The 10 Batches — What Goes Where

### CRITICAL MODIFICATION: Playwright Installation

**Playwright MUST be installed in Batch 0, not Batch 9.** The user explicitly requested this. Playwright enables UI testing throughout all subsequent batches, so every batch that involves UI changes can have browser-based verification from the start.

Add to Batch 0:
- Install Playwright: `npx playwright install --with-deps chromium`
- Install Playwright test: `npm install -D @playwright/test` (in dashboard)
- Create a basic `playwright.config.ts` in the dashboard
- Verify: `npx playwright test --list` runs without error
- Create a smoke test that opens localhost:3003 and verifies the page loads

This means batches 1-9 can all include Playwright-based verification steps alongside curl proofs.

---

### Batch 0: Foundation (Auth + Preflight + Playwright)

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-0.md`

**Items from source document:**
- REC-005 (API key injection into `apiFetch`)
- Gate 0 preflight verification (all services reachable and healthy)
- Playwright installation and configuration (ADDED — user requirement)

**What the prompt must instruct Claude Code to do:**
1. Wire `X-API-Key` header into all write calls in `lib/api.ts` (or wherever `apiFetch` is defined)
2. Audit all Next.js proxy routes (`/app/api/**`) to ensure they forward the API key
3. Install Playwright with Chromium in the dashboard project
4. Create `playwright.config.ts` pointing at localhost:3003
5. Create a smoke test: `tests/e2e/smoke.spec.ts` that opens the app and verifies basic rendering
6. Verify: `curl` without key → 401; `curl` with key → 200; browser write operations work

**Gate criteria:**
- All backend write endpoints return 401 without X-API-Key
- All backend write endpoints return 200/201 with correct X-API-Key
- `npx playwright test tests/e2e/smoke.spec.ts` passes
- No proxy route silently drops the auth header

**Dependencies:** None (this is the foundation)

**Estimated scope:** Small-Medium (~200-300 line prompt)

---

### Batch 1: P0 Routing + Missing Endpoints

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-1.md`

**Items from source document:**
- REC-001 (deal routing slug guard — `/deals/GLOBAL` or similar non-UUID routes crash the app)
- REC-002 (POST /api/deals — create deal endpoint + Next.js proxy)
- REC-003 (quarantine delete endpoint + proxy)
- REC-004 (bulk delete fix)

**What the prompt must instruct Claude Code to do:**
1. Add slug validation in the deal detail route (reject non-UUID patterns before hitting the API)
2. Add `POST /api/deals` backend endpoint if missing, plus the Next.js proxy route
3. Add quarantine delete endpoint on backend + corresponding proxy
4. Fix bulk delete (wrong HTTP method or missing proxy)

**Gate criteria:**
- `/deals/new` renders the create deal form (not a crash)
- `/deals/GLOBAL` shows a 404 page or redirects (not a crash)
- `curl -X POST /api/deals` with valid payload → 201
- `curl -X DELETE /api/quarantine/{id}` → 200
- Bulk delete with multiple IDs → 200

**Dependencies:** Batch 0 (auth must work for write verification)

**Include in verification:** Playwright test that navigates to `/deals/new` and verifies it renders.

---

### Batch 2: P1 Actions + Quarantine Cluster

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-2.md`

**Items from source document:**
- REC-009 (quarantine approve/reject wiring)
- REC-010 (quarantine preview ID fix)
- REC-011 (clear completed actions)
- REC-012 (capabilities 501 resolution)
- REC-019 (actions execute endpoint)
- DL-042 (actions count display bug)

**What the prompt must instruct Claude Code to do:**
1. Wire quarantine approve/reject buttons to real backend endpoints
2. Fix the quarantine preview passing wrong ID format
3. Add "clear completed actions" endpoint + UI button
4. Resolve the 501 on capabilities endpoint (either implement or stub with proper response)
5. Add actions execute endpoint + proxy
6. Fix actions count showing wrong number in UI

**Gate criteria:**
- Quarantine approve creates a deal from the quarantined item
- Quarantine reject removes the item
- No 405 or 501 responses from any actions/quarantine endpoint
- Actions count in sidebar matches actual count from API

**Dependencies:** Batch 1 (quarantine delete pattern reused)

---

### Batch 3: Chat + Agent Fixes

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-3.md`

**Items from source document:**
- REC-013 (markdown rendering with react-markdown)
- REC-006 (hybrid search OR RAG reindex for deal count alignment)
- REC-015 (settings test connection 405 fix)
- REC-018 (Ask Agent sidebar state verification)

**What the prompt must instruct Claude Code to do:**
1. Install `react-markdown` and `remark-gfm`, replace raw text rendering in chat with markdown
2. Fix deal count mismatch between database and agent's reported count (this is the most complex item — may involve hybrid search implementation or RAG reindex)
3. Fix the 405 on settings test connection button
4. Verify the Ask Agent sidebar shares state correctly with the main chat view

**Gate criteria:**
- Bold, italic, links, and code blocks render correctly in chat messages
- Deal count from `GET /api/deals` matches what the agent reports
- Test connection button returns 200 (not 405)
- Opening sidebar chat and sending a message works

**Note in prompt:** REC-006 (hybrid search/deal count) is the most complex single item. If it proves too large, the builder should document what was done and what remains, rather than blocking the entire batch.

**Dependencies:** Batch 0 (auth for agent writes)

---

### Batch 4: Settings Redesign (Full Spec)

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-4.md`

**Items from source document:**
- REC-008 (email integration section)
- All 6 sections from the Settings Redesign spec in the source document:
  - AI Provider (fix existing)
  - Email Integration (new section)
  - Agent Configuration (new section)
  - Notification Preferences (new section)
  - Data & Privacy (new section)
  - Appearance & Theme (new section)

**What the prompt must instruct Claude Code to do:**
1. Read the Settings Redesign spec from the source document and implement all 6 sections
2. Create new backend endpoints for user preferences persistence (`GET/PUT /api/settings/preferences`)
3. Create email integration connection flow (can be stubbed for actual OAuth)
4. Build each settings section as a separate component
5. Wire form submissions to persist via API

**Gate criteria:**
- Each of the 6 settings sections renders
- Form submissions persist (refresh page → values retained)
- Test connection button works
- Email connect flow initiates (even if OAuth is stubbed)

**Note in prompt:** Backend endpoints for email OAuth may need to be stubbed initially. The UI and API contract should be built even if the actual OAuth flow isn't wired to a real provider yet. Mark any stubs with `// STUB: [reason]` comments.

**Dependencies:** Batch 3 (test connection fix is part of Settings)

---

### Batch 5: Onboarding Redesign (Full Spec)

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-5.md`

**Items from source document:**
- REC-007 (backend persistence for onboarding)
- Full Onboarding Redesign spec from the source document:
  - Welcome screen
  - Profile Setup
  - Email Configuration
  - Meet Your Agent (live demo)
  - Resume/re-entry capability

**What the prompt must instruct Claude Code to do:**
1. Read the Onboarding Redesign spec from the source document
2. Create 6 new backend endpoints for onboarding state management
3. Replace localStorage-only onboarding with backend-persisted, resumable flow
4. Implement state machine logic for step progression
5. Create demo data management for "Meet Your Agent" step
6. Implement resume from interrupted step

**Gate criteria:**
- Complete onboarding → refresh → stays on dashboard (not sent back to onboarding)
- `GET /api/onboarding/status` returns `completed` after finishing
- Close browser mid-onboarding → reopen → resumes from correct step
- "Meet Your Agent" demo shows a working interaction

**Dependencies:** Batch 4 (email config section reused in onboarding Step 3)

---

### Batch 6: P2 Quality Hardening

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-6.md`

**Items from source document:**
- REC-020 (Zod strict mode)
- REC-024 (standardize loading states)
- REC-025 (error boundaries)
- REC-026 (no mocks in production)
- REC-029 (correlation ID)
- REC-030 (standardize error format)
- REC-027 (operator identity validation)
- REC-028 (idempotency enforcement)
- DL-026 (mock fallback behavior)

**Absorbed upgrades:**
- UP-03 (correlation ID) = REC-029
- UP-14 (typed error protocol) = REC-030
- UP-18 (graceful degradation)
- UP-24 (runtime safeParse watchdog)

**What the prompt must instruct Claude Code to do:**
1. Enable Zod strict mode — reject unknown fields in API responses
2. Create a standard `<LoadingState>` component used everywhere
3. Add React error boundaries around major page sections
4. Remove all mock/fallback data from production code paths
5. Add correlation ID middleware (generate on frontend, pass via header, log on backend)
6. Create `normalizeError()` function that handles all backend error shapes
7. Add operator identity validation for write operations
8. Add idempotency key middleware for POST/PUT operations

**Gate criteria:**
- Zod rejects payloads with unknown fields
- Error boundaries catch component crashes without taking down the whole page
- No mock data in production builds (`grep -r "MOCK\|mockData\|fallbackData" src/`)
- Correlation ID appears in response headers and backend logs
- Duplicate idempotency key returns 409

**Dependencies:** Batches 0-5 (hardens features that should already exist)

---

### Batch 7: P2/P3 UX Polish

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-7.md`

**Items from source document:**
- REC-021 (pagination)
- REC-022 (filter URL persistence)
- REC-023 (keyboard accessibility)
- REC-031 (SSE reconnect)
- REC-035 (button debounce)
- REC-036 (timezone handling)
- REC-037 (dark mode toggle location)
- REC-038 (activity timeline per deal)
- REC-033 (CSV/PDF export)
- REC-034 (concurrent edit handling)
- REC-039 (responsive breakpoints)

**Absorbed upgrades:**
- UP-05 (optimistic UI)
- UP-06 (command palette)
- UP-09 (data sync indicator)
- UP-15 (feature flags)
- UP-17 (audit trail UI) = REC-038
- UP-20 (SSE resilient) = REC-031
- UP-22 (bulk preview/rollback)

**What the prompt must instruct Claude Code to do:**
1. Add pagination to deal list (with page size selector)
2. Persist filters in URL query params (back button preserves filters)
3. Add keyboard navigation (tab order, arrow keys in lists)
4. Implement SSE reconnect with exponential backoff
5. Add debounce to all action buttons
6. Handle timezone display correctly
7. Move dark mode toggle to accessible location
8. Add per-deal activity timeline
9. Add CSV export for deal lists
10. Handle concurrent edits (optimistic locking or last-write-wins with warning)
11. Add responsive breakpoints

**Gate criteria:**
- Pagination works with >20 items
- Filters survive browser back navigation
- Tab order is logical through major UI elements
- SSE reconnects after disconnection
- Rapid double-click on action button doesn't fire twice

**Note in prompt:** This is the batch most likely to have items deferred. If something proves impractical (like full concurrent edit handling), document it in the completion report as a deferred item with the reason — do not silently skip it.

**Dependencies:** Batches 0-6

---

### Batch 8: Page Audits (HQ + Agent Activity)

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-8.md`

**Items from source document:**
- REC-016 (audit /hq page)
- REC-017 (audit /agent/activity page)
- DL-016, DL-017

**Absorbed upgrades:**
- UP-16 (health dashboard) — ties to HQ audit
- UP-21 (ops health ribbon)

**What the prompt must instruct Claude Code to do:**
1. Navigate to `/hq` and document every component, data source, and issue found
2. Navigate to `/agent/activity` and do the same
3. Fix every issue found (broken charts, missing data, wrong parsing, dead links)
4. Ensure both pages work with real data

**Gate criteria:**
- Both pages load without console errors
- Charts render with actual data (not empty or mock)
- Timeline/activity feed parses and displays correctly
- No dead links or buttons

**Note in prompt:** This batch is exploratory. The scope is unknown until the builder actually audits the pages. The prompt should instruct the builder to document everything found, fix what's fixable, and report anything that requires other batches' work to complete.

**Dependencies:** Batches 0-2 (underlying endpoints should work)

---

### Batch 9: E2E Tests + CI Gates

**File to generate:** `MISSION-DASHBOARD-R4-BATCH-9.md`

**Items from source document:**
- E2E-001, E2E-002, E2E-004, E2E-006, E2E-007, E2E-009 (all 6 E2E test suites)
- REC-040 (contract gate CI)
- REC-041 (dead UI gate CI)
- REC-042 (observability gate CI)
- Click-all-buttons sweep

**Absorbed upgrades:**
- UP-02 (click-every-button test)
- UP-10 (dead UI ESLint)
- UP-11 (visual regression) — defer if impractical
- UP-23 (method/route diff CI) = REC-040

**What the prompt must instruct Claude Code to do:**
1. Implement all 6 E2E test suites using Playwright (already installed from Batch 0)
2. Create the click-all-buttons sweep test that finds every `<button>` and `<a>` element and verifies none return 404/405/500
3. Wire contract validation as a CI gate
4. Wire dead UI detection as a CI gate
5. Wire observability checks as a CI gate

**Gate criteria:**
- All 6 E2E tests pass: `npx playwright test`
- Click-all-buttons finds no dead UI (0 elements that return error responses)
- CI gates block on violations (not advisory)
- All tests are deterministic (run 3 times, same result)

**Dependencies:** ALL previous batches (tests verify features that must exist)

---

## How to Generate Each Batch

### Step 1: Read the Source Document
Before generating batch N, read:
- The full source document (`MISSION-DASHBOARD-ROUND4-EXEC-001.md`) to find the specific REC items, their detailed descriptions, file paths, and code snippets
- The system context files (CLAUDE.md, Makefile) to know current paths and targets
- The previous batch's completion report (if available) to understand what was done

### Step 2: Extract Item Details
For each item (e.g., REC-005) in the batch, extract from the source document:
- The exact problem description
- The affected file paths
- The suggested fix (if provided)
- The verification method (curl commands, browser checks, etc.)
- The priority level

### Step 3: Write the Prompt
Using the format template above, write the complete mission prompt. Include:
- **Exact file paths** — not vague references. Look them up from the codebase.
- **Exact bash commands** — curl proofs with specific URLs, grep checks, etc.
- **Before/after code snippets** — when the source document provides them.
- **Gate criteria** — specific, measurable, binary pass/fail conditions.
- **Evidence requirements** — where to store before/after artifacts.

### Step 4: Include Playwright Verification Where Applicable
Since Playwright is installed in Batch 0, every subsequent batch that modifies UI should include at least one Playwright verification step. For example:
- Batch 1: Playwright test navigating to `/deals/new` to verify rendering
- Batch 2: Playwright test clicking the quarantine approve button
- Batch 3: Playwright test sending a chat message and verifying markdown renders
- Batch 4: Playwright test navigating through all Settings sections
- etc.

### Step 5: Include Cross-Batch Awareness
Each batch prompt should include a "CONTEXT" section that lists:
- Which previous batches are complete
- What key artifacts/endpoints were created
- What the builder should verify still works before starting new work

---

## Evidence Structure

Every batch must instruct the builder to create evidence in:

```
/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/
├── batch-0/
│   ├── evidence/
│   │   ├── auth-injection/
│   │   ├── playwright-install/
│   │   └── service-health/
│   └── completion-report.md
├── batch-1/
│   ├── evidence/
│   │   ├── rec-001-slug-guard/
│   │   ├── rec-002-create-deal/
│   │   ├── rec-003-quarantine-delete/
│   │   └── rec-004-bulk-delete/
│   └── completion-report.md
├── ...
```

---

## QA Checklist Generation

After Claude Code completes each batch, the user will need a QA verification checklist. **You do NOT generate this checklist with the batch prompt.** The user will request it separately after the builder claims completion. When asked, generate a focused QA checklist that:

1. Tests each item independently (not dependent on the builder's claimed state)
2. Includes adversarial tests for Batches 0-3 (intentionally try to break things)
3. Includes standard functional tests for Batches 4-9
4. Uses Playwright for UI verification
5. Uses curl for API verification
6. Is runnable as a single script

---

## Upgrade Items Mapping

These upgrade items from the source document are absorbed into the batches. Do NOT create separate items for them — they are part of the batch they're assigned to:

| Upgrade | Absorbed Into | Notes |
|---------|---------------|-------|
| UP-01 (contract-first client gen) | Already done (Hybrid Guardrail) | Skip |
| UP-02 (click-every-button test) | Batch 9 | |
| UP-03 (correlation ID) | Batch 6 (= REC-029) | |
| UP-04 (unified ops API) | Batch 6 or defer | Based on complexity |
| UP-05 (optimistic UI) | Batch 7 | |
| UP-06 (command palette) | Batch 7 | |
| UP-07 (BFF layer) | Evaluate in Batch 3 | Implement if natural, defer if not |
| UP-08 (hybrid search) | Batch 3 (= REC-006) | |
| UP-09 (data sync indicator) | Batch 7 | |
| UP-10 (dead UI ESLint) | Batch 9 | |
| UP-11 (visual regression) | Batch 9 or defer | |
| UP-12 (capability-based UI) | Batch 2 | Ties to capabilities endpoint |
| UP-13 (schema-driven forms) | Batch 4 | Settings is natural place |
| UP-14 (typed error protocol) | Batch 6 (= REC-030) | |
| UP-15 (feature flags) | Batch 7 | |
| UP-16 (health dashboard) | Batch 8 | Ties to HQ audit |
| UP-17 (audit trail UI) | Batch 7 (= REC-038) | |
| UP-18 (graceful degradation) | Batch 6 | |
| UP-19 (API versioning) | Evaluate in Batch 6 | Likely defer |
| UP-20 (SSE resilient) | Batch 7 (= REC-031) | |
| UP-21 (ops health ribbon) | Batch 8 | |
| UP-22 (bulk preview/rollback) | Batch 7 | |
| UP-23 (method/route diff CI) | Batch 9 (= REC-040) | |
| UP-24 (runtime safeParse watchdog) | Batch 6 | |
| UP-25 (unified SSE provider) | Batch 3 | |

Nothing is dropped. Items that prove impractical during execution get documented in the completion report's deferred section — never silently skipped.

---

## Workflow Summary

```
You (Codex) generate Batch 0 prompt
    ↓
User gives Batch 0 prompt to Claude Code
    ↓
Claude Code executes Batch 0
    ↓
User (optionally) asks you for a QA checklist for Batch 0
    ↓
User verifies / remediates if needed
    ↓
User asks you to generate Batch 1 prompt
    ↓
You read the Batch 0 completion report (if available) for context
    ↓
You generate Batch 1 prompt (includes Batch 0 context in the CONTEXT section)
    ↓
... repeat until Batch 9 is complete ...
```

---

## Key Principles to Embed in Every Prompt

1. **Zero-trust verification.** The builder must prove every fix works with evidence (curl output, grep results, Playwright screenshots). "It should work" is not evidence.

2. **Playwright from day one.** Every UI change gets a Playwright verification step alongside manual curl proofs.

3. **Exact file paths.** Look up real paths from the codebase. Never say "find the relevant file." Say `apps/dashboard/src/lib/api.ts`.

4. **Gate criteria are binary.** Either the gate passes or it doesn't. No "partially meets expectations."

5. **Autonomy rules.** If something is broken → fix it. If something is missing → create it. If a backend endpoint doesn't exist → create it. Don't ask — do.

6. **Deferred items are documented, not hidden.** If the builder can't complete an item, it goes in the completion report with the reason. Silent skipping is a failure.

7. **Contract surfaces.** Any new backend endpoint needs `response_model` in FastAPI. Any schema change triggers the appropriate `make sync-*` target. The Hybrid Guardrail is non-negotiable.

8. **Batch isolation.** Each batch is self-contained. It lists its own dependencies, its own gates, its own verification sequence. A builder should be able to execute the batch with ONLY the batch prompt and the source document.

---

## Start Here

**Generate Batch 0 first.** The user will tell you when to generate each subsequent batch.

When the user says: "Generate Batch N" — you read the source document, extract the items for that batch, and produce the complete mission prompt file following everything described above.

The output filename for each batch is: `MISSION-DASHBOARD-R4-BATCH-[N].md`
