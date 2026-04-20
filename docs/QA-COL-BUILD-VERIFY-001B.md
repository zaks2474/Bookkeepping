# MISSION: QA-COL-BUILD-VERIFY-001B
## Dashboard UI + Compliance Pipeline Verification
## Date: 2026-02-13
## Classification: QA Verification & Remediation
## Prerequisite: COL-V2-BUILD-001C (COMPLETE)
## Successor: None

---

## Preamble: Builder Operating Context

This is an independent QA verification mission. It verifies implementation quality for COL-V2-BUILD-001C (Dashboard UI + Compliance Pipeline) and applies surgical remediation only if a gate fails. The builder already loads CLAUDE.md, MEMORY.md, hooks, rules, and deny rules at session start. This mission adds verification-specific scope and evidence requirements.

---

## 1. Mission Objective

Independent verification of COL-V2-BUILD-001C (10 AC, 3 phases, 6 files created, 4 modified). Verifies citation UI, memory panel, momentum colors, smart paste, ghost knowledge toast, kbar commands, retention policy, GDPR purge, and compliance purge endpoint.

This mission will **verify, cross-check, stress-test, and remediate** the deliverables from the source execution mission. It covers a mixed surface: TypeScript dashboard components (Surface 9 compliance) and Python compliance services (agent-api Docker container).

Source artifacts:
- `/home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001C-COMPLETION.md`
- `/home/zaks/bookkeeping/mission-checkpoints/COL-V2-BUILD-001C.md`

Evidence directory: `/home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/`

Out of scope:
- COL-V2-BUILD-001A and 001B deliverables (verified separately; regression check only via XC-5)
- New feature development or redesign of existing components
- Backend API changes (zakops-backend)

---

## 2. Pre-Flight (PF)

### PF-1: Validation Baseline

```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/PF-01.txt
```

**PASS if:** exit 0. If not, stop -- codebase is broken before QA starts.

### PF-2: TypeScript Compilation

```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/PF-02.txt
```

**PASS if:** exit 0

### PF-3: Agent-API Docker Container Running

```bash
docker exec zakops-agent-api echo "container alive" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/PF-03.txt
```

**PASS if:** prints "container alive". If container is down, Python gates (VF-08, VF-09, VF-10, ST-4, ST-5, XC-5) become code-only verification with SKIP note.

### PF-4: Source Mission Completion Report Exists

```bash
ls -la /home/zaks/bookkeeping/docs/_qa_evidence/COL-V2-BUILD-001C-COMPLETION.md 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/PF-04.txt
```

**PASS if:** file exists

### PF-5: Evidence Directory

```bash
mkdir -p /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b && echo "evidence dir ready" | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/PF-05.txt
```

**PASS if:** directory created or exists

---

## 3. Verification Families (VF)

## Verification Family 01 -- CitationIndicator Component (001C AC-1)

### VF-01.1: Component file exists

```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-01-1.txt
```

**PASS if:** File exists

### VF-01.2: Green/amber/red threshold logic

```bash
grep -n "0\.5\|0\.3\|green\|amber\|yellow\|red\|Orphan\|Strong\|Weak" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-01-2.txt
```

**PASS if:** All 3 threshold bands present (>= 0.5 green, >= 0.3 amber, < 0.3 red)

### VF-01.3: Component exports

```bash
grep -n "export.*function\|export.*default\|export.*CitationIndicator" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-01-3.txt
```

**PASS if:** Named export for CitationIndicator

### VF-01.4: score ?? similarity fallback

```bash
grep -n "score.*similarity\|similarity.*score\|\?\?" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-01-4.txt
```

**PASS if:** Nullish coalescing for score/similarity

**Gate VF-01:** All 4 checks pass. CitationIndicator renders correct color bands.

---

## Verification Family 02 -- RefinedBadge Component (001C AC-2)

### VF-02.1: RefinedBadge export

```bash
grep -n "export.*RefinedBadge\|function RefinedBadge" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-02-1.txt
```

**PASS if:** RefinedBadge exported

### VF-02.2: Purple badge styling

```bash
grep -n "purple\|Refined\|sparkle\|IconSparkles" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-02-2.txt
```

**PASS if:** Purple styling + sparkle icon + "Refined" text

