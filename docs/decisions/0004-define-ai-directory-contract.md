---
status: Accepted
date: 2026-05-28
deciders: josh
consulted: claude-code-assistant
informed: team
---

# 0004. Define the ai/ directory as committed, shared, rolling state

## Context and Problem Statement

The kit's `ai/` directory is the most distinctive part of its layout: a place for session-to-session AI context. Without a contract — who writes which file, when, where it lives, how stale is too stale — the directory becomes either (a) a write-only graveyard or (b) a constant source of PR diff noise. The decision needs to lock in commit policy, file roles, ownership, and staleness signals so downstream Hooks and CI checks (Slices 2 and 4) have something concrete to enforce.

## Decision Drivers

- Institutional memory across sessions and across teammates.
- Low friction: maintaining `ai/` must be cheap or it won't happen.
- Predictable enough for AI Hooks to read at session-start and write at session-end without surprises.
- Honest about staleness — a stale `ai/current-state.md` is worse than no file.

## Considered Options

- **Option A** — Shared, committed, rolling state. Four files (`current-state`, `next-actions`, `open-questions`, `handoff`). Per-file ownership + stale thresholds.
- **Option B** — Per-developer scratchpad, gitignored. No shared state, no PR noise.
- **Option C** — Per-task working folders, committed during work, archived after merge.
- **Option D** — Ephemeral, regenerated each session from durable docs and recent commits.

## Decision Outcome

Chosen option: **Option A**, because the highest-value use of `ai/` is shared institutional memory — context the next teammate or AI session can rely on. Per-developer scratchpads (Option B) lose that benefit entirely, per-task folders (Option C) introduce more machinery than the team will sustain, and regenerated context (Option D) discards in-session reasoning that didn't make it back into docs.

### Consequences

- **Good:** A new AI session has a reliable place to start (`AGENTS.md` § "Canonical reading order").
- **Good:** The four-file split (state / intent / uncertainty / memory) maps cleanly to the cognitive load of session continuity.
- **Good:** Hooks in Slice 2 have a predictable contract to bind to.
- **Bad:** Every meaningful PR has some `ai/*.md` churn.
- **Bad:** Stale `ai/*.md` files actively mislead — the staleness thresholds and the CI freshness check must do real work.
- **Neutral:** `ai/` is in the repo's commit history forever; sensitive context (incident details, customer names) should be kept out and live in private channels.

## More Information

- File-by-file shape: `docs/STANDARDS.md` § "The `ai/` directory contract".
- Ownership and stale thresholds: `docs/STANDARDS.md` § "Ownership and update cadence".
- Starters: `docs/templates/ai-starters/`.
- AGENTS.md reading order: `AGENTS.md` § "Canonical reading order".
