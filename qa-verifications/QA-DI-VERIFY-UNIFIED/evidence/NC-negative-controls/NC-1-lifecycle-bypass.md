# NC-1: LIFECYCLE BYPASS
Date: 2026-02-08

## Pre-Sabotage State
DL-0037: status=active, stage=qualified (verified via SELECT)

## Sabotage Applied
SQL: UPDATE zakops.deals SET status='active', stage='archived' WHERE deal_id='DL-0037'

## Gate Result
The UPDATE was accepted (UPDATE 1), but the `enforce_deal_lifecycle_trigger` BEFORE trigger
AUTO-CORRECTED the impossible state:
- Input: status='active', stage='archived' (impossible per chk_deal_lifecycle)
- Output: status='archived', stage='archived' (valid state)

The trigger function logic:
```sql
IF NEW.stage IN ('archived', 'junk') AND NEW.status = 'active' AND NOT NEW.deleted THEN
    NEW.status := 'archived';
END IF;
```

This means the impossible state (active+archived) NEVER reaches the CHECK constraint because
the trigger normalizes it first. The defense is auto-correction, not rejection.

## Revert
Restored DL-0037 to status='active', stage='qualified' (verified via SELECT)

## Post-Revert State
DL-0037 confirmed at original state.

**RESULT: PASS** (trigger auto-corrects impossible state; impossible data never persists)
