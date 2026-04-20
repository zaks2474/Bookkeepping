# MISSION: DASHBOARD-R4-CONTINUE-001
## Dashboard Round 4 — Remaining Remediation (Batches 4–9)
## Date: 2026-02-09
## Classification: Feature Build + Quality Hardening — Full-Stack Dashboard
## Prerequisite: Batches 0–3 complete (verified 2026-02-09)
## Successor: QA verification mission (generated after completion)

---

## Mission Objective

Continue the Dashboard Round 4 remediation from where Batches 0–3 left off. The remaining work spans 6 phases: Settings Redesign, Onboarding Redesign, Quality Hardening, UX Polish, Page Audits, and E2E/CI Gates. Each phase has its own acceptance criteria and gate.

**What Batches 0–3 delivered (DO NOT REDO):**
- REC-001 through REC-006: Deal routing, create endpoint, quarantine delete, bulk delete, auth headers, deal count alignment
- REC-009 through REC-013: Quarantine approve/preview, actions clear/capabilities/execute, chat markdown
- REC-015, REC-018: Settings test connection, Ask Agent sidebar shared state
- DL-042: Actions count display bug
- 15 Playwright E2E tests across 4 spec files
- Completion reports: `/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-{0,1,2,3}/`

**What remains: 28 items across 6 phases.**

---

## Context: Environment Changes Since Original Mission

The environment has evolved significantly since the original R4 mission was written (2026-02-05). The builder must be aware of:

1. **Surface 9 (Component Design System)** — All dashboard component work must comply with `.claude/rules/design-system.md`. This rule auto-loads when touching `apps/dashboard/src/components/**`, `apps/dashboard/src/app/**`, or `apps/dashboard/src/styles/**`. Key constraints: `Promise.allSettled` mandatory, `console.warn` for degradation, bridge file imports only, `PIPELINE_STAGES` from `execution-contracts.ts`

2. **Deal Integrity Patterns** — 7 mandatory architectural conventions are now codified. See Part 6 of V6PP-SETUP-GUIDE.md. The builder must not violate these patterns

3. **Contract Surface Compliance** — 9 surfaces now exist. Any new API routes must go through the middleware proxy pattern (JSON 502 on failure, never HTML 500). Any new types must flow through the Hybrid Guardrail pattern (spec → codegen → generated file → bridge file → consumer)

4. **Validation Pipeline** — Run `make validate-local` after every phase. Run `make sync-all-types` if any API boundary changes

---

## PHASE 0: Discovery — Verify Current Dashboard State

Before writing any code, verify the current state post-Batches 0–3.

### Discovery Targets

1. **Confirm all batch 0–3 fixes are live:**
   - `curl -s -o /dev/null -w "%{http_code}" http://localhost:3003/deals/new` → expect 200
   - `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:3003/api/deals -H "Content-Type: application/json" -d '{"canonical_name":"test"}'` → expect 201 or 200
   - `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:3003/api/actions/clear-completed -H "Content-Type: application/json" -d '{"operation":"delete","age":"all"}'` → expect 200
   - Verify 15 Playwright tests pass: `cd /home/zaks/zakops-agent-api && npx playwright test`

2. **Confirm services are running:**
   - Dashboard on 3003, Backend on 8091, Agent API on 8095, PostgreSQL on 5432
   - Port 8090 is NOT listening (decommissioned)

3. **Confirm contract surface health:**
   - `make validate-local` passes
   - `make sync-all-types` runs without drift

4. **Scan current Settings page** — Note existing sections, current state, what's already wired
5. **Scan current Onboarding flow** — Note existing steps, localStorage usage, backend endpoint existence
6. **Scan for Surface 9 compliance** — Quick check of existing dashboard code against Category A conventions

### Discovery Output
Produce a brief summary before proceeding. Flag any surprises.

---

## PHASE 1: Settings Redesign (Batch 4)

### Remaining Items
| ID | Title | Priority | Status |
|----|-------|----------|--------|
| DL-008 / REC-008 | Email Configuration section missing | P1 | TODO |
| DL-035 / REC-036 | Timezone settings missing | P3 | TODO |
| DL-036 / REC-037 | Dark mode toggle location unclear | P3 | TODO |

### Target Architecture

