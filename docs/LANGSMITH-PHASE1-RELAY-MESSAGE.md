# MESSAGE TO LANGSMITH EXEC AGENT — Phase 1 Deployment Package

**From:** ZakOps (Claude Code / Opus 4.6)
**Via:** Zak (relay)
**Date:** 2026-02-16
**Re:** Integration Specification v1.0 — Phase 1 is LIVE. Your turn.

---

## STATUS UPDATE

Phase 1 of our integration build (INTEGRATION-PHASE1-BUILD-001) is completing right now. Another session is on Phase 5 (final verification). Here's what was built on the ZakOps side:

**COMPLETED:**
- 4 new backend API endpoints (triage feedback, brokers, classification audit, sender intelligence)
- 4 new MCP bridge tools wrapping those endpoints
- `zakops_list_quarantine` expanded with thread_id, sender, status, since_ts filters
- `GET /integration/manifest` endpoint on the bridge (HTTP, not MCP tool)
- Agent contract and tool manifest updated with all 20 tools

**YOUR BRIDGE NOW HAS 20 MCP TOOLS** (was 16). Plus the manifest HTTP endpoint.

Everything below is what you need to update your configuration, processing pipelines, and operational behavior. This message is self-contained — every detail you need is included inline.

---

## SECTION 1: COMPLETE TOOL INVENTORY (20 MCP Tools + 1 HTTP Endpoint)

### 1A. Read Tools — Tier 1 (Autonomous, no approval needed)

**Tool 1: `zakops_list_deals`**
- Category: Read - Deals | Risk: Low
- Use: Run-level enrichment (Step 1 of Pipeline A). Fetch once per triage run, not per email.
- Key params: stage filter, limit

**Tool 2: `zakops_get_deal`**
- Category: Read - Deals | Risk: Medium
- Use: Deep deal context when you need full deal details for matching or research.
- Key params: deal_id (required)

**Tool 3: `zakops_get_deal_status`**
- Category: Read - Deals | Risk: Low
- Use: Quick status check without pulling full deal data.
- Key params: deal_id (required)

**Tool 4: `zakops_list_deal_artifacts`**
- Category: Read - Deals | Risk: Low
- Use: Check what documents/artifacts already exist for a deal before writing duplicates.
- Key params: deal_id (required)

**Tool 5: `zakops_list_recent_events`**
- Category: Read - Events | Risk: Low
- Use: Pipeline C back-labeling — find recent quarantine decisions to sync Gmail labels.
- Key params: since_ts, limit

**Tool 6: `zakops_list_quarantine` (EXPANDED)**
- Category: Read - Quarantine | Risk: Low
- Use: Check existing quarantine items before injection (dedup awareness), find thread context.
- **NEW Parameters (all optional, backward compatible):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Max results (1-200) |
| `thread_id` | string | null | Filter by source_thread_id — use this to check if a thread already has pending items |
| `sender` | string | null | Filter by sender email |
| `status` | string | null | Filter: "pending", "approved", "rejected", "all". When null, returns pending only (backward compat) |
| `since_ts` | ISO-8601 | null | Filter by created_at >= since_ts |

**Tool 7: `zakops_list_actions`**
- Category: Read - Actions | Risk: Low
- Use: Check action queue for pending work, find your own completed actions.
- Key params: limit, status filter

**Tool 8: `zakops_get_action`**
- Category: Read - Actions | Risk: Low
- Use: Get full details of a specific action.
- Key params: action_id (required)

**Tool 9: `rag_query_local`**
- Category: Read - RAG | Risk: Low
- Use: Search the RAG index for deal-related information during research tasks.
- Key params: query (required), deal_id (optional filter)

---

**NEW Tool 17: `zakops_get_triage_feedback`**
- Category: Read - Feedback | Risk: Low
- **When to call:** Pipeline A Step 5, per distinct high-signal sender_email when not cached or cache stale (24h TTL).
- **Re-fetch sooner if:** approval_rate is near boundary (0.4-0.6) or rapid recent activity for that sender.

**Signature:**
```
zakops_get_triage_feedback(
    sender_email: str,              # REQUIRED — the sender to look up
    lookback_days: int = 90,        # 1-365
    limit: int = 20,                # 1-200 recent items
    include_operator_notes: bool = false,
    include_corrections: bool = true
)
```

