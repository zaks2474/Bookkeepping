# MISSION: INFRA-TRUTH-REPAIR-001
## Frontend Infrastructure Truth Repair — Track 1 + Track 2 + Manifest Hardening
## Date: 2026-02-10
## Classification: Infrastructure Remediation
## Prerequisite: SURFACE-REMEDIATION-002 and QA-SR-VERIFY-001 complete
## Successor: MISSION-SURFACES-10-14-REGISTER-001 (blocked until this mission passes)

---

## Preamble: Builder Environment Acknowledgment

This mission assumes the builder auto-loads `/home/zaks/zakops-agent-api/CLAUDE.md`, canonical memory at `/root/.claude/projects/-home-zaks/memory/MEMORY.md`, hooks, deny rules, and path-scoped rules. This prompt references those systems and only specifies mission-specific work.

---

## 1. Mission Objective

This mission repairs infrastructure truth and enforcement consistency before any expansion to Surfaces 10–14. It executes only the high-confidence path: Track 1 quick fixes, Track 2 validation wiring correction, and hardening of `infra-snapshot` so it cannot report success on failed generation.

This is a **repair and alignment mission**, not a net-new surface build mission. Surfaces 10–14 are explicitly out of scope for implementation in this mission. Their registration remains blocked until this mission proves the existing 9-surface system is coherent, enforceable, and self-consistent.

Source materials:
- `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md`
- `/home/zaks/bookkeeping/docs/QA-SR-VERIFY-001-SCORECARD.md`
- `/home/zaks/bookkeeping/docs/FORENSIC-AUDIT-RESULTS-FORENSIC-AUDIT-SURFACES-002`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`

---

## 2. Context

Current-state findings verified against live filesystem:

1. Agent skill preloads are broken by `~/` resolution in active agent files.
- `/home/zaks/.claude/agents/arch-reviewer.md`
- `/home/zaks/.claude/agents/contract-guardian.md`
- `/home/zaks/.claude/agents/test-engineer.md`

2. Agent file ownership is inconsistent.
- `/home/zaks/.claude/agents/arch-reviewer.md` is `root:root`
- Other agent files are `zaks:zaks`

3. Validation claims and enforcement are inconsistent across artifacts.
- `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` states 9 surfaces
- `/home/zaks/zakops-agent-api/CLAUDE.md` states 9 surfaces
- `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` says 7
- `/home/zaks/zakops-agent-api/Makefile` target description says 7
- `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` exists but is not wired into `validate-full` / `validate-local`

4. `infra-snapshot` currently allows false success.
- `/home/zaks/zakops-agent-api/Makefile` `infra-snapshot` target prints success even when generator errors
- `/home/zaks/tools/infra/generate-manifest.sh` can fail with permission issues while Makefile still exits success
- Current manifest shows stale/incorrect section values:
  - `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md`

5. `frontend-design` skill exists only in marketplace clone and is inert for local active skills.
- Source: `/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`
- Missing in active local skill directory: `/home/zaks/.claude/skills/`

6. Playwright MCP is present but disabled in user settings.
- `/home/zaks/.claude/settings.json`
- This mission does not force-enable it unless explicitly needed to satisfy acceptance criteria.

### Environment drift since earlier reports

- Completed missions include SURFACE-REMEDIATION-001 and SURFACE-REMEDIATION-002 in canonical memory.
- Root-level permission bypass (`dangerouslySkipPermissions: true`) remains active; hook enforcement is operationally critical.

### Must-not-regress deliverables

- `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
- `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh`
- `/home/zaks/.claude/hooks/session-start.sh`
- `/home/zaks/.claude/hooks/stop.sh`
- `/home/zaks/bookkeeping/docs/QA-SR-VERIFY-001-SCORECARD.md`

---

## Crash Recovery Protocol <!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash/interruption, run exactly:

