# Change Log

Use this file to record notable environment changes (dates, what changed, why).

- 2025-11-30: Added bookkeeping repo, capture script, cron snapshots every 10m; Docker snapshots expanded for ports/networks; added docs (service catalog, runbooks, onboarding) and Makefile; populated service catalog with OpenWebUI/Zaks-llm stack details; added service-specific health checks (Claude API, OpenWebUI, vLLM, ZakOps API, RAG REST) plus compose status.
- 2025-11-30: Enhanced capture script to copy systemd unit and docker-compose files; added systemd/Docker health checks; added before-push checklist to README.
- 2025-12-01: Moved to new apartment; LAN Wi-Fi gateway `attlocal.net`, local IP now 192.168.1.67 (WSL vEthernet 172.30.176.1). Public IP not recorded (network curl blocked); rerun `curl ifconfig.me` or `curl https://api.ipify.org` when available and update allowlists/firewalls/OAuth/webhooks accordingly.
- 2025-12-05: Added LinkedIn MCP service to Zaks-llm compose (port 8030:8000, requires LINKEDIN_COOKIE); catalog updated; logs path `logs/linkedin-mcp` created. Cookie still needed to start successfully.
- 2025-12-04: Created LinkedIn MCP implementation plan (docs/LINKEDIN-MCP-IMPLEMENTATION.md); researched best LinkedIn MCP servers; selected stickerdaniel/linkedin-mcp-server for job searching, profile research, and company analysis capabilities; established standard for storing implementation plans in docs/ as individual markdown files.
- 2025-12-04: Created automated job application workflow plan (docs/AUTOMATED-JOB-APPLICATION-WORKFLOW.md); designed end-to-end pipeline integrating LinkedIn MCP (job discovery), Claude AI (fit analysis + material generation), and mcp-browser-use (form automation); includes orchestration, safety guardrails, tracking dashboard, and monitoring; estimated 4-week implementation timeline.
