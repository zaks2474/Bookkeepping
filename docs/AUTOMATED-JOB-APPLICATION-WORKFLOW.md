# Automated Job Application Workflow Implementation Plan

**Date:** 2025-12-04
**Purpose:** Build end-to-end automation for finding, analyzing, and applying to LinkedIn jobs
**Dependencies:** LinkedIn MCP Server, mcp-browser-use, Claude Code API
**Status:** Planning - Ready for implementation after LinkedIn MCP is operational

---

## Overview

Create an intelligent job application system that:
1. **Discovers** relevant jobs via LinkedIn MCP
2. **Analyzes** job fit using AI (Claude)
3. **Prepares** customized application materials
4. **Applies** automatically via mcp-browser-use

**Goal:** Reduce job application time from 30+ minutes to 2-3 minutes with better quality and targeting.

---

## Architecture

```
┌─────────────────┐
│  LinkedIn MCP   │ ──> Job Discovery & Filtering
│   (Port 8030)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Claude Code    │ ──> Analysis & Material Generation
│   API (8090)    │     - Resume tailoring
└────────┬────────┘     - Cover letter writing
         │              - Fit assessment
         ▼
┌─────────────────┐
│ mcp-browser-use │ ──> Form Automation & Submission
│   (Port 8020)   │     - Login handling
└─────────────────┘     - Form filling
                        - Document upload
```

---

## Prerequisites

- [x] LinkedIn MCP Server running (see LINKEDIN-MCP-IMPLEMENTATION.md)
- [x] mcp-browser-use service running (already on port 8020)
- [x] Claude Code API operational (port 8090)
- [ ] Resume in standardized format (PDF + JSON metadata)
- [ ] LinkedIn credentials for mcp-browser-use
- [ ] Job search criteria defined

---

## Phase 1: Job Discovery Pipeline

### Component 1.1: Job Search Orchestrator

**File:** `/home/zaks/Zaks-llm/src/job_search_orchestrator.py`

**Purpose:** Coordinate LinkedIn MCP queries based on user preferences

**Features:**
- Daily/hourly job search scheduling
- Multiple keyword and location combinations
- Deduplication of results
- Job posting change detection
- Persistent job database (SQLite)

**Implementation:**
```python
class JobSearchOrchestrator:
    def __init__(self, linkedin_mcp_url, criteria):
        self.linkedin_mcp = LinkedInMCPClient(linkedin_mcp_url)
        self.criteria = criteria  # keywords, locations, experience, etc.
        self.db = JobDatabase('jobs.db')

    async def discover_jobs(self):
        """Execute searches and return new job postings"""
        jobs = []
        for keyword in self.criteria.keywords:
            for location in self.criteria.locations:
                results = await self.linkedin_mcp.search_jobs(
                    keywords=keyword,
                    location=location
                )
                jobs.extend(results)

        # Deduplicate and filter
        new_jobs = self.db.filter_new_jobs(jobs)
        return new_jobs

    async def get_recommended_jobs(self):
        """Get LinkedIn's recommended jobs"""
        return await self.linkedin_mcp.get_recommended_jobs()
```

**Configuration:**
```yaml
# config/job_search_criteria.yaml
keywords:
  - "Python Developer"
  - "Machine Learning Engineer"
  - "AI Engineer"
locations:
  - "San Francisco Bay Area"
  - "Remote"
  - "New York"
experience_level: ["mid-senior", "senior"]
job_types: ["full-time", "contract"]
exclude_keywords:
  - "unpaid"
  - "intern"
  - "junior"
salary_minimum: 120000
```

---

## Phase 2: AI-Powered Analysis & Fit Assessment

### Component 2.1: Job Analyzer

**File:** `/home/zaks/Zaks-llm/src/job_analyzer.py`

**Purpose:** Evaluate job fit and extract requirements

**Features:**
- Extract key requirements from job description
- Score job fit (0-100) based on your profile
- Identify gaps and strengths
- Generate talking points
- Estimate application success probability

