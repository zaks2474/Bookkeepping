# PASS 2 — MERGE DECISIONS

- Generated at (UTC): 2026-01-27T02:15:00Z
- Input: PASS1_CONFLICT_REGISTER.md, PASS1_PAIR_ALIGNMENT_MAP.md, PASS1_DECISION_GATES.md

## Summary

This document records all merge decisions made when synthesizing the 6 source prompts (Standard A/B/C + QA A/B/C) into unified Standard and QA drafts.

---

## STD-CONFLICT-01 Resolution: Artifact Requirements (Standard A vs B)

### Conflict
Standard A requires: `ledger.jsonl`, `diff.patch`, `verification_script.sh`, `resource_snapshot.txt`
Standard B requires: Evidence Manifest, HAR(s), console captures, screenshots, logs, DB outputs, pre/post checksums, E2E outputs, JSONL ledger

### Decision: MERGE → SUPERSET
**Rationale**: Both enforce traceability. Per "Stricter wins" gate, merge into superset.

**Final Artifact List (Standard)**:
1. `ledger.jsonl` — append-only command log (from A + B + C)
2. `diff.patch` — exact code changes (from A)
3. `verification_script.sh` — single verification script returning 0 on success (from A)
4. `resource_snapshot.txt` — CPU/Memory before vs after within 15% (from A)
5. `evidence_manifest.sha256` — SHA256 for every artifact (from B + C)
6. HAR(s) + console captures — browser proof (from B + C)
7. Pre/post checksum reports — scope integrity proof (from B + C)
8. Reproducibility instruction — fresh-clone single command (from C)

**Traceability**: STD-A-REQ-057..069, STD-B-REQ-087..091, STD-C-REQ-080..088

---

## STD-CONFLICT-02 Resolution: Artifact Requirements (Standard A vs C)

### Conflict
Standard C adds: HAR(s), console captures, DB query outputs, "No green until red" demonstration

### Decision: MERGE → INCLUDE ALL
**Rationale**: Standard C's additions are non-conflicting and strengthen evidence requirements. Per "Externally verifiable > self-reported" gate.

**Action**: Add to Final Artifact List:
- "No green until red" demonstration artifact (controlled failure → restore → pass)

**Traceability**: STD-C-REQ-088

---

## QA-CONFLICT-01 Resolution: Audit Structure (QA A vs B)

### Conflict
QA A: Implicit audit via same evidence standard as Standard A
QA B: Explicit 8-phase audit procedure with scripts

### Decision: SELECT QA B STRUCTURE
**Rationale**: Per "Deterministic > subjective" and "Externally verifiable > self-reported" gates, QA B's explicit scripted phases are stronger.

**Final QA Structure**:
- Phase 0: Claim Inventory
- Phase 1: Artifact Existence Verification
- Phase 2: Independent Functional Verification
- Phase 3: Evidence Block Validation
- Phase 4: Scope Violation Check
- Phase 5: Forensic Ledger Verification
- Phase 6: Acceptance Criteria Verification
- Phase 7: Persistence & Stability Verification
- Phase 8: Attack Surface Scan

**Traceability**: QA-B sections 2.1-2.9

---

## QA-CONFLICT-02 Resolution: Audit Structure (QA A vs C)

### Conflict
QA C: 9-section output format with matrices

### Decision: MERGE QA B + C
**Rationale**: QA B provides procedure, QA C provides output format. Both are complementary.

**Final QA Output Format** (from QA C):
1. AUDIT VERDICT (PASS / FAIL / UNPROVEN)
2. TOP 10 FINDINGS (ranked by severity)
3. EVIDENCE CONSISTENCY CHECKS
4. ARTIFACT AUTHENTICITY CHECKS
5. INSTRUCTION COMPLIANCE MATRIX
6. FIX VALIDATION MATRIX (per acceptance criterion)
7. SCOPE & INTEGRITY CHECKS
8. REPRODUCIBILITY CHECK
9. REQUIRED REMEDIATIONS (if not PASS)

**Traceability**: QA-C section 2

---

## STDvQA-MISMATCH-01 Resolution: Rollback/Forbidden Requirements

### Conflict
Multiple Standard excerpts mandate "immediate rollback" for out-of-scope changes and "forbidden port" checks, but these are not explicitly verified by QA prompts in some pairs.

### Decision: ADD QA VERIFICATION
**Rationale**: Per "Maintain Standard↔QA alignment" gate, add explicit QA checks.

**Action**: Add to QA Phase 4 (Scope Violation Check):
- Verify rollback occurred if out-of-scope changes detected
- Verify forbidden ports are dead (included in Phase 8: Attack Surface)

**Action**: Add to QA Phase 8 (Attack Surface Scan):
- Check FORBIDDEN_PORTS list
- Verify no legacy listeners
- Check SSOT breach conditions

**Traceability**: STDvQA-MISMATCH-01 excerpts 1-15

---

## Banned Phrases Consolidation

