# MISSION: QA-COL-BUILD-VERIFY-001A
## Agent-API Core + Intelligence Services Verification
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-V2-BUILD-001A (COMPLETE), COL-V2-BUILD-001B (COMPLETE)
## Successor: None

---

## Mission Objective

Independent verification of two completed execution missions covering the agent-api Python layer:

| Source Mission | AC | Phases | Files Created | Files Modified |
|---|---|---|---|---|
| COL-V2-BUILD-001A (Core Wiring + Service Completion) | 8 | 4 | 1 | 8 |
| COL-V2-BUILD-001B (Intelligence Services + Agent Architecture) | 11 | 4 | 5 | 3 |

**Combined scope: 19 AC** covering core graph.py wiring, 8 service completion items, legal hold migration, reflexion service, 3 cognitive intelligence services (decision fatigue sentinel, spaced repetition, sentiment coach), PlanAndExecuteGraph, node registry expansion, ghost knowledge SSE event, and MCP cost ledger.

This QA mission will **verify, cross-check, stress-test, and remediate** all 19 AC. It does NOT build new features or redesign existing services.

### Source Artifacts

| Artifact | Path |
|---|---|
| 001A Completion Report | `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md` |
| 001B Completion Report | `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001B-COMPLETION.md` |
| 001A Checkpoint | `/home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001A.md` |
| 001B Checkpoint | `/home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001B.md` |

### Evidence Directory

All gate evidence is captured to:
```
/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/
```

---

## Pre-Flight (5 checks)

### PF-1: Validation Baseline
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/PF-01.txt
```
**PASS if:** exit 0. If not, stop — codebase is broken before QA starts.

### PF-2: TypeScript Compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/PF-02.txt
```
**PASS if:** exit 0

### PF-3: Agent-API Docker Container Running
```bash
docker exec zakops-agent-api echo "container alive" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/PF-03.txt
```
**PASS if:** prints "container alive". If container is down, all live verification gates (docker exec) become SKIP with note.

### PF-4: Source Mission Completion Reports Exist
```bash
ls -la /home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md /home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001B-COMPLETION.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/PF-04.txt
```
**PASS if:** both files exist

### PF-5: Evidence Directory
```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a && echo "evidence dir ready" | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/PF-05.txt
```
**PASS if:** directory created or exists

---

## Verification Families

### VF-01 — Post-Turn Enrichment Pipeline (001A AC-1, AC-2)

#### VF-01.1: _post_turn_enrichment() exists in graph.py
```bash
grep -n "_post_turn_enrichment" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-01-1.txt
```
**PASS if:** Function definition found (`async def _post_turn_enrichment`)

#### VF-01.2: Brain extraction wired in enrichment
```bash
grep -n "brain_extract\|extract_brain\|brain.*extract" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-01-2.txt
```
**PASS if:** At least 1 brain extraction call inside enrichment function

#### VF-01.3: Drift detection wired
```bash
grep -n "drift_detection\|check_staleness" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-01-3.txt
```
**PASS if:** drift_detection import + `check_staleness()` call

#### VF-01.4: Citation audit wired
```bash
grep -n "citation_audit\|audit_citations" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-01-4.txt
```
**PASS if:** citation_audit import + `audit_citations()` call

#### VF-01.5: Fire-and-forget pattern (asyncio.create_task)
```bash
grep -n "create_task.*_post_turn_enrichment\|asyncio.create_task" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-01-5.txt
```
**PASS if:** `asyncio.create_task` wrapping enrichment call

**Gate VF-01:** All 5 checks pass. Post-turn enrichment pipeline is wired with fire-and-forget execution.

---

### VF-02 — Node Registry + Specialist Routing (001A AC-1, 001B AC-8)

#### VF-02.1: node_registry.route() called pre-LLM in graph.py
```bash
grep -n "node_registry\|route(" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-02-1.txt
```
**PASS if:** node_registry import and `route()` call

#### VF-02.2: 4 specialists registered
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.core.langgraph.node_registry import NodeRegistry
nr = NodeRegistry()
print(f'specialists: {len(nr._nodes)}')
for name in sorted(nr._nodes.keys()):
    print(f'  - {name}')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-02-2.txt
