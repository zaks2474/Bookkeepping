AGENT IDENTITY
- agent_name: Codex
- run_id: 20260205-1842-p2r4
- date_time: 2026-02-05T18:42:00Z
- repo_revision_dashboard: b96b33c5547258663123a637dcff741c96b028c9
- repo_revision_backend: 2a68de172c7faf1df6f53357f4b43b0161d5dd32
- repo_revision_agent_api: b96b33c5547258663123a637dcff741c96b028c9

# Round-4 Execution Blueprint (PASS2)

## 0) Stabilize Visible UX First (Stop-the-bleeding order)
1) **Deal routing**: `/deals/new` and `/deals/GLOBAL` must not hit `/deals/[id]` fetch.
2) **Bulk actions 405**: Deals bulk archive/delete and Actions clear‑completed/bulk endpoints must resolve to real handlers.
3) **Quarantine actions**: Approve/reject/preview/delete must call canonical quarantine endpoints (not action proxies).
4) **Auth for writes**: Ensure X‑API‑Key (or equivalent) is injected for all write requests.
5) **Chat truth + rendering**: Ensure agent deal count uses DB source or labeled; render markdown.

## 1) Required Endpoint/Contract Inventory (explicit list)
The following endpoints must exist and be used exactly as listed; if not implemented, mark **NEEDS VERIFICATION** and add before UI wiring.

### Deals (Backend 8091)
- `GET /api/deals` → list deals. Response: array of deal objects (NEEDS VERIFICATION: shape).
- `POST /api/deals` → create deal. Payload: `{...}` (NEEDS VERIFICATION: required fields).
- `GET /api/deals/{id}` → deal detail.
- `POST /api/deals/{id}/archive` → archive deal (exists).
- `POST /api/deals/{id}/transition` → stage transition (exists per cooldown middleware).
- `POST /api/deals/{id}/notes` → add note.
- `POST /api/deals/bulk-archive` → bulk archive (missing; implement OR change UI to loop single‑archive). **NEEDS VERIFICATION**.
- `POST /api/deals/bulk-delete` → bulk delete (missing; implement OR remove UI). **NEEDS VERIFICATION**.

### Quarantine (Backend 8091)
- **Canonical path must be decided**: either `/api/quarantine/*` or `/api/triage/quarantine/*` — do not mix.
- `GET /api/quarantine` (or `/api/triage/quarantine`) → list items.
- `GET /api/quarantine/{id}` → item detail/preview (or provide `/preview`).
- `POST /api/quarantine/{id}/process` → approve/reject with payload `{decision, operator, reason?}` (exists in `main.py`).
- `DELETE /api/quarantine/{id}` → delete/withdraw item (if product approves). **NEEDS VERIFICATION**.

### Actions (Backend 8091)
- `GET /api/kinetic/actions` → list actions.
- `GET /api/kinetic/actions/{id}` → action detail.
- `POST /api/kinetic/actions/{id}/approve` → approve.
- `POST /api/kinetic/actions/{id}/reject` → reject.
- `POST /api/kinetic/actions/{id}/execute` → run action. **NEEDS VERIFICATION** (backend currently lacks).
- `POST /api/kinetic/actions/{id}/cancel` → cancel. **NEEDS VERIFICATION**.
- `POST /api/kinetic/actions/{id}/retry` → retry. **NEEDS VERIFICATION**.
- `POST /api/kinetic/actions/bulk/delete` → bulk delete. **NEEDS VERIFICATION**.
- `POST /api/kinetic/actions/clear-completed` → clear completed. **NEEDS VERIFICATION**.

### Chat / Agent API (8095)
- `POST /api/chat` (dashboard proxy to agent) → SSE streaming.
- `GET /health` (agent health) used for settings “test connection”.

### Settings / Email Integration
- `GET/POST /api/integrations/email/*` (exists in backend routers) used by settings.
- Persisted settings endpoints (if missing) must be defined: `/api/settings/provider`, `/api/settings/agent`, `/api/settings/notifications` (**NEEDS VERIFICATION**).

## 2) Reserved Slugs / Route Guards
The following slugs must be protected from `/deals/[id]` fetch:
- `new`
- `GLOBAL` / `global`
- `draft` (if draft route planned) **NEEDS VERIFICATION**

Implementation options:
- Create `src/app/deals/new/page.tsx` to take precedence.
- In `src/app/deals/[id]/page.tsx`, guard and redirect/route to global view.

Proof: E2E test should visit `/deals/new` and `/deals/GLOBAL` and verify they **do not** trigger `/api/deals/{id}`.

## 3) Auth/Header Rules (must be consistent)
- **All write methods** (POST/PUT/PATCH/DELETE) must include X‑API‑Key when hitting backend 8091.
- Client‑side `apiFetch` must not issue write requests directly unless a server proxy injects the key.
- Preferred rule: **Only Next.js API routes can perform writes**; UI uses those routes for POST/PUT/PATCH/DELETE.

Proof:
- For each write endpoint, verify success with key and failure (401) without key.
- CI lint: fail if client-side writes to `/api/*` occur without server proxy.

