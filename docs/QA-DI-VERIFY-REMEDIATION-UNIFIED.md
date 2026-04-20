> **POST-CONSOLIDATION NOTE (2026-02-16):** This document references `/home/zaks/zakops-backend/` paths
> which are now at `/home/zaks/zakops-agent-api/apps/backend/` after the monorepo consolidation
> (MONOREPO-CONSOLIDATION-001). Container `zakops-backend-postgres-1` is now `zakops-postgres-1`.
> Commands referencing the old standalone repo will not work. See `POST-MERGE-INCIDENT-RCA-2026-02-16.md`.

# QA VERIFICATION + REMEDIATION — DEAL-INTEGRITY-UNIFIED-001
## Codename: `QA-DI-VERIFY-UNIFIED`
## Version: V1 (Adversarial, Zero-Trust) | Date: 2026-02-08
## Executor: Claude Code (Opus 4.6)
## Authority: FULL EXECUTION — Verify everything, fix everything, leave nothing unchecked
## Target: DEAL-INTEGRITY-UNIFIED-001 "FOUNDATION ZERO" (6-layer platform mission)
## Reference: QA-HG-VERIFY-REMEDIATION.002.v2.md (QA standard — replicate rigor)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   DIRECTIVE: ZERO-TRUST ADVERSARIAL VERIFICATION + MANDATORY REMEDIATION    ║
║                                                                              ║
║   The builder executes a 6-layer platform stabilization mission across      ║
║   3 repositories, 4 services, 9 confirmed issues, 9 page-level gaps,       ║
║   5 cross-stack gaps, and 10 mandatory constraints.                         ║
║                                                                              ║
║   PRE-ANALYSIS IDENTIFIED CRITICAL CONCERNS:                                ║
║                                                                              ║
║   1. DI-ISSUE-001 integration tests (2 specific test cases from MASTER)     ║
║      are referenced but NOT enumerated in Layer 5. Verify they exist.       ║
║   2. DealBoard uses DUAL data-fetching paths (api-client.ts vs api.ts)      ║
║      — Layer 4 does not mention this. Both paths need resilience.           ║
║   3. Dashboard PG gaps PG-001, PG-002, PG-006, PG-007 appear in the        ║
║      defect registry but are NOT explicitly called out in exit gates.       ║
║   4. `make sync-all-types` is listed as a constraint (Q6) but is NOT       ║
║      formalized as a mandatory gate in EVERY layer that changes API shapes. ║
║   5. 4 operator decisions from MASTER have rationale (3 options each)       ║
║      that is NOT documented in the unified mission or ADRs.                 ║
║   6. 34 innovation ideas are deferred to Layer 6 but the catalogue         ║
║      requirement may be silently skipped as "out of scope."                 ║
║   7. "Mission Prompt Uses Wrong Column Names" finding from PASS1 Codex     ║
║      not addressed — column name accuracy not verified.                     ║
║   8. Organizational root cause statement from Chat Analysis not explicit    ║
║      in the mission premise.                                                ║
║   9. 10 Guiding Questions (Q1-Q10) must be formally answered in gates —   ║
║      not just referenced.                                                   ║
║  10. Industry best practice scorecard from Chat Analysis not included      ║
║      — no way to measure "world-class" claim objectively.                  ║
║                                                                              ║
║   This QA mission verifies EVERY gate from ALL 6 layers,                    ║
║   investigates EVERY gap and drop identified in cross-reference audit,      ║
║   and REMEDIATES failures in place.                                         ║
║   The auditor FIXES what fails — no separate remediation mission needed.   ║
║                                                                              ║
║   NOTHING passes without independent evidence.                               ║
║   NOTHING is skipped because "it probably works."                            ║
║   EVERY gate is verified with independent checks, not builder claims.       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## VERDICT RULES (NO CONDITIONAL PASS)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ABSOLUTE RULE: THERE IS NO "CONDITIONAL PASS" OR "PARTIAL PASS"          ║
║                                                                              ║
║   The verdict is PASS or FAIL. Nothing in between.                          ║
║                                                                              ║
║   AUTOMATIC FAIL triggers:                                                  ║
║   - Any Layer Gate fails AND is not remediated to PASS                     ║
║   - Any Negative Control is SKIPPED (not attempted)                        ║
║   - Any DI-ISSUE (001-009) is not fully resolved with evidence             ║
║   - Any PG gap (001-009) is not addressed in the appropriate layer         ║
║   - Any CS gap (001-005) is not addressed                                  ║
║   - Any Q constraint (Q1-Q10) is not satisfied with a verifiable gate      ║
║   - A dropped item from cross-reference audit is still missing             ║
║   - `make validate-local` fails at final verification                      ║
║   - Any surface pair in the Parity Test shows different counts             ║
║   - Any page goes entirely blank in the Resilience Test                    ║
║                                                                              ║
║   "Accepted with notes" = FAIL                                              ║
║   "Partial pass" = FAIL                                                     ║
║   "Conditional pass" = FAIL                                                 ║
║   "Pass with caveats" = FAIL                                                ║
║   "Deferred to future work" for a required gate = FAIL                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## CROSS-REFERENCE AUDIT — ITEMS DROPPED FROM SOURCE MATERIAL

The following items were identified as dropped or incomplete when cross-referencing the unified mission against the 3 source documents. Each must be verified as present in the builder's output or remediated into the mission.

### CRITICAL Drops

| ID | Dropped Item | Source | Expected Location | Verification |
|----|-------------|--------|-------------------|--------------|
| DROP-C1 | DI-ISSUE-001 specific integration tests: (a) after archive, `GET /deals?status=active` must NOT return deal; (b) after archive, `GET /deals?status=archived` MUST return deal | MASTER 5.1.5 | Layer 5 scope item 1 | V-L5-DI001 |
| DROP-C2 | DealBoard uses `useDeals` from `api-client.ts` while `/deals` page uses `getDeals` from `api.ts` — two independent data-fetching paths | Chat Analysis | Layer 4 scope | V-L4-DUAL |
| DROP-C3 | PG-001 (`/dashboard` Promise.all fragility) not in Layer 4 exit gates by name | Chat Analysis | Layer 4 gate L4-3 | V-L4-PG001 |
| DROP-C4 | PG-002 (`/dashboard` own STAGE_ORDER, client-side counting) not in Layer 3 exit gates by name | Chat Analysis | Layer 3 gate L3-3 | V-L3-PG002 |
| DROP-C5 | PG-006 (`/deals` STATUSES array missing 'archived') referenced in scope but not in exit gate | Chat Analysis | Layer 3 gate L3-5 | V-L3-PG006 |
| DROP-C6 | PG-007 (`/actions` Promise.all, no archived indicator) not in exit gates by name | Chat Analysis | Layer 4 gate L4-5 | V-L4-PG007 |
| DROP-C7 | `make sync-all-types` not formalized as mandatory gate in Layers 1, 2, 4 (only explicit in Layer 3) | Chat Analysis Q6 | Every layer that changes API shapes | V-SYNC gates |

### MEDIUM Drops

| ID | Dropped Item | Source | Expected Location | Verification |
|----|-------------|--------|-------------------|--------------|
| DROP-M1 | Operator Decisions 1-4 rationale (3 options each with tradeoffs) not documented in ADRs | MASTER Section 3 | Layer 6 ADR-001 | V-L6-ADR |
| DROP-M2 | 34 innovation ideas not catalogued (deferred statement exists but catalogue may be skipped) | MASTER Appendix | Layer 6 scope item 5 | V-L6-INNOVATION |
| DROP-M3 | 10 Guiding Questions not formally answered as gate evidence | Chat Analysis | Cross-layer | V-Q-FORMAL |
| DROP-M4 | Organizational root cause ("four independent decisions about shared data semantics with no coordination") not in mission premise | Chat Analysis | Mission intro | V-PREMISE |
| DROP-M5 | "Mission Prompt Uses Wrong Column Names" finding — column name accuracy in mission text | Codex PASS1 | Mission accuracy | V-COLNAMES |
| DROP-M6 | QA Checklist adversarial testing pattern from Codex batch generator not adopted | Codex template | Layer 5 | V-L5-ADVERSARIAL |

### LOW Drops

| ID | Dropped Item | Source | Expected Location | Verification |
|----|-------------|--------|-------------------|--------------|
| DROP-L1 | Evidence verification bash commands from MASTER not referenced in Layer 5 | MASTER evidence | Layer 5 | V-L5-EVIDENCE |
| DROP-L2 | Industry best practice scorecard from Chat Analysis | Chat Analysis | Layer 6 or final report | V-SCORECARD |
| DROP-L3 | Dashboard page coverage matrix (page × feature × status) | Chat Analysis | Layer 3 or Layer 5 | V-COVERAGE |

---

## SECTION 0: SETUP & BASELINE

### 0.1 Path Discovery (VERIFY — DO NOT ASSUME)

```bash
MONOREPO=$(git -C /home/zaks/zakops-agent-api rev-parse --show-toplevel)
BACKEND_ROOT="/home/zaks/zakops-backend"
ZAKS_LLM_ROOT="/home/zaks/Zaks-llm"
DASHBOARD_ROOT="$MONOREPO/apps/dashboard"
AGENT_API_ROOT="$MONOREPO/apps/agent-api"
MAKEFILE="$MONOREPO/Makefile"

echo "MONOREPO=$MONOREPO"
echo "BACKEND_ROOT=$BACKEND_ROOT"
echo "ZAKS_LLM_ROOT=$ZAKS_LLM_ROOT"
echo "DASHBOARD_ROOT=$DASHBOARD_ROOT"
echo "AGENT_API_ROOT=$AGENT_API_ROOT"
echo "MAKEFILE=$MAKEFILE"

# Verify all paths exist
for d in "$MONOREPO" "$BACKEND_ROOT" "$ZAKS_LLM_ROOT" "$DASHBOARD_ROOT" "$AGENT_API_ROOT"; do
  test -d "$d" && echo "OK: $d" || echo "FAIL: $d NOT FOUND"
done
test -f "$MAKEFILE" && echo "OK: Makefile" || echo "FAIL: Makefile NOT FOUND"
```

### 0.2 Evidence Structure

```bash
EVIDENCE_ROOT="/home/zaks/bookkeeping/qa-verifications/QA-DI-VERIFY-UNIFIED"
mkdir -p "$EVIDENCE_ROOT/evidence"/{
  V0-baseline,
  V-L1-infrastructure-truth,
  V-L2-data-model-integrity,
  V-L3-application-parity,
  V-L4-defensive-architecture,
  V-L5-verification-observability,
  V-L6-governance-evolution,
  RT-red-team,
  NC-negative-controls,
  D-discrepancies,
  D-drops-audit,
  R-remediation,
  FINAL-verification
}
```

### 0.3 Pre-Mission Infrastructure Check

```bash
cd "$MONOREPO"
make infra-check 2>&1 | tee "$EVIDENCE_ROOT/evidence/V0-baseline/infra-check.log"
echo "Exit: $?" >> "$EVIDENCE_ROOT/evidence/V0-baseline/infra-check.log"

make validate-local 2>&1 | tee "$EVIDENCE_ROOT/evidence/V0-baseline/validate-local-pre.log"
echo "Exit: $?" >> "$EVIDENCE_ROOT/evidence/V0-baseline/validate-local-pre.log"
```

**STOP IF `make validate-local` FAILS.** Pre-existing infrastructure must be intact before verifying the mission.

### 0.4 Capture Source Document State

```bash
# Verify all 3 source documents exist and capture checksums
for doc in \
  "/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_MASTER.md" \
  "/home/zaks/bookkeeping/docs/Chat-DEAL-INTEGRITY-001_MASTER.md.txt" \
  "/home/zaks/bookkeeping/docs/CODEX-INSTRUCTION-DASHBOARD-ROUND4-BATCH-GENERATOR.md"; do
  if test -f "$doc"; then
    echo "OK: $(basename "$doc") ($(wc -l < "$doc") lines)"
    sha256sum "$doc"
  else
    echo "FAIL: $doc NOT FOUND"
  fi
done | tee "$EVIDENCE_ROOT/evidence/V0-baseline/source_docs.txt"

# Verify unified mission exists
UNIFIED="/home/zaks/bookkeeping/docs/MISSION-DEAL-INTEGRITY-UNIFIED.md"
test -f "$UNIFIED" && echo "OK: UNIFIED ($(wc -l < "$UNIFIED") lines)" \
  || echo "FAIL: UNIFIED MISSION NOT FOUND"
sha256sum "$UNIFIED" 2>/dev/null
```

### GATE V0

| # | Check | Command | Expected | STOP IF |
|---|-------|---------|----------|---------|
| V0.1 | infra-check passes | `make infra-check` | exit 0 | exit != 0 |
| V0.2 | validate-local passes | `make validate-local` | exit 0 | exit != 0 |
| V0.3 | All 3 source docs exist | file checks | all present | any missing |
| V0.4 | Unified mission exists | file check | present, > 900 lines | missing |
| V0.5 | Evidence directories created | `ls evidence/` | 13 subdirs | < 13 |

