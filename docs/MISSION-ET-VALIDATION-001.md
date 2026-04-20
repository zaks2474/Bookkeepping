# MISSION: ET-VALIDATION-001
## Email Triage Operational Validation Roadmap Execution
## Date: 2026-02-15
## Classification: Full-Stack Platform Validation and Operational Readiness
## Prerequisite: Bridge relocation + contract surface expansion prerequisites completed on 2026-02-14
## Successor: QA-ET-VALIDATION-001

---

## Builder Preamble

Per builder baseline loading, this mission references existing operating context rather than repeating it: `CLAUDE.md`, `MEMORY.md`, 10 hooks, 7 path-scoped rules, deny rules, and delegated agents. This mission extends governance tracking to 16 contract surfaces (including S15 and S16), preserves the standing 7-rule infrastructure discipline, and enforces mission-specific deviations and sequencing below.

Mission-specific preamble constraints:
- MCP bridge file paths are canonical at `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/`.
- Bridge entry point is `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py`.
- Do not reference legacy bridge code path `/home/zaks/scripts/agent_bridge/mcp_server.py` for implementation work.
- Phase 0 remains documented for rollback/governance completeness even if portions are pre-verified.

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If execution crashes or context becomes unreliable, resume with this sequence:

```bash
# 1) Determine last completed phase checkpoint
cat /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md

# 2) Check working trees before resuming
git -C /home/zaks/zakops-backend status
git -C /home/zaks/zakops-agent-api status

# 3) Re-establish validation baseline
cd /home/zaks/zakops-agent-api && make validate-local

# 4) Re-verify bridge health from canonical path
cd /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge && ls -l server.py
```

Resume from the first incomplete phase gate. Do not re-run completed phase gates unless rollback was explicitly triggered.

---

## Mission Objective

Execute the approved 9-phase Email Triage validation roadmap to move quarantine ingestion from "integrated but not operational" to an operationally gated, auditable, and rollback-safe workflow spanning backend, dashboard, bridge, and LangSmith configuration boundaries.

This is an execution mission. It is not a redesign of ZakOps architecture, and it is not a migration of bridge location (already completed prerequisite). It is also not a replacement of existing lifecycle primitives that already work (idempotency, outbox, transition ledger); those are verified and wired into new flow requirements.

Source artifacts:
- `/home/zaks/bookkeeping/docs/CODEX-HANDOFF-ET-VALIDATION-001.md`
- `/home/zaks/bookkeeping/docs/VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md`

---

## Context

### Ground truth that must be preserved

1. Quarantine primitives, dedup, outbox, correlation middleware, and approval lifecycle artifacts already exist and must not regress.
2. Dashboard quarantine page exists but lacks operational UX completeness for triage decisions and multi-operator safety.
3. Bridge currently requires schema expansion and strict contract alignment to eliminate "Preview not found" and field drift.
4. Resolved architecture decisions are final for this mission: dual-layer security, inline preview storage, additive schema migration, source-aware validation, and flag-gated graduation.

### 9 synthesis patches already accepted in plan generation

1. Auth split enforced by phase: Layer 2 Bearer restoration in Phase 0, Layer 1 Cloudflare Access in Phase 7.
2. `email_body_snippet` is required for bridge payloads.
3. `confidence` and `received_at` are first-class columns in schema migration.
4. Phase 2 gate dependency ordering corrected.
5. Source-aware backward compatibility required for `email_sync` vs `langsmith_*` callers.
6. `COALESCE(email_subject, subject)` is mandatory for transitional rendering.
7. Correlation ID requirement is verify-and-wire, not verify-only.
8. Phase 3 requires handoff artifact and parallel execution note.
9. Migration-number safety preflight is mandatory before SQL file creation.

### Bridge relocation context (mandatory path correction)

- Canonical bridge runtime path: `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/`
- Canonical code file: `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py`
- Supporting files: `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py`, `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/config.py`
- Bridge `.env` remains at `/home/zaks/scripts/agent_bridge/.env` via systemd `EnvironmentFile`

---

## Glossary

| Term | Definition |
|------|-----------|
| OQ Criteria | Operational Quarantine acceptance floor (OQ-01 through OQ-14); mission cannot pass without all OQ criteria met |
| S15 | MCP Bridge Tool Interface contract surface; bridge implementation must match tool schema validators |
| S16 | Email Triage Injection contract surface; LangSmith output must remain schema-valid through bridge to backend ingestion |
| Source-aware validation | Strict required fields for `langsmith_*` payloads while preserving legacy compatibility for `email_sync` |
| Hard gate chain | Mandatory sync chain after API-touching phases: `make update-spec -> make sync-types -> make sync-backend-models -> npx tsc --noEmit` |
| Context checkpoint | Mid-mission continuity point at Phase 4 boundary to avoid context drift across long execution |

