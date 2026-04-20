# DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN_FINAL

## AGENT IDENTITY
- **agent_name**: Claude-Opus
- **run_id**: 20260204-1915-p3final
- **date_time**: 2026-02-04T19:15:00Z
- **repo_revision**: 2a68de172c7faf1df6f53357f4b43b0161d5dd32
- **synthesis_type**: PASS 3 (FINAL)

---

## Executive Summary

This document synthesizes three Round-2 contrarian plans (Opus, Codex, Gemini), PASS 1 coverage analysis, and PASS 2 red-team patch set into ONE execution-ready remediation plan.

**Key Statistics:**
- V2 Issues Total: 22 (2 P0, 6 P1, 11 P2, 3 P3)
- Issues Addressed by Round-2: 14 (64%)
- Issues Missing from Round-2: 8 (36%) - NOW ADDED
- Deduplicated Upgrades: 13
- Phases: 10 (R2-0 through R2-9)
- Builder Missions: 12

**Verdict**: Previous QA passes were "soft passes" that masked Layer 4-5 contract drift, silent failures, and missing V2 issues. This plan enforces hard gates.

---

## A) DECISION SET (MUST-DECIDE-NOW)

### Decision 1: Canonical Source of Truth (DB)

**DECISION**: PostgreSQL `zakops.deals` is the SOLE source of truth.

**Anti-Split-Brain Invariants**:
1. **SOT-INV-1**: All deal writes go through Postgres only; no legacy JSON/SQLite may be written in production.
2. **SOT-INV-2**: Legacy adapters (SQLite, JSON registry) must be removed or disabled by default.
3. **SOT-INV-3**: CI guard blocks any code introducing `deal_registry.json`, `ingest_state.db`, or sqlite patterns.

**Enforcement**:
- Remove/disable: `/home/zaks/zakops-backend/src/core/database/adapter.py` SQLite default
- Remove/disable: `/home/zaks/zakops-backend/src/actions/engine/store.py` SQLite action store
- Add CI forbidden-pattern gate for legacy patterns

### Decision 2: Contract Single Source of Truth

**DECISION**: OpenAPI is the authoritative contract. Generate all client types from it.

**Strategy**:
1. Backend Pydantic models define the API (already in place)
2. OpenAPI spec generated from Pydantic (via FastAPI)
3. TypeScript client + Zod schemas generated from OpenAPI using `openapi-typescript-codegen`
4. Manual Zod schemas (`api-schemas.ts`, `api-client.ts`) deleted
5. CI contract gate: any safeParse failure = build failure

