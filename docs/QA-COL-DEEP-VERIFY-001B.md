# QA MISSION: QA-COL-DEEP-VERIFY-001B
## Deep Spec-Level Verification — Intelligence Layer, Memory, Citations, Tools, RAG, Agent Architecture
## Date: 2026-02-13
## Classification: QA Verification & Remediation (Deep Code-Level)
## Prerequisite: COL-V2 QA Verification (19 missions, 516 gates) + COL-V2-ACTIONABLE-ITEMS.md corrected
## Successor: COL-V2-CORE-001 (SM-2 execution readiness gating)
## Standard: Mission Prompt Standard v2.2

---

## Mission Objective

This is an **independent, deep code-level verification** of the COL-V2 implementation covering spec sections S5 (Summarization & Tiered Memory), S8 (Citation Validation & Self-Critique), S9 (Tool Scoping & Least Privilege), S13 (Cost Governance), S15 (Proposal Pipeline Hardening), S18 (RAG Enhancement Architecture), and S19 (Agent Architecture & Autonomous Capabilities).

The mission reads actual source files, verifies that spec-mandated functions, types, constants, and logic exist at the code level, and produces tee'd evidence for every gate. It does NOT build new features. Where a FAIL is found, it classifies and remediates per protocol.

### Source Artifacts

| Artifact | Path | Purpose |
|----------|------|---------|
| COL-DESIGN-SPEC-V2 | `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md` | Canonical design specification (3,276 lines) |
| Master Program | `/home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md` | Execution plan and sub-mission breakdown |
| Actionable Items | `/home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md` | Gap register with corrected post-audit counts |

### Evidence Directory

All evidence files are written to:

```
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001b
```

### Scope

**IN scope:** Code-level verification of 15 service files across agent-api (`app/services/`, `app/core/security/`, `app/core/langgraph/`) and cross-references to spec, migration 004, and actionable items register.

**OUT of scope:** Dashboard UI components, backend services in `zakops-backend/`, database runtime verification (psql queries), live endpoint testing, building any new features.

---

## Crash Recovery Protocol
<!-- Adopted from Improvement Area IA-2 -->

If resuming after a crash, run:

```bash
# 1. Check what evidence already exists
ls -la /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001b/

# 2. Check validation baseline
cd /home/zaks/zakops-agent-api && make validate-local

# 3. Count completed VF evidence files to determine progress
ls /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001b/VF-*.txt 2>/dev/null | wc -l
```

Resume from the first VF family that lacks evidence files.

---

## Pre-Flight

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001b
mkdir -p "$EVIDENCE_DIR"
```

### PF-1: Validation Baseline

```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee "$EVIDENCE_DIR/PF-1-validate-local.txt"
```

**PASS if:** exit 0. If not, stop — codebase is broken before QA starts.

### PF-2: TypeScript Compilation

```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee "$EVIDENCE_DIR/PF-2-tsc.txt"
```

**PASS if:** exit 0. No TypeScript compilation errors.

### PF-3: Source Artifacts Exist

```bash
{
  echo "--- COL-DESIGN-SPEC-V2.md ---"
  wc -l /home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V2.md
  echo "--- COL-V2-ACTIONABLE-ITEMS.md ---"
  wc -l /home/zaks/bookkeeping/docs/COL-V2-ACTIONABLE-ITEMS.md
  echo "--- MASTER-PROGRAM ---"
  wc -l /home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md
} 2>&1 | tee "$EVIDENCE_DIR/PF-3-source-artifacts.txt"
```

**PASS if:** All three files exist and have >100 lines each.

### PF-4: Evidence Directory Ready

```bash
ls -la "$EVIDENCE_DIR" 2>&1 | tee "$EVIDENCE_DIR/PF-4-evidence-dir.txt"
```

**PASS if:** Directory exists and is writable.

### PF-5: Agent-API Services Directory Has Sufficient Python Files

```bash
{
  echo "=== app/services/ ==="
  find /home/zaks/zakops-agent-api/apps/agent-api/app/services/ -name "*.py" -type f | wc -l
  echo "=== app/core/security/ ==="
  find /home/zaks/zakops-agent-api/apps/agent-api/app/core/security/ -name "*.py" -type f | wc -l
  echo "=== app/core/langgraph/ ==="
  find /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/ -name "*.py" -type f | wc -l
  echo "=== Total ==="
  find /home/zaks/zakops-agent-api/apps/agent-api/app/services/ /home/zaks/zakops-agent-api/apps/agent-api/app/core/security/ /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/ -name "*.py" -type f | wc -l
} 2>&1 | tee "$EVIDENCE_DIR/PF-5-python-file-count.txt"
```

**PASS if:** Total Python files >= 15.

---

## Verification Families

All commands assume `EVIDENCE_DIR` is set:

```bash
EVIDENCE_DIR=/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-deep-verify-001b
AGENT_API=/home/zaks/zakops-agent-api/apps/agent-api
```

---

## Verification Family 01 — Summarizer Implementation (S5.2-S5.3)

**Source file:** `$AGENT_API/app/services/summarizer.py`

### VF-01.1: should_summarize() checks turn_number % 5 == 0 (spec S5.3 trigger)

```bash
grep -n "should_summarize\|turn_number.*%.*5\|% 5\|%5\|every.*5.*turn" \
  "$AGENT_API/app/services/summarizer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-01-1.txt"
```

**PASS if:** Output contains a function or method named `should_summarize` and a modulo-5 check (e.g., `turn_number % 5 == 0` or `turn % 5`).

### VF-01.2: Extractive pre-filter or summarize function exists (spec S5.3 Step 1)

```bash
grep -n "extractive_summarize\|pre_filter\|_extract\|summarize\|def.*summar" \
  "$AGENT_API/app/services/summarizer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-01-2.txt"
```

**PASS if:** At least one summarization method is defined (extractive or LLM-based).

### VF-01.3: build_recall_memory() or equivalent for tiered memory (spec S5.2)

```bash
grep -n "build_recall_memory\|recall_memory\|memory_tier\|working.*recall.*archival\|tiered_memory\|MemoryTier" \
  "$AGENT_API/app/services/summarizer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-01-3.txt"
