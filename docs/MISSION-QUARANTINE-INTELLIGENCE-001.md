# MISSION: QUARANTINE-INTELLIGENCE-001
## World-Class Quarantine Decision Support — Rich Triage Intelligence Rendering
## Date: 2026-02-18
## Classification: Feature Build (Dashboard + Integration Contract)
## Prerequisite: INTEGRATION-PHASE3-BUILD-001 (Complete, 8/8 AC), Pipeline A First Run (14/14 injections PASS)
## Successor: QA-QI-VERIFY-001

---

## Mission Objective

**Build** a world-class quarantine review experience that renders the full triage intelligence the LangSmith agent produces — enabling operators to make approve/reject decisions in seconds with full context, not minutes with guesswork.

**This mission does THREE things:**
1. Fixes the Zod schema mismatch that causes "Preview not found" (root cause: `QuarantinePreviewSchema` silently drops 10+ fields the backend returns)
2. Builds a rich detail panel with 8 composable components for triage intelligence (summary, deal signals, reasoning, materials, entities, sender reputation, email body)
3. Produces a deployment package defining the structured `extraction_evidence` schema for the LangSmith agent to populate

**This mission does NOT:**
- Modify backend code (all data already flows through the API correctly)
- Add database migrations (extraction_evidence and field_confidences are existing JSONB columns)
- Modify bridge code (bridge already passes all fields)
- Implement agent-side changes (deployment package is documentation for relay)
- Redesign the quarantine list/filter/action architecture — only the detail panel and list item rendering

**Source material:**
- Pipeline A first run results (14/14 injections, 25/25 labels) — `/home/zaks/bookkeeping/CHANGES.md` entry 2026-02-18
- Integration Spec v1.0 — `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md`
- Integration Roadmap — `/home/zaks/bookkeeping/docs/INTEGRATION-ROADMAP.md`
- Phase 3 Deployment Package — `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE3-DEPLOYMENT-PACKAGE.md`
- LangSmith canonical output schema — `/tmp/langsmith-export/schemas/canonical_output_schema.json`
- LangSmith triage classifier — `/tmp/langsmith-export/subagents/triage_classifier/AGENTS.md`

---

## Context

### Current State

Pipeline A is operational — the LangSmith agent triages 25 emails, classifies them (15 DEAL_SIGNAL, 4 NEWSLETTER, 6 SPAM), applies Gmail labels, and injects 14 quarantine items via `zakops_inject_quarantine`. The backend stores all 31 fields including `extraction_evidence` (JSONB), `field_confidences` (JSONB), `triage_summary`, `company_name`, `broker_name`, `urgency`, `confidence`, and `email_body_snippet`.

### The Three Gaps

**Gap 1 — Agent produces intelligence but doesn't inject it:**
The agent's triage pipeline produces typed links (CIM/dataroom/NDA with vendor + auth flags), broker identity (name/title/firm/type), urgency signal lists, classification reasoning chains, sender reputation scores, deal match confidence, financial terms (asking price, revenue, EBITDA, multiple), and per-entity evidence trails. Most of this is lost because `extraction_evidence` is passed as an empty dict or minimally populated. The schema for what should live inside this JSONB field is undefined — there is no contract.

**Gap 2 — Dashboard drops data the backend sends:**
The backend returns all fields in both list (`GET /api/quarantine`) and detail (`GET /api/quarantine/{id}`) endpoints, including `extraction_evidence`, `field_confidences`, `triage_summary`, `email_body_snippet`. But the dashboard's `getQuarantinePreview()` (line 949 of `api.ts`) parses the response against `QuarantinePreviewSchema` (lines 228-256), which is an older schema that OMITS: `extraction_evidence`, `field_confidences`, `triage_summary`, `email_body_snippet`, `company_name`, `broker_name`, `urgency`, `confidence`, `classification`, `version`, `source_type`, `is_broker`. Since Zod validation fails or returns an incomplete object, the page shows "Preview not found."

**Gap 3 — Detail panel design is minimal:**
Even fields that flow through `selectedItem` (list data) are barely rendered. The detail panel shows: subject, sender, routing badge, confidence bar, triage summary (from list data), 6 flat key fields, field confidences, links, attachments, email body. Missing entirely: classification reasoning, urgency signals, deal financial terms, broker title/firm, typed links, entity evidence trails, sender reputation.

### Prior Deliverables That Must Not Regress

- Quarantine list filtering (status, classification, urgency, sender, search) — all existing filters
- Quarantine actions (approve, reject, escalate, delegate, bulk operations, delete) — all handlers
- Routing conflict display and "Approve into this deal" flow
- Shadow mode badge rendering
- ConfidenceIndicator component (sm/md/lg sizes)
- Delegation dialog with type selection

