---
status: Superseded by 0017
date: 2026-06-02
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0015. promote-discovery defaults to interactive decision-shaping; the CLI stays a plain flip

## Context and Problem Statement

`promote-discovery` (ADR-0008) flips a captured discovery note's frontmatter `status: raw → promoted` and records `promoted_to:`. It captures a *link* but performs no synthesis: the author still has to separately scaffold (`new-adr`/`new-rfc`) and write the structured doc by hand. Worse, a raw discovery note rarely contains the rationale an ADR needs — Context, Decision Drivers, Considered Options, the actual Outcome — so that information must be *elicited from a human*, not extracted from the note. The question: how do we make "promote this note" do the real work (turn received material into a Proposed ADR/RFC) without breaking the deterministic, hook-safe CLI that ADR-0008 established?

## Decision Drivers

- **Hook safety is non-negotiable (ADR-0008).** `promote_discovery.py` runs in a SessionStart `--check` hook: silent, deterministic, never interactive, always exit 0. An interview cannot live in that script.
- **Rationale must be elicited, not invented.** ADR quality depends on real human answers (drivers, options, why) — so the synthesis step is irreducibly an interactive, agent-driven activity (consistent with ADR-0007: scripts are dumb, the agent does the intelligent work).
- **Two audiences, two surfaces.** An AI agent invocation should do the rich thing by default; a plain CLI/Copilot/manual invocation must keep working as the simple, scriptable flip.
- **Reuse over new code.** The deterministic pieces already exist (`new-adr.py`, `new-rfc.py`, `promote_discovery.py promote`) — the feature should compose them, not add a parser or a dependency.

## Considered Options

- **Option A — Default the agent surface to interactive; keep the CLI a plain flip (chosen).** The `/promote-discovery` SKILL (and Copilot prompt) default to: propose ADR/RFC candidates → confirm → interview → draft Proposed docs → call the CLI flip. `promote_discovery.py` is unchanged.
- **Option B — A separate `shape-decision` skill.** Keeps promote-discovery untouched; adds a second skill. More surface area, two things to discover, and "promote" stays dumb even when an agent runs it.
- **Option C — Add interactivity to the script** (a `--shape` mode that prompts). Violates ADR-0008 (the script is hook-invoked) and ADR-0007 (would push synthesis into stdlib Python).

## Decision Outcome

Chosen option: **Option A**, because it puts the rich behavior exactly where the user expects it (invoking promote *via an agent*) while preserving the deterministic CLI that the hook and scripts depend on. The interview/drafting is agent guidance in the SKILL + prompt; the CLI remains the plain monotonic flip and is the final deterministic step of the rich flow.

### Consequences

- **Good:** Promoting a note via Claude (or Copilot) turns received material into Proposed ADR/RFC docs in one guided pass, with the rationale actually elicited; the audit trail (`promoted_to:`) is set automatically.
- **Good:** Zero new Python and zero new dependencies — the SKILL composes `new-adr.py`, `new-rfc.py`, and `promote_discovery.py promote`.
- **Bad:** The default behavior of an agent invocation now diverges from the bare CLI — a reader of `promote_discovery.py` alone won't see the interview. The SKILL/prompt and this ADR are where that behavior is documented.
- **Neutral:** The plain flip stays available (and is the documented fallback) for "just record the link," for Copilot/manual use, and for notes that imply no decision.

## More Information

- Extends: [0008](./0008-hooks-invoke-script-in-check-mode-behavior-writes-via-slash-command.md) (hook-safe script; behavior writes via slash command — this ADR adds the interactive default at the slash-command surface).
- Related: [0007](./0007-author-ai-tool-wrappers-as-thin-shells-over-stdlib-python-scripts.md) (scripts dumb / agent synthesizes), [0014](./0014-capture-stage-for-discovery-gitignore-raw-intake-track-synthesized-markdown.md) (capture stage that feeds `captured/` notes into this flow).
- Composes: `scripts/new-doc/new-adr.py`, `scripts/new-doc/new-rfc.py`, `scripts/promote-discovery/promote_discovery.py`.
