# MISSION: QA-CGFS-VERIFY-001
## Independent Deep Verification & Remediation — COL-GAP-FULLSTACK-001
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-GAP-FULLSTACK-001 (COMPLETE — 10/10 AC, 2026-02-13)
## Successor: None — this is a terminal QA pass

---

## Mission Objective

This is an **independent deep verification** of COL-GAP-FULLSTACK-001 — a full-stack mission that closed 2 QA gaps (Quarantine FSM + Reflexion Loop) identified by the QA-COL-DEEP-VERIFY-001A/B/C consolidated report (214 gates).

**Source artifacts:**
- Execution plan: `/home/zaks/bookkeeping/docs/COL-GAP-FULLSTACK-001.md` (308 lines)
- Completion report: `/home/zaks/bookkeeping/docs/COL-GAP-FULLSTACK-001-COMPLETION.md` (99 lines)
- CHANGES.md entry: `/home/zaks/bookkeeping/CHANGES.md` (top entry, 2026-02-13)
- Original QA findings: QA-COL-DEEP-VERIFY-001A/B/C (VF-04.1, VF-04.2, VF-03.1, VF-03.4)

**What this mission does:**
1. Verifies every AC with fresh evidence (code-level grep, DB queries, type inspection)
2. Cross-checks that all modified files are internally consistent and match specs
3. Stress-tests the implementation for edge cases, regressions, and architectural violations
4. Remediates any gaps found (fix → re-verify → record)

**What this mission does NOT do:**
- Does not build new features
- Does not redesign existing implementations
- Does not modify infrastructure beyond remediating verified failures

**Scope:** 2 repos (zakops-backend, zakops-agent-api), 9 files modified, 2 files created, 1 DB table, 2 independent tracks (Quarantine FSM + Reflexion Loop).

---

## Glossary

| Term | Definition |
|------|-----------|
| FSM Ledger | `zakops.deal_transitions` table — audit trail of all deal stage changes |
| Reflexion | Self-critique pipeline in agent service (COL-DESIGN-SPEC-V2, S8.3-8.5) |
| CritiqueResult | Pydantic model storing reflexion output (issues, severity, should_revise, etc.) |
| Refinement loop | While loop that calls `refine_if_needed()` up to MAX_REFINEMENTS times |
| Promise.allSettled | Mandatory data-fetching pattern in dashboard (Promise.all is banned) |
| RefinedBadge | UI badge in chat that shows whether a response was critiqued or refined |

---

## Pre-Flight (PF-1 through PF-5)

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-cgfs-pf1.txt
```
**PASS if:** Exit 0, output contains "All local validations passed".

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-cgfs-pf2.txt
```
**PASS if:** Exit 0, zero errors.

### PF-3: Completion Report Exists
```bash
ls -la /home/zaks/bookkeeping/docs/COL-GAP-FULLSTACK-001-COMPLETION.md 2>&1 | tee /tmp/qa-cgfs-pf3.txt
```
**PASS if:** File exists, non-empty.

### PF-4: CHANGES.md Entry Present
```bash
grep -c "COL-GAP-FULLSTACK-001" /home/zaks/bookkeeping/CHANGES.md 2>&1 | tee /tmp/qa-cgfs-pf4.txt
```
**PASS if:** Count >= 1.

### PF-5: Database Reachable
```bash
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "SELECT 1;" 2>&1 | tee /tmp/qa-cgfs-pf5.txt
```
**PASS if:** Returns "1". If FAIL, mark all DB gates as SKIP (code-only verification).

---

## Verification Family 01 — Database Migration (AC-1)

### VF-01.1: Migration file exists and has correct name
```bash
ls -la /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql 2>&1 | tee /tmp/qa-cgfs-vf01-1.txt
```
**PASS if:** File exists, owned by zaks:zaks, non-empty.

### VF-01.2: Rollback file exists
```bash
ls -la /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger_rollback.sql 2>&1 | tee /tmp/qa-cgfs-vf01-2.txt
```
**PASS if:** File exists, owned by zaks:zaks.

### VF-01.3: Migration wrapped in BEGIN/COMMIT transaction
```bash
grep -n "^BEGIN;" /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql 2>&1 | tee /tmp/qa-cgfs-vf01-3.txt
grep -n "^COMMIT;" /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql 2>&1 | tee -a /tmp/qa-cgfs-vf01-3.txt
```
**PASS if:** Both `BEGIN;` and `COMMIT;` are present.

### VF-01.4: Table has exactly 10 columns matching workflow.py INSERT
```bash
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_schema='zakops' AND table_name='deal_transitions' ORDER BY ordinal_position;" 2>&1 | tee /tmp/qa-cgfs-vf01-4.txt
```
**PASS if:** Returns exactly 10 rows: `id (uuid), deal_id (varchar 20), from_stage (varchar 50), to_stage (varchar 50), actor_id (varchar 255), actor_type (varchar 50), correlation_id (varchar 255), reason (text), idempotency_key (varchar 64), created_at (timestamptz)`. Column names must match EXACTLY — character by character — the workflow.py INSERT at lines 231-234.

