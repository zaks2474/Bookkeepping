# ZakOps Forensic Audit Report
## Evidence-Based Platform Analysis — February 1, 2026

**Label:** `claude_code`
**Auditor:** Claude Code (Opus 4.5)
**Method:** Deep codebase exploration + runtime inspection + document cross-reference
**Repos Analyzed:** `/home/zaks/zakops-agent-api/` (monorepo: agent-api, backend, dashboard)
**Documents Cross-Referenced:** `ZAKOPS_PROJECT_DEFINITION_V3.md`, `PROJECT_DEFINITION_FROM_CODE.md`

---

## Part 1: Corrected Project Definition Based on Current Code

### What ZakOps Actually Is Today

ZakOps is an **AI-powered deal lifecycle management platform for M&A acquisition pipelines**. It consists of three services in a monorepo (`zakops-agent-api`):

1. **Dashboard** (Next.js 15, port 3003) — Operator UI with deal kanban, quarantine triage, action queue, chat, approvals, and agent visibility
2. **Backend** (FastAPI, port 8091 for Deal Lifecycle + port 9200 for Orchestration) — Deal CRUD, action executors, quarantine, state machine, background worker
3. **Agent API** (FastAPI + LangGraph, port 8095) — Conversational AI agent with 5 tools, HITL approval gates, PostgreSQL checkpointing

Plus a **separate legacy stack** in `/home/zaks/Zaks-llm/` running on port 8080 ("SystemOps agent") that predates the monorepo and is still active in Docker.

### Actual End-to-End Data Flow

```
Broker sends email with CIM
    ↓
sync_acquisition_emails.py (cron, IMAP) downloads attachments
    ↓
Files land in /home/zaks/DataRoom/00-PIPELINE/Inbound/{deal}/
    ↓
zakops_analyzer.py (optional) generates deal_profile.json, scores, risks
    ↓
Backend ingests into quarantine_items table (PostgreSQL)
    ↓
Dashboard /quarantine page shows items for operator review
    ↓
Operator approves → deal created in deals table → enters pipeline
    ↓
Deal progresses: INBOUND → INITIAL_REVIEW → DUE_DILIGENCE → NEGOTIATION
                 → DOCUMENTATION → CLOSING → CLOSED_WON / CLOSED_LOST
    ↓
At each stage: operator can trigger action executors (draft LOI, valuation, etc.)
    ↓
Actions requiring approval go through HITL gates
    ↓
Agent API provides conversational interface (ask about deals, search, transition)
```

**Critical caveat:** The email-to-quarantine bridge (how files from DataRoom get INTO the PostgreSQL quarantine_items table) relies on the backend being able to read from the DataRoom filesystem OR on the legacy Zaks-llm zakops-api (port 8080) which mounts DataRoom directly. This bridge is the weakest link in the pipeline.

---

## Part 2: Gap List — V3 Document Claims vs. Code Reality

