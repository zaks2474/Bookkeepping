AGENT IDENTITY
- agent_name: Codex
- run_id: 20260204-021313-1158
- date_time: 2026-02-04T02:13:16Z
- repo_revision: a09538f04ed278c32ad6f2a037069b353bf5f797

## Executive Summary
- What is broken (top P0/P1): split-brain persistence (ZK-ISSUE-0001), email ingestion disabled (ZK-ISSUE-0002), quarantine approval does not create deals (ZK-ISSUE-0003), dashboard has no auth (ZK-ISSUE-0005), wrong UI endpoints (ZK-ISSUE-0006, ZK-ISSUE-0012), stage taxonomy conflicts (ZK-ISSUE-0007), actions split across DBs (ZK-ISSUE-0008).
- Shortest path to stability: secure dashboard access, establish correlation IDs, unify deal/action truth in Postgres, fix UI/agent contract mismatches, then re-enable ingestion and knowledge workflows on the canonical data path.
- Decisions that must be made first: canonical data store, canonical stages, agent contract boundaries, email ingestion architecture, RAG/embeddings design, HITL persistence, and auth model.

## Decision Set (must be decided BEFORE remediation)
### Source-of-truth DB model (eliminate split-brain)
Options:
- A) Single canonical Postgres (zakops.deals + related tables)
  Pros: Eliminates split-brain, Single audit trail, Simpler ops/backup
  Cons: Migration effort, Need clear schema for DataRoom + embeddings refs
- B) Multiple stores with sync (event sourcing)
  Pros: Specialized stores, Decoupled services
  Cons: Complexity, Consistency risk remains, Harder to prove truth
- C) Keep current split
  Pros: No immediate refactor
  Cons: Violates end-state, Ongoing data loss and inconsistency
Recommendation: Choose A. Make Postgres the single source of truth for deal state; other stores are derived/indexed only.
Migration approach:
1. Add explicit columns for dataroom_path, external_ids, and canonical deal_id mapping in Postgres.
2. One-time migration: ingest deal_registry.json into Postgres with deterministic ID mapping.
3. Refactor all writers (email ingestion, executors, agent tools) to use Postgres APIs.
4. Deprecate and remove JSON registry + SQLite action store after parity tests pass.
Verification proof:
- Create deal via API, email ingestion, and agent tool; verify single Postgres row and consistent deal_id.
- Ripgrep shows no writes to deal_registry.json or SQLite action store.
- Dashboards, agents, and backend all read from Postgres only.

### Deal taxonomy + stage model (canonical stages and transitions)
Options:
- A) Canonical stages from workflow.py with explicit transition rules
  Pros: Matches active backend, Deterministic lifecycle, Easy to validate
  Cons: Requires migration of legacy labels
- B) Use legacy deal_state_machine stages
  Pros: Matches some legacy scripts
  Cons: Not aligned with current backend, Rework DB constraints
- C) Per-pipeline custom stages
  Pros: Flexibility
  Cons: Higher complexity, Harder to enforce invariants
Recommendation: Choose A. Align DB constraints and defaults to canonical stages and provide mapping for legacy labels.
Migration approach:
1. Update DB default stage from 'lead' to 'inbound'.
2. Add migration script to map legacy stages into canonical stages.
3. Remove/retire legacy deal_state_machine.py or mark as archived.
Verification proof:
- DB constraint matches canonical list; no rows with non-canonical stage.
- Transition endpoint rejects invalid transitions with 409.
- UI and agent use the same canonical stage list.

### Agent tool contract boundaries
Options:
- A) Agent uses backend APIs only (no direct DB writes)
  Pros: Single source of truth, Centralized auth + validation, Auditable
  Cons: Requires robust APIs and auth
- B) Agent writes to DB directly
  Pros: Lower latency
  Cons: Bypasses validation, Harder to audit, Breaks separation
- C) Agent owns separate store and syncs
  Pros: Isolation
  Cons: Split-brain risk
Recommendation: Choose A. Agent tools must call backend APIs and include correlation_id + HITL as required.
Migration approach:
1. Add create_deal tool that calls backend /api/deals with HITL approval.
2. Ensure all existing tools include correlation_id headers and actor info.
3. Block direct DB writes from agent service.
Verification proof:
- Agent tool calls produce backend audit events with correlation_id.
- No agent code references DB credentials or direct connections.

