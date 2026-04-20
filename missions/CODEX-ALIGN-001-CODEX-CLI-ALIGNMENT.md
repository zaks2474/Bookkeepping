# MISSION: CODEX-ALIGN-001
## Codex CLI Configuration Alignment to ZakOps Operational Standard
## Date: 2026-02-12
## Classification: Infrastructure Alignment and Tooling Governance
## Prerequisite: `/home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md` approved
## Successor: QA-CODEX-ALIGN-VERIFY-001 (independent verification)

---

<!-- Adopted from Improvement Area IA-2 -->
## Recovery Protocol (Crash/Resume)
If resuming after interruption:
1. `cd /home/zaks && /root/.npm-global/bin/codex --version`
2. `cd /home/zaks/zakops-agent-api && make validate-local`
3. Re-run inventory checks from `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/baseline-inventory.md`

---

## Mission Objective
Bring Codex CLI to practical operational parity with the established ZakOps Claude environment, based on `/home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md`.

This mission configures instructions, skills, rules, MCP servers, wrapper scripts, shell integration, compatibility stubs, and verification/reporting so Codex can execute in a consistent, governed way across `/home/zaks`, `/home/zaks/zakops-agent-api`, and `/home/zaks/zakops-backend`.

This is an alignment and hardening mission, not product feature development. Do not implement unrelated app behavior changes.

---

## Context
Primary source of truth:
- `/home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md`

Standards and validation references:
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md`
- `/home/zaks/zakops-agent-api/tools/infra/validate-mission.sh`

Plan-defined alignment scope:
- Foundation: three AGENTS files and expanded Codex `config.toml`
- Skills: 26 skill directories (`~/.codex/skills` + project `.agents/skills`)
- Rules: replace ad-hoc rules with structured default rules
- MCP: register GitHub, Playwright, Gmail, crawl4ai-rag servers
- Scripts: boot/stop/notify/wrapper integration
- Shell + compatibility: `.bashrc` alias/path and superseded header in legacy instructions
- Verification: structural/content/functional/runtime/MCP checks and bookkeeping

Plan-defined permanent capability gaps to preserve as explicit constraints:
- No Codex pre-tool hooks and no pre-edit hard blocking equivalent
- No persistent memory AUTOSYNC sentinel mechanism
- No sub-agent delegation equivalent
- No compaction hooks
- No post-tool async formatting hook
- No task-completed hook equivalent

---

## Glossary

| Term | Definition |
|------|------------|
| Operational parity | Configuration-level consistency between Codex and Claude execution environments where technically possible |
| Foundation files | AGENTS and config artifacts that define baseline Codex behavior |
| Wrapper lifecycle | `codex-boot.sh` + Codex execution + `codex-stop.sh` workflow via `codex-safe` alias |
| Permanent gap | Capability that cannot be replicated in Codex and must be explicitly documented with mitigation |
| Runtime load proof | Command-based verification that AGENTS instructions are actually being read by Codex |

---

## Architectural Constraints
- **Plan lock:** Execute only the scope in `/home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md`.
- **Absolute path discipline:** All file targets and commands must use full `/home/zaks/...` paths.
- **No secret leakage:** Never store plaintext tokens/passwords in `~/.codex/config.toml` or artifacts.
- **Compatibility preservation:** Keep `/home/zaks/.codex/CODEX_INSTRUCTIONS.md` content intact except superseded header.
- **Non-destructive migration:** Do not delete existing Codex config/components unless explicitly marked replacement in plan.
- **Ownership and line endings:** All new `/home/zaks` files must be `zaks:zaks` and LF line endings.
- **Generated/contract safety:** Do not modify generated API/type files while performing Codex alignment.
- **Validation discipline:** `make validate-local` and mission verification checklist completion are required exit gates.

---

## Anti-Pattern Examples

### WRONG: Replace legacy instructions file entirely
```text
Delete CODEX_INSTRUCTIONS.md and move all content to AGENTS.md.
```

### RIGHT: Preserve backward compatibility
```text
Add superseded header to CODEX_INSTRUCTIONS.md and keep legacy content intact.
```

### WRONG: Add MCP entries without runtime verification
```text
`codex mcp add ...` executed, no per-server behavioral check recorded.
```

### RIGHT: Register + verify each MCP server
```text
Record `codex mcp list` output and one real tool interaction per server.
```

### WRONG: Claim AGENTS parity without load proof
```text
AGENTS files exist, but no `codex exec` checks verify instruction loading.
```

### RIGHT: Runtime load proof with expected answer checks
```text
Run monorepo/backend AGENTS prompt checks and compare output to expected values.
```

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|------------------|------------|--------|------------|
| 1 | AGENTS files created but Codex ignores project-scoped `.agents/AGENTS.md` | Medium | High | Runtime load proof + fallback to repo-root `AGENTS.md` path in decision tree |
| 2 | Skill directories exist but SKILL metadata invalid | Medium | Medium | Phase 2 frontmatter validation + count checks |
| 3 | MCP setup fails due auth/container prerequisites | High | Medium | Explicit per-server prerequisite handling and blocked-state documentation |
| 4 | Wrapper scripts created with CRLF/root ownership | Medium | High | Dedicated LF + ownership checks in Phase 5/8 gates |
| 5 | Config drift from typo/duplicate path entries in `config.toml` | Medium | High | Path lint check and explicit project trust verification in Phase 1 gate |

---

## Phase 0 - Baseline Inventory and Scope Freeze
**Complexity:** S
**Estimated touch points:** 1-3 files

**Purpose:** Capture current Codex state and create rollback anchors before edits.

### Blast Radius
- **Services affected:** Codex runtime only
- **Pages affected:** none
- **Downstream consumers:** all alignment phases depend on baseline inventory

### Tasks
- P0-01: Snapshot current Codex config/instruction/rules state.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/baseline-inventory.md`
  - Checkpoint: includes current profiles, rules, skills count, MCP list status.
