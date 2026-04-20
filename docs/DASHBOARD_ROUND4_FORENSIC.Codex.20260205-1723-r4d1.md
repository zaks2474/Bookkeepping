AGENT IDENTITY
- agent_name: Codex
- run_id: 20260205-1723-r4d1
- date_time: 2026-02-05T17:23:20Z
- repo_revision_dashboard: b96b33c5547258663123a637dcff741c96b028c9
- repo_revision_backend: 2a68de172c7faf1df6f53357f4b43b0161d5dd32
- repo_revision_agent_api: b96b33c5547258663123a637dcff741c96b028c9

## Executive Summary
The dashboard is visually rich but operationally brittle. Core workflows (deal detail routing, quarantine approval, action execution, bulk delete) either 405/404 or run on mock fallbacks. Multiple UI surfaces are demo-only (onboarding email connect, agent demo, Ask Agent drawer), while real backend endpoints for email integration and quarantine processing exist but are unused. Authentication for write actions is likely broken because client-side requests do not include X-API-Key even though the backend requires it. Chat renders raw markdown and can return deal counts from RAG that diverge from the UI’s database-driven counts, eroding trust. The immediate path is contract stabilization: correct routes and methods, wire quarantine to the real process endpoint, add API-key injection for writes, and eliminate mock fallbacks in production.

## Evidence Review (Screenshots -> routes/contracts)
Note: The screenshot directory `/home/zaks/bookkeeping/docs/round4_dashboard_screenshots/` is not present locally. Evidence references below use the file paths provided in the prompt; they should be treated as external evidence and reattached if available.

1) Screenshot 1: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101133.png`
- Route: `localhost:3003/deals/GLOBAL`
- Observed: “Failed to load deal”, endpoint `/api/deals/GLOBAL`
- Likely cause: catch-all `/deals/[id]` treats GLOBAL as deal_id and calls GET `/api/deals/{id}` without guarding.
- Evidence: `apps/dashboard/src/app/deals/[id]/page.tsx:89-126, 315-325`

2) Screenshot 2: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101209.png`
- Route: `localhost:3003/deals`
- Observed: toast `Method Not Allowed` after delete/bulk delete
- Likely cause: UI calls POST `/api/deals/bulk-archive` (not implemented), FastAPI treats `bulk-archive` as `{deal_id}` and returns 405.
- Evidence: `apps/dashboard/src/lib/api.ts:467-478`, backend deals endpoints in `zakops-backend/src/api/orchestration/main.py:465-949` (no bulk route)

3) Screenshot 3: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101227.png`
- Route: `localhost:3003/settings`
- Observed: Only AI provider settings; no email settings
- Evidence: `apps/dashboard/src/app/settings/page.tsx` (provider config only), `apps/dashboard/src/lib/settings/provider-settings.ts` (localStorage only)

4) Screenshot 4: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101303.png`
- Route: `localhost:3003/onboarding`
- Observed: “Configure Email Settings” button leads to Settings with no email section
- Evidence: `apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:52-62` (mock OAuth), `apps/dashboard/src/app/onboarding/page.tsx:9-18` (localStorage only)

5) Screenshot 5: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101347.png`
- Route: `localhost:3003/onboarding`
- Observed: “Meet Your Agent” cards are demo-only
- Evidence: `apps/dashboard/src/components/onboarding/steps/AgentDemoStep.tsx:1-6, 150-178` (mock demo)

6) Screenshot 6: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101440.png`
- Route: `localhost:3003/chat`
- Observed: raw `**bold**` markdown not rendered; deal count mismatch (agent says 3, UI shows 9)
- Evidence: chat rendering `apps/dashboard/src/app/chat/page.tsx:1035-1047` (plain text); agent tool search uses RAG `apps/agent-api/app/core/langgraph/tools/deal_tools.py:469-507`.