---

## SECTION 1: LAYER-BY-LAYER VERIFICATION

Every gate from the unified mission's 6 layers is re-verified independently. The auditor does NOT trust builder evidence. The auditor runs independent checks and captures fresh output.

---

### LAYER 1 VERIFICATION: INFRASTRUCTURE TRUTH

**Mission requires:** Single canonical DB, rogue DB permanently destroyed, all services verified, DSN startup gate, health endpoint DB identity.
**Pre-analysis concern:** Rogue DB destruction is irreversible by design — verify it is ACTUALLY gone, not just stopped.

```bash
L1_DIR="$EVIDENCE_ROOT/evidence/V-L1-infrastructure-truth"

# V-L1.1: Docker Postgres containers — must be exactly ONE
docker ps --filter "ancestor=postgres" --format "{{.Names}} {{.Ports}}" 2>/dev/null \
  | tee "$L1_DIR/docker_postgres_running.txt"
docker ps -a --filter "ancestor=postgres" --format "{{.Names}} {{.Status}} {{.Ports}}" 2>/dev/null \
  | tee "$L1_DIR/docker_postgres_all.txt"
POSTGRES_COUNT=$(docker ps --filter "ancestor=postgres" --format "{{.Names}}" 2>/dev/null | wc -l)
echo "Running Postgres containers: $POSTGRES_COUNT" >> "$L1_DIR/docker_postgres_running.txt"
# Must be exactly 1

# V-L1.2: Rogue DB container GONE — not just stopped, REMOVED
docker ps -a --format "{{.Names}} {{.Ports}}" 2>/dev/null | grep -i "5435\|zakops-postgres" \
  | tee "$L1_DIR/rogue_db_search.txt"
ROGUE_TRACES=$(docker ps -a --format "{{.Names}} {{.Ports}}" 2>/dev/null | grep -c "5435\|zakops-postgres" || echo 0)
echo "Rogue DB traces: $ROGUE_TRACES (must be 0)" >> "$L1_DIR/rogue_db_search.txt"

# V-L1.3: Rogue DB volumes destroyed
docker volume ls 2>/dev/null | grep -i "zakops-postgres\|5435\|legacy" \
  | tee "$L1_DIR/rogue_volumes.txt"
echo "Rogue volumes found: $(wc -l < "$L1_DIR/rogue_volumes.txt")" >> "$L1_DIR/rogue_volumes.txt"

# V-L1.4: docker-compose files — no secondary Postgres service
for compose_file in $(find "$MONOREPO" "$BACKEND_ROOT" "$ZAKS_LLM_ROOT" \
  -maxdepth 2 -name "docker-compose*.yml" -o -name "docker-compose*.yaml" 2>/dev/null); do
  echo "=== $compose_file ===" >> "$L1_DIR/compose_postgres_audit.txt"
  grep -n -A5 "postgres\|5432\|5435" "$compose_file" 2>/dev/null \
    >> "$L1_DIR/compose_postgres_audit.txt"
done

# V-L1.5: .env files — ZERO references to port 5435
for repo in "$MONOREPO" "$BACKEND_ROOT" "$ZAKS_LLM_ROOT"; do
  find "$repo" -name ".env*" -not -path "*node_modules*" -not -path "*.git*" 2>/dev/null \
    | while read envfile; do
      HITS=$(grep -c "5435" "$envfile" 2>/dev/null || echo 0)
      if [ "$HITS" -gt 0 ]; then
        echo "FAIL: $envfile has $HITS references to 5435"
        grep -n "5435" "$envfile"
      fi
    done
done | tee "$L1_DIR/env_5435_audit.txt"
# Must be empty (zero references)

# V-L1.6: Agent API DSN verification (CS-001)
echo "=== Agent API DB Config ===" | tee "$L1_DIR/agent_api_dsn.txt"
find "$AGENT_API_ROOT" -name ".env*" -o -name "config*" -o -name "settings*" 2>/dev/null \
  | while read f; do
    grep -n "DATABASE\|POSTGRES\|DB_HOST\|DB_PORT\|5432\|5435" "$f" 2>/dev/null \
      | sed 's/:[^:@]*@/:***@/' \
      | while read line; do echo "$f: $line"; done
  done >> "$L1_DIR/agent_api_dsn.txt"

# V-L1.7: RAG/LLM service DSN verification (CS-002)
echo "=== RAG/LLM DB Config ===" | tee "$L1_DIR/rag_dsn.txt"
find "$ZAKS_LLM_ROOT" -name ".env*" -o -name "config*" -o -name "settings*" 2>/dev/null \
  | while read f; do
    grep -n "DATABASE\|POSTGRES\|DB_HOST\|DB_PORT\|5432\|5435" "$f" 2>/dev/null \
      | sed 's/:[^:@]*@/:***@/' \
      | while read line; do echo "$f: $line"; done
  done >> "$L1_DIR/rag_dsn.txt"

# V-L1.8: Health endpoint reports DB identity
curl -sf http://localhost:8091/health 2>/dev/null | jq . \
  | tee "$L1_DIR/backend_health.txt"
# Must show db_host, db_port, db_name fields

# V-L1.9: Startup DSN gate exists — search for DSN validation code
grep -rn "DSN\|DATABASE_URL\|startup.*check\|startup.*gate\|refuse.*start" \
  "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null | head -20 \
  | tee "$L1_DIR/dsn_gate_code.txt"

# V-L1.10: Canonical DSN documented in a single location
find "$MONOREPO" "$BACKEND_ROOT" -name "*.md" -path "*docs*" 2>/dev/null \
  | xargs grep -l "canonical.*DSN\|DATABASE_URL\|connection.*string" 2>/dev/null \
  | tee "$L1_DIR/dsn_documentation.txt"
```

| # | Gate | Expected | Evidence | Verdict |
|---|------|----------|----------|---------|
| V-L1.1 | Exactly 1 Postgres container running | count == 1 | docker_postgres_running.txt | |
| V-L1.2 | Rogue DB container GONE (not stopped — removed) | 0 traces of 5435/zakops-postgres | rogue_db_search.txt | |
| V-L1.3 | Rogue DB volumes destroyed | 0 rogue volumes | rogue_volumes.txt | |
| V-L1.4 | docker-compose: exactly 1 Postgres service per file | no secondary postgres | compose_postgres_audit.txt | |
| V-L1.5 | .env files: ZERO references to 5435 | empty output | env_5435_audit.txt | |
| V-L1.6 | Agent API DSN → canonical DB (CS-001) | port 5432, correct db | agent_api_dsn.txt | |
| V-L1.7 | RAG/LLM DSN → canonical DB (CS-002) | port 5432, correct db | rag_dsn.txt | |
| V-L1.8 | Health endpoint reports DB identity (Q2 partial) | db_host, db_port, db_name present | backend_health.txt | |
| V-L1.9 | Startup DSN gate exists — service refuses wrong DSN | gate code found | dsn_gate_code.txt | **REMEDIATE IF MISSING** |
| V-L1.10 | Canonical DSN documented (single source of truth) | doc file found | dsn_documentation.txt | **REMEDIATE IF MISSING** |

---

### LAYER 2 VERIFICATION: DATA MODEL INTEGRITY

**Mission requires:** Option A FSM with transition function, triggers, CHECK constraints, backfill, audit_trail, concurrency, ADR-001.
**Pre-analysis concern:** Backfill must handle BOTH groups (6 archived + 12 deleted = 18 rows). CHECK constraint must not fail on edge cases. Trigger must actually fire.

```bash
L2_DIR="$EVIDENCE_ROOT/evidence/V-L2-data-model-integrity"

# V-L2.1: ADR-001 exists and documents Option A
find "$EVIDENCE_ROOT" "$MONOREPO" -name "ADR-001*" -o -name "adr-001*" -o -name "adr_001*" 2>/dev/null \
  | tee "$L2_DIR/adr001_location.txt"
# Read first 50 lines if found
ADR=$(head -1 "$L2_DIR/adr001_location.txt" 2>/dev/null)
test -n "$ADR" && head -50 "$ADR" >> "$L2_DIR/adr001_content.txt" 2>/dev/null

# V-L2.2: Archive endpoint performs COMPLETE transition (status + stage)
# Test: archive a deal, verify BOTH fields changed
curl -sf -X POST http://localhost:8091/api/deals/1/archive 2>/dev/null | jq . \
  | tee "$L2_DIR/archive_response.txt"
# Then query the DB row directly
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT id, status, stage, deleted FROM zakops.deals WHERE id = 1;" 2>/dev/null \
  | tee "$L2_DIR/archive_db_verify.txt"
# Must show: status='archived' AND stage='archived'

# V-L2.3: Restore endpoint performs COMPLETE reversal
curl -sf -X POST http://localhost:8091/api/deals/1/restore 2>/dev/null | jq . \
  | tee "$L2_DIR/restore_response.txt"
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT id, status, stage, deleted FROM zakops.deals WHERE id = 1;" 2>/dev/null \
  | tee "$L2_DIR/restore_db_verify.txt"
# Must show: status='active' AND stage != 'archived'

# V-L2.4: transition_deal_state() function exists
grep -rn "transition_deal_state\|deal_state_transition\|change_deal_state" \
  "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  | tee "$L2_DIR/transition_function_search.txt"
# Must find the function definition

# V-L2.4b: No raw UPDATE queries for status/stage/deleted outside transition function
grep -rn "UPDATE.*deals.*SET.*status\|UPDATE.*deals.*SET.*stage\|UPDATE.*deals.*SET.*deleted" \
  "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  | grep -v "transition_deal_state\|migration\|alembic\|test" \
  | tee "$L2_DIR/raw_update_audit.txt"
# Must be EMPTY — all state changes go through the transition function

# V-L2.5: Backfill complete — ZERO inconsistent states
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT COUNT(*) AS inconsistent_count FROM zakops.deals
   WHERE (stage = 'archived' AND status != 'archived')
      OR (deleted = true AND status = 'active');" 2>/dev/null \
  | tee "$L2_DIR/backfill_inconsistent_check.txt"
# Must return 0

# V-L2.6: Backfill handled BOTH groups (Q1)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT status, stage, deleted, COUNT(*) as cnt
   FROM zakops.deals GROUP BY status, stage, deleted ORDER BY status, stage, deleted;" 2>/dev/null \
  | tee "$L2_DIR/backfill_state_distribution.txt"
# Verify: no (stage='archived', status='active') rows; no (deleted=true, status='active') rows

# V-L2.6b: Total deal count
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT COUNT(*) AS total FROM zakops.deals;" 2>/dev/null \
  | tee "$L2_DIR/total_deal_count.txt"
# Should be 49 (canonical count)

# V-L2.7: CHECK constraint exists and rejects impossible states
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT conname, conrelid::regclass, pg_get_constraintdef(oid)
   FROM pg_constraint
   WHERE conrelid = 'zakops.deals'::regclass AND contype = 'c';" 2>/dev/null \
  | tee "$L2_DIR/check_constraints.txt"
# Must show constraint(s) for status/stage/deleted validity

# V-L2.7b: Constraint rejects impossible state
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "INSERT INTO zakops.deals (status, stage, deleted)
   VALUES ('active', 'archived', false);" 2>&1 \
  | tee "$L2_DIR/constraint_rejection_test.txt"
# Must show ERROR (constraint violation)

# V-L2.8: Database trigger exists on deals table
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT tgname, tgtype, tgenabled, proname
   FROM pg_trigger t JOIN pg_proc p ON t.tgfoid = p.oid
   WHERE tgrelid = 'zakops.deals'::regclass
   AND NOT tgisinternal;" 2>/dev/null \
  | tee "$L2_DIR/trigger_check.txt"
# Must show trigger(s) on INSERT/UPDATE

# V-L2.8b: Trigger enforces consistency (test raw UPDATE bypass)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "BEGIN;
   UPDATE zakops.deals SET stage = 'archived' WHERE id = 1;
   SELECT status, stage FROM zakops.deals WHERE id = 1;
   ROLLBACK;" 2>&1 \
  | tee "$L2_DIR/trigger_enforcement_test.txt"
# Trigger should either REJECT or auto-correct status to 'archived'

# V-L2.9: Backfill reversibility documented (Q1, Q3)
find "$EVIDENCE_ROOT" "$MONOREPO" -name "*reversal*" -o -name "*rollback*backfill*" 2>/dev/null \
  | tee "$L2_DIR/reversal_docs.txt"

# V-L2.10: audit_trail column exists (DI-ISSUE-008)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT column_name, data_type, column_default
   FROM information_schema.columns
   WHERE table_schema = 'zakops' AND table_name = 'deals' AND column_name = 'audit_trail';" 2>/dev/null \
  | tee "$L2_DIR/audit_trail_column.txt"
# Must show: audit_trail, jsonb, '[]'::jsonb

# V-L2.10b: Transition function writes to audit_trail
grep -n "audit_trail" "$BACKEND_ROOT/src/" -r --include="*.py" 2>/dev/null \
  | tee "$L2_DIR/audit_trail_usage.txt"
# Must show transition function appending entries

# V-L2.11: v_pipeline_summary before/after documented (CS-005)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT * FROM zakops.v_pipeline_summary;" 2>/dev/null \
  | tee "$L2_DIR/pipeline_summary_current.txt"

# V-L2.12: Concurrency control exists (Q8)
grep -rn "FOR UPDATE\|SELECT.*FOR.*UPDATE\|optimistic.*concurr\|updated_at.*WHERE" \
  "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  | tee "$L2_DIR/concurrency_mechanism.txt"
# Must find locking or optimistic concurrency in state transition code

# V-L2.13: GET /api/deals?status=active returns ZERO archived deals
curl -sf "http://localhost:8091/api/deals?status=active" 2>/dev/null | jq '[.[] | select(.stage == "archived")] | length' \
  | tee "$L2_DIR/active_filter_test.txt"
# Must be 0

# V-L2.14: GET /api/deals?status=archived returns only archived deals
curl -sf "http://localhost:8091/api/deals?status=archived" 2>/dev/null | jq 'length' \
  | tee "$L2_DIR/archived_filter_test.txt"
# Must be > 0

# V-L2.15: Transition function is single choke point for Option C migration
# Verify: all callers pass target state, not raw field values
grep -rn "transition_deal_state\|deal_state_transition" "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  | grep -v "def " \
  | tee "$L2_DIR/transition_callers.txt"
# Callers should pass a state name like 'archived' or 'active', not raw field values

# V-L2.16: Backend starts and passes health check after all changes
curl -sf http://localhost:8091/health 2>/dev/null | jq . \
  | tee "$L2_DIR/post_l2_health.txt"
```

