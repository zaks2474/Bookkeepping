# RUNBOOK — Temporal Cutover (ZakOps Local Lab)

This runbook replaces the systemd timer scheduling for:
- `zakops-email-triage.timer`
- `zakops-deal-lifecycle-controller.timer`

with **Temporal schedules + a local Temporal worker**, without rewriting the underlying business logic scripts.

## Prereqs

- Docker running on the host
- Temporal stack compose file: `/home/zaks/Zaks-llm/docker-compose.temporal.yml`
- Orchestration venv: `/home/zaks/.venvs/zakops-orchestration` (created by `make orchestration-deps`)

## Start Temporal

From `/home/zaks/bookkeeping`:

- `make temporal-up`
- Temporal UI: `http://localhost:8233`

## Install worker deps

- `make orchestration-deps`

## Start worker (foreground)

Run in a dedicated terminal/tmux pane:

- `make temporal-worker`

Worker logs:
- `/home/zaks/logs/temporal_worker/worker_stdout.log`
- Per-run logs: `/home/zaks/logs/temporal_worker/email_triage_*.log`, `/home/zaks/logs/temporal_worker/deal_controller_*.log`

## Manual validation (no schedules yet)

- `make temporal-run-once`
- Confirm new per-run logs show successful completion.

## Create schedules (paused-on-create)

- `make temporal-schedules`
- `make temporal-status` (should show both schedules `paused=True`)

At this point, schedules exist but are paused; **systemd timers may remain enabled**.

## Cutover (NO dual scheduling)

1) Pause schedules (safety):
   - `make temporal-schedules-disable`
2) Disable systemd timers:
   - `sudo systemctl disable --now zakops-email-triage.timer zakops-deal-lifecycle-controller.timer`
3) Unpause Temporal schedules:
   - `make temporal-schedules-enable`
4) Verify invariant:
   - `make orchestration-audit`
   - `make temporal-status` (should show both schedules `paused=False`)

## Post-cutover audit

- `make orchestration-audit` (no dual scheduling, systemd timers disabled)
- `make temporal-status` (schedules listed and unpaused)
- Tail Temporal worker logs as needed: `tail -n 20 /home/zaks/logs/temporal_worker/worker_stdout.log`

## Rollback to systemd

1) Pause Temporal schedules:
   - `make temporal-schedules-disable`
2) Stop the worker (Ctrl+C in the worker terminal)
3) Re-enable systemd timers:
   - `sudo systemctl enable --now zakops-email-triage.timer zakops-deal-lifecycle-controller.timer`
4) Verify:
   - `make orchestration-audit`

## Stop Temporal

- `make temporal-down`
