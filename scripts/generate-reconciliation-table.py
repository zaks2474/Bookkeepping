#!/usr/bin/env python3
"""generate-reconciliation-table.py — Produce before/after surface-count tables.

Usage: python3 generate-reconciliation-table.py [--before N] [--after N]

Reads authoritative files and outputs a markdown reconciliation table.
"""
import re
import sys


def count_surfaces_in_file(filepath: str, pattern: str, dedupe: bool = False) -> int:
    """Count surface entries matching pattern in a file."""
    try:
        with open(filepath) as f:
            content = f.read()
            matches = re.findall(pattern, content, re.MULTILINE)
            if dedupe:
                return len(set(matches))
            return len(matches)
    except FileNotFoundError:
        return -1


def main():
    before_count = None
    after_count = None

    # Parse args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--before" and i + 1 < len(args):
            before_count = int(args[i + 1])
            i += 2
        elif args[i] == "--after" and i + 1 < len(args):
            after_count = int(args[i + 1])
            i += 2
        else:
            i += 1

    # Authoritative sources
    sources = {
        "Contract Catalog": {
            "path": "/home/zaks/zakops-agent-api/.claude/rules/contract-surfaces.md",
            "pattern": r"^### Surface \d+:",
        },
        "CLAUDE.md": {
            "path": "/home/zaks/zakops-agent-api/CLAUDE.md",
            "pattern": r"^\| \d+ \|",
        },
        "Unified Validator": {
            "path": "/home/zaks/zakops-agent-api/tools/infra/validate-contract-surfaces.sh",
            "pattern": r"(Surface \d+):",
            "dedupe": True,
        },
        "Manifest": {
            "path": "/home/zaks/zakops-agent-api/INFRASTRUCTURE_MANIFEST.md",
            "pattern": r"^- S\d{1,2} ",
        },
    }

    print("## Surface Count Reconciliation Table")
    print()
    print("| Source | Count | Status |")
    print("|--------|-------|--------|")

    for name, cfg in sources.items():
        count = count_surfaces_in_file(cfg["path"], cfg["pattern"], cfg.get("dedupe", False))
        if count == -1:
            status = "FILE MISSING"
        elif after_count and count == after_count:
            status = "OK"
        elif count > 0:
            status = "OK" if after_count is None else f"MISMATCH (expected {after_count})"
        else:
            status = "EMPTY"
        print(f"| {name} | {count} | {status} |")

    print()

    if before_count is not None and after_count is not None:
        print(f"**Transition:** {before_count} -> {after_count} surfaces")
    elif after_count is not None:
        print(f"**Expected:** {after_count} surfaces")


if __name__ == "__main__":
    main()
