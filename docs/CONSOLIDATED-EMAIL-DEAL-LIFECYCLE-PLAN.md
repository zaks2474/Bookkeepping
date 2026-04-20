# Consolidated Email → Deal Lifecycle Implementation Plan

Date: 2026-01-05

## Overview

This plan consolidates two related implementation efforts:
1. **Quarantine Decision-Point UX** — Operator approval/rejection of inbound deal-signal emails
2. **Post-Approval Deal Workspace + Progressive Materials Ingestion** — Deterministic deal identity, thread continuity, and follow-on enrichment

The plans are interdependent and must be implemented in the correct order to avoid conflicts.

---

## Architecture Principles

1. **Deterministic deal identity**: A Gmail thread maps to exactly one deal (or explicitly to "non-deal")
2. **Thread continuity**: Future emails in the same thread auto-route to the same deal without human review
3. **Append-only materials**: Each email creates a timestamped bundle; never overwrite
4. **No silent drops**: Every action ends in a terminal state with structured error on failure
5. **No cloud dependency for quarantine preview**: Summary must be local/deterministic/precomputed
6. **No automatic email sending or deletion**

---

## Phase 0: DealRegistry Thread Mapping Foundation

**Goal**: Extend DealRegistry to support explicit `thread_to_deal` and `thread_to_non_deal` mappings with backward-compatible persistence.

### 0.1 Extend DealRegistry Data Model

File: `/home/zaks/scripts/deal_registry.py`

Add new instance variables:
```python
self.thread_to_deal: Dict[str, str] = {}      # gmail_thread_id -> deal_id
self.thread_to_non_deal: Dict[str, str] = {}  # gmail_thread_id -> rejection_reason
```

Add helper methods:
```python
def get_thread_deal_mapping(self, thread_id: str) -> Optional[str]:
    """Get deal_id for a thread_id, or None if not mapped."""
    return self.thread_to_deal.get(thread_id)

def add_thread_deal_mapping(self, thread_id: str, deal_id: str) -> None:
    """Map a thread to a deal. Overwrites existing mapping."""
    self.thread_to_deal[thread_id] = deal_id

def get_thread_non_deal_mapping(self, thread_id: str) -> Optional[str]:
    """Get rejection reason if thread was marked as non-deal."""
    return self.thread_to_non_deal.get(thread_id)

def add_thread_non_deal_mapping(self, thread_id: str, reason: str) -> None:
    """Mark a thread as non-deal (rejected)."""
    self.thread_to_non_deal[thread_id] = reason

def is_thread_resolved(self, thread_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if thread has been resolved.
    Returns: (is_resolved, deal_id_or_none, non_deal_reason_or_none)
    """
    if thread_id in self.thread_to_deal:
        return (True, self.thread_to_deal[thread_id], None)
    if thread_id in self.thread_to_non_deal:
        return (True, None, self.thread_to_non_deal[thread_id])
    return (False, None, None)
```

Update `_serialize()`:
```python
return {
    # ... existing fields ...
    'email_to_deal': self.email_to_deal,
    'thread_to_deal': self.thread_to_deal,          # NEW
    'thread_to_non_deal': self.thread_to_non_deal,  # NEW
}
```

Update `_deserialize()`:
```python
self.email_to_deal = data.get('email_to_deal', {})
self.thread_to_deal = data.get('thread_to_deal', {})          # NEW
self.thread_to_non_deal = data.get('thread_to_non_deal', {})  # NEW
```

### 0.2 Migration Script for Existing Data

File: `/home/zaks/scripts/migrations/migrate_thread_mappings.py`

```python
"""
One-time migration: populate thread_to_deal from existing Deal.email_thread_ids
"""
def migrate():
    registry = DealRegistry(REGISTRY_PATH)
    migrated = 0

    for deal_id, deal in registry.deals.items():
        if deal.status not in ('active', 'inactive'):
            continue
        for thread_id in (deal.email_thread_ids or []):
            if thread_id and thread_id not in registry.thread_to_deal:
                registry.thread_to_deal[thread_id] = deal_id
                migrated += 1

    registry.save()
    print(f"Migrated {migrated} thread mappings")
```

