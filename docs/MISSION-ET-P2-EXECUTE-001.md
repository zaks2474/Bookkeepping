# MISSION: ET-P2-EXECUTE-001
## Email Triage Phase 1 & 2 Execution (Schema + UX)
## Date: 2026-02-15
## Classification: Dashboard + Backend execution
## Prerequisite: P0 Safety & Perimeter (COMPLETE)
## Successor: QA-ET-P2-VERIFY-001

## Mission Objective
Execute **Phase 1 (Canonical Schema)** and **Phase 2 (Quarantine UX)** of the Email Triage Validation Roadmap. This mission expands the quarantine database schema to support operational fields, updates the bridge tool contract, and overhauls the dashboard UX to match the "Industrial Utilitarian" design spec. It also re-verifies Phase 3 artifacts.

**Scope:**
- **Phase 1:** Backend schema expansion (Migration 033), API model updates, Bridge tool contract expansion.
- **Phase 2:** Dashboard UX overhaul (List/Detail, Filters, Bulk Actions), Backend operational logic (Optimistic Locking, Escalation, Kill-switch fix).
- **Phase 3:** Re-verification of existing agent config specs (no new work).

**NOT in Scope:**
- Phase 4 (Deal Promotion) and beyond.
- Creating the Phase 3 specs (already exist).

**Source Material:**
- Exec Plan: `/home/zaks/bookkeeping/docs/VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md`
- Design Spec: `/home/zaks/bookkeeping/docs/PHASE2-QUARANTINE-UX-DESIGN-SPEC.md`
- QA Report (Failures to fix): `/home/zaks/bookkeeping/docs/QA-ET-VALIDATION-VERIFY-001-COMPLETION.md`

---

## Context
Phase 0 (Safety) is complete. The system is safe but functionally limited. The current Quarantine UX is a placeholder that lacks critical fields (`confidence`, `sender_name`) and operational controls (locking, escalation). The database schema needs expansion to support the incoming data from the LangSmith agent.

**Critical Fixes Required (from QA-ET-VALIDATION-VERIFY-001):**
1.  **Missing Fields:** UI must render `sender_name`, `confidence`, `triage_summary`.
2.  **Optimistic Locking:** Implement version-based concurrency control (ST-2 failure).
3.  **Missing Migrations:** Create `034_quarantine_escalate.sql` (VF-03.3 failure).
4.  **Kill-Switch TTL:** Reduce backend flag cache from 5s to 1s or add bypass (VF-01.2 failure).
5.  **Surface 9 Logging:** Ensure UX uses `console.warn` for degradations (VF-03.4 failure).

---

## Architectural Constraints
- **Canonical Bridge Path:** All bridge edits must occur in `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/`. Legacy paths are forbidden.
- **Sync Chain:** After ANY backend API change (P1, P2), you MUST run: `make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`.
- **Surface 9 Compliance:** Dashboard components must adhere to the design system (utilitarian aesthetic, server-side counts, `Promise.allSettled`).
- **Contract Surfaces:** This mission modifies S1, S2, S6, S8, S9, S12, S13, S15, S16.
- **Optimistic Locking:** Use `ETag` or `version` column for all write operations on quarantine items.

## Anti-Pattern Examples

### WRONG: Client-side filtering
```typescript
// Don't fetch all and filter in JS
const allItems = await getQuarantineItems();
const filtered = allItems.filter(i => i.confidence > 0.8);
```

### RIGHT: Server-side filtering
```typescript
// Pass filters to API
const items = await getQuarantineQueue({ min_confidence: 0.8 });
```

### WRONG: Skipping Sync
Changing `main.py` models and immediately editing `page.tsx` without running `make sync-types`.

### RIGHT: Mandatory Sync
Change `main.py` -> `make update-spec` -> `make sync-types` -> Update `page.tsx`.

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Dashboard build fails due to type mismatch | HIGH | Blocker | Run sync chain immediately after backend changes. |
| 2 | Migration 033 conflicts with existing state | MEDIUM | Data Loss | Verify migration safety preflight in Phase 1. |
| 3 | Optimistic locking breaks valid operator actions | MEDIUM | UX Friction | Ensure UI handles 409 Conflict gracefully with refresh prompt. |
| 4 | Kill-switch fix causes perf regression | LOW | Latency | Use aggressive caching for reads, bypass only for writes. |

