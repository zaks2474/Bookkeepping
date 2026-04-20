# V-L1.1: Exactly 1 Postgres Container Running
**VERDICT: PASS**

## Evidence
```
$ docker ps --format '{{.ID}} {{.Names}} {{.Ports}}' | grep -i postgres
71ea1caed587 zakops-backend-postgres-1 0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
```

Exactly 1 Postgres container running: `zakops-backend-postgres-1` on port 5432.
No other Postgres containers detected.
