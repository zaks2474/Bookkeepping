# Quarantine Intelligence — Phase Quick-Start Cards

**Roadmap:** `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md`
**Mission:** `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md`
**TriPass:** `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-095911/FINAL_MASTER.md`

**How to use:** Copy the relevant phase card into a new session as the opening prompt. The session reads the roadmap for full details and executes.

---

## Phase 0+1 — Schema Unification & Data Pipeline

> **Read first:**
> 1. `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md` (full roadmap)
> 2. `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (lines 170-260 for schemas, 940-965 for getQuarantinePreview)
> 3. `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
> 4. `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
>
> **Execute:** Roadmap Phase 0 (baseline) + Phase 1 (items 1-10).
>
> **The job:** Kill "Preview not found." Unify QuarantinePreviewSchema into QuarantineItemSchema. Add missing fields (routing_conflict, provenance, extraction_evidence typed schema). Fix approve dialog correction keys (company_guess→company_name, broker_email→broker_name). Add getSenderIntelligence() + getTriageFeedback() API functions. Normalize classification case at parse boundary. Graceful degradation on parse failure (never blank screen).
>
> **Files to modify:** `api.ts`, `page.tsx` (types only — no component integration yet)
>
> **Gate:** `npx tsc --noEmit` PASS. Click quarantine item → no "Preview not found." TriPass gates TG-1, TG-2, TG-11.
>
> **Commit:** `QUARANTINE-INTELLIGENCE-001 P1: Unify Zod schema, add sender intel API, fix correction keys`
>
> **Update:** Roadmap Phase 1 status → COMPLETE, CHANGES.md entry.

---

## Phase 2 — Triage Intelligence Components

> **Read first:**
> 1. `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md` — Phase 2 (items 11-24)
> 2. `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` (InfoGrid, Card, Collapsible patterns)
> 3. `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/ConfidenceIndicator.tsx`
> 4. `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
> 5. `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` (lines 247-286 for QuarantineResponse fields)
>
> **Execute:** Roadmap Phase 2 (items 11-24).
>
> **The job:** Build 10 new components in `apps/dashboard/src/components/quarantine/`: format-utils, TriageSummaryCard (+ conflicting signals warning), DealSignalsCard (dual-source pattern), ClassificationReasoningCard, MaterialsAndLinksCard (3-tier: typed_links → flat array → legacy groups), EntitiesCard, SenderIntelCard (+ past decisions), EmailBodyCard, ProvenanceFooter, TriageIntelPanel (orchestrator). Every component must handle null/empty/flat-legacy/rich-nested data. Three visual states: null → "Not available", empty → "No signals detected", partial → render what's there. Graduated confidence visuals (border tinting by band).
>
> **Files to create:** 10 files in `apps/dashboard/src/components/quarantine/`
>
> **Gate:** `npx tsc --noEmit` PASS. All components compile. Each handles null extraction_evidence without crashing. TriPass gates TG-4, TG-5, TG-7.
>
> **Commit:** `QUARANTINE-INTELLIGENCE-001 P2: Build triage intelligence components (10 files)`
>
> **Update:** Roadmap Phase 2 status → COMPLETE, CHANGES.md entry.

---

## Phase 3 — Page Integration & Decision Safety

> **Read first:**
> 1. `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md` — Phase 3 (items 25-35)
> 2. `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` (current state after P1)
> 3. `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/TriageIntelPanel.tsx` (built in P2)
>
> **Execute:** Roadmap Phase 3 (items 25-35).
>
> **The job:** Wire TriageIntelPanel into the quarantine detail panel. Add sender intel + triage feedback fetches with null-safe email extraction (fallback sender→from). Add AbortController to cancel stale fetches on rapid item switching. Replace detail panel content (~lines 928-1090) with TriageIntelPanel. Enhance header (classification badge, deal_stage_hint, confidence border). Fix approve dialog to read from unified item fields. Add undo toast after approve/reject (calls existing undoQuarantineApproval). Remove old renderLinkGroups/renderAttachments helpers. Verify ALL action handlers still work. Verify routing conflict flow. Verify graceful degradation on parse drift.
>
> **Files to modify:** `page.tsx`
>
> **Gate:** All actions work (approve, approve-into-deal, reject, escalate, delegate, bulk, delete). Browser verification at localhost:3003/quarantine. TriPass gates TG-3, TG-6, TG-8, TG-10.
>
> **Commit:** `QUARANTINE-INTELLIGENCE-001 P3: Integrate triage intel panel, AbortController, undo toast`
>
> **Update:** Roadmap Phase 3 status → COMPLETE, CHANGES.md entry.

