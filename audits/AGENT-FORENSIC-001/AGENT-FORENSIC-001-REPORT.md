# AGENT-FORENSIC-001 Report
**Auditor:** Claude Code (Opus 4.5)
**Date:** 2026-02-02
**Scope:** Agent API Infrastructure & Surface Forensic Audit
**Method:** Live infrastructure inspection + API probing + source code review
**Mode:** READ-ONLY — no fixes applied

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Checks | 30 |
| PASS | 6 |
| FAIL (Critical/High) | 7 |
| WARN (Medium/Low) | 8 |
| INFO | 9 |
| **Verdict** | **7 findings require remediation** |

The Agent API has solid foundations (parameterized queries, rate limiting, proper DB isolation, structured logging) but has **critical security gaps**: all agent endpoints are unauthenticated, there is no user isolation, LLM output validation code exists but is never wired in, and /docs + /metrics are publicly exposed.

---

## Phase 0: Infrastructure Inventory (16 checks)

| Step | Check | Result | Key Finding |
|------|-------|--------|-------------|
| 0.1 | Service Census | PASS | 14 containers, agent-api healthy 9h, Langfuse restarting |
| 0.1b | Listening Ports | PASS | 8095, 8091, 3003, 5432, 8000, 9100 all active |
| 0.2 | Network Topology | INFO | Agent on `agent-api_agent-network` (172.26.x), cross-service via `host.docker.internal` |
| 0.3 | Agent API Health | PASS | `{"status":"healthy","version":"1.0.0"}`, /docs serves Swagger |
| 0.4 | Agent DB Schema | PASS | 9 tables: 4 LangGraph checkpoint, approvals, tool_executions, audit_log, user, session |
| 0.5 | Environment | INFO | Python 3.13.2, JWT HS256, Langfuse cloud, rate limits configured |
| 0.6 | Compose Config | PASS | 8095:8000 mapping, bind-mount ./app, depends_on db(healthy) |
| 0.7 | Reachability | PASS | Backend, PostgreSQL, vLLM, Redis, MCP, RAG all reachable |
| 0.8 | Source Inventory | INFO | 65 Python files, 11,276 LOC |
| 0.9 | Log Analysis | PASS | No errors/warnings in last 500 lines |
| 0.10 | Resource Usage | INFO | 260.8 MiB RAM, 0.17% CPU, no pressure |
| 0.11 | Volume Mounts | INFO | Source bind-mount (dev mode) |
| 0.12 | TLS/SSL | INFO | No internal TLS, all plain HTTP |
| 0.13 | Process Tree | INFO | Single uvicorn worker, non-root user |
| 0.14 | Dependencies | INFO | LangGraph 1.0.7, LangChain 1.2.7, FastAPI 0.128.0, Pydantic 2.12.5 |
| 0.15 | Config Files | INFO | Dockerfile, docker-compose.yml, langgraph.json, pyproject.toml |
| 0.16 | Port 8090 | PASS | Confirmed decommissioned — not in use anywhere |

### Architecture Diagram

```
                    [Dashboard :3003]
                         |
                    (Next.js rewrites)
                         |
    [Backend :8091] <--- | ---> [Agent API :8095]
         |                           |
    [zakops_network]          [agent-api_agent-network]
    - zakops-postgres-1       - zakops-agent-api (172.26.0.2)
    - zakops-redis-1          - zakops-agent-db  (172.26.0.3)
    - outbox-worker

    Cross-network via host.docker.internal:
    Agent API -> Backend (8091), vLLM (8000), MCP (9100), RAG (8052), Redis (6379)
```

---

## Phase 1: API Surface Audit (14 checks)

| # | Check | Result | Severity | Key Finding |
|---|-------|--------|----------|-------------|
| 1.1 | Route Enumeration | INFO | -- | 28 route-method combos, 14 unique handlers |
| 1.2 | Auth Enforcement | **FAIL** | CRITICAL | All agent endpoints unauthenticated |
| 1.3 | Schema Audit | INFO | -- | Pydantic validation on all endpoints |
| 1.4 | Dashboard Proxy | WARN | MEDIUM | Service token uses `==` not `hmac.compare_digest()` |
| 1.5 | LLM Integration | **FAIL** | HIGH | output_validation.py exists but never called |
| 1.6 | Input Validation | **FAIL** | HIGH | Agent inputs (message, actor_id) zero sanitization |
| 1.7 | Error Handling | WARN | MEDIUM | `detail=str(e)` leaks exception info |
| 1.8 | Multi-User Isolation | **FAIL** | CRITICAL | No ownership checks — any caller can act on any thread/approval |
| 1.9 | Rate Limiting | PASS | -- | Functional, memory-backed (resets on restart) |
| 1.10 | CORS | WARN | LOW | `allow_origins=["*"]` with `credentials=true` |
| 1.11 | SSE/Streaming | WARN | MEDIUM | Streaming works, no auth, error events leak details |
| 1.12 | DB Query Safety | PASS | -- | All parameterized, no injection vectors |
| 1.13 | Dependency Security | WARN | MEDIUM | python-jose has known issues, no scanning |
| 1.14 | Data Exposure | **FAIL** | HIGH | /docs, /redoc, /metrics exposed without auth |

