# ZakOps Configuration Map (Key → Location → Default → Effect)

Snapshot date: `2026-01-03`  
Goal: document **where config lives**, **who reads it**, and **how to override safely** (no secrets/values).

## 1) Configuration Sources + Precedence (Current Reality)

**Highest precedence → lowest precedence**
1) **CLI args** (where implemented)  
   - Example: Kinetic runner uses CLI flags (`/home/zaks/scripts/actions_runner.py:main`)
2) **Process environment variables** (systemd unit, shell export, docker env)  
   - Examples: `/etc/systemd/system/kinetic-actions-runner.service`, `/etc/systemd/system/zakops-email-triage.service`, `/home/zaks/zakops-dashboard/next.config.ts:rewrites`, `/home/zaks/Zaks-llm/docker-compose.yml`
3) **Repo-managed manifests** (checked into repo)  
   - Tool manifests: `/home/zaks/scripts/tools/manifests/*.yaml` (`/home/zaks/scripts/tools/registry.py:ToolRegistry.load_from_directory`)
   - Action capability manifests: `/home/zaks/scripts/actions/capabilities/*.yaml` (`/home/zaks/scripts/actions/capabilities/registry.py:get_registry`)
   - Unified manifest: `/home/zaks/scripts/tools/manifest/manifest.json` (`/home/zaks/scripts/tools/manifest/registry.py:DEFAULT_MANIFEST_PATH`)
4) **Persistent state stores** (SQLite / registry JSON / events)  
   - Kinetic Actions + Tool audit + Action Memory: `ZAKOPS_STATE_DB` (`/home/zaks/scripts/actions/engine/store.py:_default_state_db_path`, `/home/zaks/scripts/tools/gateway.py:ToolGatewayConfig.audit_db_path`, `/home/zaks/scripts/actions/memory/store.py:_default_state_db_path`)
   - Deal registry + case files + events: under `DATAROOM_ROOT/.deal-registry` (`/home/zaks/scripts/actions_runner.py` constants)
5) **Hardcoded defaults** in code (used only when no env/arg set)

## 2) High-Value Config Keys (Table)

Legend:
- **Location**: where it is typically set/owned (systemd, docker, shell, file)
- **Read path**: exact code location that reads it
- **Safe override**: how to change without committing secrets

### 2.1 Core paths & state

| Key | Location (owned by) | Read path (code) | Default | Safe override | Effect |
|---|---|---|---|---|---|
| `DATAROOM_ROOT` | systemd unit and/or shell env | `/home/zaks/scripts/actions_runner.py` (module constant), `/home/zaks/scripts/deal_lifecycle_api.py` (module constant), executors like `/home/zaks/scripts/actions/executors/email_triage_review_email.py:_dataroom_root` | `/home/zaks/DataRoom` | Set env var (runner unit, backend shell, etc.) | Controls where deals, artifacts, registry live; artifact path validation uses this root |
| `ZAKOPS_STATE_DB` | systemd unit and/or shell env | `/home/zaks/scripts/actions/engine/store.py:_default_state_db_path`, `/home/zaks/scripts/tools/gateway.py:ToolGatewayConfig.audit_db_path`, `/home/zaks/scripts/actions/memory/store.py:_default_state_db_path` | `/home/zaks/DataRoom/.deal-registry/ingest_state.db` | Set env var (runner unit, backend shell); ensure filesystem perms | SQLite file for action queue/state, tool audit log, and action memory |

### 2.2 Kinetic Action Engine runner (durability + correctness)

