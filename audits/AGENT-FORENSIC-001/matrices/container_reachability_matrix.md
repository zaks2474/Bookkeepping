# Container Reachability Matrix
| From Container | Target URL | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|
| zakops-agent-api | http://host.docker.internal:8091/health | 200 OK | curl: not found | Fail (tooling missing) | evidence/phase0/11_container_reachability.txt |
| zakops-agent-api | http://host.docker.internal:8000/v1/v1/models | 200 OK + JSON | curl: not found | Fail (tooling missing) | evidence/phase0/11_container_reachability.txt |
