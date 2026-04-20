# V-P5.2: CI Bypass Check

**Verification ID**: QA-HG-VERIFY-001-V2 / V-P5.2
**Date**: 2026-02-06T08:27Z
**Verdict**: FAIL (3 CI bypass patterns found)

## Checks Performed

### 1. `paths-ignore` Check
**Result**: PASS - No `paths-ignore` directives found in either workflow.

The CI uses `dorny/paths-filter` for selective job execution (only runs jobs when relevant paths change), but this is a change-detection optimization, NOT a bypass. Jobs that DO run execute fully.

### 2. `pull_request` Trigger Check
**Result**: PASS - Both workflows have `pull_request` triggers.

- `ci.yml`: `pull_request: branches: [main]`
- `deploy.yaml`: `pull_request: branches: [main]`

### 3. `continue-on-error` Check
**Result**: FAIL - Found 1 instance.

File: `.github/workflows/ci.yml`, lines 79-81:
```yaml
      - name: Type check
        # TODO: fix 83 pre-existing type errors, then remove continue-on-error
        continue-on-error: true
        run: uv run mypy app/ --ignore-missing-imports --explicit-package-bases
```

This is in the **agent-api** job. Mypy type checking failures will NOT fail the CI build.

### 4. `|| true` Bypass Check
**Result**: FAIL - Found 2 instances.

File: `.github/workflows/ci.yml`, line 115:
```yaml
      - name: Type check
        run: npm run type-check || true
```

This is in the **dashboard** job. TypeScript type-check failures will NOT fail the CI build.

File: `.github/workflows/ci.yml`, line 135:
```yaml
      - name: Validate OpenAPI
        run: |
          npx @redocly/cli lint packages/contracts/openapi/*.json || true
```

This is in the **contracts** job. OpenAPI validation failures will NOT fail the CI build.

## Summary of CI Bypass Patterns

| Location | Pattern | Effect | Severity |
|----------|---------|--------|----------|
| agent-api/Type check | `continue-on-error: true` | Mypy failures ignored | HIGH |
| dashboard/Type check | `\|\| true` | tsc failures ignored | HIGH |
| contracts/Validate OpenAPI | `\|\| true` | OpenAPI lint failures ignored | MEDIUM |

## Conclusion
Three separate CI bypass patterns exist. All type-checking gates (Python mypy, TypeScript tsc) and the OpenAPI validation gate are effectively disabled. CI will pass even with type errors or schema validation failures. The TODO comment on line 79 acknowledges this is intentional but temporary ("fix 83 pre-existing type errors, then remove continue-on-error").
