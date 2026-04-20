# TriPass — Pass 2: Cross-Review and Deduplication

## Agent Identity
**Agent**: CODEX
**Run ID**: TP-20260218-095911
**Pipeline Mode**: design
**Timestamp**: 2026-02-18T10:09:06Z

---

## Mission (Original)

# TRIPASS MISSION: Adversarial Review of QUARANTINE-INTELLIGENCE-001

## Why This Investigation Exists

We have a mission prompt (`MISSION-QUARANTINE-INTELLIGENCE-001.md`) that plans to transform the quarantine decision-support experience from "decide blind" to "decide in 3 seconds with full context." The mission was designed by a single agent (Claude Opus 4.6). Before we execute it, we need three independent adversarial perspectives to find:

1. **What can we do better** — improvements, polish, UX patterns the mission missed
2. **What gaps exist** — data that flows through the system but isn't surfaced, operator workflows not considered
3. **What limitations we haven't addressed** — edge cases, failure modes, degradation scenarios
4. **Contrarian thinking** — what would an experienced deal operator push back on? What would a UX designer critique?
5. **Adversarial mindset** — what happens when data is wrong, stale, contradictory, or malicious?

## The Equation

- **Variable 1 (KNOWN):** The problem — operators see "Preview not found" when they click quarantine items. Even when data shows, it's bare: no reasoning, no financials, no broker identity, no entities, no links, no sender reputation.
- **Variable 2 (KNOWN):** The mission prompt — 7 phases, 13 AC, 9 new components, structured extraction_evidence schema, sender intelligence, agent deployment package.
- **Variable 3 (UNKNOWN):** What we're blind to. What would make THIS quarantine experience genuinely world-class? What would a $10M SaaS product do that we haven't thought of?

## Non-Negotiable Constraints

- This is **INVESTIGATION ONLY**: Analyze → Report → Stop.
- Do NOT propose backend changes (the mission explicitly fences those out).
- Do NOT propose database migrations.
- Focus on **dashboard UX, data rendering, operator workflow, decision ergonomics**.
- Every finding MUST reference specific files and line numbers.
- Every recommendation MUST be actionable and concrete.

## Primary Objectives

Each agent should produce findings across these 6 lenses:

### Lens 1: Decision Ergonomics
Can an operator actually make an approve/reject decision in under 3 seconds with this design? What's the cognitive flow? What information hierarchy would a UX expert design? Are the 8 cards in the right priority order? Should some be collapsed by default? What about keyboard shortcuts for rapid triage?

### Lens 2: Data Fidelity {{MISSION_DESCRIPTION}} Trust
When extraction_evidence is partially populated, what does the UI show? When confidence is 0.3 vs 0.95, does the UI communicate that difference? Can the operator trust the AI's reasoning? Should there be visual indicators of data quality/completeness? What about conflicting signals (HIGH urgency but LOW confidence)?

### Lens 3: Missing Workflows
The mission focuses on the detail panel. But what about:
- Comparison view (this item vs similar past items that were approved/rejected)?
- Batch triage patterns (5 items from same broker — should they be grouped)?
- Snooze/defer (not approve or reject, but "come back to this")?
- Quick actions without opening detail (approve from list if high confidence)?
- Undo after action (approve → immediately realize mistake)?
- Annotation/notes before deciding?

### Lens 4: Information the Agent Produces but the Mission Doesn't Surface
Read the LangSmith agent's canonical output schema and the bridge tool parameters. Cross-reference with the mission's extraction_evidence schema and the 8 planned components. What data does the agent produce that is NOT captured in extraction_evidence or is captured but NOT rendered?

### Lens 5: Edge Cases {{MISSION_DESCRIPTION}} Failure Modes
- What if extraction_evidence is `{}` (empty object)?
- What if extraction_evidence has unknown/unexpected keys?
- What if financials contain contradictory data?
- What if sender intelligence endpoint is slow/down?
- What if there are 200+ items in the queue?
- What if the same email arrives twice with different extraction?
- What about long email bodies (10,000+ chars)?
- What about non-English emails?
- What about HTML-only emails with no plain text?

### Lens 6: World-Class Benchmarks
What do the BEST deal management / email triage / CRM tools do?
- Superhuman (email triage)
- Affinity CRM (deal intelligence)
- DealCloud (M{{MISSION_DESCRIPTION}}A workflow)
- Salesforce Lightning (opportunity cards)
- Linear (issue triage with keyboard-first UX)

What patterns from these tools should inform our design?

## Scope

### Files to Read (MANDATORY — every agent must read these)

**The mission prompt being reviewed:**
- `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md`

**Current quarantine implementation (the "before"):**
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (lines 170-260 for schemas, lines 940-965 for getQuarantinePreview)