**Enforcement**:
- Delete: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts` (manual schemas)
- Delete: manual schema definitions in `api-client.ts`
- Add: `npm run generate:client` in CI pipeline
- Add: contract test comparing backend responses to generated schemas

### Decision 3: Agent Tool Boundary Model

**DECISION**: Agent tools are audited, idempotent, and HITL-gated for destructive operations.

**Model**:
| Tool | Writes To | Idempotent | HITL Required |
|------|-----------|------------|---------------|
| get_deal | - (read) | N/A | No |
| search_deals | - (read) | N/A | No |
| transition_deal | zakops.deals | Yes (via idempotency_key) | No (reversible) |
| create_deal | zakops.deals | Yes (via idempotency_key) | Yes |
| add_note | zakops.deal_notes | Yes (via idempotency_key) | No |

**Audit Requirements**:
- All tool executions logged to `zakops_agent.audit_log` with `correlation_id`
- `correlation_id` propagated to backend and stored in `deal_events`

### Decision 4: HITL Persistence & Auditability

**DECISION**: Human-in-the-loop approvals are persisted in `zakops_agent.approvals` with full audit trail.

**Requirements**:
- `approvals` table with: id, action_id, user_id, status, created_at, expires_at, resolved_at, resolution_reason
- Background job expires stale approvals (TTL: 24 hours default)
- All approval state changes logged to audit_log

### Decision 5: Email Ingestion Architecture

**DECISION**: Email ingestion writes directly to PostgreSQL, not JSON registry.

**Architecture**:
1. Email sync job reads IMAP mailbox
2. Triage/enrichment produces quarantine items → `zakops.quarantine_items`
3. Approval creates deal → `zakops.deals` (atomic, same transaction)
4. Folder scaffolding triggered as side-effect (outbox pattern)
5. RAG indexing triggered as side-effect (outbox pattern)

**Idempotency**: `message_id` uniqueness on quarantine_items prevents duplicate ingestion.

### Decision 6: Observability Standard

**DECISION**: Correlation IDs end-to-end, with OpenTelemetry as stretch goal.

**Mandatory (R2)**:
- All client requests include `X-Correlation-ID` header
- Backend logs include `correlation_id` for every request
- `deal_events` table stores `correlation_id`
- Agent audit_log stores `correlation_id`

**Stretch (Post-R2)**:
- OpenTelemetry spans across browser → backend → agent → DB
- Trace visualization in Jaeger/Zipkin

### Decision 7: Knowledge/RAG Strategy

**DECISION**: RAG is advisory, not authoritative. Freshness is tracked but not guaranteed.

**Requirements**:
- Add `last_indexed_at` and `content_hash` columns to `zakops.deals`
- Circuit breaker on RAG calls with SQL fallback
- No deal creation/mutation based solely on RAG results

---

## B) PHASED IMPLEMENTATION PLAN

### Phase R2-0: Forensic Baseline (BLOCKING)

**Owner**: infra
**Objective**: Collect 5-layer truth + browser evidence before any changes.

**Atomic Tasks**:
1. Dump OpenAPI spec from running backend
2. Diff Pydantic models vs Zod schemas vs TS types
3. Open dashboard in browser, capture DevTools console (ZodErrors)
4. List DB columns for deals, actions, quarantine_items
5. Verify 8090 references in codebase
6. Confirm env vars in docker-compose

**Dependencies**: Services running

**Risks**: None (read-only)

**Gates**:
- [ ] Evidence pack contains OpenAPI dump
- [ ] Evidence pack contains Pydantic vs Zod diff report
- [ ] Evidence pack contains browser console capture
- [ ] Evidence pack contains DB schema dump

**Evidence Required**:
- `evidence/r2-0-openapi.json`
- `evidence/r2-0-schema-diff.md`
- `evidence/r2-0-browser-console.log`
- `evidence/r2-0-db-schema.sql`

**Acceptance Criteria**:
- All 5 evidence files exist and are non-empty
- Schema diff report identifies all mismatches between Pydantic/Zod/TS
- Legacy pattern references catalogued for removal in R2-9

---

### Phase R2-1: Contract Alignment + ZodError Eradication (P0)

**Owner**: frontend
**Objective**: Zero ZodErrors in browser; single source of truth for schemas.

**Atomic Tasks**:
1. Generate TypeScript client from OpenAPI (`openapi-typescript-codegen`)
2. Generate Zod schemas from OpenAPI
3. Delete manual schemas in `api-client.ts` and `api-schemas.ts`
4. Fix ActionStatus enum: align RUNNING/PROCESSING (use PROCESSING)
5. Fix ActionSource enum: add `agent`, `api` to backend
6. Trim ActionSchema phantom fields (or expand ActionResponse)
7. Trim QuarantineItemSchema phantom fields
8. Replace silent `return []` with user-visible error handling
9. Remove `.passthrough()` from all Zod schemas after alignment

**Dependencies**: R2-0 complete

**Risks**:
- Schema changes may break existing UI components
- **Rollback**: Revert to previous client with pinned commit

**Gates**:
- [ ] `npm run generate:client` succeeds
- [ ] Browser console shows zero ZodErrors
- [ ] All safeParse calls have error handling (no silent `[]`)
- [ ] ActionStatus displays correctly for PROCESSING actions

**Evidence Required**:
- Browser console screenshot (zero errors)
- Generated client diff
- Test: create PROCESSING action, verify UI shows correct status

**Acceptance Criteria**:
- `npm run generate:client` succeeds without manual intervention
- Browser DevTools console shows zero ZodErrors on all pages
- ActionStatus displays correctly for all enum values

---

### Phase R2-2: Idempotency Layer (P0)

**Owner**: backend
**Objective**: No 500s on duplicate writes; all writes idempotent.

**Atomic Tasks**:
1. Create `idempotency_keys` table (key, response_body, status_code, expires_at)
2. Add `IdempotencyMiddleware` to backend
3. Update Dashboard `apiFetch` to inject `Idempotency-Key` header (UUID v4) on POST/PUT/PATCH
4. Update agent tools to include idempotency keys
5. Return cached response on duplicate (200), not 500 or new creation

**Dependencies**: R2-0 complete

**Risks**:
- Middleware ordering issues
- **Rollback**: Disable middleware, return 409 with structured error

**Gates**:
- [ ] Duplicate POST returns 200 with identical response
- [ ] No 500 errors on duplicate creates
- [ ] Agent double-submit creates one deal

**Evidence Required**:
- curl output: two identical POSTs, both return 200
- DB query: only one deal row

**Acceptance Criteria**:
- Duplicate POST with same Idempotency-Key returns 200 with cached response
- No 500 errors observed on duplicate submissions
- Agent tool double-submit creates exactly one resource

---

### Phase R2-3: V2 Coverage Closure (P1)

**Owner**: backend, frontend
**Objective**: Close all 8 V2 issues missing from Round-2 plans.

**Atomic Tasks**:

**ZK-ISSUE-0003 (Quarantine approval no deal)**:
1. Wire `POST /api/quarantine/{id}/process?action=approve` to create deal atomically
2. Link quarantine_item.deal_id to new deal
3. Test: approve quarantine → deal exists in DB

**ZK-ISSUE-0004 (No DataRoom folders)**:
1. Add post-create hook to scaffold folder structure
2. Use outbox pattern: write to outbox, worker creates folders
3. Test: create deal → folder exists in DataRoom

**ZK-ISSUE-0006 (Wrong quarantine endpoint)**:
1. Update Dashboard to call `/api/quarantine/{id}/process` (not `/resolve`)
2. Test: quarantine approval from UI succeeds

**ZK-ISSUE-0012 (Deal notes endpoint)**:
1. Add `POST /api/deals/{id}/notes` to orchestration API
2. Update Dashboard to use correct endpoint
3. Test: add note from UI, note visible in DB

**ZK-ISSUE-0015 (Approval expiry job)**:
1. Add background job to expire stale approvals
2. Run every 5 minutes, expire approvals past TTL
3. Emit `APPROVAL_EXPIRED` event

**ZK-ISSUE-0017 (Retention policy)**:
1. Document retention policy (e.g., archive after 90 days in junk)
2. Add cleanup job placeholder (manual trigger initially)

**ZK-ISSUE-0019 (Executors unwired)**:
1. Wire top 5 executors to UI actions
2. Add progress tracking for long-running executors

**ZK-ISSUE-0021 (Scheduling/reminders)**:
1. Add deal age tracking (created_at already exists)
2. Add "stale deal" query endpoint
3. Implement reminders as stretch goal

**ZK-ISSUE-0022 (Archive/restore)**:
1. Add `POST /api/deals/{id}/archive` and `POST /api/deals/{id}/restore`
2. Use `deleted` flag in DB
3. Test: archive deal, verify hidden; restore, verify visible

**Dependencies**: R2-1 (schema alignment)

**Risks**:
- Large scope; prioritize P1 issues first
- **Rollback**: Revert individual features; document as deferred

**Gates**:
- [ ] Each V2 issue has passing test
- [ ] All P1 issues closed (0003, 0004, 0006)
- [ ] P2/P3 issues either closed or explicitly deferred with rationale

**Evidence Required**:
- Test logs for each issue
- DB queries showing expected state

**Acceptance Criteria**:
- All 8 missing V2 issues have passing regression tests
- Quarantine approval atomically creates deal (ZK-ISSUE-0003)
- Dashboard uses correct /process endpoint (ZK-ISSUE-0006)

---

### Phase R2-4: Transactional Outbox (P1)

**Owner**: backend
**Objective**: Reliable side-effects; no fire-and-forget.

**Atomic Tasks**:
1. Create `outbox` table (id, aggregate_id, event_type, payload, created_at, processed_at)
2. Modify deal mutations to write events to outbox in same transaction
3. Implement outbox relay worker
4. Side-effects: folder scaffolding, RAG indexing, notifications

**Dependencies**: R2-2 (idempotency for dedup)

**Risks**:
- Outbox backlog if worker fails
- **Rollback**: Revert to synchronous side effects with explicit error handling

**Gates**:
- [ ] Outbox processed within 5 seconds
- [ ] No dropped events under chaos test (worker restart)
- [ ] Health endpoint shows outbox status

**Evidence Required**:
- Outbox processing logs
- Chaos test: stop worker, queue events, restart, verify processed

**Acceptance Criteria**:
- All side-effects written to outbox table atomically with main operation
- Outbox relay worker processes events within 5 seconds
- No events lost during worker restart (chaos test passes)

---

### Phase R2-5: Deal Transition Ledger (P1)

**Owner**: backend
**Objective**: Auditable, deterministic lifecycle transitions.

**Atomic Tasks**:
1. Create `deal_transitions` table (id, deal_id, from_stage, to_stage, actor_id, correlation_id, created_at)
2. Modify transition_deal to write ledger entry atomically
3. Return 422 on invalid transition
4. Add UI timeline showing transition history

**Dependencies**: R2-4 (outbox for side-effects)

**Risks**:
- Performance impact on high-volume transitions
- **Rollback**: Disable ledger writes; use logs for audit

**Gates**:
- [ ] Invalid transition returns 422 with reason
- [ ] Ledger row exists for every transition
- [ ] UI timeline displays transitions

**Evidence Required**:
- curl: invalid transition returns 422
- DB query: ledger rows for test deal
- Screenshot: UI timeline

**Acceptance Criteria**:
- Every stage transition creates a ledger entry in deal_transitions
- Invalid transitions return 422 with descriptive error message
- UI timeline component displays transition history

---

### Phase R2-6: Observability Hardening (P2)

**Owner**: infra, backend
**Objective**: Correlation IDs end-to-end; structured logs.

**Atomic Tasks**:
1. Unify Dashboard fetch wrapper to inject `X-Correlation-ID`
2. Ensure backend logs include `correlation_id`
3. Store `correlation_id` in `deal_events`
4. Add RAG circuit breaker with SQL fallback
5. (Stretch) Add OpenTelemetry spans

**Dependencies**: R2-1 (unified client)

**Risks**:
- Overhead from tracing
- **Rollback**: Disable OTel; keep correlation IDs

**Gates**:
- [ ] correlation_id present in logs for every request
- [ ] correlation_id present in deal_events
- [ ] RAG circuit breaker triggers graceful fallback on outage

**Evidence Required**:
- Log sample with correlation_id
- DB query showing correlation_id in deal_events
- Test: stop RAG, verify fallback behavior

**Acceptance Criteria**:
- All API requests include X-Correlation-ID in logs
- deal_events table contains correlation_id for every entry
- RAG circuit breaker triggers SQL fallback on service outage

---

### Phase R2-7: Contract Testing CI Gate (P2)

**Owner**: infra
**Objective**: Prevent schema drift permanently.

**Atomic Tasks**:
1. Add `npm run contract:test` script
2. Test fetches from running backend, validates against generated schemas
3. Add to CI pipeline (PR gate)
4. Add forbidden-pattern gate for legacy patterns (8090, sqlite, json registry)

**Dependencies**: R2-1 (generated client)

**Risks**:
- CI flakiness if backend not available
- **Rollback**: Make gate advisory (warn, not fail)

**Gates**:
- [ ] CI fails on schema mismatch
- [ ] CI fails on forbidden patterns
- [ ] Successful run produces contract report

**Evidence Required**:
- CI log showing contract test pass
- CI log showing forbidden-pattern check pass

**Acceptance Criteria**:
- CI pipeline fails on any schema mismatch between OpenAPI and generated client
- CI pipeline fails on forbidden patterns (8090, sqlite, json registry)
- Contract test report generated on every PR

---

### Phase R2-8: Agent Evaluation Framework (P2)

**Owner**: agent
**Objective**: Prevent regressions in agent tool selection.

**Atomic Tasks**:
1. Create golden eval dataset (20 scenarios)
2. Each scenario: user message → expected tool calls → expected outcome
3. Add `npm run eval:agent` script
4. Integrate with CI (advisory gate)

**Dependencies**: R2-3 (tools wired)

**Risks**:
- Eval dataset maintenance burden
- **Rollback**: Keep as manual test

**Gates**:
- [ ] >= 18/20 scenarios pass
- [ ] No regression on core flows (deal CRUD, transitions)

**Evidence Required**:
- Eval report showing pass/fail per scenario

**Acceptance Criteria**:
- Eval dataset contains 20+ scenarios covering all agent tools
- At least 18/20 scenarios pass (90% threshold)
- No regression on core flows (deal CRUD, stage transitions)

---

### Phase R2-9: Regression Proofing + Safe Decommissioning (P2)

**Owner**: infra, backend
**Objective**: Permanent protection for all 22 V2 issues.

**Atomic Tasks**:
1. Add regression test for each V2 issue
2. Confirm CI fails if any fix is reverted
3. Remove legacy 8090 references from Makefile/docs
4. Add CI guard for legacy patterns
5. Document decommissioned components in CHANGELOG

**Dependencies**: R2-7 (CI gates)

**Risks**:
- Test maintenance burden
- **Rollback**: Keep tests but make advisory

**Gates**:
- [ ] Revert any fix → CI fails
- [ ] rg for legacy patterns returns empty
- [ ] CHANGELOG documents decommissioned components

**Evidence Required**:
- CI log showing regression test failure on revert
- rg output for legacy patterns (empty)

**Acceptance Criteria**:
- All 22 V2 issues have corresponding regression tests
- Reverting any fix causes CI to fail
- rg for legacy patterns (8090, sqlite, json registry) returns empty

---

## C) NO-DROP COVERAGE MATRIX (ABSOLUTE)

**CRITICAL**: Every V2 issue MUST be mapped to a phase, tasks, verification, DoD, and Owner.

| Issue ID | Severity | Title | Phase | Owner | Tasks | Verification | DoD |
|----------|----------|-------|-------|-------|-------|--------------|-----|
| ZK-ISSUE-0001 | P0 | Split-brain persistence | R2-9 | backend | Remove SQLite/JSON adapters; add CI guard | rg returns empty for legacy patterns | Legacy code paths disabled |
| ZK-ISSUE-0002 | P0 | Email ingestion disabled | R2-3 | backend | Enable cron job; verify IMAP credentials | Quarantine items created | Cron active; emails processing |
| ZK-ISSUE-0003 | P1 | Quarantine approval no deal | R2-3 | backend | Wire approve→create atomically | Approve → deal in DB | Atomic flow works |
| ZK-ISSUE-0004 | P1 | No DataRoom folders | R2-3 | backend | Post-create hook via outbox | Create → folder exists | Folder scaffold works |
| ZK-ISSUE-0005 | P1 | No authentication | R2-6 | security | Unify fetch wrapper; add auth middleware | Auth headers present | Auth enforced |
| ZK-ISSUE-0006 | P1 | Wrong quarantine endpoint | R2-3 | frontend | Update Dashboard to use /process | UI approval works | No 404s |
| ZK-ISSUE-0007 | P1 | Stage taxonomy conflicts | R2-1 | backend | Align enums; set DB default inbound | DB default = inbound | Single taxonomy |
| ZK-ISSUE-0008 | P1 | Actions split Postgres/SQLite | R2-9 | backend | Remove SQLite action store | Actions in Postgres only | No SQLite |
| ZK-ISSUE-0009 | P2 | Agent cannot create deals | R2-3 | agent | Add create_deal tool with HITL | Agent creates deal | Tool works |
| ZK-ISSUE-0010 | P2 | RAG search unverified | R2-6 | backend | Add circuit breaker; verify RAG health | Fallback on outage | Graceful degradation |
| ZK-ISSUE-0011 | P2 | No event correlation | R2-6 | infra | Propagate correlation IDs | IDs in logs + DB | End-to-end trace |
| ZK-ISSUE-0012 | P2 | Deal notes endpoint mismatch | R2-3 | backend | Add /api/deals/{id}/notes | Add note works | Endpoint exists |
| ZK-ISSUE-0013 | P2 | Capabilities/metrics 501 | R2-1 | backend | Consolidate routes; return 200 | Endpoints return data | No 501s |
| ZK-ISSUE-0014 | P2 | sys.path hack | R2-9 | backend | Use proper imports | No sys.path in code | Clean imports |
| ZK-ISSUE-0015 | P3 | No approval expiry job | R2-3 | backend | Add background expiry job | Stale approvals expired | Job running |
| ZK-ISSUE-0016 | P2 | No duplicate detection | R2-2 | backend | Idempotency-Key on writes | Duplicate returns 200 | No duplicates |
| ZK-ISSUE-0017 | P3 | No retention policy | R2-3 | data | Document policy; add cleanup job | Policy documented | Policy exists |
| ZK-ISSUE-0018 | P2 | Zod schema mismatch | R2-1 | frontend | Generate schemas; align all | Zero ZodErrors | Schemas match |
| ZK-ISSUE-0019 | P2 | Executors unwired | R2-3 | backend | Wire top 5 executors | Executors callable | Actions work |
| ZK-ISSUE-0020 | P2 | SSE not implemented | R2-1 | backend | Implement SSE or document polling | SSE works or polling documented | Real-time updates |
| ZK-ISSUE-0021 | P2 | No scheduling/reminders | R2-3 | backend | Add stale deal query; reminders deferred | Stale query works | Query implemented |
| ZK-ISSUE-0022 | P3 | Archive/restore missing | R2-3 | backend | Add /archive and /restore endpoints | Archive/restore works | Endpoints exist |

**Coverage Verification**: 22/22 issues mapped (100%)

---

## D) CONTRARIAN UPGRADE REGISTER (DEDUPED)

| ID | Title | Proposed By | Priority | Phase | Verification |
|----|-------|-------------|----------|-------|--------------|
| UPG-001 | Generated TypeScript Client from OpenAPI | Opus, Codex, Gemini | P0 | R2-1 | Contract CI gate fails on mismatch |
| UPG-002 | Idempotency-Key on All Write Endpoints | Codex, Gemini | P0 | R2-2 | Duplicate POST returns same response |
| UPG-003 | Transactional Outbox for Side-Effects | Codex, Gemini | P1 | R2-4 | Chaos test; outbox processed in <=5s |
| UPG-004 | Contract Testing CI Gate | Opus, Codex, Gemini | P2 | R2-7 | CI fails on schema mismatch |
| UPG-005 | RAG Circuit Breaker | Codex, Gemini | P2 | R2-6 | Graceful fallback on RAG outage |
| UPG-006 | ActionStatus Enum Alignment | Opus | P0 | R2-1 | Actions list displays correct status |
| UPG-007 | Trim ActionSchema Phantom Fields | Opus | P1 | R2-1 | ActionSchema matches ActionResponse |
| UPG-008 | Replace Silent Failures with User Errors | Opus, Gemini | P1 | R2-1 | Schema mismatch shows user-visible error |
| UPG-009 | Deal Transition Ledger | Codex | P1 | R2-5 | Invalid transition returns 422; ledger row exists |
| UPG-010 | OpenTelemetry Integration | Codex | P2 | R2-6 | Trace visible in Jaeger/Zipkin |
| UPG-011 | Safe Decommissioning Guardrails | Codex | P1 | R2-9 | rg gate fails on legacy patterns |
| UPG-012 | Schema Migration Safety | Codex | P2 | R2-9 | Migration rollback succeeds in CI |
| UPG-013 | Agent Evaluation Framework | Codex | P2 | R2-8 | >=18/20 scenarios pass |

---

## E) BUILDER MISSION SEQUENCE

### Mission 1: R2-0 Forensic Baseline

```
MISSION: R2-0 Forensic Baseline
REPO: /home/zaks/zakops-backend, /home/zaks/zakops-agent-api
SCOPE: Read-only evidence collection

