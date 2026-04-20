# EMAIL 3H Deep Analysis Report (WHAT + HOW)

## Executive Summary

- **Email 3H** is the hourly email triage job that pulls Gmail inbox messages via a **local Gmail MCP server** (stdio JSON-RPC) and decides whether each message is a **deal signal** or not.
- **Current scheduler reality**: the legacy systemd timer `zakops-email-triage.timer` exists but is **disabled**; Email 3H is currently being triggered hourly by **Temporal schedules** (`zakops-email-triage-hourly`) which run `python -m email_triage_agent.run_once` (evidence in Appendix).
- **Classification is hybrid**:
  - deterministic scoring in `bookkeeping/scripts/email_triage_agent/triage_logic.py:310` (keywords + link types + attachment heuristics + sender denylist)
  - optional local LLM layer (vLLM/OpenAI-compatible) in `bookkeeping/scripts/email_triage_agent/llm_triage.py:63` and invoked from `bookkeeping/scripts/email_triage_agent/run_once.py:515`
- **Quarantine today is action-backed**: when final classification is `DEAL_SIGNAL`, the runner creates an approval-gated kinetic action `EMAIL_TRIAGE.REVIEW_EMAIL` (`bookkeeping/scripts/email_triage_agent/run_once.py:714`) with pointers to a quarantine folder containing the local artifacts.
- **Why irrelevant emails enter Quarantine** (top drivers observed from real historical items):
  1) keyword scoring is applied to raw HTML/URLs, so random URL/HTML tokens can hit deal keywords
  2) attachment “deal hint” matching uses substring checks and includes short tokens (e.g., `ltm`), which can appear inside random attachment IDs
  3) link type inference can mark many links as `nda` based on surrounding text, which then counts as `deal_links`
  4) sender denylist is effective but requires continuous maintenance; gaps allow marketing/newsletters through
  5) assist-mode LLM can only downgrade with high confidence; if LLM is off/unavailable/low-confidence, deterministic false positives remain

## How Email 3H Works Today (Step-by-step)

### 1) Trigger / schedule

- **Legacy (present but disabled)**: systemd timer `zakops-email-triage.timer` runs `zakops-email-triage.service` hourly.
  - Unit runs as `User=zaks` with `ExecStart=/usr/bin/python3 -m email_triage_agent.run_once` (see `/etc/systemd/system/zakops-email-triage.service` via `systemctl cat`, Appendix).
- **Current**: Temporal schedule `zakops-email-triage-hourly` (paused=false) triggers a workflow which runs an activity that executes:
  - `python -m email_triage_agent.run_once` in cwd `/home/zaks/bookkeeping/scripts` (`scripts/temporal_worker/activities.py:11`).
  - Logs go to `/home/zaks/logs/temporal_worker/email_triage_*.log` (`scripts/temporal_worker/subprocess_runner.py:41`).

### 2) Email access (Gmail MCP stdio)

- Email 3H launches the Gmail MCP server as a **stdio child process** and speaks JSON-RPC:
  - process wrapper: `bookkeeping/scripts/email_triage_agent/mcp_stdio.py:24`
  - tool calls: `tools/call` (`bookkeeping/scripts/email_triage_agent/mcp_stdio.py:174`)
- Command selection:
  - `GMAIL_MCP_COMMAND` env override; otherwise defaults to `["npx", "-y", "@gongrzhe/server-gmail-autoauth-mcp"]` (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:255`).
- Credentials:
  - `GMAIL_MCP_CREDENTIALS_PATH` env override; otherwise `~/.gmail-mcp/credentials.json` (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:269`).
  - Exported to the MCP server as both `GMAIL_CREDENTIALS_PATH` and `GMAIL_MCP_CREDENTIALS_PATH` (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:281`).

### 3) Candidate selection / idempotency

- Gmail query default: `in:inbox -label:ZakOps/Processed newer_than:30d` (`bookkeeping/scripts/email_triage_agent/run_once.py:22`).
- The runner searches Gmail via MCP `search_emails(query, maxResults)` (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:201`).
- It skips message_ids that are already marked processed in the SQLite state DB:
  - DB: `DataRoom/.deal-registry/email_triage_state.db` (`bookkeeping/scripts/email_triage_agent/run_once.py:26`)
  - Table `email_triage_messages` (`bookkeeping/scripts/email_triage_agent/state_db.py:41`)
  - “processed” short-circuit: `run_once.py:877` and `run_once.py:329`.

