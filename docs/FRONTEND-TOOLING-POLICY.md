# Frontend Tooling Policy

**Effective:** 2026-02-10
**Scope:** Claude Code sessions performing dashboard/frontend work
**Owner:** ZakOps infrastructure

---

## 1. Frontend-Design Skill

### Status: INSTALLED (local skill)

**Location:** `/home/zaks/.claude/skills/frontend-design/SKILL.md`

### Usage Policy
- The `design-system.md` path-scoped rule includes a Skill Preloads section referencing this skill
- When starting component design work (new components, visual redesigns, layout changes), read the skill before implementation
- The skill provides aesthetic guidance beyond what the design-system rule covers (tone palette, anti-convergence, texture techniques)
- The skill complements project rules — it does not override Category A architectural conventions

### When to Use
| Task Type | Use Skill? |
|-----------|-----------|
| New page or component | Yes — read before designing |
| Bug fix (logic, data) | No — unnecessary |
| Styling/theming change | Yes — especially for tone/variation guidance |
| Refactoring (no visual change) | No — unnecessary |

---

## 2. Playwright MCP

### Status: DISABLED

**Config:** `/home/zaks/.claude/settings.json` → `mcpServers.playwright.disabled: true`

### Rationale for Disabled State
1. Visual verification is not currently part of the automated validation pipeline
2. Playwright MCP adds startup latency to every Claude Code session (~3-5s)
3. Dashboard E2E tests exist independently (52 tests via the test suite) and do not require MCP integration
4. Enabling Playwright MCP introduces network and browser-process dependencies that can cause session instability in WSL

### How to Enable (when needed)
1. Edit `/home/zaks/.claude/settings.json`
2. Change `"disabled": true` to `"disabled": false` under `mcpServers.playwright`
3. Restart Claude Code session
4. Playwright tools (`browser_navigate`, `browser_screenshot`, etc.) become available

### When to Enable
- Visual regression testing during major UI redesigns
- Debugging layout issues that require screenshot comparison
- Accessibility audits requiring rendered DOM inspection

### Constraints When Enabled
- Do not leave Playwright MCP enabled permanently — disable after completing visual verification tasks
- Screenshots and browser state are ephemeral — do not rely on them for evidence artifacts
- Playwright commands add latency; avoid in tight feedback loops

---

## 3. Verification Expectations by Change Type

| Change Type | Required Verification | Optional Verification |
|-------------|----------------------|----------------------|
| Component logic/data fix | `make validate-local`, `npx tsc --noEmit` | Unit tests |
| New component | `make validate-local`, `make validate-surface9` | E2E test, Playwright screenshot |
| Styling/CSS change | `make validate-local`, manual browser check | Playwright screenshot comparison |
| Design system rule change | `make validate-surface9`, `make validate-contract-surfaces` | — |
| API type change | `make sync-types`, `npx tsc --noEmit`, `make validate-local` | — |
| Accessibility improvement | `make validate-local` | Playwright + screen reader testing |

---

## 4. Path-Scoped Rule Coverage

When editing dashboard files, these rules auto-load based on glob patterns:

| Rule | Triggers On | Purpose |
|------|------------|---------|
| `design-system.md` | components, app, styles | Architectural + design quality + operational governance |
| `dashboard-types.md` | types, lib, components, hooks | Import discipline + type handling |
| `accessibility.md` | components, app, styles, hooks | WCAG, keyboard nav, contrast, ARIA |
| `component-patterns.md` | components, app, hooks | Server/client split, loading/error states, composition |

---

*Policy established by FRONTEND-GOVERNANCE-HARDENING-001*
