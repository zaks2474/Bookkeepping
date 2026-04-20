# ZakOps + LangSmith Agent Integration Specification v1.0

**Date:** 2026-02-16
**Status:** LOCKED — Architectural Agreement Complete
**Parties:** ZakOps (Claude Code / Opus 4.6) + LangSmith Exec Agent (LangSmith Agent Builder)
**Operator:** Zak (intermediary, final authority)

---

## 1. Architecture Overview

### 1.1 System Topology

```
                    LangSmith Agent Builder (Cloud)
                    ┌─────────────────────────────────┐
                    │  Exec Agent (LLM)                │
                    │  ├── triage_classifier            │
                    │  ├── entity_extractor             │
                    │  ├── policy_guard                 │
                    │  └── document_analyzer            │
                    │                                   │
                    │  /memories/ (heuristic caches)    │
                    │  Gmail MCP  │  Slack  │  Linear   │
                    └──────┬──────┴────┬────┴────┬──────┘
                           │           │         │
               ┌───────────┘           │         │
               ▼                       ▼         ▼
        ZakOps MCP Bridge (:9100)   Slack API  Linear API
               │
        ┌──────┴──────────────┐
        ▼           ▼         ▼
     Backend    RAG API    DataRoom
     (:8091)    (:8052)    Filesystem
        │
        ▼
    PostgreSQL (:5432)
    ├── zakops (deals, quarantine, actions, events)
    ├── zakops_agent (agent state)
    └── crawlrag (RAG index)
```

### 1.2 Agent Relationship: Domain Split (C)

| Agent | Domain | Runs On |
|-------|--------|---------|
| **LangSmith Exec Agent** | External-facing: Gmail, web research, doc parsing, communications | LangSmith Agent Builder (cloud) |
| **ZakOps Internal Agent** (:8095) | Deal-side automation: FSM, internal orchestration, action execution | Local (LangGraph + vLLM) |
| **Coordination Layer** | Action queue in ZakOps backend | PostgreSQL + Bridge API |

Both agents communicate through the action queue, never directly. The internal agent may create actions assigned to the LangSmith agent; the LangSmith agent reports results back through the same queue.

---

## 2. Segregation of Duties

| Responsibility | Owner | Rationale |
|---|---|---|
| Email reading & classification | **LangSmith** | Gmail access, classification sub-agents |
| Entity extraction from emails | **LangSmith** | Specialized sub-agents |
| Gmail label management | **LangSmith** | Direct Gmail tool access |
| Quarantine injection | **LangSmith** | Primary write operation |
| Web research & external data gathering | **LangSmith** | Web search, LinkedIn, URL reading tools |
| Document analysis (CIM/teaser/financials) | **LangSmith** | document_analyzer sub-agent |
| Draft email composition | **LangSmith** | Gmail draft tools (Tier 2: supervised) |
| Slack/Linear/Calendar operations | **LangSmith** | External tool ecosystem (Tier 3: gated) |
| Deal lifecycle (stages, transitions, FSM) | **ZakOps** | Database, FSM rules, operator UI |
| Quarantine approval/rejection | **ZakOps** (via human operator) | Operator decision, not agent |
| Broker registry (source of truth) | **ZakOps** | Database-backed, operator-corrected |
| Deal profile enrichment | **Shared** | LangSmith extracts, ZakOps stores/validates |
| Deal matching (email to deal) | **Shared** | LangSmith proposes match, ZakOps makes final routing |
| Sender reputation | **Shared** | LangSmith heuristic cache + ZakOps ground truth |
| Feedback loop (approval to learning) | **ZakOps to LangSmith** | ZakOps exposes decisions, LangSmith consumes |
| RAG search & indexing | **Shared** | LangSmith queries, ZakOps indexes |
| DataRoom filesystem | **ZakOps** | Filesystem structure ownership |
| Dashboard operator UI | **ZakOps** | Operator-facing, ZakOps domain |
| Action queue coordination | **ZakOps** (infrastructure) | Backend manages queue, both agents participate |

### 2.1 Source of Truth Principle

- **ZakOps = system of record** for deals, brokers, quarantine decisions, action status
- **LangSmith /memories/ = heuristic caches** — useful for fast local decisions, but never authoritative
- When cache and ZakOps disagree, ZakOps wins
- LangSmith's `brokers.md` and `deals.md` are **read-only caches** refreshed from ZakOps

---

## 3. Tool Inventory (22 Tools)

### 3.1 Existing Tools (16)

