# MISSION: SURFACES-10-14-REGISTER-001
## Register Contract Surfaces 10-14 with Unified Validation and Manifest Coverage
## Date: 2026-02-10
## Classification: Infrastructure Expansion (Contract Surface Registration)
## Prerequisite: /home/zaks/bookkeeping/docs/QA-ITR-VERIFY-001.md reports FULL PASS
## Successor: QA-S10-14-VERIFY-001 (must run after this mission reaches FULL DONE)

---

## Preamble: Builder Operating Context

This mission assumes the builder auto-loads `/home/zaks/zakops-agent-api/CLAUDE.md`, canonical memory at `/root/.claude/projects/-home-zaks/memory/MEMORY.md`, hooks, deny rules, and path-scoped rules. This mission references those systems and adds only the mission-specific execution plan.

---

## 1. Mission Objective

This mission formalizes and registers Contract Surfaces 10-14 so the infrastructure contract system moves from a validated 9-surface baseline to a validated 14-surface baseline. It converts existing bookkeeping reference artifacts into enforceable contract surfaces with proportional, programmatic validation, and extends unified reporting so operators can see all surfaces in one place.

This is an infrastructure-contract mission, not an application feature mission. It modifies surface registration artifacts, validation scripts, manifest generation, make targets, and system guidance. It does not implement product features, API redesigns, database migrations, or frontend component behavior changes.

Source materials (ground truth):
- `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md`
- `/home/zaks/bookkeeping/docs/FORENSIC-AUDIT-RESULTS-FORENSIC-AUDIT-SURFACES-002`
- `/home/zaks/bookkeeping/docs/QA-SR-VERIFY-001-SCORECARD.md`
- `/home/zaks/bookkeeping/docs/MISSION-INFRA-TRUTH-REPAIR-001.md`
- `/home/zaks/bookkeeping/docs/QA-ITR-VERIFY-001.md`
- `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md`

---

## 2. Context

Validated current state before this mission:

