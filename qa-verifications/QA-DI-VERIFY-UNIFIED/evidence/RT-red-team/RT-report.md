# RED-TEAM GATES (RT1-RT20)
## QA-DI-VERIFY-UNIFIED | 2026-02-09

---

### RT-1: transition_deal_state() Has Actual SQL Logic — PASS

Full PL/pgSQL function verified via `pg_get_functiondef()`. Contains:
- `SELECT ... FOR UPDATE` row-level locking
- Status derivation logic (archived/junk -> 'archived', else -> 'active')
- Idempotency check (return current state if already in target)
- `UPDATE zakops.deals SET stage, status, audit_trail, updated_at`
- `INSERT INTO zakops.deal_events` with structured payload
- `RETURN QUERY` with previous/new state
- **78 lines of real PL/pgSQL** — no stubs, no TODOs

---

### RT-2: CHECK Constraint Definition is Real — PASS

Via `pg_get_constraintdef()`:

**chk_deals_stage**:
```sql
CHECK (stage IN ('inbound','screening','qualified','loi','diligence','closing','portfolio','junk','archived'))
```

**chk_deal_lifecycle**:
```sql
CHECK (
  (status='active' AND stage NOT IN ('archived','junk') AND deleted=false)
  OR (status='archived' AND stage IN ('archived','junk') AND deleted=false)
  OR (status='deleted' AND deleted=true)
)
```

Both are real constraints with actual value checks — not placeholder TRUE.

---

### RT-3: Trigger Is Real and Fires — PASS

Via `pg_get_triggerdef()`:

1. **deals_updated_at**: `BEFORE UPDATE FOR EACH ROW EXECUTE FUNCTION update_timestamp()`
2. **enforce_deal_lifecycle_trigger**: `BEFORE INSERT OR UPDATE FOR EACH ROW EXECUTE FUNCTION enforce_deal_lifecycle()`

`enforce_deal_lifecycle()` function verified — 23 lines of real PL/pgSQL:
- Auto-corrects stage=archived/junk with status=active -> sets status='archived'
- Auto-corrects deleted=true with wrong status -> sets status='deleted'
- Raises exception if active status with terminal stage

---

### RT-4: Audit Trail Has Real Data — PASS

Table name is `deal_events` (not `audit_trail`):
- **99 rows** with real entries
- Event types: deal_created, stage_changed, deal_archived, deal_restored, deal_transitioned
- Sample: DL-0001 created 2026-02-02, stage_changed inbound->screening, screening->qualified
- Fields: id, deal_id, event_type, event_source, actor, payload (JSONB), created_at, sequence_number, correlation_id
- Plus `audit_trail` JSONB column on deals table itself with per-deal history

---

### RT-5: Stage Config Imported by 4+ Consumers — PASS

`execution-contracts.ts` (PIPELINE_STAGES, DEAL_STAGE_*, ALL_STAGES_ORDERED) imported by **26 files**:
- hq/page.tsx, dashboard/page.tsx, deals/page.tsx, deals/[id]/page.tsx
- DealBoard.tsx, PipelineOverview.tsx, ActivityFeed.tsx
- DealHeader.tsx, DealWorkspace.tsx, DealTimeline.tsx, DealChat.tsx
- global-search.tsx, api/chat/route.ts
- ApprovalPreview.tsx, ApprovalCard.tsx, ToolCallCard.tsx, AgentRunTimeline.tsx, AgentPanel.tsx, ApprovalCheckpoint.tsx
- useApprovalFlow.ts, useAgentRun.ts
- types/api.ts, types/events.ts, lib/agent-client.ts
- integration.test.tsx, deal-integrity.test.ts

**26 consumers >> 4 threshold**

---

### RT-6: Server-Side Counting via Pipeline/Summary API — PASS

**hq/page.tsx**:
```typescript
// Line 54-56: DEAL-INTEGRITY-UNIFIED L3: Server-computed stage counts from pipeline summary
acc[stage] = pipelineData?.stages[stage]?.count ?? 0;
```
Uses `getPipeline()` API call, not client-side counting.

**dashboard/page.tsx**:
```typescript
// Line 117-119: DEAL-INTEGRITY-UNIFIED L3: Server-computed stage counts from pipeline summary
acc[stage] = pipelineData?.stages[stage]?.count ?? 0;
```
Same pattern — server-computed counts from pipeline API.

No `deals.filter().length` or client-side counting patterns found.

---

### RT-7: Error Boundaries Have Real Logic — PASS

File: `apps/dashboard/src/components/ErrorBoundary.tsx` (77 lines)
- `getDerivedStateFromError(error)`: returns `{ hasError: true, error }`
- `componentDidCatch(error, errorInfo)`: logs to console
- `render()`: shows Card with error message, "Try again" button
- `handleReset()`: resets state to `{ hasError: false, error: null }`
- Real UI rendering with IconAlertTriangle, CardHeader, CardContent, pre block for error message

