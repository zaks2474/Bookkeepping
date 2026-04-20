# MISSION: DEAL-DATA-ARCHITECTURE-001
## Systemic Fix for Quarantine-to-Deal Data Flow — Eliminate Incremental Patching
## Date: 2026-02-18
## Classification: Architecture Remediation (Full-Stack Data Pipeline)
## Prerequisite: DEAL-EVIDENCE-PIPELINE-001 (Complete — shared enrichment helper exists)
## Successor: None (self-contained)

---

## Mission Objective

**What:** Fix the systemic architectural deficiency that causes data fragmentation at state boundaries in the quarantine→deal pipeline. This mission replaces the procedural band-aid approach (fixing individual endpoints one by one) with a structural guarantee that data flows cleanly from injection to deal lifecycle to dashboard display.

**What this is NOT:** This is not a UI redesign, not an agent pipeline change, not a database migration. The deals table's JSONB columns already support arbitrary keys. This mission restructures HOW data moves between existing structures.

**Source material:**
- Three-pass architectural review: `/home/zaks/bookkeeping/docs/DATA-FLOW-ARCH-REVIEW-MASTER.md`
- Prior fix (band-aid): DEAL-EVIDENCE-PIPELINE-001 (added shared enrichment helper)
- Database schema: `/home/zaks/zakops-agent-api/apps/backend/db/init/001_base_tables.sql`
- Current enrichment code: `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` (lines 2758-2903)

**Core problem:** Data lives in two tables (quarantine_items and deals) with a one-time, lossy copy at approval time. Any field missed by the copy function is silently lost. There is no schema contract governing what transfers, no validation that the transfer was complete, and no runtime fallback to the source.

**This mission addresses 9 findings (F-01 through F-09) from the architecture review:**
- F-01: PATCH endpoint overwrites JSONB (HIGH)
- F-02: No formal deal data contract (HIGH)
- F-03: field_confidences dropped at approval (MEDIUM)
- F-04: attachments dropped at approval (MEDIUM)
- F-05: Traceability metadata lost at approval (MEDIUM)
- F-06: entities.people[] dropped at approval (LOW)
- F-07: extraction_evidence has no format validation (MEDIUM)
- F-08: Manual deal creation bypasses enrichment (LOW — by design, documented)
- F-09: Quarantine source not joinable in dashboard (LOW)

**Out of scope:** F-10 (retention cleanup FSM bypass) and F-11 (undo-approve workflow bypass) — these are separate infrastructure concerns.

---

## Context

DEAL-EVIDENCE-PIPELINE-001 added a shared `_build_deal_enrichment()` helper and wired it to all 4 approve paths. This fixed the immediate symptom (deals showing "TBD" after approval). But the architectural review revealed that the fix is procedural, not structural:

1. The helper is a private function in a 3000-line file — easy to bypass in new code
2. The PATCH endpoint still overwrites JSONB — any edit destroys enriched data
3. No schema validates what "complete deal data" means
4. field_confidences, attachments, traceability metadata, and people data are still dropped
5. extraction_evidence format is unvalidated — agent format changes are silent

The user's directive: "Design a permanent architectural solution. Ensure the fix is systemic — not procedural. I do not want to revisit this issue again."

---

## Glossary

| Term | Definition |
|------|-----------|
| extraction_evidence | JSONB column on quarantine_items containing structured data the agent extracted (financials, broker, entities, typed_links) |
| field_confidences | JSONB dict mapping field names to float confidence scores (0.0-1.0) from the agent |
| Non-destructive merge | JSONB update pattern that only fills NULL/missing keys, never overwrites existing values |
| JSONB overwrite | SQL pattern `SET col = $1::jsonb` that replaces the entire column value |
| JSONB merge | SQL pattern `SET col = COALESCE(col, '{}'::jsonb) || $1::jsonb` that adds/updates keys |
| Deal data contract | Formal typed schema defining what fields a deal's JSONB columns should contain |

---

## Architectural Constraints

