# MISSION: QA-IP1-VERIFY-001
## Independent QA Verification of INTEGRATION-PHASE1-BUILD-001 (Feedback Loop & Intelligence Tools)
## Date: 2026-02-17
## Classification: QA Verification & Remediation
## Prerequisite: INTEGRATION-PHASE1-BUILD-001 (Complete 2026-02-17, 9/9 AC PASS)
## Successor: INTEGRATION-PHASE2-BUILD-001 (Delegation Framework)

---

## 1. Mission Objective

Perform an **independent verification** of INTEGRATION-PHASE1-BUILD-001, which built the Phase 1 "Feedback Loop" of the ZakOps + LangSmith Agent integration. This QA mission will verify, cross-check, stress-test, and remediate as needed.

**This is a QA mission. Do not build new features. Do not redesign. Verify what was built, remediate defects, and report.**

### Source Mission Summary

| Attribute | Value |
|-----------|-------|
| Mission ID | INTEGRATION-PHASE1-BUILD-001 |
| Mission Prompt | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001.md` (634 lines) |
| Completion Report | `/home/zaks/bookkeeping/docs/INTEGRATION-PHASE1-BUILD-001-COMPLETION.md` (134 lines) |
| Integration Spec | `/home/zaks/bookkeeping/docs/INTEGRATION-SPEC-V1.0.md` (1,074 lines) |
| AC Count | 9 (reported 9/9 PASS) |
| Phase Count | 6 (P0-P5) |
| Relay Message | `/home/zaks/bookkeeping/docs/LANGSMITH-PHASE1-RELAY-MESSAGE.md` (809 lines) |

### What Was Built (per completion report)

1. **4 backend GET endpoints** in `apps/backend/src/api/orchestration/main.py`:
   - `GET /api/quarantine/feedback` (line 1652)
   - `GET /api/quarantine/brokers` (line 1769)
   - `GET /api/quarantine/audit` (line 1848)
   - `GET /api/quarantine/sender-intelligence` (line 1938)
2. **4 new MCP bridge tools** in `apps/agent-api/mcp_bridge/server.py`:
   - `zakops_get_triage_feedback` (line 1434)
   - `zakops_list_brokers` (line 1487)
   - `zakops_get_classification_audit` (line 1544)
   - `zakops_get_sender_intelligence` (line 1602)
3. **Quarantine filter expansion** — `zakops_list_quarantine` (line 752) accepts thread_id, sender, status, since_ts
4. **Integration manifest** — `GET /integration/manifest` on bridge :9100 (ASGI handler, line 1832)
5. **Agent contract** — TOOL_MANIFEST updated 15->20, system prompt updated (agent_contract.py)
6. **Bonus fix** — Surface 16 WARN resolved (inject_quarantine added to contract manifest)

### Known Issues from Execution

- asyncpg datetime serialization bug was fixed during Phase 1 (audit endpoint)
- Manifest endpoint required ASGI dispatcher-level routing (FastMCP custom_route didn't work)
- Broker data is aggregated from quarantine_items (no dedicated broker table)

---

## 2. Pre-Flight (PF-1 through PF-6)

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-ip1-pf1-validate-local.txt
```
**PASS if:** exit 0. If not, STOP — codebase is broken before QA starts.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-ip1-pf2-tsc.txt
```
**PASS if:** exit 0, zero errors.

### PF-3: Surface 15 Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-surface15 2>&1 | tee /tmp/qa-ip1-pf3-surface15.txt
```
**PASS if:** 10/10 checks PASS, 0 WARN.