**Implementation:**
```python
class JobAnalyzer:
    def __init__(self, claude_api_url, user_profile):
        self.claude = ClaudeClient(claude_api_url)
        self.profile = user_profile  # Your skills, experience, resume

    async def analyze_job(self, job_posting):
        """Deep analysis of job fit"""
        prompt = f"""
        Analyze this job posting for fit assessment:

        Job Title: {job_posting.title}
        Company: {job_posting.company}
        Description: {job_posting.description}

        My Profile:
        {self.profile.to_text()}

        Provide:
        1. Fit Score (0-100)
        2. Key matching qualifications
        3. Gaps or missing requirements
        4. Recommended customizations for resume
        5. Cover letter key points
        6. Interview preparation topics
        """

        analysis = await self.claude.analyze(prompt)
        return JobAnalysis(
            job_id=job_posting.id,
            fit_score=analysis.fit_score,
            matches=analysis.matches,
            gaps=analysis.gaps,
            recommendations=analysis.recommendations
        )
```

**Fit Scoring Logic:**
```
Factors:
- Required skills match: 40 points
- Experience level match: 20 points
- Industry/domain match: 15 points
- Location preference: 10 points
- Company culture fit: 10 points
- Salary alignment: 5 points

Threshold:
- 80+: Excellent fit - Auto-apply
- 60-79: Good fit - Review & apply
- 40-59: Moderate fit - Consider
- <40: Poor fit - Skip
```

---

### Component 2.2: Application Material Generator

**File:** `/home/zaks/Zaks-llm/src/material_generator.py`

**Purpose:** Create customized resumes and cover letters

**Features:**
- Resume tailoring (highlight relevant experience)
- Cover letter generation
- Portfolio/project selection
- Keyword optimization for ATS
- Multiple format support (PDF, DOCX)

**Implementation:**
```python
class MaterialGenerator:
    def __init__(self, claude_api_url, base_resume, templates):
        self.claude = ClaudeClient(claude_api_url)
        self.base_resume = base_resume
        self.templates = templates

    async def generate_resume(self, job_posting, job_analysis):
        """Create tailored resume"""
        prompt = f"""
        Customize this resume for the job posting:

        Base Resume:
        {self.base_resume.to_text()}

        Job Requirements:
        {job_analysis.requirements}

        Instructions:
        1. Reorder experience to highlight relevant roles
        2. Emphasize matching skills: {job_analysis.matches}
        3. Add keywords for ATS: {job_posting.keywords}
        4. Keep to 1-2 pages
        5. Use action verbs and quantify achievements
        """

        tailored_resume = await self.claude.generate(prompt)
        return Resume(
            content=tailored_resume,
            format='latex',  # Convert to PDF
            job_id=job_posting.id
        )

    async def generate_cover_letter(self, job_posting, job_analysis):
        """Create personalized cover letter"""
        prompt = f"""
        Write a compelling cover letter for:

        Company: {job_posting.company}
        Position: {job_posting.title}
        Key Requirements: {job_analysis.requirements}
        My Strengths: {job_analysis.matches}

        Talking Points:
        {job_analysis.cover_letter_points}

        Style: Professional but conversational, 3-4 paragraphs
        """

        cover_letter = await self.claude.generate(prompt)
        return CoverLetter(
            content=cover_letter,
            job_id=job_posting.id
        )
```

**Template System:**
```
templates/
├── resume_base.tex          # LaTeX resume template
├── cover_letter.md          # Markdown cover letter template
├── portfolio_entry.md       # Project showcase template
└── email_followup.md        # Follow-up email template
```

---

## Phase 3: Automated Application via Browser Automation

### Component 3.1: Browser Application Bot

**File:** `/home/zaks/Zaks-llm/src/application_bot.py`

**Purpose:** Handle form filling and submission via mcp-browser-use

**Features:**
- LinkedIn "Easy Apply" automation
- Direct company career page applications
- Form field detection and filling
- Document upload handling
- CAPTCHA detection (human intervention)
- Screenshot capture for audit trail

