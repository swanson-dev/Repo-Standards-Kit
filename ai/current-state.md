---
last_updated: 2026-05-28
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

## What's in progress

| Feature | Branch | Owner | Target |
|---|---|---|---|
| Tag `v0.2.0` and open Slice 2.5 (Hooks: `update-handoff`, `promote-discovery`) | `ai-skills-implementation` | josh | next session |

## What's blocked

- `scaffold-new-repo` Skill — blocked on Slice 3 distribution mechanism (see `ai/open-questions.md#q-2`).

## Active environments

| Environment | URL / identifier | Health |
|---|---|---|
| local | `e:\DevProfile\Repo-Standards-Kit` | green |
