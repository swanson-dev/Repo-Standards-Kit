---
status: Accepted
date: 2026-06-16
deciders: swanson-dev, codex
consulted: docs/rfcs/0005-should-the-kit-add-advisory-ai-continuity-hooks-and-standard-slash-commands/rfc.md
informed: downstream repo adopters
---

# 0020. Add advisory AI continuity hooks and standard slash commands

## Context and Problem Statement

The kit already defines canonical AI context files and an end-of-session handoff contract. It also ships a Stop hook that nudges users to refresh `ai/handoff.md`. What it lacks is an optional, low-friction way to read that context at session start and preserve the current state before compaction.

The question is how to add that continuity support without making hooks surprising, blocking, or mutating by default.

## Decision Drivers

- Session-start behavior must be advisory, non-blocking, and read-only.
- File writes should happen only through explicit slash/manual commands.
- The solution should reuse stdlib scripts and thin Claude/Copilot wrappers.
- The continuity target remains `ai/handoff.md`; no required new `ai/` file is added.
- Command names should be lowercase kebab-case and use the `standard-` prefix.

## Considered Options

- **Option A** - Rely only on manual reading of `AGENTS.md` and `ai/` files.
- **Option B** - Add a strict SessionStart gate that blocks stale or missing AI context.
- **Option C** - Add advisory hooks plus explicit `standard-*` slash-command surfaces.

## Decision Outcome

Chosen option: **Option C**, because it makes context easy to retrieve and preserve while preserving hook safety. SessionStart reads and summarizes only; handoff and compact snapshot writes are explicit user-invoked actions.

### Consequences

- **Good:** Agents can re-ground at session start and after compaction without relying on memory.
- **Good:** Pre-compaction state can be captured in the existing handoff file through an explicit command.
- **Bad:** The kit ships more AI command surfaces that need parity and hook-path tests.
- **Neutral:** Tools without SessionStart hooks can invoke `standard-get-session-context` manually.

## More Information

- Related ADRs: ADR-0007, ADR-0008, ADR-0019
- Related RFC: `docs/rfcs/0005-should-the-kit-add-advisory-ai-continuity-hooks-and-standard-slash-commands/`
- Open questions spawned: none
