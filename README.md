# Bookkeeping & Ops Index (start here)

Single entry point for this environment. Everything else is linked from here. Secrets are intentionally excluded (keys/tokens/.env/etc.).

## Quick links
- Service catalog: `docs/SERVICE-CATALOG.md` (ports, start/stop, env files, volumes, logs)
- Runbooks: `docs/RUNBOOKS.md` (common tasks)
- Onboarding: `docs/ONBOARDING.md` (orientation and commands)
- Change log: `CHANGES.md` (record every notable change)
- Health checks: `scripts/health.sh` (`make health`)
- Snapshots: `snapshots/` (packages, cron, systemd, Docker, etc.)
- Config copies: `configs/` (safe, non-secret)
- Logs: `logs/` (`capture.log`, `cron.log`; git-ignored)

## Standards
- No secrets in repo: `.env*`, keys, tokens, creds stay outside git (see `.gitignore`).
- Log every operational change:
  - Append to `CHANGES.md` with date + summary/why.
  - Keep command outputs in `logs/` if relevant.
- Use provided scripts:
  - Snapshots: `make snapshot` (runs `capture.sh`)
  - Health: `make health`
  - Logs: `make logs`
- Keep docs current: when services/env files/ports change, update `docs/SERVICE-CATALOG.md` and runbooks.
- Before pushing: review for secrets; ensure change noted in `CHANGES.md`.

## Before you push (checklist)
- `make snapshot` and ensure `snapshots/` looks sane.
- Run `make health` and resolve FAILs if services should be up.
- Update `CHANGES.md` for any edits.
- Update `docs/SERVICE-CATALOG.md` if ports/commands/env files changed.
- Confirm no secrets in git (check `.env`, keys, tokens stayed out).

## What is excluded
- SSH private keys, API tokens, cloud creds, `.env*`, `id_*`, `*.key`, `*.pem`, `.aws/`, `.azure/` (see `.gitignore`).

## How to run
```bash
cd /home/zaks/bookkeeping
make snapshot        # refresh snapshots
make health          # check key services
make logs            # tail capture log
```

## Automation
- Cron: `*/10 * * * * /home/zaks/bookkeeping/capture.sh >> /home/zaks/bookkeeping/logs/cron.log 2>&1`
- Logs from automation land in `logs/` (git-ignored).

## Docker snapshots captured
- `docker-info.txt`, `docker-containers.txt`, `docker-containers-ports.txt`, `docker-ports.txt`, `docker-images.txt`, `docker-volumes.txt`, `docker-networks.txt`, `docker-networks-detail.txt`, `docker-compose.txt` (permission errors are recorded if Docker access is restricted).

## If you add/modify services
1) Update `docs/SERVICE-CATALOG.md` (ports, start/stop, env files, volumes, logs).
2) Add/adjust runbook steps in `docs/RUNBOOKS.md`.
3) Add/change health checks in `scripts/health.sh`.
4) Record the change in `CHANGES.md`.
