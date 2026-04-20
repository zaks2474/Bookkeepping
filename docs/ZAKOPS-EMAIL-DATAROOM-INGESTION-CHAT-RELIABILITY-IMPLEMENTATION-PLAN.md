# ZakOps Email→DataRoom Ingestion + Chat UX Reliability — Implementation Plan

**Owner:** ZakOps (Lead Engineer: Codex)  
**Status:** Draft — Plan Only (Implementation next)  
**Date:** 2025-12-27  
**Scope:** Production-ready upgrades (no rewrite-from-scratch)  

**Primary baselines**
- Ingestion: `/home/zaks/scripts/sync_acquisition_emails.py`
- Registry: `/home/zaks/scripts/deal_registry.py`
- Event store: `/home/zaks/scripts/deal_events.py` (+ registry emitters in `/home/zaks/scripts/deal_registry_events.py`)
- Quarantine: existing quarantine foundation (do not rebuild; integrate)
- Run ledger: `/home/zaks/bookkeeping/scripts/run_ledger.py` → `/home/zaks/logs/run-ledger.jsonl`
- RAG REST API: `http://localhost:8051` (configurable; `8052` also supported) (`/rag/add`, `/rag/query`, `/rag/stats`, `/rag/url`)
- Chat backend: `/home/zaks/scripts/deal_lifecycle_api.py` (port `8090`) + `/home/zaks/scripts/chat_orchestrator.py`
- Dashboard UI: `/home/zaks/zakops-dashboard` (Next.js; chat: `/home/zaks/zakops-dashboard/src/app/chat/page.tsx`)
- Chat spec: `/home/zaks/bookkeeping/docs/CHAT-FRONT-DOOR-PLAN.md` (controller-local, Gemini-worker, audit + gates)

---

## 1) Goal

Upgrade Email→DataRoom ingestion and dashboard chat reliability into a **world-class, deal-centric pipeline** aligned with platform principles:

- **Deal is the unit of work**
- **Registry + events are source of truth; folders are derived views**
- **Deterministic-first; Gemini is a worker, not the controller**
- **Audit everywhere** (run-ledger + events + per-email outcomes)
- **No silent drops** (every email ends in a tracked terminal outcome)
- **No irreversible actions without approval** (moves/renames/deletes become proposals by default)
- **Secret-scan gates** before **any cloud call** and before sensitive persistence (RAG, SharePoint, traces)

### Locked operator decisions (already agreed)
- **Gemini budget defaults:** `$5/day` and `$0.50/request` (override via env/config; enforced + audited)
- **Vendor link intake:** **drop-zone only** (no Playwright-assisted browser mode in initial scope)
- **Chat stack target:** Deal Lifecycle API (`/home/zaks/scripts/deal_lifecycle_api.py`) + dashboard (`/home/zaks/zakops-dashboard`)

---

## 2) Non-Goals (Explicit)

- No “big bang” rewrite of `/home/zaks/scripts/sync_acquisition_emails.py`.
- No changes that break the existing registry/event store/quarantine/run-ledger foundations.
- No unattended portal logins or bypassing authentication flows for vendor links.
- No mass folder renames/moves by default (must be staged as proposals and/or handled via quarantine/link queue resolution).

---

## 3) Target Outcomes (Acceptance Contract)

### 3.1 Terminal outcome rule (No silent drops)
Every ingested email must end in exactly one terminal disposition:

1) **Deal-linked event chain** (email linked to a deal, with events for attachments/extraction/classification/indexing as applicable), OR  
2) **Quarantine or queue item** with explicit operator resolution instructions (low-confidence match, blocked by secrets gate, portal/auth link, extraction failure, etc.).

### 3.2 Deterministic-first rule
Deterministic matching/classification is attempted first; Gemini worker is invoked only when:
- deterministic confidence is below thresholds, or
- the task is heavy extraction where worker adds value and passes gating.

### 3.3 Approval rule (No irreversible actions)
Any destructive action (move/rename/delete, overwriting canon artifacts) must:
- be emitted as a **Proposal** (dry-run “plan” record), or
- be performed only via an explicit `--apply` or “approve proposal” workflow.

---

## 4) Architecture: Single CLI, Internally Staged

