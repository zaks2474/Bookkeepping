# CODEX — Email Triage Verification (Runtime + LLM + Quality)

Date: 2026-01-07  
Scope: **Phase 0 verification only** (no behavior changes).

## Executive Summary

- **Hourly runtime:** `zakops-email-triage.timer` triggers `zakops-email-triage.service` (oneshot) which runs `python3 -m email_triage_agent.run_once` as user `zaks`.
- **Code path:** `email_triage_agent.run_once:main → load_config → asyncio.run(run_once) → process_one_message → decide_actions_and_labels → classify_email`.
- **LLM usage:** **No LLM is used by the triage runtime today** (no vLLM/OpenAI/LangChain/LangGraph calls in the triage runner path).
- **Local Qwen availability:** vLLM is running and exposes `Qwen/Qwen2.5-32B-Instruct-AWQ` at `http://localhost:8000/v1`, but triage does not call it.
- **Quality:** Quarantine queue contains **obvious non-deals** (e.g. security product welcome email, newsletter) that were classified as `DEAL_SIGNAL` at ingestion time; extraction quality is not “world-class” (company extraction mostly null; link typing skewed toward `nda`; malformed URLs present).
- **GO / NO-GO:** **NO-GO** — triage is not using local Qwen and current output quality is not world-class. Proceed to Phase 1+ agentic upgrade.

---

## 0.1 Runtime + Wiring Confirmation (Evidence)

### What runs hourly

**Timer unit**

`/etc/systemd/system/zakops-email-triage.timer`:

```
[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=5m
Unit=zakops-email-triage.service
```

Evidence:
- `systemctl status zakops-email-triage.timer` shows the timer is **active (waiting)** and triggers the service hourly.

### Which unit and ExecStart

**Service unit**

`/etc/systemd/system/zakops-email-triage.service`:

```
[Service]
Type=oneshot
User=zaks
WorkingDirectory=/home/zaks/bookkeeping/scripts
Environment=PYTHONUNBUFFERED=1
Environment=EMAIL_TRIAGE_ENABLE_ACTIONS=true
Environment=EMAIL_TRIAGE_ACTIONS_BASE_URL=http://localhost:8090
ExecStart=/usr/bin/python3 -m email_triage_agent.run_once
```

Evidence:
- `systemctl status zakops-email-triage.service` shows **successful oneshot runs** (exits `0/SUCCESS`) and logs summary lines like:
  - `email_triage_run completed processed=<N> skipped=<N> failed=<N> query='in:inbox -label:ZakOps/Processed newer_than:30d'`

### Code path executed (module/function map)

Entrypoint:
- `bookkeeping/scripts/email_triage_agent/run_once.py:main`

Main execution path:
- `bookkeeping/scripts/email_triage_agent/run_once.py:main`
  - parses args
  - calls `load_config(args)`
  - calls `asyncio.run(run_once(cfg))`
- `bookkeeping/scripts/email_triage_agent/run_once.py:run_once`
  - loads vendor patterns
  - loads thread mappings from registry JSON
  - opens Gmail MCP stdio session (`McpStdioSession(command=gmail_mcp_command())`)
  - iterates messages from `gmail.search_emails(...)`
  - calls `process_one_message(...)` per message
- `bookkeeping/scripts/email_triage_agent/run_once.py:process_one_message`
  - calls `gmail.read_email(...)`
  - calls `decide_actions_and_labels(...)`
  - **only creates Kinetic Actions** when `decision.classification.classification == "DEAL_SIGNAL"`
- `bookkeeping/scripts/email_triage_agent/triage_logic.py:decide_actions_and_labels`
  - calls `extract_entities(...)`
  - calls `classify_email(...)`

