# TriPass — Pass 4: Meta-QA Verification

## Agent Identity
**Agent**: CLAUDE (Meta-QA) (Meta-QA Auditor)
**Run ID**: TP-20260218-095911
**Pipeline Mode**: design
**Timestamp**: 2026-02-18T10:26:39Z

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

## Your Task

You are the quality assurance auditor for this TriPass pipeline run. You have access to:
- All Pass 1 reports (3 independent investigations)
- All Pass 2 cross-reviews (3 cross-reviews)
- The FINAL_MASTER.md (consolidated deliverable from Pass 3)
- WORKSPACE.md (append-only evidence trail)
- EVIDENCE/ directory (hashes, gate results)

Your job is to verify the quality and completeness of the consolidation.

---

## QA Checks (All Must Pass)

### Check 1: No-Drop Verification
For every unique finding in each Pass 1 report, verify it appears in FINAL_MASTER.md as one of:
- A primary finding (section: CONSOLIDATED FINDINGS)
- A merged/deduplicated item (with attribution to all sources)
- An explicitly discarded item (section: DISCARDED ITEMS, with documented reason)

**Verdict:** PASS if all findings are accounted for. FAIL if any finding is silently missing.

### Check 2: Deduplication Correctness
For every merged item in FINAL_MASTER.md, verify:
- The source attributions are correct (the cited Pass 1 findings actually exist)
- The merged root cause accurately represents the original findings
- No information was lost in the merge

**Verdict:** PASS if all merges are correct. FAIL if any merge lost information.

### Check 3: Evidence Presence
For every primary finding in FINAL_MASTER.md, verify:
- All 5 required fields are present (root cause, fix, standard, system fit, enforcement)
- File:line citations exist and are plausible
- No finding relies solely on assertion without evidence

**Verdict:** PASS if all findings have evidence. FAIL if any finding lacks evidence.

### Check 4: Gate Enforceability
For every acceptance gate in FINAL_MASTER.md, verify:
- The gate command is a real, executable command
- The pass criteria are objective and machine-verifiable
- The gate would actually catch a regression if the fix were reverted

**Verdict:** PASS if all gates are enforceable. FAIL if any gate is subjective or untestable.

### Check 5: Scope Compliance
Verify that no primary finding in FINAL_MASTER.md falls outside the declared mission scope. Drift items must be in the DRIFT LOG section only.

**Verdict:** PASS if scope is clean. FAIL if primary findings include out-of-scope items.

---

## Output Format

Write your QA verdict to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/04_metaqa/METAQA.md`

Begin with exactly this header:

```
# Meta-QA Verdict — TP-20260218-095911
## Generated: 2026-02-18T10:26:39Z
```

Then:

```
## CHECK RESULTS

| Check | Verdict | Details |
|-------|---------|---------|
| 1. No-Drop | PASS/FAIL | ... |
| 2. Dedup Correctness | PASS/FAIL | ... |
| 3. Evidence Presence | PASS/FAIL | ... |
| 4. Gate Enforceability | PASS/FAIL | ... |
| 5. Scope Compliance | PASS/FAIL | ... |

## OVERALL VERDICT: PASS / FAIL

## BLOCKERS (if FAIL)
(list specific issues that must be fixed)

## OBSERVATIONS
(non-blocking quality notes)
```

---
## FINAL_MASTER.md Content
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

## Full Workspace
# TriPass Workspace — TP-20260218-095911

---
## Pass 1 — CLAUDE Report
---
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
{item.confidence != null && (
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
- If `urgency === 'HIGH' && confidence < 0.5`: Show amber alert: "High urgency flagged but confidence is low — review reasoning carefully"
- If `urgency === 'LOW' && confidence > 0.9`: Show info note: "High confidence — consider expediting despite low urgency flag"

This is a simple conditional render, not a new component. Place it between the confidence bar and match_factors in TriageSummaryCard.

**Industry Standard:**
Medical alert systems (Epic BPA) explicitly flag when multiple risk signals conflict. ISO 9241-171 for accessibility in decision support recommends "explicit disambiguation when automated signals contradict."

**System Fit:**
Both `urgency` and `confidence` are already on `QuarantineItem` (flat fields from list data). The conditional is trivial: `if (item.urgency === 'HIGH' && (item.confidence ?? 1) < 0.5)`.

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


---
## Pass 1 — GEMINI Report
---
# Gemini Agent — No Output
The Gemini agent did not produce output within the timeout.


---
## Pass 1 — CODEX Report
---
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
## Pass 2 — CLAUDE Cross-Review
---
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


---
## Pass 2 — GEMINI Cross-Review
---
# Gemini Agent — No Output
The Gemini agent did not produce output within the timeout.


---
## Pass 2 — CODEX Cross-Review
---
Could not write `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/02_pass2/codex_review.md` because the environment is read-only (`Permission denied`).  
Prepared report content:

```markdown
# Pass 2 Cross-Review — CODEX
## Run: TP-20260218-095911 | Mode: design
## Generated: 2026-02-18T10:09:06Z

