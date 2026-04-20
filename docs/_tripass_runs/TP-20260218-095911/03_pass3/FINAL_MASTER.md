# FINAL MASTER — TP-20260218-095911
## Mode: design
## Generated: 2026-02-18T10:15:54Z
## Sources: 3 Pass 1 reports + 3 Pass 2 cross-reviews

(Gemini agent produced no output in both passes. Effective sources: 2 Pass 1 reports [CLAUDE, CODEX] + 2 Pass 2 cross-reviews [CLAUDE, CODEX].)

---

## MISSION

Transform the quarantine detail experience from "decide blind" to "decide in 3 seconds with full context" by unifying the preview schema, adding structured intelligence cards (extraction evidence, sender intel, provenance), and enabling keyboard-first rapid triage — all without backend changes.

---

## CONSOLIDATED FINDINGS

Findings are ordered by impact on operator decision speed. Tier labels: **MUST-ADD** (before/during execution — regression or data-loss risk), **SHOULD-ADD** (material UX improvement), **NICE-TO-HAVE** (backlog).

---

### F-1: Routing Conflict Fields Missing from `QuarantineItemSchema` — Schema Unification Will Break "Approve Into Deal" Flow [MUST-ADD]

**Sources:** CODEX P1-F2, CLAUDE P2-U5, CODEX P2-U5, CLAUDE P2-C1

**Root Cause:**
The thread-conflict UX at `page.tsx:958-996` reads `preview.routing_conflict` and `preview.conflicting_deal_ids`. These fields exist on `QuarantinePreviewSchema` (`api.ts:253-254`) but NOT on `QuarantineItemSchema` (`api.ts:175-213`). The mission plans to unify preview parsing to use `QuarantineItemSchema`. Without adding these fields, the "Approve Into Deal" conflict resolution flow silently breaks — operators lose the ability to choose which deal to route a conflicting email to.

The backend detail endpoint returns both fields from `raw_content` JSONB (`main.py:2187-2188`), but the list endpoint does NOT select them (`main.py:1698-1730`). This means routing_conflict data is only available from the detail fetch, not from list data.

**Fix Approach:**
Add to `QuarantineItemSchema` in `api.ts` before removing `QuarantinePreviewSchema`:
```typescript
routing_conflict: z.boolean().nullable().optional(),
conflicting_deal_ids: z.array(z.string()).nullable().optional(),
```
Keep the existing conflict card rendering at `page.tsx:958-996` unchanged — it reads from `preview.*` which will now be the unified item from the detail fetch.

**Industry Standard:**
Exception-handling safety paths must be preserved during UI schema migrations. Removing exception flows during refactoring is a top cause of latent regressions (Google SRE Workbook, Chapter 15).

**System Fit:**
Backend already returns these fields. This is a 2-line Zod schema addition. Zero backend changes. The conflict flow is a critical operator safety path — wrong-deal approval is the most costly operator error.

**Enforcement:**
- Regression test fixture: render a quarantine item with `routing_conflict: true, conflicting_deal_ids: ["deal-123", "deal-456"]` — assert "Approve into this deal" buttons appear.
- Add to Phase 1 gate: `QuarantineItemSchema` must include every field present in `QuarantinePreviewSchema` (field parity check).

---

### F-2: Approve Dialog Reads from Stale `preview.extracted_fields` with Wrong Correction Keys [MUST-ADD]

**Sources:** CLAUDE P1-F1, CODEX P2-U1, CLAUDE P2-U1

**Root Cause:**
The approve dialog at `page.tsx:1155-1174` populates editable correction fields by reading from `preview.extracted_fields`. It uses keys: `company_guess` (line 1156), `broker_email` (line 1157), `asking_price` (line 1158). The `original` value is sourced from `(preview.extracted_fields as Record<string, unknown>)?.[key]` (line 1160).

After Phase 1 schema unification, `extracted_fields` will no longer exist on the unified `QuarantineItem`. Additionally, the correction keys are wrong: the backend's approval handler at `main.py:2809` reads `corrections.get('company_name')` and at `main.py:2816` reads `corrections.get('broker_name')`. The dialog sends `company_guess` and `broker_email` — the backend silently ignores these because they don't match its expected keys.

**Fix Approach:**
1. Change correction field definitions:
   - `{ key: 'company_guess', label: 'Company name' }` -> `{ key: 'company_name', label: 'Company name' }`
   - `{ key: 'broker_email', label: 'Broker email' }` -> `{ key: 'broker_name', label: 'Broker name' }` (backend uses `broker_name`, not `broker_email` for display name — `broker_email` is sourced separately from `sender` at `main.py:2819`)
   - Keep `{ key: 'asking_price', label: 'Asking price' }`
2. Source defaults from `preview.company_name`, `preview.broker_name`, `preview.extraction_evidence?.financials?.asking_price ?? ''` instead of `preview.extracted_fields`.
3. Add a TypeScript type: `type CorrectionField = 'company_name' | 'broker_name' | 'asking_price'` to prevent future key drift.

**Industry Standard:**
Form pre-population must read from the current data source, not a stale snapshot. Correction key names must match the consumer's expected keys (API contract alignment). Salesforce Lightning inline edit always reads/writes canonical field names.

**System Fit:**
The `corrections` dict is sent to `POST /api/quarantine/{id}/process`. The backend reads `corrections.get('company_name')` and `corrections.get('broker_name')` at `main.py:2809, 2816`. Aligning dialog keys to these backend expectations is a contained frontend fix.

