# MISSION: QA-ITR-VERIFY-001
## Independent QA Verification & Remediation — INFRA-TRUTH-REPAIR-001
## Date: 2026-02-10
## Classification: QA Verification & Remediation
## Prerequisite: MISSION-INFRA-TRUTH-REPAIR-001 execution complete
## Successor: MISSION-SURFACES-10-14-REGISTER-001 (unblock only on FULL PASS)

---

## Preamble: Builder Operating Context

The builder already loads project guardrails (CLAUDE.md, memory, hooks, deny rules, path-scoped rules). This QA mission does not restate those systems; it verifies the outputs and behavioral guarantees of `/home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001.md`.

---

## 1. Mission Objective

This mission independently verifies that `INFRA-TRUTH-REPAIR-001` truly repaired runtime integrity for Track 1 + Track 2 + manifest hardening, without regressions.

Source mission under test:
- `/home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001.md`
- Expected structure: 6 phases, 10 acceptance criteria, explicit Surfaces 10–14 deferment.

Expected execution artifacts from source mission:
- `/home/zaks/bookkeeping/docs/INFRA-TRUTH-REPAIR-001-BASELINE.md`
- `/home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/INFRA-TRUTH-REPAIR-001.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `INFRA-TRUTH-REPAIR-001`

This QA mission verifies, cross-checks, stress-tests, and remediates only what is needed to satisfy the source mission’s acceptance criteria.

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001.md
  rg -n '^## Phase ' /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/PF-1-source-mission.txt
```

**PASS if:** mission file exists and reports 6 phases + 10 AC entries.

### PF-2: Execution Status Check

```bash
{
  echo "=== PF-2 EXECUTION STATUS ==="
  ls -l /home/zaks/bookkeeping/docs/INFRA-TRUTH-REPAIR-001-BASELINE.md
  ls -l /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md
  ls -l /home/zaks/bookkeeping/mission-checkpoints/INFRA-TRUTH-REPAIR-001.md
  rg -n 'INFRA-TRUTH-REPAIR-001' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/PF-2-execution-status.txt
```

**PASS if:** all expected artifacts exist and CHANGES contains source mission ID.

**If FAIL:** classify as `NOT_EXECUTED` and stop QA gate progression.

### PF-3: Baseline Validation

```bash
{
  echo "=== PF-3 BASELINE VALIDATION ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-full
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/PF-3-baseline-validation.txt
```

**PASS if:** both commands exit 0.

### PF-4: Baseline Snapshot Behavior

```bash
{
  echo "=== PF-4 BASELINE SNAPSHOT ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/PF-4-baseline-snapshot.txt
```

**PASS if:** command exits 0 and no generator failure text appears.

### PF-5: Runtime Guardrail Context

```bash
{
  echo "=== PF-5 RUNTIME CONTEXT ==="
  ls -1 /home/zaks/.claude/hooks
  python3 - <<'PY'
import json
u=json.load(open('/home/zaks/.claude/settings.json'))
print('user_playwright_disabled=',u.get('mcpServers',{}).get('playwright',{}).get('disabled'))
PY
  sudo -n python3 - <<'PY'
import json
r=json.load(open('/root/.claude/settings.json'))
print('root_dangerouslySkipPermissions=',r.get('dangerouslySkipPermissions'))
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/PF-5-runtime-context.txt
```

**PASS if:** hook set is intact and root permission bypass state is readable/documented.

---

## 3. Verification Families (VF)

## Verification Family 01 — Track 1 Agent/Skill Integrity (AC-1, AC-2, AC-3)

### VF-01.1: Agent Ownership and Presence

```bash
{
  echo "=== VF-01.1 AGENT OWNERSHIP ==="
  ls -la /home/zaks/.claude/agents
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-01.1-agent-ownership.txt
```

**PASS if:** all active agent files are present and ownership is consistent with mission output requirements.

### VF-01.2: No Broken `~/.claude/skills` Preload Paths in Active Agent Files

```bash
{
  echo "=== VF-01.2 AGENT PRELOAD PATHS ==="
  rg -n '~/.claude/skills' /home/zaks/.claude/agents/*.md || true
  rg -n '/home/zaks/.claude/skills' /home/zaks/.claude/agents/*.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-01.2-agent-preload-paths.txt
```