1. Surfaces 1-9 are registered and validated by unified tooling.
- `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`
- `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
- `/home/zaks/zakops-agent-api/Makefile`
- `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md`

2. Surface 10-14 domains exist as operational concerns but are not registered as formal contract surfaces.
- Dependency health awareness (currently documented only)
- Environment cross-reference discipline (currently documented only)
- Error taxonomy consistency (currently documented only)
- Test coverage contract discipline (currently documented only)
- Performance budget contract (not yet formalized)

3. Existing source artifacts for Surfaces 10-13 already exist and must be promoted, not rewritten:
- `/home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md`
- `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md`
- `/home/zaks/bookkeeping/docs/ERROR-SHAPES.md`
- `/home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md`

4. Surface ordering is constrained by dependency risk and blast radius (from forensic findings):
- Surface 11 -> Surface 10 -> Surface 12 -> Surface 13 -> Surface 14
- Reason: environment contracts must stabilize endpoint naming before dependency checks; error taxonomy should stabilize before test and performance assertions rely on it.

5. CLAUDE.md must be updated last to avoid advertising a state that does not yet exist.

### Scope boundary in plain terms

In scope:
- Register Surfaces 10-14 in contract system
- Add validators for Surfaces 10-14
- Wire validators into unified validation and manifest
- Reconcile counts to 14 across authoritative artifacts

Out of scope:
- App feature implementation
- API response redesign
- Full performance-testing infrastructure
- Rewriting existing bookkeeping reference docs
- Frontend rule expansion items (a11y/component-pattern rule authoring)

---

## Crash Recovery Protocol <!-- Adopted from Improvement Area IA-2 -->

If resuming after crash/interruption, run exactly:

```bash
cd /home/zaks/zakops-agent-api && git log --oneline -5
cd /home/zaks/zakops-agent-api && make validate-local
find /home/zaks/bookkeeping/docs -maxdepth 1 -type f -name "MISSION-SURFACES-10-14-REGISTER-001*" -o -name "SURFACES-10-14-REGISTER-001-*"
```

If baseline validation fails during recovery, stop progression and classify the failure as pre-existing vs mission-induced before continuing.

---

## Continuation Protocol <!-- Adopted from Improvement Area IA-7 -->

At end of each session, update:
- `/home/zaks/bookkeeping/mission-checkpoints/SURFACES-10-14-REGISTER-001.md`

Checkpoint minimum content:
1. Completed phases
2. Remaining phases
3. Current validation status (`make validate-local`, `make validate-contract-surfaces`)
4. Open decisions and blockers
5. Exact next command to run

---

## Context Checkpoint <!-- Adopted from Improvement Area IA-1 -->

If context becomes constrained mid-mission:
1. Write current status to `/home/zaks/bookkeeping/mission-checkpoints/SURFACES-10-14-REGISTER-001.md`
2. Commit logically complete intermediate work
3. Resume via Crash Recovery Protocol

---

## 2b. Glossary

| Term | Definition |
|------|-----------|
| Surface 10 | Dependency Health Contract: service topology awareness and drift checks |
| Surface 11 | Secret & Environment Variable Registry Contract: cross-service env alignment checks |
| Surface 12 | Error Taxonomy Contract: documented error shape and handling consistency checks |
| Surface 13 | Test Coverage Contract: declared critical test-path presence checks |
| Surface 14 | Performance Budget Contract: explicit performance thresholds and measurement script |
| Promotion | Converting an existing reference doc from passive documentation into active contract artifact with validation |
| Reconciliation | Ensuring `contract-surfaces.md`, validator, manifest, and `CLAUDE.md` all report the same total surface count |
| Proportional validator | Smallest validator that materially catches drift for a surface without overbuilding |

---

## 3. Architectural Constraints

- **Track order is mandatory**
Meaning: Execute Surface 11 -> 10 -> 12 -> 13 -> 14 in this order.
Why: Forensic findings identified dependency and drift coupling in this sequence.

- **No application feature code changes**
Meaning: Do not modify dashboard/backend feature behavior, API business logic, or DB schema.
Why: This mission is infrastructure contract registration only.

- **Existing reference docs are inputs, not rewrite outputs**
Meaning: Use existing bookkeeping docs as source artifacts; avoid wholesale rewrites.
Why: Prior missions already established those artifacts; this mission promotes them into enforcement.

- **Validation mechanisms must be proportional**
Meaning: Simple checks for simple contracts, richer checks only where required (especially Surface 14).
Why: Prevent overengineering and reduce fragility.

- **Unified validator remains the enforcement backbone**
Meaning: End state must be one contract validation entrypoint that includes all 14 surfaces.
Why: Avoid orphan scripts and fragmented truth.

- **Manifest must report operational truth**
Meaning: `infra-snapshot` must include all 14 surfaces with actionable status.
Why: Operators depend on manifest for quick trust checks.

- **CLAUDE.md updated last**
Meaning: Do not claim 14 surfaces until wiring and validation actually pass.
Why: Prevent temporal inconsistency at session start.

- **Surface 9 conventions remain intact**
Meaning: No regression in existing design-system contract behavior.
Why: Surface 9 is already remediated and enforced.

- **Port 8090 remains forbidden**
Meaning: Do not introduce or normalize 8090 references.
Why: Decommissioned, drift-prone, historically high-risk.

- **Contract surface discipline remains mandatory**
Meaning: Generated files remain pipeline-owned; no manual edits to generated artifacts.
Why: Preserves sync integrity.

- **WSL safety remains mandatory**
Meaning: New shell files must be LF; ownership under `/home/zaks/` must be sane.
Why: Prevent delayed runtime failures.

---

## 3b. Anti-Pattern Examples

### WRONG: Registering a surface only in docs
```markdown
### Surface 10: Dependency Health
- Added in contract-surfaces.md
# (no validator, no manifest wiring)
```

### RIGHT: Full registration pattern per surface
```markdown
### Surface 10: Dependency Health
- Source artifact documented
- Validator exists and runs
- Included in unified validator output
- Included in infra-snapshot section
```

### WRONG: Hardcoded stale paths in validator
```bash
DOC_PATH="/tmp/old/SERVICE-TOPOLOGY.md"
```

### RIGHT: Canonical absolute project/bookkeeping paths
```bash
DOC_PATH="/home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md"
REPO_ROOT="/home/zaks/zakops-agent-api"
```

### WRONG: Updating CLAUDE.md early
```markdown
## Contract Surfaces (14 Total)
# (while validators still only check 9)
```

### RIGHT: Update CLAUDE.md after wiring and gate pass
```markdown
## Contract Surfaces (14 Total)
# (only after make validate-contract-surfaces confirms 14/14)
```

### WRONG: Solving validator failures by changing product code
```text
Edit backend endpoint behavior to satisfy surface script
```

### RIGHT: Keep mission in infrastructure scope
```text
Adjust contract artifact or validator logic; file app-code follow-up if needed
```

---

## 3c. Pre-Mortem: Top Failure Risks

| # | Failure Scenario | Likelihood | Impact | Mitigation |
|---|-----------------|------------|--------|------------|
| 1 | Surface validators are created but never wired into unified validation | HIGH | False confidence; surfaces remain unenforced | Phase 6 gate requires unified validator output listing 14 surfaces |
| 2 | Manifest still reports partial/stale counts after registration | HIGH | Operational trust failure | Phase 7 explicitly hardens manifest section and verifies all 14 statuses |
| 3 | CLAUDE.md updated before wiring completes | MEDIUM | Startup guide drift and operator confusion | Constraint + Phase 7 ordering rule (CLAUDE last) |
| 4 | Surface 14 overbuilt into a full perf system | MEDIUM | Scope blowout and delayed delivery | Guardrails enforce contract + baseline measurement only |
| 5 | Surface 11 validator too strict for repo variability (.env.example differences) | MEDIUM | Frequent false negatives | Phase 1 decision tree distinguishes required failures vs advisory warnings |

---

## 4. Phases

## Phase 0 - Discovery and Baseline Confirmation
**Complexity:** S  
**Estimated touch points:** 0 files modified

**Purpose:** Confirm prerequisites and capture before-state evidence before any edits.

### Blast Radius
- **Services affected:** None (read-only)
- **Pages affected:** None
- **Downstream consumers:** None

### Tasks
- P0-01: **Verify prerequisite mission state**
  - Confirm `/home/zaks/bookkeeping/docs/QA-ITR-VERIFY-001.md` indicates FULL PASS.
  - Confirm 9-surface baseline currently healthy.
  - **Checkpoint:** Prerequisite status captured in baseline evidence.

- P0-02: **Capture baseline evidence and counts**
  - Create `/home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-BASELINE.md` with outputs for:
    - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
    - `cd /home/zaks/zakops-agent-api && make infra-snapshot`
    - Count snapshots from:
      - `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`
      - `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
      - `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md`
      - `/home/zaks/zakops-agent-api/CLAUDE.md`
  - **Checkpoint:** Baseline file includes timestamped before counts.

