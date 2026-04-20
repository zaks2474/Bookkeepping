# DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL

## AGENT IDENTITY
- **agent_name:** Claude-Opus-4-5
- **run_id:** 20260204-0345-PASS3-FINAL
- **date_time:** 2026-02-04T03:45:00Z
- **repo_revision:** 07db465760f88f892b56b8eb18e1746b64f7ddf0
- **pass_type:** PASS 3 (FINAL SYNTHESIS)

---

## Source Documents Synthesized

| Pass | Agent | Run ID | Path |
|------|-------|--------|------|
| V3 Plan | Claude-Opus-4-5 | 20260204-0212-b214408d | DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Claude-Opus-4-5.20260204-0212-b214408d.md |
| V3 Plan | Gemini-CLI | 20260204-0221-gemini | DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Gemini-CLI.20260204-0221-gemini.md |
| V3 Plan | Codex | 20260204-021313-1158 | DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.Codex.20260204-021313-1158.md |
| PASS 1 | Claude-Opus-4-5 | 20260204-0304-24645315 | DEAL_LIFECYCLE_REMEDIATION_EVAL_V3.PASS1.Claude-Opus-4-5.20260204-0304-24645315.md |
| PASS 2 | Codex | 20260204-0310-5abffd | DEAL_LIFECYCLE_REMEDIATION_EVAL_V3.PASS2.Codex.20260204-0310-5abffd.md |
| Issues | All | V2 | DEAL_LIFECYCLE_HONEST_ASSESSMENT_V2.md |

### Plan Quality Scores (from PASS 1)

| Plan | Score | Rank |
|------|-------|------|
| Codex V3 | 29/30 | 1st |
| Claude V3 | 28/30 | 2nd |
| Gemini V3 | 23/30 | 3rd |

---

## PART 1: FINAL DECISION SET

These decisions are LOCKED and non-negotiable. All implementation must conform.

### D-FINAL-01: Source-of-Truth Database Model

**Decision:** PostgreSQL `zakops.deals` as SOLE source of truth

**Consensus:** ALL 3 PLANS AGREE (Claude Option A, Gemini D1, Codex Option A)

**Specification:**
- All deal state lives in `zakops.deals` and related tables
- JSON `deal_registry.json` is DEPRECATED and will be DELETED
- SQLite `ingest_state.db` retains ONLY email dedup cache (message_id), NO deal state
- DataRoom folders are derived artifacts, NOT sources of truth
- `folder_path` column in `zakops.deals` links to DataRoom location

**Migration Contract:**
1. Create `id_map` table for `DEAL-YYYY-###` → `DL-XXXX` mapping
2. Freeze legacy writers (read-only mode on JSON/SQLite)
3. Run backfill with row-count + field-by-field validation
4. Cutover with CI guards blocking legacy writes
5. NO dual-write period (increases inconsistency risk)

**Verification Proof:**
```bash
# RT-DB-SOT: Split-brain proof (5-step canary test)
# Step 1: Write canary to Postgres
CANARY_ID=$(curl -s -X POST http://localhost:8091/api/deals \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZAKOPS_API_KEY" \
  -d '{"canonical_name": "CANARY-'$(date +%s)'", "stage": "inbound"}' | jq -r '.deal_id')
# Step 2: Verify NOT in JSON
grep "$CANARY_ID" /home/zaks/DataRoom/.deal-registry/deal_registry.json && echo "FAIL: JSON written" && exit 1
# Step 3: Verify NOT in SQLite
sqlite3 /home/zaks/DataRoom/.deal-registry/ingest_state.db "SELECT * FROM deals WHERE deal_id='$CANARY_ID'" | grep -q . && echo "FAIL: SQLite written" && exit 1
# Step 4: Verify IS in Postgres
psql -c "SELECT deal_id FROM zakops.deals WHERE deal_id='$CANARY_ID'" | grep -q "$CANARY_ID" || (echo "FAIL: Not in Postgres" && exit 1)
# Step 5: Cleanup
psql -c "DELETE FROM zakops.deals WHERE deal_id='$CANARY_ID'"
echo "PASS: RT-DB-SOT"
```

---

### D-FINAL-02: Deal Taxonomy and Stage Model

**Decision:** Keep 9-stage canonical model from `workflow.py`

**Consensus:** ALL 3 PLANS AGREE

**Canonical Stages:**
```
inbound → screening → qualified → loi → diligence → closing → portfolio
                                                                    ↓
junk ←──────────────────────────────────────────────────────── archived
```

**Stage Transitions (from workflow.py):**
```python
STAGE_TRANSITIONS = {
    "inbound":    ["screening", "junk", "archived"],
    "screening":  ["qualified", "junk", "archived"],
    "qualified":  ["loi", "junk", "archived"],
    "loi":        ["diligence", "qualified", "junk", "archived"],
    "diligence":  ["closing", "loi", "junk", "archived"],
    "closing":    ["portfolio", "diligence", "junk", "archived"],
    "portfolio":  ["archived"],
    "junk":       ["inbound", "archived"],
    "archived":   []
}
```

**Migration Tasks:**
1. DELETE `/home/zaks/scripts/deal_state_machine.py` (conflicting stages)
2. UPDATE DB default from `lead` to `inbound`
3. ADD migration for any existing `lead` → `inbound`
4. REMOVE all non-canonical stage references from codebase

**Verification Proof:**
```bash
# No conflicting stage definitions
rg -c "DealStage" /home/zaks/zakops-backend/src/ /home/zaks/scripts/ --type py | grep -v workflow.py
# Expected: 0 matches (or only deprecated/archived files)
# DB default is inbound
psql -c "SELECT column_default FROM information_schema.columns WHERE table_name='deals' AND column_name='stage';"
# Expected: 'inbound'
```

---

### D-FINAL-03: Agent Tool Contract Boundaries

**Decision:** Agent calls backend HTTP APIs ONLY (no direct DB access)

**Consensus:** ALL 3 PLANS AGREE

**Agent Tool Contract:**

