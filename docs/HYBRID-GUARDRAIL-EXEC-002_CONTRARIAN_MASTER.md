# HYBRID-GUARDRAIL-EXEC-002 — Contrarian Audit Master Index

---

## Run Index

### Pass 1 — opus46 — 20260206-1936-cp1

- **agent_name:** opus46
- **run_id:** 20260206-1936-cp1
- **date_time:** 2026-02-06T19:36:36Z
- **repo_revision:** agent-api=b96b33c, backend=8546734, zaks-llm=56acbb9
- **file_path:** `/home/zaks/bookkeeping/docs/HYBRID-GUARDRAIL-EXEC-002_CONTRARIAN_PASS1.opus46.20260206-1936-cp1.md`

#### Top 10 Kill Shots

| # | Kill Shot | Severity | Summary |
|---|-----------|----------|---------|
| KS-1 | Agent tool behavioral regression | P0 | Replacing 25 `.get()` fallbacks with typed access changes error behavior from silent-default to crash |
| KS-2 | SSE types cannot be generated from OpenAPI | P0 | OpenAPI has no standard for SSE event type enumeration; 36 manual event types will remain manual |
| KS-3 | Dual event type split-brain | P0 | `agent-activity.ts` uses `agent.run_started`, `execution-contracts.ts` uses `run_started` — incompatible; EXEC-002 doesn't address |
| KS-4 | Agent API spec behind feature flag | P0 | OpenAPI endpoint returns 404 in production mode; CI spec fetch will fail |
| KS-5 | RAG contract uses manual models | P1 | Creates hand-written Pydantic models instead of codegen from RAG's own OpenAPI — violates Hybrid Guardrail thesis |
| KS-6 | Migration assertion hardcodes container names | P1 | `docker exec rag-db` / `zakops-agent-db` — violates RT-HARDEN-001 portability requirement |
| KS-7 | Three MCP servers, one schema | P1 | Schemas added to `server.py` don't protect `server_http.py` or `server_sse.py` |
| KS-8 | datamodel-code-generator non-determinism | P1 | No version pin; output varies by version; drift check becomes flaky gate |
| KS-9 | validate-all unusable with 6+ surfaces | P1 | 6 services must be healthy simultaneously; probability drops exponentially |
| KS-10 | No rollback for crawlrag migration | P1 | Initial migration may not match live schema; no verification step proposed |

#### Top 10 Missing Pieces

| # | Missing Piece | Impact |
|---|---------------|--------|
| D-1 | Agent API startup for CI | Cannot fetch spec without running service; no docker-compose exists |
| D-2 | datamodel-code-generator version pin | CI/local output mismatch → false drift detection |
| D-3 | Agent API generate-from-code script | RT-HARDEN-001 solved this for backend; not replicated for agent |
| D-4 | SSE event type contract format | OpenAPI can't describe SSE events; no alternative proposed |
| D-5 | Cross-repo service orchestration | RAG is in separate repo; CI can't start it |
| D-6 | execution-contracts.ts not addressed | 585-line file with 15 agent types completely ignored |
| D-7 | Two bridge files for agent types | api.ts already has `AgentRunApiResponse`; new `agent-api.ts` creates dual bridge |
| D-8 | Migration runner for agent/RAG | Migration FILES created but no RUNNER to apply them |
| D-9 | `|| true` in Phase 7 CI | Violates RT-HARDEN-001 Hard Rule #3 |
| D-10 | RAG secret management | `crawl4aipass` hardcoded in default env |

---

### Pass 2 — opus46 — 20260206-2200-cp2

- **agent_name:** opus46
- **run_id:** 20260206-2200-cp2
- **date_time:** 2026-02-06T22:00:00Z
- **repo_revision:** agent-api=b96b33c, backend=8546734, zaks-llm=56acbb9
- **report_path:** `/home/zaks/bookkeeping/docs/HYBRID-GUARDRAIL-EXEC-002_CONTRARIAN_PASS2.opus46.20260206-2200-cp2.md`
- **patched_mission_path:** `/home/zaks/bookkeeping/docs/MISSION-HYBRID-GUARDRAIL-EXEC-002_PATCHED_V2.opus46.20260206-2200-cp2.md`

#### Top 10 Patches (PASS1 Risks -> Concrete Plan Edits)

