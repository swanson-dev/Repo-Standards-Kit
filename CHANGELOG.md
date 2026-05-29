# Changelog

All notable changes to the Team Repository Standards Kit are recorded here.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Pre-1.0, MINOR bumps may
include breaking changes; see [`docs/versioning-policy.md`](./docs/versioning-policy.md).

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

[0.5.0]: https://example.invalid/releases/tag/v0.5.0
[0.4.0]: https://example.invalid/releases/tag/v0.4.0
[0.3.0]: https://example.invalid/releases/tag/v0.3.0
[0.2.0]: https://example.invalid/releases/tag/v0.2.0
[0.1.0]: https://example.invalid/releases/tag/v0.1.0
