| Phase | Verification | Status | Evidence | Notes |
|---|---|---|---|---|
| P0 | create_deal in HITL_TOOLS frozenset | PASS | `evidence/phase0/v1_1_hitl_tools.txt` |  |
| P0 | GROUNDING RULES in system.md | PASS | `evidence/phase0/v1_2_grounding_rules.txt` |  |
| P0 | Ownership 403 enforcement | PASS | `evidence/phase0/v1_3_ownership.txt` | See evidence/discrepancies/D-1_ownership_test.txt |
| P0 | GT-011/012/013/017/019 exist + valid | REMEDIATED+PASS | `evidence/phase0/v1_4_golden_traces_p0.txt` | REM-001 (EVALS_ROOT fix) |
| P0 | HITL lifecycle live test | REMEDIATED+PASS | `evidence/phase0/v1_5_hitl_live.txt` | REM-002 (actor_id) |
| P0 | M&A role in system.md | PASS | `evidence/phase0/v1_6_role.txt` |  |
| P1 | ToolResult schema (4 fields) | PASS | `evidence/phase1/v2_1_toolresult_schema.txt` |  |
| P1 | _tool_call try/except inside method | PASS | `evidence/phase1/v2_2_error_handling.txt` |  |
| P1 | add_note SHA-256 idempotency key | PASS | `evidence/phase1/v2_3_idempotency.txt` | No pre-check (D-2) |
| P1 | MAX_TOOL_CALLS budget ENFORCED | PASS | `evidence/phase1/v2_4_budget.txt` | Hard stop in _tool_call (D-3) |
| P1 | Malformed tool call validation | PASS | `evidence/phase1/v2_5_validation.txt` |  |
| P1 | Mock stages fixed (qualified, loi) | PASS | `evidence/phase1/v2_6_mock_stages.txt` |  |
| P1 | ToolResult imported in graph.py | PASS | `evidence/phase1/v2_7_toolresult_import.txt` |  |
| P1 | tool_call_count in GraphState | PASS | `evidence/phase1/v2_8_graphstate.txt` |  |
| P2 | correlation_id 3-layer propagation | PARTIAL | `evidence/phase2/v3_1_correlation.txt` | Header set + echoed; logs/DB missing (D-4) |
| P2 | Langfuse check_health() connectivity | PASS | `evidence/phase2/v3_2_langfuse_health.txt` | Network call via client.trace (D-5) |
| P2 | 4 span utils (turn/tool/llm/hitl) | PASS | `evidence/phase2/v3_3_span_utils.txt` |  |
| P2 | trace_llm_call wired in graph.py | PASS | `evidence/phase2/v3_4_trace_wiring.txt` |  |
| P2 | Prompt versioning v1.3.0-r3 + SHA-256 | PASS | `evidence/phase2/v3_5_prompt_version.txt` |  |
| P2 | PII redaction (email/phone/apikey) | REMEDIATED+PASS | `evidence/phase2/v3_6_pii_redaction.txt` | REM-007 |
| P2 | validate_prompt_tools.py CI runs | REMEDIATED+PASS | `evidence/phase2/v3_7_validate_tools.txt` | REM-003 (CI=true) |
| P2 | Decision Ledger model + migration | REMEDIATED+PASS | `evidence/phase2/v3_8_decision_ledger_model.txt` | Migration applied (REM-004); not wired (D-7) |
| P2 | Health endpoint tracing status | PASS | `evidence/phase2/v3_9_health_tracing.txt` |  |
| P3 | _validate_user_id RAISES (not logs) | FAIL | `evidence/phase3/v4_1_tenant_isolation.txt` | Returns False, no raise (D-8) |
| P3 | forget_user_memory GDPR method | PASS | `evidence/phase3/v4_2_gdpr.txt` |  |
| P3 | RAG fallback CALLED (not dead code) | PASS | `evidence/phase3/v4_3_rag_fallback.txt` |  |
| P3 | Provenance metadata in search results | PASS | `evidence/phase3/v4_4_provenance.txt` |  |
| P3 | Embedding provider config | PASS | `evidence/phase3/v4_5_embedding_config.txt` |  |
| P3 | Memory disabled with feature flag | PASS | `evidence/phase3/v4_6_memory_disabled.txt` |  |
| P4 | M&A domain terms in system.md (≥5) | PASS | `evidence/phase4/v5_1_mna_context.txt` |  |
| P4 | VALID_TRANSITIONS blocks invalid | PASS | `evidence/phase4/v5_2_transition_matrix.txt` |  |
| P4 | get_deal_health in 3 places | PASS | `evidence/phase4/v5_3_deal_health.txt` |  |
| P4 | 7 tools aligned (prompt ↔ registry) | PASS | `evidence/phase2/v3_7_validate_tools.txt` | CI static list (D-6) |
| P4 | 31/31 golden traces exist + valid JSON | REMEDIATED+PASS | `evidence/phase4/v5_5_golden_traces_all.txt` | REM-001 |
| P4 | Golden trace suite passes ≥95% | REMEDIATED+PASS | `evidence/phase4/v5_6_golden_trace_run.txt` | CI mode |
| P4 | system.md at v1.3.0-r3 | PASS | `evidence/phase4/v5_7_final_version.txt` |  |
| REG | Agent API health 200 | PASS | `evidence/regression/vreg_1_health.txt` |  |
| REG | Agent invoke returns response | PASS | `evidence/regression/vreg_2_invoke.txt` | Content indicates RAG/backend fallback |
| REG | Backend API healthy | PASS | `evidence/regression/vreg_3_backend.txt` |  |
| REG | Golden traces 31/31 pass | REMEDIATED+PASS | `evidence/regression/vreg_4_golden_traces.txt` | CI mode |
| REG | All new imports succeed | REMEDIATED+PASS | `evidence/regression/vreg_5_imports.txt` | REM-006 (build_graph) |
| FINAL | All gates PASS | FAIL | `evidence/final-gate/vfinal_1_gate_summary.txt` | P3.1 FAIL + RT/WC failures |
| FINAL | Zero empty evidence files | PASS | `evidence/final-gate/vfinal_2_evidence_completeness.txt` |  |
| FINAL | 7 deferred items verified complete | PASS | `evidence/final-gate/vfinal_3_deferred_items.txt` | Decision ledger not wired |
| FINAL | 4 new files present + non-empty | PASS | `evidence/final-gate/vfinal_4_new_files.txt` |  |
| RT-A | DB Source-of-Truth (split-brain) | FAIL | `evidence/red-team/rt_a_sot_verdict.txt` | Agent DB != backend DB |
| RT-B | Idempotency collision attack | FAIL | `evidence/red-team/rt_b_collision_attempt.json` | No 409; counts missing (no deals table) |
| RT-C | Identity spoof → 403 + audit | FAIL | `evidence/red-team/rt_c_spoof_attempt.txt` | 401, no audit evidence |
| RT-D | HITL bypass attempts blocked | PARTIAL | `evidence/red-team/rt_d_approval_records.txt` | Approvals exist; deal count check failed |
| RT-E | Budget bypass (threads/retries) | FAIL | `evidence/red-team/rt_e_rapid_threads.txt` | 200/000 responses; no enforcement logs |
| RT-F | W3C trace_id end-to-end | FAIL | `evidence/red-team/rt_f_db_trace.txt` | No log/DB correlation |
| RT-G | PII/secret leak test (0 found) | PARTIAL | `evidence/red-team/rt_g_log_leaks.txt` | Logs empty; ledger/tool_executions not proving |
| RT-H | No placeholders / no empty files | PASS | `evidence/red-team/rt_h_verdict.txt` |  |
| HANG | Non-interactive mode enforced | PASS | `evidence/red-team/hang_prevention.txt` |  |
| SKIP | All skips in allowlist | PASS | `evidence/red-team/skip_allowlist.txt` |  |
| WC-1 | Flake check (3 runs consistent) | PASS | `evidence/world-class/wc1_flake_runs.txt` |  |
| WC-2 | Crash recovery (pending preserved) | PARTIAL | `evidence/world-class/wc2_approval_after_restart.txt` | Deal count check failed on agent DB |