### VF-01.5: Column name parity — migration DDL vs workflow.py INSERT
```bash
grep -oP '(?<=INSERT INTO zakops.deal_transitions \()[\s\S]*?(?=\))' /home/zaks/zakops-backend/src/core/deals/workflow.py | tr ',' '\n' | sed 's/^ *//;s/ *$//' | sort 2>&1 | tee /tmp/qa-cgfs-vf01-5a.txt
grep -oP '(?<=^\s{4})\w+' /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql | grep -v "IF\|NOT\|EXISTS\|TABLE\|PRIMARY\|DEFAULT\|ON\|DELETE\|CASCADE\|INDEX\|CREATE\|REFERENCES\|NULL\|BEGIN\|COMMIT\|zakops" | sort 2>&1 | tee /tmp/qa-cgfs-vf01-5b.txt
```
**PASS if:** Both sorted lists are identical. Any mismatch means a runtime SQL error.

### VF-01.6: Foreign key references deals(deal_id) correctly
```bash
grep "REFERENCES" /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql 2>&1 | tee /tmp/qa-cgfs-vf01-6.txt
```
**PASS if:** Contains `REFERENCES zakops.deals(deal_id) ON DELETE CASCADE`.

### VF-01.7: deal_id FK type matches source table
```bash
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "SELECT data_type, character_maximum_length FROM information_schema.columns WHERE table_schema='zakops' AND table_name='deals' AND column_name='deal_id';" 2>&1 | tee /tmp/qa-cgfs-vf01-7.txt
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "SELECT data_type, character_maximum_length FROM information_schema.columns WHERE table_schema='zakops' AND table_name='deal_transitions' AND column_name='deal_id';" 2>&1 | tee -a /tmp/qa-cgfs-vf01-7.txt
```
**PASS if:** Both are `character varying / 20`. Any type mismatch causes FK constraint failure.

### VF-01.8: Two indexes exist on the table
```bash
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "SELECT indexname FROM pg_indexes WHERE tablename='deal_transitions' AND schemaname='zakops' ORDER BY indexname;" 2>&1 | tee /tmp/qa-cgfs-vf01-8.txt
```
**PASS if:** Returns exactly 3 indexes: `deal_transitions_pkey`, `idx_deal_transitions_created_at`, `idx_deal_transitions_deal_id`.

### VF-01.9: Rollback drops in reverse order (indexes before table)
```bash
grep -n "DROP" /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger_rollback.sql 2>&1 | tee /tmp/qa-cgfs-vf01-9.txt
```
**PASS if:** DROP INDEX lines appear BEFORE DROP TABLE line. Reverse order ensures clean rollback.

### VF-01.10: No CRLF in migration files
```bash
file /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql 2>&1 | tee /tmp/qa-cgfs-vf01-10.txt
file /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger_rollback.sql 2>&1 | tee -a /tmp/qa-cgfs-vf01-10.txt
```
**PASS if:** Neither file reports "CRLF" or "with CR". Must show "ASCII text" or "UTF-8 Unicode text".

**Gate VF-01:** All 10 checks pass. The deal_transitions table is correctly defined, deployed, and matches the backend INSERT schema.

---

## Verification Family 02 — Quarantine Approval Ledger Write (AC-2)

### VF-02.1: deal_transitions INSERT exists in quarantine approval flow
```bash
grep -n "INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-cgfs-vf02-1.txt
```
**PASS if:** Returns exactly 1 match, in the quarantine approval section (~line 1799-1810).

### VF-02.2: from_stage is NULL (initial creation, not a transition)
```bash
grep -A5 "INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/api/orchestration/main.py | grep "NULL" 2>&1 | tee /tmp/qa-cgfs-vf02-2.txt
```
**PASS if:** Contains `NULL` (from_stage value for initial deal creation).

### VF-02.3: to_stage is 'inbound' (matches initial deal stage)
```bash
grep -A5 "INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/api/orchestration/main.py | grep "'inbound'" 2>&1 | tee /tmp/qa-cgfs-vf02-3.txt
```
**PASS if:** Contains `'inbound'` as to_stage value.

### VF-02.4: Reason string matches expected value
```bash
grep -A10 "INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/api/orchestration/main.py | grep "Promoted from quarantine approval" 2>&1 | tee /tmp/qa-cgfs-vf02-4.txt
```
**PASS if:** Contains `'Promoted from quarantine approval'`.