7) Screenshot 7: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101506.png`
- Route: `localhost:3003/quarantine`
- Observed: “Preview not found” in right panel
- Likely cause: preview endpoint calls `/api/actions/{actionId}` but queue items come from `/api/quarantine` ids.
- Evidence: preview route `apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts:16-48`, queue route `apps/dashboard/src/app/api/actions/quarantine/route.ts:26-54`

8) Screenshot 8: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101526.png`
- Route: `localhost:3003/quarantine`
- Observed: toast `Not Found` after delete
- Likely cause: UI posts `/api/quarantine/{id}/delete` which is not implemented in backend.
- Evidence: `apps/dashboard/src/lib/api.ts:839-866`, backend quarantine endpoints `zakops-backend/src/api/orchestration/main.py:1160-1483`

9) Screenshot 9: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101612.png`
- Route: `localhost:3003/actions`
- Observed: “Delete Completed Actions” -> Method Not Allowed
- Likely cause: UI posts `/api/actions/clear-completed`; backend lacks this endpoint; Next proxy only falls back on 404 not 405.
- Evidence: `apps/dashboard/src/app/actions/page.tsx:485-499`, `apps/dashboard/src/lib/api.ts:1840-1869`, `apps/dashboard/src/app/api/actions/clear-completed/route.ts:48-85`, backend actions routes `zakops-backend/src/api/orchestration/main.py:1036-1160`

10) Screenshot 10: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101733.png`
- Route: `localhost:3003/dashboard`
- Observed: counts in pipeline vs chat mismatch risk
- Evidence: dashboard uses `getDeals` and `getQuarantineItems` from `/api/*` endpoints; chat uses agent tool search.

11) Screenshot 11: `C:\Users\mzsai\Downloads\Dashbord Srenshots\Screenshot 2026-02-05 101802.png`
- Route: `localhost:3003/deals/new`
- Observed: “Failed to load deal”; endpoint `/api/deals/new`
- Likely cause: catch-all `/deals/[id]` treats “new” as deal_id.
- Evidence: `apps/dashboard/src/app/deals/[id]/page.tsx:89-126, 315-325` and no `/deals/new` route in `apps/dashboard/src/app/deals/`.

## Dashboard Surface Inventory (pages, components, actions)
Routes discovered under `apps/dashboard/src/app`:
- `/dashboard`: uses `getDeals`, `getDueActions`, `getQuarantineHealth`, `getQuarantineItems`, `getAlerts`. Actions: refresh, approvals toggle, item links to /deals, /quarantine, /actions. Evidence: `apps/dashboard/src/app/dashboard/page.tsx`.
- `/deals`: list + board. Actions: filter/search, refresh, row click (navigate), single delete (archive), bulk delete (archive). Evidence: `apps/dashboard/src/app/deals/page.tsx`.
- `/deals/[id]`: deal workspace. Actions: add note, transition stage, chat link, run/approve/cancel/retry actions, update action inputs, view case-file/materials/enrichment. Evidence: `apps/dashboard/src/app/deals/[id]/page.tsx`.
- `/actions`: command center. Actions: create action, approve/run/cancel/retry/update inputs, bulk archive/delete, clear completed, refresh, filter. Evidence: `apps/dashboard/src/app/actions/page.tsx`.
- `/quarantine`: queue review. Actions: approve, reject, delete, bulk delete, preview, refresh. Evidence: `apps/dashboard/src/app/quarantine/page.tsx`.
- `/chat`: agent chat with SSE, execute proposals. Evidence: `apps/dashboard/src/app/chat/page.tsx`, `/api/chat`.
- `/settings`: AI provider config only. Evidence: `apps/dashboard/src/app/settings/page.tsx`.
- `/onboarding`: wizard with profile/email/agent demo/preferences. Evidence: `apps/dashboard/src/app/onboarding/page.tsx` + `components/onboarding/*`.
- `/hq`: Operator HQ overview. Evidence: `apps/dashboard/src/app/hq/page.tsx`.
- `/agent/activity`: agent activity view. Evidence: `apps/dashboard/src/app/agent/activity/page.tsx`.

## Limitations Registry (deduped, P0-P3)
Each entry includes fix, dependencies, systemic prevention, two better ideas, verification.

