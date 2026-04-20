# FINAL MASTER — TP-20260213-163446
## Mode: forensic
## Generated: 2026-02-13T17:10:10Z
## Sources: 3 Pass 1 reports + 3 Pass 2 cross-reviews

---

## MISSION

Produce an evidence-based forensic audit of the **Intake → Quarantine → Deals** pipeline: determine the canonical source-of-truth database, map the real-life data ingestion pipeline into Quarantine, assess the tightness of the Quarantine → approval → Deals promotion flow, identify gaps/misalignments against industry standards, and produce prioritized remediation recommendations. **No fixes implemented — investigation and reporting only.**

---

## CONSOLIDATED FINDINGS

### F-1: MCP Server Quarantine Endpoint Mismatch (`/review` vs `/process`)
**Sources:** Claude (P1-F001), Codex (P1-F5, G-002), Claude-P2-D1, Gemini-P2-U2, Codex-P2-U3
**Root Cause:** MCP server was coded against a draft endpoint name (`/review`) that was renamed to `/process` during implementation. The MCP server was never updated. MCP approve/reject calls (`server.py:311,341`) hit `/api/quarantine/{item_id}/review`, which returns 404. The backend only exposes `/api/quarantine/{item_id}/process` (`main.py:1591`).
**Fix Approach:** Change two lines in `zakops-backend/mcp_server/server.py` (lines 311 and 341): replace `/review` with `/process`. Add contract test ensuring MCP tool calls match backend OpenAPI.
**Industry Standard:** Consumer-driven contract testing between tool-layer and API. OpenAPI-generated clients prevent drift.
**System Fit:** MCP is a thin HTTP proxy to the backend; contract breakages are high-impact and trivially gated.
**Enforcement:** CI job executes MCP tool call against ephemeral backend and validates response schema + 2xx status. Add MCP endpoint paths to `make validate-fast` surface checks.
**Severity:** P0
**Evidence:**
- `zakops-backend/mcp_server/server.py:311` — `backend_post(f"/api/quarantine/{item_id}/review", data)`
- `zakops-backend/mcp_server/server.py:341` — `backend_post(f"/api/quarantine/{item_id}/review", data)`
- `zakops-backend/src/api/orchestration/main.py:1591` — `@app.post("/api/quarantine/{item_id}/process")`

---

### F-2: No Automated Email Ingestion Pipeline (Missing `email_ingestion` Module)
**Sources:** Claude (P1-F002), Gemini (P1-F1), Codex (P1-F2, G-001) — ALL THREE AGENTS
**Root Cause:** The `email_ingestion` external package is referenced via imports in 4+ backend files (`actions_runner.py:45`, `chat_orchestrator.py:45`, `main.py:1488,1491`) but is absent from all three repositories. No active polling/webhook/scheduler exists to automatically feed emails into quarantine. The bridge endpoint (`POST /api/quarantine`) exists and works, but has no automated producer.
**Fix Approach:** Build a native `EmailPoller` worker within `zakops-backend/src/workers/` that uses the existing `email_accounts` table and Gmail OAuth infrastructure. Polls inbox via `EmailService`, classifies messages, and writes through the canonical `POST /api/quarantine` endpoint with idempotent message identity.
**Industry Standard:** Event-driven inbox ingestion with cursor checkpoints, idempotent consumer semantics (`apscheduler` + `google-auth`), and explicit run ledger.
**System Fit:** The backend already has the necessary infrastructure (asyncpg, EmailService, Gmail OAuth, Pydantic models). Adding a dedicated worker is the idiomatic solution. Existing `actions_runner.py` demonstrates the worker pattern.
**Enforcement:** Integration test simulates email arrival and verifies exactly one quarantine item is created. Health endpoint exposes ingestion heartbeat and lag metric.
**Severity:** P0
**Evidence:**
- `zakops-backend/src/api/orchestration/main.py:1491` — bridge endpoint docstring references `email_ingestion pipeline`
- `zakops-backend/src/workers/actions_runner.py:45` — `from email_ingestion.run_ledger import ...` (module not found)
- `zakops-backend/src/core/chat_orchestrator.py:45` — dead import reference
- No polling/webhook implementation found in any active code path

---

