# FRONTEND-GOVERNANCE-HARDENING-001 — Baseline Evidence

**Captured:** 2026-02-10
**Mission:** FRONTEND-GOVERNANCE-HARDENING-001

---

## Validation Outputs

### make validate-local — PASS
```
Contract surface validation passed
Agent config validation passed
SSE schema validation passed
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit
Redocly ignores: 57 (ceiling: 57)
All local validations passed
```

### make validate-surface9 — PASS (5/5 checks)
```
Check 1: Import discipline — PASS
Check 2: Stage definitions — PASS
Check 3: Data fetching (Promise.allSettled) — PASS
Check 4: Design system manifest — PASS
Check 5: Design system path-scoped rule — PASS
Surface 9 Validation: PASS (0 violations)
```

### make validate-contract-surfaces — PASS (14/14)
```
Bridge Import Enforcement — PASS
Typed SDK Enforcement — PASS
Surface 8: Agent Config — PASS
Surface 9: Design System — PASS
Surface 10: Dependency Health — PASS
Surface 11: Env Registry — PASS
Surface 12: Error Taxonomy — PASS
Surface 13: Test Coverage — PASS
Surface 14: Performance Budget — PASS
PASS: ALL 14 CONTRACT SURFACE CHECKS PASSED
```

---

## Gate E (stop.sh) — Pre-Fix State

**File:** `/home/zaks/.claude/hooks/stop.sh`
**Lines 39-44:**
```bash
# Gate E — Raw httpx client usage in deal_tools.py (must be 0)
echo "Gate E: raw httpx client usage check"
if rg -n "httpx\\.(AsyncClient|get|post|put|patch|delete)" apps/agent-api/app/core/langgraph/tools/deal_tools.py; then
  echo "ERROR: Gate E failed (raw httpx client usage found). Blocking stop hook."
  exit 2
fi
```

**Issue:** Bare `rg` call with no fallback. If `rg` is not in PATH, scanner fails silently (command not found exits non-zero, interpreted as "no matches found" = pass). This is a fail-open vulnerability — if rg is absent, Gate E is effectively disabled.

---

## Governance Rules Inventory (Pre-Mission)

### Existing rules in `.claude/rules/`
| File | Lines | Scope |
|------|-------|-------|
| agent-tools.md | 41 | Agent API tools |
| backend-api.md | 36 | Backend API |
| contract-surfaces.md | 85+ | Contract system |
| dashboard-types.md | 27 | Dashboard types |
| design-system.md | 91 | Dashboard design |

**Total:** 5 rules

### Missing rules (per audit)
- accessibility.md (G8)
- component-patterns.md (G9)

### design-system.md Section Map
**Category A (7 sections):** A1-A7 (Data Fetching, Error Handling, CSS Architecture, Data Aggregation, Stage Definitions, API Communication, Import Discipline)

**Category B (7 sections + principle):** B1-B7 (Design Thinking, Typography, Color/Theme, Motion, Spatial Composition, Backgrounds, Anti-Patterns) + Critical Principle

### Missing governance in design-system.md (per audit)
- G10: Responsive breakpoint reference
- G11: Category B enrichment (tone palette, anti-convergence, variation)
- G12: z-index scale
- G13: Dark mode strategy
- G14: Animation performance (GPU-safe vs layout-triggering)
- G18: State management patterns

### validate-surface9.sh checks (5 total)
1. Import discipline
2. Stage definitions
3. Promise.allSettled
4. Design system manifest
5. Design system rule exists

---

## Git State
```
Repository: /home/zaks/zakops-agent-api
Status: clean working tree
```
