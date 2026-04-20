# QA VERIFICATION + REMEDIATION — QA-AB-R4-VERIFY-001 REPORT

**Date:** 2026-02-05T20:26:29Z
**Auditor:** Codex (GPT-5)
**Target:** AGENT-BRAIN-REMEDIATION-R4 (Deal Tool Data Source Routing)
**Mode:** Verify-Fix-Reverify
**Special Focus:** Schema Alignment / Zod Prevention

## Executive Summary
**VERDICT:** FAIL
**Total Checks:** 66  
**Passed:** 53  
**Failed:** 12  
**Deferred:** 1  
**Skipped:** 0

Key blockers:
- SA2 live agent response capture timed out (cannot verify response structure vs backend).
- SA4 stage alignment fails: dashboard includes stages not present in backend stage set.
- SP1.4 CI tool-list validation fails (missing duckduckgo_search in prompt).
- Golden trace local mode fails (401 — missing auth); CI mode passes.
- REG.5 imports fail (langchain_community missing in host env).
- RT2/RT3/RT6/RT7 have hard failures (mock references, multi-postgres split-brain risk, tool selection ambiguity, double-wrap check timeout).

## Schema Alignment Results
| Layer | Schema Documented | Stages Match | Fields Match |
|-------|-------------------|--------------|--------------|
| Backend API | Y | — | Y |
| Agent ToolResult | Y | N/A | **UNVERIFIED** (SA2 timeout) |
| Dashboard Types | Y | **FAIL** (extra stages) | Y |

## Acceptance Test Results
| Source | Total | Inbound | Screening | Archived | Qualified | Other |
|--------|-------|---------|-----------|----------|-----------|-------|
| Backend API | 25 | 14 | 4 | 4 | 3 | — |
| Agent Response | 25 | 14 | 4 | 4 | 3 | — |
| **MATCH** | Y | Y | Y | Y | Y | Y |