The Settings page currently has only "AI Provider Configuration" (with Test Connection fixed in Batch 3). Add 5 new sections using anchor-based navigation:

```
/settings
├── #provider       (AI Provider Configuration) — EXISTS
├── #email          (Email Integration) — NEW
├── #agent          (Agent Configuration) — NEW
├── #notifications  (Notification Preferences) — NEW
├── #data           (Data & Privacy) — NEW
└── #appearance     (Appearance & Theme) — NEW
```

### Section Specs

**Email Integration (#email):**
- Connection type selector: OAuth (Gmail/Outlook) or IMAP (Custom)
- OAuth flow: Connect/Disconnect buttons, token handling
- IMAP/SMTP fields: host, port, username, password (encrypted)
- Sync frequency selector (5min / 15min / 30min / 1hr)
- Connected accounts table with health status
- Backend endpoints: `POST /api/integrations/email/connect`, `POST /api/integrations/email/test`, `DELETE /api/integrations/email`

**Agent Configuration (#agent):**
- Auto-execute threshold slider (0–100%, default 70%)
- Max concurrent actions (number, default 5)
- Deal matching strictness (Strict/Medium/Loose)
- Enrichment sources multi-select
- Response style selector (Brief/Detailed/Verbose)
- Backend endpoints: `GET /api/user/preferences`, `PATCH /api/user/preferences`

**Notification Preferences (#notifications):**
- Email/Browser notification toggles
- Digest frequency selector
- Per-event toggles (new deals, pending approvals, completed actions)

**Data & Privacy (#data):**
- Completed action retention selector (7d/30d/90d/Forever)
- Export all data button
- Delete account button (with confirmation dialog)

**Appearance & Theme (#appearance):**
- Theme selector (System/Light/Dark) — consolidates DL-036
- Sidebar collapsed toggle
- Dense mode toggle
- Timezone selector — resolves DL-035

### Implementation Priority
1. Email Integration (P1 — core functionality)
2. Agent Configuration (P1 — core functionality)
3. Appearance & Theme (includes timezone + dark mode fixes)
4. Notification Preferences (P2)
5. Data & Privacy (P3)

### Gate P1: Settings Redesign
- All 6 settings sections render without errors
- Email section: connect/disconnect flow works (or graceful stub if backend not ready)
- Agent config: preferences save and reload on page refresh
- Appearance: theme toggle works, timezone selection persists
- `make validate-local` passes after changes
- No Surface 9 violations (Promise.allSettled for multi-fetch, bridge file imports)

---

## PHASE 2: Onboarding Redesign (Batch 5)

### Remaining Items
| ID | Title | Priority | Status |
|----|-------|----------|--------|
| DL-007 / REC-007 | Onboarding state in localStorage only — no backend persistence | P0 | TODO |

### Target Architecture

Replace localStorage-only onboarding with backend-persisted 4-step wizard:

```
Step 1: Welcome → Step 2: Profile → Step 3: Email Setup → Step 4: Agent Demo → Dashboard
```

### Backend Endpoints Required

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/onboarding/status` | GET | Check completion state + current step |
| `/api/onboarding/profile` | POST | Save profile (name, role, org, timezone) |
| `/api/onboarding/email-skipped` | POST | Mark email step skipped |
| `/api/onboarding/demo/start` | POST | Initialize demo context |
| `/api/onboarding/complete` | POST | Mark onboarding done |
| `/api/onboarding/reset` | POST | Re-enter onboarding flow |

### State Persistence Strategy
- **Primary:** Backend persistence via `/api/onboarding/*` endpoints
- **Fallback:** Session storage for draft state only (not localStorage)
- **On load:** Check `GET /api/onboarding/status` first, resume from last completed step

### Resume Policy
| Scenario | Behavior |
|----------|----------|
| Browser closed mid-flow | Resume from last completed step |
| Onboarding complete | Redirect to Dashboard, onboarding hidden |
| User wants to redo | Settings → "Redo Onboarding" → `POST /api/onboarding/reset` |

### Skip Policy
- Steps 1, 2, 4: Cannot skip
- Step 3 (Email): Can skip with warning ("Set up later in Settings")

### Gate P2: Onboarding Redesign
- `GET /api/onboarding/status` returns valid state object
- Profile step saves to backend, persists after page refresh
- Email step: connect or skip both work
- After completion, navigating to `/onboarding` redirects to `/dashboard`
- Refreshing mid-flow resumes at correct step (not step 1)
- No localStorage for onboarding state (session storage for drafts only)
- E2E test: complete flow, refresh, verify persistence

---

## PHASE 3: Quality Hardening (Batch 6)

### Remaining Items
| ID | Title | Priority |
|----|-------|----------|
| DL-020 / REC-020 | Zod schemas use `.passthrough()` and `z.unknown()` | P2 |
| DL-024 / REC-024 | Loading states inconsistent (skeleton vs spinner) | P2 |
| DL-025 / REC-025 | Error boundaries not tested / may white-screen | P2 |
| DL-026 / REC-026 | Mock fallbacks mask real errors in production | P2 |
| DL-027 / REC-027 | operatorName from localStorage not validated server-side | P2 |
| DL-028 / REC-028 | Idempotency-Key sent but backend doesn't enforce | P2 |
| DL-029 / REC-029 | No correlation_id in requests | P2 |
| DL-030 / REC-030 | Error responses inconsistent ({error} vs {detail} vs {message}) | P2 |
| DL-040 | No /api/user/profile or /me endpoint | P2 |

### Implementation Guidance

**REC-020 (Zod strictness):** Remove `.passthrough()` and `z.unknown()` from `lib/schemas.ts`. Use `.strict()` mode. Validate that existing pages still work after tightening — some backend responses may include extra fields that need explicit schema additions.

**REC-024 (Loading states):** Standardize: skeleton loaders for content areas, spinners for action buttons. Create a consistent pattern across all pages.

**REC-025 (Error boundaries):** Add React error boundaries wrapping each major page section. Fallback UI shows a user-friendly error message, not a white screen. Use `console.warn` for expected degradation per Surface 9 convention.

**REC-026 (Mock fallbacks):** Remove mock data fallbacks from production API routes. On 4xx/5xx, surface the actual error to the user. Mocks only in development/test mode.

**REC-029 (Correlation ID):** Add `X-Correlation-ID` header (UUID) to all `apiFetch` calls. Backend must log it. Enables cross-service debugging.

**REC-030 (Error format):** Standardize backend error responses to: `{code: string, message: string, details?: object, correlation_id?: string}`.

**DL-040 (User profile):** Implement `GET /api/user/profile` or `/api/me` endpoint returning authenticated user identity.

### Gate P3: Quality Hardening
- Zero `.passthrough()` or `z.unknown()` in dashboard Zod schemas
- Every page section wrapped in error boundary (verify by counting boundary components)
- No mock fallbacks in production API routes (grep for mock/fallback patterns)
- `X-Correlation-ID` header present in apiFetch calls
- Error responses from dashboard API routes follow standardized format
- Backend returns 409 on duplicate Idempotency-Key (if REC-028 implemented)
- `make validate-local` passes

---

## PHASE 4: UX Polish (Batch 7)

### Remaining Items
| ID | Title | Priority |
|----|-------|----------|
| DL-021 / REC-021 | Pagination untested / may not work | P2 |
| DL-022 / REC-022 | Filters reset on back navigation | P2 |
| DL-023 / REC-023 | Tab order, Enter/Escape handlers missing | P2 |
| DL-031 / REC-031 | SSE reconnect / partial-token handling unverified | P2 |
| DL-034 / REC-035 | Rapid button clicks cause unhandled rate limit errors | P3 |
| DL-041 | /api/alerts and /api/deferred-actions/due status enum drift | P2 |

### Implementation Guidance

**REC-021 (Pagination):** Test all list pages (deals, actions, quarantine) with >20 items. Ensure pagination controls render and navigate correctly.

**REC-022 (Filter persistence):** Persist active filters in URL search params. On back navigation, restore filters from URL. Use `useSearchParams` in Next.js App Router.

**REC-023 (Keyboard nav):** Audit Tab order on all interactive pages. Add Enter to submit, Escape to cancel/close on modals and forms.

**REC-031 (SSE reconnect):** Implement automatic SSE reconnection with last event ID. Show connection health indicator in chat UI.

**REC-035 (Debounce):** Add debounce to action buttons (300ms). Show loading state during API call. Disable button until response returns.

### Gate P4: UX Polish
- Pagination works on deals list with >20 items
- Filters persist in URL and survive back navigation
- Tab navigation works through main interactive elements
- Escape closes open modals/dialogs
- SSE reconnects after disconnection (simulate by stopping/starting backend)
- Button debounce prevents double-submit on rapid clicks
- No status enum mismatches on /api/alerts

---

## PHASE 5: Page Audits (Batch 8)

### Remaining Items
| ID | Title | Priority |
|----|-------|----------|
| DL-014 / REC-014 | POST /api/deals/bulk-archive not implemented | P1 |
| DL-016 / REC-016 | /hq page not audited — charts/stats may not load | P1 |
| DL-017 / REC-017 | /agent/activity not audited — timeline may have issues | P1 |
| DL-039 | File upload in quarantine materials tab untested | P2 |
| DL-032 / REC-033 | No export/print for deal data | P3 |
| DL-033 / REC-034 | No concurrent edit handling | P3 |
| DL-037 / REC-038 | No activity feed per deal | P3 |
| DL-038 / REC-039 | Mobile/responsive not verified | P2 |

### Implementation Guidance

**REC-014 (Bulk archive):** Implement `POST /api/deals/bulk-archive` in backend. Wire to dashboard bulk action controls.

**REC-016 (/hq audit):** Navigate to `/hq`, verify Quick Stats cards load with real data, charts render, no console errors. Fix any rendering issues.

**REC-017 (/agent/activity audit):** Navigate to `/agent/activity`, verify timeline renders, logs parse correctly, no dead links or broken components.

**P3 items (REC-033, REC-034, REC-038):** These are optional enhancements. Implement if time permits. Do not block completion on these.

### Gate P5: Page Audits
- `POST /api/deals/bulk-archive` returns 200
- `/hq` page loads with charts rendering and no console errors
- `/agent/activity` page loads with timeline rendering correctly
- No 404/405 errors on any audited page
- `make validate-local` passes

---

## PHASE 6: E2E Tests + CI Gates (Batch 9)

### Remaining Items
| ID | Title | Priority |
|----|-------|----------|
| REC-040 | CI gate: frontend API calls vs backend OpenAPI spec | P2 |
| REC-041 | CI gate: static scan + Playwright click-all for dead UI | P2 |
| REC-042 | CI gate: correlation_id in logs | P3 |
| REC-032 | CI gate: UI fetch methods vs route exports | P3 |

### E2E Suite Expansion
Expand the existing 15 Playwright tests to cover new functionality from Phases 1–5:
- Settings page: section navigation, email connect flow, preferences save
- Onboarding: full wizard completion with backend persistence
- Quality: error boundary rendering (trigger intentional error)
- UX: pagination, filter persistence, keyboard navigation
- Page audits: /hq and /agent/activity load tests

### Click-All-Buttons Dead UI Test
Implement `tests/e2e/no-dead-ui.spec.ts`:
- Visit every route: `/dashboard`, `/deals`, `/actions`, `/quarantine`, `/settings`, `/hq`, `/agent/activity`
- Click all enabled buttons (up to 10 per page)
- Fail on 404/405 network errors or error toasts

### CI Gate Implementations

**REC-040 (Contract gate):** Script that extracts frontend `apiFetch` call URLs and methods, compares against backend OpenAPI spec. Fails on mismatches.

**REC-041 (Dead UI gate):** Combine static analysis (grep for dead onClick handlers) + Playwright click-all test. Block merge on failures.

### Gate P6: E2E & CI Gates
- Full Playwright suite passes (existing 15 + new tests)
- Click-all-buttons test passes on all routes
- Contract gate script runs without false positives
- `make validate-local` passes
- Total E2E test count documented in completion report

---

## Guardrails

1. **Surface 9 compliance is mandatory.** All dashboard component work must follow `.claude/rules/design-system.md` conventions. Use `Promise.allSettled` for multi-fetch, `console.warn` for degradation, bridge file imports only. Run `bash tools/infra/validate-surface9.sh` before completing any phase
2. **Deal Integrity patterns are non-negotiable.** `transition_deal_state()` for state changes, `PIPELINE_STAGES` from `execution-contracts.ts`, server-side counts only, middleware proxy for `/api/*`
3. **No modification of completed batch fixes.** Batches 0–3 are stable. If a Phase 1–6 change conflicts with a batch 0–3 fix, resolve the conflict without reverting the earlier fix
4. **Contract surface discipline.** Any new API routes must follow the middleware proxy pattern. Any new TypeScript types that mirror backend models must go through the Hybrid Guardrail flow (spec → codegen → bridge)
5. **Run `make validate-local` after every phase.** Do not proceed to the next phase if validation fails
6. **Run `make sync-all-types` if any API boundary changes.** New backend endpoints, changed response schemas, or new OpenAPI paths all require a sync
7. **WSL safety.** Fix CRLF on any new .sh files. Fix ownership on files under `/home/zaks/`
8. **Evidence discipline.** Each phase produces evidence in `/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-{N}/`

---

## Acceptance Criteria

### AC-1: Settings Redesign
All 6 settings sections render, navigate via anchors, and persist user preferences. Email integration section has functional connect/test/disconnect flow (or graceful stub). Timezone and theme settings work.

### AC-2: Onboarding Redesign
Onboarding flow persists state in backend, not localStorage. Refresh resumes at correct step. Completion redirects to dashboard. Backend endpoints all respond correctly.

### AC-3: Quality Hardening
Zero `.passthrough()` in production Zod schemas. Error boundaries on all pages. No mock fallbacks in production. Correlation ID flows through requests. Standardized error format.

### AC-4: UX Polish
Pagination, filters, and keyboard navigation work. SSE reconnects. Buttons are debounced. No enum drift on alert endpoints.

### AC-5: Page Audits
`/hq` and `/agent/activity` load correctly. Bulk archive endpoint works. No dead UI on any audited page.

### AC-6: E2E & CI Gates
Full Playwright suite passes. Click-all-buttons test covers all routes. At least 1 CI gate script implemented and passing.

### AC-7: Validation Clean
`make validate-local` passes. `bash tools/infra/validate-surface9.sh` passes. No TypeScript compilation errors. No lint errors.

### AC-8: Evidence Complete
Each completed phase has a completion report and evidence directory under `/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/`.

---

## Remaining Items Registry (Compact)

### P0–P1 (Must Do)
| ID | Title | Phase |
|----|-------|-------|
| DL-007 / REC-007 | Onboarding backend persistence | Phase 2 |
| DL-008 / REC-008 | Settings email section | Phase 1 |
| DL-014 / REC-014 | Deals bulk archive endpoint | Phase 5 |
| DL-016 / REC-016 | /hq page audit | Phase 5 |
| DL-017 / REC-017 | /agent/activity page audit | Phase 5 |

### P2 (Should Do)
| ID | Title | Phase |
|----|-------|-------|
| DL-020 / REC-020 | Zod strict schemas | Phase 3 |
| DL-021 / REC-021 | Pagination verification | Phase 4 |
| DL-022 / REC-022 | Filter persistence in URL | Phase 4 |
| DL-023 / REC-023 | Keyboard navigation | Phase 4 |
| DL-024 / REC-024 | Loading state consistency | Phase 3 |
| DL-025 / REC-025 | Error boundaries | Phase 3 |
| DL-026 / REC-026 | Remove mock fallbacks | Phase 3 |
| DL-027 / REC-027 | Operator identity validation | Phase 3 |
| DL-028 / REC-028 | Idempotency enforcement | Phase 3 |
| DL-029 / REC-029 | Correlation ID | Phase 3 |
| DL-030 / REC-030 | Error format standardization | Phase 3 |
| DL-031 / REC-031 | SSE reconnect | Phase 4 |
| DL-038 / REC-039 | Mobile responsive | Phase 5 |
| DL-039 | Quarantine file upload | Phase 5 |
| DL-040 | User profile endpoint | Phase 3 |
| DL-041 | Alerts enum drift | Phase 4 |
| REC-040 | Contract CI gate | Phase 6 |
| REC-041 | Dead UI CI gate | Phase 6 |

### P3 (Nice to Have — Do Not Block Completion)
| ID | Title | Phase |
|----|-------|-------|
| DL-032 / REC-033 | Deal export CSV/PDF | Phase 5 |
| DL-033 / REC-034 | Concurrent edit handling | Phase 5 |
| DL-034 / REC-035 | Button debounce | Phase 4 |
| DL-035 / REC-036 | Timezone settings | Phase 1 |
| DL-036 / REC-037 | Dark mode toggle | Phase 1 |
| DL-037 / REC-038 | Activity feed per deal | Phase 5 |
| REC-032 | Route/method CI gate | Phase 6 |
| REC-042 | Observability CI gate | Phase 6 |

---

## Upgrade Ideas (Optional — Reference Only)

These 25 upgrades from the original TriPass investigation are architectural improvements, not bug fixes. Implement opportunistically if they align with phase work. Do not treat as blockers.

| ID | Upgrade | Priority | Relevant Phase |
|----|---------|----------|---------------|
| UP-01 | Contract-first client generation (orval/openapi-typescript) | High | Phase 6 |
| UP-02 | Click-every-button Playwright test | High | Phase 6 |
| UP-03 | Request correlation ID middleware | High | Phase 3 |
| UP-08 | Hybrid Search (RAG + SQL) | High | — (agent-side) |
| UP-14 | Typed error protocol | High | Phase 3 |
| UP-23 | Method/Route diff CI tool | High | Phase 6 |
| UP-04 | Unified Operations API (POST /api/ops) | Medium | — |
| UP-05 | Optimistic UI updates (onMutate) | Medium | Phase 4 |
| UP-20 | SSE resilient handling | Medium | Phase 4 |
| UP-25 | Unified chat SSE provider | Medium | Phase 4 |

*Full list of 25 upgrades available in the original mission at `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md` (Appendix F).*

---

## Execution Order

1. **Phase 0** — Discovery. Verify batches 0–3 are live. Confirm services. Scan current state
2. **Phase 1** — Settings Redesign. Priority: Email → Agent Config → Appearance → Notifications → Data
3. **Phase 2** — Onboarding Redesign. Wire to backend. Remove localStorage dependency
4. **Phase 3** — Quality Hardening. Zod → Error boundaries → Mocks → Correlation ID → Error format
5. **Phase 4** — UX Polish. Pagination → Filters → Keyboard → SSE → Debounce
6. **Phase 5** — Page Audits. /hq → /agent/activity → Bulk archive → File upload
7. **Phase 6** — E2E & CI Gates. Expand suite → Click-all-buttons → CI gate scripts
8. Run `make validate-local` and `bash tools/infra/validate-surface9.sh`
9. Update bookkeeping: CHANGES.md, evidence directories, completion reports

---

## Stop Condition

Stop when:
- All P0–P1 items are resolved (5 items)
- All P2 items are resolved or explicitly deferred with justification (18 items)
- All acceptance criteria AC-1 through AC-8 are met
- `make validate-local` passes
- Evidence pack is complete for each executed phase

P3 items are optional. Do not block completion on P3 items. Document any P3 items left unimplemented in the completion report.

---

## File Paths Reference

### Files to create
- New settings sections in `apps/dashboard/src/app/settings/`
- Onboarding backend endpoints in `zakops-backend/`
- New API routes in `apps/dashboard/src/app/api/`
- E2E test files in `apps/dashboard/tests/e2e/`
- Evidence directories: `/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-{4..9}/`

### Files to modify
- `apps/dashboard/src/app/settings/page.tsx` — Add 5 new sections
- `apps/dashboard/src/app/onboarding/page.tsx` — Backend persistence
- `apps/dashboard/src/lib/api.ts` (apiFetch) — Correlation ID header
- `apps/dashboard/src/lib/schemas.ts` — Zod strictness
- Backend API routes and models as needed for new endpoints
- `Makefile` — Add CI gate targets if applicable

### Files to read (sources of truth — do NOT modify)
- `.claude/rules/design-system.md` — Surface 9 conventions
- `.claude/rules/contract-surfaces.md` — All 9 surfaces
- `apps/dashboard/src/types/execution-contracts.ts` — PIPELINE_STAGES
- `packages/contracts/openapi/*.json` — API specs
- Original mission: `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-ROUND4-EXEC-001.md`
- Batch completion reports: `/home/zaks/bookkeeping/qa-verifications/DASHBOARD-R4/batch-{0..3}/`

---

*End of Mission Prompt — DASHBOARD-R4-CONTINUE-001*
