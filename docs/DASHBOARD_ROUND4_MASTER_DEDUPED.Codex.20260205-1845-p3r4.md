AGENT IDENTITY
- agent_name: Codex
- run_id: 20260205-1845-p3r4
- date_time: 2026-02-05T18:45:00Z
- repo_revision_dashboard: b96b33c5547258663123a637dcff741c96b028c9
- repo_revision_backend: 2a68de172c7faf1df6f53357f4b43b0161d5dd32
- repo_revision_agent_api: b96b33c5547258663123a637dcff741c96b028c9

# Round-4 Master Deduped Registry (PASS3)

Sources reviewed (from Run Index + PASS1/PASS2):
- Claude-Opus forensic + plan
- Codex forensic + plan
- Gemini-CLI forensic + plan
- PASS1 evaluations (Claude, Codex, Gemini)
- PASS2 execution blueprints (Claude, Codex)

## A) Master Deduped Limitations Registry

R4-001 Deal routing slugs captured by /deals/[id]
- Subsystem: deals/routing
- Symptom: /deals/new and /deals/GLOBAL show "Failed to load deal" and call /api/deals/{id}
- Suspected root cause: catch-all [id] route without slug guard or dedicated /deals/new
- Affected routes/endpoints: /deals/[id], GET /api/deals/{id}
- Fix options:
  1) Create /deals/new route with precedence
  2) Guard reserved slugs in /deals/[id]
- Dependencies: product decision on GLOBAL view and create flow
- Verification: Playwright visits /deals/new and /deals/GLOBAL; assert no GET /api/deals/{id} for slugs
- Two better ideas: (1) Command-palette deal creation. (2) Global portfolio analytics page instead of GLOBAL slug.
- Sources: [Claude, Codex, Gemini, PASS2]

R4-002 Deal creation workflow undefined or unverified
- Subsystem: deals/creation
- Symptom: no confirmed create form or create endpoint for /deals/new
- Root cause: missing /deals/new UI and/or POST /api/deals contract not verified
- Routes/endpoints: /deals/new, POST /api/deals (NEEDS VERIFICATION)
- Fix options: implement create form + backend create endpoint; wire to auth
- Dependencies: schema for deal creation, auth headers
- Verification: curl POST /api/deals returns new deal_id; UI redirects to detail
- Two better ideas: (1) Draft deals with temporary IDs. (2) Create-from-template modal.
- Sources: [PASS1, Gemini, Claude]

R4-003 Deals bulk archive/delete returns 405/404
- Subsystem: deals/bulk
- Symptom: bulk operation toast shows Method Not Allowed
- Root cause: UI calls /api/deals/bulk-archive or bulk-delete not implemented or misrouted
- Routes/endpoints: POST /api/deals/bulk-archive, POST /api/deals/bulk-delete (NEEDS VERIFICATION)
- Fix options: implement backend bulk endpoints OR loop single-archive/delete
- Dependencies: auth header injection, audit log
- Verification: curl bulk endpoint returns 200 and UI list updates
- Two better ideas: (1) Bulk preview with impact analysis. (2) Undo window with safe-delete.
- Sources: [Claude, Codex, Gemini, PASS2]

R4-004 Deal materials/case-file/enrichment endpoints missing
- Subsystem: deals/materials
- Symptom: materials/enrichment panels likely empty or error
- Root cause: UI calls endpoints not implemented in backend
- Routes/endpoints: GET /api/deals/{id}/materials, /enrichment, /case-file (NEEDS VERIFICATION)
- Fix options: implement endpoints or remove UI sections with explanation
- Dependencies: storage layer, RAG/document indexing
- Verification: curl endpoints return data for existing deal
- Two better ideas: (1) Materials timeline with inline viewer. (2) Enrichment provenance + confidence display.
- Sources: [Codex]

R4-005 Pagination and filter persistence not implemented/verified
- Subsystem: deals/actions/quarantine lists
- Symptom: filters reset or lists load all items; pagination behavior unclear
- Root cause: missing URL param persistence and/or backend pagination params
- Routes/endpoints: GET /api/deals, /api/actions, /api/quarantine (NEEDS VERIFICATION)
- Fix options: implement limit/offset params; persist filters in URL
- Dependencies: backend pagination support, UI state store
- Verification: apply filter, navigate away/back, filter persists and page size honored
- Two better ideas: (1) Saved views with shareable URLs. (2) Server-driven infinite scroll with cursor.
- Sources: [PASS1]

