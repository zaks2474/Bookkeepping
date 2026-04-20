# Plans Review & Unified Implementation Strategy

Date: 2026-01-03

## Executive Summary

After analyzing both plans against the current codebase, I've identified:
- **3 critical conflicts** requiring resolution
- **5 gaps** needing additions
- **4 overlapping concerns** requiring consolidation
- **2 missing prerequisites** that must be addressed first

---

## Current State Analysis

### What Already Exists (Strong Foundation)

| Component | Status | Location |
|-----------|--------|----------|
| Action state machine | Complete | `scripts/actions/engine/store.py` |
| `EMAIL_TRIAGE.REVIEW_EMAIL` executor | Complete | `scripts/actions/executors/email_triage_review_email.py` |
| `DEAL.CREATE_FROM_EMAIL` executor | Complete | `scripts/actions/executors/deal_create_from_email.py` |
| `COMMUNICATION.DRAFT_EMAIL` executor | Exists | `scripts/actions/executors/communication_draft_email.py` |
| `COMMUNICATION.SEND_EMAIL` executor | Exists | `scripts/actions/executors/communication_send_email.py` |
| ToolGateway | Exists | `scripts/tools/gateway.py` |
| Gmail MCP manifests | Exists | `scripts/tools/manifests/gmail__*.yaml` |
| Quarantine API (basic) | Exists | `deal_lifecycle_api.py:1477-1545` |
| Runner observability | Complete | `/api/actions/runner-status`, `/api/actions/metrics` |

### What's Missing

| Gap | Plan 1 Ref | Plan 2 Ref |
|-----|-----------|-----------|
| `DEAL.ENRICH_MATERIALS` executor | Phase D | Phase D |
| Quarantine → Action queue bridge | - | Phase A |
| Name Resolution in triage | - | Phase B |
| Creation-time action validation | Phase B | - |
| Deal Lifecycle Controller | Phase E | - |

---

## Critical Issues

### Issue 1: Naming Collision (Phases A-D)

Both plans use Phase A, B, C, D with different meanings:

| Phase | Plan 1 (PROMPT2) | Plan 2 (Quarantine→Deal) |
|-------|-----------------|-------------------------|
| A | Action engine hardening | Quarantine queue API |
| B | Executor registration | Business-name-first approval |
| C | Comms loop (draft/send) | Materials at approval |
| D | Materials pipeline | Post-approval enrichment |

**Resolution**: Renumber Plan 2 as Phases Q1-Q4 (Q for Quarantine) to avoid confusion.

### Issue 2: Duplicate Deal Creation Logic

Two executors both create deals from emails:
- `EMAIL_TRIAGE.REVIEW_EMAIL` (lines 248-315 in `email_triage_review_email.py`)
- `DEAL.CREATE_FROM_EMAIL` (lines 196-248 in `deal_create_from_email.py`)

Both have overlapping but slightly different:
- Folder naming logic
- Deal registry integration
- Quarantine artifact copying

**Resolution**: Consolidate into single source of truth:
- `EMAIL_TRIAGE.REVIEW_EMAIL` becomes the approval-gated entry point
- It delegates deal creation to a shared `_create_deal_from_email()` helper
- `DEAL.CREATE_FROM_EMAIL` is deprecated or becomes an internal-only executor

### Issue 3: Quarantine Data Model Mismatch

Plan 2's quarantine API expects rich preview data:
```python
{
    "preview": {"subject", "from", "date", "body_excerpt"},
    "extracted_fields": {...},
    "attachments": [...],
    "links": [...]
}
```

Current quarantine API (`deal_lifecycle_api.py:1477-1498`) delegates to `QuarantineManager` which returns raw JSON items without this structure.

**Resolution**: Plan 2 Phase Q1 must define the quarantine→action bridge that surfaces `EMAIL_TRIAGE.REVIEW_EMAIL` actions with status=`PENDING_APPROVAL` as the canonical quarantine queue, not a separate quarantine store.

---

## Overlap Analysis

### Overlap 1: Post-Approval Enrichment

