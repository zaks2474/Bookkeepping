AGENT IDENTITY
- agent_name: Codex
- run_id: 20260205-1723-r4d1
- date_time: 2026-02-05T17:23:20Z
- repo_revision_dashboard: b96b33c5547258663123a637dcff741c96b028c9
- repo_revision_backend: 2a68de172c7faf1df6f53357f4b43b0161d5dd32
- repo_revision_agent_api: b96b33c5547258663123a637dcff741c96b028c9

## Round-4 Remediation Plan (Dashboard Forensic + Product Hardening)
Goal: eliminate dead UI and method mismatches, wire real workflows from dashboard to backend/agent, and add hard gates so contract drift cannot recur.

### Non-negotiable Gates (must pass before shipping)
Gate A — Contract Gate (Dashboard <-> API)
- For every UI action, define endpoint + method + request + response + auth; verify against backend OpenAPI or route list.
- Automated check: fail build if UI calls a non-existent route or wrong method.

Gate B — E2E Gate (Playwright)
- Must pass tests for deals list, deal detail, bulk delete, quarantine approve/reject/delete, actions clear-completed, chat rendering, onboarding email settings.

Gate C — Observability Gate
- Each UI action logs correlation_id in dashboard logs and backend logs; verify via request ID headers.

Gate D — No Dead UI Gate
- Static scan for onClick handlers with TODO/empty; scan for fetch routes not in contract map; fail CI.

## Phase R4-0: Baseline Contract Inventory (blocking)
Objective: produce a definitive UI action map and verify against backend routes.
- Tasks:
  1) Enumerate all `fetch`/`apiFetch`/`agentClient` calls and map to actions.
  2) Export backend route list (FastAPI app routes) and compare.
  3) Record all 405/404 from a scripted curl run for each action endpoint.
- Dependencies: none
- Risks: incomplete mapping -> hidden failures
- Gate: Contract Gate must produce zero unknown routes.
- Acceptance criteria: a machine-readable map of actions->endpoints exists and every endpoint has a backend handler.
- Evidence required: route inventory file, diff report, curl outputs.

## Phase R4-1: Endpoint Contract Stabilization (P0)
Objective: fix route/method mismatches and reserved slugs.
- Tasks:
  1) Add `/deals/new` route or guard reserved slugs in `/deals/[id]`.
  2) Implement `/api/deals/bulk-archive` or adjust UI to loop single archive.
  3) Normalize API key injection for all write requests (route all writes through Next API routes or use session auth).
  4) Fix `/api/actions/clear-completed` and `bulk` endpoints (or remove buttons until implemented).
- Dependencies: auth model decision, backend write endpoints.
- Risks: breaking existing write paths.
- Gate: Contract Gate + No Dead UI Gate.
- Acceptance criteria: no 405/404 for core actions; reserved slugs render correct UI.
- Evidence required: curl proofs for each endpoint; Playwright tests for /deals/new and bulk delete.

## Phase R4-2: Quarantine Workflow Fix (P0)
Objective: approvals and previews operate on canonical quarantine endpoints.
- Tasks:
  1) Switch approve/reject to `/api/quarantine/{id}/process` (or implement action execute endpoints).
  2) Fix preview: `/api/quarantine/{id}` or new `/preview` endpoint.
  3) Implement delete/hide endpoints or explicitly remove delete UI.
- Dependencies: quarantine schema, deal creation logic, audit log.
- Risks: partial state transitions if approval fails mid-flight.
- Gate: Playwright quarantine tests, Observability Gate.
- Acceptance criteria: approve creates deal; preview loads; delete works or removed.
- Evidence required: curl POST `/api/quarantine/{id}/process` returns deal_id; UI shows item removed and deal appears.

## Phase R4-3: Actions Execution + Bulk Ops (P0)
Objective: ensure action lifecycle endpoints exist and UI uses them.
- Tasks:
  1) Implement `/api/actions/{id}/execute|cancel|retry|update` endpoints.
  2) Implement `/api/actions/clear-completed` and `/api/actions/bulk/*` or adjust UI.
  3) Resolve `/api/actions/capabilities` conflict (501 vs router).
- Dependencies: action engine, worker queue, audit trail.
- Risks: action execution side-effects; idempotency.
- Gate: Contract Gate, Playwright actions tests.
- Acceptance criteria: actions can be approved, executed, cleared without 405; metrics render.
- Evidence required: curl tests for each endpoint; UI confirms status changes.

## Phase R4-4: Chat UX + Truth (P1)
Objective: correct rendering and align agent data source with UI.
- Tasks:
  1) Add markdown renderer in chat and sanitize output.
  2) Add provenance indicators and RAG index freshness badges.
  3) Ensure agent deal count uses DB counts or reindex before responding.
- Dependencies: RAG indexing pipeline, UI components.
- Risks: XSS if markdown not sanitized.
- Gate: Playwright chat rendering test; contract test for agent search provenance.
- Acceptance criteria: markdown renders correctly; deal counts match UI or are labeled as RAG.
- Evidence required: chat screenshot + curl outputs for `/api/deals` and RAG.

## Phase R4-5: Settings + Onboarding Product Hardening (P1)
Objective: real email integration and durable settings.
- Tasks:
  1) Build Settings sections for email integration using `/api/integrations/email/*` endpoints.
  2) Replace mock onboarding email step with real OAuth flow.
  3) Persist onboarding state to backend instead of localStorage.
  4) Fix provider test endpoint (add GET `/api/chat/health` or use agent `/health`).
- Dependencies: auth/session model; OAuth credentials.
- Risks: OAuth complexity, secrets handling.
- Gate: Playwright onboarding tests + Contract Gate.
- Acceptance criteria: email connect success persists; settings show connected accounts.
- Evidence required: API responses from email endpoints; UI confirmation.

## Phase R4-6: Observability + Regression Proof (P2)
Objective: prevent regressions and add traceability.
- Tasks:
  1) Add correlation_id header from UI to backend for all actions.
  2) Add Playwright suite for all critical actions.
  3) Add No Dead UI static scan in CI.
- Dependencies: logging formats.
- Risks: performance overhead.
- Gate: Observability Gate, E2E Gate.
- Acceptance criteria: trace ID visible in dashboard+backend logs for every action.
- Evidence required: log excerpts with matching IDs.

## Issue-to-Phase Mapping
- L-01 -> R4-1
- L-02 -> R4-1
- L-03 -> R4-1
- L-04 -> R4-2
- L-05 -> R4-2
- L-06 -> R4-3
- L-07 -> R4-3
- L-08 -> R4-5
- L-09 -> R4-5
- L-10 -> R4-5
- L-11 -> R4-4
- L-12 -> R4-4
- L-13 -> R4-6
- L-14 -> R4-3
- L-15 -> R4-1

## Proof Artifacts Required
- Contract map file (UI action -> endpoint/method)
- curl outputs for each action endpoint
- Playwright test run logs
- Log correlation samples

