---
written: 2026-06-15T13:20:00-05:00
written_by: codex
for: next-session
---

# Handoff

## TL;DR

v1.0.0 is published. The kit now has a generated four-profile downstream
readiness gate, release/kit-guard workflows run it, and the manual external-link
workflow provides opt-in networked audits. Docs describe the stable SemVer
baseline, ADR-0018 records generated fixtures as the v1 readiness evidence, and
the published `repo-standards-kit==1.0.0` package smoke passed.

## Recently touched

- `tools/check_v1_readiness.py` validates generated downstream repos for `application`, `library`, `infra`, and `data`.
- `.github/workflows/kit-guards.yml` and `.github/workflows/release.yml` run the v1 readiness gate.
- `.github/workflows/external-links.yml` adds a manual networked external-link check.
- Version/docs/changelog state was bumped to v1.0.0 and released.

## Open threads

- Monitor downstream feedback on v1.0.0 adoption and stable SemVer expectations.
- Pick the first post-v1 public CLI milestone before adding command surface.
- Historical changelog entries, prior ADR bodies, RFCs, and superpowers plans still mention capture/promote because they describe past design work.
- No `commands`, `doctor`, interactive CLI prompting, or `standards new-skill` subcommand was added; keep that scope for a separate design pass if wanted.

## Don't do

- Do not resurrect `/capture-discovery`, `/promote-discovery`, `docs/discovery/captured/`, or `promoted_to` unless a new ADR supersedes ADR-0017.
- Do not edit the bodies of Accepted/Superseded ADRs; write a new ADR for reversals.
- Keep discovery notes simple: tracked markdown under `docs/discovery/`, linked from structured docs when they matter.
- Do not commit `.agents/` or `.codex/`; they are local tool surfaces, not the shipped kit contract.
