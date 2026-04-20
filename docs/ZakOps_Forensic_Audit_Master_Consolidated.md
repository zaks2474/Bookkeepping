# ZakOps Forensic Audit — Master Consolidated Remediation (Report A + Report B)

**Date:** 2026-02-01  
**Version:** 1.0  
**Role:** Forensic Audit Consolidator & Remediation PM

**Inputs**
- **Report A (Codex audit):** `/home/zaks/bookkeepping/doc/codex_ZakOps_Forensic_Audit_2026-02-01.md`
- **Report B (Claude Code audit):** `/home/zaks/bookkeeping/docs/CLAUDE_CODE_FORENSIC_AUDIT_20260201.md`

**No-invention pledge:** All evidence/quotes are taken verbatim from the two reports. Any additional reasoning is explicitly labeled as a hypothesis and/or marked **NEEDS VERIFICATION**.

---

## Executive Summary

### What’s broken (high-level)
- **Port + environment configuration drift** across `8090/8091/9200` prevents a deterministic runtime and causes clients/tools to call the wrong service. (`ZK-AUD-0002`)
- **Core business pipeline gap:** inbound email/files do not reliably produce `quarantine_items` in Postgres; quarantine approval and action execution are not end-to-end wired. (`ZK-AUD-0010`, `ZK-AUD-0011`, `ZK-AUD-0012`)
- **Approvals/runs UX is not consistently end-to-end** due to a broken `/api/threads/*` backend path and missing DB schema/migrations in at least one path. (`ZK-AUD-0006`, `ZK-AUD-0007`, `ZK-AUD-0016`)
- **Dashboard can look “healthy” while services are down** because of mock endpoints and “fail open” routes that return empty/mock data. (`ZK-AUD-0003`)
- **Security posture is dev-friendly but production-risky:** auth disabled by default, hardcoded service token, placeholder/empty secrets. (`ZK-AUD-0017`, `ZK-AUD-0018`, `ZK-AUD-0009`)

### Top priorities (execute in order)
**P0**
1. Fix port conflicts & drift so the stack can run deterministically. (`ZK-AUD-0002`)
2. Unify DB configuration (eliminate wrong defaults & multi-DB ambiguity). (`ZK-AUD-0016`)
3. Close the Email/DataRoom → Quarantine → Deal bridge. (`ZK-AUD-0010`)
4. Make quarantine approve/reject + execution contract consistent end-to-end. (`ZK-AUD-0011`)
5. Make actions/outbox worker actually run and process work. (`ZK-AUD-0012`)
6. Fix broken approvals/runs wiring (`/api/threads`) or remove it and wire to the correct approvals system. (`ZK-AUD-0006`)

**P1**
- Fix backend search crashes. (`ZK-AUD-0008`)
- Stabilize LLM/integration configuration and required secrets. (`ZK-AUD-0009`)
- Apply/automate approvals DB functions if required. (`ZK-AUD-0007`)
- Resolve dual-platform ambiguity and decommission legacy services. (`ZK-AUD-0001`)

**P2/P3**
- Remove “demo mode” illusions and add explicit health indicators. (`ZK-AUD-0003`)
- Normalize stage taxonomy and transition contracts. (`ZK-AUD-0004`, `ZK-AUD-0005`)
- Improve observability and validate gates/CI/chaos/blue-green reality. (`ZK-AUD-0019`, `ZK-AUD-0020`)

---

## Master Findings Register

### ZK-AUD-0001 — Multiple competing ZakOps stacks / unclear source of truth

- **Category:** `legacy_decommission`
- **Risk/Severity:** **P1** — Blast radius: **system-wide**
- **Owner Type:** `devops`
- **Finding Signature:** `competing-stacks-source-of-truth`

**Description**  
Both audits indicate overlapping “ZakOps” stacks and backend-ish codepaths, creating ambiguity about which service is authoritative for deals, email ingestion, quarantine, actions, and tool execution.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > **Key contrarian fact:** you have *multiple* “backend-ish” codepaths in-repo, but the only backend actually serving `:8091` is `zakops-backend/`.
- **Mentioned in Report B?** yes  
  > There are **two separate "ZakOps" systems** running simultaneously:

**Evidence (reports-only)**
- Report A enumerates an observed backend on `http://localhost:8091` built from `zakops-backend/`, and notes `zakops-agent-api/apps/backend/` exists but is not serving `:8091`.
- Report B cites a legacy `/home/zaks/Zaks-llm/` stack with a `zakops-api` on port `8080`.

**Root Cause Hypothesis (hypothesis)**  
Legacy and newer stacks were run in parallel to keep critical workflows alive (email/DataRoom), but the cutover/decommission plan was not completed and documentation drifted.

**Remediation Actions**
1. Decide the single authoritative “ZakOps runtime” (which API owns deals/quarantine/actions) and publish it in an operator runbook.
2. Decommission, disable, or explicitly scope legacy services (e.g., legacy `zakops-api:8080`) so operators/devs know whether it is required.
3. Remove or clearly label misleading “backend-looking” directories that are not in use (`zakops-agent-api/apps/backend/` per Report A).
4. Update scripts/docs to reference only the authoritative ports/services (see `ZK-AUD-0002`).

**Dependencies**
- `ZK-AUD-0002` (ports/URLs must be coherent before decommission decisions are safe)
- `ZK-AUD-0016` (DB strategy is part of “source of truth”)

**Verification Plan**
- Run `docker ps` and confirm only the intended stack(s) are running.
- Run `ss -lntp` and confirm only expected ports are listening for the chosen runtime.
- Confirm dashboard/agent tool base URLs target the selected authoritative backend(s).

**Definition of Done**
- One declared authoritative API for deals/quarantine/actions; others are stopped or formally documented as “legacy/bridge”.
- Onboarding documentation points to exactly one runtime topology.

---

### ZK-AUD-0002 — Port & URL configuration drift (8090/8091/9200) + docker-compose conflicts

- **Category:** `env_config`
- **Risk/Severity:** **P0** — Blast radius: **system-wide**
- **Owner Type:** `devops`
- **Finding Signature:** `port-url-config-drift`

**Description**  
Both reports describe inconsistent ports across env files, Docker defaults, docs, and clients; additionally, docker-compose port mappings conflict such that orchestration and deal-lifecycle cannot coexist cleanly.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Port **8090** is still referenced widely in docs/scripts/config despite V3 claiming it’s decommissioned.
- **Mentioned in Report B?** yes  
  > **Port conflict: both backend services claim 8091**

**Evidence (reports-only)**
- Report B: `backend-orchestration` is mapped to `8091:8091` (same as deal-lifecycle), not `9200:9200`, preventing running both from compose.
- Report B: `.env.example` says `DEAL_LIFECYCLE_API_PORT=8090`, `Dockerfile.api` defaults to `8090`, while compose maps `8091:8091`.
- Report B: dashboard `agent-client.ts` defaults to port `9200` if `NEXT_PUBLIC_API_URL` is missing.
- Report A: legacy MCP server file remains hard-coded to `:8090`: `zakops-backend/src/agent/bridge/mcp_server.py`.
- Report A: `8090` still appears in `zakops-backend/.env.example`, container env (`ZAKOPS_DEAL_API_URL`), and docs/tools.

**Root Cause Hypothesis (hypothesis)**  
Port changes were made during V2→V3 evolution and partial decommissioning, but defaults, examples, and client fallbacks were not updated consistently across repos and services.

**Remediation Actions**
1. **Fix docker-compose port mappings** so both backend services can run without collisions (Report B calls this out explicitly):  
   - Update `deployments/docker/docker-compose.yml` to map orchestration to `9200:9200` (or chosen port) and deal-lifecycle to `8091:8091`.
2. **Normalize all defaults/examples** to a single port set:
   - Update `.env.example` entries that still advertise `8090` (`apps/backend/.env.example` per Report B; `zakops-backend/.env.example` per Report A).
   - Update `Dockerfile.api` default port (Report B) to match runtime.
   - Update scripts that assume different defaults (`scripts/dev.sh` per Report B).
3. **Fix dashboard client fallbacks**:
   - Update `apps/dashboard/src/lib/agent-client.ts` default port (Report B: defaults to `9200`) to match the selected authoritative backend API.
4. **Remove/cordon legacy 8090 references**:
   - Replace or remove hard-coded `:8090` in `zakops-backend/src/agent/bridge/mcp_server.py` (Report A), and any env like `ZAKOPS_DEAL_API_URL` that points to 8090 (Report A).
5. Update documentation to reflect the final port map (ties into `ZK-AUD-0001`).

**Dependencies**
- `ZK-AUD-0001` (pick authoritative stack(s) so port normalization is aligned)

**Verification Plan**
- `docker compose up -d` (for the chosen compose file) starts all intended services with no port binding errors.
- `curl http://localhost:8091/health/ready` returns success for deal-lifecycle (if that endpoint exists in your runtime).
- `curl http://localhost:9200/health/ready` returns success for orchestration (if that service is intended to exist).
- Dashboard loads and calls the correct API without relying on fragile fallbacks (`NEXT_PUBLIC_API_URL` missing scenario).

**Definition of Done**
- No active runtime path depends on port `8090` unless explicitly documented as legacy.
- Compose can run all intended services simultaneously without collisions.
- Example envs and client fallbacks match the runtime truth.

---

### ZK-AUD-0003 — Dashboard hides failures (mock endpoints + “fail open” empty responses)

- **Category:** `reliability`
- **Risk/Severity:** **P1** — Blast radius: **system-wide**
- **Owner Type:** `frontend`
- **Finding Signature:** `dashboard-fail-open-mock-data`

**Description**  
The dashboard can present “normal/empty” states when dependencies are down and can show mock agent activity, making operators unable to distinguish “no work” from “system broken”.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Several Dashboard API routes “fail open” and return empty/mock data on backend errors (pipeline, checkpoints, delete action, etc.)
- **Mentioned in Report B?** yes  
  > ✗ BREAK: If backend not running, dashboard silently returns empty arrays (graceful degradation hides failures)

**Evidence (reports-only)**
- Report A: mock agent activity endpoint: `zakops-agent-api/apps/dashboard/src/app/api/agent/activity/route.ts`.
- Report B: explicitly states the dashboard returns empty arrays when backend is unreachable.

**Root Cause Hypothesis (hypothesis)**  
The UI was intentionally designed to degrade gracefully for demos/dev, but it masks real outages and blocks operations troubleshooting.

