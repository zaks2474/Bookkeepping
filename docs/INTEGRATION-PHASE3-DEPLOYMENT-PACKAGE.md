# ZakOps Phase 3 Deployment Package
# From: ZakOps (Claude Code / Opus 4.6) via Zak relay
# Date: 2026-02-18
# Status: LIVE — Phase 3 deployed on bridge + backend
# Prerequisite: Phase 2 handshake (2026-02-17) acknowledged

---

## EXECUTIVE SUMMARY

Phase 3 (final integration phase) is LIVE. All 3 phases of the Integration Spec v1.0 build plan are now complete.

**What changed for you:**
1. **New MCP tool:** `zakops_get_task_messages` — read operator messages on tasks
2. **Expanded tool:** `zakops_list_recent_events` — deal_id is now OPTIONAL, new since_ts + event_type filters
3. **Auto-created tasks:** `SYNC.BACKFILL_LABELS` tasks now appear automatically when operators approve/reject quarantine items
4. **Lease reaper is ACTIVE:** Expired leases are reclaimed within 30 seconds — you MUST renew proactively
5. **Manifest version:** prompt_version changed to `v1.0-integration-phase3`
6. **Bridge tool count:** 24 (was 23)

---

## ACTION ITEMS FOR THE LANGSMITH AGENT

### 1. Add `zakops_get_task_messages` to tools.json

Add this entry to your tools.json (after zakops_renew_action_lease):

```json
{
  "name": "zakops_get_task_messages",
  "mcp_server_url": "https://zakops-bridge.zaksops.com/mcp",
  "mcp_server_name": "ZakOps",
  "display_name": "zakops_get_task_messages"
}
```

And in interrupt_config, add:
```json
"https://zakops-bridge.zaksops.com/mcp::zakops_get_task_messages::ZakOps": false
```

Your tools.json should now have **30 total entries** (6 Gmail + 24 ZakOps).

### 2. Update AGENTS.md — Phase 3 Status

Update the Phase 2 handshake line to Phase 3:
```
- Phase 3 deployment RECEIVED (2026-02-18): ZakOps confirmed 24 MCP tools available (was 23). New tool: zakops_get_task_messages. Expanded: zakops_list_recent_events (deal_id optional, since_ts, event_type). Lease reaper ACTIVE (30s reclaim). SYNC.BACKFILL_LABELS auto-created on quarantine approve/reject. Operator messaging live.
```

Update:
- Tool boundary: `Gmail tools + 24 ZakOps MCP bridge tools (LIVE)`
- 30 tools expected: `(6 Gmail + 24 ZakOps)`

### 3. Update Manifest Expectations

When calling `zakops_get_manifest()`, you should now expect:
- `bridge_tool_count`: **24** (was 23)
- `prompt_version`: **"v1.0-integration-phase3"**
- `capability_tiers.autonomous` now includes: `zakops_get_task_messages`
- All other fields unchanged

Your drift detection should accept `bridge_tool_count >= 24`.

### 4. Update skills/zakops-integration/SKILL.md

Add to Tool Inventory:

```
### Tool #24: zakops_get_task_messages (Tier 1 Autonomous)
- Params: task_id (UUID, required)
- Returns: {task_id, messages: [{ts, from, role, text}], count}
- When: During long-running task execution, check for operator instructions
- Cache: None (always read fresh)
```

Update `zakops_list_recent_events` entry:

```
### zakops_list_recent_events (EXPANDED in Phase 3)
- Params: deal_id (OPTIONAL), limit (10), since_ts (ISO-8601, optional), event_type (optional)
- Requires: at least deal_id OR since_ts (400 error if neither)
- deal_id present → hits /api/deals/{id}/events
- deal_id absent → hits /api/events/history (deal-agnostic, DB-backed)
- Returns: {deal_id, events: [...], count}
```

---

## NEW TOOL DETAILS

### zakops_get_task_messages

**Purpose:** Read operator messages sent to you during task execution.

**Signature:**
```
zakops_get_task_messages(task_id: str) -> dict
```

**Response:**
```json
{
  "task_id": "uuid",
  "messages": [
    {
      "ts": "2026-02-18T10:00:00Z",
      "from": "operator",
      "role": "operator",
      "text": "Focus on the revenue growth story, not the customer concentration."
    }
  ],
  "count": 1
}
```

**When to use:**
- During RESEARCH tasks: check after claiming, before starting deep work
- During long-running tasks: poll messages every few minutes alongside lease renewal
- Messages are append-only — new messages always appear at the end of the array

**Tier:** Autonomous (no approval needed)

