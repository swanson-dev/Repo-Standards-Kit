---
written: 2026-06-01T20:00:00-05:00
written_by: swanson-dev (via claude-code-assistant)
for: next-session
---

# Handoff

## TL;DR

**Slice 5 (hardening) is implemented on `feat/slice-5-hardening`, not yet merged**, at v0.10.0.
It came out of a gap review comparing the kit against `voyager-projen`. Three threads:

1. **`standards check [target]` subcommand** — the check is now runnable from the installed
   CLI (previously only `python scripts/standards-check/check.py`). It locates the bundled
   `check.py` via `payload_root()` and subprocesses it; `check.py` gained an optional `target`
   arg + a reusable `run_checks()`. Decision recorded in **ADR-0012** (subprocess vs. refactor).
2. **Multi-profile dogfooding gate** (`tests/test_profiles_scaffold.py`) — proved
   `standards init` produced a repo failing `standards check` with ~26 errors. Fixed: `init`
   now seeds `docs/00-overview.md`, `docs/10-glossary.md`, the three folder READMEs, ticks the
   checklist core boxes + fills metadata, and stamps/strips the `ai/` starters. All four
   profiles now scaffold **0 errors, 0 warnings** (the test asserts both).
3. **RFC-0002 (Open)** — investigation into adopting onto existing non-blank repos (the
   greenfield-only `init` guard is the blocker; the `update.py` reconcile engine already solves
   most of it). Design only.

Full suite green via `python tools/run_tests.py`; `standards-check` 0/0; version coherence OK
at 0.10.0. Three commits on the branch; **no PR opened yet**.

## Recently touched

- `src/standards/cli.py` — `check` subparser + handler (subprocess the bundled `check.py`).
- `scripts/standards-check/check.py` — optional `target` arg; extracted `run_checks(root, ctx)`
  (main behavior unchanged when run with no arg).
- `src/standards/init.py` — `_stamp_ai_starter` + `_fill_checklist` helpers; scaffold-once loop
  now seeds a CI-green repo.
- `src/standards/manifest.py` — five new `SCAFFOLD_ONCE` entries (overview, glossary, three
  folder READMEs).
- `pyproject.toml` — force-include the discovery/rfcs folder READMEs into the wheel payload.
- `docs/templates/decisions-readme-template.md` (new, link-safe) + `docs/templates/README.md`
  (scaffold-source templates presented as auto-seeded, clearing broken-link warnings).
- `tests/test_cli.py` (+2 check tests), `tests/test_profiles_scaffold.py` (new).
- `docs/decisions/0012-…md` (ADR), `docs/rfcs/0002-…/rfc.md` (RFC), CHANGELOG/AGENTS/__about__
  bumped to 0.10.0.

## Open threads

- **Open the PR for `feat/slice-5-hardening` → `main`.** Three commits (check subcommand+ADR,
  init CI-green fix, RFC-0002). Not pushed yet.
- **RFC-0002 is Open** — it leans toward a `standards adopt` "first-run update" reusing
  `run_update`. Concluding it spawns an ADR + a Slice 6 plan. Don't implement retrofit before
  the RFC concludes.
- **Releasing remains a maintainer action** (unchanged from 0.9.0): PyPI Trusted-Publisher
  setup per `docs/RELEASING.md`, then tag + push. v0.10.0 supersedes 0.9.0 as the publish target.
- **Untracked file:** `repo-standards-kit-vs-voyager-projen.md` at the repo root is the
  comparison that prompted this work — left untracked deliberately; decide whether to keep/move it.

## Don't do

- Don't change `is_excluded_from_tracked` / the scaffold-source exclusion to "fix" the
  templates-README links — that's tested design (test_manifest). The README was edited instead
  to present scaffold-source templates as auto-seeded (code, not links).
- Don't refactor the `checks/` package into `src/standards/` to make `standards check` import
  in-process — ADR-0012 deliberately chose subprocess to preserve the vendored zero-install
  path; the wheel ships checks as payload data, not importable code.
- Don't make the dogfood test seed the *whole* repo — it seeds only README + CHANGELOG (the
  adopter-supplied minimum); `init` must produce everything else. It uses `date.today()` so the
  freshness assertion stays robust over time; don't hardcode a date back in.
- Don't git-tag/push a release yourself (maintainer's call); don't push to `main`; don't add a
  runtime dependency; don't edit Accepted ADRs (now 0001–0012).
- Don't run a single `pytest` over everything — `python tools/run_tests.py` (subprocess-per-suite)
  is canonical because of duplicate `test_cli.py` basenames.
