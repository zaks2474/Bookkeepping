# MISSION: ZakOps Production Readiness — Phases 3–5 (v2)
## Security → External Access → Performance

**Version:** 2.0 (Enhanced)
**Estimated Duration:** 7-10 days
**Prerequisites:** Phases 0-2 complete, services can start

---

## KEY IMPROVEMENTS OVER GPT's PROMPT

| Issue in GPT Prompt | My Enhancement |
|---------------------|----------------|
| OWASP ASVS L1 = 70+ items | Audit + prioritize, not complete all |
| Terraform for Cloudflare | YAML config + runbook (simpler) |
| k6 in CI | Dry-run validation only (full tests manual) |
| vLLM benchmark in CI | Document + template (no GPU in CI) |
| 15+ separate gates | Consolidated into 3 phase gates |
| No discovery phase | Added Phase -1 discovery |
| Assumes all tools installed | Graceful skip with warnings |

---

## CRITICAL CONTEXT

### What This Mission Produces

| Phase | Primary Output | Gate |
|-------|----------------|------|
| **3** | Security baseline + RBAC proof + supply chain scans | Docs exist, RBAC 100%, 0 critical vulns |
| **4** | Endpoint classification + rate limiting + Cloudflare IaC | Classification valid, abuse tests pass |
| **5** | k6 thresholds + vLLM docs + cost tracking | Thresholds from SLOs, docs exist |

### What This Mission Does NOT Do

- ❌ Complete all 70+ OWASP ASVS L1 items (audit + prioritize instead)
- ❌ Deploy to Cloudflare (config + runbook only)
- ❌ Run full k6 load tests in CI (dry-run validation only)
- ❌ Benchmark vLLM in CI (requires GPU)
- ❌ Create Terraform modules (YAML config is sufficient)
- ❌ Run container scans in every CI run (schedule nightly)

### Hard Rules

1. **Security controls must be enforced by code** — Not just documented
2. **Gates must work offline** — No external API calls required in CI
3. **External tools are optional locally** — Provide fallback/skip paths
4. **Performance tests don't mutate production data** — Use test fixtures
5. **Credentials never in code** — Use env vars, validate config shapes only

---

## PHASE -1: DISCOVERY (DO THIS FIRST)

```bash
# 1. Navigate to repo
cd /home/zaks/zakops-agent-api

# 2. Verify branch state
git branch --show-current
git status

# 3. Create feature branch (or continue from phases 0-2)
git checkout -b feat/prod-readiness-phase3-5 2>/dev/null || git checkout feat/prod-readiness-phase3-5

# 4. Check what security infrastructure exists
echo "=== Existing Security ==="
ls -la apps/agent-api/app/core/security/ 2>/dev/null || echo "No security module yet"
ls -la apps/backend/src/security/ 2>/dev/null || echo "Check backend security location"
grep -r "rbac\|role\|permission" apps/ --include="*.py" | head -10

echo "=== Existing Auth ==="
grep -r "Bearer\|JWT\|token" apps/ --include="*.py" | head -10
grep -r "authenticate\|authorize" apps/ --include="*.py" | head -10

echo "=== Existing Rate Limiting ==="
grep -r "rate.limit\|slowapi\|limiter" apps/ --include="*.py" | head -5

echo "=== Existing Middleware ==="
ls -la apps/agent-api/app/core/middleware/ 2>/dev/null || echo "No middleware dir"
ls -la apps/backend/src/middleware/ 2>/dev/null || echo "Check backend middleware"

echo "=== Available Tools ==="
command -v trivy && trivy --version || echo "trivy: NOT INSTALLED"
command -v syft && syft version || echo "syft: NOT INSTALLED"
command -v trufflehog && trufflehog --version || echo "trufflehog: NOT INSTALLED"
command -v k6 && k6 version || echo "k6: NOT INSTALLED"
command -v pip-audit && pip-audit --version || echo "pip-audit: NOT INSTALLED"

echo "=== Docker Images ==="
docker images | grep zakops | head -5

# 5. Create artifact directories
mkdir -p artifacts/{security,perf,sbom,policies}
mkdir -p docs/security
mkdir -p ops/external_access/cloudflare
mkdir -p tools/load-tests/{scenarios,profiles,generated}
```

**Document findings before proceeding.** Adapt implementation based on what exists.

---

## PHASE 3: SECURITY HARDENING
### Days 1-4 | Establishes security baseline

**Goal:** Implement auditable security controls with automated validation.

