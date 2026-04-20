# MISSION: FRONTEND-GOVERNANCE-HARDENING-001
## Frontend Governance Hardening with Stop Hook PATH Resilience
## Date: 2026-02-10
## Classification: Frontend Governance Remediation
## Prerequisite: /home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/SCORECARD.md reports FULL PASS
## Successor: QA-FGH-VERIFY-001 (unblock only on FULL PASS)

---

## Preamble: Builder Operating Context

The builder auto-loads `/home/zaks/zakops-agent-api/CLAUDE.md`, canonical memory at `/root/.claude/projects/-home-zaks/memory/MEMORY.md`, hooks, deny rules, and path-scoped rules. This mission references those systems and adds mission-specific remediation only.

---

## 1. Mission Objective

This mission closes the remaining frontend-governance backlog from `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md` while also hardening `stop.sh` Gate E so hook behavior does not depend on `rg` availability in hook PATH.

This is a governance and enforcement mission, not a product-feature mission. It upgrades rules, validation logic, and hook resilience. It does not redesign dashboard features, alter API behavior, or add database migrations.

Source material:
- `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/SCORECARD.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`
- `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
- `/home/zaks/.claude/hooks/stop.sh`

In-scope backlog (audit IDs):
- `INFO-2` from QA-S10-14: `rg` PATH dependency in `/home/zaks/.claude/hooks/stop.sh`
- `G8`: missing accessibility rule
- `G9`: missing component pattern rule
- `G10`: missing responsive breakpoint guidance
- `G11`: missing Category B content from frontend-design skill
- `G12`: missing z-index scale guidance
- `G13`: missing dark mode strategy guidance
- `G14`: missing animation performance guidance
- `G18`: missing state management pattern guidance

Out of scope:
- New dashboard feature implementation
- Runtime API contract changes
- New contract surfaces beyond 14
- Full Playwright infrastructure rollout (policy can be documented; deep rollout is separate)

---

## 2. Context

Current-state facts validated from filesystem and QA artifacts:

1. Surface system is now 14/14 and passing; this mission must not regress that baseline.
- `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`
- `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
- `/home/zaks/zakops-agent-api/CLAUDE.md`

2. `stop.sh` currently contains Gate E raw-httpx scanning with `rg` directly.
- `/home/zaks/.claude/hooks/stop.sh`
- QA INFO-2 indicates `rg` is not guaranteed in hook PATH context.

3. Frontend governance rule coverage is incomplete.
- Existing rules: `design-system.md`, `dashboard-types.md`
- Missing rules: `accessibility.md`, `component-patterns.md`
- Existing design-system Category B lacks several explicit governance points from frontend-design skill.

4. Surface 9 validator exists but currently checks only a narrow subset of governance integrity.
- `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh`
- It does not assert presence of additional governance rule files or enriched design-system sections.

5. Frontend-design skill exists locally and should be referenced explicitly from rule guidance.
- `/home/zaks/.claude/skills/frontend-design/SKILL.md`

---

## Crash Recovery Protocol <!-- Adopted from Improvement Area IA-2 -->

If resuming after crash/interruption, run exactly:

```bash
cd /home/zaks/zakops-agent-api && git log --oneline -5
cd /home/zaks/zakops-agent-api && make validate-local
find /home/zaks/bookkeeping/docs -maxdepth 1 -type f -name "MISSION-FRONTEND-GOVERNANCE-HARDENING-001*" -o -name "FRONTEND-GOVERNANCE-HARDENING-001-*"
```

If baseline validation fails during recovery, classify as pre-existing or mission-induced before continuing.

---

## Continuation Protocol <!-- Adopted from Improvement Area IA-7 -->

At end of each session, update:
- `/home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md`

Checkpoint minimum content:
1. Completed phases
2. Remaining phases
3. Current validation status (`make validate-local`, `make validate-surface9`)
4. Open blockers/decisions
5. Exact next command to run

---

## Context Checkpoint <!-- Adopted from Improvement Area IA-1 -->

If context becomes constrained mid-mission:
1. Write status to `/home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md`
2. Commit logically complete intermediate work
3. Resume via Crash Recovery Protocol

---

## 2b. Glossary