### VF-02.3: critiqueResult null guard

```bash
grep -n "critiqueResult\|!critiqueResult\|null" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-02-3.txt
```

**PASS if:** Returns null when critiqueResult is absent

**Gate VF-02:** All 3 checks pass. RefinedBadge renders for reflexion-critiqued messages.

---

## Verification Family 03 -- MemoryStatePanel (001C AC-3)

### VF-03.1: Component file exists

```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/MemoryStatePanel.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-03-1.txt
```

**PASS if:** File exists

### VF-03.2: 3-tier display

```bash
grep -n "working\|recall\|archival\|Working\|Recall\|Archival" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/MemoryStatePanel.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-03-2.txt
```

**PASS if:** All 3 memory tiers referenced

### VF-03.3: Server-side count props (no .length)

```bash
grep -n "Count\|count\|\.length" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/MemoryStatePanel.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-03-3.txt
```

**PASS if:** Count props present, no .length usage for display

**Gate VF-03:** All 3 checks pass. MemoryStatePanel shows 3-tier memory display.

---

## Verification Family 04 -- DealHeader Momentum Colors (001C AC-4)

### VF-04.1: getMomentumConfig function

```bash
grep -n "getMomentumConfig\|momentumConfig\|momentum" /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/DealHeader.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-04-1.txt
```

**PASS if:** getMomentumConfig function defined

### VF-04.2: Color band thresholds (70/40)

```bash
grep -n "70\|40\|green\|yellow\|red\|TrendingUp\|TrendingDown" /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/DealHeader.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-04-2.txt
```

**PASS if:** 70 and 40 thresholds with green/amber/red colors

### VF-04.3: momentumScore prop

```bash
grep -n "momentumScore" /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/DealHeader.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-04-3.txt
```

**PASS if:** momentumScore in props interface and used in JSX

### VF-04.4: Momentum badge in metrics row

```bash
grep -A 3 "Momentum" /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/DealHeader.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-04-4.txt
```

**PASS if:** Momentum label with Badge component

**Gate VF-04:** All 4 checks pass. DealHeader shows momentum with color bands.

---

## Verification Family 05 -- SmartPaste (001C AC-5)

### VF-05.1: Component file exists

```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/SmartPaste.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-05-1.txt
```

**PASS if:** File exists

### VF-05.2: Entity regex patterns

```bash
grep -n "CURRENCY_RE\|NUMBER_RE\|DATE_RE\|PROPER_NOUN_RE\|RegExp" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/SmartPaste.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-05-2.txt
```

**PASS if:** At least 3 regex patterns for entity extraction

### VF-05.3: COMMON_PHRASES filter

```bash
grep -n "COMMON_PHRASES\|common.*phrases\|false.*positive" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/SmartPaste.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-05-3.txt
```

**PASS if:** COMMON_PHRASES filter set exists

### VF-05.4: useSmartPaste hook export

```bash
grep -n "export.*useSmartPaste\|function useSmartPaste" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/SmartPaste.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-05-4.txt
```

**PASS if:** useSmartPaste hook exported

**Gate VF-05:** All 4 checks pass. SmartPaste extracts entities with false positive filtering.

---

## Verification Family 06 -- GhostKnowledgeToast (001C AC-6)

### VF-06.1: Component file exists

```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/GhostKnowledgeToast.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-06-1.txt
```

**PASS if:** File exists

### VF-06.2: Confirm/Dismiss actions

```bash
grep -n "Confirm\|Dismiss\|confirm\|dismiss\|onConfirm\|onDismiss" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/GhostKnowledgeToast.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-06-2.txt
```

**PASS if:** Both Confirm and Dismiss callbacks present

### VF-06.3: Sonner toast integration

```bash
grep -n "sonner\|toast\|Toast" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/GhostKnowledgeToast.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-06-3.txt
```

**PASS if:** Sonner toast import and usage

### VF-06.4: Toast duration

```bash
grep -n "duration\|15000\|15.*sec" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/GhostKnowledgeToast.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-06-4.txt
```

**PASS if:** 15-second duration configured

**Gate VF-06:** All 4 checks pass. GhostKnowledgeToast fires with Confirm/Dismiss actions.

