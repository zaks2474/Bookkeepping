# E03 -- Created vs Deduped Measurable

**Gate:** AC-03 -- Callers can distinguish newly created quarantine items from dedup hits via HTTP status code
**Source file:** `/home/zaks/zakops-backend/src/api/orchestration/main.py`
**Date:** 2026-02-13

---

## 1. Endpoint Under Test

```
POST /api/quarantine
```

Defined at **line 1509**:

```python
@app.post("/api/quarantine", response_model=QuarantineResponse)
async def create_quarantine_item(
    item: QuarantineCreate,
    request: Request,
    response: Response,
    pool: asyncpg.Pool = Depends(get_db)
):
```

The docstring at **lines 1516-1519** explicitly documents the contract:

> Returns 201 for newly created items, 200 for dedup hits (existing message_id).
> This distinction allows callers to measure injection vs deduplication rates.

---

## 2. Dedup Check -- 200 Response (Application-Level)

**Lines 1558-1580:** The handler performs a SELECT to check if `message_id` already exists:

```python
# Deduplicate by message_id
existing = await conn.fetchrow(
    "SELECT id FROM zakops.quarantine_items WHERE message_id = $1",
    item.message_id
)
if existing:
    # Return existing item with 200 (dedup hit, not a new creation)
    row = await conn.fetchrow(...)
    response.status_code = 200         # <-- LINE 1579
    return record_to_dict(row)
```

**Evidence:** When a quarantine item with the same `message_id` already exists in the database, the handler:
1. Fetches the existing record (line 1565-1577)
2. Sets `response.status_code = 200` (line 1579)
3. Returns the existing record (line 1580)

This is the "fast path" dedup -- no INSERT is attempted.

---

## 3. New Creation -- 201 Response

**Lines 1582-1627:** When no existing record is found, the handler INSERTs a new row:

```python
row = await conn.fetchrow(
    """
    INSERT INTO zakops.quarantine_items
        (id, message_id, subject, sender, body_preview,
         received_at, confidence, reason, raw_content, status,
         correlation_id, source_type)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, 'pending', $10, $11)
    ON CONFLICT (message_id) DO NOTHING
    RETURNING ...
    """,
    ...
)
```

If the INSERT succeeds (row is not None), execution falls through to:

```python
response.status_code = 201             # <-- LINE 1626
return record_to_dict(row)             # <-- LINE 1627
```

**Evidence:** Newly created items return HTTP 201 Created.

---

## 4. ON CONFLICT DO NOTHING -- Race Condition Handling

**Lines 1589, 1606-1624:** The INSERT uses `ON CONFLICT (message_id) DO NOTHING` to handle the TOCTOU race where two concurrent requests pass the initial SELECT check but only one wins the INSERT.

```python
# Race condition safety: if ON CONFLICT triggered (row is None),
# fetch the existing record that won the race -- this is a dedup hit
if row is None:                        # <-- LINE 1608
    row = await conn.fetchrow(
        """SELECT ... FROM zakops.quarantine_items q WHERE q.message_id = $1""",
        item.message_id
    )
    response.status_code = 200         # <-- LINE 1623
    return record_to_dict(row)         # <-- LINE 1624
```

**Evidence:** When the INSERT silently does nothing due to a concurrent insert winning the race:
1. `RETURNING` produces `None` (no row was inserted)
2. The handler detects `row is None` (line 1608)
3. Fetches the record that won the race (lines 1609-1622)
4. Sets `response.status_code = 200` (line 1623) -- correctly marking it as a dedup hit
5. Returns the existing record (line 1624)

This three-layer approach (SELECT dedup -> INSERT ON CONFLICT DO NOTHING -> fallback fetch) ensures:
- No duplicate quarantine items can ever be created for the same `message_id`
- Every response carries the correct 200/201 status regardless of concurrency
- The race window between SELECT and INSERT is safely handled by the DB constraint

---

## 5. Status Code Summary

| Scenario | Status Code | Lines |
|----------|-------------|-------|
| Existing `message_id` found by SELECT | **200** | 1559-1580 |
| INSERT succeeds (new item) | **201** | 1626-1627 |
| INSERT hits ON CONFLICT (race loser) | **200** | 1608-1624 |

---

## 6. Source Type Validation Guard

**Lines 1534-1542:** Before any dedup or creation logic, the handler validates `source_type` against the canonical set:

```python
VALID_SOURCE_TYPES = {"email", "email_sync", "langsmith_shadow", "langsmith_live", "manual"}

if source_type not in VALID_SOURCE_TYPES:
    return JSONResponse(status_code=400, ...)
```

This ensures LangSmith shadow injections (`langsmith_shadow`) are accepted while unknown source types are rejected with 400.

---

## Verdict: **PASS**

The `POST /api/quarantine` endpoint provides a clear, measurable distinction between created (201) and deduplicated (200) items through three layers of handling:

1. **Application-level dedup** (SELECT before INSERT) -- returns 200
2. **Successful creation** (INSERT succeeds) -- returns 201
3. **Race-condition dedup** (ON CONFLICT DO NOTHING + fallback fetch) -- returns 200

Callers (including the LangSmith shadow pipeline) can count 201s vs 200s to measure injection vs deduplication rates without any ambiguity.
