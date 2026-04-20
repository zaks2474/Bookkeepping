Pass 1 report is complete. Here's the summary:

## Pass 1 Report Written

**Location:** `docs/_tripass_runs/TP-20260218-194105/01_pass1/claude_report.md`
(Needs to be copied to `/home/zaks/bookkeeping/docs/_tripass_runs/TP-20260218-194105/01_pass1/claude_report.md` — sandbox restriction prevented direct write)

### 8 Primary Findings:

1. **Single-item approve drops all extraction_evidence** — metadata, broker, company_info get minimal data despite extraction_evidence being available (`SELECT *`)
2. **Bulk approve is worse** — doesn't even SELECT extraction_evidence, writes empty `{}` for company_info and broker
3. **Thread-linked path doesn't enrich existing deals** — attaches as timeline event but never merges extraction data into the deal
4. **coerceToNumber fails on "$2.5M"/"$500K"** — `parseFloat("2.5M")` returns `2.5`, off by 6 orders of magnitude
5. **Bulk approve skips thread deduplication** — always creates new deals, can produce duplicates
6. **DealDetailSchema strips unknown fields** — no `.passthrough()` on metadata/broker/company_info sub-schemas
7. **revenue and multiple are schema-defined but never rendered** in the deal UI
8. **Backfill JSONB `||` overwrites operator edits** — must use null-conditional merge

### 6 Adjacent Observations (out of scope):
- state_machine contract mismatch, bulk audit trail inconsistency, PATCH full-replace risk, missing location population path, OpenAPI schema gaps, zero test coverage for quarantine-to-deal data flow

### Acceptance Gate Status:
- TG-1 (field mapping): PARTIAL RISK
- TG-2 (currency parsing): AT RISK
- TG-3 (backfill safety): AT RISK
- TG-4 (bulk approve): BLOCKED
- TG-5 (manual deals): PASS
- TG-6 (thread-match): PARTIAL