### VF-02.5: INSERT is INSIDE the same transaction as deal creation
```bash
grep -n "async with pool.acquire\|await conn.execute\|INSERT INTO zakops.deals\|INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/api/orchestration/main.py | head -20 2>&1 | tee /tmp/qa-cgfs-vf02-5.txt
```
**PASS if:** The deal_transitions INSERT uses the same `conn` variable as the deals INSERT, ensuring atomicity. Both should be inside `async with pool.acquire() as conn:`.

### VF-02.6: VF-04 comment tag is present (traceability to original finding)
```bash
grep "VF-04" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-cgfs-vf02-6.txt
```
**PASS if:** Contains `VF-04.1/VF-04.2` comment referencing the original QA finding.

### VF-02.7: actor_type is 'system' (quarantine approval is system-initiated)
```bash
grep -A8 "INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/api/orchestration/main.py | grep "'system'" 2>&1 | tee /tmp/qa-cgfs-vf02-7.txt
```
**PASS if:** Contains `'system'` as actor_type value (quarantine approval is a system action, not a user action).

**Gate VF-02:** All 7 checks pass. Quarantine approval correctly writes to the FSM ledger with proper values and transactional integrity.

---

## Verification Family 03 — Transitions API Endpoint (AC-3)

### VF-03.1: GET endpoint exists in workflow router
```bash
grep -n "/{deal_id}/transitions" /home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py 2>&1 | tee /tmp/qa-cgfs-vf03-1.txt
```
**PASS if:** Returns a line with `@router.get("/{deal_id}/transitions")`.

### VF-03.2: Endpoint returns 3-key response shape
```bash
grep -A20 "async def get_transitions" /home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py | grep -E '"deal_id"|"transitions"|"count"' 2>&1 | tee /tmp/qa-cgfs-vf03-2.txt
```
**PASS if:** Returns 3 matches: `"deal_id"`, `"transitions"`, `"count"`.

### VF-03.3: get_transitions engine method returns chronological order
```bash
grep -A30 "async def get_transitions" /home/zaks/zakops-backend/src/core/deals/workflow.py | grep "ORDER BY" 2>&1 | tee /tmp/qa-cgfs-vf03-3.txt
```
**PASS if:** Contains `ORDER BY created_at ASC`. Chronological order is required for timeline display.

### VF-03.4: 404 error handling for non-existent deals
```bash
grep -A20 "async def get_transitions" /home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py | grep "404" 2>&1 | tee /tmp/qa-cgfs-vf03-4.txt
```
**PASS if:** Contains `status_code=404` for ValueError (deal not found).

### VF-03.5: Workflow router uses correct prefix
```bash
grep "prefix=" /home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py | head -1 2>&1 | tee /tmp/qa-cgfs-vf03-5.txt
```
**PASS if:** Contains `prefix="/api/deals"`. The full endpoint path is `/api/deals/{deal_id}/transitions`.

### VF-03.6: Engine method validates deal existence before querying transitions
```bash
grep -B2 -A8 "SELECT deal_id FROM zakops.deals" /home/zaks/zakops-backend/src/core/deals/workflow.py | grep -A6 "get_transitions" 2>&1 | tee /tmp/qa-cgfs-vf03-6.txt
```
**PASS if:** Shows a deal existence check query BEFORE the transitions SELECT. Missing validation = information leak.

### VF-03.7: Response mapping uses 'timestamp' key (not 'created_at')
```bash
grep -A15 "return \[" /home/zaks/zakops-backend/src/core/deals/workflow.py | grep '"timestamp"' 2>&1 | tee /tmp/qa-cgfs-vf03-7.txt
```
**PASS if:** Contains `"timestamp"` as the key name (frontend expects 'timestamp', DB column is 'created_at').

**Gate VF-03:** All 7 checks pass. The transitions API endpoint is correctly wired, returns the right shape, and handles errors.

---

## Verification Family 04 — Dashboard Transitions Timeline (AC-4)

### VF-04.1: getDealTransitions imported in deal detail page
```bash
grep "getDealTransitions" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-1.txt
```
**PASS if:** Returns >= 2 matches (import + usage in Promise.allSettled).

### VF-04.2: DealTransition type imported
```bash
grep "type DealTransition" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-2.txt
```
**PASS if:** Contains `type DealTransition` in the import block.

### VF-04.3: transitions state variable declared with correct type
```bash
grep "useState<DealTransition\[\]>" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-3.txt
```
**PASS if:** Returns `useState<DealTransition[]>([])`.

### VF-04.4: getDealTransitions is inside Promise.allSettled (NOT Promise.all)
```bash
grep -B20 "getDealTransitions" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx | grep "Promise.allSettled" 2>&1 | tee /tmp/qa-cgfs-vf04-4.txt
```
**PASS if:** Shows `Promise.allSettled` context. FAIL if `Promise.all` is used (banned pattern).

### VF-04.5: Results unpacking handles rejection gracefully
```bash
grep -A2 "results\[7\]" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-5.txt
```
**PASS if:** Shows `results[7].status === 'fulfilled'` check with else branch for failure tracking.