---

## Contract Surface Matrix (S1-S16)
<!-- Adopted from Improvement Area IA-15 -->

| Surface | Boundary | Applies In This Mission | Phases | Validation Command |
|---------|----------|-------------------------|--------|--------------------|
| S1 | Backend -> Dashboard | Yes | P0, P1, P2, P4, P5, P6 | `cd /home/zaks/zakops-agent-api && make sync-types` |
| S2 | Backend -> Agent SDK | Yes | P0, P1, P2, P4, P5, P6 | `cd /home/zaks/zakops-agent-api && make sync-backend-models` |
| S3 | Agent OpenAPI | Conditional (only if agent API schema changes) | P1, P6 (if touched) | `cd /home/zaks/zakops-agent-api && make update-agent-spec` |
| S4 | Agent -> Dashboard | Conditional | P6 (if agent contracts exposed) | `cd /home/zaks/zakops-agent-api && make sync-agent-types` |
| S5 | RAG -> Backend SDK | No | N/A | `cd /home/zaks/zakops-agent-api && make sync-rag-models` (not expected) |
| S6 | MCP Tools | Yes | P1, P6 | `cd /home/zaks/zakops-agent-api && make validate-surface6` |
| S7 | SSE Events | Conditional (only if event schema touched) | P6 (if touched) | reference schema gate |
| S8 | Agent Config | Yes | P1, P3 | `cd /home/zaks/zakops-agent-api && make validate-agent-config` |
| S9 | Design System -> Dashboard | Yes | P2 | `cd /home/zaks/zakops-agent-api && make validate-surface9` |
| S10 | Dependency Health | Yes | P0, P7 | `cd /home/zaks/zakops-agent-api && make validate-surface10` |
| S11 | Env Registry | Yes | P0, P7 | `cd /home/zaks/zakops-agent-api && make validate-surface11` |
| S12 | Error Taxonomy | Yes | P1, P4, P5 | `cd /home/zaks/zakops-agent-api && make validate-surface12` |
| S13 | Test Coverage | Yes | P1, P2, P4, P8 | `cd /home/zaks/zakops-agent-api && make validate-surface13` |
| S14 | Performance Budget | Yes | P8 | `cd /home/zaks/zakops-agent-api && make validate-surface14` |
| S15 | MCP Bridge Tool Interface | Yes | P0, P1, P6 | `cd /home/zaks/zakops-agent-api && make validate-surface15` |
| S16 | Email Triage Injection | Yes | P0, P1, P4, P5 | `cd /home/zaks/zakops-agent-api && make validate-surface16` |

---

## Architectural Constraints

- **Single state choke point**: all deal state transitions continue through `transition_deal_state()`; no direct state mutation shortcuts.
- **Promise discipline**: dashboard multi-fetch remains `Promise.allSettled` with typed fallbacks; `Promise.all` is forbidden for data-fetch critical paths.
- **Proxy contract**: Next.js middleware remains the `/api/*` boundary and returns JSON 502 on backend failures.
- **Phase-gated sync chain is mandatory**: after every API-touching phase (P0, P1, P2, P4, P5, P6), run `make update-spec -> make sync-types -> make sync-backend-models -> npx tsc --noEmit` as gate criteria.
- **Bridge path authority**: implementation references must use `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py`; legacy bridge file path is not valid for edits.
- **Generated file protection**: do not edit generated artifacts directly; regenerate via contract surface commands.
- **Port safety**: port 8090 is decommissioned and forbidden in all docs, tests, and runtime checks.
- **Surface 9 strictness for quarantine UX**: expected degradation logs as `console.warn`; unexpected conditions as `console.error`.
- **Server-side counts only**: list/detail aggregate counts must be server-provided, never client `.length` approximations.

---

## Anti-Pattern Examples

### WRONG: Keeping hardcoded source type in bridge
```python
payload["source_type"] = "langsmith_shadow"
```

### RIGHT: Flag-controlled source type
```python
payload["source_type"] = "langsmith_shadow" if shadow_mode else "langsmith_live"
```

### WRONG: Transitional subject drift
```sql
SELECT subject FROM zakops.quarantine_items;
```

