# Mission: Phase 2 — MVP Build

## Objective

Prove the MVP works end-to-end against real services with mocks disabled. Establish contract probes, wire direct tools to Deal API, and verify the complete HITL lifecycle path.

## Background

Phase 1 completed successfully with all security, observability, and at-rest controls proven (14/14 gates passed). Phase 2 focuses on validating real-service integration:
- Deal API at :8090 must be reachable and functional
- vLLM at :8000 must be reachable
- Agent API at :8095 must work with real (non-mocked) backends

## Scope

### In Scope
1. **Contract Probes** (P2-DEAL-PROBE-001)
   - Discover and lock Deal API base path (`/deals` vs `/api/v1/deals`)
   - Lock Deal API schema (endpoints, status codes, response structure)
   - Verify Agent API canonical prefix (`/agent/*`)
   - Generate `repro_commands.sh` with example curl commands

2. **Disable Mocks** (P2-MOCKS-001)
   - Set `ALLOW_TOOL_MOCKS=false` in acceptance tests
   - Fail if any mock path is exercised during gate run
   - Verify no mock fallbacks in production mode

3. **Direct Tool Wiring** (MVP-critical)
   - `list_deals` → Deal API `GET /deals`
   - `get_deal` → Deal API `GET /deals/{id}`
   - `transition_deal` → Deal API `POST /deals/{id}/transition`
   - `check_health` → Deal API `GET /health`

4. **E2E HITL Lifecycle** (P2-E2E-001)
   - Full workflow: invoke → `awaiting_approval` → approve → `completed`
   - Verify Deal API state actually changes after tool execution
   - Prove exactly-once semantics via `tool_executions` table

5. **Cloudflare Routing Lint** (P2-CLOUDFLARE-001)
   - Verify Cloudflare tunnel routes only to :8095
   - Lint config to ensure :8090 is NOT exposed externally

### Out of Scope
- RAG integration (Phase 3)
- MCP expansion (Phase 4)
- Queue/DLQ implementation (Phase 5)
- UI smoke tests (deferred - requires Next.js repo)

## Technical Requirements

1. All tests must use the canonical gate command: `./scripts/bring_up_tests.sh`
2. All artifacts must be written to `gate_artifacts/`
3. Contract probe must be deterministic and re-runnable
4. No mock paths exercised when `ALLOW_TOOL_MOCKS=false`

## References

- Roadmap: `/mnt/c/Users/mzsai/Downloads/ZakOps-Ultimate-Implementation-Roadmap-combine.v2.md`
- Phase 1 Gate Report: `/home/zaks/zakops-backend/gate_artifacts/phase1/phase1_gate_report.json`
- Decision Lock: `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
- QA Report: `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`