| # | Tool | Category | Risk Level |
|---|------|----------|------------|
| 1 | `zakops_list_deals` | Read - Deals | Low |
| 2 | `zakops_get_deal` | Read - Deals | Medium |
| 3 | `zakops_get_deal_status` | Read - Deals | Low |
| 4 | `zakops_list_deal_artifacts` | Read - Deals | Low |
| 5 | `zakops_list_recent_events` | Read - Events | Low |
| 6 | `zakops_list_quarantine` | Read - Quarantine | Low |
| 7 | `zakops_list_actions` | Read - Actions | Low |
| 8 | `zakops_get_action` | Read - Actions | Low |
| 9 | `rag_query_local` | Read - RAG | Low |
| 10 | `zakops_inject_quarantine` | Write - Quarantine | Critical |
| 11 | `zakops_approve_quarantine` | Write - Quarantine | High |
| 12 | `zakops_create_action` | Write - Actions | High |
| 13 | `zakops_update_deal_profile` | Write - Deals | High |
| 14 | `zakops_write_deal_artifact` | Write - Deals | High |
| 15 | `zakops_report_task_result` | Write - Tasks | Medium |
| 16 | `rag_reindex_deal` | Write - RAG | Medium |

### 3.2 New Tools — Phase 1 (6)

| # | Tool | Category | Risk Level |
|---|------|----------|------------|
| 17 | `zakops_get_triage_feedback` | Read - Feedback | Low |
| 18 | `zakops_list_brokers` | Read - Brokers | Low |
| 19 | `zakops_get_classification_audit` | Read - Audit | Low |
| 20 | `zakops_get_sender_intelligence` | Read - Intelligence | Low |
| 21 | `GET /integration/manifest` | Read - System | Low |
| — | `zakops_list_quarantine` expansion | Read - Quarantine | Low |

### 3.3 New Tools — Phase 2 (2)

| # | Tool | Category | Risk Level |
|---|------|----------|------------|
| 22 | `zakops_claim_action` | Write - Actions | Medium |
| 23 | `zakops_renew_action_lease` | Write - Actions | Medium |

### 3.4 Tool Expansion Details

**`zakops_list_quarantine` — expanded parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Max results (1-200) |
| `thread_id` | string (optional) | null | Filter by source_thread_id |
| `sender` | string (optional) | null | Filter by sender email |
| `status` | string (optional) | "pending" | Filter: pending, approved, rejected, all |
| `since_ts` | ISO-8601 (optional) | null | Filter by created_at >= since_ts |

**`zakops_list_actions` — expanded parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `assigned_to` | string (optional) | null | Filter by executor_id |
| (existing params preserved) | | | |

---

## 4. New Tool Schemas (Phase 1)

### 4.1 `zakops_get_triage_feedback`

**Signature:**
```
zakops_get_triage_feedback(
    sender_email: str,            # required
    lookback_days: int = 90,      # 1-365
    limit: int = 20,              # 1-200
    include_operator_notes: bool = false,
    include_corrections: bool = true
)
```

