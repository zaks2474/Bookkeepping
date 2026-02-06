=== R2-5: Deal Transition Ledger COMPLETE ===

**Status:** PASS
**Date:** 2026-02-04

## Summary
Implemented deal transition ledger for audit trail. Every stage transition
now writes an immutable record to the `deal_transitions` table. Invalid
transitions return HTTP 422 with structured error details.

## Implementation

### 1. Ledger Table (Pre-existing)
- Table: `zakops.deal_transitions`
- Columns: id, deal_id, from_stage, to_stage, actor_id, actor_type,
           correlation_id, reason, idempotency_key, created_at

### 2. Custom Exception for 422 Response
File: `/home/zaks/zakops-backend/src/core/deals/workflow.py`

Added `InvalidStageTransitionError` exception:
```python
class InvalidStageTransitionError(Exception):
    """
    Raised when a deal stage transition is not allowed.
    R2-5: Custom exception for 422 responses instead of ValueError.
    """
    def __init__(self, current_stage: str, new_stage: str, valid_transitions: list[str]):
        self.current_stage = current_stage
        self.new_stage = new_stage
        self.valid_transitions = valid_transitions
```

### 3. Ledger Write on Transition
File: `/home/zaks/zakops-backend/src/core/deals/workflow.py`

Added INSERT into `deal_transitions` after stage UPDATE:
```python
# R2-5: Write to deal_transitions ledger for audit trail
transition_id = uuid4()
await db.execute(
    """
    INSERT INTO zakops.deal_transitions (
        id, deal_id, from_stage, to_stage, actor_id, actor_type,
        correlation_id, reason, idempotency_key, created_at
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    """,
    ...
)
```

### 4. GET Transitions Endpoint
File: `/home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py`

Added endpoint:
```python
@router.get("/{deal_id}/transitions")
async def get_transitions(deal_id: str):
    """R2-5: Get transition ledger entries for a deal."""
```

### 5. 422 Response for Invalid Transitions
Updated router to catch `InvalidStageTransitionError` and return 422:
```python
except InvalidStageTransitionError as e:
    raise HTTPException(
        status_code=422,
        detail={
            "error": "INVALID_STAGE_TRANSITION",
            "message": str(e),
            "current_stage": e.current_stage,
            "requested_stage": e.new_stage,
            "valid_transitions": e.valid_transitions
        }
    )
```

## Verification Test

```
=== R2-5 Test: Get Transitions (empty) ===
{"deal_id": "DL-0007", "transitions": [], "count": 0}

=== R2-5 Test: Perform Transition (inbound -> screening) ===
{
    "deal_id": "DL-0007",
    "from_stage": "inbound",
    "to_stage": "screening",
    "success": true,
    "timestamp": "2026-02-04T20:25:43.582603+00:00"
}

=== R2-5 Test: Check Ledger Entry ===
{
    "deal_id": "DL-0007",
    "transitions": [{
        "id": "370665a8-b751-4310-abd8-bfa14025d9be",
        "from_stage": "inbound",
        "to_stage": "screening",
        "actor_id": "system",
        "actor_type": "system",
        "correlation_id": "test-r2-5",
        "reason": "R2-5 test transition",
        "timestamp": "2026-02-04T20:25:43.582603+00:00"
    }],
    "count": 1
}

=== R2-5 Test: Invalid Transition (inbound -> closing) ===
HTTP 422:
{
    "error": "INVALID_STAGE_TRANSITION",
    "message": "Invalid transition: inbound -> closing. Valid transitions: ['screening', 'junk', 'archived']",
    "current_stage": "inbound",
    "requested_stage": "closing",
    "valid_transitions": ["screening", "junk", "archived"]
}
```

## Gates

- [x] Ledger entry created on every transition
- [x] GET /api/deals/{id}/transitions returns ledger entries
- [x] Invalid transitions return 422 (not 400)
- [x] Error response includes valid_transitions array

## Files Modified

1. `/home/zaks/zakops-backend/src/core/deals/workflow.py`
   - Added InvalidStageTransitionError exception
   - Added ledger INSERT after stage UPDATE
   - Added get_transitions() method

2. `/home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py`
   - Import InvalidStageTransitionError
   - Catch and return 422 for invalid transitions
   - Added GET /{deal_id}/transitions endpoint

## Next Steps

- R2-6: Event-driven side effects (folder scaffolding, RAG indexing)
- Wire outbox subscribers for deal.created events
