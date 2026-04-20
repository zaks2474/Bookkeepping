# V-L2.10b: Transition Function Writes to audit_trail
**VERDICT: PASS**

## Evidence
From `transition_deal_state()` function body:

```sql
-- Build audit entry
v_audit_entry := jsonb_build_object(
    'action', 'transition',
    'from_stage', v_current_stage,
    'from_status', v_current_status,
    'to_stage', p_target_stage,
    'to_status', v_new_status,
    'actor', p_actor,
    'reason', COALESCE(p_reason, 'state transition'),
    'at', NOW()::text
);

-- Execute atomic transition
UPDATE zakops.deals d
SET stage = p_target_stage,
    status = v_new_status,
    audit_trail = d.audit_trail || jsonb_build_array(v_audit_entry),
    updated_at = NOW()
WHERE d.deal_id = p_deal_id;
```

Every transition appends a structured JSONB entry to `audit_trail` containing:
action, from_stage, from_status, to_stage, to_status, actor, reason, timestamp.
