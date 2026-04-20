# Quarantine Intelligence Roadmap

**Mission:** `MISSION-QUARANTINE-INTELLIGENCE-001` — World-Class Quarantine Decision Support
**TriPass Review:** `TP-20260218-095911` — Adversarial Review (17 findings, 6/6 gates PASS)
**Date:** 2026-02-18
**Total Phases:** 6 (build) + backlog
**Total Items:** 55 (38 mission tasks + 17 TriPass findings, merged where overlapping)

---

## Roadmap Overview

Operators currently see "Preview not found" when clicking quarantine items. Even when data shows, it's bare — no reasoning, no financials, no broker identity, no entities, no links, no sender reputation. The agent produces rich triage intelligence that is lost at three boundaries: injection (empty extraction_evidence), Zod parsing (schema mismatch), and rendering (minimal UI).

This roadmap transforms quarantine from "decide blind" to "decide in 3 seconds with full context."

**Three inputs produced this roadmap:**
1. **Gap analysis** — Mapped data loss at injection, parsing, and rendering boundaries
2. **Mission prompt** — 7 phases, 13 AC, designed by Claude Opus 4.6
3. **TriPass adversarial review** — 3 agents (Claude + Codex + Gemini), 17 findings, 5 drift items

**Scope fence:** Dashboard + documentation ONLY. No backend code, no bridge code, no migrations, no agent code.

---

## Phase Summary

| Phase | Name | Items | Status | Mission | Report |
|-------|------|-------|--------|---------|--------|
| 1 | Schema Unification & Data Pipeline | 1-10 | PENDING | [Mission](MISSION-QUARANTINE-INTELLIGENCE-001.md) | — |
| 2 | Triage Intelligence Components | 11-24 | PENDING | Same | — |
| 3 | Page Integration & Decision Safety | 25-35 | PENDING | Same | — |
| 4 | Queue Enhancement & Rapid Triage | 36-42 | PENDING | Same | — |
| 5 | Agent Deployment Package | 43-45 | PENDING | Same | — |
| 6 | Validation & Bookkeeping | 46-52 | PENDING | Same | — |

**TriPass Review:** [FINAL_MASTER.md](../_tripass_runs/TP-20260218-095911/FINAL_MASTER.md) — 17 findings, 11 gates, 0% drop rate

---

## Phase 0 — Discovery & Baseline

**Objective:** Confirm root cause, capture baseline, identify affected surfaces.

Pre-flight tasks to run before any code changes:

| # | Task | Gate | Source |
|---|------|------|--------|
| — | Run `make validate-local` baseline | Exit 0 | Mission P0-01 |
| — | Run `make validate-surface9 && make validate-surface17` | Both PASS | Mission P0-02 |
| — | Confirm backend returns `extraction_evidence` in detail endpoint | Field present in curl response | Mission P0-03 |
| — | Reproduce "Preview not found" — click item, check browser console | Zod parse warning or blank panel | Mission P0-04 |
| — | Count all `QuarantinePreview` references in dashboard | Count captured | Mission P0-05 |

**Gate P0:** Baseline green, root cause confirmed.

---

## Phase 1 — Schema Unification & Data Pipeline

**Objective:** Kill "Preview not found." Unify the Zod schema to match the backend response. Add missing fields. Wire up sender intelligence API.