- P0-02: Create boundary snapshot before edits.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/pre-align-boundary.md`
  - Checkpoint: changed-file manifest + `git diff --stat` where applicable.
- P0-03: Materialize execution checklist from plan verification matrix.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/verification-checklist.md`
  - Checkpoint: checklist includes structural/content/functional/runtime/MCP groups.

### Rollback Plan
1. Keep baseline artifacts immutable.
2. If edits must be reverted, restore files from boundary manifest and re-run baseline inventory.

### Gate P0
- Baseline inventory exists and is complete.
- Pre-align boundary snapshot exists.
- Verification checklist scaffold exists.

---

## Phase 1 - Foundation Files and Codex Config Expansion
**Complexity:** L
**Estimated touch points:** 4-8 files

**Purpose:** Build instruction foundation and aligned `config.toml`.

### Blast Radius
- **Services affected:** Codex global + project instruction loading
- **Pages affected:** none
- **Downstream consumers:** all later phases depend on foundation consistency

### Tasks
- P1-01: Create global AGENTS.
  - Path: `/home/zaks/.codex/AGENTS.md`
  - Checkpoint: includes ZakOps guidelines, constraints, lifecycle, and permanent-gap mitigations.
- P1-02: Create monorepo project AGENTS.
  - Path: `/home/zaks/zakops-agent-api/.agents/AGENTS.md`
  - Checkpoint: includes read-first docs, 14 surfaces, inlined path-scoped guidance, and checklists.
- P1-03: Create backend project AGENTS.
  - Path: `/home/zaks/zakops-backend/.agents/AGENTS.md`
  - Checkpoint: includes backend conventions, DB schema guidance, and test commands.
- P1-04: Update Codex config.
  - Path: `/home/zaks/.codex/config.toml`
  - Checkpoint: notify configured, 5 profiles present, correct trusted project paths, typo path removed.

### Decision Tree
- IF AGENTS content risks size limits -> keep concise and move deep procedure details into skills.
- ELSE -> keep full plan-defined sections in AGENTS directly.

### Rollback Plan
1. Revert only misconfigured entries in `config.toml`.
2. Restore AGENTS from baseline if malformed and regenerate with minimal required sections.

