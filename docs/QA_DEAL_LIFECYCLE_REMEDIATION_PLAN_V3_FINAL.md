❯ do this  QA VERIFICATION + REMEDIATION:                                             
  DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL                                            
  ## Adversarial Audit | Zero Trust | Verify-Fix-Reverify | Independent               
  Verification                                                                        
                                                                                      
  **Codename:** `QA-VERIFICATION-006`                                                 
  **Version:** V1 (Verify-Fix-Reverify Edition)                                       
  **Target:** DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL (69 tasks, 22 issues, 7        
  phases)                                                                             
  **Executor:** Claude Code (Opus 4.5)                                                
  **Mode:** AUDIT + REMEDIATION — Verify first, fix failures, re-verify fixes         
  **Stance:** ZERO TRUST — Assume every Builder claim is fabricated until             
  independently proven                                                                
  **Authority:** VETO power — any P0 failure that cannot be remediated = mission      
  NOT COMPLETE                                                                        
  **Source Plan:** DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL (PASS 3 FINAL             
  synthesis)                                                                          
                                                                                      
  ```                                                                                 
  ╔══════════════════════════════════════════════════════════════════════════════     
  ═╗                                                                                  
  ║                                                                                   
   ║                                                                                  
  ║   HARD RULE: NO ENDING SESSION WHILE TESTS ARE RED                                
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ║   This mission has TWO modes:                                                     
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ║   MODE 1 — AUDIT: Verify each task/gate independently.                      ║     
  ║   MODE 2 — REMEDIATE: If verification FAILS, fix the issue, then re-verify. ║     
  ║                                                                                   
   ║                                                                                  
  ║   The session CANNOT end until:                                                   
  ║                                                                                   
  ║   • Every task is PASS or REMEDIATED+PASS                                         
  ║                                                                                   
  ║   • OR explicitly marked DEFERRED with proven justification                       
  ║                                                                                   
  ║   • OR marked BLOCKED with documented blocker                                     
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ║   ALL curl commands MUST have --max-time + --connect-timeout                      
  ║                                                                                   
  ║   ALL coverage matrix cells MUST be filled — NO BLANKS                            
  ║                                                                                   
  ║   ALL remediation MUST produce before/after evidence                              
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ╚══════════════════════════════════════════════════════════════════════════════     
  ═╝                                                                                  
  ```                                                                                 
                                                                                      
  **Prior Art:**                                                                      
  - DEAL_LIFECYCLE_HONEST_ASSESSMENT_V2.md (Original 22 issues)                       
  - DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.md (Synthesized plan — UNVERIFIED        
  execution)                                                                          
  - QA_VERIFICATION_005_V2.md (Template for audit methodology)                        
                                                                                      
  **Mission Lineage:**                                                                
  - This is the verification + remediation pass for the V3 FINAL plan                 
  - Builder claims to have executed all 69 tasks across 7 phases                      
  - This mission independently verifies AND fixes what was missed                     
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 0: AUDITOR + REMEDIATOR ROLE DEFINITION                                  
                                                                                      
  ```                                                                                 
  ╔══════════════════════════════════════════════════════════════════════════════     
  ═╗                                                                                  
  ║                                                                                   
   ║                                                                                  
  ║   YOU ARE AN ADVERSARIAL QA AUDITOR WITH REMEDIATION AUTHORITY.                   
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ║   PHASE 1 OF EACH CHECK: VERIFY                                             ║     
  ║   • Run YOUR OWN commands to prove/disprove the Builder's claims                  
  ║                                                                                   
  ║   • Every claim needs YOUR independent verification                               
  ║                                                                                   
  ║   • Builder's report is MARKETING until YOU prove each claim                      
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ║   PHASE 2 OF EACH CHECK: REMEDIATE (if FAIL)                                ║     
  ║   • If verification fails → implement the fix per the V3 FINAL spec         ║     
  ║   • Capture BEFORE evidence (the broken state)                                    
  ║                                                                                   
  ║   • Apply the fix                                                                 
  ║                                                                                   
  ║   • Capture AFTER evidence (the fixed state)                                      
  ║                                                                                   
  ║   • Re-run verification to confirm fix                                            
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ║   PHASE 3 OF EACH CHECK: DOCUMENT                                           ║     
  ║   • Record verdict: PASS (already done) | REMEDIATED (fixed now) |          ║     
  ║   •   DEFERRED (justified) | BLOCKED (cannot fix)                           ║     
  ║   • Every DEFERRED must have proven justification                                 
  ║                                                                                   
  ║   • Every BLOCKED must have documented blocker                                    
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ║   YOUR OUTPUT: QA_VERIFICATION_006_REPORT.md with full evidence trail             
  ║                                                                                   
  ║                                                                                   
   ║                                                                                  
  ╚══════════════════════════════════════════════════════════════════════════════     
  ═╝                                                                                  
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 0.1: REMEDIATION PROTOCOL                                                
                                                                                      
  **CRITICAL: This is what distinguishes this mission from a pure audit.**            
                                                                                      
  ### The Verify-Fix-Reverify Loop                                                    
                                                                                      
  ```                                                                                 
  For EACH task (T0.1 through T6.10):                                                 
                                                                                      
  ┌─────────────────────┐                                                             
  │  1. VERIFY           │ ← Run YOUR commands to check if task was completed         
  │     │                │                                                            
  │     ├── PASS? ──────►│── Record PASS + evidence → next task                       
  │     │                │                                                            
  │     └── FAIL? ──────►│                                                            
  │                      │                                                            
  │  2. CAPTURE BEFORE   │ ← Screenshot/log the broken state                          
  │     │                │                                                            
  │  3. REMEDIATE        │ ← Implement the fix per V3 FINAL spec                      
  │     │                │                                                            
  │  4. CAPTURE AFTER    │ ← Screenshot/log the fixed state                           
  │     │                │                                                            
  │  5. RE-VERIFY        │ ← Re-run the SAME verification commands                    
  │     │                │                                                            
  │     ├── PASS? ──────►│── Record REMEDIATED + before/after evidence → next         
  task                                                                                
  │     │                │                                                            
  │     └── FAIL? ──────►│── Record BLOCKED + document WHY fix didn't work            
  │                      │                                                            
  └─────────────────────┘                                                             
  ```                                                                                 
                                                                                      
  ### Remediation Rules                                                               
                                                                                      
  | Rule | Description |                                                              
  |------|-------------|                                                              
  | **Follow the spec** | All remediations MUST conform to the V3 FINAL decision      
  set (D-FINAL-01 through D-FINAL-07) |                                               
  | **Minimal changes** | Fix ONLY what's broken — don't refactor, redesign, or       
  over-engineer |                                                                     
  | **Evidence trail** | Every remediation needs before + after evidence in the       
  evidence directory |                                                                
  | **No silent fixes** | Every fix must be documented in the remediation log |       
  | **Rollback-safe** | Prefer additive changes (new files, new columns) over         
  destructive ones |                                                                  
  | **Test after fix** | Re-run the exact same verification that failed — no          
  substituting easier tests |                                                         
  | **Gate respect** | Do NOT proceed past a gate until all MUST-PASS items in        
  that gate are PASS or REMEDIATED |                                                  
                                                                                      
  ### Remediation Scope Limits                                                        
                                                                                      
  **IN SCOPE (you CAN fix):**                                                         
  - Missing files that should have been created                                       
  - Missing DB columns, tables, triggers, migrations                                  
  - Missing API endpoints or incorrect endpoint paths                                 
  - Missing middleware, headers, validation logic                                     
  - Configuration changes (.env, docker-compose, etc.)                                
  - Code changes in existing files (endpoint fixes, schema fixes)                     
  - Missing documentation files                                                       
                                                                                      
  **OUT OF SCOPE (mark as DEFERRED with justification):**                             
  - Major architectural rewrites (e.g., full email ingestion refactor)                
  - External service integrations (ClamAV, OIDC providers)                            
  - CI/CD pipeline changes (GitHub Actions)                                           
  - Production data migrations                                                        
  - User authentication system (Phase 5 — requires product decisions)                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 0.2: BANNED PHRASES (FOR THE QA AUDITOR)                                 
                                                                                      
  | Banned | Replace With |                                                           
  |--------|-------------|                                                            
  | "Builder claims it works" | [run the test yourself, paste YOUR output] |          
  | "Report says PASS" | [independently verify with YOUR curl/psql/grep] |            
  | "Appears to be fixed" | [show expected output AND actual output side by side]     
   |                                                                                  
  | "Consistent with report" | [show the raw evidence that proves or disproves] |     
  | "No issues observed" | [list exactly what was tested with evidence] |             
  | "Verified" (without evidence) | [paste the command + output that proves it] |     
  | "Likely ok" | [RUN THE TEST, show output] |                                       
  | "Should work" | [PROVE IT WORKS with evidence] |                                  
  | "Fixed during remediation" (without re-verify) | [show the RE-VERIFY output       
  after fix] |                                                                        
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 0.3: ANTI-HANG ENFORCEMENT (RT-TIMEOUT)                                  
                                                                                      
  ```bash                                                                             
  # MANDATORY: All curl commands MUST use these flags                                 
  CURL_TIMEOUT="--max-time 30 --connect-timeout 10"                                   
                                                                                      
  # Example: CORRECT                                                                  
  curl $CURL_TIMEOUT -sf http://localhost:8091/health                                 
                                                                                      
  # Example: WRONG (could hang forever)                                               
  # curl -sf http://localhost:8091/health                                             
                                                                                      
  # SSE/Streaming tests MUST use --max-time                                           
  # Pytest tests MUST use pytest --timeout=60                                         
  # ANY test that runs >60s without output → print diagnostics and exit non-zero      
  ```                                                                                 
                                                                                      
  **HARD RULE: If ANY command hangs during QA, add timeout and re-run. Hanging =      
  COMPROMISED.**                                                                      
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 0.4: CONTEXT MANAGEMENT                                                  
                                                                                      
  ```                                                                                 
  This mission covers 69 tasks across 7 phases. Context WILL fill up.                 
                                                                                      
  MANDATORY /compact points:                                                          
  • After QA Phase 1 (Phase 0 verification) completes                                 
  • After QA Phase 3 (Phase 2 verification) completes                                 
  • After QA Phase 5 (Phase 4 verification) completes                                 
  • After QA Phase 7 (Phase 6 verification) completes                                 
  • After remediation of any phase with >3 FAIL items                                 
                                                                                      
  Before each /compact:                                                               
  1. Save current progress to PROGRESS_CHECKPOINT.md in evidence dir                  
  2. Record which tasks are PASS/REMEDIATED/FAIL/DEFERRED                             
  3. Record which gates have been cleared                                             
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 1: GROUND TRUTH                                                          
                                                                                      
  ### 1.1 Repository Locations                                                        
                                                                                      
  ```bash                                                                             
  AGENT_REPO="/home/zaks/zakops-agent-api"                                            
  AGENT_API_DIR="/home/zaks/zakops-agent-api/apps/agent-api"                          
  DASHBOARD_DIR="/home/zaks/zakops-agent-api/apps/dashboard"                          
  BACKEND_REPO="/home/zaks/zakops-backend"                                            
  SCRIPTS_DIR="/home/zaks/scripts"                                                    
  DATAROOM_DIR="/home/zaks/DataRoom"                                                  
  BOOKKEEPING="/home/zaks/bookkeeping"                                                
  ```                                                                                 
                                                                                      
  ### 1.2 Database Access                                                             
                                                                                      
  ```bash                                                                             
  AGENT_DB_CMD="cd /home/zaks/zakops-agent-api/apps/agent-api && docker compose       
  exec -T db psql -U agent -d zakops_agent"                                           
  BACKEND_DB_CMD="cd /home/zaks/zakops-backend && docker compose exec -T postgres     
   psql -U zakops -d zakops"                                                          
  ```                                                                                 
                                                                                      
  ### 1.3 Service URLs                                                                
                                                                                      
  ```bash                                                                             
  AGENT_API_URL="http://localhost:8095"                                               
  BACKEND_URL="http://localhost:8091"                                                 
  DASHBOARD_URL="http://localhost:3003"                                               
  RAG_URL="http://localhost:8052"                                                     
  ```                                                                                 
                                                                                      
  ### 1.4 Auth Tokens                                                                 
                                                                                      
  ```bash                                                                             
  SERVICE_TOKEN=$(grep DASHBOARD_SERVICE_TOKEN                                        
  /home/zaks/zakops-agent-api/apps/agent-api/.env | cut -d= -f2)                      
  ZAKOPS_API_KEY=$(grep -E "^(ZAKOPS_)?API_KEY" /home/zaks/zakops-backend/.env        
  2>/dev/null | head -1 | cut -d= -f2)                                                
  ```                                                                                 
                                                                                      
  ### 1.5 Output Directory                                                            
                                                                                      
  ```bash                                                                             
  QA_DIR="/home/zaks/bookkeeping/qa/QA-VERIFICATION-006"                              
  EVIDENCE_DIR="$QA_DIR/evidence"                                                     
  REMEDIATION_LOG="$QA_DIR/REMEDIATION_LOG.md"                                        
  mkdir -p "$QA_DIR"/{evidence/{phase0,phase1,phase2,phase3,phase4,phase5,phase6,     
  remediation},matrices}                                                              
                                                                                      
  # Initialize remediation log                                                        
  cat > "$REMEDIATION_LOG" << 'EOF'                                                   
  # REMEDIATION LOG — QA-VERIFICATION-006                                             
                                                                                      
  | # | Task ID | Issue ID | Phase | Verify Result | Action Taken | Re-Verify         
  Result | Evidence |                                                                 
  |---|---------|----------|-------|---------------|--------------|--------------     
  ----|----------|                                                                    
  EOF                                                                                 
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 2: QA PHASE 0 — SERVICE HEALTH & INFRASTRUCTURE BASELINE                 
                                                                                      
  **Purpose:** Before testing anything, verify services are running and establish     
   baseline state. This is the foundation — if services are down, nothing else        
  matters.                                                                            
                                                                                      
  ### QA-0.1: Service Health (WITH TIMEOUTS)                                          
                                                                                      
  ```bash                                                                             
  echo "=== QA-0.1: Service Health ===" | tee                                         
  "$EVIDENCE_DIR/phase0/qa0_1_health.txt"                                             
                                                                                      
  echo "--- Backend API ---" >> "$EVIDENCE_DIR/phase0/qa0_1_health.txt"               
  curl $CURL_TIMEOUT -sf http://localhost:8091/health 2>&1 \                          
    | python3 -m json.tool | tee -a "$EVIDENCE_DIR/phase0/qa0_1_health.txt"           
                                                                                      
  echo "--- Agent API ---" >> "$EVIDENCE_DIR/phase0/qa0_1_health.txt"                 
  curl $CURL_TIMEOUT -sf http://localhost:8095/health 2>&1 \                          
    | python3 -m json.tool | tee -a "$EVIDENCE_DIR/phase0/qa0_1_health.txt"           
                                                                                      
  echo "--- Dashboard ---" >> "$EVIDENCE_DIR/phase0/qa0_1_health.txt"                 
  curl $CURL_TIMEOUT -sf http://localhost:3003/ -o /dev/null -w "Dashboard:           
  %{http_code}\n" 2>&1 \                                                              
    | tee -a "$EVIDENCE_DIR/phase0/qa0_1_health.txt"                                  
                                                                                      
  echo "--- RAG Service ---" >> "$EVIDENCE_DIR/phase0/qa0_1_health.txt"               
  curl $CURL_TIMEOUT -sf http://localhost:8052/health 2>&1 \                          
    | tee -a "$EVIDENCE_DIR/phase0/qa0_1_health.txt"                                  
  # Note: RAG may not be running — document status, do not block                      
                                                                                      
  echo "--- Docker containers ---" >> "$EVIDENCE_DIR/phase0/qa0_1_health.txt"         
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1 \               
    | tee -a "$EVIDENCE_DIR/phase0/qa0_1_health.txt"                                  
  ```                                                                                 
                                                                                      
  **PASS criteria:** Backend 200, Agent API 200, Dashboard 200/307. RAG: document     
   status.                                                                            
  **If FAIL:** Start the failing service(s), re-check. If service won't start,        
  document blocker.                                                                   
                                                                                      
  ### QA-0.2: Database Connectivity                                                   
                                                                                      
  ```bash                                                                             
  echo "=== QA-0.2: Database Connectivity ===" | tee                                  
  "$EVIDENCE_DIR/phase0/qa0_2_db.txt"                                                 
                                                                                      
  echo "--- Agent DB ---" >> "$EVIDENCE_DIR/phase0/qa0_2_db.txt"                      
  $AGENT_DB_CMD -c "SELECT current_database(), current_user, NOW();" 2>&1 \           
    | tee -a "$EVIDENCE_DIR/phase0/qa0_2_db.txt"                                      
                                                                                      
  echo "--- Backend DB ---" >> "$EVIDENCE_DIR/phase0/qa0_2_db.txt"                    
  $BACKEND_DB_CMD -c "SELECT current_database(), current_user, NOW();" 2>&1 \         
    | tee -a "$EVIDENCE_DIR/phase0/qa0_2_db.txt"                                      
                                                                                      
  echo "--- Agent DB tables ---" >> "$EVIDENCE_DIR/phase0/qa0_2_db.txt"               
  $AGENT_DB_CMD -c "\dt" 2>&1 | tee -a "$EVIDENCE_DIR/phase0/qa0_2_db.txt"            
                                                                                      
  echo "--- Backend DB tables ---" >> "$EVIDENCE_DIR/phase0/qa0_2_db.txt"             
  $BACKEND_DB_CMD -c "\dt" 2>&1 | tee -a "$EVIDENCE_DIR/phase0/qa0_2_db.txt"          
  ```                                                                                 
                                                                                      
  **PASS criteria:** Both DBs accessible, return expected database names.             
                                                                                      
  ### QA-0.3: RT-DB-SOT — Split-Brain Proof Gate (ABSOLUTE)                           
                                                                                      
  ```bash                                                                             
  echo "=== QA-0.3: RT-DB-SOT ===" | tee "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"      
                                                                                      
  # STEP 1: Container inventory — list ALL postgres containers                        
  echo "--- STEP 1: Postgres Container Inventory ---" >>                              
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
  docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"       
  2>&1 | grep -i postgres \                                                           
    | tee -a "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                  
  POSTGRES_COUNT=$(docker ps -a --format "{{.Names}}" | grep -ci postgres)            
  echo "Total Postgres containers: $POSTGRES_COUNT" >>                                
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
                                                                                      
  # STEP 2: Show DATABASE_URL for each service container                              
  echo "--- STEP 2: Service DB configurations ---" >>                                 
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
  AGENT_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E                         
  "agent-api|agent_api" | grep -v db | head -1)                                       
  echo "Agent container: $AGENT_CONTAINER" >>                                         
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
  docker inspect "$AGENT_CONTAINER" 2>/dev/null | grep -E                             
  "DATABASE_URL|DB_HOST|POSTGRES" \                                                   
    >> "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt" 2>&1                                   
                                                                                      
  BACKEND_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "backend" | grep      
  -v postgres | head -1)                                                              
  echo "Backend container: $BACKEND_CONTAINER" >>                                     
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
  docker inspect "$BACKEND_CONTAINER" 2>/dev/null | grep -E                           
  "DATABASE_URL|DB_HOST|POSTGRES" \                                                   
    >> "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt" 2>&1                                   
                                                                                      
  # STEP 3: Live DB identity                                                          
  echo "--- STEP 3: Live DB Identity ---" >>                                          
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
  $AGENT_DB_CMD -c "SELECT current_database(), current_user, inet_server_addr(),      
  inet_server_port();" 2>&1 \                                                         
    | tee -a "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                  
  $BACKEND_DB_CMD -c "SELECT current_database(), current_user,                        
  inet_server_addr(), inet_server_port();" 2>&1 \                                     
    | tee -a "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                  
                                                                                      
  # STEP 4: If >2 postgres containers, investigate orphans                            
  if [ "$POSTGRES_COUNT" -gt 2 ]; then                                                
    echo "--- STEP 4: ORPHAN INVESTIGATION ---" >>                                    
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
    for container in $(docker ps -a --format "{{.Names}}" | grep -i postgres); do     
      echo "--- Container: $container ---" >>                                         
  "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                             
      docker inspect "$container" --format='Compose Project: {{index                  
  .Config.Labels "com.docker.compose.project"}}' 2>&1 \                               
        >> "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                    
      docker exec "$container" psql -U agent -d zakops_agent -c "SELECT COUNT(*)      
  FROM deal_events;" 2>/dev/null \                                                    
        >> "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt" || echo "Cannot connect or         
  table doesn't exist" \                                                              
        >> "$EVIDENCE_DIR/phase0/qa0_3_db_sot.txt"                                    
    done                                                                              
  fi                                                                                  
  ```                                                                                 
                                                                                      
  **HARD GATE RULES:**                                                                
  - Agent DB must be `zakops_agent`                                                   
  - Backend DB must be `zakops`                                                       
  - If >2 Postgres containers AND services connect to wrong one → **FAIL              
  (SPLIT-BRAIN)**                                                                     
  - If orphan container exists but no service connects → Document, PASS               
                                                                                      
  **GATE QA-0: Services healtDBs accessible. RT-DB-SOT passed. Baseline           
  established.**                                                                      
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 3: QA PHASE 1 — PHASE 0 VERIFICATION (Stop the Bleeding)                 
                                                                                    
  **Covers:** ZK-ISSUE-0006, ZK-ISSUE-0007, ZK-ISSUE-0010, ZK-ISSUE-0011,             
  ZK-ISSUE-0012, ZK-ISSUE-0018                                                        
  **Tasks:** T0.1 through T0.12                                                       
                                                                                      
  ### QA-1.1: T0.1 — Dashboard Quarantine Endpoint Fix (ZK-ISSUE-0006)                
                                                                                    
  **V3 Spec:** Dashboard must call `/process` not `/resolve` for quarantine           
  approval.                                                                           
                                                                                      
  ```bash                                                                             
  echo "=== QA-1.1: T0.1 Quarantine Endpoint ===" | tee                               
  "$EVIDENCE_DIR/phase1/qa1_1_quarantine.txt"                                         
                                                                                      
  # TEST 1: Source code check — does api.ts use /process?                             
  echo "--- TEST 1: api.ts quarantine calls ---" >>                                   
  "$EVIDENCE_DIR/phase1/qa1_1_quarantine.txt"                                         
  rg -n "resolve|process" "$DASHBOARD_DIR/src/lib/api.ts" 2>&1 \                    
    | grep -i "quarantine" | tee -a "$EVIDENCE_DIR/phase1/qa1_1_quarantine.txt"       
                                                                                      
  # TEST 2: Backend endpoint exists                                                   
  echo "--- TEST 2: Backend /process endpoint ---" >>                                 
  "$EVIDENCE_DIR/phase1/qa1_1_quarantine.txt"                                         
  # List quarantine-related endpoints                                                 
  rg -n "quarantine.*process\|process.*quarantine\|/process"                          
  "$BACKEND_REPO/src/api/orchestration/" --type py 2>&1 \                             
    | tee -a "$EVIDENCE_DIR/phase1/qa1_1_quarantine.txt"                              
                                                                                      
  # TEST 3: Live endpoint test (if quarantine items exist)                            
  echo "--- TEST 3: Live endpoint ---" >>                                             
  "$EVIDENCE_DIR/phase1/qa1_1_quarantine.txt"                                         
  # Check if quarantine table exists and has items                                    
  $BACKEND_DB_CMD -c "SELECT COUNT(*) FROM quarantine_items;" 2>&1 \                  
    | tee -a "$EVIDENCE_DIR/phase1/qa1_1_quarantine.txt"                              
  ```                                                                                 
                                                                                      
  **PASS:** api.ts uses `/process`, backend route exists.                             
  **IF FAIL → REMEDIATE:**                                                            
  ```                                                                                 
  1. In api.ts: replace all `/resolve` with `/process` for quarantine endpoints       
  2. If backend route missing: add POST /api/quarantine/{id}/process route            
  3. Re-verify with same tests                                                      
  ```                                                                                 
                                                                                      
  ### QA-1.2: T0.2 + T0.3 — Notes Endpoint (ZK-ISSUE-0012)                            
                                                                                      
  **V3 Spec:** Dashboard calls correct notes path. Backend has                        
  `/api/deals/{id}/notes`.                                                          
                                                                                      
  ```bash                                                                             
  echo "=== QA-1.2: T0.2+T0.3 Notes Endpoint ===" | tee                               
  "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"                                              
                                                                                      
  # TEST 1: Dashboard notes API path                                                  
  echo "--- TEST 1: Dashboard notes path ---" >>                                      
  "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"                                              
  rg -n "notes" "$DASHBOARD_DIR/src/lib/api.ts" 2>&1 \                                
    | tee -a "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"                                   
                                                                                      
  # TEST 2: Backend notes endpoint exists                                             
  echo "--- TEST 2: Backend notes endpoint ---" >>                                    
  "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"                                              
  rg -n "notes" "$BACKEND_REPO/src/api/orchestration/" --type py 2>&1 \               
    | tee -a "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"                                   
                                                                                      
  # TEST 3: Live test — POST a note                                                   
  echo "--- TEST 3: Live POST /notes ---" >>                                          
  "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"                                              
  # Get a deal ID first                                                               
  DEAL_ID=$($BACKEND_DB_CMD -t -c "SELECT deal_id FROM deals LIMIT 1;" 2>&1 | tr      
  -d ' \n')                                                                         
  echo "Test deal: $DEAL_ID" >> "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"                
                                                                                      
  if [ -n "$DEAL_ID" ]; then                                                          
    curl $CURL_TIMEOUT -s -X POST                                                     
  "http://localhost:8091/api/deals/$DEAL_ID/notes" \                                  
      -H "Content-Type: application/json" \                                           
      -H "X-API-Key: $ZAKOPS_API_KEY" \                                               
      -d '{"content":"QA-006 test note","author":"qa-auditor"}' 2>&1 \                
      | python3 -m json.tool | tee -a "$EVIDENCE_DIR/phase1/qa1_2_notes.txt"          
  fi                                                                                  
  ```                                                                                 
                                                                                      
  **PASS:** Dashboard uses correct path, backend returns 200/201 on POST.             
  **IF FAIL → REMEDIATE:**                                                            
  ```                                                                                 
  1. Fix Dashboard path in api.ts to match backend                                    
  2. If backend route missing: add POST /api/deals/{id}/notes to orchestration        
  API                                                                               
  3. Re-verify                                                                        
  ```                                                                                 
                                                                                      
  ### QA-1.3: T0.4 + T0.5 — Stage Taxonomy (ZK-ISSUE-0007)                            
                                                                                      
  **V3 Spec:** `deal_state_machine.` deleted. DB default stage is `inbound`. No     
   legacy stage names.                                                                
                                                                                      
  ```bash                                                                             
  echo "=== QA-1.3: T0.4+T0.5 Stage Taxonomy ===" | tee                               
  "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                             
                                                                                      
  # TEST 1: deal_state_machine.py deleted?                                            
  echo "--- TEST 1: deal_state_machine.py ---" >>                                     
  "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                             
  ls -la /home/zaks/scripts/deal_state_machine.py 2>&1 \                              
    | tee -a "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                  
  # PASS if "No such file"                                                            
                                                                                      
  # TEST 2: DB default stage                                                          
  echo "--- TEST 2: DB default stage ---" >>                                          
  "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                             
  $BACKEND_DB_CMD -c "SELECT column_default FROM information_schema.columns WHERE     
   table_name='deals' AND column_name='stage';" 2>&1 \                                
    | tee -a "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                  
  # Expected: 'inbound'                                                               
                                                                                      
  # TEST 3: No conflicting stage definitions in code                                  
  echo "--- TEST 3: No legacy stages ---" >>                                          
  "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                             
  rg -c "DealStage" "$BACKEND_REPO/src/" "$SCRIPTS_DIR/" --type py 2>&1 \             
    | grep -v "workflow.py" | tee -a "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"          
                                                                                      
  # TEST 4: No 'lead' stage in code (should be 'inbound')                             
  echo "--- TEST 4: No 'lead' stage references ---" >>                                
  "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                             
  rg -n '"lead"' "$BACKEND_REPO/src/" --type py 2>&1 \                                
    | grep -i "stage\|deal\|transition" | tee -a                                      
  "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                             
                                                                                      
  # TEST 5: Any existing deals with 'lead' stage?                                     
  echo "--- TEST 5: Deals with 'lead' stage ---" >>                                   
  "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                             
  $BACKEND_DB_CMD -c "SELECT COUNT(*) FROM deals WHERE stage = 'lead';" 2>&1 \        
    | tee -a "$EVIDENCE_DIR/phase1/qa1_3_stages.txt"                                  
  ```                                                                                 
                                                                                      
  **PASS:** File deleted, default is `inbound`, no legacy stages in code.             
  **IF FAIL → REMEDIATE:**                                                            
  ```                                                                                 
  1. DELETE /home/zaks/scripts/deal_state_machine.py if still exists                  
  2. ALTER TABLE deals ALTER COLUMN stage SET DEFAULT 'inbound' if default wrong      
  3. UPDATE deals SET stage = 'inbound' WHE stage = 'lead' if data exists           
  4. Re-verify                                                                        
  ```                                                                                 
                                                                                      
  ### QA-1.4: T0.6 + T0.7 + T0.8 — Correlation ID (ZK-ISSUE-0011)                     
                                                                                      
  **V3 Spec:** Dashboard generat X-Correlation-ID, backend reads and stores it      
  in deal_events.                                                                     
                                                                                      
  ```bash                                                                             
  echo "=== QA-1.4: T0.6-T0.8 Correlation ID ===" | tee                               
  "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                                        
                                                                                      
  # TEST 1: Dashboard middleware generates correlation_id                             
  echo "--- TEST 1: Dashboard middleware ---" >>                                      
  "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                                        
  rg -n "correlation\|Correlation\|X-Correlation" "$DASHBOARD_DIR/src/" --type ts     
   2>&1 \                                                                             
    | tee -a "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                             
                                                                                      
  # TEST 2: Backend reads X-Correlation-ID header                                     
  echo "--- TEST 2: Backend correlation_id ---" >>                                    
  "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                                        
  rg -n "correlation\|Correlation\|X-Correlation"                                     
  "$BACKEND_REPO/src/api/orchestration/" --type py 2>&1 \                             
    | tee -a "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                             
                                                                                      
  # TEST 3: deal_events table has correlation_id column                               
  echo "--- TEST 3: deal_events schema ---" >>                                        
  "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                                        
  $BACKEND_DB_CMD -c "\d deal_events" 2>&1 \                                          
    | tee -a "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                             
                                                                                      
  # TEST 4: Live test — send request with correlation_id, verify stored               
  echo "--- TEST 4: Live correlation test ---" >>                                     
  "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                                      
  TEST_CORR_ID="qa006-corr-$(date +%s)"                                               
  DEAL_ID=$($BACKEND_DB_CMD -t -c "SELECT deal_id FROM deals LIMIT 1;" 2>&1 | tr      
  -d ' \n')                                                                           
  if [ -n "$DEAL_ID" ]; then                                                          
    curl $CURL_TIMEOUT -s -X POST                                                     
  "http://localhost:8091/api/deals/$DEAL_ID/transition" \                             
      -H "Content-Type: application/json" \                                           
      -H "X-API-Key: $ZAKOPS_API_KEY" \                                               
      -H "X-Correlation-ID: $TEST_CORR_ID" \                                          
      -d '{"to_stage":"screening"}' 2>&1 \                                            
      | tee -a "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                           
    sleep 1                                                                           
    $BACKEND_DB_CMD -c "SELECT correlation_id FROM deal_events WHERE                  
  correlation_id = '$TEST_CORR_ID';" 2>&1 \                                           
      | tee -a "$EVIDENCE_DIR/phase1/qa1_4_correlation.txt"                           
  fi                                                                                  
  ```                                                                                 
                                                                                      
  **PASS:** Dashboard generates, backend reads and stores correlation_id in           
  deal_events.                                                                        
  **IF FAIL → REMEDIATE:**                                                            
  ```                                                                                 
  1. If deal_events lacks correlation_id column: ALTER TABLE deal_events ADD          
  COLUMN correlation_id TEXT                                                        
  2. If backend doesn't read header: add X-Correlation-ID header parsing to           
  middleware                                                                          
  3. If dashboard doesn't generate: add uuid generation in middleware.ts              
  4. Re-verify                                                                        
  ```                                                                                 
                                                                                      
  ### QA-1.5: T0.9 — RAG Health Documentation (ZK-ISSUE-0010)                         
                                                                                      
  ```bash                                                                             
  echo "=== QA-1.5: T0.9 RAG Health ===" | tee                                        
  "$EVIDENCE_DIR/phase1/qa1_5_rag.txt"                                                
                                                                                    
  # TEST 1: RAG health endpoint                                                       
  echo "--- TEST 1: RAG health ---" >> "$EVIDENCE_DIR/phase1/qa1_5_rag.txt"           
  curl $CURL_TIMEOUT -sf http://localhost:8052/health 2>&1 \                          
    | tee -a "$EVIDENCE_DIR/phase1/qa1_5_rag.txt"                                     
                                                                                      
  # TEST 2: SERVICE-CATALOG.md documents RAG                                          
  echo "--- TEST 2: SERVICE-CATALOG.md ---" >>                                        
  "$EVIDENCE_DIR/phase1/qa1_5_rag.txt"                                                
  rg -n -i "rag\|embedding\|8052" /home/zaks/bookkeeping/SERVICE-CATALOG.md 2>&1      
  \                                                                                   
    | tee -a "$EVIDENCE_DIR/phase1/qa1_5_rag.txt"                                     
  # Also check alternate locations                                                    
  find /home/zaks -name "SERVICE-CATALOG*" -o -name "service-catalog*"                
  2>/dev/null \                                                                       
    | tee -a "$EVIDENCE_DIR/phase1/qa1_5_rag.txt"                                     
  ```                                                                                 
                                                                                      
  **PASS:** RAG status documented (running or known-down).                            
  **IF FAIL → REMEDIATE:** Document RAG status in SERVICE-CATALOG.md.                 
                                                                                      
  ### QA-1.6: T0.10 — Health Check Aggregator                                         
                                                                                      
  ```bash                                                                         
  echo "=== QA-1.6: T0.10 Health Aggregator ===" | tee                                
  "$EVIDENCE_DIR/phase1/qa1_6_health_agg.txt"                                         
                                                                                      
  # TEST 1: Health aggregator endpoint in backend                                     
  echo "--- TEST 1: Health router ---" >>                                             
  "$EVIDENCE_DIR/phase1/qa1_6_health_agg.txt"                                         
  find "$BACKEND_REPO/src/api/orchestration/" -name "*health*" 2>&1 \                 
    | tee -a "$EVIDENCE_DIR/phase1/qa1_6_health_agg.txt"                              
  rg -n "health" "$BACKEND_REPO/src/api/orchestration/main.py" 2>&1 \                 
    | tee -a "$EVIDENCE_DIR/phase1/qa1_6_health_agg.txt"                              
                                                                                      
  # TEST 2: Live health endpoint                                                      
  echo "--- TEST 2: Live /health ---" >>                                              
  "$EVIDENCE_DIR/phase1/qa1_6_health_agg.txt"                                         
  curl $CURL_TIMEOUT -sf http://localhost:8091/health 2>&1 \                          
    | python3 -m json.tool | tee -a "$EVIDENCE_DIR/phase1/qa1_6_health_agg.txt"       
  ```                                                                                 
                                                                                      
  **PASS:** Health endpoint returns aggregated status.                                
                                                                                      
  ### QA-1.7: T0.11 + T0.12 — Zod Schema Fixes (ZK-ISSUE-0018)                        
                                                                                      
  ```bash                                                                             
  echo "=== QA-1: T0.11+T0.12 Zod Schemas ===" | tee                                
  "$EVIDENCE_DIR/phase1/qa1_7_zod.txt"                                                
                                                                                      
  # TEST 1: .passthrough() present in schemas                                         
  echo "--- TEST 1: Zod .passthrough() ---" >>                                        
  "$EVIDENCE_DIR/phase1/qa1_7_zod.txt"                                                
  rg -n "passthrough" "$DASHBOARD_DIR/src/lib/" --type ts 2>&1 \                      
    | tee -a "$EVIDENCE_DIR/phase1/qa1_7_zod.txt"                                     
                                                                                      
  # TEST 2: Schema validation logging                                                 
  echo "--- TEST 2: Schema validation logging ---" >>                                 
  "$EVIDENCE_DIR/phase1/qa1_7_zod.txt"                                                
  rg -n "schema.*warn\|validation.*log\|parse.*error\|safeParse"                      
  "$DASHBOARD_DIR/src/lib/" --type ts 2>&1 \                                          
    | tee -a "$EVIDENCE_DIR/phase1/qa1_7_zod.txt"                                     
                                                                                      
  # TEST 3: Check for strict schemas that would reject extra fields                   
  echo "--- TEST 3: Strict schemas ---" >> "$EVIDENCE_DIR/phase1/qa1_7_zod.txt"       
  rg -n "\.strict()" "$DASHBOARD_DIR/src/lib/" --type ts 2>&1 \                       
    | tee -a "$EVIDENCE_DIR/phase1/qa1_7_zod.txt"                                     
  ```                                                                                 
                                                                                      
  **PASS:** Schemas use `.passthrough()`, validation logging present.                 
  **IF FAIL → REMEDIATE:** Add `.passthrough()` to critical Zodchemas, add          
  console.warn logging.                                                               
                                                                                      
  ### Gate 0 Verification                                                             
                                                                                      
  ```bash                                                                             
  echo "=== GATE 0 VERIFICATION ===" | tee                                            
  "$EVIDENCE_DIR/phase1/gate0_signoff.txt"                                            
                                                                                      
  cat << 'GATE0' >> "$EVIDENCE_DIR/phase1/gate0_signoff.txt"                          
  GATE 0: STOP THE BLEEDING — PHASE 0 VERIFICATION                                    
                                                                                      
  | Gate Item | Task(s) | Issue | Verdict |vidence |                                
  |-----------|---------|-------|---------|----------|                                
  | Dashboard quarantine endpoint /process | T0.1 | ZK-0006 | [FILL] |                
  qa1_1_quarantine.txt |                                                              
  | Dashboard notes endpoint works | T0.2, T0.3 | ZK-0012 | [FILL] |                  
  qa1_2_notes.txt |                                                                   
  | No legacy stage names in code | T0.4, T0.5 | ZK-0007 | [FILL] |                   
  qa1_3_stages.txt |                                                                  
  | correlation_id in deal_events | T0.6-T0.8 | ZK-0011 | [FILL] |                    
  qa1_4_correlation.txt |                                                             
  | RAG health documented | T0.9 | ZK-0010 | [FILL] | qa1_5_rag.txt |                 
  | Health aggregator works | T0.10 | ZK-0010 | [FILL] | qa1_6_health_agg.txt |       
  | Zod schemas .passthrough() | T0.11-T0.12 | ZK-0018 | [FILL] | qa1_7_zod.txt |     
                                                                                      
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED.                                       
  GATE0                                                                               
  ```                                                                                 
                                                                                      
  **GATE QA-1: All Phase 0 tasks verified or remediated. No legacy stages.            
  Correlation wired.**                                                                
                                                                                      
  **>>> /compact checkpoint after Gate 0 <<<**                                        
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 4: QA PHASE 2 — PHASE 1 VERIFICATION (Split-Brain Elimination)           
                                                                                      
  **Covers:** ZK-ISSUE-0001 (P0), ZK-ISSUE-0008 (P1), ZK-ISSUE-0014 (P2)              
  **Tasks:** T1.1 through T1.9                                                        
  **HIGHEST RISK PHASE — P0 issue here**                                          
                                                                                      
  ### QA-2.1: T1.1 — id_map Table (ZK-ISSUE-0001)                                     
                                                                                      
  ```bash                                                                             
  echo "=== QA-2.1: T1.1 id_map Table ===" | tee                                      
  "$EVIDENCE_DIR/phase2/qa2_1_idmap.txt"                                            
                                                                                      
  # Does id_map table exist?                                                          
  $BACKEND_DB_CMD -c "\d id_map" 2>&1 | tee -a                                        
  "$EVIDENCE_DIR/phase2/qa2_1_idmap.txt"                                              
                                                                                      
  # Does it have the right schema?                                                    
  $BACKEND_DB_CMD -c "SELECT column_name, data_type FROM                              
  information_schema.columns WHERE table_name='id_map';" 2>&1 \                       
    | tee -a "$EVIDENCE_DIR/phase2/qa2_1_idmap.txt"                                   
  ```                                                                                 
                                                                                      
  **PASS:** Table exists with legacy_id and new_id columns.                           
  **IF FAIL → REMEDIATE:** Create the table with appropriate schema.                  
                                                                                      
  ### QA-2.2: T1.2 + T1.3 — Migration Script                                          
                                                                                      
  ```bash                                                                             
  echo "=== QA-2.2: T1.2+T1.3 Migratioript ===" | tee                             
  "$EVIDENCE_DIR/phase2/qa2_2_migration.txt"                                          
                                                                                      
  # Does migration script exist?                                                      
  find /home/zaks -path "*/migrations/migrate_json_to_postgres*" -o -path             
  "*/scripts/migrate*" 2>/dev/null \                                                  
    | tee -a "$EVIDENCE_DIR/phase2/qa2_2_migration.txt"                               
                                                                                      
  # Does deal_registry.json still exist? What's its content?                          
  echo "--- deal_registry.json ---" >> "$EVIDENCE_DIR/phase2/qa2_2_migration.txt"     
  ls -la /home/zaks/DataRoom/.deal-registry/deal_registry.json 2>&1 \                 
    | tee -a "$EVIDENCE_DIR/phase2/qa2_2_migration.txt"                               
  wc -l /home/zaks/DataRoom/.deal-registry/deal_registry.json 2>&1 \                  
    | tee -a "$EVIDENCE_DIR/phase2/qa2_2_migration.txt"                               
                                                                                      
  # Are deals in Postgres?                                                            
  echo "--- Postgres deal count ---" >>                                               
  "$EVIDENCE_DIR/phase2/qa2_2_migration.txt"                                          
  $BACKEND_DB_CMD -c "SELECT COUNT(*) as deal_count FROM deals;" 2>&1 \               
    | tee -a "$EVIDENCE_DIR/phase2/qa2_2_migration.txt"                               
  ```                                                                                 
                                                                                      
  **PASS:** Migration script exists. Deals are in Postgres. JSON has data but is      
  read-only.                                                                          
                                                                                      
  ### QA-2.3: T1.4 + T1.5 — Executor Refactor + sys.path Hack (ZK-ISSUE-0014)         
                                                                                      
  ```bash                                                                             
  echo "=== QA-2.3: T1.4+T1.5 Executor + sys.path ===" | tee                          
  "$EVIDENCE_DIR/phase2/qa2_3_executor.txt"                                         
                                                                                      
  # TEST 1: No sys.path hacks in production code                                      
  echo "--- TEST 1: sys.path scan ---" >>                                             
  "$EVIDENCE_DIR/phase2/qa2_3_executor.txt"                                           
  rg -n "sys\.path" "$BACKEND_REPO/src/" --type py 2>&1 \                             
    | tee -a "$EVIDENCE_DIR/phase2/qa2_3_executor.txt"                                
                                                                                      
  # TEST 2: Executor uses backend API, not direct JSON/SQLite                         
  echo "--- TEST 2: Executor imports ---" >>                                          
  "$EVIDENCE_DIR/phase2/qa2_3_executor.txt"                                           
  find "$BACKEND_REPO/src/actions/executors/" -name "*.py" -exec grep -l              
  "deal_registry\|json\.load\|sqlite3\|deal_state_machine" {} \; 2>&1 \               
    | tee -a "$EVIDENCE_DIR/phase2/qa2_3_executor.txt"                                
                                                                                      
  # TEST 3: CreateDealFromEmailExecutor exists and uses API                           
  echo "--- TEST 3: CreateDealFromEmailExecutor ---" >>                               
  "$EVIDENCE_DIR/phase2/qa2_3_executor.txt"                                           
  find "$BACKEND_REPO" -name "*deal_create*" -o -name "*email*executor*"              
  2>/dev/null \                                                                       
    | tee -a "$EVIDENCE_DIR/phase2/qa2_3_executor.txt"                                
  ```                                                                                 
                                                                                      
  **PASS:** No sys.path hacks. Executor uses API calls.                               
  **IF FAIL → REMEDIATE:** Remove sysath hacks. Refactor imports to use proper      
  module paths.                                                                       
                                                                                      
  ### QA-2.4: T1.6 — Action Engine Migration (ZK-ISSUE-0008)                          
                                                                                      
  ```bash                                                                             
  echo "=== QA-2.4: T1.6 Acon Engine ===" | tee                                     
  "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                            
                                                                                      
  # TEST 1: zakops.actions table exists in Postgres?                                  
  echo "--- TEST 1: actions table ---" >>                                             
  "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                            
  $BACKEND_DB_CMD -c "\d actions" 2>&1 | tee -a                                       
  "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                            
                                                                                      
  # TEST 2: Action engine store — does it use Postgres?                               
  echo "--- TEST 2: Store implementation ---" >>                                      
  "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                            
  find BACKEND_REPO/src/actions/" -name "store*" -o -name "engine*" 2>/dev/null     
   \                                                                                  
    | tee -a "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                 
  rg -n "sqlite\|SQLite" "$BACKEND_REPO/src/actions/" --type py 2>&1 \                
    | tee -a "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                 
                                                                                      
  # TEST 3: SQLite ingest_state.db — only email dedup, no deal state                  
  echo "--- TEST 3: SQLite content ---" >>                                            
  "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                            
  sqlite3 /home/zaks/DataRoom/.deal-registry/ingest_state.db ".tables" 2>&1 \         
    | tee -a "$EVIDENCE_DIR/phase2/qa2_4_actions.txt"                                 
  ```                                                                               
                                                                                      
  **PASS:** Actions in Postgres. SQLite has only dedup tables.                        
                                                                                      
  ### QA-2.5: T1.7 — JSON Registry Read-Only                                          
                                                                                      
  ```bash                                                                           
  echo "=== QA-2.5: T1.7 JSON Read-Only ===" | tee                                    
  "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                                      
                                                                                      
  # TEST 1: File permissions                                                          
  echo "--- TEST 1: File permissions ---" >>                                          
  "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                                      
  ls -la /home/zaks/DataRoom/.deal-registry/deal_registry.json 2>&1 \                 
    | tee -a "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                           
  stat /home/zaks/DataRoom/.deal-registry/deal_registry.json 2>&1 \                   
    | tee -a "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                           
                                                                                      
  # TEST 2: Canary write test — creating a dl via API should NOT modify JSON        
  echo "--- TEST 2: Canary test ---" >>                                               
  "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                                      
  BEFORE_HASH=$(md5sum /home/zaks/DataRoom/.deal-registry/deal_registry.json          
  2>/dev/null | cut -d' ' -f1)                                                        
  echo "Hash before: $BEFORE_HASH" >>                                                 
  "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                                      
                                                                                      
  # Create a canary deal                                                              
  curl $CURL_TIMEOUT -s -X POST http://localhost:8091/api/deals \                     
    -H "Content-Type: application/json" \                                             
    -H "X-API-Key: $ZAKOPS_API_KEY" \                                                 
    -d '{"canonical_name":"QA006-CANARY-'$(date +%s)'","stage":"inbound"}' 2>&1 \     
    | tee -a "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                           
                                                                                      
  sleep 2                                                                             
  AFTER_HASH=$(md5sum /home/zaks/DataRoom/.deal-registry/deal_registry.json           
  2>/dev/null | cut -d' ' -f1)                                                        
  echo "Hash after: $AFTER_HASH" >>                                                   
  "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                                      
                                                                                      
  if [ "$BEFORE_HASH" = "$AFTER_HASH" ]; then                                         
    echo "PASS: JSON unchanged" >> "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"     
  else                                                                                
    echo "FAIL: JSON was modified!" >>                                                
  "$EVIDENCE_DIR/phase2/qa2_5_json_readonly.txt"                                      
  fi                                                                                  
  ```                                                                                 
                                                                                      
  **PASS:** JSON file is read-only. Hash unchanged after deal creation.               
  **IF FAIL → REMEDIATE:** `chmod 444` on deal_registry.json. Find and remove         
  code that writes to it.                                                             
                                                                                      
  ### Gate 1 Verification                                                             
                                                                                      
  ```bash                                                                           
  echo "=== GATE 1 VERIFICATION ===" | tee                                            
  "$EVIDENCE_DIR/phase2/gate1_signoff.txt"                                            
                                                                                      
  cat << 'GATE1' >> "$EVIDENCE_DIR/phase2/gate1_signoff.txt"                          
  GATE 1: DATA TRUTH UNIFICATION — PHASE 1 VERIFICATION                               
                                                                                    
  | Gate Item | Task(s) | Issue | Verdict | Evidence |                                
  |-----------|---------|-------|---------|----------|                                
  | id_map table exists | T1.1 | ZK-0001 | [FILL] | qa2_1_idmap.txt |                 
  | Migration script + data in Postgres | T1.2-T1.3 | ZK-0001 | [FILL] |              
  qa2_2_migration.txt |                                                               
  | No sys.path hacks | T1.5 | ZK-0014 | [FILL] | qa2_3_executor.txt |                
  | Actions in Postgres (not SQLite) | T1.6 | ZK-0008 | [FILL] |                      
  qa2_4_actions.txt |                                                                 
  | JSON registry NOT modified by ops | T1.7 | ZK-0001 | [FILL] |                     
  qa2_5_json_readonly.txt |                                                           
  | RT-DB-SOT canary passed | T1.9 | ZK-0001 | [FILL] | qa0_3_db_sot.txt |            
                                                                                      
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED. ZK-0001 is P0 — MUST PASS.            
  GATE1                                                                               
  ```                                                                                 
                                                                                      
  **GATE QA-2: Split-brain eliminated. Postgres is sole source of truth. No           
  sys.path hacks.**                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 5: QA PHASE 3 — PHASE 2 VERIFICATION (Contract Alignment)                
                                                                                      
  **Covers:** ZK-ISSU0003 (P1), ZK-ISSUE-0004 (P1), ZK-ISSUE-0013 (P2),             
  ZK-ISSUE-0022 (P3)                                                                  
  **Tasks:** T2.1 through T2.9                                                        
                                                                                      
  ### QA-3.1: T2.1 — Quarantine Approval → Deal Creation (ZK-ISSUE-0003)              
                                                                                      
  ```bash                                                                         
  echo "=== QA-3.1: T2.1 Quarantine→Deal ===" | tee                                   
  "$EVIDENCE_DIR/phase3/qa3_1_quarantine_deal.txt"                                    
                                                                                      
  # TEST 1: Backend code for atomic deal creation on quarantine approval              
  echo "--- TEST 1: Quarantine approval wiring ---" >>                                
 $EVIDENCE_DIR/phase3/qa3_1_quarantine_deal.txt"                                    
  rg -n "quarantine.*deal\|process.*create\|approve.*deal"                            
  "$BACKEND_REPO/src/api/orchestration/" --type py 2>&1 \                             
    | tee -a "$EVIDENCE_DIR/phase3/qa3_1_quarantine_deal.txt"                         
                                                                                      
  # TEST 2: Live test if possible                                                     
  echo "--- TEST 2: Create quarantine item and approve ---" >>                        
  "$EVIDENCE_DIR/phase3/qa3_1_quarantine_deal.txt"                                    
  DEAL_COUNT_BEFORE=$($BACKEND_DB_CMD -t -c "SELECT COUNT(*) FROM deals;" 2>&1 |      
  tr -d ' \n')                                                                        
  echo "Deal count before: $DEAL_COUNT_BEFORE" >>                                     
  "$EVIDENCE_DIR/phase3/qa3_1_quarantine_deal.txt"                                    
                                                                                      
  # Check if there are pending quarantine items                                       
  $BACKEND_DB_CMD -c "SELECT id, status FROM quarantine_items WHERE status =          
  'pending' LIMIT 1;" 2>&1 \                                                          
    | tee -a "$EVIDENCE_DIR/phase3/qa3_1_quarantine_deal.txt"                         
  ```                                                                                 
                                                                                      
  **PASS:** Approving quarantine item creates deal atomically.                        
                                                                                      
  ### QA-3.2: T2.2 — DataRoom Folder Scaffolding (ZK-ISSUE-0004)                      
                                                                                      
  ```bash                                                                           
  echo "=== QA-3.2: T2.2 Folder Scaffolding ===" | tee                                
  "$EVIDENCE_DIR/phase3/qa3_2_folders.txt"                                            
                                                                                      
  # TEST 1: Folder scaffolding code exists                                            
  echo "--- TEST 1: Scaffolding code ---" >>                                          
  "$EVIDENCE_DIR/phase3/qa3_2_folders.txt"                                            
  rg -n "scaffold\|folder.*create\|DataRoom\|folder_path\|mkdir"                      
  "$BACKEND_REPO/src/" --type py 2>&1 \                                               
    | grep -i "deal" | tee -a "$EVIDENCE_DIR/phase3/qa3_2_folders.txt"                
                                                                                      
  # TEST 2: deals table has folder_path column                                        
  echo "--- TEST 2: folder_path column ---" >>                                        
  "$EVIDENCE_DIR/phase3/qa3_2_folders.txt"                                            
  $BACKEND_DB_CMD -c "SELECT column_name FROM information_schema.columns WHERE        
  table_name='deals' AND column_name='folder_path';" 2>&1 \                           
    | tee -a "$EVIDENCE_DIR/phase3/qa3_2_folders.txt"                                 
                                                                                      
  # TEST 3: Existing deals have folder paths?                                         
  echo "--- TEST 3: Deals with folder_path ---" >>                                    
  "$EVIDENCE_DIR/phase3/qa3_2_folders.txt"                                            
  $BACKEND_DB_CMD -c "SELECT deal_id, folder_path FROM deals WHERE folder_path IS     
   NOT NULL LIMIT 5;" 2>&1 \                                                          
    | tee -a "$EVIDENCE_DIR/phase3/qa3_2_folders.txt"                                 
  ```                                                                                 
                                                                                      
  **PASS:** Scaffolding code exists, folder_path column exists.                       
  **IF FAIL → REMEDIATE:** Add folder_path column if missing. Add scaffolding         
  hook to deal creation.                                                              
                                                                                       ### QA-3.3: T2.4 + T2.5 — Capabilities & Metrics Endpoints (ZK-ISSUE-0013)          
                                                                                      
  ```bash                                                                             
  echo "=== QA-3.3: T2.4+T2.5 Capabilities/Metrics ===" | tee                         
  "$EVIDENCE_DIR/phase3/qa3_3_caps_metrics.txt"                                       
                                                                                    
  # TEST 1: /capabilities endpoint                                                    
  echo "--- TEST 1: /capabilities ---" >>                                             
  "$EVIDENCE_DIR/phase3/qa3_3_caps_metrics.txt"                                       
  curl $CURL_TIMEOUT -s http://localhost:8091/api/actions/capabilities \              
    -H "X-API-Key: $ZAKOPS_API_KEY" 2>&1 \                                            
    | python3 -m json.tool | tee -a "$EVIDENCE_DIR/phase3/qa3_3_caps_metrics.txt"     
                                                                                      
  # TEST 2: /metrics endpoint                                                         
  echo "--- TEST 2: /metrics ---" >>                                                  
  "$EVIDENCE_DIR/phase3/qa3_3_caps_metrics.txt"                                       
  curl $CURL_TIMEOUT -s http://localhost:8091/api/actions/metrics \                   
    -H "X-API-Key: $ZAKOPS_API_KEY" 2>&1 \                                            
    | python3 -m json.tool | tee -a "$EVIDENCE_DIR/phase3/qa3_3_caps_metrics.txt"     
  ```                                                                                 
                                                                                      
  **PASS:** Both return 200 with data (not 501 or 404).                               
  **IF FAIL → REMEDIATE:** Add the endpoint routes to the actions router.             
                                                                                    
  ### QA-3.4: T2.6 + T2.7 — Archive/Restore Endpoints (ZK-ISSUE-0022)                 
                                                                                      
  ```bash                                                                             
  echo "=== QA-3.4: T2.6+T2.7 Archive/Restore ===" | tee                              
  "$EVIDENCE_DIR/phase3/qa3_4_archive.txt"                                            
                                                                                    
  DEAL_ID=$($BACKEND_DB_CMD -t -c "SELECT deal_id FROM deals WHERE stage !=           
  'archived' LIMIT 1;" 2>&1 | tr -d ' \n')                                            
  echo "Test deal: $DEAL_ID" >> "$EVIDENCE_DIR/phase3/qa3_4_archive.txt"              
                                                                                      
  # TEST 1: Archive endpoint                                                          
  echo "--- TEST 1: Archive ---" >> "$EVIDENCE_DIR/phase3/qa3_4_archive.txt"          
  curl $CURL_TIMEOUT -s -X POST                                                       
  "http://localhost:8091/api/deals/$DEAL_ID/archive" \                                
    -H "X-API-Key: $ZAKOPS_API_KEY" 2>&1 \                                            
    | tee -a "$EVIDENCE_DIR/phase3/qa3_4_archive.txt"                                 
                                                                                      
  # TEST 2: Restore endpoint                                                          
  echo "--- TEST 2: Restore ---" >> "$EVIDENCE_DIR/phase3/qa3_4_archive.txt"          
  curl $CURL_TIMEOUT -s -X POST                                                       
  "http://localhost:8091/api/deals/$DEAL_ID/restore" \                                
    -H "X-API-Key: $ZAKOPS_API_KEY" 2>&1 \                                            
    | tee -a "$EVIDENCE_DIR/phase3/qa3_4_archive.txt"                                 
  ```                                                                                 
                                                                                      
  **PASS:** Both endpoints return 200 and deal state changes accordingly.             
  **IF FAIL → REMEDIATE:** Add archive/restore routes to the orchestration API.       
                                                                                      
  ### Gate 2 Verification                                                           
                                                                                      
  ```bash                                                                             
  echo "=== GATE 2 VERIFICATION ===" | tee                                            
  "$EVIDENCE_DIR/phase3/gate2_signoff.txt"                                            
                                                                                      
  cat << 'GATE2' >> "$EVIDENCE_DIR/phase3/gate2_signoff.txt"                          
  GATE 2: CONTRACT ALIGNMENT — PHASE 2 VERIFICATION                                   
                                                                                      
  | Gate Item | Task(s) | Issue | Verdict | Evidence |                                
  |-----------|---------|-------|---------|----------|                                
  | Quarantine→deal atomic | T2.1 | ZK-0003 | [FILL] | qa3_1_quarantine_deal.txt      
  |                                                                               
  | Folder scaffolding works | T2.2 | ZK-0004 | [FILL] | qa3_2_folders.txt |          
  | /capabilities returns 200 | T2.4 | ZK-0013 | [FILL] | qa3_3_caps_metrics.txt      
  |                                                                                   
  | /metrics returns 200 | T2.5 | ZK-0013 | [FILL] | qa3_3_caps_metrics.txt |         
  | Archive/restore work | T2.6-T2.7 | ZK-0022 | [FILL] | qa3_4_archive.txt |         
                                                                                      
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED.                                       
  GATE2                                                                               
  ```                                                                                 
                                                                                      
  **>>> /compact checkpoint after Gate 2 <<<**                                        
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 6: QA PHASE 4 — PHASE 3 VERIFICATION (Deal Lifecycle Correctness)        
                                                                                      
  **Covers:** ZK-ISSUE-0009 (P2), ZK-ISSUE-0015 (P3), ZK-ISSUE-0016 (P2)              
  **Tasks:** T3.1 through T3.7                                                      
                                                                                      
  ### QA-4.1: T3.1 + T3.2 — Agent Tools: create_deal + add_note (ZK-ISSUE-0009)       
                                                                                      
  ```bash                                                                             
  echo "=== QA-4.1: T3.1+T3.2 Agent Tools ===" | tee                                  
  "$EVIDENCE_DIR/phaseqa4_1_agent_tools.txt"                                        
                                                                                      
  # TEST 1: create_deal tool exists                                                   
  echo "--- TEST 1: create_deal tool ---" >>                                          
  "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                                        
  rg -n "create_deal\|CreateDeal" "$AGENT_API_DIR/app/core/langgraph/tools/"          
  --type py 2>&1 \                                                                    
    | tee -a "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                             
                                                                                      
  # TEST 2: add_note tool exists                                                      
  echo "--- TEST 2: add_note tool ---" >>                                             
  "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                                        
  rg -n "add_note\|AddNote" "$AGENT_API_DIR/app/core/langgraph/tools/" --type py      
  2>&1 \                                                                              
    | tee -a "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                             
                                                                                      
  # TEST 3: Tools registered in graph                                                 
  echo "--- TEST 3: Tool registration ---" >>                                         
  "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                                        
  rg -n "create_deal\|add_note" "$AGENT_API_DIR/app/core/langgraph/graph.py" 2>&1     
   \                                                                                  
    | tee -a "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                             
                                                                                      
  # TEST 4: No direct DB imports in tools (D-FINAL-03 enforcement)                    
  echo "--- TEST 4: No direct DB access ---" >>                                       
  "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                                        
  rg "asyncpg|sqlalchemy|psycopg|import.*pg"                                          
  "$AGENT_API_DIR/app/core/langgraph/tools/" 2>&1 \                                   
    | tee -a "$EVIDENCE_DIR/phase4/qa4_1_agent_tools.txt"                             
  ```                                                                                 
                                                                                      
  **PASS:** Both tools exist, registered in graph, no direct DB imports.              
  **IF FAIL → REMEDIATE:** Create the missing tool files following D-FINAL-03         
  contract (HTTP API calls only).                                                     
                                                                                      
  ### QA-4.2: T3.3 — Correlation ID in Agent To(ZK-ISSUE-0011)                    
                                                                                      
  ```bash                                                                             
  echo "=== QA-4.2: T3.3 Agent Correlation ===" | tee                                 
  "$EVIDENCE_DIR/phase4/qa4_2_agent_corr.txt"                                         
                                                                                      
  # All tool HTTP calls must include X-Correlation-ID                                 
  rg -n "X-Correlation-ID\|correlation"                                               
  "$AGENT_API_DIR/app/core/langgraph/tools/" --type py 2>&1 \                         
    | tee -a "$EVIDENCE_DIR/phase4/qa4_2_agent_corr.txt"                              
                                                                                      
  # Check HTTP client/helper for default headers                                      
  rg -n "X-Correlation-ID\|correlation" "$AGENT_API_DIR/app/" --type py -l 2>&1 \     
    | tee -a "$EVIDENCE_DIR/phase4/qa4_2_agent_corr.txt"                              
  ```                                                                                 
                                                                                      
  **PASS:** All tool HTTP calls include X-Correlation-ID.                             
                                                                                      
  ### QA-4.3: T3.4 âuplicate Detection (ZK-ISSUE-0016)                              
                                                                                      
  ```bash                                                                             
  echo "=== QA-4.3: T3.4 Duplicate Detection ===" | tee                               
  "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                                         
                                                                                      
  # TEST 1: Code has duplicate check                                                  
  echo "--- TEST 1: Duplicate check code ---" >>                                      
  "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                                         
  rg -n "duplicate\|conflict\|409\|already.*exist\|canonical_name.*unique"            
  "$BACKEND_REPO/src/api/orchestration/" --type py 2>&1 \                             
    | tee -a "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                              
                                                                                      
  # TEST 2: Unique constraint on deals                                                
  echo "--- TEST 2: Unique constraints ---" >>                                        
  "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                                         
  $BACKEND_DB_CMD -c "\d deals" 2>&1 | grep -i "unique\|constraint\|index" \          
    | tee -a "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                              
                                                                                      
  # TEST 3: Live duplicate test                                                       
  echo "--- TEST 3: Live duplicate test ---" >>                                       
  "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                                         
  UNIQUE_NAME="QA006-DUP-$(date +%s)"                                                 
  # Create first                                                                      
  curl $CURL_TIMEOUT -s -X POST http://localhost:8091/api/deals \                     
    -H "Content-Type: application/json" \                                             
    -H "X-API-Key: $ZAKOPS_API_KEY" \                                                 
    -d "{\"canonical_name\":\"$UNIQUE_NAME\",\"stage\":\"inbound\"}" 2>&1 \           
    | tee -a "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                              
  # Create duplicate — should fail                                                  
  echo "--- Duplicate attempt ---" >> "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"     
  curl $CURL_TIMEOUT -s -X POST http://localhost:8091/api/deals \                     
    -H "Content-Type: application/json" \                                             
    -H "X-API-Key: $ZAKOPS_API_KEY" \                                                 
    -d "{\"canonical_name\":\"$UNIQUE_NAME\",\"stage\":\"inbound\"}" 2>&1 \           
    | tee -a "$EVIDENCE_DIR/phase4/qa4_3_duplicates.txt"                              
  ```                                                                                 
                                                                                      
  **PASS:** Second creation returns 409 Conflict.                                     
  **IF FAIL → REMEDIATE:** Add unique constraint on canonical_name. Add duplicate     
   check in POST handler.                                                             
                                                                                    
  ### QA-4.4: T3.5 + T3.6 — Approval Expiry + Optimistic Locking (ZK-ISSUE-0015)      
                                                                                      
  ```bash                                                                             
  echo "=== QA-4.4: T3.5+T3.6 Approval Expiry ===" | tee                              
  "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                           
                                                                                    
  # TEST 1: Expiry job code exists                                                    
  echo "--- TEST 1: Approval expiry job ---" >>                                       
  "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                           
  find "$AGENT_API_DIR" -name "*expir*" -o -name "*ttl*" 2>/dev/null \                
    | tee -a "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                
  rg -n "expir\|ttl\|stale" "$AGENT_API_DIR/app/" --type py 2>&1 \                    
    | tee -a "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                
                                                                                      
  # TEST 2: Approval table has expiry column                                          
  echo "--- TEST 2: Approval schema ---" >>                                           
  "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                           
  $AGENT_DB_CMD -c "\d approvals" 2>&1 | tee -a                                       
  "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                           
                                                                                      
  # TEST 3: Optimistic locking (version or updated_at check)                          
  echo "--- TEST 3: Optimistic locking ---" >>                                        
  "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                           
  rg -n "version\|optimistic\|CAS\|compare.*swap\|updated_at.*WHERE"                  
  "$AGENT_API_DIR/app/" --type py 2>&1 \                                              
    | tee -a "$EVIDENCE_DIR/phase4/qa4_4_approval.txt"                                
  ```                                                                                 
                                                                                      
  **PASS:** Expiry mechanism exists. TTL field in schema. Locking present.            
                                                                                      
  ### QA-4.5: T3.7 — Approval Audit Mirror (ZK-ISSUE-0015, D-FINAL-06)                
                                                                                      
  ```bash                                                                             
  echo "=== QA-4.5: T3.7 Approval Audit ===" | tee                                    
  "$EVIDENCE_DIR/phase4/qa4_5_audit_mirror.txt"                                     
                                                                                      
  # TEST 1: approval_audit table in backend DB                                        
  echo "--- TEST 1: approval_audit table ---" >>                                      
  "$EVIDENCE_DIR/phase4/qa4_5_audit_mirror.txt"                                       
  $BACKEND_DB_CMD -c "\d approval_audit" 2>&1 \                                       
    | tee -a "$EVIDENCE_DIR/phase4/qa4_5_audit_mirror.txt"                            
                                                                                      
  # TEST 2: Mirror code exists                                                        
  echo "--- TEST 2: Mirror code ---" >>                                               
  "$EVIDENCE_DIR/phase4/qa4_5_audit_mirror.txt"                                       
  rg -n "approval_audit\|mirror.*approval\|approval.*mirror"                          
  "$AGENT_API_DIR/app/" --type py 2>&1 \                                              
    | tee -a "$EVIDENCE_DIR/phase4/qa4_5_audit_mirror.txt"                            
  rg -n "approval_audit" "$BACKEND_REPO/src/" --type py 2>&1 \                        
    | tee -a "$EVIDENCE_DIR/phase4/qa4_5_audit_mirror.txt"                            
  ```                                                                                 
                                                                                      
  **PASS:** Table exists with correlation_id, deal_id, action_type columns.           
                                                                                      
  ### Gate 3 Verification                                                             
                                                                                      
  ```bash                                                                             
  echo "=== GATE 3 VERIFICATION ===" | tee                                            
  "$EVIDENCE_DIR/phase4/gate3_signoff.txt"                                            
                                                                                      
  cat << 'GATE3' >> "$EVIDENCE_DIR/phase4/gate3_signoff.txt"                          
  GATE 3: DEAL LIFECYCLE CORRECTNESS — PHASE 3 VERIFICATION                           
                                                                                      
  | Gate Item | Task(s) | Issue | Verdict | Evidence |                                
  |-------------------|-------|---------|----------|                                
  | create_deal agent tool exists | T3.1 | ZK-0009 | [FILL] |                         
  qa4_1_agent_tools.txt |                                                             
  | add_note agent tool exists | T3.2 | ZK-0009 | [FILL] | qa4_1_agent_tools.txt      
  |                                                                                   
  | Correlation IDs in agent tools | T3.3 | ZK-0011 | [FILL] |                        
  qa4_2_agent_corr.txt |                                                              
  | Duplicate detection (409) | T3.4 | ZK-0016 | [FILL] | qa4_3_duplicates.txt |      
  | Approval expiry mechanism | T3.5-T3.6 | ZK-0015 | [FILL] | qa4_4_approval.txt     
   |                                                                                  
  | Approval audit mirror | T3.7 | ZK-0015 | [FILL] | qa4_5_audit_mirror.txt |        
                                                                                      
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED.                                       
  GATE3                                                                               
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 7: QA PHASE 5 — PHASE 4 VERIFICATION (Deal Knowledge System)             
                                                                                      
  **Covers:** ZK-ISSUE-0002 (P0), ZK-ISSUE-0019 (P2), ZK-ISSUE-0020 (P2),             
  ZK-ISSUE-0021 (P2)                                                                  
  **Tasks:** T4.1 through T4.14                                                       
  **LARGEST SCOPE PHASE — P0 issue here (email ingestion)*                        
                                                                                      
  ### QA-5.1: T4.1 — Email Ingestion Refactor (ZK-ISSUE-0002 — P0)                    
                                                                                      
  ```bash                                                                             
  echo "=== QA-5.1: T4.1 Email Ingestion ===" | tee                                   
  "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                          
                                                                                      
  # TEST 1: Email ingestion Stage 4 uses backend API (not direct JSON/SQLite)         
  echo "--- TEST 1: Stage 4 implementation ---" >>                                    
  "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                              
  find "$SCRIPTS_DIR/email_ingestion/" -name "*stage*4*" -o -name "*persist*"         
  2>/dev/null \                                                                       
    | tee -a "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                   
  rg -n "api/quarantine\|POST.*quarantine\|requests\.post"                            
  "$SCRIPTS_DIR/email_ingestion/" --type py 2>&1 \                                    
    | tee -a "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                   
                                                                                      
  # TEST 2: No direct JSON/SQLite writes for deals                                    
  echo "--- TEST 2: No legacy writes ---" >>                                          
  "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                              
  rg -n "deal_registry\.json\|json\.dump.*deal\|sqlite.*deal"                         
  "$SCRIPTS_DIR/email_ingestion/" --type py 2>&1 \                                    
    | tee -a "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                   
                                                                                      
  # TEST 3: quarantine_items table exists                                             
  echo "--- TEST 3: quarantine_items table ---" >>                                    
  "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                              
  $BACKEND_DB_CMD -c "\d quarantine_items" 2>&1 \                                     
    | tee -a "$EVIDENCE_DIR/phase5/qa5_1_email.txt"                                   
  ```                                                                                 
                                                                                      
  **PASS:** Stage 4 calls backend API. No legacy writes. Quarantine table exists.     
  **Note:** Full email ingestion refactor may be DEFERRED if it's a major             
  architectural change. Document status.                                              
                                                                                      
  ### QA-5.2: T4.2 — Idempotency Key Table                                            
                                                                                      
  ```bash                                                                             
  echo "=== QA-5.2: T4.2 Idempotency ===" | tee                                       
  "$EVIDENCE_DIR/phase5/qa5_2_idempotency.txt"                                        
                                                                                    
  # TEST 1: Idempotency table                                                         
  $BACKEND_DB_CMD -c "\dt *idempotency*" 2>&1 \                                       
    | tee -a "$EVIDENCE_DIR/phase5/qa5_2_idempotency.txt"                             
  $BACKEND_DB_CMD -c "\dt *dedup*" 2>&1 \                                             
    | tee -a "$EVIDENCE_DIR/phase5/qa5_2_idempotency.txt"                             
                                                                                      
  # TEST 2: Or unique constraint on quarantine_items                                  
  $BACKEND_DB_CMD -c "SELECT indexname, indexdef FROM pg_indexes WHERE tablename      
  = 'quarantine_items';" 2>&1 \                                                       
    | tee -a "$EVIDENCE_DIR/phase5/qa5_2_idempotency.txt"                             
  ```                                                                                 
                                                                                      
  **PASS:** Idempotency mechanism exists (table or unique constraint).                
                                                                                      
  ### QA-5.3: T4.6 + T4.7 + T4.8 — Executor Wiring (ZK-ISSUE-0019)                    
                                                                                      
  ```bash                                                                             
  echo "=== QA-5.3: T4.6-T4.8 Executors ===" | e                                    
  "$EVIDENCE_DIR/phase5/qa5_3_executors.txt"                                          
                                                                                      
  # TEST 1: Executor files exist                                                      
  echo "--- TEST 1: Executor files ---" >>                                            
  "$EVIDENCE_DIR/phase5/qa5_3_executors.txt"                                          
  find "$BACKEND_REPO/src/actions/executors/" -name "*.py" 2>/dev/null \              
    | tee -a "$EVIDENCE_DIR/phase5/qa5_3_executors.txt"                               
                                                                                      
  # TEST 2: Executors are registered                                                  
  echo "--- TEST 2: Executor registration ---" >>                                     
  "$EVIDENCE_DIR/phase5/qa5_3_executors.txt"                                          
  rg -n "register\|executor\|ExecutorRegistry\|EXECUTORS"                             
  "$BACKEND_REPO/src/actions/" --type py 2>&1 \                                       
    | grep -i "register\|map\|dict" | tee -a                                          
  "$EVIDENCE_DIR/phase5/qa5_3_executors.txt"                                          
                                                                                      
  # TEST 3: At least 3 executors wired                                                
  echo "--- TEST 3: Executor count ---" >>                                            
  "$EVIDENCE_DIR/phase5/qa5_3_executors.txt"                                          
  EXECUTOR_COUNT=$(find "$BACKEND_REPO/src/actions/executors/" -name "*.py" -not      
  -name "__init__*" 2>/dev/null | wc -l)                                              
  echo "Executor files: $EXECUTOR_COUNT" >>                                           
  "$EVIDENCE_DIR/phase5/qa5_3_executors.txt"                                          
  ```                                                                                 
                                                                                      
  **PASS:** At least 3 executor files exist and are registered.                       
                                                                                      
  ### QA-5.4: T4.9 + T4.10 — RAG Indexing Columns (ZK-ISSUE-0010)                     
                                                                                    
  ```bash                                                                             
  echo "=== QA-5.4: T4.9+T4.10 RAG Columns ===" | tee                                 
  "$EVIDENCE_DIR/phase5/qa5_4_rag_columns.txt"                                        
                                                                                      
  # TEST 1: last_indexed_at column                                                    
  $BACKEND_DB_CMD -c "SELECT column_name FROM information_schema.columns WHERE        
  table_name='deals' AND column_name IN ('last_indexed_at','content_hash');" 2>&1     
   \                                                                                  
    | tee -a "$EVIDENCE_DIR/phase5/qa5_4_rag_columns.txt"                             
                                                                                      
  # TEST 2: Indexing hook code                                                        
  rg -n "last_indexed_at\|content_hash\|reindex" "$BACKEND_REPO/src/" --type py       
  2>&1 \                                                                              
    | tee -a "$EVIDENCE_DIR/phase5/qa5_4_rag_columns.txt"                             
  ```                                                                                 
                                                                                      
  **PASS:** Columns exist. Indexing hook code present.                                
                                                                                      
  ### QA-5.5: T4.12 — SSE Endpoint (ZK-ISSUE-0020)                                    
                                                                                      
  ```bash                                                                             
  echo "=== QA-5.5: T4.12 SSE ===" | tee "$EVIDENCE_DIR/phase5/qa5_5_sse.txt"         
                                                                                      
  # TEST 1: SSE code exists                                                         
  rg -n "SSE\|EventSource\|text/event-stream\|StreamingResponse"                      
  "$BACKEND_REPO/src/" --type py 2>&1 \                                               
    | tee -a "$EVIDENCE_DIR/phase5/qa5_5_sse.txt"                                     
                                                                                      
  # TEST 2: Or documented as polling                                                  
  rg -rn "polling\|SSE.*not.*implement\|event.*stream" /home/zaks/bookkeeping/        
  2>/dev/null \                                                                       
    | tee -a "$EVIDENCE_DIR/phase5/qa5_5_sse.txt"                                     
  ```                                                                                 
                                                                                      
  **PASS:** SSE works OR documented as intentional polling.                           
                                                                                      
  ### QA-5.6: T4.13 + T4.14 — Deal Age + Reminders (ZK-ISSUE-0021)                    
                                                                                      
  ```bash                                                                             
  echo "=== QA-5.6: T4.13+T4.14 Scheduling ===" | tee                                 
  "$EVIDENCE_DIR/phase5/qa5_6_scheduling.txt"                                         
                                                                                    
  # TEST 1: Deal age tracking                                                         
  $BACKEND_DB_CMD -c "SELECT column_name FROM information_schema.columns WHERE        
  table_name='deals' AND column_name IN                                               
  ('created_at','updated_at','stage_entered_at');" 2>&1 \                             
    | tee -a "$EVIDENCE_DIR/phase5/qa5_6_scheduling.txt"                              
                                                                                      
  # TEST 2: Reminder/scheduler code                                                   
  rg -n "reminder\|schedule\|cron\|overdue\|stale.*deal" "$BACKEND_REPO/src/"         
  --type py 2>&1 \                                                                    
    | tee -a "$EVIDENCE_DIR/phase5/qa5_6_scheduling.txt"                              
  ```                                                                                 
                                                                                      
  **PASS:** Age tracking fields exist. Reminder mechanism present.                    
                                                                                      
  ### Gate 4 Verification                                                             
                                                                                      
  ```bash                                                                             
  echo "=== GATE 4 VERIFICATION ===" | tee                                            
  "$EVIDENCE_DIR/phase5/gate4_signoff.txt"                                            
                                                                                      
  cat << 'GATE4' >> "$EVIDENCE_DIR/phase5/gate4_signoff.txt"                          
  GATE 4: DEAL KNOWLEDGE SYSTEM — PHASE 4 VERIFICATION                                
                                                                                    
  | Gate Item | Task(s) | Issue | Verdict | Evidence |                                
  |-----------|---------|-------|---------|----------|                                
  | Email ingestion uses API | T4.1 | ZK-0002 | [FILL] | qa5_1_email.txt |            
  | Idempotency mechanism | T4.2 | ZK-0002 | [FILL] | qa5_2_idempotency.txt |         
  | 3+ executors wired | T4.6-T4.8 | ZK-0019 | [FILL] | qa5_3_executors.txt |         
  | RAG indexing columns | T4.9-T4.10 | ZK-0010 | [FILL] | qa5_4_rag_columns.txt      
  |                                                                                   
  | SSE or documented polling | T4.12 | ZK-0020 | [FILL] | qa5_5_sse.txt |            
  | Deal age + reminders | T4.13-T4.14 | ZK-0021 | [FILL] | qa5_6_scheduling.txt      
  |                                                                                   
                                                                                      
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED. ZK-0002 is P0 — document              
  thoroughly.                                                                         
  GATE4                                                                               
  ```                                                                                 
                                                                                      
  **>>> /compact checkpoint after Gate 4 <<<**                                        
                                                                                    
  ---                                                                                 
                                                                                      
  ## SECTION 8: QA PHASE 6 — PHASE 5 VERIFICATION (Hardening)                         
                                                                                      
  **Covers:** ZK-ISSUE-0005 (P1), ZK-ISSUE-0017 (P3)                                  
  **Tasks:** T5.1 thrgh T5.10                                                       
                                                                                      
  ### QA-6.1: T5.1 + T5.2 + T5.3 — User Authentication (ZK-ISSUE-0005)                
                                                                                      
  ```bash                                                                             
  echo "=== QA-6.1: T5.1-T5.3 Auth ===" | tee                                         
  "$EVIDENCDIR/phase6/qa6_1_auth.txt"                                               
                                                                                      
  # TEST 1: Auth middleware exists                                                    
  echo "--- TEST 1: Auth middleware ---" >> "$EVIDENCE_DIR/phase6/qa6_1_auth.txt"     
  rg -n "auth\|jwt\|session\|login\|OIDC" "$DASHBOARD_DIR/src/middleware.ts" 2>&1     
   \                                                                                  
    | tee -a "$EVIDENCE_DIR/phase6/qa6_1_auth.txt"                                    
                                                                                      
  # TEST 2: Dashboard requires login                                                  
  echo "--- TEST 2: Unauthenticated access ---" >>                                    
  "$EVIDENCE_DIR/phase6/qa6_1_auth.txt"                                               
  curl $CURL_TIMEOUT -s -o /dev/null -w "%{http_code} %{redirect_url}\n"              
  http://localhost:3003/deals 2>&1 \                                                  
    | tee -a "$EVIDENCE_DIR/phase6/qa6_1_auth.txt"                                    
  # PASS if 401 or redirect to login                                                  
                                                                                      
  # TEST 3: Backend auth enforcement                                                  
  echo "--- TEST 3: Backend auth ---" >> "$EVIDENCE_DIR/phase6/qa6_1_auth.txt"        
  curl $CURL_TIMEOUT -s -X POST http://localhost:8091/api/deals \                     
    -H "Content-Type: application/json" \                                             
    -d '{"canonical_name":"no-auth-test"}' 2>&1 \                                     
    | tee -a "$EVIDENCE_DIR/phase6/qa6_1_auth.txt"                                    
  # PASS if 401/403                                                                   
  ```                                                                                 
                                                                                      
  **PASS:** Auth middleware exists. Unauthenticated requests blocked.                 
  **Note:** Full OIDC/JWT may be DEFERRED (requires product decisions). Document      
  API key auth status.                                                                
                                                                                      
  ### QA-6.2: T5.5 + T5.6 — Retention Policy (ZKSSUE-0017)                          
                                                                                      
  ```bash                                                                             
  echo "=== QA-6.2: T5.5+T5.6 Retention ===" | tee                                    
  "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                                          
                                                                                      
  # TEST 1: Retention policy document exists                                          
  echo "--- TEST 1: Policy document ---" >>                                           
  "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                                          
  find /home/zaks -name "*retention*" -o -name "*RETENTION*" 2>/dev/null \            
    | tee -a "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                               
                                                                                      
  # TEST 2: Cleanup/archive mechanism                                                 
  echo "--- TEST 2: Cleanup code ---" >>                                              
  "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                                          
  rg -rn "retention\|cleanup\|archive.*audit\|purge" "$AGENT_API_DIR/"                
  "$BACKEND_REPO/src/" --type py --type sql 2>&1 \                                    
    | tee -a "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                               
  find "$AGENT_API_DIR/scripts/" -name "*archive*" -o -name "*retention*" -o          
  -name "*maintenance*" 2>/dev/null \                                                 
    | tee -a "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                               
                                                                                      
  # TEST 3: audit_log_archive table?                                                  
  echo "--- TEST 3: Archive table ---" >>                                             
  "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                                          
  $AGENT_DB_CMD -c "\d audit_log_archive" 2>&1 \                                      
    | tee -a "$EVIDENCE_DIR/phase6/qa6_2_retention.txt"                               
  ```                                                                                 
                                                                                      
  **PASS:** Policy documented. Archive mechanism exists.                              
                                                                                      
  ### QA-6.3: T5.7 — Request Tracing                                                  
                                                                                      
  ```bash                                                                             
  echo "=== QA-6.3: T5.7 Tracing ===" | tee                                           
  "$EVIDENCE_DIR/phase6/qa6_3_tracing.txt"                                          
                                                                                      
  # TEST 1: Request tracing in backend                                                
  rg -n "trace_id\|request_id\|X-Request-ID" "$BACKEND_REPO/src/" --type py 2>&1      
  \                                                                                   
    | tee -a "$EVIDENCE_DIR/phase6/qa6_3_tracing.txt"                                 
                                                                                      
  # TEST 2: Tracing in agent API                                                      
  rg -n "trace_id\|request_id\|trace_sink\|tracing" "$AGENT_API_DIR/app/" --type      
  py 2>&1 \                                                                           
    | tee -a "$EVIDENCE_DIR/phase6/qa6_3_tracing.txt"                                 
  ```                                                                                 
                                                                                      
  **PASS:** Request tracing visible in code.                                          
                                                                                      
  ### Gate 5 Verification                                                             
                                                                                      
  ```bash                                                                             
  echo "=== GATE 5 VERIFICATION ===" | tee                                            
  "$EVIDENCE_DIR/phase6/gate5_signoff.txt"                                            
                                                                                      
  cat << 'GATE5' >> "$EVIDENCE_DIR/phase6/gate5_signoff.txt"                          
  GATE 5: HARDENING — PHASE 5 VERIFICATION                                            
                                                                                      
  | Gate Item | Task(s) | Issue | Vdict | Evidence |                                
  |-----------|---------|-------|---------|----------|                                
  | Auth middleware exists | T5.1-T5.3 | ZK-0005 | [FILL] | qa6_1_auth.txt |          
  | Retention policy documented | T5.5-T5.6 | ZK-0017 | [FILL] |                      
  qa6_2_retention.txt |                                                               
  | Request tracing present | T5.7 | — | [FILL] | qa6_3_tracing.txt |                 
                                                                                    
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED.                                       
  GATE5                                                                               
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 9: QA PHASE 7 — PHASE 6 VERIFICATION (Legacy Decommission)               
                                                                                      
  **Covers:** Final verification of all 22 issues                                     
  **Tasks:** T6.1 through T6.10                                                       
                                                                                      
  ###A-7.1: T6.1 through T6.5 — Legacy File Deletion                                
                                                                                      
  ```bash                                                                             
  echo "=== QA-7.1: Legacy Files ===" | tee                                           
  "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                                       
                                                                                    
  # TEST 1: deal_registry.json — exists but read-only (or deleted)                    
  echo "--- deal_registry.json ---" >>                                                
  "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                                       
  ls -la /home/zaks/DataRoom/.deal-registry/deal_registry.json 2>&1 \                 
    | tee -a "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                            
                                                                                    
  # TEST 2: deal_registry.py — should be deleted                                      
  echo "--- deal_registry.py ---" >>                                                  
  "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                                       
  ls -la /home/zaks/scripts/deal_registry.py 2>&1 \                                   
    | tee -a "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                            
                                                                                    
  # TEST 3: deal_state_machine.py — should be deleted (already checked in QA-1.3)     
  echo "--- deal_state_machine.py ---" >>                                             
  "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                                       
  ls -la /home/zaks/scripts/deal_state_machine.py 2>&1 \                              
    | tee -a "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                            
                                                                                    
  # TEST 4: api/deal_lifecycle/ — should be deleted                                   
  echo "--- api/deal_lifecycle/ ---" >>                                               
  "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                                       
  ls -la "$BACKEND_REPO/src/api/deal_lifecycle/" 2>&1 \                               
    | tee -a "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                            
                                                                                    
  # TEST 5: No legacy references in codebase                                          
  echo "--- TEST 5: Legacy reference scan ---" >>                                     
  "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                                       
  rg "deal_registry\.json\|deal_state_machine\|deal_lifecycle\|sys\.path" \           
    "$BACKEND_REPO/src/" "$AGENT_API_DIR/app/" --type py --type ts 2>&1 \             
    | tee -a "$EVIDENCE_DIR/phase6/qa7_1_legacy_files.txt"                            
  ```                                                                                 
                                                                                      
  **PASS:** Legacy files deleted or read-only. Zero legacy references in              
  production code.                                                                    
  **IF FAIL → REMEDIATE:** Delete the files. Remove code references.                  
                                                                                    
  ### QA-7.2: T6.7 — SERVICE-CATALOG.md Updated                                       
                                                                                      
  ```bash                                                                             
  echo "=== QA-7.2: SERVICE-CATALOG ===" | tee                                        
  "$EVIDENCE_DIR/phase6/qa7_2_catalog.txt"                                            
                                                                                    
  find /home/zaks -name "SERVICE-CATALOG*" 2>/dev/null | while read f; do             
    echo "--- $f ---" >> "$EVIDENCE_DIR/phase6/qa7_2_catalog.txt"                     
    cat "$f" >> "$EVIDENCE_DIR/phase6/qa7_2_catalog.txt"                              
  done                                                                                
  ```                                                                                 
                                                                                      
  ### QA-7.3: T6.10 — CHANGES.md Entry                                                
                                                                                      
  ```bash                                                                             
  echo "=== QA-7.3: CHANGES.md ===" | tee                                             
  "$EVIDENCE_DIR/phase6/qa7_3_changes.txt"                                          
                                                                                      
  rg "LEGACY DECOMMISSION\|deal_registry\|V3.*Remediation"                            
  /home/zaks/bookkeeping/CHANGES.md 2>&1 \                                            
    | tee -a "$EVIDENCE_DIR/phase6/qa7_3_changes.txt"                                 
  ```                                                                                 
                                                                                      
  **PASS:** CHANGES.md has legacy decommission entry.                                 
  **IF FAIL → REMEDIATE:** Add the entry per the V3 FINAL plan's changelog            
  strategy.                                                                           
                                                                                      
  ### Gate 6 Verification                                                             
                                                                                    
  ```bash                                                                             
  echo "=== GATE 6 VERIFICATION ===" | tee                                            
  "$EVIDENCE_DIR/phase6/gate6_signoff.txt"                                            
                                                                                      
  cat << 'GATE6' >> "$EVIDENCE_DIR/phase6/gate6_signoff.txt"                          
  GATE 6: LEGACY DECOMMISSION — PHASE 6 VERIFICATN                                  
                                                                                      
  | Gate Item | Task(s) | Issue | Verdict | Evidence |                                
  |-----------|---------|-------|---------|----------|                                
  | Legacy files deleted/read-only | T6.1-T6.5 | All | [FILL] |                       
  qa7_1_legacy_files.txt |                                                            
  | No legacy code references | T6.6 | All | [FILL] | qa7_1_legacy_files.txt |        
  | SERVICE-CATALOG updated | T6.7 | — | [FILL] | qa7_2_catalog.txt |                 
  | CHANGES.md entry | T6.10 | — | [FILL] | qa7_3_changes.txt |                       
                                                                                      
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED.                                       
  GATE6                                                                               
  ```                                                                             
                                                                                      
  **>>> /compact checkpoint after Gate 6 <<<**                                        
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 10: RT GATES (Red-Team Verification)                                     
                                                                                      
  **These gates run AFTER all phase verifications. They test cross-cutting            
  concerns.**                                                                         
                                                                                      
  ### RT-CORRELATION: Trace Linkage                                                   
                                                                                      
  ```bash                                                                             
  echo "=== RT-CORRELATION ===" | tee "$EVIDENCE_DIR/phase6/rt_correlation.txt"       
                                                                                      
  # Send a request with correlation_id, trace through all services                    
  TEST_CORR="rt-corr-$(date +%s)"                                                     
  curl $CURL_TIMEOUT -s http://localhost:8091/api/deals \                             
    -H "X-API-Key: $ZAKOPS_API_KEY" \                                                 
    -H "X-Correlation-ID: $TEST_CORR" 2>&1 \                                          
    | tee -a "$EVIDENCE_DIR/phase6/rt_correlation.txt"                                
                                                                                      
  # Check backend logs for correlation_id                                             
  echo "--- Backend logs ---" >> "$EVIDENCE_DIR/phase6/rt_correlation.txt"            
  cd "$BACKEND_REPO" && docker compose logs --tail=50 2>&1 | grep "$TEST_CORR" \      
    | tee -a "$EVIDENCE_DIR/phase6/rt_correlation.txt"                                
  ```                                                                                 
                                                                                      
  ### RT-ERROR-REDACT: Error Redaction                                                
                                                                                      
  ```bash                                                                             
  echo "=== RT-ERROR-REDACT ===" | tee "$EVIDENCE_DIR/phase6/rt_error_redact.txt"     
                                                                                      
  # Trigger an error, check no secrets in response                                    
  curl $CURL_TIMEOUT -s http://localhost:8091/api/deals/NONEXISTENT-DEAL \            
    -H "X-API-Key: $ZAKOPS_API_KEY" 2>&1 \                                            
    | tee -a "$EVIDENCE_DIR/phase6/rt_error_redact.txt"                               
                                                                                      
  # Check for secret patterns in error response                                       
  curl $CURL_TIMEOUT -s http://localhost:8095/agent/invoke \                          
    -H "X-Service-Token: WRONG-TOKEN" \                                               
    -H "Content-Type: application/json" \                                             
    -d '{"message":"test"}' 2>&1 \                                                    
    | tee -a "$EVIDENCE_DIR/phase6/rt_error_redact.txt"                               
                                                                                      
  # FAIL if: Stack traces, API keys, DB connection strings in responses               
  ```                                                                                 
                                                                                      
  ### RT-AUTH: Authentication Enforcement                                             
                                                                                      
  ```bash                                                                             
  echo "=== RT-AUTH ===" | tee "$EVIDENCE_DIR/phase6/rt_auth.txt"                     
                                                                                      
  # No API key → should fail                                                          
  echo "--- No API key ---" >> "$EVIDENCE_DIR/phase6/rt_auth.txt"                     
  curl $CURL_TIMEOUT -s -X POST http://localhost:8091/api/deals \                     
    -H "Content-Type: application/json" \                                             
    -d '{"canonical_name":"no-auth"}' -w "\nHTTP: %{http_code}\n" 2>&1 \              
    | tee -a "$EDENCE_DIR/phase6/rt_auth.txt"                                       
                                                                                      
  # Wrong service token → should fail                                                 
  echo "--- Wrong token ---" >> "$EVIDENCE_DIR/phase6/rt_auth.txt"                    
  curl $CURL_TIMEOUT -s http://localhost:8095/agent/invoke \                          
    -H "X-Service-Token: WRONG" \                                                     
    -HContent-Type: application/json" \                                             
    -d '{"message":"test"}' -w "\nHTTP: %{http_code}\n" 2>&1 \                        
    | tee -a "$EVIDENCE_DIR/phase6/rt_auth.txt"                                       
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 11: ADVERSARIAL QA PASS                                                  
                                                                                      
  ### QA Pass #2: Adversarial Tests                                                   
                                                                                      
  ```bash                                                                             
  echo "=== ADVERSARIAL QA ===" | tee "$EVIDENCE_DIR/phase6/adversarial.txt"          
                                                                                      
  # TEST 1: Invalid stage transition                                                  
  echo "--- Invalid stage ---" >> "$EVIDENCE_DIR/phase6/adversarial.txt"              
  DEAL_ID=$($BACKEND_DB_CMD -t -c "SELECT deal_id FROM deals LIMIT 1;" 2>&1 | tr      
  -d ' \n')                                                                           
  curl $CURL_TIMEOUT -s -X POST                                                       
  "http://localhost:8091/api/deals/$DEAL_ID/transition" \                             
    -H "Content-Type: application/json" \                                             
    -H "X-API-Key: $ZAKOPS_API_KEY" \                                                 
    -d '{"to_stage":"bogus_stage"}' 2>&1 \                                            
    | tee -a "$EVIDENCE_DIR/phase6/adversarial.txt"                                   
  # Expected: 400 Bad Request                                                         
                                                                                      
  # TEST 2: Agent with backend down (informational — don't actually stop backend)     
  echo "--- Agent error handling ---" >> "$EVIDENCE_DIR/phase6/adversarial.txt"       
  # Check agent tool code has error handling for HTTP failures                        
  rg -n "except\|try\|error\|HTTPError\|stas_code"                                  
  "$AGENT_API_DIR/app/core/langgraph/tools/" --type py 2>&1 \                         
    | head -20 | tee -a "$EVIDENCE_DIR/phase6/adversarial.txt"                        
                                                                                      
  # TEST 3: DELETE trigger on audit_log                                               
  echo "--- DELETE trigger ---" >> "$EVIDENCE_DIR/phase6/adversarial.txt"             
  $AGENT_DB_CMD -c "SELECT trigger_name FROM information_schema.triggers WHERE        
  event_object_table = 'audit_log';" 2>&1 \                                           
    | tee -a "$EVIDENCE_DIR/phase6/adversarial.txt"                                   
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 12: FULL COVERAGE MATRIX (All 22 ZK-ISSUE-*)                             
                                                                                      
  ```bash                                                                             
  echo "=== COVERAGE MATRIX ===" | tee "$QA_DIR/matrices/coverage_matrix.md"          
                                                                                      
  cat << 'MATRIX' >> "$QA_DIR/matrices/coverage_matrix.md"                            
  # NO-DROP COVERAGE MATRIX — QA-VERIFICATION-006                                     
                                                                                      
  Every issue from V2 MUST be addressed. No blanks allowed.                           
                                                                                      
  | Issue ID | Title | Sev | Phase | QA Check | Verdict | Evidence | Action |         
  |--------|-------|-----|-------|----------|---------|----------|--------|         
  | ZK-ISSUE-0001 | Split-brain persistence | P0 | 1 | QA-2.1–2.5 | [FILL] |          
  phase2/ | [FILL] |                                                                  
  | ZK-ISSUE-0002 | Email ingestion disabled | P0 | 4 | QA-5.1 | [FILL] | phase5/     
   | [FILL] |                                                                         
  | ZK-ISSUE-0003 | Quarantine no deal creation | P1 | 2 | QA-3.1 | [FILL] |        
  phase3/ | [FILL] |                                                                  
  | ZK-ISSUE-0004 | No DataRoom folders | P1 | 2 | QA-3.2 | [FILL] | phase3/ |        
  [FILL] |                                                                            
  | ZK-ISSUE-0005 | Dashboard no auth | P1 | 5 | QA-6.1 | [FILL] | phase6/ |          
  [FILL] |                                                                            
  | ZK-ISSUE-0006 | Wrong quarantine endpoint | P1 | 0 | QA-1.1 | [FILL] |            
  phase1/ | [FILL] |                                                                  
  | ZK-ISSUE-0007 | Stage taxonomy conflicts | P1 | 0 | QA-1.3 | [FILL] | phase1/     
   | [FILL] |                                                                         
  | ZK-ISSUE-0008 | Actions split PG/SQLite | P1 | 1 | QA-2.4 | [FILL] | phase2/      
  | [FILL] |                                                                          
  | ZK-ISSUE-0009 | Agent no create_deal | P2 | 3 | QA-4.1 | [FILL] | phase4/ |       
  [FILL] |                                                                            
  | ZK-ISSUE-0010 | RAG unverified | P2 | 0,4 | QA-1.5, QA-5.4 | [FILL] |             
  phase1/,phase5/ | [FILL] |                                                          
  | ZK-ISSUE-0011 | No event correlation | P2 | 0 | QA-1.4, QA-4.2 | [FILL] |         
  phase1/,phase4/ | [FILL] |                                                          
  | ZK-ISSUE-0012 | Notes endpoint mismatch | P2 | 0 | QA-1.2 | [FILL] | phase1/      
  | [FILL] |                                                                          
  | ZK-ISSUE-0013 | Capabilities/metrics 501 | P2 | 2 | QA-3.3 | [FILL] | phase3/     
   | [FILL] |                                                                         
  | ZK-ISSUE-0014 | sys.path hack | P2 | 1 | QA-2.3 | [FILL] | phase2/ | [FILL] |     
  | ZK-ISSUE-0015 | Approval expiry lazy | P3 | 3 | QA-4.4 | [FILL] | phase4/ |       
  [FILL] |                                                                            
  | ZK-ISSUE-0016 | No duplicate detection | P2 | 3 | QA-4.3 | [FILL] | phase4/ |     
   [FILL] |                                                                           
  | ZK-ISSUE-0017 | No retention policy | P3 | 5 | QA-6.2 | [FILL] | phase6/ |        
  [FILL] |                                                                            
  | ZK-ISSUE-0018 | Zod schema mismatch | P2 | 0 | QA-1.7 | [FILL] | phase1/ |        
  [FILL] |                                                                            
  | ZK-ISSUE-0019 | Executors unwired | P2 | 4 | QA-5.3 | [FILL] | phase5/ |          
  [FILL] |                                                                            
  | ZK-ISSUE-0020 | SSE not implemented | P2 | 4 | QA-5.5 | [FILL] | phase5/ |        
  [FILL] |                                                                            
  | ZK-ISSUE-0021 | No scheduling/reminders | P2 | 4 | QA-5.6 | [FILL] | phase5/      
  | [FILL] |                                                                          
  | ZK-ISSUE-0022 | Archive/restore missing | P3 | 2 | QA-3.4 | [FILL] | phase3/      
  | [FILL] |                                                                          
                                                                                      
  **Action Column Legend:**                                                           
  - PASS = Already implemented correctly                                              
  - REMEDIATED = Fixed during this QA session                                         
  - DEFERRED = Cannot fix now (with proven justification)                             
  - BLOCKED = Attempted fix, still broken (with documented blocker)                   
                                                                                      
  HARD RULE: ALL [FILL] CELLS MUST BE REPLACED. NO BLANKS.                            
  MATRIX                                                                              
  ```                                                                                 
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 13: OUTPUT FORMAT                                                        
                                                                                      
  ```markdown                                                                         
  # QA VERIFICATION 006 + REMEDIATION — REPORT                                        
                                                                                      
  **Date:** [timestamp]                                                               
  **Auditor:** Claude Code (Opus 4.5)                                                 
  **Target:** DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL                              
  **Mode:** Verify-Fix-Reverify                                                       
                                                                                      
  ## Executive Summary                                                                
  **VERDICT:** [PASS / PARTIAL / FAIL]                                                
  **Tasks Verified:** [X]/69                                                          
  **Tasks Remediated:** [X] (fixed during session)                                    
  **Tasks Deferred:** [X] (with justification)                                        
  **Tasks Blocked:** [X] (with documented blockers)                                   
  **P0 Issues (ZK-0001, ZK-0002):** [PASS/FAIL]                                       
  **P1 Issues (6 total):** [X/6 PASS]                                                 
  **P2 Issues (11 total):** [X/11 PASS]                                               
  **P3 Issues (3 total):** [X/3 PASS]                                                 
                                                                                      
  ## Gate Results                                                                     
  | Gate | Phase | Status | Remediation Required? |                                   
  |------|-------|--------|-----------------------|                                   
  | Gate 0 | Phase 0 (Stop Bleeding) | [FILL] | [FILL] |                              
  | Gate 1 | Phase 1 (Split-Brain) | [FILL] | [FILL] |                                
  | Gate 2 | Phase 2 (Contracts) | [FILL] | [FILL] |                                  
  | Gate 3 | Phase 3 (Lifecycle) | [FILL] | [FILL] |                                  
  | Gate 4 | Phase 4 (Knowledge) | [FILL] | [FILL] |                                  
  | Gate 5 | Phase 5 (Hardening) | [FILL] | [FILL] |                                  
  | Gate 6 | Phase 6 (Decommission) | [FILL] | [FILL] |                               
                                                                                      
  ## RT Gate Results                                                                  
  | Gate | Status |                                                                   
  |------|--------|                                                                   
  | RT-DB-SOT | [FILL] |                                                              
  | RT-CORRELATION | [FILL] |                                                         
  | RT-ERROR-REDACT | [FILL] |                                                        
  | RT-AUTH | [FILL] |                                                                
                                                                                      
  ## Remediation Log                                                                  
  [Full remediation log from REMEDIATION_LOG.md]                                      
                                                                                      
  ## Coverage Matrix                                                                  
  [Full 22-issue matrix from Section 12 — NO BLANKS]                                  
                                                                                      
  ## Evidence Directory                                                               
  [List of all evidence files with sizes]                                             
  ```                                                                               
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 14: GATES SUMMARY                                                        
                                                                                      
  | Gate | Phase | Requirement | Hard Stop? |                                         
  |------|-------|------------|-----------|                                           
  | QA-0 | Infrastructure | Services healthy, DBs accessible, RT-DB-SOT |             
  **ABSOLUTE** |                                                                      
  | QA-1 | Phase 0 | Endpoints fixed, stages canonical, correlation wired | YES |     
  | QA-2 | Phase 1 | Postgres sole SOT, no sys.path, JSON read-only |                 
  **ABSOLUTE** (P0) |                                                                 
  | QA-3 | Phase 2 | Quarantine→deal, capabilities/metrics, archive/restore | YES     
   |                                                                                  
  | QA-4 | Phase 3 | Agent tools, duplicate detection, approval expiry | YES |        
  | QA-5 | Phase 4 | Email ingestion, executors, RAG columns | YES (P0) |             
  | QA-6 | Phase 5 | Auth, retention, tracing | NO (may defer) |                      
  | QA-7 | Phase 6 | Legacy decommission, no reference docs updated | YES |         
  | RT-* | Cross-cutting | Correlation, error redaction, auth enforcement | YES |     
                                                                                      
  ---                                                                                 
                                                                                      
  ## SECTION 15: EXECUTION GUIDANCE                                                   
                                                                                      
  ### Sequencing                                                                      
                                                                                      
  1. Set up evidence directory (Section 1.5) — **ALWAYS FIRST**                       
  2. QA Phase 0 (Infrastructure) → GATE QA-0                                          
  3. QA Phase 1 (Phase 0 tasks) → GATE QA-1 → `/compact`                              
  4. QA Phase 2 (Phase 1 tasTE QA-2                                           
  5. QA Phase 3 (Phase 2 tasks) → GATE QA-3 → `/compact`                              
  6. QA Phase 4 (Phase 3 tasks) → GATE QA-4                                           
  7. QA Phase 5 (Phase 4 tasks) → GATE QA-5 → `/compact`                              
  8. QA Phase 6 (Phase 5 tasks) → GATE QA-6                                           
  9. QA Phase 7 (Phase 6 tasks) → GATE QA-7 → `/compact`                              
  10. RT Gates (Section 10)                                                           
  11. Adversarial QA (Section 11)                                                     
  12. Coverage Matrix (Section 12) — **ALL CELLS FILLED**                             
  13. Final Report (Section 13)                                                       
                                                                                      
  ### Verdict Rules                                                                                                                                                        
  - **PASS:** ALL ABSOLUTE gates pass. ALL P0 issues resolved. Coverage matrix        
  complete. ≥80% of tasks PASS or REMEDIATED.                                         
  - **PARTIAL:** ABSOLUTE gates pass. P0 issues resolved. Some P2/P3 tasks            
  DEFERRED with justification. ≥60% of tasks PASS or REMEDIATED.                      
  - **FAIL:** ANY ABSOLUTE gate fails. ANY P0 issue unresolved. Coverage ix       
  has blanks.                                                                         
                                                                                      
  ### Non-Negotiable Rules                                                            
                                                                                      
  1. Run YOUR OWN commands. Never trust Builder's evidence alone.                     
  2. Every claim needs YOUR independent verification.                                 
  3. Empty evidence = not verified = FAIL.                                            
  4. **ALL curl commands MUST have --max-time and --connect-timeout                   
  (RT-TIMEOUT).**                                                                     
  5. **ALL coverage matrix cells MUST be filled (NO BLANKS).**                        
  6. **RT-DB-SOT is ABSOLUTE — split-brain proof, not "likely ok".**                  
  7. **Remediation MUST produce before/after evidence.*                             
  8. **Re-verify after EVERY remediation with the SAME test that failed.**            
  9. **DEFERRED items need PROVEN justification (not "we'll do it later").**          
  10. **P0 issues (ZK-0001, ZK-0002) are NON-NEGOTIABLE — must be PASS or             
  REMEDIATED.**                                                                       
  11. Redact tokens in evidence (first 8 chars only).                                 
  12. **NO ENDING SESSION WHILE TESTS ARE RED*                                      
  13. Use `/compact` at designated checkpoint points.                                 
  14. Save progress to PROGRESS_CHECKPOINT.md before each /compact.                   
                                                                                      
  ---                                                                                 
                                                                                      
  *End of QA VERIFICATION 006 + REMEDIATION*                                          
  *Codename: QA-VERIFICATION-006*                                                     
  *Version: V1 (Verify-Fix-Reverify Edition)*                                         
  *7 QA phases | 7+ gates | 22 issues | 69 tasks | RT gates*                          
  *Mode: AUDIT + REMEDIATION (not audit-only)*                                        
  *Source: DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL*                                  
  *HARD RULES: NO BLANKS | NO HANGING TESTS | NO ENDING WHILE RED | REMEDIATE ON      
  FAIL*                                                                               
  *P0 ISSUES: ZK-0001 (split-brain) and ZK-0002 (email ingestion) are                 
  NON-NEGOTIABLE* and this Claude — GPT here. I reviewed the two Deal Lifecycle       
  QA/remediation docs (V3 FINAL plan + the QA Verification+Remediation execution      
  doc). They’re strong on policy decisions (Postgres SOT, JSON deprecated, SQLite     
   dedup-only                                                                     
                                                                                      
  DEAL_LIFECYCLE_REMEDIATION_PLAN…                                                    
                                                                                      
   and they do include canary-style gates (e.g., JSON hash unchanged after            
  creating a deal)                                                                    
                                                                                    
  QA VERIFICATION + REMEDIATION_ …                                                    
                                                                                      
  .                                                                                   
                                                                                      
  Red-team concern: too many checks can be satisfied by “code exists” (rg/grep  
  without proving “behavior works end-to-end in the dashboard with real state         
  transitions.” We need a post-execution follow-up QA that is behavioral,             
  UI-driven, and chaos-oriented, with evidence artifacts and hard fail rules.         
                                                                                      
  Please update the QA audit doc by adding a Post-QA Follow-Up Pack (run after        
  the existing gates pass). Requirements:                                         
                                                                                      
  A) “Truth-by-Execution” E2E (UI + API + DB) — no greps allowed                      
                                                                                      
  Add a new section that must perform these live steps and store evidence:            
                                                                                      
  Hard reset to zero-data (lab clean slate)                                     
                                                                                      
  Add scripts/reset_lab_data.sh (or equivalent) that:                                 
                                                                                      
  truncates the deal tables + quarantine tables in Postgres (transactional)           
                                                                                      
  clears derived artifacts (DataRoom deal folders) safely (only under known root)     
                                                                                      
  clears RAG index / vector store entries if present (or documents why not)           
                                                                                      
  clears Redis keys used for SSE/outbox dedup if applicable                           
                                                                                      
  Evidence: before/after row counts for deals, deal_events, quarantine_items,         
  plus filesystem listing proof.                                                      
                                                                                      
  Email → Quarantine → Approval → Deal → Folder scaffolding                           
                                                                                      
  Run the ingestion path for one real email (or a controlled fixture email that       
  flows through the same p.                                                   
                                                                                      
  Verify:                                                                             
                                                                                      
  row appears in quarantine_items                                                     
                                                                                      
  approving it produces exactly one deal (idempotent)                                 
                                                                                      
  DataRoom folder scaffolding exists for that deal (derived artifact)                 
                                                                                      
  Evidence: curl outputs + SQL query outputs + folder tree output.                    
  (Your plan already states Gate 4 expects this end-to-end behavior                   
                                                                                      
  DEAL_LIFECYCLE_REMEDIATION_PLAN…                                                    
                                                                                      
   — now force it as a real execution gate, not aspirational.)                        
                                                                                      
  Dashboard verification                                                              
                                                                                  
  In the dashboard:                                                                   
                                                                                      
  Quarantine item appears                                                             
                                                                                      
  Approve action succeeds                                                             
                                                                                      
  Deal shows up immediately (SSE or intentional polling)                              
                                                                                      
  Deal page loads without 404s, missing fields, or console errors                     
                                                                                      
  Evidence: screenshots + browser console export + network HAR (or playwright         
  trace if you have it).                                                              
                                                                                      
  Hard rule: if the system only “passes via API” but the dashboard can’t complete     
   the workflow, this follow-up gate FAILS.                                           
                                                                                      
  B) Anti-False-Positive Gates (kill the “tests passep broken” class)         
                                                                                      
  Add these explicit tests:                                                           
                                                                                      
  Endpoint realism sweep (dashboard-used endpoints only)                              
                                                                                      
  Enumerate the actual dashboard routes/hooks andap to backend endpoints            
  (network capture).                                                                  
                                                                                      
  For each endpoint: prove it returns non-mock, non-empty, schema-correct data        
  under at least one real record.                                                     
                                                                                      
  Fail if any dashboard feature calls:                                                
                                                                                      
  nonexistent endpoint                                                                
                                                                                      
  placeholder route                                                                   
                                                                                      
  “200 []” when there is kndata                                                   
                                                                                      
  silently swallowed error (frontend renders empty state with console errors)         
                                                                                      
  Schema-drift breaker                                                                
                                                                                      
  Generate client from OpenAPI and force TypeScript build.                            
                                                                                      
  Then run a runtime schema check for at least one payload (Zod) and require a        
  sample “schema mismatch logged” event (not silent).                                 
  (The plan already calls for schema mismatch logging evidence in places              
                                                                                      
  DEAL_CYCLE_REMEDIATION_PLAN…                                                    
                                                                                      
   — make it a mandatory “prove it happened once” check.)                             
                                                                                      
  C) Split-Brain & “Wrong DB” proof (make it impossible to regress)                   
                                                                             Even if you already have DB-SOT canaries                                            
                                                                                      
  QA VERIFICATION + REMEDIATION_ …                                                    
                                                                                      
  , add a one-command proof:                                                          
                                                                                    
  For each service (backend, outbox-worker, agent-api if involved), output:           
                                                                                      
  DB host                                                                             
                                                                                      
  DB name                                                                             
                                                                                      
  SELECT current_database(), current_schema(), inet_server_addr(),                    
  inet_server_port();                                                                 
                                                                                      
  Fail if any service points at an unexpected Postgres container/volume.              
                                                                                      
  If stale containers exist, require either:                                          
                                                                                      
  removal in dev compose, or                                                          
                                                                                      
  explicit renaming/labeling + documentation to prevent confusion.                    
                                                                                      
  This is the “worked, but on the wrong databa” nightmare class.                    
                                                                                      
  D) Outbox + SSE reliability (behavior under restart)                                
                                                                                      
  Add a chaos gate that does real work, then restarts components:                     
                                                                                      
  Create quarantine item + approve i                                                
                                                                                      
  While processing, restart outbox-worker.                                            
                                                                                      
  Confirm:                                                                            
                                                                                      
  no duplicate deal                                                                   
                                                                                      
  no stuck approval                                                                   
                                                                                      
  SSE reconnects or polling behavior is documented as intentional                     
                                                                                      
  eventual consistency window measured (time-to-visible in dashboard)                 
                                                                                      
  Evidence: timestamps + logs.                                                        
                                                                                      
  E) Observability you can actually use during lab testing                            
                                                                                      
  Add a “follow logs by correlation_id” requirement:                                  
                                                                                      
  Provide scripts/tail_all.sh to tail docker logs for backend/outbox/agent with       
  prefixes.                                                                           
                                                                                      
  Require that one end-to-end run emits the same correlation_id across services   
  (or clearly states the propagation boundary).                                       
                                                                                      
  Evidence: saved log excerpts filtered by the correlation_id.                        
                                                                                      
  F) Security sanity (minimal but real)                                               
                                                                                      
  Even in lab:                                                                        
                                                                                      
  Prove unauthenticated calls fail where expected (401/403) for sensitive             
  actions.                                                                            
                                                                                      
  Prove API-key/JWT behavior matches current security model.                          
                                                                                      
  Evidence: curl “no-auth → 401” + “auth → 200”.                                      
                                                                                      
  Output formatting / execution rules                                                 
                                                                                      
  Add a new “POST-QA FOLLOW-UP REPORT” section that mirrors your other reports:       
                                                                                      
  checklist, pass/fail, evidence paths                                                
                                                                                      
  no skipped items unless explicitly justified (and then labeled “DEFERRED” with      
  rationale)                                                                          
                                                                                  
  Hard fail if:                                                                       
                                                                                      
  any follow-up step hangs > N minutes without diagnosis                              
                                                                                      
  any evidence file missing                                                           
                                                                                      
  dashboard can’t complete the email→quarantine→deal workflow end-to-end combine      
  and  here's the original plan                                                       
  /home/zaks/bookkeeping/docs/DEAL_LIFECYCLE_REMEDIATION_PLAN_V3_FINAL.md             
                                                                                      
