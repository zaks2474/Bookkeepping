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