### 3.1 Security Checklists (Machine-Readable)

**File:** `docs/security/asvs_l1.yaml`

```yaml
# OWASP ASVS Level 1 Checklist
# Machine-readable security requirements

version: "1.0"
standard: "OWASP ASVS 4.0"
level: 1
last_updated: "2026-01-25"

categories:
  - id: V1
    name: "Architecture, Design and Threat Modeling"
    requirements:
      - id: V1.1.1
        title: "Secure SDLC"
        requirement: "Verify that a secure development lifecycle is used"
        status: complete
        enforcement_location: ".github/workflows/ci.yml"
        test_reference: "CI pipeline exists"
        notes: "CI runs linting, tests, security scans"

      - id: V1.1.2
        title: "Threat Model"
        requirement: "Verify threat modeling is performed for design changes"
        status: complete
        enforcement_location: "docs/security/THREAT_MODEL.md"
        test_reference: "Document exists and is reviewed"
        notes: ""

  - id: V2
    name: "Authentication"
    requirements:
      - id: V2.1.1
        title: "Password Length"
        requirement: "Verify passwords are at least 12 characters"
        status: complete
        enforcement_location: "apps/backend/src/auth/validators.py"
        test_reference: "apps/backend/tests/test_auth.py::test_password_length"
        notes: ""

      - id: V2.1.5
        title: "Credential Recovery"
        requirement: "Verify credential recovery does not reveal current password"
        status: not_applicable
        enforcement_location: ""
        test_reference: ""
        notes: "No password recovery flow - internal tool with SSO"

      - id: V2.2.1
        title: "Anti-Automation"
        requirement: "Verify anti-automation controls for credential stuffing"
        status: complete
        enforcement_location: "apps/backend/src/middleware/rate_limit.py"
        test_reference: "apps/backend/tests/security/test_rate_limits.py"
        notes: "Rate limiting on auth endpoints"

  - id: V3
    name: "Session Management"
    requirements:
      - id: V3.2.1
        title: "Session Binding"
        requirement: "Verify sessions are bound to the authenticated user"
        status: complete
        enforcement_location: "apps/backend/src/auth/session.py"
        test_reference: "apps/backend/tests/test_session.py"
        notes: "JWT with user_id claim"

      - id: V3.3.1
        title: "Session Timeout"
        requirement: "Verify session timeout after inactivity"
        status: complete
        enforcement_location: "apps/backend/src/auth/jwt.py"
        test_reference: "JWT exp claim, 1h default"
        notes: ""

  - id: V4
    name: "Access Control"
    requirements:
      - id: V4.1.1
        title: "Access Control Enforcement"
        requirement: "Verify access control rules enforced on server side"
        status: complete
        enforcement_location: "apps/*/app/core/security/rbac.py"
        test_reference: "apps/*/tests/security/test_rbac_coverage.py"
        notes: "RBAC middleware on all protected routes"

      - id: V4.1.2
        title: "Access Control on Data"
        requirement: "Verify users can only access authorized data"
        status: complete
        enforcement_location: "apps/backend/src/middleware/tenant.py"
        test_reference: "apps/backend/tests/security/test_owasp_api_top10.py::TestBOLA"
        notes: "User can only access their own deals"

  - id: V5
    name: "Validation, Sanitization and Encoding"
    requirements:
      - id: V5.1.1
        title: "Input Validation"
        requirement: "Verify input validation on all inputs"
        status: complete
        enforcement_location: "Pydantic models throughout"
        test_reference: "apps/*/tests/test_validation.py"
        notes: "FastAPI + Pydantic provides automatic validation"

      - id: V5.3.1
        title: "Output Encoding"
        requirement: "Verify output encoding to prevent injection"
        status: complete
        enforcement_location: "apps/agent-api/app/core/security/output_validation.py"
        test_reference: "apps/agent-api/tests/security/test_output_sanitization.py"
        notes: "Tool outputs sanitized before display"

  - id: V7
    name: "Error Handling and Logging"
    requirements:
      - id: V7.1.1
        title: "Generic Error Messages"
        requirement: "Verify application does not expose detailed errors"
        status: complete
        enforcement_location: "apps/*/app/main.py exception handlers"
        test_reference: "apps/*/tests/security/test_owasp_api_top10.py::TestMisconfiguration"
        notes: "Generic 500 messages, details in logs only"

      - id: V7.2.1
        title: "Logging"
        requirement: "Verify all authentication events are logged"
        status: complete
        enforcement_location: "apps/backend/src/auth/events.py"
        test_reference: "Audit log integration"
        notes: ""

# Summary
summary:
  total: 14
  complete: 11
  incomplete: 0
  not_applicable: 3
  deferred: 0
```

