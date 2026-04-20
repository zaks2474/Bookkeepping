# Runbooks

Short, task-focused instructions. Fill in blanks and add more tasks as needed.

## Restart Claude Code API (DECOMMISSIONED)
> **Port 8090 is decommissioned.** The Claude Code FastAPI wrapper is no longer in use.
> Chat is now handled by the Agent API at port 8095 via the dashboard at port 3003.

## Refresh snapshots manually
1) `cd /home/zaks/bookkeeping`
2) `make snapshot`
3) Review `snapshots/` and `logs/capture.log`

## Ops digest (run ledger)
- Auto: generated once per day after ~08:00 CT by `/home/zaks/scripts/run_sharepoint_sync.sh` if the daily digest file is missing.
1) Manual: `python3 /home/zaks/bookkeeping/scripts/ops_digest.py --since-hours 24`
2) If you do not want the manual run recorded in the run ledger: add `--no-ledger-record`
3) Output path is printed (default: `DataRoom/06-KNOWLEDGE-BASE/ops-daily/YYYY-MM-DD.md`, local date in `America/Chicago`)
4) If runs are missing: confirm `/home/zaks/logs/run-ledger.jsonl` is writable by `zaks`

## Run local evals (sanitized datasets)
1) Run: `python3 /home/zaks/bookkeeping/scripts/eval_runner.py /home/zaks/DataRoom/06-KNOWLEDGE-BASE/EVALS --max-examples 10`
2) Results: `DataRoom/06-KNOWLEDGE-BASE/EVALS/runs/YYYY-MM-DD/*.summary.md`
3) If your environment blocks local HTTP from Python, run the script directly from your normal WSL shell (not from a sandboxed runner).

## Check Docker stack health
1) `docker ps`
2) `docker compose ls` (if compose stacks)
3) Ports: `cat snapshots/docker-ports.txt`
4) Networks: `cat snapshots/docker-networks-detail.txt`
5) Health: `cd /home/zaks/bookkeeping && make health` (checks Backend 8091, Dashboard 3003, Agent 8095, OpenWebUI 3000, vLLM 8000, RAG REST 8052; compose ps)

## Switch ZakOps API to Orchestrator mode (Phase 2)
1) Enable orchestrator (router defaults to rules):
   - `cd /home/zaks/Zaks-llm && docker compose -f docker-compose.yml -f docker-compose.orchestrator.yml up -d --force-recreate --no-deps zakops-api`
2) Roll back to SystemOps-only:
   - `cd /home/zaks/Zaks-llm && docker compose -f docker-compose.yml up -d --force-recreate --no-deps zakops-api`
3) Verify:
   - Logs: `docker logs --tail=120 zakops-api`
   - Health (host): `curl -fsS http://localhost:8080/health`

## DFP quarantine/dashboard health (Phase 2+)
1) Quarantine health: `curl -s http://localhost:8080/api/quarantine/health | jq .`
2) Dashboard stats: `curl -s http://localhost:8080/api/dashboard/stats | jq .`
3) Classification metrics: `curl -s http://localhost:8080/api/metrics/classification | jq .`
4) If endpoints show `status=degraded`, enable DataRoom + run-ledger mounts:
   - `cd /home/zaks/Zaks-llm && docker compose -f docker-compose.yml -f docker-compose.orchestrator.yml -f docker-compose.dfp.yml up -d --force-recreate --no-deps zakops-api`
5) Directory scaffold:
   - `ls -la /home/zaks/DataRoom/_quarantine/`
   - `ls -la /home/zaks/DataRoom/_dashboard/`
   - `ls -la /home/zaks/DataRoom/_views/`

## Add a new service entry to catalog
1) Edit `docs/SERVICE-CATALOG.md`
2) Add name, port, start/stop, config path, data path, logs, notes

## Sync Dashboard Types (Hybrid Guardrail)
1) `cd /home/zaks && make sync-types`
2) Verify: exit 0 means OpenAPI fetch + codegen + format + tsc all passed
3) If codegen fails: check backend is running (`curl -sf http://localhost:8091/health`)
4) If tsc fails: fix type errors in `types/api.ts` (manual refinements may need updating)
5) If OpenAPI spec changed: review `api-types.generated.ts` diff before committing

## Troubleshoot Codegen Pipeline
- **Backend not running:** `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose up -d --no-deps backend`
- **Postgres restart loop:** Use `docker compose up -d --no-deps backend` (skips postgres dependency)
- **Types out of sync:** Run `make sync-types` — codegen takes ~90-120ms
- **Manual type mismatch:** Check `types/api.ts` hybrid types — nested interfaces (DealIdentifiers, CompanyInfo, etc.) may need updating if backend schema changed
- **CI drift gate fails:** Run `make sync-types` locally and commit the updated `api-types.generated.ts`

## Run Full Infrastructure Validation
1) `cd /home/zaks && make validate-all`
2) Runs: infra-check + sync-types + rag-routing + secret scan + enforcement audit
3) All gates must PASS — investigate any failures before proceeding