### Email ingestion architecture
Options:
- A) Event-driven ingestion (IMAP/SMTP -> queue -> triage -> quarantine -> deal update)
  Pros: Scalable, Idempotent, Near real-time
  Cons: Infrastructure complexity
- B) Cron-based polling (current pattern)
  Pros: Simple to deploy
  Cons: Batch delays, Operational drift
- C) Manual upload only
  Pros: No infrastructure
  Cons: Breaks end-state
Recommendation: Implement B immediately as a bridge, then evolve to A once canonical data path is stable.
Migration approach:
1. Point ingestion output to Postgres quarantine + deal tables.
2. Add idempotency on message_id and body_hash.
3. Attach emails and extracted artifacts to deal record; store files in DataRoom.
Verification proof:
- Synthetic email appears as quarantine item and is linked to a deal after approval.
- Attachments stored under deal folder; RAG indexing reflects new content.

### RAG/embeddings architecture
Options:
- A) Central RAG service with vector store keyed by deal_id
  Pros: Fast retrieval, Consistent with single truth
  Cons: Requires indexing pipeline
- B) Agent-local embeddings
  Pros: Simpler agent runtime
  Cons: Inconsistent context, No shared truth
- C) No embeddings
  Pros: Low complexity
  Cons: Violates end-state
Recommendation: Choose A. Embed only canonical deal artifacts and store metadata in Postgres.
Migration approach:
1. Define indexing pipeline triggered on new emails/attachments/notes.
2. Add reindex_deal action and automated nightly refresh.
3. Expose RAG health endpoint and fail-closed behavior.
Verification proof:
- search_deals returns expected hits for known content.
- RAG health endpoint returns OK and indexing metrics.

### HITL approval persistence + auditability
Options:
- A) Store approvals in backend DB with agent references
  Pros: Unified audit trail, Queryable by deal
  Cons: Migration from agent DB
- B) Keep approvals only in agent DB
  Pros: Minimal change
  Cons: No unified traceability
- C) Ephemeral approvals
  Pros: Low storage
  Cons: No auditability
Recommendation: Choose A. Mirror approvals into backend with correlation_id and deal_id.
Migration approach:
1. Add approvals table in backend and replicate current approvals on write.
2. Update approval APIs to emit audit events tied to deal_id and correlation_id.
Verification proof:
- Approval records visible in backend with correlation_id.
- Audit trail links agent action to deal_events.

### Auth model (dashboard, backend, agent)
Options:
- A) OIDC/JWT for users + service tokens for internal services
  Pros: Industry standard, User attribution, RBAC support
  Cons: Requires auth provider integration
- B) Static API keys for UI
  Pros: Simple
  Cons: No user attribution, Security risk
- C) No auth
  Pros: None
  Cons: Unacceptable
Recommendation: Choose A with local dev fallback. Enforce JWT on backend and attach user identity to deal_events.
Migration approach:
1. Add auth middleware to dashboard and backend.
2. Add RBAC policy for deal actions and admin actions.
3. Propagate user_id to audit and event tables.
Verification proof:
- Unauthenticated requests fail with 401/403.
- Audit logs include user_id for all writes.

## Phased Implementation Plan (sequenced, dependency-aware)
### Phase 0: Stop the Bleeding & Observability Baseline
- Objective: Establish security guardrails and end-to-end traceability; eliminate silent failures.
- V2 issue IDs covered: ZK-ISSUE-0005, ZK-ISSUE-0011, ZK-ISSUE-0018, ZK-ISSUE-0010
- Atomic task list:
1. Add dashboard authentication (JWT/OIDC) and user identity propagation (ZK-ISSUE-0005).
2. Add correlation_id propagation dashboard -> backend -> agent and persist in deal_events + audit_log (ZK-ISSUE-0011).
3. Add structured logging + error surfacing and explicit health checks for RAG/email ingestion (ZK-ISSUE-0010).
4. Fix dashboard Zod handling to avoid silent drops; log schema mismatch (ZK-ISSUE-0018).
- Dependencies:
- Decision Set: Auth model
- Decision Set: Agent tool boundaries
- Risks + rollback: Auth rollout may disrupt current usage; mitigate with staged rollout and feature flags.
- Gate (must-pass checks): All write endpoints require auth; correlation_id visible across logs; schema mismatches logged.
- Acceptance criteria:
- 401/403 returned for unauthenticated dashboard access.
- Every write request contains correlation_id and user_id.
- RAG/email health endpoints return explicit status (OK/FAIL).
- Evidence required:
- Auth middleware logs + curl results
- Sample trace showing correlation_id across services
- Health check outputs

