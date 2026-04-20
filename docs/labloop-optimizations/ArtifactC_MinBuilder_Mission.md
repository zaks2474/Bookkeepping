# Minimal Builder Mission: Apply Lab Loop Optimizations

**Goal:** Apply the optimization patch pack to `labloop.sh` to improve token economy, metrics, and reliability.

**Instructions:**
1.  **Apply the Patch:**
    - Read the unified diff at `/home/zaks/bookkeeping/docs/labloop-optimizations/ArtifactB_Builder_PatchPack.diff`.
    - Apply it to `/home/zaks/bookkeeping/labloop/bin/labloop.sh`.
    - Ensure all changes are applied correctly, specifically:
        - `BUNDLE_MODE` variable and CLI parsing.
        - `compose_builder_bundle` logic for condensed prompts.
        - `measure_gate_duration` function and calls.
        - `run_qa_requested_commands` function and calls.
        - `check_stuck` logic update (consecutive counter).

2.  **Verify:**
    - Run `chmod +x /home/zaks/bookkeeping/labloop/bin/labloop.sh`.
    - Ensure the script syntax is valid (no syntax errors).

**Output:**
- Confirm the file has been patched.
- Run a quick syntax check: `bash -n /home/zaks/bookkeeping/labloop/bin/labloop.sh`.