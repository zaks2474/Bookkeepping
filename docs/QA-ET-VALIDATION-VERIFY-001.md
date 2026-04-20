> **POST-CONSOLIDATION NOTE (2026-02-16):** This document references `/home/zaks/zakops-backend/` paths.
> Backend is now at `/home/zaks/zakops-agent-api/apps/backend/` (MONOREPO-CONSOLIDATION-001).
> See `POST-CONSOLIDATION-PATH-MAPPING.md` for the full path translation table.

# MISSION: QA-ET-VALIDATION-VERIFY-001
## Independent QA Verification and Remediation - ET-VALIDATION-001
## Date: 2026-02-15
## Classification: QA Verification and Remediation
## Prerequisite: `/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md` exists with execution evidence (currently partial)
## Successor: `/home/zaks/bookkeeping/docs/QA-ET-VALIDATION-VERIFY-001-COMPLETION.md`

---

## Preamble: Builder Operating Context

The executor already loads standing project controls (`CLAUDE.md`, memory, hooks, deny rules, path-scoped rules, and contract surface discipline). This mission does not restate those global rules; it independently verifies and remediates `ET-VALIDATION-001` with evidence-first QA gates.

---

## Mission Objective

This is an independent QA verification and remediation mission for:
- `/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md` (700 lines, 9 phases, 16 AC, 9 phase gates)
- Checkpoint context: `/home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md` (110 lines; P0 complete, P1-P8 not started)
- Execution source plan: `/home/zaks/bookkeeping/docs/VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md` (915 lines)

This QA mission will:
1. Verify execution state and classify mission mode (`VERIFY_ONLY` vs `EXECUTE_VERIFY`).
2. Verify Phase 0 implementation and close deferred security gap (`G0-12`) or carry explicit phase-7 deferral with evidence.
3. Verify and/or remediate Phases 1-8 to satisfy source gates `G1-01` through `G8-07`.
4. Cross-check AC/OQ consistency (`AC-1` through `AC-16`, with OQ floor `OQ-01` through `OQ-14`).
5. Produce a final scorecard with explicit PASS/FAIL/SKIP/DEFERRED rationale.

Out of scope:
- New feature invention outside source mission scope.
- Architecture redesign beyond source mission constraints.
- Port/path changes unrelated to ET-VALIDATION-001.

### Required Evidence Artifacts

| Artifact | Path | Expected QA Use |
|---------|------|-----------------|
| Source mission | `/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md` | Gate definitions and AC source of truth |
| Checkpoint | `/home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md` | Phase status and prior evidence |
| Exec plan | `/home/zaks/bookkeeping/docs/VALIDATION_ROADMAP_EXEC_PLAN.20260214-1837-vr21exec.md` | Canonical task/gate intent |
| Bridge runbook | `/home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md` | P0/P7 key rotation evidence |
| QA evidence directory | `/home/zaks/bookkeeping/qa-verifications/QA-ET-VALIDATION-VERIFY-001/evidence/` | All tee outputs |

---

## Glossary

| Term | Definition |
|------|-----------|
| VERIFY_ONLY | QA mode where all source phases are already executed; QA only verifies/remediates deltas |
| EXECUTE_VERIFY | QA mode triggered when source phases are incomplete; missing work is executed then verified |
| OQ floor | Operational Quarantine minimum acceptance set (`OQ-01` through `OQ-14`) |
| Gate evidence | Tee-captured command output proving a specific PF/VF/XC/ST check |
| Deferred gate | A gate intentionally postponed with explicit reason and successor phase for closure |

---

## Anti-Pattern Examples

### WRONG: Declaring PASS without gate evidence
```text
VF-03 PASS. UI looks good.
```

### RIGHT: Evidence-backed PASS with criterion match
```text
VF-03 PASS.
Evidence: /home/zaks/bookkeeping/qa-verifications/QA-ET-VALIDATION-VERIFY-001/evidence/VF-03-2-optimistic-locking.txt
Criterion met: version guard + 409 conflict path present in backend and UI.
```

### WRONG: Treating incomplete source execution as QA pass
```text
Phase 4 not implemented yet. Marking PASS for now.
```

