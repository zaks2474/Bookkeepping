# Onboarding

Quick orientation for new operators.

## Prereqs
- User in `docker` group (or use `sudo` for docker).
- bash available (`capture.sh` auto-switches to bash if invoked differently).
- Access to relevant repos/services (OpenWebUI, Claude CLI).

## Key locations
- Bookkeeping: `/home/zaks/bookkeeping`
- **Change Log**: `/home/zaks/bookkeeping/CHANGES.md` (record ALL environment changes here)
- Snapshots: `/home/zaks/bookkeeping/snapshots`
- Logs: `/home/zaks/bookkeeping/logs` (`capture.log`, `cron.log`)
- Config copies: `/home/zaks/bookkeeping/configs`
- Docs: `/home/zaks/bookkeeping/docs`

## Common commands
- Run snapshot: `cd /home/zaks/bookkeeping && make snapshot`
- Tail capture log: `make logs`
- Health checks: `make health` (checks Backend API 8091, Agent API 8095, OpenWebUI 3000, vLLM 8000, RAG REST 8052 via `/rag/stats`, compose ps; edit `scripts/health.sh` as services change)
- DataRoom dashboard: `/home/zaks/scripts/dataroom_dashboard.sh`
- Run SharePoint sync now: `bash /home/zaks/scripts/run_sharepoint_sync.sh`
- Run RAG index now: `bash /home/zaks/scripts/run_rag_index.sh`
- Cron schedules: `crontab -l` (bookkeeping) and `/etc/cron.d/dataroom-automation` (DataRoom SharePoint+RAG)

## Services (summary)
- Dashboard: http://localhost:3003 (Next.js, bare process)
- Backend API: http://localhost:8091 (FastAPI, Docker `zakops-backend-1`)
- Agent API: http://localhost:8095 (LangGraph + vLLM)
- OpenWebUI: http://localhost:3000
- RAG REST: http://localhost:8052
- MCP Server: port 9100 (`/home/zaks/zakops-backend/mcp_server/`)
- vLLM: http://localhost:8000 (Qwen2.5-32B-Instruct-AWQ)
- PostgreSQL: localhost:5432 (DBs: zakops, zakops_agent, crawlrag)
- **Port 8090**: DECOMMISSIONED — do not use
- Docker: `docker ps`, see `snapshots/docker-*.txt` for ports/networks
- Post-move checklist: `docs/POST-MOVE-CHECKLIST.md`

## Notes on secrets
- Secrets/keys/.env are excluded by design. Keep them outside git and load via env files or systemd `EnvironmentFile`.
- Treat as secrets (never commit/sync): `/home/zaks/Zaks-llm/sharepoint-mcp-server/config.json`, OpenWebUI `webui.db`, `/home/zaks/.git-access-tokens`.
- LangSmith tracing must be enabled in safe mode only (inputs/outputs hidden). See `docs/LANGSMITH-SAFE-TRACING.md`.

## Next steps
- Read `docs/SERVICE-CATALOG.md` and `docs/RUNBOOKS.md`.
- Update catalog entries with real start/stop commands, data paths, log paths.
- Add health checks in `scripts/health.sh` for each critical service.

## DataRoom automation (SharePoint + RAG)
- Schedule: `/etc/cron.d/dataroom-automation` (SharePoint sync every 15 min, RAG index every 30 min)
- Wrappers: `/home/zaks/scripts/run_sharepoint_sync.sh`, `/home/zaks/scripts/run_rag_index.sh` (locking + daily logs)
- Logs: `/home/zaks/logs/sharepoint_sync_YYYYMMDD.log`, `/home/zaks/logs/rag_index_YYYYMMDD.log`
- RAG health endpoint: `http://localhost:8052/rag/stats`
- OpenWebUI → SharePoint/RAG: export chats to `DataRoom/06-KNOWLEDGE-BASE/AI-Sessions/OpenWebUI/` only; do not sync/index OpenWebUI runtime (`webui.db`, `vector_db/`, `cache/`)