| Tool | Backend Endpoint | HITL Required | Correlation Required |
|------|------------------|---------------|----------------------|
| get_deal | GET /api/deals/{id} | No | Yes |
| list_deals | GET /api/deals | No | Yes |
| search_deals | POST /rag/query (8052) | No | Yes |
| transition_deal | POST /api/deals/{id}/transition | Yes | Yes |
| create_deal (NEW) | POST /api/deals | Yes | Yes |
| add_note (NEW) | POST /api/deals/{id}/notes | No | Yes |

**Enforcement:**
- Agent code MUST NOT contain `asyncpg`, `sqlalchemy`, `psycopg` imports in tools
- All requests MUST include `X-Correlation-ID` header
- HITL tools MUST wait for approval before executing backend call

**Verification Proof:**
```bash
# No direct DB access in agent tools
rg "asyncpg|sqlalchemy|psycopg|import.*pg" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/
# Expected: 0 matches
# All tool calls include correlation_id
rg "X-Correlation-ID" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/
# Expected: Present in all HTTP calls
```

---

### D-FINAL-04: Email Ingestion Architecture

**Decision:** Refactor ingestion to POST to `/api/quarantine` (Postgres-backed)

**Consensus:** ALL 3 PLANS AGREE

**Target Architecture:**
```
Gmail IMAP
    ↓
Stage 1-3: Fetch, Normalize, Match (keep existing logic)
    ↓
Stage 4: Persist → POST /api/quarantine (REWRITE - calls backend API)
    ↓
    ├── Idempotency: (message_id, mailbox, account) + body_hash fallback
    ├── Match confidence scoring + match_reason field
    └── Attachment scanning (size/type/virus check)
    ↓
Quarantine Review (Dashboard)
    ↓
Approve → POST /api/quarantine/{id}/process
    ↓
    ├── Creates Deal in zakops.deals (ATOMIC)
    ├── Scaffolds DataRoom folder structure
    ├── Triggers RAG indexing
    └── Emits deal_created event with correlation_id
    ↓
Deal visible everywhere (Dashboard, Agent, API)
```

**Safety Spec (from PASS 2 Patch 5):**
- Idempotency key: `(message_id, mailbox, account)` with body_hash fallback
- Match confidence scoring with threshold for manual review
- Attachment limits: max 50MB per file, allowed types whitelist
- Filename sanitization for path traversal protection
- Virus scan integration (ClamAV or equivalent)
- Privacy-safe storage: PII redaction in logs

**Verification Proof:**
```bash
# After refactor, run ingestion dry-run
cd /home/zaks/scripts/email_ingestion && python -m email_ingestion.cli --dry-run --days 1
# Check Postgres quarantine (should have items)
psql -c "SELECT COUNT(*) FROM zakops.quarantine_items WHERE created_at > NOW() - INTERVAL '1 hour';"
# Check JSON registry NOT updated
BEFORE=$(cat /home/zaks/DataRoom/.deal-registry/deal_registry.json | md5sum)
# ... run ingestion ...
AFTER=$(cat /home/zaks/DataRoom/.deal-registry/deal_registry.json | md5sum)
[ "$BEFORE" = "$AFTER" ] && echo "PASS: JSON unchanged" || echo "FAIL: JSON modified"
```

---

### D-FINAL-05: RAG/Embeddings Architecture

**Decision:** Central RAG service with deal_id keying and consistency contract

**Consensus:** Claude + Codex detailed; Gemini health check only → Use Claude/Codex approach

**Specification:**
- Embed only canonical deal artifacts (profiles, notes, emails, documents)
- Store `last_indexed_at` and `content_hash` in Postgres per deal
- Reindex on deal update/note add/document upload with retry queue
- Health endpoint with fail-closed behavior (search returns error, not empty)
- Nightly reconciliation job for stale index detection

**RAG Consistency Contract (from PASS 2 Patch 7):**
- Maximum stale index age: 1 hour for active deals
- Reconciliation threshold: block rollout if >5% stale
- Retry queue with exponential backoff (max 3 retries)

**Verification Proof:**
```bash
# RAG health
curl --max-time 10 http://localhost:8052/health | jq '.status'
# Expected: "ok"
# Create deal, verify indexed within SLA
DEAL_ID=$(curl -s -X POST http://localhost:8091/api/deals ... | jq -r '.deal_id')
sleep 60  # Allow indexing
curl -X POST http://localhost:8052/rag/query -d "{\"query\": \"$DEAL_ID\", \"top_k\": 5}" | jq '.results | length'
# Expected: >= 1
```

---

### D-FINAL-06: HITL Approval Persistence and Auditability

**Decision:** Mirror approvals to backend DB with correlation_id linkage

**Consensus:** Claude keeps in agent DB; Codex mirrors to backend → Use Codex approach (unified audit)

**Specification:**
- Approvals remain in `zakops_agent.approvals` for LangGraph integration
- On approval create/update, mirror to `zakops.approval_audit` with:
  - `correlation_id` (links to agent session)
  - `deal_id` (if applicable)
  - `action_type`, `actor`, `status`, `timestamps`
- Backend `deal_events` includes `correlation_id` from incoming `X-Correlation-ID` header
- Unified audit view: JOIN across `approval_audit` and `deal_events` on `correlation_id`

**Verification Proof:**
```bash
# Trigger HITL action, approve, check correlation
# 1. Agent creates pending approval (capture correlation_id)
# 2. User approves in dashboard
# 3. Query both tables
CORR_ID="test-correlation-id"
psql -c "SELECT correlation_id FROM zakops.approval_audit WHERE correlation_id='$CORR_ID';"
psql -c "SELECT correlation_id FROM zakops.deal_events WHERE correlation_id='$CORR_ID';"
# Both should return the same correlation_id
```

---

### D-FINAL-07: Authentication Model

**Decision:** Keep API key for services; add user JWT auth in Phase 5; early correlation_id in Phase 0

**Consensus:** Conflict on timing (Phase 0 vs 3 vs 5) → Resolve: Correlation Phase 0, User Auth Phase 5

**Specification:**

