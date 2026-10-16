---
written: 2026-10-15T22:25:00-05:00
written_by: claude (for Josh Swanson)
for: next-session
---

# Handoff

## TL;DR

The kit's direction is "automatic, not advisory." RFC-0007 (automation engine)
and RFC-0008 (distribution: the pip CLI plus one plugin) are approved and
committed on `docs/rfc-0007-automation-engine`. The RFC-0007 spike verified the
block-once Stop hook on Claude Code and Codex; the Copilot hosts still need the
owner's manual tests before RFC-0007 can conclude. RFC-0009 (setup wizard and
combinable profiles) is drafted for review, and RFC-0010 (retrospectives) is
drafted to build after the other three. The branch is pushed to origin, with no
PR yet.

## Recently touched

- `0216cfd`, fast-forwarded into `docs/rfc-0007-automation-engine`: the RFC-0007
  spike (`artifacts/spike/stop_hook.py` with its test, per-host hook configs,
  and `artifacts/spike-results.md`), plus a findings summary in the RFC.
- Archived the spike session and deleted its merged branch
  `CODE/eloquent-lovelace-ab5a30`. The app kept its worktree folder under
  `.claude/worktrees/` (detached HEAD) so the session can be reopened.
- Ignored `.archify/` (local diagram output) in `.gitignore`.
- Drafted `docs/rfcs/0009-how-should-setup-ask-what-a-repo-contains-and-support-more-than-one-profile/rfc.md`.
- Fixed test-first: `new-adr.py` and `new-rfc.py` print usage for `-h`/`--help`
  and reject titles that start with `-` (6 new cases in
  `scripts/new-doc/test_cli.py`, plus a `CHANGELOG.md` Fixed entry).
- Fixed test-first: the session-context brief listed answered and obsolete
  questions from `ai/open-questions.md` as open; it now lists only open ones.
- Fixed test-first: `standards update` rewrote `.standards-kit.json` with only
  the kit's fields, silently dropping adopter keys such as the `check` severity
  map. `write_marker()` now takes `keep=` and `update` passes the old marker.
- Built the RFC-0009 prototype in `artifacts/prototype/`: a pure
  `setup_logic.py` plus a throwaway terminal UI. It writes nothing; `NOTES.md`
  has the run command, things to try, and a verdict placeholder.
- Drafted `docs/rfcs/0010-how-should-the-kit-turn-session-lessons-into-lasting-improvements/rfc.md`,
  modeled on Matt Pocock's `retro` skill.
- Refreshed `ai/current-state.md` and `ai/next-actions.md`.

## Spike results (RFC-0007)

- Top-level `{"decision": "block", "reason": ...}` with exit 0 blocks once and
  lets the second stop pass on Claude Code 2.1.286 and Codex CLI 0.159.3.
- Adding VS Code's `hookSpecificOutput` wrapper to the same object works on
  Claude Code, but Codex rejects the whole output (strict schema) and fails
  open silently. One combined output for every host is ruled out.
- Codex runs a project hook only when the repo and the hook are both trusted,
  and gives no warning otherwise.

## Decisions made with the user

- Keep all five profiles, all hooks, and all skills. The user wants to lean
  more on hooks, not less, and relies on the agent to trigger ADRs and plans.
- RFC-0007 and RFC-0008 designs approved on 2026-10-14.
- Distribution is hybrid: the pip CLI scaffolds repo content and runs checks in
  CI; one plugin in Claude's `.claude-plugin/` format carries skills, hooks, and
  setup (RFC-0008).
- RFC order: 0007 automation, 0008 distribution, 0009 setup wizard and
  composable profiles.
- The changelog drift rule judges commits by conventional-commit type and falls
  back to paths for uncommitted work.
