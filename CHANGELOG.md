# Changelog

All notable changes to the Team Repository Standards Kit are recorded here.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Pre-1.0, MINOR bumps may
include breaking changes; see [`docs/versioning-policy.md`](./docs/versioning-policy.md).

## [0.11.0] - 2026-06-01

### Added
- `standards adopt [--profile …] [target]` — non-destructive adoption onto an **existing**, non-blank repo (ADR-0013, concluding RFC-0002). Keeps adopter files: a differing kit-tracked file is kept and the kit copy is written as a `<rel>.kit-<version>` sidecar; a partial file with no managed block gets the kit block appended (content preserved); one with a block is spliced to the current contract; scaffold-once seeds only when absent. Writes the marker so the repo is `update`-ready.
- `managed.extract_block()` / `managed.has_begin_marker()` helpers.
- `tests/test_adopt.py` — adopt behavior (blank→clean, conflict→sidecar, blockless AGENTS.md→append, refuse-if-adopted, adopt→update round-trip).

### Changed
- `standards init`'s collision error now points at `standards adopt` (non-destructive) instead of only offering `--force`.
- `src/standards/init.py` — shared `_seed_scaffold_once` helper used by both `init` and `adopt`.

### Notes
- RFC-0002 is **Concluded**; the blockless-partial-file case appends the kit managed block (vs. a sidecar) so adoption actually installs the contract — see ADR-0013.

## [0.10.0] - 2026-06-01

### Added
- `standards check [target]` CLI subcommand — run the standards check from the installed CLI; it locates the bundled `check.py` and runs it against the target (ADR-0012).
- `tests/test_profiles_scaffold.py` — multi-profile dogfooding gate: `standards init --profile X` must yield a repo that passes `standards check` with zero errors **and** zero warnings, for all four profiles.
- `docs/decisions/0012-…md` — ADR-0012 recording the subprocess-the-bundled-check decision.
- `docs/rfcs/0002-…/rfc.md` — RFC-0002 (Open) investigating adoption onto existing non-blank repos.
- `docs/templates/decisions-readme-template.md` — generic, link-safe decisions README seeded into adopters.

### Changed
- `standards init` now scaffolds a complete, CI-clean repo for every profile: it seeds `docs/00-overview.md`, `docs/10-glossary.md`, and the `docs/{decisions,discovery,rfcs}/README.md` folder explainers; ticks the checklist universal-core boxes and fills its metadata; and strips the leading comment + stamps the adopted date into the `ai/` starters so the freshness check passes on day one.
- `scripts/standards-check/check.py` accepts an optional `target` and exposes `run_checks()` (behavior unchanged when run with no argument).
- `docs/templates/README.md` presents scaffold-source templates as auto-seeded (clearing broken-link warnings in adopters).

### Notes
- `standards check` is implemented by subprocessing the bundled check rather than refactoring the checks into the importable package (ADR-0012); the vendored `python scripts/standards-check/check.py` path is unchanged.

## [0.9.0] - 2026-05-31

### Added
- `/standards-check` skill (Claude + Copilot) — run the checks and fix findings before pushing.
- SKILL.md <-> prompt.md parity and skills-index-drift guards in `standards-check`.
- Canonical `docs/templates/skill-template.md` + `skill-prompt-template.md`.
- An `## Available skills` index in `AGENTS.md` and an end-of-session `/standards-check` step.

### Changed
- The four existing skill wrappers polished to one consistent shape.

## [0.8.0] - 2026-05-31

### Added
- Version-coherence guard (`tools/check_version_coherence.py`) wired into a kit-only `kit-guards.yml` workflow and the release workflow (which also verifies the tag matches the version).
- `standards-check` discovery check: every `status: promoted` item must have a `promoted_to:` path that exists.

### Changed
- Handoff freshness warning tightened from 7 to 5 days; the Stop-hook nudge is louder and also fires on a stale handoff.

## [0.7.0] - 2026-05-30

### Added
- `standards-check` v2 content checks: internal link + anchor resolution, residual-placeholder lint for ADRs/RFCs, and SKILL.md format lint. New checks are errors in the kit and warnings (escalatable via `.standards-kit.json` `"check"`) in adopters.
- `scripts/standards-check/` split into a `checks/` package (structural/links/content/skills).

## [0.6.0] - 2026-05-29

