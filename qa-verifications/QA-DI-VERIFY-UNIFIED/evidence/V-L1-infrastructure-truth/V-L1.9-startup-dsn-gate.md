# V-L1.9: Startup DSN Gate Exists
**VERDICT: PASS**

## Evidence
File: `/home/zaks/zakops-backend/src/api/orchestration/main.py`, lines 366-390

```python
CANONICAL_DB_NAME = "zakops"  # line 344

# LAYER 1 -- Startup DSN verification gate
# Refuse to start if connected DB does not match canonical identity
async with db_pool.acquire() as conn:
    db_info = await conn.fetchrow(
        "SELECT current_database() AS dbname, current_user AS dbuser, "
        "inet_server_addr() AS host, inet_server_port() AS port"
    )
    actual_db = db_info["dbname"]
    actual_user = db_info["dbuser"]
    print(f"DSN gate check: db={actual_db}, user={actual_user}")
    if actual_db != CANONICAL_DB_NAME:
        await db_pool.close()
        raise RuntimeError(
            f"STARTUP GATE FAILURE: Connected to database '{actual_db}' "
            f"but canonical database is '{CANONICAL_DB_NAME}'. "
            f"Refusing to start. Fix DATABASE_URL to point to the canonical DB."
        )
    # Store DB identity for health endpoint
    app.state.db_identity = { ... }
print(f"DSN gate PASSED: {app.state.db_identity}")
```

The backend refuses to start if DATABASE_URL points to any database other than `zakops`.
This is a hard gate at lifespan startup, not just a warning.