---

## Phase 4 — Queue Enhancement & Rapid Triage

> **Read first:**
> 1. `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md` — Phase 4 (items 36-42)
> 2. `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` (current state after P3)
>
> **Execute:** Roadmap Phase 4 (items 36-42).
>
> **The job:** Enhance list items: add company_name (muted), triage_summary snippet (80 chars), broker badge. Visual hierarchy: subject (bold) → sender + broker → company + summary. Add keyboard shortcuts (j/k navigate, a approve, r reject, e escalate, d delegate, x bulk-select, Escape close, Enter confirm). Guards: no-fire when dialog open or input focused. Quick approve button on high-confidence items (≥0.85, deal_signal, is_broker). Confidence-based list item visual weight (low = larger badge, high = green border).
>
> **Files to modify:** `page.tsx` (list section + keyboard handler)
>
> **Gate:** `npx tsc --noEmit` PASS. List shows 4-tier hierarchy. Keyboard j/k/a works. No layout overflow. TriPass gate TG-9.
>
> **Commit:** `QUARANTINE-INTELLIGENCE-001 P4: Queue list enhancement + keyboard shortcuts`
>
> **Update:** Roadmap Phase 4 status → COMPLETE, CHANGES.md entry.

---

## Phase 5 — Agent Deployment Package

> **Read first:**
> 1. `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md` — Phase 5 (items 43-45)
> 2. `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (ExtractionEvidenceSchema — the Zod source of truth)
> 3. `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` (lines 832-1039 for zakops_inject_quarantine params)
>
> **Execute:** Roadmap Phase 5 (items 43-45).
>
> **The job:** Write EXTRACTION_EVIDENCE_SCHEMA.md (TypeScript interface + JSON Schema, field definitions, enums, validation rules, 3 example payloads). Write AGENT_EXTRACTION_EVIDENCE_DEPLOYMENT.md (priority fields, pipeline stage mapping, full injection example, verification checklist). Copy both to Windows Downloads for agent relay.
>
> **Files to create:** 2 docs in bookkeeping/docs/, copies in /mnt/c/Users/mzsai/Downloads/
>
> **Gate:** Documents are self-contained and internally consistent. Examples match the Zod schema in api.ts.
>
> **Commit:** `QUARANTINE-INTELLIGENCE-001 P5: extraction_evidence schema + agent deployment package`
>
> **Update:** Roadmap Phase 5 status → COMPLETE, CHANGES.md entry.

---

## Phase 6 — Validation & Bookkeeping

> **Read first:**
> 1. `/home/zaks/bookkeeping/docs/QUARANTINE-INTELLIGENCE-ROADMAP.md` — Phase 6 (items 46-52)
>
> **Execute:** Roadmap Phase 6 (items 46-52).
>
> **The job:** Full validation sweep. `npx tsc --noEmit`. `make validate-local`. `make validate-surface9 && make validate-surface17`. Browser verification: (1) rich item with extraction_evidence → all cards render, (2) bare item without → graceful degradation, (3) all actions work, (4) keyboard shortcuts work, (5) undo toast works. CRLF/ownership fix on new files. Update CHANGES.md. Write completion report. Update roadmap statuses.
>
> **Gate:** All 13 AC met. All 11 TriPass gates pass. `make validate-local` exits 0. Browser verified.
>
> **Commit:** `QUARANTINE-INTELLIGENCE-001 P6: Validation + bookkeeping`
>
> **Final commit:** `QUARANTINE-INTELLIGENCE-001: World-class quarantine decision support — complete`
>
> **Update:** Roadmap all phases → COMPLETE. CHANGES.md final entry. Completion report written.

---

## Session Protocol

Every phase session should:

1. **Start:** Read the roadmap, read the quick-start card, run `make infra-check`
2. **Execute:** Follow the items in order
3. **Gate:** Pass the phase gate before stopping
4. **Record:** Update roadmap status, CHANGES.md entry, commit with phase message
5. **Handoff:** Note any deviations or discoveries for the next phase

If a phase session runs out of context mid-phase, commit intermediate work and note where to resume in CHANGES.md.
