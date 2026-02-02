# Bookkeeping

Operational infrastructure for ZakOps: snapshots, logs, docs, change tracking.

## Critical Files
- **CHANGES.md** — Authoritative change log. ALL changes across ALL repos go here.
- **docs/ONBOARDING.md** — Session orientation (read at start of every session)
- **docs/SERVICE-CATALOG.md** — Full service inventory with start/stop/logs
- **docs/RUNBOOKS.md** — Step-by-step operational procedures

## Golden Commands
```bash
make snapshot      # Capture system state (docker, ports, processes)
make health        # Check all service health
make preflight     # Secret scan before commits
make logs          # Tail capture log
```

## Lab Loop
- Base: `labloop/`
- Tasks: `labloop/tasks/`
- Profiles: `labloop/profiles/`
- Create: `labloop/bin/labloop new <ID> --repo <DIR> --gate "<CMD>"`
- Run: `labloop/bin/labloop run <ID>`

## Structure
```
CHANGES.md          ← authoritative change log
configs/            ← config file copies
docs/               ← ONBOARDING, SERVICE-CATALOG, RUNBOOKS, etc.
labloop/            ← Lab Loop automation
logs/               ← capture.log, dashboard.log, cron.log
scripts/            ← capture.sh, health.sh, eval_runner.py, etc.
snapshots/          ← periodic system state captures
```

## Secrets Policy
This repo must NEVER contain secrets. Run `make preflight` before committing.
