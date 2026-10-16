---
status: Concluded
opened: 2026-10-14
closed: 2026-10-15
owner: Josh Swanson
time_box: 2 days (cross-host hook spike + review)
---

# 0007. How should the kit make documentation and continuity upkeep automatic instead of advisory?

## Question

How should the kit move from hooks that only remind to hooks that reliably get documentation, changelog, handoff, and procedure upkeep done before an agent finishes its turn?

## Why now

The kit exists to take routine engineering hygiene off the engineer: docs that stay current, handoffs that get written, deploy steps captured once and reused. Today every hook is advisory by design. [ADR-0008](../../decisions/0008-hooks-invoke-script-in-check-mode-behavior-writes-via-slash-command.md) made the Stop hook read-only and "always exits 0"; [ADR-0020](../../decisions/0020-add-advisory-ai-continuity-hooks-and-standard-slash-commands.md) kept hooks "advisory, non-blocking, and read-only." A hook notices drift, prints a reminder, and the turn ends anyway, so upkeep still depends on someone remembering.

RFC-0008 (distribution: the CLI plus a plugin) and RFC-0009 (setup wizard and composable profiles) follow this RFC, so they package and install the automation it settles.

## Approach

- Re-verify the hook contracts ADR-0008 relied on, against current official docs for every host the kit targets: Claude Code, Codex CLI, and GitHub Copilot in VS Code, the CLI, and the cloud agent.
- Map today's detection logic (`scripts/changelog/check_changelog.py`, `scripts/update-handoff/update_handoff.py --check`) onto a general "if X changed, Y must be updated" model.
- Inventory what the payload ships per host today (`src/standards/manifest.py`).

The owner approved this design on 2026-10-14, settled where the drift map lives (§2) and how "docs unaffected" is recorded (§4) on 2026-10-15, and concluded the RFC the same day.