---

## Glossary

| Term | Definition |
|------|-----------|
| extraction_evidence | JSONB column on `zakops.quarantine_items` — stores structured triage intelligence from the agent. Currently free-form dict, this mission defines its schema |
| field_confidences | JSONB column on `zakops.quarantine_items` — stores per-field confidence scores (0.0-1.0). Currently `z.record(z.any())` in Zod |
| QuarantinePreviewSchema | Zod schema in `api.ts` (lines 228-256) used by `getQuarantinePreview()` — the root cause of "Preview not found". Does NOT match `QuarantineResponse` |
| QuarantineItemSchema | Zod schema in `api.ts` (lines 175-213) used by the list endpoint — DOES include most fields |
| Triage Intelligence | The full agent analysis for a quarantine item: classification reasoning, urgency signals, financials, broker identity, typed links, entities with evidence, deal match confidence |
| sender-intelligence endpoint | Existing `GET /api/quarantine/sender-intelligence?sender_email=X` (lines 2039-2148 of main.py) — returns approval rate, broker likelihood, deal associations. Currently has no dashboard client |

---

## Architectural Constraints

- **Promise.allSettled mandatory** — Per Surface 9 (A1). The sender intelligence fetch runs independently from preview fetch. Use `Promise.allSettled` with typed empty fallbacks. `Promise.all` is banned.
- **Surface 9 compliance** — Per `.claude/rules/design-system.md`. `console.warn` for expected degradation (backend down, preview unavailable). `console.error` for unexpected failures only.
- **Generated file protection** — Per contract surface discipline. Never edit `*.generated.ts` or `*_models.py`. Import from bridge files only.
- **Middleware proxy pattern** — JSON 502 on backend failure, never HTML 500. Any new proxy routes follow existing pattern.
- **InfoGrid pattern** — `grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 items-baseline` (from deal detail page). Labels left-aligned muted, values right-aligned medium.
- **Collapsible pattern** — `IconChevronRight` with `group-data-[state=open]:rotate-90`. Trigger as flex with items-center gap-3.
- **Card section pattern** — `Card > CardHeader(pb-3) > CardContent(space-y-3)`. CardTitle as text-base.
- **Import discipline** — Import types from `@/lib/api` (bridge). Import UI components from `@/components/ui/*`. Import icons from `@tabler/icons-react`.

---

## Anti-Pattern Examples

### WRONG: Separate Zod schema that drifts from backend response
```
const QuarantinePreviewSchema = z.object({
  action_id: z.string().nullable().optional(),
  // ... 15 fields, but extraction_evidence is MISSING
});
// Backend sends 30+ fields → Zod silently drops the extras → "Preview not found"
```

### RIGHT: Single schema matching the backend response model
```
const QuarantineItemSchema = z.object({
  // All 30+ fields from QuarantineResponse
  extraction_evidence: ExtractionEvidenceSchema.nullable().optional(),
  field_confidences: z.record(z.number()).nullable().optional(),
  // ... every field the backend returns
}).passthrough();  // Forward compat for new fields
```

### WRONG: Crash on null extraction_evidence
```
const reasons = item.extraction_evidence.reasons.map(r => ...);
// Throws if extraction_evidence is null or reasons is undefined
```

### RIGHT: Defensive access with fallback
```
const reasons = item.extraction_evidence?.reasons ?? [];
// Old items without extraction_evidence render gracefully
```

### WRONG: Hardcoded currency formatting
```
<span>${item.extraction_evidence?.financials?.asking_price}</span>
// Shows "$2500000" or "$undefined"
```