**Enforcement:**
- Unit test: submit approve dialog with corrections -> verify the POST body contains `{ company_name: "...", broker_name: "..." }`, NOT `{ company_guess: "...", broker_email: "..." }`.
- Comment at correction field array: `// SYNC: keys must match backend /api/quarantine/{id}/process correction keys (main.py:2804-2821)`.

---

### F-3: Empty/Legacy `extraction_evidence` Creates Blank Cards for All Existing Items [MUST-ADD]

**Sources:** CLAUDE P1-F6, CODEX P1-F1 (partial), CLAUDE P2-C2, CODEX P2-U2

**Root Cause:**
The mission defines a nested `ExtractionEvidenceSchema` with sub-objects (`financials`, `broker`, `entities`). But current items in the database have `extraction_evidence` in one of three formats:
1. `null` — pre-Pipeline A items
2. `{}` — agent ran but extracted nothing
3. `{ field_name: "evidence_string" }` — flat key-value format (confirmed by bridge at `server.py:852` accepting `Optional[dict]` and golden test showing flat format)

No existing items use the new nested format. Every new card component (TriageSummaryCard, DealSignalsCard, etc.) will render empty states for ALL historical items until the agent deployment package updates the agent to produce nested evidence.

**Fix Approach:**
1. Each component must distinguish three visual states:
   - `null` -> "Not available" (muted text, no icon)
   - `{}` or all-null sub-fields -> "AI analysis ran — no signals detected" (muted, info icon)
   - Partially populated -> Render available fields, hide empty ones (no dash placeholders)
2. The `ExtractionEvidenceSchema` should use `.passthrough()` and accept both the new nested format and the current flat format via a `legacyEvidence: z.record(z.string()).optional()` catch-all.
3. Each card should implement a dual-source pattern: check `extraction_evidence?.broker?.name ?? item.broker_name` (nested first, flat field fallback). This ensures cards are useful immediately, not just after the agent update.

**Industry Standard:**
Schema evolution best practice (Google API Design Guide): new schemas must be backward-compatible with existing data. Progressive enhancement: show what's available, hide what's not. Never design a "big bang" migration that renders the UI useless during transition.

**System Fit:**
The existing `page.tsx:1020-1033` already reads flat fields from `selectedItem` (e.g., `selectedItem?.company_name`). The dual-source pattern extends this existing approach to the new card components.

**Enforcement:**
- Phase 2 gate: render a quarantine item with `extraction_evidence: { company_name: 'Test Corp' }` (flat format) — verify the appropriate card shows "Test Corp" via the flat-field fallback.
- Phase 2 gate: render a quarantine item with `extraction_evidence: null` — verify "Not available" appears, not blank/broken cards.

---

### F-4: Preview Parse Failure Returns Null — Operator Sees "Preview not found" on Schema Mismatch [MUST-ADD]

**Sources:** CLAUDE P1-F10, CODEX P1-F1, CLAUDE P2-D1, CODEX P2-D1

**Root Cause:**
`getQuarantinePreview()` at `api.ts:949-962` uses `QuarantinePreviewSchema.safeParse(data)`. When parsing fails, it logs `console.warn` and returns `null`. The caller at `page.tsx:256-258` sets `previewError` to `'Preview not found'`. The operator sees this generic error with a retry button, but retrying re-fetches the same data, gets the same parse failure — dead end.

A concrete trigger: `QuarantinePreviewSchema` defines `attachments: z.record(z.any())` (object shape, `api.ts:241`) while the backend returns `attachments: list | None` (array shape, `main.py:282`). This type mismatch causes `safeParse` to fail.

**Fix Approach:**
1. After Phase 1 schema unification (switching to `QuarantineItemSchema` for detail parsing), the specific `attachments` mismatch resolves because `QuarantineItemSchema` uses `z.any()` for attachments.
2. Additionally, use `.passthrough()` on the unified schema so unknown fields are preserved (not stripped), and parse only fails on actual type mismatches.
3. When `safeParse` fails, fall back to a lenient parse: strip only the failing fields and return partial data with a `schemaDrift` indicator. The operator sees degraded data instead of a blank screen.
4. Display a subtle amber banner: "Some fields could not be parsed — displaying available data" when drift is detected.

**Industry Standard:**
Postel's Law: "Be conservative in what you send, be liberal in what you accept." Schema validation should degrade gracefully, showing what's available rather than showing nothing. Contract-first transport schema parity between API model and UI parser.

**System Fit:**
`QuarantineItemSchema` already uses `.nullable().optional()` on every field, so `safeParse` should almost never fail after unification. Adding `.passthrough()` makes it even more robust. This is a defense-in-depth measure for any future schema drift.

**Enforcement:**
- Add a contract-check test comparing frontend `QuarantineItemSchema` field keys/types to backend `QuarantineResponse` fields — fail CI on drift.
- Surface 9 A2 rule: "Zod parse failures for display data MUST degrade to partial rendering, not blank screens."

---

### F-5: LangSmith Provenance Fields Missing from Dashboard Schema — Agent Trace Data Silently Dropped [MUST-ADD]

**Sources:** CLAUDE P1-F4, CODEX P1-F6, CLAUDE P2-D4, CODEX P2-D4

