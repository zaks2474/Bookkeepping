# E05 — Shadow-Mode Isolation Controls

**Evidence ID:** E05
**Date:** 2026-02-13
**Auditor:** Claude Opus 4.6
**Verdict:** PASS

---

## 1. Backend API — `source_type` Query Parameter + SQL Filtering

**File:** `/home/zaks/zakops-backend/src/api/orchestration/main.py`

### Endpoint declaration (lines 1394-1401)

```python
@app.get("/api/quarantine", response_model=list[QuarantineResponse])
async def list_quarantine(
    status: str | None = Query("pending", description="Filter by status"),
    classification: str | None = Query(None, description="Filter by classification"),
    source_type: str | None = Query(None, description="Filter by source_type (e.g. email, langsmith_shadow)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    pool: asyncpg.Pool = Depends(get_db)
):
```

- Line 1398: `source_type` declared as optional `Query` parameter with explicit description mentioning `langsmith_shadow`.

### SQL condition injection (lines 1418-1421)

```python
if source_type:
    conditions.append(f"q.source_type = ${param_idx}")
    params.append(source_type)
    param_idx += 1
```

- Line 1419: Parameterized SQL (`$N` placeholder) — prevents injection.
- Line 1420: Value bound via `params.append`, not string interpolation.

### WHERE clause assembly (lines 1423-1445)

```python
where_clause = " AND ".join(conditions) if conditions else "TRUE"

query = f"""
    SELECT ...
    FROM zakops.quarantine_items q
    LEFT JOIN zakops.sender_profiles sp ON q.sender = sp.email
    WHERE {where_clause}
    ...
"""
```

- Line 1423: Conditions joined with `AND` — `source_type` filter composes correctly with `status` and `classification` filters.
- Line 1445: WHERE clause applied to `quarantine_items` table — only rows matching `source_type` are returned.

**Isolation guarantee:** When `source_type=langsmith_shadow` is passed, the SQL returns ONLY quarantine items with that source type. Email-origin items (`source_type='email_sync'`) are excluded at the database level.

---

## 2. Dashboard — State, Dropdown, and Fetch Integration

**File:** `/home/zaks/zakops-agent-api/apps/dashboard/src/app/quarantine/page.tsx`

### State declaration (line 78)

```tsx
const [sourceTypeFilter, setSourceTypeFilter] = useState<string>('');
```

- Default is `''` (empty string) = "All sources" — no filter applied on initial load.

### Fetch integration (lines 80-88)

```tsx
const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const itemsData = await getQuarantineQueue({
        limit: 200,
        offset: 0,
        source_type: sourceTypeFilter || undefined,
      });
```

- Line 87: `sourceTypeFilter || undefined` — empty string becomes `undefined` (omitted from request); non-empty values (e.g. `'langsmith_shadow'`) are passed through.

### useEffect reactive trigger (lines 98-100)

```tsx
useEffect(() => {
    fetchData();
}, [sourceTypeFilter]);
```

- Line 100: `sourceTypeFilter` in dependency array — changing the dropdown immediately re-fetches with the new filter value.

### Dropdown UI (lines 318-329)

```tsx
<select
  value={sourceTypeFilter}
  onChange={(e) => setSourceTypeFilter(e.target.value)}
  className='h-9 rounded-md border ...'
  disabled={loading}
>
  <option value=''>All sources</option>
  <option value='email_sync'>Email sync</option>
  <option value='langsmith_shadow'>LangSmith shadow</option>
  <option value='langsmith_live'>LangSmith live</option>
  <option value='manual'>Manual</option>
</select>
```

- Line 326: `langsmith_shadow` is an explicit dropdown option — operators can isolate shadow-mode items with one click.
- Line 324: `''` = "All sources" shows everything (no isolation).
- Line 322: Dropdown is disabled while loading — prevents race conditions from rapid selection changes.

---

## 3. Next.js Route Handler — `source_type` Forwarding

**File:** `/home/zaks/zakops-agent-api/apps/dashboard/src/app/api/actions/quarantine/route.ts`

### Parameter extraction (lines 12-15)

```typescript
const { searchParams } = new URL(request.url);
const limit = searchParams.get('limit');
const offset = searchParams.get('offset');
const sourceType = searchParams.get('source_type');
```

- Line 15: `source_type` extracted from incoming request query string.

### Forwarding to backend (lines 18-27)

```typescript
let queryString = '';
if (limit || offset || sourceType) {
  const params = new URLSearchParams();
  if (limit) params.set('limit', limit);
  if (offset) params.set('offset', offset);
  if (sourceType) params.set('source_type', sourceType);
  queryString = '?' + params.toString();
}

const response = await backendFetch(`/api/quarantine${queryString}`);
```

- Line 23: `source_type` forwarded to backend via `URLSearchParams` — safe encoding, no injection risk.
- Line 27: Backend `/api/quarantine` endpoint called with the forwarded parameter.

### Response passthrough (line 50)

```typescript
source_type: item.source_type,
```

- `source_type` is preserved in the response transformation so the frontend can display which source produced each item.

---

## 4. API Client — `getQuarantineQueue` with `source_type`

**File:** `/home/zaks/zakops-agent-api/apps/dashboard/src/lib/api.ts`

### Function signature (lines 839-843)

```typescript
export async function getQuarantineQueue(params?: {
  limit?: number;
  offset?: number;
  source_type?: string;
}): Promise<QuarantineItem[]> {
```

### Parameter serialization (lines 845-850)

```typescript
const searchParams = new URLSearchParams();
if (params?.limit != null) searchParams.set('limit', String(params.limit));
if (params?.offset != null) searchParams.set('offset', String(params.offset));
if (params?.source_type) searchParams.set('source_type', params.source_type);
const query = searchParams.toString();
const endpoint = `/api/actions/quarantine${query ? `?${query}` : ''}`;
```

- Line 848: `source_type` included in query string only when truthy — matches the `|| undefined` guard in the page component.

### Schema includes source_type (line 192)

```typescript
source_type: z.string().nullable().optional(),
```

- Zod schema validates `source_type` as part of `QuarantineItemSchema` — type-safe end-to-end.

---

## 5. Data Flow Summary

```
Dropdown (page.tsx:320)
  → sourceTypeFilter state (page.tsx:78)
  → fetchData (page.tsx:87) passes source_type to getQuarantineQueue
  → getQuarantineQueue (api.ts:848) serializes to ?source_type=langsmith_shadow
  → Next.js route handler (route.ts:23) forwards to backend
  → Backend (main.py:1419) injects q.source_type = $N into SQL WHERE
  → PostgreSQL returns ONLY matching rows
  → Response flows back with source_type preserved at every layer
```

**Isolation is enforced at the database level** (parameterized SQL in the backend). The dashboard, route handler, and API client are pass-through layers that faithfully propagate the filter value.

---

## Verdict: PASS

All four layers (backend SQL, Next.js route handler, API client, dashboard UI) implement `source_type` filtering consistently. Shadow-mode items (`langsmith_shadow`) can be isolated from production email items (`email_sync`) with a single dropdown selection. The filter is parameterized at the SQL level, preventing injection. The `useEffect` dependency ensures immediate re-fetch on filter change.
