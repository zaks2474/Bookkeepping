# Option A Architecture — 8090 BFF + 8080 LangGraph Engine

Date: 2025-12-30

## Why Option A (reuse `zakops-api` on :8080)

- **No contract breakage**: the dashboard keeps talking to the same public API (`deal_lifecycle_api.py` on :8090).
- **LangGraph is already present** in `Zaks-llm` (container `zakops-api`), while the host python environment running :8090 does not have `langgraph/langsmith`.
- **Separation of concerns**:
  - :8090 remains the *control plane* and *executor* (approval lifecycle).
  - :8080 becomes the *proposal-only cognition plane* (LangGraph + optional LangSmith).

## Responsibilities

### Public BFF (FastAPI) — `:8090`

- File: `/home/zaks/scripts/deal_lifecycle_api.py`
- Endpoints (public contract, unchanged):
  - `POST /api/chat` (SSE streaming)
  - `POST /api/chat/complete`
  - `POST /api/chat/execute-proposal` (the only executor path)
  - `GET /api/chat/session/{session_id}`
- Owns:
  - session storage (SQLite-backed chat persistence)
  - evidence building (RAG/events/registry/case files/actions)
  - proposal storage + lifecycle (`pending_approval` → executed/failed/rejected)
  - all write execution (notes, tasks, transitions, drafts)

### Internal LangGraph engine — `:8080`

- Repo/service: `Zaks-llm` → container `zakops-api`
- New internal endpoint:
  - `POST /api/deal-chat`
- Guarantees:
  - proposal-only output (no execution)
  - canonical proposal taxonomy returned to the BFF
  - safe tracing defaults when LangSmith is enabled

## End-to-end flow (happy path)

1) Dashboard → `POST :8090/api/chat` (SSE) with `{query, scope, session_id?, options?}`
2) :8090 builds evidence bundle + session history
3) :8090 calls :8080 `POST /api/deal-chat` with same payload + adds `options.history` + `options.evidence_context`
4) :8080 runs LangGraph and returns:
   - `final_text`
   - `proposals[]` (canonical types only)
   - optional `debug` (provider/model/graph_run_id)
5) :8090 proxies response back to the UI:
   - streams `final_text` as `token` events (proxy-chunking for now)
   - emits `done` event with proposals + citations + evidence_summary
6) UI renders proposal cards; user approves
7) UI → `POST :8090/api/chat/execute-proposal`
8) :8090 executes proposal and writes audit/event records

## Rollback / kill switch

- Set `ZAKOPS_BRAIN_MODE=off` in the :8090 environment (or service config) to disable :8080 usage completely.
- Set `ZAKOPS_BRAIN_MODE=auto` to *try* :8080 first and fall back to the existing :8090 LLM streaming if :8080 is unavailable.

## Security notes

- LangSmith traces must remain safe-by-default:
  - inputs/outputs hidden unless `ZAKOPS_LANGSMITH_ALLOW_UNREDACTED=true`
- :8080 endpoint is internal; do not expose it externally.
- Rotate any leaked LangSmith API key in LangSmith (operator action).

