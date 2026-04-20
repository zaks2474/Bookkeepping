# MISSION: V5PP-MQ1 REMEDIATION — FIX THE 5 BLOCKERS
## Codename: `V5PP-REMEDIATE-001`
## Priority: P0 — Validation Pipeline Is Non-Functional
## Executor: Claude Code (Opus 4.5/4.6)
## Authority: FULL EXECUTION — Fix all 5 blockers, verify each one
## Date: 2026-02-07

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   CONTEXT: V5PP-MQ1 was executed and reported 13/13 PASS.                   ║
║   Two independent adversarial verification runs found 5 blockers.           ║
║                                                                              ║
║   The defense layer WORKS: deny rules, pre-edit hook, path-scoped rules,    ║
║   CLAUDE.md constitution — all verified functional.                          ║
║                                                                              ║
║   The detection layer is BROKEN: validate-local crashes because             ║
║   validate-contract-surfaces.sh was never created. make infra-snapshot      ║
║   doesn't exist. Two hooks have CRLF line endings. Root-owned files         ║
║   block the sync pipeline for user zaks.                                     ║
║                                                                              ║
║   This is a surgical remediation — 5 fixes, nothing else.                   ║
║   Do NOT re-run the full V5PP mission. Do NOT touch anything that works.    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## THE 5 BLOCKERS

| # | Blocker | Impact | Time Estimate |
|---|---------|--------|---------------|
| B1 | CRLF in hooks | pre-bash.sh + stop.sh exit 127 (dead code) | 30 seconds |
| B2 | Root-owned generated files | make sync-types fails as zaks (EACCES) | 30 seconds |
| B3 | validate-contract-surfaces.sh missing | validate-local crashes, stop hook fails | 10 minutes |
| B4 | make infra-snapshot missing | Manifest can't be generated, Pre-Task Protocol broken | 5 minutes |
| B5 | Stale CLAUDE.md references | make infra-check sends Claude to dead end | 5 minutes |

**Total estimated time: ~20 minutes**

---

## FIX B1: CRLF IN HOOKS

**Problem:** `pre-bash.sh` and `stop.sh` have Windows-style line endings (`\r\n`).
The shebang `#!/usr/bin/env bash\r` causes `bash\r: not found` → exit 127.
These hooks are registered in settings.json but silently fail every time.

```bash
# ════════════════════════════════════════════════════
# STEP 1: Diagnose — confirm CRLF is the issue
# ════════════════════════════════════════════════════

echo "=== BEFORE ==="
for hook in /home/zaks/.claude/hooks/pre-bash.sh /home/zaks/.claude/hooks/stop.sh; do
  if [ -f "$hook" ]; then
    echo "--- $(basename $hook) ---"
    file "$hook"                         # Should show "with CRLF" if problem exists
    head -1 "$hook" | cat -A             # ^M at end = CRLF
    bash "$hook" </dev/null 2>&1; echo "Exit: $?"
  else
    echo "MISSING: $hook"
  fi
done

# ════════════════════════════════════════════════════
# STEP 2: Fix — convert to Unix line endings
# ════════════════════════════════════════════════════

# Method 1: sed (always available)
for hook in /home/zaks/.claude/hooks/pre-bash.sh /home/zaks/.claude/hooks/stop.sh; do
  if [ -f "$hook" ]; then
    sed -i 's/\r$//' "$hook"
    echo "Fixed: $hook"
  fi
done

# Also check the other hooks while we're here
for hook in /home/zaks/.claude/hooks/pre-edit.sh /home/zaks/.claude/hooks/post-edit.sh; do
  if [ -f "$hook" ]; then
    if file "$hook" | grep -q "CRLF"; then
      sed -i 's/\r$//' "$hook"
      echo "Fixed (bonus): $hook"
    else
      echo "OK: $hook (no CRLF)"
    fi
  fi
done

# ════════════════════════════════════════════════════
# STEP 3: Verify — hooks must execute cleanly
# ════════════════════════════════════════════════════

echo ""
echo "=== AFTER ==="
for hook in /home/zaks/.claude/hooks/pre-bash.sh /home/zaks/.claude/hooks/stop.sh; do
  echo "--- $(basename $hook) ---"
  file "$hook"                           # Should NOT show "with CRLF"
  head -1 "$hook" | cat -A               # Should NOT have ^M
  ls -la "$hook"                          # Must be executable (-rwx)
done

# Behavioral test: pre-bash.sh should block destructive commands
# The hook reads the command from the tool input. Test with a simple check:
echo "rm -rf /" | /home/zaks/.claude/hooks/pre-bash.sh 2>&1
echo "pre-bash rm -rf exit: $?"
# → Must print block message and exit non-zero

# Behavioral test: stop.sh should run without crashing
cd /home/zaks/zakops-agent-api
/home/zaks/.claude/hooks/stop.sh 2>&1 | tail -5
echo "stop.sh exit: $?"
# → May have validation failures (expected until B3 is fixed) but must NOT exit 127
```