```

**PASS if:** Tiered memory concept is referenced — either `build_recall_memory()` method, `memory_tier` field usage, or working/recall/archival constants.

### VF-01.4: Stores summaries to session_summaries table (spec S5.3 Step 3)

```bash
grep -n "session_summaries\|INSERT.*session_summar\|summary.*table\|summaries.*INSERT" \
  "$AGENT_API/app/services/summarizer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-01-4.txt"
```

**PASS if:** Contains reference to `session_summaries` table (direct SQL or repository method call).

### VF-01.5: memory_tier field used (working/recall/archival per spec S5.2)

```bash
grep -n "memory_tier\|working\|recall\|archival" \
  "$AGENT_API/app/services/summarizer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-01-5.txt"
```

**PASS if:** At least one of `memory_tier`, `working`, `recall`, or `archival` is referenced in the summarizer logic.

**Gate VF-01:** All 5 checks pass. Summarizer implements spec S5.2-S5.3 turn-triggered tiered summarization.

---

## Verification Family 02 — Citation Audit (S8.2)

**Source file:** `$AGENT_API/app/core/security/citation_audit.py`

### VF-02.1: CitationCheck and CitationAuditResult types defined

```bash
grep -n "class CitationCheck\|class CitationAuditResult\|CitationCheck\|CitationAuditResult" \
  "$AGENT_API/app/core/security/citation_audit.py" 2>&1 | tee "$EVIDENCE_DIR/VF-02-1.txt"
```

**PASS if:** Both `CitationCheck` and `CitationAuditResult` class or dataclass definitions appear.

### VF-02.2: audit_citations() function with threshold logic

```bash
grep -n "def audit_citations\|async def audit_citations\|threshold\|STRONG\|WEAK\|MISMATCH" \
  "$AGENT_API/app/core/security/citation_audit.py" 2>&1 | tee "$EVIDENCE_DIR/VF-02-2.txt"
```

**PASS if:** `audit_citations` function is defined AND threshold-related terms appear.

### VF-02.3: Similarity scoring (keyword or semantic) — spec S8.2 says cosine similarity

```bash
grep -n "similarity\|cosine\|keyword_similarity\|_keyword_similarity\|semantic\|embedding" \
  "$AGENT_API/app/core/security/citation_audit.py" 2>&1 | tee "$EVIDENCE_DIR/VF-02-3.txt"
```

**PASS if:** At least one similarity scoring method is implemented (keyword-based or cosine/embedding-based).

### VF-02.4: Strong(>=0.5)/Weak(0.3-0.5)/Mismatch(<0.3) threshold bands

```bash
grep -n "0\.5\|0\.3\|strong\|weak\|mismatch\|STRONG_THRESHOLD\|WEAK_THRESHOLD" \
  "$AGENT_API/app/core/security/citation_audit.py" 2>&1 | tee "$EVIDENCE_DIR/VF-02-4.txt"
```

**PASS if:** Threshold values 0.5 and 0.3 (or named constants mapping to these) appear, matching the spec S8.2 bands.

**Gate VF-02:** All 4 checks pass. Citation audit implements spec S8.2 similarity-based verification with threshold bands.

---

## Verification Family 03 — Reflexion Self-Critique (S8.3)

**Source file:** `$AGENT_API/app/services/reflexion.py`

### VF-03.1: MAX_REFINEMENTS constant (spec says 2)

```bash
grep -n "MAX_REFINEMENTS\|max_refinements\|MAX_REFINE\|refinement.*limit\|max.*refine" \
  "$AGENT_API/app/services/reflexion.py" 2>&1 | tee "$EVIDENCE_DIR/VF-03-1.txt"
```

**PASS if:** A constant or parameter limiting refinements exists. Ideal value is 2 per spec S8.3.

### VF-03.2: evaluate() method with response + evidence parameters

```bash
grep -n "def evaluate\|async def evaluate\|def critique\|async def critique" \
  "$AGENT_API/app/services/reflexion.py" 2>&1 | tee "$EVIDENCE_DIR/VF-03-2.txt"
```

**PASS if:** An `evaluate()` or `critique()` method is defined that takes response and evidence as inputs.

### VF-03.3: CritiqueResult type with passed/issues/suggestion fields

```bash
grep -n "class CritiqueResult\|CritiqueResult\|passed\|issues\|suggestion\|refinement_count" \
  "$AGENT_API/app/services/reflexion.py" 2>&1 | tee "$EVIDENCE_DIR/VF-03-3.txt"
```

**PASS if:** `CritiqueResult` type is defined with `passed`, `issues`, and `suggestion` (or `suggestions`) fields.

### VF-03.4: refine_if_needed() or equivalent revision method

```bash
grep -n "refine_if_needed\|def refine\|def revise\|async def refine\|revision" \
  "$AGENT_API/app/services/reflexion.py" 2>&1 | tee "$EVIDENCE_DIR/VF-03-4.txt"
```

**PASS if:** A refinement/revision method exists that can iterate on a critique result.

**Gate VF-03:** All 4 checks pass. Reflexion implements spec S8.3 self-critique loop with bounded refinements.

---

## Verification Family 04 — Tool Scoping (S9.2-S9.3)

**Source file:** `$AGENT_API/app/core/security/tool_scoping.py`

### VF-04.1: SCOPE_TOOL_MAP dict with global/deal/document scopes (spec S9.2)

```bash
grep -n "SCOPE_TOOL_MAP\|scope_tool_map\|global.*deal.*document\|scope.*tools" \
  "$AGENT_API/app/core/security/tool_scoping.py" 2>&1 | tee "$EVIDENCE_DIR/VF-04-1.txt"
```

**PASS if:** A mapping from scope types (global, deal, document) to tool sets is defined.

### VF-04.2: ROLE_TOOL_MAP dict with VIEWER/OPERATOR/APPROVER/ADMIN roles (spec S9.3)

```bash
grep -n "ROLE_TOOL_MAP\|role_tool_map\|VIEWER\|OPERATOR\|APPROVER\|ADMIN" \
  "$AGENT_API/app/core/security/tool_scoping.py" 2>&1 | tee "$EVIDENCE_DIR/VF-04-2.txt"
