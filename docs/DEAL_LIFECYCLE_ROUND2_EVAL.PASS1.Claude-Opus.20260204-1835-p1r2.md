# DEAL_LIFECYCLE_ROUND2_EVAL — PASS 1: Coverage & Gaps Register

## AGENT IDENTITY
- **agent_name**: Claude-Opus
- **run_id**: 20260204-1835-p1r2
- **date_time**: 2026-02-04T18:35:00Z
- **repo_revision**: 2a68de172c7faf1df6f53357f4b43b0161d5dd32

---

## A) COVERAGE MATRIX (NO-DROP GUARANTEE)

All 22 issues from V2 Issues Register mapped to Round-2 plans.

| Issue ID | Severity | Title | Opus Plan | Codex Plan | Gemini Plan | Status |
|----------|----------|-------|-----------|------------|-------------|--------|
| ZK-ISSUE-0001 | P0 | Split-brain persistence | - | Q1-5: SQLite/JSON adapters still present | - | **ADDRESSED** |
| ZK-ISSUE-0002 | P0 | Email ingestion disabled | - | Q2: Legacy file references | - | **PARTIAL** (no explicit fix) |
| ZK-ISSUE-0003 | P1 | Quarantine approval no deal | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0004 | P1 | No DataRoom folders | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0005 | P1 | No authentication | - | Q1-6: Direct fetch bypasses auth | - | **PARTIAL** |
| ZK-ISSUE-0006 | P1 | Wrong quarantine endpoint | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0007 | P1 | Stage taxonomy conflicts | ZK-UPG-0007 (canonical_name) | Q1-6: Stage taxonomy unified | - | **ADDRESSED** |
| ZK-ISSUE-0008 | P1 | Actions split Postgres/SQLite | - | Q1-5: SQLite action store | - | **ADDRESSED** |
| ZK-ISSUE-0009 | P2 | Agent cannot create deals | - | Q4: Idempotency on tools | - | **PARTIAL** |
| ZK-ISSUE-0010 | P2 | RAG search unverified | - | Q2: RAG columns deferred | ZK-UPG-0005: RAG Circuit Breaker | **ADDRESSED** |
| ZK-ISSUE-0011 | P2 | No event correlation | - | Q1-4: Correlation ID propagation | - | **ADDRESSED** |
| ZK-ISSUE-0012 | P2 | Deal notes endpoint mismatch | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0013 | P2 | Capabilities/metrics 501 | - | Q1-7: 501 vs 200 ambiguity | - | **ADDRESSED** |
| ZK-ISSUE-0014 | P2 | sys.path hack | ZK-UPG-0008: Remove sys.path | - | Layer 2 note | **ADDRESSED** |
| ZK-ISSUE-0015 | P3 | No approval expiry job | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0016 | P2 | No duplicate detection | - | Q1-3: Idempotency layer | ZK-UPG-0002: Idempotency-Key | **ADDRESSED** |
| ZK-ISSUE-0017 | P3 | No retention policy | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0018 | P2 | Zod schema mismatch | ZK-UPG-0001-0006 | Q1-2: Zod schema drift | ZK-UPG-0001,0004 | **ADDRESSED (HIGH FOCUS)** |
| ZK-ISSUE-0019 | P2 | Executors unwired | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0020 | P2 | SSE not implemented | - | Q1-1: SSE 501 in backend+dashboard | - | **ADDRESSED** |
| ZK-ISSUE-0021 | P2 | No scheduling/reminders | - | - | - | **MISSING IN ROUND-2** |
| ZK-ISSUE-0022 | P3 | Archive/restore missing | - | - | - | **MISSING IN ROUND-2** |

### Coverage Summary
| Metric | Count |
|--------|-------|
| V2 Issues Total | 22 |
| Explicitly Addressed | 11 |
| Partially Addressed | 3 |
| **MISSING IN ROUND-2** | **8** |

