AGENT IDENTITY
- agent_name: Codex
- run_id: 20260204-1651-0e51
- date_time: 2026-02-04T16:58:52+00:00
- repo_revision: 559a5d1f5c6d22adfd90fd767191dcd421f8732a
- dashboard_zod_errors_checked: true

# DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN — Codex 20260204-1651-0e51

## Executive Summary (Brutal + Evidence-Based)
- QA_VERIFICATION_006 reports PASS with minor deferrals, but code evidence shows multiple soft-pass conditions that are **not production-grade**, especially around contract integrity, SSE, legacy references, and idempotency. Evidence: SSE endpoints return 501 in both backend and dashboard (`/home/zaks/zakops-backend/src/api/orchestration/routers/events.py:56-75`, `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/route.ts:13-17`) while frontend SSE consumer assumes a working stream (`/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/use-realtime-events.ts:240-305`).
- Five-layer contract integrity is still broken: generated TS types and Zod schemas diverge from Pydantic models (e.g., `DealResponse.email_thread_ids` exists in TS types but not in backend model), and response validation can silently drop data (`getDeals` returns `[]` on validation failure). Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/src/types/api.ts:66-83`, `/home/zaks/zakops-agent-api/apps/dashboard/src/types/api/generated.ts:59-76`, `/home/zaks/zakops-backend/src/api/orchestration/main.py:154-166`, `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:420-425`.
- Split-brain risk is **not fully eliminated**: a SQLite/JSON fallback database adapter still exists and defaults to SQLite if envs are missing, and legacy registry paths remain in production code. Evidence: `/home/zaks/zakops-backend/src/core/database/adapter.py:54-80`, `/home/zaks/zakops-backend/src/core/chat_evidence_builder.py:261-266`, `/home/zaks/zakops-backend/src/actions/engine/store.py:26-28`.
- Pre-gate (R2-0) baseline finds **no browser verification** done by QA (Layer 4–5), which historically caused “PASS while UI is broken.” This remains unaddressed and must be treated as blocking for any “hard PASS.” Evidence requirement stated in `/home/zaks/zakops-agent-api/docs/CONSTRAINTS.md:29-41`.

## Pre-Gate Comment (R2-0 Baseline)
The system has **not** been verified across Layer 4–5 in a real browser in QA_VERIFICATION_006. This is a known historic failure mode and must be treated as a blocking gap until resolved. The new Round-2 plan explicitly adds browser-based validation and Zod-vs-Pydantic contract diffing as hard gates. Evidence requirement: `/home/zaks/zakops-agent-api/docs/CONSTRAINTS.md:29-41`.

## Inputs Read (Ground Truth)
- V2 Issues Register: `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_HONEST_ASSESSMENT_V2.md`
- V3 Plans + Index: `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3.md`, `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.md`, `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_EVAL_V3.md`
- QA Baseline: `/home/zaks/bookkeeping/qa/QA-VERIFICATION-006/QA_VERIFICATION_006_REPORT.md` (primary), `/home/zaks/bookkeeping/qa/QA-VERIFICATION-006-ENHANCED/QA_VERIFICATION_006_REPORT.md` (secondary)
- Codebase: `/home/zaks/zakops-backend/`, `/home/zaks/zakops-agent-api/`

---

## Q1 — Soft PASS Items (PASS in QA, but NOT production-grade)
Each item: QA claim → evidence contradiction → hard-pass definition.

1) **ZK-ISSUE-0020 (SSE)**
- QA claim: PASS (“SSE code exists”).
- Evidence: SSE endpoints explicitly return 501 in backend and dashboard, so browser SSE is non-functional. Files: `/home/zaks/zakops-backend/src/api/orchestration/routers/events.py:56-75`, `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/route.ts:13-17`. Frontend expects SSE stream parsing (`/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/use-realtime-events.ts:240-305`).
- Hard PASS: `/api/events/stream` returns SSE with valid framing, dashboard connects successfully, no console errors, reconnection works.

2) **ZK-ISSUE-0018 (Zod Schema Drift)**
- QA claim: PASS via `.passthrough()` / `.safeParse()` usage.
- Evidence: Generated TS `DealResponse` includes `email_thread_ids` (not in backend Pydantic), `DealEvent.id` typed as number (backend uses UUID). Files: `/home/zaks/zakops-agent-api/apps/dashboard/src/types/api/generated.ts:49-76` vs `/home/zaks/zakops-backend/src/api/orchestration/main.py:154-166` and `/home/zaks/zakops-backend/src/api/orchestration/main.py:256-264`. Also `getDeals` returns `[]` on schema failure, silently hiding data (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:420-425`).
- Hard PASS: Single OpenAPI source → generated TS client + Zod schema alignment; no `.passthrough()` except explicitly documented; any mismatch fails CI.