**Implementation:**
```python
class ApplicationBot:
    def __init__(self, browser_mcp_url, credentials):
        self.browser = BrowserMCPClient(browser_mcp_url)
        self.credentials = credentials

    async def apply_to_job(self, job_url, materials):
        """Execute application process"""
        # 1. Navigate to job posting
        await self.browser.navigate(job_url)

        # 2. Click "Easy Apply" or "Apply" button
        apply_button = await self.browser.find_element(
            selector="button[class*='apply']"
        )
        await apply_button.click()

        # 3. Fill form fields
        form_fields = await self.detect_form_fields()
        for field in form_fields:
            value = self.map_field_value(field, materials)
            await self.browser.fill_field(field.id, value)

        # 4. Upload resume/cover letter
        if resume_upload := await self.find_upload_field('resume'):
            await self.browser.upload_file(
                resume_upload.id,
                materials.resume.pdf_path
            )

        # 5. Handle additional questions
        questions = await self.detect_screening_questions()
        answers = await self.answer_questions(questions, materials)

        # 6. Review and submit
        await self.browser.screenshot('pre_submit.png')

        # Require human confirmation for actual submission
        if self.auto_submit_enabled:
            await self.browser.click_submit()
        else:
            return ApplicationReview(
                status='ready_for_review',
                screenshot='pre_submit.png',
                job_url=job_url
            )

    async def detect_form_fields(self):
        """Identify all form inputs"""
        fields = await self.browser.execute_script("""
            return Array.from(document.querySelectorAll('input, textarea, select'))
                .map(el => ({
                    id: el.id,
                    name: el.name,
                    type: el.type,
                    label: el.labels?.[0]?.innerText,
                    required: el.required
                }));
        """)
        return fields

    def map_field_value(self, field, materials):
        """Map form field to application data"""
        field_map = {
            'firstName': materials.profile.first_name,
            'lastName': materials.profile.last_name,
            'email': materials.profile.email,
            'phone': materials.profile.phone,
            'linkedin': materials.profile.linkedin_url,
            'currentCompany': materials.profile.current_company,
            'yearsExperience': materials.profile.years_experience,
            # Add more mappings
        }

        # Fuzzy matching for field names
        for key, value in field_map.items():
            if key.lower() in field.name.lower():
                return value

        return None
```

**Safety Features:**
```python
class SafetyChecks:
    """Prevent accidental bad applications"""

    def pre_submit_checks(self, application):
        checks = [
            ('resume_attached', application.has_resume),
            ('email_correct', application.email == expected_email),
            ('fields_filled', application.completion_rate > 0.9),
            ('no_typos', self.spell_check(application.text_fields)),
            ('salary_reasonable', self.validate_salary(application.salary))
        ]

        failed = [name for name, result in checks if not result]
        if failed:
            raise ApplicationError(f"Failed checks: {failed}")
```

---

## Phase 4: Orchestration & Workflow Management

### Component 4.1: Application Pipeline

**File:** `/home/zaks/Zaks-llm/src/application_pipeline.py`

**Purpose:** End-to-end workflow orchestration

**State Machine:**
```
DISCOVERED → ANALYZED → MATERIALS_READY → APPLYING → SUBMITTED → TRACKING
     │          │             │               │            │           │
     └──SKIPPED─┴─────LOW_FIT─┴───────FAILED──┴────REJECTED─┴───ACCEPTED
```

**Implementation:**
```python
class ApplicationPipeline:
    def __init__(self, config):
        self.job_search = JobSearchOrchestrator(config.linkedin_mcp)
        self.analyzer = JobAnalyzer(config.claude_api, config.profile)
        self.materials = MaterialGenerator(config.claude_api, config.resume)
        self.bot = ApplicationBot(config.browser_mcp, config.credentials)
        self.db = ApplicationDatabase('applications.db')

    async def run_daily_cycle(self):
        """Execute daily job application routine"""

        # 1. Discover new jobs
        print("Discovering jobs...")
        jobs = await self.job_search.discover_jobs()
        recommended = await self.job_search.get_recommended_jobs()
        all_jobs = jobs + recommended

        print(f"Found {len(all_jobs)} new jobs")

        # 2. Analyze each job
        print("Analyzing fit...")
        analyzed_jobs = []
        for job in all_jobs:
            analysis = await self.analyzer.analyze_job(job)

            # Filter by fit score
            if analysis.fit_score >= 60:
                analyzed_jobs.append((job, analysis))
                print(f"  ✓ {job.title} at {job.company} - Score: {analysis.fit_score}")
            else:
                print(f"  ✗ {job.title} at {job.company} - Score: {analysis.fit_score} (skipped)")
                self.db.mark_skipped(job.id, reason='low_fit_score')

        # 3. Generate materials for high-fit jobs
        print(f"\nPreparing materials for {len(analyzed_jobs)} jobs...")
        applications_ready = []
        for job, analysis in analyzed_jobs:
            resume = await self.materials.generate_resume(job, analysis)
            cover_letter = await self.materials.generate_cover_letter(job, analysis)

            applications_ready.append({
                'job': job,
                'analysis': analysis,
                'resume': resume,
                'cover_letter': cover_letter
            })

        # 4. Apply to jobs
        print("\nApplying to jobs...")
        for app in applications_ready:
            try:
                # Auto-apply for excellent fits (80+)
                auto_apply = app['analysis'].fit_score >= 80

                result = await self.bot.apply_to_job(
                    job_url=app['job'].url,
                    materials=app,
                    auto_submit=auto_apply
                )

                if result.status == 'submitted':
                    print(f"  ✓ Applied: {app['job'].title}")
                    self.db.record_application(app['job'].id, 'submitted')
                else:
                    print(f"  ⏸ Ready for review: {app['job'].title}")
                    self.db.record_application(app['job'].id, 'pending_review')

                # Rate limiting
                await asyncio.sleep(60)  # Wait 1 minute between applications

            except Exception as e:
                print(f"  ✗ Failed: {app['job'].title} - {e}")
                self.db.record_application(app['job'].id, 'failed', error=str(e))

        # 5. Generate summary report
        summary = self.generate_summary(all_jobs, analyzed_jobs, applications_ready)
        await self.send_report(summary)
```

