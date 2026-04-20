# V-L2.8: Database Trigger Exists on Deals
**VERDICT: PASS**

## Evidence
```sql
SELECT tgname, pg_get_triggerdef(oid) FROM pg_trigger
WHERE tgrelid = 'zakops.deals'::regclass AND NOT tgisinternal;

tgname: deals_updated_at
  BEFORE UPDATE FOR EACH ROW EXECUTE FUNCTION update_timestamp()

tgname: enforce_deal_lifecycle_trigger
  BEFORE INSERT OR UPDATE FOR EACH ROW EXECUTE FUNCTION enforce_deal_lifecycle()
```

Two triggers exist:
1. `deals_updated_at` -- Auto-updates `updated_at` timestamp on UPDATE
2. `enforce_deal_lifecycle_trigger` -- Enforces lifecycle consistency on INSERT/UPDATE