### RIGHT: Formatted with human-readable scale
```
<span>{formatCurrency(item.extraction_evidence?.financials?.asking_price)}</span>
// Shows "$2.5M" or "—" for null
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Zod schema unification breaks existing list rendering — list items use QuarantineItemSchema already, but adding ExtractionEvidenceSchema sub-schema changes the parse behavior | MEDIUM | List page crashes | P1 gate: verify both list AND detail render correctly after schema change. Use `.passthrough()` on ExtractionEvidenceSchema |
| 2 | New components import patterns that don't exist yet — e.g., referencing a Card variant or icon not in the project | LOW | TypeScript compile failure | P2 gate: `npx tsc --noEmit` after every component. Only use components confirmed in exploration |
| 3 | Detail panel replacement breaks existing approve/reject/delegate handlers — action buttons reference `selectedItem` or `preview` state | HIGH | Operators can't take action on quarantine items | P3-06: explicit verification of all 6 action handlers. Keep action button section unchanged, only replace content above it |
| 4 | Sender intelligence endpoint returns unexpected shape, causing Zod parse failure and blank SenderIntelCard | MEDIUM | Missing sender data, but page still works | SenderIntelCard handles null gracefully. `getSenderIntelligence` returns null on any parse failure |
| 5 | Old quarantine items (pre-Pipeline A, no extraction_evidence) crash new components | HIGH | Existing items become unviewable | Every component uses `?.` optional chaining and `?? []` fallbacks. P2 gate: test with both rich and bare items |

---

## Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Confirm root cause, capture baseline, identify affected surfaces.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Run baseline validation** — `make validate-local` must exit 0
  - **Checkpoint:** Exit 0 confirmed before any changes
- P0-02: **Validate affected surfaces** — `make validate-surface9 && make validate-surface17`
  - **Checkpoint:** Both PASS
- P0-03: **Confirm backend returns extraction_evidence** — `curl -s http://localhost:8091/api/quarantine | python3 -c "import sys,json; items=json.load(sys.stdin); print([k for k in items['items'][0].keys() if 'extract' in k or 'field_conf' in k])"` to verify fields are in the API response
  - **Decision Tree:**
    - **IF** fields present → proceed
    - **ELSE IF** backend is down → mark as SKIP, proceed with code-only changes
    - **ELSE** → investigate backend QuarantineResponse model before proceeding
- P0-04: **Reproduce "Preview not found"** — Open `localhost:3003/quarantine`, click any item, check browser console for Zod parse warnings
  - **Checkpoint:** Root cause reproduced (Zod warning or "Preview not found" confirmed)
- P0-05: **Count existing QuarantinePreviewSchema references** — `grep -rn 'QuarantinePreview' /home/zaks/zakops-agent-api/apps/dashboard/src/` to know all references that must be updated
  - **Checkpoint:** Reference count captured

### Gate P0
- `make validate-local` PASS at baseline
- `make validate-surface9 && make validate-surface17` PASS
- Root cause confirmed: QuarantinePreviewSchema drops fields
- All reference sites of QuarantinePreview counted

---

## Phase 1 — Fix Data Pipeline
**Complexity:** M
**Estimated touch points:** 2 files

**Purpose:** Kill "Preview not found" by unifying the Zod schema and wiring up sender intelligence.

### Blast Radius
- **Services affected:** Dashboard (3003) — Zod parsing changes
- **Pages affected:** Quarantine page (list + detail)
- **Downstream consumers:** All quarantine page components that read `preview` state

