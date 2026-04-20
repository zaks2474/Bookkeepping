# ZakOps Dashboard Round-4 Remediation Plan

---

## 1) AGENT IDENTITY

- **agent_name:** Claude-Opus
- **run_id:** 20260205-1710-1a20a2
- **date_time:** 2026-02-05T17:10:00Z
- **dashboard_revision:** b96b33c5
- **backend_revision:** 2a68de17
- **forensic_report:** `DASHBOARD_ROUND4_FORENSIC.Claude-Opus.20260205-1710-1a20a2.md`

---

## 2) REMEDIATION STRATEGY

### 2.1 Guiding Principles

1. **Contract-First**: Every UI action MUST have a verified backend endpoint
2. **No Dead UI**: Remove or disable buttons that don't work
3. **Error Transparency**: Show real errors, not masked mock responses
4. **E2E Proof**: Every fix requires E2E test proving the workflow works

### 2.2 Priority Order

1. P0 issues blocking core workflows (4 issues)
2. P1 issues degrading user experience (6 issues)
3. P2 medium issues (5 issues)
4. P3 low issues (2 issues)

---

## 3) PHASED IMPLEMENTATION PLAN

### Phase 0 — Critical Path Unblock (P0 Issues)

**Objective:** Fix the 4 issues that completely block core user workflows.

**Issues Addressed:**
- DL-001: Deal routing bug (`/deals/GLOBAL`, `/deals/new`)
- DL-002: Data integrity mismatch (agent vs UI deal count)
- DL-003: Onboarding demo-only
- DL-004: Missing email configuration

**Tasks:**

| Task ID | Description | File(s) | DoD |
|---------|-------------|---------|-----|
| P0-T1 | Add slug guard to deals `[id]` route | `/deals/[id]/page.tsx` | "new" renders create form, "GLOBAL" renders global view |
| P0-T2 | Create `/deals/new/page.tsx` for new deal creation | New file | Create deal form renders and submits |
| P0-T3 | Investigate deal count mismatch | `/api/deals`, agent tools | Document root cause; same count in both |
| P0-T4 | Build email settings section in Settings page | `/settings/page.tsx` | Gmail OAuth flow configurable from UI |
| P0-T5 | Wire onboarding to backend | `/onboarding/page.tsx`, backend | Onboarding state persists to database |

**Evidence Required:**
- E2E test: Navigate to `/deals/new` → form renders → create deal → redirects to detail
- E2E test: Navigate to `/deals/GLOBAL` → renders global scope view (not error)
- Screenshot: Settings page with email configuration section
- Log: Agent `search_deals` count matches `/api/deals` count

**Gate P0:** All 4 P0 issues closed with verification artifacts

---

### Phase 1 — API Contract Alignment (P1 Issues)

**Objective:** Fix all 405/404 errors and missing endpoint contracts.

**Issues Addressed:**
- DL-005: Quarantine delete 404
- DL-006: Clear completed actions 405
- DL-007: Quarantine preview null
- DL-008: Chat markdown rendering
- DL-009: Deals bulk operation 405
- DL-010: Missing agent configuration

**Tasks:**

| Task ID | Description | File(s) | DoD |
|---------|-------------|---------|-----|
| P1-T1 | Add backend endpoint `/api/quarantine/{id}/delete` | Backend FastAPI | Returns 200 on delete |
| P1-T2 | Add backend endpoint `/api/actions/clear-completed` | Backend FastAPI | Returns 200 with affected_count |
| P1-T3 | Fix quarantine preview endpoint to handle all action types | Backend FastAPI | Preview returns data for all quarantine items |
| P1-T4 | Add react-markdown to chat message rendering | `/chat/page.tsx` | Markdown renders as formatted HTML |
| P1-T5 | Add backend endpoint for deals bulk operations | Backend FastAPI | Bulk archive/delete returns 200 |
| P1-T6 | Add agent configuration section to Settings | `/settings/page.tsx` | Agent settings editable |