3) **ZK-ISSUE-0016 (Duplicate Detection)**
- QA claim: PASS via DB unique constraint.
- Evidence: QA accepts 500 on duplicate create. That is a crash, not idempotent behavior. No Idempotency-Key enforced on create_deal tool or backend create endpoint. Backend create is plain insert (`/home/zaks/zakops-backend/src/api/orchestration/main.py:551-589`), agent tool does not set idempotency (`/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py:487-493`).
- Hard PASS: `Idempotency-Key` supported across write endpoints; duplicate returns 200 (same response) or 409 with structured JSON, never 500.

4) **ZK-ISSUE-0011 (Correlation ID Propagation)**
- QA claim: PASS (infra exists).
- Evidence: Dashboard `api-client.ts` fetches directly to backend without adding `X-Correlation-ID` or API key (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts:43-69`). Middleware only injects correlation for `/api/*` route paths (`/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts:28-83`). Direct fetches bypass this.
- Hard PASS: All client requests go through a single fetch wrapper that injects correlation IDs; correlation IDs present in DB events + logs for every request.

5) **ZK-ISSUE-0001 (Split-Brain Eliminated)**
- QA claim: PASS (“JSON deleted”).
- Evidence: Production code still reads legacy JSON and SQLite by default if env missing. Examples: default SQLite backend (`/home/zaks/zakops-backend/src/core/database/adapter.py:54-80`), registry path in EvidenceBuilder (`/home/zaks/zakops-backend/src/core/chat_evidence_builder.py:261-266`), SQLite action store (`/home/zaks/zakops-backend/src/actions/engine/store.py:26-28`).
- Hard PASS: Legacy JSON/SQLite references removed or isolated to explicit, off-by-default tooling; CI guardrails prevent reintroduction.

6) **ZK-ISSUE-0007 (Stage Taxonomy Unified)**
- QA claim: PASS (DB default inbound).
- Evidence: base schema still defaults to `lead` (`/home/zaks/zakops-backend/db/init/001_base_tables.sql:35-36`), and a migration enforces canonical stages (`/home/zaks/zakops-backend/db/migrations/023_stage_check_constraint.sql:5-7`). That combination can fail on fresh DBs if migrations are missed or run out-of-order.
- Hard PASS: DB default set to inbound at schema level + migration ensures existing rows; verification query proves actual default.

7) **ZK-ISSUE-0013 (Actions Capabilities/Metrics)**
- QA claim: PASS (200 endpoints).
- Evidence: `/api/actions/capabilities` and `/metrics` are defined twice: 501 in main (`/home/zaks/zakops-backend/src/api/orchestration/main.py:921-941`) and 200 in router (`/home/zaks/zakops-backend/src/api/orchestration/routers/actions.py:15-164`). Runtime precedence is ambiguous; contract risk remains.
- Hard PASS: single definitive route implementation; integration tests assert 200 with correct schema.

---

## Q2 — Unverified or Deferred Items (Must Close)
From QA_VERIFICATION_006 + unexecuted work:

- **ZK-ISSUE-0010 (RAG columns)** deferred. Codebase lacks `last_indexed_at`, `content_hash` in deals table. Must implement and backfill. Evidence: no columns in `/home/zaks/zakops-backend/db/init/001_base_tables.sql`.
- **ZK-ISSUE-0011 (Correlation population)** was marked “infra exists.” Must verify actual logs contain trace_id across services and DB events. Evidence: middleware adds correlation only for /api/ paths; direct API client bypass (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts:43-69`).
- **Legacy file references** remain (JSON/SQLite, 8090, `/home/zaks/scripts`). Evidence: `/home/zaks/zakops-agent-api/apps/dashboard/Makefile:11-103`, `/home/zaks/zakops-backend/src/core/chat_evidence_builder.py:261-266`, `/home/zaks/zakops-backend/src/actions/engine/store.py:26-28`.
- **CONTRACT-AUDIT-V1 & QA-CA-V1** never executed. Known ZodErrors remain possible; `api-schemas.ts` (strict schemas) is not imported anywhere (`rg` shows no imports). Evidence: file present `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-schemas.ts`, zero imports.

---

## Q3 — Hidden Failure Modes Likely Still Present
- **Phantom success across tools**: backend endpoints return 200 but data isn’t visible in UI because client silently returns empty arrays on schema mismatch (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:420-425`).
- **Schema drift recurrence**: multiple schema sources (Pydantic, Zod, TS types) with no generation pipeline or CI gate. Evidence: `types/api.ts` vs backend models diverge (`/home/zaks/zakops-agent-api/apps/dashboard/src/types/api.ts:66-83`, `/home/zaks/zakops-backend/src/api/orchestration/main.py:154-166`).
- **Race conditions**: no explicit DB-level locking or transition ledger; stage transitions validated in code but not enforced at DB except check constraint (`/home/zaks/zakops-backend/src/core/deals/workflow.py:35-46`, `/home/zaks/zakops-backend/db/migrations/023_stage_check_constraint.sql:5-7`).
- **Silent degradation**: outbox infrastructure exists but health endpoint notes processor never processed actions (`/home/zaks/zakops-backend/src/api/shared/routers/health.py:77-83`).
- **Legacy drift**: multiple 8090 references remain in Makefile + docs, undermining decommission guardrails (`/home/zaks/zakops-agent-api/apps/dashboard/Makefile:11-103`).

---

## Q4 — What We Should Redesign (Contrarian)
- **Generated client over manual schemas**: Stop hand-maintaining Zod schemas. Generate TS client & Zod schemas from OpenAPI with CI enforcement.
- **Event-sourced transition ledger**: Stage changes should be append-only (`deal_transitions` table) with strict validation and idempotency.
- **Outbox-based side effects only**: no fire-and-forget HTTP calls in app code.
- **Single API entry**: Remove ambiguity by consolidating routes (capabilities/metrics) into one router.
- **Browser-first verification**: QA must include UI runtime checks and Zod console validation.

---

## Q5 — Best-in-Class Platform Should Do Differently (2025–2026)
- **OpenTelemetry end-to-end** for tracing across browser → backend → agent → DB.
- **Idempotency on all write endpoints**.
- **Generated SDKs** (OpenAPI → TS client, Zod) + contract CI gate.
- **Durable agent execution** with LangGraph PostgresSaver + explicit tool audits.
- **Transactional outbox** + inbox deduplication for side effects.

---

## Rating Scorecard (0–10)
Each layer includes current score, target score, delta, proof plan.

1) **Bounded Contexts / Architecture Clarity** — Current 5 | Target 9
   - Gap: Docs show backend under `/apps/backend` but repo has no backend app (`/home/zaks/zakops-agent-api/docs/ARCHITECTURE.md:138-166`, `/home/zaks/zakops-agent-api/apps/` only has `agent-api` + `dashboard`).
   - Proof: update docs, run onboarding test with new engineer.

2) **Data Integrity + SOT** — Current 5 | Target 9
   - Gap: SQLite/JSON adapters still present; DB adapter defaults to SQLite (`/home/zaks/zakops-backend/src/core/database/adapter.py:54-80`).
   - Proof: grep for sqlite/json registry, remove or isolate; enforce DB backend via env + CI guardrail.

3) **Contract Correctness** — Current 3 | Target 9
   - Gap: mismatches in TS types vs Pydantic; no CI contract gate.
   - Proof: generate client + Zod from OpenAPI and enforce in CI; run CONTRACT-AUDIT-V1.

4) **Agent Tool Boundaries + HITL** — Current 6 | Target 9
   - Gap: tool create_deal/add_note lacks idempotency; approval audit ledger incomplete.
   - Proof: add Idempotency-Key + tool_exec log with trace_id.

5) **Observability & Debuggability** — Current 5 | Target 9
   - Gap: correlation exists only in some paths; no OTel, no browser trace propagation.
   - Proof: OTel spans + trace_id across all services + log sampling.

6) **Security/Auth Correctness** — Current 6 | Target 9
   - Gap: direct client fetch bypasses API key injection for writes (`/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts:43-69`).
   - Proof: unify client path; enforce auth at API boundary; structured JSON errors.

7) **End-to-End UX Correctness** — Current 4 | Target 9
   - Gap: silent empty lists on schema failure; SSE 501.
   - Proof: browser tests + Zod safeParse handling with user-visible errors.

8) **Email Ingestion Quality** — Current 5 | Target 9
   - Gap: legacy paths and sys.path fallback; env var not set in docker compose.
   - Proof: set `ZAKOPS_SCRIPTS_PATH` in compose and remove legacy defaults.

9) **Knowledge/RAG Integrity** — Current 4 | Target 9
   - Gap: missing `last_indexed_at`, `content_hash`; no freshness guarantee.
   - Proof: add columns + index update pipeline; add RAG audits.

10) **Operational Excellence** — Current 5 | Target 9
   - Gap: build ignores TS/lint errors (`/home/zaks/zakops-agent-api/apps/dashboard/next.config.ts:5-13`), legacy 8090 references remain.
   - Proof: CI gates for contract tests, forbidden patterns, and browser smoke tests.

---

## Contrarian Upgrade Register (ZK-UPG-0001+)
Required themes UPG-A..J are included.

**ZK-UPG-0001 (UPG-A) — Generated TypeScript Client from OpenAPI**
- Why: eliminate manual schema drift.
- Layers: 3,7,10
- Current: manual `types/api.ts`, `api.ts` Zod.
- Target: generated client + Zod from OpenAPI; CI regeneration required.
- Verification: contract CI gate fails on mismatch.
- Priority: P0 | Effort: M | Risk: Medium | Rollback: revert to previous client with pinned commit.

**ZK-UPG-0002 (UPG-B) — Transactional Outbox**
- Why: reliable side effects.
- Layers: 4,5,10
- Current: outbox exists but noted as never processed (`/home/zaks/zakops-backend/src/api/shared/routers/health.py:77-83`).
- Target: outbox used on all domain writes, relay worker tested.
- Verification: chaos test with relay restart.
- Priority: P1 | Effort: M | Risk: Medium

**ZK-UPG-0003 (UPG-C) — Idempotency Layer**
- Why: eliminate 500s on duplicates and race conditions.
- Layers: 2,4,6
- Current: idempotency only in workflow transitions; create_deal lacks idempotency.
- Target: Idempotency-Key required for write endpoints.
- Verification: duplicate POST returns same response.
- Priority: P0 | Effort: M | Risk: Low

**ZK-UPG-0004 (UPG-D) — Deal Transition Ledger**
- Why: auditable, deterministic lifecycle.
- Layers: 2,4,7
- Current: workflow engine validates transitions but no ledger table.
- Target: `deal_transitions` append-only; UI timeline.
- Verification: invalid transition yields 422; ledger row created.
- Priority: P1 | Effort: M

**ZK-UPG-0005 (UPG-E) — OpenTelemetry Integration**
- Why: real tracing across layers.
- Layers: 5,10
- Current: correlation ID middleware only.
- Target: OTel spans across services, SSE propagation.
- Verification: trace visible in Jaeger/Zipkin.
- Priority: P2 | Effort: L

**ZK-UPG-0006 (UPG-F) — Contract Testing CI Gate**
- Why: stop ZodError class of bugs.
- Layers: 3,7,10
- Current: no CI contract check.
- Target: nightly/PR gate validates responses vs OpenAPI + Zod.
- Verification: CI fails on mismatch.
- Priority: P0 | Effort: M

**ZK-UPG-0007 (UPG-G) — Circuit Breakers on External Dependencies**
- Why: prevent cascading failure (RAG, LangSmith, email).
- Layers: 5,8,9
- Current: no breakers.
- Target: breaker + retry + fallback in outbox.
- Verification: simulated outage, system degrades gracefully.
- Priority: P2 | Effort: M

**ZK-UPG-0008 (UPG-H) — Schema Migration Safety**
- Why: avoid drift and irreversible DB changes.
- Layers: 2,10
- Current: migrations exist but no enforced down path.
- Target: expand/contract strategy + CI migration test.
- Verification: migration rollback succeeds in CI.
- Priority: P2 | Effort: M

**ZK-UPG-0009 (UPG-I) — Agent Evaluation Framework**
- Why: prevent regressions in agent tool selection.
- Layers: 4,7
- Current: no golden eval suite.
- Target: scenario-based eval with expected tool calls.
- Verification: >=18/20 scenarios pass.
- Priority: P2 | Effort: M

**ZK-UPG-0010 (UPG-J) — Safe Decommissioning Guardrails**
- Why: prevent legacy resurrection.
- Layers: 2,10
- Current: 8090 references remain (`/home/zaks/zakops-agent-api/apps/dashboard/Makefile:11-103`).
- Target: CI lint forbids legacy patterns; changelog record only.
- Verification: rg gate fails if legacy patterns appear.
- Priority: P1 | Effort: S

---

## Round-2 Execution Plan (Phased)
Each phase includes objectives, tasks, dependencies, gates, acceptance criteria, and evidence.

### Phase R2-0 — Baseline Snapshot (BLOCKING)
- Objective: Collect 5-layer truth + browser evidence.
- Tasks: dump OpenAPI; diff Pydantic vs Zod; open dashboard and capture console errors; list DB columns; verify 8090 refs; confirm env vars.
- Dependencies: services running.
- Gate: evidence pack contains all 5-layer artifacts.

### Phase R2-1 — ZodError Eradication (P0)
- Objective: zero ZodErrors in browser.
- Tasks: run CONTRACT-AUDIT-V1; replace any `.parse()` at API boundaries with `safeParse` + fallback UI; align schemas to actual backend; remove unused `api-schemas.ts` or integrate.
- Gate: dashboard console = zero ZodErrors.

### Phase R2-2 — Idempotency + Error Semantics (P0)
- Objective: no 500s for expected conflicts.
- Tasks: add Idempotency-Key support in backend; store idempotency responses; update agent tools to include keys.
- Gate: duplicate POST returns original response or 409.

### Phase R2-3 — Deferred Item Closure (P1)
- Objective: close QA deferrals.
- Tasks: add `last_indexed_at` + `content_hash`; verify correlation IDs in real logs; set `ZAKOPS_SCRIPTS_PATH` in compose.
- Gate: DB query shows columns; log sample includes trace_id.

### Phase R2-4 — Transactional Outbox + Event Model (P1)
- Objective: side-effects reliable and auditable.
- Tasks: use outbox on deal mutations; verify worker processes events.
- Gate: outbox processed in <=5s; no dropped events.

### Phase R2-5 — State Machine + Transition Ledger (P1)
- Objective: formal transitions + ledger.
- Tasks: add `deal_transitions` table; enforce 422 on invalid transitions; UI timeline.
- Gate: invalid transition returns 422; ledger row exists.

### Phase R2-6 — Observability Hardening (P2)
- Objective: trace_id across browser→DB.
- Tasks: OTel instrumentation; propagate trace IDs to SSE events; structured logs.
- Gate: trace shown in collector.

### Phase R2-7 — Contract Testing + CI Gates (P2)
- Objective: prevent drift.
- Tasks: generate TS client from OpenAPI; add CI contract tests; add forbidden pattern gate.
- Gate: CI fails on any mismatch.

### Phase R2-8 — Agent Evaluation + Adversarial QA (P2)
- Objective: agent correctness + tool safety.
- Tasks: create golden dataset; run adversarial tests.
- Gate: >=18/20 pass.

### Phase R2-9 — Regression Proofing (P2)
- Objective: permanent protection for 22 ZK issues.
- Tasks: add regression tests for each ZK-ISSUE; confirm CI fails on regressions.
- Gate: revert any fix → CI fails.

---

## Adversarial Verification Scenarios (Required)
ADV-01..ADV-10 as specified; must be implemented in QA plan with expected outcomes.

---

## Evidence Index (Key Paths)
- Backend SSE 501: `/home/zaks/zakops-backend/src/api/orchestration/routers/events.py:56-75`
- Dashboard SSE 501: `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/events/route.ts:13-17`
- SSE consumer: `/home/zaks/zakops-agent-api/apps/dashboard/src/hooks/use-realtime-events.ts:240-305`
- Deal schema defaults: `/home/zaks/zakops-backend/db/init/001_base_tables.sql:35-36`
- Stage constraint: `/home/zaks/zakops-backend/db/migrations/023_stage_check_constraint.sql:5-7`
- Zod safeParse empty array: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts:420-425`
- Direct fetch bypass: `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-client.ts:43-69`
- Correlation middleware: `/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts:28-83`
- Legacy registry paths: `/home/zaks/zakops-backend/src/core/chat_evidence_builder.py:261-266`
- SQLite action store: `/home/zaks/zakops-backend/src/actions/engine/store.py:26-28`
- 8090 references (legacy): `/home/zaks/zakops-agent-api/apps/dashboard/Makefile:11-103`

---

## Known Unexecuted Work Incorporated
- CONTRACT-AUDIT-V1 (ZodError eradication)
- QA-CA-V1 (65-test contract verification)

---

## Final Self-Audit
- [x] Every claim includes evidence or is explicitly marked NEEDS VERIFICATION
- [x] Soft PASS items identified with hard-pass criteria
- [x] Scorecard includes all 10 layers
- [x] Contrarian upgrades include required UPG-A..J
- [x] Execution plan includes Phases R2-0..R2-9 and ADV-01..ADV-10
