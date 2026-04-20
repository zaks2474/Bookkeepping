# MISSION: QA-S10-14-VERIFY-001
## Independent QA Verification & Remediation - SURFACES-10-14-REGISTER-001
## Date: 2026-02-10
## Classification: QA Verification & Remediation
## Prerequisite: /home/zaks/bookkeeping/docs/MISSION-SURFACES-10-14-REGISTER-001.md execution complete
## Successor: Post-QA backlog missions (frontend governance hardening + deeper performance enforcement) only after FULL PASS

---

## Preamble: Builder Operating Context

The builder already loads project guardrails (`CLAUDE.md`, canonical memory, hooks, deny rules, path-scoped rules). This QA mission does not restate those systems. It independently verifies that `/home/zaks/bookkeeping/docs/MISSION-SURFACES-10-14-REGISTER-001.md` actually achieved its declared 14-surface end state and did not regress existing infrastructure.

---

## 1. Mission Objective

This mission performs independent QA verification and in-scope remediation for `SURFACES-10-14-REGISTER-001`.

Source mission under test:
- `/home/zaks/bookkeeping/docs/MISSION-SURFACES-10-14-REGISTER-001.md`
- Expected structure: 9 phases (Phase 0 through Phase 8), 12 acceptance criteria (AC-1 through AC-12)
- Expected end state: 14 registered surfaces, 14-surface unified validation, 14-surface manifest visibility, and 4-way count reconciliation

Expected execution artifacts from source mission:
- `/home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-BASELINE.md`
- `/home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/SURFACES-10-14-REGISTER-001.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `SURFACES-10-14-REGISTER-001`

QA scope:
- Verify all ACs with evidence
- Cross-check consistency across docs/scripts/manifests
- Stress test stability of new 14-surface enforcement
- Apply minimal remediation if any gate fails

Out of scope:
- New feature development
- Additional surface expansion beyond 14
- Re-architecting source mission design

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-SURFACES-10-14-REGISTER-001.md
  rg -n '^## Phase ' /home/zaks/bookkeeping/docs/MISSION-SURFACES-10-14-REGISTER-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-SURFACES-10-14-REGISTER-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** mission file exists and reports 9 phases + 12 AC entries.

### PF-2: Execution Artifact Presence

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACTS ==="
  ls -l /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-BASELINE.md
  ls -l /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md
  ls -l /home/zaks/bookkeeping/mission-checkpoints/SURFACES-10-14-REGISTER-001.md
  rg -n 'SURFACES-10-14-REGISTER-001' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/PF-2-execution-artifacts.txt
```

**PASS if:** all expected artifacts exist and CHANGES includes mission ID.

**If FAIL:** classify as `NOT_EXECUTED` and stop gate progression until execution completes.

### PF-3: Baseline Validation Health

```bash
{
  echo "=== PF-3 BASELINE VALIDATION HEALTH ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/PF-3-baseline-validation-health.txt
```

**PASS if:** both commands exit 0.

### PF-4: Baseline 14-Surface Claim Presence

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/PF-4-baseline-14-surface-claims.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text() if (repo/'INFRASTRUCTURE_MANIFEST.md').exists() else ''
cs_count=len(re.findall(r'^### Surface \d+:', cs, flags=re.M))
cla_match=re.search(r'Contract Surfaces \((\d+) Total\)', cla)
vs_match=re.search(r'Validates all (\d+) contract surfaces', vs)
man_lines=[]
m_sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', man)
if m_sec:
    man_lines=[ln for ln in m_sec.group(1).splitlines() if ln.startswith('- ')]
man_count=len(man_lines)
print('contract_surfaces_md=', cs_count)
print('claude_md=', int(cla_match.group(1)) if cla_match else 'MISSING')
print('validator_header=', int(vs_match.group(1)) if vs_match else 'MISSING')
print('manifest_entries=', man_count if man else 'MISSING_MANIFEST')
ok=(cs_count==14 and cla_match and int(cla_match.group(1))==14 and vs_match and int(vs_match.group(1))==14)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** contract catalog, CLAUDE.md, and validator header all state 14.