| # | Gate | Expected | Evidence | Verdict |
|---|------|----------|----------|---------|
| V-L2.1 | ADR-001 exists (Option A + FSM + Option C path) | file present, documents decision | adr001_*.txt | |
| V-L2.2 | Archive: COMPLETE transition (status + stage) | both = 'archived' | archive_*.txt | **REMEDIATE IF PARTIAL** |
| V-L2.3 | Restore: COMPLETE reversal | status='active', stage reset | restore_*.txt | **REMEDIATE IF PARTIAL** |
| V-L2.4 | transition_deal_state() exists | function found | transition_function_search.txt | **REMEDIATE IF MISSING** |
| V-L2.4b | ZERO raw UPDATE for state fields | empty output | raw_update_audit.txt | **REMEDIATE IF > 0** |
| V-L2.5 | Backfill: ZERO inconsistent states | count = 0 | backfill_inconsistent_check.txt | **REMEDIATE IF > 0** |
| V-L2.6 | Backfill: BOTH groups handled (Q1) | no (archived,active) or (deleted,active) | backfill_state_distribution.txt | |
| V-L2.6b | Total deals = 49 (canonical) | 49 | total_deal_count.txt | **INVESTIGATE IF != 49** |
| V-L2.7 | CHECK constraint exists | constraint(s) shown | check_constraints.txt | **REMEDIATE IF MISSING** |
| V-L2.7b | Constraint rejects impossible state | ERROR on insert | constraint_rejection_test.txt | |
| V-L2.8 | Trigger exists on deals INSERT/UPDATE | trigger(s) shown | trigger_check.txt | **REMEDIATE IF MISSING** |
| V-L2.8b | Trigger enforces consistency on bypass | reject or auto-correct | trigger_enforcement_test.txt | |
| V-L2.9 | Backfill reversal documented (Q1, Q3) | docs found | reversal_docs.txt | **REMEDIATE IF MISSING** |
| V-L2.10 | audit_trail column exists (DI-ISSUE-008) | JSONB column | audit_trail_column.txt | **REMEDIATE IF MISSING** |
| V-L2.10b | Transition function writes audit_trail | references found | audit_trail_usage.txt | |
| V-L2.11 | v_pipeline_summary verified (CS-005) | output captured | pipeline_summary_current.txt | |
| V-L2.12 | Concurrency control exists (Q8) | locking mechanism found | concurrency_mechanism.txt | **REMEDIATE IF MISSING** |
| V-L2.13 | active filter: ZERO archived deals | 0 | active_filter_test.txt | |
| V-L2.14 | archived filter: returns archived deals | > 0 | archived_filter_test.txt | |
| V-L2.15 | Transition function = single choke point | callers pass state name | transition_callers.txt | |
| V-L2.16 | Backend health OK after all changes | healthy response | post_l2_health.txt | |

---

### LAYER 3 VERIFICATION: APPLICATION PARITY

**Mission requires:** Canonical stage config, zero hardcoded lists, server-side counts, all page gaps fixed, cross-service parity, contract sync.
**Pre-analysis concerns:** PG-002 (dashboard STAGE_ORDER), PG-006 (/deals STATUSES), PG-009 (5+ hardcoded lists) are the critical ones to check.

```bash
L3_DIR="$EVIDENCE_ROOT/evidence/V-L3-application-parity"

# V-L3.1: Canonical stage configuration exists
echo "=== Stage Config Search ===" | tee "$L3_DIR/stage_config_search.txt"
grep -rn "PIPELINE_STAGES\|STAGE_ORDER\|stage.*config\|stageConfig\|stages.*canonical" \
  "$MONOREPO/packages/" "$DASHBOARD_ROOT/src/" "$BACKEND_ROOT/src/" \
  --include="*.ts" --include="*.tsx" --include="*.py" --include="*.json" 2>/dev/null \
  | tee -a "$L3_DIR/stage_config_search.txt"

# V-L3.2: ZERO hardcoded stage arrays in dashboard (PG-009)
echo "=== Hardcoded Stage Lists ===" | tee "$L3_DIR/hardcoded_stages.txt"
# Search for array literals with stage names
grep -rn "'prospecting'\|'qualification'\|'proposal'\|'negotiation'\|'closed_won'\|'closed_lost'\|'portfolio'\|'junk'" \
  "$DASHBOARD_ROOT/src/" --include="*.ts" --include="*.tsx" 2>/dev/null \
  | grep -v "node_modules\|.generated\." \
  | tee -a "$L3_DIR/hardcoded_stages.txt"
HARDCODED_COUNT=$(wc -l < "$L3_DIR/hardcoded_stages.txt" 2>/dev/null || echo 0)
echo "Hardcoded stage references: $HARDCODED_COUNT" >> "$L3_DIR/hardcoded_stages.txt"
# Should be 0 if all replaced with canonical config; investigate each if > 0

# V-L3.3: Server-side counts everywhere (DI-ISSUE-002, DI-ISSUE-003, PG-002)
echo "=== Client-Side Counting Audit ===" | tee "$L3_DIR/client_side_counting.txt"
grep -rn "\.filter.*stage\|\.filter.*status\|\.length" \
  "$DASHBOARD_ROOT/src/app/" --include="*.tsx" 2>/dev/null \
  | grep -i "deal\|count\|total\|stage" \
  | tee -a "$L3_DIR/client_side_counting.txt"
# Any remaining client-side deal counting = FINDING

# V-L3.4: DealBoard renders ALL pipeline stages (PG-003)
echo "=== DealBoard Stage Rendering ===" | tee "$L3_DIR/dealboard_stages.txt"
grep -n "PIPELINE_STAGES\|columns\|stage\|portfolio" \
  "$DASHBOARD_ROOT/src/components/DealBoard.tsx" 2>/dev/null \
  | tee -a "$L3_DIR/dealboard_stages.txt"
# Must show portfolio in the rendered columns

# V-L3.4b: DealBoard uses shared stage config (not local array)
head -30 "$DASHBOARD_ROOT/src/components/DealBoard.tsx" 2>/dev/null \
  | tee "$L3_DIR/dealboard_imports.txt"
# Must import from canonical config, not define locally

# V-L3.5: /deals filter includes 'archived' + button label correct (PG-005, PG-006)
echo "=== /deals Page Audit ===" | tee "$L3_DIR/deals_page_audit.txt"
grep -n "STATUSES\|status.*filter\|archived\|Archive\|Delete" \
  "$DASHBOARD_ROOT/src/app/deals/page.tsx" 2>/dev/null \
  | tee -a "$L3_DIR/deals_page_audit.txt"
# Must show: 'archived' in filter options; button labeled "Archive" not "Delete"

# V-L3.6: /deals/[id] visually distinguishes archived deals (PG-008)
grep -n "archived\|badge\|status.*color\|StatusBadge" \
  "$DASHBOARD_ROOT/src/app/deals/\[id\]/page.tsx" 2>/dev/null \
  | tee "$L3_DIR/deal_detail_archived_style.txt"
# Must show distinct styling for archived status

# V-L3.7: Agent API deal queries compatible with new lifecycle (Q5)
grep -rn "SELECT.*deals\|FROM.*deals\|status.*=\|stage.*=" \
  "$AGENT_API_ROOT/app/" --include="*.py" 2>/dev/null \
  | tee "$L3_DIR/agent_api_deal_queries.txt"
# Audit each query for compatibility with Option A lifecycle

# V-L3.8: RAG re-index after backfill (CS-003, Q5)
# Look for evidence of re-index execution
find "$EVIDENCE_ROOT" -name "*reindex*" -o -name "*re-index*" -o -name "*re_index*" 2>/dev/null \
  | tee "$L3_DIR/rag_reindex_evidence.txt"

# V-L3.9: make sync-all-types passes (Q6)
cd "$MONOREPO"
make sync-all-types 2>&1 | tee "$L3_DIR/sync_all_types.log"
echo "Exit: $?" >> "$L3_DIR/sync_all_types.log"

# V-L3.10: make validate-local passes after all Layer 3 changes
make validate-local 2>&1 | tee "$L3_DIR/validate_local_post_l3.log"
echo "Exit: $?" >> "$L3_DIR/validate_local_post_l3.log"

# V-L3.11: Pipeline summary counts sum correctly
curl -sf http://localhost:8091/api/pipeline/summary 2>/dev/null | jq . \
  | tee "$L3_DIR/pipeline_summary_api.txt"
# Verify: sum of all stage counts == total

# V-L3.12: THE PARITY TEST — 3 surface pairs must agree
echo "=== PARITY TEST ===" | tee "$L3_DIR/parity_test.txt"
# Pair A: /hq vs /dashboard header counts
echo "--- Pair A: /hq vs /dashboard ---" >> "$L3_DIR/parity_test.txt"
curl -sf http://localhost:3003/hq 2>/dev/null | grep -o "total.*[0-9]" | head -1 \
  >> "$L3_DIR/parity_test.txt"
curl -sf http://localhost:3003/dashboard 2>/dev/null | grep -o "total.*[0-9]" | head -1 \
  >> "$L3_DIR/parity_test.txt"
# Pair B: API pipeline/summary vs /hq
echo "--- Pair B: API vs /hq ---" >> "$L3_DIR/parity_test.txt"
curl -sf http://localhost:8091/api/pipeline/summary 2>/dev/null | jq '.total // .total_count' \
  >> "$L3_DIR/parity_test.txt"
# Pair C: API /deals count vs /deals page count
echo "--- Pair C: API /deals vs table ---" >> "$L3_DIR/parity_test.txt"
curl -sf http://localhost:8091/api/deals 2>/dev/null | jq 'if type == "array" then length else .total_count end' \
  >> "$L3_DIR/parity_test.txt"
```

| # | Gate | Expected | Evidence | Verdict |
|---|------|----------|----------|---------|
| V-L3.1 | Canonical stage config exists (PG-009) | single file, all stages defined | stage_config_search.txt | **REMEDIATE IF MISSING** |
| V-L3.2 | ZERO hardcoded stage arrays (PG-009) | 0 local stage lists | hardcoded_stages.txt | **REMEDIATE IF > 0** |
| V-L3.3 | Server-side counts everywhere (PG-002) | no client-side deal counting | client_side_counting.txt | **REMEDIATE IF FOUND** |
| V-L3.4 | DealBoard renders ALL stages incl. portfolio (PG-003) | portfolio in columns | dealboard_stages.txt | **REMEDIATE IF MISSING** |
| V-L3.5 | /deals: archived in filter + correct button label (PG-005, PG-006) | 'archived' option, "Archive" label | deals_page_audit.txt | **REMEDIATE IF WRONG** |
| V-L3.6 | /deals/[id]: archived visual distinction (PG-008) | distinct style for archived | deal_detail_archived_style.txt | |
| V-L3.7 | Agent API queries compatible (Q5) | no incompatibilities | agent_api_deal_queries.txt | **REMEDIATE IF INCOMPATIBLE** |
| V-L3.8 | RAG re-indexed after backfill (CS-003) | evidence of re-index | rag_reindex_evidence.txt | **REMEDIATE IF MISSING** |
| V-L3.9 | make sync-all-types passes (Q6) | exit 0 | sync_all_types.log | |
| V-L3.10 | make validate-local passes | exit 0 | validate_local_post_l3.log | |
| V-L3.11 | Pipeline summary sums correctly (DI-ISSUE-003) | sum == total | pipeline_summary_api.txt | |
| V-L3.12 | **PARITY TEST:** 3 surface pairs agree | all pairs match | parity_test.txt | **FAIL IF ANY PAIR DISAGREES** |