| # | Patch | Mitigates | Where | Key Change |
|---|-------|-----------|-------|------------|
| P-01 | Agent API `export_openapi.py` | KS-4, D-3 | Phase 2.1 | Python import replaces `curl localhost:8095` — works in CI without running service |
| P-02 | Pin `datamodel-code-generator` version | KS-8, D-2 | Phase 1.2 | `==0.26.3` in pyproject.toml; deterministic output proven via double-run diff |
| P-03 | Behavioral migration map | KS-1 | Phase 1.3a (new) | 25 `.get()` calls classified: REQUIRED/OPTIONAL/NOT-IN-SCHEMA before any refactoring |
| P-04 | RAG codegen from own OpenAPI | KS-5 | Phase 4 (replaced) | Fetch RAG spec -> codegen -> drift check. No hand-written Pydantic models. |
| P-05 | JSON Schema for SSE events | KS-2, D-4 | Phase 3.2a (new) | Python Enum -> JSON Schema -> `json-schema-to-typescript` -> CI drift check |
| P-06 | Event type split-brain resolution | KS-3, D-6 | Phase 3.0 (new) | Unify `agent-activity.ts` + `execution-contracts.ts` into ONE canonical source |
| P-07 | Portable container discovery | KS-6 | Phase 5.3 | `docker compose exec` (service names) replaces `docker exec` (container names) |
| P-08 | Live schema dump before migration | KS-10 | Phase 5.0 (new) | `pg_dump --schema-only` -> diff against proposed migration -> evidence |
| P-09 | MCP server canonicalization | KS-7 | Phase 6.0 (new) | Archive 2 of 3 server files; schemas apply to ONE canonical implementation |
| P-10 | Split `validate-all` local/live | KS-9 | Phase 7.1a (new) | `validate-local` (CI, offline), `validate-live` (needs services), `validate-all` (both) |

#### Top 10 Hardened Gates

| # | Gate | Phase | Check | Exit Code |
|---|------|-------|-------|-----------|
| G-01 | Codegen determinism | P1 | Run datamodel-codegen twice, diff output | empty diff |
| G-02 | Behavioral map complete | P1 | 25/25 .get() calls classified | evidence file |
| G-03 | Spec export offline | P2 | `export_openapi.py` works without network | valid JSON |
| G-04 | Split-brain resolved | P3 | One canonical EventType definition | 1 file |
| G-05 | ESLint blocks generated imports | P3 | Add test import -> lint fails | exit 1 |
| G-06 | RAG models codegen'd (not manual) | P4 | `git diff --exit-code rag_models.py` after regen | 0 |
| G-07 | Live schema matches migration | P5 | diff live dump vs 001_initial_schema.sql | reviewed |
| G-08 | No hardcoded container names | P5 | `grep "docker exec [a-z]" assertion.sh` | 0 matches |
| G-09 | One canonical MCP server | P6 | `ls server*.py \| grep -v archived` | 1 file |
| G-10 | Zero `\|\| true` in CI | P7 | `grep '\|\| true' ci.yml` | 0 matches |

---

### Pass 3 (FINAL) — opus46 — 20260206-2330-cp3

- **agent_name:** opus46
- **run_id:** 20260206-2330-cp3
- **date_time:** 2026-02-06T23:30:00Z
- **repo_revision:** agent-api=b96b33c, backend=8546734, zaks-llm=56acbb9
- **final_mission_path:** `/home/zaks/bookkeeping/docs/MISSION-HYBRID-GUARDRAIL-EXEC-002_FINAL.opus46.20260206-2330-cp3.md`
- **diff_summary_path:** `/home/zaks/bookkeeping/docs/MISSION-HYBRID-GUARDRAIL-EXEC-002_FINAL_DIFF.opus46.20260206-2330-cp3.md`
- **verdict:** EXECUTE — Plan is hardened and implementation-ready

#### Top 10 "Must Not Miss" Items

| # | Item | Why It Matters | Phase |
|---|------|---------------|-------|
| 1 | Behavioral migration map BEFORE refactoring | 25 `.get()` fallbacks provide silent degradation; typed access changes error semantics. Map each one BEFORE touching code. | P1.3 |
| 2 | `export_openapi.py` for Agent API (NOT curl) | Agent OpenAPI is gated behind `_enable_docs` flag — returns 404 in production mode. Python import bypasses this. | P2.1 |
| 3 | Resolve event type split-brain FIRST | `agent-activity.ts` (dot-prefix) vs `execution-contracts.ts` (no prefix) are incompatible. Codegen without resolution creates a THIRD set. | P3.0 |
| 4 | JSON Schema for SSE events (NOT OpenAPI) | OpenAPI cannot describe SSE event type enumerations. `openapi-typescript` won't generate useful SSE types. Use JSON Schema + `json-schema-to-typescript`. | P3.1 |
| 5 | Codegen RAG models from RAG's own spec | RAG is FastAPI with Pydantic models. Hand-writing duplicate models is the EXACT anti-pattern the Hybrid Guardrail eliminates. | P4.1-4.2 |
| 6 | Dump live crawlrag schema BEFORE migration | `CREATE TABLE IF NOT EXISTS` is idempotent but `CREATE INDEX` may fail if indexes exist with different names. Diff live vs proposed. | P5.0 |
| 7 | Canonicalize MCP to ONE server | Three implementations (12+10+10 tools). Schemas on one leave others unprotected. Archive non-canonical before adding schemas. | P6.0 |
| 8 | `validate-local` must work offline | CI cannot depend on 6+ services being healthy. Split into `validate-local` (CI) and `validate-live` (developer). | P7.2 |
| 9 | spec-freshness-bot is PLACEHOLDER | Current implementation is just echo statements. Must replace with real spec-vs-code comparison for both Backend and Agent API. | P7.3 |
| 10 | Pin `datamodel-code-generator==0.26.3` | Unpinned version = different output per CI run = flaky drift detection = blocked pipeline. Verify determinism with double-run diff. | P1.1 |

