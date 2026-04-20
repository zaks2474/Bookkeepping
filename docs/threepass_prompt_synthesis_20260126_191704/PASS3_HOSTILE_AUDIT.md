# PASS 3 — HOSTILE AUDIT (BREAK THE DRAFTS)

- Run directory: /home/zaks/bookkeeping/docs/threepass_prompt_synthesis_20260126_191704
- Generated at (UTC): 2026-01-27T01:48:14Z
- Inputs audited (read-only):
  - PASS2_STANDARD_PROMPT_DRAFT.md
  - PASS2_QA_PROMPT_DRAFT.md
  - PASS2_COMPLIANCE_MAP.md

## 1) Top 25 Issues (ranked)

Severity definitions:
- **BLOCKER**: Enables cheating / makes audit non-deterministic / prevents reliable PASS.
- **MAJOR**: High risk of drift or unverifiable “passes.”
- **MINOR**: Tightening/clarity; not existential.

### BLOCKER-01 — Unfilled placeholders not fail-closed (mission inputs can be empty)
- Where: **Standard** → SECTION 4: MISSION INPUTS
- Why: A Builder can leave `{{...}}` placeholders (or omit critical ports/log paths/scope) and still “proceed,” making every later gate ungrounded.
- Exact patch wording:
  - **ADD** under SECTION 4 (or Gate 0):
    ```text
    PLACEHOLDER HARD-FAIL:
    - Before Gate 0, you MUST prove there are zero unresolved template tokens in the mission prompt and artifacts.
    - Any occurrence of "{{" or "}}" in inputs/artifacts = IMMEDIATE FAIL (do not proceed).
    ```
- Test that proves the patch closes the loophole:
  - QA runs: `rg -n "\{\{|\}\}" ./completion_packet -S` and expects **0 matches**.

### BLOCKER-02 — Negative test loophole: “Red” can be unrelated to the original bug
- Where: **Standard** → SECTION 2 (NEGATIVE TEST) + SECTION 5 PHASE 4
- Why: Builder can “Force Red” by running an unrelated failing command (e.g., `false`) and claim Red→Green without ever reproducing the original failure signature.
- Exact patch wording:
  - **REPLACE** SECTION 2, item 5 with:
    ```text
    5. NEGATIVE TEST (Red-to-Green):
       - The Red step MUST reproduce the original failure mode (same Error Signature OR same failing reproduction command).
       - "Red" that does not include the Error Signature (or does not fail the reproduction command) is INVALID.
       - The Restore step MUST be re-applying the exact fix (or reverting the revert of the fix).
    ```
- Test that proves the patch closes the loophole:
  - QA checks Red evidence output contains the Error Signature string **or** shows the reproduction command exited non-zero.

### BLOCKER-03 — Scope integrity checksums are incorrect/incomplete (easy to bypass)
- Where: **Standard** → SECTION 8: CODE INTEGRITY
- Why:
  - Only hashes `*.ts`/`*.tsx` (misses other file types).
  - `find ... -type f -name "*.ts" -o -name "*.tsx"` precedence is wrong (can hash unintended paths).
  - Not safe for filenames with spaces.
  - Does not produce any proof about files *outside* approved scope.
- Exact patch wording:
  - **REPLACE** pre/post commands with (GNU tools):
    ```text
    # Pre-Change (Required)
    find {{APPROVED_SCOPE}} -type f -print0 | sort -z | xargs -0 sha256sum > pre_change_checksums.txt

    # Post-Change (Required)
    find {{APPROVED_SCOPE}} -type f -print0 | sort -z | xargs -0 sha256sum > post_change_checksums.txt

    # Verification
    diff -u pre_change_checksums.txt post_change_checksums.txt || true
    ```
  - **ADD** immediately after Verification:
    ```text
    OUT-OF-SCOPE CHANGE DETECTION:
    - You MUST also provide a changed-files list for the whole repo (git diff --name-only if git; otherwise a full-tree checksum manifest).
    - Any changed file outside {{APPROVED_SCOPE_LIST}} = IMMEDIATE FAIL + rollback proof.
    ```
- Test that proves the patch closes the loophole:
  - QA creates a file with spaces inside scope and confirms it appears in checksums.
  - QA modifies a non-TS file inside scope and confirms the checksum diff reflects it.