### 4) Read + parse message + attachments list

- For each message_id, triage reads message details via MCP `read_email(messageId)` (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:206`).
- Parsing is text-based:
  - Extracted fields: `Thread ID`, `Subject`, `From`, `To`, `Date` (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:117`)
  - Attachments are parsed from a formatted “Attachments (N):” section (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:53`).
  - The email body is the raw block after headers (may contain full HTML) (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:149`).

### 5) Thread-aware routing (before classification)

- The runner loads deterministic thread mappings from the deal registry JSON (without importing DealRegistry):
  - `thread_to_deal` + `thread_to_non_deal` from `DataRoom/.deal-registry/deal_registry.json` (`bookkeeping/scripts/email_triage_agent/run_once.py:288`).
- If `thread_to_deal[thread_id]` exists:
  - it **does not create a quarantine review item**.
  - it creates `DEAL.APPEND_EMAIL_MATERIALS` (auto-approved + executed) (`bookkeeping/scripts/email_triage_agent/run_once.py:408`).
- If `thread_to_non_deal[thread_id]` exists:
  - it auto-labels NonDeal + Processed and stops (`bookkeeping/scripts/email_triage_agent/run_once.py:475`).

### 6) Classification (deterministic-first, optionally LLM)

- Deterministic classification builds entities + link types and scores deal-likeness (`bookkeeping/scripts/email_triage_agent/triage_logic.py:390`).
- If LLM mode is enabled:
  - In **assist** mode: LLM is only called when deterministic classification is `DEAL_SIGNAL` (`bookkeeping/scripts/email_triage_agent/run_once.py:515`).
  - In **full** mode: LLM is called for most non-newsletter/non-spam emails (`bookkeeping/scripts/email_triage_agent/run_once.py:518`).

### 7) Persist quarantine artifacts (deal-signal only)

- If final classification is `DEAL_SIGNAL`, Email 3H materializes a quarantine folder:
  - `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<message_id>/` (`bookkeeping/scripts/email_triage_agent/run_once.py:574`)
  - writes: `email_body.txt` + `email.json` (`bookkeeping/scripts/email_triage_agent/run_once.py:580`).
- If LLM result exists, it writes:
  - `triage_summary.json` + `triage_summary.md` (`bookkeeping/scripts/email_triage_agent/run_once.py:599`).

### 8) Create Quarantine review action (approval-gated)

- For final `DEAL_SIGNAL`, it creates a Kinetic Action:
  - type: `EMAIL_TRIAGE.REVIEW_EMAIL` (`bookkeeping/scripts/email_triage_agent/run_once.py:746`)
  - capability: `email_triage.review_email.v1` (`bookkeeping/scripts/email_triage_agent/run_once.py:750`)
  - inputs include `quarantine_dir` and `triage_summary_path` (`bookkeeping/scripts/email_triage_agent/run_once.py:770`).

### 9) Apply labels + mark processed

- Adds Gmail labels via MCP `modify_email(addLabelIds=...)` (`bookkeeping/scripts/email_triage_agent/gmail_mcp.py:225`).
- Always adds `ZakOps/Processed` after successful processing (`bookkeeping/scripts/email_triage_agent/run_once.py:779`).
- Records the decision in the triage state DB (`bookkeeping/scripts/email_triage_agent/state_db.py:79`).
- Writes an audit JSON (no raw bodies) to:
  - `DataRoom/.deal-registry/triage_outputs/<message_id>.json` (`bookkeeping/scripts/email_triage_agent/run_once.py:123`).

## Classification Logic (Decision System)

### Deterministic decision tree (source of truth)

All deterministic rules live in `bookkeeping/scripts/email_triage_agent/triage_logic.py`:

1) **Sender domain denylist (hard block)**:
   - `_SENDER_DOMAIN_DENYLIST` (`bookkeeping/scripts/email_triage_agent/triage_logic.py:33`)
   - If denylisted → classification returns `NEWSLETTER` (`bookkeeping/scripts/email_triage_agent/triage_logic.py:320`).