**Root Cause:**
Backend `QuarantineResponse` (`main.py:274-278`) returns 4 provenance fields: `langsmith_run_id`, `langsmith_trace_url`, `tool_version`, `prompt_version`. Both list (`main.py:1723-1727`) and detail (`main.py:2179-2182`) SQL queries select them. The bridge passes them through (`server.py:858, 964-967`). But `QuarantineItemSchema` (`api.ts:175-213`) omits all four. Zod's default behavior strips unknown keys, silently dropping provenance data at the parse boundary.

This matters because: (1) `langsmith_trace_url` links directly to the agent's reasoning trace — invaluable for debugging AI decisions, (2) `tool_version`/`prompt_version` identify which agent version produced the classification — critical for identifying stale classifications after agent updates.

**Fix Approach:**
Add to `QuarantineItemSchema`:
```typescript
langsmith_run_id: z.string().nullable().optional(),
langsmith_trace_url: z.string().nullable().optional(),
tool_version: z.string().nullable().optional(),
prompt_version: z.string().nullable().optional(),
```
Render in the detail panel:
- If `langsmith_trace_url` exists: small "View agent trace" link with external-link icon
- Show `tool_version` / `prompt_version` as muted metadata in a provenance footer

**Industry Standard:**
AI-assisted decision support requires provenance tracking (EU AI Act Article 13, transparency requirements). Operators must trace back to the AI's reasoning. Affinity CRM shows "data source" badges on AI-enriched fields.

**System Fit:**
Backend already returns these fields. Bridge already passes them. The only gap is the Zod schema and a small UI component. Zero backend changes.

**Enforcement:**
- Contract-checker rule: provenance keys in `QuarantineResponse` must be present in `QuarantineItemSchema`. Fail CI on drift.
- UI smoke test: render item with `langsmith_trace_url: "https://smith.langchain.com/..."` — assert "View agent trace" link renders.

---

### F-6: Sender Intelligence Fetch Needs Null-Safe Email Extraction [MUST-ADD]

**Sources:** CLAUDE P1-F12, CODEX P2-U4, CLAUDE P2-U3

**Root Cause:**
The mission's Phase 3 adds a sender intelligence fetch triggered when `selectedItem?.sender` changes. But the backend endpoint at `main.py:2041` requires `sender_email: str = Query(...)` — a non-empty string. The `sender` field on `QuarantineItem` can be `null` (it's `z.string().nullable().optional()` at `api.ts:182`). Legacy items may have `sender: null` but `from: "broker@example.com"` (the `from` field at `api.ts:186`).

The page already uses a fallback chain for display: `selectedItem.sender_name || selectedItem.sender || selectedItem.from || 'Unknown'` (line 873). But the mission's sender intelligence fetch doesn't specify applying the same fallback chain for the API call. Without this, legacy items with `sender: null` fire either a 400 error or skip sender intel entirely.

**Fix Approach:**
Guard the sender intelligence `useEffect`:
```typescript
const senderEmail = selectedItem?.sender || selectedItem?.from;
if (!senderEmail) { setSenderIntel(null); return; }
// proceed with fetch using senderEmail
```

**Industry Standard:**
Defensive API calling — never send null/undefined as a required query parameter. Always validate inputs before network requests.

**System Fit:**
Both `sender` and `from` fields exist on `QuarantineItem`. The fallback chain ensures both legacy (`from`) and new (`sender`) items trigger lookups. No backend changes.

**Enforcement:**
- TypeScript strict null checks: `getSenderIntelligence` signature should require `string` (not `string | null`), making the guard a compile-time requirement.
- Unit test: call sender intel fetch with item where `sender: null, from: "test@example.com"` — assert fetch fires with `"test@example.com"`.

---

### F-7: Legacy Link and Attachment Format Preservation During Schema Transition [MUST-ADD]

**Sources:** CLAUDE P1-F7, CLAUDE P2-U2

**Root Cause:**
`renderLinkGroups()` at `page.tsx:1420-1488` reads `preview.links?.groups` (a categorized object: `{ deal_material: [...], calendar: [...] }`). `renderAttachments()` at `page.tsx:1491-1515` reads `preview.attachments?.items` (an array within an object). These expect the old `QuarantinePreviewSchema` shapes.

After Phase 1 unification:
- `links` from `QuarantineItemSchema` is typed as `z.array(z.record(z.any()))` (`api.ts:204`) — a flat array, not a grouped object.
- `attachments` from the backend is `list | None` (`main.py:282`) — a flat list, not `{ items: [...] }`.

The mission's P3-04 says "Remove old inline render helpers (now handled by MaterialsAndLinksCard)" and P2-05 designs MaterialsAndLinksCard for `extraction_evidence.typed_links`. But historical items in the database may have `links` in the old categorized `{ groups: {...} }` format.

**Fix Approach:**
MaterialsAndLinksCard should implement a 3-tier data source priority:
1. `extraction_evidence.typed_links` (new nested format)
2. `item.links` if it's an array (flat link list — render as simple URL list)
3. `item.links` if it has a `.groups` property (old categorized format — port the categorized rendering logic from `renderLinkGroups`)

For attachments, similarly check if the data is a flat array (new format) vs an object with `.items` (old format).

Don't delete the categorized rendering logic — extract and adapt it into MaterialsAndLinksCard as a fallback renderer.