| Key | Location (owned by) | Read path (code) | Default | Safe override | Effect |
|---|---|---|---|---|---|
| `ZAKOPS_ACTION_PROCESSING_TTL_SECONDS` | systemd unit (runner) | `/home/zaks/scripts/actions_runner.py:main` (arg default) and `/home/zaks/scripts/deal_lifecycle_api.py:actions_runner_status` (reported) | `3600` | Set in `/etc/systemd/system/kinetic-actions-runner.service` env; restart runner | PROCESSING watchdog TTL; after this, runner/store can mark action FAILED (see `ActionStore.mark_processing_timeouts`) |
| `--runner-name` | systemd unit ExecStart args | `/home/zaks/scripts/actions_runner.py:main` | `kinetic_actions` (unit sets it explicitly) | Edit unit file, then `systemctl daemon-reload` + restart | Lease namespace in `action_runner_leases` table |
| `--lease-seconds` | systemd unit ExecStart args | `/home/zaks/scripts/actions_runner.py:main` | `30` (unit sets) | Edit unit file + restart | Global runner lease renewal interval; prevents multi-runner |
| `--poll-seconds` | systemd unit ExecStart args | `/home/zaks/scripts/actions_runner.py:main` | `2.0` (unit sets) | Edit unit file + restart | How often runner polls for due work |
| `--action-lock-seconds` | systemd unit ExecStart args | `/home/zaks/scripts/actions_runner.py:main` | `300` (unit sets) | Edit unit file + restart | Per-action lease/lock duration; heartbeat in `process_one_action` |

### 2.3 ToolGateway (Phase 0.5) policy + runtime

| Key | Location (owned by) | Read path (code) | Default | Safe override | Effect |
|---|---|---|---|---|---|
| `ZAKOPS_TOOL_GATEWAY_ENABLED` | shell env / systemd env | `/home/zaks/scripts/tools/gateway.py:ToolGatewayConfig.from_env` | `false` | Export env or set in service env; restart affected process | Enables ToolGateway; when disabled, tool calls return `GATEWAY_DISABLED` |
| `ZAKOPS_TOOL_REQUIRE_ALLOWLIST` | shell env / systemd env | `/home/zaks/scripts/tools/gateway.py:ToolGatewayConfig.from_env` | `true` | Export env | Forces explicit allowlist when gateway enabled |
| `ZAKOPS_TOOL_ALLOWLIST` | shell env / systemd env | `/home/zaks/scripts/tools/gateway.py:ToolGatewayConfig.from_env` | empty | Export env with comma-separated tool_ids | Limits which tools can run (policy gate) |
| `ZAKOPS_TOOL_DENYLIST` | shell env / systemd env | `/home/zaks/scripts/tools/gateway.py:ToolGatewayConfig.from_env` | empty | Export env with comma-separated tool_ids | Explicit deny overrides allow |
| `ZAKOPS_MCP_RUNTIME_MODE` | shell env / systemd env | `/home/zaks/scripts/tools/gateway.py:ToolGatewayConfig.from_env` | `stdio` | Set to `docker` only if manifests have docker config | Chooses MCP runtime: stdio spawn-per-call vs docker-started |
| `ZAKOPS_TOOLS_DIR` | shell env | `/home/zaks/scripts/tools/registry.py:DEFAULT_MANIFESTS_DIR` | `/home/zaks/scripts/tools/manifests` | Set env var | Changes directory for tool YAML manifests |
| `ZAKOPS_UNIFIED_MANIFEST_PATH` | shell env | `/home/zaks/scripts/tools/manifest/registry.py:DEFAULT_MANIFEST_PATH` | `/home/zaks/scripts/tools/manifest/manifest.json` | Set env var | Changes unified manifest used for matching/planning |

### 2.4 Email triage runner (systemd timer-driven)

All are read in `/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py:load_config` unless noted.

