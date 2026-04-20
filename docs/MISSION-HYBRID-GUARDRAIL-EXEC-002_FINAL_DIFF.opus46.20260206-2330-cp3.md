# EXEC-002 VFINAL vs V1 — Exact Diff Summary

```
AGENT IDENTITY
agent_name:    opus46
run_id:        20260206-2330-cp3
date_time:     2026-02-06T23:30:00Z
pass:          3 of 3 (FINAL)
```

---

## ADDED ITEMS (Not in V1, present in VFinal)

| # | Added Item | Phase | Source (Kill Shot / Missing Piece / Verification) |
|---|-----------|-------|--------------------------------------------------|
| A-01 | EXEC-001 Patterns table (P1-P10) | Preamble | Pass 2 — alignment checklist |
| A-02 | Hard Rules HR-6 through HR-13 | Preamble | Pass 1 KS-4/5/6/8, Pass 2 CR-1 through CR-10 |
| A-03 | Verified Codebase State section | Preamble | Pass 3 — fresh exploration agents |
| A-04 | Dependency Graph (parallel tracks) | Structure | Pass 2 PATCH-18 |
| A-05 | `execution-contracts.ts` in baseline capture | Phase 0 | Pass 1 KS-3, D-14 |
| A-06 | MCP server files in baseline capture | Phase 0 | Pass 1 KS-7 |
| A-07 | Codegen determinism verification (double-run diff) | Phase 1.1 | Pass 1 KS-8, Pass 2 PATCH-02 |
| A-08 | Behavioral migration map (Section 1.3) | Phase 1 | Pass 1 KS-1, Pass 2 PATCH-03 |
| A-09 | "STOP IF NOT_IN_SCHEMA entries" guard | Phase 1.3 | Pass 3 — hardened gate |
| A-10 | `export_openapi.py` for Agent API | Phase 2.1 | Pass 1 KS-4, D-3, Pass 2 PATCH-01 |
| A-11 | Fix 4 missing `response_model` endpoints | Phase 2.2 | Pass 1 audit (18 endpoints, 14/18 with model) |
| A-12 | Event type split-brain resolution (Section 3.0) | Phase 3 | Pass 1 KS-3, D-6, D-14, Pass 2 PATCH-06 |
| A-13 | JSON Schema contract for SSE events | Phase 3.1 | Pass 1 KS-2, D-4, D-8, Pass 2 PATCH-05 |
| A-14 | `agent-event-types.generated.ts` codegen | Phase 3.1 | Pass 2 PATCH-05 |
| A-15 | ESLint enforcement for agent bridge | Phase 3.4 | Pass 2 PATCH-12 |
| A-16 | `make sync-agent-types` target | Phase 3.6 | Pass 2 PATCH-13 |
| A-17 | Legacy import check for agent-api-types in CI | Phase 3.6 | Pass 3 — CI parity with backend |
| A-18 | RAG `export_openapi.py` (Python import) | Phase 4.1 | Pass 1 KS-5, D-5, Pass 2 PATCH-04 |
| A-19 | `mkdir -p src/schemas` for backend | Phase 4.2 | Pass 3 — dir doesn't exist |
| A-20 | Live schema dump prerequisite | Phase 5.0 | Pass 1 KS-10, Pass 2 PATCH-08 |
| A-21 | Migration runner scripts | Phase 5.3 | Pass 1 D-10, Pass 2 PATCH-17 |
| A-22 | MCP server canonicalization (Section 6.0) | Phase 6 | Pass 1 KS-7, Pass 2 PATCH-09 |
| A-23 | `validate-local` / `validate-live` split | Phase 7.2 | Pass 1 KS-9, Pass 2 PATCH-10 |
| A-24 | Real spec-freshness-bot implementation | Phase 7.3 | Pass 3 — discovered placeholder |
| A-25 | 6 negative controls (was 3) | Phase 7.4 | Pass 2 hardened gates |
| A-26 | No-Drift Alignment Contract (full table) | Section B | Pass 3 synthesis |
| A-27 | Residual Risks section (R-1 through R-7) | Section C | Pass 3 synthesis |
| A-28 | `sync-all` Makefile target | Phase 7.2 | Pass 3 — convenience target |
| A-29 | Two docker-compose warning for agent-api | Codebase State | Pass 3 — discovered dual configs |
| A-30 | `check-agent-contract-drift` Makefile target | Phase 2.4 | Pass 2 PATCH-01 |
| A-31 | `check-rag-contract-drift` Makefile target | Phase 4.4 | Pass 2 PATCH-04 |
| A-32 | Explicit "STOP IF FAILS" markers per phase | All phases | Pass 3 — hardened control flow |

