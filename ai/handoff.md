---
written: 2026-10-19T14:25:00-05:00
written_by: claude (for Josh Swanson)
for: next-session
---

# Handoff

## TL;DR

M8 (automation engine, ADR-0023) shipped in v1.4.0 on 2026-10-18: PR 21 merged
into `main`, the `v1.4.0` tag published to PyPI, and a GitHub Release exists. It
carries the drift rules, the block-once Stop hook, the CI drift check, one hook
file per repo picked by `agents` (`init`/`adopt --agents`), a once-per-session
block on CI runners, and the `.claude` payload fix. M9 (setup wizard, ADR-0025)
is being built on `feat/m9-setup-wizard` for v1.5.0. Slice 1 (committed) merges
`infra` into `application` and keeps it as an alias. Slice 2 (uncommitted until
the owner OKs it) makes profiles combine by the strongest tier, and setup now
creates and ticks the docs they need. Slice 3, the menu and wizard, is next.
RFC-0008 (distribution) is an approved design still Open, and RFC-0010
(retrospectives) is drafted.

## Recently touched

- M9 slice 2 (ADR-0025): profiles combine. `src/standards/profiles.py` holds the
  four profiles, the `infra` alias (moved from `marker.py`), the matrix (doc ->
  template and tiers) and extras, `parse_profiles` (comma list, order kept,
  repeats dropped, `documentation` alone), `combine` (strongest tier), and
  `needed_docs`. `tests/test_profiles.py` keeps the matrix and extras in sync with
  `docs/STANDARDS.md`. The marker writes `profiles` with `profile` as its first
  entry, and `read_marker` fills `profiles` in for old markers (`profiles` wins
  when the two disagree). `init`/`adopt` take `--profile a,b`, create the
  Required and Expected docs from templates without overwriting, tick them, and
  list the extras as plain bullets so a fresh repo stays CI-green. `doctor` uses
  profile overlap. The structural check validates every name in the header and
  strips HTML comments, but text after the list, such as `(with IaC)`, still
  passes, as it did when only the first word was read. Codex found the loose
  header parse (fixed with tests) and the checklist reconciliation gap (left for
  slice 3).
- M9 slice 1 (ADR-0025): four profiles. `--profile infra` maps to `application`
  before argparse checks choices (`_profile_arg` in `cli.py`); `read_marker` reads
  an `infra` marker as `application`, so `update` rewrites it and `doctor` sees
  application; the structural check still accepts `infra` in checklists
  (`ALLOWED_PROFILES`). `docs/environments.md` is now an application extra.
  `docs/STANDARDS.md`, the templates' tier headers, README, glossary, and the API
  doc drop `infra`; `CHANGELOG.md` records it under Changed and Deprecated (the
  deprecation policy keeps an alias for at least one minor release). The tier
  matrix isn't in code yet; slice 2 adds it.
- v1.4.0 released (2026-10-18). PR 21's CI ran the drift check against
  `origin/main` and the wheel build smoke, and both passed.