**Response:**
```json
{
  "sender_email": "string",
  "summary": {
    "total_quarantine_items": "int",
    "approved_count": "int",
    "rejected_count": "int",
    "pending_count": "int",
    "approval_rate": "float|null",
    "last_seen_ts": "ISO-8601|null",
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

**When called:** Pipeline Step 0 PRE-CHECK, per distinct sender_email when not cached or cache stale.
**Cache TTL:** 24 hours per sender_email. Re-fetch sooner if approval_rate near boundary (0.4-0.6) or rapid activity.

### 4.2 `zakops_list_brokers`

**Signature:**
```
zakops_list_brokers(
    updated_since_ts: str = null,   # ISO-8601, enables incremental sync
    limit: int = 2000,              # 1-20000
    cursor: str = null,             # pagination
    include_aliases: bool = true,
    include_domains: bool = true
)
```

**Response:**
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

**When called:** Cache sync step (SYNC.REFRESH_CACHES), not per-email. Full refresh every 6-24h; incremental (updated_since_ts) hourly.
**Cache TTL:** 6 hours (full refresh); drift tolerance acceptable for broker matching.

### 4.3 `zakops_get_classification_audit`

**Signature:**
```
zakops_get_classification_audit(
    window: {start_ts: str, end_ts: str},  # ISO-8601, required
    source: str = "langsmith_agent",
    limit: int = 500,                       # 1-5000
    cursor: str = null,
    include_reasons: bool = true
)
```

**Response:**
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

**When called:** Periodic learning loop (daily or every 6h). Not in per-email critical path.
**Cache TTL:** Per-window result cached for run duration only.

### 4.4 `zakops_get_sender_intelligence`

**Signature:**
```
zakops_get_sender_intelligence(
    sender_email: str,              # required
    lookback_days: int = 365,       # 7-3650
    include_deal_ids: bool = true,
    include_time_series: bool = false
)
```

**Response:**
```json
{
  "sender_email": "string",
  "rollup": {
    "messages_seen": "int",
    "quarantine_injected": "int",
    "approved_to_deals": "int",
    "rejected": "int",
    "pending": "int",
    "approval_rate": "float|null",
    "avg_time_to_decision_hours": "float|null",
    "avg_time_to_approval_hours": "float|null",
    "first_seen_ts": "ISO-8601|null",
    "last_seen_ts": "ISO-8601|null"
  },
  "deal_associations": [
    {
      "deal_id": "string",
      "count": "int",
      "last_ts": "ISO-8601",
      "stage": "string|null"
    }
  ],
  "signals": {
    "is_known_broker": "boolean",
    "likely_broker_score": "float",
    "common_domains": ["string"],
    "notes": "string|null"
  },
  "as_of_ts": "ISO-8601"
}
```

**When called:** Step 0 enrichment for broker-like senders, high-signal new senders, or pre-reply context.
**Cache TTL:** 24 hours per sender_email (6h during ramp-up).

### 4.5 Integration Manifest

**Endpoint:** `GET /integration/manifest` (no auth required)

**Response:**
```json
{
  "integration_version": "1.0.0",
  "schema_version": "1.0.0",
  "action_type_registry_version": "1.0.0",
  "bridge_tool_count": 22,
  "prompt_version": "v3.0-integration-aligned",
  "supported_action_types": ["EMAIL_TRIAGE.PROCESS_INBOX", "..."],
  "capability_tiers": {
    "autonomous": ["zakops_list_deals", "zakops_list_quarantine", "..."],
    "supervised": ["zakops_write_deal_artifact", "zakops_create_action", "..."],
    "gated": ["zakops_approve_quarantine"]
  },
  "tool_signatures": {
    "zakops_inject_quarantine": "sha256:abcdef...",
    "zakops_list_deals": "sha256:123456..."
  },
  "last_updated": "ISO-8601"
}
```

**Drift detection rules:**
- Backward-compatible additions (new tools, new optional fields): proceed, log in run report
- Breaking changes (schema_version major bump, missing tools, signature mismatch): SAFE_DEGRADED mode (read-only, no ZakOps writes except "blocked" report)

---

## 5. Action Type Registry (16 Types)

| Action Type | Description | Trigger | Expected Duration |
|---|---|---|---|
| `EMAIL_TRIAGE.PROCESS_INBOX` | Standard hourly email poll | Scheduler | 10-90s |
| `EMAIL_TRIAGE.PROCESS_THREAD` | Analyze a specific thread | Operator/auto | 5-30s |
| `RESEARCH.COMPANY_PROFILE` | Deep company research | Operator | 3-30 min |
| `RESEARCH.BROKER_PROFILE` | Research a broker/firm | Operator | 3-15 min |
| `RESEARCH.MARKET_SCAN` | Find companies matching criteria | Operator | 10-30 min |
| `RESEARCH.VENDOR_DUE_DILIGENCE` | Evaluate dataroom vendor/portal | Operator | 3-10 min |
| `DEAL.INTAKE.SUMMARIZE_FROM_EMAIL` | Generate initial deal brief | Auto (post-approval) | 10s-2 min |
| `DEAL.MONITOR.NEW_ACTIVITY` | Poll for new thread/doc updates for deal | Scheduler | 30s-5 min |
| `DOCUMENT.ANALYZE_CIM` | Parse and structure CIM/teaser | Auto/operator | 1-10 min |
| `DOCUMENT.ANALYZE_FINANCIALS` | Parse financial documents | Auto/operator | 1-10 min |
| `DOCUMENT.EXTRACT_LINKS_AND_ACCESS` | Enumerate links, classify vendor/auth, access checklist | Auto | 30s-3 min |
| `DRAFT.BROKER_REPLY` | Draft a reply to broker email | Operator | 30s-2 min |
| `DRAFT.NDA_FOLLOWUP` | Draft NDA follow-up | Operator | 30s-2 min |
| `SYNC.REFRESH_CACHES` | Refresh broker/deal/reputation caches | Scheduler (6h) | 5-30s |
| `SYNC.BACKFILL_LABELS` | Gmail back-labeling from ZakOps decisions | Scheduler | 10-60s |
| `OPS.ERROR_RECOVERY` | Retry failed writes with idempotency | Auto/manual | 5s-5 min |
| `COMMS.SLACK_DIGEST` | Prepare Slack summary (gated: approval to post) | Operator | 10-30s |

### 5.1 Default Lease Durations

| Action Category | Default Lease (seconds) |
|---|---|
| EMAIL_TRIAGE.* | 300 |
| RESEARCH.* | 1800 |
| DEAL.INTAKE.* | 300 |
| DEAL.MONITOR.* | 600 |
| DOCUMENT.* | 900 |
| DRAFT.* | 300 |
| SYNC.* | 120 |
| OPS.* | 600 |
| COMMS.* | 120 |

Lease renewal: renew when <30% lease time remains.

---

## 6. Action Payload Schemas

### 6.1 EMAIL_TRIAGE.PROCESS_INBOX

**Inputs:**
```json
{
  "gmail_query": "in:inbox -label:ZakOps/Processed",
  "max_emails": 25,
  "include_body": false,
  "lookback_hours": null,
  "label_processed": true,
  "label_namespace": "ZakOps",
  "enable_precheck_enrichment": true,
  "deal_stage_filters": ["active", "under_review", "pipeline"],
  "high_signal_gates": {
    "require_link_or_broker": false,
    "vendor_domains": []
  }
}
```

**Result:**
```json
{
  "run_type": "EMAIL_TRIAGE.PROCESS_INBOX",
  "gmail_query": "string",
  "window": {
    "lookback_hours": "int|null",
    "started_ts": "ISO-8601",
    "finished_ts": "ISO-8601",
    "duration_seconds": "int"
  },
  "counts": {
    "emails_read": "int",
    "emails_classified": "int",
    "emails_injected": "int",
    "emails_deduped_db": "int",
    "emails_skipped_spam": "int",
    "emails_skipped_newsletter": "int",
    "emails_skipped_operational": "int",
    "emails_needs_review": "int",
    "write_failures": "int"
  },
  "enrichment": {
    "deal_list_fetched": "boolean",
    "sender_feedback_calls": "int",
    "sender_intel_calls": "int",
    "read_failures_degraded": "int"
  },
  "artifacts": [
    {
      "message_id": "string",
      "thread_id": "string|null",
      "classification": "DEAL_SIGNAL|OPERATIONAL|NEWSLETTER|SPAM",
      "urgency": "LOW|MED|HIGH",
      "matched_deal_id_proposed": "string|null",
      "injection": {
        "attempted": "boolean",
        "status": "CREATED|DEDUPED|FAILED|SKIPPED",
        "quarantine_item_id": "string|null",
        "error": "string|null"
      }
    }
  ],
  "errors": [
    {
      "scope": "READ|WRITE|PIPELINE",
      "code": "string",
      "message": "string",
      "retryable": true
    }
  ],
  "versions": {
    "prompt_version": "string",
    "schema_version": "string",
    "tool_version": "string",
    "integration_manifest_version": "string|null"
  }
}
```

### 6.2 RESEARCH.COMPANY_PROFILE

**Inputs:**
```json
{
  "deal_id": "string|null",
  "company_name": "string",
  "company_domain": "string|null",
  "known_urls": [],
  "geo_focus": [],
  "industry_focus": [],
  "research_objectives": [
    "BUSINESS_OVERVIEW", "PRODUCTS_SERVICES", "CUSTOMERS_END_MARKETS",
    "OWNERSHIP_MANAGEMENT", "SIZE_SIGNALS", "NEWS_RISKS",
    "RED_FLAGS", "SOURCE_LIST"
  ],
  "depth": "STANDARD",
  "time_budget_minutes": null,
  "requires_approval": false,
  "allowed_capabilities": ["WEB_SEARCH", "READ_URL", "RAG_QUERY"]
}
```

**Artifact (company_profile.json):**
```json
{
  "company": {
    "name": "string",
    "domain": "string|null",
    "hq_location": "string|null",
    "description": "string|null",
    "industry_tags": ["string"],
    "business_model": "string|null"
  },
  "products_services": [{"name": "string", "description": "string|null"}],
  "customers_end_markets": {
    "summary": "string|null",
    "segments": ["string"],
    "concentration_risk_notes": "string|null"
  },
  "size_signals": {
    "revenue_range": "string|null",
    "employee_count_range": "string|null",
    "locations_count": "int|null",
    "notes": "string|null"
  },
  "ownership_management": {
    "ownership_summary": "string|null",
    "key_people": [{"name": "string", "title": "string|null", "linkedin_url": "string|null"}]
  },
  "recent_news": [
    {
      "title": "string",
      "publisher": "string|null",
      "date": "ISO-8601|null",
      "url": "string",
      "relevance": "HIGH|MED|LOW",
      "summary": "string|null"
    }
  ],
  "red_flags": [{"flag": "string", "severity": "HIGH|MED|LOW", "evidence": "string"}],
  "thesis_notes": {
    "why_interesting": "string|null",
    "open_questions": ["string"]
  },
  "sources": [
    {
      "url": "string",
      "source_type": "company_site|registry|news|linkedin|database|other",
      "accessed_ts": "ISO-8601",
      "notes": "string|null"
    }
  ],
  "provenance": {
    "produced_by": "langsmith_exec_agent",
    "action_id": "string",
    "deal_id": "string|null",
    "created_ts": "ISO-8601",
    "method": "web_search+url_reads",
    "confidence": "float"
  }
}
```

**Result:**
```json
{
  "run_type": "RESEARCH.COMPANY_PROFILE",
  "deal_id": "string|null",
  "company_name": "string",
  "status": "COMPLETED|PARTIAL|FAILED",
  "artifact_written": {"kind": "deal_artifact|research_artifact", "path": "string", "artifact_id": "string|null"},
  "highlights": ["string"],
  "red_flags": ["string"],
  "sources_count": "int",
  "duration_seconds": "int",
  "errors": []
}
```

### 6.3 DEAL.INTAKE.SUMMARIZE_FROM_EMAIL

**Inputs:**
```json
{
  "deal_id": "string",
  "message_id": "string",
  "thread_id": "string|null",
  "quarantine_item_id": "string|null",
  "include_thread_context": true,
  "focus": ["WHAT_IS_IT", "WHO_SENT", "KEY_LINKS", "NEXT_STEPS", "DOCS_MISSING"],
  "output_paths": {
    "deal_brief_json": "intake/deal_brief.json",
    "deal_brief_md": null
  }
}
```

**Artifact (deal_brief.json):**
```json
{
  "deal_id": "string",
  "company": {"name": "string|null", "summary": "string|null"},
  "broker": {"name": "string|null", "email": "string|null", "firm": "string|null"},
  "inbound": {
    "message_id": "string",
    "thread_id": "string|null",
    "subject": "string|null",
    "received_ts": "ISO-8601|null"
  },
  "materials": {
    "links": [
      {"type": "cim|teaser|dataroom|nda|financials|calendar|docs|other", "url": "string", "auth_required": "boolean", "vendor_hint": "string|null"}
    ],
    "attachments_mentioned": ["string"],
    "access_notes": "string|null"
  },
  "requested_actions": [{"action": "string", "owner": "operator|zakops|agent", "notes": "string|null"}],
  "open_questions": ["string"],
  "evidence": [{"snippet": "string", "source": "email", "message_id": "string"}],
  "provenance": {"produced_by": "langsmith_exec_agent", "action_id": "string", "created_ts": "ISO-8601"}
}
```

**Result:**
```json
{
  "run_type": "DEAL.INTAKE.SUMMARIZE_FROM_EMAIL",
  "deal_id": "string",
  "message_id": "string",
  "artifact_paths": ["string"],
  "duration_seconds": "int",
  "status": "COMPLETED|FAILED",
  "errors": []
}
```

### 6.4 DOCUMENT.ANALYZE_CIM

**Inputs:**
```json
{
  "deal_id": "string|null",
  "document_url": "string|null",
  "artifact_id": "string|null",
  "doc_type": "CIM",
  "access_context": {
    "auth_required": null,
    "vendor_hint": "string|null",
    "credentials_available": false
  },
  "analysis_depth": "STANDARD",
  "output_path": "docs/cim_analysis.json"
}
```

**Artifact (cim_analysis.json) — wrapper format:**
```json
{
  "deal_id": "string|null",
  "document": {"doc_type": "CIM|TEASER|OTHER", "source_url": "string|null", "artifact_id": "string|null", "fetched_ts": "ISO-8601|null"},
  "extraction": {
    "canonical_format": "document_analyzer.v1",
    "payload": {}
  },
  "key_findings": {
    "company_name": "string|null",
    "industry": "string|null",
    "geo": "string|null",
    "high_level_thesis": "string|null",
    "financials_summary": "string|null",
    "risks": ["string"],
    "questions": ["string"]
  },
  "sources": [{"url": "string|null", "artifact_id": "string|null", "notes": "string|null"}],
  "provenance": {"produced_by": "langsmith_exec_agent", "action_id": "string", "created_ts": "ISO-8601", "confidence": "float"}
}
```

**Result:**
```json
{
  "run_type": "DOCUMENT.ANALYZE_CIM",
  "deal_id": "string|null",
  "status": "COMPLETED|PARTIAL|FAILED",
  "artifact_written": {"path": "string", "artifact_id": "string|null"},
  "duration_seconds": "int",
  "errors": []
}
```

### 6.5 OPS.ERROR_RECOVERY

**Inputs:**
```json
{
  "target": {
    "failed_action_id": "string|null",
    "failed_run_id": "string|null",
    "message_ids": []
  },
  "recovery_mode": "RETRY_WRITES|REPLAY_ACTION|RECONCILE_STATE",
  "max_retries": 2,
  "backoff_seconds": 30,
  "stop_on_first_success": false,
  "safe_mode": true
}
```

**Result:**
```json
{
  "run_type": "OPS.ERROR_RECOVERY",
  "status": "COMPLETED|PARTIAL|FAILED",
  "attempts": [
    {"scope": "INJECT|ARTIFACT_WRITE|REPORT_RESULT|LABEL", "target_id": "string", "attempt": "int", "outcome": "SUCCESS|FAILED|SKIPPED", "error": "string|null"}
  ],
  "recovered": {"writes_succeeded": "int", "writes_failed": "int"},
  "duration_seconds": "int",
  "errors": []
}
```

---

## 7. Security Tiers

### 7.1 Tier Definitions

| Tier | Name | Approval | Logging |
|---|---|---|---|
| **Tier 1** | Autonomous | None | Standard |
| **Tier 2** | Supervised | None (auto-execute) | Full audit trail |
| **Tier 3** | Gated | Explicit operator approval | Full audit + approval record |

### 7.2 Tool-to-Tier Mapping

**Tier 1 — Autonomous:**
- All ZakOps read tools (list_deals, list_quarantine, get_deal_status, etc.)
- All new feedback/intelligence tools (triage_feedback, sender_intelligence, etc.)
- Gmail read, classify, extract, label
- Web search, read_url_content
- RAG query

**Tier 2 — Supervised (logged, auto-execute):**
- `zakops_inject_quarantine`
- `zakops_create_action`
- `zakops_write_deal_artifact`
- `zakops_update_deal_profile` (extracted facts + evidence only; no speculative edits)
- `zakops_report_task_result`
- `rag_reindex_deal`
- Gmail draft_email

**Tier 3 — Gated (requires explicit approval):**
- Gmail send_email
- `zakops_approve_quarantine`
- Slack messages (DM/channel)
- Linear issue creation
- Calendar create/update events

### 7.3 Enforcement

The `policy_guard` sub-agent enforces tiers using fields from the action payload:

```json
{
  "requires_approval": true|false,
  "approved_by_operator": true|false,
  "allowed_capabilities": ["SEND_EMAIL", "CREATE_CAL_EVENT", "POST_SLACK"]
}
```

If a Tier 3 action lacks explicit approval, `policy_guard` blocks execution and the agent only drafts/proposes.

---

## 8. Processing Pipelines

### 8.1 Pipeline A: Standard Hourly Poll (EMAIL_TRIAGE.PROCESS_INBOX)

```
STEP 0: BOOT / PRE-FLIGHT
├── Set run_id = action_id OR poll_run_{ISO_TS}
├── GET /integration/manifest
│   ├── If unreachable → mode = OFFLINE_DEGRADED
│   ├── If drift detected → mode = SAFE_DEGRADED (read-only)
│   └── If OK → record manifest versions
└── If action_id: zakops_claim_action(action_id, executor_id, lease_seconds=300)
    └── If claim denied → STOP

