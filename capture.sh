#!/usr/bin/env bash
# Ensure we re-exec with bash if invoked via sh/dash
if [ -z "${BASH_VERSION:-}" ]; then
  exec /usr/bin/env bash "$0" "$@"
fi

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SNAP_DIR="${SCRIPT_DIR}/snapshots"
CONF_DIR="${SCRIPT_DIR}/configs"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/capture.log"

mkdir -p "${SNAP_DIR}" "${CONF_DIR}"/{systemd,scripts,mcp,docker} "${LOG_DIR}"

log() {
  local level="${1}"; shift
  local msg="$*"
  local ts
  ts="$(date -Is)"
  printf "[%s] %s: %s\n" "${ts}" "${level}" "${msg}" | tee -a "${LOG_FILE}" >/dev/null
}

capture_cmd() {
  local label="$1" outfile="$2"; shift 2
  {
    echo "== ${label} =="
    if "$@"; then
      :
    else
      echo "command unavailable or failed: $*"
    fi
  } >"${outfile}" 2>&1
  log "INFO" "Captured ${label} -> ${outfile}"
}

copy_if_exists() {
  local src="$1" dest="$2"
  if [ -f "${src}" ]; then
    if cp -p "${src}" "${dest}"; then
      log "INFO" "Copied $(basename "${src}") -> ${dest}"
    else
      log "WARN" "Could not copy ${src}"
    fi
  fi
}

log "INFO" "Starting capture"

# Snapshots
capture_cmd "System info" "${SNAP_DIR}/system-info.txt" bash -c "uname -a && echo && (lsb_release -a 2>/dev/null || true)"
capture_cmd "APT manual packages" "${SNAP_DIR}/apt-packages.txt" bash -c "command -v apt-mark >/dev/null && apt-mark showmanual | sort || false"
capture_cmd "Pip packages" "${SNAP_DIR}/pip-packages.txt" bash -c "command -v pip >/dev/null && pip list --format=freeze || false"
capture_cmd "NPM global packages" "${SNAP_DIR}/npm-packages.txt" bash -c "command -v npm >/dev/null && npm list -g --depth=0 || false"
capture_cmd "Cron jobs" "${SNAP_DIR}/cron.txt" bash -c "crontab -l 2>/dev/null || false"
capture_cmd "Systemd services (enabled)" "${SNAP_DIR}/systemd.txt" bash -c "command -v systemctl >/dev/null && systemctl list-unit-files --type=service --state=enabled 2>&1 || false"
capture_cmd "WSL distros" "${SNAP_DIR}/wsl.txt" bash -c "command -v wsl.exe >/dev/null && wsl.exe --list --verbose || false"
capture_cmd "Docker info" "${SNAP_DIR}/docker-info.txt" bash -c "command -v docker >/dev/null && docker info 2>&1 || false"
capture_cmd "Docker containers (all)" "${SNAP_DIR}/docker-containers.txt" bash -c "command -v docker >/dev/null && docker ps -a || false"
capture_cmd "Docker images" "${SNAP_DIR}/docker-images.txt" bash -c "command -v docker >/dev/null && docker images || false"
capture_cmd "Docker volumes" "${SNAP_DIR}/docker-volumes.txt" bash -c "command -v docker >/dev/null && docker volume ls || false"
capture_cmd "Docker networks" "${SNAP_DIR}/docker-networks.txt" bash -c "command -v docker >/dev/null && docker network ls || false"
capture_cmd "Docker compose projects" "${SNAP_DIR}/docker-compose.txt" bash -c "command -v docker >/dev/null && docker compose ls 2>/dev/null || false"
capture_cmd "Docker containers (ports view)" "${SNAP_DIR}/docker-containers-ports.txt" bash -c "command -v docker >/dev/null && docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}' || false"
capture_cmd "Docker port bindings" "${SNAP_DIR}/docker-ports.txt" bash -c '
  command -v docker >/dev/null || exit 0
  docker ps --format "{{.ID}} {{.Names}}" | while read -r id name; do
    echo "--- ${name} (${id})"
    docker port "${id}" || true
    echo
  done
