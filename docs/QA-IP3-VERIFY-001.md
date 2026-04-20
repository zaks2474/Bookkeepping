# MISSION: QA-IP3-VERIFY-001
## Independent Verification & Remediation — Integration Phase 3 (Bi-directional Communication)
## Date: 2026-02-18
## Classification: QA Verification & Remediation
## Prerequisite: INTEGRATION-PHASE3-BUILD-001 (Complete 2026-02-18)
## Successor: None

---

## Mission Objective

Independent verification of INTEGRATION-PHASE3-BUILD-001 — the final integration phase closing the bi-directional communication loop between ZakOps dashboard and LangSmith Exec Agent. This mission verifies 6 deliverables (LeaseReaper, Gmail Back-Labeling, Event Polling Expansion, Operator Messaging, Delegation UX, @ensure_dict_response decorator) across 8 acceptance criteria with fresh evidence.

Source material:
- Completion report: `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE3-BUILD-001-COMPLETION.md`
- Evidence directory: `/home/zaks/bookkeeping/qa-verifications/QA-IP3-VERIFY-001/`

This is a **VERIFY mission** — verify, cross-check, stress-test, and remediate. Do not build new features.

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-ip3-pf1.txt
```
**PASS if:** exit 0.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-ip3-pf2.txt
```
**PASS if:** exit 0, zero errors.

### PF-3: Evidence Directory
```bash
ls -la /home/zaks/bookkeeping/qa-verifications/QA-IP3-VERIFY-001/ | tee /tmp/qa-ip3-pf3.txt
```
**PASS if:** Directory exists and is writable.

### PF-4: Source Files Present
```bash
for f in \
  /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/lease_reaper.py \
  /home/zaks/zakops-agent-api/apps/backend/db/migrations/037_task_messages.sql \
  /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/history/route.ts \
  /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py \
  /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts; do
  [ -f "$f" ] && echo "PRESENT: $f" || echo "MISSING: $f"
done 2>&1 | tee /tmp/qa-ip3-pf4.txt
```
**PASS if:** All 5 files PRESENT, zero MISSING.

---

## Verification Families

## VF-01 — LeaseReaper (AC-1, D1)

### VF-01.1: LeaseReaper class exists with correct pattern
```bash
grep -n "class LeaseReaper" /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/lease_reaper.py | tee /tmp/qa-ip3-vf01-1.txt
```
**PASS if:** Class definition found.

### VF-01.2: Reaper follows OutboxProcessor pattern (asyncio.create_task)
```bash
grep -n "asyncio.create_task\|async def _run\|async def _reap\|async def start\|async def stop" /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/lease_reaper.py | tee /tmp/qa-ip3-vf01-2.txt
```
**PASS if:** All 5 patterns found (create_task, _run, _reap, start, stop).

### VF-01.3: Reaper reclaims expired leases (SQL sets status=queued, nulls lease fields)
```bash
grep -n "queued\|lease_owner_id.*NULL\|lease_expires_at.*NULL" /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/lease_reaper.py | tee /tmp/qa-ip3-vf01-3.txt
```
**PASS if:** SQL resets status to 'queued' and nulls lease fields.

### VF-01.4: Reaper starts conditionally on delegate_actions flag
```bash
grep -n "delegate_actions\|start_lease_reaper\|stop_lease_reaper" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | tee /tmp/qa-ip3-vf01-4.txt
```
**PASS if:** start_lease_reaper called within delegate_actions conditional block.

### VF-01.5: Health endpoint reports lease_reaper_active
```bash
grep -n "lease_reaper_active\|_is_lease_reaper_active" /home/zaks/zakops-agent-api/apps/backend/src/api/shared/routers/health.py | tee /tmp/qa-ip3-vf01-5.txt
```
**PASS if:** lease_reaper_active appears in health response.

### VF-01.6: Reaper records deal events on reclaim
```bash
grep -n "record_deal_event\|deal_event" /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/lease_reaper.py | tee /tmp/qa-ip3-vf01-6.txt
```
**PASS if:** record_deal_event called for reclaimed tasks.

