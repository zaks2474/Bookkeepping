# Pass 2 Cross-Review — CLAUDE
## Run: TP-20260218-095911 | Mode: design
## Generated: 2026-02-18T10:09:06Z

---

## DUPLICATES (High Confidence)

Items found by 2+ agents. Merged into single entries with attribution.

### D-1: Preview Parse Failure Returns Null — Operator Sees "Preview not found" on Schema Mismatch

**Reported by:** Agent A (Finding 10), Agent C (Finding 1)
**Consensus root cause:** `getQuarantinePreview()` at `api.ts:949-962` uses `QuarantinePreviewSchema.safeParse(data)` and returns `null` on any parse failure. The caller at `page.tsx:256-258` then shows the generic "Preview not found" error. The actual cause is a Zod validation error (backend returned data, but it didn't match the schema). Both agents identify the `attachments` field shape mismatch as a concrete trigger: `QuarantinePreviewSchema` defines `attachments: z.record(z.any())` (object) at `api.ts:241`, while the backend's `QuarantineResponse` defines `attachments: list | None` at `main.py:282`.
**Consensus fix:** Use `.passthrough()` parsing to degrade gracefully rather than returning null. Show partial data with a drift indicator instead of a blank screen. Agent A proposes a `schemaDrift` flag on the return type; Agent C proposes a contract-check test comparing frontend/backend fields. Both are complementary.
**Evidence verified:** YES
- `api.ts:241`: `attachments: z.record(z.any()).nullable().optional()` — confirmed, expects object
- `main.py:282`: `attachments: list | None = None` — confirmed, returns list
- `api.ts:952-955`: `safeParse` returns null on failure — confirmed
- `page.tsx:258`: Sets `previewError` to `'Preview not found'` — confirmed

---

### D-2: Keyboard Shortcuts Missing — 3-Second Decision Target Requires Keyboard-First UX

**Reported by:** Agent A (Finding 2), Agent C (Finding 3)
**Consensus root cause:** The entire `page.tsx` has zero keyboard event handlers. Every action (approve, reject, escalate, delegate) requires mouse clicks. The approve flow is a minimum 4-click path: click item -> read panel -> click Approve -> confirm dialog. Both agents cite Linear/Superhuman/Gmail as industry standards for keyboard-first triage.
**Consensus fix:** Add `useEffect` keyboard handler at page level with `j/k` for navigation, `a` for approve, `r` for reject, `e` for escalate, `d` for delegate, `Escape` to close dialogs. Guard shortcuts: only fire when no dialog is open and no input/textarea has focus. Agent C additionally proposes row-level quick actions and undo affordance.
**Evidence verified:** YES
- `page.tsx` full file: Confirmed zero `addEventListener('keydown')` or keyboard `useEffect` handlers
- `page.tsx:904-918`: All action buttons are click-only, confirmed `disabled={!preview || working}`
- Agent C's reference to undo API at `api.ts:1139` confirmed — `undoQuarantineApproval` exists at line 1139

---

### D-3: Async Race Condition — Rapid Item Clicking Fires Stale Concurrent Requests

**Reported by:** Agent A (Finding 3), Agent C (Finding 4)
**Consensus root cause:** Preview fetch at `page.tsx:268-273` fires on every `selectedId` change with no `AbortController` or cancellation. The mission adds a second `useEffect` for sender intelligence, compounding the issue. Rapidly clicking through N items fires N preview + N sender intel requests; only the last matters.
**Consensus fix:** Both agents agree on `AbortController` stored in a ref, aborting previous request on each new selection. Agent A additionally proposes 300ms debounce specifically for sender intelligence (supplementary data). Agent C proposes request tokens as an alternative.
**Evidence verified:** YES
- `page.tsx:268-273`: `useEffect` fires on `selectedId` with no abort — confirmed
- No `AbortController` anywhere in the file — confirmed by full file read
- `loadPreview` at line 251-266 has no signal/abort parameter — confirmed

---

### D-4: LangSmith Provenance Fields Missing from Dashboard Schema

**Reported by:** Agent A (Finding 4), Agent C (Finding 6)
**Consensus root cause:** Backend `QuarantineResponse` at `main.py:274-278` returns `langsmith_run_id`, `langsmith_trace_url`, `tool_version`, `prompt_version`. Both list (`main.py:1723-1727`) and detail (`main.py:2179-2182`) SQL queries select these fields. Dashboard `QuarantineItemSchema` at `api.ts:175-213` omits them. Zod strips unknown keys by default, silently dropping the data.
**Consensus fix:** Add the 4 fields to `QuarantineItemSchema`. Render a provenance section with "View agent trace" link when `langsmith_trace_url` exists, and show `tool_version`/`prompt_version` as muted metadata.
**Evidence verified:** YES
- `main.py:274-278`: All 4 provenance fields present in `QuarantineResponse` — confirmed
- `main.py:1723-1727`: List query selects them — confirmed
- `main.py:2179-2182`: Detail query selects them — confirmed
- `api.ts:175-213`: None of the 4 fields present in `QuarantineItemSchema` — confirmed

---

### D-5: Confidence UX Lacks Trust Differentiation — No Visual Weight Variation by Confidence Level

**Reported by:** Agent A (Finding 5), Agent C (Finding 5)
**Consensus root cause:** The UI shows confidence as a standalone indicator (dot in list at `page.tsx:804-806`, segmented bar in detail at `page.tsx:921-925`) but doesn't change the visual weight or prominence of surrounding content based on confidence level. A 0.95 and 0.35 confidence item look identical aside from the indicator itself. Agent A focuses on graduated visual borders/tinting; Agent C frames this as a "Signal Health" bar with completeness ratio.
**Consensus fix:** Agent A proposes left-border tinting by confidence band on the detail Card, and upgrading `size='sm'` to `size='md'` for low-confidence items in the list. Agent C proposes a compact "Signal Health" bar with completeness, confidence band, and contradiction badges. Both are complementary — the visual weight approach (Agent A) addresses the immediate UX gap; the Signal Health bar (Agent C) adds richer context.
**Evidence verified:** YES
- `page.tsx:804-806`: List item uses `size='sm'` (2px dot) — confirmed
- `page.tsx:921-925`: Detail uses `size='lg'` (segmented bar) — confirmed
- `ConfidenceIndicator.tsx:11-15`: `getLevel` computes high/medium/low from score thresholds — confirmed

---

### D-6: Conflicting Signals (High Urgency + Low Confidence) Not Surfaced

**Reported by:** Agent A (Finding 8), Agent C (Finding 5, subsection on contradictions)
**Consensus root cause:** Urgency badges at `page.tsx:816-820` and confidence indicators at `page.tsx:921-924` are rendered independently with no visual relationship. HIGH urgency + LOW confidence creates cognitive dissonance ("act fast on something uncertain") but the UI doesn't flag or resolve this. Agent A proposes an explicit "Signal Conflict" conditional render; Agent C bundles it into their "Signal Health" bar as contradiction badges.
**Consensus fix:** Add conditional warning when `urgency === 'HIGH' && confidence < 0.5` — inline amber alert in the summary area. Both agents agree this is a simple conditional render requiring no new component.
**Evidence verified:** YES
- `page.tsx:816-820`: Urgency badge with `destructive` variant for 'high' — confirmed
- `page.tsx:921-924`: Standalone `ConfidenceIndicator` — confirmed
- Both `urgency` and `confidence` are available on `QuarantineItem` (list data) — confirmed via `api.ts:193-194`

---

### D-7: Quick Approve / Row-Level Actions Missing for High-Confidence Items

**Reported by:** Agent A (Finding 9), Agent C (Finding 3, row quick-actions subsection)
**Consensus root cause:** The mission enhances list items (Phase 4) with more data display but no inline actions. For high-confidence, known-broker items, the operator must still go through the full 5-step flow. Agent A proposes a conditional "Quick Approve" icon button on list items meeting `confidence >= 0.85 && classification === 'DEAL_SIGNAL' && is_broker`. Agent C proposes general row quick actions.
**Consensus fix:** Add a "Quick Approve" icon button to list items meeting confidence/classification/broker thresholds. Both agree this is a SHOULD-ADD, not a MUST-ADD.
**Evidence verified:** YES
- `page.tsx:777-854`: List items render data but no action buttons except delete — confirmed
- `page.tsx:838-849`: Only the delete button exists in list items — confirmed

---

### D-8: Queue Performance — No Virtualization for 200+ Item Lists

**Reported by:** Agent A (Finding 11), Agent C (Finding 9)
**Consensus root cause:** `page.tsx:196-204` requests `limit: 200`. All items are rendered via `.map()` at `page.tsx:777-854` inside a `ScrollArea` with no virtualization. Agent A estimates ~3,000 DOM nodes at 200 items. Both agree the mission's Phase 4 additions will increase per-item DOM count further.
**Consensus fix:** Both rate this as NICE-TO-HAVE. Agent A proposes `@tanstack/react-virtual`; Agent C proposes pagination via offset + "Load more" button and notes the backend already supports offset parameter (`main.py:1614`).
**Evidence verified:** YES
- `page.tsx:197`: `limit: 200` — confirmed
- `page.tsx:777`: `.map()` over all items — confirmed
- `main.py:1613-1614`: Backend supports `limit` up to 200 and `offset` — confirmed

---

## CONFLICTS

Items where agents disagree on root cause or fix approach.

### C-1: Schema Unification Target — `QuarantineItemSchema` vs Detail-Specific Schema

**Agent A position:** Unify `getQuarantinePreview()` to return `QuarantineItem` (the existing list schema), then add missing fields (routing_conflict, conflicting_deal_ids) to `QuarantineItemSchema`. Effectively, one schema for both list and detail.
**Agent C position (Finding 2):** Creating a separate detail schema structurally aligned to `QuarantineResponse` that includes routing_conflict and conflicting_deal_ids. Agent C specifically warns that switching to `QuarantineItemSchema` without adding routing_conflict fields will break the "Approve Into Deal" thread-conflict flow at `page.tsx:958-996`.
**Evidence comparison:**
- Agent C is correct: `QuarantineItemSchema` at `api.ts:175-213` does NOT include `routing_conflict` or `conflicting_deal_ids`. It only has `routing_reason` (line 212).
- The detail panel reads `preview.routing_conflict` and `preview.conflicting_deal_ids` at lines 958, 970 — these come from `QuarantinePreviewSchema` which defines them at `api.ts:253-254`.
- The detail endpoint at `main.py:2187-2188` returns these from `raw_content` JSONB, while the list endpoint does NOT select them (confirmed at `main.py:1698-1730` — no routing_conflict or conflicting_deal_ids in the list query).
**Recommended resolution:** Agent C is correct — this is a MUST-FIX before Phase 1. Add `routing_conflict: z.boolean().nullable().optional()` and `conflicting_deal_ids: z.array(z.string()).nullable().optional()` to `QuarantineItemSchema` before removing `QuarantinePreviewSchema`. This is actually a supplement to Agent A's approach (one unified schema), not a contradiction — Agent A simply missed these two fields.

---

### C-2: Empty `extraction_evidence` Handling — Flat Legacy vs Nested New Format

**Agent A position (Finding 6):** Three distinct visual states (null, `{}`, partially populated). Proposes `legacyEvidence: z.record(z.string()).optional()` catch-all for flat key-value evidence that doesn't match the new nested schema. Each card should accept both nested `extraction_evidence` and flat `QuarantineItem` fields, preferring nested when available.
**Agent C position:** Does not explicitly address the flat-to-nested schema transition. Focuses on contract parity and `.passthrough()` parsing.
**Evidence comparison:**
- Agent A cites bridge at `server.py:852` which passes `extraction_evidence: Optional[dict] = None` — confirmed, this is an unstructured dict.
- The mission's `ExtractionEvidenceSchema` proposes nested sub-objects (`financials`, `broker`, `entities`) but no existing items in the database use this format.
- Current flat format is `{ field_name: "evidence_string" }` based on the injection tool's generic `dict` type.
**Recommended resolution:** Agent A's analysis is more thorough here. The dual-source fallback pattern (nested evidence first, flat fields fallback) is essential for the transition period. This should be explicitly called out in the mission's Phase 2 component contract.

---

## UNIQUE FINDINGS

Items found by only one agent. Verified for validity.

### U-1: Approve Dialog Reads from Stale `preview.extracted_fields` (from Agent A, Finding 1)

**Verification:** CONFIRMED
**Evidence check:**
- `page.tsx:1155-1174`: Approve dialog editable fields read from `preview.extracted_fields` — confirmed at lines 1156-1158 and 1160
- Keys used: `company_guess`, `broker_email`, `asking_price` — confirmed at lines 1156-1158
- After schema unification, `preview` becomes `QuarantineItem` which has `company_name` (not `company_guess`) and `broker_name` (not `broker_email`) — confirmed via `api.ts:197-198`
- The corrections dict would send `{ company_guess: "..." }` to the backend, but the backend column is `company_name` — this is a silent data loss bug
**Should include in final:** YES — This is a MUST-FIX. The approve dialog is the critical decision action, and broken field mapping means corrections are silently ignored.

---

### U-2: `renderLinkGroups` and `renderAttachments` Use Old Preview Schema (from Agent A, Finding 7)

**Verification:** CONFIRMED
**Evidence check:**
- `page.tsx:1420-1488`: `renderLinkGroups` reads `(preview.links as Record<string, unknown>)?.groups` — confirmed at line 1421. This expects `links` as an object with `.groups` property.
- `page.tsx:1491-1515`: `renderAttachments` reads `(preview.attachments as Record<string, unknown>)?.items` — confirmed at line 1492. This expects `attachments` as an object with `.items` property.
- After unification, `links` from `QuarantineItemSchema` is typed as `z.array(z.record(z.any()))` (flat array, not grouped object) at `api.ts:204`.
- `attachments` from `QuarantineResponse` is `list | None` at `main.py:282` — a list, not an object with `.items`.
- Both render helpers will fail silently (produce "No links detected" / "No attachments") for items whose data comes from the new schema shape.
**Should include in final:** YES — MUST-ADD. Legacy rendering support must be preserved via fallback renderers during the transition.

---

### U-3: Sender Intelligence Fetch Needs Null-Safe Email Extraction (from Agent A, Finding 12)

**Verification:** CONFIRMED
**Evidence check:**
- Backend endpoint at `main.py:2041`: `sender_email: str = Query(...)` — required parameter, confirmed
- `QuarantineItemSchema` at `api.ts:182`: `sender: z.string().nullable().optional()` — can be null, confirmed
- `QuarantineItemSchema` at `api.ts:186`: `from: z.string().nullable().optional()` — alternative field, confirmed
- `page.tsx:873`: Display fallback chain `selectedItem.sender_name || selectedItem.sender || selectedItem.from || 'Unknown'` — confirmed, but this is display-only
- The mission's sender intelligence fetch doesn't specify using this fallback chain for the API call
**Should include in final:** YES — MUST-ADD. Without the `sender || from` fallback guard, legacy items with `sender: null` would either fire a 400 error or skip sender intel entirely.

---

### U-4: Batch Triage — Broker/Sender Sort Options (from Agent A, Finding 13)

**Verification:** PARTIALLY CONFIRMED
**Evidence check:**
- `page.tsx:98-103`: `SORT_OPTIONS` only has `received_at`, `confidence`, `urgency`, `created_at` — confirmed
- `main.py:1674`: `valid_sorts = {"received_at", "urgency", "confidence", "created_at"}` — confirmed, `broker_name` and `sender` are NOT in the valid set
- Agent A claims "The backend list endpoint... already selects `broker_name` and `sender`, so sorting by them should work without backend changes" — this is INCORRECT. The backend's `valid_sorts` whitelist at line 1674-1675 would reject `broker_name` and `sender`, falling through to the default sort order. Adding broker/sender sort requires a backend change (expanding `valid_sorts`).
**Should include in final:** YES (SHOULD-ADD) — but with correction: this requires a backend change to add `broker_name`/`sender` to `valid_sorts`, not just a frontend change. Agent A's claim of "2-line frontend change + verification" understates the work.

---

### U-5: Routing Conflict Fields in Unified Schema (from Agent C, Finding 2)

**Verification:** CONFIRMED (see also C-1 above)
**Evidence check:**
- `page.tsx:958-996`: Thread conflict alert reads `preview.routing_conflict` and `preview.conflicting_deal_ids` — confirmed
- `QuarantinePreviewSchema` at `api.ts:253-254`: Has `routing_conflict` and `conflicting_deal_ids` — confirmed
- `QuarantineItemSchema` at `api.ts:175-213`: Does NOT have these fields — confirmed, only `routing_reason` at line 212
- Detail endpoint at `main.py:2187-2188`: Returns these from `raw_content` JSONB — confirmed
- List endpoint at `main.py:1698-1730`: Does NOT select them — confirmed
**Should include in final:** YES — MUST-FIX before Phase 1. This is a regression blocker for schema unification.

---

### U-6: Classification Vocabulary Drift Between Agent and UI Filters (from Agent C, Finding 7)

**Verification:** PARTIALLY CONFIRMED
**Evidence check:**
- `page.tsx:86-90`: `CLASSIFICATION_OPTIONS` uses uppercase: `DEAL_SIGNAL`, `UNCERTAIN`, `JUNK` — confirmed
- `main.py:1631`: Filter uses exact match: `COALESCE(q.raw_content->>'classification', 'unknown') = ${param_idx}` — confirmed
- Agent bridge at `server.py:877`: classification parameter documented as lowercase: `deal_signal, operational, newsletter, spam` — confirmed
- However, the bridge passes the classification value directly to the backend which stores it. The backend filter reads from `raw_content->>'classification'` — what the agent writes is what gets compared.
- The UI filters send `DEAL_SIGNAL` (uppercase). If the agent writes `deal_signal` (lowercase), the filter `DEAL_SIGNAL` won't match — the comparison is case-sensitive in PostgreSQL.
- Agent C references `/tmp/langsmith-export/canonical_output_schema.json` which could not be independently verified (temporary file from a prior session).
**Should include in final:** YES (SHOULD-ADD) — The mismatch between uppercase UI filter values and lowercase agent classification values is a real risk. The backend does NOT normalize case in the classification filter. A `LOWER()` or `UPPER()` normalization in the SQL filter, or case-insensitive comparison, would fix this. Alternatively, normalize in the frontend API boundary as Agent C suggests.

---

### U-7: Comparison Workflow — Past Decisions from Same Sender (from Agent C, Finding 8)

**Verification:** CONFIRMED
**Evidence check:**
- Backend feedback endpoint at `main.py:1753-1762`: `GET /api/quarantine/feedback` exists with `sender_email` parameter, returns approval/rejection history and corrections — confirmed
- Dashboard has no component consuming this endpoint — confirmed (no reference to `/api/quarantine/feedback` in `page.tsx` or `api.ts` quarantine section)
- This is a genuine gap: the backend already provides historical decision data per-sender, but the dashboard doesn't surface it.
**Should include in final:** YES (SHOULD-ADD) — Backend support already exists. A collapsible "Past Decisions" card would help operators make consistent decisions. Minimal frontend work (new API call + simple table component).

---

### U-8: Undo After Action (from Agent C, Finding 3, subsection)

**Verification:** CONFIRMED
**Evidence check:**
- Backend endpoint at `main.py:3076`: `POST /api/quarantine/{item_id}/undo-approve` — confirmed
- Dashboard API wrapper at `api.ts:1139-1149`: `undoQuarantineApproval()` — confirmed
- Quarantine page at `page.tsx`: No undo affordance in the UI — confirmed, no reference to `undoQuarantineApproval` import or call
**Should include in final:** YES (SHOULD-ADD) — The backend API and frontend wrapper both exist. The only gap is a UI affordance (e.g., toast with "Undo" action after approve/reject). Low-effort, high-value for preventing costly mistakes.

---

## DRIFT FLAGS

Findings that fall outside the declared mission scope.

### DRIFT-1: Broker/Sender Sort Requires Backend Change (from Agent A, Finding 13)

**Why out of scope:** The mission explicitly states "Do NOT propose backend changes." Adding `broker_name` and `sender` to `valid_sorts` at `main.py:1674` is a backend change.
**Severity if ignored:** LOW — The sort options still work for existing fields. This is a UX enhancement, not a regression. Can be tracked as a follow-up backend task outside the mission.

### DRIFT-2: Classification Filter Case Normalization (from Agent C, Finding 7)

**Why out of scope:** Fixing the exact-match filter at `main.py:1631` to use `UPPER()` or `ILIKE` is a backend SQL change. The frontend can mitigate by sending lowercase values, but the root fix is backend.
**Severity if ignored:** MEDIUM — If the agent starts injecting lowercase classifications (which the bridge documentation implies: `deal_signal, operational, newsletter, spam`), the existing uppercase UI filters (`DEAL_SIGNAL`, `UNCERTAIN`, `JUNK`) will silently fail to match. This could result in "empty queue" when items exist but are classified differently. However, this may already be normalized elsewhere in the ingestion pipeline — needs investigation.

### DRIFT-3: Sender Intelligence Endpoint Rate Limiting (from Agent A, AO-3)

**Why out of scope:** Adding rate limiting to `GET /api/quarantine/sender-intelligence` is a backend infrastructure concern. Agent A correctly labels this as out of scope. The frontend debounce mitigates the symptom.
**Severity if ignored:** LOW — Frontend debounce (from D-3) adequately mitigates this.

### DRIFT-4: Queue Virtualization Beyond Current Scope (from Agent A, Finding 11; Agent C, Finding 9)

**Why out of scope:** Both agents rate this NICE-TO-HAVE. The current 200-item limit is manageable. Virtualization or pagination is a performance optimization beyond the mission's stated "decision intelligence" focus.
**Severity if ignored:** LOW — Only becomes an issue if queue consistently exceeds 100+ items.

---

## SUMMARY

- **Duplicates:** 8 (D-1 through D-8)
- **Conflicts:** 2 (C-1: schema unification target; C-2: flat vs nested evidence handling)
- **Unique valid findings:** 8 (U-1 through U-8)
- **Drift items:** 4 (DRIFT-1 through DRIFT-4)

### Overall Assessment

The two reports show strong convergence on the critical issues (8 duplicates), which indicates high confidence in these findings. Agent B (Gemini) produced no output, so cross-validation is limited to two perspectives.

**Critical gap identified in cross-review:** Agent C's Finding 2 (routing_conflict fields missing from `QuarantineItemSchema`) is a genuine regression blocker that Agent A missed entirely. If schema unification proceeds without adding `routing_conflict` and `conflicting_deal_ids` to the unified schema, the thread-conflict "Approve Into Deal" flow at `page.tsx:958-996` breaks silently. This should be elevated to the #1 MUST-FIX.

**Revised MUST-ADD priority (before/during execution):**

| Priority | Finding | Source | Rationale |
|----------|---------|--------|-----------|
| 1 | Routing conflict fields in unified schema | U-5 / C-1 | Regression blocker — thread-conflict UX breaks |
| 2 | Approve dialog field mapping | U-1 | Regression blocker — corrections silently ignored |
| 3 | Empty extraction_evidence dual-source fallback | C-2 | Every existing item shows empty cards for weeks |
| 4 | Legacy link/attachment format preservation | U-2 | Existing data stops rendering |
| 5 | Preview parse graceful degradation | D-1 | "Preview not found" on schema drift |
| 6 | Provenance fields in Zod schema | D-4 | Zero-cost — backend already returns them |
| 7 | Sender email null-safety | U-3 | 400 errors on legacy items |
| 8 | AbortController for stale fetches | D-3 | Wrong-item data display during rapid triage |

**Revised SHOULD-ADD (during execution):**

| Priority | Finding | Source |
|----------|---------|--------|
| 9 | Keyboard shortcuts (j/k/a/r) | D-2 |
| 10 | Graduated confidence visual weight | D-5 |
| 11 | Conflicting signal indicator | D-6 |
| 12 | Classification case normalization (frontend side) | U-6 |
| 13 | Past decisions from same sender | U-7 |
| 14 | Undo affordance in UI | U-8 |

**NICE-TO-HAVE (backlog):**

| Priority | Finding | Source |
|----------|---------|--------|
| 15 | Quick approve from list | D-7 |
| 16 | List virtualization/pagination | D-8 |
| 17 | Broker/sender sort (needs backend change) | U-4 / DRIFT-1 |

### Confidence in Findings

- **D-1 through D-8 (duplicates):** HIGH confidence — independently identified by both agents with consistent evidence
- **U-1, U-2, U-3, U-5:** HIGH confidence — evidence verified against source files
- **U-4, U-6:** MEDIUM confidence — partially confirmed, Agent A's backend-change claim is incorrect, Agent C's classification values need runtime verification
- **U-7, U-8:** HIGH confidence — backend support confirmed to exist, dashboard gap confirmed

### Key Risk

The single biggest risk to mission success is the **transition period**: after Phase 1 schema unification, the new nested `ExtractionEvidenceSchema` components will show empty states for ALL existing items (which have either null or flat-format `extraction_evidence`). This persists until the agent deployment package updates the agent to produce nested evidence. Agent A's dual-source fallback pattern (Finding 6 / C-2) is essential to prevent a multi-week "blank cards" experience.
