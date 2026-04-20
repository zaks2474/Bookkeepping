# TRIPASS MISSION: Adversarial Review of QUARANTINE-INTELLIGENCE-001

## Why This Investigation Exists

We have a mission prompt (`MISSION-QUARANTINE-INTELLIGENCE-001.md`) that plans to transform the quarantine decision-support experience from "decide blind" to "decide in 3 seconds with full context." The mission was designed by a single agent (Claude Opus 4.6). Before we execute it, we need three independent adversarial perspectives to find:

1. **What can we do better** — improvements, polish, UX patterns the mission missed
2. **What gaps exist** — data that flows through the system but isn't surfaced, operator workflows not considered
3. **What limitations we haven't addressed** — edge cases, failure modes, degradation scenarios
4. **Contrarian thinking** — what would an experienced deal operator push back on? What would a UX designer critique?
5. **Adversarial mindset** — what happens when data is wrong, stale, contradictory, or malicious?

## The Equation

- **Variable 1 (KNOWN):** The problem — operators see "Preview not found" when they click quarantine items. Even when data shows, it's bare: no reasoning, no financials, no broker identity, no entities, no links, no sender reputation.
- **Variable 2 (KNOWN):** The mission prompt — 7 phases, 13 AC, 9 new components, structured extraction_evidence schema, sender intelligence, agent deployment package.
- **Variable 3 (UNKNOWN):** What we're blind to. What would make THIS quarantine experience genuinely world-class? What would a $10M SaaS product do that we haven't thought of?

## Non-Negotiable Constraints

- This is **INVESTIGATION ONLY**: Analyze → Report → Stop.
- Do NOT propose backend changes (the mission explicitly fences those out).
- Do NOT propose database migrations.
- Focus on **dashboard UX, data rendering, operator workflow, decision ergonomics**.
- Every finding MUST reference specific files and line numbers.
- Every recommendation MUST be actionable and concrete.

## Primary Objectives

Each agent should produce findings across these 6 lenses:

### Lens 1: Decision Ergonomics
Can an operator actually make an approve/reject decision in under 3 seconds with this design? What's the cognitive flow? What information hierarchy would a UX expert design? Are the 8 cards in the right priority order? Should some be collapsed by default? What about keyboard shortcuts for rapid triage?

### Lens 2: Data Fidelity & Trust
When extraction_evidence is partially populated, what does the UI show? When confidence is 0.3 vs 0.95, does the UI communicate that difference? Can the operator trust the AI's reasoning? Should there be visual indicators of data quality/completeness? What about conflicting signals (HIGH urgency but LOW confidence)?

### Lens 3: Missing Workflows
The mission focuses on the detail panel. But what about:
- Comparison view (this item vs similar past items that were approved/rejected)?
- Batch triage patterns (5 items from same broker — should they be grouped)?
- Snooze/defer (not approve or reject, but "come back to this")?
- Quick actions without opening detail (approve from list if high confidence)?
- Undo after action (approve → immediately realize mistake)?
- Annotation/notes before deciding?

### Lens 4: Information the Agent Produces but the Mission Doesn't Surface
Read the LangSmith agent's canonical output schema and the bridge tool parameters. Cross-reference with the mission's extraction_evidence schema and the 8 planned components. What data does the agent produce that is NOT captured in extraction_evidence or is captured but NOT rendered?

### Lens 5: Edge Cases & Failure Modes
- What if extraction_evidence is `{}` (empty object)?
- What if extraction_evidence has unknown/unexpected keys?
- What if financials contain contradictory data?
- What if sender intelligence endpoint is slow/down?
- What if there are 200+ items in the queue?
- What if the same email arrives twice with different extraction?
- What about long email bodies (10,000+ chars)?
- What about non-English emails?
- What about HTML-only emails with no plain text?

### Lens 6: World-Class Benchmarks
What do the BEST deal management / email triage / CRM tools do?
- Superhuman (email triage)
- Affinity CRM (deal intelligence)
- DealCloud (M&A workflow)
- Salesforce Lightning (opportunity cards)
- Linear (issue triage with keyboard-first UX)

What patterns from these tools should inform our design?

## Scope

### Files to Read (MANDATORY — every agent must read these)

**The mission prompt being reviewed:**
- `/home/zaks/bookkeeping/docs/MISSION-QUARANTINE-INTELLIGENCE-001.md`

**Current quarantine implementation (the "before"):**
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (lines 170-260 for schemas, lines 940-965 for getQuarantinePreview)

**Backend data model (what's available):**
- `/home/zaks/zakops-agent-api/apps/backend/src/api/orchestration/main.py` (lines 247-286 for QuarantineResponse, lines 1698-1742 for list endpoint, lines 2039-2148 for sender-intelligence)

**Agent injection schema (what the agent sends):**
- `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/server.py` (lines 832-1039 for zakops_inject_quarantine)

**Design system patterns (what we must follow):**
- `/home/zaks/zakops-agent-api/.claude/rules/design-system.md`
- `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` (reference patterns)

**Existing quarantine components:**
- `/home/zaks/zakops-agent-api/apps/dashboard/src/components/quarantine/` (all files)

### Repository Roots
- `/home/zaks/zakops-agent-api` (monorepo)
- `/home/zaks/bookkeeping` (docs)

## Deliverables

Each agent writes their report to the designated output file. The consolidation report should:
1. Rank ALL findings by impact on operator decision speed
2. Group into: MUST-ADD (before execution), SHOULD-ADD (during execution), NICE-TO-HAVE (backlog)
3. For MUST-ADD items, provide specific component/file/line recommendations
4. For each finding, answer: "Does this help the operator decide faster?"

## Success Criteria

The TriPass succeeds if it identifies at least 5 actionable improvements that would materially improve operator decision speed or accuracy, AND provides concrete implementation guidance for each.
