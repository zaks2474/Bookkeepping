# Email Triage Service Level Objectives (SLOs)

**Service:** ZakOps Email Triage Pipeline
**Phase:** P8-01 (Operational Excellence Gate)
**Created:** 2026-02-15
**Review Cadence:** Monthly

---

## SLI Definitions

| SLI | Definition | Measurement Method |
|-----|-----------|-------------------|
| Injection Latency | Time from bridge tool call to quarantine_items INSERT committed | Server-side: timestamp delta in bridge response |
| UI Load Time | Time from page navigation to quarantine list fully rendered | Client-side: Next.js page load metric |
| Approve-to-Deal Latency | Time from operator approve click to deal record created | Server-side: approve endpoint response time |
| Pipeline Uptime | Percentage of time the injection pipeline accepts writes | Synthetic probe: POST to health endpoint every 60s |
| Classification Accuracy | Correct classifications / Total classifications | Operator feedback on shadow items (weekly review) |

---

## SLO Targets

| SLO | Target | Window | Measurement |
|-----|--------|--------|-------------|
| Injection Latency (p95) | < 30 seconds | 30 days | `histogram_quantile(0.95, injection_duration_seconds)` |
| Injection Latency (p99) | < 60 seconds | 30 days | `histogram_quantile(0.99, injection_duration_seconds)` |
| UI Load Time (p95) | < 2 seconds | 30 days | Next.js TTFB + hydration |
| Approve-to-Deal (p95) | < 3 seconds | 30 days | `histogram_quantile(0.95, approve_duration_seconds)` |
| Pipeline Uptime | 99.5% | 30 days | `successful_health_checks / total_health_checks` |
| Classification Accuracy | > 85% | 7 days | `correct_classifications / total_reviewed` |

---

## Error Budget

| SLO | Budget (30d) | Equivalent Downtime |
|-----|-------------|-------------------|
| Pipeline Uptime (99.5%) | 0.5% | ~3.6 hours/month |
| Injection Latency (p95 < 30s) | 5% of requests | ~36 slow injections per 720 |
| UI Load (p95 < 2s) | 5% of loads | ~36 slow loads per 720 |

### Budget Consumption Thresholds

| Budget Remaining | State | Action |
|-----------------|-------|--------|
| > 50% | GREEN | Normal operations |
| 25-50% | YELLOW | Investigate recent changes |
| 10-25% | ORANGE | Feature freeze, reliability focus |
| < 10% | RED | Incident mode, kill switch standby |

---

## Monitoring Points

### Injection Pipeline
- **Probe:** Synthetic health check every 60 seconds
- **Alert:** Pipeline down for > 2 consecutive checks (2 min)
- **Kill switch alert:** `email_triage_writes_enabled` toggled to OFF

### Queue Depth
- **Metric:** Count of `status='pending'` quarantine items
- **Warning:** > 20 pending items for > 30 minutes
- **Critical:** > 50 pending items for > 15 minutes

### Operator Throughput
- **Metric:** Items processed per hour per operator
- **Baseline:** 10-15 items/hour (single operator)
- **Alert:** < 5 items/hour sustained for > 2 hours (potential UX issue)

---

## Capacity Planning

| Scenario | Volume | Operators | Expected p95 Latency |
|----------|--------|-----------|---------------------|
| Low | 100 emails/day | 1-2 | < 15s injection, < 1s UI |
| Normal | 250 emails/day | 2-3 | < 20s injection, < 1.5s UI |
| High | 500 emails/day | 3-5 | < 30s injection, < 2s UI |
| Burst | 50 emails in 5 min | 3-5 | < 45s injection, < 2.5s UI |

---

## Shadow-to-Live Graduation Criteria

Before transitioning from `shadow_mode=ON` to live operation:

1. Classification accuracy > 85% over 7-day window
2. Zero required-field NULL violations in 7-day window
3. Entity extraction recall > 75% (company_name, broker_name)
4. All SLOs met under simulated load (P8-T3)
5. Backup/restore drill completed successfully (P8-T4)
6. Operator approval of triage quality (manual review)

---

## References

- Platform SLOs: `/home/zaks/bookkeeping/docs/ZAKOPS_PRODUCTION_READINESS_ROADMAP_v2.md` (Section 0.1)
- Alerting Rules: `/home/zaks/bookkeeping/docs/EMAIL-TRIAGE-ALERTING.md`
- Data Retention: `/home/zaks/bookkeeping/docs/DATA-RETENTION-POLICY.md`