## Operator changelog

> **IMPORTANT**: The authoritative change log is `/home/zaks/bookkeeping/CHANGES.md`. All environment changes MUST be recorded there. This section contains a summary of recent changes for quick reference.

### 2025-12-21
- Updated cron template and installed schedule: `/home/zaks/scripts/cron/dataroom-automation.cron` → `/etc/cron.d/dataroom-automation`
- Added wrappers: `/home/zaks/scripts/run_sharepoint_sync.sh`, `/home/zaks/scripts/run_rag_index.sh`
- Fixed ownership so `zaks` cron jobs can write caches/logs: `/home/zaks/.cache/rag_index_hashes.json`, `/home/zaks/.cache/sharepoint_sync_hashes.json`, and the scheduled scripts
- Updated SharePoint sync defaults to include OpenWebUI exports and preserve folder paths: `/home/zaks/scripts/sync_sharepoint.py`
- Updated dashboard health checks (RAG `/rag/stats`, actionable permission check): `/home/zaks/scripts/dataroom_dashboard.sh`
- Improved SharePoint v2 script config/credential fallback (optional path): `/home/zaks/Zaks-llm/scripts/sharepoint_sync_v2.py`
- Updated implementation plan to match the new schedule/wrappers and OpenWebUI export safety notes: `/home/zaks/DataRoom-rescructure-codex`

### 2025-12-24
- Replaced OpenWebUI volume rsync with DB-only backups (keeps DataRoom clean): `/home/zaks/bookkeeping/scripts/openwebui_sync.sh`
- Removed `DataRoom/08-ARCHIVE/openwebui-chats` runtime dump and backed up all `webui.db` snapshots: `/home/zaks/scripts/cleanup_openwebui_archive.sh`
- Enabled daily OpenWebUI export + daily DataRoom backup in `/etc/cron.d/dataroom-automation`
- Fixed dashboard log parsing to only evaluate the most recent run: `/home/zaks/scripts/dataroom_dashboard.sh`
- Moved Email-to-DataRoom cron to run as `zaks` (prevents root-owned DataRoom files): `/home/zaks/bookkeeping/configs/cron/root.crontab.after-20251215-045446`

### 2025-12-25
- Added append-only run ledger writer: `/home/zaks/bookkeeping/scripts/run_ledger.py` (default ledger: `/home/zaks/logs/run-ledger.jsonl`)
- Emitted run-ledger records from core automations: `/home/zaks/bookkeeping/capture.sh`, `/home/zaks/bookkeeping/scripts/openwebui_sync.sh`, `/home/zaks/scripts/run_rag_index.sh`, `/home/zaks/scripts/run_sharepoint_sync.sh`, `/home/zaks/scripts/sync_acquisition_emails.py`
- Added best-effort secret scanning to prevent accidental RAG indexing / SharePoint exfil: `/home/zaks/scripts/zakops_secret_scan.py`, `/home/zaks/scripts/index_dataroom_to_rag.py`, `/home/zaks/scripts/sync_sharepoint.py`
- Ensured mixed root/zaks jobs can append to the run ledger (auto-fix owner/mode when written by root): `/home/zaks/bookkeeping/scripts/run_ledger.py`
- Added `make preflight` secret scan for this repo: `/home/zaks/bookkeeping/Makefile`
- Redacted LinkedIn cookie values from docs (placeholders only): `/home/zaks/bookkeeping/docs/LINKEDIN-MCP-IMPLEMENTATION.md`

### 2025-12-26
- Implemented World-Class Orchestration Patterns for year-spanning deal lifecycle:
  - Event Sourcing: `/home/zaks/scripts/deal_events.py` (append-only event log per deal)
  - State Machine: `/home/zaks/scripts/deal_state_machine.py` (enforced stage transitions, approval gates)
  - Deferred Actions: `/home/zaks/scripts/deferred_actions.py` (schedule future actions, recurring tasks)
  - Durable Checkpointing: `/home/zaks/scripts/durable_checkpoint.py` (crash recovery for long operations)
  - AI Advisory: `/home/zaks/scripts/deal_ai_advisor.py` (stage-appropriate AI recommendations)
  - Deferred Actions Processor: `/home/zaks/scripts/process_deferred_actions.py` (cron job for due actions)
  - Event-Enabled Registry: `/home/zaks/scripts/deal_registry_events.py` (emits events on mutations)
