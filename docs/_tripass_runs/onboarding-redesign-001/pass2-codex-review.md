1. **(Race/Resume)** “Welcome → Profile: no API call” means the backend can still think `current_step=0`; if the user leaves mid-Profile they’ll resume at Welcome. Fix by creating/updating the row when the wizard opens and persisting `current_step` on *every* step change (or at least on 0→1).

2. **(Missing flow)** You have a `skipped` column but no endpoint/transition that ever sets it. Decide how “Skip Setup” should work (hide banner permanently vs keep reminding) and add `POST /api/onboarding/skip` (or fold it into a unified PATCH).

3. **(API gap)** Email step completion is undefined for the “connect” path; `POST /email-skipped` only covers skipping. Either infer “email completed” from the email-config record’s existence, or add an explicit “email completed” update that also advances `current_step`.

4. **(State machine drift)** If `current_step` is only advanced on `/profile`, `/email-skipped`, `/complete`, back/forward navigation and partial progress can desync backend from UI. Treat backend as the state machine: every transition updates step + returns canonical state.

5. **(Double-submit)** All POST endpoints must be idempotent under retries/double-clicks. Use UPSERT on `user_id`, disable CTA buttons while pending, and optionally send `X-Idempotency-Key` per transition.

6. **(Multi-tab race)** Two tabs can “fight” over `current_step` and banner visibility. Mitigate with monotonic step advancement server-side (don’t decrease except on `/reset`), plus `updated_at` conflict rules and refetch-on-focus in React Query.

7. **(Schema constraints)** Add DB checks to prevent impossible combos: `current_step` in `[0..3]`, `completed XOR skipped`, `completed_at IS NOT NULL ⇔ completed=true`, and `email_skipped` only allowed once the email step is reached.

8. **(Redundant columns)** `completed` duplicates `completed_at IS NOT NULL` (and `skipped` likely wants a `skipped_at`). Pick one source of truth or enforce consistency via constraints/triggers.

9. **(Future-proofing)** Integer `current_step` is brittle when steps change. Prefer `current_step_id` (enum/text) + `flow_version` so future reorder/add/remove doesn’t corrupt existing rows.

10. **(Normalization)** Profile fields inside `onboarding_state` will become “the profile DB” unless you also have a real user profile/account table. Decide the canonical home for profile and avoid duplicating between onboarding + Settings.

11. **(Downstream breakage)** Anything currently reading profile from `zakops-onboarding-progress` localStorage (e.g., avatar initials / user menu) will go blank after migration unless updated to read from backend (via `/status` or a profile endpoint).

12. **(Migration safety)** Never clear localStorage until the backend write succeeds (2xx). If backend is down or returns non-2xx, keep localStorage and retry later—otherwise users lose progress irreversibly.

13. **(Migration mapping)** Spec needs an explicit mapping from old 6-step state to new 4-step (especially old Preferences/Complete). Without this, previously “complete” users can regress and see the banner again.

14. **(Skip/complete migration)** Define precedence when localStorage has `complete=true` or `skipped=true`. If “skipped” currently suppresses gating, persist that to backend so UX doesn’t change unexpectedly.

15. **(Migration conflict resolution)** If a backend row already exists (another browser/device), migrating stale localStorage can overwrite newer data. Compare localStorage `lastUpdated` vs backend `updated_at` and choose a deterministic winner.

16. **(Migration races)** “First load” migration can run concurrently (multiple components/tabs). Add a persistent flag (e.g., `zakops-onboarding-migrated-v2`) + in-flight lock to avoid duplicate POSTs and premature clears.

17. **(Backend unavailable)** Banner-on-all-pages means frequent `/status` calls; define behavior on 502/timeout (hide banner vs “status unavailable”) and tune React Query `retry`, `staleTime`, and `refetchOnWindowFocus` to avoid request storms.

18. **(API contract)** Every mutation should return the same `OnboardingStatus` shape as GET `/status` so the client can `setQueryData` and avoid refetch races/banner flashes.

19. **(REST surface area)** These are mostly “update onboarding state” operations; consider consolidating to `GET /api/onboarding` + `PATCH /api/onboarding` + `POST /api/onboarding/reset` to reduce edge cases and keep semantics clear.

20. **(Validation)** Specify required vs optional profile fields and enforce max lengths + timezone validity (IANA names). Return 422 with field-level errors so the UI can render inline validation.

21. **(Stored XSS)** Profile strings (name/company/role) will be displayed; ensure they’re always treated as plain text (no raw HTML rendering) and consider stripping control characters server-side.

22. **(SessionStorage security)** “Draft form values in sessionStorage” can be dangerous on Email Setup—be explicit that secrets (passwords, OAuth tokens, connection strings) are never stored in web storage.

23. **(Auth/CSRF)** With `user_id='default'`, anyone who can reach the dashboard can hit `/api/onboarding/*`. If the dashboard is ever exposed beyond localhost, add auth + CSRF protection for write endpoints (especially `/reset`).

24. **(Reset semantics)** Define whether `/reset` wipes profile fields or only progress. Many users want “rerun onboarding” without losing account/profile data; consider separate “reset progress” vs “clear profile”.

25. **(Resume entrypoint)** Spec doesn’t say how users resume at the right step: banner CTA should open `/onboarding`, and the wizard must initialize from backend `current_step` (not sessionStorage defaults).

26. **(Banner UX)** Hide the banner on `/onboarding` itself and define dismissal behavior (“snooze”, “skip”, “dismiss until reload”) tied to persisted state so it doesn’t reappear unexpectedly.

27. **(Email coupling)** If email can be configured in Settings, onboarding should reflect it (derive email step completion from email-config existence), otherwise users can “connect email” elsewhere but remain stuck in onboarding.

28. **(Timestamps)** Use `timestamptz` and set defaults/triggers: `started_at DEFAULT now()`, `updated_at` auto-updated on every write, `completed_at` set once; otherwise ordering/conflict resolution gets messy.

29. **(Error handling)** Document expected status codes (409 for invalid transitions, 422 for validation, etc.) and keep error payloads consistent (`error`, `message`, optional `errors[]`) so frontend handling is predictable.

30. **(Observability)** Log onboarding transitions and migrations with `X-Correlation-ID` and minimal PII; it’s critical for debugging “stuck banner”, “reset loop”, and migration regressions.