**PASS if:** zero `~/.claude/skills` hits and required absolute preload paths exist.

### VF-01.3: Preload Path Resolution Check

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-01.3-preload-path-resolution.txt
from pathlib import Path
import re
files=[
'/home/zaks/.claude/agents/arch-reviewer.md',
'/home/zaks/.claude/agents/contract-guardian.md',
'/home/zaks/.claude/agents/test-engineer.md',
]
ok=True
for f in files:
    txt=Path(f).read_text()
    paths=re.findall(r'-\s+(/home/zaks/.claude/skills/[^\s`]+)',txt)
    print(f'FILE: {f}')
    if not paths:
        print('  FAIL: no absolute skill paths found')
        ok=False
    for p in paths:
        exists=Path(p).exists() or Path(p+'/SKILL.md').exists()
        print(f'  {p} -> {"PASS" if exists else "FAIL"}')
        if not exists: ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** every referenced preload path resolves.

### VF-01.4: Frontend-Design Skill Activation and Content Identity

```bash
{
  echo "=== VF-01.4 FRONTEND SKILL ACTIVATION ==="
  ls -l /home/zaks/.claude/skills/frontend-design/SKILL.md
  sha256sum /home/zaks/.claude/skills/frontend-design/SKILL.md
  sha256sum /home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-01.4-frontend-skill.txt
```

**PASS if:** local skill exists and checksum matches marketplace source (or documented intentional divergence).

### VF-01.5: Skills Inventory Presence in Canonical Memory

```bash
{
  echo "=== VF-01.5 MEMORY SKILL INVENTORY ==="
  sudo -n grep -nEi 'skills|frontend-design|api-conventions|verification-standards' /root/.claude/projects/-home-zaks/memory/MEMORY.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-01.5-memory-skill-inventory.txt
```

**PASS if:** memory includes a usable skills inventory including `frontend-design`.

**Gate VF-01:** All 5 checks PASS.

---

## Verification Family 02 — 9-Surface Validation Wiring Integrity (AC-4, AC-5)

### VF-02.1: Surface Source-of-Truth Counts

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-02.1-surface-counts.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
mk=(repo/'Makefile').read_text()
cs_count=len(re.findall(r'^### Surface \d+:',cs,flags=re.M))
cla_count=int(re.search(r'Contract Surfaces \((\d+) Total\)',cla).group(1))
vs_hdr=re.search(r'Validates all (\d+) contract surfaces',vs)
mk_hdr=re.search(r'validate-contract-surfaces: ## Validate all (\d+) contract surfaces',mk)
print('contract-surfaces.md=',cs_count)
print('CLAUDE.md=',cla_count)
print('validator_header=',int(vs_hdr.group(1)) if vs_hdr else 'MISSING')
print('makefile_header=',int(mk_hdr.group(1)) if mk_hdr else 'MISSING')
ok=(cs_count==9 and cla_count==9 and vs_hdr and int(vs_hdr.group(1))==9 and mk_hdr and int(mk_hdr.group(1))==9)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** all declared counts are 9.

### VF-02.2: Contract Surface Validator Runtime Output

```bash
{
  echo "=== VF-02.2 VALIDATE CONTRACT SURFACES ==="
  cd /home/zaks/zakops-agent-api && bash /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-02.2-validate-contract-surfaces.txt
```

**PASS if:** script exits 0 and output proves all 9 surface checks are enforced.

### VF-02.3: Surface 9 Validator in Unified Validation Path

```bash
{
  echo "=== VF-02.3 SURFACE9 WIRING ==="
  cd /home/zaks/zakops-agent-api && make -n validate-local
  cd /home/zaks/zakops-agent-api && make -n validate-full
  rg -n 'Surface 9|validate-surface9' /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh /home/zaks/zakops-agent-api/Makefile
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-02.3-surface9-wiring.txt
```

**PASS if:** Surface 9 is not orphaned from unified validation.

### VF-02.4: validate-local + validate-full Pass After Wiring

