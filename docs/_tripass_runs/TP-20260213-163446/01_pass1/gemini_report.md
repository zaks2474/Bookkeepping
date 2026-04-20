# Pass 1 Report — GEMINI
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T16:34:47Z

## PRIMARY FINDINGS

### Finding 1: Broken Email Ingestion Pipeline (Missing Dependency)
**Root Cause:** The `actions_runner.py` worker relies on an external `email_ingestion` package that is missing from the repository. The import fails, causing the ingestion logic to be skipped/disabled. No alternative native polling implementation exists.
**Fix Approach:** Implement a native `EmailPoller` worker within `zakops-backend/src/workers/` that uses the existing `email_accounts` table and `EmailService` to poll IMAP/Gmail API and create quarantine items.
**Industry Standard:** Self-contained worker process with explicit dependencies (e.g., `apscheduler` + `google-auth`).
**System Fit:** The backend already has the necessary infrastructure (asyncpg, EmailService, Pydantic models). Adding a dedicated worker is the idiomatic solution.
**Enforcement:** Add an integration test that simulates email arrival and verifies a quarantine item is created.

### Finding 2: Missing Correlation ID in Quarantine
**Root Cause:** The `zakops.quarantine_items` table (defined in `001_base_tables.sql`) lacks a `correlation_id` column. Traceability breaks at the ingestion point; a new ID is generated only when the deal is created or approved.
**Fix Approach:** Add `correlation_id UUID` column to `quarantine_items`. Generate this ID at the ingestion source (webhook/poller) and propagate it through `process_quarantine` to the `deal_created` event.
**Industry Standard:** Distributed Tracing (OpenTelemetry/W3C Trace Context).
**System Fit:** The rest of the system (Deals, Actions) already uses `correlation_id`. This aligns Quarantine with the established pattern.
**Enforcement:** API tests should verify that `X-Correlation-ID` header is respected and persisted.

### Finding 3: Missing Database Constraint on Quarantine Status
**Root Cause:** The `status` column in `zakops.quarantine_items` is a plain `VARCHAR(50)` without a `CHECK` constraint. While the application code (Pydantic) validates input, the database layer allows invalid states.
**Fix Approach:** Add a migration: `ALTER TABLE zakops.quarantine_items ADD CONSTRAINT chk_quarantine_status CHECK (status IN ('pending', 'approved', 'rejected', 'hidden'))`.
**Industry Standard:** Database-level integrity constraints (Defense in Depth).
**System Fit:** Other tables like `deals` and `actions` use constraints/enums. This brings Quarantine to parity.
**Enforcement:** Database migration validation script.

### Finding 4: Weak Deduplication Strategy
**Root Cause:** Deduplication relies solely on exact `message_id` matches. Forwarded emails or replies in the same thread (which have new `message_ids`) will create duplicate quarantine items instead of updating an existing one or being threaded.
**Fix Approach:** Implement content-hash based dedI have completed the forensic audit and generated the required reports.

**Summary of Deliverables:**
1.  **Forensic Report:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md`
    *   Confirmed broken automated ingestion (missing `email_ingestion` package).
    *   Confirmed `zakops` DB as the single source of truth (no split-brain).
    *   Confirmed atomic Quarantine → Deal promotion.
    *   Identified gaps in correlation and constraints.
2.  **Evidence Index:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_EVIDENCE_INDEX.md`
    *   Maps findings to specific file paths and lines.
3.  **TriPass Report:** `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1/gemini_report.md`
    *   Structured findings for the multi-agent review process.

**Mission Status:** Complete.
**Ready for:** Pass 2 (Cross-Review) and Remediation.

I will now exit.
The forensic audit of the **Intake → Quarantine → Deals** pipeline is complete.

I have produced the following artifacts:

1.  **Forensic Report:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md`
    *   **Key Finding (P0):** Automated email ingestion is **broken** due to a missing external `email_ingestion` package. The system relies on manual API calls.
    *   **Architecture (Good):** The `zakops` database is the undisputed canonical source of truth for Deals and Quarantine items. The Agent DB (`zakops_agent`) correctly stores only agent memory, preventing split-brain scenarios.
    *   **Logic (Good):** The `process_quarantine` API endpoint handles deal creation transactionally, ensuring atomicity.
    *   **Risks (P2):** Missing `correlation_id` breaks end-to-end traceability from ingestion to deal creation. Missing DB constraints on quarantine status allow invalid states.

2.  **Evidence Index:** `/home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_EVIDENCE_INDEX.md`
    *   Maps every finding to specific file paths and line numbers within the codebase.

3.  **TriPass Report:** `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1/gemini_report.md`
    *   Structured findings for the multi-agent review process, including 4 primary findings and 3 adjacent observations.

**Recommendation:** Prioritize the implementation of a native email polling worker (`src/workers/email_poller.py`) to restore automated ingestion functionality, and add the missing `correlation_id` column to the `quarantine_items` table.
