# QA MISSION: QA-LANGSMITH-SHADOW-PILOT-EXEC-VERIFY-001
## Deep Verification — Shadow-Mode Pilot Launch & Bug Fix
## Date: 2026-02-14
## Classification: QA Verification & Remediation
## Prerequisite: LANGSMITH-SHADOW-PILOT-001 complete (5 phases, 10 AC, 13 evidence files)
## Auditor: Claude Code (Opus 4.6)

---

## 1. Mission Objective

This is an **independent verification** of LANGSMITH-SHADOW-PILOT-001. The completion report claims 10/10 AC PASS across 5 phases. The mission was primarily operational (environment cleanup, seed test, documentation creation) but also included a **real bug fix** discovered during execution:

- **Bug:** Quarantine POST dedup path returned raw UUID objects instead of strings, causing 500 ResponseValidationError
- **Fix:** Added `id::text` cast to two SELECT queries in `main.py` (dedup SELECT at ~line 1566 and race-condition SELECT at ~line 1610)
- **Bonus fix:** Removed a stale `=== Contract ===` syntax error artifact from `security.py`

This QA will:

1. **Verify the bug fix is correct and complete** — confirm all quarantine SELECT queries return `id::text`, not raw UUID. Check for similar UUID serialization issues in other endpoints.
2. **Verify the documentation deliverables** — pilot tracker has all required sections with correct formulas, decision packet has all 6 sections with correct criteria.
3. **Verify the database cleanup was safe** — confirm FK-safe deletion order, no orphaned data, no damage to unrelated tables.
4. **Verify seed test evidence** — confirm 201/200/isolation/correlation evidence is internally consistent.
5. **Cross-check evidence file line numbers against current source** — confirm the code hasn't drifted since evidence was captured.
6. **Hunt for residual issues** — UUID serialization bugs elsewhere, missing `id::text` casts, stale artifacts in other files.

**What this is NOT**: This is not a build mission. No new features. Minimal fixes only for FAIL gates.

### Source Artifacts

| Artifact | Path | Key Content |
|----------|------|-------------|
| Completion Report | `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.COMPLETION.md` | 10 AC, 5 phases, bug fix |
| Mission Prompt | `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.md` | 514 lines, 10 AC, 5 phases |
| Pilot Tracker | `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md` | 207 lines |
| Decision Packet | `/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md` | 173 lines |
| Evidence Directory | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/` | 8 evidence files |
| Backend main.py | `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Bug fix: `id::text` cast |
| Security Module | `/home/zaks/zakops-backend/src/api/shared/security.py` | Artifact removal |
| Injection Contract | `/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md` | Endpoint specification |

### Evidence Directory

```
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-shadow-pilot-exec-verify-001
```

---

## 2. Pre-Flight

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-shadow-pilot-exec-verify-001
mkdir -p "$EVIDENCE_DIR"
```

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee "$EVIDENCE_DIR/PF-1-validate-local.txt"
echo "EXIT:$?"
```
**PASS if:** Exit 0. If not, stop.

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
**PASS if:** Exit 0, JSON healthy. If down, live gates (VF-05) become SKIP(services-down).

### PF-4: Source Artifacts Exist
```bash
for f in \
  "/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.COMPLETION.md" \
  "/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md" \
  "/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md" \
  "/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-01-seed-injection.txt"; do
  test -f "$f" && echo "EXISTS: $f" || echo "MISSING: $f"
done 2>&1 | tee "$EVIDENCE_DIR/PF-4-artifacts.txt"
```
**PASS if:** All 4 files exist.

### PF-5: Evidence Directory Ready
```bash
test -d "$EVIDENCE_DIR" && echo "EVIDENCE_DIR ready" | tee "$EVIDENCE_DIR/PF-5-dir-ready.txt"
ls -la "$EVIDENCE_DIR/" | tee -a "$EVIDENCE_DIR/PF-5-dir-ready.txt"
```
**PASS if:** Directory exists and is writable.

---

## 3. Verification Families

### VF-01 — Bug Fix: `id::text` Cast in Dedup SELECT — 5 checks

**Context:** The completion report documents a 500 ResponseValidationError caused by raw UUID objects in the dedup path. The fix added `id::text` to two SELECT queries at lines ~1566 and ~1610. This VF verifies the fix is complete and no similar bugs exist elsewhere.

#### VF-01.1: Dedup SELECT at ~line 1566 uses `id::text`
```bash
grep -n "id::text" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-1.txt"
ID_TEXT_COUNT=$(grep -c "id::text" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>/dev/null) || ID_TEXT_COUNT=0
echo "ID_TEXT_CAST_COUNT=$ID_TEXT_COUNT" | tee -a "$EVIDENCE_DIR/VF-01-1.txt"
```
**PASS if:** `id::text` appears in ALL quarantine SELECT queries (not just the two fixed ones). Expect >= 4 occurrences (list query, dedup query, INSERT RETURNING, race-condition query).

#### VF-01.2: Dedup SELECT context — full query at ~line 1566
```bash
sed -n '1560,1580p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-2.txt"
```
**PASS if:** The SELECT query includes `q.id::text` in the column list (not raw `q.id`).

#### VF-01.3: Race-condition SELECT context — full query at ~line 1610
```bash
sed -n '1604,1625p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-3.txt"
```
**PASS if:** The SELECT query includes `q.id::text` in the column list (not raw `q.id`).

#### VF-01.4: INSERT RETURNING clause uses `id::text`
```bash
grep -n "RETURNING" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "quarantine" | head -5 | tee "$EVIDENCE_DIR/VF-01-4.txt"
sed -n '1585,1600p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/VF-01-4.txt"
```
**PASS if:** `RETURNING id::text, ...` — the INSERT also returns text, not raw UUID.

