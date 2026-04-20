# ZakOps M&A Copilot — Validation Roadmap

**Version:** 2.1  
**Date:** February 14, 2026  
**Purpose:** Take the system from current state to production-grade, operational M&A Copilot  
**Audience:** All builders (Claude Code, LangSmith Agent Builder, and any collaborating AI/human)  
**Authority:** This is the single execution plan. No side fixes. No fragments. Everything flows through this document.

---

## How to Read This Roadmap

This roadmap is organized into **9 phases** (Phase 0 through Phase 8). Each phase has a clear objective, a list of deliverables, and a set of validation gates that must pass before moving to the next phase. Phases are sequential — you cannot skip ahead.

Every deliverable has an **owner** (which builder is responsible) and a **verification method** (how we prove it works). Nothing is considered done until the verification passes.

**V2.1 clarification:** The word "operational" in this roadmap means the full loop works — emails arrive in a decision-grade format, operators can reliably review and decide, approvals produce complete lifecycle artifacts, and the system can be measured cleanly in shadow mode. "Connected" (which the system already is) is not the same as "operational."

---

## Division of Responsibility

Before any phase begins, all builders must agree on who owns what. These boundaries are non-negotiable and prevent the two agents from overlapping or creating conflicting implementations.

### Email Triage Owns (LangSmith Agent)

- Gmail ingestion + OAuth
- Deal-signal classification (deal_signal, operational, newsletter, spam)
- Metadata extraction (sender, subject, company/broker hints, thread context)
- A short operator-ready summary + recommendation (approve/reject + why)
- Confidence scoring (overall + per-field)
- Extraction evidence (what text the agent based each extraction on)
- Injecting quarantine items via one tool (`zakops_inject_quarantine`) with a stable schema
- Executing delegated tasks (email sending, scheduling, research) when instructed by ZakOps

### ZakOps Owns (Backend + UI + Workflow)

- Canonical storage + dedup + rate limiting + audit trail
- Schema validation + boundary enforcement (reject malformed payloads)
- Idempotency enforcement (message_id dedup)
- Correlation ID assignment and propagation
- Feature flag management (shadow_mode, auto_route, delegate_actions, send_email_enabled)
- Kill switch
- Operator review UX (list + detail + preview reliability)
- Decision workflow (approve/reject/escalate gates + reasons + optimistic locking)
- Promotion pipeline via the workflow engine (deal creation + deal_transitions + outbox events + audit trail entries)
- Auto-routing logic (thread → deal matching, conflict handling)
- Delegated task state machine (queuing, retries, dead-letter)
- Observability (correlation_id end-to-end, monitoring, alerting)
- Security perimeter (Cloudflare Access, Bearer auth, key rotation)

**Rule:** If a capability is not listed under your agent, you do not build it. If there's ambiguity, resolve it here before writing code.

---

## Current State (Where We Are)

| Component | Status | Evidence |
|-----------|--------|----------|
| LangSmith ↔ ZakOps connection | ✅ Live | 13 tools discovered, `zakops_inject_quarantine` executes |
| Full chain (LangSmith → Tunnel → Bridge → Backend → DB → Dashboard) | ✅ Working | 5 emails injected and visible in Quarantine |
| Backend dedup / idempotency (`message_id`) | ✅ Implemented + QA-verified | Backend enforces unique constraint on `message_id` |
| Backend correlation ID | ✅ Implemented + QA-verified | Middleware assigns `correlation_id` to requests |
| Backend `source_type` filtering | ✅ Implemented + QA-verified | Items tagged with `source_type` on ingestion |
| Backend rate limiting | ✅ Implemented + QA-verified | Rate limiter active on injection endpoint |
| Quarantine data quality | ❌ Broken | Most fields arrive as NULL (subject, company, broker, confidence, sender name) — Email Triage sends minimal payload |
| Quarantine detail view | ❌ Broken | "Preview not found" — no body content stored or fetchable |
| Quarantine approve/reject → deal promotion | ❌ Not wired | Buttons exist but do not trigger the workflow engine (no deal, no transitions, no outbox, no audit) |
| Email Triage system prompt | ❌ Incomplete | Agent classifies but does not extract or summarize; payload assembly does not populate required fields |
| Collaboration contract (Agent A ↔ Agent B) | ❌ Not implemented | No structured delegation, no feedback loop, no mutual awareness |
| Auto-routing (approved deal catches future emails) | ❌ Not implemented | No thread → deal index, no bypass logic |
| Document retrieval and attachment | ❌ Not implemented | No file handling workflow |
| Bearer auth on MCP bridge | ⚠️ Bypassed | LangSmith `{{SECRET}}` interpolation bug — no alternative perimeter control in place |

**V2.1 note:** The backend has hardened primitives for dedup, correlation, source_type, and rate limiting. The roadmap focus is now: operational UX wiring, schema mapping correctness, promotion workflow correctness, and security hardening. Builders must NOT re-implement or regress these existing primitives.

---

## Desired State (Where We're Going)

The M&A Copilot Architecture document defines a two-agent system. When this roadmap is complete, the platform is not merely "connected" — it is **operational**:

- Emails arrive into Quarantine in a **decision-grade format** (all fields populated, preview visible, evidence available)
- Operators can **reliably review, approve, reject, or escalate** with atomic state transitions
- Approvals produce **full lifecycle artifacts** (deal + transitions + outbox event + audit entry)
- Auto-routing catches follow-up emails for approved deals and bypasses quarantine
- Delegation enables ZakOps to instruct Email Triage to send emails, schedule meetings, and perform research — with explicit operator confirmation and structured feedback
- Shadow mode can be measured cleanly for one week with full isolation
- Security perimeter is explicit and enforceable — not dependent on LangSmith's secret handling

---

## Canonical Constants and Field Names

These values are non-negotiable. Every builder, every tool, every document, every payload must use these exact strings. No synonyms. No alternatives.

### Source Type Constants

| Constant | Meaning | When Used |
|----------|---------|-----------|
| `langsmith_shadow` | Shadow pilot — Email Triage is injecting but items are clearly marked as shadow data | During shadow pilot phase |
| `langsmith_live` | Production live — Email Triage injections are treated as real operational data | After shadow pilot graduation only |

**Rules:**
- Generic labels like `shadow`, `live`, `test`, `email_triage` are **banned** in payloads and code. Use the canonical constants above.
- Any payload with an unknown `source_type` value → rejected with HTTP 400 and error message naming the invalid value.
- `langsmith_live` must NOT appear anywhere in the system during the shadow pilot. If it does → investigation required.

### Canonical Dedup Key

The canonical dedup key for quarantine items is **`message_id`** (the Gmail message ID).

- If any document, tool definition, or code uses the name `source_message_id`, it must be mapped to `message_id` at the boundary (MCP bridge / tool layer).
- The database column is `message_id`.
- The tool parameter may be named `source_message_id` for clarity to Email Triage, but the bridge maps it to `message_id` before storage.
- No other dedup key exists. There is one key. It is `message_id`.

### Canonical Display-Critical Fields

