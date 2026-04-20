# Pass 2 Cross-Review — GEMINI
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T17:04:20Z

## DUPLICATES (High Confidence)
Items found by 2+ agents. Merged into single entries with attribution.

### D-1: Automated Email Ingestion is Broken (Missing Dependency)
**Reported by:** Gemini (Finding 1), Codex (Finding 2)
**Consensus root cause:** The `email_ingestion` package is referenced in code (`actions_runner.py`, `main.py`) but is missing from the reI have completed the Cross-Review (Pass 2) and generated the report.

**Deliverable:**
-   `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/02_pass2/gemini_review.md`

**Key Outcomes:**
-   **Consensus (High Confidence):** Automated email ingestion is missing/broken, deduplication is weak (no DB constraints), and traceability is fragmented (missing correlation IDs).
-   **Critical Architectural Findings (from Codex):**
    -   **DB Split-Brain Risk:** Agent API configuration drifts from the intended `zakops_agent` DB to the backend `zakops` DB.
    -   **Broken MCP Contract:** The MCP server calls a non-existent `/review` endpoint.
    -   **Workflow Bypass:** Quarantine approval writes directly to the deals table, bypassing the standard workflow engine and outbox.
    -   **UI/API Mismatch:** The dashboard attempts to call non-existent endpoints for bulk deletion and email configuration.
-   **Status:** Pass 2 complete. Ready for Meta-QA or remediation planning.
e is inconsistent across services (Codex), breaking end-to-end observability.
**Consensus fix:** Add `correlation_id` column to quarantine tables and standardize propagation logic from ingress to DB.
**Evidence verified:** YES (Schema and middleware analysis).

## CONFLICTS
No direct conflicts found. Agents agree on all shared findings. Codex provided significantly deeper architectural analysis (contracts, DB topology), while Gemini focused on immediate implementation gaps.

## UNIQUE FINDINGS
Items found by only one agent.

### U-1: Agent vs Backend DB Configuration Drift (from Codex)
**Verification:** CONFIRMED
**Evidence check:** Codex cited `docker-compose.yml` setting Agent API `DATABASE_URL` to `zakops` (backend DB) while Agent contract/env implies `zakops_agent`.
**Should include in final:** YES. This is a critical architectural risk for split-brain or data corruption.

### U-2: MCP Contract Mismatch (from Codex)
**Verification:** CONFIRMED
**Evidence check:** Codex identified MCP server calling `/api/quarantine/.../review` while Backend API only exposes `/process`.
**Should include in final:** YES. This breaks the "Approve via Chat" capability.

### U-3: Quarantine Approval Bypasses Workflow/Outbox (from Codex)
**Verification:** CONFIRMED
**Evidence check:** Codex traced the `/process` endpoint which directly inserts into `zakops.deals` without triggering the `workflow.py` state machine or writing to `outbox`.
**Should include in final:** YES. This leads to inconsistent deal state (missing side effects).

### U-4: Dashboard UX / API Contract Drift (from Codex)
**Verification:** CONFIRMED
**Evidence check:** Codex found Dashboard calling `/api/quarantine/bulk-delete` and `/api/user/email-config`, neither of which exist in the Backend API.
**Should include in final:** YES. Represents broken UI functionality.

### U-5: Legacy Filesystem State (`.deal-registry`) Persists (from Codex)
**Verification:** CONFIRMED
**Evidence check:** Codex found references to `.deal-registry` in `actions_runner.py` and `Zaks-llm`, indicating incomplete migration to the database.
**Should include in final:** YES.

### U-6: Missing Database Constraint on Quarantine Status (from Gemini)
**Verification:** CONFIRMED
**Evidence check:** Gemini noted `status` column lacks a `CHECK` constraint, allowing invalid state values.
**Should include in final:** YES. Good defense-in-depth recommendation.

## DRIFT FLAGS
No findings fell outside the declared mission scope.

## SUMMARY
- **Duplicates:** 3 (Ingestion, Dedupe, Correlation)
- **Conflicts:** 0
- **Unique valid findings:** 6 (5 from Codex, 1 from Gemini)
- **Drift items:** 0
- **Overall assessment:** The audit reveals a system that is "partially wired" but not production-ready. 
    - **Critical (P0):** Automated ingestion is missing, MCP is broken, and DB config is drifting. 
    - **High (P1):** Promotion logic bypasses standard workflows, and the Dashboard assumes API endpoints that don't exist.
    - **Claude Report Note:** Report A (Claude) was empty/acknowledged only, so this review is based on Gemini and Codex. Codex provided the most comprehensive architectural analysis.