STEP 1: RUN-LEVEL ENRICHMENT (if bridge available + enrichment enabled)
├── zakops_list_deals(stage in deal_stage_filters) — once per run
└── Load in-memory match structures (deal names, broker emails/domains, thread_ids)

STEP 2: READ EMAIL LIST
├── gmail_read_emails(query, max_results, include_body=false)
└── For each message: extract message_id, thread_id, from, subject, date, snippet

STEP 3: QUICK HEURISTIC GATE (per message, cheap)
├── If already labeled ZakOps/Processed → skip
├── Compute high_signal_candidate:
│   ├── Sender domain matches known broker cache?
│   ├── Subject/snippet contains deal keywords (CIM, NDA, LOI, etc.)?
│   ├── Links match vendor patterns (docsend, box, etc.)?
│   └── Thread previously seen?
├── If high_signal_candidate → continue to Step 4
└── If NOT high_signal → light classify from snippet
    ├── NEWSLETTER/SPAM/OPERATIONAL → label + ZakOps/Processed
    ├── Do NOT call ZakOps enrichment
    ├── Do NOT inject
    └── Continue to next message

STEP 4: EXPAND CONTEXT (high-signal only)
└── gmail_get_thread(thread_id) — full body, links, attachment metadata

STEP 5: PER-SENDER ENRICHMENT (high-signal, bridge available, not cached)
├── zakops_get_triage_feedback(sender_email) — if not cached <24h
├── zakops_get_sender_intelligence(sender_email) — if not cached <24h
└── Calibrate confidence thresholds using feedback

