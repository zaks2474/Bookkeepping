# MISSION: INTEGRATION-PHASE1-BUILD-001
## LangSmith Integration Phase 1 — Feedback Loop & Intelligence Tools
## Date: 2026-02-16
## Classification: Feature Build — Cross-Service Integration
## Prerequisite: POST-MERGE-STABILIZE-001 (Complete 2026-02-15)
## Successor: INTEGRATION-PHASE2-BUILD-001 (Delegation Framework)

---

<!-- Adopted from Improvement Area IA-2 -->
## Crash Recovery

If resuming after a crash, run these commands to determine current state:
1. `git log --oneline -10` in `/home/zaks/zakops-agent-api` — check what's been committed
2. `make validate-local` — verify codebase health
3. `grep -c '@mcp.tool()' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` — count bridge tools (baseline=16, target=20)
4. `curl -sf http://localhost:8091/api/quarantine/feedback?sender_email=test@example.com | head -c 200` — if returns JSON, Phase 1 backend endpoints exist
5. `curl -sf http://localhost:9100/integration/manifest | head -c 200` — if returns JSON, Phase 3 manifest exists

---

## 1. Mission Objective

Build the Phase 1 "Feedback Loop" of the ZakOps + LangSmith Agent integration as defined in Integration Specification v1.0. This phase delivers:

- **4 new read-only backend endpoints** — triage feedback, broker listing, classification audit, sender intelligence
- **4 new MCP bridge tools** wrapping those endpoints for LangSmith consumption
- **Quarantine filter expansion** — add thread_id, sender, status, since_ts parameters to the existing list endpoint and bridge tool
- **Integration manifest endpoint** — `GET /integration/manifest` on the bridge for drift detection
- **Agent contract update** — system prompt and tool manifest reflecting all new tools

This is a **BUILD mission**. It does NOT implement the delegation framework (Phase 2), action leasing (Phase 2), or bi-directional communication (Phase 3). Those are successor missions.

**Source material:**
- Integration Specification v1.0: `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` (1,074 lines)
- Phase 1 build plan: Section 14, items 1-7
- Tool schemas: Section 4 (4.1-4.5)
- Quarantine filter expansion: Section 3.4

---

## 2. Context

The LangSmith Exec Agent currently has 16 MCP tools available through the bridge at :9100. Of these, only `zakops_inject_quarantine` is actively used for email triage. The agent identified a critical gap: it has **no feedback loop**. It injects emails but never learns whether they were approved, rejected, or rerouted. This makes its classification static — it cannot improve over time.

Through a 6-message architectural negotiation between Claude Code and the LangSmith agent (with Zak as intermediary), Integration Specification v1.0 was agreed. Phase 1 delivers the feedback loop — the foundation all subsequent phases depend on.

**Environment state (verified 2026-02-15):**
- All 7 services healthy
- 17/17 contract surfaces passing
- Backend at `apps/backend/` in monorepo (post-consolidation)
- Bridge at `apps/agent-api/mcp_bridge/server.py` (16 tools, lines 467-1356)
- Agent contract at `apps/agent-api/mcp_bridge/agent_contract.py` (system prompt lines 243-602)

**Prior deliverables that must NOT be regressed:**
- Quarantine injection pipeline (31-field schema, dedup, auto-routing, shadow mode)
- All 16 existing bridge tools functional
- Surface 15 and 16 validation passing

---

## 2b. Glossary

| Term | Definition |
|------|-----------|
| Bridge | MCP server at :9100 (`apps/agent-api/mcp_bridge/server.py`) exposing tools to LangSmith via FastMCP |
| Feedback loop | Mechanism for LangSmith agent to read back operator decisions and calibrate future classifications |
| Triage feedback | Per-sender approval/rejection history from quarantine decisions |
| Sender intelligence | Aggregated signals about an email sender: volume, approval rate, broker likelihood, deal associations |
| Classification audit | Time-windowed comparison of original agent classification vs final operator decision |
| Integration manifest | Bridge HTTP endpoint returning tool inventory, versions, and schema hashes for drift detection |
| Identity contract | Required fields on all LangSmith writes: executor_id, correlation_id, langsmith_run_id, langsmith_trace_url |
| Shadow mode | Feature flag `shadow_mode` controlling source_type: `langsmith_shadow` (testing) vs `langsmith_live` (production) |
| Cursor pagination | Opaque token-based pagination pattern (vs offset-based) for large result sets |