2) **Deal-score model** (`bookkeeping/scripts/email_triage_agent/triage_logic.py:328`):
   - Strong keyword hits (word-boundary matching): `score += 1.25 * len(strong_hits)` capped at 3.0 (`triage_logic.py:333`).
   - Weak keyword hits: `score += 0.5 * len(weak_hits)` capped at 1.5 (`triage_logic.py:338`).
   - Deal-link presence (link type in `{cim,teaser,dataroom,nda,financials,docs}`) adds +1.5 (`triage_logic.py:342`).
   - Attachments heuristic (`triage_logic.py:347`):
     - +0.25 for certain “deal-like” extensions (`triage_logic.py:352`)
     - +1.5 if filename contains any deal hint substring (`triage_logic.py:354`)
     - −2.0 if filename contains non-deal hint substring (`triage_logic.py:356`)
     - clamped to [-3, +3] (`triage_logic.py:358`).

3) **Final deterministic classification** (`triage_logic.py:365`):
   - spam hints → `SPAM`
   - newsletter hints + low score → `NEWSLETTER`
   - transactional hints + low score → `OPERATIONAL` (“transactional email” reason string)
   - else if `has_deal_links` OR `strong_hits` OR `score >= 2.0` → `DEAL_SIGNAL`
   - else → `OPERATIONAL` (`triage_logic.py:378`).

### LLM layer (local vLLM Qwen)

- Config: `bookkeeping/scripts/email_triage_agent/llm_triage.py:63`
  - default `EMAIL_TRIAGE_LLM_MODE=assist`
  - default model: `Qwen/Qwen2.5-32B-Instruct-AWQ` (`llm_triage.py:76`)
  - default base_url: `http://localhost:8000/v1` if no env override (`llm_triage.py:68`)
- Call: `POST {base_url}/chat/completions` via urllib (`bookkeeping/scripts/email_triage_agent/llm_triage.py:317`)
- Assist-mode override rules (`bookkeeping/scripts/email_triage_agent/run_once.py:559`):
  - Only allows LLM to **downgrade** a `DEAL_SIGNAL` → non-deal when `confidence >= 0.85`.
- Deterministic guardrails prevent LLM from overriding obvious denylist/transactional/spam (`run_once.py:564`).

## Routing to Quarantine (Exact Triggers)

### When a message lands in Quarantine (directory)

- Quarantine folder is created if **final classification is `DEAL_SIGNAL`**:
  - `quarantine_dir = cfg.quarantine_root / message.message_id` (`bookkeeping/scripts/email_triage_agent/run_once.py:574`)
  - writes `email_body.txt` + `email.json` (`run_once.py:580`)
  - writes `triage_summary.json`/`.md` when LLM result is present (`run_once.py:599`)
  - downloads allowlisted attachments; non-allowlisted attachments set a `quarantine_flag` (`run_once.py:685`).

### When a message becomes a Quarantine *review item* (action)

- A quarantine review item is created exactly when all are true (`run_once.py:715`):
  - `not dry_run`
  - `EMAIL_TRIAGE_ENABLE_ACTIONS=true`
  - Actions API reachable (`EMAIL_TRIAGE_ACTIONS_BASE_URL`, default `http://localhost:8090`)
  - `final_classification == "DEAL_SIGNAL"`
  - AND the thread was not pre-routed by `thread_to_deal`/`thread_to_non_deal`.

### What artifacts are “guaranteed” today

For a modern `DEAL_SIGNAL` run (non-dry-run):
- always: `email_body.txt`, `email.json` (`run_once.py:580`)
- if LLM ran (or fallback summary is written): `triage_summary.json`, `triage_summary.md` (`run_once.py:599`)
- if allowlisted attachments exist: they are downloaded into the same folder (`run_once.py:271`)

## Why Irrelevant Emails Enter Quarantine (Root Causes)

Below are the top observed causes, backed by real “false-positive” Quarantine review actions.

### Root Cause 1 — Keyword scoring includes raw HTML + URLs (noise → strong hits)

- Deterministic keyword scoring runs on `blob = f"{subject}\n{body_text}".lower()` (`triage_logic.py:318`).
- If the body is HTML-only, the blob includes CSS/URLs/tracking fragments, which can contain `cim`, `vdr`, `loi`, etc. (`triage_logic.py:333`).

**Evidence example**: Express marketing email (not a deal)
- Action: `ACT-20260101T220157-6de7820a` (subject “The PERFECT last-minute gift”)
- Summary shows strong deal keyword hits: `strong_keywords=['cim', 'vdr', 'loi']`
- Quarantine body is raw HTML (`DataRoom/00-PIPELINE/_INBOX_QUARANTINE/19b52fecfa8624c1/email_body.txt` starts with HTML)