| Term | Definition |
|------|-----------|
| Gate E | `stop.sh` check that blocks raw `httpx` usage in `deal_tools.py` |
| PATH resilience | Hook behavior remains correct whether `rg` is present or absent in PATH |
| Surface 9 governance | Dashboard design-system contract and path-scoped frontend quality rules |
| Category B | Frontend design quality section in `design-system.md` |
| Anti-convergence | Explicit rule to avoid repetitive template-like frontend outputs |
| Proportional enforcement | Add enough checks to catch drift without overbuilding brittle rules |

---

## 3. Architectural Constraints

- **Fix hook resilience first**
Meaning: Address Gate E `rg` PATH fragility before broader governance work.
Why: Hook reliability is baseline infrastructure safety.

- **No app feature changes**
Meaning: Do not modify dashboard product behavior to satisfy governance checks.
Why: Mission scope is infrastructure/rules/enforcement only.

- **Preserve Surface 9 existing guarantees**
Meaning: Do not remove or weaken current design-system conventions.
Why: Existing contract behavior must remain intact.

- **Path-scoped rules must remain path-scoped**
Meaning: New rule files require valid frontmatter `paths` and actionable content.
Why: Rules must auto-load deterministically.

- **Use frontend-design skill as complement, not replacement**
Meaning: Keep project-scoped rules; add skill preload linkage for broader design guidance.
Why: Skill and rule operate at different scopes.

- **No generated file edits**
Meaning: Do not touch `*.generated.ts` or `*_models.py`.
Why: Generated artifacts are pipeline-owned.

- **Do not regress 14-surface contract state**
Meaning: `make validate-contract-surfaces` must remain green at end.
Why: Prior mission chain depends on stable 14-surface baseline.

- **Port 8090 remains forbidden**
Meaning: Do not add 8090 references in rules/hooks/docs.
Why: Historical drift risk.

- **WSL safety remains mandatory**
Meaning: New shell files LF-only, sane ownership under `/home/zaks/`.
Why: Prevent delayed runtime failures.

---

## 3b. Anti-Pattern Examples

### WRONG: Hook assumes `rg` always exists
```bash
if rg -n "httpx\.(AsyncClient|get|post|put|patch|delete)" apps/agent-api/app/core/langgraph/tools/deal_tools.py; then
  echo "ERROR"
  exit 2
fi
```

### RIGHT: Hook scan with robust fallback
```bash
if command -v rg >/dev/null 2>&1; then
  SCAN_CMD='rg -n'
else
  SCAN_CMD='grep -nE'
fi
# run chosen scanner and fail closed on scanner errors
```

### WRONG: New rule file without path frontmatter
```markdown
# Accessibility Rule
Use semantic HTML.
```

### RIGHT: Path-scoped governance rule
```markdown
---
paths:
  - "apps/dashboard/src/components/**"
  - "apps/dashboard/src/app/**"
---
# Accessibility Rule
```

### WRONG: Design-system rule stays vague
```markdown
Use responsive design and animations.
```

