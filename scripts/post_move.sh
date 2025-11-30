#!/usr/bin/env bash
# Post-move automation: run once per boot to capture health/snapshot and record new IP.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
LOG_FILE="${LOG_DIR}/post-move.log"
STAMP_FILE="${LOG_DIR}/post-move.stamp"

mkdir -p "${LOG_DIR}"

# Run at most once per day
if [ -f "${STAMP_FILE}" ] && find "${STAMP_FILE}" -mmin -1440 -print -quit | grep -q .; then
  exit 0
fi

{
  echo "=== Post-move run $(date -Is) ==="
  echo "Public IP:"
  curl -fsS ifconfig.me || echo "unable to fetch public IP"
  echo

  cd "${ROOT_DIR}"
  echo "-- make health --"
  if make health; then
    echo "health: OK"
  else
    echo "health: FAIL (see above)"
  fi
  echo

  echo "-- make snapshot --"
  if make snapshot; then
    echo "snapshot: OK"
  else
    echo "snapshot: FAIL (see above)"
  fi
  echo

  echo "=== End run ==="
} >> "${LOG_FILE}" 2>&1

touch "${STAMP_FILE}"