---

### LAYER 4 VERIFICATION: DEFENSIVE ARCHITECTURE

**Mission requires:** Promise.allSettled everywhere, graceful degradation, error boundaries, agent activity fix, kinetic endpoint resolution.
**Pre-analysis concerns:** DealBoard dual data-fetching path (DROP-C2), /dashboard fragility (PG-001), /actions fragility (PG-007).

```bash
L4_DIR="$EVIDENCE_ROOT/evidence/V-L4-defensive-architecture"

# V-L4.1: ZERO Promise.all for data fetching
echo "=== Promise.all Audit ===" | tee "$L4_DIR/promise_all_audit.txt"
grep -rn "Promise\.all" "$DASHBOARD_ROOT/src/" --include="*.ts" --include="*.tsx" 2>/dev/null \
  | grep -v "Promise\.allSettled\|node_modules\|.generated\." \
  | tee -a "$L4_DIR/promise_all_audit.txt"
PROMISE_ALL_COUNT=$(wc -l < "$L4_DIR/promise_all_audit.txt" 2>/dev/null || echo 0)
echo "Remaining Promise.all: $PROMISE_ALL_COUNT (must be 0)" >> "$L4_DIR/promise_all_audit.txt"

# V-L4.2: /hq graceful degradation (PG-001 original / DI-ISSUE-005)
echo "=== /hq Error Handling ===" | tee "$L4_DIR/hq_error_handling.txt"
grep -n "allSettled\|catch\|error\|fallback\|Failed to load" \
  "$DASHBOARD_ROOT/src/app/hq/page.tsx" 2>/dev/null \
  | tee -a "$L4_DIR/hq_error_handling.txt"

# V-L4.3: /dashboard graceful degradation (PG-001)
echo "=== /dashboard Error Handling ===" | tee "$L4_DIR/dashboard_error_handling.txt"
grep -n "allSettled\|catch\|error\|fallback\|Failed to load" \
  "$DASHBOARD_ROOT/src/app/dashboard/page.tsx" 2>/dev/null \
  | tee -a "$L4_DIR/dashboard_error_handling.txt"
# PG-001 SPECIFICALLY: /dashboard had 5 fetches with Promise.all

# V-L4.4: /deals/[id] graceful degradation (PG-004)
echo "=== /deals/[id] Error Handling ===" | tee "$L4_DIR/deal_detail_error_handling.txt"
grep -n "allSettled\|catch\|error\|fallback\|Failed to load" \
  "$DASHBOARD_ROOT/src/app/deals/\[id\]/page.tsx" 2>/dev/null \
  | tee -a "$L4_DIR/deal_detail_error_handling.txt"
# PG-004: 7 fetches with Promise.all — worst instance

# V-L4.5: /actions graceful degradation (PG-007)
echo "=== /actions Error Handling ===" | tee "$L4_DIR/actions_error_handling.txt"
grep -n "allSettled\|catch\|error\|fallback\|Failed to load" \
  "$DASHBOARD_ROOT/src/app/actions/page.tsx" 2>/dev/null \
  | tee -a "$L4_DIR/actions_error_handling.txt"

# V-L4-DUAL: DealBoard dual data-fetching path (DROP-C2)
echo "=== DealBoard Data Fetching Path ===" | tee "$L4_DIR/dealboard_fetch_path.txt"
grep -n "useDeals\|api-client\|getDeals\|fetchDeals\|useSWR\|fetch" \
  "$DASHBOARD_ROOT/src/components/DealBoard.tsx" 2>/dev/null \
  | tee -a "$L4_DIR/dealboard_fetch_path.txt"
# Compare to /deals page data fetching:
grep -n "getDeals\|api\.ts\|api-client\|fetchDeals\|useSWR\|fetch" \
  "$DASHBOARD_ROOT/src/app/deals/page.tsx" 2>/dev/null \
  | tee -a "$L4_DIR/dealboard_fetch_path.txt"
echo "--- Verify both paths have error handling ---" >> "$L4_DIR/dealboard_fetch_path.txt"

# V-L4.6: Agent activity endpoint returns consistent shape (DI-ISSUE-005)
curl -sf http://localhost:3003/api/agent/activity 2>/dev/null | jq 'type' \
  | tee "$L4_DIR/agent_activity_shape.txt"
# Must be "object" — never "array"

# V-L4.7: /api/actions/kinetic resolved (DI-ISSUE-009)
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8091/api/actions/kinetic 2>/dev/null)
echo "Status: $HTTP_STATUS" | tee "$L4_DIR/kinetic_endpoint.txt"
# Must be 200 (fixed) or 404 (removed) — NOT 500

# V-L4.8: Zero Zod validation errors under normal operation
# This requires browser testing or documented evidence
echo "Zod validation check requires browser console evidence from:" \
  | tee "$L4_DIR/zod_check.txt"
echo "  /hq, /dashboard, /deals, /deals/[id], /actions" \
  >> "$L4_DIR/zod_check.txt"

# V-L4.9: Error boundaries exist
grep -rn "ErrorBoundary\|error.*boundary\|errorElement" \
  "$DASHBOARD_ROOT/src/" --include="*.tsx" --include="*.ts" 2>/dev/null \
  | tee "$L4_DIR/error_boundaries.txt"

# V-L4.10: THE RESILIENCE TEST — fail each source, page must not blank
echo "=== RESILIENCE TEST ===" | tee "$L4_DIR/resilience_test.txt"
echo "For each dashboard page, systematically fail each data source." >> "$L4_DIR/resilience_test.txt"
echo "The page must never go entirely blank." >> "$L4_DIR/resilience_test.txt"
echo "Evidence: page x failed-source -> rendering result" >> "$L4_DIR/resilience_test.txt"
# This must be documented with actual test results

# V-L4.11: API fetcher functions all have error handling
echo "=== API Fetcher Error Handling Audit ===" | tee "$L4_DIR/api_fetcher_audit.txt"
for api_file in $(find "$DASHBOARD_ROOT/src" -name "api.ts" -o -name "api-client.ts" 2>/dev/null); do
  echo "--- $api_file ---" >> "$L4_DIR/api_fetcher_audit.txt"
  grep -n "async function\|export.*function\|try\|catch" "$api_file" 2>/dev/null \
    >> "$L4_DIR/api_fetcher_audit.txt"
done
```

| # | Gate | Expected | Evidence | Verdict |
|---|------|----------|----------|---------|
| V-L4.1 | ZERO Promise.all for data fetching | count = 0 | promise_all_audit.txt | **REMEDIATE IF > 0** |
| V-L4.2 | /hq graceful degradation | allSettled + fallbacks | hq_error_handling.txt | |
| V-L4.3 | /dashboard graceful degradation (PG-001) | allSettled + fallbacks | dashboard_error_handling.txt | **REMEDIATE IF MISSING** |
| V-L4.4 | /deals/[id] graceful degradation (PG-004) | allSettled + fallbacks | deal_detail_error_handling.txt | **REMEDIATE IF MISSING** |
| V-L4.5 | /actions graceful degradation (PG-007) | allSettled + fallbacks | actions_error_handling.txt | **REMEDIATE IF MISSING** |
| V-L4-DUAL | DealBoard dual fetch path has error handling (DROP-C2) | both paths resilient | dealboard_fetch_path.txt | **REMEDIATE IF UNPROTECTED** |
| V-L4.6 | Agent activity: always object, never array | type = "object" | agent_activity_shape.txt | **REMEDIATE IF ARRAY** |
| V-L4.7 | /api/actions/kinetic: not 500 (DI-ISSUE-009) | 200 or 404 | kinetic_endpoint.txt | **REMEDIATE IF 500** |
| V-L4.8 | Zero Zod errors on all pages | browser console clean | zod_check.txt | |
| V-L4.9 | Error boundaries exist on major sections | ErrorBoundary components found | error_boundaries.txt | **REMEDIATE IF MISSING** |
| V-L4.10 | **RESILIENCE TEST:** no page blanks on single failure | all partial renders | resilience_test.txt | **FAIL IF ANY PAGE BLANKS** |
| V-L4.11 | ALL API fetcher functions have try/catch | every function protected | api_fetcher_audit.txt | **REMEDIATE IF UNPROTECTED** |

---

### LAYER 5 VERIFICATION: VERIFICATION & OBSERVABILITY

**Mission requires:** Automated tests for every "Never Again," CI gates, performance baselines, production observability.
**Pre-analysis concerns:** DI-ISSUE-001 specific test cases (DROP-C1) must be enumerated. Adversarial test pattern (DROP-M6) should be adopted.

```bash
L5_DIR="$EVIDENCE_ROOT/evidence/V-L5-verification-observability"

# V-L5.1: Test files exist and map to MASTER "Never Again" items
echo "=== Test File Inventory ===" | tee "$L5_DIR/test_inventory.txt"
find "$MONOREPO" "$BACKEND_ROOT" "$ZAKS_LLM_ROOT" \
  -name "test_*" -o -name "*_test.*" -o -name "*.test.*" -o -name "*.spec.*" 2>/dev/null \
  | grep -v "node_modules\|__pycache__\|.git" \
  | tee -a "$L5_DIR/test_inventory.txt"
TEST_COUNT=$(wc -l < "$L5_DIR/test_inventory.txt" 2>/dev/null || echo 0)
echo "Total test files: $TEST_COUNT" >> "$L5_DIR/test_inventory.txt"

# V-L5-DI001: DI-ISSUE-001 SPECIFIC integration tests (DROP-C1)
echo "=== DI-ISSUE-001 Integration Tests ===" | tee "$L5_DIR/di001_tests.txt"
grep -rn "archive.*active\|archived.*status\|after.*archiv" \
  "$BACKEND_ROOT" "$MONOREPO" --include="*test*" --include="*spec*" 2>/dev/null \
  | tee -a "$L5_DIR/di001_tests.txt"
# MUST find:
# (a) Test: after archive, GET /deals?status=active does NOT return the deal
# (b) Test: after archive, GET /deals?status=archived DOES return the deal
# If missing → REMEDIATION REQUIRED (this was explicitly in MASTER 5.1.5)

# V-L5.2: Lifecycle transition tests pass
echo "=== Lifecycle Tests ===" | tee "$L5_DIR/lifecycle_tests.txt"
grep -rn "transition\|archive\|restore\|invalid.*state\|concurrent.*archive" \
  "$BACKEND_ROOT" "$MONOREPO" --include="*test*" 2>/dev/null \
  | tee -a "$L5_DIR/lifecycle_tests.txt"

# V-L5.3: Pipeline count invariant tests exist
grep -rn "pipeline.*count\|sum.*stage\|invariant\|total.*equal\|count.*match" \
  "$BACKEND_ROOT" "$MONOREPO" --include="*test*" 2>/dev/null \
  | tee "$L5_DIR/pipeline_invariant_tests.txt"

# V-L5.4: Contract schema tests exist (Q6)
grep -rn "schema.*valid\|zod.*test\|openapi.*match\|contract.*test" \
  "$DASHBOARD_ROOT" "$MONOREPO" --include="*test*" --include="*spec*" 2>/dev/null \
  | tee "$L5_DIR/contract_schema_tests.txt"

# V-L5.5: E2E flow tests (create → archive → restore)
grep -rn "create.*deal.*archive\|full.*flow\|e2e.*deal\|end.to.end" \
  "$BACKEND_ROOT" "$MONOREPO" --include="*test*" 2>/dev/null \
  | tee "$L5_DIR/e2e_flow_tests.txt"

# V-L5.6: API health suite — every endpoint returns non-500
echo "=== API Health Suite ===" | tee "$L5_DIR/api_health_suite.txt"
grep -rn "endpoint.*health\|api.*health\|non.500\|status.*code" \
  "$BACKEND_ROOT" "$MONOREPO" --include="*test*" 2>/dev/null \
  | tee -a "$L5_DIR/api_health_suite.txt"

# V-L5.7: make validate-local passes
cd "$MONOREPO"
make validate-local 2>&1 | tee "$L5_DIR/validate_local_post_l5.log"
echo "Exit: $?" >> "$L5_DIR/validate_local_post_l5.log"

# V-L5.8: Performance baselines captured (Q9)
find "$EVIDENCE_ROOT" -name "*performance*" -o -name "*baseline*" -o -name "*query_plan*" \
  -o -name "*explain*" -o -name "*response_time*" 2>/dev/null \
  | tee "$L5_DIR/performance_baselines.txt"

# V-L5.9: Indexes exist for critical queries
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT indexname, indexdef FROM pg_indexes
   WHERE tablename = 'deals' AND schemaname = 'zakops';" 2>/dev/null \
  | tee "$L5_DIR/deals_indexes.txt"
# Must show indexes on status, stage, deleted (or composite)

# V-L5.10: Health endpoints report DB identity + count invariants (Q2)
for svc_url in "http://localhost:8091/health" "http://localhost:8095/health"; do
  echo "=== $svc_url ===" >> "$L5_DIR/health_endpoints.txt"
  curl -sf "$svc_url" 2>/dev/null | jq . >> "$L5_DIR/health_endpoints.txt"
done

# V-L5.11: State transition logging active (Q2)
grep -rn "log.*transition\|logger.*state\|structured.*log\|audit.*log" \
  "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  | tee "$L5_DIR/transition_logging.txt"

# V-L5.12: Count invariant monitoring exists
grep -rn "invariant.*monitor\|count.*check\|invariant_holds\|deal.*count.*alert" \
  "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  | tee "$L5_DIR/invariant_monitoring.txt"
```

