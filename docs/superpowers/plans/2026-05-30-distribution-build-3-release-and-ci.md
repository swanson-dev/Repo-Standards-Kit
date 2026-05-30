# Distribution Build — Plan 3: PyPI Release Workflow + Portable CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `repo-standards-kit` releasable to PyPI and run all test suites in CI — without publishing yet (the PyPI Trusted-Publisher setup is the user's to do).

**Architecture:** A stdlib `tools/run_tests.py` runs every suite in its own subprocess (sidestepping the duplicate-`test_cli.py` discovery collision, no `pytest`). The existing `repo-standards.yml` gains a `test` matrix job + a `build-smoke` job that installs the built wheel and runs `standards init` (verifying the bundled `_payload`). A new `release.yml` publishes to PyPI via OIDC Trusted Publishing on `v*` tag-push, guarded by a `pypi` GitHub Environment. ADR-0011 records the publishing decision; `docs/RELEASING.md` documents the one-time setup + release ritual.

**Tech Stack:** Python ≥3.9 stdlib (`subprocess`, `pathlib`, `unittest`); GitHub Actions; `hatchling` (build, already configured); `pypa/gh-action-pypi-publish` (OIDC, no token).

**Ships as:** `0.6.0` — **no version bump** (Plan 3 is repo/CI infra; the first release publishes the existing 0.6.0).

**Spec:** `docs/superpowers/specs/2026-05-30-release-pypi-and-portable-ci-design.md`.

> **Naming note:** the spec wrote `tools/run-tests.py`; this plan uses `tools/run_tests.py` (underscore) so the runner's functions are importable by its unit test. The CLI invocation is `python tools/run_tests.py`.

---

## File Structure

| Path | Phase | Responsibility |
|---|---|---|
| `tools/run_tests.py` (create) | A | Portable stdlib test runner (`discover`, `run`, `main`). |
| `tests/test_run_tests.py` (create) | A | Unit-tests the runner's aggregation + exit code. |
| `.github/workflows/repo-standards.yml` (modify) | A | Add `test` (matrix) + `build-smoke` jobs. |
| `.github/workflows/release.yml` (create) | B | Tag-triggered Trusted-Publishing release. |
| `docs/decisions/0011-*.md` (create) | B | ADR-0011 publishing mechanism. |
| `docs/RELEASING.md` (create) | B | One-time PyPI setup + release ritual. |

---

# PHASE A — Portable test CI + packaging smoke

## Task A1: `tools/run_tests.py` + its test

**Files:**
- Create: `tools/run_tests.py`
- Create: `tests/test_run_tests.py`

- [ ] **Step 1: Write the failing test**

`tests/test_run_tests.py`:
```python
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from run_tests import discover, run  # noqa: E402

_PASS = ("import unittest\n"
         "class T(unittest.TestCase):\n"
         "    def test_a(self):\n"
         "        self.assertTrue(True)\n"
         "if __name__ == '__main__':\n"
         "    unittest.main()\n")
_FAIL = _PASS.replace("self.assertTrue(True)", "self.assertTrue(False)")


class RunTestsTests(unittest.TestCase):
    def _write(self, d, name, body):
        p = Path(d) / name
        p.write_text(body, encoding="utf-8")
        return p

    def test_all_passing_exits_zero(self):
        with tempfile.TemporaryDirectory() as d:
            ok = self._write(d, "test_ok.py", _PASS)
            self.assertEqual(run([ok]), 0)

    def test_a_failing_suite_exits_one(self):
        with tempfile.TemporaryDirectory() as d:
            ok = self._write(d, "test_ok.py", _PASS)
            bad = self._write(d, "test_bad.py", _FAIL)
            self.assertEqual(run([ok, bad]), 1)

    def test_discover_finds_repo_suites(self):
        root = Path(__file__).resolve().parents[1]
        names = {p.name for p in discover(root)}
        self.assertIn("test_update.py", names)        # from tests/
        self.assertIn("test_check.py", names)          # from scripts/standards-check/
        self.assertIn("test_promote_discovery.py", names)  # from scripts/promote-discovery/


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tests/test_run_tests.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'run_tests'`.