R4-006 Deal edit (PATCH) endpoints missing/untested
- Subsystem: deals/edit
- Symptom: deal metadata edits beyond notes not supported
- Root cause: missing PATCH /api/deals/{id} or UI not wired
- Routes/endpoints: PATCH /api/deals/{id} (NEEDS VERIFICATION)
- Fix options: implement patch endpoint + edit UI
- Dependencies: validation schema, auth
- Verification: edit title/broker, refresh page, data persists
- Two better ideas: (1) Inline editable fields with autosave. (2) Change history diff view.
- Sources: [PASS1]

R4-007 Invalid stage transition handling not tested
- Subsystem: deals/stage transitions
- Symptom: unknown whether invalid transition returns proper error
- Root cause: missing tests for invalid transition, unclear backend validation
- Routes/endpoints: POST /api/deals/{id}/transition
- Fix options: enforce allowed transitions and return 422 with allowed list
- Dependencies: stage model, transition rules
- Verification: attempt invalid transition returns 422 and UI shows error
- Two better ideas: (1) Transition timeline with guardrails. (2) Stage-aware action recommendations.
- Sources: [PASS1]

R4-008 Deal export/print not supported
- Subsystem: deals/export
- Symptom: no export/print flow
- Root cause: missing UI and API
- Routes/endpoints: (NEEDS VERIFICATION)
- Fix options: add export button + backend report endpoint
- Dependencies: data privacy policy
- Verification: export file generated and downloadable
- Two better ideas: (1) PDF summary pack. (2) Shareable read-only deal link.
- Sources: [PASS1]

R4-009 Reserved slug collisions on other routes not guarded
- Subsystem: routing
- Symptom: /actions/[id] or /quarantine/[id] could capture reserved slugs (metrics, bulk)
- Root cause: missing reserved slug guards beyond deals
- Routes/endpoints: /actions/[id], /quarantine/[id] (NEEDS VERIFICATION)
- Fix options: add explicit routes or slug guards
- Dependencies: route inventory
- Verification: Playwright visits /actions/metrics, /quarantine/stats
- Two better ideas: (1) Regex validation for IDs. (2) Route guard test suite.
- Sources: [PASS2]

R4-010 Actions bulk delete / clear completed 405
- Subsystem: actions/bulk
- Symptom: "Method Not Allowed" on delete completed actions
- Root cause: proxy path mismatch or missing backend endpoints
- Routes/endpoints: POST /api/actions/clear-completed, POST /api/actions/bulk/delete
- Fix options: implement backend endpoints under /api/kinetic/actions or change UI
- Dependencies: action engine, auth
- Verification: curl endpoints return affected_count; UI list updates
- Two better ideas: (1) Scheduled cleanup policy UI. (2) Bulk action dry-run preview.
- Sources: [Claude, Codex, Gemini]

R4-011 Action execution endpoints missing
- Subsystem: actions/execution
- Symptom: approve/run/cancel/retry buttons may fail or no-op
- Root cause: backend lacks /execute, /cancel, /retry, /update
- Routes/endpoints: POST /api/kinetic/actions/{id}/execute|cancel|retry|update (NEEDS VERIFICATION)
- Fix options: implement endpoints or remove buttons until ready
- Dependencies: worker queue, audit log
- Verification: action status changes on execute/cancel/retry
- Two better ideas: (1) Action sandbox simulation. (2) Retry with backoff + error classification.
- Sources: [Codex, PASS2]

R4-012 Action hard delete endpoint missing/untested
- Subsystem: actions/delete
- Symptom: delete action may 404/405
- Root cause: DELETE /api/actions/{id} not implemented
- Routes/endpoints: DELETE /api/kinetic/actions/{id} (NEEDS VERIFICATION)
- Fix options: implement soft delete or remove delete UI
- Dependencies: retention policy
- Verification: delete removes action from list
- Two better ideas: (1) Archive vs delete. (2) Retention rules with admin override.
- Sources: [PASS1]

