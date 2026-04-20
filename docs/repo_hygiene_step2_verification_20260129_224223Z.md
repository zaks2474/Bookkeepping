# Repo Hygiene Step 2 — Artifacts Hygiene Verification Report

- Timestamp (UTC): 2026-01-29T22:42:23Z
- Repo: `/home/zaks/zakops-agent-api`
- Branch: `main`

## Summary (What Changed)

1) **.gitignore hardened** to ignore all generated outputs under `artifacts/` while keeping `artifacts/README.md` tracked:

```gitignore
# Artifacts: generated outputs (do not commit)
artifacts/**
!artifacts/README.md
```

2) **Untracked already-committed generated artifacts** (kept local files) via `git rm --cached`.

3) **Stop future status pollution** by additionally ignoring local run outputs detected in `git status`:
- `.test_venv/`
- `completion_packet/`
- `apps/dashboard/test-results/`
- `*.bak_*` (timestamped backups)

4) **Permissions fix to allow git ops as normal user (`zaks`)**:
- `chown -R zaks:zaks /home/zaks/zakops-agent-api/.git`

## Preflight (Before)

Tracked artifacts count (before):
- `git ls-files artifacts | wc -l` → **91**

Example (first entries):
- `artifacts/README.md`
- `artifacts/business/beta_readiness.json`
- `artifacts/gate_artifacts/health.json`
- `artifacts/validation/phase0_service_health.json`

## Actions Taken

### Update ignore rules
- Edited: `.gitignore`
- Verified ignore behavior:

```bash
cd /home/zaks/zakops-agent-api
git check-ignore -v artifacts/logging/MASTER_REPORT.json || true
git check-ignore -v artifacts/tests/system_smoke.json || true
```

### Untrack generated artifacts (keep local files)

```bash
cd /home/zaks/zakops-agent-api
git ls-files artifacts | grep -v '^artifacts/README.md$' | xargs -r git rm --cached
git add .gitignore artifacts/README.md
```

### Commit

```bash
git commit -m "chore: stop tracking generated artifacts"
```

Commit:
- `71d52d0 chore: stop tracking generated artifacts`

## Final Verification (After)

### Repo clean

```bash
cd /home/zaks/zakops-agent-api
git status
```

Output:
```text
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

### Artifacts tracking sanity

```bash
git ls-files artifacts
```

Output:
```text
artifacts/README.md
```

### Ignore sanity

```bash
git check-ignore -v artifacts/logging/MASTER_REPORT.json || true
```

Output:
```text
.gitignore:118:artifacts/**	artifacts/logging/MASTER_REPORT.json
```

### Push dry-run (normal user, no sudo)

```bash
git remote -v
git push --dry-run origin HEAD
```

Output:
```text
origin	git@github.com:zaks2474/zakops.git (fetch)
origin	git@github.com:zaks2474/zakops.git (push)

To github.com:zaks2474/zakops.git
   423692c..71d52d0  HEAD -> main
```

## Notes

- **No local files were deleted**: untracking used `git rm --cached` only.
- `artifacts/**` is now ignored so future gate/e2e/logging runs should not pollute `git status`.
