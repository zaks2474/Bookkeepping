# DEAL-INTEGRITY-001: UNIFIED PLATFORM MISSION

## Mission ID: DEAL-INTEGRITY-UNIFIED-001
## Codename: "FOUNDATION ZERO"
## Priority: P0 — Platform-Critical
## Executor: Claude Code (Opus 4.6)
## Authority: FULL EXECUTION — Build everything, verify everything, skip nothing

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║  DIRECTIVE: BRING ZAKOPS FROM "WORKING WITH HIDDEN DEFECTS"            ║
║  TO "CORRECT BY CONSTRUCTION"                                          ║
║                                                                        ║
║  This is not a bug-fix mission. This is a platform stabilization       ║
║  program. The goal is a system where impossible states cannot           ║
║  exist, every surface shows the same truth, and the platform           ║
║  prevents its own regression.                                          ║
║                                                                        ║
║  SIX LAYERS. BOTTOM TO TOP. EACH IS A PREREQUISITE FOR THE NEXT.      ║
║  NOTHING ABOVE CAN SUCCEED IF ANYTHING BELOW IS INCOMPLETE.           ║
║                                                                        ║
║  LAYER 6 ─── GOVERNANCE & EVOLUTION                                    ║
║  LAYER 5 ─── VERIFICATION & OBSERVABILITY                              ║
║  LAYER 4 ─── DEFENSIVE ARCHITECTURE                                    ║
║  LAYER 3 ─── APPLICATION PARITY                                        ║
║  LAYER 2 ─── DATA MODEL INTEGRITY                                      ║
║  LAYER 1 ─── INFRASTRUCTURE TRUTH                                      ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                      ║
║           ZAKOPS PLATFORM                                              ║
║                                                                        ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## SOURCE MATERIAL

This mission consolidates findings from a multi-pass forensic investigation conducted on 2026-02-08 by three independent agents (Claude Code CC3, Claude Code CC1, Codex), cross-reviewed across 6 reports, deduplicated into 9 confirmed issues, 4 operator decisions, and 34 innovation ideas. The findings were then subjected to strategic review identifying 7 dashboard page-level gaps, 5 cross-stack gaps, 10 mandatory platform questions, and the organizational root cause.

### Audit Reports (read before executing any layer)

| Document | Location | Purpose |
|----------|----------|---------|
| MASTER Diagnosis | `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_MASTER.md` | 9 deduped issues, root causes, evidence index, fix approaches, innovation ideas |
| Chat Analysis | `/home/zaks/bookkeeping/docs/Chat-DEAL-INTEGRITY-001_MASTER.md.txt` | Gap analysis, 10 platform questions, six-layer architecture, dashboard page audit |
| Evidence (CC3) | `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-001/evidence/00-forensics/` | DB queries, API responses, schema dumps |
| Evidence (Codex) | `/home/zaks/bookkeeping/docs/_evidence/DEAL-INTEGRITY-001-PASS1/` | DB counts, env files, code excerpts |
| Pipeline Log | `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_PIPELINE_MASTER_LOG.md` | Append-only run log |
| META-QA | `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001.METAQA.CloudCode.20260208T165921Z.md` | Pass 4 quality assurance findings |

### System Context (read before executing any layer)

| Document | Location | Purpose |
|----------|----------|---------|
| CLAUDE.md | `/home/zaks/zakops-agent-api/CLAUDE.md` | System guide, contract surfaces, ports, codegen |
| Makefile | `/home/zaks/zakops-agent-api/Makefile` | All make targets including sync and validate |
| Backend source | `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Archive endpoint, deals listing, filters |
| Dashboard source | `/home/zaks/zakops-agent-api/apps/dashboard/` | All pages, components, API client |
| Agent API source | `/home/zaks/zakops-agent-api/apps/agent-api/` | Agent service, deal queries |
| Contracts | `/home/zaks/zakops-agent-api/packages/contracts/` | OpenAPI specs, generated types |

---

## CONFIRMED DEFECTS — COMPLETE REGISTRY

Every item below must be fully resolved by the end of this mission. No item may be silently skipped. If an item proves impractical at a given layer, it must be documented with the reason and escalated — never dropped.

### Systemic Root Causes

| ID | Root Cause | Severity | Layers That Address It |
|----|-----------|----------|----------------------|
| ROOT-A | **Incoherent Deal Lifecycle State Machine** — Three uncoordinated fields (`status`, `stage`, `deleted`) with no enforced coupling. Archive endpoint updates only `stage`, leaving `status='active'` and `deleted=false`. | CRITICAL | Layer 2 (primary), Layer 3 (surface propagation) |
| ROOT-B | **Split-Brain Database Infrastructure** — Two PostgreSQL containers (port 5432 canonical, port 5435 legacy) with divergent data (49 vs 51 deals). Cross-service data invisibility. | CRITICAL | Layer 1 (primary) |

### Issue Registry

| ID | Issue | Severity | Root Cause | Resolving Layers |
|----|-------|----------|------------|-----------------|
| DI-ISSUE-001 | Archive endpoint performs partial state transition | CRITICAL | ROOT-A | Layer 2 |
| DI-ISSUE-002 | Deal counts disagree across surfaces | HIGH | ROOT-A + ROOT-B | Layer 2 + Layer 3 |
| DI-ISSUE-003 | Pipeline stage totals don't sum to header count | HIGH | ROOT-A + hardcoded stage lists | Layer 3 |
| DI-ISSUE-004 | Active filter doesn't actually filter | MEDIUM | ROOT-A | Layer 2 + Layer 3 |
| DI-ISSUE-005 | Zod validation error on HQ (intermittent) | MEDIUM | Promise.all fragility + schema mismatch | Layer 4 |
| DI-ISSUE-006 | Split-brain database (two Postgres instances) | CRITICAL | ROOT-B | Layer 1 |
| DI-ISSUE-007 | UI-created deals don't fully propagate | MEDIUM | ROOT-A (visual) + ROOT-B (data loss) | Layer 1 + Layer 3 |
| DI-ISSUE-008 | `audit_trail` column referenced but missing from schema | LOW | Dead code / missing migration | Layer 2 |
| DI-ISSUE-009 | `/api/actions/kinetic` returns HTTP 500 | LOW | Broken or dead endpoint | Layer 4 |

### Dashboard Page-Level Gaps (from strategic review)

| ID | Page | Gap | Severity | Resolving Layer |
|----|------|-----|----------|----------------|
| PG-001 | `/dashboard` | Promise.all with 5 fetches, no error handling — same fragility as /hq but unfixed | CRITICAL | Layer 4 |
| PG-002 | `/dashboard` | Own `STAGE_ORDER` (9 stages) different from /hq's list; client-side counting | CRITICAL | Layer 3 |
| PG-003 | `DealBoard.tsx` | Only renders 6 of 9 stages — `portfolio`, `junk`, `archived` invisible | CRITICAL | Layer 3 |
| PG-004 | `/deals/[id]` | Promise.all with 7 fetches, zero error handling — worst fragility instance | CRITICAL | Layer 4 |
| PG-005 | `/deals` | "Delete" button label calls `archiveDeal()` — label/action mismatch | MEDIUM | Layer 3 |
| PG-006 | `/deals` | `STATUSES` array missing 'archived'; no stage-based filter | MEDIUM | Layer 3 |
| PG-007 | `/actions` | Promise.all with 3 fetches, no error handling; no archived indicator for referenced deals | MEDIUM | Layer 4 |
| PG-008 | `/deals/[id]` | No visual distinction for `status='archived'` in badge | MEDIUM | Layer 3 |
| PG-009 | Codebase-wide | At least 5 independent hardcoded stage lists, no shared config | CRITICAL | Layer 3 |

### Cross-Stack Gaps (from strategic review)

| ID | Gap | Resolving Layer |
|----|-----|----------------|
| CS-001 | Agent API DSN never verified — may connect to rogue DB | Layer 1 |
| CS-002 | RAG/LLM service DSN never verified — may connect to rogue DB | Layer 1 |
| CS-003 | RAG indexes stale after backfill — no re-index step | Layer 3 |
| CS-004 | Contract sync (`make sync-all-types`) never run in any original mission | Layer 3 + Layer 5 |
| CS-005 | `v_pipeline_summary` view implicitly changes after backfill — unverified | Layer 2 + Layer 3 |

---

## 10 MANDATORY PLATFORM CONSTRAINTS

These are non-negotiable requirements derived from the strategic review. Each must appear as a gate, evidence requirement, or explicit scope item within the layers below. None are optional.

| # | Constraint | Where It Appears |
|---|-----------|-----------------|
| Q1 | **Backfill reversibility** — The migration for soft-deleted deals (12 rows with `deleted=true`, `status='active'`) must be handled explicitly. The backfill must be reversible without re-creating the original bug. CHECK constraints must not fail on edge-case rows. | Layer 2: Scope, Risk & Rollback |
| Q2 | **Production observability** — Post-deployment monitoring must exist. Health endpoints reporting DB identity. Alerts on count invariant violations. Structured logging on every state transition. | Layer 5: Scope, Exit Gate |
| Q3 | **Deployment and rollback sequencing** — Each layer must define its atomic rollback unit. Rolling back Layer 2 must not break Layer 3. Dependency chains must be explicit. | Every Layer: Risk & Rollback |
| Q4 | **Automated test strategy** — Every "Never Again" enforcement from the MASTER document must become an actual test. No test may be listed but unwritten. | Layer 5: Scope, Exit Gate |
| Q5 | **Agent API and RAG service impact** — Both services must be audited for DSN configuration, deal query logic, and compatibility with the new lifecycle model. RAG must re-index after the backfill. | Layer 1: Scope; Layer 3: Scope |
| Q6 | **Contract sync enforcement** — `make sync-all-types` must be a mandatory gate after every layer that changes an API response shape. Generated types must never be stale. | Layer 3: Exit Gate; Layer 5: CI Gate |
| Q7 | **Lifecycle model decision — DECIDED: Option A with full FSM infrastructure.** Retain the three-field system, add `transition_deal_state()` as the single choke point, CHECK constraints, DB trigger, and `audit_trail` logging. Design the transition function so a future migration to Option C (lifecycle ENUM) requires changing only that one function. Document as ADR-001. | Layer 2: Scope (first action) |
| Q8 | **Concurrency safety** — Race conditions on simultaneous archive/restore operations must be addressed. Row-level locking or optimistic concurrency must be implemented. | Layer 2: Scope |
| Q9 | **Performance impact and baselines** — Critical queries must be profiled before and after changes. Indexes must be verified for the pipeline summary view. Response time baselines must be captured. | Layer 5: Scope, Evidence |
| Q10 | **Governance model** — A single source of truth for deal lifecycle semantics, a change protocol for state modifications, ADRs documenting design decisions, and a runbook for "how to add a new deal stage." | Layer 6: Full Scope |

---

## EXECUTION SEQUENCE

```
LAYER 1  ━━━━━━━━━━━━━━  [solo — no dependencies]
         ↓
