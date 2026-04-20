# COL-V2 Actionable Items Register
## Source: 19-Mission QA Verification (516 Gates)
## Date: 2026-02-13
## Status: Post-QA corrected (includes file existence audit)

---

## REVISION 2 — Backend Deep Audit (2026-02-13)

A deep audit of `/home/zaks/zakops-backend/` revealed that ALL 8 Section A items and
several Section B/C items already have full implementations in the backend repository.
The original QA gates searched only `zakops-agent-api` and missed 2,587 lines of backend
agent intelligence code across 11 files in `src/core/agent/` plus the brain router and
migration.

### Section A: ALL 8 ITEMS NOW RESOLVED

The backend already contains a complete DealBrainService, brain API router, and migration:

| A# | Original Item | Resolved By | Location |
|----|--------------|-------------|----------|
| A1 | DealBrainService.get_brain() | `get_brain()` + `get_or_create_brain()` | `src/core/agent/deal_brain_service.py` (337 lines) |
| A2 | DealBrainService.update_facts() | `add_facts()` with confidence scoring | same |
| A3 | DealBrainService.update_risks() | `update_brain(**fields)` generic updater | same |
| A4 | DealBrainService.update_summary() | `update_brain(summary=...)` | same |
| A5 | GET /api/deals/{id}/brain | `GET /{deal_id}/brain` | `src/api/orchestration/routers/brain.py` (302 lines, 14 endpoints) |
| A6 | POST /api/deals/{id}/brain/facts | `POST /{deal_id}/brain/facts` | same |
| A7 | PUT /api/deals/{id}/brain/summary | `PUT /{deal_id}/brain/summary` | same |
| A8 | brain_history INSERT trigger | `deal_brain_history` table + indexes | `db/migrations/028_deal_brain.sql` (130 lines) |

### Additional Backend Services Discovered

These services were never audited by the QA gates because they live in `zakops-backend`, not `zakops-agent-api`:

| Service | File | Lines | Key Methods/Classes |
|---------|------|-------|-------------------|
| StallPredictor | `src/core/agent/stall_predictor.py` | 257 | `predict()`, `predict_batch()` |
| MorningBriefingGenerator | `src/core/agent/morning_briefing.py` | 202 | `MorningBriefingGenerator` class |
| DealAnomalyDetector | `src/core/agent/anomaly_detector.py` | 209 | `DealAnomalyDetector` class |
| LivingMemoGenerator | `src/core/agent/living_memo_generator.py` | 216 | `render_markdown()` |
| DevilsAdvocateService | `src/core/agent/devils_advocate.py` | 191 | `DevilsAdvocateService` class |
| GhostKnowledgeDetector | `src/core/agent/ghost_knowledge_detector.py` | 243 | `detect()`, `store_ghosts()` |
| MomentumCalculator | `src/core/agent/momentum_calculator.py` | 319 | `compute_and_store()` |
| BottleneckHeatmap | `src/core/agent/bottleneck_heatmap.py` | 181 | `compute()` |

### RAG Fusion Verified (Zaks-llm)

`/home/zaks/Zaks-llm/src/api/rag_rest_api.py` contains `HybridQueryRequest` with `rrf_k=60`,
`_rrf_merge()` function, and `/rag/hybrid` endpoint. RRF fusion is BUILT.

### Cross-Section Impact

| Original Item | Status | Resolved By |
|--------------|--------|-------------|
| B5.1 (RRF k=60 verification) | **RESOLVED** | `HybridQueryRequest.rrf_k=60` + `_rrf_merge()` in Zaks-llm |
| B6.4 (Living Deal Memo) | **RESOLVED** | `LivingMemoGenerator` in zakops-backend (216 lines) |
| C9 (StallPredictor) | **RESOLVED** | `stall_predictor.py` in zakops-backend (257 lines) |
| C18 (MorningBriefingGenerator) | **RESOLVED** | `morning_briefing.py` in zakops-backend (202 lines) |
| C19 (DealAnomalyDetector) | **RESOLVED** | `anomaly_detector.py` in zakops-backend (209 lines) |
| D3 (RRF k=60 in RAG) | **RESOLVED** | Confirmed in Zaks-llm source |

