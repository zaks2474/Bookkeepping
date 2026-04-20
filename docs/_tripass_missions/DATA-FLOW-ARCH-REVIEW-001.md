# TriPass Investigation Mission: Full-Stack Data Flow Architecture Review

## Objective

Deep architectural review of the complete data injection and lifecycle pipeline — from LangSmith Agent Builder through quarantine to deal lifecycle and beyond. This is NOT a review of a specific patch. This is a review of the SYSTEM ARCHITECTURE that keeps requiring patches.

**Core Question:** Why does this system require incremental module-by-module fixes? What architectural deficiency causes data to fragment at state boundaries?

**Scope:** The ENTIRE pipeline — injection → quarantine → deal creation → deal stage transitions → downstream consumers. Every piece of data injected from the LangSmith Agent Builder must follow a clear, deterministic, and traceable path through the system.

## Source Artifacts

1. Backend orchestration (ALL endpoints): `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
2. Database schema: `/home/zaks/zakops-agent-api/apps/backend/db/init/001_base_tables.sql`
3. Deal workflow engine: `/home/zaks/zakops-agent-api/apps/backend/src/core/deals/workflow.py`
4. Agent injection bridge: `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py`
5. Dashboard DealDetailSchema: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (lines 101-139)
6. Dashboard quarantine page: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
7. Dashboard deal page: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx`
8. Email triage executor: `/home/zaks/zakops-agent-api/apps/backend/src/actions/executors/email_triage_review_email.py`
9. Existing enrichment helper: search for `_build_deal_enrichment` in orchestration/main.py
10. Deal PATCH endpoint: search for `PATCH.*deals` in orchestration/main.py
11. Action executors that modify deals: `/home/zaks/zakops-agent-api/apps/backend/src/actions/executors/`

## Investigation Lenses

### Lens 1: Schema Divergence & Impedance Mismatch

The root cause of repeated patching may be that quarantine and deal schemas were designed independently.

- What fields exist on quarantine_items that have NO corresponding location in the deal schema?
- What fields does the dashboard's DealDetailSchema expect that the backend NEVER populates?
- Is there a formal contract (schema, interface, type) that defines "what data transfers at approval time"? Or is it ad-hoc Python dicts?
- Does the deal schema even have the capacity to hold all the structured data the agent extracts?
- What happens to `field_confidences`, `attachments`, `typed_links` at approval — are they silently dropped?

### Lens 2: Transition Boundary Data Loss

Every state boundary is a potential data loss point.

- **Injection → Storage:** Does the quarantine injection endpoint preserve all agent-submitted fields? Or does it truncate/drop any?
- **Quarantine → Deal (approve):** The `_build_deal_enrichment` helper maps fields. But does it cover 100% of extraction_evidence? What about:
  - `field_confidences` — dropped? preserved? accessible from deal?
  - `attachments` — dropped? The deal has no attachment column.
  - `typed_links` — only NDA/CIM flags are extracted. The actual links are lost.
  - `entities.people[]` — only companies[0].role is extracted. All people data is lost.
  - `raw_body` (email body) — stored in quarantine `raw_content`, never carried to deal.
  - `langsmith_run_id`, `langsmith_trace_url` — traceability lost at deal creation.
- **Deal stage transitions (inbound → screening → qualified → ...):** Does any data change when a deal moves stages? Is there a risk of data loss at stage transitions?
- **Deal PATCH updates:** When an operator manually edits deal fields, does it overwrite enriched data?

### Lens 3: Single Source of Truth Violations

- Where is the canonical definition of "what data a deal should have"? Is it:
  - The database schema? (JSONB columns are schemaless)
  - The DealDetailSchema in TypeScript? (dashboard expectation)
  - The _build_deal_enrichment function? (backend mapping)
  - None of the above?
- Is there a formal "deal data contract" that all paths (quarantine approve, manual create, PATCH update) must comply with?
- The enrichment helper was just bolted on. What prevents the next endpoint from bypassing it?

### Lens 4: Architectural Alternatives

Instead of patching each endpoint to call an enrichment helper, consider:
- **Database trigger approach:** Could a BEFORE INSERT/UPDATE trigger on deals automatically enrich from the linked quarantine item?
- **Domain model approach:** Could there be a `DealFactory.from_quarantine(item, corrections)` that encapsulates ALL field mapping?
- **Event-driven approach:** Could deal creation emit an event that triggers a separate enrichment service?
- **Materialized view approach:** Could the deal page read from a view that JOINs deal + quarantine data on the fly?
- What is the RIGHT architectural pattern for this system's scale and complexity?

### Lens 5: Forward Pipeline (Post-Deal-Creation)

Data doesn't stop flowing when a deal is created.
- What happens when a deal moves from inbound → screening? Does any new data need to flow in?
- What about the case_file? How does it get populated? From quarantine data? From agent actions?
- Does the outbox event system carry enough data for downstream consumers?
- What about the DataRoom folder scaffolding — does it have access to all the enriched deal data?
- What happens when a second quarantine item is approved into the same deal? Does the enrichment merge correctly for multiple sources?

### Lens 6: Dashboard Consumption

The dashboard is the ultimate consumer.
- Does the DealDetailSchema's `coercedNumber` transform actually work with the string values stored by the backfill (e.g., "Asking Price: $2.8M (3.1x SDE)")?
- Are there dashboard components that read directly from quarantine_items for a deal (via deal_id FK)? Should they exist?
- What's the user experience when enrichment data is missing vs. present? Is there a consistent empty-state pattern?
- Does the deal edit form preserve enriched fields when an operator saves other changes?

## Acceptance Gates (TriPass)

- TG-1: Every field in extraction_evidence has a documented destination (deal column, explicit drop with reason, or backlink to quarantine)
- TG-2: The architecture supports adding a new extraction field WITHOUT modifying the approve endpoint
- TG-3: All 4 approve paths (single-new, single-attach, thread-match, bulk) produce identical enrichment quality
- TG-4: No data is silently dropped at any state transition (quarantine→deal, stage→stage)
- TG-5: The proposed architectural fix eliminates the class of bugs where "new endpoint doesn't call enrichment helper"
- TG-6: Dashboard rendering handles both enriched and non-enriched deals gracefully
