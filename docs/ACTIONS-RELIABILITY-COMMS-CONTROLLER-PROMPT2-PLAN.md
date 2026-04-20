# PROMPT 2 Plan — Actions Reliability + Executor Guarantees + Gemini Draft + Approval-Gated Send + Deal Lifecycle Controller

Date: 2026-01-03

## Scope / Non‑Negotiables (must hold)
- No auto-send / no auto-delete.
- No LangSmith tracing enablement.
- Approval gates for any irreversible action (email send, etc.).
- Backward compatible API contracts for the dashboard:
  - Kinetic Actions endpoints under `http://localhost:8090/api/actions/*`
  - Chat endpoints under `http://localhost:8090/api/chat*`
- No secrets in git or logs; secret-scan gates remain enforced for cloud/tool calls.

## Current baseline (what already exists)
- Action state machine is implemented in `scripts/actions/engine/store.py`:
  - `PENDING_APPROVAL → READY` (`approve_action`)
  - `READY → PROCESSING` only when the runner claims it (`begin_processing`)
  - `PROCESSING → COMPLETED|FAILED` (`mark_action_completed`)
  - Watchdog TTL: `mark_processing_timeouts`
  - Runner lease + per-action locks + heartbeat in `scripts/actions_runner.py`
- Runner observability exists:
  - `GET /api/actions/runner-status`
  - `GET /api/actions/metrics`
  - `GET /api/actions/{action_id}/debug`
- Comms actions exist:
  - `COMMUNICATION.DRAFT_EMAIL` executor + capability
  - `COMMUNICATION.SEND_EMAIL` executor + capability
- ToolGateway exists (`scripts/tools/gateway.py`) with:
  - explicit enable flag `ZAKOPS_TOOL_GATEWAY_ENABLED=true`
  - explicit allowlist `ZAKOPS_TOOL_ALLOWLIST=...`
  - DB-backed approval gate and secret scanning
- Known friction in production UX:
  - missing executor failures for certain action types
  - tool gateway disabled / missing MCP command wiring
  - cloud gating confusion across executors
  - occasional API contract nullability mismatches
  - controller loop not implemented (no continuous next-best action proposals)

---

## Phase 0 — Inventory & Findings (no behavior changes)
Deliverable: `bookkeeping/docs/PROMPT2_INVENTORY_AND_FINDINGS.md`

1) Inventory executors and capabilities
- Enumerate built-in executors: `scripts/actions/executors/registry.py`
- Enumerate capability manifests: `scripts/actions/capabilities/*.yaml`
- Identify mismatches:
  - capability exists but executor missing
  - executor exists but not registered
  - capability YAML invalid (cannot load)
  - capability action_type != executor action_type

2) Inventory ToolGateway + Gmail MCP wiring
- Verify ToolGateway defaults and current env flags:
  - `ZAKOPS_TOOL_GATEWAY_ENABLED`
  - `ZAKOPS_TOOL_ALLOWLIST`
  - `ZAKOPS_MCP_RUNTIME_MODE`
- Verify the Gmail tool manifests and stdio command paths:
  - `scripts/tools/manifests/gmail__send_email.yaml`
  - confirm the referenced `mcp_stdio_command` is actually runnable under the runner service.

3) Baseline real-world failure signatures (collect from DB)
- Query action errors grouped by `error.code`:
  - `executor_not_found`
  - `tool_gateway_disabled`
  - `cloud_disabled`
  - `gemini_*`

Acceptance: A single doc with concrete file paths + command outputs + a mismatch list we will close in Phases A–E.

---

## Phase A — Action engine reliability hardening (P0)
Goal: eliminate stuck/ambiguous action states, and make failures crisp + observable.

A1) Tighten transition invariants (tests-first)
- Add unit tests that prove:
  - approve invalid transitions → `409`
  - execute invalid transitions → `409`
  - runner always releases locks and records audit events on exception
- Ensure “execution requested” (`/execute`) never forces `PROCESSING` (already the design); verify via tests.

A2) “Never stuck” enforcement
- Confirm/strengthen:
  - watchdog TTL path always results in `FAILED` + audit event
  - per-action heartbeat updates lock heartbeat
  - runner always `release_action_lock` in a `finally` (already; keep)