LAYER 2  ━━━━━━━━━━━━━━  [requires Layer 1 COMPLETE]
         ↓
LAYER 3  ━━━━━━━━━━━━━━  [requires Layer 2 COMPLETE]
         ↓
LAYER 4  ━━━━━━━━━━━━━━  [can begin in parallel with Layer 3]
         ↓
LAYER 5  ━━━━━━━━━━━━━━  [requires Layers 3 + 4 COMPLETE]
         ↓
LAYER 6  ━━━━━━━━━━━━━━  [can begin in parallel with Layer 5]
```

Layers 1 and 2 are strictly sequential — the data model cannot be fixed while two databases exist. Layer 3 requires the data model to be finalized. Layer 4 (defensive architecture) is independent of Layer 3's specifics and can run in parallel. Layer 5 tests what Layers 3 and 4 built. Layer 6 is process and governance work that can begin once the technical decisions in Layer 2 are finalized.

**CRITICAL: No layer may be marked COMPLETE until all its exit gates pass, all evidence is produced, and builder self-verification plus second-pass confirmation are both documented.**

---

## EVIDENCE STRUCTURE

All evidence must be stored under:

```
/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-UNIFIED/
├── layer-1/
│   ├── evidence/
│   │   ├── pre-state/       (before any changes)
│   │   └── post-state/      (after layer completion)
│   └── completion-report.md
├── layer-2/
│   ├── evidence/
│   │   ├── pre-state/
│   │   ├── migration/
│   │   ├── backfill/
│   │   └── post-state/
│   └── completion-report.md
├── layer-3/
│   ├── evidence/
│   │   ├── page-audits/
│   │   ├── cross-service/
│   │   └── contract-sync/
│   └── completion-report.md
├── layer-4/
│   ├── evidence/
│   │   ├── failure-simulation/
│   │   └── degradation-tests/
│   └── completion-report.md
├── layer-5/
│   ├── evidence/
│   │   ├── test-results/
│   │   ├── performance-baselines/
│   │   └── monitoring-setup/
│   └── completion-report.md
├── layer-6/
│   ├── evidence/
│   │   ├── adrs/
│   │   ├── runbooks/
│   │   └── stage-config/
│   └── completion-report.md
└── final-verification.md
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYER 1: INFRASTRUCTURE TRUTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Objective

Establish that there is exactly ONE canonical data store for the ZakOps platform and that EVERY service, script, and tool connects to it. Eliminate every source of data divergence. Make split-brain physically impossible at the infrastructure level.

## Scope

### IN SCOPE

1. **Kill the rogue database. Permanently.** The legacy `zakops-postgres` container on port 5435 must be stopped, removed, and its volumes destroyed. No dump. No backup. No preservation. This container is the root cause of split-brain data divergence and it must never exist again. Any service that depended on it will be fixed to use the canonical DB — the rogue container is not a fallback for anything.

2. **Audit EVERY service's database connection.** This means:
   - Backend API (`zakops-backend`) — confirm its `DATABASE_URL` points to the canonical DB
   - Agent API (`zakops-agent-api/apps/agent-api`) — locate its DB configuration, verify it connects to the canonical DB on port 5432, fix if not
   - RAG/LLM service (`Zaks-llm`) — locate its DB configuration, verify it connects to the canonical DB, fix if not
   - Every `.env` file in every repository — search for any reference to port 5435, `localhost:5435`, or the legacy container name
   - Every `docker-compose` file — verify no secondary Postgres service is defined

3. **Add a startup DSN verification gate.** The Backend API must verify at startup that it is connected to the expected canonical database. If the DSN does not match, the service must refuse to start. This is the "never drift again" mechanism for Layer 1.

4. **Add DB identity to the health endpoint.** The `/health` endpoint (or equivalent) on every service that has one must report its connected database host, port, and database name. This allows operators to verify split-brain status with a single health check.

5. **Document the canonical database connection string** in a single authoritative location that all services reference.

### OUT OF SCOPE

- Schema changes (Layer 2)
- Data backfills (Layer 2)
- Application code changes beyond DSN configuration and health endpoints
- Dashboard changes (does not connect to DB directly)

## Dependencies

None. This is the foundation layer. It runs first.

## Exit Gates

Every gate must produce evidence. Builder must self-verify, then perform a second-pass confirmation.

