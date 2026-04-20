# PASS 1 — REQUIREMENT LEDGER

- Source file: /mnt/c/Users/mzsai/Downloads/STANDARD PROMPT SET.txt
- Generated at (UTC): 2026-01-27T01:23:53Z

---

## 1) Document Fingerprints

### STANDARD_A
- Length estimate: ~151 lines, ~4897 chars
- Unique features:
  - Banned/forbidden language enforcement
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet
  - Rollback requirements
- Biggest strengths:
  - Banned/forbidden language enforcement
  - Evidence blocks / raw output requirement

### STANDARD_B
- Length estimate: ~1051 lines, ~64060 chars
- Unique features:
  - Banned/forbidden language enforcement
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet
  - Explicit gates + PASS/FAIL semantics
  - Rollback requirements
- Biggest strengths:
  - Banned/forbidden language enforcement
  - Evidence blocks / raw output requirement

### STANDARD_C
- Length estimate: ~268 lines, ~7225 chars
- Unique features:
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet
  - Explicit gates + PASS/FAIL semantics
  - Rollback requirements
  - Adversarial QA auditor mindset
- Biggest strengths:
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet

### QA_A
- Length estimate: ~151 lines, ~4890 chars
- Unique features:
  - Banned/forbidden language enforcement
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet
  - Rollback requirements
- Biggest strengths:
  - Banned/forbidden language enforcement
  - Evidence blocks / raw output requirement

### QA_B
- Length estimate: ~1637 lines, ~69174 chars
- Unique features:
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet
  - Explicit gates + PASS/FAIL semantics
  - Adversarial QA auditor mindset
  - Fraud detection / verify-the-verifiers
- Biggest strengths:
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet

### QA_C
- Length estimate: ~220 lines, ~6448 chars
- Unique features:
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet
  - Rollback requirements
  - Adversarial QA auditor mindset
- Biggest strengths:
  - Evidence blocks / raw output requirement
  - Mandatory artifacts / completion packet

---

## 2) Atomic Requirement Ledger

Notes:
- “Requirement Text” is copied verbatim (sentence-level splitting only).
- “Source anchor” is the nearest preceding heading line in the prompt content.

### STD-A-REQ-001
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: | **Constraints** | READ-ONLY UNTIL HYPOTHESIS VALIDATED |
- Source anchor: ## PROTOCOL: ZERO TRUST | FORENSIC RIGOR | NO EXCUSES

### STD-A-REQ-002
- Domain: Standard
- Variant: A
- Category: Gates
- Strength: MUST
- Requirement Text: **⛔ VIOLATION OF ANY RULE BELOW = IMMEDIATE MISSION FAILURE ⛔**
- Source anchor: # SECTION A: THE "IMMUTABLE" CONSTITUTION

### STD-A-REQ-003
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: The following phrases indicate uncertainty/laziness and are **FORBIDDEN**:
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### STD-A-REQ-004
- Domain: Standard
- Variant: A
- Category: Other
- Strength: SHOULD
- Requirement Text: * ❌ "should work", "probably", "likely", "might"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### STD-A-REQ-005
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * ❌ "I think", "I believe", "theoretically"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### STD-A-REQ-006
- Domain: Standard
- Variant: A
- Category: Repro
- Strength: OPTIONAL
- Requirement Text: * ❌ "works for me", "can't reproduce", "local issue"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### STD-A-REQ-007
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * ❌ "acceptable trade-off", "minor bug"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### STD-A-REQ-008
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: * ❌ "done" (without evidence), "fixed" (without proof)
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### STD-A-REQ-009
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: Every action that modifies state or code must include:
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-010
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-011
- Domain: Standard
- Variant: A
- Category: Repro
- Strength: IMPLIED
- Requirement Text: **The Command:** Exact, reproducible command run.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-012
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-013
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **The Raw Output:** Unedited, non-truncated stdout/stderr.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-014
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-015
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **The State Verification:** Proof that the system state changed (DB query, file hash, API response).
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-016
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-017
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **The Negative Test:** Proof that the test fails when the fix is removed (Red -> Green).
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### STD-A-REQ-018
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: * **No New Patterns:** You must use existing design patterns found in the codebase.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### STD-A-REQ-019
- Domain: Standard
- Variant: A
- Category: Scope
- Strength: MUST
- Requirement Text: Do not introduce new frameworks or libraries unless explicitly authorized.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### STD-A-REQ-020
- Domain: Standard
- Variant: A
- Category: Scope
- Strength: OPTIONAL
- Requirement Text: * **Scope Locking:** You may only modify files within `{{AUTHORIZED_SCOPE}}`.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### STD-A-REQ-021
- Domain: Standard
- Variant: A
- Category: Scope
- Strength: MUST
- Requirement Text: Modifying files outside this scope triggers an **Immediate Rollback**.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### STD-A-REQ-022
- Domain: Standard
- Variant: A
- Category: UI
- Strength: IMPLIED
- Requirement Text: * **Dependency Freeze:** No `npm install`, `pip install`, or `apt-get` allowed unless the `package.json`/`requirements.txt` is the explicit target of the task.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### STD-A-REQ-023
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Symptom:** {{CURRENT_SYMPTOM_DESCRIPTION}}
- Source anchor: ## B.1 THE STARTING STATE

### STD-A-REQ-024
- Domain: Standard
- Variant: A
- Category: Repro
- Strength: IMPLIED
- Requirement Text: * **Reproduction Path:** `{{REPRODUCTION_COMMAND}}`
- Source anchor: ## B.1 THE STARTING STATE

### STD-A-REQ-025
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Error Signature:** `{{EXACT_ERROR_MESSAGE}}`
- Source anchor: ## B.1 THE STARTING STATE

### STD-A-REQ-026
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: The mission is ONLY complete when **ALL** of the following are true:
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-027
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-028
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: [ ] The specific symptom in B.1 is resolved.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-029
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-030
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: [ ] **Proof of Absence:** The "Error Signature" no longer appears in logs.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-031
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-032
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: [ ] **Regression Check:** `{{CRITICAL_FUNCTION}}` still works.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-033
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-034
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: [ ] **Forensic Packet:** A JSONL ledger of all commands is delivered.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-035
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 5.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-036
- Domain: Standard
- Variant: A
- Category: Repro
- Strength: IMPLIED
- Requirement Text: [ ] **Fresh Clone Test:** The solution works on a fresh environment.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### STD-A-REQ-037
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: **YOU MUST FOLLOW THIS LOOP RECURSIVELY.
- Source anchor: # SECTION C: EXECUTION PROTOCOL (THE LOOP)

### STD-A-REQ-038
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: DO NOT SKIP STEPS.**
- Source anchor: # SECTION C: EXECUTION PROTOCOL (THE LOOP)

### STD-A-REQ-039
- Domain: Standard
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: * **Allowed:** `cat`, `grep`, `ls`, `curl (GET)`, `ps`, `logs`.
- Source anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY)

### STD-A-REQ-040
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: * **Forbidden:** Editors, `sed`, `curl (POST/PUT/DELETE)`, `restart`.
- Source anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY)

### STD-A-REQ-041
- Domain: Standard
- Variant: A
- Category: UI
- Strength: IMPLIED
- Requirement Text: * **Requirement:** Identify the `PID`, `File Path`, and `Line Number` of the fault.
- Source anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY)

### STD-A-REQ-042
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Format:**
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### STD-A-REQ-043
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Hypothesis:** "The issue is caused by X because Y."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### STD-A-REQ-044
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Proposed Fix:** "I will change line N in file Z."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### STD-A-REQ-045
- Domain: Standard
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: * **Simulation:** "If I run this, I expect log stream A to stop showing error B."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### STD-A-REQ-046
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Risk:** "This might break feature C."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### STD-A-REQ-047
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: * **Pre-Flight:** Hash the file before editing (`sha256sum`).
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### STD-A-REQ-048
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Action:** Apply the edit.
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### STD-A-REQ-049
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Post-Flight:** Hash the file after editing.
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### STD-A-REQ-050
- Domain: Standard
- Variant: A
- Category: Repro
- Strength: MUST
- Requirement Text: * **Verify:** Run the reproduction command immediately.
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### STD-A-REQ-051
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### STD-A-REQ-052
- Domain: Standard
- Variant: A
- Category: Negative Proof
- Strength: IMPLIED
- Requirement Text: **Show Green:** Show the system working.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### STD-A-REQ-053
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### STD-A-REQ-054
- Domain: Standard
- Variant: A
- Category: Gates
- Strength: IMPLIED
- Requirement Text: **Force Red:** Revert the change (or break it intentionally) and prove it fails again.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### STD-A-REQ-055
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### STD-A-REQ-056
- Domain: Standard
- Variant: A
- Category: Negative Proof
- Strength: IMPLIED
- Requirement Text: **Return to Green:** Re-apply the fix and confirm success.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### STD-A-REQ-057
- Domain: Standard
- Variant: A
- Category: Evidence
- Strength: MUST
- Requirement Text: At the end of the mission, you must generate a **COMPLETION PACKET** containing:
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-058
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-059
- Domain: Standard
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: **`ledger.jsonl`**: Every command executed, timestamped.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-060
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-061
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: **`diff.patch`**: The exact code changes.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-062
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-063
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: **`verification_script.sh`**: A single script that:
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-064
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * Checks the fix.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-065
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * Checks for regressions.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-066
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * Returns `0` only if PERFECTION is achieved.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-067
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-068
- Domain: Standard
- Variant: A
- Category: Performance
- Strength: IMPLIED
- Requirement Text: **`resource_snapshot.txt`**: CPU/Memory usage before vs.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-069
- Domain: Standard
- Variant: A
- Category: Performance
- Strength: MUST
- Requirement Text: after (Must be within 15% variance).
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### STD-A-REQ-070
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Target Files:** `{{TARGET_FILES}}`
- Source anchor: # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK

### STD-A-REQ-071
- Domain: Standard
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: * **Relevant Logs:** `{{LOG_PATH}}`
- Source anchor: # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK

### STD-A-REQ-072
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Test Command:** `{{TEST_COMMAND}}`
- Source anchor: # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK

### STD-A-REQ-073
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: **You are a Senior Principal Engineer.
- Source anchor: # FINAL WARNING

### STD-A-REQ-074
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: You do not guess.
- Source anchor: # FINAL WARNING

### STD-A-REQ-075
- Domain: Standard
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: You do not "try" things.
- Source anchor: # FINAL WARNING

### STD-A-REQ-076
- Domain: Standard
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: You measure, you analyze, you execute, and you prove.**
- Source anchor: # FINAL WARNING

### STD-B-REQ-001
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## CONTENT B

### STD-B-REQ-002
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: Copy this entire template
- Source anchor: ## CONTENT B

### STD-B-REQ-003
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## CONTENT B

### STD-B-REQ-004
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: Fill in the [PLACEHOLDERS] in Section 1 (Task Definition)
- Source anchor: ## CONTENT B

### STD-B-REQ-005
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## CONTENT B

### STD-B-REQ-006
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: IMPLIED
- Requirement Text: Customize Section 2 (Scope) for your specific task
- Source anchor: ## CONTENT B

### STD-B-REQ-007
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: ## CONTENT B

### STD-B-REQ-008
- Domain: Standard
- Variant: B
- Category: Performance
- Strength: IMPLIED
- Requirement Text: Adjust time budgets in Section 9 if needed
- Source anchor: ## CONTENT B

### STD-B-REQ-009
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 5.
- Source anchor: ## CONTENT B

### STD-B-REQ-010
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: Add task-specific gates in Section 11
- Source anchor: ## CONTENT B

### STD-B-REQ-011
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 6.
- Source anchor: ## CONTENT B

### STD-B-REQ-012
- Domain: Standard
- Variant: B
- Category: UI
- Strength: IMPLIED
- Requirement Text: Send to Claude Code / Builder / Agent
- Source anchor: ## CONTENT B

### STD-B-REQ-013
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   SUCCESS CRITERIA (ALL must be true):                                       ║
- Source anchor: ## CONTENT B

### STD-B-REQ-014
- Domain: Standard
- Variant: B
- Category: Repro
- Strength: MUST
- Requirement Text: ║   [Must be reproducible and automatable]                                    ║
- Source anchor: ## CONTENT B

### STD-B-REQ-015
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: MUST
- Requirement Text: ║   EXPLICITLY OUT OF SCOPE (DO NOT touch):                                   ║
- Source anchor: ## CONTENT B

### STD-B-REQ-016
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   DEPENDENCIES (systems that must remain working):                          ║
- Source anchor: ## CONTENT B

### STD-B-REQ-017
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   • [Must maintain backward compatibility]                                  ║
- Source anchor: ## CONTENT B

### STD-B-REQ-018
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   • [Must not increase response time by >20%]                               ║
- Source anchor: ## CONTENT B

### STD-B-REQ-019
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: 3.1 FORBIDDEN PHRASES - AUTOMATIC CLAIM INVALIDATION
- Source anchor: ## CONTENT B

### STD-B-REQ-020
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: MUST
- Requirement Text: ║   ❌ "auth required"          ❌ "out of scope"                               ║
- Source anchor: ## CONTENT B

### STD-B-REQ-021
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: ║   If you cannot produce evidence, you MUST say "UNPROVEN" and treat it as   ║
- Source anchor: ## CONTENT B

### STD-B-REQ-022
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.2 CORE ENFORCEMENT PRINCIPLES
- Source anchor: ## CONTENT B

### STD-B-REQ-023
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: MUST
- Requirement Text: ║   Must demonstrate controlled failure BEFORE claiming success               ║
- Source anchor: ## CONTENT B

### STD-B-REQ-024
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   HTTP 200 is NOT success.
- Source anchor: ## CONTENT B

### STD-B-REQ-025
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: Must validate content, schema, behavior.        ║
- Source anchor: ## CONTENT B

### STD-B-REQ-026
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: MUST
- Requirement Text: ║   Out-of-scope changes = IMMEDIATE rollback                                 ║
- Source anchor: ## CONTENT B

### STD-B-REQ-027
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   Must survive restart.
- Source anchor: ## CONTENT B

### STD-B-REQ-028
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: MUST
- Requirement Text: Must pass 3 consecutive runs.                      ║
- Source anchor: ## CONTENT B

### STD-B-REQ-029
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   PRINCIPLE 7: AUTOMATION ONLY                                               ║
- Source anchor: ## CONTENT B

### STD-B-REQ-030
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   Every verification must be scriptable.
- Source anchor: ## CONTENT B

### STD-B-REQ-031
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: No manual steps.                  ║
- Source anchor: ## CONTENT B

### STD-B-REQ-032
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: Every claim of "done" or "working" MUST include this EXACT format:
- Source anchor: ## CONTENT B

### STD-B-REQ-033
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║  - Matches found: [must be 0]                                               ║
- Source anchor: ## CONTENT B

### STD-B-REQ-034
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║  - Budget: [max allowed]                                                    ║
- Source anchor: ## CONTENT B

### STD-B-REQ-035
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: ║       - All required services are running                                   ║
- Source anchor: ## CONTENT B

### STD-B-REQ-036
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: MUST
- Requirement Text: ║   IF ANY ITEM FAILS → DO NOT PROCEED.
- Source anchor: ## CONTENT B

### STD-B-REQ-037
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: FIX IT FIRST.                         ║
- Source anchor: ## CONTENT B

### STD-B-REQ-038
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: echo "=== INVARIANT 1: Required Services ==="
- Source anchor: # INVARIANT 1: Required services running

### STD-B-REQ-039
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: REQUIRED_PORTS=([LIST_YOUR_REQUIRED_PORTS])
- Source anchor: # INVARIANT 1: Required services running

### STD-B-REQ-040
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: for port in "${REQUIRED_PORTS[@]}"; do
- Source anchor: # INVARIANT 1: Required services running

### STD-B-REQ-041
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: echo "" && echo "=== INVARIANT 2: Forbidden Services ==="
- Source anchor: # INVARIANT 2: Forbidden services NOT running

### STD-B-REQ-042
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: FORBIDDEN_PORTS=([LIST_FORBIDDEN_PORTS])
- Source anchor: # INVARIANT 2: Forbidden services NOT running

### STD-B-REQ-043
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: for port in "${FORBIDDEN_PORTS[@]}"; do
- Source anchor: # INVARIANT 2: Forbidden services NOT running

### STD-B-REQ-044
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: MUST
- Requirement Text: echo "❌ INVARIANT CHECK FAILED - DO NOT PROCEED"
- Source anchor: # Final verdict

### STD-B-REQ-045
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: ║   - If any: IMMEDIATE ROLLBACK REQUIRED                                     ║
- Source anchor: # Final verdict

### STD-B-REQ-046
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   - Rollback command: [exact command]                                       ║
- Source anchor: # Final verdict

### STD-B-REQ-047
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   - Rollback tested: [YES/NO]                                               ║
- Source anchor: # Final verdict

### STD-B-REQ-048
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: MUST
- Requirement Text: HARD RULE: Out-of-scope change = IMMEDIATE rollback.
- Source anchor: # Final verdict

### STD-B-REQ-049
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: No exceptions.
- Source anchor: # Final verdict

### STD-B-REQ-050
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: SECTION 8: GATE ENFORCEMENT
- Source anchor: # Final verdict

### STD-B-REQ-051
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║                    GATE ENFORCEMENT RULES                                     ║
- Source anchor: # Final verdict

### STD-B-REQ-052
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: MUST
- Requirement Text: ║   RULE 1: SEQUENTIAL - Gates must pass in order.
- Source anchor: # Final verdict

### STD-B-REQ-053
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: No skipping.               ║
- Source anchor: # Final verdict

### STD-B-REQ-054
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   RULE 2: FOCUS - If Gate N fails, only work on Gate N.
- Source anchor: # Final verdict

### STD-B-REQ-055
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: Nothing else.       ║
- Source anchor: # Final verdict

### STD-B-REQ-056
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   RULE 3: TWO-STRIKE ROLLBACK                                                ║
- Source anchor: # Final verdict

### STD-B-REQ-057
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   If same gate fails 2 consecutive times:                                   ║
- Source anchor: # Final verdict

### STD-B-REQ-058
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   2.
- Source anchor: # Final verdict

### STD-B-REQ-059
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ROLLBACK last change                                                   ║
- Source anchor: # Final verdict

### STD-B-REQ-060
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   6.
- Source anchor: # Final verdict

### STD-B-REQ-061
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: Only then retry                                                        ║
- Source anchor: # Final verdict