### F-3: Weak / Missing Quarantine Deduplication at DB Level
**Sources:** Gemini (P1-F4), Codex (P1-F4, G-004), Claude-P2-D4
**Root Cause:** Quarantine dedup relies on app-level pre-check (`SELECT` by `message_id` before `INSERT` at `main.py:1508`). No `UNIQUE` constraint exists on `zakops.quarantine_items.message_id`. Concurrent requests can create duplicates. Additionally, forwarded emails or replies in the same thread have new `message_id` values, so content-hash based dedup is also needed for thread-level idempotency.
**Fix Approach:** Add DB-level unique index on `quarantine_items.message_id` (or `message_id + source` composite). Implement content-hash dedup for thread-variant detection. Use `ON CONFLICT` / upsert semantics in the INSERT path.
**Industry Standard:** Idempotency as a data invariant, not best-effort middleware. DB uniqueness constraints + application-level content hashing.
**System Fit:** `email_messages` table already HAS a unique constraint on `message_id` (`022_email_integration.sql:73`); quarantine_items is simply missing it. Aligning them brings parity.
**Enforcement:** Migration adds unique index. Concurrency regression suite (`N` parallel POSTs with same `message_id`) must produce one row and cached responses.
**Severity:** P0
**Evidence:**
- `zakops-backend/db/init/001_base_tables.sql:217` — `message_id VARCHAR(500)` with NO UNIQUE constraint
- `zakops-backend/src/api/orchestration/main.py:1508` — app-level dedupe SELECT
- `zakops-backend/db/migrations/022_email_integration.sql:73` — `email_messages` HAS unique constraint (quarantine missing it)

---

### F-4: Agent API Database URL Config Drift
**Sources:** Codex (P1-F1, G-008), Claude (P1-checklist, P2-D8)
**Root Cause:** Agent `.env.example` specifies `zakops_agent` DB (correct per topology contract), but the deployment `docker-compose.yml` sets `DATABASE_URL` to `zakops` (the backend DB). The runtime topology contract (`runtime.topology.json:20`) expects `zakops_agent`. This creates a configuration-level split-brain risk where the agent could read/write to the wrong database in production.
**Fix Approach:** Fix `deployments/docker/docker-compose.yml:17` to point to `zakops_agent`. Add startup gate in agent API to reject `DATABASE_URL` where dbname != `zakops_agent`. Add CI policy test comparing compose/env/topology contract values.
**Industry Standard:** Explicit bounded-context data ownership with environment contract validation at startup and CI.
**System Fit:** This architecture intentionally separates backend deal truth (`zakops`) and agent operational state (`zakops_agent`); config drift is the primary failure mode, not architectural deficiency.
**Enforcement:** Agent API startup assertion: `DATABASE_URL` dbname must equal `zakops_agent`. CI gate compares all env source files against topology contract.
**Severity:** P0
**Evidence:**
- `zakops-agent-api/apps/agent-api/.env.example:47` — `zakops_agent`
- `zakops-agent-api/deployments/docker/docker-compose.yml:17` — `zakops` (CONFLICT)
- `zakops-agent-api/packages/contracts/runtime.topology.json:20` — expects `zakops_agent`

---

### F-5: Legacy Filesystem `.deal-registry` Still in Active Code Paths (Shadow Truth)
**Sources:** Claude (P1-F003), Codex (P1-F8, G-009), Claude-P2-D7, Codex-P2-U6
**Root Cause:** Backend workers, action executors, memory store, and Zaks-llm APIs all reference `.deal-registry` filesystem paths as data sources for deals and quarantine. The dual-write adapter (`DUAL_WRITE_ENABLED=false`) is inactive but present. SQLite state DB paths are hardcoded. Critically, `Zaks-llm/src/api/server.py:701` serves a `/api/deals` endpoint reading from `.deal-registry` — if any client calls this instead of the canonical backend, it gets stale filesystem data.
**Fix Approach:** Phase 1 (P0): Remove/disable Zaks-llm deal/quarantine CRUD endpoints that read from `.deal-registry`. Phase 2 (P1): Fully deprecate all filesystem deal/quarantine state paths in backend workers/executors. Remove dual-write adapter. Phase 3: Block `.deal-registry` access in production paths via CI grep gate.
**Industry Standard:** One authoritative operational datastore per aggregate. Decommission alternative data sources with CI-enforced gates.
**System Fit:** Backend already enforces canonical DB ownership at startup (`main.py:372-405`). The filesystem paths are legacy artifacts from a pre-DB era.
**Enforcement:** CI grep gate: `rg ".deal-registry" --type py` must return zero matches in production paths. Startup assertion logs warning if `.deal-registry` directory exists.
**Severity:** P0 (Zaks-llm shadow endpoints) / P1 (inactive dual-write adapter)
**Evidence:**
- `zakops-backend/src/workers/actions_runner.py:53` — `DATAROOM_ROOT` / `.deal-registry`
- `zakops-backend/src/actions/memory/store.py:15` — SQLite path under `.deal-registry`
- `zakops-backend/src/core/database/adapter.py:56,63` — dual-write config
- `Zaks-llm/src/api/server.py:701` — deals CRUD from `.deal-registry`
- `Zaks-llm/src/api/server.py:794` — quarantine from `.deal-registry`

