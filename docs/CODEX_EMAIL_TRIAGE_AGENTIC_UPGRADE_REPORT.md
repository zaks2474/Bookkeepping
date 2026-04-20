# CODEX — Email Triage Agentic Upgrade (Local Qwen/vLLM)

Date: 2026-01-07  
Goal: Make email triage **local-first + agentic** using **local vLLM (Qwen/Qwen2.5-32B)**, while keeping all safety constraints (no auto-send, no auto-delete, no cloud).

## What Changed

### New files
- `bookkeeping/scripts/email_triage_agent/llm_triage.py`
  - Local OpenAI-compatible client (urllib-based) targeting vLLM.
  - Strict JSON contract parsing + validation.
  - Markdown renderer for Quarantine UX (`triage_summary.md`).
- `bookkeeping/scripts/email_triage_agent/tests/test_llm_triage.py`
  - Unit tests for JSON parsing and assist-mode downgrade behavior.

### Updated files
- `bookkeeping/scripts/email_triage_agent/run_once.py`
  - Loads LLM config once per run (`load_llm_config()`).
  - Calls local vLLM/Qwen (feature-flagged) to produce structured triage results.
  - In `assist` mode: allows **high-confidence downgrade** (prevents false positives entering Quarantine).
  - Writes `triage_summary.json` + `triage_summary.md` into the quarantine folder for deal-signal emails.
  - Adds `confidence` + `triage_summary_path` into the created `EMAIL_TRIAGE.REVIEW_EMAIL` action inputs.

## Feature Flags / Env Vars Added

Read by `bookkeeping/scripts/email_triage_agent/llm_triage.py:load_llm_config`:

- `EMAIL_TRIAGE_LLM_MODE` = `off|assist|full` (default: `assist`)
  - `off`: deterministic-only (previous behavior)
  - `assist`: LLM runs for deterministic `DEAL_SIGNAL` candidates; may **downgrade** to non-deal when confidence ≥ 0.85
  - `full`: LLM can classify all emails; deterministic guardrails prevent denylisted/transactional/spam from becoming `DEAL_SIGNAL`
- `EMAIL_TRIAGE_LLM_BASE_URL` (default: `OPENAI_API_BASE` → else `VLLM_ENDPOINT` → else `http://localhost:8000/v1`)
- `EMAIL_TRIAGE_LLM_MODEL` (default: `VLLM_MODEL` → else `DEFAULT_MODEL` → else `Qwen/Qwen2.5-32B-Instruct-AWQ`)
- `EMAIL_TRIAGE_LLM_TIMEOUT_S` (default: `20`)
- `EMAIL_TRIAGE_LLM_MAX_TOKENS` (default: `900`)
- `EMAIL_TRIAGE_LLM_MAX_BODY_CHARS` (default: `8000`)

## Artifacts Written (Quarantine Folder)

For emails classified as `DEAL_SIGNAL` (final classification), triage now writes:
- `email.json` (existing)
- `email_body.txt` (existing)
- `triage_summary.json` (new; structured fields for UI)
- `triage_summary.md` (new; human-readable summary)

## How to Validate (Manual)

### 1) Confirm vLLM + model
```
curl -s http://localhost:8000/v1/models | jq '.data[].id'
```
Expected to include `Qwen/Qwen2.5-32B-Instruct-AWQ` (or your configured model).

### 2) Run triage once (same as systemd)
```
cd /home/zaks/bookkeeping && make triage-run
```

### 3) Verify new artifacts exist for a newly ingested deal-signal email
Look under:
`/home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<message_id>/`

Expected files:
- `triage_summary.json`
- `triage_summary.md`

### 4) Verify Quarantine API includes pointers
```
curl -s "http://localhost:8090/api/actions/quarantine?limit=5" | jq '.items[0] | {action_id, classification, confidence, triage_summary_path, quarantine_dir}'
```

### 5) Sanity-check false-positive suppression
If a message is deterministically flagged as deal-signal but LLM is confident it’s a newsletter/receipt:
- No `EMAIL_TRIAGE.REVIEW_EMAIL` action is created.
- Labels applied: `ZakOps/NonDeal` + `ZakOps/Processed`.

## Tests Run

Required commands (both pass):
- `bash /home/zaks/scripts/run_unit_tests.sh`
- `cd /home/zaks/bookkeeping && make triage-test`

## Operator Sanity Checklist

1) **Quarantine is clean**
   - `/api/actions/quarantine` is mostly real deal-signal items (not newsletters/receipts).
2) **Each Quarantine item is fast to decide**
   - `triage_summary.md` is present and readable.
   - `triage_summary.json` includes extracted fields (company, links, attachments classification).
3) **Approval still gates irreversible steps**
   - No email is sent automatically; no email is deleted automatically.
4) **Local-first**
   - Triage only calls `http://localhost:8000/v1/chat/completions` (no Gemini/OpenAI).

## Notes / Limitations

- Existing pending Quarantine actions created **before** this upgrade are not automatically re-scored; you may still see older false positives in the queue until rejected/cancelled.
- Assist-mode intentionally only **downgrades** deal-signal candidates (confidence ≥ 0.85) to avoid suppressing real deals due to model error.

