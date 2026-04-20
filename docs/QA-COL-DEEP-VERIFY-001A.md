# QA MISSION: QA-COL-DEEP-VERIFY-001A
## Deep Spec-Level Verification — Storage Foundation + Deal Brain + Security Pipeline + Multi-User Identity
## Date: 2026-02-13
## Classification: Deep QA Verification (Code-Level Spec Compliance)
## Prerequisite: COL-V2-CORE-001 (SM-2) execution or equivalent implementation
## Successor: QA-COL-DEEP-VERIFY-001B (Sections S5, S6, S8, S9, S11-S15)
## Standard: Mission Prompt Standard v2.2 (TYPE 2 QA)

---

## 1. Mission Objective

This is an **independent, deep code-level verification** of the COL-V2 implementation against spec sections S3 (Canonical Storage Unification), S4 (Deal Brain v2), S7 (Prompt Injection & Input-Side Defenses), and S10 (Multi-User Hardening) from the COL Design Specification V2.

This mission does NOT verify at the "does the file exist?" level. It reads actual code, checks actual columns, counts actual patterns, and compares actual implementations against the spec line-by-line. Every check has a concrete bash command that produces evidence.

**Source Artifacts:**

| Artifact | Path | Lines |
|----------|------|-------|
| COL-DESIGN-SPEC-V2.md | `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` | 3,276 |
| Master Program | `/home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md` | — |
| Actionable Items Register | `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` | — |

**Scope Sections:** S3 (S3.1-S3.10), S4 (S4.1-S4.7), S7 (S7.1-S7.4), S10 (S10.1-S10.7)

**Evidence Directory:** `/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001a/`

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001a
```

---

## 2. Pre-Flight

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee $EVIDENCE_DIR/PF-1-validate-local.txt
```
**PASS if:** exit 0. If not, stop — codebase is broken before QA starts.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee $EVIDENCE_DIR/PF-2-tsc.txt
```
**PASS if:** exit 0 with no errors.

### PF-3: Agent-API Container Alive
```bash
curl -sf http://localhost:8095/health 2>&1 | tee $EVIDENCE_DIR/PF-3-agent-health.txt
```
**PASS if:** HTTP 200. If FAIL, live verification gates (VF-15, ST-1) become code-only SKIP.

### PF-4: Evidence Directory Ready
```bash
mkdir -p $EVIDENCE_DIR && ls -la $EVIDENCE_DIR 2>&1 | tee $EVIDENCE_DIR/PF-4-evidence-dir.txt
```
**PASS if:** directory exists and is writable.

### PF-5: Source Spec Exists and Is >= 3,000 Lines
```bash
wc -l /home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md 2>&1 | tee $EVIDENCE_DIR/PF-5-spec-lines.txt
```
**PASS if:** line count >= 3000.

---

## 3. Verification Families

---

## Verification Family 01 — Migration 004 Schema Completeness (S3.3)

### VF-01.1: All 9 Tables from Spec Exist in Migration 004
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "Migration file: $MIGRATION"
for TABLE in user_identity_map chat_threads chat_messages thread_ownership session_summaries turn_snapshots cost_ledger deal_budgets cross_db_outbox; do
  COUNT=$(grep -ci "CREATE TABLE.*${TABLE}" "$MIGRATION" 2>/dev/null || echo 0)
  echo "$TABLE: $COUNT occurrence(s)"
done 2>&1 | tee $EVIDENCE_DIR/VF-01-1.txt
```
**PASS if:** All 9 tables show >= 1 occurrence.

### VF-01.2: chat_threads Has ALL Spec Columns (Legal Hold + Compliance)
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
for COL in legal_hold legal_hold_reason legal_hold_set_by legal_hold_set_at compliance_tier scope_type; do
  FOUND=$(grep -c "$COL" "$MIGRATION" 2>/dev/null || echo 0)
  echo "$COL: $FOUND occurrence(s)"
done
echo "---"
echo "scope_type CHECK constraint:"
grep -A2 "chk_scope" "$MIGRATION" 2>/dev/null || echo "NOT FOUND"
echo "---"
echo "delete CHECK constraint:"
grep -A4 "chk_delete" "$MIGRATION" 2>/dev/null || echo "NOT FOUND"
2>&1 | tee $EVIDENCE_DIR/VF-01-2.txt
```
**PASS if:** All 6 columns found. `chk_scope` CHECK constraint includes `global`, `deal`, `document`. `chk_delete` constraint exists.

### VF-01.3: chat_messages Has UNIQUE(thread_id, turn_number) Constraint (GAP-M2)
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "UNIQUE constraint search:"
grep -in "UNIQUE.*thread_id.*turn_number\|uq_thread_turn" "$MIGRATION" 2>/dev/null || echo "NOT FOUND"
echo "---"
echo "turn_number column:"
grep -n "turn_number" "$MIGRATION" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-01-3.txt
```
**PASS if:** UNIQUE constraint on (thread_id, turn_number) is present.

### VF-01.4: turn_snapshots Is PARTITIONED BY RANGE(created_at) with DEFAULT Partition
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "Partition declaration:"
grep -in "PARTITION BY RANGE" "$MIGRATION" 2>/dev/null | grep -i "turn_snapshot" || echo "NOT FOUND in turn_snapshots context"
grep -in "PARTITION BY RANGE.*created_at" "$MIGRATION" 2>/dev/null || echo "NO PARTITION BY RANGE(created_at) FOUND"
echo "---"
echo "DEFAULT partition:"
grep -in "turn_snapshots_default\|PARTITION OF turn_snapshots DEFAULT" "$MIGRATION" 2>/dev/null || echo "NOT FOUND"
2>&1 | tee $EVIDENCE_DIR/VF-01-4.txt
```
**PASS if:** `turn_snapshots` is `PARTITION BY RANGE (created_at)` and a DEFAULT partition exists.

### VF-01.5: cost_ledger Is PARTITIONED with DEFAULT Partition and deal_cost_summary VIEW
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "cost_ledger partition:"
grep -in "cost_ledger" "$MIGRATION" 2>/dev/null | grep -i "PARTITION BY RANGE" || echo "NOT FOUND"
echo "---"
echo "DEFAULT partition:"
grep -in "cost_ledger_default\|PARTITION OF cost_ledger DEFAULT" "$MIGRATION" 2>/dev/null || echo "NOT FOUND"
echo "---"
echo "deal_cost_summary VIEW:"
grep -in "deal_cost_summary" "$MIGRATION" 2>/dev/null || echo "NOT FOUND"
grep -in "CREATE.*VIEW.*deal_cost_summary" "$MIGRATION" 2>/dev/null || echo "VIEW creation NOT FOUND"
2>&1 | tee $EVIDENCE_DIR/VF-01-5.txt
```
**PASS if:** `cost_ledger` is partitioned by range, has DEFAULT partition, and `deal_cost_summary` VIEW exists (not materialized view — spec GAP-M12).

**Gate VF-01:** All 5 checks pass. Migration 004 schema is complete and matches spec S3.3.

---

## Verification Family 02 — ChatRepository Methods (S3.6)

### VF-02.1: create_thread() Creates thread_ownership Row
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
echo "File: $REPO_FILE"
echo "---"
echo "create_thread method:"
grep -n "async def create_thread\|def create_thread" "$REPO_FILE" 2>/dev/null || echo "NOT FOUND"
echo "---"
echo "thread_ownership write in create_thread context:"
python3 -c "
import re
with open('$REPO_FILE', 'r') as f:
    content = f.read()