**Gate VF-01:** All 6 checks pass. LeaseReaper is fully integrated with correct lifecycle, SQL, health, and audit trail.

---

## VF-02 — Gmail Back-Labeling (AC-2, D2)

### VF-02.1: _maybe_create_backfill_task function exists
```bash
grep -n "_maybe_create_backfill_task" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | tee /tmp/qa-ip3-vf02-1.txt
```
**PASS if:** Function definition and at least one call site found.

### VF-02.2: Backfill task gated by delegate_actions flag
```bash
grep -A5 "def _maybe_create_backfill_task\|delegate_actions" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | grep -B2 -A2 "delegate_actions" | head -20 | tee /tmp/qa-ip3-vf02-2.txt
```
**PASS if:** delegate_actions check appears in or near the function.

### VF-02.3: Failure does not propagate (try/except pattern)
```bash
grep -A20 "def _maybe_create_backfill_task" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | grep -c "except" | tee /tmp/qa-ip3-vf02-3.txt
```
**PASS if:** At least 1 except clause found.

### VF-02.4: BACKFILL_LABELS documented in agent contract
```bash
grep -n "BACKFILL_LABELS\|backfill_labels\|Back-Label" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py | tee /tmp/qa-ip3-vf02-4.txt
```
**PASS if:** BACKFILL_LABELS workflow documented.

**Gate VF-02:** All 4 checks pass. Back-labeling is feature-gated, fail-safe, and documented.

---

## VF-03 — Event Polling Expansion (AC-3, D3)

### VF-03.1: GET /api/events/history endpoint exists
```bash
grep -n "events/history\|events_history" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | tee /tmp/qa-ip3-vf03-1.txt
```
**PASS if:** Endpoint route definition found.

### VF-03.2: Requires since_ts or deal_id (400 on missing params)
```bash
grep -A30 "events/history\|events_history" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | grep -n "400\|since_ts\|deal_id\|at least" | tee /tmp/qa-ip3-vf03-2.txt
```
**PASS if:** 400 response for missing params and since_ts/deal_id parameter handling found.

### VF-03.3: since_ts uses datetime.fromisoformat (not raw string to asyncpg)
```bash
grep -n "fromisoformat\|datetime.*since" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | tee /tmp/qa-ip3-vf03-3.txt
```
**PASS if:** fromisoformat parsing found (the bug fix from execution).

### VF-03.4: Dashboard route handler exists at events/history/route.ts
```bash
cat /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/history/route.ts | head -30 | tee /tmp/qa-ip3-vf03-4.txt
```
**PASS if:** File exists with GET export and backendFetch proxy.

### VF-03.5: MCP bridge events tool updated with optional deal_id
```bash
grep -n "deal_id\|since_ts\|recent_events\|list_recent_events" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-vf03-5.txt
```
**PASS if:** deal_id is optional parameter in events tool.

**Gate VF-03:** All 5 checks pass. Event polling is deal-agnostic with proper parameter validation.

---

## VF-04 — Operator Messaging (AC-4, D4)

### VF-04.1: POST /api/tasks/{id}/message endpoint exists
```bash
grep -n "tasks.*message\|task_id.*message\|TaskMessageRequest" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | tee /tmp/qa-ip3-vf04-1.txt
```
**PASS if:** Endpoint definition and request model found.

### VF-04.2: Rejects terminal tasks (completed/failed/dead_letter)
```bash
grep -A40 "TaskMessageRequest\|tasks.*message" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | grep -n "completed\|failed\|dead_letter\|terminal" | tee /tmp/qa-ip3-vf04-2.txt
```
**PASS if:** Terminal status check found with 400 response.

### VF-04.3: Migration 037 adds messages JSONB column
```bash
cat /home/zaks/zakops-agent-api/apps/backend/db/migrations/037_task_messages.sql | tee /tmp/qa-ip3-vf04-3.txt
```
**PASS if:** ALTER TABLE adds messages JSONB DEFAULT '[]' with IF NOT EXISTS.

