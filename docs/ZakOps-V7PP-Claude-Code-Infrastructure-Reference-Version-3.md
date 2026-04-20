# ZakOps Claude Code Infrastructure Reference

## Version 3 (Post-Hardening Current State)

| Field | Value |
|---|---|
| Document Class | Authoritative Infrastructure Reference |
| Version | 3 |
| Date | 2026-02-11 |
| Prior Version | `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-2.docx` |
| Scope | Claude Code runtime configuration, enforcement model, contract surfaces, governance, validation, QA closure |
| As-Of Baseline | Post mission chain through `INFRA-ENHANCEMENTS-UNIFIED-001` + `QA-IEU-VERIFY-001` |

---

## 1. Executive Summary

ZakOps Claude Code infrastructure has moved from the earlier V7PP consolidation state to a hardened, QA-closed operating baseline.

Current platform posture:
- 14 contract surfaces are registered, validated, and reconciled.
- Hook, CI, and governance enforcement has been hardened and then independently QA-verified.
- Enhancement layer is implemented (schema checks, test harnesses, drift guards, automation utilities).
- Mission family closure is complete with no open FAIL-class findings in the frontend infrastructure stream.

Program-level QA closure totals:
- QA-ITR-VERIFY-001: 45/45 PASS
- QA-S10-14-VERIFY-001: 51/51 PASS
- QA-FGH-VERIFY-001: 46/47 PASS, 1 INFO
- QA-CIH-VERIFY-001: 52/52 PASS
- QA-IEU-VERIFY-001: 56/56 PASS

---

## 2. What Changed Since Version 2

Version 2 is now stale in key areas. The environment evolved materially after it was produced.

Major upgrades now in force:
- Contract surface baseline expanded from 10-era references to validated 14-surface operation.
- Frontend governance expanded with dedicated `accessibility.md` and `component-patterns.md` rules.
- Stop hook and CI gate enforcement hardened for path resilience and script-based policy checks.
- Additional make targets and validator layers introduced for ongoing infra quality enforcement.
- QA automation and reconciliation utilities implemented and verified.

---

## 3. Configuration Architecture (Current)

### 3.1 Layered Configuration

| Layer | Path | Role |
|---|---|---|
| Root settings | `/root/.claude/settings.json` | Runtime-level root policy and MCP wiring |
| User settings | `/home/zaks/.claude/settings.json` | Active deny/allow policy, hooks, MCP declarations |
| Project constitution | `/home/zaks/zakops-agent-api/CLAUDE.md` | Monorepo operating constitution |
| Path-scoped rules | `/home/zaks/zakops-agent-api/.claude/rules/` | Context-specific engineering constraints |
| Commands | `/home/zaks/zakops-agent-api/.claude/commands/` | Operational mission workflows |
| Hooks | `/home/zaks/.claude/hooks/` | Runtime enforcement + diagnostics + sync |
| Skills | `/home/zaks/.claude/skills/` | Reusable knowledge overlays |
| Agents | `/home/zaks/.claude/agents/` | Delegated specialist behavior |

### 3.2 Live Inventory Counts

| Component | Count |
|---|---:|
| Commands | 15 |
| Rules | 7 |
| Agents | 3 |
| Skills | 8 |
| Hook scripts | 7 |
| Contract surfaces | 14 |

### 3.3 Settings Snapshot

User settings (`/home/zaks/.claude/settings.json`):
- `deny` rules: 12
- `allow` patterns: 4
- MCP servers: `github`, `playwright`
- Playwright MCP status: `disabled=true`
- Hook groups: `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`

Root settings (`/root/.claude/settings.json`):
- `dangerouslySkipPermissions=true`
- `allow` entries: 140
- `deny` entries: 12
- MCP servers: `crawl4ai-rag`, `gmail`

---

## 4. Runtime Enforcement Model

### 4.1 Effective Enforcement Reality

Permission arrays exist, but runtime safety enforcement depends on hooks and validators.

Primary blockers:
- `pre-edit.sh` for protected file and edit-time policy gates
- `pre-bash.sh` for destructive command restrictions
- `stop.sh` for end-of-session gate execution

### 4.2 Stop Hook Gate Contract (Current)

`/home/zaks/.claude/hooks/stop.sh` executes:
- Gate A: `validate-fast`
- Gate B: `validate-contract-surfaces (14 surfaces)`
- Gate E: raw `httpx` usage policy scan with `rg -> grep` fallback and fail-closed scanner behavior