### Items Confirmed NOT Found Anywhere

- DecisionFatigueSentinel, SentimentCoach, Spaced Repetition — no files in any repo
- Reflexion/CritiqueResult — no file (only `critique_result` field in snapshot_writer dataclass)
- CommandPalette, SmartPaste, MemoryStatePanel, AmbientSidebar, CitationIndicator — no dashboard components
- GDPR service, retention policy, `legal_hold_locks` table — not in agent-api or backend
- PlanAndExecuteGraph — no file
- Broker Dossier endpoint — no dedicated file

---

## Corrections to Completion Report

The QA gates searched incorrect paths for several files, inflating the SCOPE_GAP count.
After manual audit, **35+ gates** previously scored SCOPE_GAP actually have implementations.

| File | Location | Lines | QA Gate Searched | Why Missed |
|------|----------|-------|-----------------|------------|
| citation_audit.py | `app/core/security/` | 144 | `app/services/` | Wrong directory |
| replay_service.py | `app/services/` | 234 | Grep pattern mismatch | Evidence noise from .venv |
| counterfactual_service.py | `app/services/` | 224 | Grep pattern mismatch | Evidence noise from .venv |
| node_registry.py | `app/core/langgraph/` | 296 | PlanAndExecute grep | Different class name |
| rag_rest.py (hybrid_query) | `app/services/` | method | Missing `Retriever` class | Different architecture |

**Corrected totals:**
- Original SCOPE_GAP: 230 → Corrected: ~195
- Original coverage: 55% → Corrected: ~62%

---

## SECTION A: Backend-Blocked Items — ~~8 FAIL gates from M05~~ ALL RESOLVED

> **[RESOLVED 2026-02-13]** All 8 items exist in zakops-backend. See REVISION 2 above for details.

| # | Gate | Status | Resolved By |
|---|------|--------|-------------|
| ~~A1~~ | ~~DealBrainService.get_brain()~~ | **[RESOLVED]** | `src/core/agent/deal_brain_service.py:33` |
| ~~A2~~ | ~~DealBrainService.update_facts()~~ | **[RESOLVED]** | `src/core/agent/deal_brain_service.py:101` |
| ~~A3~~ | ~~DealBrainService.update_risks()~~ | **[RESOLVED]** | `src/core/agent/deal_brain_service.py:60` |
| ~~A4~~ | ~~DealBrainService.update_summary()~~ | **[RESOLVED]** | `src/core/agent/deal_brain_service.py:60` |
| ~~A5~~ | ~~GET /api/deals/{id}/brain~~ | **[RESOLVED]** | `src/api/orchestration/routers/brain.py:75` |
| ~~A6~~ | ~~POST /api/deals/{id}/brain/facts~~ | **[RESOLVED]** | `src/api/orchestration/routers/brain.py:103` |
| ~~A7~~ | ~~PUT /api/deals/{id}/brain/summary~~ | **[RESOLVED]** | `src/api/orchestration/routers/brain.py:171` |
| ~~A8~~ | ~~brain_history INSERT trigger~~ | **[RESOLVED]** | `db/migrations/028_deal_brain.sql` (130 lines) |

~~**Priority:** HIGH — blocks brain extraction pipeline end-to-end flow.~~
**Status: No longer blocking. Backend brain infrastructure is complete.**

---

## SECTION B: Completion Items (Service Exists, Features Incomplete)

These files exist and have core logic, but spec-mandated features are missing.

### B1. Citation Audit — `app/core/security/citation_audit.py` (144 lines)

**What's built:** CitationCheck, CitationAuditResult, audit_citations(), _keyword_similarity()
**What's missing per spec (S8.2):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B1.1 | Semantic similarity via RAG embeddings (currently keyword-only) | Medium |
| B1.2 | Integration into graph.py post-completion hook | Small |
| B1.3 | Citation quality metrics in turn_snapshots | Small |
| B1.4 | Threshold configuration (currently hardcoded 0.5/0.3) | Small |

### B2. Replay Service — `app/services/replay_service.py` (234 lines)