---

### F-6: Quarantine Approval Bypasses Workflow Engine / FSM / Outbox
**Sources:** Claude (P1-F005), Codex (P1-F3, G-003), Claude-P2-D3, Codex-P2-U8
**Root Cause:** Quarantine approval performs a raw `INSERT INTO zakops.deals` (`main.py:1648`) and records only a `deal_created` event (`main.py:1675`), bypassing `transition_deal_state()` in `DealWorkflowEngine` which writes to `deal_transitions` ledger and `outbox` (`workflow.py:227-277`). The `enforce_deal_lifecycle` DB trigger does fire on INSERT (providing baseline constraint enforcement via `025_deal_lifecycle_fsm.sql`), so the core constraint is partially met — but downstream consumers expecting outbox events will not be notified.
**Fix Approach:** Route quarantine promotion through a single domain service that creates the deal via the workflow engine, or call `transition_deal_state()` after the INSERT to emit the transition ledger entry and outbox event.
**Industry Standard:** "One write path per aggregate" + transactional outbox for side effects. All deal creation paths should emit identical lifecycle artifacts.
**System Fit:** Workflow engine and outbox primitives already exist. The current bypass is the sole inconsistency source.
**Enforcement:** Contract test: approving quarantine must produce expected rows in `deals`, `deal_events`, `deal_transitions`, and `outbox` tables.
**Severity:** P1
**Evidence:**
- `zakops-backend/src/api/orchestration/main.py:1648` — raw INSERT bypassing workflow
- `zakops-backend/src/api/orchestration/main.py:1675` — only `deal_created` event
- `zakops-backend/src/core/deals/workflow.py:227-277` — full FSM path with ledger + outbox

---

### F-7: Dashboard Email Settings Proxy Targets Nonexistent Backend Endpoint
**Sources:** Claude (P1-F006), Codex (P1-F6, G-006), Claude-P2-D5, Codex-P2-U4
**Root Cause:** Dashboard route proxies to `/api/user/email-config` (`route.ts:12`), but this endpoint does not exist in the backend. The test route proxies to `/api/user/email-config/test` (`test/route.ts:10`) — also nonexistent. The onboarding email step (`EmailSetupStep.tsx:56,60`) simulates OAuth with a 2-second delay and mock email instead of calling real backend OAuth endpoints at `/api/integrations/email/auth/gmail`.
**Fix Approach:** Wire onboarding to real Gmail OAuth endpoints (`/api/integrations/email/auth/gmail`). Either implement `/api/user/email-config` in the backend or redirect the dashboard proxy to the existing email integration endpoints. Remove or feature-flag dead routes.
**Industry Standard:** Configuration UX must be backed by the same control-plane APIs used in production. API-first UI with generated clients from live OpenAPI.
**System Fit:** Dashboard already has an API proxy layer and generated types; the wiring just needs to point to real endpoints.
**Enforcement:** E2E test: connect Gmail → account appears in `/api/integrations/email/accounts` → ingestion readiness check green. Playwright test for email onboarding flow.
**Severity:** P1
**Evidence:**
- `zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts:12` — proxy to `/api/user/email-config`
- `zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:56-60` — simulated OAuth
- No backend route for `/api/user/email-config` found in any search

---

