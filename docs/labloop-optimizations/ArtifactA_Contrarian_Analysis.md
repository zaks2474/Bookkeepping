# Artifact A: Contrarian Analysis & Optimization Report
**Version:** 1.1.0 (Post-Configuration Analysis)
**Date:** 2026-01-24
**Scope:** Lab Loop v2.1.2 Optimization

## 1. Executive Summary: The "Working but Wasteful" Trap

The configuration analysis confirms Lab Loop is rigorous (high strictness on gates/safety) but **inefficient** (medium strictness on builder behavior, no metrics, high token waste). The system correctly identifies "BLOCKERS first" but fails to enforce *how* the Builder fixes them or *if* it verifies them before reporting.

**Key Insight:** We are paying for "Verification Theater." The Builder claims `READY_FOR_QA`, but the Orchestrator trusts this claim blindly, only to have the QA agent spend tokens to find out the code is broken.

## 2. Critical Inefficiencies Identified

### 2.1 Token Hemorrhage in Builder Bundle (Confirmed)
**Analysis:** The `compose_builder_bundle` function dumps the *entire* `QA_REPORT.json` (often 50KB+) and full mission docs into the prompt every cycle.
**Critique:** By cycle 10, the Builder has seen the mission 9 times. It only needs the *delta*—what failed in the last cycle.
**Optimization:** Implement `CONDENSED_MODE` for cycles > 1. Send only `verdict`, `blockers`, `majors`, and `next_actions_for_builder`.

### 2.2 The "Hash-Only" Stuck Trap (Confirmed)
**Analysis:** Stuck detection relies solely on `sha256sum "$TASK_DIR/QA_REPORT.json"`.
**Critique:** This is brittle. A Builder might make valid progress (changing files) but the QA report text might remain statistically similar (or identical if the QA agent is deterministic and the error persists).
**Optimization:** Implement "Smart Stuck" logic: `STUCK` only if `hash_unchanged` AND `file_changes == 0` for `N` consecutive cycles.

### 2.3 Verification Theater (Validated by Config Analysis)
**Analysis:** The Config Analysis notes: "⚠️ No requirement to verify fix actually worked before reporting".
**Critique:** This is the single biggest source of churn. A Builder that doesn't run the gate is just guessing.
**Optimization:** Enforce a "Gate Pre-Check". If `gate_pre_check.ran_gate` is false in the Builder's JSON output, the Orchestrator should auto-reject or downgrade confidence *before* running QA.

### 2.4 The Blind Spot: Time & Cost Metrics (Validated)
**Analysis:** "Gap: No time tracking... Can't measure efficiency".
**Critique:** We don't know if a cycle took 2 minutes or 20. We don't know if the bottleneck is vLLM, the Builder, or the Gate.
**Optimization:** Add explicit start/end timestamps and duration calculation for each phase (Builder, Gate, QA), logging to `metrics.json`.

### 2.5 QA Read-Only Handcuffs (Validated)
**Analysis:** "QA can't run commands... Limited verification ability".
**Critique:** QA is blind to runtime state (e.g., "did the service actually start?").
**Optimization:** Introduce `run_qa_requested_commands`. QA can't *execute* arbitrary commands, but the Orchestrator can run a safe allowlist (`ls`, `grep`, `git status`) and provide the output to QA.

## 3. Proposed Architecture Changes

1.  **Modify `labloop.sh`**:
    *   Add `BUNDLE_MODE` (condensed vs full).
    *   Enhance `check_stuck` with `STUCK_CONSECUTIVE_CYCLES` and file-change awareness.
    *   Add `measure_duration` wrappers around agent calls.
    *   Implement `run_qa_requested_commands` (auto-collection of evidence).

2.  **Modify `builder_protocol.txt`**:
    *   Explicitly mandate "RUN VERIFICATION COMMANDS" as step #1 before reporting.

3.  **New Artifacts**:
    *   `_builder_duration.txt`, `_gate_duration.txt`, `_qa_duration.txt` for metrics.
    *   `qa_evidence_cycle_N.txt` for auto-collected system state.

## 4. Conclusion

The "Config Analysis" was spot on: we have high rigor but low efficiency. These patches will align the implementation with the desired "High Strictness" state for Builder behavior and Loop Control.