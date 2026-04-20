# Env Drift Matrix
| Variable / Check | Expected | Actual | Drift? | Evidence |
|---|---|---|---|---|
| DEAL_API_URL | http://host.docker.internal:8091 | http://host.docker.internal:8091 | No | evidence/phase0/03_agent_env_vars.txt |
| VLLM_BASE_URL | http://host.docker.internal:8000/v1 | http://host.docker.internal:8000/v1 | No | evidence/phase0/03_agent_env_vars.txt |
| RAG_REST_URL | http://host.docker.internal:8052 | http://host.docker.internal:8052 | No | evidence/phase0/03_agent_env_vars.txt |
| MCP_URL | http://host.docker.internal:9100 | http://host.docker.internal:9100 | No | evidence/phase0/03_agent_env_vars.txt |
| DASHBOARD_SERVICE_TOKEN | Matches dashboard .env | Matches (redacted) | No | evidence/phase0/05_token_match_proof.txt |
| Forbidden port 8090 in env | None | None | No | evidence/phase0/03_agent_env_vars.txt |
| food_order_db reference | None | None | No | evidence/phase0/03_agent_env_vars.txt |
| DATABASE_URL credentials | Redacted | Redacted | No | evidence/phase0/03_agent_env_vars.txt |
