# ZakOps Infrastructure Strategy — Implementation-Ready Plan
# Hybrid Guardrail: Codegen + Slim V4

**Status:** APPROVED — All 6 META-QA patches + 5 review feedback patches applied
**Base:** PASS3 Final (Codex, 20260206-0444-740d)
**Patches from:** META-QA (Opus, 20260206-0530-b9e1)
**Review feedback from:** External Review A (correlation ID, golden payloads, scaffolder) + External Review B (ESLint error, Zod wrapper ceiling)
**Detail source:** PASS2 Ship Plan (Opus, 20260206-0445-a7c3)
**Date:** 2026-02-06 (Rev 2)

---

## A) Final Decision

Adopt the Hybrid Guardrail strategy: keep V4's Claude-context primitives (topology discovery, manifest age gate, CLAUDE preflight protocol, enforcement audit) and the RAG routing proof, but replace hand-written dashboard schemas with generated API types from the FastAPI OpenAPI spec (`openapi-typescript`) plus thin manual Zod wrappers at the API boundary; enforce codegen + typecheck in CI via a single `make sync-types` workflow so drift becomes structurally unshippable while preserving the only V4 components that are uniquely necessary.

**One-sentence summary:** Replace the 488-line hand-written Zod schemas with types generated from FastAPI's OpenAPI spec via `openapi-typescript`, enforce alignment with `tsc --noEmit` in CI, keep V4's topology discovery and RAG routing proof for Claude context, and delete the 1,150+ lines of bash schema-diffing scripts that are now redundant.

---

## B) Why This Wins

- V4 already passes 15/15 gates and provides Claude context, but its 3,290+ lines of scripts are reactive and fragile; swapping schema diffing for codegen removes the largest drift source without losing the V4 context that Claude requires.
- The biggest observed failures are hand-written Zod mismatches and silent safeParse fallbacks; generated types + compiler gates prevent these by construction.
- OpenAPI already exists and is the natural contract boundary for a FastAPI → Next.js stack, enabling incremental adoption without a monorepo rewrite.
- Claude Code's session resets make "one-command sync + preflight bundle" materially safer than multi-step protocols; fewer steps = fewer skipped gates.
- RAG routing proof has no off-the-shelf replacement and must remain; Hybrid keeps it while reducing maintenance burden elsewhere.

---

## C) What We Are Eliminating (explicit)

- **Option 1 (V4 Maximal Enforcement):** too much bespoke script maintenance and still reactive; protocol compliance is not structurally enforced.
- **Option 2 (OpenAPI-First Codegen only):** drops Claude-context guardrails and RAG routing proof that are unique to ZakOps.
- **Option 4 (Schema Registry + Contract-First CI):** adds ceremony without removing hand-written schema drift.
- **Option 5 (Shared Types + Monorepo):** too risky for a solo AI builder; large refactor with high stall risk.

---

## D) Innovation Bundle (GREEN only)

### 1) Generated Schemas as Build Artifact
- **Implement:** generate `api-types.generated.ts` from `/openapi.json`, and keep thin manual Zod wrappers only for runtime validation boundaries.
- **Plug-in:** dashboard + CI.
- **Gate:** CI fails on codegen diff (generated file must be committed).
- **Impact:** makes drift structurally unshippable and removes 500+ lines of hand-written schemas.

### 2) Typecheck as Release Gate
- **Implement:** `tsc --noEmit` must pass on every PR.
- **Plug-in:** CI.
- **Gate:** compiler gate blocks merge on any mismatch.
- **Impact:** catches contract misalignment immediately with zero maintenance.

### 3) One-Command Sync (`make sync-types`)
- **Implement:** fetch `/openapi.json` → run codegen → format → typecheck.
- **Plug-in:** Makefile + CLAUDE protocol.
- **Gate:** required in pre-task and post-task hooks.
- **Impact:** reduces Claude error rate and time-to-correctness.

