# Quarantine Decision-Point UX (Email Triage) — Implementation Plan

Date: 2026-01-03

## Goal

Make `/quarantine` the operator decision point over **approval-gated** `EMAIL_TRIAGE.REVIEW_EMAIL` Kinetic Actions:

- **Approve** → executes the existing `EMAIL_TRIAGE.REVIEW_EMAIL` executor to create a Deal workspace + Deal Registry entry, then navigates to the Deal.
- **Reject** → marks the email as non-deal in Gmail and resolves the queue item so it does not reappear.

Non-negotiables:
- No automatic sending of email.
- No automatic deletion.
- No cloud dependency for quarantine preview (summary must be local / deterministic / precomputed).
- No silent drops; every action must end in a terminal state with a structured error on failure.
- Keep existing `/api/actions/*` and `/api/quarantine*` contracts backward compatible.

---

## Current State (Evidence / Inventory)

### Backend
- Canonical quarantine queue exists as action-backed list:
  - `GET /api/actions/quarantine` (filters `EMAIL_TRIAGE.REVIEW_EMAIL` + `PENDING_APPROVAL`).
  - `GET /api/actions/quarantine/{action_id}` returns `{action, quarantine_item}`.
- Legacy quarantine endpoints already surface action-backed items:
  - `GET /api/quarantine/health`, `GET /api/quarantine`, `GET /api/quarantine/{id}`, `POST /api/quarantine/{id}/resolve`.
- `EMAIL_TRIAGE.REVIEW_EMAIL` capability + executor already exist and create deals on approval+execution.

### Frontend
- `/quarantine` currently renders a list + a “Resolve” dialog (link/create/discard), but **no right-side preview panel** and **no Approve/Reject primary buttons**.
- `/quarantine` uses:
  - `getQuarantineItems()` → `/api/quarantine`
  - `resolveQuarantineItem()` → `/api/quarantine/{id}/resolve`

---

## Design Decisions

1) **Quarantine is action-backed**: the queue is the set of `EMAIL_TRIAGE.REVIEW_EMAIL` actions in `PENDING_APPROVAL` (optionally include `READY` if needed later).
2) **Preview is local-only**: build preview by reading `action.inputs` + `quarantine_dir` files (e.g., `email_body.txt`, `email.json`) without any cloud calls.
3) **Reject uses Pattern A (preferred)**:
   - Implement `EMAIL_TRIAGE.REJECT_EMAIL` as a real Kinetic Action + capability + executor.
   - Executor applies Gmail labels via ToolGateway + Gmail MCP, then completes.
   - Rationale: keeps external side-effects in the runner (audited, leased, retriable), avoids relying on the API process having tool execution perms.

---

## Phase 1 — Backend: Quarantine “Queue + Preview” APIs (local-only)

### 1.1 Queue endpoint (either convenience endpoint or documented preset)

Option A (minimal changes): keep `GET /api/actions/quarantine` as canonical and document the query preset:
- Filter: `action_type=EMAIL_TRIAGE.REVIEW_EMAIL`
- Filter: `status=PENDING_APPROVAL` (optionally add `include_ready=true` later)
- Sort: `created_at desc` (ensure store query is ordered)

If needed, extend `GET /api/actions/quarantine` to support:
- `status=PENDING_APPROVAL|READY|...` or `include_ready=true`
- `limit`, `offset` (already present)

**Response fields** (per item):
- `action_id`, `status`, `created_at`
- `message_id`, `thread_id`, `from`, `subject`, `received_at`
- `deal_score` + `reasons` (parse from the triage reason string if not stored structurally)
- `attachments[]`, `links[]`, `quarantine_dir`
- “artifact pointers” for common quarantine files (best-effort):
  - `quarantine_files[]` (names only, not arbitrary paths)
  - `has_email_body_txt`, `has_email_json`

### 1.2 Preview endpoint for right-side panel

Add a dedicated preview endpoint (action-backed):
- `GET /api/actions/quarantine/{action_id}/preview`

Preview payload (no cloud):
- `action_id`, `status`, `created_at`
- `summary_bullets` (3–6 bullets; deterministic generation)
- `extracted_fields` (best-effort regex):
  - broker/sender name + email
  - company guess (from subject / `inputs.company`)
  - asking price, revenue, EBITDA, location, industry (if detectable)
- `attachments` (name/type/size + whether present on disk in `quarantine_dir`)
- `links_grouped`:
  - `dataroom`, `cim_teaser`, `nda`, `financials`, `calendar`, `generic`
- `email_body`:
  - `snippet` (sanitized, capped)
  - optional `full_text` (sanitized, capped + behind UI expand)
  - `source` (`quarantine_dir/email_body.txt` vs `inputs` fallback)

Implementation notes:
- Hard safety: never accept arbitrary file paths; derive reads from `inputs.quarantine_dir` only and enforce it is under `DATAROOM_ROOT`.
- “Summary bullets” should be deterministic and evidence-first:
  - e.g., classification/urgency/deal_score, portal/link types detected, $ amounts present, attachments count/types.

### 1.3 Tests (backend)
- Unit tests for:
  - `GET /api/actions/quarantine` shape and required fields
  - `GET /api/actions/quarantine/{id}/preview` reads from quarantine_dir safely and returns non-empty summary + snippet
- Ensure tests do not require network/cloud.

---

## Phase 2 — Backend: Reject as a Real Kinetic Action (Pattern A)

