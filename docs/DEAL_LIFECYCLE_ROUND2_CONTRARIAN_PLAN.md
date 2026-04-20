# DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN — Run Index

This file tracks all Round-2 Contrarian audit runs across agents.

---

## Run Index

### Run: opus.run001

**Agent**: opus (Claude Opus 4.5)
**Run ID**: run001
**Timestamp**: 2026-02-04T16:30:00Z
**Repo Revision**: 3173c36f714f13524f3d81375483484887a6ac99

**Files**:
- Report: `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN.opus.run001.md`
- JSON: `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN.opus.run001.json`

**Verdict**: LAYER 4-5 CONTRACT DRIFT DETECTED (Score: 30/50, 60%)

#### Top 10 Next Actions

1. Fix ActionStatus enum — align RUNNING vs PROCESSING
2. Trim ActionSchema from 28 to 15 fields (or expand backend)
3. Trim QuarantineItemSchema — remove 11 phantom fields
4. Replace `return []` with toast/error on safeParse failure
5. Add ActionSource values 'agent' and 'api' to backend
6. Remove .passthrough() from all Zod schemas after alignment
7. Add unique constraint on deals.canonical_name
8. Remove sys.path hack from diligence_request_docs.py
9. Run browser console capture to detect live ZodErrors
10. Create contract-sync CI check (Zod vs Pydantic field count)

#### Top 10 Contrarian Upgrades

1. **ZK-UPG-0001** (P0): ActionStatus enum is silently breaking status display
2. **ZK-UPG-0002** (P1): 13 fields in ActionSchema never arrive from backend
3. **ZK-UPG-0003** (P1): QuarantineItemSchema expects data that doesn't exist
4. **ZK-UPG-0004** (P1): Users see empty lists when validation fails silently
5. **ZK-UPG-0005** (P2): ActionSource enum is incomplete in backend
6. **ZK-UPG-0006** (P2): .passthrough() is a crutch hiding real contract drift
7. **ZK-UPG-0007** (P2): Duplicate canonical_names can still be created
8. **ZK-UPG-0008** (P3): sys.path manipulation is fragile import pattern
9. **INSIGHT**: Layers 4-5 were never tested in previous QA rounds
10. **INSIGHT**: CONTRACT-AUDIT-V1 and QA-CA-V1 were never executed

#### What We Would Do Differently From Day One

- Generate Zod schemas FROM Pydantic models (single source of truth)
- Fail loudly on schema mismatch instead of .passthrough()
- Add contract-sync CI that compares field counts Zod vs Pydantic
- Show user-visible errors on validation failure, not empty arrays
- Use strict Zod schemas without .passthrough() from day one
- Include Layer 4-5 testing in every QA verification round
- Create shared enum definitions between frontend and backend
- Require browser console capture as part of QA acceptance
- Document every Pydantic→Zod field mapping explicitly
- Run E2E tests that verify actual response shapes, not just HTTP 200

---

*Index maintained by ROUND2-CONTRARIAN missions*

---

## Run Index Entry — Codex 20260204-1651-0e51
- agent_name: Codex
- run_id: 20260204-1651-0e51
- date_time: 2026-02-04T16:51:00Z
- report_path: /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN.Codex.20260204-1651-0e51.md
- json_path: /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN.Codex.20260204-1651-0e51.json

#### Scorecard Summary (Current → Target)
- Layer 1 Architecture Clarity: 5 → 9
- Layer 2 Data Integrity/SOT: 5 → 9
- Layer 3 Contract Correctness: 3 → 9
- Layer 4 Agent Boundaries/HITL: 6 → 9
- Layer 5 Observability: 5 → 9
- Layer 6 Security/Auth: 6 → 9
- Layer 7 UX Correctness: 4 → 9
- Layer 8 Email Ingestion: 5 → 9
- Layer 9 Knowledge/RAG: 4 → 9
- Layer 10 Operational Excellence: 5 → 9