```bash
cd /home/zaks/zakops-agent-api && git log --oneline -5
cd /home/zaks/zakops-agent-api && make validate-local
find /home/zaks/bookkeeping/docs -maxdepth 1 -type f -name "INFRA-TRUTH-REPAIR-001-*" -o -name "MISSION-INFRA-TRUTH-REPAIR-001*"
```

If baseline validation fails during recovery, do not continue to later phases. Re-establish baseline first and record failure cause in the checkpoint file.

---

## Continuation Protocol <!-- Adopted from Improvement Area IA-7 -->

At end of each session, update:
- `/home/zaks/bookkeeping/mission-checkpoints/INFRA-TRUTH-REPAIR-001.md`

Checkpoint minimum content:
1. Completed phases
2. Remaining phases
3. Current validation status (`make validate-local`, `make validate-full`)
4. Open decisions/blockers
5. Exact next command to run

---

## Context Checkpoint <!-- Adopted from Improvement Area IA-1 -->

If context becomes constrained mid-mission:
1. Write current status to `/home/zaks/bookkeeping/mission-checkpoints/INFRA-TRUTH-REPAIR-001.md`
2. Commit logically complete intermediate work
3. Restart from checkpoint using Crash Recovery Protocol

---

## 2b. Glossary

| Term | Definition |
|------|-----------|
| Truth repair | Aligning declared counts and enforcement behavior with actual runtime behavior and generated artifacts |
| Surface validator | `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` contract check script |
| Surface 9 validator | `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` dashboard convention check |
| Manifest false-green | `make infra-snapshot` reporting success when generator failed |
| Active skill | A skill present under `/home/zaks/.claude/skills/<name>/SKILL.md` and referenceable by active commands/agents |
| Count reconciliation | Ensuring contract surface totals match across rule doc, CLAUDE guide, validator, and manifest |

---

## 3. Architectural Constraints

- **Existing 9-surface model remains authoritative**
Meaning: No redesign of surfaces 1–9 in this mission.
Why: This mission is wiring and truth repair, not architecture replacement.

- **No Surfaces 10–14 implementation in this mission**
Meaning: Do not register or enforce new surfaces yet.
Why: Baseline 9-surface enforcement must be trustworthy first.

- **Contract-surface discipline remains mandatory**
Meaning: No direct edits to generated files; use sync/validation pipelines only.
Why: Generated artifacts are protected and drift-prone.

- **Surface 9 conventions preserved**
Meaning: Keep existing design-system enforcement patterns and validator behavior.
Why: Prior remediation and QA already rely on this contract.

- **Hook-first safety model must remain intact**
Meaning: Do not weaken pre-edit, pre-bash, session-start, stop, or memory-sync behavior.
Why: Root permission bypass makes hook enforcement primary.

- **No application feature work**
Meaning: No dashboard/backend feature additions, endpoint changes, or schema redesign.
Why: Reduces blast radius and prevents mixed-objective mission failure.

- **Port 8090 remains forbidden**
Meaning: Do not introduce any new active reference to 8090.
Why: Decommissioned and historically high-risk.

- **WSL safety remains mandatory**
Meaning: LF line endings and ownership sanity for modified files under `/home/zaks/`.
Why: Prevent delayed execution failures.

- **Reference docs in bookkeeping are inputs, not rewrite targets**
Meaning: Do not rewrite cross-service reference documents in this mission.
Why: This mission repairs enforcement infrastructure, not content authoring.

---

## 3b. Anti-Pattern Examples

### WRONG: Agent skill preload path using home shortcut
```markdown
- ~/.claude/skills/api-conventions
```

### RIGHT: Absolute path to active skill directory
```markdown
- /home/zaks/.claude/skills/api-conventions
```

### WRONG: `infra-snapshot` prints success after generator failure
```bash
bash /home/zaks/tools/infra/generate-manifest.sh
echo "Manifest generated"
```

### RIGHT: Fail-fast snapshot gate
```bash
bash /home/zaks/tools/infra/generate-manifest.sh || exit 1
test -s /home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md
```

### WRONG: 9-surface architecture with 7-surface validator claim
```bash
# Validates all 7 contract surfaces
```

