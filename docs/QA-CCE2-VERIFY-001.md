# MISSION: QA-CCE2-VERIFY-001
## Independent QA Verification and Remediation - CLAUDE-CODE-ENHANCE-002 (Slim)
## Date: 2026-02-11
## Classification: QA Verification and Remediation
## Prerequisite: /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md execution complete
## Successor: Claude hook enhancement backlog closure after FULL PASS

---

## Preamble: Builder Operating Context

This is an independent QA mission. It verifies implementation quality for the slimmed `CLAUDE-CODE-ENHANCE-002` scope and applies surgical remediation only if a gate fails.

---

## 1. Mission Objective

Verify, cross-check, stress-test, and remediate execution results for:
- `/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md`

Expected source shape:
- 4 phases (`Phase 0` through `Phase 3`)
- 10 acceptance criteria (`AC-1` through `AC-10`)

Expected execution artifacts:
- `/home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-BASELINE.md`
- `/home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/CLAUDE-CODE-ENHANCE-002.md`
- `/home/zaks/bookkeeping/CHANGES.md` entry for `CLAUDE-CODE-ENHANCE-002`

Scope:
- Verify closure of ENH-1/2/3/4/5/7/10.
- Confirm deterministic validation flow via `make qa-cce-verify`.
- Confirm no regressions in hook baseline.

Out of scope:
- ENH-6/8/9 governance automation (intentionally removed from source mission)
- product feature changes.

---

## 2. Pre-Flight (PF)

