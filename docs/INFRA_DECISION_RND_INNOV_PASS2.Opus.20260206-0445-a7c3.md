# Pass 2 — Infrastructure Strategy Stress Test

**Agent:** Opus 4.6
**Run ID:** 20260206-0445-a7c3
**Role:** Adversarial evaluator — break the options, filter the innovations
**Sources read:**
- /mnt/c/Users/mzsai/Downloads/CALL-FOR-ACTION-INFRA-STRATEGY-2026-02-05.md
- /mnt/c/Users/mzsai/Downloads/INFRA-AWARENESS-V4-COMPLETION-REPORT.md
- PASS1: /home/zaks/bookkeeping/docs/INFRA_DECISION_RND_INNOV_PASS1.Codex.20260206-0430-56df.md

**External research conducted:**
- openapi-zod-client, orval, openapi-typescript, hey-api — GitHub activity, CVEs, known issues
- FastAPI + Pydantic v2 OpenAPI 3.1 codegen failure modes
- Brownfield codegen migration failure patterns

**Codebase inspection conducted:**
- OpenAPI contract: zakops-api.json (36 paths, 26 schemas, OpenAPI 3.1.0)
- Dashboard Zod: api-schemas.ts (500 lines, 20+ safeParse, 15 phantom fields)
- Backend Pydantic: 93 BaseModel classes across 22 files
- V4 scripts: 3,290+ lines (12 infra + 4 validation scripts)
- Makefile: 23 targets, 4 phases
- Backend OpenAPI: custom openapi.py (302 lines, runtime generation)

---

## A) Option Kill Shots

### Option 1 — "V4 Maximal Enforcement"

