# P3 — Settings Internal Consistency Audit

## Shared Wrapper: `SettingsSectionCard.tsx`
All 6 sections use the same wrapper providing:
- `<Card>` → `<CardHeader>` (icon in `p-2 rounded-lg bg-primary/10 text-primary`, title `text-lg`, description) → `<CardContent className="space-y-6">` → optional footer with Save/Reset buttons.
- Consistent save status indicator (saving/saved/error).

## Internal Container Pattern Matrix

### Toggle Items (Switch controls)
| Section | Classes | Notes |
|---------|---------|-------|
| Agent (Enable toggle) | `p-4 rounded-lg border` | ✓ |
| Notifications (Email) | `p-4 rounded-lg border` | ✓ |
| Notifications (In-App) | `p-4 rounded-lg border` | ✓ |
| Notifications (Deal Stage) | `p-4 rounded-lg border` | ✓ |
| Notifications (Agent Activity) | `p-4 rounded-lg border` | ✓ |
| Notifications (Quiet Hours) | `p-4 rounded-lg border` | ✓ |
| Appearance (Sidebar Collapsed) | `p-4 rounded-lg border` | ✓ |
| Appearance (Dense Mode) | `p-4 rounded-lg border` | ✓ |
| Email (TLS) | `p-3 rounded-lg border` | Minor: p-3 (nested context) |

**Verdict:** Consistent. The p-3 on Email TLS is intentional — it's inside a nested IMAP configuration form, so reduced padding is contextually appropriate.

### Selection Items (Radio/Click)
| Section | Classes | Active State |
|---------|---------|-------------|
| Provider (provider cards) | `p-4 rounded-lg border cursor-pointer transition-colors` | `border-primary bg-primary/5` |
| Agent (approval options) | `p-4 rounded-lg border cursor-pointer transition-colors` | `border-primary bg-primary/5` |
| Notifications (digest) | `p-3 rounded-lg border cursor-pointer transition-colors` | `border-primary bg-primary/5` |
| Email (provider buttons) | `p-4 rounded-lg border-2 transition-all` | `border-primary bg-primary/5` |
| Appearance (theme buttons) | `p-4 rounded-lg border-2 transition-all duration-200` | `border-primary bg-primary/5` |

**Verdict:** Consistent active state pattern (`border-primary bg-primary/5`). Minor variations:
- Email/Appearance use `border-2` (emphasis for primary selection grids) vs `border` for inline radios — intentional visual hierarchy.
- Notifications digest uses `p-3` vs `p-4` — fits more compact radio layout, acceptable.

### Nested Radio Items (inside a parent border container)
| Section | Classes | Active State |
|---------|---------|-------------|
| Notifications (approval alerts) | `p-2 rounded-md` (inside `p-4 rounded-lg border`) | `bg-primary/10` |

**Verdict:** Consistent — nested items intentionally use smaller padding and `rounded-md` instead of `rounded-lg`.

### Info/Callout Boxes
| Section | Classes |
|---------|---------|
| Provider (Architecture Note) | `bg-muted/50 rounded-lg p-4` |
| Agent (Risk Levels) | `bg-muted/50 rounded-lg p-4 space-y-3` |

**Verdict:** Identical pattern.

### Nested Config Card
| Section | Classes |
|---------|---------|
| Provider (Active Provider Config) | `<Card className="bg-muted/30">` with CardHeader/CardContent |

**Verdict:** Unique to Provider — appropriate because it wraps dynamic provider-specific form fields. Uses Card component for structural hierarchy.

### Danger Zone
| Section | Classes |
|---------|---------|
| Data (Delete Account) | `rounded-lg border-2 border-destructive/30 bg-destructive/5 p-5 space-y-3` |

**Verdict:** Unique to Data section — appropriate for destructive action prominence.

## Overall Consistency Assessment

| Pattern | Consistent? | Variance |
|---------|-------------|----------|
| Outer wrapper (SettingsSectionCard) | ✅ Yes | None — all 6 sections use it |
| Toggle items | ✅ Yes | 1 instance of p-3 (nested context) |
| Selection items | ✅ Yes | border-2 for grid selectors vs border for inline — intentional |
| Active states | ✅ Yes | All use `border-primary bg-primary/5` |
| Info boxes | ✅ Yes | Same `bg-muted/50 rounded-lg p-4` |
| Danger zone | ✅ N/A | Unique, contextually correct |

## Conclusion

**No normalization required.** All 6 settings sections follow a consistent internal container pattern. Minor padding/border-width variations (p-3 vs p-4, border vs border-2) are contextually appropriate and do not produce visual inconsistency. The `SettingsSectionCard` wrapper ensures uniform outer structure.
