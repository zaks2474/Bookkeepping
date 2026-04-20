> **POST-CONSOLIDATION NOTE (2026-02-16):** This document references `/home/zaks/zakops-backend/` paths
> which are now at `/home/zaks/zakops-agent-api/apps/backend/` after the monorepo consolidation
> (MONOREPO-CONSOLIDATION-001). Verification commands referencing the old standalone repo will not work.
> See `POST-MERGE-INCIDENT-RCA-2026-02-16.md` for the full path mapping.

# MISSION: QA-MASTER-PROGRAM-VERIFY-001A
## SM-1 Pipeline Hardening Verification (17 Forensic Findings)
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: INTAKE-READY-001 (COMPLETE), COL-V2-BUILD QA (001A + 001B FULL PASS)
## Successor: QA-MASTER-PROGRAM-VERIFY-001B

---

## Preamble: Builder Operating Context

This is an independent QA verification mission. It verifies implementation quality for SM-1 (INTAKE-READY-001) from the master program ZAKOPS-INTAKE-COL-V2-001. The builder already loads CLAUDE.md, MEMORY.md, hooks, rules, and deny rules at session start. This mission adds verification-specific scope and evidence requirements.

**Important:** SM-2/SM-3/SM-4 agent-api + dashboard work was already QA'd by QA-COL-BUILD-VERIFY-001A (67/67 effective) and QA-COL-BUILD-VERIFY-001B (56/56 PASS). This mission covers SM-1 only — the pipeline hardening work in zakops-backend, Zaks-llm, and agent-api config that those prior QA missions did NOT cover.

---

## 1. Mission Objective

Independent verification of SM-1 (INTAKE-READY-001): 17 forensic findings (F-1 through F-17) from the TriPass audit (TP-20260213-163446), 7 readiness gates, shadow-mode injection infrastructure, and 2 database migrations across 3 repositories.

| Source | Path |
|--------|------|
| Master Program | `/home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md` |
| Program Checkpoint | `/home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md` |
| TriPass Forensic Audit | `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/FINAL_MASTER.md` |

