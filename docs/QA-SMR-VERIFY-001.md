# MISSION: QA-SMR-VERIFY-001
## Independent QA Verification — SYSTEM-MATURITY-REMEDIATION-001
## Date: 2026-02-20
## Classification: Paired QA (Read-Only Verification)
## Prerequisite: SYSTEM-MATURITY-REMEDIATION-001 (Complete 2026-02-20)
## Successor: None

---

## Context

SYSTEM-MATURITY-REMEDIATION-001 delivered a full-stack gap remediation across 12 phases (P0-P11), 35 acceptance criteria, touching 8 contract surfaces. It added 8 new agent tools (14→22), document upload/RAG, observability endpoints, LLM summarization, profile enrichment, and an analytics dashboard page. This QA mission independently verifies every claim in the completion report.

**Source artifacts:**
- Completion report: `/home/zaks/bookkeeping/docs/SYSTEM-MATURITY-REMEDIATION-001-COMPLETION.md`
- Branch: `feat/system-maturity-remediation-001`

**Contract Surfaces Affected:** 1, 2, 8, 9, 10, 12, 13, 17

---

## Pre-Flight (PF-1..4)

### PF-1: Baseline validation
```bash
cd /home/zaks/zakops-agent-api && make validate-local 2>&1 | tee /tmp/qa-smr/PF-1-validate-local.txt
# GATE: Last line contains "All local validations passed"
```