```
GATE B1: file *.sh shows NO "CRLF" for any hook.
         pre-bash.sh executes (exit != 127).
         stop.sh executes (exit != 127).
         All hooks have executable permission (-rwx).
```

---

## FIX B2: ROOT-OWNED GENERATED FILES

**Problem:** Several files in the monorepo are owned by root, not zaks.
When Claude Code runs as zaks, `make sync-types` and `make update-spec`
fail with EACCES because they can't write to root-owned files.

```bash
# ════════════════════════════════════════════════════
# STEP 1: Find all root-owned files in the monorepo
# ════════════════════════════════════════════════════

echo "=== ROOT-OWNED FILES IN MONOREPO ==="
find /home/zaks/zakops-agent-api -user root -not -path "*/node_modules/*" -not -path "*/.git/objects/*" 2>/dev/null \
  | head -50 \
  | tee /tmp/root-owned-files.txt

echo ""
echo "Count: $(wc -l < /tmp/root-owned-files.txt)"

# Also check the backend repo
echo ""
echo "=== ROOT-OWNED FILES IN BACKEND ==="
find /home/zaks/zakops-backend -user root -not -path "*/node_modules/*" -not -path "*/.git/objects/*" 2>/dev/null \
  | head -20

# ════════════════════════════════════════════════════
# STEP 2: Fix ownership — the specific known problem files
# ════════════════════════════════════════════════════

# Known problem files from verification:
sudo chown zaks:zaks /home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json 2>/dev/null
sudo chown zaks:zaks /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-types.generated.ts 2>/dev/null

# Broader fix: any root-owned file in the working trees should be owned by zaks
# (except .git internals which are managed by git)
sudo chown -R zaks:zaks /home/zaks/zakops-agent-api/packages/ 2>/dev/null
sudo chown -R zaks:zaks /home/zaks/zakops-agent-api/apps/ 2>/dev/null
sudo chown -R zaks:zaks /home/zaks/zakops-agent-api/tools/ 2>/dev/null
sudo chown -R zaks:zaks /home/zaks/zakops-agent-api/Makefile 2>/dev/null
sudo chown -R zaks:zaks /home/zaks/zakops-agent-api/CLAUDE.md 2>/dev/null

# Also fix the backend repo if needed
sudo chown -R zaks:zaks /home/zaks/zakops-backend/src/ 2>/dev/null

# ════════════════════════════════════════════════════
# STEP 3: Verify — sync pipeline must work as zaks
# ════════════════════════════════════════════════════

echo ""
echo "=== VERIFICATION ==="

# Check the specific files
ls -la /home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-types.generated.ts

# Test: can we write to the spec file?
touch /home/zaks/zakops-agent-api/packages/contracts/openapi/zakops-api.json 2>&1
echo "Touch spec file exit: $?"
# → Must be 0

# Test: can we write to the generated file?
touch /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api-types.generated.ts 2>&1
echo "Touch generated file exit: $?"
# → Must be 0

# Test: does make sync-types work now? (requires node_modules to be installed)
cd /home/zaks/zakops-agent-api
make sync-types 2>&1 | tail -5
echo "sync-types exit: $?"
```

