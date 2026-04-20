# AGENT-FORENSIC-002 V2 Report — LLM Tool Wiring & LangGraph Path Verification
**Date:** 2026-02-03T02:05:00Z — 2026-02-03T02:15:30Z
**Auditor:** Claude Code (Opus 4.5)
**Version:** V2 (GPT-5.2 Red-Team Enhanced)

## Pre-Gate Comment (User Override)
Pre-Gate **FAILED** (PG.4, PG.5, PG.6, PG.8). Per explicit user instruction, the audit continued anyway. All Phase 2–3 results should be treated as **conditional** and many checks remain **blocked/unverified** due to auth failures.

## Summary
| Category | Total | Pass | Fail | Graceful-Fail | Blocked/Unverified | Findings |
|----------|-------|------|------|--------------|-------------------|----------|
| Pre-Gate | 8     | 4    | 4    | 0            | 0                 | 2 |
| Phase 2  | 42    | 2    | 13   | 1            | 26                | 3 |
| Phase 3  | 45    | 6    | 10   | 0            | 29                | 4 |
| TOTAL    | 95    | 12   | 27   | 1            | 55                | 9 |

## Gate Evaluation

### Pre-Gate: 4/8 PASS (FAILED)
- **PG.1–PG.3:** PASS (401 on no-auth/JWT) — expected
- **PG.4–PG.5:** FAIL — `/api/v1/sessions` returns 404; only `/api/v1/auth/sessions` exists
- **PG.6:** FAIL — `/agent/invoke` with correct X-Service-Token returned 401
- **PG.7:** PASS — `/api/v1/auth/sessions` returns 200 after login
- **PG.8:** FAIL — `/docs`, `/redoc`, `/metrics` return 200

**Action:** Continued per user override.

### Phase 2 Gate (FAILED)
**Mandatory (ALL must pass):**
| Gate | Check | Result |
|------|-------|--------|
| G2.1 | LLM generates coherent response | FAIL (auth blocked) |
| G2.2 | get_deal triple-proof | FAIL |
| G2.5 | transition_deal HITL triple-proof | FAIL |
| G2.7 | Backend received tool requests | FAIL |
| G2.11 | Streaming >=3 data events | FAIL |

**Mandatory: 0/5 PASS**

**Non-mandatory (>=4 must pass):**
| Gate | Check | Result |
|------|-------|--------|
| G2.3 | search_deals tested | GRACEFUL-FAIL (RAG DB down + auth blocked) |
| G2.4 | duckduckgo_search | FAIL (auth blocked) |
| G2.6 | DEAL_API_URL resolves from agent | PASS |
| G2.8 | Tool errors graceful | FAIL (auth blocked) |
| G2.9 | Canary proves real DB | FAIL |
| G2.10 | Agent DB has new records | FAIL (no net delta) |
| G2.12 | Tool source matches expected | FAIL (3 @tool found; duckduckgo is BaseTool) |
| G2.13 | Security regression | FAIL (endpoint mismatch) |
| G2.14 | Prompt injection blocked by HITL | FAIL/UNVERIFIED (auth blocked) |
| G2.15 | Output sanitization invoked | PASS (code evidence only) |
| G2.16 | Correlation IDs propagate | FAIL |

**Non-mandatory: 2/11 PASS**
**Phase 2 Gate: FAIL**

### Phase 3 Gate (FAILED)
**Mandatory (ALL must pass):**
| Gate | Check | Result |
|------|-------|--------|
| G3.4 | Path C — HITL interrupt, pending approval | FAIL (auth blocked; status approved, not pending) |
| G3.5 | Path D — approve->execute changes stage | FAIL (phantom success) |
| G3.9 | Idempotency (no double-execute) | FAIL/UNVERIFIED (Not Found/Auth required) |
| G3.13 | Rejection — no side effects (SQL proof) | FAIL/UNVERIFIED (API reject failed) |

**Mandatory: 0/4 PASS**