### 4) Topology Probe Canary
- **Implement:** compact JSON topology output for ports/containers/DB users.
- **Plug-in:** infra tooling + CLAUDE preflight.
- **Gate:** preflight must load the canary output.
- **Impact:** reduces session reset drift and prevents wrong-target changes.

### 5) Claude Preflight Bundle
- **Implement:** auto-generated `PREFLIGHT.md` with topology + manifest summary + drift warnings.
- **Plug-in:** infra tooling.
- **Gate:** CLAUDE pre-task requires reading the bundle.
- **Impact:** improves AI builder reliability and reduces "unknown unknowns."

---

## E) Execution Plan

### Phase 1: Days 1-2 — Foundation + Proof of Concept

> **CRITICAL (PATCH 6 — anyOf trap):** The single biggest technical risk is the Pydantic v2 `anyOf` nullable codegen issue. Pydantic v2 generates `anyOf: [{"type": "string"}, {"type": "null"}]` for `Optional` fields, which breaks or produces suboptimal output in every major Zod codegen tool. This MUST be tested in the first 48 hours, not deferred to "somewhere in 30 days."

**Deliverables:**

- [ ] **Audit openapi.py (302 lines)** *(PATCH 1 — openapi.py risk)*
  Confirm it only adds metadata (descriptions, tags, security schemes) and does not alter request/response schemas. If it modifies schemas, document which endpoints are affected and exclude them from codegen until fixed. File: `/home/zaks/zakops-backend/src/api/shared/openapi.py`.

- [ ] **Test nullable/Optional field codegen explicitly** *(PATCH 6 — anyOf trap)*
  Run `openapi-typescript` against live `/openapi.json`. Specifically verify that Pydantic v2's `anyOf` unions for Optional types produce correct `| null` union types for the top 5 entities (Deals, Actions, Events, Quarantine, AgentRuns). If it doesn't, evaluate `openapi-typescript`'s `--empty-objects-unknown` flag or contribute a nullable transform.

- [ ] Document which of the 36 endpoints produce usable generated types and which need manual handling.

- [ ] Decision document: codegen tool pass/fail per endpoint. Recommendation: `openapi-typescript` for types + manual Zod for critical parse boundaries.

**Gate:** POC report with pass/fail per endpoint. If >70% of endpoints produce usable output AND `anyOf` nullable handling works for top-5 entities, proceed. If <70% OR nullable handling fails, **PIVOT** — abort codegen, retain full V4, revisit when tooling improves.

---

### Phase 2: Days 3-4 — Codegen Pipeline Setup

**Deliverables:**

- [ ] `make sync-types` target that: fetches `/openapi.json` → runs codegen → outputs to `src/lib/api-types.generated.ts` → runs prettier.
- [ ] Verify `tsc --noEmit` passes with generated types in place.
- [ ] Claude Preflight Bundle script: generates `PREFLIGHT.md` with topology + schema summary.
- [ ] Topology Probe Canary: compact JSON output from existing discover-topology.sh.

**Gate:** `make sync-types && tsc --noEmit` exits 0. PREFLIGHT.md is generated and readable.

---

### Phase 3: Days 5-7 — Schema Migration (High-Risk Entities)

**Deliverables:**

- [ ] Migrate `DealSchema` from hand-written to generated (highest-traffic entity).
- [ ] Migrate `ActionSchema` from hand-written to generated (eliminates phantom fields).
- [ ] Migrate `EventSchema` from hand-written to generated.
- [ ] For each migrated schema: verify dashboard renders correctly via curl probe.
- [ ] Add ESLint import-ban rule: **`error`** (not `warn`) on importing from `api-schemas.ts` for migrated entities. *(REVIEW PATCH B1)* A warning is shippable — the whole thesis is "drift becomes unshippable." Set to `error` on the day each entity is migrated.

**Gate:** Dashboard curl probe shows no regressions. `tsc --noEmit` passes. Zero phantom fields for migrated entities. ESLint import-ban shows 0 errors for migrated entities.

