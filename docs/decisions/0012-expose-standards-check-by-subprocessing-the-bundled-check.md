---
status: Accepted
date: 2026-06-01
deciders: swanson-dev
consulted: —
informed: kit adopters
---

# 0012. Expose standards check by subprocessing the bundled check

## Context and Problem Statement

The kit installs as the `standards` CLI (`pip`/`pipx`/`uvx`), exposing `init` and `update`.
But the kit's flagship verification — the standards check — was only runnable as
`python scripts/standards-check/check.py`, i.e. only when the script tree is vendored into a
repo. A developer who merely `pipx install`ed the tool had no way to run `standards check`.
This is a packaging/runtime boundary smell: the most valuable runtime capability lived on the
wrong side of the `pip install` line.

The complication is that the check modules ship as **payload data** — the `force-include` map
in `pyproject.toml` bundles `scripts/` under `standards/_payload/scripts/...`, and only the
`src/standards` package is importable from the wheel (ADR-0009). So `standards check` cannot
simply `import` the check logic; the `checks/` package is not on the installed import path.

## Decision Drivers

- Reuse the existing, tested check orchestration — no duplicated logic, one severity contract.
- Preserve the zero-install vendored-script story: `python scripts/standards-check/check.py`
  must keep working byte-for-byte in adopter CI (ADR-0007/0008).
- Keep runtime stdlib-only (no new dependency).
- Minimal v1 scope; avoid a large refactor while adoption is still young.

## Considered Options

- **Option A** — Locate the bundled `check.py` via `payload_root()` and run it in a
  subprocess against the target, relaying its exit code.
- **Option B** — Refactor the `checks/` package into the importable `src/standards/checks/`
  and call it in-process from the CLI.
- **Option C** — Duplicate a thin check entry point inside `src/standards/`.

## Decision Outcome

Chosen option: **Option A**, because it reuses the existing `check.py` exit-code and
severity behavior with zero duplication and zero changes to the vendored-script contract,
while keeping the v1 change small. The CLI resolves
`payload_root() / "scripts" / "standards-check" / "check.py"` (the same locator `init`/
`update` already use) and runs `[sys.executable, check_py, target]`. A minimal,
backward-compatible change to `check.py` lets it accept an optional `target` (detect the repo
root by walking up from it) while defaulting to the historical behavior when no target is
given; the check loop is extracted into a `run_checks(root, ctx)` function so the
multi-profile dogfood test can also import it.

### Consequences

- **Good:** `standards check [target]` works from an installed wheel; one source of truth for
  the checks; the vendored `python scripts/standards-check/check.py` path is unchanged; the
  target's `.standards-kit.json` severity overrides are still honored (the bundled check reads
  them from the target root).
- **Bad:** a subprocess hop (extra interpreter start) and a slight asymmetry — the CLI
  subprocesses the check while the dogfood test imports `run_checks` directly.
- **Neutral:** version skew is possible (an adopter on kit 0.9 vendored-script, but a 0.10
  `standards` on PATH runs 0.10's bundled checks); acceptable, and arguably desirable.

## Pros and Cons of the Options

### Option A (subprocess the bundled check)
- Good: zero logic duplication; vendored story untouched; smallest change.
- Bad: subprocess overhead; CLI-vs-test execution asymmetry.
- Neutral: relies on `payload_root()` resolving in both wheel and source modes (it does).

### Option B (refactor checks into the importable package)
- Good: cleanest long-term; in-process, no subprocess; symmetric with tests.
- Bad: larger refactor; changes how the vendored zero-install script is assembled and
  shipped; more risk while adoption is young.
- Neutral: a likely future direction once the check surface stabilizes.

## More Information

- Related ADRs: 0007 (thin wrappers over stdlib scripts), 0008 (hooks invoke check mode),
  0009 (PyPI distribution + payload bundling).
- Implementation: `src/standards/cli.py` (`check` subparser + handler),
  `scripts/standards-check/check.py` (`target` arg + `run_checks` extraction).
