# TriPass — Pass 1: Independent Investigation

## Agent Identity
**Agent**: CODEX
**Run ID**: TP-20260213-163446
**Pipeline Mode**: forensic
**Timestamp**: 2026-02-13T16:34:47Z

---

## Mission

# FORENSIC AUDIT MISSION — INTAKE → QUARANTINE → DEALS (SOURCE-OF-TRUTH + REAL-LIFE DATA PIPELINE)

## Why this audit exists
We've made major progress aligning the system, but we have NOT recently audited the "real-life data" entry point:
- How opportunities enter the system (email/MCP/watchers/ingestion)
- Where Quarantine items are persisted
- Whether Quarantine → approval → Deals is tight end-to-end
- Whether we currently have split-brain behavior (multiple DBs / multiple truth paths)
This audit is the last major puzzle piece before we scale real usage.

## Non-negotiable constraints
- This is FORENSICS ONLY: INVESTIGATE → REPORT → STOP.
- Do NOT implement fixes in this mission.
- Do NOT delete data.
- Do NOT run destructive DB commands (no UPDATE/DELETE).
- Provide evidence for every claim (file:line refs, env vars, curl, DB SELECTs, logs).

## Primary Objective
Produce an evidence-based "Ground Truth" report for:
1) Canonical Source-of-Truth Database (what it is, who reads/writes)
2) Real-life data ingestion pipeline into Quarantine (what exists today vs what's imagined)
3) Tightness of workflow: Quarantine → approve → Deals (and everything that should happen downstream)
4) Gaps, misalignments, and risks vs world-class/industry standard
5) A prioritized set of remediation recommendations (still no implementation here)

---

# Scope
Focus areas (must all be covered):
A) Intake layer:
- MCP server integration (email login / auth)
- Email watching / polling / webhook logic
- Email parsing/classification → opportunity extraction
- De-duplication {{MISSION_DESCRIPTION}} idempotency (avoid duplicate opportunities)
- Rate limiting / backoff / failure handling

B) Quarantine layer:
- Where Quarantine data lives (DB tables, schemas)
- What fields define a "Quarantine item"
- How Quarantine items are surfaced in UI
- Delete/clear/approve actions and their backend paths

C) Promotion layer (approval):
- What happens when user approves a quarantine item
- How it becomes a Deal (schema mapping / stage mapping)
- Which services are involved (dashboard → backend → agent → DB)
- Event logs / audit logs / traceability

D) Deal lifecycle integrity:
- After promotion: do stages, notes, tasks, RAG attachments, email association actually link to the same deal record?
- Can the agent see the same deals the UI sees?
- Are there any split-brain stores still in play?

---

# Deliverables (WSL paths, Markdown only)
Write your report here:
- /home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_REPORT.md

Also write an "Evidence Pack Index" here:
- /home/zaks/bookkeeping/docs/FORENSIC_INTAKE_QUARANTINE_DEAL_INTEGRITY_EVIDENCE_INDEX.md

Do NOT overwrite existing unrelated docs.

---

# Required report structure (must follow)
## 1) AGENT IDENTITY
- agent_name:
- run_id:
- timestamp:
- repo_revision (git hash if available):
- environment assumptions:

## 2) Executive Summary (Plain English)
- What is the real intake pipeline today?
- What is the real source-of-truth DB today?
- Is Quarantine → Deals truly wired end-to-end today?
- Biggest risks / mismatches

## 3) System Reality Map (Evidence-based)
### 3.1 Source-of-Truth DB determination
Answer with proof:
- Which DB is canonical for Deals and Quarantine?
- Which services read/write which DB(s)?
- Are there multiple DB URLs configured (dashboard vs backend vs agent)?
- Where are the env vars set (files + line refs)?

Include:
- "DB Topology Diagram" (text diagram is fine)
- "Tables of record" list (deals, quarantine, events, notes, etc.)

### 3.2 Intake pipeline: email/MCP → quarantine
Provide the end-to-end path:
- Entry point (MCP server? scheduled job? webhook? manual import?)
- Auth mechanism (tokens? OAuth? stored credentials? where?)
- Extraction {{MISSION_DESCRIPTION}} normalization logic (where in code)
- De-duplication strategy (message-id? hash? thread id?)
- Failure {{MISSION_DESCRIPTION}} retry behavior
- Observability: how do we know ingestion is running?

### 3.3 Quarantine operations: list/create/delete/approve
Map each:
- UI action → backend route → service function → DB ops
- Confirm actual routes exist and work (curl + server logs)
- Confirm DB writes are happening in the canonical DB

### 3.4 Approval flow: quarantine → deal
Prove:
- what transform/mapping happens (fields, stage)
- where deal is written
- what events/logs are emitted
- whether agent and dashboard see the same result

## 4) Forensic Questions Checklist (Answer ALL)
You must answer each of these with evidence:

### A. Data Truth {{MISSION_DESCRIPTION}} DB Split-Brain
1) Where exactly is the canonical "deal truth" stored?
2) Do agent API, backend API, and dashboard read the same DB connection string?
3) Are there multiple schemas or separate DBs for "agent memory" vs "deal truth"?
4) Can a deal exist in UI but be invisible to the agent (and why)?
5) Are there any filesystem-based stores, legacy sqlite, or cached snapshots still referenced?

### B. Intake / MCP / Email
6) What MCP server(s) exist in the repo and how are they configured?
7) Is the email integration active or stubbed?
8) What mechanism triggers ingestion (polling schedule, webhook, manual)?
9) What credentials are required and where are they stored?
10) Is there an onboarding UI for email config, and does it truly write config used by ingestion?
11) What happens if auth expires — is it detected and surfaced to UI?
12) How do we prevent duplicate opportunities from repeated emails / threads?
13) How do we associate emails to an existing Deal after it's promoted?
14) What is the attachment handling strategy (download, parse, store, link)?

### C. Quarantine Integrity
15) What fields constitute a quarantine item and how do we validate them?
16) Are Quarantine "delete/clear" endpoints real, or placeholders?
17) When user approves, does the item disappear from Quarantine reliably?
18) What audit log is created for approval/rejection?
19) Does "approve" create a deal in the same DB the dashboard reads from?

### D. Deal Lifecycle Tightness
20) After promotion, do stage changes persist to the same record everyone reads?
21) Are there mismatched stage taxonomies (different strings across systems)?
22) Are there any "shadow pipelines" (legacy endpoints/ports) still referenced?
23) Do RAG/embeddings attach to the correct deal id consistently?
24) Can we trace one deal end-to-end across logs/events?

### E. Observability {{MISSION_DESCRIPTION}} "World-class" Standards
25) Where do ingestion logs go and are they correlated with a deal id or thread id?
26) Is there a single correlation id propagated across dashboard → backend → agent → DB?
27) What metrics/alerts exist (queue lag, ingestion failure, auth failure, duplicates)?
28) What are the security risks (token storage, PII in logs, least privilege)?
29) What is the disaster scenario (email ingestion loops, duplicate floods) and how is it prevented?

## 5) Gap {{MISSION_DESCRIPTION}} Misalignment List (Reality vs Desired)
Create a table:
- Gap ID
- "Expected behavior"
- "Current reality"
- Evidence
- Risk level (P0–P3)
- Root cause hypothesis
- How to verify further (commands)

## 6) Recommendations (Permanent, Industry-standard, Best-fit)
For each gap (especially P0/P1), propose:
- Permanent fix approach (tailored to this architecture)
- Best practice / industry standard
- Why it fits this system specifically
- "Never again" enforcement: gates/tests/invariants/monitoring

Must include "systemic improvements," not only patches:
- canonical data ownership model
- ingestion idempotency contract
- audit log + event model
- configuration UX → actual runtime config wiring
- end-to-end traceability strategy

## 7) Minimum Proof Steps (Repro + Validation)
List exact steps to validate the pipeline in a real-ish way WITHOUT destructive actions:
- How to simulate ingestion safely (dry-run mode or sample email payload)
- How to confirm quarantine creation and promotion
- How to prove DB truth alignment

## 8) STOP
Do not implement fixes. End the report with:
- "Audit complete"
- "Ready for remediation mission(s)"

---

# Evidence Requirements (non-negotiable)
For every major claim, include at least one of:
- file path + line range
- env var name + where set
- curl commands + outputs
- DB SELECT queries + outputs
- log excerpts + location

If you cannot prove something, mark:
NEEDS VERIFICATION
and list exact commands to prove it.

---

# Bonus "What else is broken?" sweep (mandatory)
After completing the main audit, do a second sweep using contrarian thinking:
- assume the ingestion pipeline is partially wired to legacy components
- assume UI config does not drive runtime config
- assume multiple DBs exist and are accidentally used
List the top 10 failure patterns most likely in this system and how to detect each with proof.

---

# Repository Locations
- Monorepo (Dashboard + Agent API): /home/zaks/zakops-agent-api
- Backend API: /home/zaks/zakops-backend
- RAG/LLM Service: /home/zaks/Zaks-llm
- Bookkeeping: /home/zaks/bookkeeping

# Database Information
- zakops DB (schema: zakops, user: zakops) — Backend primary
- zakops_agent DB (schema: public, user: agent) — Agent API
- crawlrag DB (schema: public) — RAG service

# Service Ports
- Dashboard: 3003
- Backend API: 8091
- Agent API: 8095
- RAG: 8052
- MCP Server: 9100
- Port 8090: DECOMMISSIONED (never use)

## Scope

As defined in the mission document

## Repository Roots

/home/zaks/zakops-agent-api,/home/zaks/zakops-backend,/home/zaks/Zaks-llm

## Known Issues or Constraints

V5PP guardrails apply. No production code modifications.

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

Write your report to: `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260213-163446/01_pass1/codex_report.md`

Begin your report with exactly this header:

```
# Pass 1 Report — CODEX
## Run: TP-20260213-163446 | Mode: forensic
## Generated: 2026-02-13T16:34:47Z
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