### Root Cause 2 — Attachment filename substring heuristics can match random IDs

- Attachment deal hints use `if any(h in fname for h in _ATTACHMENT_DEAL_HINTS)` (`triage_logic.py:354`) and the hint list includes short tokens like `ltm`, `t12`, `ttm` (`triage_logic.py:260`).
- Many marketing/security emails include embedded images with opaque “attachment-<random>” filenames; random strings can accidentally contain these substrings.

**Evidence example**: Bitdefender welcome email (not a deal)
- Action: `ACT-20260103T021416-c5f966b5` (subject “Welcome to Bitdefender!”)
- Summary includes `attachments_score=+1.50` and `weak_keywords=['multiple']` (score hits the `>=2.0` threshold → `DEAL_SIGNAL`)
- Inputs show many attachments with random `attachment-ANG...` names (images) and no real deal docs.

### Root Cause 3 — Link typing can turn many links into “deal_links” via context

- `has_deal_links` becomes true if any link type is in `{cim,teaser,dataroom,nda,financials,docs}` (`triage_logic.py:342`).
- `_infer_link_type` checks **context** (subject/body) for NDA/CIM keywords (`triage_logic.py:131`), so an email mentioning “confidentiality” can cause unrelated links to be typed `nda`.

**Evidence example**: Account-activation emails
- `ACT-20260102T181350-b5772c2f` (“Your Account has been Activated”) links were typed as `nda` and counted as `deal_links`.
- `ACT-20260106T130122-753d4662` (“Upgrade Your Account for Instant Access”) shows the same pattern.

### Root Cause 4 — Denylist coverage is inherently incomplete (maintenance surface)

- The denylist is hard-coded (`triage_logic.py:33`) and relies on exact/parent-domain matches (`triage_logic.py:299`).
- When a marketing/newsletter domain is not present, keyword/URL noise can still classify it as `DEAL_SIGNAL`.

**Evidence example**: Legal newsletter mis-triaged
- `ACT-20260103T021344-79ebf8dc` from `newsletter.thelegalwire.ai` became `DEAL_SIGNAL` due to `strong_keywords=['nda']` + `deal_links`.
- (Note: this sender domain is currently present in `_SENDER_DOMAIN_DENYLIST`, indicating denylist expansion is one mitigation, not a complete solution.)

### Root Cause 5 — Assist-mode LLM is conservative (and can’t “save” every false positive)

- Assist mode only runs when deterministic classified `DEAL_SIGNAL` (`run_once.py:516`).
- Assist mode only downgrades when `confidence >= 0.85` (`run_once.py:561`).
- If the LLM is unavailable or returns lower confidence, the deterministic false positive remains a `DEAL_SIGNAL` and creates a review action.

## Configuration + Control Surface (What I can tune)