### Phase 1: Data Truth Unification
- Objective: Eliminate split-brain persistence and unify actions/deals in Postgres.
- V2 issue IDs covered: ZK-ISSUE-0001, ZK-ISSUE-0008, ZK-ISSUE-0014
- Atomic task list:
1. Design canonical deal schema fields (including dataroom_path and external_ids).
2. Migrate JSON deal_registry into Postgres; keep id mapping and provenance (ZK-ISSUE-0001).
3. Refactor CreateDealFromEmailExecutor to write to Postgres and remove sys.path hack (ZK-ISSUE-0014).
4. Migrate actions engine to use Postgres zakops.actions; retire SQLite store (ZK-ISSUE-0008).
- Dependencies:
- Decision Set: Source-of-truth DB model
- Risks + rollback: Data migration errors; mitigate with dry-run and reversible migration scripts.
- Gate (must-pass checks): Creating a deal via any path writes a single Postgres row; no JSON or SQLite writes.
- Acceptance criteria:
- deal_registry.json not written by any process
- SQLite action DB unused
- Postgres is sole source for deals and actions
- Evidence required:
- Migration logs
- DB queries showing consistent counts
- ripgrep results for legacy write paths

### Phase 2: Contract Alignment (UI, Backend, Agent)
- Objective: Align API contracts and ensure UI/agent calls hit active backend endpoints.
- V2 issue IDs covered: ZK-ISSUE-0006, ZK-ISSUE-0012, ZK-ISSUE-0009, ZK-ISSUE-0018
- Atomic task list:
1. Update dashboard to call /api/quarantine/{id}/process instead of legacy /resolve (ZK-ISSUE-0006).
2. Implement or align notes endpoint in orchestration API and update UI (ZK-ISSUE-0012).
3. Add agent create_deal tool with HITL and backend validation (ZK-ISSUE-0009).
4. Generate and consume OpenAPI client to reduce schema drift; harden Zod schemas (ZK-ISSUE-0018).
- Dependencies:
- Phase 0 complete
- Phase 1 (if create_deal depends on canonical DB)
- Risks + rollback: Breaking UI routes; mitigate with compatibility endpoints or redirects.
- Gate (must-pass checks): No 404s for UI core flows; agent tool contract tested against backend.
- Acceptance criteria:
- Quarantine approve works from UI
- Deal notes persist
- Agent create_deal works only with approval
- Evidence required:
- Curl tests for updated endpoints
- UI integration tests
- Agent tool logs

### Phase 3: Deal Lifecycle Correctness
- Objective: Make quarantine, stages, and transitions correct and deterministic.
- V2 issue IDs covered: ZK-ISSUE-0003, ZK-ISSUE-0007, ZK-ISSUE-0016, ZK-ISSUE-0022
- Atomic task list:
1. Align stage taxonomy across DB, backend workflow, UI, and agent; fix default stage (ZK-ISSUE-0007).
2. Implement atomic quarantine approval -> deal creation/linking with idempotency (ZK-ISSUE-0003).
3. Add duplicate deal detection (unique constraint or semantic match) (ZK-ISSUE-0016).
4. Add archive/restore endpoints in orchestration API (ZK-ISSUE-0022).
- Dependencies:
- Phase 1 complete
- Decision Set: Deal taxonomy
- Risks + rollback: Breaking existing data due to stage mismatch; mitigate with migration and backfills.
- Gate (must-pass checks): Approving quarantine creates a deal; stage transitions validated; archive/restore works.
- Acceptance criteria:
- No deals with invalid stages
- Duplicate creation returns 409 or merges
- Archive/restore toggles deleted flag
- Evidence required:
- DB queries for stage validity
- Quarantine approve end-to-end test
- Archive/restore curl tests

