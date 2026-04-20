# ZakOps Claude Code Infrastructure Reference

## Version 4 (Post-CCE2 Current State)

| Field | Value |
|---|---|
| Document Class | Authoritative Infrastructure Reference |
| Version | 4 |
| Date | 2026-02-11 |
| Prior Version | `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-3.docx` |
| Scope | Claude Code runtime configuration, enforcement model, contract surfaces, governance, validation, QA closure |
| As-Of Baseline | Post `CLAUDE-CODE-ENHANCE-002` + `QA-CCE2-VERIFY-001` |

---

## 1. Executive Summary

ZakOps Claude Code infrastructure remains in a hardened, QA-closed operating state and is now updated with the completed CCE enhancement track.

Current platform posture:
- 14 contract surfaces remain registered, validated, and reconciled.
- Hook runtime has expanded from baseline enforcement to lifecycle-aware controls (`PreCompact`, `TaskCompleted`, compact recovery quality assertions).
- Verification workflow for mission prompting is now explicitly persisted and operationalized (automation-first + validation + evidence discipline).
- Claude hook enhancement backlog subset (ENH-1/2/3/4/5/7/10) is closed with independent QA FULL PASS.

Program-level QA closure totals in this stream:
- QA-ITR-VERIFY-001: 45/45 PASS (3 INFO)
- QA-S10-14-VERIFY-001: 51/51 PASS (2 INFO)
- QA-FGH-VERIFY-001: 46/47 PASS (1 INFO)
- QA-CIH-VERIFY-001: 52/52 PASS
- QA-IEU-VERIFY-001: 56/56 PASS
- QA-CCE-VERIFY-001: 41/41 required PASS (+ evidence complete)
- QA-CCE2-VERIFY-001: 31/31 required PASS (+ 5 pre-flight = 36/36 total)

---

## 2. What Changed Since Version 3

Version 3 is now stale in several runtime-critical areas.

Major updates now in force:
- Hook inventory increased from 7 to 10 scripts with live `PreCompact` and `TaskCompleted` enforcement paths.
- User settings hook groups expanded from 4 to 6 (`PreCompact`, `TaskCompleted` added).
- Claude runtime behavior enhancements are deployed and QA-verified:
  - `ENABLE_TOOL_SEARCH=auto:5`
  - `alwaysThinkingEnabled=true`
  - compact snapshot/recovery flow
  - deterministic TaskCompleted fixture mode + machine-readable gate markers
  - configurable snapshot retention (`SNAPSHOT_RETENTION`)
- Monorepo command inventory increased from 15 to 16.
- Mission prompt generation workflow is explicitly persisted in canonical MEMORY.

---

## 3. Configuration Architecture (Current)

### 3.1 Layered Configuration

| Layer | Path | Role |
|---|---|---|
| Root settings | `/root/.claude/settings.json` | Runtime-level root policy and MCP wiring |
| User settings | `/home/zaks/.claude/settings.json` | Active deny/allow policy, hook contracts, MCP declarations |
| Project constitution | `/home/zaks/zakops-agent-api/CLAUDE.md` | Monorepo operating constitution |
| Path-scoped rules | `/home/zaks/zakops-agent-api/.claude/rules/` | Context-specific engineering constraints |
| Commands | `/home/zaks/zakops-agent-api/.claude/commands/` | Operational mission workflows |
| Hooks | `/home/zaks/.claude/hooks/` | Runtime enforcement + diagnostics + sync |
| Skills | `/home/zaks/.claude/skills/` | Reusable knowledge overlays |
| Agents | `/home/zaks/.claude/agents/` | Delegated specialist behavior |
| Persistent memory (canonical) | `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | Cross-session persistent operational memory |
| Persistent memory (symlink alias) | `/root/.claude/projects/-mnt-c-Users-mzsai/memory` | Compatibility alias to canonical memory dir |

### 3.2 Live Inventory Counts

| Component | Count |
|---|---:|
| Commands | 16 |
| Rules | 7 |
| Agents | 3 |
| Skills | 8 |
| Hook scripts | 10 |
| Contract surfaces | 14 |

### 3.3 Settings Snapshot

User settings (`/home/zaks/.claude/settings.json`):
- `deny` rules: 12
- `allow` patterns: 4
- MCP servers: `github`, `playwright`
- Playwright MCP status: `disabled=true`
- Hook groups: `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `PreCompact`, `TaskCompleted`
- Runtime enhancements:
  - `alwaysThinkingEnabled=true`
  - `ENABLE_TOOL_SEARCH=auto:5`

