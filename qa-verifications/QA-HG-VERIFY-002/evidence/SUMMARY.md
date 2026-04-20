# QA-HG-VERIFY-002 — Consolidated Results

**Date**: 2026-02-06
**Scope**: Phase 5 (DB Migrations), Phase 6 (MCP Contract), Phase 7 (CI Hardening), Red-Team (RT-1 through RT-15)

## Scorecard

| Check | Description | Result |
|-------|-------------|--------|
| **Phase 5** | | |
| V-P5.1 | Zaks-llm migrations dir | PASS |
| V-P5.2 | Initial schema 94 lines | PASS |
| V-P5.3 | Agent-api migration tracking | PASS |
| V-P5.4 | Runner scripts executable | PASS |
| V-P5.5 | migration-assertion.sh exists | PASS |
| V-P5.6 | No hardcoded containers | **FAIL** |
| V-P5.7 | rag-api in topology | PASS |
| V-P5.8 | Live schema dumps | PASS |
| **Phase 6** | | |
| V-P6.1 | Active server count = 1 | PASS |
| V-P6.2 | Archived servers | PASS |
| V-P6.3 | Tool count = 12 | PASS |
| V-P6.4 | Schema classes >= 12 | PASS |
| V-P6.5 | Server validates via tool_schemas | **FAIL** |
| V-P6.6 | Contract committed (12 tools) | PASS |
| V-P6.7 | README exists | PASS |
| **Phase 7** | | |
| V-P7.1 | "|| true" safe usage only | PASS |
| V-P7.2 | No continue-on-error | PASS |
| V-P7.4 | export_openapi >= 2 | **FAIL** |
| V-P7.5 | Agent/sync steps in CI | PASS |
| V-P7.6 | EXEC-002 in debt-ledger | **FAIL** |
| V-P7.8 | sync-all in Makefile | PASS |
| **Red-Team** | | |
| RT-1 | backend_models.py proportionality | PASS |
| RT-2 | agent-api-types 2229 lines | PASS |
| RT-3 | backend_client.py 8 HTTP refs | PASS |
| RT-4 | rag_models.py codegen header | PASS |
| RT-5 | tool_schemas.py real Field() | PASS |
| RT-6 | Initial schema 94 lines DDL | PASS |
| RT-7 | ESLint agent-api-types guard | PASS |
| RT-8 | No placeholders in bot | PASS |
| RT-11 | 0 TS suppression directives | PASS |
| RT-12 | CI triggers on push+PR | PASS |
| RT-13 | All 3 spec titles valid | PASS |
| RT-14 | All 5 Makefile targets present | PASS |
| RT-15 | Both bridge files present | PASS |

## Summary

**PASS: 27 / 31**
**FAIL: 4 / 31**

### Failures Requiring Remediation

1. **V-P5.6** — `migration-assertion.sh` uses hardcoded container names (`docker exec rag-db`, `docker exec zakops-backend-postgres-1`) instead of `docker compose exec <service>`. This makes the script brittle if container names change.

2. **V-P6.5** — `tool_schemas.py` defines 12 Pydantic BaseModel classes, but `server.py` (537 lines) does NOT import or reference `tool_schemas` at all. The schemas exist as a contract artifact but are not wired into runtime validation. Inputs arrive unvalidated.

3. **V-P7.4** — `spec-freshness-bot.yml` contains only 1 `export_openapi` reference; expected >= 2 (one for backend, one for agent-api or rag-api).

4. **V-P7.6** — `docs/debt-ledger.md` has 0 references to `EXEC-002`. The guardrail execution should be tracked in the debt ledger for audit trail.
