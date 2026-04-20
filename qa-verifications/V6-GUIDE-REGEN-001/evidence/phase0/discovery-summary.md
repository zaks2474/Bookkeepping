# V6-GUIDE-REGEN-001 — Phase 0 Discovery Summary
## Date: 2026-02-09

### Configuration State (post-Mission 1)
- **settings.json**: 97 allow rules, 12 deny rules, 2 MCP servers (gmail, filesystem), dangerouslySkipPermissions=true
- **Hooks**: 5 scripts in `~/.claude/hooks/` (memory-sync.sh, post-edit.sh, pre-bash.sh, pre-edit.sh, stop.sh)
- **Rules**: 4 files in `.claude/rules/` (agent-tools.md, backend-api.md, contract-surfaces.md, dashboard-types.md)
- **Commands**: 13 files in `.claude/commands/`
- **Agents**: 3 definitions in `~/.claude/agents/` (arch-reviewer.md [opus], contract-guardian.md [sonnet], test-engineer.md [sonnet])
- **CLAUDE.md root**: `/home/zaks/CLAUDE.md` — 64 lines
- **CLAUDE.md monorepo**: `/home/zaks/zakops-agent-api/CLAUDE.md` — 143 lines (ceiling 150, 7 spare)
- **MEMORY.md**: Active copy at `/root/.claude/projects/-home-zaks/memory/MEMORY.md` — Deal Integrity recorded, sentinel tags present

### TriPass State (post-Mission 2)
- **Orchestrator**: `/home/zaks/zakops-agent-api/tools/tripass/tripass.sh` — 1036 lines, version 1.0.0
- **SOP**: `/home/zaks/bookkeeping/docs/TRIPASS_SOP.md` — 206 lines
- **Templates**: 4 files in `_tripass_templates/` (pass1.md, pass2.md, pass3.md, pass4_metaqa.md)
- **Completed runs**: 1 (TP-20260209-211737, generate-only mode)
- **Makefile targets**: 4 (tripass-init, tripass-run, tripass-status, tripass-gates)
- **stop.sh**: Has tripass lockfile awareness
- **memory-sync.sh**: Gathers tripass run count + latest run ID
- **CHANGES.md**: Has TriPass entries
- **Phantom references**: `/mnt/skills/` found at lines 35, 161-163, 177-181, 195, 629-631

### Contract Surfaces State
- All 8 surfaces present and documented in `.claude/rules/contract-surfaces.md`
- Spec files: zakops-api.json, agent-api.json, rag-api.json, agent-events.schema.json, tool-schemas.json, runtime.topology.json
- Generated files: api-types.generated.ts (163KB), agent-api-types.generated.ts (67KB), backend_models.py (609L), rag_models.py
- Bridge files: types/api.ts (377L), types/agent-api.ts (92L)

### Dashboard Patterns (Surface 9 discovery)
- **Promise.allSettled**: Used in `deals/[id]/page.tsx` (lines 124-133) with typed empty fallbacks
- **console.warn**: 6 occurrences for degradation paths in deals/[id]/page.tsx
- **PIPELINE_STAGES**: Referenced in execution-contracts.ts and bridge files
- **Middleware proxy**: Active for `/api/*` routes via Next.js middleware
- **Import pattern**: `from '@/lib/api'` used in 8 page files; `from '@/types/api'` for bridge imports
- **API client**: Centralized at `apps/dashboard/src/lib/api.ts` with Zod validation
- **55 total TS/TSX files** in dashboard app directory

### Infrastructure
- All 8 ports listening: 3003, 8091, 8095, 8052, 9100, 3000, 8000, 5432
- Decommissioned ports NOT listening: 5435, 8090
- Docker: backend healthy, redis healthy, postgres healthy, agent-api healthy

### Discrepancies
- **Phantom plugin**: `/mnt/skills/` references in tripass.sh (6+ locations), SOP, possibly templates — addressed in Phase 2
- **MEMORY.md missing gates**: TriPass section lacks T-1 through T-6 gate names — addressed in Phase 1 (ENH-8)
- No other surprises. All systems nominal.

### Verdict: CLEAR TO PROCEED
