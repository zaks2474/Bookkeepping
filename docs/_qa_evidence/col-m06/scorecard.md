# QA-COL-M06 Scorecard

- Mission: `QA-COL-M06-VERIFY-001`
- Date: `2026-02-13`
- Evidence Dir: `/home/zaks/bookkeeping/docs/_qa_evidence/col-m06`

## Gate Results

| Gate | Evidence File | Result |
|------|---------------|--------|
| PF-1 | `pf1-validate.txt` | PASS |
| PF-2 | `pf2-dir.txt` | PASS |
| VF-01.1 | `vf01-1.txt` | PASS |
| VF-01.2 | `vf01-2.txt` | PASS |
| VF-01.3 | `vf01-3.txt` | PASS |
| VF-01.4 | `vf01-4.txt` | PASS |
| VF-02.1 | `vf02-1.txt` | PASS |
| VF-02.2 | `vf02-2.txt` | PASS |
| VF-02.3 | `vf02-3.txt` | PASS |
| VF-02.4 | `vf02-4.txt` | PASS |
| VF-02.5 | `vf02-5.txt` | PASS |
| VF-02.6 | `vf02-6.txt` | PASS |
| VF-03.1 | `vf03-1.txt` | PASS |
| VF-03.2 | `vf03-2.txt` | REMEDIATED |
| VF-03.3 | `vf03-3.txt` | PASS |
| VF-03.4 | `vf03-4.txt` | REMEDIATED |
| VF-03.5 | `vf03-5.txt` | REMEDIATED |
| VF-03.6 | `vf03-6.txt` | REMEDIATED |
| VF-04.1 | `vf04-1.txt` | REMEDIATED |
| VF-04.2 | `vf04-2.txt` | REMEDIATED |
| VF-04.3 | `vf04-3.txt` | REMEDIATED |
| VF-05.1 | `vf05-1.txt` | PASS |
| VF-05.2 | `vf05-2.txt` | REMEDIATED |
| VF-05.3 | `vf05-3.txt` | REMEDIATED |
| VF-05.4 | `vf05-4.txt` | PASS |
| VF-06.1 | `vf06-1.txt` | REMEDIATED |
| VF-06.2 | `vf06-2.txt` | REMEDIATED |
| VF-06.3 | `vf06-3.txt` | REMEDIATED |
| XC-1 | `xc1.txt` | PASS |
| XC-2 | `xc2.txt` | REMEDIATED |
| ST-1 | `st1.txt` | PASS |
| ST-2 | `st2.txt` | PASS |

## Remediation Details (FAIL -> REMEDIATED)

| Gate | Failure Class | Fix Applied | Re-verify |
|------|---------------|-------------|-----------|
| VF-03.2 | MISSING_CONTENT | Added `CanaryTokenManager` class in `apps/agent-api/app/core/security/canary_tokens.py`. | PASS |
| VF-03.4 | MISSING_CONTENT | Added `verify_no_leakage` manager + module function in `apps/agent-api/app/core/security/canary_tokens.py`. | PASS |
| VF-03.5 | SCOPE_GAP | Added sensitivity filtering (`high`/`critical`) for canary injection in `apps/agent-api/app/core/security/canary_tokens.py`. | PASS |
| VF-03.6 | MISSING_CONTENT | Added `CANARY-` prefix + sha256-derived token format in `apps/agent-api/app/core/security/canary_tokens.py`. | PASS |
| VF-04.1 | MISSING_FILE | Created `apps/agent-api/app/core/security/session_tracker.py`. | PASS |
| VF-04.2 | MISSING_CONTENT | Added `MAX_ATTEMPTS_BEFORE_LOCKDOWN = 3` and lockdown semantics in `apps/agent-api/app/core/security/session_tracker.py`; integrated usage in `apps/agent-api/app/core/langgraph/graph.py`. | PASS |
| VF-04.3 | MISSING_CONTENT | Added `record_attempt` in `apps/agent-api/app/core/security/session_tracker.py`. | PASS |
| VF-05.2 | WIRING_FAILURE | Injected canaries before LLM call via `inject_canary(...)` in `apps/agent-api/app/core/langgraph/graph.py`. | PASS |
| VF-05.3 | WIRING_FAILURE | Added post-response `verify_no_leakage(...)` checks in `apps/agent-api/app/core/langgraph/graph.py`. | PASS |
| VF-06.1 | MISSING_CONTENT | Added low-severity response matrix entries (log + sanitize + continue) in `apps/agent-api/app/core/security/injection_guard.py`. | PASS |
| VF-06.2 | MISSING_CONTENT | Added high-severity response matrix entries with tracker escalation + block in `apps/agent-api/app/core/security/injection_guard.py`. | PASS |
| VF-06.3 | MISSING_CONTENT | Added explicit canary leak `BLOCK` handling in `apps/agent-api/app/core/security/canary_tokens.py` and callsites in `apps/agent-api/app/core/langgraph/graph.py`. | PASS |
| XC-2 | SCOPE_GAP | Added `INJECTION_GUARD_MODE` (`observe`/`enforce`) toggle and enforcement helper in `apps/agent-api/app/core/security/injection_guard.py`; wired usage in `apps/agent-api/app/core/langgraph/graph.py`. | PASS |

## Summary

Summary: total gates = 32, pass = 19, fail = 0, skip = 0, remediated = 13.
