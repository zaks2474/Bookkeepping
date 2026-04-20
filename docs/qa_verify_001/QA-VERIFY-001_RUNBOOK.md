# QA-VERIFY-001 — Zero-Trust QA Verification & Testing (Runbook)

- **Mission ID:** `QA-VERIFY-001`
- **Date:** `2026-01-26`
- **Owner:** QA/Security Verifier
- **Scope:** Full-system, evidence-based verification of ZakOps services and DB consistency.

## What This Produces

Each run creates a new folder under:

- `/home/zaks/bookkeeping/qa-results/<RUN_ID>/`

Containing (minimum):

- `phase0_health.json` (HTTP/TCP readiness evidence)
- `baseline_state.json` (DB counts before tests)
- `legacy_port_8090_check.json` (must show port 8090 is down)
- `openapi_backend.json`, `openapi_agent.json`, `openapi_rag.json` (contract snapshots)
- `backend_endpoint_probe.json`, `agent_endpoint_probe.json`, `rag_endpoint_probe.json` (endpoint reachability matrix)
- `deals_crud_results.json`, `actions_crud_results.json`, `quarantine_results.json`
- `agent_api_results.json`, `agent_tool_results.json`
- `rag_api_results.json`
- `ui_route_results.json`
- `e2e_results.json`
- `QA_VERIFICATION_REPORT.md` (human-readable report)
- `summary.json` (machine-readable overall summary)

At the end of the run, the final report is copied to:

- `/home/zaks/bookkeeping/docs/qa_verify_001/QA_VERIFICATION_REPORT_<RUN_ID>.md`

## Non-Negotiable Checks

- Port `8090` must be decommissioned (connection refused / timeout). If it responds, the run hard-fails.
- Every functional test uses **double verification**:
  - Method A: API response
  - Method B: DB query evidence (`zakops-postgres-1` via `psql`)

## Environment Defaults (can override via env vars)

- `BACKEND_URL=http://localhost:8091`
- `AGENT_URL=http://localhost:8095`
- `RAG_URL=http://localhost:8052`
- `DASHBOARD_URL=http://localhost:3003`
- `PG_CONTAINER=zakops-postgres-1`
- `PG_DB=zakops`
- `PG_USER=zakops`

## How To Run

```bash
bash /home/zaks/bookkeeping/docs/qa_verify_001/qa_verify_001.sh
```

Optional overrides:

```bash
BACKEND_URL=http://localhost:8091 \
AGENT_URL=http://localhost:8095 \
RAG_URL=http://localhost:8052 \
DASHBOARD_URL=http://localhost:3003 \
PG_CONTAINER=zakops-postgres-1 \
bash /home/zaks/bookkeeping/docs/qa_verify_001/qa_verify_001.sh
```

## Notes

- The runner is **zero-trust**: it records failures even when an API returns `500` but the DB shows side effects (a critical bug class).
- The runner attempts to clean up test-created rows where safe to do so, and records cleanup steps as evidence.