- **Plan 1 Phase D**: "Add/enable `DEAL.ENRICH_MATERIALS`"
- **Plan 2 Phase D**: "Add/enable `DEAL.ENRICH_MATERIALS`"

These are identical. Consolidate into single item.

### Overlap 2: Materials Persistence

- **Plan 1 Phase D1**: "Verify/close gaps for DEAL.EXTRACT_EMAIL_ARTIFACTS"
- **Plan 2 Phase C**: "Persist source email pack + attachments into deal workspace"

`email_triage_review_email.py` already does this (lines 330-389). Plan 2 Phase C is largely implemented.

### Overlap 3: Auth-Required Links Queue

- **Plan 1 Phase D2**: "Auth-required link queueing"
- **Plan 2 Phase C**: "Append links into link_intake_queue.json for auth-required"

Both reference the same mechanism. `link_intake_queue.json` already exists and is queried by `/api/enrichment/pending-links`.

### Overlap 4: Thread Routing

- **Plan 1**: Not explicitly mentioned
- **Plan 2 Phase C**: "Route subsequent emails via thread_id/in_reply_to/message_id mapping"

This is already partially implemented in `email_triage_review_email.py:308-310`:
```python
if thread_id and thread_id not in deal_obj.email_thread_ids:
    deal_obj.email_thread_ids.append(thread_id)
```

---

## Gaps Requiring New Work

### Gap 1: Quarantine-as-Action-Queue Bridge (Plan 2 Critical)

The current `/api/quarantine` returns items from `QuarantineManager`, which is a filesystem-based store. Plan 2 expects quarantine to be backed by `EMAIL_TRIAGE.REVIEW_EMAIL` actions in `PENDING_APPROVAL` state.

**Required Work**:
1. New endpoint `GET /api/actions/quarantine` that queries:
   ```sql
   SELECT * FROM actions
   WHERE type = 'EMAIL_TRIAGE.REVIEW_EMAIL'
   AND status = 'PENDING_APPROVAL'
   ORDER BY created_at DESC
   ```
2. Normalize response to include `preview`, `extracted_fields`, `attachments`, `links` from `action.inputs`

### Gap 2: Name Resolution Pass (Plan 2 Phase B)

Current `EMAIL_TRIAGE.REVIEW_EMAIL` executor uses `_infer_deal_name()` which is basic:
```python
def _infer_deal_name(payload: ActionPayload) -> str:
    subject = str((payload.inputs or {}).get("subject") or "").strip()
    company = str((payload.inputs or {}).get("company") or "").strip()
    base = company or subject or payload.title or "Deal"
    ...
```

**Required Work**:
1. Integrate existing `NameResolver` from enrichment pipeline
2. Add `inputs.inferred_company_name` to triage output
3. Update folder naming to use company name, not subject

### Gap 3: Creation-Time Action Validation (Plan 1 Phase B)

`POST /api/actions` currently accepts any `action_type`. No validation that executor exists.

**Required Work**:
1. Add validation in `create_kinetic_action()` before `store.create_action()`
2. Return `400` with structured error for unknown executors
3. Add debug endpoints `/api/actions/debug/missing-executors`

### Gap 4: `DEAL.ENRICH_MATERIALS` Executor (Both Plans)

No executor file exists: `grep` returned no matches for `DEAL.ENRICH_MATERIALS`.

**Required Work**:
1. Create `scripts/actions/executors/deal_enrich_materials.py`
2. Create `scripts/actions/capabilities/deal.enrich_materials.v1.yaml`
3. Register in `scripts/actions/executors/registry.py`

### Gap 5: Deal Lifecycle Controller (Plan 1 Phase E)

No controller loop exists. This is a P2 item but needs architecture defined.

**Required Work**:
1. Create `scripts/deal_lifecycle_controller.py`
2. Systemd timer definition
3. Idempotency key generation for proposals
4. Rule definitions (NDA, financials, unanswered emails)

---

## Patched Unified Plan

### Prerequisites (P0 - Do First)

**P0.0 - Inventory (Plan 1 Phase 0)**
- Deliverable: `PROMPT2_INVENTORY_AND_FINDINGS.md`
- Verify all executors are registered
- Verify all capabilities load
- Query DB for error breakdown

