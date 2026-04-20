# Phase 5: CI Verification Summary

**QA ID**: QA-HG-VERIFY-001-V2
**Phase**: 5 - CI Verification
**Date**: 2026-02-06T08:27Z
**Verifier**: Claude Opus 4.6 (automated QA)
**Mode**: VERIFY ONLY (no changes made)

## Verdict Matrix

| Check | ID | Verdict | Summary |
|-------|----|---------|---------|
| Workflow Structure | V-P5.1 | FAIL | No type-sync workflow in CI; YAML valid |
| CI Bypass Patterns | V-P5.2 | FAIL | 3 bypass patterns (continue-on-error, 2x \|\| true) |
| Correlation ID Presence | V-P5.3 | PASS | X-Correlation-ID on all 4 backend endpoints |
| Correlation ID Propagation | V-P5.4 | PASS | Explicit IDs echoed back + visible in docker logs |
| Sync-Types Determinism | V-P5.5 | FAIL | Uses live backend, not committed spec |
| validate-all | V-P5.6 | PASS | Exit code 0, all sub-gates passed |

## Overall Phase Verdict: 3 PASS / 3 FAIL

## Critical Findings

### 1. No Type-Sync CI Step (V-P5.1)
The `sync-types` codegen pipeline exists only as a local Makefile target. It is not invoked in any GitHub Actions workflow. CI does not verify that generated TypeScript types match the backend's OpenAPI spec.

### 2. Three CI Bypass Patterns (V-P5.2)
All type-checking gates are effectively disabled in CI:
- **agent-api mypy**: `continue-on-error: true` (83 pre-existing errors acknowledged in TODO)
- **dashboard tsc**: `npm run type-check || true`
- **contracts OpenAPI lint**: `npx @redocly/cli lint ... || true`

This means CI will never fail due to type errors or schema validation issues.

### 3. sync-types Is Non-Deterministic (V-P5.5)
`make sync-types` fetches the OpenAPI spec from the live backend (`curl -sf http://localhost:8091/openapi.json`) rather than using the committed contract at `packages/contracts/openapi/zakops-api.json`. This creates:
- Environment-dependent codegen output
- Impossibility of running in CI without a live backend
- No drift detection between committed contract and live spec

### 4. Correlation ID Implementation is Solid (V-P5.3, V-P5.4)
The backend middleware correctly:
- Returns `X-Correlation-ID` and `X-Trace-ID` on every response
- Echoes back client-provided correlation IDs unchanged
- Auto-generates UUID v4 when no correlation ID is provided
- Logs correlation IDs in structured JSON format in docker logs
- Includes security headers on all responses

### 5. validate-all Passes Locally (V-P5.6)
`make validate-all` completed with exit code 0. All sub-gates (infra-check, sync-types, rag-routing, secrets scan, enforcement audit) passed. However, this success depends on the live backend being accessible.

## Evidence Files
- `/home/zaks/bookkeeping/qa-verifications/QA-HG-VERIFY-001/evidence/phase5-ci-verify/V-P5.1-workflow-structure.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-HG-VERIFY-001/evidence/phase5-ci-verify/V-P5.2-ci-bypass-check.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-HG-VERIFY-001/evidence/phase5-ci-verify/V-P5.3-correlation-id-presence.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-HG-VERIFY-001/evidence/phase5-ci-verify/V-P5.4-correlation-id-propagation.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-HG-VERIFY-001/evidence/phase5-ci-verify/V-P5.5-sync-types-determinism.md`
- `/home/zaks/bookkeeping/qa-verifications/QA-HG-VERIFY-001/evidence/phase5-ci-verify/V-P5.6-validate-all-result.md`