We keep `sync_acquisition_emails.py` runnable as one CLI entrypoint, but reorganize internal logic into explicit stages with strict contracts and timing instrumentation.

### Implementation layout (incremental refactor, not a rewrite)
- New package: `/home/zaks/scripts/email_ingestion/` (pipeline orchestrator + stage modules + SQLite store + workers)
- Keep `/home/zaks/scripts/sync_acquisition_emails.py` as a thin CLI wrapper that calls the staged pipeline (preserves existing operator workflow)

### Stage 0 — Preflight
Validate and log:
- paths/config sanity (`DATAROOM_ROOT`, cache dirs, logs dir, downloads dir)
- dependency availability (OCR, PDF tooling, optional Gemini SDK)
- connectivity (IMAP, RAG API, optional Gemini)
- disk space thresholds
- read/write permissions and “dangerous mode” confirmations

**Output:** `PreflightReport` (success/fail + warnings) → run-ledger entry.

### Stage 1 — Fetch
Fetch emails (IMAP pull + metadata) in a defined window:
- `--since YYYY-MM-DD` or `--days N`
- incremental checkpoint (UID or date-based)

**Output:** raw email list with fetch metadata; write stage timing.

### Stage 2 — Normalize
Produce a canonical record:
- stable `email_id` (deterministic): normalized `message_id` preferred; fallback to hash of headers+body excerpt
- normalized sender/from/to, received_at, subject, bounded body excerpt, attachment metadata
- canonical provenance object (mailbox, uid, source)

**Output:** `CanonicalEmailRecord`

### Stage 3 — Match (Deterministic-first)
Match email to deal using registry matchers (tiered):
- exact listing ID/broker ref matches
- normalized canonical-name similarity
- broker domain cues (if available)
- thresholded confidence output

**Output:** `MatchDecision` (deal_id/candidates/confidence + rationale)

### Stage 4 — Persist (Control Plane)
Write authoritative records (audit-first):
- append `email_received` (and match decision) to `DealEventStore` **if matched**
- update registry mappings (email→deal) via existing registry APIs/emitters
- write derived artifacts (folder manifests, deterministic folder placement) **non-destructively**

If not confidently matched:
- create quarantine item (or link-queue item) with resolution instructions.

### Stage 5 — Extract (Bounded)
Extract text from attachments with strict bounds:
- size limits, timeouts, max pages, OCR only when needed
- persist extracted text as artifact or cached excerpt (configurable; do not store sensitive full-text unless policy allows)

### Stage 6 — Classify / Extract Facts (Gemini worker optional + gated)
Provider abstraction with deterministic-first routing:
- Email intent classification
- Document type classification
- Key fields extraction (company, asking, EBITDA, revenue, location, etc.)
- “missing materials” detection

Guardrails:
- secret scan gate **before cloud send**
- budget caps (default `$5/day`, max `$0.50/request`) tracked in state store
- timeout + fallback to deterministic/local
- store **minimal excerpts only** for cloud

### Stage 7 — Index (RAG)
Index bounded content to RAG:
- compute relative paths from `DATAROOM_ROOT` (no hard-coded replacements)
- stable URL scheme (configurable)
- errors become warnings with audit trail, not silent failures

---

## 5) Durable State Store (SQLite) — Replace JSON Caches

### Why
Current JSON caches are not crash-safe or concurrency-safe:
- `email_sync_processed.json` (dedup)
- `downloads_processed.json` (downloads scanner)

### Approach
Add a single SQLite state DB (WAL mode, atomic transactions) used by ingestion:

**File:** `${ZAKOPS_STATE_DB:-/home/zaks/DataRoom/.deal-registry/email_ingestion.db}`

Minimum tables:
- `runs`: run metadata, window, mode, summary json
- `emails`: stable ids + dedup keys + last disposition + last error
- `artifacts`: attachments/text extracts (sha256, path, size, provenance)
- `links`: link intake queue + status + outcomes
- `timings`: per-email per-stage timing rows
- `budgets`: daily provider budgets and spend (default `$5/day`, max `$0.50/request`)
- `checkpoints`: imap uid/date checkpoints and crash-resume markers
- `chat_sessions`, `chat_messages` (chat history + debug payloads; enables “refresh-safe” UX)