### Decision Tree
- **IF** prerequisite QA mission is not FULL PASS -> stop and escalate.
- **ELSE IF** baseline validation already fails -> classify as pre-existing breakage before edits.
- **ELSE** proceed to Phase 1.

### Rollback Plan
1. No rollback required (read-only phase).
2. Verify clean state: `cd /home/zaks/zakops-agent-api && git status --short`

### Gate P0
- Baseline evidence file exists.
- Prerequisite status documented.
- Before counts captured from all 4 authoritative sources.

---

## Phase 1 - Surface 11 Contract (Env Registry)
**Complexity:** M  
**Estimated touch points:** 2-4 files modified/created

**Purpose:** Promote environment cross-reference documentation into an enforceable contract validator.

### Blast Radius
- **Services affected:** Dashboard, Agent API, Backend, RAG (validation only)
- **Pages affected:** None
- **Downstream consumers:** Validation pipeline, infra manifest

### Tasks
- P1-01: **Define Surface 11 validator behavior**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh`.
  - Validator checks should include:
    - Required artifact exists: `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md`
    - Cross-service variables declared in doc are discoverable in service env-example files (or clear advisory classification where files are intentionally absent)
    - Secret variable entries are tracked and not silently omitted from registry
  - **Checkpoint:** Script exits with deterministic PASS/FAIL semantics and readable summary.

- P1-02: **Add direct execution target**
  - Add `validate-surface11` target in `/home/zaks/zakops-agent-api/Makefile`.
  - Keep this target standalone in Phase 1 (unified wiring is Phase 6).
  - **Checkpoint:** `cd /home/zaks/zakops-agent-api && make validate-surface11` runs successfully.

- P1-03: **Record evidence output**
  - Append Phase 1 evidence to `/home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-BASELINE.md` or dedicated execution log.
  - **Checkpoint:** Evidence includes command + output + classification notes.

### Decision Tree
- **IF** an expected `.env.example` file is missing in a repo -> WARN with explicit path, do not silently pass.
- **ELSE IF** documented variable is missing where contract expects it -> FAIL.
- **ELSE** PASS.

### Rollback Plan
1. Revert only Surface 11 new script and target edits.
2. Run `cd /home/zaks/zakops-agent-api && make validate-local`.
3. Confirm 9-surface baseline behavior remains unchanged.

### Gate P1
- `make validate-surface11` executes and returns deterministic status.
- Surface 11 checks use absolute paths and include actionable output.
- No regressions in `make validate-local`.

---

## Phase 2 - Surface 10 Contract (Dependency Health)
**Complexity:** M  
**Estimated touch points:** 2-4 files modified/created

**Purpose:** Formalize dependency topology drift checks using existing topology artifacts.

### Blast Radius
- **Services affected:** Backend, Agent API, Dashboard, RAG (validation only)
- **Pages affected:** None
- **Downstream consumers:** Validation pipeline, infra operators

### Tasks
- P2-01: **Create Surface 10 validator**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh`.
  - Validate drift between:
    - `/home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md`
    - Service definitions and health endpoints in canonical repo files
  - Enforce no reintroduction of port 8090 references in topology contract paths.
  - **Checkpoint:** Script provides per-service PASS/WARN/FAIL summary.

