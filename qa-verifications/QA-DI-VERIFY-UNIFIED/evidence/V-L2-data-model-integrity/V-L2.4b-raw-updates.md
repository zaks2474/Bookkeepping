# V-L2.4b: ZERO Raw UPDATE Queries for status/stage/deleted Outside Transition Function
**VERDICT: PARTIAL PASS (with known bypass paths)**

## Evidence
Direct grep for `UPDATE.*deals.*SET.*stage|status|deleted` in Python source:

### Bypass paths found:
1. **workflow.py:220** -- `UPDATE zakops.deals SET stage = $2, updated_at = $3` -- This is the older workflow transition path. It updates stage only (not status). However, the trigger `enforce_deal_lifecycle` auto-corrects status if needed.

2. **retention/cleanup.py:343** -- `UPDATE zakops.deals SET deleted = TRUE` -- Soft-delete for junk deals past retention. This bypasses the FSM but the trigger ensures status='deleted' is set.

3. **main.py:683** -- General PATCH endpoint for deal updates (display_name, company_info, etc.). This is a field-level update, not a state transition.

4. **deal_registry.py:1033,1155** -- In-memory DealRegistry (non-DB). These modify Python object attributes, not database rows.

### Mitigation:
The `enforce_deal_lifecycle` trigger on the deals table auto-corrects impossible states at INSERT/UPDATE time, providing a safety net for any bypass path. The CHECK constraint `chk_deal_lifecycle` provides a final guard.

Raw UPDATE paths exist but are mitigated by trigger + constraint defense-in-depth.
