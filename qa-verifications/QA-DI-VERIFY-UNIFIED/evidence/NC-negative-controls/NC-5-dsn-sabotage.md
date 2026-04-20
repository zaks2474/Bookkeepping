# NC-5: DSN SABOTAGE
Date: 2026-02-08

## Investigation
Searched for DSN validation in /home/zaks/zakops-backend/src/ *.py files.

## Findings
**STARTUP DSN GATE EXISTS** in `src/api/orchestration/main.py` (lines 343-400):

```python
# LAYER 1 — Startup DSN verification gate
CANONICAL_DB_NAME = "zakops"
CANONICAL_DB_USER = "zakops"

async with db_pool.acquire() as conn:
    db_info = await conn.fetchrow(
        "SELECT current_database() AS dbname, current_user AS dbuser, ..."
    )
    actual_db = db_info["dbname"]
    if actual_db != CANONICAL_DB_NAME:
        await db_pool.close()
        raise RuntimeError(
            f"STARTUP GATE FAILURE: Connected to database '{actual_db}' "
            f"but canonical database is '{CANONICAL_DB_NAME}'. "
            f"Refusing to start."
        )
```

The gate:
1. Connects to the database pool
2. Queries `current_database()` and `current_user`
3. Compares against canonical values (zakops/zakops)
4. If mismatch: closes pool and raises RuntimeError (app refuses to start)
5. Stores verified identity in `app.state.db_identity` for health endpoint

## Gate Assessment
The DSN startup gate is a robust defense against database misrouting. It prevents
the backend from operating against the wrong database (e.g., if DATABASE_URL were
accidentally pointed at crawlrag or zakops_agent).

**RESULT: PASS** (DSN startup gate exists and is implemented correctly)
