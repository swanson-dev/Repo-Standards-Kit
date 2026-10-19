---
status: Accepted
date: 2026-10-15
deciders: Josh Swanson
consulted: Claude, Codex (cross-host spike)
informed: Repo-Standards-Kit adopters
---

# 0023. Enforce doc and continuity upkeep with block-once Stop hooks and a drift map

## Context and Problem Statement

[ADR-0008](./0008-hooks-invoke-script-in-check-mode-behavior-writes-via-slash-command.md) made the Stop hook read-only and always exit 0, because it assumed a non-zero exit "halts the Claude Code session." [ADR-0020](./0020-add-advisory-ai-continuity-hooks-and-standard-slash-commands.md) kept hooks advisory. As a result the kit could only remind: a hook noticed drift, printed a reminder, and the turn ended anyway, so upkeep still depended on someone remembering.

[RFC-0007](../rfcs/0007-how-should-the-kit-make-documentation-and-continuity-upkeep-automatic-instead-of-advisory/rfc.md) found that premise no longer holds. On every host the kit targets, a Stop hook can ask the agent to keep working instead of ending the session; a spike verified this in Claude Code and Codex. The question is how the kit should get documentation, changelog, handoff, and procedure upkeep done automatically.

## Decision Drivers

- Upkeep should happen without anyone having to remember it.
- Hooks must never write files or draft prose; the agent writes, because it has the context.
- No infinite loops, and no busywork on changes that don't affect a doc.
- Work across Claude Code, Codex, and Copilot, with a backstop that needs no agent at all.
- Existing adopters must not suddenly start being blocked.

## Considered Options

- **Keep advisory hooks** — ADR-0008 as written: reminders only.
- **Block until the doc changes** — strict, but loops when a change genuinely needs no update.
- **Block once, then trust the agent** — driven by a per-repo drift map, with a CI backstop (RFC-0007).

## Decision Outcome

Chosen option: **Block once, then trust the agent**, because it makes upkeep automatic while keeping ADR-0008's core rule that hooks never write, and the CI check covers any host whose hook can't block.

- **Modes.** Stop hooks gain an `enforce` mode. When drift is found and `stop_hook_active` is false, the hook blocks with a reason naming the changed files and the doc to update. When `stop_hook_active` is true, it lets the turn end. `advise` keeps today's reminders.
- **Output.** Exit 0 with top-level `{"decision": "block", "reason": "..."}` by default. A host that needs a different shape gets a small per-host adapter. One object carrying several shapes is not allowed, because Codex rejects unknown fields and silently drops the block.
- **Drift rules.** Defaults live in code. A repo adds or overrides rules under a `drift` key in `.standards-kit.json`. Drift is measured since the target doc was last updated, across commits and uncommitted files.
- **Changelog rule.** Committed work is judged by its conventional-commit type: `feat`, `fix`, `perf`, `revert`, and breaking changes need an entry. Uncommitted work and non-conventional commits fall back to paths.
- **CI backstop.** `standards check` gains a drift mode for pull requests. A `Docs-Unaffected:` commit trailer, or the same line in the PR description after a squash merge, waives a doc.
- **Rollout.** The kit itself and new adopters default to `enforce`; existing adopters keep `advise` until they opt in.
- **Scope.** This supersedes ADR-0008 and amends ADR-0020 for Stop hooks only. SessionStart hooks stay read-only.

### Consequences

- **Good:** Docs, the changelog, and the handoff stay current without anyone remembering.
- **Good:** Every host gets either an enforcing hook or the CI backstop.
- **Bad:** The kit maintains a small output adapter per host. The Copilot shapes are verified during implementation.
- **Bad:** Codex runs project hooks only after both the repo and the hook are trusted, and gives no warning otherwise, so adoption docs must say so.
- **Neutral:** An agent can still decide a change needs no doc update; the trailer records why.

## More Information

- Related RFC: `docs/rfcs/0007-how-should-the-kit-make-documentation-and-continuity-upkeep-automatic-instead-of-advisory/` (concluded 2026-10-15); spike results are in its `artifacts/` folder.
- Supersedes: ADR-0008. Amends: ADR-0020.
- Related: ADR-0022, daily changelog sections, on branch `feat/adr-0022-daily-changelog-grouping`.