### Gate P1
- `/home/zaks/.codex/AGENTS.md` exists and within size target.
- Project AGENTS files exist at both project paths.
- `config.toml` contains notify/profiles/trusted projects and no typo path entries.

---

## Phase 2 - Skills Layer Alignment (26 Skills)
**Complexity:** XL
**Estimated touch points:** 26-40 files

**Purpose:** Port action/knowledge/project command workflows into Codex skills.

### Blast Radius
- **Services affected:** Codex reusable workflow library
- **Pages affected:** none
- **Downstream consumers:** quality/consistency for future Codex sessions

### Tasks
- P2-01: Create 11 user action skills under `/home/zaks/.codex/skills/`.
  - Checkpoint: each skill has valid `SKILL.md` with name + description and task instructions.
- P2-02: Port 8 user knowledge skills under `/home/zaks/.codex/skills/`.
  - Checkpoint: adapted content references current ZakOps paths and constraints.
- P2-03: Create 7 project skills under `/home/zaks/zakops-agent-api/.agents/skills/`.
  - Checkpoint: commands/checklists map to current `.claude/commands` intent.
- P2-04: Validate skill discovery and counts.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/skills-validation.md`
  - Checkpoint: 19 user skills + 7 project skills verified.

### Decision Tree
- IF copied skill contains path-relative ambiguity -> rewrite paths as absolute `/home/zaks/...` references.
- ELSE -> keep source intent and minimize semantic drift.

### Rollback Plan
1. Remove only invalid skill folders.
2. Recreate from source mappings with corrected frontmatter and paths.

### Gate P2
- User skill count and project skill count match plan.
- All skill files parse and are discoverable.
- Skills-validation report is complete.

---

## Phase 3 - Sandbox Rules Normalization
**Complexity:** M
**Estimated touch points:** 1-2 files

**Purpose:** Replace ad-hoc rules with structured allow patterns.

### Blast Radius
- **Services affected:** Codex command approval behavior
- **Pages affected:** none
- **Downstream consumers:** runtime safety and friction reduction

### Tasks
- P3-01: Replace rules file with structured categories.
  - Path: `/home/zaks/.codex/rules/default.rules`
  - Checkpoint: includes make, docker, git, health, test, file-inspection, and system categories.
- P3-02: Validate rule coverage against plan categories.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/rules-validation.md`
  - Checkpoint: coverage matrix complete and no malformed entries.

### Rollback Plan
1. Restore previous rules backup from baseline snapshot.
2. Reapply structured categories incrementally.

### Gate P3
- `default.rules` exists with structured categories.
- Rules-validation report confirms plan coverage.

---

## Phase 4 - MCP Server Registration and Connectivity
**Complexity:** L
**Estimated touch points:** 2-6 files

**Purpose:** Align Codex MCP capabilities to GitHub/Playwright/Gmail/crawl4ai-rag set.

### Blast Radius
- **Services affected:** Codex tool integrations and external auth dependencies
- **Pages affected:** none
- **Downstream consumers:** workflow parity with Claude tooling

### Tasks
- P4-01: Register 4 MCP servers using plan-defined commands.
  - Checkpoint: `codex mcp list` shows all target server names.