- P2-02: **Add standalone make target**
  - Add `validate-surface10` in `/home/zaks/zakops-agent-api/Makefile`.
  - **Checkpoint:** `cd /home/zaks/zakops-agent-api && make validate-surface10` runs cleanly.

- P2-03: **Evidence capture**
  - Record output and any advisory exceptions in mission evidence file.
  - **Checkpoint:** Evidence includes service-by-service drift outcome.

### Decision Tree
- **IF** a documented endpoint/path no longer exists -> FAIL with exact missing path.
- **ELSE IF** runtime-only verification is unavailable in offline mode -> WARN and mark as runtime follow-up.
- **ELSE** PASS.

### Rollback Plan
1. Revert Surface 10 script and make-target edits only.
2. Re-run `make validate-local`.
3. Confirm baseline 9-surface pipeline still passes.

### Gate P2
- `make validate-surface10` passes with deterministic output.
- Validator catches topology drift classes identified in forensic report.
- No regression to existing validation targets.

---

## Phase 3 - Surface 12 Contract (Error Taxonomy)
**Complexity:** M  
**Estimated touch points:** 2-4 files modified/created

**Purpose:** Enforce that documented cross-service error shapes remain anchored to real handlers/artifacts.

### Blast Radius
- **Services affected:** Backend, Agent API, Dashboard (validation only)
- **Pages affected:** None
- **Downstream consumers:** Contract docs, error normalizer governance

### Tasks
- P3-01: **Create Surface 12 validator**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh`.
  - Minimum checks:
    - `/home/zaks/bookkeeping/docs/ERROR-SHAPES.md` exists and includes declared shape set
    - Referenced source files in the doc exist
    - Dashboard error normalizer file exists and still covers expected multi-shape normalization paths
  - **Checkpoint:** Validator outputs explicit checks mapped to documented shapes.

- P3-02: **Add standalone make target**
  - Add `validate-surface12` in `/home/zaks/zakops-agent-api/Makefile`.
  - **Checkpoint:** `cd /home/zaks/zakops-agent-api && make validate-surface12` passes.

- P3-03: **Evidence capture**
  - Record validator output in mission evidence file.
  - **Checkpoint:** Evidence includes source path resolution and shape checks.

### Decision Tree
- **IF** doc references a source file that no longer exists -> FAIL.
- **ELSE IF** normalizer coverage cannot be confidently determined statically -> WARN and flag for QA stress test.
- **ELSE** PASS.

### Rollback Plan
1. Revert Surface 12 script and make-target edits.
2. Re-run `make validate-local`.
3. Confirm no change in existing 9-surface outputs.

### Gate P3
- `make validate-surface12` returns pass/fail deterministically.
- Validator is contract-focused and does not require application behavior changes.
- Existing validation suite remains green.

---

## Phase 4 - Surface 13 Contract (Test Coverage Contract)
**Complexity:** M  
**Estimated touch points:** 2-4 files modified/created

**Purpose:** Enforce declared critical-path test presence without converting this mission into full coverage execution.

### Blast Radius
- **Services affected:** Backend, Agent API, Dashboard, RAG (validation inventory)
- **Pages affected:** None
- **Downstream consumers:** QA readiness and drift detection

### Tasks
- P4-01: **Create Surface 13 validator**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh`.
  - Validator checks should focus on existence of declared critical test artifacts from `/home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md`.
  - Contract is presence-based, not pass-rate or runtime coverage percentage.
  - **Checkpoint:** Validator prints counts for declared-vs-found artifacts.

