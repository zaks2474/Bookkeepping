# DASHBOARD-DEFECT-CLOSURE-001 — Execution Quick-Start

**Plan source:** `/home/zaks/bookkeeping/docs/DASHBOARD-DEFECT-CLOSURE-001-INVESTIGATION.md`
**Standard:** `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` (v2.3)
**Quick ref:** `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md`

---

## Builder Pre-Work: Standardize the Plan

Before executing any phase, the builder MUST convert the raw plan into a v2.3-compliant mission prompt.

### Step 1: Read these files (in order)
| # | File | Why |
|---|------|-----|
| 1 | `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | Authoritative structure (sections, gates, IAs) |
| 2 | `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Skeleton template |
| 3 | `/home/zaks/bookkeeping/docs/DASHBOARD-DEFECT-CLOSURE-001-INVESTIGATION.md` | Raw plan with contracts, evidence, phase tasks |
| 4 | `/home/zaks/bookkeeping/docs/DASHBOARD-ROUTE-REMEDIATION-COMPLETION-REPORT.md` | Prior mission output (predecessor context) |
| 5 | `/home/zaks/bookkeeping/docs/SYSTEM-HEALTH-AUDIT-2026-02-15.md` | Source audit that triggered this work |

### Step 2: Generate the mission prompt
Write to: `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-DEFECT-CLOSURE-001.md`

Add these missing sections (the raw plan already has phases + gates + contracts):

| Section | What to pull from | Notes |
|---------|-------------------|-------|
| Header (7 fields) | ID=`DASHBOARD-DEFECT-CLOSURE-001`, Classification=`Defect Closure + Feature Build`, Prerequisite=`DASHBOARD-ROUTE-REMEDIATION` (complete), Successor=`None` | |
| Mission Objective | Investigation Report Section 1 (A1-A6 findings) | What: 3 backend endpoints + pipeline fix + sentiment fix + Zod + S17 enforcement. What NOT: no new UI components, no backend schema migrations |
| Context | Completion report §1 (root cause), §9 (scope exclusions that are now IN scope) | |
| Architectural Constraints | CLAUDE.md non-negotiable rules + DEAL-INTEGRITY patterns from MEMORY.md | Promise.allSettled, middleware proxy, PIPELINE_STAGES, contract surface discipline |
| Anti-Patterns | Promise.all vs allSettled, console.error vs warn, client-side counting | From standard §3b examples |
| Pre-Mortem | 3-5 risks from plan's "RISKS DISCOVERED" table | R1-R5 map directly |
| Phase complexity + blast radius | Size each phase (see sizing guide in standard §4) | P0=S, P1=M, P2=L, P3=M, P4=M, P5=S, P6=M, P7=S |
| Checkpoints + decision trees | P1: IF migration 023 not applied → apply it, ELSE skip. P2C: IF no deal_brain → 404, ELSE 200 | |
| Per-phase rollback | Already in raw plan footer — move into each phase | |
| Acceptance Criteria | One AC per phase + AC-N-1 (no regression) + AC-N (bookkeeping) | ~10 ACs total |
| Guardrails | Scope fence, generated file protection, WSL safety, Surface 9, governance surfaces | |
| Self-Check Prompts | After P0: "Did I confirm all 3 endpoints 404?" After P2: "Did I test 404 for nonexistent deal?" Before done: "Does make validate-local pass NOW?" | |
| File Paths (3 tables) | Already in raw plan — reformat into modify/create/read-only | |
| Stop Condition | All ACs met + validate-local + validate-surface17 + tsc clean | |
| Crash Recovery (IA-2) | `git log --oneline -5 && make validate-local && ls /home/zaks/bookkeeping/mission-checkpoints/` | |
| Context Checkpoint (IA-1) | Midpoint = after Phase 3A (sync chain). Write checkpoint to `mission-checkpoints/DASHBOARD-DEFECT-CLOSURE-001.md` | |
| Governance surfaces (IA-15) | Affected: S1 (backend→dashboard), S2 (backend→agent), S17 (route coverage). Gates: `make validate-surface17`, `make sync-types`, `make update-spec` | |

### Step 3: Validate
```bash
/validate-mission /home/zaks/bookkeeping/docs/MISSION-DASHBOARD-DEFECT-CLOSURE-001.md
```

---

## Session Plan

### Session A: Backend (sequential, runs first)

```
Phase 0 → Phase 1 → Phase 2 → restart backend → curl verify all 3 endpoints
```

| Phase | Repo | Files |
|-------|------|-------|
| **P0** Verify Reality | Both | `psql` query + `curl` 3 endpoints + pipeline summary |
| **P1** Pipeline Fix | zakops-backend | `/home/zaks/zakops-backend/db/init/001_base_tables.sql` (EDIT view), `/home/zaks/zakops-backend/src/api/orchestration/main.py` (EDIT: HTTPException in get_pipeline_summary) |
| **P2** Deal Endpoints | zakops-backend | `/home/zaks/zakops-backend/src/api/orchestration/main.py` (EDIT: 3 new GET endpoints ~150 lines) |

**Exit gate:** `curl -sf localhost:8091/api/deals/{id}/case-file`, `/enrichment`, `/materials` all return 200 JSON. `curl -sf localhost:8091/api/pipeline/summary` returns array with `count` field.

**Blocking:** Sessions B and C cannot start until Session A's exit gate passes.

---

### Session B: Sync + Dashboard (sequential, after Session A)

```
Phase 3A (sync) → Phase 3B (Zod) → Phase 4 (agentFetch + sentiment)
```