```bash
{
  echo "=== VF-02.4 FINAL VALIDATION GATES ==="
  cd /home/zaks/zakops-agent-api && make validate-local
  cd /home/zaks/zakops-agent-api && make validate-full
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-02.4-validate-gates.txt
```

**PASS if:** both gates exit 0.

### VF-02.5: No Active “all 7 surfaces” Stale Wording in Enforcement Files

```bash
{
  echo "=== VF-02.5 STALE WORDING SWEEP ==="
  rg -n 'all 7 contract surfaces|Validates all 7 contract surfaces' \
    /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh \
    /home/zaks/zakops-agent-api/Makefile \
    /home/zaks/zakops-agent-api/.claude/commands/before-task.md \
    /home/zaks/.claude/hooks/stop.sh || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-02.5-stale-wording.txt
```

**PASS if:** zero stale wording in active enforcement paths.

### VF-02.6: Before-Task Guidance Consistency

```bash
{
  echo "=== VF-02.6 BEFORE-TASK CONSISTENCY ==="
  nl -ba /home/zaks/zakops-agent-api/.claude/commands/before-task.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-02.6-before-task.txt
```

**PASS if:** command guidance aligns with repaired 9-surface enforcement path.

**Gate VF-02:** All 6 checks PASS.

---

## Verification Family 03 — Stop Hook and Runtime Enforcement Consistency (AC-5, AC-9)

### VF-03.1: Stop Hook Contract Validation Wiring

```bash
{
  echo "=== VF-03.1 STOP HOOK WIRING ==="
  nl -ba /home/zaks/.claude/hooks/stop.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-03.1-stop-hook-wiring.txt
```

**PASS if:** stop hook invokes the correct contract-surface enforcement path and remains coherent with mission intent.

### VF-03.2: Stop Hook Runtime Gate

```bash
{
  echo "=== VF-03.2 STOP HOOK RUNTIME ==="
  cd /home/zaks/zakops-agent-api && timeout 30 bash /home/zaks/.claude/hooks/stop.sh
  echo "stop_hook_exit=$?"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-03.2-stop-hook-runtime.txt
```

**PASS if:** no timeout and no false failure from repaired validation path.

### VF-03.3: Hook Set Integrity

```bash
{
  echo "=== VF-03.3 HOOK SET INTEGRITY ==="
  ls -1 /home/zaks/.claude/hooks
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-03.3-hook-set.txt
```

**PASS if:** required hooks are present and unchanged in role.

### VF-03.4: No Regression in SessionStart Boot Diagnostics Script Availability

```bash
{
  echo "=== VF-03.4 SESSION-START AVAILABILITY ==="
  test -x /home/zaks/.claude/hooks/session-start.sh && echo PASS_session_start_executable
  test -x /home/zaks/.claude/hooks/session-boot.sh && echo PASS_session_boot_executable
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-03.4-session-hooks.txt
```

**PASS if:** both scripts are present and executable.

**Gate VF-03:** All 4 checks PASS.

---

## Verification Family 04 — `infra-snapshot` Fail-Fast and Manifest Truth (AC-6, AC-7)

### VF-04.1: Failure Injection Must Produce Non-Zero Exit

```bash
{
  echo "=== VF-04.1 FAILURE INJECTION ==="
  cd /home/zaks/zakops-agent-api
  set +e
  make infra-snapshot INFRA_TOOLS=/does/not/exist
  ec=$?
  set -e
  echo "injected_exit_code=$ec"
  test "$ec" -ne 0
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-04.1-fail-fast.txt
```

**PASS if:** injected failure returns non-zero.

### VF-04.2: Normal Snapshot Run Must Succeed

```bash
{
  echo "=== VF-04.2 NORMAL SNAPSHOT ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-04.2-snapshot-success.txt
```

**PASS if:** run exits 0 and no generator-failure text is emitted.

### VF-04.3: Manifest Contract Surface Section Count = 9

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-04.3-manifest-surface-count.txt
import re
from pathlib import Path
m=Path('/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md').read_text()
sec=re.search(r'## Contract Surfaces \(Hybrid Guardrail\)\n((?:- .*\n)+)',m)
if not sec:
    print('FAIL: section missing')
    raise SystemExit(1)