- P4-02: **Add standalone make target**
  - Add `validate-surface13` in `/home/zaks/zakops-agent-api/Makefile`.
  - **Checkpoint:** `cd /home/zaks/zakops-agent-api && make validate-surface13` runs cleanly.

- P4-03: **Evidence capture**
  - Record output and any advisory exceptions.
  - **Checkpoint:** Evidence table shows discovered missing artifacts, if any.

### Decision Tree
- **IF** a declared required test path does not exist -> FAIL.
- **ELSE IF** doc includes intentionally deferred coverage item -> WARN with explicit defer tag.
- **ELSE** PASS.

### Rollback Plan
1. Revert Surface 13 script and Makefile target edits.
2. Re-run `make validate-local`.
3. Verify no regression in existing contract checks.

### Gate P4
- `make validate-surface13` passes in deterministic mode.
- Presence checks are traceable to declared contract source.
- No app code changes introduced.

---

## Phase 5 - Surface 14 Contract (Performance Budget)
**Complexity:** L  
**Estimated touch points:** 3-6 files modified/created

**Purpose:** Create missing performance budget contract artifact and baseline validator with proportional scope.

### Blast Radius
- **Services affected:** Dashboard, Backend, Agent API (validation contract only)
- **Pages affected:** None directly
- **Downstream consumers:** Release readiness and future perf hardening

### Tasks
- P5-01: **Create Surface 14 source-of-truth contract document**
  - Create `/home/zaks/bookkeeping/docs/PERFORMANCE-BUDGET.md`.
  - Include explicit budgets for:
    - Critical API latency expectations
    - Dashboard bundle size thresholds
    - Payload size thresholds for critical routes
  - **Checkpoint:** Document has measurable thresholds, owners, and measurement method notes.

- P5-02: **Create Surface 14 validator**
  - Create `/home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh`.
  - Minimum behavior:
    - Parse/validate budget document structure and thresholds
    - Run baseline measurable checks available locally (for example bundle artifact sizes when present)
    - Support advisory mode by default; strict mode optional for CI progression
  - **Checkpoint:** Script runs without requiring full performance test stack.

- P5-03: **Add standalone make target**
  - Add `validate-surface14` target in `/home/zaks/zakops-agent-api/Makefile`.
  - **Checkpoint:** `cd /home/zaks/zakops-agent-api && make validate-surface14` executes successfully.

### Decision Tree
- **IF** required measurement artifact is unavailable offline -> WARN in advisory mode.
- **ELSE IF** strict mode is requested and threshold exceeded -> FAIL.
- **ELSE** PASS.

### Rollback Plan
1. Revert Surface 14 new files/targets.
2. Re-run `make validate-local`.
3. Confirm baseline contract validation remains intact.

### Gate P5
- `PERFORMANCE-BUDGET.md` exists and is contract-grade (explicit thresholds).
- `make validate-surface14` works in advisory mode.
- Strict mode behavior is documented and testable.

---

## Phase 6 - Register Surfaces 10-14 in Unified Contract Pipeline
**Complexity:** L  
**Estimated touch points:** 4-7 files modified

**Purpose:** Move from standalone new validators to a single authoritative 14-surface contract system.

### Blast Radius
- **Services affected:** Full infra contract validation pipeline
- **Pages affected:** None directly
- **Downstream consumers:** Hooks, make targets, QA automation, operator workflows

### Tasks
- P6-01: **Register Surfaces 10-14 in contract surface catalog**
  - Update `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` with complete entries for 10-14:
    - boundary
    - source artifact
    - validation mechanism
    - key files
  - **Checkpoint:** Document lists all 14 surfaces with no placeholder entries.

