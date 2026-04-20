# ZakOps Email-to-DataRoom Ingestion + Chat UX Upgrade

**Owner:** ZakOps (Lead Engineer)
**Status:** Plan — Ready for Implementation
**Date:** 2025-12-27

## Executive Summary

Refactor the 3,400-line email sync script into a staged pipeline with SQLite state management, add Gemini worker for AI-assisted classification, implement link intake queue for auth-required URLs, and upgrade dashboard chat with backend session persistence and performance fixes.

**Key Decisions (from user):**
- Gemini budget: $5/day, $0.50/request
- Link intake: Drop zone only (no Playwright browser mode)
- Chat backend: Now handled by Agent API at port 8095 (was port 8090, now decommissioned). Agent uses LangGraph + vLLM.

**Primary Baselines:**
- Ingestion: `/home/zaks/scripts/sync_acquisition_emails.py`
- Registry: `/home/zaks/scripts/deal_registry.py`
- Event store: `/home/zaks/scripts/deal_events.py`
- Run ledger: `/home/zaks/bookkeeping/scripts/run_ledger.py`
- Chat spec: `/home/zaks/bookkeeping/docs/CHAT-FRONT-DOOR-PLAN.md`

---

## Non-Goals (Explicit)

- No "big bang" rewrite of `sync_acquisition_emails.py`
- No changes that break existing registry/event store/quarantine/run-ledger foundations
- No unattended portal logins for vendor links
- No mass folder renames/moves by default (must be staged as proposals)
- No send tools for emails (draft only)

---

## Non-Negotiable Contracts

### 1. Terminal Outcome Rule (No Silent Drops)
Every ingested email must end in exactly one terminal disposition:
- **Deal-linked event chain** (email linked to deal with events for attachments/extraction/classification/indexing), OR
- **Quarantine/queue item** with explicit operator resolution instructions

### 2. Deterministic-First Rule
Deterministic matching/classification runs first; Gemini invoked only when:
- Confidence is below thresholds, OR
- Task is heavy extraction where worker adds value
- AND only if **all gates pass** (secret scan, budget, timeout)

### 3. Approval Rule (No Irreversible Actions)
Any destructive action (move/rename/delete/overwrite) must:
- Be emitted as a **Proposal** (dry-run "plan" record), OR
- Be performed only via explicit `--apply` or "approve proposal" workflow

### 4. No Unattended Portal Logins
Vendor links requiring auth must go through Link Intake Queue + drop-zone operator workflow.
No Playwright browser automation in scope.

### 5. Secret-Scan Gate + Budget Enforcement
- Secret-scan gate before **ANY** cloud send
- Budgets enforced: **$5/day** and **$0.50/request** (configurable)
- Excerpt minimization: never send whole documents
- Audit every worker call to run-ledger

---

## File Structure

### New Modules
```
/home/zaks/scripts/email_ingestion/
├── __init__.py
├── pipeline.py                     # Main orchestrator
├── config.py                       # Pipeline configuration
├── stages/
│   ├── __init__.py
│   ├── stage_0_preflight.py        # Paths, deps, connectivity, disk
│   ├── stage_1_fetch.py            # IMAP fetch (IMAPGmailClient)
│   ├── stage_2_normalize.py        # Canonical record, stable IDs
│   ├── stage_3_match.py            # Deal matching (deterministic-first)
│   ├── stage_4_persist.py          # Events, registry, folder artifacts
│   ├── stage_5_extract.py          # Text extraction (DocumentExtractor)
│   ├── stage_6_classify.py         # Gemini worker (optional, gated)
│   └── stage_7_index.py            # RAG indexing (RAGIndexer)
├── state/
│   ├── __init__.py
│   ├── sqlite_store.py             # SQLite state management
│   ├── checkpoint.py               # Crash-safe checkpoints
│   └── migrations.py               # JSON→SQLite migration
└── workers/
    ├── __init__.py
    ├── gemini_worker.py            # Gated Gemini classification
    └── link_intake.py              # Link queue management
```

