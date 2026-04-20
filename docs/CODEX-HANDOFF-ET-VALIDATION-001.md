# Codex Handoff Note: MISSION-ET-VALIDATION-001

**Date:** 2026-02-14
**Author:** Builder (Claude Opus 4.6)
**Purpose:** Context for Codex CLI to generate mission prompt from standard v2.3 + exec plan
**Target Output:** `/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md`

---

## A. Exec Plan Structure Summary

**Source:** `VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md`

- **9 phases** (P0–P8): Safety → Schema → UX → Agent Config → Pipeline → Routing → Collaboration → Security → Operational Excellence
- **56 gates** total (not 67 as originally estimated — see per-phase counts below)
- **14 OQ (Operational Quarantine) criteria** — minimum acceptance bar across all phases
- **29 roadmap requirements** mapped 1:1 with no-drop coverage matrix

### Per-Phase Breakdown

| Phase | Name | Tasks | Gates | Touches API? |
|-------|------|-------|-------|-------------|
| P0 | Safety & Perimeter | 9 | 12 | Yes (admin endpoints) |
| P1 | Canonical Schema + Contract | 7 | 12 | Yes (schema expansion) |
| P2 | Quarantine UX | 8 | 13 | Yes (query params) |
| P3 | Email Triage Agent Config | 4 | 7 | No (handoff doc only) |
| P4 | Quarantine→Deal Pipeline | 5 | 9 | Yes (undo-approve endpoint) |
| P5 | Auto-Routing | 4 | 8 | Yes (routing check, threads) |
| P6 | Collaboration Contract | 5 | 9 | Yes (delegation API, 3 new tools) |
| P7 | Security & Hardening | 6 | 7 | No (infra only) |
| P8 | Operational Excellence Gate | 6 | 7 | No (SLOs, monitoring) |

---

## B. The 9 Patches Applied by Orchestrator

These are modifications applied to the original roadmap during plan synthesis:

| # | Patch | Rationale |
|---|-------|-----------|
| 1 | Auth duplication split: P0-T6 = Bearer (code), P7-T1 = CF Access (infra), P7-T2 = verification | Defense in depth — immediate code fix vs later infra work |
| 2 | `email_body_snippet` made required (not optional) in bridge tool | Inline preview avoids runtime dependency on Gmail API |
| 3 | `confidence FLOAT` + `received_at TIMESTAMPTZ` added to migration 033 | Missing from original roadmap; needed for Phase 2 filtering |
| 4 | G2-05 fixed (removed premature Phase 4 reference) | Gate referenced work not yet done at Phase 2 |
| 5 | Backward compatibility sub-task added to P1-T6 (source-aware validation) | `email_sync` items need legacy validation; `langsmith_shadow` items need strict |
| 6 | `COALESCE(email_subject, subject)` added to P2-T1 and P1-T3 | Handles both column names during migration transition |
| 7 | P0-T5 upgraded from verify-only to verify-and-wire | Correlation ID must be wired, not just verified to exist |
| 8 | Phase 3 handoff artifact + parallel execution note added | Zaks implements LangSmith agent; Claude produces spec at P1 completion |
| 9 | Migration number safety check (P0-T9) added | Pre-flight prevents migration collisions |

---

## C. 7 Resolved Decisions (All Final)

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| D1: Security Perimeter | Both layers: Bearer (P0) + CF Access (P7) | Defense in depth |
| D2: Preview Storage | Inline `email_body_snippet` as required column | No runtime dependency |
| D3: Quarantine Schema | Add columns to existing `quarantine_items` table | Simpler, fewer JOINs |
| D4: Phase 3 Execution | Zaks implements in LangSmith; Claude produces handoff spec | Parallel execution |
| D5: Escalate Semantics | Status flag only — no operator assignment | Simpler, no user table |
| D6: Schema Version | Reject unknown versions (`["1.0.0"]` allowed set) | Prevents silent drift |
| D7: langsmith_live Gate | Feature flag toggle after Phase 8 burn-in | Graduation = flag flip |

---

## D. Bridge Is Now at New Path

**Critical context for all file path references in the mission prompt:**

The MCP bridge was moved from `/home/zaks/scripts/agent_bridge/` to `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/` as a prerequisite (Item 2 of pre-execution plan, completed 2026-02-14).

- `mcp_server.py` was renamed to `server.py`
- Systemd unit updated to new paths
- `.env` secrets remain at `/home/zaks/scripts/agent_bridge/.env` (referenced via EnvironmentFile)
- Bridge is running and healthy from new path

**All exec plan references to bridge files must use the NEW path:**
- `apps/agent-api/mcp_bridge/server.py` (not `scripts/agent_bridge/mcp_server.py`)
- `apps/agent-api/mcp_bridge/agent_contract.py`
- `apps/agent-api/mcp_bridge/config.py`

---

## E. 16 Contract Surfaces (Not 14)

Two new surfaces were added as prerequisites (Item 3, completed 2026-02-14):

| Surface | Boundary | Validator |
|---------|----------|-----------|
| S15: MCP Bridge Tool Interface | Bridge tool implementations ↔ tool-schemas.json | `make validate-surface15` |
| S16: Email Triage Injection | LangSmith → Bridge → Backend quarantine ingestion | `make validate-surface16` |