| # | Gate | Expected | Evidence | Verdict |
|---|------|----------|----------|---------|
| V-L5.1 | Test files exist for every "Never Again" | mapping complete | test_inventory.txt | **REMEDIATE IF GAPS** |
| V-L5-DI001 | DI-ISSUE-001 specific tests (DROP-C1) | 2 specific tests enumerated | di001_tests.txt | **REMEDIATE IF MISSING** |
| V-L5.2 | Lifecycle transition tests | tests found and pass | lifecycle_tests.txt | **REMEDIATE IF MISSING** |
| V-L5.3 | Pipeline count invariant tests | tests found | pipeline_invariant_tests.txt | **REMEDIATE IF MISSING** |
| V-L5.4 | Contract schema tests (Q6) | tests found | contract_schema_tests.txt | |
| V-L5.5 | E2E flow tests (DI-ISSUE-007) | create→archive→restore flow | e2e_flow_tests.txt | |
| V-L5.6 | API health suite (DI-ISSUE-009) | endpoint tests found | api_health_suite.txt | |
| V-L5.7 | make validate-local passes | exit 0 | validate_local_post_l5.log | |
| V-L5.8 | Performance baselines captured (Q9) | evidence files found | performance_baselines.txt | **REMEDIATE IF MISSING** |
| V-L5.9 | Indexes on critical columns (Q9) | status/stage/deleted indexed | deals_indexes.txt | **REMEDIATE IF MISSING** |
| V-L5.10 | Health endpoints report DB identity (Q2) | db fields in response | health_endpoints.txt | |
| V-L5.11 | State transition logging active (Q2) | structured log found | transition_logging.txt | **REMEDIATE IF MISSING** |
| V-L5.12 | Count invariant monitoring (Q2) | mechanism found | invariant_monitoring.txt | **REMEDIATE IF MISSING** |

---

### LAYER 6 VERIFICATION: GOVERNANCE & EVOLUTION

**Mission requires:** ADR-001/002/003, runbook, innovation roadmap, change protocol.
**Pre-analysis concerns:** Operator decision rationale (DROP-M1) must be in ADRs. Innovation catalogue (DROP-M2) must actually exist.

```bash
L6_DIR="$EVIDENCE_ROOT/evidence/V-L6-governance-evolution"

# V-L6.1: ADR-001 — Lifecycle State Machine
find "$MONOREPO" "$EVIDENCE_ROOT" -name "ADR-001*" -o -name "adr-001*" 2>/dev/null \
  | tee "$L6_DIR/adr001_search.txt"
ADR1=$(head -1 "$L6_DIR/adr001_search.txt" 2>/dev/null)
test -n "$ADR1" && wc -l "$ADR1" >> "$L6_DIR/adr001_search.txt" 2>/dev/null

# V-L6-ADR: ADR-001 includes operator decision rationale (DROP-M1)
# Must document: why Option A, not B or C; the 3 options considered; tradeoffs
test -n "$ADR1" && grep -c "Option B\|Option C\|tradeoff\|alternative\|considered\|rationale" "$ADR1" 2>/dev/null \
  | tee "$L6_DIR/adr001_rationale_check.txt"
# Must be >= 3 (showing alternatives were discussed)

# V-L6.2: ADR-002 — Canonical Database
find "$MONOREPO" "$EVIDENCE_ROOT" -name "ADR-002*" -o -name "adr-002*" 2>/dev/null \
  | tee "$L6_DIR/adr002_search.txt"

# V-L6.3: ADR-003 — Stage Configuration Authority
find "$MONOREPO" "$EVIDENCE_ROOT" -name "ADR-003*" -o -name "adr-003*" 2>/dev/null \
  | tee "$L6_DIR/adr003_search.txt"

# V-L6.4: THE RUNBOOK TEST — "How to Add a New Deal Stage"
find "$MONOREPO" "$EVIDENCE_ROOT" -name "*runbook*" -o -name "*how*to*add*stage*" 2>/dev/null \
  | tee "$L6_DIR/runbook_search.txt"
RUNBOOK=$(head -1 "$L6_DIR/runbook_search.txt" 2>/dev/null)
test -n "$RUNBOOK" && grep -c "step\|Step\|1\.\|2\.\|3\." "$RUNBOOK" 2>/dev/null \
  | tee "$L6_DIR/runbook_steps.txt"
# Must have verifiable steps that a new engineer can follow

# V-L6-INNOVATION: Innovation roadmap with 34 ideas (DROP-M2)
find "$MONOREPO" "$EVIDENCE_ROOT" -name "*innovation*" -o -name "*roadmap*" -o -name "*ideas*" 2>/dev/null \
  | tee "$L6_DIR/innovation_search.txt"
ROADMAP=$(head -1 "$L6_DIR/innovation_search.txt" 2>/dev/null)
test -n "$ROADMAP" && grep -c "I-[0-9]\|idea\|Idea" "$ROADMAP" 2>/dev/null \
  | tee "$L6_DIR/innovation_count.txt"
# Must catalogue all 34 ideas (I-01 through I-34)

# V-L6.6: Change protocol exists
find "$MONOREPO" -name "*checklist*" -o -name "*change.*protocol*" -o -name "CODEOWNERS" 2>/dev/null \
  | tee "$L6_DIR/change_protocol_search.txt"
grep -rn "deal.*state\|transition.*function\|stage.*config" \
  "$MONOREPO/.github/" --include="*.yml" --include="*.yaml" 2>/dev/null \
  | tee -a "$L6_DIR/change_protocol_search.txt"
```

| # | Gate | Expected | Evidence | Verdict |
|---|------|----------|----------|---------|
| V-L6.1 | ADR-001 exists and accurate | file present, > 20 lines | adr001_search.txt | **REMEDIATE IF MISSING** |
| V-L6-ADR | ADR-001 includes decision rationale (DROP-M1) | 3+ alternatives discussed | adr001_rationale_check.txt | **REMEDIATE IF MISSING** |
| V-L6.2 | ADR-002 exists (Canonical DB) | file present | adr002_search.txt | **REMEDIATE IF MISSING** |
| V-L6.3 | ADR-003 exists (Stage Config Authority) | file present | adr003_search.txt | **REMEDIATE IF MISSING** |
| V-L6.4 | **RUNBOOK TEST:** Add-a-stage runbook exists and is testable | file present, verifiable steps | runbook_search.txt | **REMEDIATE IF MISSING** |
| V-L6-INNOVATION | Innovation roadmap: 34 ideas catalogued (DROP-M2) | 34 entries (I-01..I-34) | innovation_count.txt | **REMEDIATE IF < 34** |
| V-L6.6 | Change protocol / PR checklist exists | checklist or CI trigger found | change_protocol_search.txt | **REMEDIATE IF MISSING** |

---

## SECTION 2: HARD RULES COMPLIANCE CHECK

Every hard rule from the unified mission verified independently.

```bash
HR_DIR="$EVIDENCE_ROOT/evidence/D-discrepancies"
echo "=== HARD RULES COMPLIANCE ===" > "$HR_DIR/hard_rules.txt"

# HR-1: No layer skipped — check all 6 completion reports exist
echo "--- HR-1: No Layers Skipped ---" >> "$HR_DIR/hard_rules.txt"
for i in 1 2 3 4 5 6; do
  REPORT="$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/layer-$i/completion-report.md"
  test -f "$REPORT" \
    && echo "OK: Layer $i completion report exists" \
    || echo "FAIL: Layer $i completion report MISSING"
done >> "$HR_DIR/hard_rules.txt"

# HR-2: No gate marked PASS without evidence
echo "--- HR-2: Evidence for Every Gate ---" >> "$HR_DIR/hard_rules.txt"
for i in 1 2 3 4 5 6; do
  EVIDENCE_DIR="$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/layer-$i/evidence/"
  if test -d "$EVIDENCE_DIR"; then
    FILE_COUNT=$(find "$EVIDENCE_DIR" -type f 2>/dev/null | wc -l)
    EMPTY_COUNT=$(find "$EVIDENCE_DIR" -type f -empty 2>/dev/null | wc -l)
    echo "Layer $i: $FILE_COUNT evidence files, $EMPTY_COUNT empty"
  else
    echo "Layer $i: evidence directory MISSING"
  fi
done >> "$HR_DIR/hard_rules.txt"

# HR-3: No silent skips — search completion reports for "skip" or "defer"
echo "--- HR-3: No Silent Skips ---" >> "$HR_DIR/hard_rules.txt"
grep -rn "skip\|defer\|out of scope\|future work\|not implemented" \
  "$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/layer-"*/completion-report.md 2>/dev/null \
  >> "$HR_DIR/hard_rules.txt"
# Each occurrence must have documented reason

# HR-4: Generated files never manually edited
echo "--- HR-4: Generated Files Untouched ---" >> "$HR_DIR/hard_rules.txt"
cd "$MONOREPO"
git log --oneline --diff-filter=M -- \
  "apps/dashboard/src/lib/api-types.generated.ts" \
  "apps/dashboard/src/lib/agent-api-types.generated.ts" \
  "apps/agent-api/app/schemas/backend_models.py" 2>/dev/null \
  | tee -a "$HR_DIR/hard_rules.txt"
# Verify: only codegen commits, not manual edits

# HR-5: CRLF hazard — check all .sh files
echo "--- HR-5: CRLF Check ---" >> "$HR_DIR/hard_rules.txt"
find "$MONOREPO" "$BACKEND_ROOT" "$ZAKS_LLM_ROOT" -name "*.sh" 2>/dev/null \
  | while read sh; do
    if file "$sh" | grep -q CRLF; then
      echo "FAIL: $sh has CRLF line endings"
    fi
  done >> "$HR_DIR/hard_rules.txt"

# HR-6: Port 8090 never referenced
echo "--- HR-6: Port 8090 Forbidden ---" >> "$HR_DIR/hard_rules.txt"
grep -rn "8090" "$MONOREPO" "$BACKEND_ROOT" "$ZAKS_LLM_ROOT" \
  --include="*.py" --include="*.ts" --include="*.tsx" --include="*.yml" --include="*.yaml" \
  --include="*.env*" --include="*.json" 2>/dev/null \
  | grep -v "node_modules\|.git\|package-lock" \
  >> "$HR_DIR/hard_rules.txt"
# Must be empty

# HR-7: zakops DB uses schema zakops, NOT public; user zakops, NOT dealengine
echo "--- HR-7: DB Schema/User ---" >> "$HR_DIR/hard_rules.txt"
grep -rn "dealengine\|public\.deals" "$BACKEND_ROOT/src/" --include="*.py" 2>/dev/null \
  >> "$HR_DIR/hard_rules.txt"
# Must be empty

# HR-8: Redocly ignore ceiling = 57
echo "--- HR-8: Redocly Ignores ---" >> "$HR_DIR/hard_rules.txt"
IGNORE_COUNT=$(grep -c "ignore" "$MONOREPO/.redocly.yaml" 2>/dev/null || echo 0)
echo "Redocly ignores: $IGNORE_COUNT (ceiling: 57)" >> "$HR_DIR/hard_rules.txt"

# HR-9: Rollback ordering respected (Layer N requires Layer N+1 rollback first)
echo "--- HR-9: Rollback Dependencies ---" >> "$HR_DIR/hard_rules.txt"
echo "Dependency chain: L1 → L2 → L3 → L5; L4 || L3; L6 || L5" >> "$HR_DIR/hard_rules.txt"
echo "Verify: each layer's completion report documents rollback procedure" >> "$HR_DIR/hard_rules.txt"

# HR-10: No new features — every change traces to DI-ISSUE/PG/CS/Q
echo "--- HR-10: No Scope Creep ---" >> "$HR_DIR/hard_rules.txt"
echo "Review git log for commits that don't reference DI-ISSUE/PG/CS/Q" >> "$HR_DIR/hard_rules.txt"
```

---