TASKS:
1. curl http://localhost:8091/openapi.json > evidence/r2-0-openapi.json
2. Create schema diff report comparing Pydantic vs Zod
3. Open Dashboard, capture browser console, save to evidence/r2-0-browser-console.log
4. psql dump: \d zakops.deals, \d zakops.actions, \d zakops.quarantine_items
5. rg -l "8090|deal_registry.json|ingest_state.db" > evidence/r2-0-legacy-refs.txt

GATE:
- All evidence files exist and are non-empty
- rg output catalogued (not necessarily empty yet)

ACCEPTANCE: Evidence pack complete
BLOCKER POLICY: If service not running, document and continue
NEXT MISSION: R2-1 Contract Alignment
```

### Mission 2: R2-1 Contract Alignment

```
MISSION: R2-1 Contract Alignment + ZodError Eradication
REPO: /home/zaks/zakops-agent-api
SCOPE: apps/dashboard/src/lib/, apps/dashboard/src/types/

TASKS:
1. Install openapi-typescript-codegen
2. npm run generate:client (create script if needed)
3. Delete manual schemas in api-client.ts, api-schemas.ts
4. Align ActionStatus enum (use PROCESSING in Zod)
5. Add agent, api to ActionSource in backend
6. Remove .passthrough() from generated schemas
7. Replace return [] with error handling in api.ts

