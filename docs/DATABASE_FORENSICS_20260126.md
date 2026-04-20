# Database State Forensics Report
**Date**: 2026-01-26
**Investigator**: Claude Opus 4.5
**Objective**: Identify why deals exist in the system despite a claimed "virgin reset"

---

## Executive Summary

A forensic investigation revealed that **two separate backend services** were running simultaneously on different ports, each with their own data storage. The Docker-based reset only cleared the PostgreSQL database, while a **native Python service** running on the host continued to serve data from **JSON files on the local filesystem**.

| Finding | Detail |
|---------|--------|
| **Root Cause** | Native service on port 8090 using filesystem JSON, not affected by Docker volume reset |
| **Deals Found** | 5 deals in `/home/zaks/DataRoom/.deal-registry/deal_registry.json` |
| **Dashboard Config** | Points to port 8090 (native service), not 8091 (Docker service) |
| **Data NOT Wiped** | JSON files, SQLite databases in `/home/zaks/DataRoom/` |

---

## Phase 1: Infrastructure Enumeration

### 1.1 Docker Volumes Discovered

```
DRIVER    VOLUME NAME
local     agent-api_agent-postgres-data
local     crawl4ai-rag_postgres_data
local     docker_postgres-data
local     docker_prometheus-data
local     docker_redis-data
local     open-webui
local     zakops_postgres_data
local     zakops_redis_data
local     zaks-llm_chroma-data
local     zaks-llm_mcp-browser-use-data
local     zaks-llm_open-webui
local     zaks_chroma-data
local     zaks_open-webui
```

### 1.2 Database Containers Running

| Container | Port Mapping | Purpose |
|-----------|--------------|---------|
| `zakops-agent-db` | 5432 (internal) | Agent API PostgreSQL |
| `rag-db` | 5434 → 5432 | RAG Vector Database |
| `zakops-postgres-1` | 5432 → 5432 | Backend PostgreSQL |
| `zakops-redis-1` | 6379 → 6379 | Redis Cache |

### 1.3 Filesystem Data Locations

```
/home/zaks/DataRoom/.deal-registry/
├── deal_registry.json          ← 5 DEALS HERE (NOT WIPED)
├── quarantine.json             ← Quarantine items
├── deferred_actions.json       ← Scheduled actions
├── ingest_state.db             ← SQLite (2.5MB)
├── email_backfill_state.db     ← Email state
├── email_triage_state.db       ← Triage state
├── link_intake_queue.json      ← Link queue
├── case_files/                 ← Deal case files
├── events/                     ← Deal events
└── backups/                    ← Registry backups
```

---

## Phase 2: Database Query Results

### 2.1 Backend PostgreSQL (zakops-postgres-1:5432)

```sql
SELECT COUNT(*) FROM zakops.deals;
```
**Result**: `0` deals ✓ (Successfully wiped)

### 2.2 RAG PostgreSQL (rag-db:5434)

```sql
\dt
```
**Result**: No relations found ✓ (Successfully wiped)

### 2.3 Agent API PostgreSQL (zakops-agent-db)

**Credentials**: `agent` / `agent_secure_pass_123` / `zakops_agent`

**Tables Found**:
```
public.approvals
public.audit_log
public.checkpoint_blobs
public.checkpoint_migrations
public.checkpoint_writes
public.checkpoints
public.session
public.tool_executions
public.user
```
**Result**: No deals table (different schema) ✓

### 2.4 Filesystem JSON (NOT in Docker)

```bash
cat /home/zaks/DataRoom/.deal-registry/deal_registry.json | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'Deals: {len(d.get(\"deals\", {}))}')"
```
**Result**: `5 deals` ✗ (NOT WIPED)

---

## Phase 3: Service Connection Tracing

### 3.1 Dashboard Environment Variables

```bash
docker exec docker-dashboard-1 env | grep -i "NEXT\|API"
```

