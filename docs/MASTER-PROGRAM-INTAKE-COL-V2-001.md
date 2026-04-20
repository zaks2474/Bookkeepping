# MASTER PROGRAM: ZAKOPS-INTAKE-COL-V2-001
## Intake Readiness + COL-V2 Intelligence Platform Build
## Date: 2026-02-13
## Classification: Platform Build + Service Integration + Pipeline Hardening
## Prerequisite: TriPass Forensic Audit (TP-20260213-163446) + COL-V2 QA Verification (19 missions, 516 gates)
## Successor: QA-MASTER-PROGRAM-VERIFY-001
## Standard: Mission Prompt Standard v2.2

---

## Program Overview

This master program unifies two convergent workstreams into a single, ordered execution plan:

1. **Intake Readiness** — Harden the Intake → Quarantine → Deals pipeline based on 17 forensic findings from the TriPass audit, prepare for LangSmith shadow-mode integration, and decommission all legacy shadow-truth paths.
2. **COL-V2 Intelligence Build** — Build and wire 69 remaining actionable items from the COL-V2 QA verification sweep: core service wiring, intelligence services, ambient UI, and compliance infrastructure.

The program is split into **4 sub-missions** executed sequentially. Each sub-mission is independently executable via Lab Loop or manual session and produces a completion report before the next sub-mission begins.

**Non-negotiable principle:** Intake Readiness (SM-1) is the FOUNDATION. The COL-V2 intelligence work (SM-2 through SM-4) builds ON TOP of a proven, hardened pipeline. SM-1 must achieve all 7 readiness gates before SM-2 begins.

---

## Sub-Mission Index & Dependency Chain

| # | Mission ID | Focus | Items | Complexity | Prerequisite |
|---|-----------|-------|-------|-----------|--------------|
| SM-1 | INTAKE-READY-001 | Pipeline hardening + shadow-mode readiness | 17 findings + 7 gates | L | TriPass audit complete |
| SM-2 | COL-V2-CORE-001 | Core wiring + service completion + compliance foundation | ~35 items | XL | SM-1 PASS |
| SM-3 | COL-V2-INTEL-001 | Reflexion + cognitive + RAG + agent architecture | ~15 items | L | SM-2 PASS |
| SM-4 | COL-V2-AMBIENT-001 | Ambient intelligence UI + compliance pipeline | ~19 items | XL | SM-3 PASS |

```
SM-1 (INTAKE-READY-001) ─── Foundation. 17 forensic fixes + shadow mode.
    │
    ▼
SM-2 (COL-V2-CORE-001) ─── Wire services into hardened pipeline.
    │
    ▼
SM-3 (COL-V2-INTEL-001) ── Intelligence services on wired core.
    │
    ▼
SM-4 (COL-V2-AMBIENT-001) ── UI surfaces + compliance on intelligence.
    │
    ▼
QA-MASTER-PROGRAM-VERIFY-001 (successor)
```

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash or context compaction, run:

```bash
# 1. Determine current sub-mission and phase
cat /home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md

# 2. Check validation state
cd /home/zaks/zakops-agent-api && make validate-local

# 3. Check for partial work
git -C /home/zaks/zakops-agent-api status
git -C /home/zaks/zakops-backend status
git -C /home/zaks/Zaks-llm status
```

Resume from the checkpoint file. Do not re-execute completed phases or sub-missions.

---

## Context Checkpoint Protocol
<!-- Adopted from Improvement Area IA-1, IA-7 -->

This is an XL multi-session program. After completing **each phase**, write a structured checkpoint:

```bash
cat > /home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md << 'CHECKPOINT'
Program: ZAKOPS-INTAKE-COL-V2-001
Current sub-mission: SM-{N} ({MISSION-ID})
Last completed phase: Phase {N}
Next phase: Phase {N+1}
Validation state: {PASS/FAIL + details}
Open decision trees: {any unresolved forks}
Files modified this session: {list}
CHECKPOINT
```

**CONTEXT SAVE POINTS:** After SM-1 Phase 3, after SM-2 Phase 2, after SM-3 Phase 2, after SM-4 Phase 2. At these points, commit intermediate work and update checkpoint if context is constrained.

---

## Program-Level Context

### Source 1: TriPass Forensic Audit (TP-20260213-163446)

The 3-agent forensic audit produced **17 deduplicated findings** (F-1 through F-17) covering the Intake → Quarantine → Deals pipeline:

| Severity | Count | Key Findings |
|----------|-------|-------------|
| P0 | 5 | MCP endpoint mismatch (F-1), missing ingestion automation (F-2), quarantine dedup gap (F-3), agent DB config drift (F-4), legacy filesystem shadow truth (F-5) |
| P1 | 6 | FSM/outbox bypass (F-6), dead email settings proxy (F-7), correlation ID fragmentation (F-8), idempotency schema bug (F-9), bulk-delete route gap (F-10), retention cleanup column bug (F-13) |
| P2 | 4 | Quarantine status constraint (F-11), DDL default stage (F-12), transition matrix duplication (F-14), attachment linkage (F-16) |
| P3 | 2 | Agent contract docstring drift (F-15), OAuth in-memory state (F-17) |

Full report: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/FINAL_MASTER.md`

### Source 2: COL-V2 Actionable Items Register (Revised)

The 19-mission QA verification (516 gates) identified 83 actionable items. A deep backend audit resolved 14, leaving **~69 items** (true net ~36 after accounting for backend services that only need wiring).

| Category | Original | Resolved | Remaining |
|----------|----------|----------|-----------|
| A: Backend-blocked | 8 | 8 | **0** — DealBrainService, brain router, migration 028 all exist |
| B: Completion items | 37 | 2 | **35** — B5.1 (RRF), B6.4 (Living Memo) resolved |
| C: Not-yet-started | 31 | 3 | **28** — C9 (StallPredictor), C18 (MorningBriefing), C19 (AnomalyDetector) resolved |
| D: Verification-only | 7 | 1 | **6** — D3 (RRF k=60) confirmed |

Full register: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md`

### Source 3: LangSmith Shadow-Mode Integration Strategy

LangSmith Agent Builder will serve as the email intake copilot. The integration model:
- **LangSmith** handles email parsing, intelligence, and classification
- **LangSmith injects** items into ZakOps Quarantine via `POST /api/quarantine`
- **ZakOps owns** everything from Quarantine forward (approval, promotion, lifecycle, audit trail)
- **Shadow mode first:** inject-only, no auto-promotion, humans approve within ZakOps

Source: User-provided INTAKE-READINESS addendum (2026-02-13)

### Backend Services Already Built (DO NOT Rebuild)

| Service | File | Lines | Status |
|---------|------|-------|--------|
| DealBrainService | `zakops-backend/src/core/agent/deal_brain_service.py` | 337 | Complete |
| Brain Router | `zakops-backend/src/api/orchestration/routers/brain.py` | 302 | 14 endpoints |
| StallPredictor | `zakops-backend/src/core/agent/stall_predictor.py` | 257 | Complete |
| MorningBriefingGenerator | `zakops-backend/src/core/agent/morning_briefing.py` | 202 | Complete |
| DealAnomalyDetector | `zakops-backend/src/core/agent/anomaly_detector.py` | 209 | Complete |
| LivingMemoGenerator | `zakops-backend/src/core/agent/living_memo_generator.py` | 216 | Complete |
| GhostKnowledgeDetector | `zakops-backend/src/core/agent/ghost_knowledge_detector.py` | 243 | Complete |
| MomentumCalculator | `zakops-backend/src/core/agent/momentum_calculator.py` | 319 | Complete |
| DevilsAdvocateService | `zakops-backend/src/core/agent/devils_advocate.py` | 191 | Complete |
| BottleneckHeatmap | `zakops-backend/src/core/agent/bottleneck_heatmap.py` | 181 | Complete |
| RRF Hybrid Query | `Zaks-llm/src/api/rag_rest_api.py` | — | `rrf_k=60`, `_rrf_merge()` |

---

## Glossary

| Term | Definition |
|------|-----------|
| Shadow Mode | LangSmith injects quarantine items tagged as shadow-mode; no auto-promotion; humans approve within ZakOps; measurement capture for quality vetting |
| Readiness Gate | Hard go/no-go verification that a system capability works end-to-end with evidence |
| Deal Brain | Per-deal knowledge accumulator — facts, risks, decisions, ghost knowledge, summary (S4) |
| Ghost Knowledge | Facts the user references that don't exist in the Deal Brain (QW-1) |
| Turn Snapshot | Complete capture of model input/output for a single conversational turn (S6) |
| Reflexion | Self-critique loop: generate → critique → revise (S8.3) |
| Drift Detection | Brain staleness check + contradiction detection + decay curve (S4.5) |
| HITL | Human-in-the-loop — proposals requiring user approval before execution |
| RRF | Reciprocal Rank Fusion — method for combining dense and sparse retrieval results |
| Ambient Intelligence | Background features: briefings, anomaly detection, smart paste (S17) |
| FSM | Finite State Machine — deal lifecycle state transitions via `transition_deal_state()` |
| Outbox | Transactional outbox table for reliable event delivery after deal state changes |

