# PASS 2 — SECTION MAP

- Generated at (UTC): 2026-01-27T02:15:00Z
- Purpose: Define canonical section structure for merged Standard and QA prompts

---

## STANDARD PROMPT — Section Structure

| Section # | Section Name | Source(s) | Merge Decision |
|-----------|--------------|-----------|----------------|
| 0 | PRIME DIRECTIVE | A: Constitution, B: Preamble, C: 0) Prime Directive | Merge strongest language |
| 1 | FORBIDDEN PHRASES | A: A.1, B: 3.1, C: 1) | Superset list |
| 2 | EVIDENCE STANDARD | A: A.2, B: Section 4, C: Section 7 | Dual-channel + comprehensive |
| 3 | ARCHITECTURAL CONTAINMENT | A: A.3, B: Section 7, C: Scope rules | Strongest constraints |
| 4 | MISSION INPUTS | A: Section B, B: Section 1-2, C: Section 3 | Template placeholders |
| 5 | EXECUTION PROTOCOL | A: Section C (Phases 1-4), B: Section 6-8, C: Section 2 format | Gate-based loop |
| 6 | GATE ENFORCEMENT | B: Section 8, C: Section 10-11 | Strictest rules |
| 7 | COMMAND LEDGER | B: Section 12, C: Section 4 | JSONL append-only |
| 8 | CODE INTEGRITY | B: Section 7, C: Section 5 | Pre/post checksums |
| 9 | SERVICE IDENTITY | C: Section 6 | PID→SHA256 chain |
| 10 | UI/NETWORK STRICTNESS | C: Section 8 | Zero console errors |
| 11 | NEGATIVE PROOF | A: Phase 4, C: Section 9 | Proof of absence |
| 12 | RELIABILITY | B: Persistence, C: Section 10 | 3-run + restart |
| 13 | TROUBLESHOOTING DISCIPLINE | C: Section 11 | Single hypothesis |
| 14 | COMPLETION PACKET | A: Section D, B: Section 13, C: Section 14 | Superset artifacts |

---

## QA PROMPT — Section Structure

| Section # | Section Name | Source(s) | Merge Decision |
|-----------|--------------|-----------|----------------|
| 0 | AUDITOR ROLE | B: Role Definition, C: Intro | Zero-trust adversarial |
| 1 | AUDITOR MINDSET | B: Section 1 | 5 Zero Trust Rules |
| 2 | FRAUD DETECTION | B: 1.2 Red Flags | Patterns list |
| 3 | AUDIT INPUTS | C: 0) Inputs | Template placeholders |
| 4 | PRIME DIRECTIVE | C: 1) Auditor Prime Directive | No paraphrase as proof |
| 5 | AUDIT PROCEDURE | B: Section 2 (8 phases), C: Section 3 | 8-phase + cross-checks |
| 6 | OUTPUT FORMAT | C: 2) Required Output Format | 9-section report |
| 7 | SCORING RULES | C: 4) Scoring/Verdict | PASS/FAIL/UNPROVEN |
| 8 | DELIVERABLES | C: 5) Deliverables | 4 required matrices |
| 9 | AUDIT REPORT TEMPLATE | B: Section 3 | Full template |
| 10 | QUICK CHECKLIST | B: Section 4 | Phase checklist |
| 11 | FINAL INSTRUCTIONS | B: Section 6 | 10 commandments |

---

## Standard Prompt — Detailed Section Breakdown

### SECTION 0: PRIME DIRECTIVE
**Content**: Non-negotiable rules that override everything else
- No claim without evidence
- No handwaving without raw output
- No scope drift
- Hard stop gates
- Immediate rollback on out-of-scope changes

**Source anchors**: STD-A Constitution, STD-B Preamble, STD-C-REQ-002..006

### SECTION 1: FORBIDDEN PHRASES
**Content**: Complete banned phrases list (uncertainty + deflection)
**Source anchors**: STD-A-REQ-003..008, STD-B-REQ-019..021, STD-C-REQ-007..011

### SECTION 2: EVIDENCE STANDARD
**Content**:
- Dual-channel proof requirement
- Evidence block format template
- SHA256 requirements
- Artifact path conventions

