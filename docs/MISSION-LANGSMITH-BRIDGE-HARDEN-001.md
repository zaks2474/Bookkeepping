# MISSION: LANGSMITH-BRIDGE-HARDEN-001
## Harden ZakOps MCP Bridge — Eliminate All ZakOps-Side Failure Modes Before LangSmith Retry
## Date: 2026-02-14
## Classification: Integration Hardening
## Prerequisite: LANGSMITH-SHADOW-PILOT-001 (complete 2026-02-14)
## Successor: LangSmith Agent Builder re-connection (manual, Gate B)

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash, run these commands to determine current state:

```bash
# 1. Check bridge health (is deal_api healthy yet?)
curl -s http://127.0.0.1:9100/health | python3 -m json.tool

# 2. Check if injection tool exists
grep -c 'zakops_inject_quarantine' /home/zaks/scripts/agent_bridge/mcp_server.py

# 3. Check port drift
grep 'localhost:8090' /home/zaks/scripts/agent_bridge/mcp_server.py

# 4. Check evidence directory
ls /home/zaks/bookkeeping/docs/_qa_evidence/langsmith-bridge-harden-001/
```

Match results against phase gates below to determine which phase to resume from.

---

## 1. Mission Objective

**What:** Fix every known ZakOps-side failure mode in the MCP bridge so that any remaining integration failure is provably 100% LangSmith-side. This mission applies 4 surgical fixes and captures evidence that the bridge is unquestionably correct.

**What this is NOT:** This mission does NOT configure LangSmith's MCP Server settings, does NOT modify the backend API, does NOT touch the dashboard, and does NOT start the one-week shadow pilot. It only hardens the bridge server at `/home/zaks/scripts/agent_bridge/mcp_server.py`.

**Source material:**
- Forensic questionnaire results from this session (2026-02-14)
- Bridge server: `/home/zaks/scripts/agent_bridge/mcp_server.py` (998 lines, 12 tools)
- Backend auth middleware: `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` (57 lines)
- Tunnel config: `/home/zaks/.cloudflared/config.yml`
- Prior failure: January 2026 LangSmith attempt failed due to overlapping port drift + missing auth + missing injection tool + transport uncertainty

**Why separate from LangSmith config:** The January attempt failed because multiple overlapping failure modes made it impossible to isolate whether the problem was ZakOps-side or LangSmith-side. This mission eliminates ALL ZakOps-side issues first, so that Gate B (LangSmith discovery) produces a single, actionable diagnostic.

---

## 2. Context

### Current State (verified 2026-02-14 11:41 UTC)

| Component | Status | Evidence |
|-----------|--------|----------|
| Bridge process | Running (PID 2892, up since Feb 12) | `ps aux \| grep mcp_server` |
| Bridge port | 9100 listening on 127.0.0.1 | `ss -tlnp \| grep 9100` |
| SSE handshake | Working (returns session endpoint) | `GET /sse` → `event: endpoint` |
| Tool discovery | 12 tools returned via JSON-RPC | `tools/list` → 12 names |
| Tunnel | Active (`zakops-bridge.zaksops.com` → `:9100`) | Health check returns 200 through tunnel |
| Backend | Healthy on port 8091 | `curl :8091/health` → healthy |
| deal_api in health | **UNHEALTHY** — bridge targets port 8090 (dead) | Health endpoint shows `deal_api: unhealthy` |

### Four Overlapping Failure Modes (all present today)

1. **Port drift:** `DEAL_API_URL=http://localhost:8090` in running process env AND as code default at `mcp_server.py:47`. Port 8090 is decommissioned. Backend is on 8091.

2. **Missing auth forwarding:** Backend middleware (`apikey.py:49`) requires `X-API-Key` header on all POST/PUT/DELETE requests to `/api/quarantine*`. The bridge never sends this header — ALL bridge tools that make write calls to the backend will get 401 Unauthorized.

3. **No injection tool:** None of the 12 existing bridge tools inject quarantine items. The `zakops_list_quarantine` tool only reads. LangSmith has no way to submit deal intake items through the bridge.

4. **Transport uncertainty:** Bridge serves SSE on `/sse`. LangSmith Agent Builder's MCP client transport requirements are not documented — it may expect Streamable HTTP on `/mcp` instead. FastMCP 2.14.4 supports both transports.

### Auth Architecture (two keys, two hops)

