# Lab Loop Mission Template

Copy and paste this template to start a Lab Loop task directly in Claude Code.
The agent will automatically detect Lab Loop mode and follow the protocol.

---

## Quick Start (Minimal)

```
LAB LOOP TASK: [task_name]

REPO: /path/to/your/repo
GATE: pytest tests/  (or use profile: python-fast)

Mission: [Describe what needs to be built or fixed]

Acceptance:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] All tests pass
```

---

## Full Template

```
LAB LOOP STANDARD (MANDATORY)

This task MUST be executed via Lab Loop automation:
- Builder = Claude Code (non-interactive)
- QA = Codex (non-interactive, JSON Schema enforced)

TASK_ID: [unique_task_name]
REPO_DIR: /path/to/your/repo
GATE_CMD: pytest tests/  # or: bash /home/zaks/bookkeeping/labloop/profiles/gate-python-fast.sh
TASK_DIR: /home/zaks/bookkeeping/labloop/tasks/[task_id]/

Authoritative docs: /home/zaks/bookkeeping/docs/

---

## Mission

[Describe the objective - what needs to be built, fixed, or changed]

### Background
[Context about current state and why this task is needed]

### Scope
**In Scope:**
- [Item 1]
- [Item 2]

**Out of Scope:**
- [Item 1]

---

## Acceptance Criteria

The task is DONE when ALL of the following are true:

### Functional Requirements
- [ ] [Requirement 1]
- [ ] [Requirement 2]

### Quality Gates
- [ ] All tests pass (gate command exits 0)
- [ ] No linting errors
- [ ] No type errors

### Spec Compliance
- [ ] Implementation matches authoritative docs
- [ ] [Specific spec requirement]

---

## Handoff Protocol

1. Builder implements changes in REPO_DIR
2. Builder writes TASK_DIR/BUILDER_REPORT.md
3. Builder outputs JSON: {"status":"READY_FOR_QA",...}
4. Controller runs GATE_CMD
5. QA verifies and writes TASK_DIR/QA_REPORT.json
6. If FAIL, Builder addresses issues and repeats
7. DONE only when QA verdict = PASS AND gate exits 0

Do not declare success early. Do not bypass the loop.
```

---

## Examples

### Example 1: Bug Fix
```
LAB LOOP TASK: fix_auth_token

REPO: /home/zaks/zakops-backend
GATE: pytest tests/test_auth.py -v

Mission: Fix JWT token validation that fails on expired tokens

Acceptance:
- [ ] Expired tokens return 401 status
- [ ] Valid tokens allow access
- [ ] Tests for both cases pass
```

### Example 2: New Feature
```
LAB LOOP TASK: add_user_export

REPO: /home/zaks/zakops-backend
GATE: bash /home/zaks/bookkeeping/labloop/profiles/gate-python-full.sh

Mission: Add endpoint to export user data as CSV

Acceptance:
- [ ] GET /api/users/export returns CSV
- [ ] CSV includes: id, email, created_at
- [ ] Requires admin authentication
- [ ] Tests cover happy path and auth failure
```

### Example 3: Refactoring
```
LAB LOOP TASK: refactor_db_queries

REPO: /home/zaks/zakops-backend
GATE: pytest tests/ --cov=src/db --cov-fail-under=80

Mission: Refactor database queries to use SQLAlchemy ORM instead of raw SQL

Acceptance:
- [ ] No raw SQL strings in src/db/
- [ ] All existing tests still pass
- [ ] Coverage >= 80%
- [ ] No N+1 query patterns
```

---

## Gate Profile Reference

Available profiles in /home/zaks/bookkeeping/labloop/profiles/:

| Profile | Command | Use For |
|---------|---------|---------|
| python-fast | `bash .../gate-python-fast.sh` | Quick iteration |
| python-full | `bash .../gate-python-full.sh` | Full validation with coverage |
| nextjs | `bash .../gate-nextjs.sh` | Next.js/React projects |
| go | `bash .../gate-go.sh` | Go projects |
| rust | `bash .../gate-rust.sh` | Rust projects |
| docker | `bash .../gate-docker.sh` | Docker-based testing |
