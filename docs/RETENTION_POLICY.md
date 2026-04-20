# Data Retention Policy

**Document ID:** RETENTION-POLICY-001
**Version:** 1.0.0
**Last Updated:** 2026-02-03
**Owner:** ZakOps Platform Team

## Overview

This document defines the data retention policies for the ZakOps Deal Lifecycle Management system. These policies ensure compliance with data governance requirements while balancing operational needs.

## Scope

This policy applies to all data stored in:
- PostgreSQL `zakops` database (deals, events, actions, quarantine)
- PostgreSQL `zakops_agent` database (agent checkpoints, approvals)
- PostgreSQL `crawlrag` database (RAG vector embeddings)
- File storage (DataRoom folders, attachments)

## Retention Periods

### Deal Data

| Data Type | Retention Period | Archive Policy |
|-----------|-----------------|----------------|
| Active deals | Indefinite | N/A |
| Archived deals | 7 years | Move to cold storage after 2 years |
| Junk deals | 90 days | Auto-delete after retention period |
| Deal events | Matches deal retention | Cascade with parent deal |
| Deal notes | Matches deal retention | Cascade with parent deal |
| Deal aliases | Matches deal retention | Cascade with parent deal |

### Action Data

| Data Type | Retention Period | Archive Policy |
|-----------|-----------------|----------------|
| Pending actions | Until resolution | N/A |
| Completed actions | 2 years | Archive to cold storage |
| Failed actions | 1 year | Delete after retention period |
| Action audit trail | 7 years | Required for compliance |

### Quarantine Data

| Data Type | Retention Period | Archive Policy |
|-----------|-----------------|----------------|
| Pending items | 30 days | Auto-reject if not processed |
| Approved items | 1 year | Delete after deal linkage verified |
| Rejected items | 90 days | Delete after retention period |

### Agent Data

| Data Type | Retention Period | Archive Policy |
|-----------|-----------------|----------------|
| Agent threads | 90 days inactive | Delete inactive threads |
| Agent runs | 30 days | Delete completed runs |
| HITL approvals | 2 years | Required for audit |
| Approval audit | 7 years | Required for compliance |

### RAG Data

| Data Type | Retention Period | Archive Policy |
|-----------|-----------------|----------------|
| Deal embeddings | Matches deal retention | Delete with parent deal |
| Orphan embeddings | 7 days | Auto-cleanup weekly |

## Implementation

### Automated Cleanup Jobs

The following cleanup jobs run automatically:

1. **Junk Deal Cleanup** (Weekly)
   - Deletes junk deals older than 90 days
   - Cascades to events, notes, aliases

2. **Quarantine Expiry** (Daily)
   - Marks pending items older than 30 days as expired
   - Creates notification for operators

3. **Agent Thread Cleanup** (Weekly)
   - Archives threads inactive for 90+ days
   - Preserves approval audit records

4. **RAG Orphan Cleanup** (Weekly)
   - Identifies embeddings without parent deals
   - Deletes orphan embeddings older than 7 days

### Manual Retention Actions

Operators can manually trigger:
- Early archival of deals
- Extension of retention period (requires justification)
- Immediate deletion (requires approval from data owner)

## Exceptions

### Legal Hold

Data under legal hold is exempt from automatic deletion until the hold is released. Legal holds are managed by the compliance team.

### Regulatory Requirements

Specific deals may have extended retention requirements based on:
- Industry regulations
- Contract terms
- Geographic jurisdiction

## Audit and Compliance

### Audit Trail

All retention actions are logged:
- Automatic deletions include reason and policy reference
- Manual deletions require operator approval and justification
- Archive operations record destination and timestamp

### Compliance Reports

Monthly reports include:
- Data volumes by category
- Retention policy compliance status
- Exception requests and approvals
- Upcoming scheduled deletions

## Contact

For questions about this policy, contact:
- Platform Team: platform@zakops.local
- Compliance: compliance@zakops.local

## Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-03 | REMEDIATION-V3 | Initial policy document |