### BLOCKER-04 — Ledger is under-specified for anti-fake chain-of-custody; QA doesn’t validate required fields
- Where: **Standard** → SECTION 7 ledger schema; **QA** → Phase 5 required fields
- Why:
  - Standard ledger example lacks `exit_code` and hash of output artifact.
  - QA Phase 5 only lists `ts, phase, cmd, why` (missing `cwd` + `output_file` required by Standard).
  - This permits fabricated ledgers and missing output capture.
- Exact patch wording:
  - **Standard: REPLACE** ledger example with:
    ```json
    {"ts_start":"...","ts_end":"...","phase":"...","cwd":"...","cmd":"...","why":"...","exit_code":0,"output_file":"...","output_sha256":"..."}
    ```
  - **Standard: ADD** under SECTION 7 Rules:
    ```text
    - exit_code and output_sha256 are REQUIRED for every entry.
    - output_file MUST be produced by redirecting raw stdout+stderr (e.g., "> file 2>&1").
    ```
  - **QA: ADD** to Phase 5 checklist:
    ```text
    - [ ] Required fields present (ts_start, ts_end, phase, cmd, cwd, why, exit_code, output_file, output_sha256)
    ```
- Test that proves the patch closes the loophole:
  - QA runs a schema validator over `ledger.jsonl` and fails if any field is missing.

### BLOCKER-05 — QA verdict terminology contradicts itself (PASS/FAIL vs APPROVED/REJECTED)
- Where: **QA** → SECTION 6/7 vs SECTION 9 template (“APPROVED / REJECTED”) and checklist footer (“APPROVED”)
- Why: This creates ambiguity and can be exploited to “pass” despite failing criteria by shifting language.
- Exact patch wording:
  - **QA: REPLACE** template line:
    ```text
    FINAL VERDICT: [PASS / FAIL / UNPROVEN]
    ```
  - **QA: REPLACE** checklist footer:
    ```text
    IF ALL BOXES CHECKED → PASS
    IF ANY BOX UNCHECKED → FAIL (specify which)
    ```
- Test that proves the patch closes the loophole:
  - QA runs a report lint: no occurrence of `APPROVED`/`REJECTED` in final output.

### BLOCKER-06 — Resource variance requirement is not operationalized (15% can be faked)
- Where: **Standard** → SECTION 4 thresholds + SECTION 14 `resource_snapshot.txt`; **QA** does not enforce measurement
- Why: “Within 15%” is meaningless without a mandated measurement method; Builder can fabricate numbers.
- Exact patch wording:
  - **Standard: ADD** under SECTION 14 item 4:
    ```text
    resource_snapshot.txt MUST include:
    - Baseline timestamp + verification timestamp
    - Command used (e.g., ps/pidstat/docker stats)
    - Raw outputs for the same PIDs/containers
    - A computed delta% with the formula shown
    ```
  - **QA: ADD** to Phase 7:
    ```text
    - [ ] Re-run the resource snapshot command yourself and compare deltas (must be <= 15%)
    ```
- Test that proves the patch closes the loophole:
  - QA re-runs the resource command; mismatch => FAIL.

### BLOCKER-07 — Service “build identity” is required by Standard but not checked by QA
- Where: **Standard** → SECTION 9 (“git commit SHA and container image digest”)
- Why: Builder can run a different build than claimed; without verifying commit/digest, audit can certify the wrong binary.
- Exact patch wording:
  - **QA: ADD** to Phase 2:
    ```text
    - [ ] Capture git commit SHA (git rev-parse HEAD) and (if containerized) image digest (docker image inspect) for each critical service
    - [ ] Include these in the audit report with evidence pointers
    ```
- Test that proves the patch closes the loophole:
  - QA records SHA/digest; then rebuilds a service to produce a new digest and confirms mismatch is flagged.

### BLOCKER-08 — “3-run stability” gate is undefined (what exactly is run 3 times?)
- Where: **Standard** → SECTION 6: Gate Rules (3-RUN STABILITY)
- Why: Builder can satisfy by running any trivial command 3 times.
- Exact patch wording:
  - **Standard: ADD** under SECTION 6:
    ```text
    STABILITY RUN DEFINITION:
    - A stability run means executing the verification_script.sh AND the reproduction command, both, end-to-end.
    - Each run must produce an artifact with raw output + sha256.
    ```
- Test that proves the patch closes the loophole:
  - QA checks 3 (or 5) distinct run artifacts exist and include both commands.

## 1b) Additional Issues (compact)

