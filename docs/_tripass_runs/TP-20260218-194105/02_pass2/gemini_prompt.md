# TriPass — Pass 2: Cross-Review and Deduplication

## Agent Identity
**Agent**: GEMINI
**Run ID**: TP-20260218-194105
**Pipeline Mode**: design
**Timestamp**: 2026-02-18T19:50:03Z

---

## Mission (Original)

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

---

## Pass 1 Reports

You have access to all three Pass 1 reports:

### Report A (CLAUDE)
Pass 1 report is complete. Here's the summary:

## Pass 1 Report Written

**Location:** `docs/_tripass_runs/TP-20260218-194105/01_pass1/claude_report.md`
(Needs to be copied to `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/01_pass1/claude_report.md` — sandbox restriction prevented direct write)

### 8 Primary Findings:

1. **Single-item approve drops all extraction_evidence** — metadata, broker, company_info get minimal data despite extraction_evidence being available (`SELECT *`)
2. **Bulk approve is worse** — doesn't even SELECT extraction_evidence, writes empty `{}` for company_info and broker
3. **Thread-linked path doesn't enrich existing deals** — attaches as timeline event but never merges extraction data into the deal
4. **coerceToNumber fails on "$2.5M"/"$500K"** — `parseFloat("2.5M")` returns `2.5`, off by 6 orders of magnitude
5. **Bulk approve skips thread deduplication** — always creates new deals, can produce duplicates
6. **DealDetailSchema strips unknown fields** — no `.passthrough()` on metadata/broker/company_info sub-schemas
7. **revenue and multiple are schema-defined but never rendered** in the deal UI
8. **Backfill JSONB `||` overwrites operator edits** — must use null-conditional merge

### 6 Adjacent Observations (out of scope):
- state_machine contract mismatch, bulk audit trail inconsistency, PATCH full-replace risk, missing location population path, OpenAPI schema gaps, zero test coverage for quarantine-to-deal data flow

### Acceptance Gate Status:
- TG-1 (field mapping): PARTIAL RISK
- TG-2 (currency parsing): AT RISK
- TG-3 (backfill safety): AT RISK
- TG-4 (bulk approve): BLOCKED
- TG-5 (manual deals): PASS
- TG-6 (thread-match): PARTIAL

### Report B (GEMINI)
I will list the files in `/root/.claude/plans/` to confirm the location of the plan, and also list the files in the current working directory to get a better sense of the structure.
I will read the content of the plan file `/root/.claude/plans/ethereal-prancing-cascade.md`.

### Report C (CODEX)
Could not write `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/01_pass1/codex_report.md` in this environment (`Permission denied` due read-only filesystem). Full report content:

# Pass 1 Report — CODEX
## Run: TP-20260218-194105 | Mode: design
## Generated: 2026-02-18T19:41:07Z

## PRIMARY FINDINGS

### Finding 1: Bulk approve path still drops extraction evidence (TG-4 fail)
**Root Cause:** The bulk endpoint creates deals with empty `company_info`/`broker` and minimal `metadata`, and never selects `extraction_evidence` from quarantine rows. Evidence: `apps/backend/src/api/orchestration/main.py:2591`, `apps/backend/src/api/orchestration/main.py:2624`, `apps/backend/src/api/orchestration/main.py:2627`, `apps/backend/src/api/orchestration/main.py:2631`. The mission plan only scopes backend changes to the single approve block (`process_quarantine`) and does not include bulk path remediation. Evidence: `/root/.claude/plans/ethereal-prancing-cascade.md:50`, `/root/.claude/plans/ethereal-prancing-cascade.md:61`, `/root/.claude/plans/ethereal-prancing-cascade.md:120`.
**Fix Approach:** Refactor enrichment into one shared builder used by both `/api/quarantine/{item_id}/process` and `/api/quarantine/bulk-process`; include the same precedence and normalization logic in both insert paths.
**Industry Standard:** Single-source business logic for equivalent mutation paths (avoid dual-write drift between “single” and “bulk” variants).
**System Fit:** Both endpoints live in `apps/backend/src/api/orchestration/main.py` and write the same JSONB columns (`company_info`, `broker`, `metadata`), so a shared helper is low-friction.
**Enforcement:** Add integration tests that bulk-approve fixtures with `extraction_evidence.financials` and `extraction_evidence.broker`, then assert populated deal JSONB fields.

