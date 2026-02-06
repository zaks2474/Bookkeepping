# Behavioral Migration Map: deal_tools.py .get() -> Typed Access

Generated: 2026-02-06T20:35:00Z
Source: apps/agent-api/app/core/langgraph/tools/deal_tools.py (39 .get() patterns)
Target Models: app/schemas/backend_models.py (DealResponse, etc.)

## Categories

### Category 1: ContextVar .get() - NOT BACKEND RESPONSE (Skip)
| Line | Pattern | Action |
|------|---------|--------|
| 50 | `_correlation_id_ctx.get()` | SKIP - ContextVar, not backend response |

### Category 2: HTTP Client .get() - METHOD CALL (Skip)
| Line | Pattern | Action |
|------|---------|--------|
| 230 | `client.get(f"{DEAL_API_URL}/api/deals/{deal_id}")` | SKIP - HTTP method |
| 314 | `client.get(f"{DEAL_API_URL}/api/deals/{deal_id}")` | SKIP - HTTP method |
| 403 | `client.get(f"{DEAL_API_URL}/api/deals/{deal_id}")` | SKIP - HTTP method |
| 477 | `client.get(f"{DEAL_API_URL}/api/deals")` | SKIP - HTTP method |
| 561 | `client.get(f"{DEAL_API_URL}/api/deals")` | SKIP - HTTP method |
| 617 | `client.get(f"{DEAL_API_URL}/api/deals")` | SKIP - HTTP method |

### Category 3: Single Deal Response Parsing - MIGRATE TO DealResponse
| Line | Pattern | Generated Model Field | Required? | Migration |
|------|---------|----------------------|-----------|-----------|
| 239 | `deal_data.get("stage", "unknown")` | `DealResponse.stage: str` | YES | `.stage` |
| 240 | `deal_data.get("updated_at", "")` | `DealResponse.updated_at: datetime` | YES | `.updated_at` |
| 324 | `verify_data.get("stage", "unknown")` | `DealResponse.stage: str` | YES | `.stage` |
| 325 | `verify_data.get("updated_at", "")` | `DealResponse.updated_at: datetime` | YES | `.updated_at` |
| 792 | `deal_data.get("deal_id", "unknown")` | `DealResponse.deal_id: str` | YES | `.deal_id` |
| 979 | `deal_data.get("stage", "inbound")` | `DealResponse.stage: str` | YES | `.stage` |
| 980 | `deal_data.get("created_at")` | `DealResponse.created_at: datetime` | YES | `.created_at` |
| 981 | `deal_data.get("updated_at")` | `DealResponse.updated_at: datetime` | YES | `.updated_at` |
| 982 | `deal_data.get("stage_changed_at")` | NOT IN DealResponse | N/A | INVESTIGATE |
| 983 | `deal_data.get("canonical_name", "")` | `DealResponse.canonical_name: str` | YES | `.canonical_name` |

### Category 4: List Response Wrapper Parsing - CREATE DealsListResponse
| Line | Pattern | Generated Model | Migration |
|------|---------|-----------------|-----------|
| 488 | `deals.get("deals", deals.get("results", []))` | Need custom wrapper | Use typed helper |
| 571 | `data.get("deals", data.get("results", []))` | Need custom wrapper | Use typed helper |
| 572 | `data.get("total", len(data.get("deals", [])))` | Need custom wrapper | Use typed helper |
| 627 | `all_deals.get("deals", all_deals.get("results", []))` | Need custom wrapper | Use typed helper |

### Category 5: Deal Field Access in List Iteration - MIGRATE TO DealResponse
| Line | Pattern | Generated Model Field | Required? | Migration |
|------|---------|----------------------|-----------|-----------|
| 496 | `d.get("stage", "unknown")` | `DealResponse.stage: str` | YES | `.stage` |
| 635 | `deal.get("canonical_name", "")` | `DealResponse.canonical_name: str` | YES | `.canonical_name` |
| 636 | `deal.get("display_name", "")` | `DealResponse.display_name: Optional[str]` | NO | `.display_name or ""` |
| 637 | `deal.get("deal_id", "")` | `DealResponse.deal_id: str` | YES | `.deal_id` |
| 638 | `deal.get("broker", {}).get("name", "")` | `DealResponse.broker: Dict[str, Any]` | YES | `.broker.get("name", "")` |
| 639 | `deal.get("stage", "")` | `DealResponse.stage: str` | YES | `.stage` |

### Category 6: Event/Result Response Parsing - SEPARATE MODELS NEEDED
| Line | Pattern | Notes |
|------|---------|-------|
| 893 | `result.get("event_id")` | Create event response, DealEvent model exists |
| 899 | `result.get("event_id")` | Create event response, DealEvent model exists |

## Missing From Generated Models

1. **stage_changed_at** - Line 982 uses this but DealResponse doesn't have it
   - **Action**: Check if backend returns this field. If yes, update OpenAPI spec.
   
2. **DealsListResponse wrapper** - Backend returns `{"deals": [...]}` or `{"results": [...]}`
   - **Action**: Create typed wrapper: `class DealsListResponse(BaseModel): deals: List[DealResponse]; total: Optional[int]`

## Migration Strategy

### Phase 1: Create BackendClient with typed methods
```python
class BackendClient:
    async def get_deal(self, deal_id: str) -> DealResponse:
        response = await self._get(f"/api/deals/{deal_id}")
        return DealResponse.model_validate(response.json())
    
    async def list_deals(self, **params) -> List[DealResponse]:
        response = await self._get("/api/deals", params=params)
        data = response.json()
        deals = data.get("deals", data.get("results", data))
        return [DealResponse.model_validate(d) for d in deals]
```

### Phase 2: Refactor tool functions
Replace raw dict access with typed model access.

## Verdict: 37 .get() patterns
- Skip (ContextVar): 1
- Skip (HTTP method): 6  
- Migrate to typed access: 30
  - Single deal (DealResponse): 16
  - List wrapper: 8
  - Event response: 2
  - Need schema investigation: 4 (stage_changed_at)
