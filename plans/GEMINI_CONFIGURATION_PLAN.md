# Gemini Configuration Plan
## Mirroring Codex & Claude Code Infrastructure for ZakOps

**Status:** Draft
**Date:** February 12, 2026
**Target:** Gemini CLI (`gemini`)

---

## 1. Executive Summary

This plan outlines the steps to configure the Gemini CLI to achieve parity with the operational standards of Codex and Claude Code within the ZakOps environment. Currently, Gemini lacks the "wrapper lifecycle" (Boot Diagnostics, Halts, Validation), persistent memory, and defined contract surfaces that govern the other agents.

**Goal:** Elevate Gemini from a basic CLI tool to a full-fledged ZakOps agent with:
1.  **Strict Identity:** A constitution (`GEMINI.md`) defining its role and constraints.
2.  **Persistent Memory:** A `MEMORY.md` file with AutoSync sentinels.
3.  **Safety Wrapper:** A `gemini-safe` launcher enforcing boot checks and post-session validation.
4.  **Tool Parity:** Configuration for GitHub and Playwright MCP servers.
5.  **Project Integration:** Recognition of the 14 contract surfaces.

---

## 2. Gap Analysis

| Feature | Codex / Claude Code (Standard) | Gemini (Current) | Gap |
| :--- | :--- | :--- | :--- |
| **Global Config** | `.codex/config.toml` / `.claude/settings.json` | `.gemini/settings.json` (Empty) | **Critical:** No tool/behavior definitions. |
| **Identity** | `AGENTS.md` / `CLAUDE.md` | `GEMINI.md` (Generic readme) | **Critical:** Missing role/surface definitions. |
| **Memory** | `MEMORY.md` with AutoSync | None | **Critical:** Amnesic between sessions. |
| **Lifecycle** | `codex-boot.sh` / `session-start.sh` | None | **Critical:** No pre-flight checks. |
| **Validation** | `codex-stop.sh` (Auto-validate) | None | **Critical:** No post-session drift check. |
| **Launcher** | `codex-safe` (Wrapper) | Raw `gemini` command | **Critical:** Bypasses safety layer. |
| **MCP Tools** | GitHub, Playwright (configured) | None | **High:** Missing capabilities. |

---

## 3. Implementation Plan

### Phase 1: Directory Structure & Global Config

1.  **Create Global Config Directory:**
    *   Ensure `/home/zaks/.gemini` exists.
    *   Create `/home/zaks/.gemini/projects/-home-zaks/memory/` for persistent memory.

2.  **Define Global Settings (`settings.json`):**
    *   Populate `/home/zaks/.gemini/settings.json` with:
        *   **MCP Servers:** GitHub (local binary), Playwright (headless, isolated).
        *   **Hooks:** Mirror Claude's hook registration (PreToolUse, SessionStart, Stop) if supported by Gemini CLI, or emulate via wrapper.
        *   **Permissions:** Set default deny rules mirroring Claude.

3.  **Create Global Constitution (`AGENTS.md`):**
    *   Create `/home/zaks/.gemini/AGENTS.md` (or `INSTRUCTIONS.md`).
    *   Content: Global operational rules, service map, "No-Go" zones (e.g., port 8090).

### Phase 2: Project-Level Configuration

1.  **Create Project Constitution (`GEMINI.md`):**
    *   **Action:** Rewrite `/home/zaks/GEMINI.md` (Root) to match `CLAUDE.md` (Root) - Operational Quick Reference.
    *   **Action:** Create `/home/zaks/zakops-agent-api/GEMINI.md` (Monorepo) to match `CLAUDE.md` (Monorepo) - Full Constitution.
        *   Include the **14 Contract Surfaces** definition.
        *   Include the **Hybrid Guardrail** pattern.
        *   Include **TriPass** role definition.

2.  **Create Project Config Directory:**
    *   Create `/home/zaks/zakops-agent-api/.gemini/`.
    *   Create `rules/` and `commands/` subdirectories.

3.  **Port Rules & Commands:**
    *   Copy critical rules (e.g., `backend-api.md`, `contract-surfaces.md`) from `.claude/rules/` to `.gemini/rules/`.
    *   Copy critical commands (e.g., `infra-check.md`, `tripass.md`) from `.claude/commands/` to `.gemini/commands/`.

### Phase 3: The Wrapper Lifecycle (Safety Layer)

1.  **Create `scripts/gemini-boot.sh`:**
    *   **Purpose:** Pre-session diagnostics.
    *   **Logic:**
        *   Check 1: Memory Integrity (exists?).
        *   Check 2: Surface Count (matches `GEMINI.md`?).
        *   Check 3: Generated Files (exist?).
        *   **Output:** Verdict (`ALL CLEAR`, `PROCEED WITH CAUTION`, `HALT`).

2.  **Create `scripts/gemini-stop.sh`:**
    *   **Purpose:** Post-session cleanup & validation.
    *   **Logic:**
        *   Run `make validate-local` (if mutations occurred).
        *   Sync `MEMORY.md` stats (AutoSync).
        *   Update `CHANGES.md` (if needed).

3.  **Create `scripts/gemini-wrapper.sh` (The Launcher):**
    *   **Purpose:** Orchestrate Boot -> Run -> Stop.
    *   **Logic:**
        1.  Run `gemini-boot.sh`.
        2.  If `HALT`, block execution (unless `GEMINI_FORCE=1`).
        3.  Run actual `gemini` CLI with args.
        4.  Run `gemini-stop.sh` on exit.
    *   **Alias:** Suggest aliasing `gemini-safe` to this script.

### Phase 4: Memory System

1.  **Initialize `MEMORY.md`:**
    *   Create `/home/zaks/.gemini/projects/-home-zaks/memory/MEMORY.md`.
    *   Content: Standard header, "Active Context", "System Architecture", "AutoSync Sentinels".

### Phase 5: Verification

1.  **Boot Check:** Run `scripts/gemini-wrapper.sh --version`.
    *   Expect: Boot diagnostics output + Gemini version.
2.  **Memory Check:** Verify `MEMORY.md` exists and is readable.
3.  **Tool Check:** Run `gemini mcp list` (via wrapper) to confirm GitHub/Playwright.

---

## 4. Next Steps

1.  **Approve this plan.**
2.  **Execute Phase 1 & 2** (Config & Identity).
3.  **Execute Phase 3** (Wrapper Scripts).
4.  **Execute Phase 4** (Memory).
5.  **Verify.**

