# PASS 1 — PAIR ALIGNMENT MAP

- Generated at (UTC): 2026-01-27T01:23:53Z

Pairing rule: Standard A ↔ QA A, Standard B ↔ QA B, Standard C ↔ QA C.

## Pair A (Standard A ↔ QA A)
- Total Standard requirements: 76
- COVERED (exact-text match): 76
- MISSING (no exact-text match): 0

### Coverage Table (Standard req → QA verification)
| Std REQ-ID | Coverage | Requirement Text | Source anchor |
|---|---|---|---|
| STD-A-REQ-001 | COVERED | \| **Constraints** \| READ-ONLY UNTIL HYPOTHESIS VALIDATED \| | ## PROTOCOL: ZERO TRUST \| FORENSIC RIGOR \| NO EXCUSES |
| STD-A-REQ-002 | COVERED | **⛔ VIOLATION OF ANY RULE BELOW = IMMEDIATE MISSION FAILURE ⛔** | # SECTION A: THE "IMMUTABLE" CONSTITUTION |
| STD-A-REQ-003 | COVERED | The following phrases indicate uncertainty/laziness and are **FORBIDDEN**: | ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES) |
| STD-A-REQ-004 | COVERED | * ❌ "should work", "probably", "likely", "might" | ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES) |
| STD-A-REQ-005 | COVERED | * ❌ "I think", "I believe", "theoretically" | ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES) |
| STD-A-REQ-006 | COVERED | * ❌ "works for me", "can't reproduce", "local issue" | ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES) |
| STD-A-REQ-007 | COVERED | * ❌ "acceptable trade-off", "minor bug" | ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES) |
| STD-A-REQ-008 | COVERED | * ❌ "done" (without evidence), "fixed" (without proof) | ## A.1 THE LANGUAGE OF RIGOR (BANNED PHRASES) |
| STD-A-REQ-009 | COVERED | Every action that modifies state or code must include: | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-010 | COVERED | 1. | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-011 | COVERED | **The Command:** Exact, reproducible command run. | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-012 | COVERED | 2. | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-013 | COVERED | **The Raw Output:** Unedited, non-truncated stdout/stderr. | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-014 | COVERED | 3. | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-015 | COVERED | **The State Verification:** Proof that the system state changed (DB query, file hash, API response). | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-016 | COVERED | 4. | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-017 | COVERED | **The Negative Test:** Proof that the test fails when the fix is removed (Red -> Green). | ## A.2 THE UNIVERSAL EVIDENCE STANDARD |
| STD-A-REQ-018 | COVERED | * **No New Patterns:** You must use existing design patterns found in the codebase. | ## A.3 ARCHITECTURAL CONTAINMENT (NEW) |
| STD-A-REQ-019 | COVERED | Do not introduce new frameworks or libraries unless explicitly authorized. | ## A.3 ARCHITECTURAL CONTAINMENT (NEW) |
| STD-A-REQ-020 | COVERED | * **Scope Locking:** You may only modify files within `{{AUTHORIZED_SCOPE}}`. | ## A.3 ARCHITECTURAL CONTAINMENT (NEW) |
| STD-A-REQ-021 | COVERED | Modifying files outside this scope triggers an **Immediate Rollback**. | ## A.3 ARCHITECTURAL CONTAINMENT (NEW) |
| STD-A-REQ-022 | COVERED | * **Dependency Freeze:** No `npm install`, `pip install`, or `apt-get` allowed unless the `package.json`/`requirements.txt` is the explicit target of the task. | ## A.3 ARCHITECTURAL CONTAINMENT (NEW) |
| STD-A-REQ-023 | COVERED | * **Symptom:** {{CURRENT_SYMPTOM_DESCRIPTION}} | ## B.1 THE STARTING STATE |
| STD-A-REQ-024 | COVERED | * **Reproduction Path:** `{{REPRODUCTION_COMMAND}}` | ## B.1 THE STARTING STATE |
| STD-A-REQ-025 | COVERED | * **Error Signature:** `{{EXACT_ERROR_MESSAGE}}` | ## B.1 THE STARTING STATE |
| STD-A-REQ-026 | COVERED | The mission is ONLY complete when **ALL** of the following are true: | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-027 | COVERED | 1. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-028 | COVERED | [ ] The specific symptom in B.1 is resolved. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-029 | COVERED | 2. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-030 | COVERED | [ ] **Proof of Absence:** The "Error Signature" no longer appears in logs. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-031 | COVERED | 3. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-032 | COVERED | [ ] **Regression Check:** `{{CRITICAL_FUNCTION}}` still works. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-033 | COVERED | 4. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-034 | COVERED | [ ] **Forensic Packet:** A JSONL ledger of all commands is delivered. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-035 | COVERED | 5. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-036 | COVERED | [ ] **Fresh Clone Test:** The solution works on a fresh environment. | ## B.2 THE DEFINITION OF DONE (DOD) |
| STD-A-REQ-037 | COVERED | **YOU MUST FOLLOW THIS LOOP RECURSIVELY. | # SECTION C: EXECUTION PROTOCOL (THE LOOP) |
| STD-A-REQ-038 | COVERED | DO NOT SKIP STEPS.** | # SECTION C: EXECUTION PROTOCOL (THE LOOP) |
| STD-A-REQ-039 | COVERED | * **Allowed:** `cat`, `grep`, `ls`, `curl (GET)`, `ps`, `logs`. | ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY) |
| STD-A-REQ-040 | COVERED | * **Forbidden:** Editors, `sed`, `curl (POST/PUT/DELETE)`, `restart`. | ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY) |
| STD-A-REQ-041 | COVERED | * **Requirement:** Identify the `PID`, `File Path`, and `Line Number` of the fault. | ## PHASE 1: FORENSIC DISCOVERY (READ-ONLY) |
| STD-A-REQ-042 | COVERED | * **Format:** | ## PHASE 2: HYPOTHESIS & SIMULATION |
| STD-A-REQ-043 | COVERED | * **Hypothesis:** "The issue is caused by X because Y." | ## PHASE 2: HYPOTHESIS & SIMULATION |
| STD-A-REQ-044 | COVERED | * **Proposed Fix:** "I will change line N in file Z." | ## PHASE 2: HYPOTHESIS & SIMULATION |
| STD-A-REQ-045 | COVERED | * **Simulation:** "If I run this, I expect log stream A to stop showing error B." | ## PHASE 2: HYPOTHESIS & SIMULATION |
| STD-A-REQ-046 | COVERED | * **Risk:** "This might break feature C." | ## PHASE 2: HYPOTHESIS & SIMULATION |
| STD-A-REQ-047 | COVERED | * **Pre-Flight:** Hash the file before editing (`sha256sum`). | ## PHASE 3: SURGICAL INTERVENTION |
| STD-A-REQ-048 | COVERED | * **Action:** Apply the edit. | ## PHASE 3: SURGICAL INTERVENTION |
| STD-A-REQ-049 | COVERED | * **Post-Flight:** Hash the file after editing. | ## PHASE 3: SURGICAL INTERVENTION |
| STD-A-REQ-050 | COVERED | * **Verify:** Run the reproduction command immediately. | ## PHASE 3: SURGICAL INTERVENTION |
| STD-A-REQ-051 | COVERED | 1. | ## PHASE 4: THE "RED-TO-GREEN" PROOF |
| STD-A-REQ-052 | COVERED | **Show Green:** Show the system working. | ## PHASE 4: THE "RED-TO-GREEN" PROOF |
| STD-A-REQ-053 | COVERED | 2. | ## PHASE 4: THE "RED-TO-GREEN" PROOF |
| STD-A-REQ-054 | COVERED | **Force Red:** Revert the change (or break it intentionally) and prove it fails again. | ## PHASE 4: THE "RED-TO-GREEN" PROOF |
| STD-A-REQ-055 | COVERED | 3. | ## PHASE 4: THE "RED-TO-GREEN" PROOF |
| STD-A-REQ-056 | COVERED | **Return to Green:** Re-apply the fix and confirm success. | ## PHASE 4: THE "RED-TO-GREEN" PROOF |
| STD-A-REQ-057 | COVERED | At the end of the mission, you must generate a **COMPLETION PACKET** containing: | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-058 | COVERED | 1. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-059 | COVERED | **`ledger.jsonl`**: Every command executed, timestamped. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-060 | COVERED | 2. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-061 | COVERED | **`diff.patch`**: The exact code changes. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-062 | COVERED | 3. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-063 | COVERED | **`verification_script.sh`**: A single script that: | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-064 | COVERED | * Checks the fix. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-065 | COVERED | * Checks for regressions. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-066 | COVERED | * Returns `0` only if PERFECTION is achieved. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-067 | COVERED | 4. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-068 | COVERED | **`resource_snapshot.txt`**: CPU/Memory usage before vs. | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-069 | COVERED | after (Must be within 15% variance). | # SECTION D: MANDATORY ARTIFACTS (THE DELIVERABLES) |
| STD-A-REQ-070 | COVERED | * **Target Files:** `{{TARGET_FILES}}` | # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK |
| STD-A-REQ-071 | COVERED | * **Relevant Logs:** `{{LOG_PATH}}` | # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK |
| STD-A-REQ-072 | COVERED | * **Test Command:** `{{TEST_COMMAND}}` | # SECTION E: SPECIAL INSTRUCTIONS FOR THIS TASK |
| STD-A-REQ-073 | COVERED | **You are a Senior Principal Engineer. | # FINAL WARNING |
| STD-A-REQ-074 | COVERED | You do not guess. | # FINAL WARNING |
| STD-A-REQ-075 | COVERED | You do not "try" things. | # FINAL WARNING |
| STD-A-REQ-076 | COVERED | You measure, you analyze, you execute, and you prove.** | # FINAL WARNING |

