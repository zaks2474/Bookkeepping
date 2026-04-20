# NC-6: COUNT INVARIANT SABOTAGE
Date: 2026-02-08

## Sabotage Applied
```sql
INSERT INTO zakops.deals (deal_id, canonical_name, status, stage, deleted)
VALUES ('DL-NC6', 'NC6-test', 'active', 'archived', false);
```

## Gate Result
The INSERT SUCCEEDED (INSERT 0 1). The `enforce_deal_lifecycle_trigger` auto-corrected
the impossible state before the CHECK constraint evaluated:
- Input: status='active', stage='archived', deleted=false
- Trigger auto-corrected to: status='archived', stage='archived', deleted=false
- This satisfies `chk_deal_lifecycle` (archived status + archived stage + not deleted = valid)

The impossible state NEVER persisted — the trigger normalized it before the row was written.

## Revert
Row deleted: `DELETE FROM zakops.deals WHERE deal_id = 'DL-NC6'` (DELETE 1)

## Analysis
The defense mechanism is AUTO-CORRECTION rather than REJECTION. The trigger function
`enforce_deal_lifecycle()` runs BEFORE INSERT/UPDATE and normalizes invalid state
combinations before the CHECK constraint evaluates. This means:
- Impossible states cannot persist in the database
- The trigger silently corrects rather than raising an error
- The CHECK constraint `chk_deal_lifecycle` serves as a SECOND layer if the trigger misses a case

This is a valid defense pattern (defense in depth), but note that the application
does not receive an error — it may believe it set status='active' when the DB actually
stored status='archived'.

**RESULT: PASS** (impossible state prevented from persisting; auto-correction defense)