### PF-5: Runtime Context and Service-Dependency Mode

```bash
{
  echo "=== PF-5 RUNTIME CONTEXT ==="
  cd /home/zaks/zakops-agent-api && git rev-parse --abbrev-ref HEAD
  cd /home/zaks/zakops-agent-api && git status --short
  docker ps --format 'table {{.Names}}\t{{.Status}}' | head -n 15
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/PF-5-runtime-context.txt
```

**PASS if:** runtime context is captured; service-dependent gates can be classified as RUN or SKIP with evidence.

---

## 3. Verification Families (VF)

## Verification Family 01 - Prerequisite Chain and Execution Evidence (AC-1)

### VF-01.1: Completion Report Presence and Structure

```bash
{
  echo "=== VF-01.1 COMPLETION REPORT STRUCTURE ==="
  wc -l /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md
  rg -n 'AC-1|AC-12|PASS|FAIL|INFO|Reconciliation' /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-01.1-completion-structure.txt
```

**PASS if:** completion report exists and references mission ACs/evidence.

### VF-01.2: Baseline Evidence Integrity

```bash
{
  echo "=== VF-01.2 BASELINE EVIDENCE INTEGRITY ==="
  ls -l /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-BASELINE.md
  head -n 60 /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-BASELINE.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-01.2-baseline-integrity.txt
```

**PASS if:** baseline file exists and contains timestamped before-state evidence.

### VF-01.3: Checkpoint File Integrity

```bash
{
  echo "=== VF-01.3 CHECKPOINT INTEGRITY ==="
  ls -l /home/zaks/bookkeeping/mission-checkpoints/SURFACES-10-14-REGISTER-001.md
  tail -n 80 /home/zaks/bookkeeping/mission-checkpoints/SURFACES-10-14-REGISTER-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-01.3-checkpoint-integrity.txt
```

**PASS if:** checkpoint exists and includes completion status or last known actionable state.

### VF-01.4: CHANGES Entry Integrity

```bash
{
  echo "=== VF-01.4 CHANGES ENTRY ==="
  rg -n 'SURFACES-10-14-REGISTER-001' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-01.4-changes-entry.txt
```

**PASS if:** CHANGES contains the mission ID and meaningful summary.

**Gate VF-01:** All 4 checks PASS.

---

## Verification Family 02 - Surface 11 + Surface 10 Validator Readiness (AC-2, AC-3)

### VF-02.1: Surface 11 Script Existence and Executability

```bash
{
  echo "=== VF-02.1 SURFACE11 SCRIPT ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh
  head -n 80 /home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-02.1-surface11-script.txt
```

**PASS if:** script exists, is executable, and references Surface 11 contract artifact(s).

### VF-02.2: Surface 10 Script Existence and Executability

```bash
{
  echo "=== VF-02.2 SURFACE10 SCRIPT ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh
  head -n 80 /home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-02.2-surface10-script.txt
```

**PASS if:** script exists, is executable, and references dependency topology checks.

### VF-02.3: Make Targets for Surfaces 10 and 11

```bash
{
  echo "=== VF-02.3 MAKE TARGETS S10/S11 ==="
  rg -n '^validate-surface10:|^validate-surface11:' /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-02.3-make-targets-s10s11.txt
```

**PASS if:** both targets are present and mapped to corresponding scripts.

### VF-02.4: Runtime Validation for Surface 11

```bash
{
  echo "=== VF-02.4 RUN SURFACE11 ==="
  cd /home/zaks/zakops-agent-api && make validate-surface11
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-02.4-run-surface11.txt
```

**PASS if:** command exits 0 and output indicates deterministic checks.

### VF-02.5: Runtime Validation for Surface 10

```bash
{
  echo "=== VF-02.5 RUN SURFACE10 ==="
  cd /home/zaks/zakops-agent-api && make validate-surface10
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-02.5-run-surface10.txt
```

**PASS if:** command exits 0 and output indicates deterministic checks.

**Gate VF-02:** All 5 checks PASS.