### Missing QA checks to add later (do not implement yet)
- None detected by exact-text match.

## Pair B (Standard B ↔ QA B)
- Total Standard requirements: 113
- COVERED (exact-text match): 5
- MISSING (no exact-text match): 108

### Coverage Table (Standard req → QA verification)
| Std REQ-ID | Coverage | Requirement Text | Source anchor |
|---|---|---|---|
| STD-B-REQ-001 | MISSING | 1. | ## CONTENT B |
| STD-B-REQ-002 | MISSING | Copy this entire template | ## CONTENT B |
| STD-B-REQ-003 | MISSING | 2. | ## CONTENT B |
| STD-B-REQ-004 | MISSING | Fill in the [PLACEHOLDERS] in Section 1 (Task Definition) | ## CONTENT B |
| STD-B-REQ-005 | MISSING | 3. | ## CONTENT B |
| STD-B-REQ-006 | MISSING | Customize Section 2 (Scope) for your specific task | ## CONTENT B |
| STD-B-REQ-007 | MISSING | 4. | ## CONTENT B |
| STD-B-REQ-008 | MISSING | Adjust time budgets in Section 9 if needed | ## CONTENT B |
| STD-B-REQ-009 | MISSING | 5. | ## CONTENT B |
| STD-B-REQ-010 | MISSING | Add task-specific gates in Section 11 | ## CONTENT B |
| STD-B-REQ-011 | MISSING | 6. | ## CONTENT B |
| STD-B-REQ-012 | MISSING | Send to Claude Code / Builder / Agent | ## CONTENT B |
| STD-B-REQ-013 | MISSING | ║   SUCCESS CRITERIA (ALL must be true):                                       ║ | ## CONTENT B |
| STD-B-REQ-014 | MISSING | ║   [Must be reproducible and automatable]                                    ║ | ## CONTENT B |
| STD-B-REQ-015 | MISSING | ║   EXPLICITLY OUT OF SCOPE (DO NOT touch):                                   ║ | ## CONTENT B |
| STD-B-REQ-016 | MISSING | ║   DEPENDENCIES (systems that must remain working):                          ║ | ## CONTENT B |
| STD-B-REQ-017 | MISSING | ║   • [Must maintain backward compatibility]                                  ║ | ## CONTENT B |
| STD-B-REQ-018 | MISSING | ║   • [Must not increase response time by >20%]                               ║ | ## CONTENT B |
| STD-B-REQ-019 | MISSING | 3.1 FORBIDDEN PHRASES - AUTOMATIC CLAIM INVALIDATION | ## CONTENT B |
| STD-B-REQ-020 | MISSING | ║   ❌ "auth required"          ❌ "out of scope"                               ║ | ## CONTENT B |
| STD-B-REQ-021 | MISSING | ║   If you cannot produce evidence, you MUST say "UNPROVEN" and treat it as   ║ | ## CONTENT B |
| STD-B-REQ-022 | MISSING | 3.2 CORE ENFORCEMENT PRINCIPLES | ## CONTENT B |
| STD-B-REQ-023 | MISSING | ║   Must demonstrate controlled failure BEFORE claiming success               ║ | ## CONTENT B |
| STD-B-REQ-024 | MISSING | ║   HTTP 200 is NOT success. | ## CONTENT B |
| STD-B-REQ-025 | MISSING | Must validate content, schema, behavior.        ║ | ## CONTENT B |
| STD-B-REQ-026 | MISSING | ║   Out-of-scope changes = IMMEDIATE rollback                                 ║ | ## CONTENT B |
| STD-B-REQ-027 | MISSING | ║   Must survive restart. | ## CONTENT B |
| STD-B-REQ-028 | MISSING | Must pass 3 consecutive runs.                      ║ | ## CONTENT B |
| STD-B-REQ-029 | MISSING | ║   PRINCIPLE 7: AUTOMATION ONLY                                               ║ | ## CONTENT B |
| STD-B-REQ-030 | MISSING | ║   Every verification must be scriptable. | ## CONTENT B |
| STD-B-REQ-031 | MISSING | No manual steps.                  ║ | ## CONTENT B |
| STD-B-REQ-032 | MISSING | Every claim of "done" or "working" MUST include this EXACT format: | ## CONTENT B |
| STD-B-REQ-033 | MISSING | ║  - Matches found: [must be 0]                                               ║ | ## CONTENT B |
| STD-B-REQ-034 | MISSING | ║  - Budget: [max allowed]                                                    ║ | ## CONTENT B |
| STD-B-REQ-035 | MISSING | ║       - All required services are running                                   ║ | ## CONTENT B |
| STD-B-REQ-036 | MISSING | ║   IF ANY ITEM FAILS → DO NOT PROCEED. | ## CONTENT B |
| STD-B-REQ-037 | MISSING | FIX IT FIRST.                         ║ | ## CONTENT B |
| STD-B-REQ-038 | MISSING | echo "=== INVARIANT 1: Required Services ===" | # INVARIANT 1: Required services running |
| STD-B-REQ-039 | MISSING | REQUIRED_PORTS=([LIST_YOUR_REQUIRED_PORTS]) | # INVARIANT 1: Required services running |
| STD-B-REQ-040 | COVERED | for port in "${REQUIRED_PORTS[@]}"; do | # INVARIANT 1: Required services running |
| STD-B-REQ-041 | MISSING | echo "" && echo "=== INVARIANT 2: Forbidden Services ===" | # INVARIANT 2: Forbidden services NOT running |
| STD-B-REQ-042 | MISSING | FORBIDDEN_PORTS=([LIST_FORBIDDEN_PORTS]) | # INVARIANT 2: Forbidden services NOT running |
| STD-B-REQ-043 | COVERED | for port in "${FORBIDDEN_PORTS[@]}"; do | # INVARIANT 2: Forbidden services NOT running |
| STD-B-REQ-044 | MISSING | echo "❌ INVARIANT CHECK FAILED - DO NOT PROCEED" | # Final verdict |
| STD-B-REQ-045 | MISSING | ║   - If any: IMMEDIATE ROLLBACK REQUIRED                                     ║ | # Final verdict |
| STD-B-REQ-046 | MISSING | ║   - Rollback command: [exact command]                                       ║ | # Final verdict |
| STD-B-REQ-047 | MISSING | ║   - Rollback tested: [YES/NO]                                               ║ | # Final verdict |
| STD-B-REQ-048 | MISSING | HARD RULE: Out-of-scope change = IMMEDIATE rollback. | # Final verdict |
| STD-B-REQ-049 | MISSING | No exceptions. | # Final verdict |
| STD-B-REQ-050 | MISSING | SECTION 8: GATE ENFORCEMENT | # Final verdict |
| STD-B-REQ-051 | MISSING | ║                    GATE ENFORCEMENT RULES                                     ║ | # Final verdict |
| STD-B-REQ-052 | MISSING | ║   RULE 1: SEQUENTIAL - Gates must pass in order. | # Final verdict |
| STD-B-REQ-053 | MISSING | No skipping.               ║ | # Final verdict |
| STD-B-REQ-054 | MISSING | ║   RULE 2: FOCUS - If Gate N fails, only work on Gate N. | # Final verdict |
| STD-B-REQ-055 | MISSING | Nothing else.       ║ | # Final verdict |
| STD-B-REQ-056 | MISSING | ║   RULE 3: TWO-STRIKE ROLLBACK                                                ║ | # Final verdict |
| STD-B-REQ-057 | MISSING | ║   If same gate fails 2 consecutive times:                                   ║ | # Final verdict |
| STD-B-REQ-058 | COVERED | ║   2. | # Final verdict |
| STD-B-REQ-059 | MISSING | ROLLBACK last change                                                   ║ | # Final verdict |
| STD-B-REQ-060 | MISSING | ║   6. | # Final verdict |
| STD-B-REQ-061 | MISSING | Only then retry                                                        ║ | # Final verdict |
| STD-B-REQ-062 | MISSING | ║   Must perform git bisect or manual bisection to isolate root cause.       ║ | # Final verdict |
| STD-B-REQ-063 | MISSING | Gate Attempt Log Format | # Final verdict |
| STD-B-REQ-064 | MISSING | ║                    GATE ATTEMPT LOG                                           ║ | # Final verdict |
| STD-B-REQ-065 | MISSING | ║   GATE: [Gate name/number]                                                   ║ | # Final verdict |
| STD-B-REQ-066 | MISSING | ║   API endpoint response             │ 5s       │ GATE FAIL                   ║ | # Final verdict |
| STD-B-REQ-067 | MISSING | ║   Page initial load                 │ 10s      │ GATE FAIL                   ║ | # Final verdict |
| STD-B-REQ-068 | MISSING | ║   UI interaction response           │ 3s       │ GATE FAIL                   ║ | # Final verdict |
| STD-B-REQ-069 | MISSING | ║   Database query                    │ 2s       │ GATE FAIL                   ║ | # Final verdict |
| STD-B-REQ-070 | MISSING | ║   Service health check              │ 1s       │ GATE FAIL                   ║ | # Final verdict |
| STD-B-REQ-071 | MISSING | ║   [ ] Evidence Block provided with all required fields                      ║ | # Final verdict |
| STD-B-REQ-072 | MISSING | ║   [ ] Only approved files modified (tree hash check)                        ║ | # Final verdict |
| STD-B-REQ-073 | MISSING | SECTION 11: TASK-SPECIFIC GATES (CUSTOMIZE) | # Final verdict |
| STD-B-REQ-074 | MISSING | ║                    TASK GATES (CUSTOMIZE FOR YOUR TASK)                       ║ | # Final verdict |
| STD-B-REQ-075 | MISSING | ║   GATE 0: PRE-FLIGHT                                                         ║ | # Final verdict |
| STD-B-REQ-076 | MISSING | ║   GATE 1: [FIRST MILESTONE - customize]                                      ║ | # Final verdict |
| STD-B-REQ-077 | MISSING | ║   GATE 2: [SECOND MILESTONE - customize]                                     ║ | # Final verdict |
| STD-B-REQ-078 | MISSING | ║   [ADD MORE GATES AS NEEDED]                                                 ║ | # Final verdict |
| STD-B-REQ-079 | MISSING | ║   GATE FINAL: COMPLETION                                                     ║ | # Final verdict |
| STD-B-REQ-080 | MISSING | ║   [ ] All prior gates passed                                                ║ | # Final verdict |
| STD-B-REQ-081 | MISSING | ║   RULE: Maintain append-only JSONL log of EVERY command run.                ║ | # Final verdict |
| STD-B-REQ-082 | MISSING | ║     "gate": "gate_name",                                                    ║ | # Final verdict |
| STD-B-REQ-083 | MISSING | ║     "why": "reason tied to gate requirement",                               ║ | # Final verdict |
| STD-B-REQ-084 | MISSING | ║   • Every command must be logged BEFORE execution                           ║ | # Final verdict |
| STD-B-REQ-085 | MISSING | ║   • Output must be captured to file (not just displayed)                   ║ | # Final verdict |
| STD-B-REQ-086 | MISSING | ║   • Ledger must be included in Completion Packet                           ║ | # Final verdict |
| STD-B-REQ-087 | MISSING | ║   REQUIRED ARTIFACTS:                                                        ║ | # Final verdict |
| STD-B-REQ-088 | MISSING | ║      [ ] One complete Evidence Block per gate passed                        ║ | # Final verdict |
| STD-B-REQ-089 | MISSING | ║   Fresh clone + single command must reproduce the same passing results.     ║ | # Final verdict |
| STD-B-REQ-090 | MISSING | ║    • Scope integrity (only approved files changed)                         ║ | # Final verdict |
| STD-B-REQ-091 | MISSING | ║    • Change manifest with rollback plan                                    ║ | # Final verdict |
| STD-B-REQ-092 | MISSING | ║   Gates are HARD STOPS.                                                      ║ | # Final verdict |
| STD-B-REQ-093 | MISSING | ║   Out-of-scope = immediate rollback.                                        ║ | # Final verdict |
| STD-B-REQ-094 | MISSING | ║   Automation only (no manual steps).                                        ║ | # Final verdict |
| STD-B-REQ-095 | MISSING | ║   Full completion packet required."                                         ║ | # Final verdict |
| STD-B-REQ-096 | MISSING | - Task ID, title, problem, expected outcome, success criteria | # Final verdict |
| STD-B-REQ-097 | MISSING | - Approved files/directories | # Final verdict |
| STD-B-REQ-098 | MISSING | - Out of scope items | # Final verdict |
| STD-B-REQ-099 | MISSING | - Dependencies and constraints | # Final verdict |
| STD-B-REQ-100 | MISSING | - Required ports/services | # Final verdict |
| STD-B-REQ-101 | MISSING | - Forbidden ports/services | # Final verdict |
| STD-B-REQ-102 | MISSING | - Environment checks | # Final verdict |
| STD-B-REQ-103 | MISSING | - Adjust limits for your task type | # Final verdict |
| STD-B-REQ-104 | MISSING | □ 5. | # Final verdict |
| STD-B-REQ-105 | MISSING | Fill in Section 11 (Task Gates) | # Final verdict |
| STD-B-REQ-106 | MISSING | - Define specific milestones for your task | # Final verdict |
| STD-B-REQ-107 | MISSING | - Each gate should have clear pass/fail criteria | # Final verdict |
| STD-B-REQ-108 | COVERED | 1.0.0 | # Final verdict |
| STD-B-REQ-109 | MISSING | Evidence Required | # Final verdict |
| STD-B-REQ-110 | MISSING | Checksummed + Immediate Rollback | # Final verdict |
| STD-B-REQ-111 | MISSING | Required (no manual steps) | # Final verdict |
| STD-B-REQ-112 | MISSING | JSONL append-only ledger | # Final verdict |
| STD-B-REQ-113 | COVERED | NOT ALLOWED | # Final verdict |

