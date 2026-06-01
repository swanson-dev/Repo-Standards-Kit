---
written: 2026-06-01T23:30:00-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**Published to PyPI through v0.12.0.** Slices 5 + 6 shipped (`standards check`, multi-profile
CI-green `init`, `standards adopt` for existing repos); v0.12.0 added README Installation +
CLI Quickstart (the README is the PyPI long-description).

**In flight: v0.13.0 — add LICENSE** on `chore/add-license` (not yet merged). The package
declared `license = "MIT"` but shipped no license text; added a top-level MIT `LICENSE`
(© 2026 Swanson Creative Studios) and `license-files = ["LICENSE"]` in pyproject so the wheel
bundles it (`.dist-info/licenses/LICENSE`, METADATA `License-File`) and GitHub recognizes it.
Prep for **making the repo public**. Version bump 0.12.0 → 0.13.0 folded into the same branch.

`standards check` 0/0; 25/25 suites; version coherence OK at 0.13.0; wheel build confirmed the
LICENSE is bundled.

## Recently touched

- `README.md` — Installation + Quickstart + adoption-via-CLI + refreshed roadmap.
- `src/standards/__about__.py`, `CHANGELOG.md` (+[0.12.0] section + reflink), `AGENTS.md`
  (sentinel + Kit-version) → 0.12.0.
- (v0.11.0, earlier) `standards adopt` in `src/standards/init.py` (`run_adopt`,
  `_seed_scaffold_once`), `managed.extract_block`/`has_begin_marker`, `cli.py` adopt
  subcommand, `tests/test_adopt.py`, ADR-0013, RFC-0002 (Concluded).

## Open threads

- **Finish the 0.13.0 release:** merge the `chore/add-license` PR → `main`, then
  `git tag v0.13.0 && git push origin v0.13.0` on the merge commit. The tag fires
  `release.yml`. Verify PyPI serves 0.13.0 and the wheel bundles the LICENSE.
- **Making the repo public** (the reason for the LICENSE): before flipping visibility, sanity-
  check git history for secrets — there are none expected (stdlib-only, no tokens; PyPI uses
  tokenless Trusted Publishing), but confirm. The `.standards-kit.json`/CI carry no secrets.
- **Stale merged branches on origin** safe to delete: `feat/slice-5-hardening` (PR #12),
  `docs/readme-install-and-cli` (PR #13).
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