## DUPLICATES (High Confidence)
Items found by 2+ agents. Merge into a single entry with attribution.

### D-1: Preview Parse Failures Caused by Schema Mismatch and Hard Null Fallback
**Reported by:** Agent A (Finding 10), Agent C (Finding 1)
**Consensus root cause:** The detail endpoint response is parsed with `QuarantinePreviewSchema`, which is structurally out of sync with backend `QuarantineResponse`; parse failure returns `null`, which surfaces as "Preview not found." The most concrete mismatch is `attachments` shape (`record` expected vs `list` returned).
**Consensus fix:** Parse detail responses against a unified `QuarantineItem` contract aligned to backend fields, then degrade gracefully on partial parse issues instead of returning `null`.
**Evidence verified:** YES (`apps/dashboard/src/lib/api.ts:228`, `apps/dashboard/src/lib/api.ts:241`, `apps/dashboard/src/lib/api.ts:952`, `apps/dashboard/src/lib/api.ts:955`, `apps/backend/src/api/orchestration/main.py:282`, `apps/backend/src/api/orchestration/main.py:2186`)

### D-2: 3-Second Triage Goal Needs Keyboard-First and Quick-Action Paths
**Reported by:** Agent A (Findings 2, 9), Agent C (Finding 3)
**Consensus root cause:** Current flow is click-heavy (select row, open dialog, confirm) and lacks keyboard shortcuts or list-level fast actions.
**Consensus fix:** Add keyboard triage (`j/k`, approve/reject hotkeys, escape handling) and optional high-confidence row quick action(s), with focus guards.
**Evidence verified:** YES (`apps/dashboard/src/app/quarantine/page.tsx:802`, `apps/dashboard/src/app/quarantine/page.tsx:905`, `apps/dashboard/src/app/quarantine/page.tsx:915`)

### D-3: Selection-Driven Fetches Are Race-Prone Without Cancellation
**Reported by:** Agent A (Finding 3), Agent C (Finding 4)
**Consensus root cause:** Preview loading on `selectedId` changes has no cancellation/staleness guard; mission adds sender-intelligence fetch on selection changes without explicit stale-response protection.
**Consensus fix:** Use `AbortController` or request tokens for each selection cycle and ignore late responses for non-active selection.
**Evidence verified:** YES (`apps/dashboard/src/app/quarantine/page.tsx:251`, `apps/dashboard/src/app/quarantine/page.tsx:268`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:283`)

### D-4: Provenance Fields Flow Through Backend/Bridge but Are Dropped in Dashboard Schema
**Reported by:** Agent A (Finding 4), Agent C (Finding 6)
**Consensus root cause:** Backend and bridge expose LangSmith provenance fields, but `QuarantineItemSchema` omits them, so frontend parsing strips them.
**Consensus fix:** Add provenance fields to `QuarantineItemSchema` and render minimal trace/version metadata in detail UX.
**Evidence verified:** YES (`apps/backend/src/api/orchestration/main.py:274`, `apps/backend/src/api/orchestration/main.py:2179`, `apps/agent-api/mcp_bridge/server.py:858`, `apps/dashboard/src/lib/api.ts:175`)

### D-5: Data-Trust Ergonomics for Low/Conflicting Signals Are Underdeveloped
**Reported by:** Agent A (Findings 5, 8), Agent C (Finding 5)
**Consensus root cause:** Confidence is shown, but there is no explicit quality/completeness/conflict framing when signals disagree (for example high urgency with low confidence).
**Consensus fix:** Add compact signal-health and conflict indicators tied to confidence and urgency context.
**Evidence verified:** YES (`apps/dashboard/src/app/quarantine/page.tsx:816`, `apps/dashboard/src/app/quarantine/page.tsx:921`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:243`)

