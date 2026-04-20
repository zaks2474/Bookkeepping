# V-L1.8: Health Endpoint Reports DB Identity
**VERDICT: PASS**

## Evidence
```
$ curl -sf http://localhost:8091/health | jq .
{
    "status": "healthy",
    "database": {
        "dbname": "zakops",
        "user": "zakops",
        "host": "172.23.0.3",
        "port": 5432
    },
    ...
}
```

The `/health` endpoint reports the connected database identity:
- Database name: `zakops` (canonical)
- User: `zakops`
- Port: 5432 (canonical, not 5435)
- Status: healthy