| Component | Auth Method | Timing |
|-----------|-------------|--------|
| Dashboard → Backend (internal) | API Key (`X-API-Key`) | Existing |
| Dashboard User Auth | JWT session (OIDC/local) | Phase 5 |
| Agent API → Backend | API Key | Existing |
| Dashboard → Agent API | Service Token (`X-Service-Token`) | Existing |
| User attribution | `user_id` in requests | Phase 5 |
| Correlation tracking | `X-Correlation-ID` header | **Phase 0** |

**Token Hardening (from PASS 2 Patch 3):**
- Short-lived service JWTs (1 hour expiry)
- Token rotation runbook
- Explicit 401/403 error codes
- Least-privilege scopes per service
- Secrets scan + alerting on long-lived tokens

**Verification Proof:**
```bash
# API key required for writes
curl -X POST http://localhost:8091/api/deals -d '{"canonical_name":"test"}' | jq '.detail'
# Expected: "Unauthorized" or 401
# With API key
curl -X POST http://localhost:8091/api/deals -H "X-API-Key: $ZAKOPS_API_KEY" -d '{"canonical_name":"test"}'
# Expected: 201 Created
```

---

## PART 2: PHASED IMPLEMENTATION PLAN

### Phase Overview

| Phase | Objective | Issues Covered | Dependencies |
|-------|-----------|----------------|--------------|
| 0 | Stop the Bleeding | ZK-0006, ZK-0007, ZK-0010, ZK-0011, ZK-0012, ZK-0018 | None |
| 1 | Data Truth Unification | ZK-0001, ZK-0008, ZK-0014 | Phase 0 |
| 2 | Contract Alignment | ZK-0003, ZK-0004, ZK-0013, ZK-0022 | Phase 1 |
| 3 | Deal Lifecycle Correctness | ZK-0009, ZK-0015, ZK-0016 | Phase 2 |
| 4 | Deal Knowledge System | ZK-0002, ZK-0019, ZK-0020, ZK-0021 | Phase 3 |
| 5 | Hardening | ZK-0005, ZK-0017 | Phase 4 |
| 6 | Legacy Decommission | Final verification | Phase 5 |

---

### Phase 0: Stop the Bleeding (Observability + Endpoint Fixes)

**Objective:** Establish traceability, fix immediate endpoint mismatches, prevent silent failures.

**Issues Covered:** ZK-ISSUE-0006, ZK-ISSUE-0007, ZK-ISSUE-0010, ZK-ISSUE-0011, ZK-ISSUE-0012, ZK-ISSUE-0018

**Tasks:**

| Task ID | Description | Owner | Effort | Files |
|---------|-------------|-------|--------|-------|
| T0.1 | Fix Dashboard quarantine endpoint: `/resolve` → `/process` | Frontend | S | `apps/dashboard/src/lib/api.ts` |
| T0.2 | Fix Dashboard notes endpoint path mismatch | Frontend | S | `apps/dashboard/src/lib/api.ts` |
| T0.3 | Add `/api/deals/{id}/notes` endpoint to orchestration API | Backend | S | `zakops-backend/src/api/orchestration/main.py` |
| T0.4 | DELETE `/home/zaks/scripts/deal_state_machine.py` | Backend | S | File deletion |
| T0.5 | Update DB default stage from `lead` to `inbound` | Backend | S | `db/migrations/xxx_fix_default_stage.sql` |
| T0.6 | Add correlation_id generation in Dashboard middleware | Frontend | M | `apps/dashboard/src/middleware.ts` |
| T0.7 | Add correlation_id propagation to backend (read `X-Correlation-ID`) | Backend | S | `zakops-backend/src/api/orchestration/main.py` |
| T0.8 | Store correlation_id in `zakops.deal_events` | Backend | S | `db/migrations/xxx_add_correlation_id.sql` |
| T0.9 | Verify RAG service health; document status | Infra | S | `SERVICE-CATALOG.md` |
| T0.10 | Add health check endpoint aggregator | Backend | M | `zakops-backend/src/api/orchestration/routers/health.py` |
| T0.11 | Fix Dashboard Zod schemas: add `.passthrough()` | Frontend | M | `apps/dashboard/src/lib/schemas.ts` |
| T0.12 | Add schema validation logging (warn on mismatch) | Frontend | S | `apps/dashboard/src/lib/api.ts` |

**Gate 0 (Must Pass):**
- [ ] Dashboard quarantine approve works (no 404) — `curl POST /process` returns 200
- [ ] Dashboard add note works — `curl POST /notes` returns 201
- [ ] No non-canonical stage names in codebase — `rg "lead|proposal|negotiation" src/` = 0
- [ ] RAG health documented in SERVICE-CATALOG.md
- [ ] correlation_id visible in logs — trace request through services
- [ ] Zod schema mismatches logged (not silent)

**Evidence Required:**
- curl outputs for endpoint tests
- ripgrep output showing zero stage conflicts
- Log trace showing correlation_id propagation
- Schema mismatch log example

**Rollback:** Revert frontend changes; add backend endpoint aliases if needed.

---

### Phase 1: Data Truth Unification (Split-Brain Elimination)

**Objective:** Make PostgreSQL the SOLE source of truth. Eliminate JSON registry writes.

**Issues Covered:** ZK-ISSUE-0001 (P0), ZK-ISSUE-0008 (P1), ZK-ISSUE-0014 (P2)

**Tasks:**

| Task ID | Description | Owner | Effort | Files |
|---------|-------------|-------|--------|-------|
| T1.1 | Create `id_map` table for legacy ID mapping | Data | S | `db/migrations/xxx_id_map.sql` |
| T1.2 | Create migration script `migrate_json_to_postgres.py` | Data | L | `scripts/migrations/migrate_json_to_postgres.py` |
| T1.3 | Run migration dry-run with validation (row count + field diff) | Data | M | N/A |
| T1.4 | Refactor `CreateDealFromEmailExecutor` to use backend API | Backend | L | `zakops-backend/src/actions/executors/deal_create_from_email.py` |
| T1.5 | Remove sys.path hack from executor | Backend | S | Same file |
| T1.6 | Migrate action engine from SQLite to Postgres `zakops.actions` | Backend | L | `zakops-backend/src/actions/engine/store.py` |
| T1.7 | Make `deal_registry.json` read-only | Infra | S | Filesystem permissions |
| T1.8 | Add CI guard: block commits adding legacy writes | DevOps | M | `.github/workflows/ci.yml` |
| T1.9 | Run production migration with rollback script ready | Data | M | N/A |

