# V-L2.12: Concurrency Control (FOR UPDATE)
**VERDICT: PASS**

## Evidence
From `transition_deal_state()` function:

```sql
-- Row-level lock for concurrency safety (Q8)
SELECT d.stage, d.status, d.deleted
INTO v_current_stage, v_current_status, v_current_deleted
FROM zakops.deals d
WHERE d.deal_id = p_deal_id
FOR UPDATE;
```

The function uses `SELECT ... FOR UPDATE` to acquire an exclusive row-level lock before
reading current state and performing the transition. This prevents race conditions where
two concurrent transitions could read the same state and both proceed.