## After moving networks (IP changed)
1) `cd /home/zaks/bookkeeping && make health`
2) `make snapshot`
3) Update allowlists/firewall/OAuth/webhooks with new public IP if applicable
4) Log the change in `CHANGES.md`
5) See `docs/POST-MOVE-CHECKLIST.md` for full list

## Add/adjust cron automation
1) Edit with `crontab -e`
2) Confirm with `crontab -l`
3) Ensure log path in `bookkeeping/logs/cron.log`

## Add new MCP or tool
1) Document location/config in `docs/SERVICE-CATALOG.md`
2) If code/config is tracked, place non-secret parts under `bookkeeping/configs/` or note paths

## DataRoom Intelligence Platform Operations

### Re-index DataRoom to RAG
1) Preferred: `bash /home/zaks/scripts/run_rag_index.sh` (locking + daily log)
2) Direct (no wrapper): `python3 /home/zaks/scripts/index_dataroom_to_rag.py`
2) Verify: `curl -s http://localhost:8052/rag/stats | jq`
3) Test query: `python3 /home/zaks/scripts/query_dataroom.py "What MSP deals are in the pipeline?"`

### Force full RAG re-index (clear cache)
1) `rm -f /home/zaks/.cache/rag_index_hashes.json`
2) `python3 /home/zaks/scripts/index_dataroom_to_rag.py`
3) Check stats: `curl -s http://localhost:8052/rag/stats | jq`

### Score a deal against buy box
1) `python3 /home/zaks/scripts/score_deal.py "TeamLogic-IT-MSP-2025" --verbose`
2) Save to file: `python3 /home/zaks/scripts/score_deal.py "DealName" -o /tmp/score.json`

### Compare two deals
1) `python3 /home/zaks/scripts/compare_deals.py "Deal1" "Deal2"`

### Check DataRoom status
1) `/home/zaks/scripts/dataroom_dashboard.sh`
2) View logs: `tail -50 /home/zaks/logs/rag_index_$(date +%Y%m%d).log`

### Backup DataRoom
1) `/home/zaks/scripts/backup_dataroom.sh`
2) List backups: `ls -la /home/zaks/backups/dataroom/`

### Export OpenWebUI chats to DataRoom
1) `python3 /home/zaks/scripts/export_openwebui_chats.py`
2) Check output: `ls /home/zaks/DataRoom/06-KNOWLEDGE-BASE/AI-Sessions/OpenWebUI/`

### Fix RAG embedding errors (Ollama connection)
1) Verify Ollama binding: `sudo grep OLLAMA_HOST /etc/systemd/system/ollama.service`
2) If missing, add `Environment="OLLAMA_HOST=0.0.0.0"` under [Service]
3) Reload: `sudo systemctl daemon-reload && sudo systemctl restart ollama`
4) Re-test: `python3 /home/zaks/scripts/index_dataroom_to_rag.py`

## Email-to-DataRoom Automation Operations

### Preview email sync (dry run)
1) `python3 /home/zaks/scripts/sync_acquisition_emails.py --dry-run --verbose`
2) Review output for emails that would be processed

### Run email sync manually
1) `python3 /home/zaks/scripts/sync_acquisition_emails.py --verbose`
2) Check logs: `tail -100 /home/zaks/logs/email_sync_$(date +%Y%m%d).log`
3) Check reports: `ls -la /home/zaks/logs/email_sync_report_*.json`

### OCR + table extraction (scanned PDFs)
1) Verify OCR tools: `ocrmypdf --version && tesseract --version | head -n 2`
2) Output locations (per deal subfolder):
   - OCR PDF: `_ocr/<filename>_OCR.pdf` (when OCR runs)
   - Table CSVs: `_tables/<filename>_p###_t##.csv` (best-effort; default runs when OCR runs)
3) Control via env (optional):
   - Disable OCR: `EMAIL_SYNC_ENABLE_OCR=0`
   - Force table extraction always: `EMAIL_SYNC_PDF_EXTRACT_TABLES_ALWAYS=1`
   - Increase OCR timeout: `EMAIL_SYNC_OCR_TIMEOUT_SECONDS=600`

### Show search criteria
1) `python3 /home/zaks/scripts/sync_acquisition_emails.py --show-query`
2) Shows broker emails, keywords, attachment types monitored

### Backfill emails (longer lookback)
1) `python3 /home/zaks/scripts/sync_acquisition_emails.py --hours 168 --verbose` (1 week)
2) For full history reprocessing: add `--force` flag

### Clear email sync cache (force reprocess)
1) `rm -f /home/zaks/.cache/email_sync_processed.json`
2) `python3 /home/zaks/scripts/sync_acquisition_emails.py --verbose`

### Setup credentials (first time)
1) `python3 /home/zaks/scripts/sync_acquisition_emails.py --setup`
2) Edit `/home/zaks/.config/email_sync.env` with Gmail address
3) Generate App Password at https://myaccount.google.com/apppasswords
4) Add app password to env file
5) Test: `python3 /home/zaks/scripts/sync_acquisition_emails.py --dry-run`