lines=[ln for ln in sec.group(1).splitlines() if ln.strip().startswith('- ')]
print('surface_entries=',len(lines))
print('\n'.join(lines))
ok=(len(lines)==9)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** exactly 9 surface entries are present.

### VF-04.4: No False `NOT FOUND` in Contract Surface Section

```bash
{
  echo "=== VF-04.4 CONTRACT SECTION NOT FOUND CHECK ==="
  python3 - <<'PY'
import re
from pathlib import Path
m=Path('/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md').read_text()
sec=re.search(r'## Contract Surfaces \(Hybrid Guardrail\)\n((?:- .*\n)+)',m)
if not sec:
    print('FAIL: section missing')
    raise SystemExit(1)
not_found=[ln for ln in sec.group(1).splitlines() if 'NOT FOUND' in ln]
print('not_found_lines=',len(not_found))
for ln in not_found:
    print(ln)
raise SystemExit(0 if len(not_found)==0 else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-04.4-no-false-notfound.txt
```

**PASS if:** zero `NOT FOUND` lines in contract section.

### VF-04.5: Generated Type Section Truth Check

```bash
{
  echo "=== VF-04.5 GENERATED TYPE SECTION ==="
  rg -n '^## Generated Type Files|NOT FOUND|present' /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-04.5-generated-types-section.txt
```

**PASS if:** section reflects real generated file state and does not claim missing files that exist.

### VF-04.6: Manifest Command/Rule Counts Match Live Filesystem

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-04.6-manifest-counts-truth.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
m=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text()
cmd_live=len(list((repo/'.claude/commands').glob('*.md')))
rule_live=len(list((repo/'.claude/rules').glob('*.md')))
cmd_doc=re.search(r'- Commands:\s*(\d+)',m)
rule_doc=re.search(r'- Rules:\s*(\d+)',m)
if not cmd_doc or not rule_doc:
    print('FAIL: missing command/rule count lines in manifest')
    raise SystemExit(1)
cmd_doc=int(cmd_doc.group(1)); rule_doc=int(rule_doc.group(1))
print('commands_live=',cmd_live,'commands_doc=',cmd_doc)
print('rules_live=',rule_live,'rules_doc=',rule_doc)
ok=(cmd_live==cmd_doc and rule_live==rule_doc)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** manifest command/rule counts equal live filesystem counts.

### VF-04.7: Snapshot Timestamp Freshness

```bash
{
  echo "=== VF-04.7 MANIFEST TIMESTAMP FRESHNESS ==="
  head -n 8 /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-04.7-manifest-timestamp.txt
```

**PASS if:** generated timestamp is fresh for this QA run.

**Gate VF-04:** All 7 checks PASS.

---

## Verification Family 05 — Count Reconciliation + Boot Diagnostics Extension (AC-8)

### VF-05.1: 4-Way Surface Count Reconciliation

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-05.1-count-reconciliation.txt
import re
from pathlib import Path
repo=Path('/home/zaks/zakops-agent-api')
m=(repo/'INFRASTRUCTURE_MANIFEST.md').read_text()
cs=(repo/'.claude/rules/contract-surfaces.md').read_text()
cla=(repo/'CLAUDE.md').read_text()
vs=(repo/'tools/infra/validate-contract-surfaces.sh').read_text()
sec=re.search(r'## Contract Surfaces \(Hybrid Guardrail\)\n((?:- .*\n)+)',m)
man_count=len([ln for ln in sec.group(1).splitlines() if ln.strip().startswith('- ')]) if sec else -1
cs_count=len(re.findall(r'^### Surface \d+:',cs,flags=re.M))
cla_count=int(re.search(r'Contract Surfaces \((\d+) Total\)',cla).group(1))
vs_count=int(re.search(r'Validates all (\d+) contract surfaces',vs).group(1))
print('contract_surfaces_md=',cs_count)
print('claude_md=',cla_count)
print('validator_header=',vs_count)
print('manifest_section=',man_count)
ok=(cs_count==cla_count==vs_count==man_count==9)
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** all four sources report 9.

