# COL-V2-BUILD-001A — Completion Report

**Mission:** Core Wiring + Service Completion
**Status:** COMPLETE
**Date:** 2026-02-13
**Phases:** 4/4 complete (0-3 execution + Phase 4 verification)

---

## Phase 0 — Discovery & Baseline (PASS)

| Gate | Result |
|------|--------|
| P0-01: make validate-local | PASS |
| P0-02: Backend health check | PASS (healthy JSON) |
| P0-03: Backend brain endpoints | 404 for fake ID (routing confirmed) |
| P0-04: D-item verification | D1=EXISTS, D2=EXISTS(agent DB), D7=EXISTS, legal_hold_locks=MISSING |
| P0-05: Import checks | 9/10 PASS (momentum_calculator exports function not singleton) |

## Phase 1 — Core Wiring into graph.py (PASS)

**Files modified:** `apps/agent-api/app/core/langgraph/graph.py`

| Task | Actionable Item | Result |
|------|----------------|--------|
| P1-01: _post_turn_enrichment() coroutine | — | CREATED — consolidates brain extraction + drift detection + citation audit |
| P1-02: snapshot_writer.write() | B9.1 | ALREADY WIRED at line 448 (kept in place — needs LLM call data) |
| P1-03: brain_extraction | — | MOVED from standalone fire-and-forget into _post_turn_enrichment() |
| P1-04: drift_detection (check_staleness) | B8.1 | WIRED — logs staleness severity when deal-scoped |
| P1-05: citation_audit (audit_citations) | B1.2 | WIRED — triggers for [cite-N] responses, logs quality_score |
| P1-06: node_registry.route() | B4.2 | WIRED pre-LLM — enhances relevant_memory with specialist analysis (confidence >= 0.6) |
| P1-07: Import cycle check | — | PASS (build_graph + all 5 service imports) |

**Gate P1:** ALL PASS (imports OK, validate-local clean)

## Phase 2 — Service Completion (PASS)

**Files modified:** 7 files across agent-api

| Task | Actionable Item | File | Result |
|------|----------------|------|--------|
| P2-01: Admin role check | B2.1, B3.1 | chatbot.py | _require_admin() with ADMIN_USER_IDS env var |
| P2-02: BackendClient migration | B3-01 | proposal_service.py, export_service.py, backend_client.py | 6 handlers migrated, raw_request() added |
| P2-03: Configurable thresholds | B3-03 | citation_audit.py | CITATION_HIGH_THRESHOLD, CITATION_LOW_THRESHOLD, CITATION_QUALITY_FLOOR |
| P2-04: Proposal expiration | B3-04 | proposal_service.py | 24h expiration check in execute() |
| P2-05: trigger_type='correction' | B3-05 | proposal_service.py | Added to brain summary PUT payload |
| P2-06: Brain export appendix | B3-06 | export_service.py | Appendix C: Deal Brain (facts, risks, summary) |
| P2-07: Replay audit log | B3-07 | replay_service.py | Structured logger.info("replay_audit") with actor_id |
| P2-08: Extractive pre-filter | B3-09 | summarizer.py | Filters short acknowledgments and filler phrases |

**Gate P2:** ALL PASS (7/7 imports OK, validate-local clean)

## Phase 3 — Compliance Foundation (PASS)

**Files created:** `apps/agent-api/migrations/029_legal_hold.sql`

| Task | Result |
|------|--------|
| P3-01: Check migration numbers | Highest existing: 004. Using 029 per mission spec. |
| P3-02: legal_hold_locks table | CREATED with indexes (thread, active) |
| P3-03: legal_hold_log table | CREATED with thread index |
| P3-04: create_monthly_partitions() | ALREADY EXISTED — updated with CREATE OR REPLACE (matching param names) |
| P3-05: Apply migration | APPLIED successfully (COMMIT) |
| P3-06: CRLF + ownership | FIXED |

**Gate P3:** ALL PASS (3 DB objects verified, validate-local clean)

## Phase 4 — Final Verification (PASS)

| Gate | Result |
|------|--------|
| P4-01: make validate-local | PASS |
| P4-02: npx tsc --noEmit | PASS |
| P4-03: All 10 service imports | PASS |
| P4-04: Backend brain endpoint | PASS (404 for fake ID, routing confirmed) |
| P4-05: CHANGES.md | UPDATED |
| P4-06: Completion report | THIS FILE |

---

## Acceptance Criteria Mapping

| AC | Description | Evidence |
|----|------------|----------|
| AC1 | 5 services wired into graph.py turn pipeline | graph.py: _post_turn_enrichment() + node_registry pre-LLM |
| AC2 | All wiring is fire-and-forget (asyncio.create_task) | graph.py: single create_task call for enrichment |
| AC3 | No import cycles | 10/10 imports clean in Docker container |
| AC4 | Admin auth on /admin/* endpoints | chatbot.py: _require_admin() gate |
| AC5 | Raw httpx eliminated from services | 6 handlers migrated to BackendClient |
| AC6 | legal_hold_locks + legal_hold_log tables exist | psql \d verification |
| AC7 | create_monthly_partitions() function exists | psql \df verification |
| AC8 | make validate-local passes after all changes | Final run: PASS |

## Files Created

| File | Phase |
|------|-------|
| `apps/agent-api/migrations/029_legal_hold.sql` | P3 |

## Files Modified

| File | Phase | Changes |
|------|-------|---------|
| `apps/agent-api/app/core/langgraph/graph.py` | P1 | +2 imports, +_post_turn_enrichment(), +node_registry routing, replaced brain extraction call |
| `apps/agent-api/app/api/v1/chatbot.py` | P2 | +os import, +_require_admin(), admin gate on 2 endpoints |
| `apps/agent-api/app/services/backend_client.py` | P2 | +raw_request() method |
| `apps/agent-api/app/services/proposal_service.py` | P2 | +BackendClient import, migrated 5 handlers, +expiration, +trigger_type |
| `apps/agent-api/app/services/export_service.py` | P2 | +BackendClient import, migrated attach_to_deal, +brain appendix |
| `apps/agent-api/app/core/security/citation_audit.py` | P2 | +3 configurable threshold constants |
| `apps/agent-api/app/services/replay_service.py` | P2 | +actor_id param, +audit log entry |
| `apps/agent-api/app/services/summarizer.py` | P2 | +extractive pre-filter for low-signal turns |