| # | Item | Description | Source | Tier |
|---|------|-------------|--------|------|
| 1 | Define `ExtractionEvidenceSchema` | Structured Zod schema for JSONB field: `reasons`, `urgency_signals`, `financials` (nested), `broker` (nested), `entities` (nested), `typed_links` (array), `deal_stage_hint`, `timeline_signals`, `deal_match_confidence`, `match_factors`. Use `.passthrough()` for forward compat. | Mission P1-01 | — |
| 2 | Define `FieldConfidencesSchema` | `z.record(z.number()).nullable().optional()` replacing `z.record(z.any())` | Mission P1-02 | — |
| 3 | Add routing conflict fields to `QuarantineItemSchema` | Add `routing_conflict: z.boolean().nullable().optional()` and `conflicting_deal_ids: z.array(z.string()).nullable().optional()` — required for "Approve into this deal" flow which reads these from preview | **TriPass F-1** | MUST |
| 4 | Add provenance fields to `QuarantineItemSchema` | Add `langsmith_run_id`, `langsmith_trace_url`, `tool_version`, `prompt_version` — all `z.string().nullable().optional()`. Backend returns them, Zod silently drops them. | **TriPass F-5** | MUST |
| 5 | Update `QuarantineItemSchema` body | Replace `extraction_evidence` and `field_confidences` with typed schemas from items 1-2. Add items 3-4. Add `.passthrough()` on the schema itself. | Mission P1-02, F-1, F-4, F-5 | — |
| 6 | Unify `getQuarantinePreview()` | Parse against `QuarantineItemSchema` instead of `QuarantinePreviewSchema`. Return `QuarantineItem \| null`. On `safeParse` failure, fall back to lenient parse with `schemaDrift` indicator — show degraded data, not "Preview not found." | Mission P1-03, **TriPass F-4** | MUST |
| 7 | Add `SenderIntelligenceSchema` + `getSenderIntelligence()` | Zod schema matching `GET /api/quarantine/sender-intelligence` response. Null return on 404/parse failure. | Mission P1-04 | — |
| 8 | Add `getTriageFeedback()` | API wrapper for existing `GET /api/quarantine/feedback?sender_email=X` endpoint — past decisions from same sender (approval/rejection history, corrections). No dashboard client exists despite backend support. | **TriPass F-13** | SHOULD |
| 9 | Normalize classification values at parse boundary | Agent sends lowercase (`deal_signal`), UI filters use uppercase (`DEAL_SIGNAL`), backend exact-matches. Normalize at API boundary: `toUpperCase()` on parsed items. Add missing filter options (`operational`, `newsletter`, `spam`). | **TriPass F-12** | SHOULD |
| 10 | Update `page.tsx` types | Change `preview` state type from `QuarantinePreview \| null` to `QuarantineItem \| null`. Fix all `.summary`, `.extracted_fields`, `.email.body`, `.links.groups` property accesses. Fix approve dialog correction keys: `company_guess` → `company_name`, `broker_email` → `broker_name` (must match backend `main.py:2809,2816`). | Mission P1-05, **TriPass F-2** | MUST |

**Rollback:** Revert `api.ts` + `page.tsx` type changes.

**Gate P1:**
- `npx tsc --noEmit` exits 0
- Click quarantine item → no "Preview not found"
- No Zod parse warnings in browser console
- List rendering unchanged
- TriPass Gate 1: Schema parity (6 new fields present)
- TriPass Gate 2: No `company_guess` or `broker_email` correction keys
- TriPass Gate 11: Lowercase `deal_signal` matches uppercase filter

---

## Phase 2 — Triage Intelligence Components

**Objective:** Build composable, gracefully-degrading components for each section of the triage intelligence panel. Every component handles null, empty, flat-legacy, and rich-nested data.