---

### Phase 4: Days 8-9 — Remaining Schemas + POST Endpoint Fix + V4 Slim

**Deliverables:**

- [ ] Migrate remaining entities (Quarantine, Threads, Runs, Auth).

- [ ] **Address the 10 POST endpoints without response schemas** *(PATCH 2)*
  For POST endpoints without `response_model`, either:
  (a) Add `response_model` to the FastAPI route definition (preferred — typically 1 line per endpoint), or
  (b) Add to the manual-exception list with hand-written Zod wrappers.
  **Target: <5 manual exceptions.**

- [ ] Handle custom coercion functions (coerceToNumber, coerceBrokerToString) — either upstream fix in backend or document as thin wrappers around generated types.

- [ ] **Delete/slim V4 scripts per table below** *(PATCH 3)*:

| Script | Lines | Action | Rationale |
|--------|-------|--------|-----------|
| schema-diff.sh | 650 | **DELETE** | Replaced by codegen + typecheck |
| detect-phantom-endpoints.sh | 204 | **DELETE** | Replaced by generated types |
| dashboard-network-capture.sh | 302 | **DELETE** | Replaced by typecheck gate + endpoint smoke |
| sse-validation.sh | 162 | **DELETE** | SSE not implemented; polling fallback covered by smoke |
| discover-topology.sh | 426 | **SLIM to <100** | Keep compact JSON output only |
| rag-routing-proof.sh | 157 | **KEEP** | No codegen replacement |
| generate-manifest.sh | 156 | **KEEP** | Claude context |
| validate-enforcement.sh | 205 | **KEEP** | Meta-gate |

**Net result:** V4 scripts reduced from 3,290+ lines to ~620 lines.

**Gate:** All schemas migrated or explicitly documented as manual exceptions. `api-schemas.ts` reduced to only manual exceptions and custom coercion. V4 scripts reduced from 3,290 lines to <1,000 lines.

---

### Phase 5: Days 10-11 — CI Integration + Protocol Update

**Deliverables:**

- [ ] GitHub Actions workflow: `make sync-types && tsc --noEmit` on every PR.
- [ ] CI check: codegen diff gate (generated file must be committed, no uncommitted changes).
- [ ] CI check: no imports from legacy `api-schemas.ts` for migrated entities.
- [ ] Updated `.claude/CLAUDE.md` with simplified protocol:
  ```
  Pre-Task:  Run `make sync-types` + read PREFLIGHT.md
  Post-Task: Run `make sync-types && tsc --noEmit`
  Cross-Layer: Change backend → make sync-types → fix compile errors → done
  ```
- [ ] Updated Makefile with new `validate-all` that includes codegen + typecheck + RAG routing proof + enforcement audit.

- [ ] **CI ceiling for manual Zod wrappers** *(REVIEW PATCH B2)*
  Add a CI check: `grep -rc 'z\.object' src/lib/ | awk -F: '{s+=$2} END {print s}'` must be below a threshold (initially set to the count after migration — expected ~5-10). Prevents "thin manual Zod wrappers" from silently growing back toward the old 488-line pattern. Fail CI if count exceeds threshold without explicit `MANUAL_ZOD_CEILING` bump in the CI config.

- [ ] **Minimal correlation ID middleware** *(REVIEW PATCH A1 — upgraded from stretch goal)*
  Add ~20-line FastAPI middleware that:
  (a) reads `X-Correlation-ID` from request header, generates UUID if missing,
  (b) sets `X-Correlation-ID` on every `/api/*` response,
  (c) logs the correlation_id on any 5xx response in backend + agent API.
  This is not full distributed tracing — it's the minimal "P0 observability" that makes debugging feasible. Cheap enough to ship in Phase 5 rather than deferring to 90 days.

**Gate:** CI pipeline runs green on a test PR. CLAUDE.md protocol has fewer than 10 lines of instructions. Manual Zod wrapper count CI check passes. Correlation ID header present on API responses.