Root settings (`/root/.claude/settings.json`):
- `dangerouslySkipPermissions=true`
- `allow` entries: 140
- `deny` entries: 12
- MCP servers: `crawl4ai-rag`, `gmail`, `playwright`

---

## 4. Runtime Enforcement Model

### 4.1 Effective Enforcement Reality

Permission arrays exist, but practical safety comes from hook contracts + validators + QA verification.

Primary active blockers/gates:
- `pre-edit.sh` for protected file and edit-time policy gates
- `pre-bash.sh` for destructive command restrictions
- `task-completed.sh` for completion-time quality gates
- `stop.sh` for end-of-session validation gates

### 4.2 Stop Hook Gate Contract (Current)

`/home/zaks/.claude/hooks/stop.sh` executes:
- Gate A: `validate-fast`
- Gate B: `validate-contract-surfaces (14 surfaces)`
- Gate E: raw `httpx` usage policy scan with `rg -> grep` fallback and fail-closed scanner behavior

Project detection is hardened:
1. `MONOREPO_ROOT_OVERRIDE`
2. `git rev-parse --show-toplevel`
3. known-path fallback (`/home/zaks/zakops-agent-api`)
4. explicit `SKIP` messaging when root cannot be validated

### 4.3 CCE Runtime Hooks (Now Active)

- `pre-compact.sh`
  - captures pre-compaction snapshots
  - retention controlled by `${SNAPSHOT_RETENTION:-10}`
- `compact-recovery.sh`
  - emits `hookSpecificOutput.additionalContext`
  - includes objective quality assertions/metadata
- `task-completed.sh`
  - supports deterministic fixture mode via `TASK_COMPLETED_TARGETS`
  - emits machine-readable `GATE_RESULT:*` markers
  - preserves exit semantics (`0` allow, `2` block)

### 4.4 Enforcement Flow Diagram

```text
Tool Request
   |
   +--> PreToolUse Hook
           |
           +--> pre-edit.sh (Edit/Write) OR pre-bash.sh (Bash)
                   |
                   +--> PASS: continue execution
                   +--> FAIL: exit 2 (blocked)

Task Completion
   |
   +--> task-completed.sh
           |
           +--> Gate 1 (CRLF)
           +--> Gate 2 (ownership)
           +--> Gate 3 (ts checks when applicable)
           +--> GATE_RESULT markers + exit 0/2

Session Compaction
   |
   +--> PreCompact (pre-compact.sh, async)
   +--> SessionStart matcher="compact" (compact-recovery.sh)

Session Stop
   |
   +--> stop.sh
           |
           +--> Gate A (validate-fast)
           +--> Gate B (validate-contract-surfaces: 14)
           +--> Gate E (raw httpx scan, fail-closed)
           +--> memory-sync + completion path
```

---

## 5. Contract Surface System (14 Total)

### 5.1 Surface Registry

Authoritative registry:
- `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`

System guide mapping:
- `/home/zaks/zakops-agent-api/CLAUDE.md`

Unified validator:
- `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`

### 5.2 Surface Catalog

| Surface | Name | Primary Validator/Command |
|---:|---|---|
| S1 | Backend -> Dashboard TS types | `make sync-types` |
| S2 | Backend -> Agent SDK | `make sync-backend-models` |
| S3 | Agent OpenAPI | `make update-agent-spec` |
| S4 | Agent -> Dashboard TS types | `make sync-agent-types` |
| S5 | RAG -> Backend SDK | `make sync-rag-models` |
| S6 | MCP tool schemas | spec/export discipline |
| S7 | SSE event schema | schema reference + validation |
| S8 | Agent configuration alignment | `make validate-agent-config` |
| S9 | Design system -> Dashboard | `make validate-surface9` |
| S10 | Dependency health | `make validate-surface10` |
| S11 | Env registry | `make validate-surface11` |
| S12 | Error taxonomy | `make validate-surface12` |
| S13 | Test coverage contract | `make validate-surface13` |
| S14 | Performance budget contract | `make validate-surface14` |