---

## Verification Family 03 - Surface 12 + Surface 13 Validator Readiness (AC-4, AC-5)

### VF-03.1: Surface 12 Script Existence and Executability

```bash
{
  echo "=== VF-03.1 SURFACE12 SCRIPT ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh
  head -n 80 /home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-03.1-surface12-script.txt
```

**PASS if:** script exists and checks error-taxonomy contract anchors.

### VF-03.2: Surface 13 Script Existence and Executability

```bash
{
  echo "=== VF-03.2 SURFACE13 SCRIPT ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh
  head -n 80 /home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-03.2-surface13-script.txt
```

**PASS if:** script exists and checks declared test-path presence contract.

### VF-03.3: Make Targets for Surfaces 12 and 13

```bash
{
  echo "=== VF-03.3 MAKE TARGETS S12/S13 ==="
  rg -n '^validate-surface12:|^validate-surface13:' /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-03.3-make-targets-s12s13.txt
```

**PASS if:** both targets exist.

### VF-03.4: Runtime Validation for Surface 12

```bash
{
  echo "=== VF-03.4 RUN SURFACE12 ==="
  cd /home/zaks/zakops-agent-api && make validate-surface12
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-03.4-run-surface12.txt
```

**PASS if:** command exits 0.

### VF-03.5: Runtime Validation for Surface 13

```bash
{
  echo "=== VF-03.5 RUN SURFACE13 ==="
  cd /home/zaks/zakops-agent-api && make validate-surface13
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-03.5-run-surface13.txt
```

**PASS if:** command exits 0.

**Gate VF-03:** All 5 checks PASS.

---

## Verification Family 04 - Surface 14 Contract and Validator Behavior (AC-6, AC-7)

### VF-04.1: Performance Budget Source Artifact Exists

```bash
{
  echo "=== VF-04.1 PERFORMANCE BUDGET ARTIFACT ==="
  ls -l /home/zaks/bookkeeping/docs/PERFORMANCE-BUDGET.md
  sed -n '1,220p' /home/zaks/bookkeeping/docs/PERFORMANCE-BUDGET.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-04.1-performance-budget-artifact.txt
```

**PASS if:** source artifact exists with explicit measurable thresholds.

### VF-04.2: Performance Budget Document Contains Required Dimensions

```bash
{
  echo "=== VF-04.2 PERFORMANCE BUDGET DIMENSIONS ==="
  rg -n 'p95|p99|latency|bundle|payload|threshold|budget|strict|advisory' /home/zaks/bookkeeping/docs/PERFORMANCE-BUDGET.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-04.2-performance-budget-dimensions.txt
```

**PASS if:** document contains concrete budget dimensions and threshold language.

### VF-04.3: Surface 14 Script and Target Existence

```bash
{
  echo "=== VF-04.3 SURFACE14 SCRIPT + TARGET ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh
  rg -n '^validate-surface14:' /home/zaks/zakops-agent-api/Makefile
  head -n 120 /home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-04.3-surface14-script-target.txt
```

**PASS if:** script exists, target exists, and script includes advisory/strict semantics.

### VF-04.4: Advisory-Mode Runtime Validation for Surface 14

```bash
{
  echo "=== VF-04.4 RUN SURFACE14 ADVISORY ==="
  cd /home/zaks/zakops-agent-api && make validate-surface14
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-04.4-run-surface14-advisory.txt
```

**PASS if:** default/advisory mode executes successfully.

### VF-04.5: Strict-Mode Capability Presence Check

```bash
{
  echo "=== VF-04.5 SURFACE14 STRICT CAPABILITY ==="
  rg -n 'strict|STRICT|--strict|ADVISORY|advisory' /home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-04.5-surface14-strict-capability.txt
```

**PASS if:** strict-mode support is discoverable and documented in script behavior.

**Gate VF-04:** All 5 checks PASS.

---

## Verification Family 05 - Unified 14-Surface Wiring and Runtime Enforcement (AC-8)

