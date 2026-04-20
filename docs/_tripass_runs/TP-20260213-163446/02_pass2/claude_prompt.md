# TriPass — Pass 2: Cross-Review and Deduplication

## Agent Identity
**Agent**: CLAUDE
**Run ID**: TP-20260213-163446
**Pipeline Mode**: forensic
**Timestamp**: 2026-02-13T17:04:20Z

---

## Mission (Original)

# FORENSIC AUDIT MISSION — INTAKE → QUARANTINE → DEALS (SOURCE-OF-TRUTH + REAL-LIFE DATA PIPELINE)

## Why this audit exists
We've made major progress aligning the system, but we have NOT recently audited the "real-life data" entry point:
- How opportunities enter the system (email/MCP/watchers/ingestion)
- Where Quarantine items are persisted
- Whether Quarantine → approval → Deals is tight end-to-end
- Whether we currently have split-brain behavior (multiple DBs / multiple truth paths)
This audit is the last major puzzle piece before we scale real usage.

## Non-negotiable constraints
- This is FORENSICS ONLY: INVESTIGATE → REPORT → STOP.
- Do NOT implement fixes in this mission.
- Do NOT delete data.
- Do NOT run destructive DB commands (no UPDATE/DELETE).
- Provide evidence for every claim (file:line refs, env vars, curl, DB SELECTs, logs).

## Primary Objective
Produce an evidence-based "Ground Truth" report for:
1) Canonical Source-of-Truth Database (what it is, who reads/writes)
2) Real-life data ingestion pipeline into Quarantine (what exists today vs what's imagined)
3) Tightness of workflow: Quarantine → approve → Deals (and everything that should happen downstream)
4) Gaps, misalignments, and risks vs world-class/industry standard
5) A prioritized set of remediation recommendations (still no implementation here)

---

# Scope
Focus areas (must all be covered):
A) Intake layer:
- MCP server integration (email login / auth)
- Email watching / polling / webhook logic
- Email parsing/classification → opportunity extraction
- De-duplication {{MISSION_DESCRIPTION}} idempotency (avoid duplicate opportunities)
- Rate limiting / backoff / failure handling

B) Quarantine layer:
- Where Quarantine data lives (DB tables, schemas)
- What fields define a "Quarantine item"
- How Quarantine items are surfaced in UI
- Delete/clear/approve actions and their backend paths

C) Promotion layer (approval):
- What happens when user approves a quarantine item
- How it becomes a Deal (schema mapping / stage mapping)
- Which services are involved (dashboard → backend → agent → DB)
- Event logs / audit logs / traceability

D) Deal lifecycle integrity:
- After promotion: do stages, notes, tasks, RAG attachments, email association actually link to the same deal record?
- Can the agent see the same deals the UI sees?
- Are there any split-brain stores still in play?

---

# Deliverables (WSL paths, Markdown only)
Write your report here:
- /home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md

Also write an "Evidence Pack Index" here:
- /home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_EVIDENCE_INDEX.md

Do NOT overwrite existing unrelated docs.

---

# Required report structure (must follow)
## 1) AGENT IDENTITY
- agent_name:
- run_id:
- timestamp:
- repo_revision (git hash if available):
- environment assumptions:

## 2) Executive Summary (Plain English)
- What is the real intake pipeline today?
- What is the real source-of-truth DB today?
- Is Quarantine → Deals truly wired end-to-end today?
- Biggest risks / mismatches

## 3) System Reality Map (Evidence-based)
### 3.1 Source-of-Truth DB determination
Answer with proof:
- Which DB is canonical for Deals and Quarantine?
- Which services read/write which DB(s)?
- Are there multiple DB URLs configured (dashboard vs backend vs agent)?
- Where are the env vars set (files + line refs)?

Include:
- "DB Topology Diagram" (text diagram is fine)
- "Tables of record" list (deals, quarantine, events, notes, etc.)

### 3.2 Intake pipeline: email/MCP → quarantine
Provide the end-to-end path:
- Entry point (MCP server? scheduled job? webhook? manual import?)
- Auth mechanism (tokens? OAuth? stored credentials? where?)
- Extraction {{MISSION_DESCRIPTION}} normalization logic (where in code)
- De-duplication strategy (message-id? hash? thread id?)
- Failure {{MISSION_DESCRIPTION}} retry behavior
- Observability: how do we know ingestion is running?

### 3.3 Quarantine operations: list/create/delete/approve
Map each:
- UI action → backend route → service function → DB ops
- Confirm actual routes exist and work (curl + server logs)
- Confirm DB writes are happening in the canonical DB

### 3.4 Approval flow: quarantine → deal
Prove:
- what transform/mapping happens (fields, stage)
- where deal is written
- what events/logs are emitted
- whether agent and dashboard see the same result

## 4) Forensic Questions Checklist (Answer ALL)
You must answer each of these with evidence:

### A. Data Truth {{MISSION_DESCRIPTION}} DB Split-Brain
1) Where exactly is the canonical "deal truth" stored?
2) Do agent API, backend API, and dashboard read the same DB connection string?
3) Are there multiple schemas or separate DBs for "agent memory" vs "deal truth"?
4) Can a deal exist in UI but be invisible to the agent (and why)?
5) Are there any filesystem-based stores, legacy sqlite, or cached snapshots still referenced?

### B. Intake / MCP / Email
6) What MCP server(s) exist in the repo and how are they configured?
7) Is the email integration active or stubbed?
8) What mechanism triggers ingestion (polling schedule, webhook, manual)?
9) What credentials are required and where are they stored?
10) Is there an onboarding UI for email config, and does it truly write config used by ingestion?
11) What happens if auth expires — is it detected and surfaced to UI?
12) How do we prevent duplicate opportunities from repeated emails / threads?
13) How do we associate emails to an existing Deal after it's promoted?
14) What is the attachment handling strategy (download, parse, store, link)?

### C. Quarantine Integrity
15) What fields constitute a quarantine item and how do we validate them?
16) Are Quarantine "delete/clear" endpoints real, or placeholders?
17) When user approves, does the item disappear from Quarantine reliably?
18) What audit log is created for approval/rejection?
19) Does "approve" create a deal in the same DB the dashboard reads from?

### D. Deal Lifecycle Tightness
20) After promotion, do stage changes persist to the same record everyone reads?
21) Are there mismatched stage taxonomies (different strings across systems)?
22) Are there any "shadow pipelines" (legacy endpoints/ports) still referenced?
23) Do RAG/embeddings attach to the correct deal id consistently?
24) Can we trace one deal end-to-end across logs/events?

### E. Observability {{MISSION_DESCRIPTION}} "World-class" Standards
25) Where do ingestion logs go and are they correlated with a deal id or thread id?
26) Is there a single correlation id propagated across dashboard → backend → agent → DB?
27) What metrics/alerts exist (queue lag, ingestion failure, auth failure, duplicates)?
28) What are the security risks (token storage, PII in logs, least privilege)?
29) What is the disaster scenario (email ingestion loops, duplicate floods) and how is it prevented?

## 5) Gap {{MISSION_DESCRIPTION}} Misalignment List (Reality vs Desired)
Create a table:
- Gap ID
- "Expected behavior"
- "Current reality"
- Evidence
- Risk level (P0–P3)
- Root cause hypothesis
- How to verify further (commands)

## 6) Recommendations (Permanent, Industry-standard, Best-fit)
For each gap (especially P0/P1), propose:
- Permanent fix approach (tailored to this architecture)
- Best practice / industry standard
- Why it fits this system specifically
- "Never again" enforcement: gates/tests/invariants/monitoring

Must include "systemic improvements," not only patches:
- canonical data ownership model
- ingestion idempotency contract
- audit log + event model
- configuration UX → actual runtime config wiring
- end-to-end traceability strategy

## 7) Minimum Proof Steps (Repro + Validation)
List exact steps to validate the pipeline in a real-ish way WITHOUT destructive actions:
- How to simulate ingestion safely (dry-run mode or sample email payload)
- How to confirm quarantine creation and promotion
- How to prove DB truth alignment

## 8) STOP
Do not implement fixes. End the report with:
- "Audit complete"
- "Ready for remediation mission(s)"

---

# Evidence Requirements (non-negotiable)
For every major claim, include at least one of:
- file path + line range
- env var name + where set
- curl commands + outputs
- DB SELECT queries + outputs
- log excerpts + location

If you cannot prove something, mark:
NEEDS VERIFICATION
and list exact commands to prove it.

---

# Bonus "What else is broken?" sweep (mandatory)
After completing the main audit, do a second sweep using contrarian thinking:
- assume the ingestion pipeline is partially wired to legacy components
- assume UI config does not drive runtime config
- assume multiple DBs exist and are accidentally used
List the top 10 failure patterns most likely in this system and how to detect each with proof.

---

# Repository Locations
- Monorepo (Dashboard + Agent API): /home/zaks/zakops-agent-api
- Backend API: /home/zaks/zakops-backend
- RAG/LLM Service: /home/zaks/Zaks-llm
- Bookkeeping: /home/zaks/bookkeeping

# Database Information
- zakops DB (schema: zakops, user: zakops) — Backend primary
- zakops_agent DB (schema: public, user: agent) — Agent API
- crawlrag DB (schema: public) — RAG service

# Service Ports
- Dashboard: 3003
- Backend API: 8091
- Agent API: 8095
- RAG: 8052
- MCP Server: 9100
- Port 8090: DECOMMISSIONED (never use)

---

## Pass 1 Reports

You have access to all three Pass 1 reports:

### Report A (CLAUDE)
Acknowledged. All four agents finished and their findings are in the report. Nothing further to do — Pass 1 is complete.

### Report B (GEMINI)
# Pass 1 Report — GEMINI
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T16:34:47Z