These fields must be populated for any quarantine item to be operationally useful. If any of these are NULL or empty on a record, the injection is considered incomplete and should be flagged.

| Field (DB column) | Display Purpose | Populated By |
|-------------------|----------------|-------------|
| `sender` | Who sent the email (email address) | Email Triage (from Gmail) |
| `email_subject` | List view title — replaces "Unknown subject" | Email Triage (from Gmail) |
| `received_at` | When the email arrived (timestamp) | Email Triage (from Gmail) |
| `email_body_snippet` | Detail panel preview — replaces "Preview not found" | Email Triage (from Gmail body, 500 char truncation) |

**Success criteria:** No "Unknown subject" and no empty preview for any injected item — unless the source email genuinely had no subject line or body (edge case, must be documented if it occurs).

---

## Phase 0: Production Envelope & Invariants

**Objective:** Establish the foundational infrastructure rules that every subsequent phase must obey. This phase defines the environment model, feature flags, idempotency verification, traceability requirements, emergency controls, and security perimeter.

### 0.1 Environment Model

**Owner:** Claude (Builder) — Backend + Infrastructure  
**Verification:** Environment variable `ZAKOPS_ENV` determines behavior; feature flags control capability rollout

| Environment | Purpose | Email Triage Writes | Deal Creation | Email Sending |
|-------------|---------|-------------------|---------------|---------------|
| `dev` | Builder testing | Allowed (no restrictions) | Allowed | Disabled (logged only) |
| `staging` | Integration testing | Allowed (shadow mode default) | Allowed | Disabled (logged only) |
| `prod` | Live operation | Controlled by feature flags | Controlled by feature flags | Requires operator confirmation |

### 0.2 Feature Flags

**Owner:** Claude (Builder) — Backend  
**Verification:** Each flag toggleable at runtime without redeployment; behavior confirmed for both ON and OFF states

| Flag | Default (prod) | What It Controls |
|------|----------------|-----------------|
| `shadow_mode` | ON | When ON, Email Triage injections are tagged `source_type=langsmith_shadow`. When OFF, injections are tagged `source_type=langsmith_live`. |
| `auto_route` | OFF | When ON, the auto-routing bypass (Phase 5) is active. When OFF, all emails go through quarantine regardless of thread match. |
| `delegate_actions` | OFF | When ON, ZakOps can delegate tasks to Email Triage. When OFF, delegation is disabled. |
| `send_email_enabled` | OFF | When ON, Email Triage is permitted to send emails. When OFF, all outbound email actions are blocked at the MCP tool level. Separate from `delegate_actions` as a safety backstop. |

Flags must be readable by both the backend and the MCP bridge. Stored in the database or a config service — not hardcoded.

### 0.3 Verify Existing Idempotency (Do Not Reimplement)

**Owner:** Claude (Builder) — Backend  
**Verification:** Confirm existing dedup on `message_id` works correctly under concurrency

The backend already enforces idempotency on `message_id`. This step verifies it, not reimplements it:

| Operation | Idempotency Key | Behavior on Duplicate | Verification Test |
|-----------|----------------|----------------------|-------------------|
| Inject quarantine item | `message_id` | Return existing quarantine item; do not create duplicate | 5 concurrent identical `message_id` injections → exactly 1 record |
| Approve quarantine item | `quarantine_item_id` + `version` (optimistic lock, Phase 2) | If already approved, return existing deal | Simultaneous approve → one succeeds, one 409 |
| Reject quarantine item | `quarantine_item_id` + `version` | If already rejected, return existing rejection | Simultaneous reject → one succeeds, one 409 |
| Auto-route email to deal | `message_id` | If already routed, return existing event | Duplicate route call → no duplicate timeline event |

**Fail-closed requirement:** If the idempotency layer (database unique constraint) is unavailable, the request must be **rejected** (500 error), not silently bypassed. Verify this by simulating a database constraint failure.

### 0.4 Verify Existing Correlation ID (Do Not Reimplement)

**Owner:** Claude (Builder) — Backend  
**Verification:** Confirm existing correlation_id middleware works end-to-end

The backend already assigns `correlation_id`. Verify:

- Every inbound MCP tool call receives or is assigned a `correlation_id`
- The `correlation_id` is stored on the quarantine item record
- The `correlation_id` appears in backend log entries for that request
- The `correlation_id` is returned in the tool response

**Extension needed:** Ensure `correlation_id` propagates to deal records and timeline events created from quarantine items (Phase 4). This may not be wired yet.

### 0.5 Kill Switch

**Owner:** Claude (Builder) — Backend + MCP Bridge  
**Verification:** Flip the kill switch → all Email Triage write operations return 503 immediately; read operations still work

A single flag (`email_triage_writes_enabled`) that, when set to `false`:

- Blocks all `zakops_inject_quarantine` calls (returns 503 with `"reason": "writes_disabled"`)
- Blocks all delegated task executions
- Does NOT block read operations (`zakops_get_deal_status`, health checks)
- Can be toggled via admin API endpoint or database flag
- Takes effect immediately (no restart required)

### 0.6 Security Perimeter (P0 — Required Even for Shadow Mode)

**Owner:** Claude (Builder) — Backend + Infrastructure  
**Verification:** MCP bridge rejects unauthenticated requests via at least one enforced control

Shadow mode does not mean security is optional. The MCP bridge must have a real perimeter before any data flows.

**PASS requires at least one of the following enforced in production:**

| Option | Mechanism | Notes |
|--------|-----------|-------|
| A | Bearer auth working end-to-end with LangSmith secrets | Preferred if LangSmith's `{{SECRET}}` interpolation is fixed |
| B | Cloudflare Access service-token protection at the tunnel edge | Infrastructure-level, independent of LangSmith |
| C | IP allowlist + Bearer token | Fallback if Cloudflare Access is not available |

**Also required regardless of which option:**
- Key rotation + revocation procedure documented with explicit, fast steps (not "refer to Cloudflare docs" — actual commands/steps for this specific setup)
- Verification that the bridge rejects requests without valid credentials (test with curl, no auth → 401/403)

### Gate 0

```
□ ZAKOPS_ENV variable controls environment behavior
□ All 4 feature flags exist, are toggleable at runtime, and default correctly for prod
□ shadow_mode ON: injected items tagged source_type=langsmith_shadow (exact string)
□ Unknown source_type → 400 rejection with clear error message
□ langsmith_live does NOT appear anywhere during shadow pilot
□ Idempotency verified: 5 concurrent identical message_id injections → exactly 1 record
□ Idempotency fail-closed: simulated DB constraint failure → 500 rejection, not silent bypass
□ correlation_id present on quarantine item and in log entries for a single injection
□ correlation_id returned in tool response
□ Kill switch ON: all write operations return 503 within 1 second
□ Kill switch ON: read operations still work
□ Kill switch OFF: normal operation resumes
□ Security perimeter: MCP bridge rejects unauthenticated requests (at least one enforced control)
□ Key rotation + revocation procedure documented with explicit steps
□ Unauthenticated curl to bridge → 401 or 403 (not 200)
```

---

## Phase 1: Quarantine Schema & Data Contract

