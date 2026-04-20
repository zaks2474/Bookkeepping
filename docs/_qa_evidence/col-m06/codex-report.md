QA-COL-M06 mission executed end-to-end.

- All 32 gate commands were run and evidence was captured in `/home/zaks/bookkeeping/docs/_qa_evidence/col-m06`.
- Failed gates were remediated, failing gate commands were re-run, and `make validate-local` was re-run per protocol.
- Final scorecard written to `/home/zaks/bookkeeping/docs/_qa_evidence/col-m06/scorecard.md`.
- Scorecard summary: total gates = 32, pass = 19, fail = 0, skip = 0, remediated = 13.

Remediation touched:
- `apps/agent-api/app/core/security/injection_guard.py`
- `apps/agent-api/app/core/security/canary_tokens.py`
- `apps/agent-api/app/core/security/session_tracker.py`
- `apps/agent-api/app/core/langgraph/graph.py`