#!/usr/bin/env python3
"""check-ac-coverage.py — Compare mission AC list with completion report AC claims.

Usage: python3 check-ac-coverage.py <mission_file> <completion_file>
"""
import re
import sys


def extract_acs(filepath: str) -> set[str]:
    """Extract AC-N patterns from a file."""
    acs = set()
    try:
        with open(filepath) as f:
            for line in f:
                matches = re.findall(r'AC-(\d+)', line)
                for m in matches:
                    acs.add(f"AC-{m}")
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    return acs


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 check-ac-coverage.py <mission_file> <completion_file>")
        print("Example: python3 check-ac-coverage.py docs/MISSION-X.md docs/X-COMPLETION.md")
        sys.exit(1)

    mission_file = sys.argv[1]
    completion_file = sys.argv[2]

    print("=== AC Coverage Check ===")
    print(f"Source: {mission_file}")
    print(f"Completion: {completion_file}")
    print()

    source_acs = extract_acs(mission_file)
    completion_acs = extract_acs(completion_file)

    print(f"Source ACs: {len(source_acs)} ({', '.join(sorted(source_acs, key=lambda x: int(x.split('-')[1])))})")
    print(f"Completion ACs: {len(completion_acs)} ({', '.join(sorted(completion_acs, key=lambda x: int(x.split('-')[1])))})")
    print()

    missing = source_acs - completion_acs
    extra = completion_acs - source_acs

    exit_code = 0

    if missing:
        print(f"MISSING from completion ({len(missing)}):")
        for ac in sorted(missing, key=lambda x: int(x.split('-')[1])):
            print(f"  - {ac}")
        exit_code = 1
    else:
        print("PASS: All source ACs present in completion report")

    if extra:
        print(f"\nEXTRA in completion ({len(extra)}):")
        for ac in sorted(extra, key=lambda x: int(x.split('-')[1])):
            print(f"  - {ac}")

    print()
    if exit_code == 0:
        print(f"AC Coverage: PASS ({len(source_acs)}/{len(source_acs)} covered)")
    else:
        print(f"AC Coverage: FAIL ({len(source_acs) - len(missing)}/{len(source_acs)} covered)")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
