---
written: 2026-05-30T00:00:15-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

Slice 3 (distribution) is two-thirds shipped and on `main`. RFC-0001 chose the mechanism: distribute the kit as a zero-dependency PyPI package (`repo-standards-kit`) run via `pipx`/`uvx`, exposing a `standards` CLI. **Plan 1 (v0.5.0, PRs #1–#2)** delivered packaging + `standards init`. **Plan 2 (v0.6.0, PR #3)** delivered `standards update` + the partial/managed-region ownership class + a non-destructive first-init guard. 97 tests green; standards-check 0/0. **Plan 3 (release) is the remaining piece** and is queued, not started.

## Recently touched

Slice 3 Plans 1 & 2 (≈40 commits across PRs #1–#3). Headlines:

- `feat(dist)`: `pyproject.toml` (hatchling, zero-dep, `standards` entry point) + `src/standards/` (`payload`/`manifest`/`marker`/`init`/`cli`/`managed`/`update`).
- `standards init` (vendor kit + `.standards-kit.json` marker) and `standards update` (three-class reconciliation, sidecar conflicts, `--dry-run`).
- Partial/managed-region class: `AGENTS.md`/`CLAUDE.md`/`.github/copilot-instructions.md` restructured with `<!-- BEGIN/END kit-managed -->` blocks.
- ADR-0009 (PyPI CLI distribution), ADR-0010 (sentinel convention); RFC-0001; CHANGELOG v0.5.0 + v0.6.0.
- `fix(standards-check)`: `parse_frontmatter` strips inline YAML comments.
- Copilot PR-review fixes on both PRs (init clobber, markerless 0.5.0 migration, duplicate-END, doc reconciliations).

Design docs live in `docs/superpowers/specs/` and `docs/superpowers/plans/` (Plans 1, 2, and the Plan 2 design spec).

## Open threads

- **Plan 3 (release) is next** — not yet planned. Scope: PyPI Trusted-Publishing (OIDC) workflow on tag-push; wire the 13 test suites (97 tests) into CI (`.github/workflows/repo-standards.yml` runs only `standards-check` today); a post-build smoke that installs the wheel and runs `standards init` (verifies the bundled `standards/_payload`, which dev/test exercise only via the repo-root fallback in `payload.py`); tag `v0.6.0` and backfill `v0.5.0`. Brainstorm → plan → execute like Plans 1 & 2.
- **`pytest` basename collision** — `test_cli.py` exists in both `tests/` and `scripts/new-doc/` with no `__init__.py`/`conftest.py`, so `pytest tests/ scripts/` fails to *collect*. All suites pass run standalone (the project's model). Fix before Plan 3 wires a single `pytest` CI step (add `conftest.py` with `--import-mode=importlib`, or unique basenames).
- **`AGENTS.md` queued-slices** now lists only Slice 4 (deeper CI). Slice 3 is no longer "out of scope" — it's shipping.
- **Marker is JSON** (`.standards-kit.json`), not the `.standards-kit.toml` named in RFC-0001 (stdlib has no TOML writer). Recorded in ADR-0009.
- The kit is **not yet git-tagged** for v0.5.0/v0.6.0 and **not published** — that's Plan 3. Tags v0.1.0–v0.4.0 exist from earlier slices.

## Don't do

- Don't edit ADRs 0001–0010; all are `Accepted`. Reversal = new ADR + flip old to `Superseded by NNNN`.
- Don't make `standards update` interactive or destructive. The contract (ADR-0009/0010) is: apply + report, conflicts go to `<path>.kit-<version>` sidecars, downstream edits (and content outside a managed block) are never clobbered. `--dry-run` must write nothing.
- Don't change the partial-branch ordering in `update.py` back to "identical-check first" — the current order (untouched-since-adoption splice first) is deliberate so the dev-mode test exercises the real splice path. Documented; opus-verified safe.
- Don't add multi-block managed regions or a `standards set-profile` command without an ADR — both are explicitly deferred to post-v1.
- Don't introduce a runtime dependency. The package is pure-stdlib by design (ADR-0009); `pipx`/`uvx` is only the delivery vehicle.
- Don't push directly to `main`; PR-and-merge per the established flow.
