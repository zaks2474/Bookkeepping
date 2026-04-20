# MISSION: QA-CODEX-ALIGN-VERIFY-001
## Independent QA Verification and Remediation for CODEX-ALIGN-001 (Durability Hardening)
## Date: 2026-02-12
## Classification: Post-Implementation QA Verification and In-Scope Remediation
## Prerequisite: `/home/zaks/bookkeeping/missions/CODEX-ALIGN-001-CODEX-CLI-ALIGNMENT.md` marked COMPLETE with artifacts present
## Successor: `QA-CODEX-ALIGN-VERIFY-002` only if any required gate remains FAIL or BLOCKED after remediation

---

## Mission Objective
Perform independent QA verification and in-scope remediation for `CODEX-ALIGN-001` with focus on correctness, security, and durability.

This QA mission must explicitly resolve the critical post-implementation defects now observed:
- `~/.codex/config.toml` parser failure at `history.persistence = "filesystem"`
- repeated "invalid SKILL.md" loading warnings
- root-path coupling in wrapper/shell integration
- ambiguous MCP source-of-truth and auth assumptions
- insufficient `CODEX_FORCE` governance
- mismatch between claimed PASS reports and current runtime behavior

This mission verifies not only file presence, but runtime behavior under:
1. fresh session restart
2. new login shell
3. full system reboot (required for final PASS)

---

## Context
Primary sources:
- `/home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md`
- `/home/zaks/bookkeeping/missions/CODEX-ALIGN-001-CODEX-CLI-ALIGNMENT.md`
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/final-verification.md`
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/mcp-verification.md`

Observed runtime failures to verify/remediate:
- `codex` config parse error: unknown variant `filesystem` for `history.persistence`
- repeated warnings: skipped skill(s) due to invalid `SKILL.md`
- repeated warnings/errors: failed to read `/home/zaks/.codex/config.toml`
- `codex-safe` boot halt due inaccessible memory path and health-log append permission

Required corrective recommendations from pre-execution review:
1. Fix MCP source-of-truth and auth assumptions first.
2. Switch mission commands to user-owned binaries (`/home/zaks/.npm-global/bin`).
3. Add strict `CODEX_FORCE` audit requirements.
4. Clarify MCP pass criteria (`configured` vs `connectivity-blocked`).
5. Relax Codex version gate to compatibility band (not exact patch pin).

---

## Architectural Constraints
- Scope is QA verification plus minimal in-scope remediation only for CODEX alignment artifacts.
- Do not modify product application behavior outside Codex alignment files.
- No plaintext secrets in config, scripts, evidence, or reports.
- All execution paths and evidence targets use absolute `/home/zaks/...` paths.
- Every FAIL requires fix-forward plus gate re-run evidence.
- Every BLOCKED gate requires explicit prerequisite and risk note.
- Final PASS requires successful reboot persistence verification.

---

## Anti-Pattern Examples

### WRONG: Count a gate PASS because the file exists
```text
"config.toml exists" -> PASS, without proving Codex can parse it.
```

### RIGHT: Require runtime parse proof
```text
Run `codex mcp list --json` and confirm exit 0 with valid JSON output.
```

### WRONG: Treat MCP registration and connectivity as one status
```text
"MCP PASS" while server is listed but auth/runtime is broken.
```

### RIGHT: Split MCP status into two gates
```text
Configured PASS only after `codex mcp list/get` checks.
Connectivity PASS only after one real tool call per server.
```

### WRONG: Allow `CODEX_FORCE=1` without audit metadata
```text
Force bypass used with no reason or user attribution.
```

### RIGHT: Enforce strict force-bypass logging
```text
Require reason, actor, timestamp, cwd, and command in immutable log line.
```

---

## Pre-Flight (PF-1..11)

Use this evidence root:
```bash
export QA_ROOT="/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001"
export EVIDENCE="$QA_ROOT/evidence"
mkdir -p "$EVIDENCE"/{preflight,vf-01,vf-02,vf-03,vf-04,vf-05,vf-06,vf-07,xc,st,final}
{
  echo "qa_root=$QA_ROOT"
  echo "evidence_root=$EVIDENCE"
} | tee "/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001/evidence/preflight/PF-0-evidence-root.txt"
```

