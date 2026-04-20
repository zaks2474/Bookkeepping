# MISSION: QA-MASTER-PROGRAM-VERIFY-001B
## Program-Level Cross-Cutting + SM-4 Late Items + Regression Verification
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: QA-MASTER-PROGRAM-VERIFY-001A (SM-1 verified)
## Successor: None

---

## Preamble: Builder Operating Context

This is the second QA sub-mission verifying the master program ZAKOPS-INTAKE-COL-V2-001. It covers:

1. **SM-4 late additions** (MorningBriefingCard, AnomalyBadge, SentimentCoachPanel) that were NOT part of the earlier COL-V2-BUILD QA missions
2. **Program-level cross-cutting concerns** — readiness gate regression, dependency chain integrity, bookkeeping completeness
3. **Full-stack regression** — verifying SM-1 fixes survive through SM-2/3/4 changes

### Prior QA Coverage

| QA Mission | Scope | Result |
|-----------|-------|--------|
| QA-COL-BUILD-VERIFY-001A | SM-2 + SM-3 agent-api core + intelligence | 67/67 FULL PASS |
| QA-COL-BUILD-VERIFY-001B | SM-4 dashboard UI + compliance pipeline | 56/56 FULL PASS |
| QA-MASTER-PROGRAM-VERIFY-001A | SM-1 pipeline hardening (17 findings) | Pending |

This mission covers what the above three do NOT: SM-4 late-added components, program-level integrity, and regression.

---

## 1. Mission Objective

Verify program-level integrity of ZAKOPS-INTAKE-COL-V2-001 (4 sub-missions, ~86 items, 3 repos). Focus on: SM-4 late items not previously QA'd, cross-sub-mission regression, bookkeeping completeness, and full-stack validation.

Source artifacts:
- `/home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md`
- `/home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md`

Evidence directory: `/home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/`

Out of scope:
- SM-2/SM-3 intelligence services (covered by QA-COL-BUILD-VERIFY-001A)
- SM-4 original dashboard components: CitationIndicator, MemoryStatePanel, SmartPaste, GhostKnowledgeToast, kbar (covered by QA-COL-BUILD-VERIFY-001B)
- SM-1 finding-level verification (covered by QA-MASTER-PROGRAM-VERIFY-001A)

---

## 2. Pre-Flight (PF)

### PF-1: Validation Baseline

```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/PF-01.txt
```

**PASS if:** exit 0

### PF-2: TypeScript Compilation

```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/PF-02.txt
```

**PASS if:** exit 0

### PF-3: Agent-API Container Running

```bash
docker exec zakops-agent-api echo "container alive" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/PF-03.txt
```

**PASS if:** "container alive". If down, Python gates become code-only with SKIP note.

