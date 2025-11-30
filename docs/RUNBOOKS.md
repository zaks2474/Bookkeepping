# Runbooks

Short, task-focused instructions. Fill in blanks and add more tasks as needed.

## Restart Claude Code API
1) `sudo systemctl restart claude-code-api`
2) Verify: `curl -fsS http://localhost:8090/health`
3) Check logs: `journalctl -u claude-code-api -n 100`

## Refresh snapshots manually
1) `cd /home/zaks/bookkeeping`
2) `make snapshot`
3) Review `snapshots/` and `logs/capture.log`

## Check Docker stack health
1) `docker ps`
2) `docker compose ls` (if compose stacks)
3) Ports: `cat snapshots/docker-ports.txt`
4) Networks: `cat snapshots/docker-networks-detail.txt`
5) Health: `cd /home/zaks/bookkeeping && make health` (checks Claude API 8090, OpenWebUI 3000, vLLM 8000, ZakOps API 8080, RAG REST 8052; compose ps)

## Add a new service entry to catalog
1) Edit `docs/SERVICE-CATALOG.md`
2) Add name, port, start/stop, config path, data path, logs, notes

## After moving networks (IP changed)
1) `cd /home/zaks/bookkeeping && make health`
2) `make snapshot`
3) Update allowlists/firewall/OAuth/webhooks with new public IP if applicable
4) Log the change in `CHANGES.md`
5) See `docs/POST-MOVE-CHECKLIST.md` for full list

## Add/adjust cron automation
1) Edit with `crontab -e`
2) Confirm with `crontab -l`
3) Ensure log path in `bookkeeping/logs/cron.log`

## Add new MCP or tool
1) Document location/config in `docs/SERVICE-CATALOG.md`
2) If code/config is tracked, place non-secret parts under `bookkeeping/configs/` or note paths