### PF-1: Baseline artifact presence
```bash
{
  echo "=== PF-1 artifact presence ==="
  ls -la /home/zaks/bookkeeping/missions/codex-align-001-artifacts
  ls -la /home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports
} | tee "$EVIDENCE/preflight/PF-1-artifacts.txt"
```

### PF-2: Codex config parser baseline
```bash
{
  echo "=== PF-2 codex parser baseline ==="
  /home/zaks/.npm-global/bin/codex mcp list --json
} | tee "$EVIDENCE/preflight/PF-2-codex-parser.txt"
```

### PF-3: Config ownership and permissions
```bash
{
  echo "=== PF-3 config permissions ==="
  stat -c '%U:%G %a %n' /home/zaks/.codex/config.toml
  ls -ld /home/zaks /home/zaks/.codex
} | tee "$EVIDENCE/preflight/PF-3-config-perms.txt"
```

### PF-4: Config schema hotspot (history.persistence)
```bash
{
  echo "=== PF-4 history.persistence ==="
  nl -ba /home/zaks/.codex/config.toml | sed -n '65,85p'
} | tee "$EVIDENCE/preflight/PF-4-history-persistence.txt"
```

### PF-5: Skill schema validity scan
```bash
{
  echo "=== PF-5 skill schema scan ==="
  find /home/zaks/.codex/skills -maxdepth 4 -type f -name 'SKILL.md' | sort | while read -r f; do
    H1=$(sed -n '1p' "$f")
    NAME=$(sed -n '1,20p' "$f" | grep -c '^name:' || true)
    DESC=$(sed -n '1,20p' "$f" | grep -c '^description:' || true)
    if [ "$H1" = "---" ] && [ "$NAME" -ge 1 ] && [ "$DESC" -ge 1 ]; then
      echo "PASS $f"
    else
      echo "FAIL $f"
    fi
  done
} | tee "$EVIDENCE/preflight/PF-5-skill-schema.txt"
```

### PF-6: Wrapper and shell integration baseline
```bash
{
  echo "=== PF-6 wrapper and shell baseline ==="
  nl -ba /home/zaks/scripts/codex-wrapper.sh | sed -n '1,120p'
  rg -n 'codex-safe|npm-global|codex-wrapper|CODEX_FORCE' /home/zaks/.bashrc /home/zaks/scripts/codex-wrapper.sh
} | tee "$EVIDENCE/preflight/PF-6-wrapper-shell.txt"
```

### PF-7: codex-safe runtime baseline (new interactive shell)
```bash
{
  echo "=== PF-7 codex-safe baseline ==="
  bash -ic 'type codex-safe; codex-safe --version'
} | tee "$EVIDENCE/preflight/PF-7-codex-safe-baseline.txt"
```

### PF-8: MCP runtime baseline
```bash
{
  echo "=== PF-8 mcp baseline ==="
  /home/zaks/.npm-global/bin/codex mcp list --json
} | tee "$EVIDENCE/preflight/PF-8-mcp-baseline.txt"
```

### PF-9: Claude MCP source-of-truth baseline
```bash
{
  echo "=== PF-9 claude mcp source baseline ==="
  nl -ba /home/zaks/.claude/settings.json | sed -n '24,60p'
  nl -ba /home/zaks/.claude/settings.local.json | sed -n '54,72p'
} | tee "$EVIDENCE/preflight/PF-9-claude-source.txt"
```

### PF-10: Regressions vs prior final-verification report
```bash
{
  echo "=== PF-10 report-vs-runtime baseline ==="
  nl -ba /home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/final-verification.md | sed -n '1,120p'
} | tee "$EVIDENCE/preflight/PF-10-report-vs-runtime.txt"
```

### PF-11: No-regression baseline (`make validate-local`)
```bash
{
  echo "=== PF-11 validate-local baseline ==="
  cd /home/zaks/zakops-agent-api
  make validate-local
} | tee "$EVIDENCE/preflight/PF-11-validate-local-baseline.txt"
```