### Finding 2: Attach-to-existing-deal approvals are not enriched, and backfill join misses them (TG-6 fail)
**Root Cause:** Enrichment only executes when `approve` and `not deal_id`; attach paths bypass mapping entirely. Evidence: `apps/backend/src/api/orchestration/main.py:2755`. Thread-match attach path records an event but does not merge evidence into the existing deal. Evidence: `apps/backend/src/api/orchestration/main.py:2767`, `apps/backend/src/api/orchestration/main.py:2773`, `apps/backend/src/api/orchestration/main.py:2786`. Quarantine row is linked via `deal_id` update. Evidence: `apps/backend/src/api/orchestration/main.py:2963`. Planned backfill joins only `deals.identifiers.quarantine_item_id = quarantine_items.id`, which excludes attach approvals into pre-existing deals. Evidence: `/root/.claude/plans/ethereal-prancing-cascade.md:205`. Frontend also supports approve with explicit `deal_id` in process payload. Evidence: `apps/dashboard/src/lib/api.ts:944`, `apps/dashboard/src/lib/api.ts:957`.
**Fix Approach:** On attach approvals, run a non-destructive merge into the target deal (`q.deal_id`) using the same field precedence. Expand backfill source relation to include approved quarantine rows linked by `q.deal_id = d.deal_id` in addition to `identifiers.quarantine_item_id`.
**Industry Standard:** Normalize enrichment at the domain boundary, independent of whether records are created or attached.
**System Fit:** Schema already has direct quarantine-to-deal linkage (`quarantine_items.deal_id`). Evidence: `apps/backend/db/init/001_base_tables.sql:212`.
**Enforcement:** Add API tests for (a) thread-match attach and (b) explicit `deal_id` approve; assert existing deal fields are enriched without overwriting operator-entered values.

### Finding 3: Planned JSONB `||` backfill strategy is destructive and not truly idempotent (TG-3 fail risk)
**Root Cause:** The plan specifies JSONB `||` merge while also claiming “only add missing fields”; those are incompatible for key collisions because `||` overwrites duplicate keys from the right operand. Evidence: `/root/.claude/plans/ethereal-prancing-cascade.md:207`, `/root/.claude/plans/ethereal-prancing-cascade.md:208`. The same file’s guardrail requires additive-only behavior. Evidence: `/root/.claude/plans/ethereal-prancing-cascade.md:264`. Manual edits to `metadata`/`broker`/`company_info` are supported today, so overwrite risk is real. Evidence: `apps/backend/src/api/orchestration/main.py:850`, `apps/backend/src/api/orchestration/main.py:870`, `apps/backend/src/api/orchestration/main.py:872`.
**Fix Approach:** Use per-key null/missing checks (e.g., `CASE` + `jsonb_set`) rather than whole-object concat, and include a reversible transaction plan (`BEGIN`, verification query, `COMMIT`/`ROLLBACK`).
**Industry Standard:** Idempotent, non-destructive backfills with explicit key-level merge rules and rollback path.
**System Fit:** Deal JSONB columns are flexible and designed for key-level updates. Evidence: `apps/backend/db/init/001_base_tables.sql:40`, `apps/backend/db/init/001_base_tables.sql:41`, `apps/backend/db/init/001_base_tables.sql:42`, `apps/backend/db/init/001_base_tables.sql:43`.
**Enforcement:** Add a repeat-run SQL verification: second execution must produce zero effective changes; assert pre-existing non-null keys are unchanged.

### Finding 4: Currency and multiple coercion plan has edge-case loss and precedence leaks (TG-2 fail risk)
**Root Cause:** Planned precedence uses `or`, so correction intent can be bypassed when parsed correction is falsy/invalid, then fallback pulls extraction value. Evidence: `/root/.claude/plans/ethereal-prancing-cascade.md:147`. Planned `multiple` cast is `float(multiple)`, which drops strings like `"4.2x"`. Evidence: `/root/.claude/plans/ethereal-prancing-cascade.md:153`, `/root/.claude/plans/ethereal-prancing-cascade.md:155`. Extraction schema includes `revenue_range`, but plan has no strategy for it. Evidence: `apps/dashboard/src/lib/api.ts:180`. Dashboard numeric coercion uses `parseFloat` after removing `$`, commas, spaces; suffix inputs like `"2.5M"` become `2.5` if backend ever leaks string values. Evidence: `apps/dashboard/src/lib/api.ts:39`, `apps/dashboard/src/lib/api.ts:44`.
**Fix Approach:** Implement one strict parser for money/multiples with documented handling for: `$2.5M`, `2,500,000`, `TBD`, `N/A`, `null`, and `4.2x`; treat ranges (`1M-5M`) as `revenue_range` metadata (string) rather than coercing into `revenue` numeric.
**Industry Standard:** Parse and normalize financial values at ingestion/approval boundary, not in presentation.
**System Fit:** Backend already has an internal money parser pattern supporting K/M suffixes that can be adapted. Evidence: `apps/backend/src/actions/executors/email_triage_review_email.py:26`, `apps/backend/src/actions/executors/email_triage_review_email.py:31`, `apps/backend/src/actions/executors/email_triage_review_email.py:42`, `apps/backend/src/actions/executors/email_triage_review_email.py:44`.
**Enforcement:** Unit tests for parser edge cases plus endpoint tests asserting corrections precedence over evidence for each financial key.