```
LangSmith → (Authorization: Bearer <BRIDGE_KEY>) → MCP Bridge :9100
MCP Bridge → (X-API-Key: <BACKEND_KEY>) → Backend :8091
```

| Key | Env Var | Current Value | Used By |
|-----|---------|---------------|---------|
| Bridge key | `ZAKOPS_BRIDGE_API_KEY` | `95fa7fa6...986d35` (64-char hex) | LangSmith → Bridge (Bearer auth) |
| Backend key | `ZAKOPS_API_KEY` | `3bwj2Ajd...ZOPs` (32-char) | Bridge → Backend (X-API-Key header) |

The bridge reads `ZAKOPS_BRIDGE_API_KEY` from its own env (verified from `/proc/2892/environ`). The backend reads `ZAKOPS_API_KEY` from its `.env` file. These are separate secrets with separate purposes.

---

## 2b. Glossary

| Term | Definition |
|------|-----------|
| Bridge | MCP server at `/home/zaks/scripts/agent_bridge/mcp_server.py`, running on port 9100. Proxies LangSmith agent tool calls to the ZakOps backend and filesystem. |
| SSE transport | MCP transport where client GETs `/sse` to open an event stream, receives a session endpoint, then POSTs JSON-RPC messages to `/messages/?session_id=<id>`. Server pushes responses through the SSE stream. |
| Streamable HTTP | Alternative MCP transport where client POSTs JSON-RPC directly to a single endpoint (typically `/mcp`). Simpler than SSE — single request/response per call. |
| DEAL_API_URL | Env var controlling which port the bridge uses to reach the backend. Currently wrong (8090, should be 8091). |
| Shadow mode | `source_type=langsmith_shadow` — quarantine items tagged this way are isolated from production email flow and only visible under the shadow filter. |

---

## 3. Architectural Constraints

- **Port 8090 is FORBIDDEN** — decommissioned legacy port. All backend traffic must target 8091.
- **Bridge is NOT in the monorepo** — it lives at `/home/zaks/scripts/agent_bridge/`. Changes here do NOT trigger `make validate-local` or contract surface sync. Validation is manual (bridge health check + tool discovery probe).
- **Existing tool conventions must be followed** — all bridge tools use `log_tool_call()` for audit logging, return `dict` with `success`/`error` keys, use `httpx.Client` with timeouts, and handle `httpx.HTTPError` consistently.
- **Bridge auth is Bearer token** — the `BearerAuthMiddleware` checks `Authorization: Bearer <token>`. Do not change this to X-API-Key — LangSmith sends Bearer tokens.
- **Backend auth is X-API-Key** — the `APIKeyMiddleware` checks `X-API-Key` header on write methods. The bridge must forward this header on ALL POST/PUT/DELETE calls to the backend.
- **Shadow mode source_type is non-overridable** — the injection tool MUST hardcode `source_type="langsmith_shadow"`. The caller cannot change this. This is a security boundary.
- **Dedup distinction matters** — the injection tool must return different signals for 201 (new) vs 200 (dedup hit). This is how precision measurement works.

---

## 3b. Anti-Pattern Examples

### WRONG: Bridge calls backend without auth header
```python
with httpx.Client(timeout=30.0) as client:
    resp = client.post(f"{DEAL_API_URL}/api/quarantine", json=payload)
# Backend returns 401 — middleware blocks because X-API-Key is missing
```

### RIGHT: Bridge forwards X-API-Key on write calls
```python
with httpx.Client(timeout=30.0) as client:
    resp = client.post(
        f"{DEAL_API_URL}/api/quarantine",
        json=payload,
        headers={"X-API-Key": os.getenv("ZAKOPS_API_KEY", "")},
    )
# Backend accepts — middleware validates X-API-Key header
```

### WRONG: Injection tool lets caller choose source_type
```python
@mcp.tool()
def zakops_inject_quarantine(source_type: str = "langsmith_shadow", ...):
    # Caller can override to "email" or "langsmith_live" — breaks shadow isolation
```

