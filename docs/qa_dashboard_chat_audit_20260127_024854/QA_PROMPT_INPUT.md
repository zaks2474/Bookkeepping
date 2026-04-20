# UNIFIED QA PROMPT — ZAKOPS DASHBOARD/CHAT AUDIT

- Generated at (UTC): 2026-01-27T04:00:00Z
- Base Template: FINAL_QA_PROMPT v1.0
- Target: ZakOps Dashboard Deal Display + Chat Agent Fix
- Status: READY FOR EXECUTION

---

# ADVERSARIAL QA AUDIT PROMPT — ZERO TRUST | INDEPENDENT VERIFICATION

---

## SECTION 0: AUDITOR ROLE DEFINITION

**YOU ARE AN ADVERSARIAL QA AUDITOR.**

- **YOUR MISSION**: Verify that the Builder completed the ZakOps Dashboard/Chat fix correctly.
- **YOUR STANCE**: ZERO TRUST. Assume EVERYTHING is fabricated until YOU prove it yourself through independent verification.
- **YOUR GOAL**: Find EVERY lie, shortcut, fake artifact, unfixed bug, and incomplete deliverable. The Builder WANTS to fool you. Don't let them.
- **YOUR AUTHORITY**: You have VETO power. If you find ANY violation, the mission is NOT complete, regardless of what the Builder claims.
- **YOUR OUTPUT**: A detailed audit report with PASS/FAIL verdict and evidence.

---

## SECTION 0.5: CRITICAL PRE-AUDIT ALERT

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🚨 CRITICAL ARCHITECTURAL CONCERN 🚨                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   THE BUILDER MADE A CLAIM THAT DIRECTLY CONTRADICTS MISSION REQUIREMENTS:   ║
║                                                                               ║
║   BUILDER CLAIM:                                                             ║
║   "Fix: Started the service → Port 8090 now responds with {"status":"ok"}"   ║
║   "Root Cause: claude-code-api.service was inactive (dead)"                  ║
║                                                                               ║
║   MISSION REQUIREMENT:                                                        ║
║   "Forbidden Ports (Legacy - MUST BE DEAD): 8090 - Legacy Python backend"    ║
║   "Agent API should be on port 8095"                                         ║
║                                                                               ║
║   ⚠️  THIS IS A MASSIVE RED FLAG ⚠️                                          ║
║                                                                               ║
║   POSSIBLE EXPLANATIONS:                                                     ║
║   1. Builder started the WRONG service (legacy instead of new agent API)     ║
║   2. Builder violated architectural constraints by reviving legacy system    ║
║   3. Builder is confused about port numbers                                  ║
║   4. Builder fabricated the fix claim entirely                              ║
║                                                                               ║
║   YOUR PRIORITY: Investigate this FIRST. If port 8090 is now alive,         ║
║   this may be a SCOPE VIOLATION and ARCHITECTURAL BREACH, not a fix.        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## SECTION 1: AUDITOR MINDSET (ZERO TRUST RULES)

### RULE 1: NEVER TRUST BUILDER CLAIMS
- Builder says "fixed" → Assume it's NOT fixed until YOU verify
- Builder provides screenshot → Assume it's FAKE until YOU reproduce
- Builder shows output → Assume it's FABRICATED until YOU re-run
- Builder says "tested" → Assume it's NOT tested until YOU test

### RULE 2: INDEPENDENT VERIFICATION
- YOU must run every verification command yourself
- YOU must check every file exists and has correct content
- YOU must test every endpoint/feature independently
- YOU must query the database directly to verify state

### RULE 3: ASSUME ADVERSARIAL BUILDER
- Builder may have created fake files with plausible names
- Builder may have hardcoded responses to fool tests
- Builder may have modified only the test, not the actual code
- Builder may have created artifacts that look correct but aren't
- Builder may have cherry-picked passing scenarios
- **Builder may have "fixed" by reviving forbidden legacy systems**

### RULE 4: VERIFY THE VERIFIERS
- Check that test scripts actually test what they claim
- Check that verification commands aren't rigged
- Check that "passing" output isn't hardcoded
- Check that artifacts weren't backdated or fabricated

### RULE 5: NO BENEFIT OF THE DOUBT
- Ambiguous evidence = FAIL
- Missing evidence = FAIL
- Incomplete evidence = FAIL
- "Should work" = FAIL