### VF-05.1: Contract Catalog Contains Surfaces 1 through 14

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-05.1-contract-catalog-1to14.txt
import re
from pathlib import Path
txt=Path('/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md').read_text()
ids=sorted({int(m.group(1)) for m in re.finditer(r'^### Surface (\d+):', txt, flags=re.M)})
print('surface_ids=', ids)
ok=(ids==list(range(1,15)))
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** catalog contains exactly Surfaces 1..14.

### VF-05.2: Unified Validator Header and Script Wiring

```bash
{
  echo "=== VF-05.2 UNIFIED VALIDATOR HEADER/WIRING ==="
  rg -n 'Validates all 14 contract surfaces|Surface 10|Surface 11|Surface 12|Surface 13|Surface 14' /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-05.2-unified-validator-header-wiring.txt
```

**PASS if:** unified script claims 14 and includes explicit checks/invocations for 10-14.

### VF-05.3: Make Target Description and Command Graph Coherence

```bash
{
  echo "=== VF-05.3 MAKE TARGET COHERENCE ==="
  rg -n '^validate-contract-surfaces:|^validate-full:|^validate-local:' /home/zaks/zakops-agent-api/Makefile
  cd /home/zaks/zakops-agent-api && make -n validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make -n validate-local
  cd /home/zaks/zakops-agent-api && make -n validate-full
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-05.3-make-target-coherence.txt
```

**PASS if:** make targets are coherent with 14-surface unified validation design.

### VF-05.4: Runtime 14-Surface Unified Validation

```bash
{
  echo "=== VF-05.4 RUN UNIFIED VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-05.4-run-unified-validation.txt
```

**PASS if:** command exits 0 and output confirms 14/14 checks.

### VF-05.5: Stop Hook Compatibility with 14-Surface State

```bash
{
  echo "=== VF-05.5 STOP HOOK COMPATIBILITY ==="
  rg -n 'validate-contract-surfaces|14|9 surfaces|Gate B' /home/zaks/.claude/hooks/stop.sh
  cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-05.5-stop-hook-compatibility.txt
```

**PASS if:** stop hook completes without timeout and remains aligned with 14-surface runtime.

**Gate VF-05:** All 5 checks PASS.

---

## Verification Family 06 - Manifest Truth and Count Reconciliation at 14 (AC-9, AC-10)

### VF-06.1: Regenerate Manifest from Current State

```bash
{
  echo "=== VF-06.1 MANIFEST REGEN ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-06.1-manifest-regen.txt
```

**PASS if:** snapshot command exits 0.

### VF-06.2: Manifest Contract Surface Section Contains 14 Entries

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-06.2-manifest-section-14.txt
import re
from pathlib import Path
m=Path('/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md').read_text()
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', m)
if not sec:
    print('FAIL: contract surfaces section missing')
    raise SystemExit(1)
lines=[ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]
print('surface_entries=', len(lines))
for ln in lines:
    print(ln)
ok=(len(lines)==14)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** exactly 14 entries are present.

### VF-06.3: Manifest Includes Surface 10-14 Labels

```bash
{
  echo "=== VF-06.3 MANIFEST LABELS S10-S14 ==="
  rg -n 'S10|Surface 10|S11|Surface 11|S12|Surface 12|S13|Surface 13|S14|Surface 14' /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-06.3-manifest-labels-s10s14.txt
```

**PASS if:** manifest explicitly includes 10-14 entries.

### VF-06.4: 4-Way Count Reconciliation = 14

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-06.4-four-way-reconciliation.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text()
cs_count=len(re.findall(r'^### Surface \d+:', cs, flags=re.M))
cla_count=int(re.search(r'Contract Surfaces \((\d+) Total\)', cla).group(1))
vs_count=int(re.search(r'Validates all (\d+) contract surfaces', vs).group(1))
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', man)
man_count=len([ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]) if sec else -1
print('contract-surfaces.md=', cs_count)
print('CLAUDE.md=', cla_count)
print('validator_header=', vs_count)
print('manifest_section=', man_count)
ok=(cs_count==cla_count==vs_count==man_count==14)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** all four authoritative counts equal 14.

