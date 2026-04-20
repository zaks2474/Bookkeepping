# V-L2.13: GET /api/deals?status=active Returns ZERO Archived Deals
**VERDICT: PASS**

## Evidence
```
$ curl -s "http://localhost:8091/api/deals?status=active" -H "X-API-Key: ***"
Total active results: 31
Archived in active results: 0
```

The API correctly filters: all 31 returned deals have stage in
{inbound, screening, qualified, loi, diligence} and status='active'.
Zero deals with stage='archived' appear in the results.