### 5.3 Four-Way Reconciliation Baseline

Current authoritative alignment remains 14:
- `contract-surfaces.md`: 14
- `CLAUDE.md` contract table: 14
- `validate-contract-surfaces.sh` declared scope: 14
- `INFRASTRUCTURE_MANIFEST.md` contract entries section: 14

---

## 6. Validation and CI Pipeline (Current)

### 6.1 Local Validation Baseline

Primary local gate:
- `make validate-local`

Current `validate-local` includes:
- type sync targets
- linting
- unified contract surface checks
- agent config validation
- SSE schema validation
- frontend governance validation

### 6.2 Surface and Governance Targets

Key make targets:
- `validate-contract-surfaces`
- `validate-surface9`
- `validate-surface10`
- `validate-surface11`
- `validate-surface12`
- `validate-surface13`
- `validate-surface14`
- `validate-frontend-governance`
- `validate-surfaces-new`
- `validate-hook-contract`
- `validate-enhancements`
- `qa-cce-verify`

### 6.3 CI Gate Expansion

CI includes script-backed gates:
- Gate B: Contract surfaces
- Gate C: Agent config
- Gate D: SSE schema
- Gate E: raw `httpx` usage (`validate-gatee-scan.sh`)
- Gate F: Frontend governance (`validate-frontend-governance.sh`)
- Gate G: CI policy guards (`validate-ci-gatee-policy.sh`, `validate-surface-count-consistency.sh`)
- Gate H: strict Surface 14 (`STRICT=1`)
- Gate I: workflow structure lint

### 6.4 CI/Validation Diagram

```text
Developer Change
   |
   +--> make validate-local
           |
           +--> contract + governance + schema gates

CCE Enhancement Validation
   |
   +--> make qa-cce-verify
           |
           +--> hook contract + compact JSON + fixture harness + integrated runner

CI Workflow
   |
   +--> Gate B -> C -> D -> E -> F -> G -> H -> I
           |
           +--> fail fast on policy/surface/gov drift
```

---

## 7. Frontend Governance and Tooling State

### 7.1 Active Governance Rules

