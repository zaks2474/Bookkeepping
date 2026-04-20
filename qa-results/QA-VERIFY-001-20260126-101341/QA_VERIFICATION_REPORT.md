# ZakOps QA Verification Report
## Zero-Trust System Testing Results

- **Run ID:** `QA-VERIFY-001-20260126-101341`
- **Timestamp (UTC):** `2026-01-26T16:13:54.331562+00:00`
- **Verdict:** `FAIL` (evidence-based)

## Summary

| Suite | Passed | Total | Status |
|------|--------|-------|--------|
| Phase 0 — Environment Setup | 3 | 3 | ✅ |
| Phase 0 — Contract Snapshots | 1 | 1 | ✅ |
| Phase 1 — Backend API | 1 | 4 | ⚠️ |
| Phase 2 — Agent API | 2 | 3 | ⚠️ |
| Phase 3 — RAG API | 2 | 2 | ✅ |
| Phase 4 — E2E Workflows | 0 | 1 | ⚠️ |
| Phase 5 — UI Routes | 1 | 1 | ✅ |
| **TOTAL** | **10** | **15** | ⚠️ |

## Evidence Artifacts

- Artifact root: `/home/zaks/bookkeeping/qa-results/QA-VERIFY-001-20260126-101341`
- `actions_crud_results.json`
- `agent_api_results.json`
- `agent_endpoint_probe.json`
- `agent_results.json`
- `agent_tool_results.json`
- `backend_endpoint_probe.json`
- `backend_results.json`
- `baseline_state.json`
- `deals_crud_results.json`
- `e2e_results.json`
- `legacy_port_8090_check.json`
- `openapi_agent.json`
- `openapi_backend.json`
- `openapi_rag.json`
- `phase0_health.json`
- `phase0_openapi_results.json`
- `phase0_results.json`
- `phase4_results.json`
- `quarantine_results.json`
- `rag_api_results.json`
- `rag_endpoint_probe.json`
- `rag_results.json`
- `run_meta.json`
- `summary.json`
- `ui_results.json`
- `ui_route_results.json`
- `runner.log`

## Stop-Ship Findings (auto-extracted)

- CRITICAL: Deal CREATE returns 5xx but still writes to DB (side-effect without success).
- CRITICAL: Deal LIST endpoint returns 5xx (breaks UI/pipeline).
- CRITICAL: Quarantine LIST endpoint returns 5xx.

## Notes

- This report is **zero-trust**: API 5xx with DB side effects is treated as FAIL and highlighted.
- Port `8090` is required to be decommissioned; the run hard-fails if it responds.

