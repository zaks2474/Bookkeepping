# TriPass — Pass 3: Consolidation

## Agent Identity
**Agent**: CLAUDE (Consolidator) (Consolidator)
**Run ID**: TP-20260218-194105
**Pipeline Mode**: design
**Timestamp**: 2026-02-18T19:55:28Z

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

## All Prior Outputs

You have access to:
- 3 Pass 1 independent reports (in 01_pass1/)
- 3 Pass 2 cross-reviews (in 02_pass2/)
- The shared WORKSPACE.md with all appended outputs

Your job is to produce a single, deduplicated master document that:
1. Preserves every unique finding (nothing silently dropped)
2. Merges duplicates with attribution to all originating agents
3. Resolves conflicts with evidence (pick the position with stronger evidence)
4. Structures the output as a builder-ready mission prompt with gates
5. Excludes drift items from primary findings (log them in a separate section)

---

## Consolidation Rules

- **No silent drops.** Every finding from every Pass 1 report must appear in the master as either:
  - A primary finding (included)
  - A merged item (deduplicated, with all source attributions)
  - An explicitly discarded item (with documented reason in DISCARDED section)
- **Evidence required.** Every primary finding must cite file:line evidence
- **All 5 fields required.** Every finding must have: root cause, fix approach, industry standard, system fit, enforcement mechanism
- **Builder-ready gates.** The master must include enforceable acceptance gates that a builder agent can run to verify completion

---

## Output Format

Write the consolidated master to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/FINAL_MASTER.md`

Begin with exactly this header:

```
# FINAL MASTER — TP-20260218-194105
## Mode: design
## Generated: 2026-02-18T19:55:28Z
## Sources: 3 Pass 1 reports + 3 Pass 2 cross-reviews
```

Then organize as:

```
## MISSION
(brief restatement of mission objective)

## CONSOLIDATED FINDINGS

### F-1: [Title]
**Sources:** Agent A (P1-F3), Agent B (P1-F1)
**Root Cause:** ...
**Fix Approach:** ...
**Industry Standard:** ...
**System Fit:** ...
**Enforcement:** ...

(repeat for each consolidated finding, numbered F-1 through F-N)

## DISCARDED ITEMS
Items from Pass 1 that were intentionally excluded, with reasons.

### DISC-1: [Title] (from Agent X, Finding Y)
**Reason for exclusion:** ...

## DRIFT LOG
Out-of-scope items flagged by cross-reviews. Not actionable in this mission.

## ACCEPTANCE GATES
Builder-enforceable gates for implementing the findings above.

### Gate 1: [Gate Name]
**Command:** ...
**Pass criteria:** ...

(repeat)

## STATISTICS
- Total Pass 1 findings across all agents: N
- Deduplicated primary findings: N
- Discarded (with reason): N
- Drift items: N
- Drop rate: 0% (all findings accounted for)
```

---
## Full Workspace (All Prior Outputs)

# TriPass Workspace — TP-20260218-194105

---
## Pass 1 — CLAUDE Report
---
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


---
## Pass 1 — GEMINI Report
---
I will list the files in `/root/.claude/plans/` to confirm the location of the plan, and also list the files in the current working directory to get a better sense of the structure.
I will read the content of the plan file `/root/.claude/plans/ethereal-prancing-cascade.md`.


---
## Pass 1 — CODEX Report
---
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
## Pass 2 — CLAUDE Cross-Review
---
Pass 2 cross-review complete. Report written to:

`docs/_tripass_runs/TP-20260218-194105/02_pass2/claude_review.md`

> **Note:** Same sandbox restriction as Pass 1 — file is in the monorepo at `/home/zaks/zakops-agent-api/docs/_tripass_runs/...`. Copy to `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/02_pass2/claude_review.md` post-run.

### Results Summary

| Metric | Count |
|--------|-------|
| **Duplicates** (high confidence, 2+ agents) | 5 |
| **Conflicts** (agents disagree) | 2 |
| **Unique valid findings** | 7 |
| **Drift items** (out of scope) | 7 |

**Key takeaways:**

- **Strong convergence** between CLAUDE and CODEX on the 5 core issues (bulk data loss, thread-match non-enrichment, destructive backfill, currency parsing, missing tests)
- **GEMINI produced no usable output** — only 2/3 agents contributed
- **Two conflicts resolved:** (1) currency normalization should happen backend-side using existing `_parse_money()`, not dashboard-side; (2) `.passthrough()` AND exact field mapping are both needed
- **Critical unique finding from CODEX:** backfill JOIN misses attach-path deals — must also join on `quarantine_items.deal_id`
- **Critical unique finding from CLAUDE:** bulk approve has no thread deduplication — creates duplicate deals
- **TG-4 (bulk approve) remains BLOCKED** — needs extraction_evidence in SELECT, shared mapper, and thread dedup


---
## Pass 2 — GEMINI Cross-Review
---
# Gemini Agent — No Output
The Gemini agent did not produce output within the timeout.


---
## Pass 2 — CODEX Cross-Review
---
Unable to write `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/02_pass2/codex_review.md` in this environment (`Permission denied` in read-only sandbox).  
Exact report content:

```markdown
# Pass 2 Cross-Review — CODEX
## Run: TP-20260218-194105 | Mode: design
## Generated: 2026-02-18T19:50:03Z