| ID | Title | Where | Why it matters |
|---|---|---|---|
| MAJOR-09 | Completion Packet location unspecified | Standard SECTION 14 | Artifacts can be scattered / swapped; enforce ./completion_packet/ root + manifest path constraints. |
| MAJOR-10 | Evidence output capture not mechanically enforced | Standard SECTION 2 | Require stdout+stderr redirection to output_file + wc/head/tail + QA re-run comparison. |
| MAJOR-11 | Dependency freeze bypass via other package managers | Standard SECTION 3 | Expand command ban coverage (pnpm/yarn/brew/poetry/uv/etc). |
| MAJOR-12 | “No new patterns” too vague | Standard SECTION 3 | Add auditable definitions (new deps/new subsystems). |
| MAJOR-13 | QA trusts pasted transcript too much | QA SECTION 3 | Treat transcript as advisory; ledger/artifacts are primary sources; discrepancies = FAIL. |
| MAJOR-14 | QA allows modification times as change detector | QA Phase 4 | Require git diff or checksum recomputation; mtimes are forgeable. |
| MAJOR-15 | HAR/console existence checks without content validation | QA Phase 1/2 | Validate host/URLs/timestamps/expected endpoints in HAR. |
| MAJOR-16 | Log absence proof can point to wrong log | Standard SECTION 11 | Require baseline shows signature existed in same log source. |
| MAJOR-17 | Idempotency definition vague | Standard SECTION 12 | Define idempotency as clean git diff (or checksum diff) after second run. |
| MAJOR-18 | verification_script.sh can be always-pass | QA Phase 3 | QA must negative-test the script by reverting fix and expecting non-zero exit. |
| MAJOR-19 | Fresh-clone reproducibility not executed | Standard SECTION 14 / QA | QA must run the fresh-clone one-command repro and capture output. |
| MAJOR-20 | Bisection requirement lacks artifact proof | Standard SECTION 13 | Require bisect logs or manual bisection notes as artifacts when triggered. |
| MAJOR-21 | Service identity missing PPID in QA | Standard SECTION 9 / QA Phase 2 | QA must capture PID+PPID+exe+sha256. |
| MINOR-22 | Forbidden ports not forced as Gate 0 check | Standard SECTION 4/13 | Make forbidden port scan an explicit Gate 0 requirement. |
| MINOR-23 | “No sed” ban too strict | Standard SECTION 5 | Ban only in-place edits (sed -i), allow read-only usage. |
| MINOR-24 | UI artifacts forced for non-UI tasks | Standard SECTION 2 | Allow Channel A = N/A with alternate independent evidence. |
| MINOR-25 | Compliance map self-certification | Compliance Map + QA Prime Directive | QA must treat summaries as advisory only; rely on independent checks. |

---

## 2) Coverage Failures (Standard hard rules not actually verified by QA as written)

These are requirements present in PASS2_STANDARD_PROMPT_DRAFT.md that are not explicitly verified by PASS2_QA_PROMPT_DRAFT.md (or are only implied/handwavy):

1. **Ledger required fields include `cwd` + `output_file`** (Standard SECTION 7) — QA Phase 5 lists fewer required fields.
2. **Build identity (git SHA + image digest)** (Standard SECTION 9) — QA does not require capturing/validating this.
3. **Resource variance <= 15%** (Standard SECTION 4/14) — QA does not define how to measure/verify.
4. **Incognito + cleared storage + hard reload** (Standard SECTION 10) — QA references cache clearing via headers, but not the full browser conditions.
5. **Bisection artifacts** when 2-strike rollback triggers (Standard SECTION 13) — QA does not require artifacts/logs.

---

## 3) “Fakeability” Map (Top 10 easiest-to-fake proofs still remaining)

For each item: **what’s fakeable** → **patch text to harden**.

1. **ledger.jsonl** → Require `exit_code` + `output_sha256` per line; QA validates schema + cross-checks with output files.
2. **verification_script.sh** → QA must negative-test the script by reverting the fix and confirming non-zero exit.
3. **resource_snapshot.txt** → Standard mandates raw command output + delta math; QA re-runs same command.
4. **HAR files** → QA validates host/URLs and captures their own HAR for comparison.
5. **Console captures** → QA validates timestamps/URLs; require capture command/source.
6. **diff.patch** → QA applies patch to clean tree and runs verification to ensure it reproduces.
7. **Pre/post checksums** → QA recomputes checksums and compares to provided files.
8. **Log “absence” grep** → Require baseline grep proof (same log source contained signature before fix).
9. **Service identity chain** → QA must compute PID/PPID/exe/sha256 themselves; not accept builder-provided only.
10. **UI interaction proof** → Require deterministic evidence: recorded steps + HAR showing request→response→UI change.