---

## Architectural Constraints

Per standing constraints in CLAUDE.md and contract surface discipline. Program-specific additions:

- **`transition_deal_state()` is the SINGLE choke point** for all deal state changes — no raw INSERT into deals table bypassing the workflow engine. This is the root cause of F-6 and must be enforced program-wide.
- **BackendClient is mandatory** for agent→backend calls — all calls from agent-api to backend MUST use `BackendClient` from `deal_tools.py`, never raw `httpx.AsyncClient`. Existing services using raw httpx must be migrated.
- **Fire-and-forget for non-critical paths** — brain extraction, drift detection, and snapshot writing are post-turn enrichments. They MUST NOT block the user-facing response. Use `asyncio.create_task()` with exception logging, not `await`.
- **Singleton pattern for services** — all COL-V2 services use module-level singleton instances. Preserve this pattern.
- **Spec section references in docstrings** — every COL-V2 service module MUST have a docstring citing its spec section.
- **One authoritative datastore per aggregate** — the `zakops` PostgreSQL database is the SINGLE source of truth for deals and quarantine. No filesystem stores, no duplicate SQLite DBs, no Zaks-llm shadow endpoints.
- **Idempotency as a data invariant** — DB-level UNIQUE constraints, not app-level pre-checks. Fail-closed on idempotency check failure.
- **Schema-qualified queries in multi-schema databases** — all queries to tables in the `zakops` schema MUST use `zakops.table_name`, never bare `table_name`.
- **Shadow-mode is inject-only** — LangSmith integration MUST NOT auto-promote, auto-approve, or perform autonomous lifecycle actions. Humans approve within ZakOps.
- **Admin endpoints require role check** — per S6.4/S6.5, admin endpoints verify user has ADMIN role.
<!-- Adopted from Improvement Area IA-15 -->
- **Governance surfaces** — if touching dependencies: `make validate-surface10`; if touching error handling: `make validate-surface12`; if adding tests: `make validate-surface13`.

---

## Anti-Pattern Examples

### WRONG: Raw INSERT bypassing workflow engine (F-6)
```python
await conn.execute("INSERT INTO zakops.deals (id, name, stage, ...) VALUES ($1, $2, $3, ...)", ...)
await conn.execute("INSERT INTO zakops.deal_events (...) VALUES (..., 'deal_created', ...)")
```

### RIGHT: Route through workflow engine
```python
from src.core.deals.workflow import DealWorkflowEngine
engine = DealWorkflowEngine(conn)
await engine.create_deal(deal_data)  # emits transition ledger + outbox event
```

### WRONG: App-level dedup without DB constraint (F-3)
```python
existing = await conn.fetchval("SELECT id FROM quarantine_items WHERE message_id = $1", msg_id)
if not existing:
    await conn.execute("INSERT INTO quarantine_items ...")  # race condition under concurrency
```

### RIGHT: DB-level UNIQUE + ON CONFLICT
```python
await conn.execute("""
    INSERT INTO zakops.quarantine_items (message_id, ...)
    VALUES ($1, ...)
    ON CONFLICT (message_id) DO UPDATE SET updated_at = NOW()
""", msg_id, ...)
```

### WRONG: Silent bypass on idempotency failure (F-9)
```python
try:
    cached = await check_idempotency(key)
except Exception:
    pass  # silently proceed without idempotency — data corruption risk
```

### RIGHT: Fail-closed on idempotency check failure
```python
try:
    cached = await check_idempotency(key)
except Exception as e:
    logger.error(f"Idempotency check failed: {e}")
    raise HTTPException(503, "Service temporarily unavailable — retry with same idempotency key")
```

### WRONG: Unqualified table reference in multi-schema DB (F-9)
```python
await conn.execute("SELECT * FROM idempotency_keys WHERE key = $1", key)
```

### RIGHT: Schema-qualified reference
```python
await conn.execute("SELECT * FROM zakops.idempotency_keys WHERE key = $1", key)
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Legacy `.deal-registry` removal (F-5) breaks Zaks-llm startup because endpoints are imported at module level | HIGH | Zaks-llm crashes | SM-1 Phase 1: verify Zaks-llm starts after removal; remove endpoints, not entire files |
| 2 | Quarantine approval reroute through workflow engine (F-6) changes response shape, breaking dashboard quarantine UI | MEDIUM | UI regression | SM-1 Phase 2: verify dashboard quarantine action response shapes before and after change |
| 3 | Migration adding UNIQUE on `message_id` fails because duplicates already exist in production data | HIGH | Migration blocked | SM-1 Phase 1 Decision Tree: deduplicate existing rows before adding constraint |
| 4 | Context window exhaustion — 4 sub-missions across multiple sessions | HIGH | Later phases get sloppy | IA-1/IA-7 checkpoints at every phase; commit intermediate work at save points |
| 5 | graph.py post-turn enrichment (SM-2) introduces import cycle between services | MEDIUM | Agent-api fails to start | SM-2 Phase 1 gate: `python -c "from app.core.langgraph.graph import build_graph"` |
| 6 | Raw httpx→BackendClient migration in proposal_service.py breaks existing proposal flow | MEDIUM | Proposal execution regresses | SM-2 gate: verify proposal execute endpoint still responds correctly |
| 7 | New migration collides with existing Alembic head (028_deal_brain) in zakops-backend | MEDIUM | Backend won't start | SM-1 Phase 1: check `alembic heads` before creating migration |
| 8 | Shadow-mode field addition to quarantine_items interacts with existing app-level validation | LOW | Shadow items rejected | SM-1 Phase 4: test injection with shadow-mode fields via curl before UI wiring |

---

# SUB-MISSION 1: INTAKE-READY-001

## Pipeline Hardening + LangSmith Shadow-Mode Readiness
## Classification: Pipeline Hardening + Integration Readiness
## Prerequisite: TriPass Forensic Audit TP-20260213-163446
## Successor: COL-V2-CORE-001

### Objective

**Harden the Intake → Quarantine → Deals pipeline** so that ZakOps can reliably receive externally injected opportunities (from LangSmith) and operate correctly from Quarantine forward. Fix all 17 forensic findings, prepare shadow-mode injection support, decommission legacy shadow-truth paths, and prove all 7 readiness gates with evidence.

**What this sub-mission is NOT:**
- This is NOT a COL-V2 intelligence build — no brain extraction, no reflexion, no ambient features
- This is NOT an email poller build — LangSmith handles email intelligence; we harden the receiving endpoint
- This is NOT a dashboard redesign — UI changes are limited to shadow-mode badges and quarantine action wiring

**Source material:**
- Forensic audit: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/FINAL_MASTER.md`
- Design spec: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md`

### SM-1 Phase 0 — Discovery & Baseline
**Complexity:** M
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify codebase state, establish validation baseline, inventory the 17 findings.

#### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

#### Tasks
- P0-01: **Run baseline validation** — `cd /home/zaks/zakops-agent-api && make validate-local`
  - **Checkpoint:** Must exit 0. Fix before proceeding.
- P0-02: **Verify backend is running** — `curl -sf http://localhost:8091/health`
  - **Decision Tree:**
    - **IF** running → proceed
    - **ELSE** → `cd /home/zaks/zakops-backend && docker compose up -d backend --no-deps`
- P0-03: **Check quarantine_items schema** — `psql -h localhost -U zakops -d zakops -c "\d zakops.quarantine_items"`
  - Record: which columns exist, which constraints exist, whether `message_id` has UNIQUE, whether `status` has CHECK, whether `correlation_id` exists, whether `source_type` exists.
- P0-04: **Check for existing duplicate message_ids** — `psql -h localhost -U zakops -d zakops -c "SELECT message_id, COUNT(*) FROM zakops.quarantine_items GROUP BY message_id HAVING COUNT(*) > 1"`
  - Record count. If duplicates exist, Phase 1 must deduplicate before adding UNIQUE constraint.
- P0-05: **Verify MCP server state** — `grep -n '/review\|/process' /home/zaks/zakops-backend/mcp_server/server.py`
  - Confirm F-1 is still present (lines 311, 341 reference `/review`).
- P0-06: **Verify Zaks-llm shadow endpoints** — `grep -n '.deal-registry' /home/zaks/Zaks-llm/src/api/server.py`
  - Record line numbers for F-5 removal.
- P0-07: **Check latest Alembic head** — `cd /home/zaks/zakops-backend && python -m alembic heads 2>/dev/null || ls db/migrations/ | tail -3`
  - Record head revision. New migrations must descend from it.
- P0-08: **Write checkpoint**

#### Gate P0
- `make validate-local` passes
- Backend health check returns 200
- Quarantine schema recorded
- Duplicate message_id count recorded

---

