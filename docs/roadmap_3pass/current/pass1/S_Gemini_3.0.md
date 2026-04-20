# ZakOps Master Implementation Roadmap v2.0 (Gemini 3.0)

**Version:** 2.0.0-GEMINI
**Date:** 2026-01-23T12:00:00Z
**Status:** APPROVED FOR EXECUTION
**Source Authority:** DECISION-LOCK-FILE.md > QA_REPORT.md > Scaffold-Master-Plan > Ultimate-Master-Doc

---

## 1. Executive Summary

We are transitioning from the successful "HITL Spike" (Cycle 3) to **Phase 1: Production Hardening**. The core architectural thesis (LangGraph + PostgresSaver + vLLM) is PROVEN. However, a critical security vulnerability (P0) regarding plaintext data persistence was identified in QA and must be remediated immediately.

**Strategic Focus:**
1.  **Security First:** Close the P0 plaintext gap before expanding functionality.
2.  **Choke Point Control:** Centralize all tool execution through a validated Gateway.
3.  **Local Sovereignty:** Maintain offline capabilities for core deal triage.

**Definition of Done:**
The Agent API (:8095) is deployed in Docker (`zakops-network`), processing requests via the Hybrid Tool Gateway with full RBAC enforcement, zero plaintext PII at rest, and observable traces in self-hosted Langfuse.

---

## 2. Current Baseline (Proven Reality)

Based on `/home/zaks/bookkeeping/docs/hitl_spike/QA_REPORT.md`, the following capabilities are **GREEN** and require no further R&D:

*   **Scaffold:** `wassim249/fastapi-langgraph...` fork is functional.
*   **Orchestration:** LangGraph `interrupt_before=["approval_gate"]` works.
*   **Persistence:** `PostgresSaver` correctly resumes state after `kill -9`.
*   **Concurrency:** Idempotency prevents duplicate tool execution (N=20 test pass).
*   **Inference:** Local vLLM (:8000) is accessible and functional.
*   **API Contract:** MDv2 response schema (`awaiting_approval` status) is implemented.

---

## 3. Hard Constraints (Decision Locks)

Extracted from `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`:

*   **Service Port:** Agent API must listen on **:8095**.
*   **Model:** Qwen2.5-32B-Instruct-AWQ via vLLM (:8000).
*   **DB:** PostgreSQL (pgvector) only. **NO** Qdrant in Phase 1.
*   **Queue:** PostgreSQL `SKIP LOCKED`. **NO** Redis in Phase 1.
*   **Auth:** RBAC (JWT + API Key). **NO** ABAC in Phase 1.
*   **Observability:** Langfuse (Self-Hosted). **NO** LangSmith Hosting.
*   **Tools:** Hybrid (MCP + Direct). **NO** direct DB access from Agent logic.
*   **Privacy:** **NEVER** log raw prompts/responses (hash + length only).

---

## 4. Phase Plan

### Phase 1: Production Hardening (Security & Core)
**Objective:** Secure the persistence layer (P0) and enforce architectural boundaries.
**Scope IN:** PII Encryption, RBAC Middleware, Tool Gateway, Graph Formalization.
**Scope OUT:** Complex RAG flows, Cloud Routing, Task Queue.

*   **Dependencies:** None (Spike complete).
*   **Risks:** Encryption overhead on checkpoints (Target: <50ms latency addition).
*   **Acceptance Gates:**
    *   `run_pii_canary.sh`: Inject canary, grep DB/logs -> FAIL if found in plaintext.
    *   `run_auth_negative_tests.sh`: Verify 403 for unauthorized roles.
    *   `run_gateway_choke_point_test.sh`: Direct tool call -> FAIL.

**Definition of Done:** P0 Security risk closed. RBAC active. Tool Gateway is the only path to execution.

### Phase 2: Agentics & Integration
**Objective:** Implement the "Brain" (Planner/Executor) and Async capabilities.
**Scope IN:** Full LangGraph nodes, Task Queue (SKIP LOCKED), RAG Tool integration.
**Scope OUT:** Performance tuning, Cloud fallback.

*   **Dependencies:** Phase 1 (Tool Gateway).
*   **Risks:** vLLM Tool Parsing fragility with complex schemas.
*   **Acceptance Gates:**
    *   `run_e2e_deal_transition.sh`: Full workflow (Plan -> Approval -> Transition).
    *   `run_queue_soak_test.sh`: 100 concurrent tasks, 0 failures.

### Phase 3: Optimization & Scale
**Objective:** Hybrid cloud routing and high-scale ops.
**Scope IN:** LiteLLM Gateway, Qdrant (conditional), ABAC.

