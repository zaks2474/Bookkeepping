# ZakOps System Analysis — WHAT + HOW (Evidence-Based)

Snapshot date: `2026-01-03`  
Scope: factual inventory + wiring map (no redesign, no behavior changes).

## 0) System Overview (Text Diagram)

```
zakops-dashboard (Next.js) :3003
  └─ proxies /api/* → deal_lifecycle_api.py :8090
        ├─ /api/chat*  → ChatOrchestrator (local-first; optional brain :8080)
        ├─ /api/actions* → Kinetic Action Engine (SQLite state store)
        │      └─ kinetic-actions-runner (systemd) executes READY actions → artifacts in DataRoom
        ├─ /api/deals*  → DealRegistry + DealEventStore (DataRoom/.deal-registry)
        └─ /api/tools*  → ToolRegistry + ToolGateway (approval + secret-scan + audit)

email triage (systemd timer) → Gmail MCP (stdio) → labels + quarantine dirs + EMAIL_TRIAGE.REVIEW_EMAIL actions

LangGraph “brain” :8080 (docker zakops-api) [optional] → proposals only (no execution)
vLLM :8000 (docker) + Chroma :8002 (docker) + RAG REST :8052 (docker) + OpenWebUI :3000 (docker)
```

Sources:
- Next.js proxy: `/home/zaks/zakops-dashboard/next.config.ts:rewrites`
- BFF routes: `/home/zaks/scripts/deal_lifecycle_api.py` (`chat_stream`, `list_kinetic_actions`, `list_deals`, `list_tools`, etc.)
- Runner: `/home/zaks/scripts/actions_runner.py:process_one_action` + systemd unit `/etc/systemd/system/kinetic-actions-runner.service`
- Email triage runner: `/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py:run_once`
- Brain endpoint: `/home/zaks/Zaks-llm/src/api/deal_chat.py:deal_chat`

## 1) Runtime Services Map (Ports, Responsibilities, Restart)

Evidence commands used for this snapshot:
- `ss -ltnp | rg ':(8090|3003|8080|8000|8002|8051|8052|3000|11434)\\b'`
- `docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Ports}}\\t{{.Status}}'`
- `ps aux | rg -n 'python3 .*deal_lifecycle_api|python3 .*actions_runner|next-server'`
- `systemctl list-timers --all | rg -i 'zakops-email-triage'`
- `systemctl show kinetic-actions-runner.service -p ActiveState -p MainPID -p ExecStart`
- `curl -sS http://localhost:8090/health`