### SM-1 Phase 1 — P0 Critical Fixes (F-1, F-3, F-4, F-5)
**Complexity:** L
**Estimated touch points:** 6–10 files across 3 repos

**Purpose:** Fix the 5 highest-severity findings that directly compromise pipeline integrity.

#### Blast Radius
- **Services affected:** zakops-backend (8091), Zaks-llm (8052), agent-api config
- **Pages affected:** None directly
- **Downstream consumers:** MCP server, quarantine ingestion, agent-api startup

#### Tasks
- P1-01: **Fix F-1 — MCP endpoint mismatch** — Change `/review` to `/process` in two lines of `/home/zaks/zakops-backend/mcp_server/server.py` (lines 311, 341).
  - **Checkpoint:** `grep '/review' /home/zaks/zakops-backend/mcp_server/server.py | grep -v '#'` returns zero matches.

- P1-02: **Fix F-3 — Quarantine dedup constraint**
  - **Decision Tree:**
    - **IF** Phase 0 found duplicate message_ids → deduplicate first: keep the newest row per message_id, delete older duplicates
    - **THEN** → create migration adding UNIQUE constraint on `zakops.quarantine_items(message_id)`
  - Target: `/home/zaks/zakops-backend/db/migrations/029_quarantine_hardening.sql` (new file)
  - Include `ON CONFLICT (message_id)` update semantics in the quarantine INSERT path at `main.py:1508`.

- P1-03: **Fix F-4 — Agent DB config drift** — In `/home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml`, change agent-api `DATABASE_URL` from `zakops` to `zakops_agent`.
  - **Checkpoint:** `grep 'DATABASE_URL.*zakops[^_]' /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml` returns zero matches.

- P1-04: **Fix F-5 — Legacy filesystem shadow truth**
  - Phase A: In `/home/zaks/Zaks-llm/src/api/server.py`, remove or disable the `/api/deals` and `/api/quarantine` endpoints that read from `.deal-registry` (around lines 701, 794). Replace with 410 Gone or redirect to canonical backend.
  - Phase B: In `/home/zaks/zakops-backend/src/workers/actions_runner.py`, remove `.deal-registry` filesystem path references. In `/home/zaks/zakops-backend/src/actions/memory/store.py`, remove SQLite path references.
  - Phase C: In `/home/zaks/zakops-backend/src/core/database/adapter.py`, remove dual-write adapter code.
  - **Checkpoint:** `rg ".deal-registry" --type py /home/zaks/zakops-backend/src/ /home/zaks/Zaks-llm/src/ | grep -v test | grep -v '#'` returns zero matches.
  - **Decision Tree:**
    - **IF** removing endpoints causes import errors in Zaks-llm → remove only the route handlers, keep the file structure
    - **IF** actions_runner.py has other active code paths using `.deal-registry` → comment out with `# DECOMMISSIONED:` prefix and add deprecation warning log

- P1-05: **Rebuild and verify affected services**
  - Backend: `cd /home/zaks/zakops-backend && docker compose build backend && docker compose up -d backend --no-deps`
  - Verify: `curl -sf http://localhost:8091/health`
  - Verify Zaks-llm still starts (if running): `curl -sf http://localhost:8052/health`

- P1-06: **Write checkpoint**

#### Rollback Plan
1. `git checkout -- /home/zaks/zakops-backend/mcp_server/server.py`
2. `git checkout -- /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml`
3. `git checkout -- /home/zaks/Zaks-llm/src/api/server.py`
4. `git checkout -- /home/zaks/zakops-backend/src/workers/actions_runner.py /home/zaks/zakops-backend/src/actions/memory/store.py /home/zaks/zakops-backend/src/core/database/adapter.py`
5. Drop migration if applied: `psql -h localhost -U zakops -d zakops -c "DROP INDEX IF EXISTS zakops.uq_quarantine_message_id;"`
6. Rebuild backend: `docker compose build backend && docker compose up -d backend --no-deps`

#### Gate P1
- MCP server: `grep -c '/process' /home/zaks/zakops-backend/mcp_server/server.py` returns >= 2
- Dedup: `psql -h localhost -U zakops -d zakops -c "\d zakops.quarantine_items" | grep -i unique` shows message_id constraint
- Agent config: `grep 'DATABASE_URL.*zakops_agent' /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml` returns match
- Legacy: `rg ".deal-registry" --type py /home/zaks/zakops-backend/src/ /home/zaks/Zaks-llm/src/ | grep -v test | grep -v '#' | wc -l` returns 0
- Backend health: `curl -sf http://localhost:8091/health` returns 200
- `make validate-local` passes

---

### SM-1 Phase 2 — P1 Pipeline Fixes (F-6, F-9, F-10, F-13)
**Complexity:** L
**Estimated touch points:** 4–6 files in zakops-backend

**Purpose:** Fix the P1 findings that affect pipeline correctness: FSM bypass, idempotency bugs, missing routes, and schema mismatches.

#### Blast Radius
- **Services affected:** zakops-backend (8091)
- **Pages affected:** Quarantine actions (approve flow may change response shape)
- **Downstream consumers:** Dashboard quarantine UI, MCP tools, retention system

#### Tasks
- P2-01: **Fix F-6 — Route quarantine approval through workflow engine** — Modify `/home/zaks/zakops-backend/src/api/orchestration/main.py` (around line 1648) to use `DealWorkflowEngine.create_deal()` or call `transition_deal_state()` after the INSERT so that `deal_transitions` ledger and `outbox` events are emitted.
  - **Checkpoint:** After fix, approving a quarantine item produces rows in both `deal_events` AND `deal_transitions`.
  - Preserve the existing response shape to avoid breaking the dashboard.

- P2-02: **Fix F-9 — Idempotency schema qualification** — In `/home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py`:
  - Schema-qualify all references: `FROM idempotency_keys` → `FROM zakops.idempotency_keys` (line 85, 127, and any others).
  - Change error-bypass at line 147 to fail-closed: on DB error, return 503 instead of silently proceeding.

- P2-03: **Fix F-10 — Bulk-delete route alignment**
  - **Decision Tree:**
    - **IF** bulk-delete is a desired feature → implement: dashboard API route `POST /api/quarantine/bulk-delete` → backend endpoint with soft-hide (`status='hidden'`)
    - **ELSE** → remove the client-side call from `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (line 942) and any UI trigger
  - Record decision in checkpoint.

- P2-04: **Fix F-13 — Retention cleanup column mismatch** — In `/home/zaks/zakops-backend/src/core/retention/cleanup.py` (line 299), change the UPDATE to use the `raw_content` JSON field pattern (matching the approval flow at `main.py:1695`) instead of referencing nonexistent `processed_by` and `processing_action` columns.

- P2-05: **Include fixes in migration 029** — If F-6 or F-13 require schema changes, add them to the migration from Phase 1 or create migration 030.

- P2-06: **Rebuild and verify backend** — Rebuild and test: `docker compose build backend && docker compose up -d backend --no-deps`

- P2-07: **Write checkpoint**

#### Rollback Plan
1. `git checkout -- /home/zaks/zakops-backend/src/api/orchestration/main.py`
2. `git checkout -- /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py`
3. `git checkout -- /home/zaks/zakops-backend/src/core/retention/cleanup.py`
4. Rebuild backend

#### Gate P2
- FSM: test quarantine approval produces `deal_transitions` row (manual psql check or curl test)
- Idempotency: `grep -c "zakops.idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py` >= 2
- Idempotency: no unqualified `FROM idempotency_keys` references remain
- Bulk-delete: either route exists (curl returns 200/204) or client call removed (grep returns 0)
- Retention: `grep 'processed_by' /home/zaks/zakops-backend/src/core/retention/cleanup.py` → either 0 matches or references `raw_content` pattern
- Backend health: 200
- `make validate-local` passes

---

### SM-1 Phase 3 — P1 Observability + Wiring (F-7, F-8)
**Complexity:** M
**Estimated touch points:** 4–6 files across backend + dashboard

**Purpose:** Fix correlation ID fragmentation and wire email settings to real endpoints.

#### Blast Radius
- **Services affected:** zakops-backend (8091), dashboard (3003)
- **Pages affected:** Settings/email page, onboarding email step
- **Downstream consumers:** Observability stack, email integration flow

#### Tasks
- P3-01: **Fix F-8 — Correlation ID propagation** — Add `correlation_id UUID` column to `zakops.quarantine_items` via migration. Ensure the quarantine INSERT path (`main.py:1508+`) captures the `X-Correlation-ID` header and stores it. Unify the two backend tracing middlewares (`trace.py` vs `tracing.py`) into one that respects incoming `X-Correlation-ID`.
  - Target migration: add to 029 or create 030.
  - **Checkpoint:** `psql -c "\d zakops.quarantine_items" | grep correlation_id` shows the column.