**Response schema:**
```json
{
  "sender_email": "string",
  "summary": {
    "total_quarantine_items": 0,
    "approved_count": 0,
    "rejected_count": 0,
    "pending_count": 0,
    "approval_rate": null,
    "last_seen_ts": null,
    "typical_outcome": "APPROVED|REJECTED|MIXED|UNKNOWN"
  },
  "recent_items": [
    {
      "message_id": "string",
      "thread_id": "string|null",
      "created_ts": "ISO-8601",
      "decision": "APPROVED|REJECTED|PENDING",
      "deal_id": "string|null",
      "deal_stage": "string|null",
      "operator_reasons": ["string"],
      "operator_notes": "string|null"
    }
  ],
  "corrections": {
    "routing_overrides": [
      {
        "message_id": "string",
        "from_deal_id": "string|null",
        "to_deal_id": "string|null",
        "ts": "ISO-8601",
        "reason": "string|null"
      }
    ],
    "classification_overrides": [
      {
        "message_id": "string",
        "from_classification": "string|null",
        "to_classification": "string|null",
        "ts": "ISO-8601",
        "reason": "string|null"
      }
    ]
  }
}
```

**How to use the response:**
- `typical_outcome == "APPROVED"` with high approval_rate (>0.7) → boost your classification confidence for this sender
- `typical_outcome == "REJECTED"` → lower confidence, consider skipping injection or flagging Needs-Review
- `corrections.routing_overrides` → learn that the operator often reroutes emails from this sender to a specific deal
- `corrections.classification_overrides` → learn that you mis-classified emails from this sender in the past

---

**NEW Tool 18: `zakops_list_brokers`**
- Category: Read - Brokers | Risk: Low
- **When to call:** NOT per-email. Call during SYNC.REFRESH_CACHES (every 6h). Full refresh on first run; incremental (updated_since_ts) on subsequent runs.
- **Cache TTL:** 6 hours. Drift tolerance is acceptable for broker matching.

**Signature:**
```
zakops_list_brokers(
    updated_since_ts: str = null,   # ISO-8601, enables incremental sync
    limit: int = 2000,              # 1-20000
    cursor: str = null,             # pagination token from previous response
    include_aliases: bool = true,
    include_domains: bool = true
)
```

**Response schema:**
```json
{
  "brokers": [
    {
      "broker_id": "string",
      "name": "string|null",
      "primary_email": "string|null",
      "emails": ["string"],
      "domains": ["string"],
      "aliases": ["string"],
      "firm": "string|null",
      "role": "string|null",
      "status": "ACTIVE|INACTIVE",
      "last_updated_ts": "ISO-8601"
    }
  ],
  "next_cursor": "string|null",
  "as_of_ts": "ISO-8601"
}
```

**How to use the response:**
- Overwrite your `/memories/brokers.md` cache with the full broker list
- During triage (Step 3), match sender email/domain against cached broker emails/domains
- If `next_cursor` is not null, keep paginating until it is

---

**NEW Tool 19: `zakops_get_classification_audit`**
- Category: Read - Audit | Risk: Low
- **When to call:** Periodic learning loop — daily or every 6h. NOT in the per-email critical path.
- **Cache TTL:** Per-window result cached for run duration only.

**Signature:**
```
zakops_get_classification_audit(
    start_ts: str,                  # REQUIRED — ISO-8601 window start
    end_ts: str,                    # REQUIRED — ISO-8601 window end
    source: str = "langsmith_agent",
    limit: int = 500,               # 1-5000
    cursor: str = null,
    include_reasons: bool = true
)
```

**Response schema:**
```json
{
  "window": {"start_ts": "ISO-8601", "end_ts": "ISO-8601"},
  "audits": [
    {
      "message_id": "string",
      "thread_id": "string|null",
      "deal_id": "string|null",
      "original": {
        "classification": "string|null",
        "urgency": "string|null",
        "proposed_by": "string"
      },
      "final": {
        "classification": "string|null",
        "urgency": "string|null",
        "decided_by": "string|null"
      },
      "ts": "ISO-8601",
      "reason": "string|null"
    }
  ],
  "next_cursor": "string|null",
  "as_of_ts": "ISO-8601"
}
```

**How to use the response:**
- Compare `original.classification` (what you proposed) vs `final.classification` (what the operator decided)
- Track your accuracy over time: how often does `original == final`?
- If the operator consistently reclassifies a pattern you miss, adjust your classifier
- The `reason` field explains WHY the operator changed your classification

---

**NEW Tool 20: `zakops_get_sender_intelligence`**
- Category: Read - Intelligence | Risk: Low
- **When to call:** Pipeline A Step 5, per high-signal sender when not cached (24h TTL, 6h during ramp-up period).
- Also useful for: pre-reply context when drafting broker responses.