### Missing QA checks to add later (do not implement yet)
- 1.
- Copy this entire template
- 2.
- Fill in the [PLACEHOLDERS] in Section 1 (Task Definition)
- 3.
- Customize Section 2 (Scope) for your specific task
- 4.
- Adjust time budgets in Section 9 if needed
- 5.
- Add task-specific gates in Section 11
- 6.
- Send to Claude Code / Builder / Agent
- ║   SUCCESS CRITERIA (ALL must be true):                                       ║
- ║   [Must be reproducible and automatable]                                    ║
- ║   EXPLICITLY OUT OF SCOPE (DO NOT touch):                                   ║
- ║   DEPENDENCIES (systems that must remain working):                          ║
- ║   • [Must maintain backward compatibility]                                  ║
- ║   • [Must not increase response time by >20%]                               ║
- 3.1 FORBIDDEN PHRASES - AUTOMATIC CLAIM INVALIDATION
- ║   ❌ "auth required"          ❌ "out of scope"                               ║
- ║   If you cannot produce evidence, you MUST say "UNPROVEN" and treat it as   ║
- 3.2 CORE ENFORCEMENT PRINCIPLES
- ║   Must demonstrate controlled failure BEFORE claiming success               ║
- ║   HTTP 200 is NOT success.
- Must validate content, schema, behavior.        ║
- ║   Out-of-scope changes = IMMEDIATE rollback                                 ║
- ║   Must survive restart.
- Must pass 3 consecutive runs.                      ║
- ║   PRINCIPLE 7: AUTOMATION ONLY                                               ║
- ║   Every verification must be scriptable.
- No manual steps.                  ║
- Every claim of "done" or "working" MUST include this EXACT format:
- ║  - Matches found: [must be 0]                                               ║
- ║  - Budget: [max allowed]                                                    ║
- ║       - All required services are running                                   ║
- ║   IF ANY ITEM FAILS → DO NOT PROCEED.
- FIX IT FIRST.                         ║
- echo "=== INVARIANT 1: Required Services ==="
- REQUIRED_PORTS=([LIST_YOUR_REQUIRED_PORTS])
- echo "" && echo "=== INVARIANT 2: Forbidden Services ==="
- FORBIDDEN_PORTS=([LIST_FORBIDDEN_PORTS])
- echo "❌ INVARIANT CHECK FAILED - DO NOT PROCEED"
- ║   - If any: IMMEDIATE ROLLBACK REQUIRED                                     ║
- ║   - Rollback command: [exact command]                                       ║
- ║   - Rollback tested: [YES/NO]                                               ║
- HARD RULE: Out-of-scope change = IMMEDIATE rollback.
- No exceptions.
- SECTION 8: GATE ENFORCEMENT
- ║                    GATE ENFORCEMENT RULES                                     ║
- ║   RULE 1: SEQUENTIAL - Gates must pass in order.
- ... (58 more)

