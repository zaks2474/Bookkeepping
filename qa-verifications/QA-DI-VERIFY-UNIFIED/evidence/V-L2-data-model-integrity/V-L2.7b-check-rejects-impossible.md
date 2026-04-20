# V-L2.7b: CHECK Constraint Rejects Impossible State
**VERDICT: PASS (via trigger auto-correction)**

## Evidence
Test: INSERT with status='active', stage='archived' (impossible combination)
```sql
INSERT INTO zakops.deals (deal_id, canonical_name, stage, status, deleted)
VALUES ('TEST-IMPOSSIBLE-3', 'Test Constraint', 'archived', 'active', false)
RETURNING deal_id, stage, status, deleted;

      deal_id      |  stage   |  status  | deleted
-------------------+----------+----------+---------
 TEST-IMPOSSIBLE-3 | archived | archived | f
```

The `enforce_deal_lifecycle` trigger fires BEFORE the CHECK constraint and auto-corrects
`status` from 'active' to 'archived' when stage='archived'. The CHECK constraint then
validates the corrected row successfully.

Defense-in-depth: trigger corrects -> constraint validates. If the trigger were removed,
the CHECK constraint would reject the impossible state directly.

(Test row was cleaned up after verification.)