### F-8: Correlation ID Not Propagated End-to-End
**Sources:** Claude (P1-F007), Gemini (P1-F2), Codex (P1-F9, G-010), Claude-P2-D6
**Root Cause:** Multiple correlation ID generators exist across layers. Dashboard middleware (`middleware.ts:50`) and API client (`api.ts:378`) both independently generate correlation IDs. Backend runs TWO tracing middlewares (`TraceMiddleware` at `main.py:451` and `TracingMiddleware` at `main.py:457`) with differing behavior (`trace.py:91` vs `tracing.py:56`), causing possible correlation churn. Additionally, `zakops.quarantine_items` table lacks a `correlation_id` column entirely, breaking traceability at the ingestion boundary.
**Fix Approach:** Define single correlation source at edge (dashboard middleware), propagate through all layers to DB events. Add `correlation_id UUID` column to `quarantine_items`. Unify the two backend tracing middlewares into one. Ensure `X-Correlation-ID` header is respected and persisted.
**Industry Standard:** W3C Trace Context + stable business correlation ID. OpenTelemetry distributed tracing.
**System Fit:** Headers and correlation columns already exist in `deal_events` (`024_correlation_id.sql:6`); needs consistency and coverage extension to quarantine and middleware layers.
**Enforcement:** Request-trace contract test verifies same correlation ID in response headers, logs, and `deal_events.correlation_id`. Dashboard alert thresholds for queue lag/failure rates.
**Severity:** P1
**Evidence:**
- `zakops-agent-api/apps/dashboard/src/middleware.ts:50` — generates correlation ID
- `zakops-agent-api/apps/dashboard/src/lib/api.ts:378` — API client generates correlation ID
- `zakops-backend/src/api/shared/middleware/trace.py:91` vs `tracing.py:56` — dual middleware
- `zakops-backend/db/init/001_base_tables.sql:210-236` — quarantine_items has no `correlation_id`

---

### F-9: Idempotency Middleware Schema-Qualification Bug + Silent Bypass
**Sources:** Codex (P1-F4, G-005), Claude-P2-U4
**Root Cause:** Idempotency middleware queries `FROM idempotency_keys` (unqualified, `idempotency.py:85`) while the table is created as `zakops.idempotency_keys` (`001_foundation_tables.sql:114`). If `search_path` doesn't include `zakops`, the query fails. On DB error, middleware bypasses idempotency entirely (`idempotency.py:147`), silently degrading to non-idempotent behavior. Additionally, agent sends note idempotency key in body (`backend_client.py:307`) but the note schema lacks the field (`main.py:855`).
**Fix Approach:** Schema-qualify all idempotency queries to `zakops.idempotency_keys`. Change error-bypass behavior to fail-closed (reject request on idempotency check failure rather than silently proceeding).
**Industry Standard:** Idempotency as a hard data invariant with fail-closed semantics. Schema-qualified queries in multi-schema databases.
**System Fit:** The middleware structure is correct; the implementation has two specific bugs (unqualified table name, silent bypass).
**Enforcement:** Unit test: idempotency middleware must fail-closed on DB error. Integration test: duplicate POST with same idempotency key returns cached response.
**Severity:** P1
**Evidence:**
- `zakops-backend/src/api/shared/middleware/idempotency.py:85` — unqualified `FROM idempotency_keys`
- `zakops-backend/src/api/shared/middleware/idempotency.py:127` — write also unqualified
- `zakops-backend/src/api/shared/middleware/idempotency.py:147` — DB error bypass
- `zakops-backend/db/migrations/001_foundation_tables.sql:114` — table created as `zakops.idempotency_keys`

---

### F-10: Dashboard `bulk-delete` Quarantine Endpoint Not Implemented
**Sources:** Codex (P1-F7, G-007), Claude-P2-U5
**Root Cause:** Frontend client calls `/api/quarantine/bulk-delete` (`api.ts:942`), but no such route exists in either the dashboard API routes or the backend. Dashboard quarantine API only implements `[id]/process`, `[id]/delete`, and `health`. This results in a hidden 404 when users attempt bulk operations.
**Fix Approach:** Either implement bulk-delete end-to-end (dashboard route → backend route → DB operation) or remove/feature-flag the client-side call. If implementing, follow the existing per-item delete pattern (soft-hide with `status='hidden'`).
**Industry Standard:** Typed API client generated from live OpenAPI, no orphan endpoints. Every client endpoint must map to a server route.
**System Fit:** Dashboard already has the proxy pattern and backend has per-item delete; bulk is an extension.
**Enforcement:** Route existence lint: every client API call must have a matching server route. CI gate validates no orphan client calls.
**Severity:** P1
**Evidence:**
- `zakops-agent-api/apps/dashboard/src/lib/api.ts:942` — calls `/api/quarantine/bulk-delete`
- Dashboard API routes: only `[id]/process`, `[id]/delete`, `health` exist

---