---

### RT-8: allSettled Results Are Handled — PASS

All 4 pages check `status === 'fulfilled'` / `'rejected'`:

**hq/page.tsx** (lines 35-42):
```typescript
if (results[0].status === 'fulfilled') setPipelineData(results[0].value);
else console.error('Failed to load pipeline:', results[0].reason);
if (results[1].status === 'fulfilled') setPendingActions(results[1].value);
else console.error('Failed to load actions:', results[1].reason);
// ... etc for all 4 results
```

Same pattern in dashboard/page.tsx, deals/[id]/page.tsx, actions/page.tsx.

---

### RT-9: DSN Gate Actually Exits/Raises on Mismatch — PASS

File: `src/api/orchestration/main.py` (lines 372-387):
```python
actual_db = db_info["dbname"]
if actual_db != CANONICAL_DB_NAME:
    await db_pool.close()
    raise RuntimeError(
        f"STARTUP GATE FAILURE: Connected to database '{actual_db}' "
        f"but canonical database is '{CANONICAL_DB_NAME}'. "
        f"Refusing to start. Fix DATABASE_URL to point to the canonical DB."
    )
```

Closes pool AND raises RuntimeError — not just a warning or log.

---

### RT-10: Health Endpoint Reads DB Info Dynamically — PASS

DB identity is populated at startup from live SQL query:
```python
db_info = await conn.fetchrow(
    "SELECT current_database() AS dbname, current_user AS dbuser, "
    "inet_server_addr() AS host, inet_server_port() AS port"
)
app.state.db_identity = {
    "dbname": actual_db,
    "user": actual_user,
    "host": str(db_info["host"]),
    "port": int(db_info["port"]),
}
```

Live verification: health returns `"dbname": "zakops"`, `"host": "172.23.0.3"` — not hardcoded localhost.

---

### RT-11: Performance Baselines Have Real Timing Numbers — PASS

From `query-profiles.md`:
- Pipeline summary: Planning 1.024ms, Execution 0.228ms
- Deals listing: Planning 0.985ms, Execution 0.109ms
- API: pipeline/summary ~1ms, deals ~4ms, health ~2ms
- 9 indexes documented with purposes

Real numbers from EXPLAIN ANALYZE output — not placeholder "TBD" values.

---

### RT-12: Tests Have Real Assertions — PASS

**deal-integrity.test.ts**: 40+ expect() calls:
```typescript
expect(res.status).toBe(200);
expect(deals.length).toBeGreaterThan(0);
expect(deal.status).toBe('active');
expect(found).toBeUndefined();
expect(checkDeal.stage).toBe('archived');
```

**test_idempotency.py**: 15+ assert statements:
```python
assert actual == expected
assert stage in STAGE_TRANSITIONS
assert transition.deal_id == "test-deal-123"
```

**test_contract_compliance.py**: validate() against OpenAPI schemas.

No empty test bodies or `pass` stubs.

---

### RT-13: ADRs Have Real Content — PASS

| ADR | Lines | TODO/TBD Count |
|-----|-------|----------------|
| ADR-001 | 55 | 0 |
| ADR-002 | 88 | 0 |
| ADR-003 | 79 | 0 |

All > 20 lines, zero TODO/TBD/PLACEHOLDER/FIXME markers. All contain Context, Decision, Implementation, and Consequences sections.

---

### RT-14: Runbook Has Concrete Commands — PASS

`RUNBOOK-add-deal-stage.md` contains:
- `make sync-all-types`
- `make validate-local`
- `npm run dev`
- `bash /home/zaks/zakops-backend/scripts/qa_smoke.sh`
- SQL: `ALTER TABLE deals DROP CONSTRAINT ...`, `ALTER TABLE deals ADD CONSTRAINT ...`
- Code examples: TypeScript (execution-contracts.ts update), Python (VALID_TRANSITIONS dict)

---

### RT-15: Innovation Roadmap Has 34+ I-XX Entries — FAIL

The roadmap contains **8 innovation ideas** organized by P1/P2/P3 priority tiers.
It does NOT use I-XX numbering (I-01 through I-34).
Only themed idea groups, not 34 individual entries.

---

### RT-16: sync-all-types Makefile Target Has Real Sub-Targets — PASS

```makefile
sync-all-types: sync-types sync-backend-models sync-agent-types sync-rag-models
```

4 real sub-targets:
1. `sync-types`: Backend -> Dashboard TypeScript types
2. `sync-backend-models`: Backend -> Agent SDK Python models
3. `sync-agent-types`: Agent -> Dashboard TypeScript types
4. `sync-rag-models`: RAG -> Backend Python models

---

### RT-17: Contract Sync Has Recent Commit on Generated Files — PASS