#### Top 10 Next Actions (Prioritized)
1. Execute R2-0 baseline: browser verification + 5-layer contract diff
2. Run CONTRACT-AUDIT-V1 + QA-CA-V1 (unexecuted work)
3. Fix SSE 501 in backend + dashboard; verify browser SSE
4. Implement Idempotency-Key on all write endpoints
5. Add `last_indexed_at` and `content_hash` to deals
6. Remove or isolate SQLite/JSON legacy paths; add CI guard
7. Generate TS client + Zod from OpenAPI; enforce CI contract gate
8. Consolidate /api/actions/capabilities and /metrics to single router
9. Enforce correlation IDs across all client calls (api-client.ts)
10. Remove 8090 references from Makefile/docs; add forbidden-pattern gate

#### Top 10 Contrarian Upgrades (Prioritized)
1. ZK-UPG-0001 — Generated TypeScript Client from OpenAPI (P0)
2. ZK-UPG-0006 — Contract Testing CI Gate (P0)
3. ZK-UPG-0003 — Idempotency Layer (P0)
4. ZK-UPG-0004 — Deal Transition Ledger (P1)
5. ZK-UPG-0002 — Transactional Outbox (P1)
6. ZK-UPG-0006 — Safe Decommissioning Guardrails (P1)
7. ZK-UPG-0005 — OpenTelemetry Integration (P2)
8. ZK-UPG-0007 — Circuit Breakers (P2)
9. ZK-UPG-0008 — Schema Migration Safety (P2)
10. ZK-UPG-0009 — Agent Evaluation Framework (P2)

#### What We Would Do Differently From Day One
- Generate client + Zod from OpenAPI; ban manual schema drift
- Add contract CI gate before any UI or backend merges
- Treat browser verification as a hard gate, not a suggestion
- Build idempotency into every write endpoint from day one
- Use event ledger + outbox for all state changes and side effects
- Eliminate legacy storage on day one (no JSON/SQLite fallback)
- Require OpenTelemetry from day one for traceability
- Avoid `.passthrough()` in schemas; fail loudly on mismatch
- Ensure stage taxonomy exists only once (DB + code), enforced by migrations
- Add regression tests for each known issue before declaring PASS

#### Known Unexecuted Work Incorporated
- CONTRACT-AUDIT-V1
- QA-CA-V1

---

## Run Index Entry: 20260204-1050-gemini

- **Agent:** Gemini-CLI
- **Run ID:** 20260204-1050-gemini
- **Date:** 2026-02-04
- **Report:** [Markdown](./DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN.Gemini-CLI.20260204-1050-gemini.md) | [JSON](./DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN.Gemini-CLI.20260204-1050-gemini.json)

### Scorecard Summary
| Layer | Score | Target | Status |
|-------|-------|--------|--------|
| Client Integration | **3/10** | 9/10 | 🔴 CRITICAL |
| UX Correctness | **5/10** | 9/10 | 🟠 POOR |
| Observability | 6/10 | 9/10 | 🟡 FAIR |
| API Contracts | 8/10 | 10/10 | 🟢 GOOD |

### Top 10 Next Actions
1. **DELETE** `DealSchema` definition in `api-client.ts`.
2. **IMPORT** `DealSchema` from `api-schemas.ts` into `api-client.ts`.
3. **ALIGN** `api-schemas.ts` with backend Pydantic models (fix `broker` type, `priority` location).
4. **REMOVE** `coerceBrokerToString` - let the UI handle the object.
5. **IMPLEMENT** `IdempotencyMiddleware` on backend.
6. **ADD** `X-Idempotency-Key` header to frontend `apiFetch`.
7. **CREATE** `tests/contracts` suite for CI.
8. **UPDATE** Dashboard components to display retrieved `metadata` and `company_info`.
9. **WRAP** RAG calls in circuit breaker.
10. **VERIFY** all write endpoints return 200 on replay.