**Evidence Required:**
- Curl test: `POST /api/quarantine/{id}/delete` returns 200
- Curl test: `POST /api/actions/clear-completed` returns `{success: true, affected_count: N}`
- Screenshot: Chat with **bold** and _italic_ rendered correctly
- E2E test: Delete quarantine item → removed from list

**Gate P1:** All P1 endpoints return 2xx; no 405/404 errors in CI

---

### Phase 2 — UX Hardening & Technical Debt (P2 Issues)

**Objective:** Complete the feature set and remove technical debt.

**Issues Addressed:**
- DL-011: Onboarding capability cards presentational
- DL-012: Missing buy box criteria
- DL-013: Missing notification preferences
- DL-014: Email settings button dead
- DL-015: Mock fallbacks masking failures

**Tasks:**

| Task ID | Description | File(s) | DoD |
|---------|-------------|---------|-----|
| P2-T1 | Wire onboarding capability cards to real actions | `OnboardingWizard` | Cards navigate to functional settings |
| P2-T2 | Add buy box criteria configuration | `/settings/page.tsx` | Buy box rules saved to backend |
| P2-T3 | Add notification preferences UI | `/settings/page.tsx` | Email/push notification toggles work |
| P2-T4 | Fix "Configure Email Settings" button navigation | `/onboarding/page.tsx` | Button navigates to `/settings#email` |
| P2-T5 | Remove mock fallbacks; fail transparently | All `/api/` routes | No mock data in production |

**Evidence Required:**
- E2E test: Onboarding → Configure Email → Settings email section
- Screenshot: Buy box criteria form
- Code review: No `[Mock]` console.log in production build

**Gate P2:** All P2 issues closed; mock code removed from production bundle

---

### Phase 3 — Polish & Observability (P3 Issues)

**Objective:** Final polish and observability integration.

**Issues Addressed:**
- DL-016: Dashboard Ask Agent sidebar integration
- DL-017: Clear actions count display bug

**Tasks:**

| Task ID | Description | File(s) | DoD |
|---------|-------------|---------|-----|
| P3-T1 | Integrate Dashboard sidebar with main chat session | `/dashboard/page.tsx`, `/chat/` | Messages appear in both views |
| P3-T2 | Fix completed actions count calculation | `/actions/page.tsx` | Count matches actual completed actions |
| P3-T3 | Add correlation_id to all dashboard API calls | `api.ts` | All requests include correlation_id header |
| P3-T4 | Add frontend error tracking | N/A | Sentry/similar captures JS errors |

**Evidence Required:**
- E2E test: Ask Agent in dashboard → see response in `/chat` page
- Screenshot: Clear actions dialog shows correct count
- Log: All API requests have correlation_id

**Gate P3:** All issues closed; observability active

---

## 4) HARD GATES

### Gate A — Contract Verification
- **What:** Every UI button/action has verified backend endpoint
- **How:** OpenAPI spec generated from backend; frontend calls validated against spec
- **Proof:** `openapi.json` matches frontend `api.ts` calls
- **Blocks:** Phase 1 exit

### Gate B — No Dead UI
- **What:** No buttons that trigger errors or do nothing
- **How:** Enumerate all clickable elements; test each one
- **Proof:** E2E test suite covers every button
- **Blocks:** Phase 2 exit

### Gate C — E2E Coverage
- **What:** All P0/P1 workflows have passing E2E tests
- **How:** Playwright test suite
- **Proof:** CI green with E2E job
- **Blocks:** Ship

### Gate D — Observability
- **What:** All API calls traceable end-to-end
- **How:** correlation_id propagation; frontend error tracking
- **Proof:** Sample trace from UI click to backend log
- **Blocks:** Production deploy

---

## 5) ISSUE-TO-TASK COVERAGE MATRIX