GATE:
- npm run build succeeds
- Browser console shows zero ZodErrors
- npm run contract:test passes (create if needed)

ACCEPTANCE: Zero ZodErrors; generated client in use
BLOCKER POLICY: If OpenAPI missing, generate from running backend first
NEXT MISSION: R2-2 Idempotency
```

### Mission 3: R2-2 Idempotency Layer

```
MISSION: R2-2 Idempotency Layer
REPO: /home/zaks/zakops-backend
SCOPE: src/api/, db/migrations/

TASKS:
1. Create migration: idempotency_keys table
2. Add IdempotencyMiddleware to FastAPI app
3. Update create_deal, add_note to check idempotency
4. Return cached response on duplicate key

GATE:
- Duplicate POST with same Idempotency-Key returns 200
- No 500 errors on duplicates
- Tests pass

ACCEPTANCE: Idempotency enforced on all write endpoints
BLOCKER POLICY: If DB migration fails, check migration order
NEXT MISSION: R2-3a V2 Coverage (Quarantine)
```

### Mission 4: R2-3a Quarantine-to-Deal Flow

```
MISSION: R2-3a V2 Coverage - Quarantine-to-Deal
REPO: /home/zaks/zakops-backend
SCOPE: src/api/orchestration/

TASKS:
1. Modify POST /api/quarantine/{id}/process to create deal on approve
2. Set quarantine_item.deal_id atomically
3. Add folder scaffold as outbox event