**Objective:** Define what a complete, actionable quarantine item looks like — and make both sides agree on it. This is an audit-grade contract: every field is typed, versioned, and traceable.

This is the foundation. Everything else depends on this schema being right.

### 1.1 Define the Canonical Quarantine Item Schema

**Owner:** Collaborative (all builders must agree)

The schema must answer: when a human operator opens a quarantine item, what do they need to see to make an approve/reject decision?

**Required fields (Email Triage must populate before injection):**

| Field | Type | Source | Purpose |
|-------|------|--------|---------|
| `email_subject` | string | Gmail thread | List view title — replaces "Unknown subject" |
| `sender` | string | Gmail message | Who sent the email (email address) |
| `sender_name` | string | Extracted by Email Triage | Human-readable name (not just email address) |
| `sender_domain` | string | Parsed from sender | Domain for quick visual grouping |
| `sender_company` | string | Extracted / inferred by Email Triage | Company name associated with sender |
| `received_at` | datetime | Gmail message metadata | When the email arrived |
| `classification` | enum | Email Triage `triage_classifier` | deal_signal, operational, newsletter, spam |
| `urgency` | enum | Email Triage assessment | HIGH, MEDIUM, LOW |
| `confidence` | float (0–1) | Email Triage `triage_classifier` | Overall classification confidence |
| `company_name` | string | Email Triage `entity_extractor` | Target company mentioned in the email |
| `broker_name` | string | Email Triage `entity_extractor` | Broker or intermediary mentioned |
| `email_body_snippet` | string (500 char max) | Gmail message body | Truncated preview for the detail panel — must not be empty |
| `triage_summary` | string | Email Triage | Agent's 2–3 sentence explanation: why this email matters, what action it implies |
| `source_thread_id` | string | Gmail API | For linking back to the original email thread + auto-routing |
| `source_message_id` | string | Gmail API | Maps to `message_id` at boundary — canonical dedup key |
| `attachments` | array of objects | Gmail API | See 1.4 for required structure |

**Versioning and traceability fields (Email Triage must populate):**

| Field | Type | Source | Purpose |
|-------|------|--------|---------|
| `schema_version` | string (semver) | Hardcoded in tool call | Which version of the quarantine schema this payload conforms to (e.g., "1.0.0") |
| `tool_version` | string (semver) | Hardcoded in tool definition | Which version of `zakops_inject_quarantine` produced this payload |
| `prompt_version` | string | Email Triage config | Identifier for the system prompt version that produced this classification |
| `langsmith_run_id` | string | LangSmith runtime | The LangSmith run ID for this execution |
| `langsmith_trace_url` | string (optional) | LangSmith runtime | Direct URL to the LangSmith trace |
| `correlation_id` | string (uuid) | Assigned by caller or MCP bridge | End-to-end correlation (from Phase 0) |

**Extraction evidence fields (Email Triage must populate):**

| Field | Type | Source | Purpose |
|-------|------|--------|---------|
| `extraction_evidence` | object | Email Triage | Structured evidence for extracted entities (see 1.3) |
| `field_confidences` | object | Email Triage | Per-field confidence scores (see 1.3) |

**Fields ZakOps owns (populated after injection):**

| Field | Type | Set By | Purpose |
|-------|------|--------|---------|
| `id` | uuid | Backend on creation | Internal identifier |
| `message_id` | string | Mapped from `source_message_id` at boundary | Canonical dedup key (DB column) |
| `status` | enum | Backend | pending, approved, rejected, escalated |
| `source_type` | enum | Backend (from `shadow_mode` flag) | `langsmith_shadow` or `langsmith_live` (exact canonical strings) |
| `operator` | string | Set by user on approve/reject | Who made the decision |
| `reject_reason` | string | Set by user on reject | Why the item was rejected |
| `approved_at` / `rejected_at` | datetime | Backend on state change | Audit timestamp |
| `created_deal_id` | uuid | Backend on approve | Links to the deal created from this item |
| `created_at` | datetime | Backend on creation | When the item entered quarantine |
| `version` | integer | Backend (optimistic lock) | Row version for concurrent edit safety (Phase 2) |

**Boundary mapping rule:** The MCP tool parameter is named `source_message_id` (clear to Email Triage). The MCP bridge maps this to `message_id` before storage. Both names refer to the same Gmail message ID. No other dedup key exists.

### 1.2 Update the `zakops_inject_quarantine` Tool Definition

**Owner:** Claude (Builder) — Backend API side  
**Verification:** Call the tool from LangSmith with a fully populated payload → confirm all fields persist in DB and appear in the Quarantine UI. Call with missing required field → confirm rejection with clear error.

The MCP tool definition must enforce this schema:

- Required fields must be validated on ingestion. The tool must reject payloads missing `email_subject`, `sender`, `classification`, `source_message_id`, `schema_version`, or `correlation_id` with a clear error message naming the missing fields.
- The tool must enforce idempotency on `message_id` (existing backend primitive).
- The tool must tag items with `source_type=langsmith_shadow` or `source_type=langsmith_live` based on the `shadow_mode` feature flag.
- The tool must reject payloads with unknown `source_type` values with HTTP 400.
- The tool must reject payloads with unknown `schema_version` values (forward compatibility guard).
- The tool must not accept extra keys beyond the defined schema (strict validation — no silent pass-through of unexpected fields).

### 1.3 Extraction Evidence and Per-Field Confidence

**Owner:** Email Triage configuration (LangSmith Agent Builder)  
**Verification:** Injected items include evidence for each extracted entity, and per-field confidence differs from overall classification confidence

The `extraction_evidence` field provides the basis for each extracted value, enabling operators to verify and correct:

```json
{
  "extraction_evidence": {
    "company_name": {
      "value": "Acme Manufacturing",
      "source": "Email body, paragraph 2: '...regarding the potential acquisition of Acme Manufacturing...'",
      "confidence": 0.92
    },
    "broker_name": {
      "value": "John Smith, Meridian Partners",
      "source": "Email signature block",
      "confidence": 0.85
    }
  },
  "field_confidences": {
    "classification": 0.94,
    "company_name": 0.92,
    "broker_name": 0.85,
    "urgency": 0.78
  }
}
```

Per-field confidence matters because an email might clearly be a deal signal (classification confidence 0.95) while the company name extraction is uncertain (company_name confidence 0.60). The operator needs to know which fields to trust and which to verify.

**Documentation requirement:** What Email Triage sets vs what ZakOps computes must be documented once and agreed. Email Triage sets `confidence`, `field_confidences`, and `extraction_evidence`. ZakOps does not override these — it may add its own computed fields (e.g., enrichment score) but they are separate columns, not overwrites.

### 1.4 Attachment Schema

**Owner:** Both builders  
**Verification:** Injected items with attachments include all required attachment fields

Each attachment in the `attachments` array must include:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `attachment_id` | string | Yes | Gmail attachment ID (for fetch-on-demand) |
| `filename` | string | Yes | Original filename |
| `mime_type` | string | Yes | MIME type (application/pdf, etc.) |
| `size_bytes` | integer | Yes | File size |
| `classification` | string | No | Document type from `document_analyzer`: cim, teaser, nda, financials, other |