### Modified Files
- `/home/zaks/scripts/sync_acquisition_emails.py` → Thin CLI wrapper
- `/home/zaks/scripts/chat_llm_router.py` → Add budget methods
- `/home/zaks/zakops-dashboard/src/app/chat/page.tsx` → Session loading, virtualization
- `/home/zaks/zakops-dashboard/src/lib/api.ts` → Session API functions

### New Database
- `/home/zaks/DataRoom/.deal-registry/email_ingestion.db` (SQLite)

---

## SQLite Schema

**Database:** `${ZAKOPS_STATE_DB:-/home/zaks/DataRoom/.deal-registry/ingest_state.db}`
**Mode:** WAL (Write-Ahead Logging) for concurrency safety

```sql
-- Processed emails (replaces email_sync_processed.json)
CREATE TABLE processed_emails (
    id INTEGER PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,
    body_hash TEXT NOT NULL,
    subject TEXT,
    sender TEXT,
    received_date TEXT,
    deal_id TEXT,
    match_confidence REAL,
    match_type TEXT,  -- 'listing_id'/'alias'/'thread'/'fuzzy'
    quarantine_id TEXT,
    status TEXT DEFAULT 'pending',  -- pending/processed/failed/quarantined
    stage_completed INTEGER DEFAULT 0,
    run_id TEXT NOT NULL,
    processed_at TEXT,
    UNIQUE(body_hash, sender)
);

-- Processed downloads (replaces downloads_processed.json)
CREATE TABLE processed_downloads (
    id INTEGER PRIMARY KEY,
    file_hash TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    email_id INTEGER REFERENCES processed_emails(id),
    deal_id TEXT,
    doc_type TEXT,
    classification_confidence REAL,
    classifier_used TEXT,  -- 'rules'/'gemini'/'hybrid'
    dest_path TEXT,
    run_id TEXT NOT NULL
);

-- Ingestion runs
CREATE TABLE ingestion_runs (
    id INTEGER PRIMARY KEY,
    run_id TEXT UNIQUE NOT NULL,
    started_at TEXT,
    ended_at TEXT,
    mode TEXT DEFAULT 'normal',  -- normal/rebuild/dry_run
    since_date TEXT,
    status TEXT DEFAULT 'running',
    emails_fetched INTEGER DEFAULT 0,
    emails_processed INTEGER DEFAULT 0,
    emails_quarantined INTEGER DEFAULT 0,
    stage_timings TEXT DEFAULT '{}'
);

-- Per-email per-stage timing rows (for dashboard breakdown)
CREATE TABLE timings (
    id INTEGER PRIMARY KEY,
    run_id TEXT NOT NULL,
    email_id INTEGER REFERENCES processed_emails(id),
    stage INTEGER NOT NULL,  -- 0-7
    stage_name TEXT NOT NULL,
    started_at TEXT,
    ended_at TEXT,
    duration_ms INTEGER,
    status TEXT,  -- 'success'/'failed'/'skipped'
    error TEXT
);

-- Crash-safe checkpoints
CREATE TABLE checkpoints (
    run_id TEXT NOT NULL,
    stage INTEGER NOT NULL,
    items_total INTEGER,
    items_completed INTEGER,
    state_snapshot TEXT,
    UNIQUE(run_id, stage)
);

-- Daily provider budgets and spend tracking
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,  -- YYYY-MM-DD
    provider TEXT NOT NULL,  -- 'gemini'
    daily_limit_usd REAL DEFAULT 5.0,
    spent_usd REAL DEFAULT 0.0,
    request_count INTEGER DEFAULT 0,
    last_updated TEXT,
    UNIQUE(date, provider)
);

-- Link intake queue
CREATE TABLE link_intake_queue (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    url_hash TEXT UNIQUE NOT NULL,
    source_email_id INTEGER,
    deal_id TEXT,
    requires_auth INTEGER DEFAULT 0,
    vendor TEXT,
    status TEXT DEFAULT 'pending',  -- pending/fetched/auth_required/failed
    downloaded_path TEXT,
    operator_note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions (backend persistence)
CREATE TABLE chat_sessions (
    session_id TEXT UNIQUE NOT NULL,
    scope_type TEXT NOT NULL,
    scope_deal_id TEXT,
    created_at TEXT,
    last_activity TEXT,
    turn_count INTEGER DEFAULT 0
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    citations TEXT,  -- JSON array
    proposals TEXT,  -- JSON array
    timings TEXT,  -- JSON object
    provider_used TEXT,
    cache_hit INTEGER DEFAULT 0
);
```