---

### Phase 6: Days 12-13 — Hardening + Edge Cases

**Deliverables:**

- [ ] Test: Claude Code session follows the new protocol correctly (run 3 simulated sessions).
- [ ] RAG routing proof integration: verify it still passes with new schema structure.
- [ ] Secret scan on all generated files.
- [ ] Verify migration completion: explicit count of migrated vs unmigrated schemas.

- [ ] **Golden Payload Capture** *(REVIEW PATCH A2)*
  For the top 5 entities (Deals, Actions, Events, Quarantine, AgentRuns):
  (a) Capture a real API payload from the running system: `curl /api/deals > golden/deals.json`
  (b) Store in `golden/*.json` as regression snapshots.
  (c) Add CI assertion: generated Zod can parse each golden payload without error, and backend still serves compatible shapes.
  This is a cheap regression test (~3 lines in CI per entity) that catches drift between the spec and reality — the gap that codegen alone doesn't cover.

**Gate:** 3 consecutive Claude sessions produce correct, type-safe changes without protocol violations. RAG routing proof PASS. Secret scan PASS. Golden payload parse PASS for all 5 entities.

---

### Phase 7: Day 14 — Documentation + Cutover

**Deliverables:**

- [ ] Delete old `api-schemas.ts` once ESLint confirms 0 remaining imports. Keep in git history for rollback.
- [ ] Update SERVICE-CATALOG.md with new `make sync-types` workflow.
- [ ] Update RUNBOOKS.md with codegen troubleshooting guide.
- [ ] Record everything in CHANGES.md.
- [ ] Final `make validate-all` run — all gates green.

**Gate:** Production dashboard operational with fully generated types. No hand-written Zod for any entity that has OpenAPI schema coverage. `make validate-all` exits 0.

---

### Phase 8: Days 15-21 — Feature Scaffolder *(REVIEW PATCH A3 — scale-readiness)*

> **Why this matters:** Claude Code is an excellent ad-hoc scaffolder, but a structured feature scaffolder serves two purposes that ad-hoc prompting does not: (1) it enforces consistent patterns across every new feature — route + response_model + typed hook + test stub — which eliminates the entire class of "button exists but not wired" and "route exists but no response_model" bugs that caused Round 4 regressions; (2) it prepares ZakOps for scaling beyond a solo AI builder — when additional builders (human or AI) join, the scaffolder becomes the shared standard that prevents pattern drift.

> **Prerequisite:** Phases 1-7 must be complete. The scaffolder builds ON TOP of the codegen pipeline — it generates code that plugs into `make sync-types` and the generated types. Building the scaffolder before the foundation exists would be premature.

**Deliverables:**

- [ ] **`zakops:new-feature` CLI command** (or `make new-feature NAME=quarantine-bulk-delete`)
  Single command that generates a complete vertical slice:

  **Backend (FastAPI):**
  - Route stub with correct HTTP method, path, and `response_model` enforced
  - Pydantic request/response models
  - Proper status codes (200/204/400/409)
  - OpenAPI tags and descriptions auto-populated

  **Dashboard (Next.js):**
  - Typed client call wrapper / React hook (e.g., `useQuarantineBulkDelete()`)
  - UI action skeleton wired to that hook
  - React Query cache invalidation pattern
  - Error toast formatting with correlation ID display

  **Contract:**
  - Auto-triggers `make sync-types` to regenerate types from updated OpenAPI
  - Registers the endpoint in a contract index

  **Tests:**
  - Backend: integration test stub for the route
  - Dashboard: Playwright test stub that clicks the control and asserts network call + UI state change

