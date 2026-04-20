# Incident Report: Post-Monorepo Consolidation Outage

**Date:** 2026-02-16
**Severity:** P1 — Multiple core features completely non-functional
**Duration:** ~2 hours (from user report to full resolution)
**Triggered by:** MONOREPO-CONSOLIDATION-001 (merge of zakops-backend into monorepo)
**Status:** Resolved

---

## 1. Executive Summary

Following the merge of the standalone `zakops-backend` repository into the monorepo at `apps/backend/`, four separate failures caused a near-total application outage. Users could not delete deals, could not delete quarantine items, could not use the AI chat assistant, and email injection from LangSmith appeared to succeed but items were invisible. The RAG service was also down.

All four issues had distinct root causes, but three of them trace back to a single class of problem: the Docker Compose configuration did not fully account for the new monorepo layout and environment variable interactions.

---

## 2. Impact

| Feature | User Experience |
|---------|----------------|
| Deal delete/archive | "Not Found" error on every attempt |
| Quarantine delete | "Not Found" error on every attempt |
| Quarantine approve/reject | Blocked (503 — "API key not configured") |
| AI Chat | Fallback message: "AI agent service is currently unavailable" |
| LangSmith email injection | Tool call shows success, but items don't appear |
| RAG search | 503 on all requests |

---

## 3. Timeline

| Time (UTC) | Event |
|------------|-------|
| ~00:00 | MONOREPO-CONSOLIDATION-001 completed. All containers reported healthy. |
| ~00:30 | User discovers delete is broken, chat is broken, LangSmith injection fails silently. |
| 02:30 | System audit begins. All 6 containers show healthy status. |
| 02:32 | **Finding 1:** Backend container has 7 routers; disk has 15. Image is stale. |
| 02:35 | **Fix 1:** Backend image rebuilt. Delete endpoints restored. |
| 02:38 | **Finding 2:** Quarantine delete returns 503 — ZAKOPS_API_KEY is empty in container. |
| 02:40 | **Fix 2:** Removed ZAKOPS_API_KEY override from docker-compose.yml. Restarted backend. |
| 02:45 | **Finding 3:** RAG returns 503 — stuck from failed DB connection at boot. |
| 02:45 | **Fix 3:** Restarted RAG container. |
| 02:51 | **Finding 4:** Chat times out at 30s; agent needs ~108s for two vLLM calls. |
| 02:57 | **Fix 4:** Increased AGENT_LOCAL_TIMEOUT from 30s to 180s. Restarted dashboard. |
| 02:58 | All features verified working via Playwright and curl. |

---

## 4. Root Cause Analysis

### Issue 1: Stale Backend Docker Image (CRITICAL)

**Symptom:** All deal delete, quarantine delete, chat, bulk operations, and several other endpoints returned 404 or 405.

**Root cause:** During the monorepo consolidation, the backend Docker image was built from the code that was merged via `git subtree add --squash`. This squash-merged code was a snapshot of the old standalone repo's `main` branch. However, significant development had occurred on the monorepo's `fix/full-remediation-001` branch *after* the subtree merge — adding 8 new routers (`actions.py`, `brain.py`, `chat.py`, `deals_bulk_delete.py`, `onboarding.py`, `preferences.py`, `quarantine_delete.py`, `models/`). The image was never rebuilt after those additions.

**Why it wasn't caught:** The `docker compose up -d` after the merge used the image that was just built from the subtree-merged code. Health checks passed because the `/health/ready` endpoint existed in the old code. The missing routers only manifest when specific endpoints are called.

**Fix:** `docker compose build backend && docker compose up -d backend outbox-worker`

**Evidence:**
- Container `main.py`: ~344 lines, 7 routers
- Disk `main.py`: 635+ lines, 15 routers
- MD5 checksums confirmed completely different files

---

### Issue 2: ZAKOPS_API_KEY Overridden to Empty (CRITICAL)

**Symptom:** All quarantine write operations (delete, approve, reject, inject) returned 503 with message "API key not configured — injection path blocked."

**Root cause:** The `docker-compose.yml` backend service had this line in its `environment:` section:

```yaml
environment:
  ZAKOPS_API_KEY: ${ZAKOPS_API_KEY:-}
```

Docker Compose `environment:` values **override** values from `env_file:`. The host machine does not have `ZAKOPS_API_KEY` set as a shell environment variable. The `:-` default means "empty string if unset." So the container received `ZAKOPS_API_KEY=""`, overriding the valid key in `apps/backend/.env`.

The backend's `APIKeyMiddleware` uses a fail-closed pattern: if `ZAKOPS_API_KEY` is empty/falsy, all write requests to `/api/quarantine*` paths are blocked with 503.

**Why it wasn't caught:** This is the same class of bug that affected `JWT_SECRET_KEY` during the consolidation itself (which was caught and fixed). The `ZAKOPS_API_KEY` line was added to docker-compose.yml as part of making environment variables documentable (since `.env.example` was blocked by deny rules), but the empty default wasn't recognized as destructive.

**Fix:** Removed the `ZAKOPS_API_KEY` line from the `environment:` section entirely. The value is correctly set in `apps/backend/.env` which is loaded via `env_file:`.