### RIGHT: Injection tool hardcodes source_type
```python
@mcp.tool()
def zakops_inject_quarantine(message_id: str, sender: str, ...):
    payload = {"source_type": "langsmith_shadow", ...}  # Non-overridable
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Port fix applied in code but running process still uses old env var (8090) | HIGH | Bridge appears fixed but still fails at runtime | Gate A1 tests the RUNNING process health, not just the code |
| 2 | X-API-Key forwarded on the new injection tool but forgotten on existing POST tools (create_action, approve_quarantine) | MEDIUM | Existing tools silently broken | Phase 2 fixes ALL write calls, not just the new one. Gate A2 tests existing POST tools. |
| 3 | Bridge restart kills the tunnel connection requiring manual tunnel restart | LOW | Tunnel unreachable until cloudflared is restarted | Check tunnel status after bridge restart. Cloudflared runs independently (PID 289). |
| 4 | LangSmith requires Streamable HTTP but bridge only serves SSE — transport mismatch | MEDIUM | Tools: 0 in LangSmith despite bridge being correct | Phase 4 adds dual-transport support as a precaution. Gate B diagnoses with evidence. |
| 5 | CRLF in mcp_server.py after editing on WSL | LOW | Python SyntaxError on restart | Not applicable — Python files are not affected by CRLF (only .sh files). But verify clean startup in logs. |

---

## Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 files (read-only)

**Purpose:** Capture baseline evidence of all 4 failure modes before any changes.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Capture bridge health baseline** — `curl -s http://127.0.0.1:9100/health | python3 -m json.tool`
  - Evidence: `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-bridge-harden-001/P0-01-health-baseline.txt`
  - **Checkpoint:** `deal_api` must show `unhealthy` (confirms port drift is still present)
- P0-02: **Capture running process env vars** — extract `ZAKOPS_DEAL_API_URL`, `ZAKOPS_BRIDGE_API_KEY`, `ZAKOPS_API_KEY` from `/proc/<PID>/environ`
  - Evidence: `P0-02-process-env.txt`
  - **Checkpoint:** `ZAKOPS_DEAL_API_URL` contains `8090` (confirms port drift in runtime)
- P0-03: **Capture tool discovery baseline** — run threaded MCP SSE probe, record 12 tool names
  - Evidence: `P0-03-tool-discovery-baseline.txt`
  - **Checkpoint:** Exactly 12 tools, `zakops_inject_quarantine` NOT present
- P0-04: **Verify backend auth requirement** — `curl -s -X POST http://localhost:8091/api/quarantine -H 'Content-Type: application/json' -d '{}' | python3 -m json.tool` (expect 401)
  - Evidence: `P0-04-backend-auth-check.txt`
  - **Checkpoint:** Response is 401 Unauthorized (confirms auth middleware is active)

### Gate P0
- All 4 evidence files created
- All 4 checkpoints confirm expected baseline state
- No code changes made

---

## Phase 1 — Port Drift Fix (8090 → 8091)
**Complexity:** S
**Estimated touch points:** 1 file

**Purpose:** Fix the bridge so it targets the real backend on port 8091.

### Blast Radius
- **Services affected:** Bridge (restart required)
- **Pages affected:** None
- **Downstream consumers:** All 12 bridge tools that call `DEAL_API_URL`

### Tasks
- P1-01: **Update code default** — change `mcp_server.py:47` from `"http://localhost:8090"` to `"http://localhost:8091"`
  - Evidence: `/home/zaks/scripts/agent_bridge/mcp_server.py:47`
  - **Checkpoint:** `grep 'localhost:8090' mcp_server.py` returns 0 matches; `grep 'localhost:8091' mcp_server.py` returns 1+ matches
- P1-02: **Update docstring** — change `mcp_server.py:9` from `:8090` to `:8091`
  - Evidence: `/home/zaks/scripts/agent_bridge/mcp_server.py:9`
- P1-03: **Restart bridge with corrected env** — stop PID 2892, restart with `ZAKOPS_DEAL_API_URL=http://localhost:8091` (plus existing env vars)
  - Evidence: `P1-03-bridge-restart.txt` (startup banner showing corrected Deal API URL)
  - **Checkpoint:** Bridge starts successfully, startup banner shows `Deal API: http://localhost:8091`

### Decision Tree
- **IF** bridge process uses systemd → restart via `systemctl restart`
- **ELSE IF** bridge runs as bare process → kill PID, re-launch with env vars
- **ELSE** → investigate process supervisor

### Rollback Plan
1. Revert `mcp_server.py:47` to `"http://localhost:8090"`
2. Restart bridge
3. Verify health endpoint returns (even if degraded)

### Gate A1
- `curl -s http://127.0.0.1:9100/health | python3 -m json.tool` shows `deal_api: "healthy"`
- Evidence: `P1-gate-A1-health.txt`