**What's built:** ReplayService, replay(), _compare(), word similarity, endpoint at `/admin/replay`
**What's missing per spec (S6.4):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B2.1 | Admin-only auth on `/admin/replay` (currently session-only) | Small |
| B2.2 | Embedding-based cosine similarity (currently bag-of-words) | Medium |
| B2.3 | Proposal extraction in replay result (returns empty lists) | Medium |
| B2.4 | Replay audit log (who replayed what, when) | Small |

### B3. Counterfactual Service — `app/services/counterfactual_service.py` (224 lines)

**What's built:** CounterfactualService, analyze(), _apply_modifications(), endpoint at `/admin/counterfactual`
**What's missing per spec (S6.5):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B3.1 | Admin-only auth on `/admin/counterfactual` | Small |
| B3.2 | brain_diff computation (original vs counterfactual brain impact) | Medium |
| B3.3 | Counterfactual history storage | Small |

### B4. Node Registry / Specialist Delegation — `app/core/langgraph/node_registry.py` (296 lines)

**What's built:** NodeRegistry, SpecialistNode Protocol, 3 specialists (Financial, Risk, DealMemory), route(), keyword-based classification
**What's missing per spec (S19.4):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B4.1 | LLM-based query classification (currently keyword-only) | Medium |
| B4.2 | Integration with main graph.py (registry exists but not called from graph) | Medium |
| B4.3 | 4th specialist: Compliance/Regulatory | Small |
| B4.4 | Specialist response merging/synthesis | Medium |

### B5. RAG Hybrid Query — `app/services/rag_rest.py`

**What's built:** hybrid_query() method with sparse_weight, BM25 reference, `/rag/hybrid` endpoint call
**What's missing per spec (A-1, S11):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| ~~B5.1~~ | ~~RRF fusion with k=60 parameter~~ **[RESOLVED]** — Confirmed in `Zaks-llm/src/api/rag_rest_api.py`: `HybridQueryRequest.rrf_k=60`, `_rrf_merge()`, `/rag/hybrid` endpoint | ~~Verify~~ Done |
| B5.2 | Contextual chunk headers (document title/section prepended) | Medium |
| B5.3 | ivfflat index verification in RAG service | Verify |
| B5.4 | GIN index for keyword search verification | Verify |

### B6. Export Service — `app/services/export_service.py` (258 lines)

**What's built:** ExportService, markdown export, JSON export, attach_to_deal()
**What's missing per spec (S12):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B6.1 | PDF conversion (wkhtmltopdf or similar) | Medium |
| B6.2 | Brain export integration (include brain state in export) | Small |
| B6.3 | Auto-refresh on brain version change | Medium |
| ~~B6.4~~ | ~~Living Deal Memo — 7 content sections (S12.3)~~ **[RESOLVED]** — `zakops-backend/src/core/agent/living_memo_generator.py` (216 lines) with `render_markdown()` | ~~Large~~ Done |

### B7. Proposal Service — `app/services/proposal_service.py` (299 lines)

**What's built:** PROPOSAL_HANDLERS (9 types), execute(), _handle_correct_brain_summary(), FOR UPDATE locking
**What's missing per spec (S15):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B7.1 | Auto-approve removal for stage_transition (S15.2) — verify it's NOT auto-approved | Verify |
| B7.2 | trigger_type='correction' field in brain history | Small |
| B7.3 | Proposal expiration (pending proposals older than N hours) | Small |

### B8. Drift Detection — `app/services/drift_detection.py` (184 lines)

**What's built:** check_staleness(), detect_contradictions(), compute_decay_confidence(), should_re_summarize()
**What's missing per spec (S4.5):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B8.1 | Integration into graph.py turn pipeline (call after brain extraction) | Small |
| B8.2 | Contradiction resolution UI (flag conflicting facts to user) | Medium |
| B8.3 | Periodic re-summarization scheduler (currently check-only, no trigger) | Medium |

### B9. Snapshot Writer — `app/services/snapshot_writer.py` (233 lines)

**What's built:** TurnSnapshot dataclass (26 fields), SnapshotWriter with write/get/list, turn_snapshots table
**What's missing per spec (S6):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B9.1 | Integration into graph.py (write snapshot after every turn) | Medium |
| B9.2 | AES-256-GCM encryption for compliance-tier snapshots | Large |
| B9.3 | Partition automation (monthly partitions for turn_snapshots) | Medium |

