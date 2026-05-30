---
last_updated: 2026-05-30
last_updated_by: swanson-dev
---

# Current State

## What works

- The kit ships a complete documentation standard for four repo profiles (application, library, infra, data) with a Required / Expected / Optional / N/A matrix.
- 21 templates under `docs/templates/` cover every artifact the kit defines: ADR (MADR 3.0), RFC, discovery starters, 11 numbered-doc skeletons, 4 `ai/` starters, 3 profile extras, and 2 per-repo governance templates.
- 6 bootstrap ADRs (`docs/decisions/0001`–`0006`) capture every Slice 1 decision in the kit's own format.
- The kit applies its own `library` profile to itself: every Required and Expected doc is present, with waivers recorded for the genuinely-skipped ones.
- `AGENTS.md` + thin `CLAUDE.md` + `.github/copilot-instructions.md` pattern is in place at the kit level.
- `scripts/standards-check/check.py` (stdlib-only Python) implements all six v1 checks and runs green against the kit itself (`0 errors, 0 warnings`).
- `.github/workflows/repo-standards.yml` invokes the check on push and pull_request.
- `CHANGELOG.md` is started at v0.1.0 (Keep-a-Changelog), closing `ai/open-questions.md#q-3`.
- `new-adr` and `new-rfc` scaffolding scripts with Claude/Copilot wrappers (Slice 2) — stdlib Python under `scripts/new-doc/`, dual SKILL.md + prompt.md surfaces, closing `ai/open-questions.md#q-1`.
- `update-handoff` slash command + Stop hook for the AGENTS.md end-of-session contract (Slice 2.5).
- `promote-discovery` slash command + SessionStart hook for the AGENTS.md end-of-session discovery-promotion contract (Slice 2.6).
- **Slice 3 distribution (v0.5.0 + v0.6.0).** The kit is a pip/`pipx`/`uvx`-installable, zero-dependency package (`repo-standards-kit`, hatchling) with a `standards` CLI under `src/standards/`:
  - `standards init [--profile …] [target]` — vendors kit content into a repo (three ownership classes: kit-tracked / scaffold-once / partial managed-region), scaffolds `ai/` starters + a profile-filled checklist, writes the `.standards-kit.json` version+hash marker, and refuses to overwrite differing pre-existing files without `--force`.
  - `standards update [target] [--dry-run]` — reconciles an adopted repo against the running version: hash-guarded overwrite of untouched kit-tracked files, managed-block splice for partial files, `<path>.kit-<version>` sidecars on conflict (never destructive), and a 0.5.0→0.6.0 markerless-migration path.
  - Decisions: RFC-0001 (mechanism), ADR-0009 (PyPI CLI + sync model), ADR-0010 (managed-region sentinels). standards-check 0/0.
- **Slice 3 Plan 3 (release infrastructure, no version bump).** The package is now releasable to PyPI without ever having been published:
  - `tools/run_tests.py` — portable stdlib test runner (subprocess per suite, zero-dependency), the canonical `python tools/run_tests.py` command. 14/14 suites green.
  - `.github/workflows/repo-standards.yml` runs `check` + a `test` matrix (Python 3.9–3.12) + a `build-smoke` job that builds the wheel, installs it in a venv, runs `standards init`, and asserts the bundled `standards/_payload` shipped.
  - `.github/workflows/release.yml` — tag-triggered (`v*`) PyPI **Trusted-Publishing (OIDC, tokenless)** release, gated on tests + build, scoped to a `pypi` GitHub Environment. Inert until the maintainer does the one-time PyPI setup and pushes a tag.
  - Decisions/docs: ADR-0011 (publish via GitHub Actions Trusted Publishing), `docs/RELEASING.md` (one-time setup + release ritual).

## What's in progress

| Feature | Branch | Owner | Target |
|---|---|---|---|
| _Nothing in flight._ Slice 3 is fully shipped. Releasing v0.6.0 is a maintainer action (PyPI Trusted-Publisher setup per `docs/RELEASING.md`, then `git tag v0.6.0 && git push`), not open dev work. Slice 4 (deeper CI) is backlog. | — | josh | — |

## What's blocked

- _Nothing blocked._ `scaffold-new-repo` (formerly blocked on the distribution mechanism, `ai/open-questions.md#q-2`) is subsumed by `standards init` and shipped in Plan 1; Q-2 is answered.

## Active environments

| Environment | URL / identifier | Health |
|---|---|---|
| local | `e:\DevProfile\Repo-Standards-Kit` | green |
