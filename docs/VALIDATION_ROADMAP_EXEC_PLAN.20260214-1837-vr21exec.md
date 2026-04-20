# VALIDATION_ROADMAP_EXEC_PLAN — COL-GAP-FULLSTACK + Email Triage Operational Readiness

**Run ID:** `20260214-1837-vr21exec`
**Source:** `ZakOps-MA-Copilot-Validation-Roadmap-v2.1.md`
**Date:** 2026-02-14
**Author:** Claude Code (Builder)
**Status:** APPROVED — patches v1 applied (9 patches + 7 decisions resolved)

---

## 1. Current Ground Truth Snapshot

### Verified Working (Code-Grounded Facts)

| Component | Evidence | Files |
|-----------|----------|-------|
| **Quarantine table** with UNIQUE message_id, CHECK status (pending/approved/rejected/hidden), correlation_id, source_type | `db/init/001_base_tables.sql:210-241`, `db/migrations/029_quarantine_hardening.sql` | zakops-backend |
| **Message_id dedup** — ON CONFLICT DO NOTHING, returns 200 (dedup) vs 201 (created) | `main.py:1558-1579` | zakops-backend |
| **Source_type validation** — 5 valid types, unknown → 400 | `main.py:277,1531-1542` (VALID_SOURCE_TYPES set) | zakops-backend |
| **Correlation ID middleware** — X-Correlation-ID/X-Trace-ID, 128-char max, stored on quarantine, forwarded to outbox | `middleware/trace.py:72-106`, `main.py:1529` | zakops-backend |
| **Rate limiting** — 120/min quarantine, 60/min general, in-memory sliding window | `shared/security.py:102-173` | zakops-backend |
| **Backend X-API-Key auth** — fail-closed for /api/quarantine* (503 if key unset) | `middleware/apikey.py:38-46` | zakops-backend |
| **Idempotency middleware** — Idempotency-Key header, 24h TTL, fail-closed | `middleware/idempotency.py` | zakops-backend |
| **Quarantine approve → deal** — atomic transaction producing: deal + deal_transitions + deal_events + outbox + quarantine status update | `main.py:1724-1903` | zakops-backend |
| **Deal_transitions table** — exists, used by workflow.py (line 227-246) and quarantine approval (line 1827-1838) | `db/migrations/031_deal_transitions_ledger.sql` | zakops-backend |
| **Outbox pattern** — full implementation, OUTBOX_ENABLED env var, pending→delivered state machine | `core/outbox/writer.py`, `db/migrations/001_foundation_tables.sql:146-177` | zakops-backend |
| **Deal workflow engine** — FSM with valid transitions, FOR UPDATE locking, idempotent transitions | `core/deals/workflow.py:105-325` | zakops-backend |
| **Email threads table** — deal_id + thread_id mapping, provider support | `db/migrations/022_email_integration.sql:34-51` | zakops-backend |
| **MCP bridge** — dual transport (SSE /sse + Streamable HTTP /mcp), 13 tools, connected to LangSmith | `/home/zaks/scripts/agent_bridge/mcp_server.py` | scripts |
| **Dashboard quarantine page** — list + detail + approve/reject/delete + source_type filter + bulk delete | `apps/dashboard/src/app/quarantine/page.tsx` | monorepo |
| **Dashboard deal transitions display** — "Stage Transitions Ledger" tab in deal detail | `apps/dashboard/src/app/deals/[id]/page.tsx:1273-1321` | monorepo |
| **Cloudflare tunnel** — `zakops-bridge.zaksops.com` → `localhost:9100`, systemd service, running | `~/.cloudflared/config.yml` | infrastructure |
| **LangSmith connection** — 13 tools discovered, zakops_inject_quarantine executes, 5 emails injected 2026-02-14 | Bridge logs, DB verification | verified live |

### Integrated but NOT Operational

| Component | Gap | Evidence |
|-----------|-----|----------|
| **Bridge inject tool schema** | Only 8 params (message_id, sender, subject, body_text, correlation_id, classification, company_name, urgency). Missing: email_subject, sender_name, sender_domain, sender_company, broker_name, received_at, email_body_snippet, triage_summary, source_thread_id, confidence, schema_version, tool_version, prompt_version, langsmith_run_id, extraction_evidence, field_confidences, attachments | `mcp_server.py:685-694` |
| **Backend QuarantineCreate model** | Has more fields than bridge sends (email_subject, sender_domain, sender_name, sender_company, is_broker, raw_body, injection_metadata) but bridge passes "subject" not "email_subject", and body goes as "body_text" which maps to body_preview | `main.py:255-273` |
| **Quarantine preview** | Detail view fetches from `/api/quarantine/{item_id}` but preview depends on quarantine_dir filesystem path (email_sync flow). LangSmith items have NO quarantine_dir → "Preview not found" | `quarantine/page.tsx:143-157`, backend GET endpoint |
| **source_type=langsmith_shadow hardcoded** in bridge tool | No runtime flag — always sends langsmith_shadow regardless of any config | `mcp_server.py:728` |
| **Quarantine DB columns** | Missing first-class columns for: email_body_snippet, triage_summary, source_thread_id, schema_version, tool_version, prompt_version, langsmith_run_id, langsmith_trace_url, extraction_evidence (JSONB), field_confidences (JSONB), attachments (JSONB). Some could go in raw_content but roadmap requires searchable/filterable fields | DB schema vs roadmap §1.1 |

### Not Implemented (NEEDS VERIFICATION = none; confirmed absent in code)

| Component | Status | Roadmap Phase |
|-----------|--------|---------------|
| Feature flag table/service (shadow_mode, auto_route, delegate_actions, send_email_enabled) | **Absent** — only env vars exist | Phase 0.2 |
| Kill switch (email_triage_writes_enabled) | **Absent** — no endpoint, no flag, no mechanism | Phase 0.5 |
| ZAKOPS_ENV environment model | **Absent** — backend uses ENVIRONMENT var for cookies only | Phase 0.1 |
| Optimistic locking / version field on quarantine_items | **Absent** — no `version` column | Phase 2.4 |
| Escalate action | **Absent** — no UI, no backend status value | Phase 2.3 |
| Approve with Edits | **Absent** — no UI for operator corrections | Phase 2.3 |
| Duplicate deal prevention (thread_id check before creation) | **Absent** — quarantine_items has no source_thread_id column | Phase 4.2 |
| Undo approval | **Absent** — no endpoint, no UI | Phase 4.4 |
| Auto-routing (pre-injection thread check) | **Absent** — no routing logic in injection path | Phase 5.2 |
| Delegated tasks table/state machine | **Absent** — actions table exists but not delegation-specific | Phase 6.1 |
| MCP bridge auth (real perimeter) | **BYPASSED** — temporary auth bypass on all MCP paths | Phase 0.6 |
| Key rotation procedure | **Absent** — manual .env updates only | Phase 0.6 |
| Cloudflare Access service token | **Absent** — tunnel has no edge protection | Phase 7.2 |
| Confidence filtering, urgency sorting | **Absent in UI** — fields exist in schema but no filter controls | Phase 2.5 |
| Deals page source indicator | **Absent** — no quarantine origin shown on deals | Phase 4.5 |