**Source anchors**: STD-A-REQ-009..017, STD-B Section 4, STD-C-REQ-054..058

### SECTION 3: ARCHITECTURAL CONTAINMENT
**Content**:
- No new patterns (use existing codebase patterns)
- Scope locking (only modify approved files)
- Dependency freeze (no package installs unless explicit target)
- Out-of-scope = immediate rollback

**Source anchors**: STD-A-REQ-018..022, STD-B-REQ-026,048, STD-C-REQ-004..005,049..050

### SECTION 4: MISSION INPUTS (Template)
**Placeholders**:
- `{{SYMPTOM}}` - Current symptom description
- `{{REPRODUCTION_COMMAND}}` - How to reproduce
- `{{ERROR_SIGNATURE}}` - Exact error message
- `{{REPO_ROOT}}` - Repository root path
- `{{RUNTIME}}` - docker/systemd/node/python/etc
- `{{CRITICAL_PORTS}}` - Required services/ports
- `{{FORBIDDEN_PORTS}}` - Legacy/banned services
- `{{DATASTORES}}` - Primary DBs and tables
- `{{LOG_PATHS}}` - Observability locations
- `{{ACCEPTANCE_CRITERIA}}` - Testable ACs
- `{{APPROVED_SCOPE}}` - Files/dirs that may change
- `{{MAX_ENDPOINT_SECONDS}}` - API latency limit
- `{{MAX_UI_SECONDS}}` - UI interaction limit
- `{{ERROR_STRINGS}}` - Signature error strings

**Source anchors**: STD-A Section B, STD-B Section 1-2, STD-C Section 3

### SECTION 5: EXECUTION PROTOCOL
**Content**: The main execution loop
- Phase 1: Forensic Discovery (READ-ONLY)
- Phase 2: Hypothesis & Simulation
- Phase 3: Surgical Intervention
- Phase 4: Red-to-Green Proof

**Source anchors**: STD-A Section C, STD-B Section 6-8, STD-C Section 2

### SECTION 6: GATE ENFORCEMENT
**Content**:
- Sequential gates (no skipping)
- Focus rule (only work on failing gate)
- Two-strike rollback
- Gate attempt log format

**Source anchors**: STD-B-REQ-052..066, STD-C-REQ-069..074

### SECTION 7: COMMAND LEDGER
**Content**:
- JSONL append-only format
- Required fields: ts, phase, cmd, cwd, why, output_file
- Must log before execution
- Must capture output to file

**Source anchors**: STD-B-REQ-081..086, STD-C-REQ-047..048

### SECTION 8: CODE INTEGRITY
**Content**:
- Pre-change checksums (sha256sum of approved scope)
- Post-change checksums
- Tree hash comparison
- Immediate self-rollback on out-of-scope changes

**Source anchors**: STD-B Section 7, STD-C Section 5

### SECTION 9: SERVICE IDENTITY
**Content**:
- Port → PID → PPID → exe path → SHA256 of executable
- Build identity: git SHA + container digest
- Must verify for every critical service

**Source anchors**: STD-C-REQ-051..053

### SECTION 10: UI/NETWORK STRICTNESS
**Content**:
- Zero console errors/warnings (network/fetch/CORS/hydration)
- HAR shows no 4xx/5xx, no retry storms
- Interactions must be real (not cached)
- Must verify in Incognito with cleared storage

**Source anchors**: STD-C-REQ-059..065

### SECTION 11: NEGATIVE PROOF
**Content**:
- Prove signature error strings are absent
- Check last N≥1000 relevant log lines
- Working UI is not enough; error must be gone

**Source anchors**: STD-A Phase 4, STD-C-REQ-066..068

### SECTION 12: RELIABILITY
**Content**:
- Must pass 3 consecutive runs
- Must survive restart
- Idempotency: 2nd run produces 0 net changes

**Source anchors**: STD-B Persistence, STD-C-REQ-069..071

### SECTION 13: TROUBLESHOOTING DISCIPLINE
**Content**:
- One falsifiable hypothesis per attempt
- Bisection (git bisect or manual) to isolate root cause
- SSOT breach triggers immediate rollback + re-baseline

**Source anchors**: STD-C-REQ-072..074

