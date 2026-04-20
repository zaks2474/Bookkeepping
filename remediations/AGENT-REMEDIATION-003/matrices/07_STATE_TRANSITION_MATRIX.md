# Matrix 7: Deal Stage Transition Matrix

## Valid Transitions (from workflow.py)

| From Stage | Valid To Stages | Tested | Status |
|------------|-----------------|--------|--------|
| inbound | screening, junk, archived | inbound→screening ✓ | ✅ PASS |
| screening | qualified, junk, archived | screening→qualified ✓ | ✅ PASS |
| qualified | loi, junk, archived | qualified→loi ✓ | ✅ PASS |
| loi | diligence, qualified, junk, archived | - | ⏭️ SKIP |
| diligence | closing, loi, junk, archived | - | ⏭️ SKIP |
| closing | portfolio, diligence, junk, archived | - | ⏭️ SKIP |
| portfolio | archived | - | ⏭️ SKIP |
| junk | inbound, archived | - | ⏭️ SKIP |
| archived | (terminal) | - | ⏭️ SKIP |

## Invalid Transition Rejection

| From | To | Expected | Actual | Status |
|------|-----|----------|--------|--------|
| qualified | inbound | HTTP 400 | 400 "Invalid transition" | ✅ PASS |
| loi | inbound | HTTP 400 | 400 "Invalid transition" | ✅ PASS |

## Backend Validation Code

```python
# workflow.py:188-193
valid_transitions = STAGE_TRANSITIONS.get(current_enum, [])
if new_enum not in valid_transitions:
    raise ValueError(
        f"Invalid transition: {current_stage} -> {new_stage}. "
        f"Valid transitions: {[s.value for s in valid_transitions]}"
    )
```

## Evidence
- R1: DL-0020 qualified→loi successful
- R2: DL-0036 inbound→screening successful
- R2: DL-0037 screening→qualified successful
- R2: Invalid loi→inbound rejected with HTTP 400

## Verdict: PASS (state machine enforced at backend)
