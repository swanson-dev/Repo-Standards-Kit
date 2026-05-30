---
written: 2026-05-30T20:20:00-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**Slice 3 (distribution) is fully shipped and on `main`.** RFC-0001 chose the mechanism: distribute the kit as a zero-dependency PyPI package (`repo-standards-kit`) run via `pipx`/`uvx`, exposing a `standards` CLI. **Plan 1 (v0.5.0, PRs #1–#2)** delivered packaging + `standards init`. **Plan 2 (v0.6.0, PR #3)** delivered `standards update` + the partial/managed-region ownership class + a non-destructive first-init guard. **Plan 3 (no version bump, PR #5)** made the package releasable: portable stdlib test CI (py3.9–3.12), a `build-smoke` wheel check, and a tag-triggered PyPI **Trusted-Publishing (OIDC)** release workflow. 14/14 test suites green; standards-check 0/0. The package is at `0.6.0`, **not yet git-tagged or published** — that's a deliberate user action (see Open threads).

## Recently touched

Slice 3 Plan 3 (PR #5, merge `b365a80`) + the PR #4 handoff refresh that preceded it. Headlines:

- `tools/run_tests.py` — portable stdlib test runner (`discover`/`run(paths)->int`/`main`). One subprocess per suite, sidestepping the `test_cli.py` basename collision without a `pytest` dependency. Canonical command: `python tools/run_tests.py`.
- `.github/workflows/repo-standards.yml` — added `test` (matrix py3.9/3.10/3.11/3.12, `fail-fast: false`) and `build-smoke` (build wheel → install in venv → `standards init` → assert `docs/STANDARDS.md` + `.standards-kit.json`, proving the wheel bundled `standards/_payload`).
- `.github/workflows/release.yml` (new) — `on: push: tags: ['v*']`; job `release` with `environment: pypi`, `permissions: id-token: write`, steps run-tests (gate) → `python -m build` → `pypa/gh-action-pypi-publish@release/v1` (no token). Inert until PyPI setup + a tag.
- ADR-0011 (publish via GitHub Actions Trusted Publishing) + `docs/decisions/README.md` index backfilled (0009–0011).
- `docs/RELEASING.md` (new) — one-time PyPI Trusted-Publisher setup + the release ritual (incl. the CHANGELOG `example.invalid` → real-tag reflink step).
- `fix(test)`: `scripts/update-handoff/test_update_handoff.py` got `from __future__ import annotations` — a pre-existing Python 3.9 bug (`env: dict | None` evaluated at def-time) that the new CI matrix surfaced. Repo-wide sweep confirmed it was the only offender.

Design docs: `docs/superpowers/specs/2026-05-30-release-pypi-and-portable-ci-design.md` and `docs/superpowers/plans/2026-05-30-distribution-build-3-release-and-ci.md`.

## Open threads

- **Releasing is now the user's deliberate action, not a code task.** To actually publish v0.6.0: (1) do the one-time PyPI Trusted-Publisher setup in `docs/RELEASING.md` (use the *pending publisher* flow for the first release), (2) create the `pypi` GitHub Environment, (3) `git tag v0.6.0 && git push origin v0.6.0`. The tag fires `release.yml`. Until then the release workflow is inert. Only the user can do this.
- **Slice 4 backlog (deeper CI, not started):** SHA-pin `pypa/gh-action-pypi-publish` (currently floating `@release/v1`); a version-coherence CI lint (`src/standards/__about__.py` ↔ CHANGELOG top entry ↔ `AGENTS.md` Kit-version block must agree — `RELEASING.md` step 1 is the manual version today); content/doc-freshness/link linting; automating the `docs/decisions/README.md` index. `AGENTS.md` "queued slices" lists only Slice 4.
- **ADO home (deferred until that repo exists):** PyPI Trusted Publishing can't be used from Azure DevOps (PyPI doesn't support ADO as an OIDC provider); that home would publish with a stored PyPI API token. The portable `tools/run_tests.py` + `standards-check` steps are shared by design. Recorded in ADR-0011.
- **Marker is JSON** (`.standards-kit.json`), not the `.standards-kit.toml` named in RFC-0001 (stdlib has no TOML writer). Recorded in ADR-0009.
- **Tags:** v0.1.0–v0.4.0 exist from earlier slices; v0.5.0/v0.6.0 are intentionally not backfilled (PyPI only needs the current version — see RELEASING.md notes).

## Don't do

- Don't `git tag`/push a release tag yourself — publishing is the user's call (it triggers a real PyPI publish). Surface RELEASING.md; let them pull the trigger.
- Don't edit ADRs 0001–0011; all are `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`.
- Don't make `standards update` interactive or destructive. The contract (ADR-0009/0010): apply + report; conflicts go to `<path>.kit-<version>` sidecars; downstream edits (and content outside a managed block) are never clobbered; `--dry-run` writes nothing.
- Don't change the partial-branch ordering in `update.py` back to "identical-check first" — the current order (untouched-since-adoption splice first) is deliberate so the dev-mode test exercises the real splice path. Documented; opus-verified safe.
- Don't reintroduce a single `pytest` CI step — `tools/run_tests.py` (subprocess-per-suite) is canonical specifically because `test_cli.py` exists in both `tests/` and `scripts/new-doc/` with no package markers, which breaks `pytest`/`unittest discover` *collection*. Suites all pass standalone; that's the project's model.
- Don't drop `from __future__ import annotations` from any test/module using PEP 604 (`X | None`) or PEP 585 (`list[...]`) at module scope — the CI matrix runs Python 3.9, where these fail at def-time without it.
- Don't add multi-block managed regions or a `standards set-profile` command without an ADR — both deferred to post-v1.
- Don't introduce a runtime dependency. The package is pure-stdlib by design (ADR-0009); `pipx`/`uvx` is only the delivery vehicle.
- Don't push directly to `main`; PR-and-merge per the established flow.