### RULE 6: TRANSCRIPT IS ADVISORY ONLY
- Treat the Builder's transcript as a hint, not truth
- The ledger and artifacts are primary sources
- Any discrepancy between transcript and artifacts = FAIL

---

## SECTION 2: FRAUD DETECTION PATTERNS

### Fake File Indicators
- File exists but is empty or near-empty
- File has plausible name but nonsensical content
- File timestamps don't match claimed work timeline
- File contains TODO/placeholder comments where code should be
- File imports don't match actual dependencies
- File has syntax errors (never actually ran)

### Fake Output Indicators
- Output is too perfect (real systems have variance)
- Output doesn't match what command actually produces
- Timestamps in output are inconsistent
- Output contains "example" or template markers
- Output references files/paths that don't exist

### Fake Fix Indicators
- Fix only works for specific test case shown
- Fix breaks when tested with different inputs
- Fix is actually a workaround that masks the problem
- Fix introduces new errors not shown by Builder
- Fix only works because of cached state
- **Fix violates architectural constraints (e.g., reviving forbidden services)**

### Evidence Manipulation Indicators
- Evidence Block missing required fields
- Screenshots are cropped suspiciously
- Logs are truncated at convenient points
- Hashes don't match actual file contents
- Forensic ledger has gaps or inconsistencies

### Scope Violation Indicators
- Files modified that weren't in approved scope
- Tree hash changed more than scope hash
- Unexplained new files outside approved directories
- Configuration changes not documented
- **Forbidden services started instead of correct services**

---

## SECTION 3: AUDIT INPUTS

### A) Builder's Claimed Fixes

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    BUILDER CLAIMS TO VERIFY                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   PROBLEM 1: Dashboard Shows "0 Deals"                                       ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║   Builder's Verification Table:                                              ║
║   ┌──────────────────────┬────────────────────┐                              ║
║   │ Database             │ ✅ 3 deals exist   │                              ║
║   │ Backend API (8091)   │ ✅ Returns 3 deals │                              ║
║   │ Dashboard API (3003) │ ✅ Returns 3 deals │                              ║
║   │ Frontend Schema      │ ❌ BUG FOUND       │                              ║
║   └──────────────────────┴────────────────────┘                              ║
║                                                                               ║
║   Claimed Root Cause:                                                        ║
║   - File: api.ts:56                                                          ║
║   - Issue: Zod schema expected broker: z.string()                            ║
║   - Reality: Backend returned broker: {} (object)                            ║
║   - Effect: Zod validation failed silently → empty array → "0 deals"        ║
║                                                                               ║
║   Claimed Fix:                                                               ║
║   - Added coerceBrokerToString() preprocessor                                ║
║   - File: apps/dashboard/src/lib/api.ts                                      ║
║                                                                               ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║                                                                               ║
║   PROBLEM 2: Chat "AI Agent Unavailable"                                     ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║   Claimed Root Cause:                                                        ║
║   - claude-code-api.service was inactive (dead)                              ║
║                                                                               ║
║   Claimed Fix:                                                               ║
║   - Started the service                                                      ║
║   - Port 8090 now responds with {"status":"ok"}                              ║
║                                                                               ║
║   ⚠️ RED FLAG: Port 8090 is FORBIDDEN (legacy backend)                       ║
║   Agent API should be on port 8095, not 8090!                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### B) Builder's Claimed Artifacts

```
Completion Packet Location: /home/zaks/completion_packet/

Claimed Contents:
- FIX_SUMMARY.md - Full documentation
- artifacts/001_db_deals_query.txt - Database evidence
- artifacts/002_backend_api_deals.txt - Backend API evidence
- artifacts/003_dashboard_api_deals.txt - Dashboard API evidence
- artifacts/004_port_check_post_fix.txt - Port status after fix
- artifacts/005_code_fix_diff.patch - Git diff of code change
```

### C) Environment Facts

| Parameter | Value |
|-----------|-------|
| Repo Root | `/home/zaks/zakops-agent-api` |
| Runtime | Docker (containerized services) + Next.js Dashboard |
| Dashboard Port | 3003 |
| Backend API Port | 8091 |
| Agent API Port | 8095 (CORRECT) |
| PostgreSQL Port | 5432 |
| Redis Port | 6379 |
| **FORBIDDEN Port** | **8090 (Legacy Python backend - MUST BE DEAD)** |
| Database | PostgreSQL `zakops` |
| Completion Packet | `/home/zaks/completion_packet/` |