---

## Phase 1 — Canonical Schema & Contract
**Complexity:** XL
**Estimated touch points:** 10 files (Backend Models, DB Migrations, Bridge Server)

**Purpose:** Expand the data model to support high-fidelity triage (confidence, summaries, snippets) and enforce the contract at the bridge level.

### Blast Radius
- **Services:** Backend API, MCP Bridge
- **Data:** `zakops.quarantine_items` table

### Tasks
- P1-01: Create Migration 033 (`033_quarantine_schema_v2.sql`) adding `email_body_snippet`, `triage_summary`, `source_thread_id`, `schema_version`, `confidence`, `received_at`, `sender_name`, `sender_domain`.
- P1-02: Update Backend Pydantic models (`QuarantineCreate`, `QuarantineResponse`) to match new schema.
- P1-03: Implement `COALESCE(email_subject, subject)` in list queries for backward compatibility.
- P1-04: Update ingestion logic to map `source_message_id` -> `message_id` and validate `source_type`.
- P1-05: Update Bridge Tool (`server.py`) to expose full 20+ parameter schema and perform local fail-fast validation.
- P1-06: Create Golden Payload test script to verify end-to-end injection.
- P1-07: Execute Sync Chain (`make update-spec && ...`).

### Rollback Plan
1. Run `033_quarantine_schema_v2_rollback.sql`.
2. Revert `main.py` and `server.py` changes.
3. Run sync chain to restore types.

### Gate P1
- G1-01: `\d zakops.quarantine_items` shows all new columns.
- G1-02: `version` column exists (default 1).
- G1-03: Bridge tool definition in `server.py` matches `LANGSMITH_AGENT_CONFIG_SPEC.md`.
- G1-04: Ingestion endpoint maps `source_message_id` correctly.
- G1-05: Bridge rejects payloads missing required fields (e.g. `email_body_snippet`).
- G1-06: Bridge rejects unknown keys (`extra='forbid'` behavior).
- G1-07: Bridge rejects invalid `schema_version`.
- G1-08: `email_body_snippet` is populated in DB.
- G1-09: Golden payload test passes (Inject -> DB -> Read).
- G1-10: Test UI rendering with 5 mock items (API level check).
- G1-11: `source_type` validation enforces canonical constants.
- G1-12: `make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit` PASSES.

---

## Phase 2 — Quarantine UX Operationalization
**Complexity:** XL
**Estimated touch points:** 12 files (Dashboard Components, API Client, Backend Logic)

**Purpose:** Transform the placeholder UI into a functional workspace with filtering, locking, and proper data display.

### Blast Radius
- **Services:** Dashboard, Backend API
- **Data:** `zakops.quarantine_items` status

### Tasks
- P2-01: Create Migration 034 (`034_quarantine_escalate.sql`) adding 'escalated' status support (if enum constraint exists) or verifying text field support.
- P2-02: Implement Backend "Kill Switch" TTL Fix: Set flag cache to 1s or add bypass for writes (remediates VF-01.2).
- P2-03: Update Dashboard `api.ts` to support new fields and filters.
- P2-04: Implement `ListDetailLayout` and updated `QuarantinePage` matching Design Spec (utilitarian, dense).
- P2-05: Implement `FilterDropdown` and server-side filtering (Source, Status, Date, Confidence).
- P2-06: Implement `BulkSelectionBar` for batch operations.
- P2-07: Implement Optimistic Locking: Backend check `version` on write; UI handles 409.
- P2-08: Implement "Escalate" action and dialog.
- P2-09: Surface 9 Compliance: Ensure `console.warn` on API degradation, `console.error` on crashes.

### Rollback Plan
1. Revert Dashboard changes to previous commit.
2. Revert Backend locking logic.
3. Run sync chain.

### Gate P2
- G2-01: List view renders `sender_name`, `confidence` (color-coded), `source_type`.
- G2-02: Detail view shows `triage_summary` and `email_body_snippet`.
- G2-03: Selecting item loads detail without stale data flash.
- G2-04: Approve action sends `version`; Backend rejects if stale (409).
- G2-05: Escalate action updates status to 'escalated'.
- G2-06: Reject requires reason (UI validation).
- G2-07: Filters (Source, Status, Confidence) update URL params and list.
- G2-08: Shadow mode items do not leak into default view (unless filtered).
- G2-09: Sorting works by `received_at`, `urgency`, `confidence`.
- G2-10: Bulk actions work for multiple items.
- G2-11: Kill switch activates within 1s (proven by test script).
- G2-12: Surface 9: Network disconnect logs `console.warn`.
- G2-13: `make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit` PASSES.