**Migration Cutover Playbook (from PASS 2 Patch 1):**
1. **Pre-cutover:** Freeze all JSON/SQLite writers (feature flag or permissions)
2. **Backfill:** Run migration with `--dry-run` first, validate counts
3. **Validation:** Row counts match, field-by-field sampling passes
4. **Cutover:** Enable Postgres-only writes, disable legacy
5. **Monitoring:** Alert on any legacy write attempts (file audit)
6. **Rollback:** If issues within 24h, restore JSON/SQLite writes, investigate

**Gate 1 (Must Pass):**
- [ ] RT-DB-SOT: Canary write test passes (see D-FINAL-01)
- [ ] Creating deal via API writes to Postgres, NOT JSON
- [ ] `deal_registry.json` not modified by any operation (file hash unchanged)
- [ ] Actions visible in API match engine state (`zakops.actions`)
- [ ] Zero sys.path hacks in production code

**Evidence Required:**
- Migration log with row counts
- DB query showing deal created via executor
- File hash diff showing JSON unchanged
- grep output confirming no sys.path

**Rollback:** Re-enable JSON writes; restore from backup if data issues.

---

### Phase 2: Contract Alignment (UI ↔ Backend ↔ Agent)

**Objective:** Ensure all API contracts are correct. Wire quarantine approval to deal creation.

**Issues Covered:** ZK-ISSUE-0003 (P1), ZK-ISSUE-0004 (P1), ZK-ISSUE-0013 (P2), ZK-ISSUE-0022 (P3)

**Tasks:**

| Task ID | Description | Owner | Effort | Files |
|---------|-------------|-------|--------|-------|
| T2.1 | Wire quarantine approval to deal creation (atomic transaction) | Backend | M | `zakops-backend/src/api/orchestration/main.py` |
| T2.2 | Add folder scaffolding hook to `POST /api/deals` | Backend | M | Same + new service |
| T2.3 | Add idempotency guard on quarantine approval | Backend | S | Same |
| T2.4 | Implement `/api/actions/capabilities` endpoint | Backend | M | `zakops-backend/src/api/orchestration/routers/actions.py` |
| T2.5 | Implement `/api/actions/metrics` endpoint | Backend | M | Same |
| T2.6 | Add `/api/deals/{id}/archive` endpoint | Backend | S | `zakops-backend/src/api/orchestration/main.py` |
| T2.7 | Add `/api/deals/{id}/restore` endpoint | Backend | S | Same |
| T2.8 | Sync OpenAPI spec with actual endpoints | Backend | M | `openapi.yaml` |
| T2.9 | Generate API client from OpenAPI | Frontend | M | `apps/dashboard/src/lib/generated/` |

**Contract Versioning (from PASS 2 Patch 2):**
- OpenAPI as source of truth for all endpoints
- Generated TypeScript client for Dashboard
- Compatibility aliases with deprecation window (2 weeks)
- Schema-drift CI check on every PR

**Gate 2 (Must Pass):**
- [ ] Approving quarantine item creates deal in ONE action (atomic)
- [ ] Deal creation creates DataRoom folder structure
- [ ] `/api/actions/capabilities` returns 200 with executor list
- [ ] `/api/actions/metrics` returns 200 with metrics data
- [ ] Archive/restore endpoints work
- [ ] OpenAPI spec matches running API (contract test passes)

**Evidence Required:**
- End-to-end trace: quarantine approval → deal creation → folder check
- curl output for capabilities/metrics
- Archive/restore curl tests
- Contract test CI output

**Rollback:** Remove atomic approval; revert to two-step manual process.

---

### Phase 3: Deal Lifecycle Correctness (Stages, HITL, Idempotency)

**Objective:** Ensure stage transitions correct, HITL works, operations idempotent.

**Issues Covered:** ZK-ISSUE-0009 (P2), ZK-ISSUE-0015 (P3), ZK-ISSUE-0016 (P2)

**Tasks:**

| Task ID | Description | Owner | Effort | Files |
|---------|-------------|-------|--------|-------|
| T3.1 | Add `create_deal` agent tool with HITL approval | Agent | M | `apps/agent-api/app/core/langgraph/tools/deal_tools.py` |
| T3.2 | Add `add_note` agent tool (no HITL) | Agent | S | Same |
| T3.3 | Pass `X-Correlation-ID` header in ALL agent tool calls | Agent | M | Same + HTTP client |
| T3.4 | Add duplicate detection to `POST /api/deals` | Backend | M | `zakops-backend/src/api/orchestration/main.py` |
| T3.5 | Add background job for approval expiry | Agent | M | `apps/agent-api/app/jobs/expire_approvals.py` |
| T3.6 | Add optimistic locking on approval execution | Agent | S | `apps/agent-api/app/services/approval.py` (NEEDS VERIFICATION: `rg -l "class.*Approval" apps/agent-api/`) |
| T3.7 | Mirror approvals to backend `approval_audit` table | Backend | M | `db/migrations/xxx_approval_audit.sql` |

**HITL Audit Unification (from PASS 2 Patch 6):**
- Every approval includes `correlation_id` and `deal_id`
- Approval mirror writes to backend on create/update
- Idempotent approval processing (check status before execute)
- TTL check at execution time (not just storage)

**Gate 3 (Must Pass):**
- [ ] Agent can create deal (with HITL approval required)
- [ ] Correlation IDs match across agent and backend logs
- [ ] Stale approvals (>1h) automatically marked expired
- [ ] Duplicate deal creation returns 409 error
- [ ] Approval executed after expiry timestamp is rejected

**Evidence Required:**
- Agent chat log showing create_deal with HITL
- SQL query showing matching correlation_ids
- Approval record showing auto-expired status
- curl showing duplicate rejection (409)