### D-6: Queue Throughput Risks at 200-Item Cap and Non-Virtualized Rendering
**Reported by:** Agent A (Finding 11), Agent C (Finding 9)
**Consensus root cause:** UI fetches up to 200 and renders full list with no virtualization/pagination; current filter row also omits some backend-supported narrowing controls.
**Consensus fix:** Add progressive loading/virtualization and expose missing narrowing controls as a separate scope item.
**Evidence verified:** YES (`apps/dashboard/src/app/quarantine/page.tsx:196`, `apps/dashboard/src/app/quarantine/page.tsx:775`, `apps/backend/src/api/orchestration/main.py:1613`, `apps/backend/src/api/orchestration/main.py:1616`)

## CONFLICTS
Items where agents disagree. State both positions with evidence.

### C-1: “Preview Not Found” Primary Root Cause Framing
**Agent A position:** The key operator-facing problem is hard failure behavior (parse failure => `null` => generic "Preview not found") and missing graceful degradation.
**Agent C position:** The immediate concrete break is contract mismatch (notably `attachments` type), so schema parity is the first-order fix.
**Evidence comparison:** Both are supported: mismatch exists (`api.ts:241` vs `main.py:282`), and failure handling is hard-null (`api.ts:952-955`).
**Recommended resolution:** Treat as layered fix, in order: (1) contract parity/unification; (2) fail-soft rendering on parse drift.

### C-2: Broker/Sender Sort Recommendation vs Actual Backend Sort Contract
**Agent A position:** Add `broker_name`/`sender` sort options to improve same-broker triage.
**Agent C position:** Queue assumptions are already misaligned; backend contract is restrictive.
**Evidence comparison:** Backend `valid_sorts` only allows `received_at`, `urgency`, `confidence`, `created_at` (`main.py:1674`), so broker/sender sort is not currently accepted.
**Recommended resolution:** Do not ship as frontend-only change; move to backlog requiring explicit backend contract extension (outside current mission fence).

## UNIQUE FINDINGS
Items found by only one agent. Verify if the finding is valid.

### U-1: Approve Dialog Sends Stale/Incorrect Correction Keys (from Agent A)
**Verification:** CONFIRMED
**Evidence check:** Dialog keys are `company_guess`, `broker_email`, `asking_price` and source from `preview.extracted_fields` (`apps/dashboard/src/app/quarantine/page.tsx:1156`, `apps/dashboard/src/app/quarantine/page.tsx:1160`). Backend promotion logic consumes `company_name`, `broker_name`, `broker_email` (`apps/backend/src/api/orchestration/main.py:2809`, `apps/backend/src/api/orchestration/main.py:2816`, `apps/backend/src/api/orchestration/main.py:2819`).
**Should include in final:** YES (silent correction loss directly hurts decision accuracy)

### U-2: Extraction Evidence Needs Explicit Null/Empty/Legacy Flat Handling (from Agent A)
**Verification:** CONFIRMED
**Evidence check:** Bridge accepts free-form optional dict (`apps/agent-api/mcp_bridge/server.py:852`), and existing golden payload uses flat evidence (`apps/agent-api/scripts/test_golden_injection.py:45`). Mission requires backward compatibility for empty/null evidence (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:452`).
**Should include in final:** YES (prevents blank/ambiguous cards on mixed historical data)

### U-3: Legacy `links.groups` Fallback Preservation (from Agent A)
**Verification:** UNVERIFIED
**Evidence check:** Current helper expects legacy grouped links (`apps/dashboard/src/app/quarantine/page.tsx:1421`), but backend detail query does not currently return a `links` field (`apps/backend/src/api/orchestration/main.py:2155`). Existing DB prevalence of `links.groups` in this path is not proven by code alone.
**Should include in final:** NO (keep as test-fixture check, not a blocking requirement)

### U-4: Sender-Intelligence Fetch Must Fallback `sender || from` and Skip Empty (from Agent A)
**Verification:** CONFIRMED
**Evidence check:** Mission task references `selectedItem?.sender` fetch trigger (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:283`), while UI already uses `sender || from` fallback for display (`apps/dashboard/src/app/quarantine/page.tsx:782`, `apps/dashboard/src/app/quarantine/page.tsx:873`). Endpoint requires non-empty `sender_email` query (`apps/backend/src/api/orchestration/main.py:2041`).
**Should include in final:** YES (avoids avoidable request errors on legacy records)