The spike had already settled the design: one output that every host accepts is ruled out, so each host gets a small output adapter, with top-level `decision`/`reason` as the default. The remaining manual tests in `artifacts/spike-results.md` (Copilot in VS Code, Copilot CLI, the Copilot cloud agent, and Codex's interactive trust flow) only decide which shape each Copilot adapter emits, so they move to the implementation. If a host's hook cannot block at all, the CI drift check still catches the missed update.

## Findings

### ADR-0008's key premise no longer holds

ADR-0008's first driver says a Stop hook that exits non-zero "halts the Claude Code session." Current Claude Code docs say otherwise. A Stop hook that exits 2, or returns `{"decision": "block", "reason": "..."}`, prevents the stop and gives Claude the reason as its instruction to keep working. Exit 0 without JSON, and any other non-zero exit, let the stop proceed. Valid JSON on exit 0 is still applied. ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks))

Blocking does not break the session. It is the mechanism that makes the agent finish the upkeep.

### Every target host can now enforce an end-of-turn step

| Host | Repo hook config | Stop event | Blocks via | Loop guard |
|---|---|---|---|---|
| Claude Code | `.claude/settings.json` (shipped today) | `Stop` | exit 2, or JSON `decision: block` | `stop_hook_active`; forced stop after 8 consecutive blocks, configurable with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` |
| Codex CLI | `.codex/hooks.json` (not shipped) | `Stop` | exit 0 plus JSON `decision: block` (the reason becomes the continuation prompt), or exit 2 | `stop_hook_active` |
| Copilot in VS Code | `.github/hooks/*.json` (not shipped) | `Stop` | JSON inside `hookSpecificOutput`, or exit 2 | `stop_hook_active` |
| Copilot CLI | `.github/hooks/*.json` (not shipped) | `agentStop` / `Stop` | JSON only; exit 2 is just a warning | `stop_hook_active`; 8-block cap |
| Copilot cloud agent | `.github/hooks/*.json` (not shipped) | `agentStop` | JSON only | 8-block cap; extra turns count against the job timeout |

Sources: [Codex hooks](https://developers.openai.com/codex/hooks), [VS Code hooks](https://code.visualstudio.com/docs/copilot/customization/hooks), [Copilot CLI hooks reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-hooks-reference), [Copilot hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference). Codex, Copilot CLI, and the cloud agent also read `AGENTS.md` natively; VS Code does behind its `chat.useAgentsMdFile` setting.

### Portability constraints

- **Exit 2 is not portable.** It blocks in Claude Code, Codex, and VS Code, but is only a warning in Copilot CLI and the cloud agent. The portable contract is exit 0 plus JSON `decision` and `reason`.
- **VS Code wants a wrapper.** Its Stop output nests the decision in `hookSpecificOutput`. Whether it also accepts top-level fields is unverified; that is the spike.
- **Crashes fail open.** An uncaught Python exception exits 1, which every host treats as non-blocking. A broken hook cannot trap a session.
- **Paths and interpreters.** Today's hooks run `python scripts/...` relative to the current directory, so they break when a session starts somewhere else. Plugin hooks run from `${CLAUDE_PLUGIN_ROOT}`, which Claude Code, Codex CLI, and Copilot in VS Code and the CLI all support, so shipping the hooks in a plugin removes that problem. The Copilot cloud agent runs bash on Linux, where `python` may not exist (only `python3`).
- **Plugins carry hooks, but not portably.** Codex CLI, Copilot in VS Code, and Copilot CLI read Claude's plugin format, and Anthropic's own `ralph-loop` plugin already blocks Stop with `decision: block`. Event names and output shapes still differ per host, so each needs a small adapter. ([Claude Code plugins](https://code.claude.com/docs/en/plugins/components), [Codex plugins](https://learn.chatgpt.com/docs/plugins), [VS Code agent plugins](https://code.visualstudio.com/docs/copilot/customization/agent-plugins), [Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference))
- **Codex requires trust.** Project hooks load only after the user trusts the repo's `.codex/` layer, so a shipped Codex hook never runs silently.
- **Only Claude Code gets hooks in adopter repos today.** The payload ships `.claude/`, but not `.codex/` (which this repo also gitignores) or `.github/hooks/`.

### Cross-host spike (2026-10-14, partial)

The spike ran a stdlib enforce-once Stop hook in throwaway repos. Full results, configs, and manual test steps are in [`artifacts/spike-results.md`](artifacts/spike-results.md).

- **Verified in Claude Code 2.1.286 and Codex CLI 0.159.3:** exit 0 with top-level `decision: block` and `reason` blocks the first stop. The agent receives the reason and acts on it. The next stop arrives with `stop_hook_active: true`, the hook prints nothing, and the turn ends.
- **One object carrying both shapes is ruled out.** Claude Code tolerates an added `hookSpecificOutput` wrapper, but Codex rejects any unknown field on Stop output and silently drops the block. So if VS Code needs its wrapper, that is a per-host shim, not a combined output.
- **Codex trust is silent.** `codex exec` ran the project hook only when the repo was trusted and the hook was trusted (or `--dangerously-bypass-hook-trust` was set). Otherwise the hook was skipped with no warning.
- **Pending (manual):** Copilot in VS Code, Copilot CLI, the Copilot cloud agent, and Codex's interactive trust flow. VS Code's own reference nests Stop's `decision` and `reason` in `hookSpecificOutput`, so the open point stands.

### Detection already exists for two rules

`check_changelog.py` answers "did meaningful work happen since the changelog was last updated?" The ADR-0022 version, parked on branch `feat/adr-0022-daily-changelog-grouping`, also ignores `ai/`-only work and recognizes today's section. `update_handoff.py --check` answers the same question for `ai/handoff.md`, plus a 5-day staleness rule. Both have the same shape: trigger paths changed since the target doc was last touched. Generalizing that shape is the drift map.

## Proposed design

### 1. Enforce once, then trust the agent

Stop hooks move from advisory to **enforce-once**:

- Drift detected and `stop_hook_active` is false: block, with a reason naming the changed files and the doc to update.
- `stop_hook_active` is true: allow the stop. The agent has had its chance to update the doc or say why the change does not need it.
- The hook never writes files and never drafts prose, which keeps ADR-0008's core rule. The agent, which has the context, writes the update.

Example reason:

```text
Not done yet: .github/workflows/release.yml changed but docs/09-deployment.md did not.
Update the deployment doc, or reply with one line explaining why it is unaffected.
```

### 2. The drift map

A per-repo list of rules: when these changes happen, this doc must move with them. The kit ships its default rules in code, and a repo adds rules or overrides a default under a `drift` key in `.standards-kit.json` (decided 2026-10-15). That file already holds the adopter's `check` severity map, so every per-repo setting lives in one place, and `standards update` now keeps adopter-owned keys there. `docs/STANDARDS.md` was ruled out because it is kit-owned, so per-repo edits there would collide with updates. Drift is measured since the doc was last updated, across both commits and uncommitted files, so an agent that commits partway through a session cannot slip past it. Sketch:

```json
"drift": [
  {"update": "CHANGELOG.md",
   "when_commits": ["feat", "fix", "perf", "revert", "!"],
   "when": ["src/**", "scripts/**"]},
  {"update": "docs/09-deployment.md",
   "when": [".github/workflows/**", "infra/**", "Dockerfile"]},
  {"update": "docs/04-api-and-integrations.md",
   "when": ["src/**/api/**"]}
]
```

For the changelog, the commit type is a better signal than paths:

- **Committed work is judged by its conventional-commit type.** `feat`, `fix`, `perf`, `revert`, and breaking changes (`!`) need an entry; `chore`, `docs`, `test`, `ci`, `style`, and `refactor` do not. A `refactor:` that touches `src/` no longer triggers a false reminder, and labeling a commit `chore:` declares that it is not user-facing.
- **Uncommitted work has no type yet**, so it falls back to the `when` paths. So does any commit whose subject is not conventional, which keeps the rule working in repos that don't use conventional commits.
- **Commit subjects feed the agent's entry; they do not replace it.** The changelog is not generated from commits. That would turn it into a copy of `git log` and conflict with ADR-0022's curated daily sections.
- **In CI**, the rule reads the PR's commits, or the PR title when the PR is squash-merged.

The hook's reason can then name the commits:

```text
Not done yet: 2 feat and 1 fix commits since the last changelog update:
  feat(cli): open a menu when run without arguments
  feat(cli): ask what the repo contains during setup
  fix(check): parse comma-separated profiles
Add entries under today's section.
```

The handoff stays a built-in rule (any meaningful session). Architecture decisions stay agent-judged, because a decision is not a path. The `AGENTS.md` rule and the `new-adr` skill cover them.

### 3. Procedure capture

- An `AGENTS.md` rule: before a deploy, a release, or any other documented procedure, follow `docs/09-deployment.md` or `docs/06-runbook.md` instead of re-deriving the steps. If the steps changed, update the doc in the same turn.
- The drift map flags deploy-config changes that did not touch the runbook.
- Optional: graduate a stable runbook into a skill with `standards new-skill`.

### 4. CI backstop

`standards check` gains a drift mode for pull requests. It compares the PR's changed files against the drift map and fails when a trigger changed without its doc. This holds for every agent and for humans. `repo-standards.yml` currently uses a default shallow checkout, so it needs `fetch-depth: 0` or an explicit base-ref fetch. Escape hatch (decided 2026-10-15): a `Docs-Unaffected:` commit trailer naming the doc and the reason, such as `Docs-Unaffected: deployment (renamed a job)`. If a squash merge drops the trailer, the same line in the PR description counts. In a session, the agent's one-line reply satisfies the hook, and the agent adds the same trailer when it commits, so CI sees the same explanation. For the changelog, the commit type already does this job: a `chore:` or `refactor:` commit needs no entry.

### 5. Rollout and compatibility

Reuse the existing severity model: error in the kit, warn by default for adopters, escalate per check in `.standards-kit.json`.

- Hooks gain a mode: `advise` (today's behavior) or `enforce`.
- The kit itself and new adopters default to `enforce`; existing adopters keep `advise` until they opt in.
- Ship the hooks in the kit's plugin, which Claude Code, Codex CLI, and Copilot in VS Code and the CLI all read, with a small output adapter per host. The CLI still scaffolds `.github/hooks/standards.json`, because the Copilot cloud agent loads hooks only from the repo. RFC-0008 settles how the plugin is distributed and kept current.
- The CLI changes ship as a minor release, with no breaking change for current adopters.

## Recommendation

Adopt enforce-once Stop hooks driven by a per-repo drift map, using a portable exit-0 JSON contract, with the changelog rule judged by conventional-commit type. Ship the hooks in the kit's plugin with a small adapter per host, plus a repo-level hook file for the Copilot cloud agent. Add a CI drift check as the agent-agnostic backstop, and keep the existing warn-by-default rollout for current adopters. This supersedes ADR-0008's "always exits 0" contract while keeping its core rule that hooks never write files. Concluded 2026-10-15: the spike settled on per-host output adapters.

## Follow-ups

- **ADR to write:** yes, [ADR-0023](../../decisions/0023-enforce-doc-and-continuity-upkeep-with-block-once-stop-hooks-and-a-drift-map.md). It supersedes ADR-0008 and amends ADR-0020's non-blocking rule. ADR-0022 is taken by the parked changelog branch.
- **Implementation plan changes:** added "M8 — Automation engine" to `docs/05-implementation-plan.md`; RFC-0008 (distribution) and RFC-0009 (setup wizard and composable profiles) follow it.
- **New open questions:** none; the Copilot adapter tests move to the implementation.
- **Discovery to promote:** none