### Phase A - Action Engine Hardening (P0)

*(Plan 1 Phase A - unchanged)*

- A1: Tighten transition invariants with tests
- A2: "Never stuck" enforcement + `POST /api/actions/{id}/unstick`
- A3: Extend `/api/actions/runner-status` with stuck_processing + error breakdown

### Phase B - Executor Registration Guarantees (P0)

*(Plan 1 Phase B - unchanged)*

- B1: Creation-time validation (reject unknown action_types)
- B2: Debug endpoints `/api/actions/debug/missing-executors`, `/api/actions/debug/capability-mismatches`
- B3: UI treatment (map blocked to FAILED + specific error codes)

### Phase Q1 - Quarantine as Action Queue (P0)

*(Plan 2 Phase A - renumbered)*

- Q1.1: New endpoint `GET /api/actions/quarantine` backed by action store
  ```python
  store.list_actions(
      action_type="EMAIL_TRIAGE.REVIEW_EMAIL",
      status="PENDING_APPROVAL"
  )
  ```
- Q1.2: Response normalization with preview fields from `action.inputs`
- Q1.3: `GET /api/actions/quarantine/{action_id}` with full detail
- Q1.4: Wire existing `/api/quarantine` to redirect or deprecate

**Acceptance**: Dashboard `/quarantine` page can render email previews from action store.

### Phase Q2 - Business-Name-First Deal Creation (P1)

*(Plan 2 Phase B - renumbered)*

- Q2.1: Add `inferred_company_name` to triage inputs (via existing enrichment NameResolver)
- Q2.2: Update `_infer_deal_name()` → `_resolve_deal_name()` with company-first logic
- Q2.3: Folder naming: `{CompanyName}-{Year}` (collision-safe suffix)
- Q2.4: Set `deal.display_name` from resolved company name

**Acceptance**: New deals have company name as primary identifier, not subject line.

### Phase C - World-class Comms Loop (P0/P1)

*(Plan 1 Phase C - unchanged)*

- C1: Gemini 2.5 for drafting with strict JSON output + artifacts
- C2: Cloud gating consistency (capability `cloud_required: true`)
- C3: Send via ToolGateway + Gmail MCP with stable artifacts
- C4: Chat "send it" determinism (no redraft if draft exists)

### Phase Q3 - Materials at Approval (P1)

*(Plan 2 Phase C - renumbered, partially implemented)*

- Q3.1: Verify source email pack persistence (already in executor)
- Q3.2: Verify attachments copied to deal workspace (already in executor)
- Q3.3: Add links to `link_intake_queue.json` for auth_required (partially exists)
- Q3.4: Thread routing for subsequent emails (partially exists - needs test coverage)

**Acceptance**: Second email to same deal routes correctly without duplicate deal creation.

### Phase D - Post-Approval Enrichment (P1)

*(Merged from both plans)*

- D1: Create `DEAL.ENRICH_MATERIALS` executor
  - Input: `deal_id`, `artifact_paths`
  - Output: enrichment results (entities, doc types, confidence scores)
  - Chain from `DEAL.CREATE_FROM_EMAIL.next_actions`
- D2: Verify `DEAL.EXTRACT_EMAIL_ARTIFACTS` executor works
- D3: Auth-required link queueing (verify `link_intake_queue.json` population)

### Phase E - Deal Lifecycle Controller (P2)

*(Plan 1 Phase E - unchanged)*

- E1: Controller architecture (hourly systemd timer)
- E2: Deterministic proposal rules (no NDA, no financials, unanswered email)
- E3: Memory + deduping with idempotency keys

---

## API Contract Summary

### New Endpoints Required

| Method | Path | Description | Phase |
|--------|------|-------------|-------|
| GET | `/api/actions/quarantine` | List EMAIL_TRIAGE.REVIEW_EMAIL PENDING_APPROVAL | Q1 |
| GET | `/api/actions/quarantine/{action_id}` | Detail with preview | Q1 |
| POST | `/api/actions/{action_id}/unstick` | Admin: force stuck→READY | A |
| GET | `/api/actions/debug/missing-executors` | List action_ids with no executor | B |
| GET | `/api/actions/debug/capability-mismatches` | List capability mismatches | B |