## 4) Phase Plan (P0 → P3)

### Phase P0 — Stop the Bleeding
**Objective:** Restore critical UX flows without 404/405 errors.

Atomic tasks:
1) Add `/deals/new` route OR slug guard in `/deals/[id]`.
2) Fix bulk operations mismatch (deals and actions) — choose canonical bulk endpoints and align UI/proxy/back‑end.
3) Wire quarantine approve/reject to canonical `/api/quarantine/{id}/process` endpoint.
4) Fix Settings “Test Connection” to call agent `/health` (GET) instead of `/api/chat`.

Dependencies:
- Decision on canonical quarantine base path (`/api/quarantine` vs `/api/triage/quarantine`).
- Decision on bulk operation endpoints (implement vs remove UI).

Rollback:
- Feature flag the new routes and proxy changes; revert by disabling flag.

Acceptance criteria:
- `/deals/new` renders creation UI; `/deals/GLOBAL` renders global view.
- Deals bulk action no longer returns 405/404.
- Quarantine approve/reject returns 200 and creates deal.
- Settings test connection returns 200.

Proof artifacts:
- Playwright tests for `/deals/new`, `/deals/GLOBAL`, quarantine approve, actions clear‑completed.
- Curl tests to backend endpoints with proper headers.

### Phase P1 — Contract Stabilization
**Objective:** Ensure all UI calls map to real backend routes + methods.

Atomic tasks:
1) Enumerate all `fetch/apiFetch` calls and map to endpoints.
2) Export backend route list and diff against UI map.
3) Add missing backend endpoints or remove UI actions.
4) Standardize payload schemas for bulk endpoints (ids vs deal_ids).

Dependencies:
- OpenAPI export for backend route list (or scripted route dump).

Rollback:
- Keep a feature‑flagged proxy map file; revert to previous mapping on failure.

Acceptance criteria:
- Zero “unknown route” diff entries.
- No 405/404 from any UI action in CI E2E run.

Proof artifacts:
- Route diff report.
- Contract map JSON.

### Phase P2 — Onboarding + Settings Real Wiring
**Objective:** Replace demo-only flows with backend‑persisted settings.

Atomic tasks:
1) Implement settings persistence endpoints (email/provider/agent/notifications).
2) Replace onboarding localStorage with API calls.
3) Implement email integration UI using `/api/integrations/email/*`.
4) Add buy box + notification preferences UI and persistence.

Dependencies:
- Auth model for settings endpoints.
- Secrets handling (encrypt at rest).

Rollback:
- Keep localStorage fallback hidden behind feature flag.

Acceptance criteria:
- Settings survive reload and match backend state.
- Onboarding completion persists and is reflected in API.

Proof artifacts:
- Screenshot + API logs for settings update.
- DB row confirmation for settings.

### Phase P3 — Polish + Observability
**Objective:** Harden UX, observability, and resilience.

Atomic tasks:
1) Add markdown rendering in chat with sanitization.
2) Add SSE reconnect logic + last-event-id resume.
3) Add correlation ID middleware and propagate to backend/agent logs.
4) Add ops health ribbon and disable UI actions when dependencies down.

Dependencies:
- Logging schema and trace ID acceptance in backend.

Rollback:
- Feature flags for SSE reconnect/health ribbon.

Acceptance criteria:
- All UI actions show correlation ID in logs.
- Chat renders markdown correctly.

Proof artifacts:
- Log samples with matching IDs.
- UI screenshots of markdown and health ribbon.

## 5) “No Dead UI” Detection Strategy

### Static checks
- `rg -n "onClick=\{\(\) => \{\s*\}\}" apps/dashboard/src` (empty handlers).
- `rg -n "TODO|FIXME|mock" apps/dashboard/src` for demo-only flow detection.
- Extract `apiFetch` methods and ensure all write calls are server-routed.

### Runtime checks (Playwright)
- Click every button on:
  - `/deals`, `/deals/[id]`, `/actions`, `/quarantine`, `/dashboard`, `/settings`, `/onboarding`, `/chat`.
- Assert no 404/405/500 toast messages.
- Verify buttons either work or are explicitly disabled with tooltip.

### Contract checks
- Generate route list from backend and compare to UI contract map.
- Fail CI if UI calls route not present in backend.

## 6) Tests/Gates (must be enforced)

**Gate 1: Contract Gate**
- Autogen UI route map from `apiFetch` + Next API routes.
- Autogen backend route list from FastAPI.
- Fail CI on mismatch.

**Gate 2: E2E Gate**
- Minimal flake tests for: deals list, deal detail, bulk delete, quarantine approve/reject, actions clear‑completed, onboarding email settings, chat markdown rendering.

**Gate 3: Auth Gate**
- For each write endpoint: assert 401 without X‑API‑Key; 200 with key.

**Gate 4: No Dead UI Gate**
- Static scan + Playwright actions; fail on missing handlers or no‑op.

**Gate 5: Observability Gate**
- Correlation ID must appear in dashboard logs and backend logs for each action.

