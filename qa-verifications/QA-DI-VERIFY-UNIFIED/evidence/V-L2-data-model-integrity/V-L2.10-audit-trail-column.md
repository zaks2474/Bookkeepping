# V-L2.10: audit_trail Column Exists (JSONB with default '[]')
**VERDICT: PASS**

## Evidence
```sql
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_schema = 'zakops' AND table_name = 'deals' AND column_name = 'audit_trail';

 column_name | data_type | column_default
-------------+-----------+----------------
 audit_trail | jsonb     | '[]'::jsonb
```

The `audit_trail` column exists on `zakops.deals`:
- Type: JSONB
- Default: `'[]'::jsonb` (empty array)