---

## 3. Architectural Constraints

- **Contract surface discipline** — New backend endpoints change the OpenAPI spec. The chain `make update-spec -> make sync-types -> make sync-backend-models -> npx tsc --noEmit` is a mandatory gate after backend API changes. <!-- Adopted from Improvement Area IA-15 -->
- **Bridge -> Backend proxy pattern** — All bridge tools proxy to backend REST endpoints via httpx. The bridge handles Bearer auth, X-API-Key forwarding, error wrapping, and response shaping. No direct DB access from the bridge.
- **Read-only tools are Tier 1** — All 4 new tools are read-only, LOW risk, no operator approval required. Per Integration Spec Section 7.2.
- **Quarantine schema immutability** — The existing `QuarantineCreate` model (orchestration/main.py lines 281-344) must NOT be modified. New endpoints READ from existing tables.
- **Backward-compatible filter expansion** — New query parameters on `GET /api/quarantine` must be optional with defaults that match current behavior. Existing consumers (dashboard, bridge) must not break.
- **Surface 15 compliance** — `make validate-surface15` must pass (10 checks: tool count, auth, port 8090 prohibition)
- **Surface 16 compliance** — `make validate-surface16` must pass (10 checks: injection params, dedup signaling, shadow mode)
- **Agent contract alignment** — Tool manifest in `agent_contract.py` must list ALL tools with correct risk levels
- **Redocly ceiling** — Ignore count is at 57 (the hard limit). New endpoints must NOT add new Redocly violations. If they do, the endpoints must be adjusted, not the ignore list.
- **Per standard architecture** — `transition_deal_state()` choke point, `Promise.allSettled` mandatory, port 8090 forbidden, generated files never edited, middleware proxy pattern (JSON 502), server-side counts only

---

## 3b. Anti-Pattern Examples

### WRONG: Bridge tool with direct DB query
```python
@mcp.tool()
def zakops_get_triage_feedback(sender_email: str):
    conn = psycopg2.connect(...)  # Bridge NEVER touches DB
    cursor.execute("SELECT ...")
```

### RIGHT: Bridge tool proxying to backend endpoint
```python
@mcp.tool()
def zakops_get_triage_feedback(sender_email: str, lookback_days: int = 90):
    resp = client.get(f"{DEAL_API_URL}/api/quarantine/feedback",
                      params={"sender_email": sender_email, "lookback_days": lookback_days},
                      headers={"X-API-Key": BACKEND_API_KEY})
    return resp.json()
```

### WRONG: Quarantine filter that changes default behavior
```python
# Before: GET /api/quarantine returns all pending items
# After: GET /api/quarantine now requires status param — BREAKS dashboard
@app.get("/api/quarantine")
async def list_quarantine(status: str):  # Required param breaks existing callers
```

### RIGHT: Backward-compatible optional filters
```python
@app.get("/api/quarantine")
async def list_quarantine(
    limit: int = 20,
    status: str | None = None,  # Optional — None returns "pending" for backward compat
    thread_id: str | None = None,
    sender: str | None = None,
    since_ts: str | None = None,
):
```

### WRONG: Manifest endpoint as MCP tool
```python
@mcp.tool()  # NO — manifest is plain HTTP, not an MCP tool
def get_integration_manifest(): ...
```

