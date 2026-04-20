AGENT IDENTITY
- agent_name: Codex
- agent_version: GPT-5
- run_id: 20260204-003640-02b34c
- repo_revision: a09538f04ed278c32ad6f2a037069b353bf5f797
- date_time: 2026-02-04T00:41:03Z

## Executive Summary (what "Deal" is in code today)
- The running backend container serves the orchestration API (CMD in `Dockerfile`) which treats a Deal as a Postgres row in `zakops.deals` created via `/api/deals` and read via `/api/deals` and `/api/deals/{deal_id}`. (refs: `Dockerfile`, `src/api/orchestration/main.py:create_deal`, `src/api/orchestration/main.py:list_deals`, `db/init/001_base_tables.sql:zakops.deals`)
- A parallel, legacy Deal exists in the DataRoom JSON registry (`/home/zaks/DataRoom/.deal-registry/deal_registry.json`) and is used by the legacy deal_lifecycle API and some action executors; this is separate from Postgres. (refs: `src/core/deal_registry.py:Deal`, `src/api/deal_lifecycle/main.py:get_registry`, `src/actions/executors/deal_create_from_email.py:CreateDealFromEmailExecutor`)
- Quarantine in the active backend is a DB table and `/api/quarantine/{id}/process` only updates status and optional linkage; it does not create a deal. (refs: `db/init/001_base_tables.sql:zakops.quarantine_items`, `src/api/orchestration/main.py:process_quarantine`)
- Agent-driven deal transitions are available via the `transition_deal` tool but require HITL approvals stored in the agent DB. (refs: `apps/agent-api/app/core/langgraph/tools/deal_tools.py:transition_deal`, `apps/agent-api/app/schemas/agent.py:HITL_TOOLS`, `apps/agent-api/app/models/approval.py:Approval`)

## Canonical Deal Data Model (as implemented)
### Postgres (active backend)
- `zakops.deals` (primary Deal record): `deal_id`, `canonical_name`, `display_name`, `folder_path`, `stage`, `status`, `identifiers`, `company_info`, `broker`, `metadata`, `deleted`, `created_at`, `updated_at`. (refs: `db/init/001_base_tables.sql:zakops.deals`, `src/api/orchestration/main.py:DealBase`, `src/api/orchestration/main.py:DealResponse`)
- `zakops.deal_events` (event history): `deal_id`, `event_type`, `event_source`, `actor`, `payload`, `created_at`. (refs: `db/init/001_base_tables.sql:zakops.deal_events`, `src/api/orchestration/main.py:get_deal_events`)
- `zakops.deal_aliases` (alternate identifiers): `deal_id`, `alias`, `alias_type`, `created_at`. (refs: `db/init/001_base_tables.sql:zakops.deal_aliases`, `src/api/orchestration/main.py:get_deal_aliases`)
- `zakops.quarantine_items` (email quarantine): `id`, `deal_id`, `sender`, `subject`, `message_id`, `body_preview`, `raw_content`, `reason`, `confidence`, `status`, `reviewed_by`, timestamps. (refs: `db/init/001_base_tables.sql:zakops.quarantine_items`, `src/api/orchestration/main.py:create_quarantine_item`)
- `zakops.actions` (workflow actions): `action_id`, `deal_id`, `action_type`, `status`, `requires_approval`, etc. (refs: `db/init/001_base_tables.sql:zakops.actions`, `src/api/orchestration/main.py:list_actions`)

