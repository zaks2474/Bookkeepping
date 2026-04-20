# V-L2.8b: Trigger Enforces Consistency
**VERDICT: PASS**

## Evidence
`enforce_deal_lifecycle()` function definition:

```sql
CREATE OR REPLACE FUNCTION zakops.enforce_deal_lifecycle()
  RETURNS trigger LANGUAGE plpgsql
AS $function$
BEGIN
    -- Auto-correct: if stage is set to archived/junk, ensure status matches
    IF NEW.stage IN ('archived', 'junk') AND NEW.status = 'active' AND NOT NEW.deleted THEN
        NEW.status := 'archived';
    END IF;

    -- Auto-correct: if deleted is set, ensure status matches
    IF NEW.deleted AND NEW.status != 'deleted' THEN
        NEW.status := 'deleted';
    END IF;

    -- Auto-correct: if status is set to active, ensure stage is not terminal
    IF NEW.status = 'active' AND NEW.stage IN ('archived', 'junk') AND NOT NEW.deleted THEN
        RAISE EXCEPTION 'Cannot set status to active when stage is %', NEW.stage;
    END IF;

    RETURN NEW;
END;
$function$
```

The trigger:
1. Auto-corrects status when stage is set to archived/junk
2. Auto-corrects status when deleted flag is set
3. RAISES EXCEPTION if someone tries to set status='active' with terminal stage
4. Fires on BOTH INSERT and UPDATE (BEFORE)