```
GATE B2: Zero root-owned files in working tree directories (packages/, apps/, tools/).
         make sync-types exits 0 (not EACCES).
         touch on spec and generated files succeeds as zaks.
```

---

## FIX B3: CREATE validate-contract-surfaces.sh

**Problem:** The V5PP-MQ1 execution report claimed this script was created (Fix 4: PASS).
Two independent verification runs confirmed it does not exist on disk.
This is the single most impactful blocker — it breaks validate-local, which breaks
the stop hook, which means session-end validation never runs.

**The script spec is in the V5PP-MQ1 mission prompt, Fix 4, lines 881-994.**
Copy it exactly, adapting paths based on what actually exists.

```bash
# ════════════════════════════════════════════════════
# STEP 1: Confirm it's missing
# ════════════════════════════════════════════════════

ls -la /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh 2>&1
# → Expected: No such file or directory

# Make sure the directory exists
mkdir -p /home/zaks/zakops-agent-api/tools/infra/

# ════════════════════════════════════════════════════
# STEP 2: Create the script
# ════════════════════════════════════════════════════

cat > /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh << 'SCRIPT'
#!/bin/bash
# validate-contract-surfaces.sh — V5PP Fix 4
# Validates all 7 contract surfaces: freshness, bridge imports, typed SDK, TypeScript
# CI-safe: does NOT require running services
set -euo pipefail

FAILURES=0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

echo "=== CONTRACT SURFACE VALIDATION ==="
echo ""

# ────────────────────────────────────────
# CHECK 1: Generated file freshness
# ────────────────────────────────────────

echo "--- Generated File Freshness ---"

check_freshness() {
  local spec="$1"
  local generated="$2"
  local name="$3"

  if [ -f "$spec" ] && [ -f "$generated" ]; then
    SPEC_TIME=$(stat -c %Y "$spec" 2>/dev/null || stat -f %m "$spec" 2>/dev/null)
    GEN_TIME=$(stat -c %Y "$generated" 2>/dev/null || stat -f %m "$generated" 2>/dev/null)
    if [ "$GEN_TIME" -ge "$SPEC_TIME" ]; then
      echo "  ✅ $name: current"
    else
      echo "  ❌ $name: STALE (generated older than spec)"
      FAILURES=$((FAILURES+1))
    fi
  elif [ -f "$spec" ] && [ ! -f "$generated" ]; then
    echo "  ❌ $name: generated file MISSING ($generated)"
    FAILURES=$((FAILURES+1))
  elif [ ! -f "$spec" ]; then
    echo "  ⚠️  $name: spec not found ($spec) — skipping"
  fi
}

check_freshness "packages/contracts/openapi/zakops-api.json" \
                "apps/dashboard/src/lib/api-types.generated.ts" \
                "Surface 1: Backend → Dashboard"

check_freshness "packages/contracts/openapi/zakops-api.json" \
                "apps/agent-api/app/schemas/backend_models.py" \
                "Surface 2: Backend → Agent SDK"

check_freshness "packages/contracts/openapi/agent-api.json" \
                "apps/dashboard/src/lib/agent-api-types.generated.ts" \
                "Surface 4: Agent → Dashboard"

check_freshness "packages/contracts/openapi/rag-api.json" \
                "zakops-backend/src/schemas/rag_models.py" \
                "Surface 5: RAG → Backend SDK"

# Surfaces 3, 6, 7 are export/reference schemas — check existence only
echo ""
echo "--- Reference Schema Existence ---"

for schema in \
  "packages/contracts/openapi/agent-api.json:Surface 3: Agent OpenAPI" \
  "packages/contracts/mcp/tool-schemas.json:Surface 6: MCP Tools" \
  "packages/contracts/sse/agent-events.schema.json:Surface 7: SSE Events"; do

  file=$(echo "$schema" | cut -d: -f1)
  name=$(echo "$schema" | cut -d: -f2-)

  if [ -f "$file" ]; then
    echo "  ✅ $name: exists"
  else
    echo "  ❌ $name: MISSING ($file)"
    FAILURES=$((FAILURES+1))
  fi
done

# ────────────────────────────────────────
# CHECK 2: Bridge import enforcement
# ────────────────────────────────────────

echo ""
echo "--- Bridge Import Enforcement ---"

DIRECT_IMPORTS=0
for dir in apps/dashboard/src/components apps/dashboard/src/hooks apps/dashboard/src/app; do
  if [ -d "$dir" ]; then
    COUNT=$(grep -rn "api-types\.generated\|agent-api-types\.generated" "$dir" \
      --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l || echo 0)
    DIRECT_IMPORTS=$((DIRECT_IMPORTS + COUNT))
  fi
done

if [ "$DIRECT_IMPORTS" -eq 0 ]; then
  echo "  ✅ No direct generated file imports found"
else
  echo "  ❌ $DIRECT_IMPORTS direct imports of generated files (must use bridge)"
  FAILURES=$((FAILURES+1))
fi

# ────────────────────────────────────────
# CHECK 3: Typed SDK enforcement
# ────────────────────────────────────────

echo ""
echo "--- Typed SDK Enforcement ---"

DEAL_TOOLS="apps/agent-api/app/core/langgraph/tools/deal_tools.py"
if [ -f "$DEAL_TOOLS" ]; then
  GET_COUNT=$(grep -c '\.get(' "$DEAL_TOOLS" 2>/dev/null || echo 0)
  JSON_COUNT=$(grep -c 'response\.json()' "$DEAL_TOOLS" 2>/dev/null || echo 0)

  if [ "$GET_COUNT" -gt 0 ] || [ "$JSON_COUNT" -gt 0 ]; then
    echo "  ❌ deal_tools.py has untyped patterns (.get()=$GET_COUNT, response.json()=$JSON_COUNT)"
    FAILURES=$((FAILURES+1))
  else
    echo "  ✅ deal_tools.py uses typed SDK (0 untyped patterns)"
  fi
else
  echo "  ⚠️  deal_tools.py not found — skipping"
fi

# ────────────────────────────────────────
# CHECK 4: TypeScript compilation
# ────────────────────────────────────────

echo ""
echo "--- TypeScript Compilation ---"

if [ -d "apps/dashboard" ]; then
  cd apps/dashboard
  if npx tsc --noEmit 2>&1 | tail -3; then
    echo "  ✅ TypeScript compiles"
  else
    echo "  ❌ TypeScript compilation FAILED"
    FAILURES=$((FAILURES+1))
  fi
  cd "$REPO_ROOT"
else
  echo "  ⚠️  apps/dashboard not found — skipping"
fi

# ────────────────────────────────────────
# RESULT
# ────────────────────────────────────────

echo ""
echo "================================"
if [ "$FAILURES" -eq 0 ]; then
  echo "✅ ALL CONTRACT SURFACE CHECKS PASSED"
  exit 0
else
  echo "❌ $FAILURES CHECK(S) FAILED"
  exit 1
fi
SCRIPT

chmod +x /home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh

# ════════════════════════════════════════════════════
# STEP 3: Wire into Makefile
# ════════════════════════════════════════════════════

# Check if the Makefile already has a validate-contract-surfaces target
cd /home/zaks/zakops-agent-api

if ! grep -q "^validate-contract-surfaces:" Makefile; then
  # Add the target. Find a good insertion point (after other validate targets)
  # The exact insertion method depends on the Makefile structure.
  # Add at end if no better spot:
  cat >> Makefile << 'MAKE'

validate-contract-surfaces: ## Validate all 7 contract surfaces (CI-safe)
	@bash tools/infra/validate-contract-surfaces.sh
MAKE
  echo "Added validate-contract-surfaces target to Makefile"
fi

# Verify validate-local includes it
# If validate-local doesn't depend on validate-contract-surfaces, add it
if grep -q "^validate-local:" Makefile; then
  if ! grep "validate-local:" Makefile | grep -q "validate-contract-surfaces"; then
    echo "⚠️  validate-local does NOT depend on validate-contract-surfaces"
    echo "   You need to add validate-contract-surfaces to the validate-local dependency list"
    echo "   Current: $(grep "^validate-local:" Makefile)"
    # Fix: add it to the dependency list
    sed -i 's/^validate-local:.*/& validate-contract-surfaces/' Makefile
    echo "   Updated: $(grep "^validate-local:" Makefile)"
  fi
fi

# ════════════════════════════════════════════════════
# STEP 4: Test the script standalone
# ════════════════════════════════════════════════════

echo ""
echo "=== RUNNING validate-contract-surfaces.sh ==="
bash tools/infra/validate-contract-surfaces.sh 2>&1
echo "Exit: $?"

# ════════════════════════════════════════════════════
# STEP 5: Test make validate-local
# ════════════════════════════════════════════════════

echo ""
echo "=== RUNNING make validate-local ==="
make validate-local 2>&1 | tail -10
echo "Exit: $?"
```

