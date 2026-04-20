# V-L2.4: transition_deal_state() Function Exists
**VERDICT: PASS**

## Evidence
SQL function exists in database:
```
Schema: zakops
Name: transition_deal_state
Returns: TABLE(deal_id, previous_stage, previous_status, new_stage, new_status)
Args: p_deal_id, p_target_stage, p_actor (default 'system'), p_reason (default NULL)
Language: plpgsql
```

The function implements:
1. Row-level lock (FOR UPDATE) for concurrency safety
2. Deal existence check
3. Deleted deal rejection
4. Status derivation from target stage (archived/junk -> 'archived', others -> 'active')
5. Idempotent handling (already in target state -> no-op)
6. Audit trail append (JSONB)
7. Atomic UPDATE of stage + status + audit_trail + updated_at
8. Event recording in deal_events table