- Created directory structure: `/home/zaks/DataRoom/.deal-registry/events/`, `/home/zaks/DataRoom/.deal-registry/checkpoints/`
- Deal stages now support full M&A lifecycle: INBOUND → SCREENING → QUALIFIED → LOI → DILIGENCE → CLOSING → INTEGRATION → OPERATIONS → GROWTH → EXIT_PLANNING → CLOSED_WON/CLOSED_LOST
- CLI tools for all patterns: `python3 /home/zaks/scripts/deal_events.py list`, `deal_state_machine.py stages`, `deferred_actions.py stats`, `durable_checkpoint.py stats`
- Added DFP CRUD endpoints to ZakOps API: `/api/deals`, `/api/deals/{id}/events`, `/api/quarantine`, `/api/deferred-actions`, `/api/checkpoints`
- Updated dashboard UI: `/home/zaks/DataRoom/_dashboard/index.html` (deal pipeline, deferred actions, checkpoints)
- Added cron jobs: hourly deferred actions processor, 15-min email sync in `/etc/cron.d/dataroom-automation`
- LangSmith safe tracing: `/home/zaks/scripts/enable_langsmith_tracing.sh`, `/home/zaks/Zaks-llm/docker-compose.langsmith.yml`
- Expanded golden datasets to 52 examples each (208 total) in `/home/zaks/DataRoom/06-KNOWLEDGE-BASE/EVALS/`

### 2025-12-31
- **Run Ledger & Secret Scanner Verification**: Verified Phase 0/1 implementation from lab environment analysis
  - **Verified**: `run_ledger.py` (append-only JSONL, file locking, correlation IDs), `zakops_secret_scan.py` (8 secret patterns)
  - **Verified integrations**: capture.sh, openwebui_sync.sh, run_rag_index.sh, run_sharepoint_sync.sh, sync_acquisition_emails.py
  - **Fix applied**: Made `run_ledger.py` executable (`chmod +x`) - was missing, causing on_exit traps to skip ledger writes
  - **Test results**: Run ledger at `/home/zaks/logs/run-ledger.jsonl` now capturing entries; secret scanner detects all patterns
- **World-Class Orchestration Plan Unification**: Merged execution plans into comprehensive unified document
  - Merged: existing `WORLD-CLASS-ORCHESTRATION-PLAN.md` + operator-provided `zakops_unified_execution_plan.md`
  - Added: 5-plane architecture model, LLM Strategy (provider abstraction for vLLM + Gemini), policy-as-code YAML, Phase 0.5 Gemini adapter
  - Added: idempotency requirements, Phase 6 evaluation, explicit execution order (0 → 0.5 → 1 → 2 → 3 → 5 → 4 → 6)
  - Operator enhancements: projection rebuild/backfill, email dedupe, feature flags, retention/backup, API security
  - Final document: `/home/zaks/bookkeeping/docs/WORLD-CLASS-ORCHESTRATION-PLAN.md` (1,140+ lines, 13 sections)
- **Global Search + Scroll Model Remediation**: Fixed critical UX issues
  - **Global Search (⌘K)**: Created Command Palette (`src/components/global-search.tsx`) with deal search, keyboard shortcut, 30s cache, navigation
  - **Scroll Model Fix**: Fixed SidebarProvider (`h-screen overflow-hidden`) and SidebarInset (`overflow-hidden`); added page-level scroll containers to all 6 pages
  - **Template Cleanup**: Removed 8 unused routes with Clerk deps (billing, kanban, product, etc.) and 5 feature dirs
  - **Testing**: 40 click-sweep tests pass including new scroll container verification (Section 8)
  - **Docs**: Created `SCROLL-MODEL.md`, updated `INTERACTION-MATRIX.md` (all 10 issues marked fixed)
