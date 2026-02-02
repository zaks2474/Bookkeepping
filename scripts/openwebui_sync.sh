#!/usr/bin/env bash
set -euo pipefail

CANDIDATE_DBS=(
  "/var/lib/docker/volumes/zaks-llm_open-webui/_data/webui.db"
  "/var/lib/docker/volumes/open-webui/_data/webui.db"
  "/var/lib/docker/volumes/zaks_open-webui/_data/webui.db"
)
DEST_DIR="/home/zaks/backups/openwebui"
DEST_LATEST_LINK="${DEST_DIR}/webui_latest.db"
LOG_DIR="/home/zaks/bookkeeping/logs"

mkdir -p "${DEST_DIR}" "${LOG_DIR}"

LEDGER_WRITER="/home/zaks/bookkeeping/scripts/run_ledger.py"
LEDGER_PATH="${ZAKOPS_RUN_LEDGER_PATH:-/home/zaks/logs/run-ledger.jsonl}"
RUN_TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ID="${RUN_TS}_openwebui_sync_${$}"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
START_EPOCH="$(date +%s)"
SKIPPED_REASON=""
DEST_DB=""
DELETED_COUNT="0"

on_exit() {
  set +e
  local exit_code=$?
  local ended_at
  ended_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local end_epoch
  end_epoch="$(date +%s)"
  local duration_seconds=$(( end_epoch - START_EPOCH ))

  local status="success"
  local -a errors=()
  if [ -n "${SKIPPED_REASON}" ]; then
    status="skipped"
    errors+=("${SKIPPED_REASON}")
  elif [ "${exit_code}" -eq 0 ]; then
    status="success"
  else
    status="fail"
    errors+=("exit_code_${exit_code}")
  fi

  local size_bytes=0
  if [ -n "${DEST_DB}" ] && [ -f "${DEST_DB}" ]; then
    size_bytes="$(stat -c%s "${DEST_DB}" 2>/dev/null || echo 0)"
  fi

  if [ -x "${LEDGER_WRITER}" ]; then
    ledger_args=(
      python3 "${LEDGER_WRITER}"
      --ledger-path "${LEDGER_PATH}"
      --component "openwebui_sync"
      --run-id "${RUN_ID}"
      --status "${status}"
      --started-at "${STARTED_AT}"
      --ended-at "${ended_at}"
      --artifact "${LOG_DIR}/openwebui-sync.log"
      --metric "exit_code=${exit_code}"
      --metric "duration_seconds=${duration_seconds}"
      --metric "db_size_bytes=${size_bytes}"
      --metric "deleted_old_backups=${DELETED_COUNT}"
    )
    if [ -n "${SRC_DB:-}" ]; then
      ledger_args+=(--correlation "src_db=${SRC_DB}")
    fi
    if [ -n "${ZAKOPS_CORRELATION_ID:-}" ]; then ledger_args+=(--correlation "correlation_id=${ZAKOPS_CORRELATION_ID}"); fi
    if [ -n "${ZAKOPS_PARENT_RUN_ID:-}" ]; then ledger_args+=(--correlation "parent_run_id=${ZAKOPS_PARENT_RUN_ID}"); fi
    if [ -n "${DEST_DB}" ]; then
      ledger_args+=(--artifact "${DEST_DB}" --correlation "dest_db=${DEST_DB}")
    fi
    for err in "${errors[@]}"; do
      ledger_args+=(--error "${err}")
    done
    "${ledger_args[@]}" >/dev/null 2>&1 || true
  fi
}

trap on_exit EXIT

SRC_DB=""
for candidate in "${CANDIDATE_DBS[@]}"; do
  if [ -f "${candidate}" ]; then
    SRC_DB="${candidate}"
    break
  fi
done

if [ -z "${SRC_DB}" ]; then
  echo "$(date -Is) WARN: OpenWebUI database not found under /var/lib/docker/volumes/*open-webui*/_data/webui.db" >> "${LOG_DIR}/openwebui-sync.log"
  SKIPPED_REASON="db_not_found"
  exit 0
fi

STAMP="$(date +%Y-%m-%d_%H%M%S)"
DEST_DB="${DEST_DIR}/webui_live_${STAMP}.db"
TMP_DB="${DEST_DB}.tmp"

export SRC_DB TMP_DB
python3 - <<'PY'
import os
import sqlite3
import sys

src = os.environ["SRC_DB"]
tmp = os.environ["TMP_DB"]

try:
    src_conn = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    dst_conn = sqlite3.connect(tmp)
    src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
except Exception as exc:
    print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
    raise
PY

mv -f "${TMP_DB}" "${DEST_DB}"
if [ "$(id -u)" -eq 0 ]; then
  chown zaks:zaks "${DEST_DB}"
fi
chmod 600 "${DEST_DB}"
ln -sfn "${DEST_DB}" "${DEST_LATEST_LINK}"

DELETED_COUNT="$(find "${DEST_DIR}" -maxdepth 1 -type f -name "webui_live_*.db" -mtime +30 -delete -print 2>/dev/null | wc -l || true)"
if [ "${DELETED_COUNT}" != "0" ]; then
  echo "$(date -Is) INFO: deleted ${DELETED_COUNT} old OpenWebUI DB backups (>30d)" >> "${LOG_DIR}/openwebui-sync.log"
fi

echo "$(date -Is) INFO: backed up OpenWebUI DB ${SRC_DB} -> ${DEST_DB}" >> "${LOG_DIR}/openwebui-sync.log"