### RIGHT: Backward-compatible subject resolution
```sql
SELECT COALESCE(email_subject, subject) AS display_subject
FROM zakops.quarantine_items;
```

### WRONG: Phase gate without sync chain after API edits
```bash
# only local unit tests
pytest
```

### RIGHT: Mandatory cross-surface chain
```bash
make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Bridge schema expansion ships but LangSmith payload assembly lags | HIGH | Injection failures or null-heavy records | Phase 1 handoff artifact + Phase 3 deterministic payload gate (G3-06) |
| 2 | UI fixes rely on new columns but migration order is wrong | MEDIUM | Detail/list regressions and empty fields | Phase 0 migration-number safety check + Phase 1 gate G1-01/G1-02 |
| 3 | Auth appears restored in app layer but edge layer remains open | MEDIUM | External injection risk | Dual-layer verification in Phase 7 Gate G7-01/G7-02 |
| 4 | Auto-routing introduces duplicate or mislinked deals | MEDIUM | Data integrity and operator trust loss | Phase 4 duplicate prevention and Phase 5 routing gates G5-02/G5-03/G5-08 |
| 5 | Long execution causes context loss and skipped surfaces | HIGH | Hidden contract drift | Context checkpoint after Phase 4 + explicit S1-S16 phase gates |

---

## Phase 0 - Safety and Perimeter
**Complexity:** L
**Estimated touch points:** 6 files plus evidence scripts

**Purpose:** Establish feature-flag control plane, kill switch behavior, migration safety preflight, correlation trace completeness, and Layer 2 bridge auth restoration.

### Blast Radius
- **Services affected:** `/home/zaks/zakops-backend`, `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge`
- **Pages affected:** Admin controls and quarantine ingress behavior
- **Downstream consumers:** LangSmith bridge caller, quarantine ingestion pipeline

### Tasks
- P0-01: Implement feature flags table + runtime admin API (`shadow_mode`, `auto_route`, `delegate_actions`, `send_email_enabled`, `email_triage_writes_enabled`) in `/home/zaks/zakops-backend`.
- P0-02: Wire kill switch before write path execution in quarantine ingestion and future delegated writes.
- P0-03: Replace hardcoded bridge source type with runtime `shadow_mode` resolution in `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py`.
- P0-04: Verify existing idempotency primitive with concurrent injection evidence (5 identical IDs => exactly 1 record).
- P0-05: Verify-and-wire correlation ID propagation end-to-end, generating fallback correlation IDs when caller omits one.
- P0-06: Remove bridge auth bypass and restore Bearer enforcement for `/mcp`, `/sse`, `/messages` paths.
- P0-07: Create `/home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md` with dual-token operational steps.
- P0-08: Add and log `ZAKOPS_ENV` environment model in backend startup.
- P0-09: Preflight migration-number safety check before creating SQL files.

### Decision Tree
- **IF** Phase 0 was pre-verified in prerequisite execution and evidence still matches current HEAD -> keep artifacts and only rerun gates.
- **ELSE IF** evidence drift is detected -> rerun full Phase 0 implementation tasks before proceeding.
- **ELSE** stop and resolve baseline inconsistency.

### Rollback Plan
1. Revert feature flag migration and backend bridge changes.
2. Restore prior bridge auth behavior only if temporary rollback is explicitly required by incident response.
3. Re-run `cd /home/zaks/zakops-agent-api && make validate-local`.

### Gate P0
- G0-01: Feature flags table exists with 5 flags, all queryable via API.
- G0-02: `shadow_mode=ON` results in `source_type=langsmith_shadow` on injected items.
- G0-03: Unknown `source_type` is rejected with 400 and clear error text.
- G0-04: Kill switch ON makes `zakops_inject_quarantine` return 503 within 1s while reads continue.
- G0-05: Kill switch OFF restores normal write behavior.
- G0-06: 5 concurrent identical `message_id` injections produce exactly 1 record.
- G0-07: `correlation_id` appears on quarantine item and log entries.
- G0-08: `correlation_id` is returned in tool response payload.
- G0-09: MCP bridge rejects unauthenticated requests after bypass removal.
- G0-10: Key rotation procedure is documented with explicit commands.
- G0-11: Curl to bridge without auth returns 401/403, never 200.
- G0-12: `langsmith_live` does not appear during shadow pilot.
- `cd /home/zaks/zakops-agent-api && make validate-surface10 && make validate-surface11 && make validate-surface15 && make validate-surface16`
- `cd /home/zaks/zakops-agent-api && make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Phase 1 - Canonical Schema and Contract Enforcement
**Complexity:** XL
**Estimated touch points:** 8-14 files across DB, backend models, and bridge contract

