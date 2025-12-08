#!/usr/bin/env bash
set -euo pipefail

SRC="/var/lib/docker/volumes/open-webui/_data/"
DEST_BASE="/home/zaks/DataRoom/08-ARCHIVE/openwebui-chats"
DATE_DIR="${DEST_BASE}/$(date +%Y-%m-%d)"
LATEST_LINK="${DEST_BASE}/latest"
LOG_DIR="/home/zaks/bookkeeping/logs"

mkdir -p "${DEST_BASE}" "${LOG_DIR}" "${DATE_DIR}"

if [ ! -d "${SRC}" ]; then
  echo "$(date -Is) WARN: source volume not found at ${SRC}" >> "${LOG_DIR}/openwebui-sync.log"
  exit 0
fi

rsync -a --delete "${SRC}" "${DATE_DIR}/"
ln -sfn "${DATE_DIR}" "${LATEST_LINK}"

echo "$(date -Is) INFO: synced OpenWebUI volume to ${DATE_DIR}" >> "${LOG_DIR}/openwebui-sync.log"