### STD-B-REQ-062
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   Must perform git bisect or manual bisection to isolate root cause.       ║
- Source anchor: # Final verdict

### STD-B-REQ-063
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: Gate Attempt Log Format
- Source anchor: # Final verdict

### STD-B-REQ-064
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║                    GATE ATTEMPT LOG                                           ║
- Source anchor: # Final verdict

### STD-B-REQ-065
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   GATE: [Gate name/number]                                                   ║
- Source anchor: # Final verdict

### STD-B-REQ-066
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   API endpoint response             │ 5s       │ GATE FAIL                   ║
- Source anchor: # Final verdict

### STD-B-REQ-067
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   Page initial load                 │ 10s      │ GATE FAIL                   ║
- Source anchor: # Final verdict

### STD-B-REQ-068
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   UI interaction response           │ 3s       │ GATE FAIL                   ║
- Source anchor: # Final verdict

### STD-B-REQ-069
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   Database query                    │ 2s       │ GATE FAIL                   ║
- Source anchor: # Final verdict

### STD-B-REQ-070
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   Service health check              │ 1s       │ GATE FAIL                   ║
- Source anchor: # Final verdict

### STD-B-REQ-071
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: ║   [ ] Evidence Block provided with all required fields                      ║
- Source anchor: # Final verdict

### STD-B-REQ-072
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   [ ] Only approved files modified (tree hash check)                        ║
- Source anchor: # Final verdict

### STD-B-REQ-073
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: SECTION 11: TASK-SPECIFIC GATES (CUSTOMIZE)
- Source anchor: # Final verdict

### STD-B-REQ-074
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║                    TASK GATES (CUSTOMIZE FOR YOUR TASK)                       ║
- Source anchor: # Final verdict

### STD-B-REQ-075
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   GATE 0: PRE-FLIGHT                                                         ║
- Source anchor: # Final verdict

### STD-B-REQ-076
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   GATE 1: [FIRST MILESTONE - customize]                                      ║
- Source anchor: # Final verdict

### STD-B-REQ-077
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   GATE 2: [SECOND MILESTONE - customize]                                     ║
- Source anchor: # Final verdict

### STD-B-REQ-078
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   [ADD MORE GATES AS NEEDED]                                                 ║
- Source anchor: # Final verdict

### STD-B-REQ-079
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   GATE FINAL: COMPLETION                                                     ║
- Source anchor: # Final verdict

### STD-B-REQ-080
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   [ ] All prior gates passed                                                ║
- Source anchor: # Final verdict

### STD-B-REQ-081
- Domain: Standard
- Variant: B
- Category: Logging
- Strength: IMPLIED
- Requirement Text: ║   RULE: Maintain append-only JSONL log of EVERY command run.                ║
- Source anchor: # Final verdict

### STD-B-REQ-082
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║     "gate": "gate_name",                                                    ║
- Source anchor: # Final verdict

### STD-B-REQ-083
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║     "why": "reason tied to gate requirement",                               ║
- Source anchor: # Final verdict

### STD-B-REQ-084
- Domain: Standard
- Variant: B
- Category: Logging
- Strength: MUST
- Requirement Text: ║   • Every command must be logged BEFORE execution                           ║
- Source anchor: # Final verdict

### STD-B-REQ-085
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: ║   • Output must be captured to file (not just displayed)                   ║
- Source anchor: # Final verdict

### STD-B-REQ-086
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: ║   • Ledger must be included in Completion Packet                           ║
- Source anchor: # Final verdict

### STD-B-REQ-087
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: ║   REQUIRED ARTIFACTS:                                                        ║
- Source anchor: # Final verdict

### STD-B-REQ-088
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: ║      [ ] One complete Evidence Block per gate passed                        ║
- Source anchor: # Final verdict

### STD-B-REQ-089
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: MUST
- Requirement Text: ║   Fresh clone + single command must reproduce the same passing results.     ║
- Source anchor: # Final verdict

### STD-B-REQ-090
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: IMPLIED
- Requirement Text: ║    • Scope integrity (only approved files changed)                         ║
- Source anchor: # Final verdict

### STD-B-REQ-091
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: ║    • Change manifest with rollback plan                                    ║
- Source anchor: # Final verdict

### STD-B-REQ-092
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   Gates are HARD STOPS.                                                      ║
- Source anchor: # Final verdict

### STD-B-REQ-093
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: MUST
- Requirement Text: ║   Out-of-scope = immediate rollback.                                        ║
- Source anchor: # Final verdict

### STD-B-REQ-094
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   Automation only (no manual steps).                                        ║
- Source anchor: # Final verdict

### STD-B-REQ-095
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: ║   Full completion packet required."                                         ║
- Source anchor: # Final verdict

### STD-B-REQ-096
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Task ID, title, problem, expected outcome, success criteria
- Source anchor: # Final verdict

### STD-B-REQ-097
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Approved files/directories
- Source anchor: # Final verdict

### STD-B-REQ-098
- Domain: Standard
- Variant: B
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - Out of scope items
- Source anchor: # Final verdict

### STD-B-REQ-099
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Dependencies and constraints
- Source anchor: # Final verdict

### STD-B-REQ-100
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: - Required ports/services
- Source anchor: # Final verdict

### STD-B-REQ-101
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: - Forbidden ports/services
- Source anchor: # Final verdict

### STD-B-REQ-102
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Environment checks
- Source anchor: # Final verdict

### STD-B-REQ-103
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Adjust limits for your task type
- Source anchor: # Final verdict

### STD-B-REQ-104
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: □ 5.
- Source anchor: # Final verdict

### STD-B-REQ-105
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: Fill in Section 11 (Task Gates)
- Source anchor: # Final verdict

### STD-B-REQ-106
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Define specific milestones for your task
- Source anchor: # Final verdict

### STD-B-REQ-107
- Domain: Standard
- Variant: B
- Category: Gates
- Strength: SHOULD
- Requirement Text: - Each gate should have clear pass/fail criteria
- Source anchor: # Final verdict

### STD-B-REQ-108
- Domain: Standard
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.0.0
- Source anchor: # Final verdict

### STD-B-REQ-109
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: Evidence Required
- Source anchor: # Final verdict

### STD-B-REQ-110
- Domain: Standard
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: Checksummed + Immediate Rollback
- Source anchor: # Final verdict

### STD-B-REQ-111
- Domain: Standard
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: Required (no manual steps)
- Source anchor: # Final verdict

### STD-B-REQ-112
- Domain: Standard
- Variant: B
- Category: Logging
- Strength: IMPLIED
- Requirement Text: JSONL append-only ledger
- Source anchor: # Final verdict

### STD-B-REQ-113
- Domain: Standard
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: NOT ALLOWED
- Source anchor: # Final verdict

### STD-C-REQ-001
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: You must follow this document **exactly**.
- Source anchor: # UNIVERSAL MISSION TEMPLATE — MANDATORY FIX / BUILD / INVESTIGATE (NO EXCUSES)

### STD-C-REQ-002
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - **No claim is true without proof.** If you cannot prove something with the required evidence, label it **UNPROVEN** and treat it as **NOT DONE**.
- Source anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE)

### STD-C-REQ-003
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - **No handwaving.** If you cannot show raw output, you do not get credit.
- Source anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE)

### STD-C-REQ-004
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - **No scope drift.** Only modify what is explicitly approved.
- Source anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE)

### STD-C-REQ-005
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: MUST
- Requirement Text: Any out-of-scope change triggers immediate rollback and mission invalidation for that attempt.
- Source anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE)

### STD-C-REQ-006
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: MUST
- Requirement Text: - **Hard stop gates.** If a gate fails, you do not proceed to later steps.
- Source anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE)

### STD-C-REQ-007
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: You must not use:
- Source anchor: ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED)

### STD-C-REQ-008
- Domain: Standard
- Variant: C
- Category: Other
- Strength: SHOULD
- Requirement Text: - “should work”, “likely”, “probably”, “seems”, “might”, “maybe”
- Source anchor: ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED)

### STD-C-REQ-009
- Domain: Standard
- Variant: C
- Category: Repro
- Strength: OPTIONAL
- Requirement Text: - “works for me”, “can’t reproduce”, “it’s fine”, “looks good”
- Source anchor: ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED)

### STD-C-REQ-010
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - “done” / “fixed” without the required Evidence Block
- Source anchor: ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED)

### STD-C-REQ-011
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: If you must express uncertainty, use: **UNPROVEN** + what evidence is missing.
- Source anchor: ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED)

### STD-C-REQ-012
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: Every response must contain these sections in this order:
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-013
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-014
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **MISSION STATE**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-015
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-016
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **SCOPE & CHANGE MANIFEST**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-017
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-018
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **PHASE 0 — BASELINE / GROUND TRUTH**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-019
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-020
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **HYPOTHESIS (SINGLE, FALSIFIABLE)**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-021
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 5.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-022
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **PLAN (NEXT COMMANDS ONLY)**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-023
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 6.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-024
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **EVIDENCE BLOCKS (RAW OUTPUT)**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-025
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 7.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-026
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: **GATE RESULT (PASS/FAIL)**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-027
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 8.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-028
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **ROLLBACK STATUS**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-029
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 9.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-030
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **NEXT ACTION**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE)

