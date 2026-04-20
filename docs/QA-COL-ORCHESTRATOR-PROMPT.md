# QA Verification & Remediation Mission Registry — COL-V2 (Spec-Level Depth)
**Source:** COL-ORCHESTRATOR-PROMPT.md
**Spec:** `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` (3,276 lines)
**Standard:** MISSION-PROMPT-STANDARD.md (v2.2)
**Date:** 2026-02-13
**Missions:** 19 (QA-COL-M01 through QA-COL-M19)
**Depth:** Spec-level — every gate checks a specific assertion from the design spec

---

## Common Reference: Remediation Protocol

All 19 QA missions use this remediation protocol. Each mission references it by name.

1. Read the evidence file for the failing gate
2. Classify the failure:
   - **MISSING_FILE** — Expected artifact does not exist on disk
   - **MISSING_CONTENT** — File exists but lacks required class, function, table, or pattern
   - **WRONG_TYPE** — Column/parameter type does not match spec (e.g., INTEGER instead of VARCHAR)
   - **WRONG_CONSTRAINT** — Missing CHECK, UNIQUE, FK, DEFAULT, or other constraint
   - **WRONG_SIGNATURE** — Method/function signature does not match spec (parameters, return type)
   - **REGRESSION** — Previously working functionality broken by this mission's changes
   - **SCOPE_GAP** — Spec requirement not addressed by the Builder
   - **FALSE_POSITIVE** — Gate check is wrong or overly strict; mark as INFO
   - **PARTIAL** — Implementation started but incomplete
   - **WIRING_FAILURE** — Artifact exists but not integrated (missing import, unused class)
3. Apply fix following original mission's architectural constraints (per standing rules)
4. Re-run the specific failing gate
5. Re-run `make validate-local` from `/home/zaks/zakops-agent-api`
6. Record remediation in the completion report: gate ID, classification, fix applied, re-verify result

## Common Reference: Evidence Directory

Each mission stores evidence in: `/home/zaks/bookkeeping/docs/_qa_evidence/col-mXX/`
Create the directory in PF-2. All `tee` commands write to this directory.

## Common Reference: Guardrails (apply to ALL 19 missions)

1. **No feature building** — this is QA verification, not implementation
2. **Remediate, don't redesign** — fix what's broken per the spec, don't invent new patterns
3. **Evidence-based only** — every PASS needs `tee`'d output in the evidence directory
4. **Read-only by default** — only write files during remediation of FAIL gates
5. **Services-down accommodation** — if services aren't running, live gates become SKIP (not FAIL)
6. **Preserve prior work** — remediation must not revert earlier mission deliverables
7. **WSL safety** — `sed -i 's/\r$//'` on any .sh files touched; `sudo chown zaks:zaks` on created files
8. **Per standing rules** — CLAUDE.md, MEMORY.md, hooks, deny rules, 14 contract surfaces all apply

---

# MISSION: QA-COL-M01-VERIFY-001
## QA Verification: Canonical Chat Store Schema (Migration 004)
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M01-STORAGE-SCHEMA (Execution complete)
## Successor: QA-COL-M02-VERIFY-001

## Mission Objective

Spec-level verification of **Migration 004** — the canonical chat store schema in `zakops_agent`.
Every column name, type, default, constraint, index, function, and trigger is checked against COL-DESIGN-SPEC-V2.md S3.2–S3.3 (lines 210–566).

**Source spec:** S3.2 (user_identity_map), S3.3 (Migration 004 DDL)
**Tables:** user_identity_map, chat_threads, chat_messages, thread_ownership, session_summaries, turn_snapshots, cost_ledger, deal_budgets, cross_db_outbox
**Partitions:** turn_snapshots_default, cost_ledger_default
**View:** deal_cost_summary
**Functions:** update_thread_message_count(), create_monthly_partitions()
**Trigger:** trg_message_count
**Rollback:** 004_chat_canonical_store_rollback.sql

## Context

Migration 004 is the foundation for the entire COL system. Every subsequent mission depends on these tables. The spec defines exact column types (VARCHAR(255) for user_id per GAP-C2), exact CHECK constraints, exact partition schemes, and exact rollback ordering.

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/pf1-validate.txt
```
**PASS if:** exit 0.

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m01 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/pf2-dir.txt
```
**PASS if:** Directory exists.

### PF-3: Migration File Location
```bash
MIGRATION=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "004_chat_canonical_store.sql" -type f 2>/dev/null) && echo "FOUND: $MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/pf3-migration.txt
```
**PASS if:** Exactly one file path returned. Set `$MIGRATION` for subsequent gates.

---

## Verification Families

## VF-01 — Migration File Existence & Structure

### VF-01.1: Forward Migration Exists
```bash
test -f "$MIGRATION" && echo "PASS" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf01-1.txt
```

### VF-01.2: Rollback Migration Exists
```bash
ROLLBACK=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "004_chat_canonical_store_rollback.sql" -type f 2>/dev/null) && echo "FOUND: $ROLLBACK" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf01-2.txt
```

### VF-01.3: Migration Tracking (GAP-M3)
```bash
grep -c "INSERT INTO schema_migrations" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf01-3.txt
```
**PASS if:** count >= 1. Spec requires `INSERT INTO schema_migrations (version, description, applied_at) VALUES ('004', ...)`.

### VF-01.4: Transaction Wrapping
```bash
{ grep -c "^BEGIN;" "$MIGRATION"; grep -c "^COMMIT;" "$MIGRATION"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf01-4.txt
```
**PASS if:** Both counts >= 1. Migration must be wrapped in a transaction.

**Gate VF-01:** 4/4 checks pass.

## VF-02 — user_identity_map Table (S3.2, 8 columns)

### VF-02.1: Table Created
```bash
grep -c "CREATE TABLE.*user_identity_map" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-1.txt
```

### VF-02.2: canonical_id VARCHAR(255) PRIMARY KEY
```bash
grep -A2 "user_identity_map" "$MIGRATION" | grep -c "canonical_id.*VARCHAR(255).*PRIMARY KEY" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-2.txt
```

### VF-02.3: email VARCHAR(255) UNIQUE
```bash
grep "email.*VARCHAR(255).*UNIQUE" "$MIGRATION" | head -1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-3.txt
```
**PASS if:** Line found containing `email` with `VARCHAR(255)` and `UNIQUE`.

### VF-02.4: auth_provider VARCHAR(50) DEFAULT 'local'
```bash
grep "auth_provider.*VARCHAR(50).*DEFAULT.*local" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-4.txt
```

### VF-02.5: external_ids JSONB DEFAULT '{}'
```bash
grep "external_ids.*JSONB.*DEFAULT" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-5.txt
```

### VF-02.6: role VARCHAR(20) DEFAULT 'VIEWER'
```bash
grep "role.*VARCHAR(20).*DEFAULT.*VIEWER" "$MIGRATION" | head -1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-6.txt
```

### VF-02.7: CHECK constraint on role — exact values
```bash
grep "chk_role.*CHECK.*role.*IN.*VIEWER.*OPERATOR.*APPROVER.*ADMIN" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-7.txt
```
**PASS if:** CHECK constraint lists exactly 4 roles: VIEWER, OPERATOR, APPROVER, ADMIN.

### VF-02.8: Timestamp columns
```bash
{ grep "created_at.*TIMESTAMPTZ.*DEFAULT.*NOW" "$MIGRATION" | head -1; grep "last_seen.*TIMESTAMPTZ.*DEFAULT.*NOW" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf02-8.txt
```
**PASS if:** Both `created_at` and `last_seen` are TIMESTAMPTZ with DEFAULT NOW().

**Gate VF-02:** 8/8 checks pass. All 8 user_identity_map columns verified per S3.2.

## VF-03 — chat_threads Table (S3.3, 17 columns + 4 indexes + 2 CHECK constraints)

### VF-03.1: Table Created
```bash
grep -c "CREATE TABLE.*chat_threads" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-1.txt
```

### VF-03.2: id VARCHAR(255) PRIMARY KEY
```bash
grep -A1 "chat_threads" "$MIGRATION" | grep "id.*VARCHAR(255).*PRIMARY KEY" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-2.txt
```

### VF-03.3: user_id VARCHAR(255) NOT NULL (GAP-C2)
```bash
grep "user_id.*VARCHAR(255).*NOT NULL" "$MIGRATION" | head -1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-3.txt
```
**PASS if:** user_id is VARCHAR(255), NOT INTEGER. This is the GAP-C2 fix.

### VF-03.4: deal_id VARCHAR(20) nullable
```bash
grep "deal_id.*VARCHAR(20)" "$MIGRATION" | head -1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-4.txt
```
**PASS if:** deal_id is VARCHAR(20) without NOT NULL (nullable by default).

### VF-03.5: scope_type with CHECK constraint
```bash
grep "scope_type.*VARCHAR(20).*NOT NULL.*DEFAULT.*global" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-5.txt
```

### VF-03.6: scope CHECK allows exactly global/deal/document
```bash
grep "chk_scope.*CHECK.*scope_type.*IN.*global.*deal.*document" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-6.txt
```

### VF-03.7: title VARCHAR(500)
```bash
grep "title.*VARCHAR(500)" "$MIGRATION" | head -1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-7.txt
```

### VF-03.8: Boolean flags — pinned, archived, deleted DEFAULT FALSE
```bash
{ grep "pinned.*BOOLEAN.*DEFAULT FALSE" "$MIGRATION" | head -1; grep "archived.*BOOLEAN.*DEFAULT FALSE" "$MIGRATION" | head -1; grep "deleted.*BOOLEAN.*DEFAULT FALSE" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-8.txt
```
**PASS if:** All 3 boolean flags present with DEFAULT FALSE.

### VF-03.9: Legal hold columns
```bash
{ grep "legal_hold .*BOOLEAN.*DEFAULT FALSE" "$MIGRATION" | head -1; grep "legal_hold_reason.*TEXT" "$MIGRATION" | head -1; grep "legal_hold_set_by.*VARCHAR(255)" "$MIGRATION" | head -1; grep "legal_hold_set_at.*TIMESTAMPTZ" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-9.txt
```
**PASS if:** All 4 legal hold columns present with correct types.

### VF-03.10: compliance_tier BOOLEAN DEFAULT FALSE
```bash
grep "compliance_tier.*BOOLEAN.*DEFAULT FALSE" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-10.txt
```

### VF-03.11: message_count INTEGER DEFAULT 0
```bash
grep "message_count.*INTEGER.*DEFAULT 0" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-11.txt
```

### VF-03.12: last_summary_version INTEGER DEFAULT 0
```bash
grep "last_summary_version.*INTEGER.*DEFAULT 0" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-12.txt
```

### VF-03.13: Deleted consistency CHECK constraint
```bash
grep "chk_delete.*CHECK" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-13.txt
```
**PASS if:** CHECK ensures (deleted=FALSE AND deleted_at IS NULL) OR (deleted=TRUE AND deleted_at IS NOT NULL).

### VF-03.14: 4 Indexes on chat_threads
```bash
{ grep "idx_threads_user" "$MIGRATION"; grep "idx_threads_deal" "$MIGRATION"; grep "idx_threads_active" "$MIGRATION"; grep "idx_threads_deleted" "$MIGRATION"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-14.txt
```
**PASS if:** All 4 index names found: idx_threads_user, idx_threads_deal, idx_threads_active, idx_threads_deleted.

### VF-03.15: Conditional index — deal WHERE deal_id IS NOT NULL
```bash
grep "idx_threads_deal.*WHERE deal_id IS NOT NULL" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-15.txt
```
**PASS if:** Partial index filters to non-null deal_id only.

### VF-03.16: Active threads index — composite (user_id, last_active DESC) WHERE deleted=FALSE
```bash
grep "idx_threads_active.*user_id.*last_active DESC.*WHERE deleted = FALSE" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf03-16.txt
```

**Gate VF-03:** 16/16 checks pass. All 17 columns, 4 indexes, and 2 CHECK constraints verified per S3.3.

## VF-04 — chat_messages Table (S3.3, 14 columns + 2 indexes + 2 constraints)

### VF-04.1: Table Created
```bash
grep -c "CREATE TABLE.*chat_messages" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-1.txt
```

### VF-04.2: id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()
```bash
grep "id.*VARCHAR(36).*PRIMARY KEY.*DEFAULT.*gen_random_uuid" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-2.txt
```

### VF-04.3: thread_id FK with ON DELETE CASCADE
```bash
grep "thread_id.*VARCHAR(255).*REFERENCES chat_threads.*ON DELETE CASCADE" "$MIGRATION" | head -1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-3.txt
```
**PASS if:** FK to chat_threads with CASCADE delete.

### VF-04.4: deal_id NOT present (GAP-M1 — removed as redundant)
```bash
grep -A20 "CREATE TABLE.*chat_messages" "$MIGRATION" | grep -v "^--" | grep "deal_id" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-4.txt
```
**PASS if:** No deal_id column in chat_messages (derivable from thread.deal_id per GAP-M1).

### VF-04.5: role VARCHAR(20) with CHECK constraint
```bash
grep -A20 "CREATE TABLE.*chat_messages" "$MIGRATION" | grep "chk_role.*CHECK.*role.*IN.*user.*assistant.*system.*tool" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-5.txt
```
**PASS if:** CHECK allows exactly: user, assistant, system, tool.

### VF-04.6: content TEXT NOT NULL
```bash
grep -A15 "CREATE TABLE.*chat_messages" "$MIGRATION" | grep "content.*TEXT.*NOT NULL" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-6.txt
```

### VF-04.7: JSONB columns — citations, proposals, evidence_summary
```bash
{ grep "citations.*JSONB.*DEFAULT" "$MIGRATION" | head -1; grep "proposals.*JSONB.*DEFAULT" "$MIGRATION" | head -1; grep "evidence_summary.*JSONB" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-7.txt
```
**PASS if:** All 3 JSONB columns present.

### VF-04.8: turn_number with UNIQUE(thread_id, turn_number) (GAP-M2)
```bash
grep "uq_thread_turn.*UNIQUE.*thread_id.*turn_number" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-8.txt
```
**PASS if:** UNIQUE constraint on (thread_id, turn_number) per GAP-M2.

### VF-04.9: 2 Indexes on chat_messages
```bash
{ grep "idx_messages_thread" "$MIGRATION"; grep "idx_messages_user" "$MIGRATION"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf04-9.txt
```

**Gate VF-04:** 9/9 checks pass.

## VF-05 — thread_ownership Table (S3.3, 4 columns + 2 indexes)

### VF-05.1: Table Created with thread_id PK + FK CASCADE
```bash
grep -A3 "CREATE TABLE.*thread_ownership" "$MIGRATION" | grep "thread_id.*VARCHAR(255).*PRIMARY KEY" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf05-1.txt
```

### VF-05.2: FK references chat_threads with ON DELETE CASCADE
```bash
grep -A5 "CREATE TABLE.*thread_ownership" "$MIGRATION" | grep "REFERENCES chat_threads.*ON DELETE CASCADE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf05-2.txt
```

### VF-05.3: user_id VARCHAR(255) NOT NULL
```bash
grep -A5 "CREATE TABLE.*thread_ownership" "$MIGRATION" | grep "user_id.*VARCHAR(255).*NOT NULL" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf05-3.txt
```

### VF-05.4: 2 Indexes — user, composite user+thread
```bash
{ grep "idx_ownership_user " "$MIGRATION"; grep "idx_ownership_user_thread" "$MIGRATION"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf05-4.txt
```

**Gate VF-05:** 4/4 checks pass.

## VF-06 — session_summaries Table (S3.3, 12 columns + UNIQUE + 1 index)

### VF-06.1: Table Created with SERIAL PK
```bash
grep -A1 "CREATE TABLE.*session_summaries" "$MIGRATION" | grep "id.*SERIAL.*PRIMARY KEY" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf06-1.txt
```

### VF-06.2: thread_id FK with ON DELETE CASCADE
```bash
grep -A5 "CREATE TABLE.*session_summaries" "$MIGRATION" | grep "thread_id.*REFERENCES chat_threads.*ON DELETE CASCADE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf06-2.txt
```

### VF-06.3: version INTEGER with UNIQUE(thread_id, version)
```bash
grep -A20 "CREATE TABLE.*session_summaries" "$MIGRATION" | grep "UNIQUE.*thread_id.*version" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf06-3.txt
```

### VF-06.4: JSONB columns — facts_json, decisions_json, open_questions
```bash
{ grep "facts_json.*JSONB" "$MIGRATION" | head -1; grep "decisions_json.*JSONB" "$MIGRATION" | head -1; grep "open_questions.*JSONB" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf06-4.txt
```

### VF-06.5: covers_turns INTEGER[] NOT NULL
```bash
grep "covers_turns.*INTEGER\[\].*NOT NULL" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf06-5.txt
```
**PASS if:** Array type `INTEGER[]` with NOT NULL.

### VF-06.6: memory_tier VARCHAR(20) DEFAULT 'recall'
```bash
grep "memory_tier.*VARCHAR(20).*DEFAULT.*recall" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf06-6.txt
```
**PASS if:** MemGPT tiered memory tier field present per S5.2.

### VF-06.7: Index — thread version DESC
```bash
grep "idx_summaries_thread.*thread_id.*version DESC" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf06-7.txt
```

**Gate VF-06:** 7/7 checks pass.

## VF-07 — turn_snapshots Table (S3.3, ~25 columns, PARTITION BY RANGE)

### VF-07.1: Table Created with PARTITION BY RANGE(created_at)
```bash
grep "CREATE TABLE.*turn_snapshots" "$MIGRATION" | grep "PARTITION BY RANGE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-1.txt
```

### VF-07.2: DEFAULT partition (GAP-C3)
```bash
grep "turn_snapshots_default.*PARTITION OF turn_snapshots.*DEFAULT" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-2.txt
```
**PASS if:** DEFAULT partition created as safety net per GAP-C3.

### VF-07.3: Input columns — rendered_system_prompt, evidence_context, evidence_hash, post_trim_messages, rolling_summary, injection_scan_result
```bash
{ grep "rendered_system_prompt.*TEXT.*NOT NULL" "$MIGRATION" | head -1; grep "evidence_context.*TEXT" "$MIGRATION" | head -1; grep "evidence_hash.*VARCHAR(64)" "$MIGRATION" | head -1; grep "post_trim_messages.*JSONB.*NOT NULL" "$MIGRATION" | head -1; grep "rolling_summary.*TEXT" "$MIGRATION" | head -1; grep "injection_scan_result.*JSONB" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-3.txt
```
**PASS if:** All 6 model-input columns present with correct types.

### VF-07.4: Model parameter columns
```bash
{ grep "model_name.*VARCHAR(100).*NOT NULL" "$MIGRATION" | head -1; grep "provider.*VARCHAR(50).*NOT NULL" "$MIGRATION" | head -1; grep "temperature.*FLOAT" "$MIGRATION" | head -1; grep "max_completion_tokens.*INTEGER" "$MIGRATION" | head -1; grep "tool_definitions.*JSONB" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-4.txt
```

### VF-07.5: Output columns — raw_completion, proposals_extracted, citations_extracted, tokens
```bash
{ grep "raw_completion.*TEXT" "$MIGRATION" | head -1; grep "proposals_extracted.*JSONB" "$MIGRATION" | head -1; grep "citations_extracted.*JSONB" "$MIGRATION" | head -1; grep "completion_tokens.*INTEGER" "$MIGRATION" | head -1; grep "prompt_tokens.*INTEGER" "$MIGRATION" | head -1; grep "total_tokens.*INTEGER" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-5.txt
```

### VF-07.6: Reflexion metadata column (V2)
```bash
grep "critique_result.*JSONB" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-6.txt
```
**PASS if:** V2 reflexion metadata column present.

### VF-07.7: UNIQUE(thread_id, turn_number)
```bash
grep -A30 "CREATE TABLE.*turn_snapshots" "$MIGRATION" | grep "UNIQUE.*thread_id.*turn_number" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-7.txt
```

### VF-07.8: encrypted BOOLEAN DEFAULT FALSE
```bash
grep "encrypted.*BOOLEAN.*DEFAULT FALSE" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf07-8.txt
```

**Gate VF-07:** 8/8 checks pass.

## VF-08 — cost_ledger Table (S3.3, 13 columns, PARTITION BY RANGE)

### VF-08.1: Table with PARTITION BY RANGE(created_at)
```bash
grep "CREATE TABLE.*cost_ledger" "$MIGRATION" | grep "PARTITION BY RANGE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf08-1.txt
```

### VF-08.2: DEFAULT partition (GAP-C3)
```bash
grep "cost_ledger_default.*PARTITION OF cost_ledger.*DEFAULT" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf08-2.txt
```

### VF-08.3: thread_id FK with ON DELETE SET NULL (not CASCADE)
```bash
grep -A3 "CREATE TABLE.*cost_ledger" "$MIGRATION" | grep "thread_id.*REFERENCES chat_threads.*ON DELETE SET NULL" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf08-3.txt
```
**PASS if:** SET NULL (not CASCADE) — cost records survive thread deletion with null thread_id.

