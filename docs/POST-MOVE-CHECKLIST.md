# Post-Move Checklist (IP/Network Change)

Use this after you arrive and reconnect on the new network.

## Immediate checks
1) Verify connectivity:
   - `ping -c 3 8.8.8.8` (basic reachability)
   - `curl ifconfig.me` (note new public IP)
2) Run local health:
   - `cd /home/zaks/bookkeeping && make health`
   - `cd /home/zaks/bookkeeping && make snapshot` (captures post-move state)
3) Check Docker:
   - `docker ps` (if you have daemon access)
   - `cd /home/zaks/Zaks-llm && docker compose ps` (if applicable)
4) Review automation log (runs at reboot): `tail -n 50 /home/zaks/bookkeeping/logs/post-move.log`

## Update allowlists / IP-bound settings
If you use IP allowlists (SSH, firewall rules, API allowlists, OAuth):
- Update any SSH/firewall/IP allowlist to include the new public IP.
- Update OAuth redirect/base URLs if they were tied to the old IP.
- Update external webhooks/integrations that target your previous IP/host.
- If you rely on a static egress, consider using VPN to keep a stable IP.

## Service-specific spot checks
- Claude API: `curl -fsS http://localhost:8090/health`
- OpenWebUI: `curl -fsS http://localhost:3000 || curl -fsS http://localhost:3000/health`
- vLLM: `curl -fsS http://localhost:8000/v1/models`
- ZakOps API: `curl -fsS http://localhost:8080/health`
- RAG REST: `curl -fsS http://localhost:8052/`
- (Optional) External reachability: from another machine, confirm any intentionally exposed ports/NAT rules.

## DNS/hostname hygiene
- Prefer hostnames (service names inside Docker, `localhost`, or VPN DNS) rather than hardcoding public IPs.
- Avoid binding services to specific IPs; `0.0.0.0` for local use is fine, but secure before exposing externally.

## Logging and documentation
- Record the move and new IP in `CHANGES.md` (date, new IP, any allowlist updates).
- Keep `logs/capture.log` and `logs/cron.log` for evidence if something fails.
- If you adjust services/ports/configs, update `docs/SERVICE-CATALOG.md` and `scripts/health.sh` if endpoints change.

## Optional hardening
- If exposing anything externally, ensure firewall/NAT rules are explicit and least-privilege.
- Consider VPN for stable egress and remote access; avoid exposing admin surfaces directly.