- **Email Sync Smart Provenance Checking**: Enhanced Downloads folder processing with email provenance verification
  - Disabled auto-creation of deal folders from Downloads documents (was creating folders for personal docs)
  - Added `search_by_terms()` to IMAPGmailClient for provenance lookup with `skip_words` filter (no false positives)
  - Added document content extraction (PDF/Word → company names, listing IDs, broker names)
  - Added `_search_email_provenance()`, `_is_acquisition_related()`, `_create_deal_from_email()` methods
  - New flow: read content → match existing deals → search emails → verify acquisition-related → create or skip
  - Fixed Gmail disconnect timing (moved Downloads scan before IMAP disconnect)
  - Test results: Personal docs skipped (no provenance), business docs with email trail processed correctly
- **ZakOps Prime Integration Plan**: Created `/home/zaks/plans/zakops-prime-email-sync-integration.md`
  - 3-Stage Architecture: Stage A (Deterministic Ingestion), Stage B (Agentic Intelligence), Stage C (Gated Outbound)
  - Per-email `manifest.json` for clean stage handoff
  - Stage B outputs: `deal_profile.json`, `RISKS.md`, `NEXT-ACTIONS.md`, duplicate detection, broker intelligence
  - Model routing: small model for classification, large model for analysis
  - Guardrails: no-overwrite, schema validation, approval gates, never auto-send

### 2026-01-17
- **ZakOps Dashboard Phase 4 UI Implementation**: Created comprehensive Phase 4 UI components
  - **Operator HQ**: `OperatorHQ.tsx`, `QuickStats.tsx`, `PipelineOverview.tsx`, `ActivityFeed.tsx` in `/home/zaks/zakops-dashboard/src/components/operator-hq/`
  - **Onboarding Wizard**: 5-step progressive wizard with `WelcomeStep`, `EmailSetupStep`, `AgentConfigStep`, `PreferencesStep`, `CompleteStep` in `/home/zaks/zakops-dashboard/src/components/onboarding/`
  - **Diligence Components**: `DiligenceChecklist`, `DiligenceProgress`, `DiligenceCategory`, `DiligenceItem`, `useDiligence` hook in `/home/zaks/zakops-dashboard/src/components/diligence/`
  - **Dashboard Components**: Enhanced `ExecutionInbox.tsx`, `TodayNextUpStrip.tsx` in `/home/zaks/zakops-dashboard/src/components/dashboard/`
  - **Approvals**: Created `ApprovalBadge.tsx` with variants and notification dot
  - **Infrastructure**: `use-render-tracking.ts`, `useApprovalFlow.ts`, enhanced `observability.ts`, `agent-client.ts`, `routes.ts`

### 2026-01-18
- **UI Polish Mission - Critical Bug Fixes**: Fixed multiple critical UI issues
  - **HQ Data Fix**: Fixed stats showing 0 - corrected property names to match `PipelineStats` interface (`total_active_deals`, `deals_by_stage`)
  - **Onboarding Layout Fix**: Fixed tiny centered card - changed to standard page layout with `p-4 md:p-6`
  - **GlobalSearch Navigation Fix**: Changed from 404-causing dynamic routes to query params (`?selected=id`)
  - **Missing Layouts**: Created `layout.tsx` for `/hq`, `/onboarding`, `/ui-test` pages with sidebar/header
  - **UI Test Page**: Created comprehensive component verification page
  - Files: `/home/zaks/zakops-dashboard/src/app/hq/page.tsx`, `/home/zaks/zakops-dashboard/src/app/onboarding/page.tsx`, `/home/zaks/zakops-dashboard/src/components/global-search.tsx`