- P6-02: **Extend unified validator from 9 to 14**
  - Update `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` to execute Surface 10-14 validators.
  - Update script header and final output to 14.
  - **Checkpoint:** Unified output explicitly reports each surface by number/name.

- P6-03: **Wire make targets and aggregate behavior**
  - Ensure `/home/zaks/zakops-agent-api/Makefile` supports:
    - individual `validate-surface10`..`validate-surface14`
    - aggregate `validate-contract-surfaces` covering 14/14
  - Keep `validate-local` and `validate-full` behavior coherent with new aggregate validator.
  - **Checkpoint:** `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces` passes with 14-surface output.

- P6-04: **Update stop-hook labeling/time budget if needed**
  - Update `/home/zaks/.claude/hooks/stop.sh` only if timeout/comment assumptions are no longer valid for 14-surface checks.
  - **Checkpoint:** Hook remains non-flaky and within time budget.

### Decision Tree
- **IF** unified validation exceeds hook budget -> tune timeout or gate composition, do not silently remove checks.
- **ELSE IF** a new surface validator is noisy/flaky -> tighten deterministic checks before wiring.
- **ELSE** proceed.

### Rollback Plan
1. Revert unified-wiring changes while preserving standalone surface validators.
2. Restore aggregate validator to prior stable state.
3. Re-run `make validate-local`.

### Gate P6
- Unified validator reports and evaluates 14 surfaces.
- `make validate-contract-surfaces` exits 0 only when all 14 pass.
- No orphaned validator scripts.

---

## Phase 7 - Manifest Expansion, CLAUDE Update, and Count Reconciliation
**Complexity:** L  
**Estimated touch points:** 4-8 files modified

**Purpose:** Complete system-wide truth alignment at 14 surfaces.

### Blast Radius
- **Services affected:** Infra manifest, startup guidance, boot diagnostics visibility
- **Pages affected:** None
- **Downstream consumers:** Operators, future builder sessions, QA audits

### Tasks
- P7-01: **Expand infra-snapshot to 14 surfaces**
  - Update `/home/zaks/tools/infra/generate-manifest.sh` so Contract Surfaces section reports all 14.
  - Include per-surface status details (exists/pass/fail/warn) and core metadata (path presence, line count or mtime where appropriate).
  - **Checkpoint:** `make infra-snapshot` output includes all 14 entries.

- P7-02: **Update CLAUDE.md last**
  - Update `/home/zaks/zakops-agent-api/CLAUDE.md` contract surface section from 9 to 14 only after P7-01 and Phase 6 gate are passing.
  - **Checkpoint:** CLAUDE table and total count accurately reflect final state.

- P7-03: **Reconcile counts across 4 authoritative sources**
  - Reconcile and record before/after table in completion report for:
    - `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md`
    - `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh`
    - `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md`
    - `/home/zaks/zakops-agent-api/CLAUDE.md`
  - **Checkpoint:** All 4 sources report 14 after completion.

### Decision Tree
- **IF** manifest shows NOT FOUND for artifacts that exist -> fix detection logic, not the artifact.
- **ELSE IF** CLAUDE count diverges from validator count -> block completion until reconciled.
- **ELSE** proceed to final verification.

### Rollback Plan
1. Revert CLAUDE and manifest edits if reconciliation fails.
2. Keep validator and registration changes intact.
3. Re-run `make infra-snapshot` and `make validate-contract-surfaces` after rollback.

### Gate P7
- `make infra-snapshot` reports 14 contract surfaces.
- CLAUDE.md says 14 and matches actual tooling.
- Reconciliation table shows 14 in all 4 sources.

---

## Phase 8 - Final Verification, Evidence, and Handoff
**Complexity:** M  
**Estimated touch points:** 2-4 files modified

**Purpose:** Prove no regressions, produce evidence, and close mission cleanly.

### Blast Radius
- **Services affected:** Validation and documentation workflows
- **Pages affected:** None
- **Downstream consumers:** QA mission, future maintenance missions

### Tasks
- P8-01: **Run final validation suite**
  - `cd /home/zaks/zakops-agent-api && make validate-local`
  - `cd /home/zaks/zakops-agent-api && make validate-contract-surfaces`
  - `cd /home/zaks/zakops-agent-api && make infra-snapshot`
  - `cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit`
  - **Checkpoint:** All required final checks pass.

