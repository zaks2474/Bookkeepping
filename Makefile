SHELL := /bin/bash

ORCH_VENV ?= /home/zaks/.venvs/zakops-orchestration
ORCH_PY := $(ORCH_VENV)/bin/python
TEMPORAL_COMPOSE := /home/zaks/Zaks-llm/docker-compose.temporal.yml
N8N_COMPOSE := /home/zaks/Zaks-llm/docker-compose.n8n.yml

.PHONY: snapshot logs health preflight help triage-run triage-test triage-status triage-logs triage-eval triage-eval-3h audit-email-runners \
	orchestration-deps orchestration-audit \
	temporal-up temporal-down temporal-logs temporal-worker temporal-run-once temporal-schedules temporal-schedules-enable temporal-schedules-disable temporal-status \
	n8n-up n8n-down n8n-logs

help:
	@echo "Common tasks:"
	@echo "  make snapshot   - run capture.sh and refresh snapshots"
	@echo "  make logs       - tail capture log"
	@echo "  make health     - run quick health checks (customize script)"
	@echo "  make preflight  - scan repo for secret-like patterns"
	@echo "  make triage-eval - generate EMAIL_TRIAGE_EVAL_REPORT.md"
	@echo "  make orchestration-deps - create venv + install Temporal/LangGraph deps"
	@echo "  make temporal-up/down   - start/stop Temporal stack"
	@echo "  make temporal-worker    - run Temporal worker (foreground)"
	@echo "  make temporal-run-once  - trigger triage+controller once"
	@echo "  make temporal-schedules - create/update schedules (paused-on-create)"
	@echo "  make temporal-schedules-enable/disable - unpause/pause schedules"
	@echo "  make orchestration-audit - assert no dual scheduling"
	@echo "  make n8n-up/down/logs - start/stop/tail n8n (optional)"

snapshot:
	@bash capture.sh

logs:
	@tail -n 50 logs/capture.log

health:
	@bash scripts/health.sh

preflight:
	@python3 /home/zaks/scripts/zakops_secret_scan.py /home/zaks/bookkeeping

triage-run:
	@sudo -u zaks bash -lc 'cd /home/zaks/bookkeeping/scripts && python3 -m email_triage_agent.run_once'

triage-test:
	@cd /home/zaks/bookkeeping/scripts && ( test -x '$(ORCH_PY)' && '$(ORCH_PY)' -m unittest discover -s email_triage_agent/tests -v || python3 -m unittest discover -s email_triage_agent/tests -v )

triage-status:
	@sudo systemctl status zakops-email-triage.timer zakops-email-triage.service --no-pager || true

triage-logs:
	@sudo journalctl -u zakops-email-triage.service -n 200 --no-pager || true

triage-eval:
	@cd /home/zaks/bookkeeping/scripts && ( test -x '$(ORCH_PY)' && '$(ORCH_PY)' -m email_triage_agent.eval_triage || python3 -m email_triage_agent.eval_triage )

triage-eval-3h:
	@cd /home/zaks/bookkeeping/scripts && ( test -x '$(ORCH_PY)' && '$(ORCH_PY)' -m email_triage_agent.eval_3h_hardening report || python3 -m email_triage_agent.eval_3h_hardening report )

audit-email-runners:
	@bash scripts/audit_email_runners.sh

orchestration-deps:
	@sudo -u zaks bash -lc "test -x '$(ORCH_PY)' || python3 -m venv --system-site-packages '$(ORCH_VENV)'"
	@sudo -u zaks bash -lc "'$(ORCH_PY)' -m pip install -r /home/zaks/bookkeeping/requirements-orchestration.txt"

orchestration-audit:
	@bash scripts/audit_email_runners.sh
	@bash scripts/orchestration_audit.sh

temporal-up:
	@docker compose -f '$(TEMPORAL_COMPOSE)' up -d
	@echo "Temporal UI: http://localhost:8233"

temporal-down:
	@docker compose -f '$(TEMPORAL_COMPOSE)' down

temporal-logs:
	@docker compose -f '$(TEMPORAL_COMPOSE)' logs -f --tail=200

temporal-worker: orchestration-deps
	@sudo -u zaks bash -lc "cd /home/zaks/scripts && '$(ORCH_PY)' -m temporal_worker.worker"

temporal-run-once: orchestration-deps
	@sudo -u zaks bash -lc "cd /home/zaks/scripts && '$(ORCH_PY)' -m temporal_worker.schedules run-once all"

temporal-schedules: orchestration-deps
	@sudo -u zaks bash -lc "cd /home/zaks/scripts && '$(ORCH_PY)' -m temporal_worker.schedules upsert --paused-on-create"

temporal-schedules-enable: orchestration-deps
	@sudo -u zaks bash -lc "cd /home/zaks/scripts && '$(ORCH_PY)' -m temporal_worker.schedules unpause"

temporal-schedules-disable: orchestration-deps
	@sudo -u zaks bash -lc "cd /home/zaks/scripts && '$(ORCH_PY)' -m temporal_worker.schedules pause"

temporal-status: orchestration-deps
	@sudo -u zaks bash -lc "cd /home/zaks/scripts && '$(ORCH_PY)' -m temporal_worker.schedules list" || true
	@sudo systemctl status zakops-email-triage.timer zakops-deal-lifecycle-controller.timer --no-pager || true

n8n-up:
	@docker compose -f '$(N8N_COMPOSE)' up -d
	@echo "n8n UI: http://localhost:5678"

n8n-down:
	@docker compose -f '$(N8N_COMPOSE)' down

n8n-logs:
	@docker compose -f '$(N8N_COMPOSE)' logs -f --tail=200