### VF-08.4: Token columns — input_tokens, output_tokens, cost_usd
```bash
{ grep "input_tokens.*INTEGER.*NOT NULL.*DEFAULT 0" "$MIGRATION" | head -1; grep "output_tokens.*INTEGER.*NOT NULL.*DEFAULT 0" "$MIGRATION" | head -1; grep "cost_usd.*NUMERIC(10,6).*NOT NULL.*DEFAULT 0" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf08-4.txt
```
**PASS if:** NUMERIC(10,6) precision for cost_usd.

### VF-08.5: 3 Indexes on cost_ledger
```bash
{ grep "idx_cost_deal" "$MIGRATION"; grep "idx_cost_user" "$MIGRATION"; grep "idx_cost_date" "$MIGRATION"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf08-5.txt
```

**Gate VF-08:** 5/5 checks pass.

## VF-09 — deal_cost_summary VIEW (S3.3, GAP-M12)

### VF-09.1: Regular VIEW (not MATERIALIZED VIEW)
```bash
grep "CREATE OR REPLACE VIEW deal_cost_summary" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf09-1.txt
```
**PASS if:** Regular VIEW per GAP-M12 fix. FAIL if MATERIALIZED VIEW.

### VF-09.2: View aggregates 8 columns
```bash
{ grep "DATE_TRUNC.*month.*created_at" "$MIGRATION" | head -1; grep "SUM.*input_tokens" "$MIGRATION" | head -1; grep "SUM.*output_tokens" "$MIGRATION" | head -1; grep "SUM.*cost_usd" "$MIGRATION" | head -1; grep "COUNT.*DISTINCT user_id" "$MIGRATION" | head -1; grep "MODE().*WITHIN GROUP.*ORDER BY model" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf09-2.txt
```
**PASS if:** View includes month grouping, token sums, cost sum, unique users, primary model.

**Gate VF-09:** 2/2 checks pass.

## VF-10 — deal_budgets Table (S3.3, GAP-C1, 8 columns)

### VF-10.1: deal_id VARCHAR(20) PRIMARY KEY — NO FK
```bash
grep -A3 "CREATE TABLE.*deal_budgets" "$MIGRATION" | grep "deal_id.*VARCHAR(20).*PRIMARY KEY" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf10-1.txt
```

### VF-10.2: No REFERENCES on deal_id (GAP-C1 fix)
```bash
grep -A10 "CREATE TABLE.*deal_budgets" "$MIGRATION" | grep "REFERENCES" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf10-2.txt
```
**PASS if:** No REFERENCES found. V1 had invalid FK to non-unique column; V2 removed it.

### VF-10.3: Predictive budgeting fields (V2 QW-8)
```bash
{ grep "avg_daily_cost.*NUMERIC(10,4)" "$MIGRATION" | head -1; grep "projected_monthly.*NUMERIC(10,2)" "$MIGRATION" | head -1; grep "budget_exhaustion_date.*DATE" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf10-3.txt
```
**PASS if:** All 3 predictive fields present per QW-8.

### VF-10.4: Budget control columns
```bash
{ grep "monthly_limit_usd.*NUMERIC(10,2).*DEFAULT 10.00" "$MIGRATION" | head -1; grep "alert_threshold.*NUMERIC(3,2).*DEFAULT 0.80" "$MIGRATION" | head -1; grep "hard_cap.*BOOLEAN.*DEFAULT FALSE" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf10-4.txt
```

**Gate VF-10:** 4/4 checks pass.

## VF-11 — cross_db_outbox Table (S3.3, GAP-M4, 10 columns)

### VF-11.1: Table Created
```bash
grep "CREATE TABLE.*cross_db_outbox" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf11-1.txt
```

### VF-11.2: event_type VARCHAR(50) NOT NULL
```bash
grep "event_type.*VARCHAR(50).*NOT NULL" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf11-2.txt
```

### VF-11.3: status VARCHAR(20) DEFAULT 'pending'
```bash
grep "status.*VARCHAR(20).*NOT NULL.*DEFAULT.*pending" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf11-3.txt
```

### VF-11.4: retry columns — retry_count, max_retries
```bash
{ grep "retry_count.*INTEGER.*DEFAULT 0" "$MIGRATION" | head -1; grep "max_retries.*INTEGER.*DEFAULT 3" "$MIGRATION" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf11-4.txt
```

### VF-11.5: Pending index
```bash
grep "idx_outbox_pending.*status.*created_at.*WHERE status = .pending." "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf11-5.txt
```

**Gate VF-11:** 5/5 checks pass.

## VF-12 — Trigger & Functions

### VF-12.1: update_thread_message_count() function
```bash
grep "CREATE OR REPLACE FUNCTION update_thread_message_count" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf12-1.txt
```

### VF-12.2: Function updates message_count AND last_active
```bash
{ grep "message_count = message_count + 1" "$MIGRATION"; grep "last_active = NOW()" "$MIGRATION"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf12-2.txt
```
**PASS if:** Function increments message_count by 1 and sets last_active to NOW().

### VF-12.3: Trigger on chat_messages AFTER INSERT
```bash
grep "trg_message_count.*AFTER INSERT ON chat_messages.*EXECUTE FUNCTION update_thread_message_count" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf12-3.txt
```

### VF-12.4: create_monthly_partitions() function (GAP-C3)
```bash
grep "CREATE OR REPLACE FUNCTION create_monthly_partitions" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf12-4.txt
```

### VF-12.5: Function parameters — (p_table TEXT, p_months_ahead INTEGER DEFAULT 3)
```bash
grep "create_monthly_partitions.*p_table TEXT.*p_months_ahead INTEGER.*DEFAULT 3" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf12-5.txt
```

### VF-12.6: Initial partition creation calls
```bash
{ grep "create_monthly_partitions.*turn_snapshots.*3" "$MIGRATION"; grep "create_monthly_partitions.*cost_ledger.*3" "$MIGRATION"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf12-6.txt
```
**PASS if:** Both turn_snapshots and cost_ledger get initial partitions with 3 months ahead.

**Gate VF-12:** 6/6 checks pass.

## VF-13 — Rollback Script Completeness

### VF-13.1: Drops all tables in reverse dependency order
```bash
{ grep "DROP TABLE.*cross_db_outbox" "$ROLLBACK"; grep "DROP TABLE.*deal_budgets" "$ROLLBACK"; grep "DROP VIEW.*deal_cost_summary" "$ROLLBACK"; grep "DROP TABLE.*cost_ledger" "$ROLLBACK"; grep "DROP TABLE.*turn_snapshots" "$ROLLBACK"; grep "DROP TABLE.*session_summaries" "$ROLLBACK"; grep "DROP TABLE.*thread_ownership" "$ROLLBACK"; grep "DROP TABLE.*chat_messages" "$ROLLBACK"; grep "DROP TABLE.*chat_threads" "$ROLLBACK"; grep "DROP TABLE.*user_identity_map" "$ROLLBACK"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf13-1.txt
```
**PASS if:** All 10 objects dropped. Must include VIEW drop before cost_ledger.

### VF-13.2: Function drops
```bash
{ grep "DROP FUNCTION.*update_thread_message_count" "$ROLLBACK"; grep "DROP FUNCTION.*create_monthly_partitions" "$ROLLBACK"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf13-2.txt
```

### VF-13.3: Migration tracking row removed
```bash
grep "DELETE FROM schema_migrations WHERE version = .004." "$ROLLBACK" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf13-3.txt
```

### VF-13.4: Rollback wrapped in transaction
```bash
{ grep "^BEGIN;" "$ROLLBACK"; grep "^COMMIT;" "$ROLLBACK"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/vf13-4.txt
```

**Gate VF-13:** 4/4 checks pass.

---

## Cross-Consistency

### XC-1: Forward migration table count matches rollback DROP count
```bash
FWD=$(grep -ci "CREATE TABLE" "$MIGRATION" 2>/dev/null) || FWD=0; REV=$(grep -ci "DROP TABLE" "$ROLLBACK" 2>/dev/null) || REV=0; echo "Forward: $FWD tables, Rollback: $REV drops" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/xc1.txt
```
**PASS if:** DROP count >= CREATE count (rollback drops everything forward creates).

### XC-2: Every VARCHAR(255) user_id (GAP-C2 global check)
```bash
grep -n "user_id.*INTEGER" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/xc2.txt
```
**PASS if:** Zero lines found. No INTEGER user_id anywhere in the migration.

### XC-3: All FK columns reference existing tables in the same migration
```bash
grep "REFERENCES" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/xc3.txt
```
**PASS if:** Every REFERENCES target (chat_threads) is created before the referencing table.

---

## Stress Tests

### ST-1: No hardcoded partition dates
```bash
grep -n "2026_0[0-9]" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/st1.txt
```
**PASS if:** Zero hardcoded partition names. Partitions created dynamically via create_monthly_partitions().

### ST-2: No MATERIALIZED VIEW (GAP-M12 regression check)
```bash
grep -ci "MATERIALIZED VIEW" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/st2.txt
```
**PASS if:** Count is 0. GAP-M12 mandates regular VIEW.

### ST-3: CASCADE vs SET NULL correctness
```bash
grep "ON DELETE" "$MIGRATION" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m01/st3.txt
```
**PASS if:** chat_messages/thread_ownership/session_summaries/turn_snapshots use CASCADE; cost_ledger uses SET NULL.

---

## Enhancement Opportunities

- **ENH-1**: Add pg_partman configuration comments with ready-to-run SELECT statement
- **ENH-2**: Add CHECK constraint on cost_ledger.cost_usd >= 0 (non-negative cost)
- **ENH-3**: Consider adding GiST index on cross_db_outbox for JSONB payload queries

## Self-Check Prompts

1. After discovery: "Have I located both migration files and set shell variables for their paths?"
2. After verification: "Did I check every column of every table against the spec, not just table names?"
3. Before completion: "Did I verify both forward AND rollback, and check cross-consistency between them?"

## File Paths Reference

| Action | Path |
|--------|------|
| Verify | Migration 004 forward SQL (found via PF-3) |
| Verify | Migration 004 rollback SQL (found via VF-01.2) |
| Read-only | `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` S3.2-S3.3 |
| Write | `/home/zaks/bookkeeping/docs/_qa_evidence/col-m01/*.txt` |

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF (Pre-Flight) | 3 | |
| VF-01 (File Existence) | 4 | |
| VF-02 (user_identity_map) | 8 | |
| VF-03 (chat_threads) | 16 | |
| VF-04 (chat_messages) | 9 | |
| VF-05 (thread_ownership) | 4 | |
| VF-06 (session_summaries) | 7 | |
| VF-07 (turn_snapshots) | 8 | |
| VF-08 (cost_ledger) | 5 | |
| VF-09 (deal_cost_summary) | 2 | |
| VF-10 (deal_budgets) | 4 | |
| VF-11 (cross_db_outbox) | 5 | |
| VF-12 (Triggers & Functions) | 6 | |
| VF-13 (Rollback) | 4 | |
| XC (Cross-Consistency) | 3 | |
| ST (Stress Tests) | 3 | |
| **TOTAL** | **91** | |

## Stop Condition

**DONE when:** All 91 gates produce evidence files in `_qa_evidence/col-m01/`. Scorecard filled. Remediations (if any) recorded. Do NOT proceed to M02 — that is a separate mission.

---

# MISSION: QA-COL-M02-VERIFY-001
## QA Verification: Chat Repository Layer
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M02-CHAT-REPOSITORY (Execution complete)
## Successor: QA-COL-M03-VERIFY-001

## Mission Objective

Spec-level verification of **ChatRepository** — the single data access layer for all chat CRUD operations.
Every method signature, SQL pattern, ownership enforcement, and outbox integration is checked against COL-DESIGN-SPEC-V2.md S3.6 (lines 678–715).

**Source spec:** S3.6 (ChatRepository class definition)
**File expected:** `apps/agent-api/app/services/chat_repository.py`
**Methods expected:** 12 (create_thread, get_thread, list_threads, update_thread, soft_delete_thread, hard_delete_thread, restore_thread, add_message, get_messages, get_thread_for_llm, validate_deal_reference, enqueue_brain_extraction)
**Scope:** Repository layer only. API endpoints are M03. Schema is M01.

## Context