### 0.3 Tests

- Unit test: `thread_to_deal` persists across save/load cycle
- Unit test: migration script correctly populates from `email_thread_ids`
- Regression test: existing registry files load without error (backward compat)

---

## Phase 1: Email Triage Runner Thread-Aware Routing

**Goal**: Make `run_once.py` check thread resolution BEFORE creating actions, routing known threads directly without human review.

### 1.1 Update run_once.py Action Creation Logic

File: `/home/zaks/bookkeeping/scripts/email_triage_agent/run_once.py`

Before creating `EMAIL_TRIAGE.REVIEW_EMAIL`, check thread status:

```python
# At top of process_one_message(), after getting message:
registry = DealRegistry(REGISTRY_PATH)  # Read-only load

# Check if thread is already resolved
is_resolved, existing_deal_id, non_deal_reason = registry.is_thread_resolved(message.thread_id)

if is_resolved:
    if existing_deal_id:
        # Thread maps to existing deal -> create DEAL.APPEND_EMAIL_MATERIALS (auto-approved)
        await asyncio.to_thread(
            actions.create_action,
            action_type="DEAL.APPEND_EMAIL_MATERIALS",
            title=f"Append materials to {existing_deal_id}: {message.subject[:60]}",
            summary=f"Follow-up email in existing deal thread",
            deal_id=existing_deal_id,
            capability_id="deal.append_email_materials.v1",
            risk_level="low",
            requires_human_review=False,  # Auto-approved for known threads
            idempotency_key=f"append_materials:{message.message_id}",
            inputs={
                "deal_id": existing_deal_id,
                "message_id": message.message_id,
                "thread_id": message.thread_id,
                # ... same inputs as REVIEW_EMAIL ...
            },
        )
        # Apply labels and return (no quarantine)
        return

    if non_deal_reason:
        # Thread was rejected -> auto-label as non-deal, skip quarantine
        label_ids_to_add = [label_ids["ZakOps/NonDeal"], label_ids["ZakOps/Processed"]]
        await gmail.add_labels(message_id=message.message_id, label_ids=label_ids_to_add)
        state_db.mark_processed(
            message_id=message.message_id,
            classification="NON_DEAL_THREAD",
            # ...
        )
        return

# Otherwise, create EMAIL_TRIAGE.REVIEW_EMAIL as before (requires human review)
```

### 1.2 Tests

- Test: email in thread with existing deal creates `APPEND_EMAIL_MATERIALS`
- Test: email in rejected thread is auto-labeled `ZakOps/NonDeal`
- Test: email in unknown thread creates `REVIEW_EMAIL` (existing behavior)

---

## Phase 2: REVIEW_EMAIL Executor Deal Resolution Enhancement

**Goal**: Update executor to use multi-tier matching as fallback, preventing duplicate deals.

### 2.1 Update Resolution Order

File: `/home/zaks/scripts/actions/executors/email_triage_review_email.py`

Replace current resolution logic with:

```python
def _resolve_existing_deal(
    self,
    registry: DealRegistry,
    inputs: Dict[str, Any],
    payload: ActionPayload,
) -> Optional[Tuple[str, str]]:
    """
    Resolve existing deal using multi-tier matching.
    Returns: (deal_id, folder_path) or None
    """
    message_id = str(inputs.get("message_id") or "").strip()
    thread_id = str(inputs.get("thread_id") or "").strip()

    # Tier 1: Explicit deal_id from inputs/payload
    explicit = str(inputs.get("link_deal_id") or inputs.get("deal_id") or payload.deal_id or "").strip()
    if explicit and explicit.upper() != "GLOBAL":
        deal = registry.get_deal(explicit)
        if deal and deal.folder_path:
            return (explicit, str(deal.folder_path))

    # Tier 2: message_id -> deal mapping
    if message_id:
        mapped = registry.get_email_deal_mapping(message_id)
        if mapped:
            deal = registry.get_deal(mapped)
            if deal and deal.folder_path:
                return (mapped, str(deal.folder_path))

    # Tier 3: thread_id -> deal mapping (NEW)
    if thread_id:
        mapped = registry.get_thread_deal_mapping(thread_id)
        if mapped:
            deal = registry.get_deal(mapped)
            if deal and deal.folder_path:
                return (mapped, str(deal.folder_path))

    # Tier 4: DealMatcher heuristic matching (NEW)
    from deal_registry import DealMatcher, EmailContent

    email_content = EmailContent(
        subject=str(inputs.get("subject") or ""),
        body="",  # Body not stored in action inputs for size reasons
        sender=str(inputs.get("from") or ""),
        message_id=message_id,
        thread_id=thread_id,
    )

    matcher = DealMatcher(registry)
    result = matcher.match(email_content)

    if result.matched and result.deal_id:
        deal = registry.get_deal(result.deal_id)
        if deal and deal.folder_path:
            return (result.deal_id, str(deal.folder_path))

    return None
```

### 2.2 Always Write Back Mappings on Success

At end of successful execution:

```python
# Ensure all mappings are recorded
if registry:
    if message_id:
        registry.add_email_deal_mapping(message_id, deal_id)
    if thread_id:
        registry.add_thread_deal_mapping(thread_id, deal_id)
    registry.save()
```

### 2.3 Tests

- Test: second email with same thread_id resolves to existing deal (no duplicate)
- Test: email matching company name resolves to existing deal
- Test: all mappings (message_id, thread_id) persisted on success

---

## Phase 3: DEAL.APPEND_EMAIL_MATERIALS Capability & Executor

**Goal**: Handle follow-up emails in existing deal threads without creating new deals.

### 3.1 Capability Manifest

File: `/home/zaks/scripts/actions/capabilities/deal.append_email_materials.v1.yaml`

```yaml
capability_id: deal.append_email_materials.v1
title: Append email materials to existing deal
description: >
  Adds a new correspondence bundle to an existing deal workspace.
  Used for follow-up emails in threads already linked to deals.
  Does NOT create new deals.
action_type: DEAL.APPEND_EMAIL_MATERIALS

input_schema:
  type: object
  properties:
    deal_id:
      type: string
      description: Target deal ID (required)
    message_id:
      type: string
      description: Gmail message id
    thread_id:
      type: string
      description: Gmail thread id
    quarantine_dir:
      type: string
      description: Path to quarantine directory with email content
    from:
      type: string
    to:
      type: string
    date:
      type: string
    subject:
      type: string
    links:
      type: array
    attachments:
      type: array
  required: [deal_id, message_id, subject]

output_artifacts:
  - kind: md
    extension: .md
    mime_type: text/markdown
    required: true
  - kind: json
    extension: .json
    mime_type: application/json
    required: true

risk_level: low
required_approval: false  # Auto-approved for known threads
llm_allowed: false

constraints:
  - Never create new deals
  - Never send email
  - Append-only to existing deal folder
```

### 3.2 Executor Implementation

File: `/home/zaks/scripts/actions/executors/deal_append_email_materials.py`

Core behavior:
1. Validate deal_id exists and has folder_path
2. Create correspondence bundle: `<deal>/07-Correspondence/<UTC_TIMESTAMP>_<message_id_suffix>/`
3. Write: `email.md`, `email.json`, `manifest.json`
4. Copy safe attachments from quarantine_dir
5. Write links inventory: `links.json`, `pending_auth_links.json`
6. Update deal-level aggregate: `<deal>/07-Correspondence/links.json`
7. Output `next_actions` for enrichment chain