---

## Verification Family 01 - Config Parser and Permission Integrity

### VF-01.1: Codex config parses cleanly
```bash
/home/zaks/.npm-global/bin/codex mcp list --json | tee "$EVIDENCE/vf-01/VF-01.1-parse.txt"
```
PASS if exit 0 and valid JSON array output.

### VF-01.2: `history.persistence` uses supported enum
```bash
nl -ba /home/zaks/.codex/config.toml | sed -n '65,85p' | tee "$EVIDENCE/vf-01/VF-01.2-history-enum.txt"
```
PASS if value is `save-all` or `none`.

### VF-01.3: Config read access under normal user shell
```bash
bash -ic '/home/zaks/.npm-global/bin/codex mcp list --json' | tee "$EVIDENCE/vf-01/VF-01.3-user-read.txt"
```
PASS if no "Permission denied".

### VF-01.4: Config ownership and mode policy
```bash
stat -c '%U:%G %a %n' /home/zaks/.codex/config.toml | tee "$EVIDENCE/vf-01/VF-01.4-config-mode.txt"
```
PASS if owned by `zaks:zaks` and mode is secure but readable by user process.

### VF-01.5: Remediation and re-verify (if any VF-01 gate fails)
Required remediation path:
1. fix invalid enum values
2. fix ownership/mode only as needed
3. re-run VF-01.1 to VF-01.4

Capture remediation diff and reruns:
```bash
{
  echo "=== VF-01 remediation rerun ==="
  git -C /home/zaks diff -- /home/zaks/.codex/config.toml
  /home/zaks/.npm-global/bin/codex mcp list --json
} | tee "$EVIDENCE/vf-01/VF-01.5-remediation-rerun.txt"
```

---

## Verification Family 02 - Skill Schema and Load Integrity

### VF-02.1: All `SKILL.md` files pass frontmatter schema check
```bash
find /home/zaks/.codex/skills -maxdepth 4 -type f -name 'SKILL.md' | sort | while read -r f; do
  H1=$(sed -n '1p' "$f")
  NAME=$(sed -n '1,20p' "$f" | grep -c '^name:' || true)
  DESC=$(sed -n '1,20p' "$f" | grep -c '^description:' || true)
  if [ "$H1" = "---" ] && [ "$NAME" -ge 1 ] && [ "$DESC" -ge 1 ]; then
    echo "PASS $f"
  else
    echo "FAIL $f"
  fi
done | tee "$EVIDENCE/vf-02/VF-02.1-skill-schema.txt"
```
PASS if zero `FAIL` lines.

### VF-02.2: Codex starts without "invalid SKILL.md" warnings
```bash
bash -ic '/home/zaks/.npm-global/bin/codex mcp list --json' 2>&1 | tee "$EVIDENCE/vf-02/VF-02.2-codex-skill-warnings.txt"
```
PASS if output does not contain `invalid SKILL.md` or `Skipped loading` warnings.

### VF-02.3: Skill discovery smoke test
```bash
/home/zaks/.npm-global/bin/codex exec "List available skills and include run-gates, project-context, before-task if present." 2>&1 | tee "$EVIDENCE/vf-02/VF-02.3-skill-discovery.txt"
```
PASS if expected skills are discoverable.

### VF-02.4: Project skill set integrity (7 required)
```bash
find /home/zaks/zakops-agent-api/.agents/skills -maxdepth 3 -type f -name 'SKILL.md' | sort | tee "$EVIDENCE/vf-02/VF-02.4-project-skills.txt"
```
PASS if exactly 7 project skill files exist and each has valid frontmatter.

### VF-02.5: Remediation and re-verify (if any VF-02 gate fails)
Add/repair frontmatter in invalid skills, then re-run VF-02.1 through VF-02.4.

---

## Verification Family 03 - MCP Registry, Auth, and Connectivity

