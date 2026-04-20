# TriPass — Pass 3: Consolidation

## Agent Identity
**Agent**: {{AGENT_NAME}} (Consolidator)
**Run ID**: {{RUN_ID}}
**Pipeline Mode**: {{MODE}}
**Timestamp**: {{TIMESTAMP}}

---

## Mission (Original)

{{MISSION_DESCRIPTION}}

---

## All Prior Outputs

You have access to:
- 3 Pass 1 independent reports (in 01_pass1/)
- 3 Pass 2 cross-reviews (in 02_pass2/)
- The shared WORKSPACE.md with all appended outputs

Your job is to produce a single, deduplicated master document that:
1. Preserves every unique finding (nothing silently dropped)
2. Merges duplicates with attribution to all originating agents
3. Resolves conflicts with evidence (pick the position with stronger evidence)
4. Structures the output as a builder-ready mission prompt with gates
5. Excludes drift items from primary findings (log them in a separate section)

---

## Consolidation Rules

- **No silent drops.** Every finding from every Pass 1 report must appear in the master as either:
  - A primary finding (included)
  - A merged item (deduplicated, with all source attributions)
  - An explicitly discarded item (with documented reason in DISCARDED section)
- **Evidence required.** Every primary finding must cite file:line evidence
- **All 5 fields required.** Every finding must have: root cause, fix approach, industry standard, system fit, enforcement mechanism
- **Builder-ready gates.** The master must include enforceable acceptance gates that a builder agent can run to verify completion

---

## Output Format

Write the consolidated master to: `{{OUTPUT_FILE}}`

Begin with exactly this header:

```
# FINAL MASTER — {{RUN_ID}}
## Mode: {{MODE}}
## Generated: {{TIMESTAMP}}
## Sources: 3 Pass 1 reports + 3 Pass 2 cross-reviews
```

Then organize as:

```
## MISSION
(brief restatement of mission objective)

## CONSOLIDATED FINDINGS

### F-1: [Title]
**Sources:** Agent A (P1-F3), Agent B (P1-F1)
**Root Cause:** ...
**Fix Approach:** ...
**Industry Standard:** ...
**System Fit:** ...
**Enforcement:** ...

(repeat for each consolidated finding, numbered F-1 through F-N)

## DISCARDED ITEMS
Items from Pass 1 that were intentionally excluded, with reasons.

### DISC-1: [Title] (from Agent X, Finding Y)
**Reason for exclusion:** ...

## DRIFT LOG
Out-of-scope items flagged by cross-reviews. Not actionable in this mission.

## ACCEPTANCE GATES
Builder-enforceable gates for implementing the findings above.

### Gate 1: [Gate Name]
**Command:** ...
**Pass criteria:** ...

(repeat)

## STATISTICS
- Total Pass 1 findings across all agents: N
- Deduplicated primary findings: N
- Discarded (with reason): N
- Drift items: N
- Drop rate: 0% (all findings accounted for)
```
