# COL Design Innovation Master — Consolidated Report

## Run Context
- **Date**: 2026-02-12
- **Artifact Reviewed**: `/home/zaks/bookkeeping/docs/COL-DESIGN-SPEC-V1.md` (1,861 lines)
- **Sources**: Gemini (TriPass Pass 1), Claude Opus (3 parallel deep investigations)
- **Investigation Domains**: AI/Architecture patterns, Forensic analysis, UX/Cognitive science, Competitive intelligence
- **Total Raw Findings**: 48 improvement ideas + 28 gaps + 5 moonshots
- **After Deduplication**: 45 unique improvement ideas + 23 unique gaps + 5 moonshots

---

## TOP 10 HIGHEST-IMPACT IMPROVEMENTS

These are the improvements that would most dramatically differentiate ZakOps from every other M&A platform. Ranked by a composite of: uniqueness, impact, feasibility, and leverage (how many other features they enable).

### #1: Ghost Knowledge Detection
**What**: Detect when the user references deal facts in chat that are NOT in the Deal Brain — "ghost knowledge" that exists only in the user's head. Auto-extract, flag, and prompt for confirmation.
**Why transformative**: This is the *inverse* of hallucination detection. Instead of catching the AI inventing facts, it catches the human holding unrecorded facts. It closes the gap between team knowledge and system knowledge — the #1 problem in M&A due diligence.
**Extends**: Section 4.4 (Extraction Prompt), Section 4.5 (Drift Detection)
**Complexity**: LOW
**Source**: Claude-UX

### #2: Deal Momentum Score
**What**: A single 0-100 composite metric per deal combining: stage velocity, event frequency, open item completion, risk trajectory, and action completion rate. Color-coded on every deal card.
**Why transformative**: Turns the abstract "how is this deal going?" into a quantifiable, comparable number. Only possible because the COL spec creates the data infrastructure (Deal Brain + cost ledger + event stream + action system) to compute it.
**Extends**: Section 4 (Deal Brain), Section 13 (Observability)
**Complexity**: LOW
**Source**: Claude-UX