**Purpose:** Expand quarantine schema to required operational fields, enforce strict contract boundaries, and eliminate preview/filepath coupling.

### Blast Radius
- **Services affected:** Backend DB/API, bridge ingestion tool schema
- **Pages affected:** Quarantine list/detail rendering fidelity
- **Downstream consumers:** LangSmith payload assembly, dashboard data consumers

### Tasks
- P1-01: Add migration 033 schema expansion and rollback SQL for new quarantine columns (`email_body_snippet`, `triage_summary`, `source_thread_id`, `schema_version`, `confidence`, `received_at`, etc.).
- P1-02: Update QuarantineCreate validation with `extra='forbid'`, source-aware required fields, and known `schema_version` allowlist.
- P1-03: Update QuarantineResponse to include expanded fields and computed subject display via `COALESCE(email_subject, subject)`.
- P1-04: Update POST ingestion mapping (`source_message_id -> message_id`) and write all expanded columns.
- P1-05: Remove preview filesystem dependency by returning inline snippet/full-body metadata from API.
- P1-06: Expand bridge tool contract to full schema and local fail-fast validation.
- P1-07: Execute golden payload test proving inject -> DB -> UI continuity.

### Rollback Plan
1. Execute 033 rollback SQL.
2. Revert backend and bridge schema contract changes.
3. Re-run `cd /home/zaks/zakops-agent-api && make validate-local` and quarantine smoke checks.

### Gate P1
- G1-01: All new DB columns exist (`\\d zakops.quarantine_items` verification).
- G1-02: `version` column exists with `DEFAULT 1`.
- G1-03: Bridge tool exposes expanded schema (20+ parameters).
- G1-04: `source_message_id` maps to `message_id` at ingestion boundary.
- G1-05: Tool rejects missing required fields and names them in error output.
- G1-06: Tool rejects extra/unknown keys (strict validation).
- G1-07: Tool rejects unknown `schema_version` with 400.
- G1-08: `email_body_snippet` always populated; preview missing state eliminated.
- G1-09: Golden flow verified: inject -> DB -> list -> detail.
- G1-10: Five complete-data test items render correctly in UI.
- G1-11: `source_type` uses canonical constants only.
- G1-12: Dedup still holds under expanded schema.
- `cd /home/zaks/zakops-agent-api && make validate-surface6 && make validate-agent-config && make validate-surface12 && make validate-surface13 && make validate-surface15 && make validate-surface16`
- `cd /home/zaks/zakops-agent-api && make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Phase 2 - Quarantine UX Operationalization
**Complexity:** XL
**Estimated touch points:** 6-12 files

**Purpose:** Make quarantine workflows operational for multi-operator triage with locking, edits, escalations, and filter/sort usability.

### Blast Radius
- **Services affected:** Backend process/query endpoints, dashboard quarantine route
- **Pages affected:** `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
- **Downstream consumers:** Deal promotion workflows and operator QA process

### Tasks
- P2-01: Fix list view to render canonical operational fields (subject, sender, classification, urgency, confidence, source_type, received_at).
- P2-02: Fix detail view sections, stale-data handling, and inline preview rendering.
- P2-03: Add optimistic locking via version checks and 409 conflict handling.
- P2-04: Add escalate action (`status=escalated`) and "Needs Review" filter support.
- P2-05: Implement approve-with-edits corrections persistence.
- P2-06: Enforce reject reason requirement in UI and backend policy.
- P2-07: Implement filter/sort controls including shadow isolation behavior.
- P2-08: Add bulk approve/reject with per-item validation and partial success reporting.

### Rollback Plan
1. Revert dashboard quarantine route changes and backend process/list changes.
2. Roll back escalate migration if introduced.
3. Re-run `cd /home/zaks/zakops-agent-api && make validate-local`.