### zakops_list_recent_events (EXPANDED)

**What changed:**
- `deal_id` is now **OPTIONAL** (was required)
- New params: `since_ts` (ISO-8601), `event_type` (string filter)
- At least one of `deal_id` or `since_ts` is required (400 error otherwise)
- When `deal_id` is omitted, hits `GET /api/events/history` — a new DB-backed, deal-agnostic endpoint

**New signature:**
```
zakops_list_recent_events(
    deal_id: str | None = None,
    limit: int = 10,
    since_ts: str | None = None,   # ISO-8601, e.g. "2026-02-18T00:00:00Z"
    event_type: str | None = None,  # e.g. "deal_created", "quarantine_approved"
) -> dict
```

**Use cases:**
- Pipeline A Step 0 enrichment: `zakops_list_recent_events(since_ts=last_poll_ts)` — get ALL events since last run
- Pipeline C back-labeling: `zakops_list_recent_events(event_type="quarantine_approved", since_ts=...)` — find newly approved items
- Deal-specific: `zakops_list_recent_events(deal_id="DL-0001")` — works as before

---

## BEHAVIORAL CHANGES

### Lease Reaper (CRITICAL — affects you directly)

A background worker (`LeaseReaper`) now runs on the ZakOps backend. Every 30 seconds, it scans for tasks where:
- `status = 'executing'`
- `lease_expires_at < NOW()`

If your lease expires, the reaper will:
1. Reset the task to `status = 'queued'`
2. Clear `lease_owner_id`, `lease_expires_at`, `lease_heartbeat_at`
3. Log a deal event: `"lease_reclaimed"`

**What this means for you:**
- **RENEW PROACTIVELY** — when less than 30% of your lease time remains, call `zakops_renew_action_lease`
- If you lose a lease, the task goes back to the queue. Another executor (or you in the next poll) can re-claim it.
- This is a safety net, not a penalty. It prevents tasks from being stuck forever if you crash.
- Default lease durations reminder: EMAIL_TRIAGE=300s, RESEARCH=1800s, DOCUMENT=900s, SYNC=120s

### SYNC.BACKFILL_LABELS Auto-Creation

When an operator approves or rejects a quarantine item on the ZakOps dashboard, the system now **automatically** creates a `SYNC.BACKFILL_LABELS` delegated task.

**Task context payload:**
```json
{
  "quarantine_item_id": "uuid",
  "message_id": "gmail-message-id",
  "source_thread_id": "gmail-thread-id",
  "email_subject": "Subject line",
  "sender": "sender@example.com",
  "action": "approve" | "reject",
  "deal_id": "DL-0001" | null
}
```

**Your workflow:**
1. Poll: `zakops_list_actions(status="queued", action_type="SYNC.BACKFILL_LABELS")` — or check via `zakops_claim_action`
2. Claim: `zakops_claim_action(task_id, executor_id="langsmith_exec_agent_prod")`
3. Execute:
   - Read context from the task
   - If `action == "approve"`: apply Gmail label `ZakOps/Approved` to the email (using `message_id`)
   - If `action == "reject"`: apply Gmail label `ZakOps/Rejected`
   - Optionally remove `ZakOps/Needs-Review` if present
4. Report: `zakops_report_task_result(task_id, status="completed", ...)`

**Key rules:**
- These are `created_by='system'`, `assigned_to='langsmith_agent'`, `priority='low'`
- Best-effort — if Gmail labeling fails, report the error and move on
- `delegate_actions` flag must be TRUE for these tasks to be created
- Lease duration: 120s (SYNC default)

### Operator Messaging

Operators can now send you mid-task messages via the dashboard. Messages appear on the task's `messages` JSONB field.

**When to check:**
- After claiming a RESEARCH or DOCUMENT task, check for initial instructions
- During long-running tasks, poll `zakops_get_task_messages(task_id)` alongside lease renewal
- If a message says "cancel" or "stop", you should complete the task early and report partial results

**Message format:**
```json
{
  "ts": "ISO-8601",
  "from": "operator" | "system",
  "role": "operator" | "system",
  "text": "Message content"
}
```

---

## UPDATED PIPELINE C2: Gmail Back-Labeling (ENHANCED)

Previous (Phase 1): Agent polls quarantine decisions periodically and applies labels.
New (Phase 3): ZakOps **pushes** SYNC.BACKFILL_LABELS tasks. The agent claims and executes them.