| # | V3 Claim | Code Reality | Severity |
|---|----------|-------------|----------|
| 1 | "39+ backend API endpoints across Deal Lifecycle and Orchestration services" | **True.** Both services have extensive real endpoints. Deal Lifecycle has 30+ and Orchestration has 25+. | OK |
| 2 | "17+ action executors covering email triage, document generation, valuation" | **True but partially stubbed.** Executor files exist with real class structures. `send_email` uses ToolGateway. `draft_email`, `generate_loi`, `build_valuation_model` call LLM but depend on vLLM being available and properly configured. | MEDIUM |
| 3 | "PostgreSQL 16, Port 5432" | **Partially true.** Docker-compose uses PostgreSQL 16-alpine. But there are **two PostgreSQL instances**: `zakops-postgres-1` (port 5432, DB: `zakops`, user: `zakops`) and `rag-db` (port 5434, DB: `crawlrag`). Agent API defaults to `food_order_db` in code (config.py:180) but `.env.development` overrides to `zakops_agent`. | HIGH |
| 4 | "Redis 7, Port 6379 — Cache, Sessions, Job queues" | **Redis runs but is NOT actually used in application code.** Docker-compose includes Redis and the backend has `REDIS_URL` in env, but no Redis client is imported or used in the Python backend or agent code. Sessions use cookies, not Redis. | HIGH |
| 5 | "Full observability stack (Prometheus/Grafana/Loki/Langfuse)" | **Docker-compose definitions exist** with Prometheus, Grafana, Loki, Promtail containers. Config files exist in `ops/observability/`. However: Langfuse is external/optional, and whether these containers are actually running is unclear (not seen in `docker ps` output from legacy stack). OTEL instrumentation is installed in requirements.txt. | MEDIUM |
| 6 | "Blue/green deployment with zero-downtime switching" | **Files exist** in `deployments/bluegreen/` but this is aspirational infrastructure, not currently deployed. | LOW |
| 7 | "31 quality gate scripts across 10 phases" | **Files exist** in `tools/gates/`. These are shell scripts. Whether they pass is unknown — likely many would fail against current runtime. | LOW |
| 8 | "6 chaos engineering scenarios" | **Files exist** in `tools/chaos/`. Aspirational, not routinely run. | LOW |
| 9 | "CI/CD pipeline with automated testing" | **GitHub Actions workflows exist** (`.github/workflows/ci.yml`, `deploy.yaml`). CI runs lint+typecheck+test. Deploy is manual trigger. Whether CI is green is unknown. | MEDIUM |
| 10 | "LangGraph conversational agent with 4 tools" | **Actually 5 tools:** `duckduckgo_search`, `transition_deal`, `get_deal`, `search_deals`, `list_deals`. V3 says 4, code has 5. | MINOR |
| 11 | "Conversations survive server restarts" (LangGraph checkpointing) | **True.** `AsyncPostgresSaver` checkpointing is properly configured in graph.py. | OK |
| 12 | "Deal Lifecycle API port 8091" | **Inconsistent.** `.env.example` says `DEAL_LIFECYCLE_API_PORT=8090`. Docker-compose maps 8091:8091. `Dockerfile.api` defaults to 8090. `scripts/dev.sh` uses 8091. The runtime is 8091 but defaults conflict. | HIGH |
| 13 | "Orchestration API port 9200" | **Port conflict in docker-compose.** `backend-orchestration` is mapped to `8091:8091` (same as deal-lifecycle!) not `9200:9200`. This means you can't run both from docker-compose simultaneously. | CRITICAL |
| 14 | "Session cookies" for Dashboard auth | **AUTH_REQUIRED defaults to false.** Auth middleware creates a mock "dev" operator when disabled. No real session management is active in dev mode. | MEDIUM |
| 15 | "Deferred actions for scheduled future operations" | **True.** `DeferredActionQueue` exists with real endpoints. | OK |
| 16 | V3 says "MSP market" in executive summary (from code doc) | V3 corrected this to "M&A". The code-generated doc incorrectly said MSP. | FIXED in V3 |
| 17 | "Background worker with lease-based execution" | **True.** `actions_runner.py` has real lease logic with crash recovery. | OK |
| 18 | "Outbox Pattern (Reliable Event Delivery)" | **Code exists** (`outbox` table in migrations, `OUTBOX_ENABLED` env var). Whether the outbox processor actually runs as a background task is unclear. | MEDIUM |

---

## Part 3: Misconfiguration List

### CRITICAL