### Missing Issues (CRITICAL GAP)
The following V2 issues are NOT explicitly mapped in any Round-2 contrarian plan:
1. **ZK-ISSUE-0003** (P1): Quarantine approval does not create deal
2. **ZK-ISSUE-0004** (P1): Dashboard deals don't create DataRoom folders
3. **ZK-ISSUE-0006** (P1): Dashboard uses wrong quarantine endpoint
4. **ZK-ISSUE-0012** (P2): Deal notes endpoint mismatch
5. **ZK-ISSUE-0015** (P3): No approval expiry background job
6. **ZK-ISSUE-0017** (P3): No retention/cleanup policy
7. **ZK-ISSUE-0019** (P2): Action executors unwired
8. **ZK-ISSUE-0021** (P2): No scheduling or reminders
9. **ZK-ISSUE-0022** (P3): Archive/restore endpoints missing

---

## B) CONTRARIAN UPGRADE DEDUPE REGISTER

All ZK-UPG-xxxx upgrades extracted and deduplicated.

### UPG-001: Generated TypeScript Client from OpenAPI
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Opus, Codex, Gemini |
| **Opus ID** | - (implicit in Layer 4-5 analysis) |
| **Codex ID** | ZK-UPG-0001 (UPG-A) |
| **Gemini ID** | ZK-UPG-0001 |
| **Merged Description** | Stop hand-maintaining Zod schemas. Generate TypeScript client and Zod schemas directly from Backend OpenAPI spec. CI regeneration required. |
| **Why It Matters** | Eliminates manual schema drift, the root cause of Layer 4-5 contract failures. Multiple sources of truth (Pydantic, Zod, TS types) cause silent data loss. |
| **Execution Order** | Phase R2-1 (P0) |
| **Verification** | Contract CI gate fails on mismatch between OpenAPI and generated client. |

### UPG-002: Idempotency-Key on All Write Endpoints
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex, Gemini |
| **Codex ID** | ZK-UPG-0003 (UPG-C) |
| **Gemini ID** | ZK-UPG-0002 |
| **Merged Description** | Enforce `Idempotency-Key` header on all POST/PUT endpoints. Middleware checks idempotency_store table. Duplicate returns 200 (cached response), not 500/409. |
| **Why It Matters** | Double-clicking "Create Deal" currently creates two deals. Prevents race conditions and 500 errors on duplicates. |
| **Execution Order** | Phase R2-2 (P0-P1) |
| **Verification** | Duplicate POST returns same response; no 500 errors. |

### UPG-003: Transactional Outbox for Side-Effects
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex, Gemini |
| **Codex ID** | ZK-UPG-0002 (UPG-B) |
| **Gemini ID** | ZK-UPG-0003 |
| **Merged Description** | Write events to `outbox` table in same transaction as domain writes. Relay worker processes them. No fire-and-forget HTTP calls in app code. |
| **Why It Matters** | If `record_deal_event` fails, notifications lost. Outbox provides reliable side effects. Health endpoint notes processor never processed actions. |
| **Execution Order** | Phase R2-4 (P1) |
| **Verification** | Chaos test with relay restart; outbox processed in <=5s; no dropped events. |

### UPG-004: Contract Testing CI Gate
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Opus, Codex, Gemini |
| **Opus ID** | ZK-UPG-0006 (remove .passthrough()) |
| **Codex ID** | ZK-UPG-0006 (UPG-F) |
| **Gemini ID** | ZK-UPG-0004 |
| **Merged Description** | CI job validates responses against OpenAPI + Zod. If `safeParse` fails on any fixture, BUILD FAILS. Stop ZodError class of bugs permanently. |
| **Why It Matters** | Current silent failures return `[]` on schema mismatch. Users see empty data. |
| **Execution Order** | Phase R2-7 (P2) |
| **Verification** | CI fails on mismatch; integration test against backend fixtures. |

### UPG-005: RAG Circuit Breaker
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex, Gemini |
| **Codex ID** | ZK-UPG-0007 (UPG-G) |
| **Gemini ID** | ZK-UPG-0005 |
| **Merged Description** | Circuit breaker wrapper on RAG calls. If RAG down, fallback to SQL `ILIKE` search or fail gracefully. Prevent cascading failure. |
| **Why It Matters** | Agent tool `search_deals` calls port 8052 blind. If down, agent crashes or hallucinates. |
| **Execution Order** | Phase R2-6 (P2) |
| **Verification** | Simulated outage; system degrades gracefully. |