- **`transition_deal_state()` choke point** — all deal stage changes go through the workflow engine. This mission does NOT modify stage transitions.
- **`Promise.allSettled` mandatory** — any new dashboard data fetching uses allSettled with typed fallbacks.
- **Generated files never edited** — `*.generated.ts` and `*_models.py` are protected by hooks.
- **Contract surface discipline** — if API response shape changes, run `make update-spec && make sync-types && npx tsc --noEmit`.
- **Surface 9 compliance** — new dashboard components follow design system rules.
- **Port 8090 FORBIDDEN** — never use or reference.
- **Operator corrections always win** — enrichment priority hierarchy: corrections > flat item > flat ev > nested ev > default.
- **Non-destructive merge for existing deals** — when enriching a deal that already has data, only fill NULL/missing keys.

---

## Anti-Pattern Examples

### WRONG: JSONB full overwrite on PATCH
```python
# Destroys enriched company, phone, email when only name is updated
await conn.execute(
    "UPDATE zakops.deals SET broker = $2::jsonb WHERE deal_id = $1",
    deal_id, json.dumps({"name": "Updated Name"})
)
```

### RIGHT: JSONB per-key merge on PATCH
```python
# Preserves existing keys, only updates submitted keys
await conn.execute(
    "UPDATE zakops.deals SET broker = COALESCE(broker, '{}'::jsonb) || $2::jsonb WHERE deal_id = $1",
    deal_id, json.dumps({"name": "Updated Name"})
)
```

### WRONG: Inline enrichment in each endpoint
```python
# Every new endpoint must remember to call this — procedural, fragile
broker_info = {}
broker_name = corrections.get('broker_name') or item.get('broker_name')
if broker_name: broker_info['name'] = broker_name
```

### RIGHT: Service class that encapsulates all mapping logic
```python
# Single import, single call — structural, impossible to forget
from src.core.deals.enrichment import DealEnrichmentService
enrichment = DealEnrichmentService().enrich_from_quarantine(item, corrections)
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Enrichment service refactor breaks existing 4 approve paths | HIGH | All quarantine approvals fail | Gate P2 requires approve+verify round-trip test |
| 2 | JSONB merge operator (||) overwrites nested keys unexpectedly | MEDIUM | Subtle data corruption on merge | Use per-key Python merge, not SQL || operator |
| 3 | New Pydantic models break API response serialization | MEDIUM | 500 errors on deal fetch | Gate P1 requires `bash scripts/test.sh` pass |
| 4 | Dashboard source link card fetches quarantine data that no longer exists (deleted/purged) | LOW | UI error on old deals | Graceful null handling with empty state |
| 5 | CRLF not stripped from new .py files or ownership not fixed | MEDIUM | Runtime import errors | WSL safety checklist in every phase gate |

---

<!-- Adopted from Improvement Area IA-2 -->
## Crash Recovery Protocol

If resuming after a crash, run these commands to determine current state:
1. `git log --oneline -5` — check which phases were committed
2. `make validate-local` — check codebase health
3. `ls -la /home/zaks/zakops-agent-api/apps/backend/src/core/deals/` — check if enrichment.py and deal_contract.py exist

---

## Phase 0 — Discovery & Baseline
**Complexity:** S | **Estimated touch points:** 0 (read-only)

**Purpose:** Verify current state matches the architecture review findings.

**Blast Radius:**
- Services affected: None
- Pages affected: None
- Downstream consumers: None

### Tasks
- P0-01: **Verify** the current `_build_deal_enrichment()` helper exists and all 4 approve paths use it
  - Evidence: `grep -n "_build_deal_enrichment" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
  - **Checkpoint:** Must find 5+ references (1 definition + 4 call sites)
- P0-02: **Verify** PATCH endpoint uses JSONB overwrite (F-01 still present)
  - Evidence: Read `update_deal()` function (line ~850-910)
- P0-03: **Verify** baseline validation passes
  - Evidence: `make validate-local`
- P0-04: **Identify contract surfaces affected** by this mission
  - Surface 1 (Backend → Dashboard types) — if API response shape changes
  - Surface 16 (Email Triage Injection) — enrichment logic changes