---

## Phase 2 — Backend Auth Forwarding
**Complexity:** M
**Estimated touch points:** 1 file (multiple locations within it)

**Purpose:** Ensure ALL bridge-to-backend write calls include the `X-API-Key` header.

### Blast Radius
- **Services affected:** Bridge (restart required)
- **Pages affected:** None
- **Downstream consumers:** `zakops_create_action`, `zakops_approve_quarantine`, and the new injection tool (Phase 3)

### Tasks
- P2-01: **Add backend API key helper** — create a module-level helper function or constant that reads `os.getenv("ZAKOPS_API_KEY", "")` and returns the appropriate headers dict for backend write calls
  - Evidence: `/home/zaks/scripts/agent_bridge/mcp_server.py` (new function near configuration section)
  - **Checkpoint:** Function/constant exists and returns `{"X-API-Key": <value>}`
- P2-02: **Update `zakops_create_action`** — add `X-API-Key` header to the `httpx.Client.post()` call at the line where it POSTs to `{DEAL_API_URL}/api/actions`
  - Evidence: `mcp_server.py` (the `zakops_create_action` function)
  - **Checkpoint:** `grep 'X-API-Key' mcp_server.py` returns matches in `zakops_create_action`
- P2-03: **Update `zakops_approve_quarantine`** — add `X-API-Key` header to the `httpx.Client.post()` call at the line where it POSTs to `{DEAL_API_URL}/api/actions/quarantine/{action_id}/approve`
  - Evidence: `mcp_server.py` (the `zakops_approve_quarantine` function)
  - **Checkpoint:** `grep 'X-API-Key' mcp_server.py` returns matches in `zakops_approve_quarantine`
- P2-04: **Audit ALL httpx calls** — search for every `client.post(`, `client.put(`, `client.delete(`, `client.patch(` in the file. Confirm each write call either (a) targets the backend and includes `X-API-Key`, or (b) targets a non-backend service (RAG) that doesn't need it
  - Evidence: `P2-04-write-call-audit.txt` (list of all write calls with auth status)
- P2-05: **Add `ZAKOPS_API_KEY` to bridge process env** — ensure the restart command from Phase 1 includes this env var. If Phase 1 already restarted the bridge, plan a second restart after Phase 3.
  - Evidence: `P2-05-env-verification.txt`
  - **Checkpoint:** `cat /proc/<NEW_PID>/environ | tr '\0' '\n' | grep ZAKOPS_API_KEY` shows the correct key

### Rollback Plan
1. Remove `X-API-Key` headers from all modified functions
2. Restart bridge
3. Write calls will return 401 (pre-existing broken state)

### Gate A2
- Call `zakops_create_action` through MCP (via local SSE probe) with a test payload — expect success (not 401)
  - **IF** `zakops_create_action` requires a valid `action_type` recognized by the backend → use a known type from the backend's allowed list, or accept a 400/422 (validation error) as PASS (proves auth passed, payload validation is a separate concern)
  - **IF** response is 401 → FAIL (auth forwarding not working)
- Evidence: `P2-gate-A2-write-auth.txt`

---

## Phase 3 — Shadow Injection Tool
**Complexity:** M
**Estimated touch points:** 1 file

**Purpose:** Add a single MCP tool that injects quarantine items with `source_type="langsmith_shadow"` (non-overridable).

### Blast Radius
- **Services affected:** Bridge (restart required), Backend (receives new injections)
- **Pages affected:** Dashboard quarantine page (new items appear under shadow filter)
- **Downstream consumers:** LangSmith Agent Builder (will call this tool)

### Tasks
- P3-01: **Implement `zakops_inject_quarantine` tool** — add a new `@mcp.tool()` decorated function to `mcp_server.py`. Requirements:
  - Parameters: `message_id` (str, required), `sender` (str, required), `subject` (str, required), `body_text` (str, required), `correlation_id` (str, optional), `classification` (str, optional), `company_name` (str, optional), `urgency` (str, optional)
  - Hardcode `source_type = "langsmith_shadow"` — NOT a parameter
  - Include `X-API-Key` header on the POST (per Phase 2 pattern)
  - Pass `X-Correlation-ID` header if `correlation_id` is provided
  - Return dict with `created` (bool), `dedup` (bool), `status_code` (int), and `data` (response JSON)
  - Distinguish 201 (created=True, dedup=False) vs 200 (created=False, dedup=True) vs error
  - Use `log_tool_call()` for audit logging
  - Handle `httpx.HTTPError` consistently with existing tools
  - Evidence: `/home/zaks/scripts/agent_bridge/mcp_server.py` (new tool function)
  - **Checkpoint:** `grep -c 'zakops_inject_quarantine' mcp_server.py` returns 1+