## SECTION 3: RED-TEAM GATES (RT1-RT20)

Adversarial checks: are the mission deliverables REAL or theater?

```bash
RT_DIR="$EVIDENCE_ROOT/evidence/RT-red-team"
echo "=== RED-TEAM GATES ===" > "$RT_DIR/rt_checks.txt"

# RT-1: transition_deal_state() is REAL (has actual SQL, not a stub)
echo "--- RT-1: Transition function reality ---" >> "$RT_DIR/rt_checks.txt"
grep -A20 "def transition_deal_state\|def change_deal_state\|def deal_state_transition" \
  "$BACKEND_ROOT/src/" -r --include="*.py" 2>/dev/null | head -30 \
  >> "$RT_DIR/rt_checks.txt"
# Must show actual UPDATE/INSERT logic, not a pass or TODO

# RT-2: CHECK constraint is REAL (not just documentation)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT pg_get_constraintdef(oid) FROM pg_constraint
   WHERE conrelid = 'zakops.deals'::regclass AND contype = 'c';" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must show actual constraint definition

# RT-3: Database trigger is REAL and fires
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT tgname, pg_get_triggerdef(oid) FROM pg_trigger
   WHERE tgrelid = 'zakops.deals'::regclass AND NOT tgisinternal;" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must show trigger definition with function body

# RT-4: audit_trail column has REAL data (not empty for all rows)
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT COUNT(*) AS rows_with_audit FROM zakops.deals
   WHERE audit_trail IS NOT NULL AND audit_trail != '[]'::jsonb;" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must be > 0 if any state transitions have occurred

# RT-5: Canonical stage config is REAL (not just a constant array that looks shared)
echo "--- RT-5: Stage config reality ---" >> "$RT_DIR/rt_checks.txt"
# Count how many files import from the canonical config
grep -rn "import.*stage.*config\|import.*pipeline.*config\|from.*stages" \
  "$DASHBOARD_ROOT/src/" --include="*.ts" --include="*.tsx" 2>/dev/null \
  | grep -v "node_modules" \
  >> "$RT_DIR/rt_checks.txt"
# Must be >= 4 (one per consuming page/component)

# RT-6: Server-side counting is REAL (not client-side with a different variable name)
echo "--- RT-6: Server-side counting reality ---" >> "$RT_DIR/rt_checks.txt"
grep -rn "pipeline/summary\|pipelineSummary\|server.*count\|api.*count" \
  "$DASHBOARD_ROOT/src/app/hq/page.tsx" \
  "$DASHBOARD_ROOT/src/app/dashboard/page.tsx" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must show API calls for counts, not local computation

# RT-7: Error boundaries are REAL React components (not empty wrappers)
echo "--- RT-7: Error boundary reality ---" >> "$RT_DIR/rt_checks.txt"
grep -A10 "class.*ErrorBoundary\|function.*ErrorBoundary\|ErrorBoundary" \
  "$DASHBOARD_ROOT/src/" -r --include="*.tsx" 2>/dev/null | head -30 \
  >> "$RT_DIR/rt_checks.txt"
# Must show componentDidCatch/getDerivedStateFromError or equivalent

# RT-8: Promise.allSettled results are ACTUALLY handled (not just awaited and ignored)
echo "--- RT-8: allSettled result handling ---" >> "$RT_DIR/rt_checks.txt"
grep -A5 "allSettled" "$DASHBOARD_ROOT/src/app/" -r --include="*.tsx" 2>/dev/null | head -40 \
  >> "$RT_DIR/rt_checks.txt"
# Must show status === 'fulfilled' / 'rejected' handling

# RT-9: DSN startup gate is REAL (not just logging)
echo "--- RT-9: DSN gate reality ---" >> "$RT_DIR/rt_checks.txt"
grep -A10 "DSN\|startup.*gate\|refuse.*start\|sys\.exit\|raise.*Exception" \
  "$BACKEND_ROOT/src/" -r --include="*.py" 2>/dev/null | head -30 \
  >> "$RT_DIR/rt_checks.txt"
# Must show actual exit/raise on mismatch, not just log.warning

# RT-10: Health endpoint DB identity fields are REAL (not hardcoded)
echo "--- RT-10: Health endpoint reality ---" >> "$RT_DIR/rt_checks.txt"
grep -A10 "health\|db_host\|db_port\|db_name" \
  "$BACKEND_ROOT/src/" -r --include="*.py" 2>/dev/null | head -30 \
  >> "$RT_DIR/rt_checks.txt"
# Must show dynamic DB connection info, not string literals

# RT-11: Performance baselines have REAL numbers (not placeholders)
echo "--- RT-11: Performance baseline reality ---" >> "$RT_DIR/rt_checks.txt"
find "$EVIDENCE_ROOT" -name "*performance*" -o -name "*baseline*" 2>/dev/null \
  | while read f; do
    echo "--- $f ---"
    grep -c "[0-9]\+ms\|[0-9]\+\..*ms\|Execution Time\|Planning Time" "$f" 2>/dev/null
  done >> "$RT_DIR/rt_checks.txt"
# Must show actual timing numbers

# RT-12: Tests have REAL assertions (not just function calls that always pass)
echo "--- RT-12: Test assertion reality ---" >> "$RT_DIR/rt_checks.txt"
find "$BACKEND_ROOT" "$MONOREPO" -name "test_*" -o -name "*_test.py" 2>/dev/null \
  | head -5 \
  | while read f; do
    echo "--- $f ---"
    grep -c "assert\|assertEqual\|expect\|should\|raise" "$f" 2>/dev/null
  done >> "$RT_DIR/rt_checks.txt"
# Must show real assertions, not empty test bodies

# RT-13: ADRs have REAL content (not templates with TODO)
echo "--- RT-13: ADR reality ---" >> "$RT_DIR/rt_checks.txt"
find "$MONOREPO" "$EVIDENCE_ROOT" -name "ADR-*" -o -name "adr-*" 2>/dev/null \
  | while read f; do
    echo "--- $f ---"
    wc -l "$f"
    grep -c "TODO\|TBD\|placeholder\|fill in" "$f" 2>/dev/null
  done >> "$RT_DIR/rt_checks.txt"
# Must show > 20 lines per ADR with 0 TODOs

# RT-14: Runbook is testable (has concrete commands/paths, not vague instructions)
echo "--- RT-14: Runbook testability ---" >> "$RT_DIR/rt_checks.txt"
RUNBOOK=$(find "$MONOREPO" "$EVIDENCE_ROOT" -name "*runbook*" 2>/dev/null | head -1)
test -n "$RUNBOOK" && grep -c "make \|npm \|curl \|psql \|\.ts\|\.py\|\.json" "$RUNBOOK" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must have concrete commands, not just prose

# RT-15: Innovation roadmap has 34 entries (not 10 with "etc.")
echo "--- RT-15: Innovation completeness ---" >> "$RT_DIR/rt_checks.txt"
ROADMAP=$(find "$MONOREPO" "$EVIDENCE_ROOT" -name "*innovation*" -o -name "*roadmap*" 2>/dev/null | head -1)
test -n "$ROADMAP" && grep -c "I-[0-9]" "$ROADMAP" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must be >= 34

# RT-16: make sync-all-types actually regenerates (not a passthrough)
echo "--- RT-16: sync-all-types reality ---" >> "$RT_DIR/rt_checks.txt"
grep -A10 "sync-all" "$MAKEFILE" 2>/dev/null | head -15 \
  >> "$RT_DIR/rt_checks.txt"
# Must show real sub-targets (sync-types, sync-agent-types, etc.)

# RT-17: Contract sync was actually run after Layer 3 (not just claimed) — DROP-C7
echo "--- RT-17: Contract sync evidence ---" >> "$RT_DIR/rt_checks.txt"
cd "$MONOREPO"
git log --oneline -10 -- "apps/dashboard/src/lib/api-types.generated.ts" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must show recent regeneration commit

# RT-18: Organizational root cause acknowledged (DROP-M4)
echo "--- RT-18: Org root cause ---" >> "$RT_DIR/rt_checks.txt"
grep -c "organizational\|four independent\|no coordination\|shared data semantics" \
  "$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/"*/completion-report.md \
  "$MONOREPO" -r --include="ADR-*" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Must be > 0 — the pattern is acknowledged somewhere

# RT-19: Column name accuracy verified (DROP-M5)
echo "--- RT-19: Column names ---" >> "$RT_DIR/rt_checks.txt"
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT column_name FROM information_schema.columns
   WHERE table_schema = 'zakops' AND table_name = 'deals' ORDER BY ordinal_position;" 2>/dev/null \
  >> "$RT_DIR/rt_checks.txt"
# Cross-reference with mission text's column references

# RT-20: 10 Q constraints formally answered (DROP-M3)
echo "--- RT-20: Q constraints ---" >> "$RT_DIR/rt_checks.txt"
for q in Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10; do
  echo "$q:"
  FOUND=$(grep -rn "$q\|Constraint.*${q#Q}" \
    "$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/"*/completion-report.md 2>/dev/null | wc -l)
  echo "  References in completion reports: $FOUND"
done >> "$RT_DIR/rt_checks.txt"
# Each Q must appear >= 1 time with evidence of satisfaction
```

| Gate | Check | Expected | Verdict |
|------|-------|----------|---------|
| RT-1 | Transition function is real code | actual SQL/logic, no stubs | |
| RT-2 | CHECK constraint is real | pg_get_constraintdef shows logic | |
| RT-3 | Trigger is real and fires | trigger definition with function | |
| RT-4 | audit_trail has real data | > 0 rows with entries | |
| RT-5 | Stage config imported by 4+ consumers | >= 4 import references | |
| RT-6 | Server-side counting via API calls | pipeline/summary calls found | |
| RT-7 | Error boundaries have real logic | componentDidCatch or equivalent | |
| RT-8 | allSettled results are handled | status check logic present | |
| RT-9 | DSN gate actually exits/raises on mismatch | sys.exit or raise found | |
| RT-10 | Health endpoint reads DB info dynamically | no hardcoded strings | |
| RT-11 | Performance baselines have real numbers | timing values present | |
| RT-12 | Tests have real assertions | assert/expect found | |
| RT-13 | ADRs have real content, 0 TODOs | > 20 lines, 0 TODO | |
| RT-14 | Runbook has concrete commands | make/npm/curl refs found | |
| RT-15 | Innovation roadmap: 34 entries | >= 34 I-XX references | |
| RT-16 | sync-all-types has real sub-targets | 4+ sync targets | |
| RT-17 | Contract sync has recent commit (DROP-C7) | recent regen commit | |
| RT-18 | Organizational root cause acknowledged (DROP-M4) | > 0 references | |
| RT-19 | Column names match DB reality (DROP-M5) | cross-reference passes | |
| RT-20 | All 10 Q constraints formally answered (DROP-M3) | each Q >= 1 reference | |

---

## SECTION 4: NEGATIVE CONTROLS (NC-0 through NC-8)

Each negative control sabotages one gate, verifies detection, then reverts.
**ALL 9 MUST PASS. No exceptions. No "test infrastructure needed."**

### NC HARNESS RULES (MANDATORY)

```
Every NC MUST follow this exact protocol:
  1. BEFORE sabotage: assert clean git tree (git status --porcelain == empty)
  2. Apply sabotage
  3. Run gate command — gate MUST fail (exit non-zero / explicit FAIL text)
  4. Revert via trap/restore — restore EXACT original state
  5. AFTER revert: assert clean git tree again
  6. Re-run gate command — gate MUST pass (positive path recovery)

If git tree is NOT clean before NC → FAIL (prior NC left residue)
If git tree is NOT clean after NC revert → FAIL (NC leaked sabotage)

Evidence: save sabotage diff + failing output + revert proof + passing output
```

