#!/usr/bin/env python3
"""Hook contract validator for Claude Code settings.json (ENH-2).

Validates:
- Required hook events are present
- Contract semantics (matcher, timeout, async, command path existence)
- Exit code semantics (no exit 1 in hook scripts)

Exit 0 = valid, Exit 1 = invalid.
"""

import json
import os
import re
import sys

SETTINGS_PATH = os.environ.get(
    "CLAUDE_SETTINGS_PATH", "/home/zaks/.claude/settings.json"
)

REQUIRED_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "SessionStart",
    "Stop",
    "PreCompact",
    "TaskCompleted",
}

# Contract requirements for specific hooks
CONTRACTS = {
    "PreCompact": {
        "matcher": "",
        "async": True,
        "timeout_max": 30,
    },
    "TaskCompleted": {
        "matcher": "",
        "timeout_max": 60,
    },
    "SessionStart:compact": {
        "matcher": "compact",
        "timeout_max": 30,
    },
}

errors = []
warnings = []


def check(condition, msg, warn_only=False):
    if not condition:
        if warn_only:
            warnings.append(f"WARN: {msg}")
        else:
            errors.append(f"FAIL: {msg}")
        return False
    return True


def main():
    # Load settings
    if not os.path.isfile(SETTINGS_PATH):
        print(f"FAIL: Settings file not found: {SETTINGS_PATH}")
        sys.exit(1)

    with open(SETTINGS_PATH, "r") as f:
        settings = json.load(f)

    hooks = settings.get("hooks", {})

    # Check required events
    present_events = set(hooks.keys())
    missing = REQUIRED_EVENTS - present_events
    check(
        len(missing) == 0,
        f"Missing required hook events: {missing}",
    )

    # Validate each hook entry
    for event, entries in hooks.items():
        for i, entry in enumerate(entries):
            matcher = entry.get("matcher", "")
            hook_list = entry.get("hooks", [])

            check(
                len(hook_list) > 0,
                f"{event}[{i}] has no hooks defined",
            )

            for j, hk in enumerate(hook_list):
                cmd = hk.get("command", "")
                timeout = hk.get("timeout")

                # Command path must exist
                check(
                    os.path.isfile(cmd),
                    f"{event}[{i}].hooks[{j}] command not found: {cmd}",
                )

                # Timeout must be positive
                if timeout is not None:
                    check(
                        timeout > 0,
                        f"{event}[{i}].hooks[{j}] timeout must be positive: {timeout}",
                    )

    # Validate specific contracts
    # PreCompact
    if "PreCompact" in hooks:
        pc = hooks["PreCompact"][0]
        pc_hook = pc["hooks"][0]
        check(pc.get("matcher", "") == "", "PreCompact matcher must be empty")
        check(
            pc_hook.get("async", False) is True,
            "PreCompact must be async=true",
        )
        check(
            pc_hook.get("timeout", 0) <= 30,
            f"PreCompact timeout ({pc_hook.get('timeout')}) exceeds max 30",
        )

    # TaskCompleted
    if "TaskCompleted" in hooks:
        tc = hooks["TaskCompleted"][0]
        tc_hook = tc["hooks"][0]
        check(tc.get("matcher", "") == "", "TaskCompleted matcher must be empty")
        check(
            tc_hook.get("timeout", 0) <= 60,
            f"TaskCompleted timeout ({tc_hook.get('timeout')}) exceeds max 60",
        )

    # SessionStart compact
    if "SessionStart" in hooks:
        compact_entries = [e for e in hooks["SessionStart"] if e.get("matcher") == "compact"]
        check(
            len(compact_entries) == 1,
            f"Expected exactly 1 SessionStart compact entry, found {len(compact_entries)}",
        )
        if compact_entries:
            sc_hook = compact_entries[0]["hooks"][0]
            check(
                sc_hook.get("timeout", 0) <= 30,
                f"SessionStart(compact) timeout ({sc_hook.get('timeout')}) exceeds max 30",
            )

    # Exit code semantics: no exit 1 in hook scripts
    for event, entries in hooks.items():
        for entry in entries:
            for hk in entry.get("hooks", []):
                cmd = hk.get("command", "")
                if os.path.isfile(cmd) and cmd.endswith(".sh"):
                    with open(cmd, "r") as f:
                        content = f.read()
                    # Match "exit 1" that is not in a comment
                    for line_num, line in enumerate(content.splitlines(), 1):
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            continue
                        if re.search(r"\bexit\s+1\b", stripped):
                            check(
                                False,
                                f"{cmd}:{line_num} uses 'exit 1' (must use exit 0 or exit 2)",
                            )

    # Report
    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    total_checks = len(errors) + len(warnings)
    passed = total_checks - len(errors)

    if errors:
        print(f"\nHook contract validation FAILED: {len(errors)} error(s)")
        sys.exit(1)
    else:
        print(f"Hook contract validation PASSED ({6 + len(hooks)} checks)")
        sys.exit(0)


if __name__ == "__main__":
    main()