| # | Item | Description | Source | Tier |
|---|------|-------------|--------|------|
| 11 | `format-utils.ts` | `formatCurrency()` (handles "$2.5M", 2500000, null → "—"), `formatConfidence()` (0.96 → "96%", null → "—") | Mission P2-01 | — |
| 12 | `TriageSummaryCard.tsx` | `triage_summary` text, `deal_match_confidence` as ConfidenceIndicator (lg), `match_factors` badges. **Add conflicting signals warning:** if `urgency === 'HIGH' && confidence < 0.5` → amber alert "High urgency flagged but confidence is low." If `urgency === 'LOW' && confidence > 0.9` → info note "High confidence — consider expediting." | Mission P2-02, **TriPass F-11** | SHOULD |
| 13 | `DealSignalsCard.tsx` | InfoGrid: company (from flat field OR `entities.companies[0]`), broker (name/title/firm from flat OR `extraction_evidence.broker`), financials grid, deal_stage_hint badge, timeline_signals. **Dual-source pattern:** nested first, flat field fallback. | Mission P2-03, **TriPass F-3** | MUST |
| 14 | `ClassificationReasoningCard.tsx` | Two Collapsible sections: "Why This Classification" (`reasons[]` bullets, default open), "Urgency Signals" (`urgency_signals[]` amber badges, default open if HIGH). `urgency_rationale` as muted text. | Mission P2-04 | — |
| 15 | `MaterialsAndLinksCard.tsx` | Renders `extraction_evidence.typed_links` with type/vendor/auth badges. **3-tier data source:** (1) `typed_links` from nested evidence, (2) `item.links` if flat array, (3) `item.links.groups` if legacy categorized format — port categorized rendering logic as fallback. Same for attachments (flat array vs `{ items: [...] }`). | Mission P2-05, **TriPass F-7** | MUST |
| 16 | `EntitiesCard.tsx` | Companies + people with role badges, confidence dots, evidence snippets. Collapsible evidence. | Mission P2-06 | — |
| 17 | `SenderIntelCard.tsx` | Broker badge, approval rate, messages seen, deal associations. Loading skeleton while fetching. **Include past decisions section:** approval/rejection history from `getTriageFeedback()` — "Last 5: 4 approved, 1 rejected. Common correction: company_name." | Mission P2-07, **TriPass F-13** | SHOULD |
| 18 | `EmailBodyCard.tsx` | Collapsible card, first 3 lines by default. Expand reveals full body. `whitespace-pre-wrap text-sm font-mono`. | Mission P2-08 | — |
| 19 | `ProvenanceFooter.tsx` | Muted metadata row: `tool_version` / `prompt_version`. If `langsmith_trace_url` exists: "View agent trace" external link icon. | **TriPass F-5** | MUST |
| 20 | `TriageIntelPanel.tsx` | Orchestrator: receives `item`, `senderIntel`, `senderIntelLoading`, `triageFeedback`. Renders all cards in priority order + ProvenanceFooter at bottom. | Mission P2-09 | — |
| 21 | Three visual states for empty data | Every component distinguishes: (1) `null` → "Not available" (muted, no icon), (2) `{}` or all-null → "AI analysis ran — no signals detected" (muted, info icon), (3) Partial → render available, hide empty (no dash placeholders). | **TriPass F-3** | MUST |
| 22 | Dual-source data pattern | Every component reads: `extraction_evidence?.field ?? item.flat_field`. Old items render via flat fields, new items via nested evidence. No blank cards for historical data. | **TriPass F-3** | MUST |
| 23 | Graduated confidence visuals | Detail panel Card: left-border tinting by confidence band (≥0.8 green, 0.5-0.8 amber, <0.5 red). TriageSummaryCard: inline warning when confidence < 0.5. | **TriPass F-10** | SHOULD |
| 24 | Confidence-based list item weight | List items with `confidence < 0.5`: upgrade indicator from `size='sm'` (dot) to `size='md'` (labeled badge) so low-confidence items stand out. | **TriPass F-10** | SHOULD |

**Rollback:** Delete all new component files.

**Gate P2:**
- `npx tsc --noEmit` exits 0
- All components compile
- Each handles null/empty extraction_evidence without crashing
- TriPass Gate 4: Legacy flat-format evidence renders via dual-source
- TriPass Gate 5: Null evidence shows "Not available" gracefully
- TriPass Gate 7: Provenance link renders with `langsmith_trace_url`

---

## Phase 3 — Page Integration & Decision Safety

**Objective:** Wire the component tree into the quarantine page. Add fetch safety (abort, debounce, null guards). Add undo. Preserve all action handlers.