### RIGHT: Manifest as HTTP endpoint on bridge server
```python
# Add route to Starlette app underlying FastMCP
@app.route("/integration/manifest")
async def integration_manifest(request): ...
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | New backend endpoints add Redocly violations beyond the 57 ceiling | MEDIUM | Blocks `make validate-local` entirely | Phase 1 gate: verify Redocly ignore count unchanged. If new violations appear, fix the endpoint schemas. |
| 2 | Bridge tool parameter names don't match backend query params exactly | HIGH | Runtime 422 errors when LangSmith calls tools | Phase 2 gate: live curl test each new endpoint through the bridge |
| 3 | Quarantine filter expansion changes response shape or default behavior | HIGH | Breaks dashboard quarantine page | Phase 1: all new params optional, default behavior identical to current |
| 4 | Agent contract tool manifest count drifts from actual @mcp.tool() count | MEDIUM | Surface 15 validation fails on tool manifest alignment | Phase 4 gate: compare tool counts programmatically |
| 5 | Backend needs to be restarted/rebuilt to pick up new endpoints, but restart fails | LOW | Cannot test new endpoints | Decision tree in Phase 1: docker compose build + restart with --no-deps |

---

<!-- Adopted from Improvement Area IA-1 -->
## Context Checkpoint

This mission has 6 phases. If your context is becoming constrained mid-execution, summarize progress (phases completed, gates passed), commit intermediate work, and continue in a fresh continuation. Write checkpoint to `/home/zaks/bookkeeping/mission-checkpoints/INTEGRATION-PHASE1-BUILD-001.md`.

---

## 4. Phases

### Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 files modified (read-only)

**Purpose:** Verify the codebase is healthy and map the exact insertion points for new code.

#### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

#### Contract Surfaces Affected by This Mission
<!-- Adopted from Improvement Area IA-15 -->

| Surface | Name | Validation | Why Affected |
|---------|------|-----------|--------------|
| 1 | Backend -> Dashboard (TS) | `make sync-types` | New backend endpoints change OpenAPI spec |
| 2 | Backend -> Agent SDK (Python) | `make sync-backend-models` | New backend endpoints change OpenAPI spec |
| 6 | MCP Tools | Export from tool_schemas.py | New bridge tools change tool inventory |
| 8 | Agent Config | `make validate-agent-config` | Agent contract system prompt updated |
| 15 | MCP Bridge Tool Interface | `make validate-surface15` | New tools added to bridge server.py |
| 16 | Email Triage Injection | `make validate-surface16` | Quarantine list endpoint expanded |

#### Tasks
- P0-01: **Run `make validate-local`** — establish green baseline
  - **Checkpoint:** Must exit 0 before proceeding
- P0-02: **Run `make validate-surface15` and `make validate-surface16`** — capture baseline surface state
  - Evidence: record current tool count (expect 16) and all check results
- P0-03: **Read Integration Spec Section 4** — review all 4 new tool schemas (triage feedback, brokers, classification audit, sender intelligence)
  - File: `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` lines 150-375
- P0-04: **Audit existing quarantine endpoints** — identify insertion point for new endpoints
  - File: `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
  - Map: GET /api/quarantine (line ~1502), POST /api/quarantine (line ~1689), process endpoint (line ~2153)
- P0-05: **Audit broker infrastructure** — determine if a broker registry table/model exists
  - Search: `grep -r "broker" apps/backend/src/ --include="*.py" -l` in the monorepo
  - **Decision tree:**
    - **IF** dedicated broker table exists -> build endpoint on top of it
    - **ELSE IF** broker data is derived from quarantine items (broker_name, is_broker fields) -> build aggregation query
    - **ELSE** -> broker endpoint returns empty result with schema stub (deferred to Phase 2)
- P0-06: **Audit bridge server.py** — identify insertion point for new tools
  - File: `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py`
  - Note: existing tools at lines 467-1356, httpx client pattern, auth headers pattern
- P0-07: **Check Redocly ignore count** — record current value
  - Command: count ignores in Redocly config or check `make validate-local` output

#### Gate P0
- `make validate-local` passes (exit 0)
- `make validate-surface15` passes
- `make validate-surface16` passes
- Current tool count documented (expect 16)
- Insertion points identified for backend and bridge
- Broker infrastructure decision recorded

---

### Phase 1 — Backend Feedback & Intelligence Endpoints
**Complexity:** L
**Estimated touch points:** 1-3 files

**Purpose:** Add 4 new read-only GET endpoints to the backend API and expand the existing quarantine list endpoint with new filter parameters.