| Parameter | Default | Where set | What it does | Risk if changed |
|---|---:|---|---|---|
| `EMAIL_TRIAGE_QUERY` | `in:inbox -label:ZakOps/Processed newer_than:30d` | env or `run_once.py:22` | Which Gmail messages are considered | High: can miss messages or flood triage |
| `EMAIL_TRIAGE_MAX_PER_RUN` | `50` | env or `run_once.py:23` | Cap per run | Low |
| `EMAIL_TRIAGE_QUARANTINE_ROOT` | `DataRoom/00-PIPELINE/_INBOX_QUARANTINE` | env or `run_once.py:25` | Where artifacts land | Medium (paths/permissions) |
| `EMAIL_TRIAGE_STATE_DB` | `DataRoom/.deal-registry/email_triage_state.db` | env or `run_once.py:26` | Idempotency + status tracking | Medium |
| `EMAIL_TRIAGE_DEAL_REGISTRY_PATH` | `DataRoom/.deal-registry/deal_registry.json` | env or `run_once.py:28` | Thread routing source | Medium |
| `EMAIL_TRIAGE_ENABLE_ACTIONS` | `true` | env or `run_once.py:825` | Whether to create `EMAIL_TRIAGE.REVIEW_EMAIL` actions | High (disables quarantine workflow) |
| `EMAIL_TRIAGE_ACTIONS_BASE_URL` | `http://localhost:8090` | env or `run_once.py:27` | Where actions are created | Medium |
| `EMAIL_TRIAGE_DRY_RUN` | `false` | env or `run_once.py:819` | If true: no labels, no downloads, no actions | Low (but changes behavior) |
| `EMAIL_TRIAGE_MARK_AS_READ` | `false` | env or `run_once.py:820` | Mark as read after processing | Low |
| `EMAIL_TRIAGE_MAX_ATTACHMENT_MB` | `25` | env or `run_once.py:821` | Skip huge attachments | Low |
| `EMAIL_TRIAGE_SAFE_EXTS` | allowlist set | env or `run_once.py:31` | Which extensions can be downloaded | Medium |
| `EMAIL_TRIAGE_UNSAFE_EXTS` | blocklist set | env or `run_once.py:45` | Explicitly block risky types | Low |
| `EMAIL_TRIAGE_VENDOR_PATTERNS_MD` | vendor_patterns.md path | env or `run_once.py:815` | Link vendor classification source | Medium |
| `EMAIL_TRIAGE_LLM_MODE` | `assist` | env or `llm_triage.py:64` | `off|assist|full` | High (classification behavior) |
| `EMAIL_TRIAGE_LLM_BACKEND` | `llm_triage` | env or `run_once.py:510` | `llm_triage` vs `langgraph` | Medium |
| `EMAIL_TRIAGE_LLM_BASE_URL` | `http://localhost:8000/v1` | env or `llm_triage.py:68` | vLLM endpoint base URL | High (must stay local-only) |
| `EMAIL_TRIAGE_LLM_MODEL` | `Qwen/Qwen2.5-32B-Instruct-AWQ` | env or `llm_triage.py:76` | Model id | Medium |
| `EMAIL_TRIAGE_LLM_TIMEOUT_S` | `20` | env or `llm_triage.py:83` | LLM request timeout | Low |
| `EMAIL_TRIAGE_LLM_MAX_TOKENS` | `900` | env or `llm_triage.py:84` | LLM max_tokens | Medium (latency/cost) |
| `EMAIL_TRIAGE_LLM_MAX_BODY_CHARS` | `8000` | env or `llm_triage.py:85` | Body truncation before LLM | Medium (quality) |
| `GMAIL_MCP_COMMAND` | `npx -y @gongrzhe/server-gmail-autoauth-mcp` | env or `gmail_mcp.py:255` | Gmail MCP launch | Medium |
| `GMAIL_MCP_CREDENTIALS_PATH` | `~/.gmail-mcp/credentials.json` | env or `gmail_mcp.py:275` | Gmail OAuth creds location | High (must exist, permissions) |

**Restart semantics**
- Changes to env used by systemd units require `systemctl daemon-reload` + restart (if using systemd timers).
- Under Temporal, the worker process spawns `email_triage_agent.run_once`; env changes require restarting the Temporal worker **if you rely on its environment**, but the triage script itself reads env on each run.

## Observability & Debugging (What logs/events exist)

### Logs

- Legacy systemd logs (only if systemd timer is enabled):
  - `journalctl -u zakops-email-triage.service` (Appendix shows historical runs).
- Current Temporal-run logs:
  - `ls -lt /home/zaks/logs/temporal_worker/email_triage_*.log` (Appendix)
  - Each run logs `email_triage_run completed processed=...` (`run_once.py:900`).

### Stored artifacts / audit trail

- Per-message triage audit JSON (no bodies):
  - `DataRoom/.deal-registry/triage_outputs/<message_id>.json` (`run_once.py:140`)
  - Includes deterministic reason string + LLM config/result stub (`run_once.py:196`).
- Idempotency + processing status:
  - `DataRoom/.deal-registry/email_triage_state.db` (`state_db.py:41`).
- Quarantine folders:
  - `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/<message_id>/` (`run_once.py:574`)

### Known observability hazard (permissions)

- `DataRoom/.triage_stats.json` is written best-effort (errors suppressed) (`run_once.py:903`).
- In this environment it is currently `root:root` and not writable by `zaks`, so it can silently stop updating (evidence in Appendix).

## Recommendations (No implementation)

Ranked by expected impact on false positives while staying local-first and not touching downstream systems.

1) **Stop keyword scoring on raw HTML/URLs**
   - Extract/score on text-only (strip tags, remove URLs before `_word_match`) to prevent random token hits.
2) **Harden attachment filename heuristics**
   - Replace `h in fname` for short tokens with boundary-aware logic; ignore “attachment-<opaque>” patterns; remove ultra-short hints like `ltm/ttm/t12` or require nearby finance context.