| # | What's Wrong | Where | Impact |
|---|-------------|-------|--------|
| 1 | **Agent API default DB is `food_order_db`** | `apps/agent-api/app/core/config.py:180` | If `.env.development` is missing or not loaded, agent connects to wrong database. Template/scaffold leftover. |
| 2 | **Port conflict: both backend services claim 8091** | `deployments/docker/docker-compose.yml` lines 37 and 52 | Cannot run deal-lifecycle AND orchestration from same compose file. Port collision. |
| 3 | **Backend `.env.example` says port 8090, runtime uses 8091** | `apps/backend/.env.example:32` vs `docker-compose.yml:37` | Developers following `.env.example` will run on wrong port. Dashboard expects 8091. |
| 4 | **Two separate PostgreSQL databases in play** | `zakops` (monorepo compose) vs `zakops_agent` (agent-api .env.development) | Agent API and Backend may be writing to different databases unless env vars are carefully aligned. |

### HIGH

| # | What's Wrong | Where | Impact |
|---|-------------|-------|--------|
| 5 | **Redis configured but never used** | `docker-compose.yml:101-113`, no Redis imports in Python code | Wasted container resources. V3 doc claims Redis for sessions/queues/cache — this is false. |
| 6 | **`agent-client.ts` defaults to port 9200** | `apps/dashboard/src/lib/agent-client.ts:26` | If `NEXT_PUBLIC_API_URL` env var is missing, dashboard calls wrong port. Overridden by `.env.local` but fragile. |
| 7 | **Auth disabled by default everywhere** | Backend: `AUTH_REQUIRED=false`, Agent: `AGENT_JWT_ENFORCE=false` | All endpoints accessible without authentication in dev. Production requires explicit opt-in. |
| 8 | **Migration SQL not auto-executed** | `apps/agent-api/migrations/001_approvals.sql` | SQLModel creates basic tables on startup, but PL/pgSQL functions (`cleanup_expired_approvals`, `reclaim_stale_claims`) are only in the SQL file and must be manually applied. |

### MEDIUM

| # | What's Wrong | Where | Impact |
|---|-------------|-------|--------|
| 9 | **Legacy Zaks-llm zakops-api on port 8080 still running** | `/home/zaks/Zaks-llm/docker-compose.yml:88-117` | Competing "zakops" service with different architecture. Confusion about which service is authoritative. |
| 10 | **DASHBOARD_SERVICE_TOKEN hardcoded in docker-compose** | `deployments/docker/docker-compose.yml:20,77` | Token `k-bG0Us8LHBso4S4OnjqVOXkCNR_C8smNqtflzukWpo` is in the compose file and `.env.local`. Should be in a secrets-only file. |
| 11 | **DataRoom mount not in monorepo docker-compose** | `deployments/docker/docker-compose.yml` | Backend in docker can't access `/home/zaks/DataRoom` unless running on host network or with explicit mounts. The Zaks-llm compose mounts it but the monorepo compose doesn't. |

---

## Part 4: Broken Pipeline Analysis

### Pipeline: Email Inbound → Quarantine → Deal

```
sync_acquisition_emails.py (IMAP/cron)
    ↓ writes to DataRoom filesystem
    ✗ BREAK: No automatic bridge from filesystem → quarantine_items DB table
    ↓ (requires manual: legacy zakops-api:8080 has DataRoom mounts,
       monorepo backend:8091 does NOT mount DataRoom in docker)
Quarantine page shows items
    ↓
Operator approves → deal created
    ✓ WORKS (if items exist in DB)
```

**Verdict:** Email ingestion works to filesystem. Filesystem → DB bridge is manual/broken.

### Pipeline: Dashboard → Backend API → Database

```
Dashboard (3003) calls /api/*
    ↓ Next.js rewrites to http://localhost:8091
    ↓ Backend reads from PostgreSQL (zakops DB)
    ✓ WORKS when backend is running and DB has data
    ✗ BREAK: If backend not running, dashboard silently returns empty arrays (graceful degradation hides failures)
```

**Verdict:** Works when stack is up. Silent failures mask problems.

### Pipeline: Dashboard → Agent API → LLM → Tool → Backend