### F-11: Missing DB Constraint on Quarantine `status` Column
**Sources:** Gemini (P1-F3), Claude-P2-U3
**Root Cause:** The `status` column in `zakops.quarantine_items` is a plain `VARCHAR(50)` without a `CHECK` constraint (`001_base_tables.sql:228`). While the application validates via Pydantic, the database layer allows arbitrary string values, violating defense-in-depth.
**Fix Approach:** Add migration: `ALTER TABLE zakops.quarantine_items ADD CONSTRAINT chk_quarantine_status CHECK (status IN ('pending', 'approved', 'rejected', 'hidden'))`.
**Industry Standard:** Database-level integrity constraints (Defense in Depth). Other tables in this schema already use CHECK constraints and enums.
**System Fit:** Brings quarantine table to parity with `deals` and `actions` tables which already have constraints.
**Enforcement:** Database migration validation script. Schema drift detection in CI.
**Severity:** P2
**Evidence:**
- `zakops-backend/db/init/001_base_tables.sql:228` — `status VARCHAR(50)` with no CHECK constraint
- `zakops-backend/db/migrations/023_stage_check_constraint.sql` — deals table HAS check constraint (quarantine missing it)

---

### F-12: DDL Default Stage `'lead'` Not in Canonical Stage Enum
**Sources:** Claude (P1-F008), Claude-P2-U2
**Root Cause:** `zakops-backend/db/init/001_base_tables.sql:36` shows `DEFAULT 'lead'` for the deals table stage column, but `DealStage` enum (`workflow.py:40-50`) has no `lead` stage. Migration `023_stage_check_constraint.sql` enforces canonical stages that do NOT include `lead`. If any code path creates a deal without explicitly setting stage, the INSERT would violate the CHECK constraint.
**Fix Approach:** Change DDL default from `'lead'` to `'inbound'` (the canonical initial stage) or add `'lead'` to the stage enum if it's a valid business concept.
**Industry Standard:** DDL defaults must be valid values within their constraints. Schema validation at migration time.
**System Fit:** The quarantine approval path explicitly sets `stage='inbound'`, so this is a latent bug — it only fires if a deal is created through a path that doesn't set stage.
**Enforcement:** Migration that updates the DEFAULT value. Schema consistency test.
**Severity:** P2
**Evidence:**
- `zakops-backend/db/init/001_base_tables.sql:36` — `DEFAULT 'lead'`
- `zakops-backend/src/core/deals/workflow.py:40-50` — no `lead` in `DealStage` enum
- `zakops-backend/db/migrations/023_stage_check_constraint.sql` — CHECK constraint excludes `lead`

---

### F-13: Retention Cleanup References Non-Existent Quarantine Columns
**Sources:** Codex (P1-Adjacent), Claude-P2-U6 (verified as real bug)
**Root Cause:** `zakops-backend/src/core/retention/cleanup.py:299` attempts to UPDATE `processed_by` and `processing_action` columns on `zakops.quarantine_items`. These columns do NOT exist in the table schema (`001_base_tables.sql:210-236`). No migration adds them. This will cause a runtime SQL error when retention cleanup encounters stale pending quarantine items.
**Fix Approach:** Either add the missing columns via migration, or change the retention cleanup to update the existing `raw_content` JSON field with processed_by/action metadata (matching the pattern used in the approval flow at `main.py:1695`).
**Industry Standard:** Schema evolution must keep application code and DB schema in sync. Migration tests validate all SQL queries against the actual schema.
**System Fit:** The approval flow already uses `raw_content` JSON for this metadata; retention cleanup should follow the same pattern.
**Enforcement:** SQL query validation test: all queries in retention cleanup must run without error against current schema.
**Severity:** P1 (runtime bug, will fail on execution)
**Evidence:**
- `zakops-backend/src/core/retention/cleanup.py:299` — UPDATE `processed_by`, `processing_action`
- `zakops-backend/db/init/001_base_tables.sql:210-236` — columns absent from schema
- `zakops-backend/src/api/orchestration/main.py:1695` — approval flow uses `raw_content` JSON instead

---