---

## 2. Target Operational Definition

**"Operational Quarantine" Checklist** — every item must PASS for the system to be declared operational:

| # | Criterion | Measurable Acceptance |
|---|-----------|----------------------|
| OQ-01 | Every LangSmith-injected item renders with real subject | Zero "Unknown subject" for items with populated email_subject |
| OQ-02 | Every item has readable preview | Zero "Preview not found" — email_body_snippet always populated and rendered |
| OQ-03 | Approve produces full lifecycle artifacts | deal + deal_transitions + deal_events + outbox + quarantine status — all 5 present per approval |
| OQ-04 | Reject requires reason | UI enforces required reject_reason (not optional) |
| OQ-05 | Concurrent operators don't corrupt state | Optimistic locking: 2 simultaneous approve → 1 success, 1 conflict (409) |
| OQ-06 | Shadow items are isolated | langsmith_shadow items never appear under other source filters |
| OQ-07 | Kill switch stops all writes in < 1s | Flip flag → zakops_inject_quarantine returns 503, reads still work |
| OQ-08 | Bridge auth is real (not bypassed) | curl with no token → 401/403, not 200 |
| OQ-09 | Schema contract is enforced | Missing required field → tool rejects with error naming missing fields |
| OQ-10 | Dedup holds under concurrency | 5 identical message_id injections → exactly 1 record |
| OQ-11 | Triage summary visible to operator | Every item with triage_summary shows it in detail panel |
| OQ-12 | Extraction evidence visible | Per-field confidence + evidence text shown in detail view |
| OQ-13 | Correlation traceable end-to-end | correlation_id on quarantine → deal_transitions → deal_events → outbox |
| OQ-14 | Source type tags visible | List view shows shadow/live badge; detail view shows full source_type |

---

## 3. Phase Plan (Dependency-Aware)

### Dependency Graph

```
Phase 0 (Safety & Perimeter)
    │
    ▼
Phase 1 (Canonical Schema + Contract Enforcement)
    │
    ├───────────────────────────────┐
    ▼                               ▼
Phase 2 (Quarantine UX)            Phase 3 (Email Triage Config — Zaks/LangSmith)
    │                               │
    ▼                               │
Phase 4 (Promotion Pipeline)        │
    │                               │
    ├───────────────────────────────┘
    │
    ▼
Phase 5 (Auto-Routing)  ←  Feature flag: auto_route
    │
    ▼
Phase 6 (Collaboration Contract)  ←  Feature flags: delegate_actions, send_email_enabled
    │
    ▼
Phase 7 (Security & Hardening)
    │
    ▼
Phase 8 (Operational Excellence Gate)
```

---

### Phase 0: Safety & Perimeter

**Objective:** Establish environment model, feature flags, verify existing primitives, add kill switch, restore real auth on bridge.

**Scope:** Backend + MCP Bridge + Infrastructure

**Dependencies:** None

**Owner:** Claude (Builder)

#### Tasks

**P0-T1: Feature Flags Table + Runtime API**
- Create migration `032_feature_flags.sql`:
  ```sql
  CREATE TABLE zakops.feature_flags (
      flag_name VARCHAR(100) PRIMARY KEY,
      flag_value BOOLEAN NOT NULL DEFAULT FALSE,
      description TEXT,
      updated_by VARCHAR(255) DEFAULT 'system',
      updated_at TIMESTAMPTZ DEFAULT NOW()
  );
  INSERT INTO zakops.feature_flags VALUES
    ('shadow_mode', true, 'Tag Email Triage injections as langsmith_shadow', 'system', NOW()),
    ('auto_route', false, 'Enable auto-routing bypass for approved deal threads', 'system', NOW()),
    ('delegate_actions', false, 'Enable delegation from ZakOps to Email Triage', 'system', NOW()),
    ('send_email_enabled', false, 'Allow Email Triage to send outbound emails', 'system', NOW()),
    ('email_triage_writes_enabled', true, 'Master kill switch for all Email Triage write ops', 'system', NOW());
  ```
- Add `GET /api/admin/flags` + `PUT /api/admin/flags/{name}` endpoints (admin-only, X-API-Key required)
- Add `get_flag(name)` helper function with 60s TTL in-memory cache (avoid DB hit per request)
- **Files:** NEW `db/migrations/032_feature_flags.sql`, EDIT `main.py` (add admin endpoints), NEW `src/core/feature_flags.py`

**P0-T2: Kill Switch Integration**
- In quarantine POST endpoint (`main.py:~1510`), before rate limit check:
  ```python
  if not await get_flag('email_triage_writes_enabled'):
      return JSONResponse(status_code=503, content={"error": "writes_disabled", "reason": "Kill switch active"})
  ```
- Similarly gate delegated task execution (future Phase 6)
- Read operations (`GET /api/quarantine`, health) remain unaffected
- **Files:** EDIT `main.py`

**P0-T3: Shadow Mode Flag Wiring**
- Replace hardcoded `"langsmith_shadow"` in bridge tool (`mcp_server.py:728`) with flag-aware logic:
  - Bridge calls `GET /api/admin/flags/shadow_mode` on startup + caches
  - If shadow_mode=true → source_type="langsmith_shadow"
  - If shadow_mode=false → source_type="langsmith_live"
- Add startup log: "Shadow mode: ON/OFF"
- **Files:** EDIT `mcp_server.py`

