# MISSION: AGENT-CONFIG-AUTOSYNC-001
## Permanent Agent Config Sync Automation
## Date: 2026-02-15
## Classification: Infrastructure Automation
## Prerequisite: None (standalone)
## Successor: MONOREPO-CONSOLIDATION-001 (benefits from this automation being in place)

---

## Mission Objective

Build a permanent automation system that keeps contract surface tables synchronized across all agent configuration files (Codex AGENTS.md, monorepo .agents/AGENTS.md, GEMINI.md) whenever the canonical source (`contract-surfaces.md`) changes.

This is a BUILD mission, not a fix mission. The immediate drift (14 → 17) will be corrected as a side effect of adding markers, but the primary deliverable is the automation that prevents future drift.

**Source material:**
- Investigation: `/home/zaks/bookkeeping/docs/AGENT-CONFIG-AUTOSYNC-001-PLAN.md` (design plan)
- Canonical source: `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` (17 surfaces)
- Stale files (say 14, should say 17):
  1. `/home/zaks/.codex/AGENTS.md` (line 123)
  2. `/home/zaks/zakops-agent-api/.agents/AGENTS.md` (line 30)
  3. `/home/zaks/zakops-agent-api/GEMINI.md` (line 11)

**What this is NOT:** This mission does not modify contract surfaces themselves, does not touch the dashboard/backend/agent code, and does not create new contract surfaces.

---

## Context

Contract surface tables in agent config files have drifted 3 times already (9→14, 14→16, 14→17). Each time required manual patching of 3+ files. The root cause is that no automation exists to propagate changes from the canonical source (`contract-surfaces.md`) to downstream config files.

The proven `<!-- AUTOSYNC:key -->` marker pattern from `memory-sync.sh` will be reused. Each target file gets start/end markers around its surface table section. A script replaces content between markers with freshly generated tables from the canonical source.

---

## Glossary

| Term | Definition |
|------|-----------|
| AUTOSYNC markers | `<!-- AUTOSYNC:surface_table_start -->` / `<!-- AUTOSYNC:surface_table_end -->` bracket pairs around auto-managed content |
| Canonical source | `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` — the single source of truth for all surface definitions |
| Standard format | 3-column table: `# | Surface | Sync Command` (used by Codex AGENTS.md and .agents/AGENTS.md) |
| Gemini format | 5-column table: `# | Surface | Boundary | Key Artifacts | Validation` (used by GEMINI.md) |

---

## Architectural Constraints

Per standing rules in CLAUDE.md and MEMORY.md:
- **Contract surface discipline** — `contract-surfaces.md` is the single source of truth; all other references are derived
- **WSL safety** — CRLF stripping on .sh files, ownership fix on files under /home/zaks/
- **Hook architecture** — stop.sh runs validation gates; new additions must be non-fatal with timeout
- **Idempotency** — automation scripts must produce no diff when run twice consecutively

---

## Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | sed marker replacement corrupts file content outside markers | MEDIUM | Agent configs become unparseable | Phase 2 script uses line-range replacement (delete between markers, insert fresh content), verified by idempotency gate in Phase 3 |
| 2 | CRLF in sync script breaks when run from stop hook | HIGH | Silent failure every session end | WSL safety checklist in Phase 2 (sed -i 's/\r$//' + chmod +x) |
| 3 | Canonical source format changes (heading pattern) break parser | LOW | Script silently extracts 0 surfaces | Script validates extracted count > 0 before writing; fails loudly if parse returns empty |
| 4 | Heading count "(N Total)" update regex matches wrong line | MEDIUM | Wrong heading updated in files with multiple "(N Total)" strings | Regex anchored to within 5 lines above start marker, not global search |

---

## Phase 0 — Discovery & Baseline
**Complexity:** S
**Estimated touch points:** 0 (read-only)

**Purpose:** Verify current state matches expectations before making changes.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Verify canonical source has 17 surfaces** — `grep -c "### Surface" /home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` must return 17
- P0-02: **Verify drift in target files** — confirm all 3 targets show 14, not 17
- P0-03: **Baseline validation** — `make validate-local` passes before any changes

### Gate P0
- Canonical source confirms 17 surfaces
- All 3 target files confirmed stale (showing 14)
- `make validate-local` passes at baseline

---

## Phase 1 — Add Markers + Fix Current Drift (3 files)
**Complexity:** M
**Estimated touch points:** 3 files

**Purpose:** Insert AUTOSYNC markers into all target files and update surface tables from 14 to 17.

### Blast Radius
- **Services affected:** None (config files only, not runtime code)
- **Pages affected:** None
- **Downstream consumers:** Codex CLI, Gemini CLI, Codex project agents — they read these files at session start

### Tasks
- P1-01: **Edit `/home/zaks/.codex/AGENTS.md`** — Replace lines 123-141 (surface section) with: updated heading "(17 Total)", start/end markers, 17-row standard-format table
  - **Checkpoint:** File parses clean, markers present, heading says 17