### PF-4: Surface 16 Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-surface16 2>&1 | tee /tmp/qa-ip1-pf4-surface16.txt
```
**PASS if:** 10/10 checks PASS, 0 WARN.

### PF-5: Backend Health
```bash
curl -sf http://localhost:8091/health 2>&1 | tee /tmp/qa-ip1-pf5-backend-health.txt
```
**PASS if:** returns JSON with healthy status. If backend is down, live endpoint verification gates become SKIP (not FAIL).

### PF-6: Bridge Health
```bash
curl -sf http://localhost:9100/integration/manifest 2>&1 | tee /tmp/qa-ip1-pf6-bridge-health.txt
```
**PASS if:** returns JSON with bridge_tool_count. If bridge is down, live bridge verification gates become SKIP (not FAIL).

**Services-down accommodation:** If PF-5 or PF-6 fail, this QA proceeds with code-only verification. Live endpoint tests become SKIP with notation "services down — code-verified only."

---

## 3. Verification Families

## Verification Family 01 — Backend Endpoints (Source: AC-1, Phase 1)

### VF-01.1: Feedback Endpoint Exists
```bash
grep -n "def.*quarantine.*feedback" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-ip1-vf01-1.txt
```
**PASS if:** grep finds `GET /api/quarantine/feedback` endpoint function.

### VF-01.2: Feedback Endpoint Parameters Match Spec
Read the endpoint function at line ~1652 in `apps/backend/src/api/orchestration/main.py`. Verify it accepts:
- `sender_email: str` (required)
- `lookback_days: int = 90`
- `limit: int = 20`
- `include_operator_notes: bool = False`
- `include_corrections: bool = True`

Per Integration Spec Section 4.1.
```bash
sed -n '1650,1770p' /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-ip1-vf01-2.txt
```
**PASS if:** All 5 parameters present with correct types and defaults.

### VF-01.3: Feedback Endpoint Live Test
```bash
curl -sf "http://localhost:8091/api/quarantine/feedback?sender_email=test@example.com" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf01-3.txt
```
**PASS if:** Returns valid JSON with `sender_email`, `summary`, `recent_items`, `corrections` keys. (If backend down: SKIP)

### VF-01.4: Brokers Endpoint Exists
```bash
grep -n "def.*quarantine.*brokers\|def.*list_brokers_endpoint\|api/quarantine/brokers\|/api/brokers" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-ip1-vf01-4.txt
```
**PASS if:** Endpoint function found.

### VF-01.5: Brokers Endpoint Parameters Match Spec
Read the endpoint function at line ~1769. Verify it accepts:
- `updated_since_ts: str | None = None`
- `limit: int = 2000`
- `cursor: str | None = None`
- `include_aliases: bool = True`
- `include_domains: bool = True`

Per Integration Spec Section 4.2.
```bash
sed -n '1768,1850p' /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-ip1-vf01-5.txt
```
**PASS if:** Parameters match spec. Pagination via cursor supported.

### VF-01.6: Brokers Endpoint Live Test
```bash
curl -sf "http://localhost:8091/api/quarantine/brokers?limit=5" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf01-6.txt
```
**PASS if:** Returns valid JSON with `brokers` array and `as_of_ts`. (If backend down: SKIP)

### VF-01.7: Audit Endpoint Exists and Parameters Match
```bash
grep -n "def.*quarantine.*audit" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-ip1-vf01-7.txt
```
Read the endpoint at line ~1848. Verify it accepts:
- `start_ts: str` (required)
- `end_ts: str` (required)
- `source: str = "langsmith_agent"`
- `limit: int = 500`
- `cursor: str | None = None`
- `include_reasons: bool = True`

Per Integration Spec Section 4.3.
**PASS if:** Endpoint exists with correct parameters.

### VF-01.8: Audit Endpoint Live Test
```bash
curl -sf "http://localhost:8091/api/quarantine/audit?start_ts=2026-01-01T00:00:00Z&end_ts=2026-12-31T23:59:59Z" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf01-8.txt
```
**PASS if:** Returns valid JSON with `window`, `audits` array, `as_of_ts`. (If backend down: SKIP)

### VF-01.9: Sender Intelligence Endpoint Exists and Parameters Match
```bash
grep -n "def.*sender.intelligence" /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-ip1-vf01-9.txt
```
Read the endpoint at line ~1938. Verify it accepts:
- `sender_email: str` (required)
- `lookback_days: int = 365`
- `include_deal_ids: bool = True`
- `include_time_series: bool = False`

Per Integration Spec Section 4.4.
**PASS if:** Endpoint exists with correct parameters.

### VF-01.10: Sender Intelligence Live Test
```bash
curl -sf "http://localhost:8091/api/quarantine/sender-intelligence?sender_email=test@example.com" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf01-10.txt
```
**PASS if:** Returns valid JSON with `sender_email`, `rollup`, `deal_associations`, `signals`. (If backend down: SKIP)

**Gate VF-01:** All 10 checks pass (live tests may SKIP if backend down). All 4 backend endpoints exist with correct parameter signatures matching Integration Spec Sections 4.1-4.4.

---

## Verification Family 02 — Bridge Tools (Source: AC-2, Phase 2)

### VF-02.1: Tool Count
```bash
grep -c '@mcp.tool()' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf02-1.txt
```
**PASS if:** Count = 20.

### VF-02.2: New Tool Functions Exist
```bash
grep -n 'def zakops_get_triage_feedback\|def zakops_list_brokers\|def zakops_get_classification_audit\|def zakops_get_sender_intelligence' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf02-2.txt
```
**PASS if:** All 4 functions found with line numbers.

### VF-02.3: Triage Feedback Tool Parameters Match Spec
Read `zakops_get_triage_feedback` function at line ~1434. Verify parameters:
- `sender_email: str` (required)
- `lookback_days: int = 90`
- `limit: int = 20`
- `include_operator_notes: bool = False`
- `include_corrections: bool = True`

Verify it proxies to `{DEAL_API_URL}/api/quarantine/feedback` with X-API-Key header.
```bash
sed -n '1433,1490p' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf02-3.txt
```
**PASS if:** Parameters match Integration Spec 4.1. Proxies to correct backend endpoint.

### VF-02.4: Brokers Tool Parameters Match Spec
Read `zakops_list_brokers` at line ~1487. Verify:
- `updated_since_ts: str | None = None`
- `limit: int = 2000`
- `cursor: str | None = None`
- `include_aliases: bool = True`
- `include_domains: bool = True`

Proxies to backend brokers endpoint.
```bash
sed -n '1486,1545p' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf02-4.txt
```
**PASS if:** Parameters match Integration Spec 4.2.

### VF-02.5: Classification Audit Tool Parameters Match Spec
Read `zakops_get_classification_audit` at line ~1544. Verify:
- `start_ts: str` (required)
- `end_ts: str` (required)
- `source: str = "langsmith_agent"`
- `limit: int = 500`
- `cursor: str | None = None`
- `include_reasons: bool = True`

Proxies to backend audit endpoint.
```bash
sed -n '1543,1605p' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf02-5.txt
```
**PASS if:** Parameters match Integration Spec 4.3.

### VF-02.6: Sender Intelligence Tool Parameters Match Spec
Read `zakops_get_sender_intelligence` at line ~1602. Verify:
- `sender_email: str` (required)
- `lookback_days: int = 365`
- `include_deal_ids: bool = True`
- `include_time_series: bool = False`

Proxies to backend sender-intelligence endpoint.
```bash
sed -n '1601,1660p' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf02-6.txt
```
**PASS if:** Parameters match Integration Spec 4.4.

### VF-02.7: All Bridge Tools Use Proxy Pattern (No Direct DB)
```bash
grep -c 'psycopg\|asyncpg\|sqlalchemy\|conn\.\|cursor\.' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf02-7.txt
```
**PASS if:** Count = 0. Bridge tools must proxy to backend, never access DB directly.

### VF-02.8: All New Tools Have X-API-Key Forwarding
```bash
grep -A 10 'def zakops_get_triage_feedback\|def zakops_list_brokers\|def zakops_get_classification_audit\|def zakops_get_sender_intelligence' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | grep -c 'X-API-Key\|BACKEND_API_KEY\|api_key' 2>&1 | tee /tmp/qa-ip1-vf02-8.txt
```
**PASS if:** Count >= 4 (one per new tool). Each tool forwards auth to backend.

**Gate VF-02:** All 8 checks pass. 20 bridge tools exist with correct parameters matching Integration Spec. No direct DB access from bridge. Auth forwarded.

---

## Verification Family 03 — Quarantine Filter Expansion (Source: AC-3, Phase 1/2)

### VF-03.1: Backend Quarantine List Accepts New Params
Read the existing `GET /api/quarantine` endpoint function. Verify it accepts:
- `thread_id: str | None = None` (or equivalent)
- `sender: str | None = None`
- `status: str | None = None`
- `since_ts: str | None = None`

All optional, default behavior unchanged.
```bash
grep -A 20 'def list_quarantine\|"/api/quarantine"' /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py | grep -i 'thread_id\|sender\|status\|since_ts' 2>&1 | tee /tmp/qa-ip1-vf03-1.txt
```
**PASS if:** All 4 new optional params found in the endpoint definition.

### VF-03.2: Bridge zakops_list_quarantine Accepts New Params
Read `zakops_list_quarantine` at line ~752. Verify params include:
- `thread_id: str | None = None`
- `sender: str | None = None`
- `status: str | None = None`
- `since_ts: str | None = None`
```bash
sed -n '751,805p' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf03-2.txt
```
**PASS if:** All 4 new params present.

### VF-03.3: Backward Compatibility — Default Behavior Unchanged
```bash
curl -sf "http://localhost:8091/api/quarantine?limit=5" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf03-3.txt
```
**PASS if:** Returns same response shape as pre-mission (items array with quarantine items). No required params changed. (If backend down: SKIP)

### VF-03.4: Filter by Thread ID Works
```bash
curl -sf "http://localhost:8091/api/quarantine?thread_id=nonexistent_thread_xyz&limit=5" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf03-4.txt
```
**PASS if:** Returns valid JSON (empty or filtered list), not 500/422. (If backend down: SKIP)

### VF-03.5: Filter by Status Works
```bash
curl -sf "http://localhost:8091/api/quarantine?status=approved&limit=5" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf03-5.txt
```
**PASS if:** Returns valid JSON with items matching status filter (or empty). (If backend down: SKIP)

**Gate VF-03:** All 5 checks pass. Quarantine filter expansion is backward-compatible and functional.

---

## Verification Family 04 — Integration Manifest (Source: AC-4, Phase 3)

### VF-04.1: Manifest Endpoint Exists as ASGI Handler (Not MCP Tool)
```bash
grep -n 'integration/manifest' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf04-1.txt
```
**PASS if:** Found in ASGI dispatcher (NOT as `@mcp.tool()`).

### VF-04.2: Manifest Is NOT an MCP Tool
```bash
grep -B 3 'integration.*manifest\|manifest.*integration' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py | grep -c '@mcp.tool()' 2>&1 | tee /tmp/qa-ip1-vf04-2.txt
```
**PASS if:** Count = 0. Manifest must be HTTP-only, never MCP tool.

### VF-04.3: Manifest Live Response
```bash
curl -sf "http://localhost:9100/integration/manifest" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf04-3.txt
```
**PASS if:** Returns valid JSON. (If bridge down: SKIP)

### VF-04.4: Manifest Contains Required Fields
Read manifest response from VF-04.3. Verify it contains:
- `integration_version` (string)
- `schema_version` (string)
- `bridge_tool_count` (int, expect 20)
- `capability_tiers` (object with autonomous/supervised/gated arrays)
- `tool_signatures` (object with sha256 hashes)
- `last_updated` (ISO-8601 timestamp)

**PASS if:** All 6 required fields present per Integration Spec Section 4.5.

### VF-04.5: Manifest Tool Count Matches Actual
Compare `bridge_tool_count` from manifest response against actual `@mcp.tool()` count.
**PASS if:** Both equal 20.

### VF-04.6: Manifest Tool Signatures Cover All 20 Tools
Count entries in `tool_signatures` from manifest response.
**PASS if:** Count = 20. Every registered tool has a signature hash.

### VF-04.7: Manifest Capability Tiers Are Correct
Read `capability_tiers` from manifest response. Verify:
- `autonomous`: all read tools (list_deals, list_quarantine, get_deal_status, list_deal_artifacts, list_recent_events, list_actions, get_action, rag_query_local, get_triage_feedback, list_brokers, get_classification_audit, get_sender_intelligence)
- `supervised`: inject_quarantine, create_action, update_deal_profile, write_deal_artifact, report_task_result, rag_reindex_deal
- `gated`: approve_quarantine

Per Integration Spec Section 7.2.
**PASS if:** Tier assignments match spec. No tool appears in multiple tiers. All 20 tools appear in exactly one tier.

### VF-04.8: Manifest Requires No Authentication
```bash
curl -sf -H "Authorization: " "http://localhost:9100/integration/manifest" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-vf04-8.txt
```
**PASS if:** Returns valid JSON even without Bearer token (per Integration Spec Section 4.5: "no auth required"). (If bridge down: SKIP)

**Gate VF-04:** All 8 checks pass. Integration manifest is HTTP-only, no-auth, returns correct tool count, complete signatures, and correct tier assignments.

---

## Verification Family 05 — Agent Contract (Source: AC-5, Phase 4)

### VF-05.1: TOOL_MANIFEST Entry Count
```bash
grep -c 'ToolDefinition\|"tool_name"' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py 2>&1 | tee /tmp/qa-ip1-vf05-1.txt
```
**PASS if:** Count aligns with 20 tool definitions (verify by reading TOOL_MANIFEST dict).

### VF-05.2: New Tools in TOOL_MANIFEST
```bash
grep -i 'triage_feedback\|list_brokers\|classification_audit\|sender_intelligence' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py 2>&1 | tee /tmp/qa-ip1-vf05-2.txt
```
**PASS if:** All 4 new tools found in TOOL_MANIFEST.

### VF-05.3: New Tools Classified as LOW Risk
Read the TOOL_MANIFEST entries for the 4 new tools. Verify each has risk level = LOW.
**PASS if:** All 4 new tools are LOW risk per Integration Spec Section 3.2.

### VF-05.4: inject_quarantine in TOOL_MANIFEST (Bonus Fix Verified)
```bash
grep -i 'inject_quarantine' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py 2>&1 | tee /tmp/qa-ip1-vf05-4.txt
```
**PASS if:** `zakops_inject_quarantine` found in TOOL_MANIFEST (this was the Surface 16 WARN fix).

### VF-05.5: System Prompt Contains New Tool Descriptions
```bash
grep -i 'triage.feedback\|list.brokers\|classification.audit\|sender.intelligence' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py 2>&1 | tee /tmp/qa-ip1-vf05-5.txt
```
**PASS if:** All 4 new tool names appear in the AGENT_SYSTEM_PROMPT section.

### VF-05.6: Manifest Count Matches Tool Count
Compare TOOL_MANIFEST entry count vs `@mcp.tool()` decorator count in server.py.
**PASS if:** Both equal 20.

**Gate VF-05:** All 6 checks pass. Agent contract reflects all 20 tools with correct risk levels.

---

## Verification Family 06 — Contract Surfaces (Source: AC-6, Phase 5)

### VF-06.1: Surface 15 — MCP Bridge Tool Interface
```bash
cd /home/zaks/zakops-agent-api && make validate-surface15 2>&1 | tee /tmp/qa-ip1-vf06-1.txt
```
**PASS if:** 10/10 checks PASS, 0 WARN.

### VF-06.2: Surface 16 — Email Triage Injection
```bash
cd /home/zaks/zakops-agent-api && make validate-surface16 2>&1 | tee /tmp/qa-ip1-vf06-2.txt
```
**PASS if:** 10/10 checks PASS, 0 WARN (was 9 PASS + 1 WARN before mission).

### VF-06.3: Full Validation
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-ip1-vf06-3.txt
```
**PASS if:** exit 0.

