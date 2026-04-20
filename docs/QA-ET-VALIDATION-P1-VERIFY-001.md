# MISSION: QA-ET-VALIDATION-P1-VERIFY-001
## Independent QA Verification and Remediation - ET-VALIDATION-001 Phase 1
## Date: 2026-02-15
## Classification: QA Verification and Remediation (Phase-Scoped)
## Prerequisite: `/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md` with Phase 1 scope available
## Successor: `/home/zaks/bookkeeping/docs/QA-ET-VALIDATION-VERIFY-001.md` (full mission QA consolidation)

---

## Preamble: Builder Operating Context

This QA mission validates and remediates only Phase 1 of `ET-VALIDATION-001` (`P1-01` through `P1-07`). Standing guardrails from `CLAUDE.md`, memory, hooks, path-scoped rules, and contract surfaces remain active and are referenced, not repeated.

---

## Mission Objective

Execute independent QA verification and remediation for Phase 1 tasks in:
- `/home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md`

Phase under test:
- `P1-01`: Database schema expansion migration + rollback
- `P1-02`: QuarantineCreate strict model + schema_version enforcement
- `P1-03`: QuarantineResponse expansion + `COALESCE(email_subject, subject)`
- `P1-04`: Quarantine POST boundary mapping + required-field enforcement
- `P1-05`: Preview-not-found elimination via inline storage
- `P1-06`: Bridge tool schema expansion + source-aware compatibility
- `P1-07`: Golden payload test

Source gate scope:
- `G1-01` through `G1-12`

Source acceptance scope (phase-relevant):
- `AC-1`, `AC-2`, `AC-9`, `AC-10`, `AC-11`, `AC-12`, `AC-14`, `AC-15`, `AC-16`

Expected output from this QA mission:
1. Verified/remediated Phase 1 implementation.
2. Evidence bundle for each PF/VF/XC/ST check.
3. Final phase scorecard for `P1-01`..`P1-07` and `G1-01`..`G1-12`.

Out of scope:
- Phase 2-8 feature implementation.
- Infrastructure hardening outside what Phase 1 directly depends on.
- New architecture patterns not present in source mission.

---

## Glossary

| Term | Definition |
|------|-----------|
| Phase-Scoped QA | QA mission targeting one phase only, not full mission closure |
| Execute+Verify | Mode used when implementation gaps are found; apply fix then re-verify |
| Golden Payload | Fully populated representative ingestion payload used for contract and UI verification |
| Source-aware validation | Strict requirements for `langsmith_*` while preserving `email_sync` compatibility |
| Gate evidence | Tee-captured output proving specific gate criteria |

---

## Anti-Pattern Examples

### WRONG: Passing G1-08 by checking only code comments
```text
Preview fix looks implemented. Mark PASS.
```

### RIGHT: Passing G1-08 with runtime-backed evidence
```text
PASS only after: inject payload -> API detail response includes email_body_snippet -> UI detail shows preview text with no fallback error.
```

### WRONG: Breaking legacy flow during strict schema rollout
```text
Reject all payloads missing email_subject, including legacy email_sync.
```

### RIGHT: Source-aware compatibility
```text
Enforce strict required fields for langsmith_* payloads only; preserve legacy email_sync acceptance rules.
```

---

## Pre-Mortem: Top QA Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Migration exists but missing key columns (`confidence`, `received_at`, `version`) | HIGH | Phase 2 UI and filtering fail | VF-01 schema-column grep + DB describe checks |
| 2 | Strict model validation breaks legacy `email_sync` | HIGH | Existing ingestion path regression | VF-06 source-aware compatibility check |
| 3 | Preview fix implemented in backend but UI still uses filesystem path | MEDIUM | "Preview not found" persists | VF-05 API+UI dual verification |
| 4 | Bridge contract expansion incomplete (partial parameters only) | MEDIUM | Injection drift and silent field loss | VF-06 param-surface and rejection checks |

---

