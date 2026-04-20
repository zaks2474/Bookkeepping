# Acceptance Criteria: E2E System Verification

## Required Gates (ALL must PASS)

- [ ] **Gate 0: Pre-Flight**
  - All services responding (Dashboard 3003, Backend 8091, Agent 8095, RAG 8052)
  - Port 8090 is FREE (no legacy services)
  - No ghost data sources (no .deal-registry/, no deal_registry.json)

- [ ] **Gate 1: Environment Configuration**
  - Dashboard NEXT_PUBLIC_API_URL = http://localhost:8091
  - Dashboard NEXT_PUBLIC_AGENT_API_URL = http://localhost:8095
  - All env vars correctly pointing to their targets

- [ ] **Gate 2: Service Connectivity**
  - [A] Dashboard → Backend (8091): HTTP 200
  - [B] Dashboard → Agent API (8095): HTTP 200/healthy
  - [C] Backend → PostgreSQL (5432): Connection OK
  - [G] RAG API → rag-db (5434): Connection OK

- [ ] **Gate 3: Database Schemas**
  - zakops.deals table exists and queryable
  - zakops.actions table exists and queryable
  - RAG crawledpage table exists

- [ ] **Gate 4: End-to-End Tests**
  - GET /api/deals returns valid response
  - Agent health check passes
  - RAG /rag/stats returns valid response

- [ ] **Gate 5: Issues Resolved**
  - All detected connectivity issues fixed
  - Backend can reach RAG (if configured)
  - Agent can reach Backend (if tool calls enabled)

## Verification Report Required

- [ ] Report generated at `/home/zaks/bookkeeping/docs/E2E_VERIFICATION_REPORT_*.md`
- [ ] All gate results documented
- [ ] Service status matrix included
- [ ] Data state documented (deal count, action count, RAG chunks)

## Final State

- [ ] All 6 gates PASSED
- [ ] System architecture diagram matches actual connections
- [ ] Ready for production use
