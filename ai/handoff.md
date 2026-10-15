---
written: 2026-10-14T21:25:00-05:00
written_by: claude (for Josh Swanson)
for: next-session
---

# Handoff

## TL;DR

Reframed the cleanup around the kit's purpose: documentation and continuity
upkeep should happen automatically, not as reminders. The user approved RFC-0007
(automation engine) and chose a hybrid distribution: the pip CLI for repo content
and CI, plus a plugin for skills, hooks, and setup. The user also approved
RFC-0008 (distribution). Both RFCs are Open and uncommitted on
`docs/rfc-0007-automation-engine`; each concludes after a short verification.

## Recently touched

- Committed the parked work as `665f820` on `feat/adr-0022-daily-changelog-grouping`:
  ADR-0022 daily changelog grouping, the managed `AGENTS.md` simplification, and
  an `ai/` refresh. Not merged, not pushed.
- `docs/rfcs/0007-how-should-the-kit-make-documentation-and-continuity-upkeep-automatic-instead-of-advisory/rfc.md`:
  approved by the user, with the agreed changes folded in: a commit-aware
  changelog rule (§2), hooks shipped in the plugin with a per-host adapter (§5),
  `${CLAUDE_PLUGIN_ROOT}` for hook paths, and the wizard renumbered to RFC-0009.
- `docs/rfcs/0008-how-should-the-kit-split-and-distribute-its-repo-content-and-agent-tooling/rfc.md`:
  drafted from the plugin research and approved by the user.
- Refreshed `ai/current-state.md` and `ai/next-actions.md`.
- Nothing is committed on this branch yet.

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

- RFC-0007: cross-host spike. Does Copilot in VS Code accept top-level
  `decision`/`reason` on Stop, or only its `hookSpecificOutput` wrapper? Also
  where the drift map lives, and how "docs unaffected" is recorded for CI.
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
- `.archify/` (a diagram folder from this session) is untracked and not gitignored.

## Research notes

Full findings and sources live in RFC-0007 (hooks) and RFC-0008 (plugins and
skills). Local precedent: Anthropic's `ralph-loop` plugin blocks Stop with
`{"decision": "block", "reason": ...}`, and the `remember` plugin ships Claude,
Codex, and Gemini manifests plus a `pyproject.toml` from one repo.

## Validation

- `python tools/run_tests.py` on this branch: 30/30 suites passed. The
  intermediate `FAIL` lines come from `tests/test_run_tests.py` exercising a
  deliberately failing fixture; trust the final summary.
- `python scripts/standards-check/check.py`: 0 errors, 0 warnings.

## Don't do

- Don't let `new-adr.py` number ADRs on this branch: it would pick 0022, which
  the parked branch already uses. Use ADR-0023 for RFC-0007 and ADR-0024 for
  RFC-0008.
- Don't link to ADR-0022 from this branch; the file only exists on the parked branch.
- Don't delete `docs/superpowers/`, `docs/discovery/README.md`, or the
  `discovery-note`/`-meeting`/`-artifact` templates. Accepted ADRs cite the
  first, the payload ships the second, and tests assert the templates.
- Don't delete files without asking; `rm` was declined twice this session.
- Don't edit accepted historical ADRs just to remove mentions of deleted
  legacy surfaces.
