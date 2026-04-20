# Acceptance Criteria: Phase 3 - Intelligence

## Definition of Done

The task is complete when ALL of the following are true:

### P3-RAG-PROBE-001: RAG REST Contract
- [ ] RAG REST endpoints discovered and documented
- [ ] `gate_artifacts/rag_rest_contract.json` exists
- [ ] Contract includes health endpoint, query endpoint, schema

### P3-EVAL-001: Tool Accuracy Eval
- [ ] Tool accuracy eval harness implemented
- [ ] Eval dataset created with 50 prompts minimum
- [ ] Tool accuracy **≥95%** on eval set
- [ ] `gate_artifacts/tool_accuracy_eval.json` exists with:
  - Per-tool breakdown
  - Error taxonomy
  - Overall accuracy percentage
- [ ] `gate_artifacts/eval_dataset_manifest.json` exists with:
  - Dataset version
  - Provenance
  - Size
  - No secrets certification

### P3-EVAL-002: Retrieval Eval
- [ ] Retrieval eval harness implemented
- [ ] Labeled query set created
- [ ] **recall@5 ≥ 0.80** on eval set
- [ ] `gate_artifacts/retrieval_eval_results.json` exists with:
  - Dataset version
  - recall@5 score
  - Latency stats (P50, P95)
  - Per-query breakdown

### P3-NO-SPLITBRAIN-001: No Split-Brain Retrieval
- [ ] Static scan implemented to detect direct pgvector queries
- [ ] Agent API has NO direct pgvector/embedding table queries
- [ ] All retrieval goes through RAG REST :8052
- [ ] `gate_artifacts/no_split_brain_retrieval_scan.log` contains `NO_SPLIT_BRAIN: PASSED`

### RAG REST Client Integration
- [ ] RAG REST client module implemented
- [ ] Client uses RAG REST :8052 exclusively
- [ ] Client integrated with tool gateway
- [ ] Error handling for RAG REST failures

### Previous Phase Artifacts (Must Not Regress)

#### Phase 0 Artifacts
- [ ] `contract_snapshot.json` still valid
- [ ] `agent_api_contract.json` still valid
- [ ] `ports_md_lint.log` contains `PORTS_MD_LINT: PASSED`
- [ ] `env_no_localhost_lint.log` contains `ENV_NO_LOCALHOST: PASSED`
- [ ] `vllm_lane_verify.json` contains `status == "PASSED"`
- [ ] `gate_registry.json` updated with Phase 3 gates
- [ ] `gate_registry_lint.log` contains `GATE_REGISTRY_LINT: PASSED`

#### Phase 1 Artifacts
- [ ] `encryption_verify.log` contains `ENCRYPTION_VERIFY: PASSED`
- [ ] `kill9_encrypted.log` contains `KILL9_ENCRYPTED: PASSED`
- [ ] `pii_canary_report.json` contains `PII_CANARY: PASSED`
- [ ] `raw_content_scan.log` contains `RAW_CONTENT_SCAN: PASSED`
- [ ] `langfuse_selfhost_gate.log` contains `LANGFUSE_SELFHOST: PASSED`

#### Baseline Invariants (BL-01 to BL-14)
- [ ] All baseline gates still PASS

## Gate Command

```bash
cd /home/zaks/zakops-agent-api && ./scripts/bring_up_tests.sh
```

This command must exit with code 0 for the task to pass.

## Required Phase 3 Artifacts Summary

| Artifact | PASS Marker |
|----------|-------------|
| `rag_rest_contract.json` | Contract schema present |
| `eval_dataset_manifest.json` | Dataset documented |
| `tool_accuracy_eval.json` | Accuracy ≥95% |
| `retrieval_eval_results.json` | recall@5 ≥0.80 |
| `no_split_brain_retrieval_scan.log` | `NO_SPLIT_BRAIN: PASSED` |

## Verification Steps

1. Run `./scripts/bring_up_tests.sh` - must exit 0
2. Verify RAG REST contract artifact exists and is valid
3. Verify tool accuracy eval shows ≥95%
4. Verify retrieval eval shows recall@5 ≥0.80
5. Verify no-split-brain scan passes
6. Verify all Phase 0, Phase 1 artifacts still pass
7. Verify all baseline invariants still pass

## Quality Thresholds

| Metric | Threshold | Hard/Soft |
|--------|-----------|-----------|
| Tool accuracy | ≥95% | HARD |
| Retrieval recall@5 | ≥0.80 | HARD |
| No split-brain | 0 violations | HARD |

## Rollback Plan

If retrieval/evals break baseline invariants or safety gates:
1. Disable retrieval path (local-only mode)
2. Revert to last known-good contract snapshot
3. Re-run baseline gate pack and Phase 2 E2E gate