```python
# Output next_actions for pipeline chaining
outputs = {
    "deal_id": deal_id,
    "bundle_path": str(bundle_path),
    "next_actions": [
        {
            "action_type": "DEAL.EXTRACT_EMAIL_ARTIFACTS",
            "idempotency_key": f"extract_artifacts:{message_id}",
            "inputs": {"deal_id": deal_id, "bundle_path": str(bundle_path)},
        },
        {
            "action_type": "DEAL.ENRICH_MATERIALS",
            "idempotency_key": f"enrich_materials:{message_id}",
            "inputs": {"deal_id": deal_id, "bundle_path": str(bundle_path)},
        },
    ],
}
```

### 3.3 Bundle Deduplication

Before creating bundle, check if already exists:

```python
def _bundle_exists(correspondence_dir: Path, message_id: str) -> bool:
    """Check if a bundle for this message_id already exists."""
    suffix = _clean_component(message_id)[-12:]
    for existing in correspondence_dir.iterdir():
        if existing.is_dir() and suffix in existing.name:
            manifest = existing / "manifest.json"
            if manifest.exists():
                try:
                    data = json.loads(manifest.read_text())
                    if data.get("message_id") == message_id:
                        return True
                except Exception:
                    pass
    return False
```

---

## Phase 4: EMAIL_TRIAGE.REJECT_EMAIL Capability & Executor

**Goal**: Implement rejection as a real Kinetic Action that labels emails and records thread for auto-rejection.

### 4.1 Capability Manifest

File: `/home/zaks/scripts/actions/capabilities/email_triage.reject_email.v1.yaml`

```yaml
capability_id: email_triage.reject_email.v1
title: Reject email as non-deal
description: >
  Marks an email as non-deal by applying Gmail labels and recording
  the thread for auto-rejection of future emails.
action_type: EMAIL_TRIAGE.REJECT_EMAIL

input_schema:
  type: object
  properties:
    message_id:
      type: string
      description: Gmail message id (required)
    thread_id:
      type: string
      description: Gmail thread id
    reason:
      type: string
      description: Rejection reason for audit trail
    labels_to_add:
      type: array
      items:
        type: string
      default: ["ZakOps/NonDeal"]
    labels_to_remove:
      type: array
      items:
        type: string
      default: ["ZakOps/Deal"]
  required: [message_id]

risk_level: medium
required_approval: true  # Created by frontend, auto-approved internally
cloud_required: true     # Gmail MCP calls
llm_allowed: false
```

### 4.2 Executor Implementation

File: `/home/zaks/scripts/actions/executors/email_triage_reject_email.py`

```python
class EmailTriageRejectEmailExecutor(ActionExecutor):
    action_type = "EMAIL_TRIAGE.REJECT_EMAIL"

    def execute(self, payload: ActionPayload, ctx: ExecutionContext) -> ExecutionResult:
        inputs = payload.inputs or {}
        message_id = str(inputs.get("message_id") or "").strip()
        thread_id = str(inputs.get("thread_id") or "").strip()
        reason = str(inputs.get("reason") or "operator_rejected").strip()
        labels_to_add = inputs.get("labels_to_add") or ["ZakOps/NonDeal"]
        labels_to_remove = inputs.get("labels_to_remove") or ["ZakOps/Deal"]

        if not message_id:
            raise ActionExecutionError(...)

        # 1. Apply Gmail labels via ToolGateway
        gateway = ctx.tool_gateway
        if not gateway:
            raise ActionExecutionError(
                ActionError(code="tool_gateway_unavailable", ...)
            )

        # Resolve label IDs
        label_ids_add = []
        for name in labels_to_add:
            result = gateway.invoke("gmail__get_or_create_label", {"name": name})
            label_ids_add.append(result["id"])

        label_ids_remove = []
        for name in labels_to_remove:
            try:
                result = gateway.invoke("gmail__get_or_create_label", {"name": name})
                label_ids_remove.append(result["id"])
            except Exception:
                pass  # Label doesn't exist, skip removal

        # Modify email labels
        gateway.invoke("gmail__modify_email", {
            "messageId": message_id,
            "addLabelIds": label_ids_add,
            "removeLabelIds": label_ids_remove,
        })

        # 2. Record thread as non-deal in registry
        registry = ctx.registry
        if registry and thread_id:
            registry.add_thread_non_deal_mapping(thread_id, reason)
            registry.save()

        return ExecutionResult(
            outputs={
                "message_id": message_id,
                "thread_id": thread_id,
                "reason": reason,
                "labels_added": labels_to_add,
                "labels_removed": labels_to_remove,
            },
            artifacts=[],
        )
```