Later (Phase 7+), add `sha256` hash for deterministic document identity and deduplication.

### 1.5 Fix "Preview Not Found" at the Contract Level

**Owner:** Claude (Builder) — Backend  
**Verification:** Every quarantine item either has inline body content or can fetch it on demand — "Preview not found" never appears

Two acceptable approaches (choose one or implement both with fallback):

**Option A — Store body content inline (preferred for reliability):**  
Email Triage includes `email_body_snippet` (500 chars, required) and optionally `email_body_full` (full text, stored separately in a content table or blob store). The detail panel renders from stored content. No external dependency at display time.

**Option B — Fetch on demand via Gmail IDs:**  
Email Triage includes `source_message_id` and `source_thread_id`. The backend has a `/api/quarantine/:id/preview` endpoint that fetches the email body from Gmail. Requires Gmail API credentials on the backend.

**Decision rule:** Option A is more reliable (works even if Gmail access is revoked or rate-limited). Option B saves storage but introduces a runtime dependency. If Option B is chosen, it must degrade gracefully (show `email_body_snippet` if the full fetch fails, never show "Preview not found").

Regardless of which option: `email_body_snippet` is a required field in the schema. It must always be populated. The detail panel must always have something to render.

### 1.6 Update Email Triage Sub-Agents to Populate All Fields

**Owner:** Email Triage configuration (LangSmith Agent Builder)  
**Verification:** Run Email Triage against 5 real emails → confirm every quarantine item has zero NULL values for required fields

The sub-agents need to be wired so their outputs feed into the injection payload:

- `triage_classifier` → `classification`, `urgency`, `confidence`, `field_confidences.classification`
- `entity_extractor` → `company_name`, `broker_name`, `sender_name`, `sender_company`, `extraction_evidence`, `field_confidences` (per entity)
- A summarization step → `triage_summary`
- Gmail API metadata → `email_subject`, `received_at`, `source_thread_id`, `source_message_id`, `email_body_snippet`, `attachments`
- LangSmith runtime → `langsmith_run_id`, `langsmith_trace_url`
- Static config → `schema_version`, `tool_version`, `prompt_version`

### Gate 1 — Mapping Contract Test

This gate proves the injected payload becomes reviewable and decision-grade, end-to-end.

```
□ Canonical schema documented and agreed by all builders
□ Schema includes schema_version, tool_version, prompt_version
□ Schema includes langsmith_run_id and/or langsmith_trace_url
□ Schema includes extraction_evidence and field_confidences
□ Attachment schema requires attachment_id + mime_type
□ source_message_id maps to message_id at boundary — documented
□ source_type uses canonical constants (langsmith_shadow / langsmith_live) — no generic labels
□ Tool rejects payloads with missing required fields (returns clear error naming fields)
□ Tool rejects payloads with extra/unknown keys (strict validation)
□ Tool rejects unknown source_type with 400
□ Tool rejects unknown schema_version with 400
□ Tool enforces idempotency on message_id (existing primitive — verified, not reimplemented)
□ "Preview not found" resolved: email_body_snippet always populated; Option A or B with fallback
□ GOLDEN TEST: One payload injected via the same tool Email Triage uses →
  - DB row shows message_id, sender, email_subject, received_at, source_type, email_body_snippet populated
  - Quarantine list row renders sender/subject/date correctly (no "Unknown subject")
  - Detail panel renders triage_summary/preview/evidence correctly (no "Preview not found")
  - If any field renders null/blank → FAIL (even if DB insert succeeded)
□ 5 test emails injected with complete data — all render correctly in UI
□ Per-field confidence differs from classification confidence where appropriate
□ Email Triage sets vs ZakOps computes: documented once and agreed
```

---

## Phase 2: Quarantine UI — Make It Operational

**Objective:** Transform the Quarantine page from a stale data display into a production-grade approval workflow that supports multiple operators, concurrent access, and scale.

### 2.1 Fix the List View (Left Panel)

**Owner:** Claude (Builder) — Dashboard  
**Verification:** Visual inspection + functional test

Each item in the queue must show:

- **Title:** `email_subject` (not "Unknown subject")
- **Subtitle:** `sender_name` at `sender_company` (or `sender` if name not available)
- **Tags:** `classification` tag, `urgency` tag (color-coded: HIGH=red, MEDIUM=yellow, LOW=green), `status` tag, `source_type` tag (`langsmith_shadow` items visually distinct from `langsmith_live`)
- **Timestamp:** `received_at` (when the email arrived, not when it hit quarantine)
- **Confidence indicator:** Visual representation of `confidence` score

### 2.2 Fix the Detail View (Right Panel)

**Owner:** Claude (Builder) — Dashboard  
**Verification:** Click each item → confirm all sections render with real data; clicking any item reliably loads that item's detail (no "stalled data" from a previously selected item)

When an operator clicks a quarantine item, the detail panel must show:

- **Header:** `email_subject` + `sender_name` / `sender_company`
- **Triage Summary section:** The `triage_summary` from Email Triage
- **Email Preview section:** Full email body content (inline or fetched on demand per Phase 1.5), never "Preview not found"
- **Extracted Entities section:** `company_name`, `broker_name` — with extraction evidence visible and per-field confidence indicators
- **Classification Details:** `classification`, `urgency`, `confidence` with clear labels
- **Attachments section:** List of attachment names/types/sizes with document classification labels
- **Traceability section (collapsible):** `langsmith_run_id` / trace URL link, `schema_version`, `prompt_version`, `correlation_id`
- **Source link:** Reference to `source_thread_id`

**Stale data prevention:** Clicking a new list item must replace the detail panel content completely. If a fetch is in progress, show a loading state — never show stale data from the previously selected item.

### 2.3 Wire the Approve/Reject/Escalate Actions

**Owner:** Claude (Builder) — Dashboard + Backend  
**Verification:** Each action tested with concurrent operator simulation; UI shows clear state for why actions are enabled or disabled

**Action enablement rules (must be explicit in the UI):**
- Approve/Reject/Escalate buttons enabled only when: item `status=pending` or `status=escalated`, and an operator name is filled
- If item already processed (approved/rejected): buttons disabled with label showing current state ("Already approved by [operator]")
- If item is loading: buttons disabled with loading indicator

**Approve** must:

1. Require the `operator` field
2. Check the `version` field against the DB row (optimistic lock — if another operator already acted, reject with 409 "This item has already been processed")
3. Set `status=approved` and `approved_at=now`
4. Increment `version`
5. Trigger the promotion pipeline (Phase 4) — deal creation via workflow engine
6. Set `created_deal_id` on the quarantine item
7. Update the UI immediately (item leaves pending queue or shows approved state)

**Approve with Edits** must:

1. Allow the operator to modify `company_name`, `broker_name`, `classification`, and `urgency` before confirming
2. Store both the original values and the operator's corrections (for training/eval purposes)
3. The corrected values flow into the created deal
4. This enables operators to fix Email Triage's extraction errors at approval time

**Reject** must:

