# E01 — source_type Drift Eliminated

**Gate:** E01
**Date:** 2026-02-13
**Auditor:** Claude Opus 4.6 (automated)

---

## Objective

Confirm that the deprecated/drifted name `langsmith_production` has been fully
eliminated from all code and documentation, and that the canonical name
`langsmith_live` is consistently used across all surfaces.

---

## Search 1 — `langsmith_production` (MUST be zero hits)

### Scope: `/home/zaks/zakops-backend/src/`
```
0 matches
```

### Scope: `/home/zaks/zakops-backend/docs/`
```
0 matches
```

### Scope: `/home/zaks/zakops-agent-api/apps/dashboard/src/`
```
0 matches
```

### Scope: `/home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md`
```
0 matches
```

**Total `langsmith_production` occurrences: 0** -- drift name fully eliminated.

---

## Search 2 — `langsmith_live` (canonical name, MUST be present)

### Scope: `/home/zaks/zakops-backend/src/`
```
/home/zaks/zakops-backend/src/api/orchestration/main.py:272:    source_type: str | None = None  # manual, email_sync, langsmith_shadow, langsmith_live
/home/zaks/zakops-backend/src/api/orchestration/main.py:277:VALID_SOURCE_TYPES = {"email", "email_sync", "langsmith_shadow", "langsmith_live", "manual"}
```
**Hits: 2**

### Scope: `/home/zaks/zakops-backend/docs/`
```
/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md:49:| **400 Bad Request** | Invalid payload or unrecognized `source_type` (must be one of: `email`, `email_sync`, `langsmith_shadow`, `langsmith_live`, `manual`) |
/home/zaks/zakops-backend/docs/INJECTION-CONTRACT.md:79:| `langsmith_live` | LangSmith live-mode items |
```
**Hits: 2**

### Scope: `/home/zaks/zakops-agent-api/apps/dashboard/src/`
```
src/app/quarantine/page.tsx:327:            <option value='langsmith_live'>LangSmith live</option>
```
**Hits: 1**

### Scope: `/home/zaks/bookkeeping/docs/MASTER-PROGRAM-INTAKE-COL-V2-001.md`
```
Line 496:  - Add `source_type VARCHAR(50) DEFAULT 'manual'` column ... Valid values: `'manual'`, `'email_sync'`, `'langsmith_shadow'`, `'langsmith_live'`.
```
**Hits: 1**

**Total `langsmith_live` occurrences: 6** -- canonical name present across backend code, backend docs, dashboard UI, and program spec.

---

## Search 3 — `VALID_SOURCE_TYPES` enforcement constant

### Scope: `/home/zaks/zakops-backend/src/`
```
/home/zaks/zakops-backend/src/api/orchestration/main.py:277:VALID_SOURCE_TYPES = {"email", "email_sync", "langsmith_shadow", "langsmith_live", "manual"}
/home/zaks/zakops-backend/src/api/orchestration/main.py:1534:    if source_type not in VALID_SOURCE_TYPES:
/home/zaks/zakops-backend/src/api/orchestration/main.py:1540:                "valid_values": sorted(VALID_SOURCE_TYPES),
```
**Hits: 3** -- constant defined (line 277), enforced at injection time (line 1534), and returned in error responses (line 1540).

### Scope: `/home/zaks/zakops-agent-api/apps/dashboard/src/`
```
0 matches
```
Not expected in dashboard (enforcement is server-side).

---

## Summary

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| `langsmith_production` in backend code | 0 | 0 | PASS |
| `langsmith_production` in backend docs | 0 | 0 | PASS |
| `langsmith_production` in dashboard | 0 | 0 | PASS |
| `langsmith_production` in program spec | 0 | 0 | PASS |
| `langsmith_live` in backend code | >= 1 | 2 | PASS |
| `langsmith_live` in backend docs | >= 1 | 2 | PASS |
| `langsmith_live` in dashboard UI | >= 1 | 1 | PASS |
| `langsmith_live` in program spec | >= 1 | 1 | PASS |
| `VALID_SOURCE_TYPES` defined | yes | yes (line 277) | PASS |
| `VALID_SOURCE_TYPES` enforced | yes | yes (line 1534) | PASS |

---

## Verdict: PASS

The deprecated `langsmith_production` source type has been fully eliminated from
all searched code and documentation surfaces. The canonical name `langsmith_live`
is consistently present in backend code, backend documentation, dashboard UI, and
the master program specification. Server-side enforcement via `VALID_SOURCE_TYPES`
ensures no drifted names can be injected at runtime.
