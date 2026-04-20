# **Title:** CRITICAL UPGRADE — Build “Kinetic Action Engine” (Actions = Executable Command Center)

**Owner:** ZakOps (Lead Engineer: Codex)  
**Status:** Plan — Ready for Implementation  
**Date:** 2025-12-31  
**Scope:** Production-ready upgrade (no rewrite-from-scratch; keep existing chat contracts)  

---

## 0) Baseline (Current System Reality — Verified)

### Frontend
- ZakOps Dashboard (Next.js): `http://localhost:3003`
- Existing Actions UI: `/home/zaks/zakops-dashboard/src/app/actions/page.tsx`
  - Currently uses `getActions()` + `getDueActions()` from `/home/zaks/zakops-dashboard/src/lib/api.ts`
  - Renders actions as read-only list items (links to deal pages)

### Backend (BFF)
- FastAPI: `/home/zaks/scripts/deal_lifecycle_api.py` on `http://localhost:8090`
- Chat endpoints **must remain backward compatible**:
  - `POST /api/chat` (SSE streaming)
  - `POST /api/chat/complete`
  - `POST /api/chat/execute-proposal`
- Current “actions” endpoints exist but are **deferred reminders** only:
  - Source of truth: `/home/zaks/scripts/deferred_actions.py` using JSON storage at `DataRoom/.deal-registry/deferred_actions.json`
  - Existing endpoints:
    - `GET /api/actions` (list)
    - `GET /api/actions/due`
    - `POST /api/actions/{action_id}/execute` (marks executed; does not generate artifacts)
    - `POST /api/actions/{action_id}/cancel`

### Chat orchestration
- Orchestrator: `/home/zaks/scripts/chat_orchestrator.py`
  - Proposals currently supported: `add_note`, `create_task` (deferred action), `draft_email`, `request_docs`, `stage_transition`
  - Proposal execution endpoint: `/api/chat/execute-proposal` (do not break)
  - LangGraph “brain” available: `http://localhost:8080` (mode: `off|auto|force`); **no LangSmith tracing requirement**

### Data + platform foundations
- Deal registry: `/home/zaks/scripts/deal_registry.py` (`deal.folder_path` is authoritative deal folder location)
- Event store: `/home/zaks/scripts/deal_events.py`
- Schemas: `/home/zaks/DataRoom/.deal-registry/schemas/*.yaml`
- SQLite state store already exists (ingestion + chat persistence):
  - Package: `/home/zaks/scripts/email_ingestion/state/sqlite_store.py`
  - Config: `ZAKOPS_STATE_DB` (default currently: `DataRoom/.deal-registry/ingest_state.db`)

---

## 1) Goal (What “Kinetic Actions” Adds)

Turn Actions into the **Execution Layer** (executable command center) tightly integrated with Chat:

1) Chat produces an action creation proposal (or an action record in pending approval).
2) Actions UI becomes the single pane of glass for **Review → Edit → Approve → Execute**.
3) Execution generates real **artifacts** (DOCX/PDF/XLSX/PPTX) saved into the deal’s DataRoom folder and downloadable immediately.
4) Every step is audited (DB audit trail + deal events + run-ledger).
5) No silent drops; fail safe; no irreversible actions without explicit approval.

---

## 2) Non‑Negotiable Constraints (Engineering Decisions Locked)

1) **Do not break** `/api/chat` request/response contract or `/api/chat/execute-proposal` payloads.
2) **Do not require** LangSmith tracing. Tracing code (if present) remains OFF by default.
3) **Chat never executes heavy actions** directly; it only proposes them.
4) **Idempotency required**: action records must dedupe via `idempotency_key` (unique in DB).
5) **Runner must survive restarts** and prevent ghost runners (lease/lock).
6) **Secret-scan gate** before any cloud call; if cloud disabled, fail clearly (especially `COMMUNICATION.DRAFT_EMAIL`).
7) **UI design stays consistent** (upgrade functionality without redesign).

---

## 3) Architecture Overview (World‑Class, Minimal Risk)

### 3.1 Core primitives
- **ActionPayload (Pydantic)**: universal schema (R1) stored as JSON + indexed columns in SQLite.
- **ActionAuditEvent**: append-only audit records (approve/execute/fail/cancel/retry).
- **Artifact**: metadata record pointing to a real file under a deal folder.
- **Executor registry**: plugin system keyed by `ActionType`.
- **Runner**: a single worker process that claims READY actions and executes via executors.

### 3.2 Source of truth model
- **SQLite is the truth** for action lifecycle state (status, inputs, outputs, audit events, artifacts).
- **Deal events** mirror action milestones for deal-centric observability (e.g., `action_created`, `action_approved`, `action_completed`).
- **Folders are derived views**: artifacts stored under deal folder; DB always knows what exists and where.

