#!/usr/bin/env bash
set -euo pipefail

echo "== Health checks =="

run_check() {
  local name="$1"
  shift
  local cmd="$*"
  echo "-- ${name}"
  if eval "${cmd}"; then
    echo "OK"
  else
    echo "FAIL"
  fi
  echo
}

checks=(
  "Claude API (8090)|curl -fsS --max-time 3 http://localhost:8090/health"
  "Claude API service (systemd)|systemctl is-active --quiet claude-code-api"
  "OpenWebUI (3000)|curl -fsS --max-time 3 http://localhost:3000 || curl -fsS --max-time 3 http://localhost:3000/health"
  "vLLM Qwen (8000 models)|curl -fsS --max-time 3 http://localhost:8000/v1/models"
  "ZakOps API (8080)|curl -fsS --max-time 3 http://localhost:8080/health"
  "RAG REST API (8052)|curl -fsS --max-time 3 http://localhost:8052/"
  "Docker daemon access|docker info >/dev/null"
)

for entry in "${checks[@]}"; do
  IFS="|" read -r name cmd <<<"${entry}"
  run_check "${name}" "${cmd}"
done

# Optional: show compose status if available
if command -v docker >/dev/null && [ -d "/home/zaks/Zaks-llm" ]; then
  echo "-- docker compose ps (Zaks-llm)"
  if (cd /home/zaks/Zaks-llm && docker compose ps); then
    echo "OK"
  else
    echo "FAIL (docker ps/permissions?)"
  fi
  echo
fi