### Top 5 Contrarian Upgrades
1. **ZK-UPG-0001:** Unified Generated Client (Stop writing Zod by hand).
2. **ZK-UPG-0002:** Idempotency-Key on Writes (Stop creating duplicate data).
3. **ZK-UPG-0003:** Transactional Outbox (Stop losing side-effects).
4. **ZK-UPG-0004:** CI Contract Gate (Stop silent schema drift).
5. **ZK-UPG-0005:** RAG Circuit Breaker (Stop crashing on external dependency failure).

### What We Would Do Differently From Day One
*   **Generate the client:** Never write a manual `fetch` wrapper or Zod schema for an API you control. Use `openapi-typescript-codegen`.
*   **Transactional Outbox:** Never fire an event or email directly from a route handler. Write to DB, let a worker send it.
*   **Monorepo Shared Types:** Share the Pydantic models (converted to TS interfaces) directly if possible, or use a single source of truth (OpenAPI).

### Known Unexecuted Work Incorporated
*   **CONTRACT-AUDIT-V1:** Fully addressed by finding the schema duplication bug.
*   **QA-CA-V1:** Addressed by proposing the CI Contract Gate.

---

## FINAL SYNTHESIS ENTRY — PASS 3: 20260204-1915-p3final

- **agent_name:** Claude-Opus
- **run_id:** 20260204-1915-p3final
- **date_time:** 2026-02-04T19:15:00Z
- **repo_revision:** 2a68de172c7faf1df6f53357f4b43b0161d5dd32
- **synthesis_type:** PASS 3 (FINAL)

### Final Plan Files
- Report: `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN_FINAL.md`
- JSON: `/home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_ROUND2_CONTRARIAN_PLAN_FINAL.json`

### Top 10 Priorities (Execution Order)

1. **R2-0**: Forensic Baseline (BLOCKING) - Collect 5-layer evidence before any changes
2. **R2-1 / UPG-001,006**: Contract Alignment - Generate client from OpenAPI; zero ZodErrors
3. **R2-1 / UPG-007,008**: Schema Cleanup - Trim phantom fields; replace silent failures
4. **R2-2 / UPG-002**: Idempotency Layer - Idempotency-Key on all write endpoints
5. **R2-3**: V2 Coverage Closure - Close 8 missing issues (0003,0004,0006,0012,0015,0017,0019,0021,0022)
6. **R2-4 / UPG-003**: Transactional Outbox - Reliable side-effects via outbox pattern
7. **R2-5 / UPG-009**: Deal Transition Ledger - Auditable lifecycle with 422 on invalid
8. **R2-6 / UPG-005,010**: Observability - Correlation IDs end-to-end; RAG circuit breaker
9. **R2-7 / UPG-004,011**: CI Gates - Contract testing + forbidden-pattern guards
10. **R2-9 / UPG-012**: Regression Proofing - Tests for all 22 V2 issues; legacy removal

### Decision Set Summary

| Decision | Resolution |
|----------|------------|
| Canonical SOT | PostgreSQL `zakops.deals` is SOLE source of truth |
| Contract SOT | OpenAPI is authoritative; generate all client types |
| Agent Boundaries | Audited, idempotent, HITL-gated for destructive ops |
| HITL Persistence | `approvals` table with background expiry job |
| Email Ingestion | Writes directly to PostgreSQL; outbox for side-effects |
| Observability | Correlation IDs mandatory; OTel as stretch goal |
| RAG Strategy | Advisory, not authoritative; circuit breaker required |

### Coverage Verification
- **V2 Issues Total:** 22
- **V2 Issues Mapped:** 22 (100%)
- **Phases:** 10 (R2-0 through R2-9)
- **Builder Missions:** 12
- **Deduplicated Upgrades:** 13

### Input Sources Synthesized
- Opus opus.run001 (21/30)
- Codex 20260204-1651-0e51 (28/30)
- Gemini 20260204-1050-gemini (21/30)
- PASS 1 Claude-Opus 20260204-1835-p1r2
- PASS 2 Codex 20260204-1728-102efc

---

*FINAL SYNTHESIS complete. Ready for execution.*