### UPG-006: ActionStatus Enum Alignment (RUNNING vs PROCESSING)
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Opus |
| **Opus ID** | ZK-UPG-0001 (P0) |
| **Merged Description** | Align ActionStatus enum between Zod (RUNNING) and Pydantic (PROCESSING). Either backend uses RUNNING or Zod uses PROCESSING. |
| **Why It Matters** | Status display fails for PROCESSING actions - backend says PROCESSING, Zod expects RUNNING. |
| **Execution Order** | Phase R2-1 (P0) |
| **Verification** | Actions list displays correct status for all states. |

### UPG-007: Trim ActionSchema Phantom Fields
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Opus |
| **Opus ID** | ZK-UPG-0002 (P1) |
| **Merged Description** | Remove 13 phantom fields from ActionSchema that backend never returns (started_at, completed_at, retry_count, etc.) OR expand ActionResponse Pydantic model. |
| **Why It Matters** | 13 fields will be undefined/missing on every API response, causing validation issues. |
| **Execution Order** | Phase R2-1 (P1) |
| **Verification** | ActionSchema fields match ActionResponse exactly. |

### UPG-008: Replace Silent Failures with User Errors
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Opus, Gemini |
| **Opus ID** | ZK-UPG-0004 (P1) |
| **Gemini ID** | (implicit in UPG-0004) |
| **Merged Description** | Instead of returning `[]` on safeParse failure, throw user-visible error or show toast notification. |
| **Why It Matters** | When Zod validation fails, UI shows empty data instead of error. Users see nothing and don't know why. |
| **Execution Order** | Phase R2-1 (P1) |
| **Verification** | Schema mismatch shows user-visible error, not empty list. |

### UPG-009: Deal Transition Ledger
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex |
| **Codex ID** | ZK-UPG-0004 (UPG-D) |
| **Merged Description** | Add `deal_transitions` append-only table. Auditable, deterministic lifecycle. Invalid transition yields 422. UI timeline. |
| **Why It Matters** | Stage changes validated in code but no ledger table. Race conditions possible. |
| **Execution Order** | Phase R2-5 (P1) |
| **Verification** | Invalid transition returns 422; ledger row exists for every transition. |

### UPG-010: OpenTelemetry Integration
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex |
| **Codex ID** | ZK-UPG-0005 (UPG-E) |
| **Merged Description** | OTel spans across services, SSE propagation. Real tracing browser → backend → agent → DB. |
| **Why It Matters** | Correlation ID middleware only exists; no OTel, no browser trace propagation. |
| **Execution Order** | Phase R2-6 (P2) |
| **Verification** | Trace visible in Jaeger/Zipkin. |

### UPG-011: Safe Decommissioning Guardrails
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex |
| **Codex ID** | ZK-UPG-0010 (UPG-J) |
| **Merged Description** | CI lint forbids legacy patterns (8090, JSON registry, SQLite). Prevent legacy resurrection. |
| **Why It Matters** | 8090 references remain in Makefile; legacy code paths can resurrect. |
| **Execution Order** | Phase R2-9 (P1) |
| **Verification** | rg gate fails if legacy patterns appear. |

### UPG-012: Schema Migration Safety
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex |
| **Codex ID** | ZK-UPG-0008 (UPG-H) |
| **Merged Description** | Expand/contract migration strategy + CI migration test. Avoid drift and irreversible DB changes. |
| **Why It Matters** | Migrations exist but no enforced down path. |
| **Execution Order** | Phase R2-9 (P2) |
| **Verification** | Migration rollback succeeds in CI. |

### UPG-013: Agent Evaluation Framework
| Attribute | Value |
|-----------|-------|
| **Proposed By** | Codex |
| **Codex ID** | ZK-UPG-0009 (UPG-I) |
| **Merged Description** | Golden eval suite with scenario-based tests for agent tool selection. Prevent regressions. |
| **Why It Matters** | No golden eval suite currently exists. |
| **Execution Order** | Phase R2-8 (P2) |
| **Verification** | >=18/20 scenarios pass. |

### Upgrade Summary
| Metric | Count |
|--------|-------|
| Total Upgrades Proposed (Raw) | 24 |
| After Deduplication | 13 |
| P0 (Critical) | 3 |
| P1 (High) | 6 |
| P2 (Medium) | 4 |

