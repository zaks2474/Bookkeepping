# Mission Prompt Quick-Start — Cheat Sheet

**Full standard:** `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` (v2.4)
**Validate a prompt:** `/validate-mission <path>`

---

## Execution Mission Skeleton

```
# MISSION: {MISSION-ID}
## {Subtitle}
## Date: YYYY-MM-DD
## Classification: {Category}
## Prerequisite: {Prior mission or "None"}
## Successor: {Next mission or "None"}

## Mission Objective          ← What to do, what NOT to do, source material
## Context                    ← Findings, environment changes, prior deliverables
## Glossary                   ← If 3+ project-specific terms (optional)
## Architectural Constraints  ← Non-negotiable patterns (MANDATORY)
## Anti-Pattern Examples      ← WRONG vs. RIGHT for critical constraints
## Pre-Mortem                 ← 3–5 specific failure scenarios with mitigations

## Phase 0 — Discovery & Baseline
  Complexity: S/M/L/XL | Blast Radius | Tasks | Checkpoints | Gate
## Phase N — {Name}
  Complexity | Blast Radius | Tasks | Decision Tree (if forks) | Rollback | Gate
## Dependency Graph           ← If 4+ phases or parallel paths

## Acceptance Criteria        ← AC-1 through AC-N (always end with no-regression + bookkeeping)
## Guardrails                 ← 6–10 items: scope fence, generated files, WSL safety, Surface 9
## Executor Self-Check Prompts ← After discovery, after code changes, before completion
## File Paths Reference       ← Three tables: modify, create, read-only
## Stop Condition             ← When DONE, what NOT to proceed to
## Completion Report          ← MANDATORY: fill in Section 9b template (phases, AC, validation, files)
```

## QA Mission Skeleton

```
# MISSION: QA-{ID}-VERIFY-{N}
## {Same 7-field header}

## Pre-Flight (PF-1..N)      ← Baseline checks before any verification
## Verification Families      ← VF-01..N, each with bash+tee evidence commands
## Cross-Consistency (XC-1..N) ← Artifacts agree with each other
## Stress Tests (ST-1..N)     ← Edge cases beyond source mission scope
## Remediation Protocol       ← Classify → fix → re-verify → record
## Enhancement Opportunities  ← ENH-1..N (feed back into next execution mission)
## Scorecard Template         ← Pre-formatted, fill in gates
## Guardrails + Stop Condition
```

## 7 Things You Must Not Forget

1. **Reference, don't repeat** — The builder already loads CLAUDE.md, MEMORY.md, hooks, rules. Say "per Surface 9" — don't copy the rules.
2. **Every phase needs a gate** — Concrete pass/fail with `make validate-local` or a mission-appropriate equivalent. If non-applicable, state why in guardrails. No gateless phases.
3. **Use absolute paths for execution targets** — `/home/zaks/zakops-agent-api/...` for files/commands being changed or verified; explanatory examples may be relative.
4. **Review Improvement Areas** — Read every IA in the standard. Include IA-2 crash recovery for 3+ phases, IA-1 context checkpoint for 5+ phases or 500+ lines, IA-7 continuity for XL missions.
5. **Evidence, not claims** — Execution: completion report per phase. QA: `tee` to evidence file for every gate.
6. **Git commit discipline** — Commit after each phase gate passes. Format: `MISSION-ID P{N}: {description}`. Feature branch for multi-phase missions.
7. **Completion report is mandatory** — Execution missions must produce a completion report (Section 9b template) as their final deliverable. Without it, the mission is not DONE.

## Session Validation Clarifications

1. **Canonical memory answer must include both paths** —  
   Canonical: `/root/.claude/projects/-home-zaks/memory/MEMORY.md`  
   Symlink alias: `/root/.claude/projects/-mnt-c-Users-mzsai/memory`
2. **Pre-write mission plan must include evidence expectations explicitly** —  
   Execution missions: completion artifacts + checkpoint + `CHANGES.md` trace.  
   QA missions: `tee` evidence capture for every PF/VF/XC/ST gate.

## Lab Loop (Automated Execution)

Lab Loop runs an iterative **Builder (Claude) → Gate → QA (Codex/Gemini)** cycle until PASS or stuck.

```bash
# Create task from mission
labloop new <TASK_ID> --repo /home/zaks/zakops-agent-api --gate "make validate-local"
# Copy mission.md + acceptance.md into tasks/<TASK_ID>/
labloop run <TASK_ID>
```

- Config: `~/.labloop/config` (models: opus / gpt-5.3-codex / gemini-3-pro)
- Profiles: `labloop/profiles/` (gate-nextjs.sh, gate-python-full.sh, etc.)
- Email alerts: STARTED, PASS, STUCK, MAX_CYCLES
- All agents use the same CLIs + configs as interactive sessions (headless mode)
- See full details in MISSION-PROMPT-STANDARD.md § "Lab Loop Automation Pipeline"

## After Generating

Run `/validate-mission /path/to/your/mission.md` to check structural completeness before handing it to a builder.

---

*Companion to MISSION-PROMPT-STANDARD.md v2.4*