match = re.search(r'(async )?def create_thread.*?(?=\n    (async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    body = match.group(0)
    if 'thread_ownership' in body or 'ownership' in body.lower():
        print('FOUND: thread_ownership reference in create_thread')
        for i, line in enumerate(body.split('\n')):
            if 'ownership' in line.lower():
                print(f'  Line: {line.strip()}')
    else:
        print('NOT FOUND: no thread_ownership reference in create_thread')
else:
    print('create_thread method not found')
" 2>&1 | tee $EVIDENCE_DIR/VF-02-1.txt
```
**PASS if:** `create_thread()` method exists and writes to `thread_ownership`.

### VF-02.2: get_thread() Includes user_id Ownership Check (S10.3)
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
python3 -c "
import re
with open('$REPO_FILE', 'r') as f:
    content = f.read()
match = re.search(r'(async )?def get_thread.*?(?=\n    (async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    body = match.group(0)
    has_user_id_param = 'user_id' in body.split('\n')[0]
    has_ownership_check = any(kw in body.lower() for kw in ['user_id', 'ownership', 'permission', 'authorize'])
    print(f'user_id parameter: {has_user_id_param}')
    print(f'Ownership/authorization check: {has_ownership_check}')
    # Show the method signature and first 15 lines
    lines = body.split('\n')[:15]
    for line in lines:
        print(f'  {line}')
else:
    print('get_thread method not found')
" 2>&1 | tee $EVIDENCE_DIR/VF-02-2.txt
```
**PASS if:** `get_thread()` accepts `user_id` parameter and includes ownership verification.

### VF-02.3: soft_delete_thread() Blocks on legal_hold=TRUE (S11.1 -> 409)
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
python3 -c "
import re
with open('$REPO_FILE', 'r') as f:
    content = f.read()
match = re.search(r'(async )?def soft_delete_thread.*?(?=\n    (async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    body = match.group(0)
    has_legal_hold = 'legal_hold' in body
    has_409 = '409' in body
    has_conflict = 'conflict' in body.lower()
    print(f'legal_hold check: {has_legal_hold}')
    print(f'409 status code: {has_409}')
    print(f'Conflict reference: {has_conflict}')
    lines = body.split('\n')[:20]
    for line in lines:
        print(f'  {line}')
else:
    print('soft_delete_thread method not found')
" 2>&1 | tee $EVIDENCE_DIR/VF-02-3.txt
```
**PASS if:** `soft_delete_thread()` checks `legal_hold` and returns/raises 409 Conflict when true.

### VF-02.4: hard_delete_thread() Performs Cascading Delete (S11.2)
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
python3 -c "
import re
with open('$REPO_FILE', 'r') as f:
    content = f.read()
match = re.search(r'(async )?def hard_delete_thread.*?(?=\n    (async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    body = match.group(0)
    tables = ['session_summaries', 'turn_snapshots', 'cost_ledger', 'cross_db_outbox',
              'decision_ledger', 'checkpoint', 'thread_ownership', 'chat_messages', 'chat_threads']
    print('Cascade delete coverage:')
    for table in tables:
        found = table.lower() in body.lower()
        print(f'  {table}: {\"FOUND\" if found else \"NOT FOUND\"} ')
    print(f'---')
    print(f'Total lines: {len(body.split(chr(10)))}')
else:
    print('hard_delete_thread method not found')
" 2>&1 | tee $EVIDENCE_DIR/VF-02-4.txt
```
**PASS if:** `hard_delete_thread()` deletes from at least 6 of the 9 spec-listed tables (session_summaries, turn_snapshots, cost_ledger, cross_db_outbox, decision_ledger, checkpoints, thread_ownership, chat_messages, chat_threads).

### VF-02.5: get_messages() Uses Cursor Pagination by turn_number (S3.5)
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
python3 -c "
import re
with open('$REPO_FILE', 'r') as f:
    content = f.read()
match = re.search(r'(async )?def get_messages.*?(?=\n    (async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    body = match.group(0)
    has_before_turn = 'before_turn' in body
    has_cursor = 'cursor' in body.lower() or 'before_turn' in body
    has_turn_number = 'turn_number' in body
    print(f'before_turn parameter: {has_before_turn}')
    print(f'Cursor-based pagination: {has_cursor}')
    print(f'turn_number reference: {has_turn_number}')
    sig = body.split('\n')[0]
    print(f'Signature: {sig.strip()}')
else:
    print('get_messages method not found')
" 2>&1 | tee $EVIDENCE_DIR/VF-02-5.txt
```
**PASS if:** `get_messages()` has `before_turn` parameter and uses `turn_number` for cursor pagination (not offset-based).

### VF-02.6: enqueue_brain_extraction() Writes to cross_db_outbox (GAP-M4)
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
python3 -c "
import re
with open('$REPO_FILE', 'r') as f:
    content = f.read()
match = re.search(r'(async )?def enqueue_brain_extraction.*?(?=\n    (async )?def |\nclass |\Z)', content, re.DOTALL)
if match:
    body = match.group(0)
    has_outbox = 'cross_db_outbox' in body or 'outbox' in body.lower()
    has_brain = 'brain' in body.lower()
    print(f'cross_db_outbox reference: {has_outbox}')
    print(f'brain reference: {has_brain}')
    lines = body.split('\n')[:15]
    for line in lines:
        print(f'  {line}')
else:
    print('enqueue_brain_extraction method not found')
" 2>&1 | tee $EVIDENCE_DIR/VF-02-6.txt
```
**PASS if:** `enqueue_brain_extraction()` method exists and references `cross_db_outbox` or outbox pattern.

**Gate VF-02:** All 6 checks pass. ChatRepository implements all spec S3.6 operations with ownership, legal hold, cascade, and outbox patterns.

---

## Verification Family 03 — Chatbot API Endpoints (S3.5)

### VF-03.1: GET /threads Endpoint with user_id Filtering
```bash
CHATBOT_FILE=$(find /home/zaks/zakops-agent-api -name "chatbot.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
echo "File: $CHATBOT_FILE"
echo "---"
grep -n "GET\|get.*threads\|list_threads\|@.*get.*thread" "$CHATBOT_FILE" 2>/dev/null | head -20
echo "---"
grep -n "user_id" "$CHATBOT_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-03-1.txt
```
**PASS if:** A GET endpoint for listing threads exists and filters by `user_id`.

### VF-03.2: GET /threads/{id}/messages with Cursor Pagination (before_turn)
```bash
CHATBOT_FILE=$(find /home/zaks/zakops-agent-api -name "chatbot.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "messages\|before_turn\|cursor\|turn_number" "$CHATBOT_FILE" 2>/dev/null | head -20
echo "---"
grep -n "GET.*message\|get.*message" "$CHATBOT_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-03-2.txt
```
**PASS if:** Messages endpoint exists with `before_turn` query parameter for cursor pagination.

### VF-03.3: POST /threads Creates Thread + Ownership
```bash
CHATBOT_FILE=$(find /home/zaks/zakops-agent-api -name "chatbot.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "POST\|post.*thread\|create_thread" "$CHATBOT_FILE" 2>/dev/null | head -10
echo "---"
grep -n "ownership" "$CHATBOT_FILE" 2>/dev/null | head -5
2>&1 | tee $EVIDENCE_DIR/VF-03-3.txt
```
**PASS if:** POST endpoint for thread creation exists and invokes `create_thread` (which creates ownership per VF-02.1).

### VF-03.4: PATCH /threads/{id} Supports title/pinned/archived
```bash
CHATBOT_FILE=$(find /home/zaks/zakops-agent-api -name "chatbot.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "PATCH\|patch.*thread\|update_thread" "$CHATBOT_FILE" 2>/dev/null | head -10
echo "---"
for FIELD in title pinned archived; do
  COUNT=$(grep -c "$FIELD" "$CHATBOT_FILE" 2>/dev/null || echo 0)
  echo "$FIELD: $COUNT occurrence(s)"
done
2>&1 | tee $EVIDENCE_DIR/VF-03-4.txt
```
**PASS if:** PATCH endpoint exists and references `title`, `pinned`, and `archived` fields.

### VF-03.5: DELETE /threads/{id} with Soft/Permanent Delete + Legal Hold Block
```bash
CHATBOT_FILE=$(find /home/zaks/zakops-agent-api -name "chatbot.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "DELETE\|delete.*thread\|soft_delete\|hard_delete\|permanent" "$CHATBOT_FILE" 2>/dev/null | head -15
echo "---"
grep -n "legal_hold\|409\|Conflict" "$CHATBOT_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-03-5.txt
```
**PASS if:** DELETE endpoint exists with `permanent` parameter support. Legal hold block references present (409/Conflict).

**Gate VF-03:** All 5 checks pass. Chatbot API covers all spec S3.5 endpoint categories.

---

## Verification Family 04 — Middleware Routing (S3.5-MW)

### VF-04.1: /api/v1/chatbot/* Routes Are Handled (GAP-H1 Fix)
```bash
MW_FILE=$(find /home/zaks/zakops-agent-api/apps/dashboard -name "middleware.ts" -not -path "*/node_modules/*" 2>/dev/null | head -1)
echo "File: $MW_FILE"
echo "---"
grep -n "chatbot\|v1/chatbot\|CHATBOT" "$MW_FILE" 2>/dev/null | head -10
echo "---"
echo "Agent API routing:"
grep -n "8095\|agent.api\|agentApi\|agent-api" "$MW_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-04-1.txt
```
**PASS if:** Middleware routes `/api/v1/chatbot/*` requests (to agent-api on port 8095 or equivalent).

### VF-04.2: X-User-Id Header Is Injected (S10.2)
```bash
MW_FILE=$(find /home/zaks/zakops-agent-api/apps/dashboard -name "middleware.ts" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "X-User-Id\|x-user-id\|ZAKOPS_USER_ID" "$MW_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-04-2.txt
```
**PASS if:** `X-User-Id` header is set in outgoing proxy requests.

### VF-04.3: X-User-Role Header Is Injected (S10.2)
```bash
MW_FILE=$(find /home/zaks/zakops-agent-api/apps/dashboard -name "middleware.ts" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "X-User-Role\|x-user-role\|User-Role" "$MW_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-04-3.txt
```
**PASS if:** `X-User-Role` header is set in outgoing proxy requests.

**Gate VF-04:** All 3 checks pass. Dashboard middleware correctly routes chatbot requests and injects identity headers.

---

## Verification Family 05 — Migration 028 Deal Brain Schema (S4.2)

### VF-05.1: deal_brain Table Has ALL Spec Columns
```bash
MIGRATION_028=$(find /home/zaks/zakops-backend -path "*/migrations/*028*" -name "*.sql" 2>/dev/null | head -1)
if [ -z "$MIGRATION_028" ]; then
  MIGRATION_028=$(find /home/zaks/zakops-backend -name "*deal_brain*" -name "*.sql" 2>/dev/null | head -1)
fi
echo "File: $MIGRATION_028"
echo "---"
for COL in summary facts risks decisions assumptions open_items ghost_facts momentum_score entities email_facts_count; do
  COUNT=$(grep -c "$COL" "$MIGRATION_028" 2>/dev/null || echo 0)
  echo "$COL: $COUNT occurrence(s)"
done
2>&1 | tee $EVIDENCE_DIR/VF-05-1.txt
```
**PASS if:** All 10 columns (summary, facts, risks, decisions, assumptions, open_items, ghost_facts, momentum_score, entities, email_facts_count) found in migration.

### VF-05.2: deal_brain_history with version/snapshot/diff/trigger_type
```bash
MIGRATION_028=$(find /home/zaks/zakops-backend -path "*/migrations/*028*" -name "*.sql" 2>/dev/null | head -1)
if [ -z "$MIGRATION_028" ]; then
  MIGRATION_028=$(find /home/zaks/zakops-backend -name "*deal_brain*" -name "*.sql" 2>/dev/null | head -1)
fi
echo "deal_brain_history table:"
grep -in "deal_brain_history" "$MIGRATION_028" 2>/dev/null | head -5
echo "---"
for COL in version snapshot diff trigger_type; do
  FOUND=$(grep -c "$COL" "$MIGRATION_028" 2>/dev/null || echo 0)
  echo "$COL: $FOUND occurrence(s)"
done
2>&1 | tee $EVIDENCE_DIR/VF-05-2.txt
```
**PASS if:** `deal_brain_history` table exists with `version`, `snapshot`, `diff`, and `trigger_type` columns.

### VF-05.3: deal_entity_graph with UNIQUE Constraint
```bash
MIGRATION_028=$(find /home/zaks/zakops-backend -path "*/migrations/*028*" -name "*.sql" 2>/dev/null | head -1)
if [ -z "$MIGRATION_028" ]; then
  MIGRATION_028=$(find /home/zaks/zakops-backend -name "*deal_brain*" -name "*.sql" 2>/dev/null | head -1)
fi
echo "deal_entity_graph table:"
grep -in "deal_entity_graph" "$MIGRATION_028" 2>/dev/null | head -5
echo "---"
echo "Columns:"
for COL in entity_type normalized_name deal_id; do
  FOUND=$(grep -c "$COL" "$MIGRATION_028" 2>/dev/null || echo 0)
  echo "  $COL: $FOUND"
done
echo "---"
echo "UNIQUE constraint:"
grep -in "UNIQUE.*entity_type.*normalized_name.*deal_id\|UNIQUE.*deal_entity" "$MIGRATION_028" 2>/dev/null || echo "NOT FOUND"
2>&1 | tee $EVIDENCE_DIR/VF-05-3.txt
```
**PASS if:** `deal_entity_graph` table exists with `entity_type`, `normalized_name`, `deal_id` columns and a UNIQUE constraint on the combination.

### VF-05.4: decision_outcomes Table Exists
```bash
MIGRATION_028=$(find /home/zaks/zakops-backend -path "*/migrations/*028*" -name "*.sql" 2>/dev/null | head -1)
if [ -z "$MIGRATION_028" ]; then
  MIGRATION_028=$(find /home/zaks/zakops-backend -name "*deal_brain*" -name "*.sql" 2>/dev/null | head -1)
fi
echo "decision_outcomes table:"
grep -in "decision_outcomes" "$MIGRATION_028" 2>/dev/null | head -5
echo "---"
grep -in "CREATE TABLE.*decision_outcomes" "$MIGRATION_028" 2>/dev/null || echo "NOT FOUND"
2>&1 | tee $EVIDENCE_DIR/VF-05-4.txt
```
**PASS if:** `decision_outcomes` table is created in the migration.

### VF-05.5: deal_access Table with Role CHECK Constraint
```bash
MIGRATION_028=$(find /home/zaks/zakops-backend -path "*/migrations/*028*" -name "*.sql" 2>/dev/null | head -1)
if [ -z "$MIGRATION_028" ]; then
  MIGRATION_028=$(find /home/zaks/zakops-backend -name "*deal_brain*" -name "*.sql" 2>/dev/null | head -1)
fi
echo "deal_access table:"
grep -in "deal_access" "$MIGRATION_028" 2>/dev/null | head -5
echo "---"
echo "Role CHECK constraint:"
grep -in "chk_deal_role\|CHECK.*role.*IN\|viewer.*operator.*approver.*admin" "$MIGRATION_028" 2>/dev/null | head -5
2>&1 | tee $EVIDENCE_DIR/VF-05-5.txt
```
**PASS if:** `deal_access` table exists with CHECK constraint on `role` column containing `viewer`, `operator`, `approver`, `admin`.

**Gate VF-05:** All 5 checks pass. Migration 028 schema matches spec S4.2 for Deal Brain v2.

---

## Verification Family 06 — Deal Brain Service (S4.3-S4.5)

### VF-06.1: get_brain() and get_or_create_brain() Methods
```bash
BRAIN_FILE=$(find /home/zaks/zakops-backend -name "deal_brain_service.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
echo "File: $BRAIN_FILE"
echo "---"
grep -n "def get_brain\|def get_or_create_brain" "$BRAIN_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-06-1.txt
```
**PASS if:** Both `get_brain()` and `get_or_create_brain()` methods exist.

### VF-06.2: add_facts() with Confidence Scoring
```bash
BRAIN_FILE=$(find /home/zaks/zakops-backend -name "deal_brain_service.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
grep -n "def add_facts\|def update_facts" "$BRAIN_FILE" 2>/dev/null | head -5
echo "---"
grep -n "confidence" "$BRAIN_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-06-2.txt
```
**PASS if:** `add_facts()` (or `update_facts()`) method exists with confidence scoring logic.

### VF-06.3: extract_from_turn() for Per-Turn Extraction (S4.3)
```bash
BRAIN_FILE=$(find /home/zaks/zakops-backend -name "deal_brain_service.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
grep -n "def extract_from_turn\|def extract_from\|def extract" "$BRAIN_FILE" 2>/dev/null | head -10
echo "---"
echo "Turn-related methods:"
grep -n "turn\|message\|conversation" "$BRAIN_FILE" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/VF-06-3.txt
```
**PASS if:** An extraction method exists that processes per-turn conversation data (matches spec S4.3 trigger: "After every assistant response in deal-scoped chat").

### VF-06.4: record_history() for Version Tracking
```bash
BRAIN_FILE=$(find /home/zaks/zakops-backend -name "deal_brain_service.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
grep -n "def record_history\|def save_history\|deal_brain_history\|history" "$BRAIN_FILE" 2>/dev/null | head -15
echo "---"
grep -n "version" "$BRAIN_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-06-4.txt
```
**PASS if:** History recording method exists that writes to `deal_brain_history` with version tracking.

### VF-06.5: Entity Extraction (deal_entity_graph Writes)
```bash
BRAIN_FILE=$(find /home/zaks/zakops-backend -name "deal_brain_service.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
grep -n "entity\|deal_entity_graph\|EntityResolver\|extract_entities" "$BRAIN_FILE" 2>/dev/null | head -10
echo "---"
# Also check for a separate entity resolver file
find /home/zaks/zakops-backend -name "*entity*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null
2>&1 | tee $EVIDENCE_DIR/VF-06-5.txt
```
**PASS if:** Entity extraction exists (either in DealBrainService or a separate EntityResolver) that writes to `deal_entity_graph`.

**Gate VF-06:** All 5 checks pass. DealBrainService implements spec S4.3-S4.5 operations.

---

## Verification Family 07 — Ghost Knowledge Detection (QW-1, S20.1)

### VF-07.1: detect() Method with user_message + existing_facts Parameters
```bash
GHOST_FILE=$(find /home/zaks/zakops-backend -name "ghost_knowledge_detector.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GHOST_FILE" ]; then
  GHOST_FILE=$(find /home/zaks/zakops-agent-api -name "ghost_knowledge*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
echo "File: $GHOST_FILE"
echo "---"
grep -n "def detect\|class Ghost" "$GHOST_FILE" 2>/dev/null | head -10
echo "---"
echo "Method signature:"
grep -A5 "def detect" "$GHOST_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-07-1.txt
```
**PASS if:** `detect()` method exists and accepts user message and existing facts as input.

### VF-07.2: Regex Patterns for $amounts, %, Dates, Proper Nouns (S4.4)
```bash
GHOST_FILE=$(find /home/zaks/zakops-backend -name "ghost_knowledge_detector.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GHOST_FILE" ]; then
  GHOST_FILE=$(find /home/zaks/zakops-agent-api -name "ghost_knowledge*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
echo "Pattern analysis:"
grep -n "\\$\|amount\|dollar\|percent\|%\|date\|proper.noun\|[A-Z][a-z]\|pattern\|regex\|re\.\|PATTERN" "$GHOST_FILE" 2>/dev/null | head -20
echo "---"
echo "All pattern definitions:"
grep -n "PATTERN\|pattern\|r'" "$GHOST_FILE" 2>/dev/null | head -20
2>&1 | tee $EVIDENCE_DIR/VF-07-2.txt
```
**PASS if:** Regex patterns exist for detecting at least 3 of 4 categories: dollar amounts, percentages, dates, proper nouns.

### VF-07.3: Returns Ghost Knowledge Flags with key/value/confidence
```bash
GHOST_FILE=$(find /home/zaks/zakops-backend -name "ghost_knowledge_detector.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GHOST_FILE" ]; then
  GHOST_FILE=$(find /home/zaks/zakops-agent-api -name "ghost_knowledge*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
for FIELD in key value confidence; do
  COUNT=$(grep -c "$FIELD" "$GHOST_FILE" 2>/dev/null || echo 0)
  echo "$FIELD: $COUNT occurrence(s)"
done
echo "---"
echo "Return type / dataclass / dict structure:"
grep -n "return\|dataclass\|TypedDict\|class.*Ghost\|ghost_knowledge" "$GHOST_FILE" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/VF-07-3.txt
```
**PASS if:** Output structure includes `key`, `value`, and `confidence` fields.

### VF-07.4: GHOST_CONFIDENCE_THRESHOLD Constant
```bash
GHOST_FILE=$(find /home/zaks/zakops-backend -name "ghost_knowledge_detector.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GHOST_FILE" ]; then
  GHOST_FILE=$(find /home/zaks/zakops-agent-api -name "ghost_knowledge*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
grep -n "THRESHOLD\|threshold\|CONFIDENCE\|MIN_CONFIDENCE" "$GHOST_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-07-4.txt
```
**PASS if:** A confidence threshold constant exists (named `GHOST_CONFIDENCE_THRESHOLD` or equivalent).

**Gate VF-07:** All 4 checks pass. Ghost Knowledge Detector implements spec QW-1/S20.1.

---

## Verification Family 08 — Momentum Calculator (QW-2, S20.2)

### VF-08.1: 5 Weighted Components Match Spec Weights
```bash
MOMENTUM_FILE=$(find /home/zaks/zakops-backend -name "momentum_calculator.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$MOMENTUM_FILE" ]; then
  MOMENTUM_FILE=$(find /home/zaks/zakops-agent-api -name "momentum*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
echo "File: $MOMENTUM_FILE"
echo "---"
echo "Weight definitions:"
grep -n "weight\|0\.30\|0\.20\|0\.15\|stage_velocity\|event_frequency\|open_item\|risk_trajectory\|action_rate" "$MOMENTUM_FILE" 2>/dev/null | head -20
2>&1 | tee $EVIDENCE_DIR/VF-08-1.txt
```
**PASS if:** 5 components found: stage_velocity(0.30), event_frequency(0.20), open_item_completion(0.20), risk_trajectory(0.15), action_rate(0.15). Weights must sum to 1.00.

### VF-08.2: Score Range 0-100
```bash
MOMENTUM_FILE=$(find /home/zaks/zakops-backend -name "momentum_calculator.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$MOMENTUM_FILE" ]; then
  MOMENTUM_FILE=$(find /home/zaks/zakops-agent-api -name "momentum*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
grep -n "100\|min\|max\|clamp\|0.*100\|score.*range" "$MOMENTUM_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-08-2.txt
```
**PASS if:** Score is bounded to 0-100 range (via min/max/clamp or equivalent).

### VF-08.3: Color Coding — green(80-100), blue(50-79), amber(20-49), red(0-19)
```bash
MOMENTUM_FILE=$(find /home/zaks/zakops-backend -name "momentum_calculator.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$MOMENTUM_FILE" ]; then
  MOMENTUM_FILE=$(find /home/zaks/zakops-agent-api -name "momentum*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
grep -n "green\|blue\|amber\|red\|color\|colour\|80\|50\|20\|tier\|band\|level" "$MOMENTUM_FILE" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/VF-08-3.txt
```
**PASS if:** Color/tier coding exists with 4 bands matching spec thresholds.

### VF-08.4: compute() Method Takes deal_id Parameter
```bash
MOMENTUM_FILE=$(find /home/zaks/zakops-backend -name "momentum_calculator.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$MOMENTUM_FILE" ]; then
  MOMENTUM_FILE=$(find /home/zaks/zakops-agent-api -name "momentum*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
grep -n "def compute\|def calculate\|def compute_and_store" "$MOMENTUM_FILE" 2>/dev/null | head -10
echo "---"
grep -A3 "def compute\|def calculate\|def compute_and_store" "$MOMENTUM_FILE" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/VF-08-4.txt
```
**PASS if:** `compute()` (or `compute_and_store()`) method exists and takes `deal_id` as parameter.

**Gate VF-08:** All 4 checks pass. Momentum Calculator implements spec QW-2/S20.2 with correct weights, range, and color coding.

---

## Verification Family 09 — Injection Guard (S7.3 Layer 1)

### VF-09.1: ScanResult Dataclass with passed/patterns_found/severity/sanitized_content
```bash
GUARD_FILE=$(find /home/zaks/zakops-agent-api -name "injection_guard.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
if [ -z "$GUARD_FILE" ]; then
  GUARD_FILE=$(find /home/zaks/zakops-backend -name "injection_guard*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
echo "File: $GUARD_FILE"
echo "---"
echo "ScanResult structure:"
grep -n "ScanResult\|dataclass\|class.*Result" "$GUARD_FILE" 2>/dev/null | head -10
echo "---"
for FIELD in passed patterns_found severity sanitized_content; do
  COUNT=$(grep -c "$FIELD" "$GUARD_FILE" 2>/dev/null || echo 0)
  echo "$FIELD: $COUNT occurrence(s)"
done
2>&1 | tee $EVIDENCE_DIR/VF-09-1.txt
```
**PASS if:** `ScanResult` dataclass (or equivalent) exists with all 4 fields: `passed`, `patterns_found`, `severity`, `sanitized_content`.

### VF-09.2: INJECTION_PATTERNS List with >= 12 Patterns (Spec Has 15)
```bash
GUARD_FILE=$(find /home/zaks/zakops-agent-api -name "injection_guard.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
if [ -z "$GUARD_FILE" ]; then
  GUARD_FILE=$(find /home/zaks/zakops-backend -name "injection_guard*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
echo "Pattern list:"
grep -n "INJECTION_PATTERNS\|PATTERNS\|patterns" "$GUARD_FILE" 2>/dev/null | head -5
echo "---"
echo "Pattern count (lines with regex):"
PATTERN_COUNT=$(grep -c "r\"\|r'" "$GUARD_FILE" 2>/dev/null || echo 0)
echo "Regex pattern lines: $PATTERN_COUNT"
echo "---"
echo "Individual patterns:"
grep -n "r\"\|r'" "$GUARD_FILE" 2>/dev/null | head -20
2>&1 | tee $EVIDENCE_DIR/VF-09-2.txt
```
**PASS if:** INJECTION_PATTERNS contains >= 12 patterns (spec defines 15).

### VF-09.3: 3 Severity Levels — low, medium, high
```bash
GUARD_FILE=$(find /home/zaks/zakops-agent-api -name "injection_guard.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
if [ -z "$GUARD_FILE" ]; then
  GUARD_FILE=$(find /home/zaks/zakops-backend -name "injection_guard*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
for LEVEL in '"low"' '"medium"' '"high"'; do
  COUNT=$(grep -c "$LEVEL" "$GUARD_FILE" 2>/dev/null || echo 0)
  echo "$LEVEL: $COUNT occurrence(s)"
done
echo "---"
grep -n "SEVERITY\|severity" "$GUARD_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-09-3.txt
```
**PASS if:** All 3 severity levels (low, medium, high) are present.

### VF-09.4: scan_input() Function Returns ScanResult
```bash
GUARD_FILE=$(find /home/zaks/zakops-agent-api -name "injection_guard.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
if [ -z "$GUARD_FILE" ]; then
  GUARD_FILE=$(find /home/zaks/zakops-backend -name "injection_guard*" -name "*.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
grep -n "def scan_input\|def scan\|-> ScanResult" "$GUARD_FILE" 2>/dev/null | head -10
echo "---"
grep -A5 "def scan_input\|def scan" "$GUARD_FILE" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/VF-09-4.txt
```
**PASS if:** `scan_input()` (or `scan()`) function exists and returns `ScanResult`.

**Gate VF-09:** All 4 checks pass. Injection Guard implements spec S7.3 Layer 1 with correct structure.

---

## Verification Family 10 — Canary Tokens (QW-3, S7.3 Layer 4)

### VF-10.1: inject_canary() Method Exists
```bash
CANARY_FILE=$(find /home/zaks/zakops-agent-api /home/zaks/zakops-backend -name "canary*" -name "*.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
echo "File: $CANARY_FILE"
echo "---"
grep -n "def inject_canary\|def inject\|class.*Canary" "$CANARY_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-10-1.txt
```
**PASS if:** `inject_canary()` method exists in a CanaryToken class/module.

### VF-10.2: verify_no_leakage() Method Exists
```bash
CANARY_FILE=$(find /home/zaks/zakops-agent-api /home/zaks/zakops-backend -name "canary*" -name "*.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "def verify_no_leakage\|def verify\|def check_leakage\|leaked" "$CANARY_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-10-2.txt
```
**PASS if:** `verify_no_leakage()` (or equivalent) method exists.

### VF-10.3: Token Generation Uses Hashing (Not Plaintext)
```bash
CANARY_FILE=$(find /home/zaks/zakops-agent-api /home/zaks/zakops-backend -name "canary*" -name "*.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
grep -n "hashlib\|sha256\|sha\|hash\|secrets\|token_bytes\|hmac" "$CANARY_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-10-3.txt
```
**PASS if:** Token generation uses cryptographic hashing (hashlib, sha256, or equivalent).

**Gate VF-10:** All 3 checks pass. Canary Token system implements spec S7.3 Layer 4.

---

## Verification Family 11 — Session Tracker (S7.3 Layer 3)

### VF-11.1: MAX_ATTEMPTS Threshold Constant
```bash
# Search across both repos for session injection tracking
TRACKER_FILE=$(find /home/zaks/zakops-agent-api /home/zaks/zakops-backend \
  \( -name "injection_guard*" -o -name "session*tracker*" -o -name "session*injection*" \) \
  -name "*.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null)
echo "Files found: $TRACKER_FILE"
echo "---"
for F in $TRACKER_FILE; do
  echo "=== $F ==="
  grep -n "MAX_ATTEMPTS\|LOCKDOWN\|max_attempts\|attempt.*limit\|escalat" "$F" 2>/dev/null | head -10
done
2>&1 | tee $EVIDENCE_DIR/VF-11-1.txt
```
**PASS if:** `MAX_ATTEMPTS_BEFORE_LOCKDOWN` (or equivalent threshold constant) exists.

### VF-11.2: record_attempt() or Equivalent Tracking Method
```bash
TRACKER_FILE=$(find /home/zaks/zakops-agent-api /home/zaks/zakops-backend \
  \( -name "injection_guard*" -o -name "session*tracker*" -o -name "session*injection*" \) \
  -name "*.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null)
for F in $TRACKER_FILE; do
  echo "=== $F ==="
  grep -n "def record_attempt\|def track\|def log_attempt\|SessionInjectionTracker\|class.*Tracker" "$F" 2>/dev/null | head -10
done
2>&1 | tee $EVIDENCE_DIR/VF-11-2.txt
```
**PASS if:** `record_attempt()` (or equivalent tracking method) exists in a session tracker class.

**Gate VF-11:** Both checks pass. Session-level escalation tracking implements spec S7.3 Layer 3.

---

## Verification Family 12 — SSE Event Catalog (S3.10, GAP-L2)

### VF-12.1: >= 10 Typed Event Models (Spec Has 14)
```bash
SSE_FILE=$(find /home/zaks/zakops-agent-api -name "sse_events.py" -o -name "sse*event*" -name "*.py" 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | head -1)
if [ -z "$SSE_FILE" ]; then
  SSE_FILE=$(find /home/zaks/zakops-agent-api -name "events.py" -path "*/sse/*" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
if [ -z "$SSE_FILE" ]; then
  echo "Searching broadly for SSE event definitions..."
  grep -rl "SSE\|sse.*event\|event.*type.*message_chunk\|event.*type.*brain_updated" /home/zaks/zakops-agent-api/apps/agent-api/ 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | head -5
fi
echo "File: $SSE_FILE"
echo "---"
if [ -n "$SSE_FILE" ]; then
  echo "Event type definitions:"
  grep -n "class.*Event\|event_type\|EVENT_TYPE\|message_chunk\|message_complete\|thread_updated\|brain_updated\|injection_alert\|budget_warning\|cost_update\|ghost_knowledge\|momentum_update\|tool_execution\|approval_required\|error\|summary_generated\|legal_hold" "$SSE_FILE" 2>/dev/null | head -30
  echo "---"
  EVENT_COUNT=$(grep -c "class.*Event\|event_type.*=\|EVENT_TYPE" "$SSE_FILE" 2>/dev/null || echo 0)
  echo "Approximate event type count: $EVENT_COUNT"
fi
2>&1 | tee $EVIDENCE_DIR/VF-12-1.txt
```
**PASS if:** >= 10 typed event models found (spec defines 14).

### VF-12.2: Includes ghost_knowledge Event Type
```bash
SSE_FILE=$(find /home/zaks/zakops-agent-api -name "sse_events.py" -o -name "sse*event*" -name "*.py" 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | head -1)
if [ -z "$SSE_FILE" ]; then
  grep -rn "ghost_knowledge" /home/zaks/zakops-agent-api/apps/agent-api/ 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | head -10
else
  grep -n "ghost_knowledge" "$SSE_FILE" 2>/dev/null | head -5
fi
2>&1 | tee $EVIDENCE_DIR/VF-12-2.txt
```
**PASS if:** `ghost_knowledge` event type is defined.

### VF-12.3: Includes legal_hold_set Event Type
```bash
SSE_FILE=$(find /home/zaks/zakops-agent-api -name "sse_events.py" -o -name "sse*event*" -name "*.py" 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | head -1)
if [ -z "$SSE_FILE" ]; then
  grep -rn "legal_hold_set\|legal_hold" /home/zaks/zakops-agent-api/apps/agent-api/ 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | head -10
else
  grep -n "legal_hold_set\|legal_hold" "$SSE_FILE" 2>/dev/null | head -5
fi
2>&1 | tee $EVIDENCE_DIR/VF-12-3.txt
```
**PASS if:** `legal_hold_set` event type is defined.

**Gate VF-12:** All 3 checks pass. SSE Event catalog covers spec S3.10 requirements.

---

## Verification Family 13 — User Identity Map (S3.2, GAP-C2)

### VF-13.1: user_identity_map Table with canonical_id VARCHAR(255) PK
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "user_identity_map definition:"
grep -A10 "CREATE TABLE.*user_identity_map" "$MIGRATION" 2>/dev/null | head -12
echo "---"
echo "canonical_id as PK:"
grep -n "canonical_id.*PRIMARY KEY\|canonical_id.*VARCHAR(255)" "$MIGRATION" 2>/dev/null | head -5
2>&1 | tee $EVIDENCE_DIR/VF-13-1.txt
```
**PASS if:** `user_identity_map` table has `canonical_id VARCHAR(255) PRIMARY KEY`.

### VF-13.2: All user_id Columns Across New Tables Are VARCHAR(255) (Not INTEGER)
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "All user_id column declarations:"
grep -n "user_id" "$MIGRATION" 2>/dev/null | head -20
echo "---"
echo "Check for INTEGER user_id (should be ZERO):"
INTEGER_COUNT=$(grep -c "user_id.*INTEGER\|user_id.*INT " "$MIGRATION" 2>/dev/null || echo 0)
echo "INTEGER user_id count: $INTEGER_COUNT"
echo "VARCHAR user_id count:"
VARCHAR_COUNT=$(grep -c "user_id.*VARCHAR" "$MIGRATION" 2>/dev/null || echo 0)
echo "VARCHAR user_id count: $VARCHAR_COUNT"
2>&1 | tee $EVIDENCE_DIR/VF-13-2.txt
```
**PASS if:** INTEGER user_id count = 0, VARCHAR user_id count >= 4 (chat_threads, chat_messages, thread_ownership, turn_snapshots, cost_ledger all use VARCHAR).

### VF-13.3: Role CHECK Constraint — VIEWER, OPERATOR, APPROVER, ADMIN
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "Role CHECK constraint on user_identity_map:"
grep -A2 "chk_role\|CHECK.*role.*IN" "$MIGRATION" 2>/dev/null | head -10
echo "---"
for ROLE in VIEWER OPERATOR APPROVER ADMIN; do
  FOUND=$(grep -c "$ROLE" "$MIGRATION" 2>/dev/null || echo 0)
  echo "$ROLE: $FOUND occurrence(s)"
done
2>&1 | tee $EVIDENCE_DIR/VF-13-3.txt
```
**PASS if:** CHECK constraint on `role` column includes all 4 values: VIEWER, OPERATOR, APPROVER, ADMIN.

**Gate VF-13:** All 3 checks pass. User identity standardization matches spec S3.2/GAP-C2.

---

## Verification Family 14 — Migration Rollbacks (GAP-M11)

### VF-14.1: 004_chat_canonical_store_rollback.sql Exists and Drops All 9 Tables
```bash
ROLLBACK_004=$(find /home/zaks/zakops-agent-api -name "*004*rollback*" -name "*.sql" 2>/dev/null | head -1)
if [ -z "$ROLLBACK_004" ]; then
  ROLLBACK_004=$(find /home/zaks/zakops-agent-api -name "*rollback*004*" -name "*.sql" 2>/dev/null | head -1)
fi
echo "File: $ROLLBACK_004"
echo "---"
if [ -n "$ROLLBACK_004" ]; then
  echo "DROP statements:"
  grep -in "DROP" "$ROLLBACK_004" 2>/dev/null | head -15
  echo "---"
  DROP_COUNT=$(grep -ci "DROP TABLE\|DROP VIEW\|DROP FUNCTION" "$ROLLBACK_004" 2>/dev/null || echo 0)
  echo "Total DROP statements: $DROP_COUNT"
  echo "---"
  echo "schema_migrations cleanup:"
  grep -in "schema_migrations\|DELETE.*FROM.*schema" "$ROLLBACK_004" 2>/dev/null | head -5
else
  echo "Rollback file NOT FOUND"
  echo "Searching alternative locations:"
  find /home/zaks/zakops-agent-api -name "*rollback*" -name "*.sql" 2>/dev/null
fi
2>&1 | tee $EVIDENCE_DIR/VF-14-1.txt
```
**PASS if:** Rollback file exists and drops all 9 tables + functions + view. Deletes from schema_migrations.

### VF-14.2: 030_partition_automation_rollback.sql Exists
```bash
ROLLBACK_030=$(find /home/zaks/zakops-agent-api -name "*030*rollback*" -o -name "*partition*rollback*" 2>/dev/null | grep ".sql" | head -1)
echo "File: $ROLLBACK_030"
if [ -n "$ROLLBACK_030" ]; then
  cat "$ROLLBACK_030" 2>/dev/null | head -30
else
  echo "NOT FOUND"
  echo "Searching for any partition-related rollback:"
  find /home/zaks/zakops-agent-api -name "*rollback*" -name "*.sql" 2>/dev/null
  echo "---"
  echo "Note: Partition automation may be handled within migration 004 rollback (VF-14.1)"
  echo "Checking 004 rollback for partition cleanup:"
  ROLLBACK_004=$(find /home/zaks/zakops-agent-api -name "*004*rollback*" -name "*.sql" 2>/dev/null | head -1)
  grep -in "partition\|create_monthly" "$ROLLBACK_004" 2>/dev/null | head -5
fi
2>&1 | tee $EVIDENCE_DIR/VF-14-2.txt
```
**PASS if:** A partition automation rollback exists (either standalone or within 004 rollback that drops `create_monthly_partitions()` function).

### VF-14.3: Rollbacks Delete from schema_migrations
```bash
echo "Checking all rollback files for schema_migrations cleanup:"
find /home/zaks/zakops-agent-api -name "*rollback*" -name "*.sql" 2>/dev/null | while read F; do
  HAS_CLEANUP=$(grep -c "schema_migrations" "$F" 2>/dev/null || echo 0)
  echo "$F: schema_migrations references = $HAS_CLEANUP"
done
echo "---"
ROLLBACK_028=$(find /home/zaks/zakops-backend -name "*028*rollback*" -o -name "*deal_brain*rollback*" 2>/dev/null | grep ".sql" | head -1)
echo "028 rollback: $ROLLBACK_028"
if [ -n "$ROLLBACK_028" ]; then
  grep -n "schema_migrations" "$ROLLBACK_028" 2>/dev/null | head -5
fi
2>&1 | tee $EVIDENCE_DIR/VF-14-3.txt
```
**PASS if:** Rollback files include `DELETE FROM schema_migrations WHERE version = '...'`.

**Gate VF-14:** All 3 checks pass. Migration rollbacks are complete and reversible per spec GAP-M11.

---

## Verification Family 15 — Graph.py Integration (S3.8 Write Path)

### VF-15.1: asyncio.create_task() for Brain Extraction (Fire-and-Forget)
```bash
GRAPH_FILE=$(find /home/zaks/zakops-agent-api -name "graph.py" -path "*/langgraph/*" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GRAPH_FILE" ]; then
  GRAPH_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "graph.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
echo "File: $GRAPH_FILE"
echo "---"
echo "asyncio.create_task calls:"
grep -n "create_task\|asyncio.*create_task" "$GRAPH_FILE" 2>/dev/null | head -15
echo "---"
echo "Brain extraction references:"
grep -n "brain\|extract\|enqueue" "$GRAPH_FILE" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/VF-15-1.txt
```
**PASS if:** `asyncio.create_task()` is used for brain extraction (fire-and-forget pattern).

### VF-15.2: asyncio.create_task() for Snapshot Writing
```bash
GRAPH_FILE=$(find /home/zaks/zakops-agent-api -name "graph.py" -path "*/langgraph/*" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GRAPH_FILE" ]; then
  GRAPH_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "graph.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
grep -n "snapshot\|turn_snapshot\|SnapshotWriter" "$GRAPH_FILE" 2>/dev/null | head -10
echo "---"
echo "create_task + snapshot context:"
grep -B2 -A2 "create_task.*snapshot\|snapshot.*create_task" "$GRAPH_FILE" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/VF-15-2.txt
```
**PASS if:** Snapshot writing uses `asyncio.create_task()` (non-blocking).

### VF-15.3: asyncio.create_task() for Cost Recording
```bash
GRAPH_FILE=$(find /home/zaks/zakops-agent-api -name "graph.py" -path "*/langgraph/*" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GRAPH_FILE" ]; then
  GRAPH_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "graph.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
grep -n "cost\|CostLedger\|cost_ledger\|record_cost" "$GRAPH_FILE" 2>/dev/null | head -10
echo "---"
echo "create_task + cost context:"
grep -B2 -A2 "create_task.*cost\|cost.*create_task" "$GRAPH_FILE" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/VF-15-3.txt
```
**PASS if:** Cost recording uses `asyncio.create_task()` (non-blocking).

### VF-15.4: No Direct Await for Enrichment Tasks (Must Not Block User Response)
```bash
GRAPH_FILE=$(find /home/zaks/zakops-agent-api -name "graph.py" -path "*/langgraph/*" -not -path "*/.venv/*" 2>/dev/null | head -1)
if [ -z "$GRAPH_FILE" ]; then
  GRAPH_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "graph.py" -not -path "*/.venv/*" 2>/dev/null | head -1)
fi
echo "Looking for blocking awaits on enrichment tasks:"
echo "Direct await on brain/snapshot/cost (should NOT exist in response path):"
grep -n "await.*brain_extract\|await.*snapshot_write\|await.*cost_record\|await.*enqueue_brain" "$GRAPH_FILE" 2>/dev/null | head -10
echo "---"
echo "Total create_task usage (should be >= 3 for brain/snapshot/cost):"
TASK_COUNT=$(grep -c "create_task" "$GRAPH_FILE" 2>/dev/null || echo 0)
echo "create_task count: $TASK_COUNT"
2>&1 | tee $EVIDENCE_DIR/VF-15-4.txt
```
**PASS if:** No direct `await` on enrichment tasks in the response path. All enrichment uses `create_task()`.

**Gate VF-15:** All 4 checks pass. Graph.py integration uses fire-and-forget pattern for all non-blocking enrichment per spec S3.8.

---

## 4. Cross-Consistency Checks

### XC-1: Migration 004 Table Count Matches Spec S3.3 (9 Tables)
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
TABLE_COUNT=$(grep -ci "CREATE TABLE" "$MIGRATION" 2>/dev/null || echo 0)
echo "CREATE TABLE count in migration 004: $TABLE_COUNT"
echo "Spec S3.3 expects: 9 tables"
echo "---"
echo "Table names found:"
grep -io "CREATE TABLE.*IF NOT EXISTS.*[a-z_]*\|CREATE TABLE.*[a-z_]*" "$MIGRATION" 2>/dev/null | head -15
2>&1 | tee $EVIDENCE_DIR/XC-1.txt
```
**PASS if:** Table count = 9 (user_identity_map, chat_threads, chat_messages, thread_ownership, session_summaries, turn_snapshots, cost_ledger, deal_budgets, cross_db_outbox). Partition sub-tables (turn_snapshots_default, cost_ledger_default) do not count.

### XC-2: ChatRepository Methods Cover ALL Spec S3.6 Operations
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
echo "All public methods in ChatRepository:"
grep -n "async def \|def " "$REPO_FILE" 2>/dev/null | grep -v "^.*#\|^.*_internal\|^.*__" | head -20
echo "---"
echo "Spec S3.6 required methods:"
METHODS="create_thread get_thread list_threads update_thread soft_delete_thread hard_delete_thread restore_thread add_message get_messages get_thread_for_llm validate_deal_reference enqueue_brain_extraction"
for M in $METHODS; do
  FOUND=$(grep -c "def $M" "$REPO_FILE" 2>/dev/null || echo 0)
  echo "  $M: $FOUND"
done
2>&1 | tee $EVIDENCE_DIR/XC-2.txt
```
**PASS if:** >= 10 of 12 spec methods are implemented.

### XC-3: Chatbot.py Endpoints Match Spec S3.5 (5 Endpoint Categories)
```bash
CHATBOT_FILE=$(find /home/zaks/zakops-agent-api -name "chatbot.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
echo "All route definitions:"
grep -n "@.*get\|@.*post\|@.*patch\|@.*delete\|@.*put\|@.*router" "$CHATBOT_FILE" 2>/dev/null | head -20
echo "---"
echo "Endpoint coverage:"
echo "  GET /threads (list): $(grep -c 'list_threads\|get.*threads.*user' "$CHATBOT_FILE" 2>/dev/null || echo 0)"
echo "  GET /threads/{id}/messages: $(grep -c 'messages\|get_messages' "$CHATBOT_FILE" 2>/dev/null || echo 0)"
echo "  POST /threads (create): $(grep -c 'create_thread\|post.*thread' "$CHATBOT_FILE" 2>/dev/null || echo 0)"
echo "  PATCH /threads/{id}: $(grep -c 'update_thread\|patch.*thread' "$CHATBOT_FILE" 2>/dev/null || echo 0)"
echo "  DELETE /threads/{id}: $(grep -c 'delete.*thread\|soft_delete\|hard_delete' "$CHATBOT_FILE" 2>/dev/null || echo 0)"
2>&1 | tee $EVIDENCE_DIR/XC-3.txt
```
**PASS if:** All 5 endpoint categories have >= 1 reference each.

### XC-4: Deal Brain Migration 028 Column Count Matches Spec S4.2
```bash
MIGRATION_028=$(find /home/zaks/zakops-backend -path "*/migrations/*028*" -name "*.sql" 2>/dev/null | head -1)
if [ -z "$MIGRATION_028" ]; then
  MIGRATION_028=$(find /home/zaks/zakops-backend -name "*deal_brain*" -name "*.sql" 2>/dev/null | head -1)
fi
echo "deal_brain table columns:"
python3 -c "
import re
with open('$MIGRATION_028', 'r') as f:
    content = f.read()
# Find deal_brain CREATE TABLE block
match = re.search(r'CREATE TABLE.*deal_brain\s*\((.*?)\);', content, re.DOTALL | re.IGNORECASE)
if match:
    body = match.group(1)
    # Count column definitions (lines with a type keyword)
    cols = [l.strip() for l in body.split('\n') if l.strip() and not l.strip().startswith('--') and not l.strip().startswith('CONSTRAINT') and any(kw in l.upper() for kw in ['VARCHAR', 'TEXT', 'INTEGER', 'FLOAT', 'JSONB', 'BOOLEAN', 'TIMESTAMPTZ', 'NUMERIC', 'SERIAL'])]
    print(f'Column count: {len(cols)}')
    for c in cols:
        # Extract column name
        name = c.strip().split()[0] if c.strip() else ''
        print(f'  {name}')
else:
    print('deal_brain CREATE TABLE not found')
" 2>&1 | tee $EVIDENCE_DIR/XC-4.txt
```
**PASS if:** deal_brain has >= 18 columns (spec defines: deal_id, version, summary, summary_model, summary_confidence, facts, risks, decisions, assumptions, open_items, ghost_facts, stage_notes, momentum_score, momentum_updated_at, momentum_components, entities, email_facts_count, last_email_ingestion, last_summarized_turn, last_summarized_at, last_fact_extraction, contradiction_count, created_at, updated_at = 24 columns).

### XC-5: SSE Event Types Cover Spec S3.10 Catalog
```bash
echo "Spec S3.10 defines 14 event types. Checking implementation coverage:"
SPEC_EVENTS="message_chunk message_complete thread_updated brain_updated summary_generated injection_alert legal_hold_set budget_warning cost_update ghost_knowledge momentum_update tool_execution approval_required error"
AGENT_API_DIR="/home/zaks/zakops-agent-api/apps/agent-api"
for EVENT in $SPEC_EVENTS; do
  COUNT=$(grep -r "$EVENT" "$AGENT_API_DIR" 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | grep -c "" 2>/dev/null || echo 0)
  echo "$EVENT: $COUNT reference(s)"
done
2>&1 | tee $EVIDENCE_DIR/XC-5.txt
```
**PASS if:** >= 10 of 14 spec event types have references in the agent-api codebase.

---

## 5. Stress Tests

### ST-1: No Raw httpx in Agent-API Services (BackendClient Monopoly)
```bash
echo "Searching for raw httpx usage in agent-api services (should use BackendClient):"
RAW_HTTPX=$(grep -rn "import httpx\|httpx.AsyncClient\|httpx.Client" /home/zaks/zakops-agent-api/apps/agent-api/app/services/ 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | grep -v "backend_client" || echo "NONE FOUND")
echo "$RAW_HTTPX"
echo "---"
echo "BackendClient usage:"
grep -rn "BackendClient\|backend_client" /home/zaks/zakops-agent-api/apps/agent-api/app/services/ 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | head -10
2>&1 | tee $EVIDENCE_DIR/ST-1.txt
```
**PASS if:** No raw `httpx` imports in service files (except `backend_client.py` itself). All HTTP calls go through BackendClient.

### ST-2: All COL-V2 Services Have Module-Level Singleton Instances
```bash
echo "Checking for module-level singleton pattern in COL-V2 services:"
COL_SERVICES="chat_repository.py injection_guard.py canary_tokens.py sse_events.py snapshot_writer.py cost_writer.py"
for SVC in $COL_SERVICES; do
  FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "$SVC" -not -path "*/.venv/*" 2>/dev/null | head -1)
  if [ -n "$FILE" ]; then
    # Look for module-level instance (variable = ClassName())
    SINGLETON=$(grep -n "^[a-z_].*=.*()$\|^[a-z_].*= .*Service()\|^[a-z_].*= .*Repository()\|^[a-z_].*= .*Guard()\|^[a-z_].*= .*Manager()" "$FILE" 2>/dev/null | head -3)
    echo "$SVC: ${SINGLETON:-NO SINGLETON FOUND}"
  else
    echo "$SVC: FILE NOT FOUND"
  fi
done
2>&1 | tee $EVIDENCE_DIR/ST-2.txt
```
**PASS if:** Majority of implemented COL-V2 services have module-level singleton instances.

### ST-3: All Service Files Have COL-V2 Spec Section Docstrings
```bash
echo "Checking for spec section references in service docstrings:"
COL_FILES=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "chat_repository.py" -o -name "injection_guard.py" -o -name "canary_tokens.py" -o -name "sse_events.py" -o -name "snapshot_writer.py" 2>/dev/null | grep -v ".venv" | grep -v "node_modules")
for FILE in $COL_FILES; do
  if [ -n "$FILE" ]; then
    DOCSTRING=$(head -20 "$FILE" 2>/dev/null | grep -i "COL\|Section\|S3\|S4\|S7\|S10\|spec" | head -3)
    echo "$(basename $FILE): ${DOCSTRING:-NO SPEC REFERENCE}"
  fi
done
echo "---"
echo "Backend services:"
BACKEND_FILES=$(find /home/zaks/zakops-backend/src/core/agent -name "*.py" -not -path "*/.venv/*" 2>/dev/null)
for FILE in $BACKEND_FILES; do
  DOCSTRING=$(head -10 "$FILE" 2>/dev/null | grep -i "COL\|Section\|S4\|S20\|spec" | head -1)
  if [ -n "$DOCSTRING" ]; then
    echo "$(basename $FILE): $DOCSTRING"
  fi
done
2>&1 | tee $EVIDENCE_DIR/ST-3.txt
```
**PASS if:** Majority of service files reference their spec section.

### ST-4: Partition Automation Function Is Idempotent (IF NOT EXISTS Check)
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api -path "*/migrations/*004*" -name "*.sql" 2>/dev/null | head -1)
echo "create_monthly_partitions function:"
grep -A30 "CREATE.*FUNCTION.*create_monthly_partitions\|create_monthly_partitions" "$MIGRATION" 2>/dev/null | head -35
echo "---"
echo "IF NOT EXISTS / idempotency check:"
grep -n "IF NOT EXISTS\|pg_class\|relname" "$MIGRATION" 2>/dev/null | head -10
2>&1 | tee $EVIDENCE_DIR/ST-4.txt
```
**PASS if:** `create_monthly_partitions()` function includes `IF NOT EXISTS` check before creating partitions.

### ST-5: Legal Hold Blocks BOTH Soft and Hard Delete in ChatRepository
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api -name "chat_repository.py" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -1)
echo "Legal hold checks in delete methods:"
echo "=== soft_delete_thread ==="
python3 -c "
import re
with open('$REPO_FILE', 'r') as f:
    content = f.read()
for method in ['soft_delete_thread', 'hard_delete_thread']:
    match = re.search(rf'(async )?def {method}.*?(?=\n    (async )?def |\nclass |\Z)', content, re.DOTALL)
    if match:
        body = match.group(0)
        has_legal = 'legal_hold' in body
        has_block = '409' in body or 'conflict' in body.lower() or 'raise' in body.lower()
        print(f'{method}: legal_hold check={has_legal}, block mechanism={has_block}')
    else:
        print(f'{method}: METHOD NOT FOUND')
" 2>&1 | tee $EVIDENCE_DIR/ST-5.txt
```
**PASS if:** BOTH `soft_delete_thread()` and `hard_delete_thread()` check `legal_hold` and block when true.

---

## 6. Remediation Protocol

When a verification gate reports FAIL:

1. **Read the evidence** file in `$EVIDENCE_DIR`
2. **Classify** the failure:
   - `MISSING_FIX` — Spec requirement not implemented
   - `REGRESSION` — Was working, now broken
   - `SCOPE_GAP` — Implementation exists but in unexpected location
   - `FALSE_POSITIVE` — Check is incorrect or outdated
   - `PARTIAL` — Partially implemented, missing elements
3. **Apply fix** following original architectural constraints
4. **Re-run** the specific VF/XC/ST gate
5. **Run** `make validate-local` to ensure no regressions
6. **Record** remediation in completion report with before/after evidence

**Remediation Guardrails:**
- Do not redesign — fix the specific gap
- Do not modify generated files (`.generated.ts`, `_models.py`)
- Do not change migration files that have already been applied
- Run `make sync-all-types` if any API boundary changes
- Fix CRLF on any new `.sh` files: `sed -i 's/\r$//'`
- Fix ownership on new files: `chown zaks:zaks`

---

## 7. Enhancement Opportunities

### ENH-1: Migration Test Harness
Add a test that applies migration 004 + 028 to a fresh database and verifies all tables, constraints, and indexes are created correctly.

### ENH-2: ChatRepository Integration Tests
Create integration tests that exercise all 12 ChatRepository methods against a real (test) database.

### ENH-3: SSE Event Type Registry
Create a typed enum or registry of all SSE event types so new events are compile-time checked.

### ENH-4: Injection Guard Pattern Hot-Reload
Allow INJECTION_PATTERNS to be loaded from a config file, enabling pattern updates without code deployment.

### ENH-5: Ghost Knowledge Detector Unit Tests
Add property-based tests for ghost knowledge detection covering edge cases (empty facts, unicode, extremely long inputs).

### ENH-6: Momentum Score Dashboard Widget
Create a reusable MomentumBadge component that renders the color-coded momentum score with trend arrow.

### ENH-7: Canary Token Rotation
Implement periodic canary token rotation to prevent adversarial learning of token patterns.

### ENH-8: Legal Hold Audit Trail
Add a `legal_hold_history` table tracking who set/removed legal holds and when, for compliance auditability.

### ENH-9: Cross-Consistency Automated Gate
Create a CI-runnable script that performs all 5 XC checks automatically as part of `make validate-local`.

### ENH-10: Partition Health Monitoring Endpoint
Add a `/health/partitions` admin endpoint that returns partition status, DEFAULT row counts, and future partition coverage.

---

## 8. Scorecard Template

```
QA-COL-DEEP-VERIFY-001A — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):           [ PASS / FAIL ]
  PF-2 (tsc --noEmit):             [ PASS / FAIL ]
  PF-3 (agent-api health):         [ PASS / FAIL / SKIP ]
  PF-4 (evidence directory):       [ PASS / FAIL ]
  PF-5 (spec line count):          [ PASS / FAIL ]

Verification Gates:
  VF-01 (Migration 004 Schema):    __ / 5 gates PASS
  VF-02 (ChatRepository):          __ / 6 gates PASS
  VF-03 (Chatbot API):             __ / 5 gates PASS
  VF-04 (Middleware Routing):      __ / 3 gates PASS
  VF-05 (Migration 028 Brain):     __ / 5 gates PASS
  VF-06 (Brain Service):           __ / 5 gates PASS
  VF-07 (Ghost Knowledge):         __ / 4 gates PASS
  VF-08 (Momentum Calculator):     __ / 4 gates PASS
  VF-09 (Injection Guard):         __ / 4 gates PASS
  VF-10 (Canary Tokens):           __ / 3 gates PASS
  VF-11 (Session Tracker):         __ / 2 gates PASS
  VF-12 (SSE Events):              __ / 3 gates PASS
  VF-13 (User Identity Map):       __ / 3 gates PASS
  VF-14 (Migration Rollbacks):     __ / 3 gates PASS
  VF-15 (Graph.py Integration):    __ / 4 gates PASS

Cross-Consistency:
  XC-1 (table count):              [ PASS / FAIL ]
  XC-2 (ChatRepository coverage):  [ PASS / FAIL ]
  XC-3 (endpoint coverage):        [ PASS / FAIL ]
  XC-4 (brain column count):       [ PASS / FAIL ]
  XC-5 (SSE event coverage):       [ PASS / FAIL ]

Stress Tests:
  ST-1 (no raw httpx):             [ PASS / FAIL ]
  ST-2 (singleton instances):      [ PASS / FAIL ]
  ST-3 (spec docstrings):          [ PASS / FAIL ]
  ST-4 (partition idempotency):    [ PASS / FAIL ]
  ST-5 (legal hold both deletes):  [ PASS / FAIL ]

Total: __ / 69 gates PASS, __ FAIL, __ SKIP, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **Do not build new features** — this is a QA verification mission. Discovery and verification only.
2. **Remediate, don't redesign** — fix specific gaps found, do not refactor implementations.
3. **Evidence-based** — every PASS requires tee'd output in `$EVIDENCE_DIR`. No subjective judgments.
4. **Services-down accommodation** — if agent-api or backend is unreachable, live verification gates (PF-3, VF-15 runtime checks) become SKIP, not FAIL. Code-level checks proceed normally.
5. **All bash evidence commands use `tee`** to the evidence directory. Evidence must be reproducible.
6. **Run `make validate-local`** after any remediation to ensure no regressions.
7. **Do not modify generated files** (`*.generated.ts`, `*_models.py`). If a generated file is wrong, fix the source and re-run the generator.
8. **Do not modify applied migrations** — if a migration gap is found, create a new migration to fix it.
9. **Port 8090 is DECOMMISSIONED** — never reference or use.
10. **WSL safety** — strip CRLF from any new `.sh` files, fix ownership on files created under `/home/zaks/`.

---

## 10. Stop Condition

Stop when all 69 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE with documented rationale), all remediations are applied and re-verified, `make validate-local` passes, the scorecard is complete, and changes are recorded in `/home/zaks/bookkeeping/CHANGES.md`.

Do NOT proceed to QA-COL-DEEP-VERIFY-001B (Sections S5, S6, S8, S9, S11-S15) — that is a separate mission.

---

*End of Mission Prompt — QA-COL-DEEP-VERIFY-001A*