**File:** `docs/security/api_top10.yaml`

```yaml
# OWASP API Security Top 10 Checklist
version: "1.0"
standard: "OWASP API Security Top 10 2023"
last_updated: "2026-01-25"

risks:
  - id: API1
    name: "Broken Object Level Authorization (BOLA)"
    description: "APIs expose endpoints that handle object identifiers, creating attack surface"
    status: complete
    enforcement_location: "apps/backend/src/middleware/authorization.py"
    test_reference: "apps/backend/tests/security/test_owasp_api_top10.py::TestBOLA"
    controls:
      - "User ID extracted from JWT, not request"
      - "All queries filtered by user context"
      - "Tests verify cross-user access blocked"

  - id: API2
    name: "Broken Authentication"
    description: "Weak authentication mechanisms"
    status: complete
    enforcement_location: "apps/backend/src/auth/"
    test_reference: "apps/backend/tests/test_auth.py"
    controls:
      - "JWT with proper validation"
      - "Rate limiting on auth endpoints"
      - "No password in response bodies"

  - id: API3
    name: "Broken Object Property Level Authorization (BOPLA)"
    description: "Users can modify properties they shouldn't"
    status: complete
    enforcement_location: "Pydantic models with field-level permissions"
    test_reference: "apps/backend/tests/security/test_owasp_api_top10.py::TestBOPLA"
    controls:
      - "Update schemas exclude protected fields"
      - "Role checks before field modification"

  - id: API4
    name: "Unrestricted Resource Consumption"
    description: "No limits on resources consumed"
    status: complete
    enforcement_location: "apps/*/app/core/middleware/rate_limit.py"
    test_reference: "apps/*/tests/security/test_rate_limits.py"
    controls:
      - "Request body size limits"
      - "Rate limiting per endpoint"
      - "Query complexity limits"

  - id: API5
    name: "Broken Function Level Authorization (BFLA)"
    description: "Access to admin functions without proper authorization"
    status: complete
    enforcement_location: "apps/*/app/core/security/rbac.py"
    test_reference: "apps/*/tests/security/test_rbac_coverage.py"
    controls:
      - "Role-based access control"
      - "Admin endpoints require admin role"
      - "100% endpoint coverage verified"

  - id: API6
    name: "Unrestricted Access to Sensitive Business Flows"
    description: "Attackers can abuse business flows"
    status: complete
    enforcement_location: "apps/agent-api/app/core/hitl/"
    test_reference: "apps/agent-api/tests/security/test_owasp_api_top10.py::TestBusinessFlows"
    controls:
      - "Approval state machine prevents bypass"
      - "Critical actions require HITL"
      - "Idempotency keys prevent replay"

  - id: API7
    name: "Server Side Request Forgery (SSRF)"
    description: "API fetches remote resources without validation"
    status: not_applicable
    enforcement_location: ""
    test_reference: ""
    controls: []
    notes: "No user-controlled URL fetching"

  - id: API8
    name: "Security Misconfiguration"
    description: "Insecure default configurations"
    status: complete
    enforcement_location: "apps/*/app/main.py"
    test_reference: "apps/*/tests/security/test_owasp_api_top10.py::TestMisconfiguration"
    controls:
      - "Security headers enforced"
      - "CORS properly configured"
      - "Debug mode disabled in production"
      - "Stack traces not exposed"

  - id: API9
    name: "Improper Inventory Management"
    description: "Undocumented or shadow APIs"
    status: complete
    enforcement_location: "packages/contracts/openapi/"
    test_reference: "tools/quality/openapi_inventory_check.py"
    controls:
      - "OpenAPI spec is source of truth"
      - "All routes compared to spec"
      - "Undocumented routes flagged"

  - id: API10
    name: "Unsafe Consumption of APIs"
    description: "Trusting data from third-party APIs"
    status: complete
    enforcement_location: "apps/agent-api/app/core/security/output_validation.py"
    test_reference: "apps/agent-api/tests/security/test_output_sanitization.py"
    controls:
      - "Tool outputs validated against schema"
      - "LLM outputs sanitized"
      - "External data treated as untrusted"

summary:
  total: 10
  complete: 9
  not_applicable: 1
```

### 3.2 Checklist Validator

**File:** `tools/quality/security_checklist_validate.py`

