# V-L1.7: RAG/LLM DSN -> Canonical DB (CS-002)
**VERDICT: PASS**

## Evidence
RAG REST in `Zaks-llm/docker-compose.yml`:
```
POSTGRES_URL=postgresql://postgres:crawl4aipass@rag-db:5432/crawlrag
```
This is the dedicated RAG/vector DB (`crawlrag`), not the deal database. Correct and expected.

Deal origination config (`Zaks-llm/src/deal_origination/config.py`):
```python
postgres_url: str = Field(
    default="postgresql://zakops:zakops_dev@localhost:5432/zakops",
    ...
)
```
Points to canonical database on port 5432. No references to 5435.

Decommissioned compose files properly documented:
```
# The deal-engine-db container on port 5435 has been permanently destroyed.
# All deal data lives in the canonical database: zakops-backend-postgres-1 on port 5432
# DSN: postgresql://zakops:zakops_dev@localhost:5432/zakops
```