**Lesson:** Never put secrets in docker-compose.yml `environment:` section with empty defaults. If the host doesn't have the var, it silently overrides the `.env` file value with empty.

---

### Issue 3: Chat Timeout Too Short (HIGH)

**Symptom:** User sends a chat message. After ~30 seconds, the UI shows a canned fallback response: "AI agent service is currently unavailable. Showing helpful guidance instead."

**Root cause:** The dashboard's `LocalProvider` (in `src/lib/agent/providers/local.ts`) uses an `AbortController` with a timeout of 30 seconds (configured via `AGENT_LOCAL_TIMEOUT` in `.env.local`). The AI agent, running Qwen 2.5 32B-Instruct-AWQ on local vLLM, requires approximately 50-60 seconds per LLM call. A tool-using conversation requires two LLM calls (first to decide which tool to call, second to format the response), totaling ~108 seconds.

The dashboard aborts the request at 30s and renders a fallback. Meanwhile, the agent continues processing in the background and successfully completes — but the result is discarded.

**Why it wasn't caught:** The timeout was set during initial development when the model was faster or simpler prompts were used. The agent's system prompt grew significantly (M&A domain context, tool routing rules, grounding rules) adding token count. The 30s timeout was never revisited.

**Fix:** Increased `AGENT_LOCAL_TIMEOUT` from `30000` to `180000` (3 minutes) in `apps/dashboard/.env.local`. Restarted dashboard.

**Verification:** After fix, chat returned "We currently have 9 deals in our pipeline, all in the inbound stage" with Source: DB — confirming the agent called `list_deals` and returned real data.

---

### Issue 4: RAG Service Stuck (MEDIUM)

**Symptom:** All RAG API requests returned 503.

**Root cause:** The RAG service (`rag-rest-api` in `Zaks-llm`) tried to connect to its database at startup. The database was still starting up (post-consolidation restart). The connection failed and the service entered a permanent 503 state with no retry logic.

**Fix:** `docker compose restart rag-rest-api` in the Zaks-llm stack.

---

## 5. What Was Fixed

| File | Change |
|------|--------|
| `docker-compose.yml` | Removed `ZAKOPS_API_KEY: ${ZAKOPS_API_KEY:-}` from backend `environment:` section |
| `apps/dashboard/.env.local` | `AGENT_LOCAL_TIMEOUT`: 30000 → 180000 |
| Backend Docker image | Rebuilt to include all 15 routers from current branch |
| RAG container | Restarted |

---

## 6. Verification

Every fix was verified end-to-end using Playwright browser automation and direct curl/API calls:

| Test | Method | Result |
|------|--------|--------|
| Deal delete (DL-0104) | Playwright click → toast | "Deal deleted (archived)" |
| Quarantine delete | Playwright click → toast | "Removed from quarantine", count 6→5 |
| Quarantine injection | curl POST /api/quarantine | 201 Created, visible in UI |
| Chat "How many deals?" | Playwright type+submit → wait | "9 deals, all inbound" (Source: DB) |
| RAG health | curl /stats | 3486 chunks, 122 URLs |
| All 9 pages load | Playwright navigate | Dashboard, Deals, Actions, Quarantine, Chat, Agent Activity, Onboarding, Settings, Operator HQ |

---

## 7. Lessons Learned

1. **Always rebuild Docker images after code changes.** Health checks passing does not mean the image has current code. Add an image rebuild step to any merge/migration checklist.

2. **Docker Compose `environment:` overrides `env_file:`.** This is by design but extremely easy to forget. Sensitive values that come from `.env` should never appear in the `environment:` section with empty defaults. This same bug class hit twice in 24 hours (JWT_SECRET_KEY, then ZAKOPS_API_KEY).

3. **Timeouts must match real-world latency.** A 32B parameter model with 8 tools and a large system prompt takes ~108 seconds for a tool-using conversation. The 30-second timeout was set during development and never updated as the agent grew in complexity.

4. **Services without DB retry logic will silently die.** The RAG service connected to its DB once at startup. If the DB isn't ready, the service enters a permanent failure state. Services should retry DB connections or have a recovery path.

---

## 8. Non-Fatal Issues (Monitoring)

These were observed during the audit but are not blocking:

| Issue | Location | Impact |
|-------|----------|--------|
| `ForeignKeyViolation` on `cost_ledger_2026_02` | agent-api `cost_repository.py` | Background task fails silently; cost tracking not recorded for some threads |
| `snapshot_write_failed` — can't import `get_db_pool` | agent-api `snapshot_writer.py` | Chat snapshots not persisted; conversation history may be incomplete |
| 34 uncommitted files on `fix/full-remediation-001` | monorepo git | All consolidation changes are uncommitted; risk of accidental loss |

---

## 9. Preventive Actions

| Action | Owner | Status |
|--------|-------|--------|
| Add `docker compose build` as mandatory step in merge checklists | Ops | Recommended |
| Audit all docker-compose.yml `environment:` entries for empty-default overrides | Ops | Recommended |
| Add smoke test script that hits all critical endpoints after deploy | Ops | Recommended |
| Commit the 34 uncommitted files on fix/full-remediation-001 | Dev | Pending |
| Investigate cost_ledger FK violation and snapshot_writer import error | Dev | Pending |