1. Require `operator` and `reject_reason` (required, not optional — this is a policy decision baked in)
2. Check `version` (optimistic lock)
3. Set `status=rejected` and `rejected_at=now`
4. Increment `version`
5. Update the UI immediately

**Escalate / Needs Review** must:

1. Set `status=escalated`
2. Optionally assign to a specific operator or team
3. Escalated items appear in a "Needs Review" filter
4. Escalated items can still be approved, rejected, or re-escalated

### 2.4 Optimistic Locking / Atomic Transitions

**Owner:** Claude (Builder) — Backend  
**Verification:** Two simultaneous approve requests for the same item → one succeeds, one fails with 409 Conflict

Every state-changing operation must:

1. Read the current `version` of the row
2. Perform the update with `WHERE id = :id AND version = :expected_version`
3. If no rows updated → return 409 Conflict
4. The frontend handles 409 gracefully (show message, refresh current state)

### 2.5 Filtering and Sorting

**Owner:** Claude (Builder) — Dashboard  
**Verification:** Each filter and sort option works independently and in combination

Filters:

- `source_type`: `langsmith_shadow` / `langsmith_live` (critical for separating shadow from live)
- `classification`: deal_signal / operational / newsletter
- `urgency`: HIGH / MEDIUM / LOW
- `confidence` threshold: slider or presets ("Low confidence only" for items needing scrutiny)
- `status`: pending / escalated (approved and rejected move to separate views)

Sorting:

- By `received_at` (newest/oldest)
- By `urgency` (highest first)
- By `confidence` (lowest first — surfaces items needing human judgment most)

**Shadow isolation requirement:** `langsmith_shadow` items must NOT appear under other source type filters. Filtering for `langsmith_live` must return zero results during shadow pilot. If `langsmith_live` items appear during shadow pilot → investigation required.

### 2.6 Bulk Actions

**Owner:** Claude (Builder) — Dashboard  
**Verification:** Select multiple items → approve or reject all; optimistic locking applies per-item; partial success reported

Each item in a bulk operation must be individually validated (optimistic lock check per item). If some items fail (already processed), the operation reports partial success with per-item details.

### Gate 2 — Concurrency + Operational Workflow

```
□ List view shows email subject, sender name, classification, urgency, confidence, source_type, timestamp
□ No "Unknown subject" for any item with a populated email_subject
□ Detail view renders all sections with real data; no "Preview not found"
□ Clicking any item reliably loads that item's detail (no stale data from previous selection)
□ Action buttons show clear enablement state (why enabled/disabled)
□ Approve creates a deal via workflow engine (Phase 4 wiring)
□ Approve with Edits allows operator correction before approval; corrections stored alongside originals
□ Reject requires reason (policy: required, not optional)
□ Escalate moves item to "Needs Review" filter
□ Approve updates UI state immediately (item leaves queue or status changes)
□ Optimistic locking: simultaneous approve on same item → one 409 Conflict
□ 5 concurrent identical message_id injections → exactly 1 record (burst dedup)
□ If idempotency layer unavailable → request rejected, not silently bypassed
□ Filters work: source_type (langsmith_shadow), classification, urgency, confidence threshold
□ Shadow isolation: langsmith_shadow items do NOT appear under other source filters
□ langsmith_live returns zero results during shadow pilot
□ Sorting works: received_at, urgency, confidence
□ Bulk approve/reject with per-item validation and partial success reporting
□ Concurrent operator test: 2 operators approve same item → 1 success, 1 conflict
```

---

## Phase 3: Email Triage Agent — System Prompt, Role Definition & Guardrails

**Objective:** Configure Email Triage so it understands its exact role, boundaries, and output requirements — with deterministic payload assembly and calibration infrastructure.

### 3.1 Rewrite the Email Triage System Prompt

**Owner:** Zaks (LangSmith Agent Builder configuration)  
**Verification:** Run the agent against 10 diverse emails → confirm outputs match the expected schema and behavior

The system prompt must cover:

**Identity and role:**
- You are Email Triage, the execution layer of the ZakOps M&A Copilot
- Your job is to monitor Gmail, classify incoming emails, extract structured deal information, and inject qualified items into ZakOps' quarantine for human review
- You do NOT approve deals, create deals, or modify deal state — that is ZakOps' responsibility

**Classification rules:**
- `deal_signal` — emails from brokers, intermediaries, or contacts that contain information about a potential acquisition target
- `operational` — emails related to deals already in progress
- `newsletter` — bulk email, market reports, industry newsletters
- `spam` — irrelevant, promotional, or junk

**Output requirements:**
- You MUST assemble the payload as a deterministic JSON object that matches the `zakops_inject_quarantine` tool schema exactly — 1:1 field correspondence, no extra keys, no missing required fields
- You MUST populate all required fields including `email_subject`, `sender`, `email_body_snippet`, `source_message_id`, `received_at`, `classification`, `schema_version`, `tool_version`, `prompt_version`, `langsmith_run_id`, `correlation_id`, `triage_summary`
- You MUST provide `extraction_evidence` and `field_confidences` for extracted entities
- You MUST set confidence honestly — reflect actual uncertainty
- You MUST NOT inject emails classified as `spam`
- You MUST NOT include extra fields beyond the defined schema

**Boundaries:**
- You do NOT have access to ZakOps deal state (until Phase 6)
- You do NOT approve or reject quarantine items
- You do NOT create deals
- You do NOT send emails unless explicitly delegated AND `send_email_enabled` is ON

### 3.2 Configure Sub-Agent Responsibilities

**Owner:** Zaks (LangSmith Agent Builder)  
**Verification:** Each sub-agent produces its expected output type

| Sub-Agent | Input | Output | Notes |
|-----------|-------|--------|-------|
| `triage_classifier` | Raw email content | `classification`, `urgency`, `confidence` | Runs first |
| `entity_extractor` | Raw email content | `company_name`, `broker_name`, `sender_name`, `sender_company`, `extraction_evidence`, `field_confidences` | Runs on deal_signal + operational |
| `policy_guard` | Classification + content | Pass/block | Blocks spam injection |
| `deal_researcher` | Extracted entities | Enrichment (optional) | Only if company found |
| `document_analyzer` | Attachment metadata | Attachment classification + structured array | Identifies CIMs, teasers, NDAs |
| `comms_drafter` | (Phase 6) | Draft email | Reserved |
| `calendar_coordinator` | (Phase 6) | Calendar event | Reserved |

### 3.3 Define the Email Processing Pipeline

```
Email arrives
  → triage_classifier: classify + urgency + confidence
  → IF spam → discard, stop
  → IF newsletter → inject with classification="newsletter", minimal extraction
  → IF deal_signal OR operational:
      → entity_extractor: extract entities + evidence + field_confidences
      → policy_guard: check content policies
      → IF has attachments → document_analyzer: classify + build attachments array
      → IF company found → deal_researcher: enrich (optional, time-boxed)
      → Assemble DETERMINISTIC JSON payload (1:1 with tool schema, no extra keys)
      → Validate payload locally before calling tool (all required fields present)
      → Call zakops_inject_quarantine
      → Log result with correlation_id
```