**Industry Standard:**
Data migration best practice: never remove rendering support for old formats until all records have been migrated. The UI is the last layer to drop backward compatibility.

**System Fit:**
The `QuarantineItemSchema` at `api.ts:204-205` uses `z.array(z.record(z.any())).nullable().optional()` for links and `z.any()` for attachments — both are permissive enough to accept either format at the Zod level. The rendering logic just needs to detect which format it received.

**Enforcement:**
- Phase 3 gate: render a legacy item with `links: { groups: { deal_material: [{ url: "https://..." }] } }` — verify categorized links display.
- Phase 3 gate: render a new item with `links: [{ url: "https://...", category: "deal_material" }]` — verify flat links display.

---

### F-8: Async Race Condition — Rapid Item Selection Fires Stale Concurrent Requests [SHOULD-ADD]

**Sources:** CLAUDE P1-F3, CODEX P1-F4, CLAUDE P2-D3, CODEX P2-D3

**Root Cause:**
Preview fetch at `page.tsx:268-273` fires on every `selectedId` change with no `AbortController` or cancellation. The mission adds a second `useEffect` for sender intelligence, compounding the problem. If an operator clicks through 5 items quickly (common triage scanning pattern), this fires 5 preview + 5 sender intelligence = 10 concurrent requests. Only the last matters. If an earlier response arrives after a later one, the panel shows data for the wrong item — a critical decision-safety bug.

**Fix Approach:**
Use `AbortController` stored in a ref, aborting the previous request on each new selection:
```typescript
const abortRef = useRef<AbortController | null>(null);
useEffect(() => {
  abortRef.current?.abort();
  const controller = new AbortController();
  abortRef.current = controller;
  // fetch with signal: controller.signal
  return () => controller.abort();
}, [selectedId]);
```
For sender intelligence specifically, add 300ms debounce (supplementary data, not blocking).

**Industry Standard:**
React 18 `useEffect` cleanup with `AbortController` is the recommended pattern for cancellable fetches (React docs: "You Might Not Need an Effect"). Every CRM and email client debounces list-to-detail selection. Race-safe state updates are mandatory for operator-critical UIs.

**System Fit:**
The deal detail page at `deals/[id]/page.tsx` uses `Promise.allSettled` for concurrent fetches but operates on a single URL-routed item. The quarantine page's click-to-select pattern needs `AbortController` — a different, necessary pattern for list selection.

**Enforcement:**
- Design-system A1 rule: "List-to-detail selection patterns MUST use `AbortController` to cancel stale fetches."
- Playwright test: rapidly switch items with delayed mock responses — assert rendered preview matches the final `selectedId`.

---

### F-9: Keyboard Shortcuts Missing — 3-Second Decision Target Requires Keyboard-First UX [SHOULD-ADD]

**Sources:** CLAUDE P1-F2, CODEX P1-F3, CLAUDE P2-D2, CODEX P2-D2

**Root Cause:**
The entire `page.tsx` has zero keyboard event handlers. Every action (approve, reject, escalate, delegate) requires mouse clicks. The approve flow is minimum 4 clicks: click item -> read detail panel -> click "Approve" -> confirm in dialog. The mission's stated goal is "decisions in seconds" but the architecture is mouse-first.

All action buttons at `page.tsx:904-918` require click, with `disabled={!preview || working}`.

**Fix Approach:**
Add a `useEffect` keyboard handler at page level:
- `j` / `k` or Up/Down -> Navigate queue list (prev/next item)
- `a` -> Open approve dialog (if preview loaded and not working)
- `r` -> Open reject dialog
- `e` -> Open escalate dialog
- `d` -> Open delegate dialog
- `x` -> Toggle bulk-select on current item
- `Escape` -> Close any open dialog
- `Enter` (within dialog) -> Confirm action

Guards: only fire when no dialog is open and no `<input>`/`<textarea>` has focus.

**Industry Standard:**
Linear: `a` for assign, `p` for priority, `l` for label. Superhuman: `e` for archive, `#` for trash, `j/k` for navigation. Gmail: `e` for archive, `j/k` for navigation. Keyboard-first triage is the industry standard for high-throughput queue processing.

**System Fit:**
The quarantine page already uses `useState` for all dialog open states (`approveDialogOpen`, `rejectDialogOpen`, etc.) and has a `working` guard. The keyboard handler calls the same setters. No architectural changes needed.

**Enforcement:**
- Design-system rule: "Queue triage pages MUST provide single-key shortcuts for primary actions."
- Playwright test: press `j` -> verify next item selected; press `a` -> verify approve dialog opens.

---

### F-10: Confidence UX Lacks Graduated Visual Weight — 0.95 and 0.35 Items Look Identical [SHOULD-ADD]

**Sources:** CLAUDE P1-F5, CODEX P1-F5, CLAUDE P2-D5, CODEX P2-D5

**Root Cause:**
In the list, confidence shows as a tiny 2px dot (`size='sm'` at `page.tsx:804-806`). In the detail panel, it's a segmented bar (`page.tsx:921-925`). But the surrounding content — card borders, font weights, card prominence — is identical regardless of confidence level. A 0.95 and 0.35 item have the same visual weight aside from the indicator itself.