Project detection is hardened:
1. `MONOREPO_ROOT_OVERRIDE`
2. `git rev-parse --show-toplevel`
3. known path fallback (`/home/zaks/zakops-agent-api`)
4. explicit `SKIP` messaging when root cannot be validated

### 4.3 Enforcement Flow Diagram

```text
Tool Request
   |
   +--> PreToolUse Hook
           |
           +--> pre-edit.sh (Edit/Write) OR pre-bash.sh (Bash)
                   |
                   +--> read boot/session verdict + policy checks
                           |
                           +--> PASS: continue execution
                           +--> FAIL: exit 2 (blocked)

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

Current authoritative alignment:
- `contract-surfaces.md`: 14
- `CLAUDE.md` table rows: 14
- `validate-contract-surfaces.sh` declared scope: 14
- `INFRASTRUCTURE_MANIFEST.md` contract entries: 14

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

### 6.3 CI Gate Expansion

CI includes script-backed gates beyond the earlier baseline:
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

These are enforced via:
- `validate-surface9.sh`
- `validate-frontend-governance.sh`
- CI gates F/G and local validation chain

### 7.2 Frontend Design Skill

Active local skill exists:
- `/home/zaks/.claude/skills/frontend-design/SKILL.md`

Model-level policy note:
- Playwright MCP remains intentionally disabled in user settings.
- Frontend tooling guidance documented in:
  - `/home/zaks/bookkeeping/docs/FRONTEND-TOOLING-POLICY.md`

---

## 8. Mission and QA Closure Ledger

### 8.1 Execution Mission Chain (Completed)

1. `MISSION-INFRA-TRUTH-REPAIR-001`
2. `MISSION-SURFACES-10-14-REGISTER-001`
3. `MISSION-FRONTEND-GOVERNANCE-HARDENING-001`
4. `MISSION-CI-HARDENING-001`
5. `MISSION-INFRA-ENHANCEMENTS-UNIFIED-001`

### 8.2 QA Verification Chain (Completed)

| QA Mission | Result | Remediations |
|---|---|---:|
| QA-ITR-VERIFY-001 | 45/45 PASS, 0 FAIL, 3 INFO | 1 |
| QA-S10-14-VERIFY-001 | 51/51 PASS, 0 FAIL, 2 INFO | 1 |
| QA-FGH-VERIFY-001 | 46/47 PASS, 0 FAIL, 1 INFO | 0 |
| QA-CIH-VERIFY-001 | 52/52 PASS, 0 FAIL, 0 INFO | 0 |
| QA-IEU-VERIFY-001 | 56/56 PASS, 0 FAIL, 0 INFO | 0 |

### 8.3 Enhancement Consolidation Outcome

`INFRA-ENHANCEMENTS-UNIFIED-001` status:
- 18/18 enhancement clusters implemented
- 0 deferred
- 16/16 AC PASS

---

## 9. Current Operational Posture

### 9.1 Stability Summary

The platform is in a hardened and reconciled state for this mission family:
- unified contract system and governance checks are active
- CI and local gates are aligned
- QA evidence chain is complete across remediation and enhancement phases

### 9.2 Residual Non-Blocking Items

- Playwright MCP remains disabled by policy design.
- A stale `/mnt/skills` reference may still exist in inert paste-cache artifacts; not part of runtime enforcement.

### 9.3 Risk Rating

For the frontend infrastructure audit remediation scope:
- Risk posture: LOW

---

## 10. Operator Quick Commands

### 10.1 Core Daily Commands

```bash
cd /home/zaks/zakops-agent-api
make validate-local
make validate-contract-surfaces
make validate-frontend-governance
make infra-snapshot
```

### 10.2 Enhanced Validation Suite

```bash
cd /home/zaks/zakops-agent-api
make validate-surfaces-new
make validate-hook-contract
make validate-enhancements
```

### 10.3 Verification Artifact Roots

- Mission docs: `/home/zaks/bookkeeping/docs/`
- QA verifications: `/home/zaks/bookkeeping/qa-verifications/`

---

## 11. Reference Paths (Authoritative)

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
| Final audit report | `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT-FINAL-REPORT.md` |

---

## 12. Versioning Note

Version 3 supersedes Version 2 as the operational reference for the current ZakOps Claude Code setup.

Version 2 remains archived for traceability:
- `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-2.md`
- `/home/zaks/bookkeeping/docs/ZakOps-V7PP-Claude-Code-Infrastructure-Reference-Version-2.docx`

---

*End of Infrastructure Reference — Version 3*