| Gate | Success Criteria | Evidence Required |
|------|-----------------|-------------------|
| GATE L1-1 | Exactly ONE Postgres container is running in the Docker environment | Capture `docker ps` output showing one and only one Postgres container |
| GATE L1-2 | The rogue database container is GONE — stopped, removed, volumes destroyed. No trace remains. | Capture `docker ps -a` output showing zero containers matching `zakops-postgres` or port 5435; `docker volume ls` showing no associated volumes |
| GATE L1-3 | The rogue database's `docker-compose` definition is deleted from source | Diff showing removal of the secondary Postgres service definition |
| GATE L1-4 | Every `.env` file across all repositories contains ZERO references to port 5435 or the legacy container | Search results showing zero matches across `zakops-backend/`, `zakops-agent-api/`, `Zaks-llm/`, and any other relevant directories |
| GATE L1-5 | Every `docker-compose` file defines exactly ONE Postgres service | File listing showing all docker-compose files and their Postgres service definitions |
| GATE L1-6 | Agent API's database configuration points to the canonical DB (port 5432) | Agent API configuration file contents or environment variable showing the canonical DSN |
| GATE L1-7 | RAG/LLM service's database configuration points to the canonical DB | RAG service configuration file contents or environment variable showing the canonical DSN |
| GATE L1-8 | Backend API health endpoint reports its DB identity (host, port, dbname) | Health endpoint response showing DB identity fields |
| GATE L1-9 | Backend API startup gate exists — service refuses to start if DSN does not match canonical | Evidence of the gate being triggered: start with a wrong DSN and capture the refusal, then start with the correct DSN and capture success |
| GATE L1-10 | The canonical database connection string is documented in a single authoritative location | File path and contents of the canonical DSN documentation |

## Risk & Rollback

**Primary risk:** A service that was silently depending on the rogue DB (port 5435) will fail at startup after the container is removed.

**This is acceptable and intentional.** Any service that breaks is a service that was reading from the wrong database. The correct response is to fix that service's DSN to point to the canonical DB — NOT to bring the rogue container back. The rogue database is permanently destroyed. There is no rollback for its removal. It does not come back under any circumstances.

**Mitigation:** The DSN audit (Gates L1-4 through L1-7) identifies and fixes all consumers BEFORE removal so failures are prevented rather than reacted to. Any service with a 5435 reference gets its configuration corrected to the canonical DB.

**Rollback for other Layer 1 changes:** The startup DSN gate and health endpoint additions are standard code changes that can be reverted via git if needed. But the rogue DB removal is permanent and irreversible by design.

**Constraint Q3 (deployment sequencing):** Layer 1 is fully independent. No other layer has started. The only irreversible action is the rogue DB destruction, and that is an explicit operator decision — not a risk to mitigate.

## "Never Again" Enforcement

- **Startup DSN gate:** Backend refuses to start if connected DB does not match canonical DSN (implemented in this layer)
- **Health endpoint DB identity:** Operators can verify at any time that every service talks to the same DB
- **Single docker-compose Postgres definition:** No secondary DB can be introduced without modifying the compose file, which is version-controlled
- **Layer 5 will add:** CI smoke test that hits every service's health endpoint and verifies DB identity matches

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYER 2: DATA MODEL INTEGRITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Objective

Make impossible states unrepresentable at the database level. Implement the deal lifecycle as a single coherent design — not a patch to the existing three-field system, but the correct long-term model chosen deliberately and implemented completely. Every state transition goes through a single function. Concurrency is safe. The migration is reversible.

## Scope

### IN SCOPE

1. **Lifecycle model: OPTION A with full FSM infrastructure (Constraint Q7 — DECIDED).** The operator has selected Option A (Status Change) with the full finite state machine infrastructure that makes a future migration to Option C (Lifecycle ENUM) straightforward. This is a final decision, not a choice for the builder.

   **What Option A means concretely:**
   - The existing three-field system (`status`, `stage`, `deleted`) is retained
   - Archive sets `status='archived'` alongside `stage='archived'` — both fields updated atomically
   - A centralized `transition_deal_state()` function governs ALL state changes — no raw UPDATE queries for state fields
   - A database trigger auto-enforces status/stage/deleted consistency on every write, catching any bypass of the transition function
   - CHECK constraints make impossible state combinations unrepresentable at the DB level
   - The transition function is designed so that when the team later migrates to Option C (single `lifecycle_state` ENUM column), the function is the ONLY code that needs to change — every caller already goes through it

   **Why Option A, not Option C now:** Option A delivers correctness immediately with minimal migration risk. The full FSM infrastructure (transition function + trigger + constraints) means the three-field coordination problem is solved by design — future developers never touch status/stage/deleted directly. Option C can be implemented later as a single-function refactor inside `transition_deal_state()` without touching any callers.

   **Document this decision** as ADR-001 in the evidence directory. This ADR will be formalized in Layer 6.

2. **Fix the archive endpoint** (`main.py:867-907`). The endpoint must perform a complete state transition, not a partial one. It must:
   - Set ALL relevant fields atomically (not just `stage`)
   - Go through a centralized state transition function — not a raw SQL UPDATE
   - Return the updated deal with its new state
   - Handle the case where the deal is already archived (idempotent)

3. **Fix the restore endpoint.** When restoring an archived deal:
   - Reset ALL relevant fields atomically (status back to 'active', stage back to a configurable default or previous stage)
   - Go through the same centralized transition function
   - Return the updated deal

4. **Create the centralized transition function.** All state changes to deals — archive, restore, delete, undelete, and any future transitions — must go through a single function (`transition_deal_state` or equivalent). This function:
   - Validates the requested transition is allowed from the current state
   - Updates all relevant fields atomically
   - Prevents impossible states by design, not just by constraint
   - Logs the transition for audit purposes

5. **Backfill existing data.** Handle ALL edge cases:
   - 6 deals with `stage='archived'`, `status='active'`, `deleted=false` — these must be corrected
   - 12 deals with `deleted=true`, `status='active'` — these must be corrected (Constraint Q1: these rows exist and will violate a naive CHECK constraint)
   - The backfill must handle both groups before any CHECK constraint is applied
   - The backfill must be reversible — document the exact reversal steps

6. **Add database constraints.** After the backfill:
   - Add CHECK constraint(s) that make impossible states unrepresentable
   - The constraint must account for ALL valid state combinations: active deals, archived deals, deleted deals, and any edge cases
   - Test the constraint by attempting to insert an invalid state — the DB must reject it

7. **Add a database trigger.** The trigger auto-enforces status/stage/deleted consistency on every write to the `deals` table, catching any code path that bypasses the transition function. This is mandatory — it is the DB-level safety net that makes the three-field system safe under Option A. The trigger must:
   - Fire on INSERT and UPDATE
   - Validate that the new row's status/stage/deleted combination is a valid state
   - Reject the write if the state combination is invalid (same enforcement as the CHECK constraint, but as a belt-and-suspenders)
   - Optionally: auto-correct derived fields (e.g., if stage is set to 'archived', auto-set status to 'archived') — this makes the system self-healing even if a code path bypasses the transition function

8. **Handle the `audit_trail` ghost column (DI-ISSUE-008).** The backend references `audit_trail` at `main.py:1103, 1142, 1263` but the column does not exist. Since the centralized transition function logs every state change (scope item 4), add the `audit_trail` column via migration (`JSONB DEFAULT '[]'`). The transition function appends an entry to this column on every state change, creating a built-in per-deal audit history. This turns a latent bug into a feature that supports the FSM design.

9. **Verify the `v_pipeline_summary` view.** After the backfill changes `status` values, this view's output changes implicitly (it filters `WHERE deleted = false AND status = 'active'`). Document what the view returns BEFORE and AFTER the backfill. Confirm the new output is correct for Layer 3's consumption. (Cross-stack gap CS-005)

10. **Address concurrency (Constraint Q8).** The archive and restore operations must be safe under concurrent access. Either:
    - Use `SELECT ... FOR UPDATE` row-level locking within transactions
    - Or use optimistic concurrency (check `updated_at` matches expected value before updating)
    - Document which approach is chosen and why

### OUT OF SCOPE

