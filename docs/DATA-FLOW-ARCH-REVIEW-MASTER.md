# Ultimate Master Document: Full-Stack Data Flow Architecture Review

**Date:** 2026-02-18
**Scope:** Quarantine injection → deal creation → deal lifecycle → dashboard consumption
**Method:** 3-pass deep architectural review (investigation, cross-review, solution design)
**Source:** DEAL-EVIDENCE-PIPELINE-001 execution + independent codebase analysis

---

## PASS 1 — Investigation: Complete Data Flow Mapping

### 1.1 Injection Pipeline (Agent → Quarantine Storage)

**Endpoint:** `POST /api/quarantine` (`orchestration/main.py:2203-2467`)

The LangSmith Agent Builder calls `zakops_inject_quarantine` via the MCP bridge. The backend accepts 38 fields across flat columns, JSONB overflow, and dedicated JSONB columns:

| Storage Location | Fields |
|-----------------|--------|
| Flat columns (18) | email_subject, sender, sender_name, sender_domain, sender_company, broker_name, company_name, urgency, confidence, message_id, source_thread_id, schema_version, tool_version, prompt_version, langsmith_run_id, langsmith_trace_url, correlation_id, source_type |
| extraction_evidence (JSONB) | Free-form dict — supports flat keys (broker_name, asking_price) AND nested (broker.name, financials.asking_price) |
| field_confidences (JSONB) | Per-field confidence scores {field: float} |
| attachments (JSONB) | Array of attachment metadata |
| raw_content (JSONB overflow) | classification, urgency, company_name, broker_name, email_body_full, routing_reason, routing_conflict, conflicting_deal_ids, injection_metadata |

**Key fact:** extraction_evidence, field_confidences, and attachments are first-class JSONB columns — NOT nested inside raw_content.

**Key fact:** The agent's extraction_evidence format uses FLAT keys in production (broker_name, asking_price, ebitda), though nested format (broker.name, financials.asking_price) is also supported by the enrichment helper.

---

### 1.2 Quarantine → Deal (Approve Paths)

**4 distinct approve paths**, all in `orchestration/main.py`:

| Path | Location | Creates New Deal? | Uses Enrichment Helper? |
|------|----------|-------------------|------------------------|
| Single approve (new deal) | Line 3096-3197 | YES | YES (_build_deal_enrichment) |
| Single approve (explicit deal_id) | Line 2979-3018 | NO (merges into existing) | YES (non-destructive merge) |
| Thread-match attach | Line 3023-3095 | NO (links to existing) | YES (non-destructive merge) |
| Bulk approve | Line 2564-2693 | YES | YES |

**All 4 paths** now use the shared `_build_deal_enrichment()` helper (added by DEAL-EVIDENCE-PIPELINE-001).

**Priority hierarchy for field resolution:**
1. Operator corrections (highest — user overrides agent)
2. Flat quarantine item columns (broker_name, company_name)
3. Flat extraction_evidence keys (extraction_evidence.broker_name)
4. Nested extraction_evidence keys (extraction_evidence.broker.name)
5. Default/empty (lowest)

**Non-destructive merge pattern** (for existing deals): Only fill NULL/missing keys. Never overwrite existing operator edits.

---

### 1.3 Deal Schema (Database)

**Table:** `zakops.deals` (7 data columns)

| Column | Type | Purpose |
|--------|------|---------|
| deal_id | VARCHAR(20) | Primary key (DL-NNNN format) |
| canonical_name | VARCHAR(255) | Deal name |
| display_name | VARCHAR(255) | Display override |
| stage | VARCHAR(50) | Pipeline stage (FSM-controlled) |
| status | VARCHAR(50) | active/archived/deleted |
| identifiers | JSONB | {quarantine_item_id, correlation_id, ...} |
| company_info | JSONB | {company_name, sector, role, location} |
| broker | JSONB | {name, email, company, phone} |
| metadata | JSONB | {asking_price, ebitda, revenue, sde, multiple, nda_status, cim_received, priority, ...} |
| audit_trail | JSONB | {created_from, source_item_id, ...} |