```
Dashboard chat page calls /api/chat
    ↓ Proxies to Agent API (8095)
    ↓ LangGraph invokes LLM (vLLM on 8000)
    ↓ LLM decides to call tool (e.g., get_deal)
    ↓ Tool makes HTTP call to Backend (8091)
    ↓ Response flows back through graph
    ✓ WORKS end-to-end IF: vLLM is running, backend is running, DB has data
    ✗ BREAK: If vLLM is down, circular fallback tries OpenAI (needs API key)
    ✗ BREAK: If both fail, user gets "All providers failed" error
```

**Verdict:** Works when all services are healthy. Fragile chain with 4 hops.

### Pipeline: Action Execution (Background Worker)

```
Operator triggers action on dashboard
    ↓ POST /api/actions → creates action in DB
    ↓ Background worker (actions_runner.py) dequeues
    ↓ Acquires lease → executes executor
    ↓ Executor calls LLM or external service
    ✓ WORKS conceptually
    ✗ BREAK: actions_runner.py must be running as separate process
    ✗ BREAK: In docker-compose, it's a separate container that depends on postgres
    ✗ BREAK: In dev (no docker), must be started manually
```

**Verdict:** Architecture is sound. Deployment gap — worker may not be running.

### Pipeline: HITL Approval Flow

```
Agent proposes transition_deal
    ↓ LangGraph interrupt() pauses graph
    ↓ Approval record created in DB
    ↓ Dashboard /approvals page shows pending
    ↓ Operator approves
    ↓ Graph resumes, executes tool
    ✓ WORKS with crash recovery (stale claim reclaim)
    ✗ POTENTIAL BREAK: Approval SQL functions not auto-applied
```

**Verdict:** Best-implemented feature. Works if migration SQL is applied.

---

## Part 5: The Contrarian View — What's Really Happening

### Finding 1: You Have Two Competing Platforms

There are **two separate "ZakOps" systems** running simultaneously:

1. **Legacy Zaks-llm stack** (`/home/zaks/Zaks-llm/`) — port 8080, mounts DataRoom, has its own zakops-api, connects to vLLM, has MCP servers. This is the system that actually touches email data and DataRoom files.

2. **Monorepo stack** (`/home/zaks/zakops-agent-api/`) — ports 8091/8095/3003, has proper architecture (LangGraph, state machine, HITL), but runs in Docker without DataRoom mounts.

**The V3 doc describes the monorepo as if it's the whole system, but the legacy stack is still doing critical work (email sync, DataRoom file management, vLLM hosting).**

### Finding 2: "It Runs" Does Not Mean "It Works"

The dashboard returns empty arrays when the backend is unreachable. This means:
- You can open the dashboard and see a clean, functioning UI
- The deals page shows an empty kanban board (looks intentional)
- The quarantine page shows no items (looks like no new emails)
- The actions page shows nothing (looks like nothing is pending)

**You cannot tell from the UI whether the backend is connected or not.**

### Finding 3: Multiple Databases, No Migration Certainty

- `zakops` database (docker-compose, user: zakops)
- `zakops_agent` database (agent-api .env.development)
- `food_order_db` (agent-api code default — leftover)
- `crawlrag` database (RAG service)
- SQLite files in DataRoom (legacy deal registry)

**There is no single migration command that sets up all schemas correctly.** The backend has SQL migration files. The agent-api uses SQLModel auto-create plus a separate SQL file. The legacy stack uses SQLite. Data may exist in one database but not another.

### Finding 4: The Observability Stack Is Theoretical

Prometheus, Grafana, Loki, and Promtail are defined in docker-compose but:
- The application code has OTEL SDKs installed but no evidence of custom metrics being emitted
- Prometheus scrape targets point to services that may not expose `/metrics`
- Grafana dashboards exist in `ops/observability/grafana/dashboards/` but may not match actual metrics
- Langfuse keys are empty in `.env.development`

### Finding 5: The Email-to-Deal Pipeline Has a Gap