### Tasks
- P1-01: **Define ExtractionEvidenceSchema** in `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` — structured Zod schema for the JSONB field. Include: `reasons`, `urgency_signals`, `urgency_rationale`, `financials` (nested: asking_price, revenue, ebitda, sde, multiple, valuation_notes), `broker` (nested: name, email, title, firm, firm_type, phone), `entities` (nested: companies array, people array — each with name, role, evidence_snippet, confidence), `typed_links` (array with url, link_type, vendor, auth_required, label), `deal_stage_hint`, `timeline_signals`, `deal_match_confidence`, `match_factors`. Use `.passthrough()` for forward compatibility.
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts`
  - **Checkpoint:** Schema compiles without errors
- P1-02: **Update QuarantineItemSchema** — Replace `extraction_evidence: z.record(z.any())` with `ExtractionEvidenceSchema.nullable().optional()`. Replace `field_confidences: z.record(z.any())` with `z.record(z.number()).nullable().optional()`.
  - Evidence: Same file
  - **Checkpoint:** Existing QuarantineItem type now includes typed extraction_evidence
- P1-03: **Unify getQuarantinePreview** — Change `getQuarantinePreview()` to parse against `QuarantineItemSchema` instead of `QuarantinePreviewSchema`. Return type becomes `QuarantineItem | null`. Remove or deprecate `QuarantinePreviewSchema` and `QuarantinePreview` type.
  - Evidence: Same file
  - **Checkpoint:** Function returns typed QuarantineItem with extraction_evidence accessible
- P1-04: **Add SenderIntelligenceSchema and getSenderIntelligence()** — Zod schema matching the existing `GET /api/quarantine/sender-intelligence` response (rollup, signals, deal_associations). API function with null return on 404/parse failure.
  - Evidence: Same file, reference backend at lines 2039-2148 of main.py
  - **Checkpoint:** Function compiles, types exported
- P1-05: **Update page.tsx types** — Change `preview` state type from `QuarantinePreview | null` to `QuarantineItem | null`. Fix all `preview.` property accesses that relied on QuarantinePreview-specific fields (e.g., `preview.summary`, `preview.extracted_fields`, `preview.email`, `preview.links`, `preview.attachments`).
  - Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
  - **Decision Tree:**
    - **IF** `preview.summary` was an array from the old schema → map to `preview.triage_summary` (string) or `extraction_evidence.reasons` (array)
    - **IF** `preview.extracted_fields.company_guess` → map to `preview.company_name` or `extraction_evidence.entities.companies[0].name`
    - **IF** `preview.email.body` → map to `preview.email_body_snippet`
    - **IF** `preview.links.groups` → this was from the old quarantine_dir disk-based preview. For injected items, use `extraction_evidence.typed_links`. For legacy items, degrade gracefully
  - **Checkpoint:** `npx tsc --noEmit` passes

### Rollback Plan
1. Revert `api.ts` changes (restore QuarantinePreviewSchema)
2. Revert `page.tsx` type changes
3. Verify: `npx tsc --noEmit` passes after rollback

### Gate P1
- `npx tsc --noEmit` exits 0
- Click quarantine item in browser → no "Preview not found"
- Browser console shows no Zod parse warnings for quarantine endpoints
- List rendering unchanged (items still show subject, sender, badges)

---

## Phase 2 — Build Triage Intelligence Components
**Complexity:** L
**Estimated touch points:** 9 new files

**Purpose:** Create composable, gracefully-degrading components for each section of the triage intelligence panel.

### Blast Radius
- **Services affected:** Dashboard (3003) — new components only, not yet integrated
- **Pages affected:** None yet (components are built but not wired in until Phase 3)
- **Downstream consumers:** Phase 3 integration

### Tasks
- P2-01: **Create format-utils.ts** at `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/format-utils.ts` — `formatCurrency(value: string | number | null | undefined): string` (handles "$2.5M", 2500000 → "$2.5M", null → "—"), `formatConfidence(score: number | null | undefined): string` (0.96 → "96%", null → "—")
  - **Checkpoint:** Utility compiles
- P2-02: **Create TriageSummaryCard.tsx** — Shows `triage_summary` text in highlighted card, `deal_match_confidence` as ConfidenceIndicator (lg), `match_factors` as row of Badge components. Empty state: muted "No AI summary available" with info icon.
  - **Checkpoint:** Component compiles, renders with null props without crashing
- P2-03: **Create DealSignalsCard.tsx** — InfoGrid layout: company_name (from flat field or entities[0]), broker (name/title/firm from flat fields or extraction_evidence.broker), financial terms grid (asking_price, revenue, EBITDA, multiple from extraction_evidence.financials), deal_stage_hint badge, timeline_signals as muted text. Empty state: "No deal signals extracted"
  - **Checkpoint:** Component compiles
- P2-04: **Create ClassificationReasoningCard.tsx** — Two Collapsible sections: (1) "Why This Classification" (default open) renders `extraction_evidence.reasons` as styled bullet list; (2) "Urgency Signals" (default open if urgency is HIGH) renders `extraction_evidence.urgency_signals` as amber-tinted badges. Shows `urgency_rationale` as muted text.
  - **Checkpoint:** Component compiles
- P2-05: **Create MaterialsAndLinksCard.tsx** — Renders `extraction_evidence.typed_links` with type badge (CIM/dataroom/NDA/financials/teaser) + vendor badge + auth-required indicator. Falls back to flat attachments field for legacy items.
  - **Checkpoint:** Component compiles
- P2-06: **Create EntitiesCard.tsx** — Two sub-sections: Companies (from extraction_evidence.entities.companies) with role badge, confidence dot, evidence snippet; People (from extraction_evidence.entities.people) with organization. Collapsible evidence snippets.
  - **Checkpoint:** Component compiles
- P2-07: **Create SenderIntelCard.tsx** — Renders sender intelligence from API: known broker badge, broker likelihood score as ConfidenceIndicator, messages seen / approval rate stat row, avg decision time, deal associations as clickable links. Loading skeleton while fetching. Null state: "Sender data unavailable".
  - **Checkpoint:** Component compiles
- P2-08: **Create EmailBodyCard.tsx** — Collapsible card showing email_body_snippet (first 3 lines by default). Expand button reveals full body. Uses `whitespace-pre-wrap text-sm font-mono`.
  - **Checkpoint:** Component compiles
- P2-09: **Create TriageIntelPanel.tsx** — Orchestrator component receiving `item: QuarantineItem`, `senderIntel: SenderIntelligence | null`, `senderIntelLoading: boolean`. Renders all cards in priority order: TriageSummaryCard → DealSignalsCard → ClassificationReasoningCard → MaterialsAndLinksCard → EntitiesCard → SenderIntelCard → EmailBodyCard.
  - **Checkpoint:** Component compiles, renders with empty extraction_evidence without crashing

### Rollback Plan
1. Delete all 9 new component files
2. Verify: `npx tsc --noEmit` passes (no dangling imports)

### Gate P2
- `npx tsc --noEmit` exits 0
- All 9 components exist and compile
- Each component handles null/empty extraction_evidence without crashing (verify by rendering with `{}` and `null` props)

---

## Phase 3 — Integrate into Quarantine Page
**Complexity:** M
**Estimated touch points:** 1 file (page.tsx)

**Purpose:** Replace the existing detail panel content with the new component tree while preserving all action handlers.

### Blast Radius
- **Services affected:** Dashboard (3003) — quarantine page rendering
- **Pages affected:** `/quarantine` page detail panel
- **Downstream consumers:** Operators reviewing quarantine items

### Tasks
- P3-01: **Add sender intelligence state + fetch** — Add `senderIntel` and `senderIntelLoading` state to page.tsx. Add useEffect that fetches sender intelligence when `selectedItem?.sender` changes. Use `getSenderIntelligence()` from api.ts.
  - **Checkpoint:** Sender intelligence loads in React DevTools when clicking items
- P3-02: **Replace detail panel content** with `<TriageIntelPanel>` — Replace lines ~928-1090 (the content section between header and action buttons) with the TriageIntelPanel orchestrator. Pass `item={preview}`, `senderIntel={senderIntel}`, `senderIntelLoading={senderIntelLoading}`.
  - **Checkpoint:** Detail panel renders new component tree
- P3-03: **Enhance header section** — Add classification badge next to urgency badge. Add `extraction_evidence.deal_stage_hint` badge if present. Keep existing ConfidenceIndicator + routing badges.
  - **Checkpoint:** Header shows classification + urgency + confidence + routing
- P3-04: **Remove old inline render helpers** — Move or remove `renderLinkGroups()` and `renderAttachments()` helper functions from page.tsx bottom (now handled by MaterialsAndLinksCard). Verify no other code paths reference them.
  - **Checkpoint:** No dead code, `npx tsc --noEmit` passes
- P3-05: **Update approve dialog** — The corrections grid currently reads from `preview.extracted_fields` (old schema). Update to read from unified item fields: `preview.company_name`, `preview.broker_name`, and `preview.extraction_evidence?.financials?.asking_price`.
  - **Checkpoint:** Approve dialog populates correction fields correctly
- P3-06: **Verify ALL action handlers** — Test each: approve (single + into deal), reject, escalate, delegate, bulk approve/reject, delete. None of these should reference removed code.
  - **Checkpoint:** All 6+ action types work in browser

### Rollback Plan
1. Revert page.tsx to pre-Phase 3 state
2. Verify: `npx tsc --noEmit` passes
3. Verify: quarantine page renders

### Gate P3
- Detail panel renders TriageIntelPanel with all card sections
- All action handlers work (approve, reject, escalate, delegate, bulk, delete)
- Browser verification at `localhost:3003/quarantine`
- `npx tsc --noEmit` exits 0

---

## Phase 4 — Enhance Queue List Items
**Complexity:** S
**Estimated touch points:** 1 file (page.tsx, list section)

**Purpose:** Add key decision signals to list items for faster scanning without clicking.

### Blast Radius
- **Services affected:** Dashboard (3003) — quarantine list sidebar
- **Pages affected:** `/quarantine` list items only
- **Downstream consumers:** Operators scanning the queue

### Tasks
- P4-01: **Add company_name to list items** — Below sender, show `company_name` in muted text (truncated). This is already in the list data.
  - **Checkpoint:** Company name visible in list
- P4-02: **Add triage_summary snippet** — Show first 80 chars of `triage_summary` as a third line, muted and truncated.
  - **Checkpoint:** Summary snippet visible in list
- P4-03: **Add broker badge** — If `broker_name` exists, show as a small secondary badge.
  - **Checkpoint:** Broker badge visible on items that have broker_name

### Rollback Plan
1. Revert list item rendering in page.tsx
2. Verify: no layout overflow

### Gate P4
- List items show: subject (bold) → sender + broker → company + summary snippet
- No layout overflow or visual regression
- `npx tsc --noEmit` exits 0

---

## Phase 5 — Agent Deployment Package + Schema Documentation
**Complexity:** S
**Estimated touch points:** 2 new documentation files

**Purpose:** Define the extraction_evidence schema contract and produce a deployment package for the LangSmith agent.

### Blast Radius
- **Services affected:** None (documentation only)
- **Pages affected:** None
- **Downstream consumers:** LangSmith agent (via Zak relay)

### Tasks
- P5-01: **Write EXTRACTION_EVIDENCE_SCHEMA.md** at `/home/zaks/bookkeeping/docs/EXTRACTION_EVIDENCE_SCHEMA.md` — The complete structured schema (TypeScript interface + JSON Schema) for the `extraction_evidence` JSONB field. Include: field definitions, types, required vs optional, enum values (link_type, firm_type, deal_stage_hint, entity role), validation rules, and 3 example payloads (full, partial, minimal).
  - **Checkpoint:** Document complete, internally consistent
- P5-02: **Write AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md** at `/home/zaks/bookkeeping/docs/AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md` — Deployment package for LangSmith agent: action items, priority fields (must-have vs nice-to-have), pipeline stage mapping (which triage step produces which field), example of a full injection call with all fields populated, verification checklist.
  - **Checkpoint:** Document is self-contained and actionable
- P5-03: **Copy deployment package to Windows Downloads** — `cp /home/zaks/bookkeeping/docs/AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md /mnt/c/Users/mzsai/Downloads/`
  - **Checkpoint:** File accessible at Windows path

### Rollback Plan
1. Delete documentation files (no code impact)

### Gate P5
- Both documents exist and are internally consistent
- Deployment package includes exact JSON examples the agent can copy

---

## Phase 6 — Validation & Bookkeeping
**Complexity:** S
**Estimated touch points:** 1 file (CHANGES.md)

**Purpose:** Full validation sweep and change log.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** QA-QI-VERIFY-001

### Tasks
- P6-01: **TypeScript compilation** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P6-02: **Full offline validation** — `make validate-local`
- P6-03: **Surface-specific validation** — `make validate-surface9 && make validate-surface17`
- P6-04: **Browser verification** — Verify at `localhost:3003/quarantine`:
  - Click item WITH rich extraction_evidence → all cards render
  - Click item WITHOUT extraction_evidence (old/bare item) → degrades gracefully, no crashes
  - Approve flow works end-to-end
  - Reject flow works
  - Delegate flow works
  - Bulk operations work
- P6-05: **WSL safety** — Fix CRLF on any new .sh files. Fix ownership on new files under `/home/zaks/`.
- P6-06: **Update CHANGES.md** — Record all changes with date, files modified, files created, purpose
- P6-07: **Write completion report** — Per Section 9b template

### Gate P6
- `npx tsc --noEmit` exits 0
- `make validate-local` exits 0
- `make validate-surface9 && make validate-surface17` both PASS
- Browser verified: rich items + bare items + all actions
- CHANGES.md updated
- Completion report written

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ▼
Phase 1 (Fix Data Pipeline)
    │
    ├──────────────────────┐
    ▼                      ▼
Phase 2 (Build Components) Phase 5 (Agent Deployment Package)
    │
    ▼
Phase 3 (Integrate into Page)
    │
    ▼
Phase 4 (Enhance List Items)
    │
    ▼
Phase 6 (Validation & Bookkeeping)
```

