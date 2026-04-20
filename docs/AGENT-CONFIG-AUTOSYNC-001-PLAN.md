# AGENT-CONFIG-AUTOSYNC-001: Permanent Agent Config Sync Automation

## Context

Every time a contract surface is added (14→17 most recently), 7+ agent config files (Codex AGENTS.md, Gemini AGENTS.md, repo-level AGENTS.md, GEMINI.md) fall out of sync. This has happened 3 times already. The fix is always manual — read the canonical source, patch each file. This plan eliminates that forever.

**Canonical source of truth:** `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`

**Stale files found today (say 14, should say 17):**
1. `/home/zaks/.codex/AGENTS.md` (line 123)
2. `/home/zaks/zakops-agent-api/.agents/AGENTS.md` (line 30)
3. `/home/zaks/zakops-agent-api/GEMINI.md` (line 11)

**Files without surface sections (no update needed):**
- `/home/zaks/.gemini/AGENTS.md` — references MEMORY.md instead
- `/home/zaks/zakops-backend/.agents/AGENTS.md` — backend-specific, no surfaces
- `/home/zaks/Zaks-llm/AGENTS.md` — generic template, no surfaces
- `/home/zaks/zakops-agent-api/docs/standards/AGENTS.md` — generic coding standards

---

## Design: Marker-Based Section Replacement

**Pattern:** Reuse the proven `<!-- AUTOSYNC:key -->` marker system from `memory-sync.sh`.

Each target file gets a pair of markers around its surface section:
```markdown
<!-- AUTOSYNC:surface_table_start -->
(generated content here)
<!-- AUTOSYNC:surface_table_end -->
```

A sync script:
1. Reads the canonical source (`contract-surfaces.md`)
2. Extracts the surface count and generates a compact table
3. Finds all files with the markers
4. Replaces content between markers with the fresh table
5. Also updates any `(N Total)` heading above the markers

**Why markers, not full-file regeneration:** Each AGENTS.md file has unique content (WSL hazards in Codex, TriPass role in Gemini, etc.). Only the surface table section should be auto-managed.

---

## Phase 1: Add Markers + Fix Current Drift (3 files)

### 1A: `/home/zaks/.codex/AGENTS.md`

Replace lines 123-141 (surface section) with:
```markdown
## Contract Surfaces (17 Total)

<!-- AUTOSYNC:surface_table_start -->
| # | Surface | Sync Command |
|---|---------|-------------|
| 1 | Backend → Dashboard | `make sync-types` |
| 2 | Backend → Agent SDK | `make sync-backend-models` |
| 3 | Agent OpenAPI | `make update-agent-spec` |
| 4 | Agent → Dashboard | `make sync-agent-types` |
| 5 | RAG → Backend SDK | `make sync-rag-models` |
| 6 | MCP Tools | (export from tool_schemas.py) |
| 7 | SSE Events | (reference schema) |
| 8 | Agent Config | `make validate-agent-config` |
| 9 | Design System → Dashboard | `make validate-surface9` |
| 10 | Dependency Health | `make validate-surface10` |
| 11 | Env Registry | `make validate-surface11` |
| 12 | Error Taxonomy | `make validate-surface12` |
| 13 | Test Coverage | `make validate-surface13` |
| 14 | Performance Budget | `make validate-surface14` |
| 15 | MCP Bridge Tool Interface | `make validate-surface15` |
| 16 | Email Triage Injection | `make validate-surface16` |
| 17 | Dashboard Route Coverage | `make validate-surface17` |
<!-- AUTOSYNC:surface_table_end -->
```

### 1B: `/home/zaks/zakops-agent-api/.agents/AGENTS.md`

Replace lines 30-78 (detailed surface section) with:
- Keep the `## Contract Surfaces (17 Total)` heading
- Add markers around the detail + table
- Update surfaces 1-8 detail sections (keep existing format)
- Expand "Surfaces 9-14" table to "Surfaces 9-17"
- Add S15, S16, S17 rows

### 1C: `/home/zaks/zakops-agent-api/GEMINI.md`

Replace lines 11-28 (surface table) with:
- Update heading from "14" to "17"
- Add markers around the table
- Add S15, S16, S17 rows matching the existing column format (`# | Surface | Boundary | Key Artifacts | Validation`)

---

## Phase 2: Create `sync-agent-configs.sh`

**File:** `/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh`

**Logic:**
```
1. Parse canonical source: contract-surfaces.md
   - Extract surface count (grep "## The N Contract Surfaces")
   - Extract compact table: for each "### Surface N:" line, build | N | name | command |

2. Define target files array:
   TARGETS=(
     "/home/zaks/.codex/AGENTS.md"
     "/home/zaks/zakops-agent-api/.agents/AGENTS.md"
     "/home/zaks/zakops-agent-api/GEMINI.md"
   )

3. For each target:
   a. Verify markers exist (<!-- AUTOSYNC:surface_table_start/end -->)
   b. Generate the appropriate table format for this file
   c. Replace content between markers with generated table
   d. Update "(N Total)" in the heading above the markers

4. Report: "Synced N files, surface count: 17"
```

