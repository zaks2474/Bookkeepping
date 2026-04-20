# Legacy Decommission & RAG Cleanup Report
**Mission ID:** LEGACY-DECOM-001
**Date:** 2026-01-26
**Status:** ✅ COMPLETE
**Operator:** Claude Opus 4.5

---

## Executive Summary

Successfully completed full decommission of legacy systems and RAG cleanup. The ZakOps environment now runs on a clean, unified Docker-based architecture with no ghost data or conflicting services.

| Metric | Before | After |
|--------|--------|-------|
| Services on port 8090 | 1 (native Python) | 0 (free) |
| Ghost deals in JSON | 5 | 0 (archived) |
| RAG MCP containers | 2 | 1 (only rag-rest-api) |
| Dashboard API target | 8090 (wrong) | 8091 (correct) |
| Systemd services masked | 0 | 7 |

---

## Phase 1: Archive Legacy System ✅

### Archives Created

| Archive | Size | Contents |
|---------|------|----------|
| `deal-registry_20260125_232201.tar.gz` | 792K | 5 deals, events, SQLite DBs |
| `legacy-service_20260125_232201.tar.gz` | 1.8M | `/home/zaks/scripts/` directory |
| `crawl4ai-rag_20260125_232201.tar.gz` | ~50MB | MCP server project |
| `LEGACY_SYSTEM_README_20260125_232201.md` | 1.3K | Restoration guide |

**Location:** `/home/zaks/bookkeeping/archives/`

---

## Phase 2: Legacy Decommission ✅

### Process Killed

The native Python service kept respawning due to systemd:

| PID | Action | Result |
|-----|--------|--------|
| 107095 | kill -15, kill -9 | Respawned as 594617 |
| 594617 | kill -9 | Respawned as 595595 |
| 595595 | systemctl mask | ✅ Finally stopped |

### Systemd Services Masked

| Service | Description | Status |
|---------|-------------|--------|
| `zakops-api-8090.service` | Deal Lifecycle API (:8090) | Masked |
| `kinetic-actions-runner.service` | Actions Runner | Masked |
| `zakops-email-triage.service` | Email Triage | Masked |
| `zakops.service` | Main ZakOps | Masked |
| `zakops-api.service` | Orchestration API | Masked |
| `deal-lifecycle.service` | Legacy API | Masked |
| `claude-code-api.service` | Claude Code API | Masked |

### Data Removed

| Item | Location | Action |
|------|----------|--------|
| `deal_registry.json` | `.deal-registry/` | Deleted |
| `ingest_state.db*` | `.deal-registry/` | Deleted |
| `email_triage_state.db` | `.deal-registry/` | Deleted |
| `sender_history.db` | `.deal-registry/` | Deleted |
| `events/` | `.deal-registry/events/` | Deleted |
| `.deal-registry/` | `/home/zaks/DataRoom/` | Renamed to `.deal-registry.DECOMMISSIONED_20260125` |

---

## Phase 3: RAG System Cleanup ✅

### Containers Removed

| Container | Port | Image | Action |
|-----------|------|-------|--------|
| `docs-rag-mcp` | 8051 | `crawl4ai-rag-docs-rag-mcp` | Removed |

### Images Removed

| Image | Size | Action |
|-------|------|--------|
| `crawl4ai-rag-docs-rag-mcp:latest` | 2.58GB | Removed |

### Directory Removed

| Path | Size | Action |
|------|------|--------|
| `/root/mcp-servers/crawl4ai-rag/` | ~50MB | Archived + Removed |

### Retained (Required by Agent)

| Service | Port | Purpose |
|---------|------|---------|
| `rag-rest-api` | 8052 | RAG query endpoint |
| `rag-db` | 5434 | pgvector database |

---

## Phase 4: Dashboard Reconfiguration ✅

### Configuration Change

**File:** `/home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml`

```yaml
# BEFORE
- NEXT_PUBLIC_API_URL=http://localhost:8090

# AFTER
- NEXT_PUBLIC_API_URL=http://localhost:8091
```

**Backup:** `docker-compose.yml.bak_20260125_232201`