- [ ] **Contract-First Feature Sheet format**
  Define a lightweight YAML spec format for features:
  ```yaml
  feature: quarantine_bulk_delete
  ui:
    page: /quarantine
    control: "Bulk delete"
  api:
    method: DELETE
    path: /api/quarantine/bulk
    body:
      ids: string[]
    response:
      deleted: number
      failed: { id: string, reason: string }[]
  db:
    tables: [quarantine_items]
  effects:
    invalidate_queries: [quarantine:list]
  tests:
    playwright: true
    backend_integration: true
  ```
  The scaffolder reads this spec and generates all files. This makes feature creation declarative and auditable.

- [ ] **UI Action Registry** (structural enforcement for no-dead-UI)
  Every clickable control must be registered:
  ```typescript
  export const actions = {
    "quarantine.delete": { endpoint: "/api/quarantine/:id", method: "DELETE" },
    "quarantine.bulkDelete": { endpoint: "/api/quarantine/bulk", method: "DELETE" },
    // ...
  } as const;
  ```
  Two CI enforcement checks:
  (a) Static check: fail CI if a component uses an unregistered action key.
  (b) Playwright probe: iterate the registry and validate endpoints exist (no 404/405).
  This generalizes the no-dead-UI gate — fix one action flow and the pattern covers all future flows.

- [ ] **Pilot: scaffold 2 real features from Round 4 pain points**
  Use the scaffolder to generate:
  (a) Quarantine single delete (currently API error)
  (b) Deals bulk delete (currently 405)
  Validate that the generated code compiles, passes `tsc --noEmit`, and the Playwright stubs run.

**Gate:** Scaffolder generates a complete vertical slice for a test feature. Generated code passes `make sync-types && tsc --noEmit`. Playwright stub runs. Two pilot features scaffolded and working.