- P4-02: Run per-server behavioral verification.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/mcp-verification.md`
  - Checkpoint: one successful functional call per server or explicit blocked reason.
- P4-03: Secret leakage scan.
  - Checkpoint: no plaintext credential values in codex config outputs.

### Decision Tree
- IF auth prerequisite missing (GitHub/Gmail/container) -> record blocked state + exact prerequisite and continue non-blocked validations.
- ELSE -> complete behavioral verification and archive evidence.

### Rollback Plan
1. Remove only broken MCP entries.
2. Re-add with corrected command/auth prerequisites.

### Gate P4
- MCP list contains 4 configured servers.
- Behavioral verification report exists with pass/blocked status per server.
- Secret scan completed and clean.

---

## Context Checkpoint (IA-1)
After Phase 4, summarize completed work and constrain context before continuing:
- Produce `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/context-checkpoint-phase4.md` with:
  - completed phases and gates
  - files touched so far
  - open risks/blockers carried into Phase 5+
  - explicit list of remaining phases/tasks

---

## Phase 5 - Wrapper Script Lifecycle
**Complexity:** L
**Estimated touch points:** 4-8 files

**Purpose:** Introduce boot/stop/notify/wrapper lifecycle and ensure script hygiene.

### Blast Radius
- **Services affected:** Codex invocation flow and event logging
- **Pages affected:** none
- **Downstream consumers:** session safety, diagnostics, and post-run validation

### Tasks
- P5-01: Create `codex-boot.sh` with 6 diagnostic checks.
  - Path: `/home/zaks/scripts/codex-boot.sh`
  - Checkpoint: emits ALL CLEAR / PROCEED WITH CAUTION / HALT and exits non-zero on HALT.
- P5-02: Create `codex-stop.sh` with `make validate-local` and logging.
  - Path: `/home/zaks/scripts/codex-stop.sh`
  - Checkpoint: outputs validation summary and appends to log.
- P5-03: Create `codex-notify.sh` event logger.
  - Path: `/home/zaks/scripts/codex-notify.sh`
  - Checkpoint: handles agent-turn-complete JSON payload logging.
- P5-04: Create `codex-wrapper.sh` unified launcher with `CODEX_FORCE` bypass.
  - Path: `/home/zaks/scripts/codex-wrapper.sh`
  - Checkpoint: wrapper runs boot -> codex -> stop in non-force path.
- P5-05: Enforce LF and executable bits.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/script-hygiene.md`
  - Checkpoint: no CRLF and all scripts executable.

### Rollback Plan
1. Restore script backups from pre-align boundary.
2. Recreate scripts one-by-one and re-run hygiene checks.

### Gate P5
- All 4 scripts exist and are executable.
- Script-hygiene report confirms LF line endings.
- Wrapper flow executes correctly in dry-run/test mode.

---

## Phase 6 - Shell Integration
**Complexity:** S
**Estimated touch points:** 1 file

**Purpose:** Ensure Codex binary path and safe wrapper alias are available in shells.

### Blast Radius
- **Services affected:** user shell startup behavior
- **Pages affected:** none
- **Downstream consumers:** operational command consistency (`codex-safe`)

### Tasks
- P6-01: Update shell init.
  - Path: `/home/zaks/.bashrc`
  - Add: npm-global PATH export and `codex-safe` alias to wrapper.
  - Checkpoint: no duplicate conflicting entries introduced.
- P6-02: Verify command resolution.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/shell-integration.md`
  - Checkpoint: `codex` and `codex-safe` resolve correctly.

### Rollback Plan
1. Remove only Codex-specific lines from `.bashrc`.
2. Re-add with deduplicated entries.

### Gate P6
- `.bashrc` includes PATH and alias entries exactly once.
- Shell-integration report shows valid command resolution.

---

## Phase 7 - Backward Compatibility and Gap Register
**Complexity:** M
**Estimated touch points:** 2-5 files

**Purpose:** Preserve legacy compatibility and publish permanent capability-gap register.

### Blast Radius
- **Services affected:** legacy tooling references and operator expectations
- **Pages affected:** none
- **Downstream consumers:** future maintainers and QA verification

### Tasks
- P7-01: Add superseded header to legacy instructions file.
  - Path: `/home/zaks/.codex/CODEX_INSTRUCTIONS.md`
  - Checkpoint: existing legacy content remains intact below header.
- P7-02: Publish permanent gap register from plan-defined non-replicable capabilities.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/permanent-gaps.md`
  - Checkpoint: each gap includes mitigation and non-mitigation notes.

### Decision Tree
- IF runtime AGENTS load proof fails for `.agents/AGENTS.md` -> create/update fallback repo-root `AGENTS.md` in affected repo and re-run proof.
- ELSE -> keep scoped `.agents/AGENTS.md` structure unchanged.

