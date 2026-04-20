# Acceptance Criteria - DEAL LIFECYCLE V3 FULL REMEDIATION

## Definition of Done

The task is complete when ALL 22 issues are resolved and ALL 7 phases pass their gates.

---

## PHASE 0: Stop the Bleeding

### Requirements
- [ ] Dashboard calls `/api/quarantine/{id}/process` (not `/resolve`)
- [ ] Dashboard calls correct notes endpoint path
- [ ] Backend `/api/deals/{id}/notes` endpoint returns 201
- [ ] `/home/zaks/scripts/deal_state_machine.py` is DELETED
- [ ] No code references non-canonical stages
- [ ] DB default stage is `inbound`
- [ ] Dashboard generates `X-Correlation-ID` header
- [ ] Backend reads/stores correlation_id in deal_events
- [ ] Zod schemas include `.passthrough()`

### Verification
```bash
[ ! -f /home/zaks/scripts/deal_state_machine.py ] && echo "PASS"
rg -c "passthrough" apps/dashboard/src/lib/ | grep -q . && echo "PASS"
```

---

## PHASE 1: Data Truth Unification

### Requirements
- [ ] id_map table exists in Postgres
- [ ] Migration script exists at `scripts/migrations/migrate_json_to_postgres.py`
- [ ] CreateDealFromEmailExecutor uses backend API (no sys.path hack)
- [ ] Action engine uses Postgres `zakops.actions`
- [ ] CI guard blocks legacy writes

### Verification
```bash
rg "sys.path" zakops-backend/src/actions/executors/deal_create_from_email.py | wc -l  # Should be 0
psql -c "SELECT 1 FROM information_schema.tables WHERE table_name='id_map';"
```

---

## PHASE 2: Contract Alignment

### Requirements
- [ ] Quarantine approval creates deal atomically
- [ ] Deal creation scaffolds DataRoom folder
- [ ] `/api/actions/capabilities` returns 200
- [ ] `/api/actions/metrics` returns 200
- [ ] `/api/deals/{id}/archive` and `/restore` work
- [ ] OpenAPI spec synced

### Verification
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8091/api/actions/capabilities  # 200
```

---

## PHASE 3: Deal Lifecycle Correctness

### Requirements
- [ ] Agent has `create_deal` tool with HITL
- [ ] Agent has `add_note` tool
- [ ] All tool calls include X-Correlation-ID
- [ ] Duplicate deal creation returns 409
- [ ] Approval expiry background job exists
- [ ] Approvals mirrored to backend

### Verification
```bash
rg "create_deal" apps/agent-api/app/core/langgraph/tools/deal_tools.py | grep -q . && echo "PASS"
```

---

## PHASE 4: Deal Knowledge System

### Requirements
- [ ] Email ingestion Stage 4 POSTs to `/api/quarantine`
- [ ] Idempotency key table exists
- [ ] deal_append_email_materials executor wired
- [ ] deal_enrich_materials executor wired
- [ ] rag_reindex_deal executor wired
- [ ] deals table has last_indexed_at column
- [ ] SSE endpoint exists (or documented as polling)

### Verification
```bash
rg "POST.*quarantine" scripts/email_ingestion/stage_4_persist.py | grep -q . && echo "PASS"
```

---

## PHASE 5: Hardening

### Requirements
- [ ] Dashboard requires authentication
- [ ] User ID passed in backend requests
- [ ] deal_events has user attribution
- [ ] Retention policy documented at `/home/zaks/bookkeeping/docs/RETENTION_POLICY.md`
- [ ] Request tracing enabled

### Verification
```bash
[ -f /home/zaks/bookkeeping/docs/RETENTION_POLICY.md ] && echo "PASS"
```

---

## PHASE 6: Legacy Decommission

### Requirements
- [ ] deal_registry.json DELETED
- [ ] deal_registry.py DELETED
- [ ] deal_state_machine.py DELETED
- [ ] deal_lifecycle/ directory DELETED
- [ ] No legacy references in codebase
- [ ] CHANGES.md entry exists

### Verification
```bash
[ ! -f /home/zaks/DataRoom/.deal-registry/deal_registry.json ] && echo "PASS"
[ ! -f /home/zaks/scripts/deal_registry.py ] && echo "PASS"
[ ! -d /home/zaks/zakops-backend/src/api/deal_lifecycle ] && echo "PASS"
rg "LEGACY DECOMMISSION" /home/zaks/bookkeeping/CHANGES.md && echo "PASS"
```

---

## Quality Gates (All Phases)

- [ ] Backend tests pass (`pytest tests/`)
- [ ] Backend lint passes (`ruff check src/`)
- [ ] Dashboard lint passes (`pnpm lint`)
- [ ] No type errors

---

## Issue Resolution Matrix

ALL 22 issues must be marked resolved:

| Issue | Title | Phase | Resolved |
|-------|-------|-------|----------|
| ZK-ISSUE-0001 | Split-brain persistence | 1 | [ ] |
| ZK-ISSUE-0002 | Email ingestion disabled | 4 | [ ] |
| ZK-ISSUE-0003 | Quarantine no deal creation | 2 | [ ] |
| ZK-ISSUE-0004 | No DataRoom folders | 2 | [ ] |
| ZK-ISSUE-0005 | Dashboard no auth | 5 | [ ] |
| ZK-ISSUE-0006 | Wrong quarantine endpoint | 0 | [ ] |
| ZK-ISSUE-0007 | Stage taxonomy conflicts | 0 | [ ] |
| ZK-ISSUE-0008 | Actions split Postgres/SQLite | 1 | [ ] |
| ZK-ISSUE-0009 | Agent no create_deal | 3 | [ ] |
| ZK-ISSUE-0010 | RAG unverified | 0,4 | [ ] |
| ZK-ISSUE-0011 | No event correlation | 0 | [ ] |
| ZK-ISSUE-0012 | Notes endpoint mismatch | 0 | [ ] |
| ZK-ISSUE-0013 | Capabilities/metrics 501 | 2 | [ ] |
| ZK-ISSUE-0014 | sys.path hack | 1 | [ ] |
| ZK-ISSUE-0015 | Approval expiry lazy | 3 | [ ] |
| ZK-ISSUE-0016 | No duplicate detection | 3 | [ ] |
| ZK-ISSUE-0017 | No retention policy | 5 | [ ] |
| ZK-ISSUE-0018 | Zod schema mismatch | 0 | [ ] |
| ZK-ISSUE-0019 | Executors unwired | 4 | [ ] |
| ZK-ISSUE-0020 | SSE not implemented | 4 | [ ] |
| ZK-ISSUE-0021 | No scheduling/reminders | 4 | [ ] |
| ZK-ISSUE-0022 | Archive/restore missing | 2 | [ ] |

---

## Final Gate Command

```bash
./scripts/gate_full_remediation.sh
```

This gate must exit 0 for the task to PASS.