- P3-02: **Fix F-7 — Wire email settings** — In the dashboard, either redirect the email settings proxy from `/api/user/email-config` to the real backend endpoint (`/api/integrations/email/auth/gmail`), or implement the missing backend endpoint. In `EmailSetupStep.tsx`, replace the simulated OAuth (2-second delay + mock) with a real OAuth flow calling the backend.
  - **Decision Tree:**
    - **IF** backend has `/api/integrations/email/auth/gmail` → redirect dashboard proxy to it
    - **ELSE** → create minimal email config endpoint in backend
  - Target: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts` and `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx`

- P3-03: **Write checkpoint**

#### Rollback Plan
1. Drop correlation_id column: `psql -c "ALTER TABLE zakops.quarantine_items DROP COLUMN IF EXISTS correlation_id;"`
2. `git checkout -- apps/dashboard/src/app/api/settings/email/route.ts apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx`
3. Rebuild backend

#### Gate P3
- Correlation: `psql -c "SELECT column_name FROM information_schema.columns WHERE table_name='quarantine_items' AND column_name='correlation_id'"` returns 1 row
- Email settings: `curl -sS http://localhost:3003/api/settings/email -o /dev/null -w '%{http_code}'` returns non-404
- `make validate-local` passes

---

### SM-1 Phase 4 — P2/P3 Fixes + Shadow-Mode Infrastructure
**Complexity:** L
**Estimated touch points:** 6–8 files across backend + dashboard

**Purpose:** Fix remaining lower-severity findings and build shadow-mode injection support for LangSmith.

#### Blast Radius
- **Services affected:** zakops-backend, dashboard
- **Pages affected:** Quarantine list (shadow-mode badges)
- **Downstream consumers:** LangSmith integration, retention system

#### Tasks
- P4-01: **Fix F-11 — Quarantine status CHECK constraint** — Add migration: `ALTER TABLE zakops.quarantine_items ADD CONSTRAINT chk_quarantine_status CHECK (status IN ('pending', 'approved', 'rejected', 'hidden'))`.

- P4-02: **Fix F-12 — DDL default stage** — Add migration or update init script: change `DEFAULT 'lead'` to `DEFAULT 'inbound'` on `zakops.deals.stage`.
  - **Decision Tree:**
    - **IF** init scripts are not re-run (production uses migrations only) → add ALTER in migration
    - **ELSE** → update both init script and add migration for existing DBs

- P4-03: **Fix F-14 — Transition matrix sync** — Remove the duplicate `VALID_TRANSITIONS` from `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py` (lines 83-95). Instead, validate transitions via the backend API that the agent already calls. Or generate from backend spec via `make sync-agent-types`.

- P4-04: **Fix F-15 — Agent contract docstring** — Update `/home/zaks/zakops-backend/src/agent/bridge/agent_contract.py` line 249: change `Won/Lost/Passed` to `portfolio/junk/archived`.

- P4-05: **Fix F-16 — Attachment linkage post-promotion** — In the quarantine approval flow (`main.py:1648+`), after creating the deal, link associated email thread and attachments via existing email thread linking APIs (`email.py:436`, `service.py:373`).

- P4-06: **Fix F-17 — OAuth state documentation** — Create ADR documenting the in-memory `OAuthStateStore` constraint. No code change needed — this is a P3 architectural awareness item.
  - Target: `/home/zaks/zakops-backend/docs/ADR-004-oauth-state-storage.md`

- P4-07: **Build shadow-mode injection support**
  - Add `source_type VARCHAR(50) DEFAULT 'manual'` column to `zakops.quarantine_items` via migration. Valid values: `'manual'`, `'email_sync'`, `'langsmith_shadow'`, `'langsmith_live'`.
  - Add `injected_at TIMESTAMPTZ`, `injection_metadata JSONB` columns for measurement capture.
  - Modify `POST /api/quarantine` endpoint to accept optional `source_type`, `injection_metadata` fields.
  - Add input validation: if `source_type` starts with `langsmith_`, require authentication (API key or service token header).
  - **No auto-promotion**: shadow-mode items follow the same manual approval flow as all other quarantine items.

- P4-08: **Add shadow-mode UI badge** — In the dashboard quarantine list, display a distinct badge for items where `source_type` starts with `langsmith_`. Per Surface 9 design system rules.
  - Target: Dashboard quarantine list component.

- P4-09: **Write checkpoint**

#### Rollback Plan
1. Drop new columns: `psql -c "ALTER TABLE zakops.quarantine_items DROP COLUMN IF EXISTS source_type, DROP COLUMN IF EXISTS injected_at, DROP COLUMN IF EXISTS injection_metadata;"`
2. Drop constraints: `psql -c "ALTER TABLE zakops.quarantine_items DROP CONSTRAINT IF EXISTS chk_quarantine_status;"`
3. `git checkout -- apps/agent-api/app/core/langgraph/tools/deal_tools.py`
4. Rebuild backend

#### Gate P4
- Status constraint: `psql -c "\d zakops.quarantine_items" | grep chk_quarantine_status`
- Default stage: DDL or migration uses `'inbound'` not `'lead'`
- Shadow-mode columns: `psql -c "SELECT column_name FROM information_schema.columns WHERE table_name='quarantine_items' AND column_name IN ('source_type','injected_at','injection_metadata')"` returns 3 rows
- `make validate-local` passes
- Dashboard compiles: `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`

---

### SM-1 Phase 5 — Readiness Gate Verification
**Complexity:** M
**Estimated touch points:** 0 (verification only) + bookkeeping

**Purpose:** Prove all 7 readiness gates with evidence. Produce the evidence pack.

#### Blast Radius
- **Services affected:** None (verification only)
- **Pages affected:** None
- **Downstream consumers:** Program continuation decision

#### Tasks
- P5-01: **Readiness Gate 1 — Injection → Quarantine** — Inject a test quarantine item via `curl -X POST http://localhost:8091/api/quarantine -H 'Content-Type: application/json' -d '{"subject":"RG-1 Test","sender":"test@example.com","message_id":"rg1-test-001","source_type":"langsmith_shadow"}'`. Verify it appears in quarantine list and dashboard UI.

- P5-02: **Readiness Gate 2 — Dedup/Idempotency** — Re-inject the same item (same `message_id`). Verify only one row exists: `psql -c "SELECT COUNT(*) FROM zakops.quarantine_items WHERE message_id='rg1-test-001'"` must return 1.

- P5-03: **Readiness Gate 3 — Quarantine Actions** — Test all quarantine actions that exist in the UI: approve, reject, delete. Verify each produces the expected DB state change. No dead buttons.

- P5-04: **Readiness Gate 4 — Approve → Deal Promotion** — Approve a quarantine item. Verify: deal created in `zakops.deals`, `deal_transitions` ledger entry exists, `deal_events` entry exists, quarantine item status changed.

- P5-05: **Readiness Gate 5 — Single Source of Truth** — After promotion, verify: dashboard `/api/deals` returns the new deal; agent-api (if running) can see the same deal via backend client. No drift.

- P5-06: **Readiness Gate 6 — Legacy Decommission** — `rg ".deal-registry" --type py /home/zaks/zakops-backend/src/ /home/zaks/Zaks-llm/src/ | grep -v test | grep -v '#'` returns zero. No legacy store can create competing truth.

- P5-07: **Readiness Gate 7 — Observability** — For the test item from RG-1, trace: injection (`quarantine_items` row with `correlation_id`) → UI render (dashboard shows it) → approval → deal creation → deal visible in dashboard and agent API. Document the trace in the evidence pack.

- P5-08: **Run all 14 FINAL_MASTER acceptance gates** — Execute each gate command from the FINAL_MASTER and record results.

- P5-09: **Produce evidence pack** — Write to `/home/zaks/bookkeeping/docs/_qa_evidence/INTAKE-READY-001-EVIDENCE.md` with:
  - Per-gate results (PASS/FAIL)
  - Screenshots or curl output for each readiness gate
  - FINAL_MASTER gate results

- P5-10: **Update bookkeeping** — Record all SM-1 changes in `/home/zaks/bookkeeping/CHANGES.md`

- P5-11: **Write final checkpoint** — Mark SM-1 as complete in checkpoint file

#### Gate P5
- All 7 readiness gates PASS with evidence
- All 14 FINAL_MASTER gates PASS (or documented exceptions)
- Evidence pack written
- CHANGES.md updated
- `make validate-local` passes

---

### SM-1 Acceptance Criteria

#### AC-SM1-1: P0 Findings Fixed
All 5 P0 findings (F-1, F-2/ingestion endpoint hardened, F-3, F-4, F-5) are resolved with evidence.

#### AC-SM1-2: P1 Findings Fixed
All 6 P1 findings (F-6, F-7, F-8, F-9, F-10, F-13) are resolved with evidence.

#### AC-SM1-3: P2/P3 Findings Fixed
All 6 P2/P3 findings (F-11, F-12, F-14, F-15, F-16, F-17) are resolved with evidence.

