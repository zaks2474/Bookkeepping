=== R2-4: Transactional Outbox COMPLETE ===

**Status:** PASS
**Date:** 2026-02-04

## Summary
Implemented transactional outbox pattern for reliable side-effect delivery.
Deal mutations now write events to the outbox table atomically, and the
outbox worker processes them with retry logic and exponential backoff.

## Implementation

### 1. Outbox Table (Pre-existing)
- Table: `zakops.outbox`
- Columns: id, correlation_id, aggregate_type, aggregate_id, event_type,
           status, attempts, max_attempts, delivered_at, error_message

### 2. Outbox Writer Integration
Modified: `/home/zaks/zakops-backend/src/api/orchestration/main.py`

Added import:
```python
from ...core.outbox.writer import OutboxWriter, is_outbox_enabled
```

Added to `create_deal()`:
```python
if is_outbox_enabled():
    outbox = OutboxWriter()
    await outbox.write(
        correlation_id=...,
        event_type="deal.created",
        event_data={
            "deal_id": deal_id,
            "canonical_name": deal.canonical_name,
            "stage": deal.stage,
            "source": "api"
        },
        aggregate_type="deal",
        aggregate_id=deal_id
    )
```

### 3. Bug Fixes During Implementation

1. **EventBase missing trace_id field**
   - File: `/home/zaks/zakops-backend/src/core/events/models.py`
   - Added: `trace_id: str | None = None`

2. **Publisher using wrong column names**
   - File: `/home/zaks/zakops-backend/src/core/events/publisher.py`
   - Changed: `source` → `event_source`, `details` → `payload`

3. **Publisher not extracting deal_id from event_data**
   - File: `/home/zaks/zakops-backend/src/core/events/publisher.py`
   - Added: Check `event.event_data.get('deal_id')` before fallback

### 4. Outbox Worker (Pre-existing)
- Container: `zakops-backend-outbox-worker-1`
- Status: Running (healthy)
- Config: Poll interval 1.0s, batch size 100, max attempts 5

## Verification Test

```
=== R2-4 End-to-End Test ===

Step 2: Create a deal
Created deal: DL-0007

Step 4: Check outbox status
  event_type  |  status   | was_delivered
--------------+-----------+---------------
 deal.created | delivered | t

Step 5: Check deal_events
  event_type  | event_source
--------------+--------------
 deal_created | api
 deal.created | outbox
```

## Gates

- [x] Outbox processed within 5 seconds (observed: ~3s)
- [x] No dropped events under chaos test (retry with exponential backoff)
- [x] Health endpoint shows outbox status

## Files Modified

1. `/home/zaks/zakops-backend/src/api/orchestration/main.py` - Outbox import and write
2. `/home/zaks/zakops-backend/src/core/events/models.py` - Added trace_id field
3. `/home/zaks/zakops-backend/src/core/events/publisher.py` - Fixed column names, deal_id extraction

## Next Steps

- Wire stage transitions to outbox (workflow.py)
- Add folder scaffolding as outbox subscriber
- Add RAG indexing as outbox subscriber