### Added
- `standards update [target] [--dry-run]` — reconciles an adopted repo with the running kit version: hash-guarded overwrite of unmodified kit-tracked files, managed-block splice for partial files, `<path>.kit-<version>` sidecars on conflict, never destructive. Reports updated/spliced/added/conflicts/unchanged/removed.
- `src/standards/managed.py` — single managed-region block primitives (find/splice/hash) per ADR-0010.
- Partial/managed-region ownership class: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` carry a kit-owned `<!-- BEGIN/END kit-managed -->` block; the rest of each file is downstream-owned.
- `docs/decisions/0010-…md` — ADR-0010 (managed-region sentinel convention).

### Changed
- `AGENTS.md` restructured: the agent contract lives in the `agents-core` managed block; repo-specifics moved to a downstream-owned `## About this repository` section.
- `init` now records partial files under the marker's `managed` table (block hash) and **refuses to overwrite pre-existing kit files with differing content** without `force` (first-init guard; closes the PR #2 data-loss gap).

### Notes
- One managed block per file (multi-block deferred). `standards set-profile` and the PyPI release workflow remain future work (Plan 3).

## [0.5.0] - 2026-05-29

### Added
- `pyproject.toml` — the kit is now a `pip`/`pipx`/`uvx`-installable package (`repo-standards-kit`), runtime zero-dependency, hatchling build backend, console entry point `standards`.
- `src/standards/` — distribution CLI: `payload`, `manifest`, `marker`, `init`, `cli` modules.
- `standards init [--profile …] [target]` — adopts the kit into a repo: vendors kit-tracked files, scaffolds `ai/` starters + `docs/STANDARDS-CHECKLIST.md` (profile-filled, copy-if-absent), writes the `.standards-kit.json` version+hash marker.
- `tests/` — distribution-package unit + CLI suite.
- `docs/decisions/0009-…md` — ADR-0009 recording the PyPI standards-CLI distribution decision (RFC-0001).

### Notes
- Marker format is JSON, not the `.standards-kit.toml` named in RFC-0001 (stdlib has no TOML writer; JSON keeps the zero-dependency stance). Recorded in ADR-0009.
- `standards update` and the partial / managed-region ownership class are deferred to Plan 2.

## [0.4.0] - 2026-05-28