GATE:
- Approve quarantine → deal exists in zakops.deals
- quarantine_item.deal_id populated
- Folder scaffold event in outbox

ACCEPTANCE: ZK-ISSUE-0003, ZK-ISSUE-0004 closed
BLOCKER POLICY: If outbox not ready, use synchronous call
NEXT MISSION: R2-3b V2 Coverage (Endpoints)
```

### Mission 5: R2-3b Missing Endpoints

```
MISSION: R2-3b V2 Coverage - Missing Endpoints
REPO: /home/zaks/zakops-backend, /home/zaks/zakops-agent-api
SCOPE: src/api/, apps/dashboard/

TASKS:
1. Add POST /api/deals/{id}/notes endpoint
2. Add POST /api/deals/{id}/archive endpoint
3. Add POST /api/deals/{id}/restore endpoint
4. Update Dashboard to use /process (not /resolve)
5. Wire top 5 executors to UI actions

GATE:
- All new endpoints return 200
- Dashboard quarantine approval works
- Notes can be added from UI

ACCEPTANCE: ZK-ISSUE-0006, ZK-ISSUE-0012, ZK-ISSUE-0019, ZK-ISSUE-0022 closed
BLOCKER POLICY: If executor wiring complex, defer to R2-3c
NEXT MISSION: R2-3c V2 Coverage (Jobs)
```

### Mission 6: R2-3c Background Jobs

```
MISSION: R2-3c V2 Coverage - Background Jobs
REPO: /home/zaks/zakops-backend, /home/zaks/zakops-agent-api
SCOPE: src/jobs/, apps/agent-api/