### 4.3 ToolGateway Manifests for Gmail

Add to tool gateway allowlist:
- `gmail__get_or_create_label`
- `gmail__modify_email`

Update runner systemd config to include these tools.

---

## Phase 5: Quarantine Preview API

**Goal**: Add dedicated preview endpoint for quarantine UI right panel.

### 5.1 Preview Endpoint

File: `/home/zaks/scripts/deal_lifecycle_api.py`

```python
@app.get("/api/actions/quarantine/{action_id}/preview")
def get_quarantine_preview(action_id: str):
    """
    Local-only preview for quarantine decision UI.
    No cloud calls - reads from action.inputs + quarantine_dir.
    """
    store = get_kinetic_action_store()
    action = store.get_action(action_id)

    if not action or action.type != "EMAIL_TRIAGE.REVIEW_EMAIL":
        raise HTTPException(status_code=404, detail="not_a_triage_action")

    inputs = action.inputs or {}
    quarantine_dir = Path(inputs.get("quarantine_dir") or "")

    # Safety: enforce quarantine_dir is under DATAROOM_ROOT
    if quarantine_dir:
        try:
            quarantine_dir.resolve().relative_to(DATAROOM_ROOT)
        except ValueError:
            quarantine_dir = None

    # Read email body from quarantine_dir
    email_body = ""
    email_body_source = "inputs"
    if quarantine_dir and quarantine_dir.exists():
        body_path = quarantine_dir / "email_body.txt"
        if body_path.exists():
            email_body = body_path.read_text(encoding="utf-8", errors="replace")[:10000]
            email_body_source = "quarantine_dir"

    # Build summary bullets (deterministic)
    summary_bullets = _build_summary_bullets(inputs, email_body)

    # Extract fields (best-effort regex)
    extracted_fields = _extract_preview_fields(inputs, email_body)

    # Group links
    links_grouped = _group_links(inputs.get("links") or [])

    # Check thread resolution status
    registry = get_registry()
    thread_id = str(inputs.get("thread_id") or "").strip()
    existing_deal_id = None
    if thread_id:
        existing_deal_id = registry.get_thread_deal_mapping(thread_id)

    return {
        "action_id": action_id,
        "status": action.status,
        "created_at": action.created_at,
        "summary_bullets": summary_bullets,
        "extracted_fields": extracted_fields,
        "attachments": inputs.get("attachments") or [],
        "links_grouped": links_grouped,
        "email_body": {
            "snippet": email_body[:500],
            "full_text": email_body,
            "source": email_body_source,
        },
        "thread_context": {
            "thread_id": thread_id,
            "existing_deal_id": existing_deal_id,
            "has_prior_emails": existing_deal_id is not None,
        },
    }


def _build_summary_bullets(inputs: Dict, body: str) -> List[str]:
    """Generate 3-6 summary bullets from email content."""
    bullets = []

    classification = inputs.get("classification") or ""
    urgency = inputs.get("urgency") or ""
    if classification:
        bullets.append(f"Classification: {classification} ({urgency} urgency)")

    links = inputs.get("links") or []
    if links:
        link_types = set(l.get("type") for l in links if l.get("type"))
        bullets.append(f"Links detected: {', '.join(link_types) or 'generic'} ({len(links)} total)")

    attachments = inputs.get("attachments") or []
    if attachments:
        bullets.append(f"Attachments: {len(attachments)} file(s)")

    # Check for $ amounts
    import re
    amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?[KMB]?', body[:2000])
    if amounts:
        bullets.append(f"Financial amounts mentioned: {', '.join(amounts[:3])}")

    company = inputs.get("company")
    if company:
        bullets.append(f"Company/deal name: {company}")

    return bullets[:6]


def _group_links(links: List[Dict]) -> Dict[str, List[Dict]]:
    """Group links by type."""
    groups = {
        "dataroom": [],
        "cim_teaser": [],
        "nda": [],
        "financials": [],
        "calendar": [],
        "generic": [],
    }
    for link in links:
        link_type = link.get("type", "generic")
        if link_type in groups:
            groups[link_type].append(link)
        else:
            groups["generic"].append(link)
    return {k: v for k, v in groups.items() if v}
```