| Service | Port | Invocation / Where it lives | Responsibilities | Config (primary) | Restart |
|---|---:|---|---|---|---|
| ZakOps Dashboard (Next.js) | `3003` | Process shows `next-server` (runtime); source in `/home/zaks/zakops-dashboard` | UI for Deals / Actions / Chat; calls `/api/*` | `/home/zaks/zakops-dashboard/next.config.ts:rewrites`, `/home/zaks/zakops-dashboard/src/lib/api.ts` | Restart the dev server process (see `/home/zaks/zakops-dashboard/package.json:scripts`) |
| Deal Lifecycle API (FastAPI BFF) | `8090` | Process shows `python3 deal_lifecycle_api.py --host 0.0.0.0 --port 8090`; code: `/home/zaks/scripts/deal_lifecycle_api.py` | Stable public API for UI: `/api/chat*`, `/api/actions*`, `/api/deals*`, `/api/tools*` | Env vars read in `/home/zaks/scripts/chat_orchestrator.py` and `/home/zaks/scripts/deal_lifecycle_api.py` | Restart the python process (no systemd unit found for `:8090` in `/etc/systemd/system`) |
| Kinetic Actions Runner | (none) | systemd unit `/etc/systemd/system/kinetic-actions-runner.service` runs `/home/zaks/scripts/actions_runner.py` | Lease-based runner; executes actions; writes artifacts; updates SQLite; emits deal events | Env vars in systemd unit (see unit file) + `/home/zaks/scripts/actions_runner.py` | `sudo systemctl restart kinetic-actions-runner.service` |
| Email Triage Runner (hourly) | (none) | `zakops-email-triage.timer` → `zakops-email-triage.service` runs `python3 -m email_triage_agent.run_once` in `/home/zaks/bookkeeping/scripts` | Gmail pull, deterministic classification, safe attachment download, labels, creates `EMAIL_TRIAGE.REVIEW_EMAIL` actions | `/etc/systemd/system/zakops-email-triage.*` + `/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py:load_config` | `sudo systemctl start zakops-email-triage.service` (one-shot) |
| LangGraph “brain” (zakops-api) | `8080` | docker container `zakops-api`; route defined in `/home/zaks/Zaks-llm/src/api/deal_chat.py:deal_chat` | Produces responses + proposals (must not execute actions) | `/home/zaks/Zaks-llm/docker-compose.yml` + `/home/zaks/scripts/chat_orchestrator.py:_call_brain_complete` | `docker restart zakops-api` (or `cd /home/zaks/Zaks-llm && docker compose restart zakops-api`) |
| vLLM (OpenAI-compatible) | `8000` | docker `vllm-qwen` | Local LLM inference endpoint used by chat/orchestrator | `/home/zaks/scripts/chat_orchestrator.py` (`OPENAI_API_BASE`, `VLLM_ENDPOINT`) + `/home/zaks/Zaks-llm/docker-compose.yml` | `docker restart vllm-qwen` |
| ChromaDB | `8002` | docker `chromadb` | Vector DB used by RAG stack | Container config (docker) | `docker restart chromadb` |
| RAG REST API | `8052` | docker `rag-rest-api` | Simple REST wrapper for RAG ops (`/rag/query`, etc.) | Container config (docker) | `docker restart rag-rest-api` |
| docs-rag-mcp | `8051` | docker `docs-rag-mcp` | MCP server for doc RAG (tooling path) | Tool manifests + ToolGateway config | `docker restart docs-rag-mcp` |
| OpenWebUI | `3000` | docker `openwebui` | Web UI for chat (separate from dashboard) | Container config (docker) | `docker restart openwebui` |
| Ollama | `11434` | `ollama` process | Local model server (not the default chat path in this snapshot) | Ollama config | restart `ollama` service/process as installed |

Notes:
- The dashboard check script `/home/zaks/scripts/dataroom_dashboard.sh` probes Chroma at `/api/v1/heartbeat`; on this machine Chroma responds `410 Gone` (“use /v2 apis”), so that health check is currently stale.

## 2) Agents Inventory (Runtime vs Design-Time)

### 2.1 Local Email Triage Agent (runtime)

Primary module: `/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py`
- Trigger: systemd timer `zakops-email-triage.timer` (see `/etc/systemd/system/zakops-email-triage.timer`)
- Workflow entry: `run_once(cfg)` + `process_one_message(...)`
- Gmail MCP wiring: `/home/zaks/bookkeeping/scripts/email_triage_agent/mcp_stdio.py:McpStdioSession` + `/home/zaks/bookkeeping/scripts/email_triage_agent/gmail_mcp.py:GmailMcpClient`
- Gmail MCP command selection: `/home/zaks/bookkeeping/scripts/email_triage_agent/gmail_mcp.py:gmail_mcp_command`
- Deterministic classifier: `/home/zaks/bookkeeping/scripts/email_triage_agent/triage_logic.py:classify_email` + `decide_actions_and_labels`
- Idempotency store: `/home/zaks/bookkeeping/scripts/email_triage_agent/state_db.py:EmailTriageStateDB` (SQLite WAL)
- Action emission: `/home/zaks/bookkeeping/scripts/email_triage_agent/kinetic_actions.py:KineticActionsClient.create_action` creates `EMAIL_TRIAGE.REVIEW_EMAIL`

### 2.2 LangGraph “brain” (runtime, optional)