- Decided 2026-10-15: drift rules live under a `drift` key in
  `.standards-kit.json`; "docs unaffected" is a `Docs-Unaffected:` commit
  trailer, with the PR description as the squash-merge fallback; the plugin
  marketplace lives in this repo; the profile matrix lives as data in the CLI,
  with a sync test against `docs/STANDARDS.md`.
- Retrospectives (RFC-0010): a `standard-retro` skill the user runs; proposals
  only, each citing evidence; output only to artifacts in git; built after
  RFC-0007 to RFC-0009 conclude. Lasting lessons go in `ai/gotchas.md`, which
  `AGENTS.md` only points to and the session-start summary lists by title.
- Approved deletions are untracked dead weight only (`_delete-me/`, `dist/`,
  tool caches). The `rm` was declined, so nothing has been deleted.

## Open threads

- RFC-0007: manual tests A–D in `artifacts/spike-results.md` (Copilot in VS
  Code, Copilot CLI, the Copilot cloud agent, Codex's interactive trust flow).
  Test A decides whether VS Code needs its own output variant.
- RFC-0008: does the Copilot cloud agent load skills from plugins declared in
  `.github/copilot/settings.json`, and does its `agentStop` hook fire? Do Codex
  marketplace-installed plugin hooks run? Do VS Code and Copilot CLI list
  `.claude/skills` as slash commands (if so, retire `.github/prompts`)?
- RFC-0009 (draft): today the profile matrix is applied by hand (the checklist
  says to copy rows from `docs/STANDARDS.md`), and `docs/STANDARDS.md` allows
  exactly one profile. Proposal: a state-aware menu for bare `standards`, one
  non-destructive setup (adopt semantics), "what does this repo contain?" with
  suggestions, profiles combined by strongest tier with back-compatible marker
  (`profiles` plus `profile`) and checklist (`application + infra`) formats, and
  setup creating the docs the profiles need. The prototype is ready for the
  owner to try. It departs from the RFC in two places, listed in `NOTES.md`:
  Enter accepts the suggested default (`0` means documentation only), and
  "Update" shows only when the repo is behind.
- RFC-0010 needs a trial retro on a real session, a threshold for promoting a
  lesson into `ai/gotchas.md`, and a call on reading Claude Code transcripts.

## Research notes

Full findings and sources live in RFC-0007 (hooks, plus the spike results) and
RFC-0008 (plugins and skills). Local precedent: Anthropic's `ralph-loop` plugin
blocks Stop with `{"decision": "block", "reason": ...}`, and the `remember`
plugin ships Claude, Codex, and Gemini manifests plus a `pyproject.toml` from
one repo.

## Validation

- `python tools/run_tests.py` on `docs/rfc-0007-automation-engine`: 30/30 suites
  passed. The intermediate `FAIL` lines come from `tests/test_run_tests.py`
  exercising a deliberately failing fixture; trust the final summary.
- `python scripts/standards-check/check.py`: 0 errors, 0 warnings.

## Don't do

- Don't open a PR for `docs/rfc-0007-automation-engine` yet; the owner asked
  for the branch to be pushed only.
- Don't separate profiles with commas in the checklist header. Older checkers
  keep only the first word, so `application, infra` reads as the invalid
  `application,`. Use `application + infra`.
- Don't emit top-level `decision`/`reason` and `hookSpecificOutput` in one
  object: Codex rejects the whole output and the block is lost.
- Don't let `new-adr.py` number ADRs on this branch: it would pick 0022, which
  the parked branch already uses. Use ADR-0023 for RFC-0007 and ADR-0024 for
  RFC-0008.
- Don't link to ADR-0022 from this branch; the file only exists on the parked branch.
- Don't delete `docs/superpowers/`, `docs/discovery/README.md`, or the
  `discovery-note`/`-meeting`/`-artifact` templates. Accepted ADRs cite the
  first, the payload ships the second, and tests assert the templates.
- Don't delete files without asking; `rm` was declined twice.
- Don't edit accepted historical ADRs just to remove mentions of deleted
  legacy surfaces.