```

**PASS if:** A role-based tool access mapping exists covering at least VIEWER, OPERATOR, APPROVER, and ADMIN.

### VF-04.3: check_tool_access() or filter function

```bash
grep -n "def check_tool_access\|def filter_tools\|def get_allowed_tools\|def scope_tools" \
  "$AGENT_API/app/core/security/tool_scoping.py" 2>&1 | tee "$EVIDENCE_DIR/VF-04-3.txt"
```

**PASS if:** A function that filters or checks tool access based on scope and/or role exists.

### VF-04.4: Deal-scoped tools include transition_deal, get_deal, add_note

```bash
grep -n "transition_deal\|get_deal\|add_note\|deal.*tools" \
  "$AGENT_API/app/core/security/tool_scoping.py" 2>&1 | tee "$EVIDENCE_DIR/VF-04-4.txt"
```

**PASS if:** `transition_deal`, `get_deal`, and `add_note` appear in the deal-scope tool list.

### VF-04.5: Global scope does NOT include transition_deal or create_deal

```bash
{
  echo "=== Lines containing 'global' scope definition ==="
  grep -n -A 20 "global.*:\|'global'\|\"global\"" \
    "$AGENT_API/app/core/security/tool_scoping.py"
  echo "=== Check: transition_deal should NOT be in global scope ==="
  python3 -c "
import ast, sys
with open('$AGENT_API/app/core/security/tool_scoping.py') as f:
    content = f.read()
if 'SCOPE_TOOL_MAP' in content:
    print('SCOPE_TOOL_MAP found — manual review needed for global scope contents')
else:
    print('No SCOPE_TOOL_MAP found')
"
} 2>&1 | tee "$EVIDENCE_DIR/VF-04-5.txt"
```

**PASS if:** The global scope tool list does NOT contain `transition_deal` or `create_deal`. Manual review of the SCOPE_TOOL_MAP `global` key is required.

**Gate VF-04:** All 5 checks pass. Tool scoping implements spec S9.2-S9.3 scope + role restriction.

---

## Verification Family 05 — Tool Verification Post-Conditions (S9.4, QW-12)

**Source file:** `$AGENT_API/app/core/security/tool_verification.py`

### VF-05.1: TOOL_POST_CONDITIONS dict or equivalent mapping

```bash
grep -n "TOOL_POST_CONDITIONS\|POST_CONDITIONS\|post_conditions\|postcondition" \
  "$AGENT_API/app/core/security/tool_verification.py" 2>&1 | tee "$EVIDENCE_DIR/VF-05-1.txt"
```

**PASS if:** A dictionary or mapping of tool names to post-condition verification functions exists.

### VF-05.2: Verify function for transition_deal

```bash
grep -n "transition_deal\|verify_transition\|deal.*verify\|state.*changed" \
  "$AGENT_API/app/core/security/tool_verification.py" 2>&1 | tee "$EVIDENCE_DIR/VF-05-2.txt"
```

**PASS if:** A post-condition verifier specifically for `transition_deal` tool exists (confirms state actually changed).

### VF-05.3: execute_with_verification() or equivalent wrapper

```bash
grep -n "execute_with_verification\|def verify_execution\|def verify_result\|verify.*post" \
  "$AGENT_API/app/core/security/tool_verification.py" 2>&1 | tee "$EVIDENCE_DIR/VF-05-3.txt"
```

**PASS if:** A wrapper function that runs the tool and then verifies post-conditions exists.

**Gate VF-05:** All 3 checks pass. Tool verification implements spec S9.4 post-condition checks.

---

## Verification Family 06 — Cost Repository (S13.2-S13.5)

**Source file:** `$AGENT_API/app/services/cost_repository.py`

### VF-06.1: record_cost() writes to cost_ledger table

```bash
grep -n "def record_cost\|async def record_cost\|cost_ledger\|INSERT.*cost" \
  "$AGENT_API/app/services/cost_repository.py" 2>&1 | tee "$EVIDENCE_DIR/VF-06-1.txt"
```

**PASS if:** `record_cost` method exists and references `cost_ledger` table.

### VF-06.2: get_daily_spend() and get_monthly_spend() methods

```bash
grep -n "def get_daily_spend\|def get_monthly_spend\|daily_spend\|monthly_spend\|daily.*cost\|monthly.*cost" \
  "$AGENT_API/app/services/cost_repository.py" 2>&1 | tee "$EVIDENCE_DIR/VF-06-2.txt"
```

**PASS if:** Both daily and monthly spend query methods exist.

### VF-06.3: Budget enforcement (check_budget or similar)

```bash
grep -n "check_budget\|enforce_budget\|budget.*check\|exceeded\|over_budget\|limit.*reached" \
  "$AGENT_API/app/services/cost_repository.py" 2>&1 | tee "$EVIDENCE_DIR/VF-06-3.txt"
```

**PASS if:** A budget check or enforcement function exists that can halt or warn on budget exceedance.

### VF-06.4: get_avg_daily_cost() for predictive budgeting (spec S13.4)

```bash
grep -n "avg_daily_cost\|average.*daily\|predictive\|projected\|rolling.*average\|budget_exhaustion" \
  "$AGENT_API/app/services/cost_repository.py" 2>&1 | tee "$EVIDENCE_DIR/VF-06-4.txt"
```

**PASS if:** A method for computing average daily cost or projecting budget exhaustion exists (spec S13.4 predictive budgeting).

### VF-06.5: deal_id filtering on cost queries

```bash
grep -n "deal_id\|WHERE.*deal\|deal.*filter\|by_deal" \
  "$AGENT_API/app/services/cost_repository.py" 2>&1 | tee "$EVIDENCE_DIR/VF-06-5.txt"