### 3.4 Deterministic Payload Assembly

**Owner:** Zaks (LangSmith Agent Builder)  
**Verification:** 20 injections → all payloads have identical key sets (no extra, no missing)

The final payload assembly must be structured and deterministic — not free-form LLM generation. Every payload that reaches `zakops_inject_quarantine` must have exactly the same key set, every time. The backend's strict validation (Phase 1.2) enforces this at the boundary, but Email Triage should validate locally before calling to reduce error rate.

### 3.5 Calibration Gate (Eval Set + Regression Check)

**Owner:** Zaks (LangSmith Agent Builder) + Claude (Builder)  
**Verification:** Eval set exists, baseline scores recorded, regression check runnable

Create a labeled evaluation set (20–50 emails) with known-correct values:

| Metric | Measurement | Minimum Baseline |
|--------|-------------|-----------------|
| Classification accuracy | % correct vs labeled set | ≥ 85% |
| Entity extraction recall | % of known entities extracted | ≥ 75% |
| Confidence calibration | Avg confidence on correct vs incorrect | Correct > Incorrect |
| False injection rate | % of spam/newsletter incorrectly injected as deal_signal | < 5% |

Run periodically (weekly or after prompt changes). If any metric regresses below baseline, revert the change.

### Gate 3

```
□ System prompt deployed to LangSmith Agent Builder
□ Sub-agent responsibilities documented and non-overlapping
□ Deterministic payload assembly: 20 injections → identical key sets, no extra keys
□ Backend strict validation catches malformed payloads (verified with intentionally bad payload)
□ 10 test emails: deal signals get full extraction, newsletters get minimal, spam discarded
□ Zero required-field NULLs on injected items
□ triage_summary present and meaningful on every injected item
□ confidence scores calibrated (not all 1.0 or all 0.5)
□ field_confidences differ from classification confidence where appropriate
□ extraction_evidence present for each extracted entity
□ Eval set created: 20+ labeled emails
□ Baseline scores recorded
□ Regression check runnable on demand
```

---

## Phase 4: Quarantine → Deal Pipeline (Promotion via Workflow Engine)

**Objective:** When an operator approves a quarantine item, the system produces full lifecycle artifacts through the workflow engine — not a raw insert. Includes duplicate prevention and undo capability.

### 4.1 Define the Quarantine-to-Deal Mapping

**Owner:** Claude (Builder) — Backend

| Quarantine Field | Maps To (Deal) | Notes |
|-----------------|----------------|-------|
| `company_name` (or operator-corrected) | `deal.name` | Falls back to `email_subject` if no company |
| `broker_name` (or operator-corrected) | `deal.broker` | Who introduced the deal |
| `sender` | `deal.source_email` | Original sender |
| `source_thread_id` | `deal.gmail_thread_id` | For auto-routing (Phase 5) |
| `classification` (or operator-corrected) | `deal.source_type` | How sourced |
| `triage_summary` | First event in deal timeline | Initial context |
| `email_body_snippet` | First event in deal timeline | Original email content |
| `attachments` | `deal.attachments` (metadata) | Associated documents |
| `correlation_id` | `deal.source_correlation_id` | Traceability back to injection |

### 4.2 Duplicate Deal Prevention

**Owner:** Claude (Builder) — Backend  
**Verification:** Approve a quarantine item whose `source_thread_id` already maps to an existing deal → email attached as timeline event, no new deal created

Before creating a new deal, check:

1. Does `source_thread_id` already exist in the deal-thread index?
2. If YES → do NOT create a new deal. Attach as timeline event on the existing deal. Update quarantine item: `status=approved`, `created_deal_id=existing_deal_id`. Inform operator: "Thread already linked to deal [name]. Email added to timeline."
3. If NO → create new deal via workflow engine

### 4.3 Promotion Must Use the Workflow Engine

**Owner:** Claude (Builder) — Backend  
**Verification:** Every approval produces all required lifecycle artifacts — if any is missing, the gate fails

Approve must produce ALL of the following in a single transaction:

| Artifact | Purpose |
|----------|---------|
| Deal row | The deal record in the deals table |
| `deal_transitions` record | Stage transition: `null → Initial Review` (or configured initial stage) |
| Outbox event | Event for downstream consumers (e.g., notifications, webhooks) |
| Audit trail entry | Who approved, when, from which quarantine item, with what corrections, correlation_id |
| Quarantine status update | `status=approved`, `approved_at`, `created_deal_id` |

If the transaction fails partway → full rollback. No orphaned deals without transitions. No transitions without audit entries.

### 4.4 Undo Approval / Correction Path

**Owner:** Claude (Builder) — Backend + Dashboard  
**Verification:** Admin reverts an approval → deal archived, quarantine item returns to pending

An admin must be able to:

1. Navigate to a recently approved quarantine item or deal
2. Trigger "Undo approval" (requires admin role)
3. The deal is soft-deleted (marked as reverted — audit trail preserved)
4. The quarantine item returns to `status=pending` with note: "Approval reverted by [admin], reason: [reason]"
5. The undo is logged as its own audit entry with `correlation_id`

### 4.5 Update Deals View to Show Source

**Owner:** Claude (Builder) — Dashboard  
**Verification:** Deals created from quarantine show source indicator

Deals from quarantine are visually distinguishable from manually created deals.

### Gate 4 — Promotion Must Produce Full Lifecycle Artifacts

```
□ Quarantine-to-deal field mapping documented and implemented
□ Operator corrections flow into created deal
□ Duplicate prevention: same thread_id → attaches to existing deal, no duplicate
□ Approve produces ALL artifacts: deal + deal_transitions + outbox event + audit entry + quarantine status update
□ If any artifact missing from approve → FAIL
□ Transaction rollback: partial failure → no orphaned state
□ Deal appears in pipeline at correct initial stage
□ Deal timeline shows creation event with quarantine context and correlation_id
□ source_thread_id registered in deal-thread index on approve
□ Undo approval: admin reverts → deal archived, quarantine returns to pending, logged
□ Deals view shows source indicator
□ 5 quarantine items approved → correct artifacts produced (accounting for thread dedup)
```

---

## Phase 5: Auto-Routing (Approved Deals Bypass Quarantine)

**Objective:** Future emails for approved deals skip quarantine and sync to the deal timeline — with conflict handling and operator override.

Controlled by the `auto_route` feature flag (Phase 0). When OFF, all emails go through quarantine.

### 5.1 Build the Deal-Thread Index

**Owner:** Claude (Builder) — Backend  
**Verification:** Query returns correct deal ID for a known thread ID

Populated on approve (Phase 4.3). Supports manual linking. Inactive deals retain mappings marked inactive.

### 5.2 Pre-Injection Routing Check

**Owner:** Claude (Builder) — Backend API (MCP bridge)  
**Verification:** Thread match → deal timeline; no match → quarantine; conflict → quarantine with reason

1. Check `auto_route` flag. OFF → quarantine.
2. Look up `source_thread_id` in deal-thread index
3. **Single match:** Route to deal timeline (bypass quarantine)
4. **Multiple matches (conflict):** Route to quarantine with `routing_conflict=true`, `routing_conflict_reason="Thread maps to deals: [id1], [id2]"` — operator resolves
5. **No match:** Quarantine as normal