**Backend data model (what's available):**
- `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` (lines 247-286 for QuarantineResponse, lines 1698-1742 for list endpoint, lines 2039-2148 for sender-intelligence)

**Agent injection schema (what the agent sends):**
- `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` (lines 832-1039 for zakops_inject_quarantine)

**Design system patterns (what we must follow):**
- `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` (reference patterns)

**Existing quarantine components:**
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/` (all files)

### Repository Roots
- `/home/zaks/zakops-agent-api` (monorepo)
- `/home/zaks/bookkeeping` (docs)

## Deliverables

Each agent writes their report to the designated output file. The consolidation report should:
1. Rank ALL findings by impact on operator decision speed
2. Group into: MUST-ADD (before execution), SHOULD-ADD (during execution), NICE-TO-HAVE (backlog)
3. For MUST-ADD items, provide specific component/file/line recommendations
4. For each finding, answer: "Does this help the operator decide faster?"

## Success Criteria

The TriPass succeeds if it identifies at least 5 actionable improvements that would materially improve operator decision speed or accuracy, AND provides concrete implementation guidance for each.

---

## Pass 1 Reports

You have access to all three Pass 1 reports:

### Report A (CLAUDE)
# Pass 1 Report — CLAUDE
## Run: TP-20260218-095911 | Mode: design
## Generated: 2026-02-18T09:59:14Z

---

## PRIMARY FINDINGS

### Finding 1: Approve Dialog Reads from Stale `preview.extracted_fields` — Will Break After Schema Unification

**Root Cause:**
`page.tsx:1155-1174` — The approve dialog populates its editable correction fields by reading from `preview.extracted_fields`, which is a field on `QuarantinePreviewSchema` (the old disk-based preview format). After Phase 1 unifies `getQuarantinePreview()` to return `QuarantineItem`, the `extracted_fields` property will no longer exist. The approve dialog becomes a blank form with no pre-populated values.

Specifically:
- Line 1156: `{ key: 'company_guess', label: 'Company name' }` reads `preview.extracted_fields?.company_guess`
- Line 1157: `{ key: 'broker_email', label: 'Broker email' }` reads `preview.extracted_fields?.broker_email`
- Line 1158: `{ key: 'asking_price', label: 'Asking price' }` reads `preview.extracted_fields?.asking_price`
- Line 1160: `const original = String((preview.extracted_fields as Record<string, unknown>)?.[key] ?? '')`

After unification, these should read from:
- `company_guess` -> `preview.company_name` or `preview.extraction_evidence?.entities?.companies?.[0]?.name`
- `broker_email` -> `preview.sender` (broker email) or `preview.extraction_evidence?.broker?.email`
- `asking_price` -> `preview.extraction_evidence?.financials?.asking_price`

The mission's P3-05 acknowledges this ("Update approve dialog — currently reads from `preview.extracted_fields`"), but the task description says to update to `preview.company_name`, `preview.broker_name`, and `preview.extraction_evidence?.financials?.asking_price`. This is **incomplete**: it doesn't specify updating the `key` field identifiers used for the `corrections` dict that gets sent to the backend. If the corrections dict sends `{ company_guess: "..." }` but the backend expects `{ company_name: "..." }`, the correction is silently ignored.

**Fix Approach:**
The approve dialog correction fields must:
1. Change `key: 'company_guess'` -> `key: 'company_name'`
2. Change `key: 'broker_email'` -> `key: 'broker_name'` (and change label to "Broker name")
3. Keep `key: 'asking_price'` but source from `preview.extraction_evidence?.financials?.asking_price ?? ''`
4. Source defaults from the unified `QuarantineItem` fields, not from `extracted_fields`

Additionally, add a 4th editable field: `broker_name` (since broker identity is now a first-class field from the agent).

**Industry Standard:**
OWASP input handling — pre-populating form fields from the correct data source prevents data loss. CRM correction workflows (Salesforce Lightning inline edit) always pre-fill from the current record, not a stale snapshot.

**System Fit:**
The `corrections` dict is sent to `POST /api/quarantine/{id}/process` as `corrections: Record<string, string>`. The backend's correction keys must match what the dialog sends. Since the backend stores `company_name` and `broker_name` as top-level columns, the correction keys should use those canonical names.

**Enforcement:**
Add a TypeScript type for correction keys: `type CorrectionField = 'company_name' | 'broker_name' | 'asking_price'`. Use this in the corrections state and the editable field array to prevent drift. Add a comment at the correction field array: `// SYNC: keys must match backend quarantine_items column names`.

---

### Finding 2: No Keyboard Shortcuts for Rapid Triage — 3-Second Decision Target Requires Keyboard-First UX

**Root Cause:**
`page.tsx` (entire file) — There are zero keyboard shortcuts defined. Every action requires clicking through the UI: click item in list -> read detail panel -> click "Approve" button -> click "Approve" in dialog. That's 4 clicks minimum for the simplest approve flow. The mission's stated goal is "approve/reject decisions in seconds" but the architecture is mouse-first.

For context, the page has 6 action buttons at lines 904-918 (Delegate, Escalate, Reject, Approve) all requiring `disabled={!preview || working}` — they're click-only.

**Fix Approach:**
Add a `useEffect` keyboard event handler at the page level:
- `a` -> Open approve dialog (if preview loaded and not working)
- `r` -> Open reject dialog
- `e` -> Open escalate dialog
- `d` -> Open delegate dialog
- `j` / `k` or Up/Down arrows -> Navigate queue list (prev/next item)
- `x` -> Toggle bulk-select on current item
- `Escape` -> Close any open dialog
- `Enter` (within dialog) -> Confirm action

Guard all shortcuts: only fire when no dialog is open and no input/textarea has focus.

**Industry Standard:**
Linear uses `a` for assign, `p` for priority, `l` for label — all single-key shortcuts. Superhuman uses `e` for archive, `#` for trash, `j/k` for navigation. Gmail uses `e` for archive, `j/k` for navigation. Keyboard-first triage is the industry standard for high-throughput queue processing.

**System Fit:**
The quarantine page already uses `useState` for all dialog open states (`approveDialogOpen`, `rejectDialogOpen`, etc.) and has a `working` guard. The keyboard handler would simply call the same setters: `setApproveDialogOpen(true)`. No architectural changes needed.

**Enforcement:**
Add to design-system.md rule: "Queue triage pages MUST provide single-key shortcuts for primary actions (approve/reject) and j/k navigation." Surface 9 validation should check for `useEffect` keyboard handler in triage pages.

---

### Finding 3: Sender Intelligence Fetch Has No Debounce — Rapid Item Clicking Fires N Concurrent Requests

**Root Cause:**
The mission's P3-01 adds a `useEffect` that fetches sender intelligence when `selectedItem?.sender` changes. But the existing preview fetch at `page.tsx:268-273` already fires on every `selectedId` change with no debounce or cancellation. If an operator clicks through 5 items quickly (a common triage pattern — scanning subjects), this fires 5 preview fetches AND 5 sender intelligence fetches = 10 concurrent requests. Only the last one matters.

The current preview fetch at line 268-273:
```typescript
useEffect(() => {
  if (!selectedItem) return;
  const itemId = selectedItem.id || selectedItem.quarantine_id;
  if (itemId) loadPreview(itemId);
}, [selectedId]);
```
No `AbortController`, no cancellation, no debounce.

**Fix Approach:**
1. Use `AbortController` for both preview and sender intelligence fetches. Store the controller in a ref. On each new fetch, abort the previous one.
2. For sender intelligence specifically, add a 300ms debounce (sender data is supplementary, not blocking).
3. Use `Promise.allSettled` to fetch preview AND sender intelligence in parallel (per Surface 9 A1 mandate), with the sender intelligence wrapped in a debounce.

Pattern:
```typescript
const abortRef = useRef<AbortController | null>(null);
useEffect(() => {
  abortRef.current?.abort();
  const controller = new AbortController();
  abortRef.current = controller;
  // ... fetch with signal: controller.signal
  return () => controller.abort();
}, [selectedId]);
```

**Industry Standard:**
React 18 `useEffect` cleanup with AbortController is the recommended pattern for cancellable fetches (React docs, "You Might Not Need an Effect"). Every CRM and email client debounces list selection to detail fetch.

**System Fit:**
The deal detail page at `deals/[id]/page.tsx` uses `Promise.allSettled` for 10 concurrent fetches but operates on a single item (URL-routed), not a selectable list. The quarantine page's click-to-select pattern needs different handling — stale closure prevention via abort.

**Enforcement:**
Add to design-system.md A1: "List-to-detail selection patterns MUST use AbortController to cancel stale fetches. Supplementary fetches (sender intelligence) SHOULD debounce 300ms."

---

### Finding 4: The Mission's ExtractionEvidence Schema Omits LangSmith Traceability Fields That the Backend Returns

**Root Cause:**
The backend's `QuarantineResponse` (`main.py:274-278`) returns 4 LangSmith traceability fields:
- `langsmith_run_id: str | None`
- `langsmith_trace_url: str | None`
- `tool_version: str | None`
- `prompt_version: str | None`

The dashboard's `QuarantineItemSchema` (`api.ts:175-213`) does NOT include these fields. They are returned by both the list and detail endpoints (see SQL at `main.py:1723-1727` and `main.py:2179-2182`). Zod's default behavior is to strip unknown keys, so these fields are silently dropped during parsing.

The mission's Phase 1 (`P1-01`, `P1-02`) focuses on adding `ExtractionEvidenceSchema` and updating `extraction_evidence`/`field_confidences` types, but never mentions adding `langsmith_run_id`, `langsmith_trace_url`, `tool_version`, or `prompt_version` to `QuarantineItemSchema`.

This matters because:
1. The `langsmith_trace_url` is a direct link to the agent's reasoning trace — invaluable for operators debugging AI decisions
2. The `tool_version` and `prompt_version` help operators identify which agent version produced the classification — critical when the agent is updated and prior classifications may be stale

**Fix Approach:**
Add to `QuarantineItemSchema` in `api.ts`:
```typescript
langsmith_run_id: z.string().nullable().optional(),
langsmith_trace_url: z.string().nullable().optional(),
tool_version: z.string().nullable().optional(),
prompt_version: z.string().nullable().optional(),
```

Then in the Phase 2 component design, add a "Provenance" or "Agent Trace" section to the TriageIntelPanel (or as a small footer on TriageSummaryCard):
- If `langsmith_trace_url` exists: render as a small "View agent trace" link with `IconExternalLink`
- Show `tool_version` / `prompt_version` as muted metadata

**Industry Standard:**
AI-assisted decision support systems require provenance tracking (EU AI Act Article 13: transparency requirements). Operators must be able to trace back to the AI's reasoning. Affinity CRM shows "data source" badges on AI-enriched fields.

**System Fit:**
The backend already returns these fields. The bridge (`server.py:856-859`) already passes them through. The only gap is the dashboard Zod schema and UI rendering. This is a zero-backend-change fix.

**Enforcement:**
After Phase 1 schema unification, add a cross-reference test: count fields in `QuarantineResponse` (Python) vs `QuarantineItemSchema` (Zod). Any field in the response model that isn't in the Zod schema is a drift bug. This could be a `make validate-surface1` enhancement.

---

### Finding 5: No Visual Differentiation Between High-Confidence and Low-Confidence AI Decisions — Operators May Over-Trust or Under-Trust

**Root Cause:**
`page.tsx:921-925` — The detail panel header shows a `ConfidenceIndicator` bar, but it's a standalone element with no contextual framing. A 0.95 confidence and a 0.35 confidence both show the same card layout, same font weights, same card borders. The only difference is the bar fill level and color.

The mission's P2-02 (`TriageSummaryCard`) adds `deal_match_confidence` as a `ConfidenceIndicator (lg)` and `match_factors` as badges. But there's no proposal for changing the visual weight or prominence of the ENTIRE detail panel based on confidence level.

In the list items (`page.tsx:804-806`), the confidence indicator is a tiny 2px dot (`size='sm'`):
```typescript
{item.confidence != null {{PASS1_REPORT_A}}{{PASS1_REPORT_A}} (
  <ConfidenceIndicator score={item.confidence} size='sm' />
)}
```
A 0.3 red dot looks almost identical to a 0.95 green dot at a glance in a list.

**Fix Approach:**
1. **List items**: Replace `size='sm'` (dot only) with `size='md'` for items with confidence < 0.5, so low-confidence items visually stand out with a labeled badge instead of a dot.
2. **Detail panel header**: Add a subtle border tint to the entire detail Card based on confidence level:
   - `confidence >= 0.8`: left border green (`border-l-4 border-l-green-500`)
   - `0.5 <= confidence < 0.8`: left border amber (`border-l-4 border-l-amber-500`)
   - `confidence < 0.5`: left border red with slightly elevated visual weight (`border-l-4 border-l-red-500`)
3. **TriageSummaryCard**: When confidence < 0.5, show an inline warning: "Low confidence — review carefully before deciding"

**Industry Standard:**
Medical decision support systems (Epic, Cerner) use graduated visual severity indicators — not just a score display, but contextual framing that changes the entire panel's visual weight. Salesforce Einstein shows "confidence level" with contextual explanation ("Based on 3 signals").

**System Fit:**
The `ConfidenceIndicator` component at `ConfidenceIndicator.tsx:11-14` already computes `level` (high/medium/low) from score thresholds. The existing CSS variables (`--confidence-high`, `--confidence-medium`, `--confidence-low`) can be reused for border tinting. This is a minimal CSS change.

**Enforcement:**
Add to design system rules: "AI-confidence-driven UI MUST provide graduated visual weight, not just score display. The visual prominence of the container must change with confidence level."

---

### Finding 6: Empty `extraction_evidence` Handling Is Underspecified — `{}` vs `null` vs Partially-Populated Create Different Failure Modes

**Root Cause:**
The mission says "every component uses `?.` optional chaining and `?? []` fallbacks" (Pre-Mortem #5), but doesn't specify behavior for these distinct cases:

1. **`extraction_evidence: null`** — Old items pre-Pipeline A. Components should show "No AI analysis available"
2. **`extraction_evidence: {}`** — Empty dict. The agent injected but produced no extraction. Components should show "AI analysis produced no signals" (different message — this indicates the agent ran but found nothing)
3. **`extraction_evidence: { reasons: [], financials: null, broker: { name: "John", email: null } }`** — Partially populated. Each sub-section must handle its own null sub-tree independently.
4. **`extraction_evidence: { unknown_future_field: "value" }`** — Forward-compat via `.passthrough()`. Components must not crash on unexpected keys.

Critically, the bridge at `server.py:852` passes `extraction_evidence: Optional[dict] = None`, and the golden test at `test_golden_injection.py:45` shows `extraction_evidence: {"company_name": "Project Falcon in subject"}` — a flat key-value dict, NOT the nested schema the mission proposes (with `financials`, `broker`, `entities` sub-objects).

This means the mission's `ExtractionEvidenceSchema` defines a FUTURE schema that NO current items populate. Every current item has either `null`, `{}`, or a flat `{ field_name: "evidence_string" }` format. The new components will show empty states for ALL existing items until the agent is updated via the deployment package.

**Fix Approach:**
1. Every component must distinguish three states visually:
   - `null` -> "Not available" (muted, no icon)
   - `{}` or all-null sub-fields -> "AI analysis ran — no signals detected" (muted, with info icon)
   - Partially populated -> Render available fields, hide empty ones (no dash placeholders cluttering the panel)
2. The `ExtractionEvidenceSchema` must use `.passthrough()` AND must accept the CURRENT flat format (evidence strings) as a fallback. Define a `legacyEvidence: z.record(z.string()).optional()` catch-all for flat key-value evidence that doesn't match the new nested schema.
3. Each card component should accept both `extraction_evidence` (new nested) and the flat fields from `QuarantineItem` (e.g., `company_name`, `broker_name`) and prefer the richer nested data when available, falling back to flat fields.

**Industry Standard:**
Schema evolution best practice (Google API Design Guide): new schemas must be backward-compatible with existing data. The UI layer must handle both old and new formats during the transition period. Progressive enhancement: show what's available, hide what's not.

**System Fit:**
The existing `page.tsx:1020-1033` already reads flat fields from `selectedItem` (e.g., `selectedItem?.company_name`). The new DealSignalsCard should check `extraction_evidence?.broker?.name ?? selectedItem?.broker_name` (nested first, flat fallback). This dual-source pattern is critical because the deployment package won't be relayed to the agent instantly.

**Enforcement:**
Phase 2 gate should include: "Render a quarantine item with `extraction_evidence: { company_name: 'Test Corp' }` (flat format) — verify it degrades gracefully and shows the flat value in the appropriate card."

---

### Finding 7: The `renderLinkGroups` and `renderAttachments` Helpers Use the Old Preview Schema — Removal Risk for Legacy Items

**Root Cause:**
`page.tsx:1420-1515` — The `renderLinkGroups()` function reads from `preview.links?.groups` (a categorized link object from the old disk-based quarantine preview) and `preview.attachments?.items` (an attachment array from the old schema). After Phase 1 unification, `preview` becomes a `QuarantineItem` which has:
- `links: z.array(z.record(z.any())).nullable().optional()` — a flat array, NOT a `{ groups: {...}, stats: {...} }` object
- `attachments: z.any().nullable().optional()` — untyped

The mission's P3-04 says "Remove old inline render helpers (now handled by MaterialsAndLinksCard)." But MaterialsAndLinksCard (P2-05) is designed for `extraction_evidence.typed_links` — the NEW format from the agent. What about:
1. **Legacy email_sync items** that have `links.groups` from the disk-based preview?
2. **Legacy items with `attachments.items`** array from the old format?

The mission says "Falls back to flat attachments field for legacy items" but doesn't specify the fallback for the old `links.groups` categorized format.

**Fix Approach:**
The MaterialsAndLinksCard should implement a 3-tier data source priority:
1. **Primary**: `extraction_evidence.typed_links` (new agent format)
2. **Secondary**: `item.links` (if it's an array, render as flat link list)
3. **Tertiary**: If `item.links` has a `.groups` property (old disk-based format), render the categorized view (port the rendering logic from `renderLinkGroups`)

Don't delete `renderLinkGroups` logic — extract and adapt it into MaterialsAndLinksCard as a fallback renderer. The old format is still in the database for historical items.

**Industry Standard:**
Data migration best practice: never remove rendering support for old formats until all existing records have been migrated. The UI should be the last thing to drop backward compatibility.

**System Fit:**
The `QuarantineItemSchema` at `api.ts:204` defines `links: z.array(z.record(z.any())).nullable().optional()` — typed as an array. But the old preview format had `links: { groups: {...}, stats: {...} }` — an object. After unification, the backend detail endpoint returns `links` from the quarantine_items table directly, not from the disk-based preview. Need to verify: what format is `links` stored in the DB? If it was populated by the old email_sync pipeline, it may be the categorized format. If populated by the new LangSmith pipeline, it may be a flat array or null.

**Enforcement:**
Phase 3 gate must include: "Test rendering a legacy email_sync item that has `links: { groups: { deal_material: [...] } }` format — verify links still display."

---

### Finding 8: Conflicting Signal Display — HIGH Urgency + LOW Confidence Creates Cognitive Dissonance Without Resolution

**Root Cause:**
The mission plans to show urgency badges (P2-04: `ClassificationReasoningCard` with urgency_signals as amber-tinted badges) and confidence indicators (P2-02: `TriageSummaryCard` with `deal_match_confidence` as ConfidenceIndicator). But there's no design for what happens when these signals conflict:
- HIGH urgency + LOW confidence (0.3) = "Act fast on something we're not sure about"
- LOW urgency + HIGH confidence (0.95) = "We're very sure this is a deal, but no rush"

Currently at `page.tsx:816-820`, urgency "high" gets a `destructive` badge variant. At line 921-924, confidence shows a segmented bar. These are in different locations (list item vs detail header) with no visual relationship.

**Fix Approach:**
Add a "Signal Conflict" indicator to the TriageSummaryCard when urgency and confidence diverge significantly:
- If `urgency === 'HIGH' {{PASS1_REPORT_A}}{{PASS1_REPORT_A}} confidence < 0.5`: Show amber alert: "High urgency flagged but confidence is low — review reasoning carefully"
- If `urgency === 'LOW' {{PASS1_REPORT_A}}{{PASS1_REPORT_A}} confidence > 0.9`: Show info note: "High confidence — consider expediting despite low urgency flag"

This is a simple conditional render, not a new component. Place it between the confidence bar and match_factors in TriageSummaryCard.

**Industry Standard:**
Medical alert systems (Epic BPA) explicitly flag when multiple risk signals conflict. ISO 9241-171 for accessibility in decision support recommends "explicit disambiguation when automated signals contradict."

**System Fit:**
Both `urgency` and `confidence` are already on `QuarantineItem` (flat fields from list data). The conditional is trivial: `if (item.urgency === 'HIGH' {{PASS1_REPORT_A}}{{PASS1_REPORT_A}} (item.confidence ?? 1) < 0.5)`.

**Enforcement:**
Add test case to Phase 2 gate: "Render item with urgency=HIGH, confidence=0.3 — verify conflict indicator appears."

---

### Finding 9: No "Quick Approve" from List — High-Confidence Items Require Full Detail Panel Drill-Down

**Root Cause:**
The mission enhances list items (Phase 4: add company name, triage summary snippet, broker badge) but doesn't add any inline actions. For the 80% case — a known broker sends a deal signal with 0.95 confidence — the operator still must: (1) click item, (2) wait for preview load, (3) scan detail panel, (4) click Approve, (5) confirm in dialog. That's a 5-step flow.

The mission's stated goal is "decisions in seconds." For high-confidence, familiar-sender items, a 2-step flow would be: (1) see green confidence dot + known broker badge + triage summary in list, (2) click "Quick Approve" button right in the list item row.

**Fix Approach:**
Add a "Quick Approve" icon button to list items that meet ALL of:
- `confidence >= 0.85`
- `classification === 'DEAL_SIGNAL'`
- Sender is a known broker (from `is_broker` flag)

The button would appear as a small green check icon in the list item row (next to the delete button at line 838-849). Clicking it opens the approve dialog pre-filled with the item's data, skipping the detail panel entirely.

For items that don't meet the threshold, don't show the button — avoid decision fatigue.

**Industry Standard:**
Gmail "Quick actions" in list view (archive, delete, snooze without opening). Linear's inline status changes. Superhuman's `e` to archive from list view without opening.

**System Fit:**
The approve handler at `page.tsx:289-329` already reads from `selectedItem`. For quick approve, clicking "Quick Approve" would set `selectedId` to the item AND open the approve dialog simultaneously.

**Enforcement:**
This is a SHOULD-ADD item. Gate: "Verify Quick Approve button only appears on items meeting confidence + classification + broker thresholds."

---

### Finding 10: `getQuarantinePreview` Returns `null` on Zod Parse Failure With No Error Details to the Operator

**Root Cause:**
`api.ts:949-962` — When `QuarantinePreviewSchema.safeParse(data)` fails, the function logs `console.warn('Invalid quarantine preview response:', parsed.error)` and returns `null`. The caller at `page.tsx:256-258` then sets `previewError` to the generic string `'Preview not found'`.

The operator sees "Preview not found" with a retry button. But the actual cause is a Zod validation error — the backend returned data, it just didn't match the schema. This is a developer bug masquerading as a user-facing error. The operator clicks "Retry" (line 944-947), gets the same data, gets the same parse failure, sees "Preview not found" again. Dead end.

After the Phase 1 schema fix, this specific failure should stop occurring. But the error handling pattern is still broken for ANY future schema drift.

**Fix Approach:**
1. In `getQuarantinePreview`, when `safeParse` fails, return a partial result using `.passthrough()` parsing instead of `null`. The operator sees degraded data instead of nothing.
2. Add a `schemaDrift` flag to the return type: `{ data: QuarantineItem; schemaDrift: boolean }`. When drift is detected, the UI shows a subtle amber banner: "Some fields could not be parsed — displaying available data."
3. Log the specific Zod error to console.warn for developer debugging.

Alternatively, simpler approach: use `QuarantineItemSchema.passthrough().safeParse(data)` so unknown fields are preserved rather than stripped, and the parse only fails on type mismatches (not missing fields, since all are `.nullable().optional()`).

**Industry Standard:**
Postel's Law: "Be conservative in what you send, be liberal in what you accept." Schema validation should degrade gracefully, showing what's available rather than showing nothing.

**System Fit:**
The `QuarantineItemSchema` already uses `.nullable().optional()` on every field, so a `safeParse` against it should almost never fail — the only failure case would be a field present with a completely wrong type (e.g., `confidence: "high"` instead of `confidence: 0.9`). Adding `.passthrough()` to the schema (as the mission already specifies) makes this even more robust.

**Enforcement:**
Add to Surface 9 A2 rules: "Zod parse failures for display data MUST degrade to partial rendering, not blank screens. Use `.passthrough()` and catch type errors per-field."

---

### Finding 11: Queue Performance at 200+ Items — No Virtualization, No Pagination

**Root Cause:**
`page.tsx:196-204` — `fetchData` requests `limit: 200` items. All 200 are rendered into the DOM at `page.tsx:776-854` (a `.map()` over all items). The `ScrollArea` provides scrolling but not virtualization — all 200 DOM nodes are rendered simultaneously.

Each list item renders: Checkbox, ConfidenceIndicator, subject text, sender text, 3 badges, date, delete button. That's ~15 DOM elements per item = 3,000 DOM nodes in the list alone, plus the detail panel.

At 200 items, initial render is noticeably slow (200-500ms on typical hardware). The mission's Phase 4 adds MORE content per list item (company name, triage summary snippet, broker badge) — increasing per-item DOM count from ~15 to ~20, totaling 4,000 DOM nodes.

**Fix Approach:**
This is a NICE-TO-HAVE for the current mission (200 items is manageable). But if the queue grows:
1. Use `@tanstack/react-virtual` to virtualize the list. Only render items in the viewport + a small overscan buffer.
2. Alternatively, add simple client-side pagination: show 50 items at a time with "Load more" button.
3. The mission should at minimum add a `TODO: virtualize list if queue exceeds 100 items` comment at the ScrollArea.

**Industry Standard:**
Gmail virtualizes its inbox list. Linear virtualizes issue lists. Any list that can exceed ~50 items should be virtualized for consistent performance.

**System Fit:**
The `ScrollArea` component from shadcn/ui wraps Radix ScrollArea. Replacing the inner `.map()` with `@tanstack/react-virtual`'s `useVirtualizer` hook is a contained change that doesn't affect the rest of the page.

**Enforcement:**
NICE-TO-HAVE for current mission. Add as backlog item.

---

### Finding 12: Sender Intelligence Fetch Needs Null-Safe Email Extraction

**Root Cause:**
The mission's P3-01 says the sender intelligence fetch fires when `selectedItem?.sender` changes. But looking at the backend endpoint at `main.py:2041`:
```python
sender_email: str = Query(..., description="Sender email to analyze")
```

The `sender` field on `QuarantineItem` can be `null` or missing (it's `.nullable().optional()` at `api.ts:182`). If the selected item has `sender: null` but `from: "broker@example.com"`, the sender intelligence fetch either fires with `null` (400 error) or doesn't fire at all (missing data).

The page already has this pattern at line 873: `selectedItem.sender_name || selectedItem.sender || selectedItem.from || 'Unknown'` — it falls back through multiple fields for display. But the mission's sender intelligence fetch doesn't specify the same fallback chain for the API call.

**Fix Approach:**
The `getSenderIntelligence()` call should use: `selectedItem?.sender || selectedItem?.from || null`. If both are null, skip the fetch entirely (don't fire a request with an empty/null email). Add this as a guard in the useEffect:
```typescript
const senderEmail = selectedItem?.sender || selectedItem?.from;
if (!senderEmail) { setSenderIntel(null); return; }
```

**Industry Standard:**
Defensive API calling — never send null/undefined as a required query parameter. Always validate inputs before making network requests.

**System Fit:**
The `QuarantineItem` type has both `sender` and `from` fields (historical: `from` is from the old email_sync schema, `sender` is from the new LangSmith schema). The fallback chain ensures both legacy and new items trigger sender intelligence lookups.

**Enforcement:**
TypeScript strict null checks should catch this if `getSenderIntelligence` signature requires `string` (not `string | null`). Add explicit guard in the fetch useEffect.

---

### Finding 13: Batch Triage Optimization — Same-Broker Grouping Missing

**Root Cause:**
`page.tsx:79-103` — The sort options are: received_at, confidence, urgency, created_at. There's no option to group or sort by `broker_name` or `sender`. When the Pipeline A agent processes 14 emails (as documented in the mission context), several may come from the same broker for different deals. An operator triaging a batch of 5 items from "John Smith at Founders Advisors" would benefit from seeing them grouped together — the first decision informs the rest.

**Fix Approach:**
Add `broker_name` and `sender` to the `SORT_OPTIONS` array at line 98-103:
```typescript
{ value: 'broker_name', label: 'Broker' },
{ value: 'sender', label: 'Sender' },
```

The backend list endpoint at `main.py:1698-1736` uses `ORDER BY {order_clause}` built from the sort parameter. It already selects `broker_name` and `sender`, so sorting by them should work without backend changes (assuming the endpoint accepts arbitrary column names for sorting — verify this).

More ambitiously: add a visual group separator in the list when sorted by broker/sender. Between items from different brokers, show a thin divider with the broker name. This is a Phase 4 enhancement.

**Industry Standard:**
Jira and Linear both allow grouping by assignee/reporter. Email clients group by sender in conversation view. CRM tools group activities by contact.

**System Fit:**
The filter/sort infrastructure at `page.tsx:125-131` and the `getQuarantineQueue` API call at line 196-204 already pass `sort_by` and `sort_order` to the backend. Adding new sort values is a 2-line frontend change + verification that the backend accepts them.

**Enforcement:**
SHOULD-ADD. Verify backend accepts `broker_name` and `sender` as sort columns before adding to frontend.

---

## ADJACENT OBSERVATIONS

### AO-1: Backend Detail Endpoint Returns `routing_conflict` from `raw_content` JSONB — Not a First-Class Column

At `main.py:2187-2189`, the detail endpoint reads:
```sql
COALESCE((q.raw_content->>'routing_conflict')::boolean, false) AS routing_conflict,
q.raw_content->'conflicting_deal_ids' AS conflicting_deal_ids,
q.raw_content->>'routing_reason' AS routing_reason
```

But the list endpoint at `main.py:1698-1730` does NOT select these routing fields. This means:
- `selectedItem` (from list data) has `routing_reason` in the Zod schema (line 212) but the list query doesn't populate it — so it's always `null` from list data.
- `preview` (from detail data) has `routing_conflict`, `conflicting_deal_ids`, `routing_reason`.

After schema unification, the routing conflict display at `page.tsx:958-996` reads from `preview.routing_conflict` — this will continue to work. But the routing_reason badge at line 883-901 reads from `selectedItem?.routing_reason` — this will be `null` from list data. The badge currently only works for items whose `routing_reason` happens to be populated from another source.

**Out of scope** — this is a backend query issue, not a dashboard issue.

### AO-2: `email_body_snippet` Truncation Not Enforced on the Frontend

The bridge at `server.py:880` says "First 500 chars of email body." But `email_body_snippet` has no length constraint in the Zod schema or the rendering. If the agent or a future pipeline sends 10,000 chars in this field, the EmailBodyCard (P2-08, designed to show "first 3 lines by default") would have its collapsed state contain an enormous amount of text.

**Out of scope** — this is a backend validation issue. Dashboard should add `max-h-24 overflow-hidden` to the collapsed state as a safety net.

### AO-3: No Rate Limiting on Sender Intelligence Endpoint

The `GET /api/quarantine/sender-intelligence` endpoint at `main.py:2039-2148` runs 4 separate SQL queries (rollup, sender profile, broker name count, deal associations). If the frontend fires this on every list item click without debounce (as noted in Finding 3), a fast-clicking operator could generate significant database load.

**Out of scope** — this is a backend performance concern. The frontend fix (debounce) mitigates this.

### AO-4: Deal Detail Page Pattern Uses Tabs — Quarantine Could Benefit from Tabs

The deal detail page at `deals/[id]/page.tsx` uses `Tabs` (TabsList/TabsTrigger/TabsContent) to organize content (Overview, Actions, Pipeline, Materials, etc.). The quarantine detail panel currently has no tabs — it's a single scrollable panel. As more cards are added (8 sections from the mission), the panel becomes very long. Consider organizing into 2 tabs: "Intelligence" (summary, signals, reasoning, entities) and "Raw Data" (email body, links, attachments).

**Out of scope** — architectural suggestion beyond the mission's scope.

---

## SUMMARY
- Total primary findings: 13
- Total adjacent observations: 4
- Confidence level: HIGH
- Key recommendation: The mission is well-structured but underestimates three critical UX concerns: (1) the approve dialog field mapping will break silently after schema unification (Finding 1 — MUST-FIX before P3), (2) the transition period where NO existing items have the new nested `extraction_evidence` format means every new component will show empty states for weeks until the agent deployment package is relayed (Finding 6 — MUST-DESIGN the dual-source fallback pattern), and (3) keyboard shortcuts are essential for the stated "3-second decision" goal (Finding 2 — MUST-ADD during execution).

### Impact Ranking (by operator decision speed improvement)

**MUST-ADD (before execution):**
1. Finding 1 — Approve dialog field mapping (breaks approve flow silently)
2. Finding 6 — Empty extraction_evidence dual-source fallback (every existing item shows empty cards)
3. Finding 7 — Legacy link format preservation (loses existing link data for old items)
4. Finding 4 — LangSmith traceability fields in Zod schema (loses agent provenance)
5. Finding 10 — Graceful parse degradation (prevents blank screens on future schema drift)
6. Finding 12 — Sender email null-safety (prevents 400 errors on legacy items)

**SHOULD-ADD (during execution):**
7. Finding 2 — Keyboard shortcuts (j/k/a/r for rapid triage)
8. Finding 3 — AbortController + debounce for stale fetch prevention
9. Finding 5 — Graduated visual confidence weighting on cards/borders
10. Finding 8 — Conflicting signal indicator (high urgency + low confidence)
11. Finding 13 — Broker/sender sort options for batch triage

**NICE-TO-HAVE (backlog):**
12. Finding 9 — Quick approve from list for high-confidence items
13. Finding 11 — List virtualization for 200+ items

### Report B (GEMINI)
# Gemini Agent — No Output
The Gemini agent did not produce output within the timeout.

### Report C (CODEX)
Could not write `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/01_pass1/codex_report.md` because this environment is read-only (`Permission denied`). Full report content is below.

# Pass 1 Report — CODEX
## Run: TP-20260218-095911 | Mode: design
## Generated: 2026-02-18T09:59:14Z

## PRIMARY FINDINGS

### Finding 1: [MUST-ADD] Preview Failure Root Cause Is Under-Specified
**Root Cause:** `getQuarantinePreview()` returns `null` on parse failure (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:952`, `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:955`). `QuarantinePreviewSchema` expects object-shaped `attachments` (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:241`), while backend detail emits list-shaped attachments (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:282`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2186`). Mission diagnosis emphasizes dropped fields (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:15`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:48`) but this type mismatch is a direct crash/degrade trigger.  
**Fix Approach:** Use a detail schema structurally aligned to backend `QuarantineResponse` and parse preview against that unified contract (with top-level `.passthrough()` and explicit legacy-field mapper).  
**Industry Standard:** Contract-first transport schema parity between API model and UI parser.  
**System Fit:** Backend already provides all data; this is dashboard parsing alignment only. This directly restores “open item and decide” speed.  
**Enforcement:** Add a contract-check test that compares frontend preview schema keys/types to backend `QuarantineResponse` fields and fails CI on drift.

### Finding 2: [MUST-ADD] P1 Unification Risks Breaking Thread-Conflict “Approve Into Deal”
**Root Cause:** Mission plans to switch preview parsing to `QuarantineItemSchema` (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:201`). The conflict UX depends on `preview.routing_conflict` and `preview.conflicting_deal_ids` (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:958`, `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:970`). `QuarantineItemSchema` omits those fields (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:175`). Mission explicitly says this flow must not regress (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:57`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:481`).  
**Fix Approach:** Include `routing_conflict` and `conflicting_deal_ids` in unified schema before removing `QuarantinePreviewSchema`; keep existing conflict card behavior intact during panel refactor.  
**Industry Standard:** Preserve exception-handling safety paths during UI schema migrations.  
**System Fit:** Backend already returns these fields (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2187`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2188`). This prevents wrong-deal approvals and speeds decisions.  
**Enforcement:** Add regression test fixture for routing conflict and assert “Approve into this deal” options render.

### Finding 3: [MUST-ADD] 3-Second Decision Goal Lacks Keyboard + Quick-Action Path
**Root Cause:** Mission objective is sub-second/seconds triage (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:12`), but current workflow is click row (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:802`) then use detail buttons (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:905`) and actions are disabled when preview absent (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:915`). No row-level quick approve/reject controls exist (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:777`). Undo API exists but is not surfaced in quarantine decision UX (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:1139`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:3076`).  
**Fix Approach:** Add keyboard triage (`J/K`, `A`, `R`, `E`), row quick actions for high-confidence items, and post-action undo affordance where role permits.  
**Industry Standard:** Keyboard-first triage patterns (Superhuman/Linear-style).  
**System Fit:** Reuses existing endpoints, no backend change. This materially cuts interaction cost per item.  
**Enforcement:** Playwright tests for hotkeys, focus handling, and quick-action latency path.

### Finding 4: [MUST-ADD] Async Race Can Show Wrong Context During Rapid Triage
**Root Cause:** Preview requests are not cancellation-safe (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:251`, `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:257`) and fire on selection changes (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:268`). Mission adds another selection-driven fetch for sender intelligence (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:283`) but does not define stale-response guards; only `Promise.allSettled` is mandated (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:79`).  
**Fix Approach:** Use request tokens or `AbortController` per `selectedId`; discard late responses for stale selection.  
**Industry Standard:** Race-safe state updates for operator-critical UIs.  
**System Fit:** Frontend-only behavior fix; avoids wrong-item decisions and rework.  
**Enforcement:** Add delayed-response test that rapidly switches items and asserts rendered preview/intel match active `selectedId`.

### Finding 5: [SHOULD-ADD] Data Trust UX Is Missing (Completeness + Contradictions)
**Root Cause:** UI shows raw confidence (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:923`) and field confidence list (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:1043`) but no quality/completeness score or contradiction signal. Mission card plan focuses on rendering extracted content (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:243`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:257`) and null safety (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:267`), not trust ergonomics.  
**Fix Approach:** Add compact “Signal Health” bar: completeness ratio, confidence band, and contradiction badges (e.g., `HIGH urgency` + low confidence).  
**Industry Standard:** AI assist tools surface uncertainty and evidence quality before decisions.  
**System Fit:** Uses existing `confidence`, `field_confidences`, `extraction_evidence`; no backend dependencies. Improves decision accuracy/speed under partial data.  
**Enforcement:** Component tests for empty/partial/conflicting fixtures with deterministic expected badges.

### Finding 6: [SHOULD-ADD] Provenance Fields Exist but Are Invisible to Operators
**Root Cause:** Bridge accepts provenance fields (`/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py:858`, `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py:968`), backend returns them (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:274`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:2180`), but quarantine frontend schema omits them (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:175`) and mission component list has no provenance surface (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:257`).  
**Fix Approach:** Add a minimal provenance block (trace URL, run ID, tool/prompt version, correlation ID copy).  
**Industry Standard:** High-trust AI decision interfaces expose source/provenance metadata inline.  
**System Fit:** Pure dashboard rendering + schema inclusion. Helps faster escalation when output looks wrong.  
**Enforcement:** Contract-checker rule for provenance keys in schema plus UI smoke test for trace-link rendering.

### Finding 7: [SHOULD-ADD] Classification Vocabulary Drift Can Break Filters
**Root Cause:** UI filter enums are uppercase legacy values (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:87`) while canonical/triage values are lowercase modern taxonomy (`/tmp/langsmith-export/canonical_output_schema.json:27`, `/tmp/langsmith-export/subagents/triage_classifier/AGENTS.md:17`, `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py:877`). Backend filter is exact match (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1631`).  
**Fix Approach:** Normalize classification values in dashboard API boundary and map to operator labels.  
**Industry Standard:** UI boundary normalization when producers emit multiple enum dialects.  
**System Fit:** Frontend-only mapping; avoids empty or misleading filter results and speeds queue narrowing.  
**Enforcement:** Unit tests for enum normalization and integration test verifying filter query values.

### Finding 8: [SHOULD-ADD] Comparison Workflow Is Missing Despite Existing Backend Support
**Root Cause:** Mission keeps scope on detail/list rendering (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:24`) and does not include “similar past decisions.” Backend already exposes sender decision history and corrections (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1753`, `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1762`). Current detail area has no historical comparison module (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:955`).  
**Fix Approach:** Add collapsible “Past Decisions from This Sender” card (last N outcomes + correction patterns) beside Sender Intel.  
**Industry Standard:** CRM/deal tooling improves operator consistency with adjacent historical context.  
**System Fit:** Uses existing endpoint; no backend change. Reduces repeat mistakes and decision hesitation.  
**Enforcement:** Add API parser + UI tests for non-empty and empty history states.

### Finding 9: [NICE-TO-HAVE] Queue Scaling and Baseline Filter Assumptions Are Misaligned
**Root Cause:** Frontend fetches max 200 (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:197`), backend also caps 200 (`/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py:1613`), and UI is single scroll list (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:775`). Mission claims status/sender/search filters are existing and must not regress (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:55`), but current filter row only exposes source/classification/urgency (`/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx:661`).  
**Fix Approach:** Add “Load more” pagination via offset, sender/status filter chips, and lightweight search over loaded rows.  
**Industry Standard:** Progressive loading + targeted filters for high-volume triage queues.  
**System Fit:** Uses existing backend query parameters (`/api/quarantine` already supports `offset`, `sender`, `status`). Improves throughput for large queues.  
**Enforcement:** Playwright scenario with >200 mocked rows validating pagination and filter behavior.

## ADJACENT OBSERVATIONS

- Mission references canonical schema at `/tmp/langsmith-export/schemas/canonical_output_schema.json` (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:31`), but available file is `/tmp/langsmith-export/canonical_output_schema.json`.
- Surface 9 requires reading frontend design skill before dashboard UI build work (`/home/zaks/zakops-agent-api/.claude/rules/design-system.md:13`); mission guardrails do not explicitly call this out.

## SUMMARY
- Total primary findings: 9
- Total adjacent observations: 2
- Confidence level: HIGH
- Key recommendation: Before execution, lock schema parity and race-safety, then add keyboard-first decision ergonomics plus trust/provenance surfaces so operators can act fast without sacrificing accuracy.

---

## Instructions

You are reviewing all three independent investigation reports. Your job is to:

1. **Identify duplicates** — findings that multiple agents reported (high confidence items)
2. **Identify conflicts** — findings where agents disagree on root cause or fix approach
3. **Identify unique findings** — items only one agent found (potential blind spot coverage)
4. **Verify evidence** — check that cited file:line references are accurate
5. **Flag drift** — note any findings that fall outside the declared mission scope

### Output Format

Write your cross-review to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/02_pass2/codex_review.md`

Begin with exactly this header:

```
# Pass 2 Cross-Review — CODEX
## Run: TP-20260218-095911 | Mode: design
## Generated: 2026-02-18T10:09:06Z
```

Then organize as:

```
## DUPLICATES (High Confidence)
Items found by 2+ agents. Merge into a single entry with attribution.

### D-1: [Merged Title]
**Reported by:** Agent A (Finding X), Agent B (Finding Y)
**Consensus root cause:** ...
**Consensus fix:** ...
**Evidence verified:** YES/NO

(repeat)

## CONFLICTS
Items where agents disagree. State both positions with evidence.

### C-1: [Conflict Title]
**Agent A position:** ...
**Agent B position:** ...
**Evidence comparison:** ...
**Recommended resolution:** ...

(repeat)

## UNIQUE FINDINGS
Items found by only one agent. Verify if the finding is valid.

### U-1: [Title] (from Agent X)
**Verification:** CONFIRMED / UNVERIFIED / INVALID
**Evidence check:** ...
**Should include in final:** YES / NO (with reason)

(repeat)

## DRIFT FLAGS
Findings that fall outside declared scope.

### DRIFT-1: [Title] (from Agent X)
**Why out of scope:** ...
**Severity if ignored:** ...

## SUMMARY
- Duplicates: N
- Conflicts: N
- Unique valid findings: N
- Drift items: N
- Overall assessment: ...
```