### PF-2: TypeScript compilation
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx tsc --noEmit 2>&1 | tee /tmp/qa-smr/PF-2-tsc.txt
# GATE: Exit code 0, no errors
```

### PF-3: Agent API health
```bash
curl -sf http://localhost:8095/health 2>&1 | tee /tmp/qa-smr/PF-3-health.txt
# GATE: {"status":"healthy"...}
```

### PF-4: Boot diagnostics
```bash
# Verify boot diagnostics show ALL CLEAR
# GATE: 0 warnings, 0 failures
```

---

## Verification Families

### VF-01: Tool Registry (AC-5, AC-23, AC-34)

**VF-01.1: Tool count = 22**
```bash
COMPOSE_PROJECT_NAME=zakops docker compose logs agent-api 2>&1 | grep "tool_count" | tail -1 | tee /tmp/qa-smr/VF-01-1-tool-count.txt
# GATE: tool_count=22
```

**VF-01.2: HITL tools = 8**
```bash
grep -c "HITL_TOOLS" /home/zaks/zakops-agent-api/apps/agent-api/app/schemas/agent.py | tee /tmp/qa-smr/VF-01-2-hitl.txt
# Also: grep the actual frozenset and count entries
grep -A 20 "HITL_TOOLS" /home/zaks/zakops-agent-api/apps/agent-api/app/schemas/agent.py | tee -a /tmp/qa-smr/VF-01-2-hitl.txt
# GATE: 8 tools in HITL_TOOLS frozenset
```

**VF-01.3: SCOPE_TOOL_MAP completeness**
```bash
# Extract all unique tool names from SCOPE_TOOL_MAP and count
grep -oP '"[a-z_]+"' /home/zaks/zakops-agent-api/apps/agent-api/app/core/security/tool_scoping.py | sort -u | tee /tmp/qa-smr/VF-01-3-scope-tools.txt
# GATE: 22 unique tool names
```

**VF-01.4: system.md tool list matches registry**
```bash
# Count numbered tools in system.md
grep -cP '^\d+\.' /home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/system.md | tee /tmp/qa-smr/VF-01-4-prompt-tools.txt
# GATE: 22 tools listed
```

**VF-01.5: 5 document/email/entity tools present**
```bash
grep -c "def list_deal_documents\|def search_deal_documents\|def analyze_document\|def get_deal_email_threads\|def lookup_entity" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/document_tools.py | tee /tmp/qa-smr/VF-01-5-doc-tools.txt
# GATE: 5
```

**VF-01.6: interview_user tool present**
```bash
grep -c "def interview_user" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/profile_tools.py | tee /tmp/qa-smr/VF-01-6-interview.txt
# GATE: 1
```

### VF-02: Agent API Endpoints (AC-14, AC-25, AC-27, AC-28, AC-29, AC-30)

**VF-02.1: Stats endpoint**
```bash
curl -sf http://localhost:8095/api/v1/agent/stats | python3 -m json.tool | tee /tmp/qa-smr/VF-02-1-stats.txt
# GATE: JSON with today_cost_usd, month_cost_usd, total_cost_usd, top_tools, background_tasks
```

**VF-02.2: Decisions endpoint**
```bash
curl -sf "http://localhost:8095/api/v1/agent/decisions?limit=5" | python3 -m json.tool | tee /tmp/qa-smr/VF-02-2-decisions.txt
# GATE: JSON with decisions array and total count
```

**VF-02.3: Alerts endpoint**
```bash
curl -sf http://localhost:8095/api/v1/agent/alerts | python3 -m json.tool | tee /tmp/qa-smr/VF-02-3-alerts.txt
# GATE: JSON with alerts array and total count
```

**VF-02.4: Conviction endpoint**
```bash
curl -sf http://localhost:8095/api/v1/agent/conviction/DL-0001 | python3 -m json.tool | tee /tmp/qa-smr/VF-02-4-conviction.txt
# GATE: JSON with score (0-100) and components breakdown
```

**VF-02.5: Knowledge endpoint**
```bash
curl -sf http://localhost:8095/api/v1/agent/knowledge/test-thread | python3 -m json.tool | tee /tmp/qa-smr/VF-02-5-knowledge.txt
# GATE: JSON with summary, brain_facts, user_profile, decisions, checkpoint fields
```

**VF-02.6: Thread archive endpoint**
```bash
curl -sf -X POST http://localhost:8095/api/v1/agent/threads/archive -H "Content-Type: application/json" -d '{"deal_id":"DL-QA-TEST"}' | python3 -m json.tool | tee /tmp/qa-smr/VF-02-6-archive.txt
# GATE: JSON with archived_count and deal_id
```

**VF-02.7: Tasks health endpoint**
```bash
curl -sf http://localhost:8095/api/v1/agent/tasks/health | python3 -m json.tool | tee /tmp/qa-smr/VF-02-7-tasks-health.txt
# GATE: JSON with active, completed, failed counts
```

### VF-03: Memory & Summarization (AC-24, AC-26)

**VF-03.1: Abstractive summarization function exists**
```bash
grep -n "async def abstractive_summarize" /home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py | tee /tmp/qa-smr/VF-03-1-abstractive.txt
# GATE: Function found
```

**VF-03.2: Retention policy function exists**
```bash
grep -n "async def enforce_retention" /home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py | tee /tmp/qa-smr/VF-03-2-retention.txt
# GATE: Function found with 90-day and 365-day thresholds
```

**VF-03.3: Summary pruning function exists**
```bash
grep -n "async def prune_old_summaries" /home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py | tee /tmp/qa-smr/VF-03-3-pruning.txt
# GATE: Function found
```

**VF-03.4: Memory backfill utility**
```bash
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/memory_backfill.py | tee /tmp/qa-smr/VF-03-4-backfill.txt
grep -c "def find_unsummarized_threads\|def backfill_thread\|async def main" /home/zaks/zakops-agent-api/apps/agent-api/app/services/memory_backfill.py | tee -a /tmp/qa-smr/VF-03-4-backfill.txt
# GATE: File exists, 3 key functions present
```

**VF-03.5: USE_LLM_SUMMARIZATION env var**
```bash
grep "USE_LLM_SUMMARIZATION" /home/zaks/zakops-agent-api/apps/agent-api/app/services/summarizer.py | tee /tmp/qa-smr/VF-03-5-env.txt
# GATE: Environment variable read with default
```

### VF-04: Profile & Onboarding (AC-2, AC-3, AC-31)

**VF-04.1: Profile enricher service**
```bash
grep -c "def enrich_profile_from_tool_calls\|def get_profile_insights\|def format_profile_insights" /home/zaks/zakops-agent-api/apps/agent-api/app/services/profile_enricher.py | tee /tmp/qa-smr/VF-04-1-enricher.txt
# GATE: 3 functions present
```

**VF-04.2: Profile insights wired into graph.py**
```bash
grep -n "profile_enricher\|format_profile_insights\|get_profile_insights" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/graph.py | tee /tmp/qa-smr/VF-04-2-wired.txt
# GATE: Import and call present in _get_cached_user_profile
```

**VF-04.3: Known sectors list**
```bash
grep -A 5 "_KNOWN_SECTORS" /home/zaks/zakops-agent-api/apps/agent-api/app/services/profile_enricher.py | tee /tmp/qa-smr/VF-04-3-sectors.txt
# GATE: At least 10 sectors defined
```

### VF-05: Dashboard & UI (AC-1, AC-8, AC-22, AC-28, AC-32)

**VF-05.1: Analytics page exists and renders**
```bash
ls -la /home/zaks/zakops-agent-api/apps/dashboard/src/app/analytics/page.tsx | tee /tmp/qa-smr/VF-05-1-analytics-page.txt
# GATE: File exists
```

**VF-05.2: Analytics nav item in config**
```bash
grep "analytics" /home/zaks/zakops-agent-api/apps/dashboard/src/config/nav-config.ts | tee /tmp/qa-smr/VF-05-2-nav.txt
# GATE: Analytics entry with url: '/analytics'
```

**VF-05.3: Analytics icon registered**
```bash
grep "analytics" /home/zaks/zakops-agent-api/apps/dashboard/src/components/icons.tsx | tee /tmp/qa-smr/VF-05-3-icon.txt
# GATE: analytics: IconChartBar
```

**VF-05.4: Promise.allSettled in analytics page**
```bash
grep "Promise.allSettled" /home/zaks/zakops-agent-api/apps/dashboard/src/app/analytics/page.tsx | tee /tmp/qa-smr/VF-05-4-allsettled.txt
# GATE: Used (not Promise.all)
```

**VF-05.5: No Promise.all in analytics page**
```bash
grep "Promise\.all[^S]" /home/zaks/zakops-agent-api/apps/dashboard/src/app/analytics/page.tsx | tee /tmp/qa-smr/VF-05-5-no-all.txt
# GATE: No matches (empty output)
```

**VF-05.6: Playwright E2E tests pass**
```bash
cd /home/zaks/zakops-agent-api/apps/dashboard && npx playwright test analytics-observability settings-provider-models chat-profile-integration deal-materials-upload --reporter=line 2>&1 | tee /tmp/qa-smr/VF-05-6-e2e.txt
# GATE: All 17 tests pass, 0 failures
```

### VF-06: Observability & Metrics (AC-16, AC-17, AC-28)

**VF-06.1: Prometheus agent_tool_calls_total counter**
```bash
grep "agent_tool_calls_total" /home/zaks/zakops-agent-api/apps/agent-api/app/core/metrics.py | tee /tmp/qa-smr/VF-06-1-prometheus.txt
# GATE: Counter defined with tool_name and success labels
```

**VF-06.2: No duplicate Prometheus registration**
```bash
grep -c "agent_background_tasks_total" /home/zaks/zakops-agent-api/apps/agent-api/app/core/metrics.py | tee /tmp/qa-smr/VF-06-2-no-dup.txt
# GATE: 0 (removed from metrics.py, lives in task_monitor.py)
```

**VF-06.3: Machine-verified tool count in prompt**
```bash
grep "tool_count" /home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/__init__.py | tee /tmp/qa-smr/VF-06-3-machine-count.txt
# GATE: {tool_count} placeholder injected from len(_registered_tools)
```

### VF-07: RAG Client & Document Pipeline (AC-20, AC-23)

**VF-07.1: RAG client exists**
```bash
ls -la /home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_client.py | tee /tmp/qa-smr/VF-07-1-rag-client.txt
grep "query_deal_documents" /home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_client.py | tee -a /tmp/qa-smr/VF-07-1-rag-client.txt
# GATE: File exists, query_deal_documents method present
```

**VF-07.2: Synthetic URL scheme**
```bash
grep "dataroom://" /home/zaks/zakops-agent-api/apps/agent-api/app/services/rag_client.py | tee /tmp/qa-smr/VF-07-2-synthetic-url.txt
# GATE: dataroom:// scheme used for deal-scoped filtering
```

**VF-07.3: BackendClient artifact methods**
```bash
grep -n "def list_deal_artifacts\|def get_artifact_text\|def get_deal_email_threads\|def search_entities" /home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py | tee /tmp/qa-smr/VF-07-3-client-methods.txt
# GATE: 4 methods present
```

---

## Cross-Consistency (XC-1..4)

### XC-1: Tool count parity
```bash
# Compare: __init__.py tool list count == SCOPE_TOOL_MAP unique tools == system.md numbered tools == startup log tool_count
echo "=== __init__.py ===" | tee /tmp/qa-smr/XC-1-parity.txt
grep -c "^    [a-z_]*,$\|^    [a-z_]*$" /home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/__init__.py | tee -a /tmp/qa-smr/XC-1-parity.txt
echo "=== system.md ===" | tee -a /tmp/qa-smr/XC-1-parity.txt
grep -cP '^\d+\. \*\*' /home/zaks/zakops-agent-api/apps/agent-api/app/core/prompts/system.md | tee -a /tmp/qa-smr/XC-1-parity.txt
echo "=== startup log ===" | tee -a /tmp/qa-smr/XC-1-parity.txt
COMPOSE_PROJECT_NAME=zakops docker compose logs agent-api 2>&1 | grep "tool_count" | tail -1 | tee -a /tmp/qa-smr/XC-1-parity.txt
# GATE: All counts = 22
```

### XC-2: Completion report AC count matches plan
```bash
grep -c "^| AC-" /home/zaks/bookkeeping/docs/SYSTEM-MATURITY-REMEDIATION-001-COMPLETION.md | tee /tmp/qa-smr/XC-2-ac-count.txt
# GATE: 35 ACs
```

### XC-3: All completion report ACs marked PASS
```bash
grep "| AC-" /home/zaks/bookkeeping/docs/SYSTEM-MATURITY-REMEDIATION-001-COMPLETION.md | grep -v "PASS" | tee /tmp/qa-smr/XC-3-all-pass.txt
# GATE: Empty output (all PASS)
```

### XC-4: CHANGES.md references mission
```bash
grep "SYSTEM-MATURITY-REMEDIATION-001" /home/zaks/bookkeeping/CHANGES.md | tee /tmp/qa-smr/XC-4-changes.txt
# GATE: At least 1 reference
```

---

## Stress Tests (ST-1..3)

### ST-1: Conviction endpoint with non-existent deal
```bash
curl -sf http://localhost:8095/api/v1/agent/conviction/NONEXISTENT-DEAL | python3 -m json.tool | tee /tmp/qa-smr/ST-1-conviction-missing.txt
# GATE: Returns valid JSON with score=50 (baseline) and empty components, NOT a 500 error
```

### ST-2: Knowledge endpoint with non-existent thread
```bash
curl -sf http://localhost:8095/api/v1/agent/knowledge/nonexistent-thread | python3 -m json.tool | tee /tmp/qa-smr/ST-2-knowledge-missing.txt
# GATE: Returns valid JSON with null/empty fields, NOT a 500 error
```

### ST-3: Thread archive with empty deal_id
```bash
curl -sf -X POST http://localhost:8095/api/v1/agent/threads/archive -H "Content-Type: application/json" -d '{"deal_id":""}' 2>&1 | tee /tmp/qa-smr/ST-3-archive-empty.txt
# GATE: Returns valid response or 400 error, NOT a 500
```

---

## Remediation Protocol

1. **Classify** — BLOCKER (prevents AC verification), DEFECT (AC claim incorrect), INFO (observation only)
2. **Fix** — For BLOCKER/DEFECT: create remediation task, fix, re-verify, record
3. **Re-verify** — Re-run the specific gate that failed
4. **Record** — Add to remediation log in scorecard

---

## Enhancement Opportunities

Document any ENH-N findings for future missions (not actionable in this QA).

---

## Scorecard Template

```
QA-SMR-VERIFY-001 SCORECARD
============================
Date: 2026-02-20
Verifier: Claude Opus 4.6

