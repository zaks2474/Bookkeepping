# INFRA-ENHANCEMENTS-UNIFIED-001 — Baseline Report

**Date:** 2026-02-10
**Mission:** INFRA-ENHANCEMENTS-UNIFIED-001

---

## Baseline Validation Outputs

### validate-local (PASS)
```
All local validations passed
- sync-types: PASS
- lint: PASS (Redocly ignores: 57/57)
- contract-surfaces: PASS (14/14)
- agent-config: PASS
- sse-schema: PASS
- frontend-governance: PASS
- tsc --noEmit: PASS
```

### validate-surface9 (PASS)
```
Surface 9 Validation: PASS (0 violations)
- Import discipline: PASS
- Stage definitions: PASS
- Data fetching: PASS
- Design system manifest: PASS
- Design system path-scoped rule: PASS
- Frontend governance rules: PASS
- Governance sections: PASS (6/6)
- Anti-convergence: PASS
```

### validate-contract-surfaces (PASS)
```
ALL 14 CONTRACT SURFACE CHECKS PASSED
- Surface 1-7: V5PP checks (bridge imports, typed SDK)
- Surface 8: Agent config alignment
- Surface 9: Design system conventions
- Surface 10: Dependency health
- Surface 11: Env registry
- Surface 12: Error taxonomy
- Surface 13: Test coverage
- Surface 14: Performance budget
```

---

## Current Infrastructure State

### Directory: tools/infra/
- 17 shell scripts, flat structure
- **No `schemas/` subdirectory** (needs creation)
- **No `tests/` subdirectory** (needs creation)

### Existing Validators (17 scripts)
| Script | Purpose |
|--------|---------|
| check-governance-drift.sh | Policy drift check (5 checks) |
| check-spec-drift.sh | OpenAPI spec drift detection |
| migration-assertion.sh | DB migration assertions |
| scan-evidence-secrets.sh | Evidence secret scanning |
| validate-agent-config.sh | Surface 8 |
| validate-api-contract.sh | API contract validation |
| validate-contract-surfaces.sh | Unified 14-surface runner |
| validate-frontend-governance.sh | Governance anchors (4 checks) |
| validate-gatee-scan.sh | Gate E httpx scanner (rg→grep fallback) |
| validate-rule-frontmatter.sh | Rule file frontmatter schema |
| validate-stop-hook-contract.sh | Stop hook contract markers |
| validate-surface9.sh | Design system conventions |
| validate-surface10.sh | Dependency health (5 checks) |
| validate-surface11.sh | Env registry (5 checks) |
| validate-surface12.sh | Error taxonomy (5 checks) |
| validate-surface13.sh | Test coverage (5 checks) |
| validate-surface14.sh | Performance budget (5 checks, advisory/strict) |

### Existing Make Targets
| Target | Scope |
|--------|-------|
| validate-contract-surfaces | All 14 surfaces |
| validate-agent-config | Surface 8 |
| validate-sse-schema | SSE events |
| validate-migrations | Gate F |
| validate-surface9..14 | Individual surfaces |
| validate-enforcement | Meta-gate |
| validate-frontend-governance | Governance + Gate E |
| validate-fast | Fast offline (stop hook tier) |
| validate-full | Full suite |
| validate-local | CI-safe offline |
| validate-live | Online validation |

### CI Workflow (.github/workflows/ci.yml)
- 307 lines, 4 job phases
- Gate E: script-based (`validate-gatee-scan.sh`)
- Gate F: frontmatter + governance scripts
- No inline Gate E policy snippets (already cleaned)
- No workflow YAML linting step
- No four-way surface count guard
- No strict S14 enforcement

### Stop Hook (stop.sh)
- 3-path detection: env-override → git → known-path
- 3 gates: A (validate-fast), B (contract-surfaces), E (httpx scan)
- Time budget enforcement
- Memory sync at session end

---

## Enhancement Inventory

### Source: QA-S10-14-VERIFY-001 (10 items)

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| ENH-1 | Machine-readable schema for PERFORMANCE-BUDGET.md + schema-lint gate | missing | No schema exists |
| ENH-2 | Unit-test harness for validate-surface10..14.sh with fixture inputs | missing | No tests/ dir |
| ENH-3 | Single `make validate-surfaces-new` meta-target for S10-S14 | missing | Not in Makefile |
| ENH-4 | Manifest contract section schema validation (entry count + fields) | missing | No schema exists |
| ENH-5 | CI check enforcing 4-way count equality at PR time | missing | Not in ci.yml |
| ENH-6 | Regression guard for S10-S14 entries from CLAUDE.md | missing | No guard script |
| ENH-7 | Stricter strict-mode contract for S14 in CI (advisory local, strict CI) | missing | Strict support exists in script but not wired in CI |
| ENH-8 | Automated reconciliation-table generation in completion reports | missing | No automation |
| ENH-9 | Pre-commit scan for stale surface-count strings in scripts/docs | missing | No scanner |
| ENH-10 | QA helper command that scaffolds evidence files | missing | No scaffold tool |

### Source: QA-FGH-VERIFY-001 (10 items)

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| ENH-1 | Dedicated unit tests for Gate E scanner branch/rc handling | missing | No test harness |
| ENH-2 | CI lint for `.claude/rules/*.md` path frontmatter validity | partial | validate-rule-frontmatter.sh exists but not schema-backed |
| ENH-3 | Rule-schema checker for governance anchors in design-system.md | missing | No schema file |
| ENH-4 | `make validate-frontend-governance` aggregate target | already_done | Target exists in Makefile |
| ENH-5 | Stop-hook self-test mode with constrained PATH emulation | missing | No self-test wrapper |
| ENH-6 | Automated comparison report: frontend-design skill vs Category B | missing | No comparison tool |
| ENH-7 | Changelog auto-insertion for governance rule updates | missing | No automation |
| ENH-8 | Policy drift check: tooling policy vs settings.json live values | partial | check-governance-drift.sh exists but doesn't cover tooling policy vs settings |
| ENH-9 | Pre-commit rule preventing stale surface count labels | missing | No scanner |
| ENH-10 | QA scaffold command for evidence skeletons | missing | No scaffold tool |

### Source: QA-CIH-VERIFY-001 (10 items)

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| ENH-1 | Unit-test harness for validate-gatee-scan.sh with fixtures | missing | No test harness |
| ENH-2 | Reusable YAML lint step for workflow structural correctness | missing | Not in CI |
| ENH-3 | Dedicated `make validate-hook-contract` target | missing | Not in Makefile |
| ENH-4 | CI assertion that forbids inline Gate E snippets in workflow | missing | No prohibition guard |
| ENH-5 | Machine-readable schema for governance anchor sets | missing | No schema file |
| ENH-6 | Pre-commit guard for stale surface-count labels | missing | No scanner |
| ENH-7 | Benchmark check for validate-frontend-governance runtime | missing | No benchmark check |
| ENH-8 | Snapshot diff summarizer for manifest changes | missing | No automation |
| ENH-9 | Automated AC coverage checker for completion reports | missing | No checker |
| ENH-10 | QA scaffold command for CI-hardening evidence skeletons | missing | No scaffold tool |

### Summary
- **already_done:** 1 (QA-FGH ENH-4)
- **partial:** 2 (QA-FGH ENH-2, ENH-8)
- **missing:** 27

---

*End of Baseline Report*