#### VF-01.5: List quarantine SELECT uses `id::text`
```bash
sed -n '1420,1460p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee "$EVIDENCE_DIR/VF-01-5.txt"
```
**PASS if:** The GET /api/quarantine list query also uses `q.id::text`. If the list query uses raw `q.id`, this is a latent bug that would surface when the list endpoint is called.

**Gate VF-01:** All 5 checks pass. UUID serialization is consistent across all quarantine queries.

---

### VF-02 — Bug Fix: security.py Artifact Removal — 3 checks

**Context:** The completion report says a stale `=== Contract ===` syntax error artifact was removed from `security.py` line 233.

#### VF-02.1: No `=== Contract ===` artifact in security.py
```bash
ARTIFACTS=$(grep -c "=== Contract\|=== Code\|=== Gap" /home/zaks/zakops-backend/src/api/shared/security.py 2>/dev/null) || ARTIFACTS=0
echo "STALE_ARTIFACTS=$ARTIFACTS" | tee "$EVIDENCE_DIR/VF-02-1.txt"
grep -n "===.*===" /home/zaks/zakops-backend/src/api/shared/security.py 2>&1 | tee -a "$EVIDENCE_DIR/VF-02-1.txt"
```
**PASS if:** STALE_ARTIFACTS is 0. No QA evidence markers left in production code.

#### VF-02.2: security.py is syntactically valid Python
```bash
python3 -c "import py_compile; py_compile.compile('/home/zaks/zakops-backend/src/api/shared/security.py', doraise=True); print('SYNTAX=VALID')" 2>&1 | tee "$EVIDENCE_DIR/VF-02-2.txt"
```
**PASS if:** SYNTAX=VALID — no SyntaxError.

#### VF-02.3: No stale QA artifacts in other backend Python files
```bash
HITS=$(grep -rn "=== Contract\|=== Code\|=== Gap\|=== Evidence" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v __pycache__ | grep "\.py:" | wc -l) || HITS=0
echo "STALE_QA_ARTIFACTS_IN_BACKEND=$HITS" | tee "$EVIDENCE_DIR/VF-02-3.txt"
grep -rn "=== Contract\|=== Code\|=== Gap\|=== Evidence" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v __pycache__ | grep "\.py:" | tee -a "$EVIDENCE_DIR/VF-02-3.txt"
```
**PASS if:** STALE_QA_ARTIFACTS_IN_BACKEND is 0. If > 0, classify each hit: active code vs QA residue.

**Gate VF-02:** All 3 checks pass. Stale artifact removed, no similar artifacts elsewhere.

---

### VF-03 — AC-1: Environment Cleanup Verified — 4 checks

**Context:** Completion report claims FK-safe cleanup of 58 deals, 1 quarantine item, 159 deal_events, 1 deal_alias, 21 outbox entries. Evidence in `P0-03-cleanup-transaction.txt`.

#### VF-03.1: Cleanup transaction evidence is internally consistent
```bash
cat /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P0-03-cleanup-transaction.txt 2>&1 | tee "$EVIDENCE_DIR/VF-03-1.txt"
echo "=== Consistency check ===" | tee -a "$EVIDENCE_DIR/VF-03-1.txt"
# Verify pre-delete counts match reported numbers
python3 -c "
evidence = open('/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P0-03-cleanup-transaction.txt').read()
checks = []
checks.append(('deals=58', 'deals' in evidence and '58' in evidence))
checks.append(('quarantine=1', 'quarantine_items' in evidence and '| 1' in evidence.split('quarantine_items')[1][:20] if 'quarantine_items' in evidence else False))
checks.append(('deal_events=159', 'deal_events' in evidence and '159' in evidence))
checks.append(('outbox=21', 'outbox' in evidence and '21' in evidence))
checks.append(('post-delete=0', 'deals' in evidence and '| 0' in evidence.split('POST-DELETE')[1] if 'POST-DELETE' in evidence else False))
checks.append(('COMMIT present', 'COMMIT' in evidence))
for name, result in checks:
    print(f'{name}: {\"PASS\" if result else \"FAIL\"}')" 2>&1 | tee -a "$EVIDENCE_DIR/VF-03-1.txt"
```
**PASS if:** All consistency checks pass — pre-delete counts match completion report, post-delete counts are 0, transaction committed.

#### VF-03.2: Current database state is clean
```bash
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "
SELECT
  (SELECT COUNT(*) FROM zakops.quarantine_items WHERE source_type IN ('langsmith_shadow', 'langsmith_production')) AS stale_quarantine,
  (SELECT COUNT(*) FROM zakops.quarantine_items WHERE message_id LIKE 'seed-test%') AS leftover_seeds;
" 2>&1 | tee "$EVIDENCE_DIR/VF-03-2.txt"
```
**PASS if:** stale_quarantine is 0 AND leftover_seeds is 0. No test artifacts or stale data remain. **If services are down:** SKIP(services-down).

#### VF-03.3: Historical artifacts preserved
```bash
cat /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P0-04-artifacts-intact.txt 2>&1 | tee "$EVIDENCE_DIR/VF-03-3.txt"
MISSING=$(grep -c "MISSING" /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P0-04-artifacts-intact.txt 2>/dev/null) || MISSING=0
echo "MISSING_ARTIFACTS=$MISSING" | tee -a "$EVIDENCE_DIR/VF-03-3.txt"
```
**PASS if:** MISSING_ARTIFACTS is 0 — all 10 historical artifacts confirmed intact.