- P3-02: **Restart bridge** — full restart with all corrected env vars (`ZAKOPS_DEAL_API_URL=http://localhost:8091`, `ZAKOPS_BRIDGE_API_KEY=<bridge_key>`, `ZAKOPS_API_KEY=<backend_key>`)
  - Evidence: `P3-02-restart-final.txt`
  - **Checkpoint:** Startup banner shows correct Deal API URL, Auth enabled

### Decision Tree (for restart)
- **IF** bridge was already restarted in Phase 1 with ZAKOPS_API_KEY → only restart once more after Phase 3 code changes
- **ELSE IF** bridge restart was deferred → restart now with ALL env vars
- **ELSE** → something unexpected; check process state

### Rollback Plan
1. Remove the `zakops_inject_quarantine` function
2. Restart bridge
3. Tool count returns to 12

### Gate A3 — Injection Creates Quarantine Row
- Call `zakops_inject_quarantine` through MCP SSE probe with test payload:
  - `message_id`: `bridge-harden-proof-001`
  - `sender`: `proof-test@bridge-harden.local`
  - `subject`: `Bridge Hardening Proof Test`
  - `body_text`: `Proof-of-concept injection from hardened MCP bridge.`
  - `correlation_id`: `harden-proof-001`
- **PASS criteria:** Response `status_code=201`, `created=True`, `dedup=False`
- Verify in DB: `SELECT id, message_id, source_type, correlation_id, status FROM zakops.quarantine_items WHERE message_id='bridge-harden-proof-001'`
- **PASS criteria:** Row exists with `source_type='langsmith_shadow'`, `correlation_id='harden-proof-001'`
- Evidence: `P3-gate-A3-injection.txt`

### Gate A4 — Dedup Behavior
- Call `zakops_inject_quarantine` again with the SAME `message_id` (`bridge-harden-proof-001`)
- **PASS criteria:** Response `status_code=200`, `created=False`, `dedup=True`
- Verify in DB: `SELECT count(*) FROM zakops.quarantine_items WHERE message_id='bridge-harden-proof-001'` → exactly 1 row
- Evidence: `P3-gate-A4-dedup.txt`

### Gate A-cleanup — Remove Proof Data
- `DELETE FROM zakops.quarantine_items WHERE message_id='bridge-harden-proof-001'`
- Verify 0 remaining: `SELECT count(*) FROM zakops.quarantine_items WHERE message_id='bridge-harden-proof-001'`
- Evidence: `P3-gate-cleanup.txt`

---

## Phase 4 — Transport Hardening & LangSmith Diagnosis
**Complexity:** M
**Estimated touch points:** 1 file (bridge) + LangSmith UI (manual verification)

**Purpose:** Ensure bridge serves both SSE and Streamable HTTP transports, then diagnose whether LangSmith can discover tools.

### Blast Radius
- **Services affected:** Bridge (restart required if transport changes)
- **Pages affected:** None
- **Downstream consumers:** LangSmith Agent Builder (the final consumer)

### Tasks
- P4-01: **Verify current tool discovery via tunnel** — run MCP SSE probe against `https://zakops-bridge.zaksops.com/sse` (same threaded probe as Phase 0 but through tunnel)
  - Evidence: `P4-01-tunnel-discovery.txt`
  - **Checkpoint:** 13 tools discovered (12 original + 1 injection) through tunnel with Bearer auth
- P4-02: **Investigate Streamable HTTP support** — FastMCP 2.14.4 supports `transport="streamable-http"` via `http_app(transport="streamable-http")`. Determine if the bridge can serve BOTH SSE (`/sse`) and Streamable HTTP (`/mcp`) simultaneously, or if it must pick one.
  - **IF** FastMCP supports dual transport or a combined mode → implement both endpoints
  - **ELSE IF** only one transport at a time → keep SSE as primary (existing), document how to switch
  - Evidence: `P4-02-transport-investigation.txt`
