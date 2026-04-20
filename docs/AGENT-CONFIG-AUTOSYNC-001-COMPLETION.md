# AGENT-CONFIG-AUTOSYNC-001 — Completion Report
## Date: 2026-02-15
## Status: COMPLETE — All 9 ACs satisfied

---

## Acceptance Criteria Evidence Map

| AC | Description | Evidence | Result |
|----|-------------|----------|--------|
| AC-1 | Markers present in all 3 target files | `grep -c "AUTOSYNC:surface_table" <file>` returns 2 for all 3 files | PASS |
| AC-2 | Current drift fixed (14 → 17) | All 3 files show "17 Total" or "17 Contract" in headings; all list S1-S17 | PASS |
| AC-3 | Sync script exists and runs clean | `/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh` exits 0 | PASS |
| AC-4 | Idempotency | Second run produces zero file changes (verified with diff) | PASS |
| AC-5 | Makefile integration | `make sync-agent-configs` target exists; included in `sync-all-types` dep chain | PASS |
| AC-6 | Stop hook integration | `stop.sh` calls sync script with 5s timeout, non-fatal error handling | PASS |
| AC-7 | Boot diagnostic CHECK 7 | `session-start.sh` includes agent config surface count consistency check (WARN, not FAIL) | PASS |
| AC-8 | No regressions | `make validate-local` passes | PASS |
| AC-9 | Bookkeeping | CHANGES.md updated with full entry | PASS |

---

## Problem Solved

Contract surface tables in agent config files (Codex AGENTS.md, monorepo .agents/AGENTS.md, GEMINI.md) had drifted 3 times previously (9→14, 14→16, 14→17). Each drift required manual patching of 3+ files. This mission built permanent automation with 3 integration points:

1. **Manual:** `make sync-agent-configs` (or included in `make sync-all-types`)
2. **Session end:** stop.sh auto-syncs (non-fatal, 5s timeout)
3. **Session start:** CHECK 7 detects drift (WARN, not FAIL — stop hook auto-fixes)

Future surface additions to `contract-surfaces.md` will automatically propagate to all 3 agent config files.

---

## Files Modified

| File | Change | Phase |
|------|--------|-------|
| `/home/zaks/.codex/AGENTS.md` | Added AUTOSYNC markers, updated 14→17 surface table | P1 |
| `/home/zaks/zakops-agent-api/.agents/AGENTS.md` | Added AUTOSYNC markers around summary table, updated 14→17, preserved detailed S1-8 descriptions outside markers | P1 |
| `/home/zaks/zakops-agent-api/GEMINI.md` | Added AUTOSYNC markers, updated 14→17 surface table (5-col Gemini format) | P1 |
| `/home/zaks/zakops-agent-api/Makefile` | Added `sync-agent-configs` target + added to `sync-all-types` dep chain + .PHONY | P3 |
| `/home/zaks/.claude/hooks/stop.sh` | Added agent-config-sync block after memory-sync (non-fatal, 5s timeout) | P3 |
| `/home/zaks/.claude/hooks/session-start.sh` | Added CHECK 7: agent config surface count consistency (3 files vs canonical) | P3 |
| `/home/zaks/bookkeeping/CHANGES.md` | Mission closure entry | P4 |

## Files Created

| File | Purpose | Phase |
|------|---------|-------|
| `/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh` | Automated sync script — parses canonical source, generates tables, replaces between markers | P2 |
| `/home/zaks/bookkeeping/docs/AGENT-CONFIG-AUTOSYNC-001-MISSION.md` | Formal mission prompt (v2.3 standard) | Pre-execution |
| `/home/zaks/bookkeeping/docs/AGENT-CONFIG-AUTOSYNC-001-COMPLETION.md` | This report | P4 |

---

## Bug Fix During Execution

**Validation parser bug (Phase 2):** Surfaces 9-17 initially showed `bash tools` instead of `make validate-surfaceN` in generated tables.

- **Root cause:** The canonical source for Surface 9+ has `**Validation:** \`bash tools/infra/validate-surface9.sh\`` (no `make` variant). The regex captured the full bash path, then `sed 's/ *\/.*$//'` stripped everything after the first `/`, leaving just `bash tools`.
- **Fix:** Two-step check — prefer `make` commands first (`\`(make[^\`]+)\``), fall back to constructing `make validate-surface${current_num}` when only a bash path is available.

---

## Architecture Decisions

1. **Marker scope for .agents/AGENTS.md:** Detailed S1-8 descriptions (60+ lines of endpoint rules, path guidance, etc.) are kept OUTSIDE markers. Only a compact 17-row summary table is inside markers. This prevents the sync script from needing to regenerate complex custom content.

2. **Two table formats:** Standard 3-column for Codex configs (machine-readable), Gemini 5-column with boundary/artifact data (richer context for Gemini's forensic role). The sync script detects format by checking for `Boundary` in the header row.

3. **WARN not FAIL for CHECK 7:** Boot diagnostic reports drift but doesn't block session start, because the stop hook auto-fixes drift. This avoids false-positive session blocks when drift is expected (e.g., right after adding a new surface to canonical source).

---

## Verification Results (Phase 4)

| Gate | Command | Result |
|------|---------|--------|
| Script runs clean | `bash tools/infra/sync-agent-configs.sh` | Exit 0 |
| All targets show 17 | `grep -c "Surface" <3 files>` | 17 each |
| Markers present | `grep -c "AUTOSYNC:surface_table" <3 files>` | 2 each |
| Idempotent | Run twice, diff second run | Zero changes |
| Makefile integration | `make sync-agent-configs` | Success |
| No regressions | `make validate-local` | PASS |
| Boot diagnostic | CHECK 7 in session-start.sh | 3/3 match canonical=17 |

---

## Boot Diagnostics After Mission

```
CHECK 1: PASS — Memory integrity OK
CHECK 2: PASS — Surface count consistent (17 everywhere)
CHECK 3: PASS — Sentinel freshness OK (4/4 current)
CHECK 4: PASS — Generated files present (4/4)
CHECK 5: PASS — Codegen freshness OK
CHECK 6: PASS — Constraint registry OK (10/10 verified)
CHECK 7: PASS — Agent config surface count OK (3/3 match canonical=17)
```

---
*End of Completion Report — AGENT-CONFIG-AUTOSYNC-001*