Configuration inputs (env vars) are read here:
- `bookkeeping/scripts/email_triage_agent/run_once.py:load_config`
  - `EMAIL_TRIAGE_QUERY`
  - `EMAIL_TRIAGE_MAX_PER_RUN`
  - `EMAIL_TRIAGE_QUARANTINE_ROOT`
  - `EMAIL_TRIAGE_STATE_DB`
  - `EMAIL_TRIAGE_DEAL_REGISTRY_PATH`
  - `EMAIL_TRIAGE_VENDOR_PATTERNS_MD`
  - `EMAIL_TRIAGE_DRY_RUN`
  - `EMAIL_TRIAGE_MARK_AS_READ`
  - `EMAIL_TRIAGE_MAX_ATTACHMENT_MB`
  - `EMAIL_TRIAGE_SAFE_EXTS`
  - `EMAIL_TRIAGE_UNSAFE_EXTS`
  - `EMAIL_TRIAGE_ACTIONS_BASE_URL`
  - `EMAIL_TRIAGE_ENABLE_ACTIONS`

---

## 0.1 LLM / “Brain” Usage (Evidence)

### Does triage call any LLM?

**No.** The triage runtime is deterministic + heuristics only.

Evidence:
- `bookkeeping/scripts/email_triage_agent/triage_logic.py` contains heuristic classification + denylist logic (no network calls).
- A repo-wide search for common LLM clients inside the triage package finds no usage in the runtime path:
  - `rg -n "OPENAI|vllm|LangChain|LangGraph|chat/completions|ollama" -S bookkeeping/scripts/email_triage_agent`
  - Result: only `export_agent_builder_config.py` mentions a LangGraph deployment base URL; the runner (`run_once.py`) does not import or call it.

### Confirm vLLM exists (local Qwen)

Evidence:
- `ss -tlnp | rg ":(8000)"` shows port `8000` is listening (docker-proxy).
- `curl -s http://localhost:8000/v1/models` returns:
  - `Qwen/Qwen2.5-32B-Instruct-AWQ`

### Confirm LangGraph “brain” exists

Evidence:
- `ss -tlnp | rg ":(8080)"` shows port `8080` is listening (docker-proxy).
- `curl -s http://localhost:8080/health` returns healthy status.

### Does triage call the brain or vLLM?

**No.** There are no references to `http://localhost:8000` or `http://localhost:8080` in the triage runner modules (`run_once.py`, `triage_logic.py`, etc.), and no HTTP client usage in the runtime path.

---

## 0.2 Quality Reality Check (10 Quarantine Items)

Source:
- `GET http://localhost:8090/api/actions/quarantine?limit=50` (sampled first 10 items)

Sanitized observations from the 10-item sample:
- **Obvious non-deals present:** at least 2/10 are clearly not acquisition deal flow:
  - security product welcome/onboarding email (sender domain `info.bitdefender.com`)
  - legal/AI newsletter (sender domain `newsletter.thelegalwire.ai`)
- **Company extraction is mostly missing:** `company` present in **1/10** sampled items.
- **Link typing is not reliable:** in the sample, link types skewed heavily toward `nda` (49 `nda` vs 8 `other`), including on non-deal newsletter content.
- **Malformed URL extraction exists:** 11 malformed URLs across the 10 sampled items (e.g., whitespace-containing or unparsable URLs).
- **No world-class summary/extraction artifacts:** triage currently persists `email.json` + `email_body.txt` and (optionally) safe attachments, but does not produce:
  - `triage_summary.json`
  - `triage_summary.md`
  - extracted fields like asking price, EBITDA, broker name, “operator next step” guidance

Implication:
- Even with deterministic improvements, **the queue still contains false positives** and the operator experience lacks the “fast decision packet” needed for world-class Quarantine.

---

## GO / NO-GO Decision

**NO-GO** for “world-class, local-first, agentic triage.”

Reasons (non-negotiables not met):
1) Triage does **not** use local Qwen/vLLM today (it uses **no LLM**).
2) Quarantine quality is not world-class:
   - false positives (non-deal emails classified as `DEAL_SIGNAL`)
   - weak extraction (company mostly null; link typing errors; malformed URLs)
   - missing operator-ready artifacts (`triage_summary.*`)

Next step (per spec): proceed to Phase 1+ implementation:
- Add a local vLLM/Qwen-powered triage layer behind feature flags (`EMAIL_TRIAGE_LLM_MODE=assist|full`) with strict JSON outputs persisted into quarantine folders.

