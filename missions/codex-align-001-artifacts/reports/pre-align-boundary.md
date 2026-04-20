# Pre-Align Boundary Snapshot — CODEX-ALIGN-001
## Date: 2026-02-12

## Files That Will Be Modified
| Path | Current State | Planned Change |
|------|--------------|----------------|
| `/home/zaks/.codex/config.toml` | 30 lines, 2 profiles | Expand: notify, 5 profiles, 3 trust entries, history |
| `/home/zaks/.codex/rules/default.rules` | 5 ad-hoc rules | Replace: ~30 structured rules |
| `/home/zaks/.codex/CODEX_INSTRUCTIONS.md` | 94 lines | Add superseded header (content preserved) |
| `/home/zaks/.bashrc` | No codex entries | Add PATH + alias |
| `/home/zaks/bookkeeping/CHANGES.md` | Existing log | Append mission entry |
| `/root/.claude/projects/-home-zaks/memory/MEMORY.md` | ~200 lines | Append completion entry |

## Files That Will Be Created
| Path | Phase |
|------|-------|
| `/home/zaks/.codex/AGENTS.md` | 1 |
| `/home/zaks/zakops-agent-api/.agents/AGENTS.md` | 1 |
| `/home/zaks/zakops-backend/.agents/AGENTS.md` | 1 |
| 19 skill dirs under `~/.codex/skills/` | 2 |
| 7 skill dirs under `zakops-agent-api/.agents/skills/` | 2 |
| `/home/zaks/scripts/codex-boot.sh` | 5 |
| `/home/zaks/scripts/codex-stop.sh` | 5 |
| `/home/zaks/scripts/codex-notify.sh` | 5 |
| `/home/zaks/scripts/codex-wrapper.sh` | 5 |

## Backup Anchors
- config.toml original: captured in baseline-inventory.md
- rules original: captured in baseline-inventory.md (5 rules)
- CODEX_INSTRUCTIONS.md: 94 lines, content preserved via superseded-header approach
