# Matrix 4: Idempotency Matrix

## Idempotency Key Generation

| Component | Before Fix | After Fix | Status |
|-----------|------------|-----------|--------|
| Key Format | `{thread}:{tool}:{hash}` (>64 chars) | SHA-256 hash only (64 chars) | ✅ FIXED |
| Key Uniqueness | Deterministic | Deterministic (SHA-256) | ✅ PASS |
| Key Restart-Safety | Deterministic | Deterministic | ✅ PASS |

## Backend Idempotency Handling

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| First transition request | Execute + record in deal_events | DB updated, event recorded | ✅ PASS |
| Retry with same key (within 24h) | Return cached result (no-op) | idempotent_hit=True returned | ✅ PASS |
| Different key, same transition | Execute (if stage changed) | Fresh execution | ✅ PASS |

## Agent-Side Idempotency

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| Same approval, same execution | Return cached | existing.success=True → cached | ✅ PASS |
| Tool execution record created before call | Claim-first pattern | ToolExecution created before invoke | ✅ PASS |

## Evidence
- `idempotency.py`: SHA-256 hash (64 chars)
- `workflow.py`: deal_events with idempotency_key column
- R1 testing confirmed idempotent behavior

## Verdict: PASS (idempotency fully implemented)