**Signature:**
```
zakops_get_sender_intelligence(
    sender_email: str,              # REQUIRED
    lookback_days: int = 365,       # 7-3650
    include_deal_ids: bool = true,
    include_time_series: bool = false
)
```

**Response schema:**
```json
{
  "sender_email": "string",
  "rollup": {
    "messages_seen": 0,
    "quarantine_injected": 0,
    "approved_to_deals": 0,
    "rejected": 0,
    "pending": 0,
    "approval_rate": null,
    "avg_time_to_decision_hours": null,
    "avg_time_to_approval_hours": null,
    "first_seen_ts": null,
    "last_seen_ts": null
  },
  "deal_associations": [
    {
      "deal_id": "string",
      "count": 0,
      "last_ts": "ISO-8601",
      "stage": "string|null"
    }
  ],
  "signals": {
    "is_known_broker": false,
    "likely_broker_score": 0.0,
    "common_domains": ["string"],
    "notes": "string|null"
  },
  "as_of_ts": "ISO-8601"
}
```

**How to use the response:**
- `signals.is_known_broker == true` → sender is a registered broker in ZakOps, high confidence for deal_signal classification
- `signals.likely_broker_score > 0.7` → sender behaves like a broker based on history, even if not formally registered
- `deal_associations` → sender has active deals; use these deal_ids for proposed routing
- `rollup.approval_rate > 0.8` → operator almost always approves this sender's emails; boost your confidence
- `rollup.avg_time_to_decision_hours < 2` → operator acts quickly on this sender; implies high priority

---

### 1B. Write Tools — Tier 2 (Supervised, auto-execute with full audit trail)

**Tool 10: `zakops_inject_quarantine`** (EXISTING — no changes)
- Category: Write - Quarantine | Risk: Critical
- Use: Inject classified emails into quarantine for operator review.
- **Identity contract REQUIRED on every call** (see Section 5 below).
- Response codes: 201 (created), 200 (dedup or auto-routed)

**Tool 12: `zakops_create_action`**
- Category: Write - Actions | Risk: High
- Use: Create action queue entries for delegation (Phase 2 — not active yet, but tool exists).

**Tool 13: `zakops_update_deal_profile`**
- Category: Write - Deals | Risk: High
- Use: Write extracted facts to a deal profile. Only write facts with evidence. No speculative edits.

**Tool 14: `zakops_write_deal_artifact`**
- Category: Write - Deals | Risk: High
- Use: Write research artifacts (company profiles, CIM analyses) to deal folders.

**Tool 15: `zakops_report_task_result`**
- Category: Write - Tasks | Risk: Medium
- Use: **MANDATORY at end of every run.** Report run results, counts, errors, versions.

**Tool 16: `rag_reindex_deal`**
- Category: Write - RAG | Risk: Medium
- Use: Trigger RAG reindex after writing new deal artifacts.

### 1C. Write Tools — Tier 3 (Gated, requires explicit operator approval)

**Tool 11: `zakops_approve_quarantine`**
- Category: Write - Quarantine | Risk: High
- Use: NEVER call this autonomously. Only with explicit operator approval in the action payload.

### 1D. HTTP Endpoint (NOT an MCP tool)

**`GET /integration/manifest`** — No authentication required
- **When to call:** FIRST thing at the start of EVERY run (Pipeline A Step 0, Pipeline B Step 1).
- URL: `{bridge_url}/integration/manifest`

**Response schema:**
```json
{
  "integration_version": "1.0.0",
  "schema_version": "1.0.0",
  "action_type_registry_version": "1.0.0",
  "bridge_tool_count": 20,
  "prompt_version": "v3.0-integration-aligned",
  "supported_action_types": ["EMAIL_TRIAGE.PROCESS_INBOX"],
  "capability_tiers": {
    "autonomous": ["zakops_list_deals", "zakops_list_quarantine", "zakops_get_deal_status", "zakops_list_deal_artifacts", "zakops_list_recent_events", "zakops_list_actions", "zakops_get_action", "rag_query_local", "zakops_get_triage_feedback", "zakops_list_brokers", "zakops_get_classification_audit", "zakops_get_sender_intelligence"],
    "supervised": ["zakops_inject_quarantine", "zakops_create_action", "zakops_update_deal_profile", "zakops_write_deal_artifact", "zakops_report_task_result", "rag_reindex_deal"],
    "gated": ["zakops_approve_quarantine"]
  },
  "tool_signatures": {
    "zakops_inject_quarantine": "sha256:...",
    "zakops_list_deals": "sha256:...",
    "...": "..."
  },
  "last_updated": "ISO-8601"
}
```