### PF-4: Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b && echo "evidence dir ready" | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/PF-04.txt
```

**PASS if:** Directory created

### PF-5: Program Checkpoint Shows All 4 SM Complete

```bash
cat /home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/PF-05.txt
```

**PASS if:** All 4 sub-missions show COMPLETE status

---

## 3. Verification Families (VF)

## Verification Family 01 -- MorningBriefingCard (SM-4 AC-SM4-1, C18)

### VF-01.1: Component file exists

```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/MorningBriefingCard.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-01-1.txt
```

**PASS if:** File exists

### VF-01.2: 'use client' directive

```bash
head -3 /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/MorningBriefingCard.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-01-2.txt
```

**PASS if:** First line contains 'use client'

### VF-01.3: Component export

```bash
grep -n "export.*function\|export.*default\|export.*MorningBriefing" /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/MorningBriefingCard.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-01-3.txt
```

**PASS if:** Named or default export present

### VF-01.4: Wired into dashboard page

```bash
grep -n "MorningBriefing" /home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-01-4.txt
```

**PASS if:** MorningBriefingCard imported and rendered in dashboard page

**Gate VF-01:** All 4 checks pass. MorningBriefingCard is created and wired.

---

## Verification Family 02 -- AnomalyBadge (SM-4 AC-SM4-1, C19)

### VF-02.1: Component file exists

```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AnomalyBadge.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-02-1.txt
```

**PASS if:** File exists

### VF-02.2: 'use client' directive

```bash
head -3 /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AnomalyBadge.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-02-2.txt
```

**PASS if:** First line contains 'use client'

### VF-02.3: Anomaly indicator logic

```bash
grep -n "anomaly\|severity\|warning\|alert\|critical" /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AnomalyBadge.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-02-3.txt
```

**PASS if:** Anomaly severity rendering logic present

### VF-02.4: Wired into dashboard page

```bash
grep -n "AnomalyBadge" /home/zaks/zakops-agent-api/apps/dashboard/src/app/dashboard/page.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-02-4.txt
```

**PASS if:** AnomalyBadge imported and rendered

**Gate VF-02:** All 4 checks pass. AnomalyBadge renders per-deal anomaly indicators.

---

## Verification Family 03 -- SentimentCoachPanel (SM-4 AC-SM4-1, C22)

### VF-03.1: Panel component exists

```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/SentimentCoachPanel.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-03-1.txt
```

**PASS if:** File exists

### VF-03.2: Sentiment trend visualization

```bash
grep -n "trend\|improving\|declining\|neutral\|volatile\|SentimentTrend" /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/SentimentCoachPanel.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-03-2.txt
```

**PASS if:** Trend types (improving/declining/neutral/volatile) referenced

### VF-03.3: API integration

```bash
grep -n "sentiment\|getSentiment\|fetchSentiment\|/sentiment" /home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-03-3.txt
```

**PASS if:** Sentiment API function defined in api.ts

### VF-03.4: Backend endpoint for sentiment

```bash
grep -n "sentiment" /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-03-4.txt
```

**PASS if:** GET /sentiment/{deal_id} endpoint exists

### VF-03.5: Wired into DealWorkspace

```bash
grep -n "SentimentCoach" /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/DealWorkspace.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-03-5.txt
```

**PASS if:** SentimentCoachPanel imported and rendered in DealWorkspace

**Gate VF-03:** All 5 checks pass. SentimentCoachPanel shows per-deal sentiment trends.

---

## Verification Family 04 -- Surface 9 Compliance (SM-4 Late Components)

### VF-04.1: 'use client' on all 3 new components

```bash
for f in MorningBriefingCard AnomalyBadge; do
  head -3 "/home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/$f.tsx" | grep -q "use client" && echo "$f: use client OK" || echo "$f: MISSING use client"
done
head -3 /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/SentimentCoachPanel.tsx | grep -q "use client" && echo "SentimentCoachPanel: use client OK" || echo "SentimentCoachPanel: MISSING use client"
echo "DONE" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-04-1.txt
```

**PASS if:** All 3 components have 'use client'

### VF-04.2: No Promise.all in new components

```bash
grep -n "Promise\.all[^S]" \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/MorningBriefingCard.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AnomalyBadge.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/SentimentCoachPanel.tsx \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-04-2.txt
```

**PASS if:** No matches (exit 1 = PASS)

### VF-04.3: No console.error in new components

```bash
grep -n "console\.error" \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/MorningBriefingCard.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AnomalyBadge.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/SentimentCoachPanel.tsx \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-04-3.txt
```

**PASS if:** No console.error (console.warn acceptable)

**Gate VF-04:** All 3 checks pass. SM-4 late components follow Surface 9 rules.

---

## Verification Family 05 -- Dashboard Barrel Exports

### VF-05.1: Dashboard index exports new components

```bash
grep -n "MorningBriefing\|AnomalyBadge" /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/index.ts 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-05-1.txt
```

**PASS if:** Both MorningBriefingCard and AnomalyBadge exported from barrel

**Gate VF-05:** Check passes. Components properly exported.

---

## Verification Family 06 -- SM-1 Regression (Post SM-2/3/4 Changes)

### VF-06.1: MCP /process still intact

```bash
grep -c '/process' /home/zaks/zakops-backend/mcp_server/server.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-06-1.txt
```

**PASS if:** Count >= 2 (SM-2/3/4 didn't regress F-1 fix)

### VF-06.2: Agent DATABASE_URL still correct

```bash
grep 'DATABASE_URL' /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-06-2.txt
```

**PASS if:** Still references zakops_agent

### VF-06.3: Idempotency still schema-qualified

```bash
grep -c "zakops.idempotency_keys" /home/zaks/zakops-backend/src/api/shared/middleware/idempotency.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-06-3.txt
```

**PASS if:** Count >= 2

### VF-06.4: Legal hold tables still exist (from SM-2)

```bash
docker exec zakops-agent-db psql -U agent -d zakops_agent -c "\d legal_hold_locks" 2>&1 | head -15 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-06-4.txt
```

**PASS if:** Table schema displayed. **If container down:** `grep -c 'legal_hold_locks' /home/zaks/zakops-agent-api/apps/agent-api/migrations/029_legal_hold.sql` >= 1

### VF-06.5: Reflexion service still importable (from SM-3)

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.reflexion import ReflexionService, CritiqueResult; print('reflexion OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-06-5.txt
```