Phase 2 and Phase 5 can run in parallel after Phase 1. Phase 3 depends on Phase 2. Phase 4 depends on Phase 3. Phase 6 depends on all.

---

## Acceptance Criteria

### AC-1: No More "Preview not found"
QuarantinePreviewSchema unified with QuarantineItemSchema. `getQuarantinePreview()` returns typed data. Clicking any quarantine item shows content, not "Preview not found."

### AC-2: Structured extraction_evidence Schema Defined
`ExtractionEvidenceSchema` Zod type in api.ts with typed fields for: reasons, urgency_signals, financials, broker, entities, typed_links, deal_stage_hint, timeline_signals, deal_match_confidence, match_factors. Schema documented in EXTRACTION_EVIDENCE_SCHEMA.md.

### AC-3: Triage Summary Renders
TriageSummaryCard shows `triage_summary` text, `deal_match_confidence` bar, and `match_factors` badges when available.

### AC-4: Deal Signals Render
DealSignalsCard shows company, broker (name/title/firm), financial terms, deal stage, and timeline when available.

### AC-5: Classification Reasoning Renders
ClassificationReasoningCard shows `reasons[]` bullet list and `urgency_signals[]` badges when available.

### AC-6: Materials and Links Render
MaterialsAndLinksCard shows typed links with type/vendor/auth badges and attachments when available.