### Phase 4: Deal Knowledge System (Email, DataRoom, RAG, Actions)
- Objective: Turn each deal into a living knowledge object with email/attachments/RAG integration.
- V2 issue IDs covered: ZK-ISSUE-0002, ZK-ISSUE-0004, ZK-ISSUE-0010, ZK-ISSUE-0013, ZK-ISSUE-0019, ZK-ISSUE-0021
- Atomic task list:
1. Re-enable email ingestion targeting Postgres quarantine/deals and attach to deals (ZK-ISSUE-0002).
2. Create DataRoom folder scaffolding on deal creation; store path in DB (ZK-ISSUE-0004).
3. Wire action executors to UI and workflows with tracking (ZK-ISSUE-0019).
4. Implement /api/actions/capabilities and /metrics from registry (ZK-ISSUE-0013).
5. Implement RAG indexing pipeline and validate search_deals (ZK-ISSUE-0010).
6. Add scheduling/reminders framework for follow-ups and SLAs (ZK-ISSUE-0021).
- Dependencies:
- Phase 1 and Phase 3 complete
- Risks + rollback: Operational load from ingestion and indexing; mitigate with throttling and monitoring.
- Gate (must-pass checks): Email -> quarantine -> deal update -> RAG searchable; DataRoom folders created.
- Acceptance criteria:
- New emails appear under correct deal
- Deal folder exists for new deal
- Actions capabilities endpoint returns data
- Evidence required:
- Email ingestion logs
- Folder existence checks
- RAG search output

### Phase 5: Hardening & Real-time UX
- Objective: Operational hardening, expiry, retention, and realtime updates.
- V2 issue IDs covered: ZK-ISSUE-0015, ZK-ISSUE-0017, ZK-ISSUE-0020
- Atomic task list:
1. Add approval expiry background job and metrics (ZK-ISSUE-0015).
2. Define and implement retention/cleanup policy for archived/junk deals (ZK-ISSUE-0017).
3. Implement SSE/WebSocket stream for realtime updates (ZK-ISSUE-0020).
- Dependencies:
- Phase 3 and Phase 4 complete
- Risks + rollback: Job scheduling reliability; mitigate with retries and idempotent jobs.
- Gate (must-pass checks): Expired approvals auto-transition; UI updates via SSE without polling.
- Acceptance criteria:
- Pending approvals older than TTL become expired
- Archived deals cleaned according to policy
- SSE endpoint streams deal updates
- Evidence required:
- Cron/job logs
- DB counts before/after cleanup
- SSE client output

### Phase 6: Legacy Decommission & Final Proof
- Objective: Remove legacy services, paths, and dead endpoints; prove no references remain.
- V2 issue IDs covered: ZK-ISSUE-0001, ZK-ISSUE-0008, ZK-ISSUE-0014, ZK-ISSUE-0006, ZK-ISSUE-0012
- Atomic task list:
1. Remove deal_lifecycle API and legacy endpoints (/resolve, /note, /archive) after replacements exist.
2. Delete or archive /home/zaks/scripts legacy registry/state machine modules.
3. Remove JSON deal_registry and SQLite action DB; add CI guard to prevent reintroduction.
4. Confirm no sys.path hacks or direct legacy imports exist.
- Dependencies:
- Phases 1-5 complete
- Risks + rollback: Breaking legacy consumers; mitigate with deprecation window and compatibility shims.
- Gate (must-pass checks): rg finds no legacy references; services only expose canonical endpoints.
- Acceptance criteria:
- Legacy endpoints return 404
- No references to deal_registry.json or scripts path
- CI checks pass
- Evidence required:
- rg output
- Service route listings
- Deployment diffs

