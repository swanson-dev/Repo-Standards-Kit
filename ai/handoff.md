---
written: 2026-05-28T21:43:09-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Slice 2.5 is complete and green. `update-handoff` ships as the kit's first dual-surface artifact (slash command + Stop hook), wired via `.claude/settings.json`. ADR-0008 records the hook-invokes-script-in-check-mode pattern as the hook-surface companion to ADR-0007. Two latent bugs surfaced during dogfooded verification and were fixed: `new-adr`/`new-rfc` were not stripping the template HTML preamble, and `update-handoff` now falls back to last 10 commits when the prior handoff's `written:` timestamp is in the future. All 36 tests pass (14 + 12 + 10 — two new tests per fix); standards-check exits clean; CHANGELOG records v0.3.0.

## Recently touched

- docs(slice-2.5): write Slice 2.5 handoff via dogfooded update-handoff
- fix(slice-2.5): update_handoff falls back to last 10 commits when prior since_ts is in the future
- fix(slice-2): strip template HTML preamble in new-adr and new-rfc scripts

Files changed:
  - `ai/handoff.md`
  - `scripts/update-handoff/test_update_handoff.py`
  - `scripts/update-handoff/update_handoff.py`
  - `scripts/new-doc/new-adr.py`
  - `scripts/new-doc/new-rfc.py`
  - `scripts/new-doc/test_cli.py`

## Open threads

- Tag `v0.3.0` (do not push without explicit user confirmation; remote is `https://github.com/swanson-dev/Repo-Standards-Kit.git`).
- Slice 2.6 (`promote-discovery`) queued — same form-factor pattern as `update-handoff`; design when ready.
- Slice 3 distribution still queued at `ai/open-questions.md#q-2` — blocks `scaffold-new-repo`.
- Wrapper-parity-lint follow-up from ADR-0007's "Bad" consequence still queued.

## Don't do

- Don't edit ADRs 0001–0008. All are `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`.
- Don't add a write-mode auto-trigger to the `update-handoff` hook. ADR-0008 explicitly chose advisory-only for the hook surface.
- Don't bypass the wrapper-parity rule. `update-handoff`'s SKILL.md and prompt.md must convey the same when/how/after content; the only documented asymmetry is the Copilot-can't-auto-trigger note.
- Don't commit `__pycache__/` or `*.pyc` files. They're in `.gitignore` as of Slice 2.5 pre-flight; a prior session committed some by accident — that was force-pushed away.
- Don't add the template HTML preamble back to the ADR/RFC templates. The `new-adr`/`new-rfc` scripts now strip it; if a future template change reintroduces it, the regression tests in `test_cli.py` will catch it.
- Don't push without confirming with the user first.