### VF-06.4: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-ip1-vf06-4.txt
```
**PASS if:** exit 0, zero errors.

### VF-06.5: Redocly Ignore Count Unchanged
Check Redocly ignore count from validate-local output.
**PASS if:** Count = 57 (unchanged from pre-mission ceiling).

**Gate VF-06:** All 5 checks pass. Surfaces 15 and 16 clean. Full validation green. No Redocly ceiling breach.

---

## Verification Family 07 — No Regressions (Source: AC-8)

### VF-07.1: Existing 16 Tools Still Present
```bash
for tool in zakops_list_deals zakops_get_deal zakops_update_deal_profile zakops_write_deal_artifact zakops_list_deal_artifacts zakops_list_quarantine zakops_inject_quarantine zakops_create_action zakops_get_action zakops_list_actions zakops_approve_quarantine zakops_get_deal_status zakops_list_recent_events zakops_report_task_result rag_query_local rag_reindex_deal; do
  if grep -q "def $tool" /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py; then
    echo "PASS: $tool"
  else
    echo "FAIL: $tool MISSING"
  fi
done 2>&1 | tee /tmp/qa-ip1-vf07-1.txt
```
**PASS if:** All 16 show PASS.

### VF-07.2: Quarantine Injection Pipeline Intact
```bash
grep -n 'def zakops_inject_quarantine' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>&1 | tee /tmp/qa-ip1-vf07-2.txt
```
Verify the inject function still maps `source_message_id` -> `message_id` at boundary, includes shadow_mode handling, and forwards all 31 fields.
**PASS if:** Injection function exists and boundary mapping intact.

### VF-07.3: Dashboard Pages Not Broken
If dashboard is running at :3003:
```bash
for page in dashboard quarantine actions settings agent onboarding operator deals; do
  STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:3003/$page" 2>/dev/null)
  echo "$page: $STATUS"