## No-Drop Coverage Matrix (V2 issue IDs -> remediation)
| Issue ID | Phase | Task(s) | Verification step(s) | Definition of Done |
|---|---|---|---|---|
| ZK-ISSUE-0001 | Phase 1 | Migrate JSON registry to Postgres; Remove split-brain writers | Create deal via all paths -> single Postgres row; No writes to deal_registry.json | Postgres only, JSON/legacy unused |
| ZK-ISSUE-0002 | Phase 4 | Enable ingestion pipeline; Write to Postgres quarantine/deal tables | Cron/queue run creates quarantine items; Email linked to deal | Ingestion active and producing rows |
| ZK-ISSUE-0003 | Phase 3 | Approve quarantine -> create deal; Idempotency guard | Approve item yields new deal row | Single action creates deal and links quarantine |
| ZK-ISSUE-0004 | Phase 4 | Create DataRoom folders on deal creation | Folder exists for new deal | Deal has folder and path stored |
| ZK-ISSUE-0005 | Phase 0 | Add dashboard auth | Unauth requests fail with 401/403 | Only authenticated users access dashboard |
| ZK-ISSUE-0006 | Phase 2 | Update UI to /process | POST /process returns 200 | UI resolves quarantine without 404 |
| ZK-ISSUE-0007 | Phase 3 | Align stage taxonomy; Fix DB default | No invalid stages in DB | All components use canonical stages |
| ZK-ISSUE-0008 | Phase 1 | Migrate actions engine to Postgres | Actions appear in zakops.actions only | SQLite action DB unused |
| ZK-ISSUE-0009 | Phase 2 | Add create_deal agent tool with HITL | Agent create_deal works after approval | Agent can create deals via backend |
| ZK-ISSUE-0010 | Phase 4 | RAG health checks; Index deals | search_deals returns results | RAG service verified and indexed |
| ZK-ISSUE-0011 | Phase 0 | Add correlation_id propagation | Same correlation_id appears in agent + backend logs | Full traceability across services |
| ZK-ISSUE-0012 | Phase 2 | Add notes endpoint in orchestration or update UI | POST /api/deals/{id}/note returns 200 | Notes endpoint matches UI |
| ZK-ISSUE-0013 | Phase 4 | Implement /actions/capabilities and /metrics | Endpoints return data (not 501) | Capabilities and metrics visible |
| ZK-ISSUE-0014 | Phase 1 | Remove sys.path hack and legacy imports | rg shows no sys.path hack | Executors use canonical backend code |
| ZK-ISSUE-0015 | Phase 5 | Add approval expiry background job | Pending approvals auto-expire | No stale approvals remain |
| ZK-ISSUE-0016 | Phase 3 | Add duplicate detection | Duplicate create returns 409 | Duplicates prevented or merged |
| ZK-ISSUE-0017 | Phase 5 | Implement retention/cleanup policy | Archived deals cleaned after policy | Retention job in place |
| ZK-ISSUE-0018 | Phase 2 | Zod passthrough + schema sync | Schema mismatches logged | No silent drop of deals |
| ZK-ISSUE-0019 | Phase 4 | Wire action executors into workflows | Executor run creates action record | Executors accessible and tracked |
| ZK-ISSUE-0020 | Phase 5 | Implement SSE/WebSocket updates | /api/events/stream returns events | UI receives realtime updates |
| ZK-ISSUE-0021 | Phase 4 | Add scheduling/reminders | Reminders fire for overdue deals | Scheduler running with notifications |
| ZK-ISSUE-0022 | Phase 3 | Add archive/restore endpoints | /archive and /restore endpoints work | Archive/restore supported |

## Verification & QA Plan (tough)
### Gate A: Code health
- Lint/typecheck/unit/integration must pass in backend, agent, and dashboard repos.
- Example checks: `pytest`, `pnpm lint`, `pnpm typecheck`, `ruff` as applicable.
### Gate B: End-to-end proof
- Dashboard -> backend -> agent -> DB: create, transition, approve, archive, and search flows all validated with correlation_id.
### QA Pass #1: Functional (happy paths)
- Create deal via API, verify Postgres row, DataRoom folder, and RAG indexing.
- Approve quarantine item -> deal created -> stage transition -> archived.
### QA Pass #2: Adversarial
- Missing auth tokens -> 401/403.
- RAG down -> search_deals fails with explicit error and logs.
- Duplicate deal creation -> 409 or merge.
### Example verification commands
- `curl -s -H 'Authorization: Bearer <jwt>' http://localhost:8091/api/deals`
- `curl -X POST http://localhost:8091/api/quarantine/<id>/process -d '{"action":"approve"}'`
- `psql -c "SELECT deal_id, stage FROM zakops.deals ORDER BY created_at DESC LIMIT 5;"`
- `curl http://localhost:8052/health`
### Correlation strategy
- Generate correlation_id in dashboard middleware; pass to backend and agent in headers.
- Store correlation_id in zakops.deal_events and agent audit_log for joinable tracing.

