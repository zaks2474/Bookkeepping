# LangGraph + LangSmith Migration Notes (Option A)

Date: 2025-12-30

## What changed

- Added internal “brain” endpoint on `zakops-api` (:8080): `POST /api/deal-chat`
  - Code: `Zaks-llm/src/api/deal_chat.py`
  - Mounted into `Zaks-llm/src/api/server.py`
- Updated :8090 chat orchestrator to optionally call :8080 and proxy results back to the UI:
  - Code: `scripts/chat_orchestrator.py`
  - Default is **no behavior change** unless `ZAKOPS_BRAIN_MODE` is enabled.
- Added contract tests that mock the :8080 call (no docker dependency):
  - `scripts/tests/test_chat_brain_integration.py`
  - Updated `scripts/tests/test_deal_lifecycle_api_chat_execute_proposal.py` to use `httpx.ASGITransport` (the FastAPI `TestClient` hangs in this environment).

## Runtime toggles (BFF :8090)

- `ZAKOPS_BRAIN_MODE`:
  - `off` (default): never call :8080
  - `auto`: try :8080, fall back to existing streaming/router
  - `force`: require :8080; if unavailable, return degraded message
- `ZAKOPS_BRAIN_URL` (default `http://localhost:8080`)
- `ZAKOPS_BRAIN_TIMEOUT_S` (default `30`)

## Safe tracing (zakops-api :8080)

- Safe-by-default guardrails live in `Zaks-llm/src/core/tracing.py`.
- Tracing is only active when `LANGCHAIN_TRACING_V2=true` is set at runtime.
- Inputs/outputs stay hidden unless `ZAKOPS_LANGSMITH_ALLOW_UNREDACTED=true`.

## Operator actions required (blockers)

1) **Rotate the leaked LangSmith API key** in LangSmith (cannot be done by code here).
2) Ensure the running `zakops-api` container has the new code loaded:
   - `Zaks-llm/docker-compose.yml` mounts `./src:/app/src`, but uvicorn may not hot-reload.
   - Restart the container to be safe.

## How to validate (manual)

### 1) Enable brain (recommended: auto)

Set in the :8090 runtime environment:
```bash
export ZAKOPS_BRAIN_MODE=auto
export ZAKOPS_BRAIN_URL=http://localhost:8080
```

Restart the :8090 service/process so it picks up env vars.

### 2) Verify :8080 endpoint responds

```bash
curl -sS http://localhost:8080/api/deal-chat \
  -H 'content-type: application/json' \
  -d '{"query":"hello","scope":{"type":"global"},"session_id":"test","options":{}}' | jq .
```

Expect:
- `final_text` is non-empty
- `proposals` is a list (likely empty in global scope)

### 3) Verify dashboard chat still works (browser)

- Open `http://localhost:3003/chat?deal_id=DEAL-2025-008`
- Send a message
- Confirm:
  - response appears
  - proposals render (if produced)
  - Approve executes via `POST :8090/api/chat/execute-proposal`

### 4) Verify via curl (SSE)

```bash
curl -N http://localhost:8090/api/chat \
  -H 'content-type: application/json' \
  -d '{"query":"Summarize this deal and propose next steps","scope":{"type":"deal","deal_id":"DEAL-2025-008"},"session_id":"test-sse"}'
```

Expect:
- `event: token` lines
- a final `event: done` containing `final_text`, `proposals`, `model_used`

## How to run tests (no docker)

```bash
python3 -m unittest discover -q /home/zaks/scripts/tests
```

