# Performance Budget Contract

## Purpose

Defines explicit performance thresholds for ZakOps services. This document is the source-of-truth artifact for Surface 14 (Performance Budget Contract).

## Status: Advisory Mode

Thresholds are enforced in **advisory mode** by default. Strict mode enforcement is available for CI gating when enabled via `STRICT=1`.

---

## API Latency Budgets

| Service | Endpoint Category | P95 Target | Measurement Method |
|---------|------------------|------------|-------------------|
| Backend | Health endpoints (`/health`, `/health/live`) | < 200ms | `curl -w '%{time_total}' -o /dev/null -s` |
| Backend | Deal CRUD (`/api/deals`, `/api/deals/{id}`) | < 500ms | `curl -w '%{time_total}' -o /dev/null -s` |
| Backend | Search (`/api/search/*`) | < 1000ms | `curl -w '%{time_total}' -o /dev/null -s` |
| Agent API | Health (`/health`) | < 200ms | `curl -w '%{time_total}' -o /dev/null -s` |
| Agent API | Invoke (`/api/v1/agent/invoke`) | < 30s | Measured via SSE first-token time |
| RAG | Health (`/`) | < 500ms | `curl -w '%{time_total}' -o /dev/null -s` |

## Dashboard Bundle Size Budgets

| Artifact | Threshold | Measurement Method |
|----------|-----------|-------------------|
| Total static directory | < 300 MB (dev), < 50 MB (prod) | `du -sm .next/static/` |
| Main JS bundle (`main-app.js`) | < 2 MB | `wc -c .next/static/chunks/main-app.js` |
| Polyfills | < 500 KB | `wc -c .next/static/chunks/polyfills.js` |

## Payload Size Budgets

| Route | Max Payload | Measurement Method |
|-------|------------|-------------------|
| `GET /api/deals` (list, default page) | < 100 KB | `curl -s \| wc -c` |
| `GET /api/deals/{id}` (detail) | < 50 KB | `curl -s \| wc -c` |
| `GET /api/pipeline/summary` | < 10 KB | `curl -s \| wc -c` |
| `GET /health` | < 5 KB | `curl -s \| wc -c` |

## OpenAPI Spec Size Budget

| Spec | Threshold | Measurement |
|------|-----------|-------------|
| `zakops-api.json` | < 500 KB | `wc -c` |
| `agent-api.json` | < 200 KB | `wc -c` |
| `rag-api.json` | < 50 KB | `wc -c` |

## Ownership

| Budget Area | Owner |
|-------------|-------|
| API latency | Backend team |
| Bundle size | Dashboard team |
| Payload size | Backend team + Dashboard team |
| Spec size | Contract surface maintainer |

## Measurement Cadence

- **Offline (CI-safe):** Bundle sizes and spec sizes checked on every validation run
- **Online (live):** API latency and payload sizes checked when services are running (`make validate-live`)
- **Advisory vs Strict:** Default is advisory (WARN on threshold breach). Set `STRICT=1` for CI enforcement (FAIL on breach).

---

## Deferred Items

These items are out of scope for the initial contract and are deferred for future hardening:

1. **Lighthouse CI integration** — automated Lighthouse scores per deploy
2. **Load testing thresholds** — concurrent user limits and degradation curves
3. **Memory budgets** — per-service RSS limits
4. **Database query time budgets** — per-query P95 targets
