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
  - `zakops-api` (port 8080:8080, env from `.env.langsmith.example`, networks: ai-network, rag-backend, mounts `./src`, `./logs`; agent mode: default SystemOps, optional orchestrator via `ZAKOPS_AGENT_MODE=orchestrator` with router `ZAKOPS_ORCHESTRATOR_ROUTER=rules|llm`; DFP endpoints: `/api/quarantine/health`, `/api/dashboard/stats`, `/api/metrics/classification`; Deal Dashboard: `http://localhost:8080/dashboard`; DFP mounts enabled via `Zaks-llm/docker-compose.dfp.yml`)
  - `rag-rest-api` (port 8052:8080, connects to external `rag-db`, uses host.docker.internal for embeddings)
  - `desktop-commander` (port 3001:3000, volume `./logs/mcp`, bind mounts repo)
  - `zakops-mcp` (port 3002:3000, volume `./logs/zakops-mcp`, bind mounts repo, tool restrictions via env)
  - `google-workspace-mcp` (port 8010:8000, volume `gws-mcp-creds`, env file for OAuth secrets)
  - `mcp-browser-use` (port 8020:8000, volume `mcp-browser-use-data`, GPU)
  - `linkedin-mcp` (port 8030:8000, needs `LINKEDIN_COOKIE` env, logs at `./logs/linkedin-mcp`)
- Logs: `docker compose logs --tail=200` (or `docker logs <container>`)

## Docker Services (google_workspace_mcp_tmp)
- Path: `/home/zaks/google_workspace_mcp_tmp`
- Start/stop: `docker compose up -d` (fill details if used)
- Notes: repo-specific MCP; document env files/volumes when active

## DataRoom Intelligence Platform
- Purpose: AI-powered deal origination and knowledge management system
- Components:
  - **DataRoom** (`/home/zaks/DataRoom`): Structured deal pipeline storage
  - **RAG REST API** (port 8052): Vector search over DataRoom content
  - **SharePoint Sync**: Cloud backup to ZakOpsDataRoom site
  - **DFP Quarantine + Views**: `DataRoom/_quarantine/`, `DataRoom/_dashboard/`, `DataRoom/_views/` (served/observed via `zakops-api:8080`)
- Scripts (`/home/zaks/scripts`):
  - `index_dataroom_to_rag.py` - Index files to RAG (hash-based incremental)
  - `query_dataroom.py` - CLI for RAG queries
  - `score_deal.py` - AI-powered deal scoring against buy box
  - `compare_deals.py` - Side-by-side deal comparison
  - `dataroom_dashboard.sh` - System status dashboard
  - `backup_dataroom.sh` - Daily backup script
  - `export_openwebui_chats.py` - Export AI sessions to DataRoom
- Cron:
  - Root crontab (`sudo crontab -l`):
    - Snapshots: `50 */5 * * * /home/zaks/bookkeeping/capture.sh ...`
    - OpenWebUI DB backups: `20 */2 * * * /home/zaks/bookkeeping/scripts/openwebui_sync.sh ...`
    - Email intake: hourly 06:00–21:59 CT; off-hours every 4 hours (22:05 and 02:05)
  - `/etc/cron.d/dataroom-automation`:
    - SharePoint sync: every 15 minutes (wrapper `run_sharepoint_sync.sh`)
    - RAG indexing: every 30 minutes (wrapper `run_rag_index.sh`)
    - OpenWebUI export: daily 02:00 (writes to `DataRoom/06-KNOWLEDGE-BASE/AI-Sessions/OpenWebUI/`)
    - DataRoom backup: daily 03:00
- Logs:
  - Workflow logs: `/home/zaks/logs/` (`sharepoint_sync_YYYYMMDD.log`, `rag_index_YYYYMMDD.log`, `email_sync_YYYYMMDD.log`, `openwebui_export.log`)
  - Ops logs: `/home/zaks/bookkeeping/logs/` (`capture.log`, `cron.log`, `openwebui-sync.log`)
  - Run ledger: `/home/zaks/logs/run-ledger.jsonl` (append-only; safe metadata only)
- Config: Hash cache at `/home/zaks/.cache/rag_index_hashes.json`
- Notes: RAG uses Ollama embeddings (bge-m3); requires `OLLAMA_HOST=0.0.0.0` in systemd

## Email-to-DataRoom Automation
- Purpose: Automated email sync for acquisition deal flow - monitors Gmail for broker emails and keywords, downloads documents, organizes in DataRoom
- Script: `/home/zaks/scripts/sync_acquisition_emails.py` (IMAP-based, standalone)
- Features:
  - IMAP Gmail client with app password authentication
  - Broker email monitoring (22 contacts from BROKER-TRACKER.csv)
  - Keyword scanning (CIM, teaser, NDA, listing, etc.)
  - Attachment downloads (PDF, Word, Excel)
  - PDF/Office text extraction for RAG indexing (PyMuPDF, python-docx, openpyxl)
  - OCR for scanned PDFs (ocrmypdf + tesseract) and best-effort table extraction to CSV (pdfplumber)
  - Public link following and document download
  - Auto-create deal folders in `00-PIPELINE/Inbound/`
  - Per-email JSON manifests and intake logs
