# CONSENSUS DECISION PIPELINE — MASTER LOG

Tracks all multi-LLM consensus decision pipeline runs.

---

## Run Registry

| Pipeline ID | Decision | Status | PASS 0 Date | Final Date | Verdict | Workspace |
|---|---|---|---|---|---|---|
| CDP-001 | ZakOps Claude Code Agent Topology | PASS 4 v3 COMPLETE | 2026-02-06 | — | **CONDITIONAL PASS** (tabletop v3) | [CONSENSUS_DECISION_WORKSPACE.md](./CONSENSUS_DECISION_WORKSPACE.md) |

---

## CDP-001: ZakOps Claude Code Agent Topology

**Source:** `/home/zaks/bookkeepping/doc/Three_Pass_assessment_001`
**Triggered by:** User — strategic decision on agent architecture for Claude Code
**Contributors:** Claude Code Builder, Claude (Reviewer), Gemini, Codex, GPT

### Pass Log

| Pass | Role | Executor | Date | Status |
|---|---|---|---|---|
| 0 | SCRIBE | Claude Opus 4.6 | 2026-02-06 | COMPLETE |
| 1 | PROPOSER | Codex + Claude Opus 4.5 | 2026-02-07 | COMPLETE (2 proposals) |
| 2 | CRITIC | Gemini-CLI + Codex + Claude Opus 4.5 | 2026-02-07 | COMPLETE (3 reviews) |
| 3 | SYNTHESIZER | Codex | 2026-02-07 | COMPLETE (final doc produced) |
| 4 | TABLETOP SIMULATION | Claude Opus 4.6 | 2026-02-07 | **v1: FAIL** (3/3) → **v2: CONDITIONAL PASS** (1 PASS + 2 CONDITIONAL) → **v3: CONDITIONAL PASS** (0 PASS + 3 CONDITIONAL) |

### Key Artifacts

- Workspace: `/home/zaks/bookkeeping/docs/CONSENSUS_DECISION_WORKSPACE.md`
- Source transcript: `/home/zaks/bookkeepping/doc/Three_Pass_assessment_001`
- Non-negotiables: 8 defined (NN-1 through NN-8)
- Scoring rubric: 6 dimensions, max score 70, pass threshold 49
- Sub-decisions: 4 (SD-1 through SD-4)

- agent_name: Codex
  run_id: 20260207-1806-p1
  timestamp: 2026-02-07T18:07:31Z
  highlights:
    - Role-based 4-agent topology (Builder, Guardian, Arch-Reviewer, Test-Engineer)
    - Contract-Guardian read-only gate after every change
    - Generative config gate for prompts/tool schemas (Surface 8)
    - Agent→Backend contract enforcement via typed SDK or schema gate
    - Shared SSE event schema validation across agent & dashboard
    - Multi-DB migration assertion across zakops, zakops_agent, crawlrag
    - External models used as CLI tools, not subagents
    - Trigger rules for guardian/reviewer/test-engineer
    - Failure modes + detection steps for top 10 risks
    - Phased implementation with acceptance criteria

- agent_name: Claude Opus 4.5
  run_id: 20260207-1845-p1
  timestamp: 2026-02-07T18:45:00Z
  highlights:
    - Role-based 4-agent topology (main-builder, contract-guardian, arch-reviewer, test-engineer)
    - Contract-guardian runs after EVERY change with read-only permissions
    - 6 CI gates + 2 advisory gates (architecture review, integration tests)
    - Surface 8 hybrid: CLAUDE.md checklist + prompts.yaml.lock in .gitignore
    - 5-layer drift prevention (file hashes, make sync-types, CI gate, git hooks, stop hook)
    - Bash allow/deny patterns per agent with minimal permissions
    - External models as CLI tools via subprocess (not subagents)
    - OWASP guardrails as explicit bash deny patterns
    - 10 failure modes with detection + mitigation strategies
    - 6-phase implementation plan (14 days) with binary gates
    - Self-score: 63/70 (90%) — PASS threshold met

## Run Entry
agent_name: Gemini-CLI
run_id: 20260206-1300-gemini
timestamp: 2026-02-06T13:00:00Z
highlights:
1. Proposed 5-Agent Asymmetric Architecture (Architect/Builder/Guardian/Forensic/QA).
2. Defined Generative Configuration (GitOps) for Surface 8 drift prevention.
3. Elevated External Models (Gemini/Codex) to specialized sub-agents.
4. Mandated READ-ONLY permissions for Guardian and Forensic agents.
5. Introduced QA-Adversary role for destructive testing.
6. Scored 50/70 (Pass) on rubric.
7. Defined specific Trigger Rules for Guardian and Forensic agents.
8. Mapped all 8 contract surfaces (including new Agent Config).
9. Identified Top 10 Failure Modes including "Context Saturation".
10. Outlined 4-Phase Implementation Plan starting with "The Guard".