**Remediation Actions**
1. Add explicit **backend connectivity/health indicator** in the UI (Report B recommends this).
2. Gate mock/fail-open behavior behind a clearly named “demo mode” flag, or remove it for production builds:
   - Replace mock agent activity with real data or label it as mock.
3. Ensure backend error states are visible (banner/toast) instead of silent empty arrays.

**Dependencies**
- `ZK-AUD-0002` (API base URLs/ports must be stable for reliable connectivity checks)

**Verification Plan**
- Stop the backend and confirm the dashboard shows a “backend disconnected” state (not just empty lists).
- Re-enable backend and confirm the status returns to “connected” and data loads.

**Definition of Done**
- Operators can distinguish “no items” vs “system down” from the UI alone.
- Mock endpoints are either removed or explicitly labeled and disabled in production profiles.

---

### ZK-AUD-0004 — Deal stage taxonomy is inconsistent across UI + backend

- **Category:** `data_flow`
- **Risk/Severity:** **P1** — Blast radius: **multi-service**
- **Owner Type:** `product`
- **Finding Signature:** `stage-taxonomy-inconsistent`

**Description**  
Multiple incompatible deal-stage enumerations exist across UI and backend, which makes filtering/sorting/transitions inconsistent and undermines reporting and automation.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > **Multiple, conflicting stage models across UI + backend**
- **Mentioned in Report B?** no  
  _No direct mention; Report B provides one stage flow example but does not describe cross-codebase inconsistency._

**Evidence (reports-only)**
- Report A cites conflicting stage sources:
  - UI: `zakops-agent-api/apps/dashboard/src/types/execution-contracts.ts` (e.g., `screening/qualified/loi/...`)
  - Backend: `zakops-backend/src/core/deals/workflow.py` (e.g., `initial_review/due_diligence/negotiation/...`)
  - UI create form: `zakops-agent-api/apps/dashboard/src/app/deals/new/page.tsx` (e.g., `underwriting/pricing/binding/...`)

**Root Cause Hypothesis (hypothesis)**  
Stages were iterated independently by different subsystems (dashboard UX, backend workflow engine, deal creation flow) without a shared canonical taxonomy.

**Remediation Actions**
1. Choose a canonical stage taxonomy (single authoritative enum + meaning per stage).
2. Update backend validation/workflow and all UI stage lists to the same taxonomy.
3. Add a migration strategy for existing deals whose `stage` values don’t match the canonical list.

**Dependencies**
- `ZK-AUD-0005` (transition payload should match once taxonomy is unified)

**Verification Plan**
- Confirm UI stage dropdowns, kanban columns, and backend workflow accept the same stage values.
- Attempt transitions across multiple deals and verify the resulting stage is consistent in DB + UI.

**Definition of Done**
- One canonical stage list is used across backend + UI.
- No stage values exist in DB that are not in the canonical taxonomy.

---

### ZK-AUD-0005 — Deal stage transition API contract mismatch (`to_stage` vs `new_stage`)

- **Category:** `ui_backend_wiring`
- **Risk/Severity:** **P0** — Blast radius: **multi-service**
- **Owner Type:** `frontend`
- **Finding Signature:** `transition-contract-mismatch`

**Description**  
The dashboard sends a transition payload shape the backend does not accept, causing UI-driven stage transitions to fail.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Deal stage transitions from UI: UI sends `{to_stage, approved_by}` but backend expects `{new_stage}`.
- **Mentioned in Report B?** no

**Evidence (reports-only)**
- Report A points to:
  - UI: `zakops-agent-api/apps/dashboard/src/lib/api.ts` (`transitionDeal()`)
  - Backend: `zakops-backend/src/api/orchestration/routers/workflow.py`
  - Backend expects `{ new_stage: "..." }`; UI sends `{ to_stage: "...", approved_by: "..." }`

**Root Cause Hypothesis (hypothesis)**  
UI and backend evolved different request contracts without a shared OpenAPI/typed client enforcing compatibility.

**Remediation Actions**
1. Update `transitionDeal()` to send `{ "new_stage": "..." }` (or introduce a server-side adapter translating UI payload → backend payload).
2. Add a contract test to prevent regressions (e.g., schema validation test against backend endpoint).

**Dependencies**
- `ZK-AUD-0004` (taxonomy consistency reduces “valid stage” mismatch risk)

**Verification Plan**
- Trigger a transition from the Deal Detail page and confirm success (no HTTP 400).
- `curl -X POST http://localhost:8091/api/deals/{deal_id}/transition -d '{"new_stage":"..."}'` returns 200 (endpoint per Report A).

**Definition of Done**
- Stage transitions succeed from the UI and are reflected in backend events/history.

---

### ZK-AUD-0006 — `/api/threads/*` is broken (DB env var mismatch + missing schema) and blocks approvals/runs UX

- **Category:** `agent_api`
- **Risk/Severity:** **P0** — Blast radius: **multi-service**
- **Owner Type:** `backend`
- **Finding Signature:** `threads-endpoints-db-miswire`

**Description**  
The dashboard’s runs/approvals UX is wired to backend `/api/threads/*`, but Report A states these endpoints 500 due to a DB URL env var mismatch and missing tables. This disables agent run streaming and tool approval flows via that path.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Backend `/api/threads` is wired to a DB URL env var that is not set + schema not present
- **Mentioned in Report B?** no (and Report B asserts HITL approvals work in a different flow; see Appendix C conflict notes)

**Evidence (reports-only)**
- Report A: `zakops-backend/src/api/orchestration/agent_invocation.py` uses `ZAKOPS_DATABASE_URL` (not `DATABASE_URL`).
- Report A: backend container does not set `ZAKOPS_DATABASE_URL`; endpoints 500 on use.
- Report A: Postgres schema lacks `zakops.agent_threads` migration/table.
- Report A: Dashboard calls Backend `/api/threads/*` and “those endpoints 500.”

**Root Cause Hypothesis (hypothesis)**  
Two separate “agent run/approval” implementations exist (backend threads vs agent-api HITL), and the dashboard is wired to the path that is currently non-functional.

**Remediation Actions**
1. **Decide** whether `/api/threads` belongs in `zakops-backend` (keep) or should be removed in favor of the Agent API’s approvals endpoints (replace).
2. If keeping `/api/threads`:
   - Standardize on `DATABASE_URL` (or set `ZAKOPS_DATABASE_URL` consistently), and add the missing DB migration for `zakops.agent_threads`.
3. If removing `/api/threads`:
   - Remove endpoints and update the dashboard to use the correct approvals/runs API (NEEDS VERIFICATION: exact dashboard wiring).

**Dependencies**
- `ZK-AUD-0016` (DB strategy + migrations)
- `ZK-AUD-0002` (consistent service routing)

**Verification Plan**
- `curl http://localhost:8091/api/threads` (or specific `/api/threads/*` used by the UI) returns 200 and reads/writes expected DB tables.
- End-to-end: create an approval from the agent and approve it from the UI; graph resumes successfully.

**Definition of Done**
- No `/api/threads/*` endpoints return 500 in the expected runtime.
- Operator approvals/runs UI works end-to-end against the chosen authoritative approvals implementation.

---

### ZK-AUD-0007 — Agent approvals DB functions not auto-applied (`001_approvals.sql`)

- **Category:** `db`
- **Risk/Severity:** **P1** — Blast radius: **single-service**
- **Owner Type:** `agent`
- **Finding Signature:** `approvals-sql-not-applied`
- **NEEDS VERIFICATION:** Confirm whether the production DB has these PL/pgSQL functions installed.

**Description**  
Report B states the Agent API relies on SQL functions for approval claim cleanup/recovery, but these are defined in a SQL migration file that is not automatically applied.

**Source Coverage**
- **Mentioned in Report A?** no
- **Mentioned in Report B?** yes  
  > **Migration SQL not auto-executed** … PL/pgSQL functions (`cleanup_expired_approvals`, `reclaim_stale_claims`) are only in the SQL file and must be manually applied.

**Evidence (reports-only)**
- Report B file reference: `apps/agent-api/migrations/001_approvals.sql`.
- Report B notes the HITL flow has “crash recovery (stale claim reclaim)” but warns of a potential break if functions are not applied.

**Root Cause Hypothesis (hypothesis)**  
The Agent API uses SQLModel auto-create for tables, but database functions live outside that mechanism and require a migration runner.

**Remediation Actions**
1. Apply `apps/agent-api/migrations/001_approvals.sql` to the actual Agent API database.
2. Add an explicit migration step to service startup/deployment so functions remain present across environments.

**Dependencies**
- `ZK-AUD-0016` (DB selection/strategy must be settled so the SQL is applied to the correct DB)

**Verification Plan**
- Query the DB to confirm `cleanup_expired_approvals` and `reclaim_stale_claims` exist.
- Exercise the approval workflow and validate stale claim recovery behavior.

**Definition of Done**
- Required PL/pgSQL functions exist in the correct database in all environments.
- HITL approval recovery works reliably after restarts/crashes.

---

### ZK-AUD-0008 — Backend search endpoints crash due to schema mismatch (`/api/search/actions`, `/api/search/global`)

- **Category:** `endpoints`
- **Risk/Severity:** **P1** — Blast radius: **single-service**
- **Owner Type:** `backend`
- **Finding Signature:** `search-endpoints-schema-mismatch`

**Description**  
Report A states backend search routes reference non-existent columns and crash with 500s.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Queries reference `zakops.actions.inputs` and `zakops.actions.risk_level`, but table uses `agent_config` and stores risk inside JSON.
- **Mentioned in Report B?** no

**Evidence (reports-only)**
- Report A points to `zakops-backend/src/api/orchestration/routers/search.py`.
- Report A states `/api/search/actions` and `/api/search/global` throw 500.

**Root Cause Hypothesis (hypothesis)**  
The search router was written against an older `zakops.actions` schema and not updated after schema changes (moving data into JSON fields).

**Remediation Actions**
1. Update `zakops-backend/src/api/orchestration/routers/search.py` to query the real schema (use `agent_config` and JSON extraction as needed).
2. Add regression tests for `/api/search/actions` and `/api/search/global`.

**Dependencies**
- None (can be fixed independently), but benefits from `ZK-AUD-0016` (schema/migration certainty).

**Verification Plan**
- `curl http://localhost:8091/api/search/actions` returns 200 (no 500).
- `curl http://localhost:8091/api/search/global` returns 200 (no 500).

**Definition of Done**
- Both search endpoints return valid responses against the current DB schema.

---

### ZK-AUD-0009 — LLM + integration configuration is brittle (wrong base URL, missing secrets, fragile fallback)

