# Type Source of Truth Decision

**Decision:** C — Multiple specs, each authoritative for their domain
**Rationale:** The backend API (port 8091) and agent API (port 8095) are separate services with separate OpenAPI specs. The dashboard consumes both.

## Authoritative Sources
- Deal/Action/Quarantine types: `packages/contracts/openapi/zakops-api.json` (backend spec)
- Agent run/session types: Manual with debt tracking (agent-api has no committed OpenAPI spec yet)
- SSE/WebSocket events: Manual with debt tracking (non-OpenAPI transport)
- Stage transition types: Manual with debt tracking (workflow router models have different field names)

## Manual Type Policy
Manual types are ONLY acceptable when:
1. The type comes from a non-OpenAPI transport (SSE, WebSocket)
2. The type is from a service without OpenAPI spec (agent-api at port 8095)
3. The type is temporary bridge during migration (e.g., field name mismatch with workflow router)

Each manual type MUST have:
- `MANUAL_TYPE_DEBT` comment with reason
- Target removal date
- Entry in `docs/debt-ledger.md`

## Current Manual Type Inventory (4 types, ceiling = 4)
1. **EventResponse** — Events use DealEvent schema but bridge needs string dates
2. **AgentRun** — Agent API service, not in backend OpenAPI
3. **StageTransitionRequest** — Workflow router TransitionRequest has different field names
4. **StageTransitionResponse** — Workflow router TransitionResponse has different field names