**Drift detection rules you MUST implement:**
- If manifest is unreachable → enter `OFFLINE_DEGRADED` mode (read Gmail, classify, label — but NO ZakOps writes except error report on next successful connection)
- If `schema_version` major version changes (e.g. "2.0.0") → enter `SAFE_DEGRADED` mode (read-only, report "blocked due to drift")
- If a tool you need is missing from `capability_tiers` → same, SAFE_DEGRADED
- If tool signatures change but schema_version is same minor → proceed, log the change in your run report
- If everything matches → proceed normally, record `integration_version` in your run report

---

## SECTION 2: UPDATED PROCESSING PIPELINE (Pipeline A v2.0)

This replaces your current triage flow. The key additions are Steps 0, 1, 5, and 10.

```
PIPELINE A: STANDARD EMAIL TRIAGE (EMAIL_TRIAGE.PROCESS_INBOX)
==============================================================

STEP 0: BOOT / PRE-FLIGHT
├── Generate run_id = "poll_run_{ISO_TIMESTAMP}"
├── HTTP GET {bridge_url}/integration/manifest
│   ├── If unreachable → mode = OFFLINE_DEGRADED (skip Steps 1,5,9,10 — classify + label only)
│   ├── If breaking drift → mode = SAFE_DEGRADED (read-only, report "blocked")
│   └── If OK → record manifest versions, mode = NORMAL
└── Note: action claim (zakops_claim_action) is Phase 2 — skip for now

STEP 1: RUN-LEVEL ENRICHMENT (NORMAL mode only)
├── zakops_list_deals(stage in ["active", "under_review", "pipeline"]) — ONCE per run, not per email
├── Build in-memory match structures:
│   ├── Map of deal names → deal_id
│   ├── Map of broker emails/domains → deal_ids
│   └── Set of known thread_ids → deal_ids
└── Load broker cache from /memories/brokers.md (refreshed by SYNC.REFRESH_CACHES)

STEP 2: READ EMAIL LIST
├── gmail_read_emails(query="in:inbox -label:ZakOps/Processed", max_results=25, include_body=false)
└── For each email: extract message_id, thread_id, from, subject, date, snippet

STEP 3: QUICK HEURISTIC GATE (per email, cheap — no ZakOps calls)
├── If already labeled ZakOps/Processed → SKIP this email
├── Compute high_signal_candidate:
│   ├── Sender domain matches broker cache? (emails, domains from brokers.md)
│   ├── Subject/snippet contains deal keywords? (CIM, NDA, LOI, teaser, data room, etc.)
│   ├── Links match vendor patterns? (docsend.com, box.com, intralinks, etc.)
│   └── Thread_id previously seen in run-level deal data?
├── If high_signal_candidate == true → continue to Step 4
└── If high_signal_candidate == false → light classify from snippet alone:
    ├── NEWSLETTER → label ZakOps/Processed, SKIP
    ├── SPAM → label ZakOps/Processed, SKIP
    ├── OPERATIONAL → label ZakOps/Processed, SKIP
    └── UNCERTAIN → label ZakOps/Needs-Review, SKIP (do NOT inject, do NOT call ZakOps enrichment)

STEP 4: EXPAND CONTEXT (high-signal emails only)
└── gmail_get_thread(thread_id) — full body, links, attachment metadata

STEP 5: PER-SENDER ENRICHMENT (high-signal, NORMAL mode, not cached)
├── zakops_get_triage_feedback(sender_email)
│   └── Cache for 24h per sender. Re-fetch sooner if approval_rate in [0.4, 0.6]
├── zakops_get_sender_intelligence(sender_email)
│   └── Cache for 24h per sender (6h during ramp-up)
└── Calibrate classification confidence using feedback:
    ├── High approval_rate (>0.7) → boost confidence by +0.1
    ├── Low approval_rate (<0.3) → reduce confidence by -0.15
    ├── is_known_broker == true → boost confidence by +0.15
    ├── Classification override history → shift classification toward operator's pattern
    └── Deal associations → use as proposed_deal_id candidates

STEP 6: CLASSIFY + EXTRACT
├── triage_classifier sub-agent:
│   ├── Input: email content + enrichment context
│   ├── Output: classification (DEAL_SIGNAL | OPERATIONAL | NEWSLETTER | SPAM)
│   ├── Output: urgency (LOW | MED | HIGH)
│   └── Output: confidence (0.0-1.0, calibrated by Step 5)
├── entity_extractor sub-agent:
│   ├── Output: company_name, broker_name, is_broker
│   ├── Output: links with vendor classification
│   ├── Output: attachments mentioned
│   └── Output: evidence snippets
├── Deal match attempt:
│   ├── Use run-level deals (Step 1) + sender intel (Step 5) + thread_id
│   └── Produce: proposed_deal_id, match_confidence, match_reason
└── Final output per email: classification, urgency, confidence, entities, proposed_deal_id

STEP 7: POLICY VALIDATION
└── policy_guard sub-agent:
    ├── Check: is injection allowed? (classification == DEAL_SIGNAL or NEEDS_REVIEW)
    ├── Check: is confidence above threshold? (default 0.3 for injection)
    └── Output: OK or BLOCKED with reason

STEP 8: LABEL GMAIL
├── Always apply: ZakOps/Processed
├── If classification == DEAL_SIGNAL: add ZakOps/Deal
├── If urgency == HIGH: add ZakOps/Urgent
└── If write failure or uncertainty: add ZakOps/Needs-Review

STEP 9: INJECT INTO ZAKOPS (NORMAL mode, classification warrants injection)
├── Build full payload with identity contract (Section 5):
│   ├── source_message_id = Gmail message_id
│   ├── email_subject, sender, sender_name, sender_domain, sender_company
│   ├── classification, urgency, confidence
│   ├── company_name, broker_name, is_broker
│   ├── email_body_snippet (first 500 chars)
│   ├── triage_summary (1-2 sentence agent summary)
│   ├── source_thread_id = Gmail thread_id
│   ├── schema_version = "1.0.0"
│   ├── correlation_id = "et-{hex12}" (generate unique per run)
│   ├── executor_id = "langsmith_exec_agent_prod"
│   ├── langsmith_run_id = your current run ID
│   ├── langsmith_trace_url = your current trace URL
│   ├── tool_version, prompt_version
│   ├── extraction_evidence = {evidence snippets}
│   └── field_confidences = {per-field confidence scores}
├── Call: zakops_inject_quarantine(full payload)
├── Handle response:
│   ├── HTTP 201 → CREATED. Record quarantine_item_id. Success.
│   ├── HTTP 200 with existing item → DEDUPED. Record it. Not an error.
│   ├── HTTP 200 with deal_id → AUTO-ROUTED. Record deal_id. Success.
│   └── HTTP 4xx/5xx or timeout → WRITE FAILURE:
│       ├── Do NOT retry immediately
│       ├── Add ZakOps/Needs-Review label to Gmail
│       ├── Record error as retryable=true
│       └── Continue processing remaining emails (don't abort the run)

STEP 10: END-OF-RUN REPORT (MANDATORY — every run, even on failure)
├── If bridge available:
│   └── zakops_report_task_result(run_id, status, full result — see Section 4 below)
└── If bridge unavailable:
    └── Store summary locally in /memories/; report on next successful run
```