Required behaviors:
- **Idempotency**: same email twice → no duplicate processing (but can re-run in rebuild mode)
- **Rebuild window**: safely reprocess last N days (`--rebuild`) without destructive folder operations
- **Crash-safe resume**: checkpointed stage completion per email; resume continues pending work
- **Retention/compaction**: prune old runs/timings; VACUUM behind `--compact`

---

## 6) Rebuild Mode (“Last 30 days”) + Dry-Run Planning

New CLI flags (must be implemented):
- `--since YYYY-MM-DD` (or `--days 30`)
- `--rebuild` (forces re-extract/re-classify/re-index within window)
- `--dry-run` (writes a proposal plan only)

Rebuild semantics:
- Re-ingest emails in window (idempotent)
- Re-run extraction/classification/indexing based on `--rebuild`
- Write updates as **events + registry changes**
- Any move/rename/delete becomes a **proposal**, not executed by default

---

## 7) Gemini Worker Integration (Hybrid Provider Abstraction)

### 7.1 Provider interface
Add a provider abstraction used by ingestion and (later) chat:

Tasks:
- `classify_email_intent(record) -> {intent, confidence, rationale, snippets}`
- `classify_document_type(doc_excerpt) -> {type, confidence, rationale, citations}`
- `extract_key_facts(bundle) -> {fields, confidence, citations}`
- `detect_missing_materials(bundle) -> {missing, confidence, citations}`

Outputs must be strict JSON, with:
- `confidence` (0–1), `rationale` (short), `citations` (snippets or offsets), `warnings`

### 7.2 Guardrails (required)
- **Secret-scan gate** using existing tooling (`/home/zaks/scripts/zakops_secret_scan.py` helpers) before cloud send
- **Budget caps** (default `$5/day`, max `$0.50/request`) persisted in SQLite
- **Timeout + fallback** (deterministic/local fallback)
- **Excerpt minimization**: never send whole documents by default
- **Audit**: run-ledger entry per worker call (provider, cost, timeout, route) + per-email events

---

## 8) Vendor Link Retrieval Strategy (Operator-in-the-loop)

Implement a “Link Intake Queue” backed by SQLite:

Decision tree for each URL:
1) Public + direct-download → fetch (bounded) + attach with provenance
2) Auth/portal/uncertain → queue item with required operator action (no pretending)

Queue item must include:
- url, inferred vendor, inferred deal candidate(s) + confidence
- reason (auth required, blocked by robots, timeout, file too large, etc.)
- required operator action:
  - **Drop-zone ingestion** (`DataRoom/.intake-dropzone/<url_hash>_<filename>` or `DataRoom/.intake-dropzone/<url_hash>/<filename>`) with provenance linking back to the queued URL/email

Auth/portal domains are treated as “operator-required” by default (examples: `axial.net`, `tupelo.ai`, `vestedbb.com`, `dealroom.net`, `firmex.com`).

All outcomes must write:
- events (link_queued, link_downloaded, link_failed, link_resolved)
- run-ledger metrics

---

## 9) RAG Indexing Correctness (Paths + Bounds + Audited Warnings)

Required changes:
- Stop hard-coded string replacement for `rel_path`
- Compute `rel_path = Path(file).relative_to(DATAROOM_ROOT)` everywhere
- URL generation must be config-driven (`ZAKOPS_RAG_URL_PREFIX`)
- Indexing bounded by:
  - max file size
  - max extracted chars
  - timeout per file

Failures:
- must emit an audited warning + per-email event
- must not crash the entire run unless preflight says “strict mode”

---

## 10) Observability & Audit Trail (Run-ledger + Events + Timings)

### Per run
Write a run-ledger record (component `email_ingest`) with:
- counts by terminal outcome
- warnings/errors summary
- budget spend / blocked calls
- stage timing totals (fetch/extract/classify/index)
- checkpoint positions (IMAP UID/date)

### Per email
Write an event chain:
- `email_received`
- `deal_match_decision`
- `quarantine_created` OR `email_linked_to_deal`
- `document_attached` (per attachment)
- `text_extracted` (bounded)
- `document_classified` / `facts_extracted` (provider, confidence)
- `rag_indexed` (or `rag_index_failed`)
- `link_queued` / `link_downloaded`

