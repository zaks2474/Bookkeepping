# M07 Boundary Snapshot — Pre-M08 Baseline
**Date:** 2026-02-11
**Commit:** 06fd038 (uncommitted M06 changes also present)

## Target Pages
- `/agent/activity` — `src/app/agent/activity/page.tsx` (658 lines)
- `/hq` — `src/app/hq/page.tsx` (120 lines) + 3 HQ components

## Key Findings Still Open
- F-23 (Sev-3): Agent Activity stat cards stack 1x4 at 375px via `md:grid-cols-4` default
- F-14 (Sev-2): HQ QuickStats `grid-cols-4` truncates labels; PipelineOverview `grid-cols-7` truncates stage badges

## Before Screenshots
- `m08-artifacts/before/agent-activity-{375,768,1280}.png`
- `m08-artifacts/before/hq-{375,768,1280}.png`