**Non-mandatory (>=5 must pass):**
| Gate | Check | Result |
|------|-------|--------|
| G3.1 | Graph source documented | PASS |
| G3.2 | Path A (Chat->END) | FAIL (auth blocked) |
| G3.3 | Path B (tool_call) | FAIL (auth blocked) |
| G3.6 | Path E (reject) | FAIL/UNVERIFIED |
| G3.7 | Checkpoint durability | FAIL/UNVERIFIED (auth blocked) |
| G3.8 | Approval field completeness | PASS |
| G3.10 | Audit log >=5 event types | PASS |
| G3.11 | tool_executions populated | PASS |
| G3.12 | Backend SQL confirms stage change | FAIL (stage unchanged) |
| G3.14 | HITL survives restart | PASS |
| G3.15 | Concurrent approvals safe | PASS |
| G3.16 | Approval ownership isolation | FAIL/UNVERIFIED (no user JWT) |

**Non-mandatory: 6/12 PASS**
**Phase 3 Gate: FAIL**

## Known Unknown Resolutions (Phase 2-3)
| # | Unknown | Answer | Evidence |
|---|---------|--------|----------|
| U3 | DEAL_API_URL resolves from container? | YES — http://host.docker.internal:8091, HTTP 200 | 27_connectivity.txt |
| U4 | vLLM model loaded and generating? | PARTIAL — model listed; agent generation blocked by auth | 20_discovery.txt, 21_llm_connectivity.txt |
| U5 | RAG REST accepting queries? | DOWN — {"detail":"Database not connected"} | 24_search_deals.txt |
| U9 | Are approval records ever created? | YES — 6 rows | 39_approval_fields.txt, 3b_final_db.txt |
| U10 | Are tool_executions ever recorded? | YES — 3 rows (transition_deal only) | 34_path_d.txt, 3b_final_db.txt |
| NEW-1 | Graph nodes (expected 4)? | 4 confirmed | 30_graph_source.txt |
| NEW-2 | Checkpoint memory multi-turn? | UNVERIFIED (auth blocked) | 38_checkpoints.txt |
| NEW-3 | Idempotency double-approve? | UNVERIFIED (Not Found/Auth required) | 36_idempotency.txt |
| NEW-4 | HITL survive restart? | YES — approval persisted, resume succeeded | 3d_restart_resume.txt |
| NEW-5 | Concurrent approves safe? | YES — 1 success, 1 already claimed | 3e_concurrent_race.txt |
| NEW-6 | Per-user approval isolation? | UNVERIFIED — registration/login JSON error | 3f_approval_isolation.txt |
| NEW-7 | Correlation IDs propagate? | PARTIAL — x-request-id only | 2g_correlation.txt |
| NEW-8 | Prompt injection bypass HITL? | UNVERIFIED — auth blocked | 2e_prompt_injection.txt |

## Finding Catalog
| F-# | Finding | Severity | Phase | Evidence |
|-----|---------|----------|-------|----------|
| F-001 | /agent/invoke rejects valid X-Service-Token in pre-gate (401) | P0 | PG | pg01_auth_gate.txt |
| F-002 | /agent/approvals accepted Bearer JWT during race test (auth inconsistency / confused deputy) | P0 | 3 | 3e_concurrent_race.txt |
| F-003 | transition_deal returns ok:true but deal stage unchanged (phantom success) | P0 | 3 | 3d_restart_resume.txt, 3c_reject_sql.txt, 34_path_d.txt |
| F-004 | LLM tool args invalid/hallucinated (from_stage/to_stage) | P1 | 3 | 39_approval_fields.txt |
| F-005 | RAG DB disconnected — search_deals degraded | P1 | 2 | 24_search_deals.txt |
| F-006 | /api/v1/sessions endpoint mismatch (404; actual /api/v1/auth/sessions) | P2 | PG/2 | pg01_auth_gate.txt, 21_llm_connectivity.txt |
| F-007 | /docs, /redoc, /metrics exposed without auth | P2 | PG | pg01_auth_gate.txt |
| F-008 | No cross-service correlation ID propagation | P2 | 2 | 2g_correlation.txt |
| F-009 | Rejection path lacks audit_log entries for f002-path-e-001 | P1 | 3 | 3a_audit_log.txt |

## P0 Blockers
- **F-001:** /agent/invoke rejects valid X-Service-Token (401) at pre-gate.
- **F-002:** /agent/approvals accepted Bearer JWT (auth inconsistency / privilege risk).
- **F-003:** transition_deal phantom success (ok:true without stage change).

## P1 High Priority
- **F-004:** LLM tool args invalid/hallucinated (from_stage/to_stage)
- **F-005:** RAG DB disconnected — search_deals degraded
- **F-009:** Rejection path missing audit_log entries