### Finding 5: Contract-surface and validation strategy in plan won’t detect this regression class
**Root Cause:** Plan tags Surface 16 as affected for approve mapping, but Surface 16 validator only checks injection-tool contract details (bridge tool existence/params/dedup/error handling), not approve-time deal enrichment. Evidence: `/root/.claude/plans/ethereal-prancing-cascade.md:30`, `tools/infra/validate-surface16.sh:2`, `tools/infra/validate-surface16.sh:3`, `tools/infra/validate-surface16.sh:48`, `tools/infra/validate-surface16.sh:88`. `make validate-local` runs schema/route/typing gates but no semantic assertion that approved deals carry evidence-derived fields. Evidence: `Makefile:545`, `Makefile:547`. Existing tests that hit process endpoints assert statuses/latency, not populated deal JSONB semantics. Evidence: `apps/backend/tests/stress/test_quarantine_locking.py:67`, `apps/backend/tests/stress/test_quarantine_locking.py:100`, `apps/backend/tests/load/test_email_triage_load.py:235`, `apps/backend/tests/load/test_email_triage_load.py:248`.
**Fix Approach:** Reclassify this as behavior enforcement (integration tests) rather than surface-schema enforcement only. Add explicit TG-1..TG-6 verification tests to CI.
**Industry Standard:** Contract checks + behavioral regression tests for high-impact data pipelines.
**System Fit:** Test suite already has integration/e2e structure; adding targeted quarantine-approve fixtures is straightforward and local to backend tests.
**Enforcement:** New CI gate: fail if approve/bulk-approve/attach flows do not persist expected broker and financial metadata fields from extraction evidence.

## ADJACENT OBSERVATIONS

- Out-of-scope workflow safety issue: `undo-approve` archives whatever deal is linked on the quarantine row, including pre-existing deals that were only attached by thread match. Evidence: `apps/backend/src/api/orchestration/main.py:3094`, `apps/backend/src/api/orchestration/main.py:3097`, `apps/backend/src/api/orchestration/main.py:3100`.
- Out-of-scope UI mismatch: conflict UI labels “Approve into this deal,” but the current approve handler does not pass a selected `deal_id`; it only opens the generic approve dialog and posts without `dealId`. Evidence: `apps/dashboard/src/app/quarantine/page.tsx:1000`, `apps/dashboard/src/app/quarantine/page.tsx:1007`, `apps/dashboard/src/app/quarantine/page.tsx:312`, `apps/dashboard/src/app/quarantine/page.tsx:316`.
- Out-of-scope UI fallback typo: asking-price “original” fallback uses `preview.company_name` when `financials.asking_price` is absent. Evidence: `apps/dashboard/src/app/quarantine/page.tsx:1110`.

## SUMMARY
- Total primary findings: 5
- Total adjacent observations: 3
- Confidence level: HIGH
- Key recommendation: Collapse approve enrichment into a shared single/bulk/attach path with non-destructive backfill semantics and enforce TG-1..TG-6 via integration tests, not surface-only gates.

---

## Instructions

You are reviewing all three independent investigation reports. Your job is to:

1. **Identify duplicates** — findings that multiple agents reported (high confidence items)
2. **Identify conflicts** — findings where agents disagree on root cause or fix approach
3. **Identify unique findings** — items only one agent found (potential blind spot coverage)
4. **Verify evidence** — check that cited file:line references are accurate
5. **Flag drift** — note any findings that fall outside the declared mission scope

### Output Format

Write your cross-review to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/02_pass2/gemini_review.md`

Begin with exactly this header:

```
# Pass 2 Cross-Review — GEMINI
## Run: TP-20260218-194105 | Mode: design
## Generated: 2026-02-18T19:50:03Z
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