R4-013 Actions capabilities endpoint conflict
- Subsystem: actions/capabilities
- Symptom: /api/actions/capabilities returns 501 or conflicting payloads
- Root cause: multiple handlers (orchestration vs router) with different outputs
- Routes/endpoints: GET /api/actions/capabilities
- Fix options: pick canonical handler; remove or rename the other
- Dependencies: OpenAPI contract
- Verification: curl /api/actions/capabilities returns consistent payload
- Two better ideas: (1) Contract tests for capabilities schema. (2) Capability feature flags per tenant.
- Sources: [Codex]

R4-014 Action status casing mismatch breaks alerts/due actions
- Subsystem: actions/status
- Symptom: due actions and alerts show incorrect counts
- Root cause: UI expects uppercase statuses while backend returns lowercase (or vice versa)
- Routes/endpoints: /api/deferred-actions/due, /api/alerts
- Fix options: normalize statuses at API boundary or align enums
- Dependencies: shared enum spec
- Verification: counts match between backend and UI
- Two better ideas: (1) Shared status enum package. (2) Status normalization middleware.
- Sources: [Codex]

R4-015 Actions delete count UI mismatch
- Subsystem: actions/UI
- Symptom: "0 action(s) will be deleted" when actions exist
- Root cause: selected count calculation bug or stale state
- Routes/endpoints: actions page state
- Fix options: fix selection state, recompute count
- Dependencies: actions list state management
- Verification: modal shows correct count after selecting items
- Two better ideas: (1) Selection summary panel. (2) Persistent selection across filters.
- Sources: [Claude]

R4-016 Actions proxy path misalignment
- Subsystem: api-proxy/actions
- Symptom: UI calls /api/actions but backend expects /api/kinetic/actions
- Root cause: proxy or rewrite mismatch
- Routes/endpoints: /api/actions -> /api/kinetic/actions
- Fix options: update proxy routes or rewrite rules
- Dependencies: Next.js route handlers vs rewrites
- Verification: GET /api/actions returns backend list with no 404
- Two better ideas: (1) Centralized proxy map. (2) Generated client from OpenAPI.
- Sources: [Gemini, PASS1]

R4-017 Quarantine approve/reject wired to actions endpoints
- Subsystem: quarantine/approval
- Symptom: approve/reject may fail if action endpoints missing
- Root cause: UI uses /api/actions/{id}/approve + /execute instead of /api/quarantine/{id}/process
- Routes/endpoints: POST /api/quarantine/{id}/process (exists) vs /api/actions/{id}/approve
- Fix options: switch to quarantine process endpoint OR implement full action execution
- Dependencies: quarantine schema, deal creation logic
- Verification: approve removes item and creates deal
- Two better ideas: (1) AI summary + risk score on quarantine items. (2) Link-to-existing-deal workflow.
- Sources: [Codex]

R4-018 Quarantine preview uses wrong ID type
- Subsystem: quarantine/preview
- Symptom: "Preview not found" for some items
- Root cause: preview endpoint expects action_id but queue uses quarantine_item_id
- Routes/endpoints: GET /api/actions/quarantine/{id}/preview
- Fix options: use GET /api/quarantine/{id} or introduce preview endpoint keyed by item_id
- Dependencies: data model mapping
- Verification: preview loads for all queue items
- Two better ideas: (1) Precomputed preview snapshots. (2) Unified ID type across action/quarantine.
- Sources: [Claude, Codex]

R4-019 Quarantine delete endpoint missing
- Subsystem: quarantine/delete
- Symptom: delete shows Not Found toast
- Root cause: /api/quarantine/{id}/delete not implemented
- Routes/endpoints: POST /api/quarantine/{id}/delete or DELETE /api/triage/quarantine/{id}
- Fix options: implement delete or remove UI action
- Dependencies: product policy on deletion
- Verification: delete removes item or hides it
- Two better ideas: (1) Soft delete with audit trail. (2) "Snooze" instead of delete.
- Sources: [Claude, Codex, Gemini]

R4-020 Quarantine bulk delete not verified
- Subsystem: quarantine/bulk
- Symptom: bulk delete behavior unknown
- Root cause: missing tests and/or endpoints
- Routes/endpoints: POST /api/quarantine/bulk-delete (NEEDS VERIFICATION)
- Fix options: implement bulk endpoint or remove UI
- Dependencies: selection state, audit
- Verification: bulk delete removes N items
- Two better ideas: (1) Bulk approve/reject with summary. (2) Queue cleanup rules.
- Sources: [PASS1]

