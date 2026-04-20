# Infra Decision Round — Innovation Pass Master Index

## Entry: 20260206-0430-56df
- agent_name: Codex
- run_id: 20260206-0430-56df
- report_path: /home/zaks/bookkeeping/docs/INFRA_DECISION_RND_INNOV_PASS1.Codex.20260206-0430-56df.md
- provisional_front_runner: Option 3 — Hybrid Guardrail (Codegen + Slim V4)

## Entry: 20260206-0445-a7c3
- agent_name: Opus
- run_id: 20260206-0445-a7c3
- pass: 2 (Stress Test / Adversarial)
- report_path: /home/zaks/bookkeeping/docs/INFRA_DECISION_RND_INNOV_PASS2.Opus.20260206-0445-a7c3.md
- confirmed_front_runner: Option 3 — Hybrid Guardrail (Codegen + Slim V4)
- confidence: 75%
- forced_ranking: Opt3 (72) > Opt2 (65) > Opt1 (55) > Opt4 (42) > Opt5 (35)
- top_5_green_innovations:
  1. "#4 Typecheck as Release Gate (tsc --noEmit)" — zero cost, immediate value
  2. "#1 Generated Zod as Build Artifact" — highest leverage, kills 500-line hand-written schema
  3. "#8 One-command Sync (make sync-types)" — reduces Claude protocol from 6 steps to 1
  4. "#5 Topology Probe Canary" — compact JSON replaces 426-line bash script for Claude context
  5. "#11 Claude Preflight Bundle" — solves no-persistent-memory constraint directly
- key_finding: Pydantic v2 + OpenAPI 3.1 anyOf-with-null is a real codegen blocker — POC required before committing
- codegen_tool_recommendation: openapi-typescript (types) + thin manual Zod wrappers (not full Zod codegen)
- innovations_killed: #7 Drift Radar Dashboard (overhead), #10 Golden Trace CI (maintenance trap), #12 Langfuse (another service), #14 API Playground (curl exists)

## Entry: 20260206-0444-740d
- agent_name: Codex
- run_id: 20260206-0444-740d
- pass: 3 (FINAL)
- report_path: /home/zaks/bookkeeping/docs/INFRA_DECISION_RND_INNOV_FINAL.Codex.20260206-0444-740d.md
- final_decision: Hybrid Guardrail (Codegen + Slim V4)
- innovation_bundle:
  1. Generated Schemas as Build Artifact (codegen + diff gate)
  2. Typecheck as Release Gate (tsc --noEmit)
  3. One-Command Sync (make sync-types)
  4. Topology Probe Canary (compact JSON)
  5. Claude Preflight Bundle (context capsule)

## Entry: 20260206-0530-b9e1
- agent_name: Opus
- run_id: 20260206-0530-b9e1
- pass: META-QA
- report_path: /home/zaks/bookkeeping/docs/INFRA_DECISION_RND_INNOV_META_QA.Opus.20260206-0530-b9e1.md
- verdict: CONDITIONAL PASS (6 required patches)
- scorecard:
  - Decisiveness: 4/5
  - Correctness under constraints: 4/5
  - Maintainability: 4/5
  - Speed to finish line: 3/5
  - Proof / verifiability: 3/5
  - TOTAL: 18/25
- required_patches:
  1. Address custom openapi.py (302 lines) risk — audit for schema modifications
  2. Explicitly handle 10 POST endpoints without response schemas — add response_model or manual exceptions
  3. Add per-script V4 deletion table (DELETE: schema-diff 650L, phantom 204L, network-capture 302L; KEEP: topology slim, RAG 157L, manifest 156L, enforcement 205L)
  4. Fix pivot plan — concrete 30/60/90 triggers, acknowledge git recovery for deleted scripts, automate detection
  5. Define correlation/tracing gate implementation or downgrade to stretch goal
  6. Name the anyOf nullable trap explicitly in POC deliverables — test in first 48 hours, not "somewhere in 30 days"
- one_sentence_decision: Replace 488-line hand-written Zod with openapi-typescript codegen, enforce via tsc --noEmit in CI, keep V4 topology + RAG routing proof for Claude context, delete 1,150+ lines of redundant bash schema-diffing scripts.
- biggest_risk: Pydantic v2 anyOf nullable codegen — if POC fails on this, entire codegen thesis collapses to V4 fallback. Must test in first 48 hours.

## Entry: IMPLEMENTATION-READY
- agent_name: Opus
- date: 2026-02-06
- pass: FINAL (patched)
- report_path: /home/zaks/bookkeeping/docs/INFRA_STRATEGY_IMPLEMENTATION_READY.md
- status: All 6 META-QA patches applied inline
- base: PASS3 Final (Codex, 20260206-0444-740d)
- patches_from: META-QA (Opus, 20260206-0530-b9e1)
- detail_from: PASS2 14-day ship plan (Opus, 20260206-0445-a7c3)
- changes_rev1:
  1. openapi.py audit added to Day 1-2 deliverables
  2. POST endpoint mitigation defined (add response_model, target <5 manual exceptions)
  3. V4 script deletion table added (DELETE 1,318L, SLIM 426→100L, KEEP 518L)
  4. Pivot plan replaced with concrete 30/60/90 triggers + automated CI detection
  5. Correlation/tracing downgraded from hard gate to 90-day stretch goal
  6. anyOf nullable trap named explicitly — mandated 48-hour POC test
  7. 30/60/90 plan replaced with PASS2's 14-day ship plan (per-day deliverables)
  8. Risk register added from PASS2
  9. Codegen tool decision table added from PASS2
- revision: Rev 2 (423 lines)
- changes_rev2 (external review feedback):
  A1. Correlation ID middleware upgraded from stretch to P0 observability in Phase 5
  A2. Golden Payload Capture added to Phase 6 (spec-vs-reality regression snapshots)
  A3. Feature Scaffolder added as Phase 8 (Days 15-21) — zakops:new-feature CLI, contract-first feature sheets, UI action registry
  B1. ESLint import-ban changed from warn to error for migrated entities
  B2. CI ceiling gate for manual Zod wrapper count added to Phase 5
- total_plan: 21 days (14 days foundation + migration, 7 days scaffolder)
- hard_gates: 8 (up from 6)