**Rollback:** Disable new agent tools; revert to existing tool set.

---

### Phase 4: Deal Knowledge System (Email + RAG + Actions)

**Objective:** Enable email ingestion, RAG indexing, wire action executors.

**Issues Covered:** ZK-ISSUE-0002 (P0), ZK-ISSUE-0019 (P2), ZK-ISSUE-0020 (P2), ZK-ISSUE-0021 (P2)

**Tasks:**

| Task ID | Description | Owner | Effort | Files |
|---------|-------------|-------|--------|-------|
| T4.1 | Refactor email ingestion Stage 4 to POST to `/api/quarantine` | Backend | L | `scripts/email_ingestion/stage_4_persist.py` |
| T4.2 | Add idempotency key table for email dedup | Backend | M | `db/migrations/xxx_ingestion_idempotency.sql` |
| T4.3 | Add attachment scanning (size/type limits) | Backend | M | Ingestion service |
| T4.4 | Test email ingestion with dry-run | QA | M | N/A |
| T4.5 | Enable email ingestion cron job | Infra | S | `/etc/cron.d/dataroom-automation` |
| T4.6 | Wire `deal_append_email_materials` executor | Backend | M | `zakops-backend/src/actions/executors/deal_append_email_materials.py` |
| T4.7 | Wire `deal_enrich_materials` executor | Backend | M | `zakops-backend/src/actions/executors/deal_enrich_materials.py` |
| T4.8 | Wire `rag_reindex_deal` executor | Backend | M | `zakops-backend/src/actions/executors/rag_reindex_deal.py` |
| T4.9 | Add `last_indexed_at` + `content_hash` columns to deals | Backend | S | Migration |
| T4.10 | Add deal indexing hook on create/update | Backend | M | Deal service |
| T4.11 | Add RAG reindex retry queue | Backend | M | `zakops-backend/src/services/queue.py` (NEEDS VERIFICATION: `rg -l "queue\|Queue" zakops-backend/src/services/`) |
| T4.12 | Implement SSE endpoint (or document as polling) | Backend | L | `routers/events.py` |
| T4.13 | Add deal age tracking field | Backend | S | Migration |
| T4.14 | Add basic scheduled reminders | Backend | M | Scheduler service |

**Email Ingestion Safety Spec (from PASS 2 Patch 5):**
- Idempotency: `(message_id, mailbox, account)` + body_hash
- Match confidence: Store `match_reason` and confidence score
- Attachment scanning: ClamAV integration, size limits
- Privacy: PII redaction in logs, secure storage

**RAG Consistency (from PASS 2 Patch 7):**
- `last_indexed_at` checked on every query
- `content_hash` for change detection
- Retry queue with max 3 attempts
- Health gate: block rollout if stale rate >5%

**Gate 4 (Must Pass):**
- [ ] Emails flow from Gmail → quarantine → deal (end-to-end)
- [ ] Duplicate emails don't create duplicate quarantine items
- [ ] Deal content indexed in RAG (search_deals returns results)
- [ ] At least 3 executors wired and tested
- [ ] SSE endpoint works OR polling documented as intentional

**Evidence Required:**
- End-to-end email → deal trace
- RAG query returning indexed deal
- Executor logs showing successful runs
- SSE event received OR documentation

**Rollback:** Disable cron job; revert ingestion to dry-run mode.

---

### Phase 5: Hardening (Security, Reliability)

**Objective:** Add user authentication, retention policy, monitoring.

**Issues Covered:** ZK-ISSUE-0005 (P1), ZK-ISSUE-0017 (P3)

**Tasks:**

| Task ID | Description | Owner | Effort | Files |
|---------|-------------|-------|--------|-------|
| T5.1 | Add user authentication to Dashboard (OIDC/JWT) | Frontend | L | `apps/dashboard/src/` |
| T5.2 | Add auth middleware to require login | Frontend | M | `middleware.ts` |
| T5.3 | Pass user ID in backend requests | Frontend | M | API client |
| T5.4 | Add user attribution to `deal_events` | Backend | S | Event service |
| T5.5 | Define retention policy document | Product | S | `/home/zaks/bookkeeping/docs/RETENTION_POLICY.md` |
| T5.6 | Implement retention cleanup job (if policy defined) | Backend | M | Scheduler |
| T5.7 | Add request tracing (trace ID in logs) | Backend | M | Middleware |
| T5.8 | Add performance monitoring (response times) | Infra | M | Metrics service |
| T5.9 | Add error alerting (Slack/email on 500s) | Infra | M | Alert rules |
| T5.10 | Add token rotation runbook | Security | S | Documentation |

**Gate 5 (Must Pass):**
- [ ] Dashboard requires login (unauthenticated → redirect)
- [ ] Deal events show user attribution
- [ ] Retention policy documented
- [ ] Traces visible in logs (request → response correlation)
- [ ] Alerts fire on 500 errors

**Evidence Required:**
- Screenshot of login page
- DB query showing user actor in events
- Retention policy document link
- Log grep showing trace ID across services

**Rollback:** Feature flag to disable auth requirement.

---

### Phase 6: Legacy Decommission and Final Proof

**Objective:** Remove all legacy components. Prove system is clean.

**Issues Covered:** Final verification of all 22 issues

**Tasks:**

| Task ID | Description | Owner | Effort | Files |
|---------|-------------|-------|--------|-------|
| T6.1 | DELETE `deal_registry.json` | Backend | S | File deletion |
| T6.2 | DELETE `/home/zaks/scripts/deal_registry.py` | Backend | S | File deletion |
| T6.3 | DELETE `/home/zaks/scripts/deal_state_machine.py` | Backend | S | File deletion |
| T6.4 | DELETE `zakops-backend/src/api/deal_lifecycle/` | Backend | M | Directory deletion |
| T6.5 | Remove SQLite state DB path from code | Backend | S | Config cleanup |
| T6.6 | Verify no code references legacy files | QA | M | ripgrep scan |
| T6.7 | Update SERVICE-CATALOG.md | Docs | S | Documentation |
| T6.8 | Run full regression test suite | QA | L | CI/CD |
| T6.9 | Final 22-issue checklist verification | QA | M | This document |
| T6.10 | Record legacy decommission in CHANGES.md | Docs | S | `/home/zaks/bookkeeping/CHANGES.md` |

