# Backup & Restore Drill Report

**Date:** 20260214_235124
**Location:** /home/zaks/bookkeeping/backups/drill_20260214_235124

## Results

| Check | Result |
|-------|--------|
| zakops_backup | PASS (116K, per-table COPY, 74 tables) |
| zakops_agent_backup | PASS (25M, via Docker) |
| crawlrag_backup | PASS (62M, via Docker) |
| zakops_restore | WARN (0 tables found) |
| zakops_agent_restore | PASS (33 tables, checksum OK) |
| crawlrag_restore | PASS (2 tables, checksum OK) |

## Summary

- **PASS:** 6
- **FAIL:** 0
- **Verdict:** PASS
