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