**Future extensions (not in scope for Phase 8, but planned):**
- Auto-regen on backend model change (YELLOW innovation #9 — adopt after 30 days of stable `make sync-types`)
- Template variants for CRUD vs action vs query patterns
- Multi-entity relationship scaffolding
- Agent tool registration scaffolding (when agent tool definitions change frequently enough to warrant it)

---

## F) Hard Gates (must-pass)

1. **Compiler/type gate:** `make sync-types && tsc --noEmit` in CI on every PR.
2. **Contract gate:** generated type artifacts must be committed; CI fails on diff.
3. **Runtime probe gate:** `/health` for backend + dashboard returns 200; `/api/deals` returns data when DB has deals.
4. **RAG routing gate:** keep `make validate-rag-routing` from V4 (agent must match API/DB counts).
5. **No-dead-UI gate:** dashboard network probe or minimal endpoint smoke set must show 0 unexpected 5xx. Once Phase 8 ships, this is enforced structurally via the UI Action Registry (every action registered, CI validates endpoints exist).
6. **Correlation ID gate** *(PATCH 5 revised — upgraded to P0 observability in Phase 5)*:
   Every `/api/*` response must include `X-Correlation-ID` header. Logs must emit correlation_id for any 5xx in backend + agent API. Implementation: ~20-line FastAPI middleware (Phase 5 deliverable). CI test: `curl -I /api/deals | grep -i x-correlation-id` must succeed.
7. **Manual Zod ceiling gate** *(REVIEW PATCH B2)*:
   CI count of `z.object` occurrences in `src/lib/` must not exceed the post-migration threshold. Prevents silent regression toward hand-written schemas.
8. **Golden payload gate** *(REVIEW PATCH A2)*:
   Generated Zod must successfully parse each `golden/*.json` snapshot. Catches spec-vs-reality drift.

---

## G) Failure Detector + Pivot Plan *(PATCH 4 — concrete triggers)*

### 30-Day Pivot Trigger
**Condition:** Codegen POC yields <70% usable types OR `anyOf` nullable handling produces incorrect output for top-5 entities.
**Action:** Abort codegen, retain full V4, revisit when FastAPI/Pydantic tooling improves.

### 60-Day Pivot Trigger
**Condition:** More than 3 schemas still on manual Zod with no codegen path, OR `tsc --noEmit` failures per week >5 due to OpenAPI inaccuracy.
**Action:** Freeze migration, restore deleted V4 scripts from git (`git checkout HEAD~N -- tools/infra/schema-diff.sh`), run both codegen and V4 schema-diff in parallel until stabilized.

### 90-Day Pivot Trigger
**Condition:** Legacy `api-schemas.ts` imports remain in >10% of dashboard files.
**Action:** Extend migration timeline by 30 days. Do NOT delete legacy file until lint shows 0 imports.

### Detection Mechanism (Automated — no human review needed)
Add a CI job that counts:
- (a) codegen diff size (should be 0 after sync)
- (b) `tsc --noEmit` failure count per week
- (c) imports from legacy schema file

CI fails if thresholds exceeded. No "weekly summary" — fully automated.

---

## H) Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Pydantic v2 `anyOf` nullable codegen failure** | Medium | **CRITICAL** | Day 1-2 POC catches this. Fallback: retain full V4. **Test in first 48 hours.** |
| Custom openapi.py produces spec quirks | Medium | Medium | Day 1 audit (PATCH 1). Inspect output vs raw FastAPI spec. |
| 10 POST endpoints without response schemas | Known | Medium | Add `response_model` or manual exceptions. Target <5 manual (PATCH 2). |
| Migration breaks existing dashboard features | Low | High | Curl probe gate at each migration step (Days 5-9). |
| Codegen tool has security vulnerability | Medium | Medium | Pin exact version. Only run against own spec (not untrusted). Use `openapi-typescript` (clean security record, 7,700 stars). |
| Claude Code imports wrong schema file during migration | Medium | Medium | ESLint import rule set to **error** (not warn). Clear file naming convention (.generated.ts). *(REVIEW B1)* |
| Dual-schema confusion during migration window | Medium | Medium | Migration tracked entity-by-entity. Import lint enforces single source per entity at error level. |
| V4 scripts deleted but needed for pivot | Low | Medium | Recovery via git history. Explicit `git checkout` command in pivot plan (PATCH 4). |
| Manual Zod wrappers silently grow back | Medium | Medium | CI ceiling gate counts `z.object` occurrences, fails if threshold exceeded. *(REVIEW B2)* |
| Spec drifts from runtime reality (codegen blind spot) | Medium | Medium | Golden payload snapshots catch spec-vs-reality drift via CI parse test. *(REVIEW A2)* |

---

## I) Codegen Tool Decision

| Tool | Stars | Last Release | Zod Support | Security | Stability | Verdict |
|------|-------|-------------|-------------|----------|-----------|---------|
| openapi-zod-client | ~1,100 | Mar 2025 | Yes (Zodios) | Clean | ABANDONED | Skip |
| orval | ~5,200 | Jan 2026 | Yes (plugin) | 3 RCE CVEs in 2026 | Active | **Risky — avoid** |
| openapi-typescript | ~7,700 | Nov 2025 | No (types only) | Clean | Stable | **RECOMMENDED** |
| hey-api | ~4,000 | Feb 2026 | Yes (plugin) | Clean | v0.x — pin version | Acceptable backup |

**Decision:** Use `openapi-typescript` for stable TypeScript type generation. For the 5-10 schemas that need Zod runtime validation at API boundaries, write thin manual Zod wrappers that reference the generated types. This avoids the maturity issues with full Zod codegen while eliminating 90% of hand-written schema maintenance.

---

## J) Top 10 Execution Steps (Quick Reference)

1. **Audit openapi.py** (302 lines) — confirm it doesn't alter response schemas; fix if it does.
2. **Run `openapi-typescript` against live `/openapi.json`** — verify output handles `anyOf` nullable unions correctly for top 5 entities. **Do this in first 48 hours.**
3. **Add `make sync-types` target** — fetches OpenAPI spec, runs codegen, outputs `src/lib/api-types.generated.ts`, runs prettier.
4. **Add `tsc --noEmit` to CI** — zero-cost gate that catches all type misalignment.
5. **Migrate DealSchema and ActionSchema** to generated types + thin manual Zod wrappers for runtime validation boundaries.
6. **Add ESLint import-ban rule at `error` level** — forbid importing from `api-schemas.ts` for migrated entities. Error, not warn.
7. **Migrate remaining schemas** (Events, Quarantine, Threads, Auth). For the ~10 POST endpoints without response schemas, add `response_model` to FastAPI routes.
8. **Delete V4 scripts:** schema-diff.sh (650L), detect-phantom-endpoints.sh (204L), dashboard-network-capture.sh (302L), sse-validation.sh (162L). Slim discover-topology.sh to <100 lines.
9. **Update CLAUDE.md protocol** to 3 lines: Pre-task = `make sync-types` + read PREFLIGHT.md. Post-task = `make sync-types && tsc --noEmit`. Cross-layer = change backend, sync types, fix compile errors, done.
10. **Delete legacy `api-schemas.ts`** once ESLint confirms 0 remaining imports.

---

## K) META-QA Patches Applied (Traceability)

| Patch | Section Modified | Change |
|-------|-----------------|--------|
| PATCH 1: openapi.py audit | E Phase 1 | Added explicit audit deliverable for 302-line custom spec modifier |
| PATCH 2: 10 POST endpoints | E Phase 4 | Changed "document gaps" to concrete mitigation: add response_model or manual exceptions, target <5 |
| PATCH 3: V4 deletion table | E Phase 4 | Added explicit per-script keep/delete/slim table with line counts and rationale |
| PATCH 4: Pivot plan | G | Replaced vague "weekly summary" with concrete 30/60/90 triggers, git recovery paths, automated CI detection |
| PATCH 5: Correlation/tracing | F | ~~Downgraded to stretch goal~~ → Upgraded back to P0 observability gate with ~20-line middleware in Phase 5 |
| PATCH 6: anyOf trap | E Phase 1 | Named the Pydantic v2 anyOf nullable trap explicitly; mandated testing in first 48 hours |
| REVIEW A1: Correlation ID middleware | E Phase 5, F | Upgraded from 90-day stretch to Phase 5 deliverable — minimal middleware, not full tracing |
| REVIEW A2: Golden Payload Capture | E Phase 6, F | Added golden/*.json regression snapshots for top 5 entities — catches spec-vs-reality drift |
| REVIEW A3: Feature Scaffolder | E Phase 8 (new) | Added 7-day Phase 8 for `zakops:new-feature` scaffolder, contract-first feature sheets, UI action registry. Scale-readiness investment. |
| REVIEW B1: ESLint error not warn | E Phase 3 | Changed import-ban from `warn` to `error` — a warning is shippable, an error is not |
| REVIEW B2: Zod wrapper ceiling | E Phase 5, F | Added CI count threshold for manual `z.object` occurrences — prevents silent regression |

---

## L) Decision Quality (from META-QA)

| Criterion | Score | Note |
|-----------|-------|------|
| Decisiveness | 4/5 | Commits to one strategy, kills four alternatives |
| Correctness under constraints | 4/5 | Claude-context mechanisms correctly retained |
| Maintainability | 4/5 | 3,290 → ~620 script lines |
| Speed to finish line | 3/5 | 14-day plan with per-day deliverables (improved from original 30/60/90) |
| Proof / verifiability | 3/5 | Compiler gate = strong proof; correlation/tracing downgraded to stretch |
| **TOTAL** | **18/25** | Patches raise execution readiness without changing score |

---

*Rev 2: PASS3 Final + 6 META-QA patches + PASS2 14-day ship plan + 5 external review patches.*
*Pipeline: PASS1 (Codex) → PASS2 (Opus) → PASS3 FINAL (Codex) → META-QA (Opus) → External Review A + B → This document.*
*Total execution plan: 21 days (14 days foundation + migration, 7 days scaffolder).*
