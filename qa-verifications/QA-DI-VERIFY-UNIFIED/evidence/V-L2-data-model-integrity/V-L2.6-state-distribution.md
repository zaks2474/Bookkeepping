# V-L2.6: Backfill State Distribution
**VERDICT: PASS**

## Evidence
```sql
SELECT stage, status, deleted, count(*)
FROM zakops.deals GROUP BY stage, status, deleted ORDER BY stage, status, deleted;

   stage   |  status  | deleted | count
-----------+----------+---------+-------
 archived  | archived | f       |     7
 diligence | active   | f       |     1
 inbound   | active   | f       |    21
 inbound   | deleted  | t       |    10
 loi       | active   | f       |     1
 qualified | deleted  | t       |     1
 screening | active   | f       |     7
 screening | deleted  | t       |     1
```

All state combinations are valid per the lifecycle model:
- Active stages (inbound/screening/qualified/loi/diligence) have status='active' and deleted=false
- Archived stage has status='archived' and deleted=false
- Deleted deals have status='deleted' and deleted=true
- No impossible combinations exist
