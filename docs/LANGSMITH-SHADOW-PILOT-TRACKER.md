# LangSmith Shadow-Mode Pilot Tracker

## Pilot Metadata

| Field | Value |
|-------|-------|
| **Mission** | LANGSMITH-SHADOW-PILOT-001 |
| **Start Date** | __________ (fill in when pilot begins) |
| **End Date** | __________ (start + 7 calendar days) |
| **Target Precision** | >= 80% |
| **Minimum Sample Size** | 20 reviewed items (TP + FP >= 20) |
| **Source Type** | `langsmith_shadow` |
| **Backend API** | `http://localhost:8091` |
| **Dashboard** | `http://localhost:3003/quarantine` |

---

## Measurement Rules

### What is a True Positive (TP)?

You review a `langsmith_shadow` quarantine item and determine it **IS a valid deal opportunity**. The key question to ask yourself:

> "Would I have wanted this in my pipeline if it came from email?"

If YES — it's a True Positive. Approve it in the dashboard (status -> approved).

**Examples of True Positives:**
- A real company inquiring about a product/service you sell
- A legitimate broker forwarding a deal opportunity
- A genuine RFP or RFI from a known industry contact

### What is a False Positive (FP)?

You review a `langsmith_shadow` quarantine item and determine it is **NOT a valid deal opportunity**. Reject it in the dashboard (status -> rejected).

**Examples of False Positives:**
- Spam or marketing emails misidentified as deals
- Internal communications that are not deal-related
- Duplicates of deals already in your pipeline (from a different source)
- Out-of-scope inquiries (wrong industry, wrong geography, etc.)

### What is Deferred?

You cannot make a TP/FP decision yet — you need more context, or the item is ambiguous. Deferred items are **excluded from precision calculation** until you resolve them.

**When to defer:**
- You need to check if the company is already in your CRM
- The email is truncated and you need the full thread
- You're unsure if the sender is a real broker

### Precision Formula

```
Precision = TP / (TP + FP)
```

- Deferred items are excluded from both numerator and denominator
- Target: Precision >= 80% (at least 4 out of 5 suggestions are valid)
- Precision is only meaningful when TP + FP >= 20 (minimum sample size)

### Sample Size Guidance

| Reviewed (TP+FP) | Precision Reliability |
|-------------------|-----------------------|
| < 10 | Too early — do not draw conclusions |
| 10-19 | Directional — note the trend but don't decide |
| 20-30 | Meaningful — precision is reliable enough for a Go/No-Go decision |
| 30+ | High confidence — strong basis for the decision |

---

## Daily Log

Fill in one row per day. If no items arrived on a given day, still record it (New=0, Reviewed=0).

| Day | Date | New Items | Reviewed | TP | FP | Deferred | Daily Precision | Cumulative TP | Cumulative FP | Cumulative Precision | Notes |
|-----|------|-----------|----------|----|----|----------|-----------------|---------------|---------------|----------------------|-------|
| 1 | | | | | | | | | | | |
| 2 | | | | | | | | | | | |
| 3 | | | | | | | | | | | |
| 4 | | | | | | | | | | | |
| 5 | | | | | | | | | | | |
| 6 | | | | | | | | | | | |
| 7 | | | | | | | | | | | |

**Daily Precision** = TP / (TP + FP) for that day only (skip if no reviews that day).

**Cumulative Precision** = (Sum of all TP so far) / (Sum of all TP + all FP so far).

---

## How to Review Shadow Items in the Dashboard

### Step-by-Step

1. **Open the Dashboard** — Navigate to `http://localhost:3003/quarantine`

2. **Select the Source Type filter** — In the header area, find the "Source Type" dropdown. Select **"LangSmith shadow"**.

3. **Review each pending item:**
   - Read the **Subject** — does it look like a real deal opportunity?
   - Check the **Sender** — is it a known company or broker?
   - Read the **Body Preview** — does the content describe a deal?

4. **Make your decision:**
   - If it's a valid deal -> Click **Approve** -> Record as **TP** in the daily log
   - If it's not a valid deal -> Click **Reject** -> Record as **FP** in the daily log
   - If you're unsure -> Leave it pending -> Record as **Deferred** in the daily log

5. **Update the daily log** — At the end of each review session, fill in the row for today.

6. **Calculate precision** — Use the formula: `TP / (TP + FP)`. Update both Daily and Cumulative columns.

### Tips

- Review at a consistent time each day (e.g., morning) to catch overnight injections
- Don't batch-approve or batch-reject — review each item individually
- If you defer an item, revisit it within 2 days and resolve it (TP or FP)
- The "All sources" option shows everything — use it to compare shadow items against email items

---

## Database Verification Queries

Use these to cross-check dashboard counts. Run via:
```bash
docker exec zakops-backend-postgres-1 psql -U zakops -d zakops -c "<QUERY>"
```

### Total shadow items by status
```sql
SELECT status, COUNT(*)
FROM zakops.quarantine_items
WHERE source_type = 'langsmith_shadow'
GROUP BY status
ORDER BY status;
```

### Daily injection rate
```sql
SELECT DATE(created_at) AS day, COUNT(*) AS new_items
FROM zakops.quarantine_items
WHERE source_type = 'langsmith_shadow'
GROUP BY DATE(created_at)
ORDER BY day;
```

### Approved vs rejected (raw TP/FP proxy)
```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'approved') AS approved_count,
  COUNT(*) FILTER (WHERE status = 'rejected') AS rejected_count,
  COUNT(*) FILTER (WHERE status = 'pending') AS pending_count,
  COUNT(*) AS total
FROM zakops.quarantine_items
WHERE source_type = 'langsmith_shadow';
```

### Precision calculation from database
```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'approved') AS tp,
  COUNT(*) FILTER (WHERE status = 'rejected') AS fp,
  CASE
    WHEN COUNT(*) FILTER (WHERE status IN ('approved', 'rejected')) = 0 THEN NULL
    ELSE ROUND(
      COUNT(*) FILTER (WHERE status = 'approved')::numeric /
      COUNT(*) FILTER (WHERE status IN ('approved', 'rejected'))::numeric * 100, 1
    )
  END AS precision_pct
FROM zakops.quarantine_items
WHERE source_type = 'langsmith_shadow';
```

**Note:** Database precision is a proxy. The pilot tracker is the authoritative record because the operator may have nuanced TP/FP judgments that the simple approved/rejected status doesn't capture.

---

## Observations Log

Use this section to record anything noteworthy during the pilot that isn't captured in the daily numbers.

| Date | Category | Observation |
|------|----------|-------------|
| | Injection | (e.g., "No items arrived today — check LangSmith connector") |
| | Quality | (e.g., "3 FPs were all from the same sender — possible spam pattern") |
| | UX | (e.g., "Dashboard filter reset when navigating away — annoying") |
| | Stability | (e.g., "Backend returned 500 on approval — restarted, worked after") |
| | Dedup | (e.g., "Same deal appeared twice with different message_ids") |

---

## End-of-Pilot Checklist

Before completing the pilot, verify:

- [ ] All 7 daily log rows are filled in
- [ ] Cumulative precision is calculated
- [ ] All deferred items are resolved (TP or FP) or explicitly noted as unresolvable
- [ ] Sample size requirement met (TP + FP >= 20)
- [ ] Observations log captures any notable events
- [ ] Decision packet (`LANGSMITH-SHADOW-PILOT-DECISION.md`) is filled in with final numbers

---

*Created by LANGSMITH-SHADOW-PILOT-001 — do not backdate entries*