Endpoint: `POST /api/deal-chat` in `/home/zaks/Zaks-llm/src/api/deal_chat.py:deal_chat`
- Contract: proposals only; no action execution (docstring in `deal_chat`)
- Tracing behavior: `configure_langsmith_safe_tracing()` early-returns unless `LANGCHAIN_TRACING_V2=true` (`/home/zaks/Zaks-llm/src/core/tracing.py:is_tracing_enabled`)
- Tracing is explicitly disabled in container env (`/home/zaks/Zaks-llm/docker-compose.yml` sets `LANGCHAIN_TRACING_V2=false`)

### 2.3 LangSmith Agent Builder (design mirror; not in local runtime path)

Source-controlled mirror:
- `/home/zaks/bookkeeping/configs/email_triage_agent/agent_config/*` (see `/home/zaks/bookkeeping/configs/email_triage_agent/agent_config/EXPORT_NOTES.md`)

Export mechanism (manual/offline):
- `/home/zaks/bookkeeping/scripts/email_triage_agent/export_agent_builder_config.py:main` fetches thread history and reconstructs `/memories/*` files

Runtime evidence of “not active locally”:
- No systemd units besides the runner + triage timer in `/etc/systemd/system/`
- `ps aux | rg -n 'deepagents|langsmith'` shows no long-running local process (only on-demand export script exists)

## 3) Tooling + MCP + ToolGateway Wiring (How tools are invoked)

### 3.1 Tool manifests → ToolRegistry

Tool manifests directory:
- `/home/zaks/scripts/tools/manifests/*.yaml`

Loader:
- `/home/zaks/scripts/tools/registry.py:ToolRegistry.load_from_directory`
- Directory override env var: `ZAKOPS_TOOLS_DIR` (`DEFAULT_MANIFESTS_DIR` in `tools/registry.py`)

### 3.2 Tool invocation gate (ToolGateway)

Core gateway:
- `/home/zaks/scripts/tools/gateway.py:ToolGateway.invoke`

Policy gates (all enforced inside `invoke()`):
- Allowlist/denylist gate: `/home/zaks/scripts/tools/gateway.py:ToolGateway._check_permissions` + envs in `ToolGatewayConfig.from_env`
- DB approval gate: `/home/zaks/scripts/tools/gateway.py:ToolGateway._check_approval_from_db` (Action must be `READY` or `PROCESSING`)
- Secret-scan gate: `/home/zaks/scripts/tools/gateway.py:SecretScanner.scan`
- SSRF gate for HTTP tools: `/home/zaks/scripts/tools/gateway.py:SSRFProtection.check_url`
- Audit logging: `/home/zaks/scripts/tools/gateway.py:ToolAuditLogger` writes `tool_invocation_log` table into `ZAKOPS_STATE_DB` path (`ToolGatewayConfig.audit_db_path`)

MCP runtime options:
- stdio spawn-per-call: `/home/zaks/scripts/tools/gateway.py:ToolGateway._invoke_mcp_stdio`
- docker runtime: `/home/zaks/scripts/tools/gateway.py:ToolGateway._invoke_mcp_docker` + TTL idle stop (`_stop_idle_containers`)

### 3.3 Unified manifest for planning/RAG (tools + internal capabilities)

Builder:
- `/home/zaks/scripts/tools/manifest/builder.py:build_unified_manifest` (merges internal capabilities via `actions.capabilities.registry.get_registry` + tools via `tools.registry.get_tool_registry`)

Loader + matcher:
- `/home/zaks/scripts/tools/manifest/registry.py:UnifiedManifestRegistry` (`match()` uses token Jaccard)

### 3.4 Gmail MCP: two distinct invocation paths (important)

Path A (Email triage agent): direct stdio MCP process, persistent per run
- `/home/zaks/bookkeeping/scripts/email_triage_agent/mcp_stdio.py:McpStdioSession`
- Command selection `/home/zaks/bookkeeping/scripts/email_triage_agent/gmail_mcp.py:gmail_mcp_command`:
  - env override `GMAIL_MCP_COMMAND`
  - else falls back to `npx -y @gongrzhe/server-gmail-autoauth-mcp`