#### Pass 3 Additions Beyond Pass 2

| # | Discovery | Impact |
|---|-----------|--------|
| N-01 | spec-freshness-bot is PLACEHOLDER (echo only) | Phase 7 must implement real bot, not just extend |
| N-02 | `zakops-backend/src/schemas/` dir doesn't exist | Phase 4 must `mkdir -p` before codegen |
| N-03 | Agent API has TWO docker-compose files | Migration assertions must target correct compose |
| N-04 | RAG `rag-db` is from external compose network | Container discovery more complex than assumed |
| N-05 | Agent API import chain may pull LangGraph at spec-export time | `export_openapi.py` may need lazy imports |
| N-06 | Legacy import check needed for agent types in CI | ESLint alone not sufficient — need grep-based backup |
| N-07 | 7 residual risks documented with detection + mitigation | Production readiness awareness |

#### Diff Statistics (VFinal vs V1)

| Metric | Count |
|--------|-------|
| Items added | 32 |
| Items removed | 11 |
| Items reordered | 7 |
| Gates hardened | 8 |
| Facts corrected | 6 |
| Hard rules added | 5 (HR-6 through HR-13) |
| Makefile targets added | 9 |
| Gate checks total | ~42 (was ~15) |
| Negative controls | 6 (was 3) |
| STOP IF markers | 8 |
| Residual risks | 7 |

---

## Pipeline Complete

| Pass | Role | Verdict | Key Contribution |
|------|------|---------|-----------------|
| Pass 1 | Contrarian Auditor | HOLD | 10 kill shots, 15 missing pieces — found structural gaps |
| Pass 2 | Patch Engineer | CONDITIONAL GO | 18 patches, hardened gates — fixed all P0 kill shots |
| Pass 3 | Final Synthesizer | EXECUTE | Fresh verification, 10 new discoveries, residual risks, implementation-ready prompt |

**FINAL VERDICT: The mission prompt is ready for execution.**

The VFinal prompt addresses all 10 kill shots from Pass 1, integrates all 18 patches
from Pass 2, adds 10 new discoveries from fresh codebase verification, documents 7
residual risks with detection/mitigation strategies, and includes 8 explicit "STOP IF
FAILS" control flow markers.

---

### META-QA — opus46 — 20260207-0015-mqa

- **agent_name:** opus46
- **run_id:** 20260207-0015-mqa
- **date_time:** 2026-02-07T00:15:00Z
- **report_path:** `/home/zaks/bookkeeping/docs/HYBRID-GUARDRAIL-EXEC-002_META_QA.opus46.20260207-0015-mqa.md`
- **json_path:** `/home/zaks/bookkeeping/docs/HYBRID-GUARDRAIL-EXEC-002_META_QA.opus46.20260207-0015-mqa.json`
- **verdict:** PASS — VFINAL is implementation-ready

#### Gate Results

| Gate | Description | Verdict |
|------|-------------|---------|
| GATE 0 | Required files present | PASS (6/6) |
| GATE 1 | No-drop contract surfaces | PASS (7/7) |
| GATE 2 | EXEC-001 architecture alignment | PASS (10/10 patterns) |
| GATE 3 | Determinism / reproducibility | PASS (zero CI bypasses) |
| GATE 4 | Negative controls | PASS (6 NCs) |
| GATE 5 | Full-stack proof artifacts | PASS (8 evidence dirs) |
| GATE 6 | Stop conditions + rollback | PASS (8 stops, 7 risks) |

#### Minor Findings (Non-Blocking)

| # | Finding | Impact |
|---|---------|--------|
| MF-01 | `.get()` count: VFINAL says 25, grep returns 39 (14 are utility .get()) | Low — migration map classifies each |
| MF-02 | spec-freshness-bot PLACEHOLDER confirmed | None — VFINAL Phase 7.3 replaces |

---

## Full Pipeline Status

| Stage | Role | Verdict | Key Contribution |
|-------|------|---------|-----------------|
| Pass 1 | Contrarian Auditor | HOLD | 10 kill shots, 15 missing pieces — found structural gaps |
| Pass 2 | Patch Engineer | CONDITIONAL GO | 18 patches, hardened gates — fixed all P0 kill shots |
| Pass 3 | Final Synthesizer | EXECUTE | Fresh verification, 10 new discoveries, residual risks, implementation-ready prompt |
| META-QA | Quality Gate | **PASS** | 7/7 gates pass, 10/10 KS resolved, 2 minor findings (non-blocking) |

**FINAL STATUS: CLEARED FOR EXECUTION.**

The VFINAL mission prompt has passed all quality gates:
- 3/3 contrarian passes delivered
- META-QA gate: PASS (7/7 gates)
- 10/10 kill shots resolved
- 7/7 contract surfaces covered
- 10/10 EXEC-001 patterns aligned

---

*Master file created: 2026-02-06*
*Pass 2 appended: 2026-02-06*
*Pass 3 (FINAL) appended: 2026-02-06*
*META-QA appended: 2026-02-07*
*Pipeline status: COMPLETE + QUALITY-GATED — Cleared for execution*
