# V-L2.15: Transition Function is Single Choke Point
**VERDICT: PARTIAL PASS**

## Evidence
### FSM path (choke point):
- `main.py:907` -- `/api/deals/{id}/archive` uses `transition_deal_state()`
- `main.py:951` -- `/api/deals/{id}/restore` uses `transition_deal_state()`

### Bypass paths:
1. **workflow.py:220** -- `UPDATE zakops.deals SET stage = $2` -- Direct stage-only update
   for the workflow transition endpoint (`POST /api/deals/{id}/transition`). This path
   does NOT use `transition_deal_state()` and does NOT update `status`. However, the
   `enforce_deal_lifecycle` trigger auto-corrects status if needed.

2. **retention/cleanup.py:343** -- `UPDATE zakops.deals SET deleted = TRUE` -- Soft-delete
   for retention cleanup. Trigger auto-corrects `status='deleted'`.

3. **main.py:683** -- General PATCH for non-lifecycle fields (display_name, company_info, etc.).

### Assessment:
The `transition_deal_state()` function is the PRIMARY choke point for archive/restore
operations. However, `workflow.py` has its own stage-transition path that bypasses the FSM.
The trigger provides defense-in-depth to catch any bypass. Not a pure single choke point,
but mitigated.