| Phase | Repo | Files |
|-------|------|-------|
| **P3A** Sync Chain | monorepo | `make update-spec && make sync-types && make sync-backend-models && npx tsc --noEmit` |
| **P3B** Zod Enforcement | monorepo | `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (EDIT: add 4 Zod schemas + safeParse wrappers for enrichment, tasks, sentiment, case-file) |
| **P4** agentFetch + Sentiment | monorepo | `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/agent-fetch.ts` (NEW), `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/agent/sentiment/[dealId]/route.ts` (NEW), `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` (EDIT: fix sentiment path), `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/complete/route.ts` (EDIT), `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/threads/route.ts` (EDIT), `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/agent/activity/route.ts` (EDIT), + any other agent route handlers |

**Exit gate:** `npx tsc --noEmit` = 0 errors. No `${AGENT_API_URL}` in route handlers (only in `agent-fetch.ts`). `getSentimentTrend` path = `/api/agent/sentiment/${dealId}`.

**Context checkpoint:** After P3A, write progress to `/home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-DEFECT-CLOSURE-001.md`.

---

### Session C: Enforcement + Validation (after Session B)

```
Phase 5 → Phase 6 → Phase 7
```

| Phase | Repo | Files |
|-------|------|-------|
| **P5** Surface 17 | monorepo | `/home/zaks/zakops-agent-api/tools/infra/validate-surface17.sh` (EDIT: PROXY_PASS_EXCEPTIONS + manifest + WARN→FAIL) |
| **P6** Liveness + Smoke | monorepo | `/home/zaks/zakops-agent-api/tools/infra/validate-endpoint-liveness.sh` (EDIT: 4 new probes with jq shape checks), `/home/zaks/zakops-agent-api/tools/infra/smoke-test.sh` (EDIT: pipeline + deal detail assertions) |
| **P7** Final Verification | all | `make validate-local && npx tsc --noEmit && make validate-surface17 && make validate-contract-surfaces && bash tools/infra/validate-surface-count-consistency.sh && make validate-endpoint-liveness && make smoke-test` |

**Exit gate:** All Phase 7 automated gates pass. CHANGES.md updated.

---

## Dependency Diagram

```
SESSION A (backend-only)          SESSION B (dashboard)           SESSION C (infra + final)
========================          ====================           =========================
P0: Verify Reality
    │
    ▼
P1: Pipeline Fix
    │
    ▼
P2: 3 Backend Endpoints
    │
    ▼
[restart backend + curl verify]
    │
    ╰──── BLOCKS ────────────▶ P3A: Sync Chain
                                    │
                                    ▼
                               P3B: Zod Schemas
                                    │
                                    ▼
                               P4: agentFetch + Sentiment
                                    │
                                    ╰──── BLOCKS ────▶ P5: S17 Enforcement
                                                            │
                                                            ▼
                                                       P6: Liveness + Smoke
                                                            │
                                                            ▼
                                                       P7: Final Verification
                                                            │
                                                            ▼
                                                       CHANGES.md + Completion
```

**No parallel sessions possible** — each session's output is a hard dependency for the next. The chain is: backend endpoints must exist → sync must run → dashboard code must compile → validators must reference new routes → liveness must probe new endpoints.

---

## Files Master List

### To Modify
| File | Session | Phase |
|------|---------|-------|
| `/home/zaks/zakops-backend/db/init/001_base_tables.sql` | A | P1 |
| `/home/zaks/zakops-backend/src/api/orchestration/main.py` | A | P1+P2 |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts` | B | P3B+P4 |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/complete/route.ts` | B | P4 |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/chat/threads/route.ts` | B | P4 |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/agent/activity/route.ts` | B | P4 |
| `/home/zaks/zakops-agent-api/tools/infra/validate-surface17.sh` | C | P5 |
| `/home/zaks/zakops-agent-api/tools/infra/validate-endpoint-liveness.sh` | C | P6 |
| `/home/zaks/zakops-agent-api/tools/infra/smoke-test.sh` | C | P6 |

### To Create
| File | Session | Phase |
|------|---------|-------|
| `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/agent-fetch.ts` | B | P4 |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/agent/sentiment/[dealId]/route.ts` | B | P4 |
| `/home/zaks/bookkeeping/mission-checkpoints/DASHBOARD-DEFECT-CLOSURE-001.md` | B | P3A |
| `/home/zaks/bookkeeping/docs/MISSION-DASHBOARD-DEFECT-CLOSURE-001.md` | Pre-work | Step 2 |

### Read-Only (sources of truth — do NOT modify)
| File | Purpose |
|------|---------|
| `/home/zaks/zakops-backend/db/migrations/023_stage_check_constraint.sql` | Correct view definition to copy into init script |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/middleware.ts` | Proxy routing rules (verify, don't change) |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/deals/[id]/page.tsx` | UI consumption patterns for contracts |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/components/deal-workspace/SentimentCoachPanel.tsx` | Sentiment UI consumption |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/pipeline/route.ts` | Pipeline fallback logic (verify ok check) |
| `/home/zaks/zakops-agent-api/apps/dashboard/src/types/execution-contracts.ts` | PIPELINE_STAGES source of truth |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-STANDARD.md` | v2.3 standard for prompt generation |
| `/home/zaks/bookkeeping/docs/MISSION-PROMPT-QUICKSTART.md` | Template skeleton |

---

## TL;DR for the Builder

1. **Read** the 5 source files (Step 1 above)
2. **Generate** the standardized mission prompt following v2.3 skeleton (Step 2)
3. **Validate** with `/validate-mission`
4. **Execute Session A** (backend: P0→P1→P2, restart, curl verify)
5. **Execute Session B** (dashboard: P3A→P3B→P4, checkpoint, tsc verify)
6. **Execute Session C** (infra: P5→P6→P7, full gate sweep, CHANGES.md)
7. **Done** when all P7 gates pass