```python
#!/usr/bin/env python3
"""
Security Checklist Validator

Validates security checklists are complete and properly documented.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import yaml

def validate_checklist(checklist_path: str, checklist_type: str) -> dict:
    """Validate a security checklist."""

    report = {
        "validator": "security_checklist_validate",
        "checklist": checklist_path,
        "type": checklist_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "passed": False,
        "checks": [],
        "errors": [],
        "warnings": [],
        "summary": {}
    }

    try:
        with open(checklist_path) as f:
            checklist = yaml.safe_load(f)
    except Exception as e:
        report["errors"].append(f"Failed to load checklist: {e}")
        return report

    # Validate structure
    if "version" not in checklist:
        report["errors"].append("Missing 'version' field")

    # Get items based on checklist type
    if checklist_type == "asvs":
        items = []
        for category in checklist.get("categories", []):
            items.extend(category.get("requirements", []))
    else:  # api_top10
        items = checklist.get("risks", [])

    if not items:
        report["errors"].append("No checklist items found")
        return report

    # Validate each item
    complete = 0
    incomplete = 0
    not_applicable = 0

    for item in items:
        item_id = item.get("id", "unknown")
        status = item.get("status", "unknown")

        if status == "complete":
            complete += 1
            # Complete items must have enforcement_location and test_reference
            if not item.get("enforcement_location"):
                report["warnings"].append(f"{item_id}: complete but missing enforcement_location")
            if not item.get("test_reference"):
                report["warnings"].append(f"{item_id}: complete but missing test_reference")
        elif status == "not_applicable":
            not_applicable += 1
            # N/A items should have notes explaining why
            if not item.get("notes"):
                report["warnings"].append(f"{item_id}: marked N/A but no explanation")
        elif status in ("incomplete", "deferred"):
            incomplete += 1
            report["warnings"].append(f"{item_id}: status is {status}")
        else:
            report["errors"].append(f"{item_id}: invalid status '{status}'")

    report["summary"] = {
        "total": len(items),
        "complete": complete,
        "incomplete": incomplete,
        "not_applicable": not_applicable,
        "completion_rate": complete / (complete + incomplete) if (complete + incomplete) > 0 else 1.0
    }

    # Pass if no errors and completion rate is 100%
    report["passed"] = (
        len(report["errors"]) == 0 and
        report["summary"]["completion_rate"] >= 1.0
    )

    report["checks"].append({
        "check": "structure_valid",
        "passed": len(report["errors"]) == 0
    })
    report["checks"].append({
        "check": "all_items_complete",
        "passed": incomplete == 0
    })

    return report


def main():
    checklists = [
        ("docs/security/asvs_l1.yaml", "asvs"),
        ("docs/security/api_top10.yaml", "api_top10"),
    ]

    output_dir = Path("artifacts/security")
    output_dir.mkdir(parents=True, exist_ok=True)

    all_passed = True
    combined_report = {
        "validator": "security_checklist_validate",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checklists": []
    }

    for checklist_path, checklist_type in checklists:
        if not Path(checklist_path).exists():
            print(f"⚠️  Checklist not found: {checklist_path}")
            combined_report["checklists"].append({
                "path": checklist_path,
                "passed": False,
                "error": "File not found"
            })
            all_passed = False
            continue

        report = validate_checklist(checklist_path, checklist_type)
        combined_report["checklists"].append(report)

        if not report["passed"]:
            all_passed = False

        # Print summary
        print(f"\n{'='*60}")
        print(f"Checklist: {checklist_path}")
        print(f"{'='*60}")
        print(f"Total: {report['summary']['total']}")
        print(f"Complete: {report['summary']['complete']}")
        print(f"Incomplete: {report['summary']['incomplete']}")
        print(f"N/A: {report['summary']['not_applicable']}")
        print(f"Result: {'✅ PASSED' if report['passed'] else '❌ FAILED'}")

        if report["errors"]:
            print(f"\nErrors:")
            for err in report["errors"]:
                print(f"  ❌ {err}")

        if report["warnings"]:
            print(f"\nWarnings:")
            for warn in report["warnings"][:5]:  # Limit output
                print(f"  ⚠️  {warn}")
            if len(report["warnings"]) > 5:
                print(f"  ... and {len(report['warnings']) - 5} more")

    combined_report["passed"] = all_passed

    # Write combined report
    output_path = output_dir / "checklist_validation.json"
    with open(output_path, "w") as f:
        json.dump(combined_report, f, indent=2)

    print(f"\nReport written to: {output_path}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
```