- **Agent Visibility Layer - Unified Architecture**: Implemented comprehensive agent visibility system
  - API endpoint: `/api/agent/activity` with deterministic status rules (`waiting_approval > working > idle`)
  - Data layer: `useAgentActivity` hook as single source of truth with SSE integration and React Query
  - Components: `AgentDrawer` (global Ask Agent), `AgentActivityWidget` (dashboard), `AgentStatusIndicator` (header), `DealAgentPanel` (deal workspace), `AgentDemoStep` (onboarding demo)
  - Page: `/agent/activity` - full history view with tabs, search, stats, and run history
  - Integration: Provider in root layout, indicator in header, widget on dashboard, nav link with robot icon (`g g` shortcut)
  - Files: `/home/zaks/zakops-dashboard/src/app/api/agent/activity/`, `/home/zaks/zakops-dashboard/src/hooks/useAgentActivity.ts`, `/home/zaks/zakops-dashboard/src/components/agent/AgentDrawer.tsx`, `/home/zaks/zakops-dashboard/src/components/dashboard/AgentActivityWidget.tsx`, `/home/zaks/zakops-dashboard/src/components/layout/AgentStatusIndicator.tsx`, `/home/zaks/zakops-dashboard/src/components/deal-workspace/DealAgentPanel.tsx`, `/home/zaks/zakops-dashboard/src/components/onboarding/steps/AgentDemoStep.tsx`

### 2025-12-27
- **ZakOps Chat System (Initial Implementation)**: Built RAG-grounded conversational interface for deal lifecycle queries:
  - Backend scripts (`/home/zaks/scripts/`):
    - `chat_orchestrator.py` - Main orchestrator with SSE streaming, deterministic routing, evidence-grounded LLM
    - `chat_evidence_builder.py` - Evidence gathering from RAG, registry, events, case files, actions
  - Frontend (`/home/zaks/zakops-dashboard/src/app/chat/page.tsx`): Chat UI with scope selector, evidence display, streaming
  - API endpoints: `POST /api/chat/complete`, `GET /api/chat/llm-health`
  - Features: Global/deal-scoped queries, RAG integration, deterministic routing for simple queries
- **Chat UI Fixes: Progress Visibility + Session Persistence + Freeze Resolution**:
  - Backend emits granular SSE progress events with `step`, `substep`, `phase`, `total_phases`
  - Frontend 50ms token batching prevents UI freeze during streaming
  - localStorage persistence for messages, session, scope - survives page refresh
  - Debug panel shows session info, provider, timing breakdown with bar chart, cache status
  - Smoke tests updated: Section 7 verifies progress events (30 tests pass)
  - Performance: Deterministic ~20ms, LLM ~20-40s
- **Chat Performance Mode v1 + Hybrid Gemini Integration**:
  - New scripts (`/home/zaks/scripts/`):
    - `chat_timing.py` - Timing/tracing infrastructure
    - `chat_cache.py` - TTL-based evidence caching (global 45s, deal 180s)
    - `chat_llm_provider.py` - Provider abstraction (vLLM, Gemini Flash/Pro)
    - `chat_budget.py` - Gemini budget/rate controls ($5/day, 60 RPM)
    - `chat_llm_router.py` - Routing policy with fallback chain
    - `chat_benchmark.py` - Performance benchmark harness
  - Modified `chat_orchestrator.py`: 7 deterministic patterns (deal counts, stage lookup, broker filter, stuck deals, actions due, what changed today), timing traces, evidence caching, provider routing, cloud safety gate
  - Modified `chat_evidence_builder.py`: Retrieval caps (top_k=6, max_snippet=600 chars, deduplication)
  - Extended `/api/chat/llm-health` endpoint with multi-provider health, budget, cache stats
  - Frontend updates (`/home/zaks/zakops-dashboard/src/app/chat/page.tsx`): Progress indicator (4-step dots), Debug panel (timing breakdown, provider info, cache status)
  - Testing: Extended `smoke-test.sh` (deterministic tests, provider health tests), new Makefile targets (`make perf`, `make provider-health`, `make budget-status`, `make cache-status`)
  - Configuration: `ALLOW_CLOUD_DEFAULT=false`, `CHAT_CACHE_ENABLED=true`, `CHAT_DETERMINISTIC_EXTENDED=true`