R4-021 Operator identity unvalidated
- Subsystem: auth/approval
- Symptom: operator name comes from localStorage
- Root cause: no server-side identity validation
- Routes/endpoints: approve/reject payloads include operator
- Fix options: derive operator from session, ignore client-provided operator
- Dependencies: auth/session system
- Verification: server rejects unknown operator
- Two better ideas: (1) Role-based approval policy. (2) Approval audit trail with user id.
- Sources: [PASS1]

R4-022 Chat renders raw markdown
- Subsystem: chat/rendering
- Symptom: **bold** shown as text
- Root cause: no markdown renderer
- Routes/endpoints: /chat UI
- Fix options: add markdown renderer with sanitization
- Dependencies: XSS-safe rendering policy
- Verification: UI renders bold/italics and lists
- Two better ideas: (1) Rich response cards. (2) Citation hover previews.
- Sources: [Claude, Codex, Gemini]

R4-023 Agent deal count mismatch (RAG vs DB)
- Subsystem: chat/data
- Symptom: agent says 3 deals; UI shows 9
- Root cause: agent search uses stale RAG index vs UI DB query
- Routes/endpoints: agent tool search_deals (RAG), UI GET /api/deals
- Fix options: reindex RAG, add hybrid search fallback, show provenance badge
- Dependencies: RAG pipeline
- Verification: agent count matches /api/deals count or labeled as RAG
- Two better ideas: (1) Data sync indicator in UI. (2) Auto-reindex button.
- Sources: [Claude, Codex, Gemini]

R4-024 Ask Agent drawer is mock-only / not integrated
- Subsystem: chat/drawer
- Symptom: drawer returns simulated responses, not real SSE
- Root cause: demo-only implementation
- Routes/endpoints: /dashboard sidebar -> /api/chat (not used)
- Fix options: wire to real chat API or remove in production
- Dependencies: agent API auth, SSE handling
- Verification: Ask Agent drawer streams real tokens
- Two better ideas: (1) Quick-ask mode with short responses. (2) Guided agent tour with real tool call.
- Sources: [Claude, Codex, Gemini]

R4-025 SSE reconnect/resume not verified
- Subsystem: chat/streaming
- Symptom: chat may drop on network loss
- Root cause: no reconnect logic
- Routes/endpoints: /api/chat SSE
- Fix options: implement reconnect with last-event-id
- Dependencies: SSE server supports resumption
- Verification: drop connection mid-stream; UI resumes
- Two better ideas: (1) Connection health badge. (2) Retry budget with backoff.
- Sources: [PASS1]

R4-026 Chat citation links untested
- Subsystem: chat/ux
- Symptom: unknown whether citations navigate correctly
- Root cause: missing E2E tests
- Routes/endpoints: chat message rendering
- Fix options: add E2E test for citation links
- Dependencies: citations schema
- Verification: click citation opens correct URL
- Two better ideas: (1) Side-panel preview. (2) Source pinning to deal record.
- Sources: [PASS1]

R4-027 Settings missing email configuration
- Subsystem: settings/email
- Symptom: no email integration section
- Root cause: Settings page only implements LLM provider
- Routes/endpoints: /settings
- Fix options: implement email integration UI + backend endpoints
- Dependencies: OAuth/IMAP config, secrets
- Verification: connect email and show sync status
- Two better ideas: (1) Email sync dashboard with errors. (2) Rules engine for auto-association.
- Sources: [Claude, Codex, Gemini]

R4-028 Settings missing agent config, buy box, notifications, retention, timezone, theme, default filters
- Subsystem: settings/general
- Symptom: settings page lacks key sections
- Root cause: settings model not implemented
- Routes/endpoints: /settings
- Fix options: add sections + persistence endpoints
- Dependencies: user settings schema
- Verification: settings persist across reload
- Two better ideas: (1) Profile templates. (2) Policy packs for teams.
- Sources: [Claude, PASS1, Codex]

R4-029 Settings provider "Test Connection" uses GET /api/chat
- Subsystem: settings/provider
- Symptom: test connection 405
- Root cause: /api/chat only supports POST
- Routes/endpoints: GET /api/chat (invalid)
- Fix options: add /api/chat/health or use agent /health
- Dependencies: agent health endpoint
- Verification: test connection returns 200
- Two better ideas: (1) Connection history log. (2) Latency + model metadata in UI.
- Sources: [Codex]