### VF-06.5: CLAUDE.md Contract Table Includes Surfaces 10-14

```bash
{
  echo "=== VF-06.5 CLAUDE TABLE S10-S14 ==="
  rg -n 'Contract Surfaces \(14 Total\)|\| 10 \||\| 11 \||\| 12 \||\| 13 \||\| 14 \|' /home/zaks/zakops-agent-api/CLAUDE.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-06.5-claude-table-s10s14.txt
```

**PASS if:** CLAUDE header and table include Surfaces 10-14.

**Gate VF-06:** All 5 checks PASS.

---

## Verification Family 07 - No Regression and Bookkeeping Closure (AC-11, AC-12)

### VF-07.1: No-Regression Validation

```bash
{
  echo "=== VF-07.1 NO REGRESSION VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-07.1-no-regression-validation.txt
```

**PASS if:** both commands exit 0.

### VF-07.2: Optional Full Validation Confirmation

```bash
{
  echo "=== VF-07.2 FULL VALIDATION CONFIRMATION ==="
  cd /home/zaks/zakops-agent-api && make validate-full
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-07.2-full-validation-confirmation.txt
```

**PASS if:** full validation exits 0, or service-dependent skips are explicitly justified.

### VF-07.3: Completion Report AC Mapping Coverage

```bash
{
  echo "=== VF-07.3 COMPLETION AC COVERAGE ==="
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10|AC-11|AC-12' /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-07.3-completion-ac-coverage.txt
```

**PASS if:** all 12 ACs are explicitly accounted for.

### VF-07.4: Evidence Completeness Audit

```bash
{
  echo "=== VF-07.4 EVIDENCE COMPLETENESS ==="
  find /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence -maxdepth 1 -type f | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/VF-07.4-evidence-completeness.txt
```

**PASS if:** PF/VF/XC/ST evidence files exist for all executed checks.

**Gate VF-07:** All 4 checks PASS.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Catalog Entries vs Validator Scripts for Surfaces 10-14

```bash
{
  echo "=== XC-1 CATALOG VS VALIDATORS ==="
  rg -n '^### Surface 10:|^### Surface 11:|^### Surface 12:|^### Surface 13:|^### Surface 14:' /home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/XC-1-catalog-vs-validators.txt
```

**PASS if:** every registered new surface has a corresponding validator script.

### XC-2: Make Targets vs Validator Script Files

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/XC-2-make-targets-vs-files.txt
from pathlib import Path
import re
mk=Path('/home/zaks/zakops-agent-api/Makefile').read_text()
base=Path('/home/zaks/zakops-agent-api/tools/infra')
ok=True
for n in range(10,15):
    tgt=bool(re.search(rf'^validate-surface{n}:', mk, flags=re.M))
    scr=(base/f'validate-surface{n}.sh').exists()
    print(f'surface{n}: target={tgt} script={scr}')
    if not (tgt and scr): ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** target/script alignment is complete for 10..14.

### XC-3: Manifest Entries vs Real Contract Artifacts

```bash
{
  echo "=== XC-3 MANIFEST VS ARTIFACTS ==="
  ls -l /home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md
  ls -l /home/zaks/bookkeeping/docs/ENV-CROSSREF.md
  ls -l /home/zaks/bookkeeping/docs/ERROR-SHAPES.md
  ls -l /home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md
  ls -l /home/zaks/bookkeeping/docs/PERFORMANCE-BUDGET.md
  rg -n 'S10|S11|S12|S13|S14|Surface 10|Surface 11|Surface 12|Surface 13|Surface 14' /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/XC-3-manifest-vs-artifacts.txt
```

**PASS if:** manifest entries correspond to actual source artifacts.

