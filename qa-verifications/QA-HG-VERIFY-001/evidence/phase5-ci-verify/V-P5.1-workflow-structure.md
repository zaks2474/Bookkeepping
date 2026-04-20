# V-P5.1: GitHub Actions Workflow for Type-Sync

**Verification ID**: QA-HG-VERIFY-001-V2 / V-P5.1
**Date**: 2026-02-06T08:27Z
**Verdict**: FAIL (no dedicated type-sync workflow in CI)

## Findings

### Workflow Files Found
Two GitHub Actions workflows exist in `/home/zaks/zakops-agent-api/.github/workflows/`:

1. **ci.yml** - Main CI pipeline
2. **deploy.yaml** - Docker Hub build/push pipeline

### ci.yml Structure Analysis

**YAML validity**: PASS (validated with `python3 yaml.safe_load()`)

Structure:
```
name: CI
on:
  push: [main, develop]
  pull_request: [main]
concurrency: cancel-in-progress per workflow+ref

jobs:
  changes:     # dorny/paths-filter to detect changed paths
  agent-api:   # Python lint (ruff), type check (mypy), test (pytest)
  dashboard:   # Node.js lint, type-check, build, test
  contracts:   # OpenAPI validation via @redocly/cli
  gates:       # Aggregate pass/fail check (push to main only)
```

### deploy.yaml Structure Analysis

**YAML validity**: PASS (validated with `python3 yaml.safe_load()`)

Structure:
```
name: Build and push to Docker Hub
on:
  push: [main]
  pull_request: [main]

jobs:
  build-and-push: # checkout, make docker-build-env, push to Docker Hub
```

### Type-Sync in CI

**No dedicated type-sync workflow or CI step exists.**

- `sync-types` is defined ONLY in `/home/zaks/Makefile` (line 15-24)
- It is a local developer command: `make sync-types`
- It fetches from the **live backend** (`curl -sf $(BACKEND_API)/openapi.json`)
- It is NOT referenced in any GitHub Actions workflow file
- The CI `dashboard` job does `npm run build` and `npm run type-check` but does NOT run `sync-types`
- The CI `contracts` job validates the committed OpenAPI spec but does NOT run codegen

### Evidence Commands
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"  # VALID YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yaml'))"  # VALID YAML
grep -r 'sync-types\|type-sync' .github/  # No matches
```

## Conclusion
The CI pipeline has no type-sync step. Type synchronization is a manual local operation only.