## PRIMARY FINDINGS

### Finding 1: Broken Email Ingestion Pipeline (Missing Dependency)
**Root Cause:** The `actions_runner.py` worker relies on an external `email_ingestion` package that is missing from the repository. The import fails, causing the ingestion logic to be skipped/disabled. No alternative native polling implementation exists.
**Fix Approach:** Implement a native `EmailPoller` worker within `zakops-backend/src/workers/` that uses the existing `email_accounts` table and `EmailService` to poll IMAP/Gmail API and create quarantine items.
**Industry Standard:** Self-contained worker process with explicit dependencies (e.g., `apscheduler` + `google-auth`).
**System Fit:** The backend already has the necessary infrastructure (asyncpg, EmailService, Pydantic models). Adding a dedicated worker is the idiomatic solution.
**Enforcement:** Add an integration test that simulates email arrival and verifies a quarantine item is created.

### Finding 2: Missing Correlation ID in Quarantine
**Root Cause:** The `zakops.quarantine_items` table (defined in `001_base_tables.sql`) lacks a `correlation_id` column. Traceability breaks at the ingestion point; a new ID is generated only when the deal is created or approved.
**Fix Approach:** Add `correlation_id UUID` column to `quarantine_items`. Generate this ID at the ingestion source (webhook/poller) and propagate it through `process_quarantine` to the `deal_created` event.
**Industry Standard:** Distributed Tracing (OpenTelemetry/W3C Trace Context).
**System Fit:** The rest of the system (Deals, Actions) already uses `correlation_id`. This aligns Quarantine with the established pattern.
**Enforcement:** API tests should verify that `X-Correlation-ID` header is respected and persisted.

### Finding 3: Missing Database Constraint on Quarantine Status
**Root Cause:** The `status` column in `zakops.quarantine_items` is a plain `VARCHAR(50)` without a `CHECK` constraint. While the application code (Pydantic) validates input, the database layer allows invalid states.
**Fix Approach:** Add a migration: `ALTER TABLE zakops.quarantine_items ADD CONSTRAINT chk_quarantine_status CHECK (status IN ('pending', 'approved', 'rejected', 'hidden'))`.
**Industry Standard:** Database-level integrity constraints (Defense in Depth).
**System Fit:** Other tables like `deals` and `actions` use constraints/enums. This brings Quarantine to parity.
**Enforcement:** Database migration validation script.

### Finding 4: Weak Deduplication Strategy
**Root Cause:** Deduplication relies solely on exact `message_id` matches. Forwarded emails or replies in the same thread (which have new `message_ids`) will create duplicate quarantine items instead of updating an existing one or being threaded.
**Fix Approach:** Implement content-hash based dedI have completed the forensic audit and generated the required reports.

**Summary of Deliverables:**
1.  **Forensic Report:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md`
    *   Confirmed broken automated ingestion (missing `email_ingestion` package).
    *   Confirmed `zakops` DB as the single source of truth (no split-brain).
    *   Confirmed atomic Quarantine → Deal promotion.
    *   Identified gaps in correlation and constraints.
2.  **Evidence Index:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_EVIDENCE_INDEX.md`
    *   Maps findings to specific file paths and lines.
3.  **TriPass Report:** `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1/gemini_report.md`
    *   Structured findings for the multi-agent review process.

**Mission Status:** Complete.
**Ready for:** Pass 2 (Cross-Review) and Remediation.

I will now exit.
The forensic audit of the **Intake → Quarantine → Deals** pipeline is complete.

I have produced the following artifacts:

1.  **Forensic Report:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md`
    *   **Key Finding (P0):** Automated email ingestion is **broken** due to a missing external `email_ingestion` package. The system relies on manual API calls.
    *   **Architecture (Good):** The `zakops` database is the undisputed canonical source of truth for Deals and Quarantine items. The Agent DB (`zakops_agent`) correctly stores only agent memory, preventing split-brain scenarios.
    *   **Logic (Good):** The `process_quarantine` API endpoint handles deal creation transactionally, ensuring atomicity.
    *   **Risks (P2):** Missing `correlation_id` breaks end-to-end traceability from ingestion to deal creation. Missing DB constraints on quarantine status allow invalid states.

2.  **Evidence Index:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_EVIDENCE_INDEX.md`
    *   Maps every finding to specific file paths and line numbers within the codebase.

3.  **TriPass Report:** `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1/gemini_report.md`
    *   Structured findings for the multi-agent review process, including 4 primary findings and 3 adjacent observations.

**Recommendation:** Prioritize the implementation of a native email polling worker (`src/workers/email_poller.py`) to restore automated ingestion functionality, and add the missing `correlation_id` column to the `quarantine_items` table.

### Report C (CODEX)
Unable to write the requested files because this session is filesystem read-only. Write attempts returned `Permission denied` for `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1` and `/home/zaks/bookkeeping/docs`.

Below is the exact markdown content for each target file.

