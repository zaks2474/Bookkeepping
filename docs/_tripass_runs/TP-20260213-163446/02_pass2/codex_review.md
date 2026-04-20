Could not write to `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/02_pass2/codex_review.md` because the directory is root-owned and this session is read-only (`Permission denied`).

```markdown
# Pass 2 Cross-Review — CODEX
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T17:04:20Z

## DUPLICATES (High Confidence)
Items found by 2+ agents. Merge into a single entry with attribution.

### D-1: Intake Automation Broken (`email_ingestion` dependency gap)
**Reported by:** GEMINI (Finding 1), CODEX (Finding 2)
**Consensus root cause:** Active code imports `email_ingestion` modules, but the package is missing from the repository; no proven always-on inbox->quarantine runner is present.
**Consensus fix:** Implement one explicit ingestion control plane (poller or webhook worker) with deterministic checkpoints and integration tests.
**Evidence verified:** YES

### D-2: Quarantine Deduplication Is Weak
**Reported by:** GEMINI (Finding 4), CODEX (Finding 4)
**Consensus root cause:** Deduplication currently depends on app-level `message_id` checks and lacks robust DB invariants for race/retry/thread variants.
**Consensus fix:** Enforce DB-level idempotency invariants (unique index strategy) and add thread/content-aware dedupe rules with concurrency tests.
**Evidence verified:** YES

### D-3: Canonical Deal/Quarantine Truth Is Backend `zakops`
**Reported by:** GEMINI (Summary), CODEX (Finding 1)
**Consensus root cause:** Backend startup gate enforces canonical DB identity (`zakops`), but external config can still drift.
**Consensus fix:** Keep backend as sole truth owner and add CI/runtime ownership validation for all service envs.
**Evidence verified:** YES

## CONFLICTS
Items where agents disagree. State both positions with evidence.

### C-1: Split-Brain Assessment (Resolved vs Latent)
**Agent A position:** GEMINI states `zakops` is the undisputed source of truth with no split-brain in current architecture.
**Agent B position:** CODEX flags latent split-brain risk from config drift (`agent-api` compose points to `zakops`) plus active legacy filesystem paths (`.deal-registry`).
**Evidence comparison:** Backend gate is real (`zakops-backend/src/api/orchestration/main.py:372`, `zakops-backend/src/api/orchestration/main.py:405`), but agent deployment DB mismatch is also real (`zakops-agent-api/deployments/docker/docker-compose.yml:17` vs `zakops-agent-api/packages/contracts/runtime.topology.json:20`), and filesystem stores remain referenced (`zakops-backend/src/workers/actions_runner.py:53`, `Zaks-llm/src/api/server.py:701`).
**Recommended resolution:** Treat this as "canonical ownership exists, latent split-brain risk remains"; prioritize ownership gates and decommission legacy paths.

### C-2: Quarantine->Deal Quality (Atomic vs Lifecycle-Complete)
**Agent A position:** GEMINI marks `process_quarantine` as transactionally safe and effectively wired.
**Agent B position:** CODEX finds approval bypasses workflow transition/outbox pathways, creating lifecycle side-effect gaps.
**Evidence comparison:** Transaction exists (`zakops-backend/src/api/orchestration/main.py:1603`), but approve path directly inserts deal/events (`zakops-backend/src/api/orchestration/main.py:1648`, `zakops-backend/src/api/orchestration/main.py:1675`) instead of workflow path that writes transition ledger + outbox (`zakops-backend/src/core/deals/workflow.py:227`, `zakops-backend/src/core/deals/workflow.py:248`).
**Recommended resolution:** Keep "atomic" as true but classify lifecycle completeness as unresolved P1 integrity gap.

### C-3: Pass-1 Report Completeness Weighting
**Agent A position:** CLAUDE report declares completion with no findings.
**Agent B position:** GEMINI/CODEX provide concrete findings.
**Evidence comparison:** `claude_report.md` contains a single status line only; no forensic claims or evidence to validate.
**Recommended resolution:** Exclude CLAUDE output from confidence weighting for technical conclusions in this run.

## UNIQUE FINDINGS
Items found by only one agent. Verify if the finding is valid.

### U-1: Missing `correlation_id` in `zakops.quarantine_items` (from GEMINI)
**Verification:** CONFIRMED
**Evidence check:** `quarantine_items` is defined without `correlation_id` (`zakops-backend/db/init/001_base_tables.sql:210`, `zakops-backend/db/init/001_base_tables.sql:236`); migration scan found no add-column for quarantine correlation.
**Should include in final:** YES (traceability gap at ingestion boundary)

### U-2: Missing DB `CHECK` Constraint on Quarantine `status` (from GEMINI)
**Verification:** CONFIRMED
**Evidence check:** `status VARCHAR(50)` is unconstrained (`zakops-backend/db/init/001_base_tables.sql:228`); migration scan found no quarantine status check constraint.
**Should include in final:** YES (data integrity risk)

### U-3: MCP Approve/Reject Route Mismatch (`/review` vs `/process`) (from CODEX)
**Verification:** CONFIRMED
**Evidence check:** MCP calls `/review` in `zakops-backend/mcp_server/server.py:311` and `zakops-backend/mcp_server/server.py:341`; backend route is `/process` in `zakops-backend/src/api/orchestration/main.py:1591`; no `/review` route found.
**Should include in final:** YES (agent action path can fail)

### U-4: Dashboard Email Config UX Not Wired to Runtime Endpoints (from CODEX)
**Verification:** CONFIRMED
**Evidence check:** Dashboard proxies `/api/user/email-config` (`zakops-agent-api/apps/dashboard/src/app/api/settings/email/route.ts:12`) and `/api/user/email-config/test` (`zakops-agent-api/apps/dashboard/src/app/api/settings/email/test/route.ts:10`), but backend has no such route; onboarding step is simulated (`zakops-agent-api/apps/dashboard/src/components/onboarding/steps/EmailSetupStep.tsx:56`).
**Should include in final:** YES (configuration UX/runtime drift)

### U-5: Quarantine Bulk-Delete Contract Drift (from CODEX)
**Verification:** CONFIRMED
**Evidence check:** Client calls `/api/quarantine/bulk-delete` (`zakops-agent-api/apps/dashboard/src/lib/api.ts:942`), while only `[id]/process`, `[id]/delete`, and `health` routes exist under dashboard quarantine API.
**Should include in final:** YES (operational UI path can 404)

### U-6: Legacy Filesystem Truth Paths Still Active (`.deal-registry`) (from CODEX)
**Verification:** CONFIRMED
**Evidence check:** Active references in backend (`zakops-backend/src/workers/actions_runner.py:53`, `zakops-backend/src/actions/memory/store.py:15`) and Zaks-llm CRUD (`Zaks-llm/src/api/server.py:701`, `Zaks-llm/src/api/server.py:794`).
**Should include in final:** YES (shadow pipeline risk)

### U-7: Correlation Propagation Churn Across Layers (from CODEX)
**Verification:** CONFIRMED
**Evidence check:** Dashboard middleware generates/forwards correlation IDs (`zakops-agent-api/apps/dashboard/src/middleware.ts:50`), client library also generates (`zakops-agent-api/apps/dashboard/src/lib/api.ts:378`), backend runs both trace middlewares (`zakops-backend/src/api/orchestration/main.py:451`, `zakops-backend/src/api/orchestration/main.py:457`) with different behavior (`zakops-backend/src/api/shared/middleware/trace.py:91`, `zakops-backend/src/api/shared/middleware/tracing.py:56`).
**Should include in final:** YES (end-to-end traceability risk)

### U-8: Approval Path Bypasses Workflow Outbox/Ledger (from CODEX)
**Verification:** CONFIRMED
**Evidence check:** Direct deal insert on approve (`zakops-backend/src/api/orchestration/main.py:1648`) and event write (`zakops-backend/src/api/orchestration/main.py:1675`) are separate from workflow transition/outbox flow (`zakops-backend/src/core/deals/workflow.py:227`, `zakops-backend/src/core/deals/workflow.py:248`).
**Should include in final:** YES (lifecycle integrity gap)

### U-9: Retention Cleanup Updates Nonexistent Quarantine Columns (from CODEX)
**Verification:** CONFIRMED
**Evidence check:** Cleanup updates `processed_by` and `processing_action` (`zakops-backend/src/core/retention/cleanup.py:299`), but these columns are absent in `quarantine_items` schema (`zakops-backend/db/init/001_base_tables.sql:210`, `zakops-backend/db/init/001_base_tables.sql:236`) and no migration adds them.
**Should include in final:** YES (adjacent data-maintenance defect)

## DRIFT FLAGS
Findings that fall outside declared scope.

### DRIFT-1: Pass-1 CLAUDE Report Contains No Forensic Output (from CLAUDE)
**Why out of scope:** It does not provide mission-required evidence, claims, or remediation rationale; it is a status acknowledgement, not an audit finding.
**Severity if ignored:** Medium

### DRIFT-2: GEMINI Report Contains Corrupted/Injected Completion Text (from GEMINI)
**Why out of scope:** Non-forensic completion chatter is embedded mid-finding (`Finding 4` truncation), reducing precision and making one finding partially unusable.
**Severity if ignored:** Low-Medium

### DRIFT-3: "Runtime Ports Closed" as Primary System Finding (from CODEX)
**Why out of scope:** This is an execution-environment constraint for this run, not a stable architectural defect of intake/quarantine/deal flows.
**Severity if ignored:** Low for product correctness, High for audit confidence if mistaken as product bug.

### DRIFT-4: Some Adjacent Operational Hygiene Checks Exceed Core Intake->Promotion Scope (from CODEX)
**Why out of scope:** Items like retention cleanup column mismatch are adjacent to quarantine operations but not central to intake->approval->deal ground-truth mapping.
**Severity if ignored:** Medium

## SUMMARY
- Duplicates: 3
- Conflicts: 3
- Unique valid findings: 9
- Drift items: 4
- Overall assessment: High confidence on core structural issues (ingestion gap, dedupe weakness, contract drift). Medium confidence on runtime behavior due services/DB being unavailable during this run; static evidence strongly supports prioritizing control-plane hardening and contract enforcement before scale-up.
```