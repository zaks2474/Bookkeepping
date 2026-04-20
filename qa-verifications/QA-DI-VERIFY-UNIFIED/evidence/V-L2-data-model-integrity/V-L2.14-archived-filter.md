# V-L2.14: GET /api/deals?status=archived Returns Archived Deals
**VERDICT: PASS**

## Evidence
```
$ curl -s "http://localhost:8091/api/deals?status=archived" -H "X-API-Key: ***"
Total archived results: 6
  DL-0042: stage=archived status=archived
  DL-0049: stage=archived status=archived
  DL-0048: stage=archived status=archived
  DL-0061: stage=archived status=archived
  DL-0047: stage=archived status=archived
  DL-0062: stage=archived status=archived
```

The API returns 6 archived deals (out of 7 total -- 1 was restored during V-L2.3 testing
and is now DL-0036 back in screening/active). All returned deals correctly have
stage='archived' and status='archived'.

Note: The DB shows 7 archived deals but DL-0036 was restored during testing (V-L2.3).
After restore, re-archiving was not performed, so count difference is expected.
