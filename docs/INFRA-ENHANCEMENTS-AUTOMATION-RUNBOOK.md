# Infrastructure Enhancement Automation Runbook

**Created:** 2026-02-10
**Mission:** INFRA-ENHANCEMENTS-UNIFIED-001

---

## QA Scaffold Generator

**Script:** `/home/zaks/bookkeeping/scripts/qa-scaffold.sh`

**Purpose:** Pre-creates QA evidence directory structure, scorecard skeleton, and completion report skeleton for a new QA mission.

**Usage:**
```bash
# Dry run (preview what would be created)
bash /home/zaks/bookkeeping/scripts/qa-scaffold.sh QA-IEU-VERIFY-001 --dry-run

# Create scaffold
bash /home/zaks/bookkeeping/scripts/qa-scaffold.sh QA-IEU-VERIFY-001
```

**Creates:**
- `qa-verifications/<MISSION_ID>/evidence/` — empty evidence directory
- `qa-verifications/<MISSION_ID>/SCORECARD.md` — scorecard template with PF/VF/XC/ST sections
- `qa-verifications/<MISSION_ID>/<MISSION_ID>-COMPLETION.md` — completion report template

---

## AC Coverage Checker

**Script:** `/home/zaks/bookkeeping/scripts/check-ac-coverage.py`

**Purpose:** Compares acceptance criteria references between a source mission file and its completion report. Reports missing and extra AC references.

**Usage:**
```bash
python3 /home/zaks/bookkeeping/scripts/check-ac-coverage.py \
  /home/zaks/bookkeeping/docs/MISSION-INFRA-ENHANCEMENTS-UNIFIED-001.md \
  /home/zaks/bookkeeping/docs/INFRA-ENHANCEMENTS-UNIFIED-001-COMPLETION.md
```

**Output:**
- `PASS` if all source ACs found in completion
- `FAIL` with list of missing ACs otherwise

---

## Reconciliation Table Generator

**Script:** `/home/zaks/bookkeeping/scripts/generate-reconciliation-table.py`

**Purpose:** Produces a markdown table showing surface counts across 4 authoritative sources (contract catalog, CLAUDE.md, unified validator, manifest).

**Usage:**
```bash
# Current state
python3 /home/zaks/bookkeeping/scripts/generate-reconciliation-table.py

# With before/after transition context
python3 /home/zaks/bookkeeping/scripts/generate-reconciliation-table.py --before 9 --after 14
```

**Output:** Markdown table with PASS/MISMATCH status per source.

---

## Governance Changelog Helper

**Script:** `/home/zaks/bookkeeping/scripts/governance-changelog-helper.sh`

**Purpose:** Lists all governance-related files with their modification dates and sizes. Useful for generating changelog entries after governance rule updates.

**Usage:**
```bash
bash /home/zaks/bookkeeping/scripts/governance-changelog-helper.sh
```

**Tracks:**
- `.claude/rules/design-system.md`
- `.claude/rules/accessibility.md`
- `.claude/rules/component-patterns.md`
- `.claude/rules/contract-surfaces.md`
- `tools/infra/validate-frontend-governance.sh`
- `tools/infra/validate-rule-frontmatter.sh`
- `tools/infra/check-governance-drift.sh`

---

## Skill vs Rule Comparison

**Script:** `/home/zaks/bookkeeping/scripts/compare-frontend-skill-vs-rule.py`

**Purpose:** Compares the frontend-design SKILL.md with design-system.md Category B sections. Reports keyword overlap and coverage gaps.

**Usage:**
```bash
python3 /home/zaks/bookkeeping/scripts/compare-frontend-skill-vs-rule.py
```

**Output:**
- Coverage table for each Category B section
- Keyword analysis (shared, rule-only, skill-only)

---

## Validation Scripts (tools/infra/)

### Schema Validators
| Script | Target |
|--------|--------|
| `validate-performance-budget-schema.sh` | PERFORMANCE-BUDGET.md structure |
| `validate-governance-anchor-schema.sh` | Governance rule anchor completeness |
| `validate-manifest-contract-section.sh` | Manifest surface entries |

### CI Policy Guards
| Script | Purpose |
|--------|---------|
| `validate-ci-gatee-policy.sh` | Prohibit inline Gate E in CI |
| `validate-surface-count-consistency.sh` | Four-way count reconciliation |

### Drift Guards
| Script | Purpose |
|--------|---------|
| `scan-stale-surface-labels.sh` | Detect stale count labels |
| `validate-claude-surface-table.sh` | CLAUDE.md table integrity |
| `check-governance-drift.sh` | Full governance drift check |

### Test Harnesses
| Script | Covers |
|--------|--------|
| `tests/test-validate-gatee-scan.sh` | Gate E scanner (4 fixture cases) |
| `tests/test-validate-surfaces10-14.sh` | Surface 10-14 validators (15 checks) |
| `validate-stop-hook-selftest.sh` | Stop hook detection branches |

### Make Targets
```bash
make validate-surfaces-new      # S10-S14 + schema checks
make validate-hook-contract     # Stop hook contract + self-test
make validate-enhancements      # Full enhancement harness suite
```

---

*End of Runbook*