```

**PASS if:** Cost queries support filtering by `deal_id` for per-deal cost tracking.

**Gate VF-06:** All 5 checks pass. Cost repository implements spec S13.2-S13.5 cost governance.

---

## Verification Family 07 — Proposal Service (S15.2-S15.4)

**Source file:** `$AGENT_API/app/services/proposal_service.py`

### VF-07.1: PROPOSAL_HANDLERS dict with >= 7 handler types

```bash
grep -n "PROPOSAL_HANDLERS\|proposal_handlers\|handler.*dict\|_handlers" \
  "$AGENT_API/app/services/proposal_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-07-1.txt"
```

**PASS if:** A `PROPOSAL_HANDLERS` dict (or equivalent) with >= 7 registered handler types (spec has 9 per actionable items B7).

### VF-07.2: correct_brain_summary handler exists (spec S15.4, GAP-M10)

```bash
grep -n "correct_brain_summary\|brain_summary\|handle_correct\|_handle_correct_brain" \
  "$AGENT_API/app/services/proposal_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-07-2.txt"
```

**PASS if:** A handler for `correct_brain_summary` proposal type is defined.

### VF-07.3: execute() method that dispatches to handlers

```bash
grep -n "def execute\|async def execute\|dispatch\|handler\[" \
  "$AGENT_API/app/services/proposal_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-07-3.txt"
```

**PASS if:** An `execute()` method exists that dispatches to the appropriate handler based on proposal type.

### VF-07.4: FOR UPDATE locking on proposal status updates (spec S15.3, GAP-L3)

```bash
grep -n "FOR UPDATE\|for_update\|SELECT.*FOR UPDATE\|row_lock\|advisory_lock" \
  "$AGENT_API/app/services/proposal_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-07-4.txt"
```

**PASS if:** `FOR UPDATE` or equivalent row-level locking is used when updating proposal status (prevents concurrent execution).

**Gate VF-07:** All 4 checks pass. Proposal service implements spec S15.2-S15.4 pipeline with concurrent safety.

---

## Verification Family 08 — Snapshot Writer (S6)

**Source file:** `$AGENT_API/app/services/snapshot_writer.py`

### VF-08.1: TurnSnapshot dataclass with >= 20 fields (spec has 26)

```bash
{
  echo "=== TurnSnapshot class definition ==="
  grep -n "class TurnSnapshot\|@dataclass" "$AGENT_API/app/services/snapshot_writer.py"
  echo "=== Field count ==="
  python3 -c "
import re
with open('$AGENT_API/app/services/snapshot_writer.py') as f:
    content = f.read()
# Count fields in TurnSnapshot
match = re.search(r'class TurnSnapshot.*?(?=\nclass|\n\ndef |\Z)', content, re.DOTALL)
if match:
    fields = re.findall(r'^\s+\w+\s*:', match.group(), re.MULTILINE)
    print(f'Field count: {len(fields)}')
    for f in fields:
        print(f'  {f.strip()}')
else:
    print('TurnSnapshot class not found')
"
} 2>&1 | tee "$EVIDENCE_DIR/VF-08-1.txt"
```

**PASS if:** TurnSnapshot dataclass exists with >= 20 fields.

### VF-08.2: write() method to persist snapshot

```bash
grep -n "def write\|async def write\|def save\|async def save\|INSERT.*turn_snapshot" \
  "$AGENT_API/app/services/snapshot_writer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-08-2.txt"
```

**PASS if:** A `write()` or `save()` method exists that persists the snapshot to the database.

### VF-08.3: critique_result field in TurnSnapshot (spec S6: reflexion metadata)

```bash
grep -n "critique_result\|reflexion\|critique" \
  "$AGENT_API/app/services/snapshot_writer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-08-3.txt"
```

**PASS if:** The `critique_result` field exists in TurnSnapshot (captures reflexion self-critique output per spec S6).

### VF-08.4: thread_id + turn_number uniqueness

```bash
grep -n "thread_id.*turn_number\|UNIQUE.*thread.*turn\|unique.*thread.*turn" \
  "$AGENT_API/app/services/snapshot_writer.py" 2>&1 | tee "$EVIDENCE_DIR/VF-08-4.txt"
```

**PASS if:** The code references or enforces uniqueness on (thread_id, turn_number) — either via SQL constraint reference or application-level check.

**Gate VF-08:** All 4 checks pass. Snapshot writer implements spec S6 deterministic replay-ready snapshots.

---

## Verification Family 09 — Replay Service (S6.4)

**Source file:** `$AGENT_API/app/services/replay_service.py`

### VF-09.1: replay() method with thread_id + turn_number parameters

```bash
grep -n "def replay\|async def replay" \
  "$AGENT_API/app/services/replay_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-09-1.txt"
```

**PASS if:** A `replay()` method is defined with `thread_id` and `turn_number` as parameters.

### VF-09.2: _compare() method with similarity scoring

```bash
grep -n "def _compare\|def compare\|similarity\|cosine\|bag_of_words\|word.*overlap" \
  "$AGENT_API/app/services/replay_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-09-2.txt"
```

**PASS if:** A comparison method exists that produces a similarity score between original and replayed output.

### VF-09.3: Endpoint at /admin/replay (spec S6.4 says admin-only)

```bash
grep -rn "admin/replay\|/replay\|replay.*endpoint\|replay.*route" \
  "$AGENT_API/app/" --include="*.py" 2>&1 | head -20 | tee "$EVIDENCE_DIR/VF-09-3.txt"
```

**PASS if:** An endpoint path containing `replay` is registered, ideally under `/admin/`.

**Gate VF-09:** All 3 checks pass. Replay service implements spec S6.4 deterministic replay with similarity scoring.

---

## Verification Family 10 — Counterfactual Service (S6.5)

**Source file:** `$AGENT_API/app/services/counterfactual_service.py`

### VF-10.1: analyze() method with modified_inputs parameter

```bash
grep -n "def analyze\|async def analyze\|modified_inputs\|modifications" \
  "$AGENT_API/app/services/counterfactual_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-10-1.txt"
```

**PASS if:** An `analyze()` method exists that accepts modification parameters.

### VF-10.2: _apply_modifications() for input overrides

```bash
grep -n "_apply_modifications\|apply_modification\|override\|modified.*snapshot" \
  "$AGENT_API/app/services/counterfactual_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-10-2.txt"