---

## Gemini Worker Design

```python
class GeminiWorker:
    """Gated Gemini worker with guardrails."""

    TASKS = {
        'email_classification': ['deal_opportunity', 'nda_request', 'cim_delivery', ...],
        'doc_type_classification': ['CIM', 'NDA', 'FINANCIALS', ...],
        'key_field_extraction': {...schema...},
        'missing_materials': ['CIM', 'NDA', 'Financials_3yr', ...]
    }

    # Guardrails:
    # 1. Secret scan gate - blocks if secrets in content
    # 2. Daily budget cap - $5/day
    # 3. Per-request max - $0.50/request
    # 4. Timeout 45s with retry
    # 5. Fallback to deterministic rules

    def classify(self, task, content, context) -> GeminiResult:
        if not self._check_gates(): return fallback_result
        if self._has_secrets(content): return fallback_result
        if not self._has_budget(task): return fallback_result

        try:
            return self._call_gemini_with_timeout(task, content)
        except:
            return fallback_result
```

**Output Schema:**
```python
@dataclass
class GeminiResult:
    success: bool
    label: str | None
    confidence: float
    reason: str
    extracted_fields: dict
    citations: list[str]
    fallback_used: bool
```

---

## Link Intake Queue Design

```
Link Detection (Stage 1)
       ↓
┌──────────────────┐
│ LinkIntakeQueue  │
└────────┬─────────┘
         ↓
   ┌─────┴─────┐
   ↓           ↓
Public      Auth-Required
   ↓           ↓
Auto-fetch  Queue for operator
   ↓           ↓
DataRoom    Drop zone upload
```

**Auth-Required Domains:** axial.net, tupelo.ai, vestedbb.com, dealroom.net, firmex.com

**Drop Zone Workflow:**
1. System detects auth-required link, queues it with status `auth_required`
2. Dashboard shows pending items in "Link Intake" view
3. Operator manually downloads file from portal
4. Operator places file in `~/DataRoom/.intake-dropzone/{url_hash}_{filename}`
5. Scanner (cron job) detects file, matches by url_hash prefix
6. File moved to deal folder, link marked `fetched`, event emitted

---

## CLI Flags (Rebuild Mode)

```bash
# Normal run
python3 sync_acquisition_emails.py

# Dry run (preview only)
python3 sync_acquisition_emails.py --dry-run

# Rebuild last N days
python3 sync_acquisition_emails.py --rebuild --days 30

# Rebuild from specific date
python3 sync_acquisition_emails.py --rebuild --since 2025-01-01

# Staged proposals only (no auto file moves)
python3 sync_acquisition_emails.py --rebuild --stage-proposal-only
```

---

## Per-Email Event Chain (Audit Trail)

Every processed email must emit this event sequence (as applicable):

```
email_received           → Initial receipt with metadata
deal_match_decision      → Match result (deal_id, confidence, type, candidates)
quarantine_created OR    → Low-confidence/blocked items
email_linked_to_deal     → Successful link to deal
document_attached        → Per attachment (filename, size, subfolder)
text_extracted           → Extraction complete (chars, method, OCR applied)
document_classified      → Classification result (type, confidence, provider)
facts_extracted          → Key fields (asking, EBITDA, etc.) if applicable
rag_indexed OR           → Indexing outcome
rag_index_failed         → Indexing failure with error
link_queued              → Link detected (public or auth-required)
link_downloaded          → Link successfully fetched
```

