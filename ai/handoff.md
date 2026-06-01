---
written: 2026-06-01T21:30:00-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**Branch `feat/slice-5-hardening` now carries Slices 5 AND 6, at v0.11.0, not yet merged.**
(The branch keeps its Slice-5 name; it grew to include Slice 6.)

- **Slice 5 (hardening):** `standards check [target]` subcommand (ADR-0012, subprocesses the
  bundled check); multi-profile dogfooding gate (`tests/test_profiles_scaffold.py`) — `init`
  now scaffolds a repo that passes the check with **0 errors, 0 warnings** for all four
  profiles.
- **Slice 6 (`standards adopt`):** non-destructive adoption onto an **existing** non-blank
  repo (RFC-0002 **Concluded**, ADR-0013). Keeps adopter files; a differing kit-tracked file
  is kept and the kit copy written as `<rel>.kit-<version>`; a partial file with no managed
  block gets the kit block **appended** (their content preserved); one with a block is
  spliced; scaffold-once seeds only when absent. Marker is written so the repo is
  `update`-ready. `init`'s collision error now points at `adopt`.

**New repos and existing repos both work now.** 25/25 suites green via
`python tools/run_tests.py`; `standards-check` 0/0; version coherence OK at 0.11.0.
No PR opened, nothing pushed.

## Recently touched

- `src/standards/init.py` — `run_adopt` (per-class non-destructive reconcile) + shared
  `_seed_scaffold_once` (used by `init` and `adopt`); collision error points at `adopt`.
- `src/standards/managed.py` — `extract_block()` (full block incl. sentinels, for appending)
  + `has_begin_marker()`.
- `src/standards/cli.py` — `adopt` subparser + handler (prints added/spliced/unchanged/
  conflicts/scaffolded; lists sidecars on stderr).
- `tests/test_adopt.py` (new), `tests/test_cli.py` (+adopt test).
- `docs/decisions/0013-…md` (ADR, Accepted) + index; `docs/rfcs/0002-…/rfc.md` flipped to
  **Concluded** with findings + ADR link.
- `__about__`/CHANGELOG/AGENTS bumped to 0.11.0 (sentinel + Kit-version + Slice 6 roadmap).
- (Slice 5, earlier this session) `standards check` subcommand, `check.py` `target`+`run_checks`,
  CI-green `init` scaffolding, `docs/templates/decisions-readme-template.md`, ADR-0012.

## Open threads

- **Open the PR for `feat/slice-5-hardening` → `main`.** It now contains 6 commits spanning
  Slices 5 + 6. Not pushed yet. Consider noting in the PR title that it covers both.
- **`adopt` does not guarantee a check-clean repo for arbitrary existing content** — by
  design. It guarantees non-destructiveness + a valid marker. A repo with conflicting files
  ends up with `.kit-<version>` sidecars the adopter merges; their kept content may still have
  its own check findings. (A blank repo adopted via `adopt` *is* check-clean — asserted.)
- **Releasing remains a maintainer action.** v0.11.0 is the publish target now (per
  `docs/RELEASING.md`). Earlier versions intentionally not back-published.
- **Untracked:** `repo-standards-kit-vs-voyager-projen.md` at the root — left untracked per
  the user's call.

## Don't do

- Don't route existing-repo adoption through `init --force` — that overwrites. `adopt` is the
  non-destructive path (ADR-0013).
- Don't make `adopt` clobber: differing kit-tracked → keep + sidecar; partial-with-block →
  splice the block only; partial-no-block → append the block (chosen over sidecar so adoption
  installs the contract). Don't change the blockless behavior without revisiting ADR-0013.
- Don't refactor the `checks/` package into `src/standards/` to make `standards check` import
  in-process (ADR-0012 chose subprocess to preserve the vendored zero-install path).
- Don't change `is_excluded_from_tracked` / scaffold-source exclusion (tested design); the
  templates-README was edited instead to present scaffold-source templates as auto-seeded.
- Don't run a single `pytest` over everything — `python tools/run_tests.py` is canonical
  (duplicate `test_cli.py` basenames). Keep `from __future__ import annotations` (3.9 matrix).
- Don't git-tag/push a release yourself; don't push to `main`; no runtime deps; don't edit
  Accepted ADRs (now 0001–0013).