- Cron: business hours hourly (06:00–21:59 CT) and every 4h off-hours (see root `crontab -l`); SharePoint sync is handled separately via `/etc/cron.d/dataroom-automation`
- Credentials: `/home/zaks/.config/email_sync.env` (Gmail app password)
- Cache: `/home/zaks/.cache/email_sync_processed.json` (deduplication)
- Lock: `/home/zaks/.cache/email_sync.lock` (prevents overlapping cron runs)
- Logs: `/home/zaks/logs/email_sync_YYYYMMDD.log`, `/home/zaks/logs/email_sync_report_YYYYMMDD-HHMMSS.json`
- CLI options: `--dry-run`, `--force`, `--hours N`, `--verbose`, `--setup`, `--show-query`, `--zakops-analyze`, `--no-zakops-analyze`, `--zakops-max`
- Derived OCR/table outputs:
  - OCR PDF: `{deal_folder}/{subfolder}/_ocr/<filename>_OCR.pdf` (when OCR runs)
  - Table CSVs: `{deal_folder}/{subfolder}/_tables/<filename>_p###_t##.csv` (best-effort; default runs when OCR runs)
  - The primary `{filename}.txt` extraction includes table CSV content (bounded by `EMAIL_SYNC_MAX_TABLE_CHARS_IN_TXT`, default 100000)
- Env toggles (optional):
  - `EMAIL_SYNC_ENABLE_OCR=1|0` (default 1)
  - `EMAIL_SYNC_OCR_LANG=eng` (tesseract language, default eng)
  - `EMAIL_SYNC_OCR_TIMEOUT_SECONDS=300`
  - `EMAIL_SYNC_PDF_EXTRACT_TABLES_ALWAYS=1` (extract tables even if OCR not needed)
  - `EMAIL_SYNC_PDF_TABLE_MAX_PAGES=60`, `EMAIL_SYNC_PDF_TABLE_MAX_TABLES=80`
- Documentation: `/home/zaks/Email-to-DataRoom-implimentation/IMPLEMENTATION-PLAN.md`

## ZakOps Prime (Email Sync Stage B Analyzer)
- Purpose: Agentic intelligence layer for Email-to-DataRoom (deal_profile extraction, buy-box scoring, risks, next actions)
- Script: `/home/zaks/scripts/zakops_analyzer.py`
- Inputs: `*_manifest.json` produced by Email-to-DataRoom (under each deal’s `07-Correspondence/`)
- Outputs (deal folder root):
  - Core: `deal_profile.json`, `SCREENING-SCORE.json`, `DEAL-ANALYSIS.md`, `RISKS.md`, `NEXT-ACTIONS.md`
  - Docs: `DOCUMENT-CLASSIFICATION.json`, `DUPLICATE-CHECK.json`
  - Summaries (if docs present): `02-CIM/CIM_SUMMARY.md`, `03-Financials/FINANCIALS_EXTRACT.md`
  - Proposals: `_PROPOSAL_broker_update.md`, optional `_PATCH_BROKER-TRACKER.json`
  - Drafts (optional, never auto-sent): `_DRAFT_broker_reply.md`, `_DRAFT_call_agenda.md`, `_DRAFT_dd_questions.md`
- Model runtime: vLLM OpenAI-compatible API (default `ZAKOPS_API_URL=http://localhost:8000/v1`)
- Lock: `/home/zaks/.cache/zakops_analyzer.lock`
- Usage:
  - Scan recent manifests: `python3 /home/zaks/scripts/zakops_analyzer.py --scan /home/zaks/DataRoom/00-PIPELINE/Inbound --since-hours 24 --max 10`
  - Analyze a single manifest: `python3 /home/zaks/scripts/zakops_analyzer.py --manifest /path/to/_manifest.json`
  - Run as part of Stage A: `python3 /home/zaks/scripts/sync_acquisition_emails.py --zakops-analyze`
  - Enable drafts: `python3 /home/zaks/scripts/zakops_analyzer.py --drafts --drafts-min-priority HIGH ...`
- Plan: `/home/zaks/plans/zakops-prime-email-sync-integration.md`

## CSV Patch Applier (Deterministic)
- Purpose: Apply `_PATCH_*.json` proposals to CSV trackers deterministically (no LLM)
- Script: `/home/zaks/scripts/apply_csv_patch.py`
- Usage:
  - Dry run: `python3 /home/zaks/scripts/apply_csv_patch.py /path/to/_PATCH_*.json --dry-run`
  - Apply: `python3 /home/zaks/scripts/apply_csv_patch.py /path/to/_PATCH_*.json`

## Email Sync Improvement Proposals (Deterministic)
- Purpose: Generate professional improvement proposals from recent sync reports and doc classifications
- Script: `/home/zaks/scripts/zakops_improvement_proposals.py`
- Output: `/home/zaks/bookkeeping/docs/PROPOSALS/email_sync_improvements_YYYYMMDD.md`
- Usage: `python3 /home/zaks/scripts/zakops_improvement_proposals.py --days 7`

## ZakOps Draft Approval (Safe Outbox)
- Purpose: Convert `_DRAFT_broker_reply.md` into an `.eml` file for manual send (no SMTP, no auto-send)
- Script: `/home/zaks/scripts/zakops_approve_drafts.py`
- Output: `{deal_folder}/07-Correspondence/OUTBOX/*.eml`
- Usage:
  - Dry run: `python3 /home/zaks/scripts/zakops_approve_drafts.py /path/to/deal`
  - Approve: `python3 /home/zaks/scripts/zakops_approve_drafts.py /path/to/deal --approve`

Add more services as needed following this pattern.