- `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
- `/home/zaks/zakops-agent-api/.claude/rules/accessibility.md`
- `/home/zaks/zakops-agent-api/.claude/rules/component-patterns.md`

Enforced via:
- `validate-surface9.sh`
- `validate-frontend-governance.sh`
- CI gates F/G and local validation chain

### 7.2 Frontend Design Skill

Active local skill:
- `/home/zaks/.claude/skills/frontend-design/SKILL.md`

Tooling policy reference:
- `/home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md`

Operational note:
- Playwright MCP remains intentionally disabled at user settings level.

---

## 8. Mission and QA Closure Ledger

### 8.1 Execution Mission Chain (Completed)

1. `MISSION-INFRA-TRUTH-REPAIR-001`
2. `MISSION-SURFACES-10-14-REGISTER-001`
3. `MISSION-FRONTEND-GOVERNANCE-HARDENING-001`
4. `MISSION-CI-HARDENING-001`
5. `MISSION-INFRA-ENHANCEMENTS-UNIFIED-001`
6. `CLAUDE-CODE-ENHANCE-001`
7. `CLAUDE-CODE-ENHANCE-002`

### 8.2 QA Verification Chain (Completed)

| QA Mission | Result | Remediations |
|---|---|---:|
| QA-ITR-VERIFY-001 | 45/45 PASS, 0 FAIL, 3 INFO | 1 |
| QA-S10-14-VERIFY-001 | 51/51 PASS, 0 FAIL, 2 INFO | 1 |
| QA-FGH-VERIFY-001 | 46/47 PASS, 0 FAIL, 1 INFO | 0 |
| QA-CIH-VERIFY-001 | 52/52 PASS, 0 FAIL, 0 INFO | 0 |
| QA-IEU-VERIFY-001 | 56/56 PASS, 0 FAIL, 0 INFO | 0 |
| QA-CCE-VERIFY-001 | 41/41 required PASS | 0 |
| QA-CCE2-VERIFY-001 | 31/31 required PASS (+ 5 PF = 36/36 total) | 0 |

### 8.3 Evidence Volume (This Stream)

| QA Mission | Evidence Files |
|---|---:|
| QA-ITR-VERIFY-001 | 45 |
| QA-S10-14-VERIFY-001 | 51 |
| QA-FGH-VERIFY-001 | 47 |
| QA-CIH-VERIFY-001 | 52 |
| QA-IEU-VERIFY-001 | 56 |
| QA-CCE-VERIFY-001 | 50 |
| QA-CCE2-VERIFY-001 | 36 |
| **Total** | **337** |

---

## 9. Mission Prompt Automation Workflow (Persistent)

Canonical persistent memory now includes an explicit mission-prompt automation rule set.

Canonical location:
- `/root/.claude/projects/-home-zaks/memory/MEMORY.md`

Workflow required for each new mission prompt:
1. Generate from standard + quickstart:
   - `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`
   - `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md`
2. Validate structure with:
   - `/validate-mission <mission-path>`
3. Run structural integrity checks:
   - phase/AC counts
   - required sections
   - path tables
   - gate presence
   - source-artifact references
4. Add explicit non-applicability notes when a default gate is intentionally excluded.
5. Perform manual final quality pass before handoff.

### 9.1 Quickstart v2.1 Clarifications Now Included

`MISSION-PROMPT-QUICKSTART.md` now explicitly encodes:
- canonical + symlink persistent memory paths
- explicit evidence expectations:
  - execution missions: completion artifacts + checkpoint + CHANGES trace
  - QA missions: `tee` evidence for every PF/VF/XC/ST gate

---

## 10. Current Operational Posture

### 10.1 Stability Summary

Infrastructure remains hardened and reconciled for this mission family:
- contract system + governance checks active
- CI and local gates aligned
- CCE enhancement runtime and QA chain closed
- mission prompt generation workflow standardized and persisted

### 10.2 Residual Non-Blocking Items

- Playwright MCP remains disabled by intentional policy design in user settings.
- Root settings still include broad allow patterns by design; enforcement remains hook/validator-centric.

### 10.3 Risk Rating

For frontend infrastructure and Claude runtime governance scope:
- Risk posture: LOW

---

## 11. Operator Quick Commands

### 11.1 Core Daily Commands

```bash
cd /home/zaks/zakops-agent-api
make validate-local
make validate-contract-surfaces
make validate-frontend-governance
make infra-snapshot
```

### 11.2 Enhanced Validation Suite

```bash
cd /home/zaks/zakops-agent-api
make validate-surfaces-new
make validate-hook-contract
make validate-enhancements
make qa-cce-verify
```

### 11.3 Verification Artifact Roots

- Mission docs: `/home/zaks/bookkeeping/docs/`
- QA verifications: `/home/zaks/bookkeeping/qa-verifications/`

---

## 12. Reference Paths (Authoritative)

| Domain | Path |
|---|---|
| System guide | `/home/zaks/zakops-agent-api/CLAUDE.md` |
| Surface registry | `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` |
| Unified validator | `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` |
| Manifest | `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md` |
| User settings | `/home/zaks/.claude/settings.json` |
| Root settings | `/root/.claude/settings.json` |
| Hook scripts | `/home/zaks/.claude/hooks/` |
| CI workflow | `/home/zaks/zakops-agent-api/.github/workflows/ci.yml` |
| Frontend policy | `/home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md` |
| Audit closure addendum | `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT-CLOSURE-ADDENDUM-2026-02-11.md` |
| CCE v1 mission | `/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-001.md` |
| CCE v2 mission | `/home/zaks/bookkeeping/missions/CLAUDE-CODE-ENHANCE-002.md` |
| CCE v1 QA scorecard | `/home/zaks/bookkeeping/qa-verifications/QA-CCE-VERIFY-001/SCORECARD.md` |
| CCE v2 QA scorecard | `/home/zaks/bookkeeping/qa-verifications/QA-CCE2-VERIFY-001/SCORECARD.md` |

---

## 13. Versioning Note

Version 4 supersedes Version 3 as the operational reference for current ZakOps Claude Code infrastructure state.

Archived prior versions:
- `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-2.md`
- `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-2.docx`
- `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-3.md`
- `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-3.docx`

---

*End of Infrastructure Reference — Version 4*