---

### Component 4.2: Application Tracking Dashboard

**File:** `/home/zaks/Zaks-llm/src/dashboard.py`

**Purpose:** Monitor application status and metrics

**Features:**
- Application history and status
- Success rate tracking
- Interview pipeline
- Response time analytics
- Weekly/monthly reports

**Schema:**
```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    job_id TEXT UNIQUE,
    job_title TEXT,
    company TEXT,
    job_url TEXT,
    discovered_date DATE,
    fit_score INTEGER,
    status TEXT,  -- discovered, analyzed, submitted, interviewing, rejected, accepted
    applied_date DATE,
    response_date DATE,
    resume_path TEXT,
    cover_letter_path TEXT,
    notes TEXT
);

CREATE TABLE metrics (
    date DATE PRIMARY KEY,
    jobs_discovered INTEGER,
    jobs_analyzed INTEGER,
    applications_submitted INTEGER,
    responses_received INTEGER,
    interviews_scheduled INTEGER
);
```

**Dashboard UI:**
```
┌─────────────────────────────────────┐
│  Job Application Dashboard          │
├─────────────────────────────────────┤
│  Today's Activity:                  │
│  • Discovered: 23 jobs              │
│  • Analyzed: 12 jobs                │
│  • Applied: 5 jobs                  │
│  • Pending Review: 3 jobs           │
├─────────────────────────────────────┤
│  Pipeline Status:                   │
│  • Submitted: 47                    │
│  • Interviewing: 3                  │
│  • Offers: 1                        │
├─────────────────────────────────────┤
│  Recent Applications:               │
│  1. [Submitted] Python Dev @ Google │
│     Fit: 92 | Applied: 2h ago      │
│  2. [Review] ML Eng @ Meta          │
│     Fit: 85 | Needs approval       │
└─────────────────────────────────────┘
```

---

## Configuration & Setup

### Step 1: Create Configuration File

**File:** `/home/zaks/Zaks-llm/config/job_application_config.yaml`

```yaml
# Job Application Automation Config

user_profile:
  name: "Your Name"
  email: "your.email@example.com"
  phone: "+1-555-0123"
  linkedin_url: "https://linkedin.com/in/yourprofile"
  location: "San Francisco, CA"
  current_company: "Current Employer"
  years_experience: 8

  skills:
    - Python
    - Machine Learning
    - Docker
    - FastAPI
    - PostgreSQL

  resume_path: "/home/zaks/documents/resume.pdf"
  base_resume_json: "/home/zaks/documents/resume.json"

search_criteria:
  keywords:
    - "Python Developer"
    - "Backend Engineer"
    - "ML Engineer"
  locations:
    - "San Francisco Bay Area"
    - "Remote"
  experience_levels:
    - "mid-senior"
    - "senior"
  job_types:
    - "full-time"
  salary_minimum: 120000
  exclude_keywords:
    - "unpaid"
    - "volunteer"

automation:
  auto_apply_threshold: 85  # Fit score for auto-submission
  daily_application_limit: 10
  rate_limit_seconds: 60  # Wait between applications
  require_human_review: true  # Always review before final submit

services:
  linkedin_mcp: "http://localhost:8030"
  claude_api: "http://localhost:8090"
  browser_mcp: "http://localhost:8020"

notifications:
  email: "your.email@example.com"
  daily_summary: true
  instant_alerts: true  # For high-fit jobs
```