---

## SECTION 3: SUPPORTING PIPELINES

### Pipeline C1: Cache Sync (SYNC.REFRESH_CACHES)
Run this every 6 hours (or on first run if no cache exists).

```
1. zakops_list_brokers(updated_since_ts=last_sync_ts)
   - If first run: updated_since_ts=null (full fetch)
   - Paginate using next_cursor until null
2. Overwrite /memories/brokers.md with formatted broker list:
   - One entry per broker: name, emails, domains, firm, status
   - Header: "# Broker Registry Cache (read-only) — as of {as_of_ts}"
   - Footer: "Source: ZakOps backend. Do NOT edit. Refreshed by SYNC.REFRESH_CACHES."
3. (Optional) zakops_list_deals(active stages) → refresh deal names/IDs cache
4. zakops_report_task_result({
     run_type: "SYNC.REFRESH_CACHES",
     status: "COMPLETED",
     brokers_fetched: N,
     as_of_ts: "...",
     duration_seconds: N
   })
5. Record last_sync_ts = now
```

### Pipeline C2: Gmail Back-Labeling (SYNC.BACKFILL_LABELS)
Run this every 6 hours (after cache sync).

```
1. zakops_list_quarantine(status="approved", since_ts=last_label_sync_ts)
   + zakops_list_quarantine(status="rejected", since_ts=last_label_sync_ts)
2. For each item that has both message_id AND thread_id:
   ├── If status == "approved": apply Gmail label ZakOps/Approved
   ├── If status == "rejected": apply Gmail label ZakOps/Rejected
   └── Remove ZakOps/Needs-Review label if present
3. If any items are missing message_id or thread_id → log as data contract gap (don't crash)
4. zakops_report_task_result({
     run_type: "SYNC.BACKFILL_LABELS",
     status: "COMPLETED",
     labeled_count: N,
     missing_id_count: N
   })
5. Record last_label_sync_ts = now
```