### VF-03.1: Clarify source-of-truth assumptions
```bash
{
  echo "settings.json mcpServers:";
  rg -n 'mcpServers|github|playwright|gmail|crawl4ai' /home/zaks/.claude/settings.json;
  echo "settings.local.json is permission allow-list, not mcp server registry:";
  rg -n 'mcp__|mcpServers' /home/zaks/.claude/settings.local.json;
} | tee "$EVIDENCE/vf-03/VF-03.1-source-of-truth.txt"
```
PASS if documentation/reporting reflects this distinction.

### VF-03.2: Codex MCP configured-state verification
```bash
/home/zaks/.npm-global/bin/codex mcp list --json | tee "$EVIDENCE/vf-03/VF-03.2-mcp-list.txt"
```
PASS if target server set is present in configured state.

### VF-03.3: Per-server config contract inspection
```bash
for s in github playwright gmail crawl4ai-rag; do
  echo "=== $s ===";
  /home/zaks/.npm-global/bin/codex mcp get "$s" --json;
done | tee "$EVIDENCE/vf-03/VF-03.3-mcp-get.txt"
```
PASS if commands and args are valid and use user-owned binary paths where applicable.

### VF-03.4: User-owned binary policy
```bash
{
  command -v codex;
  command -v playwright-mcp;
  ls -l /home/zaks/.npm-global/bin/codex /home/zaks/.npm-global/bin/playwright-mcp 2>/dev/null || true;
} | tee "$EVIDENCE/vf-03/VF-03.4-user-binary-policy.txt"
```
PASS if mission execution paths are user-owned, not root-coupled.

### VF-03.5: GitHub auth contract verification
```bash
{
  env | rg '^GITHUB_(PERSONAL_ACCESS_TOKEN|TOKEN)=' || true;
  rg -n 'GITHUB_PERSONAL_ACCESS_TOKEN|GITHUB_TOKEN' /home/zaks/.codex/config.toml /home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/mcp-verification.md || true;
} | tee "$EVIDENCE/vf-03/VF-03.5-github-auth-contract.txt"
```
PASS if token handling is documented correctly and token value is not stored in plaintext config.

### VF-03.6: Connectivity smoke - GitHub MCP
```bash
/home/zaks/.npm-global/bin/codex exec "Use GitHub MCP to search repositories for 'openai/codex' and print first result URL only." 2>&1 | tee "$EVIDENCE/vf-03/VF-03.6-github-connectivity.txt"
```
PASS if call returns repository data; BLOCKED only with explicit auth prerequisite.

### VF-03.7: Connectivity smoke - Playwright MCP
```bash
/home/zaks/.npm-global/bin/codex exec "Use Playwright MCP to open https://example.com and return the page title." 2>&1 | tee "$EVIDENCE/vf-03/VF-03.7-playwright-connectivity.txt"
```
PASS if title retrieval succeeds.

### VF-03.8: Connectivity smoke - Gmail and crawl4ai-rag
```bash
{
  /home/zaks/.npm-global/bin/codex exec "Use Gmail MCP to search recent emails and return one subject line.";
  /home/zaks/.npm-global/bin/codex exec "Use crawl4ai-rag MCP to list available sources.";
} 2>&1 | tee "$EVIDENCE/vf-03/VF-03.8-gmail-crawl4ai-connectivity.txt"
```
PASS if functional; BLOCKED allowed only with explicit unmet prerequisite and no misconfiguration.

### VF-03.9: Configured vs connectivity pass criteria split
Produce explicit matrix in evidence:
- `configured_status`: PASS/FAIL
- `connectivity_status`: PASS/BLOCKED/FAIL

Evidence file:
`$EVIDENCE/vf-03/VF-03.9-status-matrix.md`

---

## Verification Family 04 - Wrapper Lifecycle and `CODEX_FORCE` Governance

### VF-04.1: Wrapper binary path policy
```bash
nl -ba /home/zaks/scripts/codex-wrapper.sh | sed -n '1,80p' | tee "$EVIDENCE/vf-04/VF-04.1-wrapper-path.txt"
```
PASS if wrapper uses user-owned Codex path.