---

## Chat UX Fixes

Follow `/home/zaks/bookkeeping/docs/CHAT-FRONT-DOOR-PLAN.md` for API contracts and gates.

### 1. Backend Session Persistence
- Endpoint exists: `GET /api/chat/session/{id}` in `deal_lifecycle_api.py:898-925`
- **Problem**: Sessions stored in-memory (`orchestrator.sessions` dict) - lost on restart
- **Fix**: Add SQLite backing to `chat_orchestrator.py`:
  - On session create/update: write to `chat_sessions` + `chat_messages` tables
  - On server start: load active sessions from SQLite
  - On `get_chat_session()`: read from SQLite if not in memory
- Frontend: Call `getChatSession(sessionId)` on page mount before falling back to localStorage

### 2. Freeze Prevention
- Stream rendering batched at 30-60fps (buffer tokens, flush at ~16-33ms intervals)
- Add message virtualization (@tanstack/virtual or similar)
- Async localStorage saves (requestIdleCallback)
- Paginate message history (load last 50, lazy-load older)
- Evidence bundle capped at 40KB chars

### 3. Timing Breakdown Display
- Already have TimingData structure
- UI shows steps/timings per turn: Evidence build → RAG query → LLM → Tool/Proposal
- Debug panel shows: provider chosen, cache hits, warnings, gates triggered

---

## Implementation Phases (Ship Incrementally, No Big-Bang Rewrite)

### Phase A: SQLite Foundation (WAL Mode)
1. Create single SQLite state DB (path configurable via `ZAKOPS_STATE_DB` env)
2. Tables: `runs`, `emails`, `artifacts`, `links`, `timings`, `budgets`, `checkpoints`, `chat_sessions`, `chat_messages`
3. JSON→SQLite migration for existing caches (`email_sync_processed.json`, `downloads_processed.json`)
4. Add run-ledger + per-stage timing helpers
5. Unit tests for state store

### Phase B: Staged Ingestion Pipeline
1. Create `/home/zaks/scripts/email_ingestion/` package with:
   - `pipeline.py` (orchestrator)
   - Stage modules 0-7: preflight/fetch/normalize/match/persist/extract/classify/index
2. Keep `sync_acquisition_emails.py` as thin CLI wrapper calling pipeline
3. Enforce terminal outcomes + audit trail event chain per email
4. Integration tests for pipeline

### Phase C: Rebuild / Dry-Run Mode
1. CLI flags: `--since YYYY-MM-DD`, `--days N`, `--rebuild`, `--dry-run`
2. Rebuild must be idempotent
3. File moves/renames are proposals-by-default (require `--apply` to execute)
4. Dry-run writes proposal plan only (no mutations)

### Phase D: Gemini Worker
1. Create `gemini_worker.py` with provider abstraction
2. Implement gates: secret scan, budget check, timeout
3. Deterministic fallback when gates fail or provider unavailable
4. Strict JSON outputs with confidence/rationale/citations
5. Audit every call to run-ledger

### Phase E: Link Intake Queue
1. URL detection during fetch stage
2. Decision tree: public direct download → bounded fetch; else queue item
3. Queue item includes: URL, vendor, deal candidates, reason, operator instructions
4. Drop-zone workflow:
   - Operator downloads manually
   - Places file in `DataRoom/.intake-dropzone/{url_hash}_{filename}`
   - Scanner ingests with provenance and emits events

### Phase F: RAG Indexing Correctness
1. Remove hard-coded `rel_path` hacks
2. Compute: `rel_path = Path(file).relative_to(DATAROOM_ROOT)`
3. Config-driven URL prefix (`ZAKOPS_RAG_URL_PREFIX`)
4. Bounded indexing (max file size, max chars, timeout)
5. Failures become audited warnings (not silent; not full-run crash unless strict mode)

