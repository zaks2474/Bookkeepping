# Pass 2 Red Team Review — ZakOps Roadmap Syntheses

**Reviewer Model ID:** Claude OPUS 4.5
**Timestamp (UTC):** 2026-01-24T05:00:00Z
**Review Type:** Hostile Technical Audit
**Status:** STOP-SHIP FINDINGS PRESENT

---

## 1. Findings Summary

Two Pass 1 syntheses were reviewed:
- `S_Claude_OPUS_4.5.md` (16,424 bytes)
- `S_Gemini 3.0.md` (7,262 bytes)

Both validated against 4 authoritative sources:
- `QA_REPORT.md` — HITL spike verification (PASS verdict, 14 gates)
- `DECISION-LOCK-FILE.md` — Hard constraints
- `ZakOps-Scaffold-Master-Plan-v2.md` — Implementation plan
- `ZakOps-Ultimate-Master-Document-v2.md` — Complete architecture

**Verdict:** Neither document is production-ready. Multiple stop-ship findings must be resolved.

| Synthesis | Coverage | Precision | Actionability | Ship-Ready |
|-----------|----------|-----------|---------------|------------|
| S_Claude_OPUS_4.5 | 85% | 70% | 80% | **NO** |
| S_Gemini 3.0 | 65% | 75% | 70% | **NO** |

---

## 2. Stop-Ship Findings

### SS-01: S_Gemini Missing Non-Negotiable Gates Section (CRITICAL)

**Document:** `S_Gemini 3.0.md`
**Section:** Missing entirely
**Impact:** Cannot validate production readiness without explicit pass/fail gates
**Evidence:** S_Claude §6 has 8 gates (NG-01 through NG-08); S_Gemini has ZERO

**Required Fix:**
```markdown
## 6. Non-Negotiable Gates
| Gate ID | Description | Command | Pass Criteria |
|---------|-------------|---------|---------------|
| NG-01 | Kill-9 recovery | `./tests/chaos/kill9_test.sh` | State recovered |
| NG-02 | Concurrent idempotency N=20 | `./tests/chaos/concurrent_approve.sh 20` | Exactly 1 execution |
...
```

---

### SS-02: Neither Document Specifies Encryption Key Management (CRITICAL)

**Documents:** Both
**Section:** S_Claude §7 FM-01; S_Gemini SEC-01
**Impact:** Cannot implement encryption without key strategy
**Evidence:**
- S_Claude: "Hash/encrypt tool args before storage" (WHERE DOES KEY COME FROM?)
- S_Gemini: "AES-GCM" (BETTER, but still no key management)
- DECISION-LOCK §7: "Secrets via env vars (→ Vault Phase 3)"

**Problem:** Vault is Phase 3. What secures the key in Phase 1-2?

**Required Fix (both docs):**
Add to SEC tasks:
```markdown
| SEC-04 | Encryption key bootstrap | Builder | `.env.zakops` | `CHECKPOINT_ENCRYPTION_KEY` env var, 256-bit, HSM/KMS in Phase 3 | Key presence validation |
```

Specify in Phase 1 scope:
- Key source: 256-bit random, stored in `CHECKPOINT_ENCRYPTION_KEY` env var
- Key rotation: Manual until Vault (Phase 3)
- Fallback: Fail-closed (refuse to start without key)

---

### SS-03: S_Claude FM-01 Mitigation is Vague (HIGH)

**Document:** `S_Claude_OPUS_4.5.md`
**Section:** §7 Top 10 Failure Modes, FM-01
**Impact:** "Hash/encrypt" is not an implementation spec
**Evidence:**
- S_Claude: "Hash/encrypt tool args before storage"
- S_Gemini: "AES-GCM encryption using SecurePostgresSaver wrapper"
- S_Gemini is MORE SPECIFIC, which is correct

**Required Fix:**
S_Claude FM-01 mitigation must match S_Gemini precision:
```markdown
| FM-01 | Plaintext PII in checkpoints | Data breach | PII canary gate | AES-256-GCM encryption via `SecurePostgresSaver` wrapper; key from env var |
```

---

### SS-04: Neither Document Addresses `checkpoint_writes` Table (HIGH)

**Documents:** Both
**Section:** Encryption scope
**Impact:** PII may leak through unencrypted table
**Evidence:**
- QA_REPORT §4: "checkpoint tables present: `checkpoints`, `checkpoint_writes`, `checkpoint_blobs`"
- Both docs only mention `checkpoint_blobs`
- PostgresSaver uses ALL THREE tables