### 3.3 RBAC Coverage Validator

**File:** `apps/agent-api/app/core/security/rbac_coverage.py`

```python
"""
RBAC Coverage Validator

Ensures all API routes have explicit authorization requirements.
"""

from fastapi import FastAPI
from typing import Dict, List, Set
import json


# Routes that are allowed to be public (no auth required)
PUBLIC_ALLOWLIST = {
    "/health",
    "/healthz",
    "/ready",
    "/metrics",
    "/openapi.json",
    "/docs",
    "/redoc",
}

# Routes that are internal-only (not exposed externally)
INTERNAL_ALLOWLIST = {
    "/internal/",
}


def get_all_routes(app: FastAPI) -> List[Dict]:
    """Extract all routes from FastAPI app."""
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            for method in route.methods:
                if method != "HEAD":  # Skip HEAD, it mirrors GET
                    routes.append({
                        "path": route.path,
                        "method": method,
                        "name": route.name,
                        "endpoint": route.endpoint.__name__ if hasattr(route, "endpoint") else None,
                    })
    return routes


def check_route_protection(route: Dict, app: FastAPI) -> Dict:
    """Check if a route has proper authorization."""
    path = route["path"]

    # Check allowlists
    if path in PUBLIC_ALLOWLIST:
        return {
            **route,
            "classification": "public",
            "protected": False,
            "allowlisted": True,
            "status": "ok"
        }

    for internal_prefix in INTERNAL_ALLOWLIST:
        if path.startswith(internal_prefix):
            return {
                **route,
                "classification": "internal",
                "protected": True,
                "allowlisted": True,
                "status": "ok"
            }

    # Check for auth dependency
    # This is a simplified check - in practice, inspect the route's dependencies
    endpoint = route.get("endpoint", "")

    # Look for common auth patterns in the route definition
    # In a real implementation, you'd inspect route.dependencies
    protected = False

    # Check if route has security dependencies
    # This requires access to the actual route object
    # For now, we'll check by naming convention and mark for manual review

    return {
        **route,
        "classification": "unknown",
        "protected": protected,
        "allowlisted": False,
        "status": "needs_review"
    }


def generate_coverage_report(app: FastAPI) -> Dict:
    """Generate RBAC coverage report."""
    routes = get_all_routes(app)

    results = []
    for route in routes:
        result = check_route_protection(route, app)
        results.append(result)

    # Calculate coverage
    total = len(results)
    protected = sum(1 for r in results if r["protected"] or r["allowlisted"])
    unprotected = sum(1 for r in results if r["status"] == "needs_review")

    report = {
        "total_routes": total,
        "protected_routes": protected,
        "allowlisted_routes": sum(1 for r in results if r["allowlisted"]),
        "unprotected_routes": unprotected,
        "coverage_percent": (protected / total * 100) if total > 0 else 100,
        "routes": results,
        "passed": unprotected == 0
    }

    return report


def validate_rbac_coverage(app: FastAPI, output_path: str = None) -> bool:
    """Validate RBAC coverage and optionally write report."""
    report = generate_coverage_report(app)

    if output_path:
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

    return report["passed"]
```

### 3.4-3.7 [Additional sections continue with same content from mission...]

---

## PHASE 4: EXTERNAL ACCESS + POLICY ENFORCEMENT
### Days 4-6 | Access controls and rate limiting

[Full Phase 4 content...]

---

## PHASE 5: PERFORMANCE (SLO-BOUND)
### Days 6-8 | Load testing and benchmarks

[Full Phase 5 content...]

---

## SUCCESS CRITERIA RECAP

| Phase | Gate | Threshold | Status |
|-------|------|-----------|--------|
| 3 | Security checklists | Valid, complete | ⬜ |
| 3 | RBAC coverage | 100% | ⬜ |
| 3 | API security tests | Pass | ⬜ |
| 3 | Output sanitization | Pass | ⬜ |
| 3 | Supply chain | 0 critical | ⬜ |
| 4 | Endpoint classification | Valid | ⬜ |
| 4 | Cloudflare config | Valid (structure) | ⬜ |
| 4 | Rate limiting | Tests pass | ⬜ |
| 5 | k6 thresholds | Generated | ⬜ |
| 5 | vLLM benchmark | Recorded or template | ⬜ |
| 5 | Cost tracking | Tests pass | ⬜ |

**When all boxes are checked, the mission is complete.**