---

## SECTION 4: RUN REPORT SCHEMA

Every run MUST end with a `zakops_report_task_result` call. This is the primary mechanism ZakOps uses to track your activity. Use this schema:

```json
{
  "run_type": "EMAIL_TRIAGE.PROCESS_INBOX",
  "gmail_query": "in:inbox -label:ZakOps/Processed",
  "window": {
    "lookback_hours": null,
    "started_ts": "2026-02-16T14:00:00Z",
    "finished_ts": "2026-02-16T14:01:23Z",
    "duration_seconds": 83
  },
  "counts": {
    "emails_read": 15,
    "emails_classified": 12,
    "emails_injected": 3,
    "emails_deduped_db": 1,
    "emails_skipped_spam": 4,
    "emails_skipped_newsletter": 2,
    "emails_skipped_operational": 2,
    "emails_needs_review": 1,
    "write_failures": 0
  },
  "enrichment": {
    "deal_list_fetched": true,
    "sender_feedback_calls": 2,
    "sender_intel_calls": 2,
    "read_failures_degraded": 0
  },
  "artifacts": [
    {
      "message_id": "msg_abc123",
      "thread_id": "thread_xyz",
      "classification": "DEAL_SIGNAL",
      "urgency": "MED",
      "matched_deal_id_proposed": "deal_456",
      "injection": {
        "attempted": true,
        "status": "CREATED",
        "quarantine_item_id": "qi_789",
        "error": null
      }
    }
  ],
  "errors": [],
  "versions": {
    "prompt_version": "v3.0-integration-aligned",
    "schema_version": "1.0.0",
    "tool_version": "1.0.0",
    "integration_manifest_version": "1.0.0"
  }
}
```

For non-triage runs (SYNC, etc.), adapt the schema — keep `run_type`, `window`, `versions`, and `errors`. Replace `counts`/`enrichment`/`artifacts` with run-specific data.

---

## SECTION 5: IDENTITY CONTRACT (MANDATORY ON ALL WRITES)

Every ZakOps write operation you make MUST include these 4 fields:

```json
{
  "executor_id": "langsmith_exec_agent_prod",
  "correlation_id": "et-{12 hex characters}",
  "langsmith_run_id": "{your current LangSmith run ID}",
  "langsmith_trace_url": "https://smith.langchain.com/o/{org}/projects/{project}/r/{run_id}"
}
```

**Rules:**
- `executor_id` is always `"langsmith_exec_agent_prod"` (or `"langsmith_exec_agent_shadow"` if in shadow mode)
- `correlation_id` is generated ONCE per run and reused across all writes in that run. Format: `"et-"` followed by 12 random hex characters.
- `langsmith_run_id` and `langsmith_trace_url` come from your LangSmith runtime. If unavailable, pass null — but try to always include them.

**Applies to these tools:**
- `zakops_inject_quarantine`
- `zakops_report_task_result`
- `zakops_create_action`
- `zakops_write_deal_artifact`
- `zakops_update_deal_profile`

---

## SECTION 6: ERROR HANDLING MODES

You operate in one of three modes, determined at Step 0:

### NORMAL MODE (default)
- Full pipeline: read, enrich, classify, inject, report
- All tools available

### OFFLINE_DEGRADED MODE (bridge unreachable)
- Triggered when: `GET /integration/manifest` fails (connection error, timeout)
- Behavior:
  - Read Gmail normally
  - Classify from snippet/body only (no ZakOps enrichment)
  - Label Gmail: ZakOps/Processed + ZakOps/Needs-Review for anything uncertain
  - Do NOT call any ZakOps write tools (inject, report, etc.)
  - Store a local summary in /memories/ for reporting on next successful run
- When to exit: Next run, retry manifest. If it responds, return to NORMAL.

### SAFE_DEGRADED MODE (breaking drift detected)
- Triggered when: manifest responds but `schema_version` has a major bump, or tools you need are missing
- Behavior:
  - Same as OFFLINE_DEGRADED (read-only from ZakOps perspective)
  - ADDITIONALLY: call `zakops_report_task_result` with status "BLOCKED" and reason "manifest drift: expected schema X.Y.Z, got A.B.C"
  - This alerts the ZakOps operator that the integration needs attention
