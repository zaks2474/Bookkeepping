# ZakOps Cognitive Operating Layer — Design Specification V2

**Status**: Design Specification (patched, implementation-ready)
**Author**: Claude Code (Opus 4.6) + Zak
**Date**: 2026-02-13
**Base**: COL-DESIGN-SPEC-V1 (2026-02-12, 1,861 lines)
**Patches**: 23 gap fixes (3 CRITICAL, 5 HIGH, 12 MEDIUM, 3 LOW)
**Enhancements**: 45 improvement ideas + 13 Quick Wins merged from Innovation Master
**Scope**: Transform chat from UI feature to cognitive operating layer for the ZakOps M&A platform
**Canonical Principle**: Every design decision is grounded in codebase evidence from prior investigations

### V2 Change Summary

| Category | Count | Details |
|----------|-------|---------|
| CRITICAL gap fixes | 3 | deal_budgets FK, user_id type standardization, partition automation |
| HIGH gap fixes | 5 | Middleware routing, service token auth, contract surface, cross-DB integrity, SQLite migration |
| MEDIUM gap fixes | 12 | Redundant columns, UNIQUE constraints, migration tracking, outbox pattern, backfill, PII pipeline, tests, encryption, email integration, proposal type, rollbacks, mat view |
| LOW gap fixes | 3 | MCP governance, SSE catalog, proposal concurrency |
| Improvements integrated | 45 | Across 11 categories (RAG, Agent, Memory, Structured Output, Cognitive, Predictive, Collaboration, Ambient, Security, UX, Infrastructure) |
| Quick Wins approved | 13 | All LOW complexity, HIGH impact |
| New sections | 5 | S18: RAG Enhancement, S19: Agent Architecture, S20: Cognitive Intelligence, S21: Ambient Intelligence, S22: System Classification Table |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Canonical Storage Unification](#3-canonical-storage-unification)
4. [Deal Brain v2](#4-deal-brain-v2)
5. [Summarization & Tiered Memory](#5-summarization--tiered-memory)
6. [Deterministic Replay & Counterfactual Analysis](#6-deterministic-replay--counterfactual-analysis)
7. [Prompt Injection & Input-Side Defenses](#7-prompt-injection--input-side-defenses)
8. [Citation Validation & Self-Critique](#8-citation-validation--self-critique)
9. [Tool Scoping & Least Privilege](#9-tool-scoping--least-privilege)
10. [Multi-User Hardening](#10-multi-user-hardening)
11. [Delete, Retention, Legal Hold, GDPR](#11-delete-retention-legal-hold-gdpr)
12. [Export, Deal Attachment & Living Deal Memo](#12-export-deal-attachment--living-deal-memo)
13. [Cost Governance & Observability](#13-cost-governance--observability)
14. [Offline & Degraded Mode](#14-offline--degraded-mode)
15. [Proposal Pipeline Hardening](#15-proposal-pipeline-hardening)
16. [Implementation Roadmap](#16-implementation-roadmap)
17. [Risk Register](#17-risk-register)
18. [RAG & Retrieval Enhancement Architecture](#18-rag--retrieval-enhancement-architecture)
19. [Agent Architecture & Autonomous Capabilities](#19-agent-architecture--autonomous-capabilities)
20. [Cognitive Intelligence & Decision Support](#20-cognitive-intelligence--decision-support)
21. [Ambient Intelligence & Predictive Features](#21-ambient-intelligence--predictive-features)
22. [System Classification Table](#22-system-classification-table)
23. [Appendices](#23-appendices)

---

## 1. Executive Summary

### What Exists Today

The ZakOps chat system is a **well-engineered UI feature with evidence grounding and an execution pipeline**. It has:

- **Two independent chat backends**: Backend orchestrator (port 8091, evidence-grounded, 6 proposal types) and Agent API LangGraph (port 8095, 8 tools, HITL approval flow)
- **Three disconnected storage layers**: localStorage (dashboard), SQLite (backend `chat_persistence.py`), PostgreSQL (LangGraph checkpoints in `zakops_agent`)
- **Strong output sanitization**: HTML escaping, pattern detection, PII redaction at 3 enforcement points (`output_validation.py`)
- **A proto-Deal-Brain**: `DealContextSummary` in `agent_context_summaries` table with keyword-only fact extraction (no LLM summarization)
- **A decision audit trail**: `decision_ledger` with tool selection reasoning, deal_id correlation, approval tracking

### What V2 Delivers (Beyond V1's 12-Gap Closure)

V2 takes the V1 foundation and:
1. **Fixes 23 structural gaps** that would cause migration failures, type mismatches, data orphans, and partition time-bombs
2. **Integrates 45 innovation improvements** spanning RAG enhancement, agent autonomy, cognitive intelligence, predictive analytics, ambient features, and security hardening
3. **Merges 13 approved Quick Wins** — each implementable in 1-3 days with no architectural changes
4. **Classifies every component** into three execution buckets: Prototype-Critical, Functional Expansion, Production/Enterprise

### Design Principles

1. **PostgreSQL is the single source of truth** — all other stores are caches or supplements
2. **Every design decision references existing code** — file paths, line numbers, current schemas
3. **Backward compatibility** — dual-write during migration, no big-bang cutover
4. **Least privilege by default** — tools, scopes, and roles are restrictive until explicitly expanded
5. **Evidence over assertion** — every claim about current state is verifiable in the codebase
6. **[V2] Deal Brain is the keystone** — 14 of 18 cognitive features depend on it; it is P0 alongside storage
7. **[V2] User identity is canonical** — `user_id VARCHAR(255)` everywhere, mapped via cross-reference (fixes GAP-C2)
8. **[V2] Partitions are automated** — no static partitions; pg_partman + cron + DEFAULT safety net (fixes GAP-C3)

---

## 2. Architecture Overview

### Current Architecture (As-Is)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Dashboard (:3003)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ localStorage │  │ chat/page.tsx│  │ ChatHistoryRail.tsx       │ │
│  │ (20 sessions)│  │ (SSE client) │  │ (5 actions, CSS hover)   │ │
│  └──────────────┘  └──────┬───────┘  └───────────────────────────┘ │
│                           │                                         │
│  middleware.ts ───────────┼──── /api/* proxy (15s timeout) ────────┤
└───────────────────────────┼─────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────────┐
│  Backend (:8091)     │    │  Agent API (:8095)        │
│  ┌────────────────┐  │    │  ┌──────────────────────┐ │
│  │ chat_orchestr. │  │    │  │ LangGraph (4 nodes)  │ │
│  │ (6 proposals)  │  │    │  │ chat → tool_call →   │ │
│  │ EvidenceBuilder│  │    │  │ approval_gate →      │ │
│  │ LLM Router     │  │    │  │ execute_approved     │ │
│  │ SQLite persist │  │    │  └──────────────────────┘ │
│  └────────────────┘  │    │  ┌──────────────────────┐ │
│  ┌────────────────┐  │    │  │ PostgreSQL           │ │
│  │ PostgreSQL     │  │    │  │ (zakops_agent)       │ │
│  │ (zakops)       │  │    │  │ - checkpoints        │ │
│  │ - deals        │  │    │  │ - decision_ledger    │ │
│  │ - actions      │  │    │  │ - approvals          │ │
│  │ - events       │  │    │  │ - tool_executions    │ │
│  │ - artifacts    │  │    │  │ - audit_log          │ │
│  └────────────────┘  │    │  └──────────────────────┘ │
└──────────────────────┘    └──────────────────────────┘
```

### Target Architecture (V2 — To-Be)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Dashboard (:3003)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────────┐   │
│  │ localStorage │  │ chat/page.tsx│  │ ChatHistoryRail + DealBrain │   │
│  │ (CACHE ONLY) │  │ (SSE client) │  │ + MemoryStatePanel          │   │
│  │ [PGlite for  │  │ + Smart Paste│  │ + CostTab, ExportButton     │   │
│  │  offline SQL] │  │ + @Agent     │  │ + FactLineageExplorer       │   │
│  └──────────────┘  └──────┬───────┘  │ + MomentumScore badge       │   │
│                           │          └─────────────────────────────┘   │
│  middleware.ts ─── JWT ───┼──── /api/* proxy ─── /api/v1/chatbot/* ───┤
│  [V2: routes chatbot to   │                                            │
│   agent-api directly]     │                                            │
└───────────────────────────┼────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────────────────────────┐
│  Backend (:8091)     │    │  Agent API (:8095)                        │
│  ┌────────────────┐  │    │  ┌──────────────────────────┐            │
│  │ chat_orchestr. │  │    │  │ LangGraph (expanded)     │            │
│  │ → ChatRepo     │──┼────┼──│ → scope-filtered tools   │            │
│  │ → Summarizer   │  │    │  │ → injection guard        │            │
│  │ → InjectionGrd │  │    │  │ → snapshot writer        │            │
│  │ → CostWriter   │  │    │  │ → reflexion critique     │            │
│  │ → BrainExtract │  │    │  │ → canary token scanner   │            │
│  │ → GhostDetect  │  │    │  │ → ghost knowledge detect │            │
│  └────────────────┘  │    │  └──────────────────────────┘            │
│  ┌────────────────┐  │    │  ┌──────────────────────────────────────┐│
│  │ PostgreSQL     │  │    │  │ PostgreSQL (zakops_agent)            ││
│  │ (zakops)       │  │    │  │ CANONICAL CHAT STORE:                ││
│  │ - deals        │  │    │  │ - chat_threads (NEW)                 ││
│  │ - deal_brain   │  │    │  │ - chat_messages (NEW)                ││
│  │ - deal_access  │  │    │  │ - session_summaries (NEW)            ││
│  │ - deal_budgets │  │    │  │ - turn_snapshots (NEW, partitioned)  ││
│  │ - artifacts    │  │    │  │ - cost_ledger (NEW, partitioned)     ││
│  │ - cost_ledger  │  │    │  │ - user_identity_map (NEW)            ││
│  │ - outbox       │  │    │  │ + checkpoints (existing)             ││
│  └────────────────┘  │    │  │ + decision_ledger (existing)         ││
│                       │    │  │ + user, session (migrated from SQLite)│
│  ┌────────────────┐  │    │  └──────────────────────────────────────┘│
│  │ Outbox Worker  │  │    │  ┌──────────────────────────────────────┐│
│  │ (async brain   │  │    │  │ Background Workers:                  ││
│  │  extraction)   │  │    │  │ - Memory consolidation (idle >10min) ││
│  └────────────────┘  │    │  │ - Deal reconciliation (hourly)       ││
│                       │    │  │ - Partition automation (pg_cron)     ││
│                       │    │  │ - Morning briefing generator (daily) ││
│                       │    │  └──────────────────────────────────────┘│
└──────────────────────┘    └──────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Rationale | Evidence |
|----------|-----------|----------|
| `zakops_agent` PostgreSQL as canonical store | Already has checkpoints, ledger, approvals; only store with ACID + indexes + backup | `config.py:210` — 3 checkpoint tables already here |
| Backend orchestrator owns summarization | Has EvidenceBuilder, 3-tier LLM router, cost-aware model selection | `chat_llm_router.py:40-213` — DETERMINISTIC/FLASH/PRO tiers |
| JWT replaces service token for user identity | Service token gives all requests `user_id=0` | `auth.py:163-220` — `get_session_or_service()` |
| LangGraph checkpoint schema untouched | Standard LangGraph tables; ownership enforced via join table | `graph.py:851` — `AsyncPostgresSaver` standard setup |
| Deal Brain lives in `zakops` (backend DB) | Deals, events, actions all in `zakops`; brain is a deal-level concern | `context_store.py:47-125` — existing proto-brain is backend-side |
| **[V2] user_id standardized as VARCHAR(255)** | Existing `decision_ledger`, `approvals`, `user_preferences` all use string IDs; INTEGER would require casting everywhere | GAP-C2 fix |
| **[V2] Outbox pattern for cross-DB writes** | Chat writes to `zakops_agent`, Deal Brain writes to `zakops`; outbox ensures eventual consistency without distributed transactions | GAP-M4 fix |
| **[V2] SQLite user/session migrated to PostgreSQL** | Eliminates 3rd storage engine; GDPR deletion becomes 2-database instead of 3 | GAP-H5 fix |
| **[V2] pg_partman for partition automation** | Static partitions are a time bomb; pg_partman + pg_cron creates partitions automatically | GAP-C3 fix |

---

## 3. Canonical Storage Unification

### 3.1 Current State (Evidence)

| Layer | Location | What It Stores | Evidence |
|-------|----------|----------------|----------|
| localStorage | Browser | Thread list (20 max), session data blobs | `chat-history.ts:10-12` — `HISTORY_KEY`, `ARCHIVE_PREFIX`, `MAX_HISTORY=20` |
| SQLite | `/home/zaks/scripts/email_ingestion/chat_persistence.py` | Full messages (role, content, timestamp, citations, proposals, timings, provider, cache_hit) | `chat_orchestrator.py:44-48` — `PERSISTENCE_ENABLED` flag |
| LangGraph checkpoints | PostgreSQL `zakops_agent` | Full GraphState per node transition (messages, memory, tool calls, approval status) | `graph.py:848-863` — `AsyncPostgresSaver` + 3 tables |
| Decision ledger | PostgreSQL `zakops_agent` | Tool selection, args, results (500 char preview), latency, tokens | `002_decision_ledger.sql:7-59` |

**Problems with current state:**
- No single "list all threads for user X" query possible
- Delete from localStorage doesn't touch SQLite or checkpoints
- SQLite has no user isolation (single-user store)
- Dashboard `GET /api/chat/session/{id}` is a placeholder returning empty (`route.ts:9-23`)

### 3.2 User Identity Standardization [V2 — fixes GAP-C2]

**Problem**: V1 used `user_id INTEGER` everywhere, but existing tables use mixed types:
- `decision_ledger.user_id` → `VARCHAR(255)`
- `approvals.actor_id` → `VARCHAR(255)`
- `user_preferences.user_id` → `VARCHAR(255)` with DEFAULT 'default'
- Backend operators → UUID strings

**Resolution**: All new tables use `user_id VARCHAR(255)` to match existing schema. A cross-reference mapping table bridges identity systems:

```sql
-- In migration 004_chat_canonical_store.sql
CREATE TABLE IF NOT EXISTS user_identity_map (
    canonical_id    VARCHAR(255) PRIMARY KEY,   -- The ID used in chat tables
    email           VARCHAR(255) UNIQUE,
    display_name    VARCHAR(255),
    auth_provider   VARCHAR(50) DEFAULT 'local', -- local, jwt, service
    external_ids    JSONB DEFAULT '{}'::jsonb,   -- {"backend_uuid": "...", "agent_sqlite_id": N}
    role            VARCHAR(20) DEFAULT 'VIEWER',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_seen       TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_role CHECK (role IN ('VIEWER', 'OPERATOR', 'APPROVER', 'ADMIN'))
);
```

**Migration path**: Phase 1 uses X-User-Id header (string). Phase 2 uses JWT with `sub` claim mapped to `canonical_id`.

### 3.3 Canonical Schema

#### Migration: `004_chat_canonical_store.sql` (Agent API)

```sql
-- ============================================================
-- Migration 004: Canonical Chat Store
-- Part of: COL-DESIGN-SPEC-V2, Section 3
-- Fixes: GAP-C2 (user_id type), GAP-M1 (redundant deal_id),
--         GAP-M2 (UNIQUE constraint), GAP-M3 (migration tracking),
--         GAP-H5 (SQLite migration)
-- ============================================================

BEGIN;

-- Record migration
INSERT INTO schema_migrations (version, description, applied_at)
VALUES ('004', 'Canonical Chat Store (COL V2)', NOW())
ON CONFLICT DO NOTHING;

-- ----- user_identity_map -----
CREATE TABLE IF NOT EXISTS user_identity_map (
    canonical_id    VARCHAR(255) PRIMARY KEY,
    email           VARCHAR(255) UNIQUE,
    display_name    VARCHAR(255),
    auth_provider   VARCHAR(50) DEFAULT 'local',
    external_ids    JSONB DEFAULT '{}'::jsonb,
    role            VARCHAR(20) DEFAULT 'VIEWER',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_seen       TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_role CHECK (role IN ('VIEWER', 'OPERATOR', 'APPROVER', 'ADMIN'))
);

-- ----- chat_threads -----
CREATE TABLE IF NOT EXISTS chat_threads (
    id              VARCHAR(255) PRIMARY KEY,
    user_id         VARCHAR(255) NOT NULL,     -- [V2: VARCHAR, not INTEGER — GAP-C2]
    deal_id         VARCHAR(20),
    scope_type      VARCHAR(20) NOT NULL DEFAULT 'global',
    title           VARCHAR(500),
    preview         TEXT,
    pinned          BOOLEAN DEFAULT FALSE,
    archived        BOOLEAN DEFAULT FALSE,
    deleted         BOOLEAN DEFAULT FALSE,
    deleted_at      TIMESTAMPTZ,
    legal_hold      BOOLEAN DEFAULT FALSE,
    legal_hold_reason TEXT,
    legal_hold_set_by VARCHAR(255),            -- [V2: VARCHAR — GAP-C2]
    legal_hold_set_at TIMESTAMPTZ,
    compliance_tier BOOLEAN DEFAULT FALSE,
    message_count   INTEGER DEFAULT 0,
    last_summary_version INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active     TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_scope CHECK (scope_type IN ('global', 'deal', 'document')),
    CONSTRAINT chk_delete CHECK (
        (deleted = FALSE AND deleted_at IS NULL) OR
        (deleted = TRUE AND deleted_at IS NOT NULL)
    )
);

CREATE INDEX idx_threads_user ON chat_threads(user_id);
CREATE INDEX idx_threads_deal ON chat_threads(deal_id) WHERE deal_id IS NOT NULL;
CREATE INDEX idx_threads_active ON chat_threads(user_id, last_active DESC) WHERE deleted = FALSE;
CREATE INDEX idx_threads_deleted ON chat_threads(deleted_at) WHERE deleted = TRUE;

-- ----- chat_messages -----
CREATE TABLE IF NOT EXISTS chat_messages (
    id              VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    thread_id       VARCHAR(255) NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    user_id         VARCHAR(255) NOT NULL,     -- [V2: VARCHAR — GAP-C2]
    -- [V2: deal_id REMOVED — GAP-M1: redundant, always derivable from thread.deal_id]
    role            VARCHAR(20) NOT NULL,
    content         TEXT NOT NULL,
    citations       JSONB DEFAULT '[]'::jsonb,
    proposals       JSONB DEFAULT '[]'::jsonb,
    evidence_summary JSONB,
    timing          JSONB,
    provider        VARCHAR(50),
    cache_hit       BOOLEAN DEFAULT FALSE,
    turn_number     INTEGER NOT NULL,
    parent_message_id VARCHAR(36),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_role CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    CONSTRAINT uq_thread_turn UNIQUE (thread_id, turn_number)  -- [V2: GAP-M2 — explicit UNIQUE]
);

CREATE INDEX idx_messages_thread ON chat_messages(thread_id, turn_number);
CREATE INDEX idx_messages_user ON chat_messages(user_id);

-- ----- thread_ownership -----
CREATE TABLE IF NOT EXISTS thread_ownership (
    thread_id       VARCHAR(255) PRIMARY KEY
                    REFERENCES chat_threads(id) ON DELETE CASCADE,  -- [V2.1: FK + CASCADE added]
    user_id         VARCHAR(255) NOT NULL,     -- [V2: VARCHAR — GAP-C2]
    deal_id         VARCHAR(20),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ownership_user ON thread_ownership(user_id);
CREATE INDEX idx_ownership_user_thread ON thread_ownership(user_id, thread_id);  -- [V2.1: composite for ownership verification queries]

-- ----- session_summaries -----
CREATE TABLE IF NOT EXISTS session_summaries (
    id              SERIAL PRIMARY KEY,
    thread_id       VARCHAR(255) NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    summary_text    TEXT NOT NULL,
    facts_json      JSONB DEFAULT '[]'::jsonb,
    decisions_json  JSONB DEFAULT '[]'::jsonb,
    open_questions  JSONB DEFAULT '[]'::jsonb,
    covers_turns    INTEGER[] NOT NULL,
    token_count     INTEGER,
    model_used      VARCHAR(100),
    memory_tier     VARCHAR(20) DEFAULT 'recall',  -- [V2: for MemGPT tiered memory]
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(thread_id, version)
);

CREATE INDEX idx_summaries_thread ON session_summaries(thread_id, version DESC);

-- ----- turn_snapshots (partitioned) -----
CREATE TABLE IF NOT EXISTS turn_snapshots (
    id                      VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    thread_id               VARCHAR(255) NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    turn_number             INTEGER NOT NULL,
    user_id                 VARCHAR(255) NOT NULL,  -- [V2: VARCHAR — GAP-C2]
    -- [V2: deal_id derivable from thread, not duplicated here]

    -- What the model saw (INPUT)
    rendered_system_prompt  TEXT NOT NULL,
    evidence_context        TEXT,
    evidence_hash           VARCHAR(64),
    post_trim_messages      JSONB NOT NULL,
    rolling_summary         TEXT,
    injection_scan_result   JSONB,

    -- Model parameters
    model_name              VARCHAR(100) NOT NULL,
    provider                VARCHAR(50) NOT NULL,
    temperature             FLOAT,
    max_completion_tokens   INTEGER,
    tool_definitions        JSONB,

    -- What the model produced (OUTPUT)
    raw_completion          TEXT,
    proposals_extracted     JSONB DEFAULT '[]'::jsonb,
    citations_extracted     JSONB DEFAULT '[]'::jsonb,
    completion_tokens       INTEGER,
    prompt_tokens           INTEGER,
    total_tokens            INTEGER,

    -- [V2: Reflexion metadata]
    critique_result         JSONB,  -- {passed: bool, issues: [], refinement_count: int}

    -- Metadata
    prompt_version          VARCHAR(50),
    prompt_hash             VARCHAR(64),
    latency_ms              INTEGER,
    routing_decision        VARCHAR(50),
    routing_reason          TEXT,
    encrypted               BOOLEAN DEFAULT FALSE,

    created_at              TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(thread_id, turn_number)
) PARTITION BY RANGE (created_at);

-- [V2: GAP-C3 fix — DEFAULT partition as safety net]
CREATE TABLE turn_snapshots_default PARTITION OF turn_snapshots DEFAULT;

-- [V2: GAP-C3 fix — pg_partman configuration]
-- Run after pg_partman extension is installed:
-- SELECT partman.create_parent(
--     p_parent_table := 'public.turn_snapshots',
--     p_control := 'created_at',
--     p_type := 'range',
--     p_interval := '1 month',
--     p_premake := 3
-- );

-- ----- cost_ledger (partitioned) -----
CREATE TABLE IF NOT EXISTS cost_ledger (
    id              SERIAL PRIMARY KEY,
    thread_id       VARCHAR(255) REFERENCES chat_threads(id) ON DELETE SET NULL,
    user_id         VARCHAR(255) NOT NULL,  -- [V2: VARCHAR — GAP-C2]
    deal_id         VARCHAR(20),
    turn_number     INTEGER,
    request_id      VARCHAR(64),
    model           VARCHAR(100) NOT NULL,
    provider        VARCHAR(50) NOT NULL,
    input_tokens    INTEGER NOT NULL DEFAULT 0,
    output_tokens   INTEGER NOT NULL DEFAULT 0,
    cost_usd        NUMERIC(10,6) NOT NULL DEFAULT 0,
    routing_decision VARCHAR(50),
    routing_reason  VARCHAR(200),
    cache_hit       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- [V2: GAP-C3 fix — DEFAULT partition]
CREATE TABLE cost_ledger_default PARTITION OF cost_ledger DEFAULT;

CREATE INDEX idx_cost_deal ON cost_ledger(deal_id) WHERE deal_id IS NOT NULL;
CREATE INDEX idx_cost_user ON cost_ledger(user_id);
CREATE INDEX idx_cost_date ON cost_ledger(created_at);

-- [V2: GAP-M12 fix — use regular VIEW instead of materialized view to avoid refresh issues]
CREATE OR REPLACE VIEW deal_cost_summary AS
SELECT
    deal_id,
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS total_turns,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens,
    SUM(cost_usd) AS total_cost_usd,
    MAX(created_at) AS last_activity,
    COUNT(DISTINCT user_id) AS unique_users,
    MODE() WITHIN GROUP (ORDER BY model) AS primary_model
FROM cost_ledger
WHERE deal_id IS NOT NULL
GROUP BY deal_id, DATE_TRUNC('month', created_at);

-- ----- deal_budgets [V2: GAP-C1 fix — standalone PK, no FK to chat_threads] -----
CREATE TABLE IF NOT EXISTS deal_budgets (
    deal_id             VARCHAR(20) PRIMARY KEY,  -- [V2: NO FK — GAP-C1 fix]
    -- V1 had: REFERENCES chat_threads(deal_id) — INVALID because deal_id is not unique on chat_threads
    -- V2: Application-level validation. deal_id references deals in zakops DB (cross-DB, no FK possible)
    monthly_limit_usd   NUMERIC(10,2) DEFAULT 10.00,
    alert_threshold     NUMERIC(3,2) DEFAULT 0.80,
    hard_cap            BOOLEAN DEFAULT FALSE,
    -- [V2: Predictive budgeting fields — QW-8]
    avg_daily_cost      NUMERIC(10,4),             -- Rolling 7-day average
    projected_monthly   NUMERIC(10,2),             -- Extrapolated month-end cost
    budget_exhaustion_date DATE,                    -- Predicted date budget runs out
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ----- cross_db_outbox [V2: GAP-M4 fix — outbox pattern for cross-DB writes] -----
CREATE TABLE IF NOT EXISTS cross_db_outbox (
    id              SERIAL PRIMARY KEY,
    event_type      VARCHAR(50) NOT NULL,  -- 'brain_extract', 'deal_reconcile', 'brain_update'
    payload         JSONB NOT NULL,
    target_db       VARCHAR(50) NOT NULL DEFAULT 'zakops',
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, processing, done, failed
    retry_count     INTEGER DEFAULT 0,
    max_retries     INTEGER DEFAULT 3,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    processed_at    TIMESTAMPTZ,
    error_message   TEXT
);

CREATE INDEX idx_outbox_pending ON cross_db_outbox(status, created_at) WHERE status = 'pending';

-- ----- Update message_count trigger -----
CREATE OR REPLACE FUNCTION update_thread_message_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_threads
    SET message_count = message_count + 1,
        last_active = NOW()
    WHERE id = NEW.thread_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_message_count
    AFTER INSERT ON chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_thread_message_count();

-- [V2: GAP-C3 fix — partition automation function]
CREATE OR REPLACE FUNCTION create_monthly_partitions(
    p_table TEXT,
    p_months_ahead INTEGER DEFAULT 3
) RETURNS VOID AS $$
DECLARE
    v_start DATE;
    v_end DATE;
    v_partition TEXT;
    v_i INTEGER;
BEGIN
    FOR v_i IN 0..p_months_ahead LOOP
        v_start := DATE_TRUNC('month', CURRENT_DATE + (v_i || ' months')::INTERVAL);
        v_end := v_start + '1 month'::INTERVAL;
        v_partition := p_table || '_' || TO_CHAR(v_start, 'YYYY_MM');

        -- Skip if partition already exists
        IF NOT EXISTS (
            SELECT 1 FROM pg_class WHERE relname = v_partition
        ) THEN
            EXECUTE format(
                'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                v_partition, p_table, v_start, v_end
            );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create initial partitions
SELECT create_monthly_partitions('turn_snapshots', 3);
SELECT create_monthly_partitions('cost_ledger', 3);

-- [V2: GAP-H5 fix — migrate SQLite user/session tables to PostgreSQL]
-- user and session tables already exist in zakops_agent (from schema.sql)
-- This migration ensures they're in PostgreSQL if they were SQLite-only
-- The actual data migration happens via migrate_chat_data.py (Section 3.7)

COMMIT;
```

#### Rollback: `004_chat_canonical_store_rollback.sql` [V2: GAP-M11 fix]

```sql
BEGIN;
DROP TABLE IF EXISTS cross_db_outbox CASCADE;
DROP TABLE IF EXISTS deal_budgets CASCADE;
DROP VIEW IF EXISTS deal_cost_summary;
DROP TABLE IF EXISTS cost_ledger CASCADE;
DROP TABLE IF EXISTS turn_snapshots CASCADE;
DROP TABLE IF EXISTS session_summaries CASCADE;
DROP TABLE IF EXISTS thread_ownership CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_threads CASCADE;
DROP TABLE IF EXISTS user_identity_map CASCADE;
DROP FUNCTION IF EXISTS update_thread_message_count() CASCADE;
DROP FUNCTION IF EXISTS create_monthly_partitions(TEXT, INTEGER) CASCADE;
DELETE FROM schema_migrations WHERE version = '004';
COMMIT;
```

### 3.4 Canonical Source of Truth Declaration [V2.1]

Every data type has exactly ONE canonical store. All other locations are caches or workflow artifacts.

| Data Type | Canonical Store | Database | Table | Cache Locations | Workflow-Only Locations |
|-----------|----------------|----------|-------|-----------------|----------------------|
| **Chat threads** | PostgreSQL | `zakops_agent` | `chat_threads` | localStorage (browser), PGlite (future) | — |
| **Chat messages** | PostgreSQL | `zakops_agent` | `chat_messages` | localStorage (browser) | — |
| **Thread ownership** | PostgreSQL | `zakops_agent` | `thread_ownership` | — | — |
| **Session summaries** | PostgreSQL | `zakops_agent` | `session_summaries` | — | — |
| **Turn snapshots** | PostgreSQL | `zakops_agent` | `turn_snapshots` | — | — |
| **Cost records** | PostgreSQL | `zakops_agent` | `cost_ledger` | — | In-memory trackers (legacy, to be removed) |
| **Deal budgets** | PostgreSQL | `zakops_agent` | `deal_budgets` | — | `/tmp/chat_budget_state.json` (legacy) |
| **User identity** | PostgreSQL | `zakops_agent` | `user_identity_map` | — | SQLite `user` table (deprecated) |
| **Cross-DB queue** | PostgreSQL | `zakops_agent` | `cross_db_outbox` | — | — |
| **Deal Brain** | PostgreSQL | `zakops` | `deal_brain` | — | `agent_context_summaries` (deprecated proto-brain) |
| **Brain history** | PostgreSQL | `zakops` | `deal_brain_history` | — | — |
| **Entity graph** | PostgreSQL | `zakops` | `deal_entity_graph` | — | — |
| **Decision outcomes** | PostgreSQL | `zakops` | `decision_outcomes` | — | — |
| **Deal access** | PostgreSQL | `zakops` | `deal_access` | — | — |
| **LangGraph checkpoints** | PostgreSQL | `zakops_agent` | `checkpoints` + 2 | — | Workflow recovery only — NOT message source of truth |
| **Decision ledger** | PostgreSQL | `zakops_agent` | `decision_ledger` | — | Audit trail — anonymized on delete, never source for display |

**Invariant**: If a query can be answered from the canonical store, it MUST be answered from the canonical store. Cache reads are only permitted when the canonical store is unreachable (offline/degraded mode, Section 14).

**Split-brain prevention**: Dual-write phase (S3.5) writes to canonical store FIRST, then cache. On read conflict, canonical store always wins.

### 3.5 Deprecation Schedule

| Layer | Phase 1 (Dual-Write) | Phase 2 (Read Migration) | Phase 3 (Deprecation) |
|-------|----------------------|--------------------------|----------------------|
| **localStorage** | Write to both localStorage + PostgreSQL | Read from PostgreSQL API, cache in localStorage | localStorage = offline cache only (PGlite for advanced offline) |
| **SQLite sessions** | Dual-write: SQLite + PostgreSQL | Read from PostgreSQL, stop reading SQLite | Remove `ChatSessionStore`, `CHAT_PERSISTENCE_ENABLED`, SQLite file |
| **SQLite user/session** | Dual-write: SQLite + PostgreSQL user_identity_map | Read from PostgreSQL | Remove SQLite user tables entirely [V2: GAP-H5] |
| **LangGraph checkpoints** | No change (keep for graph recovery) | No change | Permanent — NOT message source of truth |

### 3.5 New API Endpoints

These replace the current placeholder stubs.

**[V2: GAP-H1 fix]** — Dashboard middleware must route `/api/v1/chatbot/*` to Agent API. Add to `middleware.ts` `handledByRoutes`:

```typescript
// middleware.ts — add to handledByRoutes array
const CHATBOT_ROUTES = ['/api/v1/chatbot'];
// In the route matching logic:
if (CHATBOT_ROUTES.some(r => path.startsWith(r))) {
    return proxyToAgentApi(request, headers);  // Port 8095
}
```

#### `GET /api/v1/chatbot/threads`
```
Auth: JWT required (user_id from token) — [V2: GAP-H2 fix, no more service token for user requests]
Query: ?deleted=false&limit=50&offset=0
Response: {
    threads: ChatThreadSummary[],
    total: int
}
ChatThreadSummary: {
    id, user_id, deal_id, scope_type, title, preview,
    pinned, archived, message_count, last_active, created_at,
    momentum_score: float | null  -- [V2: QW-2 Deal Momentum Score]
}
Sort: pinned DESC, last_active DESC
Filter: deleted=false by default; deleted=true for recycle bin
```

#### `GET /api/v1/chatbot/threads/{id}/messages`
```
Auth: JWT + thread_ownership check
Query: ?limit=50&before_turn=N (cursor pagination by turn_number)
Response: {
    messages: ChatMessage[],
    thread: ChatThreadSummary,
    has_more: bool,
    ghost_knowledge_flags: GhostFlag[]  -- [V2: QW-1 Ghost Knowledge Detection]
}
ChatMessage: {
    id, role, content, citations, proposals, evidence_summary,
    timing, provider, cache_hit, turn_number, created_at
}
```

#### `POST /api/v1/chatbot/threads`
```
Auth: JWT required
Body: { scope_type, deal_id?, title? }
Response: { thread: ChatThreadSummary }
Side effects: Creates thread_ownership row, creates deal_access if deal-scoped
```

#### `PATCH /api/v1/chatbot/threads/{id}`
```
Auth: JWT + ownership
Body: { title?, pinned?, archived? }
Response: { thread: ChatThreadSummary }
```

#### `DELETE /api/v1/chatbot/threads/{id}`
```
Auth: JWT + ownership
Query: ?permanent=false (soft delete by default)
Response: { deleted: true, permanent: bool }
Behavior:
  - permanent=false: sets deleted=TRUE, deleted_at=NOW()
  - permanent=true: cascading hard delete (see Section 11)
  - Blocked if legal_hold=TRUE (returns 409 Conflict)
```

### 3.6 ChatRepository Class

**Location**: `apps/agent-api/app/services/chat_repository.py` (new file)

Replaces `ChatSessionStore`. Single class for all chat CRUD operations:

```python
class ChatRepository:
    """Canonical chat data access layer.

    Writes to PostgreSQL (zakops_agent).
    All reads go through here — no direct table queries elsewhere.
    """

    async def create_thread(self, user_id: str, scope_type: str, deal_id: str | None = None) -> ChatThread
    async def get_thread(self, thread_id: str, user_id: str) -> ChatThread
    async def list_threads(self, user_id: str, deleted: bool = False, limit: int = 50) -> list[ChatThread]
    async def update_thread(self, thread_id: str, user_id: str, **kwargs) -> ChatThread
    async def soft_delete_thread(self, thread_id: str, user_id: str) -> None
    async def hard_delete_thread(self, thread_id: str, user_id: str) -> None
    async def restore_thread(self, thread_id: str, user_id: str) -> ChatThread

    async def add_message(self, thread_id: str, user_id: str, role: str, content: str, **metadata) -> ChatMessage
    async def get_messages(self, thread_id: str, user_id: str, limit: int = 50, before_turn: int | None = None) -> list[ChatMessage]

    async def get_thread_for_llm(self, thread_id: str, max_messages: int = 6) -> list[dict]

    # [V2: Cross-DB deal reference validation — GAP-H4]
    async def validate_deal_reference(self, deal_id: str) -> bool:
        """Application-level check that deal_id exists in zakops.deals.
        Uses backend API call since cross-DB FK is impossible."""
        ...

    # [V2: Outbox for cross-DB writes — GAP-M4]
    async def enqueue_brain_extraction(self, deal_id: str, thread_id: str, turn: int, user_msg: str, asst_msg: str) -> None:
        """Writes to cross_db_outbox instead of direct cross-DB write."""
        ...
```

### 3.7 Migration Script

**Location**: `apps/agent-api/scripts/migrate_chat_data.py` (new file)

```
Phase 1 backfill process:
1. Read all SQLite sessions from chat_persistence.py store
2. For each session:
   a. Create chat_threads row (generate thread_id if missing)
   b. Create chat_messages rows (assign turn_numbers sequentially)
   c. Create thread_ownership row (user_id from identity map, or 'legacy_user' for unmapped)
3. Read all localStorage sessions (via admin endpoint that receives client data)
4. Merge: if thread exists in both, prefer SQLite (richer data)
5. [V2: GAP-H5] Migrate SQLite user/session tables to PostgreSQL:
   a. Read all rows from SQLite `user` and `session` tables
   b. Insert into user_identity_map (canonical_id = str(sqlite_id))
   c. Map external_ids: {"agent_sqlite_id": sqlite_id}
6. [V2: GAP-M5] Handle historical data:
   a. Backfill only threads and messages (NOT turn_snapshots — historical data lacks required fields)
   b. For pre-2026-02 data: insert into DEFAULT partition (no explicit date partition needed)
   c. Mark backfilled messages with timing.backfilled = true
7. Log: {total_threads, total_messages, total_users_migrated, conflicts_resolved}
```

### 3.8 Write Path (End-to-End After Unification)

```
User types message in chat UI
  → Dashboard: POST /api/chat (Next.js route handler)
    → route.ts determines provider (local/agent)
    → [V2: QW-7] Smart Paste: if pasted text detected, offer entity extraction before send

    [Backend path — evidence-grounded chat]
    → POST to backend orchestrator
      → ChatRepository.add_message(role="user", content=query)     ← WRITE #1
      → InjectionGuard.scan(query)                                 ← INPUT DEFENSE
      → [V2: I-1] CanaryTokenScanner.verify_no_leakage(query)     ← CANARY CHECK
      → EvidenceBuilder.build(deal_id, query)
        → [V2: A-4] Prepend contextual chunk headers to each RAG chunk
        → [V2: I-1] Inject canary tokens into sensitive chunks
        → [V2: A-1] Hybrid retrieval: BM25 + pgvector, fuse via RRF
      → [V2: E-1] GhostKnowledgeDetector.scan(query, deal_brain)  ← GHOST DETECT
      → LLMRouter.decide_route(query, complexity, scope)
      → LLM call (stream via SSE)
      → [V2: B-1] ReflexionCritique.evaluate(response, evidence)  ← SELF-CRITIQUE
      → ChatRepository.add_message(role="assistant", content=response,
          citations=extracted, proposals=parsed,
          evidence_summary=bundle.summary, timing=trace)           ← WRITE #2
      → CostLedger.record(thread_id, model, tokens, cost)         ← WRITE #3
      → Summarizer.maybe_summarize(thread_id, turn_number)         ← WRITE #4 (conditional)
      → [V2: GAP-M4] Outbox.enqueue_brain_extraction(...)         ← WRITE #5 (async, cross-DB)
        → OutboxWorker picks up → DealBrain.extract_facts(deal_id, query, response)

    [Agent path — tool-calling workflow]
    → POST to agent API /v1/agent/invoke/stream
      → ScopeFilter.filter_tools(scope_type, role)                 ← TOOL SCOPING
      → InjectionGuard.scan(message)                               ← INPUT DEFENSE
      → [V2: D-2] Schema-validate all tool args via strict Pydantic
      → LangGraph invoke (chat → tool_call → approval_gate → execute)
      → [V2: B-3] GeneralizedToolVerification.assert(tool, result) ← POST-TOOL CHECK
      → SnapshotWriter.capture(thread_id, turn, prompt, messages)  ← SNAPSHOT
      → CostLedger.record(...)                                     ← COST

    → Dashboard: localStorage.setItem(cache)                       ← CACHE ONLY
```

### 3.9 Read Path (End-to-End After Unification)

```
User opens /chat page
  → Dashboard: GET /api/chat/threads (Next.js route)
    → Proxy to Agent API: GET /v1/chatbot/threads
    → ChatRepository.list_threads(user_id, deleted=false)
    → [V2: F-1] Enrich each thread with deal_momentum_score if deal-scoped
    → Returns: sorted thread list (pinned first, then last_active DESC)
    → Dashboard caches in localStorage for offline access

User selects a thread
  → Dashboard: GET /api/chat/threads/{id}/messages?limit=50
    → ChatRepository.get_messages(thread_id, user_id, limit=50)
    → [V2: E-3] SpacedRepetition.get_review_facts(deal_id) → "Remember this?" card
    → Returns: paginated messages with all metadata

User scrolls up (load more)
  → GET /api/chat/threads/{id}/messages?limit=50&before_turn=oldest_loaded
    → Cursor-based pagination, no offset drift
```

### 3.10 SSE Event Catalog [V2: GAP-L2 fix]

All Server-Sent Events emitted by the chat system:

| Event Type | Payload | Source | When |
|-----------|---------|--------|------|
| `message_chunk` | `{content: str}` | Backend/Agent | During streaming response |
| `message_complete` | `{message_id, citations, proposals}` | Backend/Agent | Response finished |
| `thread_updated` | `{thread_id, field, value}` | Agent API | Thread metadata change |
| `brain_updated` | `{deal_id, version, changes}` | Backend | After brain extraction |
| `summary_generated` | `{thread_id, version, covers_turns}` | Backend | After summarization |
| `injection_alert` | `{severity, patterns_found}` | Backend/Agent | Injection detected |
| `legal_hold_set` | `{thread_id, reason, set_by}` | Admin | Legal hold applied |
| `budget_warning` | `{spend, budget, percent}` | Backend | Budget threshold hit |
| `cost_update` | `{turn_tokens, session_total, cost}` | Backend/Agent | After each LLM call |
| `ghost_knowledge` | `{facts: [{key, value, confidence}]}` | Backend | Ghost knowledge detected |
| `momentum_update` | `{deal_id, score, delta}` | Backend | Momentum score change |
| `tool_execution` | `{tool, status, result_preview}` | Agent | Tool call completed |
| `approval_required` | `{proposal_id, type, description}` | Agent | HITL gate triggered |
| `error` | `{code, message}` | Any | Error condition |

---

## 4. Deal Brain v2

### 4.1 Current State (Evidence)

**Existing proto-brain**: `DealContextSummary` at `zakops-backend/src/core/agent/context_store.py:47-125`

| What exists | What's missing |
|-------------|----------------|
| `summary_text` field (never LLM-generated) | LLM summarization — `_extract_topics()` is keyword-only (14 hardcoded words, lines 431-445) |
| `facts` list with `ContextFact(key, value, source_event_id, confidence)` | No risks, decisions, assumptions, open items |
| `agent_context_summaries` table in `zakops` DB | No version history, no diff capability |
| `rebuild_from_events()` can reconstruct from event stream | No scheduled rebuild, no drift detection |
| `update_context_from_interaction()` auto-updates after agent runs | No user edit UI, no approval for corrections |

**Existing case file system**: JSON on disk at `/DataRoom/.deal-registry/case_files/{deal_id}.json`, read by `chat_evidence_builder.py:402-411`.

### 4.2 Schema

#### Migration: `028_deal_brain.sql` (Backend)

```sql
-- ============================================================
-- Migration 028: Deal Brain v2
-- Part of: COL-DESIGN-SPEC-V2, Section 4
-- Fixes: GAP-C2 (user_id types), GAP-M9 (email integration),
--         GAP-M10 (correct_brain_summary handler)
-- Enhancements: Ghost Knowledge, Forgetting Curve, Cross-Deal Graph
-- ============================================================

BEGIN;

INSERT INTO zakops.schema_migrations (version, description, applied_at)
VALUES ('028', 'Deal Brain v2 (COL V2)', NOW())
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS zakops.deal_brain (
    deal_id               VARCHAR(20) PRIMARY KEY REFERENCES zakops.deals(deal_id),
    version               INTEGER NOT NULL DEFAULT 1,

    -- LLM-generated natural language summary
    summary               TEXT,
    summary_model         VARCHAR(100),
    summary_confidence    FLOAT DEFAULT 1.0,

    -- Structured knowledge (JSONB arrays)
    facts                 JSONB DEFAULT '[]'::jsonb,
    -- Schema: [{key: str, value: any, confidence: float, source_event_id: str,
    --           source_type: "chat"|"event"|"action"|"manual"|"email"|"user_assertion",
    --           extracted_at: iso8601, verified_by: str|null, supersedes: str|null,
    --           last_reinforced: iso8601,       -- [V2: C-2 Forgetting Curve]
    --           reinforcement_count: int,       -- [V2: C-2]
    --           decay_confidence: float|null}]  -- [V2: C-2 computed confidence after decay]

    risks                 JSONB DEFAULT '[]'::jsonb,
    decisions             JSONB DEFAULT '[]'::jsonb,
    -- [V2: I-5 Decision Journal — extended schema]:
    -- Schema: [{id: str, description: str, rationale: str, decided_by: str,
    --           decided_at: iso8601, reversible: bool, deal_stage: str, source_thread_id: str,
    --           outcome_tracked: bool, outcome: str|null, outcome_recorded_at: iso8601|null,
    --           outcome_score: float|null}]  -- -1.0 to 1.0: negative=bad, positive=good

    assumptions           JSONB DEFAULT '[]'::jsonb,
    open_items            JSONB DEFAULT '[]'::jsonb,

    -- [V2: E-1 Ghost Knowledge tracking]
    ghost_facts           JSONB DEFAULT '[]'::jsonb,
    -- Schema: [{key: str, value: str, detected_in_thread: str, detected_at: iso8601,
    --           confirmed: bool, confirmed_by: str|null, promoted_to_fact: bool}]

    stage_notes           JSONB DEFAULT '{}'::jsonb,

    -- [V2: F-1 Deal Momentum Score]
    momentum_score        FLOAT,  -- 0-100 composite metric
    momentum_updated_at   TIMESTAMPTZ,
    momentum_components   JSONB,  -- {stage_velocity, event_freq, open_item_completion, risk_trajectory, action_rate}

    -- [V2: C-4 Cross-Deal Entity references]
    entities              JSONB DEFAULT '[]'::jsonb,
    -- Schema: [{entity_type: "person"|"company"|"term"|"risk_pattern", name: str,
    --           normalized_name: str, first_seen: iso8601, occurrences: int}]

    -- [V2: M9 Email integration tracking]
    email_facts_count     INTEGER DEFAULT 0,
    last_email_ingestion  TIMESTAMPTZ,

    -- Provenance
    last_summarized_turn  INTEGER,
    last_summarized_at    TIMESTAMPTZ,
    last_fact_extraction  TIMESTAMPTZ,
    contradiction_count   INTEGER DEFAULT 0,

    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);

-- Version history for audit trail and rollback
CREATE TABLE IF NOT EXISTS zakops.deal_brain_history (
    id              SERIAL PRIMARY KEY,
    deal_id         VARCHAR(20) NOT NULL REFERENCES zakops.deals(deal_id),
    version         INTEGER NOT NULL,
    snapshot        JSONB NOT NULL,
    diff            JSONB,
    trigger_type    VARCHAR(50) NOT NULL,
    triggered_by    VARCHAR(255),  -- [V2: VARCHAR — GAP-C2]
    trigger_context JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(deal_id, version)
);

CREATE INDEX idx_brain_history_deal ON zakops.deal_brain_history(deal_id, version DESC);

-- [V2: C-4 Cross-Deal Entity Resolution Graph]
CREATE TABLE IF NOT EXISTS zakops.deal_entity_graph (
    id              SERIAL PRIMARY KEY,
    entity_type     VARCHAR(50) NOT NULL,
    normalized_name VARCHAR(500) NOT NULL,
    deal_id         VARCHAR(20) NOT NULL REFERENCES zakops.deals(deal_id),
    occurrences     INTEGER DEFAULT 1,
    first_seen      TIMESTAMPTZ DEFAULT NOW(),
    last_seen       TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'::jsonb,
    UNIQUE(entity_type, normalized_name, deal_id)
);

CREATE INDEX idx_entity_graph_name ON zakops.deal_entity_graph(entity_type, normalized_name);
CREATE INDEX idx_entity_graph_deal ON zakops.deal_entity_graph(deal_id);

-- [V2: I-5 Decision Journal — outcome tracking]
CREATE TABLE IF NOT EXISTS zakops.decision_outcomes (
    id              SERIAL PRIMARY KEY,
    deal_id         VARCHAR(20) NOT NULL REFERENCES zakops.deals(deal_id),
    decision_id     VARCHAR(36) NOT NULL,  -- References deal_brain.decisions[].id
    predicted_value JSONB,                 -- What was believed at decision time
    actual_value    JSONB,                 -- What actually happened
    delta           JSONB,                 -- Computed difference
    recorded_by     VARCHAR(255),
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Deal access control
CREATE TABLE IF NOT EXISTS zakops.deal_access (
    deal_id         VARCHAR(20) NOT NULL REFERENCES zakops.deals(deal_id) ON DELETE CASCADE,
    user_id         VARCHAR(255) NOT NULL,  -- [V2: VARCHAR — GAP-C2]
    role            VARCHAR(20) NOT NULL DEFAULT 'viewer',
    granted_by      VARCHAR(255),           -- [V2: VARCHAR — GAP-C2]
    granted_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (deal_id, user_id),
    CONSTRAINT chk_deal_role CHECK (role IN ('viewer', 'operator', 'approver', 'admin'))
);

CREATE INDEX idx_deal_access_user ON zakops.deal_access(user_id);

-- Migrate from proto-brain
INSERT INTO zakops.deal_brain (deal_id, summary, facts, created_at, updated_at)
SELECT
    deal_id,
    summary_text,
    facts_json,
    created_at,
    updated_at
FROM zakops.agent_context_summaries
ON CONFLICT (deal_id) DO NOTHING;

COMMIT;
```

#### Rollback: `028_deal_brain_rollback.sql` [V2: GAP-M11 fix]

```sql
BEGIN;
DROP TABLE IF EXISTS zakops.decision_outcomes CASCADE;
DROP TABLE IF EXISTS zakops.deal_entity_graph CASCADE;
DROP TABLE IF EXISTS zakops.deal_access CASCADE;
DROP TABLE IF EXISTS zakops.deal_brain_history CASCADE;
DROP TABLE IF EXISTS zakops.deal_brain CASCADE;
DELETE FROM zakops.schema_migrations WHERE version = '028';
COMMIT;
```

### 4.3 Write Triggers

| Trigger | When | Approval | Implementation Point | What Changes |
|---------|------|----------|---------------------|-------------|
| **Per-turn extraction** | After every assistant response in deal-scoped chat | NO | Via outbox (GAP-M4), `DealBrainService.extract_from_turn()` | facts, risks, open_items, ghost_facts |
| **Stage change** | On `transition_deal_state()` call | NO | `025_deal_lifecycle_fsm.sql` trigger → calls brain update | summary regenerated, `stage_notes[old_stage]` finalized |
| **Periodic consolidation** | Every 10 turns OR 24h since last summary | NO | Checked in `chat_orchestrator.py` before LLM call | Full re-summarization; dedup; confidence recalculation |
| **User edit** | User modifies any field in Deal Brain UI | NO | `PATCH /api/deals/{id}/brain` | Direct write; `verified_by` = user_id |
| **Summary correction** | User flags summary as inaccurate | YES | Proposal type: `correct_brain_summary` [V2: GAP-M10 — handler defined in S15] | Regeneration requires approval |
| **Fact deletion** | User removes a fact | NO | `DELETE /api/deals/{id}/brain/facts/{key}` | Fact removed; logged to history |
| **[V2] Ghost knowledge confirmation** | User confirms ghost-detected fact | NO | `POST /api/deals/{id}/brain/ghost/{id}/confirm` | Promoted to fact with `source_type: "user_assertion"` |
| **[V2] Email ingestion** | New email processed for deal [GAP-M9] | NO | Backend email ingestion pipeline → `DealBrainService.extract_from_email()` | facts from email content, `email_facts_count++` |
| **[V2] Momentum recalculation** | After any brain change | NO | `DealBrainService.recalculate_momentum()` | momentum_score, momentum_components updated |
| **[V2] Entity extraction** | During per-turn extraction | NO | `EntityResolver.extract_and_link()` | `deal_entity_graph` rows created/updated |

### 4.4 Extraction Prompt

```
You are analyzing an M&A deal conversation to extract structured knowledge.

Given:
- Deal: {deal_id} ({canonical_name}) at stage: {current_stage}
- Current brain summary: {existing_summary}
- Current facts: {existing_facts_json}
- New conversation turn:
  User: {user_message}
  Assistant: {assistant_response}

Extract any NEW information as JSON:
{
  "new_facts": [{"key": "...", "value": "...", "confidence": 0.0-1.0}],
  "new_risks": [{"description": "...", "severity": "low|medium|high|critical", "likelihood": 0.0-1.0}],
  "new_decisions": [{"description": "...", "rationale": "..."}],
  "new_assumptions": [{"statement": "...", "confidence": 0.0-1.0}],
  "new_open_items": [{"description": "...", "priority": "low|medium|high"}],
  "contradictions": [{"existing_key": "...", "existing_value": "...", "new_value": "...", "resolution": "..."}],
  "ghost_knowledge": [{"key": "...", "value": "...", "reason": "User referenced this but it is NOT in the Deal Brain"}],
  "entities": [{"type": "person|company|term|risk_pattern", "name": "...", "normalized": "..."}],
  "should_update_summary": true|false
}

Rules:
- Only extract facts explicitly stated or strongly implied — never speculate
- Assign confidence < 0.7 if information is uncertain or from user assertion (not verified)
- Flag contradictions if new information conflicts with existing facts
- Set should_update_summary=true only if the new information is material
- [V2: QW-1] GHOST KNOWLEDGE: If the user references specific facts (names, numbers,
  dates, terms) that are NOT present in the existing facts list, flag them in ghost_knowledge.
  This detects institutional knowledge that exists only in the user's head.
- [V2: C-4] ENTITIES: Extract all named entities (people, companies, financial terms,
  risk patterns) and normalize names for cross-deal linking.
```

**Model**: Gemini Flash (cheap tier) — `model_registry.py:159` already maps "summarization" to cost-effective tier.

### 4.5 Drift Detection

Three mechanisms (V1) plus two new (V2):

1. **Staleness check**: `last_summarized_turn < thread.max_turn - 10` → amber indicator.

2. **Contradiction detection**: When extraction produces a fact with same `key` but different `value`:
   - Both facts get `confidence` reduced by 0.3
   - New `open_item` auto-created
   - `contradiction_count` incremented
   - UI shows red indicator

3. **Periodic re-summarization**: Every 10 turns, generate fresh summary. Compare via embedding cosine distance > 0.3 → log drift.

4. **[V2: B-5] Active Drift Resolution Agent**: When contradiction is detected, spawn background investigation:
   ```python
   async def resolve_contradiction(deal_id: str, old_fact: dict, new_fact: dict):
       """Search evidence to propose resolution for contradicting facts."""
       evidence = await evidence_builder.build(deal_id, f"What is the correct {old_fact['key']}?")
       resolution = await llm.generate(
           f"Two conflicting values for {old_fact['key']}: "
           f"'{old_fact['value']}' vs '{new_fact['value']}'. "
           f"Based on this evidence, which is correct?\n{evidence}"
       )
       return DriftResolution(old=old_fact, new=new_fact, recommendation=resolution)
   ```

5. **[V2: C-2 Forgetting Curve Confidence Decay — QW-6]**: Facts not reinforced in recent conversations see confidence drop:
   ```python
   def compute_decay_confidence(fact: dict, now: datetime) -> float:
       """Ebbinghaus-inspired decay: confidence drops unless reinforced."""
       days_since = (now - parse(fact['last_reinforced'])).days
       reinforcements = fact.get('reinforcement_count', 1)
       # Decay rate slows with more reinforcements (spaced repetition effect)
       decay_rate = 0.1 / max(reinforcements, 1)
       return fact['confidence'] * math.exp(-decay_rate * days_since)
   ```

### 4.6 Email Integration [V2: GAP-M9 fix]

Backend has a complete email ingestion pipeline (`/home/zaks/zakops-backend/src/core/email/`). This section bridges it to Deal Brain:

```
Email arrives → email_ingestion pipeline → classified to deal_id
  → DealBrainService.extract_from_email(deal_id, email_content, email_metadata)
    → Same extraction prompt as 4.4 but with source_type: "email"
    → Facts added with source: "email:{message_id}"
    → deal_brain.email_facts_count incremented
    → Outbox event: brain_updated (triggers SSE to connected clients)
```

### 4.7 UI Components

#### `DealBrain.tsx` — Main Panel

**Location**: `apps/dashboard/src/components/deal-workspace/DealBrain.tsx` (new file)

```
┌─────────────────────────────────────────────────────────┐
│  Deal Brain: Acme Corp Acquisition     🟢 Current  78/100│
│                                         [Momentum ████▓░]│
│  ┌───────────────────────────────────────────────────┐  │
│  │ Summary                                    [Edit] │  │
│  │ Acme Corp is a mid-market SaaS company with      │  │
│  │ $12M ARR, currently in screening stage...         │  │
│  │                                    [Regenerate ↻] │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  [Facts(12)] [Risks(3)] [Decisions(2)] [Assumptions(5)] │
│  [Open Items(4)] [Ghost(2)] [Entities(8)]               │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Key Facts                          [+ Add] [🔍]  │  │
│  │ ┌─────────────────────────────────────────────┐   │  │
│  │ │ ARR: $12M          ★★★★☆ (0.9)    [✎] [✕] │   │  │
│  │ │ Source: chat turn 5 • Verified by: Zak      │   │  │
│  │ │ [View Lineage →]                            │   │  │
│  │ └─────────────────────────────────────────────┘   │  │
│  │ ┌─────────────────────────────────────────────┐   │  │
│  │ │ EBITDA: $2.1M      ★★★☆☆ (0.7→0.5↓)  [✎] │   │  │
│  │ │ Source: RAG • Unverified • Decaying ⏳      │   │  │
│  │ │ Last reinforced: 14 days ago                │   │  │
│  │ └─────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─── Ghost Knowledge (2 unconfirmed) ───────────────┐  │
│  │ ⚠ "CEO is retiring in Q3" — detected in chat      │  │
│  │   [Confirm as Fact] [Dismiss]                      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ▸ Version History (14 versions)                        │
│  ▸ Entity Graph (8 entities across 3 deals)             │
│  ▸ Decision Journal (2 tracked outcomes)                │
└─────────────────────────────────────────────────────────┘
```

#### `FactLineageExplorer.tsx` [V2: J-2]

Visual UI linking every Deal Brain fact to the specific chat message or document citation that established it:

```
┌─ Fact Lineage: ARR = $12M ──────────────────────────┐
│                                                       │
│  Established: 2026-02-10 in thread "Acme Review"      │
│  Source: Chat Turn 5 (User assertion)                  │
│                                                       │
│  ┌─ Evidence Chain ──────────────────────────────┐    │
│  │ 📝 Turn 5: "Acme has $12M ARR"                │    │
│  │ 📄 CIM Page 12: "Annual recurring... $11.8M"  │    │
│  │ ⚠ Slight discrepancy: $12M vs $11.8M          │    │
│  └───────────────────────────────────────────────┘    │
│                                                       │
│  Reinforced: 3 times (last: 2 days ago)               │
│  Current confidence: 0.85 (decayed from 0.9)          │
└───────────────────────────────────────────────────────┘
```

#### Permissions (using RBAC from `agent_auth.py:29-41`)

| Role | View | Edit Facts | Delete | Regenerate | Purge History | Confirm Ghost |
|------|------|-----------|--------|-----------|---------------|---------------|
| VIEWER | ✓ | — | — | — | — | — |
| OPERATOR | ✓ | ✓ | — | — | — | ✓ |
| APPROVER | ✓ | ✓ | ✓ | — | — | ✓ |
| ADMIN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## 5. Summarization & Tiered Memory

### 5.1 Current State (Evidence)

| System | Truncation Method | Limit | Code Location |
|--------|-------------------|-------|---------------|
| Backend | `session.get_history_for_llm(max_messages=6)` — last N messages | 6 messages | `chat_orchestrator.py:223-229`, called at lines 1031, 1340 |
| Agent API | `trim_messages(strategy="last", max_tokens=MAX_TOKENS)` — LangChain token-aware | 2000 tokens | `utils/graph.py:119-168`, `config.py:161` |
| Evidence | Hard char truncation per source | 40k total (8k RAG, 12k events, 10k case, 5k registry, 5k actions) | `chat_evidence_builder.py:48-55` |

**No summarization infrastructure exists anywhere.** Zero prompts, zero pipelines, zero summary storage.

### 5.2 MemGPT-Style Tiered Memory [V2: C-1]

Replace the flat memory model with three explicit tiers:

| Tier | Contents | Access Pattern | Storage | Capacity |
|------|----------|---------------|---------|----------|
| **Working** | Last 6 messages (current context window) | Always in-context, every LLM call | In-memory (GraphState) | 6 messages / 2000 tokens |
| **Recall** | Deal Brain facts + rolling summaries | Searched before each LLM call, injected as context | PostgreSQL (`deal_brain`, `session_summaries`) | Unlimited (searched, not loaded whole) |
| **Archival** | Full message history + turn snapshots | Explicit retrieval on demand (user asks "what did we discuss about X?") | PostgreSQL (`chat_messages`, `turn_snapshots`) | Unlimited |

**Memory promotion/demotion flow**:
```
User sends message
  → Working Memory: last 6 messages always present
  → Recall Memory search: query Deal Brain for relevant facts
    → Inject top-K facts as system context
    → Inject rolling summary of earlier conversation
  → If user asks about distant past:
    → Archival Memory search: full-text search on chat_messages
    → Return relevant historical messages as additional context
```

### 5.3 Summarization Design

**Owner**: Backend chat orchestrator (has EvidenceBuilder, 3-tier LLM router, cost-aware selection).

**Algorithm**: Hybrid (extractive pre-filter + LLM summarization)

```
Step 1: EXTRACTIVE PRE-FILTER (deterministic, <10ms)
  - From the last N unsummarized messages:
    - Select messages containing: proposals, citations, deal entity mentions,
      question/answer pairs, action items
    - Weight: most recent message = 1.0, decay by 0.9^position
    - Hard cap: 20 messages or 8000 tokens (whichever smaller)

Step 2: LLM SUMMARIZATION (Gemini Flash, ~0.1¢)
  Prompt:
  """
  Summarize this M&A deal conversation segment for continuity.

  Context:
  - Deal: {deal_id} ({canonical_name}), Stage: {stage}
  - Previous summary (covers turns 1-{last_turn}): {previous_summary}
  - New messages (turns {last_turn+1}-{current_turn}):
    {selected_messages}

  Output JSON:
  {
    "updated_summary": "...",
    "key_facts_mentioned": ["..."],
    "decisions_made": ["..."],
    "open_questions": ["..."],
    "action_items": ["..."],
    "memory_tier": "recall"
  }

  Rules:
  - Integrate new information with the previous summary
  - Preserve all facts from previous summary unless explicitly contradicted
  - Be concise (max 500 words for summary)
  """

Step 3: MERGE + PERSIST
  - Create new session_summaries row (version N+1, memory_tier='recall')
  - Update chat_threads.last_summary_version
  - Feed into DealBrain extraction if deal-scoped
```

**Trigger conditions** (checked after every assistant message write):
```python
should_summarize = (
    turn_number % 5 == 0 and
    turn_number - (last_summary.max_turn or 0) >= 5
) or event == "session_archive"
```

### 5.4 Background Memory Consolidation [V2: C-3]

During user idle time (>10 minutes since last message), a background worker:

1. **Re-summarizes active deal brains** — merge all facts, resolve low-confidence duplicates
2. **Detects cross-deal patterns** — via `deal_entity_graph`, find shared entities
3. **Pre-computes embeddings** for recently added Deal Brain facts (ready for Recall search)
4. **Applies forgetting curve** — recalculate `decay_confidence` for all facts not reinforced recently

```python
class MemoryConsolidationWorker:
    IDLE_THRESHOLD = timedelta(minutes=10)

    async def run(self):
        while True:
            idle_deals = await self.find_idle_deals(self.IDLE_THRESHOLD)
            for deal_id in idle_deals:
                await self.consolidate_brain(deal_id)
                await self.detect_cross_deal_patterns(deal_id)
                await self.precompute_embeddings(deal_id)
                await self.apply_forgetting_curve(deal_id)
            await asyncio.sleep(60)  # Check every minute
```

### 5.5 Memory State UI: `MemoryStatePanel`

**Location**: New tab in existing Debug panel (`chat/page.tsx:1637+`)

```
┌─────────────────────────────────────────────────────┐
│  Memory State                                        │
│                                                      │
│  ┌─ Working Memory ─────────────────────────────┐   │
│  │ Context Window: ████████░░ 1,847 / 2,000 tok │   │
│  │ Model sees 6 of 23 messages                   │   │
│  │  ░ Turn 1-17: (summarized → v3)               │   │
│  │  █ Turn 18-23: [in context]                   │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Recall Memory ──────────────────────────────┐   │
│  │ Deal Brain: 12 facts (3 decaying ⏳)          │   │
│  │ Rolling Summary: v3 (covers turns 1-17)       │   │
│  │ Injected context: 847 tokens                  │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│  ┌─ Archival Memory ────────────────────────────┐   │
│  │ Full history: 23 messages (4.2 KB)            │   │
│  │ Turn snapshots: 23 (1.8 MB)                   │   │
│  │ Searchable: Yes                               │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│  Evidence This Turn:                                 │
│  ✓ RAG: 4 chunks  ✓ Events: 7  ✓ Case File  ✗ Reg. │
└─────────────────────────────────────────────────────┘
```

---

## 6. Deterministic Replay & Counterfactual Analysis

### 6.1 Current State (Evidence)

| Component | Captured? | Where | Gap |
|-----------|-----------|-------|-----|
| Full message chain | ✓ | LangGraph checkpoints (`zakops_agent`) | Pre-trim messages not stored separately |
| System prompt version | ✓ (Agent only) | `prompt_version` in decision ledger, Langfuse | Backend prompt **unversioned** |
| System prompt hash | ✓ (Agent only) | `prompts/__init__.py:37-48` computes SHA-256 | Backend: no hash |
| Rendered prompt with evidence | ✗ | — | Built fresh each request, ephemeral |
| Post-trim message list | ✗ | — | `prepare_messages()` output not stored |
| Model parameters | Partial | `provider` in SQLite messages | No temperature, max_tokens, tool defs |
| Raw LLM completion | ✗ | — | Only 500-char preview in decision ledger |
| Token counts | ✗ | `token_count` in ledger (nullable) | No extraction from LLM response |

### 6.2 Partition Automation [V2: GAP-C3 fix] [V2.1: Hard Gate]

Turn snapshots and cost ledger use range partitioning. V1 had only 2-3 static partitions — a production time bomb. V2 fixes this with a three-tier approach:

#### Tier 1: DEFAULT Partition (Structural Safety Net — always present)
Catches any rows that don't fit existing partitions. Data lands here instead of failing. **Created in migration 004 — no external dependency.**

#### Tier 2: `create_monthly_partitions()` PL/pgSQL Function (Primary Mechanism)
Pure PostgreSQL function defined in migration 004 (S3.3). Creates partitions N months ahead. **No external extensions required.** Idempotent — `IF NOT EXISTS` check prevents duplicate creation.

#### Tier 3: Automated Scheduling (pg_cron OR fallback)

**Environment Prerequisites:**
| Requirement | Check Command | Fallback if Absent |
|-------------|---------------|-------------------|
| pg_cron extension | `SELECT * FROM pg_available_extensions WHERE name = 'pg_cron'` | Use OS-level cron (see below) |
| CREATE privilege | Migration runs as DB owner | Required — no fallback |
| PostgreSQL 12+ | `SELECT version()` | Required — partition syntax depends on it |

**Option A — pg_cron (preferred, if available):**
```sql
-- Setup (run once after pg_cron is installed, NOT in migration)
SELECT cron.schedule('partition-maintenance', '0 1 1 * *',
    $$SELECT create_monthly_partitions('turn_snapshots', 3);
      SELECT create_monthly_partitions('cost_ledger', 3);$$
);
```

**Option B — OS-level cron (fallback if pg_cron unavailable):**
```bash
# /etc/cron.d/zakops-partitions (or user crontab)
0 1 1 * * postgres psql -d zakops_agent -c "SELECT create_monthly_partitions('turn_snapshots', 3); SELECT create_monthly_partitions('cost_ledger', 3);"
```

**Option C — Application-level (last resort):**
```python
# In Agent API startup sequence (app/main.py or lifespan handler)
async def ensure_partitions():
    """Called on application startup. Idempotent."""
    await db.execute("SELECT create_monthly_partitions('turn_snapshots', 3)")
    await db.execute("SELECT create_monthly_partitions('cost_ledger', 3)")
```

#### Acceptance Gates for Partition Health

| Gate | Check | Frequency | Alert If Failed |
|------|-------|-----------|-----------------|
| G-PART-1 | DEFAULT partition has 0 rows (all data in named partitions) | Daily | WARNING: rows in DEFAULT means partition creation is behind |
| G-PART-2 | Partitions exist for current month + next 2 months | Weekly | CRITICAL: missing future partitions = imminent DEFAULT spillover |
| G-PART-3 | `create_monthly_partitions()` function exists | On deploy | CRITICAL: migration 004 incomplete |
| G-PART-4 | Scheduling mechanism is active (pg_cron OR OS cron OR app startup) | Weekly | WARNING: no automation = manual partition management |

```sql
-- G-PART-1: Check DEFAULT partition row count
SELECT relname, n_live_tup FROM pg_stat_user_tables
WHERE relname IN ('turn_snapshots_default', 'cost_ledger_default');
-- Expected: n_live_tup = 0 for both

-- G-PART-2: Check future partitions exist
SELECT relname FROM pg_class WHERE relname LIKE 'turn_snapshots_20%' ORDER BY relname DESC LIMIT 3;
-- Expected: current month + 2 future months
```

### 6.3 Retention Tiers

| Tier | Retention | Encryption | Condition |
|------|-----------|-----------|-----------|
| Default | 90 days | PII-redacted only | All turns |
| Compliance | 7 years | AES-256-GCM (reuse `encryption.py` `CheckpointEncryption`) | Thread has `compliance_tier=TRUE` |
| Legal hold | Indefinite | AES-256-GCM | Thread or deal has `legal_hold=TRUE` |

**[V2: GAP-M8 fix — Compliance Encryption Specification]**:
- Encrypt the entire `turn_snapshots` row as a single JSONB blob (not column-by-column)
- Encryption key: derived from deal_id + master key via HKDF
- Key rotation: quarterly; old snapshots re-encrypted in background batch job
- Queryability: `thread_id`, `turn_number`, `created_at` remain in cleartext for indexing; all content fields encrypted
- Implementation: extend existing `CheckpointEncryption` class from `apps/agent-api/app/core/security/encryption.py`

### 6.4 Replay Endpoint

#### `POST /admin/replay` (Admin-only)

```
Auth: require_admin_role
Body: { thread_id: str, turn_number: int }
Response: {
    original: { completion, tokens, proposals, citations },
    replay: { completion, tokens, proposals, citations },
    comparison: {
        similarity_score: float,
        tool_calls_match: bool,
        token_diff: int,
        semantic_drift: str  // "none", "minor", "significant"
    }
}
```

**Acceptance test**: Compliance-tier replay achieves cosine similarity > 0.85 and `tool_calls_match == true`.

### 6.5 Counterfactual Analysis Engine [V2: E-4]

Using the deterministic replay infrastructure, answer "what if" questions about past decisions.

#### `POST /admin/counterfactual` (Admin-only)

```
Auth: require_admin_role
Body: {
    thread_id: str,
    turn_number: int,
    modified_inputs: {
        user_message?: str,      // "What if I asked this instead?"
        facts_override?: dict,   // "What if EBITDA was $3M not $2.1M?"
        stage_override?: str     // "What if the deal was in LOI stage?"
    }
}
Response: {
    original: { completion, brain_state, recommendations },
    counterfactual: { completion, brain_state, recommendations },
    divergence: {
        brain_diff: dict,        // Fields that would differ
        recommendation_diff: str, // How advice would change
        risk_assessment_change: str
    }
}
```

**Implementation**: Replay the turn snapshot with modified inputs, generate response, extract Deal Brain changes, compare with actual outcome.

---

## 7. Prompt Injection & Input-Side Defenses

### 7.1 Current State (Evidence)

| Layer | Status | Evidence |
|-------|--------|----------|
| Input validation (production) | **NONE** | `graph.py` passes user messages directly to LLM |
| Input validation (test only) | Exists | `test_owasp_llm_top10.py:29-53` — `MockAgent.blocked_patterns` (12 patterns) |
| Output sanitization | **Strong** | `output_validation.py:95-136` — HTML escaping, SQL/XSS/traversal detection, PII |
| Secret scanning | Cloud-only | `chat_evidence_builder.py:512-533` — forces local vLLM if secrets detected |

### 7.2 Unified Security Pipeline [V2: GAP-M6 fix]

V1 had injection guard and output validation as parallel systems. V2 defines the full input-to-output security chain:

```
INPUT → InjectionGuard.scan() → CanaryTokenScanner.inject() → LLM → ReflexionCritique →
  → CanaryTokenScanner.verify_no_leakage() → OutputValidation.sanitize() →
  → PII Redaction → CitationAudit → OUTPUT
```

### 7.3 Four-Layer Defense (V1 Three-Layer + V2 Canary Tokens)

#### Layer 1: Rule-Based Pattern Detection (synchronous, <1ms)

**Location**: `apps/agent-api/app/core/security/injection_guard.py` (new file)

```python
import re
from dataclasses import dataclass

@dataclass
class ScanResult:
    passed: bool
    patterns_found: list[str]
    severity: str  # "none", "low", "medium", "high"
    sanitized_content: str | None

INJECTION_PATTERNS: list[tuple[str, str, str]] = [
    # (pattern, name, severity)
    (r"ignore\s+(all\s+)?previous\s+instructions", "instruction_override", "high"),
    (r"disregard\s+(all\s+)?(prior|above|previous)", "instruction_override", "high"),
    (r"you\s+are\s+now\s+a", "role_hijack", "high"),
    (r"system\s*:\s*override", "system_override", "high"),
    (r"override\s+all\s+safety", "safety_override", "high"),
    (r"reveal\s+(your\s+)?(system\s+)?prompt", "prompt_extraction", "high"),
    (r"what\s+are\s+your\s+(rules|instructions)", "prompt_extraction", "high"),
    (r"ASSISTANT\s*:", "role_injection", "medium"),
    (r"\[INST\]|\[/INST\]", "format_injection", "medium"),
    (r"```system", "fenced_injection", "medium"),
    (r"<\|im_start\|>|<\|im_end\|>", "chatml_injection", "medium"),
    (r"<\s*/?script", "xss_attempt", "low"),
    (r"javascript\s*:", "xss_attempt", "low"),
    (r"DROP\s+TABLE|DELETE\s+FROM|TRUNCATE", "sql_injection", "low"),
    (r"SELECT\s+\*\s+FROM", "sql_injection", "low"),
]

def scan_input(content: str) -> ScanResult:
    found = []
    max_severity = "none"
    for pattern, name, severity in INJECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            found.append(name)
            if SEVERITY_ORDER[severity] > SEVERITY_ORDER[max_severity]:
                max_severity = severity
    sanitized = content
    if found:
        for pattern, name, severity in INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)
    return ScanResult(passed=len(found) == 0, patterns_found=found,
                      severity=max_severity, sanitized_content=sanitized if found else None)

SEVERITY_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}
```

#### Layer 2: Structural Separation (Architectural)

XML-delimited data boundaries in system prompts (unchanged from V1).

#### Layer 3: Session-Level Escalation

```python
class SessionInjectionTracker:
    MAX_ATTEMPTS_BEFORE_LOCKDOWN = 3

    def record_attempt(self, session_id: str, scan_result: ScanResult):
        self.attempts[session_id].append(scan_result)
        if len(self.attempts[session_id]) >= self.MAX_ATTEMPTS_BEFORE_LOCKDOWN:
            return "lockdown"
        return "continue"
```

#### Layer 4: Canary Tokens [V2: I-1 — QW-3]

**Concept**: Inject invisible unique strings into sensitive RAG chunks. If they appear in LLM output, the response is accessing data it shouldn't have — block and alert.

```python
import hashlib, secrets

class CanaryTokenManager:
    """Manages canary tokens for data leak detection."""

    def inject_canary(self, chunk: str, source_id: str, sensitivity: str) -> tuple[str, str]:
        """Inject invisible canary token into sensitive RAG chunk.
        Returns (modified_chunk, canary_token)."""
        if sensitivity not in ("high", "critical"):
            return chunk, ""
        token = f"CANARY-{hashlib.sha256(secrets.token_bytes(16)).hexdigest()[:12]}"
        # Inject as invisible Unicode (zero-width characters encode the token)
        invisible = self._encode_invisible(token)
        return f"{invisible}{chunk}", token

    def verify_no_leakage(self, output: str, active_canaries: list[str]) -> list[str]:
        """Check if any canary tokens leaked into LLM output."""
        leaked = []
        for canary in active_canaries:
            invisible = self._encode_invisible(canary)
            if invisible in output or canary in output:
                leaked.append(canary)
        return leaked  # Non-empty = BLOCK response
```

#### Layer 5: Semantic Firewall [V2: I-2]

Augment regex with a small classifier that detects jailbreak intent semantically:

```python
class SemanticFirewall:
    """BERT-based jailbreak intent classifier. Catches what regex cannot."""

    def __init__(self, model_path: str = "models/jailbreak-classifier"):
        self.classifier = pipeline("text-classification", model=model_path)

    async def classify(self, text: str) -> dict:
        result = self.classifier(text[:512])  # Truncate for speed
        return {
            "is_jailbreak": result[0]["label"] == "JAILBREAK",
            "confidence": result[0]["score"],
            "method": "semantic_firewall"
        }
```

**Deployment note**: Semantic Firewall is Bucket 3 (Production/Enterprise). Use rule-based patterns for prototype.

### 7.4 Response Matrix

| Detection | User Input | RAG Chunk | Evidence Builder |
|-----------|-----------|-----------|-----------------|
| Low severity | Log + sanitize + continue | Log + exclude chunk | Skip source |
| Medium severity | Log + sanitize + toast | Log + exclude chunk | Skip source |
| High severity | Log + sanitize + toast + tracker | Log + exclude + flag admin | Skip + alert |
| Canary leaked | **BLOCK response** + alert admin + log | N/A | N/A |
| 3+ attempts | Downgrade to deterministic-only | N/A | N/A |

---

## 8. Citation Validation & Self-Critique

### 8.1 Current State

Citations extracted via regex only (`chat_orchestrator.py:1660-1679`). No semantic validation.

### 8.2 Post-Generation Citation Audit (V1)

For each `[cite-N]` in the response:
1. Extract the **claim sentence** containing the citation
2. Extract the **source snippet** from the corresponding `Citation` object
3. Compute **semantic similarity** (embedding cosine)
4. If similarity < 0.5, flag as "weak"

### 8.3 Reflexion Self-Critique Loop [V2: B-1]

After generating a response, a critique node evaluates quality before returning to user. Max 2 refinement loops.

```python
class ReflexionCritique:
    """Post-generation self-critique for response quality."""
    MAX_REFINEMENTS = 2

    async def evaluate(self, response: str, evidence: EvidenceBundle, turn_context: dict) -> CritiqueResult:
        critique_prompt = f"""
        Evaluate this M&A assistant response for quality:

        Response: {response}
        Evidence available: {evidence.summary}
        User question: {turn_context['user_message']}

        Check:
        1. Are all cited facts present in the evidence? (evidence grounding)
        2. Does the response address the user's actual question? (relevance)
        3. Are there unsupported claims? (hallucination risk)
        4. Are there important facts in evidence NOT mentioned? (completeness)

        Output JSON:
        {{
            "passed": true|false,
            "issues": [{{
                "type": "ungrounded_claim"|"missed_evidence"|"off_topic"|"hallucination",
                "description": "...",
                "severity": "low"|"medium"|"high"
            }}],
            "suggestion": "If failed, how to improve the response"
        }}
        """
        result = await self.llm.generate(critique_prompt, model="gemini-flash")
        return CritiqueResult.parse(result)

    async def refine_if_needed(self, response: str, critique: CritiqueResult,
                                evidence: EvidenceBundle, refinement_count: int) -> str:
        if critique.passed or refinement_count >= self.MAX_REFINEMENTS:
            return response
        # Re-generate with critique feedback
        refined = await self.llm.generate(
            f"Improve this response based on critique:\n"
            f"Original: {response}\n"
            f"Issues: {critique.issues}\n"
            f"Suggestion: {critique.suggestion}\n"
            f"Evidence: {evidence.summary}"
        )
        return refined
```

### 8.4 Chain-of-Verification [V2: D-3]

After response generation, a separate verification pass:
1. Lists each factual claim in the response
2. Checks each claim against evidence
3. Revises unsupported claims inline (not post-hoc)

This runs as part of the Reflexion loop — the critique node performs Chain-of-Verification as one of its checks.

### 8.5 UI Indicators

- **Strong citations** (score >= 0.7): Green underline
- **Weak citations** (0.5-0.7): Amber underline
- **Mismatched citations** (< 0.5): Red strikethrough + "Source may not support this claim" tooltip
- **[V2] Refined responses**: Small "Refined" badge if Reflexion loop iterated

---

## 9. Tool Scoping & Least Privilege

### 9.1 Current State

All 8 tools available in all scopes. No filtering. `HITL_TOOLS = frozenset(["transition_deal", "create_deal"])`.

### 9.2 Scope Tool Map (unchanged from V1)

```python
SCOPE_TOOL_MAP: dict[str, frozenset[str]] = {
    "global": frozenset(["list_deals", "search_deals", "duckduckgo_results_json"]),
    "deal": frozenset([
        "get_deal", "get_deal_health", "add_note", "transition_deal",
        "create_deal", "list_deals", "search_deals", "duckduckgo_results_json",
    ]),
    "document": frozenset(["duckduckgo_results_json", "get_deal", "get_deal_health"]),
}
```

### 9.3 Role Tool Map (unchanged from V1)

```python
ROLE_TOOL_MAP: dict[str, frozenset[str]] = {
    "VIEWER": frozenset(["list_deals", "search_deals", "get_deal", "get_deal_health", "duckduckgo_results_json"]),
    "OPERATOR": frozenset([*VIEWER, "add_note"]),
    "APPROVER": frozenset([*OPERATOR, "transition_deal", "create_deal"]),
    "ADMIN": frozenset(["*"]),
}
```

### 9.4 Generalized Tool-Use Verification [V2: B-3 — QW-12]

Extend the No-Illusions Gate pattern from `transition_deal` to ALL mutating tools:

```python
TOOL_POST_CONDITIONS: dict[str, Callable] = {
    "transition_deal": lambda args, result: verify_stage_changed(args["deal_id"], args["to_stage"]),
    "create_deal": lambda args, result: verify_deal_exists(result["deal_id"]),
    "add_note": lambda args, result: verify_note_exists(args["deal_id"], result["note_id"]),
    # Future tools get assertions automatically via decorator
}

async def execute_with_verification(tool_name: str, args: dict) -> ToolResult:
    result = await execute_tool(tool_name, args)
    if tool_name in TOOL_POST_CONDITIONS:
        assertion = TOOL_POST_CONDITIONS[tool_name]
        if not await assertion(args, result):
            logger.error(f"Post-condition FAILED for {tool_name}")
            return ToolResult(ok=False, error="Verification failed — tool did not produce expected effect")
    return result
```

### 9.5 Schema-Validated Tool Arguments [V2: D-2 — QW-11]

Add `extra="forbid"` to ALL tool input schemas. Replace manual validation with single `model_validate()`:

```python
class TransitionDealInput(BaseModel):
    model_config = ConfigDict(extra="forbid")  # [V2: Catches hallucinated args]
    deal_id: str
    from_stage: str
    to_stage: str
    reason: str | None = None
```

### 9.6 JIT (Just-in-Time) Tool Access [V2: I-4]

For future expansion: ephemeral one-time permissions instead of static RBAC.

```python
class JITPermission:
    """Temporary, single-use tool permission."""
    tool_name: str
    granted_to: str
    granted_by: str
    expires_at: datetime
    used: bool = False
    scope: str  # deal_id or "global"
```

**Classification**: Bucket 3 (Production/Enterprise). Prototype uses static RBAC.

### 9.7 Expanded HITL Gating

```python
HITL_TOOLS = frozenset([
    "transition_deal",
    "create_deal",
    # [V2: Future additions]
    # "delete_deal",
    # "send_email",
    # "execute_action",
    # "modify_deal_brain",  — brain corrections require approval
])
```

---

## 10. Multi-User Hardening

### 10.1 Current State (Evidence)

| Component | User Isolation | Evidence |
|-----------|---------------|----------|
| Dashboard middleware | **NONE** | `middleware.ts:24-130` — no JWT |
| Agent API chatbot | Dual auth, service token = `user_id=0` | `auth.py:163-220` |
| Agent API user/session | **YES** — SQLite tables with FK | `schema.sql:1-30` |
| LangGraph checkpoints | **NO** — `thread_id` only | Standard `AsyncPostgresSaver` |
| Decision ledger | **YES** — `user_id` indexed | `002_decision_ledger.sql` |
| localStorage | **NO** — keys not namespaced | `chat-history.ts:10-12` |

### 10.2 Phase 1: X-User-Id Header [V2: GAP-H2 fix — phased approach]

**Phase 1** (prototype): Dashboard sends `X-User-Id` header. Agent API reads it. No JWT yet.
**Phase 2** (multi-user): Full JWT with signature verification.

```typescript
// middleware.ts — Phase 1 (prototype, single-user)
const headers = new Headers(request.headers);
headers.set('X-User-Id', process.env.ZAKOPS_USER_ID || 'zak');
headers.set('X-User-Role', 'ADMIN');

// Phase 2: JWT validation
// const token = request.cookies.get('zakops_token')?.value;
// const payload = verifyJwt(token);
// headers.set('X-User-Id', payload.sub);
// headers.set('X-User-Role', payload.role);
```

### 10.3 Thread Ownership (unchanged from V1)

`thread_ownership` table enforces that:
- Every `ChatRepository.get_thread()` includes `user_id` check
- Every LangGraph checkpoint read goes through `ThreadOwnershipRepository.verify()`
- PermissionError raised if ownership doesn't match

### 10.4 Deal Access Control (unchanged from V1)

`deal_access` table with role-based permissions per deal. Deal creator gets `admin`. Deal threads inherit deal access.

### 10.5 @Agent Mentions in Deal Notes [V2: G-2 — QW-5]

Type `@agent <question>` in a deal note to invoke the AI inline, visible to all team members:

```
Implementation:
1. Deal notes textarea watches for @agent pattern
2. On submit, extracts the question portion
3. Calls POST /api/v1/agent/invoke with scope=deal, deal_id=current
4. Response injected as a system-attributed note: "🤖 Agent: {response}"
5. Visible to all users with deal access
```

### 10.6 Shared Deal Workspace Presence [V2: G-3]

Live presence indicators on deal workspace:

```
Implementation (Bucket 2):
- WebSocket connection per user per deal workspace
- Broadcast: {user_id, display_name, active_tab, typing: bool}
- UI: Avatar pills at top-right of deal workspace
- Figma/Linear-style cursor presence (optional, Bucket 3)
```

### 10.7 Role-Based Redaction Views [V2: I-3]

Share chat threads with external parties where sensitive entities are auto-redacted:

```
Implementation (Bucket 3):
- GET /api/v1/chatbot/threads/{id}/export?redact=external
- Redaction rules per entity type: price/strategy/internal_assessment → [REDACTED]
- NER-based entity detection + manual redaction rules per deal
- "Secure View" URL with time-limited access token
```

---

## 11. Delete, Retention, Legal Hold, GDPR

### 11.1 Delete Semantics (unchanged from V1)

| Operation | Mechanism | Restore Window | Blocked By |
|-----------|-----------|---------------|------------|
| **Soft delete** | `deleted=TRUE, deleted_at=NOW()` | 30 days | `legal_hold=TRUE` → 409 |
| **Recycle bin** | `GET /api/v1/chatbot/threads?deleted=true` | Restore or permanent | — |
| **Hard delete** | Cascading delete across all tables | Irreversible | `legal_hold=TRUE` → 409 |
| **Auto-purge** | Retention job, 30 days | — | `legal_hold=TRUE` → skipped |

### 11.2 Cascading Hard Delete

```sql
-- 1. Derived data
DELETE FROM session_summaries WHERE thread_id = $1;
DELETE FROM turn_snapshots WHERE thread_id = $1;
DELETE FROM cost_ledger WHERE thread_id = $1;
DELETE FROM cross_db_outbox WHERE payload->>'thread_id' = $1;  -- [V2: outbox cleanup]

-- 2. Audit data (anonymize)
UPDATE decision_ledger SET user_id = 'DELETED', trigger_content = '[REDACTED]',
    tool_args = '[REDACTED]', tool_result_preview = '[REDACTED]',
    response_preview = '[REDACTED]', selection_reason = '[REDACTED]'
WHERE thread_id = $1;

-- 3. LangGraph checkpoints
DELETE FROM checkpoint_writes WHERE thread_id = $1;
DELETE FROM checkpoint_blobs WHERE thread_id = $1;
DELETE FROM checkpoints WHERE thread_id = $1;

-- 4. Thread ownership (redundant with FK CASCADE — kept as defense-in-depth for explicit audit trail)
DELETE FROM thread_ownership WHERE thread_id = $1;

-- 5. Messages
DELETE FROM chat_messages WHERE thread_id = $1;

-- 6. Thread itself
DELETE FROM chat_threads WHERE id = $1;
```

### 11.3 Cross-Database Deal Reference Reconciliation [V2: GAP-H4 fix]

7 tables in `zakops_agent` reference `deal_id` from `zakops` database. No FK possible across databases.

**Solution**: Application-level `DealReferenceValidator` + periodic reconciliation:

```python
class DealReferenceValidator:
    """Validates cross-database deal_id references."""

    async def validate_deal_exists(self, deal_id: str) -> bool:
        """Check deal exists in zakops.deals via backend API."""
        resp = await self.backend_client.get(f"/api/deals/{deal_id}")
        return resp.status_code == 200

    async def reconcile_orphans(self):
        """Find chat data referencing deals that no longer exist."""
        agent_deal_ids = await self.get_all_referenced_deal_ids()  # From zakops_agent
        backend_deal_ids = await self.backend_client.get("/api/deals/ids")  # From zakops
        orphans = agent_deal_ids - set(backend_deal_ids)
        for deal_id in orphans:
            logger.warning(f"Orphaned deal reference: {deal_id}")
            # Mark threads as orphaned, don't auto-delete (admin review)
```

**Schedule**: Hourly via background worker. Webhook on deal deletion (backend fires event).

### 11.4 Retention Policy (unchanged from V1)

| Data Type | Retention | Cleanup Mechanism | Frequency | Enforcement Path | Trigger |
|-----------|-----------|-------------------|-----------|-----------------|---------|
| Active threads | Indefinite | — | — | — | — |
| Soft-deleted threads | 30 days | `chat_retention_cleanup()` | Daily | pg_cron or OS cron | `deleted_at < NOW() - INTERVAL '30 days'` |
| Turn snapshots (default) | 90 days | Partition drop | Monthly | Same as partition automation (S6.2) | `created_at` range |
| Turn snapshots (compliance) | 7 years | Partition drop | Yearly | Manual review + automated | `compliance_tier = TRUE` |
| Decision ledger | 1 year | `DELETE WHERE created_at < interval` | Monthly | pg_cron or OS cron | Date threshold |
| Cost ledger | 2 years | Partition drop | Monthly | Same as partition automation | `created_at` range |
| Deal brain history | 2 years | `DELETE WHERE created_at < interval` | Monthly | pg_cron or OS cron | Date threshold |
| **[V2.1] cross_db_outbox** | **7 days (status=done)** | `DELETE WHERE status='done' AND processed_at < NOW() - '7 days'` | **Daily** | pg_cron or OS cron | Status + date |
| **[V2.1] cross_db_outbox (failed)** | **30 days** | Manual review; dead letter alert after 3 retries | **Daily check** | Admin alert endpoint | `status='failed' AND retry_count >= max_retries` |
| **[V2.1] user_identity_map** | Follows user lifecycle | Deleted in GDPR cascade (S11.5 step 15) | On demand | Application code | User deletion request |
| **[V2.1] deal_budgets** | Follows deal lifecycle | Deleted when deal hard-deleted via reconciliation (S11.3) | Hourly | DealReferenceValidator | Orphan detection |

**[V2.1] Enforcement Contract**: Every row in this table MUST have a corresponding implementation. "Descriptive but unenforced" retention policies are prohibited. Each cleanup mechanism must be verifiable via:
```sql
-- Verify no data exceeds retention policy
SELECT 'soft_deleted_threads' AS policy,
       COUNT(*) AS violations
FROM chat_threads
WHERE deleted = TRUE AND deleted_at < NOW() - INTERVAL '30 days'
UNION ALL
SELECT 'outbox_done', COUNT(*)
FROM cross_db_outbox
WHERE status = 'done' AND processed_at < NOW() - INTERVAL '7 days'
UNION ALL
SELECT 'decision_ledger', COUNT(*)
FROM decision_ledger
WHERE created_at < NOW() - INTERVAL '1 year';
-- Expected: 0 violations for all policies
```

### 11.5 GDPR Full User Deletion [V2: updated for VARCHAR user_id]

**Cascade checklist** (single transaction per database):

```
zakops_agent (PostgreSQL):
  1. chat_messages        WHERE user_id = $1
  2. session_summaries    WHERE thread_id IN (user's threads)
  3. turn_snapshots       WHERE user_id = $1
  4. cost_ledger          WHERE user_id = $1
  5. cross_db_outbox      WHERE payload->>'user_id' = $1
  6. chat_threads         WHERE user_id = $1
  7. thread_ownership     WHERE user_id = $1
  8. tool_executions      WHERE approval_id IN (SELECT id FROM approvals WHERE actor_id = $1)
  9. approvals            WHERE actor_id = $1
  10. decision_ledger     → ANONYMIZE (user_id='DELETED')
  11. audit_log           → ANONYMIZE (actor_id='DELETED')
  12. checkpoints         WHERE thread_id IN (user's threads)
  13. checkpoint_blobs    WHERE thread_id IN (user's threads)
  14. checkpoint_writes   WHERE thread_id IN (user's threads)
  15. user_identity_map   WHERE canonical_id = $1  -- [V2: replaces SQLite user table]

zakops (PostgreSQL):
  16. user_preferences    WHERE user_id = $1
  17. deal_access         WHERE user_id = $1
  18. deal_brain_history  → ANONYMIZE (triggered_by='DELETED')
  19. decision_outcomes   WHERE recorded_by = $1  -- [V2: new table]

mem0:
  20. forget_user_memory(user_id)
```

---

## 12. Export, Deal Attachment & Living Deal Memo

### 12.1 Export Formats (unchanged from V1)

**MVP: Markdown** — full conversation with citations, proposals, evidence bundle, Deal Brain impact.

**Future**: JSON (machine-readable), PDF (via Markdown → PDF).

### 12.2 Export API (unchanged from V1)

`GET /api/v1/chatbot/threads/{id}/export?format=markdown`

### 12.3 Attach Transcript to Deal (unchanged from V1)

`POST /api/v1/chatbot/threads/{id}/attach`

### 12.4 Living Deal Memo [V2: J-1]

Deal Brain auto-generates a human-readable Markdown/PDF memo that updates in real-time:

```
GET /api/deals/{id}/memo?format=markdown
Response: Generated deal memo including:
  - Executive summary (from Deal Brain summary)
  - Key metrics table (from Deal Brain facts)
  - Risk assessment (from Deal Brain risks)
  - Decision history (from Deal Brain decisions)
  - Open items (from Deal Brain open_items)
  - Timeline of key events
  - Appendix: source citations for every fact

Auto-refresh: Regenerated when Deal Brain version changes.
Downloadable: PDF via server-side Markdown → PDF conversion.
```

**Classification**: Bucket 2 (Functional Expansion). Prototype shows Deal Brain directly; Living Memo adds polish.

---

## 13. Cost Governance & Observability

### 13.1 Current State (Evidence)

| Tracker | Location | Persisted? | Budget |
|---------|----------|-----------|--------|
| `telemetry/cost_tracking.py` (Agent API) | In-memory list | **NO** | None |
| `core/cost_tracking.py` (Agent API) | In-memory dict | **NO** | $50/day |
| `chat_budget.py` (Backend) | `/tmp/chat_budget_state.json` | **YES** (temp file) | $5/day Gemini, 60 RPM |

### 13.2 Persistent Cost Ledger

Schema defined in Section 3.3 (`cost_ledger` table). `deal_cost_summary` is now a regular VIEW (not materialized) to avoid refresh issues [V2: GAP-M12 fix].

### 13.3 deal_budgets [V2: GAP-C1 fix]

`deal_budgets.deal_id` is a standalone PRIMARY KEY with NO foreign key constraint. V1 had `REFERENCES chat_threads(deal_id)` which is invalid because `deal_id` is not unique on `chat_threads`. Application-level validation ensures the deal exists via backend API call.

### 13.4 Predictive Budgeting [V2: H-5 — QW-8]

```python
async def update_budget_predictions(deal_id: str):
    """Calculate predictive budget metrics."""
    # Rolling 7-day average daily cost
    avg_daily = await cost_repo.get_avg_daily_cost(deal_id, days=7)
    budget = await budget_repo.get_budget(deal_id)
    if budget and avg_daily > 0:
        remaining = budget.monthly_limit_usd - await cost_repo.get_monthly_spend(deal_id)
        days_until_exhaustion = remaining / avg_daily
        projected_monthly = avg_daily * 30

        await budget_repo.update_predictions(deal_id,
            avg_daily_cost=avg_daily,
            projected_monthly=projected_monthly,
            budget_exhaustion_date=date.today() + timedelta(days=days_until_exhaustion)
        )

        if days_until_exhaustion <= 7:
            yield sse_event("budget_warning", {
                "deal_id": deal_id,
                "message": f"Budget will be exhausted in {days_until_exhaustion:.0f} days",
                "projected_monthly": float(projected_monthly),
                "budget": float(budget.monthly_limit_usd)
            })
```

### 13.5 Budget Enforcement (unchanged from V1)

Before every LLM call, check deal budget. Hard cap blocks; soft threshold triggers warning SSE.

### 13.6 Bottleneck Heatmap [V2: F-3 — QW-9]

Temperature overlay on pipeline stages:

```python
async def compute_pipeline_heatmap() -> list[StageTemperature]:
    """Compute 'temperature' for each pipeline stage."""
    stages = await deal_repo.get_stage_metrics()
    result = []
    for stage in stages:
        temp = compute_temperature(
            deal_count=stage.deal_count,
            avg_duration_days=stage.avg_duration,
            stale_ratio=stage.stale_count / max(stage.deal_count, 1),
            historical_median=stage.historical_median_duration
        )
        result.append(StageTemperature(
            stage=stage.name, temperature=temp,  # 0.0 (cold) to 1.0 (hot)
            deal_count=stage.deal_count,
            avg_duration=stage.avg_duration
        ))
    return result
```

**UI**: Color gradient overlay on pipeline view — blue (cold, flowing) → red (hot, bottleneck).

### 13.7 UI Surfaces

**1. Chat Debug Panel → "Cost" tab** (unchanged from V1)

**2. Deal Workspace header → "Usage" badge** (unchanged from V1)

**3. Settings → "Usage" section** (unchanged from V1)

**4. [V2] Pipeline view → Bottleneck Heatmap overlay**

**5. [V2] Deal Budget → Predictive forecast**: "Budget exhaustion in 4 days" warning card

---

## 14. Offline & Degraded Mode

### 14.1 Current Behavior (Unspecified)

When backends are down:
- Dashboard middleware returns JSON 502 (`middleware.ts:92-98`)
- Chat route has 3-fallback chain: Agent → Backend → static response
- localStorage data remains accessible in browser

### 14.2 Specified Degraded Behaviors (unchanged from V1)

| Backend Status | Chat Behavior | Data Access |
|----------------|--------------|-------------|
| Both up | Full functionality | PostgreSQL canonical |
| Backend down, Agent up | Tool-calling only | Agent reads from checkpoints |
| Agent down, Backend up | Evidence-grounded chat only | Backend reads from PostgreSQL |
| Both down | Read-only from localStorage + banner | localStorage only |
| PostgreSQL down | Banner: "Chat history unavailable" | In-memory only |

### 14.3 PGlite for Advanced Offline [V2: K-1]

Replace localStorage with PGlite (WASM Postgres) in browser for full SQL querying while offline:

```
Architecture:
- PGlite instance in browser (WebAssembly)
- Mirrors: chat_threads, chat_messages (most recent 100 per thread), deal_brain (facts only)
- Sync: on page load, delta-sync from PostgreSQL to PGlite via new endpoint
  GET /api/v1/chatbot/sync?since={last_sync_timestamp}
- Offline queries: full SQL on cached data — thread search, message history, fact lookup
- Conflict resolution: server always wins (last-write-wins on reconnect)
```

**Classification**: Bucket 3 (Production/Enterprise). Prototype uses localStorage cache.

---

## 15. Proposal Pipeline Hardening

### 15.1 Current State (Evidence)

| Issue | Evidence |
|-------|----------|
| `POST /api/chat/execute-proposal` is a **501 stub** | `execute-proposal/route.ts` returns 501 |
| Proposals embedded in messages, no separate table | No proposals table exists |
| No proposal status history | Status transitions unlogged |
| `create_action` auto-approves by default | `chat_orchestrator.py:2195-2200` |

### 15.2 Hardening Specification

1. **Implement `execute-proposal` route**: Wire to backend `execute_proposal()` method.

2. **Proposal status tracking** (in `chat_messages.proposals` JSONB):
   ```json
   {
       "proposal_id": "prop-abc123",
       "type": "stage_transition",
       "status": "pending_approval",
       "status_history": [
           {"status": "pending_approval", "at": "2026-02-12T14:30:00Z"},
           {"status": "approved", "at": "2026-02-12T14:35:00Z", "by": "zak@example.com"},
           {"status": "executed", "at": "2026-02-12T14:35:01Z", "result": "success"}
       ]
   }
   ```

3. **Remove auto-approve** for `create_action`.

### 15.3 Proposal Concurrency Control [V2: GAP-L3 fix]

JSONB path updates for proposal status are vulnerable to lost updates under concurrency. Use optimistic locking:

```python
async def update_proposal_status(message_id: str, proposal_id: str, new_status: str, by: str):
    """Atomic proposal status update with optimistic locking."""
    async with db.transaction():
        # Read current message with FOR UPDATE lock
        msg = await db.fetchrow(
            "SELECT proposals FROM chat_messages WHERE id = $1 FOR UPDATE", message_id
        )
        proposals = msg['proposals']
        for p in proposals:
            if p['proposal_id'] == proposal_id:
                p['status_history'].append({
                    'status': new_status, 'at': datetime.utcnow().isoformat(), 'by': by
                })
                p['status'] = new_status
                break
        await db.execute(
            "UPDATE chat_messages SET proposals = $1 WHERE id = $2",
            json.dumps(proposals), message_id
        )
```

### 15.4 correct_brain_summary Handler [V2: GAP-M10 fix]

```python
# In chat_orchestrator.py proposal handlers
PROPOSAL_HANDLERS = {
    "stage_transition": handle_stage_transition,
    "add_note": handle_add_note,
    "search_web": handle_search_web,
    "create_action": handle_create_action,
    "mark_complete": handle_mark_complete,
    "add_document": handle_add_document,
    "correct_brain_summary": handle_correct_brain_summary,  # [V2: GAP-M10]
}

async def handle_correct_brain_summary(proposal: dict, user_id: str, deal_id: str):
    """Handle approved brain summary correction."""
    old_brain = await brain_repo.get_brain(deal_id)
    # Snapshot current state to history
    await brain_repo.save_history(deal_id, old_brain, trigger_type='correction', triggered_by=user_id)
    # Regenerate summary from all facts
    new_summary = await brain_service.regenerate_summary(deal_id)
    await brain_repo.update_summary(deal_id, new_summary, user_id)
    return {"ok": True, "new_version": old_brain.version + 1}
```

---

## 16. Implementation Roadmap

### Dependency Graph

```
P0: Storage Unification (S3) ──────┐
P0: Deal Brain v2 (S4) ───────────┤  [V2: Brain elevated to P0 — keystone dependency]
P0: Multi-User Identity (S10) ─────┤
                                    ▼
P1: Input Defenses (S7) ──────────► All P2+ features require P0
P1: Delete/Retention/GDPR (S11) ──► Requires S3 (canonical store)
P1: Tool Scoping (S9) ────────────► Requires S10 (role identity)
P1: Quick Wins (13 items) ────────► Requires S3 + S4
                                    │
                                    ▼
P2: Summarization + Memory (S5) ──► Requires S3 (canonical messages)
P2: Cost Governance (S13) ────────► Requires S3 (cost_ledger)
P2: Citation + Reflexion (S8) ────► Independent (can parallel)
P2: RAG Enhancement (S18) ────────► Requires S3 + Evidence Builder
P2: Cognitive Intelligence (S20) ─► Requires S4 (Deal Brain)
                                    │
                                    ▼
P3: Deterministic Replay (S6) ────► Requires S5 + S7
P3: Export + Attach (S12) ────────► Requires S3
P3: Proposal Hardening (S15) ─────► Requires S3 + S10
P3: Agent Architecture (S19) ─────► Requires S4 + S5 + S18
P3: Ambient Intelligence (S21) ───► Requires S4 + S5 + S13
                                    │
                                    ▼
P4: Counterfactual Analysis (S6.5)► Requires S6
P4: Cross-Deal Graph (S4, C-4) ──► Requires S4 at scale
P4: PGlite Offline (S14.3) ──────► Requires S3 stable
P4: Semantic Firewall (S7.3.L5) ─► Requires training data
```

### Timeline

| Priority | Section | Effort | Key Deliverables |
|----------|---------|--------|-----------------|
| **P0** | S3: Storage Unification | 2 weeks | Migration 004, ChatRepository, 5 endpoints, dual-write, backfill |
| **P0** | S4: Deal Brain v2 | 2 weeks | Migration 028, extraction, DealBrain.tsx, drift detection |
| **P0** | S10: Multi-User Identity | 1 week | X-User-Id header, thread_ownership, deal_access |
| **P1** | S7: Input Defenses | 1 week | injection_guard.py, canary tokens, session tracker |
| **P1** | S11: Delete/Retention | 1.5 weeks | Cascading delete, retention jobs, legal hold, GDPR |
| **P1** | S9: Tool Scoping | 1 week | SCOPE_TOOL_MAP, ROLE_TOOL_MAP, schema validation |
| **P1** | Quick Wins (13) | 2 weeks | Ghost Knowledge, Momentum Score, JSON Mode, etc. |
| **P2** | S5: Summarization + Memory | 2 weeks | Summarizer, tiered memory, MemoryStatePanel |
| **P2** | S13: Cost Governance | 1.5 weeks | cost_ledger, budgets, predictive, heatmap |
| **P2** | S8: Citation + Reflexion | 1 week | audit_citations(), ReflexionCritique, UI indicators |
| **P2** | S18: RAG Enhancement | 1.5 weeks | BM25 fusion, chunk headers, deal-scoped namespaces |
| **P2** | S20: Cognitive Intelligence | 1.5 weeks | Decision journal, momentum, forgetting curve |
| **P3** | S6: Replay + Counterfactual | 2 weeks | turn_snapshots, replay endpoint, counterfactual API |
| **P3** | S12: Export + Living Memo | 1 week | Export endpoint, attach, auto-generated memo |
| **P3** | S15: Proposal Hardening | 0.5 weeks | Wire execute-proposal, correct_brain_summary handler |
| **P3** | S19: Agent Architecture | 2 weeks | Multi-specialist, plan-and-execute, typed SSE |
| **P3** | S21: Ambient Intelligence | 2 weeks | Morning briefing, command palette, anomaly alerts |
| **P4** | Advanced features | 4+ weeks | Cross-deal graph, PGlite, semantic firewall, JIT access |

**Total**: ~24 weeks of focused development (P0-P3), with P4 ongoing.

### Migration Order

| Order | Migration File | Database | Section |
|-------|---------------|----------|---------|
| 1 | `004_chat_canonical_store.sql` | `zakops_agent` | S3, S5, S6, S13 |
| 2 | `028_deal_brain.sql` | `zakops` | S4, S10, S20 |
| 3 | `029_legal_hold.sql` | `zakops` | S11 |

Rollback scripts: `004_chat_canonical_store_rollback.sql`, `028_deal_brain_rollback.sql`, `029_legal_hold_rollback.sql` [V2: GAP-M11 fix].

### Contract Surface Updates [V2: GAP-H3 fix]

New endpoints that must be added to the OpenAPI contract and sync pipeline:

| Endpoint | Service | Contract Surface |
|----------|---------|-----------------|
| `GET /api/v1/chatbot/threads` | Agent API | Surface 2 (Agent OpenAPI) |
| `GET /api/v1/chatbot/threads/{id}/messages` | Agent API | Surface 2 |
| `POST /api/v1/chatbot/threads` | Agent API | Surface 2 |
| `PATCH /api/v1/chatbot/threads/{id}` | Agent API | Surface 2 |
| `DELETE /api/v1/chatbot/threads/{id}` | Agent API | Surface 2 |
| `GET /api/v1/chatbot/threads/{id}/export` | Agent API | Surface 2 |
| `POST /api/v1/chatbot/threads/{id}/attach` | Agent API | Surface 2 |
| `PATCH /api/deals/{id}/brain` | Backend | Surface 1 (Backend OpenAPI) |
| `DELETE /api/deals/{id}/brain/facts/{key}` | Backend | Surface 1 |
| `POST /api/deals/{id}/brain/ghost/{id}/confirm` | Backend | Surface 1 |
| `GET /api/deals/{id}/memo` | Backend | Surface 1 |
| `POST /admin/replay` | Agent API | Surface 2 (admin-only) |
| `POST /admin/counterfactual` | Agent API | Surface 2 (admin-only) |
| `GET /api/v1/chatbot/sync` | Agent API | Surface 2 |
| `DELETE /api/user/account` | Both | Surface 1 + 2 |

After implementing: run `make update-spec && make update-agent-spec && make sync-all-types`.

---

## 17. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|-----------|
| R1 | Dual-write phase introduces inconsistency | Medium | High | Backfill script with checksums; reconciliation query |
| R2 | localStorage cache diverges from PostgreSQL | Low | Medium | Cache invalidation on every fetch; version counter |
| R3 | LLM extraction produces wrong facts in Deal Brain | High | Medium | All auto-extracted facts start at confidence < 1.0 |
| R4 | Summary drift goes undetected | Medium | Medium | Three-mechanism drift detection + active resolution [V2] |
| R5 | Injection patterns too aggressive (false positives) | Medium | Low | Log-only mode first 2 weeks → enforcement mode after review gate (see below) |

**[V2.1] R5 Enforcement Mode Transition Gate:**
```
Phase 1 (Days 1-14):  OBSERVE mode — log all detections, never sanitize or block.
                      Collect: {total_scans, true_positives, false_positives, severity_distribution}
Phase 2 (Day 15):     REVIEW gate — requires human sign-off:
                      - False positive rate < 5% → transition to ENFORCE
                      - False positive rate 5-15% → tune patterns, extend OBSERVE 7 days
                      - False positive rate > 15% → redesign patterns before enforcement
Phase 3 (Post-gate):  ENFORCE mode — sanitize low/medium, block high, escalate 3+ attempts
```
Configuration: `INJECTION_GUARD_MODE` environment variable (`observe` | `enforce`). Default: `observe`.
Transition: Manual — requires explicit config change after gate review. No automatic promotion.
| R6 | JWT migration breaks service-to-service auth | Low | Critical | Keep service token path for S2S; JWT only for user-facing |
| R7 | Cascading delete misses a table | Low | High | Integration test: create → populate → delete → verify zero |
| R8 | Partition management overhead | Low | Low | pg_partman + pg_cron + DEFAULT partition [V2: automated] |
| R9 | Turn snapshot storage grows beyond projection | Medium | Medium | Monthly partition drops; compliance is opt-in |
| R10 | GDPR deletion fails mid-transaction | Low | Critical | Single transaction per DB; rollback; idempotent retry |
| R11 | [V2] Ghost Knowledge produces too many false positives | Medium | Low | Confidence threshold; only flag facts with entity names/numbers |
| R12 | [V2] Reflexion loop adds latency to every response | Medium | Medium | Use Gemini Flash for critique (~100ms); skip for deterministic routes |
| R13 | [V2] Cross-deal entity graph produces wrong entity links | Medium | Medium | Normalized names via NER; human review for cross-deal connections |
| R14 | [V2] Forgetting curve decays important facts too aggressively | Low | Medium | Conservative decay rate (0.1); facts verified by user never decay below 0.5 |
| R15 | [V2] Outbox worker fails, brain extraction backlog grows | Low | High | Dead letter queue after 3 retries; admin alert; manual reprocess endpoint |
| R16 | [V2] Canary tokens detectable by sophisticated adversary | Low | Low | Rotate token encoding scheme; use multiple encoding methods |

---

## 18. RAG & Retrieval Enhancement Architecture

This section covers improvements to the evidence retrieval pipeline that feeds the chat system.

### 18.1 Hybrid Dense+Sparse Retrieval (BM25 Fusion) [A-1]

**Current**: Pure pgvector dense retrieval via `rag_rest_api.py:106-171`.
**Problem**: M&A conversations are dense with proper nouns and exact figures. "Acme Corp $2.1M EBITDA" fails pure semantic search.

**Design**:
```python
class HybridRetriever:
    """BM25 + pgvector fusion via Reciprocal Rank Fusion."""

    async def search(self, query: str, deal_id: str, top_k: int = 10) -> list[RankedChunk]:
        # Dense retrieval (existing pgvector)
        dense_results = await self.vector_search(query, deal_id, top_k=top_k * 2)

        # Sparse retrieval (BM25 via pg_trgm or tsvector)
        sparse_results = await self.bm25_search(query, deal_id, top_k=top_k * 2)

        # Reciprocal Rank Fusion
        fused = self.rrf_merge(dense_results, sparse_results, k=60)
        return fused[:top_k]

    def rrf_merge(self, *result_lists, k=60) -> list[RankedChunk]:
        scores = defaultdict(float)
        for results in result_lists:
            for rank, chunk in enumerate(results):
                scores[chunk.id] += 1.0 / (k + rank + 1)
        return sorted(scores.items(), key=lambda x: -x[1])
```

**Files**: `rag_rest_api.py:106-171`, `chat_evidence_builder.py:312-366`
**Prerequisite**: Add GIN index on `crawledpage.content` for tsvector search.
**Classification**: Bucket 1 (Prototype-Critical) — evidence accuracy is foundational.

### 18.2 Contextual Chunk Headers [A-4 — QW-4]

Prepend each RAG chunk with document title, section hierarchy, and deal association before embedding:

```python
def add_contextual_header(chunk: str, metadata: dict) -> str:
    header = f"Document: {metadata['title']}\n"
    if metadata.get('section'):
        header += f"Section: {metadata['section']}\n"
    if metadata.get('deal_id'):
        header += f"Deal: {metadata['deal_id']}\n"
    return f"{header}---\n{chunk}"
```

**Impact**: Better retrieval relevance AND better citations (LLM can reference specific documents).
**Classification**: Bucket 1 (Prototype-Critical) — trivial change, high leverage.

### 18.3 HyDE (Hypothetical Document Embeddings) [A-2]

Before RAG query, generate a hypothetical answer via cheap LLM call, embed that as the retrieval query:

```python
async def hyde_query(user_question: str) -> str:
    """Generate hypothetical answer for improved retrieval."""
    hypothetical = await llm.generate(
        f"Write a brief paragraph answering this M&A question: {user_question}",
        model="gemini-flash", max_tokens=150
    )
    return hypothetical  # Embed this instead of the raw question
```

**Classification**: Bucket 2 (Functional Expansion) — improves vague queries.

### 18.4 Deal-Scoped RAG Namespaces [A-5]

Partition the vector store by `deal_id` so queries only search within the relevant deal's documents:

```sql
-- Add deal_id to vector index
CREATE INDEX idx_embeddings_deal ON chunk_embeddings(deal_id, embedding)
    USING ivfflat (embedding vector_cosine_ops);
```

**Classification**: Bucket 1 (Prototype-Critical) — prevents cross-deal information leakage.

### 18.5 RAPTOR Hierarchical Retrieval [A-3]

Build tree of summaries: leaf=raw chunks, intermediate=cluster summaries, root=deal-level summaries. Top-down traversal for questions at any granularity level.

**Classification**: Bucket 3 (Production/Enterprise) — requires significant infrastructure.

---

## 19. Agent Architecture & Autonomous Capabilities

### 19.1 JSON Mode via vLLM Structured Generation [D-1 — QW-10]

Use `response_format={"type": "json_object"}` and Outlines-based constrained generation for all JSON-producing prompts:

```python
# In llm.py — for vLLM calls
async def generate_json(self, prompt: str, schema: type[BaseModel], **kwargs) -> BaseModel:
    response = await self.client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        **kwargs
    )
    return schema.model_validate_json(response.choices[0].message.content)
```

**Impact**: Eliminates entire class of JSON parsing bugs in extraction, summarization, tool args.
**Classification**: Bucket 1 (Prototype-Critical) — reduces failure modes.

### 19.2 Typed SSE Event Schema with Runtime Validation [D-4]

Discriminated union Pydantic models for each SSE event type:

```python
from typing import Literal, Union

class MessageChunkEvent(BaseModel):
    type: Literal["message_chunk"] = "message_chunk"
    content: str

class BrainUpdatedEvent(BaseModel):
    type: Literal["brain_updated"] = "brain_updated"
    deal_id: str
    version: int
    changes: dict

SSEEvent = Union[MessageChunkEvent, BrainUpdatedEvent, ...]  # Discriminated union

def emit_sse(event: SSEEvent) -> str:
    """Validate and serialize SSE event."""
    validated = event.model_validate(event)  # Runtime check
    return f"data: {validated.model_dump_json()}\n\n"
```

**Classification**: Bucket 2 (Functional Expansion) — improves type safety.

### 19.3 Plan-and-Execute Decomposition [B-2]

For complex multi-step queries, generate a structured execution plan first:

```python
class PlanAndExecuteGraph:
    """For complex queries: plan steps, then execute sequentially."""

    async def plan(self, query: str, context: dict) -> list[Step]:
        plan_prompt = f"Break this M&A question into executable steps:\n{query}"
        plan = await self.llm.generate_json(plan_prompt, PlanSchema, model="gemini-flash")
        return plan.steps

    async def execute(self, steps: list[Step], context: dict) -> str:
        results = []
        for step in steps:
            result = await self.execute_step(step, context, prior_results=results)
            results.append(result)
        return self.synthesize(query, results)
```

**Classification**: Bucket 2 (Functional Expansion) — handles complex multi-step queries.

### 19.4 Multi-Specialist Agent Delegation [B-4]

Route complex queries to specialist sub-graphs:

```python
SPECIALISTS = {
    "financial_analysis": FinancialAnalystGraph,  # Numbers, metrics, comparisons
    "risk_assessment": RiskAssessorGraph,          # Risk identification, mitigation
    "deal_memory": DealMemoryExpertGraph,          # Historical facts, precedents
    "market_research": MarketResearchGraph,        # Industry context, comparables
}

async def route_to_specialist(query: str, context: dict) -> str:
    classifier = await llm.generate_json(
        f"Classify this M&A query into a specialist domain: {query}",
        SpecialistClassification
    )
    specialist = SPECIALISTS.get(classifier.domain)
    if specialist:
        return await specialist.invoke(query, context)
    return await default_graph.invoke(query, context)  # Fallback
```

**Classification**: Bucket 3 (Production/Enterprise) — requires multiple specialized graphs.

### 19.5 Devil's Advocate Agent [B-6]

Periodic background review of Deal Brain that generates counter-arguments:

```
Trigger: Every 5 turns in deal-scoped chat, or on demand via "challenge my assumptions"
Prompt: "Review this deal's assumptions and facts. Generate counter-arguments and blind spots."
Output: List of challenges displayed as an expandable "Devil's Advocate" card in Deal Brain
```

**Classification**: Bucket 2 (Functional Expansion) — valuable for decision quality.

### 19.6 MCP Server Tools Governance [V2: GAP-L1 fix]

12 MCP tools at `zakops-backend/mcp_server/` currently operate outside COL governance. V2 integration plan:

| MCP Tool | COL Integration | Priority |
|----------|----------------|----------|
| deal_search, deal_get | Already covered by agent tools | P0 |
| note_add | Already covered by agent tools | P0 |
| event_list, action_list | Add to SCOPE_TOOL_MAP as read-only | P1 |
| artifact_upload | Add to HITL_TOOLS | P2 |
| deal_transition | Already in HITL_TOOLS | P0 |
| Others | Audit and classify per scope/role | P2 |

All MCP tool invocations should be logged to `decision_ledger` and tracked by `cost_ledger`.

---

## 20. Cognitive Intelligence & Decision Support

### 20.1 Ghost Knowledge Detection [E-1 — QW-1]

**What**: Detect when users reference deal facts NOT in the Deal Brain — "ghost knowledge" that exists only in the user's head.

**Implementation**: Integrated into Deal Brain extraction prompt (Section 4.4). When the extraction detects a user reference to a specific fact (name, number, date, term) that is NOT in the existing facts list, it flags it as `ghost_knowledge`.

**UI Flow**:
1. Chat response includes `ghost_knowledge_flags` in SSE metadata
2. Dashboard shows inline toast: "You mentioned 'CEO retiring in Q3' — this isn't in the Deal Brain yet"
3. User can [Confirm as Fact] (promotes to `deal_brain.facts` with `source_type: "user_assertion"`) or [Dismiss]

**Why transformative**: This is the *inverse* of hallucination detection. Instead of catching the AI inventing facts, it catches the human holding unrecorded facts. Closes the gap between team knowledge and system knowledge — the #1 problem in M&A due diligence.

### 20.2 Deal Momentum Score [F-1 — QW-2]

**What**: A single 0-100 composite metric per deal combining five signals.

```python
def compute_momentum_score(deal_id: str, metrics: DealMetrics) -> float:
    """Composite momentum score: 0 (stalled) to 100 (fast-moving)."""
    components = {
        "stage_velocity": score_velocity(metrics.days_in_current_stage, metrics.stage_median_days),
        "event_frequency": score_frequency(metrics.events_last_7d, metrics.avg_events_per_week),
        "open_item_completion": score_completion(metrics.open_items_done, metrics.open_items_total),
        "risk_trajectory": score_risk_trend(metrics.risk_scores_history),
        "action_rate": score_actions(metrics.actions_completed_7d, metrics.actions_total)
    }
    weights = {"stage_velocity": 0.30, "event_frequency": 0.20,
               "open_item_completion": 0.20, "risk_trajectory": 0.15, "action_rate": 0.15}
    score = sum(components[k] * weights[k] for k in weights)
    return round(score, 1)
```

**UI**: Color-coded badge on every deal card and in thread list for deal-scoped chats:
- 80-100: Green (accelerating)
- 50-79: Blue (on track)
- 20-49: Amber (slowing)
- 0-19: Red (stalled)

**Recalculation**: On every Deal Brain update (via trigger in Section 4.3).

### 20.3 Spaced Repetition Deal Memory [E-3 — QW-13]

Proactively surface deal facts the user is likely to have forgotten:

```python
async def get_review_facts(deal_id: str, user_id: str) -> list[ReviewFact]:
    """Get facts that need reinforcement based on forgetting curve."""
    brain = await brain_repo.get_brain(deal_id)
    review_facts = []
    for fact in brain.facts:
        decay_conf = compute_decay_confidence(fact, datetime.utcnow())
        if decay_conf < fact['confidence'] * 0.7:  # Decayed by 30%+
            review_facts.append(ReviewFact(
                key=fact['key'], value=fact['value'],
                original_confidence=fact['confidence'],
                current_confidence=decay_conf,
                days_since_reinforced=days_since(fact['last_reinforced'])
            ))
    return sorted(review_facts, key=lambda f: f.current_confidence)[:5]
```

**UI**: "Remember this?" card shown when opening a deal chat, displaying up to 5 facts that need reinforcement. Clicking "I remember" reinforces the fact (resets `last_reinforced`, increments `reinforcement_count`).

### 20.4 Decision Fatigue Sentinel [E-2]

Track decision velocity and session patterns to detect cognitive fatigue:

```python
class DecisionFatigueSentinel:
    HIGH_STAKES_THRESHOLD = 5  # decisions per 2-hour window
    SESSION_LENGTH_WARNING = timedelta(hours=3)

    async def check(self, user_id: str, session_start: datetime) -> FatigueAlert | None:
        recent_decisions = await self.count_decisions(user_id, window=timedelta(hours=2))
        session_length = datetime.utcnow() - session_start

        if recent_decisions >= self.HIGH_STAKES_THRESHOLD:
            return FatigueAlert(
                type="decision_velocity",
                message=f"You've made {recent_decisions} decisions in the last 2 hours. Consider a review pause.",
                summary=await self.summarize_recent_decisions(user_id)
            )
        if session_length >= self.SESSION_LENGTH_WARNING:
            return FatigueAlert(
                type="session_length",
                message="Long session detected. Key decisions made this session: ...",
                summary=await self.summarize_session_decisions(user_id, session_start)
            )
        return None
```

**Classification**: Bucket 2 (Functional Expansion) — cognitive safety net.

### 20.5 Deal Stall Predictor [F-2]

Survival model from historical stage durations:

```
Input: deal_id, current_stage, days_in_stage
Output: {
    stall_probability: 0.73,
    median_stage_duration: 8,
    percentile: 95,  // "95th percentile for time in this stage"
    similar_deals_that_stalled: [{deal_id, outcome}],
    recommendation: "14 days in screening. Median is 8. Past 15 days = 73% chance of going to junk."
}
```

**Classification**: Bucket 2 (Functional Expansion) — requires historical data.

### 20.6 Risk Cascade Predictor [F-4]

When a risk is flagged on one deal, scan all active deals for the same risk pattern:

```python
async def check_risk_cascade(deal_id: str, new_risk: dict):
    """Portfolio-level risk scan when a new risk is identified."""
    all_brains = await brain_repo.list_active_brains()
    related = []
    for brain in all_brains:
        if brain.deal_id == deal_id:
            continue
        for existing_risk in brain.risks:
            similarity = compute_similarity(new_risk['description'], existing_risk['description'])
            if similarity > 0.7:
                related.append({
                    "deal_id": brain.deal_id,
                    "matching_risk": existing_risk,
                    "similarity": similarity
                })
    if related:
        await alert_service.send("risk_cascade", {
            "source_deal": deal_id,
            "risk": new_risk,
            "affected_deals": related
        })
```

**Classification**: Bucket 2 (Functional Expansion) — portfolio-level intelligence.

### 20.7 Deal Precedent Network [C-5]

Auto-find past deals with similar characteristics:

```
Query: "Find precedent deals for {deal_id}"
Method: Compare Deal Brain fact vectors (embedding similarity) across all completed deals
Output: [{deal_id, similarity_score, key_similarities: [], key_differences: [], outcome}]
Example: "This deal is 87% similar to Apex Systems 2025. That deal had 6-week regulatory delay."
```

**Classification**: Bucket 2 (Functional Expansion) — requires deal history.

### 20.8 Relationship Intelligence Timeline [C-6]

Aggregate all interactions with each broker across all deals:

```
GET /api/brokers/{name}/dossier
Response: {
    broker_name: "John Smith",
    deals_involved: 7,
    success_rate: 0.57,
    avg_response_time: "2.3 days",
    terms_evolution: [{date, deal, key_terms}],
    total_value: "$42M",
    notes_across_deals: [{deal_id, note_preview, date}]
}
```

**Classification**: Bucket 3 (Production/Enterprise) — requires NER and entity linking.

---

## 21. Ambient Intelligence & Predictive Features

### 21.1 Morning Deal Briefing [H-1]

Daily automated summary of overnight changes:

```
Schedule: 7:00 AM user local time (configurable)
Channel: Dashboard notification + optional email
Content:
  "Since your last session (18h ago):
   - Acme Corp: 2 new documents uploaded, momentum 78→82 ↑
   - Beta Inc: LOI approved by legal, stage → Due Diligence
   - 3 quarantine items need review (2 HIGH priority)
   - Gamma LLC: New risk flagged — customer concentration (similar to Delta deal)
   - Budget alert: 2 deals projected to exceed monthly budget this week"
```

**Implementation**:
```python
class MorningBriefingGenerator:
    async def generate(self, user_id: str) -> Briefing:
        last_session = await self.get_last_session_end(user_id)
        deals = await self.get_user_deals(user_id)
        changes = []
        for deal in deals:
            events = await self.get_events_since(deal.deal_id, last_session)
            brain_changes = await self.get_brain_changes_since(deal.deal_id, last_session)
            momentum_delta = await self.get_momentum_delta(deal.deal_id, last_session)
            if events or brain_changes or abs(momentum_delta) > 5:
                changes.append(DealChange(deal=deal, events=events,
                    brain_changes=brain_changes, momentum_delta=momentum_delta))

        briefing_text = await self.llm.generate(
            self.briefing_prompt(user_id, changes), model="gemini-flash"
        )
        return Briefing(text=briefing_text, changes=changes, generated_at=datetime.utcnow())
```

**Classification**: Bucket 2 (Functional Expansion) — high user value, requires Deal Brain + events.

### 21.2 Context-Aware Command Palette [H-2]

Cmd+K palette adapts to current page/deal/conversation:

```
On Dashboard:
  → "Search deals...", "Create deal", "View pipeline", "Show stalled deals"

On Deal Workspace (Acme Corp):
  → "Ask about EBITDA", "Show risk summary", "Compare to similar deals",
    "View decision history", "Check momentum score", recent Deal Brain facts

On Chat (deal-scoped):
  → Recently discussed facts, "Summarize this conversation",
    "Export transcript", "Attach to deal"
```

**Implementation**: Command palette source is a function of current route + deal context + recent Deal Brain queries.

**Classification**: Bucket 2 (Functional Expansion) — productivity enhancement.

### 21.3 Anomaly-Driven Deal Alerts [H-3]

Learn the natural cadence of each deal, alert on deviations:

```python
class DealAnomalyDetector:
    async def check_anomalies(self, deal_id: str) -> list[Anomaly]:
        metrics = await self.get_deal_metrics(deal_id)
        anomalies = []

        # Unusual silence
        if metrics.days_since_last_event > metrics.avg_event_gap * 2:
            anomalies.append(Anomaly(
                type="unusual_silence",
                message=f"No activity for {metrics.days_since_last_event} days (usual: every {metrics.avg_event_gap:.0f} days)"
            ))

        # Sudden burst
        if metrics.events_today > metrics.avg_events_per_day * 3:
            anomalies.append(Anomaly(
                type="activity_burst",
                message=f"{metrics.events_today} events today (usual: {metrics.avg_events_per_day:.0f}/day)"
            ))

        return anomalies
```

**Classification**: Bucket 2 (Functional Expansion) — requires event history baseline.

### 21.4 Ambient Intelligence Sidebar [H-4]

Context sidebar that silently updates with relevant Deal Brain facts, similar deals, and news as user chats:

```
┌─ Ambient Context ──────────────────┐
│                                     │
│ Related Facts:                      │
│ • ARR: $12M (brain, 0.9 conf)      │
│ • Industry: SaaS (brain, 0.95)     │
│                                     │
│ Similar Deals:                      │
│ • Apex Systems (87% similar)        │
│ • CloudNine (72% similar)           │
│                                     │
│ Recent News:                        │
│ • "SaaS valuations drop 15% in Q1" │
│   — TechCrunch, 2 days ago          │
│                                     │
│ ⏳ Decaying Facts (need review):    │
│ • "Target headcount: 85" (0.4 ↓)   │
└─────────────────────────────────────┘
```

**Classification**: Bucket 3 (Production/Enterprise) — requires real-time UI streaming.

### 21.5 Smart Paste with Entity Extraction [J-3 — QW-7]

When pasting text into chat, auto-detect and offer to extract entities:

```
User pastes: "Meeting with John Smith from Acme. They reported $12M ARR and 85 employees.
              EBITDA margin is approximately 17%. Next meeting scheduled for March 15."

→ Toast: "Extracted 5 entities from pasted text:"
  ✓ Person: John Smith (Acme)
  ✓ Financial: ARR = $12M
  ✓ Financial: EBITDA margin = 17%
  ✓ Metric: Employees = 85
  ✓ Date: Next meeting = March 15
  [Add to Deal Brain] [Send as-is]
```

**Implementation**: Client-side entity detection via regex patterns for common M&A terms (currency amounts, percentages, dates, company names). Server-side NER for more complex extraction.

**Classification**: Bucket 1 (Prototype-Critical) — improves data quality from day one.

### 21.6 Sentiment & Negotiation Coach [K-2]

Analyze tone of user messages and counterparty documents:

```
Side-channel advice: "Consider a more conciliatory tone to close this point."
Sentiment tracking per deal over time: positive/neutral/negative trend
```

**Classification**: Bucket 3 (Production/Enterprise) — requires NLP sentiment analysis.

---

## 22. System Classification Table

Every major component and improvement classified into three execution buckets:

- **Bucket 1: Prototype-Critical** — Required for copilot concept validation. Without these, the prototype cannot demonstrate the cognitive operating layer thesis.
- **Bucket 2: Functional Expansion** — Enhances capability and differentiation. Prototype can operate without these, but they represent the competitive moat.
- **Bucket 3: Production/Enterprise** — Compliance, GDPR, multi-tenant, scale, enterprise features. Required for production deployment, not for prototype validation.

| # | Component | Description | Bucket | Justification |
|---|-----------|-------------|--------|---------------|
| **FOUNDATIONS** | | | | |
| S3 | Canonical Storage Unification | PostgreSQL as single source of truth for all chat data | 1 | Without this, chat is unreliable — 3 disconnected stores means data loss and no queryable history. Foundation for everything. |
| S3.2 | User Identity Standardization | VARCHAR(255) user_id everywhere with cross-reference mapping | 1 | GAP-C2 fix. Type mismatch causes runtime errors. Required for any multi-table query. |
| S3.3-M004 | Migration 004 | chat_threads, chat_messages, thread_ownership, cost_ledger, turn_snapshots, outbox | 1 | Physical schema for canonical storage. No tables = no features. |
| S3.3-PART | Partition Automation | pg_partman + DEFAULT partition + cron | 1 | GAP-C3 fix. Static partitions = production failure after month end. Survivability requirement. |
| S3.5 | Chat API Endpoints (5) | CRUD for threads and messages via Agent API | 1 | Replaces stubs. Dashboard cannot load chat history without these. |
| S3.5-MW | Middleware Routing | Route /api/v1/chatbot/* to Agent API | 1 | GAP-H1 fix. Without routing, new endpoints 404. |
| S3.6 | ChatRepository | Single data access layer for all chat operations | 1 | Eliminates direct table queries. Clean write path. |
| S3.7 | Migration Script | Backfill existing SQLite/localStorage data into PostgreSQL | 1 | Without backfill, users lose all existing chat history on migration. |
| S3.8 | Write Path | End-to-end write flow with injection guard, cost tracking, brain extraction | 1 | Defines how data flows through the system. Core wiring. |
| S3.10 | SSE Event Catalog | 14 typed events with documented payloads | 1 | GAP-L2 fix. Without catalog, frontend can't handle events reliably. |
| S4 | Deal Brain v2 | LLM-powered per-deal knowledge store: facts, risks, decisions, assumptions, open items | 1 | **Keystone component**. 14 of 18 cognitive features depend on it. Transforms chat from stateless to intelligent. Without brain, there's no "cognitive" in cognitive operating layer. |
| S4.2-M028 | Migration 028 | deal_brain, deal_brain_history, deal_access, deal_entity_graph, decision_outcomes | 1 | Physical schema for brain. |
| S4.3 | Brain Write Triggers | Per-turn extraction, stage change, consolidation, user edit | 1 | Without triggers, brain never populates. Manual only = useless. |
| S4.4 | Extraction Prompt | Structured LLM extraction with ghost knowledge and entity detection | 1 | The brain's intake mechanism. No extraction = empty brain. |
| S4.5 | Drift Detection | Staleness check, contradiction detection, periodic re-summarization | 1 | Without drift detection, brain becomes unreliable over time. Trust is foundational. |
| S4.7 | DealBrain.tsx | UI panel for viewing/editing brain, with health indicators | 1 | Users must see and interact with the brain. Invisible brain = no value demonstration. |
| S10.2 | X-User-Id Header (Phase 1) | Prototype-phase user identity via header | 1 | Minimum viable user isolation. Without it, all data is user_id=0. GAP-H2 fix. |
| S10.3 | Thread Ownership | Enforces user owns their threads | 1 | Without ownership check, any user sees any thread. Security baseline. |
| **CORE INTELLIGENCE** | | | | |
| S5 | Summarization System | Hybrid extractive + LLM summarization every 5 turns | 1 | Without summarization, long conversations lose all early context (currently truncated to 6 messages). Prototype must show it preserves knowledge across long sessions. |
| S5.2 | Tiered Memory (Working+Recall) | Working memory (last 6) + Recall memory (brain facts + summaries) | 1 | Two-tier is minimum for demonstrating memory persistence. Working alone = current broken state. |
| S7.3-L1 | Injection Guard (Rule-Based) | 15 regex patterns, 3 severity levels, sanitization | 1 | Production input defense. Zero input validation today = critical security gap. |
| S7.3-L2 | Structural Separation | XML-delimited data boundaries in system prompts | 1 | Architectural defense. Costs nothing, prevents category of attacks. |
| S8.2 | Citation Audit | Post-generation semantic similarity check on citations | 1 | Evidence accuracy is the core value proposition. Bad citations = no trust = no product. |
| S9 | Tool Scoping | SCOPE_TOOL_MAP + ROLE_TOOL_MAP, dual enforcement | 1 | Least privilege is a security baseline. All 8 tools everywhere is unacceptable for prototype. |
| S13.2 | Persistent Cost Ledger | cost_ledger table replacing in-memory trackers | 1 | Cost tracking resets on restart today. Unacceptable for demo. |
| S13.3 | Deal Budgets | Per-deal budget enforcement (fixed GAP-C1, no FK) | 1 | Demonstrates cost governance — a selling point for enterprise buyers. |
| QW-1 | Ghost Knowledge Detection | Detect user-held facts not in Deal Brain | 1 | LOW complexity, defines the product. No other M&A tool does this. Core differentiator for prototype demo. |
| QW-2 | Deal Momentum Score | 0-100 composite metric per deal | 1 | LOW complexity, HIGH visibility. Every deal card shows health. Immediate "wow" factor. |
| QW-3 | Canary Tokens | Invisible markers in sensitive RAG chunks for leak detection | 1 | LOW complexity, novel security. Demonstrates security-first thinking to enterprise buyers. |
| QW-4 | Contextual Chunk Headers | Prepend document/section metadata to RAG chunks | 1 | Trivial change (<20 lines), improves retrieval quality across the board. |
| QW-10 | JSON Mode (vLLM Structured Gen) | Constrained JSON output for all extraction prompts | 1 | Eliminates entire class of JSON parsing failures. Reliability baseline. |
| QW-11 | Schema-Validated Tool Args | Strict Pydantic with extra="forbid" on all tool schemas | 1 | Catches hallucinated tool arguments before execution. Safety baseline. |
| QW-12 | Generalized Tool Verification | Post-condition assertions on all mutating tools | 1 | Extends No-Illusions Gate to all tools. Execution integrity. |
| A-1 | Hybrid Dense+Sparse Retrieval | BM25 + pgvector fusion via RRF | 1 | Evidence accuracy is foundational. M&A queries are dense with proper nouns that fail pure semantic search. |
| A-5 | Deal-Scoped RAG Namespaces | Partition vector store by deal_id | 1 | Prevents cross-deal information leakage. Security and accuracy requirement. |
| **FUNCTIONAL EXPANSION** | | | | |
| S4.5-B5 | Active Drift Resolution | Background agent resolves contradictions by searching evidence | 2 | Improves brain accuracy automatically. Prototype can flag contradictions without auto-resolving. |
| S4.6 | Email Integration | Bridge email ingestion pipeline to Deal Brain extraction | 2 | GAP-M9 fix. Important but prototype can work with chat-only extraction. |
| S4-C2 | Forgetting Curve | Ebbinghaus-inspired confidence decay for unreinforced facts | 2 | QW-6. Improves brain accuracy over time. Prototype can show static confidence. |
| S4-C4 | Cross-Deal Entity Graph | Knowledge graph connecting deals by shared entities | 2 | Novel feature but requires deal volume. Prototype validates single-deal brain first. |
| S4-I5 | Decision Journal + Outcome Tracking | Capture decisions with rationale, correlate with outcomes | 2 | Powerful feature but outcomes take months. Capture rationale in prototype, track outcomes later. |
| S4-J2 | Fact Lineage Explorer | Visual UI linking facts to source chat messages/documents | 2 | Trust-building feature. Brain with lineage > brain without, but brain itself is Bucket 1. |
| S5.2-ARCH | Archival Memory Tier | Full history searchable on demand | 2 | Working + Recall is sufficient for prototype. Archival adds depth for long-running deals. |
| S5.4 | Background Memory Consolidation | Idle-time brain re-summarization, cross-deal patterns, embedding precompute | 2 | Optimization. Prototype can consolidate synchronously. |
| S6 | Deterministic Replay | turn_snapshots with full input/output capture, replay endpoint | 2 | Compliance feature. Important for enterprise, not for prototype validation. |
| S7.3-L3 | Session-Level Escalation | Lockdown after 3 injection attempts | 2 | Enhancement over base injection guard. Prototype can log and sanitize without escalation. |
| S8.3 | Reflexion Self-Critique | Post-generation critique loop, max 2 refinements | 2 | Improves response quality. Prototype can ship without self-critique if citation audit passes. |
| S8.4 | Chain-of-Verification | Inline factual claim verification | 2 | Subset of Reflexion. Valuable but additive, not foundational. |
| S11 | Delete/Retention/GDPR | Cascading hard delete, retention jobs, legal hold, GDPR endpoint | 2 | Required for real users but prototype can soft-delete only. Full cascade is pre-production. |
| S11.3 | Cross-DB Reconciliation | DealReferenceValidator, hourly reconciliation job | 2 | GAP-H4 fix. Important for data integrity but orphans won't appear in early prototype. |
| S12 | Export & Attach | Markdown export, attach transcript to deal | 2 | User value feature. Prototype can demonstrate brain; export is UX polish. |
| S12.4 | Living Deal Memo | Auto-generated downloadable deal memo from brain | 2 | Differentiating feature but requires mature brain content. |
| S13.4 | Predictive Budgeting | "Budget exhaustion in N days" forecasting | 2 | QW-8. Enhancement over base budget enforcement. |
| S13.6 | Bottleneck Heatmap | Pipeline stage temperature overlay | 2 | QW-9. Visual insight, requires pipeline data volume. |
| S15 | Proposal Hardening | Wire execute-proposal, status history, correct_brain_summary | 2 | GAP-M10 + GAP-L3 fixes. Proposals work in prototype via agent HITL; full pipeline is expansion. |
| QW-5 | @Agent Mentions in Notes | Invoke AI inline in deal notes | 2 | Nice integration but chat is the primary AI interface for prototype. |
| QW-7 | Smart Paste Entity Extraction | Auto-detect entities in pasted text | 2 | Improves data quality. Prototype can work with manual entity input via brain extraction. |
| QW-13 | Spaced Repetition | "Remember this?" fact review cards | 2 | Cognitive science feature. Valuable but prototype can show brain facts directly. |
| A-2 | HyDE Retrieval | Hypothetical document embeddings for better retrieval | 2 | Improves vague queries. Prototype with hybrid dense+sparse is sufficient. |
| B-1 | Reflexion Loop (in agent) | Self-critique in LangGraph pipeline | 2 | Same as S8.3 but in agent path. |
| B-5 | Active Drift Resolution Agent | Auto-resolve contradictions via evidence search | 2 | Enhancement over passive flagging. |
| B-6 | Devil's Advocate | Background counter-argument generation | 2 | Decision quality feature. Requires mature brain to be meaningful. |
| C-3 | Background Consolidation | Idle-time memory optimization | 2 | Performance optimization. |
| C-5 | Deal Precedent Network | Auto-find similar historical deals | 2 | Requires deal history. Novel but needs data. |
| D-3 | Chain-of-Verification | Separate factual claim verification pass | 2 | Subset of Reflexion. |
| D-4 | Typed SSE Schema | Discriminated union Pydantic models for SSE events | 2 | Type safety improvement. Prototype can use untyped JSON. |
| E-2 | Decision Fatigue Sentinel | Cognitive checkpoint after N high-stakes decisions | 2 | Cognitive safety net. Nice-to-have for prototype. |
| E-4 | Counterfactual Analysis | "What if" using replay infrastructure | 2 | Requires S6 (Replay). Category-defining but depends on mature infrastructure. |
| F-1 | Deal Stall Predictor | Survival model for stage stall probability | 2 | Requires historical stage duration data. |
| F-4 | Risk Cascade Predictor | Portfolio-level risk pattern scanning | 2 | Requires multiple active deals with populated brains. |
| G-1 | Comment Threads on Facts | Inline discussion on Deal Brain facts | 2 | Collaboration feature. Single-user prototype doesn't need it. |
| G-3 | Shared Workspace Presence | Live presence indicators (Figma-style) | 2 | Multi-user feature. Prototype is single-user. |
| H-1 | Morning Deal Briefing | Daily automated deal summary | 2 | High user value. Requires Deal Brain + events populated over time. |
| H-2 | Command Palette | Context-aware Cmd+K | 2 | Productivity enhancement. Not core to cognitive thesis. |
| H-3 | Anomaly-Driven Alerts | Learn deal cadence, alert on deviations | 2 | Requires baseline cadence data. |
| J-1 | Living Deal Memo | Auto-generated deal document | 2 | (Same as S12.4) |
| J-3 | Smart Paste | (Same as QW-7) | 2 | Listed above. |
| **PRODUCTION & ENTERPRISE** | | | | |
| S3.4 | SQLite User Migration | Migrate SQLite user/session to PostgreSQL | 3 | GAP-H5 fix. Simplifies GDPR but prototype can dual-write. |
| S3.3-OUT | Cross-DB Outbox | Outbox pattern for cross-DB writes | 3 | GAP-M4 fix. Prototype can do synchronous cross-DB writes; outbox is production reliability. |
| S5.5 | MemoryStatePanel UI | Debug panel showing memory tiers | 3 | Developer/debug tool. Not user-facing for prototype. |
| S6.3 | Compliance Encryption | AES-256-GCM for compliance-tier snapshots | 3 | GAP-M8 fix. Enterprise compliance requirement. |
| S6.5 | Counterfactual Engine | Full counterfactual replay API | 3 | Requires mature replay infrastructure. |
| S7.3-L5 | Semantic Firewall | BERT-based jailbreak classifier | 3 | Requires training data and model deployment. Rule-based is sufficient for prototype. |
| S9.6 | JIT Tool Access | Ephemeral one-time permissions | 3 | Enterprise RBAC extension. Static roles sufficient for prototype. |
| S10.2-JWT | JWT Authentication (Phase 2) | Full JWT with signature verification | 3 | X-User-Id header sufficient for prototype. JWT is multi-user production. |
| S10.4 | Deal Access Control (full) | Per-deal role-based access | 3 | Single-user prototype doesn't need per-deal RBAC. |
| S10.7 | Role-Based Redaction | Auto-redact sensitive entities for external sharing | 3 | Enterprise sharing feature. |
| S11.5 | GDPR Full Deletion | 20-table cascade across 2 databases + mem0 | 3 | Legal compliance for production. Prototype uses soft-delete. |
| S14.3 | PGlite Offline | WASM Postgres in browser for offline SQL | 3 | Advanced offline. localStorage cache sufficient for prototype. |
| S16-CS | Contract Surface Updates | Add all new endpoints to OpenAPI spec + sync pipeline | 3 | Required for CI/CD. Prototype can validate manually. |
| S17-M11 | Rollback Migrations | Rollback SQL scripts for all 3 migrations | 3 | GAP-M11 fix. Production safety. Prototype can re-create. |
| A-3 | RAPTOR Hierarchical Retrieval | Tree of summaries at multiple granularity levels | 3 | Significant infrastructure. Hybrid retrieval sufficient for prototype. |
| B-2 | Plan-and-Execute Decomposition | Multi-step query planning | 3 | Complex agent architecture. Single-step sufficient for prototype. |
| B-4 | Multi-Specialist Delegation | Route to specialist sub-graphs | 3 | Requires multiple specialized LangGraph sub-graphs. |
| C-6 | Relationship Intelligence | Broker dossier across all deals | 3 | Requires NER + entity linking + deal history. |
| GAP-L1 | MCP Tool Governance | Bring 12 MCP tools under COL cost/scope/audit | 3 | Integration task. MCP tools work independently for prototype. |
| GAP-M7 | Security Test Plan | Update 5 existing test files + new test coverage | 3 | Test infrastructure. Important but doesn't block prototype. |
| G-2 | @Agent in Notes (full) | Server-side agent invocation from deal notes | 3 | Requires note system integration. Quick Win version is Bucket 2. |
| H-4 | Ambient Intelligence Sidebar | Real-time context sidebar | 3 | Requires streaming UI + real-time data. |
| H-5 | Predictive Budgeting (full) | Budget exhaustion forecasting | 3 | (Base budget enforcement is Bucket 1; prediction is Bucket 2; full forecasting is Bucket 3) |
| I-2 | Semantic Firewall | (Same as S7.3-L5) | 3 | Listed above. |
| I-3 | Role-Based Redaction | (Same as S10.7) | 3 | Listed above. |
| I-4 | JIT Access | (Same as S9.6) | 3 | Listed above. |
| K-1 | PGlite Offline | (Same as S14.3) | 3 | Listed above. |
| K-2 | Sentiment Coach | Tone analysis and negotiation advice | 3 | Requires NLP sentiment model. |
| **MOONSHOTS** | | | | |
| MOON-1 | Deal Simulator 3000 | Monte Carlo simulation using Deal Brain facts | 3+ | Research project. Requires probabilistic modeling. |
| MOON-2 | Deal Auto-Pilot | Level 5 autonomous agent (schedules, drafts, sends) | 3+ | Requires robust agentic loop + error recovery. |
| MOON-3 | Federated Deal Learning | Global deal model via federated learning | 3+ | Requires multi-tenant + differential privacy. |
| MOON-4 | Voice-First Deal Room | "Siri for M&A" with audio processing | 3+ | Requires STT/TTS + hardware integration. |
| MOON-5 | Blockchain Audit Trail | Immutable ledger for decisions and facts | 3+ | Requires blockchain infrastructure. |

### Classification Summary

| Bucket | Count | Effort (est.) | Purpose |
|--------|-------|---------------|---------|
| **1: Prototype-Critical** | 31 components | ~10 weeks | Validates the cognitive operating layer thesis. Demonstrates: intelligent memory, evidence-grounded chat, ghost knowledge detection, deal health scoring, cost governance, security baseline. |
| **2: Functional Expansion** | 37 components | ~12 weeks | Builds the competitive moat. Adds: reflexion, export, morning briefing, anomaly detection, cross-deal intelligence, decision journal, predictive features. |
| **3: Production/Enterprise** | 27 components + 5 moonshots | ~8+ weeks | Production readiness. Adds: GDPR compliance, JWT auth, encryption, redaction, advanced offline, semantic firewall, enterprise RBAC. |

### Architectural Foundation Integrity Check

The following components are classified as Bucket 1 despite being "infrastructure" because downgrading them would compromise system survivability:

| Component | Why it cannot be deferred |
|-----------|--------------------------|
| Partition Automation (S3.3-PART) | Static partitions fail silently after month end. INSERTs start failing with no error handling. |
| User Identity Standardization (S3.2) | INTEGER vs VARCHAR mismatch causes runtime cast errors on any cross-table join. |
| Middleware Routing (S3.5-MW) | Without routing, all new chat endpoints return 404. Nothing works. |
| SSE Event Catalog (S3.10) | Without typed events, frontend randomly breaks on unknown event types. |
| Deal Brain (S4) | 14 of 18 cognitive features depend on it. Without brain, the product is "chat with RAG" — which already exists. |
| Summarization (S5) | Without summarization, conversations lose all context after 6 messages. The "knowledge accumulation" thesis fails. |
| Hybrid Retrieval (A-1) | Pure semantic search misses "Acme Corp $2.1M EBITDA" — the exact queries M&A users make. Evidence quality is the product. |

---

## 23. Appendices

### A. Files Modified Per Section (Updated for V2)

| Section | Files Created | Files Modified |
|---------|--------------|----------------|
| S3 | `chat_repository.py`, `migrate_chat_data.py`, `004_chat_canonical_store.sql`, `004_rollback.sql` | `chat_orchestrator.py`, `chat/route.ts`, `chat-history.ts`, `chatbot.py`, `middleware.ts` |
| S4 | `deal_brain_service.py`, `DealBrain.tsx`, `FactLineageExplorer.tsx`, `028_deal_brain.sql`, `028_rollback.sql` | `context_store.py`, `DealWorkspace.tsx`, `chat_evidence_builder.py` |
| S5 | `summarizer.py`, `MemoryStatePanel.tsx`, `memory_consolidation_worker.py` | `chat_orchestrator.py`, `chat/page.tsx` |
| S6 | `snapshot_writer.py`, `replay_service.py`, `counterfactual_service.py` | `chat_orchestrator.py`, `graph.py` |
| S7 | `injection_guard.py`, `session_tracker.py`, `canary_token_manager.py`, `semantic_firewall.py` | `chat_orchestrator.py`, `graph.py`, `chat_evidence_builder.py` |
| S8 | `reflexion_critique.py` | `chat_orchestrator.py`, `chat/page.tsx` |
| S9 | `scope_filter.py` | `graph.py`, `agent.py`, `deal_tools.py` |
| S10 | `login/page.tsx`, `auth_middleware.ts` | `middleware.ts`, `auth.py` |
| S11 | `chat_retention.py`, `deal_reference_validator.py`, `029_legal_hold.sql`, `029_rollback.sql` | `retention/cleanup.py`, `chat_repository.py` |
| S12 | `export_service.py`, `ExportButton.tsx`, `living_memo_generator.py` | `chatbot.py`, `ChatHistoryRail.tsx` |
| S13 | `cost_repository.py`, `CostTab.tsx`, `UsageSection.tsx`, `budget_predictor.py` | `chat_orchestrator.py`, `graph.py`, `settings/page.tsx` |
| S18 | `hybrid_retriever.py` | `rag_rest_api.py`, `chat_evidence_builder.py` |
| S19 | `plan_execute_graph.py`, `specialist_router.py` | `graph.py`, `llm.py` |
| S20 | `ghost_knowledge_detector.py`, `momentum_calculator.py`, `stall_predictor.py` | `deal_brain_service.py`, `dashboard/page.tsx` |
| S21 | `morning_briefing.py`, `anomaly_detector.py`, `command_palette_source.py` | `chat/page.tsx` |

### B. Current Tool Inventory (unchanged from V1)

| Tool | deal_id Required | HITL | Scope |
|------|-----------------|------|-------|
| `duckduckgo_results_json` | No | No | global, deal, document |
| `transition_deal` | Yes | **Yes** | deal |
| `get_deal` | Yes | No | deal, document |
| `list_deals` | No | No | global, deal |
| `search_deals` | No | No | global, deal |
| `create_deal` | No | **Yes** | deal |
| `add_note` | Yes | No | deal |
| `get_deal_health` | Yes | No | deal, document |

### C. Database Inventory (Updated for V2)

| Database | Schema | Tables (current) | New Tables (V2) |
|----------|--------|-------------------|-----------------|
| `zakops_agent` | `public` | checkpoints, checkpoint_blobs, checkpoint_writes, decision_ledger, approvals, tool_executions, audit_log, user, session | chat_threads, chat_messages, thread_ownership, session_summaries, turn_snapshots, cost_ledger, deal_budgets, cross_db_outbox, user_identity_map |
| `zakops` | `zakops` | deals, actions, artifacts, deal_events, quarantine, outbox, idempotency_keys, user_preferences, agent_context_summaries, agent_context, agent_deal_metadata | deal_brain, deal_brain_history, deal_entity_graph, decision_outcomes, deal_access |

### D. Test Plan [V2: GAP-M7 fix]

| Test Category | Files | Coverage |
|---------------|-------|----------|
| Chat Repository CRUD | `test_chat_repository.py` | Create/read/update/delete threads and messages; ownership enforcement |
| Deal Brain Extraction | `test_deal_brain_extraction.py` | Fact extraction, contradiction detection, ghost knowledge |
| Injection Guard | `test_injection_guard.py` | All 15 patterns, severity levels, sanitization, canary tokens |
| Citation Audit | `test_citation_audit.py` | Strong/weak/orphan citations, semantic similarity thresholds |
| Tool Scoping | `test_tool_scoping.py` | Scope × role matrix, tool filtering, post-condition assertions |
| Cost Ledger | `test_cost_ledger.py` | Write, read, budget enforcement, predictive budgeting |
| Cascading Delete | `test_cascading_delete.py` | Create thread → populate all tables → hard delete → verify zero rows |
| Cross-DB Reconciliation | `test_deal_reference.py` | Orphan detection, validation, reconciliation |
| GDPR Deletion | `test_gdpr_deletion.py` | Full user cascade, anonymization verification |
| Replay | `test_replay.py` | Snapshot capture, replay, comparison, compliance tier |
| Migration | `test_migration.py` | Forward migration, rollback, idempotency |

### E. Glossary (Updated for V2)

| Term | Definition |
|------|-----------|
| **COL** | Cognitive Operating Layer — the target architecture where chat becomes a knowledge accumulation and execution system |
| **Deal Brain** | Per-deal persistent knowledge store that accumulates facts, risks, decisions, and summaries across chat sessions |
| **Turn** | One user message + one assistant response = one turn |
| **Thread** | A chat session (sequence of turns) with a scope (global, deal, document) |
| **Proposal** | A structured action suggested by the LLM that requires human approval before execution |
| **HITL** | Human-in-the-loop — approval gate for high-impact tool calls |
| **Rolling Summary** | Incrementally updated summary of a conversation, generated every 5 turns |
| **Turn Snapshot** | Complete capture of model input/output for a single turn, enabling deterministic replay |
| **Scope** | The context in which a chat operates: global (no deal), deal (specific deal), document (specific document) |
| **[V2] Ghost Knowledge** | Facts that exist in a user's head but NOT in the Deal Brain — detected when users reference unrecorded information |
| **[V2] Momentum Score** | Composite 0-100 metric measuring deal health based on velocity, events, completions, risk, and action rate |
| **[V2] Tiered Memory** | MemGPT-inspired architecture: Working (in-context), Recall (searched brain/summaries), Archival (full history) |
| **[V2] Forgetting Curve** | Ebbinghaus-inspired confidence decay applied to Deal Brain facts not reinforced in recent conversations |
| **[V2] Canary Token** | Invisible marker injected into sensitive RAG chunks; if it appears in LLM output, data leakage is detected |
| **[V2] Outbox Pattern** | Asynchronous cross-database write: operation queued in source DB, processed by worker, written to target DB |
| **[V2] Counterfactual** | "What if" analysis using replay infrastructure — modify historical inputs and observe divergent outcomes |

---

### F. Canonical Cascade Table Map [V2.1]

Every table referenced in delete/retention logic, with full metadata. **No "paper cascades" — every row below is enforceable in the listed database.**

#### zakops_agent Database (PostgreSQL)

| Table | Exists Today? | New in COL? | Source of Truth For | Thread Delete Cascade | User Delete Cascade | FK Enforced? |
|-------|--------------|-------------|--------------------|--------------------|--------------------|----|
| `chat_threads` | No | **Yes** | Threads | **TARGET** (row deleted) | `DELETE WHERE user_id=$1` | PK |
| `chat_messages` | No | **Yes** | Messages | `ON DELETE CASCADE` from chat_threads FK | `DELETE WHERE user_id=$1` (via thread) | FK → chat_threads |
| `thread_ownership` | No | **Yes** | Access control | `ON DELETE CASCADE` from chat_threads FK [V2.1] | `DELETE WHERE user_id=$1` | FK → chat_threads [V2.1] |
| `session_summaries` | No | **Yes** | Summaries | `ON DELETE CASCADE` from chat_threads FK | Via thread cascade | FK → chat_threads |
| `turn_snapshots` | No | **Yes** | Replay data | `ON DELETE CASCADE` from chat_threads FK | `DELETE WHERE user_id=$1` | FK → chat_threads |
| `cost_ledger` | No | **Yes** | Cost records | `ON DELETE SET NULL` (thread_id nulled) | `DELETE WHERE user_id=$1` | FK → chat_threads (SET NULL) |
| `deal_budgets` | No | **Yes** | Budget config | Not thread-linked (deal-level) | Not user-linked | **No FK** (cross-DB, app-validated) |
| `cross_db_outbox` | No | **Yes** | Async queue | `DELETE WHERE payload->>'thread_id'=$1` | `DELETE WHERE payload->>'user_id'=$1` | No FK (JSONB payload) |
| `user_identity_map` | No | **Yes** | User identity | Not thread-linked | `DELETE WHERE canonical_id=$1` | PK |
| `checkpoints` | **Yes** | No | LangGraph state | `DELETE WHERE thread_id=$1` | Via thread list | No FK (LangGraph standard) |
| `checkpoint_blobs` | **Yes** | No | LangGraph state | `DELETE WHERE thread_id=$1` | Via thread list | No FK (LangGraph standard) |
| `checkpoint_writes` | **Yes** | No | LangGraph state | `DELETE WHERE thread_id=$1` | Via thread list | No FK (LangGraph standard) |
| `decision_ledger` | **Yes** | No | Audit trail | **ANONYMIZE** (not delete) | **ANONYMIZE** (user_id='DELETED') | No FK to chat_threads |
| `approvals` | **Yes** | No | Approval records | Not thread-linked | `DELETE WHERE actor_id=$1` | No FK to chat_threads |
| `tool_executions` | **Yes** | No | Execution records | Not thread-linked | Via approval cascade | FK → approvals |
| `audit_log` | **Yes** | No | Audit trail | Not thread-linked | **ANONYMIZE** (actor_id='DELETED') | No FK |
| `user` | **Yes** (SQLite) | Migrating | User records | Not thread-linked | `DELETE WHERE id=$1` (deprecated) | SQLite FK |
| `session` | **Yes** (SQLite) | Migrating | Session records | Not thread-linked | CASCADE from user | SQLite FK |

#### zakops Database (PostgreSQL, schema: zakops)

| Table | Exists Today? | New in COL? | Source of Truth For | Deal Delete Cascade | User Delete Cascade | FK Enforced? |
|-------|--------------|-------------|--------------------|--------------------|--------------------|----|
| `deal_brain` | No | **Yes** | Deal intelligence | `ON DELETE CASCADE` from deals FK | Not user-linked | FK → deals |
| `deal_brain_history` | No | **Yes** | Brain audit trail | FK → deals (cascade) | **ANONYMIZE** (triggered_by='DELETED') | FK → deals |
| `deal_entity_graph` | No | **Yes** | Entity links | FK → deals (cascade) | Not user-linked | FK → deals |
| `decision_outcomes` | No | **Yes** | Outcome tracking | FK → deals (cascade) | `DELETE WHERE recorded_by=$1` | FK → deals |
| `deal_access` | No | **Yes** | Access control | `ON DELETE CASCADE` from deals FK | `DELETE WHERE user_id=$1` | FK → deals |
| `deals` | **Yes** | No | Deal records | **TARGET** | Not user-linked | PK |
| `user_preferences` | **Yes** | No | User settings | Not deal-linked | `DELETE WHERE user_id=$1` | No FK |

#### External Stores

| Store | Delete Mechanism | Enforcement |
|-------|-----------------|-------------|
| mem0 (memory service) | `forget_user_memory(user_id)` via `graph.py:314-357` | Application code — no FK |
| localStorage (browser) | Client-side removal on next thread list sync | Best-effort — no server enforcement |
| SQLite (legacy) | Direct DELETE after migration complete; file deletion post-deprecation | Application code |

**Enforcement invariant**: The S11.2 hard delete sequence and S11.5 GDPR cascade MUST reference every row in this table. Any table added to the system MUST be added here with its cascade path defined.

---

### Gap Resolution Tracker

All 23 gaps from the Innovation Master, with resolution status:

| Gap ID | Severity | Description | Resolution | Section |
|--------|----------|-------------|------------|---------|
| GAP-C1 | CRITICAL | deal_budgets FK references non-unique column | Removed FK, standalone PK, application-level validation | S13.3 |
| GAP-C2 | CRITICAL | user_id type mismatch across systems | Standardized VARCHAR(255) everywhere + user_identity_map | S3.2 |
| GAP-C3 | CRITICAL | No partition automation, static partitions | pg_partman + DEFAULT partition + create_monthly_partitions() + pg_cron | S3.3, S6.2 |
| GAP-H1 | HIGH | Middleware missing chatbot routes | Added routing for /api/v1/chatbot/* to Agent API | S3.5 |
| GAP-H2 | HIGH | Service token returns user_id=0 | Phased approach: Phase 1 X-User-Id header, Phase 2 JWT | S10.2 |
| GAP-H3 | HIGH | Deal Brain endpoints missing from contract surface | Added Contract Surface Updates table with 15 new endpoints | S16 |
| GAP-H4 | HIGH | Cross-database deal_id no referential integrity | DealReferenceValidator + hourly reconciliation + deletion webhook | S11.3 |
| GAP-H5 | HIGH | SQLite user store not migrated to PostgreSQL | user_identity_map table + migration in migrate_chat_data.py | S3.3, S3.7 |
| GAP-M1 | MEDIUM | Redundant deal_id in chat_messages | Removed — derivable from thread.deal_id via JOIN | S3.3 |
| GAP-M2 | MEDIUM | Missing UNIQUE on (thread_id, turn_number) | Added explicit UNIQUE constraint | S3.3 |
| GAP-M3 | MEDIUM | Migration number tracking not addressed | Added INSERT INTO schema_migrations in both migrations | S3.3, S4.2 |
| GAP-M4 | MEDIUM | Write path spans two DBs without distributed transaction | cross_db_outbox table + OutboxWorker for async brain extraction | S3.3, S3.8 |
| GAP-M5 | MEDIUM | Historical backfill into partitioned tables | Backfill threads/messages only; DEFAULT partition catches old dates; skip snapshots | S3.7 |
| GAP-M6 | MEDIUM | PII redaction not integrated with injection guard | Defined full input-to-output security pipeline | S7.2 |
| GAP-M7 | MEDIUM | Existing security tests not updated | Added Test Plan appendix with 11 test categories | S23.D |
| GAP-M8 | MEDIUM | Compliance encryption not fully designed | Full blob encryption spec: HKDF key derivation, quarterly rotation, cleartext indexes | S6.3 |
| GAP-M9 | MEDIUM | Email ingestion integration missing | Email → DealBrain extraction pipeline with source_type: "email" | S4.6 |
| GAP-M10 | MEDIUM | correct_brain_summary proposal type underspecified | Handler defined: snapshot → history → regenerate summary → update | S15.4 |
| GAP-M11 | MEDIUM | No rollback migrations defined | Rollback scripts for all 3 migrations | S3.3, S4.2, S16 |
| GAP-M12 | MEDIUM | Materialized view refresh not scheduled | Changed to regular VIEW (no refresh needed) | S3.3 |
| GAP-L1 | LOW | MCP server tools not in COL governance | MCP tool governance table with priority classification | S19.6 |
| GAP-L2 | LOW | SSE event types not cataloged | 14 typed events cataloged with payloads | S3.10 |
| GAP-L3 | LOW | Proposal status JSONB lacks concurrency control | Optimistic locking with FOR UPDATE on proposal status changes | S15.3 |

---

*End of COL-DESIGN-SPEC-V2. Total new tables: 14 (was 10). Total new files: ~35 (was ~20). Total modified files: ~30 (was ~25). Gaps resolved: 23/23. Improvements integrated: 45/45. Quick Wins merged: 13/13. Estimated effort: 24 weeks (P0-P3), with P4 ongoing.*
