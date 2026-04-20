# E04 — Correlation ID End-to-End

**Date:** 2026-02-13
**Source:** `/home/zaks/zakops-backend/src/api/orchestration/main.py`
**Verdict:** PASS

---

## Chain Summary

```
X-Correlation-ID header (request)
  --> quarantine_items.correlation_id (INSERT)
    --> deals.identifiers.correlation_id (JSON metadata)
      --> deal_transitions.correlation_id (FSM ledger)
        --> outbox.correlation_id (event bus, UUID fallback)
```

---

## Link 1 — Header Capture (line 1529)

The `POST /api/quarantine` endpoint extracts the correlation ID from the
incoming HTTP request header, supporting both canonical and lowercase forms.

```python
# Line 1528-1529
# F-8: Capture correlation ID from incoming request header
correlation_id = request.headers.get("X-Correlation-ID") or request.headers.get("x-correlation-id")
```

**Evidence:** Case-insensitive header extraction. If neither header is present,
`correlation_id` resolves to `None`, which is a valid nullable DB column value.

---

## Link 2 — Quarantine INSERT (lines 1582-1603)

The captured `correlation_id` is persisted as a dedicated column in the
`zakops.quarantine_items` table during the INSERT.

```python
# Lines 1584-1588 (column list)
INSERT INTO zakops.quarantine_items
    (id, message_id, subject, sender, body_preview,
     received_at, confidence, reason, raw_content, status,
     correlation_id, source_type)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb, 'pending', $10, $11)
```

```python
# Lines 1600-1603 (parameter binding)
item_id, item.message_id, item.email_subject, item.sender,
item.raw_body, item.received_at, item.confidence,
item.classification, _json.dumps(raw_content),
correlation_id, source_type,
```

**Evidence:** `correlation_id` is bound as parameter `$10` in the INSERT
statement. The value comes directly from the header capture at Link 1.

---

## Link 3 — Deal Creation Metadata (lines 1806-1814)

When a quarantine item is approved and promoted to a deal, the `correlation_id`
is embedded in the `identifiers` JSONB column of the `zakops.deals` table.

```python
# Lines 1806-1814 (identifiers JSON)
json.dumps({
    'quarantine_item_id': item_id,
    'message_id': item.get('message_id'),
    # F-16: Email linkage hints for future thread resolution
    'email_sender': sender,
    'email_subject': subject,
    'source_type': item.get('source_type', 'email'),
    'correlation_id': str(item.get('correlation_id') or ''),
}),
```

**Evidence:** The `correlation_id` is read back from the quarantine item record
(`item.get('correlation_id')`) and serialized into the deal's `identifiers`
JSON. The `or ''` fallback ensures an empty string rather than `None` in JSON.

---

## Link 3b — Deal Transitions Ledger (lines 1827-1838)

The correlation ID is also forwarded into the `deal_transitions` FSM audit
ledger during the initial `NULL -> inbound` transition.

```python
# Lines 1827-1838 (VF-04.1/VF-04.2)
await conn.execute(
    """
    INSERT INTO zakops.deal_transitions (
        deal_id, from_stage, to_stage, actor_id, actor_type,
        correlation_id, reason
    ) VALUES ($1, NULL, 'inbound', $2, 'system', $3, $4)
    """,
    deal_id,
    process.processed_by or 'system',
    str(item.get('correlation_id') or ''),
    'Promoted from quarantine approval',
)
```

**Evidence:** `correlation_id` is parameter `$3`, sourced from the quarantine
item record with an empty-string fallback for `None` values.

---

## Link 4 — Outbox INSERT with UUID Fallback (lines 1856-1874)

The correlation ID is forwarded into the `zakops.outbox` table for downstream
event consumers. If the quarantine item has no correlation ID (e.g., items
created before F-8 or via direct DB insertion), a fresh UUID is generated as
fallback.

```python
# Lines 1857-1858 (UUID fallback)
# Forward original correlation_id from quarantine item (not gen_random_uuid())
outbox_correlation = item.get('correlation_id') or str(uuid.uuid4())
```

```python
# Lines 1859-1874 (outbox INSERT)
await conn.execute(
    """
    INSERT INTO zakops.outbox
        (correlation_id, aggregate_type, aggregate_id, event_type, event_data)
    VALUES ($3::uuid, 'deal', $1, 'deal_created', $2::jsonb)
    """,
    deal_id,
    json.dumps({
        'deal_id': deal_id,
        'canonical_name': canonical_name,
        'stage': 'inbound',
        'source': 'quarantine_approval',
        'quarantine_item_id': item_id,
    }),
    outbox_correlation if isinstance(outbox_correlation, str) else str(outbox_correlation),
)
```

**Evidence:**
- **UUID fallback** at line 1858: `item.get('correlation_id') or str(uuid.uuid4())`
  ensures the outbox always has a valid UUID, even when the original request
  lacked `X-Correlation-ID`.
- **Type guard** at line 1873: `isinstance(outbox_correlation, str)` handles
  both string and potential UUID object types before passing to the `$3::uuid`
  cast.
- The outbox column is typed `uuid`, so the `$3::uuid` cast guarantees
  database-level type safety.

---

## Full Chain Verification

| Step | Location | Column / Field | Source |
|------|----------|---------------|--------|
| 1. Header capture | Line 1529 | local var `correlation_id` | `X-Correlation-ID` header |
| 2. Quarantine INSERT | Lines 1587, 1603 | `quarantine_items.correlation_id` | Header capture (Link 1) |
| 3a. Deal identifiers | Line 1813 | `deals.identifiers->correlation_id` | Quarantine record |
| 3b. Transitions ledger | Line 1836 | `deal_transitions.correlation_id` | Quarantine record |
| 4. Outbox event | Lines 1858, 1862 | `outbox.correlation_id` | Quarantine record, UUID fallback |

No link in the chain drops or silently ignores the correlation ID. Every
transition either forwards the original value or applies a documented fallback.

---

## Verdict: **PASS**

The correlation ID flows end-to-end from HTTP header through quarantine storage,
deal creation metadata, FSM transition ledger, and outbox event emission. The
UUID fallback at Link 4 ensures the outbox always contains a valid correlation
ID even when the original request omitted the header.