**Critical design choice:** JSONB columns are SCHEMALESS. No CHECK constraints, no validation triggers. The columns accept ANY valid JSON.

---

### 1.4 Deal Mutations (All Paths)

#### INSERT Paths
| Path | Function | Location | Uses Enrichment? |
|------|----------|----------|-----------------|
| POST /api/deals | create_deal() | Line 791-847 | NO |
| Quarantine approve (new) | process_quarantine() | Line 3096-3197 | YES |
| Quarantine approve (bulk) | bulk_process_quarantine() | Line 2564-2693 | YES |

#### UPDATE Paths
| Path | Function | Location | JSONB Behavior |
|------|----------|----------|----------------|
| PATCH /api/deals/{id} | update_deal() | Line 850-910 | OVERWRITE (full replace) |
| Quarantine approve (merge) | process_quarantine() | Line 2979-3018 | MERGE (per-key, non-destructive) |
| Thread-match attach | process_quarantine() | Line 3023-3095 | MERGE (per-key, non-destructive) |
| Archive deal | archive endpoint | Line 1174-1199 | Stage only (via stored proc) |
| Undo approve | undo_quarantine_approve() | Line 3372-3463 | Status+stage (direct UPDATE) |
| Retention cleanup | cleanup.py:350-394 | Direct UPDATE | deleted+status (direct UPDATE) |

---

### 1.5 Deal Stage Transitions

**Engine:** `DealWorkflowEngine` (`src/core/deals/workflow.py`)

Stage transitions ONLY update the `stage` column + record events. NO data enrichment occurs at stage transitions. The workflow engine:
- Validates against `STAGE_TRANSITIONS` dict (FSM)
- Writes to `deal_transitions` ledger
- Writes to `deal_events` table
- Publishes to outbox for side-effects
- Supports idempotency keys

**Stage flow:** inbound → screening → qualified → loi → diligence → closing → portfolio

---

### 1.6 Dashboard Consumption

**Schema:** `DealDetailSchema` (`apps/dashboard/src/lib/api.ts:101-139`)

The dashboard reads deal data via `GET /api/deals/{dealId}` and validates through Zod schemas:

| Schema Section | Fields Rendered | Null Handling |
|---------------|-----------------|---------------|
| broker | name, email, company | Shows "-" if null |
| metadata | asking_price, ebitda, revenue, multiple, nda_status, cim_received | Shows "TBD" in muted gray |
| company_info | sector, location (.city, .state) | Shows "Unknown" |
| identifiers | quarantine_item_id (badge only) | Badge hidden if absent |

**coercedNumber transform:** Strips `$` and commas, then `parseFloat()`. Handles "TBD" → null, "-" → null. Does NOT handle M/K suffixes ($2.5M → 2.5, not 2500000). Backend stores as numbers, so this is fine for new data.

**Dashboard is READ-ONLY** for broker/metadata/company_info. No edit UI exists. The only UI mutation is stage transitions.

**.passthrough()** on broker, metadata, company_info sub-objects allows extra backend fields to survive Zod validation.

---

## PASS 2 — Cross-Review: Structural Gaps and Data Flow Weaknesses

### FINDING F-01: PATCH Endpoint Uses JSONB OVERWRITE — Data Loss Vector

**Severity:** HIGH
**Location:** `orchestration/main.py:871`

The `PATCH /api/deals/{deal_id}` endpoint sets JSONB columns with direct assignment (`SET broker = $N::jsonb`), completely replacing the column value. If ANY caller sends a partial broker object like `{"name": "Updated"}`, the enriched `company`, `phone`, and `email` fields are destroyed.

**Impact:** Any future deal edit feature, or any agent tool call to `zakops_update_deal`, could silently wipe enriched data.