The most critical business workflow — broker email arrives, gets processed, becomes a deal — has a discontinuity:
- `sync_acquisition_emails.py` writes to the filesystem (DataRoom)
- `zakops_analyzer.py` enriches files on the filesystem
- But the monorepo backend expects deals in PostgreSQL
- The bridge between filesystem and database is either the legacy port-8080 API or manual creation

---

## Part 6: Prioritized Fix Plan

### Tier 1: Foundation (Fix First)

| Priority | Fix | Why | Effort |
|----------|-----|-----|--------|
| P0 | **Fix agent-api default DB from `food_order_db` to `zakops_agent`** | Prevents silent connection to wrong DB | 1 line |
| P0 | **Fix docker-compose port conflict** (orchestration should be 9200:9200, not 8091:8091) | Cannot run full stack from compose | 1 line |
| P0 | **Fix `.env.example` port from 8090 to 8091** | Align documentation with reality | 1 line |
| P1 | **Run agent-api migration SQL** (`001_approvals.sql`) against actual database | Missing PL/pgSQL functions for crash recovery | Manual SQL apply |
| P1 | **Add DataRoom volume mount to monorepo docker-compose backend** | Backend needs access to deal files | 2 lines in compose |

### Tier 2: Integration (Wire Things Together)

| Priority | Fix | Why |
|----------|-----|-----|
| P2 | **Unify database strategy**: One PostgreSQL instance, one `zakops` database, both backend and agent-api schemas | Eliminates multi-DB confusion |
| P2 | **Build email→quarantine bridge**: Script or endpoint that reads DataRoom inbound files and creates quarantine_items in PostgreSQL | Closes the biggest pipeline gap |
| P2 | **Add health indicators to dashboard**: Show backend connectivity status in the UI, not just silent empty states | Operator can see when things are broken |
| P2 | **Remove Redis from docker-compose** (or actually implement Redis caching) | Eliminates false claim in docs, frees resources |

### Tier 3: Hardening (Make It Production-Ready)

| Priority | Fix | Why |
|----------|-----|-----|
| P3 | **Enable AUTH_REQUIRED=true** and configure real session management | Security baseline |
| P3 | **Decommission legacy Zaks-llm zakops-api** (port 8080) or clearly document its role | Eliminate dual-system confusion |
| P3 | **Verify and fix observability stack**: Ensure Prometheus scrapes real metrics, Grafana dashboards show real data | Operational visibility |
| P3 | **Run quality gates** (`tools/gates/`) against current stack, fix failures | Validate actual readiness |
| P3 | **Set up automatic migration execution** on service startup | Prevent schema drift |

### Tier 4: Polish

| Priority | Fix | Why |
|----------|-----|-----|
| P4 | Fix `agent-client.ts` default port from 9200 to 8091 | Correct fallback behavior |
| P4 | Remove `DASHBOARD_SERVICE_TOKEN` from docker-compose, use env-only | Secret hygiene |
| P4 | Document which services are required vs optional (RAG is optional profile) | Operational clarity |

---

## Summary

**What you truly have:** A well-architected monorepo with real implementations of deal lifecycle management, a functional LangGraph agent with HITL, and a comprehensive dashboard. The code quality is solid. The architecture patterns (idempotency, outbox, state machine, checkpointing) are genuinely well-implemented.

**What's missing or broken:** The wiring between components. Two competing platforms (legacy + monorepo). Multiple databases with no unified migration. A critical gap in the email-to-database pipeline. Silent failure modes that mask connectivity issues. Configuration defaults that conflict with runtime reality.

**Where to focus:** Fix the P0 config issues (30 minutes of work), then build the email→quarantine bridge, then unify the database strategy. Once those three things are done, you'll have a genuinely working end-to-end system.

The platform is not broken in a fundamental sense — the architecture is sound and the code is real. It's broken in a **wiring and configuration** sense, which is fixable.
