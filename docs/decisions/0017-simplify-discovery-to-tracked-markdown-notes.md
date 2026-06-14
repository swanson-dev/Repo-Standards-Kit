---
status: Accepted
date: 2026-06-12
deciders: josh
consulted: codex
informed: kit adopters
---

# 0017. Simplify discovery to tracked markdown notes

## Context and Problem Statement

ADR-0014 added a capture stage with gitignored intake folders and tracked `captured/` notes. ADR-0015 added an interactive promote workflow that flipped discovery frontmatter to `status: promoted` and set `promoted_to:`.

In practice, that workflow made discovery feel heavier than intended. Discovery should be a normal place to preserve early context, not a command-driven lifecycle with hooks, status transitions, and generated folders.

## Decision Drivers

- Keep discovery lightweight enough that teams will actually use it.
- Remove agent hooks that interrupt sessions with discovery lifecycle reminders.
- Avoid a second status system beside ADR/RFC/doc links.
- Keep the kit's payload smaller and easier to explain.

## Considered Options

- **Option A** - Keep capture/promote and only remove hooks.
- **Option B** - Keep `captured/` but remove the commands.
- **Option C** - Use flat tracked markdown notes under `docs/discovery/`.

## Decision Outcome

Chosen option: **Option C**, because it preserves the useful part of discovery - lightweight context capture - while removing the command workflow and lifecycle fields that made the folder feel over-designed.

### Consequences

- **Good:** Discovery notes are simple markdown files directly under `docs/discovery/`.
- **Good:** The kit no longer ships `capture-discovery`, `promote-discovery`, discovery SessionStart hooks, intake `.gitkeep` folders, `captured/`, or the `promoted_to` standards check.
- **Bad:** The kit no longer provides a built-in workflow for local raw binaries or automated promotion tracking.
- **Neutral:** Historical ADRs and changelog entries still describe the old workflow; this ADR supersedes that design.

## More Information

- Supersedes: ADR-0014, ADR-0015.
- Keeps: ADR-0005's distinction between discovery notes and RFC investigations.