### AC-7: Sender Intelligence Renders
SenderIntelCard fetches and displays: broker badge, approval rate, messages seen, deal associations from the existing backend endpoint.

### AC-8: Backward Compatibility
Old quarantine items (empty or null extraction_evidence) render gracefully — flat fields (company_name, broker_name, triage_summary) still display. No crashes.

### AC-9: All Actions Still Work
Approve (single + into deal), reject, escalate, delegate, bulk, and delete all function correctly after the detail panel redesign.

### AC-10: Queue List Enhanced
List items show company name, triage summary snippet, and broker badge in addition to existing subject/sender/badges.

### AC-11: Agent Deployment Package Complete
EXTRACTION_EVIDENCE_SCHEMA.md and AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md written, internally consistent, and available in Windows Downloads for relay.

### AC-12: No Regressions
`npx tsc --noEmit` exits 0. `make validate-local` exits 0. `make validate-surface9 && make validate-surface17` PASS.

### AC-13: Bookkeeping
CHANGES.md updated. Completion report produced.

---

## Guardrails

1. **Scope fence** — Dashboard + documentation ONLY. No backend code, no bridge code, no migration, no agent code.
2. **Generated file protection** — Never edit `*.generated.ts` or `*_models.py`. Per contract surface discipline.
3. **Backward compatibility** — Every new component MUST handle null/empty extraction_evidence. Old items must not crash.
4. **Surface 9 compliance** — Follow design system patterns. `console.warn` for expected degradation, `console.error` for unexpected.
5. **No over-engineering** — Cards show data when available, muted empty state when not. No skeleton shimmer for data that will never arrive.
6. **WSL safety** — CRLF fix on .sh files, ownership fix on `/home/zaks/` files.
7. **Governance surfaces** — `make validate-surface9` (design system) and `make validate-surface17` (dashboard routes) as phase gates.
8. **Action handler preservation** — Approve/reject/escalate/delegate/bulk/delete handlers must not be broken or refactored. Only the content display above them changes.
9. **Pre-task protocol** — Run `/before-task` or equivalent baseline validation before any changes.
10. **No implementation code in this prompt** — The executor decides HOW to implement. This prompt says WHAT and WHERE.

