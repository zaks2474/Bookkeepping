# CLAUDE_CODE_RESET_UPGRADES.PASS1.Gemini-CLI.20260207-1200-pass1.md

## 1. Agent Identity
- **Agent Name:** Gemini-CLI
- **Run ID:** 20260207-1200-pass1
- **Timestamp:** 2026-02-07T12:00:00Z
- **Repo Commit:** (Unknown, presumed latest HEAD)

## 2. What the Current Mission Does Well
- **Strong "Contract-First" Philosophy:** The 7-surface contract system is robust and forward-thinking, enforcing alignment across polyglot services (Python/TypeScript).
- **Explicit Dependency Graph:** The "If you change X, run Y" table in `CLAUDE.md` is crucial for preventing "shotgun surgery" errors.
- **Automated Discovery:** The "Discovery" section (Step 0) prevents hallucination by forcing the agent to verify the environment *before* acting.
- **Gate-Based Progression:** The use of "Gates" (Gate 1, Gate 2, etc.) ensures quality control at each step.
- **Comprehensive Debt Tracking:** Integration with `debt-ledger.md` and manual type debt counters ensures technical debt is visible and managed.

## 3. Gaps & Missing Pieces (Brutally Honest)
- **Lack of "Self-Correction" Mechanisms:** The mission validates heavily but relies on the human/agent to *manually* run fix commands. It should lean harder into `make auto-fix` patterns.
- **Context Window Inefficiency:** Dumping *all* 7 contract details into `CLAUDE.md` might bloat the system prompt. A "Pointer" strategy (summary in main doc, deep links to specific docs) is better for 2026 LLM context windows.
- **Hook Fragility:** The prompt assumes hooks work if the file exists. It doesn't verify execution permissions (`chmod +x`) or Git config (`git config core.hooksPath`).
- **No "Cost/Velocity" Awareness:** There's no mention of optimizing build times or token usage. Re-running *all* validators (`validate-live`) on every small change is slow and expensive.
- **Missing "Agentic Behavior" Tests:** We verify code, but we don't verify if Claude *behaves* correctly (e.g., does it actually check the debt ledger before starting?).

## 4. 2026 Best Practices for Claude Code Setup
*Based on industry trends for autonomous coding agents:*

- **Dynamic Context Loading:** Instead of a static `CLAUDE.md`, use a dynamic `context.sh` or `.claude/context` that generates a fresh summary of *relevant* system state (open ports, git status, recent errors) on every session start.
  - *Source: [Anthropic Model Context Protocol](https://modelcontextprotocol.io/)*
- **"DriftOps" (GitOps for Codebase State):** Automated workflows that detect *and commit* infrastructure fixes (e.g., regenerating stale types) automatically, reducing agent toil.
- **Epistemic Markers:** Explicitly tagging files as `@generated`, `@manual`, `@deprecated` to help the LLM understand editability permissions instantly.
- **Semantic Code Search integration:** Use embeddings-based search tools (like RAG for code) rather than just `grep` to find related logic across the monorepo.

## 5. Innovation Accelerators (Hybrid Options)

- **`make doctor-auto`:** A target that not only checks health (`doctor`) but attempts standard remediation (installing missing deps, fixing perms, regenerating types).
- **"Scope-Locked" Modes:** A slash command or mode where Claude is restricted to *only* modifying specific directories (e.g., `/mode frontend` locks it to `apps/dashboard`), preventing accidental backend breakage.
- **Automated CLAUDE.md Rotation:** A CI job that updates `CLAUDE.md` statistics (line counts, debt metrics) daily, so the agent always sees fresh data without manual updates.
- **"Impact Analysis" Tool:** A script `tools/impact.sh <file>` that outputs exactly which other files/services rely on the target file, helping Claude plan edits safely.

## 6. Concrete Patch List for Mission Prompt

### A. Add "Self-Healing" to Post-Task Protocol
*Update the "Post-Task Protocol" section in the proposed CLAUDE.md:*

```markdown
## Post-Task Protocol (MANDATORY)

1. **Attempt Auto-Fix:** Run `make auto-fix` (if available) to handle formatting/linting/sync automatically.
2. **Verify Alignment:** Run `make validate-local`.
3. **Check Compilation:** Run `npx tsc --noEmit` (dashboard).
4. **Behavioral Check:** Did you touch a "Contract Surface"? If yes, did you update the spec FIRST?
```

### B. Strengthen Hook Verification
*Update "Step 0.9: Find existing hooks" in the Discovery section:*

```bash
# ════════════════════════════════════════════════════
# STEP 0.9: Find and Verify Hooks
# ════════════════════════════════════════════════════

echo ""
echo "=== GIT HOOKS ==="
HOOK_PATH="$MONOREPO_ROOT/.git/hooks/pre-commit"
if [ -f "$HOOK_PATH" ]; then
  if [ -x "$HOOK_PATH" ]; then
    echo "✅ Pre-commit hook exists and is executable"
  else
    echo "❌ Pre-commit hook exists but is NOT executable (fix with chmod +x)"
  fi
else
  echo "❌ Pre-commit hook NOT FOUND"
fi
```

### C. Add "Token Budget" awareness to Manifest
*Update "FIX 3: UPDATE INFRASTRUCTURE MANIFEST GENERATOR":*

```bash
# Add a section to estimate context cost
echo "## Context Budget Estimate" >> $OUTPUT
echo "" >> $OUTPUT
TOTAL_LINES=$(git ls-files | xargs wc -l | tail -n 1 | awk '{print $1}')
echo "- Total tracked lines: $TOTAL_LINES" >> $OUTPUT
echo "- CLAUDE.md size: $(wc -l < .claude/CLAUDE.md) lines" >> $OUTPUT
echo "" >> $OUTPUT
```

## 7. Risk Register

- **Risk:** **Over-Engineering `CLAUDE.md`.**
  - *Impact:* If the file is too long ( > 500 lines), Claude might ignore instructions at the bottom (needle-in-haystack effect).
  - *Mitigation:* Use the "Pointer" pattern. Keep `CLAUDE.md` high-level and move details to `.claude/docs/CONTRACTS.md`, etc.
- **Risk:** **Make dependency.**
  - *Impact:* If `make` is not installed or breaks (syntax error), the agent is paralyzed.
  - *Mitigation:* Ensure `make` availability check in `doctor` and provide direct shell command fallbacks in documentation.
- **Risk:** **False Sense of Security.**
  - *Impact:* "Green" validation might mask logic bugs if tests are shallow.
  - *Mitigation:* Emphasize *E2E* tests (`e2e-smoke`) in the validation commands, not just static analysis.

## 8. Proposed "V5++ Mission Prompt Outline"

1.  **Objective:** "Autonomous Stewardship" (The agent maintains the repo, not just fixes it).
2.  **Phase 1: Dynamic Context:** Replace static `CLAUDE.md` with a dynamic context generator.
3.  **Phase 2: Self-Healing Pipelines:** Implement `make auto-fix` and "DriftOps".
4.  **Phase 3: Cognitive Load Optimization:** Refactor documentation into a hyper-linked knowledge graph optimized for LLM retrieval (RAG-ready docs).
5.  **Phase 4: Behavioral Guardrails:** Implement "Policy as Code" (OPA or similar) to strictly enforce architectural patterns (e.g., "No direct DB access from Dashboard").
