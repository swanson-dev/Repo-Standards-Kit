---
written: 2026-10-15T09:30:00-05:00
written_by: claude (for Josh Swanson)
for: next-session
---

# Handoff

## TL;DR

The kit's direction is "automatic, not advisory." RFC-0007 (automation engine)
and RFC-0008 (distribution: the pip CLI plus one plugin) are approved and
committed on `docs/rfc-0007-automation-engine`. The RFC-0007 spike verified the
block-once Stop hook on Claude Code and Codex; the Copilot hosts still need the
owner's manual tests before RFC-0007 can conclude.

## Recently touched

- `0216cfd`, fast-forwarded into `docs/rfc-0007-automation-engine`: the RFC-0007
  spike (`artifacts/spike/stop_hook.py` with its test, per-host hook configs,
  and `artifacts/spike-results.md`), plus a findings summary in the RFC.
- Archived the spike session and deleted its merged branch
  `CODE/eloquent-lovelace-ab5a30`. The app kept its worktree folder under
  `.claude/worktrees/` (detached HEAD) so the session can be reopened.
- Ignored `.archify/` (local diagram output) in `.gitignore`.
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
- Approved deletions are untracked dead weight only (`_delete-me/`, `dist/`,
  tool caches). The `rm` was declined, so nothing has been deleted.

## Open threads

- RFC-0007: manual tests A–D in `artifacts/spike-results.md` (Copilot in VS
  Code, Copilot CLI, the Copilot cloud agent, Codex's interactive trust flow).
  Test A decides whether VS Code needs its own output variant. Also open: where
  the drift map lives, and how "docs unaffected" is recorded for CI.
- RFC-0008: does the Copilot cloud agent load skills from plugins declared in
  `.github/copilot/settings.json`, and does its `agentStop` hook fire? Do Codex
  marketplace-installed plugin hooks run? Do VS Code and Copilot CLI list
  `.claude/skills` as slash commands (if so, retire `.github/prompts`)? Where
  does the marketplace live?
- RFC-0009 is not drafted. Inputs from the user: bare `standards` opens a menu
  (set up, check or fix, update, new skill); setup asks "what does this repo
  contain?" as a multi-select where docs-only means no picks; init vs adopt is
  picked automatically; the marker stores a profile list and still reads the
  old single value. The setup flow may live in the plugin.
- `scripts/new-doc/new-rfc.py --help` creates an RFC titled "help" because the
  script takes its first argument as the title.

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