Response always includes `routing_reason`:

```json
{
  "routed_to": "deal" | "quarantine",
  "deal_id": "uuid or null",
  "quarantine_id": "uuid or null",
  "routing_reason": "thread_match" | "no_match" | "routing_conflict" | "auto_route_disabled",
  "routing_conflict_deals": ["uuid1", "uuid2"]
}
```

### 5.3 Conflict Resolution UI

**Owner:** Claude (Builder) — Dashboard  
**Verification:** Conflict items show the conflicting deals; operator can choose

### 5.4 Operator Override: Re-Link Thread → Deal

**Owner:** Claude (Builder) — Dashboard + Backend  
**Verification:** Re-link a thread from Deal A to Deal B → future emails route to Deal B

Operator can: view current mappings, remove a mapping, add a mapping, move a mapping between deals. All changes logged.

### 5.5 Email Triage Awareness

Email Triage always includes `source_thread_id`. Handles all response types. Logs `routing_reason`. Does not change behavior based on routing outcome.

### Gate 5

```
□ Deal-thread index populated on approve
□ auto_route OFF: all emails → quarantine regardless of thread match
□ auto_route ON + single match: email → deal timeline
□ auto_route ON + multiple matches: email → quarantine with routing_conflict + reason
□ auto_route ON + no match: email → quarantine
□ routing_reason in every tool response
□ Conflict resolution UI shows conflicting deals
□ Operator can re-link thread → deal (add/remove/move)
□ All re-link operations logged
□ End-to-end: approve deal → follow-up email → appears in deal timeline
□ End-to-end: thread linked to 2 deals → quarantine with conflict reason
```

---

## Phase 6: Collaboration Contract (Async-First Delegation & Feedback)

**Objective:** Structured delegation between ZakOps and Email Triage — async-first with state machine, retries, dead-letter, and permission controls.

Controlled by `delegate_actions` and `send_email_enabled` feature flags.

### 6.1 Delegated Tasks State Machine

**Owner:** Claude (Builder) — Backend

`delegated_tasks` table:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | uuid | Primary key + idempotency key |
| `deal_id` | uuid | Related deal |
| `task_type` | enum | send_email, schedule_meeting, research |
| `payload` | jsonb | Task-specific content |
| `requested_by` | string | Operator who initiated |
| `status` | enum | pending, queued, executing, completed, failed, dead_letter |
| `attempts` | integer | Execution attempts |
| `max_attempts` | integer | Default 3 |
| `result` | jsonb | Structured result from Email Triage |
| `error` | text | Error if failed |
| `created_at` / `completed_at` | datetime | Timestamps |
| `correlation_id` | string | End-to-end correlation |

State machine: `pending → queued → executing → completed | failed → queued (retry) | dead_letter`

### 6.2 Permission Model for Email Sending

No outbound email without explicit operator confirmation. This is a hard rule regardless of feature flag state.

Flow: ZakOps drafts → operator reviews in UI → operator confirms "Send" → task created → Email Triage executes → result logged on timeline.

### 6.3 Feedback Loop

Every task returns structured result. ZakOps logs on deal timeline. Failed tasks retry up to max_attempts. Dead-lettered tasks surface to operator.

### 6.4 Mutual State Awareness — New Tools

**`zakops_get_deal_status`**: Read deal state by deal_id or thread_id  
**`zakops_list_recent_events`**: Read recent deal timeline events (limit N)

These enable Email Triage to catch up on deal context safely before executing delegated actions.

### Gate 6

```
□ delegated_tasks table with full state machine
□ Retry logic: failed → re-queued up to max_attempts → dead_letter
□ delegate_actions flag controls availability
□ send_email_enabled flag controls outbound email separately
□ Email sending requires explicit operator confirmation
□ Structured feedback for every completed task
□ Task results logged on deal timeline
□ Dead-lettered tasks surface to operator
□ zakops_get_deal_status tool exists and returns deal state
□ zakops_list_recent_events tool exists and returns timeline
□ End-to-end: operator triggers send → Email Triage sends → result on timeline
```

---

## Phase 7: Document Handling, Security & Operational Hardening

**Objective:** Attachments, layered security independent of LangSmith, key management, data retention, PII, resilience, and audit trail.

### 7.1 Document Retrieval from Emails

Attachment metadata flows from email through quarantine to deal on approve. Operators can view/download. Gated links displayed with "requires authentication" notice.

### 7.2 MCP Bridge Security — Do Not Depend on LangSmith

Layered, independent of LangSmith's secret handling:

**Layer 1 — Cloudflare Access service token** (infrastructure-level, edge protection)  
**Layer 2 — Bearer auth on MCP bridge** (application-level)  
**Layer 3 (future) — mTLS** (cryptographic identity)

Minimum for Gate 7: Layers 1 and 2 in place.

### 7.3 Key Rotation and Secret Hygiene

- Bearer token rotatable without downtime (accept old + new during rotation window)
- Cloudflare Access token rotation documented
- Log redaction: no secrets in log output
- No secrets in source code or committed config

### 7.4 Data Retention and PII Rules

- Retention periods configurable per data type
- PII access role-gated
- Deletion supported (GDPR/CCPA if applicable)

### 7.5 Error Handling and Resilience

- Injection failure → logged, retried (not silently dropped)
- Backend unreachable → error response, Email Triage retries
- Approval midway failure → full transaction rollback
- LLM down → Email Triage degrades gracefully
- Delegated task failure → retry → dead-letter

### 7.6 Audit Trail

Every step logged with `correlation_id`: email received, quarantine created, operator action, deal created, auto-routed, delegated task, undo approval.

### Gate 7

```
□ Attachment metadata flows email → quarantine → deal
□ Gated links displayed with auth notice
□ MCP bridge protected by Cloudflare Access (Layer 1) + Bearer auth (Layer 2)
□ Security NOT dependent on LangSmith secret interpolation
□ Key rotation procedure documented with explicit fast steps — tested
□ Log redaction: no secrets in logs
□ No secrets in source code
□ Data retention policy documented
□ PII access role-gated
□ Error handling tested for all failure modes
□ No data loss in any tested failure scenario
□ Full audit trail with correlation_id end-to-end
```

---

## Phase 8: Operational Excellence Gate

**Objective:** Prove the system is production-ready through SLOs, load testing, disaster recovery, and shadow-mode measurement readiness.

### 8.1 Service Level Objectives

| SLO | Target | Measurement |
|-----|--------|-------------|
| Injection latency | < 30s (p95) | `received_at` vs `created_at` delta |
| Quarantine UI load | < 2s (p95) | Frontend performance |
| Approve → deal latency | < 3s (p95) | `approved_at` vs deal `created_at` delta |
| Auto-route latency | < 30s (p95) | `received_at` vs timeline event delta |
| Availability | 99.5% uptime | Health check monitoring |
| Data loss rate | 0% | Every email either injected, auto-routed, or discarded with log entry |
| Classification accuracy | ≥ 85% | Periodic eval run (Phase 3.5) |

