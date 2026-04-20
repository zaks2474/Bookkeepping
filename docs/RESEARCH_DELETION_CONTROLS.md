## Deletion Controls Research (Phase 5)

This research note describes the safe deletion semantics for the Deal + Quarantine flows and documents the chosen approach before any code changes.

### Deals

- **Storage**: `DealRegistry` persists deals under `DataRoom/.deal-registry/deal_registry.json` and exposes `DealRegistry.list_deals()`, `get_deal()`, and `create_deal()` helpers that every API and agent relies on.
- **Identifiers**: `deal_id` (format `DEAL-YYYY-NNN`) is the canonical key used by:
  * actions (`deal_id` column in the kinetic action store)
  * deal materials (filesystem folders under `00-PIPELINE/Inbound`)
  * event store (`/home/zaks/DataRoom/.deal-registry/events/<deal_id>.jsonl`)
  * registrar + planner memory
  * chat proposals + UI deep links
- **Constraints**: Hard-deleting a deal would orphan actions, materials, and event logs. The registry already tracks `deleted`, `deleted_at`, `deleted_reason`, and `deleted_by` fields plus helper methods. A soft-delete / archive style approach is the safest.
- **Recommendation**: Use the existing `mark_deal_deleted()` helper to flag a deal as deleted, remove its thread/email mappings (to prevent future email auto-routing), and keep the record for audit. Provide a complementary `restore_deal()` API to re-enable the deal and re-register its known thread IDs for future mapping. The default `/api/deals` list should omit deleted records (handled by `DealRegistry.list_deals(include_deleted=False)`).

### Quarantine

- **Representation**: Quarantine rows are `EMAIL_TRIAGE.REVIEW_EMAIL` actions in `ZAKOPS_STATE_DB` (`actions` table). The UI selects pending approvals via `status='PENDING_APPROVAL'` and filters by action type.
- **Constraints**: Deleting an action row would remove crucial audit data and strand thread mappings. The safest approach is to mark the action as hidden from quarantine (the action record stays intact, continues to participate in audits, runner logic, and thread mappings, but the UI excludes it).
- **Recommendation**: Extend the action store schema with a `hidden_from_quarantine` flag + metadata (`hidden_at`, `hidden_by`, `hidden_reason`). Update `list_actions()` to skip hidden rows when requested (default behavior) and provide explicit endpoints to mark actions hidden (single + bulk). Keep the action status unchanged (so the history shows the original state) and emit an audit event for the hiding operation.

### Conclusion

Summary of safe deletion approach:

1. **Deals**: Soft delete via `deleted` flag + `deleted_at` timestamp in the registry + new archive/restore endpoints. Default API listing excludes deleted deals; the restore path re-registers thread mappings.
2. **Quarantine**: Hide pending review actions via flags on the kinetic action store. Provide explicit delete APIs (single + bulk) and keep the action record for audit. Legacy filesystem entries remain untouched.

This research note will serve as the source of truth before implementing the endpoints above.
