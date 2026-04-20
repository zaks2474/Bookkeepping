# LinkedIn MCP Server Implementation Plan

**Date:** 2025-12-04
**Purpose:** Integrate LinkedIn MCP server for AI-assisted job searching, profile research, and company analysis
**Status:** Ready for implementation

---

## Overview

Implement stickerdaniel/linkedin-mcp-server to enable Claude Code and other AI assistants to:
- Search and analyze LinkedIn job postings
- Research candidate profiles and companies
- Get personalized job recommendations
- Retrieve detailed job information

**Note:** Direct job application not supported; use with mcp-browser-use for form automation if needed.

---

## Prerequisites

- [ ] Docker installed and running
- [ ] LinkedIn account with active session
- [ ] LinkedIn authentication cookie (`li_at` value)
- [ ] Port 8030 available (or choose alternative)
- [ ] `/home/zaks/Zaks-llm` docker-compose stack accessible

---

## Step 1: Obtain LinkedIn Cookie

### Method A: Chrome DevTools (Recommended)
1. Log into linkedin.com in Chrome
2. Press F12 → Application tab → Storage → Cookies → linkedin.com
3. Find `li_at` cookie and copy its value
4. Save securely (expires in ~30 days)

### Method B: Automated Docker
```bash
docker run -it --rm stickerdaniel/linkedin-mcp-server:latest --get-cookie
```

**Security Note:** Store cookie in `.env` file (already git-ignored)

---

## Step 2: Add to Docker Compose Stack

**File:** `/home/zaks/Zaks-llm/docker-compose.yml`

Add this service:

```yaml
  linkedin-mcp:
    image: stickerdaniel/linkedin-mcp-server:latest
    container_name: linkedin-mcp
    ports:
      - "8030:8000"
    environment:
      - LINKEDIN_COOKIE=${LINKEDIN_COOKIE}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs/linkedin-mcp:/app/logs
    networks:
      - ai-network
    restart: unless-stopped
```

**Location:** Add after `mcp-browser-use` service (around line 226)

---

## Step 3: Configure Environment Variables

**File:** `/home/zaks/Zaks-llm/.env`

Add:
```bash
# LinkedIn MCP Server
LINKEDIN_COOKIE=li_at=${LINKEDIN_COOKIE}
```

**Important:** Replace `YOUR_COOKIE_VALUE_HERE` with actual cookie from Step 1

---

## Step 4: Create Log Directory

```bash
mkdir -p /home/zaks/Zaks-llm/logs/linkedin-mcp
```

---

## Step 5: Start LinkedIn MCP Service

```bash
cd /home/zaks/Zaks-llm
docker compose up -d linkedin-mcp
```

**Verify:**
```bash
docker ps | grep linkedin-mcp
docker logs linkedin-mcp --tail 20
```

**Expected:** Container running, no authentication errors in logs

---

## Step 6: Configure Claude Code MCP Integration

**File:** `/root/.config/Claude/claude_desktop_config.json`

Add to `mcpServers` section:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network", "host",
        "-e", "LINKEDIN_COOKIE",
        "stickerdaniel/linkedin-mcp-server:latest"
      ],
      "env": {
        "LINKEDIN_COOKIE": "li_at=${LINKEDIN_COOKIE}"
      }
    },
    "existing-servers": "..."
  }
}
```

**Alternative:** Point to running container via HTTP (if MCP supports remote servers):
```json
{
  "mcpServers": {
    "linkedin": {
      "url": "http://localhost:8030"
    }
  }
}
```

---

## Step 7: Restart Claude Code Service

```bash
sudo systemctl restart claude-code-api
sudo systemctl status claude-code-api
journalctl -u claude-code-api --tail 50
```

**Verify:** No MCP connection errors, LinkedIn server listed in capabilities

---

## Step 8: Test Integration

Ask Claude Code:
1. "What are my recommended jobs on LinkedIn?"
2. "Search for Python developer jobs in San Francisco"
3. "Analyze this LinkedIn profile: [URL]"
4. "Research this company: [LinkedIn company URL]"

**Expected:** Claude accesses LinkedIn data and returns results

---

## Step 9: Update Documentation

### A. Service Catalog

**File:** `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md`

Add after `mcp-browser-use` section:

```markdown
## LinkedIn MCP Server
- Purpose: LinkedIn API integration for job search, profile research, company analysis
- Port/URL: http://localhost:8030
- Start/stop: `cd /home/zaks/Zaks-llm && docker compose up -d linkedin-mcp` / `docker compose restart linkedin-mcp`
- Status: `docker logs linkedin-mcp`
- Config: `.env` (LINKEDIN_COOKIE, expires ~30 days)
- Data: `./logs/linkedin-mcp`
- Logs: `docker logs linkedin-mcp` or `tail -f /home/zaks/Zaks-llm/logs/linkedin-mcp/*.log`
- Notes: Cookie requires renewal every 30 days; only one active session per cookie; check mobile for 2FA prompts
```

### B. Change Log

**File:** `/home/zaks/bookkeeping/CHANGES.md`

Add entry:
```markdown
- 2025-12-04: Implemented LinkedIn MCP server (stickerdaniel/linkedin-mcp-server) on port 8030; added to Zaks-llm docker-compose stack; integrated with Claude Code for job searching, profile research, and company analysis; cookie auth configured in .env (30-day expiry).
```

### C. Health Check Script

**File:** `/home/zaks/bookkeeping/scripts/health.sh`

Add health check:
```bash
# LinkedIn MCP
echo -n "LinkedIn MCP (8030): "
if curl -s --connect-timeout 3 http://localhost:8030/health > /dev/null 2>&1; then
  echo -e "${GREEN}OK${NC}"
