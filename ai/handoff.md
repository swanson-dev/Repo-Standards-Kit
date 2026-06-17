---
written: 2026-06-16T19:10:08-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Published v1.2.0 with the new `documentation` repo profile for documentation/spec repos whose implementation lives elsewhere. The profile keeps the full universal core, adds `docs/source-map.md` as its profile extra, and passed local gates, release workflow gates, GitHub Release verification, and a PyPI installed-package smoke using `standards init --profile documentation`.

Follow-up fix: standards-check link traversal now skips common dependency/build/cache directories such as `node_modules/`, which prevents dependency markdown from flooding downstream checks.

Published v1.3.0 with README/CHANGELOG starter scaffolding for `standards init`/`standards adopt`, an advisory `standard-update-changelog` command plus Stop-hook reminder, and link-check exclusions for dependency/build/cache directories. Release workflow and PyPI installed-package smoke both passed.

## Recently touched

- `src/standards/cli.py`, `src/standards/init.py`, `scripts/standards-check/checks/structural.py`, and `tools/check_v1_readiness.py` add `documentation` to profile plumbing and generated readiness.
- `docs/STANDARDS.md`, downstream standards templates, numbered-doc templates, `README.md`, `docs/07-testing.md`, and `docs/versioning-policy.md` document the new profile.
- `docs/templates/source-map-template.md` adds the documentation-profile extra for linked source repos, ownership, canonical references, and sync policy.
- `docs/rfcs/0006-should-the-kit-add-a-documentation-repo-profile/rfc.md` and `docs/decisions/0021-add-a-documentation-repo-profile.md` record the decision.
- `CHANGELOG.md`, `docs/05-implementation-plan.md`, `ai/current-state.md`, and `ai/next-actions.md` describe the v1.3.0 release prep and next verification step.
- `scripts/standards-check/checks/links.py` and `scripts/standards-check/test_links.py` add the dependency/cache skip set and a `node_modules` regression test.
- `src/standards/manifest.py`, `src/standards/init.py`, `docs/templates/repo-readme-template.md`, and `docs/templates/changelog-template.md` add scaffold-once root starters.
- `scripts/changelog/check_changelog.py`, `.claude/skills/standard-update-changelog/SKILL.md`, `.github/prompts/standard-update-changelog.prompt.md`, and `.claude/settings.json` add the changelog reminder path.

Validation:
- `python tools/run_tests.py`
- `python tools/check_v1_readiness.py`
- `python scripts/standards-check/check.py`
- `python tools/check_version_coherence.py`
- `python -m unittest scripts.standards-check.test_links`
- `python -m unittest tests.test_init tests.test_adopt tests.test_profiles_scaffold tests.test_v1_readiness tests.test_payload tests.test_payload_includes_checks tests.test_manifest tests.test_workflows scripts.changelog.test_check_changelog scripts.standards-check.test_skills`
- `python -m build`
- GitHub Actions release workflow `27661574279` succeeded for `v1.3.0`.
- PyPI smoke installed `repo-standards-kit==1.3.0` and ran `standards init --profile documentation`, `standards check`, `standards check --freshness-report`, and `standards check --external-links`.

## Open threads

- Pilot `standards init --profile documentation` in a real docs-only repo and tune `docs/source-map.md` if the linked-repo fields feel too light or too heavy.
- Merge/reconcile `codex/release-v1.1.0` into `main` so main carries the v1.2.0 and v1.3.0 release work.
- Confirm whether to merge/reconcile `codex/release-v1.1.0` into `main` now that `v1.3.0` is published.

## Don't do

- Do not scaffold `docs/source-map.md` by default; it is a profile extra template, like `versioning-policy`, `environments`, and `data-contracts`.
- Do not edit accepted historical ADRs such as ADR-0003 or ADR-0018 just to update old "four profiles" wording.