| # | Item | Description | Source | Tier |
|---|------|-------------|--------|------|
| 25 | Add sender intelligence state + fetch | `senderIntel`, `senderIntelLoading` state. useEffect on `selectedItem` change. **Null-safe email extraction:** `const email = selectedItem?.sender \|\| selectedItem?.from; if (!email) return;` — legacy items have `sender: null` but `from: "broker@..."`. 300ms debounce (supplementary data). | Mission P3-01, **TriPass F-6** | MUST |
| 26 | Add triage feedback state + fetch | `triageFeedback` state. Fetch from `getTriageFeedback()` alongside sender intel, guarded by same email. | **TriPass F-13** | SHOULD |
| 27 | AbortController for stale fetches | Store `AbortController` in ref. Abort previous on new `selectedId`. Both preview AND sender intel use the controller's signal. Prevents showing data for wrong item during rapid clicking. | **TriPass F-8** | SHOULD |
| 28 | Replace detail panel content | Replace lines ~928-1090 with `<TriageIntelPanel item={preview} senderIntel={senderIntel} senderIntelLoading={senderIntelLoading} triageFeedback={triageFeedback} />`. | Mission P3-02 | — |
| 29 | Enhance header section | Add classification badge next to urgency. Add `deal_stage_hint` badge if present. Keep existing ConfidenceIndicator + routing badges. **Add confidence-based left border** on detail Card. | Mission P3-03, TriPass F-10 | — |
| 30 | Remove old inline render helpers | Remove `renderLinkGroups()` and `renderAttachments()` — now in MaterialsAndLinksCard. Verify no other code paths reference them. | Mission P3-04 | — |
| 31 | Fix approve dialog corrections | Source defaults from `preview.company_name`, `preview.broker_name`, `preview.extraction_evidence?.financials?.asking_price`. Keys: `company_name`, `broker_name`, `asking_price` (matching backend expectations). Add type: `type CorrectionField = 'company_name' \| 'broker_name' \| 'asking_price'`. | Mission P3-05, **TriPass F-2** | MUST |
| 32 | Undo affordance after approve/reject | After successful action: show toast with "Undo" button (5-second timeout). Click calls `undoQuarantineApproval()` (already exists at `api.ts:1139-1149`). Backend endpoint exists at `main.py:3076`. | **TriPass F-14** | SHOULD |
| 33 | Verify ALL action handlers | Test: approve (single), approve into deal (conflict flow), reject, escalate, delegate, bulk approve/reject, delete. None may reference removed code. | Mission P3-06 | — |
| 34 | Routing conflict regression check | Render item with `routing_conflict: true, conflicting_deal_ids: ["deal-A", "deal-B"]`. Verify "Approve into this deal" buttons appear. (This was at risk from schema unification per F-1.) | **TriPass F-1** | MUST |
| 35 | Graceful degradation on parse drift | If `safeParse` fails after schema unification, render partial data with subtle amber banner: "Some fields could not be parsed — displaying available data." Never show "Preview not found" for recoverable drift. | **TriPass F-4** | MUST |

**Rollback:** Revert `page.tsx` to pre-Phase 3 state.

**Gate P3:**
- Detail panel renders TriageIntelPanel with all card sections
- All action handlers work (7 action types verified)
- Browser verification at `localhost:3003/quarantine`
- `npx tsc --noEmit` exits 0
- TriPass Gate 3: Routing conflict UI renders
- TriPass Gate 6: Partial data renders on schema drift (no "Preview not found")
- TriPass Gate 8: Sender null safety — legacy items don't fire 400s
- TriPass Gate 10: Rapid selection shows only last-selected item's data

---

## Phase 4 — Queue Enhancement & Rapid Triage

**Objective:** Enhance list items for faster scanning. Add keyboard shortcuts for keyboard-first triage.