done 2>&1 | tee /tmp/qa-ip1-vf07-3.txt
```
**PASS if:** All pages return 200. (If dashboard down: SKIP)

### VF-07.4: Port 8090 Not Referenced
```bash
grep -rn '8090' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py /home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py 2>&1 | tee /tmp/qa-ip1-vf07-4.txt
```
**PASS if:** Zero matches (port 8090 is FORBIDDEN).

**Gate VF-07:** All 4 checks pass. No regressions to existing tools, injection pipeline, dashboard, or port discipline.

---

## Verification Family 08 — Spec Compliance Deep Check (Source: Integration Spec v1.0)

### VF-08.1: Response Schema — Triage Feedback
Read the `zakops_get_triage_feedback` bridge tool response. Verify it returns (or the backend endpoint returns) the schema structure from Integration Spec Section 4.1:
- Top-level: `sender_email`, `summary`, `recent_items`, `corrections`
- `summary`: total_quarantine_items, approved_count, rejected_count, pending_count, approval_rate, last_seen_ts, typical_outcome
- `recent_items[]`: message_id, thread_id, created_ts, decision, deal_id, deal_stage, operator_reasons, operator_notes
- `corrections`: routing_overrides[], classification_overrides[]

**PASS if:** Response structure matches spec (fields may be null/empty if no data, but keys must exist).

### VF-08.2: Response Schema — Brokers
Verify brokers endpoint returns:
- Top-level: `brokers[]`, `next_cursor`, `as_of_ts`
- `brokers[]`: broker_id, name, primary_email, emails[], domains[], aliases[], firm, role, status, last_updated_ts

**PASS if:** Structure matches Integration Spec Section 4.2.

### VF-08.3: Response Schema — Audit
Verify audit endpoint returns:
- Top-level: `window`, `audits[]`, `next_cursor`, `as_of_ts`
- `audits[]`: message_id, thread_id, deal_id, original{classification,urgency,proposed_by}, final{classification,urgency,decided_by}, ts, reason

**PASS if:** Structure matches Integration Spec Section 4.3.

### VF-08.4: Response Schema — Sender Intelligence
Verify sender-intelligence endpoint returns:
- Top-level: `sender_email`, `rollup`, `deal_associations[]`, `signals`, `as_of_ts`
- `rollup`: messages_seen, quarantine_injected, approved_to_deals, rejected, pending, approval_rate, avg_time_to_decision_hours, avg_time_to_approval_hours, first_seen_ts, last_seen_ts
- `signals`: is_known_broker, likely_broker_score, common_domains[], notes

**PASS if:** Structure matches Integration Spec Section 4.4.

### VF-08.5: Manifest Schema Compliance
Verify manifest response matches Integration Spec Section 4.5:
- `integration_version`, `schema_version`, `bridge_tool_count`, `supported_action_types[]`, `capability_tiers{}`, `tool_signatures{}`, `last_updated`

**PASS if:** All required fields present with correct types.

**Gate VF-08:** All 5 checks pass. Response schemas match the Integration Specification v1.0.

---

## 4. Cross-Consistency Checks (XC-1 through XC-5)

### XC-1: Bridge Tool Params ↔ Backend Endpoint Params Agreement
For each of the 4 new tools, verify the bridge tool parameter names match the backend endpoint query parameter names exactly. A mismatch causes 422 errors at runtime.
**PASS if:** Parameter names are identical between bridge and backend for all 4 tools.

### XC-2: TOOL_MANIFEST ↔ @mcp.tool() Count Agreement
```bash
MANIFEST_COUNT=$(grep -c 'ToolDefinition\|"tool_name"\|risk_level' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/agent_contract.py 2>/dev/null)
TOOL_COUNT=$(grep -c '@mcp.tool()' /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py 2>/dev/null)
echo "Manifest entries (approximate): $MANIFEST_COUNT"
echo "MCP tools: $TOOL_COUNT"
```
**PASS if:** Both resolve to 20 (exact matching method may vary — read the TOOL_MANIFEST dict to count entries precisely).

### XC-3: Manifest capability_tiers ↔ Integration Spec Security Tiers
Compare the `capability_tiers` object from `GET /integration/manifest` against Integration Spec Section 7.2. Every tool should appear in exactly the correct tier.
**PASS if:** Tier assignments match spec exactly.

### XC-4: Completion Report ↔ Actual Codebase Agreement
Verify each claim in the completion report against the actual code:
- "4 backend endpoints" → 4 endpoint functions exist
- "4 bridge tools" → 4 tool functions exist
- "tool count 20" → @mcp.tool() count is 20
- "TOOL_MANIFEST 15→20" → manifest has 20 entries
- "Surface 15: 10/10" → validate-surface15 still passes
- "Surface 16: 10/10" → validate-surface16 still passes

**PASS if:** All completion report claims verified.

### XC-5: Relay Message ↔ Actual Implementation Agreement
Spot-check 3 tool schemas from the relay message (`/home/zaks/bookkeeping/docs/LANGSMITH-PHASE1-RELAY-MESSAGE.md`) against the actual bridge tool implementations. Verify parameter names and types match.
**PASS if:** Relay message accurately describes the implemented tools.

---

## 5. Stress Tests (ST-1 through ST-5)

### ST-1: Backend Endpoint Error Handling — Invalid Parameters
```bash
# Missing required sender_email
curl -sf "http://localhost:8091/api/quarantine/feedback" 2>&1 | tee /tmp/qa-ip1-st1-a.txt
# Invalid lookback_days
curl -sf "http://localhost:8091/api/quarantine/feedback?sender_email=test@example.com&lookback_days=-1" 2>&1 | tee /tmp/qa-ip1-st1-b.txt
# Audit with missing required start_ts
curl -sf "http://localhost:8091/api/quarantine/audit" 2>&1 | tee /tmp/qa-ip1-st1-c.txt
```
**PASS if:** All return structured error responses (JSON, not 500 HTML). Missing required params should return 422 or 400.

### ST-2: Bridge Tool Error Propagation
If bridge is running, call a new tool with parameters that will cause a backend error. Verify the bridge returns a structured error, not a raw stack trace.
**PASS if:** Bridge wraps backend errors in a user-friendly format.

### ST-3: Quarantine Filter Combination
```bash
# Multiple filters combined
curl -sf "http://localhost:8091/api/quarantine?status=approved&sender=test@example.com&limit=5" 2>&1 | tee /tmp/qa-ip1-st3.txt
```
**PASS if:** Combined filters work together (AND logic), returns valid JSON.

### ST-4: Manifest Determinism
```bash
# Call manifest twice, compare tool_signatures
curl -sf "http://localhost:9100/integration/manifest" > /tmp/qa-ip1-st4-a.json 2>&1
curl -sf "http://localhost:9100/integration/manifest" > /tmp/qa-ip1-st4-b.json 2>&1
diff <(python3 -c "import json; d=json.load(open('/tmp/qa-ip1-st4-a.json')); print(json.dumps(d.get('tool_signatures',{}), sort_keys=True))") \
     <(python3 -c "import json; d=json.load(open('/tmp/qa-ip1-st4-b.json')); print(json.dumps(d.get('tool_signatures',{}), sort_keys=True))") 2>&1 | tee /tmp/qa-ip1-st4.txt