- P1-02: **Edit `/home/zaks/zakops-agent-api/.agents/AGENTS.md`** — Replace lines 30-78 (detailed surface section) with: updated heading "(17 Total)", start/end markers around the surface detail block, expanded table to include S15-S17
  - **Checkpoint:** File parses clean, markers present, heading says 17
- P1-03: **Edit `/home/zaks/zakops-agent-api/GEMINI.md`** — Replace lines 11-28 (surface table) with: updated heading to 17, start/end markers, 17-row Gemini-format table (5 columns)
  - **Checkpoint:** File parses clean, markers present, heading says 17

### Rollback Plan
1. `git checkout -- .agents/AGENTS.md GEMINI.md` for monorepo files
2. Restore `/home/zaks/.codex/AGENTS.md` from manual backup

### Gate P1
- All 3 files contain `<!-- AUTOSYNC:surface_table_start -->` and `<!-- AUTOSYNC:surface_table_end -->`
- All 3 files show "17 Total" or "17 Contract" in heading
- All 3 files list surfaces 1-17

---

## Phase 2 — Create sync-agent-configs.sh
**Complexity:** M
**Estimated touch points:** 1 new file

**Purpose:** Build the automated sync script that reads canonical source and updates all target files.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None
- **Downstream consumers:** Makefile, stop hook (Phase 3)

### Tasks
- P2-01: **Create `/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh`** with logic:
  1. Parse canonical source — extract surface count from `## The N Contract Surfaces` heading
  2. For each `### Surface N:` line, extract number, name, and validation command
  3. Generate standard 3-column table and Gemini 5-column table
  4. For each target file: verify markers exist, detect format (standard vs Gemini by checking header row), replace content between markers, update "(N Total)" heading
  5. Report: "Synced N files, surface count: M"
  6. Exit 0 on success, exit 1 on any error
  - **Checkpoint:** Script runs without error: `bash /home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh`
- P2-02: **WSL safety** — `sed -i 's/\r$//' /home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh && chmod +x /home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh && sudo chown zaks:zaks /home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh`
- P2-03: **Idempotency test** — Run script twice, confirm no diff on second run