#### VF-03.4: FK-safe deletion order in transaction
```bash
# The deletion order must respect foreign keys: children before parents
# Expected order: deal_transitions → deal_brain_history → deal_brain → deal_entity_graph →
#   deal_events → deal_aliases → deal_access → decision_outcomes → artifacts → email_threads →
#   quarantine_items → outbox → deals (last)
echo "=== Deletion order analysis ===" | tee "$EVIDENCE_DIR/VF-03-4.txt"
grep "DELETE" /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P0-03-cleanup-transaction.txt 2>&1 | tee -a "$EVIDENCE_DIR/VF-03-4.txt"
DEALS_LAST=$(tail -5 /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P0-03-cleanup-transaction.txt | grep -c "DELETE 58")
echo "DEALS_DELETED_LAST=$DEALS_LAST" | tee -a "$EVIDENCE_DIR/VF-03-4.txt"
```
**PASS if:** The `DELETE 58` (deals) is the last DELETE in the transaction — children were deleted before parents.

**Gate VF-03:** All 4 checks pass. Cleanup was safe, complete, and properly ordered.

---

### VF-04 — AC-2: Backend Health (PF-3 Closure) — 2 checks

**Context:** The previously-skipped PF-3 from QA-LANGSMITH-SHADOW-PILOT-VERIFY-001 was completed during this mission.

#### VF-04.1: Backend health returns healthy
```bash
curl -sf http://localhost:8091/health 2>&1 | python3 -m json.tool | tee "$EVIDENCE_DIR/VF-04-1.txt"
echo "EXIT:$?" | tee -a "$EVIDENCE_DIR/VF-04-1.txt"
```
**PASS if:** JSON response includes `"status":"healthy"` and database connection info. **If down:** SKIP(services-down).

#### VF-04.2: Evidence file P1-01 confirms health was verified during mission
```bash
# Check if the mission's own health evidence exists (even though we verified independently)
test -f "/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P1-01-backend-health.txt" && echo "EXISTS" || echo "MISSING"
# Note: P1-01 may not exist — the evidence directory shows it was claimed but file may have been lost
ls -la /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/ 2>&1 | tee "$EVIDENCE_DIR/VF-04-2.txt"
```
**INFO:** Document whether P1-01 evidence file exists. The completion report claims it does — verify.

**Gate VF-04:** VF-04.1 must PASS (or SKIP if services down). VF-04.2 is INFO.

---

### VF-05 — AC-3/AC-4/AC-5/AC-6: Seed Test Evidence — 6 checks

**Context:** The seed test exercised the full injection → dedup → isolation → cleanup loop. Evidence files P2-01 through P2-05 document the results.

#### VF-05.1: Seed injection returned 201 Created
```bash
cat /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-01-seed-injection.txt 2>&1 | tee "$EVIDENCE_DIR/VF-05-1.txt"
grep -c "201" /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-01-seed-injection.txt 2>/dev/null | tee -a "$EVIDENCE_DIR/VF-05-1.txt"
```
**PASS if:** Evidence shows HTTP_STATUS=201 and response includes the created item's ID.

#### VF-05.2: Dedup re-send returned 200 OK (not 201)
```bash
cat /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-02-seed-dedup.txt 2>&1 | tee "$EVIDENCE_DIR/VF-05-2.txt"
grep -c "200" /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-02-seed-dedup.txt 2>/dev/null | tee -a "$EVIDENCE_DIR/VF-05-2.txt"
```
**PASS if:** Evidence shows HTTP_STATUS=200. The same `message_id` produces a dedup hit.

#### VF-05.3: Isolation — seed appears under langsmith_shadow, absent under email_sync
```bash
cat /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-03-seed-isolation.txt 2>&1 | tee "$EVIDENCE_DIR/VF-05-3.txt"
echo "=== Checks ===" | tee -a "$EVIDENCE_DIR/VF-05-3.txt"
SHADOW_HIT=$(grep -c "seed-test-langsmith-shadow-001" /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-03-seed-isolation.txt 2>/dev/null) || SHADOW_HIT=0
EMPTY_EMAIL=$(grep -c '^\[\]$' /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-03-seed-isolation.txt 2>/dev/null) || EMPTY_EMAIL=0
echo "SHADOW_FILTER_HITS=$SHADOW_HIT" | tee -a "$EVIDENCE_DIR/VF-05-3.txt"
echo "EMAIL_FILTER_EMPTY=$EMPTY_EMAIL" | tee -a "$EVIDENCE_DIR/VF-05-3.txt"
```
**PASS if:** SHADOW_FILTER_HITS >= 1 AND EMAIL_FILTER_EMPTY >= 1.

#### VF-05.4: Item IDs are consistent across evidence files
```bash
echo "=== ID consistency ===" | tee "$EVIDENCE_DIR/VF-05-4.txt"
INJECTION_ID=$(python3 -c "import json; d=json.loads(open('/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-01-seed-injection.txt').readline()); print(d['id'])" 2>/dev/null)
DEDUP_ID=$(python3 -c "import json; d=json.loads(open('/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-02-seed-dedup.txt').readline()); print(d['id'])" 2>/dev/null)
echo "INJECTION_ID=$INJECTION_ID" | tee -a "$EVIDENCE_DIR/VF-05-4.txt"
echo "DEDUP_ID=$DEDUP_ID" | tee -a "$EVIDENCE_DIR/VF-05-4.txt"
if [ "$INJECTION_ID" = "$DEDUP_ID" ] && [ -n "$INJECTION_ID" ]; then
  echo "ID_MATCH=YES"
else
  echo "ID_MATCH=NO"
fi | tee -a "$EVIDENCE_DIR/VF-05-4.txt"
```
**PASS if:** ID_MATCH=YES — dedup returns the SAME item (same ID) as the original injection.

