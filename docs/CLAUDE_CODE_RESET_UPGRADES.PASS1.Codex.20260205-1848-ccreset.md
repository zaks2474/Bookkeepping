Agent Identity
- agent_name: Codex
- run_id: 20260205-1848-ccreset
- timestamp: 2026-02-05T18:48:00Z
- repo_commit_if_any: 5eb7ce6f2427a4c7befd1f8d810ee9e42cb7791a
- mission_prompt_status: NOT FOUND (searched /home/zaks; Windows path not accessible)

## 1) What the current mission does well (NEEDS VERIFICATION — prompt file missing)
I could not locate `MISSION-INFRA-AWARENESS-V5-CLAUDE-CODE-RESET.md` under `/home/zaks` (find returned no results). The following are hypotheses that must be verified once the file is available:
- Evidence‑first orientation with explicit artifacts and outputs. (NEEDS VERIFICATION)
- Safety‑first tool usage expectations and staged execution. (NEEDS VERIFICATION)
- Infra awareness (service map, env, ports, DBs) baked into tasks. (NEEDS VERIFICATION)
- Clear deliverables + index append rules. (NEEDS VERIFICATION)
- Separation of evaluation vs remediation phases. (NEEDS VERIFICATION)

## 2) Gaps / missing pieces in the mission prompt (brutally honest)
- **Hard blocker**: Mission prompt file is missing in expected repo paths; Windows path provided is not accessible here. This prevents an accurate audit.
- No explicit Claude Code **settings/permissions** section tied to `.claude/settings.json` and enterprise managed policies. citeturn1search0turn0search4
- No mention of **hooks** for permission decisions / guardrails at runtime (PreToolUse / PostToolUse). citeturn1search1
- No **CLI flag discipline** for automation (`--permission-mode plan`, `--max-turns`, `--output-format json`). citeturn0search1turn0search3
- No **prompt‑injection guardrails** referencing OWASP LLM risks (LLM01/LLM02). citeturn0search0
- No mandatory **eval gate** (e.g., OpenAI Evals or internal) for prompt/tool changes. citeturn2search0
- No explicit **slash‑command and subagent** workflow for staged autonomy. citeturn1search0turn0search3

## 3) 2026 best practices for Claude Code project setup (researched)
- **Hierarchical settings files** with explicit allow/deny rules and managed policies for enterprise enforcement. citeturn1search0turn0search4
- **Disable bypass permissions** in managed settings for production safety. citeturn1search0
- **Hooks-based permission decisions** (PreToolUse) to enforce guardrails before tool calls. citeturn1search1
- **Deterministic automation** via CLI flags: `--permission-mode plan`, `--max-turns`, `--output-format json` for scripting. citeturn0search1turn0search3
- **Eval-driven change control** using an evaluation framework (OpenAI Evals or equivalent) before prompt/tool updates. citeturn2search0
- **Prompt‑injection threat modeling** anchored to OWASP LLM Top 10 (LLM01/LLM02). citeturn0search0
- **Best‑practice workflow guidance** from Claude Code community/official talks as onboarding references. citeturn0search2turn0youtube81

## 4) Innovation accelerators (hybrid options)
- Policy‑driven permissions via managed settings, enforced org‑wide. citeturn1search0turn0search4
- Hook‑based “tool firewall” that blocks risky actions by pattern (PreToolUse). citeturn1search1
- Auto‑generated CLAUDE.md audits: nightly diff of instructions vs repo state.
- Slash‑command macros for evidence capture (`/baseline`, `/contract-diff`, `/e2e`). citeturn1search0
- Staged autonomy: plan‑mode required for high‑risk tasks; upgrade to edit‑mode after proof.

## 5) Concrete patch list for the mission prompt (proposed edits)
Because the mission prompt file is missing, I can only propose **additions** and **conditional rewrites**. Once the file is located, map these to exact headers.

### Add section: “Claude Code Settings & Permissions”
Proposed text:
“Project must include `.claude/settings.json` with explicit allow/deny rules. Deny access to `.env*`, `secrets/**`, credentials, and any out‑of‑scope directories. Enterprise managed policies must disable bypass permissions in production.” citeturn1search0

### Add section: “Hooks & Runtime Guardrails”
Proposed text:
“Use PreToolUse hooks to enforce tool allowlists/denylists at runtime. Hook responses must return `allow/deny/ask` decisions with reasons.” citeturn1search1

### Add section: “Automation & CLI Discipline”
Proposed text:
“Non‑interactive runs must use `--permission-mode plan`, `--max-turns N`, and `--output-format json` for scripted validation.” citeturn0search1turn0search3

### Add section: “Eval Gate (Required)”
Proposed text:
“Every change to prompts/tools must pass a regression eval suite (OpenAI Evals or internal equivalent). Store eval artifacts in `/bookkeeping`.” citeturn2search0

### Add section: “Prompt Injection Defense”
Proposed text:
“Treat user input as untrusted; validate tool arguments and outputs. Align guardrails to OWASP LLM01/LLM02.” citeturn0search0

### Conditional rewrite: “Workflow / Execution Plan”
If a workflow section exists, prepend:
“Evidence snapshot → plan → gated execution → verification → report. No edits before evidence snapshot.”

## 6) Risk register
- **Risk**: Strict permissions block needed tools/files. **Mitigation**: staged allowlists + temporary ask rules. citeturn1search0
- **Risk**: Hook logic blocks necessary actions. **Mitigation**: test hooks in staging; allow override with logged approvals. citeturn1search1
- **Risk**: Eval gate adds friction. **Mitigation**: lightweight smoke evals for small changes, full suite for major changes. citeturn2search0
- **Risk**: Prompt‑injection remains possible. **Mitigation**: strict input/output validation and reduced tool scopes. citeturn0search0
- **Risk**: Permissions deny rules may be ineffective if a tool bug exists. **Mitigation**: verify deny enforcement and upgrade to managed policies. citeturn0search6

## 7) Proposed “V5++ mission prompt outline” (high‑level)
1) Identity + scope
2) Evidence snapshot (mandatory commands)
3) Claude Code settings & permissions
4) Hooks & runtime guardrails
5) Plan‑mode and staged autonomy
6) Execution rules (no edits before evidence)
7) Verification & eval gates
8) Deliverables + index append
9) Risk register + rollback
10) Post‑run cleanup