```
**PASS if:** 4 specialists listed (financial_analysis, risk_assessment, deal_memory, compliance)

#### VF-02.3: synthesize() method exists
```bash
grep -n "def synthesize\|async def synthesize" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-02-3.txt
```
**PASS if:** synthesize method defined

#### VF-02.4: Compliance keywords in _classify_query
```bash
grep -A 5 "compliance.*:" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/node_registry.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-02-4.txt
```
**PASS if:** compliance domain keywords listed

**Gate VF-02:** All 4 checks pass. Node registry has 4 specialists with routing and synthesis.

---

### VF-03 — Admin Auth (001A AC-4)

#### VF-03.1: _require_admin function exists
```bash
grep -n "_require_admin\|ADMIN_USER_IDS" /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-03-1.txt
```
**PASS if:** `_require_admin` function + `ADMIN_USER_IDS` env var check

#### VF-03.2: Admin gate on /admin/replay
```bash
grep -A 5 "admin/replay" /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py | grep "_require_admin" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-03-2.txt
```
**PASS if:** `_require_admin(session)` call in replay handler

#### VF-03.3: Admin gate on /admin/counterfactual
```bash
grep -A 5 "admin/counterfactual" /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py | grep "_require_admin" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-03-3.txt
```
**PASS if:** `_require_admin(session)` call in counterfactual handler

**Gate VF-03:** All 3 checks pass. Admin endpoints are auth-guarded.

---

### VF-04 — BackendClient Migration (001A AC-5)

#### VF-04.1: No raw httpx in proposal_service
```bash
grep -n "httpx\|import httpx\|httpx.AsyncClient" /home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-04-1.txt
```
**PASS if:** No matches (exit 1 = no matches = PASS)

#### VF-04.2: No raw httpx in export_service
```bash
grep -n "httpx\|import httpx" /home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-04-2.txt
```
**PASS if:** No matches (exit 1 = no matches = PASS)

#### VF-04.3: BackendClient used instead
```bash
grep -n "BackendClient\|backend_client" /home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py /home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-04-3.txt
```
**PASS if:** BackendClient import in both files

#### VF-04.4: raw_request() method exists on BackendClient
```bash
grep -n "def raw_request\|async def raw_request" /home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-04-4.txt
```
**PASS if:** `raw_request` method defined

**Gate VF-04:** All 4 checks pass. No raw httpx in services; BackendClient used uniformly.

---

### VF-05 — Legal Hold Migration (001A AC-6, AC-7)

#### VF-05.1: legal_hold_locks table exists in DB
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
import asyncio
async def check():
    from app.services.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        r = await conn.fetchval(\"SELECT count(*) FROM information_schema.tables WHERE table_name = 'legal_hold_locks'\")
        print(f'legal_hold_locks: {\"EXISTS\" if r > 0 else \"MISSING\"}')
asyncio.run(check())
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-05-1.txt
```
**PASS if:** "EXISTS"

