# Onboarding

Quick orientation for new operators.

## Prereqs
- User in `docker` group (or use `sudo` for docker).
- bash available (`capture.sh` auto-switches to bash if invoked differently).
- Access to relevant repos/services (OpenWebUI, Claude CLI).

## Key locations
- Bookkeeping: `/home/zaks/bookkeeping`
- Snapshots: `/home/zaks/bookkeeping/snapshots`
- Logs: `/home/zaks/bookkeeping/logs` (`capture.log`, `cron.log`)
- Config copies: `/home/zaks/bookkeeping/configs`
- Docs: `/home/zaks/bookkeeping/docs`

## Common commands
- Run snapshot: `cd /home/zaks/bookkeeping && make snapshot`
- Tail capture log: `make logs`
- Health checks: `make health` (checks Claude API 8090, OpenWebUI 3000, vLLM 8000, ZakOps API 8080, RAG REST 8052, compose ps; edit `scripts/health.sh` as services change)
- Cron schedule: `crontab -l` (10-minute snapshot)

## Services (summary)
- Claude Code API: http://localhost:8090 (systemd: `claude-code-api`)
- OpenWebUI: http://localhost:3000 (fill in start/stop/logs in service catalog)
- Docker: `docker ps`, see `snapshots/docker-*.txt` for ports/networks
- Post-move checklist: `docs/POST-MOVE-CHECKLIST.md`

## Notes on secrets
- Secrets/keys/.env are excluded by design. Keep them outside git and load via env files or systemd `EnvironmentFile`.

## Next steps
- Read `docs/SERVICE-CATALOG.md` and `docs/RUNBOOKS.md`.
- Update catalog entries with real start/stop commands, data paths, log paths.
- Add health checks in `scripts/health.sh` for each critical service.
