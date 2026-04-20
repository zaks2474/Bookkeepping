# CLAUDE_CODE_RESET_V5PP_PASS1.Gemini-CLI.20260207-1230-pass1.md

## 1. Agent Identity
- **Agent Name:** Gemini-CLI
- **Run ID:** 20260207-1230-pass1
- **Timestamp:** 2026-02-07T12:30:00Z
- **Repo Revision:** unknown

## 2. Snapshot of V5 Current State
The "V5" mission prompt describes a comprehensive "Total Recall" system with 7 contract surfaces, dependency graphs, and strict protocols. However, the **actual** `CLAUDE.md` on disk (verified via `read_file`) is a legacy artifact. It lists basic service ports and some "Golden Commands" but lacks the sophisticated "Brain" infrastructure described in the V5 prompt. The system is effectively running on V3/V4 knowledge while aspiring to V5.

## 3. Best-in-Class Ideas (2026)
*   **Dynamic Context:** Static docs rot. Best-in-class setups use a `pre-command` hook that generates a `context.md` containing *live* system state (e.g., `docker ps` output, `git status`, recent build failures).
*   **DriftOps:** Instead of just *checking* for drift (`make check-drift`), the system should *auto-correct* it on commit (e.g., `make fix-drift` run by a bot).
*   **Epistemic Markers:** Files should carry metadata headers (`@generated`, `@manual`, `@frozen`) that the agent parses to determine its own permissions per-file.

## 4. Innovation Accelerators
*   **`make auto-fix`**: A "Do What I Mean" target that runs formatters, linters, type-syncs, and spec-updates in the correct dependency order.
*   **Impact Analysis Script**: A tool that accepts a filepath and returns a list of *dependent* files/services, allowing the agent to predict the blast radius of a change.
*   **Scope-Locked Modes**: "I am working on the Dashboard." -> Agent loads *only* dashboard context and refuses to touch backend files without explicit override.

## 5. Concrete Patches for Mission Prompt
*   **Add "Self-Correction" Loop:**
    *   *Current:* "If validation fails, fix it."
    *   *Proposed:* "If validation fails, run `make auto-fix` first. Only ask human if that fails."
*   **Enhance "Pre-Task Protocol":**
    *   *Current:* "Read CLAUDE.md"
    *   *Proposed:* "Run `tools/context.sh` to generate session context. Read `SESSION_CONTEXT.md`."

## 6. Risks & Mitigations
*   **Risk:** **Context Bloat.** The V5 prompt adds a massive amount of text to `CLAUDE.md`.
    *   *Mitigation:* Use the "Pointer Pattern". `CLAUDE.md` contains high-level rules and links to `docs/contracts/*.md`.
*   **Risk:** **False Confidence.** "Green" validation might mask logic errors.
    *   *Mitigation:* Enforce "Behavioral Unit Tests" (e.g., "Did the agent check the debt ledger?").

## 7. Top 5 "If We Only Do This"
1.  **Overwrite `CLAUDE.md`** with the V5 content (it's currently missing).
2.  **Implement `make auto-fix`** to reduce agent toil.
3.  **Create `tools/context.sh`** for dynamic context injection.
4.  **Enforce `@generated` headers** to prevent regression.
5.  **Add "Impact Analysis"** to the pre-task workflow.