#### VF-05.2: legal_hold_log table exists
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
import asyncio
async def check():
    from app.services.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        r = await conn.fetchval(\"SELECT count(*) FROM information_schema.tables WHERE table_name = 'legal_hold_log'\")
        print(f'legal_hold_log: {\"EXISTS\" if r > 0 else \"MISSING\"}')
asyncio.run(check())
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-05-2.txt
```
**PASS if:** "EXISTS"

#### VF-05.3: Migration file exists
```bash
ls -la /home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-05-3.txt
```
**PASS if:** File exists

#### VF-05.4: create_monthly_partitions function
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
import asyncio
async def check():
    from app.services.database import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        r = await conn.fetchval(\"SELECT count(*) FROM information_schema.routines WHERE routine_name = 'create_monthly_partitions'\")
        print(f'create_monthly_partitions: {\"EXISTS\" if r > 0 else \"MISSING\"}')
asyncio.run(check())
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-05-4.txt
```
**PASS if:** "EXISTS"

**Gate VF-05:** All 4 checks pass. Legal hold tables and partition function exist.

---

### VF-06 — Service Completion Items (001A AC-1 through AC-5)

#### VF-06.1: Configurable citation thresholds
```bash
grep -n "CITATION_HIGH_THRESHOLD\|CITATION_LOW_THRESHOLD\|CITATION_QUALITY_FLOOR" /home/zaks/zakops-agent-api/apps/agent-api/app/core/security/citation_audit.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-06-1.txt
```
**PASS if:** 3 configurable constants found

#### VF-06.2: Proposal expiration check
```bash
grep -n "expir\|24.*hour\|timedelta" /home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-06-2.txt
```
**PASS if:** Expiration logic found

#### VF-06.3: trigger_type in proposal brain PUT
```bash
grep -n "trigger_type\|correction" /home/zaks/zakops-agent-api/apps/agent-api/app/services/proposal_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-06-3.txt
```
**PASS if:** `trigger_type='correction'` found

#### VF-06.4: Brain export appendix
```bash
grep -n "appendix\|Appendix C\|Deal Brain" /home/zaks/zakops-agent-api/apps/agent-api/app/services/export_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-06-4.txt
```
**PASS if:** Appendix C: Deal Brain section found

#### VF-06.5: Replay audit log
```bash
grep -n "replay_audit\|actor_id" /home/zaks/zakops-agent-api/apps/agent-api/app/services/replay_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-06-5.txt
```
**PASS if:** replay_audit log entry with actor_id

#### VF-06.6: Extractive pre-filter
```bash
grep -n "pre_filter\|filler\|acknowledgment\|low.signal" /home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-06-6.txt
```
**PASS if:** Extractive pre-filter logic found

**Gate VF-06:** All 6 checks pass. Service completion items are implemented.

---

### VF-07 — Reflexion Service (001B AC-1, AC-2)

#### VF-07.1: ReflexionService import
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.reflexion import reflexion_service, REFLEXION_ENABLED, ReflexionService, CritiqueResult; print('reflexion import OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-07-1.txt
```
**PASS if:** "reflexion import OK"

#### VF-07.2: critique() method exists
```bash
grep -n "async def critique\|def critique" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-07-2.txt
```
**PASS if:** critique method found

#### VF-07.3: verify_claims() method exists
```bash
grep -n "async def verify_claims\|def verify_claims" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-07-3.txt
```
**PASS if:** verify_claims method found

#### VF-07.4: CritiqueResult Pydantic model
```bash
grep -n "class CritiqueResult" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-07-4.txt
```
**PASS if:** CritiqueResult class found

#### VF-07.5: Reflexion wired in enrichment pipeline
```bash
grep -n "reflexion\|REFLEXION_ENABLED" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-07-5.txt
```
**PASS if:** reflexion import + REFLEXION_ENABLED check + `critique()` call

**Gate VF-07:** All 5 checks pass. Reflexion pipeline is operational and wired.

---

### VF-08 — Decision Fatigue Sentinel (001B AC-3)

#### VF-08.1: Import
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.fatigue_sentinel import DecisionFatigueSentinel; print('fatigue import OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-08-1.txt
```
**PASS if:** "fatigue import OK"

#### VF-08.2: Threshold detection
```bash
grep -n "threshold\|FATIGUE\|warning" /home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-08-2.txt
```
**PASS if:** Threshold constant and warning logic found

#### VF-08.3: FatigueWarning model
```bash
grep -n "class FatigueWarning\|class.*Warning.*BaseModel" /home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-08-3.txt
```
**PASS if:** FatigueWarning class found

**Gate VF-08:** All 3 checks pass. Fatigue sentinel detects decision overload.

---

### VF-09 — Spaced Repetition Service (001B AC-4)

#### VF-09.1: Import
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.spaced_repetition import SpacedRepetitionService; print('spaced_repetition import OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-09-1.txt
```
**PASS if:** "spaced_repetition import OK"

#### VF-09.2: compute_decay_confidence
```bash
grep -n "compute_decay_confidence\|DECAY_THRESHOLD" /home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-09-2.txt
```
**PASS if:** decay confidence function + threshold constant

#### VF-09.3: get_review_facts
```bash
grep -n "def get_review_facts\|async def get_review_facts" /home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-09-3.txt
```
**PASS if:** Method found

**Gate VF-09:** All 3 checks pass. Spaced repetition returns review facts with decay threshold.

---

### VF-10 — Sentiment Coach (001B AC-5)

#### VF-10.1: Import
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.sentiment_coach import SentimentCoach; print('sentiment import OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-10-1.txt
```
**PASS if:** "sentiment import OK"

#### VF-10.2: Trend detection
```bash
grep -n "improving\|declining\|neutral\|volatile\|get_trend" /home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-10-2.txt
```
**PASS if:** Trend labels and `get_trend()` found

#### VF-10.3: Per-deal tracking
```bash
grep -n "deal_id\|record_sentiment" /home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-10-3.txt
```
**PASS if:** deal_id parameter + `record_sentiment()` method

**Gate VF-10:** All 3 checks pass. Sentiment coach tracks per-deal trends.

---

### VF-11 — Ghost Knowledge SSE Event (001B AC-6)

#### VF-11.1: Event class exists
```bash
grep -n "class GhostKnowledgeFlagsEvent" /home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-11-1.txt
```
**PASS if:** Class found

#### VF-11.2: Registered in SSE_EVENT_TYPES
```bash
grep -n "ghost_knowledge_flags.*GhostKnowledge\|ghost_knowledge_flags" /home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-11-2.txt
```
**PASS if:** "ghost_knowledge_flags" key in SSE_EVENT_TYPES dict

#### VF-11.3: Required fields (deal_id, flags)
```bash
grep -A 5 "class GhostKnowledgeFlagsEvent" /home/zaks/zakops-agent-api/apps/agent-api/app/schemas/sse_events.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-11-3.txt
```
**PASS if:** deal_id and flags fields present

**Gate VF-11:** All 3 checks pass. Ghost knowledge SSE event schema is correct.

---

### VF-12 — PlanAndExecuteGraph (001B AC-7)

#### VF-12.1: Import
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.core.langgraph.plan_execute import PlanAndExecuteGraph; print('plan_execute import OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-12-1.txt
```
**PASS if:** "plan_execute import OK"

#### VF-12.2: MAX_STEPS limit
```bash
grep -n "MAX_STEPS\|max_steps" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-12-2.txt
```
**PASS if:** MAX_STEPS = 10

#### VF-12.3: Plan/execute/synthesize flow
```bash
grep -n "def plan\|def execute\|def synthesize\|async def run" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-12-3.txt
```
**PASS if:** All 3 phases (plan, execute, synthesize) found

**Gate VF-12:** All 3 checks pass. PlanAndExecuteGraph has step-limited plan/execute/synthesize.

---

### VF-13 — MCP Cost Ledger (001B AC-9)

#### VF-13.1: cost_repository in graph.py
```bash
grep -n "cost_repository\|record_cost" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-13-1.txt
```
**PASS if:** `cost_repository.record_cost()` call in `_tool_call()`

#### VF-13.2: Tool name in model field
```bash
grep -n 'model.*tool:' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-13-2.txt
```
**PASS if:** `model="tool:{tool_name}"` pattern

#### VF-13.3: MCP provider label
```bash
grep -n 'provider.*mcp' /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-13-3.txt
```
**PASS if:** `provider="mcp"`

**Gate VF-13:** All 3 checks pass. MCP tool calls are cost-logged.

---

### VF-14 — No Regressions + Bookkeeping (001A AC-8, 001B AC-10, AC-11)

#### VF-14.1: No import cycles
```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.core.langgraph.graph import LangGraphAgent
from app.services.reflexion import reflexion_service
from app.services.fatigue_sentinel import DecisionFatigueSentinel
from app.services.spaced_repetition import SpacedRepetitionService
from app.services.sentiment_coach import SentimentCoach
from app.core.langgraph.plan_execute import PlanAndExecuteGraph
from app.core.langgraph.node_registry import NodeRegistry
from app.services.proposal_service import proposal_service
from app.services.export_service import export_service
from app.services.backend_client import BackendClient
print('all 10 imports OK — no cycles')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-14-1.txt
```
**PASS if:** "all 10 imports OK — no cycles"

#### VF-14.2: CHANGES.md entries exist
```bash
grep -c "COL-V2-BUILD-001A\|COL-V2-BUILD-001B" /home/zaks/bookkeeping/CHANGES.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-14-2.txt
```
**PASS if:** count >= 2

#### VF-14.3: Completion reports exist
```bash
ls -la /home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001A-COMPLETION.md /home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001B-COMPLETION.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-14-3.txt
```
**PASS if:** Both files exist

#### VF-14.4: Checkpoint files complete
```bash
grep "COMPLETE" /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001A.md /home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001B.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/VF-14-4.txt
```
**PASS if:** Both checkpoints show COMPLETE

**Gate VF-14:** All 4 checks pass. No regressions and bookkeeping is complete.

---

## Cross-Consistency Checks

### XC-1: Completion Report vs Codebase Agreement

Verify that every file listed in both completion reports actually exists and contains the claimed changes.

```bash
for f in \
  apps/agent-api/migrations/029_legal_hold.sql \
  apps/agent-api/app/services/reflexion.py \
  apps/agent-api/app/services/fatigue_sentinel.py \
  apps/agent-api/app/services/spaced_repetition.py \
  apps/agent-api/app/services/sentiment_coach.py \
  apps/agent-api/app/core/langgraph/plan_execute.py; do
  if [ -f "/home/zaks/zakops-agent-api/$f" ]; then
    echo "EXISTS: $f"
  else
    echo "MISSING: $f"
  fi
done 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/XC-01.txt
```
**PASS if:** All 6 files exist (0 MISSING)

### XC-2: Spec Section References in Docstrings

Verify COL-DESIGN-SPEC-V2 section references are present in new service files.

```bash
grep -l "COL-DESIGN-SPEC\|COL-V2\|S[0-9]" \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py \
  /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/plan_execute.py \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/XC-02.txt
```
**PASS if:** At least 3 of 5 files contain spec references

### XC-3: Singleton Pattern Compliance

Verify services use module-level singletons (not class instantiation per call).

```bash
for f in reflexion fatigue_sentinel spaced_repetition sentiment_coach; do
  echo "--- $f ---"
  grep -n "^[a-z_].*=.*${f^}\|^[a-z_].*= .*Service\|^[a-z_].*= .*Coach\|^[a-z_].*= .*Sentinel" "/home/zaks/zakops-agent-api/apps/agent-api/app/services/$f.py" 2>/dev/null || echo "  (no module-level singleton)"
done 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/XC-03.txt
```
**PASS if:** Each service exports a module-level singleton instance

### XC-4: Fire-and-Forget Pattern Audit

All post-turn enrichment calls should use `asyncio.create_task`, never `await` directly.

```bash
grep -n "await.*_post_turn_enrichment\|create_task.*_post_turn_enrichment" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/XC-04.txt
```
**PASS if:** Only `create_task` pattern found, never direct `await`

### XC-5: Import Discipline — No Circular Dependencies

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
import sys
# Import everything — if circular, this will fail
from app.core.langgraph.graph import LangGraphAgent
from app.core.langgraph.node_registry import NodeRegistry
from app.core.langgraph.plan_execute import PlanAndExecuteGraph
from app.services.reflexion import reflexion_service
from app.services.fatigue_sentinel import DecisionFatigueSentinel
from app.services.spaced_repetition import SpacedRepetitionService
from app.services.sentiment_coach import SentimentCoach
from app.core.security.citation_audit import audit_citations
print('import chain clean — no circular dependencies')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/XC-05.txt
```
**PASS if:** "import chain clean"

---

## Stress Tests

### ST-1: BackendClient Usage Sweep

Ensure NO file in agent-api services uses raw httpx (beyond BackendClient itself).

```bash
grep -rn "import httpx\|httpx.AsyncClient" /home/zaks/zakops-agent-api/apps/agent-api/app/services/ --include="*.py" | grep -v "backend_client.py" | grep -v "__pycache__" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/ST-01.txt
```
**PASS if:** No matches (exit 1 = no raw httpx outside BackendClient)

### ST-2: Config-Gated Service Verification

Verify `REFLEXION_ENABLED` is a real config gate that can disable reflexion.

```bash
grep -n "REFLEXION_ENABLED" /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/ST-02.txt
```
**PASS if:** REFLEXION_ENABLED defined in reflexion.py and checked in graph.py

### ST-3: Pydantic Model Validation

Verify all new Pydantic models (CritiqueResult, FatigueWarning, RetentionResult, etc.) inherit from BaseModel.

```bash
grep -n "class.*BaseModel" \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/fatigue_sentinel.py \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/spaced_repetition.py \
  /home/zaks/zakops-agent-api/apps/agent-api/app/services/sentiment_coach.py \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/ST-03.txt
```
**PASS if:** At least 4 BaseModel subclasses found

### ST-4: SSE Event Type Union Integrity

Verify all SSE_EVENT_TYPES keys map to actual SSEEvent subclasses.

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.schemas.sse_events import SSE_EVENT_TYPES, SSEEvent
for name, cls in SSE_EVENT_TYPES.items():
    assert issubclass(cls, SSEEvent), f'{name} is not SSEEvent subclass'
    print(f'  {name}: {cls.__name__} OK')
print(f'Total: {len(SSE_EVENT_TYPES)} event types — all valid')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/ST-04.txt
```
**PASS if:** All event types validated

### ST-5: graph.py Structural Integrity

Verify graph.py still builds cleanly with all new wiring.

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.core.langgraph.graph import LangGraphAgent
agent = LangGraphAgent()
print(f'LangGraphAgent initialized successfully')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/ST-05.txt
```
**PASS if:** "LangGraphAgent initialized successfully"

---

## Remediation Protocol

1. Read the evidence file for the failing gate
2. Classify the failure:
   - **MISSING_FIX** — code was never implemented
   - **REGRESSION** — prior working code was broken
   - **SCOPE_GAP** — source mission spec was ambiguous or incomplete
   - **FALSE_POSITIVE** — gate command is wrong, code is correct
   - **NOT_IMPLEMENTED** — feature was intentionally deferred
   - **PARTIAL** — partially implemented, needs completion
   - **VIOLATION** — violates architectural constraint (fire-and-forget, BackendClient, etc.)
3. Apply fix following original guardrails:
   - Fire-and-forget pattern for enrichment code (`asyncio.create_task`)
   - BackendClient only (no raw httpx)
   - No direct state mutation
   - Module-level singletons for services
4. Re-run the specific gate command with `tee` to the same evidence file
5. Re-run `make validate-local` to verify no regressions
6. Record the remediation in the completion report with classification, fix description, and evidence path

---

## Enhancement Opportunities

### ENH-1: Reflexion Metrics Dashboard
Add observability for reflexion critique hit rates and severity distribution.

### ENH-2: Fatigue Sentinel Integration Test
Add automated test that simulates N decisions and verifies warning trigger.

### ENH-3: Spaced Repetition Scheduler
Add cron-based scheduler to proactively surface review-due facts.

### ENH-4: Cost Ledger Aggregation API
Add endpoint to query cumulative MCP tool costs per user/deal.

### ENH-5: Node Registry Hot-Reload
Allow adding specialists at runtime without restart.

### ENH-6: BackendClient Retry Policy
Add configurable retry with exponential backoff for transient failures.

### ENH-7: Legal Hold Admin UI
Dashboard component for managing legal holds.

### ENH-8: Citation Audit Threshold Tuning UI
Dashboard settings page for adjusting citation quality thresholds.

### ENH-9: SSE Event Schema Versioning
Add version field to SSE events for backward compatibility.

### ENH-10: PlanAndExecuteGraph Observability
Add step-level logging for plan execution progress.

---

## Scorecard Template

```
QA-COL-BUILD-VERIFY-001A — Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):      [ PASS / FAIL ]
  PF-2 (tsc --noEmit):        [ PASS / FAIL ]
  PF-3 (Docker container):    [ PASS / FAIL ]
  PF-4 (Completion reports):  [ PASS / FAIL ]
  PF-5 (Evidence directory):  [ PASS / FAIL ]

Verification Gates:
  VF-01 (Enrichment pipeline):    __ / 5 PASS
  VF-02 (Node registry):          __ / 4 PASS
  VF-03 (Admin auth):             __ / 3 PASS
  VF-04 (BackendClient):          __ / 4 PASS
  VF-05 (Legal hold):             __ / 4 PASS
  VF-06 (Service completion):     __ / 6 PASS
  VF-07 (Reflexion):              __ / 5 PASS
  VF-08 (Fatigue sentinel):       __ / 3 PASS
  VF-09 (Spaced repetition):      __ / 3 PASS
  VF-10 (Sentiment coach):        __ / 3 PASS
  VF-11 (Ghost knowledge SSE):    __ / 3 PASS
  VF-12 (PlanAndExecute):         __ / 3 PASS
  VF-13 (MCP cost ledger):        __ / 3 PASS
  VF-14 (No regressions):         __ / 4 PASS

Cross-Consistency:
  XC-1 through XC-5:              __ / 5 PASS

Stress Tests:
  ST-1 through ST-5:              __ / 5 PASS

Total: __ / 63 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## Guardrails

1. **This is a QA mission** — do not build new features or redesign existing ones
2. **Remediate, don't redesign** — fix the specific gap, not the whole subsystem
3. **Evidence-based only** — every PASS needs tee'd output in evidence directory
4. **Services-down accommodation** — if Docker is down, live gates become SKIP with note
5. **Preserve prior fixes** — remediation must not revert earlier work
6. **No generated file edits** — per standing deny rules
7. **CRLF safety** — all new files use LF line endings
8. **Follow fire-and-forget pattern** — any enrichment code must use `asyncio.create_task`
9. **P3 items are not failures** — mark as INFO/DEFERRED

---

## Stop Condition

Stop when all 63 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` passes, and the scorecard is complete. Do NOT proceed to building new features or executing other missions.

---

*End of Mission Prompt — QA-COL-BUILD-VERIFY-001A*
