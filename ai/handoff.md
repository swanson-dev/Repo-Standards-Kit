---
written: 2026-05-31T18:30:00-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**Slice 4 (deeper CI enforcement) is fully shipped and on `main` at v0.9.0**, across three sequential PRs:
- **Plan 1 (v0.7.0, PR #7)** — `standards-check` v2: split `check.py` into a `checks/` package and added body-level checks (internal link+anchor resolution, ADR/RFC placeholder + CHANGELOG-shape lint, SKILL.md format lint). Introduced the **kit-vs-adopter severity model** (error in the kit / warn-default in adopters, escalatable per-check via a `"check"` map in `.standards-kit.json`).
- **Plan 2 (v0.8.0, PR #8)** — guardrails: a kit-only **version-coherence** tool (`tools/check_version_coherence.py`) wired into a non-shipped `kit-guards.yml` + a `release.yml` tag-gate; **handoff freshness tightened 7→5 days** + a louder Stop-hook nudge with a staleness trigger; a shipped **discovery `promoted_to`-existence** check.
- **Plan 3 (v0.9.0, PR #9)** — skills surface: a new `/standards-check` skill (Claude + Copilot), polished the four existing wrappers, added **SKILL.md⟺prompt.md parity + skills-index-drift** guards, skill templates, and an `## Available skills` index in `AGENTS.md`.

23/23 test suites green; `standards-check` 0/0; version coherence OK at 0.9.0. The package is at `0.9.0`, **not yet git-tagged or published** — a deliberate maintainer action (see Open threads).

## Recently touched

Slice 4 (PRs #7/#8/#9, merges through `79fa0ee`). Headlines:

- `scripts/standards-check/checks/` package — `__init__` (`Finding`/`Context`/`resolve_severity`), `structural` (v1 logic moved verbatim), `links`, `content`, `skills`, `discovery`, `_text` (shared code-span/comment stripper used by `links` + `content`). `check.py` is now a thin orchestrator that builds one `Context` and runs each module's `run(root, ctx) -> list[Finding]`.
- `tools/check_version_coherence.py` (kit-only, NOT shipped) — `find_incoherences(root, tag=None)`; verifies `src/standards/__about__.py` ↔ CHANGELOG top ↔ `AGENTS.md` Kit-version + sentinel, and (with `--tag`) the release tag. Run by `.github/workflows/kit-guards.yml` (PR-time) and a `release.yml` step (tag-time). `tests/test_version.py` was refactored to assert coherence instead of a hardcoded literal.
- `scripts/standards-check/checks/structural.py` — `HANDOFF_STALE_DAYS = 5` (current-state stays 14). `scripts/update-handoff/update_handoff.py` `--check` — louder imperative nudge + fires on a stale handoff even with no pending work (a second `HANDOFF_STALE_DAYS = 5` constant, kept in sync by comment).
- `.claude/skills/standards-check/` + `.github/prompts/standards-check.prompt.md` — the new skill. `docs/templates/skill-template.md` + `skill-prompt-template.md`. `AGENTS.md` gained an `## Available skills` index (adopter-owned region) + a `/standards-check` end-of-session checkbox (managed block).
- `src/standards/__about__.py` at `0.9.0`; CHANGELOG entries for 0.7.0/0.8.0/0.9.0.

Design/plan docs for each are under `docs/superpowers/specs/` and `docs/superpowers/plans/` (the three `2026-05-3x-slice-4-plan-*` files).

## Open threads

- **Releasing is a maintainer action, not a code task.** To publish v0.9.0: (1) one-time PyPI Trusted-Publisher setup per `docs/RELEASING.md` (pending-publisher flow for the first release), (2) create the `pypi` GitHub Environment, (3) `git tag v0.9.0 && git push origin v0.9.0`. The tag fires `release.yml`, which now runs the coherence+tag gate before building. Only the maintainer can do this. (Earlier versions 0.5.0–0.8.0 are intentionally not back-published; PyPI only needs the current version.)
- **Slice 4 backlog (genuinely future, not started):** external-link liveness (HTTP), richer doc-freshness *reporting*, and a `new-skill` scaffolder script (`scripts/new-doc/new-skill.py`, deferred from Plan 3 — would generate the SKILL.md+prompt.md pair from the templates). The `AGENTS.md` "queued slices" note now reflects Slice 4 as delivered.
- **ADO home (deferred):** PyPI Trusted Publishing can't be used from Azure DevOps; that home would publish with a stored PyPI API token. The portable `tools/run_tests.py` + `standards-check` are shared by design (ADR-0011).
- **`pypa/gh-action-pypi-publish` is still floating `@release/v1`** (SHA-pin was de-selected during Slice 4 scoping). Revisit if supply-chain pinning becomes a requirement.

## Don't do

- Don't `git tag`/push a release tag yourself — publishing triggers a real PyPI publish; it's the maintainer's call. Surface `docs/RELEASING.md`.
- Don't put kit-only checks in the shipped `repo-standards.yml` or the `checks/` package — `repo-standards.yml` ships to adopters (who lack `__about__.py`). Kit-only guards go in `kit-guards.yml` (not in the payload manifest) and `release.yml`.
- Don't put the `AGENTS.md` `## Available skills` index *inside* the `kit-managed: agents-core` block — it lives in the adopter-owned region so an adopter's own skills survive `standards update`. The `/standards-check` checkbox and Skills authoring line DO belong inside the managed block (kit contract).
- Don't interpolate `${{ github.* }}` directly into a workflow `run:` — pass via an `env:` var (Actions shell-injection; this bit the first cut of the release gate).
- Don't make freshness a CI *error* — it stays a warning; calendar time must never fail an unrelated PR.
- Don't drop `from __future__ import annotations` from any module/test using PEP 604/585 annotations — the CI matrix runs Python 3.9.
- Don't reintroduce a single `pytest` CI step — `tools/run_tests.py` (subprocess-per-suite) is canonical because of the duplicate `test_cli.py` basenames.
- Don't edit ADRs 0001–0011 (all `Accepted`) or make `standards update` interactive/destructive (ADR-0009/0010). Don't introduce a runtime dependency (pure-stdlib by design).
- Don't push directly to `main`; PR-and-merge per the established flow.