### VF-05.2: Boot CHECK 2 Logic Includes Expanded Reconciliation Inputs

```bash
{
  echo "=== VF-05.2 CHECK2 LOGIC ==="
  rg -n 'CHECK 2|Surface Count Consistency|CLAUDE.md|MEMORY.md|validate-contract-surfaces|INFRASTRUCTURE_MANIFEST|contract-surfaces' /home/zaks/.claude/hooks/session-start.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-05.2-check2-logic.txt
```

**PASS if:** CHECK 2 explicitly inspects all intended reconciliation sources added by mission.

### VF-05.3: Boot Diagnostics Runtime Verdict Presence

```bash
{
  echo "=== VF-05.3 BOOT VERDICT RUNTIME ==="
  sudo -n bash /home/zaks/.claude/hooks/session-start.sh
  cat /tmp/claude-boot-verdict.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-05.3-boot-verdict.txt
```

**PASS if:** verdict renders and includes CHECK 2 status without runtime errors.

**Gate VF-05:** All 3 checks PASS.

---

## Verification Family 06 — Completion and Bookkeeping Integrity (AC-10)

### VF-06.1: Completion Report Integrity

```bash
{
  echo "=== VF-06.1 COMPLETION REPORT ==="
  ls -l /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md || true
  rg -n 'AC-1|AC-10|PASS|FAIL|INFO' /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-06.1-completion-report.txt
```

**PASS if:** completion report exists and includes AC status mapping.

### VF-06.2: CHANGES Entry Integrity

```bash
{
  echo "=== VF-06.2 CHANGES ENTRY ==="
  rg -n 'INFRA-TRUTH-REPAIR-001' /home/zaks/bookkeeping/CHANGES.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-06.2-changes-entry.txt
```

**PASS if:** CHANGES has mission entry.

### VF-06.3: Mission Checkpoint Integrity

```bash
{
  echo "=== VF-06.3 CHECKPOINT FILE ==="
  ls -l /home/zaks/bookkeeping/mission-checkpoints/INFRA-TRUTH-REPAIR-001.md
  tail -n 40 /home/zaks/bookkeeping/mission-checkpoints/INFRA-TRUTH-REPAIR-001.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-06.3-checkpoint-integrity.txt
```

**PASS if:** checkpoint exists and contains completion state.

### VF-06.4: Evidence Completeness Audit

```bash
{
  echo "=== VF-06.4 EVIDENCE COMPLETENESS ==="
  find /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence -maxdepth 1 -type f | sort
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/VF-06.4-evidence-completeness.txt
```

**PASS if:** every PF/VF/XC/ST check produced evidence file.

**Gate VF-06:** All 4 checks PASS.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Source Mission AC Claims vs Completion Report Claims

```bash
{
  echo "=== XC-1 AC RECONCILIATION ==="
  rg -n '^### AC-' /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001.md
  rg -n 'AC-1|AC-2|AC-3|AC-4|AC-5|AC-6|AC-7|AC-8|AC-9|AC-10' /home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/XC-1-ac-reconciliation.txt
```

**PASS if:** all 10 ACs are explicitly accounted for in completion report.

### XC-2: Agent Preloads vs Local Skill Directory

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/XC-2-agent-preload-vs-skills.txt
from pathlib import Path
import re
skills={p.name for p in Path('/home/zaks/.claude/skills').iterdir() if p.is_dir()}
agents=Path('/home/zaks/.claude/agents').glob('*.md')
ok=True
for a in agents:
    txt=a.read_text()
    refs=re.findall(r'/home/zaks/.claude/skills/([A-Za-z0-9_-]+)',txt)
    for r in refs:
        exists=r in skills
        print(a.name, r, 'PASS' if exists else 'FAIL')
        if not exists: ok=False