### Gate P0
- `_build_deal_enrichment` found in 5+ locations
- PATCH overwrite pattern confirmed
- `make validate-local` passes at baseline

---

## Phase 1 — Deal Data Contract (Pydantic Schemas)
**Complexity:** M | **Estimated touch points:** 2 files

**Purpose:** Create formal typed schemas for deal JSONB sub-objects. This becomes the single source of truth for what fields a deal should contain.

**Blast Radius:**
- Services affected: Backend (new module, no behavior change yet)
- Pages affected: None
- Downstream consumers: Enrichment service (Phase 2), API response validation (future)

### Tasks
- P1-01: **Create** `/home/zaks/zakops-agent-api/apps/backend/src/core/deals/deal_contract.py`
  - Define `DealBrokerContract(BaseModel)` — name, email, company, phone (all Optional[str])
  - Define `DealMetadataContract(BaseModel)` — asking_price, ebitda, revenue, sde, multiple (all Optional[float]), nda_status, cim_received, priority (Optional), plus traceability fields: field_confidences (Optional[dict]), langsmith_run_id, langsmith_trace_url (Optional[str]), attachment_count (Optional[int]), people (Optional[list])
  - Define `DealCompanyInfoContract(BaseModel)` — company_name, sector, role, location (all Optional[str])
  - All use `model_config = ConfigDict(extra='allow')` for forward compatibility
  - **Checkpoint:** Module imports without error: `python -c "from src.core.deals.deal_contract import DealBrokerContract"`
- P1-02: **Create** `/home/zaks/zakops-agent-api/apps/backend/src/core/deals/__init__.py` if it doesn't exist (ensure package is importable)

### Rollback Plan
1. Delete `deal_contract.py`
2. Verify: `make validate-local` passes

### Gate P1
- `python -c "from src.core.deals.deal_contract import DealBrokerContract, DealMetadataContract, DealCompanyInfoContract"` succeeds
- `bash scripts/test.sh` passes (no regression)
- `make validate-local` passes

---

## Phase 2 — Enrichment Service (Extract from orchestration/main.py)
**Complexity:** L | **Estimated touch points:** 3 files

**Purpose:** Move enrichment logic from a private function in a 3000-line file to a dedicated service class. Wire all 4 approve paths to use the service. This makes it structurally harder to bypass enrichment.

**Blast Radius:**
- Services affected: Backend (enrichment behavior, approve paths)
- Pages affected: Deal page (enriched data quality)
- Downstream consumers: All 4 approve paths, future approve paths

### Tasks
- P2-01: **Create** `/home/zaks/zakops-agent-api/apps/backend/src/core/deals/enrichment.py`
  - Move `_parse_currency()`, `_parse_multiple()`, `_build_deal_enrichment()` from orchestration/main.py
  - Wrap in `DealEnrichmentService` class
  - Add `validate_extraction_evidence(ev: dict) -> list[str]` method that returns warnings for missing expected keys (F-07)
  - Add `merge_into_existing(current_broker: dict, current_meta: dict, current_company: dict, enrichment: dict) -> dict` method for non-destructive merge (DRY up the 3 merge blocks in approve paths)
  - Carry forward: field_confidences, langsmith_run_id, langsmith_trace_url, attachment_count, entities.people (F-03, F-04, F-05, F-06)
  - **Checkpoint:** Module imports without error
- P2-02: **Update** `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
  - Replace inline `_parse_currency`, `_parse_multiple`, `_build_deal_enrichment` with import from enrichment service
  - Replace 4 inline merge blocks with `service.merge_into_existing()` calls
  - Keep the inline code as comments for one commit, then remove
  - **Checkpoint:** All 4 approve paths use the service class
- P2-03: **Verify** by rebuilding backend and running tests
  - `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend`
  - `bash scripts/test.sh`

### Decision Tree
- **IF** `src/core/deals/__init__.py` doesn't exist → create it with empty content
- **IF** circular import occurs (orchestration/main.py ↔ core/deals) → use lazy import pattern

### Rollback Plan
1. Revert orchestration/main.py to pre-refactor state
2. Delete enrichment.py
3. `docker compose build backend && docker compose up -d backend`

### Gate P2
- `bash scripts/test.sh` passes
- `grep -c "_build_deal_enrichment\|_parse_currency\|_parse_multiple" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` returns 0 (all moved out)
- `grep -c "DealEnrichmentService\|enrichment_service" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` returns 4+ (all 4 paths use service)
- Backend starts without error: `docker compose up -d backend && sleep 5 && curl -sf http://localhost:8091/health`