```
**PASS if:** Tool signatures are identical between calls (deterministic). (If bridge down: SKIP)

### ST-5: Manifest No-Auth Enforcement
```bash
# Verify manifest works without any auth header
curl -sf -H "Authorization: Bearer INVALID_TOKEN" "http://localhost:9100/integration/manifest" 2>&1 | python3 -m json.tool | tee /tmp/qa-ip1-st5.txt
```
**PASS if:** Still returns valid JSON even with invalid token (manifest requires no auth). (If bridge down: SKIP)

---

## 6. Remediation Protocol

For any FAIL result:
1. Read the evidence file to understand the failure
2. Classify:
   - **MISSING_FIX** — Something from the spec wasn't implemented
   - **REGRESSION** — Existing functionality broken by the changes
   - **SPEC_DRIFT** — Implementation doesn't match Integration Spec v1.0
   - **PARTIAL** — Partially implemented
   - **FALSE_POSITIVE** — Test is wrong, not the code
3. Apply fix following original mission guardrails
4. Re-run the specific gate that failed
5. Re-run `make validate-local`
6. Record in completion report

---

## 7. Enhancement Opportunities

### ENH-1: Response Schema Validation Tests
Add automated tests that validate response schemas against the Integration Spec JSON shapes. Currently only manual curl verification.

### ENH-2: Bridge Tool Integration Tests
Create pytest tests in the agent-api test suite that call each bridge tool with mock backend responses and verify correct proxy behavior.

### ENH-3: Manifest Schema Versioning Automation
The manifest currently requires manual updates when tools change. Consider generating `bridge_tool_count` and `tool_signatures` dynamically from the actual registered tools at startup.

### ENH-4: Broker Endpoint — Dedicated Table
Current broker endpoint aggregates from quarantine_items. A dedicated broker table (Phase 2 candidate) would enable proper CRUD, aliases, and status tracking.

### ENH-5: Quarantine Filter — Pagination Cursor
The expanded quarantine filter uses limit+offset pattern. Consider adding cursor-based pagination for consistency with the brokers endpoint.

### ENH-6: Endpoint Rate Limiting
The 4 new read endpoints have no rate limiting. Consider adding rate limits to prevent abuse (especially sender-intelligence which does aggregation queries).

### ENH-7: OpenAPI Documentation for New Endpoints
Verify the 4 new endpoints appear correctly in the generated OpenAPI spec with proper descriptions, parameter docs, and response schemas.

### ENH-8: Relay Message Drift Detection
When Phase 2 changes tools, the relay message at `/home/zaks/bookkeeping/docs/LANGSMITH-PHASE1-RELAY-MESSAGE.md` will drift. Consider a validation script that checks relay message tool counts against actual bridge tool counts.

### ENH-9: Backend Endpoint Response Caching
The feedback and intelligence endpoints do DB aggregation on every call. Consider adding server-side caching (e.g., Redis with TTL) for heavy queries.

### ENH-10: Manifest Supported Action Types
Currently `supported_action_types` only lists `EMAIL_TRIAGE.PROCESS_INBOX`. Should be updated as Phase 2 registers more action types.

---

## 8. Scorecard Template

```
QA-IP1-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):     [ PASS / FAIL ]
  PF-2 (tsc --noEmit):       [ PASS / FAIL ]
  PF-3 (Surface 15):         [ PASS / FAIL ]
  PF-4 (Surface 16):         [ PASS / FAIL ]
  PF-5 (Backend health):     [ PASS / FAIL / SKIP ]
  PF-6 (Bridge health):      [ PASS / FAIL / SKIP ]