L-01 (P0) Deal detail routing treats slugs like "new" and "GLOBAL" as deal IDs
- Evidence: `apps/dashboard/src/app/deals/[id]/page.tsx:89-126, 315-325` (no guard, fetches `/api/deals/{id}`); no `/deals/new` route.
- Fix: Add `/app/deals/new/page.tsx` or guard in `[id]` for reserved slugs (new, GLOBAL). Route `/deals/new` to create form; route GLOBAL to a global view or redirect.
- Dependencies: product decision on deal creation UX; backend create endpoint readiness; auth for POST `/api/deals`.
- Systemic prevention: route lint rule for reserved slugs + Playwright route tests for `/deals/new` and `/deals/GLOBAL`.
- Better ideas: (1) Add a quick-create modal with schema-based validation. (2) Add “Global Portfolio” page for cross-deal analytics instead of abusing a deal route.
- Verification: `curl -i http://localhost:3003/deals/new` should render creation UI; `curl -i http://localhost:3003/api/deals/new` should no longer be called.

L-02 (P0) Bulk delete/archive deals hits missing endpoint `/api/deals/bulk-archive` -> 405
- Evidence: `apps/dashboard/src/lib/api.ts:467-478` (POST `/api/deals/bulk-archive`), backend lacks bulk endpoint (`zakops-backend/src/api/orchestration/main.py:465-949` lists only single deal endpoints).
- Fix: Implement backend endpoint `/api/deals/bulk-archive` (POST) or change UI to loop `POST /api/deals/{id}/archive` with idempotency.
- Dependencies: DB transaction strategy, audit log requirements, API key enforcement.
- Systemic prevention: contract tests that compare UI route list vs backend OpenAPI, and method mismatch detection.
- Better ideas: (1) Add “Archive with reason” bulk workflow and activity log. (2) Provide staged bulk operations with preview of affected deals.
- Verification: `curl -i -X POST http://localhost:8091/api/deals/bulk-archive -H "X-API-Key: $ZAKOPS_API_KEY" -d '{"deal_ids":["DL-0001"]}'` returns 200.

L-03 (P0) Client-side write calls lack X-API-Key despite backend requiring it
- Evidence: `apps/dashboard/src/lib/api.ts:361-388` (no API key header); backend enforces key for write methods `zakops-backend/src/api/shared/middleware/apikey.py:4-40`; API key is added only by Next API helpers `apps/dashboard/src/lib/backend-fetch.ts:13-20`.
- Fix: Route all write operations through Next API routes that inject X-API-Key, or implement session-based auth for client writes.
- Dependencies: auth model decision; API key rotation; CORS policy.
- Systemic prevention: lint rule disallowing direct client POST/PUT/PATCH/DELETE to `/api/*` unless route is server-side.
- Better ideas: (1) Replace API key with signed user sessions and RBAC. (2) Add request signing + replay protection for write routes.
- Verification: For each write action (deal transition, add note, create action), confirm 200 with X-API-Key and 401 without it.

L-04 (P0) Quarantine approve/reject wired to Kinetic Actions endpoints that are missing
- Evidence: `apps/dashboard/src/lib/api.ts:781-792` uses `/api/actions/{id}/approve` + `/execute`; `/api/actions/{id}/execute` does not exist in backend (`zakops-backend/src/api/orchestration/main.py:1060-1160` shows only get/approve/reject). Quarantine has a dedicated `/api/quarantine/{id}/process` endpoint (`main.py:1358-1483`) that UI does not use.
- Fix: Use `/api/quarantine/{id}/process` for approve/reject and return deal_id; or implement full Kinetic action execute/cancel/retry endpoints.
- Dependencies: decision on canonical quarantine workflow; audit trails; HITL policy.
- Systemic prevention: contract map test that ensures UI uses the canonical endpoint for each domain action.
- Better ideas: (1) Add an “Approve & Create Deal” confirmation flow with summary preview and data quality score. (2) Add “link to existing deal” option with search.
- Verification: `curl -i -X POST http://localhost:8091/api/quarantine/{id}/process -H "X-API-Key: $ZAKOPS_API_KEY" -d '{"action":"approve","processed_by":"z"}'` returns deal_id and item moves to approved.