#### VF-05.5: IDs are strings (not raw UUID objects) — confirms bug fix worked
```bash
echo "=== UUID format check ===" | tee "$EVIDENCE_DIR/VF-05-5.txt"
python3 -c "
import json, re
with open('/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-01-seed-injection.txt') as f:
    line = f.readline()
    d = json.loads(line)
    id_val = d['id']
    print(f'id_value={id_val}')
    print(f'id_type={type(id_val).__name__}')
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    if uuid_pattern.match(str(id_val)):
        print('FORMAT=valid_uuid_string')
        print('VERDICT=PASS')
    else:
        print('FORMAT=not_uuid_string')
        print('VERDICT=FAIL')
" 2>&1 | tee -a "$EVIDENCE_DIR/VF-05-5.txt"
```
**PASS if:** The `id` field in the JSON response is a valid UUID string (not a raw Python UUID repr like `UUID('...')`).

#### VF-05.6: Seed cleanup complete — no leftover seed items
```bash
# Check current database for seed test leftovers
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "
SELECT COUNT(*) AS seed_items FROM zakops.quarantine_items WHERE message_id LIKE 'seed-test%';
" 2>&1 | tee "$EVIDENCE_DIR/VF-05-6.txt"
```
**PASS if:** seed_items is 0. **If services down:** Check P2-05 evidence file instead.

**Gate VF-05:** All 6 checks pass. Seed test proves the full loop works, dedup is consistent, IDs are strings (bug fixed), and cleanup was complete.

---

### VF-06 — AC-7: Pilot Tracker Completeness — 6 checks

**Context:** Completion report claims pilot tracker has 179 lines with all required sections.

#### VF-06.1: File exists with expected length
```bash
test -f "/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md" && echo "EXISTS" || echo "MISSING"
LINES=$(wc -l < /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || LINES=0
echo "LINE_COUNT=$LINES" | tee "$EVIDENCE_DIR/VF-06-1.txt"
```
**PASS if:** File exists and LINE_COUNT > 100.

#### VF-06.2: Contains measurement rules with TP/FP/Deferred definitions
```bash
grep -n "True Positive\|False Positive\|Deferred\|Precision.*Formula\|TP.*FP" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>&1 | tee "$EVIDENCE_DIR/VF-06-2.txt"
SECTIONS=$(grep -c "True Positive\|False Positive\|Deferred" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || SECTIONS=0
echo "MEASUREMENT_SECTIONS=$SECTIONS" | tee -a "$EVIDENCE_DIR/VF-06-2.txt"
```
**PASS if:** MEASUREMENT_SECTIONS >= 3 (TP, FP, and Deferred all defined).

#### VF-06.3: Contains precision formula
```bash
grep -n "Precision\s*=\s*TP\|TP.*FP\|TP + FP" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>&1 | tee "$EVIDENCE_DIR/VF-06-3.txt"
```
**PASS if:** Formula `Precision = TP / (TP + FP)` is present.

#### VF-06.4: Contains 7-day daily log table
```bash
grep -c "| [1-7] |" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null | tee "$EVIDENCE_DIR/VF-06-4.txt"
DAY_ROWS=$(grep -c "| [1-7] |" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || DAY_ROWS=0
echo "DAY_ROWS=$DAY_ROWS" | tee -a "$EVIDENCE_DIR/VF-06-4.txt"
```
**PASS if:** DAY_ROWS is 7 (one row per day).

#### VF-06.5: Contains dashboard workflow instructions
```bash
grep -n "localhost:3003\|quarantine\|Source Type\|dropdown\|Approve\|Reject" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>&1 | tee "$EVIDENCE_DIR/VF-06-5.txt"
STEPS=$(grep -c "Step\|step\|Navigate\|Select\|Review\|Click" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || STEPS=0
echo "WORKFLOW_STEPS=$STEPS" | tee -a "$EVIDENCE_DIR/VF-06-5.txt"
```
**PASS if:** WORKFLOW_STEPS >= 4 — step-by-step instructions for reviewing shadow items.

#### VF-06.6: Contains database verification queries
```bash
grep -c "SELECT\|FROM zakops\.\|GROUP BY\|WHERE source_type" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null | tee "$EVIDENCE_DIR/VF-06-6.txt"
SQL_COUNT=$(grep -c "SELECT" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || SQL_COUNT=0
echo "SQL_QUERIES=$SQL_COUNT" | tee -a "$EVIDENCE_DIR/VF-06-6.txt"
```
**PASS if:** SQL_QUERIES >= 3 (completion report claims 4 verification queries).

**Gate VF-06:** All 6 checks pass. Pilot tracker is complete and operator-ready.

---

### VF-07 — AC-8: Decision Packet Completeness — 5 checks

**Context:** Completion report claims decision packet has 155 lines with 6 sections.

#### VF-07.1: File exists with expected length
```bash
test -f "/home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md" && echo "EXISTS" || echo "MISSING"
LINES=$(wc -l < /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>/dev/null) || LINES=0
echo "LINE_COUNT=$LINES" | tee "$EVIDENCE_DIR/VF-07-1.txt"
```
**PASS if:** File exists and LINE_COUNT > 100.

#### VF-07.2: Contains all 6 sections
```bash
for section in "Section 1" "Section 2" "Section 3" "Section 4" "Section 5" "Section 6"; do
  grep -c "$section" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>/dev/null
done | tee "$EVIDENCE_DIR/VF-07-2.txt"
SECTION_COUNT=$(grep -c "^## Section" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>/dev/null) || SECTION_COUNT=0
echo "SECTION_COUNT=$SECTION_COUNT" | tee -a "$EVIDENCE_DIR/VF-07-2.txt"
```
**PASS if:** SECTION_COUNT is 6.