### 8.2 Monitoring and Alerting

- Health checks: all services polled every 60s
- Queue depth alerts: pending items > threshold for > duration
- Kill switch activation alert
- Error rate threshold alerts
- Dead-letter queue depth alert
- Feature flag change logging

### 8.3 Load Test

| Metric | Target | Method |
|--------|--------|--------|
| Emails/day | 100 → 500+ | Simulated injection against staging |
| Concurrent reviewers | 3–5 operators | Simulated concurrent actions |
| Auto-route throughput | N emails/min for active threads | Simulated follow-ups |
| Peak burst | 50 emails in 5 minutes | Simulated CIM blast |

Verify: no dropped emails, SLOs met under load, dedup holds under concurrency, optimistic locking holds, DB stable.

### 8.4 Disaster Recovery

- All 3 databases backed up on schedule
- Restore test: full restore to staging, system operational
- Email replay: failed injections replayed from log, idempotency ensures safety
- Replay procedure documented and tested

### 8.5 Shadow-Mode Isolation + Measurement Readiness

**Verification:** Shadow pilot can be measured cleanly for one week

```
□ API and UI filtering for langsmith_shadow works deterministically
□ Shadow items do NOT appear under other source types
□ langsmith_live does NOT appear anywhere during shadow pilot
□ Measurement fields (confidence/classification/enrichment) have documented rules:
  what Email Triage sets vs what ZakOps computes — decided once, not per-item
□ One-week shadow run produces clean, filterable dataset for accuracy measurement
```

### Gate 8 (Final Production Gate)

```
□ SLOs defined and documented
□ Monitoring and alerts configured and tested
□ Load test completed — all SLOs met under load
□ No dropped emails under load
□ No duplicate records under concurrent injection
□ No duplicate deals under concurrent approval
□ Backup runs on schedule for all 3 databases
□ Restore test completed: full restore, system operational
□ Email replay procedure documented and tested (idempotent replay)
□ 7-day shadow burn-in completed with SLOs met
□ Shadow-mode measurement: clean dataset, filterable, accuracy measurable
□ Feature flags set for production: shadow_mode=ON, auto_route=OFF, delegate_actions=OFF, send_email_enabled=OFF
□ Kill switch tested and ready
□ System declared production-ready
```

---

## Phase Summary

| Phase | Objective | Dependencies | Estimated Effort |
|-------|-----------|-------------|-----------------|
| **0. Production Envelope** | Environments, flags, idempotency verification, correlation, kill switch, security perimeter | None | 2–3 days |
| **1. Schema & Data Contract** | Audit-grade quarantine schema with versioning, evidence, golden test | Phase 0 | 2–3 days |
| **2. Quarantine UI** | Multi-operator workflow with locking, edits, escalation, filters, concurrency | Phase 1 | 3–4 days |
| **3. Email Triage Prompt** | Agent config with deterministic payloads, guardrails, calibration | Phase 1 | 2–3 days |
| **4. Deal Pipeline** | Promotion via workflow engine with full artifacts, dedup, undo | Phase 2 | 2–3 days |
| **5. Auto-Routing** | Thread-based bypass with conflict handling and operator override | Phase 4 | 3–4 days |
| **6. Collaboration Contract** | Async delegation with state machine, retries, dead-letter, permissions | Phase 4 | 4–6 days |
| **7. Security & Hardening** | Layered auth, key rotation, retention, PII, resilience, audit | Phase 5+ | 4–6 days |
| **8. Operational Excellence** | SLOs, monitoring, load test, DR, shadow measurement, production gate | All prior | 3–5 days |

**Total estimated effort:** 25–37 working days

---

## Execution Rules

1. **Sequential phases.** Do not start Phase N+1 until Phase N's gate passes.
2. **Phase 0 is non-negotiable.** Security perimeter, idempotency verification, and kill switch must exist before any data flows.
3. **Schema first.** Phase 1 is the contract between all builders. Every downstream phase depends on it.
4. **Do not re-implement hardened primitives.** Backend dedup, correlation, rate limiting, and source_type filtering are already QA-verified. Verify they work. Do not rebuild them.
5. **Promotion uses the workflow engine.** Approve → Deal is not a raw insert. It produces deal + transitions + outbox + audit. If any artifact is missing, the gate fails.
6. **Canonical constants only.** `langsmith_shadow`, `langsmith_live`, `message_id` — no synonyms, no alternatives.
7. **Both builders coordinate.** Some phases require work from both sides. Neither can finish alone.
8. **Verification is not optional.** "It should work" is not a pass. Demonstrated behavior is a pass.
9. **No side fixes.** Document issues within the current phase or queue for the right phase.
10. **Feature flags control rollout.** Shadow mode first, capabilities enabled independently after gates pass.
11. **One source of truth.** This document is the roadmap. Updates go here.

---

*Prepared: February 14, 2026*  
*Version: 2.1 — Production-grade with ground-truth corrections, canonical constants, workflow engine requirement, shadow isolation, and operational excellence*  
*This document supersedes all previous versions, integration briefs, fix lists, and incremental plans.*

---

## Run Index

### Run: 20260214-1837-vr21exec

**Plan file:** `/home/zaks/bookkeeping/docs/VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md`
**Date:** 2026-02-14
**Author:** Claude Code (Builder)

**Top 10 Execution Priorities:**

1. **P0-T6: Restore real auth on MCP bridge** — AUTH BYPASS ACTIVE, highest security risk
2. **P0-T1: Feature flags table + runtime API** — unlocks kill switch, shadow mode, all flag-gated features
3. **P0-T2: Kill switch integration** — emergency stop for Email Triage writes
4. **P1-T1: Database schema expansion** — add 17 columns for canonical quarantine item
5. **P1-T6: Update bridge tool schema** — expand from 8 to 25+ params, strict validation
6. **P1-T5: Fix "Preview not found"** — inline email_body_snippet storage
7. **P2-T3: Optimistic locking** — version column + 409 Conflict for concurrent access
8. **P2-T2: Fix detail view** — triage summary, extraction evidence, traceability sections
9. **P2-T1: Fix list view** — sender_name, confidence indicator, urgency color coding
10. **P4-T2: Duplicate deal prevention** — thread_id check before deal creation

**Decisions Required from Orchestrator:**

| # | Decision | Recommendation |
|---|----------|----------------|
| D1 | Security perimeter: CF Access vs IP allowlist vs both | CF Access (infrastructure-level, independent of LangSmith) |
| D2 | Preview storage: inline vs fetch-on-demand | Inline (Option A — no runtime dependency) |
| D4 | Phase 3 execution: who configures LangSmith agent? | Zaks implements; Claude provides specs |
| D6 | Schema version enforcement: reject unknown vs warn | Reject (forward-compat guard) |

**Gates to Run First:**
- G0-04, G0-05 (kill switch) — safety prerequisite
- G0-09, G0-11 (auth restored) — security prerequisite
- G1-09 (golden payload test) — proves end-to-end schema contract
- G2-09 (optimistic locking) — proves concurrency safety