### Added
- `scripts/promote-discovery/promote_discovery.py` — stdlib script with `list` subcommand (default verbose / `--check` terse for hook mode) and `promote <path> --to <target>` subcommand (flips one discovery item's `status: raw` → `promoted` and sets `promoted_to: <target>`).
- `scripts/promote-discovery/test_promote_discovery.py` — 16 stdlib `unittest` cases.
- `scripts/promote-discovery/README.md` — script contract, exit codes, invocation surfaces.
- `.claude/skills/promote-discovery/SKILL.md` — Claude Code slash command wrapper.
- `.github/prompts/promote-discovery.prompt.md` — GitHub Copilot Chat wrapper.

### Changed
- `.claude/settings.json` — added a `SessionStart` hook entry that invokes `promote-discovery list --check`. The existing `Stop` hook for `update-handoff` is unchanged.
- `AGENTS.md` — kit version 0.3.0 → 0.4.0; queued-slices section drops the Slice 2.6 entry (it shipped); Slice 3 + Slice 4 unchanged.
- `ai/current-state.md` — Slice 2.6 in What works; Slice 3 in What's in progress.

## [0.3.0] - 2026-05-28

### Added
- `scripts/update-handoff/update_handoff.py` — stdlib script with write mode (generates draft `ai/handoff.md` from git state) and `--check` mode (advisory stderr line for Claude Code Stop hook).
- `scripts/update-handoff/test_update_handoff.py` — 10 stdlib `unittest` cases.
- `scripts/update-handoff/README.md` — script contract and invocation surfaces.
- `.claude/settings.json` — Claude Code Stop hook config (kit's first hook artifact).
- `.claude/skills/update-handoff/SKILL.md` — Claude Code slash command wrapper.
- `.github/prompts/update-handoff.prompt.md` — GitHub Copilot Chat wrapper.
- `.gitignore` — added `__pycache__/` and `*.pyc` entries (Slice 2.5 pre-flight).
- `docs/decisions/0008-…md` — ADR-0008 recording the hook-invokes-script-in-check-mode pattern (companion to ADR-0007).

### Changed
- `AGENTS.md` — kit version 0.2.0 → 0.3.0; queued-slices section moves `promote-discovery` to Slice 2.6.
- `ai/current-state.md` — Slice 2.5 in What works; Slice 2.6 in What's in progress.

## [0.2.0] - 2026-05-28

### Added
- `scripts/_doc_lib/helpers.py` — internal helper functions (`repo_root`, `next_nnnn`, `slugify`, `fill_template`).
- `scripts/new-doc/new-adr.py` — scaffolds a new MADR 3.0 ADR with next NNNN, today's date, and the title.
- `scripts/new-doc/new-rfc.py` — scaffolds a new RFC folder with `rfc.md`, next NNNN, and today as `opened`.
- `scripts/new-doc/test_helpers.py` and `scripts/new-doc/test_cli.py` — stdlib `unittest` coverage.
- `.claude/skills/new-adr/SKILL.md` and `.claude/skills/new-rfc/SKILL.md` — Claude Code wrappers.
- `.github/prompts/new-adr.prompt.md` and `.github/prompts/new-rfc.prompt.md` — GitHub Copilot Chat wrappers.
- `docs/decisions/0007-…md` — ADR-0007 recording the wrapper-over-script form factor (produced as the dogfooded smoke test).

### Changed
- `AGENTS.md` — kit version bumped to 0.2.0; out-of-scope section moves Hooks to Slice 2.5.
- `ai/open-questions.md` — Q-1 marked `answered`.

## [0.1.0] — 2026-05-28

Initial Slice 1 release: templates and standards content.

### Added

- `docs/STANDARDS.md` — authoritative spec covering repo profiles, tiered doc
  requirements (Required / Expected / Optional / N/A), the `ai/` directory
  contract, ADR/RFC/discovery rules, the AGENTS.md pattern, the waiver
  mechanism, and the v1 standards check workflow specification.
- `AGENTS.md` — canonical agent contract (root). Thin `CLAUDE.md` and
  `.github/copilot-instructions.md` pointers added per ADR 0006.
- Four repo profiles: `application`, `library`, `infra`, `data`. Profile
  matrix governs Required/Expected/Optional/N/A per numbered doc.
- 21 templates under `docs/templates/`:
  - ADR (MADR 3.0), RFC.
  - Discovery soft-landing templates (`discovery-meeting-notes`,
    `discovery-use-case`).
  - 11 numbered-doc skeletons (`overview` through `glossary`).
  - 4 `ai/` starters (`current-state`, `next-actions`, `open-questions`,
    `handoff`).
  - 3 profile extras (`versioning-policy`, `environments`, `data-contract`).
  - Per-repo governance templates (`STANDARDS.md.template`,
    `STANDARDS-CHECKLIST.md.template`).
- Bootstrap ADRs 0001–0006 capturing every Slice 1 design decision:
  - 0001 Record architecture decisions.
  - 0002 Adopt MADR 3.0 as the ADR format.
  - 0003 Adopt a repo-profile model with tiered doc requirements.
  - 0004 Define the `ai/` directory as committed, shared, rolling state.
  - 0005 Split discovery and RFCs into separate folders.
  - 0006 Adopt the AGENTS.md pattern with thin tool-specific pointers.
- `docs/discovery/`, `docs/rfcs/`, `docs/decisions/`, `docs/templates/`
  folder READMEs explaining each folder's contract.
- The kit applies its own `library` profile to itself: `docs/00-overview.md`,
  `02-architecture.md`, `04-api-and-integrations.md`, `07-testing.md`,
  `08-security-and-compliance.md`, `10-glossary.md`, `versioning-policy.md`,
  and `ai/*.md` (all four).
- `.github/pull_request_template.md` with a Standards Impact block.
- `.github/workflows/repo-standards.yml` invoking
  `scripts/standards-check/check.py` — a stdlib-only Python script
  implementing the v1 standards check (universal core, profile, waivers,
  `ai/` freshness, ADR + RFC filename and status).

### Notes for adopters (pre-1.0)

- The kit is **pre-1.0**. MINOR bumps may include breaking changes.
- Slice 2 (AI Skills + Hooks), Slice 3 (distribution), and Slice 4 (deeper CI)
  are queued. Their work may move cells in the profile matrix, change the v1
  standards-check rules, or introduce new artifact types. Pin a version.

[0.11.0]: https://github.com/swanson-dev/Repo-Standards-Kit/releases/tag/v0.11.0
[0.10.0]: https://example.invalid/releases/tag/v0.10.0
[0.9.0]: https://github.com/swanson-dev/Repo-Standards-Kit/releases/tag/v0.9.0
[0.8.0]: https://example.invalid/releases/tag/v0.8.0
[0.7.0]: https://example.invalid/releases/tag/v0.7.0
[0.6.0]: https://example.invalid/releases/tag/v0.6.0
[0.5.0]: https://example.invalid/releases/tag/v0.5.0
[0.4.0]: https://example.invalid/releases/tag/v0.4.0
[0.3.0]: https://example.invalid/releases/tag/v0.3.0
[0.2.0]: https://example.invalid/releases/tag/v0.2.0
[0.1.0]: https://example.invalid/releases/tag/v0.1.0
