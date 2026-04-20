# NC-8: MIGRATION FILE SABOTAGE
Date: 2026-02-08

## Pre-Sabotage State
Migration dir: /home/zaks/zakops-agent-api/apps/agent-api/migrations/
No 999_nc8_fake.sql file exists.

## Sabotage Applied
Created: `apps/agent-api/migrations/999_nc8_fake.sql` with content `-- NC-8 SABOTAGE`

## Gate Result
Ran: `git status --porcelain apps/agent-api/migrations/999_nc8_fake.sql`
Output: `?? apps/agent-api/migrations/999_nc8_fake.sql`
EXIT_CODE=0

**Gate DETECTED the untracked file.** `git status --porcelain` correctly shows the
unauthorized migration file as untracked (`??`). A CI pipeline with
`git status --porcelain | grep -q . && exit 1` would catch this.

## Revert
`rm -f .../999_nc8_fake.sql` — confirmed file removed (ls returns ENOENT)

## Post-Revert State
`git status --porcelain apps/agent-api/migrations/` returns empty (clean)

**RESULT: PASS** (git status detects unauthorized migration files)