### STD-C-REQ-031
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Repo root: {{REPO_ROOT}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-032
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Runtime: {{docker/systemd/node/python/etc}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-033
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Critical services/ports: {{PORTS_AND_SERVICES}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-034
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Primary datastore(s): {{DBS_AND_TABLES}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-035
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: - Known legacy / forbidden services: {{FORBIDDEN_PORTS_OR_SERVICES}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-036
- Domain: Standard
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Observability locations (logs/metrics): {{LOG_PATHS_DASHBOARDS}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-037
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: **Acceptance Criteria (must be testable):**
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-038
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - {{AC_1}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-039
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - {{AC_2}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-040
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - {{AC_3}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-041
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: OPTIONAL
- Requirement Text: **Approved Scope (ONLY these files/dirs may change this phase):**
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-042
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - {{APPROVED_SCOPE_LIST}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-043
- Domain: Standard
- Variant: C
- Category: Performance
- Strength: IMPLIED
- Requirement Text: - Endpoint max latency: {{MAX_ENDPOINT_SECONDS}} seconds
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-044
- Domain: Standard
- Variant: C
- Category: UI
- Strength: IMPLIED
- Requirement Text: - UI interaction max time: {{MAX_UI_SECONDS}} seconds
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-045
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - {{ERROR_STRING_1}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-046
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - {{ERROR_STRING_2}}
- Source anchor: ## 3) MISSION INPUTS (FILL THESE IN)

### STD-C-REQ-047
- Domain: Standard
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: Maintain an **append-only JSONL ledger** of every command you run:
- Source anchor: ## 4) CHAIN OF CUSTODY (MANDATORY COMMAND LEDGER)

### STD-C-REQ-048
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - timestamp, cwd, command, why, and pointer to raw output artifact file.
- Source anchor: ## 4) CHAIN OF CUSTODY (MANDATORY COMMAND LEDGER)

### STD-C-REQ-049
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Produce a deterministic checksum of:
- Source anchor: ## 5) CODE INTEGRITY (CHECKSUM RULES)

### STD-C-REQ-050
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: MUST
- Requirement Text: If any out-of-scope file hash changes: **IMMEDIATE SELF-ROLLBACK**.
- Source anchor: ## 5) CODE INTEGRITY (CHECKSUM RULES)

### STD-C-REQ-051
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: For every critical service check you must prove:
- Source anchor: ## 6) SERVICE IDENTITY (ANTI-FAKE / ANTI-WRONG-PORT)

### STD-C-REQ-052
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - port → PID → PPID → executable path → **SHA256 of executable**
- Source anchor: ## 6) SERVICE IDENTITY (ANTI-FAKE / ANTI-WRONG-PORT)

### STD-C-REQ-053
- Domain: Standard
- Variant: C
- Category: UI
- Strength: IMPLIED
- Requirement Text: - build identity: **git commit SHA** and **container image digest** (if containerized)
- Source anchor: ## 6) SERVICE IDENTITY (ANTI-FAKE / ANTI-WRONG-PORT)

### STD-C-REQ-054
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: Every “success” claim must include **Dual-Channel Proof**:
- Source anchor: ## 7) PROOF STANDARD (HARD TO FAKE)

### STD-C-REQ-055
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Channel A: Browser/Playwright (HAR + console)
- Source anchor: ## 7) PROOF STANDARD (HARD TO FAKE)

### STD-C-REQ-056
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Channel B: Direct system truth (DB query / curl / logs / process identity / checksum)
- Source anchor: ## 7) PROOF STANDARD (HARD TO FAKE)

### STD-C-REQ-057
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: Artifacts must be checksummed with SHA256 and listed in an **Evidence Manifest**.
- Source anchor: ## 7) PROOF STANDARD (HARD TO FAKE)

### STD-C-REQ-058
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - If output > {{MAX_INLINE_LINES}} lines, redirect to a file and attach it as an artifact.
- Source anchor: ## 7) PROOF STANDARD (HARD TO FAKE)

### STD-C-REQ-059
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: A UI gate passes only if all are true:
- Source anchor: ## 8) UI / NETWORK STRICTNESS

### STD-C-REQ-060
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - **Zero relevant console errors AND zero relevant warnings** (network/fetch/CORS/hydration).
- Source anchor: ## 8) UI / NETWORK STRICTNESS

### STD-C-REQ-061
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - HAR shows: no 4xx/5xx, no retry storms, no hung long-polls beyond threshold.
- Source anchor: ## 8) UI / NETWORK STRICTNESS

### STD-C-REQ-062
- Domain: Standard
- Variant: C
- Category: UI
- Strength: IMPLIED
- Requirement Text: - The interaction is **real**: click → network request → response → UI updates.
- Source anchor: ## 8) UI / NETWORK STRICTNESS

### STD-C-REQ-063
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: - At least one interaction must **mutate persisted state** (if applicable) and be verified by DB/system query.
- Source anchor: ## 8) UI / NETWORK STRICTNESS

### STD-C-REQ-064
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Repeat verification in **Incognito**, after clearing site data, with hard reload.
- Source anchor: ## 8) UI / NETWORK STRICTNESS

### STD-C-REQ-065
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: - Cached/SW responses do not count.
- Source anchor: ## 8) UI / NETWORK STRICTNESS

### STD-C-REQ-066
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: After the fix, you must prove the signature error strings are absent:
- Source anchor: ## 9) NEGATIVE PROOF (“PROOF OF ABSENCE”)

### STD-C-REQ-067
- Domain: Standard
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Show that the string is mathematically absent from the last **N ≥ 1000** relevant log lines.
- Source anchor: ## 9) NEGATIVE PROOF (“PROOF OF ABSENCE”)

### STD-C-REQ-068
- Domain: Standard
- Variant: C
- Category: UI
- Strength: MUST
- Requirement Text: Working UI is not enough; **the error must be gone**.
- Source anchor: ## 9) NEGATIVE PROOF (“PROOF OF ABSENCE”)

### STD-C-REQ-069
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: MUST
- Requirement Text: Every gate must pass:
- Source anchor: ## 10) RELIABILITY (WORKS-ONCE IS FAILURE)

### STD-C-REQ-070
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: MUST
- Requirement Text: And must pass **3 consecutive runs**.
- Source anchor: ## 10) RELIABILITY (WORKS-ONCE IS FAILURE)

### STD-C-REQ-071
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: - Re-run the fix steps; second run must produce **0 net changes**.
- Source anchor: ## 10) RELIABILITY (WORKS-ONCE IS FAILURE)

### STD-C-REQ-072
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: Each attempt must include exactly **one** falsifiable hypothesis and the test that disproves it.
- Source anchor: ## 11) TROUBLESHOOTING DISCIPLINE

### STD-C-REQ-073
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Perform **bisection** (git bisect or manual) until the precise offending change is isolated.
- Source anchor: ## 11) TROUBLESHOOTING DISCIPLINE

### STD-C-REQ-074
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: Any SSOT breach (e.g., forbidden port listening, legacy service running) triggers **immediate rollback + re-baseline**.
- Source anchor: ## 11) TROUBLESHOOTING DISCIPLINE

### STD-C-REQ-075
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - Mutation test: deliberately break a route/config and prove tests fail.
- Source anchor: ## 12) COURTROOM-GRADE TESTS (IF APPLICABLE)

### STD-C-REQ-076
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Schema enforcement: validate responses against JSON Schema.
- Source anchor: ## 12) COURTROOM-GRADE TESTS (IF APPLICABLE)

### STD-C-REQ-077
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: - Proxy contract tests: each `/api/*` must call intended upstream host/path and reject others.
- Source anchor: ## 12) COURTROOM-GRADE TESTS (IF APPLICABLE)

### STD-C-REQ-078
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: Each Evidence Block must include a System Health Snapshot for involved PIDs:
- Source anchor: ## 13) RESOURCE SAFETY (COLLATERAL DAMAGE WATCHDOGS)

### STD-C-REQ-079
- Domain: Standard
- Variant: C
- Category: Performance
- Strength: IMPLIED
- Requirement Text: - CPU%, RSS, FD count (if available), and a top/pidstat excerpt.
- Source anchor: ## 13) RESOURCE SAFETY (COLLATERAL DAMAGE WATCHDOGS)

### STD-C-REQ-080
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: Mission is only complete if you provide:
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-081
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Evidence Manifest (SHA256 for every artifact)
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-082
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - HAR(s), console capture(s), screenshots
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-083
- Domain: Standard
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Raw logs (as files), DB query outputs
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-084
- Domain: Standard
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Command ledger JSONL
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-085
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Pre/post checksum reports
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-086
- Domain: Standard
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - E2E run outputs (if used)
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-087
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - A fresh-clone reproducibility instruction: **one command** that regenerates the evidence or fails deterministically
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-088
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - “No green until red” demonstration (if applicable): controlled failure → restore → pass
- Source anchor: ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE)

### STD-C-REQ-089
- Domain: Standard
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: (You must fill this out first.)
- Source anchor: ## 1. MISSION STATE

### STD-C-REQ-090
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - Approved scope: {{APPROVED_SCOPE_LIST}}
- Source anchor: ## 2. SCOPE & CHANGE MANIFEST

### STD-C-REQ-091
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - Prohibited: Anything else.
- Source anchor: ## 2. SCOPE & CHANGE MANIFEST

### STD-C-REQ-092
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - Pre-change checksums: (required)
- Source anchor: ## 2. SCOPE & CHANGE MANIFEST

### STD-C-REQ-093
- Domain: Standard
- Variant: C
- Category: Scope
- Strength: MUST
- Requirement Text: - Authorized commands list: (required)
- Source anchor: ## 2. SCOPE & CHANGE MANIFEST

### STD-C-REQ-094
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: Gate verdict with evidence references.
- Source anchor: ## 7. GATE RESULT (PASS/FAIL)

### STD-C-REQ-095
- Domain: Standard
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: If failed, rollback steps + evidence.
- Source anchor: ## 8. ROLLBACK STATUS

### STD-C-REQ-096
- Domain: Standard
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: Either proceed to next gate or stop-the-line.
- Source anchor: ## 9. NEXT ACTION

### QA-A-REQ-001
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: | **Constraints** | READ-ONLY UNTIL HYPOTHESIS VALIDATED |
- Source anchor: ## PROTOCOL: ZERO TRUST | FORENSIC RIGOR | NO EXCUSES

### QA-A-REQ-002
- Domain: QA
- Variant: A
- Category: Gates
- Strength: MUST
- Requirement Text: **⛔ VIOLATION OF ANY RULE BELOW = IMMEDIATE MISSION FAILURE ⛔**
- Source anchor: # SECTION A: THE "IMMUTABLE" CONSTITUTION

### QA-A-REQ-003
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: The following phrases indicate uncertainty/laziness and are **FORBIDDEN**:
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### QA-A-REQ-004
- Domain: QA
- Variant: A
- Category: Other
- Strength: SHOULD
- Requirement Text: * ❌ "should work", "probably", "likely", "might"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### QA-A-REQ-005
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * ❌ "I think", "I believe", "theoretically"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### QA-A-REQ-006
- Domain: QA
- Variant: A
- Category: Repro
- Strength: OPTIONAL
- Requirement Text: * ❌ "works for me", "can't reproduce", "local issue"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### QA-A-REQ-007
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * ❌ "acceptable trade-off", "minor bug"
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### QA-A-REQ-008
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: * ❌ "done" (without evidence), "fixed" (without proof)
- Source anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES)

### QA-A-REQ-009
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: Every action that modifies state or code must include:
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-010
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-011
- Domain: QA
- Variant: A
- Category: Repro
- Strength: IMPLIED
- Requirement Text: **The Command:** Exact, reproducible command run.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-012
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-013
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **The Raw Output:** Unedited, non-truncated stdout/stderr.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-014
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-015
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **The State Verification:** Proof that the system state changed (DB query, file hash, API response).
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-016
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-017
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **The Negative Test:** Proof that the test fails when the fix is removed (Red -> Green).
- Source anchor: ## A.2 THE UNIVERSAL EVIDENCE STANDARD

### QA-A-REQ-018
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: * **No New Patterns:** You must use existing design patterns found in the codebase.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### QA-A-REQ-019
- Domain: QA
- Variant: A
- Category: Scope
- Strength: MUST
- Requirement Text: Do not introduce new frameworks or libraries unless explicitly authorized.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### QA-A-REQ-020
- Domain: QA
- Variant: A
- Category: Scope
- Strength: OPTIONAL
- Requirement Text: * **Scope Locking:** You may only modify files within `{{AUTHORIZED_SCOPE}}`.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### QA-A-REQ-021
- Domain: QA
- Variant: A
- Category: Scope
- Strength: MUST
- Requirement Text: Modifying files outside this scope triggers an **Immediate Rollback**.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### QA-A-REQ-022
- Domain: QA
- Variant: A
- Category: UI
- Strength: IMPLIED
- Requirement Text: * **Dependency Freeze:** No `npm install`, `pip install`, or `apt-get` allowed unless the `package.json`/`requirements.txt` is the explicit target of the task.
- Source anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW)

### QA-A-REQ-023
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Symptom:** {{CURRENT_SYMPTOM_DESCRIPTION}}
- Source anchor: ## B.1 THE STARTING STATE

### QA-A-REQ-024
- Domain: QA
- Variant: A
- Category: Repro
- Strength: IMPLIED
- Requirement Text: * **Reproduction Path:** `{{REPRODUCTION_COMMAND}}`
- Source anchor: ## B.1 THE STARTING STATE

### QA-A-REQ-025
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Error Signature:** `{{EXACT_ERROR_MESSAGE}}`
- Source anchor: ## B.1 THE STARTING STATE

### QA-A-REQ-026
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: The mission is ONLY complete when **ALL** of the following are true:
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-027
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-028
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: [ ] The specific symptom in B.1 is resolved.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-029
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-030
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: [ ] **Proof of Absence:** The "Error Signature" no longer appears in logs.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-031
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-032
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: [ ] **Regression Check:** `{{CRITICAL_FUNCTION}}` still works.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-033
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-034
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: [ ] **Forensic Packet:** A JSONL ledger of all commands is delivered.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-035
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 5.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-036
- Domain: QA
- Variant: A
- Category: Repro
- Strength: IMPLIED
- Requirement Text: [ ] **Fresh Clone Test:** The solution works on a fresh environment.
- Source anchor: ## B.2 THE DEFINITION OF DONE (DOD)

### QA-A-REQ-037
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: **YOU MUST FOLLOW THIS LOOP RECURSIVELY.
- Source anchor: # SECTION C: EXECUTION PROTOCOL (THE LOOP)

### QA-A-REQ-038
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: DO NOT SKIP STEPS.**
- Source anchor: # SECTION C: EXECUTION PROTOCOL (THE LOOP)

### QA-A-REQ-039
- Domain: QA
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: * **Allowed:** `cat`, `grep`, `ls`, `curl (GET)`, `ps`, `logs`.
- Source anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY)

### QA-A-REQ-040
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: * **Forbidden:** Editors, `sed`, `curl (POST/PUT/DELETE)`, `restart`.
- Source anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY)

### QA-A-REQ-041
- Domain: QA
- Variant: A
- Category: UI
- Strength: IMPLIED
- Requirement Text: * **Requirement:** Identify the `PID`, `File Path`, and `Line Number` of the fault.
- Source anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY)

### QA-A-REQ-042
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Format:**
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### QA-A-REQ-043
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Hypothesis:** "The issue is caused by X because Y."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### QA-A-REQ-044
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Proposed Fix:** "I will change line N in file Z."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### QA-A-REQ-045
- Domain: QA
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: * **Simulation:** "If I run this, I expect log stream A to stop showing error B."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### QA-A-REQ-046
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Risk:** "This might break feature C."
- Source anchor: ## PHASE 2: HYPOTHESIS & SIMULATION

### QA-A-REQ-047
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: * **Pre-Flight:** Hash the file before editing (`sha256sum`).
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### QA-A-REQ-048
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Action:** Apply the edit.
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### QA-A-REQ-049
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Post-Flight:** Hash the file after editing.
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### QA-A-REQ-050
- Domain: QA
- Variant: A
- Category: Repro
- Strength: MUST
- Requirement Text: * **Verify:** Run the reproduction command immediately.
- Source anchor: ## PHASE 3: SURGICAL INTERVENTION

### QA-A-REQ-051
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### QA-A-REQ-052
- Domain: QA
- Variant: A
- Category: Negative Proof
- Strength: IMPLIED
- Requirement Text: **Show Green:** Show the system working.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### QA-A-REQ-053
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### QA-A-REQ-054
- Domain: QA
- Variant: A
- Category: Gates
- Strength: IMPLIED
- Requirement Text: **Force Red:** Revert the change (or break it intentionally) and prove it fails again.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### QA-A-REQ-055
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### QA-A-REQ-056
- Domain: QA
- Variant: A
- Category: Negative Proof
- Strength: IMPLIED
- Requirement Text: **Return to Green:** Re-apply the fix and confirm success.
- Source anchor: ## PHASE 4: THE "RED-TO-GREEN" PROOF

### QA-A-REQ-057
- Domain: QA
- Variant: A
- Category: Evidence
- Strength: MUST
- Requirement Text: At the end of the mission, you must generate a **COMPLETION PACKET** containing:
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-058
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-059
- Domain: QA
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: **`ledger.jsonl`**: Every command executed, timestamped.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-060
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-061
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: **`diff.patch`**: The exact code changes.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-062
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-063
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: **`verification_script.sh`**: A single script that:
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-064
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * Checks the fix.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-065
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * Checks for regressions.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-066
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * Returns `0` only if PERFECTION is achieved.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-067
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-068
- Domain: QA
- Variant: A
- Category: Performance
- Strength: IMPLIED
- Requirement Text: **`resource_snapshot.txt`**: CPU/Memory usage before vs.
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-069
- Domain: QA
- Variant: A
- Category: Performance
- Strength: MUST
- Requirement Text: after (Must be within 15% variance).
- Source anchor: # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES)

### QA-A-REQ-070
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Target Files:** `{{TARGET_FILES}}`
- Source anchor: # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK

### QA-A-REQ-071
- Domain: QA
- Variant: A
- Category: Logging
- Strength: IMPLIED
- Requirement Text: * **Relevant Logs:** `{{LOG_PATH}}`
- Source anchor: # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK

### QA-A-REQ-072
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: * **Test Command:** `{{TEST_COMMAND}}`
- Source anchor: # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK

### QA-A-REQ-073
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: **You are a Senior Principal Engineer.
- Source anchor: # FINAL WARNING

### QA-A-REQ-074
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: You do not guess.
- Source anchor: # FINAL WARNING

### QA-A-REQ-075
- Domain: QA
- Variant: A
- Category: Other
- Strength: MUST
- Requirement Text: You do not "try" things.
- Source anchor: # FINAL WARNING

### QA-A-REQ-076
- Domain: QA
- Variant: A
- Category: Other
- Strength: IMPLIED
- Requirement Text: You measure, you analyze, you execute, and you prove.**
- Source anchor: # FINAL WARNING

### QA-B-REQ-001
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   incomplete deliverable.
- Source anchor: ## CONTENT B

### QA-B-REQ-002
- Domain: QA
- Variant: B
- Category: UI
- Strength: IMPLIED
- Requirement Text: The Builder WANTS to fool you.
- Source anchor: ## CONTENT B

### QA-B-REQ-003
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: Don't let them.    ║
- Source anchor: ## CONTENT B

### QA-B-REQ-004
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.1 ZERO TRUST PRINCIPLES
- Source anchor: ## CONTENT B

### QA-B-REQ-005
- Domain: QA
- Variant: B
- Category: UI
- Strength: IMPLIED
- Requirement Text: ║   RULE 1: NEVER TRUST BUILDER CLAIMS                                         ║
- Source anchor: ## CONTENT B

### QA-B-REQ-006
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   • YOU must run every verification command yourself                        ║
- Source anchor: ## CONTENT B

### QA-B-REQ-007
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   • YOU must check every file exists and has correct content                ║
- Source anchor: ## CONTENT B

### QA-B-REQ-008
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   • YOU must test every endpoint/feature independently                      ║
- Source anchor: ## CONTENT B

### QA-B-REQ-009
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   • YOU must query the database directly to verify state                    ║
- Source anchor: ## CONTENT B

### QA-B-REQ-010
- Domain: QA
- Variant: B
- Category: UI
- Strength: OPTIONAL
- Requirement Text: ║   • Builder may have modified only the test, not the actual code           ║
- Source anchor: ## CONTENT B

### QA-B-REQ-011
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: IMPLIED
- Requirement Text: 1.2 RED FLAGS TO LOOK FOR
- Source anchor: ## CONTENT B

### QA-B-REQ-012
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   • File timestamps don't match claimed work timeline                       ║
- Source anchor: ## CONTENT B

### QA-B-REQ-013
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   • File imports don't match actual dependencies                           ║
- Source anchor: ## CONTENT B

### QA-B-REQ-014
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   • File has syntax errors (never actually ran)                            ║
- Source anchor: ## CONTENT B

### QA-B-REQ-015
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   • Output references files/paths that don't exist                         ║
- Source anchor: ## CONTENT B

### QA-B-REQ-016
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   • Fix only works for specific test case shown                            ║
- Source anchor: ## CONTENT B

### QA-B-REQ-017
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   • Fix only works because of cached state                                 ║
- Source anchor: ## CONTENT B

### QA-B-REQ-018
- Domain: QA
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: ║   • Evidence block missing required fields                                 ║
- Source anchor: ## CONTENT B

### QA-B-REQ-019
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   • Hashes don't match actual file contents                               ║
- Source anchor: ## CONTENT B

### QA-B-REQ-020
- Domain: QA
- Variant: B
- Category: UI
- Strength: IMPLIED
- Requirement Text: 2.1 AUDIT PHASE 0: COLLECT BUILDER CLAIMS
- Source anchor: ## CONTENT B

### QA-B-REQ-021
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   4.
- Source anchor: ## CONTENT B

### QA-B-REQ-022
- Domain: QA
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: CLAIMED GATES PASSED:                                                   ║
- Source anchor: ## CONTENT B

### QA-B-REQ-023
- Domain: QA
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║      [ ] List every gate they claim to have passed                          ║
- Source anchor: ## CONTENT B

### QA-B-REQ-024
- Domain: QA
- Variant: B
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: 2.2 AUDIT PHASE 1: ARTIFACT EXISTENCE VERIFICATION
- Source anchor: ## CONTENT B

### QA-B-REQ-025
- Domain: QA
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: echo "❌ NO MANIFEST FILE - Builder didn't create required manifest"
- Source anchor: # Verify each file in manifest actually exists

### QA-B-REQ-026
- Domain: QA
- Variant: B
- Category: Evidence
- Strength: MUST
- Requirement Text: echo "❌ NO COMPLETION PACKET - Builder didn't create required directory"
- Source anchor: # Verify each file in manifest actually exists

### QA-B-REQ-027
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.3 AUDIT PHASE 2: INDEPENDENT FUNCTIONAL VERIFICATION
- Source anchor: # Verify each file in manifest actually exists

### QA-B-REQ-028
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: Test EVERYTHING yourself.
- Source anchor: # Verify each file in manifest actually exists

### QA-B-REQ-029
- Domain: QA
- Variant: B
- Category: UI
- Strength: IMPLIED
- Requirement Text: Don't trust Builder's outputs.
- Source anchor: # Verify each file in manifest actually exists

### QA-B-REQ-030
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: REQUIRED_PORTS=([LIST_REQUIRED_PORTS])
- Source anchor: # CUSTOMIZE THESE PORTS FOR YOUR TASK

### QA-B-REQ-031
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: for port in "${REQUIRED_PORTS[@]}"; do
- Source anchor: # CUSTOMIZE THESE PORTS FOR YOUR TASK

### QA-B-REQ-032
- Domain: QA
- Variant: B
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: 2.4 AUDIT PHASE 3: EVIDENCE BLOCK VALIDATION
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-033
- Domain: QA
- Variant: B
- Category: Scope
- Strength: IMPLIED
- Requirement Text: 2.5 AUDIT PHASE 4: SCOPE VIOLATION CHECK
- Source anchor: # fi

### QA-B-REQ-034
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: CHANGED_FILES=$(cd "$SOURCE_DIR" && git diff --name-only HEAD~10 2>/dev/null)
- Source anchor: # Use git if available

### QA-B-REQ-035
- Domain: QA
- Variant: B
- Category: Logging
- Strength: IMPLIED
- Requirement Text: 2.6 AUDIT PHASE 5: FORENSIC LEDGER VERIFICATION
- Source anchor: # Further investigation needed

### QA-B-REQ-036
- Domain: QA
- Variant: B
- Category: Logging
- Strength: MUST
- Requirement Text: echo "   Builder did not maintain required command log!"
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-037
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: echo "=== CHECKING REQUIRED FIELDS ==="
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-038
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: REQUIRED_FIELDS=("ts" "phase" "cmd" "why")
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-039
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: for field in "${REQUIRED_FIELDS[@]}"; do
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-040
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.7 AUDIT PHASE 6: ACCEPTANCE CRITERIA VERIFICATION
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-041
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   • EVERY criterion must be independently verified                          ║
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-042
- Domain: QA
- Variant: B
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: ║   • Don't just accept Builder's evidence - generate your own               ║
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-043
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.8 AUDIT PHASE 7: PERSISTENCE & STABILITY VERIFICATION
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-044
- Domain: QA
- Variant: B
- Category: Other
- Strength: OPTIONAL
- Requirement Text: 2.9 AUDIT PHASE 8: ATTACK SURFACE SCAN
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-045
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: echo "=== CHECK 1: FORBIDDEN LISTENERS ==="
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-046
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: FORBIDDEN_PORTS=([LIST_FORBIDDEN_PORTS])  # e.g., legacy port 8090
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-047
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: for port in "${FORBIDDEN_PORTS[@]}"; do
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-048
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: echo "🚨 FORBIDDEN PORT $port HAS A LISTENER!"
- Source anchor: # ─────────────────────────────────────────────────────────────────────────────

### QA-B-REQ-049
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   MAJOR ISSUES (must be addressed):                                          ║
- Source anchor: # List all listening ports and check for unexpected ones

### QA-B-REQ-050
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   █   [If REJECTED: List specific items that must be fixed]             █   ║
- Source anchor: # List all listening ports and check for unexpected ones

### QA-B-REQ-051
- Domain: QA
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: ║   [ ] Listed all claimed gates passed                                       ║
- Source anchor: # List all listening ports and check for unexpected ones

### QA-B-REQ-052
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   [ ] Only approved files were modified                                     ║
- Source anchor: # List all listening ports and check for unexpected ones

### QA-B-REQ-053
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: ║   [ ] Required fields present                                               ║
- Source anchor: # List all listening ports and check for unexpected ones

### QA-B-REQ-054
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: ║   [ ] No forbidden listeners                                                ║
- Source anchor: # List all listening ports and check for unexpected ones

### QA-B-REQ-055
- Domain: QA
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - Phases Passed: $PASSED_PHASES / $TOTAL_PHASES
- Source anchor: ## Final Verdict

### QA-B-REQ-056
- Domain: QA
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - Phases Failed: $FAILED_PHASES / $TOTAL_PHASES
- Source anchor: ## Final Verdict

### QA-B-REQ-057
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   2.
- Source anchor: ## Final Verdict

### QA-B-REQ-058
- Domain: QA
- Variant: B
- Category: UI
- Strength: IMPLIED
- Requirement Text: The Builder WANTS you to approve their work.
- Source anchor: ## Final Verdict

### QA-B-REQ-059
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: Don't make it easy.       ║
- Source anchor: ## Final Verdict

### QA-B-REQ-060
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   3.
- Source anchor: ## Final Verdict

### QA-B-REQ-061
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: NEVER trust screenshots, outputs, or claims.
- Source anchor: ## Final Verdict

### QA-B-REQ-062
- Domain: QA
- Variant: B
- Category: Repro
- Strength: IMPLIED
- Requirement Text: Reproduce EVERYTHING.     ║
- Source anchor: ## Final Verdict

### QA-B-REQ-063
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║   4.
- Source anchor: ## Final Verdict

### QA-B-REQ-064
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: If something seems suspicious, it probably is.
- Source anchor: ## Final Verdict

### QA-B-REQ-065
- Domain: QA
- Variant: B
- Category: Gates
- Strength: IMPLIED
- Requirement Text: Investigate.            ║
- Source anchor: ## Final Verdict

### QA-B-REQ-066
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: ║      Only approve if YOU would stake your reputation on it.                 ║
- Source anchor: ## Final Verdict

### QA-B-REQ-067
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.0.0
- Source anchor: ## Final Verdict

### QA-B-REQ-068
- Domain: QA
- Variant: B
- Category: Negative Proof
- Strength: MUST
- Requirement Text: Independent reproduction required
- Source anchor: ## Final Verdict

### QA-B-REQ-069
- Domain: QA
- Variant: B
- Category: Other
- Strength: IMPLIED
- Requirement Text: APPROVED / REJECTED only
- Source anchor: ## Final Verdict

### QA-B-REQ-070
- Domain: QA
- Variant: B
- Category: Other
- Strength: MUST
- Requirement Text: NOT ALLOWED
- Source anchor: ## Final Verdict

### QA-C-REQ-001
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: You must be adversarial, skeptical, and evidence-driven.
- Source anchor: # POST-MISSION QA / FORENSIC AUDIT PROMPT (NO EXCUSES)

### QA-C-REQ-002
- Domain: QA
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: If anything is missing, inconsistent, or unverifiable, mark it as **FAIL**.
- Source anchor: # POST-MISSION QA / FORENSIC AUDIT PROMPT (NO EXCUSES)

### QA-C-REQ-003
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Evidence manifest: {{EVIDENCE_MANIFEST_CONTENT}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-004
- Domain: QA
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Command ledger JSONL: {{COMMAND_LEDGER_JSONL}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-005
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - HAR(s): {{HAR_LIST}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-006
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Console captures: {{CONSOLE_LIST}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-007
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Screenshots: {{SCREENSHOT_LIST}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-008
- Domain: QA
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Logs (files): {{LOG_FILES_LIST}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-009
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - DB outputs: {{DB_OUTPUTS_LIST}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-010
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Pre/post checksum reports: {{CHECKSUM_REPORTS_LIST}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-011
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - E2E outputs: {{E2E_OUTPUTS_LIST}}
- Source anchor: ### C) The agent’s Completion Packet artifacts (paste file names + hashes + paths)

### QA-C-REQ-012
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Repo root: {{REPO_ROOT}}
- Source anchor: ### D) Environment facts (if known)

### QA-C-REQ-013
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Hostname / runtime: {{RUNTIME}}
- Source anchor: ### D) Environment facts (if known)

### QA-C-REQ-014
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Critical ports/services: {{PORTS}}
- Source anchor: ### D) Environment facts (if known)

### QA-C-REQ-015
- Domain: QA
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: - Forbidden ports/services: {{FORBIDDEN_PORTS}}
- Source anchor: ### D) Environment facts (if known)

### QA-C-REQ-016
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Datastores: {{DBS}}
- Source anchor: ### D) Environment facts (if known)

### QA-C-REQ-017
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Acceptance criteria: {{AC_LIST}}
- Source anchor: ### D) Environment facts (if known)

### QA-C-REQ-018
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - You must not accept any paraphrase as proof.
- Source anchor: ## 1) AUDITOR PRIME DIRECTIVE

### QA-C-REQ-019
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - You must reject any “claim” that lacks a matching Evidence Block.
- Source anchor: ## 1) AUDITOR PRIME DIRECTIVE

### QA-C-REQ-020
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: OPTIONAL
- Requirement Text: - If you cannot validate an artifact, mark it **UNVERIFIABLE** → which is **FAIL** unless the missing proof is non-essential.
- Source anchor: ## 1) AUDITOR PRIME DIRECTIVE

### QA-C-REQ-021
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - Any fabricated evidence = **AUTO-FAIL**.
- Source anchor: ## 1) AUDITOR PRIME DIRECTIVE

### QA-C-REQ-022
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 1.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-023
- Domain: QA
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: **AUDIT VERDICT** (PASS / FAIL / UNPROVEN)
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-024
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 2.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-025
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **TOP 10 FINDINGS** (ranked by severity)
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-026
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 3.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-027
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **EVIDENCE CONSISTENCY CHECKS**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-028
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 4.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-029
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: **ARTIFACT AUTHENTICITY CHECKS**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-030
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 5.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-031
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **INSTRUCTION COMPLIANCE MATRIX**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-032
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 6.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-033
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: **FIX VALIDATION MATRIX** (per acceptance criterion)
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-034
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 7.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-035
- Domain: QA
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: **SCOPE & INTEGRITY CHECKS**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-036
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 8.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-037
- Domain: QA
- Variant: C
- Category: Repro
- Strength: IMPLIED
- Requirement Text: **REPRODUCIBILITY CHECK**
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-038
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: 9.
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-039
- Domain: QA
- Variant: C
- Category: Gates
- Strength: MUST
- Requirement Text: **REQUIRED REMEDIATIONS** (if not PASS)
- Source anchor: ## 2) REQUIRED OUTPUT FORMAT (DO NOT DEVIATE)

### QA-C-REQ-040
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Verify every artifact listed in the evidence manifest:
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-041
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - has a SHA256 entry,
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-042
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - is referenced somewhere in the transcript,
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-043
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - and is consistent with the claim it supports.
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-044
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Flag:
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-045
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - missing hashes,
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-046
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - hashes without artifacts,
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-047
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - artifacts without hashes,
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-048
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - artifacts referenced but not provided.
- Source anchor: ### 3.1 Evidence Manifest Integrity

### QA-C-REQ-049
- Domain: QA
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Parse the JSONL ledger and confirm:
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-050
- Domain: QA
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - every command in the transcript appears in the ledger,
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-051
- Domain: QA
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - every ledger entry appears in transcript context,
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-052
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - commands match the “authorized commands list” from the Change Manifest (if provided),
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-053
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - timestamps are monotonically increasing (no time travel),
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-054
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - cwd paths are plausible.
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-055
- Domain: QA
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - Any unlogged command = **FAIL**.
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-056
- Domain: QA
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - Any unauthorized command = **FAIL**.
- Source anchor: ### 3.2 Command Ledger Cross-Check (Chain of Custody)

### QA-C-REQ-057
- Domain: QA
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: You must attempt to detect fabrication by checking:
- Source anchor: ### 3.3 “Fake File / Fake Output” Detection

### QA-C-REQ-058
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Evidence blocks that show outputs that look templated or too “clean”
- Source anchor: ### 3.3 “Fake File / Fake Output” Detection

### QA-C-REQ-059
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Outputs that contradict environment reality (e.g., impossible PIDs, inconsistent port bindings)
- Source anchor: ### 3.3 “Fake File / Fake Output” Detection

### QA-C-REQ-060
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Reused outputs across different commands (copy/paste patterns)
- Source anchor: ### 3.3 “Fake File / Fake Output” Detection

### QA-C-REQ-061
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - Missing raw outputs where they are required
- Source anchor: ### 3.3 “Fake File / Fake Output” Detection

### QA-C-REQ-062
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - **AUTHENTIC-LIKELY**, **SUSPICIOUS**, or **UNVERIFIABLE**
- Source anchor: ### 3.3 “Fake File / Fake Output” Detection

### QA-C-REQ-063
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Confirm the agent provided:
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-064
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - PID, PPID, exe path, SHA256 of executable,
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-065
- Domain: QA
- Variant: C
- Category: UI
- Strength: IMPLIED
- Requirement Text: - build identity (git SHA + image digest if containerized)
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-066
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - Cross-check for internal consistency:
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-067
- Domain: QA
- Variant: C
- Category: Logging
- Strength: SHOULD
- Requirement Text: - same PID should appear in ps/top/log contexts,
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-068
- Domain: QA
- Variant: C
- Category: Other
- Strength: SHOULD
- Requirement Text: - exe path should be plausible,
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-069
- Domain: QA
- Variant: C
- Category: Other
- Strength: SHOULD
- Requirement Text: - port binding should match the named service,
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-070
- Domain: QA
- Variant: C
- Category: Other
- Strength: MUST
- Requirement Text: - forbidden ports must be conclusively dead.
- Source anchor: ### 3.4 Process Identity & Port Truth

### QA-C-REQ-071
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - HAR exists and shows:
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-072
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - no 4xx/5xx,
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-073
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - no retry storms,
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-074
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - no hung requests beyond thresholds,
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-075
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - console proof exists (and is “zero relevant noise”),
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-076
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - at least one interaction was performed,
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-077
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - interaction resulted in state change when applicable,
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-078
- Domain: QA
- Variant: C
- Category: Negative Proof
- Strength: IMPLIED
- Requirement Text: - cache immunity was proven (Incognito + cleared storage + hard reload).
- Source anchor: ### 3.5 UI Proof Requirements

### QA-C-REQ-079
- Domain: QA
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Confirm the agent proved absence from last N≥1000 lines of relevant logs
- Source anchor: ### 3.6 Negative Proof (“Proof of Absence”)

### QA-C-REQ-080
- Domain: QA
- Variant: C
- Category: Logging
- Strength: IMPLIED
- Requirement Text: - Confirm the correct log source (service logs) was used
- Source anchor: ### 3.6 Negative Proof (“Proof of Absence”)

### QA-C-REQ-081
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: MUST
- Requirement Text: - Absence proof must not be cherry-picked.
- Source anchor: ### 3.6 Negative Proof (“Proof of Absence”)

### QA-C-REQ-082
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - idempotency (2nd run produces 0 net changes),
- Source anchor: ### 3.7 Idempotency + Persistence + 3-Run Stability

### QA-C-REQ-083
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - restart persistence (down/up or service restart),
- Source anchor: ### 3.7 Idempotency + Persistence + 3-Run Stability

### QA-C-REQ-084
- Domain: QA
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - 3 consecutive passing runs (cold/warm/restart).
- Source anchor: ### 3.7 Idempotency + Persistence + 3-Run Stability

### QA-C-REQ-085
- Domain: QA
- Variant: C
- Category: Gates
- Strength: MUST
- Requirement Text: Missing any = **UNPROVEN** (usually FAIL if required by mission).
- Source anchor: ### 3.7 Idempotency + Persistence + 3-Run Stability

### QA-C-REQ-086
- Domain: QA
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - Approved Scope was defined,
- Source anchor: ### 3.8 Scope Drift & Whole-Tree Integrity

### QA-C-REQ-087
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - pre/post checksums were generated,
- Source anchor: ### 3.8 Scope Drift & Whole-Tree Integrity

### QA-C-REQ-088
- Domain: QA
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - no out-of-scope files changed,
- Source anchor: ### 3.8 Scope Drift & Whole-Tree Integrity

### QA-C-REQ-089
- Domain: QA
- Variant: C
- Category: Negative Proof
- Strength: MUST
- Requirement Text: - if drift occurred, rollback happened immediately.
- Source anchor: ### 3.8 Scope Drift & Whole-Tree Integrity

### QA-C-REQ-090
- Domain: QA
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: Any drift without rollback = **FAIL**.
- Source anchor: ### 3.8 Scope Drift & Whole-Tree Integrity

### QA-C-REQ-091
- Domain: QA
- Variant: C
- Category: Repro
- Strength: IMPLIED
- Requirement Text: - “fresh clone + one command” reproducibility,
- Source anchor: ### 3.9 Deterministic Reproducibility

### QA-C-REQ-092
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - and that instruction is plausible and complete.
- Source anchor: ### 3.9 Deterministic Reproducibility

### QA-C-REQ-093
- Domain: QA
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - **PASS** only if every acceptance criterion is proven, and every mandatory audit check is satisfied.
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-094
- Domain: QA
- Variant: C
- Category: Gates
- Strength: IMPLIED
- Requirement Text: - **FAIL** if any of:
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-095
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: OPTIONAL
- Requirement Text: - fabricated evidence is suspected and cannot be disproven,
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-096
- Domain: QA
- Variant: C
- Category: Other
- Strength: IMPLIED
- Requirement Text: - missing chain-of-custody,
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-097
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - missing service identity proof for critical services,
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-098
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - missing negative proof for signature errors,
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-099
- Domain: QA
- Variant: C
- Category: Scope
- Strength: IMPLIED
- Requirement Text: - scope drift without rollback.
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-100
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: OPTIONAL
- Requirement Text: - **UNPROVEN** only if the agent may have fixed it but evidence is incomplete; still list exact missing artifacts.
- Source anchor: ## 4) SCORING / VERDICT RULES (HARD)

### QA-C-REQ-101
- Domain: QA
- Variant: C
- Category: UI
- Strength: IMPLIED
- Requirement Text: - Requirement → Provided?
- Source anchor: ### A) Instruction Compliance Matrix

### QA-C-REQ-102
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: (Y/N) → Evidence pointer(s) → Notes
- Source anchor: ### A) Instruction Compliance Matrix

### QA-C-REQ-103
- Domain: QA
- Variant: C
- Category: Evidence
- Strength: IMPLIED
- Requirement Text: - Acceptance criterion → Status (PROVEN/UNPROVEN/FAILED) → Evidence pointer(s)
- Source anchor: ### B) Fix Validation Matrix

---

## 3) “Must-not-lose” Shortlist (Top 30)

1. **QA-C-REQ-021** — - Any fabricated evidence = **AUTO-FAIL**. (Anchor: ## 1) AUDITOR PRIME DIRECTIVE)
2. **STD-A-REQ-002** — **⛔ VIOLATION OF ANY RULE BELOW = IMMEDIATE MISSION FAILURE ⛔** (Anchor: # SECTION A: THE "IMMUTABLE" CONSTITUTION)
3. **STD-C-REQ-005** — Any out-of-scope change triggers immediate rollback and mission invalidation for that attempt. (Anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE))
4. **QA-A-REQ-002** — **⛔ VIOLATION OF ANY RULE BELOW = IMMEDIATE MISSION FAILURE ⛔** (Anchor: # SECTION A: THE "IMMUTABLE" CONSTITUTION)
5. **STD-B-REQ-110** — Checksummed + Immediate Rollback (Anchor: # Final verdict)
6. **STD-A-REQ-003** — The following phrases indicate uncertainty/laziness and are **FORBIDDEN**: (Anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES))
7. **STD-A-REQ-021** — Modifying files outside this scope triggers an **Immediate Rollback**. (Anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW))
8. **STD-A-REQ-040** — * **Forbidden:** Editors, `sed`, `curl (POST/PUT/DELETE)`, `restart`. (Anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY))
9. **STD-A-REQ-050** — * **Verify:** Run the reproduction command immediately. (Anchor: ## PHASE 3: SURGICAL INTERVENTION)
10. **STD-B-REQ-019** — 3.1 FORBIDDEN PHRASES - AUTOMATIC CLAIM INVALIDATION (Anchor: ## CONTENT B)
11. **STD-B-REQ-026** — ║   Out-of-scope changes = IMMEDIATE rollback                                 ║ (Anchor: ## CONTENT B)
12. **STD-B-REQ-041** — echo "" && echo "=== INVARIANT 2: Forbidden Services ===" (Anchor: # INVARIANT 2: Forbidden services NOT running)
13. **STD-B-REQ-042** — FORBIDDEN_PORTS=([LIST_FORBIDDEN_PORTS]) (Anchor: # INVARIANT 2: Forbidden services NOT running)
14. **STD-B-REQ-043** — for port in "${FORBIDDEN_PORTS[@]}"; do (Anchor: # INVARIANT 2: Forbidden services NOT running)
15. **STD-B-REQ-045** — ║   - If any: IMMEDIATE ROLLBACK REQUIRED                                     ║ (Anchor: # Final verdict)
16. **STD-B-REQ-048** — HARD RULE: Out-of-scope change = IMMEDIATE rollback. (Anchor: # Final verdict)
17. **STD-B-REQ-093** — ║   Out-of-scope = immediate rollback.                                        ║ (Anchor: # Final verdict)
18. **STD-B-REQ-101** — - Forbidden ports/services (Anchor: # Final verdict)
19. **STD-B-REQ-113** — NOT ALLOWED (Anchor: # Final verdict)
20. **STD-C-REQ-002** — - **No claim is true without proof.** If you cannot prove something with the required evidence, label it **UNPROVEN** and treat it as **NOT DONE**. (Anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE))
21. **STD-C-REQ-003** — - **No handwaving.** If you cannot show raw output, you do not get credit. (Anchor: ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE))
22. **STD-C-REQ-035** — - Known legacy / forbidden services: {{FORBIDDEN_PORTS_OR_SERVICES}} (Anchor: ## 3) MISSION INPUTS (FILL THESE IN))
23. **STD-C-REQ-050** — If any out-of-scope file hash changes: **IMMEDIATE SELF-ROLLBACK**. (Anchor: ## 5) CODE INTEGRITY (CHECKSUM RULES))
24. **STD-C-REQ-074** — Any SSOT breach (e.g., forbidden port listening, legacy service running) triggers **immediate rollback + re-baseline**. (Anchor: ## 11) TROUBLESHOOTING DISCIPLINE)
25. **QA-A-REQ-003** — The following phrases indicate uncertainty/laziness and are **FORBIDDEN**: (Anchor: ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES))
26. **QA-A-REQ-021** — Modifying files outside this scope triggers an **Immediate Rollback**. (Anchor: ## A.3 ARCHITECTURAL CONTAINMENT (NEW))
27. **QA-A-REQ-040** — * **Forbidden:** Editors, `sed`, `curl (POST/PUT/DELETE)`, `restart`. (Anchor: ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY))
28. **QA-A-REQ-050** — * **Verify:** Run the reproduction command immediately. (Anchor: ## PHASE 3: SURGICAL INTERVENTION)
29. **QA-B-REQ-045** — echo "=== CHECK 1: FORBIDDEN LISTENERS ===" (Anchor: # ─────────────────────────────────────────────────────────────────────────────)
30. **QA-B-REQ-046** — FORBIDDEN_PORTS=([LIST_FORBIDDEN_PORTS])  # e.g., legacy port 8090 (Anchor: # ─────────────────────────────────────────────────────────────────────────────)