### #3: Cross-Deal Entity Resolution Graph
**What**: A knowledge graph connecting deals by shared entities (people, companies, terms, risks). Auto-discovers patterns like "same broker sent 3 deals with inflated EBITDA" or "two targets share a key customer."
**Why transformative**: Every M&A platform treats deals as silos. This creates institutional intelligence across the entire portfolio — a fundamentally new capability.
**Extends**: Section 4 (Deal Brain v2) — brain becomes a node in a larger graph
**Complexity**: HIGH
**Source**: Gemini (IDEA-1) + Claude-UX (#5) — merged

### #4: Reflexion Self-Critique Loop
**What**: After generating a response, a critique node evaluates: are cited facts present in evidence? Does the response address the question? Are there unsupported claims? Loops back for refinement (max 2 tries).
**Why transformative**: In M&A, a hallucinated financial figure can cause real financial harm. This adds a second defense layer that the COL spec's citation validation doesn't cover.
**Extends**: Section 8 (Citation Validation), Agent graph.py
**Complexity**: MEDIUM
**Source**: Claude-AI (#5)

### #5: Decision Journal with Outcome Tracking
**What**: Every HITL decision auto-captured with rationale (already exists via `transitionReason`), deal state, evidence context, and chat reference. Months later, correlates with actual outcome: "You moved Acme to LOI based on $12M ARR. Actual ARR was $9.2M."
**Why transformative**: No M&A tool closes the feedback loop between decision rationale and deal outcome. This creates institutional learning over time.
**Extends**: Section 4.2 (decisions JSONB), Section 6 (Deterministic Replay)
**Complexity**: MEDIUM
**Source**: Claude-UX (#3)

### #6: Hybrid Dense+Sparse Retrieval (BM25 Fusion)
**What**: Add BM25 keyword search alongside the current pgvector dense retrieval, fuse with Reciprocal Rank Fusion. Dense finds semantically similar content; sparse catches exact terms (deal names, financial figures).
**Why transformative**: M&A conversations are dense with proper nouns and exact figures. "Acme Corp $2.1M EBITDA" fails pure semantic search but BM25 catches it perfectly. Evidence accuracy is the foundation of the entire COL.
**Extends**: RAG service (`rag_rest_api.py`), `chat_evidence_builder.py`
**Complexity**: MEDIUM
**Source**: Claude-AI (#1)

### #7: Morning Deal Briefing
**What**: Daily automated summary: "Since your last session (18h ago): Acme Corp received 2 new bundles, Beta Inc's LOI was approved, 3 quarantine items need review, Gamma LLC flagged new risk." Personalized, prioritized, delivered to dashboard or email.
**Why transformative**: Bloomberg has morning market summaries. No M&A platform has morning deal flow summaries. Eliminates the daily "check all systems" ritual.
**Extends**: Section 5 (Summarization), Section 4 (Deal Brain)
**Complexity**: MEDIUM
**Source**: Claude-UX (#14)

### #8: Counterfactual Analysis Engine
**What**: Using deterministic replay, answer "what if" questions about past decisions. Replay a turn snapshot with modified inputs, show the divergent Deal Brain state and recommendations.
**Why transformative**: No decision-support tool — in any industry — combines deterministic replay with structured knowledge representation and a conversational interface to formulate counterfactuals. This is category-defining.
**Extends**: Section 6 (Deterministic Replay) — add counterfactual endpoint
**Complexity**: HIGH
**Source**: Claude-UX (#4)

### #9: MemGPT-Style Tiered Memory
**What**: Three explicit memory tiers — Working (in-context 6-message window), Recall (Deal Brain facts + summaries, searched before each LLM call), Archival (full history, searched on demand). Replace the current flat memory model.
**Why transformative**: Deals span months. Current 90-day TTL on context means long deals lose early context. Tiered memory mirrors how senior analysts work: remember key facts (recall), know where to find details (archival).
**Extends**: Section 5 (Summarization), context_store.py
**Complexity**: HIGH
**Source**: Claude-AI (#9)

### #10: Canary Tokens for Data Leak Detection
**What**: Inject invisible unique strings into sensitive RAG chunks. If they appear in LLM output without authorization, block the response and alert security. Proactive defense against data exfiltration via prompt injection.
**Why transformative**: No M&A platform or AI tool has implemented this pattern. Bridges the cybersecurity concept of canary tokens into LLM safety — a novel combination.
**Extends**: Section 7 (Injection Defense), Evidence Builder
**Complexity**: LOW
**Source**: Gemini (IDEA-8)

---

## QUICK WINS (LOW Complexity, HIGH Impact)

These can each be implemented in 1-3 days with no architectural changes.

| # | Idea | Source | Impact |
|---|------|--------|--------|
| QW-1 | Ghost Knowledge Detection | Claude-UX | Closes team-knowledge gap in every conversation |
| QW-2 | Deal Momentum Score | Claude-UX | Instant visual deal health on dashboard |
| QW-3 | Canary Tokens | Gemini | Novel security defense, minimal code |
| QW-4 | Contextual Chunk Headers for RAG | Claude-AI | Better retrieval & citations, prepend strings to chunks |
| QW-5 | @Agent Mentions in Deal Notes | Claude-UX | Eliminates chat context-switching for quick questions |
| QW-6 | Forgetting Curve Confidence Decay | Claude-AI | Auto-deprioritizes stale facts, simple math |
| QW-7 | Smart Paste with Entity Extraction | Gemini | Better data quality from user input |
| QW-8 | Predictive Budgeting | Gemini | "Budget exceeded in 4 days" alerts |
| QW-9 | Bottleneck Heatmap | Claude-UX | Pipeline stage temperature overlay |
| QW-10 | JSON Mode via vLLM Structured Generation | Claude-AI | Eliminates entire class of JSON parsing bugs |
| QW-11 | Schema-Validated Tool Args (Strict Pydantic) | Claude-AI | Catches hallucinated tool args before network calls |
| QW-12 | Generalized Tool-Use Verification | Claude-AI | Extend No-Illusions Gate to all mutating tools |
| QW-13 | Spaced Repetition Deal Memory | Claude-UX | Proactive fact surfacing based on forgetting curves |

---

## ALL IMPROVEMENT IDEAS (Deduplicated, 45 Total)

### Category A: RAG & Retrieval (5 ideas)

**A-1: Hybrid Dense+Sparse Retrieval (BM25 Fusion)** [MEDIUM]
Add BM25 keyword index to `crawledpage.content`, fuse with vector search via Reciprocal Rank Fusion. Catches exact terms (deal names, financial figures) that pure semantic search misses.
*Files*: `rag_rest_api.py:106-171`, `chat_evidence_builder.py:312-366`
*Source*: Claude-AI

**A-2: HyDE (Hypothetical Document Embeddings)** [MEDIUM]
Before RAG query, generate a hypothetical answer via cheap LLM call, embed that as the retrieval query. Dramatically improves retrieval for vague questions like "what should I worry about?"
*Files*: `chat_evidence_builder.py:312-366`, `rag_rest.py:91-158`
*Source*: Claude-AI

**A-3: RAPTOR Hierarchical Retrieval** [HIGH]
Build tree of summaries: leaf=raw chunks, intermediate=cluster summaries, root=deal-level summaries. Top-down traversal for questions at any granularity level.
*Files*: `rag_rest_api.py:174-231`, `chat_evidence_builder.py:267-310`
*Source*: Claude-AI. Related: Gemini IDEA-5 (Recursive Hierarchical Summarization)

**A-4: Contextual Chunk Headers** [LOW]
Prepend each RAG chunk with document title, section hierarchy, and deal association before embedding. Improves both retrieval relevance and citation accuracy.
*Files*: `rag_rest_api.py:174-231`, `chat_evidence_builder.py:460-471`
*Source*: Claude-AI

**A-5: Deal-Scoped RAG Namespaces** [MEDIUM]
Partition the vector store by deal_id so queries only search within the relevant deal's documents. Eliminates cross-deal information leakage and improves retrieval precision.
*Extends*: Section 3, Section 7 (Security)
*Source*: Synthesis

---

### Category B: Agent Architecture (6 ideas)

**B-1: Reflexion Self-Critique Loop** [MEDIUM]
Add "critique" node after final response that checks evidence grounding, factual accuracy, and question-addressing. Max 2 refinement loops.
*Files*: `graph.py:828-863`, `graph.py:359-441`
*Source*: Claude-AI

**B-2: Plan-and-Execute Decomposition** [HIGH]
For complex multi-step queries, generate a structured execution plan first, then execute steps sequentially. Uses FLASH for planning, PRO for execution.
*Files*: `graph.py:828-863`, `GraphState` schema
*Source*: Claude-AI

**B-3: Generalized Tool-Use Verification** [LOW]
Extend the No-Illusions Gate pattern from `transition_deal` to all mutating tools. Every state-changing tool gets a post-execution assertion.
*Files*: `deal_tools.py:333-363`, `graph.py:562-600`
*Source*: Claude-AI

**B-4: Multi-Specialist Agent Delegation** [HIGH]
Route complex queries to specialist sub-graphs: Financial Analyst, Risk Assessor, Deal Memory Expert. Mirrors how M&A teams operate.
*Files*: `graph.py:828-863`, existing pattern in `Zaks-llm/agents/orchestrator.py`
*Source*: Claude-AI

**B-5: Active Drift Resolution Agent** [MEDIUM]
When Deal Brain detects a contradiction, spawn a background investigator that searches evidence to propose resolution. Moves from passive flagging to active self-correction.
*Extends*: Section 4.5 (Drift Detection)
*Source*: Gemini (IDEA-4)

**B-6: Devil's Advocate Agent** [MEDIUM]
Periodic background review of Deal Brain that generates counter-arguments and blind spots. "You assume regulatory approval will be fast, but 3 recent deals in this sector were delayed."
*Extends*: Section 4 (Deal Brain), Multi-Agent Graph
*Source*: Gemini (IDEA-14)

---

### Category C: Memory & Knowledge (6 ideas)

**C-1: MemGPT-Style Tiered Memory** [HIGH]
Three tiers — Working (in-context), Recall (Deal Brain facts, searched before each call), Archival (full history, explicit retrieval). Replaces flat memory model.
*Files*: `context_store.py:145-471`, `graph.py:257-284`
*Source*: Claude-AI

**C-2: Forgetting Curve Confidence Decay** [LOW]
Apply Ebbinghaus temporal decay to fact confidence: facts not reinforced in recent conversations see confidence drop. Naturally deprioritizes stale information.
*Files*: `context_store.py:28-43`, `context_store.py:96-125`
*Source*: Claude-AI

**C-3: Background Memory Consolidation** [MEDIUM]
During user idle time (>10 min), re-summarize active deal brains, detect cross-deal patterns, pre-compute embeddings. Agent is "always ready" when user returns.
*Files*: `context_store.py:376-429`
*Source*: Claude-AI

**C-4: Cross-Deal Entity Resolution Graph** [HIGH]
Knowledge graph connecting deals via shared entities (people, companies, terms, risks). Enables queries like "show all deals where Person X was decision maker."
*Extends*: Section 4 (Deal Brain becomes graph node)
*Source*: Gemini (IDEA-1) + Claude-UX (#5)

**C-5: Deal Precedent Network** [MEDIUM]
Auto-find "precedent deals" — past deals with similar characteristics. "This deal is 87% similar to Apex Systems 2025. That deal had 6-week regulatory delay."
*Extends*: Section 4, Section 5
*Source*: Claude-UX

**C-6: Relationship Intelligence Timeline** [MEDIUM]
Aggregate all interactions with each broker across all deals: deal count, success rate, response times, terms evolution. Auto-maintained "broker dossier."
*Extends*: Section 4, Section 12
*Source*: Claude-UX

---

### Category D: Structured Output & Type Safety (4 ideas)

**D-1: JSON Mode via vLLM Structured Generation** [LOW]
Use `response_format={"type": "json_object"}` and Outlines-based constrained generation for all JSON-producing prompts. Eliminates parsing failures.
*Files*: `llm.py:34-67`
*Source*: Claude-AI

**D-2: Schema-Validated Tool Args (Strict Pydantic)** [LOW]
Add `extra="forbid"` to ALL tool input schemas. Replace manual validation in graph.py with single `model_validate()` call.
*Files*: `deal_tools.py:146-205`, `graph.py:488-560`
*Source*: Claude-AI

**D-3: Chain-of-Verification for Evidence Grounding** [MEDIUM]
After response generation, separate verification pass lists each factual claim, checks support in evidence, revises unsupported claims. Inline, not post-hoc.
*Files*: `graph.py:359-441`, `chat_evidence_builder.py:143-187`
*Source*: Claude-AI

**D-4: Typed SSE Event Schema with Runtime Validation** [MEDIUM]
Discriminated union Pydantic models for each SSE event type. Runtime validation before sending. TypeScript types generated from same schema.
*Files*: `graph.py:1188-1240`, `schemas/chat.py`
*Source*: Claude-AI

---

### Category E: Cognitive Science & Decision Support (4 ideas)

**E-1: Ghost Knowledge Detection** [LOW]
Detect when users reference facts NOT in Deal Brain. Auto-extract with `source_type: "user_assertion"`, prompt for confirmation.
*Extends*: Section 4.4 (Extraction Prompt), Section 4.5 (Drift Detection)
*Source*: Claude-UX

**E-2: Decision Fatigue Sentinel** [MEDIUM]
Track decision velocity, session length, and pattern quality. After N high-stakes decisions in a window, insert a "cognitive checkpoint" with summary and pause suggestion.
*Extends*: Section 4, Section 5
*Source*: Claude-UX

**E-3: Spaced Repetition Deal Memory** [LOW]
Proactively surface deal facts the user is likely to have forgotten, based on forgetting curve. "Remember this?" card when opening a deal chat.
*Extends*: Section 4.3 (Write Triggers — add "read trigger")
*Source*: Claude-UX

**E-4: Counterfactual Analysis Engine** [HIGH]
Using replay infrastructure, answer "what if" about past decisions. Replay turn snapshot with modified inputs, show divergent Deal Brain state.
*Extends*: Section 6.4 (Replay Endpoint)
*Source*: Claude-UX

---

### Category F: Predictive Intelligence (4 ideas)

**F-1: Deal Momentum Score** [LOW]
Composite 0-100 metric: stage velocity + event frequency + open item completion + risk trajectory + action completion. Color-coded on deal cards.
*Extends*: Section 4, Section 13
*Source*: Claude-UX

**F-2: Deal Stall Predictor** [MEDIUM]
Survival model from historical stage durations. "14 days in screening. Median is 8. Past 15 days = 73% chance of going to junk."
*Extends*: Section 4, Section 13
*Source*: Claude-UX

**F-3: Bottleneck Heatmap** [LOW]
Temperature overlay on pipeline stages based on deal accumulation rate, average duration, stale deal ratio. "Hot" stages are bottlenecks.
*Extends*: Section 13
*Source*: Claude-UX

**F-4: Risk Cascade Predictor** [MEDIUM]
When a risk is flagged on one deal, scan all active deals for same risk pattern. Portfolio-level risk management, not just deal-level.
*Extends*: Section 4.5 (Drift Detection)
*Source*: Claude-UX

---

### Category G: Collaboration (3 ideas)

**G-1: Comment Threads on Deal Facts** [MEDIUM]
Inline comment threads on each Deal Brain fact/risk/decision. "Broker reported $12M but CIM shows $10.8M. Need to reconcile." AI participates as fact-checker.
*Extends*: Section 4.2 (Deal Brain schema), Section 10
*Source*: Claude-UX

**G-2: @Agent Mentions in Deal Notes** [LOW]
Type "@agent what is the market multiple for SaaS at $12M ARR?" in a deal note. Agent responds inline, visible to all team members. Eliminates context switching.
*Extends*: Section 9, Section 4
*Source*: Claude-UX

**G-3: Shared Deal Workspace Presence** [MEDIUM]
Live presence indicators on deal workspace — who else is viewing, which tab, whether typing a note. Figma/Linear model for deal management.
*Extends*: Section 10 (Multi-User)
*Source*: Claude-UX

---

### Category H: Ambient Intelligence (5 ideas)

**H-1: Morning Deal Briefing** [MEDIUM]
Daily automated summary of overnight changes across all deals. Personalized, prioritized, to dashboard or email.
*Extends*: Section 5, Section 4
*Source*: Claude-UX

**H-2: Context-Aware Command Palette** [MEDIUM]
Cmd+K palette adapts to current page/deal/conversation. Surfaces deal-specific actions, recently discussed facts as searchable items.
*Extends*: Section 9, Section 4
*Source*: Claude-UX

**H-3: Anomaly-Driven Deal Alerts** [MEDIUM]
Learn the natural cadence of each deal, alert on deviations. A complex deal that normally moves slowly shouldn't trigger the same alerts as a fast deal.
*Extends*: Section 13
*Source*: Claude-UX

**H-4: Ambient Intelligence Sidebar** [MEDIUM]
Context sidebar that silently updates with relevant Deal Brain facts, similar deals, and news as user chats. Information comes to the user.
*Extends*: Chat UI
*Source*: Gemini (IDEA-15)

**H-5: Predictive Budgeting** [LOW]
Forecast cost: "At current usage, this deal exceeds $50 budget in 4 days." Suggest cheaper models or optimization.
*Extends*: Section 13 (Cost Governance)
*Source*: Gemini (IDEA-13)

---

### Category I: Security & Trust (5 ideas)

**I-1: Canary Tokens for Leak Detection** [LOW]
Inject invisible unique strings into sensitive RAG chunks. Block and alert if they appear in unauthorized LLM output.
*Extends*: Section 7, Evidence Builder
*Source*: Gemini (IDEA-8)

**I-2: Semantic Firewall (LLM Guard)** [MEDIUM]
Augment regex injection detection with a small BERT-based classifier that detects "jailbreak intent" semantically. Catches what regex can't.
*Extends*: Section 7 (Injection Defense)
*Source*: Gemini (IDEA-3)

**I-3: Role-Based Redaction Views** [HIGH]
Share chat threads with external parties where specific entities (price, strategy) are auto-redacted based on viewer's role. "Secure View" for chats.
*Extends*: Section 10, Section 12
*Source*: Gemini (IDEA-10)

**I-4: JIT (Just-in-Time) Tool Access** [MEDIUM]
Instead of static RBAC, allow ephemeral one-time permissions. User requests, admin approves, temporary token for that specific action. Reduces permission bloat.
*Extends*: Section 9 (Tool Scoping)
*Source*: Gemini (IDEA-6)

**I-5: Decision Journal with Outcome Tracking** [MEDIUM]
Capture every decision with rationale, context, and evidence. Correlate with actual outcomes months later. Close the feedback loop.
*Extends*: Section 4.2, Section 6
*Source*: Claude-UX

---

### Category J: UX & Product (3 ideas)

**J-1: Living Deal Memo** [MEDIUM]
Deal Brain auto-generates a human-readable Markdown/PDF memo that updates in real-time. Download and share instantly. Bridges "AI Knowledge" and "Business Deliverable."
*Extends*: Section 12 (Export), Section 4
*Source*: Gemini (IDEA-7)

**J-2: Fact Lineage Explorer** [MEDIUM]
Visual UI linking every Deal Brain fact to the specific chat message or document citation that established it. Builds trust: users can audit WHY the AI believes "EBITDA is $5M."
*Extends*: Section 4 (Deal Brain UI), Section 8
*Source*: Gemini (IDEA-12)

**J-3: Smart Paste with Entity Extraction** [LOW]
When pasting text into chat, auto-detect and offer to extract entities (people, dates, amounts) before sending. Better data quality for Deal Brain.
*Extends*: Section 4, Chat UI
*Source*: Gemini (IDEA-11)

---

### Category K: Infrastructure (2 ideas)

**K-1: Local-First Sync with PGlite** [HIGH]
Replace localStorage with PGlite (WASM Postgres) in browser. Full SQL querying and search while offline. "Offline Mode" becomes "Full Feature Mode (Local)."
*Extends*: Section 3, Section 14
*Source*: Gemini (IDEA-2)

**K-2: Sentiment & Negotiation Coach** [MEDIUM]
Analyze tone of user messages and counterparty documents. Side-channel advice: "Consider a more conciliatory tone to close this point."
*Extends*: Section 3 (Message Metadata), Chat UI
*Source*: Gemini (IDEA-9)

---

## MOONSHOT IDEAS (5)

### MOON-1: Deal Simulator 3000 (Monte Carlo)
Simulation engine using Deal Brain facts to run thousands of "What If" scenarios. "If we increase offer by 5%, closing probability increases 12% but ROI drops 3%." Requires probabilistic modeling and counterfactual reasoning.
*Source*: Gemini

### MOON-2: The Deal Auto-Pilot (Level 5 Autonomy)
Agent doesn't just chat — it drives. Schedules meetings, drafts LOIs, sends emails, updates CRM. Human-on-the-loop for critical approvals only. Requires robust agentic loop with reliable error recovery.
*Source*: Gemini

### MOON-3: Federated Deal Learning
Train a global "Deal Model" across all ZakOps clients without data leaving infrastructure. Learns "General Negotiation Patterns" securely. Requires federated learning and differential privacy.
*Source*: Gemini

### MOON-4: Voice-First Deal Room
"Siri for M&A" in the physical deal room. "Zak, pull up the EBITDA charts." "Zak, record this decision." Requires real-time audio processing, speaker diarization, and hardware integration.
*Source*: Gemini

### MOON-5: Blockchain Audit Trail
Anchor every Decision and Fact in Deal Brain to an immutable ledger. Mathematical proof of "Who knew what, when" for post-deal litigation or compliance.
*Source*: Gemini

---

## GAPS & FORENSIC FINDINGS (23 Unique)

### CRITICAL (3)

**GAP-C1: deal_budgets FK References Non-Unique Column** [MIGRATION FAILURE]
`deal_budgets.deal_id REFERENCES chat_threads(deal_id)` — but `deal_id` is NOT unique on `chat_threads` (multiple threads per deal). PostgreSQL will reject this FK at creation time.
*Spec*: Section 13.2, line 1594
*Fix*: Remove FK. Make `deal_id VARCHAR(20) PRIMARY KEY` with no FK constraint. Use application-level validation.

**GAP-C2: user_id Type Mismatch Across Systems** [ARCHITECTURAL INCOHERENCE]
Spec uses `INTEGER` everywhere, but existing `decision_ledger` uses `VARCHAR(255)`, `approvals` uses `actor_id VARCHAR(255)`, backend operators use `UUID`. GDPR cascade mixes these types in a single deletion sequence.
*Spec*: Section 3.2 (lines 196, 229), Section 10.4 (line 1311), Section 11.5 (lines 1414-1436)
*Fix*: Standardize on one type. Create cross-reference mapping. Document explicitly.

**GAP-C3: No Partition Automation — Only 2-3 Static Partitions** [PRODUCTION FAILURE]
`turn_snapshots` has 2 partitions (2026_02, 2026_03). `cost_ledger` has 1 (2026_02). No `pg_partman`, no cron, no default partition. After March 2026, all INSERTs fail.
*Spec*: Section 6.2 (lines 846-852), Risk R8 (line 1793)
*Fix*: Add `create_monthly_partitions()` function, pg_cron scheduling, and DEFAULT partition as safety net.

### HIGH (5)

**GAP-H1: Dashboard Middleware Missing /api/v1/chatbot Routes** [ENDPOINT 404s]
New chatbot endpoints will 404 or be proxied to wrong service. Middleware `handledByRoutes` doesn't include `/api/v1/chatbot/`.
*Spec*: Section 3.4 (lines 291-346), Section 3.8 (lines 427-443)
*Fix*: Add routing subsection specifying Next.js route handlers and middleware updates.

**GAP-H2: Service Token Returns user_id=0, Defeats Multi-User Isolation** [SECURITY]
`get_session_or_service()` returns `user_id=0` for service tokens. If dashboard uses service token, all threads have `user_id=0`. Transition to JWT timing undefined.
*Spec*: Section 3.4, Section 10.1-10.2
*Fix*: Define auth requirements per phase. Phase 1: X-User-Id header. Phase 2: JWT required.

**GAP-H3: Backend Deal Brain Endpoints Missing from Contract Surface Pipeline** [TYPE DRIFT]
New backend endpoints (`PATCH /api/deals/{id}/brain`, etc.) not mentioned in OpenAPI contract or sync pipeline.
*Spec*: Section 4.3, Section 10.4, Appendix A
*Fix*: Add "Contract Surface Updates" subsection to Section 16.

**GAP-H4: Cross-Database deal_id Has No Referential Integrity** [DATA ORPHANS]
7 tables in `zakops_agent` reference `deal_id` from `zakops` database. No FK possible across databases. No cleanup mechanism on deal deletion.
*Spec*: Section 3.2, Section 11.5
*Fix*: Application-level `DealReferenceValidator`. Periodic reconciliation job. Deal deletion webhook.

**GAP-H5: SQLite User Store Not Migrated to PostgreSQL** [ARCHITECTURAL SPLIT]
Agent API uses SQLite for users/sessions. Spec places chat in PostgreSQL. GDPR deletion now spans 3 storage engines (SQLite + 2 PostgreSQL databases).
*Spec*: Section 11.5, Appendix D
*Fix*: Migrate `user` and `session` tables to `zakops_agent` PostgreSQL. Aligns with "PostgreSQL as single source of truth."

### MEDIUM (12)

**GAP-M1: Redundant deal_id in chat_messages** — Child duplicates parent scope column. Remove to normalize. (Gemini Finding 2)

**GAP-M2: Missing UNIQUE Constraint on (thread_id, turn_number)** — Index exists but no UNIQUE guarantee. Critical for deterministic replay ordering. (Gemini Finding 3)

**GAP-M3: Migration Number Tracking Not Addressed** — Backend migration `028` is next available but no `INSERT INTO schema_migrations` statement included. (Claude-Forensic GAP-002)

**GAP-M4: Write Path Spans Two Databases Without Distributed Transaction** — Chat writes to `zakops_agent`, Deal Brain writes to `zakops`. Partial failure leaves inconsistent state. Fix: async extraction with outbox pattern. (Claude-Forensic GAP-008)

**GAP-M5: Historical Backfill Into Partitioned Tables Not Addressed** — Pre-2026-02 data has no partition. Also, `turn_snapshots` requires NOT NULL fields that historical data lacks. Fix: backfill only threads/messages, not snapshots. (Claude-Forensic GAP-010 + Gemini Finding 4)

**GAP-M6: PII Redaction Not Integrated With Injection Guard** — Two parallel security systems (injection_guard.py and output_validation.py) without unified pipeline. Fix: define full input-to-output security chain. (Claude-Forensic GAP-011)

**GAP-M7: Existing Security Tests Not Updated** — 5 existing test files will become stale. New features (RBAC, JWT, GDPR cascade) ship without tests. Fix: add Test Plan appendix. (Claude-Forensic GAP-012)

**GAP-M8: Compliance Encryption Not Fully Designed** — `encrypted BOOLEAN` column but no spec for which columns, how JSONB, key rotation, or queryability. Fix: encrypt entire snapshot as single blob. (Claude-Forensic GAP-013)

**GAP-M9: Email Ingestion Integration Missing** — Backend has complete email system but spec never mentions how emails feed Deal Brain or appear in chat timeline. Fix: add Section 4.7. (Claude-Forensic GAP-014)

**GAP-M10: New Proposal Type (correct_brain_summary) Underspecified** — Added as concept but no handler, no integration with `canonicalize_proposal_type()`. Fix: define execution handler and wire into pipeline. (Claude-Forensic GAP-017)

**GAP-M11: No Rollback Migrations Defined** — 3 new migrations with no corresponding rollback scripts. Backend has precedent (`001_rollback.sql`). Fix: add rollback scripts. (Claude-Forensic GAP-019)

**GAP-M12: Materialized View Refresh Not Scheduled** — `deal_cost_summary` materialized view never auto-refreshes. Dashboard shows stale cost data. Fix: either regular view, trigger, or pg_cron schedule. (Claude-Forensic GAP-020)

### LOW (3)

**GAP-L1: MCP Server Tools Not in COL Governance** — 12 MCP tools operate outside cost tracking, tool scoping, and audit scope. Note as V2 integration. (Claude-Forensic GAP-015)

**GAP-L2: SSE Event Types Not Cataloged** — Missing event types: thread_updated, brain_updated, summary_generated, injection_alert, legal_hold_set. Fix: add SSE Event Catalog section. (Claude-Forensic GAP-016)

**GAP-L3: Proposal Status Tracking in JSONB Lacks Concurrency Control** — Updating proposal status requires complex JSONB path updates. Consider separate `chat_proposals` table. (Gemini Finding 5)

---

## STATISTICS

| Metric | Count |
|--------|-------|
| Total unique improvement ideas | 45 |
| — LOW complexity | 13 |
| — MEDIUM complexity | 22 |
| — HIGH complexity | 10 |
| Total gaps (forensic findings) | 23 |
| — CRITICAL | 3 |
| — HIGH | 5 |
| — MEDIUM | 12 |
| — LOW | 3 |
| Total moonshot ideas | 5 |
| Innovation domains covered | All 7 from mission (RAG, Agent, Memory, Cognitive, Predictive, Collaboration, Security) |
| Quick wins (LOW + HIGH impact) | 13 |
| Source: Gemini | 15 ideas + 8 gaps + 5 moonshots |
| Source: Claude-AI | 15 ideas |
| Source: Claude-Forensic | 20 gaps |
| Source: Claude-UX | 18 ideas |
| Source: Synthesis | 2 ideas |
| Overlap/merged | 5 items |

---

## DEAL BRAIN IS THE KEYSTONE

**14 of 18 Claude-UX ideas depend on Deal Brain v2 being implemented first.** The Deal Brain is the single highest-leverage component in the entire COL spec. It is the foundation for:
- Ghost Knowledge Detection, Spaced Repetition, Decision Journal, Counterfactual Analysis
- Cross-Deal Entity Graph, Deal Precedent Network, Relationship Timeline
- Deal Momentum Score, Stall Predictor, Risk Cascade Predictor
- Comment Threads, Morning Briefing, Anomaly Alerts
- Fact Lineage Explorer, Living Deal Memo

**Recommendation**: Prioritize Deal Brain v2 (Section 4) as the P0 implementation alongside Storage Unification (Section 3). Everything else cascades from these two foundations.

---

## IMPLEMENTATION PRIORITY MATRIX

```
                HIGH IMPACT
                    │
    ┌───────────────┼───────────────┐
    │  STRATEGIC     │  QUICK WINS   │
    │  (Do next)     │  (Do first)   │
    │                │               │
    │  B-1 Reflexion │  E-1 Ghost    │
    │  C-1 Tiered   │  F-1 Momentum │
    │  A-1 Hybrid   │  I-1 Canary   │
    │  H-1 Briefing │  D-1 JSON     │
    │  I-5 Decision │  A-4 Headers  │
    │  C-5 Precedent│  G-2 @Agent   │
HIGH├───────────────┼───────────────┤LOW
EFFORT│  INVEST       │  NICE-TO-HAVE │
    │  (Plan for)    │  (Backlog)    │
    │                │               │
    │  C-4 Graph    │  K-2 Sentiment│
    │  E-4 Counter  │  H-4 Sidebar  │
    │  B-2 Plan-Exec│  H-5 Budget   │
    │  B-4 MultiSpec│               │
    │  K-1 PGlite   │               │
    │  I-3 Redaction│               │
    └───────────────┼───────────────┘
                    │
                LOW IMPACT
```

---

## NEXT STEPS

1. **Resolve 3 CRITICAL gaps** before any implementation begins (GAP-C1, C2, C3)
2. **Update COL-DESIGN-SPEC-V1.md** with all gap fixes and selected improvements
3. **Implement Quick Wins** in a single sprint (13 items, ~2 weeks total)
4. **Build Deal Brain v2 + Storage Unification** as the P0 foundation
5. **Layer Strategic improvements** in P1 (Reflexion, Hybrid Retrieval, Tiered Memory, Morning Briefing)
6. **Plan Investments** for P2+ (Knowledge Graph, Counterfactual, Multi-Specialist Agents)

---

*Generated by hybrid TriPass + manual Claude Opus investigation. TP-20260213-003326.*
