# Known Unknown Resolution — Phase 2-3 — AGENT-FORENSIC-002 V2 (Updated)

| # | Unknown | Answer | Evidence |
|---|---------|--------|----------|
| U3 | DEAL_API_URL resolves from container? | YES — http://host.docker.internal:8091, HTTP 200 | 27_connectivity.txt |
| U4 | vLLM model loaded and generating? | PARTIAL — model listed; agent generation blocked by auth | 20_discovery.txt, 21_llm_connectivity.txt |
| U5 | RAG REST accepting queries? | DOWN — {"detail":"Database not connected"} | 24_search_deals.txt |
| U9 | Are approval records ever created? | YES — 6 rows | 39_approval_fields.txt, 3b_final_db.txt |
| U10 | Are tool_executions ever recorded? | YES — 3 rows (transition_deal only) | 34_path_d.txt, 3b_final_db.txt |
| NEW-1 | How many graph nodes (expected 4)? | 4: chat, tool_call, approval_gate, execute_approved_tools | 30_graph_source.txt |
| NEW-2 | Checkpoint memory survive multi-turn? | UNVERIFIED — auth blocked | 38_checkpoints.txt |
| NEW-3 | Idempotency on double-approve? | UNVERIFIED — Not Found/Auth required | 36_idempotency.txt |
| NEW-4 | HITL survive container restart? | YES — approval persisted, resume succeeded | 3d_restart_resume.txt |
| NEW-5 | Concurrent approves handled safely? | YES — 1 success, 1 already claimed | 3e_concurrent_race.txt |
| NEW-6 | Per-user approval isolation? | UNVERIFIED — register/login JSON error, no user JWT | 3f_approval_isolation.txt |
| NEW-7 | Correlation IDs propagate? | PARTIAL — x-request-id only, no backend correlation | 2g_correlation.txt |
| NEW-8 | Prompt injection bypass HITL? | UNVERIFIED — auth blocked, no approval created | 2e_prompt_injection.txt |

**Unverified items remain due to pre-gate auth failures.**