```
GATE B3: tools/infra/validate-contract-surfaces.sh exists and is executable.
         Script runs standalone: bash tools/infra/validate-contract-surfaces.sh exits 0 or reports failures.
         Script does NOT require running services (CI-safe).
         validate-contract-surfaces target exists in Makefile.
         make validate-local includes validate-contract-surfaces.
         make validate-local completes without crashing (may have legitimate failures, but NOT "file not found").
```

---

## FIX B4: ADD make infra-snapshot TARGET

**Problem:** CLAUDE.md Pre-Task Protocol says `make infra-snapshot`. The target doesn't exist.
The generate-manifest.sh script may exist in tools/infra/ but isn't wired into make.

```bash
# ════════════════════════════════════════════════════
# STEP 1: Find what exists
# ════════════════════════════════════════════════════

cd /home/zaks/zakops-agent-api

echo "=== MANIFEST GENERATOR ==="
ls -la tools/infra/generate-manifest.sh 2>&1
# If this exists → just need Makefile target
# If missing → need to create it too (but builder report says it's 262 lines, so it should exist)

echo ""
echo "=== CURRENT MAKEFILE TARGETS (infra-related) ==="
grep "^infra" Makefile 2>/dev/null || echo "No infra-* targets found"

# ════════════════════════════════════════════════════
# STEP 2: Add Makefile targets
# ════════════════════════════════════════════════════

# Add infra-snapshot if missing
if ! grep -q "^infra-snapshot:" Makefile; then
  cat >> Makefile << 'MAKE'

infra-snapshot: ## Generate INFRASTRUCTURE_MANIFEST.md
	@bash tools/infra/generate-manifest.sh
MAKE
  echo "Added infra-snapshot target"
fi

# Add infra-check if missing (CLAUDE.md references this)
if ! grep -q "^infra-check:" Makefile; then
  cat >> Makefile << 'MAKE'

infra-check: ## Infrastructure health check (DB + migrations + manifest freshness)
	@echo "=== Infrastructure Check ==="
	@bash tools/infra/generate-manifest.sh
	@echo "--- Manifest generated ---"
	@if [ -f tools/infra/migration-assertion.sh ]; then \
		bash tools/infra/migration-assertion.sh; \
	else \
		echo "⚠️  migration-assertion.sh not found — skipping"; \
	fi
	@echo "=== Infrastructure Check Complete ==="
MAKE
  echo "Added infra-check target"
fi

# ════════════════════════════════════════════════════
# STEP 3: Verify generate-manifest.sh works
# ════════════════════════════════════════════════════

# If the script doesn't exist, this is a bigger problem.
# But the builder report claims 262 lines and 5 V5PP sections.
if [ -f tools/infra/generate-manifest.sh ]; then
  echo ""
  echo "=== RUNNING generate-manifest.sh ==="
  bash tools/infra/generate-manifest.sh 2>&1 | tail -5
  echo "Exit: $?"

  if [ -f INFRASTRUCTURE_MANIFEST.md ]; then
    LINES=$(wc -l < INFRASTRUCTURE_MANIFEST.md)
    echo "Manifest generated: $LINES lines"
  else
    echo "⚠️  Manifest file not created — check script output path"
    # The script might write to a different filename or location
    find . -name "*MANIFEST*" -newer Makefile 2>/dev/null
  fi
else
  echo "❌ generate-manifest.sh does NOT exist"
  echo "   This is a bigger gap — the builder claimed 262 lines with 5 V5PP sections"
  echo "   Check if it's at an unexpected path:"
  find /home/zaks -name "generate-manifest*" 2>/dev/null
fi

# ════════════════════════════════════════════════════
# STEP 4: Test the Makefile targets
# ════════════════════════════════════════════════════

echo ""
echo "=== make infra-snapshot ==="
make infra-snapshot 2>&1 | tail -5
echo "Exit: $?"

echo ""
echo "=== make infra-check ==="
make infra-check 2>&1 | tail -5
echo "Exit: $?"
```