```

**PASS if:** A method that applies modifications to snapshot inputs exists.

### VF-10.3: _analyze_divergence() for comparing original vs counterfactual

```bash
grep -n "_analyze_divergence\|divergence\|compare.*original\|diff.*result" \
  "$AGENT_API/app/services/counterfactual_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-10-3.txt"
```

**PASS if:** A divergence analysis method that compares original and counterfactual outputs exists.

**Gate VF-10:** All 3 checks pass. Counterfactual service implements spec S6.5 what-if analysis.

---

## Verification Family 11 — Export Service (S12)

**Source file:** `$AGENT_API/app/services/export_service.py`

### VF-11.1: Markdown export (_export_markdown)

```bash
grep -n "_export_markdown\|export_markdown\|markdown.*export\|format.*markdown" \
  "$AGENT_API/app/services/export_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-11-1.txt"
```

**PASS if:** A markdown export method is defined.

### VF-11.2: JSON export (_export_json)

```bash
grep -n "_export_json\|export_json\|json.*export\|format.*json" \
  "$AGENT_API/app/services/export_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-11-2.txt"
```

**PASS if:** A JSON export method is defined.

### VF-11.3: attach_to_deal() method (spec S12.3)

```bash
grep -n "attach_to_deal\|deal.*attach\|attach.*artifact" \
  "$AGENT_API/app/services/export_service.py" 2>&1 | tee "$EVIDENCE_DIR/VF-11-3.txt"
```

**PASS if:** An `attach_to_deal()` method exists that links exports to deal artifacts.

**Gate VF-11:** All 3 checks pass. Export service implements spec S12 multi-format export with deal attachment.

---

## Verification Family 12 — Node Registry / Specialist Delegation (S19.4)

**Source file:** `$AGENT_API/app/core/langgraph/node_registry.py`

### VF-12.1: NodeRegistry class exists

```bash
grep -n "class NodeRegistry" \
  "$AGENT_API/app/core/langgraph/node_registry.py" 2>&1 | tee "$EVIDENCE_DIR/VF-12-1.txt"
```

**PASS if:** `class NodeRegistry` is defined.

### VF-12.2: >= 3 specialist nodes: Financial, Risk, DealMemory

```bash
grep -n "Financial\|Risk\|DealMemory\|FinancialSpecialist\|RiskSpecialist\|DealMemorySpecialist\|specialist" \
  "$AGENT_API/app/core/langgraph/node_registry.py" 2>&1 | tee "$EVIDENCE_DIR/VF-12-2.txt"
```

**PASS if:** At least 3 specialist node types are defined or registered (Financial, Risk, DealMemory per spec S19.4).

### VF-12.3: SpecialistNode protocol/interface defined

```bash
grep -n "class SpecialistNode\|Protocol\|ABC\|interface\|abstract" \
  "$AGENT_API/app/core/langgraph/node_registry.py" 2>&1 | tee "$EVIDENCE_DIR/VF-12-3.txt"
```

**PASS if:** A `SpecialistNode` protocol, ABC, or interface class is defined.

### VF-12.4: route() or classification method

```bash
grep -n "def route\|def classify\|def delegate\|async def route\|keyword.*classif" \
  "$AGENT_API/app/core/langgraph/node_registry.py" 2>&1 | tee "$EVIDENCE_DIR/VF-12-4.txt"
```

**PASS if:** A routing or classification method exists that directs queries to the appropriate specialist.

**Gate VF-12:** All 4 checks pass. Node registry implements spec S19.4 specialist delegation architecture.

---

## Verification Family 13 — Plan-and-Execute Graph (S19.3)

**Source file:** `$AGENT_API/app/core/langgraph/plan_execute.py`

### VF-13.1: Plan decomposition method (plan() or similar)

```bash
grep -n "def plan\|async def plan\|decompose\|create_plan\|step.*decomp" \
  "$AGENT_API/app/core/langgraph/plan_execute.py" 2>&1 | tee "$EVIDENCE_DIR/VF-13-1.txt"
```

**PASS if:** A planning/decomposition method exists that breaks a complex query into steps.

### VF-13.2: Sequential step execution

```bash
grep -n "execute_step\|run_step\|step.*execute\|for.*step\|sequential" \
  "$AGENT_API/app/core/langgraph/plan_execute.py" 2>&1 | tee "$EVIDENCE_DIR/VF-13-2.txt"
```

**PASS if:** A step execution method or loop exists that runs plan steps in order.

### VF-13.3: Result synthesis

```bash
grep -n "synthesize\|synthesis\|combine.*result\|merge.*result\|aggregate" \
  "$AGENT_API/app/core/langgraph/plan_execute.py" 2>&1 | tee "$EVIDENCE_DIR/VF-13-3.txt"
```

**PASS if:** A synthesis method exists that combines step results into a final output.

**Gate VF-13:** All 3 checks pass. Plan-and-execute implements spec S19.3 structured multi-step reasoning.

---

## Verification Family 14 — RAG Hybrid Query (S18.1, A-1)

**Source file:** `$AGENT_API/app/services/rag_rest.py`

### VF-14.1: hybrid_query() method exists

```bash
grep -n "def hybrid_query\|async def hybrid_query\|hybrid.*query\|/rag/hybrid" \
  "$AGENT_API/app/services/rag_rest.py" 2>&1 | tee "$EVIDENCE_DIR/VF-14-1.txt"
```

**PASS if:** A `hybrid_query()` method or call to `/rag/hybrid` endpoint exists.

### VF-14.2: RRF fusion reference or parameter (spec says k=60)

```bash
grep -n "rrf\|RRF\|rrf_k\|k=60\|reciprocal_rank\|fusion" \
  "$AGENT_API/app/services/rag_rest.py" 2>&1 | tee "$EVIDENCE_DIR/VF-14-2.txt"
```

**PASS if:** RRF (Reciprocal Rank Fusion) is referenced, ideally with k=60. Note: the Zaks-llm service has the actual RRF implementation; agent-api is the client.

### VF-14.3: Both dense and sparse retrieval paths

```bash
grep -n "dense\|sparse\|bm25\|embedding\|vector\|keyword.*search\|semantic.*search\|sparse_weight" \
  "$AGENT_API/app/services/rag_rest.py" 2>&1 | tee "$EVIDENCE_DIR/VF-14-3.txt"