else
  echo -e "${RED}FAIL${NC}"
fi
```

---

## Step 10: Run Snapshot and Verify

```bash
cd /home/zaks/bookkeeping
make snapshot
make health
git add .
git commit -m "Add LinkedIn MCP server implementation"
```

---

## Available Tools After Implementation

### 1. get_person_profile
**Purpose:** Extract LinkedIn profile data
**Usage:** "Research this candidate: https://www.linkedin.com/in/username/"
**Returns:** Work history, education, skills, connections

### 2. get_company_profile
**Purpose:** Retrieve company information
**Usage:** "Analyze company: https://www.linkedin.com/company/name/"
**Returns:** Size, industry, locations, description

### 3. search_jobs
**Purpose:** Find jobs by keywords and location
**Usage:** "Find Python jobs in San Francisco"
**Returns:** List of matching job postings

### 4. get_recommended_jobs
**Purpose:** Get personalized job recommendations
**Usage:** "What jobs are recommended for me?"
**Returns:** Jobs based on your LinkedIn profile

### 5. get_job_details
**Purpose:** Detailed job posting information
**Usage:** "Analyze job: https://www.linkedin.com/jobs/view/123456/"
**Returns:** Full description, requirements, company info

### 6. close_session
**Purpose:** Properly terminate browser session
**Usage:** Automatic or "Close LinkedIn session"

---

## Troubleshooting

### Cookie Expired
**Symptom:** Authentication errors in logs
**Solution:**
```bash
docker run -it --rm stickerdaniel/linkedin-mcp-server:latest --get-cookie
# Update LINKEDIN_COOKIE in .env
docker compose restart linkedin-mcp
```

### Container Not Starting
**Check:**
```bash
docker ps -a | grep linkedin-mcp
docker logs linkedin-mcp
```
**Common issues:**
- Port 8030 already in use: Change port in docker-compose.yml
- Invalid cookie: Re-obtain from browser
- Network issues: Check `docker network ls | grep ai-network`

### LinkedIn Blocking Access
**Symptoms:** 429 errors, captcha requests
**Solutions:**
- Wait 5-10 minutes between heavy operations
- Check mobile app for 2FA confirmation prompt
- Ensure only one session active per cookie
- Consider using `--no-headless` mode for debugging

### Claude Not Seeing LinkedIn Tools
**Check:**
1. MCP config file syntax valid (JSON lint)
2. Claude service restarted after config change
3. Cookie value correctly copied (no extra spaces)
4. Docker container running: `docker ps | grep linkedin-mcp`

---

## Maintenance

### Cookie Renewal (Every 30 Days)
1. Re-obtain cookie using Step 1 method
2. Update `.env` file
3. Restart service: `docker compose restart linkedin-mcp`

### Log Rotation
```bash
# Check log size
du -sh /home/zaks/Zaks-llm/logs/linkedin-mcp

# Clear old logs if needed
rm /home/zaks/Zaks-llm/logs/linkedin-mcp/*.log.old
```

### Updates
```bash
# Pull latest image
docker pull stickerdaniel/linkedin-mcp-server:latest

# Restart with new image
cd /home/zaks/Zaks-llm
docker compose up -d linkedin-mcp
```

---

## Future Enhancements

### Option A: Job Application Automation
Combine LinkedIn MCP with mcp-browser-use:
1. LinkedIn MCP finds jobs
2. Claude analyzes fit
3. mcp-browser-use fills application forms

### Option B: Integration with OpenWebUI
Configure OpenWebUI models to access LinkedIn MCP for research tasks

### Option C: Scheduled Job Monitoring
Create cron job to:
- Check recommended jobs daily
- Alert on new postings matching criteria
- Track application status

---

## Security Considerations

1. **Cookie Storage:** Stored in `.env` (git-ignored), expires automatically
2. **Rate Limiting:** LinkedIn may throttle; avoid excessive requests
3. **Terms of Service:** Use for personal research only; review LinkedIn ToS
4. **Data Privacy:** Profile data accessed stays local; not shared externally
5. **Session Management:** Only one active session per cookie allowed

---

## References

- GitHub: https://github.com/stickerdaniel/linkedin-mcp-server
- MCP Docs: https://docs.anthropic.com/en/docs/claude-code/mcp
- Service Catalog: `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md`
- Docker Compose: `/home/zaks/Zaks-llm/docker-compose.yml`

---

## Implementation Checklist

- [ ] Obtain LinkedIn cookie
- [ ] Add service to docker-compose.yml
- [ ] Configure .env file
- [ ] Create log directory
- [ ] Start LinkedIn MCP service
- [ ] Verify container running
- [ ] Configure Claude MCP config
- [ ] Restart Claude service
- [ ] Test integration with queries
- [ ] Update SERVICE-CATALOG.md
- [ ] Update CHANGES.md
- [ ] Add health check to scripts/health.sh
- [ ] Run snapshot
- [ ] Commit changes

**Estimated Time:** 15-20 minutes
**Difficulty:** Medium (requires cookie extraction and config editing)

---

**End of Implementation Plan**
