---
written: 2026-10-16T10:15:00-05:00
written_by: claude (for Josh Swanson)
for: next-session
---

# Handoff

## TL;DR

RFC-0007 is concluded and ADR-0023 accepted: Stop hooks block once and then
trust the agent, driven by per-repo drift rules, with a CI check as the
backstop. M8 (automation engine) is active, with three slices built test-first
and reviewed by Codex: the drift detection core in `scripts/drift/drift.py`, the
block-once Stop hook (`--hook`) wired into this repo's Claude Code Stop hooks, and
the CI drift check (`standards check --drift-base`) that `repo-standards.yml`
runs on pull requests. Manual tests A–C then showed every Copilot host (VS Code,
the CLI, the cloud agent) takes the same top-level output and input, so no output
adapter is needed. The cloud agent's engine reprompts a session for its PR
description, so on CI runners the hook now blocks once per session.
RFC-0008 (distribution) and RFC-0009 (setup wizard) are
approved designs still Open; RFC-0010 (retrospectives) is drafted. Everything is
on `docs/rfc-0007-automation-engine`, pushed to origin, with no PR.

## Recently touched

- Concluded RFC-0007 and wrote ADR-0023; ADR-0008 is now "Superseded by 0023".
  Added "M8 — Automation engine" (active) to `docs/05-implementation-plan.md`.
- `scripts/drift/drift.py` with `test_drift.py` (52 tests): default rules in code
  plus a `drift` key in `.standards-kit.json`, conventional-commit types for the
  changelog, path globs with real `**`, `Docs-Unaffected:` waivers, and
  uncommitted files. Report only for now: `python scripts/drift/drift.py`.
- Stop hook: `drift.py --hook` blocks once with top-level `decision`/`reason` in
  `enforce` mode, lets the next stop through, only reminds in `advise` mode, and
  fails open on unreadable input, bad drift config, or git errors (a Codex review
  found the first two, plus a Windows encoding bug in reading hook input). No marker means the kit's own repo, which enforces;
  `init`/`adopt` write `hook_mode: "enforce"`, and markers without the key
  advise. It replaced `check_changelog.py --check` in `.claude/settings.json`,
  `scripts/drift` ships in the payload, and `docs/STANDARDS.md` documents it.
- CI drift check: `checks/doc_drift.py` (check id `drift`), opt-in with
  `--drift-base REF` on `check.py` and `standards check`. A commit is behind
  when no later doc update descends from it: HEAD's history minus everything
  reachable from the base or from any (non-merge) commit that updated the doc.
  That holds up for GitHub's synthetic merge checkout and for PRs that merge the
  base in. PR-description waivers arrive through the `STANDARDS_PR_BODY` env var.
  Drift is an error in the kit and warn by default for adopters; unreadable
  history is always an error. `repo-standards.yml` checks out full history, runs
  it on pull requests, and re-runs it when the PR description is edited.
- Copilot results (RFC-0007 manual tests A–C, recorded in `artifacts/spike-results.md`):
  VS Code 1.141.2, Copilot CLI 1.0.98, and the cloud agent all accept top-level
  `decision`/`reason`, and they all send snake_case input with `stop_hook_active`.
  The cloud agent reprompts the same session for the PR description, so `drift.py
  --hook` blocked again on each of those turns, and that failed the job. The fix is
  `ci_block_used`: when `GITHUB_ACTIONS=true`, a session blocks once, recorded as a
  file in `RUNNER_TEMP` (outside the repo). If the record can't be written, the
  hook doesn't block. Test C2 confirmed the hook sees those env vars and that the
  job then succeeds. Codex found one issue in it, a `gettempdir()` failure escaping
  fail-open, and it's fixed with a test.
- Throwaway evidence: the private repo `swanson-dev/rfc0007-hook-spike` (PRs 2 and
  3 hold the pushed hook logs) and a local copy in the session scratchpad. The
  owner deletes the repo when done.
- A Codex review of the CI slice found three real issues, all fixed with tests:
  false failures once the base branch moved on (the old single start point),
  "can't check" passing as an adopter warning, and description edits not
  re-running the check.
- A Codex review of the core found six real issues, all fixed with regression tests: git
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

- M8, what's left:
  1. Ship Copilot hook config. The kit has no `.github/hooks/` file yet, so the
     Copilot CLI and cloud agent don't run the drift hook. VS Code reads both
     `.github/hooks/` and `.claude/settings.json` by default, so shipping both
     makes it list the hook twice. Unknown: whether the CLI and cloud agent read
     `.claude/settings.json` (optional test B2). Test D (Codex's interactive
     trust flow) is still pending.
  2. Codex hook config isn't shipped: `.codex/` is gitignored here and not in
     the payload. RFC-0008's plugin is the planned way to ship it.
  3. The CI check hasn't run on GitHub yet; it runs on the first PR. Locally,
     `python scripts/standards-check/check.py --drift-base main` passes once the
     changelog is current.
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

- `python tools/run_tests.py`: 32/32 suites passed, including both drift suites
  (52 tests in `test_drift.py`).
  The intermediate `FAIL` lines come from `tests/test_run_tests.py` exercising a
  deliberately failing fixture; trust the final summary.
- `python scripts/standards-check/check.py`: 0 errors, 0 warnings.
- `ruff check .` and `mypy src/standards`: clean.

## Don't do

- Don't be surprised when this repo's own Stop hook blocks once at the end of a
  turn: with no marker the kit enforces, so update the named doc (usually
  `CHANGELOG.md`) or say why it is unaffected.
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
- Don't let a Stop hook write into the working tree: the Copilot cloud agent
  commits whatever is there into its PR. The CI-runner block record lives in
  `RUNNER_TEMP`.
- Don't edit accepted historical ADRs just to remove mentions of deleted
  legacy surfaces.
