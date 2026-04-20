# PASS 1 — DECISION GATES (for PASS 2 Merge)

- Generated at (UTC): 2026-01-27T01:23:53Z

## Non-bypassable selection rules (merge gates)
- Non-bypassable > bypassable (if a rule says “non-negotiable / auto-fail / immediate mission failure”, it takes precedence unless impossible).
- Deterministic > subjective (prefer requirements that can be verified by a command + raw output).
- Externally verifiable > self-reported (prefer DB/API/file-hash verification over “I checked”).
- Stricter wins unless it breaks implementability (if two requirements overlap, keep the stricter one unless it blocks all progress).
- Minimize duplication while preserving enforceability (merge repeated rules into one canonical phrasing while keeping all unique obligations).
- Maintain Standard↔QA alignment (every Standard MUST requirement must have a corresponding QA verification step or be flagged as “QA MISSING”).

## Conflict handling rules
- If artifact names differ across prompts, select one canonical name and add an alias mapping (do not drop the evidence requirement).
- If one prompt prohibits an action and another allows it, treat as prohibited unless the allowed action is explicitly scoped and has rollback/evidence requirements.
- If gate sequences differ, choose the sequence with the earliest hard stop + strongest anti-fluke (Red→Green) proof requirements.

## Output hygiene rules
- Every merged requirement must be traceable back to a specific prompt variant + anchor.
- Every “MUST” requirement must be testable (explicit command and expected artifact/output).
- Any non-testable requirement must be downgraded or rewritten in later passes (but not in PASS 1).
