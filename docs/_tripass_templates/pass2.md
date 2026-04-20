# TriPass — Pass 2: Cross-Review and Deduplication

## Agent Identity
**Agent**: {{AGENT_NAME}}
**Run ID**: {{RUN_ID}}
**Pipeline Mode**: {{MODE}}
**Timestamp**: {{TIMESTAMP}}

---

## Mission (Original)

{{MISSION_DESCRIPTION}}

---

## Pass 1 Reports

You have access to all three Pass 1 reports:

### Report A ({{AGENT_A_NAME}})
{{PASS1_REPORT_A}}

### Report B ({{AGENT_B_NAME}})
{{PASS1_REPORT_B}}

### Report C ({{AGENT_C_NAME}})
{{PASS1_REPORT_C}}

---

## Instructions

You are reviewing all three independent investigation reports. Your job is to:

1. **Identify duplicates** — findings that multiple agents reported (high confidence items)
2. **Identify conflicts** — findings where agents disagree on root cause or fix approach
3. **Identify unique findings** — items only one agent found (potential blind spot coverage)
4. **Verify evidence** — check that cited file:line references are accurate
5. **Flag drift** — note any findings that fall outside the declared mission scope

### Output Format

Write your cross-review to: `{{OUTPUT_FILE}}`

Begin with exactly this header:

```
# Pass 2 Cross-Review — {{AGENT_NAME}}
## Run: {{RUN_ID}} | Mode: {{MODE}}
## Generated: {{TIMESTAMP}}
```

Then organize as:

```
## DUPLICATES (High Confidence)
Items found by 2+ agents. Merge into a single entry with attribution.

### D-1: [Merged Title]
**Reported by:** Agent A (Finding X), Agent B (Finding Y)
**Consensus root cause:** ...
**Consensus fix:** ...
**Evidence verified:** YES/NO

(repeat)

## CONFLICTS
Items where agents disagree. State both positions with evidence.

### C-1: [Conflict Title]
**Agent A position:** ...
**Agent B position:** ...
**Evidence comparison:** ...
**Recommended resolution:** ...

(repeat)

## UNIQUE FINDINGS
Items found by only one agent. Verify if the finding is valid.

### U-1: [Title] (from Agent X)
**Verification:** CONFIRMED / UNVERIFIED / INVALID
**Evidence check:** ...
**Should include in final:** YES / NO (with reason)

(repeat)

## DRIFT FLAGS
Findings that fall outside declared scope.

### DRIFT-1: [Title] (from Agent X)
**Why out of scope:** ...
**Severity if ignored:** ...

## SUMMARY
- Duplicates: N
- Conflicts: N
- Unique valid findings: N
- Drift items: N
- Overall assessment: ...
```
