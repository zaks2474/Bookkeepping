# E07 — Deal Truth from PostgreSQL (No Split-Brain)

**Date:** 2026-02-13
**Auditor:** Claude Opus 4.6
**Verdict:** PASS

---

## 1. BackendClient Methods (HTTP to Backend)

**File:** `/home/zaks/zakops-agent-api/apps/agent-api/app/services/backend_client.py`

### `get_deal()` — Line 93

```python
async def get_deal(self, deal_id: str) -> DealResponse:
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.get(
            f"{self.base_url}/api/deals/{deal_id}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return DealResponse.model_validate(response.json())
```

- **HTTP endpoint:** `GET {base_url}/api/deals/{deal_id}`
- **Returns:** `DealResponse` (Pydantic-validated)
- **Backend base_url default:** `http://host.docker.internal:8091` (the FastAPI backend on port 8091, which reads from PostgreSQL `zakops` database)

### `list_deals()` — Line 122

```python
async def list_deals(
    self,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None,
) -> DealsListResponse:
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.get(
            f"{self.base_url}/api/deals",
            headers=self._headers(),
            params=params,
        )
        response.raise_for_status()
        deals = [DealResponse.model_validate(d) for d in deals_raw]
        return DealsListResponse(deals=deals, total=total)
```

- **HTTP endpoint:** `GET {base_url}/api/deals`
- **Query params:** `stage`, `status`, `limit`
- **Returns:** `DealsListResponse` (list of `DealResponse` models)

### Other deal-related methods

| Method | Line | HTTP Endpoint | Returns |
|--------|------|---------------|---------|
| `transition_deal()` | 177 | `POST /api/deals/{deal_id}/transition` | `TransitionResponse` |
| `create_deal()` | 218 | `POST /api/deals` | `DealResponse` |
| `get_deal_events()` | 244 | `GET /api/deals/{deal_id}/events` | `List[DealEvent]` |
| `add_note()` | 280 | `POST /api/deals/{deal_id}/notes` | `AddNoteResponse` |

All methods use `httpx.AsyncClient` to make HTTP requests to the Backend API (port 8091), which queries PostgreSQL. No method reads from filesystem, local cache, or any other data store.

---

## 2. Deal Tools Using BackendClient

**File:** `/home/zaks/zakops-agent-api/apps/agent-api/app/core/langgraph/tools/deal_tools.py`

Every agent tool obtains a `BackendClient` instance via `_get_client()` (line 61) and calls typed methods:

| Tool Function | Line | BackendClient Call(s) | Line(s) of Call |
|---------------|------|-----------------------|-----------------|
| `transition_deal` | 206 | `client.get_deal(deal_id)` (pre-fetch ground truth) | 254 |
| | | `client.transition_deal(deal_id, ...)` (state change) | 312 |
| | | `client.get_deal(deal_id)` (No-Illusions verification) | 333 |
| `get_deal` | 410 | `client.get_deal(deal_id)` | 427 |
| `list_deals` | 456 | `client.list_deals(stage, status, limit)` | 500 |
| `search_deals` | 573 | `client.list_deals()` (fetch all, filter client-side) | 601 |
| `create_deal` | 681 | `client.create_deal(deal_create)` | 759 |
| `add_note` | 813 | `client.add_note(deal_id, content, category, ...)` | 851 |
| `get_deal_health` | 1089 | `client.get_deal(deal_id)` | 1111 |

**Total `client.get_deal()` calls:** 5 (lines 254, 333, 427, 1111, plus docstring example at backend_client.py:62)
**Total `client.list_deals()` calls:** 2 (lines 500, 601)

---

## 3. Negative Evidence: Zero Filesystem Deal-State Reads

### Searches performed

| Search Pattern | Scope | Matches |
|----------------|-------|---------|
| `.deal-registry`, `DealRegistry`, `deal_registry` | `apps/agent-api/app/` | **0 matches** |
| `open(.*deal`, `read.*deal.*file`, `deal.*.json/csv/yaml` | `apps/agent-api/app/` | **0 matches** (2 hits were `DealResponse.model_validate(response.json())` -- parsing HTTP response JSON, not file reads) |
| `deal.*(state\|cache\|store\|registry\|sqlite\|local)` | `apps/agent-api/app/` | **0 filesystem matches** (7 hits were code comments, metadata dict keys, and the `transition_deal_state` backend FSM reference -- none involve local storage) |

**Conclusion:** There is no filesystem-based deal state, no local SQLite cache, no JSON file store, no deal registry, and no in-memory deal cache anywhere in the agent-api codebase. Every deal read flows through `BackendClient` over HTTP.

---

## 4. Data Flow Diagram

```
+-------------------+     +------------------+     +-------+     +---------+     +------------+
| LangGraph Agent   | --> | Deal Tool        | --> | Back- | --> | Backend | --> | PostgreSQL |
| (tool invocation) |     | (deal_tools.py)  |     | end   |     | FastAPI |     | zakops DB  |
|                   |     |                  |     | Client|     | :8091   |     | :5432      |
+-------------------+     +------------------+     +-------+     +---------+     +------------+
                                  |                    |
                                  |  _get_client()     |  httpx.AsyncClient
                                  |  line 61           |  GET/POST /api/deals/*
                                  +--------------------+
```

**Single path for all deal data:**

1. **Agent Tool** (`deal_tools.py`) calls `_get_client()` to obtain a `BackendClient` instance
2. **BackendClient** (`backend_client.py`) makes HTTP requests via `httpx.AsyncClient` to `{base_url}/api/deals/*`
3. **Backend FastAPI** (port 8091) receives the request and queries **PostgreSQL** (`zakops` database, `zakops` schema)
4. **Response** flows back through the same chain, validated into Pydantic models (`DealResponse`) at every layer

There is no secondary path. No filesystem reads, no local caches, no embedded databases, no in-memory stores. The agent and the dashboard share the exact same data source (confirmed by metadata in `list_deals` response: `"provenance": "Same data source as dashboard"` at line 527).

---

## 5. Architectural Safeguards Against Split-Brain

1. **Non-Negotiable Rule** (CLAUDE.md): "NEVER use raw HTTP in Agent tools -- use BackendClient." This forces all deal access through the typed SDK.
2. **No-Illusions Gate** (F-003 RT-1): `transition_deal` re-fetches deal state after mutation to verify the change actually persisted in PostgreSQL (lines 331-361).
3. **Ground Truth Fetch** (F-003 RT-2): `transition_deal` fetches the actual current stage from the backend before acting -- the LLM's `from_stage` claim is treated as advisory only (lines 252-272).
4. **System Prompt Instruction** (`system.md` line 75): "NEVER rely on previous conversation context for deal state -- deals change. Always fetch fresh data."
5. **Module Docstring** (deal_tools.py line 14): "Refactored to use typed BackendClient. All raw httpx calls replaced with BackendClient methods."

---

## Verdict

**PASS** -- All deal state reads in the agent-api flow exclusively through `BackendClient` HTTP calls to the Backend FastAPI service (port 8091), which reads from PostgreSQL. There are zero filesystem deal-state reads, zero local caches, and zero alternative data stores. Split-brain is architecturally impossible.