**Required Fix (both docs):**
Specify encryption scope explicitly:
```markdown
Encryption scope: `checkpoint_blobs.blob` column AND `checkpoint_writes.channel_values` column
```

---

### SS-05: "No Raw Content" Definition is Ambiguous (MEDIUM)

**Documents:** Both
**Section:** Observability
**Impact:** Implementation variance; possible data leaks
**Evidence:**
- DECISION-LOCK §5: "NEVER log raw prompts/responses (hash + length only)"
- S_Claude §7 FM-10: "safe_logger wrapper; hash+length only"
- Neither specifies: tool args? tool results? deal content? all?

**Required Fix (both docs):**
Add explicit definition:
```markdown
### "No Raw Content" Policy Scope
MUST hash+length only:
- LLM prompts (user messages + system prompts)
- LLM responses (assistant messages)
- Tool arguments (all tiers: READ/WRITE/CRITICAL)
- Tool results (all tiers)
- Deal content (titles, descriptions, values)
- Document text (extracted content)

MAY log in plaintext:
- Thread IDs, deal IDs (opaque identifiers)
- Timestamps
- Status strings (awaiting_approval, completed, error)
- Error codes (not error messages with user data)
```

---

## 3. Contradictions

### C-01: Phase Naming Inconsistency

| Source | Phase 1 Name |
|--------|--------------|
| S_Claude | "Production Integration" |
| S_Gemini | "Production Hardening (Security & Core)" |
| Scaffold-Plan | Phase 0-6 structure (Phase 1 = "Core Surgery") |

**Resolution Rule:** Scaffold-Plan is authoritative for phase definitions. Both S docs should align OR explicitly note deviation with rationale.

---

### C-02: Concurrency Test Threshold Mismatch

| Source | Concurrent Approves | Evidence |
|--------|---------------------|----------|
| QA_REPORT | N=20 | §3: "Concurrency N=20: exactly one 200, rest 409" |
| S_Claude NG-02 | N=50 | §6: "Concurrent idempotency N=50" |
| S_Gemini | N=20 (implicit) | References spike results |

**Issue:** S_Claude bumps N=20→N=50 WITHOUT JUSTIFICATION

**Resolution Rule:** Either:
1. Match spike (N=20) and note "validated"
2. Bump to N=50 with explicit rationale: "Production headroom: 2.5× spike threshold"

---

### C-03: Duration Estimates Conflict

| Source | Phase 1 Duration |
|--------|------------------|
| S_Claude | "1 Week" |
| S_Gemini | Not specified |
| Scaffold-Plan | "2-day time-box" for HITL spike, then Phase 0 |

**Resolution Rule:** Scaffold-Plan is authoritative. Both docs should reference it explicitly.

---

## 4. Gaps (Missing Pieces)

### M-01: Deal API Endpoint Specifications Missing

**Documents:** Both
**Impact:** Cannot implement tools without knowing endpoints
**Source Reality:** MDv2 §5.2 specifies:
```
| Agent Tool | Calls Deal API Endpoint | Method |
|------------|-------------------------|--------|
| list_deals | GET /deals | Direct HTTP |
| get_deal | GET /deals/{id} | Direct HTTP |
| transition_deal | POST /deals/{id}/transition | Direct HTTP |
```

**Required Fix:** Copy from MDv2 §5.2 into both roadmaps' API task section.

---

### M-02: Error Handling for External Services Undefined

**Documents:** Both
**Impact:** No retry logic = cascading failures
**Missing specs:**
- Deal API timeout (suggest: 10s)
- Deal API retry policy (suggest: 3× exponential backoff)
- vLLM timeout (suggest: 120s for generation)
- Circuit breaker thresholds

**Required Fix:** Add to Tool Gateway section:
```markdown
### External Service Resilience
| Service | Timeout | Retries | Backoff | Circuit Breaker |
|---------|---------|---------|---------|-----------------|
| Deal API | 10s | 3 | 1s/2s/4s | 5 failures → 30s open |
| vLLM | 120s | 2 | 5s/10s | 3 failures → 60s open |
| MCP | 30s | 3 | 1s/2s/4s | 5 failures → 30s open |
```

---

### M-03: Token Counting Not Specified