Generated files exist and are current:
- `apps/dashboard/src/lib/api-types.generated.ts` (158,295 bytes, modified 2026-02-08 22:14)
- `apps/dashboard/src/lib/agent-api-types.generated.ts`

Recent commit: `5eb7ce6 feat: HYBRID-GUARDRAIL-EXEC-002 full stack type safety + QA-HG-VERIFY-002 remediation`

`make validate-local` passes with "Surface 1: Backend -> Dashboard: current" confirming no drift.

---

### RT-18: Organizational Root Cause Acknowledged — PASS

The final-verification.md explicitly documents organizational root causes:
- **DI-ISSUE-006**: "Split-brain database (two Postgres instances)" — infrastructure misconfiguration
- **ADR-002**: Documents the discovery of a rogue container on port 5435 with divergent data
- **ADR-003**: Documents "8+ hardcoded stage arrays scattered across multiple files" as a process/codebase organization failure
- **Change Protocol**: Establishes governance to prevent recurrence

The builder documents acknowledge these were systemic issues (not just code bugs).

---

### RT-19: Column Names Match DB Reality — PASS

Actual columns from `information_schema.columns WHERE table_name='deals'`:
1. deal_id (varchar) ✓
2. canonical_name (varchar) ✓
3. display_name (varchar) ✓
4. folder_path (varchar) ✓
5. stage (varchar) ✓
6. status (varchar) ✓
7. identifiers (jsonb) ✓
8. company_info (jsonb) ✓
9. broker (jsonb) ✓
10. metadata (jsonb) ✓
11. deleted (boolean) ✓
12. created_at (timestamptz) ✓
13. updated_at (timestamptz) ✓
14. audit_trail (jsonb) ✓

All 14 columns match. deal_events table also exists with 99 rows (separate audit event store).

---

### RT-20: All 10 Q Constraints Formally Answered — PASS

From `final-verification.md` section "4. Mandatory Platform Constraints (Q1-Q10)":

| Q# | Constraint | Status |
|----|-----------|--------|
| Q1 | Backfill reversibility | SATISFIED |
| Q2 | Production observability | SATISFIED |
| Q3 | Deployment and rollback sequencing | SATISFIED |
| Q4 | Automated test strategy | SATISFIED |
| Q5 | Agent API and RAG service impact | PARTIALLY SATISFIED |
| Q6 | Contract sync enforcement | SATISFIED |
| Q7 | Lifecycle model (Option A with FSM) | SATISFIED |
| Q8 | Concurrency safety | SATISFIED |
| Q9 | Performance baselines | SATISFIED |
| Q10 | Governance model | SATISFIED |

9/10 fully satisfied, 1 partially (Q5: RAG re-index deferred).

---

## RED-TEAM SUMMARY

| Gate | Result | Key Evidence |
|------|--------|-------------|
| RT-1 | **PASS** | 78-line PL/pgSQL with SELECT FOR UPDATE, UPDATE, INSERT |
| RT-2 | **PASS** | chk_deals_stage + chk_deal_lifecycle real CHECK constraints |
| RT-3 | **PASS** | enforce_deal_lifecycle_trigger + deals_updated_at, real functions |
| RT-4 | **PASS** | deal_events: 99 rows; audit_trail JSONB on deals |
| RT-5 | **PASS** | 26 files import from execution-contracts.ts |
| RT-6 | **PASS** | hq/page + dashboard/page use getPipeline() server counts |
| RT-7 | **PASS** | ErrorBoundary with componentDidCatch + getDerivedStateFromError |
| RT-8 | **PASS** | All 4 pages check fulfilled/rejected on allSettled |
| RT-9 | **PASS** | RuntimeError raised + pool closed on DSN mismatch |
| RT-10 | **PASS** | Dynamic SQL: current_database(), inet_server_addr() |
| RT-11 | **PASS** | Real timing: 0.228ms, 0.109ms, API 1-4ms |
| RT-12 | **PASS** | 40+ expect() in TS, 15+ assert in Python |
| RT-13 | **PASS** | ADRs: 55/88/79 lines, 0 TODO/TBD |
| RT-14 | **PASS** | make, npm, ALTER TABLE, bash commands in runbook |
| RT-15 | **FAIL** | 8 ideas, no I-XX numbering, not 34 entries |
| RT-16 | **PASS** | 4 real sub-targets: sync-types, sync-backend-models, sync-agent-types, sync-rag-models |
| RT-17 | **PASS** | api-types.generated.ts current (2026-02-08), validate-local confirms |
| RT-18 | **PASS** | Split-brain DB + scattered stage arrays acknowledged as systemic |
| RT-19 | **PASS** | All 14 columns verified against information_schema |
| RT-20 | **PASS** | Q1-Q10 formally answered in final-verification.md |

**Red-Team Result: 19/20 PASS, 1 FAIL (RT-15)**