---

## Phase 3 — Agent Config Re-Verification
**Complexity:** S
**Estimated touch points:** 0 (Verification only)

**Purpose:** Confirm that the previously created Agent Config specs are still valid against the new P1 schema.

### Tasks
- P3-01: Verify `LANGSMITH_AGENT_CONFIG_SPEC.md` exists and matches P1 schema.
- P3-02: Verify Eval set exists.

### Gate P3
- G3-01: `LANGSMITH_AGENT_CONFIG_SPEC.md` aligns with deployed Bridge tool.
- G3-02: Eval dataset present.
- G3-03: (Re-verify) Zero required-field NULLs in golden test.
- G3-04: (Re-verify) Triage summary populated.
- G3-05: (Re-verify) Confidence scoring calibrated in golden test.
- G3-06: (Re-verify) Deterministic payload structure.
- G3-07: `make validate-agent-config` PASSES.

---

## Acceptance Criteria

### AC-1: Schema Completeness
All new columns (`email_body_snippet`, `confidence`, etc.) are present in the DB and populated by the bridge.

### AC-2: Bridge Contract
Bridge tool enforces schema validation and returns 400 for invalid payloads (e.g. missing `email_body_snippet`).

### AC-3: UI Operationality
Quarantine Dashboard allows filtering, sorting, escalation, and approval with optimistic locking.

### AC-4: Kill Switch Latency
Kill switch activation stops writes within 1 second.

### AC-5: No Regressions
`make validate-local` passes and all sync commands succeed.

### AC-6: Bookkeeping
`CHANGES.md` updated with Migration 033, 034 and all component changes.

---

## Guardrails
1. **Bridge Path Authority:** Edits only in `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/`.
2. **Schema Safety:** Do not alter existing columns; only add new nullable columns (or columns with defaults).
3. **Validation Discipline:** Run the full sync chain (`make update-spec` ...) after backend edits.
4. **Surface 9:** Adhere to "Industrial Utilitarian" design; no rounded-corner cards or gradients.
5. **Secrets:** Do not log PII or secrets; use `_redact` helper if logging payloads.
6. **WSL Safety:** Strip CRLF from new SQL/shell files.

---

## Executor Self-Check Prompts

### After Phase 1
- [ ] "Did I run the sync chain (`make sync-types`...)?"
- [ ] "Did I verify the bridge tool using the canonical path?"
- [ ] "Does the DB schema match the Design Spec exactly?"

### After Phase 2
- [ ] "Did I implement the Kill Switch TTL fix?"
- [ ] "Is Optimistic Locking working (tested with curl/script)?"
- [ ] "Does the UI handle 409 Conflict errors?"
- [ ] "Did I use `console.warn` for degradations per Surface 9?"

---

## Files Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | P1, P2 | Schema updates, filters, locking, kill-switch fix |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` | P1 | Tool contract expansion |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | P2 | New types/endpoints |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | P2 | Full UX overhaul |
| `/home/zaks/zakops-backend/src/core/feature_flags.py` | P2 | Cache TTL adjustment |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `.../migrations/033_quarantine_schema_v2.sql` | P1 | Schema expansion |
| `.../migrations/034_quarantine_escalate.sql` | P2 | Status enum update |
| `.../components/shared/FilterDropdown.tsx` | P2 | Shared UI |
| `.../components/shared/BulkSelectionBar.tsx` | P2 | Shared UI |
| `.../components/quarantine/ConfidenceIndicator.tsx`| P2 | Quarantine UI |

---

## Stop Condition

Mission is DONE when:
1.  All P1, P2, and P3 gates pass.
2.  `make validate-local` passes in `zakops-agent-api`.
3.  Changes are committed and `CHANGES.md` updated.
4.  Do NOT proceed to Phase 4.

---
*End of Mission Prompt — ET-P2-EXECUTE-001*