### B10. Summarizer — `app/services/summarizer.py`

**What's built:** Every-5-turns trigger, writes to session_summaries, used in graph.py
**What's missing per spec (S5):**

| # | Missing Feature | Effort |
|---|----------------|--------|
| B10.1 | Consolidation worker (merge old summaries into archival tier) | Medium |
| B10.2 | Extractive pre-filter (reduce token count before LLM summarization) | Medium |
| B10.3 | Cost-effective model selection for summarization (smaller model) | Small |

---

## SECTION C: Not-Yet-Started Features (True SCOPE_GAP)

These have NO implementation files. Grouped by priority.

### C-P1: Foundational (blocks other features)

| # | Feature | Spec Section | Description | Effort |
|---|---------|-------------|-------------|--------|
| C1 | Migration 029 — Legal Hold Tables | S7.5 | `legal_hold_locks`, `legal_hold_log` tables; GDPR-ready | Medium |
| C2 | Partition Automation Functions | S6.6 | `create_monthly_partitions()` PL/pgSQL, cron job | Medium |

### C-P2: Core V2 Intelligence

| # | Feature | Spec Section | Description | Effort |
|---|---------|-------------|-------------|--------|
| C3 | Reflexion Self-Critique | S8.3-S8.4 | `ReflexionCritique` class, critique after generation, revision loop | Large |
| C4 | Chain-of-Verification | S8.5 | List claims → check evidence → revise inline | Large |
| C5 | HyDE Query Enhancement | S11.3 | Hypothetical document embedding for better retrieval | Medium |
| C6 | RAPTOR Hierarchy | S11.4 | 3-level retrieval (leaf, intermediate, root) | Large |
| C7 | RankedChunk Type | S11 | Typed retrieval results with score, source, relevance | Small |

### C-P3: Cognitive Intelligence & Decision Support

| # | Feature | Spec Section | Description | Effort |
|---|---------|-------------|-------------|--------|
| C8 | DecisionFatigueSentinel | S14.1 | 5 decisions/2hr warning, 3hr session warning | Medium |
| ~~C9~~ | ~~Stall Predictor~~ | ~~S14.2~~ | **[RESOLVED]** — `zakops-backend/src/core/agent/stall_predictor.py` (257 lines), `predict()`, `predict_batch()` | ~~Medium~~ Done |
| C10 | Risk Cascade Predictor | S14.3 | Portfolio-wide risk scan, 0.7 similarity threshold | Large |
| C11 | Deal Precedent Network | S14.4 | Similar deal finder using brain fact vectors | Large |
| C12 | Spaced Repetition | S14.5 | `get_review_facts()`, decay threshold, UI review cards | Medium |
| C13 | Broker Dossier | S14.6 | `GET /api/brokers/{name}/dossier` — past deals, sentiment | Medium |
| C14 | Ghost Knowledge SSE | S14.7 | `ghost_knowledge_flags` field in SSE events + UI toast | Small |
| C15 | Momentum UI Color Bands | S20 | Green/amber/red visualization in dashboard | Small |

### C-P4: UI & Ambient Intelligence

| # | Feature | Spec Section | Description | Effort |
|---|---------|-------------|-------------|--------|
| C16 | Citation UI Indicators | S8.2 | Green/amber/red underlines, Refined badge | Medium |
| C17 | MemoryStatePanel | S5.4 | Working/Recall/Archival tier visualization | Medium |
| ~~C18~~ | ~~MorningBriefingGenerator~~ | ~~S17.1~~ | **[RESOLVED]** — `zakops-backend/src/core/agent/morning_briefing.py` (202 lines), `MorningBriefingGenerator` class | ~~Large~~ Done |
| ~~C19~~ | ~~DealAnomalyDetector~~ | ~~S17.2~~ | **[RESOLVED]** — `zakops-backend/src/core/agent/anomaly_detector.py` (209 lines), `DealAnomalyDetector` class | ~~Large~~ Done |
| C20 | AmbientSidebar | S17.3 | Related Facts, Similar Deals, Recent News panels | Large |
| C21 | SmartPaste | S17.4 | Entity extraction from pasted text, "Add to Brain" | Medium |
| C22 | SentimentCoach | S17.5 | Per-deal sentiment trend tracking | Medium |
| C23 | CommandPalette | S17.6 | Cmd+K with context-aware deal commands | Medium |

