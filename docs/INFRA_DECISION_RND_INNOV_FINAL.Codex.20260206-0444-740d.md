A) Final Decision
Adopt the Hybrid Guardrail strategy: keep V4’s Claude-context primitives (topology discovery, manifest age gate, CLAUDE preflight protocol, enforcement audit) and the RAG routing proof, but replace hand‑written dashboard schemas with generated API types from the FastAPI OpenAPI spec (openapi-typescript) plus thin manual Zod wrappers at the API boundary; enforce codegen + typecheck in CI via a single `make sync-types` workflow so drift becomes structurally unshippable while preserving the only V4 components that are uniquely necessary.

B) Why This Wins (5 bullets max)
- V4 already passes 15/15 gates and provides Claude context, but its 3,290+ lines of scripts are reactive and fragile; swapping schema diffing for codegen removes the largest drift source without losing the V4 context that Claude requires.
- The biggest observed failures are hand‑written Zod mismatches and silent safeParse fallbacks; generated types + compiler gates prevent these by construction.
- OpenAPI already exists and is the natural contract boundary for a FastAPI → Next.js stack, enabling incremental adoption without a monorepo rewrite.
- Claude Code’s session resets make “one-command sync + preflight bundle” materially safer than multi‑step protocols; fewer steps = fewer skipped gates.
- RAG routing proof has no off‑the‑shelf replacement and must remain; Hybrid keeps it while reducing maintenance burden elsewhere.

C) What We Are Eliminating (explicit)
- Option 1 (V4 Maximal Enforcement): too much bespoke script maintenance and still reactive; protocol compliance is not structurally enforced.
- Option 2 (OpenAPI‑First Codegen only): drops Claude-context guardrails and RAG routing proof that are unique to ZakOps.
- Option 4 (Schema Registry + Contract‑First CI): adds ceremony without removing hand‑written schema drift.
- Option 5 (Shared Types + Monorepo): too risky for a solo AI builder; large refactor with high stall risk.

D) Innovation Bundle (GREEN only)
1) Generated Schemas as Build Artifact
   - Implement: generate `api-types.generated.ts` from `/openapi.json`, and keep thin manual Zod wrappers only for runtime validation boundaries.
   - Plug‑in: dashboard + CI.
   - Gate: CI fails on codegen diff (generated file must be committed).
   - Impact: makes drift structurally unshippable and removes 500+ lines of hand‑written schemas.
2) Typecheck as Release Gate
   - Implement: `tsc --noEmit` must pass on every PR.
   - Plug‑in: CI.
   - Gate: compiler gate blocks merge on any mismatch.
   - Impact: catches contract misalignment immediately with zero maintenance.
3) One‑Command Sync (`make sync-types`)
   - Implement: fetch `/openapi.json` → run codegen → format → typecheck.
   - Plug‑in: Makefile + CLAUDE protocol.
   - Gate: required in pre‑task and post‑task hooks.
   - Impact: reduces Claude error rate and time‑to‑correctness.
4) Topology Probe Canary
   - Implement: compact JSON topology output for ports/containers/DB users.
   - Plug‑in: infra tooling + CLAUDE preflight.
   - Gate: preflight must load the canary output.
   - Impact: reduces session reset drift and prevents wrong‑target changes.
5) Claude Preflight Bundle
   - Implement: auto‑generated `PREFLIGHT.md` with topology + manifest summary + drift warnings.
   - Plug‑in: infra tooling.
   - Gate: CLAUDE pre‑task requires reading the bundle.
   - Impact: improves AI builder reliability and reduces “unknown unknowns.”

E) 30/60/90 Execution Plan
30 days (minimum enforceable drift prevention)
- POC codegen against live `/openapi.json` for top entities (Deals, Actions, Events, Quarantine, Threads); document gaps.
- Implement `make sync-types` and `tsc --noEmit` CI gate.
- Generate preflight bundle + topology canary; update CLAUDE protocol to two steps.
- Migrate highest‑risk schemas (Actions, Deals) to generated types + thin Zod wrappers.

60 days (migration + standardization completion)
- Migrate remaining schemas; remove legacy `api-schemas.ts` usage via lint rule.
- Slim V4: delete schema‑diff + phantom endpoint scripts; keep manifest, enforcement, RAG routing proof.
- Add CI check to ensure no imports from legacy schema file.

90 days (hardening + decommissioning + boring reliability)
- Finalize codegen coverage and manual exception list (if any).
- Remove legacy schemas entirely or quarantine into `api-schemas.legacy.ts` with explicit deprecation deadline.
- Run full V4 validate‑all (slim) plus typecheck; document stable runbook.

F) Hard Gates (must‑pass)
- Compiler/type gate: `make sync-types && tsc --noEmit` in CI on every PR.
- Contract gate: generated type artifacts must be committed; CI fails on diff.
- Runtime probe gate: `/health` for backend + dashboard returns 200; `/api/deals` returns data when DB has deals.
- RAG routing gate: keep `make validate-rag-routing` from V4 (agent must match API/DB counts).
- Correlation/tracing policy: responses must include correlation_id header; logs must emit correlation_id for any 5xx.
- No‑dead‑UI gate: dashboard network probe or minimal endpoint smoke set must show 0 unexpected 5xx.

G) Failure Detector + Pivot Plan
- Early failure signals: codegen POC yields <70% usable types; `tsc --noEmit` routinely fails due to OpenAPI inaccuracies; runtime Zod wrappers trigger widespread parse errors.
- Detection: weekly summary of codegen diffs, compile failures, and safeParse error counts in logs.
- Pivot (if needed): pause schema migration, re‑enable full V4 schema‑diff and phantom‑endpoint checks as temporary enforcement, and fix OpenAPI accuracy before resuming Hybrid Guardrail.