### VF-04.4: Rollback migration drops messages column
```bash
cat /home/zaks/zakops-agent-api/apps/backend/db/migrations/037_task_messages_rollback.sql | tee /tmp/qa-ip3-vf04-4.txt
```
**PASS if:** DROP COLUMN messages IF EXISTS in transaction.

### VF-04.5: Dashboard sendTaskMessage function exists
```bash
grep -n "sendTaskMessage\|task.*message\|taskMessage" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | tee /tmp/qa-ip3-vf04-5.txt
```
**PASS if:** Function exported with POST to /api/tasks/{id}/message.

### VF-04.6: MCP bridge task_messages tool exists
```bash
grep -n "task_messages\|get_task_messages\|zakops_get_task_messages" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-vf04-6.txt
```
**PASS if:** Tool function defined and registered.

### VF-04.7: Agent contract includes messages tool definition
```bash
grep -n "message\|task_messages" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py | tee /tmp/qa-ip3-vf04-7.txt
```
**PASS if:** Messages tool documented in agent contract.

**Gate VF-04:** All 7 checks pass. Messaging pipeline complete from backend through MCP to dashboard.

---

## VF-05 — Dashboard Delegation UX (AC-5, D5)

### VF-05.1: DelegationDisabledError class exists
```bash
grep -n "DelegationDisabledError\|class.*Delegation.*Error" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | tee /tmp/qa-ip3-vf05-1.txt
```
**PASS if:** Custom error class found.

### VF-05.2: 503 detection in getDelegationTypes and createDelegatedTask
```bash
grep -n "503\|DelegationDisabledError" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts | tee /tmp/qa-ip3-vf05-2.txt
```
**PASS if:** 503 status check in both functions, throws DelegationDisabledError.

### VF-05.3: UI shows delegation disabled toast
```bash
grep -n "DelegationDisabledError\|delegation.*disabled\|Delegation is disabled" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx | tee /tmp/qa-ip3-vf05-3.txt
```
**PASS if:** DelegationDisabledError catch with user-facing toast message.

**Gate VF-05:** All 3 checks pass. 503 detection and UX notification working.

---

## VF-06 — @ensure_dict_response Decorator (AC-6, D6)

### VF-06.1: Decorator defined with functools.wraps
```bash
grep -n "ensure_dict_response\|functools.wraps" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-vf06-1.txt
```
**PASS if:** Decorator definition found with functools.wraps.

### VF-06.2: Applied to exactly 9 MCP tool functions
```bash
grep -c "@ensure_dict_response" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-vf06-2.txt
```
**PASS if:** Count is exactly 9.

### VF-06.3: No remaining manual _ensure_dict(resp.json()) calls
```bash
grep -n "_ensure_dict(resp" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-vf06-3.txt
```
**PASS if:** Zero matches (all manual calls replaced by decorator).

### VF-06.4: Manifest prompt_version updated
```bash
grep -n "prompt_version\|v1.0-integration-phase3" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-vf06-4.txt
```
**PASS if:** prompt_version contains "v1.0-integration-phase3".

**Gate VF-06:** All 4 checks pass. Decorator replaces manual calls, manifest updated.

---

## VF-07 — Contract Surface Validation (AC-7)

### VF-07.1: make validate-local passes
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-ip3-vf07-1.txt
```
**PASS if:** Exit 0, "All local validations passed".

### VF-07.2: TypeScript compiles clean
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-ip3-vf07-2.txt
```
**PASS if:** Exit 0.

**Gate VF-07:** Both checks pass. Contract surfaces valid.

---

## VF-08 — Completion Report Quality (AC-8)

### VF-08.1: Completion report exists with all sections
```bash
head -40 /home/zaks/bookkeeping/docs/INTEGRATION-PHASE3-BUILD-001-COMPLETION.md | tee /tmp/qa-ip3-vf08-1.txt
```
**PASS if:** Report contains Mission Summary, AC Results, Deliverables.

