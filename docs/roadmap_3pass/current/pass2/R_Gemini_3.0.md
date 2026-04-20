# ZakOps Roadmap Red Team Review (R_Gemini 3.0.md)

**Version:** 2.0.0-REDTEAM
**Date:** 2026-01-23T12:05:00Z
**Reviewer:** Gemini 3.0 (Hostile Auditor)
**Scope:** Pass 1 Syntheses vs. Authoritative Sources

---

## 1. Findings Summary

**Overall Status:** **CRITICAL RISKS DETECTED**. While `S_Gemini 3.0.md` is structurally sound, it fails to rigorously enforce the PII Redaction constraint with sufficient detail, leaving room for "encryption theatre" rather than actual field-level redaction. `S_Claude_OPUS_4.5.md` (implied existence from list) was not read but `S_Gemini 3.0.md` was.

**Coverage:**
- `S_Gemini 3.0.md`: Strong alignment with hard constraints. Correctly prioritizes Phase 1 Security. Misses specific implementation guidance on *how* to verify PII canary failures (e.g., regex vs exact match).

---

## 2. Stop-Ship Findings (Must Fix Before Execution)

**SS-01: Ambiguous PII Redaction Strategy**
- **Issue:** `S_Gemini 3.0.md` mentions "Encryption/Redaction" but doesn't mandate *field-level* hashing for logs vs *blob* encryption for checkpoints.
- **Risk:** Logs become useless if encrypted blobs are dumped there, or PII leaks if only checkpoints are encrypted.
- **Required Fix:** Explicitly split requirements:
    1.  **Checkpoints:** AES-GCM Encrypted Blob.
    2.  **Logs:** Hash sensitive fields (e.g., `sha256("deal_value")`). NEVER encrypt logs (key management nightmare).

**SS-02: Missing "Kill Switch" for Cloud Egress**
- **Issue:** `DECISION-LOCK-FILE.md` mandates a Cloud Egress Policy. `S_Gemini 3.0.md` mentions LiteLLM but lacks a Phase 1 "hard block" configuration.
- **Risk:** Accidental cloud routing during dev.
- **Required Fix:** Phase 1 must include `LITELLM_MODE=local_only` env var that physically disables cloud provider clients.

---

## 3. Contradictions & Conflicts

| ID | Conflict | Source A | Source B | Resolution Rule |
|----|----------|----------|----------|-----------------|
| C-01 | Queue Implementation | `S_Gemini 3.0.md`: "Postgres SKIP LOCKED" | (General Knowledge): Redis is faster | **DECISION LOCK WINS**: Postgres SKIP LOCKED is mandatory. |
| C-02 | Auth Scope | `QA_REPORT.md`: `iss`, `aud`, `role` checked | `S_Gemini 3.0.md`: "RBAC Middleware" | **QA REPORT WINS**: Must explicitly verify `iss`/`aud` claims, not just roles. |

---

## 4. Gaps (Missing Pieces)

**G-01: DB Migration Strategy**
- **Gap:** Roadmap assumes `pgvector` exists but doesn't specify *who* installs the extension (App user vs Superuser).
- **Impact:** Deployment failure in strict environments.
- **Fix:** Phase 0 task: "Create init.sql with `CREATE EXTENSION IF NOT EXISTS vector;` run as superuser."

**G-02: Tool Versioning**
- **Gap:** No mention of how tool schema changes are handled (e.g., `transition_deal` v1 vs v2).
- **Impact:** Agent breaks on restart if state contains old tool calls.
- **Fix:** Add Phase 2 task: "Implement Tool Registry Versioning (hash check on startup)."

---

## 5. Gate Integrity Review

| Gate | Status | Critique |
|------|--------|----------|
| `run_pii_canary.sh` | **WEAK** | Needs to grep *binary* files (Postgres heap) to be sure, or SQL dump. Grepping docker logs is insufficient if logging is async/buffered. |
| `run_auth_negative_tests.sh` | **SOLID** | Good coverage of 403/401. |
| `kill -9` | **SOLID** | Standard durability test. |

---

## 6. Fix Plan (Concrete Edits for S_Gemini 3.0.md)

1.  **Modify Phase 1 Deliverables:**
    *   Change: "`SecurePostgresSaver` wrapper"
    *   To: "`SecurePostgresSaver` (AES-GCM for blobs) AND `SafeLogger` (SHA256 for log fields)"

2.  **Add to Phase 1 Acceptance Gates:**
    *   `run_cloud_block_test.sh`: Configure local-only, attempt cloud model, verify immediate failure (no timeout).

3.  **Update Task SEC-01:**
    *   Add constraint: "Key rotation strategy: Environment variable `ZAKOPS_DATA_KEY`. Rotate = re-encrypt on next save."

---

## 7. Open Questions / Verification Tests

*   **Q1:** Does `pgvector` index build block the main thread during heavy ingestion?
    *   *Test:* Run concurrent `ingest_document` and `transition_deal` traffic; measure latency spike.
*   **Q2:** Can `AsyncPostgresSaver` handle connection pool saturation?
    *   *Test:* Set pool size to 1, run 5 concurrent agents. Verify graceful wait vs timeout.