Verification Gates:
  VF-01 (Backend Endpoints):      __ / 10 gates PASS
  VF-02 (Bridge Tools):           __ / 8 gates PASS
  VF-03 (Quarantine Filters):     __ / 5 gates PASS
  VF-04 (Integration Manifest):   __ / 8 gates PASS
  VF-05 (Agent Contract):         __ / 6 gates PASS
  VF-06 (Contract Surfaces):      __ / 5 gates PASS
  VF-07 (No Regressions):         __ / 4 gates PASS
  VF-08 (Spec Compliance):        __ / 5 gates PASS

Cross-Consistency:
  XC-1 through XC-5:             __ / 5 gates PASS

Stress Tests:
  ST-1 through ST-5:             __ / 5 gates PASS

Total: __ / 67 gates PASS, __ FAIL, __ SKIP, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **Do not build new features** — This is a QA mission. Verify, don't create.
2. **Remediate, don't redesign** — Fix what's broken per the original spec. Don't refactor.
3. **Evidence-based only** — Every PASS needs `tee`'d output. "I checked and it's fine" is never evidence.
4. **Services-down accommodation** — If backend or bridge is down, live tests become SKIP (not FAIL). Code-only verification continues.
5. **Preserve prior fixes** — Remediation must not revert the Surface 16 WARN fix or any earlier work.
6. **Generated files** — Do NOT edit `*.generated.ts` or `*_models.py`. Enforced by hooks.
7. **WSL safety** — `sed -i 's/\r$//'` on any new .sh files. `chown zaks:zaks` on files under `/home/zaks/`.
8. **Port 8090 forbidden** — Never reference.
9. **Scope fence** — Verify Phase 1 only. Do not test Phase 2 (delegation) or Phase 3 (bi-directional) features.
10. **Redocly ceiling** — Ignore count must remain at 57.

---

## 10. Stop Condition

Stop when all 67 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` passes, and the scorecard is complete.

Produce:
- Scorecard at `/home/zaks/bookkeeping/qa-verifications/QA-IP1-VERIFY-001/QA-IP1-VERIFY-001-SCORECARD.md`
- Completion report at `/home/zaks/bookkeeping/docs/QA-IP1-VERIFY-001-COMPLETION.md`
- Record in `/home/zaks/bookkeeping/CHANGES.md`

Do NOT proceed to Phase 2 build or LangSmith master config update.

---

*End of Mission Prompt — QA-IP1-VERIFY-001*