STEP 6: CLASSIFY + EXTRACT
├── triage_classifier → classification, urgency, confidence
├── entity_extractor → company, broker, links, attachments, evidence
├── Attempt deal match using run-level deals + sender intel + thread_id
└── Produce proposed_deal_id + confidence + reason

STEP 7: POLICY VALIDATION
└── policy_guard → OK/BLOCKED with required changes

STEP 8: LABEL (Gmail)
├── Always: ZakOps/Processed
├── DEAL_SIGNAL: ZakOps/Deal
├── HIGH urgency: ZakOps/Urgent
└── Uncertainty or write failure: ZakOps/Needs-Review

STEP 9: INJECT (if DEAL_SIGNAL or NEEDS_REVIEW, bridge available)
├── zakops_inject_quarantine(full payload with identity contract)
├── Handle response:
│   ├── CREATED (201) → record quarantine_item_id
│   ├── DEDUPED (200) → record, not an error
│   ├── AUTO-ROUTED (200) → record deal_id
│   └── FAILED → WRITE FAILURE BRANCH
└── WRITE FAILURE BRANCH:
    ├── Abort ZakOps writes for this message
    ├── Label Gmail ZakOps/Needs-Review
    ├── Mark error retryable=true
    └── Continue processing other emails; run status → PARTIAL