L-05 (P0) Quarantine preview uses action ID while queue uses quarantine item IDs
- Evidence: preview route calls `/api/actions/{actionId}` (`apps/dashboard/src/app/api/actions/quarantine/[actionId]/preview/route.ts:16-48`). Queue data comes from `/api/quarantine` via `/api/actions/quarantine` route (`apps/dashboard/src/app/api/actions/quarantine/route.ts:26-54`) which returns `id`/`quarantine_id` without a matching `action_id`.
- Fix: Create `/api/quarantine/{id}/preview` (backend or Next) using quarantine data, or ensure queue items include action_id if actions exist.
- Dependencies: data model for quarantine vs action linkage.
- Systemic prevention: enforce ID type in UI types (quarantine_id vs action_id), add runtime guards.
- Better ideas: (1) Precompute preview summary and cache in DB to avoid slow parsing. (2) Add side-by-side “raw email” vs “extracted fields” view.
- Verification: selecting a quarantine item should load preview without 404; `GET /api/quarantine/{id}` should contain preview fields or link.

L-06 (P0) Actions “Clear Completed” returns 405 (Method Not Allowed)
- Evidence: UI calls `clearCompletedActions` `apps/dashboard/src/app/actions/page.tsx:485-499`; API function uses `/api/actions/clear-completed` `apps/dashboard/src/lib/api.ts:1840-1869`; proxy returns 405 when backend lacks endpoint (`main.py` has no clear-completed; only `/api/actions/{action_id}` GET/POST approve/reject).
- Fix: Implement `/api/actions/clear-completed` in backend or change UI to a supported bulk operation.
- Dependencies: retention policy; permissions; audit logging.
- Systemic prevention: add CI test that ensures any UI route has a backend handler for the method.
- Better ideas: (1) Add “Archive completed after N days” scheduled job with UI toggle. (2) Add multi-stage trash with restore.
- Verification: `curl -i -X POST http://localhost:8091/api/actions/clear-completed -H "X-API-Key: $ZAKOPS_API_KEY" -d '{"operation":"delete","age":"all"}'` returns affected_count.

L-07 (P0) Action execution endpoints referenced by UI are missing
- Evidence: UI uses `/api/actions/{id}/execute`, `/cancel`, `/retry`, `/update` (`apps/dashboard/src/lib/api.ts:1673-1715`), but backend defines only list/get/approve/reject (`zakops-backend/src/api/orchestration/main.py:1060-1160`).
- Fix: Implement execute/cancel/retry/update endpoints or remove/disable UI controls until backend supports them.
- Dependencies: action engine and worker queue; audit log schema.
- Systemic prevention: OpenAPI-driven SDK for UI to prevent calling unimplemented endpoints.
- Better ideas: (1) Add action timeline with real-time status via SSE. (2) Add action simulation mode for safe previews.
- Verification: `curl -i -X POST http://localhost:8091/api/actions/{id}/execute -H "X-API-Key: $ZAKOPS_API_KEY"` returns status change.

L-08 (P1) Settings “Test connection” uses GET /api/chat but route only supports POST
- Evidence: `apps/dashboard/src/lib/settings/provider-settings.ts:139-147` uses `fetch('/api/chat', { method: 'GET' })`; `/api/chat` defines only POST (`apps/dashboard/src/app/api/chat/route.ts:9-18`).
- Fix: Add GET `/api/chat/health` endpoint or change test to call `/health` on agent API.
- Dependencies: agent health endpoint contract.
- Systemic prevention: method-only route tests; fail if a GET/POST mismatch exists.
- Better ideas: (1) Provide “Test provider” that runs a real prompt and shows latency/model. (2) Provide connection diagnostics with auth and model metadata.
- Verification: `curl -i http://localhost:3003/api/chat/health` returns status available.