**Documents:** Both
**Impact:** vLLM OOM under large context
**Evidence:**
- DECISION-LOCK §1: "Context 32,768 tokens max"
- S_Gemini FM-07: "Token counting middleware + Context pruning"
- S_Claude: No mention of token counting

**Required Fix:** Add task:
```markdown
| CTX-001 | Token counting middleware | Builder | `app/core/middleware/context.py` | Reject >32K tokens pre-request | Unit test with 33K token input |
```

---

### M-04: Approval Expiry Implementation Missing

**Documents:** S_Claude mentions HITL-002 briefly; S_Gemini mentions TTL daemon
**Impact:** Orphaned approvals block workflows indefinitely
**Missing specs:**
- Expiry threshold (24h per Decision Lock inference)
- Auto-reject vs auto-expire distinction
- Notification on expiry
- Audit log entry for expiry

**Required Fix:** Expand HITL-002:
```markdown
| HITL-002 | Approval expiry | Builder | `app/workers/approval_expiry.py` |
  - TTL: 24 hours from `requested_at`
  - Action: Set status='expired', emit `approval.expired` event
  - Audit: Log expiry with original approval details
  - Resume: Graph terminates with "approval_expired" error
| Cron: `0 * * * *` (hourly), verify expired approvals processed |
```

---

### M-05: Phase 0 (Fork & Setup) Missing from Both

**Documents:** Both
**Source:** Scaffold-Plan §4 has explicit Phase 0 checklist
**Impact:** Cannot start Phase 1 without completing fork

**Required Fix:** Both docs need Phase 0 section:
```markdown
### Phase 0: Fork & Environment Setup (Pre-req)
- [ ] Fork wassim249/fastapi-langgraph...
- [ ] Generate SBOM
- [ ] Run license scan (no GPL/AGPL)
- [ ] Create PORTS.md
- [ ] Update docker-compose.yml
- [ ] Create .env.zakops
- [ ] Run bring-up tests
```

---

## 5. Gate Failures

### G-01: S_Gemini Has ZERO Non-Negotiable Gates

**Impact:** FATAL — cannot determine ship readiness
**Required Fix:** Add complete NG section (see SS-01)

---

### G-02: Gate Scripts Don't Exist

**Documents:** Both
**Evidence:**
- S_Claude: `./scripts/pii_canary_gate.sh`, `./scripts/health_monitor.sh`
- S_Gemini: `./scripts/gates/run_pii_canary.sh`, `./scripts/gates/verify_*`
- NEITHER checks if scripts exist

