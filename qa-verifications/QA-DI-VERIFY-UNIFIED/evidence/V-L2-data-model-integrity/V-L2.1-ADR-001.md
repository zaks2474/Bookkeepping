# V-L2.1: ADR-001 Exists
**VERDICT: FAIL**

## Evidence
```
$ find /home/zaks -maxdepth 5 -iname "adr*001*" -type f
(no results)
```

ADR-001 does not exist. Related ADRs found:
- `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-UNIFIED/layer-6/ADR-002-canonical-database.md`
- `/home/zaks/bookkeeping/qa-verifications/DEAL-INTEGRITY-UNIFIED/layer-6/ADR-003-stage-configuration-authority.md`

ADR-001 (presumably covering the deal lifecycle FSM decision) is missing.