---

## REMOVED ITEMS (In V1, removed from VFinal)

| # | Removed Item | Was In | Reason |
|---|-------------|--------|--------|
| R-01 | `curl -s http://localhost:8095/openapi.json` for Agent API spec | Phase 2.1 | KS-4: Returns 404 in production mode. Replaced with `export_openapi.py`. |
| R-02 | `curl -s http://localhost:8052/openapi.json` for RAG spec | Phase 4.3 | KS-5/D-5: RAG is external service. Replaced with `export_openapi.py`. |
| R-03 | `@app.get("/openapi.json")` manual endpoint addition | Phase 2.1 | Pass 1: FastAPI already auto-serves this. Redundant. |
| R-04 | Hand-written `rag_models.py` Pydantic models | Phase 4.1-4.2 | KS-5: RAG already has Pydantic models. Codegen from RAG spec instead. |
| R-05 | `pip install datamodel-code-generator` (unpinned) | Phase 1.2, 7.1 | KS-8: Version non-determinism. Replaced with pinned `==0.26.3`. |
| R-06 | `npx @redocly/cli lint ... \|\| true` for RAG spec | Phase 7.1 | D-12/HR-6: Silent-pass gate. NEVER `\|\| true`. |
| R-07 | `docker exec rag-db psql` (hardcoded container name) | Phase 5.3 | KS-6: Violates RT-HARDEN-001 portability. Use `docker compose exec`. |
| R-08 | `docker exec zakops-agent-db psql` (hardcoded) | Phase 5.3 | KS-6: Same portability violation. Use `docker compose exec -T db`. |
| R-09 | Hardcoded absolute paths in topology.json | Phase 5.4 | HR-7: Use relative paths with `relative_to` field. |
| R-10 | `mapEventType()` reference | Phase 3 context | Pass 1: This function does not exist. Removed false reference. |
| R-11 | Endpoint count "16" | Phase 2 | Pass 1: Actual count is 18. Corrected. |

---

## REORDERED ITEMS

| # | Item | V1 Position | VFinal Position | Reason |
|---|------|-------------|-----------------|--------|
| O-01 | Phase structure | Sequential P0-P7 | Parallel tracks: A(1->2->3), B(4), C(5), D(6), then 7 | Phases 4/5/6 are independent |
| O-02 | Hard Rules section | End of document | Top of document (after directive) | Must be visible BEFORE any phase execution |
| O-03 | EXEC-001 patterns | Not present | Top of document (after hard rules) | Must be referenced by every phase |
| O-04 | MCP canonicalization | Implicit in Phase 6 | Phase 6.0 PREREQUISITE | Must decide canonical server before adding schemas |
| O-05 | Event type resolution | Implicit in Phase 3 | Phase 3.0 PREREQUISITE | Must resolve split-brain before any codegen |
| O-06 | Live schema dump | Not present | Phase 5.0 PREREQUISITE | Must capture reality before creating migrations |
| O-07 | Behavioral migration map | Not present | Phase 1.3 (before 1.4 refactor) | Must map .get() behavior before removing it |

---

## HARDENED GATES (Gates that got stricter)

| # | Gate | V1 Version | VFinal Version | What Changed |
|---|------|-----------|----------------|-------------|
| H-01 | Phase 1 gate | "Zero .get() fallbacks" | "Zero .get() + zero response.json() + behavioral map complete + codegen deterministic" | 4 checks instead of 1 |
| H-02 | Phase 2 gate | "16 endpoints documented" | ">= 18 endpoints + export works offline + canonical JSON verified" | Corrected count + offline verification |
| H-03 | Phase 3 gate | "Manual types eliminated" | "Split-brain resolved + ESLint blocks imports + SSE schema committed + dashboard builds" | 4 new sub-gates |
| H-04 | Phase 4 gate | "rag_models.py exists" | "RAG models CODEGEN'D (not manual) + drift check passes" | Enforces codegen over manual |
| H-05 | Phase 5 gate | "migration-assertion.sh passes" | "Live schema dumped + migration matches live + no hardcoded containers + runner scripts exist" | 4 new sub-gates |
| H-06 | Phase 6 gate | "tool_schemas.py exists" | "ONE canonical server + 12 schemas + validation active + contract committed" | Canonicalization required |
| H-07 | Phase 7 gate | "validate-all exits 0" | "validate-local exits 0 (offline) + 6 NCs pass + no \|\| true + spec-freshness-bot real" | Split local/live + real bot |
| H-08 | Overall stop behavior | Implicit ("fix before proceeding") | Explicit "STOP IF FAILS" with evidence requirements | Hard stops, not suggestions |