| Issue ID | Priority | Phase | Tasks | Gate |
|----------|----------|-------|-------|------|
| DL-001 | P0 | Phase 0 | P0-T1, P0-T2 | Gate B |
| DL-002 | P0 | Phase 0 | P0-T3 | Gate C |
| DL-003 | P0 | Phase 0 | P0-T5 | Gate A |
| DL-004 | P0 | Phase 0 | P0-T4 | Gate A, Gate B |
| DL-005 | P1 | Phase 1 | P1-T1 | Gate A |
| DL-006 | P1 | Phase 1 | P1-T2 | Gate A |
| DL-007 | P1 | Phase 1 | P1-T3 | Gate A |
| DL-008 | P1 | Phase 1 | P1-T4 | Gate B |
| DL-009 | P1 | Phase 1 | P1-T5 | Gate A |
| DL-010 | P1 | Phase 1 | P1-T6 | Gate B |
| DL-011 | P2 | Phase 2 | P2-T1 | Gate B |
| DL-012 | P2 | Phase 2 | P2-T2 | Gate A |
| DL-013 | P2 | Phase 2 | P2-T3 | Gate A |
| DL-014 | P2 | Phase 2 | P2-T4 | Gate B |
| DL-015 | P2 | Phase 2 | P2-T5 | Gate C |
| DL-016 | P3 | Phase 3 | P3-T1 | Gate B |
| DL-017 | P3 | Phase 3 | P3-T2 | Gate C |

**Coverage:** 17/17 issues mapped (100%)

---

## 6) BUILDER MISSIONS

### Mission 1 — Deal Routing Fix (DL-001)

**Scope:** Fix `/deals/[id]` route to handle reserved slugs

**Steps:**
1. Add `RESERVED_DEAL_SLUGS = ['new', 'GLOBAL', 'global']` constant
2. In `page.tsx`, check if `params.id` is reserved before calling `getDeal()`
3. For "new", redirect to `/deals/new/page.tsx` (create this file)
4. For "GLOBAL", render global scope view component
5. Add E2E tests for both routes

**Acceptance Criteria:**
- `/deals/new` renders create deal form
- `/deals/GLOBAL` renders global scope view
- `/deals/DEAL-123` renders deal detail (existing behavior)

**Blocker Policy:** If redirect breaks deep links, add query param preservation

---

### Mission 2 — Backend Contract Completion (DL-005, DL-006, DL-007)

**Scope:** Add missing backend endpoints

**Steps:**
1. Add `POST /api/quarantine/{id}/delete` endpoint in FastAPI
2. Add `POST /api/actions/clear-completed` endpoint in FastAPI
3. Fix preview endpoint to handle all action types
4. Add OpenAPI annotations to all endpoints
5. Generate `openapi.json` and validate against frontend

**Acceptance Criteria:**
- All endpoints return 2xx on valid requests
- OpenAPI spec documents all parameters and responses
- Frontend `api.ts` matches spec

**Blocker Policy:** If endpoint naming conflicts with existing, add version prefix

---

### Mission 3 — Settings Completeness (DL-004, DL-010, DL-012, DL-013)

**Scope:** Build complete Settings page with all sections

**Steps:**
1. Design Settings page layout with tabs: AI Provider, Email, Agent, Buy Box, Notifications
2. Implement Email section with Gmail OAuth flow
3. Implement Agent section with model selection, temperature, tool permissions
4. Implement Buy Box section with criteria rules
5. Implement Notifications section with toggles
6. Wire all sections to backend endpoints

**Acceptance Criteria:**
- Settings page has 5 tabs
- Email OAuth flow completes and saves credentials
- All settings persist across sessions

**Blocker Policy:** If OAuth integration blocked, add manual credential entry as fallback

---

### Mission 4 — Chat Markdown Rendering (DL-008)

**Scope:** Add markdown rendering to chat messages