| # | Item | Description | Source | Tier |
|---|------|-------------|--------|------|
| 36 | Add company_name to list items | Below sender, muted text, truncated. Already in list data. | Mission P4-01 | — |
| 37 | Add triage_summary snippet | First 80 chars of `triage_summary` as third line, muted, truncated. | Mission P4-02 | — |
| 38 | Add broker badge to list items | If `broker_name` exists, show as small secondary badge. | Mission P4-03 | — |
| 39 | Visual hierarchy | Subject (bold) → sender + broker badge → company + summary snippet. 4-line list items for deal signals, 2-line for spam/newsletters. | Mission P4-01/02/03 | — |
| 40 | Keyboard shortcuts | `useEffect` keyboard handler at page level: `j`/`k` or Up/Down for navigation, `a` approve, `r` reject, `e` escalate, `d` delegate, `x` toggle bulk-select, `Escape` close dialog, `Enter` confirm in dialog. Guard: only fire when no dialog open, no input/textarea focused. | **TriPass F-9** | SHOULD |
| 41 | Quick approve from list (high confidence) | Icon button on list items meeting ALL: confidence ≥ 0.85, classification = deal_signal, `is_broker === true`. Opens approve dialog pre-filled, skips detail review. Button hidden for items not meeting thresholds. | **TriPass F-15** | NICE |
| 42 | Confidence-based list item visual weight | Low confidence items (<0.5): upgrade from `size='sm'` dot to `size='md'` labeled badge. High confidence items (≥0.85): subtle green left border on list item. | **TriPass F-10** | SHOULD |

**Rollback:** Revert list item rendering in `page.tsx`.

**Gate P4:**
- List items show 4-tier visual hierarchy
- No layout overflow
- `npx tsc --noEmit` exits 0
- TriPass Gate 9: `j`/`k` navigation and `a` approve shortcut work

---

## Phase 5 — Agent Deployment Package

**Objective:** Define the extraction_evidence schema contract. Produce a deployment package the LangSmith agent can consume to start populating rich data.

| # | Item | Description | Source | Tier |
|---|------|-------------|--------|------|
| 43 | Write `EXTRACTION_EVIDENCE_SCHEMA.md` | Complete structured schema: TypeScript interface + JSON Schema. Field definitions, types, required vs optional, enum values (`link_type`, `firm_type`, `deal_stage_hint`, entity role), validation rules, 3 example payloads (full, partial, minimal). | Mission P5-01 | — |
| 44 | Write `AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md` | Deployment package: action items, priority fields (must-have: `reasons[]`, `broker.*`, `financials.*`, `entities.companies[0]`, `typed_links[]`, `deal_match_confidence` + `match_factors[]`; nice-to-have: `urgency_rationale`, `timeline_signals`, `deal_stage_hint`). Pipeline stage mapping, full example injection, verification checklist. | Mission P5-02 | — |
| 45 | Copy to Windows Downloads | `cp` both docs to `/mnt/c/Users/mzsai/Downloads/` for agent relay. | Mission P5-03 | — |

**Gate P5:**
- Both documents exist and are internally consistent
- Deployment package includes exact JSON examples

---

## Phase 6 — Validation & Bookkeeping

**Objective:** Full validation sweep, browser verification with rich and bare items, change log.

| # | Item | Description | Source | Tier |
|---|------|-------------|--------|------|
| 46 | TypeScript compilation | `cd apps/dashboard && npx tsc --noEmit` | Mission P6-01 | — |
| 47 | Full offline validation | `make validate-local` | Mission P6-02 | — |
| 48 | Surface-specific validation | `make validate-surface9 && make validate-surface17` | Mission P6-03 | — |
| 49 | Browser verification (rich item) | Click item WITH rich `extraction_evidence` → all cards render (summary, signals, reasoning, materials, entities, sender, body, provenance) | Mission P6-04 | — |
| 50 | Browser verification (bare item) | Click item WITHOUT `extraction_evidence` (old/null) → graceful degradation, flat fields render, no crashes | Mission P6-04 | — |
| 51 | Browser verification (all actions) | Approve, approve into deal, reject, escalate, delegate, bulk, delete — all work. Undo toast appears after approve. Keyboard shortcuts work. | Mission P6-04 | — |
| 52 | CRLF/ownership fix + CHANGES.md | Fix CRLF on any .sh files. Fix ownership on /home/zaks/ files. Update CHANGES.md. Write completion report. | Mission P6-05/06/07 | — |

