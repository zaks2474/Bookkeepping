# Approval State Transition Matrix

## Valid Transitions

| From State | To State | Trigger | Evidence | Result |
|------------|----------|---------|----------|--------|
| pending | approved | POST :approve | 4_2_1_approve_valid.txt | **PASS** |
| pending | rejected | POST :reject | 4_2_4b_reject_valid.txt | **PASS** |
| pending | expired | expiry check | 4_3_3_expiry_code.txt | DOCUMENTED (lazy expiry) |

## Invalid Transitions (Must Be Blocked)

| From State | To State | Trigger | Evidence | Result |
|------------|----------|---------|----------|--------|
| approved | approved | POST :approve (double) | 4_2_2_double_approve.txt | **BLOCKED** (HTTP 409) |
| approved | rejected | POST :reject | 4_2_3_reject_approved.txt | **BLOCKED** (HTTP 409) |
| rejected | approved | POST :approve | 4_2_5_approve_rejected.txt | **BLOCKED** (HTTP 409) |
| rejected | rejected | POST :reject (double) | implicit | **BLOCKED** (HTTP 409) |

## Race Condition Testing

| Test | Description | Evidence | Result |
|------|-------------|----------|--------|
| Concurrent approve/reject | Fire both simultaneously | 4_6_2_race_results.txt | **PASS** (1 wins, 1 gets 409) |
| N=20 burst approve | 20 concurrent approvals | 4_6_y_spam_burst.txt | **PASS** (1x 200, 19x 409) |
| Replay after completion | Re-approve completed | 4_6_z_replay.txt | **PASS** (HTTP 409) |

## Tool Execution Invariants

| Check | Condition | Evidence | Result |
|-------|-----------|----------|--------|
| Approved → 1 execution | COUNT = 1 after approve | 4_2_2_double_approve.txt | **PASS** |
| Rejected → 0 executions | COUNT = 0 after reject | 4_2_6_no_exec_on_reject.txt | **PASS** |
| No orphaned executions | All executions have approval | 4_5_3_orphaned_executions.txt | **PASS** (0 rows) |
| No orphaned approvals | All approved have execution | 4_5_4_orphaned_approvals.txt | **PASS** (0 rows) |