```
GATE B4: make infra-snapshot exists and runs generate-manifest.sh.
         make infra-check exists (referenced in CLAUDE.md Pre-Task Protocol).
         INFRASTRUCTURE_MANIFEST.md is generated.
         Manifest is >200 lines (250 was the V5PP target but existence > perfection right now).
```

---

## FIX B5: FIX STALE CLAUDE.md REFERENCES

**Problem:** CLAUDE.md references `make infra-check` and potentially other targets that don't exist.
After B4, `make infra-check` should exist. But do a full audit anyway.

```bash
# ════════════════════════════════════════════════════
# STEP 1: Audit all make targets referenced in CLAUDE.md
# ════════════════════════════════════════════════════

cd /home/zaks/zakops-agent-api

echo "=== MAKE TARGETS IN CLAUDE.md ==="
grep -oE 'make [a-z][-a-z]*' CLAUDE.md | sort -u | while read cmd; do
  target=$(echo "$cmd" | cut -d' ' -f2)
  if grep -q "^$target:" Makefile 2>/dev/null; then
    echo "  ✅ $cmd"
  else
    echo "  ❌ STALE: $cmd (target does not exist)"
  fi
done

# ════════════════════════════════════════════════════
# STEP 2: Audit all file references in CLAUDE.md
# ════════════════════════════════════════════════════

echo ""
echo "=== FILE REFERENCES IN CLAUDE.md ==="
grep -oE '\./[a-zA-Z0-9/_.-]+\.(md|sh|json|ts|py)' CLAUDE.md 2>/dev/null | sort -u | while read f; do
  if [ -f "$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ BROKEN: $f"
  fi
done

# Also check relative .claude/ paths
grep -oE '\.claude/[a-zA-Z0-9/_.-]+' CLAUDE.md 2>/dev/null | sort -u | while read f; do
  if [ -f "$f" ] || [ -d "$f" ]; then
    echo "  ✅ $f"
  else
    echo "  ❌ BROKEN: $f"
  fi
done

# ════════════════════════════════════════════════════
# STEP 3: Fix any remaining stale references
# ════════════════════════════════════════════════════

# After B4, infra-check and infra-snapshot should exist.
# If any other references are broken:
# - If the target/file SHOULD exist → create it (or note as gap)
# - If the target/file was RENAMED → update CLAUDE.md
# - If the target/file was REMOVED → remove reference from CLAUDE.md

# Record what was fixed
echo ""
echo "=== FIXES APPLIED ==="
# (Builder fills this in based on what Step 1-2 find)

# ════════════════════════════════════════════════════
# STEP 4: Run brain hygiene checks from V5PP mission
# ════════════════════════════════════════════════════

echo ""
echo "=== BRAIN HYGIENE ==="

LINES=$(wc -l < CLAUDE.md)
echo "Line count: $LINES (ceiling: 150)"
if [ "$LINES" -gt 150 ]; then
  echo "❌ Over ceiling — trim content to rules files"
fi

# Full broken pointer check
BROKEN=0
grep -oE '\./[a-zA-Z0-9/_.-]+\.(md|sh|json)' CLAUDE.md 2>/dev/null | while read f; do
  [ -f "$f" ] || { echo "BROKEN: $f"; BROKEN=$((BROKEN+1)); }
done
echo "Broken pointers: $BROKEN"
```

