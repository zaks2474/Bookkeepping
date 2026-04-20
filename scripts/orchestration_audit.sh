#!/usr/bin/env bash
set -euo pipefail

ORCH_VENV="${ORCH_VENV:-/home/zaks/.venvs/zakops-orchestration}"
ORCH_PY="${ORCH_PY:-$ORCH_VENV/bin/python}"

echo "== ZakOps Orchestration Audit =="

triage_enabled=0
controller_enabled=0
if systemctl is-enabled --quiet zakops-email-triage.timer 2>/dev/null; then
  triage_enabled=1
fi
if systemctl is-enabled --quiet zakops-deal-lifecycle-controller.timer 2>/dev/null; then
  controller_enabled=1
fi

echo "systemd: zakops-email-triage.timer enabled=$triage_enabled"
echo "systemd: zakops-deal-lifecycle-controller.timer enabled=$controller_enabled"

temporal_present=0
if ss -tln 2>/dev/null | rg -q ":7233\\b"; then
  temporal_present=1
fi
echo "temporal: port_7233_listening=$temporal_present"

temporal_schedules_active=0
if [[ "$temporal_present" -eq 1 && -x "$ORCH_PY" ]]; then
  set +e
  schedules="$("$ORCH_PY" -m temporal_worker.schedules list 2>/dev/null)"
  rc=$?
  set -e
  if [[ "$rc" -eq 0 ]]; then
    if echo "$schedules" | rg -q "zakops-email-triage-hourly|zakops-deal-lifecycle-controller-hourly"; then
      if echo "$schedules" | rg -q "paused=False"; then
        temporal_schedules_active=1
      fi
    fi
  fi
fi
echo "temporal: zakops_schedules_active=$temporal_schedules_active"

if [[ "$temporal_schedules_active" -eq 1 && ( "$triage_enabled" -eq 1 || "$controller_enabled" -eq 1 ) ]]; then
  echo "ERROR: dual scheduling detected (systemd timers enabled + Temporal schedules active)."
  echo "Fix: disable systemd timers OR pause Temporal schedules before proceeding."
  exit 2
fi

echo "OK: no dual scheduling detected."