R4-030 Settings persistence uses localStorage only
- Subsystem: settings/persistence
- Symptom: settings lost across devices/clears
- Root cause: no backend persistence
- Routes/endpoints: (NEEDS VERIFICATION)
- Fix options: implement /api/settings endpoints and store in DB
- Dependencies: auth, encryption at rest
- Verification: settings persist across login
- Two better ideas: (1) Organization-wide defaults. (2) Export/import settings.
- Sources: [Codex, PASS1]

R4-031 Onboarding demo-only (localStorage)
- Subsystem: onboarding/persistence
- Symptom: onboarding completion not stored in backend
- Root cause: localStorage only
- Routes/endpoints: POST /api/onboarding/complete (NEEDS VERIFICATION)
- Fix options: add backend endpoint; persist profile/email
- Dependencies: user profile schema
- Verification: onboarding state survives reload
- Two better ideas: (1) Resume onboarding. (2) Admin re-onboard control.
- Sources: [Claude, Codex, Gemini]

R4-032 Onboarding CTA dead (Configure Email Settings)
- Subsystem: onboarding/email
- Symptom: button routes to settings with no email section
- Root cause: missing email settings UI
- Routes/endpoints: /settings#email
- Fix options: add email settings section and anchor link
- Dependencies: settings redesign
- Verification: CTA opens email settings panel
- Two better ideas: (1) Inline email setup modal. (2) Guided email connect wizard.
- Sources: [Claude]

R4-033 Meet Your Agent is demo-only
- Subsystem: onboarding/agent
- Symptom: capability cards open demo drawer, no real workflow
- Root cause: mock implementation
- Routes/endpoints: onboarding step, agent API
- Fix options: run real agent task (create test deal + approval)
- Dependencies: agent API auth, seed data
- Verification: onboarding step triggers real tool call
- Two better ideas: (1) Live agent trace viewer. (2) Sandbox environment for test run.
- Sources: [Claude, Codex, Gemini]

R4-034 Onboarding resume/skip/re-onboard missing
- Subsystem: onboarding/flow
- Symptom: cannot resume or redo onboarding
- Root cause: no persisted progress state
- Routes/endpoints: (NEEDS VERIFICATION)
- Fix options: store step progress; add re-onboard entry in settings
- Dependencies: user profile schema
- Verification: resume mid-step after reload
- Two better ideas: (1) Progress checkpointing. (2) Role-based onboarding paths.
- Sources: [PASS1]

R4-035 Client-side writes lack X-API-Key
- Subsystem: auth/requests
- Symptom: writes may fail in prod or bypass auth in dev
- Root cause: apiFetch does not inject key; rewrites do not add headers
- Routes/endpoints: all POST/PUT/PATCH/DELETE from client
- Fix options: route all writes through Next API routes that inject key or use session auth
- Dependencies: auth model decision
- Verification: 401 without key, 200 with key
- Two better ideas: (1) Signed requests with replay protection. (2) Session-based RBAC.
- Sources: [Codex, PASS1, Gemini]

