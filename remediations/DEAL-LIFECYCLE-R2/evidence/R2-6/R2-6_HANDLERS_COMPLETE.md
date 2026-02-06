=== R2-6: Event-Driven Side Effects COMPLETE ===

**Status:** PASS
**Date:** 2026-02-04

## Summary
Implemented event-driven side effects infrastructure for deal lifecycle.
Stage transitions and deal creation now write to the outbox and trigger
registered event handlers. Handlers include stub implementations for
folder scaffolding and RAG indexing that can be filled in later.

## Implementation

### 1. Stage Transitions Write to Outbox
File: `/home/zaks/zakops-backend/src/core/deals/workflow.py`

Added outbox write after ledger entry:
```python
# R2-6: Write to outbox for reliable side-effects
if is_outbox_enabled():
    outbox = OutboxWriter()
    await outbox.write(
        correlation_id=correlation_uuid,
        event_type="deal.stage_changed",
        event_data={
            "deal_id": deal_id,
            "from_stage": current_stage,
            "to_stage": new_stage,
            ...
        },
        aggregate_type="deal",
        aggregate_id=deal_id
    )
```

### 2. Event Handlers Module
File: `/home/zaks/zakops-backend/src/core/events/handlers.py` (NEW)

Created event handler infrastructure:
- `register_handler(event_type, handler)` - Register handlers
- `dispatch_event(event_type, event_data)` - Dispatch to handlers
- Wildcard pattern support (e.g., `deal.*`)

Built-in handlers:
- `handle_deal_created` - Triggers on `deal.created`
- `handle_stage_changed` - Triggers on `deal.stage_changed`

Stub implementations for:
- `_scaffold_deal_folders` - Folder creation (FOLDER_SCAFFOLDING_ENABLED)
- `_queue_rag_index` - RAG indexing (RAG_AUTO_INDEX_ENABLED)
- `_on_enter_diligence` - Diligence stage actions
- `_on_enter_closing` - Closing stage actions
- `_on_enter_portfolio` - Portfolio stage actions

### 3. Handler Dispatch in Outbox Processor
File: `/home/zaks/zakops-backend/src/core/outbox/processor.py`

Added dispatch after event publishing:
```python
# R2-6: Dispatch to event handlers for side effects
try:
    await dispatch_event(entry["event_type"], event_data)
except Exception as handler_error:
    logger.warning(f"Event handler failed: {handler_error}")
    # Continue even if handlers fail
```

## Verification Test

```
=== R2-6 Test: Create Deal ===
POST /api/deals → {"deal_id": "DL-0008"}

outbox-worker logs:
  2026-02-04 20:31:23 - [R2-6] Processing deal.created for DL-0008

=== R2-6 Test: Stage Transition ===
POST /api/deals/DL-0006/transition → {"from_stage": "inbound", "to_stage": "screening"}

outbox-worker logs:
  2026-02-04 20:31:13 - [R2-6] Processing stage change for DL-0006: inbound -> screening

=== Outbox Entries ===
deal.stage_changed | delivered | 2026-02-04 20:31:12
deal.stage_changed | delivered | 2026-02-04 20:30:25
deal.created       | delivered | 2026-02-04 20:31:23
```

## Gates

- [x] Stage transitions write to outbox
- [x] Event handlers triggered for deal.created
- [x] Event handlers triggered for deal.stage_changed
- [x] Handler failures don't block event delivery
- [x] Stub implementations ready for folder/RAG integration

## Environment Variables

New configuration options:
- `EVENT_HANDLERS_ENABLED` (default: true) - Enable/disable handlers
- `FOLDER_SCAFFOLDING_ENABLED` (default: false) - Enable folder creation
- `RAG_AUTO_INDEX_ENABLED` (default: false) - Enable RAG indexing

## Files Modified/Created

1. `/home/zaks/zakops-backend/src/core/deals/workflow.py`
   - Added outbox import
   - Added outbox write after ledger entry in transition_stage()

2. `/home/zaks/zakops-backend/src/core/events/handlers.py` (NEW)
   - Event handler registry and dispatch
   - Built-in handlers for deal lifecycle
   - Stub implementations for side effects

3. `/home/zaks/zakops-backend/src/core/outbox/processor.py`
   - Import handlers module
   - Added dispatch_event call after publishing

## Next Steps

- Enable FOLDER_SCAFFOLDING_ENABLED and implement actual folder creation
- Enable RAG_AUTO_INDEX_ENABLED and connect to RAG service
- Add notification handlers for stakeholder alerts
- Add external system integration handlers (CRM, etc.)
