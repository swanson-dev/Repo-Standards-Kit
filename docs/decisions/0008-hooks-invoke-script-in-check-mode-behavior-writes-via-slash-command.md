---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0008. Hooks invoke script in check mode; behavior writes via slash command

## Context and Problem Statement

Slice 2.5 ships `update-handoff`, the kit's first artifact that has both a slash-command surface (Claude SKILL.md + Copilot prompt.md) and an automated-trigger surface (a Claude Code Stop hook). The slash command and the hook share the same underlying behavior — inspect git state and decide whether the handoff needs updating — but they have different non-functional requirements. Slash commands run on explicit user invocation and may write files. Hooks run on every assistant turn and must never break the session, never overwrite work-in-progress, and never surprise the user with file mutations. The question is whether to write two implementations, fork the behavior across two scripts, or design a single script that meets both surfaces' requirements.

## Decision Drivers

- **Hooks must be non-blocking.** A Stop hook that exits non-zero halts the Claude Code session; one that writes files unexpectedly worsens trust and risks overwriting in-progress edits.
- **One source of truth per behavior.** Forking the inspection logic across "the hook" and "the slash command" creates drift bait — the kind of issue ADR-0007 explicitly tried to design out for wrappers.
- **Explicit-consent file writes.** A pattern where the hook nudges and the user invokes a command to actually write is auditable: the user sees the reminder, decides, runs the command, reviews the diff before committing.
- **Tool-neutrality survives.** The script runs anywhere Python 3 is installed. Only the *trigger* (Stop) is Claude-specific; Copilot users invoke the same script via the slash command.

## Considered Options

- **Option A — Two scripts: one for the hook, one for the slash command.** Maximum isolation; maximum maintenance and drift surface.
- **Option B — One script with two modes: write (default) + `--check` (chosen).** Hook calls `--check` (read-only, silent unless work happened, always exits 0). Slash commands call no flag (writes the file). Same script, two invocation surfaces.
- **Option C — Hook auto-writes with gating logic** (e.g., write only if handoff older than N hours AND commits exist). Maximum automation; brittle; violates explicit-consent.

## Decision Outcome

Chosen option: **Option B**, because it satisfies all four drivers simultaneously — one source of truth, hooks stay non-blocking, file writes stay explicit, and tool-neutrality holds. The `--check` flag is the minimal additional surface needed to make a single script serve both invocation contexts.

### Consequences

- **Good:** Adding a future hook (e.g., `promote-discovery` in Slice 2.6) follows the same shape — a `--check` mode on the script, wired in `.claude/settings.json`. New AI tools with their own hook systems integrate via the same mode. Manual debugging of the hook's logic is just running the script with `--check` in a terminal.
- **Bad:** The `--check` mode's contract (silent + exit 0 in all error paths) is the opposite of write mode's contract (loud + exit 2 on precondition failures). The script must internally distinguish the two and never let one mode's discipline leak into the other.
- **Neutral:** Copilot Chat (and any AI tool without a hook system) loses the auto-reminder but keeps the slash-command behavior. The wrapper pair documents this asymmetry explicitly.

## More Information

- Related ADRs: [0007](./0007-author-ai-tool-wrappers-as-thin-shells-over-stdlib-python-scripts.md) — the parent pattern (wrappers over scripts); this ADR is its hook-surface companion. [0006](./0006-adopt-agents-md-pattern.md) — the meta-pattern (canonical contract + thin tool pointers) both ADRs descend from.
- Resolves: no open question; flows from Q-1's Slice 2.5 resolution.