### F-14: Agent Duplicates Transition Matrix (Two Sources of Truth)
**Sources:** Claude (P1-Checklist R4-2), Claude-P2-U7
**Root Cause:** `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:83-95` contains `VALID_TRANSITIONS` that mirrors `STAGE_TRANSITIONS` in `zakops-backend/src/core/deals/workflow.py:54-64`. Two sources of truth for the same state machine logic. Changes to the canonical transition matrix must be manually duplicated.
**Fix Approach:** Remove the agent-side duplicate and validate transitions exclusively via the backend API (which the agent already calls for deal operations). Or generate the agent-side copy from the backend spec via `make sync-agent-types`.
**Industry Standard:** Single source of truth for business rules. Generated/synced copies with drift detection.
**System Fit:** Agent already validates via backend API, so the local copy is advisory. Risk is limited to misleading error messages.
**Enforcement:** Contract drift test comparing agent `VALID_TRANSITIONS` against backend `STAGE_TRANSITIONS`.
**Severity:** P2
**Evidence:**
- `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:83-95` — `VALID_TRANSITIONS`
- `zakops-backend/src/core/deals/workflow.py:54-64` — canonical `STAGE_TRANSITIONS`

---

### F-15: Mismatched Stage Taxonomy in Agent Contract Docstring
**Sources:** Codex (P1-Adjacent), Claude-P2-U8
**Root Cause:** `zakops-backend/src/agent/bridge/agent_contract.py:249` documents `Won/Lost/Passed` as terminal stages. The canonical enum uses `portfolio/junk/archived`. This is a documentation-only mismatch (docstring, not code logic), but could mislead an LLM/agent if used as context for deal stage reasoning.
**Fix Approach:** Update the docstring to reference the canonical stage names.
**Industry Standard:** Documentation must match runtime behavior. Automated doc linting against source of truth.
**System Fit:** Low risk since agent validates via API, but stale docstrings create confusion for LLM-based tools.
**Enforcement:** Grep gate for legacy stage names in documentation/contract files.
**Severity:** P3
**Evidence:**
- `zakops-backend/src/agent/bridge/agent_contract.py:249` — `Won/Lost/Passed`
- `zakops-backend/src/core/deals/workflow.py:40-50` — canonical stages (`portfolio/junk/archived`)

---

### F-16: Attachment Linkage Gap Post-Promotion
**Sources:** Codex (P1-Checklist Q14), Claude-P2-U10
**Root Cause:** Gmail parser extracts attachment metadata in-memory. Backfill executor downloads attachments to filesystem quarantine directory. However, the quarantine promotion flow does NOT automatically create `email_threads` or `email_attachments` links from quarantine item to the newly promoted deal. Attachments referenced in quarantine items have no guaranteed linkage after promotion.
**Fix Approach:** Add attachment/thread linking step to the quarantine approval flow. When creating a deal from quarantine, also link any associated email thread and attachments via the existing `email_threads` link API.
**Industry Standard:** Referential integrity across promotion lifecycle. All associated artifacts must be re-linked atomically.
**System Fit:** Email thread linking APIs already exist (`email.py:436`, `service.py:373`); the approval flow just needs to call them.
**Enforcement:** Contract test: approving a quarantine item with `message_id` that has attachments must produce `email_attachments` rows linked to the new deal.
**Severity:** P2
**Evidence:**
- `zakops-backend/src/core/integrations/email/gmail.py:392` — attachment metadata extraction
- `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1009` — filesystem attachment download
- `zakops-backend/src/api/orchestration/main.py:1648` — promotion flow lacks attachment linking

---

### F-17: OAuth State Stored In-Memory (Scalability Risk)
**Sources:** Claude (P1-F004), Claude-P2-U1
**Root Cause:** `OAuthStateStore` at `zakops-backend/src/api/orchestration/routers/email.py:31-54` uses a Python `dict` with 5-minute TTL. Comment at line 52 acknowledges it's not suitable for multi-instance deployment.
**Fix Approach:** Move OAuth state to the database or Redis when scaling to multi-instance. For current single-instance deployment, the in-memory store is functional.
**Industry Standard:** Distributed cache (Redis) or DB-backed state for OAuth CSRF tokens in multi-instance deployments.
**System Fit:** Currently single-instance, so this is a latent issue. Will become critical if horizontally scaled.
**Enforcement:** Architecture decision record (ADR) documenting the constraint. Pre-scaling checklist item.
**Severity:** P3
**Evidence:**
- `zakops-backend/src/api/orchestration/routers/email.py:31-54` — in-memory `OAuthStateStore`

---

## DISCARDED ITEMS

### DISC-1: Outlook Email Provider Stub (from Claude, Gap G-10)
**Reason for exclusion:** The absence of Outlook support is a known future feature, not a pipeline integrity issue. Gmail integration exists and is the active provider. Out of scope for this Intake → Quarantine → Deals audit.