### RIGHT: Design-system rule is enforceable
```markdown
- Breakpoint reference and usage policy
- z-index scale tokens
- dark mode strategy
- reduced-motion and GPU-safe animation guidance
- state management decision matrix
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Gate E fallback is added but scanner errors are treated as pass | HIGH | Silent enforcement gap | Phase 1 gate includes forced negative and scanner-error-path checks |
| 2 | New rules are created but not path-scoped | HIGH | Rules never auto-load | Phase 2 gate verifies frontmatter paths and file presence |
| 3 | design-system is enriched but Surface 9 validator does not enforce new sections | MEDIUM | Drift returns quickly | Phase 4 updates validator checks and requires runtime pass |
| 4 | Governance edits accidentally regress 14-surface validation | MEDIUM | Mission chain breakage | Every phase gate includes `make validate-local`; final includes contract validation |
| 5 | Playwright policy changed without clear rationale | MEDIUM | Team confusion and brittle setup | Phase 5 requires explicit tooling policy record and rationale |

---

## 4. Phases

## Phase 0 - Discovery and Baseline Evidence
**Complexity:** S  
**Estimated touch points:** 0 files modified

**Purpose:** Reconfirm findings and capture baseline before edits.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Capture baseline evidence file**
  - Create `/home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-BASELINE.md`.
  - Include outputs for:
    - `cd /home/zaks/zakops-agent-api && make validate-local`
    - `cd /home/zaks/zakops-agent-api && make validate-surface9`
    - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
  - **Checkpoint:** Baseline file has timestamped command outputs.

- P0-02: **Baseline hook/path behavior capture**
  - Capture current Gate E block from `/home/zaks/.claude/hooks/stop.sh`.
  - Capture current `design-system.md` section map and existing rules inventory.
  - **Checkpoint:** Baseline evidence shows pre-fix hook and pre-mission governance coverage.

### Decision Tree
- **IF** baseline 14-surface validation fails -> stop and classify pre-existing breakage.
- **ELSE** proceed to Phase 1.

### Rollback Plan
1. No rollback required (read-only phase).
2. Confirm clean state with `cd /home/zaks/zakops-agent-api && git status --short`.

### Gate P0
- Baseline evidence file created.
- Baseline commands and governance inventory captured.

---

## Phase 1 - Stop Hook Gate E PATH Resilience (Included by Requirement)
**Complexity:** S  
**Estimated touch points:** 1 file modified

**Purpose:** Eliminate `rg` PATH fragility in hook context while preserving fail-closed behavior.

### Blast Radius
- **Services affected:** Hook runtime validation flow
- **Pages affected:** None
- **Downstream consumers:** All sessions using `stop.sh`

### Tasks
- P1-01: **Harden Gate E scanner selection**
  - Modify `/home/zaks/.claude/hooks/stop.sh` Gate E logic to support scanner fallback (`rg` preferred, `grep -nE` fallback).
  - Ensure scanner errors are handled explicitly (do not silently pass on scanner failure).
  - **Checkpoint:** Hook code clearly distinguishes: violation found vs scanner unavailable/error.

- P1-02: **Keep Gate B labeling accurate**
  - Preserve/confirm Gate B label and comments reflect 14-surface state.
  - **Checkpoint:** No stale count labels in hook output.

- P1-03: **Run hook resilience checks**
  - Test normal run and constrained PATH run.
  - Example constrained run:
    - `cd /home/zaks/zakops-agent-api && env -i PATH=/usr/bin:/bin bash /home/zaks/.claude/hooks/stop.sh`
  - **Checkpoint:** Hook still enforces Gate E and exits correctly.

### Decision Tree
- **IF** both `rg` and `grep` unavailable -> fail closed with explicit error.
- **ELSE IF** scanner command errors for reasons other than no matches -> fail with explicit scanner error.
- **ELSE** proceed.

### Rollback Plan
1. Revert only `/home/zaks/.claude/hooks/stop.sh` changes.
2. Re-run baseline stop-hook command and `make validate-local`.

### Gate P1
- Hook passes in normal and constrained PATH contexts.
- Gate E no longer depends solely on `rg` PATH availability.
- No stale 9-surface labeling remains in `stop.sh`.

---

## Phase 2 - Create Missing Frontend Governance Rules (G8, G9)
**Complexity:** M  
**Estimated touch points:** 2-3 files created

**Purpose:** Add path-scoped rule coverage for accessibility and component composition patterns.

### Blast Radius
- **Services affected:** Dashboard development guidance
- **Pages affected:** Dashboard component/app paths (guidance only)
- **Downstream consumers:** Claude rule auto-loading, frontend implementation consistency

### Tasks
- P2-01: **Create accessibility rule**
  - Create `/home/zaks/zakops-agent-api/.claude/rules/accessibility.md` with frontmatter paths for dashboard app/component/styles/hook files.
  - Include actionable WCAG-aligned guidance:
    - semantic structure
    - keyboard navigation/focus management
    - contrast targets
    - aria usage boundaries
    - reduced-motion accessibility
  - **Checkpoint:** Rule file exists with valid frontmatter and concrete checks.

- P2-02: **Create component-patterns rule**
  - Create `/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md` with path frontmatter.
  - Include actionable pattern guidance:
    - server/client component split
    - loading/empty/error state contract
    - suspense boundaries
    - state ownership boundaries
    - composability and prop-shape discipline
  - **Checkpoint:** Rule file exists with valid frontmatter and concrete patterns.

- P2-03: **Optional registry alignment**
  - If constraint registry is used for governance checks, add only high-value constraints to `/home/zaks/zakops-agent-api/.claude/CONSTRAINT_REGISTRY.md`.
  - **Checkpoint:** Registry changes, if made, are minimal and intentional.

### Decision Tree
- **IF** rule content is too vague to enforce -> strengthen with explicit do/donot statements.
- **ELSE** proceed.

### Rollback Plan
1. Remove newly created rule files.
2. Re-run `make validate-local` and `make validate-surface9`.

### Gate P2
- `accessibility.md` and `component-patterns.md` exist with valid path frontmatter.
- Governance guidance is actionable (not generic).

---

## Phase 3 - Enrich Design System Rule Coverage (G10, G11, G12, G13, G14, G18)
**Complexity:** M  
**Estimated touch points:** 1-2 files modified

**Purpose:** Upgrade `design-system.md` from partial guidance to complete governance reference.

### Blast Radius
- **Services affected:** Dashboard frontend guidance and consistency
- **Pages affected:** Dashboard code paths covered by rule
- **Downstream consumers:** Claude-assisted frontend implementation quality

### Tasks
- P3-01: **Add skill preload linkage**
  - Update `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` to include a `Skill Preloads` section referencing:
    - `/home/zaks/.claude/skills/frontend-design/SKILL.md`
  - **Checkpoint:** Rule explicitly links local frontend skill.

- P3-02: **Add missing Category B content from audit delta**
  - Add/expand sections covering:
    - tone palette options and direction selection
    - anti-convergence and variation policy
    - additional visual-technique guidance (textures/layers/effects) where appropriate
  - **Checkpoint:** G11 delta areas are addressed in-rule.

- P3-03: **Add operational governance details**
  - Add explicit guidance for:
    - responsive breakpoint reference strategy (G10)
    - z-index scale/tokens (G12)
    - dark mode strategy (G13)
    - animation performance (GPU-safe vs layout-triggering, reduced motion) (G14)
    - state-management decision guidance (local state vs context vs server state) (G18)
  - **Checkpoint:** Each gap has a named subsection with actionable policy.

### Decision Tree
- **IF** a governance subsection cannot reference a single source-of-truth file -> define one explicitly in-rule.
- **ELSE** proceed.

### Rollback Plan
1. Revert `design-system.md` to prior revision.
2. Re-run `make validate-surface9` and `make validate-local`.

### Gate P3
- `design-system.md` includes all missing governance sections.
- Skill preload reference is present and absolute.

---

## Phase 4 - Surface 9 Validator Hardening for New Governance Rules
**Complexity:** M  
**Estimated touch points:** 1-2 files modified

**Purpose:** Ensure new governance coverage is enforced, not just documented.

### Blast Radius
- **Services affected:** Surface 9 validation and unified contract checks
- **Pages affected:** None directly
- **Downstream consumers:** `make validate-surface9`, `make validate-contract-surfaces`, stop hook gate chain

### Tasks
- P4-01: **Extend `validate-surface9.sh` checks**
  - Update `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` to verify:
    - rule file presence for `accessibility.md` and `component-patterns.md`
    - key section presence in `design-system.md` for new governance items (breakpoints, z-index, dark mode, animation performance, state management, skill preload)
  - **Checkpoint:** Script emits explicit PASS/FAIL lines for each new governance check.

- P4-02: **Maintain backward checks**
  - Preserve existing checks (import discipline, stage definitions, Promise rules, manifest/rule presence).
  - **Checkpoint:** Existing Surface 9 checks still run and remain meaningful.

- P4-03: **Run validator and aggregate checks**
  - `cd /home/zaks/zakops-agent-api && make validate-surface9`
  - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
  - **Checkpoint:** Both commands pass.

### Decision Tree
- **IF** new checks create false positives from wording variations -> normalize with robust keyword patterns.
- **ELSE** proceed.

### Rollback Plan
1. Revert `validate-surface9.sh` changes only.
2. Re-run prior baseline commands.

### Gate P4
- Surface 9 validator enforces new governance rule coverage.
- Unified contract validation remains green.

---

## Phase 5 - Frontend Tooling Policy Clarification (G7 policy closure)
**Complexity:** S  
**Estimated touch points:** 1-2 files modified/created

**Purpose:** Document clear policy for frontend tool usage (including Playwright MCP status) to remove ambiguity.

### Blast Radius
- **Services affected:** Developer/operator workflow guidance
- **Pages affected:** None
- **Downstream consumers:** Builders, QA missions, onboarding

### Tasks
- P5-01: **Document tooling policy**
  - Create `/home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md` with:
    - frontend-design skill usage policy
    - Playwright MCP status policy (`disabled` vs enabled profiles and when)
    - verification expectations by change type
  - **Checkpoint:** Policy gives explicit runbook, not general suggestions.

- P5-02: **Reference policy from governance docs**
  - Add reference link in mission completion and/or relevant docs where frontend governance is discussed.
  - **Checkpoint:** Policy is discoverable by future sessions.

### Decision Tree
- **IF** Playwright remains disabled -> policy must state rationale and enable steps.
- **ELSE IF** Playwright enabled -> policy must state constraints and usage guardrails.

### Rollback Plan
1. Remove policy document/reference additions.
2. Re-run no-regression checks.

### Gate P5
- Tooling policy exists and explicitly resolves ambiguity around Playwright status.

---

## Phase 6 - Final Verification and Bookkeeping
**Complexity:** M  
**Estimated touch points:** 2-4 files modified

**Purpose:** Verify full mission success and close with evidence.

### Blast Radius
- **Services affected:** Validation and governance documentation workflows
- **Pages affected:** None directly
- **Downstream consumers:** QA successor mission

### Tasks
- P6-01: **Run final validation gates**
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api && make validate-surface9`
  - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
  - `cd /home/zaks/zakops-agent-api && timeout 35 bash /home/zaks/.claude/hooks/stop.sh`
  - **Checkpoint:** All commands pass.