- Add a small admin-safe endpoint (optional if missing):
  - `POST /api/actions/{action_id}/unstick` → delegates to `store.unstick_action`

A3) Runner status UX upgrade
- Extend `GET /api/actions/runner-status` to include:
  - `queue_counts_by_status` (already via metrics; keep stable)
  - `stuck_processing.count` + sample IDs
  - `last_error_breakdown` (top N error codes last 24h)
  - optionally `active_locks` (if cheap to compute)

Acceptance:
- Runner-status provides enough signal to operate without tailing logs.
- A failed executor/tool call always ends in `FAILED` with `{code,message,details}` and an audit event.

---

## Phase B — Executor registration guarantees (P0)
Goal: prevent creation of actions that cannot run; surface legacy mismatches with operator tooling.

B1) Creation-time validation (single source of truth)
Implement a shared validator (new module, used by both API and internal creators):
- Inputs:
  - `action_type`
  - `capability_id` (optional)
  - `inputs`
- Validations:
  1) `action_type` resolves to a registered executor
     - includes `TOOL.*` via ToolInvokeExecutor
  2) if `capability_id` is present:
     - capability exists and loads
     - capability.action_type matches `action_type`
  3) if capability implies cloud/tool requirements:
     - mark as “requires configuration” if missing prerequisites (do not silently accept)

API behavior:
- `POST /api/actions` returns `400` with a structured error for mismatches (no DB write).
- Existing actions remain readable; legacy broken rows are handled by the debug detector.

B2) Debug endpoints for ops
Add:
- `GET /api/actions/debug/missing-executors`
  - returns list of action_ids (limit + pagination) whose `action_type` has no executor
  - includes suggested remediation (register executor vs cancel/requeue)
- `GET /api/actions/debug/capability-mismatches`
  - capability missing / invalid / action_type mismatch

B3) UI treatment (minimal, backwards-compatible)
- Do not add new action statuses (avoid breaking FE enums).
- Map “blocked” UX to:
  - `status=FAILED` + `error.code in {executor_not_found, capability_missing, tool_gateway_disabled, gemini_api_key_missing}`
- UI should display “Needs configuration” / “Executor missing” with the error code and a short operator next step.

Acceptance:
- New broken actions cannot be created from UI/chat/triage.
- Existing broken actions are discoverable via the debug endpoints.

---

## Phase C — World-class Comms Loop (P0/P1)
Goal: Draft → approve → send works deterministically and safely; no “send it” redraft loops.

C1) Drafting: Gemini 2.5 + strict JSON output + artifacts
Standardize `COMMUNICATION.DRAFT_EMAIL`:
- Provider: Gemini “Pro standard” (Gemini 2.5 Pro)
- Output contract (strict JSON):
  `{ "subject": "...", "body": "...", "cc": [...optional...], "bcc": [...optional...] }`
- Persist artifacts:
  - `email_draft.md` (human copy/paste)
  - `email_draft.json` (structured)
  - include provider/model/latency in action `outputs`
- Failure behavior:
  - If Gemini is not configured → fail clearly with `error.code=gemini_api_key_missing` (or equivalent) and an operator-facing message.

C2) Cloud gating consistency (per-action, approval-gated)
Unify cloud usage across all comms executors:
- Capabilities that may call cloud set `cloud_required: true` in their YAML.
- Runner sets `ctx.cloud_allowed` based on the capability manifest and the fact the action is approved/executing.
- Executors never rely on `ALLOW_CLOUD_DEFAULT` for approved actions.

C3) Sending: separate action + ToolGateway + Gmail MCP
Standardize `COMMUNICATION.SEND_EMAIL`:
- Must be a distinct action type (already) and always approval-required.
- Executes via ToolGateway using the Gmail MCP tool (not IMAP/SMTP).
- Persist send result:
  - `send_result.json` includes `{message_id, thread_id, provider/tool_name, timestamp}`

Critical wiring task:
- Ensure ToolGateway can actually launch the Gmail MCP server referenced by tool manifests.
  - Either update tool manifests to use the known working `npx -y @gongrzhe/server-gmail-autoauth-mcp`, or provide a stable local wrapper command installed on PATH.
  - Enable ToolGateway **only** with a tight allowlist (at minimum `gmail__send_email`) and keep secrets out of git.

