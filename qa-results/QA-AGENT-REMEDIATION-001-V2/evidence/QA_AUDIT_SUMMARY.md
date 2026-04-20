# QA Audit Summary - Agent Remediation V2
**Date:** 2026-02-02
**Auditor:** Adversarial QA Agent
**Evidence Location:** `/home/zaks/bookkeeping/qa-results/QA-AGENT-REMEDIATION-001-V2/evidence/`

---

## QA-3: Service Token Browser Boundary

**Objective:** Verify that internal service tokens are never exposed to browser/client-side code.

### Test Results

| Test | Status | Evidence |
|------|--------|----------|
| 1. Source code scan | **FAIL** | SERVICE_TOKEN found in source code |
| 2. NEXT_PUBLIC env vars | **PASS** | No NEXT_PUBLIC_*TOKEN or NEXT_PUBLIC_*SECRET found |
| 3. Built bundle check | **FAIL** | SERVICE_TOKEN found in .next/ build artifacts |
| 4. HTTP headers (root) | **PASS** | No token/secret/key/auth headers leaked |
| 5. HTTP headers (/api/chat) | **PASS** | No token/secret headers leaked |

### Critical Findings

**SECURITY VIOLATION:** Service tokens are present in server-side Next.js code and build artifacts:

1. **Source Code Location:** `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/complete/route.ts:4`
   ```typescript
   const AGENT_SERVICE_TOKEN = process.env.AGENT_SERVICE_TOKEN || process.env.DASHBOARD_SERVICE_TOKEN || '';
   ```

2. **Build Artifact Location:** `.next/server/app/api/chat/complete/route.js`
   - Contains: `const AGENT_SERVICE_TOKEN = process.env.AGENT_SERVICE_TOKEN || process.env.DASHBOARD_SERVICE_TOKEN || '';`
   - Also found in: `.next/server/app/api/chat/route.js` (provider-service.ts compiled)

**Analysis:**
- This is **SERVER-SIDE ONLY** code (Next.js API routes, RSC context)
- The tokens are accessed via `process.env` at runtime (not bundled as literal values)
- NOT exposed to browser (no NEXT_PUBLIC prefix, no client components)
- HTTP headers clean - no leakage in responses

**Risk Assessment:** **LOW**
- Next.js API routes are server-side only
- Environment variables are resolved server-side, not client-side
- No evidence of client-side exposure
- However, presence in bundled .next/ code is non-ideal from defense-in-depth perspective

**Recommendation:**
- Consider moving service token logic to server-only modules outside API routes
- Add explicit `"use server"` directives where applicable
- Monitor bundle analyzer to ensure no client-side exposure

### Overall: **CONDITIONAL PASS**
While tokens appear in build artifacts, they are properly scoped to server-side execution context and not exposed to browsers.

---

## QA-7: P2 Hardening

**Objective:** Verify implementation status of P2-priority hardening items.

### Test Results

| Item | Status | Evidence |
|------|--------|----------|
| UF-012: JWT Library | **PASS** | python-jose[cryptography]>=3.4.0 in pyproject.toml |
| UF-015: Langfuse Container | **FAIL** | Container in crash loop (Restarting) |
| UF-016: Volume Bind-Mounts | **DETECTED** | Multiple bind-mounts present |
| UF-018: RAG REST Health | **FAIL** | 404 response on /health |
| UF-019: MCP Server Health | **FAIL** | 404 response on / |
| UF-020: Backend API Health | **PASS** | Healthy response with valid JSON |
| UF-021: PATCH Session Endpoint | **FAIL** | sessions.py not found |
| UF-022: Agent API curl | **FAIL** | curl not available or container not running |

### Critical Findings

**UF-015: Langfuse Container Crash Loop**
```
zakops-backend-langfuse-1 Restarting (1) 47 seconds ago
```
- **Impact:** Observability/tracing not functional
- **Action Required:** Investigate langfuse container logs and fix startup issue

**UF-016: Volume Bind-Mounts Present**
Found bind-mounts:
- `./app:/app/app` (agent-api code mount)
- `./logs:/app/logs` (log directory)
- `./migrations:/docker-entrypoint-initdb.d:ro` (postgres init)
- `./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml`
- `./grafana/dashboards:/etc/grafana/provisioning/dashboards`
- `/:/rootfs:ro`, `/var/run:/var/run:rw`, `/sys:/sys:ro`, `/var/lib/docker/:/var/lib/docker:ro` (cadvisor mounts)

**Analysis:** Code hot-reload mounts acceptable for dev; system mounts for cadvisor are intentional.

