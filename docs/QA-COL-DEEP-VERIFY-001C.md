> **POST-CONSOLIDATION NOTE (2026-02-16):** This document references `/home/zaks/zakops-backend/` paths.
> Backend is now at `/home/zaks/zakops-agent-api/apps/backend/` (MONOREPO-CONSOLIDATION-001).
> See `POST-CONSOLIDATION-PATH-MAPPING.md` for the full path translation table.

# QA MISSION: QA-COL-DEEP-VERIFY-001C
## Deep Spec-Level Verification — TriPass Remediation + Compliance + Cognitive Services + Ambient UI
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: TriPass run TP-20260213-163446 complete, COL-V2 Actionable Items register published
## Successor: COL-V2 implementation sprint planning (Sprint 3: Compliance, Sprint 5: Ambient UI)
## Auditor: Claude Code (Opus 4.6)

---

## 1. Mission Objective

This is an **independent, deep code-level verification** of three intersecting work streams:

1. **TriPass Findings F-1 through F-17** — The forensic audit of the Intake-Quarantine-Deals pipeline produced 17 consolidated findings across three agents (Claude, Gemini, Codex). This QA verifies that remediation code exists and is correct at the source level.

2. **Spec Sections S11, S20, S21** — Compliance (legal hold, GDPR, retention), Cognitive Intelligence (stall predictor, morning briefing, anomaly detector, devil's advocate, bottleneck heatmap), and Ambient Intelligence (dashboard UI components, Deal Brain panel, smart paste, ghost knowledge). This QA verifies backend services discovered in the deep audit match spec requirements.

3. **Dashboard COL-V2 Components** — Ambient UI components (MorningBriefingCard, AnomalyBadge, CitationIndicator, SmartPaste, GhostKnowledgeToast, DealBrain panel) verified for existence, Surface 9 compliance, and API client integration.

**What this is NOT**: This is not a build or feature mission. No new code is written unless remediating a FAIL gate. Every PASS requires tee'd evidence. Every FAIL is classified, fixed, re-gated, and recorded.

### Source Artifacts

| Artifact | Path | Key Content |
|----------|------|-------------|
| COL-DESIGN-SPEC-V2 | `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` | Canonical spec (S11, S20, S21) |
| FINAL_MASTER | `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/FINAL_MASTER.md` | 17 findings, severity, evidence paths |
| Actionable Items | `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` | Corrected status register, backend deep audit |

### Evidence Directory

```
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001c
```

All evidence files are written to this directory via `| tee $EVIDENCE_DIR/<gate>.txt`.

---

## 2. Pre-Flight

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001c
mkdir -p "$EVIDENCE_DIR"
```

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee "$EVIDENCE_DIR/PF-1-validate-local.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0. If not, stop — codebase is broken before QA starts.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee "$EVIDENCE_DIR/PF-2-tsc.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0, zero errors.

### PF-3: Backend Container Alive
```bash
curl -sf http://localhost:8091/health 2>&1 | tee "$EVIDENCE_DIR/PF-3-backend-health.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0, JSON response with healthy status. If backend is down, live verification gates (VF-04, VF-11) become code-only — mark as SKIP(services-down), not FAIL.

### PF-4: Evidence Directory Ready
```bash
test -d "$EVIDENCE_DIR" && echo "EVIDENCE_DIR exists" | tee "$EVIDENCE_DIR/PF-4-dir-ready.txt"
ls -la "$EVIDENCE_DIR/" | tee -a "$EVIDENCE_DIR/PF-4-dir-ready.txt"
```
**PASS if:** Directory exists and is writable.

### PF-5: TriPass FINAL_MASTER Exists with 17 Findings
```bash
MASTER="/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/FINAL_MASTER.md"
test -f "$MASTER" && echo "FINAL_MASTER exists" | tee "$EVIDENCE_DIR/PF-5-master-exists.txt"
FCOUNT=$(grep -c "^### F-" "$MASTER" 2>/dev/null) || FCOUNT=0
echo "Finding count: $FCOUNT" | tee -a "$EVIDENCE_DIR/PF-5-master-exists.txt"
```
**PASS if:** File exists and finding count is 17.

---

## 3. Verification Families

### VF-01 — F-1 MCP Endpoint Fix (`/review` vs `/process`) — 3 checks

**Context:** MCP server at `zakops-backend/mcp_server/server.py` referenced draft endpoint `/review` instead of the live `/process` endpoint. Lines 311 and 341 must be patched.

#### VF-01.1: No `/review` endpoint references for quarantine
```bash
grep -n "/review" /home/zaks/zakops-backend/mcp_server/server.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-1.txt"
REVIEW_COUNT=$(grep -c "/review" /home/zaks/zakops-backend/mcp_server/server.py 2>/dev/null) || REVIEW_COUNT=0
echo "REVIEW_COUNT=$REVIEW_COUNT" | tee -a "$EVIDENCE_DIR/VF-01-1.txt"
```
**PASS if:** REVIEW_COUNT is 0. No occurrences of `/review` in quarantine endpoint paths.

#### VF-01.2: `/process` endpoint referenced at least twice (approve + reject paths)
```bash
grep -n "/process" /home/zaks/zakops-backend/mcp_server/server.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-2.txt"
PROCESS_COUNT=$(grep -c "/process" /home/zaks/zakops-backend/mcp_server/server.py 2>/dev/null) || PROCESS_COUNT=0
echo "PROCESS_COUNT=$PROCESS_COUNT" | tee -a "$EVIDENCE_DIR/VF-01-2.txt"
```
**PASS if:** PROCESS_COUNT >= 2 (one for approve, one for reject).

#### VF-01.3: Quarantine item processing calls use `/process` path
```bash
grep -n -A2 "quarantine.*process\|process.*quarantine" /home/zaks/zakops-backend/mcp_server/server.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-3.txt"
```
**PASS if:** Output shows quarantine processing calls with `/process` in the URL path, not `/review`.

**Gate VF-01:** All 3 checks pass. MCP server uses correct `/process` endpoint for quarantine operations.

---

### VF-02 — F-3 Quarantine Dedup (Migration 029) — 3 checks

**Context:** `quarantine_items.message_id` lacked a UNIQUE constraint. Migration 029 should add DB-level dedup.

#### VF-02.1: UNIQUE constraint on message_id column
```bash
find /home/zaks/zakops-backend/db/migrations/ -name "*029*" -o -name "*quarantine*hardening*" 2>/dev/null | head -5 | tee "$EVIDENCE_DIR/VF-02-1.txt"
for f in $(find /home/zaks/zakops-backend/db/migrations/ -name "*029*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-02-1.txt"
  grep -i -n "unique\|message_id\|constraint" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-02-1.txt"
done
```
**PASS if:** Migration file exists and contains UNIQUE constraint on `message_id` (or composite key including `message_id`).

#### VF-02.2: source_type column added
```bash
for f in $(find /home/zaks/zakops-backend/db/migrations/ -name "*029*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-02-2.txt"
  grep -i -n "source_type" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-02-2.txt"
done
```
**PASS if:** `source_type` column is added to `quarantine_items` in a migration file. If NOT FOUND, classify as NOT_IMPLEMENTED (not a regression — this is new work from the TriPass remediation plan).

#### VF-02.3: correlation_id column added
```bash
for f in $(find /home/zaks/zakops-backend/db/migrations/ -name "*029*" -o -name "*024*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-02-3.txt"
  grep -i -n "correlation_id.*quarantine\|quarantine.*correlation_id" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-02-3.txt"
done
# Also check all migrations for correlation_id on quarantine_items
grep -rn "correlation_id" /home/zaks/zakops-backend/db/migrations/ 2>&1 | grep -i "quarantine" | tee -a "$EVIDENCE_DIR/VF-02-3.txt"
```
**PASS if:** `correlation_id` column added to `quarantine_items`. If NOT FOUND, classify as NOT_IMPLEMENTED (F-8 remediation scope).

**Gate VF-02:** Check 1 is mandatory PASS. Checks 2 and 3 are PASS or NOT_IMPLEMENTED (acceptable if migration 029 scope is limited to dedup).

---

### VF-03 — F-4 Agent DB Config — 2 checks

**Context:** Agent `docker-compose.yml` sets `DATABASE_URL` to `zakops` (wrong) instead of `zakops_agent` (correct).

#### VF-03.1: Agent DATABASE_URL references zakops_agent
```bash
grep -n "DATABASE_URL" /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml 2>&1 | tee "$EVIDENCE_DIR/VF-03-1.txt"
# Check for the WRONG value (zakops without _agent suffix)
WRONG=$(grep "DATABASE_URL" /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml 2>/dev/null | grep -v "zakops_agent" | grep -c "zakops") || WRONG=0
echo "WRONG_CONFIG_COUNT=$WRONG" | tee -a "$EVIDENCE_DIR/VF-03-1.txt"
```
**PASS if:** WRONG_CONFIG_COUNT is 0. All DATABASE_URL entries reference `zakops_agent`, not bare `zakops`.

#### VF-03.2: .env.example specifies zakops_agent
```bash
grep -n "DATABASE_URL\|zakops_agent\|zakops" /home/zaks/zakops-agent-api/apps/agent-api/.env.example 2>&1 | tee "$EVIDENCE_DIR/VF-03-2.txt"
grep -c "zakops_agent" /home/zaks/zakops-agent-api/apps/agent-api/.env.example 2>&1 | tee -a "$EVIDENCE_DIR/VF-03-2.txt"
```
**PASS if:** `.env.example` contains `zakops_agent` in the DATABASE_URL.

**Gate VF-03:** Both checks pass. Agent config consistently references the correct `zakops_agent` database.

---

### VF-04 — F-6 Quarantine Approval through FSM — 3 checks

**Context:** Quarantine approval does raw INSERT bypassing `transition_deal_state()` / `DealWorkflowEngine`. The fix should route through the workflow engine to emit `deal_transitions` ledger entries and `outbox` events.

#### VF-04.1: Quarantine approval calls transition_deal_state() or DealWorkflowEngine
```bash
# Search the quarantine approval code path in main.py
grep -n -B5 -A10 "quarantine.*approv\|approv.*quarantine\|process.*approv\|status.*approved" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -80 | tee "$EVIDENCE_DIR/VF-04-1.txt"
# Check for workflow engine usage
grep -n "transition_deal_state\|DealWorkflowEngine\|workflow" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/VF-04-1.txt"
```
**PASS if:** Quarantine approval code path calls `transition_deal_state()` or instantiates `DealWorkflowEngine`. If still raw INSERT, classify as NOT_FIXED.

#### VF-04.2: deal_transitions ledger entry on promotion
```bash
grep -n "deal_transitions\|transition.*ledger" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-04-2.txt"
grep -n "deal_transitions" /home/zaks/zakops-backend/src/core/deals/workflow.py 2>&1 | tee -a "$EVIDENCE_DIR/VF-04-2.txt"
```
**PASS if:** Evidence shows `deal_transitions` INSERT in the promotion code path (either directly or via workflow engine).

#### VF-04.3: Outbox event emitted on deal creation
```bash
grep -n "outbox\|cross_db_outbox" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-04-3.txt"
grep -n "outbox" /home/zaks/zakops-backend/src/core/deals/workflow.py 2>&1 | tee -a "$EVIDENCE_DIR/VF-04-3.txt"
```
**PASS if:** Outbox event is emitted in the quarantine-to-deal promotion path.

**Gate VF-04:** All 3 checks pass. Quarantine promotion flows through the workflow engine with full ledger + outbox instrumentation.

---

### VF-05 — F-9 Idempotency Schema Qualification — 3 checks

**Context:** Idempotency middleware queries unqualified `FROM idempotency_keys` but table is `zakops.idempotency_keys`. On DB error, middleware silently bypasses.

#### VF-05.1: All table references are schema-qualified
```bash
grep -n "idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | tee "$EVIDENCE_DIR/VF-05-1.txt"
UNQUALIFIED=$(grep "idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>/dev/null | grep -cv "zakops\.idempotency_keys") || UNQUALIFIED=0
echo "UNQUALIFIED_COUNT=$UNQUALIFIED" | tee -a "$EVIDENCE_DIR/VF-05-1.txt"
```
**PASS if:** UNQUALIFIED_COUNT is 0. All references use `zakops.idempotency_keys`.

#### VF-05.2: Fail-closed semantics on DB error
```bash
grep -n -B3 -A10 "except\|error\|bypass\|skip\|pass" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | head -60 | tee "$EVIDENCE_DIR/VF-05-2.txt"
# Check for silent bypass pattern
grep -n "return\|continue\|pass" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | tee -a "$EVIDENCE_DIR/VF-05-2.txt"
```
**PASS if:** On DB error, the middleware returns an error response (fail-closed), NOT silently proceeds (fail-open). Look for: raise, HTTPException, return error response in except blocks.

#### VF-05.3: No unqualified "FROM idempotency_keys"
```bash
grep -n "FROM.*idempotency_keys\|INTO.*idempotency_keys\|UPDATE.*idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | tee "$EVIDENCE_DIR/VF-05-3.txt"
UNQUAL_SQL=$(grep -E "FROM\s+idempotency_keys|INTO\s+idempotency_keys|UPDATE\s+idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>/dev/null | grep -cv "zakops\.") || UNQUAL_SQL=0
echo "UNQUALIFIED_SQL_COUNT=$UNQUAL_SQL" | tee -a "$EVIDENCE_DIR/VF-05-3.txt"
```
**PASS if:** UNQUALIFIED_SQL_COUNT is 0. All SQL statements use `zakops.idempotency_keys`.

**Gate VF-05:** All 3 checks pass. Idempotency middleware is schema-qualified and fail-closed.

---

### VF-06 — F-11 Quarantine Status Constraint — 2 checks

**Context:** `quarantine_items.status` is plain VARCHAR(50) with no CHECK constraint. Migration should add one.

#### VF-06.1: CHECK constraint on status column in migration
```bash
grep -rn -i "check.*status\|chk_quarantine_status\|constraint.*quarantine.*status" /home/zaks/zakops-backend/db/migrations/ 2>&1 | tee "$EVIDENCE_DIR/VF-06-1.txt"
# Also check init tables for inline constraint
grep -n -A2 "status" /home/zaks/zakops-backend/db/init/001_base_tables.sql 2>&1 | grep -i "quarantine\|check" | tee -a "$EVIDENCE_DIR/VF-06-1.txt"
```
**PASS if:** A CHECK constraint exists on `quarantine_items.status` (in a migration or init file).

#### VF-06.2: Allowed values include pending, approved, rejected, hidden
```bash
grep -rn -i "pending.*approved.*rejected.*hidden\|'pending'\|'approved'\|'rejected'\|'hidden'" /home/zaks/zakops-backend/db/migrations/ 2>&1 | grep -i "quarantine\|status" | tee "$EVIDENCE_DIR/VF-06-2.txt"
```
**PASS if:** The CHECK constraint allows exactly: `pending`, `approved`, `rejected`, `hidden`.

**Gate VF-06:** Both checks pass. DB-level defense-in-depth for quarantine status values.

---

### VF-07 — F-13 Retention Cleanup Column Fix — 2 checks

**Context:** `cleanup.py:299` references `processed_by` and `processing_action` columns that do not exist on `quarantine_items`.

#### VF-07.1: No reference to processed_by column on quarantine_items
```bash
grep -n "processed_by\|processing_action" /home/zaks/zakops-backend/src/core/retention/cleanup.py 2>&1 | tee "$EVIDENCE_DIR/VF-07-1.txt"
BAD_COL=$(grep -c "processed_by\|processing_action" /home/zaks/zakops-backend/src/core/retention/cleanup.py 2>/dev/null) || BAD_COL=0
echo "BAD_COLUMN_REF_COUNT=$BAD_COL" | tee -a "$EVIDENCE_DIR/VF-07-1.txt"
```
**PASS if:** BAD_COLUMN_REF_COUNT is 0. No references to nonexistent columns.

#### VF-07.2: Uses raw_content JSON pattern or existing columns only
```bash
grep -n -B3 -A3 "quarantine\|raw_content" /home/zaks/zakops-backend/src/core/retention/cleanup.py 2>&1 | head -40 | tee "$EVIDENCE_DIR/VF-07-2.txt"
```
**PASS if:** Quarantine cleanup uses `raw_content` JSON field (matching the approval flow pattern at `main.py:1695`) or only references columns that exist in the schema (`id`, `deal_name`, `source_email`, `message_id`, `raw_content`, `status`, `priority`, `created_at`, `updated_at`).

**Gate VF-07:** Both checks pass. Retention cleanup references only columns that exist in the quarantine schema.

---

### VF-08 — Migration 029 Legal Hold (S11, S7.5) — 4 checks

**Context:** Spec S11 requires legal hold infrastructure. COL-V2 Actionable Items C1 lists migration 029 for `legal_hold_locks` and `legal_hold_log` tables.

#### VF-08.1: legal_hold_locks table definition
```bash
find /home/zaks/zakops-backend/db/ -name "*029*" -o -name "*legal*hold*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-08-1.txt"
for f in $(find /home/zaks/zakops-backend/db/ -name "*029*" -o -name "*legal*hold*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-08-1.txt"
  grep -i -n "legal_hold_locks\|hold_type\|hold_reason\|set_by\|released_at" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-08-1.txt"
done
```
**PASS if:** `legal_hold_locks` table exists with `hold_type`, `hold_reason`, `set_by`, `released_at` columns. If NOT FOUND, classify as NOT_IMPLEMENTED (C1 from Actionable Items — Sprint 3 scope).

#### VF-08.2: legal_hold_log table for immutable audit trail
```bash
for f in $(find /home/zaks/zakops-backend/db/ -name "*029*" -o -name "*legal*hold*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-08-2.txt"
  grep -i -n "legal_hold_log" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-08-2.txt"
done
```
**PASS if:** `legal_hold_log` table exists in a migration file. If NOT FOUND, classify as NOT_IMPLEMENTED.

#### VF-08.3: Index on legal_hold_locks for active holds
```bash
for f in $(find /home/zaks/zakops-backend/db/ -name "*029*" -o -name "*legal*hold*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-08-3.txt"
  grep -i -n "index\|WHERE.*released_at.*NULL\|idx_.*hold" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-08-3.txt"
done
```
**PASS if:** Partial index on `legal_hold_locks` with `WHERE released_at IS NULL`. If NOT FOUND, classify as NOT_IMPLEMENTED or PARTIAL.

#### VF-08.4: Schema migration version recorded
```bash
for f in $(find /home/zaks/zakops-backend/db/ -name "*029*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-08-4.txt"
  head -10 "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-08-4.txt"
  grep -i -n "version\|migration\|-- " "$f" 2>&1 | head -5 | tee -a "$EVIDENCE_DIR/VF-08-4.txt"
done
```
**PASS if:** Migration 029 has a version marker or migration header comment.

**Gate VF-08:** If migration 029 exists with legal hold tables, all 4 checks. If migration does not exist, classify entire family as NOT_IMPLEMENTED (Sprint 3 scope).

---

### VF-09 — GDPR Purge Service (S11.5) — 5 checks

**Context:** Spec S11 requires GDPR right-to-erasure automation. Actionable Item C27 tracks this.

#### VF-09.1: gdpr_purge() function exists
```bash
find /home/zaks/zakops-backend/src/ -name "*gdpr*" -o -name "*purge*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-09-1.txt"
grep -rn "def gdpr_purge\|class GdprPurge\|class GDPRPurge" /home/zaks/zakops-backend/src/ 2>&1 | tee -a "$EVIDENCE_DIR/VF-09-1.txt"
```
**PASS if:** `gdpr_purge()` function or `GdprPurge*` class exists. If NOT FOUND, classify as NOT_IMPLEMENTED (C27 — Sprint 3 scope).

#### VF-09.2: LEFT JOIN on legal_hold_locks to detect active holds
```bash
grep -rn "legal_hold_locks\|legal_hold\|LEFT JOIN.*hold" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | tee "$EVIDENCE_DIR/VF-09-2.txt"
```
**PASS if:** GDPR purge logic joins on `legal_hold_locks` to detect active holds. If NOT FOUND, classify as NOT_IMPLEMENTED.

#### VF-09.3: Threads with legal holds are SKIPPED
```bash
grep -rn -A5 "legal_hold\|hold.*skip\|skip.*hold" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | head -30 | tee "$EVIDENCE_DIR/VF-09-3.txt"
```
**PASS if:** Code path demonstrates skip logic for threads with active legal holds.

#### VF-09.4: Skip action logged to legal_hold_log
```bash
grep -rn "legal_hold_log\|log.*hold.*skip\|hold.*log" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | tee "$EVIDENCE_DIR/VF-09-4.txt"
```
**PASS if:** Skip actions are logged to `legal_hold_log` table.

#### VF-09.5: GdprPurgeReport with deleted_count, skipped_count, skipped_thread_ids
```bash
grep -rn "GdprPurgeReport\|PurgeReport\|deleted_count\|skipped_count\|skipped_thread_ids" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | tee "$EVIDENCE_DIR/VF-09-5.txt"
```
**PASS if:** Report dataclass/model exists with the three required fields.

**Gate VF-09:** If GDPR service exists, all 5 checks. If NOT FOUND, classify entire family as NOT_IMPLEMENTED (C27 — Sprint 3 scope). This is a SCOPE_GAP, not a regression.

---

### VF-10 — Retention Policy Engine (S11.4) — 4 checks

**Context:** Spec S11.4 defines 4 retention tiers. Actionable Item C28 tracks this.

#### VF-10.1: 4 retention tiers defined
```bash
find /home/zaks/zakops-backend/src/ -name "*retention*policy*" -o -name "*retention*" 2>/dev/null | grep -v __pycache__ | tee "$EVIDENCE_DIR/VF-10-1.txt"
grep -rn "default.*30\|deal_scoped.*90\|legal_hold.*365\|compliance.*forever\|retention.*tier\|RETENTION_TIER" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | head -20 | tee -a "$EVIDENCE_DIR/VF-10-1.txt"
```
**PASS if:** 4 retention tiers are defined: default(30d), deal_scoped(90d), legal_hold(365d), compliance(forever). If NOT FOUND, classify as NOT_IMPLEMENTED (C28 — Sprint 3).

#### VF-10.2: evaluate() method with tier selection logic
```bash
grep -rn "def evaluate\|def get_tier\|def select_tier" /home/zaks/zakops-backend/src/ 2>&1 | grep -i "retention" | tee "$EVIDENCE_DIR/VF-10-2.txt"
```
**PASS if:** Method exists that selects the appropriate retention tier.

#### VF-10.3: Tier hierarchy (compliance > legal_hold > deal_scoped > default)
```bash
grep -rn -A15 "def evaluate\|def get_tier\|def select_tier" /home/zaks/zakops-backend/src/ 2>&1 | grep -i "retention\|tier\|compliance\|legal\|deal_scoped\|default" | head -20 | tee "$EVIDENCE_DIR/VF-10-3.txt"
```
**PASS if:** Tier selection logic respects priority ordering.

#### VF-10.4: get_expired_threads() filters protected threads
```bash
grep -rn "get_expired\|expired_threads\|filter.*protected\|exclude.*hold" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | tee "$EVIDENCE_DIR/VF-10-4.txt"
```
**PASS if:** Method exists that excludes protected threads from expiry.

**Gate VF-10:** If retention policy engine exists, all 4 checks. If NOT FOUND, classify as NOT_IMPLEMENTED (C28).

---

### VF-11 — Compliance Purge Endpoint — 3 checks

**Context:** Spec S7.5 requires `POST /admin/compliance/purge`. Actionable Item C29 tracks this.

#### VF-11.1: POST /admin/compliance/purge route exists
```bash
grep -rn "compliance/purge\|compliance.*purge\|admin.*purge" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | tee "$EVIDENCE_DIR/VF-11-1.txt"
grep -rn "compliance/purge\|compliance.*purge" /home/zaks/zakops-agent-api/apps/agent-api/ 2>&1 | grep -v ".pyc\|node_modules" | tee -a "$EVIDENCE_DIR/VF-11-1.txt"
```
**PASS if:** Route handler exists for `POST /admin/compliance/purge`. If NOT FOUND, classify as NOT_IMPLEMENTED (C29 — Sprint 3).

#### VF-11.2: Admin-only guard
```bash
grep -rn -B5 "compliance.*purge\|purge.*compliance" /home/zaks/zakops-backend/src/ 2>&1 | grep -i "admin\|require_admin\|permission\|auth\|role" | tee "$EVIDENCE_DIR/VF-11-2.txt"
```
**PASS if:** Admin authorization check exists on the purge endpoint.

#### VF-11.3: Calls gdpr_purge() function
```bash
grep -rn -A10 "compliance.*purge\|purge.*compliance" /home/zaks/zakops-backend/src/ 2>&1 | grep -i "gdpr_purge\|purge_service\|purge(" | tee "$EVIDENCE_DIR/VF-11-3.txt"
```
**PASS if:** Endpoint delegates to `gdpr_purge()` or equivalent purge service.

**Gate VF-11:** If endpoint exists, all 3 checks. If NOT FOUND, classify as NOT_IMPLEMENTED (C29).

---

### VF-12 — Cognitive Services Backend (S20) — 5 checks

**Context:** COL-V2 Actionable Items deep audit confirmed 8 cognitive services in `zakops-backend/src/core/agent/`. Verify key methods match spec requirements.

#### VF-12.1: StallPredictor has predict() with stall_probability
```bash
FILE="/home/zaks/zakops-backend/src/core/agent/stall_predictor.py"
test -f "$FILE" && echo "FILE EXISTS" | tee "$EVIDENCE_DIR/VF-12-1.txt"
grep -n "def predict\|stall_probability\|predict_batch" "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-1.txt"
wc -l "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-1.txt"
```
**PASS if:** File exists, `predict()` method present, `stall_probability` in output. Per Actionable Items: 257 lines expected.

#### VF-12.2: MorningBriefingGenerator has generate() with hours_lookback
```bash
FILE="/home/zaks/zakops-backend/src/core/agent/morning_briefing.py"
test -f "$FILE" && echo "FILE EXISTS" | tee "$EVIDENCE_DIR/VF-12-2.txt"
grep -n "def generate\|class MorningBriefingGenerator\|hours_lookback\|last_session\|user_id" "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-2.txt"
wc -l "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-2.txt"
```
**PASS if:** File exists, `MorningBriefingGenerator` class present, `generate()` method with session/user parameters. Per Actionable Items: 202 lines expected.

#### VF-12.3: DealAnomalyDetector has check_anomalies() with 5 anomaly types
```bash
FILE="/home/zaks/zakops-backend/src/core/agent/anomaly_detector.py"
test -f "$FILE" && echo "FILE EXISTS" | tee "$EVIDENCE_DIR/VF-12-3.txt"
grep -n "def check_anomalies\|class DealAnomalyDetector\|unusual_silence\|activity_burst\|Anomaly" "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-3.txt"
ANOMALY_TYPES=$(grep -c "type.*=\|anomaly_type\|Anomaly(" "$FILE" 2>/dev/null) || ANOMALY_TYPES=0
echo "ANOMALY_TYPE_COUNT=$ANOMALY_TYPES" | tee -a "$EVIDENCE_DIR/VF-12-3.txt"
wc -l "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-3.txt"
```
**PASS if:** File exists, `DealAnomalyDetector` with `check_anomalies()`. Spec S21.3 shows at least `unusual_silence` and `activity_burst`. Per Actionable Items: 209 lines expected.

#### VF-12.4: DevilsAdvocateService has challenge() method
```bash
FILE="/home/zaks/zakops-backend/src/core/agent/devils_advocate.py"
test -f "$FILE" && echo "FILE EXISTS" | tee "$EVIDENCE_DIR/VF-12-4.txt"
grep -n "def challenge\|class DevilsAdvocateService\|def generate_challenge\|def critique" "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-4.txt"
wc -l "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-4.txt"
```
**PASS if:** File exists, `DevilsAdvocateService` class with `challenge()` or equivalent method. Per Actionable Items: 191 lines expected.

#### VF-12.5: BottleneckHeatmap has compute() method
```bash
FILE="/home/zaks/zakops-backend/src/core/agent/bottleneck_heatmap.py"
test -f "$FILE" && echo "FILE EXISTS" | tee "$EVIDENCE_DIR/VF-12-5.txt"
grep -n "def compute\|class BottleneckHeatmap" "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-5.txt"
wc -l "$FILE" 2>&1 | tee -a "$EVIDENCE_DIR/VF-12-5.txt"
```
**PASS if:** File exists, `BottleneckHeatmap` class with `compute()`. Per Actionable Items: 181 lines expected.

**Gate VF-12:** All 5 checks pass. Backend cognitive service infrastructure exists and matches spec methods.

---

### VF-13 — Dashboard Ambient UI Components (S21) — 5 checks

**Context:** COL-V2 spec defines ambient UI components. Actionable Items C14-C23 track dashboard UI work. Many components are NOT_IMPLEMENTED per the actionable items register ("Items Confirmed NOT Found Anywhere").

#### VF-13.1: MorningBriefingCard.tsx exists with 'use client'
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*MorningBriefing*" -o -name "*morning*briefing*" -o -name "*morning-briefing*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-13-1.txt"
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*morning*briefing*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-13-1.txt"
  head -5 "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-13-1.txt"
done
```
**PASS if:** Component file exists with `'use client'` directive. If NOT FOUND, classify as NOT_IMPLEMENTED (Sprint 5 scope per Actionable Items).

#### VF-13.2: AnomalyBadge.tsx exists with severity levels
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*AnomalyBadge*" -o -name "*anomaly*badge*" -o -name "*anomaly-badge*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-13-2.txt"
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*anomaly*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-13-2.txt"
  grep -n "high\|medium\|low\|severity" "$f" 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/VF-13-2.txt"
done
```
**PASS if:** Component exists with high/medium/low severity levels. If NOT FOUND, classify as NOT_IMPLEMENTED.

#### VF-13.3: CitationIndicator.tsx has Strong/Weak/Orphan threshold bands
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*CitationIndicator*" -o -name "*citation*indicator*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-13-3.txt"
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*citation*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-13-3.txt"
  grep -n "strong\|weak\|orphan\|threshold\|band\|confidence" "$f" 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/VF-13-3.txt"
done
```
**PASS if:** Component exists with Strong/Weak/Orphan classification. If NOT FOUND, classify as NOT_IMPLEMENTED (C16).

#### VF-13.4: SmartPaste.tsx has >= 4 regex patterns
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*SmartPaste*" -o -name "*smart*paste*" -o -name "*smart-paste*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-13-4.txt"
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*smart*paste*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-13-4.txt"
  REGEX_COUNT=$(grep -c "regex\|RegExp\|\/.*\/" "$f" 2>/dev/null) || REGEX_COUNT=0
  echo "REGEX_PATTERN_COUNT=$REGEX_COUNT" | tee -a "$EVIDENCE_DIR/VF-13-4.txt"
done
```
**PASS if:** Component exists with >= 4 regex patterns for entity extraction. If NOT FOUND, classify as NOT_IMPLEMENTED (C21).

#### VF-13.5: GhostKnowledgeToast.tsx has confirm and dismiss callbacks
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*GhostKnowledge*" -o -name "*ghost*knowledge*" -o -name "*ghost-knowledge*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-13-5.txt"
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*ghost*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-13-5.txt"
  grep -n "confirm\|dismiss\|onConfirm\|onDismiss" "$f" 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/VF-13-5.txt"
done
```
**PASS if:** Component exists with confirm and dismiss callback props. If NOT FOUND, classify as NOT_IMPLEMENTED (C14).

**Gate VF-13:** Components that exist pass individual checks. Components classified as NOT_IMPLEMENTED are Sprint 5 scope — not regressions.

---

### VF-14 — Dashboard API Client Integration — 4 checks

**Context:** Dashboard `api.ts` should have API client functions for the cognitive/brain endpoints.

#### VF-14.1: getDealBrain() function returns DealBrain interface
```bash
grep -n "getDealBrain\|dealBrain\|deal.*brain\|brain" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | head -20 | tee "$EVIDENCE_DIR/VF-14-1.txt"
grep -n "DealBrain" /home/zaks/zakops-agent-api/apps/dashboard/types/api.ts 2>&1 | tee -a "$EVIDENCE_DIR/VF-14-1.txt"
```
**PASS if:** `getDealBrain()` function exists and returns `DealBrain` interface. If NOT FOUND, classify as NOT_IMPLEMENTED (dashboard wiring for brain endpoints).

#### VF-14.2: getMorningBriefing() function
```bash
grep -n "getMorningBriefing\|morningBriefing\|morning.*briefing" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | tee "$EVIDENCE_DIR/VF-14-2.txt"
```
**PASS if:** Function exists. If NOT FOUND, classify as NOT_IMPLEMENTED.

#### VF-14.3: getDealAnomalies() function
```bash
grep -n "getDealAnomalies\|dealAnomalies\|anomal" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | tee "$EVIDENCE_DIR/VF-14-3.txt"
```
**PASS if:** Function exists. If NOT FOUND, classify as NOT_IMPLEMENTED.

#### VF-14.4: getSentimentTrend() function
```bash
grep -n "getSentimentTrend\|sentimentTrend\|sentiment" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | tee "$EVIDENCE_DIR/VF-14-4.txt"
```
**PASS if:** Function exists. If NOT FOUND, classify as NOT_IMPLEMENTED.

**Gate VF-14:** Functions that exist pass. Missing functions are classified as NOT_IMPLEMENTED (Sprint 5 dashboard wiring).

---

### VF-15 — DealBrain.tsx UI Panel (S4.7) — 5 checks

**Context:** Dashboard should have a DealBrain panel showing facts, ghost knowledge, momentum, and using spec-compliant patterns.

#### VF-15.1: Facts list with confidence display
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*DealBrain*" -o -name "*deal*brain*" -o -name "*deal-brain*" 2>/dev/null | tee "$EVIDENCE_DIR/VF-15-1.txt"
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*deal*brain*" 2>/dev/null); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/VF-15-1.txt"
  grep -n "facts\|confidence\|fact.*list\|fact.*item" "$f" 2>&1 | head -15 | tee -a "$EVIDENCE_DIR/VF-15-1.txt"
done
```
**PASS if:** DealBrain component exists with facts list and confidence display.

#### VF-15.2: Ghost knowledge section with Confirm/Dismiss actions
```bash
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*deal*brain*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-15-2.txt"
  grep -n "ghost\|confirm\|dismiss\|GhostKnowledge\|onConfirm\|onDismiss" "$f" 2>&1 | head -15 | tee -a "$EVIDENCE_DIR/VF-15-2.txt"
done
```
**PASS if:** Ghost knowledge section with user action callbacks.

#### VF-15.3: Momentum score display
```bash
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*deal*brain*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-15-3.txt"
  grep -n "momentum\|score\|MomentumScore" "$f" 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/VF-15-3.txt"
done
```
**PASS if:** Momentum score is displayed in the DealBrain panel.

#### VF-15.4: Uses Promise.allSettled (not Promise.all)
```bash
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*deal*brain*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-15-4.txt"
  grep -n "Promise.allSettled\|Promise.all" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-15-4.txt"
  PROMISE_ALL=$(grep -c "Promise\.all[^S]" "$f" 2>/dev/null) || PROMISE_ALL=0
  echo "BANNED_PROMISE_ALL_COUNT=$PROMISE_ALL" | tee -a "$EVIDENCE_DIR/VF-15-4.txt"
done
```
**PASS if:** Uses `Promise.allSettled`. BANNED_PROMISE_ALL_COUNT is 0.

#### VF-15.5: No console.error in component (Surface 9 compliance)
```bash
for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -iname "*deal*brain*" 2>/dev/null); do
  echo "=== $f ===" | tee "$EVIDENCE_DIR/VF-15-5.txt"
  grep -n "console.error" "$f" 2>&1 | tee -a "$EVIDENCE_DIR/VF-15-5.txt"
  CE_COUNT=$(grep -c "console\.error" "$f" 2>/dev/null) || CE_COUNT=0
  echo "CONSOLE_ERROR_COUNT=$CE_COUNT" | tee -a "$EVIDENCE_DIR/VF-15-5.txt"
done
```
**PASS if:** CONSOLE_ERROR_COUNT is 0. Backend-down degradation should use `console.warn`, not `console.error` (Surface 9 rule).

**Gate VF-15:** If DealBrain component exists, all 5 checks. If NOT FOUND, classify as NOT_IMPLEMENTED (Sprint 5 dashboard scope).

---

## 4. Cross-Consistency Checks

### XC-1: F-1 Fix (MCP `/process`) Consistent with Backend Endpoint
```bash
echo "=== MCP server ===" | tee "$EVIDENCE_DIR/XC-1.txt"
grep -n "/process\|/review" /home/zaks/zakops-backend/mcp_server/server.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-1.txt"
echo "=== Backend main.py ===" | tee -a "$EVIDENCE_DIR/XC-1.txt"
grep -n "quarantine.*process\|/process" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/XC-1.txt"
```
**PASS if:** MCP server endpoint path matches the backend route definition exactly.

### XC-2: GDPR Purge Skips Legal Holds from Migration 029 Tables
```bash
echo "=== Migration 029 tables ===" | tee "$EVIDENCE_DIR/XC-2.txt"
grep -rn "legal_hold_locks\|legal_hold_log" /home/zaks/zakops-backend/db/ 2>&1 | head -10 | tee -a "$EVIDENCE_DIR/XC-2.txt"
echo "=== GDPR purge references ===" | tee -a "$EVIDENCE_DIR/XC-2.txt"
grep -rn "legal_hold_locks\|legal_hold_log" /home/zaks/zakops-backend/src/ 2>&1 | grep -v ".pyc" | head -10 | tee -a "$EVIDENCE_DIR/XC-2.txt"
```
**PASS if:** GDPR purge service references the same `legal_hold_locks` table defined in migration 029. If both are NOT_IMPLEMENTED, mark as SKIP(consistent-gap).

### XC-3: Retention Policy Tiers Match Spec S11.4
```bash
echo "=== Spec S11.4 tiers ===" | tee "$EVIDENCE_DIR/XC-3.txt"
echo "Expected: default(30d), deal_scoped(90d), legal_hold(365d), compliance(forever)" | tee -a "$EVIDENCE_DIR/XC-3.txt"
echo "=== Code tiers ===" | tee -a "$EVIDENCE_DIR/XC-3.txt"
grep -rn "30\|90\|365\|forever\|indefinite\|retention.*tier\|RETENTION" /home/zaks/zakops-backend/src/ 2>&1 | grep -i "retention\|tier\|policy" | head -20 | tee -a "$EVIDENCE_DIR/XC-3.txt"
```
**PASS if:** Code retention tiers match spec table exactly. If retention engine is NOT_IMPLEMENTED, mark as SKIP(not-yet-built).

### XC-4: Dashboard API Functions Match Backend Brain Router Endpoints
```bash
echo "=== Backend brain router endpoints ===" | tee "$EVIDENCE_DIR/XC-4.txt"
grep -n "@.*get\|@.*post\|@.*put\|@.*delete\|@.*patch" /home/zaks/zakops-backend/src/api/orchestration/routers/brain.py 2>&1 | head -20 | tee -a "$EVIDENCE_DIR/XC-4.txt"
echo "=== Dashboard API client functions ===" | tee -a "$EVIDENCE_DIR/XC-4.txt"
grep -n "brain\|Brain\|anomal\|briefing\|momentum\|sentiment" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | head -20 | tee -a "$EVIDENCE_DIR/XC-4.txt"
```
**PASS if:** For every backend brain endpoint, there is a corresponding dashboard API client function. Partial coverage is classified as PARTIAL(dashboard-wiring-pending).

### XC-5: All 17 TriPass Findings Have Corresponding Fixes (Coverage Check)
```bash
echo "=== TriPass Finding Coverage ===" | tee "$EVIDENCE_DIR/XC-5.txt"
MASTER="/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/FINAL_MASTER.md"
for i in $(seq 1 17); do
  FINDING=$(grep "^### F-$i:" "$MASTER" | head -1)
  echo "F-$i: $FINDING" | tee -a "$EVIDENCE_DIR/XC-5.txt"
done
echo "---" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "Coverage check: verify each finding has a VF gate or is tracked in Actionable Items" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "VF-01=F-1, VF-02=F-3, VF-03=F-4, VF-04=F-6, VF-05=F-9, VF-06=F-11, VF-07=F-13" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "F-2(email ingestion)=out-of-scope-new-feature, F-5(filesystem)=sweep, F-7(email-settings)=UI-wiring" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "F-8(correlation-id)=VF-02.3, F-10(bulk-delete)=UI, F-12(DDL-default)=ST-1" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "F-14(transition-matrix)=ST-2, F-15(docstring)=low-priority, F-16(attachment)=promotion-flow" | tee -a "$EVIDENCE_DIR/XC-5.txt"
echo "F-17(oauth-state)=low-priority-latent" | tee -a "$EVIDENCE_DIR/XC-5.txt"
```
**PASS if:** Every F-1 through F-17 is either covered by a VF gate, tracked in Actionable Items, or explicitly classified as out-of-scope with justification. Zero unaccounted findings.

---

## 5. Stress Tests

### ST-1: F-12 DDL Default Stage — `'lead'` Should Be Fixed to `'inbound'`
```bash
grep -n "DEFAULT.*lead\|DEFAULT.*inbound\|DEFAULT.*stage" /home/zaks/zakops-backend/db/init/001_base_tables.sql 2>&1 | tee "$EVIDENCE_DIR/ST-1.txt"
LEAD_DEFAULT=$(grep -c "DEFAULT.*'lead'" /home/zaks/zakops-backend/db/init/001_base_tables.sql 2>/dev/null) || LEAD_DEFAULT=0
echo "LEAD_DEFAULT_COUNT=$LEAD_DEFAULT" | tee -a "$EVIDENCE_DIR/ST-1.txt"
```
**PASS if:** LEAD_DEFAULT_COUNT is 0. Default stage should be `'inbound'` (or another valid canonical stage from `DealStage` enum), NOT `'lead'`.

### ST-2: F-14 Transition Matrix Duplication — Agent vs Backend
```bash
echo "=== Agent VALID_TRANSITIONS ===" | tee "$EVIDENCE_DIR/ST-2.txt"
grep -n -A20 "VALID_TRANSITIONS" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py 2>&1 | head -25 | tee -a "$EVIDENCE_DIR/ST-2.txt"
echo "=== Backend STAGE_TRANSITIONS ===" | tee -a "$EVIDENCE_DIR/ST-2.txt"
grep -n -A20 "STAGE_TRANSITIONS\|VALID_TRANSITIONS" /home/zaks/zakops-backend/src/core/deals/workflow.py 2>&1 | head -25 | tee -a "$EVIDENCE_DIR/ST-2.txt"
```
**PASS if:** Agent `VALID_TRANSITIONS` exactly matches backend `STAGE_TRANSITIONS`, OR agent-side copy has been removed (delegating to backend API). Drift between the two is a FAIL.

### ST-3: Dashboard COL-V2 Components Have 'use client' Directive (Surface 9)
```bash
echo "=== Surface 9 'use client' check ===" | tee "$EVIDENCE_DIR/ST-3.txt"
for pattern in "*DealBrain*" "*MorningBriefing*" "*AnomalyBadge*" "*CitationIndicator*" "*SmartPaste*" "*GhostKnowledge*"; do
  for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -name "$pattern" 2>/dev/null); do
    FIRST_LINE=$(head -1 "$f" 2>/dev/null)
    echo "$f: $FIRST_LINE" | tee -a "$EVIDENCE_DIR/ST-3.txt"
  done
done
```
**PASS if:** Every COL-V2 dashboard component that exists has `'use client'` as its first meaningful line. Components that do not exist are SKIP.

### ST-4: No Promise.all in COL-V2 Dashboard Components
```bash
echo "=== Promise.all ban check ===" | tee "$EVIDENCE_DIR/ST-4.txt"
VIOLATIONS=0
for pattern in "*DealBrain*" "*MorningBriefing*" "*AnomalyBadge*" "*CitationIndicator*" "*SmartPaste*" "*GhostKnowledge*" "*deal-brain*" "*morning-briefing*"; do
  for f in $(find /home/zaks/zakops-agent-api/apps/dashboard/src -name "$pattern" 2>/dev/null); do
    PA_COUNT=$(grep -c "Promise\.all[^S]" "$f" 2>/dev/null) || PA_COUNT=0
    if [ "$PA_COUNT" -gt 0 ]; then
      echo "VIOLATION: $f has Promise.all ($PA_COUNT occurrences)" | tee -a "$EVIDENCE_DIR/ST-4.txt"
      VIOLATIONS=$((VIOLATIONS + PA_COUNT))
    fi
  done
done
echo "TOTAL_VIOLATIONS=$VIOLATIONS" | tee -a "$EVIDENCE_DIR/ST-4.txt"
```
**PASS if:** TOTAL_VIOLATIONS is 0. All data fetching in COL-V2 components uses `Promise.allSettled`.

### ST-5: RetentionPolicy Functional Test — evaluate() Returns Correct Tier
```bash
echo "=== Retention tier logic check ===" | tee "$EVIDENCE_DIR/ST-5.txt"
# Check if retention policy has evaluate logic with correct hierarchy
for f in $(find /home/zaks/zakops-backend/src/ -iname "*retention*policy*" -o -iname "*retention*" 2>/dev/null | grep -v __pycache__ | grep -v ".pyc"); do
  echo "=== $f ===" | tee -a "$EVIDENCE_DIR/ST-5.txt"
  grep -n -A5 "def evaluate\|compliance\|legal_hold\|deal_scoped\|default" "$f" 2>&1 | head -30 | tee -a "$EVIDENCE_DIR/ST-5.txt"
done
# If no retention policy found, check if cleanup.py has any tier logic
grep -n "tier\|retention\|30.*day\|90.*day\|365\|forever" /home/zaks/zakops-backend/src/core/retention/cleanup.py 2>&1 | head -20 | tee -a "$EVIDENCE_DIR/ST-5.txt"
```
**PASS if:** Retention policy evaluate() demonstrates correct tier hierarchy: compliance > legal_hold > deal_scoped > default. If NOT_IMPLEMENTED, classify as SCOPE_GAP.

---

## 6. Remediation Protocol

When a gate returns FAIL:

1. **Read the evidence file** — understand the exact failure
2. **Classify the failure:**
   - `MISSING_FIX` — TriPass finding was not remediated
   - `REGRESSION` — A prior fix was reverted or broken
   - `SCOPE_GAP` — Feature not yet implemented (expected, tracked in Actionable Items)
   - `NOT_IMPLEMENTED` — Spec feature not yet built (Sprint 3/5 scope)
   - `FALSE_POSITIVE` — Gate logic is wrong, code is correct
   - `PARTIAL` — Feature partially implemented
   - `VIOLATION` — Active pattern violation (Surface 9, Promise.all ban, etc.)
3. **Apply minimal fix** following existing patterns and guardrails
4. **Re-run the specific gate** — capture new evidence
5. **Re-run `make validate-local`** — ensure no regression
6. **Record in completion report** with before/after evidence paths

### Classification Decision Tree

- **IF** the finding is F-1 through F-17 AND the fix is absent: `MISSING_FIX`
- **ELSE IF** the finding is from S11/S20/S21 AND the service/component does not exist: `NOT_IMPLEMENTED`
- **ELSE IF** an existing fix was broken by subsequent work: `REGRESSION`
- **ELSE IF** the gate command is wrong but the code is correct: `FALSE_POSITIVE`
- **ELSE**: use best-fit classification

---

## 7. Enhancement Opportunities

### ENH-1: Dry-Run Flag for GDPR Purge
Add `--dry-run` parameter to `gdpr_purge()` that reports what WOULD be deleted without executing. Essential for compliance officer review before production purge.

### ENH-2: Rate Limiting on Compliance Purge Endpoint
Add per-user rate limiting on `POST /admin/compliance/purge` to prevent accidental bulk deletion. Suggest 1 purge per hour per admin.

### ENH-3: Audit Dashboard for Legal Hold Activity
Create a dedicated admin page showing active legal holds, hold duration, affected thread count, and release history. Currently this data is only queryable via SQL.

### ENH-4: MCP Contract Test in CI
Add a CI job that starts an ephemeral backend, runs every MCP tool call, and validates response schema + 2xx status. Prevents F-1-class drift from recurring.

### ENH-5: Quarantine Dedup Content-Hash Layer
Beyond `message_id` uniqueness (F-3 fix), add content-hash dedup for thread-variant detection. Forwarded emails or thread replies with new `message_id` values can still be duplicates at the content level.

### ENH-6: Agent Startup Database Assertion
Add startup gate in agent API that rejects `DATABASE_URL` where dbname != `zakops_agent`. Prevents F-4-class config drift at the application level rather than relying on CI.

### ENH-7: Retention Tier Dashboard Widget
Surface retention tier distribution in the admin dashboard: how many threads are in each tier, when the next cleanup runs, and how many threads are protected by legal holds.

### ENH-8: Cognitive Service Health Endpoint
Add `/health/cognitive` endpoint that reports availability of all 8 cognitive services (stall predictor, morning briefing, anomaly detector, etc.). Useful for dashboard to show degraded state.

### ENH-9: Ambient Component Storybook Integration
Create Storybook stories for all COL-V2 ambient components (MorningBriefingCard, AnomalyBadge, etc.) with mock data. Enables frontend review without backend dependency.

### ENH-10: TriPass Finding Regression Suite
Convert all 17 TriPass findings into a permanent regression test suite. Each finding becomes a `test_f{N}_*` test function that runs the same verification commands used in this QA mission.

---

## 8. Scorecard Template

```
QA-COL-DEEP-VERIFY-001C — Final Scorecard
Date: ____________
Auditor: Claude Code (Opus 4.6)

Pre-Flight:
  PF-1 (validate-local):          [ PASS / FAIL ]
  PF-2 (TypeScript):              [ PASS / FAIL ]
  PF-3 (Backend health):          [ PASS / FAIL / SKIP ]
  PF-4 (Evidence dir):            [ PASS / FAIL ]
  PF-5 (FINAL_MASTER):            [ PASS / FAIL ]

Verification Families:
  VF-01 (F-1 MCP Endpoint):       __ / 3  checks PASS
  VF-02 (F-3 Quarantine Dedup):   __ / 3  checks PASS
  VF-03 (F-4 Agent DB Config):    __ / 2  checks PASS
  VF-04 (F-6 FSM Promotion):      __ / 3  checks PASS
  VF-05 (F-9 Idempotency):        __ / 3  checks PASS
  VF-06 (F-11 Status Constraint): __ / 2  checks PASS
  VF-07 (F-13 Retention Cleanup): __ / 2  checks PASS
  VF-08 (Legal Hold Migration):   __ / 4  checks PASS
  VF-09 (GDPR Purge):             __ / 5  checks PASS
  VF-10 (Retention Policy):       __ / 4  checks PASS
  VF-11 (Compliance Endpoint):    __ / 3  checks PASS
  VF-12 (Cognitive Services):     __ / 5  checks PASS
  VF-13 (Ambient UI):             __ / 5  checks PASS
  VF-14 (API Client):             __ / 4  checks PASS
  VF-15 (DealBrain Panel):        __ / 5  checks PASS

Cross-Consistency:
  XC-1 (MCP/Backend alignment):   [ PASS / FAIL ]
  XC-2 (GDPR/Legal Hold):         [ PASS / FAIL / SKIP ]
  XC-3 (Retention/Spec):          [ PASS / FAIL / SKIP ]
  XC-4 (Dashboard/Backend):       [ PASS / FAIL / PARTIAL ]
  XC-5 (Finding coverage):        [ PASS / FAIL ]

Stress Tests:
  ST-1 (DDL default stage):       [ PASS / FAIL ]
  ST-2 (Transition matrix):       [ PASS / FAIL ]
  ST-3 (use client directive):    [ PASS / FAIL / SKIP ]
  ST-4 (Promise.all ban):         [ PASS / FAIL / SKIP ]
  ST-5 (Retention tiers):         [ PASS / FAIL / SKIP ]

Summary:
  Total gates:          __ / 78
  PASS:                 __
  FAIL:                 __
  NOT_IMPLEMENTED:      __
  SKIP:                 __
  INFO:                 __

  Remediations Applied: __
  Enhancement Opportunities: 10 (ENH-1 through ENH-10)

  Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **QA only** — Do not build new features. If a gate reveals a NOT_IMPLEMENTED component, classify it and move on. Do not create the component.
2. **Remediate, don't redesign** — Fixes for FAIL gates must follow existing patterns. Do not refactor while remediating.
3. **Evidence-based** — Every PASS needs tee'd output in `$EVIDENCE_DIR`. A PASS without evidence is not a PASS.
4. **Services-down accommodation** — If PF-3 (backend health) fails, live verification gates become code-only. Mark as SKIP(services-down), not FAIL.
5. **TriPass findings: verify the FIX, not re-audit the finding** — The TriPass already identified the problems. This QA verifies that fixes exist and are correct. Do not re-investigate the root causes.
6. **Surface 9 compliance** — All dashboard component checks include `'use client'` directive and `console.warn` (not `console.error`) verification.
7. **Generated files are read-only** — Do not modify `api-types.generated.ts` or `backend_models.py`. Use bridge files for type extensions.
8. **NOT_IMPLEMENTED is not FAIL** — Features from Sprint 3 (Compliance) and Sprint 5 (Ambient UI) that do not exist yet are expected gaps, not regressions.
9. **WSL safety** — If any .sh files are created during remediation, strip CRLF (`sed -i 's/\r$//'`) and fix ownership (`chown zaks:zaks`).
10. **Record all changes** — Every remediation must be recorded in `/home/zaks/bookkeeping/CHANGES.md`.

---

## 10. Stop Condition

Stop when:
- All 78 verification gates pass (PASS), are justified (SKIP/NOT_IMPLEMENTED with classification), or are remediated (FAIL -> fix -> re-gate -> PASS)
- All remediations are applied and re-verified
- `make validate-local` passes as final check
- The scorecard is complete with evidence file paths for every gate
- All changes are recorded in `/home/zaks/bookkeeping/CHANGES.md`

Do NOT proceed to implementing Sprint 3 (Compliance) or Sprint 5 (Ambient UI) features. Those are separate execution missions.

---

*End of QA Mission Prompt — QA-COL-DEEP-VERIFY-001C*
