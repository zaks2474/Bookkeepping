# PASS 3 — PATCHLIST (Implementation-Ready)

Notes:
- Target files are restricted to: PASS2_STANDARD_PROMPT_DRAFT.md, PASS2_QA_PROMPT_DRAFT.md
- Patches are written as “insert/replace” blocks with exact text.

## P3-STD-01 — Placeholder hard-fail gate
- Target: PASS2_STANDARD_PROMPT_DRAFT.md
- Insert after: SECTION 4 header
- Insert text:
```text
PLACEHOLDER HARD-FAIL:
- Before Gate 0, you MUST prove there are zero unresolved template tokens in the mission prompt and artifacts.
- Any occurrence of "{{" or "}}" in inputs/artifacts = IMMEDIATE FAIL (do not proceed).
```
- Expected effect: Prevents running with undefined ports/scope/log paths.

## P3-STD-02 — Negative test must reproduce original failure signature
- Target: PASS2_STANDARD_PROMPT_DRAFT.md
- Replace: SECTION 2 → Required Components item 5
- Replacement text:
```text
5. NEGATIVE TEST (Red-to-Green):
   - The Red step MUST reproduce the original failure mode (same Error Signature OR same failing reproduction command).
   - "Red" that does not include the Error Signature (or does not fail the reproduction command) is INVALID.
   - The Restore step MUST be re-applying the exact fix (or reverting the revert of the fix).
```
- Expected effect: Closes “false red” loophole.

## P3-STD-03 — Fix checksum commands (all files, safe with spaces)
- Target: PASS2_STANDARD_PROMPT_DRAFT.md
- Replace: SECTION 8 pre/post + verification commands
- Replacement text:
```text
# Pre-Change (Required)
find {{APPROVED_SCOPE}} -type f -print0 | sort -z | xargs -0 sha256sum > pre_change_checksums.txt

# Post-Change (Required)
find {{APPROVED_SCOPE}} -type f -print0 | sort -z | xargs -0 sha256sum > post_change_checksums.txt

# Verification
diff -u pre_change_checksums.txt post_change_checksums.txt || true
```
- Expected effect: Prevents checksum bypass and filename bugs.

## P3-STD-04 — Require out-of-scope changed-file proof
- Target: PASS2_STANDARD_PROMPT_DRAFT.md
- Insert after: SECTION 8 Verification
- Insert text:
```text
OUT-OF-SCOPE CHANGE DETECTION:
- You MUST provide a changed-files list for the whole repo (git diff --name-only if git; otherwise a full-tree checksum manifest).
- Any changed file outside {{APPROVED_SCOPE_LIST}} = IMMEDIATE FAIL + rollback proof.
```
- Expected effect: Detects hidden drift outside scope.

## P3-STD-05 — Strengthen ledger schema
- Target: PASS2_STANDARD_PROMPT_DRAFT.md
- Replace: ledger.json example in SECTION 7
- Replacement text:
```json
{"ts_start":"2026-01-27T02:15:00Z","ts_end":"2026-01-27T02:15:05Z","phase":"discovery","cwd":"/path","cmd":"command here","why":"reason tied to gate","exit_code":0,"output_file":"./artifacts/001_output.txt","output_sha256":"<sha256>"}
```
- Insert under SECTION 7 Rules:
```text
- exit_code and output_sha256 are REQUIRED for every entry.
- output_file MUST be produced by redirecting raw stdout+stderr (e.g., "> file 2>&1").
```
- Expected effect: Chain-of-custody becomes auditable.

## P3-STD-06 — Define stability run semantics
- Target: PASS2_STANDARD_PROMPT_DRAFT.md
- Insert under: SECTION 6 Gate Rules
- Insert text:
```text
STABILITY RUN DEFINITION:
- A stability run means executing the verification_script.sh AND the reproduction command, both, end-to-end.
- Each run must produce an artifact with raw output + sha256.
```
- Expected effect: Prevents “run echo ok 3 times” cheating.

## P3-STD-07 — Canonical completion_packet directory
- Target: PASS2_STANDARD_PROMPT_DRAFT.md
- Insert at start of SECTION 14
- Insert text:
```text
COMPLETION PACKET DIRECTORY:
- All artifacts MUST live under one directory: ./completion_packet/
- evidence_manifest.sha256 MUST reference only paths under ./completion_packet/
```
- Expected effect: Prevents cherry-picking/scattering artifacts.

## P3-QA-01 — Unify verdict terminology
- Target: PASS2_QA_PROMPT_DRAFT.md
- Replace in SECTION 9 template:
```text
FINAL VERDICT: [PASS / FAIL / UNPROVEN]
```
- Replace checklist footer:
```text
IF ALL BOXES CHECKED → PASS
IF ANY BOX UNCHECKED → FAIL (specify which)
```
- Expected effect: Eliminates ambiguity.

## P3-QA-02 — Ledger required-field validation matches Standard
- Target: PASS2_QA_PROMPT_DRAFT.md
- Replace Phase 5 required fields bullet with:
```text
- [ ] Required fields present (ts_start, ts_end, phase, cmd, cwd, why, exit_code, output_file, output_sha256)
```
- Expected effect: QA can actually enforce Standard ledger requirements.

## P3-QA-03 — Build identity verification
- Target: PASS2_QA_PROMPT_DRAFT.md
- Insert into Phase 2 checklist:
```text
- [ ] Capture git commit SHA (git rev-parse HEAD) and (if containerized) image digest (docker image inspect) for each critical service
```
- Expected effect: Prevents auditing the wrong binary.

## P3-QA-04 — Ban modification-times as a primary scope detector
- Target: PASS2_QA_PROMPT_DRAFT.md
- Replace Phase 4 “Detect all files changed …” bullet with:
```text
- [ ] Detect all files changed (git diff --name-only if repo is git; otherwise recompute checksum manifests)
```
- Expected effect: Removes forgeable heuristic.

## P3-QA-05 — Negative-test verification_script.sh
- Target: PASS2_QA_PROMPT_DRAFT.md
- Insert into Phase 3 checklist:
```text
- [ ] Negative-test the verification_script.sh itself: introduce a controlled failure (e.g., revert fix) and confirm script exits non-zero.
```
- Expected effect: Catches always-pass scripts.

## P3-QA-06 — Resource variance verification
- Target: PASS2_QA_PROMPT_DRAFT.md
- Insert into Phase 7 checklist:
```text
- [ ] Re-run the resource snapshot command yourself and compare deltas (must be <= 15%)
```
- Expected effect: Turns “15% variance” into an enforceable gate.

## P3-QA-07 — Fresh-clone reproducibility must be executed
- Target: PASS2_QA_PROMPT_DRAFT.md
- Insert into Phase 7 (or new Repro step) checklist:
```text
- [ ] Execute the one-command fresh-clone repro in an empty directory and confirm it reproduces the PASS evidence.
```
- Expected effect: Eliminates “plausible instruction” loophole.

