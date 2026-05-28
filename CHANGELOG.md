# Changelog

All notable changes to the Team Repository Standards Kit are recorded here.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Pre-1.0, MINOR bumps may
include breaking changes; see [`docs/versioning-policy.md`](./docs/versioning-policy.md).

## [Unreleased]

_No unreleased changes yet._

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

[Unreleased]: https://example.invalid/compare/v0.1.0...HEAD
[0.1.0]: https://example.invalid/releases/tag/v0.1.0
