# Quarantine → Approve → Deal (Current State Map)

This document describes **what happens today** when an email lands in Quarantine and an operator clicks **Approve** (or **Reject**), including the exact API calls, action types/executors, and what gets written to disk/DB.

## 1) UI Surface

- UI route: `zakops-dashboard/src/app/quarantine/page.tsx`
- Backing API client: `zakops-dashboard/src/lib/api.ts`

## 2) Canonical Data Stores (Source of Truth)

### Deals (canonical)

- Canonical store: `DataRoom/.deal-registry/deal_registry.json`
- Read/write module: `scripts/deal_registry.py` (`class DealRegistry`)
- Served via API: `scripts/deal_lifecycle_api.py` `@app.get("/api/deals")` (`list_deals`, `scripts/deal_lifecycle_api.py:432`)

### Actions + Quarantine (canonical)

- Canonical store: SQLite action store at `ZAKOPS_STATE_DB` (env-driven)
- Engine module: `scripts/actions/engine/store.py` (`class ActionStore`)
- Quarantine “queue” is **action-backed**, not filesystem-backed:
  - Type: `EMAIL_TRIAGE.REVIEW_EMAIL`
  - Status: `PENDING_APPROVAL`
  - Excludes hidden items (`hidden_from_quarantine=0`)
  - API endpoint: `GET /api/actions/quarantine` (`scripts/deal_lifecycle_api.py:1989`)

### Deal filesystem workspace (derived view)

- Workspace root: `DataRoom/00-PIPELINE/Inbound/<DealFolder>/`
- Created only after approval via executor logic.

## 3) Quarantine UI → API Calls (Current)

### 3.1 Load queue (left panel)

- UI calls: `getQuarantineQueue({limit, offset})` (`zakops-dashboard/src/lib/api.ts:648`)
- Backend endpoint: `GET /api/actions/quarantine?limit=...&offset=...` (`scripts/deal_lifecycle_api.py:1989`)
- Response items are normalized “quarantine items” derived from kinetic actions:
  - See `_triage_action_to_quarantine_item()` (`scripts/deal_lifecycle_api.py:1944`)

### 3.2 Load preview (right panel)

- UI calls: `getQuarantinePreview(actionId)` (`zakops-dashboard/src/lib/api.ts:675`)
- Backend endpoint: `GET /api/actions/quarantine/{action_id}/preview` (`scripts/deal_lifecycle_api.py:2025`)
- Preview payload is **local-only**:
  - Reads `email_body.txt` from `inputs.quarantine_dir` (bounded under `DATAROOM_ROOT`)
  - Echoes attachments metadata + link grouping (best-effort)

### 3.3 Approve (creates deal + starts ingestion chain)

- UI handler: `handleApprove()` (`zakops-dashboard/src/app/quarantine/page.tsx`)
- API sequence:
  1) `POST /api/actions/{action_id}/approve` (`scripts/deal_lifecycle_api.py:1305`)
  2) `POST /api/actions/{action_id}/execute` (`scripts/deal_lifecycle_api.py:1330`)
  3) Poll: `GET /api/actions/{action_id}` until terminal (`COMPLETED|FAILED|CANCELLED`)

Frontend helper that performs (1)+(2):
- `approveQuarantineItem()` (`zakops-dashboard/src/lib/api.ts:693`)

### 3.4 Reject (atomic; does not create a deal)

- UI handler: `handleReject()` (`zakops-dashboard/src/app/quarantine/page.tsx`)
- Backend endpoint: `POST /api/actions/quarantine/{action_id}/reject` (`scripts/deal_lifecycle_api.py:2208`)
- Behavior (current):
  - Creates a separate reject action (`EMAIL_TRIAGE.REJECT_EMAIL`)
  - Executes the reject action
  - Cancels the original `EMAIL_TRIAGE.REVIEW_EMAIL` action
  - Marks the thread as non-deal for future routing
  - Intended to apply Gmail label(s) via Gmail MCP (approval gated by operator action)

Frontend helper:
- `rejectQuarantineItem()` (`zakops-dashboard/src/lib/api.ts:712`)

## 4) What Approve Executes (Action Types + Executors)

### 4.1 Primary action: `EMAIL_TRIAGE.REVIEW_EMAIL`

- Executor: `EmailTriageReviewEmailExecutor` (`scripts/actions/executors/email_triage_review_email.py:273`)
- Trigger: runner executes after approval + execute requested
- Main responsibilities (current):
  1) Resolve deal target:
     - If `inputs.link_deal_id` provided → attach to that deal
     - Else: use registry mappings:
       - `message_id → deal_id`
       - `thread_id → deal_id`
     - Else: best-effort matcher fallback (`DealMatcher`)
     - See: `execute()` matching tiers (`scripts/actions/executors/email_triage_review_email.py:332`)
  2) If no existing deal is found:
     - Resolve a business-name-first display name (`_resolve_deal_display_name`) (`scripts/actions/executors/email_triage_review_email.py:399`)
     - Generate `deal_id` via `DealRegistry.generate_deal_id()` (`scripts/actions/executors/email_triage_review_email.py:406`)
     - Create deal folder:
       - `DataRoom/00-PIPELINE/Inbound/<slug>--<deal_id_suffix>/`
       - See folder rule: (`scripts/actions/executors/email_triage_review_email.py:409`)
     - Create standard subfolders + `README.md` (`_create_deal_workspace`, `scripts/actions/executors/email_triage_review_email.py:185`)
     - Create/update registry record + thread/email mappings and save:
       - `registry.create_deal(...)` + mappings + `registry.save()` (`scripts/actions/executors/email_triage_review_email.py:441`)
  3) Output a follow-on step chain via `outputs.next_actions[]`:
     - `DEAL.APPEND_EMAIL_MATERIALS` (auto-approved) (`scripts/actions/executors/email_triage_review_email.py:501`)

