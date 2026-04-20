## Phase 1: Research Summary

### Deals
- Stored in `DataRoom/.deal-registry/deal_registry.json` via `scripts/deal_registry.py` (consumed by API, controller, triage, runner).  
- Canonical identifier: `deal_id` (format `DEAL-YYYY-NNN`) referenced by actions, materials filesystem, events, and chat.  
- Soft-delete metadata already exists on the registry record (`deleted_at`, `deleted_by`, `deleted_reason`).  
- Backend API already exposes soft-delete endpoints:
  - `POST /api/deals/{deal_id}/archive`
  - `POST /api/deals/bulk-archive`
  - `POST /api/deals/{deal_id}/restore`
- Referencing objects: action records (`deal_id`), correspondence bundles (filesystem folders named after deal slug), event/log files in `DataRoom/.deal-registry/events`, `actions_runner` events, planner memory, chat RAG evidence, mail triage metadata.

### Quarantine
- Represented by `EMAIL_TRIAGE.REVIEW_EMAIL` action rows stored in `ZAKOPS_STATE_DB` action table. Action rows include `inputs.quarantine_dir`, `metadata`, `status`.  
- Approve/reject flows (`/api/actions/{id}/approve`, `/api/actions/{id}/execute`, `/api/actions/{id}/cancel`) rely on action state transitions to create deals, emit follow-ons.  
- Quarantine queue shown via `/api/actions/quarantine` preview endpoint; items selected by `status=PENDING_APPROVAL`, `action_type=EMAIL_TRIAGE.REVIEW_EMAIL`.  
- IDs: `action_id` (primary), `message_id` accessible in inputs, `thread_id` for mapping.
- On approve, action transitions to READY/PROCESSING and triggers deal creation; on reject, action canceled and Gmail labels applied.  
- Deleting a quarantine item should not trigger approve/reject flows (no embedded side effects).
- Backend API already exposes safe quarantine deletion as “hide from queue” (no hard delete):
  - `POST /api/quarantine/{quarantine_id}/delete`
  - `POST /api/quarantine/bulk-delete`
  - The canonical quarantine list endpoints already exclude hidden items by default.

### Safety / Integrity
- Cannot hard delete deal directories; other workflows expect deal record exists and folder path accessible.  
- Removing action rows would break audit/tracking, risk losing thread mapping.  
- Soft delete preferable:
  * For deals: flag `deleted_at` or `hidden` in registry; exclude from `/api/deals` and tables but keep data for references.  
  * For quarantine: mark action with `hidden_from_quarantine` flag or `status=CANCELED` while preserving action record for audit events; default list filters should drop deleted items.
- Risks:
  * Hard delete deal referenced by actions, events, materials causing 404; soft delete withdrawal minimizes risk.
  * Quarantine deletion must not retrigger runner or mutate Gmail state; best to set `hidden_from_quarantine` and keep action terminal.

### Change Scope
- Files to modify:
 1. Backend: **no changes required** for delete support (endpoints already implemented).
 2. Frontend: `/zakops-dashboard/src/lib/api.ts` (add archive/delete calls), `/zakops-dashboard/src/app/deals` and `/zakops-dashboard/src/app/quarantine` components (add delete UI).
 3. Tests: frontend build check + optional lightweight UI smoke; backend endpoint tests only if gaps are found.

### Recommendations
- Use soft delete with boolean flags:
  * Add `deleted` boolean plus `deleted_at` timestamp on deals registry.  
  * Add `hidden_from_quarantine` boolean on actions or `quarantine_hidden_at` field; `status` of action remains (CANCELED if already canceled).  
- Update list endpoints `/api/deals` and `/api/actions/quarantine` to exclude deleted items.
  * For `/api/deals/{id}` return 404 if deleted.  
  * Provide new delete endpoints for single/bulk operations per spec (admin gate: reuse existing `/api/actions/{id}/cancel` guard pattern).  
- No controller/workflow changes.

## Phase 2: Planning Notes
- Backend: already done (soft-delete deals + hide quarantine items).

- Frontend split:
 1. Add API helpers:
    - Deals: `archiveDeal`, `bulkArchiveDeals` (+ optional restore later).
    - Quarantine: `deleteQuarantineItem`, `bulkDeleteQuarantineItems`.
 2. Deals page: add row “Delete” + multi-select bulk delete with confirmation + toast.
 3. Quarantine page: add row “Delete” + multi-select bulk delete with confirmation + toast.
 4. Keep approve/reject behavior unchanged.

## Acceptance Criteria
- Deals UI: delete single + bulk removes rows immediately and does not trigger any other workflows.
- Quarantine UI: delete single + bulk removes items from the quarantine queue immediately and does not approve/reject or otherwise mutate Gmail.
- Backend: existing endpoints respond non-error for the same operations via `curl`.

## Validation Plan
- Backend `curl` smoke:
  - `POST /api/deals/{id}/archive` (then `GET /api/deals` no longer includes it)
  - `POST /api/quarantine/{id}/delete` (then `GET /api/actions/quarantine` no longer includes it)
- Frontend:
  - `cd /home/zaks/zakops-dashboard && npm run build`
  - Manual smoke: delete single + bulk from `/deals` and `/quarantine`
