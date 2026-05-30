# Plan 3 Design — PyPI Release Workflow + Portable CI

**Status:** Approved (brainstorming, 2026-05-30)
**Upstream:** RFC-0001 (distribution = PyPI via `pipx`/`uvx`), ADR-0009 (zero-dependency PyPI package). Plan 3 makes the already-built `repo-standards-kit` package actually releasable.
**Builds on:** Plan 1 (packaging + `init`, v0.5.0) and Plan 2 (`update` + managed-region, v0.6.0), both on `main`.

## Goal

Make `repo-standards-kit` releasable to PyPI and wire the 97 tests into CI — without publishing yet (the one-time PyPI Trusted-Publisher setup is the user's to do). Keep everything portable plain-Python so a future Azure DevOps home can reuse the test/check steps.

## Decisions (from brainstorming)

1. **Scope/target:** GitHub Actions publish workflow + portable CI now; the eventual ADO pipeline is deferred (the ADO repo doesn't exist yet). Distribution stays PyPI; the kit's *source* will eventually live in both an ADO repo and a public GitHub repo.
2. **Test runner:** stdlib `unittest` via a small portable runner — no `pytest` dependency (matches the kit's zero-dependency ethos; avoids the `test_cli.py` basename collision).
3. **Release trigger:** publish workflow fires on `v*` tag-push (Trusted Publishing, `pypi` GitHub Environment). Plan 3 does **not** push a tag — tagging is the user's deliberate release action after PyPI setup.
4. **Setup docs:** dedicated `docs/RELEASING.md` (not a README section).
5. **`build-smoke` runs on every push/PR** (cheap; catches wheel `_payload` bundling regressions early).
6. **No version bump** — Plan 3 is repo/CI infra; the package stays `0.6.0` and the first release *publishes* 0.6.0.

## Phase A — Portable test CI + packaging smoke

### A1. `tools/run-tests.py` (new, stdlib)

A single stdlib script that runs every test suite, each in its own subprocess (every test file already ends in `if __name__ == "__main__": unittest.main()` and inserts `src`/its dir on `sys.path`). Aggregates results, prints a per-suite summary + total, exits `1` if any suite fails else `0`.

- Discovers: `sorted(root.glob("tests/test_*.py")) + sorted(root.glob("scripts/**/test_*.py"))`.
- Subprocess isolation sidesteps the `pytest`/`unittest discover` duplicate-`test_cli.py` collision — no package restructure, no third-party dep.
- Becomes the canonical command (`python tools/run-tests.py`), documented in `RELEASING.md` and referenced from CI. Interface: no args; `--quiet` optional (omit for v1, YAGNI).

### A2. Extend `.github/workflows/repo-standards.yml`

Keep the existing `check` job (standards-check). Add:

- **`test` job** — matrix `python-version: ["3.9", "3.10", "3.11", "3.12"]`, `runs-on: ubuntu-latest`; steps: checkout → setup-python → `python tools/run-tests.py`.
- **`build-smoke` job** — `runs-on: ubuntu-latest`; steps: checkout → setup-python (3.x) → `pip install build` → `python -m build` → create a venv, `pip install dist/*.whl` into it → `standards init --profile library <tmpdir>` → assert the adopted repo contains `docs/STANDARDS.md` and `.standards-kit.json` (proves the wheel bundled `standards/_payload`, the path dev/test only reach via the repo-root fallback). Runs on push + PR.

All three jobs run on the existing `on: {push: {branches:[main]}, pull_request: {}}` triggers. `permissions: contents: read` unchanged.

## Phase B — Release workflow + decision record + docs

### B1. `.github/workflows/release.yml` (new)

```
on:
  push:
    tags: ["v*"]
```
One job `release`, `runs-on: ubuntu-latest`, `environment: pypi`, `permissions: {id-token: write, contents: read}`:
1. checkout → setup-python (3.x).
2. `python tools/run-tests.py` (release gate — never publish a red build).
3. `pip install build` → `python -m build` (sdist + wheel into `dist/`).
4. Publish via `pypa/gh-action-pypi-publish` (pinned major) using OIDC Trusted Publishing — **no `password`/token**.

Inert until the user (a) configures the PyPI Trusted Publisher and (b) pushes a `v*` tag.

### B2. ADR-0011 (publishing mechanism)

Record: publish to PyPI via **GitHub Actions Trusted Publishing (OIDC, tokenless)**; gated behind a `pypi` Environment and a passing test run on tag-push. The eventual **ADO** home cannot use Trusted Publishing (PyPI doesn't support ADO as an OIDC provider) and would publish via a stored PyPI API token — deferred until that repo exists. CI test + standards-check stay portable plain-Python so both homes share them. Companion to ADR-0009. Dogfood `new-adr`.

### B3. `docs/RELEASING.md` (new)

- **One-time setup (the user does this on pypi.org):** create the project's Trusted Publisher — PyPI project `repo-standards-kit`, owner `swanson-dev`, repo `Repo-Standards-Kit`, workflow `release.yml`, environment `pypi`. (Until the project exists, use PyPI's "pending publisher" flow.)
- **Release ritual:** ensure `src/standards/__about__.py` + the CHANGELOG entry + the `AGENTS.md` Kit-version match the intended version, then `git tag vX.Y.Z && git push origin vX.Y.Z`. The tag fires `release.yml`.
- **Local pre-release check:** `python tools/run-tests.py` + `python scripts/standards-check/check.py` + `python -m build`.
- Note the version-coherence invariant (`__about__` ↔ CHANGELOG top entry ↔ `AGENTS.md` block) that Slice 4 CI could later lint.

## Components & files

| Path | Phase | Responsibility |
|---|---|---|
| `tools/run-tests.py` (new) | A | Portable stdlib test runner. |
| `.github/workflows/repo-standards.yml` (modify) | A | Add `test` (matrix) + `build-smoke` jobs. |
| `.github/workflows/release.yml` (new) | B | Tag-triggered Trusted-Publishing release. |
| `docs/decisions/0011-*.md` (new) | B | ADR-0011 publishing mechanism. |
| `docs/RELEASING.md` (new) | B | One-time PyPI setup + release ritual. |
| `tests/test_run_tests.py` (new) | A | Tests the runner's pass/fail aggregation + exit code. |

## Testing strategy

- `tools/run-tests.py`: a unit test (`tests/test_run_tests.py`) that points the runner's discovery at a temp dir containing one passing and one failing dummy test file and asserts exit code `1` + that a summary is produced; and that an all-passing set exits `0`. (Refactor the runner so discovery/roots are injectable for testability — e.g. a `run(paths) -> int` core with a thin `__main__`.)
- Workflows: validated by being well-formed YAML and, for `repo-standards.yml`, by actually running on this PR (the `test` + `build-smoke` jobs execute). `release.yml` can't be end-to-end tested without a tag + PyPI config; its correctness is by inspection + the shared `tools/run-tests.py`/`build` steps that the other jobs exercise.
- standards-check stays 0/0; `tools/run-tests.py` reports 98 tests (97 + the runner's own).

## Out of scope (later)

- Actually publishing (needs the user's PyPI Trusted-Publisher setup) and pushing the `v0.6.0` tag.
- Azure DevOps `azure-pipelines.yml` (deferred until the ADO repo exists; ADR-0011 notes the token-based path).
- Backfilling a `v0.5.0` git tag — PyPI only needs the current version; not worth a historical publish.
- Version-coherence CI lint (Slice 4).
- `pytest` support (the stdlib runner is canonical).

## Version

No bump. Plan 3 ships against `0.6.0`; the first release publishes `0.6.0`.