- **Category:** `env_config`
- **Risk/Severity:** **P1** — Blast radius: **multi-service**
- **Owner Type:** `devops`
- **Finding Signature:** `llm-integration-env-brittle`
- **NEEDS VERIFICATION:** Confirm actual container networking/aliases for vLLM and whether OpenAI fallback is desired.

**Description**  
Both reports describe LLM/integration configuration problems: wrong model base URL inside containers, empty/placeholder keys, and a fragile provider fallback that leads to “All providers failed”.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > `OPENAI_API_BASE=http://localhost:8000/v1` (wrong inside container; should use a reachable host/alias)
- **Mentioned in Report B?** yes  
  > ✗ BREAK: If vLLM is down, circular fallback tries OpenAI (needs API key)

**Evidence (reports-only)**
- Report A: backend env issues include `OPENAI_API_BASE` wrong in container, `LANGSMITH_API_KEY` empty, Gmail OAuth placeholders, `TOKEN_ENCRYPTION_KEY` empty.
- Report B: executors call the LLM and depend on vLLM availability/config; when vLLM is down, fallback to OpenAI needs a key, otherwise “All providers failed”.

**Root Cause Hypothesis (hypothesis)**  
Env configuration is copied from local-host assumptions into containerized runtime, secrets management is incomplete, and fallback logic is not aligned to “local-only” deployments.

**Remediation Actions**
1. Fix LLM base URL for container-to-container networking (use a reachable hostname/alias instead of `localhost` inside containers).
2. Provide required secrets/keys (or disable the dependent integrations explicitly if not used):
   - `LANGSMITH_API_KEY` (if LangSmith is intended)
   - Gmail OAuth client id/secret + `TOKEN_ENCRYPTION_KEY` (if email OAuth is intended)
3. Decide whether OpenAI fallback is allowed/expected; if not, disable fallback and return a clear “vLLM unavailable” error.
4. Add a deployment-time validation check for required env vars (fail fast rather than failing at runtime).

**Dependencies**
- `ZK-AUD-0002` (stable ports and service discovery)
- `ZK-AUD-0016` (DB migration for features that store LLM/tool execution state)

**Verification Plan**
- With vLLM up: trigger an executor/tool call and confirm success end-to-end.
- With vLLM down: confirm the system behaves as intended (either clean fallback with credentials or a clear, non-circular error).

**Definition of Done**
- No container uses `localhost` for cross-container LLM calls.
- Required secrets are present (or integrations are explicitly disabled).
- Provider failure modes are deterministic and observable.

---

### ZK-AUD-0010 — Email/DataRoom → Quarantine → Deal pipeline is broken (missing filesystem→DB bridge)

- **Category:** `data_flow`
- **Risk/Severity:** **P0** — Blast radius: **system-wide**
- **Owner Type:** `backend`
- **Finding Signature:** `email-dataroom-to-quarantine-bridge-missing`

**Description**  
Both audits identify the same core gap: inbound email/files may land on the filesystem (DataRoom) and/or email endpoints exist, but there is no reliable, automated bridge that populates Postgres `quarantine_items` so the operator can approve and create deals.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > **Not working end-to-end:** there is no evidence of a running email ingestion loop populating quarantine…
- **Mentioned in Report B?** yes  
  > ✗ BREAK: No automatic bridge from filesystem → quarantine_items DB table

**Evidence (reports-only)**
- Report A: backend exposes Gmail OAuth + email endpoints under `/api/integrations/email/*` and has `zakops.quarantine_items` + `/api/quarantine*`.
- Report A: recommends “run a poller/webhook that populates `zakops.inbox` and `zakops.quarantine_items`.”
- Report B: describes `sync_acquisition_emails.py` writing to `/home/zaks/DataRoom/00-PIPELINE/Inbound/{deal}/`, but the monorepo backend in docker “does NOT mount DataRoom”.
- Report B: explicitly states the filesystem→DB bridge is “manual/broken.”

**Root Cause Hypothesis (hypothesis)**  
Email ingestion was implemented as filesystem-first (DataRoom) while the operator workflow expects DB-first (quarantine_items). Containerization removed filesystem access (missing DataRoom mounts), and an importer/bridge process was not operationalized.

**Remediation Actions**
1. Choose the authoritative ingestion strategy:
   - **DB-first:** email ingestion writes directly to `quarantine_items`, with DataRoom as optional artifact storage.
   - **Filesystem-first:** DataRoom remains the intake, and a bridge imports inbound files into `quarantine_items`.
2. If filesystem-first (per Report B’s described flow), add DataRoom volume mounts to the backend container (`deployments/docker/docker-compose.yml`) so it can read `/home/zaks/DataRoom`.
3. Implement and run the bridge:
   - A scheduled job/poller/webhook that reads inbound artifacts and creates `quarantine_items` in Postgres.
4. Add observability for ingestion: counts of inbound emails/files processed, counts of quarantine items created.

**Dependencies**
- `ZK-AUD-0016` (ensure the bridge writes to the correct DB)
- `ZK-AUD-0001` (decide which stack owns ingestion)

**Verification Plan**
- Send a test email with an attachment and confirm:
  - A quarantine item appears in the DB (`zakops.quarantine_items`).
  - The dashboard shows the new item on `/quarantine`.
  - Approving creates a deal record.

**Definition of Done**
- Email/files reliably produce quarantine items automatically (no manual DB inserts).
- Operator can approve/reject and see deterministic outcomes (deal created or item rejected).

---

### ZK-AUD-0011 — Quarantine model mismatch (UI treats quarantine as actions; backend exposes separate `/api/quarantine`)

- **Category:** `ui_backend_wiring`
- **Risk/Severity:** **P0** — Blast radius: **multi-service**
- **Owner Type:** `frontend`
- **Finding Signature:** `quarantine-model-mismatch`

**Description**  
Report A states the dashboard quarantine UX assumes “quarantine items are actions” and calls action execution endpoints the backend doesn’t expose, while the backend has a distinct quarantine model and endpoints.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > UI: Quarantine page assumes “quarantine items are actions” and tries `POST /api/actions/{id}/execute`
- **Mentioned in Report B?** no  
  _No direct mention of the UI contract mismatch; Report B focuses on the filesystem→DB bridge gap._