### VF-04.2: `CODEX_FORCE` strict audit requirements
```bash
{
  rg -n 'CODEX_FORCE|FORCE_OVERRIDE|reason|SESSION_START|SESSION_END' /home/zaks/scripts/codex-wrapper.sh /home/zaks/bookkeeping/logs/codex-events.log || true;
} | tee "$EVIDENCE/vf-04/VF-04.2-force-audit.txt"
```
PASS if force usage requires reason and logs user/timestamp/cwd/command.

### VF-04.3: Boot diagnostics behavior under user context
```bash
bash -ic 'codex-safe --version' 2>&1 | tee "$EVIDENCE/vf-04/VF-04.3-codex-safe-user.txt"
```
PASS if no false HALT from inaccessible root-only paths.

### VF-04.4: Health-log write path safety
```bash
stat -c '%U:%G %a %n' /home/zaks/bookkeeping/health-log.md | tee "$EVIDENCE/vf-04/VF-04.4-health-log-perms.txt"
```
PASS if write behavior matches user runtime or script uses safe writable log path.

### VF-04.5: Wrapper exit-code fidelity
```bash
bash -ic 'codex-safe --version; echo wrapper_exit=$?' 2>&1 | tee "$EVIDENCE/vf-04/VF-04.5-wrapper-exit-fidelity.txt"
```
PASS if wrapper propagates Codex exit code semantics correctly.

---

## Verification Family 05 - Shell Integration and Path Hygiene

### VF-05.1: `.bashrc` duplicate PATH entry check
```bash
rg -n 'npm-global/bin|codex-safe' /home/zaks/.bashrc | tee "$EVIDENCE/vf-05/VF-05.1-bashrc-paths.txt"
```
PASS if no duplicate conflicting entries.

### VF-05.2: New interactive shell resolution
```bash
bash -ic 'command -v codex; type codex-safe' 2>&1 | tee "$EVIDENCE/vf-05/VF-05.2-shell-resolution.txt"
```
PASS if both resolve correctly.

### VF-05.3: Non-interactive shell safety
```bash
bash -lc 'command -v codex' 2>&1 | tee "$EVIDENCE/vf-05/VF-05.3-noninteractive-resolution.txt"
```
PASS if codex binary resolves without requiring alias expansion.

### VF-05.4: Mission command-path compliance
```bash
rg -n '/root/.npm-global/bin|/home/zaks/.npm-global/bin' /home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md /home/zaks/bookkeeping/missions/CODEX-ALIGN-001-CODEX-CLI-ALIGNMENT.md | tee "$EVIDENCE/vf-05/VF-05.4-command-path-compliance.txt"
```
PASS if remediation aligns active runtime to user-owned binary policy.

---

## Verification Family 06 - Session Restart Durability

### VF-06.1: Repeated Codex startup without warnings
```bash
for i in 1 2 3; do
  echo "RUN $i";
  bash -ic '/home/zaks/.npm-global/bin/codex mcp list --json';
done 2>&1 | tee "$EVIDENCE/vf-06/VF-06.1-repeated-startup.txt"
```
PASS if no recurring parse/skill warnings.

### VF-06.2: Repeated codex-safe runs
```bash
for i in 1 2; do
  echo "SAFE RUN $i";
  bash -ic 'codex-safe --version';
done 2>&1 | tee "$EVIDENCE/vf-06/VF-06.2-repeated-codex-safe.txt"
```
PASS if stable and non-halting in normal mode.

### VF-06.3: Log integrity across restarts
```bash
tail -n 80 /home/zaks/bookkeeping/logs/codex-events.log | tee "$EVIDENCE/vf-06/VF-06.3-events-log.txt"
```
PASS if session start/end and force events are coherent and attributable.

### VF-06.4: No-regression validation after session restart checks
```bash
cd /home/zaks/zakops-agent-api && make validate-local | tee "$EVIDENCE/vf-06/VF-06.4-validate-local-post-restart.txt"
```
PASS if gate remains healthy.

---

## Verification Family 07 - Reboot Durability (Required)

