# Runbooks

Short, task-focused instructions. Fill in blanks and add more tasks as needed.

## Restart Claude Code API
1) `sudo systemctl restart claude-code-api`
2) Verify: `curl -fsS http://localhost:8090/health`
3) Check logs: `journalctl -u claude-code-api -n 100`

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
5) Health: `cd /home/zaks/bookkeeping && make health` (checks Claude API 8090, OpenWebUI 3000, vLLM 8000, ZakOps API 8080, RAG REST 8052; compose ps)

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

### Check Chat health (all providers)
1) `curl -s http://localhost:8090/api/chat/llm-health | jq`
2) Look for `status: "healthy"` and `healthy_providers` list
3) If `diagnostics` array present, review issues and `recommendations`

### Verify vLLM model configuration
1) Check running model: `curl -s http://localhost:8000/v1/models | jq '.data[0].id'`
2) Check configured model in chat:
   - `grep VLLM_MODEL /home/zaks/scripts/chat_llm_provider.py | head -1`
   - `grep VLLM_MODEL /home/zaks/scripts/chat_orchestrator.py | head -1`
3) Models must match! If mismatch, set env var:
   - `export VLLM_MODEL="Qwen/Qwen2.5-32B-Instruct-AWQ"` (or actual model name)
   - Or set `DEFAULT_MODEL` env var which is used as fallback

### Environment variables for Chat
```bash
# vLLM configuration (single source of truth)
OPENAI_API_BASE=http://localhost:8000/v1     # Base URL for OpenAI-compatible API
VLLM_MODEL=Qwen/Qwen2.5-32B-Instruct-AWQ     # Model name (must match vLLM)
VLLM_TIMEOUT_MS=120000                        # Timeout (2 min)

# Cloud LLM (Gemini) - disabled by default
ALLOW_CLOUD_DEFAULT=false                     # Set true to enable Gemini
GEMINI_API_KEY=...                           # Or use ~/.gemini_api file
GEMINI_DAILY_BUDGET=5.0                      # USD per day
GEMINI_RPM_LIMIT=60                          # Requests per minute

# Feature flags
CHAT_CACHE_ENABLED=true                      # Evidence caching
CHAT_DETERMINISTIC_EXTENDED=true             # Extended pattern matching
```

### Restart Chat after config changes
1) `sudo systemctl restart claude-code-api`
2) Verify: `curl -s http://localhost:8090/api/chat/llm-health | jq '.status'`

### Test deterministic queries (no LLM needed)
1) Deal counts: `curl -s -X POST http://localhost:8090/api/chat/complete -H 'Content-Type: application/json' -d '{"query":"how many deals","scope":{"type":"global"}}' | jq '.model_used, .content'`
2) Actions due: Same with query `"actions due today"`
3) Should show `model_used: "direct-api"`

### Test LLM queries
1) `curl -s -X POST http://localhost:8090/api/chat/complete -H 'Content-Type: application/json' -d '{"query":"analyze the risk profile","scope":{"type":"global"}}' | jq '.model_used, .content[:100]'`
2) Should show `model_used: "vllm"` or similar
3) If shows `model_used: "degraded"`, check health endpoint for errors

### Clear chat cache
1) Cache stats: `curl -s http://localhost:8090/api/chat/llm-health | jq '.cache'`
2) Cache is in-memory, restart API to clear:
   - `sudo systemctl restart claude-code-api`

### Troubleshoot "All providers failed"
1) Check health: `curl -s http://localhost:8090/api/chat/llm-health | jq '.diagnostics, .recommendations'`
2) Common issues:
   - Model mismatch: Configured model doesn't exist in vLLM
   - vLLM not running: `docker ps | grep vllm`
   - Port mismatch: Check `OPENAI_API_BASE` vs actual vLLM port
3) Test vLLM directly:
   - `curl -s http://localhost:8000/v1/models | jq '.data[].id'`
   - Should return model name

### Run Chat smoke tests
1) `cd /home/zaks/zakops-dashboard && ./smoke-test.sh`
2) Checks: pages, API proxy, chat endpoints, deterministic queries, SSE progress, LLM path

### View Chat performance benchmarks
1) `cd /home/zaks/scripts && python3 chat_benchmark.py run`
2) Or via Makefile: `cd /home/zaks/zakops-dashboard && make perf`
