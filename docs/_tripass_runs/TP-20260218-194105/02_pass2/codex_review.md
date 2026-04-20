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