### RIGHT: Validator and wiring reflect actual scope
```bash
# Validates all 9 contract surfaces
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Validator text/counts updated, but execution path still omits Surface 9 | HIGH | False confidence; drift persists | Phase 2 gate requires command output proving all 9 checks run |
| 2 | Manifest generator partially fixed but Makefile still reports success on failure | HIGH | Persistent false-green automation | Phase 3 includes failure-path test and non-zero enforcement |
| 3 | Agent skill path fixed in one file only | MEDIUM | Partial agent degradation remains | Phase 1 grep sweep over all `.claude` config files |
| 4 | Stop hook timeout breaks after validation expansion | MEDIUM | Session-end blocks or noisy failures | Phase 2 requires stop-hook timing check and timeout recalibration |
| 5 | Mission leaks into Surfaces 10–14 build work | MEDIUM | Scope blowout, delayed completion | Guardrails + Phase gates explicitly fence scope |

---

## 4. Phases

## Phase 0 — Discovery & Baseline
**Complexity:** S  
**Estimated touch points:** 0 files modified

**Purpose:** Re-validate all critical findings against current state before edits.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Capture baseline state evidence**
  - Evidence file: `/home/zaks/bookkeeping/docs/INFRA-TRUTH-REPAIR-001-BASELINE.md`
  - Capture outputs for:
    - agent ownership + skill preload path checks
    - surface count reconciliation checks
    - `make infra-snapshot` behavior (including error output)
  - **Checkpoint:** Baseline file exists and includes timestamps.

- P0-02: **Run baseline validation gates**
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api && bash /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
  - `cd /home/zaks/zakops-agent-api && bash /home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh`
  - **Checkpoint:** Record pass/fail per command in baseline file.

### Decision Tree
- **IF** baseline validation fails before edits → stop and classify as pre-existing breakage.
- **ELSE** proceed to Phase 1.

### Rollback Plan
1. No code rollback required (read-only phase).
2. Verify no files changed via `cd /home/zaks/zakops-agent-api && git status --short`.

### Gate P0
- Baseline evidence file exists with command outputs.
- Pre-edit validation status documented.

---

## Phase 1 — Track 1 Quick Fixes
**Complexity:** M  
**Estimated touch points:** 5–8 files

**Purpose:** Repair immediately broken agent/skill runtime wiring.

### Blast Radius
- **Services affected:** Claude Code runtime config only
- **Pages affected:** None
- **Downstream consumers:** Agent delegation workflows, command skill references

### Tasks
- P1-01: **Fix agent skill preload absolute paths**
  - Modify:
    - `/home/zaks/.claude/agents/arch-reviewer.md`
    - `/home/zaks/.claude/agents/contract-guardian.md`
    - `/home/zaks/.claude/agents/test-engineer.md`
  - Replace active preload references from `~/.claude/skills/...` to `/home/zaks/.claude/skills/...`
  - **Checkpoint:** No remaining `~/.claude/skills` in these files.

- P1-02: **Fix ownership inconsistency for agent definitions**
  - Ensure modified agent files are owned by `zaks:zaks`.
  - **Checkpoint:** `ls -la /home/zaks/.claude/agents` shows consistent ownership.

- P1-03: **Activate frontend-design skill by copy (not creation)**
  - Source:
    - `/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`
  - Destination:
    - `/home/zaks/.claude/skills/frontend-design/SKILL.md`
  - **Checkpoint:** destination exists and content matches source.

- P1-04: **Add skills inventory section to canonical memory**
  - Modify:
    - `/root/.claude/projects/-home-zaks/memory/MEMORY.md`
  - Add inventory of active local skills by name + purpose.
  - **Checkpoint:** inventory section present and includes `frontend-design`.

- P1-05: **Run `~/` path bug sweep in active `.claude` configs**
  - Sweep targets:
    - `/home/zaks/.claude/**/*.md`
    - `/home/zaks/.claude/**/*.sh`
    - `/home/zaks/.claude/**/*.json`
  - Fix only actionable runtime/config references.
  - Leave archival/changelog text untouched but documented.
  - **Checkpoint:** actionable `~/.claude/skills` references in active configs are zero.

### Decision Tree
- **IF** a `~/` hit is in active agent/command/hook config → fix to absolute path.
- **ELSE IF** hit is in archival/changelog/paste cache → document as inert.
- **ELSE** escalate for manual classification.

### Rollback Plan
1. Restore edited `.claude` files from immediate backups created before edit.
2. Remove `/home/zaks/.claude/skills/frontend-design/` if copied in error.
3. Re-run ownership checks and `git status`.
4. Verify `cd /home/zaks/zakops-agent-api && make validate-local` still passes.

### Gate P1
- All 3 agent files use absolute skill paths.
- `/home/zaks/.claude/skills/frontend-design/SKILL.md` exists.
- Agent file ownership is consistent.
- Skills inventory exists in canonical memory.

---

## Phase 2 — Track 2 Validation Wiring Integrity (9 Surfaces)
**Complexity:** L  
**Estimated touch points:** 4–7 files

**Purpose:** Make enforcement pipeline reflect declared 9-surface architecture.

### Blast Radius
- **Services affected:** Monorepo validation pipeline, stop-hook dependent validation flow
- **Pages affected:** None directly
- **Downstream consumers:** `/before-task`, stop hook, CI-safe validation commands

### Tasks
- P2-01: **Unify validator scope to 9 surfaces**
  - Modify:
    - `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
  - Ensure script checks S1–S9, including S8 and S9 by direct checks or delegated script calls.
  - Script output must name each surface check explicitly.
  - **Checkpoint:** running script prints checks for all 9 surfaces.

