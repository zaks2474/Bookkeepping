# Change Log

Use this file to record notable environment changes (dates, what changed, why).

- 2025-11-30: Added bookkeeping repo, capture script, cron snapshots every 10m; Docker snapshots expanded for ports/networks; added docs (service catalog, runbooks, onboarding) and Makefile; populated service catalog with OpenWebUI/Zaks-llm stack details; added service-specific health checks (Claude API, OpenWebUI, vLLM, ZakOps API, RAG REST) plus compose status.
- 2025-11-30: Enhanced capture script to copy systemd unit and docker-compose files; added systemd/Docker health checks; added before-push checklist to README.
