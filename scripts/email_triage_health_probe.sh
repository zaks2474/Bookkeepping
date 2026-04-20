#!/bin/bash
# Email Triage Health Probe
# Runs every 60s via cron, checks 4 endpoints, logs results
# Phase: P8-02 (Operational Excellence Gate)

set -uo pipefail

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LOG_DIR="/home/zaks/bookkeeping/logs"
STATE_FILE="${LOG_DIR}/.triage_health_state"
ALERT_LOG="${LOG_DIR}/triage_alerts.log"

# Endpoint configuration
BACKEND_URL="http://localhost:8091"
BRIDGE_URL="http://localhost:8095"
DASHBOARD_URL="http://localhost:3003"

# Consecutive failure tracking
declare -A FAIL_COUNTS
if [[ -f "$STATE_FILE" ]]; then
    while IFS='=' read -r key val; do
        FAIL_COUNTS["$key"]="$val"
    done < "$STATE_FILE"
fi

check_endpoint() {
    local name="$1"
    local url="$2"
    local timeout="${3:-5}"
    local status
    local latency

    local start_ms=$(date +%s%N)
    status=$(curl -sf -o /dev/null -w "%{http_code}" --connect-timeout "$timeout" --max-time "$timeout" "$url" 2>/dev/null) || status="000"
    local end_ms=$(date +%s%N)
    latency=$(( (end_ms - start_ms) / 1000000 ))

    if [[ "$status" == "200" ]]; then
        FAIL_COUNTS["$name"]=0
        echo "${TIMESTAMP} [OK]   ${name}: ${status} (${latency}ms)"
    else
        local prev=${FAIL_COUNTS["$name"]:-0}
        FAIL_COUNTS["$name"]=$((prev + 1))
        echo "${TIMESTAMP} [FAIL] ${name}: ${status} (${latency}ms) [consecutive: ${FAIL_COUNTS[$name]}]"

        # Alert after 2 consecutive failures
        if [[ ${FAIL_COUNTS["$name"]} -ge 2 ]]; then
            echo "${TIMESTAMP} [ALERT] CRITICAL: ${name} down for ${FAIL_COUNTS[$name]} consecutive checks" >> "$ALERT_LOG"
        fi
    fi
}

check_queue_depth() {
    local response
    response=$(curl -sf "${BACKEND_URL}/api/quarantine?status=pending&limit=1" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        local count
        count=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total',d.get('count',len(d) if isinstance(d,list) else 0)))" 2>/dev/null) || count=0
        echo "${TIMESTAMP} [METRIC] queue_depth_pending: ${count}"
        if [[ "$count" -gt 50 ]]; then
            echo "${TIMESTAMP} [ALERT] CRITICAL: Queue depth ${count} > 50" >> "$ALERT_LOG"
        elif [[ "$count" -gt 20 ]]; then
            echo "${TIMESTAMP} [ALERT] WARNING: Queue depth ${count} > 20" >> "$ALERT_LOG"
        fi
    fi
}

check_kill_switch() {
    local response
    response=$(curl -sf "${BACKEND_URL}/api/admin/flags" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        local writes_enabled
        writes_enabled=$(echo "$response" | python3 -c "
import sys, json
flags = json.load(sys.stdin)
if isinstance(flags, list):
    for f in flags:
        if f.get('name') == 'email_triage_writes_enabled':
            print('true' if f.get('enabled') else 'false')
            sys.exit(0)
elif isinstance(flags, dict):
    for name, val in flags.items():
        if name == 'email_triage_writes_enabled':
            print('true' if val else 'false')
            sys.exit(0)
print('unknown')
" 2>/dev/null) || writes_enabled="unknown"

        if [[ "$writes_enabled" == "false" ]]; then
            echo "${TIMESTAMP} [ALERT] CRITICAL: Kill switch ACTIVATED — writes disabled" >> "$ALERT_LOG"
            echo "${TIMESTAMP} [KILL_SWITCH] ACTIVATED"
        else
            echo "${TIMESTAMP} [METRIC] kill_switch: OFF (writes enabled)"
        fi
    fi
}

# Run checks
echo "--- Probe ${TIMESTAMP} ---"
check_endpoint "backend_health" "${BACKEND_URL}/health"
check_endpoint "quarantine_api" "${BACKEND_URL}/api/quarantine?limit=1" 10
check_endpoint "bridge_health"  "${BRIDGE_URL}/health"
check_endpoint "dashboard"      "${DASHBOARD_URL}/quarantine" 10
check_queue_depth
check_kill_switch

# Persist failure counts
{
    for key in "${!FAIL_COUNTS[@]}"; do
        echo "${key}=${FAIL_COUNTS[$key]}"
    done
} > "$STATE_FILE"