### Gate P2
- G2-01: List view renders `email_subject`, `sender_name`, `classification`, `urgency`, `confidence`, `source_type`, `received_at`.
- G2-02: No \"Unknown subject\" for items with populated `email_subject`.
- G2-03: Detail view shows all sections with real data and no preview-missing fallback.
- G2-04: Selecting an item loads matching detail with no stale carryover.
- G2-05: Approve creates all 5 lifecycle artifacts.
- G2-06: Approve-with-edits stores operator corrections with originals.
- G2-07: Reject requires reason (policy enforced in UI and backend).
- G2-08: Escalate moves item into \"Needs Review\" filter.
- G2-09: Concurrent approve race yields one success and one 409 conflict.
- G2-10: Filters support `source_type`, `classification`, `urgency`, `confidence threshold`.
- G2-11: `langsmith_shadow` items do not leak into other source filters.
- G2-12: Sorting supports `received_at`, `urgency`, `confidence`.
- G2-13: Bulk approve/reject supports per-item validation and partial success output.
- `cd /home/zaks/zakops-agent-api && make validate-surface9 && make validate-surface13`
- `cd /home/zaks/zakops-agent-api && make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Phase 3 - Email Triage Agent Configuration
**Complexity:** M
**Estimated touch points:** 1 handoff artifact + LangSmith configuration records

**Purpose:** Deliver a deterministic LangSmith configuration package aligned to backend and bridge schema contract.

### Blast Radius
- **Services affected:** LangSmith Agent Builder configuration and bridge contract assumptions
- **Pages affected:** None directly
- **Downstream consumers:** Injection payload correctness, calibration/eval reporting

### Tasks
- P3-01: Deliver system prompt rewrite with strict classification and output constraints.
- P3-02: Deliver sub-agent configuration spec (`triage_classifier`, `entity_extractor`, `policy_guard`, `document_analyzer`).
- P3-03: Deliver deterministic payload assembly spec mapping sub-agent outputs to tool schema.
- P3-04: Create collaborative 20+ item calibration eval set with baseline metrics.

### Decision Tree
- **IF** Phase 1 schema is not frozen -> stop Phase 3 and resolve schema drift first.
- **ELSE** execute Phase 3 in parallel with Phase 2.

### Rollback Plan
1. Revert LangSmith prompt/sub-agent configuration to previous known-good version.
2. Archive invalid eval runs.
3. Keep backend and dashboard code unchanged.

### Gate P3
- G3-01: System prompt is deployed in LangSmith.
- G3-02: Ten test emails show correct behavior by class (deal signals full extraction, newsletters minimal, spam discarded).
- G3-03: Zero required-field NULLs on injected items.
- G3-04: `triage_summary` present and meaningful on every item.
- G3-05: Confidence scoring calibrated (not collapsed to a single constant).
- G3-06: Deterministic payload verified across 20 injections with identical key sets.
- G3-07: Eval set exists with 20+ labeled samples and baseline scores.
- `cd /home/zaks/zakops-agent-api && make validate-agent-config`
- `cd /home/zaks/zakops-agent-api && make validate-local` (non-blocking for LangSmith-only artifacts, but still required for mission continuity)

---

## Phase 4 - Quarantine to Deal Promotion Pipeline
**Complexity:** L
**Estimated touch points:** 4-8 files

**Purpose:** Guarantee artifact completeness on approve flow, prevent duplicate deals, and add controlled undo/traceability.

### Blast Radius
- **Services affected:** Backend promotion path, deal timeline/event pipeline, dashboard deals views
- **Pages affected:** Quarantine approvals, deals list/detail indicators
- **Downstream consumers:** Timeline analytics, outbox consumers, audit pipelines

### Tasks
- P4-01: Verify existing approve transaction produces all 5 lifecycle artifacts and correlation continuity.
- P4-02: Add duplicate prevention using `source_thread_id` against `zakops.email_threads`.
- P4-03: Register thread-deal mapping for newly promoted deals.
- P4-04: Add admin-only undo approval endpoint and UI controls.
- P4-05: Add "From Quarantine" source indicator in deals views.

### Rollback Plan
1. Revert promotion logic changes and undo endpoint/UI.
2. Revert thread mapping logic if incorrect.
3. Re-run `cd /home/zaks/zakops-agent-api && make validate-local`.

### Gate P4
- G4-01: Approve action yields all 5 lifecycle artifacts with query evidence per table.
- G4-02: Operator corrections flow into created deal values.
- G4-03: Duplicate prevention attaches same-thread items to existing deals.
- G4-04: Partial failure rolls back transaction cleanly (no orphan state).
- G4-05: Deal timeline includes quarantine context and `correlation_id`.
- G4-06: `source_thread_id` is registered in `email_threads` on approve.
- G4-07: Undo approval archives deal and restores quarantine item to pending.
- G4-08: Deals view shows source indicator for quarantine-promoted records.
- G4-09: Batch of five approvals produces correct artifact outputs.
- `cd /home/zaks/zakops-agent-api && make validate-surface12 && make validate-surface13 && make validate-surface16`
- `cd /home/zaks/zakops-agent-api && make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Context Checkpoint (Phase 4 Boundary)
<!-- Adopted from Improvement Area IA-1 -->