- P6-02: **Produce completion report**
  - Create `/home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-COMPLETION.md`.
  - Include:
    - phase outcomes
    - AC-by-AC evidence mapping
    - before/after hook resilience summary
  - **Checkpoint:** Completion report references concrete evidence paths.

- P6-03: **Bookkeeping and checkpoint closure**
  - Update `/home/zaks/bookkeeping/CHANGES.md`.
  - Update `/home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md` with mission-closed status.
  - **Checkpoint:** Mission closure is traceable in project bookkeeping.

### Decision Tree
- **IF** any final gate fails -> remediate and re-run failed gate + `make validate-local`.
- **ELSE** finalize mission and hand off to QA successor.

### Rollback Plan
1. Revert latest changes from current phase.
2. Re-run baseline validation commands.
3. Rebuild completion evidence.

### Gate P6
- Final validation commands pass.
- Completion report exists with AC evidence mapping.
- CHANGES/checkpoint updated.

---

## 4b. Dependency Graph

```
Phase 0 (Discovery + Baseline)
    |
    v
Phase 1 (Stop Hook PATH Resilience)
    |
    v
Phase 2 (Create Missing Rules)
    |
    v
Phase 3 (Enrich Design System)
    |
    v
Phase 4 (Surface 9 Validator Hardening)
    |
    v
Phase 5 (Tooling Policy Clarification)
    |
    v
Phase 6 (Final Verification + Bookkeeping)
```