#### VF-07.3: Decision matrix contains GO LIVE / EXTEND / REFINE
```bash
grep -n "GO LIVE\|EXTEND\|REFINE" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>&1 | tee "$EVIDENCE_DIR/VF-07-3.txt"
OPTIONS=$(grep -c "GO LIVE\|EXTEND\|REFINE" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>/dev/null) || OPTIONS=0
echo "DECISION_OPTIONS=$OPTIONS" | tee -a "$EVIDENCE_DIR/VF-07-3.txt"
```
**PASS if:** DECISION_OPTIONS >= 3 — all three options documented.

#### VF-07.4: Precision criteria are correct (>= 80%, 70-80%, < 70%)
```bash
grep -n "80%\|70%\|>= 20\|>= 80\|< 70" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>&1 | tee "$EVIDENCE_DIR/VF-07-4.txt"
```
**PASS if:** GO LIVE requires >= 80%, EXTEND triggers at 70-80%, REFINE triggers at < 70%.

#### VF-07.5: Approval sign-off section exists
```bash
grep -n "Approval\|Sign-off\|Signature\|Decision Maker" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>&1 | tee "$EVIDENCE_DIR/VF-07-5.txt"
```
**PASS if:** Approval/sign-off section exists with name, date, and signature fields.

**Gate VF-07:** All 5 checks pass. Decision packet is complete with correct criteria.

---

### VF-08 — AC-9/AC-10: No Regressions & Bookkeeping — 3 checks

#### VF-08.1: `make validate-local` passes
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tail -5 | tee "$EVIDENCE_DIR/VF-08-1.txt"
echo "EXIT:$?" | tee -a "$EVIDENCE_DIR/VF-08-1.txt"
```
**PASS if:** Exit 0, "All local validations passed".

#### VF-08.2: CHANGES.md contains entry for this mission
```bash
grep -n "LANGSMITH-SHADOW-PILOT-001\|shadow.*pilot.*launch\|id::text\|seed test" /home/zaks/bookkeeping/CHANGES.md 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-08-2.txt"
ENTRIES=$(grep -c "LANGSMITH-SHADOW-PILOT-001" /home/zaks/bookkeeping/CHANGES.md 2>/dev/null) || ENTRIES=0
echo "CHANGES_ENTRIES=$ENTRIES" | tee -a "$EVIDENCE_DIR/VF-08-2.txt"
```
**PASS if:** CHANGES_ENTRIES >= 1.

#### VF-08.3: Completion report exists with 10/10 AC
```bash
grep "Status:.*COMPLETE\|10/10" /home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.COMPLETION.md 2>&1 | tee "$EVIDENCE_DIR/VF-08-3.txt"
AC_COUNT=$(grep -c "| AC-" /home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.COMPLETION.md 2>/dev/null) || AC_COUNT=0
echo "AC_COUNT=$AC_COUNT" | tee -a "$EVIDENCE_DIR/VF-08-3.txt"
```
**PASS if:** AC_COUNT is 10, status is COMPLETE.

**Gate VF-08:** All 3 checks pass.

---

### VF-09 — UUID Serialization Sweep (Beyond the Fix) — 3 checks

**Context:** The bug was a UUID-to-string serialization issue. This VF hunts for the SAME class of bug in other endpoints — if quarantine had it, other tables with UUID primary keys might too.

#### VF-09.1: Search for raw `q.id` (without ::text) in quarantine queries
```bash
# Find quarantine SELECT queries that return id WITHOUT ::text cast
grep -n "SELECT.*q\.id[^:]" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | grep -i "quarantine" | tee "$EVIDENCE_DIR/VF-09-1.txt"
RAW_ID=$(grep -c "SELECT.*q\.id[^:]" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>/dev/null) || RAW_ID=0
echo "RAW_ID_IN_QUARANTINE=$RAW_ID" | tee -a "$EVIDENCE_DIR/VF-09-1.txt"
```
**PASS if:** RAW_ID_IN_QUARANTINE is 0 — all quarantine queries use `id::text`.

#### VF-09.2: Search for raw `d.id` in deal queries
```bash
grep -n "SELECT.*d\.id\b" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -10 | tee "$EVIDENCE_DIR/VF-09-2.txt"
# Check if deal queries also cast to text
grep -n "d\.id::text" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | head -5 | tee -a "$EVIDENCE_DIR/VF-09-2.txt"
```
**INFO:** Document whether deal queries use `::text` cast. If they use raw UUID, it's the same class of bug waiting to surface. Classification: SCOPE_GAP (deals were not in scope for this mission).

#### VF-09.3: Check if UUID columns use `::text` cast consistently across all endpoints
```bash
echo "=== UUID cast usage ===" | tee "$EVIDENCE_DIR/VF-09-3.txt"
TEXT_CASTS=$(grep -c "id::text" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>/dev/null) || TEXT_CASTS=0
RAW_IDS=$(grep -c "SELECT.*\.id[^:]" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>/dev/null) || RAW_IDS=0
echo "ID_TEXT_CASTS=$TEXT_CASTS" | tee -a "$EVIDENCE_DIR/VF-09-3.txt"
echo "POTENTIAL_RAW_IDS=$RAW_IDS" | tee -a "$EVIDENCE_DIR/VF-09-3.txt"
```
**INFO:** Document the ratio. High RAW_IDS suggests the same bug class exists elsewhere.

**Gate VF-09:** VF-09.1 must PASS. VF-09.2 and VF-09.3 are INFO for scope assessment.

---

### VF-10 — Evidence File Completeness — 3 checks

**Context:** Completion report claims 13 evidence files. The evidence directory shows only 8 files. Are the other 5 missing?

#### VF-10.1: Count actual evidence files
```bash
ls -la /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/ 2>&1 | tee "$EVIDENCE_DIR/VF-10-1.txt"
ACTUAL=$(ls /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/ 2>/dev/null | wc -l) || ACTUAL=0
echo "ACTUAL_EVIDENCE_FILES=$ACTUAL" | tee -a "$EVIDENCE_DIR/VF-10-1.txt"
echo "CLAIMED_EVIDENCE_FILES=13" | tee -a "$EVIDENCE_DIR/VF-10-1.txt"
```
**PASS if:** ACTUAL >= 13. **FAIL if:** Files are missing. Classify as MISSING_FIX.

#### VF-10.2: Check for each claimed evidence file
```bash
MISSING=0
for f in P0-01-quarantine-baseline.txt P0-02-deals-baseline.txt P0-03-cleanup-transaction.txt P0-04-artifacts-intact.txt \
  P1-01-backend-health.txt P1-02-auth-state.txt P1-03-quarantine-endpoint.txt P1-04-dashboard-status.txt \
  P2-01-seed-injection.txt P2-02-seed-dedup.txt P2-03-seed-isolation.txt P2-04-correlation-id.txt P2-05-seed-cleanup.txt; do
  if test -f "/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/$f"; then
    echo "EXISTS: $f"
  else
    echo "MISSING: $f"
    MISSING=$((MISSING + 1))
  fi