This QA mission will **verify, cross-check, stress-test, and remediate** all 17 findings and the shadow-mode infrastructure. It does NOT build new features or modify the agent-api intelligence services (already QA'd).

### Coverage Map

| Finding | Severity | Repo | What to verify |
|---------|----------|------|----------------|
| F-1 | P0 | zakops-backend | MCP `/review` → `/process` |
| F-3 | P0 | zakops-backend | Quarantine UNIQUE on message_id |
| F-4 | P0 | zakops-agent-api | Docker DATABASE_URL → zakops_agent |
| F-5 | P0 | Zaks-llm + backend | Legacy `.deal-registry` decommissioned |
| F-6 | P1 | zakops-backend | Approval routes through workflow engine |
| F-7 | P1 | zakops-backend + dashboard | Email settings wired to real endpoint |
| F-8 | P1 | zakops-backend | correlation_id column on quarantine_items |
| F-9 | P1 | zakops-backend | Schema-qualified idempotency + fail-closed |
| F-10 | P1 | zakops-backend + dashboard | Bulk-delete route alignment |
| F-11 | P2 | zakops-backend | Quarantine status CHECK constraint |
| F-12 | P2 | zakops-backend | Default stage = 'inbound' not 'lead' |
| F-13 | P1 | zakops-backend | Retention cleanup column fix |
| F-14 | P2 | zakops-agent-api | Duplicate VALID_TRANSITIONS removed |
| F-15 | P3 | zakops-backend | Agent contract docstring fix |
| F-16 | P2 | zakops-backend | Attachment linkage post-promotion |
| F-17 | P3 | zakops-backend | OAuth state ADR-004 |
| Shadow | Enhancement | zakops-backend + dashboard | source_type, injection_metadata, shadow badge |

### Evidence Directory

All gate evidence is captured to:
```
/home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/
```

### Out of Scope

- SM-2/SM-3/SM-4 agent-api intelligence services (covered by QA-COL-BUILD-VERIFY-001A/B)
- New feature development
- Backend API redesign

---

## 2. Pre-Flight (PF)

### PF-1: Validation Baseline

```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/PF-01.txt
```

**PASS if:** exit 0. If not, stop -- codebase is broken before QA starts.

### PF-2: Backend Health

```bash
curl -sf http://localhost:8091/health 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/PF-02.txt
```

**PASS if:** Returns 200. If backend is down, live verification gates (VF-01 through VF-06, VF-09, ST-2 through ST-5) become code-only with SKIP note for live checks.

### PF-3: Program Checkpoint Status

```bash
cat /home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/PF-03.txt
```

**PASS if:** Shows SM-1 STATUS: COMPLETE

### PF-4: Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a && echo "evidence dir ready" | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/PF-04.txt
```

**PASS if:** Directory created or exists

### PF-5: TypeScript Compilation

```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/PF-05.txt
```

**PASS if:** exit 0

---

## 3. Verification Families (VF)

## Verification Family 01 -- F-1: MCP Endpoint Fix

### VF-01.1: No /review references in MCP server

```bash
grep -n '/review' /home/zaks/zakops-backend/mcp_server/server.py | grep -v '#' | grep -v test 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-01-1.txt
```

**PASS if:** Zero matches (exit 1 = no matches = PASS)

### VF-01.2: /process references present

```bash
grep -cn '/process' /home/zaks/zakops-backend/mcp_server/server.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-01-2.txt
```

**PASS if:** Count >= 2

**Gate VF-01:** Both checks pass. MCP server uses /process, not /review.

---

## Verification Family 02 -- F-3: Quarantine Dedup Constraint

### VF-02.1: UNIQUE constraint on message_id

```bash
psql -h localhost -U zakops -d zakops -c "\d zakops.quarantine_items" 2>&1 | grep -i "unique\|message_id" | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-02-1.txt
```

**PASS if:** UNIQUE constraint on message_id visible. **If backend DB down:** Check migration file instead: `grep -n 'UNIQUE.*message_id\|message_id.*UNIQUE' /home/zaks/zakops-backend/db/migrations/029*.sql`

### VF-02.2: ON CONFLICT in quarantine INSERT path

```bash
grep -n "ON CONFLICT.*message_id\|ON CONFLICT" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-02-2.txt
```

**PASS if:** ON CONFLICT clause found in quarantine insert

### VF-02.3: Migration file exists

```bash
ls -la /home/zaks/zakops-backend/db/migrations/029* 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-02-3.txt
```

**PASS if:** 029 migration file(s) exist

**Gate VF-02:** All 3 checks pass. Quarantine dedup enforced at DB level.

---

## Verification Family 03 -- F-4: Agent DB Config

### VF-03.1: DATABASE_URL points to zakops_agent

```bash
grep -n 'DATABASE_URL' /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-03-1.txt
```

**PASS if:** DATABASE_URL references `zakops_agent` (not bare `zakops`)

### VF-03.2: No drift to wrong DB name

```bash
grep 'DATABASE_URL.*zakops[^_]' /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-03-2.txt
```

**PASS if:** Zero matches (exit 1 = PASS)

**Gate VF-03:** Both checks pass. Agent-api targets correct database.

---

## Verification Family 04 -- F-5: Legacy Shadow Truth Decommissioned

### VF-04.1: No .deal-registry in production Python

```bash
grep -rn '.deal-registry' /home/zaks/zakops-backend/src/ /home/zaks/Zaks-llm/src/ --include='*.py' | grep -v test | grep -v '#' 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-04-1.txt
```

**PASS if:** Zero production matches. If matches exist, classify: legitimate deal-brain storage paths are acceptable; legacy shadow-truth paths reading/writing `.deal-registry` for deal CRUD are violations.

### VF-04.2: Zaks-llm shadow endpoints disabled

```bash
grep -n '/api/deals\|/api/quarantine' /home/zaks/Zaks-llm/src/api/rag_rest_api.py 2>&1 | head -20 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-04-2.txt
```

**PASS if:** Endpoints return 410 Gone or are removed entirely. If endpoints still serve live data from filesystem, that is a FAIL.

### VF-04.3: No dual-write adapter

```bash
grep -n 'dual.write\|shadow.write\|DualWriteAdapter' /home/zaks/zakops-backend/src/core/database/adapter.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-04-3.txt
```

**PASS if:** No dual-write patterns. Zero matches (exit 1 = PASS) or file structure cleaned.

**Gate VF-04:** All 3 checks pass. Single source of truth enforced.

---

## Verification Family 05 -- F-6: FSM/Outbox Enforcement

### VF-05.1: Quarantine approval emits outbox event

```bash
grep -n 'outbox\|deal_created\|deal_transitions\|workflow\|WorkflowEngine' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -20 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-05-1.txt
```

**PASS if:** Approval path references workflow engine or outbox event emission

### VF-05.2: No raw INSERT into deals bypassing workflow

```bash
grep -n "INSERT INTO.*deals\b" /home/zaks/zakops-backend/src/api/orchestration/main.py | grep -v '#' | grep -v 'deal_events\|deal_transitions\|quarantine' 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-05-2.txt
```

**PASS if:** If INSERT INTO deals exists, it must be paired with deal_transitions/outbox writes in the same transaction. Lone INSERT is a FAIL.

**Gate VF-05:** Both checks pass. Deal creation routes through workflow engine.

---

## Verification Family 06 -- F-9: Idempotency Hardening

### VF-06.1: Schema-qualified references

```bash
grep -cn "zakops.idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-06-1.txt
```

**PASS if:** Count >= 2

### VF-06.2: No unqualified idempotency_keys

```bash
grep -n "FROM idempotency_keys\|INTO idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py | grep -v 'zakops\.' 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-06-2.txt
```

**PASS if:** Zero unqualified references (exit 1 = PASS)

### VF-06.3: Fail-closed on DB error

```bash
grep -n "503\|Service temporarily\|fail.closed\|raise.*HTTP" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-06-3.txt
```

**PASS if:** 503 error raised on idempotency check failure (not silently proceeding)

**Gate VF-06:** All 3 checks pass. Idempotency is schema-qualified and fail-closed.

---

## Verification Family 07 -- F-8: Correlation ID

### VF-07.1: correlation_id column exists

```bash
grep -n "correlation_id" /home/zaks/zakops-backend/db/migrations/029*.sql 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-07-1.txt
```

**PASS if:** correlation_id column in migration

### VF-07.2: Correlation ID captured in quarantine INSERT

```bash
grep -n "correlation_id\|X-Correlation-ID\|x-correlation-id" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-07-2.txt
```

**PASS if:** Correlation ID read from header and stored

**Gate VF-07:** Both checks pass. Correlation ID propagated into quarantine.

---

## Verification Family 08 -- F-10, F-11, F-12, F-13: Pipeline Correctness

### VF-08.1: Bulk-delete alignment (F-10)

```bash
grep -n "bulk.delete\|bulk-delete\|bulk_delete" /home/zaks/zakops-backend/src/api/orchestration/main.py /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-08-1.txt
```

**PASS if:** Either backend route exists AND dashboard calls it, OR dashboard call removed. No dangling client-side calls to nonexistent endpoints.

### VF-08.2: Status CHECK constraint (F-11)

```bash
grep -n "CHECK.*status\|chk_quarantine_status" /home/zaks/zakops-backend/db/migrations/029*.sql 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-08-2.txt
```

**PASS if:** CHECK constraint in migration limiting status values

### VF-08.3: Default stage = inbound (F-12)

```bash
grep -n "inbound\|DEFAULT.*stage\|default.*inbound" /home/zaks/zakops-backend/db/migrations/029*.sql /home/zaks/zakops-backend/db/migrations/030*.sql 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-08-3.txt
```

**PASS if:** Default stage is 'inbound' not 'lead'. If not in migration, check init script: `grep "DEFAULT.*stage\|stage.*DEFAULT" /home/zaks/zakops-backend/db/init/*.sql`

### VF-08.4: Retention cleanup column fix (F-13)

```bash
grep -n "processed_by\|processing_action\|raw_content" /home/zaks/zakops-backend/src/core/retention/cleanup.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-08-4.txt
```

**PASS if:** No references to nonexistent `processed_by` or `processing_action` columns. Uses `raw_content` JSONB pattern instead.

**Gate VF-08:** All 4 checks pass. Pipeline correctness issues resolved.

---

## Verification Family 09 -- F-7: Email Settings

### VF-09.1: Email settings endpoint exists

```bash
grep -n "email.config\|email-config\|email_config" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-09-1.txt
```

**PASS if:** Email config CRUD endpoint(s) exist in backend

### VF-09.2: Dashboard proxy wired

```bash
grep -n "email" /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts 2>&1 | head -10 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-09-2.txt
```

**PASS if:** Route file exists and proxies to backend (not dead)

### VF-09.3: Email migration exists

```bash
ls -la /home/zaks/zakops-backend/db/migrations/030* 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-09-3.txt
```

**PASS if:** Migration 030 (email_config) exists

**Gate VF-09:** All 3 checks pass. Email settings wired to real endpoint.

---

## Verification Family 10 -- F-14, F-15, F-16, F-17: Low-Severity Fixes

### VF-10.1: Duplicate VALID_TRANSITIONS removed (F-14)

```bash
grep -cn "VALID_TRANSITIONS" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-10-1.txt
```

**PASS if:** Count = 0 (transitions delegated to backend) or count = 1 (single canonical source)

### VF-10.2: Agent contract docstring fix (F-15)

```bash
grep -n "Won\|Lost\|Passed\|portfolio\|junk\|archived" /home/zaks/zakops-backend/src/agent/bridge/agent_contract.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-10-2.txt
```

**PASS if:** Uses "portfolio/junk/archived" terminology, NOT "Won/Lost/Passed"

### VF-10.3: Attachment linkage post-promotion (F-16)

```bash
grep -n "attachment\|email_thread\|email_sender\|email_subject\|link.*email\|source_type" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -15 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-10-3.txt
```

**PASS if:** Deal creation enriches with email metadata (sender, subject, source_type)

### VF-10.4: OAuth state ADR-004 (F-17)

```bash
ls -la /home/zaks/zakops-backend/docs/ADR-004* 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-10-4.txt
```

**PASS if:** ADR-004 document exists

**Gate VF-10:** All 4 checks pass. Low-severity findings addressed.

---

## Verification Family 11 -- Shadow-Mode Infrastructure

### VF-11.1: source_type column in migration

```bash
grep -n "source_type" /home/zaks/zakops-backend/db/migrations/029*.sql 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-11-1.txt
```

**PASS if:** source_type column added in migration

### VF-11.2: injection_metadata column

```bash
grep -n "injection_metadata\|injected_at" /home/zaks/zakops-backend/db/migrations/029*.sql 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-11-2.txt
```

**PASS if:** injection_metadata JSONB and injected_at columns in migration. If columns not in migration, check if they exist via other means.

### VF-11.3: Quarantine endpoint accepts source_type

```bash
grep -n "source_type" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-11-3.txt
```

**PASS if:** source_type captured from request body or header in quarantine create

### VF-11.4: Shadow-mode badge in dashboard

```bash
grep -rn "shadow\|langsmith\|IconRobot\|source_type" /home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/ 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-11-4.txt
```

**PASS if:** Shadow-mode visual indicator in quarantine UI

**Gate VF-11:** All 4 checks pass. Shadow-mode infrastructure ready for LangSmith integration.

---

## Verification Family 12 -- Migration Integrity

### VF-12.1: Migration 029 has rollback

```bash
ls -la /home/zaks/zakops-backend/db/migrations/029*rollback* 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-12-1.txt
```

**PASS if:** Rollback file exists

### VF-12.2: Migration 030 has rollback

```bash
ls -la /home/zaks/zakops-backend/db/migrations/030*rollback* 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-12-2.txt
```

**PASS if:** Rollback file exists

### VF-12.3: No modification to existing migrations 001-028

```bash
git -C /home/zaks/zakops-backend diff --name-only -- 'db/migrations/0[0-2][0-8]*' 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-12-3.txt
```

**PASS if:** No existing migration files modified (empty output or exit 0)

**Gate VF-12:** All 3 checks pass. Migration integrity preserved.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Finding Register vs Codebase Agreement

```bash
echo "=== F-1 ===" && grep -c '/process' /home/zaks/zakops-backend/mcp_server/server.py
echo "=== F-3 ===" && grep -c 'ON CONFLICT' /home/zaks/zakops-backend/src/api/orchestration/main.py
echo "=== F-4 ===" && grep -c 'zakops_agent' /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml
echo "=== F-9 ===" && grep -c 'zakops.idempotency' /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py
echo "=== F-14 ===" && grep -c 'VALID_TRANSITIONS' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py
echo "CROSS-CHECK COMPLETE" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/XC-01.txt
```

**PASS if:** F-1 >= 2, F-3 >= 1, F-4 >= 1, F-9 >= 2, F-14 <= 1

### XC-2: Migration vs Schema Agreement

```bash
echo "=== 029 contents ===" && head -30 /home/zaks/zakops-backend/db/migrations/029*.sql 2>/dev/null
echo "=== 030 contents ===" && head -30 /home/zaks/zakops-backend/db/migrations/030*.sql 2>/dev/null
echo "MIGRATION REVIEW COMPLETE" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/XC-02.txt
```

**PASS if:** Migration DDL is syntactically valid and covers: UNIQUE message_id, CHECK status, correlation_id, source_type, email_config

### XC-3: TriPass Findings Complete Coverage

```bash
for f in 1 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do
  echo "F-$f: $(ls /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/VF-* 2>/dev/null | wc -l) evidence files"
done
echo "ALL 17 FINDINGS CHECKED" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/XC-03.txt
```

**PASS if:** All 17 findings have at least one verification gate with evidence

### XC-4: No Port 8090 References Introduced

```bash
grep -rn '8090' /home/zaks/zakops-backend/mcp_server/ /home/zaks/zakops-backend/src/api/orchestration/ 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/XC-04.txt
```

**PASS if:** Zero references to decommissioned port 8090

### XC-5: Dashboard Quarantine Actions Match Backend Routes

```bash
echo "=== Dashboard calls ===" && grep -n "quarantine.*approve\|quarantine.*reject\|quarantine.*delete\|quarantine.*bulk" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts
echo "=== Backend routes ===" && grep -n "@app\.\|@router\." /home/zaks/zakops-backend/src/api/orchestration/main.py | grep -i "quarantine" 2>&1 | head -20 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/XC-05.txt
```

**PASS if:** Every dashboard quarantine API call has a matching backend route. No dead buttons.

**XC Gate:** XC-1 through XC-5 all PASS.

---

## 5. Stress Tests (ST)

### ST-1: Idempotency Bypass Resistance

```bash
grep -n "except.*Exception\|except.*:\|pass$" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/ST-01.txt
```

**PASS if:** No bare `except: pass` that silently swallows idempotency failures. All exception handlers either re-raise or return 503.

### ST-2: Quarantine Injection with Duplicate message_id

```bash
echo "Code-only check: ON CONFLICT behavior"
grep -A 5 "ON CONFLICT" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/ST-02.txt
```

**PASS if:** ON CONFLICT clause does UPDATE (upsert) not silently discard

### ST-3: Shadow-Mode Cannot Auto-Promote

```bash
grep -n "auto.promot\|auto_promot\|langsmith.*approve\|shadow.*approve" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/ST-03.txt
```

**PASS if:** Zero matches (exit 1 = PASS). No auto-promotion logic exists.

### ST-4: Schema Qualification Sweep

```bash
grep -n "FROM idempotency\|FROM quarantine_items\|FROM deals\b\|FROM deal_events\|FROM deal_transitions" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py /home/zaks/zakops-backend/src/api/orchestration/main.py | grep -v 'zakops\.' 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/ST-04.txt
```

**PASS if:** All table references in these files use `zakops.` schema prefix. Zero unqualified matches.

### ST-5: Migration Rollback Scripts Are Valid SQL

```bash
for f in /home/zaks/zakops-backend/db/migrations/029*rollback*.sql /home/zaks/zakops-backend/db/migrations/030*rollback*.sql; do
  echo "=== $(basename $f) ==="
  head -10 "$f" 2>/dev/null || echo "  MISSING"
done 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001a/ST-05.txt
```

**PASS if:** Both rollback scripts exist and contain valid SQL (DROP/ALTER statements)

**ST Gate:** ST-1 through ST-5 all PASS.

---

## 6. Remediation Protocol

For any FAIL:

1. Read the evidence file for the failing gate.
2. Classify as one of:
   - `MISSING_FIX` -- finding was not implemented
   - `REGRESSION` -- previously working code broken
   - `SCOPE_GAP` -- edge case not covered by source mission
   - `FALSE_POSITIVE` -- gate check is incorrect, code is fine
   - `NOT_IMPLEMENTED` -- feature entirely absent
   - `PARTIAL` -- partially implemented, needs completion
   - `VIOLATION` -- violates architectural constraint
3. Apply fix following original guardrails (schema-qualified queries, fail-closed, workflow engine enforcement).
4. Re-run the specific gate command with tee.
5. Re-run `make validate-local`.
6. Record remediation in completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Quarantine Integration Tests
Add integration tests for inject → dedup → approve → deal promotion flow.

### ENH-2: Shadow-Mode Metrics Dashboard
Dashboard widget showing shadow-mode injection counts and approval rates.

### ENH-3: Correlation ID End-to-End Tracing
Add correlation_id to deal_events and deal_transitions for full trace.

### ENH-4: MCP Server Health Endpoint
Add /health to MCP server for monitoring.

### ENH-5: Email Config Encryption
Encrypt email_config JSONB at rest with column-level encryption.

### ENH-6: Idempotency Key Expiration
Add TTL-based cleanup for idempotency_keys table.

### ENH-7: Migration CI Gate
Automated migration syntax validation in CI pipeline.

### ENH-8: Quarantine Status Audit Trail
Log status transitions (pending → approved, pending → rejected) with actor.

### ENH-9: Bulk-Delete Rate Limiting
Rate-limit the bulk-delete endpoint to prevent abuse.

### ENH-10: OAuth State Redis Migration
Move OAuthStateStore from in-memory to Redis per ADR-004 migration path.

---

## 8. Scorecard Template

```text
QA-MASTER-PROGRAM-VERIFY-001A -- Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):      [ PASS / FAIL ]
  PF-2 (backend health):      [ PASS / FAIL / SKIP ]
  PF-3 (checkpoint status):   [ PASS / FAIL ]
  PF-4 (evidence directory):  [ PASS / FAIL ]
  PF-5 (tsc --noEmit):        [ PASS / FAIL ]

Verification Gates:
  VF-01 (F-1 MCP endpoint):       __ / 2 PASS
  VF-02 (F-3 Quarantine dedup):   __ / 3 PASS
  VF-03 (F-4 Agent DB config):    __ / 2 PASS
  VF-04 (F-5 Legacy decommission):__ / 3 PASS
  VF-05 (F-6 FSM/Outbox):         __ / 2 PASS
  VF-06 (F-9 Idempotency):        __ / 3 PASS
  VF-07 (F-8 Correlation ID):     __ / 2 PASS
  VF-08 (F-10/11/12/13 Pipeline): __ / 4 PASS
  VF-09 (F-7 Email settings):     __ / 3 PASS
  VF-10 (F-14/15/16/17 Low-sev):  __ / 4 PASS
  VF-11 (Shadow-mode infra):      __ / 4 PASS
  VF-12 (Migration integrity):    __ / 3 PASS

Cross-Consistency:
  XC-1 through XC-5:              __ / 5 PASS

Stress Tests:
  ST-1 through ST-5:              __ / 5 PASS

Total: __ / 45 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **This is a QA mission** -- do not build new features or redesign existing ones.
2. **Remediate, don't redesign** -- fix the specific gap, not the whole subsystem.
3. **Evidence-based only** -- every PASS needs tee'd output in evidence directory.
4. **Backend-down accommodation** -- if backend DB is unreachable, SQL verification gates become code-only (check migration DDL instead of live schema). Mark as SKIP with note.
5. **Preserve prior fixes** -- remediation must not revert SM-2/SM-3/SM-4 work or break prior QA results.
6. **No generated file edits** -- per standing deny rules.
7. **Schema-qualified queries** -- any SQL fix must use `zakops.table_name`.
8. **Workflow engine enforcement** -- any deal creation fix must route through `transition_deal_state()` or `DealWorkflowEngine`.
9. **P3 items are not failures** -- mark as INFO/DEFERRED.
10. **Re-run dependent gates after any remediation.**

---

## 10. Stop Condition

Stop when all 45 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` and `npx tsc --noEmit` both pass, and the scorecard is complete. Do NOT proceed to building new features or executing other missions.

---

*End of Mission Prompt -- QA-MASTER-PROGRAM-VERIFY-001A*