### VF-08.2: All 8 AC reported as PASS
```bash
grep -c "| PASS" /home/zaks/bookkeeping/docs/INTEGRATION-PHASE3-BUILD-001-COMPLETION.md | tee /tmp/qa-ip3-vf08-2.txt
```
**PASS if:** Count >= 8.

### VF-08.3: Files Created and Modified sections present
```bash
grep -c "Files Created\|Files Modified" /home/zaks/bookkeeping/docs/INTEGRATION-PHASE3-BUILD-001-COMPLETION.md | tee /tmp/qa-ip3-vf08-3.txt
```
**PASS if:** Both sections present (count >= 2).

**Gate VF-08:** All 3 checks pass. Completion report is complete.

---

## Cross-Consistency Checks

### XC-1: Decorator count matches completion report claim (9 sites)
Verify the completion report's claim of "9 manual call sites" replaced.
```bash
echo "Decorator uses:" && grep -c "@ensure_dict_response" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py && echo "Remaining manual calls:" && grep -c "_ensure_dict(resp" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>/dev/null; echo "done" | tee /tmp/qa-ip3-xc1.txt
```
**PASS if:** Decorator count = 9, manual calls = 0.

### XC-2: MCP tool count matches manifest (24 tools claimed)
```bash
grep -c "def zakops_\|def rag_" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-xc2.txt
```
**PASS if:** Tool function count aligns with manifest claim of 24.

### XC-3: Migration numbering sequential (037 follows 036)
```bash
ls /home/zaks/zakops-agent-api/apps/backend/db/migrations/03[5-8]* 2>/dev/null | tee /tmp/qa-ip3-xc3.txt
```
**PASS if:** 037 follows sequentially from prior migration (no gaps, no conflicts).

### XC-4: Agent contract tool list matches server.py registrations
```bash
echo "=== Contract tools ===" && grep -c "zakops_\|rag_" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py && echo "=== Server tools ===" && grep -c "def zakops_\|def rag_" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | tee /tmp/qa-ip3-xc4.txt
```
**PASS if:** Tool counts are consistent between contract and server.

### XC-5: Dashboard route.ts proxies correct backend path
```bash
grep "events/history" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/history/route.ts | tee /tmp/qa-ip3-xc5.txt
```
**PASS if:** Proxy target matches backend endpoint path `/api/events/history`.

---

## Stress Tests

### ST-1: No orphaned imports (lease_reaper imported but unused)
```bash
grep -n "from.*lease_reaper\|import.*lease_reaper" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | tee /tmp/qa-ip3-st1.txt
```
**PASS if:** All imports are actually used in the file.

### ST-2: Terminal status consistency (dead_letter defined everywhere it's needed)
```bash
grep -rn "dead_letter" /home/zaks/zakops-agent-api/apps/backend/src/ 2>/dev/null | tee /tmp/qa-ip3-st2.txt
```
**PASS if:** dead_letter status is consistently defined across all status check points.

### ST-3: Feature flag gate consistency (delegate_actions checked at all write paths)
```bash
grep -n "delegate_actions" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | tee /tmp/qa-ip3-st3.txt
```
**PASS if:** delegate_actions checked before all delegation write operations.

### ST-4: No raw string since_ts passed to asyncpg (the bug that was fixed)
```bash
grep -B5 -A5 "since_ts" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | grep -c "fromisoformat\|datetime" | tee /tmp/qa-ip3-st4.txt
```
**PASS if:** Count > 0 — datetime parsing present for since_ts.

### ST-5: CRLF check on new files
```bash
for f in \
  /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/lease_reaper.py \
  /home/zaks/zakops-agent-api/apps/backend/db/migrations/037_task_messages.sql \
  /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/history/route.ts; do
  CR=$(od -c "$f" | grep -c '\\r') || CR=0
  echo "$f: CR_COUNT=$CR"
done 2>&1 | tee /tmp/qa-ip3-st5.txt
```
**PASS if:** All CR_COUNT=0.