### Modified Endpoints

| Method | Path | Change | Phase |
|--------|------|--------|-------|
| POST | `/api/actions` | Add creation-time validation | B |
| GET | `/api/actions/runner-status` | Add stuck_processing, error_breakdown | A |

### Backwards Compatibility

- `/api/quarantine` remains functional but marked deprecated
- All existing action endpoints unchanged
- Dashboard continues to work throughout

---

## Test Plan (Unified)

### Phase A Tests
- [ ] `test_approve_invalid_transition_returns_409`
- [ ] `test_execute_invalid_transition_returns_409`
- [ ] `test_runner_releases_locks_on_exception`
- [ ] `test_watchdog_marks_timeout_as_failed`

### Phase B Tests
- [ ] `test_create_action_unknown_executor_returns_400`
- [ ] `test_create_action_capability_mismatch_returns_400`
- [ ] `test_debug_missing_executors_returns_list`

### Phase Q1 Tests
- [ ] `test_quarantine_endpoint_returns_pending_approval_triage_actions`
- [ ] `test_quarantine_detail_includes_preview_fields`

### Phase Q2 Tests
- [ ] `test_deal_name_prefers_company_over_subject`
- [ ] `test_folder_name_collision_safe`

### Phase C Tests
- [ ] `test_draft_email_produces_artifacts`
- [ ] `test_send_email_uses_tool_gateway`

### Phase D Tests
- [ ] `test_enrich_materials_executor_registered`
- [ ] `test_second_email_routes_to_existing_deal`

### Phase E Tests
- [ ] `test_controller_no_duplicate_proposals`
- [ ] `test_controller_respects_cooldown`

---

## Evidence Required at Completion

1. **Curl proofs**:
   - Create action with unknown executor → 400
   - Approve/execute lifecycle
   - Runner-status with new fields
   - Quarantine endpoint returns actions

2. **Runner logs**: Lease acquisition, heartbeat, completion

3. **Demo flow**: Quarantine → Approve → Deal Created → Enrich → Draft → Send

4. **Debug endpoint output**: Zero missing executors

5. **Test results**: All new tests pass

---

## Rollout Sequence

```
Week 1: P0.0 (Inventory) + Phase A + Phase B
Week 2: Phase Q1 + Phase C1-C2
Week 3: Phase Q2 + Phase C3-C4
Week 4: Phase Q3 + Phase D
Week N: Phase E (P2, can defer)
```

---

## Decision Points for Implementer

1. **Deprecate or redirect `/api/quarantine`?**
   - Recommend: Redirect to `/api/actions/quarantine` with deprecation header

2. **Single executor or two for deal creation?**
   - Recommend: Keep both but share `_create_deal_workspace()` helper

3. **ToolGateway default: enabled or disabled?**
   - Recommend: Disabled by default, explicit `ZAKOPS_TOOL_GATEWAY_ENABLED=true`

4. **Controller dry-run mode duration?**
   - Recommend: 2 weeks in propose-only before any auto-queueing

---

## Appendix: File Inventory

### Executors (Current)
- `communication_draft_email.py` - Exists
- `communication_send_email.py` - Exists
- `deal_create_from_email.py` - Exists
- `deal_extract_email_artifacts.py` - Exists
- `email_triage_review_email.py` - Exists
- `deal_enrich_materials.py` - **MISSING** (Phase D)

### Capabilities (Current)
- `communication.draft_email.v1.yaml` - Exists
- `communication.send_email.v1.yaml` - Exists
- `deal.create_from_email.v1.yaml` - Exists
- `deal.extract_email_artifacts.v1.yaml` - Exists
- `email_triage.review_email.v1.yaml` - Exists
- `deal.enrich_materials.v1.yaml` - **MISSING** (Phase D)

### Tool Manifests
- `gmail__send_email.yaml` - Exists
- `gmail__read_email.yaml` - Exists
- `gmail__search_emails.yaml` - Exists
