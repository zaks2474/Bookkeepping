# QA MISSION: QA-LANGSMITH-BRIDGE-HARDEN-VERIFY-001
## Deep Verification — MCP Bridge Hardening (Port, Auth, Injection, Transport)
## Date: 2026-02-14
## Classification: QA Verification & Remediation
## Prerequisite: LANGSMITH-BRIDGE-HARDEN-001 complete (6 phases, 8 AC, 17 evidence files)
## Auditor: Claude Code (Opus 4.6)

---

## 1. Mission Objective

Independent verification of LANGSMITH-BRIDGE-HARDEN-001. The completion report claims 8/8 AC PASS (Gate B DEFERRED). The mission modified a single file (`/home/zaks/scripts/agent_bridge/mcp_server.py`) to fix 4 overlapping failure modes: port drift, missing auth forwarding, missing injection tool, and transport uncertainty.

This QA will:

1. **Verify port drift is eliminated** — no references to port 8090 in code or runtime
2. **Verify auth forwarding is complete** — ALL backend write calls include X-API-Key, RAG calls do not
3. **Verify injection tool is correct** — source_type hardcoded, None stripping, 201/200 distinction, correlation ID forwarding
4. **Verify tool count** — 13 tools discoverable (12 original + injection)
5. **Verify evidence completeness** — 17 claimed files exist with meaningful content
6. **Cross-check evidence against live code** — line numbers, function names, health responses
7. **Hunt for residual issues** — port 8090 in other files, missing auth on write calls, stale artifacts

### Source Artifacts

| Artifact | Path |
|----------|------|
| Completion Report | `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-BRIDGE-HARDEN-001.COMPLETION.md` |
| Mission Prompt | `/home/zaks/bookkeeping/docs/MISSION-LANGSMITH-BRIDGE-HARDEN-001.md` |
| Bridge Server | `/home/zaks/scripts/agent_bridge/mcp_server.py` |
| Backend Auth Middleware | `/home/zaks/zakops-backend/src/api/shared/middleware/apikey.py` |
| Evidence Directory | `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-bridge-harden-001/` |

### Evidence Directory

```
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-langsmith-bridge-harden-verify-001
```

---

## 2. Pre-Flight

### PF-1: Bridge Server File Exists
Verify `/home/zaks/scripts/agent_bridge/mcp_server.py` exists.
**PASS if:** File exists and is non-empty.

### PF-2: Evidence Directory From Mission Exists
Verify `/home/zaks/bookkeeping/docs/_qa_evidence/langsmith-bridge-harden-001/` exists with 17 files.
**PASS if:** Directory exists with >= 17 files.

### PF-3: Bridge Process Running
Check if bridge is running on port 9100.
**PASS if:** Process running. If down, live gates become SKIP(services-down).

### PF-4: Completion Report Exists
**PASS if:** Completion report exists with 8/8 AC.

---

## 3. Verification Families

### VF-01 — Port Drift Elimination — 4 checks

#### VF-01.1: No port 8090 in bridge code
Search entire mcp_server.py for "8090".
**PASS if:** Zero occurrences.

#### VF-01.2: DEAL_API_URL defaults to 8091
Check line ~47 for the correct default.
**PASS if:** Default is `http://localhost:8091`.

#### VF-01.3: Docstring references 8091
Check line ~9 for the corrected docstring.
**PASS if:** Docstring says `:8091`, not `:8090`.

#### VF-01.4: No port 8090 in bridge directory
Search all files in `/home/zaks/scripts/agent_bridge/` for "8090".
**PASS if:** Zero occurrences.

### VF-02 — Auth Forwarding Completeness — 5 checks

#### VF-02.1: BACKEND_API_KEY constant exists
Check for `BACKEND_API_KEY = os.getenv("ZAKOPS_API_KEY", "")` near line ~51.
**PASS if:** Constant exists and reads from correct env var.

#### VF-02.2: zakops_create_action includes X-API-Key
Check the POST call in this function for auth header.
**PASS if:** `X-API-Key` header present.

#### VF-02.3: zakops_approve_quarantine includes X-API-Key
Check the POST call in this function for auth header.
**PASS if:** `X-API-Key` header present.

#### VF-02.4: zakops_inject_quarantine includes X-API-Key
Check the POST call in this function for auth header.
**PASS if:** `X-API-Key` header present.

#### VF-02.5: RAG calls do NOT include X-API-Key
Verify rag_query_local and rag_reindex_deal do not send X-API-Key (RAG has no auth middleware).
**PASS if:** No X-API-Key in RAG POST calls.

### VF-03 — Injection Tool Correctness — 7 checks

#### VF-03.1: source_type is hardcoded to "langsmith_shadow"
Verify source_type is NOT a parameter and IS hardcoded in the payload.
**PASS if:** `source_type` not in parameter list AND `"langsmith_shadow"` in payload construction.

#### VF-03.2: Parameters match spec
Expected: message_id (str), sender (str), subject (str), body_text (str), correlation_id (Optional[str]), classification (Optional[str]), company_name (Optional[str]), urgency (Optional[str]).
**PASS if:** All 8 parameters present with correct types.

#### VF-03.3: 201 vs 200 distinction
Verify function returns `created=True, dedup=False` for 201 and `created=False, dedup=True` for 200.
**PASS if:** Both paths exist with correct signals.

#### VF-03.4: None-valued optional fields stripped
Verify optional fields are only added to payload when provided (not None).
**PASS if:** Conditional inclusion pattern present.