- P2-02: **Align Makefile target declarations and wiring**
  - Modify:
    - `/home/zaks/zakops-agent-api/Makefile`
  - Remove stale “all 7 surfaces” descriptors.
  - Ensure `validate-full` and `validate-local` execute full 9-surface validation path.
  - **Checkpoint:** `make validate-full` and `make validate-local` both include Surface 9 enforcement path.

- P2-03: **Reconcile pre-task and stop-hook expectations**
  - Modify as needed:
    - `/home/zaks/zakops-agent-api/.claude/commands/before-task.md`
    - `/home/zaks/.claude/hooks/stop.sh`
  - Keep stop-hook time budget realistic if expanded checks increase runtime.
  - **Checkpoint:** stop hook runs without timeout regression.

- P2-04: **Eliminate stale “7 surfaces” language in active enforcement docs**
  - Update active files where enforcement language is stale.
  - **Checkpoint:** no active runtime/validation file claims 7 when architecture says 9.

### Decision Tree
- **IF** S8/S9 checks materially increase runtime → adjust timeout budgets before enabling hard gate.
- **ELSE** keep existing timeout budgets.

### Rollback Plan
1. Revert validator and Makefile edits from phase-specific backup.
2. Restore stop-hook timeouts to prior values.
3. Re-run:
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api && make validate-full`

### Gate P2
- `validate-contract-surfaces.sh` enforces 9/9 surfaces.
- `make validate-local` and `make validate-full` pass.
- Stop hook behavior remains stable.
- No active “all 7 surfaces” mismatch remains.

---

## Phase 3 — `infra-snapshot` Hardening and Manifest Truth Repair
**Complexity:** XL  
**Estimated touch points:** 3–6 files

**Purpose:** Remove false-green snapshot behavior and make manifest output trustworthy.

### Blast Radius
- **Services affected:** Infrastructure reporting pipeline only
- **Pages affected:** None
- **Downstream consumers:** Infra checks, operational runbooks, audit artifacts

### Tasks
- P3-01: **Make snapshot target fail-fast on generator failure**
  - Modify:
    - `/home/zaks/zakops-agent-api/Makefile`
  - `infra-snapshot` must exit non-zero on generator error.
  - **Checkpoint:** injected generator failure produces non-zero make exit.

- P3-02: **Fix generator write-path and execution assumptions**
  - Modify:
    - `/home/zaks/tools/infra/generate-manifest.sh`
  - Ensure output path and working directory logic cannot silently fail from permission mismatch.
  - **Checkpoint:** no permission-denied output during normal run.

- P3-03: **Expand manifest surface section to real 9-surface model**
  - Modify:
    - `/home/zaks/tools/infra/generate-manifest.sh`
  - Surface block must include S1–S9 with correct artifact checks.
  - **Checkpoint:** generated manifest surface section has 9 entries.

- P3-04: **Fix generated file and config count reporting in manifest**
  - Ensure manifest reflects actual generated artifacts and actual rules/commands counts.
  - **Checkpoint:** no stale fixed values (for example `Rules: 0`, `Commands: 12`) when live values differ.

- P3-05: **Regenerate and verify manifest integrity**
  - Commands:
    - `cd /home/zaks/zakops-agent-api && make infra-snapshot`
  - **Checkpoint:** manifest updated timestamp and truthful content.

### Decision Tree
- **IF** generator depends on services currently down → mark service-dependent sections as explicit SKIP/UNAVAILABLE, not false NOT FOUND.
- **ELSE** populate full status details.

### Rollback Plan
1. Restore Makefile and generator script from phase backups.
2. Restore last known-good manifest snapshot copy.
3. Re-run `make validate-local`.

### Gate P3
- `make infra-snapshot` fails on generator errors.
- Successful run produces updated manifest without permission errors.
- Contract surface section reports 9 entries.
- Manifest does not report false NOT FOUND for files that exist.

---

## Phase 4 — Count Reconciliation and Boot-Diagnostics Extension
**Complexity:** M  
**Estimated touch points:** 3–5 files

**Purpose:** Ensure count truth is self-checked across all core artifacts.

### Blast Radius
- **Services affected:** Hook diagnostics + documentation integrity
- **Pages affected:** None
- **Downstream consumers:** Session diagnostics, infra checks, mission QA

### Tasks
- P4-01: **Reconcile count across 4 authoritative artifacts**
  - Reconcile:
    - `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`
    - `/home/zaks/zakops-agent-api/CLAUDE.md`
    - `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
    - `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md`
  - **Checkpoint:** all report 9 consistently.