**Changelog Strategy (MANDATORY):**

Before any legacy file deletion, the following entry MUST be added to `/home/zaks/bookkeeping/CHANGES.md`:

```markdown
## YYYY-MM-DD: LEGACY DECOMMISSION COMPLETE (V3 Remediation Phase 6)

### Files Deleted:
- `/home/zaks/DataRoom/.deal-registry/deal_registry.json` — Migrated to Postgres `zakops.deals`
- `/home/zaks/scripts/deal_registry.py` — Replaced by backend orchestration API
- `/home/zaks/scripts/deal_state_machine.py` — Duplicate of `workflow.py`, removed
- `/home/zaks/zakops-backend/src/api/deal_lifecycle/` — Legacy API, replaced by orchestration API
- SQLite `ingest_state.db` deal tables — Migrated to Postgres (email dedup cache retained)

### Migration Reference:
- Migration script: `scripts/migrations/migrate_json_to_postgres.py`
- ID mapping table: `zakops.id_map`
- Remediation plan: `DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.md`

### Verification:
- All 22 ZK-ISSUE-* resolved
- RT-DB-SOT canary test passed
- CI guard active for legacy file references
```

**Changelog Verification Command:**
```bash
# Verify changelog entry exists
rg "LEGACY DECOMMISSION COMPLETE" /home/zaks/bookkeeping/CHANGES.md || (echo "FAIL: Changelog entry missing" && exit 1)
rg "deal_registry.json" /home/zaks/bookkeeping/CHANGES.md | grep -q "Deleted\|Migrated" || (echo "FAIL: deal_registry.json not documented" && exit 1)
echo "PASS: Changelog strategy verified"
```

**Decommission Verification Commands:**
```bash
# Verify no code references legacy files
rg "deal_registry.json|deal_state_machine|deal_lifecycle|sys.path" \
  /home/zaks/zakops-backend/src/ /home/zaks/zakops-agent-api/ \
  --type py --type ts
# Expected: 0 matches

# Verify files deleted
ls /home/zaks/DataRoom/.deal-registry/deal_registry.json 2>&1 | grep -q "No such file"
ls /home/zaks/scripts/deal_registry.py 2>&1 | grep -q "No such file"
ls /home/zaks/zakops-backend/src/api/deal_lifecycle/ 2>&1 | grep -q "No such file"
# All should pass

# CI guard active
git diff HEAD~1 | grep -q "deal_registry.json" && echo "BLOCKED" || echo "PASS"
```

**Gate 6 (Must Pass):**
- [ ] No legacy file references in codebase
- [ ] All 22 V2 issues verified resolved (see coverage matrix)
- [ ] Full regression passes
- [ ] Documentation updated
- [ ] CHANGES.md entry documenting legacy decommission exists

**Evidence Required:**
- ripgrep output showing no legacy references
- Coverage matrix with all checkmarks
- CI/CD test suite passing
- SERVICE-CATALOG.md diff
- CHANGES.md entry with "LEGACY DECOMMISSION COMPLETE" header

**Rollback:** Restore from git if hidden dependencies discovered.

---

## PART 3: NO-DROP COVERAGE MATRIX

Every issue from V2 MUST be addressed. No blanks allowed.

| Issue ID | Title | Severity | Phase | Tasks | Verification | Status |
|----------|-------|----------|-------|-------|--------------|--------|
| ZK-ISSUE-0001 | Split-brain persistence | P0 | 1 | T1.1-T1.9 | RT-DB-SOT canary test; JSON unchanged | [ ] |
| ZK-ISSUE-0002 | Email ingestion disabled | P0 | 4 | T4.1-T4.5 | Email → quarantine → deal trace | [ ] |
| ZK-ISSUE-0003 | Quarantine no deal creation | P1 | 2 | T2.1-T2.3 | Approve → deal exists atomically | [ ] |
| ZK-ISSUE-0004 | No DataRoom folders | P1 | 2 | T2.2 | Create deal → folder exists | [ ] |
| ZK-ISSUE-0005 | Dashboard no auth | P1 | 5 | T5.1-T5.3 | Login required; redirect if unauth | [ ] |
| ZK-ISSUE-0006 | Wrong quarantine endpoint | P1 | 0 | T0.1 | Dashboard approve works (200) | [ ] |
| ZK-ISSUE-0007 | Stage taxonomy conflicts | P1 | 0 | T0.4-T0.5 | No legacy stages in code | [ ] |
| ZK-ISSUE-0008 | Actions split Postgres/SQLite | P1 | 1 | T1.6 | Single `zakops.actions` table | [ ] |
| ZK-ISSUE-0009 | Agent no create_deal | P2 | 3 | T3.1-T3.2 | Agent creates deal with HITL | [ ] |
| ZK-ISSUE-0010 | RAG unverified | P2 | 0,4 | T0.9, T4.8-T4.11 | Health check OK; search returns results | [ ] |
| ZK-ISSUE-0011 | No event correlation | P2 | 0 | T0.6-T0.8 | Matching correlation_ids across logs | [ ] |
| ZK-ISSUE-0012 | Notes endpoint mismatch | P2 | 0 | T0.2-T0.3 | Notes endpoint works (201) | [ ] |
| ZK-ISSUE-0013 | Capabilities/metrics 501 | P2 | 2 | T2.4-T2.5 | Endpoints return 200 with data | [ ] |
| ZK-ISSUE-0014 | sys.path hack | P2 | 1 | T1.5 | No sys.path in code | [ ] |
| ZK-ISSUE-0015 | Approval expiry lazy | P3 | 3 | T3.5-T3.6 | Stale approvals auto-expired | [ ] |
| ZK-ISSUE-0016 | No duplicate detection | P2 | 3 | T3.4 | Duplicates rejected (409) | [ ] |
| ZK-ISSUE-0017 | No retention policy | P3 | 5 | T5.5-T5.6 | Policy documented + job scheduled | [ ] |
| ZK-ISSUE-0018 | Zod schema mismatch | P2 | 0 | T0.11-T0.12 | Mismatches logged; passthrough enabled | [ ] |
| ZK-ISSUE-0019 | Executors unwired | P2 | 4 | T4.6-T4.8 | 3+ executors working | [ ] |
| ZK-ISSUE-0020 | SSE not implemented | P2 | 4 | T4.12 | SSE works OR documented as polling | [ ] |
| ZK-ISSUE-0021 | No scheduling/reminders | P2 | 4 | T4.13-T4.14 | Reminders fire for overdue deals | [ ] |
| ZK-ISSUE-0022 | Archive/restore missing | P3 | 2 | T2.6-T2.7 | Endpoints work (200) | [ ] |

