#!/usr/bin/env bash
set -euo pipefail
trap 'exit 0' PIPE

ts="$(date -Is)"
echo "== ZakOps Email Runner Audit =="
echo "timestamp=$ts"
echo

echo "-- System cron (/etc/cron.d) candidates --"
ls -1 /etc/cron.d 2>/dev/null | sed 's/^/  - /' || true
echo
for f in /etc/cron.d/*; do
  [ -f "$f" ] || continue
  if rg -n -i "email|gmail|imap|triage|ingest|sync_acquisition_emails|email_ingestion" "$f" >/dev/null 2>&1; then
    echo "### $f"
    sed -n '1,200p' "$f"
    echo
  fi
done

echo "-- User crontabs --"
for u in root zaks; do
  echo "### crontab -l ($u)"
  if crontab -l -u "$u" 2>/dev/null; then
    true
  else
    echo "(no crontab or insufficient permissions)"
  fi
  echo
done

echo "-- systemd timers (system) --"
systemctl list-timers --all 2>/dev/null | rg -i "email|gmail|triage|ingest|zakops" || true
echo

echo "-- systemd timers (user: zaks) --"
sudo -u zaks systemctl --user list-timers --all 2>/dev/null | rg -i "email|gmail|triage|ingest|zakops" || true
echo

echo "-- Running processes (grep) --"
ps aux | rg -i "email_triage_agent|zakops-email-triage|sync_acquisition_emails|email_ingestion|gmail" || true
echo

echo "== End audit =="