TASKS:
1. Add approval expiry job (5 min interval)
2. Add stale deal query endpoint
3. Document retention policy in POLICY.md
4. Enable email ingestion cron (verify credentials first)

GATE:
- Expiry job running in dev
- Stale deal query returns expected results
- Policy documented

ACCEPTANCE: ZK-ISSUE-0002, ZK-ISSUE-0015, ZK-ISSUE-0017, ZK-ISSUE-0021 closed
BLOCKER POLICY: If email credentials missing, document and defer
NEXT MISSION: R2-4 Outbox
```

### Mission 7: R2-4 Transactional Outbox

```
MISSION: R2-4 Transactional Outbox
REPO: /home/zaks/zakops-backend
SCOPE: src/core/, db/migrations/

TASKS:
1. Create migration: outbox table
2. Modify deal mutations to write outbox events
3. Implement outbox relay worker
4. Add health endpoint for outbox status

GATE:
- Outbox events created on deal mutations
- Worker processes events within 5s
- Health endpoint shows outbox backlog

ACCEPTANCE: Side-effects via outbox only
BLOCKER POLICY: If worker complex, start with simple polling
NEXT MISSION: R2-5 Transition Ledger
```

### Mission 8: R2-5 Deal Transition Ledger

```
MISSION: R2-5 Deal Transition Ledger
REPO: /home/zaks/zakops-backend
SCOPE: src/core/deals/, db/migrations/