<!-- Adopted from Improvement Area IA-2 -->
<!-- Adopted from Improvement Area IA-15 -->

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I confirm the backend returns extraction_evidence in the API response?"
- [ ] "Did I count ALL references to QuarantinePreview and QuarantinePreviewSchema?"
- [ ] "Does `make validate-local` pass at baseline?"

### After Phase 1 (Schema Fix):
- [ ] "Did I use `.passthrough()` on ExtractionEvidenceSchema for forward compatibility?"
- [ ] "Did I update ALL references from QuarantinePreview to QuarantineItem?"
- [ ] "Does `npx tsc --noEmit` still pass?"
- [ ] "Do list items still render correctly after the schema change?"

### After each component (Phase 2):
- [ ] "Does this component handle null extraction_evidence without crashing?"
- [ ] "Am I using existing UI components (Card, Badge, Collapsible, ConfidenceIndicator) or creating unnecessary custom ones?"
- [ ] "Does this component follow the InfoGrid pattern from the deal detail page?"

### After Phase 3 (Integration):
- [ ] "Do ALL action handlers still work? (approve, reject, escalate, delegate, bulk, delete)"
- [ ] "Did I test with a bare item (no extraction_evidence) as well as a rich item?"
- [ ] "Is the approve dialog still populating correction fields correctly?"

### Before marking COMPLETE:
- [ ] "Does `make validate-local` pass right now, not 3 phases ago?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce a completion report?"
- [ ] "Did I create ALL 11 files listed in 'Files to Create'?"
- [ ] "Did I verify in browser with BOTH rich and bare quarantine items?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | P1 | Add ExtractionEvidenceSchema, SenderIntelligenceSchema, getSenderIntelligence(). Unify getQuarantinePreview to use QuarantineItemSchema. Update QuarantineItemSchema extraction_evidence and field_confidences types. |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | P1,P3,P4 | Fix preview type (P1). Integrate TriageIntelPanel, add sender intel state/fetch, update approve dialog, remove old render helpers (P3). Enhance list items (P4). |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/format-utils.ts` | P2 | formatCurrency, formatConfidence utility functions |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/TriageIntelPanel.tsx` | P2 | Orchestrator component for detail panel |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/TriageSummaryCard.tsx` | P2 | AI summary + match confidence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/DealSignalsCard.tsx` | P2 | Company, broker, financials, stage |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/ClassificationReasoningCard.tsx` | P2 | Classification reasons + urgency signals |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/MaterialsAndLinksCard.tsx` | P2 | Typed links + attachments |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/EntitiesCard.tsx` | P2 | Companies + people with evidence |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/SenderIntelCard.tsx` | P2 | Sender reputation from API |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/EmailBodyCard.tsx` | P2 | Expandable email body |
| `/home/zaks/bookkeeping/docs/EXTRACTION_EVIDENCE_SCHEMA.md` | P5 | Structured schema documentation |
| `/home/zaks/bookkeeping/docs/AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md` | P5 | Deployment package for LangSmith agent |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | InfoGrid, Card sections, Collapsible, Promise.allSettled patterns |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/actions/action-card.tsx` | Card + status badge + collapsible patterns |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/ConfidenceIndicator.tsx` | Reuse for confidence displays |
| `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` | Surface 9 compliance rules |
| `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` | QuarantineResponse (L247-286), sender-intelligence endpoint (L2039-2148), detail endpoint (L2151-2200) |
| `/tmp/langsmith-export/schemas/canonical_output_schema.json` | Agent triage output schema |
| `/tmp/langsmith-export/subagents/triage_classifier/AGENTS.md` | Classification signal definitions |

