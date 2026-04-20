QA-COL-DEEP-VERIFY-001A — Final Scorecard
Date: 2026-02-13
Auditor: Claude Opus 4.6

Pre-Flight:
  PF-1 (validate-local):           PASS
  PF-2 (tsc --noEmit):             PASS
  PF-3 (agent-api health):         PASS
  PF-4 (evidence directory):       PASS
  PF-5 (spec line count):          PASS (3276 >= 3000)

Verification Gates:
  VF-01 (Migration 004 Schema):    5 / 5 gates PASS
    VF-01.1: All 9 tables found (+ 2 partition sub-tables)
    VF-01.2: All 6 legal hold/compliance columns + chk_scope + chk_delete constraints
    VF-01.3: UNIQUE(thread_id, turn_number) via uq_thread_turn at line 79
    VF-01.4: PARTITION BY RANGE(created_at) for both turn_snapshots + cost_ledger, DEFAULT partitions present
    VF-01.5: cost_ledger partitioned, cost_ledger_default present, deal_cost_summary VIEW (non-materialized)

  VF-02 (ChatRepository):          6 / 6 gates PASS
    VF-02.1: create_thread writes to thread_ownership (lines 81-91)
    VF-02.2: get_thread JOINs thread_ownership, raises PermissionError (line 113)
    VF-02.3: soft_delete checks legal_hold, raises ValueError with "409 Conflict" (line 194)
    VF-02.4: hard_delete cascades across 11 tables (session_summaries through chat_threads)
    VF-02.5: get_messages uses before_turn cursor pagination by turn_number
    VF-02.6: enqueue_brain_extraction writes to cross_db_outbox (lines 504-519)

  VF-03 (Chatbot API):             5 / 5 gates PASS
    VF-03.1: GET /threads with user_id filtering via session.user_id
    VF-03.2: GET /threads/{id}/messages with before_turn Query parameter
    VF-03.3: POST /threads calls chat_repository.create_thread (ownership included)
    VF-03.4: PATCH /threads/{id} with UpdateThreadRequest(title, pinned, archived)
    VF-03.5: DELETE /threads/{id} with permanent=Query(False), 409 on legal hold

  VF-04 (Middleware Routing):      3 / 3 gates PASS
    VF-04.1: /api/v1/chatbot/* routed to AGENT_API_URL (port 8095) at line 84
    VF-04.2: X-User-Id injected in both pass-through (line 77) and proxy (line 99)
    VF-04.3: X-User-Role injected in both pass-through (line 78) and proxy (line 100)

  VF-05 (Migration 028 Brain):     5 / 5 gates PASS
    VF-05.1: All 10 spec columns present in deal_brain table
    VF-05.2: deal_brain_history with version, snapshot, diff, trigger_type
    VF-05.3: deal_entity_graph with UNIQUE(entity_type, normalized_name, deal_id)
    VF-05.4: decision_outcomes table created at line 92
    VF-05.5: deal_access with CHECK (role IN ('viewer','operator','approver','admin'))

  VF-06 (Brain Service):           5 / 5 gates PASS
    VF-06.1: get_brain (line 33) and get_or_create_brain (line 44) both present
    VF-06.2: add_facts with confidence field per fact, deduplication by key
    VF-06.3: extract_from_turn processes per-turn data (line 243), calls ghost + momentum
    VF-06.4: record_history writes to deal_brain_history with version tracking
    VF-06.5: upsert_entity writes to deal_entity_graph with ON CONFLICT increment

  VF-07 (Ghost Knowledge):         4 / 4 gates PASS
    VF-07.1: detect(deal_id, user_message, existing_facts) at line 55
    VF-07.2: 8 FACT_PATTERNS covering $amounts, %, dates, proper nouns (4/4 categories)
    VF-07.3: Returns key, detected_value (=value), confidence per ghost flag
    VF-07.4: GHOST_CONFIDENCE_THRESHOLD = 0.5 at line 40

  VF-08 (Momentum Calculator):     4 / 4 gates PASS
    VF-08.1: 5 weights: stage_velocity(0.30), event_frequency(0.20), open_item_completion(0.20), risk_trajectory(0.15), action_rate(0.15) = 1.00
    VF-08.2: _clamp(value, 0.0, 100.0) at line 46
    VF-08.3: 4 color bands: green(80-100), blue(50-79), amber(20-49), red(0-19)
    VF-08.4: compute(deal_id) at line 128, compute_and_store(deal_id) at line 207

  VF-09 (Injection Guard):         4 / 4 gates PASS
    VF-09.1: @dataclass ScanResult with passed, patterns_found, severity, sanitized_content
    VF-09.2: INJECTION_PATTERNS has 15 patterns (>= 12 threshold)
    VF-09.3: 3 severity levels: low(4), medium(4), high(7)
    VF-09.4: scan_input(content) -> ScanResult at line 64

  VF-10 (Canary Tokens):           3 / 3 gates PASS
    VF-10.1: inject_canary() at line 46 (class) and line 91 (module-level)
    VF-10.2: verify_no_leakage() at line 68, returns False on leak
    VF-10.3: hashlib.sha256 at line 41, zero-width unicode encoding

  VF-11 (Session Tracker):         2 / 2 gates PASS
    VF-11.1: MAX_ATTEMPTS_BEFORE_LOCKDOWN = 3 at line 14
    VF-11.2: record_attempt(session_id, severity) -> bool at line 31, SessionInjectionTracker class

  VF-12 (SSE Events):              3 / 3 gates PASS
    VF-12.1: 15 typed event models in SSE_EVENT_TYPES registry (>= 10 threshold)
    VF-12.2: GhostKnowledgeEvent at line 94 (+ GhostKnowledgeFlagsEvent at line 100)
    VF-12.3: LegalHoldSetEvent at line 70

  VF-13 (User Identity Map):       3 / 3 gates PASS
    VF-13.1: canonical_id VARCHAR(255) PRIMARY KEY at line 18
    VF-13.2: 0 INTEGER user_id, 5+ VARCHAR(255) user_id across tables
    VF-13.3: CHECK (role IN ('VIEWER','OPERATOR','APPROVER','ADMIN')) at line 26

  VF-14 (Migration Rollbacks):     3 / 3 gates PASS
    VF-14.1: 004 rollback drops all 9 tables + 2 partitions + 1 view + 2 functions + 1 trigger, schema_migrations cleanup
    VF-14.2: 030_partition_automation_rollback.sql exists; 004 rollback also drops create_monthly_partitions()
    VF-14.3: All rollback files include DELETE FROM schema_migrations (004: 1 ref, 030: 1 ref, 028: 1 ref)

  VF-15 (Graph.py Integration):    4 / 4 gates PASS
    VF-15.1: asyncio.create_task(_post_turn_enrichment(...)) at line 1310 wraps brain extraction
    VF-15.2: asyncio.create_task(snapshot_writer.write(snap)) at line 451
    VF-15.3: asyncio.create_task(cost_repository.record_cost(...)) at lines 418, 700
    VF-15.4: No direct await on enrichment in response path; all via create_task (11 total)

Cross-Consistency:
  XC-1 (table count):              PASS (12 CREATE TABLE, 9 main tables match spec)
  XC-2 (ChatRepository coverage):  PASS (12/12 spec methods implemented)
  XC-3 (endpoint coverage):        PASS (all 5 endpoint categories present, 17 total routes)
  XC-4 (brain column count):       PASS (24 columns in deal_brain, >= 18 threshold)
  XC-5 (SSE event coverage):       PASS (14/14 spec event types have references)

Stress Tests:
  ST-1 (no raw httpx):             PASS (INFO: rag_rest.py and llm.py use raw httpx for RAG/LLM, not backend)
  ST-2 (singleton instances):      PASS (5/6 implemented services have singletons; injection_guard uses module functions)
  ST-3 (spec docstrings):          PASS (all 6 agent-api + 6 backend service files reference spec sections)
  ST-4 (partition idempotency):    PASS (IF NOT EXISTS via pg_class check + CREATE TABLE IF NOT EXISTS)
  ST-5 (legal hold both deletes):  PASS (both soft_delete_thread and hard_delete_thread check legal_hold)

Total: 69 / 69 gates PASS, 0 FAIL, 0 SKIP, 2 INFO

INFO Items:
  1. ST-1: rag_rest.py and llm.py use raw httpx — legitimate for RAG/LLM services (not backend).
     BackendClient monopoly applies to backend API calls only.
  2. ST-2: injection_guard.py has module-level functions (scan_input, wrap_with_boundaries) instead of
     a singleton instance. This is appropriate for a stateless utility module.

Remediations Applied: 0
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: FULL PASS