**PASS if:** "reflexion OK". **If container down:** `ls /home/zaks/zakops-agent-api/apps/agent-api/app/services/reflexion.py` exists

### VF-06.6: GDPR purge still importable (from SM-4)

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.gdpr_service import gdpr_purge; print('gdpr OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-06-6.txt
```

**PASS if:** "gdpr OK". **If container down:** `ls /home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py` exists

**Gate VF-06:** All 6 checks pass. SM-1/2/3/4 deliverables survive without regression.

---

## Verification Family 07 -- Dependency Chain Integrity

### VF-07.1: graph.py still builds (SM-2 core wiring)

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.core.langgraph.graph import LangGraphAgent; print('graph OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-07-1.txt
```

**PASS if:** "graph OK". **If container down:** Code-only check.

### VF-07.2: PlanAndExecuteGraph still importable (SM-3)

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.core.langgraph.plan_execute import PlanAndExecuteGraph; print('plan_execute OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-07-2.txt
```

**PASS if:** "plan_execute OK". **If container down:** Code-only check.

### VF-07.3: All 4 cognitive services importable

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.services.reflexion import reflexion_service
from app.services.fatigue_sentinel import fatigue_sentinel
from app.services.spaced_repetition import spaced_repetition_service
from app.services.sentiment_coach import sentiment_coach
print('all 4 cognitive services OK')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-07-3.txt
```

**PASS if:** "all 4 cognitive services OK". **If container down:** `ls` all 4 files.

### VF-07.4: RetentionPolicy + GDPR chain intact

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.services.retention_policy import retention_policy
from app.services.gdpr_service import gdpr_purge, GdprPurgeReport
print('compliance chain OK')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-07-4.txt
```

**PASS if:** "compliance chain OK"

**Gate VF-07:** All 4 checks pass. Full dependency chain from SM-2 through SM-4 intact.

---

## Verification Family 08 -- Bookkeeping & Documentation

### VF-08.1: CHANGES.md records SM-1 through SM-4

```bash
grep -c "SM-1\|INTAKE-READY\|SM-2\|COL-V2-CORE\|SM-3\|COL-V2-INTEL\|SM-4\|COL-V2-AMBIENT" /home/zaks/bookkeeping/CHANGES.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-08-1.txt
```

**PASS if:** Count >= 4 (at least one reference per sub-mission)

### VF-08.2: Completion reports exist

```bash
for f in \
  COL-V2-BUILD-001A-COMPLETION.md \
  COL-V2-BUILD-001B-COMPLETION.md \
  COL-V2-BUILD-001C-COMPLETION.md \
  QA-COL-BUILD-VERIFY-001A-COMPLETION.md \
  QA-COL-BUILD-VERIFY-001B-COMPLETION.md; do
  if [ -f "/home/zaks/bookkeeping/docs/_qa_evidence/$f" ]; then
    echo "EXISTS: $f"
  else
    echo "MISSING: $f"
  fi
done 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-08-2.txt
```

**PASS if:** All 5 completion reports exist

### VF-08.3: Checkpoint file is current

```bash
grep -c "COMPLETE" /home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-08-3.txt
```

**PASS if:** Count >= 4 (each SM marked COMPLETE)

**Gate VF-08:** All 3 checks pass. Bookkeeping is complete and current.

---

## Verification Family 09 -- Deferred Backlog Preserved

### VF-09.1: Backlog items documented

```bash
grep -c "C6\|C10\|C11\|C13\|C20\|C31\|B6.1\|B6.3\|B8.3\|B9.2\|B2.2\|B2.3\|B3.2\|B1.1" /home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/VF-09-1.txt
```

**PASS if:** Count >= 10 (deferred items are documented, not dropped)

**Gate VF-09:** Check passes. Deferred backlog is preserved for future planning.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Prior QA Evidence Intact

```bash
echo "=== QA-001A evidence ===" && ls /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001a/ | wc -l
echo "=== QA-001B evidence ===" && ls /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/ | wc -l
echo "EVIDENCE CHECK COMPLETE" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/XC-01.txt
```

**PASS if:** QA-001A >= 60 files, QA-001B >= 50 files

### XC-2: Agent-API Boot Clean (No Import Errors)

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.core.langgraph.graph import LangGraphAgent
from app.services.reflexion import reflexion_service
from app.services.fatigue_sentinel import fatigue_sentinel
from app.services.spaced_repetition import spaced_repetition_service
from app.services.sentiment_coach import sentiment_coach
from app.services.retention_policy import retention_policy
from app.services.gdpr_service import gdpr_purge
from app.core.langgraph.plan_execute import PlanAndExecuteGraph
from app.core.langgraph.node_registry import NodeRegistry
print('full import chain clean')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/XC-02.txt
```

**PASS if:** "full import chain clean". **If container down:** SKIP with note.

### XC-3: Contract Surfaces Still Valid

```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tail -5 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/XC-03.txt
```

**PASS if:** "All local validations passed"

### XC-4: No Port 8090 Introduced Across Program

```bash
grep -rn '8090' /home/zaks/zakops-agent-api/apps/ /home/zaks/zakops-backend/src/ 2>&1 | grep -v node_modules | grep -v '.next' | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/XC-04.txt
```

**PASS if:** Zero references to decommissioned port

### XC-5: Checkpoint vs Reality Agreement

```bash
echo "=== Checkpoint ===" && cat /home/zaks/bookkeeping/mission-checkpoints/INTAKE-COL-V2-PROGRAM.md
echo "=== SM-4 files ===" && ls -la \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/MorningBriefingCard.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/dashboard/AnomalyBadge.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/SentimentCoachPanel.tsx \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/XC-05.txt
```

**PASS if:** Checkpoint lists these files and they exist on disk

**XC Gate:** XC-1 through XC-5 all PASS.

---

## 5. Stress Tests (ST)

### ST-1: Full Agent-API Service Load Test

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
import importlib
modules = [
    'app.services.reflexion', 'app.services.fatigue_sentinel',
    'app.services.spaced_repetition', 'app.services.sentiment_coach',
    'app.services.retention_policy', 'app.services.gdpr_service',
    'app.services.replay_service', 'app.services.snapshot_writer',
    'app.services.backend_client', 'app.services.rag_rest',
    'app.core.langgraph.graph', 'app.core.langgraph.plan_execute',
    'app.core.langgraph.node_registry',
]
ok = 0
for m in modules:
    try:
        importlib.import_module(m)
        ok += 1
    except Exception as e:
        print(f'FAIL: {m}: {e}')
print(f'{ok}/{len(modules)} modules loaded successfully')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/ST-01.txt
```

**PASS if:** 13/13 modules loaded. **If container down:** SKIP with note.

### ST-2: TypeScript Strict Mode on SM-4 Late Components

```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit --strict 2>&1 | grep -i "MorningBriefing\|AnomalyBadge\|SentimentCoach" | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/ST-02.txt
```

**PASS if:** No strict-mode errors in the 3 new SM-4 components (exit 1 = no matches = PASS, or empty output from grep)

### ST-3: No Circular Imports in Service Layer

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.services.reflexion import reflexion_service
from app.services.sentiment_coach import sentiment_coach
from app.services.retention_policy import retention_policy
from app.services.gdpr_service import gdpr_purge
from app.core.langgraph.graph import LangGraphAgent
print('no circular imports')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/ST-03.txt
```

**PASS if:** "no circular imports"

### ST-4: BackendClient Monopoly (No Raw httpx in COL-V2 Services)

```bash
grep -rn "import httpx" /home/zaks/zakops-agent-api/apps/agent-api/app/services/ | grep -v 'rag_rest\|llm\|backend_client\|test\|#' 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/ST-04.txt
```

**PASS if:** Zero matches outside rag_rest.py, llm.py, and backend_client.py

### ST-5: SSE Event Registry Complete

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.schemas.sse_events import SSE_EVENT_TYPES
for name, cls in SSE_EVENT_TYPES.items():
    print(f'  {name}: {cls.__name__}')
print(f'Total: {len(SSE_EVENT_TYPES)} event types')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-master-program-verify-001b/ST-05.txt
```

**PASS if:** ghost_knowledge_flags is present in the registry. **If container down:** SKIP with note.

**ST Gate:** ST-1 through ST-5 all PASS.

---

## 6. Remediation Protocol

For any FAIL:

1. Read the evidence file for the failing gate.
2. Classify as one of:
   - `MISSING_FIX` -- code was not implemented
   - `REGRESSION` -- previously working code broken by later sub-mission
   - `SCOPE_GAP` -- edge case not covered
   - `FALSE_POSITIVE` -- gate check is incorrect
   - `NOT_IMPLEMENTED` -- feature entirely absent
   - `PARTIAL` -- partially implemented
   - `VIOLATION` -- violates architectural constraint
3. Apply fix following original guardrails (Surface 9 for dashboard, singleton pattern for services).
4. Re-run the specific gate command with tee.
5. Re-run `make validate-local` + `npx tsc --noEmit`.
6. Record remediation in completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: MorningBriefing Unit Tests
Add React Testing Library tests for MorningBriefingCard rendering states.

### ENH-2: AnomalyBadge Severity Theming
Map anomaly severity to design system color tokens.

### ENH-3: SentimentCoach Trend Chart
Add mini sparkline visualization for sentiment trend.

### ENH-4: Program-Level Integration Test Suite
End-to-end test: inject quarantine → approve → deal → agent chat → enrichment.

### ENH-5: Regression Gate Automation
`make regression-check` target that runs SM-1 readiness gates + SM-2/3/4 import checks.

### ENH-6: Deferred Backlog Tracking
Kanban board or issue tracker for the 14 deferred items.

### ENH-7: Shadow-Mode Analytics
Dashboard widget showing shadow-mode item quality metrics.

### ENH-8: SentimentCoach History
Store sentiment readings over time for trend analysis.

### ENH-9: AnomalyBadge Drill-Down
Click anomaly badge to see full anomaly report.

### ENH-10: Cross-Sub-Mission Dependency Graph
Automated visualization of which services depend on which sub-mission deliverables.

---

## 8. Scorecard Template

```text
QA-MASTER-PROGRAM-VERIFY-001B -- Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):      [ PASS / FAIL ]
  PF-2 (tsc --noEmit):        [ PASS / FAIL ]
  PF-3 (container alive):     [ PASS / FAIL / SKIP ]
  PF-4 (evidence directory):  [ PASS / FAIL ]
  PF-5 (checkpoint status):   [ PASS / FAIL ]

Verification Gates:
  VF-01 (MorningBriefingCard):    __ / 4 PASS
  VF-02 (AnomalyBadge):           __ / 4 PASS
  VF-03 (SentimentCoachPanel):    __ / 5 PASS
  VF-04 (Surface 9 compliance):   __ / 3 PASS
  VF-05 (Barrel exports):         __ / 1 PASS
  VF-06 (SM-1 regression):        __ / 6 PASS
  VF-07 (Dependency chain):       __ / 4 PASS
  VF-08 (Bookkeeping):            __ / 3 PASS
  VF-09 (Deferred backlog):       __ / 1 PASS

Cross-Consistency:
  XC-1 through XC-5:              __ / 5 PASS

Stress Tests:
  ST-1 through ST-5:              __ / 5 PASS

Total: __ / 41 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **This is a QA mission** -- do not build new features or redesign existing ones.
2. **Remediate, don't redesign** -- fix the specific gap, not the whole subsystem.
3. **Evidence-based only** -- every PASS needs tee'd output in evidence directory.
4. **Services-down accommodation** -- if Docker containers are down, import gates become SKIP with note. Verify source files exist instead.
5. **Preserve prior QA results** -- remediation must not invalidate QA-COL-BUILD-VERIFY-001A/B or QA-MASTER-PROGRAM-VERIFY-001A results.
6. **No generated file edits** -- per standing deny rules.
7. **Surface 9 applies** -- all dashboard component fixes must follow design system rules.
8. **No Promise.all** -- Promise.allSettled with typed empty fallbacks only.
9. **P3 items are not failures** -- mark as INFO/DEFERRED.
10. **Re-run dependent gates after any remediation.**

---

## 10. Stop Condition

Stop when all 41 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` and `npx tsc --noEmit` both pass, and the scorecard is complete. Do NOT proceed to building new features or executing other missions.

---

*End of Mission Prompt -- QA-MASTER-PROGRAM-VERIFY-001B*