**Result**:
```
NEXT_PUBLIC_API_URL=http://localhost:8090      ← POINTS TO NATIVE SERVICE
NEXT_PUBLIC_AGENT_API_URL=http://localhost:8095
```

### 3.2 Agent API Environment Variables

```bash
docker exec zakops-agent-api env | grep -iE "DB|DATABASE|POSTGRES|RAG|BACKEND"
```

**Result**:
```
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=zakops_agent
POSTGRES_USER=agent
POSTGRES_PASSWORD=agent_secure_pass_123
RAG_REST_URL=http://host.docker.internal:8052
```

---

## Phase 4: API Endpoint Testing

### 4.1 Port 8090 (Native Service)

```bash
curl -s http://localhost:8090/api/deals
```

**Result**:
```json
{
  "count": 5,
  "deals": [
    {"deal_id": "DEAL-2026-001", "canonical_name": "Acquisition Opportunities", ...},
    {"deal_id": "DEAL-2026-002", "canonical_name": "Profitable IT Services Company", ...},
    {"deal_id": "DEAL-2026-003", "canonical_name": "Textile Art Education Business", ...},
    ...
  ]
}
```
**5 DEALS FOUND** ✗

### 4.2 Port 8091 (Docker Service)

```bash
curl -s http://localhost:8091/api/deals
```

**Result**:
```json
[]
```
**0 DEALS** ✓

### 4.3 RAG Stats (Port 8052)

```bash
curl -s http://localhost:8052/rag/stats
```

**Result**:
```json
{
  "total_chunks": 0,
  "unique_urls": 0,
  "embedding_model": "bge-m3",
  "embedding_dim": 1024
}
```
**0 CHUNKS** ✓

---

## Phase 5: Root Cause Identification

### 5.1 What is on Port 8090?

```bash
ss -tlnp | grep 8090
```

**Result**:
```
LISTEN  0  2048  127.0.0.1:8090  0.0.0.0:*  users:(("python3",pid=107095,fd=6))
```

**This is a NATIVE PROCESS, not a Docker container!**

### 5.2 Process Details

```bash
ps aux | grep 107095
```

**Result**:
```
zaks  107095  0.1  0.3 894780 125980 ?  Ssl  Jan16  20:39
  /usr/bin/python3 /home/zaks/scripts/deal_lifecycle_api.py --host 127.0.0.1 --port 8090
```

| Property | Value |
|----------|-------|
| **PID** | 107095 |
| **Started** | January 16, 2026 |
| **Running Time** | 20+ hours |
| **Script** | `/home/zaks/scripts/deal_lifecycle_api.py` |
| **Working Directory** | `/home/zaks/scripts` |
| **Bind Address** | 127.0.0.1:8090 |

### 5.3 Data Source in Native Service

```python
# From /home/zaks/scripts/deal_lifecycle_api.py:
db_path = os.getenv("ZAKOPS_STATE_DB", "/home/zaks/DataRoom/.deal-registry/ingest_state.db")
```

The native service reads deals from:
- **JSON**: `/home/zaks/DataRoom/.deal-registry/deal_registry.json`
- **SQLite**: `/home/zaks/DataRoom/.deal-registry/ingest_state.db`

---

## Final Forensics Table

### Service Mapping

| Service | Port | Type | Database | Deals | Reset? |
|---------|------|------|----------|-------|--------|
| Native `deal_lifecycle_api.py` | **8090** | Host Process | JSON + SQLite | **5** | **NO** |
| Docker `zakops-backend-1` | 8091 | Container | PostgreSQL | 0 | YES |
| Docker `zakops-agent-api` | 8095 | Container | PostgreSQL | N/A | YES |
| Docker `rag-rest-api` | 8052 | Container | PostgreSQL | 0 chunks | YES |

### Data Flow Diagram