Path B (ToolGateway tool manifests): manifest defaults to `npx` launcher (overridable)
- Example manifest: `/home/zaks/scripts/tools/manifests/gmail__send_email.yaml` (`mcp_stdio_command: ["npx","-y","@gongrzhe/server-gmail-autoauth-mcp"]`)
- Override supported in ToolGateway: `GMAIL_MCP_COMMAND` (or `MCP_STDIO_COMMAND_GMAIL`) to keep all Gmail calls on one launcher.

## 4) Orchestration & End-to-End Workflows (Current Reality)

### 4.1 Email ingestion / triage path (hourly)

Trigger:
- systemd timer `/etc/systemd/system/zakops-email-triage.timer` → service runs `python3 -m email_triage_agent.run_once` (see `/etc/systemd/system/zakops-email-triage.service`)

Per-run steps (code path):
1) Load config from env/args (`/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py:load_config`)
2) Start Gmail MCP stdio session (`run_once` uses `McpStdioSession(command=gmail_mcp_command())`)
3) Search Gmail (`/home/zaks/bookkeeping/scripts/email_triage_agent/gmail_mcp.py:GmailMcpClient.search_emails`)
4) Idempotency check + mark_started (`/home/zaks/bookkeeping/scripts/email_triage_agent/state_db.py:EmailTriageStateDB.get/mark_started`)
5) Read email (`GmailMcpClient.read_email`) + deterministic classification (`triage_logic.py:decide_actions_and_labels`)
6) If `DEAL_SIGNAL`, materialize quarantine dir and write `email_body.txt` + `email.json` (`run_once.py:process_one_message`)
7) Download safe attachments only (`run_once.py:download_safe_attachments` + `is_safe_attachment`)
8) Create an approval-gated Kinetic Action (`EMAIL_TRIAGE.REVIEW_EMAIL`) via BFF (`run_once.py` calls `KineticActionsClient.create_action`)
9) Apply labels only after success (`run_once.py:process_one_message` calls `gmail.add_labels`) and mark processed in state DB (`EmailTriageStateDB.mark_processed`)

### 4.2 Quarantine → Deal creation pipeline (action-based, not legacy quarantine)

Kinetic capability:
- Manifest: `/home/zaks/scripts/actions/capabilities/email_triage.review_email.v1.yaml` (`action_type: EMAIL_TRIAGE.REVIEW_EMAIL`)

Executor:
- `/home/zaks/scripts/actions/executors/email_triage_review_email.py:EmailTriageReviewEmailExecutor.execute`

Behavior on approved execution:
- Resolves/creates a deal in the existing DealRegistry (`ctx.registry`) and stores email→deal mapping (`registry.add_email_deal_mapping`) (`email_triage_review_email.py`)
- Creates a deterministic deal folder under `DataRoom/00-PIPELINE/Inbound` and standard subfolders (`_create_deal_workspace`, `_inbound_root`)
- Persists email artifacts under `<deal>/07-Correspondence/` (markdown + manifest JSON) and copies quarantine payload files into an attachments subfolder (`_copy_quarantine_payload`)

### 4.3 Kinetic Actions lifecycle (state machine + runner)

API surface (BFF):
- `/home/zaks/scripts/deal_lifecycle_api.py:list_kinetic_actions` (`GET /api/actions`)
- `/home/zaks/scripts/deal_lifecycle_api.py:create_kinetic_action` (`POST /api/actions`)
- `/home/zaks/scripts/deal_lifecycle_api.py:approve_kinetic_action` (`POST /api/actions/{id}/approve`)
- `/home/zaks/scripts/deal_lifecycle_api.py:execute_kinetic_action` (`POST /api/actions/{id}/execute`)
- `/home/zaks/scripts/deal_lifecycle_api.py:cancel_kinetic_action` (`POST /api/actions/{id}/cancel`)
- `/home/zaks/scripts/deal_lifecycle_api.py:retry_kinetic_action` (`POST /api/actions/{id}/retry`) (UI compatibility)
- `/home/zaks/scripts/deal_lifecycle_api.py:actions_runner_status` (`GET /api/actions/runner-status`)
- `/home/zaks/scripts/deal_lifecycle_api.py:debug_kinetic_action` (`GET /api/actions/{id}/debug`)

