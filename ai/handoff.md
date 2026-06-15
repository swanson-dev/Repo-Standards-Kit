---
written: 2026-06-15T11:00:00-05:00
written_by: codex
for: next-session
---

# Handoff

## TL;DR

M4 release/reporting hygiene shipped as v0.18.0. The kit now has opt-in
`--external-links` and `--freshness-report` checks; `ai/` freshness covers
current-state, next-actions, and handoff; historical changelog placeholder links
are cleaned up. The v0.18.0 GitHub Release is live with sdist/wheel artifacts
and publish attestations.

## Recently touched

- `scripts/standards-check/checks/external_links.py` adds opt-in HTTP liveness checking with URL dedupe and HEAD-to-GET fallback.
- `scripts/standards-check/checks/structural.py` now checks `ai/next-actions.md`, emits clearer freshness warning text, and supports opt-in freshness status output.
- `scripts/standards-check/check.py` and `src/standards/cli.py` expose `--external-links` and `--freshness-report`.
- Version/docs/changelog state was bumped to v0.18.0 and released.

## Open threads

- Monitor downstream feedback on the new opt-in reporting checks.
- Pick the next milestone before adding new CLI or adopter-contract surface.
- Historical changelog entries, prior ADR bodies, RFCs, and superpowers plans still mention capture/promote because they describe past design work.
- No `commands`, `doctor`, interactive CLI prompting, or `standards new-skill` subcommand was added; keep that scope for a separate design pass if wanted.

## Don't do

- Do not resurrect `/capture-discovery`, `/promote-discovery`, `docs/discovery/captured/`, or `promoted_to` unless a new ADR supersedes ADR-0017.
- Do not edit the bodies of Accepted/Superseded ADRs; write a new ADR for reversals.
- Keep discovery notes simple: tracked markdown under `docs/discovery/`, linked from structured docs when they matter.
- Do not commit `.agents/` or `.codex/`; they are local tool surfaces, not the shipped kit contract.