### VF-07.1: Pre-reboot snapshot
```bash
{
  date -u '+%Y-%m-%dT%H:%M:%SZ';
  /home/zaks/.npm-global/bin/codex mcp list --json;
  stat -c '%Y %U:%G %a %n' /home/zaks/.codex/config.toml /home/zaks/.bashrc /home/zaks/scripts/codex-wrapper.sh;
} | tee "$EVIDENCE/vf-07/VF-07.1-pre-reboot.txt"
```

### VF-07.2: Controlled reboot
```bash
echo "Execute controlled reboot now: sudo reboot"
```
Capture operator acknowledgement in:
`$EVIDENCE/vf-07/VF-07.2-reboot-ack.txt`

### VF-07.3: Post-reboot verification
```bash
{
  date -u '+%Y-%m-%dT%H:%M:%SZ';
  bash -ic '/home/zaks/.npm-global/bin/codex mcp list --json';
  bash -ic 'type codex-safe; codex-safe --version';
  stat -c '%Y %U:%G %a %n' /home/zaks/.codex/config.toml /home/zaks/.bashrc /home/zaks/scripts/codex-wrapper.sh;
} | tee "$EVIDENCE/vf-07/VF-07.3-post-reboot.txt"
```
PASS if equivalent behavior/state survives reboot.

### VF-07.4: Post-reboot MCP connectivity re-smoke
Re-run VF-03.6 to VF-03.8 and write outputs to:
- `$EVIDENCE/vf-07/VF-07.4-post-reboot-github.txt`
- `$EVIDENCE/vf-07/VF-07.4-post-reboot-playwright.txt`
- `$EVIDENCE/vf-07/VF-07.4-post-reboot-gmail-crawl4ai.txt`

PASS if pre-reboot connectivity state is preserved or blocked reasons remain unchanged and valid.

---

## Cross-Consistency (XC-1..4)

### XC-1: Prior final-verification claims vs current runtime
PASS if no contradiction remains unresolved between:
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/final-verification.md`
- live rerun evidence in this QA mission.

### XC-2: MCP verification report vs actual source/auth contracts
PASS if prerequisites and source-of-truth statements in
`/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/mcp-verification.md`
are corrected to match runtime reality.

### XC-3: Filesystem state vs runtime state
PASS if file-level checks (config, skills, wrappers, bashrc) and runtime outcomes agree.

### XC-4: Security consistency
PASS if secret scan is clean across:
- `/home/zaks/.codex/config.toml`
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/`
- `/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001/`

---

## Stress Tests (ST-1..4)

### ST-1: Profile switching stress
Run `codex` with `builder`, `review`, `forensic` profiles in separate shells.
PASS if profile-specific sandbox behavior loads without parser/warning regressions.

### ST-2: Force bypass governance stress
Attempt force run with and without reason metadata.
PASS if no-reason force is rejected and reasoned force is fully audited.

### ST-3: MCP partial outage resilience
Stop a dependent service (for crawl4ai or gmail auth unavailable) and verify status classification remains `configured=PASS`, `connectivity=BLOCKED` with explicit prerequisite.

### ST-4: Reboot edge-case replay
After reboot, run a second post-reboot shell session and repeat key checks to ensure no first-login-only behavior.

---

## Remediation Protocol
1. Classify each failing gate as `P0` (execution blocker), `P1` (high risk), `P2` (medium), `P3` (low).
2. Apply minimal in-scope fix only.
3. Re-run failed gate immediately.
4. Re-run dependent XC checks.
5. Update scorecard and remediation log with:
- gate id
- root cause
- file(s) changed
- re-run evidence path
- final status

Mandatory P0 in this mission:
- config parser failure
- codex-safe unusable in normal user flow
- unresolved reboot durability

---

## Enhancement Opportunities
1. Add automated skill frontmatter lint script under `/home/zaks/bookkeeping/scripts/`.
2. Add config schema lint preflight for `~/.codex/config.toml`.
3. Add wrapper self-test mode (`--self-test`) for non-interactive verification.
4. Add MCP status matrix generator script for configured/connectivity split.
5. Add reboot verification helper script with pre/post snapshots.
6. Add dedicated Codex health log file independent of Claude health log ownership.

---

## Scorecard Template

