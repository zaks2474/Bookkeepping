# ZakOps Agent Bridge - LangSmith Local Integration

**Date:** 2026-01-16
**Status:** Operational
**Location:** `/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/`

## Overview

The ZakOps Agent Bridge is an MCP (Model Context Protocol) server that connects LangSmith Agent Builder (cloud) to local ZakOps infrastructure. This enables cloud-based AI orchestration while keeping all state and execution local.

## Architecture

```
LangSmith Agent Builder (Cloud)
           │
           ▼
   Cloudflare Tunnel (encrypted)
           │
           ▼
ZakOps Agent Bridge (:9100)
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
  Deal   RAG   DataRoom
  API   API   Filesystem
(:8091)(:8052)
```

## Key Features

1. **Proposal-First Execution**: Actions require human approval before execution
2. **Path Safety**: All filesystem operations are sandboxed to prevent traversal attacks
3. **Atomic Writes**: JSON files are written atomically with verification
4. **Bearer Token Auth**: All endpoints (except /health) require authentication
5. **Structured Logging**: JSON logs to `/home/zaks/DataRoom/.deal-registry/logs/agent_bridge.jsonl`

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (no auth) |
| `/tools` | GET | List available tools |
| `/tools/zakops/list_deals` | GET | List all deals |
| `/tools/zakops/get_deal/{id}` | GET | Get deal with enrichments |
| `/tools/zakops/create_action` | POST | Create action proposal |
| `/tools/zakops/get_action/{id}` | GET | Get action status |
| `/tools/zakops/list_actions` | GET | List actions |
| `/tools/zakops/update_deal_profile` | POST | Update deal_profile.json |
| `/tools/zakops/write_deal_artifact` | POST | Write file to deal folder |
| `/tools/zakops/list_deal_artifacts/{id}` | GET | List files in deal folder |
| `/tools/zakops/list_quarantine` | GET | List pending quarantine items |
| `/tools/zakops/approve_quarantine/{id}` | POST | Approve quarantine item |
| `/tools/rag/query_local` | POST | Query RAG database |
| `/tools/rag/reindex_deal` | POST | Reindex deal in RAG |

## Files

```
/home/zaks/zakops-agent-api/apps/agent-api/mcp_bridge/
├── server.py                  # Main MCP server (FastMCP)
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (API key)
├── .env.example               # Template for .env
├── README.md                  # Quick start guide
├── zakops-agent-bridge.service # systemd unit file
└── cloudflare-tunnel.yaml.example # Tunnel config template
```

## Configuration

Environment variables (in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `ZAKOPS_BRIDGE_HOST` | Bind address | `127.0.0.1` |
| `ZAKOPS_BRIDGE_PORT` | Listen port | `9100` |
| `ZAKOPS_BRIDGE_API_KEY` | Bearer token for auth | (generated) |
| `ZAKOPS_DEAL_API_URL` | Deal Lifecycle API | `http://localhost:8091` |
| `ZAKOPS_RAG_API_URL` | RAG REST API | `http://localhost:8052` |
| `DATAROOM_ROOT` | DataRoom filesystem root | `/home/zaks/DataRoom` |

## Security Model

### Authentication
- All endpoints except `/health` require `Authorization: Bearer <token>` header
- Token is stored in `.env` file (not committed to git)
- 401 returned for missing/invalid tokens

### Path Safety
- All filesystem paths validated to prevent directory traversal
- `..` patterns explicitly blocked
- Paths resolved and verified to stay within allowed directories
- Only read/write operations permitted (no delete)

### Atomic Writes
- Files written to temporary location first
- Atomic rename to final destination
- Re-read and verify after write
- Cleanup on failure

## Operations

### Start Server Manually
```bash
cd /home/zaks/scripts/agent_bridge
source .env
uvicorn mcp_server:app --host 127.0.0.1 --port 9100
```

### Install systemd Service
```bash
sudo cp zakops-agent-bridge.service /etc/systemd/system/
sudo mkdir -p /var/log/zakops
sudo chown zaks:zaks /var/log/zakops
sudo systemctl daemon-reload
sudo systemctl enable zakops-agent-bridge
sudo systemctl start zakops-agent-bridge
```

### Setup Cloudflare Tunnel
```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Login and create tunnel
cloudflared tunnel login
cloudflared tunnel create zakops-bridge

# Configure tunnel
cp cloudflare-tunnel.yaml.example ~/.cloudflared/config.yml
# Edit config.yml with your tunnel UUID and hostname

# Route DNS
cloudflared tunnel route dns zakops-bridge zakops-bridge.yourdomain.com

# Run tunnel (or install as service)
cloudflared tunnel run zakops-bridge
```

### Test Endpoints
```bash
# Health check (no auth)
curl http://localhost:9100/health

# List deals (requires auth)
API_KEY=$(grep ZAKOPS_BRIDGE_API_KEY .env | cut -d= -f2)
curl -H "Authorization: Bearer $API_KEY" http://localhost:9100/tools/zakops/list_deals

# Get specific deal with enrichments
curl -H "Authorization: Bearer $API_KEY" http://localhost:9100/tools/zakops/get_deal/DEAL-2026-003
```

## Acceptance Tests

All tests passed on 2026-01-16:

| # | Test | Status |
|---|------|--------|
| 1 | Health check returns status | PASS |
| 2 | Auth rejection without token | PASS |
| 3 | List deals returns results | PASS |
| 4 | Get deal with folder enrichment | PASS |
| 5 | Path traversal blocked | PASS |
| 6 | Atomic write verification | PASS |
| 7 | RAG query works | PASS |
| 8 | Action creation attempted | PASS |

## LangSmith Integration

In LangSmith Agent Builder, configure the bridge as an MCP server:

1. **Server URL**: `https://zakops-bridge.yourdomain.com` (via Cloudflare Tunnel)
2. **Authentication**: Bearer token from `.env`
3. **Available Tools**: Listed at `/tools` endpoint

The bridge translates MCP tool calls to local API calls and filesystem operations, enabling the LangSmith agent to:
- Browse and filter deals
- Read deal data and enrichments
- Create action proposals (human-approved)
- Update deal profiles
- Query local RAG for document search
- Write artifacts to deal folders (path-safe)

## Troubleshooting

### Server won't start
- Check port 9100 is available: `lsof -i :9100`
- Verify .env file exists and has API key
- Check backend services: Deal API (:8091), RAG API (:8052)

### Authentication failures
- Verify API key matches between client and `.env`
- Check `Authorization: Bearer <token>` header format

### Deal folder not found
- Folders use pattern `{CanonicalName}--{YearNumber}` (e.g., `Foo-Bar--2026-003`)
- Verify folder exists in `/home/zaks/DataRoom/00-PIPELINE/Inbound/`

### Logs
- Console: stderr when running manually
- JSON logs: `/home/zaks/DataRoom/.deal-registry/logs/agent_bridge.jsonl`
- systemd: `/var/log/zakops/agent-bridge.log`
