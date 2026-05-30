---
status: Accepted
date: 2026-05-30
deciders: swanson-dev
consulted: team
informed: team
---

# 0011. Publish to PyPI via GitHub Actions Trusted Publishing

## Context and Problem Statement

The `repo-standards-kit` package (ADR-0009) needs a release path to PyPI. The kit's source will eventually live in both an Azure DevOps repo and a public GitHub repo; distribution stays PyPI per RFC-0001. We must choose how releases are built and published.

The primary tension is between operational simplicity (a single, auditable release action) and the constraint that the two eventual repo homes have different OIDC trust relationships with PyPI.

## Decision Drivers

- No long-lived secrets if avoidable — a leaked PyPI token is an unacceptable supply-chain risk.
- Release should be a simple, auditable action: push a tag, done.
- CI tooling (`tools/run_tests.py`, `scripts/standards-check/check.py`) should be portable plain-Python so a future Azure DevOps pipeline can reuse it unchanged.

## Considered Options

- **Option A** — GitHub Actions + PyPI Trusted Publishing (OIDC, tokenless) — **chosen**
- **Option B** — GitHub Actions + a stored PyPI API token
- **Option C** — Publish from Azure DevOps Pipelines

## Decision Outcome

Chosen option: **Option A — GitHub Actions + PyPI Trusted Publishing (OIDC)**, because it eliminates the need for any stored PyPI credential while keeping the release path to a single auditable action (push a `v*` tag).

The workflow (`.github/workflows/release.yml`) fires on a `v*` tag push, is gated by a `pypi` GitHub Environment and a passing `python tools/run_tests.py` run, then builds with hatchling and publishes via `pypa/gh-action-pypi-publish`. CI test execution and `standards-check` are portable plain-Python so a future ADO pipeline can reuse them unchanged.

### Consequences

- **Good:** No stored PyPI token to leak; release equals pushing a tag; the GitHub Environment + tag provide a clear, auditable release trail.
- **Neutral/cost:** Requires a one-time PyPI Trusted Publisher configuration (documented in `docs/RELEASING.md`); the workflow is inert until that setup is complete and a tag is pushed.
- **Deferred:** Azure DevOps Pipelines cannot use PyPI Trusted Publishing — PyPI does not support ADO as an OIDC identity provider. When the kit gains an ADO home, a publish path from ADO would require a stored PyPI API token in a variable group (Option B applied to ADO). That is out of scope until the ADO repo exists. Option B for GitHub was rejected in favor of tokenless OIDC.

## More Information

- Setup and release steps: [`docs/RELEASING.md`](../RELEASING.md)
- Design spec: [`docs/superpowers/specs/2026-05-30-release-pypi-and-portable-ci-design.md`](../superpowers/specs/2026-05-30-release-pypi-and-portable-ci-design.md)
- Companion ADR: [ADR-0009](./0009-distribute-the-kit-as-a-pypi-standards-cli-with-vendored-copy-sync.md)