## DUPLICATES (High Confidence)
Items found by 2+ agents. Merge into a single entry with attribution.

### D-1: Bulk Approve Drops Extraction Evidence
**Reported by:** Agent A (Finding 2), Agent C (Finding 1)
**Consensus root cause:** `bulk_process_quarantine` does not fetch `extraction_evidence`, then inserts deals with empty `company_info`/`broker` and minimal `metadata`.
**Consensus fix:** Use one shared quarantine→deal enrichment builder for single and bulk approve; ensure bulk select includes evidence fields and applies the same precedence logic.
**Evidence verified:** YES (`apps/backend/src/api/orchestration/main.py:2591`, `apps/backend/src/api/orchestration/main.py:2624`, `/root/.claude/plans/ethereal-prancing-cascade.md:50`)

### D-2: Attach/Thread-Match Approvals Do Not Enrich Existing Deals
**Reported by:** Agent A (Finding 3), Agent C (Finding 2)
**Consensus root cause:** Thread-match path records a timeline event but does not merge evidence into `deals.metadata`/`broker`/`company_info`; attach approvals are linked only via quarantine `deal_id` update.
**Consensus fix:** Apply the same non-destructive enrichment merge for attach approvals (thread-match and explicit `deal_id`) and include attach-linked rows in backfill source selection.
**Evidence verified:** YES (`apps/backend/src/api/orchestration/main.py:2767`, `apps/backend/src/api/orchestration/main.py:2963`, `/root/.claude/plans/ethereal-prancing-cascade.md:205`)

### D-3: Currency/Multiple Coercion Is Unsafe for Real Inputs
**Reported by:** Agent A (Finding 4), Agent C (Finding 4)
**Consensus root cause:** Numeric coercion relies on `parseFloat`/`float()` patterns that mis-handle suffixes (`M`, `K`), ranges, and annotated multiples (`4.2x`).
**Consensus fix:** Implement one documented parser for money/multiple edge cases with explicit handling for null tokens (`TBD`, `N/A`), suffixes, and range preservation (`revenue_range` as string metadata).
**Evidence verified:** YES (`apps/dashboard/src/lib/api.ts:33`, `/root/.claude/plans/ethereal-prancing-cascade.md:147`, `/root/.claude/plans/ethereal-prancing-cascade.md:155`)

### D-4: Planned Backfill Merge Can Overwrite Operator Data
**Reported by:** Agent A (Finding 8), Agent C (Finding 3)
**Consensus root cause:** Plan proposes JSONB `||` while also requiring additive-only behavior; raw `||` overwrites colliding keys.
**Consensus fix:** Use fill-only per-key merge conditions, run in transaction with dry-run verification, and prove idempotence on rerun.
**Evidence verified:** YES (`/root/.claude/plans/ethereal-prancing-cascade.md:207`, `/root/.claude/plans/ethereal-prancing-cascade.md:264`)

## CONFLICTS
Items where agents disagree. State both positions with evidence.

### C-1: JSONB Merge Mechanism (`||` vs strict key guards)
**Agent A position:** `||` can be used if merge payload is null-filtered/fill-only.
**Agent C position:** `||` is risky/destructive under key collisions; use explicit guarded key updates.
**Evidence comparison:** Both agree on non-destructive requirement; disagreement is implementation strictness.
**Recommended resolution:** Require explicit per-key “missing-only” construction and tests; if `||` is used, enforce that RHS only contains currently missing keys.

### C-2: Parser Location (Frontend vs Backend)
**Agent A position:** Harden dashboard `coerceToNumber` to parse suffix formats.
**Agent C position:** Prioritize backend normalization at approve boundary.
**Evidence comparison:** Both detect same defect (`$2.5M`, `$500K` parsing) but place remediation at different layers.
**Recommended resolution:** Normalize in backend as source of truth; keep dashboard coercion defensive for legacy/partial payloads.

## UNIQUE FINDINGS
Items found by only one agent. Verify if the finding is valid.