## Pair C (Standard C ↔ QA C)
- Total Standard requirements: 96
- COVERED (exact-text match): 10
- MISSING (no exact-text match): 86

### Coverage Table (Standard req → QA verification)
| Std REQ-ID | Coverage | Requirement Text | Source anchor |
|---|---|---|---|
| STD-C-REQ-001 | MISSING | You must follow this document **exactly**. | # UNIVERSAL MISSION TEMPLATE — MANDATORY FIX / BUILD / INVESTIGATE (NO EXCUSES) |
| STD-C-REQ-002 | MISSING | - **No claim is true without proof.** If you cannot prove something with the required evidence, label it **UNPROVEN** and treat it as **NOT DONE**. | ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE) |
| STD-C-REQ-003 | MISSING | - **No handwaving.** If you cannot show raw output, you do not get credit. | ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE) |
| STD-C-REQ-004 | MISSING | - **No scope drift.** Only modify what is explicitly approved. | ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE) |
| STD-C-REQ-005 | MISSING | Any out-of-scope change triggers immediate rollback and mission invalidation for that attempt. | ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE) |
| STD-C-REQ-006 | MISSING | - **Hard stop gates.** If a gate fails, you do not proceed to later steps. | ## 0) PRIME DIRECTIVE (NON-NEGOTIABLE) |
| STD-C-REQ-007 | MISSING | You must not use: | ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED) |
| STD-C-REQ-008 | MISSING | - “should work”, “likely”, “probably”, “seems”, “might”, “maybe” | ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED) |
| STD-C-REQ-009 | MISSING | - “works for me”, “can’t reproduce”, “it’s fine”, “looks good” | ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED) |
| STD-C-REQ-010 | MISSING | - “done” / “fixed” without the required Evidence Block | ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED) |
| STD-C-REQ-011 | MISSING | If you must express uncertainty, use: **UNPROVEN** + what evidence is missing. | ## 1) FORBIDDEN PHRASES (AUTO-FAIL IF USED) |
| STD-C-REQ-012 | MISSING | Every response must contain these sections in this order: | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-013 | COVERED | 1. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-014 | MISSING | **MISSION STATE** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-015 | COVERED | 2. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-016 | MISSING | **SCOPE & CHANGE MANIFEST** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-017 | COVERED | 3. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-018 | MISSING | **PHASE 0 — BASELINE / GROUND TRUTH** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-019 | COVERED | 4. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-020 | MISSING | **HYPOTHESIS (SINGLE, FALSIFIABLE)** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-021 | COVERED | 5. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-022 | MISSING | **PLAN (NEXT COMMANDS ONLY)** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-023 | COVERED | 6. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-024 | MISSING | **EVIDENCE BLOCKS (RAW OUTPUT)** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-025 | COVERED | 7. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-026 | MISSING | **GATE RESULT (PASS/FAIL)** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-027 | COVERED | 8. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-028 | MISSING | **ROLLBACK STATUS** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-029 | COVERED | 9. | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-030 | MISSING | **NEXT ACTION** | ## 2) REQUIRED OUTPUT FORMAT (EVERY RESPONSE) |
| STD-C-REQ-031 | COVERED | - Repo root: {{REPO_ROOT}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-032 | MISSING | - Runtime: {{docker/systemd/node/python/etc}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-033 | MISSING | - Critical services/ports: {{PORTS_AND_SERVICES}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-034 | MISSING | - Primary datastore(s): {{DBS_AND_TABLES}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-035 | MISSING | - Known legacy / forbidden services: {{FORBIDDEN_PORTS_OR_SERVICES}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-036 | MISSING | - Observability locations (logs/metrics): {{LOG_PATHS_DASHBOARDS}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-037 | MISSING | **Acceptance Criteria (must be testable):** | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-038 | MISSING | - {{AC_1}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-039 | MISSING | - {{AC_2}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-040 | MISSING | - {{AC_3}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-041 | MISSING | **Approved Scope (ONLY these files/dirs may change this phase):** | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-042 | MISSING | - {{APPROVED_SCOPE_LIST}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-043 | MISSING | - Endpoint max latency: {{MAX_ENDPOINT_SECONDS}} seconds | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-044 | MISSING | - UI interaction max time: {{MAX_UI_SECONDS}} seconds | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-045 | MISSING | - {{ERROR_STRING_1}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-046 | MISSING | - {{ERROR_STRING_2}} | ## 3) MISSION INPUTS (FILL THESE IN) |
| STD-C-REQ-047 | MISSING | Maintain an **append-only JSONL ledger** of every command you run: | ## 4) CHAIN OF CUSTODY (MANDATORY COMMAND LEDGER) |
| STD-C-REQ-048 | MISSING | - timestamp, cwd, command, why, and pointer to raw output artifact file. | ## 4) CHAIN OF CUSTODY (MANDATORY COMMAND LEDGER) |
| STD-C-REQ-049 | MISSING | - Produce a deterministic checksum of: | ## 5) CODE INTEGRITY (CHECKSUM RULES) |
| STD-C-REQ-050 | MISSING | If any out-of-scope file hash changes: **IMMEDIATE SELF-ROLLBACK**. | ## 5) CODE INTEGRITY (CHECKSUM RULES) |
| STD-C-REQ-051 | MISSING | For every critical service check you must prove: | ## 6) SERVICE IDENTITY (ANTI-FAKE / ANTI-WRONG-PORT) |
| STD-C-REQ-052 | MISSING | - port → PID → PPID → executable path → **SHA256 of executable** | ## 6) SERVICE IDENTITY (ANTI-FAKE / ANTI-WRONG-PORT) |
| STD-C-REQ-053 | MISSING | - build identity: **git commit SHA** and **container image digest** (if containerized) | ## 6) SERVICE IDENTITY (ANTI-FAKE / ANTI-WRONG-PORT) |
| STD-C-REQ-054 | MISSING | Every “success” claim must include **Dual-Channel Proof**: | ## 7) PROOF STANDARD (HARD TO FAKE) |
| STD-C-REQ-055 | MISSING | - Channel A: Browser/Playwright (HAR + console) | ## 7) PROOF STANDARD (HARD TO FAKE) |
| STD-C-REQ-056 | MISSING | - Channel B: Direct system truth (DB query / curl / logs / process identity / checksum) | ## 7) PROOF STANDARD (HARD TO FAKE) |
| STD-C-REQ-057 | MISSING | Artifacts must be checksummed with SHA256 and listed in an **Evidence Manifest**. | ## 7) PROOF STANDARD (HARD TO FAKE) |
| STD-C-REQ-058 | MISSING | - If output > {{MAX_INLINE_LINES}} lines, redirect to a file and attach it as an artifact. | ## 7) PROOF STANDARD (HARD TO FAKE) |
| STD-C-REQ-059 | MISSING | A UI gate passes only if all are true: | ## 8) UI / NETWORK STRICTNESS |
| STD-C-REQ-060 | MISSING | - **Zero relevant console errors AND zero relevant warnings** (network/fetch/CORS/hydration). | ## 8) UI / NETWORK STRICTNESS |
| STD-C-REQ-061 | MISSING | - HAR shows: no 4xx/5xx, no retry storms, no hung long-polls beyond threshold. | ## 8) UI / NETWORK STRICTNESS |
| STD-C-REQ-062 | MISSING | - The interaction is **real**: click → network request → response → UI updates. | ## 8) UI / NETWORK STRICTNESS |
| STD-C-REQ-063 | MISSING | - At least one interaction must **mutate persisted state** (if applicable) and be verified by DB/system query. | ## 8) UI / NETWORK STRICTNESS |
| STD-C-REQ-064 | MISSING | - Repeat verification in **Incognito**, after clearing site data, with hard reload. | ## 8) UI / NETWORK STRICTNESS |
| STD-C-REQ-065 | MISSING | - Cached/SW responses do not count. | ## 8) UI / NETWORK STRICTNESS |
| STD-C-REQ-066 | MISSING | After the fix, you must prove the signature error strings are absent: | ## 9) NEGATIVE PROOF (“PROOF OF ABSENCE”) |
| STD-C-REQ-067 | MISSING | - Show that the string is mathematically absent from the last **N ≥ 1000** relevant log lines. | ## 9) NEGATIVE PROOF (“PROOF OF ABSENCE”) |
| STD-C-REQ-068 | MISSING | Working UI is not enough; **the error must be gone**. | ## 9) NEGATIVE PROOF (“PROOF OF ABSENCE”) |
| STD-C-REQ-069 | MISSING | Every gate must pass: | ## 10) RELIABILITY (WORKS-ONCE IS FAILURE) |
| STD-C-REQ-070 | MISSING | And must pass **3 consecutive runs**. | ## 10) RELIABILITY (WORKS-ONCE IS FAILURE) |
| STD-C-REQ-071 | MISSING | - Re-run the fix steps; second run must produce **0 net changes**. | ## 10) RELIABILITY (WORKS-ONCE IS FAILURE) |
| STD-C-REQ-072 | MISSING | Each attempt must include exactly **one** falsifiable hypothesis and the test that disproves it. | ## 11) TROUBLESHOOTING DISCIPLINE |
| STD-C-REQ-073 | MISSING | - Perform **bisection** (git bisect or manual) until the precise offending change is isolated. | ## 11) TROUBLESHOOTING DISCIPLINE |
| STD-C-REQ-074 | MISSING | Any SSOT breach (e.g., forbidden port listening, legacy service running) triggers **immediate rollback + re-baseline**. | ## 11) TROUBLESHOOTING DISCIPLINE |
| STD-C-REQ-075 | MISSING | - Mutation test: deliberately break a route/config and prove tests fail. | ## 12) COURTROOM-GRADE TESTS (IF APPLICABLE) |
| STD-C-REQ-076 | MISSING | - Schema enforcement: validate responses against JSON Schema. | ## 12) COURTROOM-GRADE TESTS (IF APPLICABLE) |
| STD-C-REQ-077 | MISSING | - Proxy contract tests: each `/api/*` must call intended upstream host/path and reject others. | ## 12) COURTROOM-GRADE TESTS (IF APPLICABLE) |
| STD-C-REQ-078 | MISSING | Each Evidence Block must include a System Health Snapshot for involved PIDs: | ## 13) RESOURCE SAFETY (COLLATERAL DAMAGE WATCHDOGS) |
| STD-C-REQ-079 | MISSING | - CPU%, RSS, FD count (if available), and a top/pidstat excerpt. | ## 13) RESOURCE SAFETY (COLLATERAL DAMAGE WATCHDOGS) |
| STD-C-REQ-080 | MISSING | Mission is only complete if you provide: | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-081 | MISSING | - Evidence Manifest (SHA256 for every artifact) | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-082 | MISSING | - HAR(s), console capture(s), screenshots | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-083 | MISSING | - Raw logs (as files), DB query outputs | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-084 | MISSING | - Command ledger JSONL | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-085 | MISSING | - Pre/post checksum reports | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-086 | MISSING | - E2E run outputs (if used) | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-087 | MISSING | - A fresh-clone reproducibility instruction: **one command** that regenerates the evidence or fails deterministically | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-088 | MISSING | - “No green until red” demonstration (if applicable): controlled failure → restore → pass | ## 14) FINAL COMPLETION PACKET (REQUIRED OR NOT COMPLETE) |
| STD-C-REQ-089 | MISSING | (You must fill this out first.) | ## 1. MISSION STATE |
| STD-C-REQ-090 | MISSING | - Approved scope: {{APPROVED_SCOPE_LIST}} | ## 2. SCOPE & CHANGE MANIFEST |
| STD-C-REQ-091 | MISSING | - Prohibited: Anything else. | ## 2. SCOPE & CHANGE MANIFEST |
| STD-C-REQ-092 | MISSING | - Pre-change checksums: (required) | ## 2. SCOPE & CHANGE MANIFEST |
| STD-C-REQ-093 | MISSING | - Authorized commands list: (required) | ## 2. SCOPE & CHANGE MANIFEST |
| STD-C-REQ-094 | MISSING | Gate verdict with evidence references. | ## 7. GATE RESULT (PASS/FAIL) |
| STD-C-REQ-095 | MISSING | If failed, rollback steps + evidence. | ## 8. ROLLBACK STATUS |
| STD-C-REQ-096 | MISSING | Either proceed to next gate or stop-the-line. | ## 9. NEXT ACTION |

### Missing QA checks to add later (do not implement yet)
- You must follow this document **exactly**.
- - **No claim is true without proof.** If you cannot prove something with the required evidence, label it **UNPROVEN** and treat it as **NOT DONE**.
- - **No handwaving.** If you cannot show raw output, you do not get credit.
- - **No scope drift.** Only modify what is explicitly approved.
- Any out-of-scope change triggers immediate rollback and mission invalidation for that attempt.
- - **Hard stop gates.** If a gate fails, you do not proceed to later steps.
- You must not use:
- - “should work”, “likely”, “probably”, “seems”, “might”, “maybe”
- - “works for me”, “can’t reproduce”, “it’s fine”, “looks good”
- - “done” / “fixed” without the required Evidence Block
- If you must express uncertainty, use: **UNPROVEN** + what evidence is missing.
- Every response must contain these sections in this order:
- **MISSION STATE**
- **SCOPE & CHANGE MANIFEST**
- **PHASE 0 — BASELINE / GROUND TRUTH**
- **HYPOTHESIS (SINGLE, FALSIFIABLE)**
- **PLAN (NEXT COMMANDS ONLY)**
- **EVIDENCE BLOCKS (RAW OUTPUT)**
- **GATE RESULT (PASS/FAIL)**
- **ROLLBACK STATUS**
- **NEXT ACTION**
- - Runtime: {{docker/systemd/node/python/etc}}
- - Critical services/ports: {{PORTS_AND_SERVICES}}
- - Primary datastore(s): {{DBS_AND_TABLES}}
- - Known legacy / forbidden services: {{FORBIDDEN_PORTS_OR_SERVICES}}
- - Observability locations (logs/metrics): {{LOG_PATHS_DASHBOARDS}}
- **Acceptance Criteria (must be testable):**
- - {{AC_1}}
- - {{AC_2}}
- - {{AC_3}}
- **Approved Scope (ONLY these files/dirs may change this phase):**
- - {{APPROVED_SCOPE_LIST}}
- - Endpoint max latency: {{MAX_ENDPOINT_SECONDS}} seconds
- - UI interaction max time: {{MAX_UI_SECONDS}} seconds
- - {{ERROR_STRING_1}}
- - {{ERROR_STRING_2}}
- Maintain an **append-only JSONL ledger** of every command you run:
- - timestamp, cwd, command, why, and pointer to raw output artifact file.
- - Produce a deterministic checksum of:
- If any out-of-scope file hash changes: **IMMEDIATE SELF-ROLLBACK**.
- For every critical service check you must prove:
- - port → PID → PPID → executable path → **SHA256 of executable**
- - build identity: **git commit SHA** and **container image digest** (if containerized)
- Every “success” claim must include **Dual-Channel Proof**:
- - Channel A: Browser/Playwright (HAR + console)
- - Channel B: Direct system truth (DB query / curl / logs / process identity / checksum)
- Artifacts must be checksummed with SHA256 and listed in an **Evidence Manifest**.
- - If output > {{MAX_INLINE_LINES}} lines, redirect to a file and attach it as an artifact.
- A UI gate passes only if all are true:
- - **Zero relevant console errors AND zero relevant warnings** (network/fetch/CORS/hydration).
- ... (36 more)