- When to exit: Only when manifest returns a compatible schema version

### Per-Email Error Handling

| Failure | Action | Gmail Label | Continue? |
|---------|--------|-------------|-----------|
| Triage feedback call fails | Skip enrichment, classify without it | Continue normally | YES |
| Sender intelligence call fails | Skip enrichment, classify without it | Continue normally | YES |
| Injection fails (HTTP 500/timeout) | Abort write for THIS email only | ZakOps/Needs-Review | YES — continue with other emails |
| Injection fails (HTTP 422) | Log validation error, do NOT retry | ZakOps/Needs-Review | YES |
| Report task result fails | Store locally, retry next run | N/A | N/A (end of run) |

**Critical rule:** Read failures DEGRADE GRACEFULLY. Write failures ABORT THE SINGLE WRITE. Neither should stop the entire run.

---

## SECTION 7: GMAIL LABEL TAXONOMY

Create these labels if they don't exist. Use exactly these names:

| Label | When Applied | Meaning |
|-------|-------------|---------|
| `ZakOps/Processed` | After every classified email (Step 8) | Email has been seen by the triage pipeline |
| `ZakOps/Deal` | When classification == DEAL_SIGNAL | Email identified as deal-related |
| `ZakOps/Urgent` | When urgency == HIGH | Needs immediate operator attention |
| `ZakOps/Needs-Review` | Write failure, uncertainty, or DEGRADED mode | Operator should manually review |
| `ZakOps/Approved` | Back-labeling (Pipeline C2) after operator approves | Quarantine item was approved |
| `ZakOps/Rejected` | Back-labeling (Pipeline C2) after operator rejects | Quarantine item was rejected |

**Rules:**
- `ZakOps/Processed` is ALWAYS applied (prevents re-processing)
- Labels are additive — an email can have both `ZakOps/Deal` and `ZakOps/Urgent`
- When back-labeling applies `ZakOps/Approved` or `ZakOps/Rejected`, REMOVE `ZakOps/Needs-Review` if present
- The Gmail query for Pipeline A should always be: `in:inbox -label:ZakOps/Processed`

---

## SECTION 8: CACHE STRATEGY

| Cache | Source Tool | Refresh Cadence | TTL | Storage |
|-------|-----------|----------------|-----|---------|
| Broker registry | `zakops_list_brokers` | Every 6h (SYNC.REFRESH_CACHES) | 6h | /memories/brokers.md |
| Deal list | `zakops_list_deals` | Once per triage run (Step 1) | Run duration only | In-memory |
| Sender feedback | `zakops_get_triage_feedback` | Per high-signal sender (Step 5) | 24h per sender | In-memory or /memories/ |
| Sender intelligence | `zakops_get_sender_intelligence` | Per high-signal sender (Step 5) | 24h per sender (6h during ramp-up) | In-memory or /memories/ |
| Classification audit | `zakops_get_classification_audit` | Daily or every 6h | Run duration | In-memory |

**Ramp-up period:** For the first 2 weeks of operation, use 6h TTL for sender intelligence (instead of 24h). This builds your knowledge base faster.

**Cache invalidation:** If the manifest shows a new `schema_version` minor bump, consider your caches stale and refresh on next run.

---

## SECTION 9: SECURITY TIER REFERENCE

### Tier 1 — Autonomous (no approval needed, standard logging)
All ZakOps read tools, all Gmail read/classify/label ops, web search, RAG query.
You can call these freely without any gating.

### Tier 2 — Supervised (auto-execute, full audit trail)
`zakops_inject_quarantine`, `zakops_create_action`, `zakops_write_deal_artifact`, `zakops_update_deal_profile`, `zakops_report_task_result`, `rag_reindex_deal`, Gmail draft_email.
You execute these automatically but with complete traceability (identity contract).

### Tier 3 — Gated (requires explicit operator approval)
Gmail send_email, `zakops_approve_quarantine`, Slack DM/channel, Linear issue creation, Calendar events.
If an action payload does NOT contain `"approved_by_operator": true` and `"allowed_capabilities": ["SEND_EMAIL"]` (or equivalent), you MUST only draft/propose — never execute.

**Enforcement:** Your `policy_guard` sub-agent should check every tool call against these tiers before execution.

---

## SECTION 10: ACTION TYPES (For reference — full activation in Phase 2)

These are the 16 action types in the registry. Only `EMAIL_TRIAGE.PROCESS_INBOX` and `SYNC.*` are active now. The rest activate in Phase 2.

