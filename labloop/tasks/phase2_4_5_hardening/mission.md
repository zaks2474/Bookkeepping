# Mission: Phase 2 (Remaining) + Phase 4 + Phase 5 - Hardening & Integrations

## Objective

Complete the remaining Phase 2 task (UI smoke test), implement Phase 4 (MCP, routing policies, cost controls), and Phase 5 (queue/DLQ, chaos, audit immutability, secrets hygiene, rate limiting) for the ZakOps Agent API per the Ultimate Implementation Roadmap v2.

## Background

- **Repo**: `/home/zaks/zakops-agent-api`
- **Gate Command**: `./scripts/bring_up_tests.sh`
- **Artifacts Directory**: `/home/zaks/zakops-agent-api/gate_artifacts/`
- **Authoritative Docs**: `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`

**Prerequisites Completed:**
- Phase 0: Foundations & Alignment ✅
- Phase 1: Core Infrastructure (Security) ✅
- Phase 2: MVP Build (partial - UI smoke test pending)
- Phase 3: Intelligence ✅

## Scope

---

### Phase 2 (Remaining)

#### P2-UI-001: UI Smoke Test
- Implement automated UI smoke test for ZakOps Next.js frontend
- UI must use canonical `/agent/*` endpoints
- UI must support:
  - invoke
  - stream
  - list approvals
  - approve/reject
- Implement Playwright smoke flow OR minimal scripted HTTP trace check
- Output `gate_artifacts/ui_smoke_test.log` with `UI_SMOKE: PASSED`

---

### Phase 4 - Tooling + Integrations

#### P4-MCP-001: MCP Client Conformance
- Implement MCP client contract:
  - `initialize`
  - `tools/list`
  - `tools/call`
- Error normalization and tool namespace mapping rules
- MCP server at `:9100` (if enabled)
- Output `gate_artifacts/mcp_conformance.json` with conformance results
- **Note**: MCP is optional; gate should SKIP gracefully if MCP not enabled

#### P4-ROUTE-001: LiteLLM Routing Policies
- Implement hybrid routing via LiteLLM gateway
- Enforce blocked-field policy for cloud egress:
  - BLOCKED: `ssn`, `tax_id`, `bank_account`, `credit_card`
- Enforce explicit allow conditions:
  - `context_overflow`, `local_model_error`, `explicit_user_request`, `complexity_threshold`
- Fallback chain: `local-primary → cloud-claude`
- Output `gate_artifacts/routing_policy_tests.json` with `ROUTING_POLICY: PASSED`
- Output `gate_artifacts/policy_config_snapshot.json`

#### P4-COST-001: Cost Accounting
- Implement daily budget cap: **$50 max**
- Cost accounting per day and per thread
- Measure local-handling rate: **≥80% tasks handled locally**
- Output `gate_artifacts/cost_report.json`
- Output `gate_artifacts/local_percent_report.json` with `LOCAL_PERCENT: PASSED` (if ≥80%)

---

### Phase 5 - Hardening, Security, Reliability

#### P5-QUEUE-001: Queue + DLQ (Postgres SKIP LOCKED)
- Implement queue schema with Postgres SKIP LOCKED
- Worker loop with retry policy per Decision Lock:
  - Backoff: 30s × 2^attempt
  - Max attempts: 3
  - DLQ after max attempts
- Queue targets:
  - Depth warn >50, critical >100
  - P95 claim latency <100ms under load
- Output `gate_artifacts/queue_worker_smoke.log` with `QUEUE_WORKER_SMOKE: PASSED`
- Output `gate_artifacts/queue_load_test.json` with P95 latency stats

#### P5-AUDIT-001: Audit Log Immutability
- Enforce audit_log immutability at DB level
- UPDATE/DELETE must be denied on audit_log table
- Gate proves immutability via attempted UPDATE/DELETE (should fail)
- Output `gate_artifacts/audit_immutability_test.log` with `AUDIT_IMMUTABILITY: PASSED`

#### P5-CHAOS-001: Chaos Hardening
- kill -9 mid-workflow and resume test
- Concurrency headroom test N=50 (additive to baseline N=20)
- Output `gate_artifacts/chaos_kill9.log` with `CHAOS_KILL9: PASSED`
- Output `gate_artifacts/concurrency_n50.log` with `CONCURRENCY_N50: PASSED`

#### P5-SECRETS-001: Secrets Hygiene
- No default JWT secret accepted in production exposure mode
- No enabling mocks in production exposure mode
- Gate fails closed if unsafe defaults detected
- Output `gate_artifacts/secrets_hygiene_lint.log` with `SECRETS_HYGIENE: PASSED`

#### P5-RATE-001: Rate Limiting
- Implement rate limiting on Agent API
- Implement request size limits
- Required before external exposure (Cloudflare)
- Output `gate_artifacts/rate_limit_test.log` with `RATE_LIMIT: PASSED`

---

## Out of Scope

- Phase 6: Evaluation, Red-Team, QA (CI gates, adversarial suites)
- Phase 7: Deployment, Monitoring, Operations
- Phase 8: Scaling, Optimization

## Technical Requirements

- All Phase 0, Phase 1, Phase 2, Phase 3 artifacts must remain PASS
- All baseline invariants (BL-01..BL-14) must remain PASS
- Single gate entrypoint: `./scripts/bring_up_tests.sh`
- All artifacts under `gate_artifacts/`
- No mocks for acceptance runs
- MCP gates should SKIP if MCP not enabled (not FAIL)

## Constraints from Decision Lock

### Queue (locked)
- Queue: Postgres SKIP LOCKED
- Backoff: 30s × 2^attempt
- Max attempts: 3
- DLQ required
- Queue depth warn >50, critical >100
- P95 claim latency <100ms under load

### LLM Routing (locked)
- Routing: LiteLLM gateway (deterministic)
- Fallback chain: local-primary → cloud-claude
- BLOCKED fields: ssn, tax_id, bank_account, credit_card
- ALLOWED conditions: context_overflow, local_model_error, explicit_user_request, complexity_threshold
- Daily budget: $50 max
- ≥80% tasks handled locally
- PII redaction before any cloud send

### Security (locked)
- Default deny
- No default JWT secret in production
- No mocks in production exposure mode

## References

- `/home/zaks/bookkeeping/docs/DECISION-LOCK-FILE.md`
- `/home/zaks/bookkeeping/docs/ZakOps-Scaffold-Master-Plan-v2.md`
- `/mnt/c/Users/mzsai/Downloads/ZakOps-Ultimate-Implementation-Roadmap-combine.v2.md`
