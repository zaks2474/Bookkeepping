# TriPass — Pass 1: Independent Investigation

## Agent Identity
**Agent**: {{AGENT_NAME}}
**Run ID**: {{RUN_ID}}
**Pipeline Mode**: {{MODE}}
**Timestamp**: {{TIMESTAMP}}

---

## Mission

{{MISSION_DESCRIPTION}}

## Scope

{{SCOPE}}

## Repository Roots

{{REPO_ROOTS}}

## Known Issues or Constraints

{{CONSTRAINTS}}

---

## Instructions

You are one of three independent investigators analyzing this mission. Your report will be cross-reviewed by two other agents in Pass 2. No other agent can see your work during this pass.

### Investigation Protocol

1. **Read first, opine second.** Read every relevant file before forming conclusions. Cite file paths and line numbers for every claim.
2. **Stay in scope.** If you discover issues outside the declared mission scope, place them in the ADJACENT OBSERVATIONS section — never mix them with primary findings.
3. **Structure every finding** with these 5 required fields:
   - **(1) Confirmed Root Cause** — What is the actual problem, with file:line evidence?
   - **(2) Permanent Fix Approach** — What specific change resolves it?
   - **(3) Industry Standard / Best Practice** — What standard or pattern does this align with?
   - **(4) Why It Fits This System** — Why is this the right fix for THIS codebase specifically?
   - **(5) Never-Again Enforcement** — What gate, lint rule, hook, or test prevents recurrence?
4. **Be concrete.** "The middleware should validate input" is not a finding. "middleware.ts:47 accepts unsanitized query params — add zod schema validation" is a finding.

### Output Format

Write your report to: `{{OUTPUT_FILE}}`

Begin your report with exactly this header:

```
# Pass 1 Report — {{AGENT_NAME}}
## Run: {{RUN_ID}} | Mode: {{MODE}}
## Generated: {{TIMESTAMP}}
```

Then organize findings as:

```
## PRIMARY FINDINGS

### Finding 1: [Title]
**Root Cause:** ...
**Fix Approach:** ...
**Industry Standard:** ...
**System Fit:** ...
**Enforcement:** ...

### Finding 2: ...
(repeat for each finding)

## ADJACENT OBSERVATIONS
(out-of-scope items go here, clearly labeled)

## SUMMARY
- Total primary findings: N
- Total adjacent observations: N
- Confidence level: HIGH / MEDIUM / LOW
- Key recommendation: (one sentence)
```