Persistence + correctness:
- SQLite WAL store schema and transitions: `/home/zaks/scripts/actions/engine/store.py:ActionStore` (`SCHEMA_SQL`, `approve_action`, `request_execute`, `begin_processing`, `mark_processing_timeouts`)
- Lease runner loop: `/home/zaks/scripts/actions_runner.py:process_one_action` (per-action lock heartbeat + try/finally completion)

### 4.4 Chat orchestration → proposals → actions

Frontend contract:
- `/home/zaks/zakops-dashboard/src/lib/api.ts:streamChatMessage` (`POST /api/chat`, SSE)
- `/home/zaks/zakops-dashboard/src/lib/api.ts:sendChatMessage` (`POST /api/chat/complete`)
- `/home/zaks/zakops-dashboard/src/lib/api.ts:executeChatProposal` (`POST /api/chat/execute-proposal`)
- Session load: `/home/zaks/zakops-dashboard/src/lib/api.ts:getChatSession` (`GET /api/chat/session/{id}`)

Backend contract:
- `/home/zaks/scripts/deal_lifecycle_api.py:chat_stream`, `chat_complete`, `execute_proposal`, `get_chat_session`

Orchestrator core:
- `/home/zaks/scripts/chat_orchestrator.py:ChatOrchestrator` (evidence builder, routing, secret scan, proposals)
- Brain integration toggle: `/home/zaks/scripts/chat_orchestrator.py:_brain_mode` + `ZAKOPS_BRAIN_MODE` env

“Send email” behavior (separate from draft):
- Drafting is separate from sending (send is irreversible and must be approval-gated): `/home/zaks/scripts/actions/executors/communication_send_email.py:SendEmailExecutor`

## 5) Frontend Integration (Contracts + UX mechanics)

### 5.1 /api proxy target

Dashboard proxies `/api/:path*` → `${API_URL || http://localhost:8090}/api/:path*`:
- `/home/zaks/zakops-dashboard/next.config.ts:rewrites`

### 5.2 Actions UI

API client functions:
- `/home/zaks/zakops-dashboard/src/lib/api.ts:getKineticActions`
- `/home/zaks/zakops-dashboard/src/lib/api.ts:approveKineticAction`
- `/home/zaks/zakops-dashboard/src/lib/api.ts:runKineticAction`
- `/home/zaks/zakops-dashboard/src/lib/api.ts:cancelKineticAction`
- `/home/zaks/zakops-dashboard/src/lib/api.ts:retryKineticAction`
- `/home/zaks/zakops-dashboard/src/lib/api.ts:updateKineticActionInputs`
- Download URL helper: `/home/zaks/zakops-dashboard/src/lib/api.ts:getArtifactDownloadUrl`

UI button gating (status-driven):
- `/home/zaks/zakops-dashboard/src/components/actions/action-card.tsx` sets:
  - `canApprove` when `PENDING_APPROVAL`
  - `canRun` when `READY`
  - `canCancel` when `PENDING_APPROVAL` or `READY`
  - `canRetry` when `FAILED` and `error.retryable !== false`

Backend normalization to match Zod expectations:
- `/home/zaks/scripts/deal_lifecycle_api.py:_action_payload_to_frontend`

### 5.3 Chat UI (freeze resistance + history persistence)

Token batching (reduce per-token rerenders):
- `/home/zaks/zakops-dashboard/src/app/chat/page.tsx` uses `tokenBufferRef` + `flushTimeoutRef` to batch streaming updates.