L-09 (P1) Settings + onboarding email integration are demo-only; backend email endpoints unused
- Evidence: onboarding email uses mock OAuth (`EmailSetupStep.tsx:52-60`), onboarding completion uses localStorage only (`onboarding/page.tsx:9-18`), settings stores provider config in localStorage (`provider-settings.ts:105-118`). Backend email integration exists in `zakops-backend/src/api/orchestration/routers/email.py`.
- Fix: Build email settings UI tied to `/api/integrations/email/*` and persist onboarding state server-side.
- Dependencies: auth/session model; OAuth credentials; secret storage.
- Systemic prevention: require feature flags for any mock-only UI.
- Better ideas: (1) Email connection health dashboard (last sync, errors). (2) Inbox-to-deal matching rules editor with dry-run.
- Verification: connect email via `/api/integrations/email/gmail/auth` and show connected account in Settings.

L-10 (P1) Ask Agent drawer and onboarding demo are mock-only
- Evidence: AgentDrawer simulates responses (`AgentDrawer.tsx:192-207`), AgentDemoStep is mock-first (`AgentDemoStep.tsx:1-6, 150-178`).
- Fix: Wire Ask Agent drawer to real chat API or disable in production; convert demo to real workflow (create test deal, request approval).
- Dependencies: agent API auth; SSE handling in drawer.
- Systemic prevention: runtime guard that hides demo-only components when `ENV=production`.
- Better ideas: (1) Add “Agent smoke test” that runs a real tool call and verifies DB write. (2) Provide guided “first deal” walkthrough with HITL approvals.
- Verification: Ask Agent drawer should call `/api/chat` and render streamed tokens.

L-11 (P1) Chat renders raw markdown; agent responses look broken
- Evidence: Chat MessageBubble renders plain text (`apps/dashboard/src/app/chat/page.tsx:1035-1047`); chat API returns markdown in fallback responses (`apps/dashboard/src/app/api/chat/route.ts` uses `generateHelpfulResponse`).
- Fix: Render markdown via `react-markdown` + `remark-gfm` and sanitize.
- Dependencies: security review for markdown (XSS); styling.
- Systemic prevention: standardized MarkdownMessage component used across UI.
- Better ideas: (1) Render structured actions as cards with explicit buttons. (2) Add inline citations with hover previews.
- Verification: markdown `**bold**` renders as bold and tables render correctly.

L-12 (P1) Agent deal count mismatch vs UI deal count (RAG vs DB)
- Evidence: Agent tool search uses RAG REST as primary data source (`apps/agent-api/app/core/langgraph/tools/deal_tools.py:469-507`); UI deals list uses DB `/api/deals` (`apps/dashboard/src/lib/api.ts:424-445`).
- Fix: Ensure RAG index is updated or use backend DB for authoritative counts; surface provenance and staleness in UI.
- Dependencies: RAG index refresh pipeline; deal events outbox.
- Systemic prevention: enforce source-of-truth contract and display provenance in chat responses.
- Better ideas: (1) Add “Index status” badge in chat (fresh/stale). (2) Provide “Reindex deal” button in deal detail.
- Verification: `curl http://localhost:8091/api/deals | jq 'length'` equals chat-reported count; chat includes provenance.

L-13 (P2) Action status casing mismatch breaks due actions and alerts
- Evidence: deferred-actions due filter uses uppercase statuses `PENDING_APPROVAL, READY, QUEUED` (`apps/dashboard/src/app/api/deferred-actions/due/route.ts:28-32`); alerts route filters `FAILED` and `PENDING_APPROVAL` (`apps/dashboard/src/app/api/alerts/route.ts:58-71`). Backend action statuses are typically lowercase in DB and UI.
- Fix: Normalize statuses to lowercase in API routes or update filters.
- Dependencies: action status enum definition.
- Systemic prevention: shared enum constants in both backend and UI.
- Better ideas: (1) Add a status normalization middleware. (2) Add a UI diagnostic panel for status distribution.
- Verification: due actions and alerts counts match `/api/actions` real status values.

