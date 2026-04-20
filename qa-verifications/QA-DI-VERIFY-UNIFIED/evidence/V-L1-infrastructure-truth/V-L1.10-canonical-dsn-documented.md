# V-L1.10: Canonical DSN Documented
**VERDICT: PASS**

## Evidence
1. **Code constant**: `CANONICAL_DB_NAME = "zakops"` in `main.py:344`

2. **Decommissioned compose files** document canonical DB:
   - `zakops-backend/infra/docker/docker-compose.postgres.yml`: "Canonical database: zakops-backend-postgres-1 on port 5432"
   - `zakops-backend/infra/docker/docker-compose.yml`: same
   - `Zaks-llm/docker-compose.deal-engine.yml`: "All deal data lives in the canonical database: zakops-backend-postgres-1 on port 5432"
   - `Zaks-llm/src/deal_origination/docker-compose.deal-engine.yml`: same

3. **CLAUDE.md** documents: "zakops (container: zakops-postgres-1): Main DB -- deals, deal_events, quarantine_items, actions, materials"

4. **ADR-002-canonical-database.md** exists at `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-UNIFIED/layer-6/`