## Pre-Flight

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/qa-verifications/QA-ET-VALIDATION-P1-VERIFY-001/evidence
mkdir -p "$EVIDENCE_DIR"
```

### PF-1: Source Mission Phase Integrity
```bash
{
  echo "=== PF-1 PHASE-1 INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
  rg -n '^## Phase 1|P1-01|P1-02|P1-03|P1-04|P1-05|P1-06|P1-07|G1-01|G1-12' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md
} | tee "$EVIDENCE_DIR/PF-1-phase1-integrity.txt"
```
**PASS if:** Phase 1 task/gate references exist in source mission.

### PF-2: Checkpoint and Mode Selection
```bash
{
  echo "=== PF-2 CHECKPOINT MODE ==="
  cat /home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md
  python3 - <<'PY'
from pathlib import Path
import re
t=Path('/home/zaks/bookkeeping/mission-checkpoints/MISSION-ET-VALIDATION-001.md').read_text()
m=re.search(r'\|\s*P1\s*[^|]*\|\s*([A-Z_ ]+)\s*\|',t)
if not m:
    print('P1_STATUS=UNKNOWN')
    raise SystemExit(1)
status=m.group(1).strip()
print('P1_STATUS='+status)
mode='VERIFY_ONLY' if 'COMPLETE' in status else 'EXECUTE_VERIFY'
print('QA_MODE='+mode)
PY
} | tee "$EVIDENCE_DIR/PF-2-checkpoint-mode.txt"
```
**PASS if:** `P1_STATUS` and `QA_MODE` are emitted.

### PF-3: Validation Baseline
```bash
{
  echo "=== PF-3 VALIDATION BASELINE ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && npx tsc --noEmit
} | tee "$EVIDENCE_DIR/PF-3-validation-baseline.txt"
```
**PASS if:** both commands exit 0.

### PF-4: Services Snapshot (for live checks)
```bash
{
  echo "=== PF-4 SERVICE SNAPSHOT ==="
  curl -sf http://localhost:8091/health && echo "backend=UP" || echo "backend=DOWN"
  curl -sf http://localhost:3003 >/dev/null && echo "dashboard=UP" || echo "dashboard=DOWN"
  curl -sf http://localhost:8095/health && echo "agent_api=UP" || echo "agent_api=DOWN"
} | tee "$EVIDENCE_DIR/PF-4-service-snapshot.txt"
```
**PASS if:** output captured. If backend/dashboard are down, live gates become `SKIP(services-down)`.

### PF-5: Phase 1 Target Files Presence
```bash
{
  echo "=== PF-5 TARGET FILES ==="
  ls -l /home/zaks/zakops-backend/src/api/orchestration/main.py
  ls -l /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
  ls -l /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/PF-5-target-files.txt"
```
**PASS if:** core files exist.

### PF-6: Evidence Workspace Writable
```bash
{
  echo "=== PF-6 EVIDENCE WORKSPACE ==="
  test -d "$EVIDENCE_DIR" && echo "DIR=OK" || echo "DIR=MISSING"
  touch "$EVIDENCE_DIR/.write-test" && echo "WRITE=OK" || echo "WRITE=FAIL"
  ls -la "$EVIDENCE_DIR"
} | tee "$EVIDENCE_DIR/PF-6-evidence-workspace.txt"
```
**PASS if:** directory exists and write succeeds.

---

## Verification Families

## Verification Family 01 — P1-01 Schema Migration and Rollback

### VF-01.1: Migration and Rollback Files
```bash
{
  echo "=== VF-01.1 MIGRATION FILES ==="
  ls -l /home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2.sql
  ls -l /home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2_rollback.sql
} | tee "$EVIDENCE_DIR/VF-01-1-migration-files.txt"
```
**PASS if:** both files exist.

### VF-01.2: Required Columns Present in Migration
```bash
{
  echo "=== VF-01.2 REQUIRED COLUMNS ==="
  rg -n 'email_subject|sender_name|sender_domain|sender_company|broker_name|email_body_snippet|triage_summary|source_thread_id|schema_version|tool_version|prompt_version|langsmith_run_id|langsmith_trace_url|extraction_evidence|field_confidences|attachments|confidence|received_at|version|company_name|urgency' \
    /home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2.sql
} | tee "$EVIDENCE_DIR/VF-01-2-required-columns.txt"
```
**PASS if:** all required columns are present.

### VF-01.3: Compatibility and Index Clauses
```bash
{
  echo "=== VF-01.3 COMPAT + INDEX ==="
  rg -n 'subject.*preserved|COALESCE|idx_qi_source_thread_id|idx_qi_schema_version|DEFAULT 1' \
    /home/zaks/zakops-backend/db/migrations/033_quarantine_schema_v2.sql \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-01-3-compat-index.txt"
```
**PASS if:** backward-compat references and key indexes/defaults are present.

**Gate VF-01:** Supports `G1-01`, `G1-02`.

---

## Verification Family 02 — P1-02 QuarantineCreate Strict Validation

### VF-02.1: Strict Extra-Key Rejection
```bash
{
  echo "=== VF-02.1 STRICT MODEL ==="
  rg -n 'QuarantineCreate|ConfigDict\(extra=.*forbid|extra=.*forbid' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-02-1-strict-model.txt"
```
**PASS if:** model forbids extra keys.

### VF-02.2: schema_version Enforcement
```bash
{
  echo "=== VF-02.2 SCHEMA VERSION ENFORCEMENT ==="
  rg -n 'schema_version|allowed|1\.0\.0|unknown schema|reject' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-02-2-schema-version.txt"
```
**PASS if:** unknown versions are explicitly rejected.

### VF-02.3: LangSmith Required Field Set
```bash
{
  echo "=== VF-02.3 REQUIRED FIELD RULES ==="
  rg -n 'langsmith_|required|email_subject|sender|classification|source_message_id|correlation_id' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-02-3-required-field-rules.txt"
```
**PASS if:** required fields are enforced for LangSmith payloads.

**Gate VF-02:** Supports `G1-05`, `G1-06`, `G1-07`.

---

## Verification Family 03 — P1-03 QuarantineResponse Expansion and Subject Coalescing

### VF-03.1: Response Model Field Coverage
```bash
{
  echo "=== VF-03.1 RESPONSE FIELDS ==="
  rg -n 'class QuarantineResponse|email_subject|sender_name|sender_domain|sender_company|broker_name|triage_summary|source_thread_id|schema_version|tool_version|prompt_version|langsmith_run_id|langsmith_trace_url|extraction_evidence|field_confidences|attachments|confidence|received_at|version' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-03-1-response-fields.txt"
```
**PASS if:** expanded response fields exist.

### VF-03.2: Subject Coalesce Query
```bash
{
  echo "=== VF-03.2 SUBJECT COALESCE QUERY ==="
  rg -n 'COALESCE\(email_subject, subject\)|display_subject' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-03-2-subject-coalesce.txt"
```
**PASS if:** coalesce logic exists in API query layer.

**Gate VF-03:** Supports `G1-04`, `G1-10`.

---

## Verification Family 04 — P1-04 POST Endpoint Boundary Mapping

### VF-04.1: source_message_id Mapping
```bash
{
  echo "=== VF-04.1 SOURCE MESSAGE ID MAPPING ==="
  rg -n 'source_message_id|message_id|mapped to' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-04-1-message-id-mapping.txt"
```
**PASS if:** bridge/backend mapping is explicit.

### VF-04.2: Dedicated Column Persistence
```bash
{
  echo "=== VF-04.2 DEDICATED COLUMN PERSISTENCE ==="
  rg -n 'INSERT INTO.*quarantine_items|email_body_snippet|triage_summary|field_confidences|extraction_evidence|attachments|received_at|confidence' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-04-2-column-persistence.txt"
```
**PASS if:** endpoint writes expanded fields into dedicated columns.

### VF-04.3: Dedup Behavior Re-Verification Hook
```bash
{
  echo "=== VF-04.3 DEDUP PRIMITIVE PRESENCE ==="
  rg -n 'ON CONFLICT DO NOTHING|dedup|duplicate|existing record' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-04-3-dedup-presence.txt"
```
**PASS if:** dedup logic remains present after schema expansion.

**Gate VF-04:** Supports `G1-04`, `G1-12`.

---

## Verification Family 05 — P1-05 Preview Fix (Inline Storage)

### VF-05.1: Backend Detail Endpoint Returns Inline Preview Fields
```bash
{
  echo "=== VF-05.1 DETAIL ENDPOINT PREVIEW FIELDS ==="
  rg -n 'GET /api/quarantine|email_body_snippet|triage_summary|raw_content|email_body_full' \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-05-1-detail-preview-fields.txt"
```
**PASS if:** detail endpoint includes inline preview fields.

### VF-05.2: Dashboard Detail Uses API Inline Preview
```bash
{
  echo "=== VF-05.2 DASHBOARD PREVIEW RENDER ==="
  rg -n 'email_body_snippet|Preview not found|triage_summary|detail' \
    /home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx
} | tee "$EVIDENCE_DIR/VF-05-2-dashboard-preview-render.txt"
```
**PASS if:** UI consumes inline preview fields and no filesystem-only dependency remains.

### VF-05.3: Runtime Preview Smoke (Live)
```bash
{
  echo "=== VF-05.3 LIVE PREVIEW SMOKE ==="
  curl -sf http://localhost:8091/api/quarantine?limit=1 | head -c 800
} | tee "$EVIDENCE_DIR/VF-05-3-live-preview-smoke.txt"
```
**PASS if:** response contains preview-capable fields; if backend DOWN mark `SKIP(services-down)`.

**Gate VF-05:** Supports `G1-08`, `G1-09`.

---

## Verification Family 06 — P1-06 Bridge Tool Expanded Contract

### VF-06.1: Expanded Parameter Surface
```bash
{
  echo "=== VF-06.1 BRIDGE PARAM SURFACE ==="
  rg -n 'zakops_inject_quarantine|source_message_id|email_subject|sender_name|sender_domain|sender_company|received_at|email_body_snippet|triage_summary|company_name|broker_name|urgency|confidence|extraction_evidence|field_confidences|source_thread_id|tool_version|prompt_version|langsmith_run_id|langsmith_trace_url|attachments|schema_version|correlation_id' \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-06-1-bridge-param-surface.txt"
```
**PASS if:** expanded contract parameters are present.

### VF-06.2: Local Fail-Fast Validation
```bash
{
  echo "=== VF-06.2 FAIL-FAST VALIDATION ==="
  rg -n 'required|missing|required fields|validate|raise|schema_version' \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py
} | tee "$EVIDENCE_DIR/VF-06-2-fail-fast.txt"
```
**PASS if:** bridge validates required fields before backend call.

### VF-06.3: Source-Aware Compatibility for Legacy Flow
```bash
{
  echo "=== VF-06.3 SOURCE-AWARE COMPATIBILITY ==="
  rg -n 'langsmith_|email_sync|compat|backward|legacy|source_type' \
    /home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py \
    /home/zaks/zakops-backend/src/api/orchestration/main.py
} | tee "$EVIDENCE_DIR/VF-06-3-source-aware-compat.txt"
```
**PASS if:** strictness is source-aware and legacy compatibility remains.

**Gate VF-06:** Supports `G1-03`, `G1-05`, `G1-06`, `G1-07`, `G1-11`.

---

## Verification Family 07 — P1-07 Golden Payload End-to-End

### VF-07.1: Golden Payload Fixture Availability
```bash
{
  echo "=== VF-07.1 GOLDEN FIXTURE AVAILABILITY ==="
  find /home/zaks -path '*/tests/fixtures/*' -name '*golden*payload*.json' 2>/dev/null
} | tee "$EVIDENCE_DIR/VF-07-1-golden-fixture.txt"
```
**PASS if:** fixture exists or QA creates one as remediation artifact.

### VF-07.2: Golden Inject Response Check (Live)
```bash
{
  echo "=== VF-07.2 GOLDEN INJECT LIVE ==="
  curl -s -X POST http://localhost:8091/api/quarantine \
    -H 'Content-Type: application/json' \
    -d '{"message_id":"qa-p1-golden-001","source_type":"langsmith_shadow","email_subject":"Golden QA Subject","sender":"qa@example.com","classification":"deal_signal","schema_version":"1.0.0","correlation_id":"qa-p1-corr-001","email_body_snippet":"Golden preview snippet for QA"}' | head -c 1200
} | tee "$EVIDENCE_DIR/VF-07-2-golden-inject-live.txt"
```
**PASS if:** create/dedup response contains valid record ID and no validation failure. If backend DOWN mark `SKIP(services-down)`.

### VF-07.3: Golden Record Readback (Live)
```bash
{
  echo "=== VF-07.3 GOLDEN READBACK ==="
  curl -sf "http://localhost:8091/api/quarantine?limit=5" | head -c 1600
} | tee "$EVIDENCE_DIR/VF-07-3-golden-readback.txt"
```
**PASS if:** readback includes expected fields (`email_subject`, `email_body_snippet`, source tags, IDs). If backend DOWN mark `SKIP(services-down)`.

### VF-07.4: Dashboard Compile/Tests for Phase 1 Touchpoints
```bash
{
  echo "=== VF-07.4 DASHBOARD VALIDATION ==="
  cd /home/zaks/zakops-agent-api/apps/dashboard && npm run test -- --runInBand
} | tee "$EVIDENCE_DIR/VF-07-4-dashboard-tests.txt"
```
**PASS if:** tests pass or failures are classified and remediated within Phase 1 scope.

**Gate VF-07:** Supports `G1-09`, `G1-10`, `G1-12`.

---

## Cross-Consistency Checks

### XC-1: Phase 1 Gate-to-Task Coverage
```bash
{
  echo "=== XC-1 GATE TO TASK COVERAGE ==="
  rg -n 'P1-01|P1-02|P1-03|P1-04|P1-05|P1-06|P1-07|G1-01|G1-02|G1-03|G1-04|G1-05|G1-06|G1-07|G1-08|G1-09|G1-10|G1-11|G1-12' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md \
    /home/zaks/bookkeeping/docs/QA-ET-VALIDATION-P1-VERIFY-001.md
} | tee "$EVIDENCE_DIR/XC-1-gate-task-coverage.txt"
```
**PASS if:** all P1 tasks and G1 gates are represented in QA prompt.

### XC-2: Bridge Path Canonical Consistency
```bash
{
  echo "=== XC-2 BRIDGE PATH CONSISTENCY ==="
  rg -n '/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py|/home/zaks/scripts/agent_bridge/mcp_server.py' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md \
    /home/zaks/bookkeeping/docs/QA-ET-VALIDATION-P1-VERIFY-001.md
} | tee "$EVIDENCE_DIR/XC-2-bridge-path-consistency.txt"
```
**PASS if:** canonical path is used for implementation references.

### XC-3: Contract Surface Alignment for Phase 1
```bash
{
  echo "=== XC-3 SURFACE ALIGNMENT ==="
  rg -n 'S6|S8|S12|S13|S15|S16|make validate-surface6|make validate-agent-config|make validate-surface12|make validate-surface13|make validate-surface15|make validate-surface16' \
    /home/zaks/bookkeeping/docs/MISSION-ET-VALIDATION-001.md \
    /home/zaks/bookkeeping/docs/QA-ET-VALIDATION-P1-VERIFY-001.md
} | tee "$EVIDENCE_DIR/XC-3-surface-alignment.txt"
```
**PASS if:** Phase-1 relevant surfaces and validators are aligned.

---

## Stress Tests

### ST-1: Unknown schema_version Rejection
```bash
{
  echo "=== ST-1 UNKNOWN SCHEMA VERSION ==="
  curl -s -X POST http://localhost:8091/api/quarantine \
    -H 'Content-Type: application/json' \
    -d '{"message_id":"qa-p1-badver-001","source_type":"langsmith_shadow","email_subject":"badver","sender":"qa@example.com","classification":"deal_signal","schema_version":"9.9.9","correlation_id":"qa-badver","email_body_snippet":"x"}' | head -c 600
} | tee "$EVIDENCE_DIR/ST-1-unknown-schema-version.txt"
```
**PASS if:** request is rejected with explicit schema-version validation error. If backend DOWN mark `SKIP(services-down)`.

### ST-2: Extra-Key Rejection Under Strict Model
```bash
{
  echo "=== ST-2 EXTRA KEY REJECTION ==="
  curl -s -X POST http://localhost:8091/api/quarantine \
    -H 'Content-Type: application/json' \
    -d '{"message_id":"qa-p1-extrakey-001","source_type":"langsmith_shadow","email_subject":"extrakey","sender":"qa@example.com","classification":"deal_signal","schema_version":"1.0.0","correlation_id":"qa-extra","email_body_snippet":"x","unexpected_key":"boom"}' | head -c 800
} | tee "$EVIDENCE_DIR/ST-2-extra-key-rejection.txt"
```
**PASS if:** request fails with unknown/extra key validation error. If backend DOWN mark `SKIP(services-down)`.

### ST-3: Legacy Compatibility Probe
```bash
{
  echo "=== ST-3 LEGACY COMPAT PROBE ==="
  curl -s -X POST http://localhost:8091/api/quarantine \
    -H 'Content-Type: application/json' \
    -d '{"message_id":"qa-p1-legacy-001","source_type":"email_sync","sender":"legacy@example.com","subject":"legacy subject"}' | head -c 800
} | tee "$EVIDENCE_DIR/ST-3-legacy-compat-probe.txt"
```
**PASS if:** legacy flow remains accepted or documented with intentional policy change and migration path. If backend DOWN mark `SKIP(services-down)`.

### ST-4: Dedup Persistence Under Expanded Schema
```bash
{
  echo "=== ST-4 DEDUP PERSISTENCE ==="
  for i in 1 2 3 4 5; do
    curl -s -X POST http://localhost:8091/api/quarantine \
      -H 'Content-Type: application/json' \
      -d '{"message_id":"qa-p1-dedup-001","source_type":"langsmith_shadow","email_subject":"dedup","sender":"qa@example.com","classification":"deal_signal","schema_version":"1.0.0","correlation_id":"qa-dedup","email_body_snippet":"x"}' >/tmp/qa_p1_dedup_$i.json
  done
  cat /tmp/qa_p1_dedup_*.json | head -c 1600
} | tee "$EVIDENCE_DIR/ST-4-dedup-persistence.txt"
```
**PASS if:** responses indicate single create with dedup behavior for duplicates. If backend DOWN mark `SKIP(services-down)`.

---

## Remediation Protocol

For every failing check:

1. Read check evidence file and isolate failure.
2. Classify as one of:
   - `NOT_EXECUTED`
   - `MISSING_FIX`
   - `PARTIAL`
   - `REGRESSION`
   - `SCOPE_GAP`
   - `FALSE_POSITIVE`
3. Apply minimal Phase 1-scoped remediation only.
4. Re-run failing check and parent VF gate.
5. Re-run baseline:
   - `cd /home/zaks/zakops-agent-api && make validate-local`
   - `cd /home/zaks/zakops-agent-api && npx tsc --noEmit`
6. Log remediation in completion report with gate IDs and retest evidence.

---

## Dependency Graph

QA execution order:

1. Pre-Flight (PF-1..PF-6)
2. VF-01 through VF-07
3. XC-1 through XC-3
4. ST-1 through ST-4
5. Remediation loops for any FAIL
6. Final scorecard + stop condition

---

## Enhancement Opportunities

### ENH-1: Commit a canonical Phase-1 golden payload fixture in backend tests.
### ENH-2: Add CI guard to reject unknown schema versions via automated negative test.
### ENH-3: Add compatibility contract test for `email_sync` fallback behavior.
### ENH-4: Add regression test for `COALESCE(email_subject, subject)` display behavior.
### ENH-5: Add dashboard test for preview rendering without filesystem dependencies.
### ENH-6: Add bridge contract checksum validation against schema docs.
### ENH-7: Add dedup concurrency harness for expanded schema payloads.
### ENH-8: Add phase gate JSON report generator for machine-readable QA.

---

## Scorecard Template

```text
QA-ET-VALIDATION-P1-VERIFY-001 — Final Scorecard
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
  VF-01 (P1-01 Migration): __ / 3 checks PASS
  VF-02 (P1-02 Strict Model): __ / 3 checks PASS
  VF-03 (P1-03 Response/Coalesce): __ / 2 checks PASS
  VF-04 (P1-04 POST Mapping): __ / 3 checks PASS
  VF-05 (P1-05 Preview Inline): __ / 3 checks PASS
  VF-06 (P1-06 Bridge Contract): __ / 3 checks PASS
  VF-07 (P1-07 Golden Payload): __ / 4 checks PASS

Cross-Consistency:
  XC-1: [ PASS / FAIL ]
  XC-2: [ PASS / FAIL ]
  XC-3: [ PASS / FAIL ]

Stress Tests:
  ST-1: [ PASS / FAIL / SKIP ]
  ST-2: [ PASS / FAIL / SKIP ]
  ST-3: [ PASS / FAIL / SKIP ]
  ST-4: [ PASS / FAIL / SKIP ]

Totals:
  Checks: __ / 34 PASS
  VF Gates: __ / 7 PASS
  XC Gates: __ / 3 PASS
  ST Gates: __ / 4 PASS

Remediations Applied: __
Deferred with reason: __
Enhancements Logged: 8 (ENH-1..ENH-8)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## Executor Self-Check Prompts

- Did I classify Phase 1 as `VERIFY_ONLY` or `EXECUTE_VERIFY` before VF execution?
- For each PASS, is there a tee evidence file and explicit criterion match?
- Did I verify source-aware compatibility rather than strict-only validation?
- Did I rerun baseline validation after each remediation loop?

---

## Guardrails

1. No feature expansion beyond Phase 1 scope.
2. Remediate with minimal change surface.
3. Every PASS requires tee evidence output.
4. Preserve existing behavior for non-Phase-1 paths unless explicitly broken by Phase 1 work.
5. Use canonical bridge path: `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py`.
6. Generated files are read-only; use sync commands for regeneration.
7. Services-down checks may be SKIP only with explicit evidence.
8. Never reference or use decommissioned port 8090.

---

## Stop Condition

Stop when all Phase 1 verification families pass, cross-consistency and stress gates are complete, all Phase 1 remediations are re-verified, baseline validation passes, and the scorecard is fully populated with an overall verdict.

Do not proceed into Phase 2-8 QA from this prompt. Hand off to full-mission QA after Phase 1 closure.
