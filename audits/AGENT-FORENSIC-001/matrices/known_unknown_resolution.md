# Known Unknown Resolution
| # | Unknown | Answer | Evidence |
|---|---|---|---|
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