### VF-04.6: Transitions tab trigger exists with count
```bash
grep "TabsTrigger.*transitions" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-6.txt
```
**PASS if:** Contains `<TabsTrigger value='transitions'>Transitions ({transitions.length})</TabsTrigger>`.

### VF-04.7: TabsContent for transitions renders timeline
```bash
grep -c "TabsContent.*transitions" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-7.txt
```
**PASS if:** Count >= 1.

### VF-04.8: Empty state handled (no transitions scenario)
```bash
grep "No stage transitions recorded" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-8.txt
```
**PASS if:** Empty state message exists for when transitions.length === 0.

### VF-04.9: DealTransition interface has all 8 fields matching backend response
```bash
grep -A10 "export interface DealTransition" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | tee /tmp/qa-cgfs-vf04-9.txt
```
**PASS if:** Interface has 8 properties: `id, from_stage, to_stage, actor_id, actor_type, correlation_id, reason, timestamp`. Must match the 8-column SELECT in workflow.py get_transitions.

### VF-04.10: getDealTransitions returns empty array on error (never throws)
```bash
grep -A10 "async function getDealTransitions" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | grep "return \[\]" 2>&1 | tee /tmp/qa-cgfs-vf04-10.txt
```
**PASS if:** Contains `return [];` in catch block. Dashboard data fetchers must NEVER throw — they return typed empty fallbacks.

### VF-04.11: Timeline displays "Created → inbound" for null from_stage
```bash
grep -E "from_stage.*Created|Created.*inbound" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf04-11.txt
```
**PASS if:** Shows conditional rendering: null from_stage displays "Created → {to_stage}" instead of "null → inbound".

**Gate VF-04:** All 11 checks pass. Dashboard transitions timeline is correctly wired, uses Promise.allSettled, handles empty state, and displays transitions with proper null handling.

---

## Verification Family 05 — Reflexion Refinement Loop (AC-5, AC-6, AC-7)

### VF-05.1: MAX_REFINEMENTS constant exists and equals 2
```bash
grep -n "^MAX_REFINEMENTS" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/qa-cgfs-vf05-1.txt
```
**PASS if:** Returns `MAX_REFINEMENTS = 2` (exactly 2, not 1, not 3).

### VF-05.2: refine_if_needed method exists with correct signature
```bash
grep -n "async def refine_if_needed" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/qa-cgfs-vf05-2.txt
```
**PASS if:** Returns method signature with parameters: `self, original_response, critique, evidence, brain_facts`.

### VF-05.3: refine_if_needed returns tuple[str, CritiqueResult]
```bash
grep -A3 "async def refine_if_needed" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py | grep "tuple" 2>&1 | tee /tmp/qa-cgfs-vf05-3.txt
```
**PASS if:** Return type annotation includes `tuple[str, CritiqueResult]`.

### VF-05.4: refine_if_needed has guard clause (no-op when should_revise=False)
```bash
grep -A15 "async def refine_if_needed" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py | grep "not critique.should_revise" 2>&1 | tee /tmp/qa-cgfs-vf05-4.txt
```
**PASS if:** Guard clause returns early when should_revise is False. Missing guard = wasted LLM calls.

### VF-05.5: refine_if_needed calls self.critique() for re-evaluation
```bash
grep -A50 "async def refine_if_needed" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py | grep "await self.critique" 2>&1 | tee /tmp/qa-cgfs-vf05-5.txt
```
**PASS if:** Re-critique call exists after refinement. Without re-critique, the loop cannot converge.

### VF-05.6: Graph.py imports MAX_REFINEMENTS
```bash
grep "from app.services.reflexion import MAX_REFINEMENTS" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-vf05-6.txt
```
**PASS if:** Import statement exists.

### VF-05.7: While loop uses correct guard condition
```bash
grep "while critique.should_revise and refinement_count < MAX_REFINEMENTS" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-vf05-7.txt
```
**PASS if:** Exact pattern match. The loop MUST check both `should_revise` AND `refinement_count < MAX_REFINEMENTS`. Missing either guard = infinite loop or no-op.

### VF-05.8: refinement_count is incremented inside the loop
```bash
grep -A10 "while critique.should_revise" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py | grep "refinement_count += 1" 2>&1 | tee /tmp/qa-cgfs-vf05-8.txt
```
**PASS if:** `refinement_count += 1` appears inside the while block. Missing increment = infinite loop.

### VF-05.9: was_refined flag is set to True inside the loop
```bash
grep -A10 "while critique.should_revise" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py | grep "was_refined = True" 2>&1 | tee /tmp/qa-cgfs-vf05-9.txt
```
**PASS if:** `was_refined = True` is set inside the loop body.

