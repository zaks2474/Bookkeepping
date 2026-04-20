#!/usr/bin/env bash
# QA-R4C-VERIFY-001 Watchdog — One-shot check
# Runs ~10 min after the scheduled cron job
# If Claude is already running the mission → log and exit
# If not running → launch it, then exit
# Self-removes from crontab after execution

LOG="/home/zaks/bookkeeping/logs/qa-r4c-watchdog.log"
MISSION="/home/zaks/bookkeeping/docs/QA-R4C-VERIFY-001.md"
MISSION_LOG="/home/zaks/bookkeeping/logs/qa-r4c-verify-001.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') — Watchdog triggered" >> "$LOG"

# Check if claude is running with this mission
if pgrep -f "QA-R4C-VERIFY-001" > /dev/null 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') — Claude is RUNNING the mission. Going back to sleep." >> "$LOG"
elif [ -f "$MISSION_LOG" ] && [ -s "$MISSION_LOG" ]; then
    # Log exists and is non-empty — check if it finished or is still going
    if pgrep -f "claude" > /dev/null 2>&1; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') — Claude process found and mission log exists. Assuming running. Going back to sleep." >> "$LOG"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') — Mission log exists but no Claude process. Checking if completed..." >> "$LOG"
        LINES=$(wc -l < "$MISSION_LOG" 2>/dev/null || echo "0")
        if [ "$LINES" -gt 50 ]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') — Mission log has $LINES lines. Looks completed. Going back to sleep." >> "$LOG"
        else
            echo "$(date '+%Y-%m-%d %H:%M:%S') — Mission log has only $LINES lines. Looks like it failed. Re-launching..." >> "$LOG"
            sudo claude --dangerously-skip-permissions "execute this mission \"$MISSION\"" >> "$MISSION_LOG" 2>&1 &
            echo "$(date '+%Y-%m-%d %H:%M:%S') — Re-launched Claude (PID: $!). Going back to sleep." >> "$LOG"
        fi
    fi
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') — No Claude process and no mission log. Cron job likely never fired. Launching now..." >> "$LOG"
    sudo claude --dangerously-skip-permissions "execute this mission \"$MISSION\"" > "$MISSION_LOG" 2>&1 &
    echo "$(date '+%Y-%m-%d %H:%M:%S') — Launched Claude (PID: $!). Going back to sleep." >> "$LOG"
fi

# Self-remove from crontab
crontab -l 2>/dev/null | grep -v 'qa-r4c-watchdog' | crontab -
echo "$(date '+%Y-%m-%d %H:%M:%S') — Watchdog self-removed from crontab. Done." >> "$LOG"
