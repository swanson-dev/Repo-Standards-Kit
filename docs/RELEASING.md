# Releasing `repo-standards-kit`

The package is published to PyPI by `.github/workflows/release.yml`, which fires
on a `v*` tag push and publishes via Trusted Publishing (OIDC). After PyPI
publishing succeeds, the workflow creates or updates the matching GitHub Release
and attaches the built `dist/*` artifacts. There is no stored PyPI token. See
[ADR-0011](./decisions/0011-publish-to-pypi-via-github-actions-trusted-publishing.md).

## One-time setup

1. Create or claim the PyPI project `repo-standards-kit`.
2. In the project's Publishing settings, add a Trusted Publisher:
   - Owner: `swanson-dev`
   - Repository: `Repo-Standards-Kit`
   - Workflow filename: `release.yml`
   - Environment: `pypi`
3. In GitHub repo settings, create an Environment named `pypi`.

For the very first release, use PyPI's pending publisher flow so the project is
created on first publish.

## Cutting a release

1. Confirm version coherence. These three must agree:
   - `src/standards/__about__.py` (`__version__`)
   - The top numeric `## [X.Y.Z]` entry in `CHANGELOG.md`
   - The `Kit version: **X.Y.Z**` line in the `AGENTS.md` managed block
2. Point the new CHANGELOG reference link at the real tag:
   `[X.Y.Z]: https://github.com/swanson-dev/Repo-Standards-Kit/releases/tag/vX.Y.Z`
3. Run the local gates:
   ```sh
   python tools/run_tests.py
   python scripts/standards-check/check.py
   python tools/check_version_coherence.py
   python -m build
   ```
4. Tag and push:
   ```sh
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```

The tag triggers `release.yml`: tests, build, PyPI publish, then GitHub Release
creation with the sdist and wheel attached.

## Notes

- The current release version is the value shared by `src/standards/__about__.py`,
  the top numeric `CHANGELOG.md` entry, and the `AGENTS.md` kit-managed block.
- GitHub Release pages are a convenience surface for release notes and artifacts;
  PyPI remains the distribution source of truth.
- Earlier pre-publish versions (`0.1.0`-`0.5.0`) are history and are not
  back-published to PyPI.
- The Azure DevOps home, if added later, cannot use Trusted Publishing because
  PyPI does not support Azure DevOps as an OIDC provider. It would publish with
  a stored PyPI API token; see ADR-0011.
- Version coherence is enforced locally by `tools/check_version_coherence.py`
  and in CI by the kit guard workflows.