### VF-05.10: Snapshot stores refinement_count as integer
```bash
grep 'critique_data\["refinement_count"\]' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-vf05-10.txt
```
**PASS if:** `critique_data["refinement_count"] = refinement_count` exists.

### VF-05.11: Snapshot stores was_refined as boolean
```bash
grep 'critique_data\["was_refined"\]' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-vf05-11.txt
```
**PASS if:** `critique_data["was_refined"] = was_refined` exists.

### VF-05.12: Snapshot written via JSON to critique_result column
```bash
grep "json.dumps(critique_data)" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-vf05-12.txt
```
**PASS if:** JSON serialization of critique_data written to DB.

### VF-05.13: Exception handling wraps the entire reflexion block
```bash
grep -n "except.*refl_err\|reflexion_critique_failed" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-vf05-13.txt
```
**PASS if:** Outer try/except catches Exception, logs as debug. Reflexion must NEVER block the user response.

### VF-05.14: VF-03 comment tag present (traceability to original finding)
```bash
grep "VF-03" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-vf05-14.txt
```
**PASS if:** Contains `VF-03.1` reference in at least one file.

**Gate VF-05:** All 14 checks pass. Reflexion refinement loop is correctly implemented with hard cap, guard clauses, convergence mechanism, snapshot persistence, and exception safety.

---

## Verification Family 06 — Chat Refinement Badge (AC-8)

### VF-06.1: RefinedBadgeProps includes was_refined and refinement_count
```bash
grep -A8 "interface RefinedBadgeProps" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /tmp/qa-cgfs-vf06-1.txt
```
**PASS if:** Interface includes `was_refined?: boolean` and `refinement_count?: number`.

### VF-06.2: Badge distinguishes "Refined" from "Critiqued"
```bash
grep -E "Refined|Critiqued" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /tmp/qa-cgfs-vf06-2.txt
```
**PASS if:** Both strings `Refined` and `Critiqued` appear (two distinct states).

### VF-06.3: Badge shows iteration count in label
```bash
grep "refinementCount\|refinement_count" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /tmp/qa-cgfs-vf06-3.txt
```
**PASS if:** refinement_count is used in the badge label (e.g., "Refined (2x)").

### VF-06.4: Different color classes for refined vs critiqued
```bash
grep -E "purple.*500|blue.*500" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /tmp/qa-cgfs-vf06-4.txt
```
**PASS if:** Both purple (for refined) and blue (for critiqued) color classes exist.

### VF-06.5: ChatMessage type in chat/page.tsx includes new fields
```bash
grep "was_refined.*boolean\|refinement_count.*number" /home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf06-5.txt
```
**PASS if:** Both `was_refined?: boolean` and `refinement_count?: number` appear in ChatMessage interface.

### VF-06.6: Badge returns null when no critiqueResult (no spurious rendering)
```bash
grep "if (!critiqueResult) return null" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /tmp/qa-cgfs-vf06-6.txt
```
**PASS if:** Early return for null/undefined critiqueResult.

### VF-06.7: Tooltip includes severity information
```bash
grep -E "severity" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx | grep -v "interface\|import" 2>&1 | tee /tmp/qa-cgfs-vf06-7.txt
```
**PASS if:** Severity is referenced in tooltip content (not just in the interface).

**Gate VF-06:** All 7 checks pass. RefinedBadge correctly distinguishes refined from critiqued with visual differentiation and accurate metadata display.

---

## Verification Family 07 — No Regressions (AC-9)

### VF-07.1: make validate-local passes
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-cgfs-vf07-1.txt
```
**PASS if:** Exit 0, contains "All local validations passed".

### VF-07.2: TypeScript compiles clean
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-cgfs-vf07-2.txt
```
**PASS if:** Exit 0, zero errors.

### VF-07.3: No stray text in quarantine page (regression from session)
```bash
tail -3 /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>&1 | tee /tmp/qa-cgfs-vf07-3.txt
```
**PASS if:** Last line is `}` (closing brace of the component). No stray `=== Contract ===` or other junk text.

### VF-07.4: Port 8090 not referenced
```bash
grep -rn "8090" /home/zaks/zakops-backend/src/api/orchestration/main.py /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | tee /tmp/qa-cgfs-vf07-4.txt
```
**PASS if:** Zero matches. Port 8090 is DECOMMISSIONED.

**Gate VF-07:** All 4 checks pass. No regressions introduced.

---

## Verification Family 08 — Bookkeeping (AC-10)

### VF-08.1: CHANGES.md entry lists all 9 modified files
```bash
grep -A20 "COL-GAP-FULLSTACK-001" /home/zaks/bookkeeping/CHANGES.md | grep -c "\.py\|\.tsx\|\.ts\|\.sql" 2>&1 | tee /tmp/qa-cgfs-vf08-1.txt
```
**PASS if:** Count >= 9 (9 files were modified/created).