### ST-6: File ownership check (no root-owned files under /home/zaks/)
```bash
for f in \
  /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/lease_reaper.py \
  /home/zaks/zakops-agent-api/apps/backend/src/core/delegation/__init__.py \
  /home/zaks/zakops-agent-api/apps/backend/db/migrations/037_task_messages.sql \
  /home/zaks/zakops-agent-api/apps/backend/db/migrations/037_task_messages_rollback.sql \
  /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/history/route.ts; do
  OWNER=$(stat -c '%U' "$f")
  echo "$f: owner=$OWNER"
done 2>&1 | tee /tmp/qa-ip3-st6.txt
```
**PASS if:** All files owned by zaks (not root).

---

## Remediation Protocol

1. Read the evidence file for the failed gate
2. Classify: MISSING_FIX / REGRESSION / SCOPE_GAP / FALSE_POSITIVE / PARTIAL / VIOLATION
3. Apply fix following original guardrails (per contract surface discipline)
4. Re-run specific gate
5. Re-run `make validate-local`
6. Record in scorecard

---

## Enhancement Opportunities

### ENH-1: zakops_get_task_messages missing @ensure_dict_response
The new tool function doesn't use the decorator that was applied to all 9 other tools. While it returns dict directly, adding the decorator would ensure consistency.

### ENH-2: Event history response shape inconsistency
GET /api/deals/{deal_id}/events returns array; GET /api/events/history returns wrapped dict {events, count}. Standardize to wrapped dict for all event endpoints.

### ENH-3: sendTaskMessage error handling divergence
sendTaskMessage silently catches all errors while getDelegationTypes/createDelegatedTask throw DelegationDisabledError on 503. Standardize error propagation pattern.

### ENH-4: Message panel lacks polling for agent responses
UI sends messages but never displays agent replies. Future: add polling to show conversation history.

### ENH-5: No rate limiting on task message endpoint
POST /api/tasks/{id}/message has no rate limiting. Could allow message spam.

### ENH-6: Message panel has no close/dismiss UI
Once messageTaskId is set, the message panel has no way to close it.

### ENH-7: dead_letter status cross-reference
The dead_letter terminal status is used in message endpoint but may not be consistently defined across all task status enums.

### ENH-8: Lease reaper interval not configurable via env
Poll interval is hardcoded at 30s. Could be configurable via environment variable.

---

## Scorecard Template

```
QA-IP3-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: Claude Code (Opus 4.6)

Pre-Flight:
  PF-1 (validate-local):    [ PASS / FAIL ]
  PF-2 (tsc):               [ PASS / FAIL ]
  PF-3 (evidence dir):      [ PASS / FAIL ]
  PF-4 (source files):      [ PASS / FAIL ]

Verification Gates:
  VF-01 (LeaseReaper):        __ / 6 gates PASS
  VF-02 (Back-Labeling):      __ / 4 gates PASS
  VF-03 (Event Polling):      __ / 5 gates PASS
  VF-04 (Messaging):          __ / 7 gates PASS
  VF-05 (Delegation UX):      __ / 3 gates PASS
  VF-06 (Decorator):          __ / 4 gates PASS
  VF-07 (Contract Surfaces):  __ / 2 gates PASS
  VF-08 (Completion Report):  __ / 3 gates PASS

Cross-Consistency:
  XC-1 through XC-5:          __ / 5 gates PASS

Stress Tests:
  ST-1 through ST-6:          __ / 6 gates PASS

Total: __ / 45 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 8 (ENH-1 through ENH-8)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## Guardrails

1. Do not build new features — this is a QA mission
2. Remediate, don't redesign
3. Evidence-based only — every PASS needs tee'd output
4. ENH items are not failures — mark as INFO
5. Services-down accommodation — live gates become SKIP, not FAIL
6. Do not modify generated files (per contract surface discipline)
7. WSL safety (CRLF + ownership) on any remediated files
8. Preserve prior Phase 1 and Phase 2 fixes — remediation must not revert earlier work

## Stop Condition

Stop when all 45 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` passes, and the scorecard is complete.

---

*End of Mission Prompt — QA-IP3-VERIFY-001*