## P2/P3 Lower Priority
- **F-006:** /api/v1/sessions endpoint mismatch (404)
- **F-007:** /docs, /redoc, /metrics exposed without auth
- **F-008:** No cross-service correlation ID propagation

## Evidence Index
| File | Description |
|------|-------------|
| pre_gate/pg01_auth_gate.txt | Pre-gate auth re-validation (8 checks) |
| pre_gate/pg02-pg08 | Individual pre-gate results |
| phase2/20_discovery.txt | Endpoint probes, deal discovery, vLLM models, baseline DB counts |
| phase2/21_llm_connectivity.txt | LLM tests via agent (auth blocked) |
| phase2/22_tool_source.txt | Tool source code inspection |
| phase2/23_get_deal_triple.txt | get_deal triple-proof (blocked) |
| phase2/24_search_deals.txt | search_deals (RAG DB down) |
| phase2/25_duckduckgo.txt | DuckDuckGo search test (blocked) |
| phase2/26_hitl_triple.txt | HITL recognition (blocked) |
| phase2/27_connectivity.txt | Backend connectivity from container |
| phase2/28_streaming.txt | SSE streaming validation (blocked) |
| phase2/29_tool_errors.txt | Tool error handling (blocked) |
| phase2/2a_crossref2.txt | Second deal cross-reference (blocked) |
| phase2/2b_db_records.txt | Agent DB table counts and schemas |
| phase2/2c_canary.txt | Canary test (blocked) |
| phase2/2d_security_regression.txt | Security regression tests |
| phase2/2e_prompt_injection.txt | Prompt injection test (blocked) |
| phase2/2f_output_sanitization.txt | Output sanitization (code evidence) |
| phase2/2g_correlation.txt | Correlation ID tracing |
| phase2/2i_gate.txt | Phase 2 gate evaluation |
| phase3/30_graph_source.txt | LangGraph source inspection |
| phase3/31_path_a.txt | Path A: Chat->END (blocked) |
| phase3/32_path_b.txt | Path B: tool_call (blocked) |
| phase3/33_path_c.txt | Path C: HITL interrupt (blocked) |
| phase3/34_path_d.txt | Path D: approve->execute (phantom success) |
| phase3/35_path_e.txt | Path E: reject (blocked) |
| phase3/36_idempotency.txt | Idempotency (unverified) |
| phase3/38_checkpoints.txt | Checkpoint durability (unverified) |
| phase3/39_approval_fields.txt | Approval field completeness |
| phase3/3a_audit_log.txt | Audit log coverage |
| phase3/3b_final_db.txt | Final DB state |
| phase3/3c_reject_sql.txt | Rejection SQL proof (stage unchanged) |
| phase3/3d_restart_resume.txt | Restart-resume HITL |
| phase3/3e_concurrent_race.txt | Concurrent double-approve race |
| phase3/3f_approval_isolation.txt | Approval ownership isolation (blocked) |
| phase3/3g_matrices.txt | Phase 3 summary |
| phase3/3h_gate.txt | Phase 3 gate evaluation |
| cleanup/test_data_cleanup.txt | Test data inventory |
| matrices/ | 9 populated matrices |

## Verdict
- **Pre-Gate:** 4/8 PASS (FAILED) — continued per user override
- **Phase 2:** Mandatory 0/5 PASS, Non-mandatory 2/11 PASS — **Gate FAIL**
- **Phase 3:** Mandatory 0/4 PASS, Non-mandatory 6/12 PASS — **Gate FAIL**
- **Total:** 12 PASS / 27 FAIL / 1 GRACEFUL / 55 BLOCKED (out of 95)
- **LLM Status:** UNKNOWN via agent (auth blocked); vLLM models listed
- **Tool Pipeline:** PARTIAL (transition_deal executed but no stage change)
- **HITL Lifecycle:** PARTIAL (approvals recorded; restart + race observed; auth inconsistent; phantom success)
- **Checkpoint Durability:** UNVERIFIED (auth blocked)
- **Auth Regression:** INCONSISTENT (Phase2 401; Phase3 /agent/approvals accepted Bearer JWT once)
- **Canary:** FAILED (auth blocked)

**Overall: BLOCKED / CRITICAL FAILURE**

Primary blockers are pre-gate auth failures (service token rejected) and phantom success in transition_deal. The audit continued only because of explicit user override; Phase 2–3 results should be treated as conditional until auth behavior is stable and consistent.