```bash
NC_DIR="$EVIDENCE_ROOT/evidence/NC-negative-controls"

# Helper function
assert_clean() {
  local repo_dir="$1"
  local nc_name="$2"
  cd "$repo_dir"
  DIRTY=$(git status --porcelain 2>/dev/null | wc -l)
  if [ "$DIRTY" -gt 0 ]; then
    echo "INTEGRITY FAIL: $nc_name left dirty files after revert:" \
      >> "$NC_DIR/${nc_name}_integrity.txt"
    git status --porcelain >> "$NC_DIR/${nc_name}_integrity.txt"
    return 1
  fi
  echo "INTEGRITY PASS: $nc_name reverted cleanly" \
    >> "$NC_DIR/${nc_name}_integrity.txt"
  return 0
}

# ═══════════════════════════════════════════════
# NC-0: INTEGRITY HARNESS
# ═══════════════════════════════════════════════
echo "=== NC-0: INTEGRITY HARNESS ===" | tee "$NC_DIR/nc0_integrity.txt"
for repo in "$MONOREPO" "$BACKEND_ROOT" "$ZAKS_LLM_ROOT"; do
  cd "$repo"
  DIRTY=$(git status --porcelain 2>/dev/null | wc -l)
  echo "$(basename "$repo") dirty files: $DIRTY" >> "$NC_DIR/nc0_integrity.txt"
  git status --porcelain 2>/dev/null >> "$NC_DIR/nc0_integrity.txt"
done
# IF ANY TREE IS DIRTY → STOP. Clean first.

# ═══════════════════════════════════════════════
# NC-1: Lifecycle bypass — raw UPDATE without transition function
# Sabotage: directly UPDATE a deal's status without the trigger/constraint
# Gate: CHECK constraint or trigger must REJECT or auto-correct
# ═══════════════════════════════════════════════
echo "=== NC-1: LIFECYCLE BYPASS ===" | tee "$NC_DIR/nc1_lifecycle.txt"
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "BEGIN;
   UPDATE zakops.deals SET status = 'active', stage = 'archived' WHERE id = 1;
   ROLLBACK;" 2>&1 \
  | tee -a "$NC_DIR/nc1_lifecycle.txt"
# Must ERROR or auto-correct (impossible state rejected)

# ═══════════════════════════════════════════════
# NC-2: Contract drift — sabotage generated types
# Sabotage: append garbage to api-types.generated.ts
# Gate: make sync-types regenerates and obliterates sabotage
# ═══════════════════════════════════════════════
echo "=== NC-2: CONTRACT DRIFT ===" | tee "$NC_DIR/nc2_contract_drift.txt"
cd "$MONOREPO"
echo "// NC-2 SABOTAGE" >> "$DASHBOARD_ROOT/src/lib/api-types.generated.ts"
make sync-types 2>&1 > /dev/null
git diff --exit-code "$DASHBOARD_ROOT/src/lib/api-types.generated.ts" > /dev/null 2>&1
NC2_EXIT=$?
git checkout "$DASHBOARD_ROOT/src/lib/api-types.generated.ts" 2>/dev/null
assert_clean "$MONOREPO" "nc2"
echo "NC-2: exit=$NC2_EXIT (expect 0 = regen cleaned it)" >> "$NC_DIR/nc2_contract_drift.txt"

# ═══════════════════════════════════════════════
# NC-3: Hardcoded stage injection
# Sabotage: add a local PIPELINE_STAGES array to a dashboard page
# Gate: ESLint/TSC or canonical config check must catch it
# ═══════════════════════════════════════════════
echo "=== NC-3: HARDCODED STAGE INJECTION ===" | tee "$NC_DIR/nc3_hardcoded_stage.txt"
TEMP_FILE="$DASHBOARD_ROOT/src/components/qa-nc3-stage-test.tsx"
cat > "$TEMP_FILE" << 'STAGEEOF'
const PIPELINE_STAGES = ['prospecting', 'qualification', 'proposal'];
export default function NC3Test() { return <div>{PIPELINE_STAGES.join(',')}</div>; }
STAGEEOF
cd "$DASHBOARD_ROOT" && npx tsc --noEmit 2>&1 | tail -5 \
  >> "$NC_DIR/nc3_hardcoded_stage.txt"
rm -f "$TEMP_FILE"
assert_clean "$MONOREPO" "nc3"
echo "NC-3: Verify that lint/build process catches local stage arrays" \
  >> "$NC_DIR/nc3_hardcoded_stage.txt"

# ═══════════════════════════════════════════════
# NC-4: Promise.all regression
# Sabotage: replace Promise.allSettled with Promise.all in /hq
# Gate: ESLint or custom rule must catch it
# ═══════════════════════════════════════════════
echo "=== NC-4: PROMISE.ALL REGRESSION ===" | tee "$NC_DIR/nc4_promise_all.txt"
HQ_PAGE="$DASHBOARD_ROOT/src/app/hq/page.tsx"
if [ -f "$HQ_PAGE" ]; then
  cp "$HQ_PAGE" /tmp/qa-nc4-backup.tsx
  sed -i 's/Promise\.allSettled/Promise.all/g' "$HQ_PAGE"
  SABOTAGE_COUNT=$(grep -c "Promise\.all[^S]" "$HQ_PAGE" 2>/dev/null || echo 0)
  echo "Sabotaged: replaced allSettled with all ($SABOTAGE_COUNT instances)" \
    >> "$NC_DIR/nc4_promise_all.txt"
  # Check if lint catches it
  cd "$DASHBOARD_ROOT" && npx eslint "$HQ_PAGE" 2>&1 | tail -10 \
    >> "$NC_DIR/nc4_promise_all.txt"
  NC4_LINT=$?
  cp /tmp/qa-nc4-backup.tsx "$HQ_PAGE"
  assert_clean "$MONOREPO" "nc4"
  echo "NC-4: eslint exit=$NC4_LINT" >> "$NC_DIR/nc4_promise_all.txt"
fi

# ═══════════════════════════════════════════════
# NC-5: DSN sabotage
# Sabotage: change DATABASE_URL to point to port 5435
# Gate: startup DSN gate must refuse to start
# ═══════════════════════════════════════════════
echo "=== NC-5: DSN SABOTAGE ===" | tee "$NC_DIR/nc5_dsn.txt"
echo "Verify: builder implemented DSN startup gate (V-L1.9)" >> "$NC_DIR/nc5_dsn.txt"
echo "If gate exists: temporarily set DSN to port 5435 → service must refuse to start" \
  >> "$NC_DIR/nc5_dsn.txt"
echo "This NC requires a running backend and is verified via V-L1.9 evidence" \
  >> "$NC_DIR/nc5_dsn.txt"

# ═══════════════════════════════════════════════
# NC-6: Count invariant sabotage
# Sabotage: insert a deal with impossible state directly into DB
# Gate: CHECK constraint must reject it
# ═══════════════════════════════════════════════
echo "=== NC-6: COUNT INVARIANT SABOTAGE ===" | tee "$NC_DIR/nc6_invariant.txt"
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "INSERT INTO zakops.deals (status, stage, deleted)
   VALUES ('active', 'archived', false);" 2>&1 \
  | tee -a "$NC_DIR/nc6_invariant.txt"
# Must be REJECTED by CHECK constraint
# (No revert needed — the INSERT should fail)

# ═══════════════════════════════════════════════
# NC-7: Agent type drift
# Sabotage: append garbage to agent-api-types.generated.ts
# Gate: make sync-agent-types regenerates
# ═══════════════════════════════════════════════
echo "=== NC-7: AGENT TYPE DRIFT ===" | tee "$NC_DIR/nc7_agent_drift.txt"
cd "$MONOREPO"
echo "// NC-7 SABOTAGE" >> "$DASHBOARD_ROOT/src/lib/agent-api-types.generated.ts"
make sync-agent-types 2>&1 > /dev/null
git diff --exit-code "$DASHBOARD_ROOT/src/lib/agent-api-types.generated.ts" > /dev/null 2>&1
NC7_EXIT=$?
git checkout "$DASHBOARD_ROOT/src/lib/agent-api-types.generated.ts" 2>/dev/null
assert_clean "$MONOREPO" "nc7"
echo "NC-7: exit=$NC7_EXIT (expect 0 = regen cleaned it)" >> "$NC_DIR/nc7_agent_drift.txt"

# ═══════════════════════════════════════════════
# NC-8: Migration file sabotage
# Sabotage: add a fake migration file
# Gate: migration assertion or git detects it
# ═══════════════════════════════════════════════
echo "=== NC-8: MIGRATION SABOTAGE ===" | tee "$NC_DIR/nc8_migration.txt"
MIGRATION_DIR=$(find "$AGENT_API_ROOT" -type d -name "migrations" 2>/dev/null | head -1)
if [ -n "$MIGRATION_DIR" ]; then
  FAKE="$MIGRATION_DIR/999_nc8_fake.sql"
  echo "-- NC-8 SABOTAGE" > "$FAKE"
  git status --porcelain "$MIGRATION_DIR" >> "$NC_DIR/nc8_migration.txt"
  rm -f "$FAKE"
  assert_clean "$MONOREPO" "nc8"
  echo "NC-8: fake migration detected via git status, reverted cleanly" \
    >> "$NC_DIR/nc8_migration.txt"
fi
```

| # | Test | Sabotage | Expected Detection | Verdict |
|---|------|----------|-------------------|---------|
| NC-0 | **Integrity harness** | N/A (pre-check) | All git trees clean | **MUST PASS** |
| NC-1 | Lifecycle bypass | raw UPDATE impossible state | CHECK/trigger rejects | **MUST PASS** |
| NC-2 | Contract drift (backend types) | `echo >> api-types.generated.ts` | sync-types regenerates | **MUST PASS** |
| NC-3 | Hardcoded stage injection | local PIPELINE_STAGES array | lint/build catches | **MUST PASS** |
| NC-4 | Promise.all regression | replace allSettled → all | ESLint or rule catches | **MUST PASS** |
| NC-5 | DSN sabotage | point to port 5435 | startup gate refuses | **MUST PASS** |
| NC-6 | Count invariant sabotage | INSERT impossible state | CHECK constraint rejects | **MUST PASS** |
| NC-7 | Agent type drift | `echo >> agent-api-types.generated.ts` | sync-agent-types regenerates | **MUST PASS** |
| NC-8 | Migration file sabotage | add fake .sql | git/assertion detects | **MUST PASS** |

**ALL 9 MUST PASS. NC-0 failure = STOP (environment not trustworthy).**

---

## SECTION 5: CROSS-REFERENCE DROPS VERIFICATION

This section verifies that every item identified as dropped in the cross-reference audit has been addressed by the builder.

```bash
DROPS_DIR="$EVIDENCE_ROOT/evidence/D-drops-audit"

# DROP-C1: DI-ISSUE-001 specific integration tests
echo "=== DROP-C1: DI-ISSUE-001 Tests ===" | tee "$DROPS_DIR/drop_c1.txt"
# Search for the 2 specific test cases:
# (a) After archive, GET /deals?status=active must NOT return the deal
# (b) After archive, GET /deals?status=archived MUST return the deal
grep -rn "status.*active.*not.*return\|status.*archived.*must.*return\|archive.*disappear\|archive.*appear" \
  "$BACKEND_ROOT" "$MONOREPO" --include="*test*" 2>/dev/null \
  | tee -a "$DROPS_DIR/drop_c1.txt"
# If 0 matches → REMEDIATE

# DROP-C2: DealBoard dual data-fetching path
echo "=== DROP-C2: Dual Fetch Path ===" | tee "$DROPS_DIR/drop_c2.txt"
echo "api-client.ts path:" >> "$DROPS_DIR/drop_c2.txt"
grep -n "useDeals\|api-client" "$DASHBOARD_ROOT/src/components/DealBoard.tsx" 2>/dev/null \
  >> "$DROPS_DIR/drop_c2.txt"
echo "api.ts path:" >> "$DROPS_DIR/drop_c2.txt"
grep -n "getDeals\|from.*api" "$DASHBOARD_ROOT/src/app/deals/page.tsx" 2>/dev/null \
  >> "$DROPS_DIR/drop_c2.txt"
echo "Both paths must have error handling (allSettled or try/catch)" >> "$DROPS_DIR/drop_c2.txt"

# DROP-C3/C4/C5/C6: PG gaps explicitly verified in gates
echo "=== DROP-C3-C6: PG Gaps in Gates ===" | tee "$DROPS_DIR/drop_c3_c6.txt"
echo "PG-001 (/dashboard Promise.all): Checked in V-L4.3" >> "$DROPS_DIR/drop_c3_c6.txt"
echo "PG-002 (/dashboard STAGE_ORDER): Checked in V-L3.3" >> "$DROPS_DIR/drop_c3_c6.txt"
echo "PG-006 (/deals STATUSES missing archived): Checked in V-L3.5" >> "$DROPS_DIR/drop_c3_c6.txt"
echo "PG-007 (/actions Promise.all): Checked in V-L4.5" >> "$DROPS_DIR/drop_c3_c6.txt"
echo "Verify: each gate has explicit evidence pointing to the PG gap ID" >> "$DROPS_DIR/drop_c3_c6.txt"

# DROP-C7: make sync-all-types as mandatory gate in every layer
echo "=== DROP-C7: Sync Gate Coverage ===" | tee "$DROPS_DIR/drop_c7.txt"
for i in 1 2 3 4 5 6; do
  REPORT="$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/layer-$i/completion-report.md"
  SYNC_REF=$(grep -c "sync-all-types\|sync-types\|sync-agent\|sync-backend\|sync-rag" "$REPORT" 2>/dev/null || echo 0)
  echo "Layer $i: $SYNC_REF sync references in completion report"
done >> "$DROPS_DIR/drop_c7.txt"
# Layers that change API shapes (2, 3, 4) MUST have sync references

# DROP-M1: Operator decision rationale in ADRs
echo "=== DROP-M1: Decision Rationale ===" | tee "$DROPS_DIR/drop_m1.txt"
find "$MONOREPO" "$EVIDENCE_ROOT" -name "ADR-*" -o -name "adr-*" 2>/dev/null \
  | while read f; do
    echo "--- $f ---"
    grep -c "Option A\|Option B\|Option C\|Decision 1\|Decision 2\|Decision 3\|Decision 4\|alternative\|considered" "$f" 2>/dev/null
  done >> "$DROPS_DIR/drop_m1.txt"
# ADR-001 must discuss all 3 options

# DROP-M2: 34 innovation ideas catalogued
echo "=== DROP-M2: Innovation Catalogue ===" | tee "$DROPS_DIR/drop_m2.txt"
ROADMAP=$(find "$MONOREPO" "$EVIDENCE_ROOT" -name "*innovation*" -o -name "*roadmap*" 2>/dev/null | head -1)
if [ -n "$ROADMAP" ]; then
  for i in $(seq -w 1 34); do
    grep -q "I-$i\|I-0*$i" "$ROADMAP" 2>/dev/null \
      && echo "OK: I-$i" || echo "MISSING: I-$i"
  done >> "$DROPS_DIR/drop_m2.txt"
else
  echo "FAIL: No innovation roadmap found" >> "$DROPS_DIR/drop_m2.txt"
fi

# DROP-M3: 10 Q constraints formally answered
echo "=== DROP-M3: Q Constraints Answered ===" | tee "$DROPS_DIR/drop_m3.txt"
for q in Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10; do
  echo "$q:"
  grep -rn "$q" "$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/"*/completion-report.md 2>/dev/null | head -2
  echo "---"
done >> "$DROPS_DIR/drop_m3.txt"

# DROP-M4: Organizational root cause explicit
echo "=== DROP-M4: Org Root Cause ===" | tee "$DROPS_DIR/drop_m4.txt"
grep -rn "organizational\|four independent\|no coordination\|shared.*semantics\|root.*cause.*pattern" \
  "$EVIDENCE_ROOT/../DEAL-INTEGRITY-UNIFIED/" 2>/dev/null \
  | tee -a "$DROPS_DIR/drop_m4.txt"

# DROP-M5: Column name accuracy
echo "=== DROP-M5: Column Names ===" | tee "$DROPS_DIR/drop_m5.txt"
# Get actual columns from DB
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c \
  "SELECT column_name FROM information_schema.columns
   WHERE table_schema = 'zakops' AND table_name = 'deals'
   ORDER BY ordinal_position;" 2>/dev/null \
  >> "$DROPS_DIR/drop_m5.txt"
# Cross-reference with mission text references to 'status', 'stage', 'deleted', 'audit_trail'

# DROP-L2: Industry best practice scorecard
echo "=== DROP-L2: Scorecard ===" | tee "$DROPS_DIR/drop_l2.txt"
find "$EVIDENCE_ROOT" "$MONOREPO" -name "*scorecard*" -o -name "*best.practice*" 2>/dev/null \
  | tee -a "$DROPS_DIR/drop_l2.txt"
echo "MEDIUM: Scorecard is nice-to-have for measuring world-class claim" >> "$DROPS_DIR/drop_l2.txt"

# DROP-L3: Dashboard page coverage matrix
echo "=== DROP-L3: Coverage Matrix ===" | tee "$DROPS_DIR/drop_l3.txt"
find "$EVIDENCE_ROOT" "$MONOREPO" -name "*coverage*matrix*" -o -name "*page.*coverage*" 2>/dev/null \
  | tee -a "$DROPS_DIR/drop_l3.txt"
echo "LOW: Coverage matrix useful for tracking but not a gate" >> "$DROPS_DIR/drop_l3.txt"
```

