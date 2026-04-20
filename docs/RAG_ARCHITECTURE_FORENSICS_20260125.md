# RAG Architecture Forensics Report
**Date**: 2026-01-25
**Investigator**: Claude Opus 4.5
**Objective**: Identify exactly which RAG service is used by the agent, what database it connects to, and where deal data originates.

---

## Executive Summary

| Question | Answer | Evidence |
|----------|--------|----------|
| **What container serves port 8052?** | `rag-rest-api` | `docker ps` output |
| **What image is it built from?** | `zaks-llm-rag-rest-api` | Custom build from `/home/zaks/Zaks-llm/` |
| **What database does it connect to?** | `rag-db:5432` (database: `crawlrag`) | `POSTGRES_URL` env var |
| **How many chunks in RAG database?** | **0** (empty) | SQL query on `crawledpage` table |
| **How many deals in backend database?** | **0** | SQL query on `zakops.deals` |
| **Where are the 5 deals?** | **Filesystem JSON** (`/home/zaks/DataRoom/.deal-registry/deal_registry.json`) | File inspection |
| **Was crawl4ai-rag part of original architecture?** | **Yes**, created 2025-12-14 | `/root/mcp-servers/crawl4ai-rag/` |
| **What does the agent see when querying "deals"?** | **Nothing** (0 results) | RAG query test |

### Key Finding

The system has **THREE separate data stores** for deals, none of which are synchronized:

| Store | Location | Deals | Used By |
|-------|----------|-------|---------|
| Filesystem JSON | `/home/zaks/DataRoom/.deal-registry/deal_registry.json` | **5** | Native Python service (port 8090, NOT RUNNING) |
| Backend PostgreSQL | `zakops-postgres-1:5432` → `zakops.deals` | **0** | Docker Backend (port 8091) |
| RAG PostgreSQL | `rag-db:5434` → `crawlrag.crawledpage` | **0** | RAG REST API (port 8052) |

---

## Phase 1: RAG Service Inventory

### 1.1 Running RAG-Related Containers

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `rag-rest-api` | `zaks-llm-rag-rest-api` | **8052** | RAG REST API (query endpoint) |
| `docs-rag-mcp` | `crawl4ai-rag-docs-rag-mcp` | 8051 | MCP server for RAG tools |
| `rag-db` | `pgvector/pgvector:pg17` | 5434 | PostgreSQL with pgvector extension |

### 1.2 Docker Compose Sources

Multiple compose files reference RAG services:

| File | Services Defined |
|------|------------------|
| `/home/zaks/Zaks-llm/docker-compose.yml` | `rag-rest-api` (port 8052) |
| `/root/mcp-servers/crawl4ai-rag/docker-compose.yml` | `docs-rag-mcp`, `rag-db` |
| `/home/zaks/zakops-agent-api/apps/agent-api/docker-compose.yml` | References RAG_REST_URL |

### 1.3 RAG REST API Configuration

From `/home/zaks/Zaks-llm/docker-compose.yml`:
```yaml
rag-rest-api:
  build:
    context: .
    dockerfile: Dockerfile.rag-rest-api
  container_name: rag-rest-api
  ports:
    - "8052:8080"
  environment:
    - POSTGRES_URL=postgresql://postgres:crawl4aipass@rag-db:5432/crawlrag
    - OLLAMA_API_URL=http://host.docker.internal:11434/api/embeddings
    - OLLAMA_EMBED_MODEL=bge-m3
    - OLLAMA_EMBEDDING_DIM=1024
```

---

## Phase 2: Database Connectivity

### 2.1 RAG Service Database Connection

**Container**: `rag-rest-api`
**Environment Variables**:
```
POSTGRES_URL=postgresql://postgres:crawl4aipass@rag-db:5432/crawlrag
OLLAMA_API_URL=http://host.docker.internal:11434/api/embeddings
OLLAMA_EMBED_MODEL=bge-m3
OLLAMA_EMBEDDING_DIM=1024
```

**Database**: `crawlrag` on container `rag-db` (port 5434 externally, 5432 internally)

### 2.2 MCP RAG Service Database Connection

**Container**: `docs-rag-mcp`
**Environment Variables**:
```
POSTGRES_URL=postgresql://postgres:crawl4aipass@rag-db:5432/crawlrag
DATABASE_NAME=crawlrag
POSTGRES_DB=crawlrag
POSTGRES_USER=postgres
POSTGRES_PASSWORD=crawl4aipass
```

**Both services share the same database!**

---

## Phase 3: Agent RAG Configuration

### 3.1 Backend Service (zakops-backend-1)