STEP 10: END-OF-RUN REPORT
├── If bridge available:
│   └── zakops_report_task_result(run_id, status, full result schema)
└── If bridge unavailable:
    └── Keep local summary; rely on OPS.ERROR_RECOVERY next run
```

### 8.2 Pipeline B: Delegated Research (RESEARCH.COMPANY_PROFILE)

```
STEP 0: CLAIM
└── zakops_claim_action(action_id, executor_id, lease_seconds=1800)
    └── If claim denied → STOP

STEP 1: MANIFEST CHECK
└── GET /integration/manifest → if breaking drift → report failure + exit

STEP 2: EXECUTE RESEARCH
├── Use web_search, read_url_content, exa_linkedin_search (per allowed_capabilities)
├── Collect sources with timestamps and evidence snippets
├── Proactively renew lease when <30% time remains
└── Produce company_profile.json per locked schema

STEP 3: WRITE ARTIFACT
├── If deal_id present:
│   ├── zakops_write_deal_artifact(deal_id, "research/company_profile.json", content)
│   └── (optional) rag_reindex_deal(deal_id) if configured
└── If no deal_id:
    └── Write via research_id flow (Phase 2) OR report in task result

STEP 4: REPORT
└── zakops_report_task_result(action_id, status, result with artifact path + highlights)
```

### 8.3 Pipeline C: Cache Sync + Back-Labeling

```
SYNC.REFRESH_CACHES:
├── zakops_list_brokers(updated_since_ts=last_sync_ts, cursor paging)
├── Overwrite brokers.md cache (read-only)
├── (optional) zakops_list_deals(active stages) → refresh deal cache
└── zakops_report_task_result(counts + as_of_ts)

