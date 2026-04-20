# LangGraph Path Matrix — AGENT-FORENSIC-002 V2 (Updated)

| Path | Route | Thread ID | LLM Response | Tool Called | Approval Created | DB Side Effect | Thread State | Backend SQL Proof | Verdict |
|------|-------|-----------|-------------|------------|-----------------|---------------|-------------|------------------|---------|
| A | Chat->END | f002-path-a-001 | NO (auth required) | NONE (unverified) | NONE (unverified) | NONE (unverified) | UNVERIFIED | N/A | FAIL (auth blocked) |
| B | Chat->tool->Chat | f002-path-b-001 | NO (auth required) | UNVERIFIED | NONE (unverified) | NONE (unverified) | UNVERIFIED | N/A | FAIL/UNVERIFIED |
| C | Chat->gate->INT | f002-path-c-001 | NO (auth required) | transition_deal (from DB; status approved) | YES (approved row) | tool_execution exists | UNVERIFIED | DL-0020=qualified (unchanged) | FAIL (auth blocked / not pending) |
| D | approve->exec->Chat | f002-path-c-001 | UNVERIFIED | transition_deal executed | approval approved | tool_execution success=true, stage unchanged | UNVERIFIED | DL-0020=qualified (unchanged) | FAIL (phantom success) |
| E | reject->END | f002-path-e-001 | UNVERIFIED | NONE | YES (rejected row) | NONE | UNVERIFIED | DL-0020=qualified (unchanged) | FAIL/UNVERIFIED |

Note: HITL interrupt + resume observed for f002-restart-001 (approval persisted across restart). See 3d_restart_resume.txt. Stage still unchanged (phantom success).
