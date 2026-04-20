# Legacy System Archive

**Archived On:** Sun Jan 25 23:22:38 CST 2026
**Reason:** Decommissioned in favor of new Docker-based architecture

## What Was This?

The legacy system was the first version of the ZakOps deal management API:
- Ran as a native Python process on port 8090
- Stored deals in filesystem JSON (`/home/zaks/DataRoom/.deal-registry/deal_registry.json`)
- Used SQLite databases for some metadata
- Did NOT use PostgreSQL or Docker

## Why Was It Replaced?

1. **Data Isolation:** Filesystem storage doesn't scale and isn't transactional
2. **Architecture:** New system uses PostgreSQL with proper schemas
3. **Containerization:** Docker-based deployment is more portable and manageable
4. **Agent Integration:** New LangGraph agent requires proper database backend

## Contents of This Archive

- `deal-registry_*.tar.gz` - The filesystem data (deals, events, SQLite DBs)
- `legacy-service_*.tar.gz` - The Python service code (if found)
- This README file

## How to Restore (Emergency Only)

```bash
# Extract the data
tar -xzvf deal-registry_*.tar.gz -C /home/zaks/DataRoom/

# Start the legacy service
cd /home/zaks/scripts
python3 deal_lifecycle_api.py --host 127.0.0.1 --port 8090
```

**WARNING:** Do not run legacy and new systems simultaneously - they will conflict.