**Required Fix:** Add script creation to task backlog:
```markdown
| GATE-001 | Create gate scripts | Builder | `scripts/gates/` | All gate commands executable | `ls -la scripts/gates/*.sh` |
```

---

### G-03: S_Claude NG-02 Threshold Not Validated

**Issue:** Bumped from N=20 (spike) to N=50 (roadmap) without test
**Required Fix:** Either:
1. Keep N=20 (validated), OR
2. Add validation task: "Run N=50 concurrency test before Phase 1 acceptance"

---

### G-04: PII Canary Gate Has No Pattern Definition

**Documents:** Both mention PII canary
**Missing:** What patterns to scan for?
**Required Fix:**
```markdown
PII Canary Patterns (regex):
- SSN: \b\d{3}-\d{2}-\d{4}\b
- Credit Card: \b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b
- Email: \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b
- Phone: \b\d{3}[-.]?\d{3}[-.]?\d{4}\b
- Deal values: \$[\d,]+(\.\d{2})?
```

---

## 6. Fix Plan (Priority Order)

### Priority 0: Stop-Ship (Must fix before ANY work)

| Fix ID | Document | Section | Edit Required |
|--------|----------|---------|---------------|
| FIX-SS01 | S_Gemini | NEW §6 | Add complete Non-Negotiable Gates section from S_Claude |
| FIX-SS02 | Both | SEC tasks | Add `CHECKPOINT_ENCRYPTION_KEY` env var spec |
| FIX-SS03 | S_Claude | §7 FM-01 | Change "hash/encrypt" → "AES-256-GCM via SecurePostgresSaver" |
| FIX-SS04 | Both | Encryption scope | Add `checkpoint_writes.channel_values` to encryption scope |
| FIX-SS05 | Both | Observability | Add explicit "No Raw Content" scope definition |

### Priority 1: Contradictions

| Fix ID | Document | Edit Required |
|--------|----------|---------------|
| FIX-C01 | Both | Align phase naming with Scaffold-Plan OR document deviation |
| FIX-C02 | S_Claude | Either match N=20 from spike OR add rationale for N=50 |
| FIX-C03 | Both | Add duration estimates aligned with Scaffold-Plan |

### Priority 2: Gaps

| Fix ID | Document | Edit Required |
|--------|----------|---------------|
| FIX-M01 | Both | Copy Deal API endpoint table from MDv2 §5.2 |
| FIX-M02 | Both | Add External Service Resilience table |
| FIX-M03 | Both | Add token counting task |
| FIX-M04 | Both | Expand approval expiry specification |
| FIX-M05 | Both | Add Phase 0 section |

### Priority 3: Gate Integrity

| Fix ID | Document | Edit Required |
|--------|----------|---------------|
| FIX-G02 | Both | Add GATE-001 task for script creation |
| FIX-G04 | Both | Add PII canary pattern definitions |

---

## 7. Questions / Tests Required Before Phase 1

| ID | Question | Test | Owner |
|----|----------|------|-------|
| QT-01 | Does SecurePostgresSaver add >50ms latency? | Benchmark 1MB checkpoint save | Builder |
| QT-02 | Is `checkpoint_writes` column encrypted by PostgresSaver? | Inspect table after checkpoint | Builder |
| QT-03 | Does Deal API require JWT or different auth? | `curl -H "Authorization: Bearer $JWT" localhost:8090/deals` | Builder |
| QT-04 | Can vLLM Hermes parser handle nested schemas? | Run 10-prompt tool-calling suite | QA |
| QT-05 | Are all gate scripts executable from repo root? | `bash -n scripts/gates/*.sh` | CI |
| QT-06 | What is actual N=50 concurrency result? | Run extended test from spike | QA |

---

## 8. Coverage Map

### S_Claude_OPUS_4.5.md

| Section | Coverage | Quality | Notes |
|---------|----------|---------|-------|
| Executive Summary | ✅ Good | Accurate | Links to QA_REPORT correctly |
| Baseline | ✅ Good | Detailed | All 14 gates listed |
| Hard Constraints | ✅ Good | Complete | Matches DECISION-LOCK |
| Phase Plan | ⚠️ Partial | Misaligned | Doesn't match Scaffold-Plan structure |
| Task Backlog | ✅ Good | MECE | Well-structured IDs |
| Non-Negotiable Gates | ✅ Good | Specific | Commands included |
| Failure Modes | ⚠️ Partial | Vague mitigations | FM-01 is too vague |
| Risks | ✅ Good | Reasonable | 4 risks well-defined |
| Evidence Index | ✅ Good | Traceable | Source sections cited |

### S_Gemini 3.0.md

| Section | Coverage | Quality | Notes |
|---------|----------|---------|-------|
| Executive Summary | ✅ Good | Focused | Security-first framing |
| Baseline | ✅ Good | Concise | Key capabilities listed |
| Hard Constraints | ✅ Good | Complete | Matches DECISION-LOCK |
| Phase Plan | ⚠️ Partial | Less detail | Only 3 phases |
| Task Backlog | ⚠️ Partial | Smaller | Fewer tasks than S_Claude |
| Non-Negotiable Gates | ❌ MISSING | FATAL | No gates section |
| Failure Modes | ✅ Good | Specific | 10 modes with mitigations |
| Open Questions | ⚠️ Partial | Only 2 | Should be more |
| Evidence Index | ⚠️ Partial | Sparse | Only 4 entries |

---

## 9. Appendix: Source Document Checksums

| Document | SHA256 (first 16 chars) | Lines |
|----------|-------------------------|-------|
| QA_REPORT.md | (reference only) | 122 |
| DECISION-LOCK-FILE.md | (reference only) | 309 |
| ZakOps-Scaffold-Master-Plan-v2.md | (reference only) | 996 |
| ZakOps-Ultimate-Master-Document-v2.md | (reference only) | >2000 |
| S_Claude_OPUS_4.5.md | f791430f50962... | 406 |
| S_Gemini 3.0.md | (to compute) | 162 |

---

**Document End**
*Red Team Review Completed: 2026-01-24T05:00:00Z*
*Reviewer: Claude OPUS 4.5*