### 3.3 Backward compatibility strategy
- Preserve the existing deferred-reminder system under **explicit legacy endpoints**:
  - Keep `GET /api/deferred-actions` and `GET /api/deferred-actions/due` backed by `deferred_actions.json`
- Repurpose `/api/actions*` to mean **Kinetic Actions** (new engine).
- Update Dashboard UI to use the new `/api/actions*` endpoints.

---

## 4) R1 — Universal Action Schema (Canonical Pydantic Model)

### 4.1 Canonical model
Implement `ActionPayload` in the backend as a Pydantic model with at minimum:
- `action_id` (server-generated)
- `deal_id` (optional)
- `type` (enum)
- `title`, `summary`
- `status` (enum)
- `created_at`, `updated_at`
- `started_at`, `completed_at`, `duration_seconds` (nullable; for observability + UI)
- `created_by`
- `source` (`chat|ui|system`)
- `risk_level` (`low|medium|high`)
- `requires_human_review` (bool)
- `idempotency_key` (string; unique)
- `inputs` (typed JSON object per action type)
- `outputs` (typed JSON object; artifacts + results)
- `error` (nullable; structured)
- `audit_trail` (append-only list; stored as separate table and materialized view)
  - include retry metadata: `retry_count` (int) and `max_retries` (int; default per action type)
  - include `artifacts` array in API response (even if stored in a separate table)

**Schema strictness (required):** Pydantic must run with `extra="forbid"` so unknown keys don’t silently pass validation.

### 4.2 Status state machine
Implement strict transitions:
- `PENDING_APPROVAL → READY → PROCESSING → COMPLETED`
- `PROCESSING → FAILED`
- `PENDING_APPROVAL|READY|PROCESSING → CANCELLED` (policy-controlled)

### 4.3 Safe defaults
- New actions default to `PENDING_APPROVAL` and `requires_human_review=true` unless created by trusted system flows.
- Edits allowed only when `PENDING_APPROVAL` or `READY`.
- Execution forbidden until `READY`.

---

## 5) R2 — Action Types (Initial Set, End‑to‑End)

Define `ActionType` enum with at least:

1) `COMMUNICATION.DRAFT_EMAIL`
   - Requires cloud-enabled Gemini Pro for drafting (policy: fail clearly if cloud disabled)
   - Output is a saved draft (no sending required in MVP)
   - Artifact generation: DOCX (preferred) via `python-docx`; optional PDF is best-effort only
2) `DOCUMENT.GENERATE`
   - LOI / NDA / generic request letter
   - Deterministic template-first; optional LLM refinement behind gates
   - Output: DOCX (required) + PDF (best-effort if converter available)
   - Artifact generation: DOCX via `python-docx`; optional PDF best-effort (only if a headless converter is available)
3) `ANALYSIS.BUILD_MODEL`
   - XLSX valuation model template populated from known deal fields (or stub)
   - Artifact generation: XLSX via `openpyxl`
4) `PRESENTATION.GENERATE_DECK`
   - PPTX pitch / lender deck (simple templated deck; optional PDF best-effort)
   - Artifact generation: PPTX via `python-pptx`
5) `DILIGENCE.REQUEST_DOCS`
   - Generates a checklist artifact + a draft email artifact
   - Checklist must be generated deterministically even if cloud is disabled
   - Artifact generation: checklist as MD (deterministic) + optional DOCX/PDF exports best-effort

Design rule: adding a new action type must be a ~1-file change (new executor + input model + registration).

---

## 6) R3 — Executors Plugin System (Registry + Contracts)

### 6.1 Interface
Create `ActionExecutor` base class:
- `validate(payload) -> None | raises`
- `dry_run(payload) -> ActionOutputsPreview` (include estimated artifacts + cost + duration)
- `execute(payload, context) -> ActionOutputs`
- `estimate_cost(payload) -> CostEstimate`

### 6.2 Registry
- `ACTION_EXECUTORS: dict[ActionType, ActionExecutor]`
- Registration happens at import time in a single registry module (no dynamic magic).

### 6.3 Idempotency enforcement
- `idempotency_key` is required and has a DB unique constraint.
- `POST /api/actions` must be idempotent:
  - If the same `idempotency_key` is submitted twice, return the existing action (200) instead of creating a duplicate.
- `execute()` must be idempotent per action_id:
  - If `COMPLETED`, do not re-run unless explicitly `retry` (UI) which creates an audit event and moves back to `READY`.

---

## 7) R4 — Backend API (8090) Endpoints (Do Not Break Chat)

