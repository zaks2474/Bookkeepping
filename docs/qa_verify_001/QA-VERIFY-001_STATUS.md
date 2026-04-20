# QA-VERIFY-001 Status (Zero-Trust Verification)

- Latest PASS run: `QA-VERIFY-001-20260126-104909`
- Runner command: `/home/zaks/bookkeeping/docs/qa_verify_001/qa_verify_001.sh`
- Artifact root: `/home/zaks/bookkeeping/qa-results/QA-VERIFY-001-20260126-104909/`
- Report (docs): `/home/zaks/bookkeeping/docs/qa_verify_001/QA_VERIFICATION_REPORT_QA-VERIFY-001-20260126-104909.md`
- Report (Windows Downloads): `/mnt/c/Users/mzsai/Downloads/QA_VERIFICATION_REPORT_QA-VERIFY-001-20260126-104909.md`

## What Was Fixed To Reach PASS

### Backend (`/home/zaks/zakops-backend`)

- Deal response schema drift: `email_thread_ids` now defaults to `[]` (prevents FastAPI `ResponseValidationError` 5xx).
- Deal event + alias queries aligned to Postgres schema (`event_source/payload`, deal_alias columns).
- Deal update audit: `record_deal_event()` now called with a single JSON payload; JSON serialization is datetime-safe (`default=str`).
- Actions list/get: added required projection fields (`summary`, `capability_id`, `risk_level`, `requires_human_review`, `inputs`, `outputs`) to prevent `ResponseValidationError`.
- Actions approve/reject: removed dependency on non-existent `audit_trail` column; broadened “pending” acceptance (case-insensitive).
- Workflow engine: stage transition now records events via `zakops.record_deal_event` and uses `zakops.idempotency_keys` for replay (removes references to non-existent `deal_events.details/idempotency_key` columns).

### Agent (`/home/zaks/zakops-agent-api/apps/agent-api`)

- Tool-call message handling: `Message.content` now allows empty strings (tool-calling assistant messages) and supports larger tool payloads (max `20000`).
- Deal tools:
  - Default Deal API target updated to `:8091`.
  - Mocks default to **OFF** (`ALLOW_TOOL_MOCKS=false` unless explicitly enabled).
  - `transition_deal` payload matches backend contract (`new_stage`, `idempotency_key`).
  - `search_deals` targets RAG REST contract (`POST /rag/query`).
  - Fail-closed on dependency outage when mocks disabled.
- Dev env: `.env.development` updated to `DEAL_API_URL=http://host.docker.internal:8091` and `ALLOW_TOOL_MOCKS=false`.

### QA Runner (`/home/zaks/bookkeeping/docs/qa_verify_001`)

- Quarantine “endpoint existence” check now accepts `400` as valid for invalid UUID paths (custom error handler maps validation → 400).

## Gates (Must Not Regress)

- Port `8090` remains **decommissioned** (runner hard-fails if it responds).
- `qa_verify_001.sh` result stays **15/15 PASS** with evidence artifacts emitted under `/home/zaks/bookkeeping/qa-results/<RUN_ID>/`.

## Suggested Next Step (If You Want Stronger “Test Every Endpoint” Coverage)

- Extend `endpoint_probe()` to include safe-negative calls for POST/PATCH/DELETE (expecting `400/404/422`, never `5xx`) while still avoiding data mutation.