### VF-08.2: Completion report lists all 10 ACs with PASS
```bash
grep -c "PASS" /home/zaks/bookkeeping/docs/COL-GAP-FULLSTACK-001-COMPLETION.md 2>&1 | tee /tmp/qa-cgfs-vf08-2.txt
```
**PASS if:** Count >= 10 (one per AC plus verification gates).

### VF-08.3: Completion report references both gap tracks
```bash
grep -E "Quarantine FSM|Reflexion Loop" /home/zaks/bookkeeping/docs/COL-GAP-FULLSTACK-001-COMPLETION.md 2>&1 | tee /tmp/qa-cgfs-vf08-3.txt
```
**PASS if:** Both "Quarantine FSM" and "Reflexion Loop" mentioned.

**Gate VF-08:** All 3 checks pass. Documentation is complete and accurate.

---

## Cross-Consistency Checks (XC-1 through XC-6)

### XC-1: DealTransition TS interface fields match backend get_transitions response keys
```bash
echo "=== Backend response keys ===" | tee /tmp/qa-cgfs-xc1.txt
grep -oP '"[a-z_]+"' /home/zaks/zakops-backend/src/core/deals/workflow.py | grep -A20 "return \[" | sort -u 2>&1 | tee -a /tmp/qa-cgfs-xc1.txt
echo "=== Frontend interface keys ===" | tee -a /tmp/qa-cgfs-xc1.txt
grep -oP '\w+:' /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | grep -A8 "interface DealTransition" 2>&1 | tee -a /tmp/qa-cgfs-xc1.txt
```
**PASS if:** All 8 backend keys map to 8 frontend properties. Key name `created_at` (backend) maps to `timestamp` (frontend) — this is intentional.

### XC-2: RefinedBadgeProps type matches ChatMessage critiqueResult type
```bash
echo "=== CitationIndicator props ===" | tee /tmp/qa-cgfs-xc2.txt
grep -A8 "interface RefinedBadgeProps" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee -a /tmp/qa-cgfs-xc2.txt
echo "=== ChatMessage type ===" | tee -a /tmp/qa-cgfs-xc2.txt
grep "critiqueResult" /home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx 2>&1 | tee -a /tmp/qa-cgfs-xc2.txt
```
**PASS if:** Both types include the same 5 optional fields: severity, issues_count, should_revise, was_refined, refinement_count.

### XC-3: Migration column count matches workflow.py INSERT value count
```bash
echo "=== Migration columns ===" | tee /tmp/qa-cgfs-xc3.txt
grep -c "VARCHAR\|UUID\|TEXT\|TIMESTAMPTZ" /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql 2>&1 | tee -a /tmp/qa-cgfs-xc3.txt
echo "=== INSERT value placeholders ===" | tee -a /tmp/qa-cgfs-xc3.txt
grep "VALUES" /home/zaks/zakops-backend/src/core/deals/workflow.py | grep -oP '\$\d+' | wc -l 2>&1 | tee -a /tmp/qa-cgfs-xc3.txt
```
**PASS if:** Both counts equal 10.

### XC-4: Quarantine INSERT column subset is valid against full table schema
```bash
echo "=== Quarantine INSERT columns ===" | tee /tmp/qa-cgfs-xc4.txt
grep -A5 "INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/api/orchestration/main.py | head -4 2>&1 | tee -a /tmp/qa-cgfs-xc4.txt
```
**PASS if:** The 7 columns used (deal_id, from_stage, to_stage, actor_id, actor_type, correlation_id, reason) are a valid subset of the 10-column table. Omitted columns (id, idempotency_key, created_at) have defaults.

### XC-5: Graph.py critique_data keys match what RefinedBadge reads
```bash
echo "=== Graph.py stored keys ===" | tee /tmp/qa-cgfs-xc5.txt
grep 'critique_data\[' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee -a /tmp/qa-cgfs-xc5.txt
echo "=== Badge read keys ===" | tee -a /tmp/qa-cgfs-xc5.txt
grep -E "was_refined|refinement_count" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee -a /tmp/qa-cgfs-xc5.txt
```
**PASS if:** Graph stores `refinement_count` and `was_refined`; badge reads `was_refined` and `refinement_count`. Keys match exactly.

### XC-6: Workflow.py INSERT and quarantine main.py INSERT use same table name
```bash
grep "INSERT INTO zakops.deal_transitions" /home/zaks/zakops-backend/src/core/deals/workflow.py /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-cgfs-xc6.txt
```
**PASS if:** Both files reference exactly `zakops.deal_transitions` (same schema-qualified name).

**Gate XC:** All 6 checks pass. Cross-surface consistency is verified between backend, frontend, and agent service.

---

## Stress Tests (ST-1 through ST-8)