---

## Crash Recovery
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash, run these commands to determine current state:

1. `git log --oneline -5` — check committed phases
2. `npx tsc --noEmit` — current compilation state
3. `ls /home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/` — which components exist
4. `grep -c 'TriageIntelPanel' /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` — is Phase 3 integration done?
5. `grep -c 'ExtractionEvidenceSchema' /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` — is Phase 1 done?

---

## Context Checkpoint
<!-- Adopted from Improvement Area IA-1 -->

This mission has 7 phases. If context is becoming constrained after Phase 3, summarize progress, commit intermediate work (`QUARANTINE-INTELLIGENCE-001 P3: Integrate triage intel panel`), and continue in a fresh continuation.

---

## Git Commit Cadence

- **Branch:** Work on current branch (no new feature branch needed — dashboard-only changes)
- **Per-phase commits:**
  - `QUARANTINE-INTELLIGENCE-001 P1: Fix quarantine data pipeline — unify Zod schema, add sender intel API`
  - `QUARANTINE-INTELLIGENCE-001 P2: Build triage intelligence components (9 files)`
  - `QUARANTINE-INTELLIGENCE-001 P3: Integrate TriageIntelPanel into quarantine page`
  - `QUARANTINE-INTELLIGENCE-001 P4: Enhance queue list items with company/broker/summary`
  - `QUARANTINE-INTELLIGENCE-001 P5: Agent extraction_evidence schema + deployment package`
  - `QUARANTINE-INTELLIGENCE-001 P6: Validation + bookkeeping`
- **Final:** `QUARANTINE-INTELLIGENCE-001: World-class quarantine decision support`

---

## Stop Condition

DONE when all 13 AC are met, `make validate-local` passes, `make validate-surface9 && make validate-surface17` pass, browser verified with both rich and bare items, CHANGES.md updated, and completion report produced.

Do NOT proceed to:
- QA-QI-VERIFY-001 (separate session)
- Agent-side code changes (agent populates extraction_evidence via deployment package relay)
- Backend modifications (not needed)
- Bridge modifications (not needed)

---

## Completion Report Template

```
## Completion Report — QUARANTINE-INTELLIGENCE-001

**Date:** 2026-02-18
**Executor:** Claude Code (Opus 4.6)
**Status:** {COMPLETE / PARTIAL}

### Phases Completed
| Phase | Name | Gate | Status |
|-------|------|------|--------|
| P0 | Discovery & Baseline | Gate P0 | {PASS/FAIL} |
| P1 | Fix Data Pipeline | Gate P1 | {PASS/FAIL} |
| P2 | Build Triage Intelligence Components | Gate P2 | {PASS/FAIL} |
| P3 | Integrate into Quarantine Page | Gate P3 | {PASS/FAIL} |
| P4 | Enhance Queue List Items | Gate P4 | {PASS/FAIL} |
| P5 | Agent Deployment Package | Gate P5 | {PASS/FAIL} |
| P6 | Validation & Bookkeeping | Gate P6 | {PASS/FAIL} |

### Acceptance Criteria
| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-1 | No more "Preview not found" | | |
| AC-2 | ExtractionEvidence schema defined | | |
| AC-3 | Triage summary renders | | |
| AC-4 | Deal signals render | | |
| AC-5 | Classification reasoning renders | | |
| AC-6 | Materials and links render | | |
| AC-7 | Sender intelligence renders | | |
| AC-8 | Backward compatibility | | |
| AC-9 | All actions still work | | |
| AC-10 | Queue list enhanced | | |
| AC-11 | Agent deployment package complete | | |
| AC-12 | No regressions | | |
| AC-13 | Bookkeeping | | |

### Validation Results
- `make validate-local`: {PASS/FAIL}
- `npx tsc --noEmit`: {PASS/FAIL}
- `make validate-surface9`: {PASS/FAIL}
- `make validate-surface17`: {PASS/FAIL}

### Files Modified
{List with brief change description}

### Files Created
{List with purpose}

### Notes
{Deviations, decisions, issues}
```

---

*End of Mission Prompt — QUARANTINE-INTELLIGENCE-001*