---

## C) PLAN QUALITY SCORECARD

### Opus Plan (opus.run001)

| Criterion | Score (0-5) | Notes |
|-----------|-------------|-------|
| Coverage completeness (V2 issues) | 2 | Only addresses Layer 4-5 issues (ZK-UPG focused); misses 8+ V2 issues |
| Depth/contrarian value | 5 | Excellent deep-dive on Zod vs Pydantic drift; novel finding on ActionStatus RUNNING/PROCESSING |
| Sequencing & dependency clarity | 3 | Upgrades listed but no phased execution plan |
| Verification/gates toughness | 4 | Specific verification steps for each upgrade |
| Realism/executability | 4 | Actionable file paths and specific changes |
| Alignment to end-state | 3 | Focused on contracts, weak on SOT DB, auth, email |
| **Total** | **21/30** | |

### Codex Plan (20260204-1651-0e51)

| Criterion | Score (0-5) | Notes |
|-----------|-------------|-------|
| Coverage completeness (V2 issues) | 4 | Addresses 11+ V2 issues with soft-pass analysis |
| Depth/contrarian value | 5 | Excellent: identifies soft-pass illusion, evidence-based critique |
| Sequencing & dependency clarity | 5 | Full R2-0 through R2-9 phased plan with gates |
| Verification/gates toughness | 5 | Hard-pass criteria for each soft-pass; ADV scenarios |
| Realism/executability | 4 | Clear tasks but ambitious scope |
| Alignment to end-state | 5 | Covers SOT, auth, observability, email, HITL |
| **Total** | **28/30** | |

### Gemini Plan (20260204-1050-gemini)

| Criterion | Score (0-5) | Notes |
|-----------|-------------|-------|
| Coverage completeness (V2 issues) | 2 | Focuses narrowly on schema duplication bug |
| Depth/contrarian value | 4 | "Smoking Gun" analysis is compelling; finds dual DealSchema |
| Sequencing & dependency clarity | 4 | Clear R2-0 through R2-4 phases |
| Verification/gates toughness | 3 | ADV scenarios but fewer than Codex |
| Realism/executability | 5 | Focused, achievable scope |
| Alignment to end-state | 3 | Weak on SOT, auth, email, HITL |
| **Total** | **21/30** | |

---

## D) CONFLICTS & DIVERGENCES

### Conflict 1: Generated Client vs Manual Fix
| Plan | Position |
|------|----------|
| Opus | Trim/align existing schemas manually |
| Codex | Generate client from OpenAPI; delete manual schemas |
| Gemini | Delete duplicates, import from api-schemas.ts, then align |

**Resolution Evidence Needed**: Benchmark time-to-fix for manual alignment vs generation pipeline setup. Generation is more sustainable long-term.

### Conflict 2: ActionStatus Naming
| Plan | Position |
|------|----------|
| Opus | Align RUNNING/PROCESSING (either direction) |
| Codex | Not explicitly mentioned |
| Gemini | Not explicitly mentioned |

**Resolution Evidence Needed**: Check which name is used in UI copy/UX flows. Prefer the user-facing term.

### Conflict 3: Scope of R2 Remediation
| Plan | Position |
|------|----------|
| Opus | Narrow: Layer 4-5 contract drift only |
| Codex | Wide: All 10 layers, full platform hardening |
| Gemini | Medium: Client integration + idempotency |

**Resolution Evidence Needed**: Decide if R2 is a focused sprint (Opus/Gemini) or full platform upgrade (Codex).

### Conflict 4: Phasing Priority
| Plan | Position |
|------|----------|
| Opus | P0: ActionStatus fix first |
| Codex | P0: Browser verification baseline first (R2-0) |
| Gemini | P0: Schema unification first (R2-1) |

**Resolution**: These are compatible. Sequence: R2-0 baseline → schema unification (includes ActionStatus) → idempotency.

### Possible Overlap: ZK-UPG Numbering Collision
- Opus ZK-UPG-0001: ActionStatus enum fix
- Codex ZK-UPG-0001: Generated TS client
- Gemini ZK-UPG-0001: Unified generated client