**UF-018 & UF-019: Service Health Endpoints Failing**
- RAG REST (8052): 404 on /health (may use different health endpoint path)
- MCP Server (9100): 404 on / (endpoint may be /mcp/ or /health)
- **Action Required:** Confirm correct health check paths for both services

**UF-021: PATCH Session Endpoint Missing**
- sessions.py route file not found at expected location
- **Action Required:** Verify if sessions routes exist in agent-api or if this is expected

**UF-022: curl Not Available in Agent API Container**
- Container may not be running or curl not installed
- **Action Required:** Verify container status and install curl if needed for health checks

### Overall: **FAIL**
Multiple P2 items have implementation gaps requiring immediate attention.

---

## QA-9: Dashboard & MCP Compatibility

**Objective:** Verify dashboard and MCP services remain functional after remediation work.

### Test Results

| Endpoint | Expected | Actual | Status |
|----------|----------|--------|--------|
| GET / | 200-399 | 307 | **PASS** |
| GET /dashboard | 200 | 200 | **PASS** |
| GET /api/deals | 200 | 200 | **PASS** |
| GET /api/pipeline | 200 | 200 | **PASS** |
| GET /api/chat | 200 | 200 | **PASS** |
| MCP GET / | 200 | 404 | **WARN** |
| MCP GET /mcp/ | 200 | 307 | **WARN** |
| MCP POST /mcp/ | 200 | N/A | **FAIL** |

### Critical Findings

**Dashboard Endpoints: ALL PASS**
- Root redirects (307) to /dashboard - normal Next.js behavior
- All core API endpoints (deals, pipeline, chat) returning 200 OK
- Dashboard fully functional

**MCP Endpoints: ISSUES DETECTED**
- MCP root (/) returns 404 - unexpected
- MCP /mcp/ returns 307 (redirect) - may be normal but needs verification
- MCP JSON-RPC call to /mcp/ did not return visible output (truncated or failed)

**Analysis:**
- MCP server may not be running on port 9100 as expected
- Or MCP endpoint structure has changed
- Service Map indicates MCP Server should be at port 9100 in zakops-backend

**Action Required:**
1. Verify MCP server is running: `docker ps | grep mcp`
2. Check MCP server logs for startup errors
3. Confirm correct MCP endpoint path (may be /mcp/v1/ or similar)
4. Test MCP JSON-RPC with curl and verify response format

### Overall: **CONDITIONAL PASS**
Dashboard fully functional. MCP server accessibility uncertain - needs investigation.

---

## Summary Assessment

| Phase | Result | Critical Issues |
|-------|--------|-----------------|
| QA-3: Token Boundary | **CONDITIONAL PASS** | Tokens in server-side code only (acceptable) |
| QA-7: P2 Hardening | **FAIL** | Langfuse crash loop, missing health endpoints, missing routes |
| QA-9: Compatibility | **CONDITIONAL PASS** | Dashboard OK, MCP status unclear |

### Immediate Action Items

1. **HIGH PRIORITY:** Fix Langfuse container crash loop
   ```bash
   docker logs zakops-backend-langfuse-1
   cd /home/zaks/zakops-backend && docker compose restart langfuse
   ```

2. **HIGH PRIORITY:** Verify MCP server status and endpoints
   ```bash
   docker ps | grep mcp
   curl -v http://localhost:9100/
   curl -v http://localhost:9100/mcp/
   ```

3. **MEDIUM PRIORITY:** Confirm RAG REST health endpoint path
   ```bash
   curl http://localhost:8052/
   curl http://localhost:8052/api/health
   ```

4. **MEDIUM PRIORITY:** Locate sessions.py in agent-api or verify if expected
   ```bash
   find /home/zaks/zakops-agent-api/apps/agent-api -name "*session*" -type f
   ```

5. **LOW PRIORITY:** Consider refactoring service token access to dedicated server-only module

### Evidence Files

All raw test output saved to:
- `/home/zaks/bookkeeping/qa-results/QA-AGENT-REMEDIATION-001-V2/evidence/phase_r0y_qa/qa3_token_boundary.txt`
- `/home/zaks/bookkeeping/qa-results/QA-AGENT-REMEDIATION-001-V2/evidence/phase_r2_qa/qa7_p2_hardening.txt`
- `/home/zaks/bookkeeping/qa-results/QA-AGENT-REMEDIATION-001-V2/evidence/phase_rv_qa/qa9_compatibility.txt`

---

**Audit Completed:** 2026-02-02 18:00 CST
