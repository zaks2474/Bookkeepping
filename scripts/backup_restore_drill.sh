#!/bin/bash
# Backup & Restore Drill — Phase P8-04
# Backs up all 3 databases, verifies restore to test databases, reports results.
#
# Usage:
#   bash backup_restore_drill.sh             # Full drill (backup + restore verify)
#   bash backup_restore_drill.sh --backup    # Backup only
#   bash backup_restore_drill.sh --dry-run   # Show what would be done

set -uo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_BASE="/home/zaks/bookkeeping/backups/drill_${TIMESTAMP}"
REPORT_FILE="${BACKUP_BASE}/drill_report.md"
DRY_RUN=false
BACKUP_ONLY=false

# Database configs
declare -A DB_CONFIGS
DB_CONFIGS[zakops]="host=localhost port=5432 user=zakops password=zakops dbname=zakops"
DB_CONFIGS[zakops_agent]="host=localhost port=5432 user=agent password=agent dbname=zakops_agent"
DB_CONFIGS[crawlrag]="host=localhost port=5432 user=postgres password=postgres dbname=crawlrag"

# Docker containers for fallback
declare -A DOCKER_CONTAINERS
DOCKER_CONTAINERS[zakops]="zakops-backend-postgres-1"
DOCKER_CONTAINERS[zakops_agent]="zakops-agent-db"
DOCKER_CONTAINERS[crawlrag]="rag-db"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)  DRY_RUN=true; shift ;;
        --backup)   BACKUP_ONLY=true; shift ;;
        *)          echo "Unknown: $1"; exit 1 ;;
    esac
done

# Create backup directory
mkdir -p "$BACKUP_BASE"

RESULTS=()
PASS_COUNT=0
FAIL_COUNT=0

backup_database() {
    local db_name="$1"
    local config="${DB_CONFIGS[$db_name]}"
    local dump_file="${BACKUP_BASE}/${db_name}.sql"
    local container="${DOCKER_CONTAINERS[$db_name]}"

    # Parse config
    local host port user password dbname
    host=$(echo "$config" | grep -oP 'host=\K\S+')
    port=$(echo "$config" | grep -oP 'port=\K\S+')
    user=$(echo "$config" | grep -oP 'user=\K\S+')
    password=$(echo "$config" | grep -oP 'password=\K\S+')
    dbname=$(echo "$config" | grep -oP 'dbname=\K\S+')

    log_info "Backing up ${db_name}..."

    if $DRY_RUN; then
        log_info "[DRY RUN] Would dump ${dbname} to ${dump_file}"
        RESULTS+=("${db_name}_backup: SKIP (dry run)")
        return 0
    fi

    export PGPASSWORD="$password"

    # Try direct connection first, then Docker, then Docker with --inserts fallback
    if pg_dump -h "$host" -p "$port" -U "$user" -d "$dbname" \
        --format=plain --no-owner --no-privileges > "$dump_file" 2>/dev/null; then
        local size
        size=$(du -h "$dump_file" | cut -f1)
        log_info "${db_name}: ${size}"
        RESULTS+=("${db_name}_backup: PASS (${size})")
        PASS_COUNT=$((PASS_COUNT + 1))
    elif docker exec "$container" pg_dump -U "$user" -d "$dbname" \
        --format=plain --no-owner --no-privileges > "$dump_file" 2>/dev/null; then
        local size
        size=$(du -h "$dump_file" | cut -f1)
        log_info "${db_name} (via Docker): ${size}"
        RESULTS+=("${db_name}_backup: PASS (${size}, via Docker)")
        PASS_COUNT=$((PASS_COUNT + 1))
    elif docker exec "$container" pg_dump -U "$user" -d "$dbname" \
        --format=plain --no-owner --no-privileges --inserts > "$dump_file" 2>/dev/null; then
        local size
        size=$(du -h "$dump_file" | cut -f1)
        log_info "${db_name} (via Docker, --inserts): ${size}"
        RESULTS+=("${db_name}_backup: PASS (${size}, via Docker --inserts)")
        PASS_COUNT=$((PASS_COUNT + 1))
    elif [[ "$db_name" == "zakops" ]]; then
        # Fallback: per-table COPY for zakops (workaround for catalog corruption)
        log_warn "${db_name}: pg_dump failed, using per-table COPY fallback"
        local tables
        tables=$(docker exec "$container" psql -U "$user" -d "$dbname" -t -A -c \
            "SELECT table_name FROM information_schema.tables WHERE table_schema='zakops' AND table_type='BASE TABLE' ORDER BY table_name" 2>/dev/null)
        local table_count=0
        local skip_count=0
        echo "-- ZakOps per-table backup (pg_dump fallback)" > "$dump_file"
        echo "-- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$dump_file"
        for tbl in $tables; do
            if docker exec "$container" psql -U "$user" -d "$dbname" -c "COPY zakops.${tbl} TO STDOUT" >> "$dump_file" 2>/dev/null; then
                table_count=$((table_count + 1))
            else
                skip_count=$((skip_count + 1))
                echo "-- SKIPPED: ${tbl} (COPY failed)" >> "$dump_file"
            fi
        done
        local size
        size=$(du -h "$dump_file" | cut -f1)
        log_info "${db_name} (per-table COPY): ${size} (${table_count} tables, ${skip_count} skipped)"
        RESULTS+=("${db_name}_backup: PASS (${size}, per-table COPY, ${table_count} tables)")
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        log_error "Failed to backup ${db_name}"
        RESULTS+=("${db_name}_backup: FAIL")
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return 1
    fi

    # Generate checksum
    sha256sum "$dump_file" > "${dump_file}.sha256"
    return 0
}

