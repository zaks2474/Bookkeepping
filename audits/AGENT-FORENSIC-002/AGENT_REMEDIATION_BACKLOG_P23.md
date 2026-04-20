# AGENT-FORENSIC-002 Remediation Backlog — Phases 2-3 (Updated)

| # | Finding | Priority | Fix Description | Evidence |
|---|---------|----------|----------------|----------|
| F-001 | /agent/invoke rejects valid X-Service-Token in pre-gate (401) | P0 | Validate service-token config and middleware. Ensure /agent/* accepts the configured token; add health/auth self-test on startup. | pg01_auth_gate.txt |
| F-002 | /agent/approvals accepted Bearer JWT (auth inconsistency / confused deputy) | P0 | Enforce **only** X-Service-Token for /agent/* endpoints. Reject Bearer JWTs and add regression tests for confused-deputy cases. | 3e_concurrent_race.txt |
| F-003 | transition_deal returns ok:true without changing deal stage (phantom success) | P0 | Validate from_stage against current DB state and enforce allowed to_stage list. Fail closed on mismatch or invalid stage; surface backend errors. | 3d_restart_resume.txt, 3c_reject_sql.txt, 34_path_d.txt |
| F-004 | LLM tool args invalid/hallucinated (from_stage/to_stage) | P1 | Inject actual deal stage into tool context and provide valid stage list. Add server-side validation before calling backend. | 39_approval_fields.txt |
| F-005 | RAG DB disconnected — search_deals degraded | P1 | Restore RAG DB connectivity and verify /rag/query returns results. | 24_search_deals.txt |
| F-006 | Rejection path lacks audit_log entries for f002-path-e-001 | P1 | Emit audit_log events for rejection (approval_rejected + thread completion). | 3a_audit_log.txt |
| F-007 | /api/v1/sessions endpoint mismatch (404) | P2 | Update docs or add alias route; align clients to /api/v1/auth/sessions. | pg01_auth_gate.txt, 21_llm_connectivity.txt |
| F-008 | /docs, /redoc, /metrics exposed without auth | P2 | Disable or require auth for documentation/metrics in production. | pg01_auth_gate.txt |
| F-009 | No cross-service correlation ID propagation | P2 | Propagate traceparent/x-correlation-id on agent->backend requests and log it end-to-end. | 2g_correlation.txt |

## Priority Summary
- **P0 (Blocker):** 3 findings (F-001, F-002, F-003)
- **P1 (High):** 3 findings (F-004, F-005, F-006)
- **P2 (Medium):** 3 findings (F-007, F-008, F-009)