### RIGHT: Mode-aware handling
```text
Phase 4 missing under checkpoint. Classified NOT_EXECUTED.
Switched to EXECUTE_VERIFY mode, implemented remediation, re-ran VF-05 gate.
```

---

## Pre-Mortem: Top QA Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Source mission is only partially executed but QA runs as verify-only | HIGH | False confidence and invalid verdict | PF-2 mandatory `QA_MODE` classification |
| 2 | Security gap at SSE path is documented but never re-tested | HIGH | Persistent external exposure risk | VF-01.4 + VF-08.1 + ST-3 hard blocker checks |
| 3 | Gate passes are inferred from code presence without runtime evidence | MEDIUM | Behavioral regressions missed | Enforce tee evidence for every VF/XC/ST gate |
| 4 | Surface sync chain is skipped after remediation edits | MEDIUM | Contract drift between layers | Mandatory `make validate-local` and sync/surface gates |

---

## Pre-Flight

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/qa-verifications/QA-ET-VALIDATION-VERIFY-001/evidence
mkdir -p "$EVIDENCE_DIR"
```

### PF-1: Source Mission Integrity
```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
  rg -n '^## Phase [0-9]' /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
  rg -n '^### Gate P[0-9]' /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md').read_text()
phase_count=len(re.findall(r'^## Phase [0-9]',p,re.M))
ac_count=len(re.findall(r'^### AC-',p,re.M))
gate_count=len(re.findall(r'^### Gate P[0-9]',p,re.M))
print('phase_count=',phase_count)
print('ac_count=',ac_count)
print('phase_gate_count=',gate_count)
raise SystemExit(0 if (phase_count==9 and ac_count==16 and gate_count==9) else 1)
PY
} | tee "$EVIDENCE_DIR/PF-1-source-mission-integrity.txt"
```
**PASS if:** 9 phases, 16 ACs, 9 phase gates are detected.

### PF-2: Checkpoint Status and QA Mode Selection
```bash
{
  echo "=== PF-2 CHECKPOINT STATUS ==="
  cat /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md
  python3 - <<'PY'
from pathlib import Path
import re
text=Path('/home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md').read_text()
rows=re.findall(r'\|\s*(P\d)\s*[^|]*\|\s*([A-Z_ ]+)\s*\|',text)
if not rows:
    print('QA_MODE=UNKNOWN')
    raise SystemExit(1)
status={k:v.strip() for k,v in rows}
complete=[k for k,v in status.items() if 'COMPLETE' in v]
pending=[k for k,v in status.items() if 'NOT STARTED' in v or 'IN PROGRESS' in v]
print('COMPLETE_PHASES=',','.join(sorted(complete)) or 'NONE')
print('PENDING_PHASES=',','.join(sorted(pending)) or 'NONE')
mode='VERIFY_ONLY' if len(pending)==0 else 'EXECUTE_VERIFY'
print('QA_MODE='+mode)
PY
} | tee "$EVIDENCE_DIR/PF-2-checkpoint-status.txt"
```
**PASS if:** `QA_MODE` is emitted (`VERIFY_ONLY` or `EXECUTE_VERIFY`).

### PF-3: Validation Baseline
```bash
{
  echo "=== PF-3 VALIDATION BASELINE ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && npx tsc --noEmit
} | tee "$EVIDENCE_DIR/PF-3-validation-baseline.txt"
```
**PASS if:** both commands exit 0. If fail, stop and classify `BASELINE_BROKEN`.

### PF-4: Service Health Snapshot
```bash
{
  echo "=== PF-4 SERVICE HEALTH SNAPSHOT ==="
  curl -sf http://localhost:8091/health && echo "backend=UP" || echo "backend=DOWN"
  curl -sf http://localhost:8095/health && echo "agent_api=UP" || echo "agent_api=DOWN"
  curl -sf http://localhost:3003 >/dev/null && echo "dashboard=UP" || echo "dashboard=DOWN"
  curl -sf http://localhost:8052/rag/stats >/dev/null && echo "rag=UP" || echo "rag=DOWN"
} | tee "$EVIDENCE_DIR/PF-4-service-health.txt"
```
**PASS if:** output captured. If a service is DOWN, mark live gates as `SKIP(services-down)` rather than FAIL.

### PF-5: P0 Artifact Presence
```bash
{
  echo "=== PF-5 PHASE-0 ARTIFACT PRESENCE ==="
  ls -l /home/zaks/zakops-backend/db/migrations/032_feature_flags.sql
  ls -l /home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md
  ls -l /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
  rg -n 'DEFERRED' /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/PF-5-p0-artifacts.txt"
```
**PASS if:** all files exist and deferred checkpoint note is traceable.

### PF-6: QA Evidence Workspace Readiness
```bash
{
  echo "=== PF-6 EVIDENCE WORKSPACE ==="
  test -d "$EVIDENCE_DIR" && echo "EVIDENCE_DIR_EXISTS=YES" || echo "EVIDENCE_DIR_EXISTS=NO"
  touch "$EVIDENCE_DIR/.write-test" && echo "EVIDENCE_WRITABLE=YES" || echo "EVIDENCE_WRITABLE=NO"
  ls -la "$EVIDENCE_DIR"
} | tee "$EVIDENCE_DIR/PF-6-evidence-workspace.txt"
```
**PASS if:** evidence directory exists and is writable.

---

## Verification Families

## Verification Family 01 — Phase 0 Closure and Deferred Gate Audit (P0, G0-01..G0-12)

### VF-01.1: Feature Flags + Admin API Wiring
```bash
{
  echo "=== VF-01.1 FEATURE FLAGS + API ==="
  rg -n 'feature_flags|email_triage_writes_enabled|shadow_mode|auto_route|delegate_actions|send_email_enabled' \
    /home/zaks/zakops-backend/db/migrations/032_feature_flags.sql \
    /home/zaks/zakops-backend/src/api/orchestration/routers/admin.py \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-01-1-feature-flags-api.txt"
```
**PASS if:** migration and admin API code paths exist.

### VF-01.2: Kill Switch Behavior and Cache Latency Risk
```bash
{
  echo "=== VF-01.2 KILL SWITCH PATH ==="
  rg -n 'email_triage_writes_enabled|writes_disabled|Kill switch|get_flag|TTL|cache' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-backend/src/api/orchestration/feature_flags.py
} | tee "$EVIDENCE_DIR/VF-01-2-kill-switch-cache.txt"
```
**PASS if:** write-path guard exists. Mark `MAJOR` if implementation cannot satisfy gate intent (<1s) under current cache model.

### VF-01.3: Bridge Auth Bypass Removed
```bash
{
  echo "=== VF-01.3 BRIDGE AUTH ENFORCEMENT ==="
  rg -n 'Bearer|Authorization|auth bypass|/sse|/mcp|/messages|ZAKOPS_BRIDGE_API_KEY' \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-01-3-bridge-auth.txt"
```
**PASS if:** bypass code is absent and auth middleware path is evident for bridge routes.

### VF-01.4: Deferred G0-12 Validation (SSE/Live Exposure)
```bash
{
  echo "=== VF-01.4 G0-12 DEFERRED CHECK ==="
  curl -si http://localhost:9100/sse | head -n 20
  curl -si http://localhost:9100/mcp | head -n 20
  curl -si http://localhost:9100/messages/ | head -n 20
} | tee "$EVIDENCE_DIR/VF-01-4-g0-12-deferred.txt"
```
**PASS if:** unauthorized requests are blocked. If SSE remains open, classify `SECURITY_GAP` and route to Phase 7 remediation.

**Gate VF-01:** All 4 checks pass, or unresolved item is explicitly classified with remediation plan and retest target.

---

## Verification Family 02 — Canonical Schema and Contract Enforcement (P1, G1-01..G1-12)

### VF-02.1: Migration and Rollback Existence
```bash
{
  echo "=== VF-02.1 PHASE-1 MIGRATIONS ==="
  ls -l /home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2.sql
  ls -l /home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2_rollback.sql
} | tee "$EVIDENCE_DIR/VF-02-1-phase1-migrations.txt"
```
**PASS if:** both files exist. If missing and `QA_MODE=EXECUTE_VERIFY`, classify `NOT_EXECUTED` and implement before re-verification.

### VF-02.2: Backend Model Strictness and Schema Version Enforcement
```bash
{
  echo "=== VF-02.2 QUARANTINE MODEL STRICTNESS ==="
  rg -n 'QuarantineCreate|extra=.*forbid|schema_version|source_message_id|email_body_snippet|ConfigDict' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-02-2-model-strictness.txt"
```
**PASS if:** strict key handling and schema-version validation are implemented.

### VF-02.3: Bridge Expanded Tool Contract
```bash
{
  echo "=== VF-02.3 BRIDGE SCHEMA EXPANSION ==="
  rg -n 'zakops_inject_quarantine|source_message_id|email_subject|schema_version|field_confidences|extraction_evidence|attachments|routing_reason' \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-02-3-bridge-schema.txt"
```
**PASS if:** expanded parameters and validation paths are present.

### VF-02.4: Transitional Subject Compatibility
```bash
{
  echo "=== VF-02.4 SUBJECT COALESCE ==="
  rg -n 'COALESCE\(email_subject, subject\)|display_subject|email_subject' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/VF-02-4-subject-coalesce.txt"
```
**PASS if:** transitional subject handling is explicit.

**Gate VF-02:** `G1-01` through `G1-12` are evidenced as PASS or remediated then re-tested.

---

## Verification Family 03 — Quarantine UX Operationalization (P2, G2-01..G2-13)

### VF-03.1: List/Detail Field Coverage
```bash
{
  echo "=== VF-03.1 LIST + DETAIL COVERAGE ==="
  rg -n 'email_subject|sender_name|classification|urgency|confidence|source_type|received_at|triage_summary|field_confidences|extraction_evidence' \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/VF-03-1-list-detail-coverage.txt"
```
**PASS if:** required operational fields are rendered in UI code.

### VF-03.2: Optimistic Locking + 409 Handling
```bash
{
  echo "=== VF-03.2 OPTIMISTIC LOCKING ==="
  rg -n 'WHERE id = .*version|version =|409|conflict|Item already processed' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/VF-03-2-optimistic-locking.txt"
```
**PASS if:** versioned update and 409 handling are present end-to-end.

### VF-03.3: Escalate, Reject-Reason, and Bulk Actions
```bash
{
  echo "=== VF-03.3 ESCALATE + REJECT + BULK ==="
  ls -l /home/zaks/zakops-backend/db/migrations/034_quarantine_escalate.sql
  rg -n 'escalate|Needs Review|reject_reason|bulk approve|bulk reject' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/VF-03-3-escalate-reject-bulk.txt"
```
**PASS if:** all three capabilities are implemented.

### VF-03.4: Surface 9 Compliance Signals
```bash
{
  echo "=== VF-03.4 SURFACE-9 LOGGING COMPLIANCE ==="
  rg -n 'console.warn|console.error|degradation|unexpected' \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/VF-03-4-surface9-logging.txt"
```
**PASS if:** expected degradation uses warn, unexpected uses error.

**Gate VF-03:** `G2-01` through `G2-13` pass with UI/API evidence.

---

## Verification Family 04 — Agent Configuration Handoff (P3, G3-01..G3-07)

### VF-04.1: Handoff Artifact Exists
```bash
{
  echo "=== VF-04.1 LANGSMITH HANDOFF ARTIFACT ==="
  ls -l /home/zaks/bookkeeping/docs/LANGSMITH_AGENT_CONFIG_SPEC.md
  wc -l /home/zaks/bookkeeping/docs/LANGSMITH_AGENT_CONFIG_SPEC.md
} | tee "$EVIDENCE_DIR/VF-04-1-handoff-artifact.txt"
```
**PASS if:** artifact exists and is non-trivial.

### VF-04.2: Required Sections in Handoff Artifact
```bash
{
  echo "=== VF-04.2 HANDOFF REQUIRED SECTIONS ==="
  rg -n 'system prompt|sub-agent|deterministic payload|schema_version|required fields|golden payload|classification rules|eval' \
    /home/zaks/bookkeeping/docs/LANGSMITH_AGENT_CONFIG_SPEC.md
} | tee "$EVIDENCE_DIR/VF-04-2-handoff-sections.txt"
```
**PASS if:** required contract/config sections are present.

### VF-04.3: Execution Evidence for G3 Gates
```bash
{
  echo "=== VF-04.3 PHASE-3 EVIDENCE PRESENCE ==="
  rg -n 'G3-01|G3-02|G3-03|G3-04|G3-05|G3-06|G3-07' \
    /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/VF-04-3-phase3-gates.txt"
```
**PASS if:** phase-3 completion evidence exists; otherwise classify `NOT_EXECUTED` and execute+verify.

**Gate VF-04:** `G3-01` through `G3-07` are verified or remediated in-scope.

---

## Verification Family 05 — Promotion Pipeline Integrity (P4, G4-01..G4-09)

### VF-05.1: Duplicate Prevention and Thread Mapping
```bash
{
  echo "=== VF-05.1 DUPLICATE PREVENTION + THREAD MAP ==="
  rg -n 'source_thread_id|email_threads|deal_created|Thread already linked|created_deal_id' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-05-1-duplicate-thread-map.txt"
```
**PASS if:** duplicate-avoidance and thread-link logic exists.

### VF-05.2: Undo Approval Endpoint + UI
```bash
{
  echo "=== VF-05.2 UNDO APPROVAL ==="
  rg -n 'undo-approve|undo approve|archived|status=pending|admin' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/VF-05-2-undo-approval.txt"
```
**PASS if:** undo path exists with admin guard and state rollback logic.

### VF-05.3: Deals Source Indicator
```bash
{
  echo "=== VF-05.3 DEAL SOURCE INDICATOR ==="
  rg -n 'From Quarantine|Email Triage|quarantine_item_id|source indicator' \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/page.tsx \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx
} | tee "$EVIDENCE_DIR/VF-05-3-deal-source-indicator.txt"
```
**PASS if:** source indicator rendering path exists.

**Gate VF-05:** `G4-01` through `G4-09` pass with DB/API/UI evidence.

---

## Verification Family 06 — Auto-Routing Behavior (P5, G5-01..G5-08)

### VF-06.1: Routing Decision Logic + routing_reason
```bash
{
  echo "=== VF-06.1 ROUTING DECISION LOGIC ==="
  rg -n 'auto_route|routing_reason|routing_conflict|routed_to' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-06-1-routing-reason.txt"
```
**PASS if:** routing path and explicit reason output are present.

### VF-06.2: Conflict Resolution UI + Thread Relinking
```bash
{
  echo "=== VF-06.2 CONFLICT UI + THREAD RELINK ==="
  rg -n 'conflict|re-link|linked threads|/threads|add/remove/move' \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-06-2-conflict-relink.txt"
```
**PASS if:** conflict UI and relinking endpoints are implemented.

**Gate VF-06:** `G5-01` through `G5-08` are verified by route behavior evidence.

---

## Verification Family 07 — Collaboration Contract (P6, G6-01..G6-09)

### VF-07.1: Delegated Tasks Schema
```bash
{
  echo "=== VF-07.1 DELEGATED TASKS MIGRATION ==="
  ls -l /home/zaks/zakops-backend/db/migrations/035_delegated_tasks.sql
  rg -n 'delegated_tasks|dead_letter|max_attempts|status' \
    /home/zaks/zakops-backend/db/migrations/035_delegated_tasks.sql
} | tee "$EVIDENCE_DIR/VF-07-1-delegated-schema.txt"
```
**PASS if:** table and state-machine fields are present.

### VF-07.2: Delegation APIs and Flag Controls
```bash
{
  echo "=== VF-07.2 DELEGATION APIS + FLAGS ==="
  rg -n 'delegate_actions|send_email_enabled|/delegate|/tasks|report_task_result|zakops_get_deal_status|zakops_list_recent_events' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-07-2-delegation-apis-tools.txt"
```
**PASS if:** APIs, tools, and flag controls are implemented.

### VF-07.3: Dashboard Task Management Surface
```bash
{
  echo "=== VF-07.3 DASHBOARD TASK MANAGEMENT ==="
  rg -n 'delegated task|dead-letter|retry|task status|task result' \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx
} | tee "$EVIDENCE_DIR/VF-07-3-task-management-ui.txt"
```
**PASS if:** task visibility and dead-letter surfacing exist.

**Gate VF-07:** `G6-01` through `G6-09` pass with schema/API/UI/tool evidence.

---

## Verification Family 08 — Security and Hardening (P7, G7-01..G7-07)

### VF-08.1: Layered Auth Matrix
```bash
{
  echo "=== VF-08.1 AUTH LAYER MATRIX ==="
  curl -si http://localhost:9100/sse | head -n 20
  curl -si http://localhost:9100/mcp | head -n 20
  curl -si http://localhost:9100/messages/ | head -n 20
} | tee "$EVIDENCE_DIR/VF-08-1-auth-matrix.txt"
```
**PASS if:** unauthenticated path is blocked by one or both layers. If not, classify `BLOCKER`.

### VF-08.2: Key Rotation + Redaction Controls
```bash
{
  echo "=== VF-08.2 KEY ROTATION + REDACTION ==="
  rg -n 'rotation|dual-token|comma|redact|token\[:8\]|mask' \
    /home/zaks/bookkeeping/docs/KEY-ROTATION-RUNBOOK.md \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-08-2-rotation-redaction.txt"
```
**PASS if:** dual-token strategy and redaction logic are evidenced.

### VF-08.3: Retention and Purge Endpoint
```bash
{
  echo "=== VF-08.3 RETENTION + PURGE ==="
  rg -n 'retention|PII|purge|/api/quarantine/.*/purge|admin' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/bookkeeping/docs/*.md
} | tee "$EVIDENCE_DIR/VF-08-3-retention-purge.txt"
```
**PASS if:** policy and endpoint controls exist.

**Gate VF-08:** `G7-01` through `G7-07` pass or produce documented blocker remediation loop.

---

## Verification Family 09 — Operational Excellence (P8, G8-01..G8-07)

### VF-09.1: SLO and Monitoring Artifacts
```bash
{
  echo "=== VF-09.1 SLO + MONITORING ARTIFACTS ==="
  rg -n 'SLO|p95|uptime|monitor|alert|shadow burn-in|backup|restore' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md \
    /home/zaks/bookkeeping/docs/*.md
} | tee "$EVIDENCE_DIR/VF-09-1-slo-monitoring.txt"
```
**PASS if:** explicit artifacts exist for SLO, monitoring, and burn-in.

### VF-09.2: Production Safety Flag State
```bash
{
  echo "=== VF-09.2 PRODUCTION FLAG STATE ==="
  rg -n 'shadow_mode=ON|auto_route=OFF|delegate_actions=OFF|send_email_enabled=OFF' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md \
    /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/VF-09-2-production-flag-state.txt"
```
**PASS if:** production safety defaults are documented and traceable.

**Gate VF-09:** `G8-01` through `G8-07` are verified with artifact-backed evidence.

---

## Verification Family 10 — AC/OQ Compliance Matrix (AC-1..AC-16)

### VF-10.1: AC Presence and Mapping
```bash
{
  echo "=== VF-10.1 AC PRESENCE ==="
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
  rg -n 'OQ-01|OQ-02|OQ-03|OQ-04|OQ-05|OQ-06|OQ-07|OQ-08|OQ-09|OQ-10|OQ-11|OQ-12|OQ-13|OQ-14' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/VF-10-1-ac-oq-presence.txt"
```
**PASS if:** all AC-1..AC-16 and OQ references are present.

### VF-10.2: Gate-to-AC Completion Evidence
```bash
{
  echo "=== VF-10.2 GATE TO AC COMPLETION EVIDENCE ==="
  rg -n 'G0-|G1-|G2-|G3-|G4-|G5-|G6-|G7-|G8-' /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12|AC-13|AC-14|AC-15|AC-16' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/VF-10-2-gate-ac-evidence.txt"
```
**PASS if:** each AC has corresponding gate evidence or explicit remediation entry.

**Gate VF-10:** AC matrix is complete, with no unclassified gaps.

---

## Dependency Graph

QA execution order is strictly sequential:

1. Pre-Flight (PF-1..PF-6)
2. Verification Families (VF-01..VF-10)
3. Cross-Consistency (XC-1..XC-4)
4. Stress Tests (ST-1..ST-4)
5. Remediation loop (for every FAIL)
6. Scorecard + Stop Condition verdict

---

## Cross-Consistency Checks

### XC-1: Checkpoint vs Source Mission Agreement
```bash
{
  echo "=== XC-1 CHECKPOINT VS MISSION ==="
  rg -n 'P0|P1|P2|P3|P4|P5|P6|P7|P8' /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md
  rg -n '^## Phase [0-9]' /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/XC-1-checkpoint-vs-mission.txt"
```
**PASS if:** phase naming and ordering are consistent.

### XC-2: Bridge Path Consistency (No Legacy Path Drift)
```bash
{
  echo "=== XC-2 BRIDGE PATH CONSISTENCY ==="
  rg -n '/home/zaks/scripts/agent_bridge/mcp_server.py|apps/agent-api/mcp_bridge/server.py' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md \
    /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/XC-2-bridge-path-consistency.txt"
```
**PASS if:** implementation references use canonical bridge path.

### XC-3: Contract Surface Coverage Consistency
```bash
{
  echo "=== XC-3 SURFACE COVERAGE ==="
  rg -n 'S1|S2|S3|S4|S5|S6|S7|S8|S9|S10|S11|S12|S13|S14|S15|S16' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
  rg -n 'validate-surface15|validate-surface16|make update-spec|make sync-types|make sync-backend-models' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/XC-3-surface-consistency.txt"
```
**PASS if:** all required surfaces and sync-chain gates are referenced.

### XC-4: Bookkeeping Consistency
```bash
{
  echo "=== XC-4 BOOKKEEPING CONSISTENCY ==="
  rg -n 'ET-VALIDATION-001|QA-ET-VALIDATION-VERIFY-001' /home/zaks/bookkeeping/CHANGES.md || true
  ls -l /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/XC-4-bookkeeping-consistency.txt"
```
**PASS if:** mission and QA references are traceable in bookkeeping artifacts.

---

## Stress Tests

### ST-1: Kill-Switch Latency Reality Check
```bash
{
  echo "=== ST-1 KILL SWITCH LATENCY ==="
  rg -n 'TTL|cache|5s|60s|email_triage_writes_enabled' \
    /home/zaks/zakops-backend/src/api/orchestration/feature_flags.py \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/ST-1-kill-switch-latency.txt"
```
**PASS if:** measured/implemented latency does not violate gate intent; otherwise classify `MAJOR` with remediation.

### ST-2: Concurrency Risk Probe
```bash
{
  echo "=== ST-2 CONCURRENCY PROBE ==="
  rg -n 'ON CONFLICT DO NOTHING|idempotency|version|FOR UPDATE|conflict' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/ST-2-concurrency-probe.txt"
```
**PASS if:** dedup + optimistic locking protections are both present.

### ST-3: Auth Surface Probe (REST vs SSE)
```bash
{
  echo "=== ST-3 AUTH SURFACE PROBE ==="
  curl -si http://localhost:9100/sse | head -n 30
  curl -si http://localhost:9100/mcp | head -n 30
  curl -si http://localhost:9100/messages/ | head -n 30
} | tee "$EVIDENCE_DIR/ST-3-auth-surface-probe.txt"
```
**PASS if:** all unauthenticated probe paths are blocked.

### ST-4: Migration Drift and Numbering Safety
```bash
{
  echo "=== ST-4 MIGRATION DRIFT ==="
  ls /home/zaks/zakops-backend/db/migrations | sort -n | tail -n 20
  rg -n '032_|033_|034_|035_' /home/zaks/zakops-backend/db/migrations/*.sql
} | tee "$EVIDENCE_DIR/ST-4-migration-drift.txt"
```
**PASS if:** migration sequence is coherent and references are non-conflicting.

---

## Remediation Protocol

For every FAIL gate:

1. Read evidence output and isolate root cause.
2. Classify failure as one of:
   - `MISSING_FIX`
   - `NOT_EXECUTED`
   - `REGRESSION`
   - `SCOPE_GAP`
   - `PARTIAL`
   - `SECURITY_GAP`
   - `FALSE_POSITIVE`
3. Apply minimal in-scope remediation following source mission constraints.
4. Re-run the specific failing check and its parent VF gate.
5. Re-run baseline safety gate:
   - `cd /home/zaks/zakops-agent-api && make validate-local`
6. Record remediation with: gate ID, classification, fix, retest output, residual risk.

---

## Enhancement Opportunities

### ENH-1: Introduce dedicated Phase evidence directories by gate family (P0-P8)
### ENH-2: Add machine-readable gate ledger JSON per phase for deterministic QA parsing
### ENH-3: Add automated auth-surface smoke test covering `/sse`, `/mcp`, `/messages`
### ENH-4: Add feature-flag propagation latency benchmark in CI
### ENH-5: Add golden payload fixture in repo (`tests/fixtures/golden_quarantine_payload.json`)
### ENH-6: Add cross-repo migration-number lock file to avoid concurrent SQL collisions
### ENH-7: Add dashboard e2e scenario for approve-with-edits and undo-approve
### ENH-8: Add routing conflict replay harness for deterministic P5 regression testing
### ENH-9: Add delegated task dead-letter replay script for P6 resilience testing
### ENH-10: Add operational readiness score exporter for P8 SLO/report consistency

---

## Scorecard Template

```text
QA-ET-VALIDATION-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________
QA_MODE: [ VERIFY_ONLY / EXECUTE_VERIFY ]

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL / SKIP ]
  PF-5: [ PASS / FAIL ]
  PF-6: [ PASS / FAIL ]

Verification Families:
  VF-01 (Phase 0 Closure):   __ / 4 checks PASS
  VF-02 (Phase 1 Contract):  __ / 4 checks PASS
  VF-03 (Phase 2 UX):        __ / 4 checks PASS
  VF-04 (Phase 3 Agent):     __ / 3 checks PASS
  VF-05 (Phase 4 Promotion): __ / 3 checks PASS
  VF-06 (Phase 5 Routing):   __ / 2 checks PASS
  VF-07 (Phase 6 Collab):    __ / 3 checks PASS
  VF-08 (Phase 7 Security):  __ / 3 checks PASS
  VF-09 (Phase 8 Ops):       __ / 2 checks PASS
  VF-10 (AC/OQ Matrix):      __ / 2 checks PASS

Cross-Consistency:
  XC-1: [ PASS / FAIL ]
  XC-2: [ PASS / FAIL ]
  XC-3: [ PASS / FAIL ]
  XC-4: [ PASS / FAIL ]

Stress Tests:
  ST-1: [ PASS / FAIL ]
  ST-2: [ PASS / FAIL ]
  ST-3: [ PASS / FAIL ]
  ST-4: [ PASS / FAIL ]

Totals:
  Checks: __ / 31 PASS
  VF Gates: __ / 10 PASS
  XC Gates: __ / 4 PASS
  ST Gates: __ / 4 PASS

Remediations Applied: __
Deferred (with reason): __
Enhancements Logged: 10 (ENH-1..ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## Executor Self-Check Prompts

- Did I classify `QA_MODE` from checkpoint data before running any VF gate?
- For each PASS, can I point to a specific tee evidence file and criterion match?
- For every remediation, did I re-run both the failing check and its parent gate?
- Before final verdict, did I rerun `make validate-local` and refresh the scorecard totals?

---

## Guardrails

1. No new feature building: this is QA verification/remediation only.
2. Remediate, do not redesign: keep fixes minimal and source-mission aligned.
3. Evidence-first discipline: every PASS must have tee-captured output.
4. Preserve existing deliverables: do not revert previously completed work.
5. Services-down accommodation: live checks may be `SKIP(services-down)` only with explicit evidence.
6. P3 adaptive handling: if phase execution is absent, classify `NOT_EXECUTED` and run execute+verify mode.
7. Security exceptions are blockers: unresolved auth exposure is never downgraded to minor.
8. Surface discipline remains mandatory: do not bypass sync/surface gates for API-touching remediations.
9. Generated files remain protected: regenerate through contract commands only.
10. Port policy: never use or reference decommissioned port 8090.

---

## Stop Condition

Stop when all 10 verification family gates pass (or have explicit, justified `SKIP/DEFERRED/FALSE_POSITIVE`), all required remediations are re-verified, cross-consistency and stress gates are complete, baseline validation passes, and the scorecard is fully populated.

Do not start follow-on feature missions from this QA task. Emit completion artifact and handoff verdict only.