---

## Findings — Remediation Backlog

### CRITICAL (2)

| ID | Finding | File(s) | Description |
|----|---------|---------|-------------|
| AF001-SEC-001 | Agent endpoints unauthenticated | `app/api/v1/agent.py`, `app/core/security/agent_auth.py` | `AGENT_JWT_ENFORCE` defaults to `false`. `/agent/invoke`, `/agent/approvals`, `/agent/threads/*` require no auth. Anyone can invoke the LLM (cost/abuse) and approve/reject actions. |
| AF001-SEC-002 | No user/tenant isolation | `app/api/v1/agent.py` | Any caller can view any thread state and act on any approval. Actor identity taken from request body when JWT is off (spoofable). |

### HIGH (5)

| ID | Finding | File(s) | Description |
|----|---------|---------|-------------|
| AF001-SEC-003 | LLM output validation dead code | `app/core/security/output_validation.py`, `app/core/langgraph/graph.py` | `sanitize_llm_output()` defined but never imported/called. LLM responses go directly to client unsanitized. |
| AF001-SEC-004 | /docs, /redoc, /metrics exposed | `app/main.py` | Full API schema, Python version, memory usage, DB connection counts publicly accessible. |
| AF001-SEC-005 | Agent input not sanitized | `app/api/v1/agent.py` | `message`, `actor_id`, `metadata` pass directly to LLM and DB without sanitization. |
| AF001-SEC-006 | Error responses leak internals | `app/api/v1/agent.py`, `app/api/v1/chatbot.py` | `raise HTTPException(500, detail=str(e))` in 5+ handlers. |
| AF001-SEC-007 | Service token timing attack | `app/api/v1/auth.py:184` | Uses `==` instead of `hmac.compare_digest()` for token comparison. |

### MEDIUM (4)

| ID | Finding | File(s) | Description |
|----|---------|---------|-------------|
| AF001-WARN-001 | No internal TLS | All services | All inter-service HTTP, acceptable only on single-host dev. |
| AF001-WARN-002 | Single uvicorn worker | Dockerfile | No gunicorn/multi-worker. Limits throughput. |
| AF001-WARN-003 | Langfuse in restart loop | `zakops-backend-langfuse-1` | May affect agent telemetry. |
| AF001-WARN-004 | Source bind-mount (dev mode) | docker-compose.yml | Host FS changes immediately affect running container. |

### LOW (3)

| ID | Finding | Description |
|----|---------|-------------|
| AF001-INFO-001 | CORS misconfiguration | `allow_origins=["*"]` with `credentials=true` — browsers block this combo but config is incorrect. |
| AF001-INFO-002 | Rate limits memory-only | Resets on container restart. No persistence. |
| AF001-INFO-003 | python-jose dependency | Known CVE history; consider switching to PyJWT. |

---

## Evidence

All evidence files in `/home/zaks/bookkeeping/audits/AGENT-FORENSIC-001/evidence/`:

### Phase 0 (17 files)
docker-ps.txt, listening-ports.txt, network-topology.txt, agent-health.txt, agent-db-schema.txt, agent-env.txt, compose-config.txt, reachability.txt, source-inventory.txt, agent-logs.txt, resource-usage.txt, volumes.txt, tls-check.txt, processes.txt, dependencies.txt, config-files.txt, port-8090-check.txt

### Phase 1 (14 files)
routes.txt, auth-matrix.txt, schema-audit.txt, proxy-chain.txt, llm-integration.txt, input-validation.txt, error-handling.txt, isolation.txt, rate-limiting.txt, cors.txt, streaming.txt, db-safety.txt, dep-security.txt, data-exposure.txt

---

## Recommended Remediation Priority

1. **AF001-SEC-001** — Enable JWT enforcement (`AGENT_JWT_ENFORCE=true`) and test all flows
2. **AF001-SEC-002** — Add ownership checks: thread creator == current user, approval actor == authorized user
3. **AF001-SEC-003** — Wire `sanitize_llm_output()` into the LangGraph response pipeline
4. **AF001-SEC-004** — Disable /docs, /redoc, /metrics behind auth or env flag
5. **AF001-SEC-005** — Add input sanitization to agent invoke/approval handlers
6. **AF001-SEC-006** — Replace `detail=str(e)` with generic error messages
7. **AF001-SEC-007** — Use `hmac.compare_digest()` for token comparison

---

**AGENT-FORENSIC-001 audit complete. 7 critical/high findings, 7 medium/low findings. Remediation required.**
