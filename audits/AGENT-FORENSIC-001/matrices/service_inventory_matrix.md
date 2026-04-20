# Service Inventory Matrix
| Service | Container Name | Ports | Status | Evidence |
|---|---|---|---|---|
| Agent API | zakops-agent-api | 8095->8000/tcp | Up (healthy) | evidence/phase0/00_service_census.txt |
| Agent DB | zakops-agent-db | 5432/tcp | Up (healthy) | evidence/phase0/00_service_census.txt |
| Backend API | zakops-backend-backend-1 | 8091->8091/tcp | Up (healthy) | evidence/phase0/00_service_census.txt |
| Backend DB | zakops-postgres-1 | 5432->5432/tcp | Up (healthy) | evidence/phase0/00_service_census.txt |
| Backend Redis | zakops-redis-1 | 6379->6379/tcp | Up (healthy) | evidence/phase0/00_service_census.txt |
| Backend Postgres (compose) | zakops-backend-postgres-1 | (internal) | Up (healthy) | evidence/phase0/00_service_census.txt |
| Backend Redis (compose) | zakops-backend-redis-1 | (internal) | Up (healthy) | evidence/phase0/00_service_census.txt |
| Backend Outbox Worker | zakops-backend-outbox-worker-1 | 8091/tcp | Up (healthy) | evidence/phase0/00_service_census.txt |
| Backend Langfuse | zakops-backend-langfuse-1 | (internal) | Restarting | evidence/phase0/00_service_census.txt |
| vLLM | vllm-qwen | 8000->8000/tcp | Up | evidence/phase0/00_service_census.txt |
| RAG API | rag-rest-api | 8052->8080/tcp | Up | evidence/phase0/00_service_census.txt |
| RAG DB | rag-db | 5434->5432/tcp | Up | evidence/phase0/00_service_census.txt |
| OpenWebUI | openwebui | 3000->8080/tcp | Up | evidence/phase0/00_service_census.txt |
| MCP (host listener) | N/A | 9100/tcp | LISTEN | evidence/phase0/00_service_census.txt |