#### AC-SM1-4: Shadow-Mode Infrastructure
Quarantine ingestion endpoint accepts `source_type` and `injection_metadata` fields. Dashboard shows shadow-mode badge. No auto-promotion.

#### AC-SM1-5: All 7 Readiness Gates PASS
Each gate has documented evidence in the evidence pack.

#### AC-SM1-6: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes. Backend health 200.

#### AC-SM1-7: Bookkeeping
CHANGES.md updated. Evidence pack produced. Checkpoint file updated.

### SM-1 File Paths Reference

#### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-backend/mcp_server/server.py` | P1 | F-1: `/review` → `/process` |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | P1, P2, P4 | F-3: ON CONFLICT, F-6: workflow engine, F-16: attachment linking |
| `/home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml` | P1 | F-4: `zakops` → `zakops_agent` |
| `/home/zaks/Zaks-llm/src/api/server.py` | P1 | F-5: remove shadow endpoints |
| `/home/zaks/zakops-backend/src/workers/actions_runner.py` | P1 | F-5: remove `.deal-registry` refs |
| `/home/zaks/zakops-backend/src/actions/memory/store.py` | P1 | F-5: remove SQLite refs |
| `/home/zaks/zakops-backend/src/core/database/adapter.py` | P1 | F-5: remove dual-write adapter |
| `/home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py` | P2 | F-9: schema-qualify + fail-closed |
| `/home/zaks/zakops-backend/src/core/retention/cleanup.py` | P2 | F-13: fix column refs |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | P2 | F-10: bulk-delete alignment |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts` | P3 | F-7: wire to real endpoint |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx` | P3 | F-7: real OAuth |
| `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py` | P4 | F-14: remove duplicate transitions |
| `/home/zaks/zakops-backend/src/agent/bridge/agent_contract.py` | P4 | F-15: fix docstring stages |

#### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-backend/db/migrations/029_quarantine_hardening.sql` | P1-P4 | UNIQUE constraint, CHECK constraint, correlation_id, shadow-mode columns, default stage fix |
| `/home/zaks/zakops-backend/docs/ADR-004-oauth-state-storage.md` | P4 | F-17: OAuth state architecture decision |
| `/home/zaks/bookkeeping/docs/_qa_evidence/INTAKE-READY-001-EVIDENCE.md` | P5 | Evidence pack |

#### Files to Read (sources of truth)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/FINAL_MASTER.md` | 17 forensic findings |
| `/home/zaks/zakops-backend/src/core/deals/workflow.py` | Canonical DealWorkflowEngine |
| `/home/zaks/zakops-backend/db/init/001_base_tables.sql` | Base table schemas |

### SM-1 Lab Loop Configuration

```
TASK_ID=INTAKE-READY-001
REPO_DIR=/home/zaks/zakops-backend
GATE_CMD="cd /home/zaks/zakops-agent-api && make validate-local && cd /home/zaks/zakops-backend && docker compose exec backend python -c 'print(\"OK\")'"
```

### SM-1 Stop Condition

SM-1 is DONE when:
- All 7 readiness gates PASS with evidence
- All 14 FINAL_MASTER acceptance gates PASS
- `make validate-local` passes
- Evidence pack produced
- CHANGES.md updated

**Do NOT proceed to:** COL-V2-CORE-001 until all SM-1 gates PASS.

---

# SUB-MISSION 2: COL-V2-CORE-001

## Core Wiring + Service Completion + Compliance Foundation
## Classification: Service Integration + Feature Completion
## Prerequisite: INTAKE-READY-001 complete (all 7 readiness gates PASS)
## Successor: COL-V2-INTEL-001

### Objective

**Wire existing but disconnected services into the graph.py turn pipeline** and complete spec-mandated features in 10 existing services. Build the legal hold and partition automation foundation.

This sub-mission transforms the agent from "services exist" to "services are connected and functional."