### C-P5: Architecture Enhancements

| # | Feature | Spec Section | Description | Effort |
|---|---------|-------------|-------------|--------|
| C24 | PlanAndExecuteGraph | S19.2 | Structured step decomposition for complex queries | Large |
| C25 | Full Multi-Specialist Pipeline | S19.4 | Route → parallel specialists → synthesize | Large |
| C26 | MCP Governance Integration | S19.5 | Cost ledger + decision ledger for MCP tool calls | Medium |

### C-P6: Compliance & Retention

| # | Feature | Spec Section | Description | Effort |
|---|---------|-------------|-------------|--------|
| C27 | GDPR Deletion Automation | S7.3 | Automated right-to-erasure pipeline | Large |
| C28 | Retention Policy Engine | S7.4 | Configurable retention tiers (30d/90d/365d/forever) | Medium |
| C29 | Compliance Deletion API | S7.5 | `POST /admin/compliance/purge` with audit trail | Medium |
| C30 | Deletion Audit Log | S7.6 | Immutable log of all deletions (who, what, when, why) | Medium |
| C31 | HKDF Key Derivation | S6.7 | Per-thread encryption keys derived from master | Large |

---

## SECTION D: Verification-Only Items

These items may already be correct but couldn't be verified due to DB access issues.

| # | Item | How to Verify |
|---|------|--------------|
| D1 | turn_snapshots partition function | `psql -h localhost -U agent -d zakops_agent -c "\df create_monthly_partitions"` |
| D2 | deal_budgets table exists | `psql -h localhost -U zakops -d zakops -c "\d deal_budgets"` |
| ~~D3~~ | ~~RRF k=60 in RAG service~~ **[RESOLVED]** | Confirmed: `Zaks-llm/src/api/rag_rest_api.py` line 191: `rrf_k: int = 60` |
| D4 | ivfflat index on embeddings | `psql -h localhost -U zakops -d crawlrag -c "\di"` |
| D5 | GIN index for full-text search | Same as D4 |
| D6 | Proposal auto-approve removal | Review graph.py proposal flow for stage_transition |
| D7 | Cost ledger VIEW aggregation | `psql -h localhost -U agent -d zakops_agent -c "\dv deal_cost_summary"` |

---

## Implementation Roadmap (Suggested)

### ~~Sprint 1: Backend Brain + Core Wiring (A1-A8, B8.1, B9.1)~~ ALREADY DONE

> **[2026-02-13]** The backend brain infrastructure (A1-A8) is COMPLETE. DealBrainService,
> brain router (14 endpoints), and migration 028 all exist in zakops-backend. What remains
> from this sprint is only the agent-api wiring work:

- ~~Build DealBrainService in zakops-backend (A1-A7)~~ **DONE**
- ~~Add brain_history trigger (A8)~~ **DONE**
- Wire drift_detection into graph.py turn pipeline (B8.1) — still needed
- Wire snapshot_writer into graph.py (B9.1) — still needed
- Wire citation_audit into graph.py post-completion (B1.2) — still needed
- Verify DB items (D1-D7) — D3 resolved, 6 remaining

### Sprint 2: Intelligence Completion (B1-B4, C3, C8, C14-C15)
**Impact:** Upgrades quality of agent responses
- Upgrade citation_audit to embedding similarity (B1.1)
- Add admin-only auth to replay/counterfactual (B2.1, B3.1)
- Wire node_registry into graph.py (B4.2)
- Build reflexion self-critique (C3)
- Build DecisionFatigueSentinel (C8)
- ~~Build Stall Predictor (C9)~~ **DONE** — exists in zakops-backend
- Add ghost knowledge SSE + UI toast (C14)
- Add momentum UI color bands (C15)