### Legacy file-based stores (still present in code)
- Deal registry JSON (`/home/zaks/DataRoom/.deal-registry/deal_registry.json`) with fields like `deal_id`, `canonical_name`, `display_name`, `folder_path`, `stage`, `status`, `metadata`, `aliases`, etc. (refs: `src/core/deal_registry.py:Deal`, `src/api/deal_lifecycle/main.py:get_registry`)
- Deal event JSONL store in DataRoom (`/home/zaks/DataRoom/.deal-registry/events`), used by `DealEventStore`. (refs: `/home/zaks/scripts/deal_events.py:DealEventStore`, `src/api/deal_lifecycle/main.py:get_event_store`)
- Quarantine JSON (`/home/zaks/DataRoom/.deal-registry/quarantine.json`) used by `QuarantineManager` in the legacy pipeline. (refs: `/home/zaks/scripts/lifecycle_event_emitter.py:QuarantineManager`, `src/api/deal_lifecycle/main.py:get_quarantine`)
- Actions SQLite store (`ZAKOPS_STATE_DB`, default `/home/zaks/DataRoom/.deal-registry/ingest_state.db`). (refs: `src/actions/engine/store.py:_default_state_db_path`, `src/actions/engine/store.py:SCHEMA_SQL`)

### Agent HITL persistence (separate DB)
- `approvals`, `tool_executions`, `audit_log` tables in agent DB for HITL gating and tool execution audit. (refs: `apps/agent-api/app/models/approval.py:Approval`, `apps/agent-api/app/models/approval.py:ToolExecution`, `apps/agent-api/app/models/approval.py:AuditLog`)

### Source of truth (current runtime)
- The backend container runs the orchestration API (not the legacy deal_lifecycle API), so Postgres is the active deal source of truth at runtime. (refs: `Dockerfile`, `src/api/orchestration/main.py:create_deal`)
- The legacy deal_lifecycle API and DataRoom registry remain in code and are used by some action executors, creating split-brain risk. (refs: `src/api/deal_lifecycle/main.py:list_deals`, `src/actions/executors/deal_create_from_email.py:CreateDealFromEmailExecutor`, `src/core/deal_registry.py:Deal`)

## Deal State Machine (as implemented)
### Active backend (orchestration API + core workflow)
- Stages: `inbound`, `screening`, `qualified`, `loi`, `diligence`, `closing`, `portfolio`, `junk`, `archived`. (refs: `src/core/deals/workflow.py:DealStage`, `src/api/orchestration/main.py:ValidStage`, `db/migrations/023_stage_check_constraint.sql:chk_deals_stage`)
- Allowed transitions (from `STAGE_TRANSITIONS`):
  - inbound -> screening | junk | archived
  - screening -> qualified | junk | archived
  - qualified -> loi | junk | archived
  - loi -> diligence | qualified | junk | archived
  - diligence -> closing | loi | junk | archived
  - closing -> portfolio | diligence | junk | archived
  - portfolio -> archived
  - junk -> inbound | archived
  - archived -> (no transitions)
  (refs: `src/core/deals/workflow.py:STAGE_TRANSITIONS`)
- Trigger path: `/api/deals/{deal_id}/transition` (workflow router) -> `DealWorkflowEngine.transition_stage` (DB update + deal_events). (refs: `src/api/orchestration/routers/workflow.py:transition_deal_stage`, `src/core/deals/workflow.py:transition_stage`)

ASCII diagram (active backend):
```
inbound -> screening -> qualified -> loi -> diligence -> closing -> portfolio -> archived
   |          |             |          |          |          |
   +-> junk   +-> junk      +-> junk   +-> qualified +-> loi +-> diligence
   +-> archived (from inbound/screening/qualified/loi/diligence/closing/junk/portfolio)
   junk -> inbound
```
(refs: `src/core/deals/workflow.py:STAGE_TRANSITIONS`)

### Conflicting / legacy state machines (NEEDS VERIFICATION)
- Legacy `deal_state_machine.py` defines a different set of stages (integration, operations, growth, exit_planning, closed_won/lost) and transition rules. (refs: `/home/zaks/scripts/deal_state_machine.py:DealStage`, `/home/zaks/scripts/deal_state_machine.py:TRANSITIONS`)
- `DealRegistry` comments list different terminal labels (`archive`, `rejected`) not present in the DB constraint or active workflow. (refs: `src/core/deal_registry.py:Deal`)

