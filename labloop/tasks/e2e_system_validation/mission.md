# MISSION: ZakOps End-to-End System Validation (HARDENED)

## Objective
Execute comprehensive zero-trust validation of the entire ZakOps system stack. Every component must be verified with evidence artifacts. No assumptions - only proven functionality counts.

## Service Topology (Must All Be Running)
| Service | Port | Health Endpoint |
|---------|------|-----------------|
| Deal API | 8090 | /health |
| Agent API | 8095 | /health |
| Orchestration API | 8091 | /health |
| Dashboard | 3003 | / |
| RAG REST API | 8052 | /health |
| vLLM | 8000 | /health |
| Postgres | 5432 | pg_isready |
| Redis | 6379 | redis-cli ping |

## Validation Phases

### Phase 0: Baseline Service Health
- Verify ALL 8 services respond to health checks
- Evidence: `artifacts/validation/phase0_service_health.json`
- Gate: All services return 200 OK or equivalent success

### Phase 1: Integration Contract Verification
- Verify API contracts match between services
- Test Deal API → Agent API integration
- Test Agent API → Orchestration API integration
- Test Dashboard → All backend APIs
- Evidence: `artifacts/validation/phase1_integration.json`
- Gate: All cross-service calls succeed with valid responses

### Phase 2: Tool Execution Validation
- Execute each registered tool in dry-run or safe mode
- Verify tool schemas match Anthropic tool_use spec
- Test tool error handling
- Evidence: `artifacts/validation/phase2_tools.json`
- Gate: All tools execute without crashes, schemas validate

### Phase 3: Human-in-the-Loop (HITL) Verification
- Verify approval request creation works
- Verify approval webhook delivery
- Test approval/rejection flow end-to-end
- Evidence: `artifacts/validation/phase3_hitl.json`
- Gate: Full approval cycle completes successfully

### Phase 4: Dashboard-Agent Synchronization
- Verify dashboard displays accurate agent state
- Test real-time updates via SSE/WebSocket
- Verify run history matches backend
- Evidence: `artifacts/validation/phase4_dashboard_sync.json`
- Gate: Dashboard reflects backend state within 2 seconds

### Phase 5: Agent Intelligence Validation
- Test agent responds appropriately to prompts
- Verify tool selection logic
- Test multi-turn conversation handling
- Evidence: `artifacts/validation/phase5_intelligence.json`
- Gate: Agent produces coherent, tool-using responses

### Phase 6: Graph Execution Validation
- Test workflow graph creation
- Verify node execution ordering
- Test conditional branching
- Evidence: `artifacts/validation/phase6_graphs.json`
- Gate: Graphs execute in correct order with expected outputs

### Phase 7: Adversarial Testing
- Test malformed inputs (SQL injection, XSS, prompt injection)
- Verify rate limiting works
- Test authentication edge cases
- Evidence: `artifacts/validation/phase7_adversarial.json`
- Gate: All attacks rejected with proper error handling

### Phase 8: Double Verification (Skeptic Pass)
- Re-verify 3 critical paths with different methodology
- Compare results with earlier phases
- Flag any discrepancies
- Evidence: `artifacts/validation/phase8_double_verify.json`
- Gate: Results match with no unexplained discrepancies

## Master Gate Requirements
The master gate script (`tools/validation/master_gate.sh`) MUST:
1. Run all 9 phases (0-8)
2. Generate evidence artifacts for each phase
3. Produce final report with:
   - Overall verdict: PASS/FAIL
   - Phase-by-phase breakdown
   - Evidence file paths
   - Any warnings or notes

## Deliverables
1. `tools/validation/master_gate.sh` - Master gate script
2. `tools/validation/phase_*.sh` or `phase_*.py` - Individual phase scripts
3. `artifacts/validation/phase*_*.json` - Evidence artifacts
4. `artifacts/validation/VALIDATION_FINAL_REPORT.json` - Final report

## Success Criteria
- ALL 9 phases must PASS
- ALL evidence artifacts must exist and be valid JSON
- Final report must have `"verdict": "SYSTEM VALIDATED"`
- No unhandled exceptions or crashes during validation