C4) Chat “send it” behavior
Make chat deterministic:
- If a latest draft artifact exists for the deal:
  - propose `create_action` → `COMMUNICATION.SEND_EMAIL` referencing `body_artifact_path`
  - do not propose re-draft
- If no draft exists:
  - propose `COMMUNICATION.DRAFT_EMAIL`

Acceptance:
- Draft is always Gemini 2.5 (or explicit “blocked: needs configuration”).
- Send uses ToolGateway and produces a stable send result artifact.
- “Send it” does not loop back into drafting if a usable draft already exists.

---

## Phase D — Post-approval materials pipeline alignment (P1/P2)
Goal: once a deal is created, the system can run follow-on extraction/enrichment actions.

D1) Ensure executors are registered for existing deal/material actions
Verify/close gaps so these are callable and appear in `/api/actions/capabilities`:
- `DEAL.CREATE_FROM_EMAIL`
- `DEAL.EXTRACT_EMAIL_ARTIFACTS`
- (Add if missing) `DEAL.ENRICH_MATERIALS`
- (Optional) `RAG.REINDEX_DEAL`

D2) Auth-required link queueing
If ingestion surfaces `auth_required=true` links:
- create a review action (approval-gated) with safe, scrubbed URLs (no tokens)
- store link list in artifacts/outputs

Acceptance:
- After deal creation, operator can run extraction/enrichment actions from Actions UI.

---

## Phase E — P2 Deal Lifecycle Controller loop (“Deal OS”)
Goal: move from cron/scripts to a durable, deal-centric system that proposes next-best actions continuously.

E1) Controller architecture
Implement a periodic controller (hourly, systemd timer) that:
- reads Deal Registry + recent events + case files + action memory summaries
- computes stage-aware next-best actions (deterministic-first)
- creates approval-gated Kinetic Actions (no auto-execution)
- uses strong idempotency keys to avoid duplicates

E2) Controller proposal rules (initial deterministic set)
Examples (all approval-gated):
- Inbound + no NDA: propose `DILIGENCE.REQUEST_DOCS` (or a dedicated “request NDA” capability)
- Screening + no financials: propose `DILIGENCE.REQUEST_DOCS` for LTM financials
- If recent broker email received and unanswered: propose `COMMUNICATION.DRAFT_EMAIL`
- If NDA signed and materials complete: propose `DOCUMENT.GENERATE_LOI`

E3) Memory + deduping
- Use ActionStore queries + action memory store:
  - do not propose the same action type if a similar one is already `PENDING_APPROVAL/READY/PROCESSING`
  - backoff if last attempt failed recently with same inputs
  - renew proposals only after a cooldown window

Acceptance:
- Controller proposes useful actions without spamming duplicates.
- All proposals remain approval-gated and reversible where possible.

---

## Test plan (must fail before / pass after)
1) API contract tests:
- create action with unknown executor → `400` and no DB row
- create action with capability mismatch → `400`
- runner-status includes expected fields
2) Executor registry tests:
- every capability action_type has a registered executor (or explicitly marked tool-only)
3) Comms tests:
- Draft email produces `email_draft.md` + `email_draft.json` and records provider/model
- Send email calls ToolGateway tool (mocked) and stores send result artifacts
4) Controller tests:
- dedupe/idempotency: no duplicate proposals generated across runs

---

## Evidence required at implementation completion
- Curl proof of transitions and validation errors
- Runner logs showing lease acquisition and action completion
- Demo: `COMMUNICATION.DRAFT_EMAIL` → approve/execute → `COMMUNICATION.SEND_EMAIL` → approve/execute
- Debug endpoint output showing no missing executors
- Test outputs (unit tests + any added integration tests)

---

## Rollout / Safety
- Ship Phase B validation with a feature flag if needed (`ZAKOPS_ENFORCE_ACTION_REGISTRATION=true`) to avoid surprising legacy flows; default ON in production after validation.
- ToolGateway enablement requires explicit operator config:
  - keep allowlist minimal
  - document exact env vars in a runbook section
- Controller starts in “dry-run / propose-only” mode (writes actions, never executes).