### ST-1: Refinement loop terminates when critique returns should_revise=False
```bash
grep -A3 "not critique.should_revise" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/qa-cgfs-st1.txt
```
**PASS if:** Guard clause returns (original_response, critique) when should_revise=False, preventing infinite loop even if MAX_REFINEMENTS is bypassed.

### ST-2: MAX_REFINEMENTS is imported, not hardcoded in graph.py
```bash
grep "refinement_count < [0-9]" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/qa-cgfs-st2.txt
```
**PASS if:** Zero matches. The loop must use the imported `MAX_REFINEMENTS` constant, not a magic number.

### ST-3: No Promise.all usage in deal detail page
```bash
grep "Promise\.all\b" /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/\[id\]/page.tsx 2>&1 | tee /tmp/qa-cgfs-st3.txt
```
**PASS if:** Zero matches. `Promise.all` is banned — only `Promise.allSettled` is allowed.

### ST-4: No raw httpx in quarantine approval (uses connection pool)
```bash
grep -n "httpx\|requests\.\|urllib" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-cgfs-st4.txt
```
**PASS if:** Zero matches in the quarantine approval section. All DB operations must use the connection pool.

### ST-5: Reflexion service is a singleton (not instantiated per-call)
```bash
grep "reflexion_service = ReflexionService()" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/qa-cgfs-st5.txt
```
**PASS if:** Singleton instantiation exists at module level. Per-call instantiation would waste resources.

### ST-6: Snapshot UPDATE uses parameterized queries (SQL injection safe)
```bash
grep -A5 "UPDATE turn_snapshots" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py | grep '\$' 2>&1 | tee /tmp/qa-cgfs-st6.txt
```
**PASS if:** Uses `$1, $2, $3` placeholders (parameterized). FAIL if string formatting/f-strings are used.

### ST-7: Migration uses IF NOT EXISTS (idempotent re-run safe)
```bash
grep "IF NOT EXISTS" /home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql 2>&1 | tee /tmp/qa-cgfs-st7.txt
```
**PASS if:** Both CREATE TABLE and CREATE INDEX use `IF NOT EXISTS`.

### ST-8: No console.error for expected degradation paths
```bash
grep "console.error" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | grep -i "transition" 2>&1 | tee /tmp/qa-cgfs-st8.txt
```
**PASS if:** Zero matches. getDealTransitions uses console.warn for expected failures (per Surface 9 convention).

**Gate ST:** All 8 stress tests pass. Implementation is resilient to edge cases, follows security best practices, and respects architectural conventions.

---

## Remediation Protocol

When a gate FAILs:

1. **Read the evidence file** — understand what was expected vs. what was found
2. **Classify the failure:**
   - `MISSING_FIX` — The execution mission didn't implement this
   - `REGRESSION` — Code broke something that worked before
   - `SCOPE_GAP` — Not in original mission scope but should have been
   - `FALSE_POSITIVE` — Gate check is wrong, code is correct
   - `PARTIAL` — Partially implemented, needs completion
   - `VIOLATION` — Architectural constraint violated
3. **Apply fix** following original guardrails (no new features, no redesign)
4. **Re-run the specific gate** — capture new evidence
5. **Re-run `make validate-local`** — verify no regressions from the fix
6. **Record in completion report** — remediation ID, what was wrong, what was fixed

---

## Enhancement Opportunities (ENH-1 through ENH-10)

### ENH-1: Live endpoint test for transitions API
Add a gate that curls `GET /api/deals/{known_deal_id}/transitions` and validates the JSON response shape. Requires backend running.

### ENH-2: Reflexion integration test with mock LLM
Create a test that exercises the full critique → refine → re-critique loop with deterministic mock responses, verifying convergence.

### ENH-3: Deal transitions count in pipeline summary
Surface transition count in the pipeline summary view alongside deal counts per stage.

### ENH-4: Refinement quality metrics dashboard
Track refinement_count distribution across conversations to identify if the reflexion heuristic is too aggressive or too lenient.

### ENH-5: OpenAPI spec update for transitions endpoint
Verify `packages/contracts/openapi/zakops-api.json` includes the transitions endpoint schema and run `make sync-types` to propagate.

### ENH-6: E2E test for transitions timeline rendering
Add Playwright or Cypress test that creates a deal, transitions it, and verifies the timeline tab renders correctly.

### ENH-7: Rollback migration automated test
Add a gate that runs the rollback, verifies table is gone, re-runs forward migration, verifies table exists.

### ENH-8: Critique result schema validation
Add Zod schema validation for the critiqueResult field in the chat stream to catch shape mismatches early.

### ENH-9: Transition audit for existing deals
Backfill historical deal_transitions for deals that were created before the migration, using audit_trail JSONB data.

### ENH-10: Reflexion loop telemetry
Log refinement iteration timing to identify if the loop introduces unacceptable latency for the user.

---

## Scorecard Template

