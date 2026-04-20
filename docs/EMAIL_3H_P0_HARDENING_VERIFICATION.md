# EMAIL 3H — P0 Hardening Verification (Local Qwen + Full Thread + Sender Backfill)

Generated: 2026-01-11

## What This Upgrade Adds

- **Deterministic-first prefilter (hard vetoes):** newsletters/transactional/spam do not enter Quarantine unless there is strong deal evidence.
- **LLM deep understanding (local-only):** Qwen (vLLM on `http://localhost:8000/v1`) reads the **entire Gmail thread** in `EMAIL_TRIAGE_LLM_MODE=full` and produces strict JSON triage outputs.
- **Post-approval “sender history backfill”:** after an `EMAIL_TRIAGE.REVIEW_EMAIL` is approved and executed, a new follow-on action scans historical emails from the same sender and:
  - **auto-appends** confident “same deal” messages via `DEAL.APPEND_EMAIL_MATERIALS`
  - **creates new Quarantine review items** for “different/uncertain” messages (approval-gated `EMAIL_TRIAGE.REVIEW_EMAIL`)
- **Token-safe stored bodies:** `email_body.txt` artifacts in Quarantine/backfill are written with URL query/fragment stripped (prevents access tokens from being persisted into filesystem artifacts that may later be indexed).
- **Observability:** structured JSONL logs for triage and backfill, plus a safe run header on each triage run.

## Key Files Changed / Added

- Triage logging + safe run header: `bookkeeping/scripts/email_triage_agent/run_once.py`
- Email 3H v1 triage contract (schema + markdown renderer): `bookkeeping/scripts/email_triage_agent/ma_triage_v1.py`
- Local vLLM triage callers (v1 single/thread + JSON repair): `bookkeeping/scripts/email_triage_agent/llm_triage.py`
- Backfill capability + executor:
  - `scripts/actions/capabilities/deal.backfill_sender_history.v1.yaml`
  - `scripts/actions/executors/deal_backfill_sender_history.py`
- Gmail thread fetch helper (read-only, no token writes): `scripts/integrations/gmail_thread_fetch.py`
- ToolGateway: attachment download tool manifest: `scripts/tools/manifests/gmail__download_attachment.yaml`
- Review-email approval chain now emits backfill action: `scripts/actions/executors/email_triage_review_email.py`
- Diagnostics reads triage stats from fallback path if needed: `scripts/deal_lifecycle_api.py`

## Log Outputs (No Raw Bodies)

- Triage run + per-message decisions:
  - `DataRoom/.deal-registry/logs/email_triage_3h.jsonl`
- Sender-history backfill runs + per-message routing:
  - `DataRoom/.deal-registry/logs/email_backfill.jsonl`

## Systemd / Runtime Wiring (Required for Backfill)

Backfill uses ToolGateway Gmail tools: `gmail__search_emails`, `gmail__read_email`, `gmail__download_attachment`.

- Updated allowlist in:
  - template: `bookkeeping/configs/systemd/kinetic-actions-runner.service`
  - installed unit: `/etc/systemd/system/kinetic-actions-runner.service`
- Reloaded + restarted:
  - `sudo systemctl daemon-reload`
  - `sudo systemctl restart kinetic-actions-runner.service`
  - `sudo systemctl restart zakops-api-8090.service` (to pick up diagnostics fallback)

## Verification Commands Run (Proof)

- Backend unit tests: `bash /home/zaks/scripts/run_unit_tests.sh` → `OK`
- Email triage unit tests: `cd /home/zaks/bookkeeping && make triage-test` → `OK`

## Operator Validation Checklist (Manual)

1) Confirm triage run header prints local vLLM settings (journal or stdout):
   - Look for: `email_triage_config llm_mode=... llm_base_url=... llm_model=...`

2) Confirm triage logs are being appended:
   - `tail -n 5 /home/zaks/DataRoom/.deal-registry/logs/email_triage_3h.jsonl`

3) Approve a Quarantine item (existing flow) and confirm follow-on actions include backfill:
   - Find the executed `EMAIL_TRIAGE.REVIEW_EMAIL` action, then check follow-ons:
   - `curl -s 'http://localhost:8090/api/actions?deal_id=DEAL-YYYY-NNN&limit=50' | jq '.actions[].type'`
   - Expect to see: `DEAL.BACKFILL_SENDER_HISTORY` + `DEAL.APPEND_EMAIL_MATERIALS`

4) Confirm backfill logs append and create either:
   - auto-append actions (`DEAL.APPEND_EMAIL_MATERIALS`), and/or
   - new pending Quarantine review actions (`EMAIL_TRIAGE.REVIEW_EMAIL`)

## Eval (Existing)

- Operator-feedback metrics report:
  - `cd /home/zaks/bookkeeping && make triage-eval`
  - Output: `bookkeeping/docs/EMAIL_TRIAGE_EVAL_REPORT.md`

## Eval (Optional Dataset Harness)

This exports **full-thread** samples for local experimentation. Samples are gitignored by default.

- Export recent approve/reject threads:
  - `cd /home/zaks/bookkeeping/scripts && python3 -m email_triage_agent.eval_3h_hardening export --limit 20`
- Score deterministic-only baseline:
  - `cd /home/zaks/bookkeeping/scripts && python3 -m email_triage_agent.eval_3h_hardening score`
- Score deterministic vs local vLLM full-thread (slow):
  - `cd /home/zaks/bookkeeping/scripts && python3 -m email_triage_agent.eval_3h_hardening score --with-llm`

- Write a Markdown report (no raw bodies):
  - `cd /home/zaks/bookkeeping && make triage-eval-3h`
  - Output: `bookkeeping/docs/EMAIL_3H_EVAL_REPORT.md`