*   **Dependencies:** Phase 2.
*   **Triggers:**
    *   Migrate to Qdrant IF >1M vectors OR P95 retrieval >250ms.
    *   Migrate Queue to Redis IF P95 claim >500ms.

---

## 5. Task Backlog (MECE)

### Security (SEC)
*   **SEC-01** (P0, Builder): Implement `SecurePostgresSaver` wrapper to encrypt `checkpoint` blobs (AES-GCM).
    *   *Gate:* `./scripts/gates/run_pii_canary.sh`
*   **SEC-02** (P0, Builder): Implement RBAC Middleware (validate `iss`, `aud`, `role` claims).
    *   *Gate:* `./scripts/gates/run_auth_negative_tests.sh`
*   **SEC-03** (P1, Builder): Enforce Immutability on `audit_log` (Revoke DELETE/UPDATE).
    *   *Gate:* `./scripts/gates/verify_audit_immutability.sh`

### Tools (TOOL)
*   **TOOL-01** (P0, Builder): Create `HybridToolGateway` singleton (The Choke Point).
    *   *Gate:* `./scripts/gates/run_gateway_choke_point_test.sh`
*   **TOOL-02** (P1, Builder): Implement MCP Client (Streamable-HTTP) inside Gateway.
    *   *Gate:* `./scripts/gates/verify_mcp_connection.sh`
*   **TOOL-03** (P1, Builder): Implement READ tools (`list_deals`, `get_deal`).
    *   *Gate:* `./scripts/gates/run_read_tools_test.sh`

### LangGraph (LG)
*   **LG-01** (P1, Builder): Refactor Spike into formal `Router`, `Planner`, `Executor` nodes.
    *   *Gate:* `./scripts/gates/run_graph_structure_test.sh`
*   **LG-02** (P2, QA): Implement HITL edge case tests (`reject`, `expire`).
    *   *Gate:* `./scripts/gates/run_hitl_edge_case_tests.sh`

### Observability (OBS)
*   **OBS-01** (P1, Builder): Configure Langfuse (Self-Hosted) exporter.
    *   *Gate:* `./scripts/gates/verify_langfuse_trace.sh`
*   **OBS-02** (P1, Builder): Expose `/metrics` (Prometheus/OTel).
    *   *Gate:* `./scripts/gates/verify_otel_metrics.sh`

---

## 6. Top 10 Failure Modes & Mitigations

1.  **Plaintext Data Leak:** (P0) Sensitive deal info stored in checkpoints.
    *   *Mitigation:* SEC-01 (Encryption) + PII Canary Gate in CI.
2.  **Infinite Loops:** Agent gets stuck in reasoning loop.
    *   *Mitigation:* Hard cap of 10 iterations per workflow.
3.  **Tool Hallucination:** Model invents tool arguments.
    *   *Mitigation:* Strict Pydantic validation in Tool Gateway.
4.  **Checkpoint Corruption:** Encryption failures or schema drift.
    *   *Mitigation:* Checkpoint versioning and fallback recovery logic.
5.  **Queue Starvation:** Heavy tasks block lightweight ones.
    *   *Mitigation:* Priority field in `task_queue` (SKIP LOCKED handles this).
6.  **Concurrency Race Conditions:** Double-spend on approvals.
    *   *Mitigation:* `idempotency_key` constraint + Transaction isolation (verified in Spike).
7.  **vLLM OOM:** Context window exceeded.
    *   *Mitigation:* Token counting middleware + Context pruning.
8.  **Orphaned Approvals:** Workflows paused indefinitely.
    *   *Mitigation:* TTL (24h) daemon to auto-expire/reject.
9.  **Audit Tampering:** malicious actor deletes logs.
    *   *Mitigation:* DB-level permission revocation (SEC-03).
10. **Environment Drift:** Dev vs Prod config mismatch.
    *   *Mitigation:* `DECISION-LOCK-FILE.md` enforcement via CI checks.

---

## 7. Open Questions

*   **OQ-01:** Performance impact of AES-GCM encryption on checkpoint latency?
    *   *Test:* Benchmark save time with 1MB blob (Target: <50ms).
*   **OQ-02:** Stability of vLLM "Hermes" parser with nested tool schemas?
    *   *Test:* Run `prompt_eval_suite` against vLLM daily.

---

## 8. Appendix: Evidence Index

*   **P0 Plaintext Risk:** `QA_REPORT.md` (Section 5)
*   **Scaffold Choice:** `ZakOps-Scaffold-Master-Plan-v2.md` (Section 1)
*   **Hard Constraints:** `DECISION-LOCK-FILE.md` (All)
*   **Component Design:** `ZakOps-Ultimate-Master-Document-v2.md` (Section 6)