```
QA-CGFS-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]  — validate-local baseline
  PF-2: [ PASS / FAIL ]  — tsc compilation
  PF-3: [ PASS / FAIL ]  — completion report exists
  PF-4: [ PASS / FAIL ]  — CHANGES.md entry
  PF-5: [ PASS / FAIL / SKIP ]  — database reachable

Verification Gates:
  VF-01 (DB Migration):     __ / 10 gates PASS
  VF-02 (Quarantine Ledger): __ / 7 gates PASS
  VF-03 (Transitions API):  __ / 7 gates PASS
  VF-04 (Dashboard Timeline): __ / 11 gates PASS
  VF-05 (Reflexion Loop):   __ / 14 gates PASS
  VF-06 (Chat Badge):       __ / 7 gates PASS
  VF-07 (No Regressions):   __ / 4 gates PASS
  VF-08 (Bookkeeping):      __ / 3 gates PASS

Cross-Consistency:
  XC-1 through XC-6:        __ / 6 gates PASS

Stress Tests:
  ST-1 through ST-8:        __ / 8 gates PASS

Total: __ / 82 gates PASS, __ FAIL, __ INFO
  (5 PF + 63 VF + 6 XC + 8 ST = 82 total)

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## Guardrails

1. **Scope fence:** This is a QA verification mission. Do not build new features, add endpoints, or create new UI components.
2. **Remediate, don't redesign.** Fixes must follow the original implementation pattern — do not refactor during QA.
3. **Evidence-based only.** Every PASS needs `tee`'d output. "I checked and it's fine" is never evidence.
4. **Generated files are read-only.** Never edit `*.generated.ts` or `*_models.py` — per deny rules.
5. **WSL safety.** If any .sh files are created during remediation: `sed -i 's/\r$//'` + `sudo chown zaks:zaks`.
6. **Services-down accommodation.** If PF-5 fails (DB unreachable), DB-dependent gates become SKIP, not FAIL. Code verification continues.
7. **Preserve prior fixes.** Remediation must not revert earlier work from COL-GAP-FULLSTACK-001 or any predecessor mission.
8. **Per contract surface discipline.** If remediation touches API boundaries, run appropriate `make sync-*` commands.
9. **Port 8090 is FORBIDDEN.** Do not reference or use.

---

## Executor Self-Check Prompts

### After Pre-Flight:
- [ ] "Did PF-5 pass? If not, did I mark DB gates as SKIP?"
- [ ] "Is the baseline clean, or am I inheriting pre-existing failures?"

### After each Verification Family:
- [ ] "Did I run EVERY gate, or did I skip some because I assumed they'd pass?"
- [ ] "Did I capture evidence to /tmp/ files for every check?"
- [ ] "If a gate FAILed, did I classify it correctly before attempting a fix?"

### Before marking mission COMPLETE:
- [ ] "Does `make validate-local` pass RIGHT NOW, not earlier in the session?"
- [ ] "Did I fill in the complete scorecard with gate counts?"
- [ ] "Did I record all remediations with before/after evidence?"
- [ ] "Is my total gate count exactly 82 (5 PF + 63 VF + 6 XC + 8 ST)?"

---

## File Paths Reference

### Files to Verify (sources of truth — do NOT modify unless remediating a FAIL)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger.sql` | Forward migration |
| `/home/zaks/zakops-backend/db/migrations/031_deal_transitions_ledger_rollback.sql` | Rollback migration |
| `/home/zaks/zakops-backend/src/core/deals/workflow.py` | Deal workflow engine (INSERT + get_transitions) |
| `/home/zaks/zakops-backend/src/api/orchestration/routers/workflow.py` | GET transitions endpoint |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Quarantine approval flow |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` | Reflexion service |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py` | LangGraph refinement loop |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | getDealTransitions API function |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | Deal detail page with transitions tab |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx` | RefinedBadge component |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx` | ChatMessage type |
| `/home/zaks/bookkeeping/docs/COL-GAP-FULLSTACK-001-COMPLETION.md` | Completion report |
| `/home/zaks/bookkeeping/CHANGES.md` | Change log |

### Evidence Output Directory
All evidence files written to `/tmp/qa-cgfs-*.txt` (82 files expected).

---

## Crash Recovery (per IA-2)

If resuming after a session crash, run these 3 commands to determine current state:
1. `ls /tmp/qa-cgfs-*.txt | wc -l` — how many gates have been run
2. `grep "FAIL\|PASS" /tmp/qa-cgfs-*.txt | tail -5` — last 5 gate results
3. `cd /home/zaks/zakops-agent-api && make validate-local` — current validation state

Resume from the first unexecuted gate.

---

## Stop Condition

Stop when all 82 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` passes, and the scorecard is complete with evidence files for every gate.

Do NOT proceed to build new features, create new missions, or modify infrastructure beyond remediation.

---

*End of Mission Prompt — QA-CGFS-VERIFY-001*