print('OVERALL=', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
PY
```

**PASS if:** every preload reference maps to a local skill directory.

### XC-3: Manifest Surface Section vs Real Filesystem Artifact Presence

```bash
{
  echo "=== XC-3 MANIFEST VS FILESYSTEM ==="
  ls -l /home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json
  ls -l /home/zaks/zakops-agent-api/packages/contracts/openapi/agent-api.json
  ls -l /home/zaks/zakops-agent-api/packages/contracts/openapi/rag-api.json
  ls -l /home/zaks/zakops-agent-api/packages/contracts/mcp/tool-schemas.json
  ls -l /home/zaks/zakops-agent-api/packages/contracts/sse/agent-events.schema.json
  rg -n '^## Contract Surfaces \(Hybrid Guardrail\)|NOT FOUND|present' /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/XC-3-manifest-vs-fs.txt
```

**PASS if:** manifest status agrees with real artifact presence.

### XC-4: MEMORY Skill Inventory vs Active Skills

```bash
{
  echo "=== XC-4 MEMORY VS SKILLS ==="
  ls -1 /home/zaks/.claude/skills
  sudo -n grep -nEi 'skills|frontend-design|api-conventions|atomic-workflow|code-style|debugging-playbook|project-context|security-and-data|verification-standards' /root/.claude/projects/-home-zaks/memory/MEMORY.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/XC-4-memory-vs-skills.txt
```

**PASS if:** memory inventory is complete and current.

### XC-5: Validation Command Surface Count Agreement

```bash
{
  echo "=== XC-5 VALIDATION COMMAND AGREEMENT ==="
  cd /home/zaks/zakops-agent-api && make -n validate-contract-surfaces
  cd /home/zaks/zakops-agent-api && make -n validate-local
  cd /home/zaks/zakops-agent-api && make -n validate-full
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/XC-5-validation-command-agreement.txt
```

**PASS if:** command graph is coherent with 9-surface target state.

---

## 5. Stress Tests (ST)

### ST-1: Snapshot Determinism (3 Consecutive Runs)

```bash
{
  echo "=== ST-1 SNAPSHOT DETERMINISM ==="
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  cd /home/zaks/zakops-agent-api && make infra-snapshot
  cd /home/zaks/zakops-agent-api && make infra-snapshot
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/ST-1-snapshot-determinism.txt
```

**PASS if:** all three runs succeed without generator error and produce coherent manifest output.

### ST-2: Stop Hook Stability Across Repeated Invocations

```bash
{
  echo "=== ST-2 STOP HOOK STABILITY ==="
  cd /home/zaks/zakops-agent-api && timeout 30 bash /home/zaks/.claude/hooks/stop.sh
  cd /home/zaks/zakops-agent-api && timeout 30 bash /home/zaks/.claude/hooks/stop.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/ST-2-stop-hook-stability.txt
```

**PASS if:** no timeout or regression on repeated runs.

### ST-3: Boot Diagnostics TTL Behavior

```bash
{
  echo "=== ST-3 BOOT TTL ==="
  sudo -n bash /home/zaks/.claude/hooks/session-start.sh
  stat -c '%Y %n' /tmp/claude-session-boot /tmp/claude-boot-evidence /tmp/claude-boot-verdict.md
  sudo -n bash /home/zaks/.claude/hooks/session-start.sh
  stat -c '%Y %n' /tmp/claude-session-boot /tmp/claude-boot-evidence /tmp/claude-boot-verdict.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/ST-3-boot-ttl.txt
```

**PASS if:** script behaves according to TTL/dedup expectations without error.

### ST-4: Root/User Path Resolution Safety

```bash
{
  echo "=== ST-4 ROOT USER PATH SAFETY ==="
  sudo -n bash -lc 'test -f /home/zaks/.claude/skills/api-conventions/SKILL.md && echo PASS_api_conventions'
  sudo -n bash -lc 'test -f /home/zaks/.claude/skills/frontend-design/SKILL.md && echo PASS_frontend_design'
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/ST-4-root-user-path-safety.txt
```

**PASS if:** root-context checks confirm absolute preload paths are valid.

### ST-5: No Active Reintroduction of `~/.claude/skills` in Runtime Config Files

```bash
{
  echo "=== ST-5 REINTRODUCTION SWEEP ==="
  rg -n '~/.claude/skills' /home/zaks/.claude/agents /home/zaks/.claude/commands /home/zaks/.claude/hooks /home/zaks/.claude/settings.json || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/ST-5-reintroduction-sweep.txt
```

**PASS if:** zero active reintroductions.

### ST-6: Forbidden-File Regression Guard

```bash
{
  echo "=== ST-6 FORBIDDEN FILE REGRESSION GUARD ==="
  cd /home/zaks/zakops-agent-api && git status --short
  cd /home/zaks/zakops-agent-api && git diff --name-only | rg 'generated\.ts$|_models\.py$|/migrations/' || true
} | tee /home/zaks/bookkeeping/qa-verifications/QA-ITR-VERIFY-001/evidence/ST-6-forbidden-regression-guard.txt
```

**PASS if:** no unintended forbidden-file regressions are introduced by remediation.

---

## 6. Remediation Protocol

When a gate fails:

1. Capture failing evidence file path and failing command.
2. Classify failure:
- `MISSING_FIX`
- `REGRESSION`
- `SCOPE_GAP`
- `FALSE_POSITIVE`
- `NOT_IMPLEMENTED`
- `PARTIAL`
- `VIOLATION`

3. Apply minimal remediation in scope of `INFRA-TRUTH-REPAIR-001`.
4. Re-run only the failed gate first.
5. Re-run:
- `cd /home/zaks/zakops-agent-api && make validate-local`
- `cd /home/zaks/zakops-agent-api && make validate-full`

6. Record remediation details in scorecard and completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: Add CI gate that forbids active `~/.claude/skills` references in agent files.
### ENH-2: Add unit tests for `/home/zaks/tools/infra/generate-manifest.sh` with failure-injection cases.
### ENH-3: Add machine-readable manifest schema and schema validation step.
### ENH-4: Add a dedicated `make validate-surface9` target and include it in docs consistently.
### ENH-5: Add preflight checker for root-owned files under `/home/zaks/.claude/` that should be user-owned.
### ENH-6: Extend boot CHECK 2 to include checksums/hashes, not only counts.
### ENH-7: Auto-generate a surface count reconciliation table into completion reports.
### ENH-8: Add explicit profile for enabling/disabling Playwright MCP with documented policy.
### ENH-9: Add regression test ensuring `infra-snapshot` never prints success on non-zero generator exit.
### ENH-10: Add a slash command to emit QA evidence scaffolding for new QA missions.

---

## 8. Scorecard Template

```
QA-ITR-VERIFY-001 — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL / NOT_EXECUTED ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (Track1 Agent/Skill Integrity): __ / 5 checks PASS
  VF-02 (9-Surface Validation Wiring): __ / 6 checks PASS
  VF-03 (Stop Hook Runtime Consistency): __ / 4 checks PASS
  VF-04 (Snapshot Fail-Fast + Manifest Truth): __ / 7 checks PASS
  VF-05 (Count Reconciliation + Boot Check): __ / 3 checks PASS
  VF-06 (Completion + Bookkeeping): __ / 4 checks PASS

Cross-Consistency:
  XC-1 through XC-5: __ / 5 checks PASS

Stress Tests:
  ST-1 through ST-6: __ / 6 tests PASS

Total: __ / 45 checks PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not build Surfaces 10–14 here.
2. Do not introduce application feature work.
3. Remediate only what is required for source mission acceptance criteria.
4. Preserve generated-file protection and migration immutability.
5. Every PASS must have evidence output captured with `tee`.
6. If services are unavailable, classify service-dependent checks as `SKIP` with evidence, not silent PASS.
7. Preserve existing remediations from SURFACE-REMEDIATION-001/002.
8. Do not rewrite bookkeeping reference docs as part of QA.
9. Keep all file paths absolute in outputs and reports.
10. If a check is ambiguous, mark `INFO` and escalate; do not force a PASS.

---

## 10. Stop Condition

Stop when all 45 QA checks pass (or are explicitly classified and justified as `SKIP/INFO/FALSE_POSITIVE`), remediations are re-verified, `make validate-local` and `make validate-full` pass, and the scorecard is complete with evidence file paths.

Do not unblock `MISSION-SURFACES-10-14-REGISTER-001` unless overall verdict is `FULL PASS`.

---

*End of Mission Prompt — QA-ITR-VERIFY-001*