'
capture_cmd "Docker networks (containers and IPs)" "${SNAP_DIR}/docker-networks-detail.txt" bash -c '
  command -v docker >/dev/null || exit 0
  nets=$(docker network ls --format "{{.ID}} {{.Name}} {{.Driver}}")
  if [ -z "${nets}" ]; then
    echo "no networks"
    exit 0
  fi
  echo "${nets}" | while read -r id name driver; do
    echo "=== ${name} (${id}) driver=${driver}"
    docker network inspect "${id}" --format "Containers: {{range $cid,$c := .Containers}}{{$c.Name}} {{$c.IPv4Address}} {{end}}" || true
    echo
  done
'

# Safe config copies (no secrets)
copy_if_exists "${HOME}/.bashrc" "${CONF_DIR}/bashrc"
copy_if_exists "${HOME}/.profile" "${CONF_DIR}/profile"
copy_if_exists "${HOME}/.gitconfig" "${CONF_DIR}/gitconfig"
copy_if_exists "${HOME}/.ssh/config" "${CONF_DIR}/ssh_config"

# Copy user systemd units (safe scope)
if [ -d "${HOME}/.config/systemd/user" ]; then
  find "${HOME}/.config/systemd/user" -maxdepth 1 -type f -name "*.service" -o -name "*.timer" | while IFS= read -r unit; do
    dest="${CONF_DIR}/systemd/$(basename "${unit}")"
    if cp -p "${unit}" "${dest}"; then
      log "INFO" "Copied systemd unit ${unit}"
    else
      log "WARN" "Could not copy systemd unit ${unit}"
    fi
  done
fi

# Copy global systemd unit for Claude API if present
if [ -f "/etc/systemd/system/claude-code-api.service" ]; then
  if cp -p "/etc/systemd/system/claude-code-api.service" "${CONF_DIR}/systemd/claude-code-api.service"; then
    log "INFO" "Copied systemd unit /etc/systemd/system/claude-code-api.service"
  else
    log "WARN" "Could not copy /etc/systemd/system/claude-code-api.service"
  fi
fi

# Copy scripts (excluding likely secret patterns)
if [ -d "${HOME}/scripts" ]; then
  find "${HOME}/scripts" -maxdepth 1 -type f \
    ! -name "*secret*" ! -name "*credential*" ! -name "*.env" ! -name "id_*" | while IFS= read -r script; do
      dest="${CONF_DIR}/scripts/$(basename "${script}")"
      if cp -p "${script}" "${dest}"; then
        log "INFO" "Copied script ${script}"
      else
        log "WARN" "Could not copy script ${script}"
      fi
    done
fi

# Copy docker-compose files for reference (env files not copied)
if [ -f "/home/zaks/Zaks-llm/docker-compose.yml" ]; then
  if cp -p "/home/zaks/Zaks-llm/docker-compose.yml" "${CONF_DIR}/docker/Zaks-llm.docker-compose.yml"; then
    log "INFO" "Copied docker-compose.yml for Zaks-llm"
  else
    log "WARN" "Could not copy docker-compose.yml for Zaks-llm"
  fi
fi

if [ -f "/home/zaks/google_workspace_mcp_tmp/docker-compose.yml" ]; then
  if cp -p "/home/zaks/google_workspace_mcp_tmp/docker-compose.yml" "${CONF_DIR}/docker/google_workspace_mcp_tmp.docker-compose.yml"; then
    log "INFO" "Copied docker-compose.yml for google_workspace_mcp_tmp"
  else
    log "WARN" "Could not copy docker-compose.yml for google_workspace_mcp_tmp"
  fi
fi

log "INFO" "Capture complete"