---

## SECTION 6: DB SOURCE-OF-TRUTH PROOF (MANDATORY)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  PROVE EACH SERVICE TALKS TO THE CORRECT DATABASE                          ║
║                                                                              ║
║  "It worked but on the wrong DB" is a real failure mode.                   ║
║  DEAL-INTEGRITY-001 ROOT-B was literally this problem.                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

```bash
DB_SOT_DIR="$EVIDENCE_ROOT/evidence/FINAL-verification"
echo "=== DB SOURCE-OF-TRUTH ASSERTION ===" | tee "$DB_SOT_DIR/db_sot_assertion.txt"

# Step 1: Running DB containers
docker ps --filter "ancestor=postgres" --format "{{.Names}} {{.Ports}}" 2>/dev/null \
  | tee -a "$DB_SOT_DIR/db_sot_assertion.txt"
# Must show exactly 1 Postgres container

# Step 2: Service DSN verification
echo "" >> "$DB_SOT_DIR/db_sot_assertion.txt"
echo "--- Backend API DATABASE_URL ---" >> "$DB_SOT_DIR/db_sot_assertion.txt"
docker exec zakops-backend-backend-1 printenv DATABASE_URL 2>/dev/null \
  | sed 's/:[^:@]*@/:***@/' \
  >> "$DB_SOT_DIR/db_sot_assertion.txt"

echo "--- Agent API DATABASE_URL ---" >> "$DB_SOT_DIR/db_sot_assertion.txt"
grep "DATABASE_URL" "$AGENT_API_ROOT/.env" 2>/dev/null \
  | sed 's/:[^:@]*@/:***@/' \
  >> "$DB_SOT_DIR/db_sot_assertion.txt"

echo "--- RAG/LLM DATABASE_URL ---" >> "$DB_SOT_DIR/db_sot_assertion.txt"
grep "DATABASE_URL" "$ZAKS_LLM_ROOT/.env" 2>/dev/null \
  | sed 's/:[^:@]*@/:***@/' \
  >> "$DB_SOT_DIR/db_sot_assertion.txt"

# Step 3: Live SQL identity queries
echo "" >> "$DB_SOT_DIR/db_sot_assertion.txt"
for db in zakops zakops_agent crawlrag; do
  echo "=== $db ===" >> "$DB_SOT_DIR/db_sot_assertion.txt"
  docker exec zakops-backend-postgres-1 psql -U postgres -d "$db" -c "
    SELECT current_database() AS db_name, current_schema() AS schema;
    SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename LIMIT 5;
  " 2>&1 >> "$DB_SOT_DIR/db_sot_assertion.txt" \
    || echo "$db: connection FAILED" >> "$DB_SOT_DIR/db_sot_assertion.txt"
done

# Step 4: Verify NO service points to 5435
echo "" >> "$DB_SOT_DIR/db_sot_assertion.txt"
echo "--- Port 5435 References (must be ZERO) ---" >> "$DB_SOT_DIR/db_sot_assertion.txt"
grep -rn "5435" "$BACKEND_ROOT/.env" "$AGENT_API_ROOT/.env" "$ZAKS_LLM_ROOT/.env" 2>/dev/null \
  >> "$DB_SOT_DIR/db_sot_assertion.txt" || echo "PASS: No 5435 references" \
  >> "$DB_SOT_DIR/db_sot_assertion.txt"
```

---

## SECTION 7: FINAL VERIFICATION

After ALL sections above are complete:

```bash
FINAL_DIR="$EVIDENCE_ROOT/evidence/FINAL-verification"

echo "=== FINAL VERIFICATION ===" | tee "$FINAL_DIR/final_report.txt"

# 1. make validate-local — must pass
cd "$MONOREPO"
make validate-local 2>&1 | tee "$FINAL_DIR/validate_local_final.log"
echo "Exit: $?" >> "$FINAL_DIR/validate_local_final.log"

# 2. All DI-ISSUEs resolved
echo "--- DI-ISSUE Resolution ---" >> "$FINAL_DIR/final_report.txt"
for issue in DI-ISSUE-001 DI-ISSUE-002 DI-ISSUE-003 DI-ISSUE-004 DI-ISSUE-005 \
  DI-ISSUE-006 DI-ISSUE-007 DI-ISSUE-008 DI-ISSUE-009; do
  echo "$issue: [PASS/FAIL — fill with evidence reference]"
done >> "$FINAL_DIR/final_report.txt"

# 3. All PG gaps resolved
echo "--- PG Gap Resolution ---" >> "$FINAL_DIR/final_report.txt"
for pg in PG-001 PG-002 PG-003 PG-004 PG-005 PG-006 PG-007 PG-008 PG-009; do
  echo "$pg: [PASS/FAIL — fill with evidence reference]"
done >> "$FINAL_DIR/final_report.txt"

# 4. All CS gaps resolved
echo "--- CS Gap Resolution ---" >> "$FINAL_DIR/final_report.txt"
for cs in CS-001 CS-002 CS-003 CS-004 CS-005; do
  echo "$cs: [PASS/FAIL — fill with evidence reference]"
done >> "$FINAL_DIR/final_report.txt"

# 5. All Q constraints satisfied
echo "--- Q Constraint Satisfaction ---" >> "$FINAL_DIR/final_report.txt"
for q in Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 Q10; do
  echo "$q: [PASS/FAIL — fill with gate reference]"
done >> "$FINAL_DIR/final_report.txt"

# 6. All DROP items addressed
echo "--- Cross-Reference Drops ---" >> "$FINAL_DIR/final_report.txt"
for drop in DROP-C1 DROP-C2 DROP-C3 DROP-C4 DROP-C5 DROP-C6 DROP-C7 \
  DROP-M1 DROP-M2 DROP-M3 DROP-M4 DROP-M5 DROP-M6 DROP-L1 DROP-L2 DROP-L3; do
  echo "$drop: [ADDRESSED/REMEDIATED/ACCEPTED-LOW — fill with evidence]"
done >> "$FINAL_DIR/final_report.txt"

# 7. World-class criteria checklist
echo "--- World-Class Criteria ---" >> "$FINAL_DIR/final_report.txt"
cat << 'CRITERIA' >> "$FINAL_DIR/final_report.txt"
[ ] Single canonical DB truth
[ ] Full lifecycle state machine
[ ] All surfaces show same counts
[ ] Agent API + RAG + Contracts included
[ ] Defensive UI architecture
[ ] CI gates + regression tests
[ ] Observability with alerts and invariant monitors
[ ] Governance with ADRs and runbooks
[ ] Performance baselined
[ ] Concurrency safe
[ ] Backfill reversible
[ ] Contract sync enforced
[ ] Zero hardcoded stage lists
[ ] Zero Zod errors under any failure scenario
[ ] Innovation roadmap catalogued
CRITERIA

# 8. Gate summary count
echo "" >> "$FINAL_DIR/final_report.txt"
echo "=== GATE SUMMARY ===" >> "$FINAL_DIR/final_report.txt"
echo "Layer 1: 10 gates" >> "$FINAL_DIR/final_report.txt"
echo "Layer 2: 16 gates" >> "$FINAL_DIR/final_report.txt"
echo "Layer 3: 12 gates" >> "$FINAL_DIR/final_report.txt"
echo "Layer 4: 11 gates" >> "$FINAL_DIR/final_report.txt"
echo "Layer 5: 12 gates" >> "$FINAL_DIR/final_report.txt"
echo "Layer 6:  7 gates" >> "$FINAL_DIR/final_report.txt"
echo "Red-Team: 20 gates" >> "$FINAL_DIR/final_report.txt"
echo "Negative Controls: 9 tests" >> "$FINAL_DIR/final_report.txt"
echo "Drop Verifications: 16 items" >> "$FINAL_DIR/final_report.txt"
echo "TOTAL: 113 verification points" >> "$FINAL_DIR/final_report.txt"
echo "" >> "$FINAL_DIR/final_report.txt"
echo "VERDICT: [PASS / FAIL]" >> "$FINAL_DIR/final_report.txt"
```

---

## REMEDIATION PROTOCOL

When a gate FAILS, the auditor follows this protocol:

1. **Document the failure** in `evidence/R-remediation/` with: gate ID, expected result, actual result, root cause
2. **Fix the issue** — the auditor has FULL EXECUTION authority. No separate remediation mission.
3. **Re-run the gate** — the fix must cause the gate to PASS
4. **Document the remediation** — before/after evidence, what was changed
5. **Re-run `make validate-local`** — no regressions from the fix
6. **Update the gate verdict** from FAIL → PASS (REMEDIATED)

Remediation is NOT optional. A gate that fails and is not remediated = MISSION FAIL.

---

## PIPELINE MASTER LOG ENTRY

Upon QA completion, append to `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_PIPELINE_MASTER_LOG.md`:

```
[TIMESTAMP] | QA-DI-VERIFY-UNIFIED COMPLETE | Agent=[agent] | RunID=[id] | STATUS=[PASS/FAIL] | 113 verification points | [N] gates PASS | [N] gates REMEDIATED | [N] gates FAIL | [N] NCs PASS | [N] drops addressed | Report=/home/zaks/bookkeeping/qa-verifications/QA-DI-VERIFY-UNIFIED/evidence/FINAL-verification/final_report.txt
```

---

**END OF QA VERIFICATION + REMEDIATION MISSION**

**One Sentence:** The builder claims a world-class platform — this QA mission independently verifies every claim, every gate, every invariant, and remediates every failure in place, with zero tolerance for conditional passes.
