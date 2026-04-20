**Pass 1 — Infra Strategy Options**
Agent: Codex
Run ID: 20260206-0430-56df
Sources read:
- /mnt/c/Users/mzsai/Downloads/CALL-FOR-ACTION-INFRA-STRATEGY-2026-02-05.md
- /mnt/c/Users/mzsai/Downloads/INFRA-AWARENESS-V4-COMPLETION-REPORT.md

A) Reality Snapshot (10 bullets max)
- V4 infra-awareness completed with 15/15 gates PASS and validate-all green, including topology discovery, manifest, migration, schema diff, RAG routing proof, enforcement audit, and dashboard network probe.
- V4 generates a manifest with 747 DB columns and 88 backend + 29 agent endpoints; manifest age gate enforces freshness.
- V4 evidence shows backend DB = zakops (schema zakops) and agent DB = zakops_agent, with migrations synced to 024_correlation_id.
- Drift symptoms are real and recurring: Zod schema mismatches silently return empty arrays; ActionStatus enum mismatch; phantom endpoints; agent stale data via RAG.
- System is multi-layer and multi-repo: Postgres → FastAPI/Pydantic (8091) → Next.js/Zod (3003) → LangGraph agent (8095), plus vLLM (8000).
- Claude Code is the primary builder with session resets; V4 was tailored to supply context and enforce pre/post checks.
- V4 is comprehensive but reactive and script-heavy; it detects drift after it occurs and relies on enforcement discipline.
- OpenAPI is already available and accurate enough to drive code generation; TypeScript strict mode exists.
- RAG routing proof is now a first-class validation step in V4; SSE still not implemented but validated with fallback.
- Multiple postgres containers can exist in the environment; drift and split‑brain remain a real operational risk.

B) Strategy Options (3–5 options max)

Option 1 — “V4 Maximal Enforcement”
- Core mechanism: Keep V4 as the primary drift defense; expand enforcement and hard-fail gates.
- What we KEEP from V4: topology discovery, manifest + age gate, schema diff, RAG routing proof, enforcement audit, pre‑commit hooks, CLAUDE.md protocol.
- What we DELETE from V4: nothing (only minor cleanup).
- What we ADD (industry tooling): Spectral (OpenAPI lint), Schemathesis (contract testing), OpenTelemetry traces for cross‑layer proof.
- Risks / hidden costs: high maintenance burden; bash scripts remain fragile; reactive not preventive; ongoing QA time tax.
- Failure mode if chosen: drift still happens between runs, and tests get skipped or quietly fail, causing silent UI breakage.

Option 2 — “OpenAPI‑First Codegen”
- Core mechanism: Treat OpenAPI as the contract; generate Zod + TS client; compile errors block drift.
- What we KEEP from V4: minimal topology discovery + manifest + RAG routing proof.
- What we DELETE from V4: 3‑way schema diff scripts, phantom endpoint detection, hand‑written Zod, most enforcement scripts.
- What we ADD (industry tooling): openapi-zod-client or orval; openapi-typescript; CI gate on codegen diff; “typecheck = gate.”
- Risks / hidden costs: OpenAPI must stay accurate; gaps from DB→Pydantic remain; existing dashboard code must migrate to generated schemas.
- Failure mode if chosen: if OpenAPI drifts from backend reality, codegen propagates wrong types into UI.

Option 3 — “Hybrid Guardrail (Codegen + Slim V4)”
- Core mechanism: Prevent drift via codegen while preserving V4’s Claude-context and RAG routing proof.
- What we KEEP from V4: topology discovery, manifest + age gate, CLAUDE.md protocol, RAG routing proof, enforcement audit.
- What we DELETE from V4: most bash schema diffing, phantom endpoint detection, manual Zod maintenance.
- What we ADD (industry tooling): openapi‑zod‑client/orval, OpenAPI lint (Spectral), CI gate for generated artifacts, lightweight contract tests.
- Risks / hidden costs: migration work; dual source‑of‑truth risk if codegen and manual schemas coexist.
- Failure mode if chosen: partial adoption leaves drift in legacy schemas; enforcement becomes inconsistent.

Option 4 — “Schema Registry + Contract‑First CI”
- Core mechanism: Treat OpenAPI as a versioned contract; enforce breaking‑change checks in CI.
- What we KEEP from V4: topology discovery, manifest age gate, RAG routing proof, CLAUDE.md protocol.
- What we DELETE from V4: schema diff scripts and phantom endpoint detection.
- What we ADD (industry tooling): Redocly/Spectral for linting, openapi-diff for breaking‑change gates, schemathesis for runtime contract tests.
- Risks / hidden costs: still reactive if codegen not used; requires CI discipline and spec hygiene.
- Failure mode if chosen: contract stays “theory‑correct” but UI still drifts if types are not generated.

