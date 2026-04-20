# V-L2.7: CHECK Constraint Exists on Deals Table
**VERDICT: PASS**

## Evidence
```sql
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
WHERE conrelid = 'zakops.deals'::regclass AND contype = 'c';

conname: chk_deals_stage
  CHECK ((stage)::text = ANY (ARRAY['inbound','screening','qualified','loi',
         'diligence','closing','portfolio','junk','archived']))

conname: chk_deal_lifecycle
  CHECK (
    (status='active' AND stage NOT IN ('archived','junk') AND deleted=false)
    OR (status='archived' AND stage IN ('archived','junk') AND deleted=false)
    OR (status='deleted' AND deleted=true)
  )
```

Two CHECK constraints exist:
1. `chk_deals_stage` -- Restricts stage to valid enum values
2. `chk_deal_lifecycle` -- Enforces valid state combinations (status/stage/deleted triplet)