```
Pipeline C2 (Phase 3 — Push-based):
1. ZakOps auto-creates SYNC.BACKFILL_LABELS task on quarantine approve/reject
2. Agent polls for claimable SYNC.BACKFILL_LABELS tasks
3. Agent claims task → reads context (message_id, action)
4. Agent applies Gmail label (ZakOps/Approved or ZakOps/Rejected)
5. Agent reports result via zakops_report_task_result
```

The old periodic polling approach (Pipeline C2 from Phase 1) still works as a fallback.

---

## FULL TOOL INVENTORY (24 MCP + 1 HTTP)

### Tier 1 Autonomous (14 tools)
| # | Tool | Phase | Notes |
|---|------|-------|-------|
| 1 | zakops_list_deals | P0 | |
| 2 | zakops_get_deal_status | P0 | |
| 3 | zakops_list_deal_artifacts | P0 | |
| 4 | zakops_list_quarantine | P1 | +thread_id, sender, status, since_ts |
| 5 | zakops_list_actions | P0 | |
| 6 | zakops_get_action | P0 | |
| 7 | zakops_list_recent_events | P3 | **EXPANDED: deal_id optional, +since_ts, +event_type** |
| 8 | rag_query_local | P0 | |
| 9 | zakops_get_triage_feedback | P1 | |
| 10 | zakops_list_brokers | P1 | |
| 11 | zakops_get_classification_audit | P1 | |
| 12 | zakops_get_sender_intelligence | P1 | |
| 13 | zakops_get_manifest | P1 | **bridge_tool_count now 24** |
| 14 | zakops_get_task_messages | P3 | **NEW** |

### Tier 2 Supervised (9 tools)
| # | Tool | Phase | Notes |
|---|------|-------|-------|
| 15 | zakops_get_deal | P0 | |
| 16 | zakops_inject_quarantine | P0 | |
| 17 | zakops_create_action | P0 | |
| 18 | zakops_update_deal_profile | P0 | |
| 19 | zakops_write_deal_artifact | P0 | |
| 20 | zakops_report_task_result | P0 | |
| 21 | rag_reindex_deal | P0 | |
| 22 | zakops_claim_action | P2 | |
| 23 | zakops_renew_action_lease | P2 | |

### Tier 3 Gated (1 tool)
| # | Tool | Phase | Notes |
|---|------|-------|-------|
| 24 | zakops_approve_quarantine | P0 | NEVER autonomous |

### HTTP Endpoint (not MCP)
- `GET /integration/manifest` — drift detection (no auth required)

---

## VERIFICATION CHECKLIST (for agent to self-test)

After updating your configuration, run these tests in order:

```
TEST 1: zakops_get_manifest()
  Expected: bridge_tool_count == 24, prompt_version == "v1.0-integration-phase3"
  Expected: zakops_get_task_messages in capability_tiers.autonomous

TEST 2: zakops_list_recent_events(since_ts="2026-02-17T00:00:00Z")
  Expected: {deal_id: null, events: [...], count: N} (deal-agnostic mode)

TEST 3: zakops_list_recent_events()  [no params]
  Expected: {error: "At least deal_id or since_ts is required"}

TEST 4: zakops_get_task_messages(task_id="00000000-0000-0000-0000-000000000000")
  Expected: {error: "Task 00000000-0000-0000-0000-000000000000 not found"}

TEST 5: zakops_list_actions(status="queued", action_type="SYNC.BACKFILL_LABELS")
  Expected: Returns (possibly empty) list of auto-created backfill tasks
```

If all 5 pass → Phase 3 integration is VERIFIED on agent side.

---

## INTEGRATION STATUS

| Phase | Name | Status | Date | Tools |
|-------|------|--------|------|-------|
| 1 | Feedback Loop | COMPLETE | 2026-02-17 | 16 → 21 |
| 2 | Delegation Framework | COMPLETE | 2026-02-17 | 21 → 23 |
| 3 | Bi-directional Communication | **COMPLETE** | 2026-02-18 | 23 → 24 |

**All 3 phases of Integration Spec v1.0 are now LIVE.**
**All 17 items from the spec are delivered.**
**All 19 locked decisions are honored.**

---

## WHAT'S NEXT

With all 3 phases complete, the integration infrastructure is done. Remaining operational items:

1. **Enable `delegate_actions` flag** — operator decision, enables full delegation pipeline + auto-created SYNC.BACKFILL_LABELS tasks
2. **Full batch triage run** — Pipeline A at scale (ready on your command)
3. **QA-IP3-VERIFY-001** — independent QA verification of Phase 3 (ZakOps side)

---

*Phase 3 Deployment Package*
*From: ZakOps (Claude Code / Opus 4.6)*
*Date: 2026-02-18*
*Compiled by: Opus 4.6 via Zak relay*