- Dashboard UI changes (Layer 3)
- Error boundary / Promise.allSettled changes (Layer 4)
- Agent API query changes (Layer 3)
- RAG re-indexing (Layer 3)

## Dependencies

Layer 1 must be COMPLETE. There must be exactly one database. The canonical DSN must be confirmed.

## Exit Gates

| Gate | Success Criteria | Evidence Required |
|------|-----------------|-------------------|
| GATE L2-1 | ADR-001 documents Option A with full FSM infrastructure, including rationale for why Option A now and the path to Option C later | ADR file in evidence directory |
| GATE L2-2 | The archive endpoint performs a COMPLETE state transition — `status='archived'` AND `stage='archived'` set atomically via the transition function | Capture: archive a test deal, then query the DB row showing both `status` and `stage` are `'archived'` |
| GATE L2-3 | The restore endpoint performs a COMPLETE state reversal — `status='active'` and stage reset via the transition function | Capture: restore the archived test deal, then query the DB row showing `status='active'` and stage correctly reset |
| GATE L2-4 | `transition_deal_state()` function exists and ALL state-changing code paths use it — no raw UPDATE queries for status/stage/deleted anywhere | Code search evidence showing: (a) the function exists, (b) archive endpoint calls it, (c) restore endpoint calls it, (d) zero raw UPDATE queries for state fields outside the function |
| GATE L2-5 | Backfill is complete: ZERO deals exist with inconsistent state combinations | DB query: `SELECT COUNT(*) FROM zakops.deals WHERE (stage = 'archived' AND status != 'archived') OR (deleted = true AND status = 'active')` returns 0 |
| GATE L2-6 | Backfill handled BOTH groups: the 6 archived-stage deals AND the 12 soft-deleted deals (Constraint Q1) | DB query showing: (a) all `stage='archived'` deals have `status='archived'`, (b) all `deleted=true` deals have appropriate status, (c) total rows = 49 |
| GATE L2-7 | CHECK constraint exists and rejects impossible states | Attempt to INSERT a deal with `stage='archived', status='active'` — capture the DB rejection error |
| GATE L2-8 | Database trigger exists, fires on INSERT and UPDATE, and enforces status/stage/deleted consistency | Evidence: (a) trigger definition in schema, (b) attempt a raw UPDATE setting `stage='archived'` without changing `status` — the trigger either rejects it or auto-corrects `status` to `'archived'` |
| GATE L2-9 | Backfill is reversible — reversal steps are documented and tested | Document showing exact reversal SQL; evidence of testing the reversal on at least one row |
| GATE L2-10 | `audit_trail` JSONB column exists on the `deals` table and the transition function appends entries to it | DB schema showing column; DB row showing audit entry after a test state transition |
| GATE L2-11 | `v_pipeline_summary` view output is captured BEFORE and AFTER the backfill — new output is correct | Before/after query results showing what the view returns |
| GATE L2-12 | Concurrency is addressed — simultaneous archive/restore on the same deal cannot produce inconsistent state (Constraint Q8) | Description of concurrency mechanism; test showing two concurrent operations resolve correctly |
| GATE L2-13 | `GET /api/deals?status=active` returns ZERO deals with `stage='archived'` | API response evidence |
| GATE L2-14 | `GET /api/deals?status=archived` returns exactly the archived deals | API response evidence |
| GATE L2-15 | The transition function is designed as a single choke point — a future migration to Option C (lifecycle ENUM) requires changing ONLY this function, not its callers | Code review evidence showing all callers pass target state to the function, not raw field values |
| GATE L2-16 | The backend service starts successfully after all changes and passes its own health check | Health endpoint response after restart |

## Risk & Rollback

**Primary risk:** The backfill + CHECK constraint sequence can fail if edge cases are not handled in the correct order. Specifically: if the CHECK constraint is applied before all 18 inconsistent rows (6 archived + 12 deleted) are fixed, the ALTER TABLE will fail.

**Mitigation:** The backfill MUST run and be verified (Gate L2-5, L2-6) BEFORE the CHECK constraint is applied. These are two separate steps, not one.

**Rollback procedure (Constraint Q3):**
1. **Code rollback:** Revert the archive/restore endpoint changes and the transition function. This returns the backend to its pre-mission behavior.
2. **Data rollback:** Reverse the backfill using the documented reversal steps (Gate L2-8). This restores the data to its pre-mission state.
3. **Constraint rollback:** Drop the CHECK constraint. This removes the DB-level enforcement.
4. **CRITICAL ORDERING:** If Layer 3 has already been deployed (dashboard changes that assume the new data model), rolling back Layer 2 will cause Layer 3 to display incorrect data. Therefore: Layer 3 must be rolled back BEFORE Layer 2 if both need reverting.

**Constraint Q3 dependency chain:** Layer 2 → Layer 3 (unidirectional). Rolling back Layer 2 requires first rolling back Layer 3.

## "Never Again" Enforcement

- **Centralized `transition_deal_state()` function:** No code path can change deal state without going through the validated function. This is the single choke point that makes the three-field system safe and makes future migration to Option C a one-function change.
- **CHECK constraint:** The database itself rejects impossible state combinations — belt.
- **DB trigger:** Catches and rejects (or auto-corrects) any write that bypasses the transition function — suspenders.
- **`audit_trail` column:** Every state transition is logged per-deal, creating an immutable history of lifecycle changes.
- **Concurrency control:** Row-level locking or optimistic concurrency prevents race conditions from creating impossible states.
- **Option C migration path:** When the team is ready, adding a `lifecycle_state` ENUM column requires: (1) add the column with a migration, (2) update `transition_deal_state()` to write to it, (3) backfill from existing fields, (4) update queries to use the new column. No callers of the transition function change. The FSM infrastructure built in this layer makes this a bounded, predictable change.
- **Layer 5 will add:** Integration tests for every valid and invalid state transition; CI gate that fails if a new state-changing query bypasses the transition function

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYER 3: APPLICATION PARITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Objective

Every surface in the entire ZakOps platform that displays deal data must display it consistently — using the same source of truth, the same counting logic, the same stage definitions. No page, component, or service may compute deal data independently. There is ONE stage configuration. There is ONE way to count deals. Every surface renders what the server provides.

## Scope

### IN SCOPE

This is the widest layer. It addresses ALL consumers of deal data across ALL services. The original missions only fixed `/hq` and partially `/deals`. This layer fixes everything.

#### A. Canonical Stage Configuration (addresses PG-009, I-14)

1. **Create a single canonical stage configuration** that is the source of truth for all stage-related information across the entire platform. This configuration must define:
   - All valid pipeline stages (the stages shown in pipeline views)
   - All terminal stages (archived, junk, or equivalents)
   - The default stage for new deals
   - Display properties per stage (label, color, order, `show_in_pipeline` flag)
   - Whether this configuration lives in the contracts package (preferred — already exists in ZakOps architecture), a shared config file, or a backend API endpoint (`GET /api/pipeline/config`)

2. **Replace EVERY hardcoded stage list in the codebase.** The strategic review identified at least 5:
   - `/hq/page.tsx` `PIPELINE_STAGES` (7 entries)
   - `/dashboard/page.tsx` `STAGE_ORDER` (9 entries)
   - `DealBoard.tsx` `PIPELINE_STAGES` (6 entries)
   - `/deals/page.tsx` `STAGES` (9 entries)
   - `/deals/[id]/page.tsx` `STAGE_COLORS` (9 entries)

   Search the entire codebase for any other hardcoded stage arrays. Every one must be replaced with a reference to the canonical configuration.

3. **Ensure backend and frontend derive stage lists from the same source.** If the canonical config is in the contracts package, both `main.py` and the dashboard pages import from it. If it's a backend endpoint, the dashboard fetches it.

#### B. Server-Side Aggregation Everywhere (addresses DI-ISSUE-002, DI-ISSUE-003, PG-002)