TASKS:
1. Create migration: deal_transitions table
2. Modify transition_deal to write ledger entry
3. Return 422 on invalid transition
4. Add GET /api/deals/{id}/transitions endpoint

GATE:
- Ledger row created on every transition
- Invalid transition returns 422
- Transitions endpoint returns history

ACCEPTANCE: UPG-009 complete
BLOCKER POLICY: If performance concerns, add async ledger write
NEXT MISSION: R2-6 Observability
```

### Mission 9: R2-6 Observability Hardening

```
MISSION: R2-6 Observability Hardening
REPO: /home/zaks/zakops-agent-api, /home/zaks/zakops-backend
SCOPE: apps/dashboard/src/lib/, src/api/

TASKS:
1. Unify Dashboard fetch wrapper with correlation ID
2. Ensure backend logs include correlation_id
3. Add correlation_id column to deal_events
4. Add RAG circuit breaker with SQL fallback

GATE:
- correlation_id in all request logs
- correlation_id in deal_events
- RAG outage triggers fallback

ACCEPTANCE: ZK-ISSUE-0005, ZK-ISSUE-0010, ZK-ISSUE-0011 closed
BLOCKER POLICY: If OTel complex, defer to post-R2
NEXT MISSION: R2-7 CI Gates
```

### Mission 10: R2-7 Contract Testing CI Gate

```
MISSION: R2-7 Contract Testing CI Gate
REPO: /home/zaks/zakops-agent-api
SCOPE: tests/, .github/workflows/

TASKS:
1. Create tests/contracts/verify_schemas.ts
2. Add npm run contract:test script
3. Add to CI workflow (PR gate)
4. Add forbidden-pattern check for legacy patterns

GATE:
- CI fails on schema mismatch
- CI fails on forbidden patterns (8090, sqlite, json registry)
- Successful run produces report

ACCEPTANCE: UPG-004, UPG-011 complete
BLOCKER POLICY: If CI infra limited, document manual checks
NEXT MISSION: R2-8 Agent Eval
```

### Mission 11: R2-8 Agent Evaluation Framework

```
MISSION: R2-8 Agent Evaluation Framework
REPO: /home/zaks/zakops-agent-api
SCOPE: tests/eval/, apps/agent-api/

TASKS:
1. Create eval dataset (20 scenarios)
2. Implement eval runner
3. Add npm run eval:agent script
4. Document expected tool calls per scenario

GATE:
- >= 18/20 scenarios pass
- No regression on core flows
- Eval report generated

ACCEPTANCE: UPG-013 complete
BLOCKER POLICY: If eval infra complex, start with 10 scenarios
NEXT MISSION: R2-9 Regression Proofing
```

### Mission 12: R2-9 Regression Proofing

```
MISSION: R2-9 Regression Proofing
REPO: /home/zaks/zakops-backend, /home/zaks/zakops-agent-api
SCOPE: tests/, db/, src/

TASKS:
1. Add regression test for each V2 issue
2. Remove legacy 8090 references
3. Remove sys.path hacks
4. Remove/disable SQLite/JSON adapters
5. Update CHANGELOG with decommissioned components

GATE:
- Revert any fix → CI fails
- rg for legacy patterns returns empty
- All 22 V2 issues have regression tests

