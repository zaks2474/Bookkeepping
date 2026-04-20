# AGENT-FORENSIC-001 Phase 1 Summary: API Surface Audit

**Date:** 2026-02-02
**Auditor:** Claude Opus 4.5 (automated)
**Target:** Agent API (port 8095) — ZakOps Agent API v1.0.0
**Mode:** READ-ONLY

---

## Results Matrix

| # | Check | Result | Severity | Key Finding |
|---|-------|--------|----------|-------------|
| 1.1 | Route Enumeration | INFO | -- | 28 route-method combinations, 14 unique handlers, 7 duplicated at /agent/* |
| 1.2 | Auth Enforcement | **FAIL** | CRITICAL | All agent endpoints (/invoke, /approvals, /threads) require NO authentication |
| 1.3 | Request/Response Schema | INFO | -- | Schemas documented, Pydantic validation on all endpoints |
| 1.4 | Dashboard Proxy | WARN | MEDIUM | Service token compared with == (timing attack), clean proxy pattern otherwise |
| 1.5 | LLM Integration | **FAIL** | HIGH | output_validation.py exists but is NEVER called; no prompt injection protection |
| 1.6 | Input Validation | **FAIL** | HIGH | Agent endpoint inputs (message, actor_id, metadata) have zero sanitization |
| 1.7 | Error Handling | WARN | MEDIUM | 500 errors pass raw exception str(e) to client — potential info leak |
| 1.8 | Multi-User Isolation | **FAIL** | CRITICAL | No user isolation on agent endpoints; any caller can view/act on any approval/thread |
| 1.9 | Rate Limiting | PASS | LOW | Functional rate limiting on all endpoints; memory-based (resets on restart) |
| 1.10 | CORS | WARN | LOW | allow_origins=["*"] with credentials=true; effectively blocks credentialed CORS but config is wrong |
| 1.11 | SSE/Streaming | WARN | MEDIUM | Streaming endpoints work; /agent/invoke/stream has no auth; error events leak details |
| 1.12 | DB Query Safety | PASS | -- | All queries parameterized; raw SQL only for atomic operations with named params |
| 1.13 | Dependency Security | WARN | MEDIUM | python-jose has known issues; supabase unused; no dep scanning configured |
| 1.14 | Sensitive Data Exposure | **FAIL** | HIGH | /docs, /redoc, /metrics exposed without auth; environment/version/infra details visible |

---

## Critical Findings (Must Fix)

### 1. Agent Endpoints Are Completely Unauthenticated
**Files:** `app/api/v1/agent.py`, `app/core/security/agent_auth.py`
- `AGENT_JWT_ENFORCE` defaults to `"false"`
- `/agent/invoke` lets anyone invoke the LLM (cost + abuse risk)
- `/agent/approvals` lets anyone list, approve, or reject pending actions
- Actor identity is taken from request body when JWT is off (spoofable)

### 2. No User/Tenant Isolation on Agent Endpoints
**Files:** `app/api/v1/agent.py`
- Any caller can view any thread state, any approval, and act on any approval
- No ownership check between caller and thread/approval resources

### 3. LLM Output Validation Code Exists But Is Never Called
**Files:** `app/core/security/output_validation.py`, `app/core/langgraph/graph.py`
- `sanitize_llm_output()` is defined with HTML escaping, pattern detection, length limiting
- It is **never imported or used** in the response pipeline
- LLM responses go directly to the client unsanitized

### 4. Swagger/ReDoc/Metrics Exposed Without Auth
**Files:** `app/main.py`
- `/docs`, `/redoc` expose full API surface and schemas
- `/metrics` exposes Python version, memory, CPU, DB connection count
- No conditional logic to disable in production

---

## High Findings (Should Fix)

### 5. Agent Input Messages Not Sanitized
User messages, actor_id, and metadata pass directly to LLM and database without any sanitization. The `sanitize_string()` utility is only used in auth flows.

### 6. Error Responses Leak Internal Details
`raise HTTPException(status_code=500, detail=str(e))` appears in 5+ handlers. Exception messages may contain DB connection info, file paths, or Python tracebacks.

### 7. Service Token Comparison Vulnerable to Timing Attack
`auth.py:184`: `if x_service_token == settings.DASHBOARD_SERVICE_TOKEN` uses standard string comparison, not `hmac.compare_digest()`.

---

## Counts
- **FAIL (Critical/High):** 7
- **WARN (Medium/Low):** 8
- **PASS:** 4
- **INFO:** 3

---

## Evidence Files
All evidence saved to: `/home/zaks/bookkeeping/audits/AGENT-FORENSIC-001/evidence/phase1/`

| File | Check |
|------|-------|
| routes.txt | 1.1 Route Enumeration |
| auth-matrix.txt | 1.2 Auth Enforcement |
| schema-audit.txt | 1.3 Request/Response Schema |
| proxy-chain.txt | 1.4 Dashboard Proxy Analysis |
| llm-integration.txt | 1.5 LLM Integration |
| input-validation.txt | 1.6 Input Validation |
| error-handling.txt | 1.7 Error Handling |
| isolation.txt | 1.8 Multi-User Isolation |
| rate-limiting.txt | 1.9 Rate Limiting |
| cors.txt | 1.10 CORS Configuration |
| streaming.txt | 1.11 SSE/WebSocket Audit |
| db-safety.txt | 1.12 Database Query Safety |
| dep-security.txt | 1.13 Dependency Security |
| data-exposure.txt | 1.14 Sensitive Data Exposure |
