# Service Catalog

Brief reference for services, ports, commands, config paths, data, and logs. Update as services change.

## Claude Code FastAPI Wrapper
- Purpose: OpenAI-compatible API for Claude CLI (OpenWebUI integration)
- Port/URL: http://localhost:8090
- Start/stop: `sudo systemctl start|stop|restart claude-code-api` (unit: `/etc/systemd/system/claude-code-api.service`)
- Status: `systemctl status claude-code-api`
- Config/code: `/home/zaks/claude-code-openwebui`
- Logs: systemd journal (`journalctl -u claude-code-api`), app logs via uvicorn stdout
- Notes: Uses Claude CLI at `/root/.npm-global/bin/claude`, MCP config at `/root/.config/Claude/claude_desktop_config.json`

## OpenWebUI
- Port/URL: http://localhost:3000
- Start/stop: via docker compose stack `Zaks-llm`: `cd /home/zaks/Zaks-llm && docker compose up -d openwebui` / `docker compose restart openwebui`
- Config/data: docker volume `open-webui` (mounted `/app/backend/data`); docs mount `/home/zaks/documents:/app/backend/data/docs`
- Logs: `docker logs openwebui`
- Notes: Model connection points to `http://localhost:8090/v1`; depends on `vllm-qwen` on port 8000

## Docker Services (Zaks-llm compose stack)
- Path: `/home/zaks/Zaks-llm`
- Start/stop: `docker compose up -d` / `docker compose restart <service>` / `docker compose down`
- Env files: `./.env`, `./.env.langsmith.example`, `./google-workspace-mcp.env`, `./mcp-browser-use.env` (keep secrets out of git)
- Networks: `ai-network` (bridge), `rag-backend` (external `crawl4ai-rag_backend`)
- Volumes: `open-webui`, `chroma-data`, `gws-mcp-creds`, `mcp-browser-use-data`
- Services:
  - `vllm-qwen` (port 8000:8000, GPU, HF cache `/home/zaks/.cache/huggingface`)
  - `openwebui` (port 3000:8080, depends on vllm-qwen, volumes: `open-webui`, `/home/zaks/documents`)
  - `chromadb` (port 8002:8000, volume `chroma-data`)
  - `training` (GPU utility container, env from `/home/zaks/.env`, volumes: HF cache, models, data, scripts)
  - `zakops-api` (port 8080:8080, env from `.env.langsmith.example`, networks: ai-network, rag-backend, mounts `./src`, `./logs`)
  - `rag-rest-api` (port 8052:8080, connects to external `rag-db`, uses host.docker.internal for embeddings)
  - `desktop-commander` (port 3001:3000, volume `./logs/mcp`, bind mounts repo)
  - `zakops-mcp` (port 3002:3000, volume `./logs/zakops-mcp`, bind mounts repo, tool restrictions via env)
  - `google-workspace-mcp` (port 8010:8000, volume `gws-mcp-creds`, env file for OAuth secrets)
  - `mcp-browser-use` (port 8020:8000, volume `mcp-browser-use-data`, GPU)
- Logs: `docker compose logs --tail=200` (or `docker logs <container>`)

## Docker Services (google_workspace_mcp_tmp)
- Path: `/home/zaks/google_workspace_mcp_tmp`
- Start/stop: `docker compose up -d` (fill details if used)
- Notes: repo-specific MCP; document env files/volumes when active

Add more services as needed following this pattern.