## End-to-End "Deal Story" (Quarantine -> Terminal)
1) Quarantine ingestion (DB-backed): email ingestion should POST to `/api/quarantine`, which inserts into `zakops.quarantine_items` and deduplicates by `message_id`. (refs: `src/api/orchestration/main.py:create_quarantine_item`, `db/init/001_base_tables.sql:zakops.quarantine_items`)
2) Quarantine review (dashboard): UI calls `/api/actions/quarantine`, which fetches backend `/api/quarantine` and normalizes fields for display. (refs: `apps/dashboard/src/app/api/actions/quarantine/route.ts:GET`, `src/api/orchestration/main.py:list_quarantine`)
3) Quarantine decision (active backend): `/api/quarantine/{id}/process` marks status approved/rejected and optionally sets `deal_id` only; it does not create a deal. (refs: `src/api/orchestration/main.py:process_quarantine`)
4) Deal creation (manual/explicit): `/api/deals` POST generates `DL-XXXX` via `zakops.next_deal_id()` and inserts into `zakops.deals`, recording `deal_created`. (refs: `db/init/001_base_tables.sql:zakops.next_deal_id`, `src/api/orchestration/main.py:create_deal`)
5) Pipeline visibility: `/api/pipeline/summary` reads `zakops.v_pipeline_summary` (stage counts + avg age). (refs: `src/api/orchestration/main.py:get_pipeline_summary`, `db/migrations/023_stage_check_constraint.sql:v_pipeline_summary`)
6) Stage transitions: `/api/deals/{id}/transition` validates transitions, enforces idempotency, updates `zakops.deals`, and writes `deal_events`. (refs: `src/api/orchestration/routers/workflow.py:transition_deal_stage`, `src/core/deals/workflow.py:transition_stage`)
7) Agent-driven transitions (HITL): `/agent/invoke` can call `transition_deal` tool, which hits `/api/deals/{id}/transition` and requires approval in agent DB. (refs: `apps/agent-api/app/core/langgraph/tools/deal_tools.py:transition_deal`, `apps/agent-api/app/schemas/agent.py:HITL_TOOLS`, `apps/agent-api/app/core/langgraph/graph.py:_approval_gate`)
8) Terminal outcomes: `portfolio` can only go to `archived`; `junk` can return to `inbound` or `archived`; `archived` is terminal. (refs: `src/core/deals/workflow.py:STAGE_TRANSITIONS`)
9) Legacy path (if deal_lifecycle API is run): `/api/quarantine/{id}/resolve` can create a deal in the JSON registry or via the SQLite action store; this is separate from Postgres and not used by the backend container. (refs: `src/api/deal_lifecycle/main.py:resolve_quarantine`, `src/actions/engine/store.py`, `Dockerfile`)