### DISC-2: Deal Origination Email Outreach Stub (from Claude, Gap G-11)
**Reason for exclusion:** Outbound email outreach is a separate pipeline from inbound Intake → Quarantine → Deals. Out of scope.

### DISC-3: Runtime Ports Closed Finding (from Codex, Finding 10)
**Reason for exclusion:** This is an execution-environment constraint for this audit run (services were down), not a stable architectural defect. It affects audit confidence but is not a product bug.

### DISC-4: SSE Implementation Status "Conflict" (from Codex, Adjacent)
**Reason for exclusion:** Cross-review (Claude-P2-C3) confirmed both claims are accurate and NOT contradictory. The `/stream` endpoint explicitly returns 501 "not yet implemented." The health check accurately reports this. No real conflict exists.

---

## DRIFT LOG

Items flagged by cross-reviews as out-of-scope for the Intake → Quarantine → Deals pipeline mission.

### DRIFT-1: OAuth State Storage Architecture
**Source:** Claude P1-F004
**Why out of scope:** OAuth state management is email integration infrastructure, not directly part of the Intake → Quarantine → Deals data flow. The quarantine pipeline works regardless of how OAuth state is stored.
**Included as:** F-17 (lowest priority, P3) for completeness since it affects ingestion scalability.

### DRIFT-2: Outlook Provider Stub
**Source:** Claude P1-Gap G-10
**Why out of scope:** Feature gap, not pipeline integrity issue. No current pipeline risk.

### DRIFT-3: Deal Origination Email Outreach
**Source:** Claude P1-Gap G-11
**Why out of scope:** Outbound email is a different pipeline than inbound ingestion.

### DRIFT-4: Pass 1 CLAUDE Report Completeness
**Source:** Codex P2 observation
**Note:** Claude's Pass 1 report was a status acknowledgment rather than a full forensic report. However, the forensic content was captured in the existing `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md` and evidence index files, and the Claude Pass 2 cross-review was the most comprehensive of all three cross-reviews. Impact on final consolidation: none — all findings are fully attributed and verified.

### DRIFT-5: GEMINI Report Truncation
**Source:** Codex P2 observation
**Note:** Gemini's Finding 4 was truncated mid-content (deduplication finding). The finding was still identifiable and corroborated by Codex's independent Finding 4. Impact on final consolidation: none — finding captured as F-3.

---

## ACCEPTANCE GATES

Builder-enforceable gates for implementing the findings above.

### Gate 1: MCP Contract Alignment (F-1)
**Command:** `python -c "import ast; s=open('zakops-backend/mcp_server/server.py').read(); assert '/review' not in s, 'MCP still references /review endpoint'"`
**Pass criteria:** No occurrences of `/review` in MCP server quarantine paths. MCP approve/reject calls return 2xx from backend.

### Gate 2: Ingestion Worker Exists and Functions (F-2)
**Command:** `test -f zakops-backend/src/workers/email_poller.py && python -c "from workers.email_poller import EmailPoller"`
**Pass criteria:** EmailPoller class exists, is importable, and integration test passes (creates quarantine item from synthetic email payload).

### Gate 3: Quarantine Dedup DB Constraint (F-3)
**Command:** `psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -c "\d zakops.quarantine_items" | grep -i "unique.*message_id"`
**Pass criteria:** UNIQUE constraint exists on `message_id` column. Concurrent POST test with same `message_id` produces exactly one row.

### Gate 4: Agent DB Config Consistency (F-4)
**Command:** `grep -E "DATABASE_URL.*zakops[^_]" zakops-agent-api/deployments/docker/docker-compose.yml; echo "EXIT:$?"`
**Pass criteria:** Exit code 1 (no match). All agent config files reference `zakops_agent`, not `zakops`.

### Gate 5: Legacy Filesystem Paths Removed (F-5)
**Command:** `rg ".deal-registry" --type py zakops-backend/src/ Zaks-llm/src/ | grep -v "test" | grep -v "#"`
**Pass criteria:** Zero matches in non-test production code.

### Gate 6: Promotion Through Workflow Engine (F-6)
**Command:** `psql -c "SELECT COUNT(*) FROM zakops.deal_transitions WHERE deal_id = (SELECT deal_id FROM zakops.quarantine_items WHERE status='approved' ORDER BY updated_at DESC LIMIT 1)"`
**Pass criteria:** Count >= 1. Approved quarantine items produce transition ledger entries.

