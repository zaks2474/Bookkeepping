# LangSmith Shadow-Mode Pilot — Go/No-Go Decision Packet

## Section 1: Pilot Summary

| Field | Value |
|-------|-------|
| **Mission** | LANGSMITH-SHADOW-PILOT-001 |
| **Pilot Start Date** | __________ |
| **Pilot End Date** | __________ |
| **Total Items Injected** | __________ |
| **Total Items Reviewed (TP + FP)** | __________ |
| **Items Deferred (unresolved)** | __________ |
| **True Positives (TP)** | __________ |
| **False Positives (FP)** | __________ |
| **Overall Precision** | __________% |
| **Target Met (>= 80%)?** | [ YES / NO ] |
| **Sample Size Met (>= 20)?** | [ YES / NO ] |

---

## Section 2: Precision Analysis

### Daily Precision Trend

Copy from the pilot tracker's daily log:

| Day | Date | Reviewed | TP | FP | Daily Precision | Cumulative Precision |
|-----|------|----------|----|----|-----------------|----------------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |

### Trend Assessment

- Is precision improving, stable, or declining over the week? __________
- Were there any days with significantly lower precision? If so, what caused it? __________
- Did the cumulative precision stabilize by Day 5-7, or was it still fluctuating? __________

### Target Evaluation

| Criterion | Result | Pass? |
|-----------|--------|-------|
| Overall precision >= 80% | __________% | [ YES / NO ] |
| Sample size >= 20 reviewed items | __________ items | [ YES / NO ] |
| No single day with precision < 50% | __________ | [ YES / NO ] |
| Precision trend is stable or improving | __________ | [ YES / NO ] |

---

## Section 3: Stability Observations

### System Reliability

| Check | Observation |
|-------|-------------|
| Backend uptime during pilot | [ No outages / Brief outage on ____ / Extended outage ] |
| Injection success rate | [ All injections succeeded / ____ failures observed ] |
| Dedup behavior | [ Working correctly / Issues observed: __________ ] |
| Dashboard filter working | [ Yes / No — describe issue: __________ ] |
| Correlation IDs intact | [ Verified / Not checked / Issues: __________ ] |
| Rate limiter triggered | [ Never / ____ times — describe context ] |

### Data Quality

| Check | Observation |
|-------|-------------|
| Duplicate deals (same deal, different message_ids) | [ None / ____ instances ] |
| Items with missing/truncated content | [ None / ____ instances ] |
| Sender domain diversity | [ Good variety / Concentrated on ____ domains ] |
| False positives — common patterns | [ No pattern / Pattern: __________ ] |

### UX Observations

| Check | Observation |
|-------|-------------|
| Dashboard filter usability | [ Good / Needs improvement: __________ ] |
| Review workflow friction | [ Smooth / Pain points: __________ ] |
| Time spent per review | [ ~____ seconds per item ] |
| Missing information for decisions | [ None / Needed: __________ ] |

---

## Section 4: Decision Matrix

### Option A: GO LIVE

**Criteria — ALL must be met:**
- [ ] Overall precision >= 80%
- [ ] Sample size >= 20 reviewed items
- [ ] No critical stability issues during pilot
- [ ] Precision trend is stable or improving (not declining)
- [ ] No more than 1 brief backend outage during the week
- [ ] Operator is confident in the review workflow

**If GO LIVE:**
1. Change LangSmith injector source_type from `langsmith_shadow` to `langsmith_live`
2. Shadow items remain in quarantine but are no longer injected
3. Live items appear in the main quarantine queue alongside email items
4. Create mission: LANGSMITH-LIVE-PROMOTION-001 to execute the cutover
5. Continue monitoring precision for 2 more weeks at live volume

---

### Option B: EXTEND

**Criteria — ANY triggers EXTEND:**
- [ ] Precision is borderline (70-80%) — not clearly above or below target
- [ ] Sample size < 20 reviewed items (not enough data to decide)
- [ ] Precision trend is fluctuating and hasn't stabilized
- [ ] Minor stability issues that may resolve with more time

**If EXTEND:**
1. Continue shadow mode for one more week (same setup, same tracker)
2. Add a "Week 2" section to the pilot tracker
3. Re-evaluate at end of Week 2 with combined data
4. If still borderline after Week 2 → move to REFINE

---

### Option C: REFINE

**Criteria — ANY triggers REFINE:**
- [ ] Precision < 70% (too many false positives)
- [ ] Critical stability issues (repeated outages, data loss, broken dedup)
- [ ] Declining precision trend (getting worse, not better)
- [ ] Fundamental data quality issues (most items are spam/irrelevant)

**If REFINE:**
1. Stop LangSmith injections immediately
2. Analyze false positive patterns — what types of items are being rejected?
3. Feed findings back to LangSmith configuration/prompts
4. Create mission: LANGSMITH-REFINE-001 to address root causes
5. Re-run pilot after refinements are applied

---

## Section 5: Recommended Next Action

**Decision:** [ GO LIVE / EXTEND / REFINE ]

**Justification:**

_________________________________________________________________________

_________________________________________________________________________

_________________________________________________________________________

**Specific next steps:**

1. __________
2. __________
3. __________

---

## Section 6: Approvals

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Operator / Decision Maker | __________ | __________ | __________ |

### Notes

_________________________________________________________________________

---

*Template created by LANGSMITH-SHADOW-PILOT-001. Complete this document after the one-week pilot using data from LANGSMITH-SHADOW-PILOT-TRACKER.md.*