L-14 (P2) Conflicting /api/actions/capabilities and /metrics handlers
- Evidence: main app returns 501 (`main.py:1036-1055`), while router defines real responses (`routers/actions.py:1-45`). This can cause `isKineticApiAvailable` to return false and trigger mock fallbacks.
- Fix: Remove 501 handlers or ensure router overrides; add contract test to ensure 200 response.
- Dependencies: routing order; OpenAPI generation.
- Systemic prevention: CI test to detect duplicate route definitions.
- Better ideas: (1) Generate capabilities from YAML registry automatically. (2) Version capabilities and surface compatibility in UI.
- Verification: `/api/actions/capabilities` returns 200 with real capabilities.

L-15 (P2) Deal materials/case-file/enrichment endpoints used by UI but not implemented
- Evidence: UI calls `/api/deals/{id}/case-file`, `/enrichment`, `/materials` (`apps/dashboard/src/lib/api.ts:556-617, 872-881`). No corresponding backend routes in `zakops-backend/src/api/orchestration/main.py`.
- Fix: Implement endpoints or hide tabs until backend exists.
- Dependencies: data model for materials and enrichment; filesystem integration.
- Systemic prevention: feature flags tied to backend capability checks.
- Better ideas: (1) Add materials indexing and preview with file viewer. (2) Provide enrichment provenance and confidence scores.
- Verification: endpoints return 200 with expected schema and UI renders tabs.

## Feature -> Contract Mapping (every UI action)
This table summarizes expected contracts. Auth column notes if backend requires X-API-Key (write methods). All endpoints are prefixed with `/api` at the dashboard.

### Deals
- Load deals list: GET `/api/deals?stage=&status=&broker=` -> Deal[]; Auth: none; UI: list/board update. Evidence: `apps/dashboard/src/lib/api.ts:424-445`.
- Open deal detail: GET `/api/deals/{deal_id}` -> DealDetail; Auth: none; UI: detail page. Evidence: `apps/dashboard/src/app/deals/page.tsx:520-526`.
- Delete (archive) single: POST `/api/deals/{deal_id}/archive` body `{operator, reason}`; Auth: X-API-Key; UI: remove row. Evidence: `apps/dashboard/src/lib/api.ts:451-461`.
- Bulk delete (archive): POST `/api/deals/bulk-archive` body `{deal_ids, operator, reason}`; Auth: X-API-Key; UI: remove rows. Evidence: `apps/dashboard/src/lib/api.ts:467-478`.
- Transition deal stage: POST `/api/deals/{deal_id}/transition` body `{new_stage, reason}`; Auth: X-API-Key; UI: refresh detail/board. Evidence: `apps/dashboard/src/lib/api.ts:971-987`.
- Add note: POST `/api/deals/{deal_id}/notes` body `{content, category}`; Auth: X-API-Key; UI: refresh events. Evidence: `apps/dashboard/src/lib/api.ts:993-1004`.
- Deal materials/case-file/enrichment: GET `/api/deals/{id}/materials|case-file|enrichment`; Auth: none; UI: tabs. Evidence: `apps/dashboard/src/lib/api.ts:556-617, 872-881`.

### Quarantine
- Load queue: GET `/api/actions/quarantine` -> QuarantineItem[]; Auth: none. Evidence: `apps/dashboard/src/lib/api.ts:736-757`, `apps/dashboard/src/app/api/actions/quarantine/route.ts:26-54`.
- Preview: GET `/api/actions/quarantine/{id}/preview` -> QuarantinePreview; Auth: none. Evidence: `apps/dashboard/src/lib/api.ts:763-771`.
- Approve: POST `/api/actions/{id}/approve` then POST `/api/actions/{id}/execute`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:781-792`.
- Reject: POST `/api/actions/quarantine/{id}/reject`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:800-821`.
- Delete: POST `/api/quarantine/{id}/delete` or `/api/quarantine/bulk-delete`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:839-866`.

### Actions
- List actions: GET `/api/actions` -> Action[]; Auth: none. Evidence: `apps/dashboard/src/lib/api.ts:1550-1578`.
- Get action: GET `/api/actions/{id}` -> Action; Auth: none. Evidence: `apps/dashboard/src/lib/api.ts:1608-1622`.
- Create action: POST `/api/actions` body `{deal_id, action_type, capability_id, inputs...}`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:1634-1654`.
- Approve action: POST `/api/actions/{id}/approve` body `{approved_by}`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:1660-1667`.
- Execute action: POST `/api/actions/{id}/execute`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:1673-1678`.
- Cancel/Retry/Update: POST `/api/actions/{id}/cancel|retry|update`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:1684-1715`.
- Bulk archive/delete: POST `/api/actions/bulk/archive|bulk/delete`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:1805-1826`.
- Clear completed: POST `/api/actions/clear-completed`; Auth: X-API-Key. Evidence: `apps/dashboard/src/lib/api.ts:1830-1869`, `apps/dashboard/src/app/actions/page.tsx:485-499`.