**Important**: This executor **does not** copy the entire email/attachments into the deal folder itself; it creates the deal + mappings and queues the follow-on ingestion action.

### 4.2 Follow-on action 1: `DEAL.APPEND_EMAIL_MATERIALS` (auto-approved)

- Executor: `AppendEmailMaterialsExecutor` (`scripts/actions/executors/deal_append_email_materials.py:111`)
- Enqueued by runner from `outputs.next_actions`:
  - Runner chaining logic: `_enqueue_follow_on_actions()` (`scripts/actions_runner.py:87`) called from `process_one_action()` (`scripts/actions_runner.py:395`)
- Writes an append-only correspondence bundle:
  - Bundle directory:
    - `<deal>/07-Correspondence/<timestamp>_<short-message-id>/`
    - See: bundle creation (`scripts/actions/executors/deal_append_email_materials.py:185`)
  - Files written in the bundle (first creation only):
    - `email.md` (`scripts/actions/executors/deal_append_email_materials.py:199`)
    - `email.json` (`scripts/actions/executors/deal_append_email_materials.py:200`)
    - `manifest.json` (`scripts/actions/executors/deal_append_email_materials.py:201`)
    - `links.json` (`scripts/actions/executors/deal_append_email_materials.py:202`)
    - `pending_auth_links.json` (`scripts/actions/executors/deal_append_email_materials.py:203`)
    - `attachments/` (copies safe files from quarantine dir) (`scripts/actions/executors/deal_append_email_materials.py:204`)
  - Updates aggregate deal-level links inventory:
    - `<deal>/07-Correspondence/links.json` (`scripts/actions/executors/deal_append_email_materials.py:309`)
  - Emits next_actions chain:
    - `DEAL.EXTRACT_EMAIL_ARTIFACTS`
    - `DEAL.ENRICH_MATERIALS`
    - `DEAL.DEDUPE_AND_PLACE_MATERIALS`
    - `RAG.REINDEX_DEAL`
    - See: (`scripts/actions/executors/deal_append_email_materials.py:351`)

### 4.3 Follow-on chain (auto-approved)

These are enqueued from the append action (all `requires_approval=false` today):

- `DEAL.EXTRACT_EMAIL_ARTIFACTS` → `scripts/actions/executors/deal_extract_email_artifacts.py`
- `DEAL.ENRICH_MATERIALS` → `scripts/actions/executors/deal_enrich_materials.py`
- `DEAL.DEDUPE_AND_PLACE_MATERIALS` → `scripts/actions/executors/deal_dedupe_and_place_materials.py`
- `RAG.REINDEX_DEAL` → `scripts/actions/executors/rag_reindex_deal.py`

## 5) Why “Approve” Creates a Deal + What It Writes

When the `EMAIL_TRIAGE.REVIEW_EMAIL` action completes successfully:

- Deal registry record is created/updated:
  - `DataRoom/.deal-registry/deal_registry.json`
- Deal folder is created:
  - `DataRoom/00-PIPELINE/Inbound/<slug>--<suffix>/`
  - Standard subfolders + `README.md`
- Thread/email mappings are persisted:
  - `message_id → deal_id` (email_to_deal)
  - `thread_id → deal_id` (thread_to_deal)
- Email body + links + attachments are ingested in the subsequent append materials action:
  - `<deal>/07-Correspondence/...`
  - `<deal>/07-Correspondence/links.json`
  - Derived placement (CIM/NDA/etc) happens later via dedupe/place

## 6) Parameters That Drive Behavior

Key `inputs` fields on `EMAIL_TRIAGE.REVIEW_EMAIL` (present in the Quarantine action payload):

- `message_id` (required) — used for idempotency + routing
- `thread_id` — used for deterministic mapping/routing
- `subject`, `from`, `date` — used for naming + audit + bundle rendering
- `company` (optional) — influences name resolution
- `quarantine_dir` — points to the quarantine payload folder containing `email_body.txt` and downloaded attachments
- `links[]`, `attachments[]` — passed into the append action for link inventory + attachment copy
- `confidence`, `classification`, `urgency` — shown in UI + propagated into materials chain

## 7) Runner Involvement (Why “Execute” Actually Runs)

- Runner service: `kinetic-actions-runner.service` runs `scripts/actions_runner.py`
- It acquires a DB lease and polls READY actions; once claimed it transitions actions to PROCESSING and executes them.
- Chaining: after completion it enqueues `outputs.next_actions[]` (`scripts/actions_runner.py:393`)

## 8) Known Gaps (Current State)

- Deal deletion/archival is registry-backed; previously a stale in-memory registry in the runner could overwrite deletions. Runner now loads a fresh registry per action (`scripts/actions_runner.py:678`).
- The review action does not itself write full email/attachment artifacts into the deal; it relies on the follow-on ingestion action chain.