- [ ] **Step 3: Write the implementation**

`tools/run_tests.py`:
```python
#!/usr/bin/env python3
"""Run every kit test suite in its own subprocess and aggregate pass/fail.

Each test file is a standalone stdlib `unittest` module (it has a `__main__`
guard and inserts its own import paths), so we execute the files as subprocesses
rather than relying on `unittest`/`pytest` discovery — which collides on the
duplicate `test_cli.py` basename across `tests/` and `scripts/new-doc/`. No
third-party dependency; runs identically on GitHub Actions, an ADO pipeline, or
locally on Windows.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def discover(root: Path) -> list[Path]:
    """Return every test file: tests/test_*.py + scripts/**/test_*.py, sorted."""
    root = Path(root)
    return sorted(root.glob("tests/test_*.py")) + sorted(root.glob("scripts/**/test_*.py"))


def run(paths: list[Path]) -> int:
    """Run each test file in a subprocess. Return 1 if any fail, else 0."""
    failed: list[str] = []
    for tf in paths:
        result = subprocess.run([sys.executable, str(Path(tf))])
        ok = result.returncode == 0
        print(f"{'OK  ' if ok else 'FAIL'}  {Path(tf).as_posix()}")
        if not ok:
            failed.append(str(tf))
    print(f"\n{len(paths) - len(failed)}/{len(paths)} suites passed.")
    return 1 if failed else 0


def main() -> int:
    return run(discover(REPO_ROOT))


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python tests/test_run_tests.py`
Expected: PASS (3 tests).

- [ ] **Step 5: Run the whole suite through the new runner**

Run: `python tools/run_tests.py`
Expected: every line `OK`, final `14/14 suites passed.`, exit 0. (13 prior suites + the new `test_run_tests.py`.)

- [ ] **Step 6: Commit**

```bash
git add tools/run_tests.py tests/test_run_tests.py
git commit -m "feat(ci): add portable stdlib test runner (tools/run_tests.py)"
```
End the commit body with: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Task A2: Add `test` + `build-smoke` jobs to the CI workflow

**Files:**
- Modify: `.github/workflows/repo-standards.yml`

Config task — verified by the jobs actually running when this branch's PR opens.

- [ ] **Step 1: Replace `.github/workflows/repo-standards.yml` with:**

```yaml
name: Standards check

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  check:
    name: Structural lint (v1)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Run standards check
        run: python scripts/standards-check/check.py

  test:
    name: Tests (py${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Run all test suites
        run: python tools/run_tests.py

  build-smoke:
    name: Build wheel + init smoke
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Build the wheel
        run: |
          python -m pip install --upgrade build
          python -m build
      - name: Install wheel into a clean venv and adopt a temp repo
        run: |
          python -m venv /tmp/venv
          /tmp/venv/bin/pip install dist/*.whl
          /tmp/venv/bin/standards init --profile library /tmp/adopted
          test -f /tmp/adopted/docs/STANDARDS.md
          test -f /tmp/adopted/.standards-kit.json
          test -f /tmp/adopted/AGENTS.md
```

- [ ] **Step 2: Validate locally what can be validated**