#### Blast Radius
- **Services affected:** Backend (:8091)
- **Pages affected:** None directly (new endpoints are bridge-consumed, not dashboard-consumed). Dashboard quarantine page uses GET /api/quarantine which gains optional params.
- **Downstream consumers:** Bridge tools (Phase 2), generated OpenAPI spec, generated TS types, generated Python models

#### Tasks
- P1-01: **Add `GET /api/quarantine/feedback` endpoint** — per Integration Spec Section 4.1
  - Parameters: `sender_email` (required), `lookback_days` (default 90), `limit` (default 20), `include_operator_notes` (default false), `include_corrections` (default true)
  - Response: summary rollup (approved/rejected/pending counts, approval_rate, typical_outcome) + recent_items + corrections
  - Data source: quarantine_items table, filtered by sender, joined with any decision/routing data
  - File: `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py`
  - **Checkpoint:** endpoint returns valid JSON for a test sender

- P1-02: **Add `GET /api/brokers` or `GET /api/quarantine/brokers` endpoint** — per Integration Spec Section 4.2
  - Parameters: `updated_since_ts` (optional), `limit` (default 2000), `cursor` (optional), `include_aliases` (default true), `include_domains` (default true)
  - Response: broker list with emails, domains, aliases, firm, status + cursor pagination
  - **Decision tree:**
    - **IF** broker table exists (from P0-05) -> query it directly
    - **ELSE** -> aggregate from quarantine_items (distinct broker_name, sender, sender_domain where is_broker=true) as a bootstrapped view
  - **Checkpoint:** endpoint returns valid JSON (even if empty list)

- P1-03: **Add `GET /api/quarantine/audit` endpoint** — per Integration Spec Section 4.3
  - Parameters: `start_ts` (required), `end_ts` (required), `source` (default "langsmith_agent"), `limit` (default 500), `cursor` (optional), `include_reasons` (default true)
  - Response: time-windowed list of classification decisions with original vs final values
  - Data source: quarantine_items where source_type matches, comparing classification at creation vs status at decision
  - **Checkpoint:** endpoint returns valid JSON for a time window

- P1-04: **Add `GET /api/quarantine/sender-intelligence` endpoint** — per Integration Spec Section 4.4
  - Parameters: `sender_email` (required), `lookback_days` (default 365), `include_deal_ids` (default true), `include_time_series` (default false)
  - Response: rollup stats (messages_seen, approved, rejected, approval_rate, avg_time_to_decision) + deal_associations + signals (is_known_broker, likely_broker_score)
  - Data source: quarantine_items aggregated by sender, joined with deals if deal_id present
  - **Checkpoint:** endpoint returns valid JSON for a test sender

- P1-05: **Expand `GET /api/quarantine` with new filter parameters** — per Integration Spec Section 3.4
  - Add optional params: `thread_id` (filter by source_thread_id), `sender` (filter by sender email), `status` (filter by status: pending/approved/rejected/all, default behavior preserved), `since_ts` (filter by created_at >= since_ts)
  - **CRITICAL:** All new params must be optional. Default behavior must be identical to current behavior. The dashboard calls this endpoint.
  - **Checkpoint:** `curl "http://localhost:8091/api/quarantine?limit=5"` returns same shape as before

- P1-06: **Rebuild and restart backend** — pick up new endpoints
  - Command: `cd /home/zaks/zakops-agent-api && COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend --no-deps`
  - **Checkpoint:** `curl -sf http://localhost:8091/health` returns OK

#### Rollback Plan
1. `git checkout -- apps/backend/src/api/orchestration/main.py` (or relevant files)
2. Rebuild backend: `COMPOSE_PROJECT_NAME=zakops docker compose build backend && docker compose up -d backend --no-deps`
3. Verify: `make validate-local` passes

#### Gate P1
- Backend healthy: `curl -sf http://localhost:8091/health`
- All 4 new endpoints return valid JSON (not 404/500)
- Existing `GET /api/quarantine?limit=5` returns same response shape as baseline
- `make validate-local` still passes
- Redocly ignore count unchanged from P0-07 baseline

---