PRE-FLIGHT
  PF-1: [ ] validate-local PASS
  PF-2: [ ] tsc --noEmit PASS
  PF-3: [ ] Agent API healthy
  PF-4: [ ] Boot diagnostics ALL CLEAR

VERIFICATION FAMILIES
  VF-01.1: [ ] Tool count = 22
  VF-01.2: [ ] HITL tools = 8
  VF-01.3: [ ] SCOPE_TOOL_MAP complete
  VF-01.4: [ ] system.md tool list = 22
  VF-01.5: [ ] 5 document tools present
  VF-01.6: [ ] interview_user present
  VF-02.1: [ ] Stats endpoint
  VF-02.2: [ ] Decisions endpoint
  VF-02.3: [ ] Alerts endpoint
  VF-02.4: [ ] Conviction endpoint
  VF-02.5: [ ] Knowledge endpoint
  VF-02.6: [ ] Thread archive endpoint
  VF-02.7: [ ] Tasks health endpoint
  VF-03.1: [ ] Abstractive summarization
  VF-03.2: [ ] Retention policy
  VF-03.3: [ ] Summary pruning
  VF-03.4: [ ] Memory backfill utility
  VF-03.5: [ ] USE_LLM_SUMMARIZATION env
  VF-04.1: [ ] Profile enricher functions
  VF-04.2: [ ] Insights wired in graph.py
  VF-04.3: [ ] Known sectors list
  VF-05.1: [ ] Analytics page exists
  VF-05.2: [ ] Analytics nav item
  VF-05.3: [ ] Analytics icon
  VF-05.4: [ ] Promise.allSettled used
  VF-05.5: [ ] No Promise.all
  VF-05.6: [ ] E2E tests pass (17/17)
  VF-06.1: [ ] Prometheus counter
  VF-06.2: [ ] No duplicate registration
  VF-06.3: [ ] Machine-verified tool count
  VF-07.1: [ ] RAG client exists
  VF-07.2: [ ] Synthetic URL scheme
  VF-07.3: [ ] BackendClient methods