## Scenarios & Edge Cases (exhaustive)
- New deal enters quarantine (happy path): PARTIALLY IMPLEMENTED. DB quarantine insert works; approval only updates status and does not create deal. (refs: `src/api/orchestration/main.py:create_quarantine_item`, `src/api/orchestration/main.py:process_quarantine`)
- Duplicate deal detection: PARTIALLY IMPLEMENTED. Quarantine deduplicates by `message_id`; legacy registry has alias matching; no DB-level duplicate deal detection. (refs: `src/api/orchestration/main.py:create_quarantine_item`, `src/core/deal_registry.py:DealMatcher`)
- Approval flow (HITL) approve/reject/timeout: IMPLEMENTED in agent API for `transition_deal`; approvals track `pending/approved/rejected/expired/claimed`. (refs: `apps/agent-api/app/models/approval.py:ApprovalStatus`, `apps/agent-api/app/api/v1/agent.py:approve/reject`, `apps/agent-api/app/core/langgraph/graph.py:_approval_gate`)
- Manual user edits from dashboard: NEEDS VERIFICATION. API supports PATCH `/api/deals/{id}`; UI wiring for edit fields is not in scope here. (refs: `src/api/orchestration/main.py:update_deal`)
- Agent-driven updates (tool calls): IMPLEMENTED. `transition_deal` tool calls `/api/deals/{id}/transition` with idempotency key and stage validation. (refs: `apps/agent-api/app/core/langgraph/tools/deal_tools.py:transition_deal`, `src/api/orchestration/routers/workflow.py:transition_deal_stage`)
- Missing auth token / permission denied: CONFIG-DEPENDENT. APIKeyMiddleware enforces `X-API-Key` for writes when `ZAKOPS_API_KEY` is set; dashboard middleware injects the key for writes. (refs: `src/api/shared/middleware/apikey.py:APIKeyMiddleware`, `apps/dashboard/src/middleware.ts`)
- Split-brain DB risk (agent DB vs backend DB; JSON vs Postgres): ACTIVE RISK. Postgres deals/quarantine are separate from DataRoom registry/events and SQLite action store. (refs: `db/init/001_base_tables.sql:zakops.deals`, `src/core/deal_registry.py:Deal`, `src/actions/engine/store.py:SCHEMA_SQL`)
- Deal exists in DB but not visible in UI: POSSIBLE if `deleted=true` or status != active (UI typically filters), and deals created only in registry JSON will not appear in `/api/deals`. (refs: `src/api/orchestration/main.py:list_deals`, `src/actions/executors/deal_create_from_email.py:CreateDealFromEmailExecutor`, `src/core/deal_registry.py:Deal`)
- UI shows deal but agent cannot list it: NEEDS VERIFICATION. Agent tool uses `DEAL_API_URL` and optional `ZAKOPS_API_KEY`; if misconfigured or API key enforced, reads or transitions may fail. (refs: `apps/agent-api/app/core/langgraph/tools/deal_tools.py:_get_backend_headers`, `src/api/shared/middleware/apikey.py:APIKeyMiddleware`)
- Partial failure: downstream RAG service down causes `search_deals` errors; no fallback when `ALLOW_TOOL_MOCKS` false. (refs: `apps/agent-api/app/core/langgraph/tools/deal_tools.py:search_deals`)
- Retry/idempotency behavior: IMPLEMENTED. Workflow engine supports idempotency keys; transition cooldown returns 429 within 30s. (refs: `src/core/deals/workflow.py:transition_stage`, `src/api/shared/middleware/cooldown.py:TransitionCooldownMiddleware`)
- Deletion/archive behavior: PARTIALLY IMPLEMENTED. DB has `deleted` flag but orchestration API lacks archive/restore endpoints; legacy API has archive/restore against JSON registry. (refs: `db/init/001_base_tables.sql:zakops.deals`, `src/api/deal_lifecycle/main.py:archive_deal`, `src/api/deal_lifecycle/main.py:restore_deal`)

## Brutally Honest Gap Analysis
1) Split-brain Deal sources (Postgres vs DataRoom JSON)
   - Evidence: `Dockerfile` (orchestration runtime), `db/init/001_base_tables.sql:zakops.deals`, `src/core/deal_registry.py:Deal`, `src/api/deal_lifecycle/main.py:list_deals`.
   - Impact: Deals created by legacy actions/pipeline are invisible in DB-backed UI and agent tooling; stage updates can diverge.
   - Severity: P0.
   - Remediation: Choose one source of truth; migrate DealRegistry to Postgres or retire legacy API, and add sync/migration if needed.

2) Quarantine approval does not create deals in active backend
   - Evidence: `src/api/orchestration/main.py:process_quarantine` (status update only).
   - Impact: Quarantine -> Deal is manual and error-prone; UI approvals do not create deals automatically.
   - Severity: P1.
   - Remediation: Add atomic approve endpoint that creates deal (or action) and writes to `zakops.deals`.

3) Dashboard uses legacy quarantine resolve endpoint
   - Evidence: `apps/dashboard/src/lib/api.ts:resolveQuarantineItem` calls `/api/quarantine/{id}/resolve`; active backend only exposes `/api/quarantine/{id}/process`. (refs: `src/api/orchestration/main.py:process_quarantine`, `src/api/deal_lifecycle/main.py:resolve_quarantine`)
   - Impact: Quarantine resolution from UI likely 404s against orchestration API.
   - Severity: P1.
   - Remediation: Update UI to call `/api/quarantine/{id}/process` or implement `/resolve` alias in orchestration API.