---

## Phase 6: Actions Runner next_actions Support

**Goal**: After action completes, auto-enqueue follow-on actions from `outputs.next_actions[]`.

### 6.1 Runner Enhancement

File: `/home/zaks/scripts/actions_runner.py`

After `store.mark_action_completed()`, add:

```python
# Enqueue follow-on actions (pipeline chaining)
next_actions = result.outputs.get("next_actions") or []
MAX_CHAIN_DEPTH = 3

for i, next_spec in enumerate(next_actions[:5]):  # Limit to 5 follow-ons
    if not isinstance(next_spec, dict):
        continue

    action_type = next_spec.get("action_type")
    if not action_type:
        continue

    # Derive idempotency key
    base_key = next_spec.get("idempotency_key") or f"{action.action_id}:next:{i}"

    # Check chain depth
    chain_depth = int((action.inputs or {}).get("_chain_depth", 0)) + 1
    if chain_depth > MAX_CHAIN_DEPTH:
        logger.warning(f"Max chain depth exceeded for {action.action_id}, skipping next_actions")
        break

    next_inputs = dict(next_spec.get("inputs") or {})
    next_inputs["_chain_depth"] = chain_depth
    next_inputs["_parent_action_id"] = action.action_id

    try:
        store.create_action(
            action_type=action_type,
            title=next_spec.get("title") or f"Follow-on: {action_type}",
            summary=next_spec.get("summary") or "",
            deal_id=action.deal_id,
            capability_id=next_spec.get("capability_id") or "",
            risk_level=next_spec.get("risk_level") or "low",
            requires_human_review=next_spec.get("requires_human_review", False),
            idempotency_key=base_key,
            inputs=next_inputs,
        )
    except Exception as e:
        if "duplicate" not in str(e).lower():
            logger.exception(f"Failed to enqueue next_action: {action_type}")
```

### 6.2 next_actions Schema

```python
# In outputs
"next_actions": [
    {
        "action_type": "DEAL.ENRICH_MATERIALS",      # Required
        "idempotency_key": "enrich:msg123",          # Required for dedup
        "title": "Enrich deal materials",            # Optional
        "summary": "",                                # Optional
        "capability_id": "deal.enrich_materials.v1", # Optional
        "risk_level": "low",                         # Optional, default "low"
        "requires_human_review": False,              # Optional, default False
        "inputs": {...},                             # Optional
    }
]
```

---

## Phase 7: Frontend Quarantine Decision UI

**Goal**: Transform `/quarantine` into a 2-panel decision UI with Approve/Reject actions.

### 7.1 API Client Methods

File: `zakops-dashboard/src/lib/api.ts`