**Evidence (reports-only)**
- Report A:
  - Dashboard quarantine page: `zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
  - Backend quarantine endpoints: `/api/quarantine/*`
  - UI calls missing action execution endpoints (`/api/actions/{id}/execute`).

**Root Cause Hypothesis (hypothesis)**  
Two competing representations of “quarantine” exist (quarantine_items vs action-based quarantine), and the UI was built against a different contract than the running backend provides.

**Remediation Actions**
1. Pick one canonical quarantine model:
   - **Option A:** Quarantine is first-class (`/api/quarantine/*` + `quarantine_items` table). Update UI to call `/api/quarantine/{id}/process`.
   - **Option B:** Quarantine items are represented as actions. Implement backend action execution endpoints and generate actions for quarantine items.
2. Align the dashboard quarantine page to the canonical backend contract; remove calls to non-existent endpoints.
3. Add an end-to-end test: create quarantine item → approve → deal/action result.

**Dependencies**
- `ZK-AUD-0010` (quarantine must be populated)
- `ZK-AUD-0012` (if Option B, action execution must work)

**Verification Plan**
- Approve/reject a quarantine item from the UI and confirm the backend processes it without 4xx/5xx errors.
- Confirm resulting state change in DB and the UI updates accordingly.

**Definition of Done**
- Quarantine page operations (approve/reject) work end-to-end against real backend endpoints.
- No UI call path attempts `/api/actions/{id}/execute` unless that endpoint is implemented.

---

### ZK-AUD-0012 — Actions + outbox processing not running end-to-end (empty actions table, missing worker)

- **Category:** `background_jobs`
- **Risk/Severity:** **P0** — Blast radius: **system-wide**
- **Owner Type:** `backend`
- **Finding Signature:** `actions-worker-outbox-not-running`
- **NEEDS VERIFICATION:** Confirm which worker(s) are required in the intended runtime (outbox-worker vs actions_runner.py vs both).

**Description**  
Both audits agree the architecture includes background processing (outbox pattern and action runner), but in the observed runtime the worker is not running and the action pipeline is not demonstrably producing or executing actions.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > The **actions table is currently empty**.
- **Mentioned in Report B?** yes  
  > ✗ BREAK: actions_runner.py must be running as separate process

**Evidence (reports-only)**
- Report A:
  - “Your ‘outbox worker’ … is defined in compose, but is not running right now.”
  - `/health/ready` returns `outbox_processor: not running`.
  - “the action engine exists in code, but the creation + execution pipeline is not actually functioning…”
- Report B:
  - Action execution requires a separate runner process/container (`actions_runner.py`) and may not be running in dev unless started manually.
  - Outbox pattern code exists; whether processor runs is “unclear.”

**Root Cause Hypothesis (hypothesis)**  
The system’s “durable work” path depends on a worker that is not included/started in the default runtime, and the UI expects execution capabilities not fully exposed by the backend.

**Remediation Actions**
1. Make the worker(s) a first-class part of the runtime:
   - Ensure compose starts the outbox/action runner container(s).
   - Ensure `/health/ready` reports the processor running.
2. Establish a single “action lifecycle” contract:
   - How actions are created (UI/agent), leased, executed, retried, and marked complete.
3. Add a smoke test: create an action → observe lease acquisition → observe status transition to completed/failed.

**Dependencies**
- `ZK-AUD-0011` (quarantine may rely on action execution)
- `ZK-AUD-0002` (ports/URLs stable so runner can reach APIs)

**Verification Plan**
- Create a test action and confirm:
  - A DB row appears in `actions`.
  - Worker acquires lease and transitions state.
  - Logs show executor run and outcome.
- `/health/ready` indicates the processor is running (Report A evidence point).

**Definition of Done**
- Worker(s) run by default in the standard compose/dev workflow.
- Actions created by UI/agent are executed and reach terminal states reliably.

---

### ZK-AUD-0013 — Chat proposal execution is stubbed (HTTP 501)

- **Category:** `endpoints`
- **Risk/Severity:** **P2** — Blast radius: **single-service**
- **Owner Type:** `frontend`
- **Finding Signature:** `chat-proposal-execute-501`

**Description**  
The UI can display “proposals” but cannot execute approved proposals; the route handler is explicitly unimplemented and returns a placeholder status.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Chat proposal execution is explicitly unimplemented
- **Mentioned in Report B?** no

**Evidence (reports-only)**
- Report A file reference: `zakops-agent-api/apps/dashboard/src/app/api/chat/execute-proposal/route.ts`.
- Report A: “Dashboard returns HTTP 501 placeholder for proposal execution.”

**Root Cause Hypothesis (hypothesis)**  
The proposal execution path was scaffolded as part of a future “chat → action” workflow but never wired to backend execution.

**Remediation Actions**
1. Implement `POST /api/chat/execute-proposal` end-to-end to create/execute the corresponding backend action/quarantine operation, **or** remove the UI affordance until supported.
2. Add an end-to-end test that approves a proposal and verifies the resulting backend state change.

**Dependencies**
- `ZK-AUD-0012` (execution must be durable if proposals create actions)

**Verification Plan**
- `curl -X POST http://localhost:3003/api/chat/execute-proposal …` returns 2xx and triggers the intended backend change.

**Definition of Done**
- Approved chat proposals can be executed successfully, or the UI no longer exposes the feature.

---

### ZK-AUD-0014 — Backend chat fallback `/api/agent/invoke` rejects real deal IDs (expects UUID)

- **Category:** `endpoints`
- **Risk/Severity:** **P2** — Blast radius: **multi-service**
- **Owner Type:** `backend`
- **Finding Signature:** `agent-invoke-deal-id-type-mismatch`

**Description**  
Report A states the dashboard’s chat fallback uses `/api/agent/invoke`, but the backend expects a UUID deal_id whereas real deal IDs are strings (e.g., `DL-0012`), causing failures.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Break: backend expects UUID deal_id; real deal ids are strings like `DL-0012`.
- **Mentioned in Report B?** no

**Evidence (reports-only)**
- Report A: chat route fallback uses `/api/agent/invoke`; backend expects UUID deal_id.

**Root Cause Hypothesis (hypothesis)**  
The agent invocation endpoint was built assuming UUID primary keys while the deal system uses human-readable string IDs.

**Remediation Actions**
1. Align ID types: accept string IDs in `/api/agent/invoke`, or translate string IDs → UUID internally if a UUID exists.
2. Add a contract test ensuring the endpoint accepts the real deal ID format used by the system.

**Dependencies**
- `ZK-AUD-0016` (DB schema/ID strategy)

**Verification Plan**
- Invoke the fallback with a known string deal ID and confirm a successful response.

**Definition of Done**
- Chat fallback path works with real deal IDs.

---

### ZK-AUD-0015 — Redis is configured/running but not used in application code

- **Category:** `architecture`
- **Risk/Severity:** **P2** — Blast radius: **single-service**
- **Owner Type:** `devops`
- **Finding Signature:** `redis-unused`
- **NEEDS VERIFICATION:** Report A lists Redis as part of the platform; Report B claims no Redis usage in code (see Appendix C conflict notes).

**Description**  
Report B states Redis is present in docker-compose and env but not actually used by backend/agent code, contradicting platform claims that Redis powers cache/sessions/queues.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > **Redis (ZakOps)**: `localhost:6379` (Docker)
- **Mentioned in Report B?** yes  
  > **Redis runs but is NOT actually used in application code.**

**Evidence (reports-only)**
- Report B: docker-compose includes Redis and backend has `REDIS_URL` in env, but “no Redis client is imported or used in the Python backend or agent code.”

**Root Cause Hypothesis (hypothesis)**  
Redis was planned/added for queues/sessions but the implementation remained DB-based or was removed without updating infra/docs.

**Remediation Actions**
1. Decide: either remove Redis from compose and docs **or** implement Redis-backed features intentionally (cache/session/queue) and document them.
2. If removed, update V3 docs and env examples that imply Redis usage.

**Dependencies**
- None

**Verification Plan**
- Code audit: confirm whether any Redis client is used (Report B claims none).
- After removal: confirm stack still runs with no missing dependencies.

**Definition of Done**
- Redis is either actively used with documented responsibilities or removed from the default runtime and docs.

---

### ZK-AUD-0016 — Database configuration sprawl + migration uncertainty (risk of writing to the wrong DB)

- **Category:** `db`
- **Risk/Severity:** **P0** — Blast radius: **system-wide**
- **Owner Type:** `data`
- **Finding Signature:** `db-sprawl-migrations-uncertain`

**Description**  
Report B identifies multiple DBs and defaults that can cause services to silently connect to the wrong database; it also states there is no single migration command that guarantees all schemas are correctly installed.

**Source Coverage**
- **Mentioned in Report A?** yes  
  > Backend `/api/threads` is wired to a DB URL env var that is not set + schema not present
- **Mentioned in Report B?** yes  
  > Agent API defaults to `food_order_db` in code … `.env.development` overrides to `zakops_agent`.

**Evidence (reports-only)**
- Report B lists multiple databases:
  - `zakops` database (docker-compose)
  - `zakops_agent` database (agent-api `.env.development`)
  - `food_order_db` (agent-api code default — leftover)
  - `crawlrag` database (RAG service)
  - SQLite files in DataRoom (legacy deal registry)
- Report B: “There is no single migration command that sets up all schemas correctly.”
- Report A: backend `/api/threads` uses a DB URL env var not set and lacks `zakops.agent_threads`.

**Root Cause Hypothesis (hypothesis)**  
Multiple subsystems (backend, agent-api, RAG, legacy) were built with different persistence layers and defaults, without a single end-to-end migration and env alignment strategy.

**Remediation Actions**
1. Decide the authoritative DB topology:
   - Single Postgres instance with one canonical DB (preferred) vs multiple DBs with explicit contracts.
2. Remove dangerous defaults:
   - Fix agent-api default DB name (`food_order_db`) so missing envs cannot silently connect to a leftover DB.
3. Create a single migration entrypoint:
   - One command/script that initializes backend schema(s), agent schema(s), and required functions.
4. Document the DB matrix (which service uses which schema/DB) and enforce it in CI.

**Dependencies**
- `ZK-AUD-0001` (which stack is authoritative)
- `ZK-AUD-0002` (compose/env consistency)

**Verification Plan**
- Start all services with minimal env and confirm they connect to the intended DB(s) (no silent defaults).
- Run the unified migration command and confirm required tables/functions exist (including approvals and threads tables if needed).

**Definition of Done**
- No service can start while pointing at an unintended DB (fail-fast).
- A single documented migration command brings a fresh environment to a known-good state.

---

### ZK-AUD-0017 — Auth disabled by default (backend + agent) / dev-mode operator is auto-created

- **Category:** `auth`
- **Risk/Severity:** **P1** — Blast radius: **system-wide**
- **Owner Type:** `security`
- **Finding Signature:** `auth-disabled-by-default`

**Description**  
Report B indicates authentication is opt-in and disabled by default in both backend and agent services, with dev-mode behavior creating a mock operator. This is acceptable for local dev but is a production risk if not explicitly gated.

**Source Coverage**
- **Mentioned in Report A?** no
- **Mentioned in Report B?** yes  
  > **Auth disabled by default everywhere** … Backend: `AUTH_REQUIRED=false`, Agent: `AGENT_JWT_ENFORCE=false`

**Evidence (reports-only)**
- Report B: “Auth middleware creates a mock ‘dev’ operator when disabled. No real session management is active in dev mode.”

**Root Cause Hypothesis (hypothesis)**  
Local-first development defaults were never complemented with a production-safe configuration profile.

**Remediation Actions**
1. Create explicit environment profiles:
   - `dev`: auth optional
   - `prod`: auth required, no mock operator
2. Enforce `AUTH_REQUIRED=true` and `AGENT_JWT_ENFORCE=true` in production deployments.
3. Add a smoke test that fails CI if production profile allows unauthenticated access.

**Dependencies**
- `ZK-AUD-0018` (secrets/token hygiene)

**Verification Plan**
- In prod profile, call key endpoints without auth and confirm 401/403 responses.
- Confirm dev profile remains usable for local iteration.

**Definition of Done**
- Production profile rejects unauthenticated requests; dev profile behavior is explicitly documented and gated.

---

### ZK-AUD-0018 — `DASHBOARD_SERVICE_TOKEN` is hardcoded in compose/.env (secret hygiene issue)

- **Category:** `security`
- **Risk/Severity:** **P1** — Blast radius: **system-wide**
- **Owner Type:** `security`
- **Finding Signature:** `hardcoded-dashboard-service-token`

**Description**  
Report B states a dashboard service token is committed in docker-compose and `.env.local`, which is a security and operational risk (token reuse, accidental exposure).

**Source Coverage**
- **Mentioned in Report A?** no
- **Mentioned in Report B?** yes  
  > **DASHBOARD_SERVICE_TOKEN hardcoded in docker-compose**

**Evidence (reports-only)**
- Report B: `deployments/docker/docker-compose.yml:20,77` contains the token and it’s also present in `.env.local`.

**Root Cause Hypothesis (hypothesis)**  
Token was introduced for service-to-service auth during dev and committed for convenience, without secrets management/rotation.

**Remediation Actions**
1. Remove the token from versioned compose/env files.
2. Rotate the token and load it via an env-only secrets mechanism.
3. Add a repo secret-scanning gate to prevent reintroduction.

**Dependencies**
- `ZK-AUD-0017` (auth strategy)

**Verification Plan**
- Confirm token value is not present in tracked files.
- Confirm services still authenticate correctly using the rotated token loaded from secrets.

**Definition of Done**
- No committed secrets in compose/.env files; token is rotated and sourced securely.

---

### ZK-AUD-0019 — Observability stack is defined but not proven working (metrics/dashboards may be stale)

- **Category:** `logging_observability`
- **Risk/Severity:** **P2** — Blast radius: **multi-service**
- **Owner Type:** `devops`
- **Finding Signature:** `observability-theoretical`
- **NEEDS VERIFICATION:** Determine which observability components are actually running and whether services expose scrapeable metrics.

**Description**  
Report B states observability containers/configs exist (Prometheus/Grafana/Loki/Promtail; OTEL deps installed), but it is unclear whether they are running and whether the applications emit usable metrics/logs.

**Source Coverage**
- **Mentioned in Report A?** no
- **Mentioned in Report B?** yes  
  > Prometheus, Grafana, Loki, and Promtail are defined in docker-compose but…

**Evidence (reports-only)**
- Report B: configs exist in `ops/observability/` and dashboards in `ops/observability/grafana/dashboards/`.
- Report B: “Prometheus scrape targets point to services that may not expose `/metrics`.”
- Report B: “Langfuse keys are empty in `.env.development`.”

**Root Cause Hypothesis (hypothesis)**  
Observability was scaffolded as an infrastructure layer, but app instrumentation and runtime enablement were not completed or drifted from dashboards.

**Remediation Actions**
1. Verify which observability containers are actually running in the standard stack.
2. Ensure each service exposes a metrics endpoint (or OTEL exporter) that Prometheus can scrape.
3. Validate Grafana dashboards against actual metrics names.
4. Configure Langfuse/LangSmith only if required (and ensure keys are present if enabled).

**Dependencies**
- `ZK-AUD-0003` (surface health in UI)

**Verification Plan**
- Open Grafana and confirm dashboards populate with live data.
- Confirm Prometheus scrape targets are up and no longer report missing `/metrics`.

**Definition of Done**
- Operators can observe service health and key workflow metrics (ingestion counts, action queue depth, approvals pending).

---

### ZK-AUD-0020 — Unverified/aspirational infra + quality gates (CI status unknown; blue/green, chaos, gates may not match runtime)

- **Category:** `testing`
- **Risk/Severity:** **P3** — Blast radius: **system-wide**
- **Owner Type:** `devops`
- **Finding Signature:** `aspirational-infra-gates`
- **NEEDS VERIFICATION:** Run the referenced scripts/workflows against the current runtime and record pass/fail.

**Description**  
Report B notes several operational readiness assets exist (CI workflows, quality gates, chaos scripts, blue/green deployment), but their real-world validity against the current runtime is unknown or aspirational.

**Source Coverage**
- **Mentioned in Report A?** no
- **Mentioned in Report B?** yes  
  > Whether they pass is unknown — likely many would fail against current runtime.

**Evidence (reports-only)**
- Report B references:
  - `deployments/bluegreen/` (aspirational)
  - `tools/gates/` (scripts exist, pass status unknown)
  - `tools/chaos/` (aspirational)
  - `.github/workflows/ci.yml`, `deploy.yaml` (exist; CI green unknown)
  - Doc mismatch: “Actually 5 tools … V3 says 4, code has 5.”

**Root Cause Hypothesis (hypothesis)**  
Readiness artifacts were created as a roadmap, but have not been continuously maintained as the runtime wiring/config drifted.

**Remediation Actions**
1. Run CI (or replicate locally) and record failures; fix only what is required for the intended deployment profile.
2. Run `tools/gates/` and triage failures; update scripts that reference decommissioned ports/services.
3. Decide whether blue/green and chaos tooling are in-scope; if not, archive/remove to reduce confusion.
4. Update docs to reflect current tool count and runtime realities.

**Dependencies**
- `ZK-AUD-0002` (port drift likely breaks gates)
- `ZK-AUD-0001` (source-of-truth clarity)

**Verification Plan**
- Gates run clean against the declared standard stack.
- CI pipeline is green for the declared standard stack.

**Definition of Done**
- A verified set of quality gates exists that matches the current runtime and is run routinely.

---

## Consolidated Action Checklist (Execution-Ready)

### Checklist Table (1 primary action per finding)

| Finding ID | Action item | Where to change | Priority | Effort | Verification command(s)/test(s) | Expected observable result |
|---|---|---|---|---|---|---|
| ZK-AUD-0001 | Decide authoritative stack; decommission/label legacy | runbooks + service configs | P1 | M | `docker ps`; `ss -lntp` | Only intended services/ports running |
| ZK-AUD-0002 | Fix port drift + compose conflicts (8090/8091/9200) | `deployments/docker/docker-compose.yml`; env/examples | P0 | S | `docker compose up -d` | No port bind errors; services reachable on intended ports |
| ZK-AUD-0003 | Add explicit health indicator; remove/gate mock data | dashboard routes (`apps/dashboard/src/app/api/...`) | P1 | M | Stop backend → refresh UI | UI shows “disconnected”, not empty/mock |
| ZK-AUD-0004 | Choose canonical stage taxonomy and align UI/backend | `execution-contracts.ts`; `workflow.py`; create form | P1 | L | Transition + filter deals | Same stage values everywhere |
| ZK-AUD-0005 | Fix transition payload (`to_stage`→`new_stage`) | `apps/dashboard/src/lib/api.ts`; backend router | P0 | S | UI transition; `curl` transition endpoint | 2xx response; stage changes visible |
| ZK-AUD-0006 | Fix or remove `/api/threads/*` and wire approvals correctly | `agent_invocation.py`; dashboard agent client | P0 | M | `curl /api/threads/*` | No 500s; approvals UI works end-to-end |
| ZK-AUD-0007 | Apply/automate `001_approvals.sql` | `apps/agent-api/migrations/001_approvals.sql` | P1 | S | SQL check for functions | Functions exist; approvals recovery works |
| ZK-AUD-0008 | Fix `/api/search/actions` + `/api/search/global` schema mismatch | `zakops-backend/.../routers/search.py` | P1 | M | `curl /api/search/actions` | 200 responses; no 500 |
| ZK-AUD-0009 | Fix LLM base URL + required secrets; clarify fallback | env vars + integration configs | P1 | M | Run tool/executor; vLLM down test | Deterministic behavior; no “all providers failed” surprise |
| ZK-AUD-0010 | Build filesystem/email → DB quarantine bridge | ingestion bridge job + DataRoom mounts | P0 | L | Send test email → check quarantine | Quarantine items created automatically |
| ZK-AUD-0011 | Align quarantine UI contract with backend model | `apps/dashboard/src/app/quarantine/page.tsx` + backend endpoints | P0 | M | Approve/reject item in UI | Correct backend calls; state changes persist |
| ZK-AUD-0012 | Ensure actions/outbox worker runs and processes actions | compose worker + `actions_runner.py` | P0 | L | Create action → observe execution | Actions move to completed/failed |
| ZK-AUD-0013 | Implement or remove chat proposal execution | `.../execute-proposal/route.ts` | P2 | M | `curl /api/chat/execute-proposal` | 2xx + real execution, or feature removed |
| ZK-AUD-0014 | Accept real deal IDs in `/api/agent/invoke` | backend agent invoke endpoint | P2 | S | Invoke with `DL-####` | Successful response |
| ZK-AUD-0015 | Remove Redis or implement usage | docker-compose + code | P2 | S | Remove Redis → run stack | No breakage, or verified Redis feature |
| ZK-AUD-0016 | Unify DB strategy; remove wrong defaults; one migration command | agent config + env + migrations | P0 | L | Fresh setup via one command | Services point to correct DB; schema present |
| ZK-AUD-0017 | Require auth in prod profile (no mock operator) | env profiles + middleware | P1 | M | Unauthed request in prod | 401/403 in prod profile |
| ZK-AUD-0018 | Remove/rotate hardcoded service token | `deployments/docker/docker-compose.yml` | P1 | S | Secret scan + run stack | No token in repo; auth still works |
| ZK-AUD-0019 | Verify metrics/logs; fix scrape/dashboards | `ops/observability/*` | P2 | M | Prometheus targets up; dashboards populated | Live observability works |
| ZK-AUD-0020 | Run gates/CI/chaos/bluegreen; archive or fix | `tools/gates/*`; `.github/workflows/*` | P3 | M | Run gates; CI green | Verified readiness artifacts |

### Expanded Checklist (detailed)

- `ZK-AUD-0002` — Fix docker-compose ports (`deployments/docker/docker-compose.yml`) — **P0** — **S** — Verify: `docker compose up -d` — Expect: orchestration and lifecycle can run without port collision.
- `ZK-AUD-0016` — Fix Agent API DB defaults (`apps/agent-api/app/core/config.py:180`) and unify DB strategy — **P0** — **L** — Verify: run services with minimal env — Expect: no silent connection to `food_order_db`; all services target intended DB.
- `ZK-AUD-0010` — Implement/run Email/DataRoom → Quarantine bridge + mounts — **P0** — **L** — Verify: send test email — Expect: new row in `zakops.quarantine_items` and visible in UI.
- `ZK-AUD-0011` — Wire quarantine approve/reject to canonical backend contract — **P0** — **M** — Verify: approve from UI — Expect: backend processes item (no `/api/actions/{id}/execute` unless implemented).
- `ZK-AUD-0012` — Start worker(s) and make `/health/ready` green — **P0** — **L** — Verify: create action → observe execution — Expect: lease acquisition + terminal status.
- `ZK-AUD-0006` — Fix/remove `/api/threads/*` (DB env var + migrations) — **P0** — **M** — Verify: `curl /api/threads/*` — Expect: no 500; approvals/runs UI works.
- `ZK-AUD-0008` — Fix backend search schema mismatch — **P1** — **M** — Verify: `curl /api/search/actions` — Expect: 200 with results.
- `ZK-AUD-0009` — Fix LLM base URL/secrets; clarify fallback — **P1** — **M** — Verify: run executor + vLLM-down test — Expect: deterministic error/fallback behavior.
- `ZK-AUD-0007` — Apply approvals SQL functions — **P1** — **S** — Verify: DB functions exist — Expect: stale claim cleanup works.
- `ZK-AUD-0001` — Decommission/label legacy stacks — **P1** — **M** — Verify: `docker ps` and docs — Expect: one authoritative runtime.
- `ZK-AUD-0017` — Require auth in production profile — **P1** — **M** — Verify: unauthenticated request blocked — Expect: 401/403 in prod.
- `ZK-AUD-0018` — Remove/rotate hardcoded token — **P1** — **S** — Verify: secret scan + run — Expect: no token in tracked files.
- `ZK-AUD-0003` — Remove/gate mock data + add health banner — **P1** — **M** — Verify: backend down shows error — Expect: visible disconnected state.
- `ZK-AUD-0004` — Unify stage taxonomy — **P1** — **L** — Verify: filters/transitions — Expect: consistent stage values everywhere.
- `ZK-AUD-0015` — Remove Redis or implement usage — **P2** — **S** — Verify: remove Redis container and run — Expect: no break or documented Redis feature.
- `ZK-AUD-0013` — Implement or remove chat proposal execution — **P2** — **M** — Verify: `/api/chat/execute-proposal` returns 2xx or feature removed — Expect: no 501 placeholder.
- `ZK-AUD-0014` — Fix `/api/agent/invoke` deal_id type — **P2** — **S** — Verify: call with `DL-####` — Expect: success.
- `ZK-AUD-0019` — Make observability real — **P2** — **M** — Verify: dashboards populated — Expect: metrics/logs visible.
- `ZK-AUD-0020` — Validate gates/CI/chaos/bluegreen — **P3** — **M** — Verify: gates pass, CI green — Expect: readiness artifacts match runtime.

---

## Prioritized Remediation Plan (Phased)

### Phase P0 — Restore determinism + close the core pipeline
1. **Ports & routing truth:** complete `ZK-AUD-0002` so you can run the intended stack without collisions and all clients call the correct ports.
2. **DB truth:** complete `ZK-AUD-0016` so services cannot silently use the wrong DB and a fresh environment can be created reliably.
3. **Intake bridge:** complete `ZK-AUD-0010` so inbound emails/files reliably populate quarantine.
4. **Quarantine wiring:** complete `ZK-AUD-0011` so operator approval/rejection works.
5. **Execution durability:** complete `ZK-AUD-0012` so approvals cause work to run (worker(s) running and healthy).
6. **Approvals/runs UX:** complete `ZK-AUD-0006` so the UI is wired to the working approvals system.

### Phase P1 — Stabilize correctness + security posture
- Fix search crashes (`ZK-AUD-0008`).
- Fix LLM/integration env + secrets (`ZK-AUD-0009`) and approvals DB functions (`ZK-AUD-0007`).
- Remove hardcoded secrets (`ZK-AUD-0018`) and enforce auth in prod profile (`ZK-AUD-0017`).
- Decide and execute decommission plan for competing stacks (`ZK-AUD-0001`).

### Phase P2 — Reduce operator confusion; improve reliability
- Remove/gate mock/fail-open UI behavior and add explicit health indicators (`ZK-AUD-0003`).
- Fix chat fallback and proposal execution plumbing (`ZK-AUD-0013`, `ZK-AUD-0014`).
- Decide what to do with Redis (`ZK-AUD-0015`).
- Make observability verifiably functional (`ZK-AUD-0019`).

### Phase P3 — Validate readiness artifacts
- Run and reconcile gates/CI/chaos/bluegreen tooling; archive what is not maintained (`ZK-AUD-0020`).

---

## Verification & QA Plan (End-to-End Proof Strategy)

### E2E flows to prove fixed
1. **Deal CRUD + events**
   - Verify: `GET /api/deals`, `GET /api/deals/{deal_id}`, `GET /api/deals/{deal_id}/events`, `POST /api/deals/{deal_id}/note` (Report A: “Observed working” baseline).
2. **Stage transition from UI**
   - Verify UI transition works (fix `ZK-AUD-0005`) and stage taxonomy is consistent (`ZK-AUD-0004`).
3. **Search endpoints**
   - Verify `/api/search/actions` and `/api/search/global` return 200 (fix `ZK-AUD-0008`).
4. **Chat**
   - Verify Dashboard `/api/chat` and `/api/chat/complete` succeed.
   - Verify tool calls work when backend is up and DB has data.
   - Verify failure mode when vLLM is down is deterministic (`ZK-AUD-0009`).
5. **Approvals**
   - Verify end-to-end HITL approval: propose → pending approval appears → approve → graph resumes (fix `ZK-AUD-0006`, `ZK-AUD-0007`).
6. **Email/DataRoom → Quarantine → Deal**
   - Verify test email leads to new DB quarantine item and visible UI item; approving creates a deal (`ZK-AUD-0010`, `ZK-AUD-0011`).
7. **Action execution**
   - Verify creating an action results in worker execution and terminal status (`ZK-AUD-0012`).

### Minimum acceptance gates (Definition of Done across the system)
- All P0 findings have passing verification steps and observable results.
- Dashboard displays a clear “backend disconnected” indicator when the backend is unavailable.
- No critical endpoints return 500 due to avoidable schema/env drift (`/api/threads/*`, search endpoints).

---

## Coverage & Integrity Proof (No-Drop Guarantee)

### A) Coverage counts
- Count of atomic findings extracted from Report A: **17**
- Count of atomic findings extracted from Report B: **19**
- Count of unique master findings after merge: **20**

### B) No-drop guarantee checklist
- [x] Every atomic item from Report A is mapped to a Master Finding ID
- [x] Every atomic item from Report B is mapped to a Master Finding ID

### C) Traceability appendices
- Appendix A: **Report A → Master ID mapping** (includes atomic extraction fields)
- Appendix B: **Report B → Master ID mapping** (includes atomic extraction fields)

### D) Conflict register
- Appendix C: **Conflict register** (explicit contradictions + resolution/verification steps)

---

## Appendices

## Appendix A — Report A → Master ID mapping (Atomic Extraction)

> Each item below is a single “atomic finding” extracted from Report A, with the required Phase 1 fields and a mapping to a master finding ID.

### A-ATOM-001 → ZK-AUD-0001
- **Finding Signature:** `backend-codepath-source-of-truth-mismatch`
- **Category:** `architecture`
- **original_text (Report A):**
  > **Key contrarian fact:** you have *multiple* “backend-ish” codepaths in-repo, but the only backend actually serving `:8091` is `zakops-backend/`.
  > `zakops-agent-api/apps/backend/` exists but is not the backend actually serving `:8091`.
- **Impact:** Operators/devs may wire UI/tools/docs to the wrong backend implementation; duplicate/legacy backends increase operational risk.
- **Evidence:** Report A runtime observation of `:8091` served by `zakops-backend/`; explicit note that `apps/backend` is not serving.
- **Suggested fix (Report A):** Implied by “legacy leftovers” + fix plan: align on the real running backend; remove/ignore legacy paths.
- **Verification (Report A):** Not provided explicitly; verify by confirming which service serves `:8091` and aligning clients accordingly.

### A-ATOM-002 → ZK-AUD-0002
- **Finding Signature:** `no-active-9200-service-doc-mismatch`
- **Category:** `architecture`
- **original_text (Report A):**
  > **Claim:** Backend is split into Deal Lifecycle `:8091` + Orchestration `:9200`.
  > **Reality:** The running backend is a single service on `:8091` built from `zakops-backend/`. There is no active `:9200` service in the observed stack.
- **Impact:** Docs/expectations about orchestration service lead to broken wiring and incorrect operational assumptions.
- **Evidence:** “Observed stack” and explicit statement “no active `:9200` service”.
- **Suggested fix (Report A):** Align docs and runtime; remove or implement split as needed (implicit).
- **Verification (Report A):** Not provided; verify by checking listening ports and services.

### A-ATOM-003 → ZK-AUD-0002
- **Finding Signature:** `8090-decommission-claim-false`
- **Category:** `env_config`
- **original_text (Report A):**
  > Port **8090** is still referenced widely in docs/scripts/config despite V3 claiming it’s decommissioned.
  > `8090` still appears in `zakops-backend/.env.example`, backend container env (`ZAKOPS_DEAL_API_URL`), and multiple docs/tools.
  > Legacy: `zakops-backend/src/agent/bridge/mcp_server.py` (still hard-coded to `:8090`)
- **Impact:** Requests/tools may target decommissioned ports, causing outages and confusing failures.
- **Evidence:** Specific file/env references above.
- **Suggested fix (Report A):** “Port 8090 is still referenced widely…” implies removing/updating these references.
- **Verification (Report A):** Not provided; verify by searching for `8090` references and confirming runtime does not depend on them.

### A-ATOM-004 → ZK-AUD-0010
- **Finding Signature:** `email-ingestion-not-populating-quarantine`
- **Category:** `data_flow`
- **original_text (Report A):**
  > **Not working end-to-end:** there is no evidence of a running email ingestion loop populating quarantine…
  > **Ingestion loop**: run a poller/webhook that populates `zakops.inbox` and `zakops.quarantine_items`.
- **Impact:** No new quarantine items appear; operator cannot intake deals from email.
- **Evidence:** Report A explicitly states “no evidence” and suggests running a poller/webhook.
- **Suggested fix (Report A):** Run a poller/webhook to populate `zakops.inbox` and `zakops.quarantine_items`.
- **Verification (Report A):** Not provided; verify by confirming quarantine items appear after ingestion is enabled.

### A-ATOM-005 → ZK-AUD-0011
- **Finding Signature:** `quarantine-ui-assumes-actions`
- **Category:** `ui_backend_wiring`
- **original_text (Report A):**
  > UI: Quarantine page assumes “quarantine items are actions” and tries `POST /api/actions/{id}/execute`
  > Break: backend does not expose execute/retry/update endpoints; backend quarantine is a different model (`/api/quarantine/*`).
- **Impact:** Quarantine approvals fail; operator cannot process inbound items.
- **Evidence:** Endpoint mismatch described explicitly.
- **Suggested fix (Report A):** Fix plan: “Quarantine UX: wire UI to `/api/quarantine/{id}/process` … OR migrate quarantine to action-based model consistently.”
- **Verification (Report A):** Not provided; verify by approving/rejecting quarantine items end-to-end.

### A-ATOM-006 → ZK-AUD-0012
- **Finding Signature:** `actions-table-empty`
- **Category:** `background_jobs`
- **original_text (Report A):**
  > The **actions table is currently empty**.
  > **Not working end-to-end:** the action engine exists in code, but the creation + execution pipeline is not actually functioning in the running stack.
- **Impact:** No actions are executed; approvals/execution workflows stall.
- **Evidence:** Report A explicitly asserts the table is empty and pipeline not functioning.
- **Suggested fix (Report A):** Fix plan: “Bring up the outbox worker … Decide the single ‘action execution contract’ … implement execute|retry|update|cancel or remove UI controls.”
- **Verification (Report A):** Not provided; verify by creating actions and observing execution to completion.

### A-ATOM-007 → ZK-AUD-0011
- **Finding Signature:** `dashboard-expects-action-exec-endpoints`
- **Category:** `endpoints`
- **original_text (Report A):**
  > The dashboard’s “execute/run action” calls expect endpoints that the backend does not expose.
  > create/execute/retry/update flows expect endpoints that don’t exist.
- **Impact:** Operator cannot execute actions from the UI; execution controls are broken.
- **Evidence:** Explicitly stated missing endpoints.
- **Suggested fix (Report A):** “Decide the single ‘action execution contract’ … implement `/api/actions/{id}/execute|retry|update|cancel` … or remove those UI controls.”
- **Verification (Report A):** Not provided; verify UI action controls call real endpoints and succeed.

### A-ATOM-008 → ZK-AUD-0012
- **Finding Signature:** `outbox-worker-not-running`
- **Category:** `background_jobs`
- **original_text (Report A):**
  > Your “outbox worker” (background processor) is defined in compose, but is not running right now.
  > backend `/health/ready` returns `outbox_processor: not running`.
- **Impact:** Durable event processing stalls; workflows relying on outbox never complete.
- **Evidence:** `/health/ready` evidence included in report.
- **Suggested fix (Report A):** “Bring up the outbox worker … and make `/health/ready` green.”
- **Verification (Report A):** `/health/ready` indicates processor running (implicit).

### A-ATOM-009 → ZK-AUD-0005
- **Finding Signature:** `transition-payload-mismatch`
- **Category:** `ui_backend_wiring`
- **original_text (Report A):**
  > Deal stage transitions from UI: UI sends `{to_stage, approved_by}` but backend expects `{new_stage}`.
  > Stage transitions fail from the UI (HTTP 400 validation error).
- **Impact:** UI stage transitions fail; operators must use backend-only calls.
- **Evidence:** Explicit request/response mismatch and HTTP 400 cited.
- **Suggested fix (Report A):** “Fix the stage transition contract … update UI to send `new_stage` or add a route handler that translates UI → backend contract.”
- **Verification (Report A):** Not provided; verify UI transitions return 2xx and stage updates persist.

### A-ATOM-010 → ZK-AUD-0004
- **Finding Signature:** `multiple-stage-models`
- **Category:** `data_flow`
- **original_text (Report A):**
  > **Multiple, conflicting stage models across UI + backend**
  > Sorting, filtering, transitions, and “what stage means what” is inconsistent everywhere.
- **Impact:** Deals can’t be reliably filtered/sorted/transitioned; analytics and automation are unreliable.
- **Evidence:** Specific file locations cited in Report A (UI types, backend workflow, UI create form).
- **Suggested fix (Report A):** “Pick one canonical deal stage taxonomy and enforce it everywhere.”
- **Verification (Report A):** Not provided; verify one taxonomy is used across UI/backend.

### A-ATOM-011 → ZK-AUD-0006
- **Finding Signature:** `threads-endpoints-500`
- **Category:** `agent_api`
- **original_text (Report A):**
  > Backend `/api/threads` is wired to a DB URL env var that is not set + schema not present
  > Runtime: backend container does not set `ZAKOPS_DATABASE_URL`; endpoints 500 on use.
  > Postgres schema lacks `zakops.agent_threads` migration/table.
- **Impact:** Agent run streaming + tool approval workflows (Dashboard agent client) are dead.
- **Evidence:** Env var mismatch + missing tables cited.
- **Suggested fix (Report A):** “Delete or fully implement `/api/threads` … add migrations … set it to use `DATABASE_URL` … or remove endpoints + remove dashboard agentClient usage.”
- **Verification (Report A):** Not provided; verify `/api/threads/*` no longer 500 and UI works.

### A-ATOM-012 → ZK-AUD-0008
- **Finding Signature:** `search-actions-global-500`
- **Category:** `endpoints`
- **original_text (Report A):**
  > `/api/search/actions` and `/api/search/global` throw 500.
- **Impact:** Search features crash; UI search is unreliable/unusable.
- **Evidence:** Root cause described as schema mismatch (`inputs`, `risk_level` vs JSON).
- **Suggested fix (Report A):** “Fix backend search … to match the real `zakops.actions` schema.”
- **Verification (Report A):** Not provided; verify endpoints return 200.

### A-ATOM-013 → ZK-AUD-0009
- **Finding Signature:** `llm-integrations-placeholders`
- **Category:** `env_config`
- **original_text (Report A):**
  > `OPENAI_API_BASE=http://localhost:8000/v1` (wrong inside container; should use a reachable host/alias)
  > `LANGSMITH_API_KEY` empty
  > Gmail OAuth client id/secret placeholders
  > `TOKEN_ENCRYPTION_KEY` empty
- **Impact:** Backend AI invocation endpoints error; email OAuth cannot be completed securely.
- **Evidence:** Explicit env issues listed.
- **Suggested fix (Report A):** Set correct base URL and real keys; configure OAuth securely (implied).
- **Verification (Report A):** Not provided; verify AI endpoints return success and OAuth flow completes.

### A-ATOM-014 → ZK-AUD-0013
- **Finding Signature:** `execute-proposal-501`
- **Category:** `endpoints`
- **original_text (Report A):**
  > Chat proposal execution is explicitly unimplemented
  > Break: always returns 501 (placeholder).
- **Impact:** Approving a proposal does not trigger execution; “approve from chat” workflow is blocked.
- **Evidence:** Explicit 501 placeholder statement.
- **Suggested fix (Report A):** “Chat proposals … returns HTTP 501 placeholder …” implies implementing or removing it.
- **Verification (Report A):** Not provided; verify endpoint returns 2xx and executes.

### A-ATOM-015 → ZK-AUD-0003
- **Finding Signature:** `mock-agent-activity-endpoint`
- **Category:** `ui_backend_wiring`
- **original_text (Report A):**
  > Dashboard agent activity endpoint returns mock events/runs: `zakops-agent-api/apps/dashboard/src/app/api/agent/activity/route.ts`
- **Impact:** UI can look “alive” even when no agent runs exist.
- **Evidence:** Exact file path cited.
- **Suggested fix (Report A):** Fix plan: remove/mock-gate endpoints returning fake agent activity or label as demo mode.
- **Verification (Report A):** Not provided; verify agent activity reflects real runs.

### A-ATOM-016 → ZK-AUD-0003
- **Finding Signature:** `dashboard-fail-open-empty-mock`
- **Category:** `reliability`
- **original_text (Report A):**
  > Several Dashboard API routes “fail open” and return empty/mock data on backend errors (pipeline, checkpoints, delete action, etc.)
- **Impact:** Failures are hidden; operator cannot distinguish outage from “empty workload.”
- **Evidence:** Explicit claim of fail-open behavior.
- **Suggested fix (Report A):** “Remove/mock-gate … or clearly label them as ‘demo mode’.”
- **Verification (Report A):** Not provided; verify backend down shows explicit error.

### A-ATOM-017 → ZK-AUD-0014
- **Finding Signature:** `agent-invoke-deal-id-uuid`
- **Category:** `endpoints`
- **original_text (Report A):**
  > UI: chat route fallback uses `/api/agent/invoke`
  > Break: backend expects UUID deal_id; real deal ids are strings like `DL-0012`.
- **Impact:** Chat fallback fails for real deals; agent invocation path is unreliable.
- **Evidence:** Explicit contract mismatch and example deal ID format.
- **Suggested fix (Report A):** Not explicitly provided; implied: accept real deal ID format.
- **Verification (Report A):** Not provided; verify endpoint accepts `DL-####` deal IDs.

---

## Appendix B — Report B → Master ID mapping (Atomic Extraction)

> Each item below is a single “atomic finding” extracted from Report B, with the required Phase 1 fields and a mapping to a master finding ID.

### B-ATOM-001 → ZK-AUD-0001
- **Finding Signature:** `two-competing-platforms`
- **Category:** `architecture`
- **original_text (Report B):**
  > There are **two separate "ZakOps" systems** running simultaneously:
- **Impact:** Confusion about authoritative services; critical workflows may depend on the legacy stack while docs describe the monorepo.
- **Evidence:** Report B cites legacy `/home/zaks/Zaks-llm/` (port 8080) and monorepo stack ports `8091/8095/3003`.
- **Suggested fix (Report B):** “Decommission legacy Zaks-llm zakops-api … or clearly document its role.”
- **Verification (Report B):** Not explicitly provided; verify by stopping legacy stack and ensuring workflows still function (or documenting dependency).

### B-ATOM-002 → ZK-AUD-0010
- **Finding Signature:** `filesystem-to-quarantine-db-bridge-missing`
- **Category:** `data_flow`
- **original_text (Report B):**
  > ✗ BREAK: No automatic bridge from filesystem → quarantine_items DB table
- **Impact:** Email intake does not create actionable quarantine items in Postgres; operator cannot triage new items reliably.
- **Evidence:** Report B pipeline description from `sync_acquisition_emails.py` → DataRoom → missing bridge to DB.
- **Suggested fix (Report B):** “Build email→quarantine bridge… Script or endpoint that reads DataRoom inbound files and creates quarantine_items in PostgreSQL.”
- **Verification (Report B):** Send inbound email/file and confirm quarantine_items are created automatically.

### B-ATOM-003 → ZK-AUD-0010
- **Finding Signature:** `dataroom-not-mounted-into-backend`
- **Category:** `env_config`
- **original_text (Report B):**
  > **DataRoom mount not in monorepo docker-compose**
- **Impact:** Backend in docker cannot access `/home/zaks/DataRoom`, preventing filesystem-first ingestion approaches.
- **Evidence:** Report B: `deployments/docker/docker-compose.yml` missing DataRoom mounts; legacy compose mounts it but monorepo compose doesn’t.
- **Suggested fix (Report B):** “Add DataRoom volume mount to monorepo docker-compose backend.”
- **Verification (Report B):** Backend container can read DataRoom path; bridge job succeeds.

### B-ATOM-004 → ZK-AUD-0002
- **Finding Signature:** `compose-port-collision-8091`
- **Category:** `env_config`
- **original_text (Report B):**
  > **Port conflict: both backend services claim 8091**
- **Impact:** Cannot run full backend stack from compose; orchestration vs lifecycle collide.
- **Evidence:** Report B cites `deployments/docker/docker-compose.yml` lines 37 and 52 mapping both services to `8091:8091`.
- **Suggested fix (Report B):** “Fix docker-compose port conflict (orchestration should be 9200:9200, not 8091:8091).”
- **Verification (Report B):** Compose starts both services without bind errors; both ports respond.

### B-ATOM-005 → ZK-AUD-0002
- **Finding Signature:** `port-defaults-drift-8090-8091`
- **Category:** `env_config`
- **original_text (Report B):**
  > `.env.example` says `DEAL_LIFECYCLE_API_PORT=8090`. Docker-compose maps 8091:8091. `Dockerfile.api` defaults to 8090. `scripts/dev.sh` uses 8091. The runtime is 8091 but defaults conflict.
- **Impact:** Developers following `.env.example` run the wrong port; dashboard/client wiring breaks.
- **Evidence:** Explicit file/config references in Report B.
- **Suggested fix (Report B):** “Fix `.env.example` port from 8090 to 8091.”
- **Verification (Report B):** Fresh setup using `.env.example` works without manual port edits.

### B-ATOM-006 → ZK-AUD-0016
- **Finding Signature:** `agent-api-default-db-food-order-db`
- **Category:** `db`
- **original_text (Report B):**
  > **Agent API default DB is `food_order_db`**
- **Impact:** If `.env.development` is missing/not loaded, agent connects to the wrong DB silently.
- **Evidence:** Report B cites `apps/agent-api/app/core/config.py:180`.
- **Suggested fix (Report B):** “Fix agent-api default DB from `food_order_db` to `zakops_agent`.”
- **Verification (Report B):** Agent fails fast or connects to correct DB when env is missing.

### B-ATOM-007 → ZK-AUD-0016
- **Finding Signature:** `multi-db-sprawl-no-migration-certainty`
- **Category:** `db`
- **original_text (Report B):**
  > **There is no single migration command that sets up all schemas correctly.**
- **Impact:** Schema drift and data fragmentation; services may write to different DBs/schemas.
- **Evidence:** Report B lists DBs: `zakops`, `zakops_agent`, `food_order_db`, `crawlrag`, SQLite in DataRoom.
- **Suggested fix (Report B):** “Unify database strategy: One PostgreSQL instance, one `zakops` database…”
- **Verification (Report B):** Fresh install via one command creates all required schemas and services see the same data.

### B-ATOM-008 → ZK-AUD-0015
- **Finding Signature:** `redis-present-unused`
- **Category:** `architecture`
- **original_text (Report B):**
  > **Redis runs but is NOT actually used in application code.**
- **Impact:** Misleading architecture claims + wasted resources; potential false assumptions about sessions/queues.
- **Evidence:** Report B states no Redis client usage in Python backend/agent code.
- **Suggested fix (Report B):** “Remove Redis from docker-compose (or actually implement Redis caching).”
- **Verification (Report B):** Removing Redis doesn’t break runtime (or Redis features are demonstrably active).

### B-ATOM-009 → ZK-AUD-0002
- **Finding Signature:** `agent-client-defaults-to-9200`
- **Category:** `ui_backend_wiring`
- **original_text (Report B):**
  > **`agent-client.ts` defaults to port 9200**
- **Impact:** If `NEXT_PUBLIC_API_URL` is missing, dashboard calls the wrong port, causing silent failures.
- **Evidence:** Report B cites `apps/dashboard/src/lib/agent-client.ts:26`.
- **Suggested fix (Report B):** “Fix `agent-client.ts` default port from 9200 to 8091.”
- **Verification (Report B):** Dashboard works even without `NEXT_PUBLIC_API_URL` (or fails loudly with guidance).

### B-ATOM-010 → ZK-AUD-0017
- **Finding Signature:** `auth-disabled-default`
- **Category:** `auth`
- **original_text (Report B):**
  > **Auth disabled by default everywhere** … Backend: `AUTH_REQUIRED=false`, Agent: `AGENT_JWT_ENFORCE=false`
- **Impact:** Endpoints accessible without authentication; production risk if not gated.
- **Evidence:** Report B also notes a mock dev operator is created when auth is disabled.
- **Suggested fix (Report B):** “Enable AUTH_REQUIRED=true …”
- **Verification (Report B):** Unauthenticated calls are blocked in prod profile.

### B-ATOM-011 → ZK-AUD-0007
- **Finding Signature:** `approvals-sql-functions-not-applied`
- **Category:** `db`
- **original_text (Report B):**
  > PL/pgSQL functions (`cleanup_expired_approvals`, `reclaim_stale_claims`) are only in the SQL file and must be manually applied.
- **Impact:** HITL crash recovery may fail; approvals can get stuck.
- **Evidence:** Report B cites `apps/agent-api/migrations/001_approvals.sql`.
- **Suggested fix (Report B):** “Run agent-api migration SQL (001_approvals.sql) against actual database.”
- **Verification (Report B):** Functions exist and reclaim stale claims works.

### B-ATOM-012 → ZK-AUD-0018
- **Finding Signature:** `dashboard-service-token-hardcoded`
- **Category:** `security`
- **original_text (Report B):**
  > Token `k-bG0Us8LHBso4S4OnjqVOXkCNR_C8smNqtflzukWpo` is in the compose file and `.env.local`.
- **Impact:** Secret leakage and reuse risk; difficult rotation.
- **Evidence:** Report B cites `deployments/docker/docker-compose.yml:20,77`.
- **Suggested fix (Report B):** “Remove `DASHBOARD_SERVICE_TOKEN` from docker-compose, use env-only.”
- **Verification (Report B):** Token no longer in tracked files and services still authenticate.

### B-ATOM-013 → ZK-AUD-0019
- **Finding Signature:** `observability-theoretical`
- **Category:** `logging_observability`
- **original_text (Report B):**
  > The Observability Stack Is Theoretical
- **Impact:** Reduced operational visibility; dashboards may not reflect real service health.
- **Evidence:** Report B references `ops/observability/` and warns Prometheus targets may not expose `/metrics`.
- **Suggested fix (Report B):** “Verify and fix observability stack… Ensure Prometheus scrapes real metrics…”
- **Verification (Report B):** Dashboards populate with live metrics and targets are up.

### B-ATOM-014 → ZK-AUD-0009
- **Finding Signature:** `vllm-fallback-all-providers-failed`
- **Category:** `reliability`
- **original_text (Report B):**
  > ✗ BREAK: If vLLM is down, circular fallback tries OpenAI (needs API key)
- **Impact:** Chat/tools/executors fail unpredictably depending on provider availability and credentials.
- **Evidence:** Report B describes the 4-hop chain and the failure mode “All providers failed”.
- **Suggested fix (Report B):** Not explicitly detailed; implied: configure providers and fallback intentionally.
- **Verification (Report B):** vLLM-down scenario produces deterministic behavior.

### B-ATOM-015 → ZK-AUD-0012
- **Finding Signature:** `actions-runner-not-running`
- **Category:** `background_jobs`
- **original_text (Report B):**
  > ✗ BREAK: actions_runner.py must be running as separate process
- **Impact:** Actions remain pending; nothing executes without the worker.
- **Evidence:** Report B explains worker must be started manually in dev or as a compose container.
- **Suggested fix (Report B):** Ensure worker is running as part of the deployment.
- **Verification (Report B):** Create action and observe worker execution.

### B-ATOM-016 → ZK-AUD-0009
- **Finding Signature:** `executors-depend-on-vllm-config`
- **Category:** `reliability`
- **original_text (Report B):**
  > `draft_email`, `generate_loi`, `build_valuation_model` call LLM but depend on vLLM being available and properly configured.
- **Impact:** Executors may appear implemented but fail at runtime due to LLM configuration issues.
- **Evidence:** Executor names and dependency on vLLM stated in Report B.
- **Suggested fix (Report B):** Fix vLLM configuration and dependencies (ties to Tier 1 config fixes).
- **Verification (Report B):** Run executors successfully against configured vLLM.

### B-ATOM-017 → ZK-AUD-0003
- **Finding Signature:** `dashboard-silent-empty-arrays`
- **Category:** `reliability`
- **original_text (Report B):**
  > ✗ BREAK: If backend not running, dashboard silently returns empty arrays (graceful degradation hides failures)
- **Impact:** Operators cannot detect outages from UI; delays response and hides breakages.
- **Evidence:** Report B’s pipeline verdict “Silent failures mask problems.”
- **Suggested fix (Report B):** “Add health indicators to dashboard.”
- **Verification (Report B):** Backend-down scenario shows explicit UI status/error.

### B-ATOM-018 → ZK-AUD-0020
- **Finding Signature:** `gates-chaos-bluegreen-unverified`
- **Category:** `testing`
- **original_text (Report B):**
  > Whether these containers are actually running is unclear
  > Whether they pass is unknown — likely many would fail against current runtime.
- **Impact:** Readiness claims can’t be trusted; outages may go undetected until runtime.
- **Evidence:** Report B references `tools/gates/`, `tools/chaos/`, and `deployments/bluegreen/` as aspirational/unverified.
- **Suggested fix (Report B):** “Run quality gates… fix failures…”
- **Verification (Report B):** Gates/CI are green against the declared standard stack.

### B-ATOM-019 → ZK-AUD-0020
- **Finding Signature:** `doc-tool-count-mismatch`
- **Category:** `docs`
- **original_text (Report B):**
  > **Actually 5 tools:** `duckduckgo_search`, `transition_deal`, `get_deal`, `search_deals`, `list_deals`. V3 says 4, code has 5.
- **Impact:** Documentation is inaccurate; operators/devs may have wrong expectations for agent capabilities.
- **Evidence:** Explicit tool list and mismatch in Report B.
- **Suggested fix (Report B):** Update docs to reflect actual tool count.
- **Verification (Report B):** Docs align with code; tool list matches runtime.

---

## Appendix C — Conflict Register (Contradictions + Resolution Plan)

### C-1: Which backend codebase is authoritative for `:8091`?
- **Report A viewpoint:** Backend serving `:8091` is built from `zakops-backend/`, not `zakops-agent-api/apps/backend/`.
  > the only backend actually serving `:8091` is `zakops-backend/`.
- **Report B viewpoint:** “Backend” is described as part of the monorepo (`/home/zaks/zakops-agent-api/`) with Deal Lifecycle and Orchestration services.
  > It consists of three services in a monorepo (`zakops-agent-api`)
- **Resolution / NEEDS VERIFICATION:** Determine which container/process is serving `:8091` in the intended standard stack (inspect container image/source, compose file in use). Then update docs and wiring accordingly.

### C-2: HITL approvals “work” vs “dead” end-to-end
- **Report A viewpoint:** Dashboard approvals/runs UX is dead because backend `/api/threads/*` returns 500 due to DB env/table issues.
  > Agent “runs/approvals” UX … calls Backend `/api/threads/*`, but those endpoints 500.
- **Report B viewpoint:** HITL approval flow is “best-implemented” and “works” if approval SQL functions are applied.
  > **Verdict:** Best-implemented feature. Works if migration SQL is applied.
- **Resolution / NEEDS VERIFICATION:** Clarify which approvals system the UI should use (backend `/api/threads` vs agent-api approvals). Confirm DB migrations/functions are applied, then wire UI to the working system.

### C-3: Redis role (present vs used)
- **Report A viewpoint:** Redis is listed as part of the running stack and described as part of the backend backing services.
  > **Redis (ZakOps)**: `localhost:6379` (Docker)
- **Report B viewpoint:** Redis is not actually used in application code; docs claiming it is used are false.
  > Redis runs but is NOT actually used in application code.
- **Resolution / NEEDS VERIFICATION:** Code audit for Redis client usage; decide whether to remove Redis or implement it intentionally and update docs.