ACCEPTANCE: ZK-ISSUE-0001, ZK-ISSUE-0008, ZK-ISSUE-0014 closed; UPG-011, UPG-012 complete
BLOCKER POLICY: If removal risky, add feature flag first
NEXT MISSION: Final QA
```

---

## F) FINAL QA PLAN

### QA Pass 1: Functional Verification

| Test ID | Scenario | Expected Outcome | Evidence |
|---------|----------|------------------|----------|
| QA-F-01 | Create deal via API | Deal in DB, folder created | curl + ls |
| QA-F-02 | Create deal via Dashboard | Deal in DB, folder created | Screenshot + DB query |
| QA-F-03 | Approve quarantine | Deal created atomically | DB query |
| QA-F-04 | Transition deal (valid) | Stage changed, ledger entry | DB query |
| QA-F-05 | Transition deal (invalid) | 422 returned | curl output |
| QA-F-06 | Add deal note | Note in DB | DB query |
| QA-F-07 | Archive deal | deleted=true | DB query |
| QA-F-08 | Restore deal | deleted=false | DB query |
| QA-F-09 | Search deals (RAG up) | Results returned | API response |
| QA-F-10 | Agent get_deal | Correct deal returned | Tool output |
| QA-F-11 | Agent transition_deal | Stage changed | DB query |
| QA-F-12 | SSE connection | Events received | Browser Network tab |
| QA-F-13 | Browser console | Zero ZodErrors | Console screenshot |
| QA-F-14 | Correlation ID propagation | ID in logs + DB | Log + DB query |

### QA Pass 2: Adversarial Verification

| Test ID | Scenario | Expected Outcome | Evidence |
|---------|----------|------------------|----------|
| QA-A-01 | Duplicate POST (same idempotency key) | 200, same response | curl output |
| QA-A-02 | Duplicate POST (no idempotency key) | 409 or 200 (idempotent) | curl output |
| QA-A-03 | RAG service down | Graceful fallback | Error response |
| QA-A-04 | Backend down (Dashboard) | Error message, no crash | Screenshot |
| QA-A-05 | Invalid stage transition | 422 with reason | curl output |
| QA-A-06 | Outbox worker down | Events queued, processed on restart | DB + logs |
| QA-A-07 | Schema mismatch (simulated) | User-visible error, not empty | Screenshot |
| QA-A-08 | Expired approval access | 410 Gone or equivalent | API response |
| QA-A-09 | Legacy pattern injection | CI blocks | CI log |
| QA-A-10 | Concurrent stage transitions | One succeeds, one 409 | curl output |

### Proof Artifacts Required

1. **Evidence Pack** (R2-0): OpenAPI dump, schema diff, browser console, DB schema
2. **Contract Test Report** (R2-7): CI output showing pass
3. **Browser Console Capture** (R2-1): Screenshot showing zero errors
4. **Idempotency Test** (R2-2): curl output showing duplicate handling
5. **Correlation ID Trace** (R2-6): Log sample + DB query
6. **Regression Test Suite** (R2-9): CI output showing all pass
7. **Eval Report** (R2-8): Scenario pass/fail summary

### SHIP IT Definition

The system is ready to ship when ALL of the following are true:

- [ ] All 22 V2 issues have PASS status in regression tests
- [ ] QA Pass 1: 14/14 functional tests pass
- [ ] QA Pass 2: 10/10 adversarial tests pass
- [ ] Browser console shows zero ZodErrors
- [ ] Contract CI gate passes
- [ ] Forbidden pattern gate passes (no legacy patterns)
- [ ] All evidence artifacts collected and reviewed
- [ ] CHANGELOG updated with all changes

---

## Appendix: Plan Quality Sources

### Input Plans Analyzed

| Agent | Run ID | Score | Key Contributions |
|-------|--------|-------|-------------------|
| Opus | opus.run001 | 21/30 | Layer 4-5 deep-dive; ActionStatus/Zod drift discovery |
| Codex | 20260204-1651-0e51 | 28/30 | Full 10-layer coverage; R2-0 through R2-9 phasing |
| Gemini | 20260204-1050-gemini | 21/30 | Dual DealSchema "smoking gun"; idempotency emphasis |

### PASS 1 Key Findings (20260204-1835-p1r2)

- 14/22 V2 issues covered (64%)
- 8 issues missing: 0003, 0004, 0006, 0012, 0015, 0017, 0019, 0021, 0022
- 13 deduplicated upgrades

### PASS 2 Key Findings (20260204-1728-102efc)

- 25 failure modes identified
- Split-brain reintroduction audit
- Contract drift audit
- Patch set for missing items

---

*Generated by PASS 3 (FINAL) Synthesis*
*Agent: Claude-Opus*
*Run ID: 20260204-1915-p3final*
*Timestamp: 2026-02-04T19:15:00Z*