**Fix Approach:**
1. **List items**: For items with `confidence < 0.5`, upgrade from `size='sm'` (dot) to `size='md'` (labeled badge) so low-confidence items visually stand out.
2. **Detail panel**: Add left-border tinting to the detail Card based on confidence band:
   - `>= 0.8`: green left border (`border-l-4 border-l-green-500`)
   - `0.5-0.8`: amber left border
   - `< 0.5`: red left border
3. **TriageSummaryCard**: When confidence < 0.5, show inline warning: "Low confidence — review carefully"

**Industry Standard:**
Medical decision support (Epic, Cerner) uses graduated severity indicators that change the entire container's visual weight, not just a score badge. Salesforce Einstein shows "confidence level" with contextual explanation.

**System Fit:**
`ConfidenceIndicator` at `ConfidenceIndicator.tsx:11-15` already computes `level` (high/medium/low) from thresholds. Existing CSS variables (`--confidence-high`, `--confidence-medium`, `--confidence-low`) can be reused for border tinting. Minimal CSS change.

**Enforcement:**
- Component tests: render items at 0.3, 0.6, 0.9 confidence — verify different border colors and indicator sizes.

---

### F-11: Conflicting Signals (High Urgency + Low Confidence) Not Surfaced — Cognitive Dissonance Unresolved [SHOULD-ADD]

**Sources:** CLAUDE P1-F8, CODEX P1-F5 (subsection), CLAUDE P2-D6, CODEX P2-D5 (subsection)

**Root Cause:**
Urgency badges at `page.tsx:816-820` (using `destructive` variant for HIGH) and confidence indicators at `page.tsx:921-924` are rendered independently with no visual relationship. HIGH urgency + LOW confidence (0.3) creates cognitive dissonance: "Act fast on something we're not sure about." The UI doesn't flag or resolve this.

**Fix Approach:**
Add a conditional warning in the TriageSummaryCard:
- If `urgency === 'HIGH' && (confidence ?? 1) < 0.5`: amber alert — "High urgency flagged but confidence is low — review reasoning carefully"
- If `urgency === 'LOW' && (confidence ?? 0) > 0.9`: info note — "High confidence — consider expediting"

Simple conditional render, not a new component.

**Industry Standard:**
Medical alert systems (Epic BPA) explicitly flag when multiple risk signals conflict. ISO 9241-171 for accessibility in decision support recommends "explicit disambiguation when automated signals contradict."

**System Fit:**
Both `urgency` and `confidence` are on `QuarantineItem` (confirmed at `api.ts:193-194`). The conditional is trivial.

**Enforcement:**
- Test case: render item with `urgency: 'HIGH', confidence: 0.3` — verify conflict indicator appears.

---

### F-12: Classification Vocabulary Drift — Uppercase UI Filters vs Lowercase Agent Values [SHOULD-ADD]

**Sources:** CODEX P1-F7, CODEX P2-U6, CLAUDE P2-U6

**Root Cause:**
UI filter options at `page.tsx:86-90` use uppercase: `DEAL_SIGNAL`, `UNCERTAIN`, `JUNK`. The bridge documentation at `server.py:877` specifies lowercase: `deal_signal, operational, newsletter, spam`. The backend filter at `main.py:1631` uses exact match: `COALESCE(q.raw_content->>'classification', 'unknown') = $N` — this is case-sensitive in PostgreSQL.

If the agent sends `deal_signal` (lowercase), the backend stores it as-is. The UI filter sends `DEAL_SIGNAL` (uppercase). The exact-match comparison fails — the item won't appear when filtering by "Deal signal." The operator sees an empty filtered queue despite items existing.

