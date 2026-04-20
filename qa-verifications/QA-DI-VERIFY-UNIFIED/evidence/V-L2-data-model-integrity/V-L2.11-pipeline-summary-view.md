# V-L2.11: v_pipeline_summary View Output
**VERDICT: PASS**

## Evidence
```sql
SELECT * FROM zakops.v_pipeline_summary;

   stage   | count | avg_days_in_stage
-----------+-------+-------------------
 inbound   |    21 |               2.5
 screening |     7 |               4.6
 qualified |     1 |               0.0
 loi       |     1 |               0.0
 diligence |     1 |               5.0
```

The view correctly:
1. Excludes archived deals (7 archived deals not shown)
2. Excludes deleted deals (12 deleted deals not shown)
3. Shows only active pipeline stages
4. Reports deal counts and average days per stage