- P4-03: **Implement dual transport if feasible** — add a Streamable HTTP endpoint at `/mcp` alongside the existing SSE at `/sse`. This gives LangSmith two connection options.
  - **IF** dual transport is not feasible → document the limitation and provide a config switch
  - Evidence: Code changes in `mcp_server.py`
  - **Checkpoint:** `curl -X POST https://zakops-bridge.zaksops.com/mcp -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"initialize",...}'` returns a valid JSON-RPC response (if streamable HTTP was added)

### Decision Tree (LangSmith diagnosis — manual step)
- **IF** LangSmith MCP Server settings show `Tools: N` (N > 0) → PASS, proceed to tool execution test
- **ELSE IF** LangSmith shows `Tools: 0` with SSE URL → try switching to Streamable HTTP URL (`/mcp`)
- **ELSE IF** LangSmith shows `Tools: 0` with both URLs → the issue is LangSmith-side (auth header format, network routing, or MCP client version). Document as LANGSMITH_SIDE_ISSUE.
- **ELSE** → check Cloudflare tunnel logs for connection attempts

### Rollback Plan
1. If dual transport breaks SSE, revert transport changes
2. Restart bridge with `transport="sse"` only
3. Verify SSE still works via local probe

### Gate B — LangSmith Discovery (CONDITIONAL)
This gate may be DEFERRED if LangSmith UI is not accessible during execution. The bridge is proven correct by Gates A1-A4.

- LangSmith UI shows tools after configuring MCP Server with the bridge URL
- LangSmith can execute `zakops_list_quarantine` and get a response
- LangSmith can execute `zakops_inject_quarantine` and create a shadow quarantine item
- Evidence: Screenshots or `P4-gate-B-langsmith.txt`
- **IF DEFERRED:** Document exact LangSmith configuration steps for manual execution

---

## Phase 5 — Documentation & Final Verification
**Complexity:** S
**Estimated touch points:** 2 files

**Purpose:** Record all changes and produce completion report.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** Future sessions reading CHANGES.md

### Tasks
- P5-01: **Verify bridge health is fully green** — `curl -s http://127.0.0.1:9100/health` shows all components healthy
  - Evidence: `P5-01-final-health.txt`
- P5-02: **Verify tool count** — MCP probe returns 13 tools (12 original + injection)
  - Evidence: `P5-02-final-tools.txt`
- P5-03: **Verify tunnel passthrough** — health check through tunnel returns healthy
  - Evidence: `P5-03-tunnel-health.txt`
- P5-04: **Update CHANGES.md** — record all modifications with date, files, and what changed
  - Evidence: `/home/zaks/bookkeeping/CHANGES.md`
- P5-05: **Write completion report** — summary of all gates with evidence pointers
  - Evidence: `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-BRIDGE-HARDEN-001.COMPLETION.md`

### Gate P5
- All evidence files exist in `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-bridge-harden-001/`
- CHANGES.md updated
- Completion report written

---

## Dependency Graph

```
Phase 0 (Discovery & Baseline)
    │
    ▼
Phase 1 (Port Drift Fix)
    │
    ▼
Phase 2 (Auth Forwarding)
    │
    ▼
Phase 3 (Injection Tool)
    │
    ▼
Phase 4 (Transport + LangSmith Diagnosis)
    │
    ▼
Phase 5 (Documentation)
```

Phases execute strictly sequentially. Each phase's restart may be combined with the next to minimize restarts (e.g., defer Phase 1 restart until Phase 3 if all code changes are made first).

**Restart optimization:** The builder MAY combine code changes from Phases 1-3 and do a single restart before running Gates A1-A4, as long as each gate is verified independently with evidence.

---

## Acceptance Criteria

### AC-1: Port Drift Eliminated
`DEAL_API_URL` in code and running process env targets `localhost:8091`. Bridge health shows `deal_api: healthy`.

### AC-2: Auth Forwarding on All Write Calls
Every `httpx.Client.post()`, `.put()`, `.delete()`, `.patch()` call targeting `DEAL_API_URL` includes `X-API-Key` header. Verified by code audit + at least one successful POST through the bridge.

### AC-3: Shadow Injection Tool Exists
`zakops_inject_quarantine` tool is discoverable via MCP, hardcodes `source_type="langsmith_shadow"`, and successfully creates quarantine items.

### AC-4: Dedup Behavior Correct
Calling injection tool twice with the same `message_id` returns 201 then 200 with clear `created`/`dedup` signals.