**Current mitigation:** The dashboard has no edit UI for JSONB columns. But the API is public.

---

### FINDING F-02: No Formal Deal Data Contract

**Severity:** HIGH
**Location:** System-wide (no single file)

The definition of "what data a deal should have" is scattered across:
1. Database DDL — JSONB columns accept anything
2. `DealDetailSchema` in TypeScript — what the dashboard expects
3. `_build_deal_enrichment()` in Python — what the backend populates
4. `DealResponse` Pydantic model — what the API returns

These 4 definitions can drift independently. There is NO single source of truth that answers: "What fields should be in deal.broker?" No validation prevents the backend from returning data the dashboard can't render, or the dashboard from expecting data the backend never provides.

---

### FINDING F-03: field_confidences Dropped at Approval

**Severity:** MEDIUM
**Location:** `_build_deal_enrichment()` (does not read field_confidences)

The agent provides per-field confidence scores (e.g., `{"broker_name": 0.95, "asking_price": 0.7}`). These are stored as a JSONB column on quarantine_items. At approval, `_build_deal_enrichment()` never reads them. They are silently lost.

**Impact:** Operators can't see HOW confident the agent was about extracted data. A broker name with 0.3 confidence looks identical to one with 0.99 confidence.

---

### FINDING F-04: attachments Dropped at Approval

**Severity:** MEDIUM
**Location:** `_build_deal_enrichment()` (does not read attachments)

The agent provides attachment metadata (file names, MIME types, sizes). Stored as JSONB on quarantine_items. Never carried to the deal.

**Impact:** After approval, there's no record of what attachments were in the original email unless you go back to the quarantine item.

---

### FINDING F-05: Traceability Metadata Lost at Approval

**Severity:** MEDIUM
**Location:** `_build_deal_enrichment()` (does not carry langsmith_run_id, langsmith_trace_url)

The quarantine item stores `langsmith_run_id` and `langsmith_trace_url` for linking back to the agent execution trace. At approval, these are never copied to the deal. After approval, there's no way to trace back to the specific agent run that produced the extraction.

---

### FINDING F-06: entities.people[] Dropped at Approval

**Severity:** LOW
**Location:** `_build_deal_enrichment()` (only reads entities.companies[0])

The extraction_evidence can contain `entities.people[]` — names, titles, and roles of people mentioned in the email. The enrichment helper only reads `entities.companies[0]` for the company name/role. All people data is lost.

**Impact:** Operators lose contact names that the agent extracted.

---

### FINDING F-07: extraction_evidence Has No Schema Validation

**Severity:** MEDIUM
**Location:** `orchestration/main.py:2448` (stored as-is)

The injection endpoint stores `extraction_evidence` without any structural validation. The agent could send any JSON structure. If the agent changes its output format (e.g., renames `broker_name` to `broker.name`, or restructures completely), the enrichment helper would silently miss all data.

**Impact:** A silent format drift in the agent's output would cause all newly approved deals to have empty enrichment — with no error, no warning, no log.

---

### FINDING F-08: Manual Deal Creation Bypasses Enrichment

**Severity:** LOW
**Location:** `POST /api/deals` (create_deal(), line 791-847)