---

## Verification Family 07 -- kbar Intelligence Commands (001C AC-7)

### VF-07.1: COL-V2 commands registered

```bash
grep -n "Search Deals\|Open Chat\|View Deal Brain\|View Pending Actions\|Review Approvals" /home/zaks/zakops-agent-api/apps/dashboard/src/components/kbar/index.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-07-1.txt
```

**PASS if:** At least 4 of 5 commands found

### VF-07.2: kbar useRegisterActions hook

```bash
grep -n "useRegisterActions\|registerActions\|actions" /home/zaks/zakops-agent-api/apps/dashboard/src/components/kbar/index.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-07-2.txt
```

**PASS if:** Actions registered with kbar

**Gate VF-07:** All 2 checks pass. kbar extended with COL-V2 intelligence commands.

---

## Verification Family 08 -- RetentionPolicy (001C AC-8)

### VF-08.1: Import

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.retention_policy import retention_policy, RetentionPolicy, RETENTION_TIERS; print('retention import OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-08-1.txt
```

**PASS if:** "retention import OK". **If container down:** SKIP with note, verify source file exists instead.

### VF-08.2: 4 retention tiers

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.services.retention_policy import RETENTION_TIERS
for tier, days in RETENTION_TIERS.items():
    print(f'  {tier}: {days}d' if days else f'  {tier}: forever')
print(f'Total tiers: {len(RETENTION_TIERS)}')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-08-2.txt
```

**PASS if:** 4 tiers (default=30, deal_scoped=90, legal_hold=365, compliance=None)

### VF-08.3: evaluate() method

```bash
grep -n "def evaluate" /home/zaks/zakops-agent-api/apps/agent-api/app/services/retention_policy.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-08-3.txt
```

**PASS if:** evaluate method found

### VF-08.4: Protected tier hierarchy

```bash
grep -n "compliance.*legal_hold\|has_compliance_flag\|has_legal_hold\|is_protected" /home/zaks/zakops-agent-api/apps/agent-api/app/services/retention_policy.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-08-4.txt
```

**PASS if:** Compliance > legal_hold > deal_scoped > default hierarchy

**Gate VF-08:** All 4 checks pass. RetentionPolicy evaluates with correct tier hierarchy.

---

## Verification Family 09 -- GDPR Purge Service (001C AC-9)

### VF-09.1: Import

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "from app.services.gdpr_service import gdpr_purge, GdprPurgeReport; print('gdpr import OK')" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-09-1.txt
```

**PASS if:** "gdpr import OK". **If container down:** SKIP with note, verify source file exists instead.

### VF-09.2: Legal hold check (LEFT JOIN)

```bash
grep -n "legal_hold_locks\|LEFT JOIN\|has_legal_hold" /home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-09-2.txt
```

**PASS if:** LEFT JOIN legal_hold_locks + has_legal_hold check

### VF-09.3: Skip + log for held threads

```bash
grep -n "gdpr_skip\|skipped\|legal_hold_log" /home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-09-3.txt
```

**PASS if:** 'gdpr_skip' action logged to legal_hold_log

### VF-09.4: Cascade delete (messages, snapshots, summaries, threads)

```bash
grep -n "DELETE FROM" /home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-09-4.txt
```

**PASS if:** 4 DELETE statements (messages, turn_snapshots, thread_summaries, threads)

### VF-09.5: Audit report model

```bash
grep -n "class GdprPurgeReport\|deleted_count\|skipped_count\|skipped_thread_ids" /home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-09-5.txt
```

**PASS if:** GdprPurgeReport with deleted_count, skipped_count, skipped_thread_ids

**Gate VF-09:** All 5 checks pass. GDPR purge skips legal-held threads and logs all actions.

---

## Verification Family 10 -- Compliance Purge Endpoint (001C AC-10)

### VF-10.1: Route exists

```bash
grep -n "admin/compliance/purge" /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-10-1.txt
```

**PASS if:** POST route for /admin/compliance/purge

### VF-10.2: Admin guard

```bash
grep -A 8 "compliance/purge" /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py | grep "_require_admin" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-10-2.txt
```

**PASS if:** _require_admin(session) call in handler

### VF-10.3: Calls gdpr_purge

```bash
grep -A 10 "compliance/purge" /home/zaks/zakops-agent-api/apps/agent-api/app/api/v1/chatbot.py | grep "gdpr_purge" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-10-3.txt
```

**PASS if:** gdpr_purge call in handler

**Gate VF-10:** All 3 checks pass. Compliance purge endpoint is admin-guarded.

---

## Verification Family 11 -- Integration in Chat Page (001C AC-1, AC-2)

### VF-11.1: CitationIndicator imported in page.tsx

```bash
grep -n "CitationIndicator\|RefinedBadge" /home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-11-1.txt
```

**PASS if:** Import + usage of CitationIndicator and RefinedBadge

### VF-11.2: critiqueResult field on ChatMessage

```bash
grep -n "critiqueResult" /home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-11-2.txt
```

**PASS if:** critiqueResult field in ChatMessage interface

**Gate VF-11:** All 2 checks pass. Citation UI integrated into chat page.

---

## Verification Family 12 -- Surface 9 Compliance (Dashboard Design System)

### VF-12.1: 'use client' directive on all new components

```bash
for f in CitationIndicator MemoryStatePanel SmartPaste GhostKnowledgeToast; do
  head -3 "/home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/$f.tsx" | grep -q "use client" && echo "$f: use client OK" || echo "$f: MISSING use client"
done 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-12-1.txt
```

**PASS if:** All 4 components have 'use client'

### VF-12.2: No Promise.all in new components

```bash
grep -n "Promise\.all[^S]" \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/MemoryStatePanel.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/SmartPaste.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/GhostKnowledgeToast.tsx \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-12-2.txt
```

**PASS if:** No matches (exit 1 = no banned Promise.all)

### VF-12.3: No console.error in new components (console.warn only for degradation)

```bash
grep -n "console\.error" \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/CitationIndicator.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/MemoryStatePanel.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/SmartPaste.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/GhostKnowledgeToast.tsx \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/VF-12-3.txt
```

**PASS if:** No console.error (console.warn is acceptable)

**Gate VF-12:** All 3 checks pass. New dashboard components follow Surface 9 patterns.

---

## 4. Cross-Consistency Checks (XC)

### XC-1: Completion Report vs Codebase Agreement

```bash
for f in \
  apps/dashboard/src/components/chat/CitationIndicator.tsx \
  apps/dashboard/src/components/chat/MemoryStatePanel.tsx \
  apps/dashboard/src/components/chat/SmartPaste.tsx \
  apps/dashboard/src/components/chat/GhostKnowledgeToast.tsx \
  apps/agent-api/app/services/retention_policy.py \
  apps/agent-api/app/services/gdpr_service.py; do
  if [ -f "/home/zaks/zakops-agent-api/$f" ]; then
    echo "EXISTS: $f"
  else
    echo "MISSING: $f"
  fi
done 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/XC-01.txt
```

**PASS if:** All 6 files exist

### XC-2: Chat page integration consistency

Verify ChatMessage interface has critiqueResult and citation rendering uses CitationIndicator.

```bash
grep -n "critiqueResult\|CitationIndicator\|RefinedBadge" /home/zaks/zakops-agent-api/apps/dashboard/src/app/chat/page.tsx | head -20 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/XC-02.txt
```

**PASS if:** All 3 identifiers found in page.tsx

### XC-3: DealHeader momentum consistency with DealBrain

```bash
grep -n "momentum\|momentumColor\|momentumIcon\|getMomentumConfig" \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/DealHeader.tsx \
  /home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/DealBrain.tsx \
  2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/XC-03.txt
```

**PASS if:** Both DealHeader and DealBrain have momentum color logic (complementary, not conflicting)

### XC-4: GDPR purge uses correct table names matching migration

```bash
grep "DELETE FROM\|legal_hold_locks\|legal_hold_log" /home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/XC-04.txt
```

**PASS if:** Table names match migration (messages, turn_snapshots, thread_summaries, threads, legal_hold_locks, legal_hold_log)

### XC-5: 001A + 001B deliverables still intact

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.core.langgraph.graph import LangGraphAgent
from app.services.reflexion import reflexion_service
from app.core.langgraph.node_registry import NodeRegistry
print('001A+001B deliverables intact')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/XC-05.txt
```

**PASS if:** "001A+001B deliverables intact". **If container down:** SKIP with note.

**XC Gate:** XC-1 through XC-5 all PASS.

---

## 5. Stress Tests (ST)

### ST-1: SmartPaste False Positive Resilience

Check COMMON_PHRASES filter size is reasonable.

```bash
grep -c "COMMON_PHRASES\|Set\|new Set" /home/zaks/zakops-agent-api/apps/dashboard/src/components/chat/SmartPaste.tsx 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/ST-01.txt
```

**PASS if:** COMMON_PHRASES defined as a Set with entries

### ST-2: Legal Hold Edge Cases in GDPR Code

Verify both gdpr_skip AND gdpr_delete are logged to legal_hold_log.

```bash
grep -c "INSERT INTO legal_hold_log" /home/zaks/zakops-agent-api/apps/agent-api/app/services/gdpr_service.py 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/ST-02.txt
```

**PASS if:** count >= 2 (one for skip, one for delete)

### ST-3: TypeScript Strict Mode

Verify all new TSX files compile with strict TypeScript.

```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit --strict 2>&1 | head -20 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/ST-03.txt
```

**PASS if:** exit 0 or only pre-existing strict mode issues (not in new files)

### ST-4: SSE Event Type for Ghost Knowledge

Verify ghost_knowledge_flags event type is still registered after 001C changes.

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.schemas.sse_events import SSE_EVENT_TYPES
assert 'ghost_knowledge_flags' in SSE_EVENT_TYPES, 'ghost_knowledge_flags MISSING'
print(f'ghost_knowledge_flags: {SSE_EVENT_TYPES[\"ghost_knowledge_flags\"].__name__}')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/ST-04.txt
```

**PASS if:** GhostKnowledgeFlagsEvent found. **If container down:** SKIP with note.

### ST-5: Retention Policy Functional Test

Verify evaluate() returns correct results for boundary cases.

```bash
docker exec zakops-agent-api /app/.venv/bin/python -c "
from app.services.retention_policy import retention_policy
from datetime import datetime, timedelta, timezone

# Test 1: Default tier, expired
r1 = retention_policy.evaluate('t1', created_at=datetime.now(timezone.utc) - timedelta(days=31))
assert r1.tier == 'default' and r1.is_expired, f'Test 1 failed: {r1}'
# Test 2: Deal-scoped, not expired
r2 = retention_policy.evaluate('t2', scope_type='deal', created_at=datetime.now(timezone.utc) - timedelta(days=30))
assert r2.tier == 'deal_scoped' and not r2.is_expired, f'Test 2 failed: {r2}'
# Test 3: Legal hold -- protected
r3 = retention_policy.evaluate('t3', has_legal_hold=True)
assert r3.is_protected, f'Test 3 failed: {r3}'
# Test 4: Compliance -- forever, protected
r4 = retention_policy.evaluate('t4', has_compliance_flag=True)
assert r4.retention_days is None and r4.is_protected, f'Test 4 failed: {r4}'
print('All 4 functional tests PASS')
" 2>&1 | tee /home/zaks/bookkeeping/docs/_qa_evidence/qa-col-build-verify-001b/ST-05.txt
```

**PASS if:** "All 4 functional tests PASS". **If container down:** SKIP with note.

**ST Gate:** ST-1 through ST-5 all PASS.

---

## 6. Remediation Protocol

For any FAIL:

1. Read the evidence file for the failing gate.
2. Classify as one of:
   - `MISSING_FIX` -- code was not implemented
   - `REGRESSION` -- previously working code broken
   - `SCOPE_GAP` -- edge case not covered by source mission
   - `FALSE_POSITIVE` -- gate check is incorrect, code is fine
   - `NOT_IMPLEMENTED` -- feature entirely absent
   - `PARTIAL` -- partially implemented, needs completion
   - `VIOLATION` -- violates architectural constraint
3. Apply fix following original guardrails (Surface 9 for dashboard, legal hold protection for compliance).
4. Re-run the specific gate command with tee.
5. Re-run `make validate-local` + `npx tsc --noEmit`.
6. Record remediation in completion report.

---

## 7. Enhancement Opportunities (ENH)

### ENH-1: CitationIndicator Unit Tests
Add React Testing Library tests for threshold boundary cases.

### ENH-2: MemoryStatePanel Live Data Integration
Connect to actual memory state API endpoint instead of prop-passing.

### ENH-3: SmartPaste International Currency Support
Extend CURRENCY_RE to handle EUR, GBP, CAD symbols.

### ENH-4: GhostKnowledgeToast Auto-Confirm
Add user preference for auto-confirming ghost knowledge flags.

### ENH-5: Retention Policy Admin Dashboard
Dashboard widget showing thread retention tier distribution.

### ENH-6: GDPR Purge Dry-Run Mode
Add dry_run flag to preview what would be deleted without executing.

### ENH-7: kbar Intelligence Command Keyboard Shortcuts
Add individual shortcuts (Ctrl+D for deals, Ctrl+B for brain, etc.)

### ENH-8: DealHeader Momentum Trend Arrow Animation
Animate momentum change direction transitions.

### ENH-9: Compliance Purge Rate Limiting
Add rate limit to /admin/compliance/purge to prevent abuse.

### ENH-10: SmartPaste Entity Confidence Scoring
Add confidence scores to extracted entities for better filtering.

---

## 8. Scorecard Template

```text
QA-COL-BUILD-VERIFY-001B -- Final Scorecard
Date: ____________
Auditor: ____________

Pre-Flight:
  PF-1 (validate-local):      [ PASS / FAIL ]
  PF-2 (tsc --noEmit):        [ PASS / FAIL ]
  PF-3 (Docker container):    [ PASS / FAIL ]
  PF-4 (Completion report):   [ PASS / FAIL ]
  PF-5 (Evidence directory):  [ PASS / FAIL ]

Verification Gates:
  VF-01 (CitationIndicator):     __ / 4 PASS
  VF-02 (RefinedBadge):          __ / 3 PASS
  VF-03 (MemoryStatePanel):      __ / 3 PASS
  VF-04 (DealHeader momentum):   __ / 4 PASS
  VF-05 (SmartPaste):            __ / 4 PASS
  VF-06 (GhostKnowledgeToast):   __ / 4 PASS
  VF-07 (kbar commands):         __ / 2 PASS
  VF-08 (RetentionPolicy):       __ / 4 PASS
  VF-09 (GDPR purge):            __ / 5 PASS
  VF-10 (Compliance endpoint):   __ / 3 PASS
  VF-11 (Chat page integration): __ / 2 PASS
  VF-12 (Surface 9 compliance):  __ / 3 PASS

Cross-Consistency:
  XC-1 through XC-5:             __ / 5 PASS

Stress Tests:
  ST-1 through ST-5:             __ / 5 PASS

Total: __ / 56 gates PASS, __ FAIL, __ INFO

Remediations Applied: __
Enhancement Opportunities: 10 (ENH-1 through ENH-10)

Overall Verdict: [ FULL PASS / CONDITIONAL PASS / FAIL ]
```

---

## 9. Guardrails

1. **This is a QA mission** -- do not build new features or redesign existing ones.
2. **Remediate, don't redesign** -- fix the specific gap, not the whole subsystem.
3. **Evidence-based only** -- every PASS needs tee'd output in evidence directory.
4. **Surface 9 applies** -- all dashboard component changes must follow design system rules.
5. **Services-down accommodation** -- if Docker is down, Python gates become SKIP with note.
6. **Preserve prior fixes** -- remediation must not revert 001A/001B work.
7. **No generated file edits** -- per standing deny rules.
8. **No Promise.all** -- Promise.allSettled with typed empty fallbacks only.
9. **P3 items are not failures** -- mark as INFO/DEFERRED.
10. **Re-run dependent gates after any remediation.**

---

## 10. Stop Condition

Stop when all 56 verification gates pass (or are justified as SKIP/DEFERRED/FALSE_POSITIVE), all remediations are applied and re-verified, `make validate-local` and `npx tsc --noEmit` both pass, and the scorecard is complete. Do NOT proceed to building new features or executing other missions.

---

*End of Mission Prompt -- QA-COL-BUILD-VERIFY-001B*