R4-036 Next API route handlers override rewrites and drop methods
- Subsystem: api-proxy
- Symptom: 405 on DELETE when route.ts lacks handler
- Root cause: Next.js uses file-system route over rewrites
- Routes/endpoints: /api/* route handlers
- Fix options: export missing methods or remove route handlers
- Dependencies: proxy strategy decision
- Verification: DELETE/POST reach backend
- Two better ideas: (1) Centralized proxy registry. (2) Contract diff test.
- Sources: [Codex, Gemini, PASS1]

R4-037 Mock fallbacks mask real failures
- Subsystem: api-proxy
- Symptom: mock responses hide backend errors
- Root cause: fallback returns data on 404 but not 500/405
- Routes/endpoints: Next API routes with mocks
- Fix options: remove mocks in production; only use in dev with explicit banner
- Dependencies: backend readiness
- Verification: errors surface clearly; no [Mock] logs
- Two better ideas: (1) Mock server with explicit mode switch. (2) Feature flag for mock data.
- Sources: [Claude, Gemini]

R4-038 Error response schema inconsistent
- Subsystem: api-error handling
- Symptom: toast shows {detail} or {message} inconsistently
- Root cause: backend error formats not normalized
- Routes/endpoints: all
- Fix options: normalize errors at API boundary
- Dependencies: API error contract
- Verification: errors render consistent UI
- Two better ideas: (1) Structured error codes. (2) User-friendly error mapper.
- Sources: [PASS1]

R4-039 Correlation ID injection missing
- Subsystem: observability
- Symptom: cannot trace UI actions across services
- Root cause: apiFetch does not add correlation id
- Routes/endpoints: all
- Fix options: add middleware to inject X-Correlation-ID
- Dependencies: backend logging support
- Verification: same ID appears in frontend + backend logs
- Two better ideas: (1) Trace viewer in UI. (2) Automatic log linking from toasts.
- Sources: [PASS1, PASS2]

R4-040 Error boundaries and loading states inconsistent
- Subsystem: UX resilience
- Symptom: white screens or no skeletons on slow API
- Root cause: missing error boundaries and standardized loading components
- Routes/endpoints: multiple pages
- Fix options: add error boundaries + consistent skeletons
- Dependencies: component library updates
- Verification: forced API failure shows error UI
- Two better ideas: (1) Retry CTA with backoff. (2) Offline banner.
- Sources: [PASS1]

R4-041 Keyboard accessibility not verified
- Subsystem: UX/a11y
- Symptom: unclear tab order and keyboard support
- Root cause: missing a11y testing
- Fix options: add keyboard navigation tests
- Dependencies: design system
- Verification: Playwright a11y checks
- Two better ideas: (1) Skip-to-content link. (2) ARIA audit report.
- Sources: [PASS1]

R4-042 Offline/network failure handling missing
- Subsystem: UX/resilience
- Symptom: network loss behavior unknown
- Root cause: no retry logic or offline UI
- Fix options: add retry + offline banner
- Dependencies: network state hook
- Verification: simulate offline, see banner and retry
- Two better ideas: (1) Queue actions for retry. (2) Read-only offline mode.
- Sources: [PASS1]

R4-043 Session expiration handling missing
- Subsystem: auth/session
- Symptom: unknown behavior when API key expires
- Root cause: no session lifecycle handling
- Fix options: detect 401 and prompt re-auth
- Dependencies: auth provider
- Verification: simulate 401 -> redirect/login
- Two better ideas: (1) Silent re-auth. (2) Session countdown warning.
- Sources: [PASS1]

R4-044 Tenant isolation not addressed
- Subsystem: auth/tenancy
- Symptom: multi-tenant scoping unknown
- Root cause: no tenant guards in UI/requests
- Fix options: add tenant_id in API requests and enforce on backend
- Dependencies: multi-tenant data model
- Verification: cross-tenant access blocked
- Two better ideas: (1) Tenant switcher UI. (2) Tenant-scoped API keys.
- Sources: [PASS1]

R4-045 Rate limiting and idempotency not verified
- Subsystem: reliability
- Symptom: repeated clicks may duplicate operations
- Root cause: no rate limits or idempotency enforcement verified
- Fix options: add idempotency keys and server enforcement
- Dependencies: backend idempotency store
- Verification: duplicate POST with same key returns same response
- Two better ideas: (1) UI disables buttons while pending. (2) Debounce repeated clicks.
- Sources: [PASS1]

R4-046 Error tracking and performance monitoring missing
- Subsystem: observability
- Symptom: no JS error or perf telemetry
- Root cause: missing tooling (Sentry/LogRocket/Web Vitals)
- Fix options: integrate error tracking and perf metrics
- Dependencies: tooling decisions
- Verification: forced error appears in dashboard
- Two better ideas: (1) User-impact score dashboard. (2) API latency overlays.
- Sources: [PASS1]

R4-047 Pagination for actions/quarantine not verified
- Subsystem: actions/quarantine lists
- Symptom: large lists may be slow or incomplete
- Root cause: missing pagination in endpoints and UI
- Fix options: add pagination + infinite scroll
- Dependencies: backend pagination
- Verification: load page 2 via cursor
- Two better ideas: (1) Saved filters. (2) Bulk select across pages.
- Sources: [PASS1]

R4-048 File upload handling unverified
- Subsystem: materials/quarantine
- Symptom: upload paths/limits unknown
- Root cause: no UI mapping for uploads
- Fix options: define upload endpoints and UI
- Dependencies: storage policy
- Verification: upload file attaches to deal
- Two better ideas: (1) Drag/drop area. (2) Virus scanning on upload.
- Sources: [PASS1]

R4-049 Zod schemas overly loose (passthrough/unknown)
- Subsystem: schema validation
- Symptom: UI accepts unknown shapes; potential render bugs
- Root cause: loose Zod schema definitions (e.g., unknown links)
- Fix options: tighten schemas or use generated types
- Dependencies: OpenAPI schema
- Verification: enable strict mode; fix resulting errors
- Two better ideas: (1) Contract-first client generation. (2) Runtime schema diff tests.
- Sources: [PASS1 Gemini]

R4-050 API key rotation and auth lifecycle unaddressed
- Subsystem: auth
- Symptom: unknown behavior on key rotation
- Root cause: no re-auth handling or key refresh
- Fix options: add re-auth flow and key rotation support
- Dependencies: auth/secret management
- Verification: rotate key, UI prompts and recovers
- Two better ideas: (1) Dual-key grace period. (2) Key rotation notifications.
- Sources: [PASS1]

## B) Master Deduped Recommendations Catalog

### P0 - Stop the bleeding
- Add /deals/new route and slug guards for reserved slugs across /deals/[id].
- Fix bulk operations by implementing or removing /api/deals/bulk-archive and /api/actions/clear-completed.
- Switch quarantine approve/reject to /api/quarantine/{id}/process and fix preview ID mapping.
- Fix Settings "Test Connection" to call agent /health or /api/chat/health.
- Enforce X-API-Key (or session auth) for all write operations; route writes through Next API routes.

### P1 - Contract stabilization
- Generate a UI route map from apiFetch and compare to backend routes; fail CI on mismatch.
- Resolve actions proxy path mismatch (/api/actions vs /api/kinetic/actions).
- Implement missing action execution endpoints or disable buttons.
- Normalize action status enums between backend and UI.
- Remove mock fallbacks in production or gate behind explicit feature flag.

### P2 - Onboarding + settings real wiring
- Implement email integration UI using backend /api/integrations/email/* routes.
- Persist settings to backend (provider, agent, buy box, notifications, retention).
- Replace onboarding localStorage with backend persistence; add resume and re-onboard.
- Build "Meet Your Agent" real workflow (create test deal + approval).

### P3 - Polish + observability
- Add markdown rendering in chat with sanitization.
- Add SSE reconnect/resume with last-event-id.
- Add correlation ID injection in middleware and propagate to backend/agent logs.
- Add error tracking and performance monitoring (Sentry/Web Vitals).
- Add a "No Dead UI" gate: static scan + Playwright click-all.

## C) Settings Redesign Spec (World-class, deduped)

Core sections (all persisted server-side):
1) AI Provider
   - Provider selection, model, fallback, latency test.
   - Health check: /health (agent) with latency + model metadata.
2) Email Integration (P0)
   - OAuth connect (Gmail/Outlook) or IMAP/SMTP.
   - Sync status, last sync time, error log.
   - Test connection button.
3) Agent Configuration
   - Tool toggles, confidence thresholds, auto-approve rules.
4) Buy Box Criteria
   - Geographic, industry, size, broker, pricing filters.
5) Notifications
   - Email/webhook alerts for quarantine, stage transitions, action failures.
6) Data & Privacy
   - Retention policy (actions, deals), export, deletion request.
7) Appearance & Timezone
   - Theme toggle, timezone preference, date formatting.
8) Defaults
   - Default filters and saved views.

Implementation notes:
- Store settings in a `user_settings` table (encrypted at rest for secrets).
- Provide endpoints: GET/PUT /api/settings/{section}.
- Show connection history and allow re-test.

## D) Onboarding Redesign Spec (World-class, deduped)

Step 1: Welcome
- Explain value, capture company/name.

Step 2: Profile
- Persist operator name + role + company to backend.

Step 3: Connect Email
- Real OAuth or IMAP config. Validate connection and show sync status.

Step 4: Meet Your Agent (real workflow)
- Run a real test: create a sample deal and require approval.
- Show agent trace and results.

Step 5: Preferences
- Buy box criteria + notification preferences persisted.

Step 6: Complete
- Summary + links to deals, quarantine, settings.

Behavior:
- Onboarding progress persisted server-side with resume/restart.
- "Configure Email Settings" button anchors to Settings#email.
- Provide "Re-run onboarding" in Settings.