---

### Step 2: Create User Profile JSON

**File:** `/home/zaks/documents/resume.json`

```json
{
  "personal": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+1-555-0123",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/yourprofile",
    "github": "github.com/yourusername"
  },
  "summary": "Experienced software engineer specializing in...",
  "experience": [
    {
      "company": "Current Company",
      "title": "Senior Software Engineer",
      "start_date": "2020-01",
      "end_date": null,
      "highlights": [
        "Built X that achieved Y",
        "Led team of Z engineers"
      ],
      "technologies": ["Python", "Docker", "AWS"]
    }
  ],
  "education": [...],
  "skills": {
    "languages": ["Python", "JavaScript", "Go"],
    "frameworks": ["FastAPI", "React", "Django"],
    "tools": ["Docker", "Kubernetes", "PostgreSQL"]
  }
}
```

---

### Step 3: Add to Docker Compose

**File:** `/home/zaks/Zaks-llm/docker-compose.yml`

```yaml
  job-application-bot:
    build:
      context: .
      dockerfile: Dockerfile.job-bot
    container_name: job-application-bot
    environment:
      - CONFIG_PATH=/app/config/job_application_config.yaml
      - DATABASE_PATH=/app/data/applications.db
    volumes:
      - ./config:/app/config:ro
      - ./data:/app/data
      - ./logs/job-bot:/app/logs
      - /home/zaks/documents:/app/documents:ro
    networks:
      - ai-network
    depends_on:
      - linkedin-mcp
      - mcp-browser-use
    restart: unless-stopped
```

---

### Step 4: Create Dockerfile

**File:** `/home/zaks/Zaks-llm/Dockerfile.job-bot`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-job-bot.txt .
RUN pip install --no-cache-dir -r requirements-job-bot.txt

# Copy application code
COPY src/job_search_orchestrator.py src/
COPY src/job_analyzer.py src/
COPY src/material_generator.py src/
COPY src/application_bot.py src/
COPY src/application_pipeline.py src/
COPY src/dashboard.py src/

# Create data directories
RUN mkdir -p /app/data /app/logs /app/config

# Run pipeline
CMD ["python", "-m", "src.application_pipeline"]
```

---

### Step 5: Schedule Daily Runs

**Cron Job:**
```bash
# Run job application pipeline daily at 9 AM
0 9 * * * cd /home/zaks/Zaks-llm && docker compose exec job-application-bot python -m src.application_pipeline >> /home/zaks/bookkeeping/logs/job-applications.log 2>&1
```

**Or use systemd timer:**

**File:** `/etc/systemd/system/job-application-bot.service`
```ini
[Unit]
Description=Job Application Bot
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/home/zaks/Zaks-llm
ExecStart=/usr/bin/docker compose exec job-application-bot python -m src.application_pipeline
User=zaks

[Install]
WantedBy=multi-user.target
```

**File:** `/etc/systemd/system/job-application-bot.timer`
```ini
[Unit]
Description=Run Job Application Bot Daily

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

---

## Usage Examples

### Manual Run
```bash
cd /home/zaks/Zaks-llm
docker compose exec job-application-bot python -m src.application_pipeline
```

### View Dashboard
```bash
docker compose exec job-application-bot python -m src.dashboard
```

### Check Pending Reviews
```bash
docker compose exec job-application-bot python -m src.dashboard --pending
```

### Approve Application
```bash
docker compose exec job-application-bot python -m src.application_bot approve <job_id>
```

---

## Safety & Ethics

### Guardrails
1. **Human-in-the-Loop:** Require review before final submission (configurable)
2. **Rate Limiting:** Max 10 applications/day to avoid spam
3. **Quality Gates:** Only apply to 60+ fit score jobs
4. **Terms Compliance:** Respect LinkedIn ToS and robots.txt
5. **Data Privacy:** All data stays local; no external sharing

### Best Practices
- Always review materials before submission
- Customize heavily for high-priority companies
- Use automation for volume, not as replacement for quality
- Track responses to tune fit scoring algorithm
- Regularly update base resume and profile

