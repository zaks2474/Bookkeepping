# AGENT-FORENSIC-001 Remediation Backlog (P01)
| # | Finding | Priority | Fix |
|---|---------|----------|-----|
| 1 | /agent/* endpoints accept requests without valid X-Service-Token | P0 | Enforce X-Service-Token on all /agent/* routes; return 401/403 on missing/invalid token |
| 2 | /api/v1/agent/* endpoints exposed without auth | P0 | Require JWT or service token for /api/v1/agent/*; add integration tests |
| 3 | Confused deputy: JWT accepted on /agent/invoke | P0 | Reject JWT on service-token endpoints; define auth precedence rules |
| 4 | Chat streaming returns SSE error payload | P1 | Fix LangchainCallbackHandler init args; add streaming regression test |
| 5 | Session name update endpoint returns 404 | P2 | Implement/route /api/v1/auth/session/{id}/name per OpenAPI |
| 6 | No rate limiting observed | P2 | Add rate limiting (per-IP/user) and document limits |
| 7 | Container reachability check blocked (curl missing) | P2 | Add curl/wget or use busybox in agent container for probes |
| 8 | RAG /health returns 404 | P2 | Expose health endpoint or update monitoring to correct path |
| 9 | MCP root returns 404 | P2 | Expose health endpoint or update monitoring expectations |
|10 | Orchestration /health empty | P2 | Implement meaningful /health response |
|11 | Langfuse container restarting | P2 | Investigate restart loop; ensure service stable |