- P4-02: **Extend boot CHECK 2 to include validator/manifest awareness**
  - Modify:
    - `/home/zaks/.claude/hooks/session-start.sh`
  - CHECK 2 should detect mismatch across declarative and enforcement artifacts, not only CLAUDE vs memory.
  - **Checkpoint:** mismatch scenario is detected as warning/failure per design.

- P4-03: **Update constraint registry if new check dependencies were introduced**
  - Review:
    - `/home/zaks/zakops-agent-api/.claude/CONSTRAINT_REGISTRY.md`
  - Add only constraints needed for new enforcement checks.
  - **Checkpoint:** registry and check logic remain coherent.

### Decision Tree
- **IF** extending CHECK 2 risks noisy false positives → emit WARN with remediation guidance.
- **ELSE** enforce FAIL for structural mismatches.

### Rollback Plan
1. Restore hook and registry files from backups.
2. Validate hooks still execute and no startup break occurs.
3. Re-run `make validate-local`.

### Gate P4
- 4-way count reconciliation table shows `9` everywhere.
- Boot diagnostics CHECK 2 validates reconciled sources.
- No hook startup regressions.

---

## Phase 5 — Final Verification, Evidence, and Handoff
**Complexity:** M  
**Estimated touch points:** 2–4 files

**Purpose:** Prove mission completion with evidence and lock scope boundary.

### Blast Radius
- **Services affected:** None (verification/reporting)
- **Pages affected:** None
- **Downstream consumers:** Next mission planning, QA verification mission

