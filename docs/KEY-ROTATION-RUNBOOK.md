# Key Rotation Runbook

**Service:** ZakOps Agent Bridge (MCP Server)
**Date:** 2026-02-14
**Phase:** P0-T7 (Safety & Perimeter)

---

## Keys Covered

| Key | Location | Used By |
|-----|----------|---------|
| `ZAKOPS_BRIDGE_API_KEY` | `/home/zaks/scripts/agent_bridge/.env` | Bridge auth (LangSmith → Bridge) |
| `ZAKOPS_API_KEY` | Backend Docker env / `.env` | Bridge → Backend (X-API-Key header) |

---

## Rotation Procedure: ZAKOPS_BRIDGE_API_KEY (Zero-Downtime)

### Prerequisites
- SSH access to production host
- Access to LangSmith Agent Builder configuration

### Steps (Dual-Token Rolling Window — P7-03)

1. **Generate new key:**
   ```bash
   NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
   echo "New key: $NEW_KEY"
   ```

2. **Install new key as secondary (bridge keeps accepting old key):**
   ```bash
   nano /home/zaks/scripts/agent_bridge/.env
   # ADD: ZAKOPS_BRIDGE_API_KEY_SECONDARY=<NEW_KEY>
   # KEEP: ZAKOPS_BRIDGE_API_KEY=<OLD_KEY>  (unchanged)
   sudo systemctl restart zakops-agent-bridge
   ```

3. **Verify both keys work:**
   ```bash
   OLD_KEY=$(grep '^ZAKOPS_BRIDGE_API_KEY=' /home/zaks/scripts/agent_bridge/.env | cut -d= -f2)
   # Old key still works:
   curl -sf -H "Authorization: Bearer $OLD_KEY" http://localhost:9100/health
   # New key also works:
   curl -sf -H "Authorization: Bearer $NEW_KEY" http://localhost:9100/health
   ```

4. **Update LangSmith Agent Builder to use new key:**
   - Go to LangSmith Agent Builder → MCP Server Configuration
   - Update the Bearer token to `$NEW_KEY`
   - Test a tool call from the LangSmith UI

5. **Promote new key to primary, remove old:**
   ```bash
   nano /home/zaks/scripts/agent_bridge/.env
   # CHANGE: ZAKOPS_BRIDGE_API_KEY=<NEW_KEY>
   # REMOVE: ZAKOPS_BRIDGE_API_KEY_SECONDARY=
   sudo systemctl restart zakops-agent-bridge
   ```

6. **Verify final state:**
   ```bash
   curl -sf -H "Authorization: Bearer $NEW_KEY" http://localhost:9100/health
   # Expected: {"status": "ok", ...}

   # Old key should now fail:
   curl -sf -H "Authorization: Bearer $OLD_KEY" http://localhost:9100/tools 2>&1 || echo "OLD KEY REJECTED (expected)"
   ```

7. **Log rotation event:**
   ```bash
   echo "$(date -Iseconds) KEY_ROTATED key=ZAKOPS_BRIDGE_API_KEY by=$(whoami)" \
     >> /home/zaks/bookkeeping/logs/key-rotation.log
   ```

**Note:** Steps 2-4 provide a rolling window where both old and new keys are accepted.
This allows LangSmith to be updated without any request failures.

---

## Rotation Procedure: ZAKOPS_API_KEY

### Prerequisites
- SSH access to production host
- Docker access for backend restart

### Steps

1. **Generate new key:**
   ```bash
   NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
   echo "New key: $NEW_KEY"
   ```

2. **Update backend environment:**
   ```bash
   # Edit the backend Docker env file
   nano /home/zaks/zakops-agent-api/apps/backend/.env
   # Change: ZAKOPS_API_KEY=<NEW_KEY>
   ```

3. **Restart backend:**
   ```bash
   cd /home/zaks/zakops-agent-api
   COMPOSE_PROJECT_NAME=zakops docker compose up -d backend --no-deps
   ```

4. **Update bridge to use new backend key:**
   ```bash
   nano /home/zaks/scripts/agent_bridge/.env
   # Change: ZAKOPS_API_KEY=<NEW_KEY>
   sudo systemctl restart zakops-agent-bridge
   ```

5. **Verify injection works:**
   ```bash
   API_KEY=$(grep ZAKOPS_BRIDGE_API_KEY /home/zaks/scripts/agent_bridge/.env | cut -d= -f2)
   curl -sf -X POST \
     -H "Authorization: Bearer $API_KEY" \
     -H "Content-Type: application/json" \
     http://localhost:9100/tools/zakops/list_deals
   ```

---

## Emergency: Disable Bridge Auth Temporarily

If auth issues are blocking operations and keys cannot be rotated immediately:

```bash
# TEMPORARY: Clear the API key to enter development mode
# In /home/zaks/scripts/agent_bridge/.env:
# ZAKOPS_BRIDGE_API_KEY=
sudo systemctl restart zakops-agent-bridge
```

**WARNING:** This removes all authentication. Re-enable ASAP.

---

## Key Storage Policy

- Bridge keys: `/home/zaks/scripts/agent_bridge/.env` (EnvironmentFile in systemd, NOT in git)
- Backend keys: Docker environment / `.env` (NOT in git)
- Never commit keys to any repository
- Never log full key values (first 8 + last 4 chars only)
- Rotate keys quarterly or immediately after any suspected compromise

---

## Audit Trail

Key rotations should be logged:
```bash
echo "$(date -Iseconds) KEY_ROTATED key=ZAKOPS_BRIDGE_API_KEY by=$(whoami)" \
  >> /home/zaks/bookkeeping/logs/key-rotation.log
```
