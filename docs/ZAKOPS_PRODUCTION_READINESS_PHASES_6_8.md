# MISSION: ZakOps Production Readiness — Phases 6–8 (v2)
## Observability → Data Governance → Documentation

**Version:** 2.0 (Enhanced)
**Estimated Duration:** 7-10 days
**Prerequisites:** Phases 0-5 complete, services can start

---

## KEY IMPROVEMENTS OVER GPT's PROMPT

| Issue in GPT Prompt | My Enhancement |
|---------------------|----------------|
| OTEL validation requires running services | Offline validation + optional live check |
| Grafana dashboards = complex JSON | Dashboard templates with documented metrics |
| Canary requires full stack in CI | Graceful skip if services unavailable |
| Assumes multi-tenant | Default to single-tenant (homelab reality) |
| RAG quality gate requires vector store | Conditional on RAG service availability |
| Video walkthroughs | Simplify to written scripts only |
| Demo gate requires full stack | Mock mode for CI, full mode for local |
| 12+ separate gates | Consolidated into 3 phase gates |

---

## CRITICAL CONTEXT

### What This Mission Produces

| Phase | Primary Output | Gate |
|-------|----------------|------|
| **6** | OTEL conventions + SLO alerts + canary + dashboards | Conventions defined, alerts generated |
| **7** | Data policies + tenant isolation + PII redaction + RAG pipeline | Policies exist, PII tests pass |
| **8** | User docs + API docs + troubleshooting + demo script | Docs complete, demo passes |

### Hard Rules

1. **Observability config must be validated without running services**
2. **Data governance = docs + validation, not full implementation**
3. **RAG gates are conditional on RAG service availability**
4. **Demo gate has mock mode for CI**
5. **All docs must exist and have required sections**

---

## REFERENCE

Full implementation details provided in user message.