SYNC.BACKFILL_LABELS:
├── zakops_list_recent_events(since_ts=last_label_sync_ts) OR
│   zakops_list_quarantine(status in [approved,rejected], since_ts=...)
├── For each item with message_id/thread_id:
│   ├── Apply Gmail label ZakOps/Approved or ZakOps/Rejected
│   └── Remove ZakOps/Needs-Review if present
├── If missing ids → report as data contract violation
└── zakops_report_task_result(labeled_count + missing_id_count)
```

---

## 9. Error Handling Contract

| Failure Type | Behavior | Gmail Action | ZakOps Action |
|---|---|---|---|
| Bridge unreachable | OFFLINE_DEGRADED: read-only, conservative labels | Label ZakOps/Needs-Review | None (offline) |
| Manifest drift (breaking) | SAFE_DEGRADED: read-only, report "blocked" | Label ZakOps/Needs-Review | Report "blocked due to drift" |
| Read tool failure | Degrade gracefully: skip enrichment | Continue processing | Inject with deal_id=null, Needs-Review flag |
| Write tool failure (inject) | Abort write for that message | Label ZakOps/Needs-Review | Queue for retry; run status = PARTIAL |
| Write tool failure (report) | Local summary kept | None | Retry on next bridge-up run |
| Action claim denied | Stop execution | None | None (another executor owns it) |
| Lease expired mid-run | Stop writes, report partial | Label unfinished as Needs-Review | Report PARTIAL status |

---

## 10. Identity & Traceability Contract

Every ZakOps write operation MUST include:

```json
{
  "executor_id": "langsmith_exec_agent_prod",
  "correlation_id": "et-{hex12}",
  "langsmith_run_id": "run_...",
  "langsmith_trace_url": "https://smith.langchain.com/..."
}
```

**Applies to:** `zakops_inject_quarantine`, `zakops_report_task_result`, `zakops_create_action`, `zakops_write_deal_artifact`, `zakops_update_deal_profile`, `zakops_claim_action`, `zakops_renew_action_lease`.

**ZakOps commitment:** Every tool response referencing a quarantine item includes `message_id`, `source_thread_id` (if present), and `correlation_id`.

---

## 11. Cache & Sync Strategy

| Cache | Source | Refresh Cadence | TTL | Mechanism |
|---|---|---|---|---|
| brokers.md | `zakops_list_brokers` | Every 6h (SYNC.REFRESH_CACHES) | 6h | Incremental (updated_since_ts) |
| deals (in-memory) | `zakops_list_deals` | Once per poll run | Run duration | Run-level fetch |
| sender feedback | `zakops_get_triage_feedback` | Per high-signal sender | 24h per sender | Inline during Step 5 |
| sender intelligence | `zakops_get_sender_intelligence` | Per high-signal sender | 24h per sender | Inline during Step 5 |
| classification audit | `zakops_get_classification_audit` | Daily or 6h | Run duration | Periodic learning loop |
| Gmail labels (back-sync) | `zakops_list_quarantine/events` | Per SYNC.BACKFILL_LABELS run | N/A | Back-labeling pipeline |

---

## 12. Identifier Contract

| Identifier | Where Stored | Where Returned | Indexed | Purpose |
|---|---|---|---|---|
| `message_id` | quarantine_items.message_id (UNIQUE) | All quarantine responses | Yes | Dedup key, Gmail correlation |
| `source_thread_id` | quarantine_items.source_thread_id | All quarantine responses | Yes | Thread routing, Gmail back-labeling |
| `correlation_id` | quarantine_items.correlation_id | All quarantine responses | Yes | Cross-system trace linkage |
| `langsmith_run_id` | quarantine_items.langsmith_run_id | All quarantine responses | No | LangSmith trace link |
| `langsmith_trace_url` | quarantine_items.langsmith_trace_url | All quarantine responses | No | LangSmith trace URL |
| `executor_id` | action payload / raw_content | Tool responses | No | Agent identity |

---

## 13. Golden Test Suite (11 Tests)

| Test | Input | Expected Flow | Verification |
|---|---|---|---|
| **T1** | Known broker email with CIM | Classify deal_signal → extract → inject → 201 | All 31 fields in quarantine |
| **T2** | Same email re-processed | Inject → 200 dedup | No duplicate in DB |
| **T3** | Reply in existing deal thread | Inject → 200 routed with deal_id | Email linked to correct deal |
| **T4** | Email from sender with prior approvals | Triage feedback boosts confidence | Elevated confidence in injection |
| **T5** | Operator delegates RESEARCH.COMPANY_PROFILE | Action created → claimed → executed → artifact written → reported | Artifact in deal folder, action completed |
| **T6** | Bridge down during injection | Degrade → label Gmail → retry next run | Email not lost, eventually injected |
| **T7** | New broker added in ZakOps | Sync run refreshes cache | Agent matches new broker emails |
| **T8** | Inject fails (500/timeout) | Label Needs-Review → next run retries | Exactly one quarantine item, recovery in run report |
| **T9** | Two executors poll same action | Only one claims, other skips | No double execution |
| **T10** | Research artifact written | Write artifact → reindex → query RAG | Key facts retrievable via RAG |
| **T11** | Reply in thread with pending quarantine | list_quarantine(thread_id) returns pending | Agent injects with routed context or skips |

---

## 14. Build Plan

### Phase 1 — Feedback Loop (enables smart email triage)

| # | Item | Type | Dependency |
|---|---|---|---|
| 1 | `zakops_get_triage_feedback` | New bridge tool + backend endpoint | None |
| 2 | `zakops_list_brokers` | New bridge tool + backend endpoint | None |
| 3 | `zakops_get_classification_audit` | New bridge tool + backend endpoint | None |
| 4 | `zakops_get_sender_intelligence` | New bridge tool + backend endpoint | None |
| 5 | `zakops_list_quarantine` filter expansion | Bridge tool modification | None |
| 6 | `GET /integration/manifest` | New bridge endpoint | 1-5 (tool count) |
| 7 | Update `agent_contract.py` system prompt | Bridge config | 1-6 |

**Deliverable:** Updated master config v3.0 for LangSmith deployment.
**Test coverage:** T1-T4, T6-T8, T11.

### Phase 2 — Delegation Framework (enables research + external ops)

| # | Item | Type | Dependency |
|---|---|---|---|
| 8 | Action type registry (16 types) | Backend infrastructure | None |
| 9 | `zakops_claim_action` | New bridge tool | 8 |
| 10 | `zakops_renew_action_lease` | New bridge tool | 8 |
| 11 | `zakops_list_actions` assigned_to filter | Bridge tool expansion | 8 |
| 12 | `zakops_report_task_result` schema expansion | Bridge tool expansion | 8 |
| 13 | Research artifact storage (research_id flow) | Backend + bridge | 8 |
| 14 | Dashboard "Delegate to Agent" button | Frontend | 8-12 |

**Deliverable:** Full delegation round-trip working.
**Test coverage:** T5, T9, T10.

### Phase 3 — Bi-directional Communication (enables real-time collaboration)

| # | Item | Type | Dependency |
|---|---|---|---|
| 15 | Gmail back-labeling push mechanism | Action queue + bridge | Phase 2 |
| 16 | Event polling optimization (source filter) | Bridge tool expansion | Phase 1 |
| 17 | Operator-to-agent message channel | Backend + Dashboard | Phase 2 |

**Deliverable:** Full bi-directional loop.
**Test coverage:** T7 (enhanced).

---

## 15. Locked Decisions Summary

All decisions below were agreed through 6-message exchange between ZakOps and LangSmith agents, with Zak as intermediary.

1. ZakOps = system of record; LangSmith memories = heuristic caches
2. Domain split: LangSmith = external ops; ZakOps internal agent = deal-side automation
3. Action queue = coordination backbone (no direct agent-to-agent communication)
4. 22 tools (16 existing + 6 new)
5. 16 action types with default lease durations
6. 5 detailed payload schemas (inputs + results + artifacts)
7. 3 canonical processing pipelines (poll, research, sync)
8. 3-tier security model enforced by policy_guard
9. Error contract: read failures degrade, write failures abort+retry
10. Integration manifest at GET /integration/manifest with per-tool signature hashes
11. Identity contract: executor_id + correlation_id + langsmith tracing on all writes
12. Cache strategy: hybrid (6h background sync + inline for high-signal)
13. Gmail back-labeling: periodic sync primary + optional ZakOps push
14. Broker registry: ZakOps source of truth, LangSmith read-only cache
15. Deal matching: LangSmith proposes, ZakOps routes
16. 11 golden tests for verification
17. 3-phase build plan
18. Lease renewal for long-running tasks
19. Run reports committed at end of every invocation

---

*End of Integration Specification v1.0*
*Compiled: 2026-02-16*
*Agreed by: ZakOps (Claude Code / Opus 4.6) + LangSmith Exec Agent*
