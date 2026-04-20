# Remediation: topology.env has stale DASHBOARD_ROOT

## What was broken
`artifacts/infra-awareness/evidence/topology/topology.env` sets:
```
export DASHBOARD_ROOT="/home/zaks/zakops-dashboard"
```
But the active dashboard (serving on port 3003) is at:
```
/home/zaks/zakops-agent-api/apps/dashboard
```

## Impact
- generate-preflight.sh sourced topology.env and used the wrong path
- tsc --noEmit ran against the wrong dashboard (which has test file errors)

## Fix Applied
- generate-preflight.sh: hardcoded correct path override after sourcing topology.env
- topology.env update deferred to Phase 4 (discover-topology.sh slim)

## Root Cause
Two dashboard directories exist. The V4 discover-topology.sh finds the older one first.
