---
last_updated: 2026-10-20
last_updated_by: claude
---

# Current State

## What works

- The kit ships a complete documentation standard for four repo profiles (application, library, data, documentation; `infra` is an alias for application since ADR-0025) with a Required / Expected / Optional / N/A matrix.
- 28 templates under `docs/templates/` cover every artifact the kit defines: ADR (MADR 3.0), RFC, discovery starters, optional knowledge-lane starters, 11 numbered-doc skeletons, 4 `ai/` starters, 4 profile extras, and 2 per-repo governance templates.
- 6 bootstrap ADRs (`docs/decisions/0001`–`0006`) capture every Slice 1 decision in the kit's own format.
- The kit applies its own `library` profile to itself: every Required and Expected doc is present, with waivers recorded for the genuinely-skipped ones.
- `AGENTS.md` + thin `CLAUDE.md` + `.github/copilot-instructions.md` pattern is in place at the kit level.
- `scripts/standards-check/check.py` (stdlib-only Python) implements all six v1 checks and runs green against the kit itself (`0 errors, 0 warnings`).
- `.github/workflows/repo-standards.yml` invokes the check on push and pull_request.
- `CHANGELOG.md` is started at v0.1.0 (Keep-a-Changelog), closing `ai/open-questions.md#q-3`.
- `new-adr` and `new-rfc` scaffolding scripts with Claude/Copilot wrappers (Slice 2) — stdlib Python under `scripts/new-doc/`, dual SKILL.md + prompt.md surfaces, closing `ai/open-questions.md#q-1`.
- `standard-update-handoff` command surface + `update-handoff` Stop hook for the AGENTS.md end-of-session contract (Slice 2.5/M6).
- **Slice 3 distribution (v0.5.0 + v0.6.0).** The kit is a pip/`pipx`/`uvx`-installable, zero-dependency package (`repo-standards-kit`, hatchling) with a `standards` CLI under `src/standards/`:
  - `standards init [--profile …] [target]` — vendors kit content into a repo (three ownership classes: kit-tracked / scaffold-once / partial managed-region), scaffolds `ai/` starters + a profile-filled checklist, writes the `.standards-kit.json` version+hash marker, and refuses to overwrite differing pre-existing files without `--force`.
  - `standards update [target] [--dry-run]` — reconciles an adopted repo against the running version: hash-guarded overwrite of untouched kit-tracked files, managed-block splice for partial files, `<path>.kit-<version>` sidecars on conflict (never destructive), and a 0.5.0→0.6.0 markerless-migration path.
  - Decisions: RFC-0001 (mechanism), ADR-0009 (PyPI CLI + sync model), ADR-0010 (managed-region sentinels). standards-check 0/0.
- **Slice 3 Plan 3 (release infrastructure, no version bump).** The package is now releasable to PyPI without ever having been published:
  - `tools/run_tests.py` — portable stdlib test runner (subprocess per suite, zero-dependency), the canonical `python tools/run_tests.py` command. 14/14 suites green.
  - `.github/workflows/repo-standards.yml` runs `check` + a `test` matrix (Python 3.9–3.12) + a `build-smoke` job that builds the wheel, installs it in a venv, runs `standards init`, and asserts the bundled `standards/_payload` shipped.
  - `.github/workflows/release.yml` — tag-triggered (`v*`) PyPI **Trusted-Publishing (OIDC, tokenless)** release, gated on tests + build, scoped to a `pypi` GitHub Environment.
  - Decisions/docs: ADR-0011 (publish via GitHub Actions Trusted Publishing), `docs/RELEASING.md` (one-time setup + release ritual).
- **Slice 4 deeper CI enforcement (v0.7.0 → v0.9.0).** `standards-check` grew from structural to content-level, plus release/process guardrails and a guarded skill surface:
  - `scripts/standards-check/checks/` package (orchestrator + `structural`/`links`/`content`/`skills`/`_text`). Content checks: internal link+anchor resolution, ADR/RFC placeholder + CHANGELOG-shape lint, and SKILL.md-to-prompt parity + skills-index drift. **Severity model:** error in the kit, warn-default in adopters, escalatable per-check via a `.standards-kit.json` check map.
  - `tools/check_version_coherence.py` (kit-only) — `__about__` ↔ CHANGELOG ↔ `AGENTS.md` Kit-version must agree; run by `.github/workflows/kit-guards.yml` (PR) + a `release.yml` tag-gate.
  - Handoff freshness tightened 7→5 days (warning); louder Stop-hook nudge with a staleness trigger.
  - New `/standards-check` skill (Claude + Copilot), skill templates, and an `## Available skills` index in `AGENTS.md`.
  - 23/23 test suites green; standards-check 0/0; version coherence OK at 0.9.0.