The `build-smoke` steps can be dry-run locally (Windows-adjusted) to confirm the wheel bundles `_payload`:
```powershell
python -m pip install --upgrade build
python -m build
python -m venv $env:TEMP\smkvenv
& "$env:TEMP\smkvenv\Scripts\pip.exe" install (Get-ChildItem dist\*.whl | Select-Object -First 1).FullName
& "$env:TEMP\smkventv\Scripts\standards.exe" --version
```
Expected: `standards 0.6.0`. (If the venv path differs on the runner, that's fine — CI uses the Linux `/tmp/venv/bin` paths in the YAML. This step only confirms the wheel installs + entry point works; delete `dist/` and the temp venv after.)

> The full YAML (matrix `test`, `build-smoke`) is validated for real when this branch's PR opens and Actions runs it. If GitHub reports a workflow syntax error, fix and re-push.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/repo-standards.yml
git commit -m "feat(ci): run all test suites (3.9-3.12) and a wheel+init smoke in CI"
```
Trailer as above.

---

# PHASE B — Release workflow + decision record + docs

## Task B1: `release.yml` Trusted-Publishing workflow

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create `.github/workflows/release.yml` with:**

```yaml
name: Release

on:
  push:
    tags: ['v*']

permissions:
  contents: read

jobs:
  release:
    name: Build + publish to PyPI
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write   # required for PyPI Trusted Publishing (OIDC)
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Gate on the full test suite
        run: python tools/run_tests.py
      - name: Build sdist + wheel
        run: |
          python -m pip install --upgrade build
          python -m build
      - name: Publish to PyPI (Trusted Publishing — no token)
        uses: pypa/gh-action-pypi-publish@release/v1
```

> **Verify at execution:** confirm `pypa/gh-action-pypi-publish@release/v1` is the current recommended ref (it is the maintained floating major as of this plan; pin to a release SHA if the team prefers). With `id-token: write` and **no** `password:` input, the action uses OIDC Trusted Publishing automatically. The `environment: pypi` gives a protection surface and matches the Trusted Publisher config in `RELEASING.md`.

- [ ] **Step 2: Sanity-check the YAML is well-formed**

There is no stdlib YAML parser, so validate structurally: confirm indentation, the single `release` job, `on.push.tags`, `id-token: write`, and the action ref by re-reading the file. Final validation: after this branch's PR is pushed, GitHub will flag a malformed workflow in the Actions tab even though `release.yml` won't *trigger* (no tag). If flagged, fix and re-push.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "feat(ci): add tag-triggered PyPI release workflow (Trusted Publishing)"
```
Trailer as above.

---

## Task B2: ADR-0011 (publishing mechanism)

**Files:**
- Create: `docs/decisions/0011-*.md` (via `new-adr`)

- [ ] **Step 1: Generate**

Run: `python scripts/new-doc/new-adr.py "Publish to PyPI via GitHub Actions Trusted Publishing"`
Expected: `Created docs/decisions/0011-publish-to-pypi-via-github-actions-trusted-publishing.md`

- [ ] **Step 2: Fill the body**

`status: Accepted`, `date: 2026-05-30`, `deciders: swanson-dev`; remove inline `<!-- -->` hints. Record:
- **Context:** the package (ADR-0009) needs a release path. The kit's source will eventually live in both an Azure DevOps repo and a public GitHub repo; distribution stays PyPI.
- **Decision:** publish from **GitHub Actions** via **PyPI Trusted Publishing (OIDC)** — tokenless, fired on `v*` tag-push, gated by a `pypi` GitHub Environment and a passing `tools/run_tests.py` run. CI (`tools/run_tests.py`, `standards-check`) is portable plain-Python so both homes share it.
- **Considered/deferred:** Azure DevOps Pipelines cannot use PyPI Trusted Publishing (PyPI doesn't support ADO as an OIDC identity provider), so an ADO publish path would need a stored PyPI API token in a variable group — deferred until the ADO repo exists. A stored-token GitHub publish was rejected in favor of tokenless OIDC.
- **Consequences:** no long-lived secret to leak; release == push a tag; first-time setup requires configuring the Trusted Publisher on PyPI (documented in `docs/RELEASING.md`). Companion to ADR-0009.
- **More Information:** link `../RELEASING.md` and the design spec.

- [ ] **Step 3: Verify + commit**

Run: `python scripts/standards-check/check.py` → `0 error(s), 0 warning(s)`.
```bash
git add docs/decisions/0011-*.md
git commit -m "docs(slice-3): ADR-0011 publish via GitHub Actions Trusted Publishing"
```
Trailer as above.

---

## Task B3: `docs/RELEASING.md`

**Files:**
- Create: `docs/RELEASING.md`

- [ ] **Step 1: Create `docs/RELEASING.md` with:**

```markdown
# Releasing `repo-standards-kit`

The package is published to PyPI by `.github/workflows/release.yml`, which fires on a `v*` tag push and publishes via **Trusted Publishing (OIDC)** — there is no stored token. See [ADR-0011](./decisions/0011-publish-to-pypi-via-github-actions-trusted-publishing.md).

## One-time setup (PyPI side — repo maintainer)

1. Create (or claim) the PyPI project `repo-standards-kit`.
2. In the project's **Publishing** settings, add a **Trusted Publisher**:
   - Owner: `swanson-dev`
   - Repository: `Repo-Standards-Kit`
   - Workflow filename: `release.yml`
   - Environment: `pypi`
   (For the very first release, use PyPI's **pending publisher** flow so the project is created on first publish.)
3. In GitHub repo settings, create an **Environment** named `pypi` (optionally add required reviewers for a release gate).

## Cutting a release

1. Confirm version coherence — these three must agree:
   - `src/standards/__about__.py` (`__version__`)
   - the top `## [X.Y.Z]` entry in `CHANGELOG.md` (with a matching `[X.Y.Z]: …` reference link)
   - the `Kit version: **X.Y.Z**` line in the `AGENTS.md` managed block
2. Run the local gates:
   ```
   python tools/run_tests.py
   python scripts/standards-check/check.py
   python -m build
   ```
3. Tag and push:
   ```
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
   The tag triggers `release.yml` → tests → build → publish.

## Notes

- Current version is `0.6.0`; the first release publishes `0.6.0`. Earlier versions (`0.1.0`–`0.5.0`) are history and are not back-published to PyPI.
- The Azure DevOps home (future) cannot use Trusted Publishing; it would publish with a stored PyPI API token. Deferred — see ADR-0011.
- A future Slice 4 CI lint could enforce the version-coherence invariant in step 1.
```

- [ ] **Step 2: Verify + commit**

Run: `python scripts/standards-check/check.py` → 0/0 (a new top-level `docs/RELEASING.md` does not affect the checks).
```bash
git add docs/RELEASING.md
git commit -m "docs(slice-3): add RELEASING.md (PyPI Trusted-Publisher setup + release ritual)"
```
Trailer as above.

---

## Task B4: Final verification

**Files:** none (verification only).

- [ ] **Step 1: Whole suite via the runner**

Run: `python tools/run_tests.py`
Expected: every suite `OK`, `14/14 suites passed.`, exit 0.

- [ ] **Step 2: standards-check**

Run: `python scripts/standards-check/check.py`
Expected: `0 error(s), 0 warning(s)`.

- [ ] **Step 3: Confirm no version drift was introduced**

Confirm `src/standards/__about__.py` still reads `0.6.0` and the CHANGELOG top entry is still `## [0.6.0]` (Plan 3 introduces no version bump). No commit needed if clean.

---

## Self-Review (completed by plan author)

- **Spec coverage:** `tools/run_tests.py`→A1; `test`+`build-smoke` jobs→A2; `release.yml`→B1; ADR-0011→B2; `RELEASING.md`→B3. The spec's `build-smoke`-on-every-PR and RELEASING-as-dedicated-doc decisions are honored (A2, B3). Non-goals (no tag push, no ADO pipeline, no version bump) are enforced — no task pushes a tag or edits `__about__.py`.
- **Placeholder scan:** none — every workflow and the runner are given in full; the one execution-time confirmation (`gh-action-pypi-publish` ref) is flagged with the current-correct value, not left blank.
- **Type consistency:** the runner exposes `discover(root) -> list[Path]` and `run(paths) -> int`; `tests/test_run_tests.py` imports exactly those names; `main()` composes them. CI calls `python tools/run_tests.py` (underscore) consistently in both workflows and the docs.

---

## Follow-on

- The user's one-time PyPI Trusted-Publisher setup + `git push origin v0.6.0` to actually release.
- Azure DevOps `azure-pipelines.yml` once that repo exists (token-based publish per ADR-0011).
- Slice 4: deeper CI (content/doc-freshness/link lint, version-coherence lint).