### Chat
- Stream chat: POST `/api/chat` with `{query, scope, session_id, options}`; SSE tokens; Auth: none (service token for agent provider). Evidence: `apps/dashboard/src/lib/api.ts:1144-1218`, `apps/dashboard/src/app/api/chat/route.ts:17-89`.
- Execute proposal: POST `/api/chat/execute-proposal` (not evaluated here).

### Settings / Onboarding
- Provider settings: localStorage only; Test connection uses GET `/api/chat` (no handler). Evidence: `apps/dashboard/src/lib/settings/provider-settings.ts:105-156`.
- Onboarding email connect: mock OAuth only. Evidence: `EmailSetupStep.tsx:52-60`.

## Deep Dives (required)

### 1) Deals detail routing + /api/deals/* mismatch
- Root cause: `/deals/[id]` captures “new” and “GLOBAL” and immediately calls GET `/api/deals/{id}` (`deals/[id]/page.tsx:89-126`), leading to 404.
- Fix: add `/deals/new` page or guard reserved slugs; map GLOBAL to a global view or block.
- Evidence: `deals/[id]/page.tsx:315-325` shows endpoint and error state.

### 2) Bulk delete (Deals + Actions) “Method Not Allowed”
- Deals bulk archive uses `/api/deals/bulk-archive` (no backend route), so FastAPI sees POST on `/api/deals/{deal_id}` and returns 405.
- Actions clear-completed uses `/api/actions/clear-completed` (no backend route), so FastAPI matches `/api/actions/{action_id}` and returns 405.
- Evidence: `apps/dashboard/src/lib/api.ts:467-478`, `apps/dashboard/src/app/api/actions/clear-completed/route.ts:48-85`, backend `main.py:465-949, 1036-1105`.

### 3) Quarantine delete + non-clickable actions
- Delete calls `/api/quarantine/{id}/delete` (missing). Approve/reject use Kinetic actions endpoints; execute endpoint missing.
- Evidence: `apps/dashboard/src/lib/api.ts:781-866`, backend quarantine process endpoint `main.py:1358-1483`.

### 4) Onboarding: Smart Email Triage -> missing email settings
- Email setup is mock-only; Settings page has no email configuration surface.
- Evidence: `EmailSetupStep.tsx:52-60`, `settings/page.tsx` (provider-only), backend email API exists `routers/email.py`.

### 5) Onboarding: Meet Your Agent demo-only
- Agent demo uses mock timers and Ask Agent drawer uses simulated response.
- Evidence: `AgentDemoStep.tsx:1-6,150-178`, `AgentDrawer.tsx:192-207`.

### 6) Chat: rendering + deal truth mismatch
- Rendering uses plain text; markdown is not parsed (`chat/page.tsx:1035-1047`).
- Agent deal search uses RAG REST; may diverge from DB counts (`deal_tools.py:469-507`).
- Fix: add markdown renderer + add provenance + align counts.

### 7) Settings: redesign + real configuration
- Current settings only cover AI provider; no email, agent behavior, auth, or integrations; stored in localStorage.
- Evidence: `settings/page.tsx`, `provider-settings.ts:105-118`.