```

**PASS if:** The code references both dense (embedding/vector) and sparse (keyword/BM25) retrieval, either directly or via parameters to the RAG REST endpoint.

**Gate VF-14:** All 3 checks pass. RAG hybrid query implements spec S18.1 dual-retrieval with RRF fusion.

---

## Verification Family 15 — Drift Detection (S4.5)

**Source file:** `$AGENT_API/app/services/drift_detection.py`

### VF-15.1: check_staleness() method

```bash
grep -n "def check_staleness\|async def check_staleness" \
  "$AGENT_API/app/services/drift_detection.py" 2>&1 | tee "$EVIDENCE_DIR/VF-15-1.txt"
```

**PASS if:** `check_staleness()` method is defined.

### VF-15.2: detect_contradictions() method

```bash
grep -n "def detect_contradictions\|async def detect_contradictions" \
  "$AGENT_API/app/services/drift_detection.py" 2>&1 | tee "$EVIDENCE_DIR/VF-15-2.txt"
```

**PASS if:** `detect_contradictions()` method is defined.

### VF-15.3: compute_decay_confidence() with Ebbinghaus-style formula (spec S4.5 item 5)

```bash
grep -n "compute_decay_confidence\|decay_confidence\|math.exp\|exponential.*decay\|ebbinghaus\|exp(" \
  "$AGENT_API/app/services/drift_detection.py" 2>&1 | tee "$EVIDENCE_DIR/VF-15-3.txt"
