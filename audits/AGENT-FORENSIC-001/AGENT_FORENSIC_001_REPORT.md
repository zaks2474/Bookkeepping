# AGENT-FORENSIC-001 Report (V2)
**Date:** 2026-02-02 22:25:08 UTC
**Auditor:** Claude Code

## Summary
| Category | Total | Pass | Fail |
|----------|-------|------|------|
| Phase 0  | 30    | 25   | 5    |
| Phase 1  | 35    | 25   | 10   |
| TOTAL    | 65    | 50   | 15   |

## Known Unknown Resolutions
| # | Unknown | Answer | Evidence |
|---|---------|--------|----------|
| U1 | Agent DB name (food_order_db?) | zakops_agent | evidence/phase0/01_agent_db_identity.txt |
| U2 | Split-brain DBs healthy? | Agent vs backend tables listed; split-brain check recorded | evidence/phase0/02_backend_db_identity.txt |
| U3 | DEAL_API_URL resolves from container? | Blocked: curl not installed in container; reachability check failed | evidence/phase0/11_container_reachability.txt |
| U4 | vLLM model loaded? | Qwen/Qwen2.5-32B-Instruct-AWQ present | evidence/phase0/06_llm_health.txt |
| U5 | RAG service state | /health returned Not Found | evidence/phase0/07_rag_health.txt |
| U6 | Service discovery completeness | All expected services discovered; langfuse restarting | evidence/phase0/00_service_census.txt |
| U7 | MCP status | HTTP 404 on root | evidence/phase0/08_mcp_status.txt |
| U8 | Orchestration status | /health returned empty response | evidence/phase0/09_orchestration_status.txt |
| U9 | Agent DB tables | 9 tables in public schema | evidence/phase0/01_agent_db_identity.txt |
| U10 | Agent DB user | agent | evidence/phase0/01_agent_db_identity.txt |
| U11 | Orchestration service present | Port 9200 probed; /health empty (status unknown) | evidence/phase0/09_orchestration_status.txt |
| U12 | Hidden endpoints? | OpenAPI at /api/v1/openapi.json; 26 endpoints discovered | evidence/phase1/10_openapi_discovery.txt |
| U13 | Cross-user isolation? | Delete other user's session returned 404 (pass); GET not supported (405) | evidence/phase1/19_multi_user_isolation.txt |
| U14 | Password hashing? | hashed_password column uses bcrypt prefix ($2b$12) | evidence/phase1/18_account_security.txt |