When a deal is created manually via `POST /api/deals` (or through the dashboard's "New Deal" form), no enrichment runs. If a quarantine item is later linked to this deal (via thread-match or explicit deal_id), enrichment runs. But if the deal is created independently without a quarantine source, it has empty JSONB columns forever.

**Impact:** Low — manual deals don't have quarantine data to enrich from. But inconsistency in data patterns.

---

### FINDING F-09: Quarantine Source Not Joinable in Dashboard

**Severity:** LOW
**Location:** Deal page (`apps/dashboard/src/app/deals/[id]/page.tsx`)

The deal stores `identifiers.quarantine_item_id` as a reference, but the dashboard NEVER fetches the quarantine item to supplement deal display. If enrichment misses a field, it's gone from the deal page forever. There's no "view source data" fallback.

---

### FINDING F-10: Retention Cleanup Bypasses FSM Choke Point

**Severity:** LOW
**Location:** `cleanup.py:350-394`

The retention cleanup does `UPDATE zakops.deals SET deleted = TRUE, status = 'deleted'` directly, bypassing the `transition_deal_state()` stored procedure. This violates the ADR-001 choke-point pattern. No transition event, no outbox entry, no audit trail.

---

### FINDING F-11: Undo-Approve Uses Direct UPDATE

**Severity:** LOW
**Location:** `orchestration/main.py:3395` (undo_quarantine_approve)

The undo-approve endpoint sets `status = 'archived', stage = 'archived'` via direct SQL UPDATE, bypassing the workflow engine. This creates a deal_event but does NOT write to deal_transitions, breaking the audit trail.

---

## PASS 3 — Solution Design: Systemic Architectural Fix

### Root Cause Analysis

The system's fundamental architectural deficiency is:

**Data lives in two tables (quarantine_items and deals) with a one-time, lossy, procedural copy at approval time. Any field missed by the copy function is silently lost forever. There is no schema contract governing what transfers, no validation that the transfer was complete, and no runtime fallback to the source data.**

This manifests as:
- Incremental endpoint-by-endpoint patching (yesterday quarantine, today deals, tomorrow the next gap)
- Silent data loss with no errors or warnings
- No single point to fix when the agent changes its extraction format
- Dashboard expecting fields the backend never populates

### Design Principle: Eliminate the Class of Bugs, Not the Individual Bug

The fix must make it **architecturally impossible** to:
1. Add a new approve path that forgets to enrich
2. Lose data when the PATCH endpoint is called
3. Have dashboard schema drift from backend reality
4. Miss a format change in the agent's extraction_evidence

### Proposed Architecture (6 Layers)

#### Layer 1: Deal Data Contract (Pydantic schemas as single source of truth)

**What:** Create typed Pydantic models for deal JSONB sub-objects.
**Where:** `apps/backend/src/core/deals/deal_contract.py`
**Why:** Eliminates F-02 (no formal contract). Both the enrichment service and the API response can validate against this schema. The DealDetailSchema in TypeScript should align with these models.

Models: `DealBrokerContract`, `DealMetadataContract`, `DealCompanyInfoContract`, `DealIdentifiersContract`

These use `model_config = ConfigDict(extra='allow')` for forward compatibility (mirrors .passthrough() in Zod).

#### Layer 2: Enrichment Service (proper service class, not inline helper)

**What:** Promote `_build_deal_enrichment` to a dedicated service class.
**Where:** `apps/backend/src/core/deals/enrichment.py`
**Why:** Eliminates the risk of future code bypassing the helper. A service class with a clear interface is harder to forget than an underscore-prefixed function buried in a 3000-line file.

Class: `DealEnrichmentService`
- `enrich_from_quarantine(item: dict, corrections: dict | None = None) -> DealEnrichment`
- `merge_into_existing(current: dict, enrichment: DealEnrichment) -> dict` (non-destructive)
- `validate_extraction_evidence(ev: dict) -> list[str]` (returns warnings for missing expected keys)

#### Layer 3: PATCH Endpoint JSONB Merge (eliminate overwrite risk)

**What:** Change PATCH to merge JSONB per-key instead of full overwrite.
**Where:** `orchestration/main.py:850-910` (update_deal function)
**Why:** Eliminates F-01 (PATCH data loss). Sending `{broker: {name: "New"}}` updates only `name`, preserving `company`, `phone`, `email`.

SQL pattern: `SET broker = COALESCE(broker, '{}'::jsonb) || $N::jsonb`

#### Layer 4: Carry Forward Traceability + Confidence

**What:** Include field_confidences, langsmith metadata, and attachment references in deal metadata.
**Where:** Enrichment service (Layer 2)
**Why:** Eliminates F-03, F-04, F-05 (dropped metadata at approval).

New metadata fields:
- `metadata.field_confidences` — per-field confidence from the agent
- `metadata.langsmith_run_id` — link to agent trace
- `metadata.langsmith_trace_url` — clickable URL to trace
- `metadata.attachment_count` — number of attachments (not full metadata, to avoid bloat)
- `metadata.people` — extracted people names/titles from entities

#### Layer 5: extraction_evidence Format Validation

**What:** Add structural validation at injection time with warnings (not rejections) for unexpected formats.
**Where:** Injection endpoint validation
**Why:** Eliminates F-07 (silent format drift). If the agent changes its extraction format, the backend logs a warning that the enrichment helper can detect.

Validation: Check for expected top-level keys (broker_name OR broker.name, asking_price OR financials.asking_price). If neither format is found, log a warning with the actual keys received.

#### Layer 6: Quarantine Source Link in Deal Page

**What:** Add a "Source Intelligence" card to the deal detail page that fetches the linked quarantine item.
**Where:** Dashboard deal page, new API endpoint
**Why:** Eliminates F-09 (no fallback). Even if enrichment misses a field, operators can see the full quarantine data. Also shows field confidences, full extraction evidence, and original email context.

API: `GET /api/deals/{deal_id}/quarantine-source` — returns the linked quarantine item with extraction_evidence
Dashboard: New "Source Intelligence" card on the deal Overview tab

---

## Summary of All Findings and Their Fixes

| # | Finding | Severity | Fix Layer | Phase |
|---|---------|----------|-----------|-------|
| F-01 | PATCH overwrites JSONB | HIGH | L3: JSONB merge | P2 |
| F-02 | No formal deal data contract | HIGH | L1: Pydantic schemas | P1 |
| F-03 | field_confidences dropped | MEDIUM | L4: Carry forward | P3 |
| F-04 | attachments dropped | MEDIUM | L4: Carry forward | P3 |
| F-05 | Traceability metadata lost | MEDIUM | L4: Carry forward | P3 |
| F-06 | entities.people[] dropped | LOW | L4: Carry forward | P3 |
| F-07 | extraction_evidence no validation | MEDIUM | L5: Format validation | P4 |
| F-08 | Manual deal creation bypasses enrichment | LOW | Out of scope (by design) |
| F-09 | Quarantine not joinable in dashboard | LOW | L6: Source link card | P5 |
| F-10 | Retention cleanup bypasses FSM | LOW | Out of scope (separate mission) |
| F-11 | Undo-approve bypasses workflow | LOW | Out of scope (separate mission) |

---

## Architectural Decision: Why This and Not Alternatives

### Rejected: Database trigger approach
A BEFORE INSERT/UPDATE trigger on deals could auto-enrich from quarantine. Rejected because:
- Triggers are invisible, hard to debug, and couple the schema to specific JSONB key names
- Doesn't solve the dashboard consumption gap

### Rejected: Materialized view approach
A view JOIN-ing deals + quarantine_items could provide combined data. Rejected because:
- Breaks the deal API's return type contract
- Adds query complexity to every deal fetch
- Doesn't solve the PATCH overwrite problem

### Rejected: Event-driven enrichment service
Deal creation emits an event → separate service enriches. Rejected because:
- Adds eventual consistency complexity
- Overkill for synchronous approval flow
- Doesn't solve the PATCH overwrite problem

### Chosen: Service layer + JSONB merge + source link
- Synchronous, deterministic, debuggable
- No new infrastructure (no triggers, no queues, no views)
- Addresses ALL 9 addressable findings
- Forward-compatible (new fields just need Pydantic model + enrichment mapping)

---

*End of Ultimate Master Document — DATA-FLOW-ARCH-REVIEW*