---

## CORRECTED FACTS (V1 Errors Fixed)

| # | V1 Claim | Actual | Fix |
|---|----------|--------|-----|
| F-01 | "16 endpoints" | 18 endpoints (8 agent + 4 chatbot + 6 auth) | Updated count |
| F-02 | "NO spec generation" for Agent API | FastAPI auto-generates but gates behind `_enable_docs` | Described actual gating mechanism |
| F-03 | "10+ manual events in mapEventType()" | 21 events in `agent-activity.ts`, `mapEventType()` does NOT exist | Corrected count and removed false reference |
| F-04 | "12 files (1,062 lines)" for backend migrations | 12+ files but numbering skips to 024 | Corrected numbering |
| F-05 | RAG "has NO spec generation" | RAG is FastAPI — auto-generates OpenAPI | Corrected to use RAG's own spec |
| F-06 | "No secret management" for RAG | Out of scope for contract coverage | Removed as not relevant to codegen mission |

---

## PASS 3 ADDITIONS BEYOND PASS 2

Items that VFinal adds BEYOND what the V2-PATCHED draft proposed:

| # | Addition | Source | Why Pass 2 Missed It |
|---|----------|--------|---------------------|
| N-01 | spec-freshness-bot is PLACEHOLDER | Fresh codebase verification | Pass 2 assumed it was functional (just needed extension) |
| N-02 | Backend `src/schemas/` dir doesn't exist | Fresh codebase verification | Pass 2 assumed directory existed for rag_models.py |
| N-03 | Agent API has TWO docker-compose files | Fresh codebase verification | Pass 2 only checked apps/agent-api/docker-compose.yml |
| N-04 | RAG `rag-db` is from external compose | Fresh codebase verification | Pass 2 assumed Zaks-llm compose owns rag-db |
| N-05 | Agent API `export_openapi.py` may fail on LangGraph imports | Fresh verification of import chain | Pass 2 proposed script but didn't consider import-time side effects |
| N-06 | Legacy import check needed for agent-api types in CI | CI workflow analysis | Pass 2 had ESLint but not the grep-based CI backup check |
| N-07 | Residual risks section (R-1 through R-7) | Synthesis of all findings | Pass 2 focused on patches, not residual risk enumeration |
| N-08 | No-Drift Alignment Contract as formal table | Synthesis | Pass 2 had checklist but not structured contract table |
| N-09 | `sync-all` convenience target | Makefile analysis | Quality-of-life addition for developer workflow |
| N-10 | Explicit `--target-python-version 3.12` | pyproject.toml verification (dependencies show Python 3.12 features) | Pass 2 had 3.12 but didn't verify against actual project Python version |

---

## SUMMARY STATISTICS

| Metric | V1 Original | VFinal |
|--------|------------|--------|
| Total phases | 8 (P0-P7) | 8 (P0-P7, same structure) |
| Hard rules | 8 | 13 (+5) |
| Makefile targets (new) | 4 | 9 (+5) |
| Gate checks (total) | ~15 | ~42 (+27) |
| Negative controls | 3 | 6 (+3) |
| STOP IF markers | 0 | 8 (one per phase + prerequisites) |
| Facts corrected | 0 | 6 |
| Items added | 0 | 32 |
| Items removed | 0 | 11 |
| Items reordered | 0 | 7 |
| Gates hardened | 0 | 8 |
| Residual risks documented | 0 | 7 |
| Contrarian passes synthesized | 0 | 3 (Pass 1 + Pass 2 + Pass 3 verification) |

---

*Generated: 2026-02-06T23:30:00Z*
*Auditor: Claude Code (Opus 4.6)*
*Protocol: PASS 3 (Final Synthesis)*
