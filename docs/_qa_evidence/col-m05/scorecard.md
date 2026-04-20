# QA-COL-M05 Scorecard

| Gate | Result | Evidence |
|------|--------|----------|
| PF-1 | PASS | `pf1-validate.txt` |
| PF-2 | PASS | `pf2-dir.txt` |
| VF-01.1 | PASS | `vf01-1.txt` |
| VF-01.2 | PASS | `vf01-2.txt` |
| VF-01.3 | FAIL | `vf01-3.txt` |
| VF-01.4 | FAIL | `vf01-4.txt` |
| VF-01.5 | PASS | `vf01-5.txt` |
| VF-02.1 | FAIL | `vf02-1.txt` |
| VF-02.2 | FAIL | `vf02-2.txt` |
| VF-02.3 | PASS | `vf02-3.txt` |
| VF-02.4 | PASS | `vf02-4.txt` |
| VF-02.5 | PASS | `vf02-5.txt` |
| VF-02.6 | PASS | `vf02-6.txt` |
| VF-03.1 | FAIL | `vf03-1.txt` |
| VF-03.2 | FAIL | `vf03-2.txt` |
| VF-03.3 | FAIL | `vf03-3.txt` |
| VF-04.1 | PASS | `vf04-1.txt` |
| VF-04.2 | PASS | `vf04-2.txt` |
| VF-04.3 | PASS | `vf04-3.txt` |
| VF-04.4 | PASS | `vf04-4.txt` |
| VF-05.1 | PASS | `vf05-1.txt` |
| VF-05.2 | PASS | `vf05-2.txt` |
| VF-05.3 | PASS | `vf05-3.txt` |
| VF-05.4 | PASS | `vf05-4.txt` |
| VF-05.5 | PASS | `vf05-5.txt` |
| VF-06.1 | PASS | `vf06-1.txt` |
| VF-06.2 | PASS | `vf06-2.txt` |
| VF-06.3 | REMEDIATED | `vf06-3.txt` |
| VF-07.1 | PASS | `vf07-1.txt` |
| VF-07.2 | PASS | `vf07-2.txt` |
| VF-07.3 | PASS | `vf07-3.txt` |
| XC-1 | PASS | `xc1.txt` |
| XC-2 | PASS | `xc2.txt` |
| XC-3 | PASS | `xc3.txt` |
| ST-1 | PASS | `st1.txt` |
| ST-2 | FAIL | `st2.txt` |

## Remediation Details (FAIL → REMEDIATED)

### VF-06.3
- Classification: `WIRING_FAILURE`
- Failure: Agent API did not read `X-User-Id` from request headers (empty evidence in initial run).
- Fix applied: Added `_resolve_actor_id()` in `apps/agent-api/app/api/v1/agent.py` to read `X-User-Id`/`x-user-id` header and fallback to request body actor ID; applied to invoke/approve/reject handlers.
- Re-verify: Re-ran exact gate command; evidence now shows header-read lines in `vf06-3.txt`.
- Validation re-run: `make validate-local` passed after remediation.

## Unremediated FAIL Classifications

- VF-01.3: `MISSING_CONTENT` (no `regenerate_summary`/`summarize` method found in backend service)
- VF-01.4: `MISSING_CONTENT` (no `recalculate_momentum`/`momentum` method definition in backend service)
- VF-02.1: `MISSING_CONTENT` (missing extraction prompt context fields evidence for `current_stage`, `existing_facts`, `existing_summary`)
- VF-02.2: `MISSING_CONTENT` (missing extraction output fields `new_risks`, `new_decisions`, `new_assumptions`, `new_open_items`)
- VF-03.1: `MISSING_CONTENT` (staleness logic not evidenced)
- VF-03.2: `MISSING_CONTENT` (contradiction counter increment logic not evidenced)
- VF-03.3: `MISSING_CONTENT` (periodic 10-turn re-summarization trigger not evidenced)
- ST-2: `MISSING_CONTENT` (no cost-effective extraction model tier marker found)

Remediation blocker for backend-targeted FAIL gates above: filesystem write denied for `/home/zaks/zakops-backend/src` in this environment (evidence: `remediation-backend-write-blocked.txt`).

**Summary:** total gates `36`, pass count `27`, fail count `8`, skip count `0` (plus `1` remediated)