done 2>&1 | tee "$EVIDENCE_DIR/VF-10-2.txt"
echo "MISSING_COUNT=$MISSING" | tee -a "$EVIDENCE_DIR/VF-10-2.txt"
```
**PASS if:** MISSING_COUNT is 0. All 13 claimed files exist.

#### VF-10.3: No empty evidence files
```bash
EMPTY=0
for f in /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/*.txt; do
  SIZE=$(wc -c < "$f" 2>/dev/null) || SIZE=0
  if [ "$SIZE" -eq 0 ]; then
    echo "EMPTY: $f"
    EMPTY=$((EMPTY + 1))
  fi
done 2>&1 | tee "$EVIDENCE_DIR/VF-10-3.txt"
echo "EMPTY_FILES=$EMPTY" | tee -a "$EVIDENCE_DIR/VF-10-3.txt"
```
**PASS if:** EMPTY_FILES is 0.

**Gate VF-10:** All 3 checks pass. Evidence pack is complete.

---

## 4. Cross-Consistency Checks

### XC-1: Completion Report AC Count Matches Mission Prompt AC Count
```bash
echo "=== Mission prompt ACs ===" | tee "$EVIDENCE_DIR/XC-1.txt"
MISSION_AC=$(grep -c "^### AC-" /home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.md 2>/dev/null) || MISSION_AC=0
echo "MISSION_PROMPT_AC=$MISSION_AC" | tee -a "$EVIDENCE_DIR/XC-1.txt"
echo "=== Completion report ACs ===" | tee -a "$EVIDENCE_DIR/XC-1.txt"
COMPLETION_AC=$(grep -c "| AC-" /home/zaks/bookkeeping/docs/MISSION-LANGSMITH-SHADOW-PILOT-001.COMPLETION.md 2>/dev/null) || COMPLETION_AC=0
echo "COMPLETION_AC=$COMPLETION_AC" | tee -a "$EVIDENCE_DIR/XC-1.txt"
echo "MATCH=$([ $MISSION_AC -eq $COMPLETION_AC ] && echo 'YES' || echo 'NO')" | tee -a "$EVIDENCE_DIR/XC-1.txt"
```
**PASS if:** MATCH=YES — both have 10 AC.

### XC-2: Tracker Precision Formula Matches Decision Packet Criteria
```bash
echo "=== Tracker formula ===" | tee "$EVIDENCE_DIR/XC-2.txt"
grep "Precision.*=" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>&1 | head -3 | tee -a "$EVIDENCE_DIR/XC-2.txt"
echo "=== Decision packet criteria ===" | tee -a "$EVIDENCE_DIR/XC-2.txt"
grep "80%\|>= 80\|>= 20" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>&1 | head -5 | tee -a "$EVIDENCE_DIR/XC-2.txt"
```
**PASS if:** Both documents agree on 80% target and 20-item minimum sample size.

### XC-3: Seed Injection Evidence Matches Injection Contract
```bash
echo "=== Contract says source_type in body is highest priority ===" | tee "$EVIDENCE_DIR/XC-3.txt"
grep "Priority\|body.*field\|Request body" /home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md 2>&1 | head -5 | tee -a "$EVIDENCE_DIR/XC-3.txt"
echo "=== Seed injection used body source_type ===" | tee -a "$EVIDENCE_DIR/XC-3.txt"
python3 -c "
import json
with open('/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/P2-01-seed-injection.txt') as f:
    line = f.readline()
    d = json.loads(line)
    print(f'Response received (source_type not in response = contract compliant)')
    print(f'message_id={d.get(\"message_id\")}')
    print(f'status={d.get(\"status\")}')
" 2>&1 | tee -a "$EVIDENCE_DIR/XC-3.txt"
```
**PASS if:** Seed injection followed the contract (source_type in body, X-API-Key header, valid message_id).

### XC-4: Bug Fix Evidence Matches Code
```bash
echo "=== Completion report says fix at lines ~1566 and ~1610 ===" | tee "$EVIDENCE_DIR/XC-4.txt"
grep -n "id::text" /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-4.txt"
echo "=== Lines 1566 and 1610 should contain id::text ===" | tee -a "$EVIDENCE_DIR/XC-4.txt"
sed -n '1565,1567p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-4.txt"
sed -n '1609,1611p' /home/zaks/zakops-backend/src/api/orchestration/main.py 2>&1 | tee -a "$EVIDENCE_DIR/XC-4.txt"
```
**PASS if:** Lines ~1566 and ~1610 contain `id::text`. If lines shifted, classify as INFO (not FAIL).

### XC-5: Decision Packet References Correct Tracker Path
```bash
grep -n "TRACKER\|tracker\|LANGSMITH-SHADOW-PILOT-TRACKER" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>&1 | tee "$EVIDENCE_DIR/XC-5.txt"
```
**PASS if:** Decision packet references the tracker file by name so the operator knows where to get the data.

---

## 5. Stress Tests

### ST-1: No `langsmith_live` Used During Pilot (Shadow-Only Guarantee)
```bash
# Search evidence files for any use of langsmith_live (should be zero)
LIVE_HITS=$(grep -rc "langsmith_live" /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-shadow-pilot-001/ 2>/dev/null | awk -F: '{sum+=$2} END {print sum}') || LIVE_HITS=0
echo "LANGSMITH_LIVE_IN_EVIDENCE=$LIVE_HITS" | tee "$EVIDENCE_DIR/ST-1.txt"
```
**PASS if:** LANGSMITH_LIVE_IN_EVIDENCE is 0. The pilot used `langsmith_shadow` exclusively.

### ST-2: No Stale QA Evidence Markers in Production Code
```bash
MARKERS=$(grep -rn "=== Contract ===\|=== Code ===\|=== Gap ===\|VERDICT:\|EXIT:" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v __pycache__ | grep "\.py:" | wc -l) || MARKERS=0
echo "STALE_QA_MARKERS=$MARKERS" | tee "$EVIDENCE_DIR/ST-2.txt"
grep -rn "=== Contract ===\|=== Code ===\|=== Gap ===" /home/zaks/zakops-backend/src/ 2>/dev/null | grep -v __pycache__ | grep "\.py:" | tee -a "$EVIDENCE_DIR/ST-2.txt"
```
**PASS if:** STALE_QA_MARKERS is 0.

### ST-3: Pilot Tracker Uses Correct API Port (8091, Not 8090)
```bash
PORT_8090=$(grep -c "8090" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || PORT_8090=0
PORT_8091=$(grep -c "8091" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || PORT_8091=0
echo "PORT_8090_REFS=$PORT_8090" | tee "$EVIDENCE_DIR/ST-3.txt"
echo "PORT_8091_REFS=$PORT_8091" | tee -a "$EVIDENCE_DIR/ST-3.txt"
echo "VERDICT: $([ $PORT_8090 -eq 0 ] && echo 'PASS' || echo 'FAIL — forbidden port 8090 referenced')" | tee -a "$EVIDENCE_DIR/ST-3.txt"
```
**PASS if:** PORT_8090_REFS is 0.

### ST-4: Decision Packet Has No Hardcoded Dates (Template Only)
```bash
HARDCODED_DATES=$(grep -cE "202[0-9]-[0-9]{2}-[0-9]{2}" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>/dev/null) || HARDCODED_DATES=0
echo "HARDCODED_DATES=$HARDCODED_DATES" | tee "$EVIDENCE_DIR/ST-4.txt"
grep -nE "202[0-9]-[0-9]{2}-[0-9]{2}" /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-DECISION.md 2>&1 | tee -a "$EVIDENCE_DIR/ST-4.txt"
```
**PASS if:** HARDCODED_DATES is 0 — decision packet is a clean template with blank date fields. If dates are present, classify: template example vs hardcoded (INFO vs FAIL).

### ST-5: Tracker SQL Queries Reference Correct Schema (zakops, not public)
```bash
PUBLIC_SCHEMA=$(grep -c "public\." /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || PUBLIC_SCHEMA=0
ZAKOPS_SCHEMA=$(grep -c "zakops\." /home/zaks/bookkeeping/docs/LANGSMITH-SHADOW-PILOT-TRACKER.md 2>/dev/null) || ZAKOPS_SCHEMA=0
echo "PUBLIC_SCHEMA_REFS=$PUBLIC_SCHEMA" | tee "$EVIDENCE_DIR/ST-5.txt"
echo "ZAKOPS_SCHEMA_REFS=$ZAKOPS_SCHEMA" | tee -a "$EVIDENCE_DIR/ST-5.txt"
echo "VERDICT: $([ $PUBLIC_SCHEMA -eq 0 ] && [ $ZAKOPS_SCHEMA -gt 0 ] && echo 'PASS' || echo 'CHECK — verify schema usage')" | tee -a "$EVIDENCE_DIR/ST-5.txt"
```
**PASS if:** ZAKOPS_SCHEMA_REFS > 0 AND PUBLIC_SCHEMA_REFS is 0. The quarantine_items table is in the `zakops` schema, not `public`.

### ST-6: No Promise.all or console.error Regressions in Dashboard
```bash
PA=$(grep -c "Promise\.all[^S]" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null) || PA=0
CE=$(grep -c "console\.error" /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx 2>/dev/null) || CE=0
echo "PROMISE_ALL=$PA" | tee "$EVIDENCE_DIR/ST-6.txt"
echo "CONSOLE_ERROR=$CE" | tee -a "$EVIDENCE_DIR/ST-6.txt"
echo "VERDICT: $([ $PA -eq 0 ] && [ $CE -eq 0 ] && echo 'PASS' || echo 'FAIL')" | tee -a "$EVIDENCE_DIR/ST-6.txt"
```
**PASS if:** Both are 0 (Surface 9 compliance maintained).

---

## 6. Remediation Protocol

When a gate returns FAIL:

1. **Read the evidence file** — understand the exact failure
2. **Classify the failure:**
   - `MISSING_FIX` — Claimed fix was not applied
   - `MISSING_EVIDENCE` — Evidence file claimed in completion report does not exist
   - `REGRESSION` — A prior fix was reverted or broken
   - `RESIDUAL_ARTIFACT` — Stale QA markers or test data left in production code
   - `TEMPLATE_ERROR` — Documentation deliverable has incorrect formulas, criteria, or references
   - `FALSE_POSITIVE` — Gate logic is wrong, code/docs are correct
   - `SCOPE_GAP` — Issue exists outside the mission's declared scope
3. **Apply minimal fix** following existing patterns
4. **Re-run the specific gate** — capture new evidence
5. **Re-run `make validate-local`** — ensure no regression
6. **Record in completion report** with before/after evidence paths

---

## 7. Enhancement Opportunities

### ENH-1: UUID Serialization Audit Across All Endpoints
The `id::text` bug in quarantine suggests other endpoints may have the same issue. A systematic audit of all SELECT queries returning UUID columns would prevent future 500 errors.

### ENH-2: Automated Evidence File Completeness Check
The completion report claimed 13 evidence files but only 8 exist in the directory. A post-mission script that compares claimed evidence against actual files would catch this.

### ENH-3: Pilot Tracker Auto-Population Script
Create a script that queries the database and pre-fills the daily log row, reducing operator manual work during the pilot.

### ENH-4: Decision Packet Precision Auto-Calculator
A script that reads the tracker and calculates cumulative precision, saving the operator from manual arithmetic.

### ENH-5: Database Cleanup Audit Trail
The cleanup transaction deleted 58 deals, 159 events, etc. without a record of WHAT was deleted (only counts). A pre-delete dump of deal IDs/names would provide a complete audit trail.

### ENH-6: Seed Test as Automated Smoke Test
The seed test curl commands could become a reusable smoke test script (`scripts/smoke-quarantine.sh`) that runs after deployments.

### ENH-7: ResponseValidationError Detection in CI
Add a test that exercises all response paths of the quarantine endpoint to catch UUID serialization issues before they reach production.

---

## 8. Scorecard Template

```
QA-LANGSMITH-SHADOW-PILOT-EXEC-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: Claude Code (Opus 4.6)

Pre-Flight:
  PF-1 (validate-local):          [ PASS / FAIL ]
  PF-2 (TypeScript):              [ PASS / FAIL ]
  PF-3 (Backend health):          [ PASS / FAIL / SKIP ]
  PF-4 (Source artifacts):        [ PASS / FAIL ]
  PF-5 (Evidence dir):            [ PASS / FAIL ]

Verification Families:
  VF-01 (id::text bug fix):       __ / 5  checks PASS
  VF-02 (security.py artifact):   __ / 3  checks PASS
  VF-03 (Environment cleanup):    __ / 4  checks PASS
  VF-04 (Backend health PF-3):    __ / 2  checks PASS
  VF-05 (Seed test evidence):     __ / 6  checks PASS
  VF-06 (Pilot tracker):          __ / 6  checks PASS
  VF-07 (Decision packet):        __ / 5  checks PASS
  VF-08 (Regressions/bookkeeping):__ / 3  checks PASS
  VF-09 (UUID sweep):             __ / 3  checks PASS/INFO
  VF-10 (Evidence completeness):  __ / 3  checks PASS

Cross-Consistency:
  XC-1 (AC count match):          [ PASS / FAIL ]
  XC-2 (Precision formula match): [ PASS / FAIL ]
  XC-3 (Contract compliance):     [ PASS / FAIL ]
  XC-4 (Bug fix line numbers):    [ PASS / FAIL / INFO ]
  XC-5 (Tracker reference):       [ PASS / FAIL ]

Stress Tests:
  ST-1 (Shadow-only guarantee):   [ PASS / FAIL ]
  ST-2 (No stale QA markers):     [ PASS / FAIL ]
  ST-3 (Port 8090 forbidden):     [ PASS / FAIL ]
  ST-4 (No hardcoded dates):      [ PASS / FAIL ]
  ST-5 (Correct schema):          [ PASS / FAIL ]
  ST-6 (Surface 9 compliance):    [ PASS / FAIL ]

Summary:
  Total gates:          __ / 72
  PASS:                 __
  FAIL:                 __
  INFO:                 __
  SKIP:                 __

  Remediations Applied: __
  Enhancement Opportunities: 7 (ENH-1 through ENH-7)

  Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **QA only** — Do not build new features. If a gate reveals a gap, classify and fix minimally.
2. **Remediate, don't redesign** — Fixes must follow existing patterns.
3. **Evidence-based** — Every PASS needs tee'd output in `$EVIDENCE_DIR`.
4. **Services-down accommodation** — If PF-3 fails, live gates (VF-03.2, VF-04.1, VF-05.6) become SKIP(services-down).
5. **Surface 9 compliance** — Dashboard checks include `'use client'`, `console.warn`, `Promise.allSettled`.
6. **Generated files are read-only** — Do not modify `api-types.generated.ts` or `backend_models.py`.
7. **WSL safety** — Strip CRLF and fix ownership on any new files.
8. **Record all changes** in `/home/zaks/bookkeeping/CHANGES.md`.
9. **Preserve prior fixes** — Remediation must not revert the `id::text` cast or `security.py` cleanup.
10. **No database modifications** — This QA reads database state but does not INSERT/UPDATE/DELETE.

---

## 10. Stop Condition

Stop when:
- All 72 verification gates pass, are justified (SKIP/INFO), or are remediated (FAIL → fix → re-gate → PASS)
- All remediations are applied and re-verified
- `make validate-local` passes as final check
- The scorecard is complete with evidence paths for every gate
- All changes recorded in CHANGES.md

Do NOT proceed to: one-week pilot execution, live promotion, or database cleanup. Those are out of scope.

---

*End of QA Mission Prompt — QA-LANGSMITH-SHADOW-PILOT-EXEC-VERIFY-001*