#### VF-03.5: X-Correlation-ID forwarded conditionally
Verify correlation_id parameter maps to X-Correlation-ID header when provided.
**PASS if:** Conditional header inclusion present.

#### VF-03.6: Uses log_tool_call() for audit
Verify the function calls log_tool_call() like other tools.
**PASS if:** log_tool_call() present.

#### VF-03.7: Handles httpx.HTTPError consistently
Verify exception handling follows existing tool patterns.
**PASS if:** httpx.HTTPError catch block present.

### VF-04 — Tool Count & Discovery — 3 checks

#### VF-04.1: 13 @mcp.tool() decorators in code
Count decorators.
**PASS if:** Exactly 13.

#### VF-04.2: Evidence P5-02 shows 13 tools
Check final tool discovery evidence.
**PASS if:** Tool count = 13 and zakops_inject_quarantine present.

#### VF-04.3: All 12 original tools preserved
Cross-check P0-03 baseline (12 tools) against P5-02 final (13 tools).
**PASS if:** All 12 original tool names present in final list + injection tool added.

### VF-05 — Health Check Endpoint — 3 checks

#### VF-05.1: Health reports 4 components
Verify health endpoint checks bridge, deal_api, rag_api, dataroom.
**PASS if:** All 4 components in health response structure.

#### VF-05.2: Transport field in health response
Verify health response includes transport type and switch instructions.
**PASS if:** `transport` and `transport_switch` fields present.

#### VF-05.3: deal_api health check targets correct URL
Verify health check uses DEAL_API_URL (8091), not hardcoded 8090.
**PASS if:** Health check uses `DEAL_API_URL` variable.

### VF-06 — Gate Evidence Verification — 5 checks

#### VF-06.1: Gate A1 — deal_api healthy in evidence
Check P1-gate-A1-health.txt shows deal_api: healthy.
**PASS if:** JSON shows `"deal_api": "healthy"`.

#### VF-06.2: Gate A2 — write auth NOT 401
Check P2-gate-A2-write-auth.txt shows non-401 response.
**PASS if:** Response is NOT 401 (405 acceptable = auth passed, method not allowed is separate).

#### VF-06.3: Gate A3 — injection created with 201
Check P3-gate-A3-injection.txt shows status_code=201.
**PASS if:** Evidence shows created=True, status_code=201.

#### VF-06.4: Gate A4 — dedup returned 200
Check P3-gate-A4-dedup.txt shows status_code=200.
**PASS if:** Evidence shows created=False, dedup=True, status_code=200.

#### VF-06.5: Gate cleanup — proof data removed
Check P3-gate-cleanup.txt shows 0 remaining.
**PASS if:** remaining=0.

### VF-07 — Evidence File Completeness — 2 checks

#### VF-07.1: All 17 files exist
Check each claimed evidence file.
**PASS if:** All 17 exist.

#### VF-07.2: No empty evidence files
Check all evidence files have > 0 bytes.
**PASS if:** All non-empty.

### VF-08 — Bookkeeping & No Regressions — 3 checks

#### VF-08.1: CHANGES.md entry
Verify CHANGES.md has entry for LANGSMITH-BRIDGE-HARDEN-001.
**PASS if:** Entry exists.

#### VF-08.2: Completion report has 8 AC
Verify AC count.
**PASS if:** 8 AC rows in completion report.

#### VF-08.3: Startup banner shows correct info
Check startup banner in code shows Deal API URL, auth status, transport.
**PASS if:** Banner includes DEAL_API_URL, auth indicator, transport info.

---

## 4. Cross-Consistency Checks

### XC-1: Baseline health was degraded, final health is healthy
Cross-check P0-01 (degraded, deal_api unhealthy) vs P5-01 (healthy, all green).

### XC-2: Baseline had 12 tools, final has 13
Cross-check P0-03 (12 tools) vs P5-02 (13 tools).

### XC-3: Write call audit matches actual code
Cross-check P2-04 line numbers against actual mcp_server.py.

### XC-4: Process env before/after
Cross-check P0-02 (8090) vs P2-05 (8091).

### XC-5: AC count in mission matches completion report
Both should have 8 AC.

---

## 5. Stress Tests

### ST-1: No port 8090 anywhere in agent_bridge directory
Sweep all files for forbidden port.

### ST-2: No hardcoded API keys in code
Verify no literal key values in mcp_server.py (should use env vars).

### ST-3: Bridge auth mechanism unchanged (Bearer, not X-API-Key)
Verify BearerAuthMiddleware is used, not X-API-Key auth for bridge-level auth.

### ST-4: source_type cannot be overridden by caller
Verify "langsmith_shadow" is in code body, not function signature.

### ST-5: Tunnel config points to correct port
Check cloudflared config still routes to 9100.

### ST-6: No stale QA artifacts in bridge code
Verify no `=== Contract ===` or similar markers.

---

## 6. Enhancement Opportunities

### ENH-1: Automated bridge health smoke test script
### ENH-2: CI gate for bridge port drift detection
### ENH-3: Bridge startup self-test (call health, verify all green)
### ENH-4: Injection tool input validation (email format, message_id uniqueness hint)
### ENH-5: Rate limiting documentation for bridge callers
### ENH-6: Bridge process supervisor (systemd unit or supervisord)
### ENH-7: Dual transport support as a first-class feature

---

*End of QA Mission Prompt — QA-LANGSMITH-BRIDGE-HARDEN-VERIFY-001*
