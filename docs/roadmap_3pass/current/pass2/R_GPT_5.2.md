# Pass 2 Red‑Team Review — ZakOps Roadmap 3‑Pass (Pass 1 Syntheses)

- **Model ID:** GPT 5.2
- **Timestamp (UTC):** 2026-01-24T03:31:07Z

## Findings Summary

### Diversity check

- **PASS**: 3 Pass‑1 syntheses found:
  - `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_Gemini_3.0.md`
  - `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_Claude_OPUS_4.5.md`
  - `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_GPT_5.2.md`

### One‑sentence verdict

All three Pass‑1 roadmaps are **directionally aligned**, but **not execution‑grade** because they (a) treat unverified assumptions as facts, and (b) reference many **non-existent gates/scripts** without an explicit “create-the-gate” contract.

### Best/worst (hostile)

- **Best structure + grounding to QA reality**: `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_GPT_5.2.md` (it anchors to existing HITL spike artifacts and states authority-order conflict resolution).
- **Best artifact specificity**: `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_Claude_OPUS_4.5.md` (it enumerates spike artifacts/gates), but it makes multiple **unverified infra assertions** and introduces **Langfuse compliance drift**.
- **Most security-forward**: `/home/zaks/bookkeeping/docs/roadmap_3pass/current/pass1/S_Gemini_3.0.md` (immediately prioritizes plaintext-at-rest risk), but it uses **unsupported “APPROVED” language** and proposes encryption/perf targets without proof.


## Stop‑Ship (must resolve before starting Phase 1)

> “Stop‑Ship” means: do not proceed because it will cause drift or a non‑compliant implementation.

### SS‑01 — Misleading status claims (“APPROVED”, “EXECUTION‑READY”)

- Where:
  - `S_Gemini_3.0.md` header: “Status: APPROVED FOR EXECUTION”
  - `S_Claude_OPUS_4.5.md` header: “Status: EXECUTION‑READY”
- Why it fails:
  - None of the authoritative sources grant this approval.
  - It causes teams to skip gates and treat assumptions as facts.
- Required fix:
  - Replace with “Draft; execution requires gate PASS evidence” and explicitly list the required gate artifacts.

### SS‑02 — Langfuse compliance drift (self-hosted requirement vs cloud fallback)

- Authority:
  - Decision Lock requires **Langfuse (self-hosted) on :3001**, with DoD including “Langfuse UI accessible at :3001” and “Complete trace visible”.
- Where:
  - `S_Claude_OPUS_4.5.md` Phase 1 Scope IN: “Deploy Langfuse at :3001 (self-hosted or cloud fallback)”
- Why it fails:
  - “Cloud fallback” is not labeled as **non-compliant**, and thus will be used as a default.
- Required fix:
  - Cloud Langfuse can exist only as “temporary dev mode”; Phase‑1 DoD must still require self-hosted :3001.

### SS‑03 — Plaintext-at-rest risk is not converted into a hard gate

- Authority:
  - QA flags plaintext persistence risk as **Major**.
  - Decision Lock requires “NEVER log raw prompts/responses”.
  - Scaffold Plan demands “no raw content” across surfaces (logs/traces/DB), enforced by tests.
- Where:
  - All three S docs mention the risk; none defines a deterministic, repo-real gate that fails closed.
- Required fix:
  - Define and implement one **PII canary gate** that injects a unique token and proves it does not appear in:
    - docker logs
    - Langfuse traces (when enabled)
    - DB tables containing checkpoint/tool state
  - Gate must produce an artifact and non-zero exit on failure.

### SS‑04 — “Paper gates” (referencing scripts/tests that do not exist)

- Authority:
  - QA baseline gate pack exists and is runnable: `./scripts/bring_up_tests.sh`.
- Where:
  - `S_GPT_5.2.md` references many new scripts (e.g., `ports_lint.sh`, `env_lint.sh`, soak scripts, queue scripts) without defining or creating them.
  - `S_Claude_OPUS_4.5.md` references `pytest` and multiple scripts that are not evidenced by repo inspection.
  - `S_Gemini_3.0.md` uses placeholder gate names.
- Repo reality:
  - In `/home/zaks/zakops-agent-api/scripts`, the only gating script currently present is `bring_up_tests.sh`.
- Required fix:
  - Either:
    1) consolidate all new gates into `./scripts/bring_up_tests.sh` (preferred), OR
    2) explicitly create every referenced script and require it to write a named artifact with a PASS marker.

