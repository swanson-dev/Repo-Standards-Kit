---
written: 2026-06-01T22:30:00-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**v0.14.0 — discovery capture** is built and verified on `feat/discovery-capture` (PR open,
not yet merged). It closes the gap where dropping a PDF/JSON into `docs/discovery/` and running
`/promote-discovery` reported zero items: there was no *capture* stage and the intake subfolders
were never scaffolded.

New flow (ADR-0014): drop raw source into the **gitignored** intake folders
(`docs/discovery/{meetings,requirements,use-cases,notes}/`) → `/capture-discovery` synthesizes it
into **tracked** markdown notes under `docs/discovery/captured/` → `/promote-discovery` promotes
those. "Markdown only" became "markdown only **in version control**": binaries stay local, only
synthesized markdown is committed.

`standards check` 0/0; 26/26 suites; version coherence OK at 0.14.0; wheel build confirms the new
payload (`.gitignore`, `captured/README.md`, 4 `.gitkeep`, `capture-discovery` script) is bundled.

## Recently touched

- **New:** `scripts/capture-discovery/` (`capture_discovery.py` + tests), `.claude/skills/capture-discovery/SKILL.md`, `.github/prompts/capture-discovery.prompt.md`, ADR-0014, `docs/discovery/.gitignore`, `docs/discovery/captured/README.md`, 4 intake `.gitkeep`.
- **Scaffolding:** `src/standards/manifest.py` (`SCAFFOLD_ONCE`) + `pyproject.toml` force-include + `tests/test_init.py`/`test_adopt.py`.
- **Scoped:** `scripts/promote-discovery/promote_discovery.py` + test + README, `scripts/standards-check/checks/discovery.py` + test (both exclude intake folders).
- **Hook:** `.claude/settings.json` SessionStart now also runs `capture-discovery list --check`.
- **Docs:** `docs/discovery/README.md`, `02-architecture.md`, `STANDARDS.md`, `AGENTS.md` (skills index + end-of-session contract + version), `10-glossary.md`, `00-overview.md`, `templates/README.md` + both discovery templates (now point at `captured/`), root `README.md`, `CHANGELOG.md`.

## Open threads

- **Finish the 0.14.0 release:** merge the `feat/discovery-capture` PR → `main`, then
  `git tag v0.14.0 && git push origin v0.14.0` on the merge commit. The tag fires `release.yml`.
  Verify PyPI serves 0.14.0 and the wheel bundles the discovery payload.
- The CHANGELOG `[0.14.0]` reflink already points at the real release-tag URL (folded into the PR,
  per the proven v0.9.0/v0.11.0/v0.13.0 pattern).
- Stale merged branches on origin safe to delete: `chore/add-license` (PR #14, v0.13.0).

## Don't do

- Don't commit raw discovery intake — the `docs/discovery/.gitignore` keeps the folders
  (`.gitkeep`) but ignores their contents on purpose. Hand-authored notes go in `captured/`, not the intake folders.
- Don't tag off a feature branch — tag the `main` merge commit (matches v0.9.0/v0.11.0/v0.13.0).
- Don't run a single `pytest` — `python tools/run_tests.py` is canonical (duplicate
  `test_cli.py` basenames). Keep `from __future__ import annotations` (3.9 matrix).
- Don't push to `main` directly; don't add runtime deps; don't edit Accepted ADRs (0001–0014).
- Don't route existing-repo adoption through `init --force` — `adopt` is non-destructive (ADR-0013).
