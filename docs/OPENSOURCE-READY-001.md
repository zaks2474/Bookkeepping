# MISSION: OPENSOURCE-READY-001
## Make ZakOps Monorepo Contributor-Ready and Open-Source
## Date: 2026-02-24
## Classification: Platform Transformation — Repository Governance & Developer Experience (L)
## Prerequisite: TRIAGE-BRIDGE-ALIGN-001 (complete)
## Successor: QA-OSR-VERIFY-001

---

## Context

Zak is the sole developer on ZakOps. His W2 job limits available time. The project is production-grade but contributor-hostile: proprietary license, no community infrastructure, GPU required to run. This mission transforms the repo so experienced full-stack devs can discover, set up, and contribute independently while Zak reviews PRs in batches.

**Current state:** 6.2/10 contributor readiness. **Target:** 8.5/10.

**Key decisions (confirmed with user):**
- License: **MIT** (replacing proprietary)
- Target contributors: **Experienced full-stack devs** (FastAPI + Next.js + Docker)
- Mock mode: **Yes** — `DEMO_MODE=true` so contributors can run without GPU/vLLM/RAG

---

## Architectural Constraints

1. **Generated files never edited** — `*.generated.ts`, `*_models.py` protected by hooks
2. **No new external dependencies for mock mode** — use only `langchain_core` (already in deps)
3. **Existing code paths unchanged** — demo mode is additive, never modifies production behavior
4. **Port 8090 FORBIDDEN** — no references in any new docs
5. **Secrets never committed** — all examples use placeholder values
6. **WSL safety** — `sed -i 's/\r$//'` on .sh files, `chown zaks:zaks` on files under `/home/zaks/`
7. **Contributor-facing docs use repo-relative paths only** — no `/home/zaks/` paths

---

## Anti-Pattern Examples

**WRONG:** Mock that silently catches errors
```python
try: return await real_llm(msg)
except: return {"content": "Mock"}  # Hides bugs
```

**RIGHT:** Mock as explicit named code path
```python
if settings.DEMO_MODE:
    return MockLLMProvider().generate(messages)
return RealLLMProvider().generate(messages)
```

---

## Pre-Mortem

| Risk | Mitigation |
|------|-----------|
| DEMO_MODE env set but app never reads it (existing demo compose bug) | Phase 3 implements actual mock providers with tests |
| Secrets accidentally committed in new docs | Phase 0 secret scan; all examples use `your-xxx-here` |
| New .sh files with CRLF break on first contributor use | WSL checklist in every gate |
| Docs reference `/home/zaks/` — meaningless to contributors | Phase 6 scan: `grep -r "/home/zaks/" <contributor docs>` must return 0 |
| Mock LLM requires new pip dependency | Constraint: use only langchain_core FakeListChatModel (already available) |

---

## Phase 0 — Baseline Verification
**Complexity:** S | **Blast radius:** None (read-only)

- P0-01: `make validate-local` — capture baseline (must pass)
- P0-02: Secret scan — `grep -r` for real credential patterns in tracked files
- P0-03: Verify demo compose syntax: `docker compose -f deployments/demo/compose.demo.yml config`
- P0-04: Identify affected surfaces: **Surface 11** (Env Registry — DEMO_MODE)

**Gate P0:** validate-local PASS, no secrets in tracked files, surfaces identified

---

## Phase 1 — Repository Hygiene (Legal + Structure)
**Complexity:** M | **Blast radius:** GitHub UI only, no services

**Files to create:**
| File | Purpose |
|------|---------|
| `LICENSE` | Overwrite with MIT License (copyright 2025-2026 ZakOps Contributors) |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1, contact: dev@zakops.io |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug report: description, steps, expected, environment |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Feature: problem, solution, alternatives |
| `.github/ISSUE_TEMPLATE/config.yml` | Link "Ask a question" to Discussions |
| `.github/PULL_REQUEST_TEMPLATE.md` | Checklist: description, type, tests, `make validate-local` |

**Files to modify:**
| File | Change |
|------|--------|
| `README.md` | Update license reference from "Proprietary" to "MIT" |

**Gate P1:**
- LICENSE contains "MIT License"
- CODE_OF_CONDUCT.md exists with "Contributor Covenant"
- `.github/ISSUE_TEMPLATE/` has 3 files
- `.github/PULL_REQUEST_TEMPLATE.md` exists
- `make validate-local` PASS

---

## Phase 2 — Developer Onboarding Documentation
**Complexity:** L | **Blast radius:** Documentation only

