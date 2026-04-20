# CLAUDE_CODE_RESET_V5PP_PASS2.Codex.20260207-0245-pass2.md

## 1. Agent Identity
- **Agent Name:** Codex
- **Run ID:** 20260207-0245-pass2
- **Timestamp:** 2026-02-07T02:45:00Z
- **Repo Revision:** (Unknown)

## 2. Red-Team Analysis of PASS 1 Ideas

### A. The "Context" Conflict
*   **Gemini** proposed `context.sh` (dynamic script).
*   **Claude** proposed `.claude/rules/*.md` (path-scoped rules) + split `CLAUDE.md`.
*   **Critique:** `context.sh` is a hack that requires manual running or a complex hook setup. Native `.claude/rules/` with `paths:` frontmatter is the 2026 "Claude Native" way to handle context. It automatically loads relevant info when files are touched.
*   **Verdict:** **Reject** `context.sh`. **Keep** Path-Scoped Rules + Constitution Split.

### B. The "Enforcement" Trap
*   **V5 Prompt** relies heavily on `make check` commands that the user must run.
*   **Codex (Pass 1)** proposed `settings.json` permissions (`deny` edits to generated files).
*   **Gemini** proposed "Epistemic Markers" (comments in files).
*   **Critique:** Comments are weak ("please don't edit"). Permissions are strong ("cannot edit"). Permissions prevent the error before it happens.
*   **Verdict:** **Keep** `permissions.deny` in `settings.json` as the primary guardrail.

### C. The "Automation" Risk
*   **Gemini** proposed "DriftOps" (auto-commit fixes).
*   **Claude** proposed "Contract-Checker Subagent" (validate on demand).
*   **Critique:** Auto-committing code changes via a background bot while an agent is also working can cause git lock contention and confusion. Better to have a subagent *propose* the fix or a pre-commit hook *block* the bad commit.
*   **Verdict:** **Reject** background auto-commit bots. **Keep** Subagent validators.

### D. The "Missing Piece"
*   None of the agents explicitly addressed **Token Budgeting** for the "Total Recall" strategy. V5 wants to dump *everything* into context.
*   **Solution:** The "Constitution" pattern (Claude's idea) solves this by only loading high-level rules, with detailed specs loaded lazily via Rules or Subagents.

## 3. Recommended "Final Shape" for V5PP

**The "Claude Native" Architecture:**
1.  **Settings (`.claude/settings.json`)**: Hard guardrails.
    *   `permissions.deny`: `["Edit(*/generated.ts)", "Edit(*_models.py)"]`
    *   `additionalDirectories`: Cross-repo access.
2.  **Constitution (`CLAUDE.md`)**: Slim (~150 lines). High-level philosophy, map of the system, and pointers to skills.
3.  **Path-Scoped Rules (`.claude/rules/`)**: Context injection.
    *   `contracts.md`: Loads when `packages/contracts` is touched.
    *   `backend.md`: Loads when `zakops-backend` is touched.
4.  **Hooks (`.claude/hooks/`)**: Active defense.
    *   `PreToolUse`: Block forbidden patterns (e.g. `docker rm` without flag).
    *   `PostToolUse`: Auto-run `make sync-*` if a spec file was just edited.
5.  **Subagents (`.claude/agents/`)**: Specialized workers.
    *   `contract-checker`: Knows how to run all 7 validation suites.

## 4. Concrete Patch Plan
The V5 mission prompt needs to be rewritten to **stop implementing V4 patterns** (monolithic CLAUDE.md, manual checks) and **start implementing V5PP patterns** (Settings, Rules, Hooks).

*   **Delete** "FIX 1: REWRITE CLAUDE.md" (Monolithic).
*   **Replace with** "FIX 1: IMPLEMENT CLAUDE NATIVE CONFIG" (Settings + Rules + Slim CLAUDE.md).
*   **Add** "FIX 2: CONFIGURE PERMISSIONS & HOOKS".
