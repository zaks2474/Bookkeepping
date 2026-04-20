# Agent Brain Round 3 Forensic Audit — Run Index

This file is append-only. Each agent run adds an index entry below.

---

## Run Index Entry: 20260204-1300-r3f01

| Field | Value |
|-------|-------|
| agent_name | Claude-Opus-4.5 |
| run_id | 20260204-1300-r3f01 |
| date_time | 2026-02-04T13:00:00-06:00 |
| report_path | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_FORENSIC.Claude-Opus.20260204-1300-r3f01.md` |
| json_path | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_FORENSIC.Claude-Opus.20260204-1300-r3f01.json` |
| overall_score | 4.5/10 |
| production_ready | NO |

### Top 10 Findings

1. **G-001**: `create_deal` not in `HITL_TOOLS` frozenset — executes without approval
2. **G-002**: No grounding enforcement — agent can answer deal questions without tool calls
3. **G-003**: Langfuse tracing not configured in production
4. **G-004**: System prompt lacks M&A domain intelligence (minimal stage context)
5. **G-005**: No tool call budget enforcement (infinite loop risk)
6. **G-006**: No prompt versioning (cannot trace which prompt version was used)
7. **G-007**: Evals have no CI gate (only 10 golden traces)
8. **G-008**: No correlation_id propagation across systems
9. **G-009**: Long-term memory disabled (`DISABLE_LONG_TERM_MEMORY=true`)
10. **G-010**: No deal-scoped memory (cannot recall prior deal conversations)

### Top 10 Recommended Actions

1. Add `create_deal` to `HITL_TOOLS` frozenset in `schemas/agent.py`
2. Add grounding enforcement to system prompt
3. Configure Langfuse API keys in production
4. Rewrite system prompt with M&A domain context
5. Add tool call budget enforcement (max 10 per turn)
6. Add prompt version tracking
7. Add CI gate blocking deployment on eval failure
8. Add correlation_id header propagation
9. Expand eval suite to 30+ golden traces
10. Enable long-term memory with deal-scoped retrieval

### Top 10 Contrarian Risks

1. Agent hallucinates deal details without calling `get_deal` (HIGH/HIGH)
2. `create_deal` executes without HITL approval (HIGH/HIGH)
3. LLM gets stuck in tool-calling loop (no budget)
4. Backend down = agent crash (no circuit breaker)
5. Prompt injection via user message (basic sanitization only)
6. Long conversation exceeds context window (no token budget)
7. Eval suite passes but production fails (only 10 traces)
8. New tool added without HITL consideration (manual process)
9. RAG REST unavailable = search fails hard (no fallback)
10. vLLM returns malformed tool call JSON (no robust parsing)

---

## Run Index Entry: 20260204-1903-1b4aee

| Field | Value |
|-------|-------|
| agent_name | Codex |
| run_id | 20260204-1903-1b4aee |
| date_time | 2026-02-04T19:03:47Z |
| report_path | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_FORENSIC.Codex.20260204-1903-1b4aee.md` |
| json_path | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_FORENSIC.Codex.20260204-1903-1b4aee.json` |
| overall_score | 4.1/10 |
| production_ready | NO |

### Top 10 Findings

1. HITL not enforced for `create_deal` despite prompt claiming it (HITL_TOOLS only transition_deal).
2. Service-token flows trust caller-supplied actor_id; impersonation risk.
3. Non-idempotent write tools (create_deal/add_note) allow duplicates on retries.
4. Tool output schema inconsistent (get_deal/search_deals return plain error strings).
5. No correlation ID propagation across UI -> agent -> backend.
6. Long-term memory disabled by default; no deal-scoped memory.
7. mem0 uses OpenAI provider even in local-vLLM deployments.
8. _tool_call lacks try/except; tool failures can crash the run.
9. RAG results lack provenance and freshness checks.
10. System prompt lacks M&A domain guidance and versioning.

### Top 10 Recommended Actions

1. Add `create_deal` (and other write tools) to HITL enforcement in `schemas/agent.py`.
2. Verify actor_id against auth claims for service-token requests; reject mismatches.
3. Add idempotency keys to create_deal/add_note payloads and backend handling.
4. Implement ToolResult schema and wrap all tool outputs with success/data/error.
5. Add try/except to `_tool_call` to prevent tool exceptions crashing runs.
6. Implement correlation_id middleware and forward headers to backend tools.
7. Add DealContext loader and deal-scoped memory.
8. Add RAG provenance + freshness enforcement.
9. Remove hard OpenAI dependency in mem0 or make it optional via config.
10. Version and harden system prompt with M&A domain rules + grounding policy.

### Top 10 Contrarian Risks

1. Agent creates deals without HITL approval (HIGH/HIGH).
2. Actor impersonation via service-token calls (HIGH/HIGH).
3. Duplicate deal/note creation on retries (MED/HIGH).
4. LLM answers without grounding (HIGH/MED).
5. Tool exceptions crash request (MED/HIGH).
6. RAG outage fails agent responses (MED/MED).
7. Stale approvals never expire (MED/MED).
8. No correlation IDs prevent debugging incidents (HIGH/MED).
9. mem0 calls OpenAI unexpectedly in local-only environments (MED/MED).
10. Prompt drift not versioned; regressions undetected (MED/MED).