### Check inbox index
1) `cat /home/zaks/DataRoom/00-PIPELINE/Inbound/_INBOX-INDEX.md`
2) Shows all deals created by automation with timestamps

### Troubleshoot authentication failures
1) Verify 2FA is enabled on Gmail account
2) Generate fresh App Password (old ones may be revoked)
3) Check `/home/zaks/.config/email_sync.env` for typos
4) Test: `python3 -c "import imaplib; m=imaplib.IMAP4_SSL('imap.gmail.com'); m.login('your-email', 'app-password')"`

## ZakOps Prime Analyzer (Stage B) Operations

### Analyze recent inbound manifests (recommended)
1) `python3 /home/zaks/scripts/zakops_analyzer.py --scan /home/zaks/DataRoom/00-PIPELINE/Inbound --since-hours 24 --max 10`
2) Confirm outputs created in the deal folder: `deal_profile.json`, `SCREENING-SCORE.json`, `DEAL-ANALYSIS.md`, `RISKS.md`, `NEXT-ACTIONS.md`

### Analyze a single manifest
1) `python3 /home/zaks/scripts/zakops_analyzer.py --manifest /path/to/07-Correspondence/*_manifest.json`

### Run Stage A + Stage B together
1) `python3 /home/zaks/scripts/sync_acquisition_emails.py --zakops-analyze --zakops-max 3 --verbose`

### Generate drafts (approval-gated)
1) `python3 /home/zaks/scripts/zakops_analyzer.py --scan /home/zaks/DataRoom/00-PIPELINE/Inbound --since-hours 24 --max 10 --drafts --drafts-min-priority HIGH`
2) Review `_DRAFT_*.md` files in the deal folder root (never auto-sent)

### Approve a broker reply draft (generate .eml outbox file)
1) Dry run: `python3 /home/zaks/scripts/zakops_approve_drafts.py /path/to/deal`
2) Approve: `python3 /home/zaks/scripts/zakops_approve_drafts.py /path/to/deal --approve`
3) Send: open `{deal_folder}/07-Correspondence/OUTBOX/*.eml` in your email client and send manually

### Apply a broker tracker patch (proposal → deterministic apply)
1) Dry run: `python3 /home/zaks/scripts/apply_csv_patch.py /path/to/_PATCH_BROKER-TRACKER.json --dry-run`
2) Apply: `python3 /home/zaks/scripts/apply_csv_patch.py /path/to/_PATCH_BROKER-TRACKER.json`
3) Validate: open `/home/zaks/DataRoom/03-DEAL-SOURCES/BROKER-TRACKER.csv` and confirm changes look correct

### Generate pipeline improvement proposals
1) `python3 /home/zaks/scripts/zakops_improvement_proposals.py --days 7`
2) Review the generated file under `/home/zaks/bookkeeping/docs/PROPOSALS/`

### Troubleshoot vLLM connectivity
1) Verify vLLM is running/listening on `:8000`
2) Test: `curl -fsS http://localhost:8000/v1/models | head`
3) If port differs, set `ZAKOPS_API_URL=http://localhost:<port>/v1`

## ZakOps Chat / LLM Operations

> **Note:** The old Claude Code FastAPI wrapper on port 8090 is **decommissioned**.
> Chat is now handled by the **Agent API** (port 8095) via the **Dashboard** (port 3003).
> The agent uses Qwen 2.5 32B-Instruct-AWQ via local vLLM with LangGraph tool orchestration.

### Check Agent API health
1) `curl -s http://localhost:8095/health | jq`
2) Check agent chat: open http://localhost:3003/chat in browser

### Verify vLLM model
1) Check running model: `curl -s http://localhost:8000/v1/models | jq '.data[0].id'`
2) vLLM serves Qwen2.5-32B-Instruct-AWQ on port 8000
3) Agent API connects to vLLM internally via Docker network

### Agent Chat timeout
- Dashboard timeout: `AGENT_LOCAL_TIMEOUT` in `apps/dashboard/.env.local` (current: 180000ms = 3 min)
- Agent needs ~108s for tool-using conversations (two LLM round-trips)
- If chat returns "AI agent service is currently unavailable", increase timeout

### Test Chat
1) Send a message via the dashboard at http://localhost:3003/chat
2) Or test agent directly: `curl -s -X POST http://localhost:8095/api/v1/chatbot/chat -H 'Content-Type: application/json' -H 'Authorization: Bearer <token>' -d '{"messages":[{"role":"user","content":"How many deals do we have?"}]}'`

### Troubleshoot Chat failures
1) Check agent logs: `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose logs agent-api --tail=50`
2) Check vLLM: `docker ps | grep vllm` and `curl -s http://localhost:8000/v1/models`
3) Check dashboard logs for timeout errors
4) Common issues:
   - Timeout too short (increase `AGENT_LOCAL_TIMEOUT`)
   - vLLM not running or OOM
   - Agent API container not started

### Run QA smoke tests
1) `cd /home/zaks/zakops-agent-api/apps/backend && bash scripts/qa_smoke.sh`
2) Checks: health endpoints, API responses, golden paths
