---
written: 2026-06-16T19:10:08-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Published v1.2.0 with the new `documentation` repo profile for documentation/spec repos whose implementation lives elsewhere. The profile keeps the full universal core, adds `docs/source-map.md` as its profile extra, and passed local gates, release workflow gates, GitHub Release verification, and a PyPI installed-package smoke using `standards init --profile documentation`.

## Recently touched

- `src/standards/cli.py`, `src/standards/init.py`, `scripts/standards-check/checks/structural.py`, and `tools/check_v1_readiness.py` add `documentation` to profile plumbing and generated readiness.
- `docs/STANDARDS.md`, downstream standards templates, numbered-doc templates, `README.md`, `docs/07-testing.md`, and `docs/versioning-policy.md` document the new profile.
- `docs/templates/source-map-template.md` adds the documentation-profile extra for linked source repos, ownership, canonical references, and sync policy.
- `docs/rfcs/0006-should-the-kit-add-a-documentation-repo-profile/rfc.md` and `docs/decisions/0021-add-a-documentation-repo-profile.md` record the decision.
- `CHANGELOG.md`, `docs/05-implementation-plan.md`, `ai/current-state.md`, and `ai/next-actions.md` describe the published v1.2.0 release and next pilot step.

Validation:
- `python tools/run_tests.py`
- `python tools/check_v1_readiness.py`
- `python scripts/standards-check/check.py`
- `python tools/check_version_coherence.py`

## Open threads

- Pilot `standards init --profile documentation` in a real docs-only repo and tune `docs/source-map.md` if the linked-repo fields feel too light or too heavy.
- Merge/reconcile `codex/release-v1.1.0` into `main` so main carries the v1.2.0 release commit and post-release changelog link.

## Don't do

- Do not scaffold `docs/source-map.md` by default; it is a profile extra template, like `versioning-policy`, `environments`, and `data-contracts`.
- Do not edit accepted historical ADRs such as ADR-0003 or ADR-0018 just to update old "four profiles" wording.