```

**PASS if:** `compute_decay_confidence()` exists and uses exponential decay (references `math.exp`, `exp(`, or equivalent).

### VF-15.4: should_re_summarize() method

```bash
grep -n "def should_re_summarize\|async def should_re_summarize" \
  "$AGENT_API/app/services/drift_detection.py" 2>&1 | tee "$EVIDENCE_DIR/VF-15-4.txt"
```

**PASS if:** `should_re_summarize()` method is defined.

**Gate VF-15:** All 4 checks pass. Drift detection implements spec S4.5 staleness, contradiction, and decay analysis.

---

## Cross-Consistency Checks

### XC-1: Summarizer writes to session_summaries table that migration 004 creates

```bash
{
  echo "=== Summarizer references to session_summaries ==="
  grep -n "session_summaries" "$AGENT_API/app/services/summarizer.py"
  echo ""
  echo "=== Migration 004 creates session_summaries ==="
  grep -rn "CREATE TABLE.*session_summaries" "$AGENT_API/" --include="*.sql" --include="*.py"
} 2>&1 | tee "$EVIDENCE_DIR/XC-1.txt"
```

**PASS if:** The summarizer references the same `session_summaries` table defined in migration 004.

### XC-2: Tool scoping roles match middleware X-User-Role values

```bash
{
  echo "=== Tool scoping roles ==="
  grep -n "VIEWER\|OPERATOR\|APPROVER\|ADMIN" "$AGENT_API/app/core/security/tool_scoping.py"
  echo ""
  echo "=== Middleware role extraction ==="
  grep -rn "X-User-Role\|user_role\|role.*header" "$AGENT_API/app/core/" --include="*.py"
} 2>&1 | tee "$EVIDENCE_DIR/XC-2.txt"
```

**PASS if:** The role names in tool_scoping.py match those extracted from middleware headers (VIEWER, OPERATOR, APPROVER, ADMIN).

### XC-3: Proposal handlers include all spec S15 types

```bash
{
  echo "=== Proposal handler types in service ==="
  grep -n "PROPOSAL_HANDLERS\|handler.*type\|'stage_transition'\|'correct_brain'\|'add_note'" \
    "$AGENT_API/app/services/proposal_service.py"
  echo ""
  echo "=== Spec S15 proposal types (from actionable items) ==="
  echo "Expected: stage_transition, add_note, create_deal, assign_deal, update_priority, escalate, correct_brain_summary, update_deal_field, bulk_action (9 types per B7)"
} 2>&1 | tee "$EVIDENCE_DIR/XC-3.txt"
```

**PASS if:** The handler dict includes >= 7 of the 9 expected proposal types from spec S15.

### XC-4: Cost repository writes to cost_ledger table from migration 004

```bash
{
  echo "=== Cost repository references to cost_ledger ==="
  grep -n "cost_ledger" "$AGENT_API/app/services/cost_repository.py"
  echo ""
  echo "=== Migration 004 creates cost_ledger ==="
  grep -rn "CREATE TABLE.*cost_ledger" "$AGENT_API/" --include="*.sql" --include="*.py"
} 2>&1 | tee "$EVIDENCE_DIR/XC-4.txt"
```

**PASS if:** The cost repository writes to the same `cost_ledger` table defined in migration 004.

### XC-5: Snapshot writer fields match turn_snapshots table columns

```bash
{
  echo "=== TurnSnapshot dataclass fields ==="
  grep -n "^\s\+\w\+\s*:" "$AGENT_API/app/services/snapshot_writer.py" | head -30
  echo ""
  echo "=== turn_snapshots SQL columns ==="
  grep -rn "turn_snapshots\|rendered_system_prompt\|evidence_context\|critique_result" \
    "$AGENT_API/" --include="*.sql" --include="*.py" | head -20
} 2>&1 | tee "$EVIDENCE_DIR/XC-5.txt"
```

**PASS if:** The TurnSnapshot dataclass fields align with the `turn_snapshots` table columns (especially `critique_result` field).

---

## Stress Tests

### ST-1: Reflexion MAX_REFINEMENTS is exactly 2 (spec S8.3)

```bash
{
  echo "=== MAX_REFINEMENTS value ==="
  grep -n "MAX_REFINEMENTS\|max_refinements" "$AGENT_API/app/services/reflexion.py"
  echo ""
  echo "=== Checking for value 2 ==="
  grep -n "= 2\|=2\|: 2\|:2" "$AGENT_API/app/services/reflexion.py" | grep -i "refine\|max"
} 2>&1 | tee "$EVIDENCE_DIR/ST-1.txt"
```

**PASS if:** MAX_REFINEMENTS (or equivalent) is set to exactly 2. FAIL if set to any other value.

### ST-2: Tool scoping: global scope has <= 3 tools (spec S9.2)

```bash
{
  echo "=== Global scope tool count ==="
  python3 -c "
import re
with open('$AGENT_API/app/core/security/tool_scoping.py') as f:
    content = f.read()
# Try to find global scope tools
lines = content.split('\n')
in_global = False
tools = []
for line in lines:
    if 'global' in line.lower() and (':' in line or '=' in line):
        in_global = True
        continue
    if in_global:
        if line.strip().startswith(']') or line.strip().startswith('}'):
            break
        stripped = line.strip().strip(',').strip('\"').strip(\"'\")
        if stripped:
            tools.append(stripped)
print(f'Global scope tools found: {len(tools)}')
for t in tools:
    print(f'  - {t}')
" 2>/dev/null
  echo ""
  echo "=== Raw global section ==="
  grep -A 10 "'global'" "$AGENT_API/app/core/security/tool_scoping.py"
} 2>&1 | tee "$EVIDENCE_DIR/ST-2.txt"
```

**PASS if:** Global scope contains <= 3 tools (spec S9.2 says limited read-only tools). FAIL if > 3.

### ST-3: Summarizer trigger at every 5 turns (not 3, not 10)

```bash
{
  echo "=== Modulo check in summarizer ==="
  grep -n "% 5\|%5\|== 0\|turn.*5\|every.*5\|SUMMARIZE_INTERVAL\|summarize_interval" \
    "$AGENT_API/app/services/summarizer.py"
  echo ""
  echo "=== Verify NOT 3 or 10 ==="
  grep -n "% 3\|% 10\|%3\|%10" "$AGENT_API/app/services/summarizer.py"
} 2>&1 | tee "$EVIDENCE_DIR/ST-3.txt"
```

**PASS if:** Summarization is triggered at turn multiples of 5 (not 3, not 10). Second grep should be empty.

### ST-4: All B-section actionable items from COL-V2-ACTIONABLE-ITEMS.md have corresponding service files

```bash
{
  echo "=== B-section services and file existence ==="
  echo "B1: citation_audit.py"
  ls -la "$AGENT_API/app/core/security/citation_audit.py" 2>&1
  echo "B2: replay_service.py"
  ls -la "$AGENT_API/app/services/replay_service.py" 2>&1
  echo "B3: counterfactual_service.py"
  ls -la "$AGENT_API/app/services/counterfactual_service.py" 2>&1
  echo "B4: node_registry.py"
  ls -la "$AGENT_API/app/core/langgraph/node_registry.py" 2>&1
  echo "B5: rag_rest.py"
  ls -la "$AGENT_API/app/services/rag_rest.py" 2>&1
  echo "B6: export_service.py"
  ls -la "$AGENT_API/app/services/export_service.py" 2>&1
  echo "B7: proposal_service.py"
  ls -la "$AGENT_API/app/services/proposal_service.py" 2>&1
  echo "B8: drift_detection.py"
  ls -la "$AGENT_API/app/services/drift_detection.py" 2>&1
  echo "B9: snapshot_writer.py"
  ls -la "$AGENT_API/app/services/snapshot_writer.py" 2>&1
  echo "B10: summarizer.py"
  ls -la "$AGENT_API/app/services/summarizer.py" 2>&1
} 2>&1 | tee "$EVIDENCE_DIR/ST-4.txt"
```

**PASS if:** All 10 B-section service files exist (no "No such file" errors).

### ST-5: Drift detection decay formula uses exponential decay (math.exp or similar)

```bash
{
  echo "=== Exponential decay in drift_detection.py ==="
  grep -n "math.exp\|np.exp\|exp(\|exponential\|ebbinghaus\|e\*\*\|pow(" \
    "$AGENT_API/app/services/drift_detection.py"
  echo ""
  echo "=== Import math or numpy ==="
  grep -n "import math\|from math\|import numpy" "$AGENT_API/app/services/drift_detection.py"
} 2>&1 | tee "$EVIDENCE_DIR/ST-5.txt"
```

**PASS if:** The decay formula uses `math.exp` or equivalent exponential function (spec S4.5 item 5 says Ebbinghaus-style).

---

## Remediation Protocol

When a gate results in FAIL:

1. **Read the evidence file** — understand what was expected vs. what was found
2. **Classify the failure:**
   - `MISSING_FIX` — Code was supposed to exist but doesn't
   - `REGRESSION` — Code existed before but was removed or broken
   - `SCOPE_GAP` — Feature is listed as not-yet-started in actionable items (expected)
   - `FALSE_POSITIVE` — The grep pattern missed existing code (different naming)
   - `NOT_IMPLEMENTED` — Spec feature has no implementation at all
   - `PARTIAL` — Implementation exists but is incomplete
   - `VIOLATION` — Implementation contradicts the spec
3. **Apply fix** following original guardrails (QA only — no new features)
4. **Re-run the specific gate** and tee to the same evidence file (overwrites)
5. **Run `make validate-local`** to ensure fix didn't break anything
6. **Record** the remediation in the completion report with: gate ID, classification, fix applied, evidence path

### Decision Tree for Classifications

- **IF** file exists but function is named differently → `FALSE_POSITIVE` → re-run with corrected grep pattern
- **ELSE IF** file exists but feature is incomplete per actionable items B-section → `PARTIAL` → mark as INFO, note what's missing
- **ELSE IF** file does not exist and feature is in C-section (not-yet-started) → `SCOPE_GAP` → mark as INFO/DEFERRED
- **ELSE IF** file exists and function exists but value is wrong (e.g., MAX_REFINEMENTS=3 instead of 2) → `VIOLATION` → remediate
- **ELSE** → `NOT_IMPLEMENTED` → note in remediation log

---

## Enhancement Opportunities

### ENH-1: Embedding-Based Citation Similarity
Citation audit (VF-02) currently uses keyword similarity. Upgrading to embedding-based cosine similarity (via RAG service) would match spec S8.2 precisely and improve citation quality scoring.

### ENH-2: Admin Auth on Replay/Counterfactual Endpoints
Replay (VF-09) and counterfactual (VF-10) endpoints need admin-only authentication. Currently session-only auth per actionable items B2.1 and B3.1.

### ENH-3: Reflexion Integration into Graph Pipeline
The reflexion service (VF-03) exists standalone but needs wiring into the LangGraph turn pipeline as a post-generation step. Currently not called from graph.py.

### ENH-4: Node Registry Integration into Main Graph
Node registry (VF-12) has 3 specialists but is not called from the main LangGraph flow per actionable items B4.2.

### ENH-5: Snapshot Writer Graph Integration
Snapshot writer (VF-08) exists but needs wiring into graph.py to capture every turn automatically per actionable items B9.1.

### ENH-6: Citation Audit Graph Integration
Citation audit (VF-02) needs integration as a post-completion hook in graph.py per actionable items B1.2.

### ENH-7: Drift Detection Graph Integration
Drift detection (VF-15) needs wiring into the turn pipeline to check after brain extraction per actionable items B8.1.

### ENH-8: Test Coverage for All VF Services
None of the 15 verified services have comprehensive unit test files in the agent-api test directory. Each service should have corresponding `test_*.py` files.

### ENH-9: Predictive Budget Exhaustion Alerts
Cost repository (VF-06) has predictive fields in the deal_budgets table but no alert/notification mechanism when projected spend exceeds monthly limit.

### ENH-10: Counterfactual Brain-Diff Computation
Counterfactual service (VF-10) is missing brain_diff comparison between original and counterfactual outcomes per actionable items B3.2.

---

## Scorecard Template

```
QA-COL-DEEP-VERIFY-001B — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):           [ PASS / FAIL ]
  PF-2 (TypeScript compilation):   [ PASS / FAIL ]
  PF-3 (Source artifacts exist):   [ PASS / FAIL ]
  PF-4 (Evidence directory ready): [ PASS / FAIL ]
  PF-5 (Python file count >= 15):  [ PASS / FAIL ]

Verification Gates:
  VF-01 (Summarizer):              __ / 5 checks PASS
  VF-02 (Citation Audit):          __ / 4 checks PASS
  VF-03 (Reflexion):               __ / 4 checks PASS
  VF-04 (Tool Scoping):            __ / 5 checks PASS
  VF-05 (Tool Verification):       __ / 3 checks PASS
  VF-06 (Cost Repository):         __ / 5 checks PASS
  VF-07 (Proposal Service):        __ / 4 checks PASS
  VF-08 (Snapshot Writer):         __ / 4 checks PASS
  VF-09 (Replay Service):          __ / 3 checks PASS
  VF-10 (Counterfactual Service):  __ / 3 checks PASS
  VF-11 (Export Service):          __ / 3 checks PASS
  VF-12 (Node Registry):           __ / 4 checks PASS
  VF-13 (Plan-and-Execute):        __ / 3 checks PASS
  VF-14 (RAG Hybrid Query):        __ / 3 checks PASS
  VF-15 (Drift Detection):         __ / 4 checks PASS

Cross-Consistency:
  XC-1 (Summarizer → migration 004):    [ PASS / FAIL ]
  XC-2 (Tool roles → middleware):        [ PASS / FAIL ]
  XC-3 (Proposal handlers → spec S15):  [ PASS / FAIL ]
  XC-4 (Cost repo → migration 004):     [ PASS / FAIL ]
  XC-5 (Snapshot fields → table cols):   [ PASS / FAIL ]

Stress Tests:
  ST-1 (MAX_REFINEMENTS = 2):        [ PASS / FAIL ]
  ST-2 (Global scope <= 3 tools):    [ PASS / FAIL ]
  ST-3 (Summarize every 5 turns):    [ PASS / FAIL ]
  ST-4 (B-section files exist):      [ PASS / FAIL ]
  ST-5 (Exponential decay formula):  [ PASS / FAIL ]

Total: __ / 67 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

### Gate Count Breakdown

| Section | Gates |
|---------|-------|
| Pre-Flight | 5 |
| VF-01 through VF-15 | 57 |
| Cross-Consistency | 5 |
| Stress Tests | 5 |
| **Total** | **67** |

---

## Guardrails

1. **QA only — do not build new features.** This mission verifies existing code against the spec. It does not implement missing features.
2. **Remediate, don't redesign.** If a function is named differently than expected, update the grep pattern and recheck — do not rename the function.
3. **Evidence-based: every PASS needs tee'd output.** "I checked and it's fine" is never evidence. Every gate writes to `$EVIDENCE_DIR/`.
4. **Services-down accommodation.** All gates in this mission are code-level (grep/read), not live endpoint tests. No service needs to be running.
5. **All bash evidence commands use `tee` to evidence directory.** Every command pipes to `| tee "$EVIDENCE_DIR/{gate-id}.txt"`.
6. **Preserve existing code.** Do not modify service files to make gates pass. If code doesn't match, classify and document.
7. **FALSE_POSITIVE before FAIL.** If a grep pattern doesn't match but manual inspection shows the code exists with different naming, classify as FALSE_POSITIVE, adjust the pattern, and re-run.
8. **SCOPE_GAP items are INFO, not FAIL.** Features listed in Section C (not-yet-started) of the actionable items are expected gaps — mark as INFO/DEFERRED.
9. **Per contract surface discipline.** Do not edit generated files. Do not modify migration files.
10. **WSL safety.** If any new `.sh` files are created: `sed -i 's/\r$//'`. If any files created under `/home/zaks/`: `sudo chown zaks:zaks`.

---

## Stop Condition

Stop when all 67 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE with documented rationale), all remediations are applied and re-verified, `make validate-local` passes, and the scorecard is complete with evidence file paths for every gate.

Do NOT proceed to building COL-V2 features. Do NOT proceed to SM-2 execution. This mission produces a verified baseline of what exists, what's partial, and what's missing — feeding the execution plan.

---

*End of Mission Prompt — QA-COL-DEEP-VERIFY-001B*