**Environment**:
```
ZAKOPS_RAG_API_URL=http://172.23.0.1:8052
```

**Code** (`/home/zaks/zakops-backend/src/core/chat_evidence_builder.py`):
```python
_rag_base = os.getenv("RAG_ENDPOINT") or os.getenv("ZAKOPS_RAG_API_URL", "http://localhost:8052")
RAG_ENDPOINT = _rag_base.rstrip("/") + "/rag/query" if not _rag_base.endswith("/rag/query") else _rag_base
RAG_TIMEOUT = int(os.getenv("RAG_TIMEOUT", "30"))
```

**Effective Endpoint**: `http://172.23.0.1:8052/rag/query`

### 3.2 Agent API Service (zakops-agent-api)

**Environment**:
```
RAG_REST_URL=http://host.docker.internal:8052
```

### 3.3 Connectivity Test

```bash
# Backend -> RAG
docker exec zakops-backend-1 curl http://172.23.0.1:8052/rag/stats
# Result: {"total_chunks":0,"unique_urls":0,"embedding_model":"bge-m3","embedding_dim":1024}
```

**Connectivity: WORKING** - Backend can reach RAG service.

---

## Phase 4: Database Contents

### 4.1 Backend PostgreSQL (zakops-postgres-1)

```sql
SELECT COUNT(*) as deal_count FROM zakops.deals;
```
**Result**: `0` deals

### 4.2 RAG PostgreSQL (rag-db)

**Tables**:
```
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+----------
 public | crawledpage | table | postgres
```

**Chunk Count**:
```sql
SELECT COUNT(*) FROM crawledpage;
```
**Result**: `0` rows (empty)

### 4.3 Filesystem JSON (NOT in any database)

**File**: `/home/zaks/DataRoom/.deal-registry/deal_registry.json`

**Contents**:
| Deal ID | Name |
|---------|------|
| DEAL-2026-001 | Acquisition Opportunities |
| DEAL-2026-002 | Profitable IT Services Company |
| DEAL-2026-003 | Textile Art Education Business |
| DEAL-2026-004 | AI Shopify Analytics SaaS |
| DEAL-2026-005 | High-Ticket Design Education Business |

**Count**: **5 deals** (THIS IS WHERE THE DEALS ARE!)

---

## Phase 5: API Endpoint Verification

### 5.1 RAG Stats (port 8052)

```bash
curl http://localhost:8052/rag/stats
```
```json
{
  "total_chunks": 0,
  "unique_urls": 0,
  "embedding_model": "bge-m3",
  "embedding_dim": 1024
}
```

### 5.2 RAG Query Test

```bash
curl -X POST http://localhost:8052/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "deals", "top_k": 10}'
```
```json
{
  "query": "deals",
  "results": [],
  "count": 0
}
```

### 5.3 Backend Deals API (port 8091 - Docker)

```bash
curl http://localhost:8091/api/deals
```
**Result**: `[]` (empty array)

### 5.4 Native Service (port 8090)

**Status**: NOT RUNNING
```bash
ss -tlnp | grep 8090
# No output - service is down
```

---

## Phase 6: Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CURRENT DATA ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────────┐
│    Dashboard    │     │   Agent API     │     │         Backend             │
│   (Port 3003)   │     │  (Port 8095)    │     │       (Port 8091)           │
└────────┬────────┘     └────────┬────────┘     └────────────┬────────────────┘
         │                       │                           │
         │ NEXT_PUBLIC_          │ RAG_REST_URL=             │ ZAKOPS_RAG_API_URL=
         │ API_URL=8090          │ host.docker.internal:8052 │ 172.23.0.1:8052
         │ (POINTS TO            │                           │
         │  DEAD SERVICE!)       ▼                           ▼
         │              ┌─────────────────┐         ┌─────────────────┐
         │              │  rag-rest-api   │         │  rag-rest-api   │
         │              │   (Port 8052)   │◀────────│   (Port 8052)   │
         │              └────────┬────────┘         └─────────────────┘
         │                       │
         │                       │ POSTGRES_URL=
         │                       │ rag-db:5432/crawlrag
         │                       ▼
         │              ┌─────────────────┐
         │              │     rag-db      │
         │              │  (Port 5434)    │
         │              │   0 CHUNKS      │
         │              │   (EMPTY!)      │
         │              └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Native Python  │
│  (Port 8090)    │
│  NOT RUNNING!   │
└────────┬────────┘
         │
         │ reads from
         ▼