### QA Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence
```

### PF-1: Source Mission Integrity

```bash
{
  echo "=== PF-1 SOURCE MISSION INTEGRITY ==="
  wc -l /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md
  rg -n '^## Phase [0-9]+' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md
  rg -n '^### AC-[0-9]+:' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md
  python3 - <<'PY'
from pathlib import Path
import re
p=Path('/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md')
t=p.read_text()
phase_count=len(re.findall(r'^## Phase [0-9]+', t, flags=re.M))
ac_count=len(re.findall(r'^### AC-[0-9]+:', t, flags=re.M))
print('phase_count=', phase_count)
print('ac_count=', ac_count)
raise SystemExit(0 if (phase_count==4 and ac_count==10) else 1)
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/PF-1-source-mission-integrity.txt
```

**PASS if:** source mission reports 4 phases and 10 ACs.

### PF-2: Execution Artifact Presence

```bash
{
  echo "=== PF-2 EXECUTION ARTIFACTS ==="
  ls -l /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-BASELINE.md
  ls -l /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md
  ls -l /home/zaks/bookkeeping/mission-checkpoints/CLAUDE-CODE-ENHANCE-002.md
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'CLAUDE-CODE-ENHANCE-002' /home/zaks/bookkeeping/CHANGES.md
  else
    sudo rg -n 'CLAUDE-CODE-ENHANCE-002' /home/zaks/bookkeeping/CHANGES.md
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/PF-2-execution-artifacts.txt
```

**PASS if:** all artifacts exist and CHANGES includes mission ID.

### PF-3: Baseline Runtime Health

```bash
{
  echo "=== PF-3 BASELINE HEALTH ==="
  python3 /home/zaks/bookkeeping/scripts/validate-claude-hook-config.py
  bash /home/zaks/bookkeeping/scripts/tests/test-compact-recovery-json.sh
  bash /home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh
  cd /home/zaks/zakops-agent-api && make qa-cce-verify
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/PF-3-baseline-health.txt
```

**PASS if:** all checks exit 0.

### PF-4: Hook Snapshot

```bash
{
  echo "=== PF-4 HOOK SNAPSHOT ==="
  ls -l /home/zaks/.claude/hooks/pre-compact.sh
  ls -l /home/zaks/.claude/hooks/task-completed.sh
  ls -l /home/zaks/.claude/hooks/compact-recovery.sh
  bash -n /home/zaks/.claude/hooks/pre-compact.sh
  bash -n /home/zaks/.claude/hooks/task-completed.sh
  bash -n /home/zaks/.claude/hooks/compact-recovery.sh
  file /home/zaks/.claude/hooks/pre-compact.sh
  file /home/zaks/.claude/hooks/task-completed.sh
  file /home/zaks/.claude/hooks/compact-recovery.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/PF-4-hook-snapshot.txt
```

**PASS if:** scripts exist, parse, and are LF-safe.

### PF-5: Scope Applicability Check

```bash
{
  echo "=== PF-5 SCOPE APPLICABILITY ==="
  rg -n 'make validate-local is not a required gate|does not change application codepaths' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/PF-5-scope-applicability.txt
```

**PASS if:** mission explicitly marks `make validate-local` as non-applicable.

---

## 3. Verification Families (VF)

## Verification Family 01 - Evidence and AC Coverage Integrity

### VF-01.1: Completion Report Structure

```bash
{
  echo "=== VF-01.1 COMPLETION STRUCTURE ==="
  wc -l /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md
  rg -n 'Phase 0|Phase 1|Phase 2|Phase 3|AC-1|AC-10|PASS|FAIL' /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-01.1-completion-structure.txt
```

**PASS if:** all phases and AC range are represented.

### VF-01.2: Baseline Integrity

```bash
{
  echo "=== VF-01.2 BASELINE INTEGRITY ==="
  rg -n 'ENH-1|ENH-2|ENH-3|ENH-4|ENH-5|ENH-7|ENH-10' /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-BASELINE.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-01.2-baseline-integrity.txt
```

**PASS if:** baseline includes all 7 enhancement IDs.

### VF-01.3: Checkpoint Closure

```bash
{
  echo "=== VF-01.3 CHECKPOINT CLOSURE ==="
  rg -n 'CLOSED|COMPLETE|QA-CCE2-VERIFY-001|next command' /home/zaks/bookkeeping/mission-checkpoints/CLAUDE-CODE-ENHANCE-002.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-01.3-checkpoint-closure.txt
```

**PASS if:** checkpoint indicates closure and QA handoff.

### VF-01.4: CHANGES Traceability

```bash
{
  echo "=== VF-01.4 CHANGES TRACEABILITY ==="
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'CLAUDE-CODE-ENHANCE-002|qa-cce-verify|validate-claude-hook-config|fixture mode|GATE_RESULT|SNAPSHOT_RETENTION' /home/zaks/bookkeeping/CHANGES.md
  else
    sudo rg -n 'CLAUDE-CODE-ENHANCE-002|qa-cce-verify|validate-claude-hook-config|fixture mode|GATE_RESULT|SNAPSHOT_RETENTION' /home/zaks/bookkeeping/CHANGES.md
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-01.4-changes-traceability.txt
```

**PASS if:** CHANGES includes mission and key deliverables.

**Gate VF-01:** all 4 checks PASS.

---

## Verification Family 02 - Hook Runtime Enhancements (AC-2,3,4,5)

### VF-02.1: Retention Config in pre-compact

```bash
{
  echo "=== VF-02.1 RETENTION CONFIG ==="
  rg -n 'SNAPSHOT_RETENTION|\$\{SNAPSHOT_RETENTION:-10\}' /home/zaks/.claude/hooks/pre-compact.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-02.1-retention-config.txt
```

**PASS if:** env-driven retention logic with safe default exists.

### VF-02.2: Retention Override Runtime

```bash
{
  echo "=== VF-02.2 RETENTION OVERRIDE RUNTIME ==="
  SNAPSHOT_RETENTION=3 bash -c 'for i in 1 2 3 4 5; do echo "{\"trigger\":\"vf022-$i\",\"session_id\":\"vf022-$i\"}" | bash /home/zaks/.claude/hooks/pre-compact.sh; done'
  C=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md 2>/dev/null | wc -l | tr -d ' ')
  echo "count=$C"
  test "$C" -le 3
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-02.2-retention-override-runtime.txt
```

**PASS if:** override cap is enforced.

### VF-02.3: Fixture Mode in task-completed

```bash
{
  echo "=== VF-02.3 FIXTURE MODE ==="
  rg -n 'TASK_COMPLETED_TARGETS' /home/zaks/.claude/hooks/task-completed.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-02.3-fixture-mode.txt
```

**PASS if:** fixture mode path exists in script.

### VF-02.4: Machine Markers in task-completed

```bash
{
  echo "=== VF-02.4 MACHINE MARKERS ==="
  bash /home/zaks/.claude/hooks/task-completed.sh > /tmp/qa-cce2-vf024.out 2>&1 || true
  rg -n 'GATE_RESULT:' /tmp/qa-cce2-vf024.out
  rm -f /tmp/qa-cce2-vf024.out
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-02.4-machine-markers.txt
```

**PASS if:** output contains `GATE_RESULT:` markers.

### VF-02.5: Objective compact context quality

```bash
bash /home/zaks/.claude/hooks/compact-recovery.sh | python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-02.5-objective-context-quality.txt
import json,sys
j=json.load(sys.stdin)
h=j.get('hookSpecificOutput',{})
ctx=h.get('additionalContext','')
print('non_empty=', bool(ctx.strip()))
print('has_paths=', 'Key Paths Reminder' in ctx)
print('has_changes=', 'Recent Changes' in ctx)
raise SystemExit(0 if (ctx.strip() and 'Key Paths Reminder' in ctx and 'Recent Changes' in ctx) else 1)
PY
```

**PASS if:** objective criteria pass.

**Gate VF-02:** all 5 checks PASS.

---

## Verification Family 03 - Validator, Harnesses, and Make Wiring (AC-6,7,8,9)

### VF-03.1: Hook Contract Validator Runtime

```bash
{
  echo "=== VF-03.1 HOOK CONTRACT VALIDATOR ==="
  ls -l /home/zaks/bookkeeping/scripts/validate-claude-hook-config.py
  python3 /home/zaks/bookkeeping/scripts/validate-claude-hook-config.py
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-03.1-hook-contract-validator.txt
```

**PASS if:** validator exists and exits 0.

### VF-03.2: Compact Recovery Harness Runtime

```bash
{
  echo "=== VF-03.2 COMPACT HARNESS ==="
  ls -l /home/zaks/bookkeeping/scripts/tests/test-compact-recovery-json.sh
  bash /home/zaks/bookkeeping/scripts/tests/test-compact-recovery-json.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-03.2-compact-harness.txt
```

**PASS if:** harness exists and exits 0.

### VF-03.3: TaskCompleted Fixture Harness Runtime

```bash
{
  echo "=== VF-03.3 TASK HARNESS ==="
  ls -l /home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh
  bash /home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-03.3-task-harness.txt
```

**PASS if:** harness exists and exits 0.

### VF-03.4: Combined Runner Runtime

```bash
{
  echo "=== VF-03.4 COMBINED RUNNER ==="
  ls -l /home/zaks/bookkeeping/scripts/run-qa-cce-verify.sh
  bash /home/zaks/bookkeeping/scripts/run-qa-cce-verify.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-03.4-combined-runner.txt
```

**PASS if:** runner exists and exits 0.

### VF-03.5: Make Target Runtime

```bash
{
  echo "=== VF-03.5 MAKE TARGET RUNTIME ==="
  rg -n '^qa-cce-verify:' /home/zaks/zakops-agent-api/Makefile
  cd /home/zaks/zakops-agent-api && make qa-cce-verify
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-03.5-make-target-runtime.txt
```

**PASS if:** target exists and exits 0.

**Gate VF-03:** all 5 checks PASS.

---

## Verification Family 04 - No Regression and Scope Integrity (AC-10)

### VF-04.1: Hook Event Integrity

```bash
python3 - <<'PY' | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-04.1-hook-event-integrity.txt
import json
j=json.load(open('/home/zaks/.claude/settings.json'))
req={'PreToolUse','PostToolUse','SessionStart','Stop','PreCompact','TaskCompleted'}
h=set(j.get('hooks',{}).keys())
print('events=', sorted(h))
print('missing=', sorted(req-h))
raise SystemExit(0 if req.issubset(h) else 1)
PY
```

**PASS if:** all required hook events remain present.

### VF-04.2: Core Hook Presence

```bash
{
  echo "=== VF-04.2 CORE HOOK PRESENCE ==="
  for f in pre-edit.sh pre-bash.sh post-edit.sh session-boot.sh session-start.sh stop.sh memory-sync.sh; do
    test -f "/home/zaks/.claude/hooks/$f" || exit 1
    ls -l "/home/zaks/.claude/hooks/$f"
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-04.2-core-hook-presence.txt
```

**PASS if:** existing hook chain files still exist.

### VF-04.3: Syntax + CRLF Integrity

```bash
{
  echo "=== VF-04.3 SYNTAX + CRLF INTEGRITY ==="
  bash -n /home/zaks/.claude/hooks/pre-compact.sh
  bash -n /home/zaks/.claude/hooks/task-completed.sh
  bash -n /home/zaks/.claude/hooks/compact-recovery.sh
  ! file /home/zaks/.claude/hooks/pre-compact.sh | grep -q CRLF
  ! file /home/zaks/.claude/hooks/task-completed.sh | grep -q CRLF
  ! file /home/zaks/.claude/hooks/compact-recovery.sh | grep -q CRLF
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-04.3-syntax-crlf-integrity.txt
```

**PASS if:** syntax clean and no CRLF regressions.

### VF-04.4: Scope Compliance (`validate-local` non-applicable)

```bash
{
  echo "=== VF-04.4 SCOPE COMPLIANCE ==="
  rg -n 'make validate-local is not a required gate' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md
  rg -n 'does not change application codepaths|scope fence' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/VF-04.4-scope-compliance.txt
```

**PASS if:** mission clearly encodes the non-applicability and scope rationale.

**Gate VF-04:** all 4 checks PASS.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Make target ↔ runner consistency

```bash
{
  echo "=== XC-1 MAKE TARGET RUNNER CONSISTENCY ==="
  rg -n '^qa-cce-verify:' /home/zaks/zakops-agent-api/Makefile
  rg -n 'run-qa-cce-verify.sh' /home/zaks/zakops-agent-api/Makefile
  test -f /home/zaks/bookkeeping/scripts/run-qa-cce-verify.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/XC-1-make-runner-consistency.txt
```

### XC-2: Hook validator ↔ settings consistency

```bash
{
  echo "=== XC-2 VALIDATOR SETTINGS CONSISTENCY ==="
  python3 /home/zaks/bookkeeping/scripts/validate-claude-hook-config.py
  python3 - <<'PY'
import json
j=json.load(open('/home/zaks/.claude/settings.json'))
print('PreCompact=', len(j.get('hooks',{}).get('PreCompact',[])))
print('TaskCompleted=', len(j.get('hooks',{}).get('TaskCompleted',[])))
print('SessionStart=', len(j.get('hooks',{}).get('SessionStart',[])))
PY
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/XC-2-validator-settings-consistency.txt
```

### XC-3: Fixture mode code ↔ fixture harness consistency

```bash
{
  echo "=== XC-3 FIXTURE CONSISTENCY ==="
  rg -n 'TASK_COMPLETED_TARGETS' /home/zaks/.claude/hooks/task-completed.sh
  rg -n 'TASK_COMPLETED_TARGETS|fixture' /home/zaks/bookkeeping/scripts/tests/test-task-completed-fixture-mode.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/XC-3-fixture-consistency.txt
```

### XC-4: Retention code ↔ runtime behavior consistency

```bash
{
  echo "=== XC-4 RETENTION CONSISTENCY ==="
  rg -n 'SNAPSHOT_RETENTION' /home/zaks/.claude/hooks/pre-compact.sh
  SNAPSHOT_RETENTION=2 bash -c 'for i in 1 2 3 4; do echo "{\"trigger\":\"xc4-$i\",\"session_id\":\"xc4-$i\"}" | bash /home/zaks/.claude/hooks/pre-compact.sh; done'
  C=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md | wc -l | tr -d ' ')
  echo "count=$C"
  test "$C" -le 2
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/XC-4-retention-consistency.txt
```

### XC-5: Completion report ↔ AC coverage consistency

```bash
{
  echo "=== XC-5 COMPLETION AC CONSISTENCY ==="
  rg -n '^### AC-1:|^### AC-10:' /home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md
  rg -n 'AC-1|AC-10|qa-cce-verify|fixture mode|GATE_RESULT|SNAPSHOT_RETENTION' /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/XC-5-completion-ac-consistency.txt
```

### XC-6: Completion narrative ↔ CHANGES narrative consistency

```bash
{
  echo "=== XC-6 COMPLETION CHANGES CONSISTENCY ==="
  rg -n 'qa-cce-verify|validate-claude-hook-config|fixture mode|GATE_RESULT|SNAPSHOT_RETENTION' /home/zaks/bookkeeping/docs/CLAUDE-CODE-ENHANCE-002-COMPLETION.md
  if [ -r /home/zaks/bookkeeping/CHANGES.md ]; then
    rg -n 'CLAUDE-CODE-ENHANCE-002|qa-cce-verify|validate-claude-hook-config|fixture mode|GATE_RESULT|SNAPSHOT_RETENTION' /home/zaks/bookkeeping/CHANGES.md
  else
    sudo rg -n 'CLAUDE-CODE-ENHANCE-002|qa-cce-verify|validate-claude-hook-config|fixture mode|GATE_RESULT|SNAPSHOT_RETENTION' /home/zaks/bookkeeping/CHANGES.md
  fi
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/XC-6-completion-changes-consistency.txt
```

**XC Gate:** XC-1 through XC-6 all PASS.

---

## 5. Stress Tests (ST)

### ST-1: `make qa-cce-verify` deterministic (3 runs)

```bash
{
  echo "=== ST-1 DETERMINISTIC MAKE TARGET ==="
  cd /home/zaks/zakops-agent-api && make qa-cce-verify
  cd /home/zaks/zakops-agent-api && make qa-cce-verify
  cd /home/zaks/zakops-agent-api && make qa-cce-verify
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/ST-1-deterministic-make-target.txt
```

### ST-2: Fixture mode pass/fail cycle

```bash
{
  echo "=== ST-2 FIXTURE PASS FAIL CYCLE ==="
  TMP=/tmp/qa-cce2-st2
  mkdir -p "$TMP"
  printf '#!/usr/bin/env bash\necho ok\n' > "$TMP/clean.sh"
  chmod +x "$TMP/clean.sh"
  TASK_COMPLETED_TARGETS="$TMP/clean.sh" bash /home/zaks/.claude/hooks/task-completed.sh

  printf '#!/usr/bin/env bash\r\necho bad\r\n' > "$TMP/bad.sh"
  chmod +x "$TMP/bad.sh"
  set +e
  TASK_COMPLETED_TARGETS="$TMP/bad.sh" bash /home/zaks/.claude/hooks/task-completed.sh
  RC=$?
  set -e
  echo "rc_bad=$RC"
  test "$RC" -eq 2
  rm -rf "$TMP"
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/ST-2-fixture-pass-fail-cycle.txt
```

### ST-3: Retention boundary checks

```bash
{
  echo "=== ST-3 RETENTION BOUNDARY ==="
  SNAPSHOT_RETENTION=1 bash -c 'for i in 1 2 3; do echo "{\"trigger\":\"st3a-$i\",\"session_id\":\"st3a-$i\"}" | bash /home/zaks/.claude/hooks/pre-compact.sh; done'
  C1=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md | wc -l | tr -d ' ')
  echo "count_ret1=$C1"
  test "$C1" -le 1

  SNAPSHOT_RETENTION=20 bash -c 'for i in 1 2 3 4 5; do echo "{\"trigger\":\"st3b-$i\",\"session_id\":\"st3b-$i\"}" | bash /home/zaks/.claude/hooks/pre-compact.sh; done'
  C2=$(ls -1 /home/zaks/bookkeeping/snapshots/pre-compact-*.md | wc -l | tr -d ' ')
  echo "count_ret20=$C2"
  test "$C2" -le 20
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/ST-3-retention-boundary.txt
```

### ST-4: Compact recovery parse stability (5 runs)

```bash
{
  echo "=== ST-4 COMPACT RECOVERY STABILITY ==="
  for i in 1 2 3 4 5; do
    bash /home/zaks/.claude/hooks/compact-recovery.sh | python3 - <<'PY'
import json,sys
j=json.load(sys.stdin)
ctx=j.get('hookSpecificOutput',{}).get('additionalContext','')
print('len=', len(ctx))
raise SystemExit(0 if ctx.strip() else 1)
PY
  done
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/ST-4-compact-recovery-stability.txt
```

### ST-5: Gate markers remain parseable in failure mode

```bash
{
  echo "=== ST-5 MARKER PARSE FAILURE MODE ==="
  TMP=/tmp/qa-cce2-st5
  mkdir -p "$TMP"
  printf '#!/usr/bin/env bash\r\necho bad\r\n' > "$TMP/bad.sh"
  chmod +x "$TMP/bad.sh"
  set +e
  TASK_COMPLETED_TARGETS="$TMP/bad.sh" bash /home/zaks/.claude/hooks/task-completed.sh > /tmp/qa-cce2-st5.out 2>&1
  RC=$?
  set -e
  echo "rc=$RC"
  test "$RC" -eq 2
  rg -n 'GATE_RESULT:' /tmp/qa-cce2-st5.out
  rm -rf "$TMP" /tmp/qa-cce2-st5.out
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/ST-5-marker-parse-failure-mode.txt
```

### ST-6: Combined runner repeatability

```bash
{
  echo "=== ST-6 COMBINED RUNNER REPEATABILITY ==="
  bash /home/zaks/bookkeeping/scripts/run-qa-cce-verify.sh
  bash /home/zaks/bookkeeping/scripts/run-qa-cce-verify.sh
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/ST-6-runner-repeatability.txt
```

### ST-7: Post-stress no-regression hook contract check

```bash
{
  echo "=== ST-7 POST STRESS CONTRACT CHECK ==="
  python3 /home/zaks/bookkeeping/scripts/validate-claude-hook-config.py
  cd /home/zaks/zakops-agent-api && make qa-cce-verify
} | tee /home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/evidence/ST-7-post-stress-contract-check.txt
```

**ST Gate:** ST-1 through ST-7 all PASS.

---

## 6. Remediation Protocol

For any FAIL:

1. Inspect the failing evidence file.
2. Classify as one of:
   - `MISSING_FIX`
   - `REGRESSION`
   - `SCOPE_GAP`
   - `FALSE_POSITIVE`
   - `NOT_IMPLEMENTED`
   - `PARTIAL`
   - `VIOLATION`
3. Apply minimal in-scope fix.
4. Re-run the failed check.
5. Re-run affected VF gate.
6. Re-run XC gate and ST-7.
7. Record remediation in completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: JSON output mode for validators
### ENH-2: Shared marker formatting utility
### ENH-3: Auto-generate AC trace from completion report
### ENH-4: Hook contract drift alert in stop diagnostics
### ENH-5: Nightly dry-run for `qa-cce-verify`
### ENH-6: Compact context diff report between runs
### ENH-7: Fixture harness summary report generator
### ENH-8: Strict optional retention clamp warnings
### ENH-9: CI smoke check for `qa-cce-verify` target
### ENH-10: Evidence manifest auto-indexer

---

## 8. Scorecard Template

```text
QA-CCE2-VERIFY-001 - Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1: [ PASS / FAIL ]
  PF-2: [ PASS / FAIL ]
  PF-3: [ PASS / FAIL ]
  PF-4: [ PASS / FAIL ]
  PF-5: [ PASS / FAIL ]

Verification Families:
  VF-01 (Evidence + AC Coverage): __ / 4 PASS
  VF-02 (Hook Runtime Enhancements): __ / 5 PASS
  VF-03 (Validator/Harness/Make): __ / 5 PASS
  VF-04 (No Regression + Scope): __ / 4 PASS

Cross-Consistency:
  XC-1 through XC-6: __ / 6 PASS

Stress Tests:
  ST-1 through ST-7: __ / 7 PASS

Total: __ / 31 required checks PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. Do not build new features.
2. Remediate, do not redesign.
3. Evidence-first: every PASS needs captured output.
4. Keep fixes in scope of slim mission only.
5. Preserve hook exit semantics.
6. Do not add governance artifacts that source mission intentionally removed.
7. Respect `validate-local` non-applicability for this mission.
8. Do not touch generated files.
9. Do not use destructive git commands.
10. Re-run dependent gates after any remediation.

---

## 10. Stop Condition

Stop when all 31 required checks pass (or are explicitly justified as conditional), remediations are re-verified, and the scorecard is complete with evidence references.

---
*End of Mission Prompt - QA-CCE2-VERIFY-001*