4) Stage taxonomy conflicts across components
   - Evidence: Active stages in `src/core/deals/workflow.py:DealStage` and DB constraint (`db/migrations/023_stage_check_constraint.sql`) differ from legacy `scripts/deal_state_machine.py:DealStage` and `src/core/deal_registry.py:Deal` comments; DB default stage is `lead` (not allowed). (refs: `db/init/001_base_tables.sql:zakops.deals`, `db/migrations/023_stage_check_constraint.sql`, `/home/zaks/scripts/deal_state_machine.py:DealStage`)
   - Impact: Invalid stage values, failed transitions, and inconsistent UI/agent expectations.
   - Severity: P1.
   - Remediation: Align all stage enums and defaults to the canonical list; remove/retire legacy stage machine.

5) Actions system split (Postgres vs SQLite)
   - Evidence: Orchestration API uses `zakops.actions` (Postgres); action engine uses SQLite `ZAKOPS_STATE_DB`. (refs: `src/api/orchestration/main.py:list_actions`, `src/actions/engine/store.py:SCHEMA_SQL`)
   - Impact: Actions created/executed by the engine may not appear in the UI or DB metrics; quarantine actions may split across stores.
   - Severity: P1.
   - Remediation: Consolidate actions into Postgres or migrate engine to use `zakops.actions`.

6) Deal notes endpoint mismatch
   - Evidence: UI calls `/api/deals/{id}/note` (legacy) but orchestration API does not define it; deal_lifecycle API does. (refs: `apps/dashboard/src/lib/api.ts:addDealNote`, `src/api/deal_lifecycle/main.py:add_deal_note`)
   - Impact: Deal note UI likely fails against active backend.
   - Severity: P2.
   - Remediation: Add `/api/deals/{id}/note` to orchestration API or update UI to new endpoint.

7) Actions capabilities/metrics not implemented
   - Evidence: `/api/actions/capabilities` and `/api/actions/metrics` return 501. (refs: `src/api/orchestration/main.py:get_action_capabilities`, `src/api/orchestration/main.py:get_action_metrics`)
   - Impact: Actions UI has limited functionality and cannot show capability metadata.
   - Severity: P2.
   - Remediation: Implement capability registry or provide a static list wired to executors.

## Comparison to Prior Assessment (MANDATORY)
### New findings vs prior report
- Active backend runs orchestration API (Postgres-first), not legacy deal_lifecycle API. (refs: `Dockerfile`, `src/api/orchestration/main.py`)
- Dashboard calls legacy `/api/quarantine/{id}/resolve` while orchestration exposes `/api/quarantine/{id}/process`. (refs: `apps/dashboard/src/lib/api.ts:resolveQuarantineItem`, `src/api/orchestration/main.py:process_quarantine`)
- Actions system is split between Postgres and SQLite engine, increasing drift risk. (refs: `src/api/orchestration/main.py:list_actions`, `src/actions/engine/store.py:SCHEMA_SQL`)

### Disagreements/conflicts vs prior report
- Prior report describes a single stage taxonomy; current code has at least two conflicting state machines (`core/deals/workflow.py` vs `scripts/deal_state_machine.py`). (refs: `src/core/deals/workflow.py:DealStage`, `/home/zaks/scripts/deal_state_machine.py:DealStage`)
- Prior report implies quarantine approval creates deals in DB; in orchestration it only updates status and optional `deal_id`. (refs: `src/api/orchestration/main.py:process_quarantine`)

