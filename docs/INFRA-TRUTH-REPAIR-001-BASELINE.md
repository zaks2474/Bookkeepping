# INFRA-TRUTH-REPAIR-001 — Baseline Evidence
## Captured: 2026-02-10T16:52Z

---

## 1. Agent Skill Preload Path Checks

### arch-reviewer.md (lines 94-97)
```
- ~/.claude/skills/api-conventions
- ~/.claude/skills/security-and-data
- ~/.claude/skills/project-context
```
**Status:** BROKEN — `~/` does not resolve in agent preload context.

### contract-guardian.md (lines 65-66)
```
- ~/.claude/skills/verification-standards
- ~/.claude/skills/api-conventions
```
**Status:** BROKEN — same `~/` issue.

### test-engineer.md (lines 95-96)
```
- ~/.claude/skills/verification-standards
- ~/.claude/skills/debugging-playbook
```
**Status:** BROKEN — same `~/` issue.

---

## 2. Agent File Ownership

```
-rw-r--r--  1 root root 3318 Feb  9 18:31 arch-reviewer.md
-rw-r--r--  1 zaks zaks 2133 Feb  9 17:46 contract-guardian.md
-rw-r--r--  1 zaks zaks 2612 Feb  9 17:49 test-engineer.md
```
**Status:** INCONSISTENT — arch-reviewer.md is root:root.

---

## 3. Surface Count Reconciliation

| Artifact | Claims | Actual |
|----------|--------|--------|
| `.claude/rules/contract-surfaces.md` | 9 surfaces | 9 (S1-S9 defined) |
| `CLAUDE.md` (monorepo) | 9 Total | 9 (table has 9 rows) |
| `validate-contract-surfaces.sh` header | "all 7" | Checks S1-S7 only |
| Makefile target description (line 400) | "all 7" | S8/S9 not in target |
| `validate-surface9.sh` | exists | NOT wired into validate-full/validate-local |
| `validate-full` deps | S1-S8 | Missing S9 |
| `validate-local` deps | S1-S8 | Missing S9 |

**Status:** MISMATCH — Declared 9, enforced 7-8.

---

## 4. infra-snapshot Behavior

### Makefile `infra-snapshot` target (lines 463-472)
- Generator failure does NOT propagate: commands chained with `;` not `&&`
- `cp -f ... || true` swallows copy errors
- "Manifest generated" echoed regardless of generator exit code
**Status:** FALSE-GREEN — generator failure still prints success.

### generate-manifest.sh contract surfaces section (lines 148-169)
- Only checks 5 spec files: zakops-api.json, agent-api.json, rag-api.json, tool-schemas.json, agent-events.schema.json
- Missing: S8 (agent config alignment), S9 (design system conventions)
**Status:** INCOMPLETE — 5/9 surfaces represented.

---

## 5. Frontend-Design Skill

- Source exists: `/home/zaks/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`
- Active skills directory has 7 skills: api-conventions, atomic-workflow, code-style, debugging-playbook, project-context, security-and-data, verification-standards
- `frontend-design` NOT present in active skills
**Status:** MISSING — skill is inert.

---

## 6. Baseline Validation Gates

| Gate | Command | Result |
|------|---------|--------|
| validate-local | `make validate-local` | **PASS** |
| validate-contract-surfaces | `bash tools/infra/validate-contract-surfaces.sh` | **PASS** (7/7 only) |
| validate-surface9 | `bash tools/infra/validate-surface9.sh` | **PASS** (5/5 checks) |
| Boot diagnostics | session-start.sh | **ALL CLEAR** (0W, 0F) |

---

## 7. Session-Start CHECK 2 Scope

Currently compares: CLAUDE.md surface count vs MEMORY.md surface count only.
Does NOT check: validator header, Makefile target description, manifest content.
**Status:** NARROW — only 2 of 4+ authoritative sources checked.

---

## 8. Stop Hook Timing

Current budget: 15s total, Gate A 12s timeout, Gate B 6s timeout.
No Surface 9 check in stop hook.
**Status:** OK for current scope; needs review if S9 added.

---

*Baseline captured before any Phase 1 edits.*