### Tasks
- P5-01: **Run final verification matrix**
  - Required commands:
    - `cd /home/zaks/zakops-agent-api && make validate-local`
    - `cd /home/zaks/zakops-agent-api && make validate-full`
    - `cd /home/zaks/zakops-agent-api && bash /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
    - `cd /home/zaks/zakops-agent-api && make infra-snapshot`
  - **Checkpoint:** all required gates pass.

- P5-02: **Produce completion report**
  - Create:
    - `/home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md`
  - Include before/after reconciliation table and evidence paths.
  - **Checkpoint:** report includes all acceptance criteria status.

- P5-03: **Update bookkeeping**
  - Update:
    - `/home/zaks/bookkeeping/CHANGES.md`
  - **Checkpoint:** entry added with mission ID and summary.

- P5-04: **Declare deferred scope for successor mission**
  - Add deferred section in completion report for Surfaces 10–14 implementation mission.
  - **Checkpoint:** successor mission remains blocked until this mission marked PASS.

### Decision Tree
- **IF** any final gate fails → do not mark mission complete; return to owning phase.
- **ELSE** finalize completion report and stop.

### Rollback Plan
1. Restore mission-phase edits from backups if final regression discovered.
2. Re-run full verification matrix.
3. Update completion report with rollback evidence.

### Gate P5
- All phase gates and final verification commands pass.
- Completion report exists with evidence links.
- CHANGES entry exists.

---

## 4b. Dependency Graph

Phases execute sequentially with one hard block:

```
Phase 0 (Discovery)
   |
   v
Phase 1 (Track 1 Quick Fixes)
   |
   v
Phase 2 (Track 2 Validation Wiring)
   |
   v
Phase 3 (Infra Snapshot Hardening)
   |
   v
Phase 4 (Count Reconciliation + Boot Check Extension)
   |
   v