## Finding Catalog
| F-# | Finding | Severity | Phase | Evidence |
|-----|---------|----------|-------|----------|
| F-01 | /agent/* endpoints accept requests without valid X-Service-Token | P0 | 1 | evidence/phase1/16_auth_enforcement.txt |
| F-02 | /api/v1/agent/* endpoints exposed without auth (200 with no auth/JWT) | P0 | 1 | evidence/phase1/15b_openapi_additional_endpoints.txt |
| F-03 | Confused deputy: JWT accepted on /agent/invoke (and both headers) | P0 | 1 | evidence/phase1/17_confused_deputy.txt |
| F-04 | Chat streaming returns SSE error payload (LangchainCallbackHandler) | P1 | 1 | evidence/phase1/14_chat_v1.txt |
| F-05 | Session name update endpoint returns 404 for existing session | P2 | 1 | evidence/phase1/13_session_crud.txt |
| F-06 | No rate limiting observed (all 200) | P2 | 1 | evidence/phase1/22_rate_limiting.txt |
| F-07 | Container reachability test blocked (curl missing in agent container) | P2 | 0 | evidence/phase0/11_container_reachability.txt |
| F-08 | RAG /health returns 404 | P2 | 0 | evidence/phase0/07_rag_health.txt |
| F-09 | MCP root returns 404 | P2 | 0 | evidence/phase0/08_mcp_status.txt |
| F-10 | Orchestration /health returned empty response | P2 | 0 | evidence/phase0/09_orchestration_status.txt |
| F-11 | Langfuse container restarting | P2 | 0 | evidence/phase0/00_service_census.txt |

## P0 Blockers
- F-01: /agent/* endpoints accept no/invalid service token
- F-02: /api/v1/agent/* endpoints exposed without auth
- F-03: Confused deputy (JWT accepted on /agent/invoke)

## P1 High Priority
- F-04: Chat streaming returns SSE error payload

## P2/P3 Lower Priority
- F-05: Session name update endpoint returns 404
- F-06: No rate limiting observed
- F-07: Container reachability blocked (curl missing)
- F-08: RAG /health 404
- F-09: MCP root 404
- F-10: Orchestration /health empty
- F-11: Langfuse container restarting

## Remediation Backlog
| # | Finding | Priority | Fix |
|---|---------|----------|-----|
| 1 | F-01 | P0 | Enforce X-Service-Token on all /agent/* routes; return 401/403 on missing/invalid token |
| 2 | F-02 | P0 | Require auth for /api/v1/agent/* (JWT or service token); add middleware tests |
| 3 | F-03 | P0 | Reject JWT on service-token endpoints; ensure precedence rules for mixed headers |
| 4 | F-04 | P1 | Fix chat streaming handler (LangchainCallbackHandler init arg); add regression test |
| 5 | F-05 | P2 | Align /api/v1/auth/session/{id}/name route implementation with OpenAPI | 
| 6 | F-06 | P2 | Implement rate limiting and document limits (429 on bursts) |
| 7 | F-07 | P2 | Add curl or alternative probe inside agent container for reachability checks |
| 8 | F-08 | P2 | Add/repair RAG /health endpoint or update monitoring to correct path |
| 9 | F-09 | P2 | Add/repair MCP /health endpoint or update monitoring expectations |
|10 | F-10 | P2 | Investigate orchestration /health response; ensure meaningful status |
|11 | F-11 | P2 | Stabilize langfuse container; resolve restart loop |

## Evidence Index
| File | Description |
|------|-------------|
| evidence/phase0/00_service_census.txt | Docker service census + listening ports |
| evidence/phase0/01_agent_db_identity.txt | Agent DB name, user, tables |
| evidence/phase0/02_backend_db_identity.txt | Backend DB tables + split-brain note |
| evidence/phase0/03_agent_env_vars.txt | Agent API env vars (redacted) |
| evidence/phase0/05_token_match_proof.txt | Dashboard ↔ Agent token match |
| evidence/phase0/06_llm_health.txt | vLLM model list + chat test |
| evidence/phase0/07_rag_health.txt | RAG /health response |
| evidence/phase0/08_mcp_status.txt | MCP root response |
| evidence/phase0/09_orchestration_status.txt | Orchestration /health response |
| evidence/phase0/10_code_provenance.txt | Git SHAs + image digests |
| evidence/phase0/11_container_reachability.txt | In-container reachability attempt |
| evidence/phase0/12_db_write_canary.txt | DB write canary results |
| evidence/phase0/13_config_contradictions.txt | Config contradiction scan |
| evidence/phase0/14_logging_readiness.txt | Recent logs + baseline capture |
| evidence/phase0/15_clock_drift.txt | Host vs container time drift |
| evidence/phase1/10_openapi_discovery.txt | OpenAPI discovery + endpoint list |
| evidence/phase1/11_root_health.txt | Root + /health responses |
| evidence/phase1/12_auth_endpoints.txt | Register/login flows (redacted) |
| evidence/phase1/13_session_crud.txt | Session CRUD attempts |
| evidence/phase1/14_chat_v1.txt | Chat + streaming + messages |
| evidence/phase1/15_agent_mdv2.txt | /agent invoke + approvals |
| evidence/phase1/15b_openapi_additional_endpoints.txt | Additional OpenAPI endpoint coverage |
| evidence/phase1/16_auth_enforcement.txt | Auth enforcement checks |
| evidence/phase1/17_confused_deputy.txt | Confused deputy tests |
| evidence/phase1/18_account_security.txt | Enumeration + hash check |
| evidence/phase1/19_multi_user_isolation.txt | Cross-user isolation tests |
| evidence/phase1/20_input_hardening.txt | Malformed input tests |
| evidence/phase1/21_streaming_validation.txt | Streaming time-to-first-token |
| evidence/phase1/22_rate_limiting.txt | Rate limiting probe |
| evidence/cleanup/test_data_cleanup.txt | Cleanup actions |
| matrices/* | All 8 matrices |

## Verdict
- Phase 0: 25/30 | Gate: 11/12
- Phase 1: 25/35 | Gate: 10/11
- Total: 50/65
- P0 Blockers: 3
- LLM Status: HEALTHY
- Token Match: MATCH
- Cross-User Isolation: VERIFIED
- Password Storage: HASHED

**Overall:** CRITICAL FAILURE
