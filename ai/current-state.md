---
last_updated: 2026-06-01
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
- **Slice 4 deeper CI enforcement (v0.7.0 → v0.9.0).** `standards-check` grew from structural to content-level, plus release/process guardrails and a guarded skill surface:
  - `scripts/standards-check/checks/` package (orchestrator + `structural`/`links`/`content`/`skills`/`discovery`/`_text`). Content checks: internal link+anchor resolution, ADR/RFC placeholder + CHANGELOG-shape lint, SKILL.md format + SKILL.md⟺prompt.md parity + skills-index-drift, discovery `promoted_to`-existence. **Severity model:** error in the kit, warn-default in adopters, escalatable per-check via a `"check"` map in `.standards-kit.json`.
  - `tools/check_version_coherence.py` (kit-only) — `__about__` ↔ CHANGELOG ↔ `AGENTS.md` Kit-version must agree; run by `.github/workflows/kit-guards.yml` (PR) + a `release.yml` tag-gate.
  - Handoff freshness tightened 7→5 days (warning); louder Stop-hook nudge with a staleness trigger.
  - New `/standards-check` skill (Claude + Copilot), skill templates, and an `## Available skills` index in `AGENTS.md`.
  - 23/23 test suites green; standards-check 0/0; version coherence OK at 0.9.0.

## What's in progress

| Feature | Branch | Owner | Target |
|---|---|---|---|
| **Slices 5 + 6, v0.11.0** — on branch, not yet merged. Slice 5: `standards check [target]` subcommand (ADR-0012) + multi-profile dogfooding gate (`init` scaffolds a CI-green repo for all four profiles). Slice 6: `standards adopt` — non-destructive adoption onto existing non-blank repos (RFC-0002 **Concluded**, ADR-0013): keeps adopter files, sidecars differing kit-tracked files, appends/splices the managed block, seeds scaffold-once when absent. | `feat/slice-5-hardening` | josh | PR → main |
| _Otherwise idle._ Slices 1–4 shipped (kit at **v0.9.0** on `main`). Releasing is a maintainer action (PyPI Trusted-Publisher setup per `docs/RELEASING.md`, then `git tag && git push`). Backlog: external-link liveness, doc-freshness reporting, a `new-skill` scaffolder. | — | josh | — |

## What's blocked

- _Nothing blocked._ `scaffold-new-repo` (formerly blocked on the distribution mechanism, `ai/open-questions.md#q-2`) is subsumed by `standards init` and shipped in Plan 1; Q-2 is answered.

## Active environments

| Environment | URL / identifier | Health |
|---|---|---|
| local | `e:\DevProfile\Repo-Standards-Kit` | green |