- P8-02: **Produce completion report with evidence references**
  - Create `/home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md`.
  - Include:
    - Phase-by-phase outcomes
    - Final reconciliation table (before vs after)
    - Any deferred follow-ups explicitly marked
  - **Checkpoint:** Every AC is mapped to evidence.

- P8-03: **Bookkeeping and commit hygiene**
  - Update `/home/zaks/bookkeeping/CHANGES.md`.
  - Update checkpoint file with mission-closed status.
  - Commit changes as coherent units.
  - **Checkpoint:** Working tree reflects complete, traceable mission state.

### Decision Tree
- **IF** any final gate fails -> remediate and re-run failed gate plus `make validate-local`.
- **ELSE** mark mission complete and prepare QA successor.

### Rollback Plan
1. Revert latest phase-only documentation edits if evidence is incomplete.
2. Re-run final validation commands.
3. Regenerate completion report.

### Gate P8
- Final validation commands pass.
- Completion report exists with evidence per AC.
- CHANGES entry recorded.

---

## 4b. Dependency Graph

```
Phase 0 (Discovery + Baseline)
    |
    v
Phase 1 (Surface 11: Env Registry)
    |
    v
Phase 2 (Surface 10: Dependency Health)
    |
    v
Phase 3 (Surface 12: Error Taxonomy)
    |
    v
Phase 4 (Surface 13: Test Coverage)
    |
    v
Phase 5 (Surface 14: Performance Budget)
    |
    v
Phase 6 (Unified 14-Surface Wiring)
    |
    v
Phase 7 (Manifest + CLAUDE + Reconciliation)
    |
    v
Phase 8 (Final Verification + Handoff)
```

Phases execute sequentially; no parallel execution is permitted due count-consistency and registration-order dependencies.

---

## 5. Acceptance Criteria

### AC-1: Prerequisite Integrity
Baseline confirms prerequisite QA pass and 9-surface starting state before edits.

### AC-2: Surface 11 Validator Live
`validate-surface11` exists, runs, and catches env-registry drift classes.

### AC-3: Surface 10 Validator Live
`validate-surface10` exists, runs, and catches topology drift classes.

### AC-4: Surface 12 Validator Live
`validate-surface12` exists, runs, and validates documented error-shape anchors.

### AC-5: Surface 13 Validator Live
`validate-surface13` exists, runs, and enforces declared critical test-path presence.

### AC-6: Surface 14 Contract Created
`PERFORMANCE-BUDGET.md` exists with measurable thresholds and measurement strategy.

### AC-7: Surface 14 Validator Live
`validate-surface14` exists, runs in advisory mode, and supports strict enforcement mode.

### AC-8: Unified Validation at 14
`make validate-contract-surfaces` validates 14/14 surfaces and exits non-zero on failure.

### AC-9: Manifest Coverage at 14
`make infra-snapshot` produces 14-surface contract section with truthful per-surface status.

### AC-10: Count Reconciliation
All authoritative sources agree on 14 after completion:
- contract surface rule doc
- unified validator
- manifest
- CLAUDE system guide

### AC-11: No Regressions
`make validate-local` and dashboard TypeScript compile pass after changes.

### AC-12: Bookkeeping
`/home/zaks/bookkeeping/CHANGES.md` and completion report are updated with evidence.

---

## 6. Guardrails

1. Do not implement product features or endpoint redesign in this mission.
2. Do not remove or redesign Surfaces 1-9; only extend to 10-14.
3. Do not manually edit generated files (`*.generated.ts`, `*_models.py`).
4. Do not rewrite bookkeeping source docs wholesale; promote them through validators.
5. Do not update `/home/zaks/zakops-agent-api/CLAUDE.md` to 14 before wiring and gates pass.
6. Do not bypass unified validator wiring with orphan scripts at completion.
7. Do not introduce port 8090 references in contracts, validators, or manifests.
8. Do not change application code to force validator pass; log follow-up instead.
9. Do enforce LF endings on new `.sh` files and ownership sanity under `/home/zaks/`.
10. Do run `make validate-local` after each major phase.

---

## 7. Executor Self-Check Prompts

### After Phase 0
- [ ] Did I verify prerequisite QA is FULL PASS, not assumed pass?
- [ ] Did I capture all four baseline counts before editing anything?
- [ ] Did I confirm the baseline validator output is recorded with timestamps?