## Gate Results
| Gate | Section | Status | Critical? | Evidence |
|------|---------|--------|-----------|----------|
| V0 | Baseline | PASS | No | v0-baseline/*.json/*.txt |
| SA | Schema Alignment | FAIL | YES | sa2_3 timeout, sa4 stage mismatch |
| TI | Tool Implementation | FAIL | YES | ti1_3, ti2_2 timeouts |
| SP | System Prompt | FAIL | No | sp1_4_tool_count.txt |
| RV | Routing Verification | FAIL | Yes | rv1_2_rag_calls.txt (false positives) |
| GT | Golden Traces | FAIL | Yes | gt1_3_suite_results.txt (401) |
| AT | Acceptance Test | PASS | YES | at1_* |
| REG | Regression | FAIL | No | reg5_imports.txt |
| RT | Red-Team Hardening | FAIL | YES | rt2_3, rt3_2, rt6_3, rt7_2 |

## Red-Team Hardening Results
| RT Gate | Description | Status | Evidence |
|---------|-------------|--------|----------|
| RT1 | Canary/Empty-State | PASS | rt1_* |
| RT2 | Real Backend Proof | **PARTIAL** | rt2_* (no-mock FAIL) |
| RT3 | DB Source-of-Truth | **FAIL** | rt3_2_postgres_containers.txt |
| RT4 | OpenAPI Contract | PASS | rt4_* |
| RT5 | Negative Path Tests | **DEFERRED** | rt5_1_backend_down.txt (manual only) |
| RT6 | Tool Semantics | **FAIL** | rt6_3_selection_tests.txt (ambiguous) |
| RT7 | Response Wrapper | **FAIL** | rt7_2_shape_check.txt (timeout) |
| RT8 | Skip Risk | PASS | rt8_1_skip_check.txt |
| RT9 | Golden Prompt E2E | PASS | rt9_1_golden_prompt.txt |
| RT10 | Scope/Rollback | PASS | rt10_* |

## Discrepancy Investigation Results
| ID | Status | Evidence | Notes |
|----|--------|----------|-------|
| D-1 | RESOLVED | ti1_2_routing_check.txt, rv1_1_logs.txt | Backend API call confirmed |
| D-2 | RESOLVED | ti2_1_search_deals_routing.txt | RAG refs = 0 |
| D-3 | RESOLVED | ti3_1_from_legacy.txt | from_legacy handles ok/error/data |
| D-4 | **FAIL** | sa4_1_stage_comparison.txt | Backend uses subset; dashboard has extra stages |
| D-5 | **FAIL** | sp1_4_tool_count.txt | duckduckgo_search missing in prompt |
| D-6 | RESOLVED | sa4_2_tsc_check.txt, reg6_tsc.txt | tsc --noEmit exit 0 |
| D-7 | RESOLVED | sa4_3_zod_parse.txt | Zod parse OK |
| D-8 | **FAIL** | sa2_3_agent_response.txt | Agent response timed out; no field validation |
| D-9 | **PARTIAL** | gt1_2_trace_content.txt; gt1_3_suite_results*.txt | CI pass, local mode 401 |
| D-10 | RESOLVED | sp1_3_routing_section.txt | TOOL ROUTING present |
| D-11 | RESOLVED | rt1_3_empty_state.txt | Agent reports no matches |
| D-12 | **FAIL** | rt3_2_postgres_containers.txt | Multiple postgres containers running |
| D-13 | **FAIL** | rt2_3_no_mocks.txt | "mock" strings present (comments) |
| D-14 | RESOLVED | rt2_2_correlation.txt | correlation_id propagated |
| D-15 | DEFERRED | rt5_1_backend_down.txt | Manual backend-down test only |
| D-16 | RESOLVED | rt5_2_auth_failure.txt | 401 returned, no stack trace |
| D-17 | RESOLVED | rt5_3_pagination.txt | limit enforced in code |
| D-18 | **FAIL** | rt6_3_selection_tests.txt | tool usage not detectable in response |
| D-19 | **FAIL** | rt7_2_shape_check.txt | timeout prevents wrapper verification |
| D-20 | RESOLVED | rt8_1_skip_check.txt | 0 skip decorators found |

## Coverage Matrix (ALL CELLS FILLED)
| Section | Verification | Status | Evidence | Notes |
|---------|--------------|--------|----------|-------|
| V0 | Agent API healthy | PASS | v0-baseline/agent_health.json | - |
| V0 | Backend API healthy | PASS | v0-baseline/backend_health.json | - |
| V0 | Backend /api/deals returns data | PASS | v0-baseline/deals_availability.txt | - |
| SA1 | Backend schema documented (all fields) | PASS | schema-alignment/sa1_1_backend_fields.txt | - |
| SA1 | Backend stage values extracted | PASS | schema-alignment/sa1_2_backend_stages.txt | - |
| SA2 | list_deals implementation captured | PASS | schema-alignment/sa2_1_list_deals_impl.txt | - |
| SA2 | ToolResult schema documented | PASS | schema-alignment/sa2_2_toolresult_schema.txt | - |
| SA2 | Agent returns matching field names | FAIL | schema-alignment/sa2_3_agent_response.txt | timed out |
| SA3 | Dashboard Deal types found | PASS | dashboard-types/sa3_1_deal_types_grep.txt | - |
| SA3 | Dashboard stage values documented | PASS | dashboard-types/sa3_2_stage_definitions.txt | - |
| SA3 | Zod schemas identified (if any) | PASS | zod-validation/sa3_3_zod_files.txt | - |
| SA4 | Stage values match (case-sensitive) | FAIL | schema-alignment/sa4_1_stage_comparison.txt | dashboard has extra stages |
| SA4 | TypeScript compiles (tsc --noEmit) | PASS | dashboard-types/sa4_2_tsc_check.txt | - |
| SA4 | Zod parsing works (if applicable) | PASS | zod-validation/sa4_3_zod_parse.txt | - |
| TI1 | list_deals exists in deal_tools.py | PASS | tool-implementation/ti1_1_list_deals_exists.txt | - |
| TI1 | list_deals exported in __init__.py | PASS | tool-implementation/ti1_1_list_deals_exists.txt | - |
| TI1 | list_deals uses backend (0 RAG refs) | PASS | tool-implementation/ti1_2_routing_check.txt | - |
| TI1 | list_deals returns ToolResult | FAIL | tool-implementation/ti1_3_toolresult.txt | legacy JSON only |
| TI1 | list_deals LIVE TEST passes | PASS | tool-implementation/ti1_4_live_test.txt | - |
| TI2 | search_deals no longer uses RAG for deals | PASS | tool-implementation/ti2_1_search_deals_routing.txt | - |
| TI2 | search_deals LIVE TEST passes | FAIL | tool-implementation/ti2_2_search_live.txt | timeout |
| TI3 | ToolResult.from_legacy() fix verified | PASS | tool-implementation/ti3_1_from_legacy.txt | - |
| SP | Prompt version v1.4.0-r4 | PASS | system-prompt/sp1_1_version.txt | - |
| SP | list_deals documented in prompt | PASS | system-prompt/sp1_2_list_deals_doc.txt | - |
| SP | TOOL ROUTING section exists | PASS | system-prompt/sp1_3_routing_section.txt | - |
| SP | CI validates 8 tools | FAIL | system-prompt/sp1_4_tool_count.txt | missing duckduckgo_search |
| RV | Agent logs show list_deals called | PASS | routing-verification/rv1_1_logs.txt | - |
| RV | NO RAG calls for deal queries | FAIL | routing-verification/rv1_2_rag_calls.txt | grep matches prompt text |
| RV | Backend /api/deals WAS called | PASS | routing-verification/rv1_3_backend_calls.txt | - |
| GT | GT-032 exists and valid JSON | PASS | golden-traces/gt1_1_new_traces.txt | - |
| GT | GT-033 exists and valid JSON | PASS | golden-traces/gt1_1_new_traces.txt | - |
| GT | GT-034 exists and valid JSON | PASS | golden-traces/gt1_1_new_traces.txt | - |
| GT | Golden trace suite passes ≥95% | FAIL | golden-traces/gt1_3_suite_results.txt | local mode 401; CI pass in gt1_3_suite_results_ci.txt |
| GT | Total traces ≥34 | PASS | golden-traces/gt1_4_trace_count.txt | 34 |
| AT | Backend deal count extracted | PASS | acceptance-test/at1_1_backend_count.txt | - |
| AT | Agent deal count extracted | PASS | acceptance-test/at1_2_agent_response.txt | - |
| AT | COUNTS MATCH EXACTLY | PASS | acceptance-test/at1_3_comparison.txt | - |
| REG | Agent health 200 | PASS | regression/reg1_health.txt | - |
| REG | get_deal works | PASS | regression/reg2_get_deal.txt | used DL-0025 |
| REG | search_deals works | PASS | regression/reg3_search_deals.txt | - |
| REG | HITL triggers for create_deal | PASS | regression/reg4_hitl.txt | pending_approval returned |
| REG | All imports succeed | FAIL | regression/reg5_imports.txt | langchain_community missing |
| REG | TypeScript compiles (exit 0) | PASS | regression/reg6_tsc.txt | - |
| RT1 | Canary deals created across stages | PASS | v0-baseline/rt1_1_canary_created.txt | - |
| RT1 | Full list schema validated (all deals) | PASS | schema-alignment/rt1_2_full_list_validation.txt | - |
| RT1 | Empty-state test passes (no hallucination) | PASS | tool-implementation/rt1_3_empty_state.txt | manual confirm |
| RT2 | Tool logging shows real HTTP calls | PASS | routing-verification/rt2_1_tool_logging.txt | - |
| RT2 | Correlation IDs match agent→backend | PASS | routing-verification/rt2_2_correlation.txt | - |
| RT2 | No mock/stub/cache in tool code | FAIL | routing-verification/rt2_3_no_mocks.txt | comment hits |
| RT3 | All services point to same database | FAIL | v0-baseline/rt3_2_postgres_containers.txt | multiple containers |
| RT3 | DB count matches API count (no split-brain) | PASS | v0-baseline/rt3_1_db_sot.txt | 22==22 at test time |
| RT4 | OpenAPI spec captured | PASS | schema-alignment/rt4_1_openapi.json | - |
| RT5 | Backend-down behavior documented | DEFERRED | regression/rt5_1_backend_down.txt | manual only |
| RT5 | Auth failure returns proper error | PASS | regression/rt5_2_auth_failure.txt | 401 |
| RT5 | Pagination/limit exists for large datasets | PASS | tool-implementation/rt5_3_pagination.txt | - |
| RT6 | Tool descriptions enforce correct selection | PASS | system-prompt/rt6_1_tool_descriptions.txt | - |
| RT6 | Prompt has explicit routing guidance | PASS | system-prompt/rt6_2_tool_guidance.txt | - |
| RT6 | Tool selection tests pass (count→list) | FAIL | system-prompt/rt6_3_selection_tests.txt | tool usage not detectable |
| RT7 | ToolResult schema is canonical | PASS | tool-implementation/rt7_1_toolresult_schema.txt | - |
| RT7 | No double-wrapping in responses | FAIL | tool-implementation/rt7_2_shape_check.txt | timeout |
| RT8 | Skip count documented | PASS | final-gate/rt8_1_skip_check.txt | - |
| RT8 | 0 skipped tests for core R4 suites | PASS | final-gate/rt8_1_skip_check.txt | - |
| RT9 | Golden prompt executed | PASS | acceptance-test/rt9_1_golden_prompt.txt | - |
| RT9 | Golden prompt result matches backend | PASS | acceptance-test/rt9_1_golden_prompt.txt | 25 total |
| RT10 | Edit scope documented | PASS | final-gate/rt10_1_scope.txt | - |
| RT10 | Rollback plan exists | PASS | final-gate/rt10_2_rollback.txt | - |

## Remediation Log
- Refreshed backend deal snapshot and re-ran RT9 golden prompt to eliminate stale-count mismatch (no code changes).
- Re-attempted SA2.3, TI2.2, RT7.2 with max-time=10; all still timed out → left as FAIL with evidence.
- Filled empty evidence files with explicit “no response body” notes to satisfy non-empty requirement.

## Final Verdict
**FAIL** — critical gaps remain (schema alignment, tool list validation, local golden traces, imports, split-brain risk, and multiple red-team gates). Do not certify R4 as complete until failures are remediated and re-verified.

## Recommendations for Next Phase
- Fix prompt tool list (add duckduckgo_search) and re-run SP1.4.
- Align dashboard stage enum with backend or document allowed supersets; re-run SA4.
- Resolve agent invoke timeouts for SA2/TI2/RT7 (optimize LLM latency or provide faster path).
- Run golden traces in local mode with proper service token headers.
- Remove mock/stub references or update RT2.3 check to ignore comments with proof.
- Consolidate postgres containers or document canonical DB; re-run RT3.
- Install/enable langchain_community in the host test env or run REG.5 in container.