## Run Entry
agent_name: Gemini-CLI
run_id: 20260207-1815-p2
timestamp: 2026-02-07T18:15:00Z
recommendation: CONTROLLED MERGE
highlights:
1. Recommends **Controlled Merge** of Codex/Claude topology + Gemini's Generative Config & QA-Adversary.
2. Identifies **Gemini's Infinite Loop** as a top Kill-Shot Risk.
3. Identifies **Codex/Claude's Context Blindness** as a top Kill-Shot Risk.
4. Mandates **Generative Config** for Surface 8 to eliminate toil.
5. Recommends **QA-Adversary** role instead of standard Test-Engineer.
6. Proposes **Context-Injector Wrapper** for CLI tools to solve context loss.
7. Requires **Multi-DB Migration Gate** for all 3 databases.
8. Scores Codex/Claude 58/70 and Gemini 57/70 - effective tie.
9. Highlights risk of **Guardian Bypass** if not CI-enforced.
10. Calls out **Migration Drift** across databases as a universal risk.

- agent_name: Codex
  run_id: 20260207-1814-p2
  timestamp: 2026-02-07T18:15:06Z
  recommended_winner: Claude (Opus 4.5) with controlled merge (Generative Config + hardened gates)

- agent_name: Claude Opus 4.5
  run_id: 20260207-2245-p2-critic
  timestamp: 2026-02-07T22:45:00Z
  recommended_winner: CONTROLLED MERGE — Claude base + Codex specificity + Gemini Generative Config
  highlights:
    - Re-scored all 3 proposals: Codex 51, Claude 56, Gemini 46 (FAIL NN-5)
    - Flagged NN-5 VIOLATION in Gemini (Gemini 1.5 Pro not in allowed model list)
    - Identified 10 kill-shots per proposal with concrete fixes
    - Mapped 8 drift vectors common to all proposals
    - Quantified coordination overhead: Gemini 3x higher token cost
    - Proposed MVP patches: Codex 200 lines/2 days, Claude 150 lines/1.5 days, Gemini 400 lines/4 days
    - Defined 10 must-add gates for PASS 3 (MG-1 through MG-10)
    - Cross-reviewed Gemini-CLI and Codex PASS 2 submissions
    - Identified consensus: Claude base + Gemini Generative Config (phased)
    - Rejected: Architect/Builder split, QA-Adversary (prefer Test-Engineer)

- agent_name: Codex
  run_id: 20260207-1820-80c8
  timestamp: 2026-02-07T18:20:00Z
  final_doc_path: /home/zaks/bookkeeping/docs/CONSENSUS_DECISION_FINAL.md
  what_changed_vs_alternatives:
    - Rejected domain-split and architect/builder split; chose role-based 4-agent topology.
    - External models integrated as CLI tools only; no Gemini/Codex subagents (NN-5 compliance).
    - Contract-Guardian is mandatory, read-only, and gate-enforced (no self-grading).
    - Arch-Reviewer added for high-impact changes; Test-Engineer retained (no QA-adversary swap).
    - Surface 8 addressed via phased generative config (AST-based), not just checklist.
    - Explicit runnable gates A–H defined (validate-local, contract surfaces, config gen, SSE schema, SDK enforcement, multi-DB migration, CLI availability, stop-hook block).
    - Agent→backend SDK enforcement is mandatory (ban raw httpx in tools).
    - SSE schema validation required for dashboard↔agent contract.
    - Multi-DB migration assertion expanded to zakops, zakops_agent, crawlrag.
    - Stop hook must block on failure; CI required checks added (no paper pass).