### Actions

1. Stopped and removed old dashboard container
2. Rebuilt dashboard image with new config
3. Started new dashboard container
4. Verified environment variables

---

## Phase 5: Final Verification ✅

### Service Health

| Service | Port | Status |
|---------|------|--------|
| Docker Backend | 8091 | ✅ HTTP 200 |
| Agent API | 8095 | ✅ HTTP 200 |
| RAG API | 8052 | ✅ HTTP 200 |
| Dashboard | 3003 | ✅ HTTP 307 |

### Data State (Virgin)

| Data Type | Count |
|-----------|-------|
| Deals in PostgreSQL | 0 |
| Chunks in RAG | 0 |
| Ghost JSON files | 0 |

### Ghost Check

| Check | Result |
|-------|--------|
| Port 8090 free? | ✅ Yes |
| `deal_registry.json` exists? | ✅ No |
| `.deal-registry/` exists? | ✅ No |
| `crawl4ai-rag/` exists? | ✅ No |
| Dashboard points to 8091? | ✅ Yes |

---

## Final Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ZAKOPS CLEAN ARCHITECTURE (FINAL)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                                                       │
│   │    Dashboard    │                                                       │
│   │   (Port 3003)   │                                                       │
│   └────────┬────────┘                                                       │
│            │                                                                │
│            ├── NEXT_PUBLIC_API_URL ──────────► Docker Backend (8091)       │
│            │                                    └── zakops-postgres (5432)  │
│            │                                        └── zakops.deals = 0    │
│            │                                                                │
│            └── NEXT_PUBLIC_AGENT_API_URL ────► Agent API (8095)            │
│                                                 └── LangGraph Agent         │
│                                                     │                       │
│                                                     └── RAG API (8052)      │
│                                                         └── rag-db (5434)   │
│                                                             └── chunks = 0  │
│                                                                             │
│   DECOMMISSIONED:                                                           │
│   ├── Legacy Python (8090) - KILLED + 7 systemd services MASKED            │
│   ├── Filesystem JSON - ARCHIVED (792K) + DELETED                          │
│   ├── crawl4ai-rag - ARCHIVED + REMOVED                                    │
│   └── docs-rag-mcp (8051) - CONTAINER + IMAGE REMOVED                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Rollback Procedure (Emergency Only)

If something goes wrong, restore from archives:

```bash
# 1. Unmask and start legacy services
sudo systemctl unmask zakops-api-8090.service
sudo systemctl start zakops-api-8090.service

# 2. Restore legacy data
tar -xzvf /home/zaks/bookkeeping/archives/deal-registry_20260125_232201.tar.gz \
    -C /home/zaks/DataRoom/

# 3. Restore crawl4ai-rag
tar -xzvf /home/zaks/bookkeeping/archives/crawl4ai-rag_20260125_232201.tar.gz \
    -C /root/mcp-servers/

# 4. Revert dashboard config
cp /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml.bak_20260125_232201 \
   /home/zaks/zakops-agent-api/deployments/docker/docker-compose.yml
docker compose -f deployments/docker/docker-compose.yml up -d dashboard
```

---

## Gate Results

| Gate | Phase | Result |
|------|-------|--------|
| Gate 0 | Pre-Flight | ✅ PASSED |
| Gate 1 | Archive | ✅ PASSED |
| Gate 2 | Legacy Decommission | ✅ PASSED (retry) |
| Gate 3 | RAG Cleanup | ✅ PASSED |
| Gate 4 | Dashboard Reconfig | ✅ PASSED |
| Gate 5 | Final Verification | ✅ PASSED |

---

## Document Metadata

| Field | Value |
|-------|-------|
| Created | 2026-01-26 |
| Author | Claude Opus 4.5 |
| Mission ID | LEGACY-DECOM-001 |
| Duration | ~25 minutes |
| Location | `/home/zaks/bookkeeping/docs/LEGACY_DECOMMISSION_REPORT_20260126.md` |
| Related | `RAG_ARCHITECTURE_FORENSICS_20260125.md`, `DATABASE_FORENSICS_20260126.md` |