### `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1/codex_report.md`
```markdown
# Pass 1 Report — CODEX
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T16:34:47Z

## PRIMARY FINDINGS

### Finding 1: Canonical DB intent exists, but deployment/config drift can still create split-brain
**Root Cause:** Backend enforces canonical `zakops` DB at startup (`zakops-backend/src/api/orchestration/main.py:372`, `zakops-backend/src/api/orchestration/main.py:395`, `zakops-backend/src/api/orchestration/main.py:405`), but agent-side deployment config points `DATABASE_URL` to `zakops` instead of expected `zakops_agent` (`zakops-agent-api/deployments/docker/docker-compose.yml:17`) while topology contract expects `zakops_agent` (`zakops-agent-api/packages/contracts/runtime.topology.json:20`) and agent `.env.example` also expects `zakops_agent` (`zakops-agent-api/apps/agent-api/.env.example:47`).
**Fix Approach:** Enforce per-service DB ownership contract in CI/CD and runtime startup checks for agent and backend.
**Industry Standard:** Explicit bounded-context data ownership with environment contract validation.
**System Fit:** This architecture intentionally separates backend deal truth and agent operational state; config drift is the main failure mode.
**Enforcement:** Add a startup gate in agent API to reject `DATABASE_URL` dbname != `zakops_agent`; add CI policy test comparing compose/env/topology contract.

### Finding 2: Real intake automation into Quarantine is not proven; pipeline appears partially imagined
**Root Cause:** Backend has a bridge endpoint documented for `email_ingestion` (`zakops-backend/src/api/orchestration/main.py:1488`, `zakops-backend/src/api/orchestration/main.py:1491`), but `email_ingestion` package directory is missing while imports remain (`zakops-backend/src/workers/actions_runner.py:45`, `zakops-backend/src/core/chat_orchestrator.py:45`). No webhook/polling scheduler for “inbox -> quarantine” was found in active API/email integration paths.
**Fix Approach:** Implement one explicit ingestion runner (polling/webhook) that writes only through canonical backend API or DB service layer.
**Industry Standard:** Single ingestion control plane with idempotent message processing and explicit run ledger.
**System Fit:** Existing email OAuth and thread APIs can remain; missing piece is deterministic ingestion orchestration.
**Enforcement:** Add integration test proving new email message creates exactly one quarantine item; add health endpoint for ingestion loop heartbeat and lag.

### Finding 3: Quarantine approval bypasses lifecycle transition/outbox pathways
**Root Cause:** Approve flow can directly `INSERT` deal with stage `inbound` (`zakops-backend/src/api/orchestration/main.py:1648`, `zakops-backend/src/api/orchestration/main.py:1659`) and records only `deal_created` (`zakops-backend/src/api/orchestration/main.py:1672`) instead of going through workflow transition engine which writes transition ledger and outbox (`zakops-backend/src/core/deals/workflow.py:227`, `zakops-backend/src/core/deals/workflow.py:248`, `zakops-backend/src/core/deals/workflow.py:277`).
**Fix Approach:** Route promotion through a single domain service that creates deal + emits complete lifecycle/outbox artifacts.
**Industry Standard:** “One write path per aggregate” + transactional outbox for side effects.
**System Fit:** Prevents inconsistencies between deals created from API vs quarantine promotion.
**Enforcement:** Contract test: approving quarantine must produce `deal_created`, transition ledger entry, and outbox message.

### Finding 4: Quarantine dedupe and idempotency controls are incomplete
**Root Cause:** Quarantine create dedupes via app-level pre-select on `message_id` (`zakops-backend/src/api/orchestration/main.py:1508`) without DB unique constraint on `zakops.quarantine_items.message_id` (table definition has no unique constraint: `zakops-backend/db/init/001_base_tables.sql:217`). Idempotency middleware reads/writes unqualified `idempotency_keys` (`zakops-backend/src/api/shared/middleware/idempotency.py:85`, `zakops-backend/src/api/shared/middleware/idempotency.py:127`) while table is created as `zakops.idempotency_keys` (`zakops-backend/db/migrations/001_foundation_tables.sql:114`), and on DB error middleware bypasses idempotency (`zakops-backend/src/api/shared/middleware/idempotency.py:147`).
**Fix Approach:** Add DB-level unique index for quarantine message identity and fix schema-qualified idempotency queries.
**Industry Standard:** Idempotency as data invariant, not best-effort middleware.
**System Fit:** Immediate reduction of duplicate opportunity floods under retries/races.
**Enforcement:** Migration adds unique index; chaos test with concurrent duplicate POSTs must return one record + cached responses.

### Finding 5: MCP approve/reject contract is broken against backend routes
**Root Cause:** MCP server posts to `/api/quarantine/{item_id}/review` (`zakops-backend/mcp_server/server.py:311`, `zakops-backend/mcp_server/server.py:341`), but backend exposes `/process` (`zakops-backend/src/api/orchestration/main.py:1591`) and no `/review` route was found.
**Fix Approach:** Align MCP tool endpoint path and payload contract with backend OpenAPI.
**Industry Standard:** Contract-driven integration tests between tool server and API.
**System Fit:** Prevents agent/MCP approvals from silently failing while dashboard path works.
**Enforcement:** CI contract test runs MCP tool call against ephemeral backend and asserts 2xx + expected schema.

### Finding 6: Dashboard email configuration UX is not wired to active runtime endpoints
**Root Cause:** Dashboard settings proxy targets `/api/user/email-config` (`zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts:12`, `zakops-agent-api/apps/dashboard/src/app/api/settings/email/test/route.ts:10`), but backend route not found. Onboarding email step simulates OAuth with mock email (`zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:56`, `zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:60`).
**Fix Approach:** Replace simulated onboarding with real OAuth initiation endpoints and persisted account status readback.
**Industry Standard:** Configuration UX must be backed by the same control-plane APIs used in production.
**System Fit:** Eliminates user belief that ingestion is live when it is not.
**Enforcement:** E2E test: connect Gmail -> account appears in `/api/integrations/email/accounts` -> ingestion readiness check green.

### Finding 7: Quarantine UI/backend contract drift (bulk-delete path)
**Root Cause:** Frontend client calls `/api/quarantine/bulk-delete` (`zakops-agent-api/apps/dashboard/src/lib/api.ts:942`), but dashboard API routes only implement `[id]/process`, `[id]/delete`, `health` and no bulk-delete route exists.
**Fix Approach:** Either implement bulk-delete end-to-end or remove/feature-flag client call.
**Industry Standard:** Typed API client generated from live OpenAPI, no orphan endpoints.
**System Fit:** Prevents hidden 404 behavior in operational triage workflows.
**Enforcement:** Route existence lint: every client endpoint must map to server route and backend route.

### Finding 8: Legacy filesystem pipelines remain in active code paths
**Root Cause:** Backend worker and actions still reference DataRoom `.deal-registry` sources (`zakops-backend/src/workers/actions_runner.py:53`, `zakops-backend/src/actions/memory/store.py:15`, `zakops-backend/src/actions/capabilities/email_triage.review_email.v1.yaml:5`), and executors write registry mappings/filesystem artifacts (`zakops-backend/src/actions/executors/email_triage_review_email.py:665`). Separate Zaks-llm API still serves deals/quarantine from `.deal-registry` (`Zaks-llm/src/api/server.py:701`, `Zaks-llm/src/api/server.py:794`).
**Fix Approach:** Fully deprecate filesystem deal/quarantine state paths; keep only canonical DB-backed APIs.
**Industry Standard:** One authoritative operational datastore per aggregate.
**System Fit:** Removes cross-process drift and “looks healthy but reading wrong store” failures.
**Enforcement:** CI grep gate disallowing `.deal-registry` access in production paths.

### Finding 9: Correlation and tracing propagation is inconsistent across layers
**Root Cause:** Dashboard and client both generate correlation IDs (`zakops-agent-api/apps/dashboard/src/middleware.ts:50`, `zakops-agent-api/apps/dashboard/src/lib/api.ts:378`), backend runs both `TraceMiddleware` and `TracingMiddleware` (`zakops-backend/src/api/orchestration/main.py:451`, `zakops-backend/src/api/orchestration/main.py:457`) with differing behavior (`zakops-backend/src/api/shared/middleware/trace.py:91` vs `zakops-backend/src/api/shared/middleware/tracing.py:56`), causing possible correlation churn.
**Fix Approach:** Define single correlation source and propagation policy from edge to DB events.
**Industry Standard:** End-to-end trace context propagation (W3C Trace Context + stable business correlation id).
**System Fit:** Critical for forensic traceability across dashboard/backend/agent/outbox.
**Enforcement:** Request-trace contract test verifies same correlation ID in response headers, logs, and `deal_events.correlation_id`.

### Finding 10: Runtime observability and validation are currently blocked by environment state
**Root Cause:** All target service ports were closed (3003/8091/8095/8052/9100), curl health checks failed connection, docker socket inaccessible, and DB port 5432 closed in this run.
**Fix Approach:** Run controlled validation environment and execute non-destructive proof script.
**Industry Standard:** Continuous verification pipeline with synthetic transactions.
**System Fit:** Needed to move from static code confidence to operational confidence.
**Enforcement:** Nightly forensic smoke pipeline that runs ingestion synthetic, quarantine approve, and cross-service consistency checks.

## ADJACENT OBSERVATIONS
- Retention cleanup updates columns not present in base quarantine table schema (`processed_by`, `processing_action`) at `zakops-backend/src/core/retention/cleanup.py:299`.
- Legacy/decommission artifacts still reference old `:8090` and prior split-brain stack (`zakops-backend/gate_artifacts/phase1/deal_api_contract.json:3`).
- Health router says SSE not implemented (`zakops-backend/src/api/shared/routers/health.py:115`) while SSE stream route exists (`zakops-backend/src/api/shared/routers/events.py:164`).

## SUMMARY
- Total primary findings: 10
- Total adjacent observations: 3
- Confidence level: MEDIUM
- Key recommendation: Establish one explicit ingestion control plane and enforce canonical data ownership contracts at startup and CI boundaries before remediation coding.
```

---

### `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md`
```markdown
## 1) AGENT IDENTITY
- agent_name: CODEX
- run_id: TP-20260213-163446
- timestamp: 2026-02-13T16:34:47Z
- repo_revision (git hash if available):
  - zakops-agent-api: `fc5e39d8f7bfa0ffa1859c8d2b5d914d063dffec`
  - zakops-backend: `444dff682885a7358767aa378759ffc9fbedf609`
  - Zaks-llm: `4dfa4625ac55a62b811e56c58f00fb51e2c053b4`
- environment assumptions:
  - Filesystem is read-only in this run; report files could not be written (`Permission denied`).
  - Services were not running locally on expected ports (3003, 8091, 8095, 8052, 9100).
  - Docker socket access denied; runtime container state could not be queried.
  - DB port 5432 was closed; DB `SELECT` runtime validation is marked `NEEDS VERIFICATION`.
  - No production code was modified.

## 2) Executive Summary (Plain English)
- What is the real intake pipeline today?
  - There is a real Gmail OAuth/account integration and inbox/thread/search/send API surface.
  - There is a backend `/api/quarantine` create bridge intended for an `email_ingestion` pipeline.
  - The actual always-on ingestion loop (watcher/poller/webhook) that feeds quarantine is not proven in active runtime code for this repo state; references exist to `email_ingestion`, but module path is missing.
- What is the real source-of-truth DB today?
  - Backend API treats PostgreSQL `zakops` as canonical for deals/quarantine and enforces it at startup.
  - Agent API has separate DB ownership (`zakops_agent`) by design, but deployment examples include conflicting DB URLs.
  - Legacy filesystem `.deal-registry` stores are still referenced in active code paths, creating shadow-truth risk.
- Is Quarantine → Deals truly wired end-to-end today?
  - Backend endpoints for list/create/delete/process are real and the approve path creates a deal in `zakops.deals` and updates `zakops.quarantine_items`.
  - However, promotion bypasses workflow transition/outbox pathways, and MCP approval currently targets wrong backend route (`/review` vs `/process`).
- Biggest risks / mismatches
  - Intake automation appears incomplete/not verifiably running.
  - Multiple truth paths (canonical DB + filesystem/DataRoom paths + cross-service DB drift).
  - Contract mismatches (MCP route mismatch, dashboard bulk-delete and email-config mismatches).
  - Idempotency/correlation inconsistencies reduce resilience and traceability.

## 3) System Reality Map (Evidence-based)

### 3.1 Source-of-Truth DB determination

#### Which DB is canonical for Deals and Quarantine?
- Canonical backend DB is `zakops`:
  - `zakops-backend/src/api/orchestration/main.py:373` (`CANONICAL_DB_NAME = "zakops"`)
  - startup gate refuses non-canonical DB: `zakops-backend/src/api/orchestration/main.py:395`, `zakops-backend/src/api/orchestration/main.py:405`
  - default DB URL also points to `zakops`: `zakops-backend/src/api/orchestration/main.py:85`

#### Which services read/write which DB(s)?
- Backend API (8091): reads/writes `zakops` tables via asyncpg pool (`zakops-backend/src/api/orchestration/main.py:387`).
- Outbox worker: same backend DB URL (`zakops-backend/docker-compose.yml:106`).
- Agent API (8095): reads/writes DB from `DATABASE_URL` (expected agent DB) and calls backend over HTTP for deal truth:
  - strict `DATABASE_URL` required: `zakops-agent-api/apps/agent-api/app/core/config.py:185`
  - engine built from `DATABASE_URL`: `zakops-agent-api/apps/agent-api/app/services/database.py:42`
  - deal operations via backend client: `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:585`
- RAG REST (8052): separate `crawlrag` DB:
  - `Zaks-llm/src/api/rag_rest_api.py:22`

#### Are there multiple DB URLs configured (dashboard vs backend vs agent)?
- Yes.
  - Backend compose `DATABASE_URL`: `zakops-backend/docker-compose.yml:65`
  - Agent `.env.example`: `zakops-agent`: `zakops-agent-api/apps/agent-api/.env.example:47`
  - Monorepo deploy compose sets agent API `DATABASE_URL` to `zakops`: `zakops-agent-api/deployments/docker/docker-compose.yml:17`
  - Dashboard uses backend URL env (`API_URL/BACKEND_URL`), no direct DB.
    - `zakops-agent-api/apps/dashboard/src/middleware.ts:27`
    - `zakops-agent-api/apps/dashboard/src/lib/backend-fetch.ts:7`

#### Where are env vars set (files + refs)?
- Backend DB env: `zakops-backend/docker-compose.yml:65`, `zakops-backend/docker-compose.yml:66`
- Agent DB env: `zakops-agent-api/apps/agent-api/.env.example:47`
- Agent deploy DB env drift: `zakops-agent-api/deployments/docker/docker-compose.yml:17`
- Runtime topology contract: `zakops-agent-api/packages/contracts/runtime.topology.json:20`

#### DB Topology Diagram
```text
[Dashboard :3003]
   -> HTTP (API_URL/BACKEND_URL)
      -> [Backend API :8091] -> [Postgres zakops]
           tables: deals, quarantine_items, deal_events, actions, email_*
      -> [Agent API :8095] (separate app DB by DATABASE_URL; expected zakops_agent)
           -> HTTP to Backend API for deal truth
      -> [MCP :9100] -> HTTP to Backend API