History persistence across refresh (backend-first then localStorage fallback):
- `/home/zaks/zakops-dashboard/src/app/chat/page.tsx` loads `sessionId` from localStorage, then calls `/api/chat/session/{id}` via `getChatSession`.

## 6) Findings + Gaps (Prioritized)

### P0 (system can break or mislead operators)

1) **ToolGateway Gmail tools likely non-functional due to missing binary**
   - Tool manifests require `mcp_stdio_command: ["gmail-mcp"]` (example: `/home/zaks/scripts/tools/manifests/gmail__send_email.yaml`)
   - Host PATH check: `command -v gmail-mcp` returned no path in this snapshot.

2) **Backend `:8090` is not managed by systemd**
   - Only runner + triage units exist in `/etc/systemd/system/`.
   - Risk: manual restart required after code changes; drift between what’s on disk and what’s running.

3) **Chroma health probe in dashboard script is stale**
   - `/home/zaks/scripts/dataroom_dashboard.sh` probes `http://localhost:8002/api/v1/heartbeat`; this Chroma returns `410 Gone`.

### P1 (stability/maintainability hazards)

1) **Two separate Gmail MCP invocation stacks**
   - Email triage uses `gmail_mcp_command()` fallback to `npx @gongrzhe/server-gmail-autoauth-mcp` (`/home/zaks/bookkeeping/scripts/email_triage_agent/gmail_mcp.py`)
   - ToolGateway uses manifests that expect `gmail-mcp` (different surface and secrets model)

2) **Quarantine UI uses legacy quarantine endpoints, not action-based quarantine**
   - `/home/zaks/zakops-dashboard/src/app/quarantine/page.tsx` calls `getQuarantineItems/getQuarantineHealth/resolveQuarantineItem` from `/home/zaks/zakops-dashboard/src/lib/api.ts` (legacy `/api/quarantine*`), while triage flow is action-based (`EMAIL_TRIAGE.REVIEW_EMAIL`).

3) **UI “stuck processing” threshold differs from backend TTL**
   - UI warns after 2 minutes (`PROCESSING_STUCK_THRESHOLD_MS` in `/home/zaks/zakops-dashboard/src/components/actions/action-card.tsx`)
   - Backend runner TTL is `ZAKOPS_ACTION_PROCESSING_TTL_SECONDS` (exposed in `/home/zaks/scripts/deal_lifecycle_api.py:actions_runner_status`).

### P2 (performance/future enhancements)

1) **Unified manifest file freshness**
   - `scripts/tools/manifest/manifest.json` has its own `generated_at` timestamp and must be regenerated to include newly added capabilities (`/home/zaks/scripts/tools/manifest/builder.py:build_unified_manifest`).

## Appendix: “Where to look” (Code anchors)

- BFF API: `/home/zaks/scripts/deal_lifecycle_api.py` (FastAPI routes)
- Chat orchestration: `/home/zaks/scripts/chat_orchestrator.py:ChatOrchestrator`
- Action runner: `/home/zaks/scripts/actions_runner.py:process_one_action`
- Action persistence: `/home/zaks/scripts/actions/engine/store.py:ActionStore`
- Executors: `/home/zaks/scripts/actions/executors/*` (e.g., `EmailTriageReviewEmailExecutor`, `SendEmailExecutor`, `ToolInvokeExecutor`)
- Tooling: `/home/zaks/scripts/tools/gateway.py:ToolGateway`, `/home/zaks/scripts/tools/registry.py:ToolRegistry`
- Email triage: `/home/zaks/bookkeeping/scripts/email_triage_agent/*`
- Brain: `/home/zaks/Zaks-llm/src/api/deal_chat.py:deal_chat`
- Frontend API client: `/home/zaks/zakops-dashboard/src/lib/api.ts`
- Frontend pages: `/home/zaks/zakops-dashboard/src/app/actions/page.tsx`, `/home/zaks/zakops-dashboard/src/app/chat/page.tsx`
