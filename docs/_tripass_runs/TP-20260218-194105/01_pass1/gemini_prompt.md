# TriPass — Pass 1: Independent Investigation

## Agent Identity
**Agent**: GEMINI
**Run ID**: TP-20260218-194105
**Pipeline Mode**: design
**Timestamp**: 2026-02-18T19:41:07Z

---

## Mission

# TriPass Investigation Mission: DEAL-EVIDENCE-PIPELINE-001 Adversarial Review

## Objective
Adversarial review of the DEAL-EVIDENCE-PIPELINE-001 mission plan. The plan fixes data loss when quarantine items are approved into deals — the backend approve endpoint doesn't map extraction_evidence fields (financials, broker details, entities) into the deal's JSONB columns.

## Source Artifacts
1. Implementation plan: `/root/.claude/plans/ethereal-prancing-cascade.md`
2. Backend approve endpoint: `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` (lines 2788-2871)
3. Dashboard DealDetailSchema: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (lines 101-139)
4. Deal page rendering: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` (lines 497-600)
5. Extraction evidence schema: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (lines 209-226)

## Investigation Lenses

### Lens 1: Data Fidelity {{MISSION_DESCRIPTION}} Mapping Completeness
- Are ALL extraction_evidence fields that the dashboard renders accounted for in the mapping?
- Are there fields the dashboard expects but the plan doesn't map?
- What happens when extraction_evidence has partial data (some fields null)?
- Does the priority hierarchy (corrections > flat > evidence > default) cover all edge cases?

### Lens 2: Currency {{MISSION_DESCRIPTION}} Type Coercion Risks
- The plan proposes `_parse_currency()` — what edge cases could break it? ("$2.5M", "2,500,000", "TBD", null, "N/A")
- What about the `multiple` field (e.g., "4.2x" vs 4.2)?
- What about revenue_range ("1M-5M") — does the dashboard handle this?
- Type mismatch risks: backend stores float, dashboard expects coercedNumber — any gaps?

### Lens 3: Backfill Safety
- The SQL backfill uses JSONB `||` merge — does this overwrite existing non-null values?
- What if a deal was manually edited after approval (operator set asking_price manually)?
- What if the quarantine item was deleted or has no extraction_evidence?
- Should the backfill be wrapped in a transaction? What's the rollback strategy?

### Lens 4: Regression {{MISSION_DESCRIPTION}} Side Effects
- Does modifying the approve endpoint break any existing tests?
- Does adding `.passthrough()` to DealDetailSchema break any TypeScript consumers?
- Does the bulk approve endpoint (`bulk-process`) have the same data loss bug?
- What about the "attach to existing deal" path (thread match found) — does it also lose data?

### Lens 5: Missing Workflows
- What about deals NOT created from quarantine? (manual deals, imported deals) — do they need the same enrichment?
- What about deal stage transitions — when a deal moves from inbound to screening, is extraction_evidence preserved?
- What about the undo-approve flow — if someone undoes an approval, is the deal metadata cleaned up?
- What about re-approval — if the same quarantine item is re-processed, does it double-write?

### Lens 6: Contract Surface Compliance
- Does the plan correctly identify all affected contract surfaces?
- Does `make validate-local` catch any of the changes?
- Does the backfill script need to be validated against surface 16?
- Are there any generated file protections that could block the backend edit?

## Acceptance Gates (TriPass)
- TG-1: Every extraction_evidence field that appears in DealDetailSchema is mapped
- TG-2: _parse_currency handles at least 5 documented edge cases
- TG-3: Backfill script is idempotent and non-destructive
- TG-4: Bulk approve path is also fixed (or explicitly flagged as out-of-scope)
- TG-5: No regression in existing deal creation from manual/non-quarantine sources
- TG-6: Thread-match (attach to existing deal) path is addressed

## Scope

As defined in the mission document

## Repository Roots

/home/zaks/zakops-agent-api

## Known Issues or Constraints

V5PP guardrails apply. No production code modifications.

---

## Instructions

You are one of three independent investigators analyzing this mission. Your report will be cross-reviewed by two other agents in Pass 2. No other agent can see your work during this pass.

### Investigation Protocol

1. **Read first, opine second.** Read every relevant file before forming conclusions. Cite file paths and line numbers for every claim.
2. **Stay in scope.** If you discover issues outside the declared mission scope, place them in the ADJACENT OBSERVATIONS section — never mix them with primary findings.
3. **Structure every finding** with these 5 required fields:
   - **(1) Confirmed Root Cause** — What is the actual problem, with file:line evidence?
   - **(2) Permanent Fix Approach** — What specific change resolves it?
   - **(3) Industry Standard / Best Practice** — What standard or pattern does this align with?
   - **(4) Why It Fits This System** — Why is this the right fix for THIS codebase specifically?
   - **(5) Never-Again Enforcement** — What gate, lint rule, hook, or test prevents recurrence?
4. **Be concrete.** "The middleware should validate input" is not a finding. "middleware.ts:47 accepts unsanitized query params — add zod schema validation" is a finding.

### Output Format

Write your report to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/01_pass1/gemini_report.md`

Begin your report with exactly this header:

```
# Pass 1 Report — GEMINI
## Run: TP-20260218-194105 | Mode: design
## Generated: 2026-02-18T19:41:07Z
```

Then organize findings as:

```
## PRIMARY FINDINGS

### Finding 1: [Title]
**Root Cause:** ...
**Fix Approach:** ...
**Industry Standard:** ...
**System Fit:** ...
**Enforcement:** ...

### Finding 2: ...
(repeat for each finding)

## ADJACENT OBSERVATIONS
(out-of-scope items go here, clearly labeled)

## SUMMARY
- Total primary findings: N
- Total adjacent observations: N
- Confidence level: HIGH / MEDIUM / LOW
- Key recommendation: (one sentence)
```
