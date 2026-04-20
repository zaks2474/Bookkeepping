# LangGraph + LangSmith Migration (Option A) — Inventory & Findings

Date: 2025-12-30

This document is required by the migration non‑negotiables: **do not change contracts until we have concrete evidence of what’s running and where LangGraph/LangSmith already exists.**

## A1) Running services + ports (evidence)

### Ports listening (local)

Command:
```bash
ss -ltnp | rg -n ":(3000|3001|3003|8000|8020|8030|8051|8052|8080|8090)"
```

Output (process details restricted in this environment; ports confirmed):
```text
LISTEN 0 0 0.0.0.0:8090 0.0.0.0:*
LISTEN 0 0 0.0.0.0:8080 0.0.0.0:*
LISTEN 0 0 0.0.0.0:8030 0.0.0.0:*
LISTEN 0 0 0.0.0.0:8020 0.0.0.0:*
LISTEN 0 0 0.0.0.0:8000 0.0.0.0:*
LISTEN 0 0 0.0.0.0:8051 0.0.0.0:*
LISTEN 0 0 0.0.0.0:8052 0.0.0.0:*
LISTEN 0 0 0.0.0.0:3001 0.0.0.0:*
LISTEN 0 0 0.0.0.0:3000 0.0.0.0:*
LISTEN 0 0 0.0.0.0:3003 0.0.0.0:*
```

### Key processes (host PID namespace evidence)

Command:
```bash
ps -eo pid,ppid,user,cmd --sort=start_time | rg -n "deal_lifecycle_api.py|next dev|vllm\\.entrypoints\\.openai\\.api_server|open_webui\\.main|rag_rest_api"
```

Relevant output:
```text
python3 -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-32B-Instruct-AWQ ...
/usr/local/bin/python3.12 /usr/local/bin/uvicorn src.api.rag_rest_api:app --host 0.0.0.0 --port 8080
/usr/local/bin/python3 -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 ...
npm exec next dev --port 3003
python3 deal_lifecycle_api.py --host 0.0.0.0
```

### Docker containers + ports (snapshot evidence)

Source: `bookkeeping/snapshots/docker-containers-ports.txt`

Key lines:
```text
zakops-api   ... 0.0.0.0:8080->8080/tcp
rag-rest-api ... 0.0.0.0:8052->8080/tcp
openwebui    ... 0.0.0.0:3000->8080/tcp
vllm-qwen    ... 0.0.0.0:8000->8000/tcp
```

## A2) Codebase scan: LangGraph/LangSmith presence

Command:
```bash
rg -n "langgraph|StateGraph|langsmith|LANGSMITH|LANGCHAIN_TRACING|traceable|RunnableConfig|Agent Builder" /home/zaks/Zaks-llm/src | head -n 120
```

Key hits (representative):
- `Zaks-llm/src/agents/systemops.py` uses `StateGraph`
- `Zaks-llm/src/agents/sub_agents/base.py` uses `StateGraph` + `ToolNode`
- `Zaks-llm/src/deal_origination/modules/orchestrator.py` uses `StateGraph`
- `Zaks-llm/src/core/tracing.py` implements safe LangSmith tracing defaults

Conclusion: **LangGraph/LangSmith are already in `Zaks-llm` (the 8080 “zakops-api” container).**

## A3) Python deps (what’s installed where)

### `Zaks-llm` dependencies

Source: `Zaks-llm/requirements.txt`
```text
langgraph==0.2.45
langchain==0.3.7
langchain-openai==0.2.8
langchain-community==0.3.5
langsmith==0.1.147
```

### Host python (8090) dependencies

Evidence (host python cannot import these libs):
```text
langgraph False
langsmith False
langchain False
```

Conclusion: **LangGraph execution must run in 8080 (`zakops-api`)**, and 8090 must integrate via HTTP adapter + mocks for tests.

## A4) Existing tracing configuration (LangSmith)

### Host env vars

Evidence (names only; no values):
```bash
env | cut -d= -f1 | rg -n "^(LANGCHAIN_|LANGSMITH|ZAKOPS_LANGSMITH)"
```
No LangSmith env vars were present in the current host shell environment.

### Container tracing config source (repo evidence)

Source: `Zaks-llm/docker-compose.yml`
- `zakops-api` uses `env_file: ./.env.langsmith.example`

Source: `Zaks-llm/.env.langsmith.example`
- Defaults to `LANGCHAIN_TRACING_V2=false`
- Enforces safe mode defaults: `LANGCHAIN_HIDE_INPUTS=true`, `LANGCHAIN_HIDE_OUTPUTS=true`

## A5) Current orchestration entrypoints (evidence)

### Public BFF (dashboard contract)
- `scripts/deal_lifecycle_api.py` (FastAPI @ :8090)
  - `POST /api/chat` (SSE)
  - `POST /api/chat/complete`
  - `POST /api/chat/execute-proposal`
  - `GET /api/chat/session/{session_id}`

### Current chat/orchestration engine (host)
- `scripts/chat_orchestrator.py` (LLM routing + deterministic patterns + proposal parsing + proposal execution)

### Existing LangGraph engine (container)
- `Zaks-llm/src/api/server.py` (FastAPI inside `zakops-api` @ :8080)
- `Zaks-llm/src/agents/*` (LangGraph-based agents + safe tracing)

## A6) Existing “graph-like” routers/pipelines already implemented

- `Zaks-llm/src/agents/orchestrator.py` (routes to domain sub-agents; uses TaskPacket protocol)
- `Zaks-llm/src/agents/systemops.py` and `Zaks-llm/src/agents/sub_agents/base.py` (StateGraph-based workflows)

## Known constraints / blockers

- Docker socket access is restricted from this environment (cannot `docker ps` / restart containers here).
- Any integration must be verifiable via:
  - unit/contract tests with mocked 8080 HTTP calls, and
  - manual validation steps (curl + browser) when operator can restart/update containers.