### SECTION 14: COMPLETION PACKET
**Content**: Required artifacts list
1. ledger.jsonl
2. diff.patch
3. verification_script.sh
4. resource_snapshot.txt
5. evidence_manifest.sha256
6. HAR(s) + console captures
7. Pre/post checksum reports
8. Reproducibility instruction
9. "No green until red" demonstration

**Source anchors**: STD-A-REQ-057..069, STD-B-REQ-087..095, STD-C-REQ-080..088

---

## QA Prompt — Detailed Section Breakdown

### SECTION 0: AUDITOR ROLE
**Content**: Adversarial QA Auditor identity and mission

### SECTION 1: AUDITOR MINDSET
**Content**: 5 Zero Trust Rules
- Rule 1: Never trust Builder claims
- Rule 2: Independent verification
- Rule 3: Assume adversarial Builder
- Rule 4: Verify the verifiers
- Rule 5: No benefit of the doubt

### SECTION 2: FRAUD DETECTION
**Content**: Red flags to look for
- Fake file indicators
- Fake output indicators
- Fake fix indicators
- Evidence manipulation indicators
- Scope violation indicators

### SECTION 3: AUDIT INPUTS (Template)
**Placeholders**:
- `{{MISSION_PROMPT}}` - Full mission prompt used
- `{{AGENT_TRANSCRIPT}}` - All agent responses
- `{{COMPLETION_PACKET}}` - Artifact list with hashes
- `{{ENVIRONMENT_FACTS}}` - Ports, services, DBs, ACs

### SECTION 4: PRIME DIRECTIVE
**Content**:
- No paraphrase as proof
- Reject claims without Evidence Block
- UNVERIFIABLE = FAIL
- Fabricated evidence = AUTO-FAIL

### SECTION 5: AUDIT PROCEDURE (8 Phases)
- Phase 0: Claim Inventory
- Phase 1: Artifact Existence Verification
- Phase 2: Independent Functional Verification
- Phase 3: Evidence Block Validation
- Phase 4: Scope Violation Check
- Phase 5: Forensic Ledger Verification
- Phase 6: Acceptance Criteria Verification
- Phase 7: Persistence & Stability Verification
- Phase 8: Attack Surface Scan

### SECTION 6: OUTPUT FORMAT (9 Sections)
1. AUDIT VERDICT
2. TOP 10 FINDINGS
3. EVIDENCE CONSISTENCY CHECKS
4. ARTIFACT AUTHENTICITY CHECKS
5. INSTRUCTION COMPLIANCE MATRIX
6. FIX VALIDATION MATRIX
7. SCOPE & INTEGRITY CHECKS
8. REPRODUCIBILITY CHECK
9. REQUIRED REMEDIATIONS

### SECTION 7: SCORING RULES
**Content**: PASS/FAIL/UNPROVEN criteria

### SECTION 8: DELIVERABLES
**Content**: 4 required matrices
- Instruction Compliance Matrix
- Fix Validation Matrix
- Tamper/Fabrication Findings
- Remediation List

### SECTION 9: AUDIT REPORT TEMPLATE
**Content**: Full template with all fields

### SECTION 10: QUICK CHECKLIST
**Content**: Phase-by-phase checkbox list

### SECTION 11: FINAL INSTRUCTIONS
**Content**: 10 commandments for auditors

---

## Cross-Reference: Standard Section → QA Verification

| Standard Section | QA Verification Phase |
|-----------------|----------------------|
| 1: Forbidden Phrases | Phase 3: Evidence Block Validation |
| 2: Evidence Standard | Phase 3: Evidence Block Validation |
| 3: Architectural Containment | Phase 4: Scope Violation Check |
| 6: Gate Enforcement | Phase 6: Acceptance Criteria |
| 7: Command Ledger | Phase 5: Forensic Ledger |
| 8: Code Integrity | Phase 4: Scope Violation Check |
| 9: Service Identity | Phase 2: Functional Verification |
| 10: UI/Network Strictness | Phase 2: Functional Verification |
| 11: Negative Proof | Phase 6: Acceptance Criteria |
| 12: Reliability | Phase 7: Persistence & Stability |
| 14: Completion Packet | Phase 1: Artifact Existence |