### Phase G: Chat Reliability
1. Add SQLite persistence to `chat_orchestrator.py`:
   - Sessions/messages tables
   - Restore on server start
   - Read-through cache pattern
2. Frontend fixes:
   - Token batching at 30-60fps
   - Message virtualization/pagination
   - Load session from backend before localStorage fallback
3. Show timing breakdown + debug signals:
   - Provider used, cache hits, warnings, gates triggered, blocked sends

---

## Key Commands (Runbook)

### Normal Operations

```bash
# Run ingestion normally
python3 sync_acquisition_emails.py

# Dry-run (proposal plan only, no mutations)
python3 sync_acquisition_emails.py --dry-run

# Rebuild last 30 days safely
python3 sync_acquisition_emails.py --rebuild --days 30

# Rebuild from specific date
python3 sync_acquisition_emails.py --rebuild --since 2025-01-01

# Apply proposals from dry-run
python3 sync_acquisition_emails.py --rebuild --days 30 --apply
```

### Quarantine Management

```bash
# List pending quarantine items
python3 lifecycle_event_emitter.py quarantine-list

# Resolve quarantine item (link to deal)
python3 lifecycle_event_emitter.py quarantine-resolve QRN-xxx --action link --deal-id DEAL-2025-001

# Resolve quarantine item (discard)
python3 lifecycle_event_emitter.py quarantine-resolve QRN-xxx --action discard
```

### Link Intake Queue

```bash
# Check auth-required links
sqlite3 $ZAKOPS_STATE_DB "SELECT url, vendor, status FROM link_intake_queue WHERE status='auth_required'"

# After operator drops file in intake-dropzone, scanner processes automatically
# Or manually trigger:
python3 -m email_ingestion.workers.link_intake --scan-dropzone
```

### Debugging

```bash
# Check run-ledger for recent runs
tail -20 /home/zaks/logs/run-ledger.jsonl | jq .

# Check state DB for pending emails
sqlite3 $ZAKOPS_STATE_DB "SELECT COUNT(*) FROM processed_emails WHERE status='pending'"

# Check Gemini budget
python3 -c "from email_ingestion.workers.gemini_worker import get_budget; print(get_budget())"

# Preflight validation
make preflight

# Run smoke tests
make ingest-smoke
make chat-smoke
```

---

## Critical Files to Modify

| File | Change |
|------|--------|
| `/home/zaks/scripts/sync_acquisition_emails.py` | Refactor to thin CLI wrapper |
| `/home/zaks/scripts/deal_registry.py` | No changes (integrate with) |
| `/home/zaks/scripts/deal_events.py` | No changes (integrate with) |
| `/home/zaks/scripts/lifecycle_event_emitter.py` | No changes (integrate with) |
| `/home/zaks/scripts/chat_llm_router.py` | Add budget tracking methods |
| `/home/zaks/scripts/chat_orchestrator.py` | Add SQLite session persistence |
| `/home/zaks/scripts/deal_lifecycle_api.py` | No changes (session endpoint exists) |
| `/home/zaks/zakops-dashboard/src/app/chat/page.tsx` | Session loading on mount, virtualization |
| `/home/zaks/zakops-dashboard/src/lib/api.ts` | getChatSession already exists, add error handling |

---

## Tests + Runbook Are Release Gates

**All tests must pass before shipping each phase.**

### Smoke Tests Required

1. **Preflight**: paths, deps, IMAP connectivity, disk space
2. **IMAP fetch**: mockable test with sample emails
3. **Dedup idempotency**: same email twice → 1 event chain (not 2)
4. **Rebuild window**: `--days 30 --rebuild` reprocesses correctly
5. **Link intake**: public URLs fetched, auth URLs queued
6. **Gemini gating**: secret blocks send, budget cap enforced, timeout triggers fallback
7. **RAG paths**: `rel_path` computed correctly from `DATAROOM_ROOT`
8. **Chat session**: refresh preserves history (backend then localStorage)
9. **Chat streaming**: no freeze on long responses (30-60fps batching)
10. **Chat breakdown**: timing visible in debug panel