**Files to create/rewrite:**
| File | What |
|------|------|
| `README.md` | **Complete rewrite**: value prop, badges, 5-min quickstart (demo mode default), architecture overview, services table, prerequisites, contributing link, MIT license |
| `CONTRIBUTING.md` | **Expand to ~150 lines**: fork workflow, contract surface overview, required gates (`make lint`, `make test`, `make validate-local`), demo mode dev, code style, commit convention, PR review SLA (24-48h batches) |
| `docs/GETTING-STARTED.md` | **New ~200 lines**: prerequisites checklist, step-by-step setup, demo mode section, full stack section, troubleshooting (token mismatch, port conflicts, CRLF) |
| `docs/ROADMAP.md` | Current capabilities, short/medium/long-term goals, how to propose features |
| `CONTRIBUTORS.md` | Initial entry: Zak (@zaks2474), instructions for adding names |

**Key constraint:** NO `/home/zaks/` paths in any of these files. All paths repo-relative.

**Gate P2:**
- README has "Quick Start" with demo mode
- CONTRIBUTING mentions `make validate-local` and `make sync-types`
- docs/GETTING-STARTED.md has "Demo Mode" section
- docs/ROADMAP.md exists
- `grep -r "/home/zaks/" README.md CONTRIBUTING.md CONTRIBUTORS.md docs/GETTING-STARTED.md docs/ROADMAP.md` returns 0
- `make validate-local` PASS

---

## Phase 3 — Demo/Mock Mode Implementation
**Complexity:** L | **Blast radius:** agent-api (mock providers), .env.example files, Makefile

This is the only phase with real code changes. The demo compose at `deployments/demo/compose.demo.yml` already sets `DEMO_MODE=true` and `LLM_MOCK_MODE=true` but the application never reads them.

**Integration points (verified):**
- `apps/agent-api/app/core/config.py` line 121: `Settings.__init__()` — add `self.DEMO_MODE`
- `apps/agent-api/app/services/llm.py` line 40: `_create_llm_instance()` — when DEMO_MODE, use `FakeListChatModel` from `langchain_core.language_models`
- `apps/agent-api/app/services/llm.py` line 91: `LLMRegistry._init_llms()` — when DEMO_MODE, register mock model instead of vLLM/OpenAI
- `apps/agent-api/app/services/rag_rest.py` line 20: RAG client — when DEMO_MODE, return mock `RetrievalResult` objects

**Files to create:**
| File | Purpose |
|------|---------|
| `apps/agent-api/app/services/mock_llm.py` | Mock LLM using `FakeListChatModel` (no new deps) |
| `apps/agent-api/app/services/mock_rag.py` | Mock RAG returning sample `RetrievalResult` objects |
| `apps/agent-api/tests/test_mock_providers.py` | Tests: mock LLM returns AIMessage, mock RAG returns RetrievalResult |

**Files to modify:**
| File | Change |
|------|--------|
| `apps/agent-api/app/core/config.py` | Add `self.DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")` |
| `apps/agent-api/app/services/llm.py` | If `settings.DEMO_MODE`: register mock model in `LLMRegistry._init_llms()` |
| `apps/agent-api/app/services/rag_rest.py` | If `settings.DEMO_MODE`: return mock results instead of HTTP call |
| `.env.example` | Add `DEMO_MODE=false` with comment |
| `apps/agent-api/.env.example` | Add `DEMO_MODE=false` |
| `apps/backend/.env.example` | Add `DEMO_MODE=false` |
| `apps/dashboard/.env.example` | Add `DEMO_MODE=false` |
| `Makefile` | Add `bootstrap` target: `bootstrap-docker` + `install` + copy .env.example → .env |
| `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md` | Register DEMO_MODE in Surface 11 |

**Gate P3:**
- `grep DEMO_MODE apps/agent-api/app/core/config.py` shows the setting
- Mock tests pass: `cd apps/agent-api && uv run pytest tests/test_mock_providers.py -v`
- All 4 `.env.example` files contain DEMO_MODE
- `make bootstrap` runs without error
- DEMO_MODE in ENV-CROSSREF.md
- `make validate-local` PASS
- `make validate-surface11` PASS
- No new external dependencies added

---

## Phase 4 — GitHub Community Infrastructure
**Complexity:** M | **Blast radius:** GitHub metadata only