**Gate P6:**
- `npx tsc --noEmit` exits 0
- `make validate-local` exits 0
- `make validate-surface9 && make validate-surface17` PASS
- Browser verified: rich items + bare items + all actions + keyboard
- CHANGES.md updated
- Completion report written

---

## Acceptance Criteria (13 from Mission + 11 TriPass Gates)

### Mission Acceptance Criteria

| AC | Description | Phase |
|----|-------------|-------|
| AC-1 | No more "Preview not found" — Zod schema unified | P1 |
| AC-2 | `extraction_evidence` structured schema defined and documented | P1, P5 |
| AC-3 | Triage summary renders (text + confidence + match factors) | P2, P3 |
| AC-4 | Deal signals render (company, broker, financials, stage, timeline) | P2, P3 |
| AC-5 | Classification reasoning renders (reasons + urgency signals) | P2, P3 |
| AC-6 | Materials and links render (typed links + attachments) | P2, P3 |
| AC-7 | Sender intelligence renders (broker badge, approval rate, deals) | P2, P3 |
| AC-8 | Backward compatibility — old items degrade gracefully | P2, P3 |
| AC-9 | All actions still work (approve, reject, escalate, delegate, bulk, delete) | P3 |
| AC-10 | Queue list enhanced (company, broker, summary snippet) | P4 |
| AC-11 | Agent deployment package complete | P5 |
| AC-12 | No regressions (`tsc`, `validate-local`, surfaces 9 + 17) | P6 |
| AC-13 | Bookkeeping (CHANGES.md + completion report) | P6 |

### TriPass Acceptance Gates

| Gate | Description | Validates | Phase |
|------|-------------|-----------|-------|
| TG-1 | Schema parity — 6 new fields in `QuarantineItemSchema` | F-1, F-5 | P1 |
| TG-2 | No `company_guess`/`broker_email` correction keys | F-2 | P1, P3 |
| TG-3 | Routing conflict UI renders with `routing_conflict: true` | F-1 | P3 |
| TG-4 | Legacy flat-format evidence renders via dual-source | F-3 | P2, P3 |
| TG-5 | Null evidence shows "Not available" gracefully | F-3, F-4 | P2 |
| TG-6 | Partial data renders on schema drift (no blank screen) | F-4 | P3 |
| TG-7 | Provenance "View agent trace" link renders | F-5 | P2, P3 |
| TG-8 | Sender null safety — fallback from `sender` to `from` | F-6 | P3 |
| TG-9 | Keyboard navigation (`j`/`k`) and action shortcuts (`a`) | F-9 | P4 |
| TG-10 | AbortController — rapid selection shows correct data | F-8 | P3 |
| TG-11 | Classification filter matches despite case difference | F-12 | P1 |

---

## TriPass Findings Register

Full traceability from TriPass findings to roadmap items.

| Finding | Tier | Title | Roadmap Item(s) |
|---------|------|-------|-----------------|
| F-1 | MUST | Routing conflict fields missing from schema | Item 3, Item 34 |
| F-2 | MUST | Approve dialog sends wrong correction keys | Item 10, Item 31 |
| F-3 | MUST | Empty/legacy extraction_evidence creates blank cards | Items 13, 21, 22 |
| F-4 | MUST | Parse failure returns null → "Preview not found" | Item 6, Item 35 |
| F-5 | MUST | LangSmith provenance fields silently dropped | Item 4, Item 19 |
| F-6 | MUST | Sender intelligence needs null-safe email extraction | Item 25 |
| F-7 | MUST | Legacy link/attachment format preservation | Item 15 |
| F-8 | SHOULD | Async race condition — stale concurrent requests | Item 27 |
| F-9 | SHOULD | Keyboard shortcuts for rapid triage | Item 40 |
| F-10 | SHOULD | Confidence lacks graduated visual weight | Items 23, 24, 42 |
| F-11 | SHOULD | Conflicting signals (HIGH urgency + LOW confidence) | Item 12 |
| F-12 | SHOULD | Classification filter case mismatch | Item 9 |
| F-13 | SHOULD | Past decisions from same sender not surfaced | Items 8, 17, 26 |
| F-14 | SHOULD | Undo affordance missing | Item 32 |
| F-15 | NICE | Quick approve from list for high-confidence items | Item 41 |
| F-16 | NICE | Queue virtualization at 200+ items | Backlog |
| F-17 | NICE | Broker/sender sort (needs backend change) | Backlog |