```
┌─────────────────┐     ┌──────────────────────────────────────────┐
│    Dashboard    │     │           HOST FILESYSTEM                │
│  (Port 3003)    │     │  /home/zaks/DataRoom/.deal-registry/     │
└────────┬────────┘     │  ├── deal_registry.json  ← 5 DEALS       │
         │              │  ├── quarantine.json                     │
         │ NEXT_PUBLIC_ │  ├── ingest_state.db                     │
         │ API_URL      │  └── ...                                 │
         ▼              └──────────────────────────────────────────┘
┌─────────────────┐                      ▲
│  Native Python  │                      │ reads
│  (Port 8090)    │──────────────────────┘
│  PID: 107095    │
└─────────────────┘

         ╳ NOT CONNECTED

┌─────────────────┐     ┌──────────────────────────────────────────┐
│ Docker Backend  │     │         DOCKER VOLUMES                   │
│  (Port 8091)    │────▶│  zakops_postgres_data  ← 0 DEALS (WIPED) │
└─────────────────┘     └──────────────────────────────────────────┘
```

### Why Reset Failed

| What Was Reset | What Was NOT Reset |
|----------------|-------------------|
| Docker volumes (`zakops_postgres_data`) | Filesystem JSON files |
| PostgreSQL databases | SQLite databases |
| RAG vector store | Native Python service |
| Redis cache | `/home/zaks/DataRoom/` directory |

---

## Remediation Steps

To achieve a **true virgin state**, execute:

```bash
# 1. Stop the native service
kill 107095

# 2. Wipe the JSON data files
rm -f /home/zaks/DataRoom/.deal-registry/deal_registry.json
rm -f /home/zaks/DataRoom/.deal-registry/quarantine.json
rm -f /home/zaks/DataRoom/.deal-registry/deferred_actions.json

# 3. Wipe the SQLite databases
rm -f /home/zaks/DataRoom/.deal-registry/ingest_state.db*
rm -f /home/zaks/DataRoom/.deal-registry/email_backfill_state.db
rm -f /home/zaks/DataRoom/.deal-registry/email_triage_state.db

# 4. Wipe case files and events
rm -rf /home/zaks/DataRoom/.deal-registry/case_files/*
rm -rf /home/zaks/DataRoom/.deal-registry/events/*

# 5. Either:
#    a) Fix Dashboard to use Docker backend (port 8091)
#    b) Or restart native service after wipe
```

### Option A: Use Docker Backend Only

Update Dashboard environment:
```bash
# In docker-compose or Dockerfile
NEXT_PUBLIC_API_URL=http://localhost:8091
```

### Option B: Keep Native Service

Restart after filesystem wipe:
```bash
cd /home/zaks/scripts
python3 deal_lifecycle_api.py --host 127.0.0.1 --port 8090 &
```

---

## Recommendations

1. **Consolidate Services**: Choose either Docker backend (8091) or native service (8090), not both
2. **Update Dashboard Config**: Ensure `NEXT_PUBLIC_API_URL` points to the correct backend
3. **Document Data Locations**: Maintain a clear map of all data storage locations
4. **Update Reset Script**: Include filesystem wipe in `tools/ops/reset_state.sh`:
   ```bash
   # Add to reset script
   rm -rf /home/zaks/DataRoom/.deal-registry/*.json
   rm -rf /home/zaks/DataRoom/.deal-registry/*.db*
   ```

---

## Appendix: Full Deal List (From JSON)

```json
{
  "DEAL-2026-001": "Acquisition Opportunities",
  "DEAL-2026-002": "Profitable IT Services Company",
  "DEAL-2026-003": "Textile Art Education Business",
  "DEAL-2026-004": "...",
  "DEAL-2026-005": "..."
}
```

---

## Document Metadata

| Field | Value |
|-------|-------|
| Created | 2026-01-26 |
| Author | Claude Opus 4.5 |
| Location | `/home/zaks/bookkeeping/docs/DATABASE_FORENSICS_20260126.md` |
| Related | `SESSION_REPORT_20260126_RAG_FIX_SYSTEM_RESET.md` |
