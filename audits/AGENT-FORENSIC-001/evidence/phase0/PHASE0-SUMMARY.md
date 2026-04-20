# AGENT-FORENSIC-001 Phase 0 Summary

**Audit Date:** 2026-02-02
**Scope:** Infrastructure inventory of Agent API layer (READ-ONLY)
**Auditor:** Claude Opus 4.5

---

## Check Results

| Step | Check | Result | Key Findings |
|------|-------|--------|--------------|
| 0.1 | Service Census | PASS | 14 containers running. Agent API (`zakops-agent-api`) up 9h healthy. Agent DB (`zakops-agent-db`) up 10h healthy. Langfuse restarting. |
| 0.1 | Listening Ports | PASS | All expected ports active: 8095 (agent-api), 8091 (backend), 3003 (dashboard/Next.js bare), 5432 (postgres), 8000 (vLLM), 9100 (MCP/python3). |
| 0.2 | Network Topology | INFO | Agent API + Agent DB on `agent-api_agent-network` (172.26.0.x). Backend stack on `zakops_network` (172.23.0.x). vLLM/OpenWebUI on `zaks-llm_ai-network` (172.18.0.x). Networks are isolated; agent-api reaches other services via `host.docker.internal`. |
| 0.3 | Agent API Health | PASS | Root returns `{"status":"healthy","version":"1.0.0"}`. /docs serves Swagger UI. /health returned rate limit (hit 20/min cap during testing). |
| 0.4 | Agent DB Schema | PASS | 9 tables: `approvals`, `audit_log`, `checkpoint_blobs`, `checkpoint_migrations`, `checkpoint_writes`, `checkpoints`, `session`, `tool_executions`, `user`. LangGraph checkpoint tables + HITL approval workflow tables. |
| 0.5 | Environment Variables | INFO | Python 3.13.2. Uses `host.docker.internal` for cross-service comms (backend:8091, vLLM:8000, MCP:9100, RAG:8052). Langfuse cloud integration. JWT auth with HS256. Rate limits configured. Secrets redacted. |
| 0.6 | Docker Compose Config | PASS | agent-api: builds from local Dockerfile, maps 8095:8000, bind-mounts `./app` and `./logs`, depends on `db` (healthy), on `agent-network` bridge. DB: pgvector/pg16, no host port (internal only). Optional monitoring profile (Prometheus, Grafana, cAdvisor). |
| 0.7 | Reachability | PASS | Backend (8091): reachable, healthy. PostgreSQL (5432): reachable. vLLM (8000): reachable (empty response from /health). Redis (6379): reachable. MCP (9100): reachable (404 on root, expected). RAG REST (8052): reachable. |
| 0.8 | Source Code Inventory | INFO | 65 Python files, 11,276 LOC. Structure: `app/` (main.py, api/, core/, models/, schemas/, services/, utils/), `evals/`, `tests/`. Key modules: LangGraph graph, deal tools, DuckDuckGo search, HITL approvals, cost tracking, security (RBAC, output validation, PII redaction). |
| 0.9 | Log Analysis | PASS | No errors, exceptions, or warnings in last 500 log lines. Logs are structured JSON at DEBUG level. |
| 0.10 | Resource Usage | PASS | Agent API: 260.8 MiB RAM (0.82%), 0.17% CPU, 37 PIDs. Agent DB: 70.27 MiB. vLLM dominates at 2.6 GiB (8.36% of 31 GiB). No resource pressure observed. |
| 0.11 | Volume Mounts | INFO | Two bind mounts: `./app` -> `/app/app` (RW, source code hot-reload), `./logs` -> `/app/logs` (RW). |
| 0.12 | TLS/SSL Check | INFO | No TLS for internal services. All inter-service URLs use `http://`. Only external connection (Langfuse cloud) uses HTTPS. No TLS env vars in container. |
| 0.13 | Process Tree | PASS | Single process: `uvicorn app.main:app --host 0.0.0.0 --port 8000` running as `zaks` user (non-root). |
| 0.14 | Dependency Versions | INFO | Python 3.13.2, LangGraph 1.0.7, LangChain 1.2.7, FastAPI 0.128.0, Uvicorn 0.40.0, Pydantic 2.12.5, OpenAI 2.16.0, psycopg 3.3.2, langgraph-checkpoint-postgres 3.0.4, Langfuse 3.9.1, SlowAPI 0.1.9, SQLAlchemy 2.0.46. |
| 0.15 | Config Files | INFO | Dockerfile, docker-compose.yml, langgraph.json, pyproject.toml, .env files present. See evidence/config-files.txt. |
| 0.16 | Port 8090 Verification | PASS | Port 8090 not listening, not in any docker container, not in compose config. Confirmed decommissioned. |

---

## Architecture Summary

```
                    [Dashboard :3003]
                         |
                    (Next.js rewrites)
                         |
    [Backend :8091] <--- | ---> [Agent API :8095]
         |                           |
    [zakops_network]          [agent-api_agent-network]
    - zakops-postgres-1       - zakops-agent-api (172.26.0.2)
    - zakops-redis-1          - zakops-agent-db  (172.26.0.3)
    - outbox-worker
    - backend

    Cross-network via host.docker.internal:
    Agent API -> Backend (8091)
    Agent API -> vLLM (8000)
    Agent API -> MCP (9100)
    Agent API -> RAG REST (8052)
    Agent API -> Redis (6379)
```

## Notable Findings

1. **Network Isolation**: Agent API is on its own bridge network (`agent-api_agent-network`), separate from the backend stack. All cross-service communication goes through `host.docker.internal`, which means it traverses the host network stack rather than Docker-internal networking.

2. **No TLS Internally**: All inter-service communication is plain HTTP. Only acceptable if this runs on a single host with no untrusted network segments.

3. **Rate Limiting Active**: Agent API has rate limits configured (50/min for agent, 100/min for chat, 1000/day default). The /health endpoint is rate-limited, which may affect monitoring.

4. **Langfuse Restarting**: The `zakops-backend-langfuse-1` container is in a restart loop. This is in the backend stack, not agent-api, but may affect agent telemetry if it tries to send traces.

5. **Hot-reload Bind Mount**: Source code is bind-mounted into the container (`./app` -> `/app/app`), meaning changes on host immediately affect the running container. Appropriate for development, not production.

6. **Agent DB Not Exposed**: PostgreSQL for agent (zakops-agent-db) has no host port mapping -- only reachable within `agent-api_agent-network`. Good security practice.

7. **Single Process**: Agent API runs a single uvicorn process (no workers/gunicorn). May limit throughput under load.

---

## Evidence Files

All evidence saved to: `/home/zaks/bookkeeping/audits/AGENT-FORENSIC-001/evidence/phase0/`

| File | Description |
|------|-------------|
| docker-ps.txt | Container census |
| listening-ports.txt | Port listener check |
| network-topology.txt | Docker network mapping |
| agent-health.txt | Health endpoint responses |
| agent-db-schema.txt | Full database schema |
| agent-env.txt | Environment variables (redacted) |
| compose-config.txt | docker-compose.yml |
| reachability.txt | Container-to-container connectivity |
| source-inventory.txt | Python file listing + LOC count |
| agent-logs.txt | Recent container logs |
| resource-usage.txt | Docker stats snapshot |
| volumes.txt | Volume mount details |
| tls-check.txt | TLS/SSL findings |
| processes.txt | Container process tree |
| dependencies.txt | Python package versions |
| config-files.txt | Configuration file contents |
| port-8090-check.txt | Decommissioned port verification |
