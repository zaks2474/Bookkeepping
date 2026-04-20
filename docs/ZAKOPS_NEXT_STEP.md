# ZakOps — Concrete Next Step (Post HITL Spike PASS)

**Date:** 2026-01-23  
**Inputs read (authoritative):**
- `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`
- `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`
- `/home/zaks/bookkeeping/docs/ZakOps-Ultimate-Master-Document-v2.md`
- `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`

## Current state (what’s true right now)

- The HITL spike is **PASS** (`QA-CYCLE-3`) with Gate Pack green, proving:
  - HITL interrupt/resume for `transition_deal`
  - Approval persisted before interrupt
  - Kill `-9` recovery
  - Concurrency → exactly-once execution
  - Strict tool args
  - JWT negative tests + actor spoofing protection (when enforced)
  - SSE streaming endpoint works
- This satisfies the **Master Plan v2 Spike DoD**, so we can move forward to the next phase.

## Concrete next step (do this next)

### Phase 1 kickoff = “Real-Service E2E Demo, No Mocks” (ONE goal)

**Goal:** Prove the Agent API controls *real* ZakOps services (Deal API :8090 + RAG REST :8052 + MCP :9100 + vLLM :8000) with `ALLOW_TOOL_MOCKS=false`, and that a real deal transition is reflected in the Deal API after approval.

This is the fastest path to de-risk the project before building more features.

### Why this is the next step (from the docs)

- **Master Plan v2** says the next action after the spike is to proceed into Phase 0/Phase 1 work and validate the “First Working Demo” scenario end-to-end.  
- **Decision Lock** requires direct tools (`list_deals`, `get_deal`, `transition_deal`, `check_health`) and prohibits “pass-by-mocks” for anything CRITICAL in a production-like path.
- **QA_REPORT.md** still flags a major residual risk: plaintext persistence in checkpoints/tool args/results; so we should only proceed with real data after confirming policy/mitigation (below).

## Checklist (builder-ready)

### A) Verify external services are reachable (fast, non-hanging)

Run with short timeouts (replace endpoints if your services differ):
- `curl --max-time 2 -sS -o /dev/null -w '%{http_code}\n' http://localhost:8000/health`
- `curl --max-time 2 -sS -o /dev/null -w '%{http_code}\n' http://localhost:8090/health` (or your Deal API health path)
- `curl --max-time 2 -sS -o /dev/null -w '%{http_code}\n' http://localhost:8052/health` (or your RAG REST health path)
- `curl --max-time 2 -sS -o /dev/null -w '%{http_code}\n' http://localhost:9100/health` (or MCP health path)

**Pass condition:** all return `200`.  
**If unknown/404:** don’t guess; identify the correct health endpoints and update the Agent tool URLs accordingly.

### B) Disable mocks and prove a real deal transition

1) Set runtime env so mocks cannot “hide” missing dependencies:
   - `APP_ENV=development`
   - `ALLOW_TOOL_MOCKS=false`
2) Run the agent Gate Pack again:
   - `cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh`
3) Run the “First Working Demo” against a *real* deal id that exists in Deal API:
   - `POST /agent/invoke` with a message that triggers `transition_deal`
   - capture `approval_id`
   - approve via `POST /agent/approvals/{approval_id}:approve`
4) Verify the stage transition via the Deal API (using its actual endpoint).

**Pass condition:**
- Agent returns `awaiting_approval` → approval row exists → approve returns `completed`
- Deal API reflects the stage change
- DB shows exactly one tool execution for that idempotency key
- No raw prompt/response appears in logs/traces

### C) Decide how to handle plaintext persistence (must decide before real data at scale)

From `QA_REPORT.md`: checkpoints/tool args/results may persist plaintext.

**Decision required now:** choose one of these before loading real confidential deal content:
1) **Accept** plaintext in checkpoints *only in dev* + enforce short TTL + local-only + disk encryption (documented risk).
2) **Mitigate** by encrypting/scrubbing checkpoint payloads and tool args/results at rest (higher effort; strongest policy compliance).

**Concrete action:** add a “PII canary” test gate (Master Plan v2 Phase 5) and decide whether it must pass in `APP_ENV=production` only or in all environments.

## After that (Phase 1 workstream)

Once the Real-Service E2E demo is green, start Phase 1 deliverables (highest ROI first):
1) Implement the remaining required direct tools from Decision Lock:
   - `list_deals` (READ)
   - `check_health` (READ)
2) Add JSON schema contract tests for `/agent/*` endpoints (fail CI on drift).
3) Start UI wiring (Next.js) for approvals + SSE stream consumption.

