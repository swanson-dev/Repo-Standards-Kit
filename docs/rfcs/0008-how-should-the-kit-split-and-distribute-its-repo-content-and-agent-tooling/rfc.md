---
status: Open
opened: 2026-10-14
closed:
owner: Josh Swanson
time_box: 2 days (cloud-agent and Codex checks + review)
---

# 0008. How should the kit split and distribute its repo content and agent tooling?

## Question

How should the kit split what it ships between repo content and agent tooling, and distribute each so both stay current with the least per-repo work?

## Why now

Today `standards init` copies everything into every adopter repo: the docs and templates, but also the skills (`.claude/skills`), Copilot prompt files (`.github/prompts`), hook config, and the `scripts/` that run them. [ADR-0009](../../decisions/0009-distribute-the-kit-as-a-pypi-standards-cli-with-vendored-copy-sync.md) chose this vendored-copy model, and `standards update` (hash guards, managed regions, `.kit-` sidecars) exists to keep those copies in sync. Every kit release therefore means running `standards update` in every repo.

[RFC-0007](../0007-how-should-the-kit-make-documentation-and-continuity-upkeep-automatic-instead-of-advisory/rfc.md) adds hooks that must run on five agent hosts, and RFC-0009 (setup wizard and composable profiles) depends on whether setup runs in a terminal or inside the agent. This RFC revisits [RFC-0001](../0001-what-is-the-kit-s-distribution-and-upgrade-mechanism/rfc.md) and ADR-0009 before either is built.

## Approach

- Research plugin systems, skill folders, and update behavior on every target host: Claude Code, Codex (CLI and IDE extension), and GitHub Copilot in VS Code, the CLI, and the cloud agent.
- Inspect plugins installed on the owner's machine for working precedent.
- Compare against what the payload ships today (`src/standards/manifest.py`).

The owner chose the hybrid direction (CLI plus plugin) and approved this design on 2026-10-14. Remaining before this RFC concludes:

- **Cloud agent.** Whether skills from plugins declared in `.github/copilot/settings.json` load in the Copilot cloud agent, and whether its `agentStop` hook fires.
- **Codex plugin hooks.** Codex's docs conflict on whether hooks bundled in a marketplace-installed plugin run. Test on a real install.
- **Prompt files.** Confirm that VS Code and Copilot CLI list `.claude/skills` skills as slash commands before retiring `.github/prompts` and its parity check.
- **Marketplace home.** This repo (one repo for the pip package, the plugin, and `marketplace.json`) or a dedicated repo.

## Findings

### One plugin reaches four of five hosts

| Host | Plugins | Reads Claude's `.claude-plugin/` format | Skills folders it reads | Updates |
|---|---|---|---|---|
| Claude Code | yes | native | `.claude/skills`, plugin `skills/` | auto-update off by default for third-party marketplaces |
| Codex CLI | yes | yes ("legacy-compatible"); sets `CLAUDE_PLUGIN_ROOT` | `.agents/skills` (not `.claude/skills`) | `codex plugin marketplace upgrade` |
| Codex IDE extension | no | n/a | `.agents/skills` | n/a |
| Copilot in VS Code | yes ("agent plugins") | yes; supports `${CLAUDE_PLUGIN_ROOT}` | `.github/skills`, `.claude/skills`, `.agents/skills` | checks every 24 hours |
| Copilot CLI | yes | yes; reads `.claude-plugin/` plugin and marketplace files | `.github/skills`, `.claude/skills`, `.agents/skills` | `copilot plugin update`; auto-update for first-party only |
| Copilot cloud agent | declared in `.github/copilot/settings.json` only | same as Copilot CLI | `.github/skills`, `.claude/skills`, `.agents/skills` | n/a |

