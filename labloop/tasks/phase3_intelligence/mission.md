# Mission: Phase 3 - Intelligence / Agent Capabilities

## Objective

Implement Phase 3 (Intelligence / Agent Capabilities) for the ZakOps Agent API per the Ultimate Implementation Roadmap v2. This phase adds retrieval capabilities and measurable quality evals.

## Background

- **Repo**: `/home/zaks/zakops-agent-api`
- **Gate Command**: `./scripts/bring_up_tests.sh`
- **Artifacts Directory**: `/home/zaks/zakops-agent-api/gate_artifacts/`
- **Authoritative Docs**: `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`

**Prerequisites Completed:**
- Phase 0: Foundations & Alignment ✅
- Phase 1: Core Infrastructure (Security) ✅
- Phase 2: MVP Build (partial - UI smoke test pending)

**RAG REST Service**: Available at `:8052`

## Scope

### P3-RAG-PROBE-001: RAG REST Contract Probe
- Discover and lock RAG REST endpoints/schema via probe
- Write `gate_artifacts/rag_rest_contract.json`
- Update contract lock pack with RAG REST contract

### P3-EVAL-001: Tool Accuracy Eval
- Implement tool accuracy eval harness
- Define "tool accuracy" precisely:
  - Correct tool selection
  - Schema-valid arguments
  - Expected side effect (when applicable)
  - Idempotency behavior (no duplicate exec)
- Target: **≥95% accuracy on 50 prompts**
- Output `gate_artifacts/tool_accuracy_eval.json` with per-tool breakdown
- Output `gate_artifacts/eval_dataset_manifest.json`

### P3-EVAL-002: Retrieval Eval
- Implement retrieval eval harness
- Target: **recall@5 ≥ 0.80**
- Output `gate_artifacts/retrieval_eval_results.json` including:
  - Dataset version
  - Latency stats
  - Per-query breakdown

### P3-NO-SPLITBRAIN-001: No Split-Brain Retrieval
- Add static scan gate to verify Agent API has no direct pgvector queries
- All retrieval MUST go through RAG REST `:8052` only
- Output `gate_artifacts/no_split_brain_retrieval_scan.log` with `NO_SPLIT_BRAIN: PASSED`

### P3-RAG-INTEGRATION: RAG REST Client Integration
- Implement RAG REST client in Agent API
- Retrieval only via RAG REST (never direct pgvector)
- Integrate with tool gateway for retrieval operations

### Eval Dataset Management
- Define dataset storage path: `evals/datasets/<name>/<version>/...`
- Add `eval_dataset_manifest.json` describing:
  - Provenance
  - Size
  - Allowed data (no secrets)

### Reranker Rubric (Optional)
- Adopt reranker only if:
  - MRR uplift ≥10%
  - Within latency budget
- Record decision in artifacts

## Out of Scope
- Hybrid routing / LiteLLM (Phase 4)
- Queue/DLQ (Phase 5)
- MCP expansion (Phase 4)

## Technical Requirements

- All Phase 0, Phase 1, Phase 2 artifacts must remain PASS
- All baseline invariants (BL-01..BL-14) must remain PASS
- Single gate entrypoint: `./scripts/bring_up_tests.sh`
- All artifacts under `gate_artifacts/`
- No mocks for acceptance runs
- Retrieval via RAG REST only (Decision Lock)

## Constraints from Decision Lock

- Embeddings: BGE-M3 (1024)
- Quality DoD: recall@5 ≥ 0.8
- Single retrieval path (no split-brain)
- Agent API retrieval exclusively via RAG REST :8052

## References

- `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
- `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md` (retrieval via RAG REST only)
- `/mnt/c/Users/mzsai/Downloads/ZakOps-Ultimate-Implementation-Roadmap-combine.v2.md`
