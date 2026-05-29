---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0007. Author AI-tool wrappers as thin shells over stdlib Python scripts

## Context and Problem Statement

Slice 2 of the Repo Standards Kit ships two scaffolding Skills (`new-adr` and `new-rfc`) that downstream repos and AI tools will invoke daily. Each Skill needs a surface in at least two AI tools — Claude Code (via SKILL.md) and GitHub Copilot Chat (via prompt files) — and ideally a tool-neutral fallback for Codex, plain bash, and future tools. The question is *where the behavior lives*: bake it into each tool's wrapper (forks per tool) or in a shared underlying script with thin per-tool wrappers (DRY, tool-neutral). The choice is load-bearing for Slice 2.5 (Hooks), Slice 3 (Distribution), and every future AI-surface Skill the kit ships.

## Decision Drivers

- **Tool-neutrality.** Claude Code, GitHub Copilot Chat, Codex, and plain bash invocations must reach the same behavior — the kit cannot privilege one AI tool's users.
- **Zero new toolchain.** The kit's existing `scripts/standards-check/check.py` is stdlib-only Python; new scaffolding behavior should inherit the same constraint so the kit stays installable by anyone with Python 3.
- **Slice-3 distribution simplicity.** Every artifact in the kit is markdown or stdlib Python; distribution as a template repo, plugin, or copy script stays trivial.
- **One source of truth per Skill.** Behavior changes must land in one place — drift between Claude SKILL.md and Copilot prompt.md is a bug, not a feature.

## Considered Options

- **Option A — Wrapper-as-source-of-truth.** Each AI-tool wrapper (SKILL.md, prompt.md, future Codex format) carries the full behavior as inline instructions for the model. No underlying script. The model interprets each wrapper independently.
- **Option B — Script-as-source-of-truth + thin wrappers (chosen).** Behavior lives in a stdlib Python script. Each AI-tool wrapper is a ~20-line markdown file that describes when to invoke and shells out to the script.
- **Option C — Full duplication per tool.** A complete behavioral implementation per tool (one Python script per tool, plus the wrapper). Maximum isolation; maximum maintenance.

## Decision Outcome

Chosen option: **Option B**, because it's the only choice that satisfies all four drivers simultaneously — the script gives us tool-neutrality and a single source of truth, stdlib keeps the toolchain at zero, and the thin-wrapper pattern mirrors the AGENTS.md shape the kit already adopted in ADR-0006.

### Consequences

- **Good:** Adding a new AI tool (Codex prompt file, Cursor rules, etc.) is a ~20-line markdown wrapper that calls the existing script. Behavior changes happen in one file. Codex and bash users get the script directly with zero wrapper overhead.
- **Bad:** Wrapper parity is manual until a future Slice ships a single-source generator or lint. Two markdown files per Skill must be kept in sync by humans (or by a code reviewer); silent drift is possible.
- **Neutral:** SKILL.md and prompt.md become documentation-grade artifacts, not behavior-grade. Reviewers and downstream consumers must understand that the canonical behavior is in `scripts/`, not in the wrappers.

## More Information

- Related ADRs: [0006](./0006-adopt-agents-md-pattern.md) — the parent pattern (canonical contract + thin tool pointers).
- Resolves: [`ai/open-questions.md#q-1`](../../ai/open-questions.md#q-1-which-slice-2-skills-should-ship-first) — Slice 2 Skill selection.
