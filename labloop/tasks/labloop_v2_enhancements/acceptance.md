# Acceptance: Lab Loop v2 Enhancements

## A) Backwards Compatibility (MUST PASS)
- Running an existing task with only REPO_DIR + GATE_CMD works unchanged.
- No new required fields added to QA schema or builder schema.
- No changes required to existing task folders.

## B) Flaky Gate Policy (MUST PASS)
- Create and run the included "flake policy test task".
- Evidence must exist:
  - history/gate_attempt_1.log and history/gate_attempt_2.log
  - artifacts/gate_attempts.json
- artifacts/gate_attempts.json must show:
  - attempts >= 2
  - first exit_code != 0
  - final exit_code == 0
  - flake_suspected == true
- QA_REPORT.json must still have verdict PASS when final is successful.

## C) Spec Oracle (MUST PASS)
- Create and run the included "spec oracle test task".
- When SPEC_CHECK_CMD fails:
  - cycle verdict FAIL
  - spec_check.json shows passed=false and exit_code != 0
- After Builder fix:
  - spec_check.json shows passed=true and exit_code==0
  - task verdict PASS

## D) Prompt Evals (MUST PASS)
- Create and run the included "prompt eval test task".
- When EVAL_CMD fails:
  - cycle verdict FAIL
  - eval_results.json is missing or indicates failure
- After Builder fix:
  - eval_results.json exists at configured path and contains valid JSON
  - task verdict PASS

## E) Bundling & Visibility (MUST PASS)
- QA bundle includes the new artifacts when present:
  - gate_attempts.json
  - spec_check.json (+ last spec log)
  - eval_results.json (+ last eval log)
- `labloop status <task>` displays:
  - flake_suspected
  - spec_check pass/fail
  - eval pass/fail

## F) Escalation Packet Completeness (MUST PASS)
On STUCK condition:
- escalation zip contains:
  - gate_attempt_*.log + gate_attempts.json
  - spec_check.* files if configured
  - eval_results.* files if configured

## G) NO GUIDE V2 EDITS (HARD REQUIREMENT)
- /home/zaks/bookkeeping/docs/ must remain at guide version 2.
- The file designated as "guide v2" must not be changed in this mission.
- If documentation is needed, it must be in:
  - labloop-addendum-v2.x.md and/or labloop-release-notes-v2.x.md

## Gate Command
```bash
./tasks/labloop_v2_enhancements/verify.sh
```