```typescript
export async function getQuarantineQueue(): Promise<QuarantineItem[]> {
  const res = await fetch(`${API_BASE}/api/actions/quarantine`);
  const data = await res.json();
  return data.items;
}

export async function getQuarantinePreview(actionId: string): Promise<QuarantinePreview> {
  const res = await fetch(`${API_BASE}/api/actions/quarantine/${actionId}/preview`);
  return res.json();
}

export async function approveQuarantineItem(actionId: string, approvedBy: string): Promise<void> {
  // 1. Approve
  await fetch(`${API_BASE}/api/actions/${actionId}/approve`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({approved_by: approvedBy}),
  });
  // 2. Request execution
  await fetch(`${API_BASE}/api/actions/${actionId}/execute`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({actor: approvedBy}),
  });
}

export async function rejectQuarantineItem(
  originalActionId: string,
  messageId: string,
  threadId: string,
  reason: string,
  rejectedBy: string,
): Promise<void> {
  // 1. Create reject action
  const res = await fetch(`${API_BASE}/api/actions`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      action_type: 'EMAIL_TRIAGE.REJECT_EMAIL',
      title: `Reject email: ${reason}`,
      summary: reason,
      capability_id: 'email_triage.reject_email.v1',
      risk_level: 'medium',
      requires_human_review: false, // Auto-approved
      idempotency_key: `reject:${messageId}`,
      inputs: {
        message_id: messageId,
        thread_id: threadId,
        reason: reason,
      },
    }),
  });
  const rejectAction = await res.json();

  // 2. Execute reject action (auto-approved)
  await fetch(`${API_BASE}/api/actions/${rejectAction.action_id}/execute`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({actor: rejectedBy}),
  });

  // 3. Cancel original review action
  await fetch(`${API_BASE}/api/actions/${originalActionId}/cancel`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({actor: rejectedBy, reason: 'rejected_as_non_deal'}),
  });
}
```

### 7.2 UI Layout

File: `zakops-dashboard/src/app/quarantine/page.tsx`

```
+------------------------------------------+
| Quarantine Queue                    [?]  |
+------------------------------------------+
| Left Panel (40%)   | Right Panel (60%)   |
| +-----------------+ +-------------------+ |
| | Subject         | | [Approve] [Reject]| |
| | From: sender    | +-------------------+ |
| | 2 hours ago     | | Summary Bullets   | |
| | MED • DEAL      | | • Classification  | |
| +-----------------+ | • Links detected  | |
| | Subject         | | • Attachments     | |
| | From: sender    | +-------------------+ |
| | 5 hours ago     | | Extracted Fields  | |
| | HIGH • DEAL     | | Company: ...      | |
| +-----------------+ | Asking: $...      | |
|                     +-------------------+ |
|                     | Links (grouped)   | |
|                     | [Dataroom] [CIM]  | |
|                     +-------------------+ |
|                     | Email Body        | |
|                     | [Expand/Collapse] | |
+------------------------------------------+
```

### 7.3 Polling & State Management

```typescript
// Poll action status after approve/reject
async function pollActionUntilTerminal(actionId: string): Promise<Action> {
  for (let i = 0; i < 30; i++) {
    const action = await getAction(actionId);
    if (['COMPLETED', 'FAILED', 'CANCELLED'].includes(action.status)) {
      return action;
    }
    await new Promise(r => setTimeout(r, 1000));
  }
  throw new Error('Action did not complete in time');
}

// On Approve success, navigate to deal
const action = await pollActionUntilTerminal(actionId);
if (action.status === 'COMPLETED' && action.outputs?.deal_id) {
  router.push(`/deals/${action.outputs.deal_id}`);
}
```

---

## Phase 8: Enrichment & RAG Reindex Actions

**Goal**: Follow-on actions for URL classification, pending-auth queue, and incremental RAG indexing.

### 8.1 DEAL.ENRICH_MATERIALS

