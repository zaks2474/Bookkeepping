# CI-HARDENING-001 Baseline Evidence

## Captured: 2026-02-10

---

## 1. validate-local Output

**Result: PASS**

- sync-types: PASS (openapi-typescript 7.10.1)
- sync-agent-types: PASS
- lint-dashboard: PASS (9 warnings, 0 errors — existing useEffect dep warnings)
- validate-contract-surfaces: ALL 14 PASS
- validate-agent-config: PASS (with expected WARN: prompt tool list requires running DB)
- validate-sse-schema: PASS
- tsc --noEmit: PASS
- check-redocly-debt: 57 ignores (ceiling: 57) — at limit

## 2. validate-surface9 Output

**Result: PASS (0 violations)**

- Check 1: Import discipline — PASS
- Check 2: Stage definitions — PASS
- Check 3: Data fetching (Promise.allSettled) — PASS
- Check 4: Design system manifest — PASS
- Check 5: Design system rule — PASS
- Check 6: Governance rules (accessibility.md, component-patterns.md) — PASS
- Check 7: Design-system governance sections (6/6) — PASS
- Check 8: Anti-convergence policy — PASS

## 3. validate-contract-surfaces Output

**Result: ALL 14 PASS**

- Surface 1-5: Generated file freshness — PASS
- Surface 3,6,7: Reference schema existence — PASS
- Bridge import enforcement — PASS
- Typed SDK enforcement — PASS
- Surface 8: Agent config alignment — PASS
- Surface 9: Design system conventions — PASS
- Surface 10-14: All sub-validators — PASS

## 4. Hook Pre-State: stop.sh Project Detection

**File:** `/home/zaks/.claude/hooks/stop.sh`

### Current Detection Logic (lines 10-13):
```bash
# Only run if in a recognized project
MONOREPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
if [ -n "$MONOREPO_ROOT" ] && [ -f "$MONOREPO_ROOT/Makefile" ] && grep -q "validate-fast" "$MONOREPO_ROOT/Makefile" 2>/dev/null; then
  cd "$MONOREPO_ROOT"
```

### Behavior:
- **Normal (inside git repo with Makefile):** Runs Gates A, B, E
- **Constrained PATH (git not in PATH):** `git rev-parse` fails → `MONOREPO_ROOT=""` → entire gate chain SKIPPED silently with "Not in a recognized project"
- **Outside repo:** Same silent skip

### Issue (VF-01.5 from QA-FGH-VERIFY-001):
When launched from a constrained PATH context (e.g., login shell without git), project detection fails even though the monorepo root is inferable from known paths. All gates are silently skipped.

## 5. CI Gate E Pre-State

**File:** `/home/zaks/zakops-agent-api/.github/workflows/ci.yml` (lines 271-278)

### Current Logic:
```yaml
- name: Gate E — Raw httpx client usage (must be 0)
  run: |
    if rg -n "httpx\\.(AsyncClient|get|post|put|patch|delete)" apps/agent-api/app/core/langgraph/tools/deal_tools.py; then
      echo "::error::Raw httpx client usage found in deal_tools.py (use BackendClient)"
      exit 1
    fi
    echo "PASS: no raw httpx client usage in deal_tools.py"
```

### Issues:
1. Hard dependency on `rg` — no fallback to `grep` if `rg` install step fails
2. No explicit rc handling for scanner errors (rc >= 2)
3. Inline logic, not reusable by local validation

## 6. Git Status

```
clean working tree (no uncommitted changes)
```