| Key | Location (owned by) | Read path (code) | Default | Safe override | Effect |
|---|---|---|---|---|---|
| `EMAIL_TRIAGE_QUERY` | systemd env / shell env | `run_once.py:load_config` | `in:inbox -label:ZakOps/Processed newer_than:30d` (`DEFAULT_QUERY`) | Set env var; keep query narrow | Gmail search query (scope of triage) |
| `EMAIL_TRIAGE_MAX_PER_RUN` | systemd env / shell env | `run_once.py:load_config` | `50` | Set env var | Limits messages per run |
| `EMAIL_TRIAGE_QUARANTINE_ROOT` | systemd env / shell env | `run_once.py:load_config` | `/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE` | Set env var | Filesystem location for quarantined email payloads |
| `EMAIL_TRIAGE_STATE_DB` | systemd env / shell env | `run_once.py:load_config` | `/home/zaks/DataRoom/.deal-registry/email_triage_state.db` | Set env var | SQLite DB for triage idempotency (processed/failed) |
| `EMAIL_TRIAGE_VENDOR_PATTERNS_MD` | systemd env / shell env | `run_once.py:load_config` | `/home/zaks/bookkeeping/configs/email_triage_agent/agent_config/memories/vendor_patterns.md` | Set env var | Vendor pattern hints used by URL classifier (`vendor_patterns.py`) |
| `EMAIL_TRIAGE_DRY_RUN` | systemd env / shell env | `run_once.py:_bool_env` | `false` | Set env var | If true: do not write labels or download attachments |
| `EMAIL_TRIAGE_MARK_AS_READ` | systemd env / shell env | `run_once.py:_bool_env` | `false` | Set env var | If true: removes `UNREAD` label after processing |
| `EMAIL_TRIAGE_MAX_ATTACHMENT_MB` | systemd env / shell env | `run_once.py:_int_env` | `25` | Set env var | Size cap for downloads |
| `EMAIL_TRIAGE_SAFE_EXTS` | systemd env / shell env | `run_once.py:_csv_env_set` | `pdf,doc,docx,rtf,txt,xls,xlsx,csv,ppt,pptx,zip` | Set env var | Allowlist for attachment types |
| `EMAIL_TRIAGE_UNSAFE_EXTS` | systemd env / shell env | `run_once.py:_csv_env_set` | `exe,bat,cmd,...` | Set env var | Denylist for attachment types |
| `EMAIL_TRIAGE_ACTIONS_BASE_URL` | systemd env | `run_once.py:load_config` | `http://localhost:8090` | Set env var | Where triage posts `POST /api/actions` to create `EMAIL_TRIAGE.REVIEW_EMAIL` |
| `EMAIL_TRIAGE_ENABLE_ACTIONS` | systemd env | `run_once.py:_bool_env` | `true` | Set env var | Enables action creation; when false triage only labels and writes state |

Gmail MCP command selection (triage-only):
- `GMAIL_MCP_COMMAND` read by `/home/zaks/bookkeeping/scripts/email_triage_agent/gmail_mcp.py:gmail_mcp_command` (space-separated override).  
If unset, it falls back to `npx -y @gongrzhe/server-gmail-autoauth-mcp`.

### 2.5 Chat orchestration (BFF)

All are read in `/home/zaks/scripts/chat_orchestrator.py` unless noted.

| Key | Location (owned by) | Read path (code) | Default | Safe override | Effect |
|---|---|---|---|---|---|
| `OPENAI_API_BASE` | shell env | `chat_orchestrator.py` (module constant) | `http://localhost:8000/v1` | Export env before starting `deal_lifecycle_api.py` | Points local chat to vLLM OpenAI-compatible endpoint |
| `DEFAULT_MODEL` / `VLLM_MODEL` | shell env | `chat_orchestrator.py` (module constants) | `Qwen/Qwen2.5-32B-Instruct-AWQ` | Export env | Model name passed to provider/router |
| `VLLM_TIMEOUT` | shell env | `chat_orchestrator.py` | `120` seconds | Export env | Request timeout for local LLM calls |
| `ALLOW_CLOUD_DEFAULT` | shell env | `chat_orchestrator.py` (`ALLOW_CLOUD`) | `false` | Export env | Enables cloud fallback for eligible flows (still gated; secrets scanned) |
| `ZAKOPS_BRAIN_URL` | shell env | `chat_orchestrator.py` | `http://localhost:8080` | Export env | Target for LangGraph brain when enabled |
| `ZAKOPS_BRAIN_MODE` | shell env | `chat_orchestrator.py:_brain_mode` | `off` | Export env `off|auto|force` | Enables/disables brain; `force` fails if brain unavailable |
| `ZAKOPS_BRAIN_TIMEOUT_S` / `ZAKOPS_BRAIN_TIMEOUT` | shell env | `chat_orchestrator.py` | `30` seconds | Export env | Timeout for brain HTTP calls |
| `CHAT_CACHE_ENABLED` | shell env | `chat_orchestrator.py` | `true` | Export env | Enables chat cache layer (`chat_cache.py:get_cache`) |
| `CHAT_DETERMINISTIC_EXTENDED` | shell env | `chat_orchestrator.py` | `true` | Export env | Enables “deterministic-first” helpers (see router/evidence builder usage) |
| `CHAT_PERSISTENCE_ENABLED` | shell env | `chat_orchestrator.py` (try/except import) | `true` (if persistence module importable) | Export env | Enables SQLite-backed chat session persistence (`email_ingestion/chat_persistence.py`) |