Phase 5 (Final Verification + Handoff)
```

Blocking rule: do not start Phase 4 until Phase 3 gate passes (manifest truth repair is prerequisite for count reconciliation).

---

## 5. Acceptance Criteria

### AC-1: Agent Skill Path Integrity
All active agent preload paths resolve to existing files under `/home/zaks/.claude/skills/`.

### AC-2: Agent Ownership Integrity
Agent definition ownership is consistent and writable by `zaks` where required.

### AC-3: Frontend Skill Activation
`frontend-design` exists as an active local skill at `/home/zaks/.claude/skills/frontend-design/SKILL.md`.

### AC-4: 9-Surface Validator Integrity
`validate-contract-surfaces` enforces and reports all 9 surfaces.

### AC-5: Validation Pipeline Integrity
`make validate-local` and `make validate-full` include full intended surface checks and pass.

### AC-6: Snapshot Fail-Fast Integrity
`make infra-snapshot` returns non-zero on generation failure and zero only on successful generation.

### AC-7: Manifest Truth Integrity
Manifest contract surface section reflects 9 surfaces with truthful status; no false NOT FOUND for existing files.

### AC-8: Count Reconciliation Integrity
All four artifacts (rule doc, CLAUDE guide, validator, manifest) report consistent surface counts.

### AC-9: No Regressions
No regressions in existing validation gates or hook execution paths.

### AC-10: Bookkeeping
Completion report and CHANGES entry are present and complete.

---

## 6. Guardrails

1. Do not implement Surfaces 10–14 in this mission.
2. Do not modify application feature code unless required to restore validation truth wiring.
3. Do not edit generated files directly.
4. Do not alter migration histories.
5. Do not weaken hook enforcement semantics.
6. Do not rewrite bookkeeping reference documents as part of this mission scope.
7. Use absolute paths only in edits, commands, and reports.
8. Preserve Surface 9 conventions and existing dashboard design-system constraints.
9. Maintain WSL safety: LF endings and ownership sanity on modified shell/config files.
10. If uncertain on severity classification, prioritize truthful reporting over optimistic PASS claims.

---

## 7. Executor Self-Check Prompts

### After Phase 0
- [ ] Did I verify findings against live files instead of assuming audit text is still current?
- [ ] Did I capture baseline evidence before making edits?
- [ ] Did baseline validation pass before starting fixes?

### After Every Edit Batch
- [ ] Did I accidentally change scope into Surfaces 10–14 implementation?
- [ ] Did I keep paths absolute and ownership sane?
- [ ] Did I update only enforcement/wiring files, not unrelated feature code?

### Before Closing Each Phase
- [ ] Did I run this phase gate commands, not just inspect files?
- [ ] Did I record outputs in evidence artifacts?
- [ ] Did I verify no stale “7 surfaces” mismatch remains where relevant?

### Before Mission Complete
- [ ] Does `make validate-local` pass now?
- [ ] Does `make validate-full` pass now?
- [ ] Does `make infra-snapshot` behave fail-fast on error?
- [ ] Is the completion report fully populated with evidence paths?
- [ ] Is CHANGES updated?

---

## 8. File Paths Reference

### Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/.claude/agents/arch-reviewer.md` | 1 | Fix skill preload paths; ownership consistency |
| `/home/zaks/.claude/agents/contract-guardian.md` | 1 | Fix skill preload paths |
| `/home/zaks/.claude/agents/test-engineer.md` | 1 | Fix skill preload paths |
| `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | 1 | Add skills inventory section |
| `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` | 2 | Enforce/report all 9 surfaces |
| `/home/zaks/zakops-agent-api/Makefile` | 2,3 | Align validation wiring and harden `infra-snapshot` fail behavior |
| `/home/zaks/.claude/hooks/stop.sh` | 2 | Keep stop-hook validation timing coherent |
| `/home/zaks/zakops-agent-api/.claude/commands/before-task.md` | 2 | Align pre-task wording with 9-surface enforcement |
| `/home/zaks/tools/infra/generate-manifest.sh` | 3 | Fix write path + truthful 9-surface manifest generation |
| `/home/zaks/.claude/hooks/session-start.sh` | 4 | Extend count consistency diagnostics |
| `/home/zaks/zakops-agent-api/.claude/CONSTRAINT_REGISTRY.md` | 4 | Update only if new check dependencies require registry entries |
| `/home/zaks/bookkeeping/CHANGES.md` | 5 | Record mission completion summary |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/bookkeeping/docs/INFRA-TRUTH-REPAIR-001-BASELINE.md` | 0 | Baseline evidence and pre-edit state |
| `/home/zaks/bookkeeping/mission-checkpoints/INFRA-TRUTH-REPAIR-001.md` | 0-5 | Session continuity checkpoints |
| `/home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001-COMPLETION.md` | 5 | Final completion report with AC reconciliation |
| `/home/zaks/.claude/skills/frontend-design/SKILL.md` | 1 | Activate local frontend-design skill |

### Files to Read (Do Not Modify Unless Explicit Task Says So)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md` | Source findings and proposed tracks |
| `/home/zaks/bookkeeping/docs/QA-SR-VERIFY-001-SCORECARD.md` | Prior QA outcomes and known INFO gaps |
| `/home/zaks/bookkeeping/docs/FORENSIC-AUDIT-RESULTS-FORENSIC-AUDIT-SURFACES-002` | Ground truth context for future Surfaces 10–14 |
| `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` | 9-surface source of truth |
| `/home/zaks/zakops-agent-api/CLAUDE.md` | Session-level declared surface count and constraints |
| `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md` | Current manifest output to be repaired |
| `/home/zaks/.claude/settings.json` | User-level hook and MCP configuration state |

---

## 9. Stop Condition

Stop when all phase gates pass, all acceptance criteria AC-1 through AC-10 are satisfied, `make validate-local` and `make validate-full` both pass, `make infra-snapshot` is fail-fast and truthful, and completion artifacts are written.

Do not proceed to Surfaces 10–14 registration/build in this mission. The successor mission may begin only after this mission is marked complete with evidence-backed PASS.

---

*End of Mission Prompt — INFRA-TRUTH-REPAIR-001*