### D) Acceptance Criteria (Original Mission)

| ID | Criterion | Testable Condition |
|----|-----------|-------------------|
| AC-1 | Deal Display Fixed | Dashboard shows correct deal count matching database |
| AC-2 | Deals Page Works | /deals page shows deals with correct data |
| AC-3 | Chat Responds | Chat page shows actual response, not "No response received" |
| AC-4 | No Warning Banner | "AI agent service unavailable" warning does NOT appear |
| AC-5 | End-to-End Verified | DB → Backend → Dashboard API → Frontend → UI path traced |

### E) Signature Error Strings (Must Be Absent After Fix)

- `"No response received."`
- `"AI agent service is currently unavailable"`
- `"0 Deals"` (when deals exist in DB)
- `"No deals found"` (when deals exist in DB)

---

## SECTION 4: AUDITOR PRIME DIRECTIVE

- You must not accept any **paraphrase as proof**.
- You must reject any "claim" that lacks a matching **Evidence Block**.
- If you cannot validate an artifact, mark it **UNVERIFIABLE** → which is **FAIL**.
- Any **fabricated evidence = AUTO-FAIL**.
- **Transcript and summaries are advisory only** — rely on independent checks and artifact validation.
- **Architectural violations = AUTO-FAIL** (e.g., starting forbidden port 8090)

---

## SECTION 5: AUDIT PROCEDURE (8 PHASES)

### PHASE 0: CLAIM INVENTORY

**Collect and verify these specific Builder claims:**

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PHASE 0: CLAIM INVENTORY CHECKLIST                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   CLAIMED FIXES:                                                             ║
║   [ ] 1. "Database has 3 deals" - Verify with direct SELECT                 ║
║   [ ] 2. "Backend API returns 3 deals" - Test :8091/api/deals               ║
║   [ ] 3. "Dashboard API returns 3 deals" - Test :3003/api/deals             ║
║   [ ] 4. "Zod schema bug fixed in api.ts:56" - Check file exists/changed    ║
║   [ ] 5. "coerceBrokerToString() added" - Verify function exists            ║
║   [ ] 6. "Port 8090 responds with status ok" - Test (BUT THIS IS FORBIDDEN) ║
║                                                                               ║
║   CLAIMED ARTIFACTS:                                                         ║
║   [ ] FIX_SUMMARY.md exists and has content                                 ║
║   [ ] artifacts/001_db_deals_query.txt exists                               ║
║   [ ] artifacts/002_backend_api_deals.txt exists                            ║
║   [ ] artifacts/003_dashboard_api_deals.txt exists                          ║
║   [ ] artifacts/004_port_check_post_fix.txt exists                          ║
║   [ ] artifacts/005_code_fix_diff.patch exists and is valid patch           ║
║                                                                               ║
║   MISSING FROM BUILDER'S CLAIMS (RED FLAGS):                                 ║
║   [ ] ❌ No ledger.jsonl mentioned                                          ║
║   [ ] ❌ No evidence_manifest.sha256 mentioned                              ║
║   [ ] ❌ No verification_script.sh mentioned                                ║
║   [ ] ❌ No HAR captures mentioned                                          ║
║   [ ] ❌ No browser screenshots mentioned                                   ║
║   [ ] ❌ No console captures mentioned                                      ║
║   [ ] ❌ No pre/post checksum reports mentioned                             ║
║   [ ] ❌ No red-to-green demonstration mentioned                            ║
║   [ ] ❌ No 3-run stability test mentioned                                  ║
║   [ ] ❌ No restart persistence test mentioned                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### PHASE 1: ARTIFACT EXISTENCE VERIFICATION

**Run these commands yourself:**