| Gate | Description | Status (PASS/FAIL/BLOCKED) | Evidence | Remediation Applied | Re-run Status |
|------|-------------|----------------------------|----------|---------------------|---------------|
| PF-1 | Artifact presence |  |  |  |  |
| PF-2 | Codex parser baseline |  |  |  |  |
| PF-3 | Config permissions |  |  |  |  |
| PF-4 | History enum check |  |  |  |  |
| PF-5 | Skill schema scan |  |  |  |  |
| PF-6 | Wrapper/shell baseline |  |  |  |  |
| PF-7 | codex-safe baseline |  |  |  |  |
| PF-8 | MCP baseline |  |  |  |  |
| PF-9 | Claude source baseline |  |  |  |  |
| PF-10 | Report-vs-runtime baseline |  |  |  |  |
| PF-11 | validate-local baseline |  |  |  |  |
| VF-01 | Config parser/perms |  |  |  |  |
| VF-02 | Skill schema/load |  |  |  |  |
| VF-03 | MCP source/auth/connectivity |  |  |  |  |
| VF-04 | Wrapper + CODEX_FORCE governance |  |  |  |  |
| VF-05 | Shell/path hygiene |  |  |  |  |
| VF-06 | Session restart durability |  |  |  |  |
| VF-07 | Reboot durability |  |  |  |  |
| XC-1 | Report consistency |  |  |  |  |
| XC-2 | MCP consistency |  |  |  |  |
| XC-3 | FS vs runtime consistency |  |  |  |  |
| XC-4 | Security consistency |  |  |  |  |
| ST-1 | Profile switching stress |  |  |  |  |
| ST-2 | Force bypass stress |  |  |  |  |
| ST-3 | MCP outage classification stress |  |  |  |  |
| ST-4 | Post-reboot replay stress |  |  |  |  |

---

## Guardrails
1. Do not expose or print secret values; redact all tokens in evidence.
2. Do not declare PASS without command output evidence.
3. Any remediation must stay inside Codex alignment scope and related bookkeeping.
4. Keep all QA evidence under `/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001/`.
5. Maintain absolute path discipline in all commands and reports.
6. Use user-owned binaries for Codex execution paths unless explicitly justified.
7. Treat reboot verification as required, not optional, for final PASS.
8. Re-run `make validate-local` after remediation phases that touch scripts/config used by development workflow.

---

## File Paths Reference

### Files to Modify (as needed by remediation)
- `/home/zaks/.codex/config.toml`
- `/home/zaks/.bashrc`
- `/home/zaks/scripts/codex-wrapper.sh`
- `/home/zaks/scripts/codex-boot.sh`
- `/home/zaks/scripts/codex-stop.sh`
- `/home/zaks/.codex/skills/*/SKILL.md`
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/final-verification.md`
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/mcp-verification.md`
- `/home/zaks/bookkeeping/CHANGES.md`
- `/root/.claude/projects/-home-zaks/memory/MEMORY.md`

### Files to Create
- `/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001/`
- `/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001/evidence/`
- `/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001/SCORECARD.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-CODEX-ALIGN-VERIFY-001/FINAL-REPORT.md`

### Files to Read
- `/home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md`
- `/home/zaks/bookkeeping/missions/CODEX-ALIGN-001-CODEX-CLI-ALIGNMENT.md`
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/final-verification.md`
- `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/mcp-verification.md`
- `/home/zaks/.claude/settings.json`
- `/home/zaks/.claude/settings.local.json`

---

## Stop Condition
Stop only when all required PF, VF, XC, and ST gates are PASS, or are explicitly BLOCKED with valid prerequisites and zero unremediated P0 items.

Final PASS requires:
1. parser/permission/skill warnings resolved,
2. MCP configured vs connectivity states correctly split and evidenced,
3. strict `CODEX_FORCE` audit controls enforced,
4. session restart and full reboot durability evidence complete,
5. `make validate-local` no-regression gate green,
6. scorecard and final report completed with evidence references.

---

*End of Mission Prompt - QA-CODEX-ALIGN-VERIFY-001*