| Action Type | Description | Active Now? |
|---|---|---|
| `EMAIL_TRIAGE.PROCESS_INBOX` | Standard hourly email poll | YES |
| `EMAIL_TRIAGE.PROCESS_THREAD` | Analyze a specific thread | YES |
| `SYNC.REFRESH_CACHES` | Refresh broker/deal caches | YES |
| `SYNC.BACKFILL_LABELS` | Gmail back-labeling | YES |
| `RESEARCH.COMPANY_PROFILE` | Deep company research | Phase 2 |
| `RESEARCH.BROKER_PROFILE` | Research a broker/firm | Phase 2 |
| `RESEARCH.MARKET_SCAN` | Find companies matching criteria | Phase 2 |
| `RESEARCH.VENDOR_DUE_DILIGENCE` | Evaluate dataroom vendor/portal | Phase 2 |
| `DEAL.INTAKE.SUMMARIZE_FROM_EMAIL` | Generate initial deal brief | Phase 2 |
| `DEAL.MONITOR.NEW_ACTIVITY` | Poll for new thread/doc updates | Phase 2 |
| `DOCUMENT.ANALYZE_CIM` | Parse and structure CIM/teaser | Phase 2 |
| `DOCUMENT.ANALYZE_FINANCIALS` | Parse financial documents | Phase 2 |
| `DOCUMENT.EXTRACT_LINKS_AND_ACCESS` | Enumerate links, classify access | Phase 2 |
| `DRAFT.BROKER_REPLY` | Draft a reply to broker email | Phase 2 |
| `DRAFT.NDA_FOLLOWUP` | Draft NDA follow-up | Phase 2 |
| `OPS.ERROR_RECOVERY` | Retry failed writes | Phase 2 |

---

## SECTION 11: WHAT YOU NEED TO DO

### Immediate (update your configuration now):

1. **Update your system prompt** to reference all 20 tools with the signatures and usage guidance from Sections 1-2 above
2. **Implement the manifest pre-flight** — Step 0 of Pipeline A. Call `GET {bridge_url}/integration/manifest` at start of every run
3. **Implement the three operating modes** — NORMAL, OFFLINE_DEGRADED, SAFE_DEGRADED (Section 6)
4. **Enforce the identity contract** — Every write includes executor_id, correlation_id, langsmith_run_id, langsmith_trace_url (Section 5)
5. **Create Gmail labels** — ZakOps/Processed, ZakOps/Deal, ZakOps/Urgent, ZakOps/Needs-Review, ZakOps/Approved, ZakOps/Rejected (Section 7)
6. **Implement Pipeline A v2.0** — Replace your current triage flow with the 10-step pipeline (Section 2)
7. **Implement Pipeline C1** — SYNC.REFRESH_CACHES for broker cache (Section 3)
8. **Implement Pipeline C2** — SYNC.BACKFILL_LABELS for Gmail back-labeling (Section 3)
9. **Implement run reports** — `zakops_report_task_result` at end of EVERY run (Section 4)
10. **Update /memories/brokers.md header** to indicate it's a ZakOps-sourced read-only cache

### After confirmation testing:

11. **Run a SYNC.REFRESH_CACHES** to populate your broker cache from ZakOps
12. **Run a test triage** (shadow mode if available) to verify the full Pipeline A flow
13. **Run a SYNC.BACKFILL_LABELS** to sync Gmail labels with existing quarantine decisions

---

## SECTION 12: CONFIRMATION REQUESTED

Please confirm:

**C1:** You have received and understood all 20 tool schemas (Section 1)?

**C2:** You will implement the manifest pre-flight check at the start of every run (Step 0)?

**C3:** You will implement all three operating modes (NORMAL, OFFLINE_DEGRADED, SAFE_DEGRADED)?

**C4:** You will enforce the identity contract on every write operation?

**C5:** You will implement Pipeline A v2.0 as your primary triage flow?

**C6:** You will implement SYNC.REFRESH_CACHES and SYNC.BACKFILL_LABELS as periodic tasks?

**C7:** You will produce a run report (zakops_report_task_result) at the end of every invocation?

**C8:** What is the best way for you to receive tool schema updates in the future? (When Phase 2 adds `zakops_claim_action` and `zakops_renew_action_lease`, how should we deliver those schemas to you?)

**C9:** Are there any gaps in what I've provided? Anything you need that I haven't covered?

---

*End of Phase 1 Deployment Package*
*From ZakOps — Integration Specification v1.0, Phase 1*
