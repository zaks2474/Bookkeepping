# Finding-to-Fix Matrix — AGENT-REMEDIATION-005

| Finding | Severity | Phase | Status | Fix Description | Evidence |
|---------|----------|-------|--------|-----------------|----------|
| F-001 | P2 | R1.A | FIXED | Langfuse readiness infrastructure | r1_a6_*, r1_a7_trace_sink_test.txt |
| F-002 | P2 | R1.B | DEFERRED | Container NOT orphan - has active data | r1_b_deferred_justification.md |
| F-003 | P3 | R2.A | FIXED | audit_log DELETE trigger installed | r2_a1_trigger_create.txt, r2_a2_*.txt |
| F-004 | P3 | R2.B | EXISTING | /docs, /redoc already conditional | main.py:59-69 |
| F-005 | P3 | R2.B | DOCUMENTED | /metrics - needs production env test | production mode required |
| F-006 | P3 | R2.C | FIXED | Docker log rotation configured | r2_c3_log_config.txt |
| F-007 | P3 | R2.D | FIXED | audit_log retention policy + archive table | r2_d2_archive_table.txt, r2_d3_retention_policy.md |
| F-008 | P3 | R2.E | PARTIAL | Server header - version not disclosed | r2_e3_server_header.txt, r2_e4_fingerprint_scan.txt |

## Summary
- **Fixed**: F-001, F-003, F-006, F-007
- **Partial**: F-008 (version masked, header name visible)
- **Existing**: F-004 (already implemented)
- **Documented**: F-005 (requires production mode)
- **Deferred**: F-002 (data safety - container has active data)
