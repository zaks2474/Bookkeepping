# V-L2.3: Restore Endpoint Performs COMPLETE Reversal
**VERDICT: PASS**

## Evidence
Test: Restore DL-0036 from archived to screening
```
$ curl -s -X POST "http://localhost:8091/api/deals/DL-0036/restore?target_stage=screening" -H "X-API-Key: ***"
{"success":true,"deal_id":"DL-0036","restored_to_stage":"screening","previous_status":"archived","new_status":"active"}
```

DB verification after restore:
```
 deal_id |   stage   | status | deleted
---------+-----------+--------+---------
 DL-0036 | screening | active | f
```

The restore endpoint:
1. Restores stage to target (screening) (DONE)
2. Restores status to 'active' (DONE)
3. deleted remains false (DONE)

Full reversal via `zakops.transition_deal_state()` SQL function.