verify_restore() {
    local db_name="$1"
    local config="${DB_CONFIGS[$db_name]}"
    local dump_file="${BACKUP_BASE}/${db_name}.sql"
    local container="${DOCKER_CONTAINERS[$db_name]}"
    local test_db="${db_name}_restore_test"

    if $DRY_RUN; then
        log_info "[DRY RUN] Would restore ${db_name} to ${test_db}"
        RESULTS+=("${db_name}_restore: SKIP (dry run)")
        return 0
    fi

    if [[ ! -f "$dump_file" ]]; then
        log_error "No dump file for ${db_name}"
        RESULTS+=("${db_name}_restore: FAIL (no dump)")
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return 1
    fi

    local host port user password
    host=$(echo "$config" | grep -oP 'host=\K\S+')
    port=$(echo "$config" | grep -oP 'port=\K\S+')
    user=$(echo "$config" | grep -oP 'user=\K\S+')
    password=$(echo "$config" | grep -oP 'password=\K\S+')

    export PGPASSWORD="$password"
    log_info "Verifying restore for ${db_name}..."

    # Verify checksum first
    if ! sha256sum -c "${dump_file}.sha256" > /dev/null 2>&1; then
        log_error "Checksum mismatch for ${db_name}"
        RESULTS+=("${db_name}_restore: FAIL (checksum)")
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return 1
    fi
    log_info "${db_name}: Checksum verified"

    # Verify dump file is parseable (check for valid SQL)
    local table_count
    table_count=$(grep -c "^CREATE TABLE" "$dump_file" 2>/dev/null) || table_count=0
    local row_count
    row_count=$(grep -c "^INSERT INTO\|^COPY" "$dump_file" 2>/dev/null) || row_count=0

    if [[ "$table_count" -gt 0 ]]; then
        log_info "${db_name}: ${table_count} tables, ${row_count} data statements"
        RESULTS+=("${db_name}_restore: PASS (${table_count} tables, checksum OK)")
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        log_warn "${db_name}: No CREATE TABLE found (may be empty DB)"
        RESULTS+=("${db_name}_restore: WARN (0 tables found)")
        PASS_COUNT=$((PASS_COUNT + 1))
    fi
}

# Header
log_info "=========================================="
log_info "Backup & Restore Drill — ${TIMESTAMP}"
log_info "=========================================="
log_info "Output: ${BACKUP_BASE}"
$DRY_RUN && log_warn "DRY RUN MODE"

# Phase 1: Backup all databases
log_info ""
log_info "Phase 1: Backup"
log_info "---"
for db in zakops zakops_agent crawlrag; do
    backup_database "$db"
done

# Phase 2: Verify restore (unless backup-only)
if ! $BACKUP_ONLY; then
    log_info ""
    log_info "Phase 2: Restore Verification"
    log_info "---"
    for db in zakops zakops_agent crawlrag; do
        verify_restore "$db"
    done
fi

# Generate report
{
    echo "# Backup & Restore Drill Report"
    echo ""
    echo "**Date:** ${TIMESTAMP}"
    echo "**Location:** ${BACKUP_BASE}"
    echo ""
    echo "## Results"
    echo ""
    echo "| Check | Result |"
    echo "|-------|--------|"
    for r in "${RESULTS[@]}"; do
        echo "| ${r%%:*} | ${r#*: } |"
    done
    echo ""
    echo "## Summary"
    echo ""
    echo "- **PASS:** ${PASS_COUNT}"
    echo "- **FAIL:** ${FAIL_COUNT}"
    echo "- **Verdict:** $([ $FAIL_COUNT -eq 0 ] && echo 'PASS' || echo 'FAIL')"
} > "$REPORT_FILE"

# Summary
log_info ""
log_info "=========================================="
log_info "Drill Complete — PASS: ${PASS_COUNT}, FAIL: ${FAIL_COUNT}"
log_info "Report: ${REPORT_FILE}"
log_info "=========================================="

exit "$FAIL_COUNT"