```
GATE B5: Zero stale make targets in CLAUDE.md.
         Zero broken file references in CLAUDE.md.
         Line count still < 150.
```

---

## VERIFICATION SEQUENCE

```
Execute in this order:

1. B1: Fix CRLF in hooks (30 seconds)
   └─ Unblocks: stop hook, pre-bash hook

2. B2: Fix root-owned files (30 seconds)
   └─ Unblocks: make sync-types, make update-spec

3. B3: Create validate-contract-surfaces.sh (10 minutes)
   └─ Unblocks: make validate-local, stop hook validation

4. B4: Add make infra-snapshot + make infra-check (5 minutes)
   └─ Unblocks: Pre-Task Protocol, manifest generation

5. B5: Fix stale CLAUDE.md references (5 minutes)
   └─ Depends on: B4 (which creates the referenced targets)

FINAL VERIFICATION (run ALL of these):

  # Hooks work
  file ~/.claude/hooks/pre-bash.sh          → NO "CRLF"
  file ~/.claude/hooks/stop.sh              → NO "CRLF"
  ~/.claude/hooks/pre-bash.sh </dev/null    → exit != 127

  # File ownership
  ls -la packages/contracts/openapi/zakops-api.json → owner: zaks
  ls -la apps/dashboard/src/lib/api-types.generated.ts → owner: zaks

  # Validation pipeline
  make validate-contract-surfaces            → exit 0 (or reports real failures, not "file not found")
  make validate-local                        → completes (no crash)
  make infra-snapshot                        → generates INFRASTRUCTURE_MANIFEST.md
  make infra-check                           → exit 0

  # CLAUDE.md integrity
  wc -l CLAUDE.md                            → < 150
  # Run brain hygiene checks                 → 0 broken pointers, 0 stale targets

  # End-to-end: stop hook uses validate-local
  ~/.claude/hooks/stop.sh                    → runs validate-local (may warn, must not crash)
```

