---
written: 2026-06-14T00:45:00-05:00
written_by: codex
for: next-session
---

# Handoff

## TL;DR

v0.17.0 is published to PyPI and now has a GitHub Release with the sdist and wheel
attached. The remaining local work is release-workflow polish: future tag pushes
should create/update the GitHub Release after PyPI publish so this gap does not recur.

## Recently touched

- `v0.17.0` GitHub Release was created from the existing tag using the changelog section as notes, with the `0.17.0` wheel and sdist attached.
- `.github/workflows/release.yml` now grants `contents: write` and adds an idempotent GitHub Release creation/upload step after PyPI publish.
- `docs/RELEASING.md`, `CHANGELOG.md`, `ai/current-state.md`, and `ai/next-actions.md` were updated to describe the release workflow and next work accurately.

## Open threads

- Push the workflow/docs update after validation.
- External-link liveness is the most valuable next reporting slice; it would catch missing release/tag links in `CHANGELOG.md`.
- Historical changelog entries, prior ADR bodies, RFCs, and superpowers plans still mention capture/promote because they describe past design work.
- No `commands`, `doctor`, interactive CLI prompting, or `standards new-skill` subcommand was added; keep that scope for a separate design pass if wanted.

## Don't do

- Do not resurrect `/capture-discovery`, `/promote-discovery`, `docs/discovery/captured/`, or `promoted_to` unless a new ADR supersedes ADR-0017.
- Do not edit the bodies of Accepted/Superseded ADRs; write a new ADR for reversals.
- Keep discovery notes simple: tracked markdown under `docs/discovery/`, linked from structured docs when they matter.
- Do not commit `.agents/` or `.codex/`; they are local tool surfaces, not the shipped kit contract.