**P0-T4: Verify Existing Idempotency (Test, Don't Reimplement)**
- Script: 5 concurrent identical message_id POSTs → assert exactly 1 DB record
- Script: Simulate DB constraint failure → assert 500 (not silent bypass)
- **Files:** NEW evidence script (one-shot, not committed)

**P0-T5: Verify & Wire Correlation ID End-to-End**
- Inject with X-Correlation-ID → verify it appears in: quarantine_items.correlation_id, deal_transitions.correlation_id (after approve), outbox.correlation_id
- If any link in the chain is broken (correlation_id not propagated to deal_transitions or outbox), **fix it** — don't just document the gap
- Wire the bridge tool to always generate a correlation_id if LangSmith doesn't provide one: `correlation_id = correlation_id or f"et-{uuid4().hex[:12]}"`
- **Files:** EDIT `mcp_server.py` (if wiring needed), NEW evidence script

**P0-T6: Restore Bearer Auth on MCP Bridge (Layer 2 — Code Only)**
- Remove the auth bypass block (`mcp_server.py:157-170`) entirely
- Restore Bearer auth (existing BearerAuthMiddleware) on all MCP paths (`/mcp`, `/sse`, `/messages/`)
- The middleware already validates `ZAKOPS_BRIDGE_API_KEY` — removing the bypass re-enables it
- Add IP allowlist as secondary check: allow LangSmith IPs (34.59.65.97, 35.188.222.201, 34.9.99.224) + localhost to pass Bearer auth; block all others outright
- Verify: `curl` with no token → 401; `curl` with wrong token → 401; `curl` with correct token → 200
- **Note:** This is Layer 2 only (application-level). Layer 1 (Cloudflare Access) is added in Phase 7.
- **Files:** EDIT `mcp_server.py`

**P0-T7: Key Rotation Procedure**
- Document in `/home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md`:
  1. Generate new key: `openssl rand -hex 32`
  2. Update bridge .env + restart (zero-downtime: accept both old+new during window)
  3. Update LangSmith config
  4. Remove old key after confirmation
  5. Update backend ZAKOPS_API_KEY if needed
- **Files:** NEW `bookkeeping/docs/KEY-ROTATION-RUNBOOK.md`

**P0-T8: ZAKOPS_ENV Environment Variable**
- Add to backend startup: `ZAKOPS_ENV = os.getenv("ZAKOPS_ENV", "dev")`
- Log environment on startup
- Feature flags default differently per environment (table seed handles prod defaults)
- **Files:** EDIT backend config

**P0-T9: Migration Number Safety Check**
- Before creating ANY migration file, run: `ls /home/zaks/zakops-backend/db/migrations/ | sort -n | tail -5` to verify the next available number
- This plan assumes 032 (feature flags), 033 (schema expansion), 034 (escalate), 035 (delegated tasks) — but numbers may have shifted due to COL QA remediations or other concurrent work
- If a conflict is found, renumber ALL plan migrations accordingly and update all references in this document
- **This is a pre-flight check, not a code change** — run it at the START of Phase 0 before writing any SQL

#### Gate 0

```
□ G0-01: Feature flags table exists with 5 flags, all queryable via API
□ G0-02: shadow_mode=ON → injected items tagged source_type=langsmith_shadow (exact string)
□ G0-03: Unknown source_type → 400 rejection with clear error (EXISTING — verify)
□ G0-04: Kill switch ON → zakops_inject_quarantine returns 503 within 1s; reads still work
□ G0-05: Kill switch OFF → normal operation resumes
□ G0-06: 5 concurrent identical message_id → exactly 1 record (EXISTING — verify)
□ G0-07: correlation_id present on quarantine item + in log entries (EXISTING — verify)
□ G0-08: correlation_id returned in tool response (EXISTING — verify)
□ G0-09: MCP bridge rejects unauthenticated requests (auth bypass removed)
□ G0-10: Key rotation procedure documented with explicit commands
□ G0-11: curl with no auth to bridge → 401/403 (not 200)
□ G0-12: langsmith_live does NOT appear anywhere during shadow pilot
```

**Evidence:** SQL queries showing flags, curl transcripts, concurrent test output, correlation_id trace

**Rollback:** Drop migration 032, revert main.py changes, bridge reverts to current state (bypass still active)

---

### Phase 1: Canonical Schema + Contract Enforcement

**Objective:** Expand quarantine schema to support all roadmap-required fields. Update bridge tool contract. Ensure "Preview not found" is eliminated.

**Scope:** Backend DB + Backend API + MCP Bridge tool

**Dependencies:** Phase 0

#### Tasks

**P1-T1: Database Schema Expansion**
- Migration `033_quarantine_schema_v2.sql`:
  ```sql
  ALTER TABLE zakops.quarantine_items
    ADD COLUMN IF NOT EXISTS email_subject VARCHAR(500),
    ADD COLUMN IF NOT EXISTS sender_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS sender_domain VARCHAR(255),
    ADD COLUMN IF NOT EXISTS sender_company VARCHAR(255),
    ADD COLUMN IF NOT EXISTS broker_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS email_body_snippet TEXT,
    ADD COLUMN IF NOT EXISTS triage_summary TEXT,
    ADD COLUMN IF NOT EXISTS source_thread_id VARCHAR(255),
    ADD COLUMN IF NOT EXISTS schema_version VARCHAR(20),
    ADD COLUMN IF NOT EXISTS tool_version VARCHAR(20),
    ADD COLUMN IF NOT EXISTS prompt_version VARCHAR(100),
    ADD COLUMN IF NOT EXISTS langsmith_run_id VARCHAR(255),
    ADD COLUMN IF NOT EXISTS langsmith_trace_url TEXT,
    ADD COLUMN IF NOT EXISTS extraction_evidence JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS field_confidences JSONB DEFAULT '{}',
    ADD COLUMN IF NOT EXISTS attachments JSONB DEFAULT '[]',
    ADD COLUMN IF NOT EXISTS confidence FLOAT,
    ADD COLUMN IF NOT EXISTS received_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS company_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS urgency VARCHAR(20) DEFAULT 'normal';
  -- Note: existing `subject` column (VARCHAR 500) preserved for backward compat
  -- email_subject is the canonical display field; `subject` retained for email_sync flow
  CREATE INDEX IF NOT EXISTS idx_qi_source_thread_id ON zakops.quarantine_items(source_thread_id) WHERE source_thread_id IS NOT NULL;
  CREATE INDEX IF NOT EXISTS idx_qi_schema_version ON zakops.quarantine_items(schema_version);
  ```
- Rollback: `033_quarantine_schema_v2_rollback.sql`
- **Files:** NEW migration + rollback

**P1-T2: Update QuarantineCreate Pydantic Model**
- Add all new fields to `QuarantineCreate` with appropriate types and validation
- Add `schema_version` validation: reject unknown versions (initially accept "1.0.0" only)
- Add strict validation: reject extra keys beyond defined schema (Pydantic `model_config = ConfigDict(extra='forbid')`)
- Required fields for LangSmith source: email_subject, sender, classification, source_message_id, schema_version, correlation_id
- **Files:** EDIT `main.py` (QuarantineCreate model)

**P1-T3: Update QuarantineResponse Model**
- Add all new fields so they're returned in API responses
- Add computed `display_subject` field: `COALESCE(email_subject, subject)` in the SELECT query — ensures backward compat with legacy `email_sync` items that only have `subject`
- **Files:** EDIT `main.py` (QuarantineResponse model + GET query)

**P1-T4: Update Quarantine POST Endpoint**
- Map `source_message_id` → `message_id` at boundary (bridge sends source_message_id, backend stores as message_id)
- Store email_body_snippet (required, 500 char max — truncate if longer)
- Store all new fields in their dedicated columns
- Validate required fields when source_type starts with "langsmith_": reject if email_subject, sender, classification, schema_version, or correlation_id are missing
- **Files:** EDIT `main.py` (create_quarantine endpoint)

**P1-T5: Fix "Preview Not Found" — Option A (Inline Storage)**
- Store `email_body_snippet` in dedicated column (always populated for LangSmith items)
- Store `raw_body` in raw_content JSONB under key `email_body_full` (optional, for "Expand" button)
- Update `GET /api/quarantine/{item_id}` to return email_body_snippet and triage_summary directly (no filesystem dependency)
- **Files:** EDIT `main.py` (GET endpoint response)

**P1-T6: Update Bridge Tool — Expanded Schema**
- Rewrite `zakops_inject_quarantine` tool with full roadmap schema:
  ```python
  @mcp.tool()
  def zakops_inject_quarantine(
      source_message_id: str,       # Canonical dedup key (mapped to message_id)
      email_subject: str,           # Required
      sender: str,                  # Required
      classification: str,          # Required: deal_signal, operational, newsletter
      schema_version: str,          # Required: "1.0.0"
      correlation_id: str,          # Required
      # Display-critical
      sender_name: Optional[str] = None,
      sender_domain: Optional[str] = None,
      sender_company: Optional[str] = None,
      received_at: Optional[str] = None,
      email_body_snippet: str,                    # Required — 500 char max (eliminates "Preview not found")
      triage_summary: Optional[str] = None,
      # Extraction
      company_name: Optional[str] = None,
      broker_name: Optional[str] = None,
      urgency: Optional[str] = None,     # HIGH, MEDIUM, LOW
      confidence: Optional[float] = None,
      extraction_evidence: Optional[dict] = None,
      field_confidences: Optional[dict] = None,
      # Threading & traceability
      source_thread_id: Optional[str] = None,
      tool_version: Optional[str] = None,
      prompt_version: Optional[str] = None,
      langsmith_run_id: Optional[str] = None,
      langsmith_trace_url: Optional[str] = None,
      # Attachments
      attachments: Optional[list] = None,
  ) -> dict:
  ```
- Bridge maps `source_message_id` → `message_id` in payload
- Bridge reads `shadow_mode` flag to set `source_type`
- Validate required fields locally before calling backend (fail fast with clear error)
- **Backward compatibility:** New required fields (email_subject, schema_version, etc.) are enforced ONLY when `source_type` starts with `langsmith_`. Existing `email_sync` callers continue working with the old parameter set — no breaking change for non-LangSmith flows.
- **Files:** EDIT `mcp_server.py`

**P1-T7: Golden Payload Test**
- Inject one fully-populated payload via bridge tool
- Verify all fields stored in DB, all fields rendered in UI
- **Files:** NEW evidence script

#### Gate 1

```
□ G1-01: All new DB columns exist (verified via \d zakops.quarantine_items)
□ G1-02: version column exists with DEFAULT 1
□ G1-03: Bridge tool has expanded schema (20+ params)
□ G1-04: source_message_id maps to message_id at boundary
□ G1-05: Tool rejects missing required fields with error naming them
□ G1-06: Tool rejects extra/unknown keys (strict validation)
□ G1-07: Tool rejects unknown schema_version with 400
□ G1-08: email_body_snippet always populated; "Preview not found" eliminated
□ G1-09: GOLDEN TEST: inject → DB shows all fields → list renders subject/sender/date → detail renders summary/preview/evidence
□ G1-10: 5 test items with complete data → all render correctly in UI
□ G1-11: source_type uses canonical constants only
□ G1-12: Dedup still works (existing primitive — re-verify with new schema)
```

**Evidence:** DB \d output, curl inject + response, dashboard screenshots, golden payload JSON

**Rollback:** Run 033_rollback.sql, revert main.py + mcp_server.py

---

### Phase 2: Quarantine UX — Make It Operational

**Objective:** Transform the quarantine page into a multi-operator approval workflow with locking, edits, escalation, filtering, and concurrency safety.

**Scope:** Dashboard + Backend API

**Dependencies:** Phase 1

#### Tasks

**P2-T1: Fix List View**
- Show: email_subject (not "Unknown subject"), sender_name @ sender_company (fallback to sender), classification tag (color-coded), urgency tag (HIGH=red, MEDIUM=yellow, LOW=green), confidence indicator (dot or bar), source_type badge, received_at timestamp
- **Subject display:** Use `COALESCE(email_subject, subject)` in backend query so legacy `email_sync` items (which only populate `subject`) still render correctly. Dashboard renders whichever value is returned — no client-side fallback logic needed.
- **Files:** EDIT `quarantine/page.tsx`

**P2-T2: Fix Detail View**
- Sections: Header (subject + sender), Triage Summary (from triage_summary field), Email Preview (from email_body_snippet, expand for full body from raw_content), Extracted Entities (company_name, broker_name with evidence + per-field confidence), Classification Details (classification, urgency, confidence), Attachments (names/types/sizes), Traceability (collapsible: langsmith_run_id link, schema_version, prompt_version, correlation_id)
- Replace filesystem-based preview with inline data from API response
- Stale data prevention: clear detail panel immediately on selection change, show loading state
- **Files:** EDIT `quarantine/page.tsx`, possibly EDIT API route handler

**P2-T3: Optimistic Locking**
- Backend: Add `WHERE id = $1 AND version = $2` to process endpoint UPDATE
- If 0 rows updated → return 409 Conflict with `{"error": "conflict", "message": "Item already processed"}`
- Increment version on every state change
- Frontend: handle 409 gracefully (toast + refresh)
- **Files:** EDIT `main.py` (process endpoint), EDIT `quarantine/page.tsx`

**P2-T4: Wire Escalate Action**
- Add `escalated` to status CHECK constraint (migration `034_quarantine_escalate.sql`)
- Backend: accept `action: "escalate"` in process endpoint
- Set status=escalated, optionally assign to specific operator
- Dashboard: add Escalate button (enabled when status=pending or status=escalated)
- Add "Needs Review" filter option
- **Files:** NEW migration, EDIT `main.py`, EDIT `quarantine/page.tsx`

**P2-T5: Approve with Edits**
- Dashboard: modal/inline form allowing operator to modify company_name, broker_name, classification, urgency before confirming
- Backend: accept `corrections` dict in process payload; store both original values and corrections in raw_content JSONB; corrections flow into created deal
- **Files:** EDIT `main.py`, EDIT `quarantine/page.tsx`, possibly NEW component

**P2-T6: Reject Reason Required (Policy)**
- Change UI: reject_reason from optional to required (disable Reject button when empty)
- Backend: reject process(action=reject) if notes is empty → 422
- **Files:** EDIT `quarantine/page.tsx`, EDIT `main.py`

**P2-T7: Filtering & Sorting**
- Add filter controls: classification (deal_signal/operational/newsletter), urgency (HIGH/MEDIUM/LOW), confidence threshold slider
- Add sort options: received_at (newest/oldest), urgency (highest first), confidence (lowest first)
- Backend: add query params to GET endpoint for all filters + sort
- Shadow isolation: langsmith_shadow never appears under other source filters
- **Files:** EDIT `quarantine/page.tsx`, EDIT `main.py` (GET endpoint params)

**P2-T8: Bulk Approve/Reject**
- Extend existing bulk delete to support bulk approve/reject
- Per-item validation (optimistic lock per item)
- Partial success reporting: `{approved: [...], failed: [...]}`
- **Files:** EDIT `main.py`, EDIT `quarantine/page.tsx`

#### Gate 2

```
□ G2-01: List view shows email_subject, sender_name, classification, urgency, confidence, source_type, received_at
□ G2-02: No "Unknown subject" for items with populated email_subject
□ G2-03: Detail view renders all sections with real data; no "Preview not found"
□ G2-04: Clicking item loads that item's detail (no stale data)
□ G2-05: Approve creates deal with full lifecycle artifacts (5 artifacts: deal + transitions + events + outbox + quarantine status)
□ G2-06: Approve with Edits stores corrections alongside originals
□ G2-07: Reject requires reason (policy enforced)
□ G2-08: Escalate moves item to "Needs Review" filter
□ G2-09: Optimistic locking: 2 simultaneous approve → 1 success, 1 conflict (409)
□ G2-10: Filters: source_type, classification, urgency, confidence threshold
□ G2-11: Shadow isolation: langsmith_shadow items don't leak into other filters
□ G2-12: Sorting: received_at, urgency, confidence
□ G2-13: Bulk approve/reject with per-item validation
```

**Evidence:** Dashboard screenshots, concurrent curl tests, filter/sort verification

**Rollback:** Revert dashboard + backend changes, run migration rollback

---

### Phase 3: Email Triage Agent Configuration

**Objective:** Configure LangSmith agent with proper system prompt, sub-agent pipeline, and deterministic payload assembly.

**Scope:** LangSmith Agent Builder (Zaks-owned)

**Dependencies:** Phase 1 (schema must be agreed first)

**Owner:** Zaks (LangSmith Agent Builder) — Claude provides the spec, Zaks implements in LangSmith

#### Tasks

**P3-T1: System Prompt Rewrite**
- Provide complete system prompt text for LangSmith configuration
- Covers: identity, classification rules (deal_signal/operational/newsletter/spam), output requirements (1:1 field correspondence with tool schema), boundaries (no deal creation, no email sending unless delegated)
- **Deliverable:** System prompt document for Zaks to deploy

**P3-T2: Sub-Agent Configuration Spec**
- Define responsibilities for: triage_classifier, entity_extractor, policy_guard, document_analyzer
- Specify input/output contracts per sub-agent
- **Deliverable:** Sub-agent spec document

**P3-T3: Deterministic Payload Assembly Spec**
- Define the exact JSON structure Email Triage must produce
- Map each sub-agent output to a tool parameter
- Include validation rules (required fields, types, max lengths)
- **Deliverable:** Payload assembly specification

**P3-T4: Calibration Eval Set (Collaborative)**
- Create 20+ labeled emails with known-correct classifications
- Record baseline scores: classification accuracy ≥85%, entity recall ≥75%
- **Deliverable:** Eval set + baseline scores

#### Gate 3

```
□ G3-01: System prompt deployed in LangSmith
□ G3-02: 10 test emails processed: deal signals get full extraction, newsletters minimal, spam discarded
□ G3-03: Zero required-field NULLs on injected items
□ G3-04: triage_summary present and meaningful on every item
□ G3-05: confidence scores calibrated (not all 1.0 or all 0.5)
□ G3-06: Deterministic payload: 20 injections → identical key sets
□ G3-07: Eval set exists with 20+ labeled emails and baseline scores
```

**Handoff Artifact:** At Phase 1 completion, produce `LANGSMITH_AGENT_CONFIG_SPEC.md` containing: tool schema (JSON), required/optional field table, validation rules, example golden payload, classification rules, and sub-agent responsibilities. This is the spec Zaks uses to configure the LangSmith agent.

**Parallel Execution Note:** Phase 3 runs in parallel with Phase 2. Both depend on Phase 1 completion. Phase 2 (Quarantine UX) is Claude-executed; Phase 3 (Agent Config) is Zaks-executed in LangSmith. Neither blocks the other.

**Evidence:** LangSmith traces, DB queries showing field completeness

**Rollback:** Revert to previous system prompt in LangSmith

---

### Phase 4: Quarantine → Deal Pipeline (Promotion)

**Objective:** Ensure approve produces all lifecycle artifacts, add duplicate prevention, add undo capability.

**Scope:** Backend + Dashboard

**Dependencies:** Phase 2

#### Tasks

**P4-T1: Verify Existing Promotion Logic**
- The atomic approve flow (main.py:1724-1903) already produces all 5 artifacts
- Verify: deal + deal_transitions + deal_events + outbox + quarantine status
- Verify: correlation_id propagates through all artifacts
- Verify: operator corrections (from Phase 2.5) flow into deal fields
- **Files:** Evidence scripts (query all 5 tables after approve)

**P4-T2: Duplicate Deal Prevention**
- Before creating deal, check if `source_thread_id` exists in `zakops.email_threads`
- If match: attach as timeline event on existing deal (new deal_events entry), update quarantine status to approved, set created_deal_id to existing deal, return `{"deal_created": false, "deal_id": existing_id, "message": "Thread already linked"}`
- If no match: create new deal (existing flow)
- **Files:** EDIT `main.py` (approve logic)

**P4-T3: Register Thread-Deal Mapping on Approve**
- After creating new deal, INSERT into `zakops.email_threads` with source_thread_id from quarantine item
- Only if source_thread_id is not null
- **Files:** EDIT `main.py`

**P4-T4: Undo Approval**
- New endpoint: `POST /api/quarantine/{item_id}/undo-approve`
- Requires admin role (X-API-Key + specific header or claim)
- Soft-deletes deal (sets deleted=true), removes thread mapping
- Returns quarantine item to status=pending with undo audit note in raw_content
- Logged as its own deal_events entry + outbox event
- **Files:** EDIT `main.py`, EDIT `quarantine/page.tsx` (admin UI)

**P4-T5: Deals Page Source Indicator**
- Show badge on deals created from quarantine: "From Quarantine" or "Email Triage"
- Data: check `identifiers` JSONB for `quarantine_item_id` key
- **Files:** EDIT `deals/page.tsx`, possibly `deals/[id]/page.tsx`

#### Gate 4

```
□ G4-01: Approve produces ALL 5 artifacts (verified by querying each table)
□ G4-02: Operator corrections flow into created deal
□ G4-03: Duplicate prevention: same thread_id → attaches to existing deal
□ G4-04: Transaction rollback: partial failure → no orphaned state
□ G4-05: Deal timeline shows creation event with quarantine context + correlation_id
□ G4-06: source_thread_id registered in email_threads on approve
□ G4-07: Undo approval: admin reverts → deal archived, quarantine returns to pending
□ G4-08: Deals view shows source indicator for quarantine-promoted deals
□ G4-09: 5 quarantine items approved → correct artifacts produced
```

**Evidence:** Multi-table queries, undo test, deals page screenshot

**Rollback:** Revert main.py + dashboard changes

---

### Phase 5: Auto-Routing

**Objective:** Future emails for approved deals skip quarantine. Controlled by `auto_route` flag.

**Scope:** Backend + Bridge + Dashboard

**Dependencies:** Phase 4

#### Tasks

**P5-T1: Pre-Injection Routing Check**
- In quarantine POST endpoint, after kill switch check, before insert:
  1. Check `auto_route` flag (OFF → quarantine as normal)
  2. Look up `source_thread_id` in `email_threads`
  3. Single match → create deal_events entry on matched deal, return `{routed_to: "deal", deal_id: ...}`
  4. Multiple matches → quarantine with `routing_conflict=true` in raw_content
  5. No match → quarantine as normal
- Always return `routing_reason` in response
- **Files:** EDIT `main.py`

**P5-T2: Conflict Resolution UI**
- Items with `routing_conflict=true` show the conflicting deal IDs
- Operator can choose which deal to attach to, or create new deal
- **Files:** EDIT `quarantine/page.tsx`

**P5-T3: Operator Thread Re-Linking**
- Dashboard: deal detail shows linked threads
- Operator can add/remove/move thread mappings
- Backend: `POST /api/deals/{deal_id}/threads` + `DELETE`
- **Files:** EDIT `deals/[id]/page.tsx`, EDIT backend router

**P5-T4: Update Bridge Tool Response**
- Tool response always includes `routing_reason`
- Email Triage logs but does not change behavior based on routing
- **Files:** EDIT `mcp_server.py`

#### Gate 5

```
□ G5-01: auto_route OFF → all emails → quarantine
□ G5-02: auto_route ON + single thread match → deal timeline
□ G5-03: auto_route ON + multiple matches → quarantine with conflict reason
□ G5-04: auto_route ON + no match → quarantine
□ G5-05: routing_reason in every tool response
□ G5-06: Conflict resolution UI shows conflicting deals
□ G5-07: Operator can re-link thread (add/remove/move)
□ G5-08: End-to-end: approve deal → follow-up email → appears in deal timeline
```

**Evidence:** API responses with routing_reason, deal timeline entries, UI screenshots

**Rollback:** Set auto_route=false (flag-gated — no code revert needed for deactivation)

---

### Phase 6: Collaboration Contract

**Objective:** Structured async delegation between ZakOps and Email Triage.

**Scope:** Backend + Bridge + Dashboard

**Dependencies:** Phase 4

#### Tasks

**P6-T1: Delegated Tasks Table**
- Migration `035_delegated_tasks.sql` with state machine: pending → queued → executing → completed | failed → queued (retry) | dead_letter
- Fields: id, deal_id, task_type (enum), payload (JSONB), requested_by, status, attempts, max_attempts (default 3), result (JSONB), error, correlation_id, timestamps
- **Files:** NEW migration

**P6-T2: Delegation API**
- `POST /api/deals/{deal_id}/delegate` — create delegated task
- `GET /api/deals/{deal_id}/tasks` — list tasks for deal
- `PUT /api/tasks/{task_id}/result` — Email Triage reports result
- Gated by `delegate_actions` feature flag
- **Files:** EDIT backend routers

**P6-T3: Email Sending Permission Model**
- Flow: ZakOps drafts → operator confirms → task created → Email Triage executes
- `send_email_enabled` flag must be ON (separate from delegate_actions as safety backstop)
- **Files:** EDIT backend + bridge

**P6-T4: New MCP Tools**
- `zakops_get_deal_status` — read deal state
- `zakops_list_recent_events` — read recent deal timeline
- `zakops_report_task_result` — report delegation result
- **Files:** EDIT `mcp_server.py`

**P6-T5: Dashboard Task Management**
- Deal detail: show delegated tasks tab
- Task list with status, retry count, result
- Dead-lettered tasks surface as alert
- **Files:** EDIT `deals/[id]/page.tsx`

#### Gate 6

```
□ G6-01: delegated_tasks table with state machine
□ G6-02: Retry: failed → re-queued up to max_attempts → dead_letter
□ G6-03: delegate_actions flag controls availability
□ G6-04: send_email_enabled flag blocks outbound email separately
□ G6-05: Email sending requires operator confirmation
□ G6-06: Structured feedback for every task
□ G6-07: Task results on deal timeline
□ G6-08: Dead-lettered tasks surface to operator
□ G6-09: zakops_get_deal_status + zakops_list_recent_events tools work
```

**Evidence:** Task lifecycle traces, flag toggle tests, delegation flow

**Rollback:** Set delegate_actions=false, send_email_enabled=false (flag-gated)

---

### Phase 7: Security & Hardening

**Objective:** Layered security, key management, data retention, PII rules, resilience.

**Scope:** Infrastructure + Backend + Bridge

**Dependencies:** Phase 5+

#### Tasks

**P7-T1: Cloudflare Access Service Token (Layer 1 — Infrastructure Hardening)**
- Configure CF Access application for zakops-bridge.zaksops.com
- Create service token, configure LangSmith to send CF-Access-Client-Id + CF-Access-Client-Secret headers
- This adds edge-level protection independent of application auth (Layer 2 was restored in P0-T6)
- Verify: request without CF headers → 403 at edge (never reaches bridge)
- **Deliverable:** CF config + LangSmith config update

**P7-T2: Verify Both Auth Layers Active**
- Confirm Layer 1 (CF Access) + Layer 2 (Bearer auth, restored in P0-T6) are both enforced
- Test: no CF headers → 403; valid CF headers + no Bearer → 401; valid CF + valid Bearer → 200
- **This is a verification task, not a code change** — Bearer auth was already restored in Phase 0
- **Files:** Evidence scripts only

**P7-T3: Key Rotation — Dual-Token Window**
- Bridge accepts both old and new tokens during rotation (configurable via comma-separated env var)
- Token rotation procedure tested end-to-end
- **Files:** EDIT `mcp_server.py`

**P7-T4: Log Redaction Audit**
- Verify no secrets in logs (bridge, backend, access logs)
- Auth tokens shown as first 8 chars only (already done in bridge)
- **Files:** Audit existing logs

**P7-T5: Data Retention & PII**
- Document retention periods per data type
- Add `DELETE /api/quarantine/{item_id}/purge` for hard delete (admin only)
- PII access logged
- **Files:** EDIT backend, NEW docs

**P7-T6: Error Handling Audit**
- Test: backend unreachable → bridge returns error (not hang)
- Test: partial transaction failure → full rollback
- Test: bridge restart → LangSmith reconnects
- **Files:** Evidence scripts

#### Gate 7

```
□ G7-01: MCP bridge protected by CF Access (Layer 1) + Bearer auth (Layer 2)
□ G7-02: Security NOT dependent on LangSmith secret interpolation
□ G7-03: Key rotation tested end-to-end
□ G7-04: No secrets in logs
□ G7-05: Data retention policy documented
□ G7-06: Error handling for all failure modes tested
□ G7-07: Full audit trail with correlation_id end-to-end
```

**Evidence:** CF Access config, curl tests, log audit, error scenario tests

**Rollback:** Revert bridge changes, CF Access can be disabled independently

---

### Phase 8: Operational Excellence Gate

**Objective:** SLOs, monitoring, load test, DR, shadow measurement readiness.

**Scope:** All services

**Dependencies:** All prior phases

#### Tasks

**P8-T1: Define SLOs** — injection <30s p95, UI load <2s p95, approve→deal <3s p95, 99.5% uptime
**P8-T2: Monitoring & Alerting** — health checks every 60s, queue depth alerts, kill switch activation alert
**P8-T3: Load Test** — 100→500 emails/day simulated, 3-5 concurrent operators, 50-email burst
**P8-T4: Backup & Restore Test** — all 3 databases backed up, restore to staging verified
**P8-T5: Shadow Measurement Readiness** — filterable dataset, accuracy measurement script
**P8-T6: 7-Day Shadow Burn-In** — run Email Triage for 1 week, measure precision/recall

#### Gate 8

```
□ G8-01: SLOs defined and documented
□ G8-02: Monitoring and alerts configured
□ G8-03: Load test completed — SLOs met under load
□ G8-04: Backup + restore test completed
□ G8-05: 7-day shadow burn-in with clean dataset
□ G8-06: Feature flags set for production: shadow_mode=ON, auto_route=OFF, delegate_actions=OFF, send_email_enabled=OFF
□ G8-07: System declared production-ready
```

---

## 4. No-Drop Coverage Matrix

| Roadmap Req | Phase | Tasks | Gate | Definition of Done |
|-------------|-------|-------|------|--------------------|
| Feature flags (4) + runtime toggle | P0 | P0-T1 | G0-01 | Table exists, API works, flags toggleable |
| Kill switch | P0 | P0-T2 | G0-04,G0-05 | 503 on write, reads unaffected, toggle < 1s |
| Shadow mode wiring | P0 | P0-T3 | G0-02 | Flag controls source_type assignment |
| Idempotency verification | P0 | P0-T4 | G0-06 | 5 concurrent → 1 record |
| Correlation ID verification | P0 | P0-T5 | G0-07,G0-08 | End-to-end trace proven |
| Security perimeter | P0 | P0-T6 | G0-09,G0-11 | Auth enforced, bypass removed |
| Key rotation procedure | P0 | P0-T7 | G0-10 | Runbook with explicit steps |
| Canonical schema | P1 | P1-T1 thru P1-T4 | G1-01 thru G1-08 | All fields in DB + API |
| Bridge tool contract | P1 | P1-T6 | G1-03 thru G1-07 | Strict validation, expanded params |
| "Preview not found" fix | P1 | P1-T5 | G1-08 | email_body_snippet always rendered |
| Golden payload test | P1 | P1-T7 | G1-09 | Full inject → DB → UI verified |
| List view fix | P2 | P2-T1 | G2-01,G2-02 | All fields rendered correctly |
| Detail view fix | P2 | P2-T2 | G2-03,G2-04 | All sections with real data |
| Optimistic locking | P2 | P2-T3 | G2-09 | Concurrent approve → 1 success, 1 conflict |
| Escalate action | P2 | P2-T4 | G2-08 | Status + UI + filter |
| Approve with Edits | P2 | P2-T5 | G2-06 | Corrections stored + flow to deal |
| Reject reason required | P2 | P2-T6 | G2-07 | UI + backend enforce |
| Filtering & sorting | P2 | P2-T7 | G2-10 thru G2-12 | All filters + sorts work |
| Bulk actions | P2 | P2-T8 | G2-13 | Per-item validation + partial success |
| System prompt | P3 | P3-T1 | G3-01 | Deployed in LangSmith |
| Deterministic payloads | P3 | P3-T3 | G3-06 | 20 identical key sets |
| Calibration eval set | P3 | P3-T4 | G3-07 | 20+ labeled, baseline recorded |
| Quarantine→deal mapping | P4 | P4-T1 | G4-01 | All 5 artifacts verified |
| Duplicate deal prevention | P4 | P4-T2 | G4-03 | Thread match → attach, no duplicate |
| Thread-deal registration | P4 | P4-T3 | G4-06 | email_threads row created on approve |
| Undo approval | P4 | P4-T4 | G4-07 | Admin reverts → deal archived, item restored |
| Deals source indicator | P4 | P4-T5 | G4-08 | Badge on quarantine-promoted deals |
| Auto-routing | P5 | P5-T1 thru P5-T4 | G5-01 thru G5-08 | Flag-gated routing with conflict handling |
| Delegated tasks | P6 | P6-T1 thru P6-T5 | G6-01 thru G6-09 | State machine + retry + dead-letter |
| Cloudflare Access | P7 | P7-T1 | G7-01 | Layer 1 edge protection |
| Key rotation | P7 | P7-T3 | G7-03 | Dual-token window tested |
| Data retention | P7 | P7-T5 | G7-05 | Policy documented |
| SLOs + monitoring | P8 | P8-T1,P8-T2 | G8-01,G8-02 | Defined + alerting active |
| Load test | P8 | P8-T3 | G8-03 | SLOs met under load |
| Shadow burn-in | P8 | P8-T6 | G8-05 | 7-day dataset, accuracy measurable |

---

## 5. Resolved Decisions

All 7 decisions have been resolved by the orchestrator. These are final — no further deliberation needed.

| # | Decision | Resolution | Rationale |
|---|----------|-----------|-----------|
| D1 | **Security perimeter approach** | **C) Both layers** — Bearer auth restored in P0-T6 (code, immediate), CF Access added in P7-T1 (infra, later) | Defense in depth. Layer 2 (Bearer) is zero-cost to restore now. Layer 1 (CF Access) adds edge protection but is infra work — deferred to Phase 7. |
| D2 | **Preview storage** | **A) Inline** — `email_body_snippet` stored as required column, always populated | No runtime dependency on Gmail API or filesystem. Works for all source types. |
| D3 | **Quarantine schema migration** | **A) Add columns** to existing `quarantine_items` table | Simpler, fewer JOINs, all data in one query. Extension table adds complexity with no benefit at this scale. |
| D4 | **Phase 3 execution** | **Zaks implements** in LangSmith Agent Builder; Claude produces `LANGSMITH_AGENT_CONFIG_SPEC.md` as handoff artifact at Phase 1 completion | Phase 3 runs in parallel with Phase 2. Handoff artifact ensures Zaks has everything needed. |
| D5 | **Escalate semantics** | **A) Needs senior review** — no operator assignment, just a status flag | Simpler. No user management table needed. "Needs Review" filter surfaces escalated items. |
| D6 | **Schema version enforcement** | **A) Reject unknown versions** — `schema_version` must be in allowed set (initially `["1.0.0"]`) | Prevents silent drift. New versions added explicitly as the schema evolves. |
| D7 | **langsmith_live gate** | **Feature flag toggle** — `shadow_mode=false` after Phase 8 gates pass | Graduation is a flag flip, not a code deploy. Phase 8 burn-in must pass first. |