┌─────────────────────────────────────────┐
│      FILESYSTEM (NOT A DATABASE)        │
│  /home/zaks/DataRoom/.deal-registry/    │
│  └── deal_registry.json                 │
│       └── 5 DEALS HERE!                 │
└─────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                           SEPARATE: BACKEND DATABASE                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│ zakops-backend  │
│  (Port 8091)    │
└────────┬────────┘
         │
         │ connects to
         ▼
┌─────────────────┐
│zakops-postgres-1│
│  (Port 5432)    │
│ zakops.deals=0  │
└─────────────────┘
```

---

## Phase 7: Root Cause Analysis

### Why Are There 5 Deals That Won't Go Away?

| Issue | Explanation |
|-------|-------------|
| **Data Location** | Deals are in a **JSON file on the filesystem**, not in any PostgreSQL database |
| **Service Mismatch** | Dashboard (`NEXT_PUBLIC_API_URL`) points to port 8090, which runs a **native Python script** that reads from JSON |
| **Docker Reset Ineffective** | `docker volume rm` only affects Docker volumes, **not filesystem files** |
| **RAG Database Empty** | The RAG system (`crawlrag` database) has **0 chunks** - it was never populated or was wiped |
| **Backend Database Empty** | The Docker backend (`zakops.deals`) has **0 deals** - it's a separate system |

### Why Was the Reset Incomplete?

The "virgin reset" performed earlier only cleared:
- Docker volumes (`zakops_postgres_data`, `crawl4ai-rag_postgres_data`, etc.)
- Container data

It did NOT clear:
- `/home/zaks/DataRoom/.deal-registry/deal_registry.json` (5 deals)
- `/home/zaks/DataRoom/.deal-registry/*.db` (SQLite databases)
- `/home/zaks/DataRoom/.deal-registry/events/` (deal events)

---

## Phase 8: Service Origin Analysis

### Was crawl4ai-rag Part of Original Architecture?

**Location**: `/root/mcp-servers/crawl4ai-rag/`
**Created**: 2025-12-14 11:17:49
**Source**: External MCP server package

The crawl4ai-rag service was added as an **MCP server** for documentation RAG capabilities. It is:
- A separate project from the main ZakOps codebase
- Designed for web crawling and document retrieval
- Not originally integrated with the deal management system

### RAG REST API Origin

**Location**: `/home/zaks/Zaks-llm/`
**Service**: `rag-rest-api`

This is a **custom-built service** from the Zaks-llm project that:
- Shares the same database (`crawlrag`) as crawl4ai-rag
- Provides REST endpoints for RAG queries
- Uses Ollama embeddings (bge-m3 model)

---

## Recommendations

### Option A: Use Docker Backend Only (Recommended)

1. **Stop/remove native service** (already not running)
2. **Delete filesystem data**:
   ```bash
   rm -f /home/zaks/DataRoom/.deal-registry/deal_registry.json
   rm -f /home/zaks/DataRoom/.deal-registry/*.db*
   ```
3. **Update Dashboard** to point to Docker backend:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8091
   ```

### Option B: Populate RAG Database

If you want RAG to contain deal information:
1. **Ingest deal documents** into the RAG system via crawl4ai
2. **Sync deal data** between backend PostgreSQL and RAG

### Option C: Consolidate Data Sources

Create a migration to:
1. Load deals from JSON into PostgreSQL
2. Remove JSON-based storage
3. Update all services to use single PostgreSQL database

---

## Summary Table

| Component | Port | Database | Connection String | Data |
|-----------|------|----------|-------------------|------|
| Dashboard | 3003 | N/A | Points to 8090 (dead) | - |
| Native Service | 8090 | Filesystem JSON | `/home/zaks/DataRoom/.deal-registry/deal_registry.json` | **5 deals** |
| Docker Backend | 8091 | PostgreSQL | `zakops-postgres-1:5432/zakops` | **0 deals** |
| RAG REST API | 8052 | PostgreSQL (pgvector) | `rag-db:5432/crawlrag` | **0 chunks** |
| RAG MCP | 8051 | PostgreSQL (pgvector) | `rag-db:5432/crawlrag` | **0 chunks** |
| Agent API | 8095 | PostgreSQL (pgvector) | `zakops-agent-db:5432/zakops_agent` | N/A (different schema) |

---

## Document Metadata

| Field | Value |
|-------|-------|
| Created | 2026-01-25 |
| Author | Claude Opus 4.5 |
| Location | `/home/zaks/bookkeeping/docs/RAG_ARCHITECTURE_FORENSICS_20260125.md` |
| Related | `DATABASE_FORENSICS_20260126.md`, `SESSION_REPORT_20260126_RAG_FIX_SYSTEM_RESET.md` |