### 2.6 LangGraph brain container (zakops-api)

Primary location: `/home/zaks/Zaks-llm/docker-compose.yml` (service `zakops-api`)

| Key | Location (owned by) | Read path (code) | Default | Safe override | Effect |
|---|---|---|---|---|---|
| `LANGCHAIN_TRACING_V2` | docker compose env | `/home/zaks/Zaks-llm/src/core/tracing.py:is_tracing_enabled` | `false` (compose sets it explicitly) | Keep `false` for current phase | Controls LangSmith tracing enablement (must remain off per constraints) |
| `LANGCHAIN_API_KEY` | docker compose env | tracing libs | empty in compose | **Do not commit**; only in local env if ever enabled | LangSmith auth (disabled now) |
| `OPENAI_API_BASE` | docker compose env | brain providers | `http://vllm-qwen:8000/v1` (compose) | Update compose env | Brain’s local LLM endpoint |

### 2.7 Frontend (Next.js dashboard)

| Key | Location (owned by) | Read path (code) | Default | Safe override | Effect |
|---|---|---|---|---|---|
| `API_URL` | Next.js environment | `/home/zaks/zakops-dashboard/next.config.ts:rewrites` | `http://localhost:8090` | Set env var before `next dev` / `next start` | Controls where `/api/*` is proxied |

### 2.8 Tool manifests (per-tool config)

Tool manifests are YAML files in `/home/zaks/scripts/tools/manifests/` (loaded by `/home/zaks/scripts/tools/registry.py:ToolRegistry.load_from_directory`).

Example: Gmail send tool:
- `/home/zaks/scripts/tools/manifests/gmail__send_email.yaml`
  - `mcp_stdio_command: ["gmail-mcp"]` (binary must exist in PATH for ToolGateway)
  - `secrets_refs` includes `GMAIL_MCP_CREDENTIALS_PATH: env:GMAIL_MCP_CREDENTIALS_PATH`
  - `irreversible: true` and `risk_level: high` (policy metadata)

Safe override pattern:
- prefer env/file references (`secrets_refs: env:...` or `file:...`) and never hardcode secret values in YAML.

### 2.9 Action capability manifests (per-action metadata)

Action capability manifests are YAML files in `/home/zaks/scripts/actions/capabilities/` (loaded by `/home/zaks/scripts/actions/capabilities/registry.py:get_registry`).

Example: Email triage quarantine gate:
- `/home/zaks/scripts/actions/capabilities/email_triage.review_email.v1.yaml`
  - `action_type: EMAIL_TRIAGE.REVIEW_EMAIL`
  - `required_approval: true`
  - `llm_allowed: false`

## 3) Schedulers / Automation (non-AI but affects operations)

Cron automation file (system-level):
- `/etc/cron.d/dataroom-automation`
  - SharePoint sync every 15 minutes (`/home/zaks/scripts/run_sharepoint_sync.sh`)
  - RAG index every 30 minutes (`/home/zaks/scripts/run_rag_index.sh`)
  - Deferred actions hourly (`/home/zaks/scripts/process_deferred_actions.py`)

These jobs can affect perceived system behavior (freshness of DataRoom/RAG) but are separate from the Kinetic Action runner.