Sources: [Claude Code plugins](https://code.claude.com/docs/en/plugins/components), [Claude Code plugin loading and updates](https://code.claude.com/docs/en/plugins/loading), [Codex plugins](https://learn.chatgpt.com/docs/plugins), [VS Code agent plugins](https://code.visualstudio.com/docs/copilot/customization/agent-plugins), [Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [About Copilot plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins). Skills follow the cross-tool Agent Skills (`SKILL.md`) format on every host.

### What a plugin cannot do

- **No always-on instructions.** A plugin's root `CLAUDE.md` is not loaded; plugins offer skills (loaded when relevant), hooks, and SessionStart context. `AGENTS.md` therefore stays in the repo, where every host reads it (Claude Code through the `CLAUDE.md` pointer).
- **No CI.** GitHub Actions has no agent, so `standards check` and RFC-0007's drift check stay in the CLI.
- **No portable hooks.** Event names and output shapes differ between hosts, so each needs a small adapter (RFC-0007). The Copilot cloud agent loads hooks only from the repo's `.github/hooks/*.json`, and Codex never auto-trusts plugin hooks.

### Updates and team rollout

- A user gets a new copy of a plugin when its version changes. Claude Code leaves auto-update off by default for third-party marketplaces, so users enable it once per marketplace or run an update. That is one action per machine, against one `standards update` per repo today.
- A repo can declare the kit's marketplace and plugin in `.claude/settings.json` (`extraKnownMarketplaces`, `enabledPlugins`). Teammates are prompted once they trust the folder, but still run `claude plugin install` for a plugin hosted elsewhere. The Copilot cloud agent reads the equivalent `.github/copilot/settings.json`.
- Plugin skills are namespaced: `new-adr` becomes `/standards:new-adr` in Claude Code.

### Precedent

- Anthropic's `ralph-loop` plugin blocks Stop from `${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh` by printing `{"decision": "block", "reason": ...}`.
- The `remember` plugin ships `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` (with its own hooks file), a Gemini extension, and a `pyproject.toml` from one repo. That is the CLI-plus-plugin shape proposed here.

### A competing standard is forming

"Agent Plugins 1.0" uses a root `plugin.json` and is backed by OpenAI, Microsoft, Cursor, Amazon, Vercel, and Google; GitHub reports it generally available in VS Code and Copilot CLI. Anthropic is not listed, and whether Claude Code reads a root `plugin.json` is unverified. Claude's format is what all four plugin-capable hosts read today.

## Proposed design

### The split

| Piece | Home | Read by |
|---|---|---|
| `AGENTS.md`, the `CLAUDE.md` pointer, docs structure, `ai/` starters, `CHANGELOG.md`, checklist, `.standards-kit.json` | repo, scaffolded by the CLI | every host, every human, CI |
| CI workflow that runs a pinned CLI | repo, scaffolded by the CLI | GitHub Actions |
| `.github/hooks/standards.json` | repo, scaffolded by the CLI | Copilot cloud agent |
| Plugin and marketplace declarations (`.claude/settings.json`, `.github/copilot/settings.json`) | repo, scaffolded by the CLI | Claude Code, Copilot cloud agent |
| Skills, hooks, and the setup skill | the kit's plugin, in Claude's `.claude-plugin/` format | Claude Code, Codex CLI, Copilot in VS Code and the CLI |
| `standards` CLI: `init`, `adopt`, `update`, `check`, `doctor` | PyPI | humans, CI, the plugin |

### One engine, two front doors

The plugin's hook scripts and the CLI's checks come from the same codebase and the same release. Each plugin hook reads the repo's kit version from `.standards-kit.json` and warns when the plugin and the repo disagree, so a hook and CI can't quietly judge drift by different rules.

### What stops being copied into repos

- `.claude/skills/` and `.github/prompts/`, which the plugin serves.
- `scripts/`. CI runs a pinned CLI through `uvx` or `pipx`, and plugin hooks run from the plugin's own folder.
- Hook config in `.claude/settings.json`, which the plugin carries.

`standards update` then manages only repo content: the managed block in `AGENTS.md`, the CI workflow, the cloud-agent hook file, and the plugin declarations.

### Migration for existing adopters

`standards update` already reports removals. Kit-tracked copies the adopter never modified (the hash still matches) are removed; modified copies stay and are flagged in the report. The update also adds the plugin declarations. Repos that skip the plugin keep today's behavior through `AGENTS.md`.

### Known gap

The Codex IDE extension has no plugins and reads only `.agents/skills`. Covering it means an opt-in copy of the skills in that folder. Until someone needs it, it gets `AGENTS.md` only.

## Recommendation

Keep the pip CLI for repo content and CI, and move skills, hooks, and the setup flow into one plugin in Claude's `.claude-plugin/` format, distributed from a marketplace. Stop copying agent tooling into adopter repos. This amends ADR-0009: the CLI still scaffolds and updates repo content, but no longer vendors skills, hooks, or scripts. Conclude after the cloud-agent and Codex checks above.

## Follow-ups

- **ADR to write:** yes. ADR-0024 amends ADR-0009. ADR-0022 (the parked changelog branch) and ADR-0023 (RFC-0007) are already reserved.
- **Implementation plan changes:** on conclusion, add a "Distribution" milestone to `docs/05-implementation-plan.md` after the automation engine (RFC-0007) and before the setup wizard (RFC-0009).
- **New open questions:** none; the remaining items are tracked under Approach until this RFC concludes.
- **Discovery to promote:** none
