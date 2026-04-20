# SharePoint DataRoom Sync Guide

**Created:** December 7, 2025
**Purpose:** Sync local DataRoom to SharePoint ZakOpsDataRoom site
**Script:** `/home/zaks/Zaks-llm/scripts/sharepoint_sync.py`

---

## Overview

Automatically sync your DataRoom, Implementation Plans, and Deal Origination Engine docs to SharePoint for:
- Cloud backup and disaster recovery
- Access from anywhere (mobile, web, desktop)
- Version history and collaboration
- Professional presentation for advisors/partners

**Target Site:** https://zaks24.sharepoint.com/sites/ZakOpsDataRoom

---

## Quick Start (5 Minutes)

### Step 1: Configure Credentials

```bash
cd /home/zaks/Zaks-llm
cp .env.sharepoint.example .env.sharepoint
nano .env.sharepoint
```

**Fill in your Microsoft 365 credentials:**
```bash
SHAREPOINT_AUTH_METHOD=user
SHAREPOINT_USERNAME=zaks373631@gmail.com
SHAREPOINT_PASSWORD=your_actual_password
```

### Step 2: Run Sync

```bash
source venv/bin/activate
python scripts/sharepoint_sync.py
```

### Step 3: Verify

Visit: https://zaks24.sharepoint.com/sites/ZakOpsDataRoom/Shared%20Documents

You should see:
```
Shared Documents/
├── DataRoom/
│   ├── OPERATOR-BIO.md
│   ├── MASTER-DASHBOARD.md
│   ├── 00-PIPELINE/
│   ├── 01-ACTIVE-DEALS/
│   └── ...
├── Implementation-Plans/
│   ├── LINKEDIN-MCP-IMPLEMENTATION.md
│   ├── AUTOMATED-JOB-APPLICATION-WORKFLOW.md
│   └── ...
└── Deal-Origination-Engine/
    ├── DEAL-ORIGINATION-ENGINE-ARCHITECTURE.md
    ├── DEAL-ORIGINATION-ENGINE-IMPLEMENTATION.md
    ├── DEAL-ORIGINATION-ENGINE-SUMMARY.md
    └── DEAL-ORIGINATION-PLAYBOOK.md
```

---

## What Gets Synced

### DataRoom Structure
- **Source:** `/home/zaks/DataRoom/`
- **Target:** `Shared Documents/DataRoom/`
- **Contents:** All folders, documents, deal files, templates

### Implementation Plans
- **Source:** `/home/zaks/bookkeeping/docs/`
- **Target:** `Shared Documents/Implementation-Plans/`
- **Contents:** LinkedIn MCP, Job Application Workflow, SharePoint guide

### Deal Origination Engine
- **Target:** `Shared Documents/Deal-Origination-Engine/`
- **Contents:** Architecture, Implementation, Playbook, Summary

### Excluded Files
- `.git`, `__pycache__`, `*.pyc` (code artifacts)
- `.env`, `*.log` (secrets and logs)
- `.DS_Store`, `node_modules` (system files)

---

## Authentication Options

### Option 1: User Authentication (Recommended for Quick Start)

**Pros:**
- Fast setup (5 minutes)
- No Azure configuration needed

**Cons:**
- Less secure (password in file)
- MFA may require app password

**Setup:**
```bash
SHAREPOINT_AUTH_METHOD=user
SHAREPOINT_USERNAME=your_email@zaks24.onmicrosoft.com
SHAREPOINT_PASSWORD=your_password
```

**If MFA is enabled:**
1. Go to https://account.activedirectory.windowsazure.com/AppPasswords.aspx
2. Create new app password
3. Use app password in `.env.sharepoint`

---

### Option 2: App Registration (Recommended for Automation)

**Pros:**
- More secure (no password storage)
- Better for scheduled/automated syncs
- Works with MFA

**Cons:**
- Requires Azure AD setup (20 minutes)

#### Setup Steps:

**1. Register App in Azure AD**

a) Go to: https://portal.azure.com → Azure Active Directory → App registrations → New registration

b) Configure:
- **Name:** DataRoom Sync Script
- **Supported account types:** Single tenant
- **Redirect URI:** Leave blank
- Click **Register**

c) Note down:
- **Application (client) ID** → `SHAREPOINT_CLIENT_ID`
- **Directory (tenant) ID** → `SHAREPOINT_TENANT_ID`

**2. Create Client Secret**

a) In your app → Certificates & secrets → New client secret
b) Description: "Sync Script"
c) Expires: 24 months
d) Click **Add**
e) **Copy the Value immediately** → `SHAREPOINT_CLIENT_SECRET`
   (You cannot view it again!)

**3. Grant API Permissions**

a) In your app → API permissions → Add a permission
b) Select **SharePoint** → **Application permissions**
c) Add these permissions:
   - `Sites.ReadWrite.All`
   - `Files.ReadWrite.All`
d) Click **Grant admin consent for [Your Organization]**

**4. Configure Environment**

```bash
nano .env.sharepoint
```

```bash
SHAREPOINT_AUTH_METHOD=app
SHAREPOINT_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SHAREPOINT_CLIENT_SECRET=your_secret_value_here
SHAREPOINT_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## Usage

### Manual Sync

```bash
cd /home/zaks/Zaks-llm
source venv/bin/activate

# Load credentials
source .env.sharepoint