[RAG REST :8052] -> [Postgres crawlrag]
[Legacy/Zaks-llm APIs] -> filesystem .deal-registry (shadow path)
```

#### Tables of record (canonical backend)
- Deals: `zakops.deals` (`zakops-backend/db/init/001_base_tables.sql:29`)
- Quarantine: `zakops.quarantine_items` (`zakops-backend/db/init/001_base_tables.sql:210`)
- Deal events: `zakops.deal_events` (`zakops-backend/db/init/001_base_tables.sql:107`)
- Deal aliases: `zakops.deal_aliases` (`zakops-backend/db/init/001_base_tables.sql:174`)
- Actions: `zakops.actions` (`zakops-backend/db/init/001_base_tables.sql:64`)
- Email accounts/threads/messages/attachments:
  - `zakops.email_accounts` (`zakops-backend/db/migrations/022_email_integration.sql:11`)
  - `zakops.email_threads` (`zakops-backend/db/migrations/022_email_integration.sql:34`)
  - `zakops.email_messages` (`zakops-backend/db/migrations/022_email_integration.sql:57`)
  - `zakops.email_attachments` (`zakops-backend/db/migrations/022_email_integration.sql:84`)
- Outbox/idempotency:
  - `zakops.outbox` (`zakops-backend/db/migrations/001_foundation_tables.sql:146`)
  - `zakops.idempotency_keys` (`zakops-backend/db/migrations/001_foundation_tables.sql:114`)

### 3.2 Intake pipeline: email/MCP → quarantine

#### Entry point
- Email integration endpoints are real (`/api/integrations/email/*`):
  - router prefix: `zakops-backend/src/api/orchestration/routers/email.py:23`
  - Gmail auth callback/accounts/send/inbox/thread/search/link/unlink are implemented.
- Quarantine ingest bridge endpoint exists:
  - `POST /api/quarantine`: `zakops-backend/src/api/orchestration/main.py:1483`
  - docstring claims `email_ingestion pipeline calls this`: `zakops-backend/src/api/orchestration/main.py:1491`

#### Auth mechanism
- OAuth state token is in-memory with 5-minute TTL:
  - `zakops-backend/src/api/orchestration/routers/email.py:31`
  - expiry check: `zakops-backend/src/api/orchestration/routers/email.py:52`
- Gmail OAuth requires env credentials:
  - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: `zakops-backend/src/core/integrations/email/gmail.py:41`
  - missing creds raises error: `zakops-backend/src/core/integrations/email/gmail.py:69`
- Tokens are stored in DB table `zakops.email_accounts`:
  - schema includes access/refresh token fields: `zakops-backend/db/migrations/022_email_integration.sql:16`

#### Extraction/normalization logic
- Quarantine create model and payload normalization:
  - request model: `zakops-backend/src/api/orchestration/main.py:255`
  - raw_content normalization: `zakops-backend/src/api/orchestration/main.py:1498`

#### Deduplication strategy
- Quarantine create checks existing by `message_id` before insert:
  - `zakops-backend/src/api/orchestration/main.py:1508`
- Email messages table has DB unique constraint on provider `message_id`:
  - `zakops-backend/db/migrations/022_email_integration.sql:73`
- No DB unique constraint found on `zakops.quarantine_items.message_id` in base table:
  - `zakops-backend/db/init/001_base_tables.sql:217`

#### Failure/retry behavior
- Email token refresh behavior exists:
  - `zakops-backend/src/core/integrations/email/service.py:255`
- No explicit intake scheduler/backoff loop was found in active API integration path.
- Action runner has exponential backoff utility:
  - `zakops-backend/src/workers/actions_runner.py:79`

#### Observability
- Quarantine health endpoint exists:
  - `zakops-backend/src/api/orchestration/main.py:1437`
- SSE/event framework exists:
  - stream route: `zakops-backend/src/api/shared/routers/events.py:164`
  - SSE response builder: `zakops-backend/src/api/shared/sse.py:511`
- But health endpoint still says SSE not implemented:
  - `zakops-backend/src/api/shared/routers/health.py:115`

### 3.3 Quarantine operations: list/create/delete/approve

#### UI action → backend route → service function → DB ops

| Operation | UI path | Dashboard API proxy | Backend route | DB operation evidence |
|---|---|---|---|---|
| List | `getQuarantineItems()` usage from UI | `/api/actions/quarantine` | `/api/quarantine` | `SELECT ... FROM zakops.quarantine_items` at `zakops-backend/src/api/orchestration/main.py:1417` |
| Create | No direct dashboard write found | N/A | `/api/quarantine` | `INSERT INTO zakops.quarantine_items` at `zakops-backend/src/api/orchestration/main.py:1533` |
| Delete/Hide | `deleteQuarantineItem()` | `/api/quarantine/{id}/delete` | `/api/quarantine/{item_id}/delete` | soft-hide `status='hidden'` at `zakops-backend/src/api/orchestration/main.py:1576` |
| Approve/Reject | `approveQuarantineItem()` / `rejectQuarantineItem()` | `/api/quarantine/{id}/process` | `/api/quarantine/{item_id}/process` | approve updates item + optional deal insert: `zakops-backend/src/api/orchestration/main.py:1648`, `zakops-backend/src/api/orchestration/main.py:1691` |

#### Route existence and runtime behavior checks
- Static route existence is confirmed in code.
- Runtime HTTP checks failed because services were down.
  - `curl http://127.0.0.1:8091/health` -> connection failure.
- `NEEDS VERIFICATION` commands are provided in Section 7.

#### Canonical DB write confirmation
- Quarantine and deal writes use schema-qualified `zakops.*` SQL in backend route handlers:
  - `zakops-backend/src/api/orchestration/main.py:1533`
  - `zakops-backend/src/api/orchestration/main.py:1650`
  - `zakops-backend/src/api/orchestration/main.py:1691`

### 3.4 Approval flow: quarantine → deal

#### Transform/mapping
- On approve with no `deal_id`:
  - generate deal id: `zakops-backend/src/api/orchestration/main.py:1623`
  - canonical name from subject/sender: `zakops-backend/src/api/orchestration/main.py:1634`
  - stage set `inbound`: `zakops-backend/src/api/orchestration/main.py:1659`
  - metadata includes source `quarantine_approval`: `zakops-backend/src/api/orchestration/main.py:1665`

#### Where deal is written
- `INSERT INTO zakops.deals (...)`: `zakops-backend/src/api/orchestration/main.py:1650`

#### Event logs/audit emitted
- Creates `deal_created` event:
  - `zakops-backend/src/api/orchestration/main.py:1675`
- Updates quarantine raw_content with processed_by/action:
  - `zakops-backend/src/api/orchestration/main.py:1695`

#### Agent/dashboard same result?
- Dashboard reads backend deals endpoint (`/api/deals`) through middleware/proxy.
- Agent deal tools explicitly query backend API for pipeline data:
  - `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:585`
- Risk remains if agent DB or service URL config drifts (see Section 4 answers 2, 3, 4).

## 4) Forensic Questions Checklist (Answer ALL)

### A. Data Truth / DB Split-Brain
1. Where exactly is the canonical "deal truth" stored?  
Answer: Backend PostgreSQL `zakops` (`zakops.deals`, `zakops.quarantine_items`) enforced by startup gate.  
Evidence: `zakops-backend/src/api/orchestration/main.py:373`, `zakops-backend/src/api/orchestration/main.py:405`, `zakops-backend/db/init/001_base_tables.sql:29`, `zakops-backend/db/init/001_base_tables.sql:210`.  
Status: CONFIRMED.

2. Do agent API, backend API, and dashboard read the same DB connection string?  
Answer: No single shared DB string. Backend uses `zakops`; dashboard uses backend URL; agent uses its own `DATABASE_URL` (expected `zakops_agent`) but deployment file sets it to `zakops`.  
Evidence: `zakops-backend/docker-compose.yml:65`, `zakops-agent-api/apps/agent-api/.env.example:47`, `zakops-agent-api/deployments/docker/docker-compose.yml:17`, `zakops-agent-api/apps/dashboard/src/middleware.ts:27`.  
Status: CONFIRMED.

3. Are there multiple schemas or separate DBs for "agent memory" vs "deal truth"?  
Answer: Yes by design (`zakops_agent` for chat/agent state, backend `zakops` for deal truth), plus separate `crawlrag` for RAG.  
Evidence: `zakops-agent-api/packages/contracts/runtime.topology.json:20`, `zakops-agent-api/apps/agent-api/app/services/chat_repository.py:46`, `Zaks-llm/src/api/rag_rest_api.py:22`.  
Status: CONFIRMED.

4. Can a deal exist in UI but be invisible to the agent (and why)?  
Answer: Yes, under config drift or backend connectivity issues. Agent deal tools depend on backend API; if `DEAL_API_URL` wrong/down, agent cannot read UI-visible deals.  
Evidence: `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:585`, `zakops-agent-api/apps/agent-api/app/core/config.py:245`, runtime ports closed evidence.  
Status: CONFIRMED (path), runtime manifestation `NEEDS VERIFICATION`.

5. Are there any filesystem-based stores, legacy sqlite, or cached snapshots still referenced?  
Answer: Yes, extensively (`.deal-registry`, sqlite state DBs, Zaks-llm filesystem APIs).  
Evidence: `zakops-backend/src/workers/actions_runner.py:53`, `zakops-backend/src/actions/memory/store.py:15`, `Zaks-llm/src/api/server.py:701`.  
Status: CONFIRMED.

### B. Intake / MCP / Email
6. What MCP server(s) exist in the repo and how are they configured?  
Answer: Backend MCP server exists at `zakops-backend/mcp_server/server.py`, default backend URL `http://localhost:8091`, default port 9100, SSE transport. Archived MCP variants also exist.  
Evidence: `zakops-backend/mcp_server/server.py:33`, `zakops-backend/mcp_server/server.py:525`, `zakops-backend/mcp_server/archived/server_http.py`.  
Status: CONFIRMED.

7. Is the email integration active or stubbed?  
Answer: Gmail integration is active in code; Outlook is scaffold-only.  
Evidence: `zakops-backend/src/core/integrations/email/gmail.py:37`, `zakops-backend/src/core/integrations/email/outlook.py:4`.  
Status: CONFIRMED.

8. What mechanism triggers ingestion (polling schedule, webhook, manual)?  
Answer: No active always-on ingestion trigger was found in backend email router/service. A bridge endpoint exists for external `email_ingestion` caller.  
Evidence: `zakops-backend/src/api/orchestration/main.py:1491`, search results showed no webhook/polling implementation in active email API path.  
Status: `NEEDS VERIFICATION` (runtime).  
Commands: `rg -n "webhook|poll|cron|schedule" /home/zaks/zakops-backend/src`.

9. What credentials are required and where are they stored?  
Answer: Gmail OAuth creds via env (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`); per-account tokens stored in `zakops.email_accounts`.  
Evidence: `zakops-backend/src/core/integrations/email/gmail.py:41`, `zakops-backend/db/migrations/022_email_integration.sql:16`.  
Status: CONFIRMED.

10. Is there an onboarding UI for email config, and does it truly write config used by ingestion?  
Answer: Onboarding UI exists but simulates OAuth and does not call backend OAuth endpoints. Settings route proxies to backend endpoints that do not exist.  
Evidence: `zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:56`, `zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts:12`, no backend route match.  
Status: CONFIRMED.

11. What happens if auth expires — is it detected and surfaced to UI?  
Answer: Token expiry is detected and refresh attempted in email service; explicit user-facing auth-expired UX was not found in dashboard integration path.  
Evidence: `zakops-backend/src/core/integrations/email/service.py:43`, `zakops-backend/src/core/integrations/email/service.py:255`.  
Status: PARTIALLY CONFIRMED, UI surfacing `NEEDS VERIFICATION`.

12. How do we prevent duplicate opportunities from repeated emails/threads?  
Answer: App-level pre-check on quarantine by message_id and unique constraint on `email_messages.message_id`; no DB uniqueness on `quarantine_items.message_id`.  
Evidence: `zakops-backend/src/api/orchestration/main.py:1508`, `zakops-backend/db/migrations/022_email_integration.sql:73`, `zakops-backend/db/init/001_base_tables.sql:217`.  
Status: CONFIRMED (gap exists).

13. How do we associate emails to an existing Deal after it's promoted?  
Answer: Email threads can be linked to deals via `email_threads` and link APIs; promotion flow itself does not automatically create `email_threads` link from quarantine item.  
Evidence: `zakops-backend/src/core/integrations/email/service.py:373`, `zakops-backend/src/api/orchestration/routers/email.py:436`, promote flow at `zakops-backend/src/api/orchestration/main.py:1648`.  
Status: CONFIRMED.

14. What is the attachment handling strategy (download, parse, store, link)?  
Answer: Gmail parser extracts attachment metadata in-memory; backfill executor downloads allowed attachments to filesystem quarantine dir; canonical DB artifact linkage is optional/not guaranteed in this path.  
Evidence: `zakops-backend/src/core/integrations/email/gmail.py:392`, `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1009`, `zakops-backend/db/migrations/022_email_integration.sql:91`.  
Status: CONFIRMED.

### C. Quarantine Integrity
15. What fields constitute a quarantine item and how do we validate them?  
Answer: API model `QuarantineCreate` + DB table fields define shape; model includes validators for bounds/normalization.  
Evidence: `zakops-backend/src/api/orchestration/main.py:255`, `zakops-backend/src/api/orchestration/main.py:273`, `zakops-backend/db/init/001_base_tables.sql:210`.  
Status: CONFIRMED.

16. Are Quarantine "delete/clear" endpoints real, or placeholders?  
Answer: Per-item delete (`/delete`) and process (`/process`) are real. Bulk-delete/clear endpoint called by frontend is not implemented in backend/dashboard routes.  
Evidence: `zakops-backend/src/api/orchestration/main.py:1555`, `zakops-backend/src/api/orchestration/main.py:1591`, `zakops-agent-api/apps/dashboard/src/lib/api.ts:942`, route file listing only `[id]/delete`, `[id]/process`, `health`.  
Status: CONFIRMED.

17. When user approves, does the item disappear from Quarantine reliably?  
Answer: Backend sets status to `approved`; list endpoint defaults to `pending`, so approved item should no longer appear in default list. Runtime confirmation pending due services down.  
Evidence: `zakops-backend/src/api/orchestration/main.py:1617`, `zakops-backend/src/api/orchestration/main.py:1692`, `zakops-backend/src/api/orchestration/main.py:1376`.  
Status: LOGIC CONFIRMED, runtime `NEEDS VERIFICATION`.

18. What audit log is created for approval/rejection?  
Answer: On auto-create approve path, a `deal_created` event is recorded; quarantine item raw_content gets `processed_by` and `processing_action`. No dedicated quarantine audit table found.  
Evidence: `zakops-backend/src/api/orchestration/main.py:1675`, `zakops-backend/src/api/orchestration/main.py:1695`.  
Status: CONFIRMED.

19. Does "approve" create a deal in the same DB the dashboard reads from?  
Answer: Yes, approve inserts into `zakops.deals`; dashboard reads backend `/api/deals`.  
Evidence: `zakops-backend/src/api/orchestration/main.py:1650`, `zakops-agent-api/apps/dashboard/src/middleware.ts:85`, `zakops-backend/src/api/orchestration/main.py:535`.  
Status: CONFIRMED.

### D. Deal Lifecycle Tightness
20. After promotion, do stage changes persist to the same record everyone reads?  
Answer: Stage transitions via workflow update `zakops.deals.stage` and write events/ledger; promotion creates deal directly in `zakops.deals` with `stage='inbound'`.  
Evidence: `zakops-backend/src/core/deals/workflow.py:218`, `zakops-backend/src/api/orchestration/main.py:1659`.  
Status: CONFIRMED.

21. Are mismatched stage taxonomies present?  
Answer: Yes. Canonical stage set differs from legacy agent contract text (`Won/Lost/Passed`).  
Evidence: `zakops-backend/src/core/deals/workflow.py:40`, `zakops-backend/src/agent/bridge/agent_contract.py:249`.  
Status: CONFIRMED.

22. Are there shadow pipelines (legacy endpoints/ports) still referenced?  
Answer: Yes. Decommissioned artifacts and old `:8090` references remain; Zaks-llm DataRoom CRUD APIs still exist.  
Evidence: `zakops-backend/gate_artifacts/phase1/deal_api_contract.json:3`, `Zaks-llm/src/api/deal_chat.py:4`, `Zaks-llm/src/api/server.py:701`.  
Status: CONFIRMED.

23. Do RAG/embeddings attach to correct deal id consistently?  
Answer: Not fully provable from runtime. RAG DB is separate (`crawlrag`), and promotion flow bypasses outbox-triggered side effects in workflow path.  
Evidence: `Zaks-llm/src/api/rag_rest_api.py:22`, `zakops-backend/src/core/deals/workflow.py:248`, `zakops-backend/src/api/orchestration/main.py:1648`.  
Status: `NEEDS VERIFICATION`.

24. Can we trace one deal end-to-end across logs/events?  
Answer: Partial instrumentation exists (`deal_events.correlation_id`, middleware headers), but propagation is inconsistent and runtime services were unavailable.  
Evidence: `zakops-backend/db/migrations/024_correlation_id.sql:6`, `zakops-agent-api/apps/dashboard/src/middleware.ts:50`, `zakops-backend/src/api/shared/middleware/trace.py:91`.  
Status: `NEEDS VERIFICATION`.

### E. Observability / World-class Standards
25. Where do ingestion logs go and are they correlated with deal/thread id?  
Answer: No single canonical ingestion service/log sink was found. Some backfill paths log JSONL and include message/thread context.  
Evidence: `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1122`, `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1190`.  
Status: PARTIAL, `NEEDS VERIFICATION` for production ingestion loop.

26. Is there a single correlation id propagated dashboard → backend → agent → DB?  
Answer: No clear single strategy; multiple generators and middleware behaviors exist.  
Evidence: `zakops-agent-api/apps/dashboard/src/lib/api.ts:378`, `zakops-agent-api/apps/dashboard/src/middleware.ts:50`, `zakops-backend/src/api/shared/middleware/trace.py:91`, `zakops-backend/src/api/shared/middleware/tracing.py:56`.  
Status: CONFIRMED.

27. What metrics/alerts exist (queue lag, ingestion failure, auth failure, duplicates)?  
Answer: Limited observability exists (SSE status, health checks, outbox checks), but no strong evidence of duplicate/auth-failure specific alerting pipeline.  
Evidence: `zakops-backend/src/api/shared/routers/events.py:198`, `zakops-backend/src/api/shared/routers/health.py:97`.  
Status: PARTIAL, `NEEDS VERIFICATION`.

28. What are security risks (token storage, PII in logs, least privilege)?  
Answer: OAuth access/refresh tokens are persisted in DB; multiple code paths log operational details; filesystem artifacts include email contents.  
Evidence: `zakops-backend/db/migrations/022_email_integration.sql:16`, `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1025`, `zakops-backend/src/core/integrations/email/gmail.py:169`.  
Status: CONFIRMED.

29. What is the disaster scenario (ingestion loops, duplicate floods) and how prevented?  
Answer: Prevention is incomplete. Dedupe is partially app-level, missing DB uniqueness in quarantine, and no proven active ingestion control loop safeguards in this run.  
Evidence: `zakops-backend/src/api/orchestration/main.py:1508`, `zakops-backend/db/init/001_base_tables.sql:217`, missing ingestion module evidence.  
Status: CONFIRMED risk; full runtime prevention `NEEDS VERIFICATION`.

## 5) Gap / Misalignment List (Reality vs Desired)

| Gap ID | Expected behavior | Current reality | Evidence | Risk level | Root cause hypothesis | How to verify further (commands) |
|---|---|---|---|---|---|---|
| G-001 | Single active email intake control-plane (poll/webhook) into canonical quarantine | Bridge endpoint exists, but no proven active ingestion runner; `email_ingestion` references unresolved | `zakops-backend/src/api/orchestration/main.py:1491`, `zakops-backend/src/workers/actions_runner.py:45` | P0 | Integration migration unfinished | `rg -n "email_ingestion|webhook|poll|schedule" /home/zaks/zakops-backend/src` |
| G-002 | MCP approve/reject uses same contract as backend | MCP calls `/review`, backend uses `/process` | `zakops-backend/mcp_server/server.py:311`, `zakops-backend/src/api/orchestration/main.py:1591` | P0 | Contract drift | `curl -i -X POST http://localhost:9100/...` and backend logs |
| G-003 | Quarantine promotion goes through lifecycle engine + outbox | Promotion directly inserts deal and emits limited events | `zakops-backend/src/api/orchestration/main.py:1648`, `zakops-backend/src/core/deals/workflow.py:248` | P1 | Parallel write paths | SQL check for outbox rows after approve |
| G-004 | Dedupe enforced at DB boundary | Quarantine dedupe is pre-check only; no unique DB constraint on message_id | `zakops-backend/src/api/orchestration/main.py:1508`, `zakops-backend/db/init/001_base_tables.sql:217` | P0 | Missing schema invariant | Concurrent POST test with same `message_id` |
| G-005 | Idempotency is schema-correct and hard-fail safe | Middleware queries unqualified table and bypasses on DB errors | `zakops-backend/src/api/shared/middleware/idempotency.py:85`, `zakops-backend/src/api/shared/middleware/idempotency.py:147` | P1 | Implementation mismatch vs migrations | Send duplicate POST with same key; inspect DB/response headers |
| G-006 | UX config drives runtime email integration | Onboarding simulates OAuth; settings route points to missing backend endpoint | `...EmailSetupStep.tsx:56`, `...settings/email/route.ts:12` | P1 | Frontend scaffolding not wired | Run UI flow and inspect network calls |
| G-007 | UI API contract and backend contract are aligned | Frontend calls `/api/quarantine/bulk-delete`; route absent | `.../src/lib/api.ts:942`, route file listing only 3 quarantine routes | P1 | Contract drift / stale client helper | `curl -i -X POST http://localhost:3003/api/quarantine/bulk-delete` |
| G-008 | Service DB ownership config is consistent | Agent deploy compose DB URL points to `zakops` while topology expects `zakops_agent` | `...deployments/docker/docker-compose.yml:17`, `...runtime.topology.json:20` | P0 | Env management drift | `docker inspect` env dump + startup logs |
| G-009 | Legacy shadow stores fully retired | DataRoom `.deal-registry` still used in active backend/llm paths | `zakops-backend/src/workers/actions_runner.py:53`, `Zaks-llm/src/api/server.py:701` | P0 | Incomplete decommission | Run grep gates + runtime call-path tracing |
| G-010 | End-to-end traceability with one correlation ID and complete observability | Multiple correlation generators/middlewares; SSE health message contradicts implementation; no proven ingestion metrics/alerts | `.../src/lib/api.ts:378`, `.../trace.py:91`, `.../health.py:115`, `.../events.py:164` | P1 | Fragmented observability evolution | Inject fixed correlation ID and trace across logs/events/DB |

## 6) Recommendations (Permanent, Industry-standard, Best-fit)

### For G-001 (P0): Canonical Intake Control Plane
- Permanent fix approach: Build one ingestion service (poller/webhook) that reads provider deltas and writes only via canonical backend service method to `zakops.quarantine_items`.
- Industry standard / best practice: Event-driven inbox ingestion with cursor checkpoints and idempotent consumer semantics.
- Why it fits this system: Existing OAuth + email APIs already exist; missing piece is deterministic orchestration and scheduling.
- Never-again enforcement: CI integration test with synthetic email payload must produce exactly one quarantine record and stable checkpoint advancement.

### For G-002 (P0): MCP Contract Lock
- Permanent fix approach: Align MCP tool calls to `/api/quarantine/{id}/process` and lock payload schema in shared contract package.
- Industry standard / best practice: Consumer-driven contract tests between tool-layer and API.
- Why it fits this system: MCP is a thin proxy to backend; contract breakages are high-impact and easy to gate.
- Never-again enforcement: CI job executes MCP tool against ephemeral backend and validates response schema + status.

### For G-004/G-005 (P0/P1): Idempotency + Dedupe as DB Invariants
- Permanent fix approach: Add unique index for quarantine identity (`message_id` + provider/source if needed), schema-qualify idempotency table access, and fail-safe behavior on DB errors.
- Industry standard / best practice: Idempotent write APIs with DB uniqueness and replay-safe response cache.
- Why it fits this system: Current middleware and route logic already attempt idempotency; this makes it reliable under concurrency.
- Never-again enforcement: Concurrency regression suite (`N` parallel creates same message-id) must produce one row and cached responses.

### For G-003 (P1): Promotion Through Unified Domain Service
- Permanent fix approach: Move quarantine approval write path into the same lifecycle service that handles stage transitions and outbox events.
- Industry standard / best practice: Single aggregate write path + transactional outbox.
- Why it fits this system: Already has workflow engine and outbox primitives; current bypass is the inconsistency source.
- Never-again enforcement: Contract test: approve action must produce expected `deals`, `deal_events`, `deal_transitions`, and `outbox` rows.

### For G-006/G-007 (P1): UX/Runtime Contract Unification
- Permanent fix approach: Replace simulated onboarding with real OAuth flow; remove or implement orphan endpoints (`/api/quarantine/bulk-delete`, `/api/user/email-config`).
- Industry standard / best practice: API-first UI with generated clients from live OpenAPI.
- Why it fits this system: Dashboard already has API proxy layer and generated types.
- Never-again enforcement: API route existence gate in CI and Playwright flow test for email onboarding + quarantine bulk operations.

### For G-008/G-009 (P0): Canonical Data Ownership Enforcement
- Permanent fix approach: Explicitly classify canonical vs non-canonical stores; block production use of DataRoom `.deal-registry` for deals/quarantine.
- Industry standard / best practice: Bounded context ownership with deprecation gates and read/write kill switches.
- Why it fits this system: Existing topology contract already documents intended ownership.
- Never-again enforcement: static grep gate banning `.deal-registry` imports in production paths + startup assertions for DB identity.

### For G-010 (P1): End-to-End Traceability and Observability
- Permanent fix approach: Use one correlation ID policy from ingress to DB events; unify tracing middleware behavior; add metrics for ingestion lag, auth failures, duplicate rate.
- Industry standard / best practice: OpenTelemetry + business correlation propagation with SLO alerts.
- Why it fits this system: Headers and correlation columns already exist; needs consistency and coverage.
- Never-again enforcement: trace propagation integration test + dashboard alert thresholds for queue lag/failure rates.

### Systemic improvements (cross-gap)
1. Canonical data ownership model: formal ADR with service-level startup gates.
2. Ingestion idempotency contract: provider message identity, dedupe window, and replay semantics documented and tested.
3. Audit log + event model: quarantine decisions, promotions, stage transitions emit standardized events with actor/correlation.
4. Configuration UX to runtime wiring: every config screen must hit a live backend endpoint with persisted readback.
5. End-to-end traceability strategy: mandatory correlation ID and trace context through dashboard → backend → agent → DB/outbox.

## BONUS) Contrarian Sweep — Top 10 Likely Failure Patterns

| Pattern | Why likely here | Detection with proof |
|---|---|---|
| F-01 Dual DB drift (agent points to wrong DB) | Conflicting `DATABASE_URL` examples/deploy files | `rg -n "DATABASE_URL" deployments apps/agent-api/.env.example` |
| F-02 Ingestion appears “on” but no worker running | Onboarding simulates OAuth, no proven poller | Observe onboarding network calls + lack of ingestion heartbeats |
| F-03 MCP approves fail silently | MCP `/review` mismatch vs backend `/process` | Call MCP tool and inspect backend 404 logs |
| F-04 Duplicate quarantine floods under race | App-level dedupe without DB unique index | Concurrent POST with same `message_id` and count rows |
| F-05 Event side-effects missing after approve | Promotion bypasses workflow/outbox path | Approve item and query `zakops.outbox` + `deal_transitions` |
| F-06 Shadow filesystem truth resurrects old data | `.deal-registry` still in active code | grep `.deal-registry` and trace called code path in logs |
| F-07 Correlation ID breaks across hops | Multiple generators/middleware behavior | Inject fixed header and trace across response + DB events |
| F-08 UI contract drift causes hidden 404s | bulk-delete/email-config endpoint mismatches | Hit UI routes and inspect status + proxy backend calls |
| F-09 Token expiry errors are internal-only | refresh exists, UX surfacing uncertain | expire token in test account; verify API and UI error propagation |
| F-10 Observability mismatch misleads operators | health says SSE not implemented while stream exists | Compare `/health/ready` response vs `/api/events/stream` behavior |

## 7) Minimum Proof Steps (Repro + Validation)

> Non-destructive only; uses `GET`, `POST` test records, and `SELECT`.

### A) Bring services up and verify health
```bash
# Backend stack
cd /home/zaks/zakops-backend
docker compose up -d

# Agent/Dashboard stack (if separate)
cd /home/zaks/zakops-agent-api/deployments/docker
docker compose up -d

# Health checks
curl -sS http://localhost:8091/health/ready
curl -sS http://localhost:8095/health
curl -sS http://localhost:3003/api/quarantine/health
curl -sS http://localhost:9100/health || true
```

### B) Safe ingestion simulation (no destructive actions)
```bash
MID="forensic-${RANDOM}-$(date +%s)"
curl -sS -X POST http://localhost:8091/api/quarantine \
  -H 'Content-Type: application/json' \
  -d "{
    \"message_id\":\"${MID}\",
    \"email_subject\":\"Forensic Intake Test ${MID}\",
    \"sender\":\"broker@example.com\",
    \"classification\":\"deal_signal\",
    \"urgency\":\"HIGH\",
    \"confidence\":0.91
  }"
```

### C) Confirm quarantine creation in canonical DB
```bash
psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -c \
"SELECT id, message_id, status, created_at FROM zakops.quarantine_items WHERE message_id='${MID}';"
```

### D) Approve and verify promotion
```bash
QID=$(psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -Atc \
"SELECT id FROM zakops.quarantine_items WHERE message_id='${MID}' LIMIT 1;")

curl -sS -X POST "http://localhost:8091/api/quarantine/${QID}/process" \
  -H 'Content-Type: application/json' \
  -d '{"action":"approve","processed_by":"forensic_audit"}'
```

### E) Verify DB truth alignment
```bash
psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -c \
"SELECT q.id, q.status, q.deal_id, d.stage, d.canonical_name
 FROM zakops.quarantine_items q
 LEFT JOIN zakops.deals d ON d.deal_id=q.deal_id
 WHERE q.id='${QID}';"

psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -c \
"SELECT event_type, actor, created_at
 FROM zakops.deal_events
 WHERE deal_id=(SELECT deal_id FROM zakops.quarantine_items WHERE id='${QID}')
 ORDER BY created_at DESC LIMIT 10;"
```

### F) Verify dedupe/idempotency behavior
```bash
# Repeat same create payload with identical MID
curl -sS -X POST http://localhost:8091/api/quarantine \
  -H 'Content-Type: application/json' \
  -d "{\"message_id\":\"${MID}\",\"email_subject\":\"dup test\"}"

psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -c \
"SELECT COUNT(*) FROM zakops.quarantine_items WHERE message_id='${MID}';"
```

### G) Verify agent/dashboard see same deal truth
```bash
DEAL_ID=$(psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -Atc \
"SELECT deal_id FROM zakops.quarantine_items WHERE id='${QID}';")

curl -sS "http://localhost:8091/api/deals/${DEAL_ID}"
# Agent side: verify DEAL_API_URL points to same backend
docker exec -it <agent-container> printenv DEAL_API_URL
```

## 8) STOP
Audit complete  
Ready for remediation mission(s)
```

---

### `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_EVIDENCE_INDEX.md`
```markdown
# FORENSIC INTAKE / QUARANTINE / DEAL INTEGRITY — Evidence Pack Index
Run ID: TP-20260213-163446  
Agent: CODEX  
Timestamp: 2026-02-13T16:34:47Z

## Runtime Evidence
| ID | Type | Evidence | Notes |
|---|---|---|---|
| E46 | command output | write attempt to `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1/__write_test.tmp` returned `Permission denied` | Read-only filesystem constraint |
| E47 | command output | port probes: `3003 closed`, `8091 closed`, `8095 closed`, `8052 closed`, `9100 closed` | Services down in this run |
| E48 | command output | curl to `http://127.0.0.1:{3003,8091,8095,8052,9100}` returned `curl: (7) Failed to connect` | Runtime route execution not possible |
| E49 | command output | `docker ps` -> `permission denied ... /var/run/docker.sock` | Container runtime introspection blocked |
| E50 | command output | port probe `5432 closed` | DB runtime validation blocked |
| E51 | command output | git revisions: `fc5e39d...`, `444dff6...`, `4dfa462...` | Repo snapshots for audit traceability |

## Canonical DB {{PASS1_REPORT_C}} Schema Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E01 | file:line | `zakops-backend/src/api/orchestration/main.py:85`, `zakops-backend/src/api/orchestration/main.py:373`, `zakops-backend/src/api/orchestration/main.py:395` | Backend canonical DB (`zakops`) and startup DSN gate |
| E02 | file:line | `zakops-backend/docker-compose.yml:65`, `zakops-backend/docker-compose.yml:106` | Backend + outbox worker use same DB URL/backend |
| E03 | file:line | `zakops-backend/db/init/001_base_tables.sql:29`, `zakops-backend/db/init/001_base_tables.sql:107`, `zakops-backend/db/init/001_base_tables.sql:210` | Deals/quarantine/events table definitions |
| E04 | file:line | `zakops-backend/db/migrations/022_email_integration.sql:11`, `zakops-backend/db/migrations/022_email_integration.sql:57`, `zakops-backend/db/migrations/022_email_integration.sql:84` | Email integration persistence tables |
| E05 | file:line | `zakops-backend/db/migrations/023_stage_check_constraint.sql:5`, `zakops-backend/db/migrations/024_correlation_id.sql:6`, `zakops-backend/db/migrations/025_deal_lifecycle_fsm.sql:67` | Stage/correlation/lifecycle constraints |

## Backend API Path Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E06 | file:line | `zakops-backend/src/api/orchestration/main.py:451`, `zakops-backend/src/api/orchestration/main.py:489`, `zakops-backend/src/api/orchestration/main.py:495` | Middleware/router wiring |
| E07 | file:line | `zakops-backend/src/api/orchestration/main.py:1374`, `zakops-backend/src/api/orchestration/main.py:1483`, `zakops-backend/src/api/orchestration/main.py:1555`, `zakops-backend/src/api/orchestration/main.py:1591` | Quarantine list/create/delete/process routes |
| E08 | file:line | `zakops-backend/src/api/orchestration/main.py:1648`, `zakops-backend/src/api/orchestration/main.py:1675`, `zakops-backend/src/api/orchestration/main.py:1691` | Approval creates deal + event + quarantine status update |
| E09 | file:line | `zakops-backend/src/core/deals/workflow.py:218`, `zakops-backend/src/core/deals/workflow.py:227`, `zakops-backend/src/core/deals/workflow.py:248` | Workflow stage update + transition ledger + outbox |
| E40 | file:line | `zakops-backend/src/api/orchestration/main.py:1046` | Legacy alias `/api/actions/quarantine` exists |

## Dashboard Contract/Wiring Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E10 | file:line | `zakops-agent-api/apps/dashboard/src/lib/backend-fetch.ts:7`, `zakops-agent-api/apps/dashboard/src/middleware.ts:27` | BACKEND_URL/API_URL precedence mismatch across files |
| E11 | file:line | `zakops-agent-api/apps/dashboard/src/middleware.ts:50`, `zakops-agent-api/apps/dashboard/src/lib/api.ts:378`, `zakops-agent-api/apps/dashboard/src/lib/api.ts:389` | Correlation + idempotency headers behavior |
| E12 | file:line | `zakops-agent-api/apps/dashboard/src/lib/api.ts:872`, `zakops-agent-api/apps/dashboard/src/lib/api.ts:926`, `zakops-agent-api/apps/dashboard/src/lib/api.ts:942` | UI quarantine calls include process/delete/bulk-delete |
| E13 | file listing + file:line | `apps/dashboard/src/app/api/quarantine/[id]/process/route.ts:21`, `apps/dashboard/src/app/api/quarantine/[id]/delete/route.ts:20`, `apps/dashboard/src/app/api/quarantine/health/route.ts:13` | Only process/delete/health routes present |
| E14 | file:line | `zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts:25`, `zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts:54` | Quarantine list fallback to `/api/actions` |
| E15 | file:line | `zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts:12`, `zakops-agent-api/apps/dashboard/src/app/api/settings/email/test/route.ts:10` | Settings proxy targets `/api/user/email-config*` |
| E16 | search output | no matches for `user/email-config` under `zakops-backend/src` | Backend route absent |
| E17 | file:line | `zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:56`, `zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:60` | Onboarding email setup is simulated |

## Email Integration {{PASS1_REPORT_C}} Intake Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E18 | file:line | `zakops-backend/src/api/orchestration/routers/email.py:23`, `zakops-backend/src/api/orchestration/routers/email.py:31`, `zakops-backend/src/api/orchestration/routers/email.py:160` | Email router + in-memory OAuth state + Gmail auth endpoints |
| E19 | file:line | `zakops-backend/src/core/integrations/email/service.py:11`, `zakops-backend/src/core/integrations/email/service.py:255`, `zakops-backend/src/core/integrations/email/service.py:370` | Service uses DB adapter, token refresh, thread linking |
| E20 | file:line | `zakops-backend/src/core/integrations/email/gmail.py:41`, `zakops-backend/src/core/integrations/email/gmail.py:69`, `zakops-backend/src/core/integrations/email/gmail.py:392` | Gmail env credentials + attachment metadata parse |
| E21 | file:line | `zakops-backend/src/core/integrations/email/outlook.py:4`, `zakops-backend/src/core/integrations/email/outlook.py:84` | Outlook integration scaffold-only |
| E41 | search output | search in active email API path returned only doc mentions at `main.py:1488`, `main.py:1491` | No obvious poll/webhook ingestion implementation in scanned path |

## DB Adapter, Idempotency, Tracing Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E22 | file:line | `zakops-backend/src/core/database/adapter.py:74`, `zakops-backend/src/core/database/adapter.py:56`, `zakops-backend/src/core/database/adapter.py:63` | Adapter defaults SQLite path + dual-write options |
| E23 | file:line | `zakops-backend/src/api/shared/middleware/idempotency.py:85`, `zakops-backend/src/api/shared/middleware/idempotency.py:127`, `zakops-backend/db/migrations/001_foundation_tables.sql:114` | Unqualified idempotency table query vs schema-qualified table |
| E24 | file:line | `zakops-backend/src/api/shared/middleware/idempotency.py:147`, `zakops-agent-api/apps/agent-api/app/services/backend_client.py:307`, `zakops-backend/src/api/orchestration/main.py:855` | Idempotency bypass + agent sends note idempotency in body but note schema lacks field |
| E25 | file:line | `zakops-backend/src/api/shared/middleware/trace.py:91`, `zakops-backend/src/api/shared/middleware/tracing.py:56`, `zakops-backend/src/api/orchestration/main.py:451` | Trace/correlation behavior mismatch with both middlewares active |
| E26 | file:line | `zakops-backend/src/api/shared/routers/events.py:164`, `zakops-backend/src/api/shared/sse.py:511`, `zakops-backend/src/api/shared/routers/health.py:115` | SSE implemented while health message says not implemented |
| E27 | file:line | `zakops-backend/src/api/shared/routers/events.py:233` | Polling endpoint reads `zakops.agent_events` |
| E28 | file:line + search | `zakops-backend/db/migrations/001_foundation_tables.sql:243` plus no `CREATE TABLE ... agent_events` in `zakops-backend/db` search | `agent_events` creation uncertainty |

## MCP Integration Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E29 | file:line | `zakops-backend/mcp_server/server.py:33`, `zakops-backend/mcp_server/server.py:311`, `zakops-backend/mcp_server/server.py:341`, `zakops-backend/mcp_server/server.py:525` | MCP backend URL + wrong quarantine review path + port |
| E30 | file:line + search | `zakops-backend/src/api/orchestration/main.py:1591` and no `/review` route match | MCP/backend contract mismatch |
| E31 | file listing | `zakops-backend/mcp_server/archived/server_http.py`, `zakops-backend/mcp_server/archived/server_sse.py` | Archived/shadow MCP variants remain |

## Agent API {{PASS1_REPORT_C}} Cross-DB Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E32 | file:line | `zakops-agent-api/apps/agent-api/app/core/config.py:185`, `zakops-agent-api/apps/agent-api/app/core/config.py:245` | Agent requires `DATABASE_URL`; external service URLs configured |
| E33 | file:line | `zakops-agent-api/apps/agent-api/app/services/database.py:42` | Agent DB engine from `DATABASE_URL` |
| E34 | file:line | `zakops-agent-api/apps/agent-api/app/services/chat_repository.py:46`, `zakops-agent-api/apps/agent-api/app/services/chat_repository.py:415`, `zakops-agent-api/apps/agent-api/app/services/chat_repository.py:526` | `zakops_agent` writes + cross-db outbox + backend-based deal validation |
| E35 | file:line | `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:585`, `zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:508` | Agent tools use backend API for deal truth |

## Environment Drift Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E36 | file:line | `zakops-agent-api/apps/agent-api/.env.example:47`, `zakops-agent-api/.env.example:7`, `zakops-agent-api/deployments/docker/docker-compose.yml:17`, `zakops-agent-api/packages/contracts/runtime.topology.json:20` | Agent DB env mismatch across files |

## Legacy / Shadow Pipeline Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E37 | file:line | `zakops-backend/src/workers/actions_runner.py:53`, `zakops-backend/src/workers/actions_runner.py:45` | DataRoom path and `email_ingestion` imports in runner |
| E38 | file:line | `zakops-backend/src/actions/memory/store.py:15` | SQLite state store under `.deal-registry` |
| E39 | file:line | `zakops-backend/src/actions/capabilities/email_triage.review_email.v1.yaml:5`, `zakops-backend/src/actions/capabilities/email_triage.review_email.v1.yaml:75` | Capability still declares Deal Registry mapping |
| E40 | file:line | `zakops-backend/src/actions/executors/email_triage_review_email.py:665`, `zakops-backend/src/actions/executors/email_triage_review_email.py:675` | Executor writes/validates Deal Registry |
| E41 | file:line | `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1009`, `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1068`, `zakops-backend/src/actions/executors/deal_backfill_sender_history.py:1152` | Filesystem quarantine directories + attachment downloads + re-queue triage |
| E42 | command output + references | `email_ingestion dir missing` and references in `actions_runner.py:45`, `chat_orchestrator.py:45` | Missing module with active imports |
| E43 | file:line | `Zaks-llm/src/api/server.py:701`, `Zaks-llm/src/api/server.py:794`, `Zaks-llm/src/api/server.py:849` | Zaks-llm CRUD reads/writes DataRoom deal/quarantine/deferred stores |
| E44 | file:line | `Zaks-llm/src/api/rag_rest_api.py:22`, `Zaks-llm/src/api/rag_rest_api.py:56` | RAG service uses separate `crawlrag` DB |
| E45 | file:line | `zakops-backend/infra/docker/docker-compose.yml:1`, `Zaks-llm/docker-compose.deal-engine.yml:1`, `zakops-backend/gate_artifacts/phase1/deal_api_contract.json:3` | Decommissioned split-brain artifacts and legacy `:8090` references |

## Additional Integrity Evidence
| ID | Type | Source | Claim supported |
|---|---|---|---|
| E43b | file:line | `zakops-backend/src/agent/bridge/agent_contract.py:249` | Legacy stage taxonomy (`Won/Lost/Passed`) mismatch |
| E42b | file:line | `zakops-backend/src/core/retention/cleanup.py:255`, `zakops-backend/src/core/retention/cleanup.py:299` | Quarantine retention cleanup includes delete/update behaviors |

## Reproduction Commands (non-destructive)
```bash
# Service reachability
for p in 3003 8091 8095 8052 9100 5432; do
  timeout 1 bash -lc "</dev/tcp/127.0.0.1/$p" 2>/dev/null {{PASS1_REPORT_C}}{{PASS1_REPORT_C}} echo "$p open" || echo "$p closed"
done

# Health probes
curl -sS -m 2 http://127.0.0.1:8091/health/ready
curl -sS -m 2 http://127.0.0.1:3003/api/quarantine/health
curl -sS -m 2 http://127.0.0.1:8095/health
curl -sS -m 2 http://127.0.0.1:9100/health

# Quarantine workflow probe (when backend is up)
MID="forensic-$(date +%s)"
curl -sS -X POST http://localhost:8091/api/quarantine \
  -H 'Content-Type: application/json' \
  -d "{\"message_id\":\"$MID\",\"email_subject\":\"forensic\",\"sender\":\"broker@example.com\"}"

# DB read-only proof checks
psql "postgresql://zakops:zakops_dev@localhost:5432/zakops" -c \
"SELECT id,message_id,status,deal_id FROM zakops.quarantine_items ORDER BY created_at DESC LIMIT 5;"
```
```

Natural next step if you want these written to disk automatically: rerun this mission in a writable workspace mode, and I will emit these exact contents directly to the three target paths.

---

## Instructions

You are reviewing all three independent investigation reports. Your job is to:

1. **Identify duplicates** — findings that multiple agents reported (high confidence items)
2. **Identify conflicts** — findings where agents disagree on root cause or fix approach
3. **Identify unique findings** — items only one agent found (potential blind spot coverage)
4. **Verify evidence** — check that cited file:line references are accurate
5. **Flag drift** — note any findings that fall outside the declared mission scope

### Output Format

Write your cross-review to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/02_pass2/claude_review.md`

Begin with exactly this header:

```
# Pass 2 Cross-Review — CLAUDE
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T17:04:20Z
```

Then organize as:

```
## DUPLICATES (High Confidence)
Items found by 2+ agents. Merge into a single entry with attribution.

### D-1: [Merged Title]
**Reported by:** Agent A (Finding X), Agent B (Finding Y)
**Consensus root cause:** ...
**Consensus fix:** ...
**Evidence verified:** YES/NO

(repeat)

## CONFLICTS
Items where agents disagree. State both positions with evidence.

### C-1: [Conflict Title]
**Agent A position:** ...
**Agent B position:** ...
**Evidence comparison:** ...
**Recommended resolution:** ...

(repeat)

## UNIQUE FINDINGS
Items found by only one agent. Verify if the finding is valid.

### U-1: [Title] (from Agent X)
**Verification:** CONFIRMED / UNVERIFIED / INVALID
**Evidence check:** ...
**Should include in final:** YES / NO (with reason)

(repeat)

## DRIFT FLAGS
Findings that fall outside declared scope.

### DRIFT-1: [Title] (from Agent X)
**Why out of scope:** ...
**Severity if ignored:** ...

## SUMMARY
- Duplicates: N
- Conflicts: N
- Unique valid findings: N
- Drift items: N
- Overall assessment: ...
```