### U-1: Single-item approve path still drops extraction evidence fields (from Agent A)
**Verification:** CONFIRMED
**Evidence check:** Single approve builds minimal `broker` and `metadata`; no `extraction_evidence` mapping despite `SELECT *` (`apps/backend/src/api/orchestration/main.py:2701`, `apps/backend/src/api/orchestration/main.py:2815`, `apps/backend/src/api/orchestration/main.py:2863`).
**Should include in final:** YES (core mission root cause)

### U-2: Bulk approve lacks thread deduplication and can create duplicate deals (from Agent A)
**Verification:** CONFIRMED
**Evidence check:** Bulk approve always calls `next_deal_id()` and has no `email_threads` lookup path (`apps/backend/src/api/orchestration/main.py:2610`, `apps/backend/src/api/orchestration/main.py:2756`).
**Should include in final:** YES (TG-4/TG-6 risk)

### U-3: DealDetailSchema strips unknown JSONB keys without passthrough (from Agent A)
**Verification:** CONFIRMED
**Evidence check:** `broker`, `company_info`, `metadata` are strict `z.object(...)` with no `.passthrough()` (`apps/dashboard/src/lib/api.ts:108`, `apps/dashboard/src/lib/api.ts:114`, `apps/dashboard/src/lib/api.ts:118`).
**Should include in final:** YES (plan already proposes mitigation; low risk to include)

### U-4: Revenue/multiple are typed but not rendered in deal page (from Agent A)
**Verification:** CONFIRMED
**Evidence check:** Schema includes `revenue`/`multiple`, but Financials UI only renders asking price/EBITDA/NDA/CIM (`apps/dashboard/src/lib/api.ts:122`, `apps/dashboard/src/app/deals/[id]/page.tsx:557`).
**Should include in final:** NO (valid but scope-adjacent UI parity item, not core data-loss blocker)

### U-5: Backfill join misses attach-linked approvals via `quarantine_items.deal_id` (from Agent C)
**Verification:** CONFIRMED
**Evidence check:** Plan join only uses `identifiers.quarantine_item_id`; attach path persists linkage through `q.deal_id` (`/root/.claude/plans/ethereal-prancing-cascade.md:205`, `apps/backend/src/api/orchestration/main.py:2963`).
**Should include in final:** YES (critical for TG-6 completeness)

### U-6: Current contract-surface gates will not catch enrichment regressions (from Agent C)
**Verification:** CONFIRMED
**Evidence check:** Surface 16 validator targets injection-tool contract checks, not approve enrichment semantics; `validate-local` runs schema/typing gates without this behavior assertion (`tools/infra/validate-surface16.sh:2`, `Makefile:545`).
**Should include in final:** YES (testing strategy gap)

### U-7: Undo-approve can archive pre-existing deals that were only attached (from Agent C)
**Verification:** CONFIRMED
**Evidence check:** Undo path archives whatever `item.deal_id` references with no provenance check (`apps/backend/src/api/orchestration/main.py:3094`, `apps/backend/src/api/orchestration/main.py:3099`).
**Should include in final:** YES (workflow safety under Lens 5)

## DRIFT FLAGS
Findings that fall outside declared scope.

### DRIFT-1: `state_machine` contract mismatch on deal detail (from Agent A)
**Why out of scope:** Mission targets quarantine→deal evidence mapping; this is a broader deal-detail contract mismatch unrelated to evidence promotion.
**Severity if ignored:** Medium

### DRIFT-2: PATCH endpoint full-replace JSONB risk (from Agent A)
**Why out of scope:** This concerns generic `/api/deals/{deal_id}` update semantics, not quarantine approval mapping.
**Severity if ignored:** Medium-High

### DRIFT-3: Quarantine conflict UI says “Approve into this deal” but does not pass `deal_id` (from Agent C)
**Why out of scope:** Frontend routing-conflict UX bug; mission artifacts and plan focus approve enrichment pipeline, not conflict selector UX wiring.
**Severity if ignored:** Medium

### DRIFT-4: Approve dialog fallback typo uses `company_name` for asking price (from Agent C)
**Why out of scope:** UI fallback correctness issue in preview form, not backend evidence persistence.
**Severity if ignored:** Low-Medium

## SUMMARY
- Duplicates: 4
- Conflicts: 2
- Unique valid findings: 7
- Drift items: 4
- Overall assessment: Core consensus is strong and evidence-backed: single/bulk/attach parity and non-destructive backfill are the critical blockers; parser hardening and behavioral tests are required to meet TG-1..TG-6 reliably. Agent B contributed no substantive technical findings in Pass 1, so confidence is weighted to Agent A + Agent C convergence.
```

