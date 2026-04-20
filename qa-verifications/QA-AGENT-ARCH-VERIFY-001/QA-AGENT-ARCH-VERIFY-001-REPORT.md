# QA-AGENT-ARCH-VERIFY-001 COMPLETION REPORT

**Date:** 2026-02-07T21:00Z
**Executor:** Claude Opus 4.6 (independent verifier — different instance than builder)
**Verdict:** FAIL (2 of 42 checks failed)
**Source of Truth:** `/home/zaks/bookkeeping/docs/CONSENSUS_DECISION_FINAL.md`
**Supersedes:** Codex run 20260207-2038 (21/42 PASS — many failures were CRLF parsing artifacts)

---

## Summary

- Checks passed: 39/42
- Checks failed: 2
- Informational: 1

---

## Section Results

| Section | Checks | Passed | Failed | Notes |
|---------|--------|--------|--------|-------|
| 1. Agent Files | 6 | 6 | 0 | All 3 agents exist with correct frontmatter, models, tools, prompts, skills |
| 2. Permissions | 8 | 8 | 0 | All permission boundaries verified: guardian/reviewer read-only, test-engineer write-scoped |
| 3. Gate Scripts | 9 | 9 | 0 | All gate scripts exist, run without crashing, validate correct artifacts |
| 4. Makefile | 5 | 4 | 1 | **4.5 FAIL: hardcoded /home/zaks path in Makefile:17** |
| 5. Stop Hook | 4 | 4 | 0 | Stop hook exists, fast-tier only, has timeout, Unix line endings |
| 6. CLAUDE.md | 5 | 5 | 0 | Delegation protocol, agent commands, tool change guide, triggers all present |
| 7. MCP & CLI | 3 | 2 | 0 | GitHub MCP configured; Gate G correctly non-blocking; 1 INFO |
| 8. Integration | 2 | 1 | 1 | **8.1 FAIL: validate-full exit 2 (migration drift)** |

---

## Failed Checks

| Check | Section | Issue | Remediation |
|-------|---------|-------|-------------|
| **4.5** | Makefile Portability | `Makefile:17` contains `USER_HOME ?= /home/zaks` — hardcoded absolute path. Although `?=` is conditional (overridable), the check requires zero `/home/zaks` references. | Replace with `USER_HOME ?= $(HOME)` or `USER_HOME ?= $(shell echo ~)` |
| **8.1** | validate-full Integration | `make validate-full` exits 2. Root cause: `validate-migrations` finds drift in 2 databases: (1) crawlrag — DB unreachable, no `schema_migrations` table; (2) zakops — file=024_correlation_id but DB=022 (2 unapplied migrations). | Apply pending migrations to zakops DB. Either start crawlrag DB or make migration-assertion handle unreachable DBs gracefully. |

### Failure Analysis

**Check 4.5 (Makefile:17):**
```
USER_HOME ?= /home/zaks
```
This is the only remaining hardcoded path. It was introduced as a variable default for `USER_HOME` which is used in other make targets. The `?=` operator means it's overridable via environment, but the default still contains an absolute path. **Severity: LOW** — functional but not portable.

**Check 8.1 (validate-full exit 2):**
This is NOT a gate script bug — the gate is working correctly by detecting real drift:
- **crawlrag DB**: The Zaks-llm RAG database is not running or not reachable from the host. `migration-assertion.sh` correctly reports this as a failure.
- **zakops DB**: Backend has migrations up to `024_correlation_id` on disk, but the live database only has through `022`. Two migrations need to be applied.

**Severity: MEDIUM** — the architecture works but the environment has operational drift. The gate is doing exactly what it should (catching unapplied migrations), but the environment isn't clean.

---

## Bonus Findings (issues not in the build mission)

| # | Finding | Severity |
|---|---------|----------|
| BF-1 | `validate-agent-config.sh` warns about 7 tools in system.md not found in deal_tools.py (`add_note`, `create_deal`, etc.) — this is because the script is looking for function names matching the tool names, but deal_tools.py uses different function names. The gate passes (exit 0) but the warnings indicate the tool-name-to-function mapping is imprecise. | LOW |
| BF-2 | `validate_prompt_tools.py` requires a running database (fails with `psycopg.OperationalError` on DNS resolution for host 'db'). The gate script correctly handles this by skipping and printing a warning, but this means Gate C never runs the full prompt/tool validation in offline mode. | MEDIUM |
| BF-3 | Agent files are at `/home/zaks/.claude/agents/` (user-level) not `/home/zaks/zakops-agent-api/.claude/agents/` (repo-level). This means they're not committed to the repository and are only on this machine. The consensus document (Phase 0) says "Create `.claude/agents/*.md`" which could mean either location. | LOW |

---

## Detailed Check Results

