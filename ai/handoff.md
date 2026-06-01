---
written: 2026-06-01T22:30:00-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**v0.11.0 is shipped and published to PyPI** (Slices 5 + 6: `standards check` subcommand,
multi-profile CI-green `init`, and `standards adopt` for existing repos). New repos *and*
existing repos can both adopt the kit.

**In flight: a v0.12.0 docs release** on `docs/readme-install-and-cli` (**PR #13**, not yet
merged). The README had no install instructions and was frozen at v0.1.0; it now has
Installation (`pipx`/`uvx`/`pip`) + a CLI Quickstart (`init`/`adopt`/`check`/`update`), with
the stale header/roadmap refreshed. Because the README is the PyPI long-description, cutting
0.12.0 refreshes the package page (0.11.0's page keeps the old README until then). The version
bump (0.11.0 → 0.12.0 across `__about__`/CHANGELOG/AGENTS) is folded into PR #13.

`standards check` 0/0; 25/25 suites; version coherence OK at 0.12.0.

## Recently touched

- `README.md` — Installation + Quickstart + adoption-via-CLI + refreshed roadmap.
- `src/standards/__about__.py`, `CHANGELOG.md` (+[0.12.0] section + reflink), `AGENTS.md`
  (sentinel + Kit-version) → 0.12.0.
- (v0.11.0, earlier) `standards adopt` in `src/standards/init.py` (`run_adopt`,
  `_seed_scaffold_once`), `managed.extract_block`/`has_begin_marker`, `cli.py` adopt
  subcommand, `tests/test_adopt.py`, ADR-0013, RFC-0002 (Concluded).

## Open threads

- **Finish the 0.12.0 release:** merge PR #13 → `main`, then `git tag v0.12.0 && git push
  origin v0.12.0` on the merge commit. The tag fires `release.yml` (coherence+tag gate →
  tests → build → Trusted-Publishing publish). Verify PyPI serves 0.12.0 + the new README.
- **Two unmerged branches exist on origin:** `feat/slice-5-hardening` (already merged via
  PR #12 — safe to delete) and `docs/readme-install-and-cli` (PR #13, in flight).
- Releasing pattern (proven for v0.9.0/v0.11.0): release on the PR merge commit; RELEASING.md
  step 2 (CHANGELOG reflink → real tag) is folded into the PR before tagging.

## Don't do

- Don't forget the CHANGELOG reflink for a new version (RELEASING.md step 2) — it's folded
  into the release PR, not a separate one.
- Don't tag off a feature branch — tag the `main` merge commit (matches v0.9.0/v0.11.0).
- Don't route existing-repo adoption through `init --force` — `adopt` is the non-destructive
  path (ADR-0013). Don't refactor `checks/` into the package (ADR-0012 chose subprocess).
- Don't run a single `pytest` — `python tools/run_tests.py` is canonical (duplicate
  `test_cli.py` basenames). Keep `from __future__ import annotations` (3.9 matrix).
- Don't push to `main` directly; don't add runtime deps; don't edit Accepted ADRs (0001–0013).
