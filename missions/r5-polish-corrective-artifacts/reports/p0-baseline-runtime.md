# P0 — Baseline Runtime Report

## P0-01: Process & Ownership Baseline

### Stale processes found:
```
root 327686 npm exec next dev --port 3003
root 327700 sh -c next dev --port 3003
root 327701 node .../next dev --port 3003
root 327736 next-server (v15.5.9)
```
All running as **root** (not zaks).

### .next directory state:
- BUILD_ID: **MISSING**
- Mixed ownership: root + zaks files
- Root-owned stale cache: `cache.root-owned.1770919679/`
- Conclusion: **Stale/corrupted build artifacts confirmed**

## P0-02: Cleanup

- Killed all Next.js processes (force-kill required for orphans)
- Removed `.next` directory entirely
- Confirmed: no stale processes, no `.next` directory

## P0-03: Fresh Dev Server

- `.next` removed, fresh `npx next dev --port 3003` started
- Ready in 974ms — `Next.js 15.5.9` on `http://localhost:3003`
- Fresh compile of middleware + routes confirmed
- All Phase 1 layout fixes applied BEFORE compile (stretch grid, flex-1 card, flex CardContent, flex-1 ScrollArea)