**Steps:**
1. Install `react-markdown` and `rehype-highlight` (if code blocks needed)
2. Create `ChatMessageContent` component that renders markdown
3. Replace plain text rendering in chat page
4. Handle edge cases: links open in new tab, code blocks styled
5. Add tests for common markdown patterns

**Acceptance Criteria:**
- `**bold**` renders as **bold**
- `_italic_` renders as _italic_
- Code blocks have syntax highlighting
- Links are clickable and open in new tab

**Blocker Policy:** If performance issues with large messages, add virtualization

---

### Mission 5 — Onboarding Backend Integration (DL-003, DL-011, DL-014)

**Scope:** Make onboarding functional with backend persistence

**Steps:**
1. Design onboarding state schema (user prefs, email config, agent settings)
2. Create backend endpoint `POST /api/onboarding/complete`
3. Wire `handleComplete` to call backend instead of localStorage
4. Make capability cards navigate to real settings sections
5. Fix "Configure Email Settings" button to navigate to `/settings#email`

**Acceptance Criteria:**
- Onboarding state saves to database
- Page refresh preserves onboarding progress
- Capability cards lead to functional configuration

**Blocker Policy:** If email OAuth not ready, skip email step with warning

---

## 7) SHIP CRITERIA

**Dashboard R4 is ready to ship when:**

| Criterion | Target | Verification |
|-----------|--------|--------------|
| P0 Issues Closed | 4/4 | Issue tracker |
| P1 Issues Closed | 6/6 | Issue tracker |
| E2E Tests Passing | 100% | CI green |
| No 405/404 Errors | 0 | E2E test suite |
| No Dead Buttons | 0 | Manual audit + E2E |
| Mock Code Removed | 0 | Code review |
| Observability Active | Yes | Trace sample |
| Settings Complete | 5 sections | Screenshot |

---

## 8) RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|------------|
| OAuth integration blocked by Google review | P0-T4 delayed | Use service account for dev; manual config fallback |
| Backend team unavailable for endpoint work | P1 delayed | Frontend team adds Next.js API routes as bridge |
| E2E tests flaky | Gate C false negatives | Add retry logic; quarantine flaky tests |
| Data integrity fix requires DB migration | P0-T3 delayed | Add compatibility layer; migrate during low-traffic window |

---

## 9) TIMELINE ESTIMATE

**Note:** No time estimates per policy. Tasks ordered by dependency and priority.

**Dependency Graph:**
```
Phase 0: P0-T1 → P0-T2 (sequential)
         P0-T3 (independent)
         P0-T4 → P0-T5 (email config needed for onboarding)

Phase 1: P1-T1, P1-T2, P1-T3, P1-T5 (backend, parallel)
         P1-T4, P1-T6 (frontend, parallel)

Phase 2: Depends on Phase 1 completion

Phase 3: Depends on Phase 2 completion
```

---

## 10) APPENDIX: API CONTRACT SPECIFICATION

### Missing Endpoints to Implement

```yaml
# POST /api/quarantine/{quarantine_id}/delete
parameters:
  - name: quarantine_id
    in: path
    required: true
    schema:
      type: string
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:
          deleted_by:
            type: string
          reason:
            type: string
responses:
  200:
    description: Item deleted
    content:
      application/json:
        schema:
          type: object
          properties:
            hidden:
              type: boolean
            quarantine_id:
              type: string

# POST /api/actions/clear-completed
requestBody:
  content:
    application/json:
      schema:
        type: object
        required:
          - operation
          - age
        properties:
          operation:
            type: string
            enum: [archive, delete]
          age:
            type: string
            enum: [all, 7d, 30d]
responses:
  200:
    description: Actions cleared
    content:
      application/json:
        schema:
          type: object
          properties:
            success:
              type: boolean
            affected_count:
              type: integer
            operation:
              type: string
            age:
              type: string
```

---

*Remediation Plan Generated: 2026-02-05T17:10:00Z*
*Architect: Claude-Opus*