---

## HARD RULES

```
1. DO NOT re-run the full V5PP mission. This is surgical.
2. DO NOT modify anything that currently works (deny rules, pre-edit hook, path-scoped rules, CLAUDE.md content).
3. EVERY fix has a verification step. Run it before claiming PASS.
4. If generate-manifest.sh doesn't exist, that's a SEPARATE gap — note it but don't block on it.
5. If make sync-types still fails after B2, investigate WHY (missing deps? different error?) — don't just claim PASS.
6. The script in B3 must be CI-safe (no curl, no service calls, no network).
7. After all fixes, run the FINAL VERIFICATION sequence. ALL items must pass.
```

---

## OUTPUT FORMAT

```markdown
# V5PP-REMEDIATE-001 COMPLETION REPORT

**Date:** [timestamp]
**Executor:** Claude Code [version]

## Results
| # | Fix | Status | Evidence |
|---|-----|--------|----------|
| B1 | CRLF hooks | [PASS/FAIL] | file output showing no CRLF, exit codes |
| B2 | File ownership | [PASS/FAIL] | ls -la showing zaks ownership, sync exit code |
| B3 | validate-contract-surfaces.sh | [PASS/FAIL] | Script runs, make validate-local completes |
| B4 | Makefile targets | [PASS/FAIL] | make infra-snapshot + infra-check both work |
| B5 | CLAUDE.md refs | [PASS/FAIL] | 0 stale targets, 0 broken pointers |

## Final Verification
- Hook CRLF: [clean/dirty]
- File ownership: [zaks/root]
- make validate-contract-surfaces: [exit code]
- make validate-local: [exit code]
- make infra-snapshot: [exit code]
- make infra-check: [exit code]
- CLAUDE.md line count: [N]
- Broken pointers: [N]
- Stale targets: [N]
```

---

*Generated: 2026-02-07*
*Purpose: Fix 5 blockers found by adversarial verification of V5PP-MQ1*
*Scope: Surgical — hooks, ownership, missing script, Makefile targets, CLAUDE.md refs*
*Time estimate: ~20 minutes*