### Legal Considerations
- LinkedIn ToS prohibits automated scraping (personal use gray area)
- Many job boards explicitly ban bots
- Use at your own risk; this is for personal research/efficiency
- Consider using API integrations where available

---

## Testing Plan

### Phase 1: Unit Tests
```bash
pytest tests/test_job_search.py
pytest tests/test_analyzer.py
pytest tests/test_materials.py
pytest tests/test_bot.py
```

### Phase 2: Integration Tests
```bash
# Test with fake job posting
python -m tests.integration.test_pipeline_mock

# Test LinkedIn MCP connection
python -m tests.integration.test_linkedin_mcp

# Test browser automation (dry run)
python -m tests.integration.test_browser_bot --dry-run
```

### Phase 3: Dry Run
```bash
# Run full pipeline without actual submissions
python -m src.application_pipeline --dry-run --limit 5
```

### Phase 4: Pilot
```bash
# Apply to 2-3 test jobs with human review
python -m src.application_pipeline --manual-approve --limit 3
```

---

## Monitoring & Alerts

### Metrics to Track
- Jobs discovered per day
- Average fit score
- Application submission rate
- Response rate (%)
- Time to first response
- Interview conversion rate
- Offer acceptance rate

### Alerts
```yaml
alerts:
  - trigger: "high_fit_job_found"  # Fit score > 90
    action: "send_email"

  - trigger: "application_failed"
    action: "log_error"

  - trigger: "response_received"
    action: "send_notification"

  - trigger: "interview_scheduled"
    action: "update_calendar"
```

---

## Future Enhancements

### Phase 2 Features
- Email response parsing and auto-replies
- Calendar integration for interview scheduling
- Salary negotiation assistant
- Interview prep automation (research company, practice questions)
- LinkedIn profile optimization based on job trends

### Phase 3 Features
- Multi-platform support (Indeed, Glassdoor, AngelList)
- Recruiter outreach automation
- Network analysis (2nd/3rd connections at target companies)
- Company research reports
- Offer comparison and negotiation analytics

---

## Rollback Plan

If automation causes issues:

1. **Disable Auto-Apply:**
   ```yaml
   automation:
     require_human_review: true
     auto_apply_threshold: 999  # Effectively disabled
   ```

2. **Pause Pipeline:**
   ```bash
   docker compose stop job-application-bot
   ```

3. **Review Applications:**
   ```bash
   python -m src.dashboard --status submitted --last 24h
   ```

4. **Withdraw if Needed:**
   - Manually withdraw from LinkedIn
   - Send apology email if error detected

---

## Implementation Checklist

### Prerequisites
- [ ] LinkedIn MCP server operational
- [ ] mcp-browser-use tested and working
- [ ] Resume in PDF + JSON format
- [ ] Profile data complete
- [ ] Job search criteria defined

### Development
- [ ] Create job_application_config.yaml
- [ ] Implement JobSearchOrchestrator
- [ ] Implement JobAnalyzer
- [ ] Implement MaterialGenerator
- [ ] Implement ApplicationBot
- [ ] Implement ApplicationPipeline
- [ ] Create Dashboard
- [ ] Write unit tests
- [ ] Write integration tests

### Deployment
- [ ] Create Dockerfile.job-bot
- [ ] Add service to docker-compose.yml
- [ ] Build and test container
- [ ] Run dry-run tests
- [ ] Pilot with 2-3 applications
- [ ] Set up monitoring and alerts
- [ ] Configure cron/systemd timer
- [ ] Update SERVICE-CATALOG.md
- [ ] Update CHANGES.md

### Operations
- [ ] Document troubleshooting procedures
- [ ] Set up log rotation
- [ ] Create backup strategy for applications.db
- [ ] Establish review cadence
- [ ] Track success metrics

**Estimated Development Time:** 2-3 weeks
**Estimated Testing Time:** 1 week
**Total:** ~4 weeks for full implementation

---

## References

- LinkedIn MCP: `/home/zaks/bookkeeping/docs/LINKEDIN-MCP-IMPLEMENTATION.md`
- mcp-browser-use: Port 8020 (already running)
- Claude Code API: Port 8090
- Service Catalog: `/home/zaks/bookkeeping/docs/SERVICE-CATALOG.md`

---

**End of Implementation Plan**
