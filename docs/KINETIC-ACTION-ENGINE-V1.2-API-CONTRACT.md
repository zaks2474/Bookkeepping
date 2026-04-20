# Kinetic Action Engine v1.2 — API Contract (Backend :8090)

**Status:** Implemented  
**Backend:** `/home/zaks/scripts/deal_lifecycle_api.py`  
**Runner:** `/home/zaks/scripts/actions_runner.py`  
**DB:** `ZAKOPS_STATE_DB` (SQLite, WAL)

---

## Backward Compatibility

- **Chat endpoints remain unchanged (stable contract):**
  - `POST /api/chat` (SSE streaming)
  - `POST /api/chat/complete`
  - `POST /api/chat/execute-proposal`

- **Legacy deferred reminders preserved under new namespace:**
  - `GET /api/deferred-actions`
  - `GET /api/deferred-actions/due`
  - `POST /api/deferred-actions/{id}/execute`
  - `POST /api/deferred-actions/{id}/cancel`

---

## Kinetic Actions (v1.2)

### Action Status State Machine
`PENDING_APPROVAL → READY → PROCESSING → COMPLETED|FAILED` (+ `CANCELLED`)

### `GET /api/actions`
Query params:
- `deal_id` (optional)
- `status` (optional)
- `action_type` (optional)
- `created_after` / `created_before` (optional ISO8601)
- `limit` (default 50, max 200)
- `offset` (default 0)

Response:
```json
{ "count": 1, "actions": [ { "action_id": "...", "type": "...", "status": "..." } ] }
```

### `POST /api/actions` (create)
Request:
```json
{
  "action_type": "COMMUNICATION.DRAFT_EMAIL",
  "title": "Draft broker email",
  "summary": "",
  "deal_id": "DEAL-2025-001",
  "capability_id": "communication.draft_email.v1",
  "created_by": "operator",
  "source": "ui",
  "risk_level": "medium",
  "requires_human_review": true,
  "idempotency_key": "optional-string",
  "inputs": { "to": "broker@example.com", "subject": "Re: CIM", "context": "Please send the CIM." }
}
```

Response:
```json
{ "success": true, "created_new": true, "action": { "action_id": "...", "status": "PENDING_APPROVAL", "...": "..." } }
```

### `POST /api/actions/{action_id}/approve`
Request:
```json
{ "approved_by": "operator" }
```
Transitions: `PENDING_APPROVAL → READY` (does not enqueue).

### `POST /api/actions/{action_id}/execute` (enqueue)
Request:
```json
{ "requested_by": "operator" }
```
Enqueues the action for the runner by setting `next_attempt_at=now` and recording an `execution_requested` audit event.

Notes:
- Does **not** set `status=PROCESSING` (runner does that when it actually starts work).
- Allowed status: `READY` only.

### `POST /api/actions/{action_id}/cancel`
Request:
```json
{ "cancelled_by": "operator", "reason": "Cancelled via API" }
```

### `POST /api/actions/{action_id}/update` (edit inputs pre-run)
Request:
```json
{ "updated_by": "operator", "inputs": { "any": "json" } }
```
Allowed statuses: `PENDING_APPROVAL`, `READY`.

### `GET /api/actions/{action_id}`
Returns full action including:
- `audit_trail[]`
- `artifacts[]` with `download_url`

### `GET /api/actions/{action_id}/artifacts`
Response:
```json
{ "count": 1, "artifacts": [ { "artifact_id": "...", "filename": "...", "download_url": "/api/actions/<id>/artifact/<artifact_id>" } ] }
```

### `GET /api/actions/{action_id}/artifact/{artifact_id}`
Downloads the artifact file.

Safety:
- Path traversal is blocked: artifact path must resolve under `DATAROOM_ROOT` (default `/home/zaks/DataRoom`).

---

## Capabilities + Planner

### `GET /api/actions/capabilities`
Returns capability manifests loaded from:
- `scripts/actions/capabilities/*.yaml`
- plus tool manifests indexed as `TOOL.<tool_id>.v<major>`

### `GET /api/actions/capabilities/{capability_id}`
Returns one manifest.

### `POST /api/actions/plan`
Deterministic-first planner endpoint.

Request:
```json
{ "query": "Draft email to broker@example.com about LOI terms", "deal_id": "optional", "inputs": {} }
```

Response (`ActionPlan`):
```json
{
  "intent": "...",
  "interpretation": "...",
  "selected_capability_id": "...",
  "action_type": "...",
  "action_inputs": {},
  "missing_fields": [],
  "plan_steps": [],
  "requires_clarification": false,
  "clarifying_questions": [],
  "is_refusal": false,
  "refusal_reason": null,
  "suggested_alternatives": [],
  "confidence": 0.0,
  "risk_level": "medium"
}
```

---

## Metrics

### `GET /api/actions/metrics`
Includes:
- queue counts
- success rate / avg duration (window)
- runner lease info
- stuck processing action IDs (heartbeat stale)

---

## Tools (Phase 0.5)

### `GET /api/tools`
Lists tool manifests (from `scripts/tools/manifests/*.yaml`).

### `GET /api/tools/{tool_id}`
Returns one tool.

### `GET /api/tools/health`
Runs cached health checks (requires ToolGateway enabled + allowlist configured unless bypassed).

---

## Runner / Ops

- Start runner: `cd /home/zaks/scripts && make actions-runner`
- Metrics: `curl -s http://localhost:8090/api/actions/metrics | jq`
- Runner status: `curl -s http://localhost:8090/api/actions/runner-status | jq`
- Action debug: `curl -s http://localhost:8090/api/actions/<ACTION_ID>/debug | jq`
- Unstick: `cd /home/zaks/scripts && make actions-retry-stuck`

### `GET /api/actions/runner-status`
Returns runner lease holder + heartbeat, queue counts, and `processing_ttl_seconds`.

### `GET /api/actions/{action_id}/debug`
Returns action payload + audit tail + last tool invocation (best-effort) + transition timestamps.

### `POST /api/actions/{action_id}/requeue`
Admin endpoint to move `FAILED → READY` and enqueue immediately.

Request:
```json
{ "requeued_by": "operator", "reason": "retry_after_timeout" }
```

Env:
- `ZAKOPS_ACTION_PROCESSING_TTL_SECONDS` (default `3600`): runner watchdog marks stale `PROCESSING` actions as `FAILED` with code `processing_timeout`.