### U-5: Schema Unification Can Regress Thread-Conflict Approval Flow (from Agent C)
**Verification:** CONFIRMED
**Evidence check:** Conflict UI depends on `preview.routing_conflict` and `preview.conflicting_deal_ids` (`apps/dashboard/src/app/quarantine/page.tsx:958`, `apps/dashboard/src/app/quarantine/page.tsx:970`), but `QuarantineItemSchema` currently omits these fields (`apps/dashboard/src/lib/api.ts:175`). Backend detail returns both (`apps/backend/src/api/orchestration/main.py:2187`, `apps/backend/src/api/orchestration/main.py:2188`).
**Should include in final:** YES (mission explicitly says this flow must not regress)

### U-6: Classification Enum Dialect Drift Can Break Filtering (from Agent C)
**Verification:** CONFIRMED
**Evidence check:** UI filter uses uppercase legacy values (`apps/dashboard/src/app/quarantine/page.tsx:86`), backend classification filter is exact-match (`apps/backend/src/api/orchestration/main.py:1631`), and canonical schema uses lowercase values (`/tmp/langsmith-export/canonical_output_schema.json:27`).
**Should include in final:** YES (directly impacts queue narrowing and operator speed)

### U-7: Comparison Workflow Is Missing Despite Existing Feedback Endpoint (from Agent C)
**Verification:** CONFIRMED
**Evidence check:** Backend sender feedback API exists (`apps/backend/src/api/orchestration/main.py:1753`), but quarantine dashboard client/page has no feedback fetch/render path (`apps/dashboard/src/lib/api.ts`, `apps/dashboard/src/app/quarantine/page.tsx`).
**Should include in final:** YES (as SHOULD-ADD/backlog; improves consistency decisions)

### U-8: Mission Source Path for Canonical Schema Is Stale (from Agent C)
**Verification:** CONFIRMED
**Evidence check:** Mission references `/tmp/langsmith-export/schemas/canonical_output_schema.json` (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:31`), but available file is `/tmp/langsmith-export/canonical_output_schema.json`.
**Should include in final:** YES (documentation hygiene; prevents executor confusion)

## DRIFT FLAGS
Findings that fall outside declared scope.

### DRIFT-1: Quick Approve/Undo Workflow Expansion (from Agent A Finding 9, Agent C Finding 3)
**Why out of scope:** Mission fences list/filter/action architecture redesign and emphasizes preserving existing handlers (`/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:24`, `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md:481`).
**Severity if ignored:** MEDIUM (throughput gain deferred, but mission ACs remain attainable)

### DRIFT-2: Pagination/Virtualization Queue Refactor (from Agent A Finding 11, Agent C Finding 9)
**Why out of scope:** This is queue architecture/performance redesign, not detail-panel/list-signal rendering.
**Severity if ignored:** LOW to MEDIUM (performance risk emerges mainly at sustained high queue sizes)

### DRIFT-3: Broker/Sender Sort + Grouping (from Agent A Finding 13)
**Why out of scope:** Requires backend sort-contract changes (`valid_sorts` restriction) and exceeds dashboard-only mission fence.
**Severity if ignored:** LOW (operator grouping convenience deferred)

### DRIFT-4: Design-System Rulebook Amendments as Deliverable (from Agent A enforcement notes)
**Why out of scope:** Mission execution scope is product UI/data behavior, not governance-document updates.
**Severity if ignored:** LOW (no direct runtime impact)

## SUMMARY
- Duplicates: 6
- Conflicts: 2
- Unique valid findings: 7
- Drift items: 4
- Overall assessment: High convergence on schema parity, race safety, provenance visibility, and fast triage ergonomics. The most critical pre-execution blockers are correction-key drift, routing-conflict field parity, and classification enum normalization; most remaining items are scoped enhancements or backlog candidates.
```