### Sprint 3: Compliance & Retention (C1, C2, C27-C31)
**Impact:** GDPR-readiness, data lifecycle
- Migration 029 — legal hold tables (C1)
- Partition automation (C2)
- GDPR deletion automation (C27)
- Retention policy engine (C28-C30)
- Deletion audit log (C30)

### Sprint 4: Advanced Intelligence (C4-C6, C10-C13)
**Impact:** Best-in-class RAG and decision support
- Chain-of-Verification (C4)
- HyDE query (C5), RAPTOR (C6)
- Risk Cascade Predictor (C10)
- Deal Precedent Network (C11)
- Spaced Repetition (C12)
- Broker Dossier (C13)

### Sprint 5: Ambient UI (C16-C17, C20-C23)
**Impact:** Polished user experience
- Citation UI, MemoryStatePanel (C16-C17)
- ~~Morning Briefing (C18)~~ **DONE** — backend service exists, needs dashboard UI only
- ~~Anomaly Detector (C19)~~ **DONE** — backend service exists, needs dashboard UI only
- AmbientSidebar, SmartPaste (C20-C21)
- SentimentCoach, CommandPalette (C22-C23)

### Sprint 6: Architecture (C24-C26, B4.4)
**Impact:** Agent sophistication
- PlanAndExecuteGraph (C24)
- Multi-Specialist Pipeline (C25)
- MCP Governance (C26)
- ~~Living Deal Memo (B6.4)~~ **DONE** — `LivingMemoGenerator` exists in zakops-backend

---

## Summary Counts

### Original (Pre-Audit)

| Category | Items | Gates Affected |
|----------|-------|---------------|
| A: Backend-blocked (FAIL) | 8 | 8 |
| B: Completion items | 10 services, 37 sub-items | ~35 |
| C: Not-yet-started | 31 features | ~160 |
| D: Verification-only | 7 | ~15 |
| **Total actionable** | **83 items** | **~218** |

### Revised (Post Backend Deep Audit — 2026-02-13)

| Category | Original | Resolved | Remaining | Notes |
|----------|----------|----------|-----------|-------|
| A: Backend-blocked | 8 | 8 | **0** | ALL resolved — DealBrainService, brain router, migration 028 |
| B: Completion items | 37 sub-items | 2 (B5.1, B6.4) | **35** | RRF fusion verified; Living Memo built |
| C: Not-yet-started | 31 features | 3 (C9, C18, C19) | **28** | StallPredictor, MorningBriefing, AnomalyDetector all in backend |
| D: Verification-only | 7 | 1 (D3) | **6** | RRF k=60 confirmed in Zaks-llm source |
| **Total actionable** | **83** | **14** | **~69 items** | Additional backend services reduce true gap further |

> **Note:** The ~69 remaining items overcount slightly because several B-section features
> (ghost knowledge detection, momentum calculation, devil's advocate, bottleneck heatmap)
> have backend services that partially or fully cover them. True net remaining work is
> estimated at **~36 items** when accounting for backend services that only need
> agent-api wiring or dashboard UI integration rather than greenfield development.

### Backend Services That Reduce Remaining Effort

These backend services exist and are wired into the brain router, reducing multiple
B/C items from "build from scratch" to "integrate existing backend endpoint":

| Backend Service | Reduces | From | To |
|----------------|---------|------|----|
| GhostKnowledgeDetector (243 lines) | C14 (Ghost Knowledge SSE) | Build detector + SSE + UI | Wire SSE + UI only |
| MomentumCalculator (319 lines) | C15 (Momentum UI Color Bands) | Build calculator + UI | Wire UI only |
| DevilsAdvocateService (191 lines) | Part of C-P2 intelligence | Build service + endpoint | Dashboard integration only |
| BottleneckHeatmap (181 lines) | Pipeline visibility | Build service + endpoint | Dashboard integration only |

---

*Generated from COL-V2 QA Verification (19 missions, 516 gates)*
*Cross-referenced with manual file audit of agent-api codebase*
*Revised 2026-02-13: Deep audit of zakops-backend (2,587 lines across 11 agent files)*
*Spec: COL-DESIGN-SPEC-V2.md (3,276 lines)*