### Confirmed items (both agree)
- DataRoom JSON registry is separate from Postgres deals. (refs: `src/core/deal_registry.py:Deal`, `db/init/001_base_tables.sql:zakops.deals`)
- Agent tool `transition_deal` is HITL-gated and calls backend `/api/deals/{id}/transition`. (refs: `apps/agent-api/app/core/langgraph/tools/deal_tools.py:transition_deal`, `apps/agent-api/app/schemas/agent.py:HITL_TOOLS`)
- RAG-backed `search_deals` depends on RAG REST service and can fail if down. (refs: `apps/agent-api/app/core/langgraph/tools/deal_tools.py:search_deals`)

## Verification Plan (proof, not vibes)
### Quarantine ingestion
- Create quarantine item:
  ```bash
  curl -s -X POST http://localhost:8091/api/quarantine \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ZAKOPS_API_KEY" \
    -d '{"message_id":"msg-123","email_subject":"Test","sender":"a@b.com","raw_body":"hi","confidence":0.9}'
  ```
  Evidence: `/api/quarantine` and `zakops.quarantine_items`. (refs: `src/api/orchestration/main.py:create_quarantine_item`, `db/init/001_base_tables.sql:zakops.quarantine_items`)
- Verify DB row:
  ```sql
  SELECT id, status, message_id FROM zakops.quarantine_items WHERE message_id='msg-123';
  ```
  (refs: `db/init/001_base_tables.sql:zakops.quarantine_items`)

### Quarantine decision
- Process quarantine:
  ```bash
  curl -s -X POST http://localhost:8091/api/quarantine/<id>/process \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ZAKOPS_API_KEY" \
    -d '{"action":"approve","processed_by":"operator"}'
  ```
  Expected: status changes, no deal created. (refs: `src/api/orchestration/main.py:process_quarantine`)

### Deal creation
- Create deal:
  ```bash
  curl -s -X POST http://localhost:8091/api/deals \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ZAKOPS_API_KEY" \
    -d '{"canonical_name":"Acme","stage":"inbound"}'
  ```
  Verify DB row:
  ```sql
  SELECT deal_id, stage, status FROM zakops.deals ORDER BY created_at DESC LIMIT 1;
  ```
  (refs: `src/api/orchestration/main.py:create_deal`, `db/init/001_base_tables.sql:zakops.deals`)

### Stage transitions
- Transition deal:
  ```bash
  curl -s -X POST http://localhost:8091/api/deals/<deal_id>/transition \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ZAKOPS_API_KEY" \
    -d '{"new_stage":"screening","reason":"test"}'
  ```
  Verify:
  ```sql
  SELECT stage FROM zakops.deals WHERE deal_id='<deal_id>';
  SELECT event_type, payload FROM zakops.deal_events WHERE deal_id='<deal_id>' ORDER BY created_at DESC LIMIT 1;
  ```
  (refs: `src/api/orchestration/routers/workflow.py:transition_deal_stage`, `src/core/deals/workflow.py:transition_stage`)

### Agent HITL
- Invoke agent (requires X-Service-Token):
  ```bash
  curl -s -X POST http://localhost:8095/agent/invoke \
    -H "X-Service-Token: $DASHBOARD_SERVICE_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"message":"Move DL-0001 to screening","thread_id":"verify-hitl"}'
  ```
  Verify approvals in agent DB:
  ```sql
  SELECT id, status, tool_name FROM approvals WHERE thread_id='verify-hitl';
  ```
  (refs: `apps/agent-api/app/api/v1/agent.py:invoke_agent`, `apps/agent-api/app/models/approval.py:Approval`)

### Legacy registry verification (if deal_lifecycle API is run)
- Inspect registry JSON:
  ```bash
  jq '.deals | keys' /home/zaks/DataRoom/.deal-registry/deal_registry.json
  ```
  (refs: `src/core/deal_registry.py:Deal`)

## Final Tough Gate (Self-Audit)
- [x] Every stage/state mentioned exists in code (or is marked NEEDS VERIFICATION)
- [x] Every scenario includes evidence refs or is marked NEEDS VERIFICATION
- [x] Gap list is actionable and prioritized
- [x] Appended (not overwrote) the master file with a Run Index Entry
- [x] Produced unique per-agent report + JSON with agent_name + run_id
