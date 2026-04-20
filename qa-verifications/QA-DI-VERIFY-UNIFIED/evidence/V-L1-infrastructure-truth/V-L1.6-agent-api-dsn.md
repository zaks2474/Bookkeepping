# V-L1.6: Agent API DSN -> Canonical DB (CS-001)
**VERDICT: PASS**

## Evidence
Agent API `.env.development`:
```
DATABASE_URL=postgresql://agent:agent_secure_pass_123@db:5432/zakops_agent
```

Agent API `docker-compose.yml`:
```
POSTGRES_HOST=db  (internal Docker networking to its own postgres service)
```

The Agent API connects to its own dedicated database `zakops_agent` (separate schema/user),
NOT to the rogue 5435 port. The `db` service in agent-api's docker-compose.yml is a dedicated
container for agent state (LangGraph checkpoints), which is the expected architecture per
SERVICE-CATALOG. No references to port 5435.