```bash
#!/bin/bash
# PHASE 1: Artifact Existence Check

PACKET_DIR="/home/zaks/completion_packet"

echo "=== PHASE 1: ARTIFACT EXISTENCE ==="

# Check completion packet directory exists
if [ -d "$PACKET_DIR" ]; then
    echo "✅ Completion packet directory exists"
else
    echo "❌ FAIL: Completion packet directory MISSING"
    exit 1
fi

# Check each claimed artifact
CLAIMED_FILES=(
    "FIX_SUMMARY.md"
    "artifacts/001_db_deals_query.txt"
    "artifacts/002_backend_api_deals.txt"
    "artifacts/003_dashboard_api_deals.txt"
    "artifacts/004_port_check_post_fix.txt"
    "artifacts/005_code_fix_diff.patch"
)

for file in "${CLAIMED_FILES[@]}"; do
    FULL_PATH="$PACKET_DIR/$file"
    if [ -f "$FULL_PATH" ]; then
        SIZE=$(wc -c < "$FULL_PATH")
        if [ "$SIZE" -lt 10 ]; then
            echo "🚨 SUSPICIOUS: $file exists but is nearly empty ($SIZE bytes)"
        else
            echo "✅ EXISTS: $file ($SIZE bytes)"
        fi
    else
        echo "❌ MISSING: $file"
    fi
done

# Check for REQUIRED artifacts that Builder didn't mention
REQUIRED_BUT_MISSING=(
    "ledger.jsonl"
    "evidence_manifest.sha256"
    "verification_script.sh"
)

echo ""
echo "=== CHECKING REQUIRED ARTIFACTS (not mentioned by Builder) ==="
for file in "${REQUIRED_BUT_MISSING[@]}"; do
    if [ -f "$PACKET_DIR/$file" ]; then
        echo "✅ EXISTS: $file (Builder didn't mention but exists)"
    else
        echo "❌ MISSING REQUIRED: $file"
    fi
done

# Check for placeholder content
echo ""
echo "=== CHECKING FOR PLACEHOLDER CONTENT ==="
grep -r "TODO\|FIXME\|placeholder\|implement" "$PACKET_DIR" 2>/dev/null && echo "🚨 PLACEHOLDER CONTENT FOUND"
```

### PHASE 2: INDEPENDENT FUNCTIONAL VERIFICATION

**YOU must run these tests yourself:**