### Rollback Plan
1. Remove only superseded header if placement is incorrect.
2. Regenerate gap register from plan source and baseline evidence.

### Gate P7
- Superseded header present and legacy instructions preserved.
- Permanent-gaps report exists and maps all plan-listed gaps.

---

## Phase 8 - Full Verification, Ownership, and Bookkeeping
**Complexity:** L
**Estimated touch points:** 4-10 files

**Purpose:** Execute full checklist and produce mission-complete evidence pack.

### Blast Radius
- **Services affected:** Codex runtime and validation reporting
- **Pages affected:** none
- **Downstream consumers:** QA verifier and future alignment maintenance

### Tasks
- P8-01: Run structural/content/functional/runtime/MCP verification checklist.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/verification-results.md`
  - Checkpoint: every checklist item marked PASS/FAIL/BLOCKED with evidence.
- P8-02: Fix ownership and line endings for `/home/zaks` deliverables.
  - Checkpoint: files owned by `zaks:zaks`, scripts LF-only.
- P8-03: Update bookkeeping.
  - Paths:
    - `/home/zaks/bookkeeping/CHANGES.md`
    - `/root/.claude/projects/-home-zaks/memory/MEMORY.md`
  - Checkpoint: mission completion entry recorded in both.
- P8-04: Publish completion summary.
  - Evidence: `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/completion-summary.md`
  - Checkpoint: includes final counts, blockers, and handoff notes.

### Rollback Plan
1. Revert incomplete/invalid verification outputs.
2. Re-run failed checklist categories until evidence is complete.

### Gate P8
- Verification-results report complete.
- Ownership/CRLF requirements satisfied.
- CHANGES and MEMORY updated.
- Completion summary published.

---

## Dependency Graph
Phases execute sequentially with limited internal parallelism:

Phase 0
  -> Phase 1 (1.1/1.2/1.3 parallel-safe, then 1.4)
  -> Phase 2 (action + knowledge skills parallel-safe, then project skills)
  -> Phase 3
  -> Phase 4
  -> Context Checkpoint (IA-1)
  -> Phase 5 (5.1/5.2/5.3 parallel-safe, then 5.4/5.5)
  -> Phase 6
  -> Phase 7
  -> Phase 8

---

## Acceptance Criteria

### AC-1: Foundation alignment complete
All three AGENTS files and expanded `config.toml` are present and conform to plan constraints.

### AC-2: Skills layer complete
26 skills are created/discoverable with valid `SKILL.md` metadata.

### AC-3: Rules alignment complete
`/home/zaks/.codex/rules/default.rules` is structured and category-complete per plan.

### AC-4: MCP integration complete
All four target MCP servers are registered and behavior-verified or explicitly blocked with prerequisites documented.

### AC-5: Wrapper lifecycle complete
All wrapper scripts exist, are executable, LF-only, and wrapper flow is verifiable.

### AC-6: Compatibility and gap register complete
Legacy `CODEX_INSTRUCTIONS.md` remains intact with superseded header and permanent gaps are documented with mitigations.

### AC-7: Verification checklist complete
Structural, content, functional, runtime, and MCP checks are fully reported with evidence.

### AC-8: Hygiene and ownership complete
No CRLF in scripts and `/home/zaks` deliverables are `zaks:zaks` owned.

### AC-9: Bookkeeping complete
`/home/zaks/bookkeeping/CHANGES.md` and `/root/.claude/projects/-home-zaks/memory/MEMORY.md` include mission completion entries.

---

## Guardrails
1. Do not modify unrelated product code while aligning Codex configuration.
2. Do not remove legacy instruction content from `/home/zaks/.codex/CODEX_INSTRUCTIONS.md`.
3. Do not store plaintext credentials in configs, reports, or scripts.
4. Keep all alignment artifacts under `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/`.
5. Preserve existing Claude-specific automation; this mission aligns Codex without degrading Claude setup.
6. If MCP server verification is blocked by auth/runtime prerequisites, mark `BLOCKED` with explicit reason and continue remaining gates.
7. Use deterministic command outputs for evidence; avoid unsupported assumptions.
8. Keep rollback paths clear for each phase.

---

## Non-Applicability Notes
- UI-specific design-system convergence rule `B7` is **not applicable** to this infrastructure alignment mission.
- Exact replication of Claude pre-tool hook enforcement is **not applicable** due Codex capability limits.
- Persistent memory AUTOSYNC parity is **not applicable**; only "read MEMORY.md" mitigation is feasible.
- Sub-agent delegation parity is **not applicable**; inline checklists are the replacement strategy.

---

## Executor Self-Check Prompts

### After Phase 0
- [ ] Did I capture a complete baseline inventory before any edits?
- [ ] Are verification checklist categories fully scaffolded?

### After each edit phase
- [ ] Did I keep changes strictly within plan-defined scope?
- [ ] Are all new paths absolute and consistent with `/home/zaks/...`?
- [ ] Did I avoid introducing secrets or destructive config drift?

### Before marking COMPLETE
- [ ] Do all phase gates P0-P8 pass with evidence?
- [ ] Are blocked items explicitly documented with prerequisites?
- [ ] Are ownership and LF hygiene checks complete?
- [ ] Do `make validate-local` and runtime proofs pass?
- [ ] Did I update CHANGES and MEMORY entries?

---

## File Paths Reference

### Files to Modify

| Path | Phase | Change |
|------|-------|--------|
| `/home/zaks/.codex/config.toml` | Phase 1 | Notify, profiles, trust entries, history, fallback filenames |
| `/home/zaks/.bashrc` | Phase 6 | Codex PATH export + `codex-safe` alias |
| `/home/zaks/.codex/CODEX_INSTRUCTIONS.md` | Phase 7 | Superseded header while preserving legacy content |
| `/home/zaks/bookkeeping/CHANGES.md` | Phase 8 | Mission bookkeeping entry |
| `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | Phase 8 | Mission completion record |