---

## 6. Consultant Notes (Risks / Tightening Recommendations)

### Security: Auth Bypass Must Be Removed Before Broader Pilot

**Current state:** All MCP paths (`/mcp`, `/sse`, `/messages/`) bypass authentication entirely (`mcp_server.py:157-170`). Any client that can reach `zakops-bridge.zaksops.com` can call any tool, including `zakops_inject_quarantine`.

**Risk:** HIGH — anyone who discovers the tunnel URL can inject data into the quarantine pipeline.

**Recommendation:** Phase 0 Task 6 is the HIGHEST PRIORITY task in the entire roadmap. Before any additional data flows through the system:
1. Implement Cloudflare Access service token (5 minutes to configure, infrastructure-level)
2. Then remove the auth bypass from the bridge code
3. Verify: unauthenticated curl → 403 (CF Access) or 401 (bridge)

### Preview Reliability: Choose Inline Storage

**Current state:** LangSmith-injected items show "Preview not found" because the preview depends on a `quarantine_dir` filesystem path that only exists for email_sync items.

**Recommendation:** Option A (inline storage) is strictly superior for this use case:
- No runtime dependency on Gmail API or filesystem
- Works for all source types (email_sync, langsmith_shadow, langsmith_live, manual)
- 500-char snippet covers 95% of operator decision needs
- Full body stored in `raw_content` JSONB for "Expand" button
- This is a one-line change in the backend + bridge tool expansion