### Sources
- Standard A: A.1 THE LANGUAGE OF RIGOR (7 banned phrase categories)
- Standard B: 3.1 FORBIDDEN PHRASES (expanded list with deflection language)
- Standard C: 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED)

### Decision: MERGE → SUPERSET
**Final Banned Phrases List**:

**Uncertainty/Laziness (AUTO-FAIL)**:
- "should work", "probably", "likely", "might", "maybe"
- "I think", "I believe", "theoretically", "seems"
- "works for me", "can't reproduce", "local issue", "it's fine", "looks good"
- "acceptable trade-off", "minor bug"
- "done" / "fixed" (without evidence block)
- "complete" (without completion packet)
- "verified" (without dual-channel proof)
- "tested" (without raw output shown)

**Deflection Language (BANNED)**:
- "that's a different issue", "unrelated"
- "separate concern", "out of band"
- "not blocking", "can address later"
- "low priority", "minor issue"
- "cosmetic", "non-critical"
- "auth required", "out of scope"

**Traceability**: STD-A-REQ-003..008, STD-B-REQ-019..021, STD-C-REQ-007..011

---

## Evidence Block Format Decision

### Sources
- Standard A: A.2 Universal Evidence Standard (4 components)
- Standard B: Section 4 Mandatory Evidence Block Template (detailed format)
- Standard C: Section 7 Proof Standard (Dual-Channel)

### Decision: MERGE → COMPREHENSIVE FORMAT
**Final Evidence Block Components**:
1. CLAIM + TIMESTAMP
2. CHANNEL A (Browser/UI): command, HAR, console capture
3. CHANNEL B (System/API): command, raw output, artifact path + SHA256
4. STATE VERIFICATION: method + evidence
5. NEGATIVE TEST (Red-to-Green): break, failure evidence, restore, success evidence
6. VERDICT: PROVEN / UNPROVEN

**Traceability**: STD-A-REQ-009..017, STD-B section 4, STD-C-REQ-054..058

---

## Gate Enforcement Decision

### Sources
- Standard A: PHASE 1-4 (Discovery, Hypothesis, Intervention, Proof)
- Standard B: Section 8 GATE ENFORCEMENT (sequential, focus, two-strike rollback)
- Standard C: Hard stop gates, 3 consecutive runs

### Decision: MERGE → STRICTEST
**Final Gate Rules**:
1. SEQUENTIAL: Gates must pass in order. No skipping.
2. FOCUS: If Gate N fails, only work on Gate N. Nothing else.
3. TWO-STRIKE ROLLBACK: If same gate fails 2 consecutive times → ROLLBACK + bisect root cause
4. 3-RUN STABILITY: Every gate must pass 3 consecutive runs
5. RESTART PERSISTENCE: Must survive service restart
6. HARD STOP: Gate failure = no progress until fixed

**Traceability**: STD-B-REQ-052..062, STD-C-REQ-069..074

---

## Scope Integrity Decision

### Sources
All three Standard prompts mandate scope locking and immediate rollback.

### Decision: STRONGEST ENFORCEMENT
**Final Scope Rules**:
1. Pre-change checksums required (tree hash of approved scope)
2. Out-of-scope file modification = IMMEDIATE SELF-ROLLBACK
3. No exceptions, no "quick fixes" to unrelated areas
4. Post-change checksums required
5. Tree hash delta must match scope hash delta

**Traceability**: STD-A-REQ-020..021, STD-B-REQ-026,048,093, STD-C-REQ-049..050

---

## Alias Mapping (Artifact Name Reconciliation)

| Canonical Name | Aliases | Source |
|---------------|---------|--------|
| `ledger.jsonl` | command_ledger.jsonl, forensic_ledger.jsonl | A, B, C |
| `evidence_manifest.sha256` | COMPLETION_PACKET_MANIFEST.sha256 | B, C |
| `verification_script.sh` | gate_verification.sh | A |
| `completion_packet/` | COMPLETION_PACKET_DIR | B |

---

## Decision Log

| Decision ID | Conflict | Resolution | Gate Applied |
|-------------|----------|------------|--------------|
| MERGE-001 | STD-CONFLICT-01 | Superset artifacts | Stricter wins |
| MERGE-002 | STD-CONFLICT-02 | Include all | Externally verifiable > self-reported |
| MERGE-003 | QA-CONFLICT-01 | Select QA B structure | Deterministic > subjective |
| MERGE-004 | QA-CONFLICT-02 | Merge B + C | Non-conflicting complement |
| MERGE-005 | STDvQA-MISMATCH-01 | Add QA verification | Standard↔QA alignment |
| MERGE-006 | Banned phrases | Superset | Stricter wins |
| MERGE-007 | Evidence block | Comprehensive format | Stricter wins |
| MERGE-008 | Gate enforcement | Strictest rules | Non-bypassable > bypassable |
| MERGE-009 | Scope integrity | Strongest enforcement | Non-bypassable > bypassable |