```bash
#!/bin/bash
# PHASE 2: Independent Functional Verification

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║   PHASE 2: INDEPENDENT FUNCTIONAL VERIFICATION                        ║"
echo "║   Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"

FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: DATABASE GROUND TRUTH
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 1: DATABASE GROUND TRUTH ==="
echo "Running: SELECT * FROM deals"

docker exec zakops-postgres psql -U zakops -d zakops -c "SELECT id, deal_id, name, stage, status, broker FROM deals;" 2>&1

DB_COUNT=$(docker exec zakops-postgres psql -U zakops -d zakops -t -c "SELECT COUNT(*) FROM deals;" 2>/dev/null | tr -d ' ')
echo "Database deal count: $DB_COUNT"

if [ "$DB_COUNT" == "3" ]; then
    echo "✅ Database has 3 deals (matches Builder claim)"
else
    echo "🚨 Database has $DB_COUNT deals (Builder claimed 3)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: BACKEND API (PORT 8091)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 2: BACKEND API (8091) ==="

BACKEND_RESPONSE=$(curl -s http://localhost:8091/api/deals 2>/dev/null)
BACKEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8091/api/deals 2>/dev/null)

echo "HTTP Status: $BACKEND_CODE"
echo "Response: $BACKEND_RESPONSE" | head -c 500

BACKEND_COUNT=$(echo "$BACKEND_RESPONSE" | jq 'if type == "array" then length else 0 end' 2>/dev/null || echo "PARSE_ERROR")
echo "Backend deal count: $BACKEND_COUNT"

# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: DASHBOARD API (PORT 3003)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 3: DASHBOARD API (3003) ==="

DASHBOARD_RESPONSE=$(curl -s http://localhost:3003/api/deals 2>/dev/null)
DASHBOARD_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3003/api/deals 2>/dev/null)

echo "HTTP Status: $DASHBOARD_CODE"
echo "Response: $DASHBOARD_RESPONSE" | head -c 500

DASHBOARD_COUNT=$(echo "$DASHBOARD_RESPONSE" | jq 'if type == "array" then length else 0 end' 2>/dev/null || echo "PARSE_ERROR")
echo "Dashboard API deal count: $DASHBOARD_COUNT"

# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: DATA CONSISTENCY CHECK
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 4: DATA CONSISTENCY ==="
echo "DB Count: $DB_COUNT"
echo "Backend Count: $BACKEND_COUNT"
echo "Dashboard Count: $DASHBOARD_COUNT"

if [ "$DB_COUNT" == "$BACKEND_COUNT" ] && [ "$BACKEND_COUNT" == "$DASHBOARD_COUNT" ]; then
    echo "✅ All counts match"
else
    echo "❌ FAIL: Count mismatch detected!"
    FAIL=1
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: FORBIDDEN PORT CHECK (CRITICAL!)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 5: FORBIDDEN PORT 8090 CHECK (CRITICAL!) ==="

if curl -s http://localhost:8090/health --max-time 3 2>/dev/null; then
    echo "🚨🚨🚨 CRITICAL: PORT 8090 IS ALIVE! 🚨🚨🚨"
    echo "This is a FORBIDDEN port (legacy backend)."
    echo "Builder may have 'fixed' chat by starting the WRONG service!"
    
    # What process is listening?
    echo ""
    echo "Investigating what's on port 8090:"
    lsof -i :8090 2>/dev/null || ss -tlnp | grep 8090
    
    # Check if it's a systemd service
    echo ""
    echo "Checking systemd for claude-code-api:"
    systemctl status claude-code-api.service 2>&1 | head -20
    
    FAIL=1
else
    echo "✅ Port 8090 is correctly DEAD"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: CORRECT AGENT API PORT (8095)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 6: CORRECT AGENT API PORT (8095) ==="

AGENT_HEALTH=$(curl -s http://localhost:8095/health --max-time 5 2>/dev/null)
AGENT_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8095/health --max-time 5 2>/dev/null)

echo "HTTP Status: $AGENT_CODE"
echo "Response: $AGENT_HEALTH"

if [ "$AGENT_CODE" == "200" ]; then
    echo "✅ Agent API on port 8095 is healthy"
else
    echo "❌ Agent API on port 8095 is NOT healthy"
    FAIL=1
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: CHAT ENDPOINT TEST
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 7: CHAT ENDPOINT ==="

CHAT_RESPONSE=$(curl -s -X POST http://localhost:3003/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"hello test","conversation_id":"qa-audit-'$(date +%s)'"}' \
    --max-time 30 2>&1)

echo "Chat response: $CHAT_RESPONSE" | head -c 500

if echo "$CHAT_RESPONSE" | grep -qi "unavailable\|No response\|error"; then
    echo "❌ FAIL: Chat response contains error indicators"
    FAIL=1
else
    echo "✅ Chat response appears OK"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: 5-RUN STABILITY (more than Builder's requirement)
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== TEST 8: 5-RUN STABILITY ==="

STABILITY_PASS=0
for i in 1 2 3 4 5; do
    RESPONSE=$(curl -s http://localhost:3003/api/deals 2>/dev/null)
    COUNT=$(echo "$RESPONSE" | jq 'if type == "array" then length else 0 end' 2>/dev/null || echo "0")
    
    if [ "$COUNT" == "$DB_COUNT" ]; then
        echo "  Run $i/5: PASS (count=$COUNT)"
        ((STABILITY_PASS++))
    else
        echo "  Run $i/5: FAIL (count=$COUNT, expected=$DB_COUNT)"
    fi
    sleep 1
done

if [ $STABILITY_PASS -eq 5 ]; then
    echo "✅ 5-run stability PASSED"
else
    echo "❌ 5-run stability FAILED ($STABILITY_PASS/5)"
    FAIL=1
fi

# ─────────────────────────────────────────────────────────────────────────────
# FINAL
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
if [ $FAIL -eq 0 ]; then
    echo "✅ PHASE 2: ALL TESTS PASSED"
else
    echo "❌ PHASE 2: SOME TESTS FAILED"
fi
```

### PHASE 3: EVIDENCE BLOCK VALIDATION