### XC-4: CLAUDE Contract Surface Table vs Contract Catalog

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/XC-4-claude-vs-catalog.txt
import re
from pathlib import Path
cla=Path('/home/zaks/zakops-agent-api/CLAUDE.md').read_text()
cat=Path('/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md').read_text()
cla_ids=sorted({int(m.group(1)) for m in re.finditer(r'^\|\s*(\d+)\s*\|', cla, flags=re.M)})
cat_ids=sorted({int(m.group(1)) for m in re.finditer(r'^### Surface (\d+):', cat, flags=re.M)})
print('claude_ids=', cla_ids)
print('catalog_ids=', cat_ids)
ok=(cla_ids==cat_ids==list(range(1,15)))
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** both sources enumerate exactly 1..14.

### XC-5: Unified Validator Output vs Manifest Count

```bash
{
  echo "=== XC-5 VALIDATOR VS MANIFEST COUNT ==="
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  python3 - <<'PY'
import re
from pathlib import Path
m=Path('/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md').read_text()
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', m)
cnt=len([ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]) if sec else -1
print('manifest_surface_count=',cnt)
raise SystemExit(0 if cnt==14 else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/XC-5-validator-vs-manifest.txt
```

**PASS if:** manifest surface count remains 14 after fresh unified validation.

### XC-6: Completion Reconciliation Table Integrity

```bash
{
  echo "=== XC-6 COMPLETION RECONCILIATION TABLE ==="
  rg -n 'Surface Count Before|Surface Count After|contract-surfaces.md|validate-contract-surfaces.sh|INFRASTRUCTURE_MANIFEST|CLAUDE.md|14' /home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/XC-6-completion-reconciliation-table.txt
```

**PASS if:** completion report contains explicit before/after reconciliation table and 14-state evidence.

---

## 5. Stress Tests (ST)

### ST-1: Unified Validator Determinism (3 Consecutive Runs)

```bash
{
  echo "=== ST-1 UNIFIED VALIDATOR DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make validate-contract-surfaces
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/ST-1-unified-validator-determinism.txt
```

**PASS if:** all three runs pass with stable 14-surface behavior.

### ST-2: Snapshot Determinism (3 Consecutive Runs)

```bash
{
  echo "=== ST-2 SNAPSHOT DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  cd /home/zaks/zakops-agent-api && make infra-snapshot
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/ST-2-snapshot-determinism.txt
```

**PASS if:** all three runs succeed and preserve 14-surface section integrity.

### ST-3: Stop Hook Runtime Budget Under 14-Surface State

```bash
{
  echo "=== ST-3 STOP HOOK RUNTIME BUDGET ==="
  cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh
  echo "stop_hook_exit=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/ST-3-stop-hook-runtime-budget.txt
```

**PASS if:** no timeout and no false block under healthy state.

### ST-4: Fail-Fast Snapshot Injection Still Works

```bash
{
  echo "=== ST-4 SNAPSHOT FAIL-FAST INJECTION ==="
  cd /home/zaks/zakops-agent-api
  set +e
  make infra-snapshot INFRA_TOOLS=/does/not/exist
  ec=$?
  set -e
  echo "injected_exit_code=$ec"
  test "$ec" -ne 0
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/ST-4-snapshot-failfast-injection.txt
```

**PASS if:** injected failure yields non-zero exit code.

### ST-5: 4-Way Count Stability After Stress Runs

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/ST-5-count-stability.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
man=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text()
counts={
 'contract_surfaces_md': len(re.findall(r'^### Surface \d+:', cs, flags=re.M)),
 'claude_md': int(re.search(r'Contract Surfaces \((\d+) Total\)', cla).group(1)),
 'validator_header': int(re.search(r'Validates all (\d+) contract surfaces', vs).group(1)),
}
sec=re.search(r'## Contract Surfaces .*?\n((?:- .*\n)+)', man)
counts['manifest_section']=len([ln for ln in sec.group(1).splitlines() if ln.startswith('- ')]) if sec else -1
for k,v in counts.items():
    print(k,'=',v)
ok=all(v==14 for v in counts.values())
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** all count sources remain 14 after repeated runs.

### ST-6: New Validator Script Ownership and Line Ending Hygiene

```bash
{
  echo "=== ST-6 SCRIPT OWNERSHIP + LINE ENDINGS ==="
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh
  ls -l /home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh
  file /home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/ST-6-script-hygiene.txt
```