**Coverage Confirmation:**
- [x] All 22 ZK-ISSUE-* IDs have assigned phase and tasks
- [x] All 22 ZK-ISSUE-* IDs have verification criteria
- [x] No issue deferred to "Backlog" (ZK-ISSUE-0021 promoted from Gemini backlog)
- [x] P0 issues in earliest possible phase
- [x] Dependencies respected in phase ordering

---

## PART 4: BUILDER MISSION SEQUENCE

Ordered task list for execution. Each task is atomic and can be assigned to a developer.

### Sprint 0: Stop the Bleeding (Phase 0)
**Duration:** 3-5 days
**Parallel Tracks:** Frontend (T0.1, T0.2, T0.6, T0.11, T0.12) | Backend (T0.3-T0.5, T0.7-T0.10)

```
DAY 1:
├─ T0.1: Fix Dashboard /resolve → /process [Frontend]
├─ T0.4: DELETE deal_state_machine.py [Backend]
└─ T0.5: Fix DB default stage [Backend]

DAY 2:
├─ T0.2: Fix Dashboard notes endpoint [Frontend]
├─ T0.3: Add /notes endpoint to orchestration API [Backend]
└─ T0.9: Verify RAG health, document [Infra]

DAY 3:
├─ T0.6: Add correlation_id generation [Frontend]
├─ T0.7: Add correlation_id reading [Backend]
└─ T0.8: Add correlation_id to deal_events [Backend]

DAY 4:
├─ T0.10: Add health check aggregator [Backend]
├─ T0.11: Fix Zod schemas (.passthrough) [Frontend]
└─ T0.12: Add schema validation logging [Frontend]

DAY 5:
└─ Gate 0 verification and sign-off
```

### Sprint 1: Data Truth Unification (Phase 1)
**Duration:** 7-10 days
**Parallel Tracks:** Migration (T1.1-T1.3, T1.7-T1.9) | Refactor (T1.4-T1.6, T1.8)

```
WEEK 1:
├─ T1.1: Create id_map table [Data]
├─ T1.2: Write migration script [Data]
├─ T1.4: Refactor CreateDealFromEmailExecutor [Backend]
└─ T1.5: Remove sys.path hack [Backend]

WEEK 2:
├─ T1.3: Run migration dry-run [Data]
├─ T1.6: Migrate action engine to Postgres [Backend]
├─ T1.7: Make deal_registry.json read-only [Infra]
├─ T1.8: Add CI guard [DevOps]
└─ T1.9: Production migration [Data]

└─ Gate 1 verification and sign-off
```

### Sprint 2: Contract Alignment (Phase 2)
**Duration:** 5-7 days

```
DAYS 1-3:
├─ T2.1: Wire quarantine approval to deal creation [Backend]
├─ T2.2: Add folder scaffolding hook [Backend]
└─ T2.3: Add idempotency guard [Backend]

DAYS 4-5:
├─ T2.4: Implement /capabilities endpoint [Backend]
├─ T2.5: Implement /metrics endpoint [Backend]
├─ T2.6: Add /archive endpoint [Backend]
└─ T2.7: Add /restore endpoint [Backend]

DAYS 6-7:
├─ T2.8: Sync OpenAPI spec [Backend]
├─ T2.9: Generate API client [Frontend]
└─ Gate 2 verification and sign-off
```

### Sprint 3: Deal Lifecycle Correctness (Phase 3)
**Duration:** 5-7 days

```
DAYS 1-3:
├─ T3.1: Add create_deal agent tool [Agent]
├─ T3.2: Add add_note agent tool [Agent]
└─ T3.3: Add correlation_id to all tool calls [Agent]

DAYS 4-5:
├─ T3.4: Add duplicate detection [Backend]
├─ T3.5: Add approval expiry job [Agent]
└─ T3.6: Add optimistic locking [Agent]

DAYS 6-7:
├─ T3.7: Mirror approvals to backend [Backend]
└─ Gate 3 verification and sign-off
```

### Sprint 4: Deal Knowledge System (Phase 4)
**Duration:** 10-14 days

```
WEEK 1:
├─ T4.1: Refactor email ingestion Stage 4 [Backend]
├─ T4.2: Add idempotency key table [Backend]
├─ T4.3: Add attachment scanning [Backend]
├─ T4.4: Test with dry-run [QA]
└─ T4.5: Enable cron job [Infra]

WEEK 2:
├─ T4.6: Wire deal_append_email_materials [Backend]
├─ T4.7: Wire deal_enrich_materials [Backend]
├─ T4.8: Wire rag_reindex_deal [Backend]
├─ T4.9: Add last_indexed_at columns [Backend]
└─ T4.10: Add deal indexing hook [Backend]

DAYS 11-14:
├─ T4.11: Add RAG reindex retry queue [Backend]
├─ T4.12: Implement SSE endpoint [Backend]
├─ T4.13: Add deal age tracking [Backend]
├─ T4.14: Add scheduled reminders [Backend]
└─ Gate 4 verification and sign-off
```

### Sprint 5: Hardening (Phase 5)
**Duration:** 7-10 days