### After each new surface validator phase (1-5)
- [ ] Does this validator catch real drift, not just file existence?
- [ ] Are pass/fail semantics deterministic and non-flaky?
- [ ] Is this validator still within mission scope (no app feature edits)?

### Before Phase 6 wiring
- [ ] Are all five new validators individually runnable from Make targets?
- [ ] Did I avoid changing declared global counts prematurely?
- [ ] Are all paths absolute and environment-stable?

### Before marking mission complete
- [ ] Does unified validation explicitly report 14 surfaces?
- [ ] Does manifest show 14 surfaces with truthful status?
- [ ] Does CLAUDE.md match final reality and was it updated last?
- [ ] Does `make validate-local` pass now?
- [ ] Did I update CHANGES and completion evidence?

---

## 8. File Paths Reference

### Files to Modify

| File | Phase | Change |
|------|-------|--------|
| `/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md` | 6 | Register Surfaces 10-14 with full entries |
| `/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh` | 6 | Extend unified checks from 9 to 14 |
| `/home/zaks/zakops-agent-api/Makefile` | 1-6 | Add `validate-surface10`..`validate-surface14` and keep aggregate coherent |
| `/home/zaks/tools/infra/generate-manifest.sh` | 7 | Extend contract surface section to 14 with truthful statuses |
| `/home/zaks/zakops-agent-api/CLAUDE.md` | 7 | Update surface section to 14 (last) |
| `/home/zaks/.claude/hooks/stop.sh` | 6 (if needed) | Update labels/time budget only if 14-surface runtime requires it |
| `/home/zaks/bookkeeping/CHANGES.md` | 8 | Record mission changes |

### Files to Create

| File | Phase | Purpose |
|------|-------|---------|
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface10.sh` | 2 | Surface 10 dependency-health validator |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface11.sh` | 1 | Surface 11 env-registry validator |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface12.sh` | 3 | Surface 12 error-taxonomy validator |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface13.sh` | 4 | Surface 13 test-coverage-contract validator |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface14.sh` | 5 | Surface 14 performance-budget validator |
| `/home/zaks/bookkeeping/docs/PERFORMANCE-BUDGET.md` | 5 | Surface 14 source-of-truth artifact |
| `/home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-BASELINE.md` | 0 | Baseline evidence and before counts |
| `/home/zaks/bookkeeping/docs/SURFACES-10-14-REGISTER-001-COMPLETION.md` | 8 | Completion report with reconciliation table |
| `/home/zaks/bookkeeping/mission-checkpoints/SURFACES-10-14-REGISTER-001.md` | all | Continuation checkpoint for multi-session execution |

### Files to Read (Do Not Modify Unless an Explicit Task Requires It)

| File | Purpose |
|------|---------|
| `/home/zaks/bookkeeping/docs/FRONTEND-INFRASTRUCTURE-AUDIT.md` | Audit findings and gap registry |
| `/home/zaks/bookkeeping/docs/FORENSIC-AUDIT-RESULTS-FORENSIC-AUDIT-SURFACES-002` | Forensic ordering and area findings for Surfaces 10-14 |
| `/home/zaks/bookkeeping/docs/QA-SR-VERIFY-001-SCORECARD.md` | Existing verification baseline context |
| `/home/zaks/bookkeeping/docs/QA-ITR-VERIFY-001.md` | Prerequisite QA pass evidence |
| `/home/zaks/bookkeeping/docs/SERVICE-TOPOLOGY.md` | Surface 10 artifact |
| `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md` | Surface 11 artifact |
| `/home/zaks/bookkeeping/docs/ERROR-SHAPES.md` | Surface 12 artifact |
| `/home/zaks/bookkeeping/docs/TEST-COVERAGE-GAPS.md` | Surface 13 artifact |
| `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | Canonical memory context and counts |
| `/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md` | Manifest output validation target |

---

## 9. Stop Condition

Stop when all ACs (AC-1 through AC-12) are met, unified validation and manifest both reflect 14 surfaces, count reconciliation is complete across all 4 authoritative sources, `make validate-local` passes, and completion evidence is written.

Do not proceed into frontend governance backlog work (a11y rule expansion, component-pattern rule authoring, Playwright policy changes) within this mission. Those are separate follow-on scope once QA validates this mission.

---

*End of Mission Prompt - SURFACES-10-14-REGISTER-001*