3) **Introduce an explicit “PORTAL/ACCOUNT” classification**
   - Account activation / upgrade flows should not be treated as deal emails; they should create a different operator queue item (still approval-gated).
4) **Strengthen newsletter detection beyond denylist**
   - Use body indicators (`unsubscribe`, `view in browser`) as stronger blockers even when deal keywords exist, or require a minimum “deal evidence” set (e.g., one of: broker domain allowlist, CIM/teaser terms outside URLs/HTML, real financial figures).
5) **Tune LLM assist behavior for downgrade**
   - Consider lowering downgrade threshold or adding a deterministic “LLM second opinion” when evidence is weak (e.g., score barely ≥2.0) to reduce quarantine flood.
6) **Fix silent observability failures**
   - Ensure `DataRoom/.triage_stats.json` is writable by the triage runtime user and log failures instead of swallowing them.

## Appendix: Evidence (commands + outputs + code references)

### Trigger / schedule evidence

```bash
systemctl cat zakops-email-triage.service
systemctl cat zakops-email-triage.timer
systemctl status zakops-email-triage.timer --no-pager
```

Temporal schedule list:

```bash
/home/zaks/.venvs/zakops-orchestration/bin/python -m temporal_worker.schedules list
```

Code: Temporal runs triage via subprocess:
- `scripts/temporal_worker/activities.py:11`
- `scripts/temporal_worker/subprocess_runner.py:41`

### Gmail MCP wiring evidence

Code:
- `bookkeeping/scripts/email_triage_agent/gmail_mcp.py:255` (command)
- `bookkeeping/scripts/email_triage_agent/gmail_mcp.py:269` (credentials env)
- `bookkeeping/scripts/email_triage_agent/mcp_stdio.py:24` (stdio session)

### Example Quarantine artifacts (deal-signal)

Folder:
- `DataRoom/00-PIPELINE/_INBOX_QUARANTINE/19ba346c281df10e/`

Files:
- `email.json`
- `email_body.txt`
- `triage_summary.json`
- `triage_summary.md`

### Example Quarantine review action payload (Actions API)

```bash
curl -sS 'http://localhost:8090/api/actions/ACT-20260109T152828-34ea867c' | jq .
```

Action creation code:
- `bookkeeping/scripts/email_triage_agent/run_once.py:714`

### False-positive examples (evidence)

```bash
curl -sS 'http://localhost:8090/api/actions/ACT-20260101T220157-6de7820a' | jq '{action_id,status,summary,inputs:{from:.inputs.from,subject:.inputs.subject,quarantine_dir:.inputs.quarantine_dir}}'
curl -sS 'http://localhost:8090/api/actions/ACT-20260103T021416-c5f966b5' | jq '{action_id,status,summary,inputs:{from:.inputs.from,subject:.inputs.subject,attachments:.inputs.attachments}}'
curl -sS 'http://localhost:8090/api/actions/ACT-20260103T021344-79ebf8dc' | jq '{action_id,status,summary,inputs:{from:.inputs.from,subject:.inputs.subject,links:.inputs.links}}'
curl -sS 'http://localhost:8090/api/actions/ACT-20260102T181350-b5772c2f' | jq '{action_id,status,summary,inputs:{from:.inputs.from,subject:.inputs.subject,links:.inputs.links}}'
curl -sS 'http://localhost:8090/api/actions/ACT-20260106T130122-753d4662' | jq '{action_id,status,summary,inputs:{from:.inputs.from,subject:.inputs.subject,links:.inputs.links}}'
```

Key decision points in code:
- scoring + threshold: `bookkeeping/scripts/email_triage_agent/triage_logic.py:328`
- attachment substring hints: `bookkeeping/scripts/email_triage_agent/triage_logic.py:349`
- URL extraction: `bookkeeping/scripts/email_triage_agent/triage_logic.py:98`
- deal_links: `bookkeeping/scripts/email_triage_agent/triage_logic.py:342`

### Local vLLM evidence (model)

```bash
curl -sS http://localhost:8000/v1/models | jq '{count: (.data|length), first: .data[0]}'
```

LLM config defaults:
- `bookkeeping/scripts/email_triage_agent/llm_triage.py:63`

### Observability hazard evidence

```bash
ls -la /home/zaks/DataRoom/.triage_stats.json
cat /home/zaks/DataRoom/.triage_stats.json | jq .
```