- Copilot hook config (owner's rule, 2026-10-16): `standards init`/`adopt` take
  `--agents claude,copilot`, record `agents` in `.standards-kit.json`, and with
  no flag reuse a recorded choice (force re-init) or detect the machine
  (`detect_agents` in `cli.py`: `claude`/`copilot` on PATH, `~/.claude`,
  `~/.copilot`, or a VS Code `github.copilot*` extension). `update` follows the
  marker; a missing or broken `agents` keeps the Claude file. One hook file per
  repo (`manifest.hook_file`): `.claude/settings.json` if Claude is listed, else
  `.github/hooks/standards.json`, whose source is
  `docs/templates/copilot-hooks.json` (`PAYLOAD_SOURCES`) so the kit's own repo
  never has a live `.github/hooks/`. That file carries only the two Stop hooks.
  `init --force` refuses to switch while the old tracked hook file exists. Codex
  found two bugs (force re-init switching, misspelled `agents`), both fixed with
  tests. Docs: `docs/STANDARDS.md`, `docs/templates/README.md`, RFC-0007's
  `spike-results.md` (B2 rows), RFC-0008 (corrected the cloud agent claim, added
  a double-run check), RFC-0009 (its setup asks the agents question).
- Test B2 (2026-10-16): Copilot CLI 1.0.98 runs Stop hooks from
  `.claude/settings.json`, and with `.github/hooks/` too it runs each twice. The
  cloud agent runs `.claude/settings.json` hooks with plain `python` (branch
  `spike/b2-claude-settings`, PR 4 in the throwaway repo). Copilot runs
  SessionStart hooks but drops their plain stdout.
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
- Throwaway evidence: the cloud hook logs from PRs 2, 3, and 4 of the private
  repo `swanson-dev/rfc0007-hook-spike` are saved in RFC-0007's
  `artifacts/spike/logs/`, so the owner can delete that repo.
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

- Keep all hooks and all skills. The user wants to lean more on hooks, not less,
  and relies on the agent to trigger ADRs and plans. Profiles: on 2026-10-17 the
  user merged `infra` into `application`, leaving four (application, library,
  data, documentation). ADR-0025 records it and supersedes ADR-0003; M9 slice 1
  builds it, keeping `infra` as an alias.
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
- Hook config (2026-10-16): "If the user only has Copilot it should use .github
  but if the user has claude and copilot it should use the claude hook for both."
  The choice is recorded in the repo, with machine detection only as the default,
  and RFC-0009's setup will ask it.
- Retrospectives (RFC-0010): a `standard-retro` skill the user runs; proposals
  only, each citing evidence; output only to artifacts in git. Lasting lessons go
  in `ai/gotchas.md`, which `AGENTS.md` only points to.
- RFC order: 0007 automation, 0008 distribution, 0009 setup wizard, 0010 retro.
- Approved deletions are untracked dead weight only (`_delete-me/`, `dist/`,
  tool caches). The `rm` was declined, so nothing has been deleted.

## Open threads

- M9, what's left: slice 3, the bare `standards` menu and the setup wizard. See
  `ai/next-actions.md` item 1. Its "Change what this repo contains" action must
  reconcile an existing checklist: `adopt` and `init --force` keep a checklist
  that already exists, so its header and rows can disagree with the profiles
  they record and the docs they create. That was already true for one profile;
  Codex flagged it in the slice 2 review.
- M8 leftovers: test D (Codex's interactive trust flow) is still a manual run,
  and Codex hook config isn't shipped (`.codex/` is gitignored here and not in
  the payload); RFC-0008's plugin is the planned way to ship it.
- RFC-0008 checks: does the Copilot cloud agent load skills from plugins declared
  in `.github/copilot/settings.json`, and does its `agentStop` hook fire? Do
  Codex marketplace-installed plugin hooks run? Do VS Code and Copilot CLI list
  `.claude/skills` as slash commands (if so, retire `.github/prompts`)? New:
  if the plugin carries the hooks while the repo keeps hook config for the cloud
  agent, VS Code and the Copilot CLI run each hook twice; RFC-0008 now lists it.
- The SessionStart context brief doesn't reach Copilot agents: Copilot runs the
  hook but drops plain stdout. Needs Copilot's structured output, then a
  SessionStart entry in `docs/templates/copilot-hooks.json`.
- RFC-0009 is concluded. The owner approved the prototype's menu and kept its
  two departures: Enter accepts the default in brackets, and "Update" shows only
  when the repo is behind. M9 builds it.
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

- `python tools/run_tests.py`: 32/32 suites passed after the agents change
  (2026-10-16), including both drift suites (52 tests in `test_drift.py`).
  The intermediate `FAIL` lines come from `tests/test_run_tests.py` exercising a
  deliberately failing fixture; trust the final summary.
- `python scripts/standards-check/check.py`: 0 errors, 0 warnings.
- `ruff check .` and `mypy src/standards`: clean.
- `python scripts/standards-check/check.py --drift-base main`: 0 errors, 0 warnings.
- Not run locally: a wheel build. The Copilot file's source rides the existing
  `docs/templates` force-include; CI's `build-smoke` job is the first real check.

## Don't do

- Don't be surprised when this repo's own Stop hook blocks once at the end of a
  turn: with no marker the kit enforces, so update the named doc (usually
  `CHANGELOG.md`) or say why it is unaffected.
- Don't build drift logic into `scripts/changelog/check_changelog.py` until the
  parked ADR-0022 branch lands; it rewrites that script. Keep new logic in
  `scripts/drift/`.
- Don't let a hook treat `DriftError` as "nothing behind". The Stop hook fails
  open (exit 0) but says why on stderr; the CI check must fail loudly.
- Don't separate profiles with commas in the checklist header. Older checkers
  keep only the first word, so `application, data` reads as the invalid
  `application,`. Use `application + data`.
- Don't emit top-level `decision`/`reason` and `hookSpecificOutput` in one
  object: Codex rejects the whole output and the block is lost.
- Don't let `new-adr.py` number ADRs on this branch: it would pick 0022, which
  the parked branch already uses. ADR-0024 is reserved for RFC-0008, and
  ADR-0026 is next after it (RFC-0010).
- Don't link to ADR-0022 from this branch; the file only exists on the parked branch.
- Don't delete `docs/superpowers/`, `docs/discovery/README.md`, or the
  `discovery-note`/`-meeting`/`-artifact` templates. Accepted ADRs cite the
  first, the payload ships the second, and tests assert the templates.
- Don't delete files without asking; `rm` was declined twice.
- Don't ship hooks in both `.claude/settings.json` and `.github/hooks/`: every
  Copilot host reads both and runs each hook twice. Don't create a live
  `.github/hooks/` in the kit's own repo; the Copilot file's source is
  `docs/templates/copilot-hooks.json`.
- Don't add `SessionStart` to the Copilot hook file until `session_context.py`
  emits output Copilot passes to the agent; plain stdout is dropped.
- Don't let a Stop hook write into the working tree: the Copilot cloud agent
  commits whatever is there into its PR. The CI-runner block record lives in
  `RUNNER_TEMP`.
- Don't edit accepted historical ADRs just to remove mentions of deleted
  legacy surfaces.