4. **Every page that displays deal counts must use server-computed counts.** No client-side `deals.filter(d => d.stage === stage).length`. The backend already has `GET /api/pipeline/summary` — use it. Specifically:
   - `/hq/page.tsx` — switch from client-side counting to pipeline summary API (original Mission 3's scope)
   - `/dashboard/page.tsx` — switch from client-side counting to pipeline summary API (gap PG-002, NOT in original missions)
   - `DealBoard.tsx` — if it displays per-column counts, they must come from the server or from a single shared fetch (gap PG-003)

5. **Add `total_count` to the `/api/deals` response.** Every page that displays a deal count should use this field instead of `array.length`. This includes `/hq`, `/dashboard`, `/deals`, and any other consumer.

6. **Ensure header counts and pipeline card sums are always equal.** After this layer, the invariant `header_total == sum(displayed_stage_counts) + sum(terminal_stage_counts)` must hold on every page that shows a pipeline view.

#### C. Dashboard Page Parity (addresses PG-001 through PG-009)

7. **`DealBoard.tsx` — add missing stages (PG-003).** The Kanban board currently shows only 6 of 9 stages. After this layer:
   - All pipeline stages from the canonical config are rendered as columns
   - `portfolio` is visible (it's a real active pipeline stage with deals in it)
   - Terminal stages (`archived`, `junk`) are either shown as a separate section below the pipeline columns or are explicitly excluded with a clear rationale documented in the ADR. The operator's Decision 4 (from MASTER doc Section 3) applies here.

8. **`/deals` page — fix filter and display (PG-005, PG-006).** After this layer:
   - The status filter dropdown reflects meaningful user-facing states (not raw DB column values)
   - `'archived'` is an available filter option
   - The "Delete" button label accurately reflects its action (if it archives, label it "Archive")
   - The page uses `total_count` from the API response (not `sortedDeals.length`)

9. **`/deals/[id]` page — archived deal visual design (PG-008).** After this layer:
   - The status badge visually distinguishes archived deals from active deals (distinct color, icon, or styling)
   - The stage transition UI correctly shows "No transitions available" for archived deals (verify `state_machine.allowed_transitions` returns empty)

10. **`/actions` page — archived deal context (PG-007 partial).** After this layer:
    - When viewing actions for an archived deal, there is a visual indicator that the referenced deal is archived

#### D. Cross-Service Parity (addresses CS-001 through CS-005, Constraint Q5)

11. **Agent API compatibility audit.** Read the Agent API's deal-related queries and endpoints. Verify that:
    - Its deal listing queries are compatible with the new lifecycle model from Layer 2
    - It does not have its own independent understanding of deal states that contradicts the backend
    - If it has pipeline or stats endpoints, they align with the canonical stage configuration
    - Fix any incompatibilities found

12. **RAG/LLM service — re-index after backfill (CS-003, Constraint Q5).** After Layer 2's backfill changes deal data:
    - Trigger a re-index in the RAG service so that embeddings and search indexes reflect the updated deal states
    - Verify that the RAG service's deal queries are compatible with the new data model
    - Document the re-index process

13. **Contract sync (CS-004, Constraint Q6).** After ALL code changes in this layer:
    - Run `make update-spec` (fetches live backend OpenAPI spec)
    - Run `make sync-all-types` (regenerates `api-types.generated.ts` and `backend_models.py`)
    - Verify `make validate-local` passes
    - If any generated type has changed, verify that consuming code still compiles and passes type-checking

#### E. `v_pipeline_summary` View Verification (CS-005)

14. **Verify the pipeline summary view.** After Layer 2's backfill and any Layer 3 changes to the view:
    - Capture the view's output and confirm it matches expectations
    - Confirm that `GET /api/pipeline/summary` returns correct counts
    - Confirm that the sum of all stage counts in the response equals the total active deals count
    - If the view definition needs updating (e.g., to support the new lifecycle model), update it

### OUT OF SCOPE

- Error handling / Promise.allSettled changes (Layer 4)
- Test creation (Layer 5)
- Governance documents (Layer 6)
- Any new feature development — this layer only ensures existing features display correct, consistent data

## Dependencies

Layer 2 must be COMPLETE. The data model must be finalized, the backfill must be done, and the archive/restore endpoints must be working correctly.

## Exit Gates

| Gate | Success Criteria | Evidence Required |
|------|-----------------|-------------------|
| GATE L3-1 | A canonical stage configuration exists in a single location | File path and contents of the stage config; proof that it defines all stages with display properties |
| GATE L3-2 | ZERO hardcoded stage arrays exist in the dashboard codebase | Search results across the entire dashboard `src/` directory showing no hardcoded stage lists |
| GATE L3-3 | Every dashboard page that shows deal counts uses server-computed counts (not client-side filtering) | Code review evidence for: `/hq`, `/dashboard`, `DealBoard`, `/deals` |
| GATE L3-4 | `DealBoard.tsx` renders columns for ALL pipeline stages including `portfolio` | Capture of the DealBoard column list |
| GATE L3-5 | `/deals` page filter includes 'archived' as an option and the "Delete" button is correctly labeled | Code evidence showing updated filter options and button labels |
| GATE L3-6 | `/deals/[id]` page visually distinguishes archived deals from active deals | Code evidence showing distinct styling for archived status |
| GATE L3-7 | Agent API's deal queries are verified compatible with the new lifecycle model | Audit results documenting each Agent API deal query and its compatibility status |
| GATE L3-8 | RAG service has been re-indexed after the Layer 2 backfill | Evidence of re-index execution and verification that search results reflect updated deal states |
| GATE L3-9 | `make sync-all-types` has been run and passes (Constraint Q6) | Terminal output of the sync command |
| GATE L3-10 | `make validate-local` passes after all Layer 3 changes | Terminal output of the validation command |
| GATE L3-11 | `GET /api/pipeline/summary` returns counts that sum correctly | API response showing `sum(stage_counts) == total` |
| GATE L3-12 | **THE PARITY TEST:** Pick any two surfaces that display deal data. They show the same total count, the same stage breakdown, and the same list of stages. | Evidence from at least 3 surface pairs: (a) /hq vs /dashboard, (b) /deals table vs DealBoard, (c) API pipeline/summary vs /hq header |

## Risk & Rollback

**Primary risk:** Changing 5+ dashboard pages simultaneously creates many potential regressions.

**Mitigation:** Each page change is independently verifiable. The parity test (Gate L3-12) catches any inconsistency.

**Rollback procedure (Constraint Q3):**
1. Dashboard changes are UI-only (except contract sync) — git revert the dashboard commits
2. Contract sync is regenerative — running `make sync-all-types` after revert restores previous types
3. Agent API and RAG changes (if any) are independently revertible
4. **CRITICAL:** If Layer 2 needs rollback after Layer 3, Layer 3 must be rolled back FIRST

## "Never Again" Enforcement

- **Canonical stage config:** Adding a new stage means updating ONE file — the config. Every surface inherits it.
- **Server-side aggregation:** Client-side counting is eliminated. Counts can only drift if the server changes.
- **Contract sync as mandatory gate:** Generated types are always in sync with the API
- **Layer 5 will add:** Parity test in CI that hits multiple surfaces and compares counts; contract drift detector

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYER 4: DEFENSIVE ARCHITECTURE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Objective

Individual component failures must not cascade into system-wide failures. Every page that fetches multiple data sources must handle partial failures gracefully. A quarantine API outage does not blank the pipeline view. Every API endpoint either works correctly or does not exist.

**This layer can begin in parallel with Layer 3.** It does not depend on Layer 3's specific data changes — it addresses the structural fragility of how data is fetched and displayed.

## Scope

### IN SCOPE

#### A. Promise.all → Promise.allSettled Everywhere (addresses DI-ISSUE-005, PG-001, PG-004, PG-007)

1. **Identify EVERY page in the dashboard that uses `Promise.all` for data fetching.** The strategic review found 4:
   - `/hq/page.tsx` — 4 parallel fetches (line 38-46) — original Mission 4 scope
   - `/dashboard/page.tsx` — 5 parallel fetches (line 83-89) — gap PG-001
   - `/deals/[id]/page.tsx` — 7 parallel fetches (line 132-140) — gap PG-004
   - `/actions/page.tsx` — 3 parallel fetches (line 184) — gap PG-007

   Search the entire dashboard codebase for any other `Promise.all` used for data fetching. Every instance must be converted.

2. **For each page, implement graceful degradation:**
   - Replace `Promise.all` with `Promise.allSettled` (or equivalent pattern)
   - Each data source has its own error handling — a failed fetch returns a typed empty/error state, not an exception
   - The page renders what it can and shows a specific failure indicator for what it cannot ("Failed to load quarantine data", "Agent activity unavailable")
   - No page goes entirely blank under any single-endpoint failure scenario

3. **Add individual try/catch to every API fetcher function** that does not already have one. The MASTER doc notes that `getAgentActivity` has try/catch but `getQuarantineQueue` and `getKineticActions` do not. Audit every function in `api.ts` and `api-client.ts`.

#### B. API Schema Hardening (addresses DI-ISSUE-005 Factor B)

4. **Fix the agent activity schema mismatch.** `/api/agent/activity` sometimes returns `[]` (empty array) instead of the expected object. Either:
   - Fix the upstream service to always return a typed object
   - Or update the schema and parsing to handle both shapes gracefully
   - The root cause must be identified: is the mismatch in the Agent API service itself (port 8095) or in the Next.js proxy route handler? Fix at the source.

5. **Fix the quarantine endpoint instability (DI-ISSUE-005 Factor C).** `getQuarantineQueue` calls `/api/actions/quarantine` without error handling. Add proper try/catch and a typed fallback state.

#### C. Dead Endpoint Resolution (addresses DI-ISSUE-009)

6. **Fix or remove `/api/actions/kinetic`.** This endpoint returns HTTP 500. Either:
   - Fix the implementation so it returns a valid response
   - Or remove the endpoint entirely if it is deprecated
   - If removed: remove all references to it in the codebase, update the OpenAPI spec
   - No endpoint in the platform should return 500 under normal operation

7. **Audit ALL API endpoints for unexpected error responses.** The evidence file `api-stats-endpoints.txt` documents known endpoint statuses. Verify every documented endpoint returns a valid response. Document any that return 404, 405, or 500 and either fix or remove them.

#### D. Per-Widget Error Boundaries (industry best practice from DI-ISSUE-005)

8. **Add React error boundaries around major page sections.** Each independent data section of a page should be wrapped in an error boundary so that a rendering crash in one section does not take down the entire page. Priority pages:
   - `/hq` — pipeline section, agent activity section, quarantine section
   - `/dashboard` — pipeline funnel, action strip, alerts section
   - `/deals/[id]` — deal info, events timeline, case file, enrichment, materials, actions tabs

### OUT OF SCOPE

- Data model changes (Layer 2)
- Stage configuration or count logic changes (Layer 3)
- Test creation (Layer 5)

## Dependencies

Layer 2 must be COMPLETE (data model finalized). Layer 3 can run in parallel — the defensive architecture changes are structural and do not depend on which specific data is displayed.

## Exit Gates

| Gate | Success Criteria | Evidence Required |
|------|-----------------|-------------------|
| GATE L4-1 | ZERO instances of `Promise.all` for data fetching remain in the dashboard | Search results across the entire dashboard showing no data-fetching `Promise.all` patterns |
| GATE L4-2 | `/hq` renders pipeline data even when quarantine API returns an error | Evidence of: stopping or blocking the quarantine endpoint, loading /hq, seeing pipeline data with quarantine section showing failure state |
| GATE L4-3 | `/dashboard` renders even when one of its 5 data sources fails | Evidence of: blocking one endpoint, loading /dashboard, seeing partial rendering with failure indicator |
| GATE L4-4 | `/deals/[id]` renders deal info even when enrichment or materials endpoints fail | Evidence of: blocking one non-critical endpoint, loading a deal page, seeing deal info with failed sections indicated |
| GATE L4-5 | `/actions` renders even when one of its data sources fails | Same pattern as above |
| GATE L4-6 | Agent activity endpoint returns a consistent shape (always object, never array) | API response evidence showing typed object response; code evidence showing the fix |
| GATE L4-7 | `/api/actions/kinetic` no longer returns 500 (either fixed or removed) | API response evidence showing valid response or 404 if removed |
| GATE L4-8 | Zero Zod validation errors in browser console on any dashboard page under normal operation | Browser console evidence from: /hq, /dashboard, /deals, /deals/[id], /actions |
| GATE L4-9 | Error boundaries exist around major page sections | Code evidence showing ErrorBoundary components wrapping independent sections |
| GATE L4-10 | **THE RESILIENCE TEST:** For each dashboard page that fetches multiple data sources, systematically fail each source one at a time. The page must never go entirely blank. | Evidence table: page × failed-source → rendering result (partial vs blank) |

## Risk & Rollback

**Primary risk:** Changing fetch patterns across 4+ pages could introduce subtle rendering bugs.

**Mitigation:** Each page change is independently testable. The resilience test (Gate L4-10) provides systematic verification.

**Rollback:** All changes are frontend-only (except the agent activity schema fix if in the Agent API). Git revert the dashboard commits. The platform returns to its current behavior (fragile but functional under happy-path conditions).

## "Never Again" Enforcement

- **Code pattern:** All data-fetching pages use the graceful degradation pattern — this becomes the team standard
- **Error boundaries:** Component crashes are isolated by design
- **Layer 5 will add:** Automated failure simulation tests that verify resilience under partial outage

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYER 5: VERIFICATION & OBSERVABILITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Objective

Create the safety net that prevents the next DEAL-INTEGRITY incident. Codify every invariant from Layers 1-4 as automated tests. Establish production monitoring that detects drift in real time. Capture performance baselines. Make regression invisible no more.

## Scope

### IN SCOPE

#### A. Automated Test Suite (Constraint Q4)

Every "Never Again" enforcement mechanism listed in the MASTER document (Sections under each DI-ISSUE) must become an actual, runnable test. Nothing listed remains unwritten.

1. **Lifecycle transition tests** (from DI-ISSUE-001 "Never Again"):
   - After archiving: `GET /api/deals?status=active` must NOT return the archived deal
   - After archiving: `GET /api/deals?status=archived` MUST return the deal
   - After restoring: deal returns to active state with all fields correct
   - Attempting an invalid state transition is rejected
   - Concurrent archive + restore resolves consistently

2. **Pipeline count invariant tests** (from DI-ISSUE-002, 003 "Never Again"):
   - `sum(stage_counts)` from pipeline summary equals `total_active_deals`
   - API deal count matches DB deal count
   - Pipeline summary endpoint and deals listing endpoint agree on totals

3. **Contract schema tests** (from DI-ISSUE-005 "Never Again", Constraint Q6):
   - Zod schemas in the dashboard validate successfully against actual API endpoint responses
   - Run against live endpoints (or CI fixtures from test DB)
   - `/api/agent/activity` response matches `AgentActivityResponseSchema`
   - Every endpoint's actual response shape matches its OpenAPI spec

4. **Startup self-check tests** (from DI-ISSUE-006 "Never Again"):
   - Backend health endpoint reports correct DB identity
   - Backend refuses to start with wrong DSN (verify the startup gate from Layer 1)

5. **E2E flow tests** (from DI-ISSUE-007 "Never Again"):
   - Create deal → verify it appears in `/deals`, `/hq`, `/dashboard`, `DealBoard`, and pipeline summary
   - Archive deal → verify it disappears from active views and appears in archived views
   - Restore deal → verify it returns to active views
   - Full quarantine → deal creation → pipeline visibility flow

6. **API health suite** (from DI-ISSUE-009 "Never Again"):
   - Every documented API endpoint returns a non-500 response
   - Every route handler has at least one test

7. **Schema/code parity test** (from DI-ISSUE-008 "Never Again"):
   - Every SQL column reference in the backend code maps to a real column in the database schema
   - No dead column references exist

8. **Failure resilience tests** (from Layer 4):
   - For each dashboard page, simulate failure of each data source
   - Verify the page renders partially (not blank)
   - Verify no Zod errors in console under any failure scenario

#### B. CI Gates

9. **Contract sync gate:** `make validate-local` runs on every PR and blocks merge on failure. This includes the contract surface validation that ensures generated types match OpenAPI specs.

10. **Pipeline invariant gate:** CI runs the pipeline count invariant test. If `sum(stage_counts) != total_active_deals`, the build fails.

11. **Lifecycle invariant gate:** CI runs the lifecycle transition tests. If an impossible state is creatable through the API, the build fails.

12. **Schema drift gate:** CI runs Zod schemas against API response fixtures. If a schema drifts from the actual response shape, the build fails.

#### C. Performance Baselines (Constraint Q9)

13. **Profile critical queries before and after the mission changes:**
    - `v_pipeline_summary` view query — capture execution plan and timing
    - Deals listing query with status filter — capture execution plan and timing
    - Pipeline summary endpoint — capture response time
    - Deals listing endpoint — capture response time

14. **Verify indexes exist for critical query patterns:**
    - Index on `(deleted, status, stage)` or equivalent for the pipeline summary view
    - Index on `(status)` for the deals listing filter
    - If indexes are missing, add them

15. **Document performance baselines** in the evidence directory. These become the reference for future performance monitoring.

#### D. Production Observability (Constraint Q2)

16. **Health endpoints:** Every service must have a health endpoint that reports:
    - Service name and version
    - Database connection status (host, port, dbname)
    - Current deal count invariant: `total_deals`, `active_deals`, `archived_deals`, `deleted_deals`
    - Uptime

17. **Structured logging for state transitions:** Every call to the centralized transition function (from Layer 2) must produce a structured log entry with: deal ID, previous state, new state, operator/caller identity, timestamp.

18. **Count invariant monitoring:** Implement a mechanism (health check, scheduled job, or monitoring endpoint) that periodically verifies `sum(stage_counts) == total_active_deals` and alerts if the invariant is violated. The implementation can be as simple as a health check endpoint that returns `invariant_holds: true/false`.

### OUT OF SCOPE

- Implementing new features
- Grafana/Prometheus setup (unless the team already has it — in that case, add alerts)
- Load testing or stress testing

## Dependencies

Layers 3 and 4 must BOTH be COMPLETE. The tests verify the work done in those layers.

## Exit Gates

| Gate | Success Criteria | Evidence Required |
|------|-----------------|-------------------|
| GATE L5-1 | Every "Never Again" test from the MASTER document exists as a runnable test | Test file listing with mapping to MASTER document enforcement items |
| GATE L5-2 | All lifecycle transition tests pass | Test execution output |
| GATE L5-3 | All pipeline count invariant tests pass | Test execution output |
| GATE L5-4 | All contract schema tests pass | Test execution output |
| GATE L5-5 | All E2E flow tests pass (create → verify → archive → verify → restore → verify) | Test execution output |
| GATE L5-6 | API health suite passes — every documented endpoint returns non-500 | Test execution output |
| GATE L5-7 | `make validate-local` passes | Terminal output |
| GATE L5-8 | Performance baselines are captured for critical queries and endpoints | Evidence files with query plans and response times |
| GATE L5-9 | Indexes exist for critical query patterns | DB schema evidence showing index definitions |
| GATE L5-10 | Health endpoints on all services report DB identity and deal count invariants | Health endpoint responses from Backend, Agent API, and any other service with a health endpoint |
| GATE L5-11 | State transition logging is active — archiving a deal produces a structured log entry | Log output showing a test state transition |
| GATE L5-12 | Count invariant monitoring is implemented and returns a correct result | Monitoring endpoint or health check response showing `invariant_holds: true` |

## Risk & Rollback

**Primary risk:** Tests may reveal issues in Layers 1-4 that were not caught by their exit gates. This is a feature, not a risk — it's exactly why this layer exists.

**Mitigation:** If tests reveal issues, fix the issues in the appropriate layer before proceeding. Do not skip failing tests.

**Rollback:** Tests and monitoring are additive — they can be removed without affecting platform functionality. However, removing them removes the safety net. Rollback is not recommended.

## "Never Again" Enforcement

This layer IS the "Never Again" enforcement for the entire mission. If this layer is complete and all gates pass, the platform has automated protection against recurrence of every issue found in the DEAL-INTEGRITY-001 investigation.

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LAYER 6: GOVERNANCE & EVOLUTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Objective

Address the organizational root cause — why four independent decisions about shared data semantics with no coordination mechanism produced a system with phantom states and split-brain data. Establish the processes and documents that make this pattern impossible to repeat.

**This layer can begin in parallel with Layer 5.** The governance documents can be drafted as soon as the technical decisions in Layer 2 are finalized.

## Scope

### IN SCOPE

#### A. Architecture Decision Records (ADRs) (Constraint Q10)

1. **ADR-001: Deal Lifecycle State Machine Design.** Document:
   - The decision made in Layer 2 (which option was chosen and why)
   - The valid deal states and the valid transitions between them
   - How the centralized transition function works
   - Why the three-field system (status/stage/deleted) exists and how it is now coordinated (or replaced)
   - What constraints exist at the DB level
   - Consequences: what this decision means for future development

2. **ADR-002: Single Canonical Database.** Document:
   - Why the split-brain existed and how it was resolved
   - The canonical DSN and how services discover it
   - The startup gate that prevents drift
   - Consequences: no secondary databases, no local Postgres for testing (use the canonical container)

3. **ADR-003: Pipeline Stage Configuration Authority.** Document:
   - Where the canonical stage configuration lives
   - How stages are added, modified, or removed
   - What happens when the config changes (which files/services are affected)
   - Consequences: adding a stage is a defined process, not an ad-hoc code change

#### B. Runbook: "How to Add a New Deal Stage" (Constraint Q10)

4. **Create a runbook** that a new engineer can follow to add a deal stage to ZakOps. This runbook must cover:
   - Update the canonical stage configuration (file path, format)
   - Update the database CHECK constraint (if stages are constrained)
   - Update the centralized transition function (if the new stage has transitions)
   - Run `make sync-all-types` to regenerate types
   - Run `make validate-local` to verify
   - Verify all dashboard pages render the new stage
   - Verify the pipeline summary includes the new stage
   - Update tests to cover the new stage
   - The runbook must be testable — following it produces a working result

#### C. Innovation Roadmap

5. **Catalogue the 34 innovation ideas from the MASTER document** into a prioritized roadmap. For each idea:
   - Current status: implemented (during this mission), deferred, or out of scope
   - Priority: P1 (next quarter), P2 (future), P3 (nice to have)
   - Dependencies: what must exist first
   - Estimated effort: S/M/L

   The roadmap does not need to be executed — it needs to exist as a reference so that good ideas are not lost.

#### D. Change Protocol for Deal State Modifications

6. **Establish a PR checklist or CI check** that triggers when files related to deal state are modified. When a PR modifies:
   - The centralized transition function
   - The stage configuration
   - Any endpoint that changes deal state
   - The database schema for the deals table

   The checklist must require: review of the ADRs, verification of stage config consistency, `make sync-all-types`, and `make validate-local`.

### OUT OF SCOPE

- Implementing innovation ideas (they are catalogued, not executed)
- Organizational process changes outside the engineering team
- Hiring or team structure changes

## Dependencies

Layer 2 must be COMPLETE (the technical decisions must be finalized before they can be documented). Layers 3, 4, 5 should be complete or nearly complete (the full picture must be known before the runbook is accurate).

## Exit Gates

| Gate | Success Criteria | Evidence Required |
|------|-----------------|-------------------|
| GATE L6-1 | ADR-001 (Lifecycle State Machine) exists and accurately describes the Layer 2 implementation | ADR file reviewed for accuracy against actual implementation |
| GATE L6-2 | ADR-002 (Canonical Database) exists and accurately describes the Layer 1 implementation | ADR file reviewed for accuracy |
| GATE L6-3 | ADR-003 (Stage Configuration Authority) exists and accurately describes the Layer 3 implementation | ADR file reviewed for accuracy |
| GATE L6-4 | **THE RUNBOOK TEST:** A new-engineer simulation — follow the "How to Add a New Deal Stage" runbook with a test stage. Verify the test stage appears on all surfaces, passes all tests, and can be removed cleanly. | Evidence of: (a) adding a test stage following the runbook, (b) verifying it appears everywhere, (c) removing it cleanly |
| GATE L6-5 | Innovation roadmap exists with all 34 ideas catalogued and prioritized | Roadmap file with complete mapping to MASTER document Appendix |
| GATE L6-6 | Change protocol exists (checklist or CI trigger) for deal state modifications | Description of the protocol; evidence that it triggers on relevant file changes |

## Risk & Rollback

**Risk:** Documentation becomes stale if not maintained. The ADRs and runbook are only valuable if they are updated when the system changes.

**Mitigation:** The change protocol (Gate L6-6) acts as a trigger — when deal state files change, the checklist reminds engineers to update documentation.

**Rollback:** Documentation is additive. Removing it has no technical impact on the platform. However, removing it removes the organizational safeguard against repeating the pattern that caused DEAL-INTEGRITY-001.

## "Never Again" Enforcement

This layer IS the organizational "Never Again" enforcement. Code gates (Layers 1-5) prevent specific bugs from recurring. Governance (Layer 6) prevents the pattern — independent decisions about shared data semantics — from recurring.

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MISSION-WIDE RULES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Autonomy Rules

1. **If something is broken → fix it.** Do not stop to ask unless genuinely blocked.
2. **If something is missing → create it.** If a backend endpoint doesn't exist, create it. If a test framework isn't set up, set it up.
3. **Adapt to what you find.** The codebase may have changed since the audit. File paths may differ. Use the evidence and descriptions to find the correct locations.
4. **Deferred items are documented, not hidden.** If an item proves impractical at a given layer, document it in the completion report with the reason. Never silently skip.
5. **Contract surfaces are non-negotiable.** Any new backend endpoint needs `response_model` in FastAPI. Any schema change triggers the appropriate `make sync-*` target. Any API response shape change requires `make update-spec` followed by `make sync-all-types`.

## Verification Protocol

Every layer uses the same two-pass verification:

1. **Builder self-verification:** After completing all items in a layer, the builder systematically verifies every exit gate. Capture evidence. Document results.
2. **Second-pass confirmation:** Re-verify each gate from scratch (not by reviewing the first pass, but by re-running the actual checks). Any discrepancy between passes must be investigated and resolved.

This double-verification protocol prevents "works on first try, missed an edge case" failures.

## Completion Report Format

Each layer produces a completion report at:
`/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-UNIFIED/layer-N/completion-report.md`

Format:

```
# LAYER [N]: [NAME] — COMPLETION REPORT

## Timestamp
[ISO 8601]

## Status
[COMPLETE / PARTIAL — if partial, list remaining items]

## Gate Results

| Gate | Result | Evidence Location |
|------|--------|-------------------|
| L[N]-1 | PASS/FAIL | path/to/evidence |
| ... | ... | ... |

## Items Completed
[List of every scope item completed with brief description]

## Items Deferred (if any)
[List with reason for each deferral]

## Issues Discovered During Execution
[Anything found that was not in the original audit]

## Dependencies Verified
[Confirmation that prerequisite layers are still healthy]

## Second-Pass Confirmation
[Results of the second verification pass — any discrepancies noted and resolved]
```

## Final Verification

After ALL six layers are complete, produce a final verification report at:
`/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-UNIFIED/final-verification.md`

This report must:
1. Confirm every DI-ISSUE (001-009) is fully resolved with evidence
2. Confirm every dashboard page-level gap (PG-001 through PG-009) is resolved
3. Confirm every cross-stack gap (CS-001 through CS-005) is resolved
4. Confirm all 10 mandatory platform constraints (Q1-Q10) are satisfied
5. Run `make validate-local` one final time and capture the result
6. Run the full test suite and capture the result
7. State the mission outcome: COMPLETE or PARTIAL with remaining items

## Hard Rules

1. **No layer may be skipped.** Even if a layer seems "already done" — verify with evidence.
2. **No gate may be marked PASS without evidence.** "It should work" is not evidence.
3. **No silent skips.** Every scope item is either completed with evidence, or deferred with a documented reason.
4. **Generated files are never manually edited.** `api-types.generated.ts` and `backend_models.py` are regenerated via the sync pipeline, never hand-edited.
5. **CRLF hazard (WSL environment).** Every shell script written must have `sed -i 's/\r$//'` applied. Every file created under `/home/zaks/` must have ownership corrected with `chown zaks:zaks`.
6. **Port 8090 is FORBIDDEN.** Legacy, decommissioned. Never reference it.
7. **The `zakops` database uses schema `zakops`, NOT `public`.** User is `zakops`, NOT `dealengine`.
8. **The Redocly ignore ceiling is 57.** Do not add new ignores unless one is removed first.
9. **Rolling back a layer requires rolling back all layers above it first.** The dependency chain is: 1 → 2 → 3 → 5, with 4 parallel to 3 and 6 parallel to 5.
10. **This mission fixes the platform. It does not add new features.** Every change must trace back to a DI-ISSUE, a PG gap, a CS gap, or a mandatory constraint (Q1-Q10).

## Pipeline Master Log Entry

Upon mission completion, append to `/home/zaks/bookkeeping/docs/DEAL-INTEGRITY-001_PIPELINE_MASTER_LOG.md`:

```
[TIMESTAMP] | UNIFIED MISSION COMPLETE | Agent=[agent] | RunID=[id] | STATUS=[COMPLETE/PARTIAL] | 6 layers executed | [N] gates passed | [N] tests created | Report=/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-UNIFIED/final-verification.md
```

---

## WORLD-CLASS CRITERIA CHECKLIST

At the end of this mission, all of the following must be true:

- [ ] Single canonical DB truth — one database, every service connected, verified at startup
- [ ] Full lifecycle state machine — no impossible states at the DB level, single transition function
- [ ] All surfaces show the same counts — any two surfaces displaying deal data agree
- [ ] Agent API + RAG + Contracts included — not just UI/backend
- [ ] Defensive UI architecture — partial failures do not cascade
- [ ] CI gates + regression tests — breaking an invariant fails the build
- [ ] Observability with alerts and invariant monitors — drift is detected in real time
- [ ] Governance with ADRs and runbooks — a new engineer can add a stage by following one document
- [ ] Performance baselined — critical queries profiled and indexed
- [ ] Concurrency safe — simultaneous operations cannot produce impossible states
- [ ] Backfill reversible — every data change can be undone
- [ ] Contract sync enforced — generated types are never stale
- [ ] Zero hardcoded stage lists — one canonical configuration drives everything
- [ ] Zero Zod errors under any failure scenario — schemas match reality
- [ ] Innovation roadmap catalogued — 34 ideas preserved and prioritized for future work

---

**END OF MISSION PROMPT**

**One Sentence:** The original 5 missions asked "how do we fix what's broken?" This mission asks "how do we build a platform where this class of problem cannot occur?"
