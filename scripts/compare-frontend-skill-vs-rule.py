#!/usr/bin/env python3
"""compare-frontend-skill-vs-rule.py — Compare frontend-design skill with Category B rule sections.

Usage: python3 compare-frontend-skill-vs-rule.py

Produces a report showing which Category B topics from design-system.md
are also covered in the frontend-design SKILL.md, and vice versa.
"""
import re
import sys


def extract_headings(filepath: str) -> list[str]:
    """Extract markdown headings from a file."""
    headings = []
    try:
        with open(filepath) as f:
            for line in f:
                match = re.match(r'^#{1,4}\s+(.+)', line.strip())
                if match:
                    headings.append(match.group(1).strip())
    except FileNotFoundError:
        return []
    return headings


def extract_keywords(filepath: str) -> set[str]:
    """Extract significant keywords from a file."""
    keywords = set()
    stopwords = {'the', 'a', 'an', 'is', 'are', 'and', 'or', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'not', 'no', 'use', 'do', 'should', 'must', 'can', 'may',
                 'will', 'be', 'it', 'this', 'that', 'from', 'by', 'as', 'if', 'when'}
    try:
        with open(filepath) as f:
            for line in f:
                words = re.findall(r'\b[a-z]{4,}\b', line.lower())
                for w in words:
                    if w not in stopwords:
                        keywords.add(w)
    except FileNotFoundError:
        pass
    return keywords


def main():
    rule_file = "/home/zaks/zakops-agent-api/.claude/rules/design-system.md"
    skill_file = "/home/zaks/.claude/skills/frontend-design/SKILL.md"

    print("=== Frontend Skill vs Rule Comparison ===")
    print()
    print(f"Rule: {rule_file}")
    print(f"Skill: {skill_file}")
    print()

    rule_headings = extract_headings(rule_file)
    skill_headings = extract_headings(skill_file)

    print(f"Rule headings: {len(rule_headings)}")
    print(f"Skill headings: {len(skill_headings)}")
    print()

    # Category B headings from design-system.md
    cat_b = [h for h in rule_headings if re.match(r'B\d\.', h)]
    print("## Category B Coverage in design-system.md")
    print()
    print("| Section | In Rule | In Skill |")
    print("|---------|---------|----------|")

    rule_keywords = extract_keywords(rule_file)
    skill_keywords = extract_keywords(skill_file)

    for heading in cat_b:
        # Check if key words from heading appear in skill
        words = set(re.findall(r'\b[a-z]{4,}\b', heading.lower()))
        in_skill = "Yes" if words & skill_keywords else "No"
        print(f"| {heading} | Yes | {in_skill} |")

    print()

    # Keyword overlap
    overlap = rule_keywords & skill_keywords
    rule_only = rule_keywords - skill_keywords
    skill_only = skill_keywords - rule_keywords

    print("## Keyword Analysis")
    print(f"- Shared keywords: {len(overlap)}")
    print(f"- Rule-only keywords: {len(rule_only)}")
    print(f"- Skill-only keywords: {len(skill_only)}")
    print()

    # Top unique keywords
    print("### Top rule-only keywords (sample)")
    for kw in sorted(rule_only)[:10]:
        print(f"  - {kw}")

    print()
    print("### Top skill-only keywords (sample)")
    for kw in sorted(skill_only)[:10]:
        print(f"  - {kw}")

    print()
    print("Skill vs Rule Comparison: DONE")


if __name__ == "__main__":
    main()