ChatRepository replaces the old `ChatSessionStore`. It is the SINGLE point of access for all chat data — no direct table queries elsewhere. All methods enforce thread ownership via user_id checks. Cross-DB writes go through the outbox pattern (GAP-M4).

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m02 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/pf2-dir.txt
```

### PF-3: Repository File Exists
```bash
REPO_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "chat_repository.py" -type f 2>/dev/null) && echo "FOUND: $REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/pf3-file.txt
```

---

## Verification Families

## VF-01 — Class Structure

### VF-01.1: ChatRepository class defined
```bash
grep -n "class ChatRepository" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf01-1.txt
```

### VF-01.2: Docstring mentions canonical / single source
```bash
grep -A3 "class ChatRepository" "$REPO_FILE" | grep -i "canonical\|single.*source\|data access" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf01-2.txt
```

**Gate VF-01:** 2/2 checks pass.

## VF-02 — Thread CRUD Methods (7 methods)

### VF-02.1: create_thread(user_id, scope_type, deal_id=None) -> ChatThread
```bash
grep -n "async def create_thread" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf02-1.txt
```
**PASS if:** Method exists with parameters: user_id: str, scope_type: str, deal_id optional.

### VF-02.2: get_thread(thread_id, user_id) -> ChatThread
```bash
grep -n "async def get_thread" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf02-2.txt
```
**PASS if:** Both thread_id AND user_id required (ownership check baked in).

### VF-02.3: list_threads(user_id, deleted=False, limit=50)
```bash
grep -n "async def list_threads" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf02-3.txt
```
**PASS if:** user_id required, deleted defaults to False, limit defaults to 50.

### VF-02.4: update_thread(thread_id, user_id, **kwargs)
```bash
grep -n "async def update_thread" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf02-4.txt
```

### VF-02.5: soft_delete_thread(thread_id, user_id)
```bash
grep -n "async def soft_delete_thread" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf02-5.txt
```

### VF-02.6: hard_delete_thread(thread_id, user_id)
```bash
grep -n "async def hard_delete_thread" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf02-6.txt
```

### VF-02.7: restore_thread(thread_id, user_id) -> ChatThread
```bash
grep -n "async def restore_thread" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf02-7.txt
```

**Gate VF-02:** 7/7 thread methods verified.

## VF-03 — Message Methods (3 methods)

### VF-03.1: add_message(thread_id, user_id, role, content, **metadata)
```bash
grep -n "async def add_message" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf03-1.txt
```

### VF-03.2: get_messages(thread_id, user_id, limit=50, before_turn=None)
```bash
grep -n "async def get_messages" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf03-2.txt
```
**PASS if:** cursor pagination via before_turn parameter per spec.

### VF-03.3: get_thread_for_llm(thread_id, max_messages=6)
```bash
grep -n "async def get_thread_for_llm" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf03-3.txt
```
**PASS if:** max_messages defaults to 6 per Working Memory tier.

**Gate VF-03:** 3/3 message methods verified.

## VF-04 — Cross-DB Methods (2 methods, GAP-H4 + GAP-M4)

### VF-04.1: validate_deal_reference(deal_id) -> bool
```bash
grep -n "async def validate_deal_reference" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf04-1.txt
```
**PASS if:** Application-level deal_id existence check (cross-DB FK impossible per GAP-H4).

### VF-04.2: enqueue_brain_extraction(deal_id, thread_id, turn, user_msg, asst_msg)
```bash
grep -n "async def enqueue_brain_extraction" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf04-2.txt
```
**PASS if:** Writes to cross_db_outbox instead of direct cross-DB write per GAP-M4.

**Gate VF-04:** 2/2 cross-DB methods verified.

## VF-05 — Ownership Enforcement

### VF-05.1: All get/update/delete methods include user_id parameter
```bash
grep "async def.*thread.*self.*user_id" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf05-1.txt
```
**PASS if:** Every thread-accessing method includes user_id (not just thread_id).

### VF-05.2: SQL queries include user_id in WHERE clause
```bash
grep -c "user_id" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf05-2.txt
```
**PASS if:** user_id referenced at least 12 times (once per method that takes it).

### VF-05.3: thread_ownership table referenced
```bash
grep -c "thread_ownership" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf05-3.txt
```
**PASS if:** thread_ownership referenced at least once (for create_thread ownership row creation).

### VF-05.4: PermissionError or similar raised on ownership mismatch
```bash
grep -i "PermissionError\|Forbidden\|ownership.*mismatch\|not.*authorized" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf05-4.txt
```

**Gate VF-05:** 4/4 ownership checks verified.

## VF-06 — SQL Pattern Safety

### VF-06.1: Parameterized queries (no f-string SQL)
```bash
grep -n 'f".*SELECT\|f".*INSERT\|f".*UPDATE\|f".*DELETE' "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf06-1.txt
```
**PASS if:** Zero lines. All SQL must use parameterized queries ($1, $2) not f-strings.

### VF-06.2: legal_hold check in delete methods
```bash
grep -A10 "def hard_delete_thread\|def soft_delete_thread" "$REPO_FILE" | grep -i "legal_hold" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf06-2.txt
```
**PASS if:** Delete methods check legal_hold=TRUE and return 409 per spec.

### VF-06.3: create_thread creates thread_ownership row
```bash
grep -A20 "def create_thread" "$REPO_FILE" | grep "thread_ownership" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf06-3.txt
```

**Gate VF-06:** 3/3 safety patterns verified.

## VF-07 — Outbox Integration

### VF-07.1: enqueue_brain_extraction writes to cross_db_outbox
```bash
grep -A15 "def enqueue_brain_extraction" "$REPO_FILE" | grep "cross_db_outbox\|outbox" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf07-1.txt
```

### VF-07.2: Outbox payload includes deal_id, thread_id, turn
```bash
grep -A15 "def enqueue_brain_extraction" "$REPO_FILE" | grep "deal_id\|thread_id\|turn" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/vf07-2.txt
```

**Gate VF-07:** 2/2 outbox checks verified.

---

## Cross-Consistency

### XC-1: Method count matches spec
```bash
grep -c "async def " "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/xc1.txt
```
**PASS if:** >= 12 async methods (spec defines 12 public methods).

### XC-2: No direct table queries outside ChatRepository
```bash
grep -rn "chat_threads\|chat_messages\|thread_ownership" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "chat_repository\|migration\|test\|__pycache__" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/xc2.txt
```
**PASS if:** Zero direct table references outside ChatRepository (single access point rule).

### XC-3: ChatRepository imported where needed
```bash
grep -rn "from.*chat_repository.*import\|import.*ChatRepository" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "__pycache__" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/xc3.txt
```
**PASS if:** At least 1 import found (ChatRepository must be used, not just defined).

---

## Stress Tests

### ST-1: No SQLite references in ChatRepository
```bash
grep -i "sqlite\|ChatSessionStore\|chat_persistence" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/st1.txt
```
**PASS if:** Zero lines. ChatRepository replaces SQLite — no backward references.

### ST-2: No Promise.all equivalent (Python asyncio.gather without error handling)
```bash
grep "asyncio.gather" "$REPO_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m02/st2.txt
```
**PASS if:** Zero lines or uses return_exceptions=True.

---

## Enhancement Opportunities

- **ENH-1**: Add connection pooling configuration for high-throughput message writes
- **ENH-2**: Add batch message insertion method for migration backfill performance
- **ENH-3**: Add read-through cache for frequently accessed threads

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 3 | |
| VF-01 (Class Structure) | 2 | |
| VF-02 (Thread CRUD) | 7 | |
| VF-03 (Message Methods) | 3 | |
| VF-04 (Cross-DB) | 2 | |
| VF-05 (Ownership) | 4 | |
| VF-06 (SQL Safety) | 3 | |
| VF-07 (Outbox) | 2 | |
| XC | 3 | |
| ST | 2 | |
| **TOTAL** | **31** | |

## Stop Condition

**DONE when:** All 31 gates produce evidence files. Do NOT proceed to M03.

---

# MISSION: QA-COL-M03-VERIFY-001
## QA Verification: Chat API Endpoints & Middleware Routing
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M03-CHAT-ENDPOINTS (Execution complete)
## Successor: QA-COL-M04-VERIFY-001

## Mission Objective

Spec-level verification of **5 chat API endpoints** and **middleware routing** for `/api/v1/chatbot/*` to Agent API.
Every endpoint path, method, auth requirement, query parameter, and response shape is checked against COL-DESIGN-SPEC-V2.md S3.5 (lines 604–676) and S3.10 (SSE Event Catalog).

**Source spec:** S3.5 (endpoints + middleware), S3.10 (SSE catalog)
**Endpoints:** GET /threads, GET /threads/{id}/messages, POST /threads, PATCH /threads/{id}, DELETE /threads/{id}
**Middleware:** `/api/v1/chatbot/*` routed to Agent API port 8095 (GAP-H1)
**SSE Events:** 14 typed events cataloged per GAP-L2

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m03 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/pf2-dir.txt
```

---

## Verification Families

## VF-01 — Middleware Routing (GAP-H1)

### VF-01.1: Middleware file exists
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "middleware.ts" -type f 2>/dev/null | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf01-1.txt
```

### VF-01.2: Chatbot routes defined
```bash
MW_FILE=$(find /home/zaks/zakops-agent-api/apps/dashboard -name "middleware.ts" -path "*/src/*" -o -name "middleware.ts" -path "*/apps/dashboard/*" | head -1) && grep -i "chatbot\|/api/v1/chatbot" "$MW_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf01-2.txt
```
**PASS if:** `/api/v1/chatbot` route pattern present in middleware.

### VF-01.3: Routes proxy to Agent API (port 8095)
```bash
grep -i "8095\|agent.*api\|AGENT_API" "$MW_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf01-3.txt
```
**PASS if:** Agent API target (port 8095) referenced for chatbot routes.

**Gate VF-01:** 3/3 middleware checks pass.

## VF-02 — GET /api/v1/chatbot/threads Endpoint

### VF-02.1: Route handler file exists
```bash
find /home/zaks/zakops-agent-api/apps/agent-api -name "chatbot.py" -o -name "chatbot_routes.py" -o -name "threads.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf02-1.txt
```

### VF-02.2: GET /threads endpoint defined
```bash
CHATBOT_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "chatbot*.py" -path "*/api/*" -type f | head -1) && grep -n "threads.*get\|GET.*threads\|@.*get.*threads\|def.*list_threads\|def.*get_threads" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf02-2.txt
```

### VF-02.3: Query parameters — deleted, limit, offset
```bash
grep -A10 "def.*list_threads\|def.*get_threads" "$CHATBOT_FILE" | grep -i "deleted\|limit\|offset" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf02-3.txt
```
**PASS if:** deleted=false, limit=50, offset=0 defaults per spec.

### VF-02.4: Response includes threads array and total count
```bash
grep -A20 "def.*list_threads\|def.*get_threads" "$CHATBOT_FILE" | grep -i "threads\|total" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf02-4.txt
```

### VF-02.5: Sort order — pinned DESC, last_active DESC
```bash
grep -i "pinned.*DESC\|last_active.*DESC\|ORDER BY.*pinned" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf02-5.txt
```

**Gate VF-02:** 5/5 checks pass.

## VF-03 — GET /api/v1/chatbot/threads/{id}/messages Endpoint

### VF-03.1: Messages endpoint with cursor pagination
```bash
grep -n "messages\|get_messages" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf03-1.txt
```

### VF-03.2: before_turn parameter for cursor pagination
```bash
grep -i "before_turn\|cursor\|turn_number" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf03-2.txt
```
**PASS if:** Cursor pagination by turn_number (not offset-based) per spec.

### VF-03.3: Response includes has_more boolean
```bash
grep -i "has_more" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf03-3.txt
```

### VF-03.4: Ownership check (JWT + thread_ownership)
```bash
grep -A15 "def.*get_messages\|def.*messages" "$CHATBOT_FILE" | grep -i "user_id\|ownership\|auth" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf03-4.txt
```

**Gate VF-03:** 4/4 checks pass.

## VF-04 — POST /api/v1/chatbot/threads Endpoint

### VF-04.1: Create thread endpoint
```bash
grep -n "def.*create_thread\|POST.*threads" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf04-1.txt
```

### VF-04.2: Body includes scope_type, optional deal_id and title
```bash
grep -A10 "def.*create_thread" "$CHATBOT_FILE" | grep -i "scope_type\|deal_id\|title" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf04-2.txt
```

### VF-04.3: Side effects — creates thread_ownership row
```bash
grep -A20 "def.*create_thread" "$CHATBOT_FILE" | grep -i "ownership" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf04-3.txt
```

**Gate VF-04:** 3/3 checks pass.

## VF-05 — PATCH /api/v1/chatbot/threads/{id} Endpoint

### VF-05.1: Update thread endpoint
```bash
grep -n "def.*update_thread\|PATCH.*threads" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf05-1.txt
```

### VF-05.2: Body allows title, pinned, archived updates
```bash
grep -A10 "def.*update_thread" "$CHATBOT_FILE" | grep -i "title\|pinned\|archived" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf05-2.txt
```

**Gate VF-05:** 2/2 checks pass.

## VF-06 — DELETE /api/v1/chatbot/threads/{id} Endpoint

### VF-06.1: Delete endpoint exists
```bash
grep -n "def.*delete_thread\|DELETE.*threads" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf06-1.txt
```

### VF-06.2: permanent query parameter (default false)
```bash
grep -A10 "def.*delete_thread" "$CHATBOT_FILE" | grep -i "permanent" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf06-2.txt
```
**PASS if:** permanent=false default (soft delete by default, hard delete on request).

### VF-06.3: Legal hold block returns 409
```bash
grep -A20 "def.*delete_thread" "$CHATBOT_FILE" | grep -i "legal_hold\|409\|Conflict" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf06-3.txt
```
**PASS if:** Returns 409 Conflict if legal_hold=TRUE.

**Gate VF-06:** 3/3 checks pass.

## VF-07 — SSE Event Catalog (GAP-L2, 14 events)

### VF-07.1: SSE event types defined
```bash
find /home/zaks/zakops-agent-api/apps/agent-api -name "*.py" -exec grep -l "message_chunk\|message_complete\|thread_updated\|brain_updated" {} \; | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf07-1.txt
```

### VF-07.2: At least 10 of 14 SSE event types present
```bash
for EVENT in message_chunk message_complete thread_updated brain_updated summary_generated injection_alert legal_hold_set budget_warning cost_update ghost_knowledge momentum_update tool_execution approval_required error; do grep -rq "$EVENT" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" && echo "FOUND: $EVENT"; done 2>/dev/null | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf07-2.txt
```
**PASS if:** >= 10 of 14 event types found (some may be in later missions).

**Gate VF-07:** 2/2 SSE checks pass.

## VF-08 — Pydantic Response Models

### VF-08.1: ChatThreadSummary model
```bash
grep -rn "class ChatThreadSummary\|ChatThreadSummary" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf08-1.txt
```

### VF-08.2: ChatThreadSummary includes momentum_score field (QW-2)
```bash
grep -A20 "class ChatThreadSummary" /home/zaks/zakops-agent-api/apps/agent-api/app/ -r --include="*.py" | grep -i "momentum" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf08-2.txt
```

### VF-08.3: ChatMessage model with required fields
```bash
grep -rn "class ChatMessage" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/vf08-3.txt
```

**Gate VF-08:** 3/3 model checks pass.

---

## Cross-Consistency

### XC-1: Endpoint count matches spec (5 CRUD endpoints)
```bash
grep -c "def.*thread\|def.*message" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/xc1.txt
```
**PASS if:** >= 5 endpoint handlers.

### XC-2: All endpoints use ChatRepository (not direct SQL)
```bash
grep "ChatRepository\|chat_repository" "$CHATBOT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/xc2.txt
```

### XC-3: Middleware routes match endpoint paths
```bash
grep "chatbot" "$MW_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/xc3.txt
```

---

## Stress Tests

### ST-1: No hardcoded port numbers in endpoint files
```bash
grep -n "8091\|8095\|3003" "$CHATBOT_FILE" 2>/dev/null | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/st1.txt
```
**PASS if:** Zero hardcoded ports (should use config/env vars).

### ST-2: No 501 stubs remaining (execute-proposal was 501)
```bash
grep -rn "501\|Not Implemented" /home/zaks/zakops-agent-api/apps/agent-api/app/api/ --include="*.py" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m03/st2.txt
```
**PASS if:** Zero 501 responses in chatbot endpoints.

---

## Enhancement Opportunities

- **ENH-1**: Add rate limiting on thread creation endpoint
- **ENH-2**: Add OpenAPI schema annotations for auto-generated docs
- **ENH-3**: Consider WebSocket alternative for SSE events with bidirectional needs

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Middleware) | 3 | |
| VF-02 (GET threads) | 5 | |
| VF-03 (GET messages) | 4 | |
| VF-04 (POST threads) | 3 | |
| VF-05 (PATCH threads) | 2 | |
| VF-06 (DELETE threads) | 3 | |
| VF-07 (SSE Catalog) | 2 | |
| VF-08 (Models) | 3 | |
| XC | 3 | |
| ST | 2 | |
| **TOTAL** | **32** | |

## Stop Condition

**DONE when:** All 32 gates produce evidence files. Do NOT proceed to M04.

---

# MISSION: QA-COL-M04-VERIFY-001
## QA Verification: Deal Brain Schema (Migration 028)
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M04-DEAL-BRAIN-SCHEMA (Execution complete)
## Successor: QA-COL-M05-VERIFY-001

## Mission Objective

Spec-level verification of **Migration 028** — the Deal Brain v2 schema in the `zakops` database (schema `zakops`).
Every column, JSONB schema, FK reference, index, and constraint is checked against COL-DESIGN-SPEC-V2.md S4.2 (lines 846–992).

**Source spec:** S4.2 (Migration 028 DDL)
**Database:** zakops (schema: zakops — NOT public)
**Tables:** deal_brain, deal_brain_history, deal_entity_graph, decision_outcomes, deal_access
**Data migration:** Backfill from agent_context_summaries

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m04 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/pf2-dir.txt
```

### PF-3: Migration File Location
```bash
M028=$(find /home/zaks/zakops-backend -name "028_deal_brain*" -type f 2>/dev/null | head -1) && echo "FOUND: $M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/pf3-migration.txt
```

---

## Verification Families

## VF-01 — Migration File Existence

### VF-01.1: Forward Migration Exists
```bash
test -f "$M028" && echo "PASS: $M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf01-1.txt
```

### VF-01.2: Rollback Migration Exists
```bash
M028R=$(find /home/zaks/zakops-backend -name "028_deal_brain*rollback*" -type f 2>/dev/null | head -1) && echo "FOUND: $M028R" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf01-2.txt
```

### VF-01.3: Migration Tracking
```bash
grep "INSERT INTO zakops.schema_migrations.*028" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf01-3.txt
```

### VF-01.4: Uses zakops schema (NOT public)
```bash
grep "zakops\." "$M028" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf01-4.txt
```
**PASS if:** Tables created under `zakops.` schema prefix.

**Gate VF-01:** 4/4 checks pass.

## VF-02 — deal_brain Table (S4.2, ~25 columns)

### VF-02.1: Table Created with deal_id PK + FK to deals
```bash
grep "CREATE TABLE.*zakops.deal_brain" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-1.txt
```

### VF-02.2: deal_id VARCHAR(20) PRIMARY KEY REFERENCES zakops.deals
```bash
grep -A2 "zakops.deal_brain" "$M028" | grep "deal_id.*VARCHAR(20).*PRIMARY KEY.*REFERENCES.*zakops.deals" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-2.txt
```
**PASS if:** FK to zakops.deals(deal_id) — brain is deal-level.

### VF-02.3: version INTEGER NOT NULL DEFAULT 1
```bash
grep -A30 "CREATE TABLE.*zakops.deal_brain" "$M028" | grep "version.*INTEGER.*NOT NULL.*DEFAULT 1" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-3.txt
```

### VF-02.4: Summary columns — summary TEXT, summary_model VARCHAR(100), summary_confidence FLOAT
```bash
{ grep "summary .*TEXT" "$M028" | head -1; grep "summary_model.*VARCHAR(100)" "$M028" | head -1; grep "summary_confidence.*FLOAT.*DEFAULT 1.0" "$M028" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-4.txt
```

### VF-02.5: JSONB knowledge columns — facts, risks, decisions, assumptions, open_items
```bash
for COL in facts risks decisions assumptions open_items; do grep "$COL.*JSONB.*DEFAULT.*\[\]" "$M028" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-5.txt
```
**PASS if:** All 5 JSONB columns with DEFAULT '[]'::jsonb.

### VF-02.6: Ghost Knowledge column (V2 E-1)
```bash
grep "ghost_facts.*JSONB.*DEFAULT.*\[\]" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-6.txt
```
**PASS if:** ghost_facts JSONB column for V2 Ghost Knowledge Detection.

### VF-02.7: Momentum Score columns (V2 F-1)
```bash
{ grep "momentum_score.*FLOAT" "$M028" | head -1; grep "momentum_updated_at.*TIMESTAMPTZ" "$M028" | head -1; grep "momentum_components.*JSONB" "$M028" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-7.txt
```
**PASS if:** All 3 momentum columns present per QW-2.

### VF-02.8: Cross-Deal Entity column (V2 C-4)
```bash
grep "entities.*JSONB.*DEFAULT.*\[\]" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-8.txt
```

### VF-02.9: Email integration columns (V2 GAP-M9)
```bash
{ grep "email_facts_count.*INTEGER.*DEFAULT 0" "$M028" | head -1; grep "last_email_ingestion.*TIMESTAMPTZ" "$M028" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-9.txt
```

### VF-02.10: Provenance columns
```bash
{ grep "last_summarized_turn.*INTEGER" "$M028" | head -1; grep "last_summarized_at.*TIMESTAMPTZ" "$M028" | head -1; grep "last_fact_extraction.*TIMESTAMPTZ" "$M028" | head -1; grep "contradiction_count.*INTEGER.*DEFAULT 0" "$M028" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-10.txt
```

### VF-02.11: stage_notes JSONB DEFAULT '{}'
```bash
grep "stage_notes.*JSONB.*DEFAULT.*{}" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf02-11.txt
```

**Gate VF-02:** 11/11 deal_brain columns verified.

## VF-03 — deal_brain_history Table (S4.2, 8 columns)

### VF-03.1: Table Created
```bash
grep "CREATE TABLE.*zakops.deal_brain_history" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf03-1.txt
```

### VF-03.2: deal_id FK to zakops.deals
```bash
grep -A5 "deal_brain_history" "$M028" | grep "deal_id.*REFERENCES.*zakops.deals" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf03-2.txt
```

### VF-03.3: UNIQUE(deal_id, version)
```bash
grep -A10 "deal_brain_history" "$M028" | grep "UNIQUE.*deal_id.*version" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf03-3.txt
```

### VF-03.4: snapshot JSONB NOT NULL + diff JSONB
```bash
{ grep "snapshot.*JSONB.*NOT NULL" "$M028" | head -1; grep "diff.*JSONB" "$M028" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf03-4.txt
```

### VF-03.5: triggered_by VARCHAR(255) — GAP-C2 fix
```bash
grep "triggered_by.*VARCHAR(255)" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf03-5.txt
```
**PASS if:** VARCHAR(255) not INTEGER per GAP-C2.

### VF-03.6: Index on (deal_id, version DESC)
```bash
grep "idx_brain_history_deal.*deal_id.*version DESC" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf03-6.txt
```

**Gate VF-03:** 6/6 checks pass.

## VF-04 — deal_entity_graph Table (V2 C-4, 8 columns)

### VF-04.1: Table Created
```bash
grep "CREATE TABLE.*zakops.deal_entity_graph" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf04-1.txt
```

### VF-04.2: UNIQUE(entity_type, normalized_name, deal_id)
```bash
grep "UNIQUE.*entity_type.*normalized_name.*deal_id" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf04-2.txt
```

### VF-04.3: 2 Indexes
```bash
{ grep "idx_entity_graph_name" "$M028"; grep "idx_entity_graph_deal" "$M028"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf04-3.txt
```

### VF-04.4: deal_id FK to zakops.deals
```bash
grep -A5 "deal_entity_graph" "$M028" | grep "deal_id.*REFERENCES.*zakops.deals" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf04-4.txt
```

**Gate VF-04:** 4/4 checks pass.

## VF-05 — decision_outcomes Table (V2 I-5, 7 columns)

### VF-05.1: Table Created
```bash
grep "CREATE TABLE.*zakops.decision_outcomes" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf05-1.txt
```

### VF-05.2: decision_id VARCHAR(36) — references deal_brain.decisions[].id
```bash
grep "decision_id.*VARCHAR(36)" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf05-2.txt
```

### VF-05.3: predicted_value, actual_value, delta — all JSONB
```bash
{ grep "predicted_value.*JSONB" "$M028" | head -1; grep "actual_value.*JSONB" "$M028" | head -1; grep "delta.*JSONB" "$M028" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf05-3.txt
```

**Gate VF-05:** 3/3 checks pass.

## VF-06 — deal_access Table (S4.2, 5 columns + CHECK)

### VF-06.1: Table Created with composite PK
```bash
grep "CREATE TABLE.*zakops.deal_access" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf06-1.txt
```

### VF-06.2: PRIMARY KEY (deal_id, user_id)
```bash
grep -A10 "deal_access" "$M028" | grep "PRIMARY KEY.*deal_id.*user_id" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf06-2.txt
```

### VF-06.3: deal_id FK with ON DELETE CASCADE
```bash
grep -A5 "deal_access" "$M028" | grep "deal_id.*REFERENCES.*zakops.deals.*ON DELETE CASCADE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf06-3.txt
```

### VF-06.4: Role CHECK — viewer, operator, approver, admin
```bash
grep "chk_deal_role.*CHECK.*role.*IN.*viewer.*operator.*approver.*admin" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf06-4.txt
```

### VF-06.5: user_id VARCHAR(255) — GAP-C2
```bash
grep -A10 "deal_access" "$M028" | grep "user_id.*VARCHAR(255)" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf06-5.txt
```

### VF-06.6: Index on user_id
```bash
grep "idx_deal_access_user" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf06-6.txt
```

**Gate VF-06:** 6/6 checks pass.

## VF-07 — Data Migration from Proto-Brain

### VF-07.1: INSERT INTO deal_brain SELECT FROM agent_context_summaries
```bash
grep "INSERT INTO zakops.deal_brain.*SELECT.*FROM zakops.agent_context_summaries" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf07-1.txt
```
**PASS if:** Backfill from existing proto-brain on migration.

### VF-07.2: ON CONFLICT DO NOTHING (idempotent)
```bash
grep "ON CONFLICT.*DO NOTHING" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf07-2.txt
```

**Gate VF-07:** 2/2 checks pass.

## VF-08 — Rollback Script

### VF-08.1: Drops all 5 tables in reverse dependency order
```bash
{ grep "DROP TABLE.*decision_outcomes" "$M028R"; grep "DROP TABLE.*deal_entity_graph" "$M028R"; grep "DROP TABLE.*deal_access" "$M028R"; grep "DROP TABLE.*deal_brain_history" "$M028R"; grep "DROP TABLE.*deal_brain" "$M028R"; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf08-1.txt
```

### VF-08.2: Removes migration tracking
```bash
grep "DELETE FROM zakops.schema_migrations WHERE version = .028." "$M028R" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/vf08-2.txt
```

**Gate VF-08:** 2/2 checks pass.

---

## Cross-Consistency

### XC-1: All VARCHAR(255) user_id columns (GAP-C2)
```bash
grep -n "user_id.*INTEGER" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/xc1.txt
```
**PASS if:** Zero INTEGER user_id references.

### XC-2: All FK references to zakops.deals exist
```bash
grep "REFERENCES zakops.deals" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/xc2.txt
```
**PASS if:** At least 4 FKs (deal_brain, deal_brain_history, deal_entity_graph, deal_access).

### XC-3: Rollback DROP count matches CREATE count
```bash
FWD=$(grep -ci "CREATE TABLE" "$M028" 2>/dev/null) || FWD=0; REV=$(grep -ci "DROP TABLE" "$M028R" 2>/dev/null) || REV=0; echo "Forward: $FWD, Rollback: $REV" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/xc3.txt
```

---

## Stress Tests

### ST-1: No cross-database FKs (zakops_agent tables referenced from zakops)
```bash
grep "REFERENCES.*public\.\|REFERENCES.*chat_threads\|REFERENCES.*cost_ledger" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/st1.txt
```
**PASS if:** Zero cross-DB FKs. Brain is in zakops, chat tables in zakops_agent.

### ST-2: deal_brain has no partition scheme (simple table)
```bash
grep "PARTITION BY" "$M028" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m04/st2.txt
```
**PASS if:** Zero. deal_brain is a simple table (partitioned tables are in Migration 004).

---

## Enhancement Opportunities

- **ENH-1**: Add partial index on deal_brain.momentum_score for dashboard queries
- **ENH-2**: Add trigger to auto-update deal_brain.updated_at on any column change
- **ENH-3**: Consider adding GIN index on deal_brain.facts for JSONB containment queries

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 3 | |
| VF-01 (File Existence) | 4 | |
| VF-02 (deal_brain) | 11 | |
| VF-03 (deal_brain_history) | 6 | |
| VF-04 (deal_entity_graph) | 4 | |
| VF-05 (decision_outcomes) | 3 | |
| VF-06 (deal_access) | 6 | |
| VF-07 (Data Migration) | 2 | |
| VF-08 (Rollback) | 2 | |
| XC | 3 | |
| ST | 2 | |
| **TOTAL** | **46** | |

## Stop Condition

**DONE when:** All 46 gates produce evidence files. Do NOT proceed to M05.

---

# MISSION: QA-COL-M05-VERIFY-001
## QA Verification: Deal Brain Service, Extraction & Multi-User Identity
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M05-DEAL-BRAIN-SERVICE (Execution complete)
## Successor: QA-COL-M06-VERIFY-001

## Mission Objective

Spec-level verification of **DealBrainService**, **extraction prompt**, **drift detection**, **momentum calculation**, and **multi-user identity** (X-User-Id header).
Every method signature, write trigger, extraction field, and drift mechanism is checked against S4.3–S4.7, S10.2–S10.4, S20.1–S20.2.

**Source spec:** S4.3 (write triggers), S4.4 (extraction prompt), S4.5 (drift detection), S4.7 (DealBrain.tsx), S10.2 (X-User-Id), S10.3 (thread ownership), S10.4 (deal access control), S20.1 (ghost knowledge), S20.2 (momentum score)
**Files expected:** deal_brain_service.py, DealBrain.tsx, momentum_calculator.py, ghost_knowledge_detector.py

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m05 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/pf2-dir.txt
```

---

## Verification Families

## VF-01 — DealBrainService Class

### VF-01.1: Service file exists
```bash
BRAIN_SVC=$(find /home/zaks/zakops-backend/src -name "deal_brain_service.py" -o -name "brain_service.py" | head -1) && echo "FOUND: $BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf01-1.txt
```

### VF-01.2: extract_from_turn method
```bash
grep -n "def.*extract_from_turn\|def.*extract.*turn" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf01-2.txt
```
**PASS if:** Per-turn extraction method exists (write trigger from S4.3).

### VF-01.3: regenerate_summary method
```bash
grep -n "def.*regenerate_summary\|def.*summarize" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf01-3.txt
```

### VF-01.4: recalculate_momentum method
```bash
grep -n "def.*recalculate_momentum\|def.*momentum" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf01-4.txt
```

### VF-01.5: save_history method for audit trail
```bash
grep -n "def.*save_history\|def.*history" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf01-5.txt
```

**Gate VF-01:** 5/5 checks pass.

## VF-02 — Extraction Prompt (S4.4)

### VF-02.1: Extraction prompt references deal_id, current_stage, existing facts
```bash
grep -i "deal_id\|current_stage\|existing_facts\|existing_summary" "$BRAIN_SVC" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf02-1.txt
```

### VF-02.2: Output schema includes new_facts, new_risks, new_decisions, new_assumptions, new_open_items
```bash
for FIELD in new_facts new_risks new_decisions new_assumptions new_open_items; do grep "$FIELD" "$BRAIN_SVC"; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf02-2.txt
```
**PASS if:** All 5 extraction output fields present per S4.4 JSON schema.

### VF-02.3: Ghost knowledge detection in extraction
```bash
grep -i "ghost_knowledge\|ghost.*fact" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf02-3.txt
```
**PASS if:** Ghost knowledge detection integrated into extraction per QW-1.

### VF-02.4: Entity extraction in output
```bash
grep -i "entities\|entity_type\|normalized_name" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf02-4.txt
```
**PASS if:** Entity extraction for cross-deal linking per C-4.

### VF-02.5: Contradiction detection
```bash
grep -i "contradiction" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf02-5.txt
```
**PASS if:** Contradictions detected and flagged per S4.4.

### VF-02.6: Confidence threshold < 1.0 for auto-extracted facts
```bash
grep -i "confidence\|0\.\[0-9\]" "$BRAIN_SVC" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf02-6.txt
```
**PASS if:** Auto-extracted facts start at confidence < 1.0 per R3 risk mitigation.

**Gate VF-02:** 6/6 extraction checks verified.

## VF-03 — Drift Detection (S4.5, 3+ mechanisms)

### VF-03.1: Staleness check
```bash
grep -i "staleness\|stale\|last_summarized_turn" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf03-1.txt
```
**PASS if:** Staleness check: last_summarized_turn < max_turn - 10.

### VF-03.2: Contradiction detection and count increment
```bash
grep -i "contradiction_count" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf03-2.txt
```

### VF-03.3: Periodic re-summarization trigger
```bash
grep -i "10.*turns\|periodic\|re.summar" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf03-3.txt
```
**PASS if:** Re-summarization every 10 turns per S4.5.

**Gate VF-03:** 3/3 drift checks verified.

## VF-04 — Momentum Score Calculator (S20.2, QW-2)

### VF-04.1: Calculator file exists
```bash
find /home/zaks/zakops-backend/src -name "*momentum*" -type f 2>/dev/null | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf04-1.txt
```

### VF-04.2: 5 component weights present
```bash
for COMP in stage_velocity event_frequency open_item_completion risk_trajectory action_rate; do grep -r "$COMP" /home/zaks/zakops-backend/src/ --include="*.py" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf04-2.txt
```
**PASS if:** All 5 momentum components present per S20.2 spec.

### VF-04.3: Weight values (0.30, 0.20, 0.20, 0.15, 0.15)
```bash
grep -r "0\.30\|0\.20\|0\.15" /home/zaks/zakops-backend/src/ --include="*.py" | grep -i "weight\|velocity\|frequency\|completion\|risk\|action" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf04-3.txt
```

### VF-04.4: Score range 0-100
```bash
grep -r "round\|0.*100\|score.*100" /home/zaks/zakops-backend/src/ --include="*.py" | grep -i "momentum" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf04-4.txt
```

**Gate VF-04:** 4/4 momentum checks verified.

## VF-05 — DealBrain.tsx UI Component (S4.7)

### VF-05.1: Component file exists
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "DealBrain*" -type f 2>/dev/null | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf05-1.txt
```

### VF-05.2: Displays summary section
```bash
BRAIN_TSX=$(find /home/zaks/zakops-agent-api/apps/dashboard/src -name "DealBrain*" -type f | head -1) && grep -i "summary" "$BRAIN_TSX" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf05-2.txt
```

### VF-05.3: Tab sections for Facts, Risks, Decisions, Assumptions, Open Items
```bash
for TAB in facts risks decisions assumptions open_items; do grep -i "$TAB" "$BRAIN_TSX" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf05-3.txt
```

### VF-05.4: Ghost Knowledge section
```bash
grep -i "ghost" "$BRAIN_TSX" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf05-4.txt
```

### VF-05.5: Momentum score display
```bash
grep -i "momentum" "$BRAIN_TSX" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf05-5.txt
```

**Gate VF-05:** 5/5 UI checks verified.

## VF-06 — Multi-User Identity (S10.2)

### VF-06.1: X-User-Id header in middleware
```bash
grep -i "X-User-Id\|x-user-id\|ZAKOPS_USER_ID" /home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf06-1.txt
```
**PASS if:** X-User-Id header set from env or default.

### VF-06.2: X-User-Role header
```bash
grep -i "X-User-Role\|x-user-role" /home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf06-2.txt
```

### VF-06.3: Agent API reads user_id from header
```bash
grep -rn "X-User-Id\|x-user-id\|user_id.*header" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf06-3.txt
```

**Gate VF-06:** 3/3 multi-user checks verified.

## VF-07 — Ghost Knowledge Detector (S20.1, QW-1)

### VF-07.1: Detector file or integration exists
```bash
find /home/zaks/zakops-backend/src -name "*ghost*" -type f 2>/dev/null; grep -rl "ghost_knowledge\|GhostKnowledge" /home/zaks/zakops-backend/src/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf07-1.txt
```

### VF-07.2: Detection logic — user references facts NOT in brain
```bash
grep -rn "not.*in.*facts\|missing.*fact\|unrecorded\|ghost" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf07-2.txt
```

### VF-07.3: Confirm/dismiss workflow
```bash
grep -rn "confirm.*ghost\|promote.*fact\|user_assertion\|dismiss" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/vf07-3.txt
```

**Gate VF-07:** 3/3 ghost knowledge checks verified.

---

## Cross-Consistency

### XC-1: DealBrainService writes to deal_brain table
```bash
grep "deal_brain" "$BRAIN_SVC" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/xc1.txt
```

### XC-2: Momentum score stored in deal_brain.momentum_score
```bash
grep -i "momentum_score" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/xc2.txt
```

### XC-3: Brain history saved on every update
```bash
grep -i "deal_brain_history\|save_history\|history" "$BRAIN_SVC" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/xc3.txt
```

---

## Stress Tests

### ST-1: No direct cross-DB queries from brain service to zakops_agent
```bash
grep -i "zakops_agent\|chat_threads\|chat_messages" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/st1.txt
```
**PASS if:** Zero direct cross-DB queries. Uses outbox for cross-DB communication.

### ST-2: Extraction uses cost-effective model tier
```bash
grep -i "flash\|gemini.*flash\|cheap\|cost.*effective\|summarization.*tier" "$BRAIN_SVC" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m05/st2.txt
```
**PASS if:** Extraction uses Gemini Flash or equivalent cheap tier per S4.4.

---

## Enhancement Opportunities

- **ENH-1**: Add fact lineage tracking linking each fact to its source message
- **ENH-2**: Implement Ebbinghaus forgetting curve for fact confidence decay
- **ENH-3**: Add email integration bridge for DealBrainService.extract_from_email()

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Service Class) | 5 | |
| VF-02 (Extraction) | 6 | |
| VF-03 (Drift Detection) | 3 | |
| VF-04 (Momentum) | 4 | |
| VF-05 (UI Component) | 5 | |
| VF-06 (Multi-User) | 3 | |
| VF-07 (Ghost Knowledge) | 3 | |
| XC | 3 | |
| ST | 2 | |
| **TOTAL** | **36** | |

## Stop Condition

**DONE when:** All 36 gates produce evidence files. Do NOT proceed to M06.

---

# MISSION: QA-COL-M06-VERIFY-001
## QA Verification: Injection Guard & Security Pipeline
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M06-SECURITY-PIPELINE (Execution complete)
## Successor: QA-COL-M07-VERIFY-001

## Mission Objective

Spec-level verification of the **4-layer security pipeline**: rule-based injection guard, structural separation, session-level escalation, and canary tokens.
Every regex pattern, severity level, response matrix action, and canary token mechanism is checked against S7.2–S7.4.

**Source spec:** S7.2 (unified pipeline), S7.3 (4 layers), S7.4 (response matrix)
**Files expected:** injection_guard.py, canary_token_manager.py, session_tracker.py
**Patterns:** 15 regex patterns, 3 severity levels, 4 response actions

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m06 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/pf2-dir.txt
```

---

## Verification Families

## VF-01 — Injection Guard File & Class (S7.3 Layer 1)

### VF-01.1: injection_guard.py exists
```bash
IG_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "injection_guard.py" -type f 2>/dev/null | head -1) && echo "FOUND: $IG_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf01-1.txt
```

### VF-01.2: ScanResult dataclass
```bash
grep "class ScanResult\|ScanResult" "$IG_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf01-2.txt
```

### VF-01.3: ScanResult fields — passed, patterns_found, severity, sanitized_content
```bash
for FIELD in passed patterns_found severity sanitized_content; do grep "$FIELD" "$IG_FILE" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf01-3.txt
```

### VF-01.4: scan_input function
```bash
grep "def scan_input\|def scan" "$IG_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf01-4.txt
```

**Gate VF-01:** 4/4 checks pass.

## VF-02 — Injection Patterns (S7.3, 15 patterns across 3 severities)

### VF-02.1: HIGH severity patterns (5 patterns)
```bash
for PATTERN in "instruction_override" "role_hijack" "system_override" "safety_override" "prompt_extraction"; do grep "$PATTERN" "$IG_FILE" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf02-1.txt
```
**PASS if:** All 5 HIGH patterns present: instruction_override, role_hijack, system_override, safety_override, prompt_extraction.

### VF-02.2: MEDIUM severity patterns (4 patterns)
```bash
for PATTERN in "role_injection" "format_injection" "fenced_injection" "chatml_injection"; do grep "$PATTERN" "$IG_FILE" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf02-2.txt
```

### VF-02.3: LOW severity patterns (4 patterns)
```bash
for PATTERN in "xss_attempt" "sql_injection"; do grep "$PATTERN" "$IG_FILE" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf02-3.txt
```

### VF-02.4: Total pattern count >= 15
```bash
grep -c "pattern\|INJECTION_PATTERN" "$IG_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf02-4.txt
```

### VF-02.5: Regex patterns for key attacks
```bash
{ grep "ignore.*previous.*instructions" "$IG_FILE" | head -1; grep "you.*are.*now.*a" "$IG_FILE" | head -1; grep "reveal.*prompt" "$IG_FILE" | head -1; grep "ASSISTANT" "$IG_FILE" | head -1; grep "im_start\|im_end" "$IG_FILE" | head -1; } | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf02-5.txt
```

### VF-02.6: Severity ordering — SEVERITY_ORDER dict
```bash
grep "SEVERITY_ORDER\|severity.*order" "$IG_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf02-6.txt
```

**Gate VF-02:** 6/6 pattern checks verified.

## VF-03 — Canary Token Manager (S7.3 Layer 4, V2 I-1 QW-3)

### VF-03.1: Canary token file exists
```bash
CT_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "canary*" -type f 2>/dev/null | head -1) && echo "FOUND: $CT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf03-1.txt
```

### VF-03.2: CanaryTokenManager class
```bash
grep "class CanaryTokenManager\|CanaryToken" "$CT_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf03-2.txt
```

### VF-03.3: inject_canary method
```bash
grep "def inject_canary\|def inject" "$CT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf03-3.txt
```

### VF-03.4: verify_no_leakage method
```bash
grep "def verify_no_leakage\|def verify" "$CT_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf03-4.txt
```

### VF-03.5: Sensitivity filtering — only high/critical chunks get canaries
```bash
grep -i "high\|critical\|sensitivity" "$CT_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf03-5.txt
```

### VF-03.6: Token format uses CANARY- prefix + hash
```bash
grep "CANARY\|hashlib\|sha256\|token" "$CT_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf03-6.txt
```

**Gate VF-03:** 6/6 canary checks verified.

## VF-04 — Session Escalation Tracker (S7.3 Layer 3)

### VF-04.1: Session tracker exists
```bash
ST_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "session_tracker*" -o -name "injection_tracker*" | head -1) && echo "FOUND: $ST_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf04-1.txt
```

### VF-04.2: MAX_ATTEMPTS_BEFORE_LOCKDOWN = 3
```bash
grep -r "MAX_ATTEMPTS\|LOCKDOWN\|3.*attempt\|lockdown" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf04-2.txt
```
**PASS if:** Lockdown after 3 injection attempts per S7.3.

### VF-04.3: record_attempt method
```bash
grep -r "def record_attempt\|def record" /home/zaks/zakops-agent-api/apps/agent-api/app/core/security/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf04-3.txt
```

**Gate VF-04:** 3/3 escalation checks verified.

## VF-05 — Security Pipeline Integration (S7.2)

### VF-05.1: Injection guard called before LLM in chat orchestrator or graph
```bash
grep -rn "scan_input\|injection_guard\|InjectionGuard" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "test\|__pycache__" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf05-1.txt
```
**PASS if:** InjectionGuard imported and called in the request path.

### VF-05.2: Canary tokens injected before LLM call
```bash
grep -rn "inject_canary\|CanaryToken" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "test\|__pycache__" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf05-2.txt
```

### VF-05.3: Canary verification after LLM response
```bash
grep -rn "verify_no_leakage" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "test\|__pycache__" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf05-3.txt
```

### VF-05.4: Sanitization applied for found patterns
```bash
grep -r "sanitize\|FILTERED\|\[FILTERED\]" "$IG_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf05-4.txt
```

**Gate VF-05:** 4/4 integration checks verified.

## VF-06 — Response Matrix (S7.4)

### VF-06.1: Low severity — log + sanitize + continue
```bash
grep -i "low.*log\|low.*sanitize\|log.*continue" "$IG_FILE" | head -2 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf06-1.txt
```

### VF-06.2: High severity — log + sanitize + toast + tracker
```bash
grep -i "high.*block\|high.*tracker\|escalat" "$IG_FILE" | head -2 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf06-2.txt
```

### VF-06.3: Canary leaked — BLOCK response
```bash
grep -r "block\|BLOCK\|leaked" "$CT_FILE" 2>/dev/null | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/vf06-3.txt
```

**Gate VF-06:** 3/3 response matrix checks verified.

---

## Cross-Consistency

### XC-1: Injection guard integrated in both backend and agent paths
```bash
grep -rn "injection_guard\|InjectionGuard\|scan_input" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | wc -l | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/xc1.txt
```

### XC-2: INJECTION_GUARD_MODE env var for observe/enforce toggle (R5)
```bash
grep -r "INJECTION_GUARD_MODE\|observe\|enforce" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/xc2.txt
```

---

## Stress Tests

### ST-1: No eval() or exec() in security files
```bash
grep -n "eval(\|exec(" "$IG_FILE" "$CT_FILE" 2>/dev/null | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/st1.txt
```
**PASS if:** Zero — security code must not use eval/exec.

### ST-2: Regex patterns use re.IGNORECASE
```bash
grep "re.IGNORECASE\|IGNORECASE\|re.I" "$IG_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m06/st2.txt
```

---

## Enhancement Opportunities

- **ENH-1**: Add metrics endpoint for injection detection rates (observe mode analytics)
- **ENH-2**: Implement BERT-based semantic firewall (Bucket 3, S7.3 Layer 5)
- **ENH-3**: Add admin dashboard for reviewing blocked injection attempts

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Guard File) | 4 | |
| VF-02 (Patterns) | 6 | |
| VF-03 (Canary Tokens) | 6 | |
| VF-04 (Session Tracker) | 3 | |
| VF-05 (Integration) | 4 | |
| VF-06 (Response Matrix) | 3 | |
| XC | 2 | |
| ST | 2 | |
| **TOTAL** | **32** | |

## Stop Condition

**DONE when:** All 32 gates produce evidence files. Do NOT proceed to M07.

---

# MISSION: QA-COL-M07-VERIFY-001
## QA Verification: Delete, Retention, Legal Hold, GDPR
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M07-DELETE-RETENTION (Execution complete)
## Successor: QA-COL-M08-VERIFY-001

## Mission Objective

Spec-level verification of **cascading delete**, **retention policies**, **legal hold**, **GDPR deletion**, and **cross-DB reconciliation**.
Every delete cascade step, retention interval, legal hold check, and GDPR table is checked against S11.1–S11.5, S11.3 (DealReferenceValidator).

**Source spec:** S11.1 (delete semantics), S11.2 (cascading hard delete, 6 steps), S11.3 (cross-DB reconciliation), S11.4 (retention policy, 8 data types), S11.5 (GDPR cascade, 20 tables)
**Files expected:** chat_retention.py, deal_reference_validator.py, 029_legal_hold.sql

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m07 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/pf2-dir.txt
```

---

## Verification Families

## VF-01 — Migration 029 Legal Hold

### VF-01.1: Migration file exists
```bash
M029=$(find /home/zaks/zakops-backend -name "029_legal_hold*" -type f 2>/dev/null | head -1) && echo "FOUND: $M029" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf01-1.txt
```

### VF-01.2: Rollback exists
```bash
M029R=$(find /home/zaks/zakops-backend -name "029*rollback*" -type f 2>/dev/null | head -1) && echo "FOUND: $M029R" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf01-2.txt
```

### VF-01.3: Migration tracking
```bash
grep "INSERT INTO.*schema_migrations.*029" "$M029" 2>/dev/null | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf01-3.txt
```

**Gate VF-01:** 3/3 checks pass.

## VF-02 — Cascading Hard Delete (S11.2, 6 steps)

### VF-02.1: Delete implementation file exists
```bash
RET_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "chat_retention*" -o -name "*retention*" -o -name "*delete*" | grep -v test | head -1) && echo "FOUND: $RET_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-1.txt
```

### VF-02.2: Step 1 — Delete session_summaries WHERE thread_id
```bash
grep -rn "session_summaries" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "delete" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-2.txt
```

### VF-02.3: Step 2 — Delete turn_snapshots WHERE thread_id
```bash
grep -rn "turn_snapshots" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "delete" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-3.txt
```

### VF-02.4: Step 3 — Delete cost_ledger WHERE thread_id
```bash
grep -rn "cost_ledger" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "delete" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-4.txt
```

### VF-02.5: Step 4 — Delete cross_db_outbox WHERE thread_id in payload
```bash
grep -rn "cross_db_outbox" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "delete" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-5.txt
```

### VF-02.6: Step 5 — Anonymize decision_ledger (not delete)
```bash
grep -rn "decision_ledger" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "ANONYMIZE\|DELETED\|REDACTED\|UPDATE.*SET.*user_id" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-6.txt
```
**PASS if:** decision_ledger is ANONYMIZED (not deleted) per S11.2.

### VF-02.7: Step 6 — Delete LangGraph checkpoints
```bash
grep -rn "checkpoints\|checkpoint_blobs\|checkpoint_writes" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "delete" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-7.txt
```

### VF-02.8: Delete order — derived data first, then thread last
```bash
grep -rn "def.*hard_delete\|def.*cascade_delete" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf02-8.txt
```

**Gate VF-02:** 8/8 cascading delete steps verified.

## VF-03 — Legal Hold Enforcement

### VF-03.1: Legal hold blocks soft delete
```bash
grep -rn "legal_hold" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "block\|409\|Conflict\|cannot\|prevent" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf03-1.txt
```
**PASS if:** Returns 409 Conflict when legal_hold=TRUE.

### VF-03.2: Legal hold blocks hard delete
```bash
grep -rn "legal_hold.*hard\|hard.*legal_hold" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf03-2.txt
```

### VF-03.3: Legal hold blocks auto-purge retention job
```bash
grep -rn "legal_hold" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "skip\|retention\|purge" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf03-3.txt
```

**Gate VF-03:** 3/3 legal hold checks verified.

## VF-04 — Retention Policy (S11.4, 8 data types)

### VF-04.1: Soft-deleted threads — 30 day retention
```bash
grep -rn "30.*day\|INTERVAL.*30" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf04-1.txt
```

### VF-04.2: Turn snapshots — 90 day default retention
```bash
grep -rn "90.*day\|INTERVAL.*90" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf04-2.txt
```

### VF-04.3: Outbox done entries — 7 day retention
```bash
grep -rn "7.*day.*outbox\|outbox.*7.*day\|cross_db_outbox.*done" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf04-3.txt
```

### VF-04.4: Compliance tier — 7 year retention
```bash
grep -rn "7.*year\|compliance.*retention\|INTERVAL.*7.*year" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf04-4.txt
```

**Gate VF-04:** 4/4 retention intervals verified.

## VF-05 — Cross-DB Reconciliation (S11.3, GAP-H4)

### VF-05.1: DealReferenceValidator class
```bash
VALIDATOR_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "*deal_reference*" -o -name "*validator*" | grep -v test | head -1) && grep "class DealReferenceValidator\|class.*Validator" "$VALIDATOR_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf05-1.txt
```

### VF-05.2: validate_deal_exists method
```bash
grep -n "def.*validate_deal_exists\|def.*validate.*deal" "$VALIDATOR_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf05-2.txt
```

### VF-05.3: reconcile_orphans method
```bash
grep -n "def.*reconcile_orphans\|def.*reconcile" "$VALIDATOR_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf05-3.txt
```

### VF-05.4: Uses backend API for cross-DB check (not direct query)
```bash
grep -i "backend.*api\|/api/deals\|client.*get" "$VALIDATOR_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf05-4.txt
```

**Gate VF-05:** 4/4 reconciliation checks verified.

## VF-06 — GDPR Full Deletion (S11.5, 20 tables)

### VF-06.1: GDPR deletion function/endpoint exists
```bash
grep -rn "def.*gdpr_delete\|def.*full_deletion\|def.*delete_user\|DELETE.*user.*account" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf06-1.txt
```

### VF-06.2: Covers zakops_agent tables (chat_messages, session_summaries, turn_snapshots, cost_ledger, cross_db_outbox, chat_threads, thread_ownership)
```bash
for TABLE in chat_messages session_summaries turn_snapshots cost_ledger cross_db_outbox chat_threads thread_ownership; do grep -rn "$TABLE" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "delete\|gdpr" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf06-2.txt
```

### VF-06.3: user_identity_map deleted (step 15 in spec)
```bash
grep -rn "user_identity_map" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "delete" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf06-3.txt
```

### VF-06.4: Anonymization of audit tables (decision_ledger, audit_log)
```bash
grep -rn "ANONYMIZE\|DELETED\|REDACTED" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/vf06-4.txt
```

**Gate VF-06:** 4/4 GDPR checks verified.

---

## Cross-Consistency

### XC-1: Every cascade table in S11.2 is also in ChatRepository.hard_delete_thread
```bash
grep -rn "def.*hard_delete" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" -A 30 | head -40 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/xc1.txt
```

### XC-2: Retention intervals match spec table S11.4
```bash
grep -rn "INTERVAL\|days\|year" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "retention\|purge\|cleanup" | head -10 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/xc2.txt
```

---

## Stress Tests

### ST-1: No direct DELETE without legal_hold check
```bash
grep -rn "DELETE FROM chat_threads\|DELETE FROM chat_messages" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "legal_hold\|test" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/st1.txt
```
**PASS if:** All direct deletes are preceded by legal_hold checks.

### ST-2: GDPR uses single transaction per database
```bash
grep -rn "transaction\|BEGIN\|COMMIT\|atomic" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "gdpr\|delete_user\|full_delete" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m07/st2.txt
```

---

## Enhancement Opportunities

- **ENH-1**: Add verification SQL from S11.4 to check retention policy enforcement
- **ENH-2**: Add dead-letter alerting for failed outbox entries after 3 retries
- **ENH-3**: Add audit trail for GDPR deletion requests (who requested, when completed)

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Migration 029) | 3 | |
| VF-02 (Cascading Delete) | 8 | |
| VF-03 (Legal Hold) | 3 | |
| VF-04 (Retention) | 4 | |
| VF-05 (Reconciliation) | 4 | |
| VF-06 (GDPR) | 4 | |
| XC | 2 | |
| ST | 2 | |
| **TOTAL** | **32** | |

## Stop Condition

**DONE when:** All 32 gates produce evidence files. Do NOT proceed to M08.

---

# MISSION: QA-COL-M08-VERIFY-001
## QA Verification: Tool Scoping & Least Privilege
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M08-TOOL-SCOPING (Execution complete)
## Successor: QA-COL-M09-VERIFY-001

## Mission Objective

Spec-level verification of **SCOPE_TOOL_MAP**, **ROLE_TOOL_MAP**, **generalized tool verification**, and **schema-validated tool arguments**.
Every scope-tool mapping, role-tool permission, post-condition assertion, and Pydantic schema is checked against S9.2–S9.7.

**Source spec:** S9.2 (scope map), S9.3 (role map), S9.4 (generalized verification QW-12), S9.5 (schema validation QW-11), S9.7 (expanded HITL)

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m08 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/pf2-dir.txt
```

---

## Verification Families

## VF-01 — Scope Tool Map (S9.2)

### VF-01.1: SCOPE_TOOL_MAP defined
```bash
SCOPE_FILE=$(grep -rl "SCOPE_TOOL_MAP" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -1) && grep "SCOPE_TOOL_MAP" "$SCOPE_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf01-1.txt
```

### VF-01.2: Global scope — list_deals, search_deals, duckduckgo_results_json only
```bash
grep -A5 '"global"' "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf01-2.txt
```
**PASS if:** Global scope has exactly 3 tools: list_deals, search_deals, duckduckgo_results_json.

### VF-01.3: Deal scope — all 8 tools
```bash
grep -A10 '"deal"' "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf01-3.txt
```

### VF-01.4: Document scope — restricted set
```bash
grep -A5 '"document"' "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf01-4.txt
```
**PASS if:** Document scope has only: duckduckgo_results_json, get_deal, get_deal_health.

**Gate VF-01:** 4/4 scope checks verified.

## VF-02 — Role Tool Map (S9.3)

### VF-02.1: ROLE_TOOL_MAP defined
```bash
grep "ROLE_TOOL_MAP" "$SCOPE_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf02-1.txt
```

### VF-02.2: VIEWER — read-only tools only
```bash
grep -A5 '"VIEWER"' "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf02-2.txt
```
**PASS if:** VIEWER has: list_deals, search_deals, get_deal, get_deal_health, duckduckgo_results_json.

### VF-02.3: OPERATOR — adds add_note
```bash
grep -A5 '"OPERATOR"' "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf02-3.txt
```

### VF-02.4: APPROVER — adds transition_deal, create_deal
```bash
grep -A5 '"APPROVER"' "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf02-4.txt
```

### VF-02.5: ADMIN — all tools ("*")
```bash
grep -A3 '"ADMIN"' "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf02-5.txt
```

**Gate VF-02:** 5/5 role checks verified.

## VF-03 — HITL Tools (S9.7)

### VF-03.1: HITL_TOOLS frozenset defined
```bash
grep "HITL_TOOLS" "$SCOPE_FILE" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf03-1.txt
```

### VF-03.2: transition_deal and create_deal in HITL set
```bash
grep -A5 "HITL_TOOLS" "$SCOPE_FILE" | grep "transition_deal\|create_deal" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf03-2.txt
```

**Gate VF-03:** 2/2 HITL checks verified.

## VF-04 — Generalized Tool Verification (S9.4, QW-12)

### VF-04.1: TOOL_POST_CONDITIONS dict defined
```bash
grep -rn "TOOL_POST_CONDITIONS\|post_condition" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf04-1.txt
```

### VF-04.2: Post-conditions for transition_deal, create_deal, add_note
```bash
for TOOL in transition_deal create_deal add_note; do grep -r "$TOOL" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "post.*condition\|verify\|assert" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf04-2.txt
```

### VF-04.3: execute_with_verification function
```bash
grep -rn "def.*execute_with_verification\|def.*verify.*tool" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf04-3.txt
```

**Gate VF-04:** 3/3 verification checks verified.

## VF-05 — Schema-Validated Tool Arguments (S9.5, QW-11)

### VF-05.1: Pydantic models with extra="forbid"
```bash
grep -rn 'extra.*=.*"forbid"\|extra="forbid"' /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf05-1.txt
```
**PASS if:** At least 1 tool input model uses extra="forbid" to catch hallucinated args.

### VF-05.2: TransitionDealInput model with forbid
```bash
grep -rn "class TransitionDealInput\|TransitionDealInput" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf05-2.txt
```

### VF-05.3: model_validate or model_validate_json usage
```bash
grep -rn "model_validate\|model_validate_json" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf05-3.txt
```

**Gate VF-05:** 3/3 schema validation checks verified.

## VF-06 — Scope Filter Integration

### VF-06.1: Scope filter applied in LangGraph tool node
```bash
grep -rn "scope_filter\|ScopeFilter\|filter_tools" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf06-1.txt
```

### VF-06.2: Both scope AND role checked (dual enforcement)
```bash
grep -rn "scope.*role\|role.*scope\|SCOPE_TOOL_MAP.*ROLE_TOOL_MAP" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/vf06-2.txt
```

**Gate VF-06:** 2/2 integration checks verified.

---

## Cross-Consistency

### XC-1: All 8 current tools appear in at least one scope
```bash
for TOOL in list_deals search_deals get_deal get_deal_health add_note transition_deal create_deal duckduckgo_results_json; do grep "$TOOL" "$SCOPE_FILE" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/xc1.txt
```

### XC-2: Tool inventory matches Appendix B (8 tools)
```bash
grep -c "frozenset\|\"[a-z_]*\"" "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/xc2.txt
```

---

## Stress Tests

### ST-1: No tool accessible in all scopes except via ADMIN role
```bash
grep -A20 "SCOPE_TOOL_MAP" "$SCOPE_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m08/st1.txt
```
**PASS if:** No tool appears in global, deal, AND document scopes (document is restricted).

---

## Enhancement Opportunities

- **ENH-1**: Add MCP tool governance integration (S19.6 — bring 12 MCP tools under COL)
- **ENH-2**: Consider logging tool access denials for security audit
- **ENH-3**: Add JIT (Just-in-Time) tool access for future enterprise needs (S9.6)

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Scope Map) | 4 | |
| VF-02 (Role Map) | 5 | |
| VF-03 (HITL) | 2 | |
| VF-04 (Post-Conditions) | 3 | |
| VF-05 (Schema Validation) | 3 | |
| VF-06 (Integration) | 2 | |
| XC | 2 | |
| ST | 1 | |
| **TOTAL** | **24** | |

## Stop Condition

**DONE when:** All 24 gates produce evidence files. Do NOT proceed to M09.

---

# MISSION: QA-COL-M09-VERIFY-001
## QA Verification: Write Path & Migration Script
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M09-WRITE-PATH (Execution complete)
## Successor: QA-COL-M10-VERIFY-001

## Mission Objective

Spec-level verification of the **end-to-end write path** and **data migration script** (backfill from SQLite/localStorage to PostgreSQL).
Every write step, injection guard hook, cost recording, brain extraction, and migration phase is checked against S3.7–S3.8.

**Source spec:** S3.7 (migration script), S3.8 (write path — 5 writes per turn)
**Files expected:** migrate_chat_data.py (new), modifications to chat_orchestrator.py and graph.py

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m09 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/pf2-dir.txt
```

---

## Verification Families

## VF-01 — Migration Script (S3.7)

### VF-01.1: migrate_chat_data.py exists
```bash
MIG_SCRIPT=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "migrate_chat_data*" -type f 2>/dev/null | head -1) && echo "FOUND: $MIG_SCRIPT" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-1.txt
```

### VF-01.2: Reads SQLite sessions
```bash
grep -i "sqlite\|chat_persistence\|ChatSessionStore" "$MIG_SCRIPT" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-2.txt
```

### VF-01.3: Creates chat_threads rows
```bash
grep -i "chat_threads\|create_thread" "$MIG_SCRIPT" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-3.txt
```

### VF-01.4: Creates chat_messages rows with turn_numbers
```bash
grep -i "chat_messages\|turn_number\|add_message" "$MIG_SCRIPT" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-4.txt
```

### VF-01.5: Creates thread_ownership rows
```bash
grep -i "thread_ownership\|ownership" "$MIG_SCRIPT" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-5.txt
```

### VF-01.6: GAP-H5 — SQLite user/session migration to user_identity_map
```bash
grep -i "user_identity_map\|canonical_id\|external_ids" "$MIG_SCRIPT" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-6.txt
```

### VF-01.7: GAP-M5 — Historical data in DEFAULT partition, marked as backfilled
```bash
grep -i "backfill\|DEFAULT\|historical\|timing.*backfill" "$MIG_SCRIPT" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-7.txt
```

### VF-01.8: Logging — total_threads, total_messages, total_users_migrated
```bash
grep -i "total_threads\|total_messages\|total_users\|conflicts_resolved\|log" "$MIG_SCRIPT" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf01-8.txt
```

**Gate VF-01:** 8/8 migration script checks verified.

## VF-02 — Write Path (S3.8, 5 writes per turn)

### VF-02.1: WRITE #1 — ChatRepository.add_message(role="user")
```bash
grep -rn "add_message.*user\|role.*user.*add_message" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v test | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf02-1.txt
```

### VF-02.2: InjectionGuard.scan() before LLM call
```bash
grep -rn "scan_input\|InjectionGuard" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "test\|security" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf02-2.txt
```

### VF-02.3: WRITE #2 — ChatRepository.add_message(role="assistant") with citations, proposals
```bash
grep -rn "add_message.*assistant\|role.*assistant" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v test | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf02-3.txt
```

### VF-02.4: WRITE #3 — CostLedger.record()
```bash
grep -rn "cost_ledger\|CostLedger\|record.*cost\|cost.*record" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v test | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf02-4.txt
```

### VF-02.5: WRITE #4 — Summarizer.maybe_summarize() (conditional)
```bash
grep -rn "maybe_summarize\|should_summarize\|summariz" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v test | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf02-5.txt
```

### VF-02.6: WRITE #5 — Outbox.enqueue_brain_extraction() (async, cross-DB)
```bash
grep -rn "enqueue_brain\|outbox.*brain\|brain_extract" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v test | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf02-6.txt
```

### VF-02.7: localStorage write is CACHE ONLY (not canonical)
```bash
grep -rn "localStorage\|setItem" /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.ts" --include="*.tsx" | grep -i "cache\|chat" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/vf02-7.txt
```

**Gate VF-02:** 7/7 write path steps verified.

---

## Cross-Consistency

### XC-1: Write path uses ChatRepository (not direct SQL)
```bash
grep -rn "ChatRepository\|chat_repository" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v "test\|__pycache__" | wc -l | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/xc1.txt
```

### XC-2: Migration script references all M01 tables
```bash
for TABLE in chat_threads chat_messages thread_ownership user_identity_map; do grep "$TABLE" "$MIG_SCRIPT" | head -1; done | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/xc2.txt
```

---

## Stress Tests

### ST-1: Migration handles duplicates (ON CONFLICT or check)
```bash
grep -i "ON CONFLICT\|conflict\|duplicate\|skip\|exists" "$MIG_SCRIPT" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/st1.txt
```

### ST-2: No turn_snapshots backfill for historical data (GAP-M5)
```bash
grep -i "turn_snapshot.*backfill\|backfill.*snapshot" "$MIG_SCRIPT" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m09/st2.txt
```
**PASS if:** Zero — historical data lacks required fields for snapshots.

---

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Migration Script) | 8 | |
| VF-02 (Write Path) | 7 | |
| XC | 2 | |
| ST | 2 | |
| **TOTAL** | **21** | |

## Stop Condition

**DONE when:** All 21 gates produce evidence files. Do NOT proceed to M10.

---

# MISSION: QA-COL-M10-VERIFY-001
## QA Verification: Summarization & Tiered Memory
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M10-SUMMARIZATION (Execution complete)
## Successor: QA-COL-M11-VERIFY-001

## Mission Objective

Spec-level verification of **summarization system**, **MemGPT-style tiered memory** (Working + Recall + Archival), and **background consolidation worker**.
Every summarization trigger, prompt template, memory tier, and worker mechanism is checked against S5.1–S5.5.

**Source spec:** S5.2 (tiered memory), S5.3 (summarization design), S5.4 (consolidation worker), S5.5 (MemoryStatePanel UI)

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m10 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/pf2-dir.txt
```

---

## Verification Families

## VF-01 — Summarizer (S5.3)

### VF-01.1: Summarizer file exists
```bash
SUM_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -o -name "summarizer.py" -o -name "*summar*" 2>/dev/null | grep -v test | grep "\.py$" | head -1); find /home/zaks/zakops-backend/src -name "summarizer*" -o -name "*summar*.py" 2>/dev/null | head -1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf01-1.txt
```

### VF-01.2: Trigger condition — every 5 turns
```bash
grep -rn "5.*turn\|turn.*5\|turn_number.*%.*5\|should_summarize" /home/zaks/zakops-backend/src/ /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf01-2.txt
```
**PASS if:** Summarization triggers every 5 turns per S5.3.

### VF-01.3: Step 1 — Extractive pre-filter (message selection)
```bash
grep -rn "extract\|pre.filter\|select.*message\|weight\|decay\|0\.9" /home/zaks/zakops-backend/src/ --include="*.py" | grep -i "summar" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf01-3.txt
```

### VF-01.4: Step 2 — LLM summarization prompt
```bash
grep -rn "summarize\|summary.*prompt\|Summarize this.*conversation" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf01-4.txt
```

### VF-01.5: Step 3 — Writes session_summaries row
```bash
grep -rn "session_summaries\|summary.*version\|summary.*persist" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf01-5.txt
```

### VF-01.6: Uses cost-effective model (Gemini Flash ~0.1¢)
```bash
grep -rn "flash\|gemini.*flash\|cost.*effective\|cheap" /home/zaks/zakops-backend/src/ --include="*.py" | grep -i "summar" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf01-6.txt
```

**Gate VF-01:** 6/6 summarizer checks verified.

## VF-02 — Tiered Memory (S5.2)

### VF-02.1: Working Memory — last 6 messages in context
```bash
grep -rn "max_messages.*6\|6.*message\|working.*memory" /home/zaks/zakops-agent-api/apps/agent-api/app/ /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf02-1.txt
```

### VF-02.2: Recall Memory — Deal Brain facts + rolling summaries injected as context
```bash
grep -rn "recall\|brain.*facts\|rolling.*summary\|inject.*context" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf02-2.txt
```

### VF-02.3: memory_tier field in session_summaries
```bash
grep -rn "memory_tier" /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf02-3.txt
```

**Gate VF-02:** 3/3 tiered memory checks verified.

## VF-03 — Background Consolidation Worker (S5.4)

### VF-03.1: Worker class exists
```bash
find /home/zaks/zakops-agent-api/apps/agent-api -name "*consolidation*" -o -name "*memory_worker*" | head -3; find /home/zaks/zakops-backend/src -name "*consolidation*" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf03-1.txt
```

### VF-03.2: Idle threshold (>10 minutes)
```bash
grep -rn "10.*min\|IDLE_THRESHOLD\|idle.*threshold\|timedelta.*10" /home/zaks/zakops-backend/src/ /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf03-2.txt
```

### VF-03.3: Forgetting curve application
```bash
grep -rn "forgetting\|decay.*confidence\|ebbinghaus\|reinforcement_count" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf03-3.txt
```

**Gate VF-03:** 3/3 consolidation checks verified.

## VF-04 — MemoryStatePanel UI (S5.5)

### VF-04.1: Component file exists
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*MemoryState*" -o -name "*memory*panel*" -o -name "*memory*state*" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf04-1.txt
```

### VF-04.2: Shows Working, Recall, Archival tiers
```bash
MEMORY_TSX=$(find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*MemoryState*" -o -name "*memory*" | grep -i "panel\|state" | head -1) && grep -i "working\|recall\|archival" "$MEMORY_TSX" 2>/dev/null | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/vf04-2.txt
```

**Gate VF-04:** 2/2 UI checks verified.

---

## Cross-Consistency / Stress Tests

### XC-1: Summarizer writes to session_summaries table from M01
```bash
grep -rn "session_summaries" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/xc1.txt
```

### ST-1: No hardcoded token limits (should use config)
```bash
grep -rn "2000\|MAX_TOKENS" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v test | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m10/st1.txt
```

---

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Summarizer) | 6 | |
| VF-02 (Tiered Memory) | 3 | |
| VF-03 (Consolidation) | 3 | |
| VF-04 (UI) | 2 | |
| XC | 1 | |
| ST | 1 | |
| **TOTAL** | **18** | |

## Stop Condition

**DONE when:** All 18 gates produce evidence files. Do NOT proceed to M11.

---

# MISSION: QA-COL-M11-VERIFY-001
## QA Verification: Cost Governance & Observability
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-M11-COST-GOVERNANCE (Execution complete)
## Successor: QA-COL-M12-VERIFY-001

## Mission Objective

Spec-level verification of **persistent cost ledger**, **deal budgets**, **predictive budgeting**, and **bottleneck heatmap**.
Every cost recording field, budget threshold, prediction formula, and UI surface is checked against S13.1–S13.7.

**Source spec:** S13.2 (persistent ledger), S13.3 (deal_budgets GAP-C1), S13.4 (predictive QW-8), S13.5 (enforcement), S13.6 (heatmap QW-9)

---

## Pre-Flight

### PF-1: Validation Baseline
```bash
make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/pf1-validate.txt
```

### PF-2: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/col-m11 && echo "CREATED" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/pf2-dir.txt
```

---

## Verification Families

## VF-01 — Cost Repository

### VF-01.1: Cost repository file exists
```bash
COST_FILE=$(find /home/zaks/zakops-agent-api/apps/agent-api -name "cost_repository*" -o -name "cost_*" | grep -v test | grep "\.py$" | head -1) && echo "FOUND: $COST_FILE" | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf01-1.txt
```

### VF-01.2: record() method writes to cost_ledger
```bash
grep -rn "def.*record\|cost_ledger.*INSERT" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "cost" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf01-2.txt
```

### VF-01.3: Records model, provider, tokens, cost_usd
```bash
grep -rn "model\|provider\|input_tokens\|output_tokens\|cost_usd" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -i "cost.*record\|ledger" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf01-3.txt
```

**Gate VF-01:** 3/3 checks pass.

## VF-02 — Budget Enforcement (S13.5)

### VF-02.1: Budget check before LLM call
```bash
grep -rn "budget.*check\|check.*budget\|budget.*enforce\|hard_cap" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf02-1.txt
```

### VF-02.2: Hard cap blocks, soft threshold warns
```bash
grep -rn "hard_cap\|alert_threshold\|budget_warning\|SSE.*budget" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf02-2.txt
```

**Gate VF-02:** 2/2 checks pass.

## VF-03 — Predictive Budgeting (S13.4, QW-8)

### VF-03.1: Rolling 7-day average daily cost
```bash
grep -rn "avg_daily\|7.*day.*average\|rolling.*average" /home/zaks/zakops-agent-api/apps/agent-api/app/ /home/zaks/zakops-backend/src/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf03-1.txt
```

### VF-03.2: Budget exhaustion date prediction
```bash
grep -rn "exhaustion\|budget_exhaustion_date\|days_until" /home/zaks/zakops-agent-api/apps/agent-api/app/ /home/zaks/zakops-backend/src/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf03-2.txt
```

### VF-03.3: Projected monthly spend
```bash
grep -rn "projected_monthly\|projected.*month" /home/zaks/zakops-agent-api/apps/agent-api/app/ /home/zaks/zakops-backend/src/ --include="*.py" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf03-3.txt
```

**Gate VF-03:** 3/3 predictive checks verified.

## VF-04 — Bottleneck Heatmap (S13.6, QW-9)

### VF-04.1: Heatmap computation
```bash
grep -rn "heatmap\|temperature\|bottleneck\|StageTemperature\|compute_temperature" /home/zaks/zakops-backend/src/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf04-1.txt
```

### VF-04.2: UI component for pipeline overlay
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*heatmap*" -o -name "*bottleneck*" -o -name "*temperature*" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf04-2.txt
```

**Gate VF-04:** 2/2 checks pass.

## VF-05 — Cost UI Surfaces (S13.7)

### VF-05.1: Cost tab in debug panel
```bash
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*CostTab*" -o -name "*cost*" | grep -i "tab\|panel" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf05-1.txt
```

### VF-05.2: Usage section in settings
```bash
grep -rn "usage\|Usage" /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" | grep -i "settings\|section" | head -3 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/vf05-2.txt
```

**Gate VF-05:** 2/2 UI checks pass.

---

## Cross-Consistency / Stress Tests

### XC-1: In-memory cost trackers replaced by persistent ledger
```bash
grep -rn "in.memory\|dict()\|cost_tracking" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | grep -v test | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/xc1.txt
```

### ST-1: deal_budgets has no FK (GAP-C1 verified at schema level)
```bash
grep -rn "deal_budgets" /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" | head -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/col-m11/st1.txt
```

---

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Cost Repository) | 3 | |
| VF-02 (Enforcement) | 2 | |
| VF-03 (Predictive) | 3 | |
| VF-04 (Heatmap) | 2 | |
| VF-05 (UI) | 2 | |
| XC | 1 | |
| ST | 1 | |
| **TOTAL** | **16** | |

## Stop Condition

**DONE when:** All 16 gates produce evidence files. Do NOT proceed to M12.

---


# ═══════════════════════════════════════════════
# M12 — Citation Validation & Self-Critique
# Spec: S8.1–S8.5
# ═══════════════════════════════════════════════

## Mission Objective

Verify the citation audit pipeline, Reflexion self-critique loop, chain-of-verification integration, and UI indicators match COL-DESIGN-SPEC-V2 §8.2–§8.5 exactly. Every class, method signature, threshold, and UI color code must be confirmed against the spec.

## Pre-Flight

```bash
# PF-1: Verify citation audit module exists
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/citation_audit.py 2>&1 | tee /tmp/col-qa/m12/pf-1.txt

# PF-2: Verify reflexion module exists
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/pf-2.txt
```

## Verification Family VF-01 — Post-Generation Citation Audit (S8.2)

```bash
# VF-01.1: Cite-N regex extraction exists
grep -n 'cite-N\|cite_pattern\|\[cite-' /home/zaks/zakops-agent-api/apps/agent-api/app/services/citation_audit.py 2>&1 | tee /tmp/col-qa/m12/vf-01-1.txt

# VF-01.2: Claim sentence extraction from response
grep -n 'claim.sentence\|claim_sentence\|extract.*claim' /home/zaks/zakops-agent-api/apps/agent-api/app/services/citation_audit.py 2>&1 | tee /tmp/col-qa/m12/vf-01-2.txt

# VF-01.3: Source snippet extraction from Citation object
grep -n 'source.snippet\|Citation.*snippet\|source_snippet' /home/zaks/zakops-agent-api/apps/agent-api/app/services/citation_audit.py 2>&1 | tee /tmp/col-qa/m12/vf-01-3.txt

# VF-01.4: Semantic similarity via embedding cosine
grep -n 'cosine\|semantic_similarity\|embedding.*sim' /home/zaks/zakops-agent-api/apps/agent-api/app/services/citation_audit.py 2>&1 | tee /tmp/col-qa/m12/vf-01-4.txt

# VF-01.5: Threshold 0.5 for "weak" flag (spec: "If similarity < 0.5, flag as weak")
grep -n '0\.5\|weak' /home/zaks/zakops-agent-api/apps/agent-api/app/services/citation_audit.py 2>&1 | tee /tmp/col-qa/m12/vf-01-5.txt
```

## Verification Family VF-02 — ReflexionCritique Class (S8.3)

```bash
# VF-02.1: ReflexionCritique class definition
grep -n 'class ReflexionCritique' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-1.txt

# VF-02.2: MAX_REFINEMENTS = 2 (spec exact value)
grep -n 'MAX_REFINEMENTS.*=.*2' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-2.txt

# VF-02.3: evaluate method signature — (response, evidence: EvidenceBundle, turn_context: dict) -> CritiqueResult
grep -n 'async def evaluate' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-3.txt

# VF-02.4: CritiqueResult model — must include passed, issues, suggestion fields
grep -n 'class CritiqueResult\|passed.*bool\|issues.*list\|suggestion.*str' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-4.txt

# VF-02.5: Issue type enum — exactly 4 values per spec
grep -n 'ungrounded_claim\|missed_evidence\|off_topic\|hallucination' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-5.txt

# VF-02.6: Issue severity enum — exactly 3 values
grep -n '"low"\|"medium"\|"high"\|Literal.*low.*medium.*high' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-6.txt

# VF-02.7: refine_if_needed method — checks passed AND refinement_count >= MAX_REFINEMENTS
grep -n 'async def refine_if_needed\|refinement_count.*MAX_REFINEMENTS' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-7.txt

# VF-02.8: Critique uses gemini-flash model (spec: model="gemini-flash")
grep -n 'gemini.flash\|gemini-flash' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-02-8.txt
```

## Verification Family VF-03 — Chain-of-Verification (S8.4)

```bash
# VF-03.1: Chain-of-Verification runs as part of Reflexion loop (not separate)
grep -n 'chain.*verif\|verification.*pass\|factual.*claim' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-03-1.txt

# VF-03.2: Three steps — list claims, check against evidence, revise inline
grep -n 'list.*claim\|check.*evidence\|revise.*inline\|unsupported' /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /tmp/col-qa/m12/vf-03-2.txt
```

## Verification Family VF-04 — UI Citation Indicators (S8.5)

```bash
# VF-04.1: Strong citations — green underline, score >= 0.7
grep -rn '0\.7\|green.*underline\|strong.*cit' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" --include="*.css" 2>&1 | head -20 | tee /tmp/col-qa/m12/vf-04-1.txt

# VF-04.2: Weak citations — amber underline, score 0.5-0.7
grep -rn 'amber.*underline\|weak.*cit\|0\.5.*0\.7' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" --include="*.css" 2>&1 | head -20 | tee /tmp/col-qa/m12/vf-04-2.txt

# VF-04.3: Mismatched citations — red strikethrough, < 0.5, tooltip text
grep -rn 'red.*strikethrough\|mismatch.*cit\|Source may not support' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" --include="*.css" 2>&1 | head -20 | tee /tmp/col-qa/m12/vf-04-3.txt

# VF-04.4: Refined response badge (spec: "Refined" badge if Reflexion iterated)
grep -rn 'Refined\|refined.*badge\|reflexion.*badge' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m12/vf-04-4.txt
```

## Cross-Consistency

```bash
# XC-1: Citation audit feeds into chat_orchestrator write path
grep -n 'citation_audit\|audit_citations\|CitationAudit' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/col-qa/m12/xc-1.txt

# XC-2: Reflexion result stored in turn_snapshots
grep -n 'reflexion\|critique_result\|refinement_count' /home/zaks/zakops-agent-api/apps/agent-api/app/services/turn_snapshot.py 2>&1 | tee /tmp/col-qa/m12/xc-2.txt
```

## Stress Tests

```bash
# ST-1: No hardcoded model names outside reflexion.py (should use config)
grep -rn 'gemini-flash' /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" 2>&1 | grep -v 'reflexion\|__pycache__' | tee /tmp/col-qa/m12/st-1.txt
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Citation Audit) | 5 | |
| VF-02 (Reflexion) | 8 | |
| VF-03 (Chain-of-Verification) | 2 | |
| VF-04 (UI Indicators) | 4 | |
| XC | 2 | |
| ST | 1 | |
| **TOTAL** | **24** | |

## Stop Condition

**DONE when:** All 24 gates produce evidence files. Do NOT proceed to M13.

---

# ═══════════════════════════════════════════════
# M13 — RAG & Retrieval Enhancement
# Spec: S18.1–S18.5
# ═══════════════════════════════════════════════

## Mission Objective

Verify the RAG enhancement pipeline — hybrid retrieval, contextual chunk headers, HyDE, deal-scoped namespaces, and RAPTOR hierarchy — against COL-DESIGN-SPEC-V2 §18.1–§18.5. Check class names, method signatures, SQL indexes, fusion parameters, and classification buckets.

## Pre-Flight

```bash
# PF-1: Verify RAG enhancement module exists
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_enhanced.py 2>&1 | tee /tmp/col-qa/m13/pf-1.txt
# Also check alternative paths
ls -la /home/zaks/Zaks-llm/app/services/hybrid_retriever.py 2>&1 | tee -a /tmp/col-qa/m13/pf-1.txt

# PF-2: Verify rag_rest_api.py exists (spec reference: lines 106-171)
ls -la /home/zaks/Zaks-llm/app/rag_rest_api.py 2>&1 | tee /tmp/col-qa/m13/pf-2.txt
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_rest.py 2>&1 | tee -a /tmp/col-qa/m13/pf-2.txt
```

## Verification Family VF-01 — Hybrid Dense+Sparse Retrieval (S18.1)

```bash
# VF-01.1: HybridRetriever class definition
grep -rn 'class HybridRetriever' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-01-1.txt

# VF-01.2: search method with (query, deal_id, top_k=10) signature
grep -rn 'async def search.*query.*deal_id.*top_k' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-01-2.txt

# VF-01.3: Dense retrieval (pgvector) — top_k * 2 oversampling
grep -rn 'vector_search\|dense.*result\|top_k.*\*.*2' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m13/vf-01-3.txt

# VF-01.4: Sparse retrieval (BM25 via pg_trgm or tsvector) — top_k * 2 oversampling
grep -rn 'bm25_search\|sparse.*result\|tsvector\|pg_trgm' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m13/vf-01-4.txt

# VF-01.5: Reciprocal Rank Fusion with k=60 (spec exact value)
grep -rn 'rrf_merge\|reciprocal.*rank\|k.*=.*60' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-01-5.txt

# VF-01.6: GIN index on crawledpage.content for tsvector
grep -rn 'GIN\|gin.*index\|tsvector.*crawledpage' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" --include="*.sql" 2>&1 | tee /tmp/col-qa/m13/vf-01-6.txt
```

## Verification Family VF-02 — Contextual Chunk Headers (S18.2)

```bash
# VF-02.1: add_contextual_header function
grep -rn 'def add_contextual_header\|contextual_header' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-02-1.txt

# VF-02.2: Header includes Document title, Section hierarchy, Deal association (3 fields)
grep -rn "Document:.*title\|Section:.*section\|Deal:.*deal_id" /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-02-2.txt

# VF-02.3: Header uses "---\n" separator before chunk content
grep -rn '---\\n.*chunk\|separator.*---' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-02-3.txt
```

## Verification Family VF-03 — HyDE (S18.3)

```bash
# VF-03.1: hyde_query function
grep -rn 'def hyde_query\|hyde.*query\|hypothetical.*document' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-03-1.txt

# VF-03.2: Uses gemini-flash model with max_tokens=150 (spec exact values)
grep -rn 'gemini-flash.*150\|max_tokens.*150.*gemini' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-03-2.txt

# VF-03.3: Embeds hypothetical answer instead of raw question
grep -rn 'embed.*hypothetical\|hypothetical.*embed\|instead.*raw.*question' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-03-3.txt
```

## Verification Family VF-04 — Deal-Scoped RAG Namespaces (S18.4)

```bash
# VF-04.1: idx_embeddings_deal index (spec exact name)
grep -rn 'idx_embeddings_deal' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" --include="*.sql" 2>&1 | tee /tmp/col-qa/m13/vf-04-1.txt

# VF-04.2: Index uses ivfflat with vector_cosine_ops (spec exact index type)
grep -rn 'ivfflat.*vector_cosine_ops\|vector_cosine_ops.*ivfflat' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" --include="*.sql" 2>&1 | tee /tmp/col-qa/m13/vf-04-2.txt

# VF-04.3: Queries filtered by deal_id (prevents cross-deal leakage)
grep -rn 'deal_id.*filter\|WHERE.*deal_id\|namespace.*deal' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m13/vf-04-3.txt
```

## Verification Family VF-05 — RAPTOR Hierarchy (S18.5)

```bash
# VF-05.1: RAPTOR or hierarchical retrieval implementation
grep -rn 'RAPTOR\|raptor\|hierarchical.*retriev\|tree.*summar' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/vf-05-1.txt

# VF-05.2: Three levels — leaf (raw chunks), intermediate (cluster summaries), root (deal-level)
grep -rn 'leaf\|intermediate\|root.*summar\|cluster.*summar\|deal.*level.*summar' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m13/vf-05-2.txt
```

## Cross-Consistency

```bash
# XC-1: HybridRetriever called from chat_evidence_builder (spec: chat_evidence_builder.py:312-366)
grep -rn 'HybridRetriever\|hybrid.*retriev' /home/zaks/zakops-agent-api/apps/agent-api/app/services/chat_evidence_builder.py 2>&1 | tee /tmp/col-qa/m13/xc-1.txt

# XC-2: RankedChunk return type used consistently
grep -rn 'class RankedChunk\|RankedChunk' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/Zaks-llm/ --include="*.py" 2>&1 | tee /tmp/col-qa/m13/xc-2.txt
```

## Stress Tests

```bash
# ST-1: No cross-deal query paths that bypass deal_id filter
grep -rn 'def.*search\|def.*retriev' /home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_enhanced.py 2>&1 | tee /tmp/col-qa/m13/st-1.txt
# Check each search method has deal_id parameter
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Hybrid Retrieval) | 6 | |
| VF-02 (Chunk Headers) | 3 | |
| VF-03 (HyDE) | 3 | |
| VF-04 (Deal-Scoped) | 3 | |
| VF-05 (RAPTOR) | 2 | |
| XC | 2 | |
| ST | 1 | |
| **TOTAL** | **22** | |

## Stop Condition

**DONE when:** All 22 gates produce evidence files. Do NOT proceed to M14.

---

# ═══════════════════════════════════════════════
# M14 — Cognitive Intelligence & Decision Support
# Spec: S20.1–S20.8
# ═══════════════════════════════════════════════

## Mission Objective

Verify every cognitive intelligence component — ghost knowledge, momentum scoring, spaced repetition, decision fatigue sentinel, stall predictor, risk cascade, precedent network, and relationship intelligence — against COL-DESIGN-SPEC-V2 §20.1–§20.8. Check exact weights, thresholds, color bands, class names, and computation logic.

## Pre-Flight

```bash
# PF-1: Verify cognitive intelligence service directory
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/cognitive/ 2>&1 | tee /tmp/col-qa/m14/pf-1.txt
# Also check flat structure
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/momentum*.py /home/zaks/zakops-agent-api/apps/agent-api/app/services/ghost*.py /home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue*.py 2>&1 | tee -a /tmp/col-qa/m14/pf-1.txt

# PF-2: Verify DealBrain.tsx exists for UI components
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*DealBrain*" -o -name "*deal-brain*" -o -name "*momentum*" -o -name "*ghost*" 2>&1 | tee /tmp/col-qa/m14/pf-2.txt
```

## Verification Family VF-01 — Ghost Knowledge Detection (S20.1)

```bash
# VF-01.1: Ghost knowledge detection in extraction prompt
grep -rn 'ghost_knowledge\|ghost.*knowledge' /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-01-1.txt

# VF-01.2: ghost_knowledge_flags in SSE metadata (spec exact field name)
grep -rn 'ghost_knowledge_flags' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-01-2.txt

# VF-01.3: source_type "user_assertion" for confirmed ghost facts (spec exact value)
grep -rn 'user_assertion' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-01-3.txt

# VF-01.4: UI toast — "isn't in the Deal Brain yet" (spec toast text)
grep -rn "isn.*t in the Deal Brain\|ghost.*toast\|Confirm as Fact\|Dismiss" /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-01-4.txt
```

## Verification Family VF-02 — Deal Momentum Score (S20.2)

```bash
# VF-02.1: compute_momentum_score function with (deal_id, metrics) -> float
grep -rn 'def compute_momentum_score\|momentum_score' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-02-1.txt

# VF-02.2: Exactly 5 components — stage_velocity, event_frequency, open_item_completion, risk_trajectory, action_rate
grep -rn 'stage_velocity\|event_frequency\|open_item_completion\|risk_trajectory\|action_rate' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-02-2.txt

# VF-02.3: Exact weights — 0.30, 0.20, 0.20, 0.15, 0.15 (spec S20.2)
grep -rn '0\.30\|0\.20\|0\.15' /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-02-3.txt

# VF-02.4: Score range 0-100, round to 1 decimal (spec: round(score, 1))
grep -rn 'round.*score.*1\|0.*100' /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-02-4.txt

# VF-02.5: UI color bands — Green 80-100, Blue 50-79, Amber 20-49, Red 0-19
grep -rn '80.*100.*[Gg]reen\|50.*79.*[Bb]lue\|20.*49.*[Aa]mber\|0.*19.*[Rr]ed\|momentum.*color\|momentum.*band' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-02-5.txt

# VF-02.6: Recalculation triggered on every Deal Brain update (spec: via trigger in S4.3)
grep -rn 'momentum.*trigger\|brain.*update.*momentum\|on_brain_update' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-02-6.txt
```

## Verification Family VF-03 — Spaced Repetition (S20.3)

```bash
# VF-03.1: get_review_facts function with (deal_id, user_id) -> list[ReviewFact]
grep -rn 'def get_review_facts\|ReviewFact' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-03-1.txt

# VF-03.2: Decay threshold — 30% decay (spec: decay_conf < fact['confidence'] * 0.7)
grep -rn '0\.7\|decay.*conf\|compute_decay_confidence\|forgetting.*curve' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-03-2.txt

# VF-03.3: Returns top 5 facts sorted by current_confidence ascending
grep -rn 'sorted.*current_confidence\|\[:5\]\|top.*5.*fact' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-03-3.txt

# VF-03.4: UI "Remember this?" card (spec: shown when opening deal chat)
grep -rn 'Remember this\|review.*fact\|I remember\|reinforce' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-03-4.txt

# VF-03.5: Reinforcement resets last_reinforced, increments reinforcement_count
grep -rn 'last_reinforced\|reinforcement_count' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-03-5.txt
```

## Verification Family VF-04 — Decision Fatigue Sentinel (S20.4)

```bash
# VF-04.1: DecisionFatigueSentinel class
grep -rn 'class DecisionFatigueSentinel' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-04-1.txt

# VF-04.2: HIGH_STAKES_THRESHOLD = 5 (spec exact value — 5 decisions per 2-hour window)
grep -rn 'HIGH_STAKES_THRESHOLD.*=.*5' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-04-2.txt

# VF-04.3: SESSION_LENGTH_WARNING = timedelta(hours=3) (spec exact value)
grep -rn 'SESSION_LENGTH_WARNING.*3\|hours.*=.*3' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-04-3.txt

# VF-04.4: FatigueAlert model with type and message fields
grep -rn 'class FatigueAlert\|FatigueAlert\|decision_velocity\|session_length' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-04-4.txt

# VF-04.5: Two alert types — "decision_velocity" and "session_length" (spec exact values)
grep -rn '"decision_velocity"\|"session_length"' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-04-5.txt
```

## Verification Family VF-05 — Deal Stall Predictor (S20.5)

```bash
# VF-05.1: Stall predictor implementation
grep -rn 'stall.*predict\|StallPredict\|survival.*model\|stall_probability' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-05-1.txt

# VF-05.2: Output fields — stall_probability, median_stage_duration, percentile, similar_deals, recommendation
grep -rn 'stall_probability\|median_stage_duration\|percentile\|similar_deals_that_stalled\|recommendation' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-05-2.txt
```

## Verification Family VF-06 — Risk Cascade Predictor (S20.6)

```bash
# VF-06.1: check_risk_cascade function
grep -rn 'def check_risk_cascade\|risk_cascade' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-06-1.txt

# VF-06.2: Similarity threshold 0.7 for related risks (spec exact value)
grep -rn 'similarity.*>.*0\.7\|0\.7.*similar' /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-06-2.txt

# VF-06.3: Portfolio-wide scan of all active brains (spec: list_active_brains)
grep -rn 'list_active_brains\|all.*brains\|portfolio.*scan' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-06-3.txt

# VF-06.4: Alert via alert_service.send("risk_cascade", ...)
grep -rn 'alert_service.*risk_cascade\|send.*risk_cascade' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-06-4.txt
```

## Verification Family VF-07 — Deal Precedent Network (S20.7)

```bash
# VF-07.1: Precedent network / similar deal finder
grep -rn 'precedent.*network\|similar.*deal\|deal.*similarity\|fact.*vector' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-07-1.txt

# VF-07.2: Output includes similarity_score, key_similarities, key_differences, outcome
grep -rn 'key_similarities\|key_differences\|similarity_score.*outcome' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-07-2.txt
```

## Verification Family VF-08 — Relationship Intelligence (S20.8)

```bash
# VF-08.1: Broker dossier endpoint (spec: GET /api/brokers/{name}/dossier)
grep -rn 'broker.*dossier\|/api/brokers\|broker_name.*deals_involved\|success_rate' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/zakops-backend/ --include="*.py" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m14/vf-08-1.txt

# VF-08.2: Response fields — deals_involved, success_rate, avg_response_time, terms_evolution, total_value
grep -rn 'deals_involved\|avg_response_time\|terms_evolution\|total_value\|notes_across_deals' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/zakops-backend/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/vf-08-2.txt
```

## Cross-Consistency

```bash
# XC-1: Momentum score stored in deal_brain.momentum column (from M04 migration)
grep -rn 'momentum' /home/zaks/zakops-agent-api/apps/agent-api/app/services/deal_brain*.py 2>&1 | head -15 | tee /tmp/col-qa/m14/xc-1.txt

# XC-2: Ghost knowledge uses deal_brain.ghost_facts column (from M04 migration)
grep -rn 'ghost_facts' /home/zaks/zakops-agent-api/apps/agent-api/app/services/deal_brain*.py 2>&1 | tee /tmp/col-qa/m14/xc-2.txt
```

## Stress Tests

```bash
# ST-1: Momentum weights sum to exactly 1.0
python3 -c "print(0.30 + 0.20 + 0.20 + 0.15 + 0.15)" 2>&1 | tee /tmp/col-qa/m14/st-1.txt
# Expected: 1.0

# ST-2: Fatigue sentinel 2-hour window matches count_decisions query
grep -rn 'timedelta.*hours.*2\|window.*2.*hour' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m14/st-2.txt
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Ghost Knowledge) | 4 | |
| VF-02 (Momentum) | 6 | |
| VF-03 (Spaced Repetition) | 5 | |
| VF-04 (Fatigue Sentinel) | 5 | |
| VF-05 (Stall Predictor) | 2 | |
| VF-06 (Risk Cascade) | 4 | |
| VF-07 (Precedent Network) | 2 | |
| VF-08 (Relationship Intelligence) | 2 | |
| XC | 2 | |
| ST | 2 | |
| **TOTAL** | **36** | |

## Stop Condition

**DONE when:** All 36 gates produce evidence files. Do NOT proceed to M15.

---

# ═══════════════════════════════════════════════
# M15 — Deterministic Replay & Partition Automation
# Spec: S6.1–S6.5
# ═══════════════════════════════════════════════

## Mission Objective

Verify the replay infrastructure — turn snapshots, partition automation (3-tier), retention tiers, replay endpoint, and counterfactual analysis engine — against COL-DESIGN-SPEC-V2 §6.1–§6.5. Check partition gates, encryption specs, endpoint signatures, and admin-only auth.

## Pre-Flight

```bash
# PF-1: Verify turn_snapshots table exists (created by Migration 004)
psql -U agent -d zakops_agent -c "\d turn_snapshots" 2>&1 | tee /tmp/col-qa/m15/pf-1.txt

# PF-2: Verify partition automation function exists
psql -U agent -d zakops_agent -c "\df create_monthly_partitions" 2>&1 | tee /tmp/col-qa/m15/pf-2.txt
```

## Verification Family VF-01 — Current State Capture Completeness (S6.1)

```bash
# VF-01.1: Full message chain captured in LangGraph checkpoints
grep -rn 'checkpoint\|full.*message.*chain\|message.*store' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m15/vf-01-1.txt

# VF-01.2: System prompt version stored (spec: prompt_version in decision ledger)
grep -rn 'prompt_version' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-01-2.txt

# VF-01.3: System prompt SHA-256 hash (spec: prompts/__init__.py:37-48)
grep -rn 'sha.*256\|SHA256\|prompt.*hash' /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-01-3.txt

# VF-01.4: Rendered prompt captured (spec gap: "built fresh each request, ephemeral")
grep -rn 'rendered_prompt\|full_prompt.*snapshot\|prompt.*capture' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-01-4.txt
```

## Verification Family VF-02 — Partition Automation 3-Tier (S6.2)

```bash
# VF-02.1: Tier 1 — DEFAULT partition exists for turn_snapshots
psql -U agent -d zakops_agent -c "SELECT relname FROM pg_class WHERE relname = 'turn_snapshots_default'" 2>&1 | tee /tmp/col-qa/m15/vf-02-1.txt

# VF-02.2: Tier 1 — DEFAULT partition exists for cost_ledger
psql -U agent -d zakops_agent -c "SELECT relname FROM pg_class WHERE relname = 'cost_ledger_default'" 2>&1 | tee /tmp/col-qa/m15/vf-02-2.txt

# VF-02.3: Tier 2 — create_monthly_partitions() is PL/pgSQL function (spec: defined in migration 004)
psql -U agent -d zakops_agent -c "SELECT proname, prolang, prosrc FROM pg_proc WHERE proname = 'create_monthly_partitions'" 2>&1 | tee /tmp/col-qa/m15/vf-02-3.txt

# VF-02.4: Function is idempotent (spec: IF NOT EXISTS check)
grep -rn 'IF NOT EXISTS\|idempotent\|create_monthly_partitions' /home/zaks/zakops-agent-api/apps/agent-api/migrations/ --include="*.sql" --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-02-4.txt

# VF-02.5: Function creates N months ahead (spec: 3 months ahead)
grep -rn 'months_ahead\|3.*months\|create_monthly_partitions.*3' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" --include="*.sql" 2>&1 | tee /tmp/col-qa/m15/vf-02-5.txt

# VF-02.6: Tier 3 — scheduling mechanism (pg_cron OR OS cron OR app startup)
grep -rn 'cron.schedule\|partition.*maintenance\|ensure_partitions\|create_monthly_partitions' /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-02-6.txt

# VF-02.7: G-PART-1 — DEFAULT has 0 rows (data in named partitions)
psql -U agent -d zakops_agent -c "SELECT relname, n_live_tup FROM pg_stat_user_tables WHERE relname IN ('turn_snapshots_default', 'cost_ledger_default')" 2>&1 | tee /tmp/col-qa/m15/vf-02-7.txt

# VF-02.8: G-PART-2 — Future partitions exist (current + next 2 months)
psql -U agent -d zakops_agent -c "SELECT relname FROM pg_class WHERE relname LIKE 'turn_snapshots_20%' ORDER BY relname DESC LIMIT 5" 2>&1 | tee /tmp/col-qa/m15/vf-02-8.txt
```

## Verification Family VF-03 — Retention Tiers (S6.3)

```bash
# VF-03.1: Three retention tiers — Default 90d, Compliance 7y, Legal hold indefinite
grep -rn 'retention.*90\|retention.*7.*year\|retention.*indefinite\|compliance_tier\|legal_hold' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m15/vf-03-1.txt

# VF-03.2: AES-256-GCM encryption for compliance/legal-hold tiers (spec: reuse CheckpointEncryption)
grep -rn 'AES.*256.*GCM\|CheckpointEncryption\|encryption.*compliance' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-03-2.txt

# VF-03.3: Encryption key derived via HKDF from deal_id + master key (spec exact derivation)
grep -rn 'HKDF\|hkdf\|deal_id.*master.*key\|key.*derivation' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-03-3.txt

# VF-03.4: Cleartext index fields — thread_id, turn_number, created_at (rest encrypted)
grep -rn 'cleartext\|unencrypted.*thread_id\|unencrypted.*turn_number\|unencrypted.*created_at' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-03-4.txt
```

## Verification Family VF-04 — Replay Endpoint (S6.4)

```bash
# VF-04.1: POST /admin/replay endpoint exists
grep -rn 'admin.*replay\|replay.*endpoint\|/admin/replay' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-04-1.txt

# VF-04.2: Auth requires admin role (spec: require_admin_role)
grep -rn 'require_admin_role\|admin.*auth.*replay\|admin_only.*replay' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-04-2.txt

# VF-04.3: Request body — thread_id: str, turn_number: int
grep -rn 'thread_id.*turn_number\|ReplayRequest\|replay.*body' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-04-3.txt

# VF-04.4: Response includes original, replay, comparison fields (spec exact structure)
grep -rn 'similarity_score.*float\|tool_calls_match.*bool\|semantic_drift\|ReplayResponse' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-04-4.txt

# VF-04.5: Acceptance test — cosine similarity > 0.85 and tool_calls_match == true
grep -rn '0\.85\|similarity.*threshold\|tool_calls_match' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-04-5.txt
```

## Verification Family VF-05 — Counterfactual Analysis (S6.5)

```bash
# VF-05.1: POST /admin/counterfactual endpoint
grep -rn 'admin.*counterfactual\|/admin/counterfactual\|CounterfactualRequest' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-05-1.txt

# VF-05.2: Three modified_inputs — user_message, facts_override, stage_override (spec exact fields)
grep -rn 'user_message.*facts_override\|facts_override.*stage_override\|modified_inputs' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-05-2.txt

# VF-05.3: Response includes brain_diff, recommendation_diff, risk_assessment_change
grep -rn 'brain_diff\|recommendation_diff\|risk_assessment_change\|CounterfactualResponse' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/vf-05-3.txt
```

## Cross-Consistency

```bash
# XC-1: turn_snapshots referenced in M09 write path (Step 7)
grep -rn 'turn_snapshot\|save_snapshot' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /tmp/col-qa/m15/xc-1.txt

# XC-2: Partition automation covers both turn_snapshots AND cost_ledger (from M11)
grep -rn 'create_monthly_partitions.*turn_snapshots\|create_monthly_partitions.*cost_ledger' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" --include="*.sql" 2>&1 | tee /tmp/col-qa/m15/xc-2.txt
```

## Stress Tests

```bash
# ST-1: No direct INSERT into turn_snapshots that bypasses partition routing
grep -rn 'INSERT INTO turn_snapshots' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m15/st-1.txt
# All inserts should go through parent table (PostgreSQL routes to correct partition)
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (State Capture) | 4 | |
| VF-02 (Partition Automation) | 8 | |
| VF-03 (Retention Tiers) | 4 | |
| VF-04 (Replay Endpoint) | 5 | |
| VF-05 (Counterfactual) | 3 | |
| XC | 2 | |
| ST | 1 | |
| **TOTAL** | **29** | |

## Stop Condition

**DONE when:** All 29 gates produce evidence files. Do NOT proceed to M16.

---

# ═══════════════════════════════════════════════
# M16 — Export & Living Deal Memo
# Spec: S12.1–S12.4
# ═══════════════════════════════════════════════

## Mission Objective

Verify the export pipeline — Markdown export, JSON/PDF roadmap, attach-to-deal, and Living Deal Memo — against COL-DESIGN-SPEC-V2 §12.1–§12.4. Check endpoint paths, response formats, memo content sections, and auto-refresh trigger.

## Pre-Flight

```bash
# PF-1: Verify export endpoint file exists
find /home/zaks/zakops-agent-api/apps/agent-api -name "*export*" -type f 2>&1 | tee /tmp/col-qa/m16/pf-1.txt
find /home/zaks/zakops-agent-api/apps/dashboard/src -path "*export*" -type f 2>&1 | tee -a /tmp/col-qa/m16/pf-1.txt

# PF-2: Verify memo endpoint or service exists
find /home/zaks/zakops-agent-api/apps/agent-api -name "*memo*" -type f 2>&1 | tee /tmp/col-qa/m16/pf-2.txt
grep -rn 'memo\|living.*deal' /home/zaks/zakops-agent-api/apps/agent-api/app/api/ --include="*.py" 2>&1 | head -15 | tee -a /tmp/col-qa/m16/pf-2.txt
```

## Verification Family VF-01 — Export Formats (S12.1)

```bash
# VF-01.1: Markdown export is MVP format
grep -rn 'markdown\|format.*markdown\|export.*md' /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m16/vf-01-1.txt

# VF-01.2: Export includes citations, proposals, evidence bundle, Deal Brain impact (spec: 4 elements)
grep -rn 'citation.*export\|proposal.*export\|evidence.*bundle\|brain.*impact' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m16/vf-01-2.txt
```

## Verification Family VF-02 — Export API Endpoint (S12.2)

```bash
# VF-02.1: GET /api/v1/chatbot/threads/{id}/export?format=markdown (spec exact path)
grep -rn 'threads.*export\|export.*format\|/export' /home/zaks/zakops-agent-api/apps/agent-api/app/api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m16/vf-02-1.txt

# VF-02.2: format query parameter support
grep -rn 'format.*=.*markdown\|query.*format\|format.*param' /home/zaks/zakops-agent-api/apps/agent-api/app/api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m16/vf-02-2.txt
```

## Verification Family VF-03 — Attach Transcript (S12.3)

```bash
# VF-03.1: POST /api/v1/chatbot/threads/{id}/attach endpoint (spec exact path)
grep -rn 'threads.*attach\|/attach\|attach.*transcript' /home/zaks/zakops-agent-api/apps/agent-api/app/api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m16/vf-03-1.txt

# VF-03.2: Dashboard route for attach-to-deal action
grep -rn 'attach.*deal\|attach.*transcript' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m16/vf-03-2.txt
```

## Verification Family VF-04 — Living Deal Memo (S12.4)

```bash
# VF-04.1: GET /api/deals/{id}/memo?format=markdown endpoint (spec exact path)
grep -rn 'deals.*memo\|/memo\|memo.*format' /home/zaks/zakops-agent-api/apps/agent-api/app/api/ /home/zaks/zakops-backend/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m16/vf-04-1.txt

# VF-04.2: Memo includes all 7 content sections per spec
# Sections: executive summary, key metrics, risk assessment, decision history, open items, timeline, appendix citations
grep -rn 'executive.*summary\|key.*metrics\|risk.*assessment\|decision.*history\|open.*items\|timeline\|appendix.*citation\|source.*citation' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m16/vf-04-2.txt

# VF-04.3: Auto-refresh when Deal Brain version changes (spec: "Regenerated when Deal Brain version changes")
grep -rn 'brain.*version.*change\|auto.*refresh.*memo\|memo.*regenerat\|version.*trigger.*memo' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m16/vf-04-3.txt

# VF-04.4: PDF conversion support (spec: "PDF via server-side Markdown → PDF conversion")
grep -rn 'markdown.*pdf\|pdf.*convert\|format.*pdf' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m16/vf-04-4.txt
```

## Cross-Consistency

```bash
# XC-1: Export uses Deal Brain data (connected to M04/M05 brain)
grep -rn 'brain.*export\|deal_brain.*memo\|brain_repo.*get_brain' /home/zaks/zakops-agent-api/apps/agent-api/app/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m16/xc-1.txt
```

## Stress Tests

```bash
# ST-1: Export endpoint has proper auth (not public)
grep -rn 'auth\|require.*role\|permission\|current_user' /home/zaks/zakops-agent-api/apps/agent-api/app/api/ --include="*.py" 2>&1 | grep -i 'export\|memo' | tee /tmp/col-qa/m16/st-1.txt
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Export Formats) | 2 | |
| VF-02 (Export API) | 2 | |
| VF-03 (Attach Transcript) | 2 | |
| VF-04 (Living Memo) | 4 | |
| XC | 1 | |
| ST | 1 | |
| **TOTAL** | **14** | |

## Stop Condition

**DONE when:** All 14 gates produce evidence files. Do NOT proceed to M17.

---

# ═══════════════════════════════════════════════
# M17 — Proposal Pipeline Hardening
# Spec: S15.1–S15.4
# ═══════════════════════════════════════════════

## Mission Objective

Verify proposal pipeline hardening — execute-proposal route, status tracking JSONB, concurrency control, and correct_brain_summary handler — against COL-DESIGN-SPEC-V2 §15.1–§15.4. Check that the 501 stub is replaced, JSONB status_history structure matches spec, FOR UPDATE locking is used, and all 7 PROPOSAL_HANDLERS entries exist.

## Pre-Flight

```bash
# PF-1: Verify execute-proposal route exists and is NOT a 501 stub
grep -rn '501\|Not Implemented\|stub' /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/execute-proposal/route.ts 2>&1 | tee /tmp/col-qa/m17/pf-1.txt

# PF-2: Verify proposal handling code in agent API
grep -rn 'proposal\|PROPOSAL_HANDLERS' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m17/pf-2.txt
```

## Verification Family VF-01 — Execute-Proposal Route (S15.2)

```bash
# VF-01.1: Route no longer returns 501 (should wire to backend execute_proposal)
grep -rn 'return.*501\|NextResponse.*501\|Not.*Implemented' /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/execute-proposal/route.ts 2>&1 | tee /tmp/col-qa/m17/vf-01-1.txt
# PASS = no matches (501 removed)

# VF-01.2: Route calls backend execute_proposal method
grep -rn 'execute_proposal\|fetch.*execute.*proposal\|BACKEND_URL.*proposal' /home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/execute-proposal/route.ts 2>&1 | tee /tmp/col-qa/m17/vf-01-2.txt
```

## Verification Family VF-02 — Proposal Status Tracking (S15.2)

```bash
# VF-02.1: proposal_id field in proposals JSONB
grep -rn 'proposal_id' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m17/vf-02-1.txt

# VF-02.2: status field with valid values — pending_approval, approved, executed (spec exact values)
grep -rn 'pending_approval\|approved\|executed' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m17/vf-02-2.txt

# VF-02.3: status_history array — each entry has status, at, by fields (spec exact JSONB structure)
grep -rn 'status_history\|status.*at.*by' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m17/vf-02-3.txt

# VF-02.4: auto-approve REMOVED for create_action (spec: "Remove auto-approve")
grep -rn 'auto.*approve\|create_action.*approve\|auto_approve' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/vf-02-4.txt
# PASS = no auto-approve matches for create_action
```

## Verification Family VF-03 — Concurrency Control (S15.3 — GAP-L3)

```bash
# VF-03.1: update_proposal_status function with optimistic locking
grep -rn 'def update_proposal_status\|update_proposal_status' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/vf-03-1.txt

# VF-03.2: FOR UPDATE lock on chat_messages row
grep -rn 'FOR UPDATE\|for_update\|SELECT.*proposals.*FOR UPDATE' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/vf-03-2.txt

# VF-03.3: Transaction wrapper (spec: async with db.transaction())
grep -rn 'transaction\(\)\|db\.transaction\|BEGIN\|COMMIT' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m17/vf-03-3.txt

# VF-03.4: status_history append within lock (not outside transaction)
grep -rn 'status_history.*append\|append.*status' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/vf-03-4.txt
```

## Verification Family VF-04 — PROPOSAL_HANDLERS Dict (S15.4)

```bash
# VF-04.1: PROPOSAL_HANDLERS dictionary exists with all 7 entries
grep -rn 'PROPOSAL_HANDLERS' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/vf-04-1.txt

# VF-04.2: All 7 handler entries per spec
# stage_transition, add_note, search_web, create_action, mark_complete, add_document, correct_brain_summary
{ grep -rn 'stage_transition.*handle\|handle.*stage_transition' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1; \
  grep -rn 'add_note.*handle\|handle.*add_note' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1; \
  grep -rn 'search_web.*handle\|handle.*search_web' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1; \
  grep -rn 'create_action.*handle\|handle.*create_action' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1; \
  grep -rn 'mark_complete.*handle\|handle.*mark_complete' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1; \
  grep -rn 'add_document.*handle\|handle.*add_document' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1; \
  grep -rn 'correct_brain_summary.*handle\|handle.*correct_brain_summary' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1; } | tee /tmp/col-qa/m17/vf-04-2.txt

# VF-04.3: correct_brain_summary handler — snapshots to history, regenerates summary (S15.4 — GAP-M10)
grep -rn 'correct_brain_summary\|save_history.*correction\|regenerate_summary' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/vf-04-3.txt

# VF-04.4: History snapshot with trigger_type='correction' and triggered_by=user_id
grep -rn "trigger_type.*correction\|triggered_by.*user_id" /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/vf-04-4.txt
```

## Cross-Consistency

```bash
# XC-1: Proposals stored in chat_messages.proposals JSONB (from M01 migration)
psql -U agent -d zakops_agent -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='chat_messages' AND column_name='proposals'" 2>&1 | tee /tmp/col-qa/m17/xc-1.txt

# XC-2: correct_brain_summary connects to brain_repo (from M05)
grep -rn 'brain_repo\|brain_service' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m17/xc-2.txt
```

## Stress Tests

```bash
# ST-1: No proposal mutations outside of transactional update_proposal_status
grep -rn "UPDATE.*chat_messages.*SET.*proposals" /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m17/st-1.txt
# All updates should route through update_proposal_status
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Execute-Proposal) | 2 | |
| VF-02 (Status Tracking) | 4 | |
| VF-03 (Concurrency) | 4 | |
| VF-04 (PROPOSAL_HANDLERS) | 4 | |
| XC | 2 | |
| ST | 1 | |
| **TOTAL** | **19** | |

## Stop Condition

**DONE when:** All 19 gates produce evidence files. Do NOT proceed to M18.

---

# ═══════════════════════════════════════════════
# M18 — Agent Architecture & Autonomous Capabilities
# Spec: S19.1–S19.6
# ═══════════════════════════════════════════════

## Mission Objective

Verify agent architecture enhancements — JSON mode via vLLM, typed SSE events, plan-and-execute decomposition, multi-specialist delegation, devil's advocate, and MCP governance — against COL-DESIGN-SPEC-V2 §19.1–§19.6. Check method signatures, Pydantic models, SPECIALISTS dict, MCP integration table, and trigger intervals.

## Pre-Flight

```bash
# PF-1: Verify llm.py has generate_json method
grep -rn 'def generate_json\|generate_json' /home/zaks/zakops-agent-api/apps/agent-api/app/services/llm.py 2>&1 | tee /tmp/col-qa/m18/pf-1.txt

# PF-2: Verify SSE event models exist
grep -rn 'SSEEvent\|MessageChunkEvent\|BrainUpdatedEvent' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m18/pf-2.txt
```

## Verification Family VF-01 — JSON Mode via vLLM (S19.1)

```bash
# VF-01.1: generate_json method in llm.py
grep -n 'async def generate_json' /home/zaks/zakops-agent-api/apps/agent-api/app/services/llm.py 2>&1 | tee /tmp/col-qa/m18/vf-01-1.txt

# VF-01.2: Uses response_format={"type": "json_object"} (spec exact parameter)
grep -n 'response_format.*json_object\|"type".*"json_object"' /home/zaks/zakops-agent-api/apps/agent-api/app/services/llm.py 2>&1 | tee /tmp/col-qa/m18/vf-01-2.txt

# VF-01.3: Returns BaseModel via model_validate_json (spec exact method)
grep -n 'model_validate_json\|schema.*model_validate' /home/zaks/zakops-agent-api/apps/agent-api/app/services/llm.py 2>&1 | tee /tmp/col-qa/m18/vf-01-3.txt

# VF-01.4: Accepts schema parameter of type BaseModel
grep -n 'schema.*BaseModel\|schema.*type\[BaseModel\]' /home/zaks/zakops-agent-api/apps/agent-api/app/services/llm.py 2>&1 | tee /tmp/col-qa/m18/vf-01-4.txt
```

## Verification Family VF-02 — Typed SSE Events (S19.2)

```bash
# VF-02.1: MessageChunkEvent with type: Literal["message_chunk"] and content: str
grep -rn 'class MessageChunkEvent\|message_chunk.*Literal' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-02-1.txt

# VF-02.2: BrainUpdatedEvent with type, deal_id, version, changes fields
grep -rn 'class BrainUpdatedEvent\|brain_updated.*Literal\|deal_id.*version.*changes' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-02-2.txt

# VF-02.3: SSEEvent discriminated union (spec: Union[MessageChunkEvent, BrainUpdatedEvent, ...])
grep -rn 'SSEEvent.*=.*Union\|Annotated.*discriminator\|discriminated.*union' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-02-3.txt

# VF-02.4: emit_sse function with runtime validation (spec: model_validate + model_dump_json)
grep -rn 'def emit_sse\|model_validate\|model_dump_json' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m18/vf-02-4.txt
```

## Verification Family VF-03 — Plan-and-Execute (S19.3)

```bash
# VF-03.1: PlanAndExecuteGraph class
grep -rn 'class PlanAndExecuteGraph\|PlanAndExecute' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-03-1.txt

# VF-03.2: plan method that generates structured steps (spec: returns list[Step])
grep -rn 'async def plan\|PlanSchema\|list\[Step\]' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-03-2.txt

# VF-03.3: execute method that runs steps sequentially with prior_results
grep -rn 'async def execute\|execute_step.*prior_results\|prior_results' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-03-3.txt

# VF-03.4: synthesize method that combines results
grep -rn 'def synthesize\|synthesize.*results' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-03-4.txt
```

## Verification Family VF-04 — Multi-Specialist Delegation (S19.4)

```bash
# VF-04.1: SPECIALISTS dictionary with 4 entries (spec exact keys)
grep -rn 'SPECIALISTS.*=\|SPECIALISTS\[' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-04-1.txt

# VF-04.2: Four specialist graphs — financial_analysis, risk_assessment, deal_memory, market_research
grep -rn 'financial_analysis\|FinancialAnalystGraph\|risk_assessment\|RiskAssessorGraph\|deal_memory\|DealMemoryExpertGraph\|market_research\|MarketResearchGraph' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-04-2.txt

# VF-04.3: route_to_specialist function with classifier and default fallback
grep -rn 'def route_to_specialist\|SpecialistClassification\|default_graph.*fallback' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-04-3.txt
```

## Verification Family VF-05 — Devil's Advocate (S19.5)

```bash
# VF-05.1: Devil's advocate trigger — every 5 turns in deal-scoped chat
grep -rn 'devil.*advocate\|counter.*argument\|challenge.*assumption\|every.*5.*turn' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-05-1.txt

# VF-05.2: Output displayed as expandable card in Deal Brain
grep -rn "Devil.*Advocate\|devil.*advocate\|counter.*card\|challenge.*card" /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m18/vf-05-2.txt
```

## Verification Family VF-06 — MCP Governance (S19.6 — GAP-L1)

```bash
# VF-06.1: MCP tools integration documented (spec: 12 MCP tools at zakops-backend/mcp_server/)
ls -la /home/zaks/zakops-backend/mcp_server/ 2>&1 | tee /tmp/col-qa/m18/vf-06-1.txt

# VF-06.2: MCP tool invocations logged to decision_ledger
grep -rn 'decision_ledger.*mcp\|mcp.*decision_ledger\|mcp.*log\|log.*mcp.*tool' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/zakops-backend/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m18/vf-06-2.txt

# VF-06.3: MCP tool invocations tracked by cost_ledger
grep -rn 'cost_ledger.*mcp\|mcp.*cost\|mcp.*token' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/zakops-backend/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m18/vf-06-3.txt

# VF-06.4: SCOPE_TOOL_MAP includes MCP tools (spec: event_list, action_list as read-only)
grep -rn 'SCOPE_TOOL_MAP\|event_list\|action_list' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m18/vf-06-4.txt

# VF-06.5: artifact_upload in HITL_TOOLS (spec: add to HITL_TOOLS)
grep -rn 'artifact_upload.*HITL\|HITL.*artifact_upload' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/vf-06-5.txt
```

## Cross-Consistency

```bash
# XC-1: generate_json used in Deal Brain extraction (M05) — not raw JSON parsing
grep -rn 'generate_json\|generate.*json' /home/zaks/zakops-agent-api/apps/agent-api/app/services/deal_brain*.py 2>&1 | tee /tmp/col-qa/m18/xc-1.txt

# XC-2: SSE events match M03's SSE catalog (14 events)
grep -rn 'class.*Event.*BaseModel\|type.*Literal' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | head -20 | tee /tmp/col-qa/m18/xc-2.txt
```

## Stress Tests

```bash
# ST-1: No raw JSON parsing (json.loads on LLM output) bypassing generate_json
grep -rn 'json\.loads.*response\|json\.loads.*completion\|json\.loads.*content' /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" 2>&1 | tee /tmp/col-qa/m18/st-1.txt
# Flag any that should use generate_json instead
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (JSON Mode) | 4 | |
| VF-02 (Typed SSE) | 4 | |
| VF-03 (Plan-Execute) | 4 | |
| VF-04 (Specialists) | 3 | |
| VF-05 (Devil's Advocate) | 2 | |
| VF-06 (MCP Governance) | 5 | |
| XC | 2 | |
| ST | 1 | |
| **TOTAL** | **27** | |

## Stop Condition

**DONE when:** All 27 gates produce evidence files. Do NOT proceed to M19.

---

# ═══════════════════════════════════════════════
# M19 — Ambient Intelligence & Predictive Features
# Spec: S21.1–S21.6
# ═══════════════════════════════════════════════

## Mission Objective

Verify ambient intelligence features — morning briefing, command palette, anomaly alerts, ambient sidebar, smart paste, and sentiment coach — against COL-DESIGN-SPEC-V2 §21.1–§21.6. Check class names, trigger conditions, thresholds, entity types, and UI layout specifications.

## Pre-Flight

```bash
# PF-1: Verify ambient intelligence service files
find /home/zaks/zakops-agent-api/apps/agent-api -name "*ambient*" -o -name "*briefing*" -o -name "*anomaly*" 2>&1 | tee /tmp/col-qa/m19/pf-1.txt

# PF-2: Verify command palette and smart paste UI components
find /home/zaks/zakops-agent-api/apps/dashboard/src -name "*command*" -o -name "*palette*" -o -name "*smart-paste*" -o -name "*SmartPaste*" 2>&1 | tee /tmp/col-qa/m19/pf-2.txt
```

## Verification Family VF-01 — Morning Deal Briefing (S21.1)

```bash
# VF-01.1: MorningBriefingGenerator class
grep -rn 'class MorningBriefingGenerator\|MorningBriefing' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-01-1.txt

# VF-01.2: Schedule — 7:00 AM configurable (spec exact time)
grep -rn '7.*AM\|07:00\|morning.*schedule\|briefing.*time' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-01-2.txt

# VF-01.3: Content sources — events_since, brain_changes_since, momentum_delta
grep -rn 'get_events_since\|get_brain_changes_since\|get_momentum_delta\|momentum_delta.*5' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-01-3.txt

# VF-01.4: Channels — dashboard notification + optional email (spec: both channels)
grep -rn 'notification.*email\|email.*briefing\|dashboard.*notification.*briefing' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-01-4.txt

# VF-01.5: Briefing generated via gemini-flash (spec: model="gemini-flash")
grep -rn 'briefing.*gemini.*flash\|gemini-flash.*briefing' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-01-5.txt

# VF-01.6: Momentum delta threshold > 5 triggers inclusion (spec: abs(momentum_delta) > 5)
grep -rn 'momentum_delta.*>.*5\|abs.*momentum_delta' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-01-6.txt
```

## Verification Family VF-02 — Command Palette (S21.2)

```bash
# VF-02.1: Command palette component (Cmd+K)
grep -rn 'Cmd.*K\|command.*palette\|CommandPalette\|cmdk\|command-menu' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/vf-02-1.txt

# VF-02.2: Context-aware commands — different for dashboard, deal workspace, chat (spec: 3 contexts)
grep -rn 'Search deals\|Create deal\|View pipeline\|Show stalled\|Ask about\|Show risk summary\|Compare.*similar\|Summarize.*conversation\|Export transcript\|Attach to deal' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m19/vf-02-2.txt

# VF-02.3: Route-based command source (spec: "function of current route + deal context")
grep -rn 'route.*command\|current.*route.*palette\|usePathname.*command\|useRouter.*palette' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/vf-02-3.txt
```

## Verification Family VF-03 — Anomaly Detection (S21.3)

```bash
# VF-03.1: DealAnomalyDetector class
grep -rn 'class DealAnomalyDetector\|DealAnomalyDetect' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-03-1.txt

# VF-03.2: Unusual silence — days_since_last_event > avg_event_gap * 2 (spec exact formula)
grep -rn 'days_since_last_event.*avg_event_gap.*2\|unusual_silence\|avg_event_gap.*\*.*2' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-03-2.txt

# VF-03.3: Activity burst — events_today > avg_events_per_day * 3 (spec exact formula)
grep -rn 'events_today.*avg_events_per_day.*3\|activity_burst\|avg_events_per_day.*\*.*3' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-03-3.txt

# VF-03.4: Anomaly model with type and message fields
grep -rn 'class Anomaly\|Anomaly.*type.*message' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-03-4.txt
```

## Verification Family VF-04 — Ambient Sidebar (S21.4)

```bash
# VF-04.1: Ambient sidebar component
grep -rn 'Ambient.*Context\|ambient.*sidebar\|AmbientSidebar\|AmbientContext' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/vf-04-1.txt

# VF-04.2: Four sections — Related Facts, Similar Deals, Recent News, Decaying Facts (spec layout)
grep -rn 'Related Facts\|Similar Deals\|Recent News\|Decaying Facts\|related.*facts\|similar.*deals\|recent.*news\|decaying.*facts' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m19/vf-04-2.txt
```

## Verification Family VF-05 — Smart Paste (S21.5)

```bash
# VF-05.1: Smart paste with entity extraction
grep -rn 'smart.*paste\|SmartPaste\|entity.*extract\|paste.*entity' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/vf-05-1.txt

# VF-05.2: Five entity types — Person, Financial (x2), Metric, Date (spec: 5 types in example)
grep -rn 'Person\|Financial\|Metric\|Date.*extract\|entity.*type' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -20 | tee /tmp/col-qa/m19/vf-05-2.txt

# VF-05.3: "Add to Deal Brain" action from entity extraction toast
grep -rn 'Add to Deal Brain\|add.*brain.*entity\|Send as.*is\|entity.*toast' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/vf-05-3.txt

# VF-05.4: Client-side regex for M&A terms (spec: "client-side entity detection via regex")
grep -rn 'currency.*regex\|percentage.*regex\|date.*regex\|company.*regex\|entity.*pattern' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/vf-05-4.txt
```

## Verification Family VF-06 — Sentiment Coach (S21.6)

```bash
# VF-06.1: Sentiment analysis implementation
grep -rn 'sentiment\|negotiation.*coach\|Sentiment.*Coach\|tone.*analy' /home/zaks/zakops-agent-api/apps/agent-api/ /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.py" --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/vf-06-1.txt

# VF-06.2: Per-deal sentiment trend tracking (positive/neutral/negative)
grep -rn 'positive.*neutral.*negative\|sentiment.*trend\|sentiment.*deal' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/vf-06-2.txt
```

## Cross-Consistency

```bash
# XC-1: Morning briefing uses Deal Brain data (connected to M04/M05)
grep -rn 'brain.*briefing\|deal_brain.*morning\|brain_repo.*briefing' /home/zaks/zakops-agent-api/apps/agent-api/ --include="*.py" 2>&1 | tee /tmp/col-qa/m19/xc-1.txt

# XC-2: Smart paste entities feed into Deal Brain (from M05 ghost knowledge path)
grep -rn 'entity.*brain\|paste.*brain\|extract.*brain' /home/zaks/zakops-agent-api/apps/dashboard/src/ --include="*.tsx" --include="*.ts" 2>&1 | head -15 | tee /tmp/col-qa/m19/xc-2.txt
```

## Stress Tests

```bash
# ST-1: Anomaly thresholds don't fire on empty deals (no division by zero)
grep -rn 'max.*1\|or.*1\|zero.*div\|division.*zero' /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" 2>&1 | head -15 | tee /tmp/col-qa/m19/st-1.txt
```

## Scorecard

| Gate | Checks | Result |
|------|--------|--------|
| PF | 2 | |
| VF-01 (Morning Briefing) | 6 | |
| VF-02 (Command Palette) | 3 | |
| VF-03 (Anomaly Detection) | 4 | |
| VF-04 (Ambient Sidebar) | 2 | |
| VF-05 (Smart Paste) | 4 | |
| VF-06 (Sentiment Coach) | 2 | |
| XC | 2 | |
| ST | 1 | |
| **TOTAL** | **26** | |

## Stop Condition

**DONE when:** All 26 gates produce evidence files. This is the FINAL mission. Proceed to Registry Summary.

---

# ═══════════════════════════════════════════════
# REGISTRY SUMMARY — All 19 Missions
# ═══════════════════════════════════════════════

| Mission | Spec Section | Focus | Gates |
|---------|-------------|-------|-------|
| M01 | S3.2–S3.3 | Migration 004 DDL (9 tables, indexes, functions) | 91 |
| M02 | S3.6 | ChatRepository (12 methods, ownership, outbox) | 31 |
| M03 | S3.5, S3.10 | Chat API (5 endpoints, middleware, SSE catalog) | 32 |
| M04 | S4.2 | Migration 028 DDL (deal_brain, history, entity graph) | 46 |
| M05 | S4.3–S4.7 | Deal Brain Service (extraction, drift, momentum, UI) | 36 |
| M06 | S7.1–S7.4 | Security (injection guard, canary, session tracker) | 32 |
| M07 | S11.1–S11.5 | Delete & Retention (cascade, legal hold, GDPR) | 32 |
| M08 | S9.1–S9.7 | Tool Scoping (scope map, role map, HITL, schema) | 24 |
| M09 | S3.7–S3.8 | Migration Script & Write Path | 21 |
| M10 | S5.1–S5.4 | Summarization & Tiered Memory | 18 |
| M11 | S13.1–S13.7 | Cost Governance (budget, predictive, heatmap) | 16 |
| M12 | S8.1–S8.5 | Citation Validation & Reflexion | 24 |
| M13 | S18.1–S18.5 | RAG Enhancement (hybrid, HyDE, namespaces) | 22 |
| M14 | S20.1–S20.8 | Cognitive Intelligence (ghost, momentum, fatigue) | 36 |
| M15 | S6.1–S6.5 | Replay & Partition Automation | 29 |
| M16 | S12.1–S12.4 | Export & Living Deal Memo | 14 |
| M17 | S15.1–S15.4 | Proposal Pipeline Hardening | 19 |
| M18 | S19.1–S19.6 | Agent Architecture (JSON mode, SSE, specialists) | 27 |
| M19 | S21.1–S21.6 | Ambient Intelligence (briefing, palette, anomaly) | 26 |
| | | **GRAND TOTAL** | **516** |

## Execution Protocol

1. Execute missions M01 through M19 **sequentially** — each depends on prior discoveries
2. Create evidence directory before each mission: `mkdir -p /tmp/col-qa/m{N}`
3. For each gate, capture output via `tee` to the evidence file path shown
4. After all gates for a mission complete, fill in the scorecard
5. If any gate FAILS, follow the Remediation Protocol in the Common section
6. After remediation, re-run only the failed gates
7. Do NOT proceed to the next mission until current mission scorecard is complete

## Final Completion Criteria

- All 516 gates have evidence files in `/tmp/col-qa/`
- All 19 scorecards filled with PASS/FAIL/REMEDIATED
- Zero unresolved FAIL entries
- Completion report written to `/tmp/col-qa/COMPLETION-REPORT.md`