**What this sub-mission is NOT:**
- Not building new intelligence services (that's SM-3)
- Not building dashboard UI beyond what's needed for wiring verification
- Not modifying the backend repo (that was SM-1)

**Source material:**
- Actionable items: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` (Sections B, C1-C2, D)
- Design spec: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md`

### SM-2 Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify SM-1 is complete, establish SM-2 baseline, verify existing services still load.

#### Tasks
- P0-01: **Verify SM-1 checkpoint** — Read checkpoint file; confirm SM-1 is marked complete.
- P0-02: **Run baseline validation** — `make validate-local`
- P0-03: **Verify existing services load** — For each: `cd /home/zaks/zakops-agent-api/apps/agent-api && python -c "from app.services.{service} import {class_or_instance}; print('OK')"`
  - Services: `replay_service`, `snapshot_writer`, `counterfactual_service`, `export_service`, `proposal_service`, `brain_extraction`, `drift_detection`, `momentum_calculator`, `summarizer`
  - Record which import successfully and which fail.
- P0-04: **Verify DB items (D1, D2, D4-D7)** — Run psql checks from actionable items register Section D.
- P0-05: **Read spec sections** for Phase 1 items: S4.5, S6, S8.2, S19.4.
- P0-06: **Write checkpoint**

#### Gate P0
- SM-1 checkpoint confirms completion
- `make validate-local` passes
- At least 7 of 9 services import successfully
- D-items verification recorded

---

### SM-2 Phase 1 — Core Wiring into graph.py (B1.2, B4.2, B8.1, B9.1)
**Complexity:** L
**Estimated touch points:** 3–5 files in agent-api

**Purpose:** Connect existing but unwired services into the graph.py turn pipeline as fire-and-forget post-turn enrichments.

#### Blast Radius
- **Services affected:** agent-api (8095)
- **Pages affected:** None (backend enrichment)
- **Downstream consumers:** turn_snapshots table, brain facts, drift alerts

#### Tasks
- P1-01: **Create post-turn enrichment function** in `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py`:
  - After the assistant response is generated, call `_post_turn_enrichment()` via `asyncio.create_task()`
  - Orchestrates: (1) snapshot_writer.write(), (2) brain_extraction trigger, (3) drift_detection checks, (4) citation_audit if citations present
  - All calls are fire-and-forget with try/except logging
  - **Checkpoint:** `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`

- P1-02: **Wire citation_audit (B1.2)** — After LLM response, if response contains `[cite-N]` patterns, call `audit_citations()` and store quality_score in turn snapshot's `citations_extracted` field.

- P1-03: **Wire drift_detection (B8.1)** — After brain extraction, call `check_staleness()` and `detect_contradictions()`. Log warnings on staleness; log contradictions and reduce confidence.

- P1-04: **Wire snapshot_writer (B9.1)** — Build `TurnSnapshot` from current turn data and call `snapshot_writer.write()`. Populate: thread_id, turn_number, user_id, model_name, raw_completion, token counts, latency_ms.

- P1-05: **Wire node_registry (B4.2)** — Before the main LLM call, call `node_registry.route(query, context)`. If specialist returns confidence >= 0.6, enhance system prompt with specialist analysis.

- P1-06: **Write checkpoint**

#### Rollback Plan
1. `git checkout -- apps/agent-api/app/core/langgraph/graph.py`
2. Restart agent-api

#### Gate P1
- `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- No import cycles: `python -c "import app.services.replay_service; import app.services.snapshot_writer; import app.services.drift_detection; import app.core.security.citation_audit; print('All imports OK')"`
- `make validate-local` passes

---

### SM-2 Phase 2 — Service Completion (B-section items)
**Complexity:** XL
**Estimated touch points:** 10–12 files in agent-api

**Purpose:** Add spec-mandated features to the 10 existing services that have partial implementations.

#### Blast Radius
- **Services affected:** agent-api
- **Pages affected:** None (service-layer only)
- **Downstream consumers:** graph.py enrichment pipeline, API endpoints

#### Tasks
- P2-01: **Migrate raw httpx to BackendClient** in `proposal_service.py` and `export_service.py`
  - **Checkpoint:** Both services still import cleanly.

- P2-02: **Add admin role check (B2.1, B3.1)** to `/admin/replay` and `/admin/counterfactual` endpoints
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py`

- P2-03: **Add configurable thresholds (B1.4)** to citation_audit.py — Replace hardcoded 0.5/0.3 with module-level constants

- P2-04: **Add proposal expiration (B7.3)** — Pending proposals older than 24 hours auto-expire. Add `expires_at` field.

- P2-05: **Add trigger_type field (B7.2)** — When `_handle_correct_brain_summary` executes, pass `trigger_type='correction'` to backend brain summary endpoint.

- P2-06: **Add brain export integration (B6.2)** — When exporting a deal-scoped thread, include Deal Brain state as appendix in markdown export.

- P2-07: **Add replay audit log (B2.4)** — Structured log entry for replay operations.

- P2-08: **Add counterfactual history (B3.3)** — Store analysis results as JSONB on turn_snapshot.

- P2-09: **Add extractive pre-filter (B10.2)** — Filter low-signal turns before LLM summarization.

- P2-10: **Write checkpoint**

#### Rollback Plan
1. `git checkout -- apps/agent-api/app/services/*.py apps/agent-api/app/api/v1/chatbot.py apps/agent-api/app/core/security/citation_audit.py`

#### Gate P2
- All modified services import cleanly
- BackendClient used (no raw httpx in production service code): `grep -r "httpx.AsyncClient" apps/agent-api/app/services/ | grep -v test | grep -v '#'` returns 0
- `make validate-local` passes

---

### SM-2 Phase 3 — Compliance Foundation (C1, C2)
**Complexity:** M
**Estimated touch points:** 2–3 files in agent-api

**Purpose:** Build legal hold and partition automation foundation.

#### Blast Radius
- **Services affected:** agent-api (database schema)
- **Pages affected:** None
- **Downstream consumers:** Retention policy engine (SM-4), GDPR pipeline (SM-4)

#### Tasks
- P3-01: **Create migration 029 — Legal Hold Tables (C1)** per S7.5:
  - `legal_hold_locks`: thread_id, hold_type, hold_reason, set_by, set_at, released_at
  - `legal_hold_log`: id, thread_id, action, hold_type, actor, reason, created_at
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/migrations/` (new SQL file)
  - **Decision Tree:**
    - **IF** tables already exist → skip, record in checkpoint
    - **ELSE** → create migration following existing naming convention

- P3-02: **Create partition automation function (C2)** per S6.6:
  - PL/pgSQL function `create_monthly_partitions(table_name, months_ahead)` for turn_snapshots and chat_messages
  - **Decision Tree:**
    - **IF** function already exists (check D1 from Phase 0) → skip
    - **ELSE** → include in migration

- P3-03: **Run migration**
- P3-04: **Write checkpoint**

#### Rollback Plan
1. Drop tables: `psql -h localhost -U agent -d zakops_agent -c "DROP TABLE IF EXISTS legal_hold_log, legal_hold_locks CASCADE;"`
2. Drop function: `psql -h localhost -U agent -d zakops_agent -c "DROP FUNCTION IF EXISTS create_monthly_partitions;"`

#### Gate P3
- `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_locks"` shows schema
- `psql -h localhost -U agent -d zakops_agent -c "\d legal_hold_log"` shows schema
- `make validate-local` passes

---

### SM-2 Phase 4 — Verification & Self-Audit
**Complexity:** S
**Estimated touch points:** 0 (verification) + bookkeeping

#### Tasks
- P4-01: **Run full validation** — `make validate-local`
- P4-02: **TypeScript compilation** — `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
- P4-03: **Verify all services import** — Import check for every modified file
- P4-04: **Count changes** — Produce summary
- P4-05: **Update CHANGES.md**
- P4-06: **Produce completion report** — `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-CORE-001-COMPLETION.md`
- P4-07: **Write final checkpoint**

#### Gate P4
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All services import cleanly
- CHANGES.md updated
- Completion report written

---

### SM-2 Acceptance Criteria

#### AC-SM2-1: Core Pipeline Wired
graph.py post-turn enrichment calls snapshot_writer, brain_extraction, drift_detection, and citation_audit as fire-and-forget. No blocking of user response.

#### AC-SM2-2: Existing Services Completed
Admin auth on replay/counterfactual, BackendClient migration, configurable thresholds, proposal expiration, brain export in export_service.

#### AC-SM2-3: Legal Hold Infrastructure
legal_hold_locks and legal_hold_log tables exist. create_monthly_partitions function exists (or verified existing).

#### AC-SM2-4: Verification Items
D-items (D1, D2, D4-D7) verified and recorded.

#### AC-SM2-5: No Regressions
`make validate-local` passes. `npx tsc --noEmit` passes.

#### AC-SM2-6: Bookkeeping
CHANGES.md updated. Completion report produced.

### SM-2 Lab Loop Configuration

```
TASK_ID=COL-V2-CORE-001
REPO_DIR=/home/zaks/zakops-agent-api
GATE_CMD="make validate-local && cd apps/agent-api && python -c 'from app.core.langgraph.graph import build_graph; print(\"OK\")'"
```

### SM-2 Stop Condition

SM-2 is DONE when all 6 AC are met and completion report is produced. Do NOT proceed to COL-V2-INTEL-001 until SM-2 is complete.

---

## CONTEXT CHECKPOINT — SM-1 + SM-2 Complete
<!-- Adopted from Improvement Area IA-1 -->

At this point, the pipeline is hardened (SM-1) and core services are wired (SM-2). Commit all work, update checkpoint, and continue in a fresh session if context is constrained.

---

# SUB-MISSION 3: COL-V2-INTEL-001

## Intelligence Services Build
## Classification: Feature Build
## Prerequisite: COL-V2-CORE-001 complete
## Successor: COL-V2-AMBIENT-001

### Objective

**Build the intelligence services** that make the agent genuinely smart: reflexion self-critique, cognitive intelligence (fatigue detection, spaced repetition), RAG enhancement, and advanced agent architecture (PlanAndExecute, multi-specialist).

**What this sub-mission is NOT:**
- Not building dashboard UI (that's SM-4)
- Not modifying the backend repo
- Not rebuilding services that already exist in the backend (StallPredictor, MorningBriefing, AnomalyDetector, etc.)

**Source material:**
- Actionable items: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` (Sections C-P2 through C-P5)
- Design spec: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md`

### SM-3 Phase 0 — Checkpoint Recovery & Baseline
**Complexity:** S

#### Tasks
- P0-01: Read checkpoint file, verify SM-2 is complete
- P0-02: `make validate-local`
- P0-03: Verify graph.py enrichment pipeline still works: `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- P0-04: Read spec sections: S8.3-S8.5, S11.3, S14.1-S14.7, S19.2-S19.5
- P0-05: Write checkpoint

---

### SM-3 Phase 1 — Reflexion & Chain-of-Verification (C3, C4)
**Complexity:** L
**Estimated touch points:** 2–3 new files

**Purpose:** Build the self-critique and verification pipeline.

#### Blast Radius
- **Services affected:** agent-api
- **Pages affected:** None
- **Downstream consumers:** graph.py turn pipeline, turn_snapshots

#### Tasks
- P1-01: **Build ReflexionService (C3)** per S8.3-S8.4:
  - `ReflexionService` with `critique(response, evidence, brain_facts)` → `CritiqueResult`
  - `CritiqueResult`: issues, severity, should_revise, revised_response
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py`

- P1-02: **Build Chain-of-Verification (C4)** per S8.5:
  - `verify_claims(response_text, evidence_sources)` → verified/unverified claims
  - Integrate into ReflexionService or separate module

- P1-03: **Wire reflexion into graph.py** — After LLM response, optionally run critique. Config flag: enabled for deal-scoped chats only.

- P1-04: **Store critique_result in turn snapshot**

- P1-05: **Write checkpoint**

#### Rollback Plan
1. `rm apps/agent-api/app/services/reflexion.py`
2. `git checkout -- apps/agent-api/app/core/langgraph/graph.py`

#### Gate P1
- `python -c "from app.services.reflexion import ReflexionService, CritiqueResult; print('OK')"`
- `python -c "from app.core.langgraph.graph import build_graph; print('OK')"`
- `make validate-local` passes

---

### SM-3 Phase 2 — Cognitive Intelligence (C8, C12, C14, C15)
**Complexity:** M
**Estimated touch points:** 3–4 new files

**Purpose:** Build cognitive intelligence services. Note: C9 (StallPredictor), C18 (MorningBriefing), C19 (AnomalyDetector) already exist in the backend — this phase builds only what's MISSING.

#### Blast Radius
- **Services affected:** agent-api
- **Pages affected:** None (backend services only)
- **Downstream consumers:** SSE events, dashboard (SM-4)

#### Tasks
- P2-01: **Build DecisionFatigueSentinel (C8)** per S14.1
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py`

- P2-02: **Build Spaced Repetition (C12)** per S14.5
  - `get_review_facts(deal_id)` → facts below decay threshold
  - Depends on: drift_detection.py `compute_decay_confidence()`
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py`

- P2-03: **Add ghost_knowledge_flags to SSE events (C14)** per S14.7
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py`

- P2-04: **Add momentum UI color bands (C15)** per S20
  - Green (70+), amber (40-69), red (0-39) — this is a data-mapping task; the backend `MomentumCalculator` already exists
  - Target: identify dashboard deal detail component

- P2-05: **Write checkpoint**

#### Gate P2
- All new services import cleanly
- SSE events schema validates
- `make validate-local` passes

---

### SM-3 Phase 3 — RAG Enhancement (C5, C7, B5.2-B5.4, B10.1)
**Complexity:** M
**Estimated touch points:** 3–4 files

**Purpose:** Enhance retrieval quality and add missing RAG features.

#### Tasks
- P3-01: **Add HyDE query option (C5)** per S11.3 — Add `hyde` parameter to rag_rest.py
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_rest.py`

- P3-02: **Add RankedChunk type (C7)** per S11
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/schemas/` (new schema file)

- P3-03: **Add contextual chunk headers (B5.2)** — Prepend document title/section to chunks

- P3-04: **Verify RAG indexes (B5.3, B5.4)** — Check ivfflat and GIN indexes exist in crawlrag DB

- P3-05: **Build consolidation worker (B10.1)** — Merge old summaries into archival tier

- P3-06: **Write checkpoint**

#### Gate P3
- `python -c "from app.schemas... import RankedChunk; print('OK')"` (adjust import path)
- `make validate-local` passes

---

### SM-3 Phase 4 — Agent Architecture (C24-C26, B4.3-B4.4)
**Complexity:** L
**Estimated touch points:** 3–4 files

**Purpose:** Build PlanAndExecute graph and complete multi-specialist delegation.

#### Tasks
- P4-01: **Build PlanAndExecuteGraph (C24)** per S19.2
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py`

- P4-02: **Add 4th specialist — Compliance/Regulatory (B4.3)** per S19.4
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py`

- P4-03: **Add specialist response synthesis (B4.4)**

- P4-04: **Add MCP cost/decision ledger (C26)** per S19.5

- P4-05: **Write checkpoint**

#### Gate P4
- `python -c "from app.core.langgraph.plan_execute import PlanAndExecuteGraph; print('OK')"`
- `python -c "from app.core.langgraph.node_registry import node_registry; assert len(node_registry.list_specialists()) >= 4; print('OK')"`
- `make validate-local` passes

---

### SM-3 Phase 5 — Verification & Self-Audit
**Complexity:** S

#### Tasks
- P5-01: `make validate-local`
- P5-02: `npx tsc --noEmit`
- P5-03: Import check for all new files
- P5-04: Update CHANGES.md
- P5-05: Produce completion report: `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-INTEL-001-COMPLETION.md`
- P5-06: Write final checkpoint

#### Gate P5
- All gates pass, completion report written

---

### SM-3 Acceptance Criteria

#### AC-SM3-1: Reflexion Pipeline
ReflexionService + CritiqueResult exist, wired into graph.py for deal-scoped chats.

#### AC-SM3-2: Cognitive Intelligence
DecisionFatigueSentinel and SpacedRepetition services exist. Ghost knowledge SSE event type registered.

#### AC-SM3-3: RAG Enhancement
HyDE query option in rag_rest.py. RankedChunk type defined.

#### AC-SM3-4: Agent Architecture
PlanAndExecuteGraph exists. NodeRegistry has 4+ specialists with synthesis.

#### AC-SM3-5: No Regressions
`make validate-local` and `npx tsc --noEmit` pass.

#### AC-SM3-6: Bookkeeping
CHANGES.md updated. Completion report produced.

### SM-3 Lab Loop Configuration

```
TASK_ID=COL-V2-INTEL-001
REPO_DIR=/home/zaks/zakops-agent-api
GATE_CMD="make validate-local && cd apps/agent-api && python -c 'from app.services.reflexion import ReflexionService; from app.core.langgraph.plan_execute import PlanAndExecuteGraph; print(\"OK\")'"
```

### SM-3 Stop Condition

SM-3 is DONE when all 6 AC are met. Do NOT proceed to COL-V2-AMBIENT-001 until complete.

---

# SUB-MISSION 4: COL-V2-AMBIENT-001

## Ambient Intelligence UI + Compliance Pipeline
## Classification: Feature Build + UI + Compliance
## Prerequisite: COL-V2-INTEL-001 complete
## Successor: QA-MASTER-PROGRAM-VERIFY-001

### Objective

**Build the ambient intelligence dashboard UI** (citation indicators, memory panel, smart paste, command palette) and the **compliance pipeline** (GDPR deletion, retention policy, audit trail). Surface the intelligence services from SM-3 and the existing backend services to users.

**What this sub-mission is NOT:**
- Not building new backend intelligence services (they exist or were built in SM-3)
- Not modifying the core agent pipeline (that was SM-2)
- Not rebuilding the intake pipeline (that was SM-1)

**Source material:**
- Actionable items: `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` (Section C-P4, C-P6)
- Design spec: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md`

### SM-4 Phase 0 — Checkpoint Recovery & Baseline
**Complexity:** S

#### Tasks
- P0-01: Read checkpoint, verify SM-3 complete
- P0-02: `make validate-local`
- P0-03: `npx tsc --noEmit`
- P0-04: Read spec sections: S5.4, S8.2, S17.1-S17.6
- P0-05: Write checkpoint

---

### SM-4 Phase 1 — Dashboard UI for Existing Backend Services
**Complexity:** M
**Estimated touch points:** 3–5 dashboard files

**Purpose:** Build dashboard components for backend services that already exist but have no UI.

#### Blast Radius
- **Services affected:** dashboard (3003)
- **Pages affected:** Deal detail (momentum), deal list (anomaly badges, morning briefing)
- **Downstream consumers:** End users

#### Tasks
- P1-01: **Morning Briefing UI (C18)** — Dashboard component showing daily briefing from existing backend `MorningBriefingGenerator`. Per Surface 9.

- P1-02: **Anomaly badges in deal list (C19)** — Display anomaly indicators from existing backend `DealAnomalyDetector`. Per Surface 9.

- P1-03: **Momentum color bands (C15 UI)** — Green/amber/red in deal detail from existing backend `MomentumCalculator`. Per Surface 9.

- P1-04: **Write checkpoint**

#### Gate P1
- Dashboard compiles: `npx tsc --noEmit`
- `make validate-local` passes

---

### SM-4 Phase 2 — New Dashboard UI Components (C16, C17, C21-C23)
**Complexity:** XL
**Estimated touch points:** 6–10 dashboard files

**Purpose:** Build the ambient intelligence UI features.

#### Blast Radius
- **Services affected:** dashboard
- **Pages affected:** Chat (citation indicators, memory panel, smart paste), global (command palette)
- **Downstream consumers:** End users

#### Tasks
- P2-01: **Citation UI Indicators (C16)** per S8.2 — Green/amber/red underlines for citation strength. "Refined" badge on messages that went through reflexion. Per Surface 9.

- P2-02: **MemoryStatePanel (C17)** per S5.4 — Sidebar panel: Working memory (last 6 messages), Recall (brain facts + summaries), Archival (expired summaries). Per Surface 9.

- P2-03: **SmartPaste (C21)** per S17.4 — On paste, extract entities and offer "Add to Deal Brain." Per Surface 9.

- P2-04: **SentimentCoach (C22)** per S17.5 — Per-deal sentiment trend tracking and visualization.
  - This requires building the service AND the UI.
  - Target service: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py`

- P2-05: **CommandPalette (C23)** per S17.6 — Cmd+K with context-aware commands. Per Surface 9.

- P2-06: **Write checkpoint**

#### Decision Tree
- **IF** building dashboard components → follow Surface 9 design system rules (`.claude/rules/design-system.md`)
- **IF** agent-api is not running → build with mock data, test rendering only

#### Gate P2
- `npx tsc --noEmit` passes
- `make validate-local` passes
- Surface 9 compliance: no design system violations

---

### SM-4 Phase 3 — Compliance Pipeline (C27-C31)
**Complexity:** L
**Estimated touch points:** 4–6 files in agent-api

**Purpose:** Build GDPR and data retention infrastructure.

#### Blast Radius
- **Services affected:** agent-api (database + API)
- **Pages affected:** None (admin-only)
- **Downstream consumers:** Legal hold system, admin panel

#### Tasks
- P3-01: **Retention policy engine (C28)** per S7.4
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/retention_policy.py`

- P3-02: **GDPR deletion automation (C27)** per S7.3
  - `gdpr_purge(user_id)` — respects legal holds, logs deletions
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py`

- P3-03: **Compliance deletion API (C29)** per S7.5
  - `POST /admin/compliance/purge` — admin role required
  - Target: `/home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py`

- P3-04: **Deletion audit log (C30)** per S7.6
  - Use legal_hold_log table from SM-2 Phase 3

- P3-05: **Write checkpoint**

#### Gate P3
- `python -c "from app.services.retention_policy import RetentionPolicy; print('OK')"`
- `python -c "from app.services.gdpr_service import gdpr_purge; print('OK')"`
- `make validate-local` passes

---

### SM-4 Phase 4 — Final Verification & Program Self-Audit
**Complexity:** M
**Estimated touch points:** 0 (verification) + bookkeeping

**Purpose:** Comprehensive validation for the ENTIRE program, not just SM-4.

#### Tasks
- P4-01: **Full validation** — `make validate-local`
- P4-02: **TypeScript** — `npx tsc --noEmit`
- P4-03: **Verify ALL new services import** — Every new file from SM-2, SM-3, SM-4
- P4-04: **Verify backend brain endpoints** — curl test GET/POST brain endpoints
- P4-05: **Re-run SM-1 readiness gates** — Verify intake readiness has not regressed
- P4-06: **Count files created and modified** — Full program summary
- P4-07: **Update CHANGES.md** — SM-4 changes
- P4-08: **Produce program completion report** — `/home/zaks/bookkeeping/docs/_qa_evidence/INTAKE-COL-V2-PROGRAM-COMPLETION.md`
  - Sub-mission results (SM-1 through SM-4)
  - Files created and modified across all sub-missions
  - Items completed vs. deferred
  - Validation results
  - Evidence paths for every AC across all sub-missions
- P4-09: **Fix CRLF and ownership** — `sed -i 's/\r$//'` on .sh files, `chown zaks:zaks` on files under /home/zaks/
- P4-10: **Write final checkpoint** — Mark entire program as complete

#### Gate P4
- `make validate-local` passes
- `npx tsc --noEmit` passes
- All new services import cleanly
- SM-1 readiness gates still PASS
- Program completion report written
- CHANGES.md updated

---

### SM-4 Acceptance Criteria

#### AC-SM4-1: Ambient Intelligence UI
Morning briefing, anomaly badges, momentum colors, citation indicators, MemoryStatePanel, SmartPaste, SentimentCoach, and CommandPalette components created per Surface 9.

#### AC-SM4-2: Compliance Pipeline
Retention policy engine, GDPR deletion service, and compliance purge admin endpoint exist.

#### AC-SM4-3: No Regressions
`make validate-local` and `npx tsc --noEmit` pass. SM-1 readiness gates still PASS.

#### AC-SM4-4: Bookkeeping
CHANGES.md updated. Program completion report produced with evidence for all AC across all sub-missions.

### SM-4 Lab Loop Configuration

```
TASK_ID=COL-V2-AMBIENT-001
REPO_DIR=/home/zaks/zakops-agent-api
GATE_CMD="make validate-local && cd apps/dashboard && npx tsc --noEmit"
```

### SM-4 Stop Condition

SM-4 and the entire program is DONE when all AC are met, program completion report is produced, and the checkpoint file reflects completion.

**Do NOT proceed to:**
- Running QA (QA-MASTER-PROGRAM-VERIFY-001) — that is a separate session
- Deploying to production
- Modifying COL-DESIGN-SPEC-V2.md

---

## Future Backlog (Explicitly Deferred)

These items are intentionally OUT OF SCOPE for this program. They are Large effort items that are not core to the current platform readiness or intelligence build:

| Item | Spec Section | Reason for Deferral |
|------|-------------|---------------------|
| C6: RAPTOR Hierarchy | S11.4 | Large effort, advanced RAG — build after HyDE proves value |
| C10: Risk Cascade Predictor | S14.3 | Large effort, portfolio-wide scan — needs production data |
| C11: Deal Precedent Network | S14.4 | Large effort, vector similarity — needs brain data at scale |
| C13: Broker Dossier | S14.6 | Medium effort, standalone feature — can be independent mission |
| C20: AmbientSidebar | S17.3 | Large effort — revisit after core ambient features prove useful |
| C31: HKDF Key Derivation | S6.7 | Large effort, crypto — enterprise compliance requirement |
| B6.1: PDF Export | S12 | Medium effort, standalone — can be independent mission |
| B6.3: Auto-refresh on brain version | S12 | Medium effort, depends on brain being actively used |
| B8.3: Periodic re-summarization | S4.5 | Medium effort, scheduler — operational concern for later |
| B9.2: AES-256-GCM encryption | S6 | Large effort, crypto — same as C31 |
| B2.2: Embedding-based replay similarity | S6.4 | Medium effort, improvement to existing feature |
| B2.3: Proposal extraction in replay | S6.4 | Medium effort, improvement to existing feature |
| B3.2: brain_diff computation | S6.5 | Medium effort, improvement to existing feature |
| B1.1: Semantic similarity in citation audit | S8.2 | Medium effort, needs RAG embeddings integrated first |

These items are recorded here so they are NOT dropped. They feed into the next program planning cycle.

---

## Program-Level Guardrails

1. **Scope: Build what's in the sources** — do not add features beyond the 17 findings, 7 readiness gates, and actionable items register. Do not redesign existing services.
2. **Generated files** — do not edit `*.generated.ts` or `*_models.py`. Use bridge files.
3. **Migration safety** — do not modify existing migration files (001-028). Only create new migrations.
4. **Backend repo boundary** — SM-1 is the primary backend modifier. SM-2 through SM-4 modify agent-api and dashboard only (except as noted).
5. **Fire-and-forget for enrichment** — post-turn enrichment MUST NOT block user response.
6. **Contract surface discipline** — run `make sync-all-types` if any API boundary changes.
7. **Surface 9 compliance** — all dashboard components follow design system rules.
8. **WSL safety** — strip CRLF from .sh files, fix ownership on files under /home/zaks/.
9. **Port 8090 is FORBIDDEN** — never use or reference.
10. **BackendClient mandatory** — no raw httpx in agent-api services for backend calls.
11. **Shadow-mode is inject-only** — no auto-promotion, no autonomous lifecycle actions from LangSmith.
12. **No silent failures** — if something can fail, it must fail loudly and observably. Fail-closed, not fail-open.
13. **Canonical truth must be preserved** — no split-brain, no shadow truth, no competing data stores.
<!-- Adopted from Improvement Area IA-15 -->
14. **Governance surfaces** — if touching dependencies: `make validate-surface10`; if touching error handling: `make validate-surface12`; if adding tests: `make validate-surface13`.

---

## Program-Level Executor Self-Check Prompts

### After Phase 0 (any sub-mission):
- [ ] "Did I verify the previous sub-mission is complete?"
- [ ] "Does `make validate-local` pass at baseline before I touch anything?"
- [ ] "Did I read the checkpoint file?"

### After every code change:
- [ ] "Am I using BackendClient, not raw httpx?"
- [ ] "Is this enrichment fire-and-forget or blocking the user response?"
- [ ] "Did I add a spec section reference in the docstring?"
- [ ] "Did I run `make sync-all-types` if I changed an API boundary?"
- [ ] "Am I creating shadow truth or using the canonical source?" <!-- DI-001 lesson -->

### Before marking a phase COMPLETE:
- [ ] "Did I run the phase gate checks?"
- [ ] "Did I update the checkpoint file?"
- [ ] "Did I create new .sh files? → CRLF stripped?"
- [ ] "Did I create files under /home/zaks/? → Ownership fixed?"

### Before marking a sub-mission COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Does `npx tsc --noEmit` pass?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I produce a completion report with evidence paths?"
- [ ] "Did I create ALL files listed in the sub-mission?"
<!-- Adopted from Improvement Area IA-10 -->
- [ ] "Do test names contain functional keywords for QA grep?"

---

## Program Stop Condition

This program is DONE when:
- SM-1: All 7 readiness gates PASS with evidence
- SM-2: All services wired and completing, compliance foundation built
- SM-3: Intelligence services built and importable
- SM-4: Ambient UI components created, compliance pipeline built
- `make validate-local` passes across the monorepo
- `npx tsc --noEmit` passes
- SM-1 readiness gates still PASS (no regression)
- Program completion report produced at `/home/zaks/bookkeeping/docs/_qa_evidence/INTAKE-COL-V2-PROGRAM-COMPLETION.md`
- All changes recorded in CHANGES.md
- Future backlog documented (not dropped)

**The successor mission (QA-MASTER-PROGRAM-VERIFY-001) is a separate session.** Do not combine QA with execution.

---

## Improvement Areas Reviewed
<!-- Required by MISSION-PROMPT-STANDARD.md v2.2 -->

| IA# | Status | Applied? | Notes |
|-----|--------|----------|-------|
| IA-1 | Ready | YES | Context checkpoints at every phase + explicit save points |
| IA-2 | Ready | YES | Crash recovery protocol at top of document |
| IA-3 | Under eval | NO | No token measurement tooling yet |
| IA-4 | Under eval | NO | Standard still evolving |
| IA-5 | Under eval | NO | Spec-first QA not applicable here |
| IA-6 | Under eval | NO | Piloting not yet started |
| IA-7 | Ready | YES | Multi-session continuity via checkpoint file |
| IA-8 | Under eval | NO | All sub-missions get full QA |
| IA-9 | Ready | N/A | This is a new doc, not an update |
| IA-10 | Ready | YES | Self-check includes test naming keywords |
| IA-11 | Under eval | NO | Artifact drift checker not yet built |
| IA-12 | Ready | NO | No "raise to X standard" findings in this program |
| IA-13 | Adopted | N/A | No TriPass design-mode in this program |
| IA-14 | Ready | NO | Not modifying hooks/rules/skills |
| IA-15 | Ready | YES | Governance surface references in guardrails |

---

*End of Master Program — ZAKOPS-INTAKE-COL-V2-001*
*Sub-missions: INTAKE-READY-001, COL-V2-CORE-001, COL-V2-INTEL-001, COL-V2-AMBIENT-001*
*Standard: Mission Prompt Standard v2.2*