### Phase 2 — Bridge Tools (Feedback Loop)
**Complexity:** L
**Estimated touch points:** 1 file (server.py)

**Purpose:** Add 4 new MCP bridge tools wrapping the Phase 1 backend endpoints, and expand `zakops_list_quarantine` with new filter parameters.

#### Blast Radius
- **Services affected:** Bridge (:9100)
- **Pages affected:** None (bridge serves LangSmith, not dashboard)
- **Downstream consumers:** LangSmith Exec Agent, Surface 15 validator, agent_contract.py tool manifest

#### Tasks
- P2-01: **Add `zakops_get_triage_feedback` bridge tool** — wraps `GET /api/quarantine/feedback`
  - Follow existing tool pattern in server.py (httpx client, X-API-Key header, error handling)
  - Parameters match Integration Spec Section 4.1: sender_email (required), lookback_days=90, limit=20, include_operator_notes=false, include_corrections=true
  - Docstring must explain when the tool is used (per-sender enrichment during triage)
  - **Checkpoint:** tool appears in `@mcp.tool()` count

- P2-02: **Add `zakops_list_brokers` bridge tool** — wraps `GET /api/brokers` (or equivalent from P1-02)
  - Parameters: updated_since_ts=null, limit=2000, cursor=null, include_aliases=true, include_domains=true
  - Docstring: used during SYNC.REFRESH_CACHES, not per-email
  - **Checkpoint:** tool appears in count

- P2-03: **Add `zakops_get_classification_audit` bridge tool** — wraps `GET /api/quarantine/audit`
  - Parameters: start_ts (required), end_ts (required), source="langsmith_agent", limit=500, cursor=null, include_reasons=true
  - Docstring: periodic learning loop, not in per-email path
  - **Checkpoint:** tool appears in count

- P2-04: **Add `zakops_get_sender_intelligence` bridge tool** — wraps `GET /api/quarantine/sender-intelligence`
  - Parameters: sender_email (required), lookback_days=365, include_deal_ids=true, include_time_series=false
  - Docstring: Step 0 enrichment for high-signal senders
  - **Checkpoint:** tool appears in count

- P2-05: **Expand `zakops_list_quarantine` with new parameters**
  - Add optional params: thread_id, sender, status, since_ts — matching backend filter expansion from P1-05
  - Preserve existing `limit` parameter and default behavior
  - Forward new params as query parameters to backend

- P2-06: **Restart bridge service** to pick up new tools
  - **Decision tree:**
    - **IF** bridge runs as a systemd service or Docker container -> restart it
    - **IF** bridge runs as a bare process -> stop and restart manually
  - **Checkpoint:** `grep -c '@mcp.tool()' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` returns 20

#### Rollback Plan
1. `git checkout -- apps/agent-api/mcp_bridge/server.py`
2. Restart bridge service
3. Verify: tool count returns to 16

#### Gate P2
- `@mcp.tool()` count in server.py equals 20 (16 existing + 4 new)
- Each new tool is callable without errors (bridge must be running)
- `zakops_list_quarantine` still works with just `limit` parameter (backward compat)
- `make validate-surface15` passes

---

### Phase 3 — Integration Manifest Endpoint
**Complexity:** M
**Estimated touch points:** 1 file (server.py)

**Purpose:** Add `GET /integration/manifest` HTTP endpoint on the bridge server for LangSmith drift detection.

#### Blast Radius
- **Services affected:** Bridge (:9100)
- **Pages affected:** None
- **Downstream consumers:** LangSmith Exec Agent (pre-flight check)