## Run Entry — PASS 4: TABLETOP SIMULATION
- agent_name: Claude Opus 4.6
  run_id: 20260207-2330-p4-tabletop
  timestamp: 2026-02-07T23:30:00Z
  status: **FAIL**
  output_doc: /home/zaks/bookkeeping/docs/CONSENSUS_DECISION_TABLETOP_SIM.md
  highlights:
    - Performed ground-truth audit of all 8 gates (A-H) before simulating
    - **Gate C (generate_agent_config.py) does not exist** — pure vapor
    - **Gate D (validate_sse_schema.py) does not exist** — pure vapor
    - **Gate H (stop.sh) always exits 0** — never blocks, even on failure
    - **`.claude/agents/` directory does not exist** — zero agents created
    - Scenario 1 (backend schema change): **FAIL** — `make update-spec` is manual; no live-vs-committed spec diff
    - Scenario 2 (agent tool added): **FAIL** — Gate C is vapor; `validate_prompt_tools.py` not in CI
    - Scenario 3 (multi-DB migration mismatch): **FAIL** — `migration-assertion.sh` not wired into automation; backend SKIP returns 0
    - All 3 scenarios violate kill-switch rule (rely on humans remembering to run something)
    - Proposed 10 enforcement fixes (EF-1 through EF-10)
    - Revised implementation phases: added Phase 0a/0b/0c as blocking prerequisites
    - Added Gate I (check-spec-drift.sh) to gate list
    - Key fix: stop.sh must propagate exit code; validate-agent-config must be created and wired into validate-local; migration-assertion must be wired into validate-live

## Run Entry — PASS 4 v2: TABLETOP SIMULATION (RE-RUN)
- agent_name: Claude Opus 4.6
  run_id: 20260207-2345-p4-tabletop-v2
  timestamp: 2026-02-07T23:45:00Z
  status: **CONDITIONAL PASS**
  supersedes: 20260207-2330-p4-tabletop
  output_doc: /home/zaks/bookkeeping/docs/CONSENSUS_DECISION_TABLETOP_SIM.md
  highlights:
    - 8 of 10 enforcement fixes from v1 have been applied since last run
    - **Gate C now exists** — `generate_agent_config.py` (116 lines, AST-based tool/prompt/MCP validation)
    - **Gate D now exists** — `validate_sse_schema.py` (JSON schema structure + $ref resolution)
    - **Gate H now blocks** — `stop.sh` exits 2 on validate-local failure
    - **Gate I now exists** — `check-spec-drift.sh` (live vs committed spec diff via jq)
    - **validate-local expanded** — now includes validate-agent-config + validate-sse-schema
    - **validate-live expanded** — now includes migration-assertion.sh + check-spec-drift.sh
    - **migration-assertion.sh backend SKIP→FAIL fixed** — unreachable DB = failure, not silent pass
    - Scenario 1 (backend schema change): **CONDITIONAL PASS** — check-spec-drift.sh works but validate-live is manual
    - Scenario 2 (agent tool added): **PASS** — fully automated via stop hook → validate-local → AST-based gate
    - Scenario 3 (multi-DB migration): **CONDITIONAL PASS** — migration-assertion works but validate-live is manual
    - **Single remaining fix:** Automate `make validate-live` (CI pipeline, pre-push hook, or nightly cron)
    - `.claude/agents/` directory still does not exist — Phase 0 not started (workflow gap, not enforcement gap)

## Run Entry — PASS 4 v3: TABLETOP SIMULATION (RE-RUN)
- agent_name: Claude Opus 4.6
  run_id: 20260207-2400-p4-tabletop-v3
  timestamp: 2026-02-07T24:00:00Z
  status: **CONDITIONAL PASS**
  supersedes: 20260207-2345-p4-tabletop-v2
  output_doc: /home/zaks/bookkeeping/docs/CONSENSUS_DECISION_TABLETOP_SIM.md
  highlights:
    - **NEW FINDING: CI pipeline (`ci.yml`) implements NONE of Gates A-H** — plan Section 3.10 claims "CI required checks: Gate A-H" but this is aspirational
    - 4 offline gates (B, C, D, E) have zero service dependencies and COULD run in CI but DON'T
    - `spec-freshness-bot.yml` and `instructions-freshness-bot.yml` exist (daily crons) but are advisory only (`::warning::`, never fail)
    - No script changes since v2 — all gate scripts confirmed unchanged
    - `.claude/agents/` directory still does not exist — Phase 0 not started
    - No pre-push hook, no validate-live cron, no CI job for validate-live
    - Scenario 1 (backend schema change): **CONDITIONAL PASS** — unchanged from v2
    - Scenario 2 (agent tool added): **CONDITIONAL PASS** ↓ (downgraded from PASS in v2) — stop hook catches it but CI does not; bypass via direct git push
    - Scenario 3 (multi-DB migration): **CONDITIONAL PASS** — unchanged from v2
    - **2 remaining patches:** R-1 (automate validate-live) + R-2 (add offline gates B/C/D/E to CI pipeline)
    - Dual-path enforcement model documented: Path 1 (stop hook) = STRONG, Path 2 (CI) = WEAK, Path 3 (validate-live) = MANUAL, Path 4 (bots) = ADVISORY
    - Upgrade to full PASS requires ~1-2 hours of CI wiring (all scripts already exist)