### AC-5: Tool Discovery Through Tunnel
13 tools discoverable via `https://zakops-bridge.zaksops.com/sse` with Bearer auth.

### AC-6: Transport Investigation Complete
Streamable HTTP feasibility documented. If feasible, dual transport implemented. If not, limitation documented with config switch.

### AC-7: No Regressions
Bridge serves all 12 existing tools without errors. Health check returns healthy for bridge, deal_api, and dataroom.

### AC-8: Bookkeeping
CHANGES.md updated. Completion report written with evidence pointers for every gate.

---

## Guardrails

1. **Scope fence:** Only modify `/home/zaks/scripts/agent_bridge/mcp_server.py`. Do NOT modify backend code, dashboard code, or monorepo files. The backend quarantine endpoint and auth middleware are already correct.
2. **Do not modify the backend `.env`** — the bridge reads its own env vars at process startup, not from the backend's `.env` file.
3. **Do not change the bridge auth mechanism** — keep Bearer token auth via `BearerAuthMiddleware`. LangSmith sends Bearer tokens.
4. **Shadow mode is non-overridable** — the injection tool MUST hardcode `source_type="langsmith_shadow"`. Never expose it as a parameter.
5. **WSL safety** — `sudo chown zaks:zaks` on any modified files under `/home/zaks/`. CRLF is not a concern for Python files but verify clean startup.
6. **Preserve existing tools** — do not remove, rename, or change the behavior of any of the 12 existing tools. Only ADD the injection tool and ADD auth headers.
7. **Tunnel independence** — cloudflared (PID 289) runs independently of the bridge. Do not restart the tunnel. Only restart the bridge process.
8. **Evidence for every gate** — save to `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-bridge-harden-001/`. No unsaved evidence.
9. **Proof data cleanup** — all test quarantine items created during gate verification MUST be deleted before mission completion.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I capture evidence of ALL 4 failure modes (port, auth, injection, transport)?"
- [ ] "Did I verify the running process env, not just the code on disk?"
- [ ] "Are all 4 evidence files written to the evidence directory?"

### After code changes (Phases 1-3):
- [ ] "Did I fix the port in BOTH the code default AND the process startup command?"
- [ ] "Did I add X-API-Key to ALL write calls, not just the new injection tool?"
- [ ] "Is source_type hardcoded in the injection tool, not a parameter?"
- [ ] "Did I verify the bridge actually restarted and is serving on port 9100?"

### Before marking the mission COMPLETE:
- [ ] "Did all Gates A1-A4 pass with evidence?"
- [ ] "Did I clean up ALL proof test data from the database?"
- [ ] "Did I update CHANGES.md?"
- [ ] "Did I write the completion report with evidence pointers?"
- [ ] "Is the bridge health check showing ALL components healthy?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/scripts/agent_bridge/mcp_server.py` | 1 | Fix port default 8090 → 8091 |
| `/home/zaks/scripts/agent_bridge/mcp_server.py` | 2 | Add X-API-Key header to all write calls |
| `/home/zaks/scripts/agent_bridge/mcp_server.py` | 3 | Add `zakops_inject_quarantine` tool |
| `/home/zaks/scripts/agent_bridge/mcp_server.py` | 4 | Add Streamable HTTP transport (if feasible) |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| Evidence files (P0-01 through P5-03) | 0-5 | Gate evidence |
| `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-BRIDGE-HARDEN-001.COMPLETION.md` | 5 | Completion report |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` | Backend auth middleware (understand X-API-Key requirement) |
| `/home/zaks/zakops-backend/.env` | Backend API key value (read for ZAKOPS_API_KEY) |
| `/home/zaks/.cloudflared/config.yml` | Tunnel routing config |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | Quarantine endpoint contract (valid source_types, response codes) |

---

## Stop Condition

This mission is DONE when:
- Gates A1 (health), A2 (auth), A3 (injection), A4 (dedup) all PASS with evidence
- Gate B is either PASS or DEFERRED with documentation
- All 12 existing tools still work (no regressions)
- Bridge health shows all components healthy
- All proof test data cleaned up
- CHANGES.md updated
- Completion report written

Do NOT proceed to: configuring LangSmith MCP Server settings (that is a manual step after this mission), starting the one-week shadow pilot, or modifying backend/dashboard code.

---

*End of Mission Prompt — LANGSMITH-BRIDGE-HARDEN-001*