### Gate 7: Email Settings Wired (F-7)
**Command:** `curl -sS http://localhost:3003/api/settings/email -o /dev/null -w '%{http_code}'`
**Pass criteria:** Returns 200 (not 404/502). Onboarding flow hits real OAuth endpoints.

### Gate 8: Correlation ID Consistency (F-8)
**Command:** `psql -c "SELECT correlation_id FROM zakops.quarantine_items ORDER BY created_at DESC LIMIT 1"` (column must exist and be non-null)
**Pass criteria:** `correlation_id` column exists in quarantine_items. End-to-end test shows same ID in response header and DB record.

### Gate 9: Idempotency Schema Fix (F-9)
**Command:** `grep -c "zakops.idempotency_keys" zakops-backend/src/api/shared/middleware/idempotency.py`
**Pass criteria:** All references are schema-qualified. No unqualified `idempotency_keys` queries remain.

### Gate 10: Bulk-Delete Route Alignment (F-10)
**Command:** `curl -sS -X POST http://localhost:3003/api/quarantine/bulk-delete -H 'Content-Type: application/json' -d '{"ids":[]}' -o /dev/null -w '%{http_code}'`
**Pass criteria:** Returns 200/204 (not 404). Or: client code no longer calls the endpoint (grep returns zero matches for `bulk-delete` in `api.ts`).

### Gate 11: Quarantine Status Constraint (F-11)
**Command:** `psql -c "\d zakops.quarantine_items" | grep -i "chk_quarantine_status"`
**Pass criteria:** CHECK constraint exists on `status` column.

### Gate 12: DDL Default Stage Fix (F-12)
**Command:** `grep "DEFAULT" zakops-backend/db/init/001_base_tables.sql | grep "stage" | grep -v "lead"`
**Pass criteria:** Default stage value is a valid canonical stage (e.g., `'inbound'`).

### Gate 13: Retention Cleanup Fix (F-13)
**Command:** `python -c "import re; s=open('zakops-backend/src/core/retention/cleanup.py').read(); assert 'processed_by' not in s or 'raw_content' in s.split('processed_by')[0][-200:]"`
**Pass criteria:** Retention cleanup either uses `raw_content` JSON pattern or references columns that exist in the schema.

### Gate 14: Transition Matrix Sync (F-14)
**Command:** `make validate-agent-config 2>&1 | grep -i "transition"`
**Pass criteria:** Agent transitions match backend transitions, or agent-side copy is removed.

---

## STATISTICS

| Metric | Count |
|--------|-------|
| Total Pass 1 findings across all agents | 24 primary + 9 adjacent + 22 gap items |
| Deduplicated primary findings (F-1 through F-17) | 17 |
| Discarded (with reason) | 4 (DISC-1 through DISC-4) |
| Drift items | 5 (DRIFT-1 through DRIFT-5) |
| **Drop rate** | **0%** (all findings accounted for) |

### Severity Distribution

| Severity | Findings | IDs |
|----------|----------|-----|
| P0 (Must Fix) | 5 | F-1, F-2, F-3, F-4, F-5 |
| P1 (Should Fix) | 6 | F-6, F-7, F-8, F-9, F-10, F-13 |
| P2 (Improve) | 4 | F-11, F-12, F-14, F-16 |
| P3 (Low Priority) | 2 | F-15, F-17 |

### Agent Contribution Summary

| Agent | P1 Findings | P2 Cross-Review Quality | Novel Contributions |
|-------|-------------|------------------------|---------------------|
| CLAUDE | 8 primary + 12 gaps | Most comprehensive review (8 dupes, 3 conflicts, 9 unique) | OAuth state, DDL default, transition matrix |
| GEMINI | 4 primary + 3 adjacent | Focused review, confirmed Codex findings | Quarantine status constraint, content-hash dedup |
| CODEX | 10 primary + 3 adjacent | Thorough review (3 dupes, 3 conflicts, 9 unique) | MCP contract, config drift, FSM bypass, idempotency bug, bulk-delete, retention bug |

### Evidence Quality

All file:line references cited by all three agents were independently verified during Pass 2 cross-reviews. **Every cited evidence reference was confirmed accurate.** One additional bug (F-13: retention cleanup column mismatch) was discovered during cross-review verification.

---

*End of FINAL_MASTER — TP-20260213-163446*
*Consolidation Agent: CLAUDE (Consolidator)*
*Pipeline: TriPass forensic mode*