The mission prompt MUST reference all 16 surfaces where applicable. Specifically:
- **S1, S2:** Phases 0, 1, 2, 4, 5, 6 (backend API changes)
- **S6:** Phases 1, 6 (MCP tool changes)
- **S8:** Phase 1 (agent config spec)
- **S9:** Phase 2 (dashboard UX)
- **S10:** Phases 0, 7 (dependency health after service changes)
- **S11:** Phases 0, 7 (env variables: ZAKOPS_ENV, feature flags)
- **S12:** Phases 1, 4, 5 (error handling changes)
- **S13:** Phases 1, 2, 4, 8 (test coverage)
- **S14:** Phase 8 (performance budget, SLOs)
- **S15:** Phases 0, 1, 6 (bridge tool changes)
- **S16:** Phases 0, 1, 4, 5 (injection pipeline changes)

---

## F. Applicable Improvement Areas (IAs)

The following IAs from Mission Prompt Standard v2.3 apply to this mission:

| IA | Name | How It Applies |
|----|------|---------------|
| IA-1 | Context Checkpoints | 9 phases, 900+ line plan → needs checkpoint at Phase 4 boundary |
| IA-2 | Crash Recovery | 9 phases → mandatory crash recovery section |
| IA-7 | Rollback Per Phase | Already in exec plan — each phase has explicit rollback |
| IA-10 | Test Naming Convention | Phase 1 golden payload test, Phase 8 load test need functional keywords |
| IA-14 | Multi-Agent Parity | Phase 3 involves LangSmith agent config — cross-agent consideration |
| IA-15 | Governance Surface Validation | Newly adopted (v2.3) — ALL phases must reference affected surfaces |

---

## G. Deep Q&A Answers (7 Topics)

### 1. Backfill Strategy
No data migration for existing quarantine items. New columns (`confidence`, `received_at`, `email_body_snippet`, `schema_version`, etc.) are all nullable with defaults. Existing `email_sync` items continue with legacy validation. `langsmith_shadow` items require strict validation (all new fields required). This is enforced via source-aware validation in P1-T6.

### 2. Testing Approach
- **Golden Payload Test (P1-T7):** Fully-populated injection → verify all fields stored → verify rendered in UI
- **Concurrency Tests:** P0-T4 (5 concurrent identical message_ids → 1 record), P2-T3 (2 simultaneous approvals → 1 success + 409)
- **Load Test (P8-T3):** 100→500 emails/day, 3–5 concurrent operators, 50-email bursts
- **Evidence scripts throughout** — one-shot verification, not committed to repo
- Recommended: commit `tests/fixtures/golden_quarantine_payload.json` for regression

### 3. Coordination Between Services
- **Bridge reads feature flags** from backend API (60s TTL cache) — DB is authoritative
- **Phase 3 handoff:** `LANGSMITH_AGENT_CONFIG_SPEC.md` delivered at P1 completion; Zaks implements LangSmith agent in parallel with Phase 2
- **Phase 6 delegation:** Structured tasks table with state machine (pending → queued → executing → completed | dead-letter)

### 4. Rollback Strategy
Each phase has explicit rollback. Key pattern:
- **P0:** Drop migration 032, revert main.py + bridge
- **P1:** Run 033_rollback.sql, revert main.py + server.py
- **P2:** Revert dashboard + backend, run migration rollback
- **P5+:** Flag-gated — set `auto_route=false` (no code revert needed)
- **P6:** Set `delegate_actions=false`, `send_email_enabled=false`

### 5. Monitoring & Observability
- Correlation_id propagates end-to-end: quarantine → deal_transitions → deal_events → outbox → logs
- Phase 8 SLOs: injection <30s p95, UI load <2s p95, approve→deal <3s p95, 99.5% uptime
- Feature flag changes logged in `deal_events` (event_type='flag_changed')
- Health checks every 60s; queue depth alerts; kill switch activation alert

### 6. Spec Sync Timing
After each phase touching API boundaries:
```
make update-spec → make sync-types → make sync-backend-models → npx tsc --noEmit
```
This chain is a **hard gate** (not informational). Applies after: P0, P1, P2, P4, P5, P6.

### 7. Phase 0 Is Already Complete
Phase 0 is being executed as part of the prerequisite plan (Item 7). When the mission prompt is generated, Phase 0 should still be documented (for completeness and rollback reference) but the mission may note that Phase 0 gates are pre-verified.

---

## H. Instructions for Codex

1. Read `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` (v2.3)
2. Read `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md`
3. Read `/home/zaks/bookkeeping/docs/VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md`
4. Read this handoff note
5. Generate mission prompt following standard v2.3 structure:
   - Preamble (reference builder infra, 16 surfaces, 10 hooks, 7 rules)
   - Phase structure matching exec plan (P0–P8)
   - Gates from exec plan as phase gates
   - OQ criteria as acceptance criteria
   - `make sync-*` as mandatory phase gates (per IA-15)
   - Surface 9 compliance for Phase 2
   - All 16 surfaces referenced where applicable (see section E)
   - Crash recovery section (per IA-2)
   - Context checkpoint at Phase 4 boundary (per IA-1)
6. Validate with: `bash tools/infra/validate-mission.sh MISSION-ET-VALIDATION-001.md`
7. Output to: `/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md`

---

*End of handoff note*