# Run sync
python scripts/sharepoint_sync.py
```

### Scheduled Sync (Daily)

Add to crontab:
```bash
crontab -e
```

```bash
# Sync DataRoom to SharePoint every day at 6 PM
0 18 * * * cd /home/zaks/Zaks-llm && source venv/bin/activate && source .env.sharepoint && python scripts/sharepoint_sync.py >> /home/zaks/bookkeeping/logs/sharepoint-sync.log 2>&1
```

### Sync Specific Folder

Edit script and call:
```python
syncer.sync_directory(
    "/home/zaks/DataRoom/01-ACTIVE-DEALS",
    "Shared Documents/DataRoom/01-ACTIVE-DEALS"
)
```

---

## Troubleshooting

### Authentication Failed

**Error:** `User authentication failed`

**Solutions:**
1. Check username/password are correct
2. If MFA enabled, use app password (see above)
3. Verify SharePoint site URL is correct
4. Check account has access to ZakOpsDataRoom site

---

### Permission Denied

**Error:** `403 Forbidden` or `Access denied`

**Solutions:**
1. Verify you're a site member/owner
2. For app auth: Check API permissions granted
3. For app auth: Ensure admin consent was given
4. Verify tenant ID is correct

---

### Folder Not Found

**Error:** `Folder does not exist`

**Solutions:**
1. Script auto-creates folders, but check site exists
2. Verify SharePoint library name is "Shared Documents"
3. Check site URL format: `https://zaks24.sharepoint.com/sites/ZakOpsDataRoom`

---

### Files Not Appearing

**Possible causes:**
1. Check excluded patterns (script skips .env, .log, etc.)
2. Verify file permissions (read access)
3. Check script output for errors
4. Refresh SharePoint page (Ctrl+F5)

---

## SharePoint Structure After Sync

```
ZakOpsDataRoom Site
│
└── Shared Documents/
    │
    ├── DataRoom/                              [Main DataRoom Mirror]
    │   ├── OPERATOR-BIO.md
    │   ├── OPERATOR-BIO.pdf
    │   ├── MASTER-DASHBOARD.md
    │   ├── DIRECTORY-MAP.md
    │   ├── README.md
    │   ├── 00-PIPELINE/
    │   │   ├── MASTER-DEAL-TRACKER.csv
    │   │   ├── Inbound/
    │   │   ├── Screening/
    │   │   └── Qualified/
    │   ├── 01-ACTIVE-DEALS/
    │   │   ├── TFSource-Ecommerce-2025/
    │   │   ├── StoryXpress-SaaS-2025/
    │   │   ├── RateLiner-Logistics-2025/
    │   │   └── AVS-Cybersecurity-2025/
    │   ├── 02-PORTFOLIO/
    │   ├── 03-DEAL-SOURCES/
    │   ├── 04-FRAMEWORKS/
    │   ├── 05-ADVISORS/
    │   ├── 06-KNOWLEDGE-BASE/
    │   ├── 07-FINANCE/
    │   └── 08-ARCHIVE/
    │
    ├── Implementation-Plans/                   [Tech Implementation Docs]
    │   ├── LINKEDIN-MCP-IMPLEMENTATION.md
    │   ├── AUTOMATED-JOB-APPLICATION-WORKFLOW.md
    │   └── SHAREPOINT-SYNC-GUIDE.md (this file)
    │
    └── Deal-Origination-Engine/                [DOE Documentation]
        ├── DEAL-ORIGINATION-ENGINE-ARCHITECTURE.md
        ├── DEAL-ORIGINATION-ENGINE-IMPLEMENTATION.md
        ├── DEAL-ORIGINATION-ENGINE-SUMMARY.md
        └── DEAL-ORIGINATION-PLAYBOOK.md
```

---

## Advanced: Version Control Integration

To automatically sync after git commits:

**Create git hook:**
```bash
nano /home/zaks/DataRoom/.git/hooks/post-commit
```

```bash
#!/bin/bash
cd /home/zaks/Zaks-llm
source venv/bin/activate
source .env.sharepoint
python scripts/sharepoint_sync.py --quiet
```

```bash
chmod +x /home/zaks/DataRoom/.git/hooks/post-commit
```

---

## Security Best Practices

1. **Never commit `.env.sharepoint` to git**
   - Already in `.gitignore`
   - Contains sensitive credentials

2. **Use app authentication for automation**
   - More secure than password
   - Works with MFA

3. **Rotate secrets regularly**
   - App secrets: Every 6-12 months
   - App passwords: Every 3-6 months

4. **Monitor access logs**
   - SharePoint site settings → Site permissions → Advanced
   - Check "Site Collection Audit Log Reports"

5. **Backup credentials securely**
   - Store in password manager (1Password, LastPass, Bitwarden)
   - Have recovery plan if credentials lost

---

## Cost

**SharePoint Storage:**
- Included with Microsoft 365 subscription
- 1 TB per user (likely sufficient)
- Additional storage: $0.20/GB/month if needed

**Script Operation:**
- Free (runs locally, no API charges)

---

## Next Steps

1. ✅ Run initial sync (see Quick Start)
2. ✅ Verify files in SharePoint
3. ✅ Set up scheduled sync (cron job)
4. ✅ Share site with advisors/partners if needed
5. ✅ Configure version history settings in SharePoint

---

## Support

**Script Issues:**
- Check logs: `/home/zaks/bookkeeping/logs/sharepoint-sync.log`
- Run with verbose: `python scripts/sharepoint_sync.py --verbose`

**SharePoint Issues:**
- Microsoft 365 admin center: https://admin.microsoft.com
- SharePoint admin: https://zaks24-admin.sharepoint.com

**Documentation:**
- Office365-REST-Python-Client: https://github.com/vgrem/Office365-REST-Python-Client
- Microsoft Graph API: https://learn.microsoft.com/en-us/graph/

---

**Last Updated:** December 7, 2025
**Maintained by:** Zaks / ZakOps Prime
**Version:** 1.0
