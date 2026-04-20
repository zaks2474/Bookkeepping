# F-002 DEFERRED — zakops-postgres-1 Investigation

## Finding
F-002 identified `zakops-postgres-1` as an "orphan container" creating split-brain confusion risk.

## Investigation Results

### Container Details
- Name: zakops-postgres-1
- Project: "zakops" (different from "zakops-backend")
- Image: postgres:15-alpine
- Status: Running, healthy
- Port: 5432 (host-bound)
- Created: 2026-01-26

### Data Comparison (CRITICAL)

| Database | Container | Deal Events | Most Recent Event |
|----------|-----------|-------------|-------------------|
| zakops | zakops-backend-postgres-1 | 5 | 2026-02-02 15:25 (yesterday) |
| zakops | zakops-postgres-1 | 29 | 2026-02-03 21:00 (TODAY) |

### Analysis
- `zakops-postgres-1` has MORE data and MORE RECENT events
- The backend container uses `postgres:5432` (docker service) → `zakops-backend-postgres-1`
- Yet `zakops-postgres-1` has today's events, suggesting another process is writing to it
- **Removing this container could result in DATA LOSS**

## Decision: DEFERRED

Cannot safely remove `zakops-postgres-1` without:
1. Identifying what process is writing to it
2. Understanding why it has more recent data
3. Planning a data migration if needed

## Recommendation
1. Keep both containers running for now
2. Investigate which application/process uses `localhost:5432` (host port → zakops-postgres-1)
3. If confirmed orphan after investigation, migrate data before removal

## Evidence
- r0_3_containers_before.txt: Container inventory
- r1_b1_orphan_inspect.txt: Container labels and ports
- This file: Investigation results
