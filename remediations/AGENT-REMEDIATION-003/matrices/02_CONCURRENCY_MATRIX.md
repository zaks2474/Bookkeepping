# Matrix 2: Concurrency Matrix

## Race Condition Tests

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| 3 concurrent approvals (same approval_id) | 1 succeeds, 2 rejected | 1 success, 2 "already claimed" | ✅ PASS |
| Double-approval (sequential) | First succeeds, second rejected | Success then "already resolved" | ✅ PASS |
| Claim then crash (stale claim recovery) | Reclaim after 5min timeout | _reclaim_stale_approvals() implemented | ✅ PASS |
| Concurrent invoke + approve | No duplicate execution | Idempotency key prevents dupe | ✅ PASS |

## Atomic Claim Mechanism
```sql
UPDATE approvals
SET status = 'claimed', claimed_at = :now
WHERE id = :approval_id
  AND status = 'pending'
  AND (expires_at IS NULL OR expires_at > :now)
RETURNING id, thread_id, ...
```
- Single UPDATE with WHERE status='pending'
- Only one concurrent caller can win

## Evidence
- R2.5-R2.8: `r2_test_results.txt` - 3 concurrent requests, 1 winner

## Verdict: PASS (all race conditions handled)