#### Tasks
- P3-01: **Add `GET /integration/manifest` route** — per Integration Spec Section 4.5
  - This is a plain HTTP endpoint, NOT an MCP tool
  - Response includes: integration_version, schema_version, bridge_tool_count, supported_action_types (initially just EMAIL_TRIAGE.PROCESS_INBOX), capability_tiers (autonomous/supervised/gated tool lists), tool_signatures (sha256 hash of each tool's docstring or signature), last_updated timestamp
  - **No authentication required** — LangSmith needs to check drift before authenticating
  - **Decision tree for adding HTTP routes:**
    - **IF** FastMCP exposes the underlying Starlette app -> add route directly
    - **ELSE IF** FastMCP has a custom route mechanism -> use that
    - **ELSE** -> mount a separate Starlette sub-app
  - **Checkpoint:** `curl -sf http://localhost:9100/integration/manifest | python3 -m json.tool` returns valid JSON

- P3-02: **Implement tool signature generation** — deterministic hash of each tool's parameter schema
  - Use hashlib.sha256 on a canonical JSON representation of each tool's parameters
  - Must be deterministic: same code produces same hash on every call
  - **Checkpoint:** `tool_signatures` dict has entries for all 20 tools

#### Rollback Plan
1. Remove the manifest route from server.py
2. Restart bridge
3. Verify: existing tools still work

#### Gate P3
- `curl -sf http://localhost:9100/integration/manifest` returns valid JSON
- Response contains `bridge_tool_count: 20`
- Response contains `tool_signatures` with 20 entries
- Response contains `capability_tiers` with correct tool-to-tier mapping
- Bridge still serves MCP tools normally after manifest addition

---

### Phase 4 — Agent Contract & Tool Manifest Update
**Complexity:** M
**Estimated touch points:** 1 file (agent_contract.py)

**Purpose:** Update the agent contract system prompt and tool manifest to include all new tools with correct risk levels and descriptions.

#### Blast Radius
- **Services affected:** Bridge (:9100) — agent contract affects tool evaluation
- **Pages affected:** None
- **Downstream consumers:** LangSmith Exec Agent (system prompt), Surface 15 validator (tool manifest alignment check)

#### Tasks
- P4-01: **Add 4 new tools to TOOL_MANIFEST** in agent_contract.py
  - `zakops_get_triage_feedback` — risk: LOW, category: Read - Feedback
  - `zakops_list_brokers` — risk: LOW, category: Read - Brokers
  - `zakops_get_classification_audit` — risk: LOW, category: Read - Audit
  - `zakops_get_sender_intelligence` — risk: LOW, category: Read - Intelligence
  - **Checkpoint:** TOOL_MANIFEST has 20 entries (was 16 + 1 health = 17 definitions)

- P4-02: **Update AGENT_SYSTEM_PROMPT** with new tool descriptions
  - Add the 4 new tools to the "Available Tools" section
  - Describe when each tool should be used (per Integration Spec cache TTL and pipeline step references)
  - **Checkpoint:** system prompt mentions all 4 new tool names

- P4-03: **Verify tool manifest alignment**
  - Count ToolDefinition entries in agent_contract.py vs @mcp.tool() decorators in server.py
  - These must match (or manifest must be a superset that includes the tools)

#### Rollback Plan
1. `git checkout -- apps/agent-api/mcp_bridge/agent_contract.py`
2. Restart bridge
3. Verify: existing tools still functional

#### Gate P4
- Tool manifest count matches @mcp.tool() count (both = 20)
- `make validate-surface15` passes (check 8: tool manifest alignment)
- `make validate-agent-config` passes (if applicable to bridge contract)
- System prompt contains all 4 new tool names

---

### Phase 5 — Spec Sync, Surface Validation & Bookkeeping
**Complexity:** M
**Estimated touch points:** Multiple generated files (via sync), CHANGES.md

**Purpose:** Run the full spec sync chain, validate all affected contract surfaces, and record changes.

#### Blast Radius
- **Services affected:** None directly (validation only)
- **Pages affected:** Dashboard (generated types will change, must verify no breakage)
- **Downstream consumers:** All type consumers (dashboard, agent SDK)

#### Tasks
- P5-01: **Run spec sync chain** (mandatory per IA-15)
  - `make update-spec` — capture new backend endpoints in OpenAPI spec (backend must be running)
  - `make sync-types` — regenerate dashboard TS types
  - `make sync-backend-models` — regenerate agent Python models
  - `npx tsc --noEmit` — verify TypeScript still compiles
  - **Checkpoint:** all 4 commands exit 0

- P5-02: **Run full surface validation**
  - `make validate-local` — full offline validation
  - `make validate-surface15` — MCP Bridge Tool Interface
  - `make validate-surface16` — Email Triage Injection
  - **Checkpoint:** all pass

- P5-03: **Verify dashboard is not broken** by new generated types
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit` — explicit TypeScript check
  - **Decision tree:**
    - **IF** tsc fails -> check which new types cause issues, fix bridge imports if needed
    - **IF** tsc passes -> proceed

- P5-04: **Fix CRLF and ownership** on any new files
  - `find /home/zaks/zakops-agent-api -newer /tmp/phase0-marker -name "*.sh" -exec sed -i 's/\r$//' {} +`
  - `sudo chown -R zaks:zaks /home/zaks/zakops-agent-api/apps/`

- P5-05: **Record changes in CHANGES.md**
  - File: `/home/zaks/bookkeeping/CHANGES.md`
  - Document: what was built, which endpoints/tools were added, tool count change (16->20), affected surfaces

- P5-06: **Write completion report**
  - File: `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md`
  - Include: per-phase results, gate outcomes, tool inventory, endpoint inventory, AC status

#### Rollback Plan
1. `make sync-all-types` — re-sync to undo any spec drift
2. Verify: `make validate-local` passes

#### Gate P5
- `make validate-local` passes
- `make validate-surface15` passes
- `make validate-surface16` passes
- `npx tsc --noEmit` passes
- Redocly ignore count unchanged from baseline
- CHANGES.md updated
- Completion report written

---

## 4b. Dependency Graph

```
Phase 0 (Discovery & Baseline)
    |
    v
Phase 1 (Backend Endpoints)
    |
    +------------------+
    |                  |
    v                  v
Phase 2             Phase 3
(Bridge Tools)      (Manifest)
    |                  |
    +--------+---------+
             |
             v
         Phase 4
    (Agent Contract)
             |
             v
         Phase 5
    (Sync & Verify)
```

Phase 2 and Phase 3 may execute in parallel (both depend only on Phase 1). Phase 4 depends on both Phase 2 and Phase 3 (needs final tool count). Phase 5 depends on all prior phases.

---

## 5. Acceptance Criteria

### AC-1: Backend Feedback Endpoints
4 new GET endpoints respond with valid JSON matching the schemas in Integration Spec Section 4 (4.1-4.4). Endpoints: `/api/quarantine/feedback`, brokers endpoint, `/api/quarantine/audit`, `/api/quarantine/sender-intelligence`.

### AC-2: Bridge Feedback Tools
4 new MCP tools registered: `zakops_get_triage_feedback`, `zakops_list_brokers`, `zakops_get_classification_audit`, `zakops_get_sender_intelligence`. Total @mcp.tool() count = 20.

### AC-3: Quarantine Filter Expansion
`zakops_list_quarantine` accepts thread_id, sender, status, since_ts parameters. Default behavior (no new params) is identical to pre-mission behavior. Dashboard quarantine page not broken.

### AC-4: Integration Manifest
`GET /integration/manifest` returns valid JSON with bridge_tool_count=20, capability_tiers, and tool_signatures for all 20 tools.

### AC-5: Agent Contract Updated
`agent_contract.py` TOOL_MANIFEST includes all 4 new tools at LOW risk. AGENT_SYSTEM_PROMPT describes when to use each new tool.

### AC-6: Contract Surfaces Pass
Surfaces 15 and 16 pass validation. `make validate-local` passes. `npx tsc --noEmit` passes.

### AC-7: Spec Sync Complete
`make update-spec` captures new endpoints. `make sync-types` and `make sync-backend-models` regenerate types without errors.

### AC-8: No Regressions
All 16 existing bridge tools still functional. Quarantine injection pipeline unaffected. Dashboard renders without new errors. `make validate-local` passes.

### AC-9: Bookkeeping
Changes recorded in `/home/zaks/bookkeeping/CHANGES.md`. Completion report at `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md`.

---

## 6. Guardrails

1. **Scope fence** — Build only Phase 1 items. Do NOT implement action leasing (Phase 2), delegation UI (Phase 2), or Gmail back-labeling (Phase 3).
2. **Generated file protection** — Do NOT edit `api-types.generated.ts`, `agent-api-types.generated.ts`, or `backend_models.py`. Use `make sync-*` pipeline. Enforced by pre-edit hook.
3. **Quarantine backward compatibility** — All new parameters on GET /api/quarantine must be optional. Default behavior must be byte-for-byte identical to current.
4. **Redocly ceiling** — Do NOT add entries to the Redocly ignore list. The ceiling is 57 and at capacity. Fix endpoint schemas if violations arise.
5. **Surface 9 compliance** — If any dashboard code is touched (should not be needed), follow design system rules per `.claude/rules/design-system.md`.
6. **WSL safety** — Strip CRLF from any new .sh files. Fix ownership with `chown zaks:zaks` on files under `/home/zaks/`.
7. **Port 8090 forbidden** — Never reference in any code.
8. **Governance surface gates** — Surfaces 15 and 16 must pass at every phase gate, not just final. <!-- Adopted from Improvement Area IA-15 -->
9. **No direct DB access from bridge** — All bridge tools must proxy through backend REST endpoints.
10. **Manifest is HTTP, not MCP** — `GET /integration/manifest` is a plain HTTP endpoint. It must NOT be registered as an `@mcp.tool()`.

---

## 7. Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify `make validate-local` passes at baseline before touching anything?"
- [ ] "Did I identify ALL 6 affected contract surfaces?"
- [ ] "Did I determine whether a broker table/model exists?"
- [ ] "Did I record the current Redocly ignore count?"

### After backend changes (Phase 1):
- [ ] "Did I rebuild and restart the backend to pick up new endpoints?"
- [ ] "Did I test each new endpoint with curl to verify it returns valid JSON?"
- [ ] "Does `GET /api/quarantine?limit=5` still return the same shape as before my changes?"
- [ ] "Did any new Redocly violations appear?"

### After bridge changes (Phase 2-3):
- [ ] "Does the @mcp.tool() count equal 20?"
- [ ] "Is the manifest endpoint HTTP-only, not an MCP tool?"
- [ ] "Did I restart the bridge after changes?"
- [ ] "Does `make validate-surface15` still pass?"

### Before marking the mission COMPLETE:
- [ ] "Did I run the full spec sync chain: make update-spec -> make sync-types -> make sync-backend-models -> npx tsc --noEmit?"
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I write the completion report?"
- [ ] "Did I create ALL files listed in the 'Files to Create' table?"

---

## 8. File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` | P1 | Add 4 new GET endpoints + expand quarantine list filters |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` | P2, P3 | Add 4 new tools + expand list_quarantine params + manifest endpoint |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py` | P4 | Update TOOL_MANIFEST + AGENT_SYSTEM_PROMPT with new tools |
| `/home/zaks/bookkeeping/CHANGES.md` | P5 | Record mission changes |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md` | P5 | Completion report with evidence |
| `/home/zaks/bookkeeping/mission-checkpoints/INTEGRATION-PHASE1-BUILD-001.md` | Any | Checkpoint for crash recovery (if needed) |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` | Integration spec — tool schemas, pipelines, security tiers |
| `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` | Existing quarantine endpoints — insertion point reference |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` | Existing bridge tools — pattern reference |
| `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py` | Existing tool manifest — pattern reference |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface15.sh` | Surface 15 validator — understand what's checked |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface16.sh` | Surface 16 validator — understand what's checked |

---

## 9. Stop Condition

This mission is DONE when:
1. All 9 acceptance criteria (AC-1 through AC-9) are met
2. `make validate-local` passes
3. `make validate-surface15` and `make validate-surface16` pass
4. `npx tsc --noEmit` passes
5. All changes committed to the monorepo
6. Completion report produced at `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md`
7. CHANGES.md updated

Do NOT proceed to:
- Phase 2 delegation framework (action type registry, claim/lease tools)
- Phase 3 bi-directional communication (Gmail back-labeling, event polling)
- Updating the LangSmith master config v3.0 (separate task after this mission)
- Deploying changes to production LangSmith agent

---

*End of Mission Prompt — INTEGRATION-PHASE1-BUILD-001*