- **Chat vLLM Provider Hardening**:
  - Fixed model name mismatch: Default changed from `Qwen/Qwen2.5-7B-Instruct` to `Qwen/Qwen2.5-32B-Instruct-AWQ`
  - Centralized config: `OPENAI_API_BASE` is now single source of truth for vLLM endpoint
  - Health check validates configured model exists in vLLM's model list
  - Graceful degradation: Returns user-friendly message instead of "All providers failed" error
  - New deterministic pattern: "What's this deal about?" returns comprehensive deal summary
  - Health endpoint now includes `diagnostics`, `recommendations`, `primary_provider`
  - Added Section 9 smoke tests for non-deterministic chat and graceful degradation
  - Runbook: Added "ZakOps Chat / LLM Operations" section (12 procedures)

## World-Class Orchestration Patterns

Deal lifecycle patterns for year-spanning workflows:

| Pattern | Script | Purpose | CLI Example |
|---------|--------|---------|-------------|
| Event Sourcing | `deal_events.py` | Immutable audit trail, state replay | `python3 deal_events.py list` |
| State Machine | `deal_state_machine.py` | Enforced transitions, approvals | `python3 deal_state_machine.py stages` |
| Deferred Actions | `deferred_actions.py` | Future tasks, recurring actions | `python3 deferred_actions.py stats` |
| Checkpointing | `durable_checkpoint.py` | Crash recovery, resume | `python3 durable_checkpoint.py stats` |
| AI Advisory | `deal_ai_advisor.py` | Stage-appropriate AI recommendations | `python3 deal_ai_advisor.py checklist --stage screening` |
| Action Processor | `process_deferred_actions.py` | Execute due actions (cron) | `python3 process_deferred_actions.py --show-pending` |
| Event Registry | `deal_registry_events.py` | Auto-emit events on mutations | Used via `EventEnabledRegistry` class |

Environment variables:
```bash
DEAL_EVENTS_DIR=/home/zaks/DataRoom/.deal-registry/events
DEAL_STATE_MACHINE_ENABLED=true
DEAL_APPROVAL_REQUIRED_STAGES=loi,closing,exit_planning,closed_won
DEFERRED_ACTIONS_PATH=/home/zaks/DataRoom/.deal-registry/deferred_actions.json
CHECKPOINT_DIR=/home/zaks/DataRoom/.deal-registry/checkpoints
AI_ADVISORY_ENABLED=true
AI_ADVISORY_MODEL=Qwen/Qwen2.5-32B-Instruct-AWQ
```

## Deal Lifecycle API Endpoints

Deal Lifecycle API endpoints available at `http://localhost:8091`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/deals` | List deals (filter: `?status=active&stage=screening`) |
| GET | `/api/deals/{id}` | Get single deal |
| GET | `/api/deals/{id}/events` | Get deal event history |
| GET | `/api/quarantine` | List quarantine items |
| GET | `/api/quarantine/{id}` | Get single quarantine item |
| GET | `/api/deferred-actions` | List all deferred actions |
| GET | `/api/deferred-actions/due` | List due actions only |
| GET | `/api/checkpoints` | List checkpoints |
| GET | `/dashboard` | Dashboard UI |

## LangSmith Tracing

Enable safe tracing (inputs/outputs hidden by default):

```bash
# Option 1: Shell script
export LANGCHAIN_API_KEY=your-key
source /home/zaks/scripts/enable_langsmith_tracing.sh

# Option 2: Docker Compose overlay
export LANGCHAIN_API_KEY=your-key
docker compose -f docker-compose.yml -f docker-compose.langsmith.yml up -d zakops-api
```

See `docs/LANGSMITH-SAFE-TRACING.md` for full documentation.