| Check | Result | Evidence |
|-------|--------|----------|
| 1.1 Agent file existence | PASS | All 3 files found at /home/zaks/.claude/agents/ |
| 1.2 YAML frontmatter | PASS | All 3 have valid --- delimiters |
| 1.3 Model assignment | PASS | guardian=sonnet, reviewer=opus, test-engineer=sonnet |
| 1.4 Tool configuration | PASS | All 3 have tools + disallowedTools sections |
| 1.5 System prompt content | PASS | guardian=42, reviewer=82, test-engineer=76 lines |
| 1.6 Skill preloads | PASS | All 7 skill references match consensus 3.12 |
| 2.1 Guardian Edit blocked | PASS | Edit in disallowedTools, not in tools |
| 2.2 Guardian Write blocked | PASS | Write in disallowedTools, not in tools |
| 2.3 Reviewer Edit blocked | PASS | Edit in disallowedTools, not in tools |
| 2.4 Reviewer Write blocked | PASS | Write in disallowedTools, not in tools |
| 2.5 Reviewer Bash blocked | PASS | Bash in disallowedTools, not in tools |
| 2.6 Test-engineer Edit blocked | PASS | Edit in disallowedTools |
| 2.7 Test-engineer Write allowed | PASS | Write in tools, not in disallowedTools; scope refs=10 |
| 2.8 Guardian Bash scoped | PASS | Bash(make:*), Bash(npx:*), etc. in tools; not in disallowed |
| 3.1 Gate C script exists | PASS | validate-agent-config.sh (57 lines, executable) |
| 3.2 Gate C execution | PASS | exit 0 |
| 3.3 Gate C content | PASS | References deal_tools, system.md, tool-schemas |
| 3.4 Gate D script exists | PASS | validate_sse_schema.py (59 lines) |
| 3.5 Gate D execution | PASS | exit 0 |
| 3.6 Gate F multi-DB | PASS | zakops, zakops_agent, crawlrag all referenced |
| 3.7 Gate F execution | PASS | exit 1 (valid failure — detected real drift) |
| 3.8 Gate E SDK enforcement | PASS | httpx=0, BackendClient=22 |
| 3.9 CRLF check | PASS | All gate scripts have Unix line endings |
| 4.1 Required targets | PASS | validate-fast, validate-full, validate-agent-config, validate-sse-schema, validate-migrations |
| 4.2 validate-full composition | PASS | Includes all required sub-targets |
| 4.3 validate-all alias | PASS | Aliases validate-full |
| 4.4 validate-fast execution | PASS | exit 0 |
| 4.5 Makefile portability | **FAIL** | `USER_HOME ?= /home/zaks` at line 17 |
| 5.1 Stop hook exists | PASS | 44 lines, executable |
| 5.2 Fast tier only | PASS | References validate-fast + contract-surfaces |
| 5.3 Timeout protection | PASS | Has timeout mechanism |
| 5.4 Line endings | PASS | Unix (LF) |
| 6.1 Delegation protocol | PASS | "Agent Delegation Protocol" section present |
| 6.2 Agent commands | PASS | contract-guardian, arch-reviewer, test-engineer all referenced |
| 6.3 Tool change guide | PASS | References deal_tools, system.md, tool-schemas |
| 6.4 validate-full | PASS | Documented in essential commands |
| 6.5 Trigger specificity | PASS | Pydantic, migration, LangGraph all mentioned; 0 vague phrases |
| 7.1 GitHub MCP | PASS | Configured in settings.json |
| 7.2 External CLI status | INFO | gemini/codex not installed (optional) |
| 7.3 Gate G non-blocking | PASS | Not in stop hook or validate-full blocking path |
| 8.1 validate-full integration | **FAIL** | exit 2 — migration drift in crawlrag + zakops |
| 8.2 Evidence completeness | PASS | 42 evidence files, 0 empty |

---

## Evidence Location

All evidence stored at:
```
/home/zaks/bookkeeping/qa-verifications/QA-AGENT-ARCH-VERIFY-001/evidence/
  section-1-agent-files/   (check-1.1.txt through check-1.6.txt)
  section-2-permissions/   (check-2.1.txt through check-2.8.txt)
  section-3-gate-scripts/  (check-3.1.txt through check-3.9.txt)
  section-4-makefile/      (check-4.1.txt through check-4.5.txt)
  section-5-stop-hook/     (check-5.1.txt through check-5.4.txt, hook-content.txt)
  section-6-claude-md/     (check-6.1.txt through check-6.5.txt)
  section-7-mcp-cli/       (check-7.1.txt through check-7.3.txt)
  section-8-integration/   (check-8.1.txt through check-8.2.txt)
```

---

## Verification Integrity Notes

1. The builder's completion report was NOT read before running checks.
2. All evidence was captured to files before determining PASS/FAIL.
3. Section 2 (permissions) required re-running due to shell parsing issues with the scoped YAML tool format (`Bash(make:*)`). All 8 checks confirmed PASS on corrected run.
4. Check 3.7 (migration-assertion execution) returned exit code 1 (validation failure — detected real drift), which is acceptable per mission rules ("Exit 1 is OK. Exit 127/126 is FAIL.").
5. Agent files found at `/home/zaks/.claude/agents/` not `/root/.claude/agents/` (since verification runs as root, `~` resolves to `/root/`).
6. Previous Codex run (20260207-2038) reported 20 failures — many were false positives caused by CRLF parsing artifacts in the check scripts. This run used corrected parsing and found only 2 genuine failures.

---

*Generated: 2026-02-07*
*Verifies: AGENT-ARCH-001 (4-agent architecture implementation)*
*Source of truth: CONSENSUS_DECISION_FINAL.md*
*Checks: 42 across 8 sections*
*Stance: Zero trust. Every claim independently verified.*