Phases execute sequentially. Do not parallelize Phase 1 with frontend rule work.

---

## 5. Acceptance Criteria

### AC-1: Baseline Evidence Captured
`FRONTEND-GOVERNANCE-HARDENING-001-BASELINE.md` exists with pre-edit validation and inventory outputs.

### AC-2: Gate E PATH Resilience Fixed
`/home/zaks/.claude/hooks/stop.sh` Gate E no longer depends solely on `rg` PATH availability.

### AC-3: Accessibility Rule Coverage Added
`/home/zaks/zakops-agent-api/.claude/rules/accessibility.md` exists, path-scoped, and actionable.

### AC-4: Component Pattern Rule Coverage Added
`/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md` exists, path-scoped, and actionable.

### AC-5: Design-System Skill Linkage Added
`design-system.md` includes explicit preload/reference to `/home/zaks/.claude/skills/frontend-design/SKILL.md`.

### AC-6: Design-System Governance Gaps Closed
`design-system.md` includes explicit sections for breakpoints, z-index scale, dark mode strategy, animation performance, anti-convergence/variation, and state management guidance.

### AC-7: Surface 9 Validator Enforces New Governance
`validate-surface9.sh` checks rule presence and new design-system governance section anchors.

### AC-8: Surface Validation Integrity Preserved
`make validate-surface9` and `make validate-contract-surfaces` pass after changes.

### AC-9: Hook Runtime Integrity Preserved
`stop.sh` passes in normal and constrained PATH contexts without false passes.