**Table generation:** The script reads `contract-surfaces.md` and generates a compact 3-column table (same format used in Codex AGENTS.md — `# | Surface | Sync Command`). For GEMINI.md which uses a 5-column format, generate a GEMINI-specific variant.

**Approach:** Two table formats:
- **Standard** (Codex, .agents): `| # | Surface | Sync Command |`
- **Gemini** (GEMINI.md): `| # | Surface | Boundary | Key Artifacts | Validation |`

The script detects which format to use by checking the header row between the markers.

---

## Phase 3: Integrate into Automation

### 3A: Makefile Target

```makefile
sync-agent-configs: ## Sync contract surface tables to all agent config files
	@echo "$(CYAN)=== Sync Agent Configs ===$(RESET)"
	@bash tools/infra/sync-agent-configs.sh
	@echo "$(GREEN)Agent configs synced$(RESET)"
```

Add to `sync-all-types` dependency chain:
```makefile
sync-all-types: sync-types sync-backend-models sync-agent-types sync-rag-models sync-agent-configs
```

### 3B: Stop Hook Integration

In `/home/zaks/.claude/hooks/stop.sh`, add after memory-sync (line 140):
```bash
# ── Agent Config Sync (non-fatal, 5s timeout) ──
AGENT_SYNC="/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh"
if [ -f "$AGENT_SYNC" ] && [ -x "$AGENT_SYNC" ]; then
  echo "Running agent-config-sync..."
  timeout 5 bash "$AGENT_SYNC" 2>&1 || {
    echo "WARNING: agent-config-sync failed (non-fatal)."
  }
fi
```

### 3C: Boot Diagnostic Enhancement

In `/home/zaks/.claude/hooks/session-start.sh`, add a CHECK 7:
```
CHECK 7: Agent config surface count consistency
  - For each target file with markers, extract count from heading
  - Compare to canonical count
  - WARN if mismatch (not FAIL — stop hook will auto-fix)
```

---

## Phase 4: Verification

### Automated Gates
```bash
# 1. Script runs clean
bash tools/infra/sync-agent-configs.sh

# 2. All targets show correct count
grep -c "17 Total\|17 Contract" /home/zaks/.codex/AGENTS.md \
  /home/zaks/zakops-agent-api/.agents/AGENTS.md \
  /home/zaks/zakops-agent-api/GEMINI.md

# 3. Markers present in all targets
grep -c "AUTOSYNC:surface_table" /home/zaks/.codex/AGENTS.md \
  /home/zaks/zakops-agent-api/.agents/AGENTS.md \
  /home/zaks/zakops-agent-api/GEMINI.md

# 4. Idempotency: running twice produces no diff
bash tools/infra/sync-agent-configs.sh
bash tools/infra/sync-agent-configs.sh
# No changes on second run

# 5. make sync-all-types includes agent configs
make sync-all-types  # should call sync-agent-configs

# 6. Simulate surface addition: temporarily add "### Surface 18: Test" to
#    contract-surfaces.md, run sync, verify all files show 18
```

### Manual Verification
- Restart session → boot diagnostics CHECK 7 passes
- Session end → stop.sh runs sync without error

---

## Files Summary

| File | Action |
|------|--------|
| `/home/zaks/.codex/AGENTS.md` | EDIT — add markers, update 14→17, add S15-17 |
| `/home/zaks/zakops-agent-api/.agents/AGENTS.md` | EDIT — add markers, update 14→17, add S15-17 |
| `/home/zaks/zakops-agent-api/GEMINI.md` | EDIT — add markers, update 14→17, add S15-17 |
| `/home/zaks/zakops-agent-api/tools/infra/sync-agent-configs.sh` | NEW — sync script |
| `/home/zaks/zakops-agent-api/Makefile` | EDIT — add `sync-agent-configs` target + dependency |
| `/home/zaks/.claude/hooks/stop.sh` | EDIT — add sync call after memory-sync |
| `/home/zaks/.claude/hooks/session-start.sh` | EDIT — add CHECK 7 |
| `/home/zaks/bookkeeping/CHANGES.md` | Record changes |

---

## Why This Works Permanently

1. **Single source of truth**: `contract-surfaces.md` is already maintained (it's a `.claude/rules/` file, auto-loaded for contract work)
2. **Markers make it safe**: Only the table section is replaced — custom content around it is untouched
3. **Three integration points**: manual (`make sync-agent-configs`), session end (stop hook), and session start (boot diagnostic warns on drift)
4. **Idempotent**: Running twice produces no diff — safe to run in any context
5. **New surface = automatic propagation**: Add `### Surface 18: Foo` to `contract-surfaces.md` → next session end auto-updates all agent files