### SS‑05 — Unverified infra claims treated as facts

- Where:
  - `S_Claude_OPUS_4.5.md` “Infrastructure Verified” table asserts RAG REST and PostgreSQL are running.
- Why it fails:
  - QA_REPORT does not prove those services.
  - It causes plans to “skip contract discovery” and implement against guessed endpoints.
- Required fix:
  - Mark as UNVERIFIED and add contract probe gates.


## Contradictions

### C‑01 — Langfuse self-hosted requirement vs “cloud fallback” (non-compliance not labeled)

- Claim A (authoritative): `DECISION-LOCK-FILE.md` §5 Tracing/Observability requires Langfuse self-hosted at :3001 and trace visible.
- Claim B: `S_Claude_OPUS_4.5.md` Phase 1 allows cloud fallback without labeling it non-compliant.
- Impact: violations of locked constraints; missing traceability in the lab.
- Resolution rule: **Decision Lock wins**.
- Test:
  - `curl -f http://localhost:3001/api/public/health`
  - Run one workflow and verify trace exists in Langfuse UI.

### C‑02 — Auth negative semantics (401 vs 403) are vague in S_Gemini

- Claim A (observed): `QA_REPORT.md` §4 says missing/invalid claims → 401; insufficient role → 403.
- Claim B: `S_Gemini_3.0.md` Phase 1 gate text “Verify 403 for unauthorized roles” (too vague and likely wrong for missing role).
- Impact: clients cannot rely on stable semantics; policy enforcement regresses.
- Resolution rule: **QA reality wins** (and matches Decision Lock required claims).
- Test:
  - Re-run `./scripts/bring_up_tests.sh` and assert codes in `gate_artifacts/auth_negative_tests.json`.

### C‑03 — Retrieval path ownership (RAG REST-only vs “pgvector-only, optional RAG REST”)

- Claim A (Scaffold Plan, higher priority than Master Doc in this review): `ZakOps-Scaffold-Master-Plan-v2.md` §3.5 says retrieval is exclusively via RAG REST and Agent must not query pgvector directly.
- Claim B (Master Doc): `ZakOps-Ultimate-Master-Document-v2.md` §Memory/RAG describes pgvector-only Phase 1-2 with optional RAG REST frontend.
- Impact: split-brain retrieval semantics; security boundary confusion.
- Resolution rule: **Scaffold Plan wins** per the required authority order (after Decision Lock and QA reality).
- Tests:
  - Static scan: `rg -n "deal_embeddings|SELECT .*FROM deal_embeddings|psycopg" /home/zaks/zakops-agent-api/app` must not show direct embedding-table queries from Agent.
  - Runtime: retrieval tools must call `RAG_REST_URL` only.

### C‑04 — Phase naming drift (MVP vs Hardening)

- Claim A (Decision Lock): Checklist Summary defines Phase 1 = MVP, Phase 2 = Hardening.
- Claim B: `S_Gemini_3.0.md` calls Phase 1 “Production Hardening” and Phase 2 “Agentics & Integration”.
- Impact: teams will mis-sequence deliverables and claim completion against the wrong checklist.
- Resolution rule: **Decision Lock wins**: keep Phase naming aligned to lock file.
- Test:
  - In roadmap text, explicitly map each phase’s DoD to Decision Lock checklist items.


## Gaps (required for real execution)

### M‑01 — Real-service vs mocks is not proven

- Problem:
  - HITL spike passes, but it can pass while calling mocked tools.
- Impact:
  - “Green” does not imply integration with Deal API and real side effects.
- Required fix:
  - Add a hard gate that enforces `ALLOW_TOOL_MOCKS=false` and proves Deal API state changed after approval.

### M‑02 — Missing contract probes for Deal API, RAG REST, MCP

- Problem:
  - None of the S docs defines a deterministic probe artifact for service contracts.
- Impact:
  - Tool clients may be implemented against guessed endpoints.
- Required fix:
  - Add container-side probes producing:
    - `gate_artifacts/deal_api_contract.json`
    - `gate_artifacts/rag_rest_contract.json`
    - `gate_artifacts/mcp_contract.json`

### M‑03 — audit_log immutability is not proven by a gate

- Problem:
  - Decision Lock demands audit immutability; plans do not define a DB-level enforcement test.
- Impact:
  - Audit trail can be tampered with.