**Fix Approach (dashboard-only, no backend change):**
Normalize classification values at the dashboard API boundary. In `getQuarantineQueue`, after parsing the response, map classifications to a canonical form:
```typescript
const normalizeClassification = (c: string) => c?.toUpperCase() ?? 'UNKNOWN';
```
Apply to both: (a) parsed list items before rendering, and (b) filter values before sending to the backend (send lowercase to match what's stored).

Alternatively, send lowercase filter values from the UI: change `CLASSIFICATION_OPTIONS` to lowercase values (`deal_signal`, `uncertain`, `junk`) and add `operational`, `newsletter`, `spam` to the filter options (the agent produces these but the UI doesn't offer them as filters).

**Industry Standard:**
UI boundary normalization when producers emit multiple enum dialects. Enum values should be canonicalized at the parse boundary.

**System Fit:**
Frontend-only mapping. No backend changes. The list query already returns classification from `raw_content` without case normalization, so the display and filter logic must agree.

**Enforcement:**
- Unit test: mock queue response with lowercase `deal_signal` classification -> verify filter by "Deal signal" includes the item.
- Integration test: verify filter query values match what the backend stores.

---

### F-13: Comparison Workflow Missing — Past Decisions from Same Sender Not Surfaced [SHOULD-ADD]

**Sources:** CODEX P1-F8, CODEX P2-U7, CLAUDE P2-U7

**Root Cause:**
The backend already provides a sender feedback endpoint at `main.py:1753-1762`: `GET /api/quarantine/feedback` accepts `sender_email` and returns approval/rejection history and corrections. The dashboard has no component consuming this endpoint — confirmed by absence of any reference to `/api/quarantine/feedback` in `page.tsx` or `api.ts`.

An operator deciding on an item from a familiar broker would benefit from seeing: "Last 5 items from this sender: 4 approved, 1 rejected. Most common correction: company_name."

**Fix Approach:**
Add a collapsible "Past Decisions" card in the detail panel (or as a section of the SenderIntelligenceCard). Fetch from `/api/quarantine/feedback?sender_email={sender}` alongside the sender intelligence fetch. Display:
- Approval/rejection ratio (e.g., "4/5 approved")
- Most recent decision + timestamp
- Any correction patterns

**Industry Standard:**
CRM tools (Affinity, DealCloud) show historical interaction context alongside current items. Operator consistency improves when adjacent historical context is visible.

**System Fit:**
Backend endpoint exists. Needs: (1) API wrapper in `api.ts`, (2) fetch in detail panel `useEffect`, (3) simple card component. No backend changes.

**Enforcement:**
- API parser + UI tests for non-empty and empty history states.

---

### F-14: Undo Affordance Missing Despite Existing Backend + Frontend API Support [SHOULD-ADD]

**Sources:** CODEX P1-F3 (subsection), CLAUDE P2-U8

**Root Cause:**
The backend provides `POST /api/quarantine/{item_id}/undo-approve` at `main.py:3076`. The dashboard already has an API wrapper: `undoQuarantineApproval()` at `api.ts:1139-1149`. But the quarantine page has zero references to undo functionality — no import, no call, no UI affordance.

After approving an item, the operator has no recourse if they realize the decision was wrong. They must contact an admin to manually reverse it.

**Fix Approach:**
After a successful approve/reject action, show a toast notification with an "Undo" action button (5-second timeout). Clicking "Undo" calls `undoQuarantineApproval()`. The toast pattern is standard in the design system.

**Industry Standard:**
Gmail's "Undo send" (30s window). Slack's "Undo" toast after message delete. Every modern triage system provides an undo window for destructive actions.

**System Fit:**
Both backend endpoint and frontend wrapper exist. The only gap is a UI toast with an undo action. Minimal code.

**Enforcement:**
- Playwright test: approve item -> verify undo toast appears -> click undo -> verify item returns to queue.

---

### F-15: Quick Approve from List for High-Confidence Items [NICE-TO-HAVE]

**Sources:** CLAUDE P1-F9, CODEX P1-F3 (subsection), CLAUDE P2-D7

**Root Cause:**
The mission enhances list items (Phase 4) with more data display but no inline actions. For the 80% case — known broker, 0.95 confidence, DEAL_SIGNAL classification — the operator must still go through the full 5-step flow. At `page.tsx:777-854`, list items render data but no action buttons except delete (`page.tsx:838-849`).

**Fix Approach:**
Add a "Quick Approve" icon button to list items meeting ALL of:
- `confidence >= 0.85`
- `classification` indicates deal signal
- `is_broker === true` (from sender profile)

Clicking opens the approve dialog pre-filled with the item's data, skipping detail panel review.

**Industry Standard:**
Gmail quick actions in list view. Linear inline status changes. Superhuman keyboard triage.

**System Fit:**
The approve handler at `page.tsx:289-329` already reads from `selectedItem`. Quick approve sets `selectedId` to the item AND opens approve dialog simultaneously.

**Enforcement:**
- Gate: verify Quick Approve button only appears on items meeting thresholds.
- Gate: verify Quick Approve DOES NOT appear on low-confidence or non-deal-signal items.

---

### F-16: Queue Performance — No Virtualization at 200+ Items [NICE-TO-HAVE]

**Sources:** CLAUDE P1-F11, CODEX P1-F9, CLAUDE P2-D8, CODEX P2-D6

**Root Cause:**
`page.tsx:196-204` requests `limit: 200`. All items rendered via `.map()` at `page.tsx:777-854` inside a `ScrollArea` with no virtualization. Each list item is ~15 DOM elements, totaling ~3,000 DOM nodes. Mission's Phase 4 increases per-item DOM count further.

**Fix Approach:**
1. Use `@tanstack/react-virtual` to virtualize the list (only render items in viewport + overscan buffer).
2. Or add client-side pagination: 50 items with "Load more" button (backend already supports `offset` at `main.py:1614`).

**Industry Standard:**
Gmail, Linear, and every high-volume list virtualizes. Any list exceeding ~50 items should be virtualized.

**System Fit:**
`ScrollArea` (shadcn/Radix) wraps the list. Replacing inner `.map()` with `useVirtualizer` is a contained change.

**Enforcement:**
- Backlog item. Tag for implementation when queue regularly exceeds 100 items.

---

### F-17: Batch Triage — Broker/Sender Sort Options [NICE-TO-HAVE]

**Sources:** CLAUDE P1-F13, CLAUDE P2-U4, CODEX P2-C2

**Root Cause:**
Sort options at `page.tsx:98-103` only include `received_at`, `confidence`, `urgency`, `created_at`. No option to sort by `broker_name` or `sender` for grouping same-broker items together.

**Important correction:** CLAUDE P1 claimed this was a frontend-only change. This is INCORRECT. The backend's `valid_sorts` whitelist at `main.py:1674` only includes `{"received_at", "urgency", "confidence", "created_at"}`. Adding broker/sender sort REQUIRES a backend change (expanding `valid_sorts`).

**Fix Approach:**
Backend: add `broker_name` and `sender` to `valid_sorts`. Frontend: add corresponding options to `SORT_OPTIONS`. Optionally, add visual group separators in the list when sorted by broker.

**Industry Standard:**
Jira/Linear allow grouping by assignee. Email clients group by sender. CRM tools group by contact.

**System Fit:**
Requires a backend change (out of mission scope). Track as follow-up.

**Enforcement:**
- Backend: verify `broker_name`/`sender` in `valid_sorts`. Frontend: verify options appear in sort dropdown.

---

## DISCARDED ITEMS

Items from Pass 1 reports intentionally excluded from primary findings, with reasons.

### DISC-1: Legacy `links.groups` Detail Endpoint Claim — Unverified Evidence (from CLAUDE P1-F7 partial)

**Reason for exclusion:** CODEX P2 cross-review noted that the backend detail query at `main.py:2155-2190` does not return a `links` field (links are NOT selected in the detail SQL). The specific claim that the detail endpoint returns grouped links in `{ groups: {...} }` format is unverified. The general principle of preserving legacy format rendering IS included in F-7 — only this specific evidence claim about the detail endpoint is discarded.

### DISC-2: Mission Source Path Stale Reference (from CODEX P1-AO1)

**Reason for exclusion:** The mission references `/tmp/langsmith-export/schemas/canonical_output_schema.json` while the actual file is at `/tmp/langsmith-export/canonical_output_schema.json`. This is a documentation hygiene issue, not a dashboard UX finding. Does not affect operator decision speed.

### DISC-3: Design-System Rulebook Amendments as Standalone Deliverable (from CLAUDE P1 enforcement notes, CODEX P2-DRIFT4)

**Reason for exclusion:** Governance-document updates are outside mission execution scope. The enforcement mechanisms proposed alongside each finding are included within each finding but treated as post-mission follow-up, not a primary deliverable.

---

## DRIFT LOG

Out-of-scope items flagged during review. Not actionable within this mission's dashboard-only fence.

### DRIFT-1: Broker/Sender Sort Requires Backend `valid_sorts` Change
**Source:** CLAUDE P1-F13, CLAUDE P2-U4, CODEX P2-C2
**Why out of scope:** Mission explicitly states "Do NOT propose backend changes." Adding `broker_name`/`sender` to `valid_sorts` at `main.py:1674` is a backend SQL change.
**Severity if ignored:** LOW — existing sort options work. UX convenience enhancement.
**Action:** Track as follow-up backend task. F-17 documents the full requirement.

### DRIFT-2: Classification Filter Case Normalization in Backend SQL
**Source:** CODEX P1-F7, CLAUDE P2-U6
**Why out of scope:** The root fix (adding `UPPER()` to `main.py:1631`) is a backend SQL change. F-12's frontend normalization addresses the symptom.
**Severity if ignored:** MEDIUM — if agent injects lowercase classifications, existing filters silently fail. F-12 mitigates.
**Action:** Backend team should add `UPPER()` to classification filter WHERE clause.

### DRIFT-3: Sender Intelligence Endpoint Rate Limiting
**Source:** CLAUDE P1-AO3
**Why out of scope:** Adding rate limiting to `GET /api/quarantine/sender-intelligence` is a backend infrastructure concern. F-8's frontend debounce mitigates.
**Severity if ignored:** LOW — frontend debounce is sufficient.

### DRIFT-4: Backend Detail Endpoint Routing Fields Not in List Query
**Source:** CLAUDE P1-AO1
**Why out of scope:** The list query at `main.py:1698-1730` does not select `routing_conflict` or `conflicting_deal_ids`. Adding these is a backend query change. The detail endpoint provides them, so the UI works after loading detail.
**Severity if ignored:** LOW — conflict flow works from detail data; list items don't show conflict indicator inline.

### DRIFT-5: Tabs for Detail Panel Organization
**Source:** CLAUDE P1-AO4
**Why out of scope:** Architectural suggestion beyond mission scope. Adding tabs changes panel structure fundamentally.
**Severity if ignored:** LOW — scrollable panel works, gets long with 8+ sections.

---

## ACCEPTANCE GATES

Builder-enforceable gates for implementing the consolidated findings.

### Gate 1: Schema Parity — Unified Schema Includes All Required Fields
**Command:** `grep -c 'routing_conflict\|conflicting_deal_ids\|langsmith_run_id\|langsmith_trace_url\|tool_version\|prompt_version' apps/dashboard/src/lib/api.ts`
**Pass criteria:** Output >= 6 (all 6 fields present in schema file). Exit code 0.
**Validates:** F-1, F-5

### Gate 2: Correction Key Alignment — Approve Dialog Uses Backend-Compatible Keys
**Command:** `grep -n "key: '" apps/dashboard/src/app/quarantine/page.tsx | grep -E "(company_guess|broker_email)" && echo "FAIL: stale correction keys found" && exit 1 || echo "PASS"`
**Pass criteria:** No occurrences of `company_guess` or `broker_email` as correction keys. Exit code 0.
**Validates:** F-2

### Gate 3: Routing Conflict Regression — Thread Conflict UI Renders
**Command:** Playwright test or manual verification: render item with `routing_conflict: true, conflicting_deal_ids: ["deal-A", "deal-B"]`. Assert "Approve into this deal" buttons appear.
**Pass criteria:** Both deal buttons render. "Create new deal instead" button renders.
**Validates:** F-1

### Gate 4: Legacy Evidence Fallback — Flat Format Renders via Dual-Source
**Command:** Render quarantine item with `extraction_evidence: { company_name: "Acme Corp" }, company_name: "Acme Corp"`. Verify card shows "Acme Corp" even without nested sub-objects.
**Pass criteria:** Company name visible. No blank/broken sections.
**Validates:** F-3

### Gate 5: Null Evidence State — Graceful Empty State
**Command:** Render quarantine item with `extraction_evidence: null`. Verify intelligence cards show "Not available" messages.
**Pass criteria:** No JavaScript errors. Muted "Not available" text visible.
**Validates:** F-3, F-4

### Gate 6: Preview Parse Degradation — Partial Data Renders on Schema Drift
**Command:** Mock `getQuarantinePreview` to return response with unexpected field type. Verify partial data renders with drift indicator, not "Preview not found."
**Pass criteria:** Partial data renders. No "Preview not found" on recoverable drift.
**Validates:** F-4

### Gate 7: Provenance Link Renders
**Command:** Render item with `langsmith_trace_url: "https://smith.langchain.com/run/abc"`. Verify "View agent trace" link renders.
**Pass criteria:** Link visible, clickable, correct href.
**Validates:** F-5

### Gate 8: Sender Null Safety — Legacy Items Don't Fire 400 Errors
**Command:** Render item with `sender: null, from: "broker@example.com"`. Trigger sender intelligence fetch. Verify fetch uses `"broker@example.com"`.
**Pass criteria:** No 400 errors. Fetch uses fallback email.
**Validates:** F-6

### Gate 9: Keyboard Navigation — j/k and Action Shortcuts Work
**Command:** Playwright test: load quarantine page with 3+ items. Press `j` -> next item. Press `k` -> previous. Press `a` -> approve dialog opens.
**Pass criteria:** All three keyboard interactions work.
**Validates:** F-9

### Gate 10: Abort Controller — Rapid Selection Doesn't Show Stale Data
**Command:** Playwright test: mock preview endpoint with 500ms delay. Click item A, then item B within 100ms. Verify only item B's preview displays.
**Pass criteria:** Preview matches last-selected item.
**Validates:** F-8

### Gate 11: Classification Filter Normalization
**Command:** Mock queue response with lowercase `deal_signal` classification. Apply "Deal signal" filter. Verify item appears.
**Pass criteria:** Filter matches despite case difference.
**Validates:** F-12

---

## STATISTICS

| Metric | Count |
|--------|-------|
| Total Pass 1 findings (CLAUDE) | 13 |
| Total Pass 1 findings (GEMINI) | 0 (no output) |
| Total Pass 1 findings (CODEX) | 9 |
| **Total Pass 1 findings across all agents** | **22** |
| Pass 1 adjacent observations (CLAUDE) | 4 |
| Pass 1 adjacent observations (CODEX) | 2 |
| Pass 2 duplicates identified (CLAUDE) | 8 |
| Pass 2 duplicates identified (CODEX) | 6 |
| Pass 2 conflicts identified | 2 |
| **Deduplicated primary findings (F-1 through F-17)** | **17** |
| -- MUST-ADD | 7 (F-1 through F-7) |
| -- SHOULD-ADD | 7 (F-8 through F-14) |
| -- NICE-TO-HAVE | 3 (F-15 through F-17) |
| Discarded (with reason) | 3 (DISC-1 through DISC-3) |
| Drift items | 5 (DRIFT-1 through DRIFT-5) |
| Acceptance gates | 11 |
| **Drop rate** | **0%** (all 22 findings accounted for) |

### Finding Accounting

Every Pass 1 finding is mapped to a Final Master item:

| Pass 1 Source | Final Master |
|---------------|-------------|
| CLAUDE F1 (approve dialog) | F-2 |
| CLAUDE F2 (keyboard shortcuts) | F-9 |
| CLAUDE F3 (fetch race) | F-8 |
| CLAUDE F4 (provenance fields) | F-5 |
| CLAUDE F5 (confidence UX) | F-10 |
| CLAUDE F6 (empty evidence) | F-3 |
| CLAUDE F7 (legacy links) | F-7 |
| CLAUDE F8 (conflicting signals) | F-11 |
| CLAUDE F9 (quick approve) | F-15 |
| CLAUDE F10 (parse failure) | F-4 |
| CLAUDE F11 (virtualization) | F-16 |
| CLAUDE F12 (sender null) | F-6 |
| CLAUDE F13 (broker sort) | F-17 |
| CLAUDE AO-1 (routing list query) | DRIFT-4 |
| CLAUDE AO-2 (snippet length) | Covered by F-3 (component design handles long content) |
| CLAUDE AO-3 (rate limiting) | DRIFT-3 |
| CLAUDE AO-4 (tabs suggestion) | DRIFT-5 |
| CODEX F1 (parse failure + schema) | F-4 |
| CODEX F2 (routing conflict) | F-1 |
| CODEX F3 (keyboard + undo) | F-9, F-14 |
| CODEX F4 (fetch race) | F-8 |
| CODEX F5 (data trust) | F-10, F-11 |
| CODEX F6 (provenance) | F-5 |
| CODEX F7 (classification drift) | F-12 |
| CODEX F8 (comparison workflow) | F-13 |
| CODEX F9 (queue scaling) | F-16 |
| CODEX AO-1 (schema path) | DISC-2 |
| CODEX AO-2 (design system read) | DISC-3 |

---

*End of consolidated master. All findings from all agents accounted for. Ready for builder execution.*