### Files to Create

| Path | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/.codex/AGENTS.md` | Phase 1 | Global Codex operating instructions |
| `/home/zaks/zakops-agent-api/.agents/AGENTS.md` | Phase 1 | Monorepo project instructions |
| `/home/zaks/zakops-backend/.agents/AGENTS.md` | Phase 1 | Backend project instructions |
| `/home/zaks/.codex/skills/` | Phase 2 | User action + knowledge skills root |
| `/home/zaks/zakops-agent-api/.agents/skills/` | Phase 2 | Project skill set root |
| `/home/zaks/.codex/rules/default.rules` | Phase 3 | Structured sandbox rules |
| `/home/zaks/scripts/codex-boot.sh` | Phase 5 | Pre-session diagnostics script |
| `/home/zaks/scripts/codex-stop.sh` | Phase 5 | Post-session validation script |
| `/home/zaks/scripts/codex-notify.sh` | Phase 5 | Notify event logger |
| `/home/zaks/scripts/codex-wrapper.sh` | Phase 5 | Unified boot/launch/stop wrapper |
| `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/` | Phase 0-8 | Artifact root |
| `/home/zaks/bookkeeping/missions/codex-align-001-artifacts/reports/` | Phase 0-8 | Verification and closure reports |

### Files to Read (sources of truth - do NOT modify)

| Path | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/CODEX-ALIGN-001-PLAN.md` | Primary alignment source of truth |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Mission structure standard |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Prompt checklist |
| `/home/zaks/CLAUDE.md` | Existing operational reference content for AGENTS adaptation |
| `/home/zaks/zakops-agent-api/.claude/rules/` | Path-scoped rule source for project AGENTS inlining |
| `/home/zaks/zakops-agent-api/.claude/commands/` | Source for project skill mappings |
| `/home/zaks/zakops-agent-api/tools/infra/validate-mission.sh` | Structural mission validator |

---

## Stop Condition
Stop when AC-1 through AC-9 are satisfied, phase gates P0-P8 are evidenced, and bookkeeping updates are complete. Do not start QA-CODEX-ALIGN-VERIFY-001 from this mission.

---
*End of Mission Prompt - CODEX-ALIGN-001*