### Contract Testing: Golden Payload Fixture

**Recommendation:** Create a committed fixture file `tests/fixtures/golden_quarantine_payload.json` containing a fully-populated quarantine injection payload. Use it for:
1. Unit test: deserialize → model validates
2. Integration test: POST to endpoint → 201, verify all fields stored
3. UI test: rendered list item + detail panel match expected values
4. Regression gate: run before every deploy

This prevents the "it worked once but broke silently" failure mode.

### Feature Flags: Single Source of Truth

**Risk:** If flags are stored in DB but bridge caches them, drift is possible (bridge sees stale value).

**Recommendation:**
- DB is authoritative, bridge caches with 60s TTL
- Admin API returns `updated_at` timestamp; bridge logs stale-cache warnings
- Dashboard settings page shows current flag values (read from API, not hardcoded)
- Flag changes logged in `deal_events` (event_type='flag_changed') for audit trail
- No feature flag env vars — DB table is the only source

### Quarantine Schema: raw_content JSONB vs Dedicated Columns

**Risk:** Putting new fields in `raw_content` JSONB makes them unsearchable/unfilterable by standard SQL.

**Recommendation:** All fields that need to be filtered, sorted, or displayed in list view MUST be dedicated columns. `raw_content` is for:
- Full email body (too large for column)
- Processing metadata (hidden_at, hidden_by, corrections)
- LangSmith-specific metadata that may change structure
- Anything not in the canonical schema

### Concurrent Rate: In-Memory Rate Limiter

**Risk:** Single-instance rate limiter doesn't survive restart and can't coordinate across multiple instances.

**Recommendation:** Acceptable for current single-instance deployment. When scaling to multiple instances, migrate to Redis-based rate limiting or database-backed sliding window. Log a TODO for this.

### Bridge Tool: Backward Compatibility During Schema Transition

**Risk:** If bridge tool schema changes (new required fields) and LangSmith agent hasn't been updated, all injections will fail.

**Recommendation:**
- Phase 1 (bridge tool expansion) and Phase 3 (LangSmith agent config) must be coordinated
- During transition: make new fields conditionally required based on source_type
  - `langsmith_shadow` items: strict validation (all required fields)
  - `email_sync` items: existing validation (backward compatible)
- This prevents breaking existing email_sync flow while tightening LangSmith contract

---

*End of Execution Plan — VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec*