**PASS if:** ownership is sane and scripts are not CRLF-corrupted.

### ST-7: Forbidden File Regression Guard

```bash
{
  echo "=== ST-7 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
  cd /home/zaks/zakops-agent-api && git diff --name-only | rg 'generated\.ts$|_models\.py$|/migrations/' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/evidence/ST-7-forbidden-file-regression-guard.txt
```

**PASS if:** no unintended forbidden-file regressions are introduced by QA remediations.

---

## 6. Remediation Protocol

When a gate fails:

1. Capture failing evidence file path and exact failing command.
2. Classify failure:
- `MISSING_FIX`
- `REGRESSION`
- `SCOPE_GAP`
- `FALSE_POSITIVE`
- `NOT_IMPLEMENTED`
- `PARTIAL`
- `VIOLATION`
- `COUNT_MISMATCH`
- `WIRING_GAP`

3. Apply minimal in-scope remediation aligned to `SURFACES-10-14-REGISTER-001` constraints.
4. Re-run failed check first.
5. Re-run no-regression baseline:
- `cd /home/zaks/zakops-agent-api && make validate-local`
- `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`

6. Re-run `make infra-snapshot` if any manifest/count-related remediation occurred.
7. Record remediation details in scorecard and completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Add machine-readable schema for `PERFORMANCE-BUDGET.md` and schema-lint gate.
### ENH-2: Add unit-test harness for `validate-surface10.sh` through `validate-surface14.sh` with fixture inputs.
### ENH-3: Add single `make validate-surfaces-new` meta-target for surfaces 10-14.
### ENH-4: Add manifest contract section schema validation (entry count + required fields).
### ENH-5: Add CI check that enforces 4-way count equality at PR time.
### ENH-6: Add regression guard for accidental removal of Surface 10-14 entries from `CLAUDE.md`.
### ENH-7: Add stricter strict-mode contract for Surface 14 in CI (advisory local, strict CI).
### ENH-8: Add automated reconciliation-table generation in completion reports.
### ENH-9: Add pre-commit scan for stale surface-count strings in scripts/docs.
### ENH-10: Add QA helper command that scaffolds PF/VF/XC/ST evidence files for new QA missions.

---

## 8. Scorecard Template

```
QA-S10-14-VERIFY-001 - Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL / NOT_EXECUTED ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (Prerequisite + Evidence Integrity): __ / 4 checks PASS
  VF-02 (Surface 11 + 10 Validators): __ / 5 checks PASS
  VF-03 (Surface 12 + 13 Validators): __ / 5 checks PASS
  VF-04 (Surface 14 Contract + Validator): __ / 5 checks PASS
  VF-05 (Unified 14-Surface Wiring): __ / 5 checks PASS
  VF-06 (Manifest + Reconciliation at 14): __ / 5 checks PASS
  VF-07 (No Regression + Bookkeeping): __ / 4 checks PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 checks PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 tests PASS

Total: __ / 51 checks PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not build new surfaces beyond 14 in this QA mission.
2. Do not introduce application feature work.
3. Remediate only what is required to satisfy source mission ACs.
4. Preserve generated-file immutability and migration safety boundaries.
5. Every PASS must be backed by captured evidence (`tee` output).
6. If services are unavailable, classify dependent checks as `SKIP` with evidence.
7. Preserve established Surfaces 1-9 behavior while verifying 10-14 additions.
8. Do not rewrite bookkeeping source docs except minimal remediation required by failed gates.
9. Keep all file paths absolute in commands and reports.
10. If classification is ambiguous, mark `INFO` and escalate instead of forcing PASS.

---

## 10. Stop Condition

Stop when all 51 QA checks pass (or are explicitly and correctly classified as `SKIP/INFO/FALSE_POSITIVE`), remediations are re-verified, baseline validation remains healthy, and the scorecard is complete with evidence paths.

Do not declare `FULL PASS` unless Surfaces 10-14 are validated end-to-end and all four authoritative count sources report `14`.

---

*End of Mission Prompt - QA-S10-14-VERIFY-001*