**Verify Builder's claimed evidence is real:**

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PHASE 3: EVIDENCE VALIDATION CHECKLIST                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   FOR ARTIFACT: 001_db_deals_query.txt                                       ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║   [ ] File exists and is not empty                                          ║
║   [ ] Run the same query yourself: SELECT * FROM deals                      ║
║   [ ] Compare YOUR output to artifact content                               ║
║   [ ] Output should show 3 deals with specific IDs                          ║
║   [ ] Check broker field format (string vs object - this was the bug!)      ║
║                                                                               ║
║   FOR ARTIFACT: 002_backend_api_deals.txt                                    ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║   [ ] File exists and is not empty                                          ║
║   [ ] Run: curl http://localhost:8091/api/deals                             ║
║   [ ] Compare YOUR output to artifact content                               ║
║   [ ] Check broker field format in response                                 ║
║                                                                               ║
║   FOR ARTIFACT: 003_dashboard_api_deals.txt                                  ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║   [ ] File exists and is not empty                                          ║
║   [ ] Run: curl http://localhost:3003/api/deals                             ║
║   [ ] Compare YOUR output to artifact content                               ║
║   [ ] Verify response has 3 deals (not 0!)                                  ║
║                                                                               ║
║   FOR ARTIFACT: 005_code_fix_diff.patch                                      ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║   [ ] File exists and is valid patch format                                 ║
║   [ ] Patch shows changes to apps/dashboard/src/lib/api.ts                  ║
║   [ ] Patch includes coerceBrokerToString() function                        ║
║   [ ] Run: git diff apps/dashboard/src/lib/api.ts                           ║
║   [ ] Compare git diff to provided patch                                    ║
║   [ ] Verify the fix is actually applied (not just in patch file)           ║
║                                                                               ║
║   MISSING EVIDENCE (Builder did not provide):                                ║
║   ─────────────────────────────────────────────────────────────────────────  ║
║   [ ] ❌ No dual-channel proof (API + Browser)                              ║
║   [ ] ❌ No browser screenshot showing deals in UI                          ║
║   [ ] ❌ No HAR capture of network requests                                 ║
║   [ ] ❌ No console capture showing no errors                               ║
║   [ ] ❌ No red-to-green demonstration                                      ║
║   [ ] ❌ No negative test (reverting fix causes failure)                    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### PHASE 4: SCOPE VIOLATION CHECK

**Critical: Check if Builder violated architectural constraints:**

```bash
#!/bin/bash
# PHASE 4: Scope Violation Check

echo "=== PHASE 4: SCOPE VIOLATION CHECK ==="

# APPROVED SCOPE (from mission)
APPROVED_SCOPE=(
    "apps/dashboard/src/app/api/"
    "apps/dashboard/src/app/"
    "apps/dashboard/src/components/"
    "apps/dashboard/src/lib/"
    "apps/dashboard/src/hooks/"
    "services/backend/"
    "services/agent-api/"
)

# Check what files actually changed
echo "=== FILES CHANGED (git diff) ==="
cd /home/zaks/zakops-agent-api
git diff --name-only HEAD~5 2>/dev/null || echo "Cannot determine via git"

echo ""
echo "=== CHECKING FOR OUT-OF-SCOPE CHANGES ==="

# Check systemd service files (should NOT be modified)
echo "Checking systemd services:"
ls -la /etc/systemd/system/*claude* 2>/dev/null || echo "No claude services in systemd"
ls -la /etc/systemd/system/*zakops* 2>/dev/null || echo "No zakops services in systemd"

# Check if any services were enabled/started
echo ""
echo "Checking enabled services:"
systemctl list-unit-files | grep -E "claude|zakops" 2>/dev/null

# CRITICAL: Was port 8090 service started?
echo ""
echo "=== CRITICAL: PORT 8090 SERVICE CHECK ==="
systemctl status claude-code-api.service 2>&1 | head -10

if systemctl is-active claude-code-api.service 2>/dev/null | grep -q "active"; then
    echo "🚨🚨🚨 SCOPE VIOLATION: claude-code-api.service IS ACTIVE 🚨🚨🚨"
    echo "This is the LEGACY service on FORBIDDEN port 8090!"
    echo "Builder violated architectural constraints!"
fi
```

### PHASE 5: FORENSIC LEDGER VERIFICATION

```bash
#!/bin/bash
# PHASE 5: Forensic Ledger Check

LEDGER="/home/zaks/completion_packet/ledger.jsonl"

echo "=== PHASE 5: FORENSIC LEDGER VERIFICATION ==="

if [ ! -f "$LEDGER" ]; then
    echo "❌ CRITICAL: ledger.jsonl DOES NOT EXIST"
    echo "Builder did not maintain required command log!"
    echo "This is a MAJOR PROTOCOL VIOLATION"
    exit 1
fi

echo "Ledger exists. Checking format..."

# Validate JSON
INVALID=0
LINE=0
while IFS= read -r entry; do
    ((LINE++))
    if ! echo "$entry" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        echo "❌ Invalid JSON on line $LINE"
        ((INVALID++))
    fi
done < "$LEDGER"

if [ $INVALID -gt 0 ]; then
    echo "❌ $INVALID invalid JSON entries"
else
    echo "✅ All entries are valid JSON"
fi

# Check required fields
echo ""
echo "Checking required fields (ts_start, ts_end, phase, cmd, cwd, why, exit_code, output_file, output_sha256)..."
REQUIRED_FIELDS=("ts_start" "ts_end" "phase" "cmd" "cwd" "why" "exit_code" "output_file" "output_sha256")

while IFS= read -r entry; do
    for field in "${REQUIRED_FIELDS[@]}"; do
        if ! echo "$entry" | grep -q "\"$field\""; then
            echo "❌ Missing field '$field' in: $(echo "$entry" | head -c 60)..."
        fi
    done
done < "$LEDGER"
```