After Gate P4 and before Phase 5:
- Summarize completed tasks and outstanding risks into `/home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md`.
- Commit or stash coherent intermediate work per repository.
- If context is constrained, resume with Phase 5 in a fresh continuation using the checkpoint artifact.

---

## Phase 5 - Auto-Routing
**Complexity:** L
**Estimated touch points:** 4-9 files

**Purpose:** Introduce feature-flagged thread-aware routing that can bypass quarantine safely when match confidence is unambiguous.

### Blast Radius
- **Services affected:** Backend ingest route, bridge response contract, dashboard conflict workflows
- **Pages affected:** Quarantine conflict UI, deal thread controls
- **Downstream consumers:** Timeline events and routing analytics

### Tasks
- P5-01: Add pre-injection routing decision in backend ingest path with explicit `routing_reason` output.
- P5-02: Implement conflict resolution UI for multi-match thread scenarios.
- P5-03: Implement operator thread relinking controls and backend endpoints.
- P5-04: Ensure bridge tool response always includes routing metadata.

### Rollback Plan
1. Set `auto_route=false` immediately to deactivate behavior.
2. Revert code changes only if required after flag rollback.
3. Re-run `cd /home/zaks/zakops-agent-api && make validate-local`.

### Gate P5
- G5-01: `auto_route=OFF` sends all emails to quarantine.
- G5-02: `auto_route=ON` plus single thread match routes to deal timeline.
- G5-03: `auto_route=ON` plus multiple matches quarantines with conflict reason.
- G5-04: `auto_route=ON` with no match follows normal quarantine path.
- G5-05: `routing_reason` appears in every tool response.
- G5-06: Conflict resolution UI renders conflicting deal options.
- G5-07: Operators can add/remove/move thread links.
- G5-08: End-to-end follow-up email after approval lands in existing deal timeline.
- `cd /home/zaks/zakops-agent-api && make validate-surface12 && make validate-surface16`
- `cd /home/zaks/zakops-agent-api && make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Phase 6 - Collaboration Contract
**Complexity:** XL
**Estimated touch points:** 7-12 files

**Purpose:** Implement structured asynchronous delegation between ZakOps and Email Triage with explicit state machine and safety flags.

### Blast Radius
- **Services affected:** Backend task APIs, bridge tools, dashboard deal task management
- **Pages affected:** Deal detail task management surfaces
- **Downstream consumers:** Delegated task event stream and dead-letter operations

### Tasks
- P6-01: Add delegated tasks migration and state machine (`pending -> queued -> executing -> completed|failed|dead_letter`).
- P6-02: Implement delegation APIs and feature-flag gating (`delegate_actions`).
- P6-03: Enforce separate outbound-email gate (`send_email_enabled`) with operator confirmation.
- P6-04: Add bridge tools (`zakops_get_deal_status`, `zakops_list_recent_events`, `zakops_report_task_result`).
- P6-05: Add dashboard delegated task management views and dead-letter visibility.

### Rollback Plan
1. Disable delegation via flags (`delegate_actions=false`, `send_email_enabled=false`).
2. Revert schema/API/tool/view code only if needed beyond flag shutdown.
3. Re-run `cd /home/zaks/zakops-agent-api && make validate-local`.

### Gate P6
- G6-01: `delegated_tasks` table exists with declared state machine.
- G6-02: Retry flow supports failed -> re-queued up to `max_attempts` -> `dead_letter`.
- G6-03: `delegate_actions` flag controls delegation availability.
- G6-04: `send_email_enabled` independently gates outbound email behavior.
- G6-05: Email sending path requires explicit operator confirmation.
- G6-06: Structured feedback is stored for every task.
- G6-07: Task outcomes are visible in deal timeline.
- G6-08: Dead-letter tasks surface clearly to operators.
- G6-09: `zakops_get_deal_status` and `zakops_list_recent_events` tools function correctly.
- `cd /home/zaks/zakops-agent-api && make validate-surface6 && make validate-surface15`
- `cd /home/zaks/zakops-agent-api && make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Phase 7 - Security and Hardening
**Complexity:** M
**Estimated touch points:** 3-7 files plus infra config

**Purpose:** Complete defense-in-depth with edge auth, key rotation resilience, log redaction, retention policies, and failure-mode tests.

