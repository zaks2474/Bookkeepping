# Acceptance Criteria: ZakOps E2E System Validation (HARDENED)

## Definition of Done

The task is complete when ALL of the following are true:

### Phase 0: Baseline Service Health
- [ ] Deal API (8090) responds 200 to /health
- [ ] Agent API (8095) responds 200 to /health
- [ ] Orchestration API (8091) responds 200 to /health
- [ ] Dashboard (3003) responds 200 to /
- [ ] RAG REST API (8052) responds 200 to /health
- [ ] vLLM (8000) responds 200 to /health
- [ ] Postgres (5432) passes pg_isready check
- [ ] Redis (6379) responds PONG to PING
- [ ] Evidence artifact exists: `artifacts/validation/phase0_service_health.json`

### Phase 1: Integration Contract Verification
- [ ] Deal API can call Agent API successfully
- [ ] Agent API can call Orchestration API successfully
- [ ] Dashboard can fetch data from all backend APIs
- [ ] Response schemas match expected contracts
- [ ] Evidence artifact exists: `artifacts/validation/phase1_integration.json`

### Phase 2: Tool Execution Validation
- [ ] All registered tools are enumerated
- [ ] Tool schemas validate against Anthropic tool_use spec
- [ ] At least one tool executes in dry-run/safe mode successfully
- [ ] Tool error handling returns proper error structure
- [ ] Evidence artifact exists: `artifacts/validation/phase2_tools.json`

### Phase 3: Human-in-the-Loop (HITL) Verification
- [ ] Approval request can be created via API
- [ ] Approval request appears in pending list
- [ ] Approval can be granted via API
- [ ] Rejection can be issued via API
- [ ] Approval status propagates to agent run
- [ ] Evidence artifact exists: `artifacts/validation/phase3_hitl.json`

### Phase 4: Dashboard-Agent Synchronization
- [ ] Dashboard shows current agent runs
- [ ] Run status updates within 2 seconds of backend change
- [ ] Run history matches backend database
- [ ] SSE/WebSocket connection established successfully
- [ ] Evidence artifact exists: `artifacts/validation/phase4_dashboard_sync.json`

### Phase 5: Agent Intelligence Validation
- [ ] Agent responds coherently to test prompt
- [ ] Agent selects appropriate tool for task
- [ ] Multi-turn conversation maintains context
- [ ] Agent handles edge case prompts gracefully
- [ ] Evidence artifact exists: `artifacts/validation/phase5_intelligence.json`

### Phase 6: Graph Execution Validation
- [ ] Workflow graph can be created via API
- [ ] Graph nodes execute in topological order
- [ ] Conditional branching follows correct path
- [ ] Graph execution produces expected outputs
- [ ] Evidence artifact exists: `artifacts/validation/phase6_graphs.json`

### Phase 7: Adversarial Testing
- [ ] SQL injection attempts are rejected
- [ ] XSS payloads are sanitized or rejected
- [ ] Prompt injection attempts are handled safely
- [ ] Rate limiting triggers at configured threshold
- [ ] Invalid auth tokens are rejected
- [ ] Evidence artifact exists: `artifacts/validation/phase7_adversarial.json`

### Phase 8: Double Verification (Skeptic Pass)
- [ ] 3 critical paths re-verified with alternative method
- [ ] Results consistent with earlier phases
- [ ] Any discrepancies documented and explained
- [ ] Evidence artifact exists: `artifacts/validation/phase8_double_verify.json`

### Final Deliverables
- [ ] `tools/validation/master_gate.sh` exists and is executable
- [ ] Individual phase scripts exist in `tools/validation/`
- [ ] All 9 phase evidence artifacts exist in `artifacts/validation/`
- [ ] `artifacts/validation/VALIDATION_FINAL_REPORT.json` exists
- [ ] Final report contains `"verdict": "SYSTEM VALIDATED"`

## Verification Steps

1. Run master gate: `bash tools/validation/master_gate.sh`
2. Verify exit code is 0
3. Check all evidence artifacts exist and are valid JSON
4. Verify final report shows all phases passed
5. Confirm verdict is "SYSTEM VALIDATED"

## Gate Command

```bash
bash tools/validation/master_gate.sh
```

This command must:
- Execute all 9 validation phases
- Generate all evidence artifacts
- Produce final report
- Exit with code 0 only if ALL phases pass

## Non-Functional Requirements

- Gate must complete within 10 minutes
- All JSON artifacts must be valid parseable JSON
- No unhandled exceptions or stack traces in output
- Clear PASS/FAIL indicators for each phase
- Summary statistics at end of run