**Files to create:**
| File | Purpose |
|------|---------|
| `.github/ISSUE_TEMPLATE/rfc.md` | RFC template for architecture proposals |
| `.github/FUNDING.yml` | GitHub Sponsors config (commented out, ready to enable) |
| `.github/labels.yml` | 15+ label definitions for github-label-sync |
| `docs/STARTER-ISSUES.md` | 15-20 issue descriptions across 3 difficulty levels |

**Starter issues breakdown:**
- **good-first-issue (6):** unit test additions, docstring improvements, error message improvements, UI loading states, input validation, dark mode CSS variables
- **help-wanted (6):** chat pagination, deal search/filter, API docs theme, WebSocket real-time updates, CSV export, rate limit headers
- **architecture (4):** multi-tenant isolation, plugin system, event sourcing, alternative LLM backends

**Gate P4:**
- `.github/ISSUE_TEMPLATE/rfc.md` exists
- `.github/labels.yml` has 15+ labels
- `docs/STARTER-ISSUES.md` has 15+ issues across 3 difficulty tiers
- `make validate-local` PASS

---

## Phase 5 — Contributor Recruitment & Async Workflow
**Complexity:** M | **Blast radius:** Documentation only

**Files to create:**
| File | Purpose |
|------|---------|
| `docs/RECRUITING.md` | Community-specific post templates: Reddit (r/opensource, r/FastAPI, r/nextjs, r/SideProject), Dev.to article outline, Discord targets, Twitter thread template |
| `docs/ASYNC-WORKFLOW.md` | How async contribution works: PR review SLA (24-48h), issue claiming, branch naming, what makes a good PR, discussion vs issue vs PR |

**Files to modify:**
| File | Change |
|------|--------|
| `.github/CODEOWNERS` | Add comments for maintainer expansion path |

**Gate P5:**
- docs/RECRUITING.md exists with 4+ community templates
- docs/ASYNC-WORKFLOW.md exists with PR review SLA
- CODEOWNERS has expansion path comment
- `make validate-local` PASS

---

## Phase 6 — Final Verification & Bookkeeping
**Complexity:** S | **Blast radius:** None

- P6-01: `make validate-local` — final pass
- P6-02: `make validate-surface11` — DEMO_MODE registered
- P6-03: Mock tests pass
- P6-04: CRLF scan on any new .sh files
- P6-05: Path scan: no `/home/zaks/` in contributor-facing docs
- P6-06: Secret scan: no real credentials in any new files
- P6-07: Update `/home/zaks/bookkeeping/CHANGES.md`
- P6-08: Produce completion report

**Gate P6:** All checks pass, CHANGES.md updated, completion report written

---

## Dependency Graph

```
P0 (Baseline)
 └─► P1 (Repo Hygiene) ──► P2 (Onboarding Docs) ──► P3 (Demo Mode)
                                                       └─► P4 (Community Infra) ─┐
                                                       └─► P5 (Recruitment)  ─────┤
                                                                                   ▼
                                                                           P6 (Verification)
```
P1 → P2 → P3 are sequential. P4 and P5 can run in parallel after P3. P6 is final.

---

## Acceptance Criteria

| AC | Description | Phase |
|----|-------------|-------|
| AC-1 | LICENSE is MIT | P1 |
| AC-2 | CODE_OF_CONDUCT, expanded CONTRIBUTING, SECURITY all present | P1, P2 |
| AC-3 | GitHub issue templates (3) + PR template exist | P1 |
| AC-4 | README has 5-min quickstart with demo mode as default path | P2 |
| AC-5 | docs/GETTING-STARTED.md (200+ lines) with demo mode and troubleshooting | P2 |
| AC-6 | DEMO_MODE=true activates mock LLM + mock RAG in agent-api. Tests pass. | P3 |
| AC-7 | `make bootstrap` exists: creates volumes, copies .env, installs deps | P3 |
| AC-8 | Surface 11 updated with DEMO_MODE, `make validate-surface11` PASS | P3 |
| AC-9 | docs/STARTER-ISSUES.md has 15+ issues across 3 difficulty levels | P4 |
| AC-10 | docs/RECRUITING.md has 4+ community-specific post templates | P5 |
| AC-11 | docs/ASYNC-WORKFLOW.md documents PR review SLA and async contribution model | P5 |
| AC-12 | `make validate-local` PASS, no regressions, no secrets, no CRLF, no `/home/zaks/` in contributor docs | P6 |
| AC-13 | CHANGES.md updated | P6 |

---

## Guardrails

