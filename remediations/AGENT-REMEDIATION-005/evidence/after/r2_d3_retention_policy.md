# audit_log Retention Policy

## Policy
- Retention period: 90 days in main table
- Archived data: moved to audit_log_archive (indefinite retention)
- Schedule: Monthly maintenance window (manual for now)

## Maintenance Procedure
1. Review audit_log size: `SELECT pg_size_pretty(pg_total_relation_size('audit_log'));`
2. Run: `psql -f scripts/audit_log_maintenance.sql`
3. Verify trigger re-enabled: `SELECT * FROM information_schema.triggers WHERE event_object_table = 'audit_log';`
4. Verify row counts decreased in main table

## Future Enhancement
- Partition audit_log by month for automatic retention management
- Add cron job for automated monthly archival

## Files
- `scripts/audit_log_maintenance.sql` - Maintenance script
- `audit_log_archive` table - Created for archival

## Created
Part of AGENT-REMEDIATION-005 (F-007 fix)
