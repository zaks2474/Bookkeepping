# Finding-to-Fix Matrix — AGENT-BRAIN-REMEDIATION-R3

| Issue ID | Severity | Description | Phase | Fix Task | Before Evidence | After Evidence | Status |
|----------|----------|-------------|-------|----------|-----------------|----------------|--------|
| ZK-BRAIN-ISSUE-0001 | P0 | create_deal not in HITL_TOOLS | Phase 0 | P0.1 | p0_hitl_tools_before.txt | p0_create_deal_hitl_test.txt | ✅ FIXED |
| ZK-BRAIN-ISSUE-0002 | P0 | No grounding enforcement | Phase 0 | P0.2 | p0_system_prompt_before.txt | p0_grounding_test.txt | ✅ FIXED |
| ZK-BRAIN-ISSUE-0003 | P0 | Langfuse not configured | Phase 0 | P0.3 | p0_langfuse_config_before.txt | p0_langfuse_config_after.txt | ⏸️ DEFERRED |
| ZK-BRAIN-ISSUE-0004 | P0 | actor_id not validated | Phase 0 | P0.4 | p0_auth_flow_before.txt | p0_auth_adversarial.txt | ⚠️ PARTIAL |
| ZK-BRAIN-ISSUE-0005 | P2 | Long-term memory disabled | Phase 3 | P3.1 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0006 | P2 | No deal-scoped memory | Phase 3 | P3.2 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0007 | P1 | No M&A domain intelligence | Phase 4 | P4.1 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0008 | P1 | No tool call budget | Phase 1 | P1.4 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0009 | P1 | No prompt versioning | Phase 2 | P2.3 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0010 | P1 | No CI gate for evals | Phase 4 | P4.7 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0011 | P1 | No correlation_id propagation | Phase 2 | P2.1 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0012 | P1 | Missing idempotency keys | Phase 1 | P1.3 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0013 | P1 | No ToolResult schema | Phase 1 | P1.1 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0014 | P2 | Hardcoded OpenAI embeddings | Phase 3 | P3.3 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0015 | P1 | No tool try/except | Phase 1 | P1.2 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0016 | P2 | RAG no provenance/freshness | Phase 3 | P3.4 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0017 | P2 | No decision ledger | Phase 2 | P2.6 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0018 | P2 | Hardcoded tool list in prompt | Phase 2 | P2.4 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0019 | P2 | No response logging | Phase 2 | P2.5 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0020 | P1 | Only 10 golden traces | Phase 4 | P4.5 | — | — | IN PROGRESS (now 15) |
| ZK-BRAIN-ISSUE-0021 | P2 | No stage transition rules | Phase 4 | P4.2 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0022 | P2 | Invalid stages in dev mocks | Phase 1 | P1.6 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0023 | P3 | No deal health scoring | Phase 4 | P4.3 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0024 | P3 | No next-step recommendations | Phase 4 | P4.4 | — | — | PENDING |
| ZK-BRAIN-ISSUE-0025 | P2 | No reasoning capture | Phase 2 | P2.6 | — | — | PENDING |

**TOTAL: 25 issues | FIXED: 2 | PARTIAL: 1 | DEFERRED: 1 | PENDING: 21**

## Phase 0 Summary
- **P0.1**: Added create_deal to HITL_TOOLS frozenset
- **P0.2**: Added GROUNDING RULES section to system prompt
- **P0.3**: Langfuse deferred (requires infrastructure)
- **P0.4**: Ownership check verified; full impersonation prevention needs architecture changes
- **P0.5-P0.6**: 5 new golden traces added (GT-011, GT-012, GT-013, GT-017, GT-019)