```
WEEK 1:
├─ T5.1: Add user authentication [Frontend]
├─ T5.2: Add auth middleware [Frontend]
├─ T5.3: Pass user ID in requests [Frontend]
└─ T5.4: Add user attribution [Backend]

WEEK 2:
├─ T5.5: Define retention policy [Product]
├─ T5.6: Implement cleanup job [Backend]
├─ T5.7: Add request tracing [Backend]
├─ T5.8: Add performance monitoring [Infra]
├─ T5.9: Add error alerting [Infra]
├─ T5.10: Token rotation runbook [Security]
└─ Gate 5 verification and sign-off
```

### Sprint 6: Legacy Decommission (Phase 6)
**Duration:** 3-5 days

```
DAYS 1-2:
├─ T6.1: DELETE deal_registry.json
├─ T6.2: DELETE scripts/deal_registry.py
├─ T6.3: DELETE scripts/deal_state_machine.py
├─ T6.4: DELETE api/deal_lifecycle/
└─ T6.5: Remove SQLite path from code

DAYS 3-5:
├─ T6.6: Verify no legacy references
├─ T6.7: Update SERVICE-CATALOG.md
├─ T6.8: Run full regression
├─ T6.9: Final 22-issue checklist
└─ Gate 6 verification and sign-off
```

---

## PART 5: FINAL QA PLAN

### RT Gates (Red-Team Verification)

| Gate ID | Name | Phase | Test Procedure | Pass Criteria |
|---------|------|-------|----------------|---------------|
| RT-DB-SOT | Split-brain proof | 1 | Canary write to Postgres, verify NOT in JSON/SQLite | Canary only in Postgres |
| RT-TIMEOUT | Anti-hang enforcement | All | All curl commands have `--max-time 30` | No hung tests |
| RT-PATH-MATRIX | Endpoint coverage | 2 | Test all endpoints in OpenAPI spec | 100% coverage |
| RT-ERROR-REDACT | Error redaction | 5 | Trigger errors, verify no secrets in logs | No API keys/tokens in errors |
| RT-GOLDEN-PATH | E2E smoke test | 4 | Full email → deal → RAG flow | End-to-end success |
| RT-CORRELATION | Trace linkage | 0 | Request with correlation_id, verify in all logs | Same ID across services |

### QA Pass #1: Functional (Happy Paths)

| Test | Steps | Expected |
|------|-------|----------|
| Deal CRUD | Create, Read, Update, Archive | All operations succeed |
| Stage Transitions | inbound→screening→qualified | Transitions work, events logged |
| Quarantine Flow | Create item, approve, deal created | Deal exists with folder |
| Agent Tools | get_deal, transition_deal, create_deal | All return correct data |
| Email Ingestion | Send test email, wait for cron | Quarantine item created |
| RAG Search | Index deal, search for content | Results returned |

### QA Pass #2: Adversarial

| Test | Steps | Expected |
|------|-------|----------|
| Auth Failure | Call without API key | 401 Unauthorized |
| Invalid Stage | Transition to "bogus" | 400 Bad Request |
| Backend Down | Stop backend, call agent | Graceful error message |
| RAG Down | Stop RAG, call search_deals | Explicit error, not empty |
| Duplicate Deal | Create same name twice | 409 Conflict |
| HITL Timeout | Create approval, wait 2 hours | Approval marked expired |
| Concurrent Transition | Two transitions same deal | One succeeds, one fails |
| Legacy Write | Attempt to write to JSON | Permission denied or CI block |

### Evidence Checklist

For each gate and QA pass, the following evidence must be captured:

```
/home/zaks/bookkeeping/evidence/
├── phase0/
│   ├── gate0_endpoint_tests.log
│   ├── gate0_correlation_trace.log
│   └── gate0_signoff.md
├── phase1/
│   ├── gate1_rt_db_sot.log
│   ├── gate1_migration_report.csv
│   └── gate1_signoff.md
├── phase2/
│   ├── gate2_contract_tests.log
│   ├── gate2_quarantine_flow.log
│   └── gate2_signoff.md
├── phase3/
│   ├── gate3_agent_tools.log
│   ├── gate3_correlation_proof.log
│   └── gate3_signoff.md
├── phase4/
│   ├── gate4_email_flow.log
│   ├── gate4_rag_indexing.log
│   ├── gate4_executor_tests.log
│   └── gate4_signoff.md
├── phase5/
│   ├── gate5_auth_tests.log
│   ├── gate5_retention_policy.md
│   └── gate5_signoff.md
├── phase6/
│   ├── gate6_legacy_scan.log
│   ├── gate6_regression_results.xml
│   ├── gate6_coverage_matrix_final.md
│   └── gate6_signoff.md
└── final/
    ├── qa_pass1_functional.log
    ├── qa_pass2_adversarial.log
    └── REMEDIATION_COMPLETE.md
```

---

## Summary

This V3 FINAL plan synthesizes three independent remediation plans, PASS 1 coverage analysis, and PASS 2 red-team patches into one execution-ready document.

**Key Metrics:**
- **Total Issues:** 22 (2 P0, 6 P1, 11 P2, 3 P3)
- **Total Tasks:** 69 atomic tasks across 7 phases
- **Total Phases:** 7 (0-6)
- **Decision Set:** 7 locked decisions with consensus
- **Gates:** 7 phase gates + 6 RT gates
- **QA Passes:** 2 (functional + adversarial)

**Critical Path:**
1. Phase 0 (Stop the Bleeding) → 3-5 days
2. Phase 1 (Split-Brain Fix) → 7-10 days ← **HIGHEST RISK**
3. Phase 2 (Contract Alignment) → 5-7 days
4. Phase 3 (Lifecycle Correctness) → 5-7 days
5. Phase 4 (Knowledge System) → 10-14 days ← **LARGEST SCOPE**
6. Phase 5 (Hardening) → 7-10 days
7. Phase 6 (Decommission) → 3-5 days

**Total Estimated Duration:** 40-58 days (developer-days, parallelizable)

---

*PASS 3 FINAL synthesized by Claude-Opus-4-5 on 2026-02-04.*
*All 22 V2 issues covered. No drops. Ready for execution.*
