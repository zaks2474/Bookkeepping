# Email 3H — Triage Accuracy Baseline (Pre-World-Class Schema)

Generated: 2026-01-11

Scope:
- Establish a **sanitized** baseline for current Email 3H behavior and the main **false-positive drivers** observed in recent Quarantine actions.
- No raw email bodies, attachments, or full URLs (query/fragment) are included in this report.

## 1) Scheduler reality (source of truth)

- Email 3H is currently triggered by **Temporal** (`zakops-email-triage-hourly`) rather than the systemd timer.
- `zakops-email-triage.timer` exists but is **disabled** (inactive).

Operator commands:
- `cd /home/zaks/bookkeeping && make temporal-status`
- `systemctl status zakops-email-triage.timer --no-pager`

## 2) Local vLLM usage (no cloud)

- Local OpenAI-compatible vLLM is running on `http://localhost:8000/v1`
- Model list includes: `Qwen/Qwen2.5-32B-Instruct-AWQ`

Operator commands:
- `curl -s http://localhost:8000/v1/models | jq -r '.data[].id'`
- `cd /home/zaks/bookkeeping/scripts && python3 -m email_triage_agent.run_once --dry-run --max-per-run 1`
  - Expect a header like: `email_triage_config llm_mode=... llm_base_url=http://localhost:8000/v1 ...`

## 3) False-positive drivers (observed patterns)

We sampled recent `EMAIL_TRIAGE.REVIEW_EMAIL` actions and inspected only **metadata** fields:
- `action.summary` (deterministic reason string)
- `inputs.classification`, `inputs.urgency`
- whether `inputs.links` and/or `inputs.attachments` were present

Operator command:
- `curl -s 'http://localhost:8090/api/actions?action_type=EMAIL_TRIAGE.REVIEW_EMAIL&limit=20' | jq ...`

### 3.1 Dominant driver: NDA/confidentiality keyword hits

Most recent review actions show strong weighting on:
- `strong_keywords=['nda']` and/or `['non-disclosure', 'confidentiality']`
- often combined with `deal_links`

This indicates the current scoring is still (in many cases) “keyword + link presence”, not “M&A meaning with evidence”.

### 3.2 Link typing risk: “deal_links” without strong deal context

Many items include `deal_links` even when the underlying email could be:
- legal boilerplate / generic confidentiality language
- portal/access emails that aren’t actually deal opportunities

This supports the blueprint change: LLM should become the deep-understanding classifier (thread-aware), while deterministic rules are strict vetoes for newsletters/transactional.

### 3.3 Attachment weighting risk: attachments_score without semantic check

Some review actions were triggered primarily by:
- `attachments_score=+X.XX` with no meaningful links

This supports hardening “meaningful filename” + “deal-material type” checks before quarantine creation.

## 4) What changes next (per blueprint)

The next implementation step is to:
- adopt a versioned, evidence-based LLM JSON contract (`zakops.email_triage.v1`)
- make evidence quotes + reasons first-class (not just keyword scoring)
- keep deterministic vetoes for newsletters/transactional/spam
- preserve URL sanitization everywhere (no query/fragment)

