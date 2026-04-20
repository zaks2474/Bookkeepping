# EMAIL 3H — World-Class Triage Verification (Local Qwen/vLLM, Thread-Aware, Backfill v1)

Generated: 2026-01-11

## Summary (What Changed)

- Email triage now writes a **versioned triage artifact**: `triage_summary.json` uses `zakops.email_triage.v1` and `triage_summary.md` is rendered from the same payload.
- In `EMAIL_TRIAGE_LLM_MODE=full`, triage is **thread-aware** and now includes a **best-effort fallback** when the Gmail thread fetch fails (Gmail search-based approximation, capped to 25 messages).
- Sender-history backfill now emits a **versioned report**: `sender_history_backfill_v1.json` uses `zakops.email_backfill.v1`, with sanitized evidence quotes (no URL query/fragment).
- Eval harness for Email 3H now supports a **Markdown report** over exported samples and uses the **v1 triage schema** when scoring the LLM path.

## Safety / Non-Negotiables Check

- Local-only: triage and backfill refuse non-local LLM base URLs (vLLM on `http://localhost:8000/v1`).
- No auto-send, no auto-delete: this work does not add any outbound email sending.
- URL sanitization: persisted links, evidence quotes, and stored `email_body.txt` artifacts strip URL query/fragment.
- No LangSmith tracing enablement.

## Files Changed (Core)

- `bookkeeping/scripts/email_triage_agent/ma_triage_v1.py`
- `bookkeeping/scripts/email_triage_agent/llm_triage.py`
- `bookkeeping/scripts/email_triage_agent/run_once.py`
- `bookkeeping/scripts/email_triage_agent/eval_3h_hardening.py`
- `bookkeeping/scripts/email_triage_agent/tests/test_llm_triage.py`
- `bookkeeping/scripts/email_triage_agent/tests/test_thread_fallback_search.py`
- `scripts/actions/executors/deal_backfill_sender_history.py`
- `bookkeeping/Makefile`
- `bookkeeping/docs/EMAIL_3H_P0_HARDENING_VERIFICATION.md`

## Proof (Commands Run)

- `cd /home/zaks/bookkeeping && make triage-test` (passes)
- `bash /home/zaks/scripts/run_unit_tests.sh` (passes)
- `cd /home/zaks/bookkeeping && make triage-eval-3h` (writes `bookkeeping/docs/EMAIL_3H_EVAL_REPORT.md`)

## Operator Validation Checklist (Manual)

1) Run triage once (dry-run first if desired):
   - `cd /home/zaks/bookkeeping/scripts && sudo -u zaks python3 -m email_triage_agent.run_once --dry-run --max-per-run 5`
2) Confirm deal-signal items write v1 artifacts:
   - `find /home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE -maxdepth 2 -name triage_summary.json | head`
   - Inspect one: ensure `schema_version` is `zakops.email_triage.v1`
3) Confirm thread fallback works when thread fetch fails:
   - Look for `fallback_search_used` in `DataRoom/.deal-registry/logs/email_triage_3h.jsonl`
4) Approve a Quarantine item and confirm backfill emits v1 report:
   - Find the `DEAL.BACKFILL_SENDER_HISTORY` action artifacts and confirm `sender_history_backfill_v1.json` exists.
   - Confirm a copy is written under the deal folder: `<deal>/07-Correspondence/backfill_sender_history_*.json`

## Known Limitations / Follow-ups

- Non-deal subtype: the v1 triage contract models “M&A relevance”; non-deal subtypes (newsletter vs receipt) remain primarily deterministic/label-based.
- Thread fallback uses Gmail search (`threadid:` first, then `from:+subject`); it is approximate by design and caps to 25 messages.