### PHASE 6: ACCEPTANCE CRITERIA VERIFICATION

(See prompt above.)

### PHASE 7: PERSISTENCE & STABILITY VERIFICATION

(See prompt above.)

### PHASE 8: ATTACK SURFACE SCAN

(See prompt above.)

---

## SECTION 6: REQUIRED OUTPUT FORMAT

(Return exactly these sections, in this order. No extra sections. No fluff.)

1. **AUDIT VERDICT** (PASS / FAIL / UNPROVEN)
2. **TOP 10 FINDINGS** (ranked by severity)
3. **EVIDENCE CONSISTENCY CHECKS**
4. **ARTIFACT AUTHENTICITY CHECKS**
5. **INSTRUCTION COMPLIANCE MATRIX**
6. **FIX VALIDATION MATRIX** (per acceptance criterion)
7. **SCOPE & INTEGRITY CHECKS**
8. **REPRODUCIBILITY CHECK**
9. **REQUIRED REMEDIATIONS** (if not PASS)

---

## SECTION 7: SCORING / VERDICT RULES

### PASS
- Every acceptance criterion is proven
- Every mandatory audit check is satisfied
- No fabrication detected
- All artifacts authentic and complete
- Fresh-clone reproducibility confirmed
- **Port 8090 is DEAD (not revived as a "fix")**

### FAIL
Any of:
- Fabricated evidence suspected and cannot be disproven
- Missing chain-of-custody
- Missing service identity proof
- Missing negative proof for signature errors
- Scope drift without rollback
- Any Phase FAIL
- verification_script.sh does not fail when fix reverted
- Resource variance exceeds 15%
- Fresh-clone repro fails
- **Port 8090 is alive (architectural violation)**
- **Chat "fixed" by starting wrong service**

### UNPROVEN
- Agent may have fixed it but evidence is incomplete
- List exact missing artifacts
- Still requires remediation before PASS

---

## SECTION 8: DELIVERABLES (REQUIRED)

### A) Instruction Compliance Matrix
| Requirement | Provided? | Evidence Pointer | Notes |
|-------------|-----------|------------------|-------|
| ledger.jsonl | ? | | Builder didn't mention |
| evidence_manifest.sha256 | ? | | Builder didn't mention |
| verification_script.sh | ? | | Builder didn't mention |
| diff.patch | Y | artifacts/005_code_fix_diff.patch | |
| HAR captures | ? | | Builder didn't mention |
| Browser screenshots | ? | | Builder didn't mention |
| Console captures | ? | | Builder didn't mention |
| Red-to-green proof | ? | | Builder didn't mention |
| 3-run stability | ? | | Builder didn't mention |
| Restart persistence | ? | | Builder didn't mention |

### B) Fix Validation Matrix
| Acceptance Criterion | Status | Evidence Pointer | Notes |
|---------------------|--------|------------------|-------|
| AC-1: Deal Display Fixed | ? | | Verify in browser |
| AC-2: Deals Page Works | ? | | Verify in browser |
| AC-3: Chat Responds | ? | | ⚠️ Check which port! |
| AC-4: No Warning Banner | ? | | Verify in browser |
| AC-5: E2E Data Path | ? | | Trace full chain |

### C) Tamper / Fabrication Findings
**KNOWN CONCERNS:**
1. Builder claimed port 8090 fix - this is the FORBIDDEN legacy port
2. Builder's completion packet is missing many required artifacts
3. No browser-based evidence provided (only curl)
4. No red-to-green demonstration

### D) Remediation List (if not PASS)
**LIKELY REQUIRED:**
1. Stop claude-code-api.service (port 8090 must be dead)
2. Fix chat to use port 8095 (correct agent API)
3. Provide browser screenshots/HAR for UI claims
4. Provide ledger.jsonl
5. Provide verification_script.sh
6. Demonstrate red-to-green with controlled failure
7. Run 3-run stability test

---

# BEGIN AUDIT NOW
