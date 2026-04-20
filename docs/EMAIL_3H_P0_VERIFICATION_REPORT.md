# EMAIL 3H — P0 Verification Report (No Changes)

Generated: 2026-01-11T00:49:35-06:00

Scope: **verification only**. This report contains evidence of how “Email 3H” is running right now (scheduler + local LLM usage + current Quarantine signal drivers). No code/config changes were made to produce this report.

## 1) Scheduler reality (what triggers Email 3H)

### 1.1 systemd timer (present, currently disabled)

Evidence:

```bash
$ systemctl status zakops-email-triage.timer --no-pager
```

Output (sanitized):

```
Loaded: loaded (/etc/systemd/system/zakops-email-triage.timer; disabled; preset: enabled)
Active: inactive (dead)
```

The systemd *service* unit exists and documents the one-shot command:

```bash
$ systemctl cat zakops-email-triage.service
```

Key lines:

```
User=zaks
WorkingDirectory=/home/zaks/bookkeeping/scripts
ExecStart=/usr/bin/python3 -m email_triage_agent.run_once
```

### 1.2 Temporal schedule (currently active and unpaused)

Evidence:

```bash
$ cd /home/zaks/bookkeeping && make temporal-status
```

Output (sanitized):

```
zakops-email-triage-hourly    paused=False
zakops-deal-lifecycle-controller-hourly    paused=False
```

The Temporal activity that runs Email 3H is implemented here:
- `/home/zaks/scripts/temporal_worker/activities.py`

Evidence (code path):

```
command=[cfg.python_bin, "-m", "email_triage_agent.run_once"]
cwd="/home/zaks/bookkeeping/scripts"
```

Temporal writes one log file per run:
- `/home/zaks/logs/temporal_worker/email_triage_YYYYMMDD_HHMMSS.log`

Evidence (recent run outputs are just the one-line summary printed by `run_once.py`):

```bash
$ tail -n 2 /home/zaks/logs/temporal_worker/email_triage_20260111_060016.log
```

Output:

```
email_triage_run completed processed=1 skipped=0 failed=0 query='in:inbox -label:ZakOps/Processed newer_than:30d'
```

Conclusion: **Email 3H is currently triggered hourly by Temporal schedules**, not by the systemd timer (which is disabled).

## 2) Local vLLM (Qwen) usage (no cloud calls)

### 2.1 Local vLLM is running and exposes Qwen 2.5 32B

Evidence:

```bash
$ curl -s http://localhost:8000/v1/models | jq -r '.data[].id'
```

Output:

```
Qwen/Qwen2.5-32B-Instruct-AWQ
```

### 2.2 Email triage runner’s LLM config defaults to local vLLM

Source:
- `/home/zaks/bookkeeping/scripts/email_triage_agent/llm_triage.py:load_llm_config()`

Current default behavior:
- `EMAIL_TRIAGE_LLM_MODE` defaults to `assist`
- `EMAIL_TRIAGE_LLM_BASE_URL` defaults to `http://localhost:8000/v1` (unless overridden)
- `EMAIL_TRIAGE_LLM_MODEL` defaults to `Qwen/Qwen2.5-32B-Instruct-AWQ` (unless overridden)

The Temporal worker process does **not** set any `EMAIL_TRIAGE_LLM_*` / `OPENAI_API_BASE` / `VLLM_*` env overrides (filtered check against `/proc/<pid>/environ`), so the triage run uses the local defaults.

### 2.3 Evidence that triage writes Qwen model metadata into Quarantine artifacts

Example artifact (fields only; bullets redacted):

```bash
$ jq '{classification, confidence, model, latency_ms, llm_error, summary_bullets_len:(.summary_bullets|length)}' \\
  /home/zaks/DataRoom/00-PIPELINE/_INBOX_QUARANTINE/19ba346c281df10e/triage_summary.json
```

Output:

```json
{
  "classification": "DEAL_SIGNAL",
  "confidence": 0.9,
  "model": "Qwen/Qwen2.5-32B-Instruct-AWQ",
  "latency_ms": 11706,
  "llm_error": null,
  "summary_bullets_len": 4
}
```

Conclusion: The current triage runtime is capable of using **local vLLM/Qwen** and is already persisting model metadata into Quarantine artifacts when LLM output is available.

## 3) Quarantine false-positive signal drivers (evidence from action history)

### 3.1 Current Quarantine queue (pending approvals)

At the time of this report, the “pending quarantine” queue is empty:

```bash
$ curl -s http://localhost:8090/api/actions/quarantine?limit=50 | jq '{count}'
```

Output:

```json
{"count":0}
```

### 3.2 Recent REVIEW_EMAIL action history (includes completed/rejected)

Since `/api/actions/quarantine` only returns items requiring operator attention, we sampled the most recent `EMAIL_TRIAGE.REVIEW_EMAIL` actions directly:

```bash
$ curl -s 'http://localhost:8090/api/actions?action_type=EMAIL_TRIAGE.REVIEW_EMAIL&limit=200'
```

Aggregate evidence (no subject/sender/body content included):
- review actions returned: `27`
- status breakdown: `COMPLETED=17`, `CANCELLED=7`, `READY=2`, `FAILED=1`
- all were originally classified `DEAL_SIGNAL` at creation time
- LLM confidence present (inputs.confidence non-null): `7 / 27`
- “reason” driver prevalence (from action summary string):
  - `deal_links`: `18 / 27`
  - `attachments_score`: `3 / 27`
  - top strong keywords: `nda (15)`, `non-disclosure (6)`, `confidentiality (5)`, then `cim`, `vdr`, etc.

Interpretation: current Quarantine drivers skew heavily toward **NDA/confidentiality keywords + deal_links**, and a meaningful share of reviewed items end up rejected/cancelled (proxy for false positives).

## 4) Blockers / inconsistencies discovered (and what happens next)

1) **Spec contradiction**: Phase 0 says “No Changes”, but also asks to “add a log line at start of each run” for LLM config visibility. That log line requires a code change.  
   - Resolution: implement the safe log line at the start of Phase 1 (right after this report), and include it in the Phase 1+ verification note.

2) **Historical artifact gaps**: many historical `EMAIL_TRIAGE.REVIEW_EMAIL` actions reference a `triage_summary_path` that no longer exists on disk (likely older runs or artifact movement/cleanup).  
   - Resolution: Phase 2 will ensure every deal-signal run writes `triage_summary.json` + `triage_summary.md` deterministically, and Phase 1 will harden prefiltering so fewer irrelevant emails ever create review actions.