## Legacy Decommission Plan (MANDATORY)
- Remove legacy deal_lifecycle API routes and deployment artifacts after replacements exist.
- Delete/retire legacy scripts under /home/zaks/scripts used by sys.path hacks.
- Remove JSON deal_registry and SQLite action store after data migration.
- Add CI guard rails: rg -n 'deal_registry.json|deal_lifecycle|sys.path' must return 0.
- Verification commands:
  - `rg -n 'deal_registry.json|deal_lifecycle|sys.path' /home/zaks/zakops-backend /home/zaks/zakops-agent-api`
  - `curl -i http://localhost:8091/api/quarantine/<id>/resolve` (expect 404)
  - `ls /home/zaks/DataRoom/.deal-registry` (expect removed or archived)

## Prioritized Backlog (P0-P3)
| ID | Priority | Effort | Owner | Dependencies | Verification | Expected Outcome |
|---|---|---|---|---|---|---|
| ZK-ISSUE-0001 | P0 | L | backend/data | Decision: source-of-truth DB | Single Postgres row created from all paths | Split-brain eliminated |
| ZK-ISSUE-0002 | P0 | M | infra/data | Phase 1 + Phase 3 | Ingestion creates quarantine items | Email ingestion active |
| ZK-ISSUE-0003 | P1 | M | backend | Phase 1 | Approve -> deal created | Quarantine approval creates deal |
| ZK-ISSUE-0004 | P1 | M | backend/infra | Phase 1 | Folder created for new deal | DataRoom folders consistent |
| ZK-ISSUE-0005 | P1 | M | frontend/security | Auth decision | Unauthorized access blocked | Dashboard secured |
| ZK-ISSUE-0006 | P1 | S | frontend/backend | Phase 2 | /process endpoint works | Quarantine UI works |
| ZK-ISSUE-0007 | P1 | M | backend/data | Deal taxonomy decision | Stage mismatch eliminated | Single stage model |
| ZK-ISSUE-0008 | P1 | M | backend/data | Phase 1 | Actions stored in Postgres | Unified actions |
| ZK-ISSUE-0009 | P2 | S | agent/backend | Phase 2 | Agent create_deal tool works | Agent can create deals with HITL |
| ZK-ISSUE-0010 | P2 | M | infra/agent | Phase 4 | RAG health OK + search_deals returns results | RAG integration verified |
| ZK-ISSUE-0011 | P2 | M | backend/agent | Phase 0 | correlation_id links logs | Unified audit trail |
| ZK-ISSUE-0012 | P2 | S | frontend/backend | Phase 2 | Notes endpoint works | Deal notes functional |
| ZK-ISSUE-0013 | P2 | S | backend | Phase 4 | Capabilities/metrics return 200 | Actions UI functional |
| ZK-ISSUE-0014 | P2 | S | backend | Phase 1 | No sys.path hacks | Legacy hacks removed |
| ZK-ISSUE-0015 | P3 | S | agent/backend | Phase 5 | Expired approvals auto-closed | Approval queue clean |
| ZK-ISSUE-0016 | P2 | S | backend/data | Phase 3 | Duplicate create returns 409 | Duplicate deals prevented |
| ZK-ISSUE-0017 | P3 | M | backend/infra | Phase 5 | Cleanup job removes aged deals | Retention policy enforced |
| ZK-ISSUE-0018 | P2 | S | frontend | Phase 2 | Schema mismatch logged | No silent UI drops |
| ZK-ISSUE-0019 | P2 | L | backend/agent | Phase 4 | Executors wired + tracked | Actions usable |
| ZK-ISSUE-0020 | P2 | M | backend/frontend | Phase 5 | SSE streams updates | Realtime updates |
| ZK-ISSUE-0021 | P2 | M | backend | Phase 4 | Reminders fire | Scheduling available |
| ZK-ISSUE-0022 | P3 | S | backend | Phase 3 | Archive/restore endpoints work | Archive supported |