Responsibilities:
- Classify URLs (dataroom, CIM, NDA, calendar, generic)
- Identify auth-required links
- Write `link_intake_queue.json` for auth-required links
- Optionally download public direct-links (off by default via env flag)

### 8.2 RAG.REINDEX_DEAL

Responsibilities:
- Find newly added text artifacts in deal folder
- Run secret-scan gate
- Index via rag-rest-api (reuse `index_dataroom_to_rag.py` logic)
- Track indexed artifacts to avoid re-indexing

```python
# Track indexed files
def _get_indexed_manifest(deal_path: Path) -> Set[str]:
    manifest = deal_path / ".rag_indexed_files.json"
    if manifest.exists():
        return set(json.loads(manifest.read_text()))
    return set()

def _save_indexed_manifest(deal_path: Path, indexed: Set[str]) -> None:
    manifest = deal_path / ".rag_indexed_files.json"
    manifest.write_text(json.dumps(sorted(indexed), indent=2))
```

---

## Verification Checklist

### Backend Tests

- [ ] DealRegistry: `thread_to_deal` persists and loads correctly
- [ ] DealRegistry: migration script populates from `email_thread_ids`
- [ ] run_once.py: email in known deal thread creates `APPEND_EMAIL_MATERIALS`
- [ ] run_once.py: email in rejected thread auto-labels `ZakOps/NonDeal`
- [ ] REVIEW_EMAIL executor: DealMatcher fallback prevents duplicates
- [ ] APPEND_EMAIL_MATERIALS: creates bundle without creating deal
- [ ] APPEND_EMAIL_MATERIALS: deduplication prevents duplicate bundles
- [ ] REJECT_EMAIL: applies Gmail labels via ToolGateway
- [ ] REJECT_EMAIL: records `thread_to_non_deal` mapping
- [ ] Preview endpoint: returns summary bullets, grouped links, extracted fields
- [ ] Runner: `next_actions` enqueued after completion
- [ ] Runner: max chain depth (3) enforced

### Manual E2E Verification

1. [ ] Send new deal-signal email → appears in quarantine
2. [ ] Select email → preview panel shows summary + fields + links
3. [ ] Click Approve → deal created, navigate to deal, item removed from queue
4. [ ] Reply in same thread → auto-appends to deal (no quarantine)
5. [ ] Send new email → click Reject → labeled `ZakOps/NonDeal`, item removed
6. [ ] Reply in rejected thread → auto-labeled `ZakOps/NonDeal` (no quarantine)
7. [ ] Verify enrichment actions run after approval
8. [ ] Verify RAG reindex runs for new text artifacts

---

## Rollback Plan

1. **Disable reject execution**: Remove `gmail__get_or_create_label` and `gmail__modify_email` from runner allowlist, restart `kinetic-actions-runner.service`

2. **Disable thread auto-routing**: Set `EMAIL_TRIAGE_SKIP_THREAD_CHECK=1` environment variable in runner

3. **Disable next_actions chaining**: Set `KINETIC_RUNNER_DISABLE_CHAINING=1` environment variable

4. **Keep legacy endpoints**: `/api/quarantine*` endpoints remain backward compatible

---

## Implementation Order Summary

```
Phase 0: DealRegistry thread mappings (foundation)        [1-2 days]
Phase 1: run_once.py thread-aware routing                 [1 day]
Phase 2: REVIEW_EMAIL DealMatcher enhancement             [1 day]
Phase 3: DEAL.APPEND_EMAIL_MATERIALS                      [2 days]
Phase 4: EMAIL_TRIAGE.REJECT_EMAIL                        [2 days]
Phase 5: Quarantine Preview API                           [1 day]
Phase 6: Runner next_actions support                      [1 day]
Phase 7: Frontend Quarantine UI                           [3-4 days]
Phase 8: Enrichment + RAG reindex                         [2-3 days]
```

**Critical path**: Phases 0-4 must be completed before Phase 7 frontend work can be fully tested.