### 7.1 New Kinetic Actions endpoints (required)
- `GET /api/actions`
  - Filters: `status`, `type`, `deal_id`, `created_after`, `created_before`
  - Pagination: `limit`, `offset` (default limit; deterministic sort by `created_at desc`)
- `GET /api/actions/{action_id}`
- `POST /api/actions` (create; status defaults `PENDING_APPROVAL`)
- `POST /api/actions/{action_id}/update` (edit inputs/title/summary while allowed)
- `POST /api/actions/{action_id}/approve` (moves to `READY`)
- `POST /api/actions/{action_id}/execute` (enqueue + returns immediately; status becomes `PROCESSING`)
- `POST /api/actions/{action_id}/cancel`
- `GET /api/actions/{action_id}/artifacts`
- `GET /api/actions/{action_id}/artifact/{artifact_id}` (download)

### 7.2 Legacy endpoints preserved (for current deferred reminders)
- Keep existing behaviour at:
  - `GET /api/deferred-actions`
  - `GET /api/deferred-actions/due`
  - `POST /api/deferred-actions/{action_id}/execute`
  - `POST /api/deferred-actions/{action_id}/cancel`

### 7.3 Execution semantics
- `POST /api/actions/{id}/execute` does **not** execute inline; it enqueues and returns:
  - `202 Accepted` with `{ action_id, status, runner_hint }`
- The UI polls `GET /api/actions/{id}` until terminal status.

---

## 8) R4 — Execution Runtime: Durable Queue + Single Runner

### 8.1 Storage decision (reasonable + minimal-risk)
Extend the existing SQLite state DB (`ZAKOPS_STATE_DB`, currently used for ingestion + chat persistence) with:
- `actions`
- `action_audit_events`
- `action_artifacts`
- `action_runner_leases`

(This avoids introducing a second DB and reuses the existing WAL + migration patterns.)

### 8.2 Runner process
Add a runner entrypoint (one process):
- `python3 /home/zaks/scripts/actions_runner.py`
- or `python3 -m zakops_actions.runner` (preferred if we package it)

Responsibilities:
- Acquire lease in DB (`action_runner_leases`) to prevent ghost runners.
- Claim one READY action at a time using an atomic `UPDATE ... WHERE status='READY' ... RETURNING` style transaction.
- Execute via plugin executor.
- Persist outputs + artifacts + audit events.
- Emit deal events for major lifecycle milestones.
- Heartbeat updates; lease expiry enables safe takeover after crash.
- Graceful shutdown: handle SIGTERM/SIGINT, stop claiming new work, release lease + PID file.

Retry policy (required):
- Persist `retry_count` and `max_retries`
- On failure:
  - if `retry_count < max_retries`: transition back to `READY` (optionally with backoff timestamp)
  - else: terminal `FAILED` with structured error + audit event `execution_failed_max_retries`

Runner singleton enforcement (required):
- Use DB lease as the primary guard.
- Also write a PID file (e.g., `/tmp/zakops_action_runner.pid`) as an operator-friendly “is it running?” indicator and stale-lock detector.

### 8.3 Make target
Add to `/home/zaks/zakops-dashboard/Makefile`:
- `make actions-runner` (starts runner in foreground)
- `make actions-runner-bg` (nohup to `/tmp/actions_runner.log`)
- `make actions-runner-stop`

---

## 9) R5 — Chat → Action Bridging (Critical)

### 9.1 Proposal model (do not break existing)
Add a new canonical proposal type: `create_action`
- Executing (`/api/chat/execute-proposal`) with `approve` creates an Action record in `PENDING_APPROVAL`
- Result returned includes `action_id` and a URL the UI can link to

Keep existing proposal types unchanged:
- `draft_email`, `create_task`, `request_docs`, etc.

### 9.2 Orchestrator changes
Update `/home/zaks/scripts/chat_orchestrator.py`:
- Add `create_action` to canonical proposal types
- Add an executor branch in `execute_proposal()` to create an action record (idempotent)
- Ensure session persistence stores proposal results so refresh keeps “Created action” state

### 9.3 LangGraph integration (Option A)
When `ZAKOPS_BRAIN_MODE=auto|force`:
- The 8080 brain is allowed to generate `create_action` proposals with typed `inputs`
- 8090 remains the stable persistence layer (authoritative action record creation)

---

## 10) R6 — Frontend UX Upgrade (No Redesign; Functionality Upgrade Only)

### 10.1 Actions page
Upgrade `/home/zaks/zakops-dashboard/src/app/actions/page.tsx`:
- Render each action as an interactive card:
  - Title, type badge, status badge, deal_id, created_at
  - Expand/collapse details: editable inputs (before execution), outputs, error, audit timeline