- **Milestone roadmap (v0.16.0).** PR #18 has landed on `main` and local `v0.16.0` is tagged. The implementation-plan template now carries a `## Roadmap` milestone table, and the kit dogfoods the roadmap in `docs/05-implementation-plan.md` (RFC-0003, ADR-0016).
- **Workflow simplification + AI readiness (v0.17.0).** Discovery remains a normal tracked markdown folder under `docs/discovery/`; the capture/promote command workflow, intake scaffold, `captured/` folder, discovery SessionStart hooks, and `promoted_to` standards check have been removed from the shipped kit payload. ADR-0017 supersedes ADR-0014 and ADR-0015.
- **CLI help polish (v0.17.0).** The `standards` CLI now has richer argparse workflow help, concrete subcommand examples, a `standards help [command]` alias, and clearer `update` guidance for repos that have not been adopted yet.
- **AI tooling polish (v0.17.0).** `scripts/new-doc/new-skill.py` scaffolds paired Claude/Copilot skill files and updates the `AGENTS.md` skills index; `skill-format` checks also cover the Copilot pointer and local Claude hook script references. Agent-readiness guidance now lives in `docs/STANDARDS.md` and the shipped standards template.
- **v0.17.0 published.** The `v0.17.0` tag published successfully to PyPI and now has a GitHub Release with the sdist and wheel attached.
- **M4 release/reporting hygiene (v0.18.0 published).** The `v0.18.0` tag published successfully to PyPI and has a GitHub Release with the sdist, wheel, and publish attestations attached. The tag-triggered release workflow creates/updates GitHub Releases, `standards-check` has opt-in `--external-links` and `--freshness-report` modes, historical changelog placeholder links are cleaned up, and `ai/` freshness now covers `current-state`, `next-actions`, and `handoff`.
- **v1.0.0 published.** The `v1.0.0` tag published successfully to PyPI and has a GitHub Release with the sdist, wheel, and publish attestations attached. Generated downstream fixture repos now validate all four profiles through `init`, `check`, `update`, and `check` again; release/kit-guard workflows run the v1 gate; the manual external-link workflow provides opt-in networked audits; docs now describe the stable SemVer baseline and published-package smoke.
- **M6 adoption assistant + AI continuity (v1.1.0 published).** The CLI now includes `standards doctor [--recommend]`, `standards new-skill`, and `standards commands`; optional templates cover discovery notes, meetings, artifact indexes, design notes, incidents, troubleshooting, and guides. The AI surface also includes `standard-update-handoff`, `standard-get-session-context`, and `standard-compact-snapshot`, plus an advisory read-only SessionStart context hook. RFC-0004/ADR-0019 and RFC-0005/ADR-0020 record the decisions. The `v1.1.0` tag published successfully to PyPI and has a GitHub Release with the sdist, wheel, and publish attestations attached. Published-package smoke passed from a clean temporary environment.
- **v1.2.0 published.** The `documentation` profile is now a supported profile for docs/spec repos whose implementation lives elsewhere. The profile keeps the universal core, adds `docs/source-map.md` as its profile extra, updates CLI/check/profile readiness plumbing, and records RFC-0006/ADR-0021. The `v1.2.0` tag published successfully to PyPI and has a GitHub Release with the sdist, wheel, and publish attestations attached. Published-package smoke passed from a clean temporary environment using `standards init --profile documentation`.
- **v1.3.0 published.** `standards init` and `standards adopt` now seed missing root `README.md` and `CHANGELOG.md` files, preserve existing ones, and ship an advisory `standard-update-changelog` skill plus Stop-hook reminder. The `v1.3.0` tag published successfully to PyPI and has a GitHub Release with the sdist, wheel, and publish attestations attached. Published-package smoke passed from a clean temporary environment using `standards init --profile documentation` without manually seeding README/CHANGELOG.
- **Standards-check traversal fix (v1.3.0).** Internal and external markdown link checks now skip common dependency, build, and cache directories such as `node_modules/`, `dist/`, `build/`, `.venv/`, and `.next/`.
- **v1.4.0 published (M8 automation engine).** PR #21 merged as `f7bcc26`, and the `v1.4.0` tag published to PyPI with a GitHub Release (sdist, wheel, attestations). It ships the drift rules, the block-once Stop hook, the CI drift check, Copilot support (one hook file per repo via `--agents`), and a once-per-session block on CI runners.
- **v1.5.0 published (M9 setup wizard).** PR #22 merged as `3d96ac2`, and the `v1.5.0` tag published to PyPI with a GitHub Release (sdist, wheel, attestations). It ships four profiles (`infra` kept as an alias for `application`), profiles that combine by the strongest tier with setup creating and ticking their docs, the bare `standards` menu and setup wizard, and `standards change`. Published-package smoke passed from a clean environment.
- **v1.5.1 published (code-review hardening).** PR #25 merged as `e49eb5d`, and the `v1.5.1` tag published to PyPI with a GitHub Release; latest on PyPI is `repo-standards-kit` 1.5.1. A patch over v1.5.0 from a code review of the CLI and `update` paths (fixes first merged in PR #24): bare `standards` now checks real console handles via `GetConsoleMode` (Windows reported the `NUL` device as a tty, so a redirected `standards < NUL` opened the menu), `standards update` prunes marker entries for files the kit no longer ships so the `removed` count converges, and corrupt or profile-less markers fail with a clear error and exit 2 instead of a traceback.

## What's in progress

| Feature | Branch | Owner | Target |
|---|---|---|---|
| RFC-0008 distribution (pip CLI for repo content + plugin for skills and hooks) | docs/rfc-0007-automation-engine | Josh Swanson | design approved; cloud-agent and Codex checks, then ADR-0024 |
| RFC-0010 retrospectives (`standard-retro` skill) | docs/rfc-0007-automation-engine | Josh Swanson | draft; build after RFC-0007 to RFC-0009, then ADR-0026 |
| ADR-0022 daily changelog grouping + managed `AGENTS.md` simplification (parked, not merged) | feat/adr-0022-daily-changelog-grouping | Josh Swanson | land via PR |

## What's blocked

- _Nothing blocked._ `scaffold-new-repo` (formerly blocked on the distribution mechanism, `ai/open-questions.md#q-2`) is subsumed by `standards init` and shipped in Plan 1; Q-2 is answered.

## Active environments

| Environment | URL / identifier | Health |
|---|---|---|
| local | `e:\DevProfile\Repo-Standards-Kit` | green |