### Timings
Persist per-email per-stage timing rows to SQLite so the dashboard can show breakdowns.

---

## 11) Dashboard Chat Reliability (Freeze + Persistence + Breakdown)

Follow `/home/zaks/bookkeeping/docs/CHAT-FRONT-DOOR-PLAN.md` for contracts and gates, but deliver at minimum:

### 11.1 Freeze fix
- stream rendering must be batched (buffer tokens, flush at 30–60fps) to avoid render storms
- add message list virtualization and pagination in `/home/zaks/zakops-dashboard/src/app/chat/page.tsx`

### 11.2 Persist history across refresh
- durable `session_id` (localStorage)
- backend session store (SQLite) for history + debug metadata (Deal Lifecycle API `8090`)
- page load restores from backend session endpoint; localStorage is only a fallback cache
  - note: `/home/zaks/bookkeeping/docs/CHAT-FRONT-DOOR-PLAN.md` mentions Redis; SQLite persistence is the initial “durable truth”, with Redis as an optional later cache layer

### 11.3 Show timing breakdown + debug
UI shows steps/timings per turn:
- Evidence build
- RAG query
- LLM controller
- Worker calls (Gemini/local) + budget/cost
- Tool/proposal creation

Debug panel shows:
- provider chosen, cache hits, warnings, gates triggered, blocked sends

---

## 12) Implementation Work Breakdown (Phased, Incremental)

### Phase A — Contracts + State Store (foundation)
1) Define canonical IDs and record schemas
2) Implement SQLite state store + migrations from JSON caches
3) Add run-ledger + timing helpers

### Phase B — Ingestion stage refactor (keep CLI)
1) Add stage wrapper functions with structured results + timing
2) Wire in state store for dedup/checkpoints/rebuild
3) Ensure “terminal outcome rule” is enforced

### Phase C — Gemini worker provider + gates
1) Provider abstraction
2) Gemini worker implementation with secret-scan + budgets + timeouts
3) Deterministic fallback and run-ledger auditing

### Phase D — Link intake queue + operator flows
1) Link classification + queue creation
2) Drop-zone ingestion with provenance (scanner + url_hash matching)

### Phase E — RAG indexing correctness + bounds
1) Centralize path computations
2) Add bounded indexing + audited warnings

### Phase F — Chat reliability
1) Backend: session persistence + breakdown payloads
2) Frontend: streaming batching + restore history + debug panel

---

## 13) Testing / Acceptance (Must Ship With Changes)

Add/extend smoke tests:
- ingestion preflight
- IMAP fetch (mockable)
- dedup idempotency: same email twice → 1 event chain
- rebuild window mode (`--days 30 --rebuild`)
- link intake queue behavior (public vs auth)
- Gemini worker gating (secret blocks; cost cap; timeout fallback)
- RAG indexing path correctness (URL + rel_path)
- chat UI: refresh preserves session; streaming doesn’t freeze under long response; breakdown visible

Add workflows:
- `make preflight`
- `make ingest-smoke`
- `make chat-smoke`

---

## 14) Runbook (Operator-Facing)

This repo must ship a short runbook covering:
- Run ingestion normally
- Run ingestion dry-run plan
- Rebuild last 30 days safely
- Resolve quarantine items
- Resolve link queue items (drop-zone workflow)
- Debug: where to look (run-ledger, events, state DB, logs)

---

## 15) Open Questions / Decisions to Confirm Before Coding

1) Confirm ingest SQLite DB path (default: `DataRoom/.deal-registry/email_ingestion.db`)
2) Canonical URL scheme for RAG: `https://dataroom.local/DataRoom/<rel_path>` vs `dataroom://<deal_id>/<artifact_id>`
3) “No silent drops” policy for junk/unsubscribe: treat as an audited terminal disposition (no quarantine) or always quarantine?
4) Which UI is the source of “freeze” issue: ZakOps dashboard UI, OpenWebUI, or both?
5) Chat session retention: TTL + cleanup cadence (e.g., 24h TTL with periodic cleanup)
6) Evidence bundle limits for chat (e.g., 40KB total, 8KB per source) to prevent UI + model overload