Option 5 — “Shared Types Package + Monorepo Convergence”
- Core mechanism: Move toward monorepo or shared package; single versioned types for backend + dashboard + agent.
- What we KEEP from V4: manifest + topology discovery; RAG routing proof.
- What we DELETE from V4: most diff scripts; manual Zod; phantom endpoints.
- What we ADD (industry tooling): pnpm workspace or Nx; openapi‑typescript or datamodel‑code‑generator; changeset tooling.
- Risks / hidden costs: repo restructuring; integration overhead; higher blast radius.
- Failure mode if chosen: migration drag stalls progress; Claude Code struggles with large refactors and multi‑repo coupling.

C) Innovation Harvest (MANDATORY)

Prevention
1) “Generated Zod as Build Artifact” — generate Zod schemas in CI and fail if git diff is non‑empty. Plug‑in: dashboard/CI. Impact: correctness, drift prevention. Self‑host: YES (openapi‑zod‑client/orval).
2) “OpenAPI Breaking‑Change Gate” — run openapi‑diff vs main branch, block breaking changes. Plug‑in: backend/CI. Impact: correctness, maintainability. Self‑host: YES (openapi‑diff CLI).
3) “Schema Contract Snapshot Lock” — store /openapi.json in artifacts; require explicit version bump to change. Plug‑in: backend/CI. Impact: proofability, drift prevention. Self‑host: YES.
4) “Typecheck as Release Gate” — make dashboard `tsc --noEmit` required for merge. Plug‑in: CI. Impact: correctness. Self‑host: YES.

Discovery
5) “Topology Probe Canary” — minimal script that checks ports/containers/users and publishes a compact JSON used by Claude. Plug‑in: infra/CI. Impact: truth visibility. Self‑host: YES (shell + docker).
6) “Cross‑Layer Request Trace” — OpenTelemetry spans from UI→backend→agent with correlation_id assertion. Plug‑in: backend + agent. Impact: proofability, debugging. Self‑host: YES (OTel + Grafana Tempo).
7) “Drift Radar Dashboard” — daily job compares OpenAPI, generated types, and UI compile; posts a summary in a dashboard panel. Plug‑in: CI + dashboard. Impact: discovery, correctness. Self‑host: YES.

Automation
8) “One‑command Sync” — `make sync-types` does OpenAPI fetch + codegen + prettier + typecheck. Plug‑in: dev/CI. Impact: speed, consistency. Self‑host: YES.
9) “Auto‑regen on backend change” — CI detects backend route/model changes and auto‑runs codegen. Plug‑in: backend/CI. Impact: speed, drift prevention. Self‑host: YES.
10) “Golden Trace CI Mode” — run agent golden traces in CI mode with deterministic mocks; gate on 95%+. Plug‑in: agent/CI. Impact: quality, speed. Self‑host: YES.

Developer UX
11) “Claude Preflight Bundle” — a single markdown “context capsule” generated per session (topology + schema + ports). Plug‑in: infra. Impact: Claude robustness. Self‑host: YES.
12) “Local LangSmith‑like UI” — self‑host Langfuse or similar to view tool calls and traces. Plug‑in: agent. Impact: debugging, transparency. Self‑host: YES (Langfuse OSS).
13) “Prompt + Tool Registry Validator” — fail CI if prompt lists tools not in registry or missing. Plug‑in: agent/CI. Impact: correctness. Self‑host: YES.
14) “API Client Playground” — generate a typed client and provide a minimal CLI to call endpoints with schema validation. Plug‑in: dev. Impact: speed, correctness. Self‑host: YES.

D) Decision Criteria (weighted; total=100)
- Drift prevention strength: 25
- Maintenance cost: 15
- Robustness to Claude mistakes: 20
- Time‑to‑impact: 15
- End‑to‑end proofability: 15
- Innovation leverage (evolve quickly): 10

E) Provisional Front‑runner (NOT final)
- Front‑runner: Option 3 — Hybrid Guardrail (Codegen + Slim V4)
- Why: preserves Claude‑specific context + RAG routing proof while making drift structurally harder via codegen and typecheck gates.
- Evidence that would change my mind:
  1) OpenAPI proves too inaccurate to drive codegen without heavy refactoring.
  2) Migration cost is higher than V4 maintenance (e.g., large dashboard rewrites).
  3) Monorepo/shared‑types becomes feasible with low risk → Option 5 might dominate.
  4) V4 gates demonstrate near‑zero false positives with minimal upkeep → Option 1 might suffice.
