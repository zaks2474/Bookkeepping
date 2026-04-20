# Acceptance Criteria: Phase 2 — MVP Build

## Definition of Done

The task is complete when ALL of the following are true:

### Functional Requirements

#### Contract Probes
- [ ] `gate_artifacts/deal_api_contract.json` exists and contains:
  - Deal API base path (discovered, not guessed)
  - Available endpoints and methods
  - Response schema samples
- [ ] `gate_artifacts/agent_api_contract.json` exists with `/agent/*` endpoints
- [ ] `gate_artifacts/repro_commands.sh` exists with example curl commands

#### Mocks Disabled
- [ ] `gate_artifacts/mocks_disabled_check.log` contains `MOCKS_DISABLED: PASSED`
- [ ] No mock fallback paths exercised during gate run
- [ ] `ALLOW_TOOL_MOCKS=false` enforced in test environment

#### Direct Tool Wiring
- [ ] `list_deals` executes against real Deal API :8090
- [ ] `get_deal` executes against real Deal API :8090
- [ ] `transition_deal` executes against real Deal API :8090
- [ ] `check_health` executes against real Deal API :8090

#### E2E HITL Lifecycle
- [ ] `gate_artifacts/deal_api_e2e_transition.json` contains `E2E_TRANSITION: PASSED`
- [ ] Workflow proves: invoke → `awaiting_approval` → approve → `completed`
- [ ] Deal API state verification (deal actually transitioned)
- [ ] Exactly-once semantics proven (no duplicate tool executions)

#### Cloudflare Routing
- [ ] `gate_artifacts/cloudflare_route_lint.log` contains `CLOUDFLARE_ROUTE_LINT: PASSED`
- [ ] Cloudflare config verified to route only to :8095
- [ ] :8090 (Deal API) is NOT exposed externally

### Quality Gates
- [ ] All Phase 1 gates still pass (BL-01 through BL-14)
- [ ] All unit tests pass (`pytest tests/`)
- [ ] No linting errors (`ruff check`)
- [ ] No type errors (`mypy`)

### Spec Compliance
- [ ] Deal API endpoint paths match discovered contract
- [ ] Agent API endpoints use canonical `/agent/*` prefix
- [ ] Status string `awaiting_approval` used (not `pending_approval`)
- [ ] Response status `completed` after successful approval

## Verification Steps

1. Run contract probe and verify Deal API discovery
2. Run gate with `ALLOW_TOOL_MOCKS=false` and verify no mocks triggered
3. Execute E2E HITL workflow and verify Deal API state change
4. Run Cloudflare config lint
5. Run full gate pack: `./scripts/bring_up_tests.sh`

## Gate Command

```bash
cd /home/zaks/zakops-backend && ./scripts/bring_up_tests.sh
```

This command must exit with code 0 for the task to pass.

## Required Artifacts (Phase 2)

| Artifact | PASS Marker |
|----------|-------------|
| `deal_api_contract.json` | Contract discovered |
| `agent_api_contract.json` | Endpoints validated |
| `repro_commands.sh` | Commands generated |
| `mocks_disabled_check.log` | `MOCKS_DISABLED: PASSED` |
| `deal_api_e2e_transition.json` | `E2E_TRANSITION: PASSED` |
| `cloudflare_route_lint.log` | `CLOUDFLARE_ROUTE_LINT: PASSED` |