**Catastrophic failure mode:**
Claude skips pre/post task hooks ~30% of sessions (CLAUDE.md compliance is not structurally enforced — it's a request, not a compiler error). A single skipped `make validate-schema-diff` after a backend model change ships silent Zod parse failures to the dashboard. The user sees empty lists. There is no alarm. This has already happened multiple times — V4 was built precisely because drift kept occurring.

**Slow-burn failure mode:**
3,290+ lines of bash scripts (schema-diff.sh alone is 650 lines) become a second codebase to maintain. Every backend refactor risks breaking the scripts that validate the backend. The scripts parse Python AST and Zod source via text — any change to import style, class declaration patterns, or file organization silently degrades script accuracy. The P2 count (94 informational warnings) grows over time and buries real P1 issues in noise.

**Irreducible maintenance burden:**
- schema-diff.sh must track every Pydantic model change, every Zod schema change, and every DB migration
- discover-topology.sh hardcodes fallback paths and must be updated when services move
- Dashboard network capture (302 lines) does source-code extraction via regex — fragile
- 6+ evidence directories to manage, clean, and not leak secrets into

**Where drift still sneaks in:**
- Between V4 runs (drift exists from commit to next `make validate-all`)
- In safeParse fallback behavior (V4 checks schema structure, not runtime parse behavior)
- In the 15 phantom fields in ActionSchema that V4 classifies as P2 informational
- In response shape changes that don't change field names (type changes, nesting changes)

**Minimal gates required to survive:**
1. `make validate-all` in CI on every PR (not just developer discipline)
2. P2 count regression gate (fail if P2 count increases without explicit acknowledgement)
3. safeParse failure alerting in production (not just compile-time checks)

---

### Option 2 — "OpenAPI-First Codegen"

**Catastrophic failure mode:**
The OpenAPI spec drifts from backend reality. This is not hypothetical — the codebase already has a custom `openapi.py` (302 lines) that modifies FastAPI's auto-generated spec at runtime. If that customization diverges from actual endpoint behavior, codegen propagates wrong types. The generated Zod schemas pass typecheck but fail at runtime because the API returns a different shape than the spec promised. This is worse than no codegen because it creates false confidence.

**Additionally critical — the Pydantic v2 + OpenAPI 3.1 `anyOf` trap:**
FastAPI with Pydantic v2 generates `anyOf: [{"type": "string"}, {"type": "null"}]` for `Optional[str]` fields. Research confirms this breaks or produces suboptimal output in every major codegen tool:
- orval: Wraps in unnecessary union types (source: FastAPI Discussion #9900)
- hey-api: Generates `?` but not `| null`, so nullable fields don't round-trip correctly (Issue #549)
- openapi-typescript: Handles at type level but no runtime validation
- openapi-zod-client: Effectively abandoned — skip

10 of the 36 OpenAPI paths are POST endpoints with missing response schemas. Codegen cannot generate return types for endpoints that don't declare them. These 10 endpoints would need manual Zod schemas anyway, partially defeating the purpose.

**Slow-burn failure mode:**
The team trusts the generated types and stops thinking about contract boundaries. When the OpenAPI spec has a subtle inaccuracy (a field marked required that's actually sometimes null in edge cases), the generated Zod schema throws at runtime, and because safeParse was replaced with generated parse, the dashboard crashes instead of gracefully degrading.

**Irreducible maintenance burden:**
- Custom openapi.py (302 lines) must be maintained and tested to ensure spec accuracy
- Codegen tool dependency (orval, hey-api) introduces supply chain risk and update churn
- orval had 3 RCE CVEs in early 2026 (CVE-2026-23947, CVE-2026-25141, CVE-2026-22785) — unsanitized enum descriptions became executable JS in generated code
- hey-api is v0.x with breaking changes between minor versions — no stability guarantee
- Migration of 500 lines of hand-written Zod with custom coercion logic (coerceToNumber, coerceBrokerToString) that codegen cannot replicate

**Where drift still sneaks in:**
- DB → Pydantic gap (codegen only covers API → Zod, not the full chain)
- Custom response middleware or error handlers that modify response shapes after Pydantic serialization
- Endpoints that return raw dicts or non-model responses
- Agent RAG routing (codegen does nothing for this problem)

**Minimal gates required to survive:**
1. `make sync-types && tsc --noEmit` in CI on every PR
2. OpenAPI spec snapshot diffing (fail on undocumented spec changes)
3. Runtime response validation at dashboard API boundary (don't trust codegen blindly)
4. Keep RAG routing proof from V4

---

### Option 3 — "Hybrid Guardrail (Codegen + Slim V4)"

**Catastrophic failure mode:**
Dual source of truth during migration. Hand-written Zod and generated Zod coexist. Claude Code gets confused about which to import — it sees both `api-schemas.ts` (500 lines, hand-written) and `api-schemas.generated.ts` (new, generated). It imports the wrong one. The dashboard compiles fine because both export compatible types, but the hand-written one has stale fields. This failure mode is invisible to both the compiler and the developer.

**Slow-burn failure mode:**
The migration from hand-written to generated Zod never completes. The "slim V4" retains the script burden for the schemas that haven't been migrated. The team now maintains THREE things instead of one: codegen pipeline, slim V4 scripts, and residual hand-written Zod. Net complexity increases rather than decreases.

**Irreducible maintenance burden:**
- Codegen tool dependency (same supply chain risk as Option 2)
- Slim V4 scripts still need updating when topology changes
- Migration plan must be tracked — which entities use generated vs hand-written Zod
- Custom coercion logic (coerceToNumber, etc.) must be handled in the generated pipeline or wrapped

**Where drift still sneaks in:**
- During the migration window: hand-written schemas for unmigrated entities
- DB → Pydantic gap (same as Option 2)
- Agent RAG routing (still needs custom validation, not addressed by codegen)
- In the "slim" V4 scripts — which ones to keep is a judgment call that may be wrong

**Minimal gates required to survive:**
1. Codegen + typecheck in CI
2. Import lint rule: no importing from `api-schemas.ts` once `api-schemas.generated.ts` exists for that entity
3. Migration completion tracker (explicit list of migrated vs unmigrated schemas)
4. RAG routing proof (kept from V4)
5. Manifest + topology discovery (kept from V4)

---

### Option 4 — "Schema Registry + Contract-First CI"

**Catastrophic failure mode:**
The contract (OpenAPI spec) is treated as the source of truth, but nobody generates types from it. Developers (Claude Code) update the spec, update the backend, and update the dashboard independently. The CI gate says "spec is valid and hasn't broken compatibility" but the dashboard Zod still drifts because types aren't generated. This is V4-lite with extra ceremony and less actual protection.

**Slow-burn failure mode:**
Breaking-change detection becomes a false comfort. The CI gate catches structural spec changes but not behavioral changes (a field that used to always be populated but now returns null in edge cases). The team trusts the green CI badge and stops manually testing API responses.

**Irreducible maintenance burden:**
- Spec linting rules (Spectral) must be configured and maintained for ZakOps-specific patterns
- Breaking-change definitions are subjective — what counts as "breaking" requires ongoing curation
- Without codegen, all the hand-written Zod maintenance remains

**Where drift still sneaks in:**
- Everywhere that Option 1 drifts, because types are still hand-written
- In contract definitions that are "correct" but don't match implementation (spec says required, implementation sometimes returns null)

**Minimal gates required to survive:**
1. Everything from Option 1 (because without codegen, you still need V4's schema diffing)
2. Plus Spectral/Redocly config maintenance
3. Plus breaking-change gate calibration

**Verdict: This option adds gates without removing the root cause (hand-written types). It's Option 1 with extra steps.**

---

### Option 5 — "Shared Types Package + Monorepo Convergence"

**Catastrophic failure mode:**
The repo restructuring breaks the existing deployment pipeline. Dashboard, backend, and agent currently deploy independently. Coupling them via a shared package means a type change in the shared package triggers rebuilds of all three services. A bad type change cascades failures across the entire platform simultaneously instead of being isolated to one layer.

**Slow-burn failure mode:**
Claude Code struggles with large structural refactors (confirmed in the Call for Action: "Claude Code added features without architectural planning"). Moving to a shared types package requires understanding dependency graphs, build pipelines, and version resolution across the monorepo. Each session, Claude must relearn the monorepo structure. The migration stalls at 40% complete, leaving the worst-case scenario: partially shared types and partially independent types.

**Irreducible maintenance burden:**
- Monorepo tooling (pnpm workspaces or Nx) adds configuration complexity
- Shared package versioning (changesets) adds ceremony to every type change
- Build pipeline must handle cross-package dependencies
- The Python backend cannot consume TypeScript types — you still need a bridge layer

**Where drift still sneaks in:**
- Between the Python types (Pydantic) and the shared TypeScript types — the language boundary is irreducible
- In the agent layer, which uses Python and can't import TypeScript packages

**Minimal gates required to survive:**
1. Full CI pipeline with cross-package typecheck
2. Integration tests that verify Python-TypeScript type compatibility
3. Monorepo-aware Claude Code instructions (significant CLAUDE.md expansion)

**Verdict: Highest risk, highest reward, but wrong for a solo AI-builder with session resets. This is a human team strategy, not a Claude Code strategy.**

---

## B) Innovation Filter

### From PASS1's 14 innovations:

#### GREEN — Adopt Now

**#4: "Typecheck as Release Gate" (`tsc --noEmit` required for merge)**
- Why GREEN: Zero implementation cost, zero maintenance cost, immediate value. Just add to CI.
- What proof is needed: Verify `tsc --noEmit` currently passes on the dashboard codebase.
- What makes it safe: It's a standard compiler check. Cannot break anything. Catches entire categories of drift.
- Source contribution: Industry standard in every serious TypeScript project (Vercel, Next.js, etc.)

**#1: "Generated Zod as Build Artifact" (codegen + git diff gate)**
- Why GREEN: This is the single highest-leverage change. Eliminates the 500-line hand-written api-schemas.ts and its 15 phantom fields.
- What proof is needed: (a) Run codegen against the live OpenAPI spec and diff against current api-schemas.ts to quantify the gap. (b) Verify that the 10 POST endpoints without response schemas can be handled (either add schemas to backend or exclude those endpoints).
- What makes it safe: The generated file is gitignored or committed as `.generated.ts` — the git diff gate catches unexpected changes. Pair with import lint to prevent importing the old hand-written file.
- Caveat: Choose the codegen tool carefully. Recommend openapi-typescript for types + thin manual Zod wrappers for the 5-10 schemas that need runtime validation, rather than full Zod codegen (which has tool maturity issues per research).

**#8: "One-command Sync" (`make sync-types`)**
- Why GREEN: Force multiplier for Claude Code. Reduces cognitive load from "run 6 different commands" to "run 1 command." This directly addresses the 30% protocol compliance problem — fewer steps = fewer missed steps.
- What proof is needed: None beyond implementing it correctly.
- What makes it safe: It's a Makefile target wrapping existing operations.

**#5: "Topology Probe Canary" (compact JSON for Claude context)**
- Why GREEN: Already essentially exists in V4's discover-topology.sh. The innovation is making the output a compact JSON that Claude reads in 5 seconds instead of a 426-line bash script.
- What proof is needed: Show that the compact JSON provides sufficient context for Claude to make safe changes.
- What makes it safe: Read-only operation. Cannot break anything.

**#11: "Claude Preflight Bundle" (context capsule per session)**
- Why GREEN: Directly solves the "Claude has no persistent memory" constraint. A single markdown file with topology + schema summary + active drift warnings, generated fresh at session start.
- What proof is needed: Test that Claude Code actually reads and uses the bundle (run 5 sessions with and without).
- What makes it safe: Read-only generated file.

#### YELLOW — Adopt Later / Needs Proof

**#2: "OpenAPI Breaking-Change Gate" (openapi-diff vs main)**
- Why YELLOW: Useful but secondary. The real problem is types not being generated from the spec, not that the spec changes without notice. Once codegen is in place (#1), spec changes become visible via generated code diffs anyway.
- What proof is needed: Demonstrate that spec changes that don't change generated types (e.g., description updates) are worth gating separately.
- What would make it safe: Adopt after codegen is stable. Don't add ceremony before the foundation exists.

**#3: "Schema Contract Snapshot Lock" (version bump to change spec)**
- Why YELLOW: Adds friction without proportional value in a solo-AI-builder workflow. Version bumps are a team coordination mechanism. Claude Code is the only builder — it doesn't need to coordinate with itself.
- What proof is needed: Show a scenario where spec versioning would have prevented a real incident.
- What would make it safe: Only adopt if/when multiple builders (human or AI) are working simultaneously.

**#6: "Cross-Layer Request Trace" (OpenTelemetry spans)**
- Why YELLOW: High value for debugging but significant implementation effort. Requires instrumenting FastAPI, Next.js, and LangGraph with OTel. Needs a trace backend (Grafana Tempo, Jaeger). Not a drift-prevention mechanism — it's a debugging tool.
- What proof is needed: Estimate implementation hours. Verify that the correlation_id field (migration 024) can serve as the trace ID.
- What would make it safe: Implement after codegen is stable. Don't distract from the primary drift-prevention goal.

**#9: "Auto-regen on backend change" (CI detects model changes → runs codegen)**
- Why YELLOW: Depends on #1 being stable first. Automation of an unstable process amplifies failures.
- What proof is needed: 30 days of successful manual `make sync-types` runs before automating.
- What would make it safe: Feature-flag it behind a CI environment variable.

**#13: "Prompt + Tool Registry Validator" (fail CI if tools missing)**
- Why YELLOW: Good idea but narrow applicability. Only relevant when agent tool definitions change, which is infrequent.
- What proof is needed: Count how many times tool registry drift has caused a real incident.
- What would make it safe: Implement as a simple JSON schema check, not a complex validation framework.

#### RED — Likely Trap / Wrong ROI

**#7: "Drift Radar Dashboard" (daily comparison job + dashboard panel)**
- Why RED: Building a dashboard to display drift information means maintaining a dashboard about a dashboard. The daily job adds another moving part. If drift is prevented by codegen (#1), the radar has nothing to detect. If drift is not prevented, displaying it on a dashboard doesn't fix it — the problem is that drift goes unnoticed between V4 runs, and a daily dashboard is still a daily cadence.
- What would change my mind: If the system grew to 10+ services where drift is expected and must be triaged, a radar makes sense. At 3 services, it's overhead.

**#10: "Golden Trace CI Mode" (deterministic agent traces in CI)**
- Why RED: The agent uses vLLM serving Qwen 2.5 — a local LLM. Deterministic outputs require setting temperature=0 and seeding, which changes model behavior. "95% pass rate" is a metric that requires maintaining a golden dataset, updating it as prompts change, and debugging failures that may be model behavior changes, not bugs. The maintenance burden exceeds the testing value for a solo builder.
- What would change my mind: If the agent were serving external users and reliability was a contractual obligation.

**#12: "Local LangSmith-like UI" (self-host Langfuse)**
- Why RED: Another service to deploy, maintain, and keep running. The system already has 7+ containers. Langfuse requires its own Postgres database, its own auth, and its own UI. The value (viewing tool calls and traces) can be achieved with structured logging to a file, which the codebase already does.
- What would change my mind: If agent debugging consumed >2 hours/week of developer time.

**#14: "API Client Playground" (typed CLI for endpoint testing)**
- Why RED: Curl already exists. The dashboard is the playground. A typed CLI adds a maintenance surface for a tool that would be used occasionally at best.
- What would change my mind: Nothing. This is a nice-to-have for a team of 10, not for a solo AI builder.

---

## C) Forced Ranking

| Rank | Option | Score (weighted /100) | Rationale |
|------|--------|----------------------|-----------|
| **1** | **Option 3: Hybrid Guardrail** | **72** | Best balance of prevention + Claude-awareness. Codegen kills the largest drift source (hand-written Zod). Slim V4 retains what's irreplaceable (topology, RAG proof). Risk: migration window with dual schemas. |
| **2** | Option 2: OpenAPI-First Codegen | 65 | Strong drift prevention but loses Claude context mechanisms. DB→Pydantic gap unaddressed. Agent RAG routing unaddressed. Assumes OpenAPI spec is trustworthy (risky given custom openapi.py). |
| **3** | Option 1: V4 Maximal Enforcement | 55 | Works today, proven 15/15 gates. But 3,290+ lines of bash, reactive not preventive, and protocol compliance ~70%. The 30% miss rate is not fixable by adding more checks — it's structural. |
| **4** | Option 4: Schema Registry + Contract-First CI | 42 | Adds ceremony without removing root cause. Without codegen, all hand-written Zod problems persist. Breaking-change gates are useful but secondary to type generation. |
| **5** | Option 5: Shared Types + Monorepo | 35 | Right destination, wrong time. Language boundary (Python↔TypeScript) is irreducible. Monorepo migration is a multi-week project that Claude Code will struggle to complete consistently across sessions. |

### Scoring Breakdown (criteria from PASS1)

| Criterion (weight) | Opt 1 | Opt 2 | Opt 3 | Opt 4 | Opt 5 |
|--------------------|-------|-------|-------|-------|-------|
| Drift prevention (25) | 12 | 22 | 20 | 10 | 23 |
| Maintenance cost (15) | 6 | 10 | 9 | 5 | 3 |
| Claude robustness (20) | 14 | 8 | 16 | 10 | 4 |
| Time-to-impact (15) | 12 | 10 | 10 | 8 | 2 |
| Proofability (15) | 8 | 10 | 12 | 6 | 2 |
| Innovation leverage (10) | 3 | 5 | 5 | 3 | 1 |
| **Total** | **55** | **65** | **72** | **42** | **35** |

### Confidence: 75%

**Why not higher:**
- The Pydantic v2 / OpenAPI 3.1 `anyOf` trap is a real blocker for Zod codegen tools. If the current spec produces unusable Zod output, Option 3 degrades to Option 1.
- The 302-line custom openapi.py introduces unknown risk — it may produce spec quirks that break codegen.
- hey-api's v0.x instability and orval's CVE history mean the codegen tool choice carries non-trivial supply chain risk.

**What would raise confidence to 90%:**
- A successful proof-of-concept: run codegen against the live `/openapi.json` and verify the output is usable for the top 5 entities (Deals, Actions, Events, Quarantine, Threads).
- Confirm that `anyOf` nullable handling produces correct Zod output for the chosen tool.

**What would flip the ranking:**
- If codegen POC fails → Option 1 wins by default (it works today).
- If monorepo migration proves feasible in <3 days → Option 5 leapfrogs to #2.
- If V4 gates can be moved to CI with 100% enforcement → Option 1 becomes competitive with Option 3.

---

## D) 14-Day Ship Plan — Option 3: Hybrid Guardrail

**Constraint:** Claude Code is the builder. Each day = 1-2 Claude sessions. No human development.

### Days 1-2: Foundation + Proof of Concept

**Deliverables:**
- [ ] Run live backend's `/openapi.json` through `openapi-typescript` → verify output is clean TypeScript types
- [ ] Run live backend's `/openapi.json` through `hey-api` with Zod plugin (pinned version) → verify Zod output handles nullable fields correctly
- [ ] Document which of the 36 endpoints produce usable generated types and which need manual handling
- [ ] Decision document: which codegen tool to adopt (recommendation: `openapi-typescript` for types, manual Zod for critical parse boundaries)

**Gate:** POC report with pass/fail per endpoint. If >70% of endpoints produce usable output, proceed. If <70%, fall back to Option 1.

### Days 3-4: Codegen Pipeline Setup

**Deliverables:**
- [ ] `make sync-types` target that: fetches `/openapi.json` → runs codegen → outputs to `src/lib/api-types.generated.ts`
- [ ] `tsc --noEmit` passes with generated types in place (Innovation #4 — GREEN)
- [ ] Claude Preflight Bundle script: generates `PREFLIGHT.md` with topology + schema summary (Innovation #11 — GREEN)
- [ ] Topology Probe Canary: compact JSON output from existing discover-topology.sh (Innovation #5 — GREEN)

**Gate:** `make sync-types && tsc --noEmit` exits 0. PREFLIGHT.md is generated and readable.

### Days 5-7: Schema Migration (Entity by Entity)

**Deliverables:**
- [ ] Migrate `DealSchema` from hand-written to generated (highest-traffic entity)
- [ ] Migrate `ActionSchema` from hand-written to generated (eliminates 15 phantom fields)
- [ ] Migrate `EventSchema` from hand-written to generated
- [ ] For each migrated schema: verify dashboard renders correctly via curl probe
- [ ] Import lint rule: ESLint rule that warns on importing from `api-schemas.ts` for migrated entities

**Gate:** Dashboard curl probe (from V4's dashboard-network-capture.sh) shows no regressions. `tsc --noEmit` passes. Zero phantom fields for migrated entities.

### Days 8-9: Remaining Schemas + Slim V4

**Deliverables:**
- [ ] Migrate remaining entities (Quarantine, Threads, Runs, Auth)
- [ ] Handle the 10 POST endpoints without response schemas: add `response_model` to FastAPI routes OR document as manual-schema exceptions
- [ ] Delete or archive V4 scripts that are now redundant:
  - DELETE: schema-diff.sh (650 lines) — replaced by codegen + typecheck
  - DELETE: detect-phantom-endpoints.sh (204 lines) — replaced by generated types
  - KEEP: discover-topology.sh (426 lines) → slim to <100 lines (compact JSON output only)
  - KEEP: rag-routing-proof.sh (157 lines) — no codegen replacement exists
  - KEEP: generate-manifest.sh (156 lines) — Claude context
  - KEEP: validate-enforcement.sh (205 lines) — meta-gate
  - DELETE: dashboard-network-capture.sh (302 lines) — replaced by typecheck gate

**Gate:** All schemas migrated or explicitly documented as manual exceptions. `api-schemas.ts` reduced to only manual exceptions and custom coercion. V4 scripts reduced from 3,290 lines to <1,000 lines.

### Days 10-11: CI Integration + Protocol Update

**Deliverables:**
- [ ] GitHub Actions workflow: `make sync-types && tsc --noEmit` on every PR
- [ ] Updated `.claude/CLAUDE.md` with simplified protocol:
  ```
  Pre-Task: Run `make sync-types` + read PREFLIGHT.md
  Post-Task: Run `make sync-types && tsc --noEmit`
  Cross-Layer: Change backend → make sync-types → fix compile errors → done
  ```
- [ ] Updated Makefile with new `validate-all` that includes codegen + typecheck + RAG routing proof + enforcement audit
- [ ] OpenAPI Breaking-Change Gate: `openapi-diff` comparison vs main branch (Innovation #2 — promoted to GREEN now that codegen exists)

**Gate:** CI pipeline runs green on a test PR. CLAUDE.md protocol has fewer than 10 lines of instructions (down from current ~30).

### Days 12-13: Hardening + Edge Cases

**Deliverables:**
- [ ] Test: Claude Code session follows the new protocol correctly (run 3 simulated sessions)
- [ ] Handle edge cases: custom coercion functions (coerceToNumber, coerceBrokerToString) — either upstream fix in backend or document as thin wrappers around generated types
- [ ] RAG routing proof integration: verify it still passes with new schema structure
- [ ] Secret scan on all generated files

**Gate:** 3 consecutive Claude sessions produce correct, type-safe changes without protocol violations. RAG routing proof PASS. Secret scan PASS.

### Day 14: Documentation + Cutover

**Deliverables:**
- [ ] Delete old `api-schemas.ts` (rename to `api-schemas.legacy.ts` for 1-week rollback window)
- [ ] Update SERVICE-CATALOG.md with new `make sync-types` workflow
- [ ] Update RUNBOOKS.md with codegen troubleshooting guide
- [ ] Record everything in CHANGES.md
- [ ] Final `make validate-all` run — all gates green

**Gate:** Production dashboard operational with fully generated types. No hand-written Zod for any entity that has OpenAPI schema coverage. `make validate-all` exits 0. CHANGES.md updated.

### Ship Plan Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Codegen tool produces unusable output for `anyOf` nullable | Medium | High | Day 1-2 POC catches this. Fallback: Option 1. |
| Custom openapi.py produces spec quirks | Medium | Medium | Inspect openapi.py output vs raw FastAPI spec in POC. |
| Migration breaks existing dashboard features | Low | High | Curl probe gate at each migration step. |
| Codegen tool has security vulnerability | Medium | Medium | Pin exact version. Only run against own spec (not untrusted). |
| Claude Code imports wrong schema file during migration | Medium | Medium | ESLint import rule. Clear file naming convention (.generated.ts). |
| New V4 slim scripts still have bugs | Low | Low | Keep validate-enforcement.sh to verify enforcement is active. |

---

## Appendix: Codegen Tool Recommendation

Based on external research (2026-02-06):

| Tool | Stars | Last Release | Zod Support | Security | Stability | Verdict |
|------|-------|-------------|-------------|----------|-----------|---------|
| openapi-zod-client | ~1,100 | Mar 2025 | Yes (Zodios) | Clean | ABANDONED | Skip |
| orval | ~5,200 | Jan 2026 | Yes (plugin) | 3 RCE CVEs in 2026 | Active | Risky |
| openapi-typescript | ~7,700 | Nov 2025 | No (types only) | Clean | Stable | **RECOMMENDED for types** |
| hey-api | ~4,000 | Feb 2026 | Yes (plugin) | Clean | v0.x — pin version | Acceptable for Zod |

**Recommendation:** Use `openapi-typescript` for stable TypeScript type generation (zero-risk, deterministic output, no runtime overhead). For the 5-10 schemas that need Zod runtime validation at API boundaries, write thin manual Zod wrappers that reference the generated types. This avoids the maturity issues with full Zod codegen while still eliminating 90% of hand-written schema maintenance.

If full Zod codegen is desired: use `hey-api` at a pinned version, but accept the v0.x upgrade risk. Avoid orval until the CVE pattern stabilizes.

Sources:
- [FastAPI Discussion #9900 — Pydantic v2 anyOf with null](https://github.com/fastapi/fastapi/discussions/9900)
- [hey-api Issue #549 — Optional fields null handling](https://github.com/hey-api/openapi-ts/issues/549)
- [CVE-2026-23947 — Orval RCE via enum descriptions](https://www.cvedetails.com/cve/CVE-2026-23947/)
- [CVE-2026-25141 — Orval RCE via comment escape](https://advisories.gitlab.com/pkg/npm/@orval/core/CVE-2026-25141/)
- [Pydantic Issue #5436 — Nested discriminated unions](https://github.com/pydantic/pydantic/issues/5436)
- [openapi-typescript GitHub](https://github.com/openapi-ts/openapi-typescript)
- [hey-api/openapi-ts GitHub](https://github.com/hey-api/openapi-ts)
- [Orval Zod Schema Validation — DeepWiki](https://deepwiki.com/orval-labs/orval/4.1-zod-schema-validation)