- Buttons:
  - **Approve** (PENDING_APPROVAL → READY)
  - **Run** (READY → PROCESSING)
  - **Cancel**
  - **Retry** (FAILED → READY with audit)
- Completed actions show artifacts with **Download/View** immediately.

### 10.2 Deal detail page
Update `/home/zaks/zakops-dashboard/src/app/deals/[id]/page.tsx`:
- “Actions for this deal” rail shows kinetic actions (pending + recent).

### 10.3 Chat UX hook
When a `create_action` proposal is executed successfully:
- Add a system message: “Created action: <title>” with deep link to Actions page filtered to that action.

### 10.4 API client updates
Update `/home/zaks/zakops-dashboard/src/lib/api.ts`:
- Add Zod schemas for `ActionPayload` + artifacts list
- Add API functions for approve/execute/update/cancel/artifact download

---

## 11) R7 — Artifacts + DataRoom Integration (Must Work)

### 11.1 Storage convention (decision)
Artifacts are saved under the deal’s folder (from registry) in the **existing canonical subfolder taxonomy** (so humans can also find them on disk), with one per-action subfolder to avoid clutter:

`<deal.folder_path>/<CATEGORY>/<action_id>/`

Category mapping (initial):
- `COMMUNICATION.DRAFT_EMAIL` → `07-Correspondence`
- `DOCUMENT.GENERATE`:
  - LOI → `08-LOI-Offer`
  - NDA → `01-NDA`
  - other → `05-Legal`
- `ANALYSIS.BUILD_MODEL` → `06-Analysis`
- `PRESENTATION.GENERATE_DECK` → `06-Analysis`
- `DILIGENCE.REQUEST_DOCS` → `06-Analysis` (checklist + draft artifacts together)

Folder safety rule: create missing folders; never delete/move existing artifacts automatically.

Each artifact is recorded in DB with:
- `artifact_id`, filename, mime type, absolute path, sha256, created_at, size_bytes

### 11.2 Download endpoints
- Backend serves artifacts via `GET /api/actions/{action_id}/artifact/{artifact_id}`
- Use streaming response + correct `Content-Type` + `Content-Disposition` filename.

Artifact metadata (required; returned to UI):
- `artifact_id`, `filename`, `mime_type`, `path`, `size_bytes`, `created_at`
- `download_url` (precomputed `/api/actions/{action_id}/artifact/{artifact_id}`) so UI doesn’t have to construct routes

---

## 12) R8 — Testing (Rigorous; Proves End‑to‑End)

### 12.1 Backend tests (pytest)
Add tests proving:
- Schema validation (ActionPayload + per-type inputs)
- Executor unit tests (at least `dry_run` for each required action type)
- API tests:
  - create → approve → execute → completed
  - idempotency: same `idempotency_key` twice → same action record returned
  - artifact download returns file bytes and correct headers
- Runner tests:
  - lease prevents multiple runners
  - crash recovery: stuck PROCESSING with expired lease is re-queued safely
  - retry policy: failed execution increments `retry_count` and respects `max_retries`

### 12.2 UI tests
Extend existing click-sweep tests (or add minimal Playwright if supported):
- Actions page renders interactive card
- Approve/Run triggers state changes
- Artifacts appear and download link is present after completion

If Playwright infra is not available in CI, include deterministic scripted steps in the Verification Report.

---

## 13) R9 — Documentation + Runbook

Create docs (implementation will place them under `/home/zaks/zakops-dashboard/docs/` to keep them with the product repo):
- `docs/ACTIONS-ENGINE.md`
  - schema, DB tables, executor interface, how to add new action type
- `docs/ACTIONS-RUNBOOK.md`
  - how to run runner, debug stuck actions, clear leases safely, where logs live
- Operator safety checklist:
  - “one runner only” verification
  - idempotency keys required
  - safe failure modes + retry rules

---

## 14) Acceptance Criteria (DoD) + Verification Report

### Must pass
1) From Chat (deal scope): “Draft an LOI for DEAL-2025-001”
   - Chat produces `create_action` proposal (or direct action record) visible in Actions page.
2) Actions page shows it `PENDING_APPROVAL`.
3) Approve → becomes `READY`.
4) Run → becomes `PROCESSING` then `COMPLETED`.
5) A DOCX (and optional PDF) artifact is generated under the deal folder and downloadable.
6) Re-running “create action” with same idempotency key does **not** create duplicates.
7) All tests pass.

### Verification Report (deliverable)
Produce `KINETIC-ACTION-ENGINE-VERIFICATION-REPORT.md` with:
- curl commands for create/approve/execute/poll/download
- DB queries demonstrating idempotency + audit trail
- UI screenshots or terminal outputs (as available)
