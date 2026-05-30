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
2. Point the new CHANGELOG reference link at the real tag (the entries currently use an `https://example.invalid/…` placeholder): set `[X.Y.Z]: https://github.com/swanson-dev/Repo-Standards-Kit/releases/tag/vX.Y.Z`.
3. Run the local gates:
   ```
   python tools/run_tests.py
   python scripts/standards-check/check.py
   python -m build
   ```
4. Tag and push:
   ```
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
   The tag triggers `release.yml` → tests → build → publish.

## Notes

- Current version is `0.6.0`; the first release publishes `0.6.0`. Earlier versions (`0.1.0`–`0.5.0`) are history and are not back-published to PyPI.
- The Azure DevOps home (future) cannot use Trusted Publishing; it would publish with a stored PyPI API token. Deferred — see ADR-0011.
- A future Slice 4 CI lint could enforce the version-coherence invariant in step 1.