### Blast Radius
- **Services affected:** Bridge ingress edge and app auth, backend policy endpoints, operational logs
- **Pages affected:** Admin/security operations surfaces
- **Downstream consumers:** Security posture and incident response processes

### Tasks
- P7-01: Add Cloudflare Access service-token protection for bridge edge ingress.
- P7-02: Verify dual-layer auth matrix (no CF -> 403, CF only -> 401, CF + Bearer -> 200).
- P7-03: Implement/test dual-token key rotation window in bridge runtime.
- P7-04: Audit logs for secret redaction compliance.
- P7-05: Document retention/PII policy and add admin purge endpoint.
- P7-06: Audit failure handling (backend unavailable, partial transaction, bridge restart reconnect).

### Rollback Plan
1. Disable CF Access integration if emergency access restoration is required.
2. Revert bridge key-rotation changes.
3. Keep Layer 2 auth intact unless incident commander directs otherwise.

### Gate P7
- G7-01: Bridge is protected by Layer 1 CF Access plus Layer 2 Bearer auth.
- G7-02: Security posture is not dependent on LangSmith secret interpolation behavior.
- G7-03: Key rotation dual-token workflow is tested end-to-end.
- G7-04: Logs contain no secret leakage.
- G7-05: Data retention policy is documented and enforceable.
- G7-06: Error handling paths are tested for declared failure modes.
- G7-07: Full correlation audit trail is preserved end-to-end.
- `cd /home/zaks/zakops-agent-api && make validate-surface10 && make validate-surface11`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Phase 8 - Operational Excellence Gate
**Complexity:** L
**Estimated touch points:** 2-6 operational artifacts plus test scripts

**Purpose:** Declare production readiness through SLOs, monitoring, load/DR validation, and shadow burn-in data integrity.

### Blast Radius
- **Services affected:** All mission services
- **Pages affected:** Operational dashboards and runbook workflows
- **Downstream consumers:** On-call readiness and release governance

### Tasks
- P8-01: Define and publish SLOs (injection latency, UI load, approve-to-deal, uptime).
- P8-02: Configure monitoring/alerting cadence and kill-switch alerts.
- P8-03: Execute load test profile (100-500 emails/day, burst traffic, 3-5 operators).
- P8-04: Execute backup and restore drills across all three databases.
- P8-05: Validate shadow measurement readiness dataset and scripts.
- P8-06: Run 7-day shadow burn-in and collect precision/recall dataset.

### Rollback Plan
1. Retain `shadow_mode=ON`, `auto_route=OFF`, `delegate_actions=OFF`, `send_email_enabled=OFF` until readiness issues are resolved.
2. Keep production graduation blocked and continue shadow-only operation.

### Gate P8
- G8-01: SLOs are defined and documented.
- G8-02: Monitoring and alerts are configured.
- G8-03: Load test is completed and SLOs are met under load.
- G8-04: Backup and restore tests are completed.
- G8-05: Seven-day shadow burn-in dataset is clean and measurable.
- G8-06: Production safety flags are set (`shadow_mode=ON`, `auto_route=OFF`, `delegate_actions=OFF`, `send_email_enabled=OFF`).
- G8-07: System is declared production-ready by gate criteria.
- `cd /home/zaks/zakops-agent-api && make validate-surface13 && make validate-surface14`
- `cd /home/zaks/zakops-agent-api && make validate-local`

---

## Dependency Graph

Phases execute in this order, with parallel lane at Phase 2 and Phase 3:

1. P0 -> P1
2. P1 -> (P2 and P3 in parallel)
3. P2 + P3 completion -> P4
4. P4 -> P5 -> P6 -> P7 -> P8

---

## Acceptance Criteria

The first 14 criteria are the mandatory OQ acceptance floor.

### AC-1
OQ-01 satisfied: LangSmith-injected items render with real subject (zero false "Unknown subject" when `email_subject` is populated).

### AC-2
OQ-02 satisfied: `email_body_snippet` always populated and rendered; zero "Preview not found" regressions.

### AC-3
OQ-03 satisfied: every approve action writes all 5 lifecycle artifacts.

### AC-4
OQ-04 satisfied: reject action requires reason in UI and backend validation.

### AC-5
OQ-05 satisfied: optimistic locking yields one success and one 409 in concurrent approve race.

### AC-6
OQ-06 satisfied: `langsmith_shadow` isolation preserved across filters.

