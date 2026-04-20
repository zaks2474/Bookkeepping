# Performance Baselines — DEAL-INTEGRITY-UNIFIED Layer 5

## Timestamp
2026-02-08T22:52:00Z

## Database: zakops (49 total rows)

### Pipeline Summary Query
```sql
SELECT stage, count(*) FROM zakops.deals
WHERE deleted = false AND status = 'active' GROUP BY stage;
```

**Execution Plan:**
- GroupAggregate (quicksort, Memory: 26kB)
- Seq Scan (Filter: NOT deleted AND status='active')
- Rows Removed by Filter: 18
- **Planning Time: 1.024 ms**
- **Execution Time: 0.228 ms**

### Deals Listing Query
```sql
SELECT * FROM zakops.deals
WHERE deleted = false AND status = 'active'
ORDER BY updated_at DESC LIMIT 50;
```

**Execution Plan:**
- Limit + Sort (quicksort, Memory: 31kB)
- Seq Scan (Filter: NOT deleted AND status='active')
- Rows Removed by Filter: 18
- **Planning Time: 0.985 ms**
- **Execution Time: 0.109 ms**

### API Response Times
| Endpoint | Response Time | Status |
|----------|--------------|--------|
| GET /api/pipeline/summary | 1ms (x-response-time header) | 200 |
| GET /api/deals?status=active | ~4ms | 200 |
| GET /health | ~2ms | 200 |

## Indexes Verified (L5-9)

| Index Name | Columns | Purpose |
|------------|---------|---------|
| `idx_deals_lifecycle` | `(deleted, status, stage)` | Primary composite index for pipeline summary view |
| `idx_deals_status` | `(status)` | Fast status filtering |
| `idx_deals_stage` | `(stage)` | Fast stage filtering |
| `idx_deals_updated_at` | `(updated_at DESC)` | Sort ordering for deals list |
| `idx_deals_cursor_pagination` | `(updated_at DESC, deal_id DESC)` | Cursor-based pagination |
| `idx_deals_created_at` | `(created_at DESC)` | Time-based queries |
| `idx_deals_canonical_name` | `(canonical_name)` | Name lookups |
| `deals_canonical_name_unique` | `(canonical_name)` UNIQUE | Duplicate prevention |
| `deals_pkey` | `(deal_id)` UNIQUE | Primary key |

**Total: 9 indexes on deals table — all critical patterns covered.**

## Note on Sequential Scans
The deals table has 49 rows. At this size, Postgres correctly chooses sequential scan over index scan (cheaper for small tables). The `idx_deals_lifecycle` index will become effective as the table grows beyond ~100-200 rows.