### 2.1 Capability + executor

Add:
- Capability manifest: `email_triage.reject_email.v1` → `EMAIL_TRIAGE.REJECT_EMAIL`
- Executor: `EMAIL_TRIAGE.REJECT_EMAIL`

Executor responsibilities (deterministic, local-only):
- Inputs:
  - `message_id` (required)
  - optional `thread_id`
  - optional `labels_to_add` (default: `ZakOps/NonDeal`)
  - optional `labels_to_remove` (default: `ZakOps/Deal`)
  - `reason` (optional; for audit)
- Behavior:
  - Resolve label IDs (create if missing)
  - Apply Gmail label changes via ToolGateway (Gmail MCP)
  - Write action outputs:
    - label ids used, and tool output summary (no secrets)

### 2.2 ToolGateway wiring (Gmail MCP)

Add missing Gmail ToolGateway manifests required for labeling:
- `gmail__get_or_create_label` → MCP tool `get_or_create_label` (low/medium risk; approval required)
- `gmail__modify_email` → MCP tool `modify_email` (medium risk; approval required)

Update runner allowlist (systemd for `kinetic-actions-runner.service`) to include only what’s needed:
- `gmail__send_email` (already)
- `gmail__get_or_create_label`
- `gmail__modify_email`

### 2.3 Tests (backend)
- Unit test: reject action execution succeeds with ToolGateway mocked (no real Gmail calls).
- Regression: creation-time action validation accepts `EMAIL_TRIAGE.REJECT_EMAIL` and rejects unknown types.

---

## Phase 3 — Frontend: `/quarantine` becomes a 2-panel Decision UI

### 3.1 Data model + API client

Add API client methods in `zakops-dashboard/src/lib/api.ts`:
- `getQuarantineQueue()` → `GET /api/actions/quarantine`
- `getQuarantinePreview(action_id)` → `GET /api/actions/quarantine/{action_id}/preview`
- Reuse existing Actions client methods:
  - `approveKineticAction(action_id, approved_by)`
  - `runKineticAction(action_id)`
  - `getKineticAction(action_id)` polling
  - `createKineticAction(...)` (for reject flow)

### 3.2 UI layout + interactions

Update `/zakops-dashboard/src/app/quarantine/page.tsx`:
- Left column: list (subject, from, received_at, urgency badge, deal_score)
- Right column: preview panel
  - summary bullets
  - extracted fields
  - attachments
  - grouped links (clickable)
  - email snippet/full text (expand)
- Primary actions (top of right panel):
  - **Approve**
  - **Reject**

### 3.3 Approve behavior
- On Approve:
  1) `approveKineticAction(action_id, approved_by)`
  2) `runKineticAction(action_id)`
  3) poll `/api/actions/{id}` until `COMPLETED|FAILED`
  4) on success:
     - read `outputs.deal_id`
     - navigate to Deals UI (`/deals/{deal_id}` or the existing route)
     - remove item from list (optimistic local removal + refetch)

### 3.4 Reject behavior (Pattern A)
- On Reject:
  1) create a new `EMAIL_TRIAGE.REJECT_EMAIL` action (hidden from the user) using `createKineticAction`:
     - inputs derived from selected review action preview (`message_id`, `thread_id`, reason)
  2) approve + run reject action
  3) poll reject action until terminal
  4) if reject action completed:
     - cancel the original `EMAIL_TRIAGE.REVIEW_EMAIL` action (or call `POST /api/quarantine/{id}/resolve discard` as compatibility)
     - remove item from list
  5) if reject action failed:
     - show error; leave original item intact

---

## Phase 4 — Verification

### Manual E2E checklist
1) Ensure a deal-signal email exists and appears in `/quarantine` list.
2) Select it and confirm preview panel loads (summary + fields + links + attachments + snippet).
3) Click Approve:
   - action transitions `PENDING_APPROVAL → READY → PROCESSING → COMPLETED`
   - deal is created and appears under Deals list
   - UI navigates to the deal and removes the quarantine item.
4) Click Reject:
   - `EMAIL_TRIAGE.REJECT_EMAIL` runs and applies Gmail label `ZakOps/NonDeal` (and removes `ZakOps/Deal`)
   - original review action is cancelled/resolved
   - item disappears and does not reappear on refresh.

### Automated tests
- Backend: extend existing python unit tests (httpx ASGI transport) for preview and reject flow.
- Frontend: add a Playwright E2E spec for `/quarantine` (optional if Playwright install is not stable on the machine; if blocked, keep backend integration tests as required and document the blocker).

---

## Risks / Mitigations

- Gmail MCP tool names/args drift:
  - Mitigation: implement ToolGateway manifests with exact MCP tool names (`get_or_create_label`, `modify_email`) and add a mocked unit test.
- Runner allowlist change is a production safety boundary:
  - Mitigation: allowlist only the two additional tools required for labeling; document rollback (remove from allowlist and restart runner).
- Quarantine preview file safety (path traversal):
  - Mitigation: only read from `inputs.quarantine_dir` and enforce it’s under `DATAROOM_ROOT`.

---

## Rollback Plan

- Disable reject execution:
  - Remove `gmail__get_or_create_label` and `gmail__modify_email` from runner allowlist and restart `kinetic-actions-runner.service`.
  - Quarantine UI can fall back to “Discard” (cancel) without Gmail labeling if needed.
- Keep `/api/quarantine*` legacy endpoints intact for compatibility.