## Systemic Patterns and Generalized Solutions
1) Proxy/route collisions: Next API routes override rewrites; missing methods lead to 405. -> Add route audit tests + OpenAPI-based client generation.
2) Mock fallbacks in production paths: UI shows success without backend execution. -> Feature-flag mocks; require explicit “demo mode”.
3) Auth mismatch for writes: client writes without API key. -> Centralize write calls in server routes or introduce session-based auth.
4) Multiple API clients (api.ts vs api-client.ts) with inconsistent validation/caching. -> Single API client with typed schemas + React Query.
5) No contract guardrails: missing endpoints discovered only at runtime. -> Contract gate + Playwright E2E gate.

## Phased Remediation Plan (summary)
- R4-0 Baseline contract inventory: enumerate UI actions -> endpoints, methods, schemas; verify with curl.
- R4-1 Endpoint contract stabilization: add missing backend endpoints or change UI; fix method mismatches and reserved slugs.
- R4-2 Quarantine workflow fix: use `/api/quarantine/{id}/process`, fix preview, ensure deal creation.
- R4-3 Actions execution fix: implement execute/cancel/retry/update and clear-completed; remove mocks in production.
- R4-4 Chat UX + truth: markdown rendering + provenance; align agent search source.
- R4-5 Settings + Onboarding: build email settings + real OAuth; persist onboarding state.
- Gates: Contract Gate, Playwright E2E Gate, Observability Gate, No Dead UI Gate (see plan file).

## Verification Commands (examples)
```
# Deal detail (reserved slugs should not call /api/deals/{id})
curl -i http://localhost:3003/deals/new
curl -i http://localhost:3003/deals/GLOBAL

# Bulk archive deals (post-fix)
curl -i -X POST http://localhost:8091/api/deals/bulk-archive \
  -H "X-API-Key: $ZAKOPS_API_KEY" -H "Content-Type: application/json" \
  -d '{"deal_ids":["DL-0001"],"operator":"qa"}'

# Quarantine approve (canonical)
curl -i -X POST http://localhost:8091/api/quarantine/{id}/process \
  -H "X-API-Key: $ZAKOPS_API_KEY" -H "Content-Type: application/json" \
  -d '{"action":"approve","processed_by":"qa"}'

# Actions clear completed (post-fix)
curl -i -X POST http://localhost:8091/api/actions/clear-completed \
  -H "X-API-Key: $ZAKOPS_API_KEY" -H "Content-Type: application/json" \
  -d '{"operation":"delete","age":"all"}'

# Chat markdown rendering test
curl -s http://localhost:3003/api/chat -X POST -H "Content-Type: application/json" \
  -d '{"query":"Render **bold** text"}'
```

## Two Better Ideas per Issue (appendix)
- L-01: (1) Dedicated “Deal Intake” page with schema-driven form. (2) Global portfolio analytics page instead of using GLOBAL slug.
- L-02: (1) Bulk archive preview with impact analysis. (2) Safe-delete workflow with undo window.
- L-03: (1) Session-based auth + RBAC; remove API key from client. (2) Signed request headers with replay protection.
- L-04: (1) Quarantine triage assisted by AI summary + risk score. (2) Link-to-existing-deal workflow with fuzzy matching.
- L-05: (1) Precomputed preview snapshots stored in DB. (2) Unified “quarantine_item_id” type to avoid action/quarantine confusion.
- L-06: (1) Retention policy UI with scheduled cleanup. (2) “Archive completed” job with audit trail.
- L-07: (1) Action execution pipeline with job queue and retries. (2) Action sandbox to simulate runs before execution.
- L-08: (1) Real agent health check with latency and model metadata. (2) Provider connection history and alerts.
- L-09: (1) Email integration dashboard (sync status, errors). (2) Rules engine for email-to-deal association.
- L-10: (1) Ask Agent drawer uses real agent with lightweight “quick ask”. (2) Guided agent tour that executes a real tool call.
- L-11: (1) Markdown renderer with citation hover cards. (2) Rich response cards (deal summaries, actions).
- L-12: (1) Provenance badges in chat. (2) Auto-reindex button when RAG is stale.
- L-13: (1) Shared status enums across backend and UI. (2) Status normalization middleware.
- L-14: (1) Route conflict detection in CI. (2) Auto-generated SDK and API contract tests.
- L-15: (1) Materials timeline with file viewer. (2) Enrichment provenance + confidence display.
