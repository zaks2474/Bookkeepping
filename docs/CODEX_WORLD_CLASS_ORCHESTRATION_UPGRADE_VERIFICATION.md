# CODEX — World-Class Orchestration Upgrade (Verification)

Date: 2026-01-08

This file captures **reproducible verification** for:
- Temporal orchestration cutover tooling
- LangGraph triage backend (feature-flagged)
- Optional n8n peripheral webhooks

## Phase 0 — Baseline

- Baseline script: `/home/zaks/scripts/codex_baseline_check.py`
- Baseline report: `/home/zaks/bookkeeping/docs/CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md`

Run:
- `python3 /home/zaks/scripts/codex_baseline_check.py > /home/zaks/bookkeeping/docs/CODEX_TRIAGE_RUNTIME_BASELINE_REPORT.md`
- `bash /home/zaks/scripts/run_unit_tests.sh`
- `cd /home/zaks/bookkeeping && make triage-test`
- `bash /home/zaks/scripts/test_quarantine_e2e.sh`

## Phase 1 — Temporal

Start stack:
- `cd /home/zaks/bookkeeping && make temporal-up`
- Temporal UI: `http://localhost:8233`

Install deps (venv):
- `cd /home/zaks/bookkeeping && make orchestration-deps`

Start worker (foreground, dedicated terminal):
- `cd /home/zaks/bookkeeping && make temporal-worker`

Manual run (no schedules):
- `cd /home/zaks/bookkeeping && make temporal-run-once`
- Logs:
  - `/home/zaks/logs/temporal_worker/email_triage_*.log`
  - `/home/zaks/logs/temporal_worker/deal_controller_*.log`

Create schedules (paused-on-create):
- `cd /home/zaks/bookkeeping && make temporal-schedules`
- `cd /home/zaks/bookkeeping && make temporal-status`

Cutover invariant check (no dual scheduling):
- `cd /home/zaks/bookkeeping && make orchestration-audit`

Cutover completion:
- Systemd timers `zakops-email-triage.timer` and `zakops-deal-lifecycle-controller.timer` are now disabled
- Temporal schedules are unpaused and running hourly (`make temporal-schedules-enable`)
## Phase 2 — LangGraph triage backend (feature-flagged)

Backend selector (default remains `llm_triage`):
- `EMAIL_TRIAGE_LLM_BACKEND=langgraph`

Safety:
- LangGraph backend hard-blocks non-local `EMAIL_TRIAGE_LLM_BASE_URL` to prevent cloud calls.

Tests:
- `cd /home/zaks/bookkeeping && make triage-test`

Enable for a single dry run:
- `sudo -u zaks bash -lc 'export EMAIL_TRIAGE_LLM_BACKEND=langgraph; cd /home/zaks/bookkeeping/scripts && python3 -m email_triage_agent.run_once --dry-run'`

## Phase 3 — n8n (optional)

Start n8n (requires explicit creds env vars):
- `export N8N_BASIC_AUTH_USER=...`
- `export N8N_BASIC_AUTH_PASSWORD=...`
- `cd /home/zaks/bookkeeping && make n8n-up`
- n8n UI: `http://localhost:5678`

Starter workflow exports:
- `/home/zaks/bookkeeping/docs/n8n_workflows/quarantine_webhook_receiver.json`
- `/home/zaks/bookkeeping/docs/n8n_workflows/materials_webhook_receiver.json`

Webhook emitter (disabled unless set):
- `export ZAKOPS_N8N_WEBHOOK_URL=http://localhost:5678/webhook/zakops/quarantine`
- Events emitted by backend executors (best-effort):
  - `quarantine.approved`
  - `quarantine.rejected`
  - `materials.auth_required_links_detected`