1. **Scope fence:** Do NOT refactor existing application code. Demo mode is additive only.
2. **No new external dependencies** for mock mode — use `langchain_core.language_models.fake.FakeListChatModel`
3. **Generated file protection** — `*.generated.ts`, `*_models.py` never touched
4. **Port 8090 FORBIDDEN** in all new docs
5. **Secrets never committed** — all `.env.example` use placeholders
6. **WSL safety** on all new .sh files
7. **Internal docs unchanged** — `agent.md`, `CLAUDE.md`, `GEMINI.md`, bookkeeping stay internal
8. **Contributor docs are repo-relative** — no absolute paths

---

## Executor Self-Check Prompts

**After Phase 0:** Did validate-local pass? Did secret scan find anything?
**After every code change:** Any new .sh files? CRLF stripped? Any `/home/zaks/` in contributor docs? Any new env var not in Surface 11?
**Before Phase 3 complete:** Do mock providers use only existing deps? Do tests pass?
**Before mission complete:** Does `make validate-local` pass? Does `make validate-surface11` pass? Is CHANGES.md updated?

---

## Manual Steps (Zak must do in GitHub UI after mission completes)

1. Set repo visibility to **Public** (Settings > Danger Zone)
2. Add GitHub Topics: `agentic-ai`, `langchain`, `fastapi`, `nextjs`, `mcp`, `deal-management`
3. Enable **GitHub Discussions** (Settings > Features)
4. Set **branch protection** on `main`: require CI pass + 1 review
5. Create **GitHub labels** from `.github/labels.yml`
6. Create **15-20 GitHub issues** from `docs/STARTER-ISSUES.md`
7. Create **GitHub Project board**: Backlog → Ready → In Progress → Review → Done
8. **Rotate secrets** that may have been in git history before making public
9. Post recruitment content from `docs/RECRUITING.md` to communities

---

## Files Reference

### Files to Modify (15)
| File | Phase |
|------|-------|
| `LICENSE` | P1 |
| `README.md` | P1, P2 |
| `CONTRIBUTING.md` | P2 |
| `apps/agent-api/app/core/config.py` | P3 |
| `apps/agent-api/app/services/llm.py` | P3 |
| `apps/agent-api/app/services/rag_rest.py` | P3 |
| `.env.example` | P3 |
| `apps/agent-api/.env.example` | P3 |
| `apps/backend/.env.example` | P3 |
| `apps/dashboard/.env.example` | P3 |
| `Makefile` | P3 |
| `/home/zaks/bookkeeping/docs/ENV-CROSSREF.md` | P3 |
| `.github/CODEOWNERS` | P5 |
| `/home/zaks/bookkeeping/CHANGES.md` | P6 |

### Files to Create (18)
| File | Phase |
|------|-------|
| `CODE_OF_CONDUCT.md` | P1 |
| `.github/ISSUE_TEMPLATE/bug_report.md` | P1 |
| `.github/ISSUE_TEMPLATE/feature_request.md` | P1 |
| `.github/ISSUE_TEMPLATE/config.yml` | P1 |
| `.github/PULL_REQUEST_TEMPLATE.md` | P1 |
| `docs/GETTING-STARTED.md` | P2 |
| `docs/ROADMAP.md` | P2 |
| `CONTRIBUTORS.md` | P2 |
| `apps/agent-api/app/services/mock_llm.py` | P3 |
| `apps/agent-api/app/services/mock_rag.py` | P3 |
| `apps/agent-api/tests/test_mock_providers.py` | P3 |
| `.github/ISSUE_TEMPLATE/rfc.md` | P4 |
| `.github/FUNDING.yml` | P4 |
| `.github/labels.yml` | P4 |
| `docs/STARTER-ISSUES.md` | P4 |
| `docs/RECRUITING.md` | P5 |
| `docs/ASYNC-WORKFLOW.md` | P5 |

### Files to Read (reference only)
| File | Purpose |
|------|---------|
| `docs/ARCHITECTURE.md` | Architecture reference for README |
| `apps/agent-api/app/services/llm.py` | LLM service integration point |
| `apps/agent-api/app/services/rag_rest.py` | RAG client integration point |
| `deployments/demo/compose.demo.yml` | Existing demo compose reference |
| `.github/workflows/ci.yml` | CI reference for contributor docs |

---

## Stop Condition

DONE when all 13 AC pass, `make validate-local` PASS, `make validate-surface11` PASS, all changes committed on `feature/opensource-ready`, completion report produced, CHANGES.md updated. Zak then executes manual steps (make public, create issues, post to communities).