### AC-10: Frontend Tooling Policy Clarified
`FRONTEND-TOOLING-POLICY.md` exists and resolves Playwright/skill usage ambiguity.

### AC-11: No Regressions
`make validate-local` passes; no generated-file or migration regressions introduced.

### AC-12: Bookkeeping Complete
CHANGES/checkpoint/completion report updated with evidence references.

---

## 6. Guardrails

1. Do not implement product features or visual redesigns in this mission.
2. Do not modify API endpoints, backend business logic, or database schema.
3. Do not weaken or remove existing Surface 9 enforcement checks.
4. Do not introduce hook logic that silently passes scanner errors.
5. Do not add non-path-scoped rule files under `.claude/rules/`.
6. Do not edit generated files or migration files.
7. Do not regress 14-surface validation baseline.
8. Do not add port 8090 references.
9. Do keep new shell logic LF-only and ownership sane under `/home/zaks/`.
10. Do capture evidence for each phase gate.

---

## 7. Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture baseline outputs before changing hook/rules?
- [ ] Did I confirm 14-surface validation was green at baseline?
- [ ] Did I record the exact pre-fix Gate E behavior?

### After Phase 1
- [ ] Can Gate E detect violations when `rg` is absent?
- [ ] Are scanner errors fail-closed, not silent pass?
- [ ] Is Gate B still labeled as 14 surfaces?

### After Phases 2-4
- [ ] Are new rule files path-scoped with valid frontmatter?
- [ ] Are governance sections in `design-system.md` explicit and testable?
- [ ] Does `validate-surface9.sh` enforce the new governance additions?

### Before Mission Complete
- [ ] Did `make validate-local` pass after final changes?
- [ ] Did `make validate-contract-surfaces` remain green at 14/14?
- [ ] Did constrained-PATH stop-hook run pass correctly?
- [ ] Did I update CHANGES, checkpoint, and completion report?

---

## 8. File Paths Reference

### Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/.claude/hooks/stop.sh` | 1 | Harden Gate E scanner PATH resilience |
| `/home/zaks/zakops-agent-api/.claude/rules/design-system.md` | 3 | Add missing governance sections and skill preload linkage |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface9.sh` | 4 | Enforce new governance anchors/rule presence |
| `/home/zaks/zakops-agent-api/.claude/CONSTRAINT_REGISTRY.md` | 2 (optional) | Add minimal governance constraints if justified |
| `/home/zaks/bookkeeping/CHANGES.md` | 6 | Record mission changes |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/.claude/rules/accessibility.md` | 2 | Path-scoped accessibility governance rule |
| `/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md` | 2 | Path-scoped component pattern governance rule |
| `/home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md` | 5 | Tooling policy for frontend skill/Playwright usage |
| `/home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-BASELINE.md` | 0 | Baseline evidence capture |
| `/home/zaks/bookkeeping/docs/FRONTEND-GOVERNANCE-HARDENING-001-COMPLETION.md` | 6 | Completion report with AC evidence mapping |
| `/home/zaks/bookkeeping/mission-checkpoints/FRONTEND-GOVERNANCE-HARDENING-001.md` | all | Multi-session checkpoint |

### Files to Read (Do Not Modify Unless Explicit Task Requires It)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md` | Ground truth for governance gaps G8-G14, G18 |
| `/home/zaks/bookkeeping/qa-verifications/QA-S10-14-VERIFY-001/SCORECARD.md` | INFO-2 hook PATH issue and post-14 baseline context |
| `/home/zaks/.claude/skills/frontend-design/SKILL.md` | Source guidance for Category B enrichment |
| `/home/zaks/zakops-agent-api/.claude/rules/dashboard-types.md` | Existing dashboard type guidance context |
| `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` | Surface 9 context and 14-surface baseline |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/types/design-system-manifest.ts` | Existing Surface 9 convention manifest |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Prompt format and quality standard |

---

## 9. Stop Condition

Stop when all ACs (AC-1 through AC-12) are satisfied, hook Gate E is PATH-resilient, frontend governance rules are complete and enforced by Surface 9 validation, and no regressions appear in 14-surface validation baseline.

Do not proceed into broader frontend feature redesign or CI-wide performance initiatives within this mission. Those remain successor work after QA confirms this mission.

---

*End of Mission Prompt - FRONTEND-GOVERNANCE-HARDENING-001*