CROSS-CONSISTENCY
  XC-1: [ ] Tool count parity (4-way)
  XC-2: [ ] AC count = 35
  XC-3: [ ] All ACs PASS
  XC-4: [ ] CHANGES.md updated

STRESS TESTS
  ST-1: [ ] Conviction non-existent deal
  ST-2: [ ] Knowledge non-existent thread
  ST-3: [ ] Archive empty deal_id

TOTAL: ___/41 gates
REMEDIATIONS: ___
ENHANCEMENTS: ___
VERDICT: ___
```

---

## Guardrails

1. **Read-only verification** — Do NOT modify source code. Only create evidence files in `/tmp/qa-smr/`.
2. **Evidence for every gate** — Use `tee` to capture output.
3. **No false positives** — If a gate passes with caveats, note them.
4. **Surface 2 pre-existing** — `sync-backend-models` failure is pre-existing (datamodel-codegen missing). Do not count as SMR-001 failure.

## Stop Condition

DONE when all 41 gates are evaluated, scorecard is filled, remediations (if any) are completed, and enhancement opportunities are documented. Write scorecard to `/home/zaks/bookkeeping/qa-verifications/QA-SMR-VERIFY-001/QA-SMR-VERIFY-001-SCORECARD.md`.

---

## Execution Steps

1. `mkdir -p /tmp/qa-smr` — Create evidence directory
2. Run all PF gates (4)
3. Run all VF gates (33)
4. Run all XC gates (4)
5. Run all ST gates (3)
6. Fill scorecard, classify any failures
7. Remediate BLOCKERs/DEFECTs if found
8. Write final scorecard + completion summary

---

*End of QA Mission — QA-SMR-VERIFY-001*
