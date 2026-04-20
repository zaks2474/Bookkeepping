# QA-COL-M04-VERIFY-001 Scorecard

| Gate | Result |
|---|---|
| PF-1 | PASS |
| PF-2 | PASS |
| PF-3 | REMEDIATED |
| VF-01.1 | PASS |
| VF-01.2 | PASS |
| VF-01.3 | REMEDIATED |
| VF-01.4 | REMEDIATED |
| VF-02.1 | REMEDIATED |
| VF-02.2 | REMEDIATED |
| VF-02.3 | REMEDIATED |
| VF-02.4 | REMEDIATED |
| VF-02.5 | REMEDIATED |
| VF-02.6 | REMEDIATED |
| VF-02.7 | REMEDIATED |
| VF-02.8 | REMEDIATED |
| VF-02.9 | REMEDIATED |
| VF-02.10 | REMEDIATED |
| VF-02.11 | REMEDIATED |
| VF-03.1 | REMEDIATED |
| VF-03.2 | REMEDIATED |
| VF-03.3 | REMEDIATED |
| VF-03.4 | REMEDIATED |
| VF-03.5 | REMEDIATED |
| VF-03.6 | REMEDIATED |
| VF-04.1 | REMEDIATED |
| VF-04.2 | REMEDIATED |
| VF-04.3 | REMEDIATED |
| VF-04.4 | REMEDIATED |
| VF-05.1 | REMEDIATED |
| VF-05.2 | REMEDIATED |
| VF-05.3 | REMEDIATED |
| VF-06.1 | REMEDIATED |
| VF-06.2 | REMEDIATED |
| VF-06.3 | REMEDIATED |
| VF-06.4 | REMEDIATED |
| VF-06.5 | REMEDIATED |
| VF-06.6 | REMEDIATED |
| VF-07.1 | REMEDIATED |
| VF-07.2 | REMEDIATED |
| VF-08.1 | PASS |
| VF-08.2 | PASS |
| XC-1 | PASS |
| XC-2 | REMEDIATED |
| XC-3 | REMEDIATED |
| ST-1 | PASS |
| ST-2 | PASS |

## Remediation Details (FAIL -> REMEDIATED)

1. Gate IDs: PF-3, VF-01.4, VF-02.1..VF-02.11, VF-03.1..VF-03.6, VF-04.1..VF-04.4, VF-05.1..VF-05.3, VF-06.1..VF-06.6, VF-07.2, XC-2, XC-3
   - Classification: WIRING_FAILURE
   - Evidence read: `/tmp/col-m04-initial-1771004030/*.txt`
   - Root cause: PF-3 `find /home/zaks/zakops-backend -name "028_deal_brain*" | head -1` resolved to rollback file (`028_deal_brain_rollback.sql`) instead of forward migration.
   - Fix applied: Explicitly bound `M028=/home/zaks/zakops-backend/db/migrations/028_deal_brain.sql` and re-ran the affected gate commands to regenerate evidence files.
   - Re-verify: Affected gate evidence files now contain expected patterns under `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/`.
   - Validation rerun: `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/remediation-validate.txt` (PASS).

2. Gate ID: VF-01.3
   - Classification: FALSE_POSITIVE
   - Evidence read: `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf01-3.txt`
   - Root cause: Gate regex expects `INSERT ... 028` on one line; migration uses multiline SQL (`INSERT` line + `VALUES ('028',...)` line).
   - Fix applied: Added multiline verification evidence in `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf01-3-remediation.txt`.
   - Re-verify: Required migration tracking statement with version `028` confirmed.
   - Validation rerun: `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/remediation-validate-2.txt` (PASS).

3. Gate ID: VF-07.1
   - Classification: FALSE_POSITIVE
   - Evidence read: `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf07-1.txt`
   - Root cause: Gate regex expects `INSERT ... SELECT ... FROM ...` on one line; migration uses multiline SQL block.
   - Fix applied: Added multiline verification evidence in `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf07-1-remediation.txt`.
   - Re-verify: Backfill `INSERT INTO zakops.deal_brain ... FROM zakops.agent_context_summaries` confirmed.
   - Validation rerun: `/home/zaks/bookkeeping/docs/_qa_evidence/col-m04/remediation-validate-2.txt` (PASS).

Summary: total gates = 46, pass count = 9, fail count = 0, skip count = 0, remediated count = 37.