**Drop rate: 0%** — All 17 findings mapped. F-16 and F-17 in backlog (explained below).

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ▼
Phase 1 (Schema Unification & Data Pipeline)
    │
    ├──────────────────────────┐
    ▼                          ▼
Phase 2 (Triage Components)   Phase 5 (Agent Deployment Package)
    │
    ▼
Phase 3 (Page Integration & Decision Safety)
    │
    ▼
Phase 4 (Queue Enhancement & Rapid Triage)
    │
    ▼
Phase 6 (Validation & Bookkeeping)
```

Phase 2 and Phase 5 can run in parallel after Phase 1.

---

## Drift Items (Out of Scope — Backend Changes Required)

Items identified by TriPass that require backend modifications. Tracked for follow-up.

| ID | Description | Severity | Source |
|----|-------------|----------|--------|
| DRIFT-1 | Backend `valid_sorts` needs `broker_name`/`sender` for sort-by-broker feature | LOW | TriPass F-17 |
| DRIFT-2 | Backend classification filter SQL needs `UPPER()` for case-insensitive matching | MEDIUM (mitigated by Item 9 frontend normalization) | TriPass F-12 |
| DRIFT-3 | Sender intelligence endpoint needs rate limiting | LOW (mitigated by Item 27 debounce) | TriPass |
| DRIFT-4 | Backend list query doesn't select `routing_conflict`/`conflicting_deal_ids` (detail does) | LOW — conflict flow works from detail data | TriPass F-1 |
| DRIFT-5 | Tab-based detail panel organization (architectural suggestion) | LOW — scrollable panel works | TriPass |

---

## Backlog (Post-Mission)

| Item | Priority | Description | Status |
|------|----------|-------------|--------|
| Queue virtualization | MEDIUM | F-16: No virtualization at 200+ items. Use `@tanstack/react-virtual` when queue regularly exceeds 100. | BACKLOGGED |
| Broker/sender sort | LOW | F-17: Requires backend `valid_sorts` expansion (DRIFT-1). Frontend options trivial after backend change. | BACKLOGGED (needs backend) |
| Agent populates extraction_evidence | HIGH | Agent relay of Phase 5 deployment package → LangSmith agent starts injecting rich nested evidence. Dashboard ready to render it immediately. | PENDING RELAY |
| Self-delegate pattern | MEDIUM | Agent needs `zakops_create_action` before `zakops_report_task_result` for self-initiated runs (500 on poll_run_ IDs). | OPEN (from Integration Roadmap) |
| Domain Knowledge Extraction | LOW | Extract classification signals, vendor patterns, broker heuristics from LangSmith export. | BACKLOGGED (from Integration Roadmap) |

---

## Discarded Items (TriPass)

Items investigated but excluded with documented reasons.

| ID | Description | Reason |
|----|-------------|--------|
| DISC-1 | Legacy `links.groups` detail endpoint claim | Unverified evidence — detail query doesn't select `links`. General principle preserved in F-7. |
| DISC-2 | Mission source path stale reference | Documentation hygiene, not a UX finding. |
| DISC-3 | Design-system rulebook amendments as standalone deliverable | Governance updates outside mission scope. Enforcement included within each finding. |

---

## Files Reference

### Files to Modify

| File | Phase | Changes |
|------|-------|---------|
| `apps/dashboard/src/lib/api.ts` | P1 | ExtractionEvidenceSchema, SenderIntelligenceSchema, TriageFeedbackSchema, getSenderIntelligence(), getTriageFeedback(), unify getQuarantinePreview, add routing/provenance fields, classification normalization |
| `apps/dashboard/src/app/quarantine/page.tsx` | P1,P3,P4 | Fix types (P1). Integrate TriageIntelPanel, AbortController, sender intel/feedback fetches, undo toast, approve dialog fix, remove old helpers, header enhance (P3). List items + keyboard shortcuts + quick approve (P4). |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `apps/dashboard/src/components/quarantine/format-utils.ts` | P2 | formatCurrency, formatConfidence |
| `apps/dashboard/src/components/quarantine/TriageSummaryCard.tsx` | P2 | AI summary + confidence + conflicting signals |
| `apps/dashboard/src/components/quarantine/DealSignalsCard.tsx` | P2 | Company, broker, financials, stage |
| `apps/dashboard/src/components/quarantine/ClassificationReasoningCard.tsx` | P2 | Reasons + urgency signals |
| `apps/dashboard/src/components/quarantine/MaterialsAndLinksCard.tsx` | P2 | Typed links + legacy formats + attachments |
| `apps/dashboard/src/components/quarantine/EntitiesCard.tsx` | P2 | Companies + people with evidence |
| `apps/dashboard/src/components/quarantine/SenderIntelCard.tsx` | P2 | Sender reputation + past decisions |
| `apps/dashboard/src/components/quarantine/EmailBodyCard.tsx` | P2 | Expandable email body |
| `apps/dashboard/src/components/quarantine/ProvenanceFooter.tsx` | P2 | Agent trace link + version metadata |
| `apps/dashboard/src/components/quarantine/TriageIntelPanel.tsx` | P2 | Orchestrator component |
| `bookkeeping/docs/EXTRACTION_EVIDENCE_SCHEMA.md` | P5 | Schema documentation |
| `bookkeeping/docs/AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md` | P5 | Agent deployment package |

### Files to Read (Sources of Truth)

| File | Purpose |
|------|---------|
| `apps/dashboard/src/app/deals/[id]/page.tsx` | InfoGrid, Card, Collapsible, Promise.allSettled patterns |
| `apps/dashboard/src/components/actions/action-card.tsx` | Card + status badge patterns |
| `apps/dashboard/src/components/quarantine/ConfidenceIndicator.tsx` | Reuse for confidence displays |
| `.claude/rules/design-system.md` | Surface 9 compliance |
| `apps/backend/src/api/orchestration/main.py` | QuarantineResponse (L247-286), sender-intelligence (L2039-2148), feedback (L1753-1762) |

---

## Key Artifact Paths

| Artifact | Path |
|----------|------|
| This roadmap | `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md` |
| Mission prompt | `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md` |
| TriPass run | `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/` |
| TriPass final master | `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/FINAL_MASTER.md` |
| TriPass mission | `/home/zaks/bookkeeping/docs/_tripass_missions/QI-ADVERSARIAL-REVIEW-001.md` |
| Integration Roadmap | `/home/zaks/bookkeeping/docs/INTEGRATION-ROADMAP.md` |
| Integration Spec v1.0 | `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` |
| Change log | `/home/zaks/bookkeeping/CHANGES.md` |

---

## Statistics

| Metric | Count |
|--------|-------|
| Mission prompt tasks | 38 |
| TriPass findings | 17 (7 MUST + 7 SHOULD + 3 NICE) |
| TriPass drift items | 5 |
| TriPass discarded items | 3 |
| **Roadmap items (merged)** | **52** |
| Mission AC | 13 |
| TriPass gates | 11 |
| **Total acceptance gates** | **24** |
| Files to modify | 2 |
| Files to create | 12 |
| Items in backlog | 5 |
| **Drop rate** | **0%** |

---

*Last Updated: 2026-02-18*