- Required fix:
  - Add DB-level constraint/trigger/permissions + a gate that attempts UPDATE/DELETE and expects failure.

### M‑04 — No-raw-content policy is not end-to-end

- Problem:
  - Decision Lock bans raw prompts/responses in traces/logs; QA still flags plaintext-at-rest as Major.
- Impact:
  - Data leakage risk; compliance failure.
- Required fix:
  - Define allowed persisted fields (hash+length only) and enforce with canary scans.

### M‑05 — DB topology decision is not pinned

- Problem:
  - Scaffold Plan offers host-services DB vs internal compose DB; none of the S docs pins the lab baseline with a proof gate.
- Impact:
  - Port collisions and environment drift.
- Required fix:
  - Choose one lab baseline topology and add a gate that prints effective `DATABASE_URL` from inside the container and verifies it points to the intended DB.


## Gate Failures (integrity problems)

### G‑01 — Non-existent gate scripts are treated as if they exist

- Evidence:
  - Repo contains `/home/zaks/zakops-agent-api/scripts/bring_up_tests.sh`.
  - Plans reference additional scripts without a creation/DoD contract.
- Fix (choose one, explicitly):
  1) Expand `bring_up_tests.sh` to include each new gate and to write stable artifacts, OR
  2) Create each new script and require:
     - stable output file path under `gate_artifacts/`
     - PASS marker string
     - non-zero exit on failure.

### G‑02 — Gate artifact naming not standardized

- Problem:
  - Some plans say “store under gate_artifacts/phase1/” but do not define the file set.
- Fix:
  - Standardize: `gate_artifacts/<gate_id>.*` + a single `gate_artifacts/run.log` summary.


## Fix Plan (exact edits required in Pass 3)

> Pass 3 should produce one “final” roadmap after applying these edits.

### Edits required for S_Gemini_3.0.md

1) **Header:** Replace “Status: APPROVED FOR EXECUTION” with:
   - “Status: Draft; execution requires gate PASS evidence.”
2) **Phase naming:** Rename phases to align with Decision Lock checklist (Phase 1 MVP, Phase 2 Hardening, Phase 3 Advanced).
3) **Encryption claim:** Replace “AES-GCM + <50ms overhead” with:
   - “At-rest mitigation approach TBD; must preserve kill-9 recovery; acceptance is kill-9 PASS + canary PASS.”
4) **Acceptance gates:** Replace placeholder script names with:
   - either `./scripts/bring_up_tests.sh` (extended) OR explicitly specified new scripts with artifacts.

### Edits required for S_Claude_OPUS_4.5.md

1) **Header:** Replace “Status: EXECUTION‑READY” with gate-based status.
2) **Infrastructure Verified:** Change to “UNVERIFIED” unless supported by probe artifacts; add contract probes.
3) **Langfuse:** Replace “self-hosted or cloud fallback” with:
   - “Self-hosted Langfuse :3001 required for Phase‑1 DoD; cloud is dev-only and non-compliant.”
4) **Gates:** Replace `pytest` and missing script references with either:
   - existing `bring_up_tests.sh` artifacts, OR
   - a “create-the-gate” list with artifact paths and PASS markers.

### Edits required for S_GPT_5.2.md

1) **Paper scripts:** For each referenced script not present today (`ports_lint.sh`, `env_lint.sh`, soak scripts, queue scripts, etc.), add an explicit backlog item:
   - “Create script at /scripts/<name>, output artifact gate_artifacts/<name>.*, PASS marker, non-zero exit.”
   OR consolidate them into `bring_up_tests.sh`.
2) **DB topology:** Convert OQ‑03 into an explicit lab decision and add a proof gate.
3) **Langfuse DoD:** Keep self-hosted requirement and make it a hard PASS/FAIL for Phase‑1 completion.


## Questions / Tests

1) **Deal API contract**: exact endpoints + auth requirements + response schemas.
   - Test: container-side probe writes `gate_artifacts/deal_api_contract.json`.
2) **RAG REST contract**: health endpoint + query endpoint + schema.
   - Test: probe writes `gate_artifacts/rag_rest_contract.json`.
3) **At-rest mitigation that preserves crash recovery**.
   - Test: implement mitigation and rerun kill‑9 gate; must remain PASS.
4) **Langfuse self-hosted readiness**.
   - Test: `curl -f http://localhost:3001/api/public/health` + trace presence.