### Decision Tree
- **IF** canonical source heading format changed → update grep pattern to match new format
- **IF** a target file lacks markers → script prints ERROR and skips that file (doesn't exit, continues to next)

### Rollback Plan
1. `rm /home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh`

### Gate P2
- Script runs clean (exit 0)
- All 3 target files show correct count after run
- Second run produces zero changes (idempotent)
- Script handles missing-marker case gracefully

---

## Phase 3 — Integrate into Automation
**Complexity:** M
**Estimated touch points:** 3 files

**Purpose:** Wire the sync script into the Makefile, stop hook, and boot diagnostics so it runs automatically.

### Blast Radius
- **Services affected:** None directly; affects session lifecycle hooks
- **Pages affected:** None
- **Downstream consumers:** All Claude Code sessions (stop hook), `make sync-all-types` callers

### Tasks
- P3-01: **Add Makefile target** — Add `sync-agent-configs` target to `/home/zaks/zakops-agent-api/Makefile` and add it to `sync-all-types` dependency chain
  - **Checkpoint:** `make sync-agent-configs` runs successfully
- P3-02: **Add stop hook integration** — Edit `/home/zaks/.claude/hooks/stop.sh` to call `sync-agent-configs.sh` after memory-sync (non-fatal, 5s timeout)
  - **Checkpoint:** stop.sh parses without syntax error
- P3-03: **Add boot diagnostic CHECK 7** — Edit `/home/zaks/.claude/hooks/session-start.sh` to check agent config surface count consistency (WARN on mismatch, not FAIL)
  - **Checkpoint:** session-start.sh parses without syntax error

### Rollback Plan
1. Revert Makefile changes: `git checkout -- Makefile`
2. Revert stop.sh: remove the agent-config-sync block
3. Revert session-start.sh: remove CHECK 7 block

### Gate P3
- `make sync-agent-configs` completes successfully
- `make sync-all-types` includes `sync-agent-configs` in its execution
- stop.sh has no bash syntax errors: `bash -n /home/zaks/.claude/hooks/stop.sh`
- session-start.sh has no bash syntax errors: `bash -n /home/zaks/.claude/hooks/session-start.sh`

---

## Phase 4 — Final Verification
**Complexity:** S
**Estimated touch points:** 1 file (CHANGES.md)

**Purpose:** Run all verification gates and record changes.

### Blast Radius
- **Services affected:** None
- **Pages affected:** None

### Tasks
- P4-01: **Run full verification suite:**
  1. `bash /home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh` — clean run
  2. Verify all 3 targets show correct count (17)
  3. Verify markers present in all 3 targets
  4. Idempotency: run twice, no diff
  5. `make sync-all-types` succeeds (includes agent configs)
- P4-02: **Record in CHANGES.md** — `/home/zaks/bookkeeping/CHANGES.md`

### Gate P4
- All verification checks pass
- CHANGES.md updated

---

## Dependency Graph

Phases execute sequentially: 0 → 1 → 2 → 3 → 4 → Final.

---

## Acceptance Criteria

### AC-1: Markers Present
All 3 target files contain `<!-- AUTOSYNC:surface_table_start -->` and `<!-- AUTOSYNC:surface_table_end -->` markers.

### AC-2: Current Drift Fixed
All 3 target files show 17 surfaces (not 14).

### AC-3: Sync Script Exists and Runs Clean
`/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh` exists, is executable, and exits 0.

### AC-4: Idempotency
Running the sync script twice produces zero file changes on the second run.

### AC-5: Makefile Integration
`make sync-agent-configs` target exists and is included in `sync-all-types` dependency chain.

### AC-6: Stop Hook Integration
`/home/zaks/.claude/hooks/stop.sh` calls `sync-agent-configs.sh` with timeout and non-fatal error handling.

### AC-7: Boot Diagnostic CHECK 7
`/home/zaks/.claude/hooks/session-start.sh` includes a surface count consistency check for agent config files.

### AC-8: No Regressions
`make validate-local` passes, no existing functionality broken.

### AC-9: Bookkeeping
CHANGES.md updated with all changes.

---

## Guardrails

1. **Scope fence:** Do not modify contract surfaces themselves — only sync the tables to agent config files.
2. **Generated file protection:** Per standing deny rules — do not edit *.generated.ts or *_models.py.
3. **Hook safety:** Stop hook additions must be non-fatal (|| { echo WARNING }) with timeout. Never block session end on agent config sync failure.
4. **Boot diagnostic safety:** CHECK 7 must be WARN, not FAIL — the stop hook auto-fixes drift, so boot only needs to report.
5. **WSL safety:** CRLF strip and ownership fix on any new .sh files.
6. **Marker integrity:** Never delete or modify content OUTSIDE the start/end markers — each file has unique custom content that must be preserved.
7. **Canonical source is read-only:** The sync script reads `contract-surfaces.md` but never writes to it.

---

## Executor Self-Check Prompts

### After Phase 0 (Discovery):
- [ ] "Did I verify the canonical source has exactly 17 surfaces?"
- [ ] "Did I confirm all 3 target files are actually stale (showing 14)?"

### After Phase 1 (Markers):
- [ ] "Do all 3 files have both start AND end markers?"
- [ ] "Did I preserve all custom content outside the markers?"
- [ ] "Does the Gemini format use 5 columns, not 3?"

### After Phase 2 (Script):
- [ ] "Did I strip CRLF from the new .sh file?"
- [ ] "Did I fix ownership (chown zaks:zaks)?"
- [ ] "Is the script idempotent (second run = no changes)?"
- [ ] "Does the script fail gracefully if a target file lacks markers?"

### Before marking COMPLETE:
- [ ] "Does `make validate-local` pass right now?"
- [ ] "Did I update CHANGES.md?"

---

## File Paths Reference

### Files to Modify
| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/.codex/AGENTS.md` | P1 | Add markers, update 14→17, add S15-17 |
| `/home/zaks/zakops-agent-api/.agents/AGENTS.md` | P1 | Add markers, update 14→17, add S15-17 |
| `/home/zaks/zakops-agent-api/GEMINI.md` | P1 | Add markers, update 14→17, add S15-17 |
| `/home/zaks/zakops-agent-api/Makefile` | P3 | Add sync-agent-configs target + sync-all-types dep |
| `/home/zaks/.claude/hooks/stop.sh` | P3 | Add sync call after memory-sync |
| `/home/zaks/.claude/hooks/session-start.sh` | P3 | Add CHECK 7 |
| `/home/zaks/bookkeeping/CHANGES.md` | P4 | Record changes |

### Files to Create
| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh` | P2 | Automated sync script |

### Files to Read (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` | Canonical source for surface definitions |
| `/home/zaks/bookkeeping/docs/AGENT-CONFIG-AUTOSYNC-001-PLAN.md` | Design plan |

---

## Crash Recovery (per IA-2)

If resuming after a crash, run these commands to determine current state:
1. `grep -c "AUTOSYNC:surface_table" /home/zaks/.codex/AGENTS.md /home/zaks/zakops-agent-api/.agents/AGENTS.md /home/zaks/zakops-agent-api/GEMINI.md` — if all show 2, Phase 1 is complete
2. `ls -la /home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh` — if exists, Phase 2 is complete
3. `grep -c "sync-agent-configs" /home/zaks/zakops-agent-api/Makefile` — if >0, Phase 3A is complete
4. `grep -c "agent-config-sync" /home/zaks/.claude/hooks/stop.sh` — if >0, Phase 3B is complete

---

## Stop Condition

Mission is DONE when:
- All 9 AC pass
- `make validate-local` passes
- All changes recorded in CHANGES.md
- Sync script is idempotent (proven by double-run test)

Do NOT proceed to MONOREPO-CONSOLIDATION-001 — that is a separate mission with its own plan.

---
*End of Mission Prompt — AGENT-CONFIG-AUTOSYNC-001*
