SHELL := /bin/bash

.PHONY: snapshot logs health help

help:
	@echo "Common tasks:"
	@echo "  make snapshot   - run capture.sh and refresh snapshots"
	@echo "  make logs       - tail capture log"
	@echo "  make health     - run quick health checks (customize script)"

snapshot:
	@bash capture.sh

logs:
	@tail -n 50 logs/capture.log

health:
	@bash scripts/health.sh