---

## Run Index Entry: 20260204-1050-gemini

- **Agent:** Gemini-CLI
- **Run ID:** 20260204-1050-gemini
- **Date:** 2026-02-04
- **Report:** [Markdown](./AGENT_BRAIN_ROUND3_FORENSIC.Gemini.20260204-1050-gemini.md) | [JSON](./AGENT_BRAIN_ROUND3_FORENSIC.Gemini.20260204-1050-gemini.json)

### Top 10 Findings
1. **P1** Blind Agent: No "Deal Context" injected; agent operates blindly.
2. **P1** Amnesic: `DISABLE_LONG_TERM_MEMORY=true` default.
3. **P2** RAG Fragility: `search_deals` tool has no SQL fallback.
4. **P2** Prompt Drift: Tool list hardcoded in `system.md`, not dynamic.
5. **Strength**: HITL architecture (`transition_deal`) is robust (Tier 2+).
6. **Strength**: Idempotency is cryptographic (SHA-256) and restart-safe.
7. **Strength**: Tool schemas are strict (`extra='forbid'`).
8. **Gap**: No "Decision Ledger" for explainability (only raw audit logs).
9. **Gap**: Observability is limited to logs/Langfuse; no OTel spans.
10. **Gap**: Golden Traces exist but aren't integrated into CI regression.

### Top 10 Recommended Actions
1. **INJECT** `DealContext` into system prompt (Stage, Missing Docs, Next Steps).
2. **ENABLE** Long-Term Memory (pgvector/mem0).
3. **IMPLEMENT** RAG Circuit Breaker (SQL Fallback).
4. **AUTOMATE** System Prompt generation from Tool Registry.
5. **CREATE** `decisions` table for reasoning audit.
6. **DEPLOY** Golden Traces to CI pipeline.
7. **ADD** OpenTelemetry spans to `deal_tools.py`.
8. **EXPAND** `GetDealInput` to allow fetching by name/alias.
9. **ADD** "Forget" tool for privacy compliance.
10. **VERIFY** RAG freshness monitor.

### Top 10 Contrarian Risks
1. **Environment Drift**: Dev vs Prod config divergence (vLLM vs Cloud).
2. **Zombie Approvals**: Race conditions in approval claiming (mitigated by atomic SQL).
3. **Prompt Injection**: No specific guardrails against adversarial user input.
4. **Tool Loop**: No explicit "max tool calls" budget visible in graph logic.
5. **Silent Failure**: If RAG is down, agent might say "No deals found" instead of "Error".
6. **Context Window**: Large deal history might overflow prompt context.
7. **Tenant Isolation**: Memory scoping relies on weak `user_id` string.
8. **Stale Data**: Agent might hallucinate off old context if not refreshed.
9. **Model Swap**: Hardcoded prompt tuning might break on model switch.
10. **Cost**: Unbounded context window growth = high token cost.
## FINAL SYNTHESIS ENTRY: 20260204-2004-4b2f4e

| Field | Value |
|-------|-------|
| agent_name | Codex |
| run_id | 20260204-2004-4b2f4e |
| date_time | 2026-02-04T20:04:19Z |
| final_plan_md | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_PLAN_FINAL.md` |
| final_plan_json | `/home/zaks/bookkeeping/docs/AGENT_BRAIN_ROUND3_PLAN_FINAL.json` |

### Top 10 Priorities
1. Enforce HITL for all destructive tools (create_deal, transition_deal, add_note if policy requires).
2. Enforce grounding: deal-specific answers require get_deal/search_deals; refuse if unavailable.
3. Fix actor_id impersonation by validating auth claims and tenant scoping.
4. Standardize ToolResult schema and wrap tool errors with try/except.
5. Add idempotency keys for write tools and backend de-duplication.
6. Implement tool call budget and robust tool-call parsing.
7. Add correlation_id propagation + Langfuse/OTel tracing + prompt versioning.
8. Build decision ledger + response logging with redaction.
9. Enable deal-scoped memory + RAG provenance/freshness + fallback path.
10. Expand evals (>=30 traces) + adversarial suite + CI gate.

### Decision Set Summary
- HITL policy: destructive writes require approval; enforced centrally with tests.
- Grounding policy: deal facts require tools; refuse without data.
- ToolResult schema: unified outputs/errors with robust parsing.
- Idempotency: all write tools include idempotency_key; backend enforces.
- Auth model: actor_id verified against auth claims; tenant scoping.
- Memory: long-term enabled; deal-scoped retrieval; privacy controls.
- RAG: provenance + freshness with SQL/DB fallback; explicit outage behavior.
- Observability: correlation_id propagation; Langfuse/OTel tracing; prompt version tracking.
- Evals: >=30 golden traces + adversarial suite; CI gate.

---