### Make Targets

```bash
make preflight      # Validate environment before run
make ingest-smoke   # Run ingestion smoke tests
make chat-smoke     # Run chat smoke tests
```

### Definition of Done

A rebuild run over `--days 30` must finish with:
- **0 "pending" emails** in state DB
- **All emails have terminal dispositions** (deal-linked OR quarantined)
- **No silent drops** (run-ledger shows all outcomes)

---

## Known Limitations (To Document)

1. Playwright browser mode for auth links: not implemented - drop zone only
2. Drop zone matching: filename must include url_hash prefix
3. Chat virtualization: may affect search/scroll UX
4. Gemini budget: shared across all pipeline runs
5. SQLite: single-writer constraint (use file locking)
6. Rebuild mode: file moves are proposals only by default

---

## Open Questions / Decisions to Confirm Before Coding

1. **SQLite DB location**: Default `DataRoom/.deal-registry/ingest_state.db` — acceptable?
2. **Canonical URL scheme for RAG**: `https://dataroom.local/DataRoom/<rel_path>` vs `dataroom://<deal_id>/<artifact_id>`?
3. **Junk/unsubscribe policy**: Treat as audited terminal disposition (no quarantine) or always quarantine?
4. **Chat freeze scope**: Confirm it's ZakOps dashboard only (not OpenWebUI)?
5. **Session TTL**: 24 hours default with 6-hour cleanup cron — acceptable?
6. **Evidence bundle limits**: 40KB total, 8KB per source — acceptable?
7. **`--compact` flag**: Should we add explicit retention/compaction CLI flag?

---

## Expected Output (Commit Summary)

Upon completion, deliver:

### Files Changed / New Modules
```
NEW:  /home/zaks/scripts/email_ingestion/
      ├── __init__.py
      ├── pipeline.py
      ├── config.py
      ├── stages/stage_0_preflight.py ... stage_7_index.py
      ├── state/sqlite_store.py, checkpoint.py, migrations.py
      └── workers/gemini_worker.py, link_intake.py

MODIFIED:
      /home/zaks/scripts/sync_acquisition_emails.py (thin wrapper)
      /home/zaks/scripts/chat_orchestrator.py (SQLite session persistence)
      /home/zaks/scripts/chat_llm_router.py (budget tracking)
      /home/zaks/zakops-dashboard/src/app/chat/page.tsx (session loading, virtualization)

NEW DB:
      /home/zaks/DataRoom/.deal-registry/ingest_state.db
```

### Validation Commands
```bash
make preflight      # Environment validation
make ingest-smoke   # Ingestion smoke tests
make chat-smoke     # Chat smoke tests

# Demonstrate rebuild
python3 sync_acquisition_emails.py --rebuild --days 30 --dry-run
# Verify: 0 pending emails, all have terminal dispositions
```

---

## Comparison with Codex Plan

This plan incorporates improvements from `/home/zaks/bookkeeping/docs/ZAKOPS-EMAIL-DATAROOM-INGESTION-CHAT-RELIABILITY-IMPLEMENTATION-PLAN.md`:

| Feature | Added |
|---------|-------|
| Non-Goals section | ✓ |
| Non-negotiable contracts (5 rules) | ✓ |
| `timings` table for per-stage metrics | ✓ |
| `budgets` table for Gemini spend | ✓ |
| Per-email event chain | ✓ |
| Open questions section | ✓ |
| CHAT-FRONT-DOOR-PLAN.md reference | ✓ |
| WAL mode for SQLite | ✓ |
| 30-60fps batching spec | ✓ |
| Phase A-G naming convention | ✓ |
| Tests as release gates | ✓ |
| Definition of Done criteria | ✓ |
