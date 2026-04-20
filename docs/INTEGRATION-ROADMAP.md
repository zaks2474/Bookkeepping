# ZakOps + LangSmith Agent Integration Roadmap

**Spec:** `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` (1,074 lines, compiled 2026-02-16)
**Agreed by:** ZakOps (Claude Code / Opus 4.6) + LangSmith Exec Agent
**Total Phases:** 3 (per Locked Decision #17: "3-phase build plan")

---

## Integration Overview

The integration connects two autonomous systems:
- **ZakOps** — deal lifecycle management, quarantine, operator dashboard (system of record)
- **LangSmith Exec Agent** — email triage, research, document analysis, Gmail management

Communication flows through the **MCP Bridge** (port 9100, 23 tools) using an **action queue** as the coordination backbone. No direct agent-to-agent communication.

---

## Phase Summary

| Phase | Name | Items | Status | Completion Date | Report |
|-------|------|-------|--------|-----------------|--------|
| 1 | Feedback Loop | 1-7 | COMPLETE (9/9 AC) | 2026-02-17 | [Completion Report](INTEGRATION-PHASE1-BUILD-001-COMPLETION.md) |
| 2 | Delegation Framework | 8-14 | COMPLETE (11/11 AC) | 2026-02-17 | [Completion Report](INTEGRATION-PHASE2-BUILD-001-COMPLETION.md) |
| 3 | Bi-directional Communication | 15-17 + ENH | COMPLETE (8/8 AC) | 2026-02-18 | [Completion Report](INTEGRATION-PHASE3-BUILD-001-COMPLETION.md) |

**QA Verification (P1+P2):** [QA-UNIFIED-P1P2-VERIFY-001](../qa-verifications/QA-UNIFIED-P1P2-VERIFY-001/QA-UNIFIED-P1P2-VERIFY-001-SCORECARD.md) — 60/60 gates PASS, 0 FAIL, 10 ENH
**QA Verification (P3):** [QA-IP3-VERIFY-001](QA-IP3-VERIFY-001.md) — 49/49 gates PASS, 0 FAIL, 8 ENH

---

## Phase 1 — Feedback Loop (COMPLETE)

**Objective:** Enable the agent to learn from operator decisions and self-audit classification accuracy.

**Deliverables:**
- `zakops_get_triage_feedback` — per-sender approval/rejection history
- `zakops_list_brokers` — broker registry with incremental sync
- `zakops_get_classification_audit` — historical accuracy metrics
- `zakops_get_sender_intelligence` — aggregated sender signals
- `zakops_get_manifest` — integration manifest with per-tool SHA256 signatures
- `zakops_list_quarantine` expansion — since_ts, status, sender, thread_id filters

**Key Result:** Pipeline A injection test proven end-to-end — email classified as DEAL_SIGNAL (0.97 confidence), injected to quarantine (201 Created), quarantine item `69223113-4528-43fb-97a6-5c67d597bb7f` created, operator approved, routed to deal DL-0121.

**MCP Bridge:** 16 → 21 tools

---

## Phase 2 — Delegation Framework (COMPLETE)

**Objective:** Enable atomic task delegation with lease-based claiming, race-condition protection, and research artifact storage.

**Deliverables:**
- Migration 036: 9 lease columns + 2 indexes on `delegated_tasks`
- 16 integration action types with default lease durations (Spec §5)
- `POST /api/tasks/{id}/claim` — atomic SELECT FOR UPDATE claiming
- `POST /api/tasks/{id}/renew-lease` — lease heartbeat renewal
- `POST /api/tasks/{id}/result` expansion — artifacts, research_id, LangSmith tracing
- `GET /api/delegation/tasks` — deal-agnostic task listing with claimable filters
- `GET /api/delegation/types` — action type registry
- `POST /api/delegation/tasks` — deal-optional task creation (feature-flag gated)
- `zakops_claim_action` + `zakops_renew_action_lease` MCP tools
- Dashboard "Delegate" button on quarantine page

**Key Result:** Race condition proven safe — `asyncio.gather` with two concurrent claims produces exactly [200, 409]. Golden tests T5 (round-trip), T9 (race condition), T10 (artifact storage) all PASS.

**MCP Bridge:** 21 → 23 tools

---

## Phase 3 — Bi-directional Communication (COMPLETE)

**Objective:** Close the bi-directional loop — proactive push, efficient polling, and mid-task operator-agent messaging.

**Deliverables:**
- **Lease expiry reaper** (ENH-9) — `LeaseReaper` background worker reclaims expired leases (8 tasks reclaimed in golden test)
- **Gmail back-labeling push** (Item 15) — `_maybe_create_backfill_task` hooked into approve/reject paths
- **Event polling expansion** (Item 16) — `since_ts`, `event_type` params + deal-agnostic `GET /api/events/history`
- **Operator-to-agent messaging** (Item 17) — `POST /api/tasks/{id}/message` + `zakops_get_task_messages` MCP tool + dashboard message UI panel
- **Dashboard UX fixes** (ENH-5, ENH-6) — `DelegationDisabledError` for 503 detection, specific error toasts
- **`@ensure_dict_response` decorator** (ENH-10) — replaced 9 manual `_ensure_dict()` call sites

**Key Result:** All 4 golden tests PASS — T7-enhanced (event history with filters), T-reaper (8 expired-lease reclaims), T-backlabel (quarantine approve creates SYNC.BACKFILL_LABELS task), T-message (operator + system messages with terminal rejection).

**Bugs found & fixed during build:** since_ts string→datetime parsing, logger undefined in helper (print() pattern), SSE stub route blocking /api/events/history proxy.

**MCP Bridge:** 23 → 23 tools (existing tools expanded, no new tool count increase)

**Mission Prompt:** [`MISSION-INTEGRATION-PHASE3-BUILD-001.md`](MISSION-INTEGRATION-PHASE3-BUILD-001.md)
**Completion Report:** [`INTEGRATION-PHASE3-BUILD-001-COMPLETION.md`](INTEGRATION-PHASE3-BUILD-001-COMPLETION.md)
**Successor:** QA-IP3-VERIFY-001

---

## LangSmith Agent Handshake Status

**Last Verified:** 2026-02-18 (Phase 3 deployment verified)
**Agent Identity:** `langsmith_exec_agent_prod`
**Agent Tools:** 30 total (6 Gmail MCP + 24 ZakOps MCP)

| Capability | Status |
|-----------|--------|
| Pipeline A (read → classify → label → inject) | **PRODUCTION RUN COMPLETE** (14/14 injections, 25/25 labels) |
| Phase 1 read enrichment (5 tools) | ALL 5 LIVE |
| Phase 2 delegation (claim → execute → report) | LIVE (`delegate_actions` = true) |
| Phase 3 bi-directional (events, messaging, back-label) | ALL 5 TESTS PASS |
| Full batch triage | **COMPLETE** — first run 2026-02-18 |

**Phase 3 Verification (2026-02-18):**
- TEST 1: `zakops_get_manifest()` — bridge_tool_count=24, prompt_version="v1.0-integration-phase3" PASS
- TEST 2: `zakops_list_recent_events(since_ts=...)` — deal-agnostic mode, 4 events returned PASS
- TEST 3: `zakops_list_recent_events()` [no params] — 400 guard correct PASS
- TEST 4: `zakops_get_task_messages` — in autonomous tier, signature confirmed PASS
- TEST 5: `zakops_list_actions(action_type="SYNC.BACKFILL_LABELS")` — correct empty structure PASS

**First Production Run (2026-02-18):**
- Run ID: `poll_run_2026-02-18T08:47:00Z` | Correlation: `et-a3f7c1b9d4e2`
- 25 emails fetched → 15 DEAL_SIGNAL, 4 NEWSLETTER, 6 SPAM
- 14/14 quarantine injections (all 201 Created), 25/25 Gmail labels applied
- 2 HIGH urgency (ENLIGN + Transworld), 1 MED, 22 LOW
- Known gap: `zakops_report_task_result` 500 — agent needs self-delegate pattern for ad-hoc runs

**Operational State:**
- `delegate_actions` = **true** (enabled 2026-02-18)
- Lease reaper ACTIVE (30s reclaim — agent renews proactively)
- 16 task types registered
- SYNC.BACKFILL_LABELS auto-creation LIVE
- Operator messaging channel open

---

## 19 Locked Decisions (from Spec §15)

1. ZakOps = system of record; LangSmith memories = heuristic caches
2. Domain split: LangSmith = external ops; ZakOps internal agent = deal-side automation
3. Action queue = coordination backbone (no direct agent-to-agent communication)
4. 22 tools (16 existing + 6 new) — actual: 23 after Phase 2
5. 16 action types with default lease durations
6. 5 detailed payload schemas (inputs + results + artifacts)
7. 3 canonical processing pipelines (poll, research, sync)
8. 3-tier security model enforced by policy_guard
9. Error contract: read failures degrade, write failures abort+retry
10. Integration manifest at GET /integration/manifest with per-tool signature hashes
11. Identity contract: executor_id + correlation_id + langsmith tracing on all writes
12. Cache strategy: hybrid (6h background sync + inline for high-signal)
13. Gmail back-labeling: periodic sync primary + optional ZakOps push
14. Broker registry: ZakOps source of truth, LangSmith read-only cache
15. Deal matching: LangSmith proposes, ZakOps routes
16. 11 golden tests for verification
17. 3-phase build plan
18. Lease renewal for long-running tasks
19. Run reports committed at end of every invocation

---

## 11 Golden Tests (from Spec §13)

| Test | Scenario | Phase | Status |
|------|----------|-------|--------|
| T1 | Fresh email from unknown sender | P1 | Covered (injection test) |
| T2 | Email matching known broker pattern | P1 | Covered (broker registry) |
| T3 | Duplicate email (same message_id) | P1 | Covered (dedup) |
| T4 | Email from sender with prior approvals | P1 | Covered (feedback boost) |
| T5 | Operator delegates RESEARCH.COMPANY_PROFILE | P2 | **PASS** (7-step round-trip) |
| T6 | Bridge down during injection | P1 | Covered (degrade + retry) |
| T7 | New broker added in ZakOps | P3 | **PASS** (enhanced with since_ts, deal_id, error cases) |
| T8 | Inject fails (500/timeout) | P1 | Covered (label + retry) |
| T9 | Two executors poll same action | P2 | **PASS** (concurrent claims → [200, 409]) |
| T10 | Research artifact written | P2 | **PASS** (artifact in DB, research_id linked) |
| T11 | Reply in thread with pending quarantine | P1 | Covered (thread_id filter) |

---

## Integration Complete — Post-Integration Backlog

All 3 phases delivered. The integration is functionally complete per Spec v1.0.

| Item | Priority | Description | Status |
|------|----------|-------------|--------|
| QA-IP3-VERIFY-001 | HIGH | Independent QA verification of Phase 3 | **COMPLETE** (49/49 gates, 0 remediations) |
| Feature flag enablement | OPERATOR | Set `delegate_actions=true` to enable full delegation pipeline | **DONE** (2026-02-18) |
| Pipeline A batch triage | HIGH | First full production run | **DONE** (14/14 injections, 25/25 labels) |
| Self-delegate pattern for ad-hoc runs | MEDIUM | Agent needs to `zakops_create_action` before `zakops_report_task_result` for self-initiated runs (500 on poll_run_ IDs) | OPEN |
| Domain Knowledge Extraction | LOW | Extract classification signals, vendor patterns, broker heuristics from LangSmith Agent Builder export into local systems (Option A from analysis) | BACKLOGGED |

---

## Key Artifact Paths

| Artifact | Path |
|----------|------|
| This roadmap | `/home/zaks/bookkeeping/docs/INTEGRATION-ROADMAP.md` |
| Integration Spec v1.0 | `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` |
| Phase 1 completion | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md` |
| Phase 2 completion | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE2-BUILD-001-COMPLETION.md` |
| Phase 3 mission | `/home/zaks/bookkeeping/docs/MISSION-INTEGRATION-PHASE3-BUILD-001.md` |
| Phase 3 completion | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE3-BUILD-001-COMPLETION.md` |
| P1+P2 QA scorecard | `/home/zaks/bookkeeping/qa-verifications/QA-UNIFIED-P1P2-VERIFY-001/QA-UNIFIED-P1P2-VERIFY-001-SCORECARD.md` |
| Phase 3 deployment package | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE3-DEPLOYMENT-PACKAGE.md` |
| LangSmith export | `/mnt/c/Users/mzsai/Downloads/ZakOps_Gmail_Triage_Agent.zip` (58KB, config+prompts only) |
| Change log | `/home/zaks/bookkeeping/CHANGES.md` |

---

*Last Updated: 2026-02-18*
