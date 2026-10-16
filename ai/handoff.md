---
written: 2026-10-15T23:00:00-05:00
written_by: claude (for Josh Swanson)
for: next-session
---

# Handoff

## TL;DR

RFC-0007 is concluded and ADR-0023 accepted: Stop hooks block once and then
trust the agent, driven by per-repo drift rules, with a CI check as the
backstop. M8 (automation engine) is active, and its first slice, the drift
detection core in `scripts/drift/drift.py`, is built test-first, reviewed by
Codex, and committed. RFC-0008 (distribution) and RFC-0009 (setup wizard) are
approved designs still Open; RFC-0010 (retrospectives) is drafted. Everything is
on `docs/rfc-0007-automation-engine`, pushed to origin, with no PR.

## Recently touched

- Concluded RFC-0007 and wrote ADR-0023; ADR-0008 is now "Superseded by 0023".
  Added "M8 — Automation engine" (active) to `docs/05-implementation-plan.md`.
- `scripts/drift/drift.py` with `test_drift.py` (25 tests): default rules in code
  plus a `drift` key in `.standards-kit.json`, conventional-commit types for the
  changelog, path globs with real `**`, `Docs-Unaffected:` waivers, and
  uncommitted files. Report only for now: `python scripts/drift/drift.py`.
- A Codex review found six real issues, all fixed with regression tests: git
  errors and shallow clones now raise `DriftError` instead of reporting nothing
  behind, and changes made in merge commits (`--cc`), both sides of renames,
  `src/api/**` matching, and `BREAKING-CHANGE:` footers are handled.
- Earlier on this branch: the RFC-0008, RFC-0009, and RFC-0010 drafts, the
  RFC-0009 prototype, and three test-first fixes (new-doc `--help`, the session
  brief listing answered questions, `standards update` dropping adopter marker
  keys).

## Decisions made with the user

- Keep all five profiles, all hooks, and all skills. The user wants to lean
  more on hooks, not less, and relies on the agent to trigger ADRs and plans.
- RFC-0007 concluded on 2026-10-15 on the spike's evidence: per-host output
  adapters, top-level `decision`/`reason` by default. The Copilot adapter shapes
  are verified during the build.
- RFC-0008 design approved: the pip CLI scaffolds repo content and runs CI
  checks; one plugin in Claude's `.claude-plugin/` format carries skills, hooks,
  and setup. The marketplace lives in this repo.
- RFC-0009: the profile matrix lives as data in the CLI, with a sync test
  against `docs/STANDARDS.md`.
- Drift rules live under a `drift` key in `.standards-kit.json`; "docs
  unaffected" is a `Docs-Unaffected:` commit trailer, with the PR description as
  the squash-merge fallback.
- Retrospectives (RFC-0010): a `standard-retro` skill the user runs; proposals
  only, each citing evidence; output only to artifacts in git. Lasting lessons go
  in `ai/gotchas.md`, which `AGENTS.md` only points to.
- RFC order: 0007 automation, 0008 distribution, 0009 setup wizard, 0010 retro.
- Approved deletions are untracked dead weight only (`_delete-me/`, `dist/`,
  tool caches). The `rm` was declined, so nothing has been deleted.

## Open threads

- M8 next slices:
  1. Block-once Stop hook: an `enforce`/`advise` mode in the marker, top-level
     JSON for Claude Code and Codex, failing open on `DriftError`, wired into
     `.claude/settings.json` and `.codex/hooks.json`. Ship `scripts/drift` in the
     payload (`PAYLOAD_DIRS` in `src/standards/manifest.py`) in the same change.
  2. CI drift check: a drift mode in `standards check` over the PR range,
     honoring the `Docs-Unaffected:` trailer and the PR-description fallback,
     with `fetch-depth: 0` in `repo-standards.yml`.
  3. Copilot adapters, shaped by manual tests A–C in RFC-0007's
     `artifacts/spike-results.md`; test D checks Codex's interactive trust flow.
- RFC-0008 checks: does the Copilot cloud agent load skills from plugins declared
  in `.github/copilot/settings.json`, and does its `agentStop` hook fire? Do
  Codex marketplace-installed plugin hooks run? Do VS Code and Copilot CLI list
  `.claude/skills` as slash commands (if so, retire `.github/prompts`)?
- RFC-0009: the owner tries the prototype in its `artifacts/prototype/` and
  records a verdict in `NOTES.md`.
- RFC-0010 needs a trial retro on a real session, a threshold for promoting a
  lesson into `ai/gotchas.md`, and a call on reading Claude Code transcripts.
- The parked ADR-0022 branch rewrites `scripts/changelog/check_changelog.py`.
  Once both land, the drift engine's changelog rule should replace or wrap that
  script. Landing ADR-0022 early avoids conflicts in `CHANGELOG.md` and `ai/`.

## Research notes

Hook findings and the spike results live in RFC-0007 and its `artifacts/`;
plugin and skill findings live in RFC-0008. Local precedent: Anthropic's
`ralph-loop` plugin blocks Stop with `{"decision": "block", "reason": ...}`, and
the `remember` plugin ships Claude, Codex, and Gemini manifests plus a
`pyproject.toml` from one repo.

## Validation

- `python tools/run_tests.py`: 31/31 suites passed, including the drift suite.
  The intermediate `FAIL` lines come from `tests/test_run_tests.py` exercising a
  deliberately failing fixture; trust the final summary.
- `python scripts/standards-check/check.py`: 0 errors, 0 warnings.
- `ruff check .` and `mypy src/standards`: clean.

## Don't do

- Don't open a PR for `docs/rfc-0007-automation-engine` yet; the owner asked
  for the branch to be pushed only.
- Don't build drift logic into `scripts/changelog/check_changelog.py` on this
  branch; the parked ADR-0022 branch rewrites it. Keep new logic in
  `scripts/drift/`.
- Don't let a hook treat `DriftError` as "nothing behind". The Stop hook fails
  open (exit 0) but says why on stderr; the CI check must fail loudly.
- Don't separate profiles with commas in the checklist header. Older checkers
  keep only the first word, so `application, infra` reads as the invalid
  `application,`. Use `application + infra`.
- Don't emit top-level `decision`/`reason` and `hookSpecificOutput` in one
  object: Codex rejects the whole output and the block is lost.
- Don't let `new-adr.py` number ADRs on this branch: it would pick 0022, which
  the parked branch already uses. ADR-0024 is next, for RFC-0008.
- Don't link to ADR-0022 from this branch; the file only exists on the parked branch.
- Don't delete `docs/superpowers/`, `docs/discovery/README.md`, or the
  `discovery-note`/`-meeting`/`-artifact` templates. Accepted ADRs cite the
  first, the payload ships the second, and tests assert the templates.
- Don't delete files without asking; `rm` was declined twice.
- Don't edit accepted historical ADRs just to remove mentions of deleted
  legacy surfaces.
