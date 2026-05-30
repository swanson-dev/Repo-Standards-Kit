---
last_updated: 2026-05-30
last_updated_by: josh
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
  - Decisions: RFC-0001 (mechanism), ADR-0009 (PyPI CLI + sync model), ADR-0010 (managed-region sentinels). 97 tests green; standards-check 0/0.

## What's in progress

| Feature | Branch | Owner | Target |
|---|---|---|---|
| Slice 3 Plan 3 (release): PyPI publish workflow + CI test wiring + tag v0.6.0/backfill v0.5.0 | _not started_ | josh | next session |

## What's blocked

- _Nothing blocked._ `scaffold-new-repo` (formerly blocked on the distribution mechanism, `ai/open-questions.md#q-2`) is subsumed by `standards init` and shipped in Plan 1; Q-2 is answered.

## Active environments

| Environment | URL / identifier | Health |
|---|---|---|
| local | `e:\DevProfile\Repo-Standards-Kit` | green |