### AC-7
OQ-07 satisfied: kill switch disables writes in under one second and preserves reads.

### AC-8
OQ-08 satisfied: unauthenticated bridge requests are blocked (401/403, never 200).

### AC-9
OQ-09 satisfied: schema contract rejects missing required fields with explicit errors.

### AC-10
OQ-10 satisfied: dedup under concurrency proves exactly one record for duplicate injections.

### AC-11
OQ-11 satisfied: triage summary is visible in detail panel for all applicable items.

### AC-12
OQ-12 satisfied: extraction evidence and field confidences are visible in detail UI.

### AC-13
OQ-13 satisfied: correlation ID trace is complete from quarantine through transitions/events/outbox.

### AC-14
OQ-14 satisfied: source type indicators visible in list and detail surfaces.

### AC-15
No-regression requirement satisfied: all applicable phase gates and sync/surface commands pass after final phase.

### AC-16
Bookkeeping and evidence requirement satisfied: mission checkpoints, evidence artifacts, and `/home/zaks/bookkeeping/CHANGES.md` updates are complete.

---

## Guardrails

1. Scope fence: execute only this mission; do not start follow-on QA remediation tasks.
2. Generated-file safety: regenerate contract outputs via make targets; do not hand-edit generated files.
3. WSL safety: strip CRLF from new shell scripts and correct ownership if sudo writes under `/home/zaks/`.
4. Governance safety: all affected surfaces (especially S10-S16) must have explicit phase gates.
5. Security safety: never log or commit secrets; use redacted evidence only.
6. Bridge path safety: all edits use canonical bridge path under `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/`.
7. Surface 9 safety: quarantine UI updates preserve design-system error/degradation logging semantics.
8. Contract chain safety: API changes are incomplete until sync chain and TypeScript compile gate passes.
9. Port safety: do not use or reference port 8090 in any script, config, or evidence.

---

## Executor Self-Check Prompts

- After discovery: Did I confirm canonical bridge paths and active contract surfaces before editing?
- After each API phase: Did I run the mandatory sync chain and record evidence output?
- Before phase completion: Are all gate IDs for this phase explicitly evidenced, not inferred?
- Before mission completion: Did I update checkpoint artifacts and `/home/zaks/bookkeeping/CHANGES.md`?

---

## File Paths Reference

### Files to Modify

| Path | Reason |
|------|--------|
| `/home/zaks/zakops-backend/main.py` | Quarantine schema/process, flags APIs, promotion routing, undo, retention endpoints |
| `/home/zaks/zakops-backend/src/core/feature_flags.py` | Feature flag retrieval/cache helper |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` | Bridge auth, source type wiring, expanded tool schema, routing response, delegation tools |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx` | Operational quarantine UX, lock handling, edits/escalation/bulk/filter/sort |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx` | Quarantine source indicator |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | Thread linking and delegated task visibility |

### Files to Create

| Path | Reason |
|------|--------|
| `/home/zaks/zakops-backend/db/migrations/032_feature_flags.sql` | Feature flag storage and seed defaults |
| `/home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2.sql` | Canonical schema expansion |
| `/home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2_rollback.sql` | Schema rollback path |
| `/home/zaks/zakops-backend/db/migrations/034_quarantine_escalate.sql` | Escalate status support |
| `/home/zaks/zakops-backend/db/migrations/035_delegated_tasks.sql` | Delegated task state machine |
| `/home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md` | Key lifecycle operational runbook |
| `/home/zaks/bookkeeping/docs/LANGSMITH_AGENT_CONFIG_SPEC.md` | Phase 3 handoff artifact for Zaks LangSmith configuration |
| `/home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md` | Crash recovery and phase continuity state |

### Files to Read Only

| Path | Reason |
|------|--------|
| `/home/zaks/bookkeeping/docs/CODEX-HANDOFF-ET-VALIDATION-001.md` | Mission synthesis constraints and patches |
| `/home/zaks/bookkeeping/docs/VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md` | Authoritative phase/task/gate source |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Mission structure standard v2.3 |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Skeleton and checklist shortcuts |
| `/home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json` | Contract drift checks |

---

## Stop Condition

Stop when all of the following are true:
- Gates P0 through P8 are evidenced as passed, including required surface validations and sync chain gates.
- AC-1 through AC-16 are satisfied with artifacts and command output.
- Mission checkpoint and bookkeeping artifacts are updated, and no unresolved blocker remains for QA successor mission.

Do not begin QA execution within this mission. Handoff only after execution evidence is complete.