**Note**: Same upgrade ID used for different scopes. Dedupe register above consolidates these.

---

## E) WHAT'S STILL NOT PROVEN

Even if plans claim "fixed," these items require runtime proof:

### 1. Browser Console Zero ZodErrors
| Item | Proof Required |
|------|----------------|
| **Claim** | Zod schemas aligned |
| **Runtime Test** | Open Dashboard in browser, navigate to Actions and Deals pages, capture DevTools Console, grep for "ZodError" or schema failures |
| **Evidence Path** | Screenshot or console log file |

### 2. SSE Actually Works
| Item | Proof Required |
|------|----------------|
| **Claim** | SSE 501 will be fixed |
| **Runtime Test** | `curl http://localhost:8091/api/events/stream` returns SSE frames; Dashboard connects without console errors; reconnection works after disconnect |
| **Evidence Path** | curl output + browser Network tab screenshot |

### 3. Idempotency Returns 200 on Duplicate
| Item | Proof Required |
|------|----------------|
| **Claim** | Idempotency-Key implemented |
| **Runtime Test** | POST /api/deals with same Idempotency-Key twice; second returns 200 (not 201/409/500) with identical response body |
| **Evidence Path** | curl output showing both requests and responses |

### 4. Legacy Paths Actually Deleted
| Item | Proof Required |
|------|----------------|
| **Claim** | SQLite/JSON adapters removed |
| **Runtime Test** | `rg -l "deal_registry.json|ingest_state.db|sqlite" --type py` returns empty in production code; CI guard blocks reintroduction |
| **Evidence Path** | rg output |

### 5. Correlation IDs in All Logs
| Item | Proof Required |
|------|----------------|
| **Claim** | Correlation ID propagation |
| **Runtime Test** | Make API request with X-Correlation-ID header; grep backend logs and deal_events table for that ID |
| **Evidence Path** | Log sample + SQL query result |

### 6. RAG Service Health
| Item | Proof Required |
|------|----------------|
| **Claim** | RAG service will have circuit breaker |
| **Runtime Test** | Stop RAG service; call search_deals; verify graceful fallback (not crash) |
| **Evidence Path** | Error response or fallback behavior |

### 7. ActionStatus Displays Correctly
| Item | Proof Required |
|------|----------------|
| **Claim** | RUNNING/PROCESSING aligned |
| **Runtime Test** | Create action with PROCESSING status in backend; verify Dashboard shows correct status (not blank or error) |
| **Evidence Path** | Screenshot of Dashboard Actions page |

### 8. Stage Taxonomy at DB Level
| Item | Proof Required |
|------|----------------|
| **Claim** | DB default is 'inbound' |
| **Runtime Test** | `SELECT column_default FROM information_schema.columns WHERE table_name='deals' AND column_name='stage';` returns 'inbound' (not 'lead') |
| **Evidence Path** | SQL query result |

---

## F) CONSENSUS VS DIVERGENT ITEMS

### High-Leverage Consensus (All 3 agents agree)
1. **Generated client from OpenAPI** - Eliminates manual schema drift
2. **Idempotency-Key on writes** - Prevents duplicates and 500 errors
3. **Contract CI gate** - Prevents regression
4. **RAG circuit breaker** - Prevents cascading failure

### High-Leverage Divergent (Only 1-2 agents propose)
1. **Deal Transition Ledger** (Codex only) - Append-only audit trail
2. **OpenTelemetry** (Codex only) - Full distributed tracing
3. **Agent Evaluation Framework** (Codex only) - Golden test suite
4. **ActionStatus enum fix** (Opus only) - Specific RUNNING/PROCESSING issue

---

## G) STATISTICS

| Metric | Value |
|--------|-------|
| V2 Issues Total | 22 |
| V2 Issues Mapped to R2 | 14 (64%) |
| V2 Issues MISSING in R2 | 8 (36%) |
| Raw Upgrades Proposed | 24 |
| Deduplicated Upgrades | 13 |
| Agents Analyzed | 3 |
| Plans Read | 3 |

---

*Generated by PASS 1 Coverage & Gaps Register*
*Agent: Claude-Opus*
*Run ID: 20260204-1835-p1r2*
*Timestamp: 2026-02-04T18:35:00Z*