---

## Phase 3 — PATCH Endpoint JSONB Merge
**Complexity:** S | **Estimated touch points:** 1 file

**Purpose:** Change the PATCH /api/deals/{deal_id} endpoint from JSONB overwrite to per-key merge. This prevents any caller from accidentally destroying enriched data by sending partial objects.

**Blast Radius:**
- Services affected: Backend (PATCH behavior change)
- Pages affected: None (dashboard doesn't PATCH JSONB columns currently)
- Downstream consumers: Any future deal edit feature, agent tools

### Tasks
- P3-01: **Modify** the `update_deal()` function in orchestration/main.py
  - For JSONB columns (broker, metadata, company_info, identifiers): change from `SET {field} = $N::jsonb` to `SET {field} = COALESCE({field}, '{{}}'::jsonb) || $N::jsonb`
  - Non-JSONB columns (canonical_name, display_name, folder_path) remain as direct assignment
  - **Checkpoint:** Read the SQL query string and verify merge pattern

### Rollback Plan
1. Revert the SQL pattern back to direct assignment
2. Rebuild backend

### Gate P3
- `bash scripts/test.sh` passes
- Backend starts: `curl -sf http://localhost:8091/health`
- `make validate-local` passes

---

## Phase 4 — extraction_evidence Format Validation
**Complexity:** S | **Estimated touch points:** 1 file

**Purpose:** Add structural validation to the injection endpoint so format drift in the agent's output produces visible warnings rather than silent data loss.

**Blast Radius:**
- Services affected: Backend (injection endpoint logging)
- Pages affected: None
- Downstream consumers: Enrichment service (reads validated data)

### Tasks
- P4-01: **Add** validation logic in the enrichment service's `validate_extraction_evidence()` method
  - Check for expected keys: at least one of (broker_name OR broker.name), at least one of (asking_price OR financials.asking_price)
  - If extraction_evidence is non-empty but has ZERO recognized keys → log WARNING with actual keys
  - Return list of warnings (empty list = all recognized)
- P4-02: **Call** validation in the approve endpoint after reading extraction_evidence
  - Log warnings but do NOT reject — validation is advisory, not blocking
  - **Checkpoint:** Test with a quarantine item that has extraction_evidence with unusual keys

### Rollback Plan
1. Remove validation call from approve endpoint
2. Rebuild backend

### Gate P4
- `bash scripts/test.sh` passes
- Backend starts without error
- `make validate-local` passes

---

## Phase 5 — Quarantine Source Link in Deal Page
**Complexity:** M | **Estimated touch points:** 3 files

**Purpose:** Add a "Source Intelligence" card to the deal page that shows linked quarantine data. This gives operators a fallback when enrichment misses fields, and exposes field confidences and the full extraction evidence.

**Blast Radius:**
- Services affected: Backend (new endpoint), Dashboard (new component)
- Pages affected: Deal detail page
- Downstream consumers: Operators viewing deal details

### Tasks
- P5-01: **Add** backend endpoint `GET /api/deals/{deal_id}/quarantine-source` in orchestration/main.py
  - Query: `SELECT * FROM zakops.quarantine_items WHERE deal_id = $1 OR id::text = (SELECT identifiers->>'quarantine_item_id' FROM zakops.deals WHERE deal_id = $1) ORDER BY created_at DESC LIMIT 1`
  - Return: quarantine item with extraction_evidence, field_confidences, triage_summary, attachments, sender info
  - Return 404 if no linked quarantine item
  - **Checkpoint:** `curl -sf http://localhost:8091/api/deals/DL-0121/quarantine-source | python3 -m json.tool | head -20`
- P5-02: **Add** fetch function in dashboard `apps/dashboard/src/lib/api.ts`
  - `getDealQuarantineSource(dealId: string)` — fetches the new endpoint
  - Loose Zod schema (z.record for most fields) — quarantine data is exploratory, not strongly typed
- P5-03: **Add** "Source Intelligence" card to deal Overview tab in `apps/dashboard/src/app/deals/[id]/page.tsx`
  - Only shown when `identifiers?.quarantine_item_id` is present
  - Shows: triage_summary, field_confidences (as confidence badges), extraction_evidence (collapsible JSON), attachment count, langsmith trace link
  - Per Surface 9 design system rules
  - Graceful empty state if quarantine item was purged
  - **Checkpoint:** Open deal page in browser, verify card appears for triage-sourced deals

### Decision Tree
- **IF** no quarantine item linked → card not rendered (hidden)
- **IF** quarantine item exists but extraction_evidence is empty → show "No extraction data available"
- **IF** fetch fails → show error state per Promise.allSettled fallback pattern

### Rollback Plan
1. Remove the new endpoint from orchestration/main.py
2. Remove fetch function from api.ts
3. Remove card from deal page
4. Rebuild backend + restart dashboard

### Gate P5
- `npx tsc --noEmit` passes in dashboard
- Backend starts: `curl -sf http://localhost:8091/health`
- New endpoint returns data: `curl -sf http://localhost:8091/api/deals/DL-0121/quarantine-source`
- `make validate-local` passes

---

## Phase 6 — Backfill Traceability for Existing Deals
**Complexity:** S | **Estimated touch points:** 1 file (SQL)

**Purpose:** Enrich existing deals with field_confidences, langsmith metadata, and attachment counts from their source quarantine items.

**Blast Radius:**
- Services affected: Database (deal rows updated)
- Pages affected: Deal page (more metadata visible)
- Downstream consumers: Dashboard deal cards

### Tasks
- P6-01: **Write** backfill SQL at `/home/zaks/zakops-agent-api/apps/backend/scripts/backfill_deal_traceability.sql`
  - JOIN deals with quarantine_items
  - For each deal: add field_confidences, langsmith_run_id, langsmith_trace_url, attachment_count to metadata using per-key COALESCE (never overwrite existing)
  - Dry-run with `BEGIN; ... ROLLBACK;` first
- P6-02: **Execute** the backfill after dry-run verification
  - **Checkpoint:** Verify DL-0121 metadata now includes langsmith and confidence data

### Rollback Plan
1. No structural rollback needed — backfill is additive
2. To remove: `UPDATE zakops.deals SET metadata = metadata - 'field_confidences' - 'langsmith_run_id' - 'langsmith_trace_url' - 'attachment_count' WHERE metadata ? 'field_confidences'`

### Gate P6
- Existing deals show traceability metadata via API
- No deal shows NULL/broken data after backfill

---

## Phase 7 — Final Validation & Bookkeeping
**Complexity:** S | **Estimated touch points:** 1 file

**Purpose:** Run all validation gates, verify end-to-end, update bookkeeping.

**Blast Radius:** None

### Tasks
- P7-01: **Rebuild** backend: `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend`
- P7-02: **Run** `npx tsc --noEmit` in dashboard
- P7-03: **Run** `make validate-local`
- P7-04: **Browser verify:** Approve a quarantine item → deal page shows full enrichment INCLUDING field_confidences and source intelligence card
- P7-05: **Browser verify:** Existing deal (DL-0121) shows traceability metadata
- P7-06: **Update** `/home/zaks/bookkeeping/CHANGES.md`
- P7-07: **Produce** completion report

### Gate P7
- All validation passes
- Browser verification confirms end-to-end data flow
- CHANGES.md updated
- Completion report produced

---

## Dependency Graph

```
Phase 0 (Discovery)
    |
    v
Phase 1 (Deal Data Contract)
    |
    v
Phase 2 (Enrichment Service) ----+
    |                             |
    v                             v
Phase 3 (PATCH Merge)     Phase 4 (Format Validation)
    |                             |
    +-----------------------------+
    |
    v
Phase 5 (Source Link Card)
    |
    v
Phase 6 (Backfill Traceability)
    |
    v
Phase 7 (Final Validation)
```

Phases 3 and 4 can run in parallel after Phase 2.

---

## Acceptance Criteria

### AC-1: Deal Data Contract Exists
Pydantic models `DealBrokerContract`, `DealMetadataContract`, `DealCompanyInfoContract` exist and are importable.

### AC-2: Enrichment Service Replaces Inline Helper
`_build_deal_enrichment`, `_parse_currency`, `_parse_multiple` no longer exist in orchestration/main.py. All 4 approve paths use `DealEnrichmentService`.

### AC-3: PATCH Uses JSONB Merge
`PATCH /api/deals/{id}` with partial broker object preserves existing keys.

### AC-4: field_confidences Carried to Deal
Approving a quarantine item with field_confidences → deal metadata includes field_confidences.

### AC-5: Traceability Metadata Carried to Deal
Approving a quarantine item with langsmith_run_id → deal metadata includes langsmith_run_id and langsmith_trace_url.

### AC-6: extraction_evidence Format Validated
Non-empty extraction_evidence with zero recognized keys produces a WARNING log.

### AC-7: Quarantine Source Card Visible
Deal page shows "Source Intelligence" card for triage-sourced deals.

### AC-8: Existing Deals Backfilled
DL-0121 metadata includes field_confidences and langsmith traceability after backfill.

### AC-9: No Regressions
`make validate-local` passes, `npx tsc --noEmit` passes, `bash scripts/test.sh` passes.

### AC-10: Bookkeeping
CHANGES.md updated. Completion report produced.

---

## Guardrails

1. **Scope boundary** — Do NOT modify database migrations. JSONB columns already support arbitrary keys. Do NOT modify the agent API or injection endpoint schema (only add validation warnings).
2. **Generated file protection** — Never edit `*.generated.ts` or `*_models.py` (hooks enforce this).
3. **Operator corrections always win** — The enrichment service maintains the priority hierarchy. Never let extraction_evidence override user corrections.
4. **Non-destructive merge** — When enriching existing deals, only fill NULL/missing keys.
5. **Surface 9 compliance** — New dashboard card follows design system rules in `.claude/rules/design-system.md`.
6. **WSL safety** — CRLF fix on any new .sh/.sql files. Ownership fix on files under /home/zaks/.
7. **F-08 is by design** — Manual deal creation without quarantine source does NOT need enrichment. Document, don't fix.
8. **F-10 and F-11 are out of scope** — Retention cleanup and undo-approve FSM bypass are separate infrastructure concerns.
9. **Backward compatibility** — Existing deals with no quarantine source must continue to work. Source Intelligence card hidden when no source exists.
10. **API contract safety** — If the new endpoint changes DealResponse shape, run `make update-spec && make sync-types && npx tsc --noEmit`.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I confirm all 4 approve paths use the enrichment helper?"
- [ ] "Did I identify all affected contract surfaces?"

### After every code change:
- [ ] "Did I run `bash scripts/test.sh` to check for regressions?"
- [ ] "Am I using the enrichment SERVICE, not re-implementing enrichment inline?"
- [ ] "If I created a file under /home/zaks/, did I fix ownership?"

### Before marking Phase 2 COMPLETE:
- [ ] "Are there ZERO references to `_build_deal_enrichment` or `_parse_currency` in orchestration/main.py?"
- [ ] "Do all 4 approve paths import from the enrichment service?"
- [ ] "Did I handle the case where extraction_evidence is a JSON string, not a dict?"

### Before marking the mission COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce a completion report with evidence for every AC?"
- [ ] "Did I create ALL files listed in the Files to Create table?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` | P2, P3, P5 | Extract enrichment to service; JSONB merge in PATCH; new quarantine-source endpoint |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | P5 | Add getDealQuarantineSource fetch function |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | P5 | Add Source Intelligence card |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/apps/backend/src/core/deals/deal_contract.py` | P1 | Pydantic models for deal JSONB sub-objects |
| `/home/zaks/zakops-agent-api/apps/backend/src/core/deals/enrichment.py` | P2 | DealEnrichmentService class |
| `/home/zaks/zakops-agent-api/apps/backend/scripts/backfill_deal_traceability.sql` | P6 | Backfill script for traceability metadata |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/apps/backend/db/init/001_base_tables.sql` | Database schema reference |
| `/home/zaks/zakops-agent-api/apps/backend/src/core/deals/workflow.py` | Deal FSM reference |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py` | Agent tool definitions |
| `/home/zaks/bookkeeping/docs/DATA-FLOW-ARCH-REVIEW-MASTER.md` | Architecture review findings |

---

<!-- Adopted from Improvement Area IA-15 -->
## Git Commit Discipline

- Branch: Work on current branch (no new feature branch needed — this is a continuation)
- Commit after each phase gate passes
- Format: `DEAL-DATA-ARCHITECTURE-001 P{N}: {description}`
- Final commit: `DEAL-DATA-ARCHITECTURE-001: Systemic fix for quarantine-to-deal data flow`

---

## Completion Report Template

```
## Completion Report — DEAL-DATA-ARCHITECTURE-001

**Date:** 2026-02-18
**Executor:** Claude Opus 4.6
**Status:** {COMPLETE / PARTIAL}

### Phases Completed
| Phase | Name | Gate | Status |
|-------|------|------|--------|
| P0 | Discovery & Baseline | Gate P0 | {PASS/FAIL} |
| P1 | Deal Data Contract | Gate P1 | {PASS/FAIL} |
| P2 | Enrichment Service | Gate P2 | {PASS/FAIL} |
| P3 | PATCH JSONB Merge | Gate P3 | {PASS/FAIL} |
| P4 | Format Validation | Gate P4 | {PASS/FAIL} |
| P5 | Source Link Card | Gate P5 | {PASS/FAIL} |
| P6 | Backfill Traceability | Gate P6 | {PASS/FAIL} |
| P7 | Final Validation | Gate P7 | {PASS/FAIL} |

### Acceptance Criteria
| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-1 | Deal Data Contract exists | {PASS/FAIL} | {evidence} |
| AC-2 | Enrichment Service replaces inline helper | {PASS/FAIL} | {evidence} |
| AC-3 | PATCH uses JSONB merge | {PASS/FAIL} | {evidence} |
| AC-4 | field_confidences carried to deal | {PASS/FAIL} | {evidence} |
| AC-5 | Traceability metadata carried | {PASS/FAIL} | {evidence} |
| AC-6 | extraction_evidence validated | {PASS/FAIL} | {evidence} |
| AC-7 | Source Intelligence card visible | {PASS/FAIL} | {evidence} |
| AC-8 | Existing deals backfilled | {PASS/FAIL} | {evidence} |
| AC-9 | No regressions | {PASS/FAIL} | {evidence} |
| AC-10 | Bookkeeping complete | {PASS/FAIL} | {evidence} |

### Validation Results
- `make validate-local`: {PASS/FAIL}
- TypeScript compilation: {PASS/FAIL}
- Backend tests: {PASS/FAIL}

### Files Modified
{list}

### Files Created
{list}

### Notes
{deviations, decisions, issues}
```

---

## Stop Condition

DONE when all 10 AC are met, all 8 phase gates pass, `make validate-local` and `npx tsc --noEmit` both pass, backend tests pass, and the completion report is produced with evidence for every AC.

Do NOT proceed to: UI redesign, agent pipeline changes, additional deal page features, or FSM bypass fixes (F-10/F-11). Those are separate missions.

---

*End of Mission Prompt — DEAL-DATA-ARCHITECTURE-001*
